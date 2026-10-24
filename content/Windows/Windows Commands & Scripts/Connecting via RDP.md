---
created: 2026-10-19
updated: 2026-10-20
tags:
  - Windows
---
## RDP

>**[Remote Desktop Protocol (RDP)](https://learn.microsoft.com/en-us/troubleshoot/windows-server/remote/understanding-remote-desktop-protocol)** is a Microsoft-proprietary application-layer protocol that provides an interactive graphical session with a remote computer over the network.

- RDP follows a **client-server model**: the client initiates the connection and renders the remote graphical session locally, while the server — the Windows host — accepts the connection and serves the session.
- RDP is installed by default on all Windows versions, but on most editions the RDP server (the capability to accept incoming connections) is disabled by default.
- It is based on the ITU-T T.128 application-sharing standard. A single connection multiplexes several **virtual channels**, and each carries a distinct feature: display, keyboard and mouse input, clipboard, audio, printer, and drive redirection.
- Beyond screen, keyboard, and mouse, RDP supports:
	- **Clipboard sharing** — bidirectional copy-paste between client and server.
	- **Drive redirection** — mount local directories as network shares inside the remote session.
	- **Printer redirection** — print from the remote session to a local printer.
	- **Port redirection** — tunnel arbitrary TCP connections through the RDP session.
	- **Audio redirection** — play remote audio locally, or forward the local microphone to the server.
	- **32-bit color and dynamic resolution.**

>[!important]+ By default, RDP listens on **TCP port `3389`**.
>- Starting with RDP 8.0 (Windows 8 / Server 2012), **UDP port `3389`** is also supported for performance acceleration.
>- When both are available, **RDP prefers UDP** and falls back to TCP on failure.

### RDP ports

| Port       | Protocol  | Description                                                                              |
| ---------- | --------- | --------------------------------------------------------------------------------------- |
| `3389/tcp` | RDP (TCP) | **Default RDP listener**, secured with TLS and Network Level Authentication (NLA).       |
| `3389/udp` | RDP (UDP) | **Performance-acceleration transport** (RDP 8.0+); RDP prefers it and falls back to TCP. |

### Authentication and NLA

>**[Network Level Authentication (NLA)](https://en.wikipedia.org/wiki/Remote_Desktop_Services#Network_Level_Authentication)** is an RDP security feature that requires the user to authenticate before a remote desktop session is established.

- Modern RDP sessions are secured with **TLS** and **NLA**.
- With NLA, the server verifies the user's credentials through the **[Credential Security Support Provider (`CredSSP`)](https://learn.microsoft.com/en-us/windows/win32/secauthn/credential-security-support-provider)** protocol during the initial connection negotiation, before any session is served. This prevents the login screen from loading for unauthenticated attempts and ensures that only authenticated users reach the remote host.

>[!note] Before NLA, connecting to an RDP server loaded a full Windows login screen, so the server rendered a graphical session for *every incoming connection*, authenticated or not. This was exploitable (denial-of-service, [BlueKeep](https://en.wikipedia.org/wiki/BlueKeep)), and NLA was Microsoft's mitigation. NLA is enabled by default on Windows Vista / Server 2008 and later.

>[!note]+ Besides `CredSSP`, RDP can authenticate with:
> - **Kerberos** — on domain-joined hosts when a KDC is reachable.
> - **NTLM** — the fallback when Kerberos is unavailable; used for workgroup machines or cross-domain connections.
> - **Local accounts** — on standalone, workgroup hosts.

>[!important] The **`Remote Desktop Users` group** is a built-in Windows security group that grants members the right to **log on remotely** via RDP. By default, only members of the **`Administrators`** and **`Remote Desktop Users`** groups can log on through RDP.

- To connect from Linux, use [`xfreerdp`](https://www.freerdp.com/) (CLI), [`Remmina`](https://remmina.org/) (GUI), or the older [`rdesktop`](http://www.rdesktop.org/).
- Windows supports RDP natively: double-clicking an `.rdp` file in File Explorer starts a connection, and [`mstsc`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/mstsc) is the built-in command-line client.

## `xfreerdp`

>[`xfreerdp`](https://www.freerdp.com/) is an open-source, command-line **Remote Desktop Protocol (RDP)** client for Linux, part of the [FreeRDP](https://github.com/FreeRDP/FreeRDP) project.

- Beyond basic RDP functionality, `xfreerdp` also supports:
	- **Drive redirection** (`/drive:name,path`), **printer redirection** (`/printer`), **smartcard** (`/smartcard`), and **USB device** (`/usb`) passthrough.
	- Shared clipboard (`+clipboard`).
	- **Audio output** (`/sound`) and **microphone input** (`/microphone`) redirection; supports various audio subsystems, including ALSA and PulseAudio.
	- Connecting using [[Pass-the-Hash]] (`/pth`).
	- Skipping certificate validation (`/cert:ignore`).
	- Multi-monitor support (`/multimon`) and full screen support (`/f`).

>[!tip]+ On Wayland, use [`wlfreerdp`](https://manpages.debian.org/testing/freerdp2-wayland/wlfreerdp.1.en.html) instead of `xfreerdp`.

### Connecting via `xfreerdp`

- Connect to a Windows system:

```bash
xfreerdp /v:10.10.11.5 /u:jdoe /p:'passwd123'
```

- Enable dynamic screen resolution (resize the screen with the client window):

```bash
xfreerdp /v:10.10.11.5 /u:jdoe /p:'passwd123' /dynamic-resolution
```

- Ignore certificate validation:

```bash
xfreerdp /v:10.10.11.5 /u:jdoe /p:'passwd123' /dynamic-resolution /cert:ignore
```

### Shared clipboard

- Connect with a shared clipboard:

```bash
xfreerdp /v:10.10.11.5 /u:jdoe /p:'passwd123' +clipboard
```

### Drive redirection

- The `/drive` option enables **drive redirection**, making local files and directories accessible inside the remote RDP session.

```text
/drive:<share_name>,<local_path>
```

- Mount a local directory as a share named `tools`:

```bash
xfreerdp /v:10.10.11.5 /u:jdoe /p:'passwd123' /drive:tools,/home/user/tools
```

![[xfreerdp_drive_redirection.svg]]

- Redirected drives appear under `\\tsclient`:

```powershell
copy \\tsclient\tools\SharpHound.exe C:\Users\jdoe\SharpHound.exe
```

- In File Explorer, redirected shares appear under `This PC` → `Redirected drives and folders`.
- To redirect *all* local drives (potentially risky), use `+drives`:

```bash
xfreerdp /v:10.10.11.5 /u:jdoe /p:'passwd123' +drives
```

>[!note] Do not include a trailing slash in the path (e.g., use `/home/user/tools`, not `/home/user/tools/`), otherwise the share may appear empty.

### Redirecting audio

```bash
/sound[:sys:<backend>,dev:<device>,...]
```

- The `/sound` option enables **audio output redirection**: audio from the remote Windows machine plays on the local Linux machine.
- For example, `/sound:sys:alsa` enables redirection (`/sound`) using the **ALSA backend** (`sys:alsa`).

>[!info]+ Audio backends
> - An **audio backend** on Linux is the software layer that handles audio playback and routing between applications and hardware. 
> - Common backends:
> 	- ALSA (`sys:alsa`) — low-level Linux sound system with direct hardware access.
> 	- PulseAudio (`sys:pulse`) — PulseAudio sound server; the default on Ubuntu, Kali, and similar.
> 	- PipeWire (`sys:pipewire`) — modern replacement for PulseAudio (often compatible via `pulse`).
>- `xfreerdp` chooses PulseAudio by default when it is available.

- Connect with audio output redirection:

```bash
xfreerdp /v:10.10.11.5 /u:jdoe /p:'passwd123' /sound:sys:alsa
```

### Pass-the-Hash

- Connect using Pass-the-Hash in Restricted Admin Mode ([[Pass-the-Hash]]):

```bash
xfreerdp /v:10.10.11.5 /u:Administrator /pth:2b576acfd5e0c865136732c44b49b6b1 /restricted-admin /cert:ignore
```

>[!note] `/pth` requires Restricted Admin Mode to be enabled on the target. See [[RDP#Restricted Admin Mode and Pass-the-Hash attacks]].

- Test credentials against NLA (Network Level Authentication) without opening a graphical window:

```bash
xfreerdp /v:10.10.11.5 /u:jdoe /p:'passwd123' /d:example.com +auth-only /cert:ignore
```

### `xfreerdp` options

- Connection and authentication:

| Option                              | Description                                                                   |
| :---------------------------------- | :---------------------------------------------------------------------------- |
| `/v:server[:port]`                  | Specify the target RDP server hostname, IP address, or URL, with optional port. |
| `/port:port`                        | Set the target port when it is not included in `/v:`.                         |
| `/u:[domain\user\|user@domain]`     | Set the username for authentication.                                          |
| `/p:password`                       | Set the password (alternatively, use `/from-stdin`).                          |
| `/d:domain`                         | Set the authentication domain.                                                |
| `/from-stdin[:force]`               | Read credentials from `stdin`; with `:force`, prompt before connecting.       |
| `/pth:hash`                         | Authenticate with an NT hash (Pass-the-Hash); requires `/restricted-admin`.   |
| `/restricted-admin`                 | Connect in Restricted Admin Mode (no plaintext credentials cached on the server). |
| `/admin`, `/console`                | Connect to the admin (console) session of the server.                         |
| `+auth-only`                        | Authenticate against NLA without opening a graphical window.                  |
| `/auth-pkg-list:`                   | Filter the allowed authentication packages (e.g. `!ntlm,kerberos`).           |
| `+credentials-delegation`           | Enable credential delegation to the server.                                   |

- Display and window:

| Option                      | Description                                        |
| :-------------------------- | :------------------------------------------------- |
| `/f`                        | Start in full-screen mode (toggle with `Ctrl+Alt+Enter`). |
| `/w:width`                  | Set the window width (default `1024`).             |
| `/h:height`                 | Set the window height (default `768`).             |
| `/size:<width>x<height>`    | Set the session size (e.g. `1280x1024` or `/size:90%`). |
| `/smart-sizing`             | Scale the remote desktop to the window size.       |
| `/scale:100\|140\|180`      | Set the display scaling factor.                    |
| `/dynamic-resolution`       | Update the resolution when the window is resized.  |
| `/multimon[:force]`         | Use multiple monitors.                             |
| `/workarea`                 | Use the available work area instead of the full screen. |
| `/window-position:<x>x<y>`  | Set the initial window position.                   |
| `/bpp:depth`                | Set the color depth in bits per pixel.             |
| `-wallpaper`                | Disable remote wallpaper rendering.                |
| `-themes`                   | Disable remote visual themes.                      |

- Redirection:

| Option                           | Description                                                      |
| :------------------------------- | :--------------------------------------------------------------- |
| `+clipboard`                     | Enable bidirectional clipboard redirection (disable with `-clipboard`). |
| `/clipboard:`                    | Configure clipboard direction and X selection.                  |
| `/drive:<name>,<path>`           | Redirect a local directory as a mapped share (e.g. `/drive:home,/home/user`). |
| `+drives`                        | Redirect all local drives and mount points.                     |
| `/sound[:sys:<backend>]`         | Redirect audio output to the local machine (e.g. `/sound:sys:alsa`). |
| `/microphone`                    | Redirect the local microphone to the server.                    |
| `/usb:id:<vid>:<pid>` or `/usb:auto` | Redirect USB devices by ID or automatically.                |
| `/smartcard`                     | Redirect smartcards.                                            |

- Reliability:

| Option                            | Description                                               |
| :-------------------------------- | :-------------------------------------------------------- |
| `+auto-reconnect`                 | Reconnect automatically on connection loss.              |
| `/auto-reconnect-max-retries:n`   | Set the maximum reconnection attempts (`0` means unlimited). |
| `/timeout:ms`                     | Set the connection timeout for high-latency links.       |

- Security and encryption:

| Option                               | Description                                                                 |
| :----------------------------------- | :-------------------------------------------------------------------------- |
| `/cert:ignore`                       | Ignore certificate validation errors (also `deny`, `tofu`, `name:`, `fingerprint:`). |
| `/encryption-methods:40\|56\|128\|FIPS` | Restrict the allowed standard RDP encryption methods.                    |
| `+fipsmode`                          | Enable FIPS mode.                                                           |
| `/tls:`                              | Configure TLS ciphers, security level, or protocol version.                |

>[!note] See the [`xfreerdp` man page](https://man.archlinux.org/man/extra/freerdp/xfreerdp3.1.en) for the complete option set.


## Connecting via RDP using native Windows tools

- [`mstsc.exe`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/mstsc) (Microsoft Terminal Services Client) is the built-in Windows RDP client. 
- Running `mstsc` with no arguments opens the Remote Desktop Connection GUI; a saved `.rdp` file can be launched directly or opened for editing with `/edit`.

---

- Connect in Restricted Admin Mode:

```powershell
mstsc.exe /v:10.10.11.5 /restrictedAdmin
```

- Connect directly to the console (admin) session:

```powershell
mstsc.exe /v:10.10.11.5 /admin
```

- Start Remote Desktop in full-screen mode:

```powershell
mstsc.exe /v:10.10.11.5 /f
```

| Option             | Description                                                                            |
| :----------------- | :------------------------------------------------------------------------------------- |
| `/v`               | Remote computer and optional port to connect to.                                       |
| `/restrictedAdmin` | Connect in Restricted Admin Mode to prevent credential caching in remote LSASS memory. |
| `/admin`           | Connect to the console session for administering the server.                           |
| `/f`               | Start Remote Desktop in full-screen mode.                                              |
| `/w`               | Set the width of the Remote Desktop window.                                            |
| `/h`               | Set the height of the Remote Desktop window.                                           |
| `/edit`            | Open the specified `.rdp` connection file for editing.                                 |

## Enabling RDP on the target

- Enable RDP server via registry:

```powershell
reg add "HKLM\System\CurrentControlSet\Control\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f
```

- Allow Remote Desktop through the Windows firewall:

```powershell
netsh advfirewall firewall set rule group="remote desktop" new enable=Yes
```

>[!note] To enable Restricted Admin Mode (required for Pass-the-Hash over RDP), see [[RDP#Restricted Admin Mode and Pass-the-Hash attacks]].

## References and further reading

- [`Understanding the Remote Desktop Protocol — Microsoft Learn`](https://learn.microsoft.com/en-us/troubleshoot/windows-server/remote/understanding-remote-desktop-protocol)
- [`Credential Security Support Provider — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/secauthn/credential-security-support-provider)
- [`mstsc — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/mstsc)

---

- [`FreeRDP`](https://www.freerdp.com/)
- [`xfreerdp — man page`](https://man.archlinux.org/man/extra/freerdp/xfreerdp3.1.en)
- [`rdesktop — man page`](https://man.archlinux.org/man/rdesktop.1)
- [`Remmina`](https://remmina.org/)

## Appendix A: `rdesktop`

>[`rdesktop`](http://www.rdesktop.org/) is an older open-source RDP client for Linux. It predates `xfreerdp` and lacks support for some newer RDP features, but it remains available on most distributions.

- Connect to a Windows host:

```bash
rdesktop -u jdoe -p 'passwd123' 10.10.11.5
```

- Enable clipboard redirection and full-screen mode:

```bash
rdesktop -r clipboard:PRIMARYCLIPBOARD -f 10.10.11.5
```

- Redirect a local directory as a share:

```bash
rdesktop -r disk:share=/home/user/tools 10.10.11.5
```

| Option                     | Description                                                   |
| :------------------------- | :----------------------------------------------------------- |
| `-u`                       | Set the username.                                            |
| `-p`                       | Set the password (`-` reads it from `stdin`).               |
| `-d`                       | Set the authentication domain.                              |
| `-g`                       | Set the geometry (`<width>x<height>` or a percentage).      |
| `-f`                       | Start in full-screen mode (toggle with `Ctrl+Alt+Enter`).   |
| `-r clipboard:`            | Redirect the clipboard (`PRIMARYCLIPBOARD` or `CLIPBOARD`). |
| `-r disk:<share>=<path>`   | Redirect a local directory as a share.                      |
| `-r sound:`                | Redirect sound (`local`, `remote`, or `off`).               |
