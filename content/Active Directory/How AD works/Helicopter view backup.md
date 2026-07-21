---
created: 2026-07-28
updated: 2026-07-28
---
- improve definitions
- add short explanations
- paraphrase sentences so they sound natural and better
- extend concepts when necessary.
- add more important information.

style: academic, textbook

## Active Directory

>[`Active Directory (AD)`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview) is a directory service that serves as the **centralized identity and access management system** for Windows domain networks. 

- AD functions as both a database — to store information about network objects such as users, computers, groups, printers, and shared folders — and a directory service.
- Its primary functions include:
	- **Authentication and authorization** — AD verifies user identities (typically via Kerberos) and determines what resources each user is permitted to access; it can also be used to implement **SSO (Single Sign-On)**.
	- **Centralized management** — Administrators can manage user accounts, permissions, and security policies from a single console on all devices rather than configuring each device individually.
	- **Policy enforcement** — AD **Group Policy Objects (GPOs)** can be used to enforce security settings across all devices in the domain.
	- **Resource organization** — AD uses a hierarchical structure of **domains, trees, and forests** to logically organize network resources.

>[!note] Around 95% of [Fortune 500](https://en.wikipedia.org/wiki/Fortune_500) companies run Active Directory.

>[!note] See [`Active Directory Domain Services overview — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview).

## Directory structure and administrative boundaries

### Forests

(write a better definition)

>A **forest** is is the highest level of organization in Active Directory that serves as a logical container that holds one or more **domains** and represents the ultimate security boundary.

>A **forest** is the highest-level logical structure in Active Directory that encompasses one or more **domains** that share a common directory schema, configuration, and Global Catalog.

- A forest contains or more **directory trees**, which in turn contain multiple domains.
- All domains within a forest share a common **directory schema, configuration, and Global Catalog**.
- By default, domains within the same forest are linked by **implicit two-way transitive trust relationships**, meaning that users in one domain can access resources in other domains.
- The forest acts as a distinct **security boundary**; by default, users or administrators in one forest cannot access resources in another forest unless a specific trust is established.
- Each forest operates with a **single global address list** and a unified security database for its contained objects.
- Enterprise-wide administrative roles (e.g., Enterprise Admins) operate at the forest level.

### Trees

>A **tree** is a hierarchical collection of one or more domains that share a **contiguous DNS namespace** and are connected through **transitive trust relationships**.

- All domains in the tree share the same naming structure (e.g., `domain1.example.com` under `example.com`).
- Domains in the same tree automatically establish **two-way transitive trust** (meaning if `Domain A` trusts `Domain B`, and `Domain B` trusts `Domain C`, then `Domain A` implicitly trusts `Domain C`).
- A tree begins with a single **root domain** and branches out into peripheral **child domains**, all sharing a common directory schema, configuration, and global catalog.
- Multiple trees may coexist within a single forest.

>[!important] Trees do not constitute security boundaries.

### Domains

>A **domain** is a logical grouping of network objects, such as users, computers, and groups, that share the same **Active Directory database**, administrative boundaries, and security policies.

>A **domain** is a logical administrative and replication unit that stores directory objects and provides centralized authentication, authorization, and policy enforcement for those objects.

- A domain is a fundamental administrative unit in AD. It stores users, computers, groups, and other objects.
- Each domain is managed by one or more **Domain Controllers (DCs)**.
- Policies are commonly applied at the domain level.
- Domains replicate independently while remaining members of the forest.


### Organizational Units (OUs)

>An **Organizational Unit (OU)** is a logical container within a domain used to organize directory objects, delegate administrative authority, and apply Group Policy Objects (GPOs).


- OUs exist only inside a domain.
- They are used for administrative delegation and to support hierarchical organization.
- OUs are the primary scope for applying Group Policies. 
- An OU does not represent a security boundary.

### Site

>A **site** is a representation of the physical network topology, consisting of one or more well-connected IP subnets, used to optimize authentication and replication traffic.

- Site represents physical rather than logical organization. It optimizes client logon and reduces WAN replication traffic.
- It also determines preferred DCs and is independent of domains and forests.
## Directory infrastructure

### Domain Controllers (DCs)

>A **Domain Controller (DC)** is a Windows Server that hosts the Active Directory Domain Services database and provides authentication, authorization, replication, and directory services to domain members.

- A DC stores a writable copy of the **directory database, `NTDS.dit`**.
- It is responsible for authenticating users and computers, issuing Kerberos tickets, processing LDAP requests, participating in directory replication, and often provides DNS services for the domain.
### Read-Only Domain Controllers (RODCs)

>A **Read-Only Domain Controller (RODC)** is a  Domain Controller that maintains a read-only replica of the Active Directory database to improve security in locations with limited physical protection.

- A RODC can't update the database (can't write to it); it just replicates changes from writable DCs.
### Active Directory database

>The **Active Directory database** is the Extensible Storage Engine (ESE) database that stores all directory objects, attributes, and security information within a domain.

- The database is stored the **`NTDS.dit`** file on DCs.

### Schema

>A **[schema](https://learn.microsoft.com/en-us/windows/win32/ad/schema)** is the formal definition of all object classes and attributes that may exist within the directory service.

- One schema is shared by the entire forest, so schema changes replicate forest-wide.
### Global Catalog (GC)

>The **[Global Catalog](https://learn.microsoft.com/en-us/windows/win32/ad/global-catalog)** is a distributed data repository that contains a complete replica of objects from its local domain and a partial replica of objects from every other domain in the forest.

- A GC is what enables forest-wide searches. It accelerates user logon and resolves Universal Group memberships.
- GCs support Microsoft Exchange.
- They are usually hosted on selected DCs.
### Replication

>**Replication** is the distributed synchronization process through which Active Directory maintains consistent directory information across all Domain Controllers.

## Directory objects

### Object

>An **object** in Active Directory is an individual directory entry representing a resource, identity, or service, uniquely identified by its attributes.

- An object is a basic unit of the directory; it's defined by the schema.
- Each object has a **Distinguished Name (DN)** and a **Globally Unique Identifier (GUID)**.
- Depending on object type (specifically, for security principals), it may have a **Security Identifier (SID)**.
- The are two main types of objects:
	- **Container objects** — hold other objects and have a defined place in the directory subtree hierarchy. (?)
	- **Leaf objects** — do not contain other object and are found at the end of the subtree hierarchy. (?)
### Distinguished Name (DN)

>A **[Distinguished Name (DN)](https://learn.microsoft.com/en-us/previous-versions/windows/desktop/ldap/distinguished-names)** is the unique hierarchical identifier that specifies the exact location of an object within the directory tree.

- A DN uniquely identifiers an object and represents object hierarchy.
- DNs are used in LDAP queries.
- If an object is moved, its DN changes (because it points to the object's location the directory).

- Example DN:

```
CN=John Doe,OU=DevOps,DC=Fabrikam,DC=COM
```

```
CN=Jane Doe,CN=admin,DC=corp,DC=Fabrikam,DC=COM
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

>A **[Relative Distinguished Name (RDN)](https://docs.microsoft.com/en-us/windows/win32/ad/object-names-and-identities)** is the attribute-value pair that uniquely identifies an object relative to its parent container. 

- It is the first component of an object's DN and is determined by the object's most specific structural class upon creation, typically using the **Common Name (CN)** attribute for users and groups, or **Organizational Unit (OU)** for organizational units.
- The RDN follows the syntax `attribute=value` (e.g., `CN=John Doe` or `OU=DevOps`). While the **Distinguished Name** provides the full hierarchical path to the object (e.g., `CN=John Smith,CN=Users,DC=example,DC=com`), the RDN specifically refers to the leaf-level identifier (`CN=John Smith`).

### Globally Unique Identifier (GUID)

>A **Globally Unique Identifier (GUID)** is a permanent, immutable 128-bit identifier assigned to every Active Directory object.

- Unlike DN, GUID never changes. It remains the same even after an object is renamed. 
- GUIDs are used internally by AD and are globally unique (as follows from the name).
- Every single object created by Active Directory is assigned a GUID, not only user and group objects (unlike SIDs).
- The GUID is stored in the `ObjectGUID` attribute.
### Attribute

>An **attribute** is an individual property associated with an Active Directory object, defined by the directory schema.

- Attributes store information about an object. For example, `mail`, `displayName`, or `memberOf`.
- Schema defines allowed attributes. 
- An attribute may be indexed for efficient search.

---

- [`sAMAccountName`](https://docs.microsoft.com/en-us/windows/win32/ad/naming-properties#samaccountname) — the user's logon name.
- [`userPrincipalName`](https://social.technet.microsoft.com/wiki/contents/articles/52250.active-directory-user-principal-name.aspx) (optional) — `<username>@<domain>`, e.g., `jdoe@example.com`.

## Identity and Security Principals

### Security principals


>A **[security principal](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-principals)** is any object that has a **Security Identifier (SID)** and can be assigned permissions or act as a trustee in an Access Control Entry (ACE).

- Examples of security principals include **user accounts**, **computer accounts**, and **security groups**.
- Examples of security principals include **user accounts**, **computer accounts**, and **security groups**.
- Conversely, objects such as **Organizational Units (OUs)**, **containers**, **contacts**, and **distribution groups** are **not** security principals because they lack a SID and can't be directly granted permissions.

### User accounts

>A **user account** is a security principal representing an individual identity capable of authenticating to Active Directory.

- Represents a human user.
- Receives a Security Identifier (SID).
- Authenticates via Kerberos or NTLM.
- May belong to multiple security groups.
- Can own resources.
### Computer accounts

>A **computer account** is a security principal that represents a domain-joined computer that authenticates to Active Directory.

- A computer account is created automatically when the computer joins a domain.
- Each computer account has its own password (rotated automatically).
- It's required for domain authentication.
- Each computer account receives a unique SID (same as user accounts and security groups).
### Groups

>A **group** is a collection of security principals managed as a single unit to simplify permission assignment and administrative management.

- A group may contain users, computers, and other groups.
- Security groups receive SIDs and are used to simplify authorization.

- Includes Global, Domain Local, and Universal scopes (what are even scopes)

>[!note] See [[🛠️ AD users and groups]].

### Service accounts

>A **service account** is a security principal used by applications and services to authenticate and access network resources.

- Service accounts are used by server applications; they can authenticate like user accounts. 
- They support delegated permissions.
- Modern deployments prefer Group Managed Service Accounts (gMSAs).
- Password management may be automated.

### Contacts


### SIDs

>A **Security Identifier (SID)** is a unique, immutable identifier assigned to every security principal and used internally by Windows for authorization decisions.

- SIDs are used instead of usernames and are never reused. 
- They are used in ACLs.
- They remain constant after account renaming.

### FSMO roles

>**[`Flexible Single Master Operation (FSMO) roles`](https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/fsmo-roles)**


| **Roles**                  | **Description**                                                                                                                                                                                                                                                                                                    |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `Schema Master`            | This role manages the read/write copy of the AD schema, which defines all attributes that can apply to an object in AD.                                                                                                                                                                                            |
| `Domain Naming Master`     | Manages domain names and ensures that two domains of the same name are not created in the same forest.                                                                                                                                                                                                             |
| `Relative ID (RID) Master` | The RID Master assigns blocks of RIDs to other DCs within the domain that can be used for new objects. The RID Master helps ensure that multiple objects are not assigned the same SID. Domain object SIDs are the domain SID combined with the RID number assigned to the object to make the unique SID.          |
| `PDC Emulator`             | The host with this role would be the authoritative DC in the domain and respond to authentication requests, password changes, and manage Group Policy Objects (GPOs). The PDC Emulator also maintains time within the domain.                                                                                      |
| `Infrastructure Master`    | This role translates GUIDs, SIDs, and DNs between domains. This role is used in organizations with multiple domains in a single forest. The Infrastructure Master helps them to communicate. If this role is not functioning properly, Access Control Lists (ACLs) will show SIDs instead of fully resolved names. |
## Key protocols

### NTLM

>See [[🛠️ NTLM]].
### Kerberos

[Kerberos](https://en.wikipedia.org/wiki/Kerberos_\(protocol\))


>[!note] See [[🛠️ Kerberos]].

### LDAP

 [Lightweight Directory Access Protocol (LDAP)](https://en.wikipedia.org/wiki/Lightweight_Directory_Access_Protocol)

### DNS

[DNS](https://en.wikipedia.org/wiki/Domain_Name_System)

### MSRPC

 [MSRPC](https://ldapwiki.com/wiki/MSRPC) which is the Microsoft implementation of [Remote Procedure Call (RPC)](https://en.wikipedia.org/wiki/Remote_procedure_call)
## Policy and administrative management

### Group Policies

>**Group Policy** is the centralized management framework through which administrators configure operating systems, users, and applications across an Active Directory environment.

- Centralized configuration management.
- Applied through Group Policy Objects (GPOs).
- Supports computer and user settings.
- Processes according to LSDOU order (Local, Site, Domain, Organizational Unit).
- Enables security baselines, software deployment, scripts, and administrative restrictions.
### Group Policy Objects (GPOs)

>A **Group Policy Object (GPO)** is a collection of policy settings stored within Active Directory and linked to sites, domains, or Organizational Units for automated configuration management.

- Contains administrative settings.
- Linked to Sites, Domains, or OUs.
- May contain thousands of policy settings.
- Supports inheritance and precedence.
- Replicated among Domain Controllers.

### DNS

>The **Domain Name System (DNS)** is the distributed naming service used by Active Directory to locate Domain Controllers and directory services.

- Required for normal AD operation.
- Stores Service (SRV) records.
- Enables Domain Controller discovery.
- Supports Kerberos authentication.
- Often integrated directly with Active Directory.
### Trust relationships

>A **trust** is a security relationship established between domains or forests that enables authenticated users in one security boundary to access resources in another, subject to authorization.

Trust types

| **Trust Type** | **Description**                                                                                                                                                        |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Parent-child` | Domains within the same forest. The child domain has a two-way transitive trust with the parent domain.                                                                |
| `Cross-link`   | a trust between child domains to speed up authentication.                                                                                                              |
| `External`     | A non-transitive trust between two separate domains in separate forests which are not already joined by a forest trust. This type of trust utilizes SID filtering.     |
| `Tree-root`    | a two-way transitive trust between a forest root domain and a new tree root domain. They are created by design when you set up a new tree root domain within a forest. |
| `Forest`       | a transitive trust between two forest root domains.                                                                                                                    |

Trusts can be transitive or non-transitive.

- A transitive trust means that trust is extended to objects that the child domain trusts.
- In a non-transitive trust, only the child domain itself is trusted.

Trusts can be set up to be one-way or two-way (bidirectional).

- In bidirectional trusts, users from both trusting domains can access resources.
- In a one-way trust, only users in a trusted domain can access resources in a trusting domain, not vice-versa. The direction of trust is opposite to the direction of access.
## References and further reading

- [`Active Directory Domain Services overview — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview)

- Add (idk where in the structure, maybe just mention in necessary sections depending on the importance)
	- [`Tombstone`](https://ldapwiki.com/wiki/Wiki.jsp?page=Tombstone)
	- [`AD Recycle Bin`](https://techcommunity.microsoft.com/t5/ask-the-directory-services-team/the-ad-recycle-bin-understanding-implementing-best-practices-and/ba-p/396944)
	- [`SYSVOL`](https://social.technet.microsoft.com/wiki/contents/articles/8548.active-directory-sysvol-and-netlogon.aspx)
	- [`AdminSDHolder`](https://docs.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/appendix-c--protected-accounts-and-groups-in-active-directory)
	- [`dsHeuristics`](https://docs.microsoft.com/en-us/windows/win32/adschema/a-dsheuristics)
	- [`Protected Groups`](https://docs.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/appendix-c--protected-accounts-and-groups-in-active-directory)
	- [`adminCount`](https://docs.microsoft.com/en-us/windows/win32/adschema/a-admincount)
	- `ADSI Edit`
	- `sIDHistory`
	- `NTDS.DIT`
	- shared folder

|                           |                                                                                                                                                                                                                                                                                  |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `UserPrincipalName` (UPN) | This is the primary logon name for the user. By convention, the UPN uses the email address of the user.                                                                                                                                                                          |
| `ObjectGUID`              | This is a unique identifier of the user. In AD, the ObjectGUID attribute name never changes and remains unique even if the user is removed.                                                                                                                                      |
| `SAMAccountName`          | This is a logon name that supports the previous version of Windows clients and servers.                                                                                                                                                                                          |
| `objectSID`               | The user's Security Identifier (SID). This attribute identifies a user and its group memberships during security interactions with the server.                                                                                                                                   |
| `sIDHistory`              | This contains previous SIDs for the user object if moved from another domain and is typically seen in migration scenarios from domain to domain. After a migration occurs, the last SID will be added to the `sIDHistory` property, and the new SID will become its `objectSID`. |

| | |
|---|---|
|`UserPrincipalName` (UPN)|This is the primary logon name for the user. By convention, the UPN uses the email address of the user.|
|`ObjectGUID`|This is a unique identifier of the user. In AD, the ObjectGUID attribute name never changes and remains unique even if the user is removed.|
|`SAMAccountName`|This is a logon name that supports the previous version of Windows clients and servers.|
|`objectSID`|The user's Security Identifier (SID). This attribute identifies a user and its group memberships during security interactions with the server.|
|`sIDHistory`|This contains previous SIDs for the user object if moved from another domain and is typically seen in migration scenarios from domain to domain. After a migration occurs, the last SID will be added to the `sIDHistory` property, and the new SID will become its `objectSID`.|

#### Domain functional levels

| Domain Functional Level | Features Available                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Supported Domain Controller Operating Systems                                                                 |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------- |
| Windows 2000 native     | Universal groups for distribution and security groups, group nesting, group conversion (between security and distribution and security groups), SID history.                                                                                                                                                                                                                                                                                                                               | Windows Server 2008 R2, Windows Server 2008, Windows Server 2003, Windows 2000                                |
| Windows Server 2003     | Netdom.exe domain management tool, lastLogonTimestamp attribute introduced, well-known users and computers containers, constrained delegation, selective authentication.                                                                                                                                                                                                                                                                                                                   | Windows Server 2012 R2, Windows Server 2012, Windows Server 2008 R2, Windows Server 2008, Windows Server 2003 |
| Windows Server 2008     | Distributed File System (DFS) replication support, Advanced Encryption Standard (AES 128 and AES 256) support for the Kerberos protocol, Fine-grained password policies                                                                                                                                                                                                                                                                                                                    | Windows Server 2012 R2, Windows Server 2012, Windows Server 2008 R2, Windows Server 2008                      |
| Windows Server 2008 R2  | Authentication mechanism assurance, Managed Service Accounts                                                                                                                                                                                                                                                                                                                                                                                                                               | Windows Server 2012 R2, Windows Server 2012, Windows Server 2008 R2                                           |
| Windows Server 2012     | KDC support for claims, compound authentication, and Kerberos armoring                                                                                                                                                                                                                                                                                                                                                                                                                     | Windows Server 2012 R2, Windows Server 2012                                                                   |
| Windows Server 2012 R2  | Extra protections for members of the Protected Users group, Authentication Policies, Authentication Policy Silos                                                                                                                                                                                                                                                                                                                                                                           | Windows Server 2012 R2                                                                                        |
| Windows Server 2016     | [Smart card required for interactive logon](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/interactive-logon-require-smart-card) new [Kerberos](https://docs.microsoft.com/en-us/windows-server/security/kerberos/whats-new-in-kerberos-authentication) features and new [credential protection](https://docs.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/whats-new-in-credential-protection) features | Windows Server 2019 and Windows Server 2016                                                                   |
#### Forest functional levels

| **Version**              | **Capabilities**                                                                                                                                                                                               |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Windows Server 2003`    | saw the introduction of the forest trust, domain renaming, read-only domain controllers (RODC), and more.                                                                                                      |
| `Windows Server 2008`    | All new domains added to the forest default to the Server 2008 domain functional level. No additional new features.                                                                                            |
| `Windows Server 2008 R2` | Active Directory Recycle Bin provides the ability to restore deleted objects when AD DS is running.                                                                                                            |
| `Windows Server 2012`    | All new domains added to the forest default to the Server 2012 domain functional level. No additional new features.                                                                                            |
| `Windows Server 2012 R2` | All new domains added to the forest default to the Server 2012 R2 domain functional level. No additional new features.                                                                                         |
| `Windows Server 2016`    | [Privileged access management (PAM) using Microsoft Identity Manager (MIM).](https://docs.microsoft.com/en-us/windows-server/identity/whats-new-active-directory-domain-services#privileged-access-management) |



- During post-exploitation, accounts with `adminCount=1` are high-value targets — they historically held elevated privileges even if they have since been removed from protected groups.