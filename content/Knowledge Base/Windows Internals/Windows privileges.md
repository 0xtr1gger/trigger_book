---
created: 2026-07-20
tags:
  - Windows
status: incomplete
updated: 2026-10-04
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

>[!note] See [[Access tokens and impersonation]].

>[!note]- Privileges vs. access rights
> - **Access rights (permissions)** determine whether a subject (e.g., a user) can access a particular securable object (e.g., a file, registry key, service, or process). They are defined by **Access Control Entries (ACEs)** in an object's **Discretionary Access Control List (DACL)**.
> - **Privileges** authorize system-wide operations that are not associated with a specific object. During a privileged operation, Windows checks the caller's access token for the required privilege rather than consulting an object's DACL.

>[!note] Each privilege is identified internally by a **Locally Unique Identifier (LUID)**. Human-readable names such as `SeDebugPrivilege` or `SeBackupPrivilege` are mapped to these LUIDs by the operating system.

### Privilege evaluation

- A privilege only participates in an authorization decision if it is **present** in the **effective access token** and is in the **enabled** state.
- When a thread or process attempts a privileged operation, Windows determines which access token applies and checks whether it contains the required privilege in an enabled state. 
- The evaluation process follows these steps:
	1. Determine the **effective access token**: the thread's **impersonation token**, if one exists; otherwise, the process's **primary access token**.
	2. Determine whether the required privilege is **present** in the token.
	3. Verify that the privilege is **enabled**.
	4. If all checks succeed, authorize the privilege operation; otherwise, deny it.
- If the required privilege is missing or disabled, the operation typically fails. Some APIs return success but don't perform the privileged action (fail silently), and others fail with `ERROR_PRIVILEGE_NOT_HELD`.

>[!important] A privilege must be **both present and enabled** in the effective access token for Windows to authorize an operation that requires it.

>[!note] If a thread is impersonating another security principal, Windows evaluates the **thread's impersonation token** rather than the process's primary token.

### Privilege states

- Each privilege stored in an access token has [attributes](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_privilege_set) that describe its current state. During a privilege check, Windows only considers privileges that are **enabled**.

| State | Description |
| :--- | :--- |
| **Enabled (`SE_PRIVILEGE_ENABLED`)** | Active and can be used immediately during authorization checks. |
| **Disabled** | Present in the token but inactive; must be enabled before Windows considers it during privilege checks. |
| **Enabled by default (`SE_PRIVILEGE_ENABLED_BY_DEFAULT`)** | Enabled automatically when the access token is created; may later be disabled or re-enabled. |
| **Removed (`SE_PRIVILEGE_REMOVED`)** | Permanently removed from the token and can't be re-enabled for that token. |

>[!note] A process can enable or disable privileges that are already **present** in its access token by calling [`AdjustTokenPrivileges()`](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-adjusttokenprivileges). This function can't add new privileges to a token; privilege assignment is performed administratively *before* the token is created.

- Some Windows APIs temporarily enable a required privilege for the duration of a specific operation if the privilege is already present in the caller's token; others require the caller to explicitly enable the privilege beforehand.

>[!example] A process whose token contains `SeDebugPrivilege` in a **disabled** state can't open a protected process just because the privilege is present. The process must first enable `SeDebugPrivilege`, and only then will Windows consider it during the authorization check. If the privilege is absent from the token entirely, you can't enable it without obtaining a new access token that contains the privilege.

### User rights assignment

> **User Rights Assignment** is a Local Security Policy that determines which **privileges** and **logon rights** are granted to users and security groups. These assignments are incorporated into a user's access token upon successful authentication.

- Windows uses User Rights Assignment to define what a security principal is allowed to do on a system. 
- Some assignments grant **privileges** (allow system-level operations such as debugging processes); others define **logon rights** (list the ways in which a user is allowed/denied to authenticate to the machine).
- User rights can be assigned through:
	- **Local Security Policy** (`secpol.msc`)
	- **Local Group Policy** (`gpedit.msc`)
	- **Domain [Group Policy Objects (GPOs)](https://learn.microsoft.com/en-us/previous-versions/windows/desktop/policy/group-policy-objects)** in AD environments

>[!note] Although domain GPOs distribute these assignments, they are ultimately enforced by the **Local Security Authority (LSA)** on each individual system.

- Export and inspect assigned user rights using:

```powershell
secedit /export /cfg C:\Temp\policy.cfg
```

#### Important user rights 

- User rights commonly encountered in Windows environments: 

| Privilege | Group Policy setting | Description |
| :--- | :--- | :--- |
| `SeTcbPrivilege` | [`Act as part of the operating system`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/act-as-part-of-the-operating-system) | Allows a process to **act as part of the operating system** and **create or manipulate security tokens**. Reserved for highly trusted system components. |
| `SeBackupPrivilege` | [`Back up files and directories`](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/back-up-files-and-directories) | **Bypasses file and registry permissions for backup operations** performed through Windows backup APIs. |
| `SeCreateTokenPrivilege` | [`Create a token object`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/create-a-token-object) | Allows a process to **create access tokens**. Reserved for the LSA. |
| `SeDebugPrivilege` | [`Debug programs`](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/debug-programs) | Allows a process to **open and debug processes (including reading memory) that would otherwise be inaccessible** (subject to protected-process restrictions). |
| `SeEnableDelegationPrivilege` | [`Enable computer and user accounts to be trusted for delegation`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/enable-computer-and-user-accounts-to-be-trusted-for-delegation) | Allows **configuring accounts for Kerberos delegation**. |
| `SeAuditPrivilege` | [`Generate security audits`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/generate-security-audits) | Allows **writing audit records to the Security event log**. |
| `SeImpersonatePrivilege` | [`Impersonate a client after authentication`](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/impersonate-a-client-after-authentication) | Allows a server process to **impersonate authenticated clients**. |
| `SeLoadDriverPrivilege` | [`Load and unload device drivers`](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/load-and-unload-device-drivers) | Allows **loading or unloading kernel-mode drivers**. |
| `SeSecurityPrivilege` | [`Manage auditing and security log`](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/manage-auditing-and-security-log) | Allows a process to **manage auditing settings and the Security event log**. |
| `SeSystemEnvironmentPrivilege` | [`Modify firmware environment values`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/modify-firmware-environment-values) | Allows a process to **modify UEFI/firmware environment variables**. |
| `SeAssignPrimaryTokenPrivilege` | [`Replace a process level token`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/replace-a-process-level-token) | Allows **assigning a primary token to a process**. |
| `SeRestorePrivilege` | [`Restore files and directories`](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/restore-files-and-directories) | **Bypasses file and registry permissions during restore operations**, allowing **restoring security descriptors**. |
| `SeTakeOwnershipPrivilege` | [`Take ownership of files or other objects`](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/take-ownership-of-files-or-other-objects) | Allows **taking ownership of securable objects regardless of the current owner**. |
| `SeNetworkLogonRight` | [`Access this computer from the network`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/access-this-computer-from-the-network) | Grants the ability to **log on over the network** (SMB, RPC, WinRM, etc.). |
| `SeRemoteInteractiveLogonRight` | [`Allow log on through Remote Desktop Services`](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/allow-log-on-through-remote-desktop-services) | Grants the ability to **log on interactively through RDP**. |

>[!note] See [`User Rights Assignment — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/user-rights-assignment).

>[!note] **Logon rights** (such as `SeNetworkLogonRight` and `SeRemoteInteractiveLogonRight`) determine **how** a user authenticates to a system. Unlike privileges, they do not authorize privileged system operations after logon.

>[!info] When a user logs on with **administrative-equivalent privileges** (any of the above except `SeNetworkLogonRight` and `SeRemoteInteractiveLogonRight`), Windows generates Event ID **[`4672`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4672)** (`Special privileges assigned to new logon`).

## Enumerating privileges

- Display all information from the access token, including user SID, group memberships, privileges, integrity level, and logon information:

```cmd
whoami /all
```

- Display only privileges present in the current access token:

```cmd
whoami /priv
```

- The output includes each privilege's current state (`Enabled` or `Disabled`).

>[!note] `whoami` only displays privileges present in the **current access token**. It does **not** show every privilege assigned to the user through User Rights Assignment, as some assignments (particularly logon rights) are not represented as token privileges.

## `SeImpersonatePrivilege`

> The **[`SeImpersonatePrivilege`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/impersonate-a-client-after-authentication)** user right gives a process the ability to attach an **impersonation token** to one of its threads and execute in the security context represented by that token.

- **Default assignments:**
	- `NT AUTHORITY\SYSTEM` (kernel-level services)
	- `NT AUTHORITY\LocalService` (low-privilege local services)
	- `NT AUTHORITY\NetworkService` (network-facing local services)
	- `IIS APPPOOL\<PoolName>` (IIS worker process, per app pool)
	- `NT SERVICE\MSSQL$<instance>` (SQL Server service, per instance)
	- `NT SERVICE\<service_name>` (per-service virtual accounts)

- Without `SeImpersonatePrivilege`, a process can still call impersonation APIs (e.g., `ImpersonateNamedPipeClient()`), but Windows silently downgrades the impersonation level to `SecurityIdentification` — the token becomes read-only for identity inspection and can't be used for resource access.
- A process may impersonate a token **without** `SeImpersonatePrivilege` only if:
	1. The token represents the same user who owns the calling process.
	2. The requested impersonation level is below `SecurityImpersonation` (e.g., `Identification`).

>[!important] `SeImpersonatePrivilege` makes impersonation effective. Without it, you can inspect who the token belongs to, but you can't act as that identity.

>[!note] See [[🛠️ JuicyPotato]], [[RoguePotato]], [[PrintSpoofer]], [[GodPotato]], and [[🛠️ SweetPotato]] for privilege escalation techniques that exploit `SeImpersonatePrivilege`.

## `SeAssignPrimaryTokenPrivilege`

> The **[`SeAssignPrimaryTokenPrivilege`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/replace-a-process-level-token)** user right gives a process the ability to assign a **primary token** to a new or suspended child process.

- Default assignments (generally the service accounts holding `SeImpersonatePrivilege`):
	- `NT AUTHORITY\SYSTEM`
	- `NT AUTHORITY\LocalService`
	- `NT AUTHORITY\NetworkService`

- While `SeImpersonatePrivilege` operates on thread-level impersonation tokens, `SeAssignPrimaryTokenPrivilege` operates on process-level primary tokens.
- APIs like `CreateProcessAsUserW()` require this privilege to take a primary token and spawn a new process under that identity.

>[!note] See [[Access tokens and impersonation#Token duplication]].

## `SeDebugPrivilege`

> The **[`SeDebugPrivilege`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/debug-programs)** user right gives a process the ability to open or attach to any other process on the system, regardless of its security descriptor or ownership — including processes running as `SYSTEM`.

- Default assignments:
	- `BUILTIN\Administrators`

- `SeDebugPrivilege` allows developers and administrators to debug system components without requiring full administrative rights.
- When present and enabled, the kernel bypasses normal discretionary access checks during `OpenProcess()` calls and permits requested rights such as `PROCESS_VM_READ`, `PROCESS_VM_WRITE`, `PROCESS_VM_OPERATION`, and `PROCESS_CREATE_PROCESS` against privileged targets (`lsass.exe`, `services.exe`, `winlogon.exe`).

>[!important] Protected Process Light (PPL) enforcement restricts handle creation against protected processes like `lsass.exe` even when `SeDebugPrivilege` is enabled, unless PPL is bypassed via kernel drivers.

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

>[!note] See [[SeDebugPrivilege]] for privilege escalation techniques that exploit this privilege.

## `SeTakeOwnershipPrivilege`

> The **[`SeTakeOwnershipPrivilege`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/take-ownership-of-files-or-other-objects)** user right gives a user the ability to take ownership of any securable object, including AD objects, NTFS files/folders, printers, registry keys, services, and processes, even without explicit discretionary access.

- Default assignments:
	- `BUILTIN\Administrators`

- Every [securable object](https://learn.microsoft.com/en-us/windows/win32/secauthz/securable-objects) in Windows has an **owner** defined in its security descriptor. The owner determines how permissions are assigned and which principals are granted access.
- By default, the creator of an object becomes its owner.
- Formally, `SeTakeOwnershipPrivilege` grants [`WRITE_OWNER`](https://learn.microsoft.com/en-us/windows/win32/secauthz/standard-access-rights) access right against a target object's security descriptor. This allows the assigned principal to change the object's `Owner` to an arbitrary SID (including their own).

>[!important] The owner can always modify an object's DACL (Discretionary Access Control List), even if explicitly denied all other permissions.

>[!note] See [[SeTakeOwnershipPrivilege]].

## `SeBackupPrivilege`

> The **[`SeBackupPrivilege`](https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/privileges)** user right allows a process to **bypass file, directory, registry, and object permissions** when backing up files.

- Default assignments (workstations and servers):
	- `BUILTIN\Administrators`
	- `BUILTIN\Backup Operators`
- Default assignments (Domain Controllers):
	- `BUILTIN\Administrators`
	- `BUILTIN\Backup Operators`
	- `BUILTIN\Server Operators`

- `SeBackupPrivilege` grants `READ_CONTROL` and `FILE_READ_DATA` access rights on any file or directory object, bypassing any DACLs. It also grants `FILE_TRAVERSE` on directories regardless of their ACLs.
- However, this user right is effective **only when an application attempts access through the NTFS backup API** (by specifying the [`FILE_FLAG_BACKUP_SEMANTICS`](https://docs.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilea) flag during handle creation), otherwise standard file permissions apply.

>[!important] `SeBackupPrivilege` operates on arbitrary files **only programmatically** or through backup-aware tools specifying `FILE_FLAG_BACKUP_SEMANTICS`. Standard file read utilities do not set this flag, therefore `SeBackupPrivilege` is not effective for them.

### Commands that support `SeBackupPrivilege`

- **[`robocopy /b`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/robocopy)** — uses backup mode (`FILE_FLAG_BACKUP_SEMANTICS`):

```powershell
robocopy /B C:\Windows\System32\config\SAM C:\Temp sam.hive
```

```powershell
robocopy /B C:\Windows\System32\config\SYSTEM C:\Temp system.hive
```

>[!note] `robocopy /ZB` tries normal copy first, and if denied, switches to backup mode.

- **[`reg save`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/reg-save)** — registry subsystem and LSA natively support `SeBackupPrivilege` for hive exports:

```powershell
reg save HKLM\SAM C:\Temp\sam.hive
```

```powershell
reg save HKLM\SYSTEM C:\Temp\system.hive
```

- **VSS tools and Backup APIs** — utilities like [`diskshadow`](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/diskshadow) and Windows Backup APIs interact with the Volume Shadow Copy service using `SeBackupPrivilege`.

### Commands that don't support `SeBackupPrivilege`

- [`copy`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/copy) — uses standard file APIs without backup flags.
- [`Copy-Item`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/copy-item) (PowerShell) — standard .NET file APIs without backup semantics.
- [`type`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/type), [`more`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/more), `notepad` — standard file read APIs.

>[!note] For privilege escalation techniques exploiting `SeBackupPrivilege`, see [[SeBackupPrivilege & SeRestorePrivilege]].

## `SeRestorePrivilege`

>The **[`SeRestorePrivilege`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/restore-files-and-directories)** user right allows a user or process to **bypass file, directory, and registry write permissions** specifically for restoring files and directories.

- Default assignments:
	- `BUILTIN\Administrators`
	- `BUILTIN\Backup Operators`
	- `BUILTIN\Server Operators`

- `SeRestorePrivilege` grants `WRITE_DAC`, `WRITE_OWNER`, and `FILE_WRITE_DATA` access rights on any file or directory object, overriding discretionary ACLs.
- When a caller holds `SeRestorePrivilege` and passes `FILE_FLAG_BACKUP_SEMANTICS` to `CreateFile()`, the kernel bypasses normal DACL write validation.
- This privilege permits replacing any file or registry key on the operating system, regardless of object ownership or explicit deny ACEs.

>[!note] For privilege escalation techniques exploiting `SeRestorePrivilege`, see [[SeBackupPrivilege & SeRestorePrivilege]].

## `SeLoadDriverPrivilege`

> The **[`SeLoadDriverPrivilege`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/load-and-unload-device-drivers)** user right grants a process the ability to dynamically load and unload device drivers into kernel memory.

- Default assignments:
	- `BUILTIN\Administrators`
	- `Print Operators`
	- `Server Operators`

- Driver loading via system APIs (`NtLoadDriver()` / `ZwLoadDriver()`) requires a service entry under `HKLM\SYSTEM\CurrentControlSet\Services\<DriverName>` (or `HKCU\System\CurrentControlSet\<DriverName>`) containing `ImagePath` and `Type = 1` (`SERVICE_KERNEL_DRIVER`).
- `SeLoadDriverPrivilege` authorizes calling `NtLoadDriver()` without requiring full local administrative rights.
- Operating system Code Integrity policy (Kernel-Mode Code Signing, or KMCS) enforces Authenticode digital signatures on driver binaries. Legitimate signed drivers with known vulnerabilities satisfy KMCS verification.

>[!note] See [[SeLoadDriverPrivilege]] for privilege escalation techniques that exploit this privilege.

## `SeManageVolumePrivilege`

> The **[`SeManageVolumePrivilege`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/manage-the-files-on-a-volume)** user right grants permission to perform volume maintenance operations, including raw volume device handle creation and direct hardlink creation.

- Default assignments:
	- `BUILTIN\Administrators`
	- Dedicated backup and storage management service accounts

- `SeManageVolumePrivilege` grants `FILE_READ_DATA` and `FILE_WRITE_DATA` access rights to raw volume device objects (such as `\\.\C:` or `\\.\PhysicalDrive0`).
- Operating at the volume management layer allows manipulating file system metadata and creating hardlinks across file object DACL boundaries, bypassing normal file security descriptors.


## Appendix A: Windows privilege table

| Privilege | Description |
| :--- | :--- |
| `SeAssignPrimaryTokenPrivilege` | Replace the primary access token associated with a process. |
| `SeAuditPrivilege` | Generate security audit entries; allows writing to the security event log. |
| `SeBackupPrivilege` | Back up files and directories, bypassing normal ACL read controls. |
| `SeChangeNotifyPrivilege` | Bypass directory traversal checking; allows moving through folders even without explicit permissions. |
| `SeCreateGlobalPrivilege` | Create named objects in the global namespace (session-aware). |
| `SeCreatePagefilePrivilege` | Create or change the size of a paging file. |
| `SeCreatePermanentPrivilege` | Create permanent shared objects in the object namespace. |
| `SeCreateSymbolicLinkPrivilege` | Create symbolic links in the file system. |
| `SeCreateTokenPrivilege` | Create a new access token object (requires acting as part of the TCB). |
| `SeDebugPrivilege` | Debug and adjust the memory of other processes; bypasses most security checks. |
| `SeDelegateSessionUserImpersonatePrivilege` | Impersonate another user in the same session. |
| `SeEnableDelegationPrivilege` | Enable computer and user accounts to be trusted for delegation. |
| `SeImpersonatePrivilege` | Impersonate a client after authentication. |
| `SeIncreaseBasePriorityPrivilege` | Increase the base priority of a process. |
| `SeIncreaseQuotaPrivilege` | Adjust memory quotas for a process. |
| `SeIncreaseWorkingSetPrivilege` | Increase the working set of a process. |
| `SeLoadDriverPrivilege` | Load and unload device drivers. |
| `SeLockMemoryPrivilege` | Lock physical pages in memory to prevent them from being paged to disk. |
| `SeMachineAccountPrivilege` | Add workstation/computer accounts to a domain. |
| `SeManageVolumePrivilege` | Perform volume maintenance tasks, such as defragmentation or remote file creation. |
| `SeProfileSingleProcessPrivilege` | Profile a single process's performance. |
| `SeRelabelPrivilege` | Modify an object's Mandatory Integrity Label (MIC). |
| `SeRemoteShutdownPrivilege` | Force a shutdown from a remote system. |
| `SeRestorePrivilege` | Restore files and directories, bypassing normal ACL write controls. |
| `SeSecurityPrivilege` | Manage auditing and the security log (view/clear logs, set SACLs). |
| `SeShutdownPrivilege` | Shut down the local system. |
| `SeSyncAgentPrivilege` | Synchronize directory service data (Directory Replication). |
| `SeSystemEnvironmentPrivilege` | Modify nonvolatile firmware environment settings (UEFI/BIOS). |
| `SeSystemProfilePrivilege` | Profile system performance (kernel-wide). |
| `SeSystemtimePrivilege` | Change the system time. |
| `SeTakeOwnershipPrivilege` | Take ownership of objects (files, registry keys) regardless of permissions. |
| `SeTcbPrivilege` | Act as part of the operating system (Trusted Computing Base). |
| `SeTimeZonePrivilege` | Change the system time zone. |
| `SeTrustedCredManAccessPrivilege` | Access Credential Manager in a trusted way. |
| `SeUndockPrivilege` | Remove a laptop from a docking station. |
| `SeUnsolicitedInputPrivilege` | (Obsolete) Read unsolicited input from a terminal device. |

## References and further reading

- [`Privileges — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/secauthz/privileges)
- [`User Rights Assignment — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/user-rights-assignment)
- [`Windows Privilege Abuse: Auditing, Detection, and Defense — Palantir Blog`](https://blog.palantir.com/windows-privilege-abuse-auditing-detection-and-defense-3078a403d74e)
- [`AdjustTokenPrivileges function — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-adjusttokenprivileges)
- [`Event ID 4672: Special privileges assigned to new logon — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4672)
- [`Managing privileges in a file system — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/privileges)