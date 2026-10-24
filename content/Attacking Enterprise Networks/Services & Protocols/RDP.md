---
created: 2026-09-22
updated: 2026-10-20
tags:
  - services_n_protocols
---
>[!note] See [[Connecting via RDP]] and [[Privileged remote access]].
## RDP

>**[Remote Desktop Protocol (RDP)](https://en.wikipedia.org/wiki/Remote_Desktop_Protocol)** is a [Microsoft-proprietary](https://learn.microsoft.com/en-us/troubleshoot/windows-server/remote/understanding-remote-desktop-protocol) application-layer protocol that lets a user connect to and control another computer over the network through a graphical session.

- RDP is one of the most commonly used Windows administrative tools. It is installed by default on all Windows versions; on most editions, however, the RDP server (the capability to accept incoming connections) is disabled by default.
- By default, RDP listens on **TCP and UDP port `3389`** and secures sessions with **TLS** and **Network Level Authentication (NLA)**.

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

>[!note] See [[Connecting via RDP]].

## Restricted Admin Mode and Pass-the-Hash attacks

- **Restricted Admin Mode** is an RDP security feature introduced in Windows 8.1 and Server 2012 R2.
- Instead of an interactive logon, the mode forces a **network logon**, so the remote host does not store the user's plaintext credentials in memory.
- This mitigates credential theft from a compromised server, but it also enables **Pass-the-Hash against the RDP protocol itself**: an NT hash becomes sufficient to authenticate interactively.

- With Restricted Admin Mode enabled on the target and an NT hash in hand, authenticate interactively with `xfreerdp /pth /restricted-admin` ([[Pass-the-Hash]], [[Connecting via RDP#Pass-the-Hash]]).
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
