---
created: 2026-07-20
tags:
  - Windows
  - Windows_PrivEsc
  - cheatsheet
status: incomplete
---
>[!note] See [`Windows Commmands — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/windows-commands).

## General system information

- Key objectives:
	- **OS name**: Windows OS type (workstation or server) and level (Windows 7 or 10, Server 2008, 2012, 2016, 2019, etc.).
	- **OS version** (search for known vulnerabilities and public exploits).
	- **Running services** (especially those running as `NT AUTHORITY\SYSTEM` or an administrator-level account).

>[!note] See [`Comparison of Microsoft Windows versions — Wikipedia`](https://en.wikipedia.org/wiki/Comparison_of_Microsoft_Windows_versions).
### System and configuration information

- Display Windows version and build number:

```powershell
winver
```

- Display detailed system configuration, including OS name/version, build, architecture, installed hotfixes, and so on:

```bash
systeminfo
```

>[!note] See [`systeminfo`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/systeminfo).

```powershell
wmic os get Caption,Version,BuildNumber,OSArchitecture
```

>[!note]+ Output breakdown
> - `Caption` -> OS name
> - `Version` -> internal version number
> - `BuildNumber` -> OS build
> - `OSArchitecture` -> 32 or 64-bit

- In PowerShell, use [`Get-WmiObject`](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-wmiobject?view=powershell-5.1):

```powershell
Get-WmiObject -Class Win32_OperatingSystem | Select Version,BuildNumber
```

- Or [`Get-CimInstance`](https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/get-ciminstance?view=powershell-7.5) (same results):

```powershell
Get-CimInstance Win32_OperatingSystem | Select Caption, Version, BuildNumber, OSArchitecture
```

>[!warning] `Get-WmiObject` is deprecated in favor of [`Get-CimInstance`](https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/get-ciminstance?view=powershell-7.5) in PowerShell 3.0.

-  [`Get-ComputerInfo`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-computerinfo?view=powershell-7.5) (registry + WMI data):

```powershell
Get-ComputerInfo | Select-Object OSName, OSDisplayVersion, OSVersion, WindowsEditionId, WindowsProductName
```

- The `OS` environment variable stores OS family name (`Windows_NT`), and the:

```powershell
$env:OS
```

- The `PROCESSOR_ARCHITECTURE` variable shows CPU architecture (e.g., AMD64, x86, etc.):

```powershell
$env:PROCESSOR_ARCHITECTURE
```

### Patches and updates

- Display hotfixes and updates:

```bash
wmic qfe
```

>[!note] See [`QFE (Quick Fix Engineering) — Microsoft Learn`](https://docs.microsoft.com/en-us/windows/win32/cimwin32prov/win32-quickfixengineering).

- In PowerShell, use [`Get-Hotfix`](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-hotfix?view=powershell-7.1):

```powershell
Get-HotFix | ft -AutoSize
```

>[!tip] [`Format-Table`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/format-table?view=powershell-7.5) (`ft`) formats output as a table.

- Check if a specific KB is installed:

```powershell
Get-HotFix -Id KB5001234
```

>[!note] See [`Get-Hotfix`](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-hotfix?view=powershell-7.1).

### Running processes and services

- Running processes:

```powershell
tasklist /v
```

- Running processes and service information:

```powershell
tasklist /svc
```

| Option  | Description                                                                                           |
| ------- | ----------------------------------------------------------------------------------------------------- |
| `/v`    | Display verbose task information.                                                                     |
| `/svc`  | List all service information for each process (without truncation); <br>`/fo` must be set to `table`. |
| `/apps` | Display Store Apps and their associated processes.                                                    |
| `/fo`   | Output format (`table`, `list`, or `csv`; default: `table`).                                          |

- More detailed process information:

```powershll
wmic process get name,executablepath,processid,parentprocessid
```

>[!tip]+ See what properties `wmic` can read
>```cmd
>wmic os get /value
>```

>[!warning] WMIC is deprecated in newer Windows versions (starting Windows 10).

>[!note] See [`tasklist`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/tasklist) and [`wmic`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/wmic) (`wmic` is an interface to [WMI (Windows Management Instrumentation)](https://docs.microsoft.com/en-us/windows/win32/wmisdk/wmi-start-page)).

- In PowerShell, use [`Get-Process`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-process?view=powershell-7.5) or [`Get-WmiObject`](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-wmiobject?view=powershell-5.1):

```powershell
Get-Process | Select-Object Name, Id, Path, Company, Product | ft -AutoSize
```

```powershell
Get-WmiObject -Class Win32_Process | Select-Object Name, ProcessId, ExecutablePath, CommandLine | ft -AutoSize
```

>[!note] See [`Get-Process`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-process?view=powershell-7.5) and [`Get-WmiObject`](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-wmiobject?view=powershell-5.1).

### Environment variables

- List all environment variables and their values:

```cmd
set
```

- In PowerShell, use [`Get-ChildItem`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-childitem?view=powershell-7.5) (or `gci`, its alias):

```powershell
Get-ChildItem Env:
```

```powershell
gci env:
```

>[!note] See [`Get-ChildItem`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-childitem?view=powershell-7.5).


### Installed programs

- Display installed software:

```powershell
wmic product get name
```

- In PowerShell, use [`Get-WmiObject`](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-wmiobject?view=powershell-5.1):

```powershell
Get-WmiObject -Class Win32_Product | select Name, Version
```

>[!tip] Run `LaZagne` to check for stored credentials for the installed applications. See [[🛠️ Windows credential hunting]].

>[!note] See [`Get-WmiObject`](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-wmiobject?view=powershell-5.1).
## Network information

### Interfaces, IP addresses, DNS information

```powershell
ipconfig /all
```

- In PowerShell, use [`Get-NetIPConfiguration`](https://learn.microsoft.com/en-us/powershell/module/nettcpip/get-netipconfiguration?view=windowsserver2025-ps) and [`Get-NetIPAddress`](https://learn.microsoft.com/en-us/powershell/module/nettcpip/get-netipaddress?view=windowsserver2025-ps):

```powershell
Get-NetIPConfiguration | Format-List
```

```powershell
Get-NetIPAddress | Format-Table
```

>[!note] See [`Get-NetIPConfiguration`](https://learn.microsoft.com/en-us/powershell/module/nettcpip/get-netipconfiguration?view=windowsserver2025-ps) or [`Get-NetIPAddress`](https://learn.microsoft.com/en-us/powershell/module/nettcpip/get-netipaddress?view=windowsserver2025-ps).

### ARP table

- ARP table:

```powershell 
arp -a
```

>[!note] See [`arp`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/arp).

### Routing table

```powershell
route print
```

>[!note] See [`route`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/route_ws2008).

### Network connections and listening ports

```powershell
netstat -ano
```

| Option | Description                                                 |
| ------ | ----------------------------------------------------------- |
| `-a`   | Show all connections and listening ports.                   |
| `-n`   | Display addresses and port numbers numerically.             |
| `-o`   | Show the owning process ID associated with each connection. |

>[!note] See [`netstat`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/netstat).

- In PowerShell:

```powershell
Get-NetTCPConnection | Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, State, OwningProcess | Format-Table -AutoSize
```

>[!note] See [`Get-NetTCPConnection`](https://learn.microsoft.com/en-us/powershell/module/nettcpip/get-nettcpconnection?view=windowsserver2025-ps).

#### Identifying what process is listening on a specific port

1. Get process ID:

```cmd
netstat -ano | findstr ":<port>"
```

2. Find which executable is running under that process ID:

```cmd
tasklist /fi "PID eq <pid>"
```

>[!example]-
> ```cmd
> netstat -ano | findstr ":8080"
> ```
> ```cmd
>   TCP    0.0.0.0:8080           0.0.0.0:0              LISTENING       2296
>   TCP    [::]:8080              [::]:0                 LISTENING       2296
> ```
> 
> ```cmd
> tasklist /fi "PID eq 2296"
> ```
> ```cmd
> Image Name                     PID Session Name        Session#    Mem Usage
> ========================= ======== ================ =========== ============
> Tomcat8.exe                   2296 Services                   0    100,608 K
> ```
>![[find_process_by_port.png]]

>[!tip] This helps identify services that might be exploitable locally even if they're not exposed externally.
### Network shares

- List local shares:

```cmd
net share
```

>[!note] See [`net share — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/hh750728(v=ws.11)).

- List shares on a remote system (if you have access):

```powershell
net view \\<computer_name> /all
```

## Users and groups

### Logged-in users

- Currently logged-in users:

```powershell
query user
```

- List user sessions:

```powershell
query session
```

>[!note] See [`query`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/query) and [`query user`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/query-user).

### Current user

- Username of the current user (environment variable):

```powershell
echo %USERNAME%
```

- In PowerShell (environment variable):

```powershell
$Env:USERNAME
```

- Current user in the NTLM format (`domain\username`):

```cmd
whoami
```

- More detailed information including SID:

```cmd
whoami /user
```

>[!note] See [`whoami`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/whoami).

#### Current user privileges

```powershell
whoami /priv
```
#### Current user group information

```powershell
whoami /groups
```

>[!tip] To display all available information about the current user, including SID, privileges, and group information, run:
>```powershell
>whoami /all
>```

### All users 

- List all users:

```powershell
net user
```

>[!note] See [`net user`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/net-user).

- Get password policies and other account information:

```cmd
net accounts
```

### All groups

- List all local groups:

```powershell
net localgroup
```

- Get details about a specific group:

```powershell
net localgroup administrators
```

- [`Get-LocalGroupMember`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.localaccounts/get-localgroupmember?view=powershell-5.1) lists members of a local group on the current machine:

```powershell
Get-LocalGroupMember -Group "Administrators"
```

## Defenses

### Windows Defender

- Check Windows Defender status:

```powershell
Get-MpComputerStatus
```

### AppLocker

- List AppLocker rules:

```powershell
Get-AppLockerPolicy -Effective | select -ExpandProperty RuleCollections
```

- Test an AppLocker policy:

```powershell
Get-AppLockerPolicy -Local | Test-AppLockerPolicy -path C:\Windows\System32\cmd.exe -User Everyone
```

>[!note] See [`Get-AppLockerPolicy`](https://learn.microsoft.com/en-us/powershell/module/applocker/get-applockerpolicy?view=windowsserver2019-ps) and [`Test-AppLockerPolicy`](https://learn.microsoft.com/en-us/powershell/module/applocker/test-applockerpolicy?view=windowsserver2019-ps).
### Firewall configuration

- Use [`netsh advfirewall`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/netsh-advfirewall?tabs=consecadd%2Cfirewalladd%2Cmainmodeadd%2Cmonitordelete) to display firewall status and enumerate rules:

```cmd
netsh advfirewall show allprofiles
```

```cmd
netsh advfirewall firewall show rule name=all
```

- In PowerShell (Windows 8+/Server 2012+), use [`Get-NetFirewallProfile`](https://learn.microsoft.com/en-us/powershell/module/netsecurity/get-netfirewallprofile?view=windowsserver2025-ps) and [`Get-NetFirewallRule`](https://learn.microsoft.com/en-us/powershell/module/netsecurity/get-netfirewallrule?view=windowsserver2025-ps):

```powershell
Get-NetFirewallProfile | Select-Object Name, Enabled
```

```powershell
Get-NetFirewallRule | Where-Object { $_.Enabled -eq 'True' } | Select-Object DisplayName, Direction, Action | Format-Table
```
## References and further reading

- [`Windows Commmands — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/windows-commands)
- [`Comparison of Microsoft Windows versions — Wikipedia`](https://en.wikipedia.org/wiki/Comparison_of_Microsoft_Windows_versions)
- [`Windows - Privilege Escalation — Internal All The Things`](https://swisskyrepo.github.io/InternalAllTheThings/redteam/escalation/windows-privilege-escalation/)

>[!note]- TODO
>- I have screenshots of some command outputs. Should I leave them in callouts collapsed by default so they don't take much space but show an example of how output looks like?