---
created: 2026-07-20
tags:
  - Windows
status: draft
---
## RDP

- To connect to an RDP server from a Linux system, you can use [`xfreerdp`](https://www.freerdp.com/) or [`Remmina`](https://remmina.org/) (GUI). Alternatively, you can use an older [`rdesktop`](http://www.rdesktop.org/).

>[!note] See [`xfreerdp`](https://man.archlinux.org/man/extra/freerdp/xfreerdp3.1.en) and [`rdesktop`](https://man.archlinux.org/man/rdesktop.1) man pages. 
### `xfreerdp`

- Connect to a Windows system:

```bash
xfreerdp /v:<ip_address> /u:<username> /p:<password>
```

- Connect with audio output redirection:

```bash
xfreerdp /v:<ip_address> /u:<username> /p:<password> /sound:sys:alsa
```

- Dynamic resolution:

```bash
xfreerdp /v:<ip_address> /u:<username> /p:<password> /dynamic-resolution
```

- Clipboard redirection:

```bash
xfreerdp /v:<ip_address> /u:<username> /p:<password> +clipboard
```

- Ignore any certificate checks:

```bash
xfreerdp /v:<ip_address> /u:<username> /p:<password> /cert:ignore
```

- Connection & authentication:

| Option               | Description                                                                                                                    |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `/v:<server>[:port]` | Target server hostname, IP, or URL (required).                                                                                 |
| `/u:<username>`      | Username for authentication.                                                                                                   |
| `/p:<password>`      | Password (consider `/from-stdin`).                                                                                             |
| `/d:<domain>`        | Domain name.                                                                                                                   |
| `/port:<number>`     | Server port (default: `3389`).                                                                                                 |
| `/from-stdin`        | Read credentials from `stdin`.<br>With `/from-stdin:force`, the prompt appears before connection, otherwise on server request. |
| `/pth:<NTLM-hash>`   | Pass-the-Hash (restricted admin mode).                                                                                         |
| `/cert:ignore`       | Ignore certificate validation.                                                                                                 |

- Display & window:

| Option                                     | Description                                      |
| ------------------------------------------ | ------------------------------------------------ |
| `/f`                                       | Full screen mode (toggle with `Ctrl+Alt+Enter`). |
| `/w:width`                                 | Screen width (default: `1024`).                  |
| `/h:height`                                | Screen height (default `768`).                   |
| `/size:<width>x<height>`<br>or `/size:50%` | Screen size (e.g. `1024x768` or percent).        |
| `/smart-sizing`                            | Scale remote desktop to window size.             |
| `/scale:100\|140\|180`                     | Display scaling factor.                          |
| `/dynamic-resolution`                      | Update resolution on window resize.              |
| `/multimon[:force]`                        | Use multiple monitors.                           |
| `/workarea`                                | Use available work area.                         |
| `/window-position:xxy`                     | Set initial window position.                     |

- Redirection (drives, clipboard, etc.):

| Option                           | Description                                                       |
| -------------------------------- | ----------------------------------------------------------------- |
| `+clipboard`                     | Enable clipboard redirection (use `-clipboard` to disable).       |
| `/drive:<name>,<path>`           | Redirect local directory as share (e.g. `/drive:home,/home/user`) |
| `+drives`                        | Redirect all local drives/mount points.                           |
| `/sound` or `/audio`             | Audio output redirection (e.g., `/sound:sys:alsa`).               |
| `/microphone` or `/mic`          | Microphone (input) redirection.                                   |
| `/usb:id:vid:pid` or `/usb:auto` | USB device redirection.                                           |
| `/smartcard`                     | Smartcard redirection.                                            |




- Windows supports RDP natively — just double-clicking on an `.rdp` file in File Explorer starts up a connection. From CLI, you can use [`mstsc`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/mstsc).
- 

## References and further reading

- [`xfreerdp — TLDR pages`](https://www.cheat-sheets.org/project/tldr/command/xfreerdp/os/linux/)