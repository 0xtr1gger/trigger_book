---
created: 2026-10-04
updated: 2026-10-11
tags:
  - AD_attacks
  - AD
---
## Active Directory password policy

>A **[password policy](https://en.wikipedia.org/wiki/Password_policy)** is a set of rules that defines the required password length, complexity, and restrictions on reuse, as well as how passwords must be created, managed, stored, and protected.

- In Active Directory, password policy is expressed through a set of attributes defined on the domain:
	- Minimum password length (`minPwdLength`)
	- Password complexity requirements (`pwdProperties`)
	- Password history enforcement (`pwdHistoryLength`)
	- Password age limits (`minPwdAge`, `maxPwdAge`)
	- Account lockout parameters (`lockoutThreshold`, `lockoutDuration`, `lockOutObservationWindow`)

- A password policy is enforced at two levels:
	- A single **Default Domain Password Policy** applied via [GPO (Group Policy Objects)](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/group-policy/group-policy-overview).
	- Optional **[Fine-Grained Password Policies (FGPPs)](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2008-R2-and-2008/cc770394(v=ws.10))** that override the domain default for specific users or groups.

>[!note]- Domain- and OU-level password policy GPOs
> - For domain user accounts, password and account lockout policies are enforced through *domain-level password policy settings*, normally configured in a **domain root GPO**.
> - Password and lockout policies in GPOs that are linked only to OUs **do not apply to domain accounts**, even when those accounts reside in those OUs.
### Password policy standards

- [`NIST SP 800-63B`](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-63b.pdf) — Digital Identity Guidelines (favor length over complexity, screen against breach corpuses, don't force rotation).
- [`CIS Password Policy Guide`](https://www.cisecurity.org/insights/white-papers/cis-password-policy-guide) (focuses on password length and favors passphrases over complex passwords).
- [`PCI DSS`](https://www.pcisecuritystandards.org/document_library?category=pcidss&document=pci_dss) — for cardholder-data environments.

>[!info] A **breach corpus** is a curated collection of passwords or credentials known to have been exposed in prior data breaches.
## Enumerating the password policy

- Knowing the domain password and lockout policy tells you which passwords are plausible, so you can drop candidates the policy forbids (e.g., 6-character passwords when the minimum is 8) and cut needless failed logons. Importantly, it tells you how many attempts are safe before an account locks out during [[Password spraying in AD|password spraying]].

- The domain-wide password policy is stored in the **domain root object** (`domainDNS` object, e.g., `DC=EXAMPLE,DC=COM`) in the `NTDS.dit` database and replicates across all Domain Controllers.
---
- Key `domainDNS` LDAP attributes that govern password policies:

| LDAP attribute             | Data type       | Description                                                                               |
| -------------------------- | --------------- | ----------------------------------------------------------------------------------------- |
| `minPwdLength`             | Integer         | Minimum character length required for user passwords.                                     |
| `minPwdAge`                | 64-bit Integer  | Minimum duration a password must be kept before it can be changed.                        |
| `maxPwdAge`                | 64-bit Integer  | Password expiration interval (`0x8000000000000000` = never expires).                      |
| `pwdHistoryLength`         | Integer         | Number of prior unique passwords stored to prevent reuse.                                 |
| `pwdProperties`            | Bitmask (Flags) | Domain password complexity and storage properties.                                        |
| `lockoutThreshold`         | Integer         | **Lockout threshold**; consecutive failed logon attempts before lockout (`0` = disabled). |
| `lockoutDuration`          | 64-bit Integer  | **Lockout duration**; duration an account remains locked after reaching threshold.        |
| `lockOutObservationWindow` | 64-bit Integer  | **Observation window**; sliding window during which failed attempts accumulate.           |
| `forceLogoff`              | 64-bit Integer  | Interval before forcing user logoff upon logon hours expiration.                          |

- User objects additionally carry `badPwdCount` and `badPwdTime` attributes, important for account lockout (see [[#Account lockout policy]]).
### Ways to read the policy

- There's only one password policy in AD, but multiple ways to get it:

- **SAMR over MS-RPC**
	- The [SAMR (Security Account Manager Remote)](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-samr/d0360910-33dd-4e3c-b5a2-26daf95f5ffa) RPC interface provides the `SamrQueryInformationDomain` call over SMB named pipes (`\pipe\samr`) on TCP ports `445` and `139`.
	- It returns different information depending on the levels you query:
		- Level `2` (`DomainPasswordInformation`) -> minimum password length, password history length, complexity flags, maximum/minimum password age.
		- Level `3` (`DomainLockoutInformation`) -> lockout threshold, lockout duration, observation window.
		- Level `4` (`DomainInformation`) -> domain name, server role, domain state.

- **LDAP**
	- Domain policy attributes are stored on the root `domainDNS` object (`DC=domain,DC=com`).
	- Accessible via authenticated LDAP queries or unauthenticated LDAP anonymous binds (if misconfigured) on TCP port `389` (or `636` over LDAPS).

- **`SYSVOL` GPO Template (`GptTmpl.inf`)**
	- The Default Domain Policy GPO is stored in cleartext within `SYSVOL`: `\\<domain>\sysvol\<domain>\Policies\{31B2F340-016D-11D2-945F-00C04FB984F9}\MACHINE\Microsoft\Windows NT\SecEdit\GptTmpl.inf`.
	- Because `SYSVOL` is world-readable to all domain-authenticated users (and sometimes anonymous users), you can read `GptTmpl.inf` to retrieve policy configurations directly.

- **Local SAM Policy (`net accounts`)**
	- The Windows `net accounts` utility calls `NetUserModalsGet` via SAMR. Executed on a Domain Controller, it queries the domain-wide policy; executed on a member workstation/server, it returns the local machine SAM policy.

>[!note] `badPwdCount` is tracked independently per Domain Controller — query the **PDC Emulator** directly for an absolute, domain-wide failure count. See [[#Account lockout policy]].

### From Linux

#### NetExec / CrackMapExec

- NetExec (or CrackMapExec) queries the SAMR RPC interface over SMB to extract policy details:

```bash
netexec smb 10.10.11.5 -u jdoe -p passwd123 --pass-pol
```

```bash
crackmapexec smb 10.10.11.5 -u jdoe -p passwd123 --pass-pol
```

>[!note]- Option breakdown
>- `smb` — targets the SMB service on the Domain Controller.
>- `-u` — specifies a username for authentication. 
>- `-p` — specifies a password for authentication. 
>- `--pass-pol` — invokes the password policy enumeration module via SAMR RPC calls.

>[!example]-
> ```bash
> crackmapexec smb 172.16.5.5 -u avazquez -p Password123 --pass-pol
> ```
> 
> ```bash
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  [*] Windows 10.0 Build 17763 x64 (name:ACADEMY-EA-DC01) (domain:INLANEFREIGHT.LOCAL) (signing:True) (SMBv1:False)
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  [+] INLANEFREIGHT.LOCAL\avazquez:Password123 
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  [+] Dumping password info for domain: INLANEFREIGHT
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  Minimum password length: 8
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  Password history length: 24
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  Maximum password age: Not Set
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  Password Complexity Flags: 000001
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  	Domain Refuse Password Change: 0
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  	Domain Password Store Cleartext: 0
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  	Domain Password Lockout Admins: 0
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  	Domain Password No Clear Change: 0
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  	Domain Password No Anon Change: 0
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  	Domain Password Complex: 1
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  Minimum password age: 1 day 4 minutes 
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  Reset Account Lockout Counter: 30 minutes 
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  Locked Account Duration: 30 minutes 
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  Account Lockout Threshold: 5
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  Forced Log off Time: Not Set
> ```
> - An account locks after 5 consecutive failed authentication attempts. 
> - The failure counter resets after 30 minutes without another failed attempt. 
> - Once locked, the account remains locked for 30 minutes (or until an administrator unlocks it).
> - A safe approach is to try 2-3 passwords, and then wait for 30+ minutes for each account. However, even this should be done with caution: you don't know how many failed login attempts were made during the last 30 minutes. If the failure counter is already greater than `0` when you start the attack (e.g., `4`), you may cause a lockout even with one incorrect login attempt.

#### `rpcclient`

- `rpcclient` establishes an MS-RPC connection to the target host to query SAMR directly:

```bash
rpcclient -U "jdoe%passwd123" 10.10.11.5
```

>[!note]- Option breakdown 
>- `-U "username%password"` — specifies credentials separated by `%`; for SMB `null` sessions, use `-U ""` and `-N` (no password).

```bash
rpcclient $> querydominfo
```

```bash
rpcclient $> getdompwinfo
```

- `querydominfo` issues SAMR query level `4` (`DomainInformation`); returns server role and user counts (`ROLE_DOMAIN_PDC` verifies the host is the PDC Emulator).
- `getdompwinfo` issues SAMR query level `2` (`DomainPasswordInformation`); returns minimum password length and complexity flag bitmasks.

>[!example]-
> ```bash
> rpcclient -U "" -N 172.16.5.5
> ```
> 
> ```bash
> rpcclient $> querydominfo
> 
> INLANEFREIGHT
> Server:		
> Comment:	
> Total Users:	3509
> Total Groups:	0
> Total Aliases:	203
> Sequence No:	1
> Force Logoff:	-1
> Domain Server State:	0x1
> Server Role:	ROLE_DOMAIN_PDC
> Unknown 3:	0x1
> ```
> 
> ```bash
> rpcclient $> getdompwinfo
> 
> min_password_length: 8
> password_properties: 0x00000001
> 	DOMAIN_PASSWORD_COMPLEX
> rpcclient $> 
> ```

>[!tip] Additional `rpcclient` policy inspection commands: `getdomlockoutinfo` (lockout parameters) and `getdomlogoffinfo` (logoff constraints).

#### `enum4linux-ng`

- `enum4linux-ng` automates SMB dialect negotiation, null session verification, and RPC policy dumping:

```bash
enum4linux-ng -P 10.10.11.5
```

- Flag breakdown:
	- `-P` — instructs `enum4linux-ng` to retrieve domain password and lockout policies via RPC.

>[!example]-
> ```bash
> enum4linux-ng -P 172.16.5.5
> ```
> 
> ```bash
> ENUM4LINUX - next generation
> 
>  ==========================
> |    Target Information    |
>  ==========================
> [*] Target ........... 172.16.5.5
> [*] Username ......... ''
> [*] Random Username .. 'ekrlfhpz'
> [*] Password ......... ''
> [*] Timeout .......... 5 second(s)
> 
>  ==================================
> |    Service Scan on 172.16.5.5    |
>  ==================================
> [*] Checking SMB
> [+] SMB is accessible on 445/tcp
> [*] Checking SMB over NetBIOS
> [+] SMB over NetBIOS is accessible on 139/tcp
> 
>  =======================================
> |    SMB Dialect Check on 172.16.5.5    |
>  =======================================
> [*] Trying on 445/tcp
> [+] Supported dialects and settings:
> SMB 1.0: false
> SMB 2.02: true
> SMB 2.1: true
> SMB 3.0: true
> SMB1 only: false
> Preferred dialect: SMB 3.0
> SMB signing required: true
> 
>  =======================================
> |    RPC Session Check on 172.16.5.5    |
>  =======================================
> [*] Check for null session
> [+] Server allows session using username '', password ''
> [*] Check for random user session
> [-] Could not establish random user session: STATUS_LOGON_FAILURE
> 
>  =================================================
> |    Domain Information via RPC for 172.16.5.5    |
>  =================================================
> [+] Domain: INLANEFREIGHT
> [+] SID: S-1-5-21-3842939050-3880317879-2865463114
> [+] Host is part of a domain (not a workgroup)
> 
>  =========================================================
> |    Domain Information via SMB session for 172.16.5.5    |
>  =========================================================
> [*] Enumerating via unauthenticated SMB session on 445/tcp
> [+] Found domain information via SMB
> NetBIOS computer name: ACADEMY-EA-DC01
> NetBIOS domain name: INLANEFREIGHT
> DNS domain: INLANEFREIGHT.LOCAL
> FQDN: ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL
> 
>  =======================================
> |    Policies via RPC for 172.16.5.5    |
>  =======================================
> [*] Trying port 445/tcp
> [+] Found policy:
> domain_password_information:
>   pw_history_length: 24
>   min_pw_length: 8
>   min_pw_age: 1 day 4 minutes
>   max_pw_age: not set
>   pw_properties:
>   - DOMAIN_PASSWORD_COMPLEX: true
>   - DOMAIN_PASSWORD_NO_ANON_CHANGE: false
>   - DOMAIN_PASSWORD_NO_CLEAR_CHANGE: false
>   - DOMAIN_PASSWORD_LOCKOUT_ADMINS: false
>   - DOMAIN_PASSWORD_PASSWORD_STORE_CLEARTEXT: false
>   - DOMAIN_PASSWORD_REFUSE_PASSWORD_CHANGE: false
> domain_lockout_information:
>   lockout_observation_window: 30 minutes
>   lockout_duration: 30 minutes
>   lockout_threshold: 5
> domain_logoff_information:
>   force_logoff_time: not set
> 
> Completed after 5.35 seconds
> ```

#### `ldapsearch`

- `ldapsearch` queries AD's LDAP directory directly; use it to read policy attributes from the `domainDNS` object:

```bash
ldapsearch -x -H ldap://10.10.11.5 -b "DC=EXAMPLE,DC=COM" "(objectClass=domainDNS)" minPwdLength minPwdAge maxPwdAge pwdHistoryLength pwdProperties lockoutThreshold lockoutDuration lockOutObservationWindow forceLogoff
```

>[!note]- Option breakdown 
> - `-x` — uses simple authentication (instead of SASL GSSAPI).
> - `-H ldap://10.10.11.5` — target LDAP server URI.
> - `-b "DC=EXAMPLE,DC=COM"` — base Distinguished Name (DN) for the search.
> - `"(objectClass=domainDNS)"` — LDAP search filter; targets the domain root object.
> - `minPwdLength ...` — list of specific LDAP attributes to retrieve.

>[!example]-
> ```bash
> ldapsearch -x -H ldap://172.16.5.5 -b "DC=INLANEFREIGHT,DC=LOCAL" "(objectClass=domainDNS)" minPwdLength minPwdAge maxPwdAge pwdHistoryLength pwdProperties lockoutThreshold lockoutDuration lockOutObservationWindow forceLogoff
> ```
> 
> ```bash
> # extended LDIF
> #
> # LDAPv3
> # base <DC=INLANEFREIGHT,DC=LOCAL> with scope subtree
> # filter: (objectClass=domainDNS)
> # requesting: minPwdLength minPwdAge maxPwdAge pwdHistoryLength pwdProperties lockoutThreshold lockoutDuration lockOutObservationWindow forceLogoff 
> #
> 
> # INLANEFREIGHT.LOCAL
> dn: DC=INLANEFREIGHT,DC=LOCAL
> forceLogoff: -9223372036854775808
> lockoutDuration: -18000000000
> lockOutObservationWindow: -18000000000
> lockoutThreshold: 5
> maxPwdAge: -9223372036854775808
> minPwdAge: -864000000000
> minPwdLength: 8
> pwdProperties: 1
> pwdHistoryLength: 24
> 
> # search reference
> ref: ldap://LOGISTICS.INLANEFREIGHT.LOCAL/DC=LOGISTICS,DC=INLANEFREIGHT,DC=LOC
>  AL
> 
> # search reference
> ref: ldap://ForestDnsZones.INLANEFREIGHT.LOCAL/DC=ForestDnsZones,DC=INLANEFREI
>  GHT,DC=LOCAL
> 
> # search reference
> ref: ldap://DomainDnsZones.INLANEFREIGHT.LOCAL/DC=DomainDnsZones,DC=INLANEFREI
>  GHT,DC=LOCAL
> 
> # search reference
> ref: ldap://INLANEFREIGHT.LOCAL/CN=Configuration,DC=INLANEFREIGHT,DC=LOCAL
> 
> # search result
> search: 2
> result: 0 Success
> 
> # numResponses: 6
> # numEntries: 1
> # numReferences: 4
> ```

>[!note]+ Decoding LDAP negative timestamps
> - Active Directory represents duration attributes as **negative signed 64-bit integers** representing **100-nanosecond intervals (`FILETIME`)** relative to the current time.
> - A negative value signifies a relative time interval ending at the current moment. To convert the absolute duration into seconds, take the absolute value and divide by `10,000,000` ($10^7$):
> 
> $$
> \text{seconds} = \frac{|\text{attribute value}|}{10,000,000}
> $$

| Attribute                  | Raw LDAP value         | Calculated duration                                        |
| -------------------------- | ---------------------- | ---------------------------------------------------------- |
| `lockoutDuration`          | `-18000000000`         | $18,000,000,000 / 10,000,000 = 1,800\text{ s}$ (30 min).   |
| `lockOutObservationWindow` | `-18000000000`         | $18,000,000,000 / 10,000,000 = 1,800\text{ s}$ (30 min).   |
| `minPwdAge`                | `-864000000000`        | $864,000,000,000 / 10,000,000 = 86,400\text{ s}$ (1 day).  |
| `maxPwdAge`                | `-9223372036854775808` | `0x8000000000000000` sentinel value = Not set (Unlimited). |
| `forceLogoff`              | `-9223372036854775808` | `0x8000000000000000` sentinel value = Not set.             |
| `pwdProperties`            | `1`                    | Bitmask value `0x1` enabled (Complexity required).         |
| `lockoutThreshold`         | `5`                    | Integer value = 5 failed attempts before lockout.          |

>[!note]+ `pwdProperties` bitmask values
> 
> | Bitmask value | Constant name | Meaning |
> | --- | --- | --- |
> | `0x0001` | `DOMAIN_PASSWORD_COMPLEX` | Password complexity enforced. |
> | `0x0002` | `DOMAIN_PASSWORD_NO_ANON_CHANGE` | Anonymous password change prohibited. |
> | `0x0004` | `DOMAIN_PASSWORD_NO_CLEAR_CHANGE` | Unencrypted password change prohibited. |
> | `0x0008` | `DOMAIN_PASSWORD_LOCKOUT_ADMINS` | Administrator accounts subject to lockout. |
> | `0x0010` | `DOMAIN_PASSWORD_STORE_CLEARTEXT` | Reversible encryption enabled (cleartext storage). |
> | `0x0020` | `DOMAIN_PASSWORD_REFUSE_PASSWORD_CHANGE` | User password changes prohibited. |

### From Windows

#### `net use` null session probing

- The built-in Windows `net use` command connects to SMB network shares (such as `IPC$`). 
- You can use it to check for SMB `null` sessions (or identify account status):

```powershell
net use \\DC01\ipc$ "" /u:""
```

>[!note]+ Interpreting `net use` Windows error codes
> - Even when logon fails, `net use` error messages reveal account state:
> 
> ```powershell
> net use \\DC01\ipc$ "" /u:guest
> 
> System error 1331 has occurred.
> This user can't sign in because this account is currently disabled.
> ```
> 
> ```powershell
> net use \\DC01\ipc$ "password" /u:guest
> 
> System error 1326 has occurred.
> The user name or password is incorrect.
> ```
> 
> ```
> net use \\DC01\ipc$ "password" /u:guest
> 
> System error 1909 has occurred.
> The referenced account is currently locked out and may not be logged on to.
> ```

- On a DC or a domain-joined machine, the `net accounts` command displays domain-wide password and lockout policies:

```powershell
net accounts /domain
```

>[!example]-
> ```powershell
> net accounts
> ```
> 
> ```powershell
> Force user logoff how long after time expires?:       Never
> Minimum password age (days):                          1
> Maximum password age (days):                          Unlimited
> Minimum password length:                              8
> Length of password history maintained:                24
> Lockout threshold:                                    5
> Lockout duration (minutes):                           30
> Lockout observation window (minutes):                 30
> Computer role:                                        SERVER
> The command completed successfully.
> ```

>[!note] When executed on a non-domain-joined machine, `net accounts` shows only the machine's local SAM policy; this means `net accounts /domain` fails on workgroup workstations.

- In PowerShell, use [`Get-ADDefaultDomainPasswordPolicy`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-addefaultdomainpasswordpolicy?view=windowsserver2025-ps) (`ActiveDirectory` module):

```powershell
Get-ADDefaultDomainPasswordPolicy | Select-Object ComplexityEnabled, LockoutDuration, LockoutObservationWindow, LockoutThreshold, MaxPasswordAge, MinPasswordAge, MinPasswordLength, PasswordHistoryCount
```

#### `PowerView` (`Get-DomainPolicy`)

- `PowerView`'s `Get-DomainPolicy` cmdlet reads the Default Domain Policy GPO file directly from `SYSVOL` (`GptTmpl.inf`):

```powershell
Import-Module .\PowerView.ps1
```

```powershell
Get-DomainPolicy
```

>[!example]-
> ```powershell
> PS C:\htb> Import-Module .\PowerView.ps1
> ```
> 
> ```powershell
> PS C:\htb> Get-DomainPolicy
> ```
> 
> ```powershell
> Unicode        : @{Unicode=yes}
> SystemAccess   : @{MinimumPasswordAge=1; MaximumPasswordAge=-1; MinimumPasswordLength=8; PasswordComplexity=1;
>                  PasswordHistorySize=24; LockoutBadCount=5; ResetLockoutCount=30; LockoutDuration=30;
>                  RequireLogonToChangePassword=0; ForceLogoffWhenHourExpire=0; ClearTextPassword=0;
>                  LSAAnonymousNameLookup=0}
> KerberosPolicy : @{MaxTicketAge=10; MaxRenewAge=7; MaxServiceAge=600; MaxClockSkew=5; TicketValidateClient=1}
> Version        : @{signature="$CHICAGO$"; Revision=1}
> RegistryValues : @{MACHINE\System\CurrentControlSet\Control\Lsa\NoLMHash=System.Object[]}
> Path           : \\INLANEFREIGHT.LOCAL\sysvol\INLANEFREIGHT.LOCAL\Policies\{31B2F340-016D-11D2-945F-00C04FB984F9}\MACHI
>                  NE\Microsoft\Windows NT\SecEdit\GptTmpl.inf
> GPOName        : {31B2F340-016D-11D2-945F-00C04FB984F9}
> GPO DisplayName: Default Domain Policy
> ```

>[!tip] `SharpView` (the .NET port of `PowerView`) exposes the same functionality for hosts where PowerShell is locked down.

### When you can't read the policy

- If you can't retrieve the policy, assume the out-of-the-box defaults — see [[#Default Domain Password Policy]].
- Also assume the **strictest** policy applies to everyone: a domain may enforce tighter rules on some accounts through [[#Fine-Grained Password Policies (FGPPs)]], and `DomainPasswordSpray` automatically assumes the most restrictive lockout threshold it finds (see [[Password spraying in AD#Executing password spraying from Windows]]).

## Default domain password policy

- The default domain password policy is configured in the `Default Domain Policy` GPO linked to the domain root.
- GPO path: `Computer Configuration > Policies > Windows Settings > Security Settings > Account Policies > Password Policy`.

| Policy setting                   | Default Active Directory value |
| -------------------------------- | ------------------------------ |
| Enforce password history         | 24 passwords remembered        |
| Maximum password age             | 42 days                        |
| Minimum password age             | 1 day                          |
| Minimum password length          | 7 characters                   |
| Password complexity requirements | Enabled                        |
| Reversible encryption storage    | Disabled                       |
| Account lockout threshold        | `0` (no lockout)               |
| Account lockout duration         | Not set                        |
| Lockout observation window       | Not set                        |

| Setting | Default value | Recommended (standard users) | Recommended (privileged accounts) |
| --- | --- | --- | --- |
| **Enforce password history** | `24` passwords | `24` passwords | `24` passwords |
| **Maximum password age** | `42` days | `90–365` days (or no expiry with compensating controls) | `60–90` days |
| **Minimum password age** | `1` day | `1` day | `1` day |
| **Minimum password length** | `7` characters | `14+` characters | `25+` characters |
| **Password must meet complexity requirements** | Enabled | Enabled | Enabled |
| **Store passwords using reversible encryption** | Disabled | **Disabled** (never enable) | **Disabled** |

- **Complexity requirements** (when enabled) enforce at least 3 of 5 character categories:
	- Uppercase (`A`-`Z`), lowercase (`a`-`z`), digits (`0`-`9`), non-alphanumeric (`!@#$%^&*`), Unicode characters.
- The password must not contain the user's `sAMAccountName` or `displayName` (if longer than 2 characters).

> [!warning] Complexity alone does not prevent weak passwords. `Password1!` satisfies complexity requirements but is trivially guessable. A **minimum length of 14+ characters** combined with a banned-password list is far more effective.

- View the current policy using `net accounts /domain` or `Get-ADDefaultDomainPasswordPolicy` — see [[#Enumerating the password policy]].

## Fine-Grained Password Policies (FGPPs)

> **Fine-Grained Password Policies** allow administrators to define multiple password and lockout policies within a single domain, applying stricter requirements to privileged accounts or specific groups without changing the global domain default.

- FGPPs are available since Windows Server 2008; require domain functional level 2008+. 
- FGPPs are stored as `msDS-PasswordSettings` objects (**Password Settings Objects, PSOs**) in `CN=Password Settings Container,CN=System,DC=domain,DC=local`.
- FGPPs apply to **user objects** and **global security groups** — not OUs. To target all users in an OU, create a group containing those users.

### Precedence rules

- When multiple PSOs apply to a user, the PSO with the **lowest `msDS-PasswordSettingsPrecedence` value** wins (lower = higher priority).
- A PSO applied **directly** to a user object always overrides a PSO applied via group membership, regardless of precedence value.
- If no FGPP applies, the Default Domain Password Policy is used.

---

- Create a FGPP for Tier `0` accounts:

```powershell
New-ADFineGrainedPasswordPolicy -Name "Tier0_PasswordPolicy" `
    -Precedence 10 `
    -MinPasswordLength 25 `
    -PasswordHistoryCount 24 `
    -ComplexityEnabled $true `
    -MaxPasswordAge "60.00:00:00" `
    -MinPasswordAge "1.00:00:00" `
    -LockoutThreshold 5 `
    -LockoutDuration "0.00:30:00" `
    -LockoutObservationWindow "0.00:30:00" `
    -ReversibleEncryptionEnabled $false `
    -Description "25-character minimum for Tier 0 administrative accounts"
```

- Apply to a group:

```powershell
Add-ADFineGrainedPasswordPolicySubject -Identity "Tier0_PasswordPolicy" -Subjects "Tier0-Admins"
```

---
- Create a FGPP for service accounts:

```powershell
New-ADFineGrainedPasswordPolicy -Name "ServiceAccount_PasswordPolicy" `
    -Precedence 20 `
    -MinPasswordLength 30 `
    -PasswordHistoryCount 24 `
    -ComplexityEnabled $true `
    -MaxPasswordAge "90.00:00:00" `
    -MinPasswordAge "1.00:00:00" `
    -LockoutThreshold 0 `
    -ReversibleEncryptionEnabled $false `
    -Description "30-character minimum for traditional service accounts"
```

> [!note] Setting `LockoutThreshold` to `0` (no lockout) for service accounts prevents denial-of-service against critical services. Compensate with strong passwords and monitoring.

- Query existing FGPPs:

```powershell
Get-ADFineGrainedPasswordPolicy -Filter * |
    Select-Object Name, Precedence, MinPasswordLength, MaxPasswordAge, LockoutThreshold |
    Sort-Object Precedence
```

- Determine which PSO applies to a specific user (resultant policy):

```powershell
Get-ADUserResultantPasswordPolicy -Identity "jdoe-t0"
```

## Account lockout policy

>An **account lockout policy** is a set of rules that defines when an account is locked after repeated failed login attempts, how long the lockout lasts, and when the failed-attempt counter is reset.

- The account lockout policy is configured in the `Default Domain Policy` GPO linked to the domain root (lockout settings in OU-linked GPOs are ignored for domain accounts).
-  GPO path: `Computer Configuration > Policies > Windows Settings > Security Settings > Account Policies > Account Lockout Policy`

---
- The policy is governed by three parameters, each exposed as a GPO setting and as an LDAP attribute on the `domainDNS` object:

| LDAP attribute             | Controls                                                                                          | Default        | Recommended              |
| -------------------------- | ------------------------------------------------------------------------------------------------- | -------------- | ------------------------ |
| `lockoutThreshold`         | Consecutive failed logons allowed before the account locks (`0` = lockout disabled).              | `0` (disabled) | `10–15` invalid attempts |
| `lockoutDuration`          | How long the account stays locked before auto-unlocking (`0` = locked until an admin unlocks it). | N/A            | `15–30` minutes          |
| `lockOutObservationWindow` | Sliding window after which the failed-logon counter resets to `0` if no further failures occur.   | N/A            | `15–30` minutes          |

- The failed-logon counter is tracked per user with two attributes:
	- `badPwdCount` — number of consecutive failed authentication attempts; reset to `0` on a successful logon or once the observation window (`lockOutObservationWindow`) elapses with no further failures.
	- `badPwdTime` — timestamp of the last failed authentication attempt.

### On `badPwdCount`

- The lockout *policy* is domain-wide and replicates to every DC, but **`badPwdCount` is tracked independently by each DC**. A failed authentication increments the counter **only on the DC that processed it**.
- When a failed login attempt is detected by a non-primary DC, that DC forwards that attempt to the **PDC Emulator** for verification before registering it. 
- To read an absolute, domain-wide `badPwdCount` value for an account, you need to query the **PDC Emulator** directly.

>[!note] See [[Password spraying in AD#Account lockouts]].
### Lockout trade-offs

- **Too aggressive** (e.g., 3 attempts, 24-hour lockout, manual admin unlock):
	- Becomes a **denial-of-service attack surface** — an attacker can intentionally lock out critical accounts (Domain Admins, service accounts) by spraying a few invalid passwords.
	- Overwhelms help desk staff.
- **Too permissive** (e.g., 50 attempts, 1-minute reset):
	- Permits sustained password spraying without triggering lockouts.
- The balance: `10`-`15` attempts with `15`-`30` minute auto-unlock deters spraying while avoiding self-inflicted DoS.

> [!important] The `RID-500 Administrator` account is **exempt from lockout** by default. This makes it a prime target for targeted brute-force. Rename it and consider disabling it in favour of a LAPS-managed replacement.

### Monitoring lockouts

| Event ID                                                                                                                               | Description                                      |
| -------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| [`4740`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4740) | A user account was locked out.                   |
| [`4625`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4625) | An account failed to log on (source of lockout). |
| [`4767`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4767) | A user account was unlocked.                     |

```powershell
Get-WinEvent -FilterHashtable @{ LogName='Security'; Id=4740 } -MaxEvents 50 |
    Select-Object TimeCreated, @{n='Account';e={$_.Properties[0].Value}}, @{n='CallerComputer';e={$_.Properties[1].Value}} |
    Format-Table -AutoSize
```


## References and further reading

- [`Password Policy — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/password-policy)
- [`Fine-Grained Password Policies — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/adac/introduction-to-active-directory-administrative-center-enhancements--level-100-#fine_grained_pswd_policy_mgmt)
- [`NIST SP 800-63B — Digital Identity Guidelines`](https://pages.nist.gov/800-63-3/sp800-63b.html)
- [`Microsoft Entra Password Protection — Microsoft Learn`](https://learn.microsoft.com/en-us/entra/identity/authentication/concept-password-ban-bad-on-premises)
- [`Account Lockout Policy — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/account-lockout-policy)
- [`AD DC: Fine-Grained Password Policies — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2008-R2-and-2008/cc770394(v=ws.10))
