---
created: 2026-09-22
updated: 2026-10-11
tags:
  - services_n_protocols
---
>[!note] See [[Privileged remote access]].
## RDP

>**[Remote Desktop Protocol (RDP)](https://en.wikipedia.org/wiki/Remote_Desktop_Protocol)** is a [Microsoft-proprietary](https://learn.microsoft.com/en-us/troubleshoot/windows-server/remote/understanding-remote-desktop-protocol) application-layer protocol that lets a user connect to and control another computer over the network through a graphical session.

- RDP is one of the most widely deployed administrative tools and is installed on Windows by default.
- It is also one of the most commonly exploited remote-access vectors, both through weak credentials and through protocol-level vulnerabilities.
- RDP follows a **client-server model**:
	- The **client** initiates the connection and renders the remote graphical session locally.
	- The **server** is the Windows host that accepts the connection and serves the session.

>[!important] By default, RDP listens on **TCP port `3389`**.
>- Starting with RDP 8.0 (Windows 8 / Server 2012), **UDP port `3389`** is also supported for performance acceleration.
>- When both are available, **RDP prefers UDP** and falls back to TCP on failure.

- The protocol multiplexes several **virtual channels** within a single connection, each carrying a distinct feature such as display data, audio, clipboard content, drive redirection, or printer traffic.
- Beyond screen, keyboard, and mouse, RDP supports:
	- **Clipboard sharing** — bidirectional copy-paste between client and server.
	- **Drive redirection** — mount local directories as network shares inside the remote session.
	- **Printer redirection** — print from the remote session to a local printer.
	- **Port redirection** — tunnel arbitrary TCP connections through the RDP session.
	- **Audio redirection** — play remote audio locally or forward the local microphone to the server.
	- **32-bit color and dynamic resolution.**

### RDP ports

| Port       | Protocol  | Description                                                                            |
| ---------- | --------- | ------------------------------------------------------------------------------------- |
| `3389/tcp` | RDP (TCP) | **Default RDP listener**, secured with TLS and Network Level Authentication (NLA).     |
| `3389/udp` | RDP (UDP) | **Performance-acceleration transport** (RDP 8.0+); RDP prefers it and falls back to TCP. |

### How RDP works

- Modern RDP sessions are secured with **TLS** and **Network Level Authentication (NLA)**.
- The protocol is based on the ITU-T T.128 application-sharing standard and multiplexes display, input, clipboard, audio, and redirection traffic over separate virtual channels within one connection.

#### RDP authentication and NLA

>**[Network Level Authentication (NLA)](https://en.wikipedia.org/wiki/Remote_Desktop_Services#Network_Level_Authentication)** is an RDP security feature that requires the user to authenticate before a remote desktop session is established.

>[!note] Before NLA, connecting to an RDP server loaded a full Windows login screen, meaning the server rendered a graphical session for *every incoming connection*, authenticated or not. This was exploitable (denial-of-service, [BlueKeep](https://en.wikipedia.org/wiki/BlueKeep)), and NLA was Microsoft's mitigation.

- With NLA, the server verifies the user's credentials through the **Credential Security Support Provider (`CredSSP`)** protocol during the *initial connection negotiation*, before any session is served.
- This prevents the login screen from loading for unauthorized attempts and ensures that only authenticated users reach the remote host.

>[!note] NLA is enabled by default on Windows Vista / Server 2008 and later.

>[!note]+ Besides `CredSSP`, RDP can authenticate with:
> - **Kerberos** — on domain-joined hosts when a KDC is reachable.
> - **NTLM** — the fallback when Kerberos is unavailable; used for workgroup machines or cross-domain connections.
> - **Local accounts** — on standalone, workgroup hosts.

>[!important] By default, only members of the **`Administrators`** and **`Remote Desktop Users`** groups can log on through RDP.


## Enumerating RDP

### Port scanning and version detection

- Perform service version detection on the default RDP port:

```bash
sudo nmap -sV -p 3389 10.10.11.5
```

>[!tip]+
> - Scan the full TCP range with version detection in case RDP is bound to a non-standard port:
> 
> ```bash
> sudo nmap -sV -p- 10.10.11.5
> ```

- Run version detection together with the default NSE scripts:

```bash
sudo nmap -sV -sC -p 3389 10.10.11.5
```

- Run all available RDP NSE scripts:

```bash
nmap -p 3389 --script "rdp-*" 10.10.11.5
```

| Option     | Description                                                   |
| :--------- | :---------------------------------------------------------- |
| `-sV`      | Enable service version detection.                           |
| `-sC`      | Run the default NSE script set.                             |
| `-p`       | Specify destination port(s) to scan (`3389` or `-p-`).      |
| `--script` | Execute a specific NSE script or glob expression.           |

- Key Nmap RDP scripts:

| Script                                                                            | Categories          | Description                                                                                                                       |
| --------------------------------------------------------------------------------- | ------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| [`rdp-enum-encryption`](https://nmap.org/nsedoc/scripts/rdp-enum-encryption.html) | `discovery`, `safe` | Determine the supported RDP security layers and encryption levels by testing available protocols and ciphers.                     |
| [`rdp-ntlm-info`](https://nmap.org/nsedoc/scripts/rdp-ntlm-info.html)             | `discovery`, `safe` | Enumerate NTLM information from RDP services with `CredSSP` (NLA) enabled, including domain, hostname, and OS build details.       |
| [`rdp-vuln-ms12-020`](https://nmap.org/nsedoc/scripts/rdp-vuln-ms12-020.html)     | `vuln`, `safe`      | Check whether the target is vulnerable to `MS12-020`, which can allow denial-of-service or remote code execution.                 |

- Determine the supported encryption and retrieve NTLM information:

```bash
nmap -p 3389 --script rdp-enum-encryption,rdp-ntlm-info 10.10.11.5
```

- Check for the `MS12-020` vulnerability:

```bash
nmap -p 3389 --script rdp-vuln-ms12-020 10.10.11.5
```

>[!tip]+
> - List local Nmap scripts for RDP:
> 
> ```bash
> ls -l /usr/share/nmap/scripts/*rdp*
> ```

### Enumerating usernames

- RDP returns different error messages for valid and invalid usernames, which can be abused to enumerate accounts.

- Enumerate usernames using [`crowbar`](https://github.com/galkan/crowbar):

```bash
crowbar -b rdp -s 10.10.11.5/32 -u usernames.txt -C /usr/share/wordlists/rockyou.txt
```

>[!note] `crowbar` takes its target in CIDR notation. Use `/32` for a single host, or supply a network address and prefix to sweep a range.

### Enumerating active sessions

- With valid credentials or from the same host, active RDP sessions can be listed without connecting to one.

- List active sessions on a remote host with `query user`:

```powershell
query user /server:10.10.11.5
```

- Use the shorter `quser` alias:

```powershell
quser /server:10.10.11.5
```

- List sessions with [`qwinsta`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/qwinsta):

```powershell
qwinsta /server:10.10.11.5
```

### Auditing RDP security settings

>[`rdp-sec-check`](https://github.com/CiscoCXSecurity/rdp-sec-check) is a Perl script that enumerates the security settings of an RDP service. It was developed by [CiscoCXSecurity](https://github.com/CiscoCXSecurity).

- Audit the RDP service configuration:

```bash
perl ./rdp-sec-check.pl 10.10.11.5
```

>[!warning] `rdp-sec-check` is old and does not test for recent vulnerabilities, but it remains useful for basic checks such as weak encryption and missing NLA.

## Brute-forcing credentials

>[!note]+ Common credentials to try first
> 
> ```text
> Administrator:<blank>
> Administrator:admin
> Administrator:password
> Administrator:Password123
> admin:admin
> user:user
> ```

- Brute-force the password for a single user using Hydra:

```bash
hydra -l Administrator -P /usr/share/wordlists/rockyou.txt rdp://10.10.11.5
```

- Brute-force credentials for multiple users on a non-standard port using Hydra:

```bash
hydra -L usernames.txt -P /usr/share/wordlists/rockyou.txt -s 3390 10.10.11.5 rdp
```

- Brute-force credentials using Medusa:

```bash
medusa -M rdp -h 10.10.11.5 -u Administrator -P /usr/share/wordlists/rockyou.txt -e ns
```

- Brute-force credentials using [`crowbar`](https://github.com/galkan/crowbar), which handles NLA better than Hydra in some configurations:

```bash
crowbar -b rdp -s 10.10.11.5/32 -u Administrator -C /usr/share/wordlists/rockyou.txt
```

- Brute-force both usernames and passwords with `crowbar`:

```bash
crowbar -b rdp -s 10.10.11.5/32 -U usernames.txt -C /usr/share/wordlists/rockyou.txt
```

| Option        | Description                                                          |
| :------------ | :------------------------------------------------------------------ |
| `-l` / `-L`   | Set a single username or a username wordlist (Hydra).               |
| `-P`          | Read passwords from a wordlist file (Hydra, Medusa).                |
| `-s`          | Set the target port (Hydra `-s`, before the `rdp` service keyword). |
| `-M`          | Select the target protocol module (Medusa).                        |
| `-u` / `-U`   | Set a single username or a username wordlist (Medusa, `crowbar`).   |
| `-e ns`       | Additionally test an empty password (`n`) and the username as the password (`s`) (Medusa). |
| `-b`          | Select the target protocol (`crowbar`).                            |
| `-C`          | Read passwords from a wordlist file (`crowbar`).                    |
| `-v`          | Produce verbose output (`crowbar`).                                |

>[!note] See [[🛠️ Custom wordlists and rules]] for building targeted username and password lists.

>[!warning] RDP logon failures are logged and count against domain account lockout policies. Prefer measured password spraying over exhaustive brute-forcing against domain accounts.

## Connecting over RDP

>[!note] See [[Privileged remote access#RDP]] for the full client reference, including native Windows connections with `mstsc.exe`.

- From Linux, connect to an RDP server with [`xfreerdp`](https://www.freerdp.com/), [`Remmina`](https://remmina.org/) (GUI), or the older [`rdesktop`](http://www.rdesktop.org/).

>[!tip]+ On Wayland, use [`wlfreerdp`](https://manpages.debian.org/testing/freerdp2-wayland/wlfreerdp.1.en.html) instead of `xfreerdp`.

- Connect to a Windows host:

```bash
xfreerdp /v:10.10.11.5 /u:jdoe /p:'passwd123'
```

- Enable clipboard redirection:

```bash
xfreerdp /v:10.10.11.5 /u:jdoe /p:'passwd123' +clipboard
```

- Enable audio output redirection:

```bash
xfreerdp /v:10.10.11.5 /u:jdoe /p:'passwd123' /sound:sys:alsa
```

- Enable dynamic resolution:

```bash
xfreerdp /v:10.10.11.5 /u:jdoe /p:'passwd123' /dynamic-resolution
```

- Mount a local directory as a redirected drive in the remote session:

```bash
xfreerdp /v:10.10.11.5 /u:jdoe /p:'passwd123' /drive:loot,/tmp
```

- Ignore TLS certificate validation errors:

```bash
xfreerdp /v:10.10.11.5 /u:jdoe /p:'passwd123' /cert:ignore
```

>[!interesting]- Linux audio backends and RDP audio redirection
>```bash
>/sound[:sys:<backend>,dev:<device>,...]
>```
>- The `/sound` option enables **audio output redirection**: audio from the remote Windows machine plays on the local Linux machine.
>- For example, `/sound:sys:alsa` enables redirection (`/sound`) using the **ALSA backend** (`sys:alsa`).
>
>An **audio backend** on Linux is the software layer that handles audio playback and routing between applications and hardware. Common backends:
>- ALSA (`sys:alsa`) — low-level Linux sound system with direct hardware access.
>- PulseAudio (`sys:pulse`) — PulseAudio sound server; the default on Ubuntu, Kali, and similar.
>- PipeWire (`sys:pipewire`) — modern replacement for PulseAudio (often compatible via `pulse`).
>
>`xfreerdp` chooses PulseAudio by default when it is available.

>[!interesting]- Drive redirection
>```bash
>/drive:<name>,<local_path>
>```
>- The `/drive` option enables **drive redirection**, making local files and directories appear inside the remote RDP session.
>- Redirected drives appear under `\\tsclient` (open Explorer and type `\\tsclient`) and under `This PC` → `Redirected drives and folders`.
>- For example, `/drive:home,/home/user` redirects the local `/home/user` directory into the session as a drive named `home`.
>- To redirect *all* local drives (potentially risky), use `/drives`.

### `xfreerdp` option reference

- Core connection settings:

| Option                          | Description                                                                    |
| ------------------------------- | ------------------------------------------------------------------------------ |
| `/v:server[:port]`              | Specify the target RDP server hostname, IP address, or URL with optional port. |
| `/u:[domain\user\|user@domain]` | Specify the username for authentication.                                       |
| `/p:password`                   | Specify the password for authentication.                                       |
| `/d:domain`                     | Specify the authentication domain.                                             |
| `/port:port`                    | Specify the port when it is not included in `/v:`.                             |

- Authentication and session control:

| Option                    | Description                                                      |
| ------------------------- | ---------------------------------------------------------------- |
| `/admin` or `/console`    | Connect to the admin (console) session of the server.            |
| `+auth-only`              | Perform authentication without establishing a full session.      |
| `/auth-pkg-list:`         | Filter the allowed authentication packages, such as NTLM or Kerberos. |
| `+credentials-delegation` | Enable credential delegation to the server.                      |
| `/pth:hash`               | Authenticate with an NT hash (Pass-the-Hash, Restricted Admin Mode). |
| `/restricted-admin`       | Connect in Restricted Admin Mode.                                |

- Re-connection and reliability:

| Option                                | Description                                               |
| ------------------------------------- | --------------------------------------------------------- |
| `+auto-reconnect`                     | Enable automatic reconnection on connection loss.         |
| `/auto-reconnect-max-retries:retries` | Set the maximum reconnection attempts (`0` means unlimited). |
| `/timeout:ms`                         | Adjust the connection timeout for high-latency environments. |

- Display and graphics:

| Option                | Description                                                  |
| --------------------- | ------------------------------------------------------------ |
| `/f`                  | Enable fullscreen mode.                                      |
| `/w:width`            | Set the window width.                                        |
| `/h:height`           | Set the window height.                                       |
| `+dynamic-resolution` | Update the resolution when the window is resized.            |
| `/bpp:depth`          | Set the color depth in bits per pixel.                       |
| `-wallpaper`          | Disable wallpaper rendering.                                 |
| `-themes`             | Disable themes.                                              |
| `/workarea`           | Use the available work area instead of full screen.          |

- Device and resource redirection:

| Option             | Description                                                   |
| ------------------ | ------------------------------------------------------------- |
| `/drive:name,path` | Redirect a local directory as a network share.               |
| `+drives`          | Redirect all mounted drives.                                  |
| `/clipboard:`      | Configure clipboard redirection behavior and direction.      |
| `/usb:`            | Redirect USB devices using vendor/product or bus addressing. |
| `/sound:`          | Redirect audio output to the local machine.                  |
| `/microphone:`     | Redirect the local microphone to the server.                 |

- Security and encryption:

| Option                 | Description                                                                 |
| ---------------------- | --------------------------------------------------------------------------- |
| `/cert:`               | Control certificate validation behavior (`ignore`, `deny`, `tofu`, `fingerprint`). |
| `/encryption-methods:` | Specify the allowed RDP encryption methods (`40`, `56`, `128`, `FIPS`).     |
| `+fipsmode`            | Enable FIPS mode.                                                           |
| `/tls:`                | Configure TLS settings, including ciphers and protocol versions.            |

>[!note] See [`xfreerdp — man page`](https://man.archlinux.org/man/extra/freerdp/xfreerdp3.1.en) for the complete option list.

## Restricted Admin Mode and Pass-the-Hash attacks

- **Restricted Admin Mode** is an RDP security feature introduced in Windows 8.1 and Server 2012 R2.
- Instead of an interactive logon, the mode forces a **network logon**, so the remote host does not store the user's plaintext credentials in memory.
- This mitigates credential theft from a compromised server, but it also enables **Pass-the-Hash against the RDP protocol itself**: an NT hash becomes sufficient to authenticate interactively.

- With Restricted Admin Mode enabled on the target and an NT hash in hand, authenticate with `xfreerdp` ([[Pass-the-Hash]]):

```bash
xfreerdp /v:10.10.11.5 /u:Administrator /pth:2b576acfd5e0c865136732c44b49b6b1 /restricted-admin /cert:ignore
```

- Enabling Restricted Admin Mode on a target requires existing administrative access and a registry change:

```powershell
reg add HKLM\System\CurrentControlSet\Control\Lsa /t REG_DWORD /v DisableRestrictedAdmin /d 0x0 /f
```

- Setting `DisableRestrictedAdmin` to `0` *enables* Restricted Admin Mode. Once set, authentication with an NT hash is accepted in place of a password.


## References and further reading

- [`Remote Desktop Protocol — Wikipedia`](https://en.wikipedia.org/wiki/Remote_Desktop_Protocol)
- [`Understanding the Remote Desktop Protocol — Microsoft Learn`](https://learn.microsoft.com/en-us/troubleshoot/windows-server/remote/understanding-remote-desktop-protocol)
- [`xfreerdp — man page`](https://man.archlinux.org/man/extra/freerdp/xfreerdp3.1.en)
- [`mstsc — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/mstsc)
- [`Remote Desktop Penetration Testing (Port 3389) — Hacking Articles`](https://www.hackingarticles.in/remote-desktop-penetration-testing-port-3389/)
- [`3389 - Pentesting RDP — HackTricks`](https://web.archive.org/web/20250802225113/https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-rdp.html)
- [`RDP (Remote Desktop Protocol) — Hackviser`](https://hackviser.com/tactics/pentesting/services/rdp)

>[!todo]- Planned additions
> - RDP session hijacking (post-exploitation).
> - Protocol-level CVEs: `BlueKeep` (`CVE-2019-0708`), `DejaBlue`, `MS12-020` (denial-of-service).
> - Pivoting through RDP.
