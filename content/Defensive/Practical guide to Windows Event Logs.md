---
created: 2026-03-16
---
## Windows Event Logs

>**Windows Event Logs** are a centralized record of system, security, and application events in the Windows operating system, used for troubleshooting, monitoring, and security analysis.

- Even logs are stored as **XML files** with an **`.evtx` extension**, primarily located at `C:\Windows\System32\winevt\Logs`.  

```powershell
C:\Windows\System32\winevt\Logs
```

>[!note] See [[#Appendix A Common event log files]].

- The **Windows Event Log service (`eventlog`)** runs inside a shared `svchost.exe` process. It is responsible for:
	- Receiving events from registered providers via **Event Tracing for Windows (ETW)**.
	- Writing events to the correct **event channels** and writing then to corresponding `.evtx` files on disk.
	- Enforcing per-log **ACLs** — not every log is readable by every user.
	- Handling **log rotation**: when a log hits its configured max size, it either overwrites old entries (`Circular`), retains them (`Retain`), or archives them (`AutoBackup`).
	- Exposing events to consumers via the **Windows Event Log API**.

>[!warning]+ When you pull `.evtx` files off a system during IR, you're working with the on-disk representation of what the `eventlog` service wrote. Log rotation means evidence can be **silently overwritten**. The `Security.evtx` default max size is only 20 MB — on an active domain controller, that can roll over in hours. 

>[!note] To learn more about how Windows logging infrastructure works, refer to [[Windows Logging Infrastructure_]]. This guide is mostly practical.

There are two primary tools used to access and query Windows Logs:
- **Event Viewer (GUI)**
- `Get-WinEvent` cmdlet

## Event Viewer

>**[Event Viewer](https://learn.microsoft.com/en-us/shows/inside/event-viewer) (`eventvwr.msc`)** is a native Windows interface for inspecting event logs.

- Event Viewer exposes logs from Windows core components (`Application`, `Security`, `System`, `Setup`, `Forwarded Events`), services and applications (`Applications and Services Logs`), and tools like Sysmon.
- It's good for manual triage and simple investigation, but not suitable for large-scale analysis, correlation, or automation.

```powershell
eventvwr.msc
```

### Anatomy of an event

- Each event has two main views: **General** and **Details**.
#### General tab

The `General` tab contains high-level event metadata:

- `Log Name` 
	- The log category this event belongs to (`Security`, `System`, `Application`, etc.).

- `Source`
	- The component that generated the event (e.g.,  `Microsoft-Windows-Security-Auditing`, `Service Control Manager`, or `Microsoft-Windows-PowerShell`).

- `Event ID`
	- A numeric identifier for the event type; often the primary filter criterion.
	- For example, Event ID `4624` always means `successful logon`, and Event ID `4625` always means `failed logon`.

- `Task Category`
	- A higher-level classification that groups related event IDs. For example, the category `Logon` includes Event IDs `4624`, `4625`, `4634`, and others.
	- Less specific than Event ID but useful for broad queries.

- `Level`
	- Severity classification — `Information`, `Warning`, `Error`, `Critical`, and `Verbose`. 
	- Most security events are classified as `Information` because they're audit records, not errors. Don't filter by `Level` when hunting for malicious activity.

- `Keywords`
	- Flags that categorize events (e.g., `Audit Success` and `Audit Failure`) for Security log events.

- `User`
	- The security context which generated the event. 
	- For authentication events, this is usually `SYSTEM` (since the authentication subsystem is what logs the event, not the user). 
	- For process creation (with Sysmon or advanced auditing), this is the user who launched the process.

- `OpCode`
	- Identifies the specific operation being reported.
	- This is mostly useful for debugging and correlation in application logs. In Security logs, it's less commonly used.

- `Logged`
	- The timestamp when the event was written to the log.
	- Watch for timezone offsets and clock skew when correlating events across systems.

- `Computer`
	- The hostname of the system that generated the event. 
	- In Forwarded Event logs, distinguishes between source systems.

- `More Information`
	- A link to Microsoft's online documentation for the event. Useful when encountering unfamiliar event IDs, but the quality of documentation varies.


![[event_general.png]]

#### Details tab

- The `Details` tab exposes the raw XML structure of the event.

```xml
<Event xmlns="http://schemas.microsoft.com/win/2004/08/events/event">
  <System>
    <Provider Name="Microsoft-Windows-Security-Auditing" Guid="{...}" />
    <EventID>4624</EventID>
    <Version>2</Version>
    <Level>0</Level>
    <Task>12544</Task>
    <Opcode>0</Opcode>
    <Keywords>0x8020000000000000</Keywords>
    <TimeCreated SystemTime="2026-03-15T10:30:45.123456Z" />
    <EventRecordID>12345</EventRecordID>
    <Correlation ActivityID="{...}" RelatedActivityID="{...}" />
    <Execution ProcessID="652" ThreadID="4028" />
    <Channel>Security</Channel>
    <Computer>DESKTOP-ABC123</Computer>
    <Security UserID="S-1-5-18" />
  </System>
  <EventData>
    <Data Name="SubjectUserSid">S-1-5-21-...</Data>
    <Data Name="SubjectUserName">SYSTEM</Data>
    <Data Name="TargetUserSid">S-1-5-21-...</Data>
    <Data Name="TargetUserName">Administrator</Data>
    <!-- More fields... -->
  </EventData>
</Event>
```

- The `<System>` block contains metadata common to all events.
- The `<EventData>` block contains the event-specific fields.
- Named `<Data>` fields (e.g., `TargetUserName`, `LogonType`) are what you use for filtering (such as XPath filters in Event Viewer, or filters in `Get-WinEvent`).

![[event_details_XML.png]]

- You can use `Friendly View` instead of reading raw XML:
 ![[event_details.png]]

#### Custom XML filters in Event Viewer

- The built-in filter dialog (`Actions` -> `Create Custom View...` -> `Filter`) in fine of basic scenarios — you can filter by Event ID, severity level, time range, user, and some other parameters.

![[create_custom_view.png]]

- However, it falls apart the moment you need to correlate on specific `EventData` field values. For that, you write custom XPath queries. 

- In `Actions` -> `Create Custom View...` panel, navigate to the `XML` tab and check `Edit query manually`:

![[edit_XML_manually.png]]


The query format is an XPath expression wrapped in a `<QueryList>` structure:

```xml
<QueryList>
  <Query Id="0" Path="Security">
    <Select Path="Security">
      *[System[EventID=4624]]
    </Select>
  </Query>
</QueryList>
```

>[!tip]+
>XPath structure in Event Viewer follows this pattern:
>
>`*[ System[...] and EventData[...] ]`
>
>- `System` → metadata (`EventID`, `TimeCreated`, `Provider`, etc.).
>- `EventData` → actual evidence (usernames, processes, paths, etc.).


- Filter by multiple event IDs:

```xml
<Select Path="Security">
  *[System[EventID=4624 or EventID=4625 or EventID=4648]]
</Select>
```

>[!note]+ XPath breakdown
>- `*` selects **all events**, and the predicate `[ ... ]` specifies the parameters based on which to match events.
>- `System[ ... ]` refers to the `<System>` element of the event XML (metadata common to all events).
>- `EventID=4624 or EventID=4625 or EventID=4648` matches events where `<EventID>` element (inside `<System>`) has any of the specified values.


- Filter on `EventData` fields:

```xml
<Select Path="Security">
  *[System[EventID=4625]]
  and
  *[EventData[Data[@Name='TargetUserName']='Administrator')]]
</Select>
```

>[!note]+ XPath breakdown
>- `EventData[...]` targets the `<EventData>` section, which contains **event-specific fields**.
>- `Data[@Name='TargetUserName']` selects `<Data>` elements whose `Name` attribute equals `TargetUserName`.
>- `='Administrator'` ensures that the **value of that field** equals `Administrator`.

>[!warning] Event Viewer evaluates each `*[...]` separately — both conditions must match the **same event**, not different ones.

- Filter by time:

```xml
<Select Path="Security">
  *[System[TimeCreated[
	  @SystemTime >= '2026-03-01T00:00:00.000Z' and 
	  @SystemTime &lt;= '2026-03-02T00:00:00.000Z'
	]]]
</Select>
```

>[!note]+ XPath breakdown
>- `TimeCreated[...]` selects the `<TimeCreated>` element inside `<System>`.
>- `@SystemTime` refers to the **timestamp attribute** (stored in UTC, ISO 8601 format).
>	- `>=` → start time (inclusive)
>	- `<=` → end time (inclusive)

>[!note] `&lt;` is the XML-safe form of `<`.

>[!warning] Event Viewer UI shows **local time**, but XPath uses **UTC (`Z`)**.

>[!example]+
> The following query checks whether `TiWorker.exe` modified the auditing settings (SACL) of a specific DLL — useful for detecting tampering with object auditing:
> 
> ```XML
> <QueryList>
>   <Query Id="0" Path="Security">
>     <Select Path="Security">*[System[(EventID=4907)]]
>     and
>     *[EventData[Data[@Name='ObjectName'] and (Data='C:\Windows\Microsoft.NET\Framework64\v4.0.30319\WPF\wpfgfx_v0400.dll')]]
>     and
>     *[EventData[Data[@Name='SubjectUserName'] and (Data='C:\Windows\WinSxS\amd64_microsoft-windows-servicingstack_31bf3856ad364e35_10.0.19041.1790_none_7df2aec07ca10e81\TiWorker.exe')]]
>     </Select>
>   </Query>
> </QueryList>
> ```
> Event ID `4907` fires whenever the SACL of an object (file, registry key, etc.) is changed. A SACL (System Access Control List) defines what access attempts generate audit log entries — changing it is a classic anti-forensics technique. See [Microsoft's Event 4907 documentation](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4907) and [SACL Access Right](https://learn.microsoft.com/en-us/windows/win32/secauthz/sacl-access-right).

## Get-WinEvent

>The [`Get-Event`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.diagnostics/get-winevent?view=powershell-7.5) cmdlet is used to query event logs and event tracing log files on local and remote systems.

- Syntax:

```powershell
Get-WinEvent -LogName <LogName> [-FilterXPath <XPath>] [-MaxEvents <Count>]
```

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

 
- List providers that contain a specific word in the name:

```powershell
Get-WinEvent -ListProvider *Policy*
```

>[!tip]+
> - To format output as a table, use the [`Format-Table`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/format-table?view=powershell-7.5) cmdlet:
> 
> ```powershell
> Get-WinEvent -ListProvider * | Format-Table -AutoSize
> ```
> 

- Listing event logs and providers:

| Option                     | Description                                |
| -------------------------- | ------------------------------------------ |
| `-ListLog <string[]>`      | List available event logs on the system.   |
| `-ListProvider <string[]>` | List event providers that generate events. |

- Querying events:

| Option                     | Description                                                               |
| -------------------------- | ------------------------------------------------------------------------- |
| `-LogName <string[]>`      | Retrieve events from the specified event log channels.                    |
| `-ProviderName <string[]>` | Retrieve events generated by specified providers.                         |
| `-Path <string[]>`         | Read events from the specified event log files (`.evtx`, `.evt`, `.etl`). |

- Filtering and sorting:

| Option                         | Description                                                    |
| ------------------------------ | -------------------------------------------------------------- |
| `-MaxEvents <int>`             | Limit the number of returned events.                           |
| `-FilterXml <xml>`             | Filter events using a structured XML query.                    |
| `-FilterXPath <string>`        | Filter events using an XPath query expression.                 |
| `-FilterHashtable <hashtable>` | Filter events using a simplified key-value query.              |
| `-Oldest`                      | Return events in chronological order starting with the oldest. |
| `-Force`                       | Include analytic and debug logs that are normally hidden.      |
- Querying logs on remote systems:

| Option                       | Description                                       |
| ---------------------------- | ------------------------------------------------- |
| `-ComputerName <string>`     | Retrieve events from a specified remote computer. |
| `-Credential <PSCredential>` | Authenticate using specified credentials.         |
### Querying events

- Get events from a live log:

```powershell
Get-WinEvent -LogName Security
```

- Get the latest 50 events from the Application log:

```powershell
Get-WinEvent -LogName Application -MaxEvents 50
```

- Read events from an exported `.evtx` file:

```powershell
Get-WinEvent -Path "C:\Logs\Security.evtx"
```

- Read from all `.evtx` files in the current directory:

```powershell
Get-WinEvent -Path "$(pwd)\*.evtx"
```

- Retrieve events from a remote computer:

```powershell
Get-WinEvent -LogName Security -ComputerName SRV01
```

### Filtering with -FilterHashtable

- Filter by log name — get all Security log events:

```powershell
Get-WinEvent -FilterHashtable @{
    LogName = 'Security'
}
```

- Filter by Event ID — get all failed logon:

```powershell
Get-WinEvent -FilterHashtable @{
    LogName = 'Security'
    ID = 4625
}
```

- Filter by multiple Event IDs — get all successful (`4624`), failed (`4625`), and privileged (`4672`) logon:

```powershell
Get-WinEvent -FilterHashtable @{
    LogName = 'Security'
    ID = 4624,4625,4672
}
```

- Filter by provider — get all events generated by Service Control Manager (SCM):

```powershell
Get-WinEvent -FilterHashtable @{
    LogName = 'System'
    ProviderName = 'Service Control Manager'
}
```

- Filter by time range — get all events from the last 24 hours:

```powershell
$Start = (Get-Date).AddHours(-24)

Get-WinEvent -FilterHashtable @{
    LogName = 'Security'
    StartTime = $Start
}
```

- Filter between two days:

```powershell
Get-WinEvent -FilterHashtable @{
    LogName = 'Security'
    StartTime = '2026-03-01'
    EndTime = '2026-03-02'
}
```

> [!note]+ `StartTime` and `EndTime`
> - `StartTime` → inclusive
> - `EndTime` → exclusive
>
>>[!example] `EndTime` of `2026-03-02` returns events up to but not including midnight on March the 2nd.

- Filter by severity level — get errors only:

```powershell
Get-WinEvent -FilterHashtable @{
    LogName = 'System'
    Level = 2
}
```

| Value | Level       |
| ----- | ----------- |
| `1`   | Critical    |
| `2`   | Error       |
| `3`   | Warning     |
| `4`   | Information |
| `5`   | Verbose     |

- Filter by provider name:

```powershell
Get-WinEvent -FilterHashtable @{
    LogName      = 'System'
    ProviderName = 'Service Control Manager'
}
```

- Filter by user SID — get all events from `SYSTEM`:

```powershell
Get-WinEvent -FilterHashtable @{
    LogName = 'Security'
    UserID = 'S-1-5-18'
}
```

- Filter events from an `.evtx` file:

```powershell
Get-WinEvent -FilterHashtable @{
    Path = 'C:\Logs\Security.evtx'
    ID = 4625
}
```

- Find share creation events in `.evtx` logs located in the current directory:

```powershell
Get-WinEvent -FilterHashtable @{
    Path = "$(pwd)\*.evtx"
    ID   = 5142 # share created
}
```

> [!warning] When using `-FilterHashtable`, always use the `Path` key inside the hashtable. Using the `-Path` cmdlet option with `-FilterHashtable` will throw an error.

- `FilterHashtable` keys:

| Key            | Type       | Description                                             |
| -------------- | ---------- | ------------------------------------------------------- |
| `LogName`      | `String[]` | Live log channel name.                                  |
| `ProviderName` | `String[]` | Provider (source) that generated the event.             |
| `Path`         | `String[]` | `.evtx` / `.evt` / `.etl` file to retrieve events from. |
| `ID`           | `Int32[]`  | Event ID(s).                                            |
| `Level`        | `Int32[]`  | Severity level (`1`-`5`).                               |
| `Keywords`     | `Long[]`   | Keyword bitmask flags.                                  |
| `StartTime`    | `DateTime` | Start of time range (inclusive).                        |
| `EndTime`      | `DateTime` | End of time range (exclusive).                          |
| `UserID`       | `SID`      | SID of the user associated with the event.              |
| `Data`         | `String[]` | Matches against any field in `EventData`.               |
### Accessing event properties

Event objects retrieved with `Get-WinEvent` have a `Properties` array that maps to the `<EventData>` fields in order. So the named fields you see in the XML (e.g., `TargetUserName`, `LogonType`) correspond to positional indices in this array.

- The index positions vary by event ID, so you need to know which position maps to which field. For example, for Event ID `4624` (successful logon):

```powershell
Get-WinEvent -FilterHashtable @{ LogName='Security'; Id=4624 } -MaxEvents 1 | 
	ForEach-Object { $_.Properties | ForEach-Object { $_.Value } }
```

- This dumps all field values so you can identify the index positions. Once known, you reference them directly:

```powershell
Get-WinEvent -FilterHashtable @{ LogName='Security'; Id=4624 } | ForEach-Object {
    [PSCustomObject]@{
        Time        = $_.TimeCreated
        TargetUser  = $_.Properties[5].Value   # TargetUserName
        Domain      = $_.Properties[6].Value   # TargetDomainName
        LogonType   = $_.Properties[8].Value   # LogonType
        SourceIP    = $_.Properties[18].Value  # IpAddress
        WorkStation = $_.Properties[11].Value  # WorkstationName
    }
} | Format-Table -AutoSize
```

>[!warning] Always verify indices when working with a new environment — they're not formally guaranteed and may change depending on the Windows version, event schema version, and audit policy configuration.

- The `Message` property contains the fully rendered, human-readable description of the event. Use this with `-match` for quick string searches when you don't know the property index:

```powershell
Get-WinEvent -FilterHashtable @{ LogName='Security'; Id=4688 } |
    Where-Object { $_.Message -match 'mimikatz' }
```
### XPath and XML filtering

- `-FilterHashtable` can directly filter on top-level `<System>` fields (e.g., `EventID`, `LogName`, `ProviderName`) — but it can't filter on specific named `<EventData>` fields.
- Although you can access `<EventData>` fields via the `.Properties[]` array, this happens *after the events are retrieved* (you're working with *.NET objects* `Get-WinEvents` returns using the `Where-Object` and  `ForEach-Object` cmdlets), not at query time. And since indexes may shift over time, this isn't reliable for automation. 
- For precise filtering on fields like `TargetUserName`, use XPath via `-FilterXPath` or the full `-FilterXml` approach.

#### Filtering with -FilterXPath

`-FilterXPath` takes a plain XPath string and applies it to the specified log:

- Filter by a single Event ID:

```powershell
Get-WinEvent -LogName Security -FilterXPath "*[System[EventID=4624]]"
```

- Filter by Event ID and a specific `EventData` field:

```powershell
Get-WinEvent -LogName Security -FilterXPath "*[System[EventID=4625] and EventData[Data[@Name='TargetUserName']='Administrator']]"
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

`-FilterXml` accepts the full `<QueryList>` XML structure — the same format used in Event Viewer's custom filter editor. This is the most reliable approach for complex queries.

- Query with a full XML filter:

```powershell
$xml = @"
<QueryList>
  <Query Id="0" Path="Security">
    <Select Path="Security">
      *[System[EventID=4625]]
      and
      *[EventData[Data[@Name='TargetUserName'] and (Data='Administrator')]]
    </Select>
  </Query>
</QueryList>
"@

Get-WinEvent -FilterXml $xml
```

- Multi-log query in a single pass (query Security and System simultaneously):

```powershell
$xml = @"
<QueryList>
  <Query Id="0" Path="Security">
    <Select Path="Security">*[System[EventID=4624 or EventID=4625]]</Select>
  </Query>
  <Query Id="1" Path="System">
    <Select Path="System">*[System[EventID=7045]]</Select>
  </Query>
</QueryList>
"@

Get-WinEvent -FilterXml $xml
```

- Suppress known-noisy entries while still pulling your target events:

```powershell
$xml = @"
<QueryList>
  <Query Id="0" Path="Security">
    <Select Path="Security">*[System[EventID=4624]]</Select>
    <Suppress Path="Security">
      *[EventData[Data[@Name='TargetUserName']='ANONYMOUS LOGON']]
    </Suppress>
    <Suppress Path="Security">
      *[EventData[Data[@Name='LogonType']='5']]
    </Suppress>
  </Query>
</QueryList>
"@

Get-WinEvent -FilterXml $xml
```

> [!note] Logon Type `5` is a Service logon. It comes useful to suppress it when you're inspecting interactive or network logons.
### Examples

- Get failed logon attempts in last 24 hours:

```powershell
$startTime = (Get-Date).AddHours(-24)
Get-WinEvent -FilterHashtable @{
    LogName = 'Security'
    ID = 4625
    StartTime = $startTime
} | ForEach-Object {
    [PSCustomObject]@{
        Time = $_.TimeCreated
        User = $_.Properties[5].Value
        Domain = $_.Properties[6].Value
        SourceIP = $_.Properties[19].Value
        Status = $_.Properties[7].Value
        SubStatus = $_.Properties[9].Value
    }
} | Format-Table -AutoSize
```

- Find RDP sessions (logon type `10`):

```powershell
Get-WinEvent -FilterHashtable @{
    LogName = 'Security'
    ID = 4624
} | Where-Object { $_.Properties[8].Value -eq 10 } | 
ForEach-Object {
    [PSCustomObject]@{
        Time = $_.TimeCreated
        User = $_.Properties[5].Value
        SourceIP = $_.Properties[18].Value
        Workstation = $_.Properties[11].Value
    }
} | Format-Table -AutoSize
```

- Get new user accounts created:

```powershell
Get-WinEvent -FilterHashtable @{
    LogName = 'Security'
    ID = 4720
} | ForEach-Object {
    [PSCustomObject]@{
        Time = $_.TimeCreated
        NewUser = $_.Properties[0].Value
        CreatedBy = $_.Properties[4].Value
    }
} | Format-Table -AutoSize
```

- Monitor `Domain Admins` and other privileged groups:

```powershell
Get-WinEvent -FilterHashtable @{
    LogName = 'Security'
    ID = 4728,4732,4756
} | ForEach-Object {
    [PSCustomObject]@{
        Time = $_.TimeCreated
        EventID = $_.Id
        MemberAdded = $_.Properties[0].Value
        GroupName = $_.Properties[2].Value
        ChangedBy = $_.Properties[6].Value
    }
} | Format-Table -AutoSize
```

- Find encoded PowerShell execution:

```powershell
Get-WinEvent -FilterHashtable @{
    LogName = 'Security'
    ID = 4688
} | Where-Object { 
    $_.Properties[8].Value -match 'powershell|cmd' -and 
    $_.Properties[8].Value -match '-enc|-e\s|base64'
} | ForEach-Object {
    [PSCustomObject]@{
        Time = $_.TimeCreated
        User = $_.Properties[1].Value
        CommandLine = $_.Properties[8].Value
        ParentProcess = $_.Properties[13].Value
    }
}
```

```powershell
Get-WinEvent -Path "$(pwd)\*.evtx"
```
## Sysmon

Windows Security logs handle authentication and high-level audit events, but they were never designed to capture details about process DLL loads, network connections, process parent-child relationships, raw file operations, or registry changes — events where your're looking for indicators of compromise. Sysmon bridges that gap.

>**[Sysmon (System Monitor)](https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon)** is a free kernel-mode driver and user-mode service developed by Microsoft as part of the Sysinternals suite. It logs detailed system activity — such as process creation, network connections, file changes, registry modifications, and driver loads — to the Windows Event Log.

- Sysmon itself **does not store logs**; it **monitors system activity**, **generates detailed logs**, and then writes these logs into the **Windows Event Log** system.

>[!note] Sysmon's unique capability lies in its ability to log information that typically doesn't appear in the Security Event logs by default.

>[!note]+ Installation
>- Download the `sysmon.exe` from official source: [Microsoft Sysinternals Sysmon](https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon).
>- To install Sysmon, run the following command as Administrator:
>```powershell
>sysmon.exe -i -accepteula -h md5,sha256,imphash -l -n
>```
>- `-i`: Install.
>- `-accepteula`: Accept license without prompting
>- `-h md5,sha256,imphash`: Hash algorithms (`MD5`, `SHA256`, `imphash` for PE files)
>- `-l`: Log to Windows Event Log.
>- `-n` — Log network connections (disabled by default; use this if you need network monitoring).
>
>To uninstall Sysmon, use `sysmon.exe -u` — this erases both driver and service.

- Sysmon events appear in Event Viewer under `Applications and Services Logs` -> `Microsoft` -> `Windows` -> `Sysmon` -> `Operational`.

![[sysmon_logs_location_in_event_viewer.png]]

![[sysmon_location_in_event_viewer_2.png]]

- To query Sysmon events using `Get-WinEvent`:

```powershell
Get-WinEvent -LogName "Microsoft-Windows-Sysmon/Operational"
```

### Sysmon Event ID reference

- Sysmon categorizes different types of system activity using **event IDs**, where each ID corresponds to a specific type of event.
- Here are some of the most important Sysmon event IDs:

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

>[!note] See [`Sysmon — Microsoft Learn`](https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon).
### Basic Sysmon configuration

- Without a proper configuration, you'll be drowned in noise. The service generates thousands of events per second on a busy system.
- Configuration files control what gets logged via `include` / `exclude` rules per event type:
	- `onmatch="include"` with no rules = **log nothing** (whitelist model). 
	- `onmatch="exclude"` with no rules = **log everything** (blacklist model).

- Recommended community baseline configurations:
	- [`SwiftOnSecurity/sysmon-config`](https://github.com/SwiftOnSecurity/sysmon-config) — solid baseline for most environments.
	- [`olafhartong/sysmon-modular`](https://github.com/olafhartong/sysmon-modular) — modular approach for custom builds.

>[!example]+
> ```xml
> <Sysmon schemaversion="4.82">
>   <EventFiltering>
>     
>     <!-- Process Creation: Log everything except known noise -->
>     <ProcessCreate onmatch="exclude">
>       <Image condition="is">C:\Windows\System32\svchost.exe</Image>
>       <Image condition="is">C:\Windows\System32\winlogon.exe</Image>
>       <CommandLine condition="contains">Windows Update</CommandLine>
>     </ProcessCreate>
> 
>     <!-- DLL Loading: Log everything (high volume, be careful) -->
>     <ImageLoad onmatch="exclude">
>       <Image condition="contains">C:\Windows\System32</Image>
>     </ImageLoad>
> 
>     <!-- Network Connections: Log only interesting destinations -->
>     <NetworkConnect onmatch="include">
>       <DestinationPort condition="is">443</DestinationPort>
>       <DestinationPort condition="is">80</DestinationPort>
>       <DestinationPort condition="is">4444</DestinationPort>
>       <DestinationPort condition="is">8080</DestinationPort>
>     </NetworkConnect>
> 
>     <!-- Registry: Log configuration changes -->
>     <RegistryEvent onmatch="exclude">
>       <TargetObject condition="contains">HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run</TargetObject>
>     </RegistryEvent>
> 
>   </EventFiltering>
> </Sysmon>
> ```

- Apply a configuration file to running Sysmon:

```powershell
sysmon.exe -c filename.xml
```

- Check current configuration:

```powershell
sysmon.exe -c
```

>[!example]+
> ```powershell
> sysmon.exe -c sysmononfig-export.xml
> ```
> 
>![[start_sysmon.png]]

### Example 1: Detecting DLL injection

>[!bug]+ The DLL hijacking attack
> When a program needs a DLL, Windows searches for it in a predefined list of locations, in order (simplified):
> 1. Application directory (where the program itself is located, e.g., `C:\Users\Desktop`).
> 2. `C:\Windows\System32` (contains essential system files, DLLs, and executables required for the OS to function).
> 3. `C:\Windows` (Windows directory).
> 4. Current directory (the one from where the program was launched, usually the application directory).
> 5. Directories listed in `PATH`.
>
>If an attacker places a malicious DLL in a directory that's searched before the legitimate one, the application loads the malicious version instead. This is known as **DLL hijacking** or **DLL side-loading**.

- To detect DLL hijacking, you would monitor for **Sysmon events with Event ID `7`** — `ImageLoad` that logs **every DLL loaded by processes**.

For demonstration, we will reproduce a simple DLL hijacking attack using examples from the [`stephenfewer's ReflectiveDLLInjection repository`](https://github.com/stephenfewer/ReflectiveDLLInjection) ([`ReflectiveDLLInjection/bin` directory](https://github.com/stephenfewer/ReflectiveDLLInjection/tree/master/bin)) and then watch what Sysmon says.

To start monitoring for Sysmon Event ID `7`:

1. Enable logging of Sysmon **Event ID `7` (`ImageLoad`)** by changing `<ImageLoad onmatch="include">`  in the configuration to `<ImageLoad onmatch="include">`. 

>[!example]+
> Here is the configuration using `sysmonconfig-export.xml` from [`SwiftOnSecurity/sysmon-config`](https://github.com/SwiftOnSecurity/sysmon-config):
> 
> ```xml
> <!--SYSMON EVENT ID 7 : DLL (IMAGE) LOADED BY PROCESS [ImageLoad]-->
> 		<!--COMMENT:	Can cause high system load, disabled by default.-->
> 		<!--COMMENT:	[ https://attack.mitre.org/wiki/Technique/T1073 ] [ https://attack.mitre.org/wiki/Technique/T1038 ] [ https://attack.mitre.org/wiki/Technique/T1034 ] -->
> 
> 		<!--DATA: UtcTime, ProcessGuid, ProcessId, Image, ImageLoaded, Hashes, Signed, Signature, SignatureStatus-->
> 	<RuleGroup name="" groupRelation="or">
> 		<ImageLoad onmatch="exclude">
> 			<!--NOTE: Using "include" with no rules means nothing in this section will be logged-->
> 		</ImageLoad>
> 	</RuleGroup>
> ```
> 

2. Apply the modified Sysmon configuration:

```bash
sysmon.exe -c sysmonconfig-export.xml
```

Now **Event ID 7 will appear in Event Viewer**.

![[start_sysmon.png]]

To reproduce the attack:

1. Copy the target executable (in this case, `calc.exe`) and the malicious DLL (this one is actually harmless) to the directory of your control (in this case, Administrator's `Desktop` folder):

```powershell
copy C:\Windows\System32\calc.exe C:\Users\Administrator\Desktop
```

```powershell
copy "C:\Tools\Reflective DLLInjection\reflective_dll.x64.dll" .
```

2. Rename the DLL file so it matches one of the DLLs `calc.exe` loads:

```powershell
move reflective_dll.x64.dll WININET.dll
```

3. Start the program:

```powershell
.\calc.exe
```

![[replicating_reflective_DLL_injection.png]]

- Instead of the Calculator application, a [`MessageBox`](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-messageboxa) is displayed — this is because `calc.exe` loaded your malicious DLL (that pops up that messages box) instead of the legitimate `C:\Windows\System32\WININET.dll`.

- Now you can use `Get-WinEvent` to query for Sysmon-generated events with `Event ID 7`:

```powershell
Get-WinEvent -FilterHashtable @{
	LogName='Microsoft-Windows-Sysmon/Operational'; 
	ID=7
} | Where-Object { $_.Message -match 'Signed: false' }
```

- Or you can find it in Event Viewer (filter to events with Event ID 7 and search for the event in the log):

![[sysmon_7.png]]

![[event_7_sysmon.png]]

![[calc.exe_loaded_dll.png]]

- Key IOCs (Indicators of Compromise):
	1. `calc.exe`, that should reside in `System32` or `Syswow64`, runs from a writable directory. It should not be found in a writable directory.
	2. `WININET.dll` is loaded from a path other than the original `System32`.
	3. The original `WININET.dll` is Microsoft-signed, but the injected DLL is not signed (`Signed: false`).

- For comparison, here is a normal DLL loading event:

![[normal_dll_loading.png]]

### Example 2: Detecting credential dumping via LSASS

>[!bug]+ LSASS memory dumping
> [Mimikatz](https://github.com/gentilkiwi/mimikatz) and similar tools can access LSASS memory and dump credentials from there. The `sekurlsa::logonpasswords` module, for example, dumps user account password hashes or (occasionally) plaintext passwords from LSASS memory (this can only be done as `SYSTEM` or local admin with `SeDebugPrivilege`).
> 
>>[!note] To learn more about credential dumping from LSASS memory, check out my article: [[LSASS memory]].

- LSASS credential dumping attacks can be detected by monitoring for **Sysmon Event ID `10`** — `ProcessAccess` that logs every occasion when a process opens another process's memory.

To start monitoring for Sysmon Event ID `10`:

1. Enable logging of Sysmon **Event ID `10` (`ProcessAccess`)** by changing `<ProcessAccess onmatch="include">`  in the configuration to `<ProcessAccess onmatch="exclude">`. 

>[!example]+
> Here is how it looks like in `sysmonconfig-export.xml` from [`SwiftOnSecurity/sysmon-config`](https://github.com/SwiftOnSecurity/sysmon-config):
> ```xml
> <!--SYSMON EVENT ID 10 : INTER-PROCESS ACCESS [ProcessAccess]-->
> 	<!--EVENT 10: "Process accessed"-->
> 	<!--COMMENT:	Can cause high system load, disabled by default.-->
> 	<!--COMMENT:	Monitor for processes accessing other process' memory.-->
> 
> 	<!--DATA: UtcTime, SourceProcessGuid, SourceProcessId, SourceThreadId, SourceImage, TargetProcessGuid, TargetProcessId, TargetImage, GrantedAccess, CallTrace-->
> <RuleGroup name="" groupRelation="or">
> 	<ProcessAccess onmatch="exclude">
> 		<!--NOTE: Using "include" with no rules means nothing in this section will be logged-->
> 	</ProcessAccess>
> </RuleGroup>
> ```
> 

2. Apply the modified Sysmon configuration:

```bash
sysmon.exe -c sysmonconfig-export.xml
```

![[start_sysmon.png]]

To reproduce the attack:

1. From a `SYSTEM` shell, run `Mimikatz`'s `privilege::debug` to acquire `SeDebugPrivilege`, and then `sekurlsa::logonpasswords` to dump LSASS memory:

```powershell
mimikatz.exe
```

```powershell
privilege::debug
```

```powershell
sekurlsa::logonpasswords
```

To detect the event, use `Get-WinEvent` (search for events where `TargetImage` is `lsass.exe`):

```powershell
Get-WinEvent -MaxEvents 50 -FilterHashtable @{
    LogName='Microsoft-Windows-Sysmon/Operational',
    ID = 10
} | Where-Object {  
$_.Properties[5].Value -like "*lsass.exe*"  
}
```

Or filter Sysmon's logs to `Event ID 10` in Event Viewer:

![Sysmon Event 10: Process accessed, SourceImage AgentEXE.exe, TargetImage lsass.exe, SourceUser DESKTOP-R4PEEIF\waldo, TargetUser NT AUTHORITY\SYSTEM.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/216/image33.png)

### Example 3: Detecting unmanaged PowerShell/C-Sharp injection

>[!interesting]+ C# is a managed language
>- C# is considered a **managed language**, which means its code is executed under the control of a runtime environment.
>- Code written in C# is executed under the supervision of the **[Common Language Runtime (CLR)](https://learn.microsoft.com/en-us/dotnet/standard/clr)**, a runtime environment provided by the .NET framework. 
>- CLR handles memory management (e.g., garbage collection), JIT compilation ([CIL](https://en.wikipedia.org/wiki/Common_Intermediate_Language) -> native code), security (verification and sandboxing), exception handling (e.g., runtime error control), and other. 
>- C# code is compiled into **Intermediate Language (IL)**, also known as **Common Intermediate Language (CIL)**, rather than directly into machine code (like C would do, for example). The CLR then uses **Just-In-Time (JIT) compilation** to convert this IL into native machine code at runtime, tailored to the specific hardware and operating system.
>- Developers can still write **unmanaged code** in C#, though. 

>[!note] Another example of a managed language is Java, which the code is executed in a JVM (Java Virtual Machine).

>[!bug]+ Unmanaged PowerShell injection
> - Normally, managed process like `powershell.exe` load .NET-related DLLs like `clr.dll` and `clrjit.dll`. 
> - But it is possible to **inject the CLR into a native (unmanaged) process** (e.g., `spoolsv.exe`, `notepad.exe`, `svchost.exe`), which allows you to **Execute PowerShell code without spawning `powershell.exe`** or **run C# assemblies in memory**. With this, you can **bypass logging, AppLocker, and EDRs** — malicious PowerShell scripts run in trusted processes you wouldn't normally suspect.

- Again, DLL loading is logged by **Sysmon Event ID `7` (`ImageLoad`)** — and this is what you would use to detect unmanaged PowerShell injection.
- To reproduce the attack, we will use [`PSInject`](https://github.com/EmpireProject/PSInject) by [`ExpireProject`](https://github.com/EmpireProject).

To start monitoring for Sysmon Event ID `7`:

1. Enable logging of Sysmon **Event ID `7` (`ImageLoad`)** by changing `<ImageLoad onmatch="include">`  in the configuration to `<ImageLoad onmatch="include">`. 

>[!example]+
> Here is the configuration using `sysmonconfig-export.xml` from [`SwiftOnSecurity/sysmon-config`](https://github.com/SwiftOnSecurity/sysmon-config):
> 
> ```xml
> <!--SYSMON EVENT ID 7 : DLL (IMAGE) LOADED BY PROCESS [ImageLoad]-->
> 		<!--COMMENT:	Can cause high system load, disabled by default.-->
> 		<!--COMMENT:	[ https://attack.mitre.org/wiki/Technique/T1073 ] [ https://attack.mitre.org/wiki/Technique/T1038 ] [ https://attack.mitre.org/wiki/Technique/T1034 ] -->
> 
> 		<!--DATA: UtcTime, ProcessGuid, ProcessId, Image, ImageLoaded, Hashes, Signed, Signature, SignatureStatus-->
> 	<RuleGroup name="" groupRelation="or">
> 		<ImageLoad onmatch="exclude">
> 			<!--NOTE: Using "include" with no rules means nothing in this section will be logged-->
> 		</ImageLoad>
> 	</RuleGroup>
> ```
> 

2. Apply the modified Sysmon configuration:

```bash
sysmon.exe -c sysmonconfig-export.xml
```

To reproduce the attack:

1. Get the PID of a legitimate process like `spoolsv.exe`:

```powershell
Get-Process spoolsv
```

2. Launch PowerShell with relaxed execution policy:

```powershell
powershell -ep bypass
```

3. Import `PSInject` module:

```powershell
cd C:\Tools\PSInject
```

```powershell
Import-Module .\Invoke-PSInject.ps1
```

- Perform the injection:

```powershell
Invoke-PSInject -ProcId <PID> -PoshCode "V3JpdGUtSG9zdCAiSGVsbG8gZnJvbSAweHRyMWdnZXIgOiki"
```

>[!note]+ Command breakdown
>- **`-ProcId`**: Specifies the process ID of the target process. 
>- **`-PoshCode`**: A **Base64-encoded PowerShell script block** to execute in the target process.

>[!example]+
>![[unmanaged_powershell_injection_psinject.png]]

- CLR was injected into `spoolsv.exe`, and PowerShell executed **inside that process memory**.

To detect the injection with `Get-WinEvent`:

```powershell
Get-WinEvent -FilterHashtable @{
    LogName='Microsoft-Windows-Sysmon/Operational'
    ID=7
} | Where-Object {
    $_.Message -match "clr.dll" -or $_.Message -match "clrjit.dll"
} | fl *
```

![[spoolsv_logged.png]]

- You can also see this in [Process Hacker](https://processhacker.sourceforge.io/):

![[spoolsv_managed.png]]

- `spoolsv.exe` becomes a managed process. 

- Key IOCs (Indicators of Compromise):
	1. `spoolsv.exe` loads `clr.dll` or `clrjit.dll` — which it normally doesn't.
	2. Process suddenly becomes `.NET` — but there's no `powershell.exe`.

## Tapping into ETW

- Sysmon is built on **Event Tracing for Windows (ETW)**, but it only exposes a curated subset of what the Windows logging framework can provide. For scenarios where Sysmon's telemetry fails short — such as PPID spoofing detection and in-memory .NET execution —you need to tap ETW providers directly.

>[!note]+ Many modern EDRs and tools like Sysmon rely on ETW to collect telemetry.

>[!note]+ Key difference from Sysmon
>- Sysmon is a driver that logs to the Windows Event Log. 
>- ETW is the underlying framework that Sysmon uses. You can tap ETW directly in real time to detect events that Sysmon might miss.

>[!note] To learn more about ETW and how it works, see [[Windows Logging Infrastructure_#Event Tracing for Windows (ETW)]].

### Interacting with ETW

#### Logman — managing ETW sessions 

[`logman.exe`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/logman) is the built-in command-line tool for ETW session management. It comes preinstalled on very Windows system.

- List all active ETW sessions:

```powershell
logman query -ets
```

- List all available providers on the system:

```powershell
logman query providers
```

- **On Windows 10/11, you'll see 1000+ providers.** Filter by keyword:

```powershell
logman query providers | findstr "PowerShell"
```

- Inspect a specific active session (shows subscribed providers, keywords, log level):

```powershell
logman.exe query "EventLog-System" -ets
```

```powershell
logman query "EventLog-Security" -ets
```

#### SilkETW — capturing ETW events

[`SilkETW`](https://github.com/mandiant/SilkETW) by [`Mandiant`](https://github.com/mandiant) wraps the ETW API and lets you capture events from any provider with minimal setup. This is the go-to tool for custom ETW investigation.
### ETW Example 1: Detecting strange parent-child relationships

- Every process in Windows is created by another process (its **parent**). Certain process relationships are normal in Windows. But some combinations are red flags that may indicate code execution.
- For example, `calc.exe` spawning `cmd.exe` is really not something you would see during normal system operation.
- Examples of suspicious parent-child pairs:

| Parent                       | Child                        | Why Suspicious                                         |
| ---------------------------- | ---------------------------- | ------------------------------------------------------ |
| `winword.exe`                | `cmd.exe` / `powershell.exe` | Macro execution — classic phishing payload             |
| `excel.exe`                  | `wscript.exe` / `mshta.exe`  | Macro-driven LOLBin abuse                              |
| `outlook.exe`                | `powershell.exe`             | Email-borne payload                                    |
| `calc.exe`                   | `cmd.exe`                    | Should never happen — indicates hollowing or hijacking |
| `svchost.exe` (wrong parent) | Any                          | PPID spoofing                                          |
| `explorer.exe`               | `mimikatz.exe`               | Direct tool execution                                  |

- Sysmon Event ID `1` (`ProcessCreate`) logs all process creation events and provides detailed information about newly created processes, including the parent PID.

>[!tip]+
>  Samir Bousseaden has shared an insightful mind map introducing common parent-child relationships, which can be referenced [here](https://twitter.com/SBousseaden/status/1195373669930983424).
> 
> ![[parent-child_processes_Windows.jpeg]]

- However, if an attacker tries to **fake the parent process**, such as using **Parent PID Spoofing** —  **[`MITRE ATT&CK technique T1134.004`](https://attack.mitre.org/techniques/T1134/004/)** — Sysmon won't show it.

>[!bug] **Parent PID Spoofing** allows an attacker to create a process while **pretending it was launched by another process**.
>- One way of explicitly assigning the PPID of a new process is via the `CreateProcess` API call, which supports a parameter that defines the PPID to use.

- To obtain deeper visibility, you should use **ETW** — the `Microsoft-Windows-Kernel-Process` provider that shows **real process parent rather than the declared one**.

- Capture kernel process events with `SilkETW`:

```powershell
cd C:\Tools\SilkETW_SilkService_v8\v8\SilkETW
```

```powershell
.\SilkETW.exe -t user -pn Microsoft-Windows-Kernel-Process -ot file -p C:\windows\temp\etw.json
```

- `-t user`: User-mode ETW session.
- `-pn Microsoft-Windows-Kernel-Process`: Provider name.
- `-ot file`: Output to file.
- `-p`: File path.
### ETW Example 2: Detecting malicious .NET assembly loading

- Instead of abusing built-in tools (*Living-Off-the-Land*), attackers now often **create their own custom tools in .NET** (*Bring-Your-Own-Land*) that are made completely independent on any tools present on the target and execute entirely in memory.

>[!note] Windows comes with .NET preinstalled. 

- Modern post-exploitation frameworks like Cobalt Strike, Covenant, and Donut, load .NET assemblies entirely in memory using functions like `Assembly.Load(byte[])`, which bypasses disk-based detection. 
- One of such tools is [Seatbelt](https://github.com/GhostPack/Seatbelt) a well-known .NET assembly used for [[Windows credential hunting _]].

>[!example]+
> ```powershell
> .\Seatbelt.exe TokenPrivileges
> ```
> 
> ```powershell
> 
>                         %&&@@@&&
>                         &&&&&&&%%%,                       #&&@@@@@@%%%%%%###############%
>                         &%&   %&%%                        &////(((&%%%%%#%################//((((###%%%%%%%%%%%%%%%
> %%%%%%%%%%%######%%%#%%####%  &%%**#                      @////(((&%%%%%%######################(((((((((((((((((((
> #%#%%%%%%%#######%#%%#######  %&%,,,,,,,,,,,,,,,,         @////(((&%%%%%#%#####################(((((((((((((((((((
> #%#%%%%%%#####%%#%#%%#######  %%%,,,,,,  ,,.   ,,         @////(((&%%%%%%%######################(#(((#(#((((((((((
> #####%%%####################  &%%......  ...   ..         @////(((&%%%%%%%###############%######((#(#(####((((((((
> #######%##########%#########  %%%......  ...   ..         @////(((&%%%%%#########################(#(#######((#####
> ###%##%%####################  &%%...............          @////(((&%%%%%%%%##############%#######(#########((#####
> #####%######################  %%%..                       @////(((&%%%%%%%################
>                         &%&   %%%%%      Seatbelt         %////(((&%%%%%%%%#############*
>                         &%%&&&%%%%%        v1.2.1         ,(((&%%%%%%%%%%%%%%%%%,
>                          #%%%%##,
> 
> 
> ====== TokenPrivileges ======
> 
> Current Token's Privileges
> 
>                      SeIncreaseQuotaPrivilege:  DISABLED
>                           SeSecurityPrivilege:  DISABLED
>                      SeTakeOwnershipPrivilege:  DISABLED
>                         SeLoadDriverPrivilege:  DISABLED
>                      SeSystemProfilePrivilege:  DISABLED
>                         SeSystemtimePrivilege:  DISABLED
>               SeProfileSingleProcessPrivilege:  DISABLED
>               SeIncreaseBasePriorityPrivilege:  DISABLED
>                     SeCreatePagefilePrivilege:  DISABLED
>                             SeBackupPrivilege:  DISABLED
>                            SeRestorePrivilege:  DISABLED
>                           SeShutdownPrivilege:  DISABLED
>                              SeDebugPrivilege:  SE_PRIVILEGE_ENABLED
>                  SeSystemEnvironmentPrivilege:  DISABLED
>                       SeChangeNotifyPrivilege:  SE_PRIVILEGE_ENABLED_BY_DEFAULT, SE_PRIVILEGE_ENABLED
>                     SeRemoteShutdownPrivilege:  DISABLED
>                             SeUndockPrivilege:  DISABLED
>                       SeManageVolumePrivilege:  DISABLED
>                        SeImpersonatePrivilege:  SE_PRIVILEGE_ENABLED_BY_DEFAULT, SE_PRIVILEGE_ENABLED
>                       SeCreateGlobalPrivilege:  SE_PRIVILEGE_ENABLED_BY_DEFAULT, SE_PRIVILEGE_ENABLED
>                 SeIncreaseWorkingSetPrivilege:  DISABLED
>                           SeTimeZonePrivilege:  DISABLED
>                 SeCreateSymbolicLinkPrivilege:  DISABLED
>     SeDelegateSessionUserImpersonatePrivilege:  DISABLED
> 
> ```

- Sure, Sysmon Event ID `7` will catch CLR DLLs loading, but it can be challenging to work with due to how much noise it generates. It also won't show you what assembly content is actually executing. 
- The `Microsoft-Windows-DotNETRuntime` ETW provider can provide deeper insights into the actual assembly being loaded. 

1. Open the first terminal window and start capturing ETW .NET Runtime Events using [`SilkETW`](https://github.com/mandiant/SilkETW):
`
```powershell
cd C:\Tools\SilkETW_SilkService_v8\v8\SilkETW
```

```powershell
.\SilkETW.exe -t user -pn Microsoft-Windows-DotNETRuntime -uk 0x2038 -ot file -p C:\Windows\Temp\etw.json
```

This starts collecting **CLR runtime telemetry** from the `Microsoft-Windows-DotNETRuntime` provider. Leave this window running.

>[!note]+ Command breakdown
>- `-t user`: Capture user-mode events.
>- `-pn Microsoft-Windows-DotNETRuntime`: Subscribe to .NET Runtime provider.
>- `-uk 0x2038`: Enable JIT + `Interop` + `Loader` + `NGen` keywords.
>- `-ot flie`: Write output to file.
>- `-p C:\Windows\Temp\etw.json`: Output path.

![[silketw.png]]

2. Open another terminal window with PowerShell, and start Seatbelt:

```powershell
cd "C:\Tools\GhostPack Compiled Binaries"
```

```powershell
.\Seatbelt.exe TokenPrivileges
```

This triggers CLR initialization, JIT compilation, and Interop API calls, which generates ETW telemetry captured by `SilkETW`. Wait until Seatbelt finishes printing results.

![[seatbelt.png]]

3. Return to terminal 1 (`SilkETW`) and terminate the process:

```powershell
Ctrl + C
```

This stops the trace and saves the output file `C:\Windows\Temp\etw.json`.

4. Open the file (e.g., `notepad C:\Windows\Temp\etw.json`) and search for `ManagedInteropMethodName` (`Ctrl + F` in Notepad). You should find entries like:

```powershell
"ManagedInteropMethodName":"GetTokenInformation"
```

![[notepad_find.png]]

- Or use `Select-String` instead of searching manually: 

```powershell
Select-String -Path C:\Windows\Temp\etw.json -Pattern ManagedInteropMethodName
```

You will see entries like `GetTokenInformation`, `OpenProcess`, `LookupPrivilegeValue` — the exact Windows API calls the assembly is making. This technique works because the CLR must JIT-compile real native calls regardless of any source-level obfuscation.

In the `SilkETW` command, we selectively target a subset of events, indicated by `0x2038`. This includes:

| Keyword          | Value    | What It Captures                                                                           |
| ---------------- | -------- | ------------------------------------------------------------------------------------------ |
| `LoaderKeyword`  | `0x8`    | Assembly and module load events — what .NET code is being loaded into the process.         |
| `JitKeyword`     | `0x10`   | Just-in-time  (JIT) compilation — which managed methods are being compiled to native code. |
| `NGenKeyword`    | `0x20`   | Native Image Generator (`NGen`) events — precompiled assembly usage.                       |
| `InteropKeyword` | `0x2000` | Managed-to-unmanaged interoperability events — which Win32 APIs managed code is calling.   |

## References and further reading

- [`Sysmon — Microsoft Learn`](https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon).
- [`Sysmon documentation — Microsoft Learn`](https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon)
-  [`sysmon-config — SwiftOnSecurity, GitHub`](https://github.com/SwiftOnSecurity/sysmon-config)
- [`Hijacking DLLs in Windows — witzebeukema.nl`](https://www.wietzebeukema.nl/blog/hijacking-dlls-in-windows) — very good guide to DLL hijacking attacks
- [`ReflectiveDLLInjection/bin — stephenfewer`](https://github.com/stephenfewer/ReflectiveDLLInjection/tree/master/bin)
- [`Advanced XML filtering in the Windows Event Viewer — NedPyle, techcommunity.microsoft.com`](https://techcommunity.microsoft.com/blog/askds/advanced-xml-filtering-in-the-windows-event-viewer/399761)
- [`Event Types — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/eventlog/event-types)
- [`Defining Channels — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/wes/defining-channels)
- [`Providing Events — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/etw/providing-events)

- [`Important Windows Event IDs For SIEM Monitoring — Valency Networks`](https://www.valencynetworks.com/blogs/important-windows-event-ids-for-siem-monitoring/)

- [`Common Language Runtime (CLR) overview — Microsoft Learn`](https://learn.microsoft.com/en-us/dotnet/standard/clr)
- [`What is "managed code"? — Microsoft Learn`](https://learn.microsoft.com/en-us/dotnet/standard/managed-code)
- [`Process Hacker — SourceForge`](https://processhacker.sourceforge.io/)
- [`Unmanaged PowerShell - PowerShell without powershell.exe — Cobalt Strike Archive, YouTube`](https://www.youtube.com/watch?v=7tvfb9poTKg)
- [`UnmanagedPowerShell — leechristensen, GitHub`](https://github.com/leechristensen/UnmanagedPowerShell)
-  [`PSInject — EmpireProject, GitHub`](https://github.com/EmpireProject/PSInject)
- [`Event Tracing for Windows — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-hardware/test/wpt/event-tracing-for-windows)

- [`Windows Event Logs — SOC LEVEL 1`](https://jacob-taylor.gitbook.io/security-analyst/path-4/endpoint-security-monitoring/windows-event-logs)
- [`IR Event Log Cheatsheet — s0cm0nkey's Security Reference Guide`](https://s0cm0nkey.gitbook.io/s0cm0nkeys-security-reference-guide/dfir-digital-forensics-and-incident-response/ir-event-log-cheatsheet#security-log-information)
- [`Windows Loggin Basics — SolarWinds`](https://www.loggly.com/ultimate-guide/windows-logging-basics/)
- [`Hiding in Plain Sight: Monitoring and Testing for Living-Off-the-Land Binaries — Federico Quattrin, Nick Desler, Tin Tam, and Matthew Rutkoske — attackiq`](https://www.attackiq.com/2023/03/16/hiding-in-plain-sight/)
- [`Bring Your Own Land (BYOL) — A Novel Red Teaming Technique — Nathan Kirk, Google Cloud`](https://cloud.google.com/blog/topics/threat-intelligence/bring-your-own-land-novel-red-teaming-technique/)
- [`Cobalt Strike 3.11 – The snake that eats its tail — Cobalt Strike`](https://www.cobaltstrike.com/blog/cobalt-strike-3-11-the-snake-that-eats-its-tail)
- [`Detecting .NET/C# injection (Execute-Assembly) — redhead0ntherun, Medium`](https://redhead0ntherun.medium.com/detecting-net-c-injection-execute-assembly-1894dbb04ff7)
- [`Threat Hunting with ETW events and HELK — Part 1: Installing SilkETW — Roberto Rodriguez, Medium`](https://medium.com/threat-hunters-forge/threat-hunting-with-etw-events-and-helk-part-1-installing-silketw-6eb74815e4a0)


## Appendix A: Common event log files

### Core log files

| Path<br>`C:\Windows\System32\winevt\Logs\` | Description                                                                                                                                                                                                                         |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Application.evtx`                         | **Application log** — Events logged by installed applications and services, including application crashes, service errors, application-specific warnings, and runtime failures.                                                     |
| `Security.evtx`                            | **Security log** — Audit events governed by the system audit policy (e.g., logon/logoff, authentication success/failure, privilege use/change, account lockouts).<br>Used for detecting unauthorized access and malicious activity. |
| `System.evtx`                              | **System log** — Events from Windows system components (kernel, drivers, services). Useful for OS troubleshooting (e.g., service start/stop, driver load errors, hardware issues).                                                  |
| `Setup.evtx`                               | **Setup log** — Events related to OS installations, feature upgrades, role additions, and software setups. Important for correlating configuration changes or installation issues.                                                  |
| `ForwardedEvents.evtx`                     | **Forwarded Events** — used in enterprise logging to collect and store event logs sent from remote machines (Windows Event Forwarding, WE). <br>Not enabled by default on standalone client systems.                                |

- Authentication and account activity:

| **File**                                                                   | **Description and Purpose**                                                                                                                                                                |
| -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `Microsoft-Windows-TerminalServices-LocalSessionManager%4Operational.evtx` | Tracks **RDP/logon sessions** (success, disconnects, reconnects).                                                                                                                          |
| `Microsoft-Windows-Security-Auditing%4Operational.evtx` (if present)       | Operational channel variant of security auditing (similar content as `Security.evtx` but scoped to specific providers). These logs may present finer granularity for certain audit events. |

- System components and hardware:

| **File**                                          | **Description and Purpose**                                                              |
| ------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `Microsoft-Windows-Dhcp-Client%4Operational.evtx` | DHCP client events (lease renewals, failures).                                           |
| `Microsoft-Windows-Dns-Client%4Operational.evtx`  | DNS client resolution events.                                                            |
| `Microsoft-Windows-TermService%4Operational.evtx` | Terminal Services/Remote Desktop Services connection events. Important for RDP tracking. |

- Update and deployment:

| **File**                                                   | **Description and Purpose**                                                             |
| ---------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| `Microsoft-Windows-WindowsUpdateClient%4Operational.evtx`  | Windows Update client activity (scan/installation statuses).                            |
| `Microsoft-Windows-AppXDeploymentServer%4Operational.evtx` | AppX (modern UWP app) deployment logs — shows install/remove operations for Store apps. |

| File                                                                                                           | Description                                                                                                                                                       |
| -------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `C:\Windows\System32\winevt\Logs\ForwardedEvents.evtx`                                                         | Stores logs forwarded from remote systems via Windows Event Forwarding (WEF). Often used in centralized logging environments.                                     |
| `C:\Windows\System32\winevt\Logs\Microsoft-Windows-Sysmon%4Operational.evtx`                                   | Detailed system activity if Sysmon is installed: process creation, network connections, registry changes, file creation, etc. Highly valuable for threat hunting. |
| `C:\Windows\System32\winevt\Logs\Microsoft-Windows-PowerShell%4Operational.evtx`                               | PowerShell execution events including module logging, pipeline execution, and script block logging. Useful for detecting malicious PowerShell usage.              |
| `C:\Windows\System32\winevt\Logs\Windows PowerShell.evtx`                                                      | Legacy PowerShell engine log showing PowerShell host start/stop and command activity.                                                                             |
| `C:\Windows\System32\winevt\Logs\Microsoft-Windows-WMI-Activity%4Operational.evtx`                             | Logs WMI queries and execution. Important for detecting lateral movement or persistence using WMI.                                                                |
| `C:\Windows\System32\winevt\Logs\Microsoft-Windows-TaskScheduler%4Operational.evtx`                            | Logs scheduled task creation, modification, and execution. Frequently used for persistence by attackers.                                                          |
| `C:\Windows\System32\winevt\Logs\Microsoft-Windows-Windows Defender%4Operational.evtx`                         | Microsoft Defender events including detections, scans, exclusions, and tampering attempts.                                                                        |
| `C:\Windows\System32\winevt\Logs\Microsoft-Windows-Windows Firewall With Advanced Security%4Firewall.evtx`     | Firewall rule changes, filtering events, and configuration modifications. Useful for identifying unauthorized rule creation.                                      |
| `C:\Windows\System32\winevt\Logs\Microsoft-Windows-TerminalServices-RemoteConnectionManager%4Operational.evtx` | Logs RDP connection attempts and session management events. Useful for detecting lateral movement via RDP.                                                        |
| `C:\Windows\System32\winevt\Logs\Microsoft-Windows-RemoteDesktopServices-RdpCoreTS%4Operational.evtx`          | Lower-level RDP connection and transport events useful for forensic analysis of remote desktop activity.                                                          |
| `C:\Windows\System32\winevt\Logs\Microsoft-Windows-SMBServer%4Security.evtx`                                   | Logs SMB server authentication and file access events; useful for tracking lateral movement and file share access.                                                |
| `C:\Windows\System32\winevt\Logs\Microsoft-Windows-SmbClient%4Security.evtx`                                   | Logs SMB client-side connection and authentication activity to remote shares.                                                                                     |
| `C:\Windows\System32\winevt\Logs\Microsoft-Windows-WinRM%4Operational.evtx`                                    | Logs Windows Remote Management activity.                                                                                                                          |
| `C:\Windows\System32\winevt\Logs\Microsoft-Windows-Winlogon%4Operational.evtx`                                 | Winlogon-related events including session initialization and authentication processes.                                                                            |
| `C:\Windows\System32\winevt\Logs\Microsoft-Windows-Bits-Client%4Operational.evtx`                              | Logs Background Intelligent Transfer Service activity.                                                                                                            |

## Appendix B: Event record IDs
### Authentication & logon events

- These events track **authentication activity**, including successful and failed logons, use of credentials, and session lifecycle events. 

| Event ID                                                                                           | Short description               | Description                                                                                                    |
| -------------------------------------------------------------------------------------------------- | ------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| [`4624`](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4624) | Successful logon                | Generated when **a logon session is successfully created** on the target system.                               |
| [`4625`](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4625) | Failed logon                    | Generated when **an authentication attempt fails**.                                                            |
| [`4634`](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4634) | Logoff                          | Generated when **a logon session is terminated** and the user logs off.                                        |
| [`4647`](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4647) | User initiated logoff           | Generated when **a user explicitly initiates a logoff** using the logoff mechanism.                            |
| [`4648`](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4648) | Logon with explicit credentials | Generated when **a process attempts logon using explicit credentials** (e.g., `runas`, alternate credentials). |
| [`4672`](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4672) | Special privileges assigned     | Generated when a logon session **receives administrative privileges** such as `SeDebugPrivilege`.              |
| [`4778`](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4778) | RDP session reconnected         | Generated when **a disconnected Remote Desktop session (RDP) is reconnected**.                                 |
| [`4779`](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4779) | RDP session disconnected        | Generated when **a Remote Desktop session is disconnected** from the system.                                   |

- Logon types:

| Type | Name              | Context                                                        |
| ---- | ----------------- | -------------------------------------------------------------- |
| `2`  | Interactive       | Local console logon.                                           |
| `3`  | Network           | Net use, WMI, SMB access, remote registry.                     |
| `4`  | Batch             | Scheduled tasks.                                               |
| `5`  | Service           | Service account startup.                                       |
| `7`  | Unlock            | Screen unlock.                                                 |
| `8`  | NetworkCleartext  | Plaintext credentials over network (IIS basic auth, old SMTP). |
| `9`  | NewCredentials    | RunAs with `/netonly`. Credentials for network use only.       |
| `10` | RemoteInteractive | RDP session.                                                   |
| `11` | CachedInteractive | Logon using cached domain credentials (no DC contact).         |



- Common sub-status codes for failed logons (`4625`):

| SubStatus    | Meaning                         |
| ------------ | ------------------------------- |
| `0xC0000064` | Username does not exist.        |
| `0xC000006A` | Wrong password, valid username. |
| `0xC0000234` | Account locked out.             |
| `0xC0000072` | Account disabled.               |
| `0xC000006F` | Outside allowed logon hours.    |
| `0xC0000193` | Account expired.                |
| `0xC0000070` | Workstation restriction.        |

### Kerberos authentication events (Domain Controllers)

| Event ID                                                                                           | Short description                   | Description                                                                                      |
| -------------------------------------------------------------------------------------------------- | ----------------------------------- | ------------------------------------------------------------------------------------------------ |
| [`4768`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4768) | Kerberos TGT requested              | Generated when a TGT (Ticket-Granting Ticket) is requested from a domain controller.             |
| [`4769`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4769) | Kerberos service ticket requested   | Generated when an ST (Service Ticket) is requested for access to a specific service.             |
| [`4770`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4770) | Kerberos service ticket renewed     | Generated when an existing ST is renewed.                                                        |
| [`4771`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4771) | Kerberos pre-authentication failure | Generated when Kerberos pre-authentication fails during ticket request processing.               |
| [`4776`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4776) | NTLM authentication validation      | Generated when a domain controller validates credentials using the NTLM authentication protocol. |

### Account management events

| Event ID                                                                                           | Short description       | Description                                                                      |
| -------------------------------------------------------------------------------------------------- | ----------------------- | -------------------------------------------------------------------------------- |
| [`4720`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4720) | User account created    | Generated when a new user account object is created.                             |
| [`4722`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4722) | User account enabled    | Generated when a previously disabled user account is enabled.                    |
| [`4723`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4723) | Password change attempt | Generated when a user attempts to change their account password.                 |
| [`4724`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4724) | Password reset attempt  | Generated when an attempt is made to reset another account's password.           |
| [`4725`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4725) | User account disabled   | Generated when a user account is disabled.                                       |
| [`4726`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4726) | User account deleted    | Generated when a user account object is deleted.                                 |
| [`4738`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4738) | User account changed    | Generated when properties of a user account are modified.                        |
| [`4740`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4740) | Account locked out      | Generated when an account is locked due to configured lockout policy thresholds. |

### Group membership changes


| Event ID                                                                                           | Short description            | Description                                                         |
| -------------------------------------------------------------------------------------------------- | ---------------------------- | ------------------------------------------------------------------- |
| [`4728`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4728) | Added to global group        | Generated when a member is added to a global security group.        |
| [`4729`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4729) | Removed from global group    | Generated when a member is removed from a global security group.    |
| [`4732`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4732) | Added to local group         | Generated when a member is added to a local security group.         |
| [`4733`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4733) | Removed from local group     | Generated when a member is removed from a local security group.     |
| [`4756`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4756) | Added to universal group     | Generated when a member is added to a universal security group.     |
| [`4757`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4757) | Removed from universal group | Generated when a member is removed from a universal security group. |

### Process execution events


| Event ID                                                                                           | Short description   | Description                                            |
| -------------------------------------------------------------------------------------------------- | ------------------- | ------------------------------------------------------ |
| [`4688`](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4688) | Process creation    | Generated when a new process is created on the system. |
| [`4689`](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4689) | Process termination | Generated when a process exits or is terminated.       |

### Object access events

| Event ID                                                                                           | Short description          | Description                                                                             |
| -------------------------------------------------------------------------------------------------- | -------------------------- | --------------------------------------------------------------------------------------- |
| [`4656`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4656) | Handle requested to object | Generated when a process requests a handle to an object such as a file or registry key. |
| [`4663`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4663) | Object access attempt      | Generated when an operation is performed on an object for which auditing is enabled.    |
| [`4657`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4657) | Registry value modified    | Generated when a registry value is modified and auditing is configured.                 |

### System integrity & audit policy events

| Event ID                                                                                           | Short description              | Description                                                   |
| -------------------------------------------------------------------------------------------------- | ------------------------------ | ------------------------------------------------------------- |
| [`1100`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=1100) | Event logging service shutdown | Generated when the Windows Event Log service is shut down.    |
| [`1102`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=1102) | Security log cleared           | Generated when the Windows Security Event Log is cleared.     |
| [`4719`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4719) | Audit policy changed           | Generated when system audit policy configuration is modified. |

### Scheduled tasks & services

| Event ID                                                                                           | Short description          | Description                                                          |
| -------------------------------------------------------------------------------------------------- | -------------------------- | -------------------------------------------------------------------- |
| [`4697`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4697) | Service installed          | Generated when a new service is installed on the system.             |
| [`4698`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4698) | Scheduled task created     | Generated when a new scheduled task is created.                      |
| [`4700`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4700) | Scheduled task enabled     | Generated when a scheduled task is enabled.                          |
| [`4701`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4701) | Scheduled task disabled    | Generated when an existing scheduled task is disabled.               |
| [`4702`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4702) | Scheduled task updated     | Generated when an existing scheduled task configuration is modified. |
| [`7040`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=7040) | Service start type changed | Generated when the startup type of a service is modified.            |
| [`7045`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=7045) | Service installed          | Generated when a new service is installed on the system.             |
### Network share access

| Event ID                                                                                           | Short description      | Description                                                                        |
| -------------------------------------------------------------------------------------------------- | ---------------------- | ---------------------------------------------------------------------------------- |
| [`5140`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=5140) | Network share accessed | Generated when a network share object is accessed over SMB.                        |
| [`5145`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=5145) | Detailed share access  | Generated when a user attempts access to a specific object within a network share. |

### System startup & shutdown

| Event ID                                                                                                                              | Short description         | Description                                                                        |
| ------------------------------------------------------------------------------------------------------------------------------------- | ------------------------- | ---------------------------------------------------------------------------------- |
| [`1074`](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-1074)                                    | System shutdown initiated | Generated when a process or user initiates a system shutdown or restart operation. |
| [`4608`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4608)                                    | Windows started           | Generated when the Windows operating system starts.                                |
| [`4609`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4609)                                    | Windows shutting down     | Generated when the Windows operating system begins shutdown.                       |
| [`6005`](https://learn.microsoft.com/en-us/troubleshoot/windows-server/performance/troubleshoot-unexpected-reboots-system-event-logs) | Event Log service started | Generated when the Windows Event Log service starts during system boot.            |
| [`6006`](https://learn.microsoft.com/en-us/troubleshoot/windows-server/performance/troubleshoot-unexpected-reboots-system-event-logs) | Event Log service stopped | Generated when the Windows Event Log service stops during system shutdown.         |
| [`6013`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=6013)                                    | System uptime reported    | Generated periodically to record the current system uptime in seconds.             |


### Windows Defender / AV events

| Event ID                                                                                                                       | Short description            | Description                                                                       |
| ------------------------------------------------------------------------------------------------------------------------------ | ---------------------------- | --------------------------------------------------------------------------------- |
| [`1116`](https://learn.microsoft.com/en-us/microsoft-365/security/defender-endpoint/troubleshoot-microsoft-defender-antivirus) | Malware detected             | Generated when Microsoft Defender detects malicious software.                     |
| [`1118`](https://learn.microsoft.com/en-us/microsoft-365/security/defender-endpoint/troubleshoot-microsoft-defender-antivirus) | Remediation started          | Generated when Microsoft Defender begins remediation of detected malware.         |
| [`1119`](https://learn.microsoft.com/en-us/microsoft-365/security/defender-endpoint/troubleshoot-microsoft-defender-antivirus) | Remediation succeeded        | Generated when Microsoft Defender successfully completes malware remediation.     |
| [`1120`](https://learn.microsoft.com/en-us/microsoft-365/security/defender-endpoint/troubleshoot-microsoft-defender-antivirus) | Remediation failed           | Generated when Microsoft Defender remediation of detected malware fails.          |
| [`5001`](https://learn.microsoft.com/en-us/microsoft-365/security/defender-endpoint/troubleshoot-microsoft-defender-antivirus) | Real-time protection changed | Generated when Microsoft Defender real-time protection configuration is modified. |


### Network & firewall events

| Event ID                                                                                           | Short description         | Description                                                                        |
| -------------------------------------------------------------------------------------------------- | ------------------------- | ---------------------------------------------------------------------------------- |
| [`5142`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=5142) | Network share created     | Generated when a new network share is created.                                     |
| [`5157`](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=5157) | Connection blocked by WFP | Generated when the Windows Filtering Platform blocks a network connection attempt. |



