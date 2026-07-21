---
created: 2026-07-21
tags:
  - Windows
  - Windows_PrivEsc
status: draft
---

## `Event Log Readers`

![[🛠️ Windows groups#`Event Log Readers`]]

- Confirm group membership:

```powershell
net localgroup "Event Log Readers"
```

- 
	- Many Windows commands support passing credentials, such as usernames and passwords, as parameters, visible in command history and logs. 
## Searching `Security` logs using `wevutil` and `Get-WinEvent`

explain commands

```powershell
wevtutil qe Security /rd:true /f:text | Select-String "/user"
```

We can also specify alternate credentials for `wevtutil` using the parameters `/u` and `/p`.

```powershell
wevtutil qe Security /rd:true /f:text | Select-String "/user"
```

- Credential search:

```powershell
wevtutil qe Security /rd:true /f:text | findstr /i "pass password user"
```

```powershell
Get-WinEvent -LogName Security | Where-Object {
    $_.Message -match "pass|password|user"
}
```

>[!important] Searching the `Security` event log with `Get-WInEvent` requires administrator access or permissions adjusted on the registry key `HKLM\System\CurrentControlSet\Services\Eventlog\Security`. Membership in just the `Event Log Readers` group is not sufficient.

- Process creation events (Event ID `4688`):

```powershell
wevtutil qe Security /rd:true /f:text "/q:*[System[EventID=4688]]" | findstr /i "pass user"
```

```powershell
Get-WinEvent -LogName security | where { $_.ID -eq 4688 -and $_.Properties[8].Value -like '*/user*'} | Select-Object @{name='CommandLine';expression={ $_.Properties[8].Value }}
```

```powershell
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4688} |
Where-Object {
    $_.Properties[8].Value -match "pass|user"
} |
Select-Object @{n="CommandLine";e={$_.Properties[8].Value}}
```


- `runas`/explicit credentials (Event ID `4648`):

```powershell
wevtutil qe Security "/q:*[System[EventID=4648]]"
```

```powershell
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4648}
```

- Explicit credentials in command line (Event ID `4648`):

```powershell
wevtutil qe Security "/q:*[System[EventID=4688] and EventData[Data[contains(.,'pass')]]]"
```

```powershell
Get-WinEvent -LogName Security -FilterXPath "*[
  System[EventID=4688]
  and
  EventData[contains(Data,'pass')]
]"
```

- Search for specific tools:

```powershell
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4688} |
Where-Object {
    $_.Properties[8].Value -match "net use|cmdkey|runas"
}
```

- Remote machine logs:

```powershell
wevtutil qe Security /r:<target> /u:<domain>\user /p:<password> /rd:true | findstr /i "pass"
```

```powershell
Get-WinEvent -LogName Security -ComputerName <target> -Credential (Get-Credential)
```

> [!note]+ Option breakdown: `wevtutil`
> 
> - `qe`: Query events from a log.
> - `/q:<xpath>`: Filter using XPath (core filtering method).
> - `/rd:true`: Reverse order (newest first).
> - `/c:<n>`: Limit number of events.
> - `/f:text|xml`: Output format (text for grep, XML for parsing).
> - `/r:<host>`: Query remote system.
> - `/u:<user>`: Username for authentication.
> - `/p:<pass>`: Password (visible in command line).
> - `/lf:true`: Treat target as `.evtx` file instead of live log.

> [!note]+ Option breakdown: `Get-WinEvent`
> 
> - `-LogName`: Specify log (e.g., `Security`).
> - `-FilterHashtable`: Fast filtering by fields (`Id`, `LogName`, `Time`).
> - `-FilterXPath`: Precise filtering (required for `EventData` fields).
> - `-MaxEvents`: Limit number of events returned.
> - `-Oldest`: Return oldest first.
> - `-ComputerName`: Query remote system.
> - `-Credential`: Authenticate as another user.
> - `Where-Object`: Post-filtering (slower but flexible).
### `Get-WinEvent`

- Basic keyword search:



- Relevant Event IDs:

| Event ID                                                                                           | Why it matters                                                                           |
| -------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| [`4688`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4688) | A new process was created on the system (plaintext credentials in command-line options). |
| [`4624`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4624) | An account was successfully logged on (who authenticated).                               |
| [`4625`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4625) | An account failed to log on.                                                             |
| [`4648`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4648) | A logon attempt was made using explicit credentials (e.g., RunAs, scheduled tasks).      |
| [`4672`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4672) | Special privileges were assigned to a new logon session.                                 |
| [`4768`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4768) | A Kerberos TGT (Ticket-Granting Ticket) was requested from a DC.                         |
| [`4769`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4769) | A Kerberos ST (Service Ticket) was requested from a DC.                                  |

>[!note] For a more complete list, see [[Windows Logs Cheat Sheet#Windows Event IDs]].

### Credential hunting in Windows logs

Suppose [auditing of process creation](https://docs.microsoft.com/en-us/windows/security/threat-protection/auditing/audit-process-creation) events and corresponding command line values is enabled. In that case, this information is saved to the Windows security event log as event ID [4688: A new process has been created](https://docs.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4688). Organizations may enable logging of process command lines to help defenders monitor and identify possibly malicious behavior and identify binaries that should not be present on a system. This data can be shipped to a SIEM tool or ingested into a search tool, such as ElasticSearch, to give defenders visibility into what binaries are being run on systems in the network. The tools would then flag any potentially malicious activity, such as the `whoami`, `netstat`, and `tasklist` commands being run from a marketing executive's workstation.

This [study](https://blogs.jpcert.or.jp/en/2016/01/windows-commands-abused-by-attackers.html) shows some of the most run commands by attackers after initial access (`tasklist`, `ver`, `ipconfig`, `systeminfo`, etc.), for reconnaissance (`dir`, `net view`, `ping`, `net use`, `type`, etc.), and for spreading malware within a network (`at`, `reg`, `wmic`, `wusa`, etc.). Aside from monitoring for these commands being run, an organization could take things a step further and restrict the execution of specific commands using fine-tuned AppLocker rules. For an organization with a tight security budget, leveraging these built-in tools from Microsoft can offer excellent visibility into network activities at the host level. Most modern enterprise EDR tools perform detection/blocking but can be out of reach for many organizations due to budgetary and personnel constraints. This small example shows that security improvements, such as network and host-level visibility, can be done with minimal effort, cost, and massive impact.


I performed a penetration test against a medium-sized organization a few years ago with a small security team, no enterprise EDR, but was using a similar configuration to what was detailed above (auditing process creation and command-line values). They caught and contained one of my team members when they ran the `tasklist` command from a member of the finance department's workstation (after capturing credentials using `Responder` and cracking them offline).

Administrators or members of the [Event Log Readers](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-R2-and-2012/dn579255\(v=ws.11\)?redirectedfrom=MSDN#event-log-readers) group have permission to access this log. It is conceivable that system administrators might want to add power users or developers into this group to perform certain tasks without having to grant them administrative access.




Microsoft has published a reference [guide](https://download.microsoft.com/download/5/8/9/58911986-D4AD-4695-BF63-F734CD4DF8F2/ws-commands.pdf) for all built-in Windows commands, including syntax, parameters, and examples. Many Windows commands support passing a password as a parameter, and if auditing of process command lines is enabled, this sensitive information will be captured.

We can query Windows events from the command line using the [wevtutil](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/wevtutil) utility and the [Get-WinEvent](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.diagnostics/get-winevent?view=powershell-7.1) PowerShell cmdlet.

#### Searching Security Logs Using wevtutil

```powershell
wevtutil qe Security /rd:true /f:text | Select-String "/user"
```
```powershell
	Process Command Line: net use T: \\fs01\backups /user:tim MyStr0ngP@ssword
```

We can also specify alternate credentials for `wevtutil` using the parameters `/u` and `/p`.

#### Passing Credentials to wevtutil

```powershell
wevtutil qe Security /rd:true /f:text /r:share01 /u:julie.clay /p:Welcome1 | findstr "/user"
```

For `Get-WinEvent`, the syntax is as follows. In this example, we filter for process creation events (4688), which contain `/user` in the process command line.

Note: Searching the `Security` event log with `Get-WInEvent` requires administrator access or permissions adjusted on the registry key `HKLM\System\CurrentControlSet\Services\Eventlog\Security`. Membership in just the `Event Log Readers` group is not sufficient.

#### Searching Security Logs Using Get-WinEvent

```powershell
Get-WinEvent -LogName security | where { $_.ID -eq 4688 -and $_.Properties[8].Value -like '*/user*'} | Select-Object @{name='CommandLine';expression={ $_.Properties[8].Value }}
```

```powershell
CommandLine 
----------- 
net use T: \\fs01\backups /user:tim MyStr0ngP@ssword
```

The cmdlet can also be run as another user with the `-Credential` parameter.

Other logs include [PowerShell Operational](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_logging_windows?view=powershell-7.1) log, which may also contain sensitive information or credentials if script block or module logging is enabled. This log is accessible to unprivileged users.

>[!example]+ Complete example
> Using the methods demonstrated in this section find the password for the user `mary`.
> 
> 
> - `whoami`:
> 
> ```powershell
> PS C:\Users\logger> whoami /groups
> ```
> 
> ```powershell
> GROUP INFORMATION
> -----------------
> 
> Group Name                             Type             SID          Attributes
> ====================================== ================ ============ ==================================================
> Everyone                               Well-known group S-1-1-0      Mandatory group, Enabled by default, Enabled group
> BUILTIN\Event Log Readers              Alias            S-1-5-32-573 Mandatory group, Enabled by default, Enabled group
> BUILTIN\Remote Desktop Users           Alias            S-1-5-32-555 Mandatory group, Enabled by default, Enabled group
> BUILTIN\Users                          Alias            S-1-5-32-545 Mandatory group, Enabled by default, Enabled group
> NT AUTHORITY\REMOTE INTERACTIVE LOGON  Well-known group S-1-5-14     Mandatory group, Enabled by default, Enabled group
> NT AUTHORITY\INTERACTIVE               Well-known group S-1-5-4      Mandatory group, Enabled by default, Enabled group
> NT AUTHORITY\Authenticated Users       Well-known group S-1-5-11     Mandatory group, Enabled by default, Enabled group
> NT AUTHORITY\This Organization         Well-known group S-1-5-15     Mandatory group, Enabled by default, Enabled group
> NT AUTHORITY\Local account             Well-known group S-1-5-113    Mandatory group, Enabled by default, Enabled group  LOCAL                                  Well-known group S-1-2-0      Mandatory group, Enabled by default, Enabled group
> NT AUTHORITY\NTLM Authentication       Well-known group S-1-5-64-10  Mandatory group, Enabled by default, Enabled group  
> ```
> 
> 
> - Confirm group membership:
> 
> 
> ```powershell
> net localgroup "Event Log Readers"
> ```
> 
> ```powershell
> Alias name     Event Log Readers
> Comment        Members of this group can read event logs from local machine
> 
> Members                                                                              -------------------------------------------------------------------------------    logger
> The command completed successfully.
> ```
> 
> - Search security logs:
> 
> ```powershell
> wevtutil qe Security /rd:true /f:text | Select-String "/user"
> ```
> ```powershell
>        Process Command Line:   cmdkey  /add:WEB01 /user:amanda /pass:Passw0rd!
>        Process Command Line:   net  use Z: \\DB01\scripts /user:mary W1ntergreen_gum_2021!
>        Process Command Line:   net  use T: \\fs01\backups /user:tim MyStr0ngP@ssword
> ```

## References and further reading

- [`Event Log readers — OSCP-CPTS NOTES`](https://notes.dollarboysushil.com/windows-privilege-escalation/group-privileges/event-log-readers)