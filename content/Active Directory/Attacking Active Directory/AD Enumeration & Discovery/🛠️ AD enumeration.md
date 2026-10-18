---
created: 2026-07-30
updated: 2026-10-10
---

>[!note] To identify if a Linux machine is domain-joined, use [`realm`](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/7/html/windows_integration_guide/cmd-realmd).
>```bash
>realm list
>```
## AD enumeration

- Enumeration is not a single step; it is an **iterative process** that progresses from unauthenticated external recon to deep authenticated analysis. Each piece of information informs the next query.
- The goal is to answer: *What exists in this environment, how is it configured, and where are the weaknesses?*
- Enumeration never truly ends — every new credential, every new foothold, and every new host unlocks additional data.

> [!important] The quality of the attack phase is directly proportional to the quality of the enumeration phase. **You can't attack what you can't see.**
### Tools

- [`Impacket toolkit`](https://github.com/CoreSecurity/impacket/) — A collection of tools written in Python for interacting with network protocols; includes scripts for enumerating and attacking Active Directory.

```bash
pipx install impacket
```

- [`Responder`](https://github.com/lgandx/Responder) — A tool designed fro LLMNR, NDT-NS, and MDNS poisoning for HTTP, SMB, MSSQL, FTP, LDAP, Kerberos, DNS, and more.

```bash
apt install responder
```

- [`fping`](https://github.com/schweikert/fping) — A tool for sending ICMP probes, similar to `ping`, but optimized for scanning multiple hosts in parallel.

```bash
apt install fping
```

- [`enum4linux`](https://github.com/CiscoCXSecurity/enum4linux) — A tool for enumerating data from Windows ad Samba hosts from Linux.

```bash
apt install enum4linux
```

- [`enum4linux-ng`](https://github.com/cddmp/enum4linux-ng) — An improved rework of the original `enum4linux` tool.

```bash
apt install enum4linux-ng 
```

- [`BloodHound`](https://github.com/BloodHoundAD/BloodHound) — Visualizes hidden relationships and permissions withing Active Directory domains using graph theory.
- [`BloodHound.py`](https://github.com/fox-it/BloodHound.py) — is a **Python-based data collector (ingestor)** for `BloodHound`, based on `Impacket`.

```bash
pipx install bloodhound-py
```

- [`Kerbrute`](https://github.com/ropnop/kerbrute) — A tool written in Go that uses Kerberos Pre-Authentication to enumerate Active Directory accounts, perform password spraying, and brute-forcing.

```bash
wget https://github.com/ropnop/kerbrute/releases/latest/download/kerbrute_linux_amd64
chmod +x kerbrute_linux_amd64 && sudo mv kerbrute_linux_amd64 /usr/local/bin/kerbrute
```

- [`NetExec`](https://github.com/Pennyw0rth/NetExec) — Successor of `CrackMapExec` (CME), a versatile network enumeration, execution, and brute-force tool.

```bash
pipx install git+https://github.com/Pennyw0rth/NetExec
```

- [`Snaffler`](https://github.com/SnaffCon/Snaffler) — A tool useful for finding information (such as credentials) in Active Directory on computers with accessible file shares.

```bash
wget https://github.com/SnaffCon/Snaffler/releases/download/1.0.244/Snaffler.exe
```

- [`smbmap`](https://github.com/ShawnDEvans/smbmap) — An SMB share enumeration tool across a domain.

```bash
pipx install smbmap
```

- A wordlist for username enumeration (`jdoe` format): 

```bash
git clone https://github.com/insidetrust/statistically-likely-usernames /opt/statistically-likely-usernames
```

- [`ldapsearch`](https://man.archlinux.org/man/ldapsearch.1.en) — An LDAP search tool.

```bash
apt install openldap
```

- [`rpcclient`](https://www.samba.org/samba/docs/current/man-html/rpcclient.1.html) — A part of the Samba suite on Linux distributions that can be used to perform a variety of Active Directory enumeration tasks via the remote RPC service.

```bash
pip install rpcclient
```


## Network discovery

- The next step is to discovery live hosts, open ports, and running services. 
### `fping`

- [`fping`](https://github.com/schweikert/fping) is optimized for sending ICMP probes to multiple hosts in parallel — far faster than traditional `ping` on subnets:

```bash
fping -asgq 10.10.11.0/23
```

>[!example]-
> ```bash
> fping -asgq 172.16.5.0/23
> ```
> 
> ```bash
> 172.16.5.5
> 172.16.5.130
> 172.16.5.225
> 
>      510 targets
>        3 alive
>      507 unreachable
>        0 unknown addresses
> 
>     2028 timeouts (waiting for response)
>     2031 ICMP Echos sent
>        3 ICMP Echo Replies received
>     2028 other ICMP received
> 
>  0.147 ms (min round trip time)
>  1.28 ms (avg round trip time)
>  3.24 ms (max round trip time)
>        15.005 sec (elapsed real time)
> ```

| Option             | Description                                                                             |
| ------------------ | --------------------------------------------------------------------------------------- |
| `-a`, `--alive`    | Show live targets.                                                                      |
| `-s`, `--stats`    | Print final stats.                                                                      |
| `-q`, `--quiet`    | Quiet mode (don't show per-target/per-ping results).                                    |
| `-n`, `--name`     | Show targets by hostnames (perform reverse DNS lookup for target IP addresses).         |
| `-A`, `--addr`     | Show targets by address.                                                                |
| `-g`, `--generate` | Auto-generate a list of targets from a CIDR range (works only if no `-f` is specified). |
| `-f`, `--file`     | Read targets from a file (`-` means `stdin`).                                           |
### `arp-ping`

> [!note] Only applicable when you're on the **local broadcast domain** (you must be on the same subnet; ARP is non-routable).

- [`arp-scan`](https://github.com/royhills/arp-scan) uses ARP requests to discover hosts on the local subnet; it often finds hosts that block ICMP:

```bash
sudo arp-scan -I eth0 172.16.5.0/24
```
### Nmap

- For ping sweeps, use `-sn`: 

```bash
nmap -sn 10.10.11.0/24
```

- Port and service discovery:

```bash
nmap -Pn -sV -A -iL hosts.txt -oA nmap_scan
```

>[!example]-
> ```bash
> nmap -Pn -sV -A -iL hosts.txt
> ```
> 
> ```bash
> Starting Nmap 7.92 ( https://nmap.org ) at 2026-07-30 09:22 EDT
> 
> Nmap scan report for inlanefreight.local (172.16.5.5)
> Host is up (0.060s latency).
> Not shown: 988 closed tcp ports (conn-refused)
> PORT     STATE SERVICE       VERSION
> 53/tcp   open  domain        Simple DNS Plus
> 88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-07-30 13:23:41Z)
> 135/tcp  open  msrpc         Microsoft Windows RPC
> 139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
> 389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: INLANEFREIGHT.LOCAL0., Site: Default-First-Site-Name)
> | ssl-cert: Subject: 
> | Subject Alternative Name: DNS:ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL, DNS:INLANEFREIGHT.LOCAL, DNS:INLANEFREIGHT
> | Not valid before: 2026-07-22T08:52:23
> |_Not valid after:  2027-07-22T08:52:23
> |_ssl-date: 2026-07-30T13:25:25+00:00; +20s from scanner time.
> 445/tcp  open  microsoft-ds?
> 464/tcp  open  kpasswd5?
> 593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
> 636/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: INLANEFREIGHT.LOCAL0., Site: Default-First-Site-Name)
> |_ssl-date: 2026-07-30T13:25:25+00:00; +20s from scanner time.
> | ssl-cert: Subject: 
> | Subject Alternative Name: DNS:ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL, DNS:INLANEFREIGHT.LOCAL, DNS:INLANEFREIGHT
> | Not valid before: 2026-07-22T08:52:23
> |_Not valid after:  2027-07-22T08:52:23
> 3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: INLANEFREIGHT.LOCAL0., Site: Default-First-Site-Name)
> | ssl-cert: Subject: 
> | Subject Alternative Name: DNS:ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL, DNS:INLANEFREIGHT.LOCAL, DNS:INLANEFREIGHT
> | Not valid before: 2026-07-22T08:52:23
> |_Not valid after:  2027-07-22T08:52:23
> |_ssl-date: 2026-07-30T13:25:25+00:00; +20s from scanner time.
> 3269/tcp open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: INLANEFREIGHT.LOCAL0., Site: Default-First-Site-Name)
> | ssl-cert: Subject: 
> | Subject Alternative Name: DNS:ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL, DNS:INLANEFREIGHT.LOCAL, DNS:INLANEFREIGHT
> | Not valid before: 2026-07-22T08:52:23
> |_Not valid after:  2027-07-22T08:52:23
> |_ssl-date: 2026-07-30T13:25:25+00:00; +20s from scanner time.
> 3389/tcp open  ms-wbt-server Microsoft Terminal Services
> |_ssl-date: 2026-07-30T13:25:25+00:00; +20s from scanner time.
> | ssl-cert: Subject: commonName=ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL
> | Not valid before: 2026-07-21T08:46:17
> |_Not valid after:  2027-01-20T08:46:17
> | rdp-ntlm-info: 
> |   Target_Name: INLANEFREIGHT
> |   NetBIOS_Domain_Name: INLANEFREIGHT
> |   NetBIOS_Computer_Name: ACADEMY-EA-DC01
> |   DNS_Domain_Name: INLANEFREIGHT.LOCAL
> |   DNS_Computer_Name: ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL
> |   Product_Version: 10.0.17763
> |_  System_Time: 2026-07-30T13:24:20+00:00
> Service Info: Host: ACADEMY-EA-DC01; OS: Windows; CPE: cpe:/o:microsoft:windows
> 
> Host script results:
> |_clock-skew: mean: 19s, deviation: 0s, median: 19s
> |_nbstat: NetBIOS name: ACADEMY-EA-DC01, NetBIOS user: <unknown>, NetBIOS MAC: a2:de:ad:07:37:60 (unknown)
> | smb2-security-mode: 
> |   3.1.1: 
> |_    Message signing enabled and required
> | smb2-time: 
> |   date: 2026-07-30T13:24:20
> |_  start_date: N/A
> 
> Nmap scan report for 172.16.5.130
> Host is up (0.062s latency).
> Not shown: 992 closed tcp ports (conn-refused)
> PORT      STATE SERVICE       VERSION
> 80/tcp    open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
> 135/tcp   open  msrpc         Microsoft Windows RPC
> 139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
> 445/tcp   open  microsoft-ds?
> 808/tcp   open  ccproxy-http?
> 1433/tcp  open  ms-sql-s      Microsoft SQL Server 2019 15.00.2000.00; RTM
> | ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback
> | Not valid before: 2026-07-30T13:06:03
> |_Not valid after:  2056-07-30T13:06:03
> |_ssl-date: 2026-07-30T13:25:25+00:00; +20s from scanner time.
> | ms-sql-ntlm-info: 
> |   Target_Name: INLANEFREIGHT
> |   NetBIOS_Domain_Name: INLANEFREIGHT
> |   NetBIOS_Computer_Name: ACADEMY-EA-FILE
> |   DNS_Domain_Name: INLANEFREIGHT.LOCAL
> |   DNS_Computer_Name: ACADEMY-EA-FILE.INLANEFREIGHT.LOCAL
> |   DNS_Tree_Name: INLANEFREIGHT.LOCAL
> |_  Product_Version: 10.0.17763
> 3389/tcp  open  ms-wbt-server Microsoft Terminal Services
> | ssl-cert: Subject: commonName=ACADEMY-EA-FILE.INLANEFREIGHT.LOCAL
> | Not valid before: 2026-07-21T08:47:09
> |_Not valid after:  2027-01-20T08:47:09
> |_ssl-date: 2026-07-30T13:25:25+00:00; +20s from scanner time.
> | rdp-ntlm-info: 
> |   Target_Name: INLANEFREIGHT
> |   NetBIOS_Domain_Name: INLANEFREIGHT
> |   NetBIOS_Computer_Name: ACADEMY-EA-FILE
> |   DNS_Domain_Name: INLANEFREIGHT.LOCAL
> |   DNS_Computer_Name: ACADEMY-EA-FILE.INLANEFREIGHT.LOCAL
> |   DNS_Tree_Name: INLANEFREIGHT.LOCAL
> |   Product_Version: 10.0.17763
> |_  System_Time: 2026-07-30T13:24:20+00:00
> 16001/tcp open  mc-nmf        .NET Message Framing
> Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows
> 
> Host script results:
> |_nbstat: NetBIOS name: ACADEMY-EA-FILE, NetBIOS user: <unknown>, NetBIOS MAC: a2:de:ad:86:80:b7 (unknown)
> |_clock-skew: mean: 19s, deviation: 0s, median: 19s
> | smb2-time: 
> |   date: 2026-07-30T13:24:20
> |_  start_date: N/A
> | smb2-security-mode: 
> |   3.1.1: 
> |_    Message signing enabled but not required
> | ms-sql-info: 
> |   172.16.5.130:1433: 
> |     Version: 
> |       name: Microsoft SQL Server 2019 RTM
> |       number: 15.00.2000.00
> |       Product: Microsoft SQL Server 2019
> |       Service pack level: RTM
> |       Post-SP patches applied: false
> |_    TCP port: 1433
> 
> Nmap scan report for 172.16.5.225
> Host is up (0.063s latency).
> Not shown: 998 closed tcp ports (conn-refused)
> PORT     STATE SERVICE       VERSION
> 22/tcp   open  ssh           OpenSSH 8.4p1 Debian 5 (protocol 2.0)
> | ssh-hostkey: 
> |   3072 97:cc:9f:d0:a3:84:da:d1:a2:01:58:a1:f2:71:37:e5 (RSA)
> |   256 03:15:a9:1c:84:26:87:b7:5f:8d:72:73:9f:96:e0:f2 (ECDSA)
> |_  256 55:c9:4a:d2:63:8b:5f:f2:ed:7b:4e:38:e1:c9:f5:71 (ED25519)
> 3389/tcp open  ms-wbt-server xrdp
> Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
> 
> Post-scan script results:
> | clock-skew: 
> |   19s: 
> |     172.16.5.130
> |_    172.16.5.5 (inlanefreight.local)
> Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
> Nmap done: 3 IP addresses (3 hosts up) scanned in 132.41 seconds
> ```

| Option | Purpose                                                 |
| ------ | ------------------------------------------------------- |
| `-Pn`  | Treat all hosts as up (skip `ping` check).              |
| `-sV`  | Version detection on open ports.                        |
| `-A`   | Aggressive (OS detection, script scanning, traceroute). |
| `-iL`  | Read targets from a file.                               |
| `-oA`  | Output in all formats (`.nmap`, `.gnmap`, `.xml`).      |

**Key ports for AD enumeration:**

| Port          | Service        | Description                                |
| ------------- | -------------- | ------------------------------------------ |
| `53`          | DNS            | Domain resolution, SRV record enumeration. |
| `88`          | Kerberos       | Kerberos authentication.                   |
| `135`         | RPC            | Endpoint mapper — RPC service discovery.   |
| `139`/`445`   | SMB            | SMB shares.                                |
| `389`         | LDAP           | Anonymous LDAP binds, directory queries.   |
| `636`         | LDAPS          | Encrypted LDAP.                            |
| `3268`/`3269` | Global Catalog | Forest-wide searches.                      |
| `3389`        | RDP            | Remote Desktop Services.                   |
| `5985`/`5986` | WinRM          | Remote management (PowerShell remoting).   |
| `9389`        | AD WS          | Active Directory Web Services.             |

- Scan only ports most relevant to AD:

```bash
nmap -Pn -sV -A -p 53,88,135,139,445,389,636,3268,3269,3389,5985,5986 -iL hosts.txt
```

### Identifying Domain Controllers

>[!note] Domain Controllers typically have ports `88`, `389`, `636`, `3268`-`3269` open.

- The most reliable way to identify Domain Controllers using Nmap is using the **[`ldap-rootdse`](https://nmap.org/nsedoc/scripts/ldap-rootdse.html) script.** 
- The `ldap-rootdse` script queries the LDAP RootDSE (Root Directory Server Agent Service Entry) object, which is a special, read-only LDAP entry with a **zero-length DN (Distinguished Name)**. RootDSE provides metadata about the directory server itself and therefore only present on DCs.

```bash
nmap -Pn -p 389,636 --script ldap-rootdse -iL hosts.txt
```

- Another method is to run service discovery on ports that are often open on DCs:

```bash
nmap -p 88,389,445,464 --open -sV -iL hosts.txt
```

>[!example]-
> ```bash
> sudo nmap -Pn --script ldap-rootdse -iL hosts.txt
> ```
> 
> ```bash
> Starting Nmap 7.92 ( https://nmap.org ) at 2026-07-30 09:33 EDT
> Nmap scan report for inlanefreight.local (172.16.5.5)
> Host is up (0.019s latency).
> Not shown: 988 closed tcp ports (reset)
> PORT     STATE SERVICE
> 53/tcp   open  domain
> 88/tcp   open  kerberos-sec
> 135/tcp  open  msrpc
> 139/tcp  open  netbios-ssn
> 389/tcp  open  ldap
> | ldap-rootdse: 
> | LDAP Results
> |   <ROOT>
> |       domainFunctionality: 7
> |       forestFunctionality: 7
> |       domainControllerFunctionality: 7
> |       rootDomainNamingContext: DC=INLANEFREIGHT,DC=LOCAL
> |       ldapServiceName: INLANEFREIGHT.LOCAL:academy-ea-dc01$@INLANEFREIGHT.LOCAL
> |       isGlobalCatalogReady: TRUE
> |       supportedSASLMechanisms: GSSAPI
> |       supportedSASLMechanisms: GSS-SPNEGO
> |       supportedSASLMechanisms: EXTERNAL
> |       supportedSASLMechanisms: DIGEST-MD5
> |       supportedLDAPVersion: 3
> |       supportedLDAPVersion: 2
> |       supportedLDAPPolicies: MaxPoolThreads
> |       supportedLDAPPolicies: MaxPercentDirSyncRequests
> |       supportedLDAPPolicies: MaxDatagramRecv
> |       supportedLDAPPolicies: MaxReceiveBuffer
> |       supportedLDAPPolicies: InitRecvTimeout
> |       supportedLDAPPolicies: MaxConnections
> |       supportedLDAPPolicies: MaxConnIdleTime
> |       supportedLDAPPolicies: MaxPageSize
> |       supportedLDAPPolicies: MaxBatchReturnMessages
> |       supportedLDAPPolicies: MaxQueryDuration
> |       supportedLDAPPolicies: MaxDirSyncDuration
> |       supportedLDAPPolicies: MaxTempTableSize
> |       supportedLDAPPolicies: MaxResultSetSize
> |       supportedLDAPPolicies: MinResultSets
> |       supportedLDAPPolicies: MaxResultSetsPerConn
> |       supportedLDAPPolicies: MaxNotificationPerConn
> |       supportedLDAPPolicies: MaxValRange
> |       supportedLDAPPolicies: MaxValRangeTransitive
> |       supportedLDAPPolicies: ThreadMemoryLimit
> |       supportedLDAPPolicies: SystemMemoryLimitPercent
> |       supportedControl: 1.2.840.113556.1.4.319
> |       supportedControl: 1.2.840.113556.1.4.801
> |       supportedControl: 1.2.840.113556.1.4.473
> |       supportedControl: 1.2.840.113556.1.4.528
> |       supportedControl: 1.2.840.113556.1.4.417
> |       supportedControl: 1.2.840.113556.1.4.619
> |       supportedControl: 1.2.840.113556.1.4.841
> |       supportedControl: 1.2.840.113556.1.4.529
> |       supportedControl: 1.2.840.113556.1.4.805
> |       supportedControl: 1.2.840.113556.1.4.521
> |       supportedControl: 1.2.840.113556.1.4.970
> |       supportedControl: 1.2.840.113556.1.4.1338
> |       supportedControl: 1.2.840.113556.1.4.474
> |       supportedControl: 1.2.840.113556.1.4.1339
> |       supportedControl: 1.2.840.113556.1.4.1340
> |       supportedControl: 1.2.840.113556.1.4.1413
> |       supportedControl: 2.16.840.1.113730.3.4.9
> |       supportedControl: 2.16.840.1.113730.3.4.10
> |       supportedControl: 1.2.840.113556.1.4.1504
> |       supportedControl: 1.2.840.113556.1.4.1852
> |       supportedControl: 1.2.840.113556.1.4.802
> |       supportedControl: 1.2.840.113556.1.4.1907
> |       supportedControl: 1.2.840.113556.1.4.1948
> |       supportedControl: 1.2.840.113556.1.4.1974
> |       supportedControl: 1.2.840.113556.1.4.1341
> |       supportedControl: 1.2.840.113556.1.4.2026
> |       supportedControl: 1.2.840.113556.1.4.2064
> |       supportedControl: 1.2.840.113556.1.4.2065
> |       supportedControl: 1.2.840.113556.1.4.2066
> |       supportedControl: 1.2.840.113556.1.4.2090
> |       supportedControl: 1.2.840.113556.1.4.2205
> |       supportedControl: 1.2.840.113556.1.4.2204
> |       supportedControl: 1.2.840.113556.1.4.2206
> |       supportedControl: 1.2.840.113556.1.4.2211
> |       supportedControl: 1.2.840.113556.1.4.2239
> |       supportedControl: 1.2.840.113556.1.4.2255
> |       supportedControl: 1.2.840.113556.1.4.2256
> |       supportedControl: 1.2.840.113556.1.4.2309
> |       supportedControl: 1.2.840.113556.1.4.2330
> |       supportedControl: 1.2.840.113556.1.4.2354
> |       supportedCapabilities: 1.2.840.113556.1.4.800
> |       supportedCapabilities: 1.2.840.113556.1.4.1670
> |       supportedCapabilities: 1.2.840.113556.1.4.1791
> |       supportedCapabilities: 1.2.840.113556.1.4.1935
> |       supportedCapabilities: 1.2.840.113556.1.4.2080
> |       supportedCapabilities: 1.2.840.113556.1.4.2237
> |       subschemaSubentry: CN=Aggregate,CN=Schema,CN=Configuration,DC=INLANEFREIGHT,DC=LOCAL
> |       serverName: CN=ACADEMY-EA-DC01,CN=Servers,CN=Default-First-Site-Name,CN=Sites,CN=Configuration,DC=INLANEFREIGHT,DC=LOCAL
> |       schemaNamingContext: CN=Schema,CN=Configuration,DC=INLANEFREIGHT,DC=LOCAL
> |       namingContexts: DC=INLANEFREIGHT,DC=LOCAL
> |       namingContexts: CN=Configuration,DC=INLANEFREIGHT,DC=LOCAL
> |       namingContexts: CN=Schema,CN=Configuration,DC=INLANEFREIGHT,DC=LOCAL
> |       namingContexts: DC=DomainDnsZones,DC=INLANEFREIGHT,DC=LOCAL
> |       namingContexts: DC=ForestDnsZones,DC=INLANEFREIGHT,DC=LOCAL
> |       isSynchronized: TRUE
> |       highestCommittedUSN: 3326130
> |       dsServiceName: CN=NTDS Settings,CN=ACADEMY-EA-DC01,CN=Servers,CN=Default-First-Site-Name,CN=Sites,CN=Configuration,DC=INLANEFREIGHT,DC=LOCAL
> |       dnsHostName: ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL
> |       defaultNamingContext: DC=INLANEFREIGHT,DC=LOCAL
> |       currentTime: 20260730133354.0Z
> |_      configurationNamingContext: CN=Configuration,DC=INLANEFREIGHT,DC=LOCAL
> 445/tcp  open  microsoft-ds
> 464/tcp  open  kpasswd5
> 593/tcp  open  http-rpc-epmap
> 636/tcp  open  ldap
> | ldap-rootdse: 
> | LDAP Results
> |   <ROOT>
> |       domainFunctionality: 7
> |       forestFunctionality: 7
> |       domainControllerFunctionality: 7
> |       rootDomainNamingContext: DC=INLANEFREIGHT,DC=LOCAL
> |       ldapServiceName: INLANEFREIGHT.LOCAL:academy-ea-dc01$@INLANEFREIGHT.LOCAL
> |       isGlobalCatalogReady: TRUE
> |       supportedSASLMechanisms: GSSAPI
> |       supportedSASLMechanisms: GSS-SPNEGO
> |       supportedSASLMechanisms: EXTERNAL
> |       supportedSASLMechanisms: DIGEST-MD5
> |       supportedLDAPVersion: 3
> |       supportedLDAPVersion: 2
> |       supportedLDAPPolicies: MaxPoolThreads
> |       supportedLDAPPolicies: MaxPercentDirSyncRequests
> |       supportedLDAPPolicies: MaxDatagramRecv
> |       supportedLDAPPolicies: MaxReceiveBuffer
> |       supportedLDAPPolicies: InitRecvTimeout
> |       supportedLDAPPolicies: MaxConnections
> |       supportedLDAPPolicies: MaxConnIdleTime
> |       supportedLDAPPolicies: MaxPageSize
> |       supportedLDAPPolicies: MaxBatchReturnMessages
> |       supportedLDAPPolicies: MaxQueryDuration
> |       supportedLDAPPolicies: MaxDirSyncDuration
> |       supportedLDAPPolicies: MaxTempTableSize
> |       supportedLDAPPolicies: MaxResultSetSize
> |       supportedLDAPPolicies: MinResultSets
> |       supportedLDAPPolicies: MaxResultSetsPerConn
> |       supportedLDAPPolicies: MaxNotificationPerConn
> |       supportedLDAPPolicies: MaxValRange
> |       supportedLDAPPolicies: MaxValRangeTransitive
> |       supportedLDAPPolicies: ThreadMemoryLimit
> |       supportedLDAPPolicies: SystemMemoryLimitPercent
> |       supportedControl: 1.2.840.113556.1.4.319
> |       supportedControl: 1.2.840.113556.1.4.801
> |       supportedControl: 1.2.840.113556.1.4.473
> |       supportedControl: 1.2.840.113556.1.4.528
> |       supportedControl: 1.2.840.113556.1.4.417
> |       supportedControl: 1.2.840.113556.1.4.619
> |       supportedControl: 1.2.840.113556.1.4.841
> |       supportedControl: 1.2.840.113556.1.4.529
> |       supportedControl: 1.2.840.113556.1.4.805
> |       supportedControl: 1.2.840.113556.1.4.521
> |       supportedControl: 1.2.840.113556.1.4.970
> |       supportedControl: 1.2.840.113556.1.4.1338
> |       supportedControl: 1.2.840.113556.1.4.474
> |       supportedControl: 1.2.840.113556.1.4.1339
> |       supportedControl: 1.2.840.113556.1.4.1340
> |       supportedControl: 1.2.840.113556.1.4.1413
> |       supportedControl: 2.16.840.1.113730.3.4.9
> |       supportedControl: 2.16.840.1.113730.3.4.10
> |       supportedControl: 1.2.840.113556.1.4.1504
> |       supportedControl: 1.2.840.113556.1.4.1852
> |       supportedControl: 1.2.840.113556.1.4.802
> |       supportedControl: 1.2.840.113556.1.4.1907
> |       supportedControl: 1.2.840.113556.1.4.1948
> |       supportedControl: 1.2.840.113556.1.4.1974
> |       supportedControl: 1.2.840.113556.1.4.1341
> |       supportedControl: 1.2.840.113556.1.4.2026
> |       supportedControl: 1.2.840.113556.1.4.2064
> |       supportedControl: 1.2.840.113556.1.4.2065
> |       supportedControl: 1.2.840.113556.1.4.2066
> |       supportedControl: 1.2.840.113556.1.4.2090
> |       supportedControl: 1.2.840.113556.1.4.2205
> |       supportedControl: 1.2.840.113556.1.4.2204
> |       supportedControl: 1.2.840.113556.1.4.2206
> |       supportedControl: 1.2.840.113556.1.4.2211
> |       supportedControl: 1.2.840.113556.1.4.2239
> |       supportedControl: 1.2.840.113556.1.4.2255
> |       supportedControl: 1.2.840.113556.1.4.2256
> |       supportedControl: 1.2.840.113556.1.4.2309
> |       supportedControl: 1.2.840.113556.1.4.2330
> |       supportedControl: 1.2.840.113556.1.4.2354
> |       supportedCapabilities: 1.2.840.113556.1.4.800
> |       supportedCapabilities: 1.2.840.113556.1.4.1670
> |       supportedCapabilities: 1.2.840.113556.1.4.1791
> |       supportedCapabilities: 1.2.840.113556.1.4.1935
> |       supportedCapabilities: 1.2.840.113556.1.4.2080
> |       supportedCapabilities: 1.2.840.113556.1.4.2237
> |       subschemaSubentry: CN=Aggregate,CN=Schema,CN=Configuration,DC=INLANEFREIGHT,DC=LOCAL
> |       serverName: CN=ACADEMY-EA-DC01,CN=Servers,CN=Default-First-Site-Name,CN=Sites,CN=Configuration,DC=INLANEFREIGHT,DC=LOCAL
> |       schemaNamingContext: CN=Schema,CN=Configuration,DC=INLANEFREIGHT,DC=LOCAL
> |       namingContexts: DC=INLANEFREIGHT,DC=LOCAL
> |       namingContexts: CN=Configuration,DC=INLANEFREIGHT,DC=LOCAL
> |       namingContexts: CN=Schema,CN=Configuration,DC=INLANEFREIGHT,DC=LOCAL
> |       namingContexts: DC=DomainDnsZones,DC=INLANEFREIGHT,DC=LOCAL
> |       namingContexts: DC=ForestDnsZones,DC=INLANEFREIGHT,DC=LOCAL
> |       isSynchronized: TRUE
> |       highestCommittedUSN: 3326130
> |       dsServiceName: CN=NTDS Settings,CN=ACADEMY-EA-DC01,CN=Servers,CN=Default-First-Site-Name,CN=Sites,CN=Configuration,DC=INLANEFREIGHT,DC=LOCAL
> |       dnsHostName: ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL
> |       defaultNamingContext: DC=INLANEFREIGHT,DC=LOCAL
> |       currentTime: 20260730133354.0Z
> |_      configurationNamingContext: CN=Configuration,DC=INLANEFREIGHT,DC=LOCAL
> 3268/tcp open  globalcatLDAP
> 3269/tcp open  globalcatLDAPssl
> 3389/tcp open  ms-wbt-server
> MAC Address: A2:DE:AD:07:37:60 (Unknown)
> Service Info: Host: ACADEMY-EA-DC01; OS: Windows
> 
> Nmap scan report for 172.16.5.130
> Host is up (0.018s latency).
> Not shown: 992 closed tcp ports (reset)
> PORT      STATE SERVICE
> 80/tcp    open  http
> 135/tcp   open  msrpc
> 139/tcp   open  netbios-ssn
> 445/tcp   open  microsoft-ds
> 808/tcp   open  ccproxy-http
> 1433/tcp  open  ms-sql-s
> 3389/tcp  open  ms-wbt-server
> 16001/tcp open  fmsascon
> MAC Address: A2:DE:AD:86:80:B7 (Unknown)
> 
> Nmap scan report for 172.16.5.225
> Host is up (0.019s latency).
> Not shown: 998 closed tcp ports (reset)
> PORT     STATE SERVICE
> 22/tcp   open  ssh
> 3389/tcp open  ms-wbt-server
> 
> Nmap done: 3 IP addresses (3 hosts up) scanned in 29.10 seconds
> ```
> - From the scanning results, only `172.16.5.5` is a Domain Controller (LDAP ports `389`, `636` and Kerberos port `88` are open, `ldap-roodse` gives a lot of information. 



## Authenticated enumeration (low-privileged) — from Linux

### Impacket

- [`psexec.py`](https://github.com/fortra/impacket/blob/master/examples/psexec.py): Execute interactive `cmb.exe` terminal session via SMB and Windows Service Creation (requires admin privileges):

```bash
impacket-psexec example.com/jdoe:'passwd123'@10.10.11.5
```

- [`wmiexec.py`](https://github.com/fortra/impacket/blob/master/examples/wmiexec.py): Execute semi-interactive shell via Windows Management Instrumentation (WMI) without service creation:

```bash
impacket-wmiexec example.com/jdoe:'passwd123'@10.10.11.5
```

- [`GetNPUsers.py`](https://github.com/fortra/impacket/blob/master/examples/GetNPUsers.py): Request AS-REP encrypted Kerberos tickets for users configured with `DONT_REQ_PREAUTH` (AS-REP Roasting):


```bash
impacket-GetNPUsers example.com/jdoe:'passwd123' -dc-ip 10.10.11.5 -request -format hashcat -outputfile asprep_hashes.txt
```

- [`GetUserSPN.py`](https://github.com/fortra/impacket/blob/master/examples/GetUserSPNs.py): Enumerate domain accounts with configured SPNs (Service Principal Names) and request TGS tickets (Kerberoasting):

```bash
impacket-GetUserSPNs example.com/jdoe:'passwd123' -dc-ip 10.10.11.5 -request -outputfile kerberoast_hashes.txt
```


- [`lookupsid.py`](https://github.com/fortra/impacket/blob/master/examples/lookupsid.py): Brute-force and map Domain SIDs to usernames and group objects via SAMBA/LSA RPC interface:

```bash
impacket-lookupsid example.com/jdoe:'passwd123'@10.10.11.5
```

| Script           | Description                                                                   |
| ---------------- | ----------------------------------------------------------------------------- |
| `psexec.py`      | PSService-based remote command execution (`SYSTEM` shell).                    |
| `wmiexec.py`     | Command execution via WMI/DCOM interfaces (`CMD`/`PowerShell`).               |
| `smbexec.py`     | Native SMB service execution interface (no binaries are dropped to disk).     |
| `atexec.py`      | Command execution via Task Scheduler service (`atsvc`).                       |
| `GetNPUsers.py`  | Query accounts with Kerberos pre-authentication disabled for AS-REP roasting. |
| `GetUserSPNs.py` | Query service principal accounts and request Kerberos TGS tickets.            |
| `lookupsid.py`   | SID brute-forcing and resolution over RPC/LSA pipes.                          |


### `net` commands (native Windows CLI)

- Retrieve domain information and current logged-in domain controller:

```powershell
net config workstation
```

- Query the domain password policy and lockout threshold:

```powershell
net accounts /domain
```

- List all users registered in the domain:

```powershell
net user /domain
```

- Retrieve detailed account information for a specific domain user:

```powershell
net user <username> /domain
```

- List all domain groups:

```powershell
net group /domain
```

- List members of a specific domain group:

```powershell
net group "Domain Admins" /domain
```

| Command                | Description                                             |
| ---------------------- | ------------------------------------------------------- |
| `net accounts /domain` | Retrieve password and lockout policies for the domain.  |
| `net user /domain`     | List or query domain user accounts.                     |
| `net group /domain`    | List or query domain group objects.                     |
| `net localgroup`       | List local security groups on the host machine.         |
| `net view /domain`     | Enumerate computers and shared resources in the domain. |

### Active Directory PowerShell module

>[!tip]+
> - Check if the Active Directory PowerShell module is installed and available in the current session:
> ```powershell
> Get-Module -ListAvailable ActiveDirectory
> ```
> 
> - Import the Active Directory PowerShell module into the current session:
> 
> ```powershell
> Import-Module ActiveDirectory
> ```

- Retrieve core information about the current domain, including Domain SID, domain controllers, and infrastructure roles:

```powershell
Get-ADDomain
```

- Retrieve the domain password policy (e.g., lockout thresholds, password complexity rules):

```powershell
Get-ADDefaultDomainPasswordPolicy
```

- Enumerate fine-grained password policies (FGPP) defined in the domain:

```powershell
Get-ADFineGrainedPasswordPolicy -Filter *
```

- List all user accounts in the domain:

```powershell
Get-ADUser -Filter * -Properties *
```

- Enumerate users configured with Kerberos SPNs (Service Principal Names) — for [[Kerberoasting]]:

```powershell
Get-ADUser -Filter {ServicePrincipalName -ne "$null"} -Properties ServicePrincipalName
```

- Enumerate users configured with Kerberos pre-authentication disabled (`DONT_REQ_PREAUTH`) — for [[AS-REP roasting]]:

```powershell
Get-ADUser -Filter {DoesNotRequirePreAuth -eq $True} -Properties DoesNotRequirePreAuth
```

- List all domain groups:

```powershell
Get-ADGroup -Filter * | Select-Object Name
```

- Query detailed properties and member lists for a specific group (e.g., `Backup Operators`):

```powershell
Get-ADGroup -Identity "Backup Operators" -Properties *
```

- List all computer objects joined to the domain along with their operating systems:

```powershell
Get-ADComputer -Filter * -Properties OperatingSystem, OperatingSystemVersion
```

- Enumerate all domain trust relationships:

```powershell
Get-ADTrust -Filter *
```

| Command                    | Description                                                     |
| -------------------------- | --------------------------------------------------------------- |
| `Get-ADDomain`             | Retrieve domain metadata, forest root, and SIDs.                |
| `Get-ADUser`               | Query user accounts and associated Active Directory attributes. |
| `Get-ADGroup`              | Query group objects and group memberships.                      |
| `Get-ADGroupMember`        | List members of a designated AD group.                          |
| `Get-ADComputer`           | Query computer objects joined to the domain.                    |
| `Get-ADTrust`              | Enumerate directional domain and forest trust relationships.    |
| `Get-ADOrganizationalUnit` | Enumerate OUs and container structures across the domain.       |
| `Get-ADObject`             | Query arbitrary AD objects using explicit LDAP filters.         |

### PowerView

- Retrieve fundamental domain details and Domain SID:

```
Get-Domain
```

- Retrieve domain password policy settings:

```powershell
Get-DomainPolicyData
```

- Enumerate Domain Controllers:

```powershell
Get-DomainController
```

- List domain user accounts and export specific attributes:

```powershell
Get-DomainUser -Properties samaccountname,description,memberof
```

- Search account description fields for sensitive keywords or hardcoded passwords:

```powershell
Get-DomainUser -LDAPFilter "(description=*pass*)" | Select-Object samaccountname,description
```

- Enumerate domain user accounts configured with Service Principal Names ([[Kerberoasting]]):

```
Get-DomainUser -SPN
```

- Enumerate domain user accounts configured with pre-authentication disabled ([[AS-REP roasting]]):

```powershell
Get-DomainUser -PreauthNotRequired
```

- List all domain groups or filter for specific administrative groups:

```powershell
Get-DomainGroup -Identity "Domain Admins"
```

- Recursively expand group members to reveal nested accounts:

```powershell
Get-DomainGroupMember -Identity "Domain Admins" -Recurse
```

- List computer objects in the domain:

```powershell
Get-DomainComputer -Properties dnshostname,operatingsystem
```

- Enumerate local administrator accounts across domain computers (RPC):

```powershell
Get-DomainLocalGroup -ComputerName <ComputerName> -API
```

- Map domain trust relationships across forests or child domains:

```powershell
Get-DomainTrust
```

- Enumerate GPOs (Group Policy Objects) and identify linked OUs (Organizational Units):

```powershell
Get-DomainGPO
```

- Find explicit ACEs (Access Control Entries) where a specified user or group holds modifying rights:

```powershell
Get-DomainObjectAcl -Identity "Domain Admins" -ResolveGUIDs
```

- Enumerate accounts configured for `Unconstrained`, `Constrained`, or `Resource-Based Constrained` delegation:

```powershell
Get-DomainUser -Unconstrained
Get-DomainUser -AllowDelegation
Get-DomainComputer -Unconstrained
```

---

- Basic information:

| Command                     | Description                                                                     |
| --------------------------- | ------------------------------------------------------------------------------- |
| `Get-Domain`                | Retrieve core domain information.                                               |
| `Get-DomainUser`            | Query user objects and attributes.                                              |
| `Get-DomainGroup`           | Query domain groups and properties.                                             |
| `Get-DomainComputer`        | Query domain computer objects.                                                  |
| `Get-DomainOU`              | Query domain OU (Organizational Unit) objects.                                  |
| `Get-DomainGPO`             | Enumerate GPOs (Group Policy Objects).                                          |
| `Get-DomainTrust`           | Enumerate domain and forest trusts.                                             |
| `Get-DomainObjectAcl`       | Query ACLs (Access Control Lists) for AD objects.                               |
| `Find-InterestingDomainAcl` | Search for anomalous / misconfigured ACLs across the domain.                    |
| `Get-DomainForeignUser`     | Find users from external domains holding group memberships in the local domain. |
| `Get-DomainGroupMember`     | List members of a specific domain group.                                        |
| `Get-DomainFileServer`      | List servers that are likely functioning as file servers.                       |
| `Get-DomainDFSShare`        | List all distributed file systems for the current (or specified) domain.        |

- GPOs:

| Command            | Description                                    |
| ------------------ | ---------------------------------------------- |
| `Get-DomainGPO`    | Query GPO objects.                             |
| `Get-DomainPolicy` | Return the default domain policy or DC policy. |

- Local enumeration:

| Command                   | Description                                                                               |
| ------------------------- | ----------------------------------------------------------------------------------------- |
| `Get-NetLocalGroup`       | List local groups on the current (or specified) machine.                                  |
| `Get-NetLocalGroupMember` | List members of a specific local group.                                                   |
| `Get-NetShare`            | List open shares on the current (or specified) machine.                                   |
| `Get-NetSession`          | Return session information for the current (or specified) machine.                        |
| `Test-AdminAccess`        | Test if the current user has administrative access on the current (or specified) machine. |

- Meta:

| Command                           | **Description**                                                                               |
| --------------------------------- | ----------------------------------------------------------------------------------------- |
| `Find-DomainUserLocation`         | Find machines where specific users are logged-in.                                         |
| `Find-DomainShare`                | Find reachable SMB shares.                                                                |
| `Find-InterestingDomainShareFile` | Search for files matching a specific criteria on readable shares in the domain.           |
| `Find-LocalAdminAccess`           | Find machines on the local domain where the current user has local administrative access. |

- Domain trust:

| Command                        | Description                                                                      |
| ------------------------------ | -------------------------------------------------------------------------------- |
| `Get-DomainTrust`              | List domain trusts for the current (or specified) domain.                        |
| `Get-ForestTrust`              | Returns all forest trusts for the current (or specified) forest.                 |
| `Get-DomainForeignUser`        | Enumerate users who are members of the groups outside the current domain.        |
| `Get-DomainForeignGroupMember` | Enumerate groups with users outside the group domain, return each foreign member |
| `Get-DomainTrustMapping`       | Enumerate all trusts for the current domain + any others domains discovered.     |

### Sysinternals suite (`AdExplorer` & `PsTools`)

- Execute `AdExplorer` with low-privileged credentials to interactively browse, search, and snapshot the Active Directory tree:

```powershell
AdExplorer.exe -connect domain.local -user jdoe -password passwd123
```

- Query user accounts and attributes via `PsUser`:

```powershell
psuser.exe \\DC01 jdoe
```

- List active logon sessions on a remote host using `PsLoggedOn`:

```powershell
psloggedon.exe \\<target_host>
```

| Utility          | Description                                                                |
| ---------------- | -------------------------------------------------------------------------- |
| `AdExplorer.exe` | Graphical Active Directory viewer and offline database snapshot tool.      |
| `AdInsight.exe`  | Real-time LDAP monitoring and troubleshooting tool for AD applications.    |
| `PsLoggedOn.exe` | Enumerate locally logged-on users and active network resource connections. |
| `PsUser.exe`     | Display information about local or domain user accounts.                   |

## `SharpHound` / `BloodHound`

- Execute `SharpHound.exe` to collect all domain graph data and compress output into a ZIP file for BloodHound import:


```powershell
SharpHound.exe --CollectionMethods All --ZipFileName collection.zip
```

- Execute session enumeration sweep to locate logged-in privileged users across target subnets:

```powershell
SharpHound.exe --CollectionMethods Session --Stealth
```

- `SharpHound` flags:

|**Flag**|**Description**|
|---|---|
|`--CollectionMethods`|Specify collection routines (`All`, `Group`, `LocalAdmin`, `Session`, `ACL`, `Trusts`, `LoggedOn`).|
|`--Domain`|Specify target domain name if different from host context.|
|`--Stealth`|Stealthy session enumeration using single-threaded requests.|
|`--ZipFileName`|Custom filename for output ZIP archive.|
|`--ExcludeDCs`|Exclude Domain Controllers from session enumeration enumeration.|

## References and further reading

- [`Active Directory ENumeration: RPCClient — Hacking Articles`](https://www.hackingarticles.in/active-directory-enumeration-rpcclient/)















# drafts

## Unauthenticated AD enumeration

- The following enumeration techniques are relevant when you don't have any credentials in the domain and want to gain an initial foothold.
- The information you can get without any authentication is limited, but is often enough to find a way in. 

### Enumerating DNS `SRV` records



## Enumerating users

### `Kerbrute`

- [`Kerbrute`](https://github.com/ropnop/kerbrute) can be used to quickly brute-force active directory accounts through Kerberos pre-authentication — without leaving much noise. It takes advantage of the fact that Kerberos pre-authentication failures often do not trigger any logs or alerts.

>[!note] See [[Kerberos#1. AS exchange (KRB_AS_REQ / KRB_AS_REP)]].

```bash
kerbrute userenum -d EXAMPLE.COM --dc 10.10.11.5 usernames.txt -o valid_ad_users
```


