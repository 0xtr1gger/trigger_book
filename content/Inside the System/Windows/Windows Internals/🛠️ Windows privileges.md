---
created: 2026-07-20
tags:
  - Windows
status: substantial
---
## Windows privileges

> A **[Windows privilege](https://learn.microsoft.com/en-us/windows/win32/secauthz/privileges)** is a named right assigned to a security principal (a user or group) and stored in their access token. It authorizes the holder to perform specific **system-level operations** on a local system — such as loading drivers, changing system time, or shutting down the system — independently of object-specific Access Control Lists (ACLs).

- **Privileges vs. access rights**:
	- **Access rights** control a subject's ability to interact with specific securable objects (e.g., files, registry keys, processes). They are defined in Access Control Entries (ACEs) within an object's Discretionary Access Control List (DACL).
	- **Privileges**, in contrast, are not tied to individual objects. They authorize system-level operations and access to protected resources. Privileges are assigned to users and groups administratively and are evaluated based on those present in the user's access token.

- Privilege assignment is an administrative configuration, not an inherent property of an account.
- Each privilege is identified internally by a **Locally Unique Identifier (LUID)**.
- User privileges are stored in the access token created upon successful logon.

>[!note] See [[🛠️ Access tokens and impersonation]].

> [!important] Privileges are enforced locally by the Local Security Authority (LSA) on each machine, even when assigned via domain Group Policy.

### Privilege evaluation

- When a process requests a privileged operation, Windows evaluates the **effective access token** to decide if the action should be allowed. The process consists of several steps: 
	1. Determine the effective token (the thread's impersonation token, if one exists; otherwise, the process token).
	2. Check whether the required privilege is present in the token. 
	3. Verify that the privilege is **enabled**.

- If either check fails, the operation is denied. Some APIs return success but don't perform the privileged action (fail silently), and others fail with `ERROR_PRIVILEGE_NOT_HELD`.

>[!important] A privilege must be **both present and enabled** in the effective access token before Windows will authorize an operation that requires it.

>[!bug] Privilege Escalation Context
> Many Windows privilege escalation techniques exploit accounts or services that possess powerful but misconfigured privileges. Examples include the Potato family of attacks (e.g., Rotten Potato, Juicy Potato, Rogue Potato, PrintSpoofer), which abuse impersonation-related privileges such as `SeImpersonatePrivilege` or `SeAssignPrimaryTokenPrivilege`.

### Privilege states

- Privileges within an access token have [attributes](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_privilege_set) that determine whether they can be used. Only **enabled** privileges are considered during access checks.

| State                                                      | Meaning                                                                     |
| ---------------------------------------------------------- | --------------------------------------------------------------------------- |
| **Enabled (`SE_PRIVILEGE_ENABLED`)**                       | Active and immediately usable.                                              |
| **Disabled**                                               | Present but inactive; must be explicitly enabled programmatically.          |
| **Enabled by default (`SE_PRIVILEGE_ENABLED_BY_DEFAULT`)** | Automatically enabled when the token is created, but can be disabled later. |
| **Removed (`SE_PRIVILEGE_REMOVED`)**                       | Permanently removed from the token; cannot be restored.                      |

> [!note] Disabled privileges can be enabled programmatically using [`AdjustTokenPrivileges()`](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-adjusttokenprivileges).

- Many Windows APIs automatically enable required privileges during execution, for the duration of the privileged operations.

### User rights assignment

- Privileges are assigned to users and groups through **User Rights Assignment**:
	- Local configuration: `secpol.msc`, `gpedit.msc`.
	- Domain environments: [Group Policy (GPOs)](https://learn.microsoft.com/en-us/previous-versions/windows/desktop/policy/group-policy-objects).

- Even in domain scenarios, enforcement remains local to each system.

- You can view assigned privileges and policies by exporting them:

```powershell
secedit /export /cfg C:\temp\policy.cfg
```

- Below are some of the key rights assignments:

| Privilege                       | Group Policy setting                                                                                                                                                                                                                                               | Description                                                                                                                                                                                                     |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `SeTcbPrivilege`                | [Act as part of the operating system](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/act-as-part-of-the-operating-system)                                                       | Assume the identity of any user and thereby gain access to the resources that the user is authorized to access.                                                                                                 |
| `SeBackupPrivilege`             | [Back up files and directories](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/back-up-files-and-directories)                                                                                                        | Bypass file and directory, registry, and other persistent object permissions (for backup purposes).<br>Only effective for access through NTFS backup API; otherwise, standard permissions apply.                |
| `SeCreateTokenPrivilege`        | [Create a token object](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/create-a-token-object)                                                                                   | Create access tokens and use it to gain access to local resources.                                                                                                                                              |
| `SeDebugPrivilege`              | [Debug programs](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/debug-programs)                                                                                                                                      | Attach to or open any process, even a process they do not own (e.g., read process's memory).                                                                                                                    |
| `SeEnableDelegationPrivilege`   | [Enable computer and user accounts to be trusted for delegation](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/enable-computer-and-user-accounts-to-be-trusted-for-delegation) | Set the **Trusted for Delegation** setting on a user or computer object.                                                                                                                                        |
| `SeAuditPrivilege`              | [Generate security audits](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/generate-security-audits)                                                                             | Generate audit records in the security event log.                                                                                                                                                               |
| `SeImpersonatePrivilege`        | [Impersonate a client after authentication](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/impersonate-a-client-after-authentication)                                                                                | Impersonate a user or another specified account and act on behalf of the user.                                                                                                                                  |
| `SeLoadDriverPrivilege`         | [Load and unload device drivers](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/load-and-unload-device-drivers)                                                                                                      | Dynamically load and unload device drivers.                                                                                                                                                                     |
| `SeSecurityPrivilege`           | [Manage auditing and security log](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/manage-auditing-and-security-log)                                                                                                  | Specify object access audit options for individual resources such as files, Active Directory objects, and registry keys.                                                                                        |
| `SeSystemEnvironmentPrivilege`  | [Modify firmware environment values](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/modify-firmware-environment-values)                                                         | Modify firmware environment values.                                                                                                                                                                              |
| `SeAssignPrimaryTokenPrivilege` | [Replace a process level token](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/replace-a-process-level-token)                                                                   | Replace the access token that is associated with a child process.                                                                                                                                               |
| `SeRestorePrivilege`            | [Restore files and directories](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/restore-files-and-directories)                                                                                                        | Bypass file, directory, registry, and other persistent object permissions when they restore backed up files and directories; determine which users can set valid security principals as the owner of an object. |
| `SeTakeOwnershipPrivilege`      | [Take ownership of files or other objects](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/take-ownership-of-files-or-other-objects)                                                                                  | Take ownership of any securable object in the device, including Active Directory objects, NTFS files and folders, printers, registry keys, services, processes, and threads.                                    |
| `SeNetworkLogonRight`           | [Access this computer from the network](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/access-this-computer-from-the-network)                                                   | Access the system over the network (e.g., SMB, NetBIOS, CIFS, COM+, etc.).                                                                                                               |
| `SeRemoteInteractiveLogonRight` | [Allow log on through Remote Desktop Services](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/allow-log-on-through-remote-desktop-services)                                                                          | Access the sign-in screen through RDP.                                                                                                                                                                          |

>[!note] See [`User Rights Assignment — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/user-rights-assignment).

>[!important] When a user logs on with **administrative-equivalent privileges** (any of the above except `SeNetworkLogonRight` and `SeRemoteInteractiveLogonRight`), Windows generates Event ID **[`4672`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4672)** (`Special privileges assigned to new logon`).

> [!note] Logon rights such as `SeNetworkLogonRight` and `SeRemoteInteractiveLogonRight` control _how_ a user can log on, not what privileged operations they can perform after authentication.

## Enumerating privileges

- Full token information, including group memberships and privileges:

```cmd
whoami /all
```

- Privileges only:

```cmd
whoami /priv
```

## Specific privileges

### `SeImpersonatePrivilege`

> The **[`SeImpersonatePrivilege`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/impersonate-a-client-after-authentication)** user right gives a process the ability to attach an **impersonation token** to one of its threads and execute in the security context represented by that token.

- **Default assignments:**
	- `NT AUTHORITY\SYSTEM` (kernel-level services)
	- `NT AUTHORITY\LocalService` (low-privilege local services)
	- `NT AUTHORITY\NetworkService` (network-facing local services)
	- `IIS APPPOOL\<PoolName>` (IIS worker process, per app pool)
	- `NT SERVICE\MSSQL$<instance>` (SQL Server service, per instance)
	- `NT SERVICE\<service_name>` (per-service virtual accounts)

- **Mechanics:**
	- Without `SeImpersonatePrivilege`, a process can still *call* impersonation APIs (e.g., `ImpersonateNamedPipeClient()`), but Windows silently downgrades the impersonation level to `SecurityIdentification` — the token becomes read-only for identity inspection and cannot be used for resource access.
	- A process may impersonate a token **without** `SeImpersonatePrivilege` only if:
		1. The token represents the same user who owns the calling process.
		2. The requested impersonation level is below `SecurityImpersonation` (e.g., `Identification`).

> [!important] `SeImpersonatePrivilege` is what makes the impersonation *effective*. Without it, you can see who the token belongs to, but you cannot act as them.

> [!bug] Exploitation
> This privilege is the foundation of the "Potato" family privilege escalation techniques. When landing on a host via an IIS webshell, MSSQL `xp_cmdshell`, or a Jenkins executor, you are almost certainly running as a service account — which means you likely have `SeImpersonatePrivilege`.
> See [[JuicyPotato]], [[RoguePotato]], [[PrintSpoofer]], [[GodPotato]], [[SweetPotato]] for exploitation.

### `SeAssignPrimaryTokenPrivilege`

> The **[`SeAssignPrimaryTokenPrivilege`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/replace-a-process-level-token)** user right gives a process the ability to assign a **primary token** to a new or suspended child process.

- **Default assignments:**
	- `NT AUTHORITY\SYSTEM`
	- `NT AUTHORITY\LocalService`
	- `NT AUTHORITY\NetworkService`
	- (Generally, the same service accounts that hold `SeImpersonatePrivilege`).

- **Mechanics:**
	- While `SeImpersonatePrivilege` works with *thread-level* impersonation tokens, `SeAssignPrimaryTokenPrivilege` works with *process-level* primary tokens.
	- This privilege is required by APIs like `CreateProcessAsUserW()`, which takes a primary token and spawns a new process under it.

> [!bug] Exploitation
> To escalate to `SYSTEM` using these privileges, the exploitation chain typically follows:
> 1. Obtain a `SYSTEM`-level **impersonation token** (via a named pipe, RPC, or COM authentication capture).
> 2. Use `SeImpersonatePrivilege` to attach it to your thread — your thread now *is* `SYSTEM`.
> 3. Duplicate the impersonation token into a **primary token** using `DuplicateTokenEx()`.
> 4. Use `CreateProcessWithTokenW()` (requires `SeImpersonatePrivilege`) or `CreateProcessAsUserW()` (requires `SeAssignPrimaryTokenPrivilege`) to spawn a new process under that primary token.
> See [[🛠️ Access tokens and impersonation#Token duplication]] for details on token conversion.

### `SeDebugPrivilege`

> The **[`SeDebugPrivilege`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/debug-programs)** user right gives a process an ability to open or attach to any other process on the system, regardless of its security descriptor or ownership — including processes running as `SYSTEM`.

- **Default assignments:**
	- `BUILTIN\Administrators`

- **Mechanics:**
	- `SeDebugPrivilege` was originally intended for developers and administrators to debug system components without granting full administrative rights.
	- It bypasses most security checks regarding process memory access.

>[!example]+ Validating `SeDebugPrivilege`
> ```powershell
> PS C:\Windows\system32> whoami /priv
> ```
> ```
> PRIVILEGES INFORMATION
> ----------------------                                                               
> Privilege Name                Description                    State     
> ============================= ============================== ========  
> SeDebugPrivilege              Debug programs                 Enabled   
> SeChangeNotifyPrivilege       Bypass traverse checking       Enabled   
> SeIncreaseWorkingSetPrivilege Increase a process working set Disabled  
> ```

> [!bug] Exploitation
> `SeDebugPrivilege` is commonly abused for **credential theft and privilege escalation** (e.g., dumping LSASS memory to extract credentials).
> See [[🛠️ SeDebugPrivilege]].

### `SeTakeOwnershipPrivilege`

> The **[`SeTakeOwnershipPrivilege`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/take-ownership-of-files-or-other-objects)** user right gives a user an ability to take ownership of any securable object, including AD objects, NTFS files/folders, printers, registry keys, services, and processes, even without explicit discretionary access.

- **Default assignments:**
	- `BUILTIN\Administrators`

- **Mechanics:**
	- Every [securable object](https://learn.microsoft.com/en-us/windows/win32/secauthz/securable-objects) in Windows has an **owner** defined in its security descriptor. The owner determines how permissions are assigned and which principals are granted access.
	- By default, the creator of an object becomes its owner.
	- Formally, `SeTakeOwnershipPrivilege` assigns [`WRITE_OWNER`](https://learn.microsoft.com/en-us/windows/win32/secauthz/standard-access-rights) access rights against a target object's security descriptor, which allows the assignee to replace the current owner in the `Owner` field with their own Security Identifier (SID).

> [!important] The owner can always modify an object's DACL (Discretionary Access Control List), even if they are explicitly denied all other permissions.

> [!bug] Exploitation
> It is not uncommon to find this privilege assigned to a service account running backup jobs or VSS snapshots. While somewhat situational, abusing `SeTakeOwnershipPrivilege` to assume ownership of critical system files, services, or registry keys can lead to **privilege escalation**.

### `SeBackupPrivilege`

> The **[`SeBackupPrivilege`](https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/privileges)** user right allows a user or process to **bypass file and directory, registry, and other persistent object permissions** specifically for the purpose of backing up.

- **Default assignments (Workstations and Servers):**
	- `BUILTIN\Administrators`
	- `BUILTIN\Backup Operators`
- **Default assignments (Domain Controllers):**
	- `BUILTIN\Administrators`
	- `BUILTIN\Backup Operators`
	- `BUILTIN\Server Operators`

- **Mechanics:**
	- This user right is similar to granting the following permissions to the user or group you selected on **all files and folders on the system**:
		- Traverse Folder/Execute File
		- List Folder/Read Data
		- Read Attributes
		- Read Extended Attributes
		- Read Permissions
	- This user right is effective **only when an application attempts access through the NTFS backup Application Programming Interface (API)**. Otherwise, standard file and directory permissions apply.

> [!important] `SeBackupPrivilege` can operate on arbitrary files **only programmatically**, by explicitly specifying the [`FILE_FLAG_BACKUP_SEMANTICS`](https://docs.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilea) flag during file handle creation. Most normal commands do not use this flag.

#### Commands that work with `SeBackupPrivilege`

- **`robocopy /b`** (uses backup mode via `SeBackupPrivilege` and `SeRestorePrivilege`):
  ```powershell
  robocopy C:\Windows\System32\config C:\temp SAM /b
  ```
  *(Note: `robocopy /zb` first tries normal copy, and if denied, switches to backup mode).*
- **`reg save`** (works for registry hives because it leverages the registry subsystem/LSA, which natively supports `SeBackupPrivilege`):
  ```powershell
  reg save HKLM\SAM C:\Windows\Temp\sam.hive
  reg save HKLM\SYSTEM C:\Windows\Temp\system.hive
  ```
- **Custom tools:** Tools like the [`SeBackupPrivilege.ps1 PoC`](https://github.com/giuliano108/SeBackupPrivilege) work because they set `FILE_FLAG_BACKUP_SEMANTICS` manually.
- **Backup APIs:** VSS tools such as [`diskshadow`](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/diskshadow) and Windows Backup APIs are specifically designed to use `SeBackupPrivilege`.

#### Commands that do NOT work with `SeBackupPrivilege`

- `copy` — uses standard file APIs without setting the backup flag.
- `Copy-Item` (PowerShell) — normal .NET file APIs; no backup semantics.
- `type`, `more`, `notepad` — normal file read APIs.

> [!bug] Exploitation
> Attackers can abuse this privilege to extract sensitive files that are normally restricted, such as the `SAM` and `SYSTEM` registry hives or the `NTDS.dit` file on Domain Controllers, allowing for offline credential dumping.
> See [[🛠️ Backup Operators and SeBackupPrivilege]].

## Appendix A: Windows privilege table

| Privilege                                   | Description                                                                                           |
| :------------------------------------------ | :---------------------------------------------------------------------------------------------------- |
| `SeAssignPrimaryTokenPrivilege`             | Replace the primary access token associated with a process.                                           |
| `SeAuditPrivilege`                          | Generate security audit entries; allows writing to the security event log.                            |
| `SeBackupPrivilege`                         | Back up files and directories, bypassing normal ACL read controls.                                    |
| `SeChangeNotifyPrivilege`                   | Bypass directory traversal checking; allows moving through folders even without explicit permissions. |
| `SeCreateGlobalPrivilege`                   | Create named objects in the global namespace (session-aware).                                         |
| `SeCreatePagefilePrivilege`                 | Create or change the size of a paging file.                                                           |
| `SeCreatePermanentPrivilege`                | Create permanent shared objects in the object namespace.                                              |
| `SeCreateSymbolicLinkPrivilege`             | Create symbolic links in the file system.                                                             |
| `SeCreateTokenPrivilege`                    | Create a new access token object (requires acting as part of the TCB).                                |
| `SeDebugPrivilege`                          | Debug and adjust the memory of other processes; bypasses most security checks.                        |
| `SeDelegateSessionUserImpersonatePrivilege` | Impersonate another user in the same session.                                                         |
| `SeEnableDelegationPrivilege`               | Enable computer and user accounts to be trusted for delegation.                                       |
| `SeImpersonatePrivilege`                    | Impersonate a client after authentication.                                                            |
| `SeIncreaseBasePriorityPrivilege`           | Increase the base priority of a process.                                                              |
| `SeIncreaseQuotaPrivilege`                  | Adjust memory quotas for a process.                                                                   |
| `SeIncreaseWorkingSetPrivilege`             | Increase the working set of a process.                                                                |
| `SeLoadDriverPrivilege`                     | Load and unload device drivers.                                                                       |
| `SeLockMemoryPrivilege`                     | Lock physical pages in memory to prevent them from being paged to disk.                               |
| `SeMachineAccountPrivilege`                 | Add workstation/computer accounts to a domain.                                                        |
| `SeManageVolumePrivilege`                   | Perform volume maintenance tasks, such as defragmentation or remote file creation.                    |
| `SeProfileSingleProcessPrivilege`           | Profile a single process's performance.                                                               |
| `SeRelabelPrivilege`                        | Modify an object's Mandatory Integrity Label (MIC).                                                   |
| `SeRemoteShutdownPrivilege`                 | Force a shutdown from a remote system.                                                                |
| `SeRestorePrivilege`                        | Restore files and directories, bypassing normal ACL write controls.                                   |
| `SeSecurityPrivilege`                       | Manage auditing and the security log (view/clear logs, set SACLs).                                    |
| `SeShutdownPrivilege`                       | Shut down the local system.                                                                           |
| `SeSyncAgentPrivilege`                      | Synchronize directory service data (Directory Replication).                                           |
| `SeSystemEnvironmentPrivilege`              | Modify nonvolatile firmware environment settings (UEFI/BIOS).                                         |
| `SeSystemProfilePrivilege`                  | Profile system performance (kernel-wide).                                                             |
| `SeSystemtimePrivilege`                     | Change the system time.                                                                               |
| `SeTakeOwnershipPrivilege`                  | Take ownership of objects (files, registry keys) regardless of permissions.                           |
| `SeTcbPrivilege`                            | Act as part of the operating system (Trusted Computing Base).                                         |
| `SeTimeZonePrivilege`                       | Change the system time zone.                                                                          |
| `SeTrustedCredManAccessPrivilege`           | Access Credential Manager in a trusted way.                                                           |
| `SeUndockPrivilege`                         | Remove a laptop from a docking station.                                                               |
| `SeUnsolicitedInputPrivilege`               | (Obsolete) Read unsolicited input from a terminal device.                                             |

## References and further reading

- [`Privileges — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/secauthz/privileges)
- [`User Rights Assignment — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/user-rights-assignment)
- [`Windows Privilege Abuse: Auditing, Detection, and Defense — Palantir Blog, Medium`](https://blog.palantir.com/windows-privilege-abuse-auditing-detection-and-defense-3078a403d74e)
- [`AdjustTokenPrivileges function (securitybaseapi.h) — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-adjusttokenprivileges)
- [`4672(S): Special privileges assigned to new logon. — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4672)
- [`Managing privileges in a file system — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/privileges)