---
created: 06-01-2026
---
## Windows security principals

Windows security model revolves around **security principals**.

>A **[security principal](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-principals)** is any entity that can authenticate to Windows and be assigned permissions.

Security principals include:

- **Users**
	- Human or service identities (e.g., `Administrator`, `Guest`).
	- Used for interactive logins or service execution. 
    
- **Groups**
	- Collections of security principals, such as users, computers, or other groups (e.g., `Administrators`, `Users`).
	- Used to simplify permission management by aggregating multiple principals under a single identity.
    
- **Computers**
	- Machine accounts in domains (e.g., `MACHINE$` in Active Directory).
	- Used for authentication and access control in AD environments.
    
- **Services**
	- Background processes (e.g., `SYSTEM`, `NETWORK SERVICE`).
    
- **Special system identities**
	- Built-in accounts with unique privileges (e.g., `LocalSystem`, `Authenticated Users`).

Think of a security principal as an identity that the OS recognizes and can make access control decisions about. 

Every security principal has two key representations:
- **SID (Security Identifier)** — a unique, binary identifier assigned at creation time; the "true identity" that the OS uses internally.
- **Access token** — a runtime object created at logon; the token contains the principal's SID, group memberships, privilege assignments, and other information. This is what Windows *actually* checks when access decisions are made.

>[!note] For more about access tokens, see [[_Windows_security#Access tokens]].
## SIDs (Security Identifiers)

>A **SID (Security Identifier)** is a unique, immutable binary value used to identify a security principal, such as a user account, computer account, or security group.

- A SID of a security principal **never changes** throughout its entire lifetime. If you rename an account, its SID stays the same.
- Permissions are assigned to SIDs, not usernames.
- If you delete a security principal and recreate it with the exact same name, the new principal; will receive a **different SID** and lose access to resources previously granted to the old principal.
- ACLs pointing to deleted principals are not automatically deleted. Whoever is assigned the same SID receives all permissions previously assigned to the SID of the deleted principal.
### SID structure

SIDs are binary values but are usually represented as strings for readability. The string format follows a hierarchical structure:

```
S-R-X-Y1-Y2-Yn-1-Yn
```

```
{SID}-{revision_level}-{identifier_authority}-{subauthority_1}-{subauthority_2}-...-{subauthority_n}
```

>[!example]+ Example of a SID
> ```
> S-1-5-21-3623811015-3361044348-30300820-1013
> ```

| Component | Description                                                                                                                 | Example                          |
| --------- | --------------------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| `S`       | Indicates that the string is a SID.                                                                                         | `S`                              |
| `R`       | **Revision level**; currently always `1`.                                                                                   | `1`                              |
| `X`       | **Identifier authority**; indicates the entity that issued the SID (e.g., "NT Authority").                                  | `5`                              |
| `Y`       | A series of subauthority values (where `n` is the number of values); represents the **domain** or **machine identifier**.   | `3623811015-3361044348-30300820` |
| `Yn`      | **Relative Identifier (RID)**, the last subauthority value; uniquely identifies the principal within the domain or computer | `1013`                           |

>[!important] SIDs on the same machine or domain are identical except the last subauthority value — RID (Relative Identifier).

### Common RIDs

- The first user account you create typically gets an RID of `1000`, the second gets `1001`, and so on.

>[!important] The RID is the only part that changes as you create new accounts on the same machine.

- **Built-in accounts and groups** have fixed RIDs that remain constant across all Windows installations.

**Built-in local accounts:**

| RID   | Account            |
| ----- | ------------------ |
| `500` | **Administrator**  |
| `501` | Guest              |
| `502` | KRBTGT (domain)    |
| `503` | DefaultAccount     |
| `504` | WDAGUtilityAccount |

**Built-in groups:**

| RID   | Group              |
| ----- | ------------------ |
| `512` | Domain Admins      |
| `513` | Domain Users       |
| `514` | Domain Guests      |
| `515` | Domain Computers   |
| `516` | Domain Controllers |
| `544` | **Administrators** |
| `545` | Users              |
| `546` | Guests             |
| `547` | Power Users        |
| `548` | Account Operators  |
| `549` | Server Operators   |
| `550` | Print Operators    |
| `551` | Backup Operators   |


>[!note] See [`Security identifiers — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-identifiers) for a full list.

### Identifier authority values

**Identifier authority** indicates the entity that issued the SID. Below are some well-known values:

| Authority | Formal name          | Description         |
| --------- | -------------------- | ------------------- |
| `0`       | Null Authority       | No authority        |
| `1`       | World Authority      | Everyone            |
| `2`       | Local Authority      | Local system        |
| `3`       | Creator Authority    | Creator owner/group |
| `4`       | Non-unique Authority | NTLM-style          |
| `5`       | **NT Authority**     |                     |
| `9`       | Resource Manager     |                     |

| Authority | Formal name     | Description                                                                                                               |
| --------- | --------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `0`       | Null Authority  | Represents nothing; rarely used except in theoretical examples (e.g., Nobody (`S-1-0-0`)).                                |
| `1`       | World Authority | Used for well-known groups that represent categories of users rather than specific accounts (e.g., Everyone (`S-1-1-0`)). |
| `5`       | NT Authority    | Start for Windows security subsystem-managed SIDs.                                                                        |

### Well-known SIDs

Beyond the uniquely created, domain-specific SID, Windows defines numerous **well-known SIDs** that are identical on every Windows system:

| Well-known SID | Security principal                  | Description                                                                                                                                                  |
| -------------- | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `S-1-0-0`      | Nobody                              | No security principal.<br>This appears in some security logs when the system can't determine who performed an action.                                        |
| `S-1-1-0`      | Everyone (world)                    | A group that includes all users — anonymous users, guests, authenticated users — literally everyone.<br>Any security principal can exercise this permission. |
| `S-1-2-0`      | Local                               | Users who have logged in locally (those physically present at the console); doesn't include users connected remotely.                                        |
| `S-1-5-11`     | Authenticated users                 | A groups that includes all users who have successfully authenticated to the system.<br>Doesn't include anonymous or guest users.                             |
| `S-1-5-18`     | Local System (`SYSTEM`)             | A service account used by the operating system itself; the **highest privilege level** on a standalone machine.                                              |
| `S-1-5-19`     | Local Service (`LOCAL SERVICE`)     | A service account with minimal privileges; used for services that don't need network access.                                                                 |
| `S-1-5-20`     | Network Service (`NETWORK SERVICE`) | Another service account with minimal local privileges but with a network authentication capability; used for services that do need network access.           |

>[!note] Domain-joined computers have both a domain SID (assigned when the computer joined the domain) and a local machine SID (unique to that computer). 

### Querying SIDs

- Get the current user's SID:

```PowerShell
whoami /user
```

- Find the SID of a specific user:

```PowerShell
Get-LocalUser -Name "username" | Select-Object SID
```

```CMD
wmic useraccount where name='username' get sid
```


- Find the account name associated with a specific SID:

```PowerShell
 $objSID = New-Object System.Security.Principal.SecurityIdentifier("S-1-5-21-3623811015-3361044348-30300820-1013")
 $objUser = $objSID.Translate([System.Security.Principal.NTAccount])
 $objUser.Value
```

- Find the local machine SID (remove the last component of any local user's SID):

```powershell
(Get-LocalUser | Select-Object -First 1).SID.AccountDomainSid
```
## Users 

>A **Windows user account** is a type of security principal that represents an **interactive or service logon identity** used by a human or application to authenticate to a Windows system or domain.

### Local vs. domain user accounts

User accounts can be **local** and **domain**:

- **Local users**
	- Created and managed on a single computer.
	- Credentials and account information is stored locally in the computer's **SAM (Security Accounts Manager)** database. 
	- Can authenticate into and access resources on the computer where the account is defined, but not other computers on the domain (unless those computers define identical local accounts).
	- Credentials are validated by the local **LSASS (Local Security Authority Subsystem Service)**.

>[!important] Local user accounts are stored in the **SAM (Security Accounts Manager) database** on the local machine (`%SystemRoot%\System32\config\SAM`). See [[#SAM]].

- **Domain users**
	- Stored in **Active Directory** (database on Domain Controllers).
	- Valid across the entire domain; can authenticate to and access resources on any computer within that domain.
	- Credentials are validated by **Domain Controllers (DCs)**, and the domain administrator can manage access rights of that user.

### Default local user accounts

>[!note] See [`Default local user accounts — Local Accounts, Microsoft Learn`](https://learn.microsoft.com/en-us/windows/security/identity-protection/access-control/local-accounts#default-local-user-accounts).

Windows defines several **default local user accounts** that are created automatically and exist on **every Windows system**:

- **Administrator**
	- **SID**: `S-1-5-21-<machine_id>-500`
	- The default local administrator account created during installation.
	- Has unrestricted access to the system.
	- Not subject to UAC filtering (on most configurations).
	- A prime target for privilege escalation attacks.
	- Can't be deleted, but can be disabled. 

>[!warning] Even when the Administrator account is disabled, it can still be used to gain access to a computer by using safe mode. In the Recovery Console or in safe mode, the Administrator account is automatically enabled. When normal operations are resumed, it's disabled.

- **Guest** 
	- **SID**: `S-1-5-21-<machine_id>-501`
	- Intended for temporary access.
	- Have extremely limited privileges.
	- Disabled by default; has no password (or a blank password) if enabled.

- **DefaultAccount**
	- **SID**: `S-1-5-21-<machine_id>-503`
	- Also known as **Default System Managed Account (DSMA)**.
	- From a permission perspective, a standard user account.
	- Created during first boot, disabled by default.


- **HelpAssistant**
	- **SID**: `S-1-5-21-<domain>-1000`
	- Created when Remote Assistance is used, provides limited access for remote support. Automatically deleted when the session ends.

>[!note] The DefaultAccount is needed to run multi-user-manifested apps (MUMA apps). MUMA apps run all the time and react to users signing in and signing out of the devices. Unlike Windows Desktop where apps run in context of the user and get terminated when the user signs off, MUMA apps run by using the DSMA.

>[!important] Default accounts can't be removed or deleted, and they don't provide access to network resources.
### Default local system accounts

>Windows **system accounts** are used to run Windows services and system processes in the background. 

- System accounts are used by the OS and services, and are not for human interaction. 
- They have **no passwords or user settings** (any password you specify is ignored), can't log in interactively, and can't be added to groups.
- System accounts are managed by **Service Control Manager (SCM)**. 

>[!note] See [`Default local system accounts — Local Accounts, Microsoft Learn`](https://learn.microsoft.com/en-us/windows/security/identity-protection/access-control/local-accounts#default-local-system-accounts).

Important system accounts include:

- **`SYSTEM` (SID: `S-1-5-18`)**
	- The highest-privileged local account, used by the Windows kernel and core services.
	- `SYSTEM` has complete control over all local resources, more than even local `Administrator`.
	- But you can't log into it directly or add it to groups.

- **`NETWORK SERVICE` (SID: `S-1-5-20`)** 
	- A build-in  service account with minimal local privileges but with a network authentication capability. 

- **`LOCAL SERVICE` (SID: `S-1-5-19`)**
	- A built-in service account with minimal privileges, similar to `NETWORK SERVICE` but without an ability for network authentication.

 - **Virtual accounts**
	- Introduced in Windows Server 2008 R2 and Windows 7, these are managed service accounts created automatically per-service. They appear in `NT SERVICE\<ServiceName>`.
	- Virtual accounts are managed automatically; no password management is required.
	- They have access to the network in a domain environment.

### `SYSTEM` (`LocalSystem`)

>**`SYSTEM`**, or **`LocalSystem`** is **the most powerful account** on a standalone Windows machine.

- **SID**: `S-1-5-18`.
- This account as full access to the local system, including the `HKLM\SECURITY` registry hive (which normal Administrators can't read); has the `SeTcbPrivilege` assigned (act as part of the operating system).
- This account is not recognized by the security subsystem, therefore it can't be queried via standard [`LookupAccountName`](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-lookupaccountnamea) APIs; it exists outside the standard security subsystem. `SYSTEM` doesn't show up in User Manager either.
- **Can't be used to log in interactively** via Winlogon.
- There's no password for this account. Any password information you provide is ignored.

>[!important] `SYSTEM` has full control over all system objects, the registry (including `HKLM\SECURITY`), files, and processes. 

>[!bug] `SYSTEM` is the ultimate privilege escalation target on standalone machines and domain members. Gaining `SYSTEM` means **full local compromise**.

- Launch a command prompt as `SYSTEM`:

```powershell
psexec -s -i cmd.exe
```

>[!important] `SYSTEM` has higher privileges than Administrator. 
### `NETWORK SERVICE`

>**`NETWORK SERVICE`**, or **`NetworkService`**, is a predefined service account with reduced local privileges compared to `SYSTEM`, designed for services that require network access but don't need full system-level control.

- **SID:** `S-1-5-20`.
- `NETWORK SERVICE` has **minimal privileges on the local system**. It's designed for services that require network access without needing full system-level control.
- This account is not recognized by the security subsystem, therefore it can't be queried via the [`LookupAccountName`](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-lookupaccountnamea) function.

>[!important] A service that runs in the context of the `NetworkService` account presents the computer's credentials to remote servers.
>- By default, the remote token contains SIDs for the `Everyone` and `Authenticated` Users groups. The user SID is created from the `SECURITY_NETWORK_SERVICE_RID` value.

- This account is used by IIS, SQL Server and other network-aware services.

>[!bug] `NETWORK SERVICE` is often encountered in web application and database server contexts.
>- Exploiting a service running as `NETWORK SERVICE` provides a foothold but requires further escalation techniques.
### `LOCAL SERVICE`

>**`LOCAL SERVICE`**, or `LocalService`, is a predefined service account with the **least privileges**, designed for services that only require local services and don't need network authentication.

- `LOCAL SERVICE` SID: `S-1-5-19`.
- Privileges are even more restricted than `NETWORK SERVICE`.
- `LOCAL SERVICE` can't write to protected system areas or modify most registry keys.
- Presents anonymous credentials to the network; provides on identity or authentication to remote systems (therefore can't access network resources protected with authentication credentials).
- This account is used for simple services with minimal access requirements.

>[!bug] `LOCAL SERVICE` is the least valuable system account for direct privilege escalation.

### Regular user accounts

>**Regular user accounts** can be created by administrators or during initial setup for daily use. 

- By default, regular users have limited privileges; they can't install system-wide software or modify system settings without UAC.

>[!important] By default, Home folders for default and custom accounts are located in the `Users` directory (e.g., `C:\Users\<username>`). They contain files and folders owned and managed by the respective users.


## Groups

>A **Windows group** is a security principal that represents a **collection of other security principals** (users, computers, or other groups) for the purpose of simplifying permission assignment.

- As any security principal, each group is uniquely identified by a SID.
- Local groups are defined in the SAM database. 
- A group can not authenticate or execute code.

Groups can contain:
- Users
- Other groups
- Computers (domain context)

Windows defines several built-in security groups:

- **Administrators**
	- SID: `S-1-5-32-544`
	- Members of this groups have broad system control; they can modify system files, manage users and groups, load drivers, and bypass most discretionary access controls. 

>[!important] Membership does **not automatically mean elevated execution**. UAC filtering applies unless explicitly disabled

- **Users**
	- SID: `S-1-5-32-545`
	- Contains standard users and represents the baseline interactive user context.
	- Members have read access to most system files, but write access is limited to user profile files. 

- **Guests**
	- SID: `S-1-5-32-546`
	- Guests have extremely restricted access to the system; historically used for temporary logons.
	- Currently mostly deprecated. 


- **Backup operators**
	- SID: `S-1-5-32-551`
	- This group exists to allow backup operations **without full administrative control**.
	- Members can read **almost any file** and write files during restore operations. 
	- But they can not change system configuration broadly.

- **Power users** (legacy)
	- **SID:** `S-1-5-32-547`
	- Intended to bridge the gap between Users and Administrators.
	- Mostly deprecated.
	- Retained for compatibility.
	- May still appear in ACLs; matters on older systems and legacy software.

- **Remote Desktop Users**
	- **SID:** `S-1-5-32-555`
	- Grants members permissions to log in via Remote Desktop (RDP).
	- Doesn't grant administrative rights by default. 
	- This group controls **logon rights**, not system authority.

- **Event log readers**
	- **SID:** `S-1-5-32-573`
	- Members can read Windows event logs but can't modify them. 
	- This group exists to allow auditing without administration.

- **Server Operations / Print operations**
	- Exist primarily on server editions.
	- Delegate narrow administrative roles.

| RID   | Account            | Description                                                                                                                       |
| ----- | ------------------ | --------------------------------------------------------------------------------------------------------------------------------- |
| `512` | Domain Admins      | A global group whose members are authorized to administer the domain (AD).                                                        |
| `513` | Domain Users       | A global group that includes all user accounts in a domain (AD).                                                                  |
| `514` | Domain Guest       | A global group that, by default, has only one member — the domain's built-in Guest account (AD).                                  |
| `515` | Domain Computers   | A global group that includes all domain clients and servers that have joined the domain (AD).                                     |
| `516` | Domain Controllers | A global group that includes all domain controllers in the domain.                                                                |
| `544` | Administrators     | A built-in group the only member of which, by default, is Administrator.                                                          |
| `545` | Users              | A built-in group for authenticated users.                                                                                         |
| `546` | Guests             | A built-in group the only member of which, by default, is Guest.                                                                  |
| `547` | Power Users        | A built-in group with no members by default.<br>Used to bridge the gap between all-might administrators and low-privileged users. |

## Enumerating local users and groups

### Users

- To list local users on PowerShell, use [`Get-LocalUser`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.localaccounts/get-localuser?view=powershell-5.1):

```PowerShell
Get-LocalUser
```

- For CMD, you can use [`net user`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/net-user?source=recommendations):

```cmd
net user
```

- Get detailed information about a specific user:

```PowerShell
Get-LocalUser -Name "Administrator" | Select-Object *
```

```CMD
net user Administrator
```

- Get a user's SID:

```powershell
Get-LocalUser -Name "Administrator" | Select-Object SID
```

### Groups

- To list local groups, you can use [`Get-LocalGroup`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.localaccounts/get-localgroup?view=powershell-5.1):

```powershell
Get-LocalGroup
```

- Or [`net group`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/cc754051(v=ws.11)) for CMD:

- Get information about a specific group:

```powershell
Get-LocalGroup -Name "group_name" | Select-Object *
```
## SAM

>The **[Security Access Manager (SAM)](https://en.wikipedia.org/wiki/Security_Account_Manager)** is a database file that stores information about local users and groups, including password hashes.

- SAM is used only for **local authentication**, meaning accounts defined on the machine itself. Domain authentication uses Active Directory instead.
- SAM is stored under `%SystemRoot%\System32\config\SAM`:

```powershell
C:\Windows\System32\config\SAM
```

- This is a **registry have**.

>[!note] See [[registry]].

## References and further reading

- [`Security principals — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-principals)
- [`Securable Objects — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/secauthz/securable-objects)
- [`Security identifiers — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-identifiers)


- [`Local Accounts — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/security/identity-protection/access-control/local-accounts#default-local-system-accounts)
- [`Service Accounts — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/dn617203(v=ws.11))


- [`Security Identifier — Wikipedia`](https://en.wikipedia.org/wiki/Security_Identifier)

- [`Well-known SIDs — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/secauthz/well-known-sids)
- [`Well-known Security Identifiers — ldapwiki.com`](https://ldapwiki.com/wiki/Wiki.jsp?page=Well-known%20Security%20Identifiers)


