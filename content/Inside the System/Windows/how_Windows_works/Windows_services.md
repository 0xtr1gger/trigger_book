---
created: 18-02-2026
tags:
  - Windows
  - how_Windows_works
---

>[!note] From an offensive perspective, services are one of the most important attack surfaces on a Windows system. 
>- They run persistently, often with elevated privileges, and are usually configured once and forgotten. 
>- Misconfigurations accumulate over time, and when you're on an engagement, those misconfigs are your path from a low-privileged shell to `NT AUTHORITY\SYSTEM`.

>[!note]+ Service applications vs driver services 
>>**Service applications**, or just **services**, are processes started and managed by the Service Control Manager (SCM).
> 
>>**Driver services** conform to device driver protocols and run in kernel mode. They're not managed by the SCM.
>
>For Windows privilege escalation, we will focus on service applications.

## Windows services

>A **Windows [service](https://learn.microsoft.com/en-us/windows/win32/services/services)** is a long-running process that operates in the background, typically without user interaction or GUI (Graphical User Interface).

- Windows services can be started automatically at system boot without user intervention. These services can continue to run in the background even after the user logs out.
- Windows services are managed by the Windows **Service Control Manager (SCM)**.

>**[Service Control Manager (SCM)](https://learn.microsoft.com/en-us/windows/win32/services/service-control-manager)** is a user-mode system component implemented in `services.exe`. It exposes an RPC (Remote Procedure Call) interface used by administrative tools and service processes to manage service state and configuration.

- SCM runs as part of `%SystemRoot%\System32\services.exe`, which starts during boot under the **`LocalSystem` account**.
- Every interaction with a service — starting it, stopping it, querying its status — goes through the SCM via RPC.

>[!example]+
> When you run `sc start <service>`, you're sending an RPC request to the SCM, which then decides whether to honor it based on the service's security descriptor and your token's privileges.  

- SCM maintains a database of installed services; it lives in the registry under:

```powershell
HKLM\SYSTEM\CurrentControlSet\Services\
```

- Each subkey represents a service, such as `HKLM\SYSTEM\CurrentControlSet\Services\Spooler`.
- The database includes information on how each service or driver service should be started.
## Enumerating services

Every service actually has three different identifiers:

- **Registry key name (internal name)**: The canonical identifier used by `sc.exe`, PowerShell's `Get-Service`, and most APIs. For example, `Spooler`.
- **Display name**: The human-readable name shown in `services.msc` and Task Manager. The Print Spooler display name is `"Print Spooler"`. 
- **Process name**: The process name shown in Task Manager or `tasklist`. Many services share a process (`svchost.exe`), so this alone doesn't identify which service you're looking at.

Services also have an optional description field that can help you quickly understand what a service does (sometimes, s suspicious service with a vague or empty description is a red flag worth investigating).


Ways to display services: 

>**[Microsoft Management Console (MMC)](https://learn.microsoft.com/en-us/troubleshoot/windows-server/system-management-components/what-is-microsoft-management-console)** — built-in Service Manager
- Press `Win+R` and type `services.msc`, then press `Enter`.
- Alternatively, open the `Control Panel`, select `Administrative Tools > Services`.

![[services.msc_1.png]] 
![[services.msc_2.png]]

>**[Task Manager](https://learn.microsoft.com/en-us/shows/inside/task-manager)**
- Press `Ctrl+Shift+Esc`, then go to the **Service** tab (or start Task Manager directly).
- Click `Open Services` to launch the full Services console.
 ![[task_manager.png]]
![[task_manager_services.png]]

>[WMIC](https://learn.microsoft.com/en-us/windows/win32/wmisdk/wmic) in CMD

```powershell
wmic service list brief
```

![[wmic_services_brief.png]]


>[`Get-Service`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-service?view=powershell-7.5) cmdlet in PowerShell

- List all services:

```powershell
Get-Service
```


- Get information about a specific service:

```powershell
Get-Service -Name "ServiceName"   
```

- Only running services:

```powershell
Get-Service | ? {$_.Status -eq "Running"} | ft -AutoSize
```

>[!example]-
> ```powershell
> Get-Service | ? {$_.Status -eq "Running"} | ft -AutoSize 
> ```
> 
> ```powershell
> Status  Name                     DisplayName
> ------  ----                     -----------
> Running AudioEndpointBuilder     Windows Audio Endpoint Builder
> Running Audiosrv                 Windows Audio
> Running BFE                      Base Filtering Engine
> Running BITS                     Background Intelligent Transfer Service
> Running BrokerInfrastructure     Background Tasks Infrastructure Service
> Running Browser                  Computer Browser
> Running BthAvctpSvc              AVCTP service
> Running camsvc                   Capability Access Manager Service
> Running cbdhsvc_7cf9a            Clipboard User Service_7cf9a
> Running CDPSvc                   Connected Devices Platform Service
> Running CDPUserSvc_7cf9a         Connected Devices Platform User Service_7cf9a
> Running CertPropSvc              Certificate Propagation
> Running ClipSVC                  Client License Service (ClipSVC)
> Running COMSysApp                COM+ System Application
> Running CoreMessagingRegistrar   CoreMessaging
> Running CryptSvc                 Cryptographic Services
> Running DcomLaunch               DCOM Server Process Launcher
> Running Dhcp                     DHCP Client
> Running DiagTrack                Connected User Experiences and Telemetry
> Running DispBrokerDesktopSvc     Display Policy Service
> Running Dnscache                 DNS Client
> Running DPS                      Diagnostic Policy Service
> Running DsmSvc                   Device Setup Manager
> Running DusmSvc                  Data Usage
> Running EventLog                 Windows Event Log
> Running EventSystem              COM+ Event System
> Running FontCache                Windows Font Cache Service
> Running FoxitReaderUpdateService Foxit Reader Update Service
> Running gpsvc                    Group Policy Client
> Running InstallService           Microsoft Store Install Service
> Running iphlpsvc                 IP Helper
> Running KeyIso                   CNG Key Isolation
> Running LanmanServer             Server
> Running LanmanWorkstation        Workstation
> Running lfsvc                    Geolocation Service
> Running LicenseManager           Windows License Manager Service
> Running lmhosts                  TCP/IP NetBIOS Helper
> Running LSM                      Local Session Manager
> Running mpssvc                   Windows Defender Firewall
> Running MSDTC                    Distributed Transaction Coordinator
> Running NcbService               Network Connection Broker
> Running netprofm                 Network List Service
> Running NlaSvc                   Network Location Awareness
> Running nsi                      Network Store Interface Service
> Running OneSyncSvc_7cf9a         Sync Host_7cf9a
> Running PlugPlay                 Plug and Play
> Running Power                    Power
> Running ProfSvc                  User Profile Service
> Running RmSvc                    Radio Management Service
> Running RpcEptMapper             RPC Endpoint Mapper
> Running RpcSs                    Remote Procedure Call (RPC)
> Running SamSs                    Security Accounts Manager
> Running ScDeviceEnum             Smart Card Device Enumeration Service
> Running Schedule                 Task Scheduler
> Running SecurityHealthService    Windows Security Service
> Running SENS                     System Event Notification Service
> Running SessionEnv               Remote Desktop Configuration
> Running SgrmBroker               System Guard Runtime Monitor Broker
> Running ShellHWDetection         Shell Hardware Detection
> Running Spooler                  Print Spooler
> Running SSDPSRV                  SSDP Discovery
> Running StateRepository          State Repository Service
> Running StorSvc                  Storage Service
> Running SysMain                  SysMain
> Running SystemEventsBroker       System Events Broker
> Running TabletInputService       Touch Keyboard and Handwriting Panel Service
> Running TermService              Remote Desktop Services
> Running Themes                   Themes
> Running TimeBrokerSvc            Time Broker
> Running TokenBroker              Web Account Manager
> Running TrkWks                   Distributed Link Tracking Client
> Running UmRdpService             Remote Desktop Services UserMode Port Redirector
> Running UserManager              User Manager
> Running UsoSvc                   Update Orchestrator Service
> Running VaultSvc                 Credential Manager
> Running VGAuthService            VMware Alias Manager and Ticket Service
> Running vm3dservice              VMware SVGA Helper Service
> Running VMTools                  VMware Tools
> Running WaaSMedicSvc             Windows Update Medic Service
> Running Wcmsvc                   Windows Connection Manager
> Running WdiServiceHost           Diagnostic Service Host
> Running WdNisSvc                 Microsoft Defender Antivirus Network Inspection Service
> Running WinDefend                Microsoft Defender Antivirus Service
> Running WinHttpAutoProxySvc      WinHTTP Web Proxy Auto-Discovery Service
> Running Winmgmt                  Windows Management Instrumentation
> Running wlidsvc                  Microsoft Account Sign-in Assistant
> Running WpnService               Windows Push Notifications System Service
> Running WpnUserService_7cf9a     Windows Push Notifications User Service_7cf9a
> Running wscsvc                   Security Center
> Running WSearch                  Windows Search
> Running wuauserv                 Windows Update
> ```

- Detailed information:

```powershell
Get-Service | ? {$_.Status -eq "Running"}  | fl
```

- Search for services with a string in `DisplayName` field:

```powershell
Get-Service | ? {$_.Status -eq “Running”} | ? {$_.DisplayName -match “update” } | fl
```

>[!example]-
> ```powershell
>  Get-Service | ? {$_.Status -eq "Running"} | select -First 2 | fl
> ```
> 
> ```powershell
> Name                : AppXSvc
> DisplayName         : AppX Deployment Service (AppXSVC)
> Status              : Running
> DependentServices   : {}
> ServicesDependedOn  : {rpcss, staterepository}
> CanPauseAndContinue : False
> CanShutdown         : True
> CanStop             : True
> ServiceType         : Win32OwnProcess, Win32ShareProcess
> 
> Name                : AudioEndpointBuilder
> DisplayName         : Windows Audio Endpoint Builder
> Status              : Running
> DependentServices   : {AarSvc_7cf9a, AarSvc, Audiosrv}
> ServicesDependedOn  : {}
> CanPauseAndContinue : False
> CanShutdown         : False
> CanStop             : True
> ServiceType         : Win32OwnProcess, Win32ShareProcess
> ```

>[`Cim-Instance`](https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/get-ciminstance?view=powershell-7.5) cmdlet in PowerShell

```powershell
Get-CimInstance Win32_Service
```

>[!tip]+
>- Enumerate services using [`winPEAS`](https://github.com/peass-ng/PEASS-ng/tree/master/winPEAS):
>```powershell
>winPEAS.exe servicesinfo
>```
>- [`PowerUp.ps1`](https://github.com/PowerShellMafia/PowerSploit/blob/master/Privesc/PowerUp.ps1):
>```powershell
>Import-Module .\PowerUp.ps1
>Invoke-AllChecks
>```

- To check what permissions the current user has over a specific service, you can use [`AccessChk`](https://learn.microsoft.com/en-us/sysinternals/downloads/accesschk) from Sysinternals:

```powershell
accesschk.exe /accepteula -ucqv <service_name>
```

>[!note] Without `/accepteula`, `accesschk` pops an EULA dialog and hangs.

### Examining services using `sc`

The [`sc.exe`](https://learn.microsoft.com/en-us/windows/win32/services/controlling-a-service-using-sc) command-line utility can be used to examine and control services. 

- [`sc.exe query`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/sc-query) can be used to display information about the specified service. Show running services:

```powershell
sc query
```

- Show all services:

```powershell
sc query state= all
```

- `sc qc` can be used to query details about a specific service:

```powershell 
sc qc <service_name>
```

- `sc start` can be used to start services, and `sc stop` to stop them (requires administrative privileges): 

```powershell
sc stop wuauserv
```

- [`sc sdshow`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/cc742133(v=ws.11)) displays a service's [security descriptor](https://learn.microsoft.com/en-us/windows/win32/secauthz/security-descriptors) using [SDDL (Security Definition Language)](https://learn.microsoft.com/en-us/windows/win32/secauthz/security-descriptor-definition-language):

```powershell
sc sdshow <service>
```

>[!example]+
> ```powershell
> sc sdshow wuauserv
> ```
> 
> ```powershell
> D:(A;;CCLCSWRPLORC;;;AU)(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;BA)(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;SY)S:(AU;FA;CCDCLCSWRPWPDTLOSDRCWDWO;;;WD)
> ```

- Convert SDDL to readable ACL:

```powershell
$sddl = (sc.exe sdshow wuauserv)
$sd = New-Object System.Security.AccessControl.CommonSecurityDescriptor $false, $false, $sddl
$sd.DiscretionaryAcl
```

- To format the output:

```powershell
$sd.DiscretionaryAcl | Format-Table IdentityReference, AccessMask, AceType, IsInherited
```

- One-liner:

```powershell
([System.Security.AccessControl.CommonSecurityDescriptor]::new($false,$false,(sc.exe sdshow wuauserv))).DiscretionaryAcl

```

>[!tip]+
> - Alternatively, you can use the [`Get-Acl`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/get-acl?view=powershell-7.5) cmdlet to display the security descriptor of a service or other resource:
> 
> ```powershell
> Get-ACL -Path HKLM:\System\CurrentControlSet\Services\wuauserv | Format-List
> ```
## Service types

The `Type` value in a service's registry key controls how the service runs:

| Name                 | Value | Description                                                                                                  |
| -------------------- | ----- | ------------------------------------------------------------------------------------------------------------ |
| `KernelDriver`       | `1`   | Kernel device driver — low-level hardware interaction (e.g., hard disk).                                     |
| `FileSystemDriver`   | `2`   | Kernel device driver, handles filesystem operations.                                                         |
| `Adapter`            | `4`   | Hardware adapter services (services for hardware devices that require their own drivers).                    |
| `RecognizerDriver`   | `8`   | Filesystem driver; used during startup to detect and identify filesystems.                                   |
| `Win32OwnProcess`    | `16`  | Win32 programs started by SCM; runs in its own dedicated process (primary targets for privilege escalation). |
| `Win32ShareProcess`  | `32`  | Win32 services that share a process with other Win32 services (`svchost` model).                             |
| `InteractiveProcess` | `256` | Services that can interact with the desktop (legacy, rarely used today).                                     |
>[!note] See [service types](https://learn.microsoft.com/en-us/dotnet/api/system.serviceprocess.servicetype?view=net-10.0-pp).

## Service Host: `svchost.exe`

>**[`Svchost.exe`](https://en.wikipedia.org/wiki/Svchost.exe)** (**Service Host**) is a system process that can host one or more Windows services.

- `svchost.exe` is used for services implemented as DLLs rather than standalone executables. Instead of each service shipping its own `.exe`, it ships a `.dll` and gets hosted inside a shared `svchost.exe` instance. 
- This reduces process overhead, but it means many critical system services don't have their own process — they share one.

- List services running inside `svchost.exe`:

```powershell
tasklist /svc
```

- Detailed view:

```powershell 
tlist /s
```

>[!note] On modern Windows 10/11, Microsoft broke out many services into isolated `svchost.exe` instances (one per service on systems with sufficient RAM) specifically to improve security and reduce blast radius if one gets compromised. On older or lower-resource systems, more services share a single instance.
## Service accounts and privileges 

Every service runs under some security principal. Common built-in service accounts, from most to least powerful:
- [`LocalSystem`](https://learn.microsoft.com/en-us/windows/win32/services/localsystem-account) (`NT AUTHORITY\SYSTEM`)
	- The most privileged account on the local machine.
	- Has essentially unrestricted access to local resources; acts as the computer account when accessing network resources
- [`LocalService`](https://learn.microsoft.com/en-us/windows/win32/services/localservice-account) (`NT AUTHORITY\LOCAL SERVICE`)
	- Has minimal privileges on the local system, presents anonymous credentials on the network.
- [`NetworkService`](https://learn.microsoft.com/en-us/windows/win32/services/networkservice-account)  (`NT AUTHORITY\NETWORK SERVICE`)
	- Similar to `LocalService`, has limited local privileges, but uses the computer's domain identity when accessing the network.
- [**Virtual service accounts**, or **per-user services**](https://learn.microsoft.com/en-us/windows/application-management/per-user-services-in-windows) (`NT SERVICE\<ServiceName>`)
	- Introduced in Windows 7/Server 2008 R2.
	- Unique identity per service, managed automatically; uses computer credentials for network access.
	- Increasingly common in hardened environments.

>[!note]+ Accounts designed for domain-based services:
> - **[Standalone Managed Service Accounts (sMSA)](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-service-accounts#standalone-managed-service-accounts)**
> 	- A domain account, can be used on one computer only; password is automatically managed by Active Directory.
>  - **[Group Managed Service Accounts (gMSA)](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-service-accounts#group-managed-service-accounts)**
> 	 - Extension to sMSA; a domain account, can be used across multiple servers; password is automatically managed and rotated.

You can also configure custom user accounts; additionally services can sometimes run under `Administrator` (through this is not recommended).

>[!note] See [`Service accounts — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-service-accounts#standalone-managed-service-accounts).

- Most services run in special service accounts, such as `SYSTEM` or `LOCAL SERVICE`, but some can run with the same security context as logged-in user accounts.


## Critical system services

| Service                   | Description                                                                                                                                                                                                                                                                                                                                                                 |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `smss.exe`                | [Session Manager Subsystem](https://en.wikipedia.org/wiki/Session_Manager_Subsystem); responsible for handling sessions on the system.                                                                                                                                                                                                                                      |
| `csrss.exe`               | [Client-Server Runtime Process](https://en.wikipedia.org/wiki/Client/Server_Runtime_Subsystem); the user-mode portion of the Win32 subsystem.                                                                                                                                                                                                                               |
| `wininit.exe`             | Starts the Wininit file; `.ini` file that lists all of the changes to be made to Windows when the computer is restarted after installing a program.                                                                                                                                                                                                                         |
| `logonui.exe`             | Used for facilitating user login into a PC                                                                                                                                                                                                                                                                                                                                  |
| `lsass.exe`               | [Local Security Authority Subsystem Service](https://en.wikipedia.org/wiki/Local_Security_Authority_Subsystem_Service); verifies the validity of user logons to a PC or server. It starts the process responsible for authenticating users for the Winlogon service.                                                                                                        |
| `services.exe`            | [Service Control Manager](https://en.wikipedia.org/wiki/Service_Control_Manager); manages the operation of starting and stopping services.                                                                                                                                                                                                                                  |
| `winlogon.exe`            | [Windows Logon](https://en.wikipedia.org/wiki/Winlogon); responsible for handling the secure attention sequence (SAS), loading a user profile on logon, and locking the computer when a screensaver is running.                                                                                                                                                             |
| `svchost.exe`             | [Service Host](https://en.wikipedia.org/wiki/Svchost.exe); manages system services that run from dynamic-link libraries (files with the extension `.dll`) such as `Automatic Updates`, `Windows Firewall`, and `Plug and Play`. Can use the Remote Procedure Call (RPC) Service (RPCSS) or  the Distributed Component Object Model (DCOM) and Plug and Play (PnP) services. |


>[!note] See [`Windows service — Wikipedia`](https://en.wikipedia.org/wiki/Windows_service).
## References and further reading

- [`Windows service — Wikipedia`](https://en.wikipedia.org/wiki/Windows_service)

