---
created: 2026-07-21
tags:
  - Windows
status: incomplete
updated: 2026-07-27
---
- Write about default group on Windows systems
- And default groups on a DC
## Windows groups

>A **Windows group** is a security principal that represents a **collection of other security principals** (users, computers, or other groups). Instead of assigning permissions to every user individually, Windows assigns permissions to **groups**, and users inherit those permissions through their group memberships.

>[!important] Any user added to a group automatically receives all permissions assigned to that group.

- Like any other security principal, every group has its own unique SID (Security Identifier).
- Local groups are stored in the SAM (Security Accounts Manager) database, and domain groups are stored on Domain Controllers.

>[!important] A group can't authenticate or execute code; only user, computer, or service account can.

>[!note]+ Types of groups
> - There are two primary types of Windows groups:
> 	- **Security Groups** <- That's what we're talking about
> 		- Used to grant permissions and privileges to a group of security principals; can be used in ACLs (files, registry, services), and user rights assignments. 
> 	- **Distribution Groups**
> 		- Used for email lists (e.g., Exchange).
> 		-  Have no SID and can't be used for access control.

### Default Windows groups
### Group scopes (Active Directory)

>**Group scope** determines **where a group can be granted permissions** and **which security principals it is allowed to contain**. Scope is relevant only in **Active Directory**; local groups have no scope beyond the local computer.

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

## `Backup Operators`

>The **[`Backup Operators`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups#bkmk-backupoperators)** group is a built-in Windows security group intended for users who perform **system backup and recovery operations** without granting them full administrative access.

- Members of the `Backup Operators` group can **read and restore any file on the system**, **regardless of file ownership and permissions**. 
- However, the privileges granted by `Backup Operators` can be used **only through the Windows backup/restore APIs**.

>[!important] `Backup Operators` **does not grant unrestricted file access**. Instead, it grants the ability to **bypass access checks** during backup and restore operations using APIs that honor these privileges.

- `Backup Operators` grants two user rights:
	- `SeBackupPrivilege`
		- Allows reading files and other securable objects regardless of their ACLs, for backup purposes. 
		- See [Back up files and directories](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/back-up-files-and-directories).
	- `SeRestorePrivilege`
		- Allows restoring files to protected locations and writing objects regardless of their ACLs, for backup purposes. 
		- See [Restore files and directories](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/restore-files-and-directories).

>[!note] See [[Windows privileges#`SeBackupPrivilege`]].

>[!bug] See [[Backup Operators and SeBackupPrivilege]] for privilege escalation.

## `Event Log Readers`

>The **`Event Log Readers`** group is a built-in local group designed to allow members to read event logs (including `System`, `Application`, and `Security` logs) on a specific machine without granting full administrative privileges.

- Members of this group have the following privileges:
	- **Read event logs**
	- **View security logs**

- While membership in `Event Log Readers` does not inherently grant elevated privileges or code execution, it can serve as a powerful **information gathering and indirect privilege escalation path**.
- By analyzing logs, attackers can:
	- Identify sensitive information in command lines, such as plaintext credentials passed to tools like `runas`, `net use`, or `cmdkey`.
	- Monitor account lockouts or configuration changes made by other users. 
	- Enumerate vulnerabilities by identifying misconfigurations or software paths exposed in error logs.

>[!bug] See [[Event Log Readers]] for techniques on extracting credentials from event logs.

## `DnsAdmins`

>The **[`DnsAdmins`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups#dnsadmins)** group is a privileged Active Directory security group that grants administrative control over the DNS Server service, including the ability to manage DNS zones, records, and server-level configuration.

- Active Directory heavily relies on DNS for dynamic service discovery. Domain-joined systems query DNS for **[`SRV` (Service Locator) records](https://en.wikipedia.org/wiki/SRV_record)** to locate Domain Controllers and services (like LDAP or Kerberos).
- As a result, **AD is non-functional without DNS**, and any compromise of DNS infrastructure directly impacts domain authentication.
- By default, the DNS Server role is installed on Domain Controllers, and the DNS service (`dns.exe`) runs as `NT AUTHORITY\SYSTEM`.

>[!important] Because the DNS service typically runs as `SYSTEM` on a Domain Controller, gaining control over the DNS service effectively translates to `SYSTEM`-level execution on a DC, which is equivalent to **full domain compromise**.

>[!info]- DNS Service Locator (`SRV`) records
>When a client needs to locate a DC, it performs a DNS query for an `SRV` record, which advertises that a host provides specific services.
>- Structure: `_service._protocol.name. ttl IN SRV priority weight port target.`
>- Examples:
>  ```powershell
>  _ldap._tcp.dc._msdcs.<domain>
>  _kerberos._tcp.dc._msdcs.<domain>   → Kerberos authentication service
>  _ldap._tcp.gc._msdcs.<forest>       → Global Catalog servers
>  ```
>When multiple records are returned, the client selects one based on the defined **priority** and **weight**.

- Members of the `DnsAdmins` group can configure the DNS server to load a custom server-level plugin DLL. This can be exploited to execute arbitrary code as `SYSTEM`.
- Additionally, `DnsAdmins` membership allows disabling global query block security and creating WPAD (Web Proxy Automatic Discovery) records, which can be used to spoof traffic and capture password hashes.

>[!note] See [`DnsAdmins, Active Directory security groups — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups#dnsadmins).

>[!bug] See [[DnsAdmins]] for privilege escalation.

## `Print Operators`

>The **[`Print Operators`](https://docs.microsoft.com/en-us/windows/security/identity-protection/access-control/active-directory-security-groups#print-operators)** group is a built-in Windows security group primarily intended for administrators responsible for managing printers on **Domain Controllers**.

- Members of this group can:
	- Install and manage printer drivers.
	- Create, delete, and share printers.
	- Manage print queues.
	- Log on locally to a Domain Controller
	- Shut down a Domain Controller.

- Members of this group are granted the **[`SeLoadDriverPrivilege`](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/load-and-unload-device-drivers)** user right, because it's needed to install or update printer drivers (running in kernel mode).

>[!note] See [`Load and unload device drivers — Microsoft Learn`](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/load-and-unload-device-drivers).

> [!bug] `SeLoadDriverPrivilege` can be abused to load a vulnerable kernel-mode driver, which can lead to `SYSTEM`-level code execution. See [[Print Operators]] for privilege escalation.

## `Server Operators`

>The [`Server Operators`](https://docs.microsoft.com/en-us/windows/security/identity-protection/access-control/active-directory-security-groups#bkmk-serveroperators) group is a built-in Windows security group intended for administrators responsible for managing Windows servers — without granting full **Domain Admin** privileges.

>[!important] The `Server Operators` group exists only on Domain Controllers.

- Historically, members of this group were expected to perform routine server administration tasks such as:
	- Starting and stopping services
	- Managing shared folders
	- Performing system backups and restores
	- Logging on locally to servers (including Domain Controllers)
	- Shutting down or restarting servers

- To perform these tasks, members are granted several powerful rights, including the aforementioned `SeBackupPrivilege` and `SeRestorePrivilege` privileges. More importantly, **`Server Operators` grants full control over many local services**.

>[!bug] For privilege escalation using `SeBackupPrivilege`, see already mentioned [[Backup Operators and SeBackupPrivilege]] (the same attack path applies). For privilege escalation via local services, see 

## References and further reading

- [`Group Scope — Mictosoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-authsod/597504d8-5408-4629-9d81-aab661e6c953)
- [`How-to: Windows Built-in Users, Default Groups and Special Identities — SS64`](https://ss64.com/nt/syntax-security_groups.html)
- [`Security identifiers — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-identifiers)
- [`Group Privileges — OSCP-CPTS NOTES`](https://notes.dollarboysushil.com/windows-privilege-escalation/group-privileges)

## Appendix A: Built-in local security groups

>[!note] SIDs starting with **`S-1-5-32-*`** identify **built-in local groups**.

>[!note] SIDs of local security groups start with `SID S-1-5-32-*`.

- **Administrative and privileged groups**:

| Group                      | SID            | Description                                                                                                                                                                                   |
| -------------------------- | -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`Administrators`**       | `S-1-5-32-544` | Grants complete and unrestricted access to the system.                                                                                                                                        |
| **`Backup Operators`**     | `S-1-5-32-551` | Back up and restore all files on a computer, bypassing ACLs.<br>Privileges: `SeInteractiveLogonRight`, `SeBackupPrivilege`, `SeBatchLogonRight`, `SeRestorePrivilege`, `SeShutdownPrivilege`. |
| **`Server Operators`**     | `S-1-5-32-549` | Manage services (mostly servers).                                                                                                                                                             |
| **`Print Operators`**      | `S-1-5-32-550` | Manage printers.                                                                                                                                                                              |
| **`Power Users`** (legacy) | `S-1-5-32-547` | Limited admin-like rights (deprecated).                                                                                                                                                       |
| **`Acccount Operators`**   | `S-1-5-32-548` | Limited account creation privileges to a user (create/modify most types of accounts, but not `Administrator` user. administrator's accounts, `Administrators` group, and some others).        |

- **Account & access control groups**:

| Group                         | SID            | Description              |
| ----------------------------- | -------------- | ------------------------ |
| **`Users`**                   | `S-1-5-32-545` | Standard users.          |
| **`Guests`**                  | `S-1-5-32-546` | Highly restricted users. |
| **`Remote Desktop Users`**    | `S-1-5-32-555` | Allows RDP logon.        |
| **`Distributed COM Users`**   | `S-1-5-32-562` | DCOM access permissions. |
| **`Remote Management Users`** | `S-1-5-32-580` | WinRM access.            |

- **Monitoring and auditing groups**:

| Group                           | SID            | Description                  |
| ------------------------------- | -------------- | ---------------------------- |
| **`Event Log Readers`**         | `S-1-5-32-573` | Read event logs.             |
| **`Performance Log Users`**     | `S-1-5-32-559` | Manage performance logs.     |
| **`Performance Monitor Users`** | `S-1-5-32-558` | Access performance counters. |

- **Service & system interaction groups**:

| Group                                 | SID            | Description                       |
| ------------------------------------- | -------------- | --------------------------------- |
| **`Network Configuration Operators`** | `S-1-5-32-556` | Change network settings.          |
| **`Cryptographic Operators`**         | `S-1-5-32-569` | Perform cryptographic operations. |
| **`IIS_IUSRS`**                       | `S-1-5-32-568` | IIS worker processes.             |

- **Storage and file replication**:

| Group                  | SID            | Description               |
| ---------------------- | -------------- | ------------------------- |
| **`Replicator`**       | `S-1-5-32-552` | File replication support. |
| **`Backup Operators`** | `S-1-5-32-551` | (repeated intentionally). |

- **Hyper-V / virtualization**:

| Group                                     | SID            | Description                                                                                 |
| ----------------------------------------- | -------------- | ------------------------------------------------------------------------------------------- |
| **`Hyper-V Administrators`**              | `S-1-5-32-578` | Manage Hyper-V.                                                                             |
| **`Access Control Assistance Operators`** | `S-1-5-32-579` | Remotely query authorization attributes and permissions (ACLs) for resources on the system. |

- **Special / less obvious groups**:

| Group                     | SID        | Description                                       |
| ------------------------- | ---------- | ------------------------------------------------- |
| **`Authenticated Users`** | `S-1-5-11` | All authenticated users.                          |
| **`Everyone`**            | `S-1-1-0`  | All users (including anonymous in some contexts). |
| **`Interactive`**         | `S-1-5-4`  | Local/interactive logon users.                    |
| **`Network`**             | `S-1-5-2`  | Network logons.                                   |
| **`Batch`**               | `S-1-5-3`  | Scheduled task context.                           |

>[!note] Reference: [`How-to: Windows Built-in Users, Default Groups and Special Identities — SS64`](https://ss64.com/nt/syntax-security_groups.html) and [`Security identifiers — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-identifiers).

>[!note] See [[Windows privileges]].
