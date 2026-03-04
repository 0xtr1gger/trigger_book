---
created: 01-02-2026
---

## System information
### Basic system information

- [`systeminfo`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/systeminfo) displays detailed system configuration, including OS name/version, build, architecture, installed hotfixes, etc.:

```cmd
systeminfo
```

>[!example]-
> ```cmd
> systeminfo
> ```
> 
> ![[systeminfo.png]]

- You can also use [WMI](https://docs.microsoft.com/en-us/windows/win32/wmisdk/wmi-start-page) (Windows Management Instrumentation) to retrieve information about the system. [WMIC](https://learn.microsoft.com/en-us/windows/win32/wmisdk/wmic) provides a command-line interface to WMI:

```cmd
wmic os get Caption,Version,BuildNumber,OSArchitecture
```

- `Caption` -> OS name
- `Version` -> internal version number
- `BuildNumber` -> OS build
- `OSArchitecture` -> 32 or 64-bit

>[!tip]+
>- To return values of all properties `wmic` can read, use:
>```cmd
>wmic os get /value
>```

>[!warning] WMIC is deprecated in newer Windows versions (starting Windows 10).

- The [`Get-WmiObject`](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-wmiobject?view=powershell-5.1) [cmdlet](https://docs.microsoft.com/en-us/powershell/scripting/developer/cmdlet/cmdlet-overview?view=powershell-7) is the PowerShell equivalent of WMIC:

```powershell
Get-WmiObject -Class Win32_OperatingSystem | Select Version,BuildNumber
```

>[!warning] `Get-WmiObject` is deprecated in favor of [`Get-CimInstance`](https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/get-ciminstance?view=powershell-7.5) in PowerShell 3.0.

- [`Get-CimInstance`](https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/get-ciminstance?view=powershell-7.5) (CIM) is a modern replacement for WMI queries:

```powershell
Get-CimInstance Win32_OperatingSystem | Select Caption, Version, BuildNumber, OSArchitecture
```

>[!note] These commands output the same results but use different tools.

>[!example]-
> ```cmd
> wmic os get Caption,Version,BuildNumber,OSArchitecture
> ```
> 
> ```powershell
> Get-WmiObject -Class Win32_OperatingSystem | Select Version,BuildNumber
> ```
> 
> ```powershell
> Get-CimInstance Win32_OperatingSystem | Select Caption, Version, BuildNumber, OSArchitecture
> ```
> 
> ![[three_wmi_commands.png]]

- [`Get-ComputerInfo`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-computerinfo?view=powershell-7.5) aggregates registry + WMI data to provide comprehensive system information:

```powershell
Get-ComputerInfo | Select-Object OSName, OSDisplayVersion, OSVersion, WindowsEditionId, WindowsProductName
```

>[!example]-
> ```powershell
> Get-ComputerInfo | Select-Object OSName, OSDisplayVersion, OSVersion, WindowsEditionId, WindowsProductName
> ```
> 
> ![[get-computerinfo.png]]

- The `OS` environment variable stores OS family name (`Windows_NT`), and the `PROCESSOR_ARCHITECTURE` variable stores CPU architecture (e.g., AMD64, x86, etc.):

```powershell
$env:OS
```

```powershell
$env:PROCESSOR_ARCHITECTURE
```

>[!example]-
> ```powershell
> $env:OS
> ```
> ```powershell
> Windows_NT
> ```
> ```powershell
> $env:PROCESSOR_ARCHITECTURE
> ```
> ```powershell
> AMD64
> ```

### Installed updates and hotfixes 

- WMIC can be used to list installed [QFE](https://docs.microsoft.com/en-us/windows/win32/cimwin32prov/win32-quickfixengineering) (Quick Fix Engineering) updates (KB patches):

```cmd
wmic qfe list
```

>[!example]-
> ```cmd
> wmic qfe list
> ```
> 
> ![[installed_qfe.png]]

- [`Get-HotFix`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-hotfix?view=powershell-7.5) is a PowerShell equivalent to `wmic qfe`:

```powershell
Get-HotFix | tf -AutoSize
```

- [`Format-Table`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/format-table?view=powershell-7.5) (`ft`) formats hotfix list as a table.

>[!example]+
>```powershell
>Get-HotFix | tf -AutoSize
>```
>![[get-hotfix.png]]

- To check if a specific KB is installed:

```powershell
Get-HotFix -Id KB5001234
```

## Users and groups
### Who am I?

- Username of the current user:

```cmd
echo %USERNAME%
```

To display information about the current user, including groups and privileges, you can use the [`whoami`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/whoami) command.

- Current user in the NTLM format (`domain\username`):

```cmd
whoami
```

- More detailed information including SID:

```cmd
whoami /user
```

>[!example]-
> ```cmd
> whoami /user
> ```
> 
> ![[whoami_user.png]]

- Group membership of the current user, type of the account, SID, and attributes:

```cmd
whoami /groups
```

>[!example]-
>```cmd 
>whoami /groups
>```
>![[whoami_groups.png]]

- Current integrity level:

```powershell
whoami /groups | Where-Object { $_ -match "Label" }
```

>[!note]+ Integrity levels
>Integrity levels provide an additional security boundary. 
>Your integrity level affects what you can do even with seemingly appropriate permissions:
>- *Medium integrity* is standard for users
>- *High integrity* indicates elevated (administrator) privileges
>- *System integrity* is for `SYSTEM` processes
>- *Low integrity* is used for sandboxed applications like Internet Explorer's Protected Mode.
>
>Say, if you're in the Administrators group but running at Medium integrity, you're constrained by UAC and need to bypass it to achieve High integrity.

- Security privileges of the current user:

```cmd
whoami /priv
```

On a typical local standard account, you usually see:

| Privilege                           | Meaning                      | State    |
| ----------------------------------- | ---------------------------- | -------- |
| **`SeChangeNotifyPrivilege`**       | Bypass traverse checking     | Enabled  |
| **`SeIncreaseWorkingSetPrivilege`** | Increase process working set | Disabled |
- **`SeChangeNotifyPrivilege`** is granted to *Everyone* by default.

>[!note] See [[_privileges]] to learn more about Windows privileges.

>[!example]+
>```cmd
>whoami /priv
>```
>![[whoami_priv.png]]

- Display all available information:

```cmd
whoami /all
```

>[!example]-
>```cmd
>whoami /all
>```
>![[whoami_all.png]]

### Other users

- List all users:

```cmd
net user
```

>[!example]-
> ```cmd
> net user
> ```
> 
> ![[net_user.png]]

>[!note] See [`net user — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/net-user).


- List currently logged-in users (display active and disconnected sessions):

```cmd
query user
```

>[!example]-
> ```cmd
> query user
> ```
> 
> ![[query_user.png]]

>[!note] See [`query — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/query).

- List user sessions:

```powershell
query session
```

>[!example]+
> ```cmd 
> query session
> ```
> 
> ![[images/Windows/query_session.png]]

- Get password policies and other account information:

```cmd
net accounts
```

>[!example]+
> ```cmd
> net accounts
> ```
> 
> ![[net_accounts.png]]

- List all groups on the local system:

```cmd
net localgroup
```

>[!example]-
> ```cmd
> net localgroup
> ```
> ![[net_localgroup.png]]
>[!note] See [`net localgroup — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/cc725622(v=ws.11))

- Display more information about a group:

```cmd
net localgroup administrators
```

>[!example]-
> ```cmd
> net localgroup administrators
> ```
> 
> ![[net_localgroup_administrators.png]]

- [`Get-LocalGroupMember`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.localaccounts/get-localgroupmember?view=powershell-5.1) lists members of a local group on the current machine:

```powershell
Get-LocalGroupMember -Group "Administrators"
```

## Environment

- List all environment variables and their values:

```cmd
set
```

- In PowerShell, use [`Get-ChildItem`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-childitem?view=powershell-7.5) cmdlet (or its shorter alias, `gci`):

```powershell
Get-ChildItem Env:
```

```powershell
gci env:
```

>[!example]-
> ```powershell
> Get-ChildItem Env:
> ```
> ![[env.png]]


## Network enumeration

- Interfaces, IP addresses, DNS information:

```cmd 
ipconfig /all
```

- In PowerShell, use [`Get-NetIPConfiguration`](https://learn.microsoft.com/en-us/powershell/module/nettcpip/get-netipconfiguration?view=windowsserver2025-ps) and [`Get-NetIPAddress`](https://learn.microsoft.com/en-us/powershell/module/nettcpip/get-netipaddress?view=windowsserver2025-ps):

```powershell
Get-NetIPConfiguration | Format-List
```

```powershell
Get-NetIPAddress | Format-Table
```

- To display ARP table, use [`arp`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/arp):

```powershell 
arp -a
```

- [`netstat`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/netstat) displays all network connections and listening ports:

```cmd
netstat -ano
```

>[!note]+ `netstat -ano`
> - `-a`: Shows all connections and listening ports.
> - `-n`: Displays addresses and port numbers numerically.
> - `-o`: Shows the owning process ID associated with each connection.

>[!example]-
>```cmd
>netstat -ano
>```
>![[netstat_ano.png]]

- In PowerShell, use [`Get-NetTCPConnection`](https://learn.microsoft.com/en-us/powershell/module/nettcpip/get-nettcpconnection?view=windowsserver2025-ps):

```powershell
Get-NetTCPConnection | Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, State, OwningProcess | Format-Table -AutoSize
```

- To identify what process is listening on a specific port:

	1. Get the ID of the process:
	
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

>[!note] This helps identify services that might be exploitable locally even if they're not exposed externally.

### Network shares

- List local shares:

```cmd
net share
```

>[!note] See [`net share — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/hh750728(v=ws.11)).

- List shares on a remote system (if you have access):

```cmd
net view \\<computer_name> /all
```

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
## System drives and storage

- List all available drives, their filesystems, and free space:

```cmd
wmic logicaldisk get caption,volumename,filesystem,size,freespace
```

>[!example]-
> ```cmd
> wmic logicaldisk get caption,volumename,filesystem,size,freespace
> ```
> 
> ```powershell
> Caption  FileSystem  FreeSpace    Size         VolumeName
> C:       NTFS        18288455680  42355126272
> ```

- In PowerShell, use [`Get-PSDrive`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-psdrive?view=powershell-7.5):

```powershell
Get-PSDrive -PSProvider FileSystem | Select-Object Name, Root, Used, Free
```

>[!example]-
>```powershell
>Get-PSDrive -PSProvider FileSystem | Select-Object Name, Root, Used, Free
>```
>![[psdrive.png]]
## Processes

- List all running processes:

```powershell
tasklist /v
```

- List services:

```powershell
tasklist /svc
```

| Parameter | Description                                        |
| --------- | -------------------------------------------------- |
| `/v`      | Display verbose information.                       |
| `/svc`    | Display services hosted in each process.           |
| `/apps`   | Display Store Apps and their associated processes. |

- Get more detailed process information:

```powershll
wmic process get name,executablepath,processid,parentprocessid
```

- In PowerShell, use [`Get-Process`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-process?view=powershell-7.5):

```powershell
Get-Process | Select-Object Name, Id, Path, Company, Product | ft -AutoSize
```

- Or WMI:
```powershell
Get-WmiObject -Class Win32_Process | Select-Object Name, ProcessId, ExecutablePath, CommandLine | ft -AutoSize
```

## Installed applications

```cmd
wmic product get name
```


## Security


- Check Windows Defender status:

```powershell
Get-MpComputerStatus
```

- List AppLocker rules:

```powershell
Get-AppLockerPolicy -Effective | select -ExpandProperty RuleCollections
```

- Test AppLocker policy:

```powershell
Get-AppLockerPolicy -Local | Test-AppLockerPolicy -path C:\Windows\System32\cmd.exe -User Everyone
```

## References and further reading

- [`Windows - Privilege Escalation — Internal All The Things`](https://swisskyrepo.github.io/InternalAllTheThings/redteam/escalation/windows-privilege-escalation/)