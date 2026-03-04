---
created: 15-02-2026
---
```
Hello, act as a Windows and Cybersecurity expert.
Could you please tell me Windows privileges and permissions? Stuff like owners, ACEs, security decriptors, securable objects, etc.

- Be technical, accurate. Explain to someone who is not bad at CS but still needs to learn a lot about Windows.
- Be really detailed and accurate. Please, give links to relevant Microsoft documentation.

USE NARRATIVE STYLE (full sentenses, explanations), do not throw bullet points at me, please
```

## SRM

>A **[Security Reference Monitor (SRM)](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/windows-kernel-mode-security-reference-monitor)** is a core kernel-mode component of the Windows security architecture responsible for enforcing access control policies across the operating system. 


>[!important]+ SRM
>The component of the system responsible for defining the access token data structure to represent a security context, performing security access checks on objects, manipulating privileges (user rights), and generating audit messages is called a **Security Reference Monitor (SRM)** — the component of the Windows executive (`Ntoskrnl.exe`).
## Security principals

>A **[security principal](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-principals)** is any entity that can be authenticated by the operating system, such as a user account, computer account, or security groups of these accounts. Once authenticated, a principal can be granted or denied access to [securable objects](https://learn.microsoft.com/en-us/windows/win32/secauthz/securable-objects) (files, registry keys, processes, etc.).


Security principals can be:

- **User accounts** 
	- Represent either individual human users or service identities.

- **Computer accounts** 
	- Represent machines in a domain (e.g., `MACHINE$` accounts in Active Directory).
	- Computer accounts are used for machine-to-machine authentication, particularly in Kerberos authentication.

- **Security groups**
	- A set of security principals. 
	- Groups are used to simplify permission management: instead of assigning permissions individually to every user, you can add users to a group and then assign permissions to that group. 
	- Since a security group is itself a security principal, this means groups can be nested — you can add a group to another group.

>[!important] Each security principal uniquely identified by a **Security Identifier (SID)**.

## Security Identifiers

>A **[SID (Security Identifier)](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-identifiers)** is a unique, immutable binary value that identifies a security principal.

- Internally, Windows doesn't use account names to make access control decisions, but SIDs.
- A SID **never changes during the lifetime of the security principal**. If you rename a user account, its SID stays the same. 
- ACEs (Access Control Entries) reference SIDs, not names.

### SID structure

SIDs are stored as binary structures, but commonly represented in a standardized string format for readability:

```
S-R-X-Y1-Y2-...-Yn
```

>[!example]+
> ```
> S-1-5-21-3623811015-3361044348-30300820-1013
> ```

| Component | Description                                                                                                                 | Example                          |
| --------- | --------------------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| `S`       | Indicates that the string is a SID.                                                                                         | -                                |
| `R`       | **Revision level**; currently always `1`.                                                                                   | -                                |
| `X`       | **Identifier authority**; indicates the entity that issued the SID (e.g., "NT Authority").                                  | `5`                              |
| `Y`       | A series of subauthority values (where `n` is the number of values); represents the **domain** or **machine identifier**.   | `3623811015-3361044348-30300820` |
| `Yn`      | **Relative Identifier (RID)**, the last subauthority value; uniquely identifies the principal within the domain or computer | `1013`                           |

#### Identifier authority

The **identifier authority** indicates which authority issued the SID namespace.
Common values:

| Authority | Formal name     | Description                                                                   |
| --------- | --------------- | ----------------------------------------------------------------------------- |
| `0`       | Null Authority  | Used for `S-1-0-0` (Nobody), represents nothing.                              |
| `1`       | World Authority | Used for `S-1-1-0` (Everyone).                                                |
| `5`       | NT Authority    | Used by the Windows security subsystem. Most Windows SIDs begin with `S-1-5`. |
- `S-1-1-0` → World Authority → Everyone
- `S-1-5-18` → NT Authority → Local System

#### Domain or machine ID

For most local and domain accounts, SIDs follow this pattern:

```
S-1-5-21-<identifier>-<identifier>-<identifier>-RID
```

- On a domain-joined system, these three large numeric values following `21` form the **Active Directory domain SID**.
- On a standalone machine, they represent the **local machine SID**.

All accounts within the same domain (or local machine) share the same domain identifier portion. What makes them unique is the **RID**.
#### Relative Identifier (RID)

>The **RID (Relative Identifier)** is the last subauthority value in the SID. It uniquely identifies a security principal within its domain or local machine.

>[!example]+
> ```
> S-1-5-21-3623811015-3361044348-30300820-1013
>                                            ↑
>                                           RID
> ```

The RID is the only portion that changes when new accounts are created within the same domain or machine.

- On a standalone Windows system, the first manually create local user typically receives RID `1000`. The next receives `1001`, and so on.
- In Active Directory environments, RIDs are allocated in pools by DCs (Domain Controllers).

Certain accounts and groups have **well-known RIDs** that are consistent across all Windows installations (within their domain scope):

| RID   | Account                    |
| ----- | -------------------------- |
| `500` | Administrator              |
| `501` | Guest                      |
| `512` | Domain Admins              |
| `513` | Domain Users               |
| `514` | Domain Guest               |
| `515` | Domain Computers           |
| `516` | Domain Controllers         |
| `544` | Administrators local group |
| `545` | Users local group          |

- `500` and `501` refer to the built-in Administrator and Guest accounts within a given domain or local SAM.
- `512–516` exist only in Active Directory domains.
- `544` and `545` are RIDs within the **Built-in domain** (`S-1-5-32`), which is a special namespace for built-in local groups.

>[!example] For example, `S-1-5-32-544` represents the local `Administrators` group.

>[!note] See [`Security identifiers — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-identifiers) for a full list.
### Well-known SIDs

In addition to domain-specific SIDs, Windows defines **well-known SIDs** that are constant across all systems. They do not depend on a domain identifier.

| Well-known SID          | Security principal                  | Description                                                                                                                                                  |
| ----------------------- | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `S-1-0-0`               | Nobody                              | No security principal.<br>This appears in some security logs when the system can't determine who performed an action.                                        |
| `S-1-1-0`               | Everyone (world)                    | A group that includes all users — anonymous users, guests, authenticated users — literally everyone.<br>Any security principal can exercise this permission. |
| `S-1-2-0`               | Local                               | Users who have logged in locally (those physically present at the console); doesn't include users connected remotely.                                        |
| `S-1-5-11`              | Authenticated users                 | A groups that includes all users who have successfully authenticated to the system.<br>Doesn't include anonymous or guest users.                             |
| `S-1-5-18`              | Local System (`SYSTEM`)             | A service account used by the operating system itself; the **highest privilege level** on a standalone machine.                                              |
| `S-1-5-19`              | Local Service (`LOCAL SERVICE`)     | A service account with minimal privileges; used for services that don't need network access.                                                                 |
| `S-1-5-20`              | Network Service (`NETWORK SERVICE`) | Another service account with minimal local privileges but with a network authentication capability; used for services that do need network access.           |

>[!note] Domain-joined computers have both a domain SID (assigned when the computer joined the domain) and a local machine SID (unique to that computer).
>- Local accounts use the local machine SID base. 
>- Domain accounts use the domain SID base. 
## Securable objects

>A [securable object](https://learn.microsoft.com/en-us/windows/win32/secauthz/securable-objects) is an object that can have a security descriptor.

- All *named* Windows objects are securable. 
- Some unnamed objects, such as [_process_](https://learn.microsoft.com/en-us/windows/desktop/SecGloss/p-gly) and thread objects, can have security descriptors too.

>A [security descriptor](https://learn.microsoft.com/en-us/windows/win32/secauthz/security-descriptors) is a data structure that defines security attributes of a securable object.

- A security descriptor determines who can access the object and how, by specifying:
	- The **SID** of the object's owner, who has the right to modify the object's security settings.
	- The SID of the group associated with the object, used for POSIX compatibility.
	- A **Discretionary Access Control List (DACL)** that controls which users or groups can access the object and what actions they can perform (e.g., read, write, execute).
	- A **System Access Control List (SACL)** that defines auditing rules to log access attempts (successful or failed) to the object.

>[!note] Security Descriptors are stored in binary format in the system (e.g., NTFS metadata or Active Directory), but can be represented in human-readable text using **Security Descriptor Definition Language (SDDL)**.

- Conceptually, every time a thread attempts to open a handle to a securable object, the Windows SRM evaluates:
	1. The object’s security descriptor.
	2. The caller’s access token.
	3. The requested access mask.
- The result is either access granted or denied.


## Access tokens 

>An [access token](https://learn.microsoft.com/en-us/windows/win32/secauthz/access-tokens) is a kernel object that describes a security context of a process or thread.

- Access tokens are created by the **Local Security Authority (LSA)** during logon and attached to a process. 
- A token includes information about the identity and privileges of the user account associated with the process or thread. 
- An access token is an immutable structure once created (you can enable/disable privileges, but you cannot arbitrarily add SIDs unless you create a new token via special APIs such as `CreateRestrictedToken`).
- The Windows Security Reference Monitor (SRM) uses tokens during access checks against securable objects.

- The information access tokens carry includes:
	- The SID for the user account.
	- SIDs for the groups to which the user belongs.
	- A *logon SID* (uniquely identifies a logon session; is used to isolate session objects).
	- A list of *privileges* held by the user or the user's groups.
	- An *owner SID* (the default owner SID used when the process creates securable objects; usually the user SID).
	- The SID for the primary group (for POSIX compatibility).
	- The *default DACL* the system uses when the user creates a securable object without specifying a security descriptor.
	- The *source* of an access token.
	- Whether the token is a *primary* or *impersonation* token.
	- (Optional) A list of *[restricted tokens](https://learn.microsoft.com/en-us/windows/win32/secauthz/restricted-tokens)* (used for sandboxing).
	- Current impersonation levels (only for impersonation tokens).
	- Etc.

- A *logon SID* unique identifies a logon session and used to isolate session objects.

>[!note] The *token source* indicates which component created the token. It doesn't directly affect access decisions, and mostly used for auditing and diagnostics.
>- `"User32"` -> interactive logon
>- `"NtLmSsp"` -> NTLM authentication package
>- `"Kerberos"` -> Kerberos authentication
>- `"SecLogo"` -> Secondary logon service (`RunAs`)

Tokens in Windows can be **primary** and **impersonation**. 

### Primary tokens

>A **primary token** describes the security context of the user account associated with the process.

- When you log in, the **Local Security Authority (LSA)** validates your credentials, and if they're correct, authenticates you and creates an access token for you. 
- This tokens becomes the primary token of your initial shell. Every child process inherits or duplicates that primary token.
- Every process has a primary token (and only one).
- The Windows Security Reference Monitor (SRM) uses the primary token for access checks when a thread interacts with a securable object.

>[!important] Every process has exactly one primary token. A process can't execute without an access token.

>[!important] You cannot “detach” a primary token from a running process and replace it with another one. You must create a new process.

>[!important] All processes in a logon session have the same primary access token.
### Impersonation tokens

>An **impersonation token** is attached to a thread and allows it to act as another security principal.

>[!important] Impersonation tokens can't be attached to threads, but not processes.

>[!important] Impersonation tokens can't be used to start a process. 

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
- If no impersonation token is present, the thread falls back to the process’s primary token.

>[!example]+
> - An IIS worker process impersonating a remote user.
> - An SMB server thread impersonating a network client.

#### Impersonation levels

Not all impersonation tokens are equally powerful. Windows defines four [impersonation levels](https://learn.microsoft.com/en-us/windows/win32/secauthz/impersonation-levels):

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

## High-level security architecture

The Windows security model is built on a principle of separation of concerns. User-facing components collect credentials, security subsystems validate them, and kernel-level components enforce access decisions. T

### LSA


>**LSA (Local Security Authority)** is the security subsystem in Windows responsible for creating access tokens, managing authentication policies, auditing policy enforcement, creating logon sessions, assigning privileges, and storing secrets.

>**LSASS (Local Security Authority Subsystem Service)** is the **user-mode process** that implements LSA. It's the only process that can **issue, modify, and destroy access tokens, audit security events, and manage security policies**.

- **Path: `C:\Windows\System32\lsass.exe`.**
- **LSASS** runs as **`NT AUTHORITY\SYSTEM`** and starts early at boot. 

>[!note]+ PPL
>LSASS is protected by **Protected Process Light (PPL)** on modern Windows systems (e.g., `lsass.exe` is a **PPL with `WIN32K` protection level**). This makes it harder for low‑privilege malware to inject code. 

- LSASS hosts **authentication packages** and **SSPs (Security Support Providers)**.
- LSASS communicates with the kernel via SRM (Security Reference Monitor).
- LSASS stores credentials, hashes, and Kerberos tickets vis LSA secrets.

Key components of LSASS include:

- **Authentication Packages**
	- loaded DLLs (`Kerberos.dll`, `NTLM.dll`, `Negotiate.dll`).
- **Logon Session Manager**
	- maintains a table of **LUID → Logon Session** structures.
- **Token Manager**
	- builds **access tokens** from the logon session data.
- **Audit Subsystem** 
	- writes events to the Security Event Log.


>[!note]+ Logon session 
>A **logon session** is a session that begins when a user authentication is successful and ends when the user logs off of the system. 

- `LUID` – 64‑bit locally unique identifier for each logon session.
- `SECURITY_LOGON_SESSION_DATA` – exposed via `LsaQueryLogonSessionData`. Contains user SID, logon type, authentication package, logon time, etc.
- `TOKEN` – kernel object representing the security context

The LSA reads security policies from the **registry** (`HKLM\System\CurrentControlSet\Control\Lsa`) and from **Group Policy** (`Computer Configuration → Windows Settings → Security Settings`).



- For **local** accounts, LSA queries the **SAM** database (via `SamIGetUserInformation`).
- For **domain** accounts, LSA contacts the **Netlogon** service, which in turn talks to the **Domain Controller (KDC)**.

LSA stores **cached domain credentials** (NTLM hash of the password) in the **LSA Secrets** store, encrypted with **DPAPI** using the machine key. This enables **CachedInteractive** logons when the DC is unavailable.


Every successful or failed logon generates an event in the **Security** log (Event ID 4624, 4625, 4776, etc.). The LSA formats the event and hands it to the **Event Log Service**.


---

Authentication packages are DLLs loaded by LSASS that:
- Understand specific credential formats
- Validate credentials
- Return success/failure
- Provide identity data for token creation
Configured at: `HKLM\SYSTEM\CurrentControlSet\Control\Lsa`


- `msv1_0.dll` (NTLM)
	- NTML authentication 
	- Local account logons
	- NT hash validation
	- Challenge-response logic
	- Local logons and NTLM network authentication; fallback when Kerberos is unavailable.
- `kerberos.dll` (Kerberos)
	- Kerberos
	- TGT and TGS tickets
	- PAC validation
	- Domain authentication
	- Domain logos
	- Service authenticaoitn
	- Mutual authentication
- `negotiate.dll` (`SPNEGO`)
	- Does not authenticate by itself but negotiates which protocol to use; chooses between Kerberos and NTLM. 
	- Used in SMB, HTTP, WinRM, RDP, etc.
- `tspkg.dll` (terminal services)
	- Used for RDP authentication and `RemoteInteractive` logons
	- Works with NTML and Kerberos.


What is PAC?

### SAM


### Winlogon

>**Winlogon** is the **session manager for interactive logons**.

- Winlogon (`winlogon.exe`) is the first user-mode process that runs after the kernel boots. 
- It's responsible for:
	- Displaying the secure desktop (`Ctrl + Alt + Del`).
	- Loading the **Credential Provider** (or legacy GINA).
	- Starting the user’s **Shell** (`explorer.exe`) after a successful logon.
	- Handling **Lock/Unlock**, **Fast User Switching**, **Logoff**, and **Shutdown** events.

>[!note] Winlogon is the only user-mode process allowed to receive `Ctrl + Alt + Del`.

Winlogon includes:
- _Winlogon Notification Packages_ (e.g., `Userenv.dll`, `SAS.dll`) – receive **SAS** (Secure Attention Sequence) notifications; 
- _Winlogon Hooks_ (registry `HKLM\Software\Microsoft\Windows NT\CurrentVersion\Winlogon\Notify`) – used by third‑party software (e.g., smart‑card middleware).

It never validates passwords itself; it merely forwards the credential blob to **LSA**. All cryptographic checks happen inside the authentication packages.

❌ It does not authenticate  
❌ It does not validate passwords  
❌ It does not create tokens


### Credential providers

>**Credential Providers** are UI plug‑ins that collect authentication data from the user. 

- Implement the COM interfaces `ICredentialProvider` and `ICredentialProviderCredential`. The OS loads each provider, asks it to enumerate **tiles** (the UI elements you see on the logon screen), and then calls `GetSerialization` on the selected tile.

>[!note] Credential providers replace the old **GINA** (Graphical Identification and Authentication) DLL from Windows XP onward.

Credential Providers are **pluggable COM objects** that:
- Display authentication UI
- Collect credentials
- Package credentials for LSA

Built-in providers include:

- `PasswordProvider.dll`
	- Classic username/password.
- `SmartCardProvider.dll`
	- Smart‑card + PIN.
- `HelloProvider.dll` 
	- Windows Hello (biometrics, PIN).

Can be extended with third‑party vendors (e.g., Duo, RSA SecurID) ship their own providers that can perform **pre‑authentication** (e.g., push notification) before handing the credential to LSA.

The provider runs in the **Winlogon** process (`SYSTEM`). A compromised provider can **exfiltrate** the clear‑text password before it ever reaches LSA. This is why the OS enforces **code signing** and **kernel‑mode driver signing** for providers on domain‑joined machines.

`HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Authentication\Credential Providers\<Provider GUID>` – contains `DllPath`, `ProviderFlags`, etc.

Data flow:

```
User input → Credential Provider → Winlogon → LSASS
```

```
- Bash history lifecycle
- How it works
- On shell exit (tell me more)
	- These cause `bash_history` to be written:
		- `^D`, exit, logout
		- `SIGTERM`, `SIGHUP` bash process
		- Killing (even `SIGKILL`) parent SSH process
		- Exit windoring environment, shutdown, reboot
	- Anything else? No bash history update

```
### Security support providers (SSPs)

SSPs implement **security protocols** used by applications.

They provide:
- Authentication 
- Message signing
- Encryption

Used by:
- SMB
- LDAP
- HTTP
- RPC

Common SSPs:

| SSP       | Protocol              |
| --------- | --------------------- |
| Kerberos  | Kerberos              |
| NTLM      | NTLM                  |
| Negotiate | Protocol selection    |
| Schannel  | TLS/SSL               |
| CredSSP   | Credential delegation |

### Netlogon

Netlogon is a service responsible for maintaining secure channel to DC and performing machine authentication.

This note doesn't talk about AD so we skip this


### DPAPI

## Logon process

Occurs when a user logs on directly at the local console using a keyboard and mouse. This includes local logons, domain logons, and logons via smart cards or biometrics.

>[!note] See [`Windows logon scenarios — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/security/windows-authentication/windows-logon-scenarios).


At a high level, local interactive logon works like this:

1. **Secure Attention Sequence (`Ctrl+Alt+Del`)**
	- The logon process begins with the **Secure Authentication Sequence (SAS)** key combination, typically `Ctrl+Alt+Del`.
	- The SAS can be receives exclusively by Winlogon and no other processes. This is enforced so that no user-mode processes can spoof the logon UI. 
	- Winlogon launches the `LogonUI.exe`, which loads registered **Credential Providers**.

2. **Credential Providers and LogonUI**
	- Credential Providers are [COM](https://learn.microsoft.com/en-us/windows/win32/com/component-object-model--com--portal) components that gather credentials (username/password, smart card, PIN, biometric assertion), package credentials into a serialized format, and return a `CREDENTIAL_PROVIDER_CREDENTIAL_SERIALIZATION` structure.
	- This structure contains an authentication package ID (e.g., Kerberos, NTLM), serialized credentials blob, and logon type (interactive, unlock, etc.).
	- LogonUI does not validate credentials. It forwards them via an LPC/RPC channel to **Local Security Authority Subsystem Service (LSASS)**.

3. **Local Security Authority Subsystem Service (LSASS) and credential packages**
	- LSASS calls calls [`LsaLogonUser()`](https://learn.microsoft.com/en-us/windows/win32/api/ntsecapi/nf-ntsecapi-lsalogonuser) and sends the credential block to the selected authentication package. 
	- The package performs the verification:
		- Kerberos contacts a domain controller and obtains a TGT.
		- NTLM verifies password hash against SAM or domain controller.
	- If verification succeeds, the authentication package returns a structure that contains:
		- User SID
		- Domain SID
		- Group membership SIDs
		- Logon restrictions
		- Profile path
		- Logon type
		- Authentication ID (LUID seed)

4. **Logon session creation**
	- Upon successful authentication, LSASS creates a **logon session**.
	- Internally, it generates a **Locally Unique Identifier (LUID)** that identifies the logon session globally on that machine.
	- The LUID is stored in the eventual access token, LSASS internal logon session table, and audit logs (Event ID `4624`).
	- LSASS also creates a logon SID in the form `S-1-5-5-X-Y`, unique per logon session. It's primarily used for session isolation.

5. **Access token construction**
	- LSASS now calls `NtCreateToken()` to create an access token.
	- Normally, only LSASS (running as `SYSTEM` can create arbitrary tokens).

6. **Initial user process**
	- After token creation, Winlogon calls `CreateProcessAsUser()`. This API accepts the newly created primary token, creates a new `EPROCESS` kernel structure, and assigns the token pointer to `EPROCESS`->Token. 
	- The first process is typically `userinit.exe`, which loads user profile (registry hive under HKU), sets environment variables, and launches `explorer.exe`. Explorer inherits the same primary token.
	- From this point forward, all child processes either inherit the primary token, or duplicate it via `DuplicateTokenEx`.

## ACLs

>An **Access Control List (ACL)** is a list of **Access Control Entries (ACEs)**.

>Each ACE in an ACL identifies a **trustee** and specifies the access rights allowed, denied, or audited for that trustee.

>A **[trustee](https://learn.microsoft.com/en-us/windows/win32/secauthz/trustees)** is the user account, group account, or logon session to which an ACE applies. Each ACE in an ACL has one SID that identifies a trustee.

The security descriptor for a securable object can contain two types of ACLs: a DACL and an SACL.

### DACL

>A **Discretionary Access Control List (DACL)** identifies the trustees that are allowed or denied access to a securable object.

- When a process tries to access a securable object, the system checks the ACEs in the object's DACL to determine whether to grant access to it. 
- If the object doesn't have a DACL, the system grants full access to everyone.
- If the object's DACL has no ACEs, the system denies all attempts to access the object because the DACL doesn't allow any access rights. 
- The system checks the ACEs in sequence until it finds one or more ACEs that allow all the requested access rights, or until any of the requested access rights are denied.

When a process attempts to open a handle to an object:

1. The [Object Manager](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/windows-kernel-mode-object-manager) resolves the object.
2. The Security Reference Monitor (SRM) retrieves:
    - The caller’s access token
    - The object’s security descriptor
3. It extracts the DACL.
4. It performs the access check.
The algorithm is sequential:
- The DACL is evaluated in order.
- Each ACE is examined.
- If the SID matches one in the token:
    - If it is a deny ACE and overlaps with requested rights → immediate failure.
    - If it is an allow ACE → granted rights are accumulated.
Evaluation continues until:
- All requested rights are granted → success
- A deny ACE blocks → failure
- End of DACL reached without full grant → failure

>[!important] Null DACL vs empty DACL
>- **Null DACL** → No DACL present → Full access granted to everyone.
>- **Empty DACL** → DACL exists but contains no ACEs → No access granted to anyone.
### SACL

>A **System Access Control List (SACL)** allows administrators to log attempts to access a secured object. 

- Each ACE in an SACL specifies the types of access attempts by a specified trustee that cause the system to generate a record in the security event log.
- An ACE in an SACL can generate audit records when an access attempt fails, when it succeeds, or both.


## Types of logons in Windows

A **logon type** describes **how LSASS creates a logon session and access token**, not just _how a user logs in_.

Logon type defines:
- Where authentication happens (local vs. network)
- Which credentials are acceptable
- How the resulting token is restricted
- How the event is audited

| Logon Type                  | Value        | Description                                                       | Credentials Accepted                 | Token                                         | Examples                         |
| --------------------------- | ------------ | ----------------------------------------------------------------- | ------------------------------------ | --------------------------------------------- | -------------------------------- |
| **Interactive**             | `2`          | User logs on **locally at the console**                           | Password, Smartcard, Windows Hello   | Full interactive token, local groups enabled  | Keyboard login, physical console |
| **Network**                 | `3`          | Authentication over the **network only**                          | NTLM hash, Kerberos ticket, password | **Network token** (no local admin privileges) | SMB, PsExec, WinRM               |
| **Batch**                   | `4`          | Non-interactive execution by scheduler                            | Password (stored as LSA secret)      | Restricted, no desktop                        | Scheduled Tasks                  |
| **Service**                 | `5`          | Service startup authentication                                    | Password (LSA secret)                | Service token, no UI                          | Windows services                 |
| **Unlock**                  | `7`          | Unlock an already logged-in session                               | Cached credentials                   | Same token reused                             | Unlock workstation               |
| **NetworkCleartext**        | `8`          | Network logon using **plaintext password**                        | Plaintext password                   | Network token                                 | IIS Basic Auth                   |
| **NewCredentials**          | `9`          | Clone token, but use **different creds for outbound connections** | Password                             | Hybrid token                                  | `runas /netonly`                 |
| **RemoteInteractive**       | `10`         | Interactive logon via remote session                              | Password, Smartcard                  | Interactive + network                         | RDP                              |
| **CachedInteractive**       | `11`         | Local login using **cached domain creds**                         | Cached hash                          | Interactive token                             | Laptop offline login             |
| **CachedRemoteInteractive** | _(internal)_ | Cached version of RemoteInteractive                               | Cached creds                         | Same as RDP                                   | Auditing only                    |
| **CachedUnlock**            | _(internal)_ | Cached unlock of workstation                                      | Cached creds                         | Same token reused                             | Auditing only                    |




- [`Administrative tools and logon types — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/identity/securing-privileged-access/reference-tools-logon-types)



| Component                                    | Binary / Registry                                              | Primary Responsibility                                                                      | Typical Interaction                               |
| -------------------------------------------- | -------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| **Winlogon**                                 | `winlogon.exe`                                                 | UI for interactive logons, starts user session, loads user profile.                         | Calls Credential Provider → LSA.                  |
| **Credential Provider**                      | `CREDPROV*.dll` (e.g., `PasswordProvider.dll`)                 | Collects credentials (password, smart‑card, PIN).                                           | Returns credential blobs to Winlogon → LSA.       |
| **LSA (Local Security Authority)**           | `lsass.exe`                                                    | Central security authority; stores policies, manages logon sessions, creates access tokens. | Loads authentication packages, enforces policies. |
| **Authentication Packages**                  | `Kerberos.dll`, `NTLM.dll`, `Negotiate.dll`, `SspCredProv.dll` | Implements a specific auth protocol; validates credentials; builds token.                   | Called by LSA via `LsaLogonUser`.                 |
| **SAM (Security Account Manager)**           | `sam.dll` + `C:\Windows\System32\config\SAM`                   | Stores local user & group objects, password hashes (LM/NTLM).                               | Queried by LSA for local logons.                  |
| **Netlogon Service**                         | `netlogon.dll` (`netlogon.exe`)                                | Handles domain controller communication (secure channel, DC locator, password changes).     | Used for domain logons, trust validation.         |
| **Kerberos KDC (Domain Controller)**         | `kdc.exe` (part of `lsass.exe` on DC)                          | Issues Ticket‑Granting Tickets (TGT) and Service Tickets (TGS).                             | Receives AS‑REQ/AS‑REP, TGS‑REQ/TGS‑REP.          |
| **DPAPI (Data Protection API)**              | `crypt32.dll`                                                  | Encrypts/decrypts stored secrets (e.g., cached credentials, LSA secrets).                   | Used by Credential Manager, cached domain logons. |
| **Credential Guard**                         | `LsaIso.exe` (Isolated LSA)                                    | Isolates LSASS secrets in a virtual‑secure mode (VSM).                                      | Prevents LSASS memory dumping.                    |
| **Security Accounts Manager (SAM) Registry** | `HKLM\SAM` (protected)                                         | Holds local password hashes, account control flags.                                         | Accessed only by LSASS.                           |
| **Group Policy (SecPol)**                    | `secpol.msc` / `gpedit.msc`                                    | Centralizes security options (e.g., NTLM restrictions, Kerberos settings).                  | Applied at boot / logon.                          |




## Privileges

Permissions (DACLs) control access to specific objects.  
Privileges grant the ability to perform _system-level operations_, sometimes bypassing normal DACL enforcement entirely.

>A **[privilege](https://learn.microsoft.com/en-us/windows/win32/secauthz/privileges)** is a system-level right assigned to an account (or group) that allows the holder to preform sensitive operations that are not governed purely by DACL checks. 

- Privileges are stored in access tokens and evaluated by the kernel's SRM during specific security-sensitive operations.

- Privileges differ from access rights in two ways:

	- Privileges control access to system resources and system-related tasks, whereas access rights control access to securable objects.
	- A system administrator assigns privileges to user and group accounts, whereas the system grants or denies access to a securable object based on the access rights granted in the ACEs in the object's DACL.

 - Each system has an account database that stores the privileges held by user and group accounts. 
 - When a user logs on, the system produces an access token that contains a list of the user's privileges, including those granted to the user or to groups to which the user belongs. 

See [`User Rights Assignment — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/user-rights-assignment).

| Setting [Constant](https://docs.microsoft.com/en-us/windows/win32/secauthz/privilege-constants) | Setting Name                                                                                                                                                                                                 | Standard Assignment                                     | Description                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| SeNetworkLogonRight                                                                             | [Access this computer from the network](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/access-this-computer-from-the-network)                                  | Administrators, Authenticated Users                     | Determines which users can connect to the device from the network. This is required by network protocols such as SMB, NetBIOS, CIFS, and COM+.                                                                                                                                                                                                                                                                                       |
| SeRemoteInteractiveLogonRight                                                                   | [Allow log on through Remote Desktop Services](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/allow-log-on-through-remote-desktop-services)                    | Administrators, Remote Desktop Users                    | This policy setting determines which users or groups can access the login screen of a remote device through a Remote Desktop Services connection. A user can establish a Remote Desktop Services connection to a particular server but not be able to log on to the console of that same server.                                                                                                                                     |
| SeBackupPrivilege                                                                               | [Back up files and directories](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/back-up-files-and-directories)                                                  | Administrators                                          | This user right determines which users can bypass file and directory, registry, and other persistent object permissions for the purposes of backing up the system.                                                                                                                                                                                                                                                                   |
| SeSecurityPrivilege                                                                             | [Manage auditing and security log](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/manage-auditing-and-security-log)                                            | Administrators                                          | This policy setting determines which users can specify object access audit options for individual resources such as files, Active Directory objects, and registry keys. These objects specify their system access control lists (SACL). A user assigned this user right can also view and clear the Security log in Event Viewer.                                                                                                    |
| SeTakeOwnershipPrivilege                                                                        | [Take ownership of files or other objects](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/take-ownership-of-files-or-other-objects)                            | Administrators                                          | This policy setting determines which users can take ownership of any securable object in the device, including Active Directory objects, NTFS files and folders, printers, registry keys, services, processes, and threads.                                                                                                                                                                                                          |
| SeDebugPrivilege                                                                                | [Debug programs](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/debug-programs)                                                                                | Administrators                                          | This policy setting determines which users can attach to or open any process, even a process they do not own. Developers who are debugging their applications do not need this user right. Developers who are debugging new system components need this user right. This user right provides access to sensitive and critical operating system components.                                                                           |
| SeImpersonatePrivilege                                                                          | [Impersonate a client after authentication](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/impersonate-a-client-after-authentication)                          | Administrators, Local Service, Network Service, Service | This policy setting determines which programs are allowed to impersonate a user or another specified account and act on behalf of the user.                                                                                                                                                                                                                                                                                          |
| SeLoadDriverPrivilege                                                                           | [Load and unload device drivers](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/load-and-unload-device-drivers)                                                | Administrators                                          | This policy setting determines which users can dynamically load and unload device drivers. This user right is not required if a signed driver for the new hardware already exists in the driver.cab file on the device. Device drivers run as highly privileged code.                                                                                                                                                                |
| SeRestorePrivilege                                                                              | [Restore files and directories](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/restore-files-and-directories)                                                  | Administrators                                          | This security setting determines which users can bypass file, directory, registry, and other persistent object permissions when they restore backed up files and directories. It determines which users can set valid security principals as the owner of an object.                                                                                                                                                                 |
| SeTcbPrivilege                                                                                  | [Act as part of the operating system](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/act-as-part-of-the-operating-system) | Administrators, Local Service, Network Service, Service | This security setting determines whether a process can assume the identity of any user and, through this, obtain access to resources that the targeted user is permitted to access (impersonation). This may be assigned to antivirus or backup tools that need the ability to access all system files for scans or backups. This privilege should be reserved for service accounts requiring this access for legitimate activities. |
### Group privileges 

Windows contains many groups that grant their members powerful rights and privileges. Many of these can be abused to escalate privileges on both a standalone Windows host and within an Active Directory domain environment. Ultimately, these may be used to gain Domain Admin, local administrator, or SYSTEM privileges on a Windows workstation, server, or Domain Controller (DC). Some of these groups are listed below.

| **Group**                   | **Description**                                                                                                                                                                                                                                                                                                                                                                                               |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Default Administrators      | Domain Admins and Enterprise Admins are "super" groups.                                                                                                                                                                                                                                                                                                                                                       |
| Server Operators            | Members can modify services, access SMB shares, and backup files.                                                                                                                                                                                                                                                                                                                                             |
| Backup Operators            | Members are allowed to log onto DCs locally and should be considered Domain Admins. They can make shadow copies of the SAM/NTDS database, read the registry remotely, and access the file system on the DC via SMB. This group is sometimes added to the local Backup Operators group on non-DCs.                                                                                                             |
| Print Operators             | Members can log on to DCs locally and "trick" Windows into loading a malicious driver.                                                                                                                                                                                                                                                                                                                        |
| Hyper-V Administrators      | If there are virtual DCs, any virtualization admins, such as members of Hyper-V Administrators, should be considered Domain Admins.                                                                                                                                                                                                                                                                           |
| Account Operators           | Members can modify non-protected accounts and groups in the domain.                                                                                                                                                                                                                                                                                                                                           |
| Remote Desktop Users        | Members are not given any useful permissions by default but are often granted additional rights such as `Allow Login Through Remote Desktop Services` and can move laterally using the RDP protocol.                                                                                                                                                                                                          |
| Remote Management Users     | Members can log on to DCs with PSRemoting (This group is sometimes added to the local remote management group on non-DCs).                                                                                                                                                                                                                                                                                    |
| Group Policy Creator Owners | Members can create new GPOs but would need to be delegated additional permissions to link GPOs to a container such as a domain or OU.                                                                                                                                                                                                                                                                         |
| Schema Admins               | Members can modify the Active Directory schema structure and backdoor any to-be-created Group/GPO by adding a compromised account to the default object ACL.                                                                                                                                                                                                                                                  |
| DNS Admins                  | Members can load a DLL on a DC, but do not have the necessary permissions to restart the DNS server. They can load a malicious DLL and wait for a reboot as a persistence mechanism. Loading a DLL will often result in the service crashing. A more reliable way to exploit this group is to [create a WPAD record](https://web.archive.org/web/20231115070425/https://cube0x0.github.io/Pocing-Beyond-DA/). |

## References and further reading

- [`Administrative tools and logon types — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/identity/securing-privileged-access/reference-tools-logon-types)
- [`SECURITY_LOGON_TYPE enumeration (ntsecapi.h) — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/api/ntsecapi/ne-ntsecapi-security_logon_type)
- [`Local Security Authority Subsystem Service — Wikipedia`](https://en.wikipedia.org/wiki/Local_Security_Authority_Subsystem_Service)
- [`Internal Components — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-azod/d28d536d-3973-4c8d-b2c9-989e3a8ba3c5)


- [`Interactive Authentication — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/secauthn/interactive-authentication)



- [`LSA Authentication — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/secauthn/lsa-authentication)

- [`LSA Logon Sessions — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/secauthn/lsa-logon-sessions)
- [`LSA Authentication Model`](https://learn.microsoft.com/en-us/windows/win32/secauthn/lsa-authentication-model)

- [`Authentication Packages — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/secauthn/authentication-packages)

- [`Access tokens — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/secauthz/access-tokens)
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

# drafts

>[!tip]
>Look for `SeImpersonatePrivilege` or `SeAssignPrimaryToken`. If you see these, **Potato** attacks (Juicy/Rotten/PrintSpoofer) are likely on the table.
## Windows privileges

On a typical domain or local standard user account, you usually see:

|Privilege|Meaning|State|
|---|---|---|
|**SeChangeNotifyPrivilege**|Bypass traverse checking|Enabled|
|**SeIncreaseWorkingSetPrivilege**|Increase process working set|Disabled|

- **SeChangeNotifyPrivilege** is granted to _Everyone_ by default.
    
- Most other powerful privileges are **not present at all**, not just disabled.



---
- **SeDebugPrivilege** – Debug other processes (very powerful)
    
- **SeImpersonatePrivilege** – Impersonate tokens (Potato-style attacks)
    
- **SeAssignPrimaryTokenPrivilege**
    
- **SeIncreaseQuotaPrivilege**
    
- **SeBackupPrivilege**
    
- **SeRestorePrivilege**
    
- **SeTakeOwnershipPrivilege**
    
- **SeLoadDriverPrivilege**
    
- **SeSecurityPrivilege**
    
- **SeSystemtimePrivilege**
    
- **SeShutdownPrivilege**
    
- **SeUndockPrivilege**
    
- **SeManageVolumePrivilege**
    
- **SeCreateSymbolicLinkPrivilege**

These are normally assigned to:

- Administrators
    
- LocalSystem
    
- LocalService / NetworkService
    
- Service accounts

---

**SeImpersonatePrivilege**: This is one of the most powerful privileges for local privilege escalation. It allows a process to impersonate any client's security context after obtaining a handle to their token. This privilege is exploitable through various "potato" attacks (PrintSpoofer, GodPotato, JuicyPotato, etc.) that trick a privileged process into connecting to your controlled endpoint, giving you an impersonation token with SYSTEM privileges.

**SeAssignPrimaryPrivilege**: This privilege allows a process to assign the primary token of a new process. Combined with SeImpersonatePrivilege, this enables spawning processes as any user.

**SeBackupPrivilege**: This privilege allows reading any file regardless of ACL. You can use this to read protected files like SAM and SYSTEM registry hives, extract LSA secrets, or read any file on the system. The attack typically involves creating a shadow copy or using specialized backup APIs to copy protected files.

**SeRestorePrivilege**: This privilege allows writing to any file regardless of ACL. You can use this to replace system files, modify registry hives, or overwrite executable files that run with higher privileges.

**SeDebugPrivilege**: This privilege allows debugging and adjusting the memory of any process. You can use this to inject code into privileged processes, dump process memory to extract credentials, or use tools like Mimikatz.

**SeTakeOwnershipPrivilege**: This privilege allows taking ownership of any object. Combined with the ability to modify permissions (which administrators typically have), you can gain full control over any securable object.

**SeLoadDriverPrivilege**: This privilege allows loading and unloading device drivers. You can load a malicious driver to gain kernel-level access, though modern Windows has mitigations requiring driver signing.

**SeCreateTokenPrivilege**: This extremely powerful privilege allows creating tokens with arbitrary contents. With this privilege, you can create a token with any desired privileges and group memberships.

**SeTcbPrivilege**: Acting as part of the trusted computer base, this privilege allows creating tokens and other privileged operations.