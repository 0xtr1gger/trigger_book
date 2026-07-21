---
created: 2026-02-20
tags:
  - Windows
status: substantial
---
## Access tokens

- On Windows, every process/thread is assigned an **access token** that describes its security context.

>An [access token](https://learn.microsoft.com/en-us/windows/win32/secauthz/access-tokens) is a kernel object that describes a security context of a process or thread.

- An access token includes information about the user account identity, including the **SID** (user Security Identifier), **group memberships**, **privileges**, and default **DACLs (Discretionary Access Control Lists)**.
- Access tokens are created and assigned to the user by the **Local Security Authority (LSA)** during logon, upon user authentication.

>[!note] Once created, tokens are immutable. 

>[!info]+ An access token includes the following information:
> - The **SID (Security Identifier)** for the user's account.
> - **SIDs for the groups of which the user is a member**.
> - A **logon SID** (uniquely identifies a logon session; is used to isolate session objects).
> - A list of **privileges** held by the user or the user's groups.
> - An **owner SID** (the default owner SID used when the process creates securable objects; usually the user SID).
> - The **SID for the primary group** (for POSIX compatibility).
> - The **default DACL** the system uses when the user creates a securable object without specifying a security descriptor.
> - The **source** of an access token.
> - Whether the token is a *primary* or *impersonation* token.
> - (Optional) A list of *[restricted tokens](https://learn.microsoft.com/en-us/windows/win32/secauthz/restricted-tokens)* (used for sandboxing).
> - Current impersonation levels (only for impersonation tokens).
>
>>[!note]- The token **source** indicates which component created the token. It doesn't directly affect access decisions, and mostly used for auditing and diagnostics.
>>- `"User32"` -> interactive logon
>>- `"NtLmSsp"` -> NTLM authentication package
>>- `"Kerberos"` -> Kerberos authentication
>>- `"SecLogo"` -> Secondary logon service (`RunAs`)

- The Windows **Security Reference Monitor (SRM)** uses tokens during access checks against securable objects.
## Primary and Impersonation tokens

 There are two main types of tokens in Windows:
 - **Primary token**
 - **Impersonation token**
### Primary tokens

>A **primary token** describes the security context of the user account associated with the process.

- When you log in, the **Local Security Authority (LSA)** validates your credentials, and if they're correct, authenticates you and creates an access token for you. 
- This token becomes the primary token of your initial shell. Every child process inherits or duplicates that primary token.
- Every process has a primary token (and only one).
- The Windows Security Reference Monitor (SRM) uses the primary token for access checks when a thread interacts with a securable object.

>[!important] Every process has exactly one primary token. A process can't execute without an access token.

>[!important] You cannot "detach" a primary token from a running process and replace it with another one. You must create a new process.

>[!important] All processes in a logon session have the same primary access token.
### Impersonation tokens

>An **impersonation token** is attached to a thread and allows it to act as another security principal.

>[!important] Impersonation tokens can be attached to threads, but not processes.

>[!important] Impersonation tokens can't be used to start a process. To start a process as another user, you must **duplicate** the impersonation token into a **primary token** using `DuplicateTokenEx()`, then call `CreateProcessWithTokenW()` or `CreateProcessAsUserW()`.

- Impersonation tokens are used heavily in client-server scenarios. Such as when a client connects to a service, the service authenticates the client, and then the service *impersonates* the client. The service acts as if it were the client.
- Impersonation tokens usually come from **authentication events**, such as:
	- A client authenticating to a named pipe
	- An RPC client connecting to a server
	- A COM client invoking a method
	- SMB authentication
	- Explicit calls such as `LogonUser` or `DuplicateTokenEx`

>[!important] If an impersonation token is attached to a thread, it overrides the thread's primary token during access checks.

- A single process can simultaneously act as itself in one thread and another user in another thread.
- If a thread has an impersonation token, access checks use it instead of the process token.
- If no impersonation token is present, the thread falls back to the process's primary token.

>[!example]+
> - An IIS worker process impersonating a remote user.
> - An SMB server thread impersonating a network client.

#### Impersonation levels

Not all impersonation tokens are equally powerful. 
Windows defines four [impersonation levels](https://learn.microsoft.com/en-us/windows/win32/secauthz/impersonation-levels):

- **`SecurityAnonymous`**
	- The server can't impersonate or identify the client.
	- The impersonation token doesn't contain any information about the client, and the client is anonymous to the server. 
	- Rare in practice.
- **`SecurityIdentification`**
	- The server can get the identity and privileges of the client, but can't impersonate the client.
	- This is for identity inspection — but not acting as the client.
- **`SecurityImpersonation`**
	- The server can impersonate the client's security context on the local system.
	- This is the most common level of impersonation, and what people usually mean by an "impersonation token".
- **`SecurityDelegation`**
	- The server can impersonate the client's security context on remote systems.

>[!important] Only **`SecurityImpersonation`** and above allow meaningful access operations. `SecurityIdentification` allows inspecting the identity, but all access checks using that token will fail.

## Impersonation

>**Impersonation** is the ability of a thread to execute under a security context that is different from the primary security context of the process that owns the thread.

- Impersonation exists to support the Windows **client-server execution model**.
	- Windows services (e.g., SMB, RPC, COM servers) operate as **multi-client servers**.
	- Each client may have **different permissions and identities**.
	- The server must enforce **per-client authorization**, not its own.
- To achieve this, the server temporarily executes in the client's security context when performing operations on the client's behalf.

### How impersonation works

1. A client authenticates to a server using a mechanism such as NTLM or Kerberos.
2. Upon successful authentication, the LSASS security subsystem creates an **access token** on the server. This token represents the authenticated client identity.
	- It contains the user SID, group memberships, privileges, and logon type (e.g., network logon).
3. The server attaches this token to one of its threads via an impersonation API.
4. Once impersonation is active, any resource access performed by that thread is evaluated against the **client's identity**, not the server's.
	- Examples include file access, registry access, and named pipe operations.
5. After completing the operation, the thread returns to the original process identity (`RevertToSelf()`).

>[!note]+ A token can be attached to a thread via APIs such as:
> - `ImpersonateLoggedOnUser()` — Impersonate an arbitrary logged-on user given their token. 
> - `RpcImpersonateClient()` — Impersonate an RPC client.
> - `ImpersonateNamedPipeClient()` — Impersonate whoever connected to a named pipe.
> - `SetThreadToken()` — Directly assign a token to a thread.

>[!note] The client does not control impersonation. The server decides when and how to use their token.

### `SeImpersonatePrivilege` and impersonation

- To actually *use* an impersonation token for resource access (i.e., at `SecurityImpersonation` level or higher), the server process must hold **`SeImpersonatePrivilege`**.
- Without it, Windows silently downgrades the token to `SecurityIdentification` — you can see who it belongs to, but you can't act as them.

>[!note] See [[Windows privileges#`SeImpersonatePrivilege` and `SeAssignPrimaryTokenPrivilege`]] for details on which accounts hold this privilege.

### Token duplication

- An **impersonation token** cannot be used to start a new process. Only a **primary token** can be assigned to a process.
- To convert between token types, use `DuplicateTokenEx()`:
	- Impersonation → Primary: needed to spawn a process as the impersonated user.
	- Primary → Impersonation: needed to assign it to a thread.

- Once you have a primary token, you can create a process under it using:
	- `CreateProcessWithTokenW()` — requires `SeImpersonatePrivilege`.
	- `CreateProcessAsUserW()` — requires `SeAssignPrimaryTokenPrivilege`.

>[!bug] This is the core of every potato-family privilege escalation: capture a `SYSTEM` impersonation token → duplicate to primary → spawn a `SYSTEM` process.

>[!note] See [[JuicyPotato]], [[PrintSpoofer]], [[RoguePotato]], [[GodPotato]], and [[SweetPotato]] for practical exploitation of this chain.

## References and further reading

- [`Access tokens — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/secauthz/access-tokens)
- [`Restricted Tokens — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/secauthz/restricted-tokens)
- [`Impersonation Levels (Authorization) — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/secauthz/impersonation-levels)
- [`Client Impersonation (Authorization) — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/secauthz/client-impersonation)
- [`DuplicateTokenEx function — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-duplicatetokenex)