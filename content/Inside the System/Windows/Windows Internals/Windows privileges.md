---
created: 2026-07-20
tags:
  - Windows
status: incomplete
---
## Windows privileges

> A **[Windows privilege](https://learn.microsoft.com/en-us/windows/win32/secauthz/privileges)** is a named system right assigned to a **security principal** (a user or group) that authorizes the holder to perform specific **system-level operations** on a local machine.

- Unlike permissions on files and other objects, privileges are granted directly to the principal and are stored in the principal's **access token** after a successful logon. 
- Privileges exist because some operations affect the operating system itself rather than a particular object, for example, changing the system time, loading kernel drivers, taking ownership of files, debugging other processes, or shutting down the system.
- Privileges, therefore, are evaluated independently of any specific object ACL (Access Control List). 

>[!important] Privileges are enforced **locally** by the **Local Security Authority (LSA)** on each machine, even when they are assigned through domain Group Policy.
>- A domain controller can distribute privilege assignments, but each Windows system ultimately decides whether a local process has the required privilege.

- Privilege assignment is an administrative configuration, not an inherent property of a user account.
- The privileges available to a process are determined when its access token is created during logon. 

>[!note] See [[🛠️ Access tokens and impersonation]].

>[!note]- Privileges vs. access rights
> - **Access rights (permissions)** determine whether a subject (e.g., a user) can access a particular securable object (e.g., a file, registry key, service, or process). They are defined by **Access Control Entries (ACEs)** in an object's **Discretionary Access Control List (DACL)**.
>- **Privileges** authorize system-wide operations that are not associated with a specific object. During a privileged operation, Windows checks the caller's access token for the required privilege rather than consulting an object's DACL.

>[!note] Each privilege is identified internally by a **Locally Unique Identifier (LUID)**. Human-readable names such as `SeDebugPrivilege` or `SeBackupPrivilege` are mapped to these LUIDs by the operating system.
### Privilege evaluation

- A privilege only participates in an authorization decision if it is **present** in the **effective access token** and is in the **enabled** state.
- When a thread or process attempts a privileged operation, Windows determines which access token applies and checks whether it contains the required privilege in an enabled state. 
- The process looks as follows:
	1. Determine the **effective access token**:
		- the thread's **impersonation token**, in one exists;
		- otherwise, the process's **primary access token**.
	2. Determine whether the required privilege is **present** in the token.
	3. Verify that the privilege is **enabled**.
	4. If all checks succeed, authorize the privilege operation; otherwise, deny it.
- If the required privilege is missing or disabled, the operation typically fails. Some APIs return success but don't perform the privileged action (fail silently), and others fail with `ERROR_PRIVILEGE_NOT_HELD`.

>[!important] A privilege must be **both present and enabled** in the effective access token for Windows to authorize an operation that requires it.

>[!note] If a thread is impersonating another security principal, Windows evaluates the **thread's impersonation token** rather than the process's primary token.

### Privilege states

- Each privilege stored in an access token has [attributes](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_privilege_set) that describe its current state. During a privilege check, Windows only considers privileges that are **enabled**.

| State                                                      | Meaning                                                                                                 |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| **Enabled (`SE_PRIVILEGE_ENABLED`)**                       | Active and can be used immediately during authorization checks.                                         |
| **Disabled**                                               | Present in the token but inactive; must be enabled before Windows considers it during privilege checks. |
| **Enabled by default (`SE_PRIVILEGE_ENABLED_BY_DEFAULT`)** | Enabled automatically when the access token is created; may later be disabled or re-enabled.            |
| **Removed (`SE_PRIVILEGE_REMOVED`)**                       | Permanently removed from the token and can't be re-enabled for that token.                              |

>[!note] A process can enable or disable privileges that are already **present** in its access token by calling [`AdjustTokenPrivileges()`](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-adjusttokenprivileges). This function can't add new privileges to a token; privilege assignment is performed administratively *before* the token is created.

- Some Windows APIs temporarily enable a required privilege for the duration of a specific operation if the privilege is already present in the caller's token; others require the caller to explicitly enable the privilege beforehand.

>[!example] A process whose token contains `SeDebugPrivilege` in a **disabled** state can't open a protected process just because the privilege is present. The process must first enable `SeDebugPrivilege`, and only then will Windows consider it during the authorization check. If the privilege is absent from the token entirely, it's impossible to enable it without obtaining a new access token that contains the privilege.
### User rights assignment

>**User Rights Assignment** is a Local Security Policy that determines which **privileges** and **logon rights** are granted to users and security groups. These assignments are incorporated into a user's access token upon successful authentication.

- Windows uses User Rights Assignment to define what a security principal is allowed to do on a system. 
- Some assignments grant **privileges** (allow system-level operations such as debugging processes); others define **logon rights** (list the ways in which a user is allowed/denied to authenticate to the machine).
- User rights can be assigned through:
	- **Local Security Policy** (`secpol.msc`)
	- **Local Group Policy** (`gpedit.msc`)
	- **Domain [Group Policy Objects (GPOs)](https://learn.microsoft.com/en-us/previous-versions/windows/desktop/policy/group-policy-objects)** in AD environments

>[!note] Again, although domain GPOs distribute these assignments, they are ultimately enforced by the **Local Security Authority (LSA)** on each individual system.

- Export and inspect assigned using rights using:

```powershell
secedit /export /cfg C:\Temp\policy.cfg
```

#### Important user rights 

- User rights commonly using in Windows privilege escalation: 

| Privilege                       | Group Policy setting                                                                                                                                                                                                                                                 | Description                                                                                                                                                              |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `SeTcbPrivilege`                | [`Act as part of the operating system`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/act-as-part-of-the-operating-system)                                                       | Allows a process to **act as part of the operating system** and **create or manipulate security tokens**. Intended only for highly trusted system components.            |
| `SeBackupPrivilege`             | [`Back up files and directories`](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/back-up-files-and-directories)                                                                                                        | **Bypasses file and registry permissions for backup operations** performed through the Windows backup APIs.                                                              |
| `SeCreateTokenPrivilege`        | [`Create a token object`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/create-a-token-object)                                                                                   | Allows a process to **create access tokens**. Normally reserved for the LSA.                                                                                             |
| `SeDebugPrivilege`              | [`Debug programs`](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/debug-programs)                                                                                                                                      | Allows a process **open and debug processes (including reading their memory) that would otherwise be inaccessible** (subject to certain protected-process restrictions). |
| `SeEnableDelegationPrivilege`   | [`Enable computer and user accounts to be trusted for delegation`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/enable-computer-and-user-accounts-to-be-trusted-for-delegation) | Allows **configuring accounts for Kerberos delegation**.                                                                                                                 |
| `SeAuditPrivilege`              | [`Generate security audits`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/generate-security-audits)                                                                             | Allows **writing audit records to the Security event log**.                                                                                                              |
| `SeImpersonatePrivilege`        | [`Impersonate a client after authentication`](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/impersonate-a-client-after-authentication)                                                                                | Allows a server process to **impersonate authenticated clients**.                                                                                                        |
| `SeLoadDriverPrivilege`         | [`Load and unload device drivers`](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/load-and-unload-device-drivers)                                                                                                      | Allows **loading or unloading kernel-mode drivers**.                                                                                                                     |
| `SeSecurityPrivilege`           | [`Manage auditing and security log`](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/manage-auditing-and-security-log)                                                                                                  | Allows a process **manage auditing settings and the Security event log**.                                                                                                |
| `SeSystemEnvironmentPrivilege`  | [`Modify firmware environment values`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/modify-firmware-environment-values)                                                         | Allows a process **modify UEFI/firmware environment variables**.                                                                                                         |
| `SeAssignPrimaryTokenPrivilege` | [`Replace a process level token`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/replace-a-process-level-token)                                                                   | Allows **assigning a primary token to a process**.                                                                                                                       |
| `SeRestorePrivilege`            | [`Restore files and directories`](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/restore-files-and-directories)                                                                                                        | **Bypasses file and registry permissions during restore operations**, allows **restoring security descriptors**.                                                         |
| `SeTakeOwnershipPrivilege`      | [`Take ownership of files or other objects`](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/take-ownership-of-files-or-other-objects)                                                                                  | Allows **taking ownership of securable objects regardless of the current owner**.                                                                                        |
| `SeNetworkLogonRight`           | [`Access this computer from the network`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/access-this-computer-from-the-network)                                                   | Grants the ability to **log on over the network** (SMB, RPC, WinRM, etc.).                                                                                               |
| `SeRemoteInteractiveLogonRight` | [`Allow log on through Remote Desktop Services`](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/allow-log-on-through-remote-desktop-services)                                                                          | Grants the ability to **log on interactively through RDP**.                                                                                                              |

>[!note] See [`User Rights Assignment — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/user-rights-assignment).

>[!note] **Logon rights** (such as `SeNetworkLogonRight` and `SeRemoteInteractiveLogonRight`) determine **how** a user may authenticate to a system. Unlike privileges, they do not authorize privileged system operations after logon.

>[!info] When a user logs on with **administrative-equivalent privileges** (any of the above except `SeNetworkLogonRight` and `SeRemoteInteractiveLogonRight`), Windows generates Event ID **[`4672`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4672)** (`Special privileges assigned to new logon`); commonly used in monitoring.
## Enumerating privileges

- Display all information from the access token, including the user SID, group memberships, privileges, integrity level, and logon information:

```cmd
whoami /all
```

- Display only the privileges present in the current access token:

```cmd
whoami /priv
```

- The output includes each privilege's current state (for example, `Enabled` or `Disabled`).

>[!note] `whoami` only displays the privileges present in the **current access token**. It does **not** show every privilege that has been assigned to the user through User Rights Assignment, as some assignments (particularly logon rights) are not represented as token privileges.

## `SeImpersonatePrivilege`

> The **[`SeImpersonatePrivilege`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/impersonate-a-client-after-authentication)** user right gives a process the ability to attach an **impersonation token** to one of its threads and execute in the security context represented by that token.

- **Default assignments:**
	- `NT AUTHORITY\SYSTEM` (kernel-level services)
	- `NT AUTHORITY\LocalService` (low-privilege local services)
	- `NT AUTHORITY\NetworkService` (network-facing local services)
	- `IIS APPPOOL\<PoolName>` (IIS worker process, per app pool)
	- `NT SERVICE\MSSQL$<instance>` (SQL Server service, per instance)
	- `NT SERVICE\<service_name>` (per-service virtual accounts)

- Without `SeImpersonatePrivilege`, a process can still *call* impersonation APIs (e.g., `ImpersonateNamedPipeClient()`), but Windows silently downgrades the impersonation level to `SecurityIdentification` — the token becomes read-only for identity inspection and cannot be used for resource access.
- A process may impersonate a token **without** `SeImpersonatePrivilege` only if:
	1. The token represents the same user who owns the calling process.
	2. The requested impersonation level is below `SecurityImpersonation` (e.g., `Identification`).

> [!important] `SeImpersonatePrivilege` is what makes the impersonation *effective*. Without it, you can see who the token belongs to, but you cannot act as them.

> [!bug] This privilege is the foundation of the "Potato" family privilege escalation techniques. See [[JuicyPotato]], [[RoguePotato]], [[PrintSpoofer]], [[GodPotato]], [[SweetPotato]] for exploitation.

## `SeAssignPrimaryTokenPrivilege`

> The **[`SeAssignPrimaryTokenPrivilege`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/replace-a-process-level-token)** user right gives a process the ability to assign a **primary token** to a new or suspended child process.

- Default assignments (generally, the same service accounts that hold `SeImpersonatePrivilege`):
	- `NT AUTHORITY\SYSTEM`
	- `NT AUTHORITY\LocalService`
	- `NT AUTHORITY\NetworkService`

- While `SeImpersonatePrivilege` works with *thread-level* impersonation tokens, `SeAssignPrimaryTokenPrivilege` works with *process-level* primary tokens.
- This privilege is required by APIs like `CreateProcessAsUserW()`, which takes a primary token and spawns a new process under it.

>[!note] See [[🛠️ Access tokens and impersonation#Token duplication]].

## `SeDebugPrivilege`

> The **[`SeDebugPrivilege`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/debug-programs)** user right gives a process an ability to open or attach to any other process on the system, regardless of its security descriptor or ownership — including processes running as `SYSTEM`.

- Default assignments:
	- `BUILTIN\Administrators`

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

> [!bug] `SeDebugPrivilege` can be to **dump LSASS memory to extract credentials** (see [[🛠️ SeDebugPrivilege]]).
## `SeTakeOwnershipPrivilege`

> The **[`SeTakeOwnershipPrivilege`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/take-ownership-of-files-or-other-objects)** user right gives a user an ability to take ownership of any securable object, including AD objects, NTFS files/folders, printers, registry keys, services, and processes, even without explicit discretionary access.

- Default assignments:
	- `BUILTIN\Administrators`

- Every [securable object](https://learn.microsoft.com/en-us/windows/win32/secauthz/securable-objects) in Windows has an **owner** defined in its security descriptor. The owner determines how permissions are assigned and which principals are granted access.
- By default, the creator of an object becomes its owner.
- Formally, `SeTakeOwnershipPrivilege` assigns [`WRITE_OWNER`](https://learn.microsoft.com/en-us/windows/win32/secauthz/standard-access-rights) access rights against a target object's security descriptor, which allows the assignee to replace the current owner in the `Owner` field with their own Security Identifier (SID).

> [!important] The owner can always modify an object's DACL (Discretionary Access Control List), even if they are explicitly denied all other permissions.

> [!bug] While somewhat situational, `SeTakeOwnershipPrivilege` can be abused to take ownership of critical system files, services, or registry keys and lead to **privilege escalation**. See [[🛠️ SeTakeOwnershipPrivilege]].

## `SeBackupPrivilege`

> The **[`SeBackupPrivilege`](https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/privileges)** user right allows a user or process to **bypass file and directory, registry, and other persistent object permissions** specifically for the purpose of backing up.

- Default assignments (workstations and servers):
	- `BUILTIN\Administrators`
	- `BUILTIN\Backup Operators`
- Default assignments (Domain Controllers):
	- `BUILTIN\Administrators`
	- `BUILTIN\Backup Operators`
	- `BUILTIN\Server Operators`

- This user right is similar to granting the following permissions to the user or group you selected on **all files and folders on the system**:
	- Traverse Folder/Execute File
	- List Folder/Read Data
	- Read Attributes
	- Read Extended Attributes
	- Read Permissions
- This user right is effective **only when an application attempts access through the NTFS backup API**. Otherwise, standard file and directory permissions apply.

> [!important] `SeBackupPrivilege` can operate on arbitrary files **only programmatically**, by explicitly specifying the [`FILE_FLAG_BACKUP_SEMANTICS`](https://docs.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilea) flag during file handle creation. Most normal commands do not use this flag.
### Commands that work with `SeBackupPrivilege`

- **[`robocopy /b`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/robocopy)** — uses backup mode via `SeBackupPrivilege` and `SeRestorePrivilege`:

```powershell
robocopy /B C:\Windows\System32\config\SAM C:\Temp sam.hive
```

```powershell
robocopy /B C:\Windows\System32\config\SYSTEM C:\Temp system.hive
```

>[!note] `robocopy /ZB` first tries normal copy, and if denied, switches to backup mode.

>[!note] See [[Backup Operators and SeBackupPrivilege#Using `robocopy /B`]].

  - **[`reg save`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/reg-save)** — works for registry hives because it uses the registry subsystem/LSA, which natively supports `SeBackupPrivilege`:

```powershell
reg save HKLM\SAM C:\Temp\sam.hive
```

```powershell
reg save HKLM\SYSTEM C:\Temp\system.hive
```

>[!note] See [[Backup Operators and SeBackupPrivilege#Using `reg save`]].

- VSS (Volume Shadow Copy) tools like [`diskshadow`](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/diskshadow) and Windows Backup APIs are specifically designed to use `SeBackupPrivilege`, so they will work, too.

>[!note] See [[Backup Operators and SeBackupPrivilege#Copying `NTDS.dit` using `diskshadow`]].

>[!tip]+ Alternatively, you can use custom tools like the [`SeBackupPrivilege.ps1`](https://github.com/giuliano108/SeBackupPrivilege) PoC; they work because they set `FILE_FLAG_BACKUP_SEMANTICS` manually. See [[Backup Operators and SeBackupPrivilege#Using `SeBackupPrivilege.ps1` PoC]].

- **Backup APIs:** VSS tools such as [`diskshadow`](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/diskshadow) and Windows Backup APIs are specifically designed to use `SeBackupPrivilege`.
### Commands that don't work with `SeBackupPrivilege`

- [`copy`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/copy) — uses standard file APIs without setting the backup flag.
- [`Copy-Item`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/copy-item?view=powershell-7.6) (PowerShell) — normal .NET file APIs; no backup semantics.
- [`type`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/type), [`more`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/more), `notepad` — use normal file read APIs.
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
>[!bug] Privilege Escalation Context
> Many Windows privilege escalation techniques exploit accounts or services that possess powerful but misconfigured privileges. Examples include the Potato family of attacks (e.g., Rotten Potato, Juicy Potato, Rogue Potato, PrintSpoofer), which abuse impersonation-related privileges such as `SeImpersonatePrivilege` or `SeAssignPrimaryTokenPrivilege`.



- Privileges of a security principal are listed in their access token (created at logon upon successful authentication).


> [!bug]+ `SeAssignPrimaryTokenPrivilege` privilege escalation
> To escalate to `SYSTEM` using these privileges, the exploitation chain typically follows:
> 1. Obtain a `SYSTEM`-level **impersonation token** (via a named pipe, RPC, or COM authentication capture).
> 2. Use `SeImpersonatePrivilege` to attach it to your thread — your thread now *is* `SYSTEM`.
> 3. Duplicate the impersonation token into a **primary token** using `DuplicateTokenEx()`.
> 4. Use `CreateProcessWithTokenW()` (requires `SeImpersonatePrivilege`) or `CreateProcessAsUserW()` (requires `SeAssignPrimaryTokenPrivilege`) to spawn a new process under that primary token.