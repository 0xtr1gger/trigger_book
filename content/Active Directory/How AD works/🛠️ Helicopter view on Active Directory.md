---
created: 2026-07-24
updated: 2026-07-28
tags:
  - AD
status: substantial
---
## Active Directory

>[`Active Directory (AD)`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview) is a directory service that serves as the **centralized identity and access management system** for Windows domain networks.

- AD functions as both a database — that stores information about network objects such as users, computers, groups, printers, shared folders — and a directory service — that makes that data queryable and manageable.
- Its primary functions include:
	- **Authentication and authorization** — AD verifies user identities (typically via Kerberos) and determines what resources each user is permitted to access; it also enables **SSO (Single Sign-On)** across domain-joined services.
	- **Centralized management** — Administrators can manage user accounts, permissions, and security policies from a single console across all domain-joined devices, rather than configuring each one individually.
	- **Policy enforcement** — AD **Group Policy Objects (GPOs)** enforce security settings, software configurations, and administrative restrictions across all devices in the domain.
	- **Resource organization** — AD uses a hierarchical structure of **domains, trees, and forests** to logically organize network resources.

>[!note] Around 95% of [Fortune 500](https://en.wikipedia.org/wiki/Fortune_500) companies run Active Directory.

>[!note] See [`Active Directory Domain Services overview — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview).

## Directory structure and administrative boundaries

### Forests

>A **forest** is the highest-level logical structure in Active Directory that encompasses one or more **domains** sharing a common directory schema, configuration, and Global Catalog. It represents the ultimate **security boundary** in AD.

- A forest contains one or more **directory trees**, each of which in turn contains one or more domains.
- All domains within a forest share a common **directory schema, configuration, and Global Catalog**.
- By default, domains within the same forest are linked by **implicit two-way transitive trust relationships**, meaning that users in one domain can authenticate against and access resources in other domains without explicit trust configuration.
- The forest acts as the distinct **security boundary**; by default, users or administrators in one forest cannot access resources in another forest unless a specific trust relationship is established.
- Each forest operates with a **single global address list** and a unified security database for all contained objects.
- Enterprise-wide administrative roles (e.g., **Enterprise Admins**, **Schema Admins**) operate at the forest level and have authority over every domain within it.
### Trees

>A **tree** is a hierarchical collection of one or more domains that share a **contiguous DNS namespace** and are connected through **transitive trust relationships**.

- A tree begins with a single **root domain** and branches out into **child domains**; all of them share a common directory schema, configuration, and Global Catalog.
- All domains in the tree share the same naming structure — for example, `child.example.com` is a child domain under the `example.com` root domain.
- Domains in the same tree automatically establish **two-way transitive trust** (if domain `A` -> trusts `B`, and `B` -> trusts `C`, then `A` -> implicitly trusts `C`).
- Multiple trees may coexist within a single forest; when they do, they form a **discontiguous DNS namespace** (e.g., `example.com` and `unrelated.net` in the same forest).

>[!important] Trees do not constitute security boundaries. The forest is the security boundary.

### Domains

>A **domain** is a logical group of network objects — such as users, computers, and groups — that share the same **Active Directory database**, administrative boundaries, and security policies. 

- Domain is the fundamental unit of replication and administration in AD.
- Each domain is hosted by one or more **Domain Controllers (DCs)** that maintain copies of the domain's directory database.
- Security policies (password policies, account lockout policies, etc.) are commonly applied at the domain level.
- Domains replicate directory data independently while remaining members of the forest.
- A domain defines its own **namespace** (e.g., `corp.example.com`) and its own set of **security identifiers (SIDs)** for all objects within it.

### Organizational Units (OUs)

>An **Organizational Unit (OU)** is a logical container within a domain used to organize directory objects, delegate administrative authority, and apply Group Policy Objects (GPOs).

- OUs exist only inside a domain — they do not span across domains or forests.
- They are the primary mechanism for **administrative delegation**: an administrator can grant a user full or partial control over an OU without granting domain-wide privileges.
- OUs are the **primary scope for applying Group Policies**; GPOs are linked to OUs to configure settings for the objects they contain.
- An OU does **not** represent a security boundary — users with sufficient domain-level privileges can bypass OU-level restrictions.

### Sites

>A **site** in Active Directory represents the **physical network topology**, consisting of one or more well-connected IP subnets, used to optimize authentication traffic and directory replication.

- Sites represent **physical** rather than **logical** organization — they map to network segments, not to administrative groupings.
- Sites optimize **client logon** by directing clients to the nearest Domain Controller and reduce **WAN replication traffic** by controlling how and when directory changes replicate between geographically dispersed locations.
- A site determines which DCs are **preferred** for a given subnet; this is independent of domain and forest boundaries.
- Sites are configured via **Active Directory Sites and Services** and are replicated forest-wide through the configuration partition.

## Directory infrastructure

### Domain Controllers (DCs)

>A **Domain Controller (DC)** is a Windows Server that hosts the Active Directory Domain Services database and provides authentication, authorization, replication, and directory services to domain members.

- A DC stores a **writable copy** of the domain's directory database (`NTDS.dit`).
- It authenticates users and computers, issues Kerberos tickets, processes LDAP requests, and participates in directory replication.
- DCs often also provide **DNS services** for the domain, as DNS is a prerequisite for AD functionality.
- Every domain must have at least one DC; production environments typically deploy multiple DCs for redundancy and load distribution.

### Read-Only Domain Controllers (RODCs)

>A **Read-Only Domain Controller (RODC)** is a Domain Controller that maintains a **read-only replica** of the Active Directory database, designed to improve security in locations with limited physical protection (e.g., branch offices).

- An RODC cannot write to the directory database — it only replicates changes from writable DCs.
- It stores credentials for only those users that explicitly need to authenticate at that location, reducing the attack surface if the RODC is compromised.
- RODCs use a feature called **credential caching** that can be restricted to specific accounts or disabled entirely.

### Active Directory database

>The **Active Directory database** is an Extensible Storage Engine (ESE) database that stores all directory objects, attributes, and security information within a domain.

- The database is stored in the **`NTDS.dit`** file on each Domain Controller, typically located at `C:\Windows\NTDS\NTDS.dit`.
- The database is accompanied by transaction log files (`edb*.log`) and a checkpoint file (`edb.chk`) that ensure data integrity through write-ahead logging.
- The database can be inspected and modified using the **ADSI Edit** snap-in or the `ntdsutil` command-line tool.

### Schema

>The Active Directory [**schema**](https://learn.microsoft.com/en-us/windows/win32/ad/schema) is the formal definition of all **object classes** and **attributes** that may exist within the directory service.

- A single schema is shared by the entire forest, so schema changes replicate forest-wide and affect every domain.
- The schema is stored in the `Schema` naming context and can be modified using tools like `ADSI Edit` or `ldifde`.
- Extending the schema (adding new object classes or attributes) is an irreversible operation — once an attribute is added, it cannot be removed.

### Global Catalog (GC)

>The [**Global Catalog (GC)**](https://learn.microsoft.com/en-us/windows/win32/ad/global-catalog) is a distributed data repository that contains a **complete replica** of all objects from its local domain and a **partial replica** (a subset of commonly queried attributes) of objects from every other domain in the forest.

- The GC enables **forest-wide searches** without requiring referrals to individual domain controllers.
- It accelerates **user logon** by resolving **Universal Group memberships** during authentication — without a GC, Universal Group membership cannot be determined.
- GCs are required by **Microsoft Exchange** for address list lookups and recipient resolution.
- By default, every DC hosts a GC replica, but in large environments, GC placement can be restricted to specific DCs to reduce replication overhead.

### Replication

>**Replication** is the distributed synchronization process through which Active Directory maintains consistent directory information across all Domain Controllers.

- AD uses **multi-master replication**: any DC can accept write operations, and changes propagate to other DCs through replication.
- The **Knowledge Consistency Checker (KCC)** automatically computes the replication topology, creating connection objects between DCs to form an efficient replication ring.
- Replication occurs within a domain (intra-domain) and between domains (inter-domain), each following separate replication schedules and topologies.
- **Change originating** DCs assign a **Update Sequence Number (USN)** to each change; other DCs track which USNs they have received from each partner to avoid replicating the same change twice.
- Replication can be triggered on a schedule or on-demand using tools like `repadmin /syncall`.
- **Sites** influence replication: intra-site replication is frequent and uncompressed, while inter-site replication is scheduled and compressed to conserve WAN bandwidth.

### `SYSVOL`

>**`SYSVOL`** is a shared folder replicated among Domain Controllers that stores the server's copy of the domain's public files, including **Group Policy Objects (GPOs)**, **logon scripts**, and **startup scripts**.

- `SYSVOL` is accessible at `\\<domain>\SYSVOL` and is replicated using **Distributed File System Replication (DFS-R)** on modern functional levels (Windows Server 2008 and later); older environments may use **File Replication Service (FRS)**.
- GPOs are stored under `\\<domain>\SYSVOL\<domain>\Policies\` and consist of a `Machine` and `User` subdirectory containing registry-based policy files and scripts.
- Because `SYSVOL` is publicly accessible to authenticated domain users, it is a common target for credential harvesting (e.g., GPP password discovery) and logon script abuse.

### Tombstones and AD recycle bin

>A **tombstone** is a hidden, deactivated copy of a deleted object retained in the directory for a limited time (the **tombstone lifetime**, typically 180 days by default) to allow replication to propagate the deletion across all DCs.

- When an object is deleted, it is not immediately removed from the database — it is marked as a tombstone and stripped of most attributes.
- After the tombstone lifetime expires, the object is permanently removed during **garbage collection**.
- The **AD Recycle Bin** (available at Windows Server 2008 R2 forest functional level and above) preserves all object attributes during deletion, allowing administrators to **restore deleted objects** with their group memberships, link-value history, and other metadata intact.
- Without the AD Recycle Bin, restoring a tombstoned object requires manual reconstruction and results in a new SID, breaking group memberships and resource access.

>[!note] See [`The AD Recycle Bin — Microsoft Tech Community`](https://techcommunity.microsoft.com/t5/ask-the-directory-services-team/the-ad-recycle-bin-understanding-implementing-best-practices-and/ba-p/396944).

## Directory objects

### Object

>An **object** in Active Directory is an individual directory entry representing a resource, identity, or service, uniquely identified by its attributes and defined by the schema.

- Objects are the basic units of the directory — every user, computer, group, printer, and shared folder is an object.
- Each object has a **Distinguished Name (DN)** and a **Globally Unique Identifier (GUID)**.
- Security principals (users, computers, security groups) additionally receive a **Security Identifier (SID)**.
- There are two main types of objects:
	- **Container objects** — hold other objects and have a defined place in the directory subtree hierarchy (e.g., domains, OUs, containers like `CN=Users`).
	- **Leaf objects** — do not contain other objects and represent the terminal entries in the directory hierarchy (e.g., user accounts, computer accounts).

### Distinguished Name (DN)

>A [**Distinguished Name (DN)**](https://learn.microsoft.com/en-us/previous-versions/windows/desktop/ldap/distinguished-names) is the unique hierarchical identifier that specifies the exact location of an object within the directory tree.

- A DN uniquely identifies an object and represents its full path through the directory hierarchy.
- DNs are used in **LDAP queries** to locate and retrieve specific objects.
- If an object is moved to a different container, its DN changes because it encodes the object's location within the directory.

- Example DNs:

```
CN=John Doe,OU=DevOps,DC=Fabrikam,DC=COM
CN=Jane Doe,CN=Users,DC=corp,DC=Fabrikam,DC=COM
```

| String   | Attribute type           |
| -------- | ------------------------ |
| `DC`     | `domainComponent`        |
| `CN`     | `commonName`             |
| `OU`     | `organizationalUnitName` |
| `O`      | `organizationName`       |
| `STREET` | `streetAddress`          |
| `L`      | `localityName`           |
| `ST`     | `stateOrProvinceName`    |
| `C`      | `countryName`            |
| `UID`    | `userid`                 |

#### Relative Distinguished Name (RDN)

>A [**Relative Distinguished Name (RDN)**](https://docs.microsoft.com/en-us/windows/win32/ad/object-names-and-identities) is the leftmost component of an object's DN — the attribute-value pair that uniquely identifies the object **relative to its parent container**.

- The RDN follows the syntax `attribute=value` (e.g., `CN=John Doe` or `OU=DevOps`).
- While the **Distinguished Name** provides the full hierarchical path (e.g., `CN=John Doe,CN=Users,DC=example,DC=com`), the RDN is specifically the first component: `CN=John Doe`.
- Two objects in different containers may share the same RDN — uniqueness is only guaranteed within the parent container.

### Globally Unique Identifier (GUID)

>A **Globally Unique Identifier (GUID)** is a permanent, immutable 128-bit identifier assigned to every Active Directory object at creation.

- Unlike a DN, a GUID **never changes** — it remains the same even after an object is renamed or moved.
- GUIDs are used internally by AD for referencing objects and are globally unique across the entire forest.
- Every object created in AD receives a GUID, regardless of type — unlike SIDs, which are only assigned to security principals.
- The GUID is stored in the `objectGUID` attribute and can be used in LDAP queries to locate objects irrespective of their current DN.

### Attribute

>An **attribute** is an individual property associated with an Active Directory object, defined and constrained by the directory schema.

- Attributes store information about objects — for example, `mail`, `displayName`, `memberOf`, or `pwdLastSet`.
- The schema defines which attributes are available for each object class and whether they are single-valued or multi-valued.
- Frequently queried attributes may be **indexed** by the database engine to improve search performance.
- Notable user-related attributes:

| Attribute             | Description                                                                                                                              |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `sAMAccountName`      | The user's logon name (e.g., `jdoe`); used for legacy authentication and must be unique within the domain.                              |
| `userPrincipalName`   | The UPN logon name in the format `username@domain` (e.g., `jdoe@example.com`); the preferred logon format in modern environments.       |
| `objectGUID`          | A permanent, immutable identifier that never changes, even if the object is renamed or moved.                                            |
| `objectSID`           | The user's Security Identifier, used by Windows for all authorization decisions; identifies the user and their group memberships.       |
| `sIDHistory`          | Contains previous SIDs from other domains — populated during cross-domain migrations to preserve access to resources in the old domain.  |
| `distinguishedName`   | The full hierarchical path to the object within the directory.                                                                           |
| `objectClass`         | Identifies the type of object (e.g., `user`, `computer`, `group`) and determines which attributes are available.                       |

## Identity and security principals

### Security principals

>A [**security principal**](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-principals) is any object that possesses a **Security Identifier (SID)** and can therefore be assigned permissions or act as a trustee in an Access Control Entry (ACE).

- The three primary types of security principals are **user accounts**, **computer accounts**, and **security groups**.
- Conversely, objects such as **Organizational Units (OUs)**, **containers**, **contacts**, and **distribution groups** are **not** security principals — they lack a SID and cannot be directly granted permissions in an ACL.

### User accounts

>A **user account** is a security principal that represents an individual identity capable of authenticating to Active Directory and accessing domain resources.

- Each user account represents a single human user (or, in some cases, a service identity).
- User accounts receive a **Security Identifier (SID)** and are authenticated via **Kerberos** (preferred) or **NTLM** (legacy).
- A user account has several key attributes: `sAMAccountName` (logon name), `userPrincipalName` (UPN), `distinguishedName`, `pwdLastSet`, `lastLogon`, and `memberOf` (group memberships).
- Users may belong to multiple security groups and can own resources such as files, shares, and certificates.
- User accounts are managed through tools like **Active Directory Users and Computers (ADUC)**, PowerShell (`New-ADUser`), or the AD Administrative Center.

### Computer accounts

>A **computer account** is a security principal that represents a domain-joined computer, allowing it to authenticate to Active Directory and participate in the domain.

- A computer account is **created automatically** when a workstation or server joins a domain.
- The computer's `sAMAccountName` is the machine name followed by a `$` suffix (e.g., `WORKSTATION01$`).
- Each computer account has its own machine password that is **rotated automatically** (by default, every 30 days) — the machine itself manages this process.
- Computer accounts receive a unique SID and can be members of security groups, granting the machine (and services running on it) access to domain resources.
- Domain-joined computers rely on their computer account for **Kerberos authentication**, **Group Policy processing**, and **DNS registration**.

### Groups

>A **group** is a security principal that collects multiple users, computers, or other groups into a single unit, simplifying permission assignment and administrative management.

- A group may contain user accounts, computer accounts, and nested groups.
- **Security groups** receive SIDs and are used in ACLs to authorize access to resources; **distribution groups** are used only for email routing and cannot be granted permissions.
- Groups have three **scopes** that determine where they can be used:
	- **Domain Local** — can contain members from any domain but can only be granted permissions within the domain where it is defined.
	- **Global** — can only contain members from the same domain but can be used to grant permissions in any domain in the forest.
	- **Universal** — can contain members from any domain in the forest and can be used to grant permissions in any domain; memberships are resolved via the Global Catalog.

>[!note] See [[🛠️ AD users and groups]].

### Service accounts

>A **service account** is a security principal used by applications and services to authenticate to Active Directory and access network resources on behalf of a service.

- Standard service accounts function like user accounts but are intended for non-interactive use by server applications (IIS, SQL Server, etc.).
- **Group Managed Service Accounts (gMSAs)** are the modern preferred approach — they provide automatic password management, Kerberos delegation support, and eliminate the need to manually manage service account credentials.
- **Managed Service Accounts (MSAs)** are single-domain gMSAs designed for a single server; gMSAs extend this to support multiple hosts.
- Service accounts can be granted **delegated permissions** to access specific resources, following the principle of least privilege.

### Contacts

>A **contact** is a non-security principal directory object typically used to represent an external user or a mail-enabled entity in environments integrated with **Microsoft Exchange**.

- Contacts do **not** have a SID and cannot authenticate to the domain — they exist solely for email addressing and directory lookups.
- A contact can have attributes such as `mail`, `displayName`, `targetAddress`, and `proxyAddresses`.
- Contacts are often created for external collaborators whose email is managed through Exchange but who do not need a domain account.

### Security Identifiers (SIDs)

>A **Security Identifier (SID)** is a unique, immutable value assigned to every security principal that Windows uses internally for **authorization decisions**.

- SIDs are used in **Access Control Lists (ACLs)** instead of usernames — every permission entry references a SID.
- SIDs are never reused, even after an account is deleted; if a new account is created with the same name, it receives a new SID.
- A SID remains constant even after an account is renamed.
- The SID structure consists of a **domain SID** (unique per domain) combined with a **Relative Identifier (RID)** (unique per object within the domain).
- The **`sIDHistory`** attribute stores previous SIDs for accounts that were migrated from another domain, preserving access to resources in the source domain — this is a common target for **SID history injection** attacks in compromised environments.

### FSMO roles

>**[Flexible Single Master Operation (FSMO) roles](https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/fsmo-roles)** are specialized roles assigned to Domain Controllers that handle tasks requiring a single authoritative source to prevent conflicts in a multi-master replication environment.

- AD uses multi-master replication for most operations, but certain tasks must be performed by a single DC to avoid conflicts. These tasks are delegated through five FSMO roles.
- Two roles are assigned **forest-wide** (one per forest), and three are assigned **per domain** (one per domain).

| **Role**                   | **Scope**    | **Description**                                                                                                                                                                                                |
| -------------------------- | ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Schema Master**          | Forest       | Manages the read/write copy of the AD schema. All schema changes must be made on the DC holding this role.                                                                                                     |
| **Domain Naming Master**   | Forest       | Manages the addition and removal of domains in the forest. Ensures that no two domains share the same name within a forest.                                                                                    |
| **RID Master**             | Domain       | Allocates blocks of **Relative Identifiers (RID)** to other DCs for SID generation. Ensures that no two objects in the domain receive the same SID.                                                            |
| **PDC Emulator**           | Domain       | The authoritative DC for password changes, account lockout processing, and Group Policy updates. Emulates a Windows NT 4.0 PDC for legacy clients. Also maintains **domain time synchronization**.            |
| **Infrastructure Master**  | Domain       | Translates GUIDs, SIDs, and DNs between domains in multi-domain forests. If this role is not functioning correctly, ACLs may display unresolved SIDs instead of object names.                                 |

## Key protocols

### NTLM

>**NTLM (NT LAN Manager)** is a challenge-response authentication protocol used by Windows for backward compatibility with older systems that do not support Kerberos.

- The protocol is used as a fallback when Kerberos is unavailable (e.g., workgroup machines, older applications).
- NTLM authentication consists of three messages: **`NEGOTIATE_MESSAGE`**, **`CHALLENGE_MESSAGE`**, and **`AUTHENTICATE_MESSAGE`**.

>[!bug] NTLM is vulnerable to **pass-the-hash** and **relay attacks**, which makes it a significant attack vector in AD environments.

>[!note] See [[🛠️ NTLM]].
### Kerberos

>**[Kerberos](https://en.wikipedia.org/wiki/Kerberos_(protocol))** is the primary authentication protocol in modern AD environments that provides mutual authentication between clients and services using symmetric-key cryptography and a trusted third-party Key Distribution Center (KDC).

- Kerberos authenticates users by issuing **Tickets**: a **Ticket-Granting Ticket (TGT)** for initial authentication and **Service Tickets (ST)** for accessing specific services.
- It supports **mutual authentication** (both client and server verify each other) and **delegation** (a service can act on behalf of a user).

>[!bug] Kerberos is vulnerable to **Kerberoasting**, **AS-REP roasting**, **Golden Ticket**, and **Silver Ticket** attacks when credentials or keys are compromised.

>[!note] See [[🛠️ Kerberos]].
### LDAP

>**[Lightweight Directory Access Protocol (LDAP)](https://en.wikipedia.org/wiki/Lightweight_Directory_Access_Protocol)** is the standard application protocol used to query and modify directory services, including Active Directory.

- LDAP operates over **TCP port `389`** (cleartext) or **TCP port `636`** (LDAPS — LDAP over TLS/SSL).
- AD uses LDAP for directory queries, object creation/modification, authentication bind operations, and schema lookups.
- LDAP queries use **Distinguished Names (DNs)** to locate objects and support search filters for complex attribute-based queries.
- To interact with AD through LDAP, tools like `ldapsearch`, **ADSI Edit**, and PowerShell's `Get-ADObject` are used.

### DNS

>**[Domain Name System (DNS)](https://en.wikipedia.org/wiki/Domain_Name_System)** is the distributed naming service that maps hostnames to IP addresses; it is **essential** for Active Directory operation.

- AD relies on DNS for **Domain Controller discovery** — clients locate DCs by querying for **`SRV` (Service) records** (e.g., `_ldap._tcp.dc._msdcs.<domain>`).
- DNS supports **Kerberos authentication** by resolving service principal names (SPNs) to the correct hosts.
- AD-integrated DNS zones are stored within the directory itself and replicate via AD replication, providing fault tolerance and dynamic updates.
- Without functioning DNS, domain-joined computers cannot locate DCs, and authentication will fail entirely.

### MSRPC

>**[MSRPC](https://ldapwiki.com/wiki/MSRPC)** is Microsoft's implementation of [Remote Procedure Call (RPC)](https://en.wikipedia.org/wiki/Remote_procedure_call), used for inter-process and inter-machine communication in Windows environments.

- MSRPC is used extensively by AD for **inter-DC replication**, **domain join operations**, **Group Policy processing**, and **distributed COM (DCOM)** communication.
- It operates over various transports including **TCP/IP** (dynamic port allocation by default, though static ports can be configured for firewalls).
- MSRPC relies on **named pipes** and **endpoints** defined in the endpoint mapper (TCP port `135`).
## Policy and administrative management

### Group Policy

>**Group Policy** is the centralized management framework through which administrators configure operating system settings, user environments, and application behavior across an Active Directory environment.

- Group Policy allows administrators to enforce configurations from a central location rather than configuring each machine individually.
- Policies are applied through **Group Policy Objects (GPOs)**, which contain **Computer Configuration** settings (applied at startup) and **User Configuration** settings (applied at logon).
- GPOs are processed in **LSDOU order**: **Local** policy is applied first, followed by **Site**, **Domain**, and finally **Organizational Unit** policies — with OU-level settings taking the highest precedence.
- Group Policy enables **security baselines**, **software deployment**, **logon/startup scripts**, **registry-based preferences**, and **administrative template enforcement**.
- Policy refresh occurs automatically (every 90 minutes with a random offset) or can be forced with `gpupdate /force`.

### Group Policy Objects (GPOs)

>A **Group Policy Object (GPO)** is a collection of policy settings stored within Active Directory and linked to **sites**, **domains**, or **Organizational Units** for automated configuration management.

- A single GPO can contain thousands of policy settings spanning security, software installation, scripts, and registry preferences.
- GPOs support **inheritance**: child OUs inherit policies from parent OUs, and lower-level policies can **block** or **override** inherited settings through precedence.
- GPOs are replicated among Domain Controllers via **SYSVOL** replication (DFS-R or FRS).
- Each GPO has a unique **GUID** and is stored in two parts: the **Group Policy Container (GPC)** in AD and the **Group Policy Template (GPT)** in the `SYSVOL` share.

### Trust relationships

>A **trust** is a security relationship established between domains or forests that enables authenticated users in one security boundary to access resources in another, subject to authorization.

- Trusts allow cross-domain and cross-forest resource access without requiring separate accounts in each domain.

- Trust types:

| **Trust type** | **Description**                                                                                                                                                    |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `Parent-child` | A two-way transitive trust between domains within the same forest. <br>Created automatically when a child domain is added.                                         |
| `Cross-link`   | A trust between child domains to reduce the number of intermediate hops in authentication; speeds up cross-domain access.                                          |
| `External`     | A non-transitive trust between two domains in separate forests that are not already joined by a forest trust. <br>Uses **SID filtering** to prevent SID injection. |
| `Tree-root`    | A two-way transitive trust created automatically between a forest root domain and a new tree root domain within the same forest.                                   |
| `Forest`       | A transitive trust between two forest root domains; enables cross-forest resource access with selective authentication.                                            |

- Trusts can be **transitive** or **non-transitive**:
	- In a **transitive** trust, trust is extended to all objects that the trusted domain trusts (if `A` -> trusts `B`, and `B` -> trusts `C`, then `A` -> also trusts `C`).
	- In a **non-transitive** trust, only the directly trusted domain is included.
- Trusts can be **one-way** or **two-way (bidirectional)**:
	- In a **two-way trust**, users from both domains can access resources in the other.
	- In a **one-way trust**, only users in the **trusted domain** can access resources in the **trusting domain** — the direction of trust is opposite to the direction of access.
## Functional levels

### Domain functional levels

>**Domain functional levels** determine which AD features are available within a domain and which operating systems can run as Domain Controllers. Raising the functional level enables new capabilities but restricts the minimum DC operating system version.

| Domain Functional Level | Features Available                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Supported DC Operating Systems                                                                 |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------- |
| Windows 2000 native     | Universal groups for distribution and security groups, group nesting, group conversion (between security and distribution groups), SID history.                                                                                                                                                                                                                                                                                                                               | Windows Server 2008 R2, 2008, 2003, 2000                                |
| Windows Server 2003     | `Netdom.exe` domain management, `lastLogonTimestamp` attribute, well-known users and computers containers, constrained delegation, selective authentication.                                                                                                                                                                                                                                                                                                                   | Windows Server 2012 R2, 2012, 2008 R2, 2008, 2003 |
| Windows Server 2008     | DFS replication support, AES 128 and AES 256 for Kerberos, fine-grained password policies.                                                                                                                                                                                                                                                                                                                    | Windows Server 2012 R2, 2012, 2008 R2, 2008                      |
| Windows Server 2008 R2  | Authentication mechanism assurance, Managed Service Accounts.                                                                                                                                                                                                                                                                                                                                                                                                                               | Windows Server 2012 R2, 2012, 2008 R2                                           |
| Windows Server 2012     | KDC support for claims, compound authentication, Kerberos armoring.                                                                                                                                                                                                                                                                                                                                                                                                                     | Windows Server 2012 R2, 2012                                                                   |
| Windows Server 2012 R2  | Extra protections for Protected Users group, Authentication Policies, Authentication Policy Silos.                                                                                                                                                                                                                                                                                                                                                                           | Windows Server 2012 R2                                                                                        |
| Windows Server 2016     | [Smart card required for interactive logon](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/interactive-logon-require-smart-card), new [Kerberos](https://docs.microsoft.com/en-us/windows-server/security/kerberos/whats-new-in-kerberos-authentication) features, new [credential protection](https://docs.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/whats-new-in-credential-protection) features. | Windows Server 2019 and 2016                                                                   |

### Forest functional levels

>**Forest functional levels** determine which forest-wide features are available and which operating systems can run as Domain Controllers across the entire forest.

| **Version**              | **Capabilities**                                                                                                                                                                                               |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Windows Server 2003`    | Forest trust, domain renaming, read-only domain controllers (RODC), and more.                                                                                                      |
| `Windows Server 2008`    | New domains default to the Server 2008 domain functional level. No additional forest-level features.                                                                                            |
| `Windows Server 2008 R2` | **AD Recycle Bin** — the ability to restore deleted objects with full attribute preservation.                                                                                                            |
| `Windows Server 2012`    | New domains default to the Server 2012 domain functional level. No additional forest-level features.                                                                                            |
| `Windows Server 2012 R2` | New domains default to the Server 2012 R2 domain functional level. No additional forest-level features.                                                                                         |
| `Windows Server 2016`    | [Privileged Access Management (PAM)](https://docs.microsoft.com/en-us/windows-server/identity/whats-new-active-directory-domain-services#privileged-access-management) using Microsoft Identity Manager (MIM). |

## `AdminSDHolder` and `dsHeuristics`

### `AdminSDHolder` and protected groups

>**[`AdminSDHolder`](https://docs.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/appendix-c--protected-accounts-and-groups-in-active-directory)** is a special container object (`CN=AdminSDHolder,CN=System`) whose **DACL** is replicated onto all protected accounts and groups every **60 minutes** by the **`SDProp` (Security Descriptor Propagator)** process.

- In other words, **`AdminSDHolder`** is a special security template in AD that protects high-privilege accounts (like Domain Admins) by ensuring their permissions remain consistent and restrictive.
- So, when an account becomes a member of a protected group, its DACL is overwritten with the `AdminSDHolder` ACL — any custom permissions are removed.

>[!note] Protected groups include **`Domain Admins`**, **`Enterprise Admins`**, **`Schema Admins`**, **`Administrators`**, **`Account Operators`**, **`Server Operators`**, and others.

- To enforce the template permissions, a background process called **`SDProp`** (Security Descriptor Propagator) runs every 60 minutes on the Primary Domain Controller. So, if any protected account’s permissions differ from the `AdminSDHolder` template, `SDProp` automatically resets them to match the template.
- The [`adminCount`](https://docs.microsoft.com/en-us/windows/win32/adschema/a-admincount) attribute on an object indicates whether it is managed by `SDProp`; a value of `1` means the object is protected.

---

- This mechanism exists to prevent privilege escalation through ACL manipulation, but it also means that legitimate permission changes on protected accounts will be reverted within an hour.
### `dsHeuristics`

>The [`dsHeuristics`](https://docs.microsoft.com/en-us/windows/win32/adschema/a-dsheuristics) attribute is a string attribute on the **Directory Service object** (`CN=Directory Service,CN=Windows NT,CN=Services`) that controls various behavioral settings for the directory service.

- It is a single string where each character position represents a specific configuration option.
- Common uses include controlling the default ACL for new objects, the length of the well-known containers, and the behavior of the Global Catalog.
- Changes to `dsHeuristics` are typically made through `ADSI Edit` or `ldifde` and should be approached with caution, as misconfiguration can alter fundamental AD behavior.

## References and further reading

- [`Active Directory Domain Services overview — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview)
- [`Active Directory schema — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/ad/schema)
- [`FSMO roles — Microsoft Learn`](https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/fsmo-roles)
- [`Security principals — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-principals)
- [`Protected Accounts and Groups — Microsoft Learn`](https://docs.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/appendix-c--protected-accounts-and-groups-in-active-directory)
- [`The AD Recycle Bin — Microsoft Tech Community`](https://techcommunity.microsoft.com/t5/ask-the-directory-services-team/the-ad-recycle-bin-understanding-implementing-best-practices-and/ba-p/396944)
- [`SYSVOL and Netlogon — Microsoft TechNet`](https://social.technet.microsoft.com/wiki/contents/articles/8548.active-directory-sysvol-and-netlogon.aspx)
- [`dsHeuristics — Microsoft Learn`](https://docs.microsoft.com/en-us/windows/win32/adschema/a-dsheuristics)

- [`Active Directory Domain Service Deep Dive — John Savill's Technical Training`](https://www.youtube.com/watch?v=4qC7H-y7oKI)

![](https://www.youtube.com/watch?v=4qC7H-y7oKI)