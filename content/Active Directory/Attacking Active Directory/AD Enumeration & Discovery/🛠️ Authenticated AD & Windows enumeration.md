---
created: 2026-08-12
updated: 2026-10-11
tags:
  - AD
  - AD_attacks
  - Windows
  - enumeration
status: incomplete
---
## Initial context

- Before performing authenticated enumeration, at minimum, identify the IP address of the domain controller and an AD DNS domain. 

>[!important] Authenticated enumeration requires valid credentials (any authenticated context, no privileges required).

- Derive the Kerberos realm; it normally corresponds to the DNS domain in uppercase. 
- Determine whether the target is reachable (use ICMP ping or other probes).

>[!note] See [[External AD & Windows enumeration]].

>[!note] For DNS enumeration, see [[External AD & Windows enumeration#DNS enumeration]].
### Identifying exposed Active Directory services

- Scan the Domain Controller for common Active Directory ports:

```bash
sudo nmap -Pn -sC -p 53,88,135,139,389,445,464,636,3268,3269,3389,5985,5986 10.10.11.5
```

- Relevant ports:
	- `53/tcp,udp` — DNS
	- `88/tcp,udp` — Kerberos
	- `135/tcp` — RPC Endpoint Mapper
	- `139/tcp` — NetBIOS Session Service
	- `389/tcp` — LDAP
	- `445/tcp` — SMB / RPC over SMB
	- `464/tcp,udp` — Kerberos password change
	- `636/tcp` — LDAPS
	- `3268/tcp` — Global Catalog LDAP
	- `3269/tcp` — Global Catalog LDAPS
	- `3389/tcp` — RDP
	- `5985/tcp` — WinRM HTTP
	- `5986/tcp` — WinRM HTTPS

- Perform service detection where needed:

```bash
nmap -Pn -sV -p 53,88,389,445,636,3268,3269 10.10.11.5
```

### Validating credentials

- Test basic authenticated LDAP access:

```bash
ldapsearch -x -H 'ldap://10.10.11.5' -D 'jdoe@example.com' -w 'passwd123' -s base -b '' '(objectClass=*)' defaultNamingContext
```

- A successful result confirms basic directory read access. 

>[!info] Avoid placing passwords directly on the command line when practical; `-W` prompts for password interactively and doesn't expose it through shell history or process arguments. 

## `53` — DNS

>[!note] See [[External AD & Windows enumeration#DNS enumeration]].
## `389`/`636` — Querying LDAP

>[!note] See [[Querying LDAP]].
## `88` — Kerberos

> [!note] See [[Kerberos]] to learn more about the protocol and how it works.

- [ ] Confirm Kerberos authentication works with the supplied credentials. 
- [ ] Identify the Kerberos realm and KDCs.
- [ ] Obtain and inspect a TGT.
- [ ] Enumerate accounts that do not require Kerberos pre-authentication (candidates for [[AS-REP roasting]]).
- [ ] Enumerate accounts that have SPNs (candidates for [[Kerberoasting]]).
- [ ] Review Kerberos encryption types (where relevant).
- [ ] Review unconstrained, constrained, and resource-based constrained delegation discovered through LDAP.
- [ ] Record relevant SPNs for services such as SMB, LDAP, HTTP, MSSQL, and WinRM.
### Setting up Kerberos
#### Confirming the KDC is reachable

>[!important] By default, Kerberos KDCs use **TCP and UDP port `88`**.

- Check TCP port `88` on the Domain Controller:

```bash
nmap -Pn -sT -p 88 10.10.11.5
```

- Check UDP port `88`:

```bash
nmap -Pn -sU -p 88 10.10.11.5
```

>[!note] Kerberos supports both UDP and TCP; TCP is necessary when Kerberos messages exceed the practical UDP transport size.
#### Discovering Kerberos infrastructure through DNS

- Active Directory uses DNS `SRV` records to advertise Kerberos KDCs and related services.

- Discover Kerberos KDCs for the domain:

```bash
dig @10.10.11.5 _kerberos._tcp.example.com SRV
```

- Discover KDCs advertising Kerberos over UDP:

```bash
dig @10.10.11.5 _kerberos._udp.example.com SRV
```

- Discover Kerberos services specifically associated with Domain Controllers:

```bash
dig @10.10.11.5 _kerberos._tcp.dc._msdcs.example.com SRV
```

- Discover Kerberos password-change services (`kpasswd`, TCP/UDP port `464`):

```bash
dig @10.10.11.5 _kpasswd._tcp.example.com SRV
```

- Resolve the Domain Controller hostname:

```bash
dig @10.10.11.5 DC01.example.com A
```

>[!note] Correct DNS resolution is important because Kerberos service tickets contain SPNs (such as `ldap/DC01.example.com`, `HTTP/web01.example.com`) that are based on hostnames rather than IP addresses.

>[!note] [[External AD & Windows enumeration#DNS enumeration]] and [[Querying DNS]].

#### Verifying time synchronization

- Kerberos authentication is time-sensitive. In Active Directory, the default maximum tolerated clock skew is normally **five minutes**; excessive skew can result in errors like `KRB_AP_ERR_SKEW`.

- Check the local system time:

```bash
date
```

- Query the Domain Controller's NTP service, if available:

```bash
ntpdate -q 10.10.11.5
```

- If needed, synchronize the local clock with the Domain Controller:

```bash
sudo ntpdate 10.10.11.5
```

>[!note] `ntpdate` may not be installed on newer Linux distributions. `chrony` or another NTP client can be used instead.
#### Configuring the Linux Kerberos client

- Inspect the local Kerberos configuration (`/etc/krb5.conf`):

```bash
cat /etc/krb5.conf
```

- At minimum, the client configuration should define a realm (`EXAMPLE.COM`), KDC (`DC01.example.com`), and DNS or explicit realm-to-domain mapping.

>[!example]-
> ```bash 
> cat /etc/krb5.conf
> ```
> 
> ```bash
> [libdefaults]
>     default_realm = EXAMPLE.COM
>     dns_lookup_realm = true
>     dns_lookup_kdc = true
>     ticket_lifetime = 24h
>     renew_lifetime = 7d
>     forwardable = true
> 
> [realms]
>     EXAMPLE.COM = {
>         kdc = kdc.example.com
>         admin_server = kdc.example.com
>     }
> 
> [domain_realm]
>     .example.com = EXAMPLE.COM
>     example.com = EXAMPLE.COM   
> ```
> >[!note] `admin_server` is mainly relevant to Kerberos administrative operations and is not required simply to obtain normal AD Kerberos tickets.

#### Obtaining a TGT from using MIT Kerberos

- Request a TGT (Ticket-Granting Ticket) using known credentials:

```bash
kinit jdoe@EXAMPLE.COM
```

- `kinit` prompts for the user's password and stores the resulting TGT in the local Kerberos credential cache. Successful execution normally produces no output.
### Kerberos credential cache
##### Inspecting the Kerberos credential cache

- List cached Kerberos tickets:

```bash
klist
```

>[!note] The cache should contain a TGT similar to `krbtgt/EXAMPLE.COM@EXAMPLE.COM`. 

- Display the encryption types associated with cached tickets:

```bash
klist -e
```

- Display ticket flags:

```bash
klist -f
```

- Common ticket flags:

| Flag | Meaning     |
| ---- | ----------- |
| `F`  | forwardable |
| `f`  | forwarded   |
| `R`  | renewable   |
| `I`  | initial     |
| `P`  | proxiable   |
>[!note] Forwardable tickets are particularly relevant when testing Kerberos delegation behavior.

>[!tip]+
>- Destroy the current Kerberos credential cache when it is no longer needed:
>```bash
>kdestroy
>```

##### Using Kerberos credential caches

- Many Linux Kerberos-aware tools read tickets from the credential cache referenced by the `KRB5CCNAME` environment variable.

```bash
export KRB5CCNAME=/tmp/jdoe.ccache
```
```bash
klist
```

- This allows you to reuse an existing TGT or service ticket without supplying the account password again.
### Obtaining TGTs using Impacket

- Impacket's `getTGT.py` can obtain a TGT using a password, NT hash, or AES Kerberos key and save it as a `.ccache` file.
- Request a TGT **using a password**:

```bash
getTGT.py example.com/jdoe:'passwd123' -dc-ip 10.10.11.5
```

- Request a TGT **using an NT hash**: 

```bash
getTGT.py example.com/jdoe -hashes aad3b435b51404eeaad3b435b51404ee:8846f7eaee8fb117ad06bdd830b7586c -dc-ip 10.10.11.5
```

>[!note] The `-hashes` option expects `LM_hash:NT_hash`. If you don't have an LM hash, just submit an empty value instead (`:NT_hash`).

- Request a TGT using an AES Kerberos key (long-term key):

```bash
getTGT.py example.com/jdoe -aesKey 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef -dc-ip 10.10.11.5
```

| Option     | Description                                                                                       |
| ---------- | ------------------------------------------------------------------------------------------------- |
| `-dc-ip`   | IP address of the Domain Controller.                                                              |
| `-hashes`  | NT and/or LM hashes to use for authentication; format: `LM_hash:NT_hash` ([[Pass-the-Hash]]). |
| `-aesKey`  | AES key (128 or 256 bits) to use for authentication.                                              |
| `-no-pass` | Skip password prompts (useful with `-k`).                                                         |
| `-k`       | Authenticate using credentials from the cache (pointed to by `KRB5CCNAME` variable).              |
| `-service` | Request an ST (Service Ticket) for the specified SPN directly through the AS exchange.            |

>[!note] [`getTGT.py`](https://github.com/fortra/impacket/blob/master/examples/getTGT.py)

### Enumerating valid usernames

![[Username enumeration in AD#Username enumeration with Kerbrute]]

### Identifying accounts that don't require Kerberos pre-authentication and checking for AS-REP roasting

- Accounts that do not require Kerberos pre-authentication (those configured with `UF_DONT_REQUIRE_PREAUTH`) are susceptible to [[AS-REP roasting]].
- You can find these accounts using LDAP (as mentioned in [[Querying LDAP#Enumerating users]]):

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s sub '(&(objectCategory=person)(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=4194304)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))' sAMAccountName distinguishedName userAccountControl
```

>[!note] The `4194304` (`0x400000`) flag corresponds to `UF_DONT_REQUIRE_PREAUTH`.

- Alternatively, use Impacket's [`GetNPUsers.py`](https://github.com/fortra/impacket/blob/master/examples/GetNPUsers.py) to query the directory for accounts with this flag:

```bash
GetNPUsers.py example.com/jdoe:'passwd123' -dc-ip 10.10.11.5
```

- Request `AS-REP` responses for the discovered accounts and save them to attempt cracking it offline later:

```bash
GetNPUsers.py example.com/jdoe:'passwd123' -request -format hashcat -outputfile asrep.hashes -dc-ip 10.10.11.5
```

>[!note] `-request` requests TGT material for accounts discovered with `UF_DONT_REQUIRE_PREAUTH`.

- It is also possible to test a known list of usernames without authenticating:

```bash
GetNPUsers.py example.com/ -no-pass -usersfile users.txt -request -format hashcat -outputfile asrep.hashes -dc-ip 10.10.11.5
```

- For a specific known account:

```bash
GetNPUsers.py example.com/svc_backup -no-pass -request -dc-ip 10.10.11.5
```

- If Kerberos pre-authentication is required for the account, the KDC rejects the unauthenticated ticket request.
- If pre-authentication is disabled, the response will contain password-derived encrypted material you can try to crack offline.

>[!note] See [[AS-REP roasting]].

### Identifying accounts with SPNs and checking for Kerberoasting

- Accounts with SPNs generally represent service identities and are potential targets for [[Kerberoasting]].
- Enumerate accounts with SPNs using LDAP:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s sub '(&(objectCategory=person)(objectClass=user)(servicePrincipalName=*))' sAMAccountName distinguishedName userAccountControl servicePrincipalName
```

- You can use Impacket's [`GetUserSPN.py`](https://github.com/fortra/impacket/blob/master/examples/GetUserSPNs.py) to query Active Directory for SPNs associated with user accounts:

```bash
GetUserSPNs.py example.com/jdoe:'passwd123' -dc-ip 10.10.11.5
```

- Request STs (Service Tickets) for the discovered accounts and save the hashes into a file:

```bash
GetUserSPNs.py example.com/jdoe:'passwd123' -request -outputfile kerberoast.hashes -dc-ip 10.10.11.5
```

>[!note] `GetUserSPNs.py -request` requests TGS tickets and saves the encrypted ticket material in a format you can use for offline password cracking.

- Request an ST only for the SPN associated with a specific account:

```bash
GetUserSPNs.py example.com/jdoe:'passwd123' -request-user svc_sql -dc-ip 10.10.11.5
```

>[!note] See [[Kerberoasting]].

### Requesting service tickets

- Once you have  a valid TGT, you can request service tickets for specific SPNs. 

- Request a ticket using MIT Kerberos (`kvno`) and store it in the credential cache:

```bash
kvno cifs/DC01.example.com
```

- Confirm the ticket was added:

```bash
klist
```

- Request a ST using known credentials with Impacket's [`getST.py`](https://github.com/fortra/impacket/blob/master/examples/getST.py):

```bash
getST.py -spn cifs/DC01.example.com example.com/jdoe:'passwd123' -dc-ip 10.10.11.5
```

- Using an existing Kerberos cache:

```bash
export KRB5CCNAME=/tmp/jdoe.ccache
```
```bash
getST.py -spn cifs/DC01.example.com example.com/jdoe -k -no-pass -dc-ip 10.10.11.5
```

## `139`/`445` — SMB

>[!abstract] Objective: **interrogate Windows and Samba systems through SMB and SMB-backed MSRPC interfaces; enumerate protocol security, server information, shares, permissions, files, users, groups, sessions, policies, and related host information**.

- [ ] Confirm TCP ports `445` and, where applicable, `139`.
- [ ] Identify the SMB server, hostname, domain, OS/build, role, and time.
- [ ] Enumerate supported SMB dialects and capabilities.
- [ ] Check SMB signing.
- [ ] Check SMB encryption.
- [ ] Confirm authentication using NTLM and Kerberos separately.
- [ ] Test anonymous access where permitted.
- [ ] Enumerate shares and share descriptions.
- [ ] Determine read access without creating remote files.
- [ ] Retrieve share and filesystem ACLs.
- [ ] Enumerate `SYSVOL` and `NETLOGON`.
- [ ] Review GPO files, scripts, deployment files, and configuration data.
- [ ] Enumerate custom shares and their contents.
- [ ] Search approved shares for potentially sensitive files.
- [ ] Enumerate domain or local users and groups through SAMR.
- [ ] Enumerate group membership.
- [ ] Retrieve domain password policy through SAMR.
- [ ] Enumerate SMB sessions, connections, and logged-on users where permitted.
- [ ] Enumerate disks, services, printers, and RPC-exposed host information where permitted.
- [ ] Enumerate DFS namespaces and referrals.
- [ ] Identify administrative SMB access without executing commands.
- [ ] Correlate SMB results with LDAP, DNS, Kerberos, and BloodHound data.

| Port              | Description                                                    |
| :---------------- | -------------------------------------------------------------- |
| TCP port `445`    | SMB over TCP                                                   |
| TCP port `139`    | SMB over NetBIOS (legacy SMB transport)                        |
| UDP port `137`    | NetBIOS Name Service (legacy name registration and resolution) |
| UDP port `138`    | NetBIOS Datagram Service (legacy NetBIOS datagrams)            |
| TCP port `135`    | MSRPC Endpoint Mapper (TCP RPC endpoint discovery)             |
| Dynamic TCP ports | MSRPC                                                          |

>[!note] Modern Active Directory environments normally use SMB directly over TCP port `445`. Port `139` is relevant to legacy systems, Samba/NAS systems, or networks where NetBIOS remains enabled.

>[!note] SMB commonly transports MSRPC through named pipes under `IPC$`. SMB enumeration commands may actually use RPC inside an SMB session.

### Connectivity and basic fingerprint

- Check TCP ports `139` and `445`:

```bash
nmap -Pn -sT -p 139,445 10.10.11.5
```

- Perform service detection:

```bash
nmap -Pn -sV -p 139,445 10.10.11.5
```

>[!note] Service detection can return the NetBIOS name, DNS domain, workgroup, product, or OS details.

- Gather basic domain information, SMB signing status, OS versions, and DC names using NetExec/CrackMapExec (+ check authentication works):

```bash
nxc smb 10.10.11.0/24 -u 'jdoe' -p 'passwd123' -d 'example.com'
```

>[!example]-
> ```bash
> crackmapexec smb 172.16.5.0/24 -u forend -p Klmcargo2 -d 'inlanefreight.local'
> ```
> 
> ```bash
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  [*] Windows 10.0 Build 17763 x64 (name:ACADEMY-EA-DC01) (domain:inlanefreight.local) (signing:True) (SMBv1:False)
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  [+] inlanefreight.local\forend:Klmcargo2 
> SMB         172.16.5.130    445    ACADEMY-EA-FILE  [*] Windows 10.0 Build 17763 x64 (name:ACADEMY-EA-FILE) (domain:inlanefreight.local) (signing:False) (SMBv1:False)
> SMB         172.16.5.130    445    ACADEMY-EA-FILE  [+] inlanefreight.local\forend:Klmcargo2 (Pwn3d!)
> ```
>>[!note] For SMB targets, `(Pwn3d!)` generally indicates NetExec determined that the authenticated principal has local administrative-level access sufficient for its supported execution technique

- Enumerate SMB dialects:

```bash
nmap -Pn -p 445 --script smb-protocols 10.10.11.5
```

| Dialect           | Description                                                   |
| ----------------- | ------------------------------------------------------------- |
| SMB1 / NT LM 0.12 | Legacy SMB; obsolete and insecure.                            |
| SMB 2.0.2         | Initial SMB2 release.                                         |
| SMB 2.1           | Windows 7 / Server 2008 R2 generation.                        |
| SMB 3.0           | Adds encryption and multichannel capabilities.                |
| SMB 3.0.2         | Incremental SMBv3 revision.                                   |
| SMB 3.1.1         | Adds pre-authentication integrity and negotiation protection. |

- Enumerate SMBv2/SMBv3 capabilities:

```bash
nmap -Pn -p 445 --script smb2-capabilities 10.10.11.5
```

- Check SMB signing:

```bash
nmap -Pn -p 445 --script smb2-security-mode 10.10.11.5
```

>[!note]+ SMB signing can be one of:
>- **Required** — unsigned SMB sessions are rejected.
>- **Enabled but not required** — the server supports signing but may accept unsigned sessions.
>- **Disabled/not supported** — verify with another tool; means the server accepts unsigned sessions.

- Nmap SMB checks in one run (OS information, supported dialects, signing configuration, and server time):

```bash
nmap -Pn -n -p 445 --script smb-os-discovery,smb-protocols,smb-security-mode,smb2-security-mode,smb2-time 10.10.11.5 -oA nmap/smb_initial_info
```

- Security checks:
	- Record whether SMBv1 is enabled.
	- Identify systems that support only SMBv1.
	- Identify systems that still accept SMBv1 alongside SMBv2/SMBv3.
	- Determine the highest negotiated dialect.
	- Identify unexpected dialect differences between comparable servers.
	- Determine whether SMB 3.x encryption is supported.
	- Determine whether SMB multichannel is advertised.
	- Identify NAS or Samba implementations that behave differently from Windows SMB servers.

>[!note] SMB encryption is available in SMB 3.x; it may be enabled or required globally or on individual shares.

### Connection and authentication

>[!note] For anonymous and `Guest` access, see [[External AD & Windows enumeration#SMB null and `Guest` sessions]].
#### NTLM authentication

- Connect using Samba [`smbclient`](https://www.samba.org/samba/docs/current/man-html/smbclient.1.html):

```bash
smbclient -L //10.10.11.5 -U 'example.com/jdoe%passwd123'
```

- Connect to a specific share:

```bash
smbclient //10.10.11.5/SYSVOL -U 'example.com/jdoe%passwd123'
```

- Using Impacket's [`smbclient.py`](https://github.com/fortra/impacket/blob/master/examples/smbclient.py):

```bash
smbclient.py example.com/jdoe:passwd123@10.10.11.5
```

#### Kerberos authentication

>[!note] Kerberos SMB authentication normally uses an SPN such as `cifs/DC01.example.com`.

- Connect to `SYSVOL` and require Kerberos:

```bash
smbclient //DC01.example.com/SYSVOL --use-krb5-ccache=FILE:/tmp/jdoe.ccache -c 'ls'
```

>[!note] `--use-krb5-ccache` forces Samba to use the specified credential cache and requires Kerberos.

- Request a Kerberos-authenticated connection directly with a password:

```bash
smbclient //DC01.example.com/SYSVOL -U 'jdoe@EXAMPLE.COM%passwd123' --use-kerberos=required -c 'ls'
```

- Test with NetExec:

```bash
nxc smb DC01.example.com -u jdoe -p passwd123 -d example.com -k --kdcHost 10.10.11.5
```

- Test with Impacket:

```bash
smbclient.py -k -dc-ip 10.10.11.5 example.com/jdoe:passwd123@DC01.example.com
```

### Enumerating shares

- Enumerate shares across the domain:

```bash
Snaffler.exe -s -o example.com -d example.com
```

>[!note] See [[Credential hunting in network shares]].

- List available shares on a specific system:

```bash
smbclient -L //10.10.11.5 -U 'example.com/jdoe%passwd123'
```

```bash
nxc smb 10.10.11.5 -u 'jdoe' -p 'passwd123' --shares
```

>[!example]-
> ```bash
> crackmapexec smb 172.16.5.5 -u forend -p Klmcargo2 --shares
> ```
> 
> ```bash
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  [*] Windows 10.0 Build 17763 x64 (name:ACADEMY-EA-DC01) (domain:INLANEFREIGHT.LOCAL) (signing:True) (SMBv1:False)
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  [+] INLANEFREIGHT.LOCAL\forend:Klmcargo2 
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  [+] Enumerated shares
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  Share           Permissions     Remark
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  -----           -----------     ------
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  ADMIN$                          Remote Admin
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  C$                              Default share
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  Department Shares READ            
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  IPC$            READ            Remote IPC
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  NETLOGON        READ            Logon server share 
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  SYSVOL          READ            Logon server share 
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  User Shares     READ            
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  ZZZ_archive     READ    
> ```

```bash
smbmap -u 'jdoe' -p 'passwd123' -d 'example.com' -H 10.10.11.5
```

>[!example]-
> ```bash
> smbmap -u forend -p Klmcargo2 -H 172.16.5.5
> ```
> 
> ```bash
> [+] IP: 172.16.5.5:445	Name: inlanefreight.local                               
>         Disk                                                  	Permissions	Comment
> 	----                                                  	-----------	-------
> 	ADMIN$                                            	NO ACCESS	Remote Admin
> 	C$                                                	NO ACCESS	Default share
> 	Department Shares                                 	READ ONLY	
> 	IPC$                                              	READ ONLY	Remote IPC
> 	NETLOGON                                          	READ ONLY	Logon server share 
> 	SYSVOL                                            	READ ONLY	Logon server share 
> 	User Shares                                       	READ ONLY	
> 	ZZZ_archive                                       	READ ONLY	
> ```

- Common default SMB shares:

| Share         | Purpose                                                    |
| ------------- | ---------------------------------------------------------- |
| `IPC$`        | Named pipes and inter-process communication.               |
| `ADMIN$`      | Windows installation directory; normally administrative.   |
| `C$`, `D$`    | Administrative disk shares.                                |
| `SYSVOL`      | Group Policy and domain-public files.                      |
| `NETLOGON`    | Domain logon scripts and related files.                    |
| Custom shares | Business, application, deployment, backup, user data, etc. |

- Connect to a specific share:

```bash
smbclient //10.10.11.5/SYSVOL -U 'example.com/jdoe%passwd123'
```

```bash
smbclient //10.10.11.5/SYSVOL -U 'example.com/jdoe%passwd123' -c 'ls'
```

### Listing share files

- List readable files on a share:

```bash
nxc smb 10.10.11.5 -u 'jdoe' -p 'passwd123' -M spider_plus --share 'Department Shares'
```

>[!example]-
> ```bash
> crackmapexec smb 172.16.5.5 -u forend -p Klmcargo2 -M spider_plus --share 'Remote Admin'
> ```
> 
> ```bash
> [-] Failed loading module at /usr/lib/python3/dist-packages/cme/modules/slinky.py: No module named 'pylnk3'
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  [*] Windows 10.0 Build 17763 x64 (name:ACADEMY-EA-DC01) (domain:INLANEFREIGHT.LOCAL) (signing:True) (SMBv1:False)
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  [+] INLANEFREIGHT.LOCAL\forend:Klmcargo2 
> SPIDER_P... 172.16.5.5      445    ACADEMY-EA-DC01  [*] Started spidering plus with option:
> SPIDER_P... 172.16.5.5      445    ACADEMY-EA-DC01  [*]        DIR: ['print$']
> SPIDER_P... 172.16.5.5      445    ACADEMY-EA-DC01  [*]        EXT: ['ico', 'lnk']
> SPIDER_P... 172.16.5.5      445    ACADEMY-EA-DC01  [*]       SIZE: 51200
> SPIDER_P... 172.16.5.5      445    ACADEMY-EA-DC01  [*]     OUTPUT: /tmp/cme_spider_plus
> ```

- Recursively list share directory contents up to a specified depth:

```bash
smbmap -u 'jdoe' -p 'passwd123' -d 'example.com' -H 10.10.11.5 -R 'Department Shares' --depth 3
```

>[!example]-
> ```bash
> smbmap -u forend -p Klmcargo2 -H 172.16.5.5 -R 'Department Shares' --depth 3
> ```
> 
> ```bash
> [+] IP: 172.16.5.5:445	Name: inlanefreight.local                               
>         Disk                                                  	Permissions	Comment
> 	----                                                  	-----------	-------
> 	Department Shares                                 	READ ONLY	
> 	.\Department Shares\*
> 	dr--r--r--                0 Thu Mar 31 15:34:29 2022	.
> 	dr--r--r--                0 Thu Mar 31 15:34:29 2022	..
> 	dr--r--r--                0 Thu Mar 31 15:14:48 2022	Accounting
> 	dr--r--r--                0 Thu Mar 31 15:14:39 2022	Executives
> 	dr--r--r--                0 Thu Mar 31 15:14:57 2022	Finance
> 	dr--r--r--                0 Thu Mar 31 15:15:04 2022	HR
> 	dr--r--r--                0 Thu Mar 31 15:15:21 2022	IT
> 	dr--r--r--                0 Thu Mar 31 15:15:29 2022	Legal
> 	dr--r--r--                0 Thu Mar 31 15:15:37 2022	Marketing
> 	dr--r--r--                0 Thu Mar 31 15:15:47 2022	Operations
> 	dr--r--r--                0 Thu Mar 31 15:15:58 2022	R&D
> 	dr--r--r--                0 Thu Mar 31 15:16:10 2022	Temp
> 	dr--r--r--                0 Thu Mar 31 15:16:18 2022	Warehouse
> 	.\Department Shares\Accounting\*
> 	dr--r--r--                0 Thu Mar 31 15:14:48 2022	.
> 	dr--r--r--                0 Thu Mar 31 15:14:48 2022	..
> 	dr--r--r--                0 Thu Mar 31 15:14:46 2022	Private
> 	dr--r--r--                0 Thu Mar 31 15:14:48 2022	Public
> 	.\Department Shares\Accounting\Private\*
> 	dr--r--r--                0 Thu Mar 31 15:14:46 2022	.
> 	dr--r--r--                0 Thu Mar 31 15:14:46 2022	..
> 	fr--r--r--              278 Thu Mar 31 15:14:46 2022	AddSelect.bat
> 	fr--r--r--              289 Thu Mar 31 15:14:46 2022	ApproveConnect.wmf
> 	.\Department Shares\Accounting\Public\*
> 	dr--r--r--                0 Thu Mar 31 15:14:48 2022	.
> 	dr--r--r--                0 Thu Mar 31 15:14:48 2022	..
> 	fr--r--r--              288 Thu Mar 31 15:14:48 2022	AssertImport.reg
> 	.\Department Shares\Executives\*
> 	dr--r--r--                0 Thu Mar 31 15:14:39 2022	.
> 	dr--r--r--                0 Thu Mar 31 15:14:39 2022	..
> 	dr--r--r--                0 Thu Mar 31 15:14:39 2022	Private
> 	dr--r--r--                0 Thu Mar 31 15:14:37 2022	Public
> ```

- Search for matching filename patterns across all accessible shares:

```bash
smbmap -u 'jdoe' -p 'passwd123' -d 'example.com' -H 10.10.11.5 -F 'pass'
```

- `smbmap` options:

| Option       | Description                                                         |
| ------------ | ------------------------------------------------------------------- |
| `-H`         | Target IP address, hostname, or IP subnet.                          |
| `-u`         | Username for authentication.                                        |
| `-p`         | Password or NTLM hash (`lmhash:nthash`) for authentication.         |
| `-d`         | Domain name.                                                        |
| `-s`         | Target share to browse or operate on.                               |
| `-R`         | Recursively list directories and files on accessible shares.        |
| `--depth`    | Maximum directory recursion depth level (default: `5`).             |
| `-F`         | File search pattern.                                                |
| `--download` | Download a file from an accessible SMB share.                       |
| `--upload`   | Upload a local file to a remote SMB share.                          |
| `-x`         | Execute a command on remote host via SCM (Service Control Manager). |

### Downloading and uploading files 

- Download a remote file directly from an SMB share:

```bash
smbmap -u 'jdoe' -p 'passwd123' -d 'example.com' -H 10.10.11.5 --download 'Department Shares/IT/passwords.txt'
```

- Upload a file from the local machine to the remote share:

```bash
smbmap -u 'jdoe' -p 'passwd123' -d 'example.com' -H 10.10.11.5 --upload 'exploit.zip' 'Department Shares/IT/exploit.zip'
```

- Recursively download all contents from an exposed SMB share:

```bash
smbclient //10.10.11.5/Development -N -c 'prompt OFF; recurse ON; mget *'
```

> [!note] [`smbmap`](https://github.com/ShawnDEvans/smbmap) · [`smbclient`](https://www.samba.org/samba/docs/current/man-html/smbclient.1.html)


### Domain password policy and domain users

- Retrieve domain password policy:

```bash
nxc smb 10.10.11.5 -u 'jdoe' -p 'passwd123' --pass-pol
```

>[!example]-
> ```bash
> crackmapexec smb 172.16.5.5 -u forend -p Klmcargo2 --pass-pol
> ```
> 
> ```bash
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  [*] Windows 10.0 Build 17763 x64 (name:ACADEMY-EA-DC01) (domain:INLANEFREIGHT.LOCAL) (signing:True) (SMBv1:False)
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  [+] INLANEFREIGHT.LOCAL\forend:Klmcargo2 
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

>[!note] See [[Password and account lockout policies in AD#Enumerating the password policy]].

- Enumerate domain users:

```bash
nxc smb 10.10.11.5 -u 'jdoe' -p 'passwd123' --users
```

>[!example]-
> ```bash
> crackmapexec smb 172.16.5.5 -u forend -p Klmcargo2 --users
> ```
> 
> ```bash
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  [*] Windows 10.0 Build 17763 x64 (name:ACADEMY-EA-DC01) (domain:INLANEFREIGHT.LOCAL) (signing:True) (SMBv1:False)
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  [+] INLANEFREIGHT.LOCAL\forend:Klmcargo2 
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  [+] Enumerated domain user(s)
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  INLANEFREIGHT.LOCAL\administrator                  badpwdcount: 1 baddpwdtime: 2026-07-22 05:01:40.034946
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  INLANEFREIGHT.LOCAL\guest                          badpwdcount: 0 baddpwdtime: 1600-12-31 19:03:58
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  INLANEFREIGHT.LOCAL\lab_adm                        badpwdcount: 0 baddpwdtime: 2026-07-22 05:01:06.175589
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  INLANEFREIGHT.LOCAL\krbtgt                         badpwdcount: 0 baddpwdtime: 1600-12-31 19:03:58
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  INLANEFREIGHT.LOCAL\htb-student                    badpwdcount: 0 baddpwdtime: 2022-03-30 16:27:41.960920
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  INLANEFREIGHT.LOCAL\avazquez                       badpwdcount: 3 baddpwdtime: 2022-02-24 18:10:01.903395
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  INLANEFREIGHT.LOCAL\pfalcon                        badpwdcount: 3 baddpwdtime: 2022-02-24 18:10:01.919005
> ```

- Enumerate domain groups:

```bash
nxc smb 10.10.11.5 -u 'jdoe' -p 'passwd123' --groups
```

>[!example]-
> ```bash
> crackmapexec smb 172.16.5.5 -u forend -p Klmcargo2 --groups
> ```
> 
> ```bash
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  [*] Windows 10.0 Build 17763 x64 (name:ACADEMY-EA-DC01) (domain:INLANEFREIGHT.LOCAL) (signing:True) (SMBv1:False)
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  [+] INLANEFREIGHT.LOCAL\forend:Klmcargo2 
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  [+] Enumerated domain group(s)
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  Administrators                           membercount: 3
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  Users                                    membercount: 4
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  Guests                                   membercount: 2
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  Print Operators                          membercount: 0
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  Backup Operators                         membercount: 1
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  Replicator                               membercount: 0
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  Remote Desktop Users                     membercount: 0
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  Network Configuration Operators          membercount: 0
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  Performance Monitor Users                membercount: 0
> ```

- Enumerate currently logged-in users:

```bash
nxc smb 10.10.11.5 -u 'jdoe' -p 'passwd123' --loggedon-users
```

- `nxc smb`/`cme smb` options:

| Option                 | Description                                                                                    |
| ---------------------- | ---------------------------------------------------------------------------------------------- |
| `-d`, `--domain`       | Domain to authenticate to.                                                                     |
| `--local-auth`         | Authenticate locally to each target.                                                           |
| `--port`               | SMB port (default: `445`).                                                                     |
| `-u`, `--username`     | Username for authentication.                                                                   |
| `-p`, `--password`     | Password for authentication.                                                                   |
| `-M`, `--module`       | Module to use.                                                                                 |
| `-L`, `--list-modules` | List available modules.                                                                        |
| `--shares`             | Enumerate accessible shares.                                                                   |
| `--users`              | Enumerate domain users (if a user is specified, information only for that user is queried).    |
| `--groups`             | Enumerate domain groups (if a group is specified, information only for that group is queried). |
| `--computers`          | Enumerate domain computer accounts.                                                            |
| `--local-groups`       | Enumerate local groups (if a group is specified, information only for that group is queried).  |
| `--pass-pol`           | Retrieve password policy.                                                                      |
| `--loggedon-users`     | Enumerate logged on users (if a user is specified, information only for that user is queried). |
| `--smb-sessions`       | Enumerate active SMB sessions.                                                                 |
| `--tasklist`           | Enumerate processes running on the target system (if a process is specified, filter for it).   |
### Automated enumeration with `enum4linux-ng`

- Perform standard authenticated enumeration:

```bash
enum4linux-ng 10.10.11.5 -A -u jdoe -p passwd123 -w example.com
```

- Shorter set without NetBIOS-name lookup:

```bash
enum4linux-ng 10.10.11.5 -As -u jdoe -p passwd123 -w example.com
```

## MSRPC / SAMR / LSARPC

- [ ] Enumerate domain information.
- [ ] Enumerate domain users where permitted.
- [ ] Enumerate domain groups.
- [ ] Enumerate group membership.
- [ ] Enumerate domain password policy.
- [ ] Resolve RIDs/SIDs to usernames and groups.
- [ ] Enumerate trusted domains where exposed.
- [ ] Enumerate logged-on users/session information where authorized and available.
- [ ] Compare RPC results with LDAP results; differences can expose filtering or permissions issues.


- MSRPC transports:

| Protocol sequence   | Transport                | Typical endpoint                            |
| ------------------- | ------------------------ | ------------------------------------------- |
| `ncacn_ip_tcp`      | RPC directly over TCP    | TCP `135` followed by a dynamic TCP port    |
| `ncacn_np`          | RPC over SMB named pipes | TCP `445` or legacy TCP `139`               |
| `ncacn_http`        | RPC over HTTP            | TCP `593`                                   |
| RPC over HTTP proxy | Encapsulated/proxied RPC | Usually HTTPS TCP `443`                     |
| `ncalrpc`           | Local RPC                | Local-only endpoint; not remotely reachable |

- Important ports:

| Port                | Purpose                                               |
| :------------------ | :---------------------------------------------------- |
| TCP `135`           | RPC Endpoint Mapper.                                  |
| TCP `445`           | SMB transport for named-pipe RPC.                     |
| TCP `139`           | Legacy SMB/NetBIOS transport.                         |
| TCP `593`           | RPC over HTTP.                                        |
| TCP `443`           | RPC over HTTP proxy in some Exchange/RDS deployments. |
| TCP `49152`-`65535` | Default dynamic RPC range on modern Windows.          |
| TCP `1025`-`5000`   | Common legacy dynamic range.                          |

### Checking well-known RPC ports

- Check the Endpoint Mapper and common RPC transports:

```bash
nmap -Pn -sT -p 135,139,445,593 10.10.11.5
```

- Perform service detection:

```
nmap -Pn -sV -p 135,139,445,593 10.10.11.5
```

### Enumerating RPC Endpoint Mapper

- The Endpoint Mapper records which RPC interfaces are registered and how clients can reach them.

- Query the MSRPC Endpoint Mapper using Nmap's [`msrpc-enum`](https://nmap.org/nsedoc/scripts/msrpc-enum.html):

```bash
nmap -Pn -p 135 --script msrpc-enum 10.10.11.5
```

>[!note] The [`msrpc-enum`](https://nmap.org/nsedoc/scripts/msrpc-enum.html) NSE script queries the Endpoint Mapper for mapped services. 

- Query the Endpoint Mapper directly over TCP `135` using Impacket's [`rpcdump.py`](https://github.com/fortra/impacket/blob/master/examples/rpcdump.py):

```bash
rpcdump.py 10.10.11.5 -port 135
```

>[!note] RPC Endpoint Mapper enumeration on TCP port `135` often does not require authentication.

- Query the Endpoint Mapper through SMB on TCP `445` (authenticated):

```bash
rpcdump.py example.com/jdoe:passwd123@10.10.11.5 -port 445
```

- Query through legacy SMB on TCP port `139`:

```bash
rpcdump.py example.com/jdoe:passwd123@10.10.11.5 -port 139
```

- Query RPC over HTTP on TCP port `593`:

```bash
rpcdump.py 10.10.11.5 -port 593
```

>[!note] [`rpcdump.py`](https://github.com/fortra/impacket/blob/master/examples/rpcdump.py) reports interface UUIDs, versions, annotations, provider information, and bindings. 


- Query endpoint bindings using a direct TCP binding:

```bash
rpcclient 'ncacn_ip_tcp:10.10.11.5[135]' -c 'epmlookup'
```

- Query with authentication if the environment requires it:

```bash
rpcclient -U 'example.com/jdoe%passwd123' 'ncacn_ip_tcp:10.10.11.5[135]' -c 'epmlookup'
```
### `rpcclient`

- Establish an RPC connection:

```bash
rpcclient -U "jdoe" --password='passwd123' 10.10.11.5
```

- Establish an RPC connection and run commands:

```bash
rpcclient -U "jdoe" --password='passwd123' 10.10.11.5 -c "getdompwinfo; querydominfo"
```

- Kerberos authentication (using a `.ccache` file):

```bash
rpcclient --use-krb5-ccache=FILE:/tmp/jdoe.ccache 'ncacn_np:DC01.example.com[lsarpc,sign,seal,krb5]' -c 'lsaquery'
```

- Useful `rpcclient` commands for AD enumeration:

| Command                  | Description                                                      |
| ------------------------ | ---------------------------------------------------------------- |
| `srvinfo`                | Retrieve target OS version, domain name, hostname, etc.          |
| `querydominfo`           | Retrieve domain, server, users on the system, etc.               |
| `enumdomusers`           | Enumerate domain users.                                          |
| `enumdomgroups`          | Enumerate domain groups.                                         |
| `querygroup <rid>`       | Query information about a specific group.                        |
| `queryuser <username>`   | Query information about a specific user.                         |
| `enumprivs`              | Enumerate privileges and rights assignments of the current user. |
| `getdompwinfo`           | Retrieve domain password policies.                               |
| `getusrdompwinfo <rid>`  | Retrieve password policies for a specific user.                  |
| `lsaenumsid`             | Enumerate LSA SIDs.                                              |
| `lookupnames <username>` | Map usernames to SIDs.                                           |
| `lookupsids <sid>`       | Map SIDs to usernames.                                           |

> [!tip]+ Relative ID (RID) reference
> - `500`: Built-in Administrator account (`0x1f4`).
> - `501`: Guest account (`0x1f5`).
> - `502`: `krbtgt` account (`0x1f6`).
> - `512`: Domain Admins group (`0x200`).
> - `513`: Domain Users group (`0x201`).
> - `515`: Domain Computers group (`0x203`).
> - `516`: Domain Controllers group (`0x204`).

>[!note] `rpcclient` accepts either a hostname or a DCE/RPC binding string.
>- Binding syntax:
>```bash
>transport:host[endpoint,options]
>```
>- Examples:
>```bash
>ncacn_np:10.10.11.5[samr]
> ncacn_np:10.10.11.5[lsarpc,sign,seal]
> ncacn_ip_tcp:10.10.11.5[49664]
> ncacn_ip_tcp:DC01.example.com[sign,seal,krb5]
>```
> 
> | Option    | Meaning                           |
> | --------- | --------------------------------- |
> | `sign`    | RPC packet integrity.             |
> | `seal`    | RPC packet privacy/encryption.    |
> | `connect` | RPC connect-level authentication. |
> | `packet`  | RPC packet-level authentication.  |
> | `spnego`  | SPNEGO negotiation.               |
> | `ntlm`    | NTLM authentication.              |
> | `krb5`    | Kerberos authentication.          |
> | `smb2`    | Use SMBv2/SMBv3 for named pipes.  |
> | `ndr64`   | Request NDR64 transfer syntax.    |

### Host and domain enumeration

- Retrieve effective username, server information, domain role, join information, time, domain SID, and other domain information:

```bash
rpcclient -p 445 -U 'example.com/jdoe%passwd123' 10.10.11.5 -c 'getusername;srvinfo;dsroledominfo;wkssvc_wkstagetinfo;wkssvc_getjoininformation;netremotetod;lsaquery;querydominfo'
```

| Command                     | Description                                       |
| --------------------------- | ------------------------------------------------- |
| `getusername`               | Show authenticated username/domain.               |
| `srvinfo`                   | Server OS, platform, and server-type information. |
| `dsroledominfo`             | Domain role / Active Directory role information.  |
| `wkssvc_wkstagetinfo`       | Workstation/server information through WKSSVC.    |
| `wkssvc_getjoininformation` | Check domain/workgroup membership.                |
| `netremotetod`              | Retrieve remote system time.                      |
| `lsaquery`                  | Query LSA policy/domain information.              |
| `querydominfo`              | Query SAM domain information.                     |

- `rpcclient` command cheat sheet:
### RID cycling attack via `rpcclient` or `NetExec`

- If `enumdomusers` is restricted, you can brute-force domain accounts by cycling RIDs through LSA lookup functions:

- Execute RID cycling using `NetExec`:

```bash
netexec smb 10.10.11.5 -u '' -p '' --rid-brute 10000
```

- Execute RID cycling using `ridenumerate` / `impacket-lookupsid`:

```bash
impacket-lookupsid anonymous@10.10.11.5 -no-pass
```

> [!note] [`rpcclient`](https://www.samba.org/samba/docs/current/man-html/rpcclient.1.html) · [`Impacket`](https://github.com/fortra/impacket)

### `rpcdump`

- Enumerate exposed RPC endpoints using [`impacket-rpcdump`](https://github.com/fortra/impacket/blob/master/examples/rpcdump.py):

```bash
impacket-rpcdump 10.10.11.5
```

> [!note] [`rpcdump`](https://github.com/fortra/impacket/blob/master/examples/rpcdump.py)

## `5985`/`5986` — WinRM

>[!abstract] **Objective**: identify exposed WinRM/WS-Management listeners, supported transports and authentication mechanisms, information disclosure, credential validity, PowerShell-remoting authorization, endpoint permissions, security controls, and monitoring coverage without changing the target configuration.

>[!note] `netexec winrm`, `evil-winrm`

- [ ] Determine which hosts expose WinRM.
- [ ] Test authenticated access.
- [ ] Determine whether the supplied account obtains a shell.
- [ ] Identify systems where the account is in:
    - [ ] local Administrators
    - [ ] Remote Management Users
- [ ] Prioritize administrative servers, management hosts, jump boxes, and application servers.

|Port|Transport|Notes|
|--:|---|---|
|TCP `5985`|WinRM over HTTP|Modern default HTTP listener|
|TCP `5986`|WinRM over HTTPS|Modern default HTTPS listener|
|TCP `80`|Compatibility/custom HTTP|Legacy WinRM or application-specific endpoint|
|TCP `443`|Compatibility/custom HTTPS|Legacy WinRM, Exchange remote PowerShell, proxy, or another HTTPS service|
|TCP `47001`|Local WinRM service endpoint|Normally intended for local requests; do not assume remote exposure is expected|
|Custom|HTTP or HTTPS|WinRM listeners can use arbitrary ports|

>[!note] Modern default listener ports are `5985` and `5986`; arbitrary ports and migrated legacy listeners are possible. See [Microsoft WinRM configuration documentation](https://learn.microsoft.com/en-us/windows/win32/winrm/installation-and-configuration-for-windows-remote-management).

>[!note] WinRM over TCP `5985` does not automatically mean that PowerShell commands and output travel unprotected:
> 
> - Kerberos and NTLM can provide WS-Man message-level encryption.
> - HTTPS provides transport-level TLS protection.
> - Basic authentication provides no authentication-layer encryption and is unsafe without TLS.
> - `AllowUnencrypted=false` prevents unencrypted WS-Man messages.
> - CredSSP uses TLS and delegates explicit credentials to the remote system.

### Checking WinRM ports

- Check the normal WinRM ports and perform service detection:

```bash
nmap -Pn -sT -p 5985,5986 10.10.11.5
```

- Include legacy and occasionally observed endpoints:

```bash
nmap -Pn -sV -p 80,443,5985,5986,47001 10.10.11.5
```

- Identify the WS-Management endpoint:

```bash
curl -i --max-time 10 http://10.10.11.5:5985/wsman
```

```bash
curl -ik --max-time 10 https://10.10.11.5:5986/wsman
```

>[!tip]+
>Responses such as `401`, `404`, `405`, or a SOAP/WS-Man fault can still confirm that an HTTP service exists. Review:
> - `Server` headers such as `Microsoft-HTTPAPI/2.0`.
> - `WWW-Authenticate` mechanisms.
> - Redirections.
> - TLS certificate errors.
> - Unexpected proxies or web servers.
> - Whether `/wsman` differs from `/`.
> - Whether a custom URL prefix appears to be in use.

### Inspecting certificates

- Inspect HTTPS certificate:

```bash
nmap -Pn -sV -p 5986 --script ssl-cert 10.10.11.5
```

- Enumerate TLS protocol and ciphers:

```bash
nmap -Pn -p 5986 --script ssl-enum-ciphers 10.10.11.5
```

>[!note] `ssl-enum-ciphers` performs multiple TLS handshakes, so use it deliberately against large ranges.

### Connecting to WinRM

- Authenticate via NTLM:

```bash
nxc winrm 10.10.11.5 -u jdoe -p passwd123 -d example.com
```

```bash
evil-winrm -i 10.10.11.5 -u jdoe -p passwd123
```

- Over HTTPS:

```bash
evil-winrm -i SRV01.example.com -u jdoe -p passwd123 -S -P 5986
```

- Local authentication:

```bash
nxc winrm 10.10.11.5 -u Administrator -p passwd123 --local-auth
```

- Authenticate using an NT hash ([[Pass-the-Hash]]):

```bash
nxc winrm 10.10.11.5 -u jdoe -H 0123456789abcdef0123456789abcdef -d example.com
```

```bash
evil-winrm -i 10.10.11.5 -u jdoe -H 0123456789abcdef0123456789abcdef
```

- Kerberos cache:

```bash
evil-winrm -i SRV01.example.com -r EXAMPLE.COM -K /tmp/jdoe.ccache
```

>[!note] See [[Privileged remote access]].

## `3389` — RDP

>[!note] `nmap`, `netexec`, `xfreerdp`

- [ ] Identify systems exposing RDP.
- [ ] Determine whether Network Level Authentication is required.
- [ ] Test whether supplied credentials are authorized for RDP.
- [ ] Identify hosts where non-administrative domain groups have interactive logon rights.
- [ ] Correlate RDP access with privileged users and administrative hosts.

|       Port | Protocol       | Purpose                                              |
| ---------: | -------------- | ---------------------------------------------------- |
| TCP `3389` | RDP            | Initial connection, authentication, graphics/control |
| UDP `3389` | RDP-UDP        | Performance transport used alongside TCP             |
|  TCP `443` | HTTPS          | RD Gateway and RD Web Access                         |
| UDP `3391` | RD Gateway UDP | Optional gateway UDP transport                       |
|     Custom | TCP/UDP        | RDP listener can be moved from `3389`                |

### Checking RDP ports

Add descriptions


```bash
nmap -Pn -sT -sV -p 3389 10.10.11.5
```

```bash
nmap -Pn -sT -sU -sV -p T:3389,U:3389 10.10.11.5
```

```bash
nmap -Pn -sV -p 443 10.10.11.5
```

```bash
nmap -Pn -sU -p 3391 10.10.11.5
```

```bash
map -Pn -p 3389 --script rdp-enum-encryption 10.10.11.5
```

### RDP certificate checks

```bash
nmap -Pn -p 3389 --script ssl-cert 10.10.11.5
```

```bash
nmap -Pn -p 3389 --script ssl-enum-ciphers 10.10.11.5
```
## `1433` — MSSQL

**Tools:** `netexec mssql`, `mssqlclient.py`, `nmap`

- [ ] Identify SQL Server instances.
- [ ] Test Windows-integrated authentication.
- [ ] Determine current SQL privileges.
- [ ] Enumerate databases.
- [ ] Enumerate SQL logins and mapped domain principals where allowed.
- [ ] Identify SQL Server service account.
- [ ] Identify linked SQL servers.
- [ ] Review whether SQL service accounts are privileged in AD.
- [ ] Identify instances where the current domain account maps to elevated SQL privileges.

## BloodHound

>[!Note] See [[🛠️ BloodHound]]

## References and further reading