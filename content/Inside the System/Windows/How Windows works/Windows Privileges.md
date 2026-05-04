---
created: 2026-04-12
---
## Windows Privileges

> A **[Windows privilege](https://learn.microsoft.com/en-us/windows/win32/secauthz/privileges)** is a named right, stored within an access token, that authorizes an account to perform specific **system-level operations** on the local machine — such as loading kernel drivers, modifying system time, or bypassing file access controls — independently of any object-specific ACLs.

>[!note]+ Privileges vs. access rights
> 
> - **Access rights** control a subject’s ability to read, write, or execute specific securable objects (e.g., files, registry keys, processes). They are defined in the ACEs (Access Control Entries) of an object's DACL (Discretionary Access Control List).
> - **Privileges**, in contrast, are not tied to individual objects. They authorize system-level operations and access to protected resources. Privileges are assigned to users and groups by administrators; the right to perform a specific system operation of a given user is evaluated based on privileges stored in their access token.

> [!note] Privileges are evaluated locally on each system.

- When a user logs on, the LSA (Local Security Authority) generates an **access token** that contains a list of user's privileges, including those inherited from group memberships.
- Every process launched by the user inherits this token. Threads may also carry **impersonation tokens** to act in another security context.

> [!important] User privileges are stored in the access token created at logon.

>[!note] See [[🛠️ Access tokens]].

- When the user attempts to perform a privileged operation, the system checks whether the required privilege exists in the user's access token and whether it is **enabled**.
- If not, the operation is denied or may silently fail (common in legacy Win32 APIs).

>[!bug] Many privilege escalation techniques rely on abusing misconfigured or overly permissive privileges.
### Privilege states

>Privileges in Windows have states (attributes) within an access token. A privilege can be **enabled, disabled, or enabled by default**. Even if assigned, a privilege must be **enabled to be used**, as Windows evaluates only enabled privileges during access checks.

Privileges in a token have [attributes](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_privilege_set) that determine whether they can be used. Only **enabled** privileges are considered during access checks.

| State                                                      | Meaning                                                                  |
| ---------------------------------------------------------- | ------------------------------------------------------------------------ |
| **Enabled (`SE_PRIVILEGE_ENABLED`)**                       | Active and can be used immediately.                                      |
| **Disabled**                                               | Present in the token but currently inactive; must be explicitly enabled. |
| **Enabled by default (`SE_PRIVILEGE_ENABLED_BY_DEFAULT`)** | Automatically enabled when the token is created.                         |
| **Removed (`SE_PRIVILEGE_REMOVED`)**                       | Permanently stripped from the token; can't be restored.                  |

> [!tip]+ Disabled privileges can be enabled using `AdjustTokenPrivileges`. 

>[!important] Many Windows APIs (e.g., backup, restore, debug operations) **enable privileges privileges automatically as needed** during execution.

>[!important] Many Windows APIs **enable privileges automatically when needed**.

> [!note] Each privilege is identified by a **LUID (Locally Unique Identifier)**.

>[!note]+ Privilege checks
> When the user attempts to perform a privileged operation, the kernel performs the following check:
> 
> 1. Identify the effective token of the calling thread (thread impersonation token or process token).
> 2. Check whether the required privilege exists in the token.
> 3. Verify the privilege is **enabled**.
> 4. If any check fails -> access is denied or the operation silently falls.

### User rights assignment

- Privileges are assigned to users and groups via **User Rights Assignment** (`secpol.msc`, `gpedit.msc`).
- In domain environments, they are distributed through [Group Policy (GPOs)](https://learn.microsoft.com/en-us/previous-versions/windows/desktop/policy/group-policy-objects).

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
| `SeSystemEnvironmentPrivilege`  | [Modify firmware environment values](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/modify-firmware-environment-values)                                                         | Modify firmware environment values                                                                                                                                                                              |
| `SeAssignPrimaryTokenPrivilege` | [Replace a process level token](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/replace-a-process-level-token)                                                                   | Replace the access token that is associated with a child process.                                                                                                                                               |
| `SeRestorePrivilege`            | [Restore files and directories](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/restore-files-and-directories)                                                                                                        | Bypass file, directory, registry, and other persistent object permissions when they restore backed up files and directories; determine which users can set valid security principals as the owner of an object. |
| `SeTakeOwnershipPrivilege`      | [Take ownership of files or other objects](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/take-ownership-of-files-or-other-objects)                                                                                  | Take ownership of any securable object in the device, including Active Directory objects, NTFS files and folders, printers, registry keys, services, processes, and threads.                                    |
| `SeNetworkLogonRight`           | [Access this computer from the network](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/access-this-computer-from-the-network)                                                   | Access the system over the network (e.g., SMB, NetBIOS, CIFS, COM+, etc.).                                                                                                                                      |
| `SeRemoteInteractiveLogonRight` | [Allow log on through Remote Desktop Services](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/allow-log-on-through-remote-desktop-services)                                                                          | Access the sign-in screen through RDP.                                                                                                                                                                          |

>[!note] See [`User Rights Assignment — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/user-rights-assignment).

>[!important] When a new account logs on with any of these privileges (except `SeNetworkLogonRight` and `SeRemoteInteractiveLogonRight`), an event with Event ID [`4672`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4672) is generated. 

>[!note] It's possible for a user to establish a Remote Desktop Services connection to a particular server but not be able to sign in to the console of that same server (i.e., without `SeRemoteInteractiveLogonRight`).

>[!bug]+ Privilege abuse
>- [[🛠️ Potatoes]]
>- [[🛠️ SeDebugPrivilege]]

## Enumerating privileges

- Display comprehensive information about the current user, including group memberships and privileges:

```cmd
whoami /all
```

>[!example]-
>```cmd
>whoami /all
>```
>![[whoami_all.png]]

- Privileges only:

```bash
whoami /priv
```

>[!example]+
>```cmd
>whoami /priv
>```
>![[whoami_priv.png]]

## References and further reading

- [`Privileges — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/secauthz/privileges)
- [`User Rights Assignment — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/user-rights-assignment)
- [`Windows Privilege Abuse: Auditing, Detection, and Defense — Palantir Blog, Medium`](# Windows Privilege Abuse: Auditing, Detection, and Defense)
- [`AdjustTokenPrivileges function (securitybaseapi.h) — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-adjusttokenprivileges)
- [`4672(S): Special privileges assigned to new logon. — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4672)
## Appendix A: Windows privilege table

| Privilege Name                              | Description (User Right / What it Allows)                                                             |
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
| `SeProfileSingleProcessPrivilege`           | Profile a single process’s performance.                                                               |
| `SeRelabelPrivilege`                        | Modify an object’s Mandatory Integrity Label (MIC).                                                   |
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
