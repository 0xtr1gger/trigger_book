---
created: 2026-08-12
updated: 2026-08-16
tags:
  - walkthrough
---
## External enumeration

```bash
sudo nmap -sC -sV 10.129.95.210 -oA nmap/common_tcp_ports
```

```bash
Starting Nmap 7.95 ( https://nmap.org ) at 2026-08-12 10:57 EDT
Nmap scan report for 10.129.95.210
Host is up (0.011s latency).
Not shown: 988 closed tcp ports (reset)
PORT     STATE SERVICE      VERSION
53/tcp   open  domain       Simple DNS Plus
88/tcp   open  kerberos-sec Microsoft Windows Kerberos (server time: 2026-08-12 15:04:40Z)
135/tcp  open  msrpc        Microsoft Windows RPC
139/tcp  open  netbios-ssn  Microsoft Windows netbios-ssn
389/tcp  open  ldap         Microsoft Windows Active Directory LDAP (Domain: htb.local, Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds Windows Server 2016 Standard 14393 microsoft-ds (workgroup: HTB)
464/tcp  open  kpasswd5?
593/tcp  open  ncacn_http   Microsoft Windows RPC over HTTP 1.0
636/tcp  open  tcpwrapped
3268/tcp open  ldap         Microsoft Windows Active Directory LDAP (Domain: htb.local, Site: Default-First-Site-Name)
3269/tcp open  tcpwrapped
5985/tcp open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
Service Info: Host: FOREST; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb-os-discovery: 
|   OS: Windows Server 2016 Standard 14393 (Windows Server 2016 Standard 6.3)
|   Computer name: FOREST
|   NetBIOS computer name: FOREST\x00
|   Domain name: htb.local
|   Forest name: htb.local
|   FQDN: FOREST.htb.local
|_  System time: 2026-08-12T08:04:45-07:00
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: required
| smb2-time: 
|   date: 2026-08-12T15:04:42
|_  start_date: 2026-08-12T14:36:01
| smb2-security-mode: 
|   3:1:1: 
|_    Message signing enabled and required
|_clock-skew: mean: 2h26m50s, deviation: 4h02m32s, median: 6m48s

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 17.14 seconds
```

- Scan all TCP ports:

```bash
sudo nmap -sC -sV 10.129.95.210 -p- -oA nmap/all_tcp_ports
```

```bash
Starting Nmap 7.95 ( https://nmap.org ) at 2026-08-12 10:58 EDT
Nmap scan report for 10.129.95.210
Host is up (0.0089s latency).
Not shown: 65511 closed tcp ports (reset)
PORT      STATE SERVICE      VERSION
53/tcp    open  domain       Simple DNS Plus
88/tcp    open  kerberos-sec Microsoft Windows Kerberos (server time: 2026-08-12 15:05:57Z)
135/tcp   open  msrpc        Microsoft Windows RPC
139/tcp   open  netbios-ssn  Microsoft Windows netbios-ssn
389/tcp   open  ldap         Microsoft Windows Active Directory LDAP (Domain: htb.local, Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds Windows Server 2016 Standard 14393 microsoft-ds (workgroup: HTB)
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http   Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap         Microsoft Windows Active Directory LDAP (Domain: htb.local, Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
5985/tcp  open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp  open  mc-nmf       .NET Message Framing
47001/tcp open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
49664/tcp open  msrpc        Microsoft Windows RPC
49665/tcp open  msrpc        Microsoft Windows RPC
49666/tcp open  msrpc        Microsoft Windows RPC
49668/tcp open  msrpc        Microsoft Windows RPC
49671/tcp open  msrpc        Microsoft Windows RPC
49680/tcp open  ncacn_http   Microsoft Windows RPC over HTTP 1.0
49681/tcp open  msrpc        Microsoft Windows RPC
49685/tcp open  msrpc        Microsoft Windows RPC
49700/tcp open  msrpc        Microsoft Windows RPC
49864/tcp open  msrpc        Microsoft Windows RPC
Service Info: Host: FOREST; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb-os-discovery: 
|   OS: Windows Server 2016 Standard 14393 (Windows Server 2016 Standard 6.3)
|   Computer name: FOREST
|   NetBIOS computer name: FOREST\x00
|   Domain name: htb.local
|   Forest name: htb.local
|   FQDN: FOREST.htb.local
|_  System time: 2026-08-12T08:06:50-07:00
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: required
| smb2-security-mode: 
|   3:1:1: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2026-08-12T15:06:46
|_  start_date: 2026-08-12T14:36:01
|_clock-skew: mean: 2h26m50s, deviation: 4h02m32s, median: 6m48s

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 78.69 seconds
```

- SMB information: 

```bash
netexec smb 10.129.95.210 
```

```bash
SMB         10.129.95.210   445    FOREST           [*] Windows Server 2016 Standard 14393 x64 (name:FOREST) (domain:htb.local) (signing:True) (SMBv1:True) (Null Auth:True)
```

- WinRM:

```bash
netexec winrm 10.129.95.210 
WINRM       10.129.95.210   5985   FOREST           [*] Windows 10 / Server 2016 Build 14393 (name:FOREST) (domain:htb.local) 
```

- SMB discovery:

```bash
nmap -Pn -p 445 --script smb-os-discovery,smb2-security-mode 10.129.95.210
```

```bash
Starting Nmap 7.95 ( https://nmap.org ) at 2026-08-12 11:35 EDT
Nmap scan report for 10.129.95.210
Host is up (0.0083s latency).

PORT    STATE SERVICE
445/tcp open  microsoft-ds

Host script results:
| smb-os-discovery: 
|   OS: Windows Server 2016 Standard 14393 (Windows Server 2016 Standard 6.3)
|   Computer name: FOREST
|   NetBIOS computer name: FOREST\x00
|   Domain name: htb.local
|   Forest name: htb.local
|   FQDN: FOREST.htb.local
|_  System time: 2026-08-12T08:41:56-07:00
| smb2-security-mode: 
|   3:1:1: 
|_    Message signing enabled and required

Nmap done: 1 IP address (1 host up) scanned in 3.16 seconds
```

- LDAP scan:

```bash
nmap -Pn -p 389 --script ldap-rootdse 10.129.95.210
```

```bash
Starting Nmap 7.95 ( https://nmap.org ) at 2026-08-12 11:36 EDT
Nmap scan report for 10.129.95.210
Host is up (0.0083s latency).

PORT    STATE SERVICE
389/tcp open  ldap
| ldap-rootdse: 
| LDAP Results
|   <ROOT>
|       currentTime: 20260812154334.0Z
|       subschemaSubentry: CN=Aggregate,CN=Schema,CN=Configuration,DC=htb,DC=local
|       dsServiceName: CN=NTDS Settings,CN=FOREST,CN=Servers,CN=Default-First-Site-Name,CN=Sites,CN=Configuration,DC=htb,DC=local
|       namingContexts: DC=htb,DC=local
|       namingContexts: CN=Configuration,DC=htb,DC=local
|       namingContexts: CN=Schema,CN=Configuration,DC=htb,DC=local
|       namingContexts: DC=DomainDnsZones,DC=htb,DC=local
|       namingContexts: DC=ForestDnsZones,DC=htb,DC=local
|       defaultNamingContext: DC=htb,DC=local
|       schemaNamingContext: CN=Schema,CN=Configuration,DC=htb,DC=local
|       configurationNamingContext: CN=Configuration,DC=htb,DC=local
|       rootDomainNamingContext: DC=htb,DC=local
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
|       highestCommittedUSN: 1189293
|       supportedSASLMechanisms: GSSAPI
|       supportedSASLMechanisms: GSS-SPNEGO
|       supportedSASLMechanisms: EXTERNAL
|       supportedSASLMechanisms: DIGEST-MD5
|       dnsHostName: FOREST.htb.local
|       ldapServiceName: htb.local:forest$@HTB.LOCAL
|       serverName: CN=FOREST,CN=Servers,CN=Default-First-Site-Name,CN=Sites,CN=Configuration,DC=htb,DC=local
|       supportedCapabilities: 1.2.840.113556.1.4.800
|       supportedCapabilities: 1.2.840.113556.1.4.1670
|       supportedCapabilities: 1.2.840.113556.1.4.1791
|       supportedCapabilities: 1.2.840.113556.1.4.1935
|       supportedCapabilities: 1.2.840.113556.1.4.2080
|       supportedCapabilities: 1.2.840.113556.1.4.2237
|       isSynchronized: TRUE
|       isGlobalCatalogReady: TRUE
|       domainFunctionality: 7
|       forestFunctionality: 7
|_      domainControllerFunctionality: 7
Service Info: Host: FOREST; OS: Windows

Nmap done: 1 IP address (1 host up) scanned in 0.11 seconds
```

### Checking for anonymous access

- SMB anonymous access check:

```bash
netexec smb 10.129.95.210 -u '' -p '' --shares
```

```bash
SMB         10.129.95.210   445    FOREST           [*] Windows Server 2016 Standard 14393 x64 (name:FOREST) (domain:htb.local) (signing:True) (SMBv1:True) (Null Auth:True)
SMB         10.129.95.210   445    FOREST           [+] htb.local\: 
SMB         10.129.95.210   445    FOREST           [-] Error enumerating shares: STATUS_ACCESS_DENIED
```

>[!important] Anonymous succeeds, no shares (access denied).

## LDAP

### Querying RootDSE

```bash
ldapsearch -x -H ldap://10.129.95.210 -b '' -s base '(objectClass=*)'
```

```bash
# extended LDIF
#
# LDAPv3
# base <> with scope baseObject
# filter: (objectClass=*)
# requesting: ALL
#

#
dn:
currentTime: 20260815103850.0Z
subschemaSubentry: CN=Aggregate,CN=Schema,CN=Configuration,DC=htb,DC=local
dsServiceName: CN=NTDS Settings,CN=FOREST,CN=Servers,CN=Default-First-Site-Nam
 e,CN=Sites,CN=Configuration,DC=htb,DC=local
namingContexts: DC=htb,DC=local
namingContexts: CN=Configuration,DC=htb,DC=local
namingContexts: CN=Schema,CN=Configuration,DC=htb,DC=local
namingContexts: DC=DomainDnsZones,DC=htb,DC=local
namingContexts: DC=ForestDnsZones,DC=htb,DC=local
defaultNamingContext: DC=htb,DC=local
schemaNamingContext: CN=Schema,CN=Configuration,DC=htb,DC=local
configurationNamingContext: CN=Configuration,DC=htb,DC=local
rootDomainNamingContext: DC=htb,DC=local
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
highestCommittedUSN: 1070877
supportedSASLMechanisms: GSSAPI
supportedSASLMechanisms: GSS-SPNEGO
supportedSASLMechanisms: EXTERNAL
supportedSASLMechanisms: DIGEST-MD5
dnsHostName: FOREST.htb.local
ldapServiceName: htb.local:forest$@HTB.LOCAL
serverName: CN=FOREST,CN=Servers,CN=Default-First-Site-Name,CN=Sites,CN=Config
 uration,DC=htb,DC=local
supportedCapabilities: 1.2.840.113556.1.4.800
supportedCapabilities: 1.2.840.113556.1.4.1670
supportedCapabilities: 1.2.840.113556.1.4.1791
supportedCapabilities: 1.2.840.113556.1.4.1935
supportedCapabilities: 1.2.840.113556.1.4.2080
supportedCapabilities: 1.2.840.113556.1.4.2237
isSynchronized: TRUE
isGlobalCatalogReady: TRUE
domainFunctionality: 7
forestFunctionality: 7
domainControllerFunctionality: 7

# search result
search: 2
result: 0 Success

# numResponses: 2
# numEntries: 1
```

- Checking for anonymous access:

```bash
ldapsearch -x -H ldap://10.129.95.210 -b 'DC=htb,DC=local' -s base '(objectClass=domain)' distinguishedName objectSid
```

```bash
# extended LDIF
#
# LDAPv3
# base <DC=htb,DC=local> with scope baseObject
# filter: (objectClass=domain)
# requesting: distinguishedName objectSid 
#

# htb.local
dn: DC=htb,DC=local
distinguishedName: DC=htb,DC=local
objectSid:: AQQAAAAAAAUVAAAALB4ltxV1shXFsPNP

# search result
search: 2
result: 0 Success

# numResponses: 2
# numEntries: 1
```

- The query succeeds, which means you can use LDAP anonymous bind to enumerate the domain.

### Dumping all users


- Enumerate all domain user objects:

```bash
ldapsearch -x -H ldap://10.129.95.210 -b 'DC=htb,DC=local' -s sub '(&(objectCategory=person)(objectClass=user))' sAMAccountName userPrincipalName displayName distinguishedName
```

```bash
# extended LDIF
#
# LDAPv3
# base <DC=htb,DC=local> with scope subtree
# filter: (&(objectCategory=person)(objectClass=user))
# requesting: sAMAccountName userPrincipalName displayName distinguishedName 
#

# Guest, Users, htb.local
dn: CN=Guest,CN=Users,DC=htb,DC=local
distinguishedName: CN=Guest,CN=Users,DC=htb,DC=local
sAMAccountName: Guest

# DefaultAccount, Users, htb.local
dn: CN=DefaultAccount,CN=Users,DC=htb,DC=local
distinguishedName: CN=DefaultAccount,CN=Users,DC=htb,DC=local
sAMAccountName: DefaultAccount

# Exchange Online-ApplicationAccount, Users, htb.local
dn: CN=Exchange Online-ApplicationAccount,CN=Users,DC=htb,DC=local
distinguishedName: CN=Exchange Online-ApplicationAccount,CN=Users,DC=htb,DC=lo
 cal
sAMAccountName: $331000-VK4ADACQNUCA
userPrincipalName: Exchange_Online-ApplicationAccount@htb.local

# SystemMailbox{1f05a927-89c0-4725-adca-4527114196a1}, Users, htb.local
dn: CN=SystemMailbox{1f05a927-89c0-4725-adca-4527114196a1},CN=Users,DC=htb,DC=
 local
distinguishedName: CN=SystemMailbox{1f05a927-89c0-4725-adca-4527114196a1},CN=U
 sers,DC=htb,DC=local
displayName: Microsoft Exchange Approval Assistant
sAMAccountName: SM_2c8eef0a09b545acb
userPrincipalName: SystemMailbox{1f05a927-89c0-4725-adca-4527114196a1}@htb.loc
 al

# SystemMailbox{bb558c35-97f1-4cb9-8ff7-d53741dc928c}, Users, htb.local
dn: CN=SystemMailbox{bb558c35-97f1-4cb9-8ff7-d53741dc928c},CN=Users,DC=htb,DC=
 local
distinguishedName: CN=SystemMailbox{bb558c35-97f1-4cb9-8ff7-d53741dc928c},CN=U
 sers,DC=htb,DC=local
displayName: Microsoft Exchange
sAMAccountName: SM_ca8c2ed5bdab4dc9b
userPrincipalName: SystemMailbox{bb558c35-97f1-4cb9-8ff7-d53741dc928c}@htb.loc
 al

# SystemMailbox{e0dc1c29-89c3-4034-b678-e6c29d823ed9}, Users, htb.local
dn: CN=SystemMailbox{e0dc1c29-89c3-4034-b678-e6c29d823ed9},CN=Users,DC=htb,DC=
 local
distinguishedName: CN=SystemMailbox{e0dc1c29-89c3-4034-b678-e6c29d823ed9},CN=U
 sers,DC=htb,DC=local
displayName: Microsoft Exchange
sAMAccountName: SM_75a538d3025e4db9a
userPrincipalName: SystemMailbox{e0dc1c29-89c3-4034-b678-e6c29d823ed9}@htb.loc
 al

# DiscoverySearchMailbox {D919BA05-46A6-415f-80AD-7E09334BB852}, Users, htb.loc
 al
dn: CN=DiscoverySearchMailbox {D919BA05-46A6-415f-80AD-7E09334BB852},CN=Users,
 DC=htb,DC=local
distinguishedName: CN=DiscoverySearchMailbox {D919BA05-46A6-415f-80AD-7E09334B
 B852},CN=Users,DC=htb,DC=local
displayName: Discovery Search Mailbox
sAMAccountName: SM_681f53d4942840e18
userPrincipalName: DiscoverySearchMailbox {D919BA05-46A6-415f-80AD-7E09334BB85
 2}@htb.local

# Migration.8f3e7716-2011-43e4-96b1-aba62d229136, Users, htb.local
dn: CN=Migration.8f3e7716-2011-43e4-96b1-aba62d229136,CN=Users,DC=htb,DC=local
distinguishedName: CN=Migration.8f3e7716-2011-43e4-96b1-aba62d229136,CN=Users,
 DC=htb,DC=local
displayName: Microsoft Exchange Migration
sAMAccountName: SM_1b41c9286325456bb
userPrincipalName: Migration.8f3e7716-2011-43e4-96b1-aba62d229136@htb.local

# FederatedEmail.4c1f4d8b-8179-4148-93bf-00a95fa1e042, Users, htb.local
dn: CN=FederatedEmail.4c1f4d8b-8179-4148-93bf-00a95fa1e042,CN=Users,DC=htb,DC=
 local
distinguishedName: CN=FederatedEmail.4c1f4d8b-8179-4148-93bf-00a95fa1e042,CN=U
 sers,DC=htb,DC=local
displayName: Microsoft Exchange Federation Mailbox
sAMAccountName: SM_9b69f1b9d2cc45549
userPrincipalName: FederatedEmail.4c1f4d8b-8179-4148-93bf-00a95fa1e042@htb.loc
 al

# SystemMailbox{D0E409A0-AF9B-4720-92FE-AAC869B0D201}, Users, htb.local
dn: CN=SystemMailbox{D0E409A0-AF9B-4720-92FE-AAC869B0D201},CN=Users,DC=htb,DC=
 local
distinguishedName: CN=SystemMailbox{D0E409A0-AF9B-4720-92FE-AAC869B0D201},CN=U
 sers,DC=htb,DC=local
displayName: E4E Encryption Store - Active
sAMAccountName: SM_7c96b981967141ebb
userPrincipalName: SystemMailbox{D0E409A0-AF9B-4720-92FE-AAC869B0D201}@htb.loc
 al

# SystemMailbox{2CE34405-31BE-455D-89D7-A7C7DA7A0DAA}, Users, htb.local
dn: CN=SystemMailbox{2CE34405-31BE-455D-89D7-A7C7DA7A0DAA},CN=Users,DC=htb,DC=
 local
distinguishedName: CN=SystemMailbox{2CE34405-31BE-455D-89D7-A7C7DA7A0DAA},CN=U
 sers,DC=htb,DC=local
displayName: Microsoft Exchange
sAMAccountName: SM_c75ee099d0a64c91b
userPrincipalName: SystemMailbox{2CE34405-31BE-455D-89D7-A7C7DA7A0DAA}@htb.loc
 al

# SystemMailbox{8cc370d3-822a-4ab8-a926-bb94bd0641a9}, Users, htb.local
dn: CN=SystemMailbox{8cc370d3-822a-4ab8-a926-bb94bd0641a9},CN=Users,DC=htb,DC=
 local
distinguishedName: CN=SystemMailbox{8cc370d3-822a-4ab8-a926-bb94bd0641a9},CN=U
 sers,DC=htb,DC=local
displayName: SystemMailbox{8cc370d3-822a-4ab8-a926-bb94bd0641a9}
sAMAccountName: SM_1ffab36a2f5f479cb
userPrincipalName: SystemMailbox{8cc370d3-822a-4ab8-a926-bb94bd0641a9}@htb.loc
 al

# HealthMailboxc3d7722415ad41a5b19e3e00e165edbe, Monitoring Mailboxes, Microsof
 t Exchange System Objects, htb.local
dn: CN=HealthMailboxc3d7722415ad41a5b19e3e00e165edbe,CN=Monitoring Mailboxes,C
 N=Microsoft Exchange System Objects,DC=htb,DC=local
distinguishedName: CN=HealthMailboxc3d7722415ad41a5b19e3e00e165edbe,CN=Monitor
 ing Mailboxes,CN=Microsoft Exchange System Objects,DC=htb,DC=local
displayName: HealthMailbox-EXCH01-Mailbox-Database-1118319013
sAMAccountName: HealthMailboxc3d7722
userPrincipalName: HealthMailboxc3d7722415ad41a5b19e3e00e165edbe@htb.local

# HealthMailboxfc9daad117b84fe08b081886bd8a5a50, Monitoring Mailboxes, Microsof
 t Exchange System Objects, htb.local
dn: CN=HealthMailboxfc9daad117b84fe08b081886bd8a5a50,CN=Monitoring Mailboxes,C
 N=Microsoft Exchange System Objects,DC=htb,DC=local
distinguishedName: CN=HealthMailboxfc9daad117b84fe08b081886bd8a5a50,CN=Monitor
 ing Mailboxes,CN=Microsoft Exchange System Objects,DC=htb,DC=local
displayName: HealthMailbox-EXCH01-001
sAMAccountName: HealthMailboxfc9daad
userPrincipalName: HealthMailboxfc9daad117b84fe08b081886bd8a5a50@htb.local

# HealthMailboxc0a90c97d4994429b15003d6a518f3f5, Monitoring Mailboxes, Microsof
 t Exchange System Objects, htb.local
dn: CN=HealthMailboxc0a90c97d4994429b15003d6a518f3f5,CN=Monitoring Mailboxes,C
 N=Microsoft Exchange System Objects,DC=htb,DC=local
distinguishedName: CN=HealthMailboxc0a90c97d4994429b15003d6a518f3f5,CN=Monitor
 ing Mailboxes,CN=Microsoft Exchange System Objects,DC=htb,DC=local
displayName: HealthMailbox-EXCH01-002
sAMAccountName: HealthMailboxc0a90c9
userPrincipalName: HealthMailboxc0a90c97d4994429b15003d6a518f3f5@htb.local

# HealthMailbox670628ec4dd64321acfdf6e67db3a2d8, Monitoring Mailboxes, Microsof
 t Exchange System Objects, htb.local
dn: CN=HealthMailbox670628ec4dd64321acfdf6e67db3a2d8,CN=Monitoring Mailboxes,C
 N=Microsoft Exchange System Objects,DC=htb,DC=local
distinguishedName: CN=HealthMailbox670628ec4dd64321acfdf6e67db3a2d8,CN=Monitor
 ing Mailboxes,CN=Microsoft Exchange System Objects,DC=htb,DC=local
displayName: HealthMailbox-EXCH01-003
sAMAccountName: HealthMailbox670628e
userPrincipalName: HealthMailbox670628ec4dd64321acfdf6e67db3a2d8@htb.local

# HealthMailbox968e74dd3edb414cb4018376e7dd95ba, Monitoring Mailboxes, Microsof
 t Exchange System Objects, htb.local
dn: CN=HealthMailbox968e74dd3edb414cb4018376e7dd95ba,CN=Monitoring Mailboxes,C
 N=Microsoft Exchange System Objects,DC=htb,DC=local
distinguishedName: CN=HealthMailbox968e74dd3edb414cb4018376e7dd95ba,CN=Monitor
 ing Mailboxes,CN=Microsoft Exchange System Objects,DC=htb,DC=local
displayName: HealthMailbox-EXCH01-004
sAMAccountName: HealthMailbox968e74d
userPrincipalName: HealthMailbox968e74dd3edb414cb4018376e7dd95ba@htb.local

# HealthMailbox6ded67848a234577a1756e072081d01f, Monitoring Mailboxes, Microsof
 t Exchange System Objects, htb.local
dn: CN=HealthMailbox6ded67848a234577a1756e072081d01f,CN=Monitoring Mailboxes,C
 N=Microsoft Exchange System Objects,DC=htb,DC=local
distinguishedName: CN=HealthMailbox6ded67848a234577a1756e072081d01f,CN=Monitor
 ing Mailboxes,CN=Microsoft Exchange System Objects,DC=htb,DC=local
displayName: HealthMailbox-EXCH01-005
sAMAccountName: HealthMailbox6ded678
userPrincipalName: HealthMailbox6ded67848a234577a1756e072081d01f@htb.local

# HealthMailbox83d6781be36b4bbf8893b03c2ee379ab, Monitoring Mailboxes, Microsof
 t Exchange System Objects, htb.local
dn: CN=HealthMailbox83d6781be36b4bbf8893b03c2ee379ab,CN=Monitoring Mailboxes,C
 N=Microsoft Exchange System Objects,DC=htb,DC=local
distinguishedName: CN=HealthMailbox83d6781be36b4bbf8893b03c2ee379ab,CN=Monitor
 ing Mailboxes,CN=Microsoft Exchange System Objects,DC=htb,DC=local
displayName: HealthMailbox-EXCH01-006
sAMAccountName: HealthMailbox83d6781
userPrincipalName: HealthMailbox83d6781be36b4bbf8893b03c2ee379ab@htb.local

# HealthMailboxfd87238e536e49e08738480d300e3772, Monitoring Mailboxes, Microsof
 t Exchange System Objects, htb.local
dn: CN=HealthMailboxfd87238e536e49e08738480d300e3772,CN=Monitoring Mailboxes,C
 N=Microsoft Exchange System Objects,DC=htb,DC=local
distinguishedName: CN=HealthMailboxfd87238e536e49e08738480d300e3772,CN=Monitor
 ing Mailboxes,CN=Microsoft Exchange System Objects,DC=htb,DC=local
displayName: HealthMailbox-EXCH01-007
sAMAccountName: HealthMailboxfd87238
userPrincipalName: HealthMailboxfd87238e536e49e08738480d300e3772@htb.local

# HealthMailboxb01ac647a64648d2a5fa21df27058a24, Monitoring Mailboxes, Microsof
 t Exchange System Objects, htb.local
dn: CN=HealthMailboxb01ac647a64648d2a5fa21df27058a24,CN=Monitoring Mailboxes,C
 N=Microsoft Exchange System Objects,DC=htb,DC=local
distinguishedName: CN=HealthMailboxb01ac647a64648d2a5fa21df27058a24,CN=Monitor
 ing Mailboxes,CN=Microsoft Exchange System Objects,DC=htb,DC=local
displayName: HealthMailbox-EXCH01-008
sAMAccountName: HealthMailboxb01ac64
userPrincipalName: HealthMailboxb01ac647a64648d2a5fa21df27058a24@htb.local

# HealthMailbox7108a4e350f84b32a7a90d8e718f78cf, Monitoring Mailboxes, Microsof
 t Exchange System Objects, htb.local
dn: CN=HealthMailbox7108a4e350f84b32a7a90d8e718f78cf,CN=Monitoring Mailboxes,C
 N=Microsoft Exchange System Objects,DC=htb,DC=local
distinguishedName: CN=HealthMailbox7108a4e350f84b32a7a90d8e718f78cf,CN=Monitor
 ing Mailboxes,CN=Microsoft Exchange System Objects,DC=htb,DC=local
displayName: HealthMailbox-EXCH01-009
sAMAccountName: HealthMailbox7108a4e
userPrincipalName: HealthMailbox7108a4e350f84b32a7a90d8e718f78cf@htb.local

# HealthMailbox0659cc188f4c4f9f978f6c2142c4181e, Monitoring Mailboxes, Microsof
 t Exchange System Objects, htb.local
dn: CN=HealthMailbox0659cc188f4c4f9f978f6c2142c4181e,CN=Monitoring Mailboxes,C
 N=Microsoft Exchange System Objects,DC=htb,DC=local
distinguishedName: CN=HealthMailbox0659cc188f4c4f9f978f6c2142c4181e,CN=Monitor
 ing Mailboxes,CN=Microsoft Exchange System Objects,DC=htb,DC=local
displayName: HealthMailbox-EXCH01-010
sAMAccountName: HealthMailbox0659cc1
userPrincipalName: HealthMailbox0659cc188f4c4f9f978f6c2142c4181e@htb.local

# Sebastien Caron, Exchange Administrators, Information Technology, Employees, 
 htb.local
dn: CN=Sebastien Caron,OU=Exchange Administrators,OU=Information Technology,OU
 =Employees,DC=htb,DC=local
distinguishedName: CN=Sebastien Caron,OU=Exchange Administrators,OU=Informatio
 n Technology,OU=Employees,DC=htb,DC=local
displayName: Sebastien Caron
sAMAccountName: sebastien
userPrincipalName: sebastien@htb.local

# Lucinda Berger, IT Management, Information Technology, Employees, htb.local
dn: CN=Lucinda Berger,OU=IT Management,OU=Information Technology,OU=Employees,
 DC=htb,DC=local
distinguishedName: CN=Lucinda Berger,OU=IT Management,OU=Information Technolog
 y,OU=Employees,DC=htb,DC=local
displayName: Lucinda Berger
sAMAccountName: lucinda
userPrincipalName: lucinda@htb.local

# Andy Hislip, Helpdesk, Information Technology, Employees, htb.local
dn: CN=Andy Hislip,OU=Helpdesk,OU=Information Technology,OU=Employees,DC=htb,D
 C=local
distinguishedName: CN=Andy Hislip,OU=Helpdesk,OU=Information Technology,OU=Emp
 loyees,DC=htb,DC=local
displayName: Andy Hislip
sAMAccountName: andy
userPrincipalName: andy@htb.local

# Mark Brandt, Sysadmins, Information Technology, Employees, htb.local
dn: CN=Mark Brandt,OU=Sysadmins,OU=Information Technology,OU=Employees,DC=htb,
 DC=local
distinguishedName: CN=Mark Brandt,OU=Sysadmins,OU=Information Technology,OU=Em
 ployees,DC=htb,DC=local
displayName: Mark Brandt
sAMAccountName: mark
userPrincipalName: mark@htb.local

# Santi Rodriguez, Developers, Information Technology, Employees, htb.local
dn: CN=Santi Rodriguez,OU=Developers,OU=Information Technology,OU=Employees,DC
 =htb,DC=local
distinguishedName: CN=Santi Rodriguez,OU=Developers,OU=Information Technology,
 OU=Employees,DC=htb,DC=local
displayName: Santi Rodriguez
sAMAccountName: santi
userPrincipalName: santi@htb.local

# search reference
ref: ldap://ForestDnsZones.htb.local/DC=ForestDnsZones,DC=htb,DC=local

# search reference
ref: ldap://DomainDnsZones.htb.local/DC=DomainDnsZones,DC=htb,DC=local

# search reference
ref: ldap://htb.local/CN=Configuration,DC=htb,DC=local

# search result
search: 2
result: 0 Success

# numResponses: 32
# numEntries: 28
# numReferences: 3
```

### Accounts with pre-authentication disabled (AS-REP roasting)

- Find accounts with pre-authentication disabled:

```bash
ldapsearch -x -H ldap://10.129.95.210 -b 'DC=htb,DC=local' -s sub '(&(objectCategory=person)(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=4194304)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))' sAMAccountName userPrincipalName distinguishedName userAccountControl
```



## RPC enumeration


- RPC anonymous access gives you a session:

```bash
rpcclient -U "" -N 10.129.95.210
rpcclient $> 
```

>[!important] RPC anonymous works.


- Domain information:

```bash
rpcclient $> querydominfo

Domain:		HTB
Server:		
Comment:	
Total Users:	105
Total Groups:	0
Total Aliases:	0
Sequence No:	1
Force Logoff:	18446744073709551615
Domain Server State:	0x1
Server Role:	ROLE_DOMAIN_PDC
Unknown 3:	0x1
```

- Enumerating domain users:

```bash
rpcclient $> enumdomusers

user:[Administrator] rid:[0x1f4]
user:[Guest] rid:[0x1f5]
user:[krbtgt] rid:[0x1f6]
user:[DefaultAccount] rid:[0x1f7]
user:[$331000-VK4ADACQNUCA] rid:[0x463]
user:[SM_2c8eef0a09b545acb] rid:[0x464]
user:[SM_ca8c2ed5bdab4dc9b] rid:[0x465]
user:[SM_75a538d3025e4db9a] rid:[0x466]
user:[SM_681f53d4942840e18] rid:[0x467]
user:[SM_1b41c9286325456bb] rid:[0x468]
user:[SM_9b69f1b9d2cc45549] rid:[0x469]
user:[SM_7c96b981967141ebb] rid:[0x46a]
user:[SM_c75ee099d0a64c91b] rid:[0x46b]
user:[SM_1ffab36a2f5f479cb] rid:[0x46c]
user:[HealthMailboxc3d7722] rid:[0x46e]
user:[HealthMailboxfc9daad] rid:[0x46f]
user:[HealthMailboxc0a90c9] rid:[0x470]
user:[HealthMailbox670628e] rid:[0x471]
user:[HealthMailbox968e74d] rid:[0x472]
user:[HealthMailbox6ded678] rid:[0x473]
user:[HealthMailbox83d6781] rid:[0x474]
user:[HealthMailboxfd87238] rid:[0x475]
user:[HealthMailboxb01ac64] rid:[0x476]
user:[HealthMailbox7108a4e] rid:[0x477]
user:[HealthMailbox0659cc1] rid:[0x478]
user:[sebastien] rid:[0x479]
user:[lucinda] rid:[0x47a]
user:[svc-alfresco] rid:[0x47b]
user:[andy] rid:[0x47e]
user:[mark] rid:[0x47f]
user:[santi] rid:[0x480]
```

- Domain groups:

```bash
rpcclient $> enumdomgroups

group:[Enterprise Read-only Domain Controllers] rid:[0x1f2]
group:[Domain Admins] rid:[0x200]
group:[Domain Users] rid:[0x201]
group:[Domain Guests] rid:[0x202]
group:[Domain Computers] rid:[0x203]
group:[Domain Controllers] rid:[0x204]
group:[Schema Admins] rid:[0x206]
group:[Enterprise Admins] rid:[0x207]
group:[Group Policy Creator Owners] rid:[0x208]
group:[Read-only Domain Controllers] rid:[0x209]
group:[Cloneable Domain Controllers] rid:[0x20a]
group:[Protected Users] rid:[0x20d]
group:[Key Admins] rid:[0x20e]
group:[Enterprise Key Admins] rid:[0x20f]
group:[DnsUpdateProxy] rid:[0x44e]
group:[Organization Management] rid:[0x450]
group:[Recipient Management] rid:[0x451]
group:[View-Only Organization Management] rid:[0x452]
group:[Public Folder Management] rid:[0x453]
group:[UM Management] rid:[0x454]
group:[Help Desk] rid:[0x455]
group:[Records Management] rid:[0x456]
group:[Discovery Management] rid:[0x457]
group:[Server Management] rid:[0x458]
group:[Delegated Setup] rid:[0x459]
group:[Hygiene Management] rid:[0x45a]
group:[Compliance Management] rid:[0x45b]
group:[Security Reader] rid:[0x45c]
group:[Security Administrator] rid:[0x45d]
group:[Exchange Servers] rid:[0x45e]
group:[Exchange Trusted Subsystem] rid:[0x45f]
group:[Managed Availability Servers] rid:[0x460]
group:[Exchange Windows Permissions] rid:[0x461]
group:[ExchangeLegacyInterop] rid:[0x462]
group:[$D31000-NSEL5BRJ63V7] rid:[0x46d]
group:[Service Accounts] rid:[0x47c]
group:[Privileged IT Accounts] rid:[0x47d]
group:[test] rid:[0x13ed]
```
## Questions

1. For which domain is this machine a Domain Controller?
	- `htb.local`

2. Which of the following services allows for anonymous authentication and can provide us with valuable information about the machine? FTP, LDAP, SMB, WinRM
	- LDAP

3. Which user has Kerberos Pre-Authentication disabled?
	- 