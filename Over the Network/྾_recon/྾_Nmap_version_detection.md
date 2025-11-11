---
created: 2025-09-26
tags:
  - nmap
---
## Version detection

Nmap can not only tell which ports are closed and which are open, but also what services are running there, their versions, and what's the OS of the target system. With this information alone you are already able to search for known exploits and plan attacks.

>[!interesting]+ How Nmap version detection works
> Nmap maintains a library of probes in the **[`nmap-service-probes`](https://nmap.org/book/vscan-fileformat.html) file**. Each probe is a protocol- or service-specific message (like HTTP `GET`, SMTP `HELO`/`ELHO`, SSL/TLS handshake, DNS query, etc.) designed to elicit a unique response.
> For service detection, Nmap first builds a list of **open** ports, and then sends corresponding probes, chosen from the `nmap-service-probes` file, to each open port.\
> The response is matched against a vast set of **regular expressions** to identify:
>- Service protocol (e.g., HTTP, SSH, FTP, etc.)
>- Application name (e.g., Apache `httpd`, OpenSSH, etc.)
>- Version number
>- Device type, hostname, OS family (if available)
>- CPE (Common Platform Enumeration) string for vulnerability mapping

Key Nmap options for version detection:

| Option                      | Description                                                                                                                                                                                            |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `-sV`                       | Enable service/version detection.                                                                                                                                                                      |
| `--version-intensity <0-9>` | Control how many/which probes are sent.<br>The higher the number the more likely the service will be identified correctly; however, more intensive scans take longer.<br>The default intensity is `7`. |
| `--version-light`           | Same as `--version-intensity 2`; light scans are faster but less likely to identify services.                                                                                                          |
| `--version-all`             | Same as `--version-intensity 9`; ensures that every single probe is attempted against each port; takes much longer.                                                                                    |
| `--version-trace`           | Print out extensive debugging information on version scanning (a subset of `--packet-trace`).                                                                                                          |
| `--allports`                | Don't exclude any ports from version detection.                                                                                                                                                        |

>[!tip]
>- Lower intensity (`--version-intensity 0-3`) is stealthier but less thorough.
>- Higher intensity (`7-9`) is more accurate but slower and noisier.

>[!tip] Use `--allports` to include ports like `9100` (often excluded because some printers simply print anything sent to that port). 

- Enable service/version detection:

```bash
nmap -sV <target>
```

## OS detection

>[!interesting]+ How Nmap OS detection works 
>Fore remote OS detection, Nmap uses **TCP/IP stack fingerprinting**: it sends a series of TCP and UDP packets (e.g., TCP ISN sampling, TCP options support and ordering, IP ID sampling, initial windows size check, etc.) to the target host and compares the responses to the its internal database, `nmap-os-db`. 
>[`nmap-os-db`](https://nmap.org/book/nmap-os-db.html) is a large file with hundreds of example of how different OSs respond to Nmap's OS detection probes. The file is divided into blocks known as fingerprints; each fingerprint contains:
>- Vendor name (e.g., Microsoft)
>- OS family and generation (e.g., Windows 10)
>- Device type (e.g., general-purpose, router, switch, etc.)
>- CPE (Common Platform Enumeration) string for standardized identification (e.g., `cpe:/o:linux:linux_kernel:2.6`).

Nmap OS detection options:

| Option           | Description                                                                                                                                                                                                                                                                                                                   |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `-O`             | Enable OS detection.                                                                                                                                                                                                                                                                                                          |
| `-A`             | Aggressive scan (OS and service version detection, scripts, and traceroute).                                                                                                                                                                                                                                                  |
| `--osscan-limit` | For effective OS detection, Nmap needs to find at least one open and one closed port on the target.<br>With this option, Nmap won't even try OS detection against hosts that don't meet this criteria.<br>Only applies if `-O` or `-A` options are used.                                                                      |
| `--osscan-guess` | Guess OS when uncertain; close matches.                                                                                                                                                                                                                                                                                       |
| `--max-os-tries` | Set the maximum number of OS detection tries against a target.<br>by default, Nmap tries five times when the target meets the requirements for reliable OS detection and two times when the conditions aren't so good.<br>Lower values speed up the scan, but may miss out on retries that could potentially identify the OS. |

Nmap can detect the Operating System (OS) based on its behavior and any telltale signs in its responses. OS detection can be enabled using `-O`.

```bash
nmap -O <target>
```

>[!important] For OS version detection, Nmap needs to find at least one open and one closed port on the target to make a reliable guess.

>[!note] The target OS fingerprints might get distorted due to the use of virtualization and similar technologies. That's why you should always take the OS version with a grain of salt.

## References and further reading 

- [`nmap-service-probes File Format — Nmap`](https://nmap.org/book/vscan-fileformat.html)
- [`Service and Version Detection — Nmap`](https://nmap.org/book/man-version-detection.html)
- [`Nmap OS Detection DB: nmap-os-db — Nmap`](https://nmap.org/book/nmap-os-db.html)
- [`OS detection — Nmap`](https://nmap.org/book/man-os-detection.html)