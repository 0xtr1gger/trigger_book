---
created: 2026-07-30
updated: 2026-09-20
tags:
  - tools
  - AD_attacks
---
## `Responder`

>[`Responder`](https://github.com/lgandx/Responder)  is a LLMNR, NBT-NS, and MDNS poisoning tool with built-in rogue authentication servers for HTTP, SMB, MSSQL, FTP, LDAP, Kerberos, DNS, and more. It supports NTLMv1/NTLMv2/LMv2, Extended Security NTLMSSP, and various authentication methods across 15+ protocols.

>[!note]+ Installation
>```bash
>apt install responder
>```
> See [`Installation — Responder, GitHub`](https://github.com/lgandx/Responder#installation).


## `Responder` configuration 


> [!tip]+
> In environments with heavy monitoring, disable servers for protocols you don't need. Fewer open ports = lower detection surface.

- Located at `/usr/share/responder/Responder.conf`.
- Controls which rogue servers Responder operates and how it listens.

```ini
[Responder Core]
; Set to On/Off for each protocol server
SMB = On
HTTP = On
HTTPS = On
MSSQL = Off
FTP = Off
LDAP = On
```



## Option reference

- Poisoning:

| Option                  | Description                                                             |
| ----------------------- | ----------------------------------------------------------------------- |
| `-I` , `--interface`    | Network interface to use; `ALL` to use all interfaces.                  |
| `-A`, `--analyze`       | Analyze mode; see NBT-NS, MDNS, LLMNR requests without responding.      |
| `-w`, `--wpad`          | Start WPAD rogue proxy server; catches HTTP traffic (default: `off`).   |
| `-F`, `--ForceWpadAuth` | Force NTLM/Basic authentication on `wpad.dat` retrieval (old networks), |
| `-P, --ProxyAuth`       | Force NTLM/Basic authentication for proxy (highly effective).           |

- DHCP/DHCPv6:

| Option             | Description                                                 |
| ------------------ | ----------------------------------------------------------- |
| `-d`, `--DHCP`     | Enable DHCP broadcast responses with WPAD injection (IPv4). |
| `-D`, `--DHCP-DNS` | Inject DNS server in DHCP response instead of WPAD.         |
| `--dhcpv6`         | Enable DHCPv6 poisoning (responds to `SOLICIT` messages).   |

- IP poisoning: 

| Option                | Description                                |
| --------------------- | ------------------------------------------ |
| `-e`, `--externalip`  | Poison requests with another IPv4 address. |
| `-6`, `--externalip6` | Poison requests with another IPv6 address. |
| `-i, --ip`            | Local IP address to use (macOS only).      |

- Authentication:

| Option          | Description                                         |
| --------------- | --------------------------------------------------- |
| `-b`, `--basic` | Return HTTP Basic authentication (default: `NTLM`). |
| `--lm`          | Force LM hashing downgrade (Windows XP/2003).       |
| `--disable-ess` | Force Extended Security NTLMSSP downgrade.          |

- Advanced:

| Option                   | Description                                                           |
| ------------------------ | --------------------------------------------------------------------- |
| `-u`, `--upstream-proxy` | Upstream HTTP proxy for rogue WPAD (`<host>:<port>`).                 |
| `-t`, `--ttl`            | Change Windows TTL for poisoned answers (hex: `30s=1e`, or `random`). |
| `-N, --AnswerName`       | Canonical name for LLMNR answers (useful for Kerberos relay).         |
| `-E`, `--ErrorCode`      | Return `STATUS_LOGON_FAILURE` (enables WebDAV auth capture).          |
- Output:

| Option            | Description                          |
| ----------------- | ------------------------------------ |
| `-v`, `--verbose` | Increase verbosity (recommended).    |
| `-Q`, `--quiet`   | Quiet mode; disable poisoner output. |
- Info:

| Option       | Description                    |
| ------------ | ------------------------------ |
| `--version`  | Show program version and exit. |
| `-h, --help` | Show help message and exit.    |