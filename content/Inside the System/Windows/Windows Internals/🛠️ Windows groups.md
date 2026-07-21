---
created: 2026-07-21
tags:
  - Windows
  - Windows_PrivEsc
status: draft
---
## Windows groups

>A **Windows group** is a security principal that represents a **collection of other security principals** (users, computers, or other groups) for the purpose of simplifying permission assignment.

- As any security principal, each group is uniquely identified by a SID.
- Local groups are defined in the SAM database. 

>[!important] A group can not authenticate or execute code.

- Groups can contain:
	- Users
	- Other groups
	- Computers (domain context)

>[!note]+ Types of groups
> - There are two primary types of Windows groups:
> 	- **Security Groups** <- That's what we're talking about
> 		- Used to grant permissions and privileges to a group of security principals; can be used in ACLs (files, registry, services), and user rights assignments. 
> 	- **Distribution Groups**
> 		- Used for email lists (e.g., Exchange).
> 		-  Have no SID and can't be used for access control.
### Group scopes

- Group **scope** determines where a particular group can be used, and what it can contains:

| Scope                    | Description                                                                                                                                                                                                                                           |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Local groups**         | Can exist only withing the local security database of the computer were it's created.<br>Can contain user accounts that are local to the computer and user accounts and global groups from their own domain.                                          |
| **Domain local groups**  | Can contain **members from any trusted domain**, but can be granted **permissions only to resources in their own domain**.                                                                                                                            |
| **Domain global groups** | Can contain **members only from their own domain**, but can be granted **permissions to resources in any trusting domain**.<br>Global groups are created on DCs and exist in the domain directory database.                                           |
| **Universal groups**     | Can contain members for any domain and can be granted permissions to resources in any domain in a specific [AD forest](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2003/cc783351(v=ws.10)?redirectedfrom=MSDN). |

## Enumerating groups

- List groups the current user is a member of:

```powershell
whoami /groups
```

```powershell
net user <username>
```

>[!note] `whoami /groups` lists security groups only.

- For domain context:

```powershell
net user <username> /domain
```


- PowerShell:

```powershell
Get-DomainGroupMember
```

- List all groups:

```powershell
net localgroup
```

- List all users in a group:

```powershell
net localgroup <group_name>
```
## Built-in local security groups

>[!note] SIDs starting with **`S-1-5-32-*`** identify **built-in local groups**.

>[!note] SIDs of local security groups start with `SID S-1-5-32-*`.

> [!bug] High-value groups for privilege escalation
> - Administrators
> - [[🛠️ Backup Operators]]
>- [[🛠️ Event Log Readers]]
> - Server Operators
> - Print Operators
> - Remote Desktop Users
> - Distributed COM Users / DCOM Users
> - `IIS_IUSRS` / Web-related groups

- Administrative and privileged groups:

| Group                      | SID            | Description                                                                                                                                                                                   |
| -------------------------- | -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`Administrators`**       | `S-1-5-32-544` | Grants complete and unrestricted access to the system.                                                                                                                                        |
| **`Backup Operators`**     | `S-1-5-32-551` | Back up and restore all files on a computer, bypassing ACLs.<br>Privileges: `SeInteractiveLogonRight`, `SeBackupPrivilege`, `SeBatchLogonRight`, `SeRestorePrivilege`, `SeShutdownPrivilege`. |
| **`Server Operators`**     | `S-1-5-32-549` | Manage services (mostly servers).                                                                                                                                                             |
| **`Print Operators`**      | `S-1-5-32-550` | Manage printers.                                                                                                                                                                              |
| **`Power Users`** (legacy) | `S-1-5-32-547` | Limited admin-like rights (deprecated).                                                                                                                                                       |
| **`Acccount Operators`**   | `S-1-5-32-548` | Limited account creation privileges to a user (create/modify most types of accounts, but not `Administrator` user. administrator's accounts, `Administrators` group, and some others).        |

- Account & access control groups:

| Group                         | SID            | Description              |
| ----------------------------- | -------------- | ------------------------ |
| **`Users`**                   | `S-1-5-32-545` | Standard users.          |
| **`Guests`**                  | `S-1-5-32-546` | Highly restricted users. |
| **`Remote Desktop Users`**    | `S-1-5-32-555` | Allows RDP logon.        |
| **`Distributed COM Users`**   | `S-1-5-32-562` | DCOM access permissions. |
| **`Remote Management Users`** | `S-1-5-32-580` | WinRM access.            |

- Monitoring and auditing groups:

| Group                           | SID            | Description                  |
| ------------------------------- | -------------- | ---------------------------- |
| **`Event Log Readers`**         | `S-1-5-32-573` | Read event logs.             |
| **`Performance Log Users`**     | `S-1-5-32-559` | Manage performance logs.     |
| **`Performance Monitor Users`** | `S-1-5-32-558` | Access performance counters. |

- Service & system interaction groups:

| Group                                 | SID            | Description                       |
| ------------------------------------- | -------------- | --------------------------------- |
| **`Network Configuration Operators`** | `S-1-5-32-556` | Change network settings.          |
| **`Cryptographic Operators`**         | `S-1-5-32-569` | Perform cryptographic operations. |
| **`IIS_IUSRS`**                       | `S-1-5-32-568` | IIS worker processes.             |

- Storage and file replication:

| Group                  | SID            | Description               |
| ---------------------- | -------------- | ------------------------- |
| **`Replicator`**       | `S-1-5-32-552` | File replication support. |
| **`Backup Operators`** | `S-1-5-32-551` | (repeated intentionally). |

- Hyper-V / virtualization:

| Group                                     | SID            | Description                                                                                 |
| ----------------------------------------- | -------------- | ------------------------------------------------------------------------------------------- |
| **`Hyper-V Administrators`**              | `S-1-5-32-578` | Manage Hyper-V.                                                                             |
| **`Access Control Assistance Operators`** | `S-1-5-32-579` | Remotely query authorization attributes and permissions (ACLs) for resources on the system. |

- Special / less obvious groups:

| Group                     | SID        | Description                                       |
| ------------------------- | ---------- | ------------------------------------------------- |
| **`Authenticated Users`** | `S-1-5-11` | All authenticated users.                          |
| **`Everyone`**            | `S-1-1-0`  | All users (including anonymous in some contexts). |
| **`Interactive`**         | `S-1-5-4`  | Local/interactive logon users.                    |
| **`Network`**             | `S-1-5-2`  | Network logons.                                   |
| **`Batch`**               | `S-1-5-3`  | Scheduled task context.                           |

>[!note] Reference: [`How-to: Windows Built-in Users, Default Groups and Special Identities — SS64`](https://ss64.com/nt/syntax-security_groups.html) and [`Security identifiers — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-identifiers).

>[!note] See [[🛠️ Windows privileges]].

## `Backup Operators`


>The **`Backup Operators` group** is a built-in local group that grants members the ability to back up and restore all files on a computer, regardless of the permissions that protect those files.

- The intended purpose of the `Backup Operators` group is to give members an ability to **read any file on the system** and **restore files** (even system files) without full administrative privileges for the purpose of operating backups.

>[!tip]+
> - List groups you're a member of:
> 
> ```powershell
> whoami /groups
> ```

- Normally, NTFS permissions would block backup tools:
	- Files owned by other users are inaccessible
	- System files are protected
	- Locked files are problematic to handle
- So Windows introduces a special model where backup operators can **override ACLs**.
- Instead of modifying permissions, Windows allows _trusted identities_ to bypass them **only for backup/restore operations**.

>[!bug] `Backup Operators` is often abused for privilege escalation. It can access sensitive files like the SAM database and system files (owned by `SYSTEM`).

>[!note] `Backup Operators` is not about getting access to files. It's about **getting the ability to ignore access control** when using **specific APIs**.

- Key privileges of the `Backup Operators` group:

	- `SeBackupPrivilege`
		- Allows users to **bypass file system permissions** to back up files. This means a Backup Operator can read files that they normally do not have permissions to access.
	- `SeRestorePrivilege`
		- Allows users to **restore files** to any location on the file system, including protected or sensitive locations. This also allows modifying files that would otherwise be restricted.

| Privilege            | Name                                                                                                                                                        | Description                                                                                                                                                                                                     |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `SeBackupPrivilege`  | [Back up files and directories](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/back-up-files-and-directories) | Bypass file and directory, registry, and other persistent object permissions (for backup purposes).<br>Only effective for access through NTFS backup API; otherwise, standard permissions apply.                |
| `SeRestorePrivilege` | [Restore files and directories](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/restore-files-and-directories) | Bypass file, directory, registry, and other persistent object permissions when they restore backed up files and directories; determine which users can set valid security principals as the owner of an object. |

>[!note] See [[🛠️ Windows privileges#`SeBackupPrivilege`]].
## `Event Log Readers`


>The **`Event Log Readers` group** is a built-in local group designed to allow members to read event logs (including `System`, `Application`, and `Security` logs) on a specific machine without granting full administrative privileges.

- Members of the Event Log Readers group have the following privileges:
	- **Read event logs**
	- **View security logs**

- While doesn't inherently grant elevated privileges, membership in `Event Log Readers` may serve as an indirect privilege escalation path. By analyzing logs, you can:
	- Identify sensitive information, such as account credentials, account lockouts, or changes made by other users. 
		- This information could potentially be leveraged to gain unauthorized access to accounts or systems. 
	- Identify vulnerabilities by searching for indicates of misconfigurations in the logs. 
	- Target other users

>[!tip]+
> - List groups you're a member of:
> 
> ```powershell
> whoami /groups
> ```


## `DnsAdmins`

### DNS in Active Directory

- Active Directory uses DNS as its primary mechanism for dynamic service discovery.
- Rather than maintaining a static list of servers, domain-joined systems query DNS to determine which DCs (Domain Controllers) provide the required services within the domain. 
---
- When a client needs to locate a DC, it performs a DNS query for **[`SRV` (Service Locator) records](https://en.wikipedia.org/wiki/SRV_record)**. A `SRV` record advertises that a particular host provides specific services over a specific protocol and port.

>[!info]- `SRV` record structure
>- A `SRV` records has the form:
>```powershell
>_service._protocol.name. ttl IN SRV priority weight port target.
>```
>- `service`: The network service being offered.
>- `protocol`: The transport protocol of the desired service (usually TCP/UDP).
>- `name`: The domain name for which this record is valid (ends with a dot).
>- `ttl`: Standard DNS TTL (Time-To-Live).
>- `IN`: Standard DNS class field (always `IN`).
>- `SRV`: Record type (always `SRV` for `SRV` records).
>- `priority`: The priority of the target host (lower value -> more preferred).
>- `weight`: A relative weight of records with the same priority (higher value -> higher chance of getting picked).
>- `port`: The TCP or UDP port on which the service listens.
>- `target`: The canonical hostname of the machine providing the service (ends with a dot).
>

- Some examples of `SRV` records:

```powershell
_ldap._tcp.dc._msdcs.<domain>
_kerberos._tcp.dc._msdcs.<domain>   → Kerberos authentication service
_ldap._tcp.gc._msdcs.<forest>       → Global Catalog servers
_ldap._tcp.<site>._sites.dc._msdcs.<domain> → Site-specific Domain Controllers
```

>[!note] When multiple SRV records are returned, the client selects one according to the **priority** and **weight** values defined in the DNS records.

- As a result, **AD is non-functional without DNS**. Any compromise of DNS infrastructure directly impacts domain authentication and directory operations.
- In most cases, the DNS Server role is installed on Domain Controllers. The DNS service (`dns.exe`) runs as `NT AUTHORITY\SYSTEM`.
- Therefore, **control over DNS on a DC effectively means `SYSTEM`-level execution on a Domain Controller**, which is equivalent to **full domain compromise**.

### `DnsAdmins` group


>The **[`DnsAdmins`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups#dnsadmins)** group is a privileged Active Directory security group that grants administrative control over the DNS Server service, including the ability to manage DNS zones, records, and server-level configuration.


>[!note] See [`DnsAdmins, Active Directory security groups — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups#dnsadmins).




## `Hyper-V Administrators`
## `Print Operators`

## `Server Operators`
## References and further reading

- [`Group Scope — Mictosoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-authsod/597504d8-5408-4629-9d81-aab661e6c953)
- [`How-to: Windows Built-in Users, Default Groups and Special Identities — SS64`](https://ss64.com/nt/syntax-security_groups.html)
- [`Security identifiers — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-identifiers)
- [`Group Privileges — OSCP-CPTS NOTES`](https://notes.dollarboysushil.com/windows-privilege-escalation/group-privileges)

- `Backup Operators`
	- `SeBackupPrivilege`
	- `SeRestorePrivilege`