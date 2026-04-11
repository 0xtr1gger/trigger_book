---
created: 2026-04-08
---
## WinRM

>**[WinRM (Windows Remote Management)](https://learn.microsoft.com/en-us/windows/win32/winrm/portal)** is Microsoft's implementation of the DMTF WS-Management (WS-Man) protocol — a SOAP-based protocol built on HTTP(S) and used for exchanging management information across IT infrastructure. WinRM provides an HTTP-based interface to WMI operations, which can be used for remote command execution, configuration management, and PowerShell remoting on Windows systems.

- Think of WinRM as SSH for Windows administrators. It's deeply integrated into modern Windows environments, built into every Windows Server installation since 2008 R2, and actively used by sysadmins, automation tools (Ansible, Chef, Puppet), and DevOps pipelines. It's everywhere.

> **WS-Management (WS-Man)** is an DMTF standard that specifies a SOAP-based protocol for the managing devices, applications, and web services. It defines a common way to access and exchange management information across different vendor implementations using standard HTTP/HTTPS transport.

>[!important] By default, WinRM listens on TCP port `5985` for HTTP connections and on TCP port `5986` for HTTPS connections.

- WinRM supports NTLM, Kerberos, Basic (insecure) and `CredSSP` authentication.

> [!note] WinRM doesn't transmit plaintext credentials on port `5985` — NTLM still hashes them. But the absence of TLS means the entire SOAP payload (commands, output, files) travels unencrypted and is trivially captured by a man-in-the-middle.

>[!interesting]+ WinRM connection process — in a nutshell
> 
> 1. The client sends an HTTP `POST` to `/wsman` (e.g., `http://<target>:5985/wsman`).
> 2. The server responds with a `401 Unauthorized` and an `WWW-Authenticate` header advertising supported authentication schemes (NTLM, Kerberos, etc.).
> 3. The client performs authentication negotiation (e.g., NTLM challenge-response, or Kerberos ticket exchange).
> 4. Once authenticated, a WinRM **shell** resource is created (`ResourceURI: http://schemas.microsoft.com/wbem/wsman/1/windows/shell/cmd`).
> 5. Commands are issued as SOAP messages (`<rsp:CommandLine>`) and responses come back as XML.
> 6. PowerShell Remoting (`PSRemoting`) wraps this further using the **PSRP** (PowerShell Remoting Protocol) on top of WS-Man. It uses a serialization layer to transmit full .NET objects, not just text output  (this is why `Enter-PSSession` gives you a richer experience than a raw shell).
>
>>[!note] On the target, the session is handled by `wsmprovhost.exe`. Each `PSRemoting` session spawns a new `wsmprovhost` process.

## Enumeration

### Nmap scanning

- Check default WinRM ports and run version scan:

```bash
sudo nmap -sV -p 5985,5986 <target>
```

> [!tip]+
> - Basic port scanning + version detection — in case you suspect non-standard ports:
> 
> ```bash
> sudo nmap -sV -p- <target>
> ```

### Testing if WinRM is configured

- From a Windows machine, you can directly probe a target using built-in tools:

```powershell
Test-WSMan <target>
```
## `evil-winrm`

>[`evil-winrm`](https://github.com/Hackplayers/evil-winrm) is the primary tool for interacting with WinRM from a Linux machine. It supports plaintext passwords, NT hashes, Kerberos tickets, and SSL certificates. Beyond a basic shell, it provides file upload/download, PowerShell module loading, AMSI bypass, and script execution built into the session.

### Connecting

- Basic connection:

```bash
evil-winrm -i <target> -u <username> -p <password>
```

- With a domain account:

```bash
evil-winrm -i <target> -u <username> -p <password>
```

- Over HTTPS (port `5986`):

```bash
evil-winrm -i <target> -u <username> -p <password> -S
```

- Supply a client certificate and private key to authenticate with a certificate:

```bash
evil-winrm -i <target> -u <username> -S -c /path/to/cert.pem -k /path/to/key.pem
```

### Pass-the-Hash

- Hash instead of a password:

```bash
evil-winrm -i <target> -u <username> -H <NT_hash>
```

- Specify a domain:

```bash
evil-winrm -i <target> -u <username> -H <NT_hash> -d <domain>
```

>[!note] See [[Pass-the-Hash]].
### Kerberos authentication

In domain environments, WinRM supports Kerberos ticket authentication:

1. Export your ticket to a file and set the `KRB5CCNAME` environment variable:

```bash
export KRB5CCNAME=/path/to/ticket.ccache
```

2. Connect using the hostname (not IP address — Kerberos requires it):

```bash
evil-winrm -i <target_hostname> -u <username> -r <domain>
```

> [!note]+ If needed, add the hostname to `/etc/hosts`
> ```bash
> echo "<target> <target_hostname>.<domain>" >> /etc/hosts
> ```
### File download and upload

- Upload a file to the remote server:

```bash
upload /path/to/local/file.exe C:\Windows\Temp\file.exe
```

- Download a file from the server:

```bash
download C:\Windows\Temp\output.txt /tmp/output.txt
```

Without a destination path, the file downloads to the current local directory.
## References and further reading


- [`WinRM (Windows Remote Management`](https://hackviser.com/tactics/pentesting/services/winrm)
- [`5985,5986 - Pentesting WinRM`](https://hacktricks.wiki/en/network-services-pentesting/5985-5986-pentesting-winrm.html)
- [`WinRM Penetration Testing — Hacking Articles`](https://www.hackingarticles.in/winrm-penetration-testing/)

- [`Windows Remote Management — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/winrm/portal)
- [`WS-Management Protocol — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/winrm/ws-management-protocol)
- [`SOAP — Wikipedia`](https://en.wikipedia.org/wiki/SOAP)
- [`ecil-winrm — Ful WinRM Shell Usage Guide — HackIndex`](https://hackindex.io/services/winrm/exploitation/evil-winrm)


- [`WinRM (Windows Remote Management) — Hackviser`](https://hackviser.com/tactics/pentesting/services/winrm)