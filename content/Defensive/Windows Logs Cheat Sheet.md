---
created: 2026-03-29
tags:
  - cheatsheet
  - defensive
  - Windows
  - logging
  - monitoring
---
## Windows Event IDs 

### Authentication & logon events

| Event ID                                                                                           | Description                                                                         |
| -------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| [`4624`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4624) | An account was successfully logged on.                                              |
| [`4625`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4625) | An account failed to log on.                                                        |
| [`4634`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4634) | An account was logged off.                                                          |
| [`4647`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4647) | A user initiated a logoff.                                                          |
| [`4648`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4648) | A logon attempt was made using explicit credentials (e.g., RunAs, scheduled tasks). |
| [`4672`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4672) | Special privileges were assigned to a new logon session.                            |
| [`4776`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4776) | The domain controller attempted to validate credentials for an account.             |
| [`4777`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4777) | The domain controller failed to validate credentials for an account.                |


#### 4624 logon types

| Logon type | Name                | Description                                                                                        |
| ---------- | ------------------- | -------------------------------------------------------------------------------------------------- |
| `2`        | `Interactive`       | A user logged on locally at the console or via direct access to the machine.                       |
| `3`        | `Network`           | A user or system accessed the machine over the network without interactive login (e.g., WMI, SMB). |
| `10`       | `RemoteInteractive` | A user logged on remotely using Remote Desktop or Terminal Services.                               |
| `7`        | `Unlock`            | A workstation was unlocked using previously logged-in credentials (screen unlock).                 |
| `11`       | `CachedInteractive` | A user logged in using cached domain credentials when DC was unavailable..                         |

---

| Logon type | Name                | Description                                                                                                                                    |
| ---------- | ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `0`        | `System`            | Used internally by the `SYSTEM` account during system startup.                                                                                 |
| `2`        | `Interactive`       | A user logged on locally at the console or via direct access to the machine.                                                                   |
| `3`        | `Network`           | A user or system accessed the machine over the network without interactive login (e.g., WMI, SMB).                                             |
| `4`        | `Batch`             | A batch process executed on behalf of a user without interaction.                                                                              |
| `5`        | `Service`           | A service started by the Service Control Manager (SCM).                                                                                        |
| `7`        | `Unlock`            | A workstation was unlocked using previously logged-in credentials (screen unlock).                                                             |
| `8`        | `NetworkCleartext`  | A network logon where credentials were provided in plaintext to the authentication package (e.g., Basic Authentication, PowerShell `CredSSP`). |
| `9`        | `NewCredentials`    | A process used different credentials for outbound connections without changing local identity (e.g., `runas /netonly`).                        |
| `10`       | `RemoteInteractive` | A user logged on remotely using Remote Desktop or Terminal Services.                                                                           |
| `11`       | `CachedInteractive` | A user logged in using cached domain credentials when DC was unavailable..                                                                     |

#### 4625 failed logon sub-codes

| SubStatus    | Meaning                         |
| ------------ | ------------------------------- |
| `0xC0000064` | Username does not exist.        |
| `0xC000006A` | Wrong password, valid username. |
| `0xC0000234` | Account locked out.             |
| `0xC0000072` | Account disabled.               |
| `0xC000006F` | Outside allowed logon hours.    |
| `0xC0000193` | Account expired.                |
| `0xC0000070` | Workstation restriction.        |

### Account management events




| Event ID                                                                                           | Description                                          |
| -------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| [`4720`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4720) | A user account was created.                          |
| [`4722`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4722) | A user account was enabled.                          |
| [`4723`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4723) | An attempt was made to change an account's password. |
| [`4724`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4724) | An attempt was made to reset an account's password.  |
| [`4725`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4725) | A user account was disabled.                         |
| [`4726`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4726) | A user account was deleted.                          |
| [`4738`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4738) | A user account was changed.                          |
| [`4781`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4781) | The name of an account was changed.                  |

- Lockout:

| Event ID                                                                                           | Description                    |
| -------------------------------------------------------------------------------------------------- | ------------------------------ |
| [`4740`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4740) | A user account was locked out. |
| [`4767`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4767) | A user account was unlocked.   |


### Group & privilege management events


| Event ID                                                                                           | Description                                                   |
| -------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| [`4727`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4727) | A security-enabled global group was created.                  |
| [`4728`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4728) | A member was added to a security-enabled global group.        |
| [`4729`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4729) | A member was removed from a security-enabled global group.    |
| [`4732`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4732) | A member was added to a security-enabled local group.         |
| [`4733`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4733) | A member was removed from a security-enabled local group.     |
| [`4735`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4735) | A security-enabled local group was changed.                   |
| [`4737`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4737) | A security-enabled global group was changed.                  |
| [`4756`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4756) | A member was added to a security-enabled universal group.     |
| [`4757`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4757) | A member was removed from a security-enabled universal group. |
### Process execution & persistence mechanisms


- Processes:

| Event ID                                                                                           | Description                                |
| -------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| [`4688`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4688) | A new process was created on the system.   |
| [`4689`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4689) | A process exited on the system.            |
| [`4696`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4696) | A primary token was assigned to a process. |

- Services:

| Event ID                                                                                           | Description                                |
| -------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| [`4697`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4697) | A new service was installed on the system. |
| [`7040`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=7040) | Startup type of a service is modified.     |
| [`7045`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=7045) | A new service was installed in the system. |

- Scheduled tasks:

| Event ID                                                                                           | Description                                            |
| -------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| [`4698`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4698) | A scheduled task was created.                          |
| [`4699`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4699) | A scheduled task was deleted.                          |
| [`4700`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4700) | A scheduled task was enabled.                          |
| [`4701`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4701) | A scheduled task was disabled.                         |
| [`4702`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4702) | A scheduled task was updated (modified configuration). |


### Object access & file activity

| Event ID                                                                                           | Description                              |
| -------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| [`4656`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4656) | A handle to an object was requested.     |
| [`4657`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4657) | A registry value was modified.           |
| [`4663`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4663) | An attempt was made to access an object. |
| [`4660`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4660) | An object was deleted.                   |
| [`4670`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4670) | Permissions on an object were changed.   |

### Network access 

- Network shares:

| Event ID                                                                                           | Description                                                |
| -------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| [`5140`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=5140) | A network share object was accessed.                       |
| [`5142`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=5142) | A new network share was created.                           |
| [`5145`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=5145) | A network share object was checked for access permissions. |



- Remote Desktop sessions:

| Event ID                                                                                           | Description                                       |
| -------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| [`4778`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4778) | A session was reconnected to a Window Station.    |
| [`4779`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4779) | A session was disconnected from a Window Station. |

### Kerberos & authentication tickets

| Event ID                                                                                           | Description                                                      |
| -------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| [`4768`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4768) | A Kerberos TGT (Ticket-Granting Ticket) was requested from a DC. |
| [`4769`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4769) | A Kerberos ST (Service Ticket) was requested from a DC.          |
| [`4770`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4770) | An existing ST (Service Ticket) was renewed.                     |
| [`4771`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4771) | Kerberos pre-authentication failed.                              |
| [`4772`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4772) | A Kerberos authentication ticket request failed.                 |

- NTLM:

| Event ID                                                                                           | Description                            |
| -------------------------------------------------------------------------------------------------- | -------------------------------------- |
| [`4776`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4776) | A DC validated credentials using NTLM. |

### Active Directory & Directory Services

| Event ID                                                                                           | Description                               |
| -------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| [`5136`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=5136) | A directory service object was modified.  |
| [`5137`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=5137) | A directory service object was created.   |
| [`5138`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=5138) | A directory service object was undeleted. |
| [`5139`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=5139) | A directory service object was moved.     |

### Policy changes & security configuration

| Event ID                                                                                           | Description                          |
| -------------------------------------------------------------------------------------------------- | ------------------------------------ |
| [`4719`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4719) | The system audit policy was changed. |
| [`4713`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4713) | Kerberos policy was changed.         |
| [`4704`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4704) | A user right was assigned.           |
| [`4705`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4705) | A user right was removed.            |


### Windows Defender / AV 
events

| Event ID                                                                                                                       | Short description                                                   |
| ------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------- |
| [`1116`](https://learn.microsoft.com/en-us/microsoft-365/security/defender-endpoint/troubleshoot-microsoft-defender-antivirus) | Malware was detected.                                               |
| [`1118`](https://learn.microsoft.com/en-us/microsoft-365/security/defender-endpoint/troubleshoot-microsoft-defender-antivirus) | Remediation started for detected malware.                           |
| [`1119`](https://learn.microsoft.com/en-us/microsoft-365/security/defender-endpoint/troubleshoot-microsoft-defender-antivirus) | Remediation of detected malware was successfully completed.         |
| [`1120`](https://learn.microsoft.com/en-us/microsoft-365/security/defender-endpoint/troubleshoot-microsoft-defender-antivirus) | Remediation of detected malware failed.                             |
| [`5001`](https://learn.microsoft.com/en-us/microsoft-365/security/defender-endpoint/troubleshoot-microsoft-defender-antivirus) | Microsoft Defender real-time protection configuration was modified. |

### Network & firewall events

| Event ID                                                                                           | Short description                                                    |
| -------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| [`5157`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=5157) | The Windows Filtering Platform blocked a network connection attempt. |




### Log integrity & anti-forensics

| Event ID                                                                                           | Description                              |
| -------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| [`1102`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=1102) | The audit log was cleared.               |
| [`1100`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=1100) | The event logging service was shut down. |
| [`1104`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=1104) | The security log is now full.            |

### Miscellaneous system events

- Startup and shutdown:

| Event ID                                                                                                                              | Description                                                                   |
| ------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| [`1074`](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-1074)                                    | System shutdown or restart operation was initiated.                           |
| [`4608`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4608)                                    | The Windows OS started.                                                       |
| [`4609`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4609)                                    | The Windows OS beings shutdown.                                               |
| [`6005`](https://learn.microsoft.com/en-us/troubleshoot/windows-server/performance/troubleshoot-unexpected-reboots-system-event-logs) | Event Log service started (during system boot).                               |
| [`6006`](https://learn.microsoft.com/en-us/troubleshoot/windows-server/performance/troubleshoot-unexpected-reboots-system-event-logs) | Event Log service stopped (during system shutdown).                           |
| [`6013`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=6013)                                    | System uptime reported (generated periodically to record uptime, in seconds). |


## Sysmon Event IDs

| Event ID | Name                                  | Catches...                                                                                                                                                                                                 |
| -------- | ------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `1`      | `ProcessCreate`                       | Process creation events; provides detailed information about newly created processes, including full command line, parent process, and `ProcessGUID` (a unique identifier of the process across a domain). |
| `3`      | `NetworkConnect`                      | TCP/UDP connections, including source/destination IP addresses and port numbers.<br>Each connection is linked to a process (`ProcessId` or `ProcessGuid`).<br>Disabled by default.                         |
| `5`      | `ProcessTerminate`                    | Process exit; useful for detecting short-lived processes.                                                                                                                                                  |
| `6`      | `DriverLoad`                          | Diver loads, including hash and signature status; useful for detecting malicious/unsigned drivers (e.g., rootkits).                                                                                        |
| `7`      | `ImageLoad`                           | Every DLL loaded by every process. High volume, but catches DLL injection and hijacking.                                                                                                                   |
| `8`      | `CreateRemoteThread`                  | Indicates a process created a thread in another process; commonly seen in code injection.                                                                                                                  |
| `9`      | `RawAccessRead`                       | Raw disk reads via `\\.\` paths; can indicate credential dumping or forensic bypass techniques.                                                                                                            |
| `10`     | `ProcessAccess`                       | One process opening another process's memory; useful for detecting [[LSASS memory]] dumping.                                                                                                               |
| `11`     | `FileCreate`                          | File creation or overwrite; catches payload drops.                                                                                                                                                         |
| `12`     | `RegistryEvent (ObjectCreate/Delete)` | Registry key/value creation/deletion.                                                                                                                                                                      |
| `13`     | `RegistryEvent (ValueSet)`            | Registry value changes.                                                                                                                                                                                    |
| `14`     | `RegistryEvent (Rename)`              | Registry key/value rename.                                                                                                                                                                                 |
| `15`     | `FileCreateStreamHash`                | Alternate Data Stream (ADS) creation with hash (malware commonly hides in ADS).                                                                                                                            |
| `16`     | `ServiceConfigurationChange`          | Changes to the Sysmon config.<br>If you didn't do it, someone is tampering with your monitoring.                                                                                                           |
| `17`     | `PipeCreated`                         | Named pipe creation.                                                                                                                                                                                       |
| `18`     | `PipeConnected`                       | Named pipe connection.                                                                                                                                                                                     |
| `19`     | `WmiEventFilter`                      | Ceation of WMI event filters.                                                                                                                                                                              |
| `20`     | `WmiEventConsumer`                    | Registration of WMI consumers.                                                                                                                                                                             |
| `21`     | `WmiEventConsumerToFilter`            | Binding of WMI consumers to filters.                                                                                                                                                                       |
| `22`     | `DnsQuery`                            | DNS queries with the requesting process.                                                                                                                                                                   |
| `23`     | `FileDelete (Archived)`               | File deletion with optional copy of the deleted file for forensic recovery.                                                                                                                                |
| `25`     | `ProcessTampering`                    | Process hollowing, herpaderping, ghosting — attacks that replace a legitimate process image with malicious code.                                                                                           |
| `26`     | `FileDeleteDetected`                  | File deletion logged without archiving.                                                                                                                                                                    |

## Get-WinEvent

>[`Get-Event`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.diagnostics/get-winevent?view=powershell-7.5) retrieves Windows event log records from local or remote computers — from live logs, ETW trace files, and `.evtx`/`.etl` files; it can filter events using hash tables, XPath, or XML (structured) queries.

- Syntax:

```powershell
Get-WinEvent [-LogName <log_channel>]
Get-WinEvent [-ProviderName <provider>]
Get-WinEvent [-Path <path_to_log_file>]
Get-WinEvent [-FilterHashtable <hashtable>]
Get-WinEvent [-FilterXPath <xpath>]
Get-WinEvent [-FilterXml <xml_document>]
```

- Quick command reference:

| Command                                | Description                                              |
| -------------------------------------- | -------------------------------------------------------- |
| `Get‑WinEvent -ListLog *`              | List all available logs.                                 |
| `Get‑WinEvent -ListProvider *`         | List all event log providers.                            |
| `Get‑WinEvent -LogName Security`       | Retrieve all events from `Security` log.                 |
| `Get‑WinEvent -Path *.evtx`            | Read events from all `*.evtx` files in the current path. |
| `Get‑WinEvent -FilterHashtable @{...}` | Filter events using a simplified key-value query.        |
| `Get‑WinEvent -FilterXPath "..."`      | Filter events using an XPath query expression.           |
| `Get‑WinEvent -FilterXml $xml`         | Filter events using a structured XML query.              |

>[!example]- Example: `Get‑WinEvent -ListLog *`
> 
> ```
> Get‑WinEvent -ListLog *
> ```
> 
> ```powershell
> LogMode   MaximumSizeInBytes RecordCount LogName
> -------   ------------------ ----------- -------
> Circular            20971520        1367 Application
> Circular            20971520           0 HardwareEvents
> Circular             1052672           0 Internet Explorer
> Circular            20971520           0 Key Management Service
> Circular            20971520       28200 Security
> Circular            20971520       24619 System
> Circular            15728640        2268 Windows PowerShell
> Circular            20971520             ForwardedEvents
> Circular            10485760           0 Microsoft-AppV-Client/Admin
> Circular            10485760           0 Microsoft-AppV-Client/Operational
> Circular            10485760           0 Microsoft-AppV-Client/Virtual Applications
> Circular             1052672        1841 Microsoft-Client-Licensing-Platform/Admin
> 
> Circular             1052672             Microsoft-Management-UI/Admin
> Circular             1052672           0 Microsoft-Rdms-UI/Admin
> Circular             1052672           0 Microsoft-Rdms-UI/Operational
> # ...
> ```

>[!example]- Example: `Get-WinEvent -ListProvider * | ft`
> 
> ```powershell
> Get-WinEvent -ListProvider * | ft
> ```
> 
> ```powershell
> Name                                  LogLinks
> ----                                  --------
> .NET Runtime                          {Application}
> .NET Runtime Optimization Service     {Application}
> Application                           {Application}
> Application Error                     {Application}
> Application Hang                      {Application}
> Application Management                {Application}
> ASP.NET 2.0.50727.0                   {Application}
> AWSLiteAgent                          {Application}
> CardSpace 4.0.0.0                     {Application}
> Chkdsk                                {Application}
> DeliveryOptimization                  {Application}
> Desktop Window Manager                {Application}
> DiskQuota                             {Application}
> ```

### Option reference


- Listing event logs and providers:

| Option                     | Description                               |
| -------------------------- | ----------------------------------------- |
| `-ListLog <string[]>`      | List available event logs.                |
| `-ListProvider <string[]>` | List event providers (sources of events). |

- Querying events:

| Option                     | Description                                                               |
| -------------------------- | ------------------------------------------------------------------------- |
| `-LogName <string[]>`      | Retrieve events from the specified event log channels.                    |
| `-ProviderName <string[]>` | Retrieve events generated by specified providers.                         |
| `-Path <string[]>`         | Read events from the specified event log files (`.evtx`, `.evt`, `.etl`). |
>[!warning] `‑Path` _can_ be combined with `‑FilterXPath` but **not with `‑FilterHashtable`** (you'll get an error).

- Query options:

| Option                         | Description                                       |
| ------------------------------ | ------------------------------------------------- |
| `-MaxEvents <int>`             | Limit the number of returned events.              |
| `-Oldest`                      | Return oldest events first.                       |
| `-Force`                       | Include debug/analytic logs (hidden by default).  |
- Filtering:

| Option                         | Description                                       |
| ------------------------------ | ------------------------------------------------- |
| `-FilterHashtable <hashtable>` | Filter events using a simplified key-value query. |
| `-FilterXPath <xpath>`         | Filter events using an XPath query expression.    |
| `-FilterXml <xml_document>`    | Filter events using a structured XML query.       |

>[!warning] `-FilterHashtable` can not be combined with `-FilterPath` or `-FilterXml`.

>[!note]+ When to use `-FilterXPath` and `-FilterXML` instead of `-FilterHashtable`
> - `-FilterHashtable` can directly filter on top-level `<System>` fields (e.g., `EventID`, `LogName`, `ProviderName`) — but it can't filter on specific named `<EventData>` fields.
> - Although you can access `<EventData>` fields via the `.Properties[]` array, this happens *after the events are retrieved* (you're working with *.NET objects* `Get-WinEvents` returns using the `Where-Object` and  `ForEach-Object` cmdlets), not at query time. And since indexes may shift over time, this isn't reliable for automation. 
> - For precise filtering on fields like `TargetUserName`, use XPath via `-FilterXPath` or the full `-FilterXml` approach.

>[!note]+ You do can filter using `Where-Object` — but it's **slower**.

- Querying logs on remote systems:

| Option                       | Description                                       |
| ---------------------------- | ------------------------------------------------- |
| `-ComputerName <string>`     | Retrieve events from a specified remote computer. |
| `-Credential <PSCredential>` | Specify credentials to authenticate with.         |

- Some common cmdlet parameters (see [[PowerShell#Common parameters]]):

| Option                  | Description                                                                                                                                           |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `-Verbose`, `-vb`       | Show detailed operation messages (`Write-Verbose`). Overrides `$VerbosePreference`.                                                                   |
| `-ErrorAction`, `-ea`   | Specify how non-terminating error messages are handled.<br>Values: `Continue`, `Stop`, `SilentlyContinue`, `Inquire`, `Ignore`, `Suspend` (workflow). |
| `-Debug`, `-db`         | Show developer/debug messages (from `Write-Debug`). Overrides `$DebugPreference`.                                                                     |
| `-WarningAction`, `-wa` | Specify how warning messages are handled (`Write-Warning`).<br>Values: `Continue`, `Stop`, `SilentlyContinue`, `Inquire`, `Ignore`.                   |

Which option works with which

| Set                | Works With                                                                 |
| ------------------ | -------------------------------------------------------------------------- |
| `-ListLog`         | `-ComputerName`, `-Credential`, `-Force`.                                  |
| `-ListProvider`    | `-ComputerName`, `-Credential`.                                            |
| `-FilterHashtable` | `-MaxEvents`, `-ComputerName`, `-Credential`, `-Oldest`, `-Force`.         |
| `-FilterXPath`     | `-LogName/-Path`, `-MaxEvents`, `-ComputerName`, `-Credential`, `-Oldest`. |
| `-FilterXml`       | `-MaxEvents`, `-ComputerName`, `-Credential`, `-Oldest`.                   |
### Listing event logs and providers

- List all event log channels on the system:

```powershell
Get-WinEvent -ListLog *
```

>[!tip]+
> - You can select which columns to display using [`Select-Object`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/select-object?view=powershell-7.5):
> 
> ```powershell
> Get-WinEvent -ListLog * | Select-Object LogName, RecordCount, IsClassicLog, IsEnabled, LogMode, LogType | Format-Table -AutoSize
> ```

>[!note]+ Important fields `-ListLog` returns
> 
> | Field          | Meaning                            |
> | -------------- | ---------------------------------- |
> | `LogName`      | Name of the event log channel.     |
> | `RecordCount`  | Number of events currently stored. |
> | `IsClassicLog` | True = old `.evt` format.          |
> | `IsEnabled`    | Whether logging is enabled.        |
> | `LogMode`      | How log handles size limits.       |
> | `LogType`      | Category of log.                   |
> 
> - `LogMode` values:
> 
> | Mode         | Meaning                           |
> | ------------ | --------------------------------- |
> | `Circular`   | Old logs overwritten when full.   |
> | `Retain`     | Logs kept until manually cleared. |
> | `AutoBackup` | Old logs automatically archived.  |

- List all installed event providers:

```powershell
Get-WinEvent -ListProvider *
```

- You can also use wildcards to find providers you need:

```powershell
Get‑WinEvent -ListProvider *Audit*
Get‑WinEvent -ListProvider *PowerShell*
```


>[!warning] `‑ListLog` and `‑ListProvider` are separate sets — you _don’t combine them with normal filtering_.

>[!important]+ Log vs provider
>**Log** = where events are stored (e.g., `Security`, `Application`, `System`, etc.).
>- Get events stored in a specific log (such as `Security`):
>```powershell
>Get-WinEvent -LogName Security
>```
>**Provider** = what created the event (e.g., `Microsoft-Windows-Security-Auditing`).
>- Get events generated by a specific provider:
>```powershell
>Get-WinEvent -ProviderName "Service Control Manager"
>```

>[!warning]+ You do can specify both provider and log (event channel). But the provider must write to the log you specified.
> 
> - Take this example:
> 
> ```powershell
> Get-WinEvent -FilterHashtable @{
>     LogName='Security'
>     ProviderName='Service Control Manager'
> }
> ```
> 
> - This command will **fail** because the `Service Control Manager` provider **does not write to the `Security` log**.
> - You'll see this error:
> 
> ```powershell
> Get-WinEvent : The specified providers do not write
> events to any of the specified logs.
> At line:1 char:1
> + Get-WinEvent -FilterHashtable @{
> + ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
>     + CategoryInfo          : InvalidArgument: (:) [Get-WinEvent], Exception
>     + FullyQualifiedErrorId : LogsAndProvidersDontOverlap,Microsoft.PowerShell.Commands.GetWinEventCommand
> ```
> 
> - But this command works:
> 
> ```bash
> Get-WinEvent -FilterHashtable @{
>     LogName='System'
>     ProviderName='Service Control Manager'
> }
> ```
> 
> - Because SCM provider does write to the `System` log.
### FilterHashtable

| Key                  | Type        | Description                                             |
| -------------------- | ----------- | ------------------------------------------------------- |
| `LogName`            | `String[]`  | Live log channel name.                                  |
| `ProviderName`       | `String[]`  | Provider (source) that generated the event.             |
| `Path`               | `String[]`  | `.evtx` / `.evt` / `.etl` file to retrieve events from. |
| `ID`                 | `Int32[]`   | Event ID(s).                                            |
| `Level`              | `Int32[]`   | Severity level (`1`-`5`).                               |
| `Keywords`           | `Long[]`    | Keyword bitmask flags.                                  |
| `StartTime`          | `DateTime`  | Start of time range (inclusive).                        |
| `EndTime`            | `DateTime`  | End of time range (exclusive).                          |
| `UserID`             | `SID`       | SID of the user associated with the event.              |
| `Data`               | `String[]`  | Matches against any field in `EventData`.               |
| `SuppressHashFilter` | `Hashtable` | Exclude matching events.                                |
| `<named-data>`       |             | Specific `EventData` field.                             |

- Get `Security` log events:

```powershell
Get-WinEvent -FilterHashtable @{LogName='Security'}
```

- Failed logons (Event ID `4625`):

```powershell
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4625}
```

- Event ID `4625` (failed logons) + `4624` (successful logons) — multiple Event IDs:

```powershell
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4624,4625}
```

- Last 24 hours:

```powershell
$start=(Get-Date).AddHours(-24)
Get-WinEvent -FilterHashtable @{LogName='Security'; StartTime=$start}
```

| Command                          | Description      |
| -------------------------------- | ---------------- |
| `(Get-Date).AddDays(-1)`         | Last 24 hours.   |
| `(Get-Date).AddDays(-7)`         | Last 7 days.     |
| `(Get-Date).AddHours(-1)`        | Last hour.       |
| `(Get-Date).AddMinutes(-10)`     | Last 10 minutes. |
| `Get-Date "2026-03-29"`          | Specific date.   |
| `Get-Date "2026-03-29 10:15:00"` | Date + time.     |
>[!important] `Get-Date` returns a `DateTime` object, not a string. To query a specific date, you need to convert its string representation to an object `-FilterHashtable` can work with.

- Specific time window:

```powershell
Get-WinEvent -FilterHashtable @{
    LogName='Security'
    StartTime=(Get-Date "2026-03-29 10:00")
    EndTime=(Get-Date "2026-03-29 12:00")
}
```

> [!note]+ `StartTime` and `EndTime`
> - `StartTime` → inclusive
> - `EndTime` → exclusive

- Filter by provider:

```powershell
Get-WinEvent -FilterHashtable @{LogName='System'; ProviderName='Service Control Manager'}
```

- Read from `.evtx` file:

```powershell
Get-WinEvent -FilterHashtable @{Path='C:\Logs\Security.evtx'; Id=4625}
```


- Get events only with a severity level `2` (`Error`):

```powershell
Get-WinEvent -FilterHashtable @{LogName='System'; Level=2}
```

| #   | Level         |
| --- | ------------- |
| `1` | `Critical`    |
| `2` | `Error`       |
| `3` | `Warning`     |
| `4` | `Information` |
| `5` | `Verbose`     |

- Exclude events with a severity level of `4` (`Information`):

```powershell
Get-WinEvent -FilterHashtable @{LogName='Application'; SuppressHashFilter=@{Level=4}}
```

- Get all `Security` events generated under `SYSTEM`:

```powershell
Get-WinEvent -FilterHashtable @{LogName='Security'; UserID='S-1-5-18'}
```

- Find share creation events in `.evtx` logs located in the current directory:

```powershell
Get-WinEvent -FilterHashtable @{Path = "$(pwd)\*.evtx"; Id=5142}
```

> [!warning] When using `-FilterHashtable`, always use the `Path` key inside the hashtable. Using the `-Path` cmdlet option with `-FilterHashtable` will throw an error.

#### FilterXPath

>[!tip]+ Use `-FilterXPath` when you need **named fields**.

- Failed logons (Event ID `4624`):

```powershell
Get-WinEvent -LogName Security -FilterXPath "*[System[EventID=4624]]"
```

- Failed `Administrator` logons (specific `EventData` field of Event ID `4625` events):

```powershell
Get-WinEvent -LogName Security -FilterXPath "*[System[EventID=4625] and EventData[Data[@Name='TargetUserName']='Administrator']]"
```

> [!important]+ Retrieve properties of a specific Event ID you can filter by (+ field names)
> 
> ```powershell
> Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4624} -MaxEvents 1 |
>     ForEach-Object {
>         [xml]$xml = $_.ToXml()
>         $xml.Event.EventData.Data
>     }
> ```
>- This command takes the first event with a chosen Event ID and returns all its properties along with property names. You can use it to see what you can filter based on.


>[!example]+
> ```powershell
> Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4624} -MaxEvents 1 |
>     ForEach-Object {
>         [xml]$xml = $_.ToXml()
>         $xml.Event.EventData.Data
>     }
> ```
> 
> ```powershell
> Name                      #text
> ----                      -----
> SubjectUserSid            S-1-5-18
> SubjectUserName           WIN-1O0UJBNP9G7$
> SubjectDomainName         WORKGROUP
> SubjectLogonId            0x3e7
> TargetUserSid             S-1-5-21-1881654409-284601696-3713096779-500
> TargetUserName            Administrator
> TargetDomainName          WIN-1O0UJBNP9G7
> TargetLogonId             0x77c607
> LogonType                 10
> LogonProcessName          User32
> AuthenticationPackageName Negotiate
> WorkstationName           WIN-1O0UJBNP9G7
> LogonGuid                 {00000000-0000-0000-0000-000000000000}
> TransmittedServices       -
> LmPackageName             -
> KeyLength                 0
> ProcessId                 0x7f0
> ProcessName               C:\Windows\System32\svchost.exe
> IpAddress                 10.113.69.122
> IpPort                    0
> ImpersonationLevel        %%1833
> RestrictedAdminMode       %%1843
> TargetOutboundUserName    -
> TargetOutboundDomainName  -
> VirtualAccount            %%1843
> TargetLinkedLogonId       0x0
> ElevatedToken             %%1842
> ```

- Specific `.evtx` file:

```powershell
Get-WinEvent -Path "C:\Logs\Security.evtx" -FilterXPath "*[System[EventID=4624]]"
```

- Filter by time range using XPath:

```powershell
Get-WinEvent -LogName Security -FilterXPath "*[System[TimeCreated[@SystemTime>='2026-03-01T00:00:00.000Z' and @SystemTime<='2026-03-02T00:00:00.000Z']]]"
```

- Match a partial string using `contains()`:

```powershell
Get-WinEvent -LogName Security -FilterXPath "*[System[EventID=4688] and EventData[contains(Data[@Name='CommandLine'],'powershell')]]"
```

- Filter from an `.evtx` file using XPath:

```powershell
Get-WinEvent -Path "C:\Logs\Security.evtx" -FilterXPath "*[System[EventID=4624]]"
```

### Filtering with -FilterXml

>[!tip] `-FilterXml` is the most reliable option for complex queries. It accepts the full `<QueryList>` XML structure — the same format used in Event Viewer's custom filter editor.

- Failed logons (Event ID `4625`):

```powershell
$xml = @"
<QueryList>
  <Query Id="0" Path="Security">
    <Select Path="Security">
      *[System[EventID=4625]]
    </Select>
  </Query>
</QueryList>
"@

Get-WinEvent -FilterXml $xml
```

- Multiple Event IDs (`OR` logic):

```powershell
$xml = @"
<QueryList>
  <Query Id="0" Path="Security">
    <Select Path="Security">
      *[System[(EventID=4624 or EventID=4625)]]
    </Select>
  </Query>
</QueryList>
"@

Get-WinEvent -FilterXml $xml
```

- Failed `Administrator` logons (specific `EventData` field of Event ID `4625` events):

```powershell
$xml = @"
<QueryList>
  <Query Id="0" Path="Security">
    <Select Path="Security">
      *[
        System[EventID=4625]
        and
        EventData[Data[@Name='TargetUserName']='Administrator']
      ]
    </Select>
  </Query>
</QueryList>
"@

Get-WinEvent -FilterXml $xml
```

- Filter by time range:

```powershell
$xml = @"
<QueryList>
  <Query Id="0" Path="Security">
    <Select Path="Security">
      *[
        System[
          TimeCreated[
            @SystemTime >= '2026-03-29T00:00:00.000Z'
            and
            @SystemTime <= '2026-03-29T00:00:00.000Z'
          ]
        ]
      ]
    </Select>
  </Query>
</QueryList>
"@

Get-WinEvent -FilterXml $xml
```

- Multi-log query (unique to `-FilterXml`):

```powershell
$xml = @"
<QueryList>
  <Query Id="0" Path="Security">
    <Select Path="Security">*[System[EventID=4625]]</Select>
  </Query>
  <Query Id="1" Path="System">
    <Select Path="System">*[System[EventID=7045]]</Select>
  </Query>
</QueryList>
"@

Get-WinEvent -FilterXml $xml
```

- Suppress noise:

```powershell
$xml = @"
<QueryList>
  <Query Id="0" Path="Security">
    <Select Path="Security">
      *[System[EventID=4624]]
    </Select>
    <Suppress Path="Security">
      *[EventData[Data[@Name='TargetUserName']='ANONYMOUS LOGON']]
    </Suppress>
  </Query>
</QueryList>
"@

Get-WinEvent -FilterXml $xml
```

- Combine multiple conditions:

```powershell
$xml = @"
<QueryList>
  <Query Id="0" Path="Security">
    <Select Path="Security">
      *[
        System[EventID=4688]
        and
        EventData[
          Data[@Name='CommandLine']
          and
          (contains(.,'powershell') or contains(.,'cmd'))
        ]
      ]
    </Select>
  </Query>
</QueryList>
"@

Get-WinEvent -FilterXml $xml
```

> [!note] Logon Type `5` is a Service logon. It comes useful to suppress it when you're inspecting interactive or network logons.

## Event channels and providers
### Log names (event channels)

- Core Windows logs:

| `LogName`         | Description                                                                                                                                                                                                                         |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Security`        | **Application log** — Events logged by installed applications and services, including application crashes, service errors, application-specific warnings, and runtime failures.                                                     |
| `System`          | **Security log** — Audit events governed by the system audit policy (e.g., logon/logoff, authentication success/failure, privilege use/change, account lockouts).<br>Used for detecting unauthorized access and malicious activity. |
| `Application`     | **System log** — Events from Windows system components (kernel, drivers, services). Useful for OS troubleshooting (e.g., service start/stop, driver load errors, hardware issues).                                                  |
| `Setup`           | **Setup log** — Events related to OS installations, feature upgrades, role additions, and software setups. Important for correlating configuration changes or installation issues.                                                  |
| `ForwardedEvents` | **Forwarded Events** — used in enterprise logging to collect and store event logs sent from remote machines (Windows Event Forwarding, WE). <br>Not enabled by default on standalone client systems.                                |

- Operational:


| **Channel Name**                                         | **Description**                                                                                              |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `Microsoft‑Windows‑GroupPolicy/Operational`              | Group Policy operational events (application of GPOs, errors, processing). Great for policy troubleshooting. |
| `Microsoft‑Windows‑TaskScheduler/Operational`            | Task Scheduler activities (tasks created, run results, failures).                                            |
| `Microsoft‑Windows‑AppXDeploymentServer/Operational`     | AppX deployment and update events (Microsoft Store installs).                                                |
| `Microsoft‑Windows‑Store/Operational`                    | Windows Store install/update events.                                                                         |
| `Microsoft‑Windows‑EapHost/Operational**`                | EAP (network authentication) operations — useful in network auth diagnostics.                                |
| `Microsoft‑Windows‑StateRepository/Operational`          | State repository operations, often used internally by system components.                                     |
| `Windows PowerShell/Operational`                         | PowerShell engine start/stop, detailed script execution events.                                              |
| `Microsoft‑Windows‑WindowsUpdateClient/Operational`      | Windows Update client activity (updates installed, failures).                                                |
| `Microsoft‑Windows‑WER‑SystemErrorReporting/Operational` | System error reporting (e.g., BSOD or application crash dumps; path to machine error reports logged).        |

- Services/components:

| **Channel Name**                                          | **Description**                                                                                          |
| --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `Microsoft‑Windows‑CAPI2/Operational`                     | Cryptographic API logging (certificate chain validation, etc.) — often useful in TLS/PKI investigations. |
| `Microsoft‑Windows‑DriverFrameworks‑UserMode/Operational` | User mode driver framework messages; useful for driver load/unload and device interface events.          |
| `Microsoft‑Windows‑AppLocker/EXE and DLL`                 | AppLocker policy enforcement for `.exe`/`.dll` execution.                                                |
| `Microsoft‑Windows‑AppLocker/MSI and Script`              | AppLocker rules for installers and scripts.                                                              |

- Custom/product-specific:

| **Example Channel Name**                                                        | **Description**                                                       |
| ------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `Microsoft‑Windows‑Backup/Operational`                                          | Windows native backup operational results.                            |
| `Microsoft‑Windows‑DNS Server/Operational`                                      | DNS server query, zone, and DNS resolution events. (DNS role logging) |
| `Microsoft‑Windows‑RemoteDesktopServices‑RemoteDesktopServicesCore/Operational` | RDP session and RDS core activities.                                  |
| `Microsoft‑Windows‑WLAN‑AutoConfig/Operational`                                 | Wi‑Fi association/connection events.                                  |
| `Microsoft‑Windows‑Windows Firewall with Advanced Security/Firewall`            | Firewall policy and block/allow decision logs.                        |
| `Microsoft‑Windows‑Bluetooth/Operational`                                       | Bluetooth adapter and device events.                                  |
### Event Providers

- Security & OS-level:

| Provider name                        | Where it logs                                    | Description                                                                                                                                                                                                                                            |
| ------------------------------------ | ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `Microsoft‑Windows‑SecurityAuditing` | `Security`                                       | The **primary built‑in Windows security audit provider**. Emits authentication, logon/logoff, account management, privilege usage, object access, policy change events (e.g., `4624`, `4625`, `4720`). Used for virtually all security event analysis. |
| `Service Control Manager`            | `System`                                         | Emits events related to **service or driver start/stop/failure**, such as service installation, termination, and status changes.                                                                                                                       |
| `Microsoft‑Windows‑Windows Defender` | `Microsoft‑Windows‑Windows Defender/Operational` | Windows Defender Antivirus provider. Emits malware detection, threat removal, update, scan events in Defender operational log.                                                                                                                         |
| `Microsoft‑Windows‑GroupPolicy`      | `Microsoft‑Windows‑GroupPolicy/Operational`      | Logs Group Policy processing errors, successes, GPO application events — critical for configuration and system hardening analysis.                                                                                                                     |
| `Microsoft‑Windows‑PowerShell`       | `Windows PowerShell/Operational`                 | Emits PowerShell engine events such as script start/stop, module loads, pipeline execution (detailed PowerShell activity). Often used in threat hunting.                                                                                               |
| `Microsoft‑Windows‑Sysmon`           | `Microsoft‑Windows‑Sysmon/Operational`           | _If Sysmon is installed_, this provider emits detailed system tracking (process create, network connect, file create, registry changes) — extremely useful for DFIR.                                                                                   |
| `Microsoft‑Windows‑DNS‑Client`       | `Microsoft‑Windows‑DNS‑Client/Operational`       | DNS client behavior, useful for DNS investigation and name resolution tracking.                                                                                                                                                                        |

- Useful components & service providers:


| **Provider name**                             | Where it logs                                             | Description                                                                                                          |
| --------------------------------------------- | --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `Microsoft‑Windows‑TaskScheduler`             | `Microsoft‑Windows‑TaskScheduler/Operational`             | Logs scheduled task events: creation, execution results, failures.                                                   |
| `Microsoft‑Windows‑WindowsUpdateClient`       | `Microsoft‑Windows‑WindowsUpdateClient/Operational`       | Windows Update operations — update installations, reboots required, failures.                                        |
| `Microsoft‑Windows‑AppLocker`                 | `AppLocker/EXE and DLL / MSI and Script`                  | AppLocker audit/enforcement for executable, DLL, MSI, script rules (useful to detect blocked/allowed exec patterns). |
| `Microsoft‑Windows‑CAPI2`                     | `Microsoft‑Windows‑CAPI2/Operational`                     | Cryptography API events — certificate validation and trust chain behavior.                                           |
| `Microsoft‑Windows‑DriverFrameworks‑UserMode` | `Microsoft‑Windows‑DriverFrameworks‑UserMode/Operational` | User‑mode driver framework events — driver load/creation notifications.                                              |
- Network & connectivity:

| Provider name                                                       | Where it logs                                                                   | Description                                                                                    |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `Microsoft‑Windows‑WLAN‑AutoConfig`                                 | `Microsoft‑Windows‑WLAN‑AutoConfig/Operational`                                 | Wireless LAN events: association, disassociation, configuration events on Wi‑Fi interfaces.    |
| `Microsoft‑Windows‑DNS‑Server`                                      | `Microsoft‑Windows‑DNS‑Server/Operational*`                                     | DNS server events on servers (look up DNS role behavior). Often used in DNS forensic analysis. |
| `Microsoft‑Windows‑RemoteDesktopServices‑RemoteDesktopServicesCore` | `Microsoft‑Windows‑RemoteDesktopServices‑RemoteDesktopServicesCore/Operational` | RDP session events, errors, licensing, connection events.                                      |
- Applications:

| Provider name                            | Where it logs                                        | ****Description**                                                          |
| ---------------------------------------- | ---------------------------------------------------- | -------------------------------------------------------------------------- |
| `Application Error`                      | `Application`                                        | Application crash and fault messages for executables running in user‑mode. |
| `Windows PowerShell`                     | `Windows PowerShell/Operational`                     | Record PowerShell script execution, command lines (great for hunting).     |
| `Microsoft‑Windows‑AppXDeploymentServer` | `Microsoft‑Windows‑AppXDeploymentServer/Operational` | AppX installation and deployment events (Microsoft Store app delivery).    |
| `Microsoft‑Windows‑StateRepository`      | `Microsoft‑Windows‑StateRepository/Operational`      | OS state repository activity (system configuration changes).               |