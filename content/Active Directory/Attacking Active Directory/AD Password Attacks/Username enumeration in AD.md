---
created: 2026-10-08
updated: 2026-10-11
tags:
  - AD_attacks
  - AD
---
## Username enumeration

- A comprehensive list of valid usernames makes [[Password spraying in AD|password spraying]] far more efficient.
- Common ways to enumerate users in Active Directory:
	- SMB `null` sessions (querying SAMR RPC interface without credentials).
	- Anonymous LDAP binds (querying LDAP directory without credentials).
	- Kerberos pre-authentication username enumeration using `Kerbrute`.
	- Passive traffic analysis with `Responder -A`, `tcpdump`, or Wireshark — only when you're on the internal network (see [[🛠️ AD enumeration]]).
	- LLMNR & NBT-NS poisoning (see [[LLMNR & NBT-NS poisoning]]).

### Username enumeration via SMB `null` sessions

- If SMB `null` sessions are enabled on the Domain Controller, you can query the SAMR RPC interface to retrieve a complete list of domain users.
- NetExec `--users`:

```bash
netexec smb 10.10.11.5 --users
```

>[!note] NetExec `--users` enumerates domain accounts via SAMR/RPC.

- CrackMapExec (legacy):

```bash
crackmapexec smb 10.10.11.5 --users
```

>[!example]-
> ```bash
> crackmapexec smb 172.16.5.5 --users
> ```
> 
> ```bash
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  [*] Windows 10.0 Build 17763 x64 (name:ACADEMY-EA-DC01) (domain:INLANEFREIGHT.LOCAL) (signing:True) (SMBv1:False)
> 
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  [+] Enumerated domain user(s)
> 
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  INLANEFREIGHT.LOCAL\administrator                 badpwdcount: 1 baddpwdtime: 2026-07-22 05:01:40.034946
> 
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  INLANEFREIGHT.LOCAL\guest                         badpwdcount: 0 baddpwdtime: 1600-12-31 19:03:58
> 
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  INLANEFREIGHT.LOCAL\lab_adm                       badpwdcount: 0 baddpwdtime: 2026-07-22 05:01:06.175589
> 
> SMB         172.16.5.5      445    ACADEMY-EA-DC01  INLANEFREIGHT.LOCAL\krbtgt                        badpwdcount: 0 baddpwdtime: 1600-12-31 19:03:58
> # ...
> ```

- `rpcclient`:

```bash
rpcclient -U "" -N 10.10.11.5
```

```bash
rpcclient $> enumdomusers
```

- `enumdomusers` issues `SamrEnumDomainUsers` to enumerate all domain account names and RIDs.

>[!example]-
> 
> ```bash
> rpcclient -U "" -N 172.16.5.5 
> ```
> 
> ```bash
> rpcclient $> enumdomusers
> 
> user:[administrator] rid:[0x1f4]
> user:[guest] rid:[0x1f5]
> user:[krbtgt] rid:[0x1f6]
> user:[lab_adm] rid:[0x3e9]
> user:[htb-student] rid:[0x457]
> user:[avazquez] rid:[0x458]
> user:[pfalcon] rid:[0x459]
> user:[fanthony] rid:[0x45a]
> user:[wdillard] rid:[0x45b]
> user:[lbradford] rid:[0x45c]
> user:[sgage] rid:[0x45d]
> user:[asanchez] rid:[0x45e]
> user:[dbranch] rid:[0x45f]
> user:[ccruz] rid:[0x460]
> user:[njohnson] rid:[0x461]
> user:[mholliday] rid:[0x462]
> ```

- `enum4linux-ng`:

```bash
enum4linux-ng -U 10.10.11.5
```

>[!note] `-U` enumerates domain users via SAMR (`querydispinfo` and `enumdomusers`).

- `enum4linux` (legacy):

```bash
enum4linux -U 10.10.11.5
```

>[!example]-
> ```bash
> enum4linux-ng -U 172.16.5.5 
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
> [*] Random Username .. 'ewrtzeru'
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
>  ===================================
> |    Users via RPC on 172.16.5.5    |
>  ===================================
> [*] Enumerating users via 'querydispinfo'
> [+] Found 100 users via 'querydispinfo'
> [*] Enumerating users via 'enumdomusers'
> [+] Found 513 users via 'enumdomusers'
> [+] After merging user results we have 589 users total:
> '1001':
>   username: lab_adm
> '1111':
>   username: htb-student
> '1112':
>   username: avazquez
> '1113':
>   username: pfalcon
> '1114':
>   username: fanthony
> '1115':
>   username: wdillard
> # ...
> '500':
>   username: administrator
>   name: Administrator
>   acb: '0x00000210'
>   description: Built-in account for administering the computer/domain
> '501':
>   username: guest
> '502':
>   username: krbtgt
> '5191':
>   username: $725000-9jb50uejje9f
>   name: Jessica Ramsey
>   acb: '0x00020015'
>   description: (null)
> '5244':
>   username: adfs
>   name: Sharepoint Admin
>   acb: '0x00000010'
>   description: (null)
> 
> Completed after 5.48 seconds
> ```

### Username enumeration via LDAP anonymous bind

- When anonymous LDAP bind is enabled, you can use `ldapsearch` to query the `sAMAccountName` attribute and dump all domain users:

```bash
ldapsearch -x -H ldap://10.10.11.5 -b "DC=EXAMPLE,DC=COM" -s sub "(&(objectclass=user))" | grep sAMAccountName: | cut -f2 -d" "
```

- `grep sAMAccountName: | cut -f2 -d" "` extracts raw user account names.

>[!note]+ Option breakdown
> - `-x`: unauthenticated simple bind.
> - `-s sub`: subtree search scope.
> - `"(&(objectclass=user))"`: LDAP filter; selects user objects.

>[!example]-
> ```bash
> ldapsearch -h 172.16.5.5 -x -b "DC=INLANEFREIGHT,DC=LOCAL" -s sub "(&(objectclass=user))"
> ```
> 
> ```bash
> # extended LDIF
> #
> # LDAPv3
> # base <DC=INLANEFREIGHT,DC=LOCAL> with scope subtree
> # filter: (&(objectclass=user))
> # requesting: ALL
> #
> 
> # Guest, Users, INLANEFREIGHT.LOCAL
> dn: CN=Guest,CN=Users,DC=INLANEFREIGHT,DC=LOCAL
> objectClass: top
> objectClass: person
> objectClass: organizationalPerson
> objectClass: user
> cn: Guest
> sn: Manley
> # ...
> ```
> 
> ```bash
> ldapsearch -h 172.16.5.5 -x -b "DC=INLANEFREIGHT,DC=LOCAL" -s sub "(&(objectclass=user))"  | grep sAMAccountName: | cut -f2 -d" "
> ```
> 
> ```bash
> guest
> ACADEMY-EA-DC01$
> ACADEMY-EA-MS01$
> htb-student
> avazquez
> pfalcon
> fanthony
> wdillard
> lbradford
> sgage
> asanchez
> dbranch
> ccruz
> njohnson
> mholliday
> mshoemaker
> aslater
> kprentiss
> gdavis
> jmcdaniel
> jjones
> tgarcia
> mharrison
> nhight
> wbaird
> mochoa
> jhopkins
> hblea
> cpennington
> dglen
> khartsfield
> rramirez
> ohafner
> lmatthews
> # ...
> ```

### Username enumeration with `Kerbrute`

- You can enumerate valid domain usernames using **Kerberos pre-authentication requests**; `Kerbrute` automates this process:

```bash
kerbrute userenum -d example.com --dc 10.10.11.5 /usr/share/wordlists/statistically-likely-usernames/jsmith.txt
```

>[!note]+ Option breakdown
> - `userenum`: selects Kerberos username enumeration mode.
> - `-d`: specifies the target domain realm (FQDN).
> - `--dc`: specifies target Domain Controller IP address.
> - `jsmith.txt`: path to a list of candidate usernames.

>[!note] See [[Kerberos#Kerberos operation]].

>[!example]-
> ```bash
> kerbrute userenum -d inlanefreight.local --dc 172.16.5.5 /opt/jsmith.txt 
> ```
> 
> ```bash
>     __             __               __     
>    / /_____  _____/ /_  _______  __/ /____ 
>   / //_/ _ \/ ___/ __ \/ ___/ / / / __/ _ \
>  / ,< /  __/ /  / /_/ / /  / /_/ / /_/  __/
> /_/|_|\___/_/   \__,_/\__/\___/                                        
> 
> Version: dev (9cfb81e) - 08/01/26 - Ronnie Flathers @ropnop
> 
> 2026/08/01 09:43:11 >  Using KDC(s):
> 2026/08/01 09:43:11 >  	172.16.5.5:88
> 
> 2026/08/01 09:43:11 >  [+] VALID USERNAME:	 jjones@inlanefreight.local
> 2026/08/01 09:43:11 >  [+] VALID USERNAME:	 tjohnson@inlanefreight.local
> 2026/08/01 09:43:11 >  [+] VALID USERNAME:	 sbrown@inlanefreight.local
> 2026/08/01 09:43:11 >  [+] VALID USERNAME:	 jwilson@inlanefreight.local
> 2026/08/01 09:43:11 >  [+] VALID USERNAME:	 bdavis@inlanefreight.local
> 2026/08/01 09:43:11 >  [+] VALID USERNAME:	 asanchez@inlanefreight.local
> 2026/08/01 09:43:11 >  [+] VALID USERNAME:	 njohnson@inlanefreight.local
> 2026/08/01 09:43:11 >  [+] VALID USERNAME:	 dlewis@inlanefreight.local
> 2026/08/01 09:43:11 >  [+] VALID USERNAME:	 ccruz@inlanefreight.local
> 2026/08/01 09:43:11 >  [+] mmorgan has no pre auth required. Dumping hash to crack offline:
> $krb5asrep$23$mmorgan@INLANEFREIGHT.LOCAL:accc0288f8978a82b4b82afd606f4a7f$1c262bfb7a7dcfdc2397b7dd1660a4f0f0fbc445875d359a57847a36d05f7801e4bee861f23088c3fd1abf3c5fd1977b8d1f50a740135cd249e1f2e70796559266641b26d5c6191d7f6a576dea45a5af8e1ee259baa772b82278a6424f2a4f7d54f1abb6fef1a473af57fff0707f28b99bd9f2ac77ab070cbbc27861b6031c9b67cbb24297a39e3fd09a00841a11245cb207748f3603546f2461e3e9f43b2f67bc8e0aaa10f5ab826a9c424fb59d8dc72553b2617712f5b2d2190dbc6ecae077328f7af8f16aa4f20fb98ae5ed9525d42eb4ba140e9d8fcba5098354f7f2bffb79b7666bb11988c750a0932532f59e1b0625eba4594fbcd89aa5d486e444dc26a708a045966d174bf8ea
> 2026/08/01 09:43:11 >  [+] VALID USERNAME:	 mmorgan@inlanefreight.local
> 2026/08/01 09:43:11 >  [+] VALID USERNAME:	 rramirez@inlanefreight.local
> # ...
> ```

>[!note] `Kerbrute` ships as a static Go binary, so it runs on Windows the same way.

#### Where to get username wordlists

- For username wordlists, use [`statistically-likely-usernames`](https://github.com/insidetrust/statistically-likely-usernames). It includes wordlists in several widely-used naming conventions (`jdoe`, `jane.doe`, `j.doe`, etc.) derived from statistically common names. `jsmith.txt` alone contains 48,705 candidate usernames in `jdoe` format.
- To enrich your lists, do some OSINT:
	- Scrape usernames from LinkedIn using [`linkedin2username`](https://github.com/initstring/linkedin2username).
	- Crawl target's website and gather publicly exposed employees' names.
	- Email harvesting — use `theHarvester`, search engines, leaked databases.
	- Extract metadata of published documents (e.g., PDF/DOCX `Author` fields may reveal internal username scheme).
	- Bounced emails — external SMTP servers sometimes echo the mailbox name in the NDR (returned message).
	- Default service accounts — `admin`, `administrator`, `backup`, `svc_backup`, `sqlservice`, etc.

#### How and why `Kerbrute` works

- The part of the Kerberos authentication process relevant to user enumeration is the **AS (Authentication Server) exchange**, also called **pre-authentication**.
- The client sends an `AS-REQ` to the KDC's AS, proving its identity; on success, the AS returns a TGT (Ticket-Granting Ticket) in the `AS-REP`.

>[!note] See [[Kerberos#1. AS exchange (KRB_AS_REQ / KRB_AS_REP)]].

- Importantly, when authentication fails the **AS returns verbose `KRB-ERROR` messages that reveal whether the account exists**.

| KDC response code | Constant name                     | Meaning                                                                |
| ----------------- | --------------------------------- | ---------------------------------------------------------------------- |
| `0x6`             | `KRB5KDC_ERR_C_PRINCIPAL_UNKNOWN` | Account **does not exist** in the realm.                               |
| `0x19`            | `KRB5KDC_ERR_PREAUTH_REQUIRED`    | Account **exists** (KDC requests pre-authentication proof).            |
| `0x18`            | `KRB5KDC_ERR_PREAUTH_FAILED`      | Account exists, but pre-auth proof was invalid (used during spraying). |
| `0x1C`            | `KRB5KDC_ERR_CLIENT_REVOKED`      | Account exists, but is **disabled, locked out, or revoked**.           |

- Better still, since the AS doesn't verify the user's password (the client is verified via encrypted timestamps, so no credentials are sent), failed attempts **don't generate event ID `4625` (`An account failed to log on`)**, **don't increment `badPwdCount`**, and **don't trigger lockouts**.

- `Kerbrute`'s `userenum` module exploits exactly this; as a bonus, the enumeration is extremely fast.

>[!note] Each `AS-REQ` does generate event ID `4768` (`A Kerberos authentication ticket (TGT) was requested`) — but only when [Kerberos event logging](https://docs.microsoft.com/en-us/troubleshoot/windows-server/identity/enable-kerberos-event-logging) is enabled via GPO. So, enumeration *can* be detected in the SIEM by a burst of `4768` events, but it's far less conspicuous than a burst of failed logons (event ID `4625`).

>[!warning] This stealth advantage only applies to **username enumeration (`userenum`)**. Once you switch to Kerberos password spraying (`passwordspray`), failed pre-authentication attempts return `KRB5KDC_ERR_PREAUTH_FAILED` (Event ID **`4771`**, `Kerberos pre-authentication failed`), **do** increment `badPwdCount`, and **do** trigger account lockouts. See [[Password spraying in AD]].

## References and further reading

- [`statistically-likely-usernames Repository — GitHub`](https://github.com/insidetrust/statistically-likely-usernames)
- [`Kerbrute — Active Directory Username Enumeration & Spraying — GitHub`](https://github.com/ropnop/kerbrute)
- [`linkedin2username — OSINT Username Generator — GitHub`](https://github.com/initstring/linkedin2username)
