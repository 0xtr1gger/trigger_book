---
created: 2026-08-14
updated: 2026-10-11
tags:
  - AD
  - AD_attacks
  - enumeration
status: substantial
---
>[!abstract] Objective: **interrogate Active Directory via LDAP to enumerate directory objects and their attributes; gather information about the domain**.

- [ ] Query RootDSE.
- [ ] Determine `BASE`, `CONFIG`, Schema, and DNS naming contexts.
- [ ] Verify LDAP/LDAPS/Global Catalog connectivity.
- [ ] Enumerate users.
- [ ] Enumerate enabled, disabled, stale, and privileged users.
- [ ] Enumerate groups and recursive memberships.
- [ ] Enumerate computers and Domain Controllers.
- [ ] Enumerate OUs and GPO links.
- [ ] Enumerate GPO objects.
- [ ] Retrieve default password and lockout policy.
- [ ] Enumerate Fine-Grained Password Policies.
- [ ] Enumerate trusts.
- [ ] Find users susceptible to [[AS-REP roasting]].
- [ ] Find users susceptible to [[Kerberoasting]].
- [ ] Enumerate unconstrained delegation.
- [ ] Enumerate constrained delegation.
- [ ] Enumerate RBCD.
- [ ] Check legacy LAPS.
- [ ] Check Windows LAPS.
- [ ] Enumerate gMSAs and managed-password access.
- [ ] Check BitLocker recovery information.
- [ ] Search free-text attributes for sensitive data.
- [ ] Review `SIDHistory`.
- [ ] Enumerate AD-integrated DNS.
- [ ] Discover AD CS.
- [ ] Collect ACL relationships.
- [ ] Perform BloodHound collection.
## `ldapsearch`

>[`ldapsearch`](https://man.archlinux.org/man/ldapsearch.1.en) is a command-line utility that allows users to query and interact with LDAP directory services.

- `ldapsearch` syntax:

```bash
ldapsearch -x -LLL -H ldap://<target> -b '<base_DN>' '<filter>' <attributes>
```

- Common options:

| Option                | Description                                                                                           |
| --------------------- | ----------------------------------------------------------------------------------------------------- |
| `-H`                  | LDAP Server URI (e.g., `ldap://10.10.11.5` or `ldaps://10.10.11.5:636`).                              |
| `-x`                  | Use simple authentication (username/password instead of SASL).                                        |
| `-b`                  | Base DN to start the search from (e.g., `DC=example,DC=com`); normally required for subtree searches. |
| `-s`                  | Search scope: `base`, `one`, `sub` (subtree), or `children` (default: `sub`).                         |
| `-D`                  | Bind DN (e.g., `jdoe@example.com` or `CN=User,DC=example,DC=com`).                                    |
| `-w`                  | Provide bind password inline.                                                                         |
| `-W`                  | Prompt for password interactively.                                                                    |
| `-LLL`                | Suppress LDIF comments and version headers.                                                           |
| `-E pr=1000/noprompt` | Use paged results to avoid AD size limits.                                                            |
>[!note] See [[#Appendix A ldapsearch option reference]].

### Search bases and scopes

- The **search base (base DN)** defines the starting point in the directory tree where the query begins.
- The **search scope** determines how deep relative to that base LDAP searches.

| Search scope    | Description                                                                                                                                                 |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `base`          | `baseObject`<br>Limits the search to **only the entry** specified as the search base; doesn't search any subordinates.                                      |
| `one`           | `singleLevel`<br>Searches **only the immediate children** of the search base; doesn't include the base entry itself, nor does it search deeper descendants. |
| `sub` (default) | `wholeSubtree`<br>Searches **the entire subtree** starting from the search base, including the base entry itself and all the descendants to any depth.      |
| `children`      | `subordinateSubtree`<br>Similar to `one`, but requires support for LDAPv3 subordinate feature extension.                                                    |

>[!note] See [`The LDAP Search Operation — ldap.com`](https://ldap.com/the-ldap-search-operation/).

## Querying RootDSE (anonymously)

- Query the RootDSE:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b '' -s base '(objectClass=*)'
```

- Important values:
	- `defaultNamingContext` — distinguished name (DN) of the directory’s default domain partition.
    - `configurationNamingContext` — DN of the Configuration partition (contains forest-wide configuration data).
    - `schemaNamingContext` — DN of the Schema partition (defines object classes and attributes).
    - `rootDomainNamingContext` — DN of the forest’s root domain partition.
    - `dnsHostName` — DNS hostname of the LDAP/Active Directory server.
    - `namingContexts` — list of directory partitions (naming contexts) hosted or known by the server.
    - `supportedControl` — LDAP controls/OIDs supported by the server.
    - `supportedCapabilities` — server capabilities/features identified by OIDs.
    - `supportedLDAPVersion` — LDAP protocol versions supported by the server, typically version 3.
    - `supportedSASLMechanisms` — SASL authentication mechanisms supported by the server.

>[!important] Many RootDSE attributes are intentionally readable without authentication even when normal anonymous LDAP searches of the directory are disabled.

>[!important] Anonymous RootDSE read does not imply anonymous LDAP search is permitted.
>

>[!info] Querying RootDSE is the only case where you can specify an base DN (`-b ''`). Normal LDAP searches generally require a non-empty base DN (e.g., `DC=example,DC=com`).
### Determining LDAP naming contexts

- Retrieve the main domain base DN explicitly:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b '' -s base '(objectClass=*)' defaultNamingContext
```

- Retrieve the configuration partition:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b '' -s base '(objectClass=*)' configurationNamingContext
```

- Retrieve the schema partition:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b '' -s base '(objectClass=*)' schemaNamingContext
```

- Retrieve all naming contexts:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b '' -s base '(objectClass=*)' namingContexts
```

### Identifying the Domain Controller 

- Retrieve the DNS hostname of the LDAP server:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b '' -s base '(objectClass=*)' dnsHostName 
```

- Retrieve server and directory service information:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b '' -s base '(objectClass=*)' dnsHostName serverName dsServiceName
```

### LDAP capabilities and controls

- Enumerate supported LDAP versions:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b '' -s base '(objectClass=*)' supportedLDAPVersion
```

- Enumerate supported SASL mechanisms:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b '' -s base '(objectClass=*)' supportedSASLMechanisms
```

- Enumerate LDAP controls:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b '' -s base '(objectClass=*)' supportedControl
```

- Enumerate AD-specific LDAP capabilities:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b '' -s base '(objectClass=*)' supportedCapabilities
```

### LDAP, StartTLS, LDAPS

- Test normal LDAP over TCP port `389`:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5:389 -b '' -s base '(objectClass=*)' defaultNamingContext
```

- Test LDAP with StartTLS:

```bash
ldapsearch -x -LLL -ZZ -H ldap://10.10.11.5:389 -b '' -s base '(objectClass=*)' defaultNamingContext
```

>[!note] `-ZZ` requires successful StartTLS negotiation.

- Test LDAPS:

```bash
ldapsearch -x -LLL -H ldaps://10.10.11.5:636 -b '' -s base '(objectClass=*)' defaultNamingContext
```

## Testing for anonymous and Guest LDAP bind

- Test for an anonymous LDAP bind (attempting to read the domain object):

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s base '(objectClass=domain)' distinguishedName objectSid
```

- Test for a Guest bind:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -D 'Guest' -w '' -b 'DC=example,DC=com' -s base '(objectClass=domain)' distinguishedName objectSid
```

> [!warning] By default, Windows Server 2003 and later restrict anonymous LDAP access to directory objects. However, misconfigurations that allow anonymous access are still fairly common.

## Querying Global Catalog

- Query the Global Catalog using TCP port `3268`:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5:3268 -b 'DC=example,DC=com' -s sub '(objectClass=*)' distinguishedName
```

- Query the Global Catalog over TLS using TCP port `3269`:

```bash
ldapsearch -x -LLL -H ldaps://10.10.11.5:3269 -b 'DC=example,DC=com' -s sub '(objectClass=*)' distinguishedName
```

> [!note]+ Querying the Global Catalog (`3268` / `3269`) vs. standard LDAP (`389` / `636`)
> 
> - Standard LDAP queries on ports `389` / `636` search the directory partition of the **current domain** and can return the full set of attributes available for its objects.
> - The Global Catalog on ports `3268` / `3269` searches **across all domains in the AD forest**.
> - To make forest-wide searches efficient, the Global Catalog stores only a **partial attribute set (PAS)** for each object. As a result, some attributes may not be available through the Global Catalog and must be queried directly against the object's domain over standard LDAP.
> - In practice, use the Global Catalog when you need to **discover objects across the forest**, then query the appropriate DC over `389` / `636` if you need attributes that are not replicated to the Global Catalog.

## Enumerating domain information

- Retrieve the domain object:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s base '(objectClass=domain)'
```

## Enumerating users

- Enumerate **all user objects representing people**:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s sub '(&(objectCategory=person)(objectClass=user))' sAMAccountName userPrincipalName mail
```

- Enumerate **enabled users**:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s sub '(&(objectCategory=person)(objectClass=user)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))' sAMAccountName userPrincipalName distinguishedName
```

>[!note] The LDAP matching rule `1.2.840.113556.1.4.803` performs a bitwise `AND` operation against integer attributes such as `userAccountControl`. See [[🛠️ LDAP#Bitwise matching rules (Extensible Match OIDs)]].

- Enumerate **disabled users**:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s sub '(&(objectCategory=person)(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=2))' sAMAccountName userPrincipalName distinguishedName
```

- Enumerate accounts marked `adminCount=1` (indicates accounts currently or formerly under `AdminSDHolder` protection):

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s sub '(&(objectCategory=person)(objectClass=user)(adminCount=1))' sAMAccountName objectClass distinguishedName memberOf adminCount
```

>[!note] `adminCount=1` is not definitive proof that the account is currently privileged.

### Security checks

- Find accounts with **passwords set to never expire**:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s sub '(&(objectCategory=person)(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=65536))' sAMAccountName distinguishedName userAccountControl
```

- Find accounts marked **`PASSWD_NOTREQD`** (allows an account to have a **blank password**, ignoring domain password policies):

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s sub '(&(objectCategory=person)(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=32))' sAMAccountName distinguishedName userAccountControl
```

- Find accounts configured for **reversible password encryption**:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s sub '(&(objectCategory=person)(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=128))' sAMAccountName distinguishedName userAccountControl
```

- Find enabled users that **don't require Kerberos pre-authentication** (susceptible to [[AS-REP roasting]]):

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s sub '(&(objectCategory=person)(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=4194304)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))' sAMAccountName distinguishedName userAccountControl
```

- Enumerate user service accounts with SPNs (susceptible to [[Kerberoasting]]):

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s sub '(&(objectCategory=person)(objectClass=user)(servicePrincipalName=*))' sAMAccountName distinguishedName userAccountControl
```
## Enumerating groups

- Enumerate all groups and their direct members:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s sub  '(objectCategory=group)' cn sAMAccountName distinguishedName groupType member 
```

- Enumerate groups marked `adminCount=1`:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s sub '(&(objectCategory=group)(adminCount=1))' cn sAMAccountName distinguishedName groupType member 
```

- Enumerate the direct members of a specific group (e.g., `Domain Admins`)

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'CN=Domain Admins,CN=Users,DC=example,DC=com' -s base '(objectClass=group)' member 
```

### Recursively enumerating group membership

- Find all objects that are direct or nested members of a specific group (e.g., `Domain Admins`):

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s base '(&(objectClass=user)(memberOf:1.2.840.113556.1.4.1941:=CN=Domain Admins,CN=Users,DC=example,DC=com))' sAMAccountName distinguishedName
```


>[!note] The LDAP matching rule `1.2.840.113556.1.4.1941` performs recursive evaluation of D-valued attributes such as `memberOf`, so you can find objects that belong to a group either directly or through nested group membership.

## Enumerating computers

- Enumerate domain computer objects:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s sub '(objectCategory=computer)' sAMAccountName dNSHostName distinguishedName operatingSystem operatingSystemVersion servicePrincipalName userAccountControl msDS-SupportedEncryptionTypes
```

### Enumerating Domain Controllers

- Domain Controller machine accounts normally have the `SERVER_TRUST_ACCOUNT` flag:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s sub '(&(objectCategory=computer)(userAccountControl:1.2.840.113556.1.4.803:=8192))' sAMAccountName dNSHostName distinguishedName operatingSystem operatingSystemVersion servicePrincipalName
```

## Enumerating OUs and contains

- Enumerate Organizational Units (OUs):

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s sub '(objectClass=organizationalUnit)' ou distinguishedName gPLink gPOptions
```

- Enumerate generic container objects:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s sub  '(objectClass=container)' ou distinguishedName
```

>[!note] Containers and OUs are distinct AD object classes and should both be enumerated.

## Enumerating Group Policy Objects

- Enumerating Group Policy Objects (GPOs):

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s sub '(objectClass=groupPolicyContainer)' displayName cn distinguishedName gPCFileSysPath flags versionNumber
```

>[!note] `gPCFileSysPath` identifies the corresponding Group Policy Template in `SYSVOL`.


## Domain password and lockout policy

- Retrieve the default domain password and account lockout policy:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s base '(objectClass=domain)' minPwdLength minPwdAge maxPwdAge pwdHistoryLength pwdProperties lockoutThreshold lockoutDuration lockOutObservationWindow
```

>[!note] AD time-duration attributes are generally stored as negative 100-nanosecond intervals and require conversion for convenient interpretation.

>[!note] See [[Password and account lockout policies in AD]].
### Fine-Grained Password Policies

- Fine-Grained Password Policies are stored as Password Settings Objects under `CN=Password Settings Container,CN=System,<domain DN>`. 
- Enumerate all PSOs:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'CN=Password Settings Container,CN=System,DC=example,DC=com' '(objectClass=msDS-PasswordSettings)' \
	cn distinguishedName \ 
	msDS-PasswordSettingsPrecedence \ 
	msDS-MinimumPasswordLength \ 
	msDS-PasswordHistoryLength \ 
	msDS-MinimumPasswordAge \ 
	msDS-MaximumPasswordAge \ 
	msDS-LockoutThreshold \ 
	msDS-LockoutDuration \ 
	msDS-LockoutObservationWindow \ 
	msDS-PasswordComplexityEnabled \ 
	msDS-PasswordReversibleEncryptionEnabled \ 
	msDS-PSOAppliesTo
```

## Enumerating domain trusts

- Enumerate trust objects:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' '(objectClass=trustedDomain)' \ 
	cn distinguishedName \ 
	trustPartner trustDirection \ 
	trustType trustAttributes \ 
	securityIdentifier
```

## Unconstrained delegation

- Find accounts configured for unconstrained delegation:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s sub '(userAccountControl:1.2.840.113556.1.4.803:=524288)' sAMAccountName objectClass dNSHostName distinguishedName userAccountControl
```

- Find principals configured for classic constrained delegation:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s sub '(msDS-AllowedToDelegateTo=*)' sAMAccountName objectClass distinguishedName msDS-AllowedToDelegateTo userAccountControl
```

- Find constrained-delegation accounts with protocol transition (`TRUSTED_TO_AUTH_FOR_DELEGATION`):

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s sub '(userAccountControl:1.2.840.113556.1.4.803:=16777216)' sAMAccountName distinguishedName msDS-AllowedToDelegateTo userAccountControl
```

- Find objects configured for Resource-Based Constrained Delegation (RBCD):

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s sub '(msDS-AllowedToActOnBehalfOfOtherIdentity=*)' sAMAccountName dNSHostName distinguishedName msDS-AllowedToActOnBehalfOfOtherIdentity
```

## LAPS

- Find computers where the current identity can read legacy LAPS passwords:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s sub '(&(objectCategory=computer)(ms-Mcs-AdmPwd=*))' sAMAccountName dNSHostName distinguishedName ms-Mcs-AdmPwd ms-Mcs-AdmPwdExpirationTime
```

>[!note] If password values are returned, the bind identity has effective read access to those attributes for the returned objects.

- Find readable Windows LAPS cleartext password attributes:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s sub '(&(objectCategory=computer)(msLAPS-Password=*))' sAMAccountName dNSHostName distinguishedName msLAPS-Password msLAPS-PasswordExpirationTime
```

- Find objects containing encrypted Windows LAPS passwords:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s sub '(&(objectCategory=computer)(msLAPS-EncryptedPassword=*))' sAMAccountName dNSHostName distinguishedName msLAPS-EncryptedPassword msLAPS-PasswordExpirationTime
```

>[!note] Presence of an encrypted blob does not imply that the current identity can decrypt it.

## Group Managed Service Accounts

- Enumerate Group Managed Service Accounts (gMSAs):

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s sub '(objectClass=msDS-GroupManagedServiceAccount)' sAMAccountName distinguishedName servicePrincipalName msDS-GroupMSAMembership msDS-ManagedPasswordInterval msDS-SupportedEncryptionTypes
```

- Test whether managed-password blobs are readable by the current principal.

```bash
ldapsearch -x -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s sub '(&(objectClass=msDS-GroupManagedServiceAccount)(msDS-ManagedPassword=*))' sAMAccountName distinguishedName msDS-ManagedPassword
```

>[!note] `msDS-ManagedPassword` is a binary structure rather than a plaintext password.

## BitLocker recovery information

- Enumerate BitLocker recovery objects:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s sub '(objectClass=msFVE-RecoveryInformation)' distinguishedName msFVE-RecoveryGuid msFVE-VolumeGuid msFVE-RecoveryPassword
```

>[!note] If `msFVE-RecoveryPassword` values are returned, the current identity has read access to those credentials.

## Searching descriptive fields for sensitive information

- Search common free-text attributes:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s sub '(&(objectCategory=person)(objectClass=user)(|(description=*)(comment=*)(info=*)(userPassword=*)(userCertificate=*)))' sAMAccountName objectClass distinguishedName description comment info
```

- Search explicitly for password-related text:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s sub '(|(description=*pass*)(comment=*pass*)(info=*pass*))' sAMAccountName distinguishedName description comment info
```

>[!note] LDAP substring searches are case-insensitive for attributes using case-insensitive matching rules; behavior ultimately depends on the attribute schema.


## `windapsearch`

- Enumerate all domain user accounts via custom LDAP queries:

```bash
windapsearch -d 10.10.11.5 -u "jdoe@example.com" -p "passwd123" --dc-ip 10.10.11.5 -U
```

- Enumerate privileged domain groups and their members:

```bash
windapsearch -d 10.10.11.5 -u "jdoe@example.com" -p "passwd123" --dc-ip 10.10.11.5 -C
```

- Enumerate custom domain Unconstrained and Constrained Kerberos delegations:

```bash
windapsearch -d 10.10.11.5 -u "jdoe@example.com" -p "passwd123" --dc-ip 10.10.11.5 --delegation
```

| Option              | Description                                               |
| ------------------- | --------------------------------------------------------- |
| `-d`, `--domain`    | Target FQDN domain name or DC IP.                         |
| `-u`, `--username`  | User principal name or domain user account.               |
| `-p`, `--password`  | Cleartext password for domain authentication.             |
| `--dc-ip`           | IP address of target Domain Controller.                   |
| `-U`, `--users`     | Execute standard domain user enumeration module.          |
| `-G`, `--groups`    | Execute group membership enumeration module.              |
| `-C`, `--computers` | Execute computer domain object enumeration module.        |
| `--admin-objects`   | Query privileged administrative objects (`adminCount=1`). |
| `--da`              | Display members of Domain Admins group.                   |
| `--delegation`      | Enumerate accounts configured for Kerberos Delegation.    |
| `-m`, `--module`    | Specify custom module execution (e.g., `custom`, `gpos`). |

>[!note] See [`windapsearch`](https://github.com/ropnop/windapsearch).


## References and further reading