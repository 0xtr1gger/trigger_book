---
created: 2026-07-20
updated: 2026-09-20
tags:
  - Windows
  - Windows_PrivEsc
  - enumeration
status: complete
---
>[!abstract] **Scope**: Windows enumeration methodology for identifying local privilege escalation vectors on a local Windows machine.
## Windows enumeration checklist

- [ ] Perform rapid initial 5-minute triage (identity, privileges, OS build, Defender/firewall, active connections).
- [ ] Enumerate user context, group memberships, and token privileges (`whoami /all`).
- [ ] Inspect local services for weak permissions, unquoted paths, and writable registry keys.
- [ ] Audit running processes, process owners, and writable process binaries/directories.
- [ ] Check scheduled tasks and autorun registry keys for writable executables or missing binaries.
- [ ] Search file system permissions (`PATH` environment variable, `Program Files`, `ProgramData`, `C:\Temp`).
- [ ] Inspect security controls, Defender status, AppLocker rules, UAC settings, and LSA protection (`RunAsPPL`).
- [ ] Execute automated enumeration scripts (`winPEAS`, `Seatbelt`, `PrivescCheck`, `PowerUp`).
### Initial 5-minute triage

- **Current user** identity and token **privileges**:

```powershell
whoami /all
```

- **OS version** and installed **hotfixes**:

```powershell
systeminfo
```

```powershell
wmic qfe get HotFixID,InstalledOn,Description
```

- **Running processes** and **associated services**:

```powershell
tasklist /svc
```

- **Active network connections** and **listening TCP ports**:

```powershell
netstat -ano
```

- **Registered services** (status and state):

```powershell
sc.exe query
```

- **Windows Defender** and **real-time protection status**:

```powershell
Get-MpComputerStatus
```

## Users and groups

### Who am I?

- Display current username in NTLM format (`domain\username`):

```powershell
whoami
```

- Display the SID (Security Identifier) assigned to the current user:

```powershell
whoami /user
```

- Display current username alongside all active group memberships:

```powershell
whoami /group
```

>[!tip]+
>- Look for group memberships that provide capabilities beyond those of a standard user, such as:
>	- `Administrators`
>	- [[Backup Operators]]
>	- [[Server Operators]]
>	- `Remote Management Users`
>	- [[Hyper-V Administrators]]
>	- `Distributed COM Users`
>
>>[!note] [[Windows groups]].

- List explicit **security privileges** assigned to the current process access token:

```powershell
whoami /priv
```

>[!tip]+
>- Pay particular attention to privileges such as:
>	- `SeBackupPrivilege`
>	- `SeDebugPrivilege`
>	- `SeImpersonationPrivilege`
>	- `SeAssignPrimaryTokenPrivilege`
>	- `SeTakeOwnershipPrivilege`
>	- `SeLoadDriverPrivilege`
>	- `SeCreateTokenPrivilege`
>
>>[!note] See [[Windows privileges]].

- Display user SID, group memberships, token privileges, and claims:

```powershell
whoami /all
```

- Query environment variables for domain membership information:

```powershell
# CMD
echo %USERDOMAIN%    
echo %USERDNSDOMAIN%
```

```powershell
# PowerShell
$env:USERDOMAIN
$env:USERDNSDOMAIN
```

>[!note] [`whoami`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/whoami)

### Local users

- List local user accounts:

```powershell
net user
```

```powershell
Get-LocalUser
```

>[!tip]+
> - Look for:
> 	- Administrative accounts.
> 	- Service accounts.
> 	- Application-specific accounts.
> 	- Disabled accounts.
> 	- Accounts with unusual names.
> 	- Accounts that appear to have been created for a specific application or task.

- Query extended account properties and flags for a specific local user:

```powershell
net user <username>
```

```powershell
Get-LocalUser -Name <username>
```

>[!info]- Enumerate local users through CIM/WMI
> 
> ```cmd
> wmic useraccount get name,sid,status
> ```
> 
> ```powershell
> Get-CimInstance Win32_UserAccount -Filter "LocalAccount=True" | Select-Object Name,SID,Status
> ```
> 
> ```powershell
> Get-CimInstance Win32_UserAccount -Filter "LocalAccount=True" | Select-Object *
> ```
> 
>- WMI can be useful when working on older Windows versions or when standard PowerShell cmdlets are unavailable.

- Retrieve complete object attributes for all local user accounts:

```powershell
Get-LocalUser | Format-List *
```

- Query user account names, description fields, and account state (`Enabled`/`Disabled`):

```powershell
Get-LocalUser | Select-Object Name,Description,Enabled
```

- Enumerate currently logged-in users (including active and disconnected user sessions):

```powershell
query user
```

>[!note] [`net user`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/net-user) · [`Get-LocalUser`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.localaccounts/get-localuser?view=powershell-5.1) · [`wmic`](https://learn.microsoft.com/en-us/windows/win32/wmisdk/wmic) · [`Get-CimInstance`](https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/get-ciminstance?view=powershell-7.6) · [`query user`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/query-user) 

### Local groups

- List local security groups:

```powershell
net localgroup
```

```powershell
Get-LocalGroup
```

>[!info]- Enumerate local groups through CIM/WMI
> 
> ```powershell
> wmic group get name,sid
> ```
> 
> ```powershell
> Get-CimInstance Win32_Group -Filter "LocalAccount=True" | Select-Object Name,SID,Description
> ```

- List members of a specific groups:

```powershell
net localgroup 'Backup Operators'
```

```powershell
Get-LocalGroupMember -Group "Backup Operators"
```

>[!tip]+
>- Enumerate privileged groups systematically:
> ```powershell
> net localgroup "Administrators" 
> net localgroup "Backup Operators" 
> net localgroup "Server Operators" 
> net localgroup "Remote Management Users" 
> net localgroup "Remote Desktop Users" 
> net localgroup "Hyper-V Administrators" 
> net localgroup "Distributed COM Users"
> ```
> ```powershell
> "Administrators", "Backup Operators", "Server Operators", "Remote Management Users", "Remote Desktop Users", "Hyper-V Administrators", "Distributed COM Users" | ForEach-Object { Get-LocalGroupMember -Group $_ -ErrorAction SilentlyContinue }
> ```

>[!info]- Enumerate members of a specific local group through CIM/WMI
> 
> ```powershell
> wmic group get name,sid
> ```
> 
> ```powershell
> Get-CimInstance Win32_GroupUser | Select-Object GroupComponent,PartComponent
> ```

>[!tip]+
> - Also query domain groups:
> 
> ```cmd
> net group /domain
> ```
> 
> ```powershell
> net group "<group>" /domain
> ```
>>[!note] [`net group`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/cc754051(v=ws.11))
>
>>[!note] See [[🛠️ AD enumeration]].

>[!note] [`net localgroup`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/cc725622(v=ws.11)) · [`Get-LocalGroup`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.localaccounts/get-localgroup?view=powershell-5.1) · [`wmic`](https://learn.microsoft.com/en-us/windows/win32/wmisdk/wmic) · [`Get-CimInstance`](https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/get-ciminstance?view=powershell-7.6) · [`Get-LocalGroupMember`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.localaccounts/get-localgroupmember?view=powershell-5.1)

### Domain/workgroup and hostname

- Determine whether the host is part of an Active Directory domain or workgroup:

```cmd
wmic computersystem get domain,partofdomain
```

```powershell
Get-CimInstance Win32_ComputerSystem | Select-Object Domain,PartOfDomain
```

- Output local hostname (useful for distinguishing local accounts from domain accounts):

```powershell
hostname
```

```powershell
$env:COMPUTERNAME
```

>[!tip] The hostname is useful to tell apart local accounts from domain accounts.

>[!note] [`wmic`](https://learn.microsoft.com/en-us/windows/win32/wmisdk/wmic) · [`Get-CimInstance`](https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/get-ciminstance?view=powershell-7.6) · [`hostname`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/hostname)

## System information 

### Operating system

- Display exact Windows release version and OS build information:

```powershell
ver
```

```powershell
systeminfo
```

```powershell
Get-CimInstance Win32_OperatingSystem | Format-List *
```

>[!tip]+
>- Record Windows edition, version, build number, and architecture. 
>- The exact build number is useful to lookup missing security patches and assess local privilege-escalation vulnerabilities, including kernel exploits.
>
>>[!note] See [[🛠️ Windows kernel exploits]].

>[!note] [`ver`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/ver) · [`systeminfo`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/systeminfo) · [`Get-CimInstance`](https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/get-ciminstance?view=powershell-7.6)

### Architecture

- Display OS architecture (`x64` vs `x86`):

```powershell
wmic os get osarchitecture
```

```powershell
Get-CimInstance Win32_OperatingSystem | Select-Object OSArchitecture
```

- Display architecture of the current process:

```powershell
echo %PROCESSOR_ARCHITECTURE% # CMD
```

```powershell
$env:PROCESSOR_ARCHITECTURE   # PowerShell
```

>[!info]- OS vs. process architecture
>- The OS architecture refers to the underlying hardware platform and bitness of the installed OS, such as `x64`, `ARM64`.
>- The architecture of the current process refers to the bitness of the specific application / runtime executing at the moment. 
>- In Windows, these values can differ because of emulation layers like **[WoW64 (Windows-on-Windows 64-bit)](https://en.wikipedia.org/wiki/WoW64)**, which allows 32-bit applications to run on 64-bit systems.

- Check current PowerShell process bitness:

```powershell
[Environment]::Is64BitProcess
```

- Check if the host OS architecture is 64-bit:

```powershell
[Environment]::Is64BitOperatingSystem
```

>[!note] [`Win32_OperatingSystem`](https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-operatingsystem) · [`Environment.Is64BitProcess`](https://learn.microsoft.com/en-us/dotnet/api/system.environment.is64bitprocess) · [`Environment.Is64BitOperatingSystem`](https://learn.microsoft.com/en-us/dotnet/api/system.environment.is64bitoperatingsystem)

### Windows build and hotfixes

- Display installed hotfixes:

```powershell
wmic qfe get HotFixID,InstalledOn,Description
```

```powershell
Get-HotFix
```

- Display recently applied patches (list the 10 most recently installed KBs sorted by date):

```powershell
Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 10
```

- Search `systeminfo` output for KB patches:

```powershell
systeminfo | Select-String "KB"
```

>[!note] On older Windows systems, `systeminfo` can provide useful patch information even when newer PowerShell cmdlets are unavailable.

>[!note] [`Get-HotFix`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-hotfix?view=powershell-5.1) · [`Win32_QuickFixEngineering`](https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-quickfixengineering)

## Environment variables

- Display all environment variables for the current session:

```powershell
set                 # CMD
```

```powershell
Get-ChildItem Env:  # PowerShell
```

- Display effective `PATH` variable:

```powershell
echo %PATH% # CMD
```

```powershell
$env:PATH   # PowerShell
```

- Split `PATH` entries line-by-line:

```powershell
$env:PATH -split ';'
```

>[!tip]+
>- Review `PATH` for writable directories, custom application directories, and any non-standard locations.
>- A writable directory in `PATH` can become relevant when a privileged process executes a command without specifying an absolute path. 
>- To find exploitation possibilities, determine whether a **privileged process** uses `PATH` to resolve an executable and whether the relevant directory can be modified by the current user.

- **Inspect key environment variables**: Query individual system environment variables:

```powershell
# CMD
echo %SystemRoot%
echo %WINDIR%
echo %TEMP%
echo %TMP%
echo %ProgramFiles%
echo %ProgramFiles(x86)%
echo %ProgramData%
echo %USERPROFILE%
```

```powershell
# PowerShell
$env:SystemRoot
$env:WINDIR
$env:TEMP
$env:TMP
$env:ProgramFiles
${env:ProgramFiles(x86)}
$env:ProgramData
$env:USERPROFILE
```

>[!tip]+
> - Environment variables can reveal:
> 	- Windows installation paths.
> 	- User-writable temporary locations.
> 	- Installed application locations.
> 	- Shared application-data directories.
> 	- Potentially interesting directories referenced by privileged applications.

## Credential hunting

>[!note] See [[🛠️ Windows credential hunting]].

## Services

- Windows services are a high-priority privilege-escalation target because they often execute automatically or on demand under privileged accounts like `LocalSystem`, `LocalService`, or `NetworkService`.
- Your goal is to identify **which privileged services execute something that the current user can influence**.

### Enumerating services

- Enumerate all registered Windows services and current statuses:

```powershell
sc query
```

```powershell
Get-Service
```

- Retrieve service name, display name, state, start mode, and executable path via CIM/WMI:

```cmd
wmic service get Name,DisplayName,State,StartMode,PathName
```

```powershell
Get-CimInstance Win32_Service | Select-Object Name,DisplayName,State,StartMode,PathName
```

>[!tip]+
>- `StartName` — account used to run the service.
>- `PathName` — service executable and its arguments.
>- `StartMode` — when and how the service starts.
>- `State` — current service state.
>- `ProcessId` — associated process ID.

- List currently running services:

```powershell
sc query state= active
```

```powershell
Get-Service | Where-Object Status -eq 'Running'
```

```powershell
Get-CimInstance Win32_Service |
    Where-Object State -eq 'Running' |
    Select-Object Name,DisplayName,StartName,PathName
```

>[!note] [`sc query`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/sc-query) · [`Get-Service`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-service) · [`wmic`](https://learn.microsoft.com/en-us/windows/win32/wmisdk/wmic) · [`Get-CimInstance`](https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/get-ciminstance?view=powershell-7.6) · [`Win32_Service`](https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-service)

### Privileged services

- Filter services running as built-in privileged accounts (services running as `SYSTEM`, `LocalService`, or `NetworkService`):

```powershell
Get-CimInstance Win32_Service |
    Where-Object {
        $_.StartName -in @(
            'LocalSystem',
            'NT AUTHORITY\SYSTEM',
            'LocalService',
            'NT AUTHORITY\LocalService',
            'NetworkService',
            'NT AUTHORITY\NetworkService'
        )
    } |
    Select-Object Name,StartName,State,StartMode,PathName
```

- Filter services running as `SYSTEM`:

```powershell
Get-CimInstance Win32_Service |
    Where-Object {
        $_.StartName -match '^(LocalSystem|NT AUTHORITY\\SYSTEM)$'
    } |
    Select-Object Name,State,StartMode,StartName,PathName
```

>[!info]- Enumerate services and display account context through CIM/WMI
> 
> ```powershell
> wmic service get Name,StartName
> ```
> 
> ```powershell
> Get-CimInstance Win32_Service | Select-Object Name,StartName
> ```

>[!tip] Pay special attention to services running as `LocalSystem` (or privileged domain accounts) that point to custom / non-standard binary locations. These are potential paths to privilege escalation.

>[!note] [`Get-CimInstance`](https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/get-ciminstance?view=powershell-7.6) · [`Win32_Service`](https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-service)

### Inspecting a specific service

- Display service configuration (binary path, start type, account):

```powershell
sc qc <service_name>
```

```powershell
Get-CimInstance Win32_Service -Filter "Name='<service_name>'" | Select-Object Name,PathName,StartName,StartMode
```

- Display service operational state (and process ID):

```powershell
sc query <service>
```

- Display extended service information (process ID and service flags):

```powershell
sc queryex <service>
```

- Display complete service CIM object (all properties):

```powershell
Get-CimInstance Win32_Service -Filter "Name='<service>'" | Format-List *
```

>[!note] [`sc qc`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/sc-qc) · [`sc query`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/sc-query) · [`sc queryex`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/sc-queryex) · [`Get-CimInstance`](https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/get-ciminstance?view=powershell-7.6)

### Service executable paths

- Display service binary paths across all services:

```powershell
wmic service get Name,StartName,PathName
```

```powershell
Get-CimInstance Win32_Service |
    Where-Object PathName |
    Select-Object Name,StartName,PathName
```

>[!tip]+ What to look for in `PathName`:
>- Executables **outside standard Windows directories**.
>- Executables in **writable directories** or **custom application directories**; interesting locations include `C:\Users\`, `C:\Temp\`, `C:\Windows\Temp\`, `C:\ProgramData\`, `C:\Public\`, and others.
>- Scripts (`.bat`, `.cmd`, `.ps1`, `.vbs`, `.py`).
>- **Unquoted paths containing spaces**.
>- **Missing executables**.
>- **Relative paths**.
>- Additional **command-line arguments**.

>[!note] [`wmic`](https://learn.microsoft.com/en-us/windows/win32/wmisdk/wmic) · [`Get-CimInstance`](https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/get-ciminstance?view=powershell-7.6)

#### Unquoted service paths

- Search unquoted service paths containing space delimiters:

```powershell
Get-CimInstance Win32_Service | 
	Where-Object { 
		$_.PathName -and
		$_.PathName -notmatch '^"' -and
		$_.PathName -match ' ' 
	} | Select-Object Name, DisplayName, PathName   
```

>[!note]+ Command breakdown
>- `$_.PathName` matches objects with the `PathName` property set.
>- `$_.PathName -notmatch '^"'` matches `PathName` attributes that do not start with a quote `"`.
>- `$_.PathName -match ' '` matches `PathName` that contain spaces. 

- Query service binary paths using `wmic`:

```powershell
wmic service get Name,StartName,PathName
```

>[!note] See [[Unquoted service paths]].

>[!note] [`Get-CimInstance`](https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/get-ciminstance?view=powershell-7.6) · [`wmic`](https://learn.microsoft.com/en-us/windows/win32/wmisdk/wmic)

### Binary and directory permissions

- Display executable path for a specific service:

```powershell
Get-CimInstance Win32_Service -Filter "Name='<service>'" |
    Select-Object Name,StartName,PathName
```

- Check service binary permissions (look for modification rights):

```powershell
icacls "C:\Program Files\Example\App\example.exe"
```

```powershell
Get-Acl "C:\Program Files\Example\App\example.exe" | Format-List
```
 
- Check permissions of all parent directories along the service binary path:

```powershell
icacls "C:\Program Files\Example\App\"
icacls "C:\Program Files\Example\"
icacls "C:\Program Files\"
icacls "C:\"
```

>[!tip]+
>- A non-writable executable can still be exploitable if the current user can manipulate any parent directory in a way that allows the executable to be replaced (or otherwise influences execution). 
>- Also examine permissions on files loaded or referenced by the service binary.

>[!note] [`Get-CimInstance`](https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/get-ciminstance?view=powershell-7.6) · [`icacls`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls) · [`Get-Acl`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/get-acl?view=powershell-7.5)

### Service configuration permissions

- Display SDDL (Security Descriptor Definition Language) string for service:

```powershell
sc sdshow <service_name>
```

- Display service configuration — check if low-privileged account can reconfigure service binary path:

```powershell
sc qc <service_name>
```

>[!tip]+
>- Service permissions determine who can start, stop, pause, query, delete, or change the configuration of the service. 
>- A service running as `SYSTEM` is especially interesting if a low-privileged user has `SERVICE_CHANGE_CONFIG` or `SERVICE_ALL_ACCESS`.

- Audit permissions on a specific Windows service using `AccessChk` (identify privilege escalation vectors):

```powershell
accesschk.exe -c <service>
```

>[!note] `AccessChk` inspects service DACL to detect services where low-privileged users have write access (privilege escalation vector).

- Audit permissions across all installed services:

```powershell
accesschk.exe -c *
```

- List services writable by a specific user:

```powershell
accesschk.exe -c -u <username> *
```

>[!note] [`sc sdshow`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/cc742133(v=ws.11)) · [`sc qc`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/cc742055(v=ws.11)) · [`AccessChk`](https://learn.microsoft.com/en-us/sysinternals/downloads/accesschk)

### Service registry configuration

>[!tip] Service configuration is stored under `HKLM\SYSTEM\CurrentControlSet\Services\`.

- Query registry keys for a specific service configuration:

```powershell
reg query "HKLM\SYSTEM\CurrentControlSet\Services\<service>"
```

```powershell
Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Services\<service>"
```

- Recursively list subkeys under target service registry path:

```powershell
reg query "HKLM\SYSTEM\CurrentControlSet\Services\<service>" /s
```

- Check ACLs on service registry key (search for write access):

```powershell
reg query "HKLM\SYSTEM\CurrentControlSet\Services\<service_name>"
```

```powershell
Get-Acl -Path "HKLM:\SYSTEM\CurrentControlSet\Services\<service_name>" | Format-List
```

>[!tip]+
> - If a low-privileged account has write permissions on the service registry key, you can often modify `ImagePath` (`binPath`) to **execute arbitrary code as the service account** (like `SYSTEM`). 
> - Look for `SERVICE_CHANGE_CONFIG` or `SERVICE_ALL_ACCESS`.

>[!note] [`reg query`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/reg-query) · [`Get-ItemProperty`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-itemproperty?view=powershell-7.6) · [`Get-Acl`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/get-acl)

### Dependencies and hosted services

- Display service configuration — inspect required service dependencies:

```powershell
sc qc <service_name>
```

```powershell
sc enumdepend <service_name>
```

```powershell
Get-Service <service_name> -DependentServices
```

```powershell
Get-Service <service_name> -RequiredServices
```

- Group services sharing process IDs (e.g., shared `svchost` processes):

```powershell
Get-CimInstance Win32_Service |
    Where-Object ProcessId -ne 0 |
    Group-Object ProcessId |
    Where-Object Count -gt 1 |
    Select-Object Name,Count,Group
```

- Query process IDs associated with active services:

```powershell
sc queryex type= service state= all
```

```powershell
Get-CimInstance Win32_Service | Select-Object Name,ProcessId,StartName,State
```

>[!note] [`sc qc`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/sc-qc) · [`sc enumdepend`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/sc-enumdepend) · [`Get-Service`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-service) · [`Get-CimInstance`](https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/get-ciminstance?view=powershell-7.6)

## Processes

- Processes are another high-value target during local privilege escalation. Privileged processes (especially those running as `SYSTEM` or high-privileged users) may load writable DLLs, execute binaries from weak locations, or expose other hijacking opportunities.
- Your goal is to identify processes running with elevated privileges whose binary, working directory, or loaded modules can be influenced by the current user.

### Enumerating processes

- List running processes:

```powershell
tasklist
```

```powershell
Get-Process
```

- List processes with associated service bindings:

```cmd
tasklist /svc
```

- Query process ID, name, binary path, and command line arguments:

```powershell
Get-CimInstance Win32_Process | Select-Object ProcessId,Name,ExecutablePath,CommandLine
```

```powershell
wmic process get ProcessId,Name,ExecutablePath,CommandLine
```

- List third-party processes (exclude core Windows system directories to identify non-standard applications):

```powershell
Get-Process | Where-Object { $_.Path -and $_.Path -notmatch 'Windows|System32|SysWOW64' } | Select-Object Id,Name,Path
```

>[!tip]+
> - Focus on processes running as `SYSTEM`, high-privileged service accounts, or administrative users.
> - Note non-standard / third-party processes and processes started from unusual locations.

>[!note] [`tasklist`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/tasklist) · [`Get-Process`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-process) · [`Get-CimInstance`](https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/get-ciminstance?view=powershell-7.6) · [`Win32_Process`](https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-process)

### Process owners

- Display owner account for active processes (domain and username):

```powershell
Get-CimInstance Win32_Process | ForEach-Object {
    $owner = $_.GetOwner()
    [PSCustomObject]@{
        ProcessId = $_.ProcessId
        Name      = $_.Name
        User      = "$($owner.Domain)\$($owner.User)"
    }
}
```

- List processes and associated user accounts:

```powershell
tasklist /v /fo list
```

>[!tip] Processes running as `NT AUTHORITY\SYSTEM`, `LOCAL SERVICE`, `NETWORK SERVICE`, or administrative users are the most interesting.

- List background processes executing in system session context:

```powershell
Get-Process | Where-Object { $_.SessionId -eq 0 }
```

>[!note] [`Get-CimInstance`](https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/get-ciminstance?view=powershell-7.6) · [`tasklist`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/tasklist) · [`Get-Process`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-process)

### Process command lines and executable paths

- Inspect complete command-line strings used to launch processes, such as to find credentials in command-line or paths to configuration files:

```powershell
Get-CimInstance Win32_Process | Select-Object ProcessId,Name,CommandLine | Format-List
```

```powershell
wmic process get ProcessId,Name,CommandLine
```

- Display process executable binary paths:

```powershell
Get-CimInstance Win32_Process | Where-Object ExecutablePath | Select-Object Name,ExecutablePath
```

>[!tip] Always inspect the full command line. Scripts, configuration files, or additional binaries referenced in arguments can be valuable targets.

>[!note] [`Get-CimInstance`](https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/get-ciminstance?view=powershell-7.6) · [`wmic`](https://learn.microsoft.com/en-us/windows/win32/wmisdk/wmic)

### Binary and directory permissions

- Check process binary permissions (look for modification rights):

```powershell
icacls "C:\Program Files\Example\App\example.exe"
```

```powershell
Get-Acl "C:\Program Files\Example\App\example.exe" | Format-List
```

- Check permissions of all parent directories along the process executable path:

```powershell
icacls "C:\Program Files\Example\App\"
icacls "C:\Program Files\Example\"
icacls "C:\Program Files\"
icacls "C:\"
```

>[!tip]+
>- A **writable process binary** or a **writable directory in its path** may allow [[DLL hijacking|DLL hijacking]].
>- A non-writable executable can still be exploitable if the current user can manipulate ***any parent directory*** in a way that allows the executable to be replaced (or otherwise influences execution). 
>- Also checks permissions on files loaded or referenced by the binary.

>[!note] [`icacls`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls) · [`Get-Acl`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/get-acl)

## Scheduled tasks & autostart locations

>[!important] Tasks configured to run as `SYSTEM` or other privileged accounts — and that execute binaries or scripts from locations writable by the current user — are potential targets for privilege escalation.
### Enumerating scheduled tasks

- List all registered scheduled tasks across the system:

```powershell
schtasks /query /fo LIST /v
```

```powershell
Get-ScheduledTask
```

- Display task execution details and state:

```powershell
schtasks /query /fo LIST /v
```

```powershell
Get-ScheduledTask | Get-ScheduledTaskInfo
```

```powershell
Get-ScheduledTask | Select-Object TaskName,TaskPath,State | Format-Table -AutoSize
```

- Extract action commands (look for executable paths to inspect later):

```powershell
Get-ScheduledTask | ForEach-Object {
    $actions = $_.Actions
    [PSCustomObject]@{
        TaskName = $_.TaskName
        Execute  = $actions.Execute
        Arguments = $actions.Arguments
    }
}
```

>[!tip]+
>- Focus on tasks that run as `SYSTEM` or other high-privileged accounts.
>- Pay attention to tasks with `Run level = Highest` or tasks that are triggered frequently / at logon / at startup.

>[!note] [`schtasks`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks-query) · [`Get-ScheduledTask`](https://learn.microsoft.com/en-us/powershell/module/scheduledtasks/get-scheduledtask)

### Privileged scheduled tasks

- Filter tasks running as `SYSTEM` or `Administrator`:

```powershell
Get-ScheduledTask | Where-Object { $_.Principal.UserId -match 'SYSTEM|Administrator' } | 
    Select-Object TaskName,TaskPath,State,@{n='RunAs';e={$_.Principal.UserId}}
```

```powershell
schtasks /query /fo LIST /v | findstr /i "SYSTEM Run Level"
```

>[!note] [`Get-ScheduledTask`](https://learn.microsoft.com/en-us/powershell/module/scheduledtasks/get-scheduledtask) · [`schtasks`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks-query)

### Task binary and directory permissions

- Check permissions on executable invoked by a privileged task (look for modification rights):

```powershell
icacls "C:\Program Files\Example\App\example.exe"
```

```powershell
Get-Acl "C:\Program Files\Example\App\example.exe" | Format-List
```

- Check permissions of all parent directories along the executable path:

```powershell
icacls "C:\Program Files\Example\App\"
icacls "C:\Program Files\Example\"
icacls "C:\Program Files\"
icacls "C:\"
```

- Audit permissions on task definition files and directories:

```powershell
accesschk.exe -cveu "C:\Windows\System32\Tasks" /accepteula
```

>[!tip]+ Also inspect any configuration files or DLLs loaded by the task binary.

>[!note] [`icacls`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls) · [`Get-Acl`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/get-acl)

### Autostart locations

>[!important] Windows has multiple locations that automatically execute programs at startup or logon. Weak permissions in these locations can lead to privilege escalation or  persistence.
#### Registry Run keys

- Query system-wide and user-specific `Run` and `RunOnce` registry keys:

```powershell
# system-wide
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"

# specific to the current user
reg query "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
reg query "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"
```

```powershell
# system-wide
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"

# specific to the current user
Get-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
```

>[!note] [`reg query`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/reg-query) · [`Get-ItemProperty`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-itemproperty)

#### Startup folders

- Inspect system-wide and user-specific `StartUp` folders: 

```powershell
dir "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp"
```

```powershell
dir "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
```

>[!note] [`dir`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/dir) · [`Get-ChildItem`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-childitem?view=powershell-7.6)

#### Other common autorun locations

- Inspect additional registry paths used for automatic execution (logon policies and init scripts):

```powershell
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer\Run"
```

```powershell
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v Userinit
```

```powershell
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v Shell
```

```powershell
reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager" /v BootExecute
```

>[!note] [`reg query`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/reg-query) 

## File system permissions

>[!important] Weak file and directory permissions are one of the most common and reliable privilege-escalation vectors on Windows. 
> - The goal is to find locations where a privileged process or service reads, writes, or executes something that the current low-privileged user can modify.
### Interesting directories

- Audit permissions on common application and temporary folders:

```powershell
icacls "C:\Program Files"
icacls "C:\Program Files (x86)"
icacls "C:\ProgramData"
icacls "C:\Windows\Temp"
icacls "C:\Temp"
icacls "C:\Users\Public"
```

```powershell
Get-Acl "C:\Program Files" | Format-List
Get-Acl "C:\ProgramData" | Format-List
```

- Search for writable directories recursively using `AccessChk`:

```powershell
accesschk.exe -uwdqs Users C:\
accesschk.exe -uwdqs "Authenticated Users" C:\
```

```powershell
accesschk.exe -uwdqs Users "C:\Program Files"
accesschk.exe -uwdqs Users "C:\Program Files (x86)"
accesschk.exe -uwdqs Users "C:\ProgramData"
```

>[!tip]+ Pay special attention to:
>- Writable directories inside `C:\Program Files` or `C:\Program Files (x86)`.
>- `C:\ProgramData` subfolders used by services or scheduled tasks.
>- World-writable directories used by privileged processes. 
>- Directories that appear in the `PATH` environment variable.

>[!note] [`icacls`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls) · [`Get-Acl`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/get-acl) · [`AccessChk`](https://learn.microsoft.com/en-us/sysinternals/downloads/accesschk)

### Writable files used by privileged processes

- Check permissions on executable invoked by a privileged task (look for modification rights):

```powershell
icacls "C:\Program Files\Example\App\example.exe"
```

```powershell
Get-Acl "C:\Program Files\Example\App\example.exe" | Format-List
```

- Check permissions of all parent directories along the executable path:

```powershell
icacls "C:\Program Files\Example\App\"
icacls "C:\Program Files\Example\"
icacls "C:\Program Files\"
icacls "C:\"
```

>[!tip]+
>- A non-writable binary can still be exploitable if any parent directory allows file creation/replacement.
>- Also inspect configuration files, scripts, and DLLs loaded by the privileged binary.

>[!note] [`icacls`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls) · [`Get-Acl`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/get-acl)

### `PATH` directories

- Iterate through directories in system `PATH` and check permissions:

```powershell
$env:PATH -split ';' | ForEach-Object { if ($_ -and (Test-Path $_)) { icacls $_ } }
```

- Output structured ACL string for each  directory in `PATH`:

```powershell
$env:PATH -split ';' | ForEach-Object {
    if ($_ -and (Test-Path $_)) {
        [PSCustomObject]@{
            Path = $_
            Acl  = (Get-Acl $_).AccessToString
        }
    }
}
```

>[!tip] A writable directory in `PATH` becomes dangerous when a privileged process executes a command without a full path ([[DLL hijacking|DLL hijacking]]).

>[!note] [`icacls`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls) · [`Get-Acl`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/get-acl)

### `AccessChk`

- Find directories writable by low-privileged groups (`Users`, `Authenticated Users`, `Everyone`):

```powershell
accesschk.exe -uwdqs Users C:\
accesschk.exe -uwdqs "Authenticated Users" C:\
accesschk.exe -uwdqs Everyone C:\
```

- Find files writable by low-privileged groups: 

```powershell
accesschk.exe -uwqs Users C:\
accesschk.exe -uwqs "Authenticated Users" C:\
accesschk.exe -uwqs Everyone C:\
```

>[!note] [`AccessChk`](https://learn.microsoft.com/en-us/sysinternals/downloads/accesschk)

## Registry

- The Windows Registry stores service configurations, autorun entries, application settings, and sometimes credentials.
- Weak permissions on sensitive keys can allow privilege escalation (for example by modifying a service `ImagePath`).

### Interesting registry keys

- List service registry keys (under `CurrentControlSet`):

```powershell
reg query "HKLM\SYSTEM\CurrentControlSet\Services"
```

```powershell
Get-ChildItem "HKLM:\SYSTEM\CurrentControlSet\Services" | Select-Object Name
```

- Query system-wide and user-specific `Run` and `RunOnce` registry keys:

```powershell
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"
reg query "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
reg query "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"
```

```powershell
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
Get-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
```
 
- Query policy settings that enable elevated MSI installation (`AlwaysInstallElevated`):

```powershell
reg query "HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer" /v AlwaysInstallElevated
reg query "HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer" /v AlwaysInstallElevated
```

```powershell
Get-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Installer" -Name AlwaysInstallElevated -ErrorAction SilentlyContinue
Get-ItemProperty "HKCU:\SOFTWARE\Policies\Microsoft\Windows\Installer" -Name AlwaysInstallElevated -ErrorAction SilentlyContinue
```

- Query auxiliary system registry keys (inspect `Winlogon`, `BootExecute`, `Policy Run` keys):

```powershell
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager" /v BootExecute
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer\Run"
```

>[!tip]+ Always check both the values and the permissions on the key itself.

>[!note] [`reg query`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/reg-query) · [`Get-ItemProperty`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-itemproperty) · [`Get-ChildItem`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-childitem)

### Registry key permissions

- Inspect permissions on a specific service registry key:

```powershell
Get-Acl "HKLM:\SYSTEM\CurrentControlSet\Services\<service_name>" | Format-List
```

```powershell
reg query "HKLM\SYSTEM\CurrentControlSet\Services\<service_name>"
```

- Inspect permissions on autorun keys:

```powershell
Get-Acl "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" | Format-List
Get-Acl "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce" | Format-List
```

- Find writable registry keys using `AccessChk` (scans registry hives for keys writable by low-privileged groups):

```powershell
accesschk.exe -kvuqsw "Authenticated Users" hklm\software
accesschk.exe -kvuqsw Users hklm\system\currentcontrolset\services
accesschk.exe -kvuqsw "Authenticated Users" hklm\system\currentcontrolset\services
```

>[!tip]+
>- Look for keys where the current user (or `Users` / `Authenticated Users` / `Everyone`) has `Full Control`, `Set Value`, `Create Subkey`, or `Write` permissions.
>- Being able to modify a service `ImagePath` or an autorun value that executes in a privileged context is often enough for privilege escalation.

>[!note] [`Get-Acl`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/get-acl) · [`reg query`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/reg-query) · [`AccessChk`](https://learn.microsoft.com/en-us/sysinternals/downloads/accesschk)

### Searching the registry

- Search registry for credential/password strings:

```powershell
reg query HKLM /f "password" /t REG_SZ /s
reg query HKCU /f "password" /t REG_SZ /s
```

```powershell
reg query HKLM /f "password" /t REG_SZ /s
reg query HKLM /f "pwd" /t REG_SZ /s
reg query HKLM /f "cred" /t REG_SZ /s
```

>[!tip] Registry searches can be very slow. Prefer targeted searches under `HKLM\SOFTWARE`, `HKLM\SYSTEM`, and `HKCU` rather than the entire registry when possible.

>[!note] [`reg query`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/reg-query)

## Installed software and drivers

>[!important] Installed third-party software and drivers often introduce privilege-escalation opportunities, such as through outdated versions, weak permissions, or known vulnerable drivers.
### Installed software

- List installed software via `Uninstall` registry keys:

```powershell
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*", 
	"HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*" |
    Select-Object DisplayName,DisplayVersion,Publisher,InstallLocation | Format-Table -AutoSize
```

```powershell
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" /s
reg query "HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall" /s
```

>[!note]+ List installed software via CIM/WMI (software names and versions):
> ```powershell
> wmic product get Name,Version,Vendor
> ```
> 
> ```powershell
> Get-CimInstance Win32_Product | Select-Object Name,Version,Vendor
> ```
> 
>>[!warning] Querying **`Win32_Product`** is **strongly discouraged**. Not only is it slow, but every query triggers a consistency check on all MSI-installed applications, which can initiate **silent, automatic repairs** and potentially **reset local configurations** (e.g., network driver settings).
>>- Query `Uninstall` registry keys instead whenever possible (quick and safe).

- Inspect standard software installation directories — check subfolders in `Program Files` and `ProgramData`:

```powershell
dir "C:\Program Files"
```

```powershell
dir "C:\Program Files (x86)"
```

```powershell
dir "C:\ProgramData"
```

>[!tip]+
> - Note non-Microsoft software, especially outdated software (potentially with known local privilege-escalation vulnerabilities), software running as service or scheduled tasks, and applications installed in unusual or writable locations.
> - Always cross-reference interesting software with the services, processes, and scheduled tasks you already enumerated.

>[!note] [`wmic`](https://learn.microsoft.com/en-us/windows/win32/wmisdk/wmic) · [`Get-CimInstance`](https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/get-ciminstance?view=powershell-7.6) · [`Get-ItemProperty`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-itemproperty) · [`reg query`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/reg-query)

### Drivers

- List loaded kernel drivers:

```powershell
driverquery
```

```powershell
driverquery /v /fo list
```

```powershell
Get-CimInstance Win32_SystemDriver | Select-Object Name,State,PathName,StartMode
```

- Display signed driver info (provider names and versions):

```powershell
driverquery /si
```

```powershell
Get-WindowsDriver -Online -All | Select-Object Driver,OriginalFileName,ProviderName,Date,Version
```

>[!tip]+
> - Look for third-party or outdated drivers.
> - Vulnerable drivers (especially those allowing arbitrary kernel read/write) can be abused for privilege escalation or credential extraction (e.g., bringing your own vulnerable driver).
> - Note the path of non-Microsoft drivers and check their file permissions.

>[!note] [`driverquery`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/driverquery) · [`Get-CimInstance`](https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/get-ciminstance?view=powershell-7.6) · [`Get-WindowsDriver`](https://learn.microsoft.com/en-us/powershell/module/dism/get-windowsdriver)

## Network enumeration

>[!important] Network information helps identify additional attack surface, potential lateral movement paths, and services listening on the local machine that may be running with elevated privileges.
### Network interfaces and IP addresses

- Display IP configuration (network interfaces, gateway, DNS servers):

```powershell
ipconfig /all
```

```powershell
Get-NetIPAddress
```

```powershell
Get-NetIPConfiguration
```

```powershell
Get-CimInstance Win32_NetworkAdapterConfiguration | Where-Object IPEnabled -eq $true | Select-Object Description,IPAddress,IPSubnet,DefaultIPGateway,DNSServerSearchOrder
```

>[!note] [`ipconfig`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/ipconfig) · [`Get-NetIPAddress`](https://learn.microsoft.com/en-us/powershell/module/nettcpip/get-netipaddress) · [`Get-NetIPConfiguration`](https://learn.microsoft.com/en-us/powershell/module/nettcpip/get-nettcpconfiguration) · [`Get-CimInstance`](https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/get-ciminstance?view=powershell-7.6)

### Listening ports and connections


- Display all listening TCP/UDP ports and active socket connections (including process IDs):

```powershell
netstat -ano
```

```powershell
netstat -ano | findstr LISTENING
```

```powershell
Get-NetTCPConnection | Select-Object LocalAddress,LocalPort,State,OwningProcess
```

```powershell
Get-NetTCPConnection -State Listen | Select-Object LocalAddress,LocalPort,OwningProcess
```

- Map listening ports to owning process IDs and names: 

```powershell
netstat -ano
tasklist /fi "pid eq <PID>"
```

```powershell
Get-NetTCPConnection -State Listen | ForEach-Object {
    $p = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
    [PSCustomObject]@{
        LocalAddress = $_.LocalAddress
        LocalPort    = $_.LocalPort
        PID          = $_.OwningProcess
        ProcessName  = $p.ProcessName
    }
}
```

>[!tip]+
> - Focus on listening ports bound to privileged processes.
> - Unusual high ports or services listening only on localhost can still be interesting if they run as `SYSTEM`.

>[!note] [`netstat`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/netstat) · [`Get-NetTCPConnection`](https://learn.microsoft.com/en-us/powershell/module/nettcpip/get-nettcpconnection) · [`Get-Process`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-process) · [`tasklist`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/tasklist)

### Shares

- List SMB network shares exported by the system:

```powershell
net share
```

```powershell
Get-SmbShare
```

```powershell
wmic share get Name,Path,Description
```

- List active remote share connections (and mapped drives):

```powershell
net use
```

>[!note] [`net share`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/bb490949(v=ws.11)) · [`Get-SmbShare`](https://learn.microsoft.com/en-us/powershell/module/smbshare/get-smbshare) · [`wmic`](https://learn.microsoft.com/en-us/windows/win32/wmisdk/wmic) · [`net use`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/bb490948(v=ws.11))

### Routing and ARP

- Display IP routing table (static and dynamic routes):

```powershell
route print
```

```powershell
Get-NetRoute
```

- Display ARP cache table:

```powershell
arp -a
```

```powershell
Get-NetNeighbor
```

>[!note] [`route`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/route) · [`Get-NetRoute`](https://learn.microsoft.com/en-us/powershell/module/nettcpip/get-netroute) · [`arp`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/arp) · [`Get-NetNeighbor`](https://learn.microsoft.com/en-us/powershell/module/nettcpip/get-netneighbor)

## Security tools and controls

### Antivirus / EDR / security products

- Query installed AV and EDR software:

```powershell
wmic /namespace:\\root\securitycenter2 path antivirusproduct get displayName,productState
```

```powershell
Get-CimInstance -Namespace "root\SecurityCenter2" -ClassName AntivirusProduct | Select-Object displayName,productState
```

- Match active processes against common EDR keywords:

```powershell
Get-Process | Where-Object { $_.ProcessName -match 'defender|crowdstrike|csfalcon|sentinel|carbonblack|cb|symantec|norton|mcafee|sophos|trend|eset|bitdefender|avast|avg' }
```

```powershell
Get-Service | Where-Object { $_.DisplayName -match 'defender|crowd|falcon|sentinel|carbon|symantec|mcafee|sophos|trend|eset|bitdefender' }
```

>[!tip] Presence of strong EDR does not mean privilege escalation is impossible, but it should influence your choice of tools and techniques (prefer living-off-the-land and other methods that don't make much noise).

>[!note] [`wmic`](https://learn.microsoft.com/en-us/windows/win32/wmisdk/wmic) · [`Get-CimInstance`](https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/get-ciminstance?view=powershell-7.6) · [`Get-Process`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-process) · [`Get-Service`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-service)

### AppLocker / WDAC / software restriction

- Query active AppLocker policies (XML/structured format):

```powershell
Get-AppLockerPolicy -Effective -Xml
```

```powershell
Get-AppLockerPolicy -Effective | Select-Object -ExpandProperty RuleCollections
```

- Query active WDAC (Windows Defender Application Control) and CI (Code Integrity) policies:

```powershell
Get-CimInstance -Namespace root\Microsoft\Windows\CI -ClassName PS_CodeIntegrityPolicy -ErrorAction SilentlyContinue
```

```powershell
reg query "HKLM\SYSTEM\CurrentControlSet\Control\CI\Policy"
```

>[!note] [`Get-AppLockerPolicy`](https://learn.microsoft.com/en-us/powershell/module/applocker/get-applockerpolicy) · [`Get-CimInstance`](https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/get-ciminstance?view=powershell-7.6) · [`reg query`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/reg-query)

### Windows Defender

- Display Defender operational status (real-time protection, signature versions, engine status):

```powershell
Get-MpComputerStatus
```

- Display Defender configuration and scan rules::

```powershell
Get-MpPreference
```

- Display excluded paths and processes:

```powershell
Get-MpPreference | Select-Object -ExpandProperty ExclusionPath
```

```powershell
Get-MpPreference | Select-Object -ExpandProperty ExclusionProcess
```

>[!note] [`Get-MpComputerStatus`](https://learn.microsoft.com/en-us/powershell/module/defender/get-mpcomputerstatus) · [`Get-MpPreference`](https://learn.microsoft.com/en-us/powershell/module/defender/get-mppreference)

### Firewall

- Check firewall status across all profiles (display `Domain`, `Private`, and `Public` firewall states):

```powershell
netsh advfirewall show allprofiles
```

```powershell
Get-NetFirewallProfile | Select-Object Name,Enabled
```

>[!note] [`netsh`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/netsh) · [`Get-NetFirewallProfile`](https://learn.microsoft.com/en-us/powershell/module/netsecurity/get-netfirewallprofile)

### User Account Control (UAC)

- Check UAC registry keys (including `EnableLUA` and consent prompts):

```powershell
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v EnableLUA
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v ConsentPromptBehaviorAdmin
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v PromptOnSecureDesktop
```

```powershell
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" | Select-Object EnableLUA,ConsentPromptBehaviorAdmin,PromptOnSecureDesktop
```

>[!note] See [[🛠️ UAC bypasses]].

>[!note] [`reg query`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/reg-query) · [`Get-ItemProperty`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-itemproperty)

### LSA protection and Credential Guard

- Query `RunAsPPL` registry value to check LSA process isolation status:

```powershell
reg query HKLM\SYSTEM\CurrentControlSet\Control\Lsa /v RunAsPPL
```

- Query `LsaCfgFlags` registry value to check Credential Guard status:

```powershell
reg query HKLM\SYSTEM\CurrentControlSet\Control\Lsa /v LsaCfgFlags
```

>[!tip]+
>- `RunAsPPL = 1` or `2`: LSA protection is enabled as a Protected Process Light (PPL), which prevents unauthenticated memory dumping (e.g., Mimikatz `sekurlsa::logonpasswords`) without a signed driver or PPL bypass.

>[!note] [`LSA Protection`](https://learn.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/configuring-additional-lsa-protection)

## Automated enumeration tools

>[!important] Automated tools are extremely useful to quickly identify low-hanging fruit, but they should never replace manual understanding.

### `PrivescCheck`

- Download and execute `PrivescCheck` in memory (without writing the script to disk):

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
. .\PrivescCheck.ps1
Invoke-PrivescCheck -Extended
```

### `winPEAS`

- Execute `winPEAS` in quiet fast mode:

```powershell
winPEASx64.exe quiet cmd fast
```

- Execute `winPEAS` with full log output:

```powershell
winPEASx64.exe searchfast log
```

### `Seatbelt`

- Audit host security and system configuration:

```powershell
Seatbelt.exe -group=system
```

- Audit user configuration and session artifacts:

```powershell
Seatbelt.exe -group=user
```

- Run all `Seatbelt` checks:

```powershell
Seatbelt.exe -group=all
```

### `PowerUp`

- Import `PowerUp` module:

```powershell
Import-Module .\PowerUp.ps1
```

- Execute all privilege escalation checks:

```powershell
Invoke-AllChecks
```

>[!note] [`PrivescCheck`](https://github.com/itm4n/PrivescCheck) · [`winPEAS`](https://github.com/peass-ng/PEASS-ng/tree/master/winPEAS) · [`Seatbelt`](https://github.com/GhostPack/Seatbelt) · [`PowerUp`](https://github.com/PowerShellEmpire/PowerTools/tree/master/PowerUp) · [`SharpUp`](https://github.com/GhostPack/SharpUp) · [`AccessChk`](https://learn.microsoft.com/en-us/sysinternals/downloads/accesschk)

## References and further reading

- [`Windows Commands — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/windows-commands)
- [`PrivescCheck — GitHub Repository`](https://github.com/itm4n/PrivescCheck)
- [`WinPEAS — Privilege Escalation Awesome Scripts`](https://github.com/peass-ng/PEASS-ng/tree/master/winPEAS)
- [`Seatbelt — GhostPack Toolset`](https://github.com/GhostPack/Seatbelt)
- [`PowerUp — PowerShellEmpire`](https://github.com/PowerShellEmpire/PowerTools/tree/master/PowerUp)
- [`PowerUp — PowerShellEmpire`](https://github.com/PowerShellEmpire/PowerTools/tree/master/PowerUp)