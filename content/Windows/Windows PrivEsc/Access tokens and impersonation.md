---
created: 2026-02-20
tags:
  - Windows
status: complete
updated: 2026-09-20
---
## Access tokens and impersonation

> [!abstract]+ **Scope**: Access tokens; primary, impersonation, and delegation tokens; impersonation levels; token privileges relevant to privilege escalation.

## How access tokens work

- Every Windows process operates under an **access token** that defines its security context, and individual threads can also use an impersonation token.
-
>An [access token](https://learn.microsoft.com/en-us/windows/win32/secauthz/access-tokens) is a kernel object that describes the security context of a process or thread.

- Access tokens contain the user account identity, including the user **SID (Security Identifier)**, **group SIDs**, **privileges**, default **DACLs (Discretionary Access Control Lists)**, and authentication metadata.
- Access tokens are created by the **Local Security Authority (LSA)** during authentication and then associated with the newly created logon session.
- The Windows **[Security Reference Monitor (SRM)](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/windows-kernel-mode-security-reference-monitor)** evaluates access tokens during authorization checks against securable objects (such as files, registry keys, named pipes, and process handles).

>[!note] Once created by LSA, access tokens are immutable kernel objects.

>[!info]+ An access token includes the following components:
> - The **user SID** that identifies the account owner.
> - **Group SIDs** for every security group of which the user is a member.
> - A **logon SID** that uniquely identifies the logon session to isolate session-specific objects.
> - A list of **privileges** assigned to the user or their groups.
> - An **owner SID** used as the default owner when creating securable objects.
> - The **primary group SID** (retained for POSIX compatibility).
> - The **default DACL** applied when creating securable objects without an explicit security descriptor.
> - The **token source** that identifies the component that created the token.
> - The **token type** (primary or impersonation).
> - An optional list of *[restricted SIDs](https://learn.microsoft.com/en-us/windows/win32/secauthz/restricted-tokens)* used for sandboxing.
> - The **impersonation level** (applicable only to impersonation tokens).

>[!note]+ States 
>- Some of these entries also have a **state** that determines whether and how Windows uses them during authorization:
>	- A privilege can be **enabled** or **disabled**. A privilege may be present in the token without currently being enabled.
>	- A group SID can be enabled, disabled, or marked deny-only, which affects how the SID participates in access checks.
>	- Restricted tokens can contain restricted SIDs and removed or disabled privileges that further limit the token's effective permissions.

>[!note]+ The token **source** identifies the component that created the token (mostly used for auditing):
> - `"User32"` → interactive logon
> - `"NtLmSsp"` → NTLM authentication package
> - `"Kerberos"` → Kerberos authentication package
> - `"SecLogo"` → Secondary logon service (`RunAs`)

## Primary, impersonation, and delegation tokens

- Windows defines two token types: **primary** and **impersonation**.
### Primary tokens

>A **primary token** describes the default security context of a process.

- When you authenticate, the LSA validates your credentials and creates an access token associated with the resulting logon session.
- Processes started in that session are assigned a **primary token**, which defines their default security context. Examples include `explorer.exe` and `cmd.exe`.
- By default, a child process runs under a primary token representing the same security context as its parent, unless another token is explicitly supplied.
- When a thread accesses a securable object, SRM uses the process's primary token for the access check unless the thread is actively impersonating another security context.

>[!important] Every process has exactly one primary token. 

>[!important] Processes in the same logon session may have equivalent security contexts, but they do not necessarily share the same token object or identical token state.

>[!important] You generally can't replace the primary token of an already running process. To run code under a different primary token, you typically create a new process using that token.
### Impersonation tokens

>An **impersonation token** is attached to an individual thread and allows that thread to perform actions under a security context distinct from the process's primary token.

>[!important] Impersonation tokens are assigned to individual threads rather than directly to processes.

>[!important] When an impersonation token is attached to a thread, SRM uses the impersonation token instead of the process's primary token during access checks.

>[!note] Impersonation tokens can't start a new process directly. To launch a process under another user's security context, you must duplicate the impersonation token into a primary token using `DuplicateTokenEx()`, then call `CreateProcessWithTokenW()` or `CreateProcessAsUserW()`.

- Impersonation tokens are common in client-server architectures where a multi-client service (such as an IIS web server or an RPC server) executes requests on behalf of authenticated clients.
- Impersonation tokens originate from client authentication events, including:
	- Client connections to named pipes.
	- RPC client requests.
	- COM client method invocations.
	- SMB file access requests.
	- Explicit authentication APIs such as `LogonUser()` or token duplication via `DuplicateTokenEx()`.

- Within a multithreaded process, one thread can use the process's primary token while another uses an impersonation token representing a client.
- If a thread removes its impersonation token (by calling `RevertToSelf()`), it reverts to using the process's primary token.

> [!example]+ Common impersonation scenarios
> - An IIS worker process (`w3wp.exe`) impersonates an authenticated web application user to read a file from disk.
> - An SMB server thread in the Servier service (`lanmanserver`) impersonates a domain user accessing a network share.
## Impersonation levels

- Windows enforces four distinct [impersonation levels](https://learn.microsoft.com/en-us/windows/win32/secauthz/impersonation-levels):

| Impersonation level      | Description                                                                            | Practical impact                                                                                        |
| :----------------------- | :------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------ |
| `SecurityAnonymous`      | The server can't retrieve the client's identify or impersonate the client.             | The token contains no client identity details.                                                          |
| `SecurityIdentification` | The server can query client identity and privileges, but can't impersonate the client. | Useful for identity verification.<br>All resource access checks using this token fail.                  |
| `SecurityImpersonation`  | The server can impersonate the client security context on the local system.            | Standard impersonation level.<br>Allows access local files, registry keys, and local securable objects. |
| `SecurityDelegation`     | The server can impersonate the client security context on local and remote systems.    | Highest impersonation level.<br>Enables remote network authentication across domain hosts.              |

>[!important] Only `SecurityImpersonation` and `SecurityDelegation` allow resource access operations. `SecurityIdentification` allows identity inspection, but access checks using that token will fail.

### Delegation tokens

>A **delegation token** is an impersonation token with the `SecurityDelegation` impersonation level. It allows a server to impersonate a client to other remote systems.

- An impersonation token at the `SecurityImpersonation` level allows the server to impersonate the client locally but not to delegate that identity to another remote system.
- The `SecurityDelegation` level can allow the client's security context to be used on remote systems (typically used in Kerberos delegation scenarios).
- When a user connects to a service configured for delegation, the server receives a credential structure or ticket that can request secondary Kerberos service tickets for remote network resources **as the user**.

> [!note] See [[Kerberos#Kerberos delegation]] and [[◯ RBCD attacks]].

## Token privileges and security contexts

- In addition to SIDs, access tokens hold **privileges** that grant specific system-level rights, some of which can bypass normal object access checks (DACLs).
- Privileges are assigned to user accounts and security groups through **Local Security Policy** or **Group Policy**.
- Key security privileges relevant to privilege escalation include:
	- `SeImpersonatePrivilege` ([Impersonate a client after authentication]((https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/dn221967(v=ws.11))): Allows a process to impersonate a client after authentication (when the required token and impersonation conditions are present).
	- `SeAssignPrimaryTokenPrivilege` ([Replace a process-level token](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/dn221975\(v=ws.11\))): Allows a process to assign primary tokens to newly created processes.
	- `SeDebugPrivilege` ([Debug programs](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/dn221969\(v=ws.11\))): Allows a process to bypass normal access checks to open handles to other processes (including `SYSTEM` processes like `lsass.exe`).
	- `SeTakeOwnershipPrivilege` ([Take ownership of files or other objects](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/dn221976\(v=ws.11\))): Allows a process to take ownership of any file, registry key, or securable object on the machine.
	- `SeRestorePrivilege` ([Restore files and directories](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/dn221962\(v=ws.11\)))/`SeBackupPrivilege` ([Back up files and directories](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/dn221961\(v=ws.11\))): Allows backup or restore operations that bypass certain file and directory access checks.
	- `SeLoadDriverPrivilege` ([Load and unload device drivers](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/dn221964\(v=ws.11\))): Allows a process to load or unload kernel-mode drivers, which can provide a path to kernel-mode code execution.
	- `SeTcbPrivilege` ([Act as part of the operating system](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/dn221957\(v=ws.11\))): Allows a process to assume the identity of any user without authentication. This privilege identifies its holder as part of the Trusted Computer Base (TCB) and is typically reserved for low-level authentication services and the Local System account.
	- `SeIncreaseQuotaPrivilege` ([Adjust memory quotas for a process](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/dn221983\(v=ws.11\))): Allows a process to change the maximum memory that can be consumed by a process.

>[!note] See [[Windows privileges]] and [`User Rights Assignment — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/dn221963(v=ws.11)).

>[!note] See [[SeDebugPrivilege]], [[SeTakeOwnershipPrivilege]], [[Backup Operators]], and [[Print Operators]].


## How impersonation works

> **Impersonation** is the ability of a thread to execute under a security context different from that defined by the owning process's primary token.

- The client-server impersonation lifecycle follows these steps:
	1. A client authenticates to a server using an authentication or communication mechanism such as NTLM, Kerberos, named pipes, or RPC.
	2. Windows obtains or creates a token representing the authenticated client's security context on the server/
	3. The server attaches the token to the thread handling the request via APIs such as:
		 - `ImpersonateLoggedOnUser()` — Impersonates a logged-on user given a token handle.
		 - `RpcImpersonateClient()` — Impersonates an authenticated RPC client.
		 - `ImpersonateNamedPipeClient()` — Impersonates a client connected to a named pipe.
		 - `SetThreadToken()` — Directly assigns a token to a specified thread.
	4. The thread executes file, registry, or system operations under the client context.
	5. The thread calls `RevertToSelf()` to detach the impersonation token and return to the primary process identity.

>[!note] The client does not control when or how the server impersonates it. How the token is used is determined by the server application's code.

### `SeImpersonatePrivilege` requirements

- In many cases, impersonating a client at the `SecurityImpersonation` or `SecurityDelegation` level requires `SeImpersonatePrivilege`, although Windows provides specific exceptions for certain trusted or explicitly authenticated contexts.
- Without `SeImpersonatePrivilege`, Windows silently downgrades impersonation tokens to `SecurityIdentification`, rendering them unusable for resource access or token elevation.

### Duplicating tokens and executing processes

- Impersonation tokens can't launch processes directly. Only primary tokens can be assigned to a process.
- `DuplicateTokenEx()` can be used to duplicate a token and specify whether the resulting token is primary or impersonation.
	- Impersonation token → primary token: Required to spawn a process under the impersonated identity.
	- Primary token → impersonation token: Useful when a primary token needs to be duplicated as an impersonation token and assigned to a thread.
- Common APIs for creating a process with another primary token include:
	- `CreateProcessWithTokenW()` — Generally requires `SeImpersonatePrivilege`.
	- `CreateProcessAsUserW()` — May require `SeAssignPrimaryTokenPrivilege` and `SeIncreaseQuotaPrivilege`, depending on the token and calling context.

> [!bug] Token impersonation and duplication are central mechanisms used by Potato-family privilege escalation techniques (capturing `SYSTEM` impersonation token → `DuplicateTokenEx()` to primary token → spawn `SYSTEM` process).

> [!note] See [[GodPotato]], [[PrintSpoofer]], [[🛠️ JuicyPotato]], [[RoguePotato]], and [[🛠️ SweetPotato]].

## References and further reading

- [`Access tokens — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/secauthz/access-tokens)
- [`Restricted tokens — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/secauthz/restricted-tokens)
- [`Impersonation levels (Authorization) — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/secauthz/impersonation-levels)
- [`Client impersonation (Authorization) — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/secauthz/client-impersonation)
- [`DuplicateTokenEx function — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-duplicatetokenex)

