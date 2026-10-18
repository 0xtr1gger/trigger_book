---
created: 2026-08-12
updated: 2026-10-11
tags:
  - AD
  - AD_attacks
  - Windows
  - enumeration
status: substantial
---

## External AD & Windows enumeration

>[!abstract]+ **Scope**: External enumeration of an Active Directory domain and Windows machines **without any authenticated access or known usernames**, from a Linux machine.

## Checklist

>[!important] Main objective: **enumerate information available without credentials**. 

- [ ] Confirm the target IP address/range.
- [ ] Perform passive reconnaissance (applicable only when connected to the target LAN).
- [ ] Enumerate live hosts. 
- [ ] Perform port scanning and identify exposed services. 
- [ ] Gather basic information about the domain:
	- [ ] Hostname
	- [ ] Domain name
	- [ ] FQDN (Fully-Qualified Domain Name)
	- [ ] NetBIOS name
	- [ ] NetBIOS domain
	- [ ] Base DN
	- [ ] DNS server
	- [ ] Time 
- [ ] Identify Domain Controllers
- [ ] Perform DNS enumeration
	- [ ] Query `SRV` records
- [ ] Test for anonymous access / null sessions
	- [ ] Test for LDAP anonymous bind
	- [ ] Test for SMB null sessions
	- [ ] Test for MS-RPC anonymous access
- [ ] Scan other exposed Windows services that can disclose NTLM/domain metadata

>[!tip]+
>- For username enumeration and password spraying, see [[Username enumeration in AD]] and [[Password spraying in AD]].
>- For enumeration with credentials, see [[🛠️ Authenticated AD & Windows enumeration]].

### Domain names, hostnames, and FQDNs

Different identifiers discovered during enumeration serve different purposes:

- **Hostname** — the local name assigned to a single machine (e.g., `DC01`); primary method of network identification in AD, serve as SPNs (Service Principal Names) for [[Kerberos]] authentication.

- **DNS domain name** — the DNS name of an AD domain (e.g., `example.com`).

- **FQDN (Fully-Qualified Domain Name)** — the complete DNS name of a host (e.g., `DC01.example.com`).

>[!note] Kerberos service tickets are requested for SPNs, which normally contain hostnames rather than IP addresses, and that's why correct forward and reverse name resolution matter for Kerberos authentication. 
>- If an application can't use Kerberos, it may fall back to [[🛠️ NTLM]] (but this depends on the client, protocol, and policy).

- **Kerberos realm** — the [[Kerberos]] administrative namespace; in AD, it normally corresponds to the DNS domain and is conventionally written in uppercase (e.g., `EXAMPLE.COM`).

---

- **NetBIOS computer name** — the legacy fallback Windows name, often the same as the hostname (e.g., `DC01`); NetBIOS name has a 16-byte limit, 15 usable characters.

- **NetBIOS domain name** — the pre-Windows 2000 flat domain name used by legacy Windows interfaces and commonly included in NTLM metadata (e.g., `EXAMPLE`).

---

- **DN (Distinguished Name)** — the LDAP path of an object (`CN=Jane,CN=Users,DC=example,DC=com`).

- **Base DN (domain naming context)** — the DN at the root of a domain partition (`DC=example,DC=com`).

>[!note] LDAP directory searches normally require a search base; the only exception is RootDSE queries, which specify an empty base DN. See [[Querying LDAP]].

- **Computer account** — the AD object representing a computer; its `sAMAccountName` normally ends in `$` (e.g., `DC01$`).

- **SPN (Service Principal Name)** — a directory attribute that identifies a service instance (e.g., `HOST/dc01.example.com`, `MSSQLSvc/sql01.example.com:1433`).
## Passive reconnaissance

> [!info] Only applicable when you're connected to the target internal network (same Layer-2 segment).

- Passive reconnaissance helps you learn information about the target environment from network network traffic — without actively querying AD or scanning hosts. 

- The objective is identify:
	- IPv4 and IPv6 addresses of active hosts
	- Hostnames, domain names, and Kerberos realms
	- MAC addresses and device vendors
	- DNS servers 
	- DHCP servers
	- Default gateways
	- Possible Domain Controllers and Global Catalog servers
	- 
- Also note:
	- Broadcast traffic
	- [LLMNR](https://en.wikipedia.org/wiki/Link-Local_Multicast_Name_Resolution), [NetBIOS](https://en.wikipedia.org/wiki/NetBIOS), and [mDNS](https://en.wikipedia.org/wiki/Multicast_DNS) queries
	- [[Kerberos]] authentication traffic (`AS-REQ`/`AS-REP`)
	- [[🛠️ NTLM]] authentication traffic (challenge-response exchanges)
	- DNS and DHCP queries
	- SMB and LDAP activity 
	- DHCP traffic
	- Naming conventions and possible usernames visible in protocol metadata

### Packet capture

- For traffic capture and analysis, you can use tools like:
    - Wireshark
    - `tcpdump`
    - `Responder` (`-A` for analysis)
    - `tshark`

> [!note] See [[Wireshark]] and [[tcpdump]].

- Listen on `eth0` and capture traffic for offline analysis:

```bash
sudo tcpdump -i eth0 -w capture.pcap
```

- Read a capture with `tshark`:

```bash
tshark -r capture.pcap
```

>[!example]-
> ```bash
> tshark -r capture.pcap
> ```
> 
> ```bash
>     1   0.000000 a2:de:ad:07:37:60 \u2192 Broadcast    ARP 60 Who has 172.16.5.1? Tell 172.16.5.5
>     2   0.037531 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>     3   0.192677 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>     4   0.364586 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>     5   0.364687 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>     6   0.395871 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>     7   0.397501 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>     8   0.489639 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>     9   0.536286 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>    10   0.603845 a2:de:ad:07:37:60 \u2192 Broadcast    ARP 60 Who has 172.16.5.1? Tell 172.16.5.5
>    11   0.785904 fe80::ffff:ffff:ffff:ffff \u2192 ff02::1      ICMPv6 90 Multicast Listener Query
>    12   0.785904      0.0.0.0 \u2192 224.0.0.1    IGMPv3 60 Membership Query, general
>    13   0.786348 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>    14   0.786417 fe80::ffff:ffff:ffff:ffff \u2192 ff02::1      ICMPv6 90 Multicast Listener Query
>    15   0.786418      0.0.0.0 \u2192 224.0.0.1    IGMPv3 60 Membership Query, general
>    16   0.786635      0.0.0.0 \u2192 224.0.0.1    IGMPv3 60 Membership Query, general
>    17   0.786650 fe80::ffff:ffff:ffff:ffff \u2192 ff02::1      ICMPv6 90 Multicast Listener Query
>    18   0.843230 fe80::32e6:baa0:e3aa:25da \u2192 ff02::16     ICMPv6 90 Multicast Listener Report Message v2
>    19   0.958322 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>    20   1.130117 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>    21   1.130190 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>    22   1.161356 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>    23   1.255122 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>    24   1.551989 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>    25   1.603885 a2:de:ad:07:37:60 \u2192 Broadcast    ARP 60 Who has 172.16.5.1? Tell 172.16.5.5
>    26   1.926998 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>    27   2.177669 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>    28   2.303907 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>    29   2.708819 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>    30   2.724971 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>    31   2.912322 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>    32   2.912812 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>    33   2.926815 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>    34   3.037162 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>    35   3.067748 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>    36   3.458316 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>    37   3.473863 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>    38   3.661487 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>    39   3.661553 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>    40   3.692666 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>    41   3.708890 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>    42   3.801980 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>    43   3.833232 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>    44   4.198208 a2:de:ad:07:37:60 \u2192 Broadcast    ARP 60 Who has 172.16.5.1? Tell 172.16.5.5
>    45   4.223843 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>    46   4.223946 172.16.5.130 \u2192 172.16.5.255 NBNS 92 Name query NB ACADEMY-EA-WEB0<00>
>    47   4.254951 a2:de:ad:86:80:b7 \u2192 Broadcast    ARP 60 Who has 172.16.5.1? Tell 172.16.5.130
> # ...
> ```

- `Responder` can operate in analysis mode (`-A`) to passively listen for traffic without poisoning requests:

```bash
sudo responder -I eth0 -A
```

>[!example]-
> ```bash
> sudo responder -I ens224 -A
> ```
> 
> ```bash
> 
>                                          __
> 
>   .----.-----.-----.-----.-----.-----.--|  |.-----.----.
> 
>   |   _|  -__|__ --|  _  |  _  |     |  _  ||  -__|   _|
> 
>   |__| |_____|_____|   __|_____|__|__|_____||_____|__|
> 
>                    |__|
> 
> 
>            NBT-NS, LLMNR & MDNS Responder 3.0.6.0
> 
>   Author: Laurent Gaffie (laurent.gaffie@gmail.com)
>   To kill this script hit CTRL-C
> 
> [+] Poisoners:
>     LLMNR                      [ON]
>     NBT-NS                     [ON]
>     DNS/MDNS                   [ON]
> 
> [+] Servers:
>     HTTP server                [ON]
>     HTTPS server               [ON]
>     WPAD proxy                 [OFF]
>     Auth proxy                 [OFF]
>     SMB server                 [ON]
>     Kerberos server            [ON]
>     SQL server                 [ON]
>     FTP server                 [ON]
>     IMAP server                [ON]
>     POP3 server                [ON]
>     SMTP server                [ON]
>     DNS server                 [ON]
>     LDAP server                [ON]
>     RDP server                 [ON]
>     DCE-RPC server             [ON]
>     WinRM server               [ON]
> 
> [+] HTTP Options:
>     Always serving EXE         [OFF]
>     Serving EXE                [OFF]
>     Serving HTML               [OFF]
>     Upstream Proxy             [OFF]
> 
> [+] Poisoning Options:
>     Analyze Mode               [ON]
>     Force WPAD auth            [OFF]
>     Force Basic Auth           [OFF]
>     Force LM downgrade         [OFF]
>     Fingerprint hosts          [OFF]
> 
> [+] Generic Options:
>     Responder NIC              [ens224]
>     Responder IP               [172.16.5.225]
>     Challenge set              [random]
>     Don't Respond To Names     ['ISATAP']
> 
> [+] Current Session Variables:
>     Responder Machine Name     [WIN-AEF8ASW35SU]
>     Responder Domain Name      [74SQ.LOCAL]
>     Responder DCE-RPC Port     [47137]
> [i] Responder is in analyze mode. No NBT-NS, LLMNR, MDNS requests will be poisoned.
> [Analyze mode: ICMP] You can ICMP Redirect on this network.
> [Analyze mode: ICMP] This workstation (172.16.5.225) is not on the same subnet than the DNS server (1.1.1.1).
> [Analyze mode: ICMP] Use `python tools/Icmp-Redirect.py` for more details.
> [Analyze mode: ICMP] You can ICMP Redirect on this network.
> [Analyze mode: ICMP] This workstation (172.16.5.225) is not on the same subnet than the DNS server (8.8.8.8).
> [Analyze mode: ICMP] Use `python tools/Icmp-Redirect.py` for more details.
> [!] Error starting TCP server on port 3389, check permissions or other servers running.
> 
> [+] Listening for events...
> 
> [Analyze mode: NBT-NS] Request by 172.16.5.130 for ACADEMY-EA-WEB0, ignoring
> [Analyze mode: NBT-NS] Request by 172.16.5.130 for ACADEMY-EA-WEB0, ignoring
> [Analyze mode: NBT-NS] Request by 172.16.5.130 for ACADEMY-EA-WEB0, ignoring
> [Analyze mode: LLMNR] Request by 172.16.5.130 for academy-ea-web0, ignoring
> [Analyze mode: MDNS] Request by 172.16.5.130 for academy-ea-web0.local, ignoring
> [Analyze mode: MDNS] Request by 172.16.5.130 for academy-ea-web0.local, ignoring
> [Analyze mode: LLMNR] Request by 172.16.5.130 for academy-ea-web0, ignoring
> [Analyze mode: NBT-NS] Request by 172.16.5.130 for ACADEMY-EA-WEB0, ignoring
> [Analyze mode: LLMNR] Request by 172.16.5.130 for academy-ea-web0, ignoring
> [Analyze mode: NBT-NS] Request by 172.16.5.130 for ACADEMY-EA-WEB0, ignoring
> [Analyze mode: MDNS] Request by 172.16.5.130 for academy-ea-web0.local, ignoring
> [Analyze mode: LLMNR] Request by 172.16.5.130 for academy-ea-web0, ignoring
> [Analyze mode: NBT-NS] Request by 172.16.5.130 for ACADEMY-EA-WEB0, ignoring
> [Analyze mode: NBT-NS] Request by 172.16.5.130 for ACADEMY-EA-WEB0, ignoring
> [Analyze mode: MDNS] Request by 172.16.5.130 for academy-ea-web0.local, ignoring
> [Analyze mode: NBT-NS] Request by 172.16.5.130 for ACADEMY-EA-WEB0, ignoring
> [Analyze mode: MDNS] Request by 172.16.5.130 for academy-ea-web0.local, ignoring[Analyze mode: NBT-NS] Request by 172.16.5.130 for ACADEMY-EA-WEB0, ignoring
> [Analyze mode: LLMNR] Request by 172.16.5.130 for academy-ea-web0, ignoring
> [Analyze mode: LLMNR] Request by 172.16.5.130 for academy-ea-web0, ignoring
> ```
## Host discovery
### Ping sweeps

- A **ping sweep** sends ICMP echo requests to a range of IP addresses to identify which hosts are live.

- [`fping`](https://github.com/schweikert/fping) can send ICMP probes to multiple hosts in parallel — far faster than traditional `ping` on subnets:

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

- Useful `fping` options:

| Option             | Description                                                                             |
| ------------------ | --------------------------------------------------------------------------------------- |
| `-a`, `--alive`    | Show live targets.                                                                      |
| `-s`, `--stats`    | Print final stats.                                                                      |
| `-q`, `--quiet`    | Quiet mode (don't show per-target/per-ping results).                                    |
| `-n`, `--name`     | Show targets by hostnames (perform reverse DNS lookup for target IP addresses).         |
| `-A`, `--addr`     | Show targets by address.                                                                |
| `-g`, `--generate` | Auto-generate a list of targets from a CIDR range (works only if no `-f` is specified). |
| `-f`, `--file`     | Read targets from a file (`-` means `stdin`).                                           |

### Nmap host discovery

- Nmap host discovery (`-sn`):

```bash
sudo nmap -sn 10.10.11.0/24 -oA nmap/ping_sweep
```

> [!note]+ Nmap `-sn` performs host discovery only (no port scan)
> 
> - When run with root/administrator privileges, Nmap normally uses ICMP Echo and Timestamp requests plus TCP `SYN` to port `443` and TCP `ACK` to port `80`. On a local Ethernet network, it uses ARP instead.
> - On Unix-like systems without root privileges, Nmap uses TCP `connect()` (`-sT`) probes to ports `80` and `443`.
> 
> See [[Nmap host discovery]].

- On routed networks where filtering might be an issue, add TCP `SYN` (`-PS`) and TCP `ACK` (`-PA`) probes to ports commonly reachable on Windows systems:

```bash
sudo nmap -sn 10.10.11.0/24 -PS 445,3389,5985,88 -PA 445,3389 -oA nmap/host_discovery
```

| Option | Description          |
| ------ | -------------------- |
| `-sn`  | Ping scan (default). |
| `-PS`  | TCP `SYN` ping scan. |
| `-PA`  | TCP `ACK` ping scan. |

> [!note] Windows firewalls drop ICMP requests by default.

>[!note] See [[Nmap host discovery]].
### ARP scans

> [!info] Only applicable when you're connected to the target internal network.

- When available, ARP is by far the most reliable method of host discovery (since ARP is what hosts use to discover each other's MAC addresses for normal network communication). You can use [`arp-scan`](https://github.com/royhills/arp-scan).

- Generate addresses from interface configuration:

```bash
sudo arp-scan -I eth0 --localnet
```

- Specify the target network explicitly: 

```bash
sudo arp-scan -I eth0 10.10.11.0/24
```

| Option              | Description                                      |
| ------------------- | ------------------------------------------------ |
| `-l`, `--localnet`  | Generate addresses from interface configuration. |
| `-I`, `--interface` | Specify network interface to use.                |

> [!note] [`fping`](https://github.com/schweikert/fping) · [`arp-scan`](https://github.com/royhills/arp-scan) · [`Nmap host discovery`](https://nmap.org/book/man-host-discovery.html)

## Port scanning and service discovery

- Scan the top 1,000 most common TCP ports and perform version detection:

```bash
sudo nmap -Pn -sV -sC -n 10.10.11.5 -oA nmap/tcp_ports
```

- Scan common Windows / Active Directory ports and perform version detection:

```bash
sudo nmap -Pn -sV -sC -p 53,88,135,139,389,445,464,593,636,1433,3268,3269,3389,5985,5986,9389 10.10.11.5 -oA nmap/windows_ad_ports
```

- Scan all 65,535 TCP ports and perform version detection:

```bash
sudo nmap -Pn -sV -sC -p- 10.10.11.5 -oA nmap/all_tcp_ports
```

>[!note] A full TCP scan may take a lot of time, so it's best to perform it in parallel with other enumeration.

- Scan common AD UDP ports (`53`, `88`, `123`, `137`, `138`, `389`):

```bash
sudo nmap -Pn -sU -sV -sC -p 53,88,123,137,138,389,500,1434,4500 10.10.11.5 -oA nmap/common_udp_ports
```

>[!note]+ `53` (DNS) · `88` (Kerberos) · `137`/`138` (NetBIOS) · `389` (CLDAP) · `123` (NTP) · `161` (SNMP) · `1434` (SQL Browser) · `500`/`4500` (IKE)
>- NTP (`123`) is useful for time and clock-skew checks.
>- SNMP (`161`), SQL Browser (`1434`) and IKE (`500`/`4500`) are not AD services, but when exposed they can reveal hostnames, OS details, and other useful information.

>[!note] See [[Nmap port scanning]] and [[Nmap version detection]].

| Port          | Protocol / service       | Information / follow-up                                                                                                   |
| ------------- | ------------------------ | ------------------------------------------------------------------------------------------------------------------------- |
| `53`          | DNS                      | Domain infrastructure, SRV records, `PTR` records, `AXFR` (zone transfers).                                               |
| `88`          | Kerberos                 | Identifies KDC/DC; used for username enumeration, [[AS-REP roasting]].                                                    |
| `135`         | MSRPC                    | RPC endpoint mapper, RPC enumeration.                                                                                     |
| `137`/`138`   | NetBIOS-NS / NetBIOS-DGM | Hostname and domain information.                                                                                          |
| `139`/`445`   | NetBIOS-SSN / SMB        | Host information, shares, users, signing, null sessions.                                                                  |
| `389`/`636`   | LDAP / LDAPS             | RootDSE, directory queries, anonymous access.                                                                             |
| `464`         | Kpasswd                  | Kerberos password change service; identifies DCs.                                                                         |
| `593`         | RPC over HTTP            | RPC service exposure.                                                                                                     |
| `1433`        | MSSQL                    | MSSQL enumeration and authentication.                                                                                     |
| `3268`/`3269` | Global Catalog / GC SSL  | Forest-wide LDAP queries.                                                                                                 |
| `3389`        | RDP                      | Host/domain information and remote access.                                                                                |
| `5985`/`5986` | WinRM (HTTP / HTTPS)     | Remote management interface; password spraying target.                                                                    |
| `9389`        | AD Web Services (ADWS)   | Active Directory Web Services port (indicates DC running Windows Server 2008 R2+); used for authenticated AD enumeration. |

>[!note] [`Nmap port scanning — Nmap`](https://nmap.org/book/man-port-scanning-techniques.html)

## Gathering initial information about the domain 

- The objective is to determine as much of the following as possible:
	- Host IPv4/IPv6 addresses
	- Hostname
	- Host FQDN
	- AD DNS domain and Kerberos realm
	- NetBIOS computer name
	- NetBIOS domain name
	- Base DN (Distinguished Name) for LDAP
	- Forest root domain
	- Forest root naming context
	- Likely Domain Controllers
	- Global Catalog status
	- AD site name
	- OS family and build
	- SMB dialects and signing requirement
	- Target time and clock skew
	- TLS certificate names, PKI info
### Initial probes

- Fingerprint SMB:

```bash
nxc smb 10.10.11.5
```

>[!example]-
> ```bash
> nxc smb 10.129.48.134
> ```
> 
> ```bash
> SMB         10.129.48.134   445    FOREST           [*] Windows Server 2016 Standard 14393 x64 (name:FOREST) (domain:htb.local) (signing:True) (SMBv1:True) (Null Auth:True)
> ```

- If supported by the installed NetExec version, probe other discovered services.

- Fingerprint RDP:

```bash
nxc rdp 10.10.11.5
```

- Fingerprint WinRM:

```bash
nxc winrm 10.10.11.5
```

- Fingerprint MSSQL:

```bash
nxc mssql 10.10.11.5
```

- Query the target over SMB, including OS information, supported dialects, signing configuration, and server time:

```bash
nmap -Pn -n -p 445 --script smb-os-discovery,smb-protocols,smb-security-mode,smb2-security-mode,smb2-time 10.10.11.5
```

>[!note]+ SMB signin can be one of:
>- **Required** — unsigned SMB sessions are rejected.
>- **Enabled but not required** — the server supports signing but may accept unsigned sessions.
>- **Disabled/not supported** — verify with another tool; means the server accepts unsigned sessions.

> [!note] [`NetExec`](https://github.com/Pennyw0rth/NetExec)
### NTLM challenge metadata

- Some services that support NTLM authentication return an NTLMv2 challenge before credentials are supplied. Depending on the service, it can reveal NetBIOS domain name/computer name, DNS domain name, host FQDN, and other information.

- Gather NTLM metadata from RDP (when NLA/CredSSP is enabled):

```bash
nmap -Pn -n -p 3389 --script rdp-ntlm-info,rdp-enum-encryption 10.10.11.5
```

- Gather NTLM metadata from Microsoft SQL Server:

```bash
nmap -Pn -n -p 1433 --script ms-sql-ntlm-info 10.10.11.5
```

- Gather NTLM information from HTTP/HTTPS endpoints that advertise NTLM:

```bash
nmap -Pn -n -p 80,443 --script http-ntlm-info 10.10.11.5 -oA nmap/http_ntlm_info
```

- The HTTP script must query a path that actually offers NTLM. For WinRM over HTTP, use `/wsman`:

```bash
nmap -Pn -n -p 5985 --script http-ntlm-info --script-args http-ntlm-info.root=/wsman 10.10.11.5
```

- For WinRM over HTTPS:

```bash
nmap -Pn -n -p 5986 --script http-ntlm-info --script-args http-ntlm-info.root=/wsman 10.10.11.5
```
### HTTP redirects and headers

- Query discovered HTTP services:

```bash
curl -sS -I http://10.10.11.5/
```

```bash
curl -k -sS -I https://10.10.11.5/
```

- Collect titles and headers across discovered web ports:

```bash
nmap -Pn -n -sV -p 80,443,5985,5986,8530,8531 --script http-title,http-headers 10.10.11.5 -oA nmap/http_initial_info
```
### NetBIOS name discovery

>[!note] NetBIOS name discovery is useful only where UDP port `137` is reachable and NetBIOS over TCP/IP is enabled.

- Scan a network range:

```bash
sudo nbtscan -r 10.10.11.0/24
```

>[!note] `-r` uses local port `137` for sending queries (normally requires elevated privileges on Linux).

- NetBIOS status query against a specific IP address:

```bash
nmblookup -A 10.10.11.5
```

- If needed, resolve a NetBIOS name to an IP address:

```bash
nmblookup <hostname>
```

>[!tip]+
>- Once you've discovered FQDN of a Domain Controller, append it to `/etc/hosts`; Kerberos authentication requires DNS resolution.
> ```bash
> sudo tee -a /etc/hosts <<EOF
> 10.10.11.5   dc01.example.com
> EOF
> ```
> - Failing to resolve domain FQDNs to target IP addresses will cause Kerberos tools (`kerbrute`, `GetNPUsers.py`, `GetUserSPNs.py`) to fail with resolution errors.

> [!note] [`nbtscan`](https://github.com/resurrecting-open-source-projects/nbtscan) · [`nmblookup`](https://www.samba.org/samba/docs/current/man-html/nmblookup.1.html)
### Querying RPC endpoints

- The RPC Endpoint Mapper on TCP `135` can disclose registered interfaces and dynamic RPC ports — without credentials:

```bash
nmap -Pn -n -p 135 --script msrpc-enum 10.10.11.5
```

- Or, using Impacket's [`rcpdump.py`](https://github.com/fortra/impacket/blob/master/examples/rpcdump.py):

```bash
rpcdump.py @10.10.11.5
```

### Identifying Domain Controllers

- Ports commonly open on DCs:
	- Kerberos `88` (TCP/UDP)
	- LDAP/CLDAP on `389` (TCP/UDP)
	- Kerberos password change (`Kpasswd`) on `464` (TCP/UDP)
	- SMB on `445` (TCP)
	- Global Catalog on `3268`/`3269` (TCP) when the DC is a GC
	- AD Web Services on `9389` (TCP)

>[!note] LDAPS (`636`) is optional, and not every DC is a Global Catalog. Their absence does not rule out a DC.

- The most reliable way to identify Domain Controllers is by querying **LDAP RootDSE**.

>[!note] See [[Querying LDAP#Querying RootDSE (anonymously)]].

- You can query LDAP RootDSE (Root Directory Server Agent Service Entry) using `ldapsearch`, or use the Nmap's **[`ldap-rootdse`](https://nmap.org/nsedoc/scripts/ldap-rootdse.html) script**:

```bash
nmap -Pn -p 389,636 --script ldap-rootdse -iL hosts.txt
```

- Since RootDSE provides metadata about the directory server, it's only present on DCs. Moreover, RootDSE can be queried **without credentials** (even if anonymous LDAP searches are disabled).

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

### Time and clock skew

- Kerberos authentication is time-sensitive. In Active Directory, the default maximum tolerated clock skew is normally **five minutes**; excessive skew can result in errors like `KRB_AP_ERR_SKEW`.

- Check the local system time:

```bash
date
```

- Query SMB time:

```bash
nmap -Pn -n -p 445 --script smb2-time 10.10.11.5
```

- Query NTP when UDP `123` is open:

```bash
sudo nmap -Pn -n -sU -p 123 --script ntp-info 10.10.11.5
```

```bash
ntpdate -q 10.10.11.5
```

- If needed, synchronize the local clock with the Domain Controller:

```bash
sudo ntpdate 10.10.11.5
```
### Inspecting TLS certificates

- Certificates can disclose internal FQDNs, aliases, CA names, organizational naming and validity periods. 
- Inspect certificates on every discovered TLS service:

```bash
nmap -Pn -n -sV -p 443,636,3269,3389,5986,8531 --script ssl-cert 10.10.11.5 -oA nmap/tls_certificates
```

>[!note] `443` (HTTPS) · `636` (LDAPS) · `3389` (RDP, encrypted by default) · `5986` (WinRM over HTTPS) · `8531` (Windows Server Update Services, WSUS over TLS)

- Inspect the LDAPS certificate directly:

```bash
openssl s_client -connect 10.10.11.5:636 -showcerts </dev/null 2>/dev/null | openssl x509 -noout -subject -issuer -serial -dates -ext subjectAltName
```
## DNS enumeration

- Active Directory relies heavily on DNS for name resolution and service discovery. Querying DNS is one of the first things to do once the domain name and a DNS server are known.
### Start of Authority (`SOA`) records

- The **`SOA` (Start of Authority)** record marks the beginning of a DNS zone and contains administrative information about that zone.
- The **`MNAME` field** identifies the name server configured as the primary source for the zone.
- The **`RNAME` field** contains email address of the administrator responsible for the zone (where `@` is replaced with `.`). This gives insights into the username format, which comes helpful during username enumeration.
- The record also contains the serial number (`SERIAL`) of the zone, as well as its refresh (`REFRESH`), retry (`RETRY`), and expire (`EXPIRE`) timers that reveal how frequently the secondary DNS servers sync changes with the primary.

- Query `SOA` records:

```bash
nslookup -type=SOA example.com 10.10.11.5
```

>[!example]-
> ```bash
> nslookup -type=SOA htb.local 10.129.95.210
> ```
> 
> ```bash
> Server:		10.129.95.210
> Address:	10.129.95.210#53
> 
> htb.local
> 	origin = forest.htb.local
> 	mail addr = hostmaster.htb.local
> 	serial = 119
> 	refresh = 900
> 	retry = 600
> 	expire = 86400
> 	minimum = 3600
> ```

```bash
dig SOA example.com @10.10.11.5
```

>[!example]-
> ```bash
> dig SOA htb.local @10.129.95.210
> ```
> 
> ```bash
> ; <<>> DiG 9.20.18-1~deb13u1-Debian <<>> SOA htb.local @10.129.95.210
> ;; global options: +cmd
> ;; Got answer:
> ;; WARNING: .local is reserved for Multicast DNS
> ;; You are currently testing what happens when an mDNS query is leaked to DNS
> ;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 11109
> ;; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 3
> 
> ;; OPT PSEUDOSECTION:
> ; EDNS: version: 0, flags:; udp: 4000
> ; COOKIE: 0cc2c1e91b0e4cdb (echoed)
> ;; QUESTION SECTION:
> ;htb.local.			IN	SOA
> 
> ;; ANSWER SECTION:
> htb.local.		3600	IN	SOA	forest.htb.local. hostmaster.htb.local. 119 900 600 86400 3600
> 
> ;; ADDITIONAL SECTION:
> forest.htb.local.	3600	IN	A	10.129.95.210
> forest.htb.local.	3600	IN	AAAA	dead:beef::9085:b600:caf3:bbbf
> 
> ;; Query time: 9 msec
> ;; SERVER: 10.129.95.210#53(10.129.95.210) (UDP)
> ;; WHEN: Fri Aug 14 04:55:51 EDT 2026
> ;; MSG SIZE  rcvd: 148
> ```

| Field         | Example                  | Description                                                                            |
| ------------- | ------------------------ | -------------------------------------------------------------------------------------- |
| **`MNAME`**   | `DC01.example.com`       | Primary authoritative DNS server. <br>Reveals core Domain Controllers.                 |
| **`RNAME`**   | `hostmaster.example.cp,` | Email of the administrator responsible for the zone. <br>Helps map naming conventions. |
| **`SERIAL`**  | `2026081401`             | Incremental zone version. <br>Changes indicate recent DNS modifications.               |
| **`REFRESH`** | `900` (15m)              | How often secondary DNS servers query the primary server for updates.                  |
| **`RETRY`**   | `600` (10m)              | Wait time before retrying a failed zone refresh attempt.                               |
| **`EXPIRE`**  | `86400` (24h)            | Time limit before secondary servers stop serving un-refreshed zone data.               |

>[!note] See [`SOA record — Wikipedia`](https://en.wikipedia.org/wiki/SOA_record).
### `SRV` (Service Location) records

- Active Directory automatically publishes **`SRV` (Service Location)** DNS records that define the location — the hostname and port number — of servers for specified services. This means Domain Controllers, Global Catalog servers, Kerberos KDC, and all other services register themselves via `SRV` records.
- The records are **readable by anyone** who can query the DNS server, without any authentication needed, and this is why they are so important for information gathering.

- `SRV` records follow the format: `_service._protocol.domain` (e.g., `_ldap._tcp.corp.local`).

| Prefix / component | Description                                                                                    |
| ------------------ | ---------------------------------------------------------------------------------------------- |
| `_ldap`            | Locates LDAP services (typically running on Domain Controllers).                               |
| `_kerberos`        | Locates Key Distribution Centers (KDCs) that handle authentication.                            |
| `_kpasswd`         | Locates servers handling Kerberos password changes (Kpasswd).                                  |
| `_gc`              | Locates Global Catalog servers (multi-domain search index).                                    |
| `_tcp` / `_udp`    | Transport protocol used by the target service (TCP or UDP).                                    |
| `dc`               | Limits service location query results strictly to Domain Controllers.                          |
| `pdc`              | Identifies the DC holding the **PDC Emulator FSMO role**.                                      |
| `_sites`           | Limits service location query results to a specific Active Directory site boundary.            |
| `_msdcs`           | Microsoft Domain Controller Services zone used internally for AD replication and DC discovery. |

- Locate all DCs via LDAP `SRV` record:

```bash
nslookup -type=srv _ldap._tcp.dc._msdcs.example.com 10.10.11.5
```

```bash
dig _ldap._tcp.dc._msdcs.example.com SRV @10.10.11.5
```

- Locate Global Catalog servers:

```bash
nslookup -type=srv _gc._tcp.example.com 10.10.11.5
```

```bash
dig -t SRV _gc._tcp.example.com @10.10.11.5
```

- Locate Kerberos KDC:

```bash
nslookup -type=srv _kerberos._tcp.example.com 10.10.11.5
```

```bash
dig -t SRV _kerberos._tcp.example.com @10.10.11.5
```

- Locate Kerberos password change servers:

```bash
nslookup -type=srv _kpasswd._tcp.example.com 10.10.11.5
```

```bash
dig _kpasswd._tcp.iexample.com SRV @10.10.11.5
```

| Record                             | Description                              |
| ---------------------------------- | ---------------------------------------- |
| `_ldap._tcp.example.com`           | Locate all Domain Controllers.           |
| `_kerberos._tcp.example.com`       | Locate KDCs.                             |
| `_kpasswd._tcp.example.com`        | Locate Kerberos password change servers. |
| `_gc._tcp.example.com`             | Locate Global Catalog servers.           |

>[!note] See [`SRV record — Wikipedia`](https://en.wikipedia.org/wiki/SRV_record).
### Reverse DNS lookup (`PTR` sweeps)

- **`PTR` (pointer) records** maps IP addresses to corresponding domain names or hostnames. They come useful when you know the target IP address range and want to the the domain name and hostnames.

- Query an individual `PTR` record:

```bash
nslookup -type=PTR 10.10.11.5 10.10.11.5
```

```bash
dig -x 10.10.11.5 @10.10.11.5
```

- Perform a `PTR` sweep across a subnet:

```bash
nmap -sn -R --dns-servers 10.10.11.5 10.10.11.0/24
```

```bash
dnsrecon -r 10.10.11.0/24 -n 10.10.11.5
```

### Unauthenticated DNS zone transfers (`AXFR`)

- An **`AXFR` (Asynchronous Full Transfer)** query requests a complete copy of the entire DNS database zone file from the DNS server. 
- Although misconfigurations become less and less common today, successful zone transfers instantly map out every host, server, alias, and subdomain registered in the domain, so it's worth trying.

```bash
dig AXFR example.com @10.10.11.5
```

```bash
dnsrecon -d example.com -n 10.10.11.5 -t axfr
```

> [!note] [`dig man page — BIND`](https://bind9.readthedocs.io/en/v9.18.1/manpages/dig.html) · [`dnsrecon — GitHub`](https://github.com/darkoperator/dnsrecon)

### `dnsrecon`

- [`dnsrecon`](https://github.com/darkoperator/dnsrecon) automatically checks multiple records (including `SOA`, `SRV`, `PTR`) and tests for zone transfers.
- Query standard records: `NS`, `SOA`, `MX`, `SRV`:

```bash
dnsrecon -d example.com -t std
```

- Attempt a zone transfer:

```bash
dnsrecon -d example.com -n 10.10.11.5 -t axfr
```

- DNSSEC zone walking (if DNSSEC is enabled):

```bash
dnsrecon -d example.com -t zonewalk
```

>[!note] See [[Querying DNS]] and [[Subdomain enumeration#DNSSEC zone walking]].
## SMB enumeration

### Fingerprinting

- Gather SMB information:

```bash
nxc smb 10.10.11.5
```

>[!example]-
> ```bash
> nxc smb 10.129.48.134
> ```
> 
> ```bash
> SMB         10.129.48.134   445    FOREST           [*] Windows Server 2016 Standard 14393 x64 (name:FOREST) (domain:htb.local) (signing:True) (SMBv1:True) (Null Auth:True)
> ```

- Check SMB security flags (SMB signing, guest access):

```bash
nmap -Pn -p 445 --script smb-security-mode,smb2-security-mode 10.10.11.5
```

> [!example]-
> ```bash
> nmap -Pn -p 445 --script smb-security-mode,smb2-security-mode 10.129.95.210
> ```
> 
> ```bash
> Starting Nmap 7.95 ( https://nmap.org ) at 2026-08-14 05:35 EDT
> Nmap scan report for 10.129.95.210
> Host is up (0.0077s latency).
> 
> PORT    STATE SERVICE
> 445/tcp open  microsoft-ds
> 
> Host script results:
> | smb-security-mode: 
> |   account_used: guest
> |   authentication_level: user
> |   challenge_response: supported
> |_  message_signing: required
> | smb2-security-mode: 
> |   3:1:1: 
> |_    Message signing enabled and required
> 
> Nmap done: 1 IP address (1 host up) scanned in 2.11 seconds
> ```

- Attempt to enumerate accessible shared folders and extract usernames via SMB:

```bash
nmap -Pn -p 445 --script smb-enum-shares,smb-enum-users 10.10.11.5
```
### SMB null and `Guest` sessions

- An **SMB null session** occurs when a client establishes an SMB connection to the server using an empty username `''` and an empty password `''`.

>[!warning] **Windows 10/11** and **Windows Server 2016+** disable guest and null SMB access by default (but legacy servers or misconfigured file shares often remain vulnerable).

- Test for SMB null sessions:

```bash
nxc smb 10.10.11.5 -u '' -p ''
```

- Test for `Guest` sessions:

```bash
nxc smb 10.10.11.5 -u 'Guest' -p '' 
```

- Enumerate shares accessible via a null session:

```bash
nxc smb 10.10.11.5 -u '' -p '' --shares
```

```bash
smbclient -L //10.10.11.5 -N
```

- Enumerate shares accessible via a `Guest` session:

```bash
nxc smb 10.10.11.5 -u 'Guest' -p '' --shares
```

```bash
smbclient -L //10.10.11.5 -U 'Guest%'
```

- Attempt to connect to a specific share using a null session:

```bash
smbclient //10.10.11.5/IPC$ -N
```
```bash
smbclient //10.10.11.5/SYSVOL -N
```

>[!tip]+ If anonymous access or credentials are found, perform authenticated enumeration. See [[🛠️ Authenticated AD & Windows enumeration#SMB enumeration]].

## LDAP enumeration

### LDAP anonymous binds

- By default, Active Directory Domain Controllers require authenticated binds (GSS-API/NTLM/simple bind with credentials) for LDAP queries. 
- However, misconfigured DCs may allow **anonymous binds** (simple binds with no password).

- Check for anonymous LDAP bind:

```bash
ldapsearch -x -H ldap://10.10.11.5
```

> [!example]-
> ```bash
> ldapsearch -x -H ldap://10.129.48.134
> ```
> 
> ```bash
> # extended LDIF
> #
> # LDAPv3
> # base <> (default) with scope subtree
> # filter: (objectclass=*)
> # requesting: ALL
> #
> 
> # search result
> search: 2
> result: 32 No such object
> text: 0000208D: NameErr: DSID-0310021B, problem 2001 (NO_OBJECT), data 0, best 
>  match of:
> 	''
> 
> 
> # numResponses: 1
> ```

>[!tip]+
> - LDAP search operations normally require a valid base DN; running a query without it may return `No such object`.
> - The base DN can be discovered by querying RootDSE, for example with Nmap's `ldap-rootdse` script:
> 
> ```bash
> nmap -Pn -p 389 --script ldap-rootdse 10.10.11.5
> ```
> 
>  - RootDSE is commonly readable anonymously, even when anonymous directory searches are disabled.
>  - A `No such object` response doesn't by itself indicate whether anonymous LDAP searches are allowed. 
>  - Query RootDSE first, obtain `defaultNamingContext`, then test a search against that DN. 
> 
>>[!note] See [[#Discovering RootDSE]].

- Attempt to execute a search query using anonymous LDAP bind (`ldap-search`):

```bash
nmap -p 389 --script ldap-search 10.10.11.5
```


- Check for anonymous LDAP bind by querying RootDSE:

```bash
ldapsearch -x -H ldap://10.10.11.5 -b "" -s base
```


- Attempt to enumerate all user accounts on the domain (returns only their `sAMAccountName`) using anonymous LDAP bind:

```bash
ldapsearch -x -H ldap://10.10.11.5 -b "DC=example,DC=com" "(objectClass=user)" sAMAccountName
```

| Option | Description                                                                                       |
| ------ | ------------------------------------------------------------------------------------------------- |
| `-x`   | Force simple authentication (instead of SASL).                                                    |
| `-H`   | LDAP URI (`ldap://<host>`).                                                                       |
| `-b`   | Base DN to use for search.                                                                        |
| `-s`   | Scope to use for search queries; possible values: `base`, `one`, `sub` (default), `subordinates`. |

>[!tip]+ If LDAP anonymous bind succeeds, proceed to authenticated enumeration. See [[🛠️ Authenticated AD & Windows enumeration#Querying LDAP]].

>[!note] [`ldapsearch`](https://docs.ldap.com/ldap-sdk/docs/tool-usages/ldapsearch.html)
### Discovering RootDSE

- Attempt to query RootDSE attributes via an unauthenticated LDAP query:

```bash
ldapsearch -x -H ldap://10.10.11.5 \
  -b '' -s base '(objectClass=*)' \
  defaultNamingContext rootDomainNamingContext dnsHostName \
  ldapServiceName namingContexts isGlobalCatalogReady currentTime
```

```bash
nmap -Pn -p 389 --script ldap-rootdse 10.10.11.5
```

### Inspecting LDAPS certificates

- Query and inspect LDAPS certificate:

```bash
openssl s_client -connect dc01.example.com:636 -servername dc01.example.com </dev/null 2>/dev/null | openssl x509 -noout -subject -issuer -ext subjectAltName
```

## MS-RPC enumeration

- Windows RPC can be exposed through SMB named pipes and through dynamically mapped RPC endpoints.
### Enumerating RPC endpoints

- Enumerate RPC endpoints:

```bash
nmap 10.10.11.5 --script msrpc-enum
```
### RPC null sessions

- Check for MS-RPC null sessions:

```bash
rpcclient -U '' -N 10.10.11.5
```

- Establish an RPC null session and run commands:

```bash
rpcclient -U '' -N 10.10.11.5 -c 'querydominfo; getdompwinfo; enumdomains; enumdomusers; enumdomgroups'
```

>[!tip] If succeeds, proceed to authenticated RPC enumeration. See [[🛠️ Authenticated AD & Windows enumeration#rpcclient]].

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

## Automated enumeration: `enum4linux-ng`

- Test for null sessions across SMB, RPC, and LDAP simultaneously:

```bash
enum4linux-ng -A 10.10.11.5
```

- Specify empty credentials explicitly:

```bash
enum4linux-ng -u '' -p '' 10.10.11.5
```

>[!note] See [`enum4linux-ng`](https://github.com/cddmp/enum4linux-ng).
### Unauthenticated Kerberos username enumeration

- Enumerate domain users via Kerberos pre-authentication (anonymously):

```bash
kerbrute userenum -d example.com --dc 10.10.11.5 /usr/share/wordlists/statistically-likely-usernames/jsmith.txt
```

>[!note] See [[Username enumeration in AD#Username enumeration with Kerbrute]].
## References and further reading

- [`Active Directory Domain Services Overview — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview)
- [`NetExec Documentation — NetExec`](https://www.netexec.wiki/)
- [`Impacket Tools — Fortra GitHub`](https://github.com/fortra/impacket)
- [`Kerbrute — ropnop GitHub`](https://github.com/ropnop/kerbrute)
- [`enum4linux-ng — cddmp GitHub`](https://github.com/cddmp/enum4linux-ng)
- [`Nmap Network Scanning — Nmap`](https://nmap.org/book/)
- [`RFC 4120 — The Kerberos Network Authentication Service (V5)`](https://datatracker.ietf.org/doc/html/rfc4120)
- [`Statistically Likely Usernames — InsideTrust GitHub`](https://github.com/insidetrust/statistically-likely-usernames)

- [`SOA record — Wikipedia`](https://en.wikipedia.org/wiki/SOA_record)
- [`SRV record — Wikipedia`](https://en.wikipedia.org/wiki/SRV_record)




>[!note]+ Output breakdown
> - `rootDomainNamingContext` / `defaultNamingContext`: Domain Distinguished Name (`DC=EXAMPLE,DC=COM`).
> - `dnsHostName`: Fully Qualified Domain Name (FQDN) of the Domain Controller (`ACADEMY-EA-DC01.EXAMPLE.COM`).
> - `domainFunctionality`: Active Directory domain functional level.


	-  NTLM messages pass the NetBIOS domain name during the authentication challenge-response exchange. This identifier is required, for example, In NTLM Relay attacks.
- 
	- Any raw LDAP query (via `ldapsearch`, PowerShell AD modules, or tools like `BloodHound`/`SharpHound`) requires the base DN.

>[!note] NetBIOS name matters in [[LLMNR & NBT-NS poisoning]]. When a user queries a domain name DNS can't resolve, Windows falls back to local broadcast protocols like LLMNR and NBT-NS. Tools like `Responder` can capture these broadcast queries and trick the client into sending hashed credentials (NetNTLMv2 challenge-response material) to an attacker-controlled machine.