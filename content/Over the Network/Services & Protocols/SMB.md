---
created: 2026-03-29
tags:
  - network_services
  - net_hack
---
## SMB

>**[SMB (Server Message Block)](https://en.wikipedia.org/wiki/Server_Message_Block)** is a network communication protocol that enables shared access to files, printers, serial ports, and other resources between nodes on a network. 

- SMB operates on a **client-server model**: a client sends requests and the server responds based on session context and access control lists.

>[!note] SMB is primarily used in Windows environments, but Linux machines can speak it, too, using [Samba](https://en.wikipedia.org/wiki/Samba_(software)).

>[!interesting] SMB can also be used for inter-process communication (IPC) over a network.
### Shares

SMB introduces a concept of **shares**.

>An **SMB share** is a named resource — a filesystem directory, printer, or IPC endpoint — exported by an SMB server and made accessible to authenticated or unauthenticated clients over a network.

- Each share carries its own ACL (Access Control List), meaning two users connecting to the same server may have completely different access profiles.
- This per-share ACL is layered *on top of the underlying filesystem permissions* (e.g., NTFS); the more restrictive of the two wins.

### Direct SMB vs. SMB over NetBIOS

SMB can run in one of the following two modes:

- **Direct SMB**
	- Modern SMB runs directly over **TCP port `445`** (TCP segments carry SMB messages directly in the payload).
- **SMB over NetBIOS**
	- Older implementations use **SMB over NetBIOS** on **TCP port `139`**. In this case, SMB messages are wrapped inside a NetBIOS session (NetBIOS handshake is needed before any SMB communication).
	- NetBIOS also handles name resolution instead of DNS.
	- UDP ports `137` and `138` handle NetBIOS name and datagram services, respectively.
	- This method is deprecated but is still often supported for backward compatibility.
### SMB session lifecycle

1. **Connection establishment**
	- An SMB client initiates a TCP connection to the server (TCP port `445`). 
	- Both sides negotiate the SMB version to use — the *dialect* — and session parameters. The server picks the highest dialect both parties support.

2. **Authentication**
	- The client presents authentication credentials, and the server verifies them using Kerberos (in Active Directory environments) or NTLM (in workgroups, or as fallback in AD).

3. **Tree connect**
	- The client requests access to a specific share (`\\server\sharename`). 
	- The server issues a Tree ID (TID) and authorizes access using share-level ACLs.

4. **Resource operations**
	- The client requests standard file I/O operations (open, read, write, close).
	- Each operation is subject to both NTFS permissions and share permissions (the more restrictive of the two wins).

5. **Session termination**
	- Client sends a logoff; server tears down the session context.

### SMB versions

| Version                         | Introduced with             | Description                                                                                                                                                                                                                                                               |
| ------------------------------- | --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **SMBv1** (`1.0`)               | Windows NT                  | The original SMB protocol.<br>No encryption support for data in transit.<br>Multiple known CVEs, exploited by [EternalBlue](https://en.wikipedia.org/wiki/EternalBlue/)/[WannaCry](https://en.wikipedia.org/wiki/WannaCry_ransomware_attack).<br>Deprecated by Microsoft. |
| **SMBv2** (`2.0`/`2.1`)         | Windows Vista / Server 2008 | Addresses many SMBv1 limitations.<br>Redesigned protocol architecture; reduced attack surface compared to SMBv1.<br>Better hashing algorithms (HMAC-SHA256 for message signing).                                                                                          |
| SMBv3 (SMB `3.0`/`3.1`/`3.1.1`) | Windows 8 / Server 2012     | **End-to-end encryption** support (AES-CCM; AES-256-GCM in Windows 11/Windows Server 2022).<br>Better hashing algorithms (AES-CMAC for integrity checks).<br>Security dialect negotiation (prevents downgrade attacks).                                                   |

> [!note] Nmap often won't tell you the exact SMB dialect on Windows targets — it returns the OS build number instead. Use `crackmapexec` or `smbmap` to identify the exact SMB dialect in use. On Samba (Linux), version information is usually visible in Nmap output directly.

### SMB authentication

SMB supports two access models:

- **User-level authentication**
	- The client must supply a valid username and password to authenticate and establish a session; upon successful authentication, access is governed by share and file-system ACLs.

- **Share-level authentication**
	- Legacy; access to a share is protected by a share-specific password, no per-user identity.

>[!important] Under both authentication levels, the password is sent encrypted. 

Under the hood, SMB delegates actual credential verification to one of two protocols:

- [NTLM](https://en.wikipedia.org/wiki/NTLM) (NT LAN Manager)
	- Challenge-response protocol; vulnerable to replay and downgrade attacks.
	- See [[NTLM_]].
- [Kerberos](https://en.wikipedia.org/wiki/Kerberos_\(protocol\)) 
	- Ticket-based, cryptographically secure; preferred in Active Directory environments.
	- See [[how_Kerberos_works]].

>[!important] SMB can be configuration not to require authentication at all. This is often called a **null session**, similar to FTP's anonymous session.

### Standard administrative shares

Windows automatically creates a set of **hidden administrative shares** (identified by the `$` suffix). These shares are **built-in, can't normally be removed permanently**, and are intended for **remote system management and administration**.

>[!note] The `$` suffix means the share is **hidden from normal browsing**, but it is still fully accessible if you know the name (e.g., via `smbclient`, `net view`, etc.).

- **Disk shares: `C$`, `D$`, `$E`, etc.**
	- Automatically created for **every drive letter** on the system.
	- Correspond to system drives; provide full filesystem access to that drive (e.g., `$C` -> `C:\`).

```bash
smbclient //target/C$ -U admin
```

- **`ADMIN$`**
	- Maps to the **Windows system root directory** (`%SystemRoot%`, usually `C:\Windows`); by default, only accessible to administrators.
	- Primarily used for remote administration, service creation (e.g., PsExec uploads binaries here), and system-level file access.

```bash
smbclient //target/ADMIN$ -U admin
```

- **`IPC$`**
	- Special share used for **inter-process communication (IPC)** via **named pipes**.
	- Doesn't provide filesystem access.
	- Used internally for RPC (Remote Procedure Calls), authentication/session setup, and remote service control (SCM, WMI, etc.).
	- Often accessible in null sessions (depending on configuration) and low-privileged contexts (historically mode permissive).

```bash
smbclient //target/IPC$ -N
```

Other common administrative shares:

| Share      | Description                                                     |
| ---------- | --------------------------------------------------------------- |
| `PRINT$`   | Printer driver directory (`C:\Windows\System32\spool\drivers`). |
| `FAX$`     | Fax service data (if enabled).                                  |
| `SYSVOL`   | Domain controller share (Group Policy, scripts).                |
| `NETLOGON` | Logon scripts for domain users.                                 |

## SMB commands

>[!note]+ SMB clients
>Below are some tools you can use to interact with SMB servers:
>- [`smbclient`](https://www.samba.org/samba/docs/current/man-html/smbclient.1.html)
>- [`CrackMapExec`](https://github.com/byt3bl33d3r/CrackMapExec)
>- [`SMBMap`](https://github.com/ShawnDEvans/smbmap)
>- [`Impacket`](https://github.com/fortra/impacket)
### smbclient

>[`smbclient`](https://www.samba.org/samba/docs/current/man-html/smbclient.1.html) is the most commonly used tool to connect to an SMB server from a Linux machine. It provides an FTP-like interface for direct interaction with SMB shares. 

>**`Smbclient`** is an **open-source** command-line tool that provides SMB/CIFS protocol client functionality, similar to an FTP client.

>[!note]+ Primary `smbclient` use cases
> - Share enumeration
> - File transfers
> - Authentication testing
> - Remove command executions (given appropriate permissions)
> - Interactive shells
> - Automated scripting (supports non-interactive mode)

- Syntax:

```bash
smbcliebt [options] //server/share
```


- Connect to a share:

```bash
smbclient //<target>/<share>
```

>[!note] If authentication is required, you'll be prompted for credentials.

- Connect with a username:

```bash
smbclient //<target>/<share> -U username
```

- Connect with username and password:

```bash
smbclient //<target>/<share> -U username%password
```

- Connect anonymously (null session):

```bash
smbclient //<target>/<share> -N
```

- Connect to a share using a specific domain/workgroup:

```bash
smbclient //<target>/<share> -U username -W <domain>
```

- List shares:

```bash
smbclient -L //<target> -U username
```

- List shares anonymously:

```bash
smbclient -L //<target> -N
```

- Run commands (non-interactive):

```bash
smbclient //<target>/<share> -U username -c "cd folder; ls"
```

- Download a file (non-interactive):

```bash
smbclient //<target>/<share> -U username -c "get file.txt"
```

- Upload a file (non-interactive):

```bash
smbclient //<target>/<share> -U username -c "put file.txt"
```
 
#### Command reference

- Navigation & directory management:

| Command      | Description                                      |
| ------------ | ------------------------------------------------ |
| `ls` / `dir` | List files and directories in current remote directory. |
| `cd <dir>`   | Change remote directory.                         |
| `pwd`        | Show current remote directory.                   |
| `lcd <dir>`  | Change local working directory.                  |
| `lpwd`       | Show current local directory.                    |

- File transfers:

| Command                | Description                                      |
| ---------------------- | ------------------------------------------------ |
| `get <remote> [local]` | Download file from server.                       |
| `put <local> [remote]` | Upload file to server.                           |
| `mget <mask>`          | Download multiple files (supports wildcards).    |
| `mput <mask>`          | Upload multiple files.                           |

- File & directory management:

| Command                | Description                                      |
| ---------------------- | ------------------------------------------------ |
| `mkdir <dir>`          | Create directory on server.                      |
| `rmdir <dir>` / `rd`   | Remove directory.                                |
| `rm <mask>`            | Delete file(s).                                  |
| `rename <old> <new>`   | Rename file.                                     |
| `scopy <src> <dst>`    | Server-side file copy (if supported).            |
| `hardlink <src> <dst>` | Create hard link (UNIX extensions).              |

- File information & inspection:

| Command           | Description                                      |
| ----------------- | ------------------------------------------------ |
| `allinfo <file>`  | Show all metadata about a file.                  |
| `stat <file>`     | Show file info (if supported).                   |
| `altname <file>`  | Show 8.3 (DOS) filename.                        |
| `readlink <file>` | Show symlink target.                             |
| `getfacl <file>`  | Get POSIX ACLs (UNIX extensions).               |

- Viewing, printing & output:

| Command        | Description                                      |
| -------------- | ------------------------------------------------ |
| `more <file>`  | View remote file via pager.                      |
| `print <file>` | Send file to remote printer.                     |
| `queue`        | Show print queue.                                |

- Session behavior & environment:

| Command          | Description                                      |
| ---------------- | ------------------------------------------------ |
| `iosize <bytes>` | Set transfer buffer size.                        |
| `blocksize <n>`  | Set tar block size.                              |
| `archive <n>`    | Control archive-bit behavior.                    |
| `backup`         | Toggle backup intent flag.                       |
| `posix`          | Enable or query UNIX extensions.                 |

- Local shell & command execution:

| Command      | Description                                      |
| ------------ | ------------------------------------------------ |
| `! <cmd>`    | Execute local shell command.                     |
| `history`    | Show command history.                            |
| `help` / `?` | Show help or list commands.                      |

- Session control:

| Command                 | Description                                      |
| ----------------------- | ------------------------------------------------ |
| `exit` / `quit` / `bye` | Close session.                                   |

#### Option reference

- Authentication & credentials:

| Option                                  | Description                                               |
| --------------------------------------- | --------------------------------------------------------- |
| `-U`, `--user`                          | Specify the username for authentication (`user%password`). |
| `-N`, `--no-pass`                       | Don't prompt for a password (SMB null sessions).          |
| `--password`                            | Provide password explicitly.                              |
| `--pw-nt-hash`                          | Use an NT hash instead of a password (pass-the-hash).     |
| `-A`, `--authentication-file`           | Read credentials from a file (username/password/domain).  |
| `--use-kerberos=desired\|required\|off` | Use Kerberos authentication (Active Directory).           |
| `-C`, `--use-ccache`                    | Use cached credentials from `winbind`.                    |
| `-W`, `--workgroup`                     | Specify domain or workgroup.                              |

>[!note] User credentials are specified in the form `[domain/]username[%password]`.

- Target selection & connection:

| Option               | Description                                      |
| -------------------- | ------------------------------------------------ |
| `-L`, `--list`       | List available shares on a server.               |
| `-I`, `--ip-address` | Use a specific IP address to connect to.         |
| `-p`, `--port`       | Specify port number to connect to.               |

- Command execution & session behavior:

| Option                 | Description                                      |
| ---------------------- | ------------------------------------------------ |
| `-c`, `--command`      | Execute commands, semicolon-separated.           |
| `-D`, `--directory`    | Change to initial remote directory.              |
| `-g`, `--grepable`     | Produce grepable output.                         |
| `-E`, `--stderr`       | Write messages to `stderr` instead of `stdout`.  |
| `-d`, `--debuglevel`   | Set debug level.                                 |
| `-l`, `--log-basename` | Base directory for logs.                         |

- Security & protocol:

| Option                 | Description                                      |
| ---------------------- | ------------------------------------------------ |
| `-e`, `--encrypt`      | Require encrypted connection.                    |
| `-m`, `--max-protocol` | Set maximum SMB protocol version.                |
| `--option=name=value`  | Override `smb.conf` options.                     |

- File transfer & performance:

| Option                   | Description                              |
| ------------------------ | ---------------------------------------- |
| `-b`, `--send-buffer`    | Set transfer buffer size.                |
| `-T`, `--tar`            | Create or extract tar archives over SMB. |
| `-O`, `--socket-options` | Set TCP socket options.                  |


## SMB enumeration

>[!note]+ Tools
>- [`smbclient`](https://www.samba.org/samba/docs/current/man-html/smbclient.1.html)
>- [`smbmap`](https://github.com/ShawnDEvans/smbmap)
>- `rcpclient`

### Nmap port scanning and version detection

- Check default FTP ports and run version scan:

```bash
sudo nmap -sV -p 137-139,445 <target>
```

> [!tip]+
> - Basic port scanning + version detection — in case you suspect non-standard ports:
> 
> ```bash
> sudo nmap -sV -p- <target>
> ```

>[!warning] Depending on the SMB implementation and the underlying operating system, Nmap will return different information. 
>- When targeting Windows, SMB version information is usually not included as part of Nmap scan results.

- Run default SMB scripts:

```bash
sudo nmap -sV -sC -p 137-139,445 <target>
```

>[!example]- Example: SMB Nmap scan
> 
> ```bash
> sudo nmap -sC -sV 10.129.203.6
> ```
> 
> ```bash
> Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-09-16 08:42 CDT
> Nmap scan report for 10.129.203.6
> Host is up (0.076s latency).
> Not shown: 995 closed tcp ports (reset)
> PORT     STATE SERVICE     VERSION
> # ...
> 139/tcp  open  netbios-ssn Samba smbd 4.6.2
> 445/tcp  open  netbios-ssn Samba smbd 4.6.2
> # ...
> 
> Host script results:
> |_nbstat: NetBIOS name: ATTCSVC-LINUX, NetBIOS user: <unknown>, NetBIOS MAC: <unknown> (unknown)
> | smb2-time: 
> |   date: 2025-09-16T13:43:11
> |_  start_date: N/A
> | smb2-security-mode: 
> |   3:1:1: 
> |_    Message signing enabled but not required
> 
> Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
> Nmap done: 1 IP address (1 host up) scanned in 67.56 seconds
> ```

>[!note]+ "Message signing enabled but not required"
>SMB signing being enabled but not required means the server _supports_ signing but doesn't _enforce_ it — requests can be sent unsigned; vulnerable to **SMB relay attacks**.

- Execute all Nmap scripts relevant to SMB:

```bash
nmap --script smb* <target>
```


>[!tip]+ Nmap SMB scripts
> 
> - List Nmap scripts for SMB:
> 
> ```bash
> ls -l /usr/share/nmap/scripts/*smb*
> ```
> 

- User enumeration:

```bash
nmap --script smb-enum-shares -p 139,445 <target>
```

### Enumerating shares

- List shares anonymously:

```bash
smbclient -L //<target> -U anonymous
```

```bash
smbmap -H <target>
```

- Nmap [`smb-enum-shares`](https://nmap.org/nsedoc/scripts/smb-enum-shares.html) script:

```bash
nmap -p 445 --script=smb-enum-shares <target>
```

- List shares with credentials:

```bash
smbclient -L //<target> -U username%password
```

```bash
smbmap -H <target> -u username -p password
```

```bash
crackmapexec smb 192.168.1.11 -u USERNAME -p PASSWORD --shares
```

>[!example]-
> ```bash
> crackmapexec smb 10.129.203.6 -u '' -p '' --shares
> ```
> 
> ```bash
> SMB         10.129.234.211  445    DEVSMB           [*] Windows 6.1 Build 0 (name:DEVSMB) (domain:) (signing:False) (SMBv1:False)
> SMB         10.129.234.211  445    DEVSMB           [+] \: 
> SMB         10.129.234.211  445    DEVSMB           [*] Enumerated shares
> SMB         10.129.234.211  445    DEVSMB           Share           Permissions     Remark
> SMB         10.129.234.211  445    DEVSMB           -----           -----------     ------
> SMB         10.129.234.211  445    DEVSMB           print$                          Printer Drivers
> SMB         10.129.234.211  445    DEVSMB           sambashare      READ            InFreight SMB v3.1
> SMB         10.129.234.211  445    DEVSMB           IPC$                            IPC Service (InlaneFreight SMB server (Samba, Ubuntu))
> ```

- Recursive enumeration:

```bash
smbmap -H <target> -u "username" -p "password" -r
```

### Enumerating users, groups, and domains

- Username enumeration:

```bash
enum4linux -U <target>
```

- Nmap [`smb-enum-users`](https://nmap.org/nsedoc/scripts/smb-enum-users.html) script:

```bash
nmap -p 445 --script=smb-enum-users <target>
```

- Group enumeration:

```bash
enum4linux -G <target>
```

- Nmap [`smb-enum-groups`](https://nmap.org/nsedoc/scripts/smb-enum-groups.html)  and [`smb-enum-domains`](https://nmap.org/nsedoc/scripts/smb-enum-domains.html) scripts:

```bash
nmap -p 445 --script=smb-enum-groups,smb-enum-domains <target>
```

- Password policy:

```bash
enum4linux -P <target>
```

- Security settings (Nmap [`smb-security-mode`](https://nmap.org/nsedoc/scripts/smb-security-mode.html) script):

```bash
nmap -p 445 --script=smb-security-mode <target>
```

>[!example]- Example: SMB Nmap scan
> 
> ```bash
> sudo nmap -sC -sV 10.129.203.6
> ```
> 
> ```bash
> Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-09-16 08:42 CDT
> Nmap scan report for 10.129.203.6
> Host is up (0.076s latency).
> Not shown: 995 closed tcp ports (reset)
> PORT     STATE SERVICE     VERSION
> # ...
> 139/tcp  open  netbios-ssn Samba smbd 4.6.2
> 445/tcp  open  netbios-ssn Samba smbd 4.6.2
> # ...
> 
> Host script results:
> |_nbstat: NetBIOS name: ATTCSVC-LINUX, NetBIOS user: <unknown>, NetBIOS MAC: <unknown> (unknown)
> | smb2-time: 
> |   date: 2025-09-16T13:43:11
> |_  start_date: N/A
> | smb2-security-mode: 
> |   3:1:1: 
> |_    Message signing enabled but not required
> 
> Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
> Nmap done: 1 IP address (1 host up) scanned in 67.56 seconds
> ```

### smbmap

>[`smbmap`](https://github.com/ShawnDEvans/smbmap) is a tool designed for detailed SMB enumeration across large networks. 

- Basic share enumeration (null session):

```bash
smbmap -H <target>
```

- Authenticated enumeration:

```bash
smbmap -H <target> -u username -p password
```

- Specify a domain:

```bash
smbmap -H <target> -u username -p password -d DOMAIN
```

> [!example]+ Example: SMB share enumeration
> ```bash
> smbmap -H 10.129.203.6
> ```
> 
> ```bash
> [+] IP: 10.129.203.6:445	Name: 10.129.203.6                                      
>      Disk                Permissions  Comment
> 	----                 -----------  -------
> 	print$               NO ACCESS    Printer Drivers
> 	GGJ                  READ ONLY    Priv
> 	IPC$                 NO ACCESS    IPC Service (attcsvc-linux Samba)
> ```

>[!note] `Permissions` column
> - `READ ONLY`: You can browse the share and download files.
> - `READ, WRITE`: You can browse the share, download and upload files.
> - `NO ACCESS`: Means exactly that.


- Use NT has instead of a password ([[Pass-the-Hash]]):

```bash
smbmap -H <target> -u username -p 'LMHASH:NTHASH'
```

- List all files in a share recursively:

```bash
smbmap -H <target> -s <share> -r
```

>[!example]+ Example: Recursive file listing in an SMB share 
> 
> ```bash
> smbmap -H 10.129.203.6 -s GGJ -r
> ```
> 
> ```bash
> [+] IP: 10.129.203.6:445	Name: 10.129.203.6                                      
>         Disk                                                  	Permissions	Comment
> 	----                                                  	-----------	-------
> 	print$                                            	NO ACCESS	Printer Drivers
> 	GGJ                                               	READ ONLY	Priv
> 	.\GGJ\*
> 	dr--r--r--                0 Tue Apr 19 16:33:55 2022	.
> 	dr--r--r--                0 Mon Apr 18 12:08:30 2022	..
> 	fr--r--r--             3381 Tue Apr 19 16:33:03 2022	id_rsa
> 	IPC$                                              	NO ACCESS	IPC Service (attcsvc-linux Samba)
> ```

- List files recursively in all shares, with credentials:

```bash
smbmap -H <target> -u username -p password -r
```

- Download a file:

```bash
smbmap -H <target> -s <share> --download '<share>\filename'
```

>[!example]+ Example: Download file from an SMB share
> 
> ```bash
> smbmap -H 10.129.203.6 -s GGJ -u 'jason' -p '34c8zuNBo91!@28Bszh' --download 'GGJ\id_rsa'
> ```
> 
> ```bash
> [+] Starting download: GGJ\id_rsa (3381 bytes)
> [+] File output to: /home/htb-ac-1908986/10.129.203.6-GGJ_id_rsa
> ```

- Upload a file:

```bash
smbmap -H <target> -s <share> --upload /local/path/file.txt '<share>\file.txt'
```

- Delete a remote file:

```bash
smbmap -H <target> --delete '<share>\file.txt'
```

- Execute a command (requires admin-level access):

```bash
smbmap -H <target> -u username -p password -x 'whoami'
```

- List all drives (requires admin access):

```bash
smbmap -H <target> -u username -p password -L
```
#### Option reference

- Connection:

| Option        | Description                                           |
| ------------- | ----------------------------------------------------- |
| `-H`          | Target IP address or FQDN.                            |
| `--host-file` | File containing a list of hosts to connect to.        |
| `-s`          | Specify a share (default: `C$`).                      |
| `-d`          | Specify a domain name (default: `WORKGROUP`).         |
| `-P`          | SMB port number (default: `445`).                     |
| `--timeout`   | Set port scan socket timeout (default: `.5` seconds). |

- Authentication:

| Option             | Description                                               |
| ------------------ | --------------------------------------------------------- |
| `-u`, `--username` | Username; if omitted, null session assumed.               |
| `-p`, `--password` | Password or NT hash; format: `<LM_hash>:<NT_hash>`.       |
| `--prompt`         | Prompt for a password.                                    |
| `-k`, `--kerberos` | Use Kerberos authentication.                              |
| `--no-pass`        | Use CCache file (`export KRB5CCNAME='~/current.ccache'`). |
| `--dc-ip`          | IP address or FQDN of the DC.                             |


- Information gathering:

| Option               | Description                                                                                                                                          |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `-v`, `--version`    | Return the OS version of the remote host.                                                                                                            |
| `--signing`          | Check if host has SMB signing disabled, enabled, or required.                                                                                        |
| `--admin`            | Report if the user is an admin.                                                                                                                      |
| `-L`                 | List all drives on the specified host (requires admin rights).                                                                                       |
| `-r`                 | Recursively list directories and files (no share\path lists the root of ALL shares); e.g., `email/backup`.                                           |
| `--depth`            | Traverse a directory tree to a specific depth (default: `1` (root node)).                                                                            |
| `--exclude <shares>` | Exclude shares from searching and listing, e.g., `--exclude ADMIN$ C$`.                                                                              |
| `-A <pattern>`       | Define a file name pattern (regex) that auto-downloads a file on a match (requires `-r`), case in-sensitive; e.g., `'(web\|global).(asax\|config)'`. |

- Command execution:

| Option   | Description                                                   |
| -------- | ------------------------------------------------------------- |
| `-x`     | Execute a command.                                            |
| `--mode` | Set the execution method, `wmi` or `psexec` (default: `wmi`). |

- File Operations:

| Option                 | Description                   |
| ---------------------- | ----------------------------- |
| `--download <path>`    | Download a file from a share. |
| `--upload <src> <dst>` | Upload a file to the a share. |
| `--delete <path>`      | Delete a remote file.         |


- Output:

| Option         | Description                                                                                                              |
| -------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `--no-banner`  | Do not print banner on top of the output.                                                                                |
| `--no-color`   | Remove color from the output.                                                                                            |
| `--no-update`  | Remove `Working on it` message.                                                                                          |
| `-g <file>`    | Output to a file and a grepable format.                                                                                  |
| `--csv <file>` | Output in a CSV format.                                                                                                  |
| `-q`           | Quiet mode; only show shares you have `read` or `write` on, and suppresses file listing when performing a search (`-A`). |

### enum4linux

> [`enum4linux`](https://www.kali.org/tools/enum4linux/) is a wrapper around Samba utilities (`smbclient`, `rpcclient`, `net`, `nmblookup`) designed for comprehensive SMB/RPC enumeration.

>[!note]+ `enum4linux` can retrieve:
> - Domain and workgroup information.
> - User accounts and RIDs (Relative IDs).
> - Group memberships and descriptions.
> - Share names and permissions.
> - Password policies and account restrictions.
> - OS version and system information.
> - NetBIOS name tables (if used).

- The `-a` flag performs all basic enumeration in one shot:

```bash
enum4linux -a <tartget>
```

- Authenticated enumeration:

```bash
enum4linux -a -u <username> -p <password> <target>
```

- Targeted enumeration:

```bash
enum4linux -U <target>   # Users
enum4linux -S <target>   # Shares
enum4linux -G <target>   # Groups
enum4linux -P <target>   # Password policy
enum4linux -o <target>   # OS information
enum4linux -n <target>   # NetBIOS name table (nmblookup)
enum4linux -r <target>   # RID cycling — enumerate users by brute-forcing RIDs
```
#### Option reference

- Enumerate:

| Option           | Description                                                                                                                      |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `-a`             | Perform all basic enumeration (`-U -S -G -P -r -o -n -i`).<br>Default if no options are provided.                                |
| `-U`             | List users.                                                                                                                      |
| `-M`             | List machines.                                                                                                                   |
| `-S`             | List shares.                                                                                                                     |
| `-G`             | List groups and members.                                                                                                         |
| `-P`             | Get password policy.                                                                                                             |
| `-o`             | Get OS information.                                                                                                              |
| `-i`             | Get printer information.                                                                                                         |
| `-n`             | Run `nmblookup` (NetBIOS name table; similar to `nbtstat`).                                                                      |
| `-s`             | Brute-force share names from a wordlist.                                                                                         |
| `-d`             | Detailed mode (applies to `-U` and `-S`).                                                                                        |
| `-u <username>`  | Username (default: blank).                                                                                                       |
| `-p <password>`  | Password (default: blank).                                                                                                       |
| `-w <workgroup>` | Specify workgroup manually (usually found automatically).                                                                        |
| `-v`             | Verbose output (show full commands being run).                                                                                   |
| `-A`             | Aggressive mode (perform write checks on shares, etc.).                                                                          |
| `-r`             | Enumerate users via RID cycling.                                                                                                 |
| `-R`             | RID ranges to enumerate.                                                                                                         |
| `-k`             | Users that exist on the target system.<br>(default: `administrator`, `guest`, `krbtgt`, `domain admins`, `root`, `bin`, `none`). |
> [!note]+ `enum4linux-ng`
> `enum4linux-ng` is the modern rewrite of `enum4linux` with better output formatting (JSON/YAML support) and improved reliability. Use it if the original hangs or fails. 
> - Syntax is similar
> ```
> enum4linux-ng -A <target>
> ```

### CrackMapExec

> [CrackMapExec (CME)](https://github.com/byt3bl33d3r/CrackMapExec) is a post-exploitation and network assessment tool built for Windows/Active Directory environments. CME automates credential testing, share enumeration, and command execution across multiple hosts simultaneously.

CME is one of the most practical tools in your SMB toolkit. It's fast, noisy , and gives you clear pass/fail output for credential testing across entire subnets.

- Enumerate shares (null session):

```bash
crackmapexec smb <target> -u '' -p '' --shares
```

- Enumerate shares (authenticated):

```bash
crackmapexec smb <target> -u username -p password --shares
```

- Enumerate logged-in users:

```bash
crackmapexec smb <target> -u username -p password --loggedon-users
```

- Enumerate local users:

```bash
crackmapexec smb <target> -u username -p password --users
```

- Enumerate domain groups:

```bash
crackmapexec smb <target> -u username -p password --groups
```

- Get password policy:

```bash
crackmapexec smb <target> -u username -p password --pass-pol
```

- Execute a command (requires admin):

```bash
crackmapexec smb <target> -u username -p password -x 'whoami'
```

```bash
crackmapexec smb <target> -u username -p password -X 'Get-Process' # PowerShell
```

## SMB null sessions

>A **null session** is an unauthenticated SMB connection established with an empty username and password.

>[!note] Null sessions were practically _standard_ on Windows 2000 networks. Microsoft restricted them significantly in Windows XP SP2 and Server 2003, but misonfigurations are still common.

>[!note] Null sessions grant clients access to the `IPC$` share.

- Check for null sessions using `smbclient`:

```bash
smbclient -N -L //<target>
```

```bash
smbclient //<target>/<share> -U anonymous
```

>[!example]+ Example: SMB null session scan with `smbclient`
> ```bash
> smbclient -L //10.129.203.6 -N
> ```
> 
> ```bash
> 	Sharename       Type      Comment
> 	---------       ----      -------
> 	print$          Disk      Printer Drivers
> 	GGJ             Disk      Priv
> 	IPC$            IPC       IPC Service (attcsvc-linux Samba)
> ```

- Nmap [`smb-enum-shares`](https://nmap.org/nsedoc/scripts/smb-enum-shares.html) script (attempts a null session):

```bash
nmap -p 445 --script=smb-enum-shares <target>
```

- Establish a null session using `rpcclient`:

```bash
rpcclient -U '%' <target> 
```

>[!note] See [[#rpcclient]] for a command cheat sheet.
## Brute-forcing credentials

- SMB credentials brute-force using Medusa:

```bash
medusa -M smb -h <target> -u admin -P /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt -e ns
```

>[!note]+ Option breakdown
>- `-M`: Medusa mode (protocol).
>- `-h`: Target host.
>- `-u`: Username to test (`-U` to brute-force usernames, too).
>- `-P`: Password wordlist.
>- `-e n`: Check for empty passwords.
>- `-e s`: Check for passwords matching the username. 

- FTP credentials brute-force using Hydra:

```bash
hydra -l admin -P /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt smb://<target>
```

- Non-standard port:

```bash
hydra -L usernames.txt -P passwords.txt -s 2121 <target> smb
```

>[!note]+ Option breakdown
>- `-l`: Username to test (`-L` to brute-force usernames, too).
>- `-P`: Password wordlist.
>- `-s`: Specify port the target service is listening on.
>- `smb` or `smb://`: Target protocol (SMB).

- Nmap [`smb-brute`](https://nmap.org/nsedoc/scripts/smb-brute.html) script:

```bash
nmap -p 21 --script smb-brute <target>
```

```bash
nmap -p 445 --script smb-brute --script-args userdb=users.txt,passdb=/usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt <target>
```

- Metasploit:

```bash
use auxiliary/scanner/smb/smb_login  
set RHOSTS <target>  
set USER_FILE /path/to/users.txt  
set PASS_FILE /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt
set STOP_ON_SUCCESS true  
exploit
```

- [`CrackMapExec`](https://github.com/byt3bl33d3r/CrackMapExec) (CME):

```bash
crackmapexec smb 192.168.1.11 -u usernames.txt -p /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt --local-auth
```


>[!example]+ Example: Cracking SMB password with CME
> ```bash
> crackmapexec smb 10.129.203.6 -u "jason" -p pws.list --local-auth
> ```
> 
> ```bash
> SMB         10.129.203.6    445    ATTCSVC-LINUX    [*] Windows 6.1 Build 0 (name:ATTCSVC-LINUX) (domain:ATTCSVC-LINUX) (signing:False) (SMBv1:False)
> SMB         10.129.203.6    445    ATTCSVC-LINUX    [-] ATTCSVC-LINUX\jason:liverpool STATUS_LOGON_FAILURE
> SMB         10.129.203.6    445    ATTCSVC-LINUX    [-] ATTCSVC-LINUX\jason:theman STATUS_LOGON_FAILURE
> SMB         10.129.203.6    445    ATTCSVC-LINUX    [-] ATTCSVC-LINUX\jason:bandit STATUS_LOGON_FAILURE
> # ...
> SMB         10.129.203.6    445    ATTCSVC-LINUX    [+] ATTCSVC-LINUX\jason:34c8zuNBo91!@28Bszh 
> ```

>[!tip]+
>By default, CME exits as soon as it finds a successful login. To continue brute-force even after that to find additional users and passwords, add the `--continue-on-success` option to the command.
## RPC Over SMB

> **RPC (Remote Procedure Call)** is a communication protocol that enables a process on one host to execute a procedure on a remote host, abstracting the underlying network transport from the calling application.

> **MS-RPCE (Microsoft Remote Procedure Call Protocol Extensions)** is Microsoft's extension of the DCE/RPC standard that supports RPC transport over SMB named pipes, enabling remote access to Windows management interfaces via standard SMB connections.

- RPC over SMB works by encapsulating **Remote Procedure Call (RPC)** data directly within SMB transactions, specifically using **named pipes** over the hidden **`IPC`$ share**:
	- The client connects to the `IPC$` share on the target server (TCP port `445`) and authenticates (NTLM/Kerberos/null session), then opens a **named pipe** (e.g, `\pipe\samr`). 
	- Once the pipe is open, the client sends SMB Transaction packets that wrap the raw RPC data. 
	- The server strips the SMB wrapper to process the RPC request, executes the operation, and returns the marshalled response through the same pipe mechanism.

- Each named pipe maps to a different Windows service:

| Named pipe        | Service                        | What you can enumerate               |
| ----------------- | ------------------------------ | ------------------------------------ |
| `\\pipe\samr`     | Security Account Manager (SAM) | Users, groups, password policy.      |
| `\\pipe\lsarpc`   | Local Security Authority (LSA) | SIDs, privileges, trusts, policies.  |
| `\\pipe\srvsvc`   | Server Service                 | Shares, sessions, connected users.   |
| `\\pipe\winreg`   | Windows Registry               | Registry keys (if enabled).          |
| `\\pipe\netlogon` | Netlogon Service               | Domain authentication information.   |
| `\\pipe\svcctl`   | Service Control Manager (SCM)  | Create/start services (remote exec). |

- Pipes are accessible via:

```
\\target\IPC$\PIPE\<pipe>
```

- Some pipes allow **anonymous/null session access** (depending on configuration), others require **authenticated or administrative privileges**.

### rpcclient

>`rpcclient` is a **Samba tool** that provides direct access to **RPC interfaces over SMB named pipes**.

- Connect using a null session (anonymous):

```bash
rpcclient -U '%' <target>
```

- Connect with credentials:

```bash
rpcclient -U 'username%password' <target>
```

#### Command reference

- Domain & server commands:

| Command        | Description                                                 |
| -------------- | ----------------------------------------------------------- |
| `srvinfo`      | Server information: OS version, platform ID, server type.   |
| `querydominfo` | Domain info: name, user count, lockout policy, server role. |
| `getdompwinfo` | Password policy.                                            |

>[!example]- Example: `srvinfo`
> ```bash
> rpcclient $> srvinfo
> ```
> ```bash
> 	DEVSMB         Wk Sv PrQ Unx NT SNT InlaneFreight SMB server (Samba, Ubuntu)
> 	platform_id     :	500
> 	os version      :	6.1
> 	server type     :	0x809a03
> ```

>[!example]- Example: `querydominfo`
> ```bash
> rpcclient $> querydominfo
> ```
> 
> ```bash
> Domain:		DEVOPS
> Server:		DEVSMB
> Comment:	InlaneFreight SMB server (Samba, Ubuntu)
> Total Users:	0
> Total Groups:	0
> Total Aliases:	0
> Sequence No:	1758529521
> Force Logoff:	-1
> Domain Server State:	0x1
> Server Role:	ROLE_DOMAIN_PDC
> Unknown 3:	0x1
> ```

- User enumeration:

| Command           | Description                              |
| ----------------- | ---------------------------------------- |
| `enumdomusers`    | List all users (RID + username).         |
| `queryuser <RID>` | Detailed info on a specific user by RID. |
| `querydispinfo`   | User list with descriptions.             |
- Group enumeration:

| Command            | Description                                      |
| ------------------ | ------------------------------------------------ |
| `enumdomgroups`    | List domain groups.                              |
| `querygroup <RID>` | Detailed information on a specific group by RID. |

- SID & identity mapping:

| Command              | Description                  |
| -------------------- | ---------------------------- |
| `lsaenumsid`         | Enumerate SIDs.              |
| `lookupsids <SID>`   | Resolve a SID to a username. |
| `lookupnames <name>` | Resolve a username to a SID. |

- Share enumeration:

| Command                   | Description                               |
| ------------------------- | ----------------------------------------- |
| `netshareenumall`         | List all shares.                          |
| `netsharegetinfo <share>` | Detailed information on a specific share. |

>[!example]- Example: `netshareenumall`
> 
> ```bash
> rpcclient $> netshareenumall
> ```
> 
> ```bash
> netname: print$
> 	remark:	Printer Drivers
> 	path:	C:\var\lib\samba\printers
> 	password:	
> netname: sambashare
> 	remark:	InFreight SMB v3.1
> 	path:	C:\home\sambauser\
> 	password:	
> netname: IPC$
> 	remark:	IPC Service (InlaneFreight SMB server (Samba, Ubuntu))
> 	path:	C:\tmp
> 	password:
> ```

For a complete list of `rpcclient` commands, see:
- [`rpclient man page`](https://www.samba.org/samba/docs/current/man-html/rpcclient.1.html)
- [`SMB Access from Linux Cheat Sheet`](https://www.willhackforsushi.com/sec504/SMB-Access-from-Linux.pdf)

## References and further reading

- [`A Little Guide to SMB Enumeration — Hacking Articles`](https://www.hackingarticles.in/a-little-guide-to-smb-enumeration/)

- [`Microsoft SMB Protocol Authentication — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/fileio/microsoft-smb-protocol-authentication)
- [`What is the Server Message Block (SMB) protocol?`](https://www.techtarget.com/searchnetworking/definition/Server-Message-Block-Protocol)
- [`Server Message Block — Wikipedia`](https://en.wikipedia.org/wiki/Server_Message_Block)
- [`Samba — Wikipedia`](https://en.wikipedia.org/wiki/Samba_(software))

- [`Pass the hash — Wikipedia`](https://en.wikipedia.org/wiki/Pass_the_hash)
- [`NTLM — Wikipedia`](https://en.wikipedia.org/wiki/NTLM)

- [`SMB (Server Message Block) — Hackviser`](https://hackviser.com/tactics/pentesting/services/smb)

- [`Smbclient — Hackviser`](https://hackviser.com/tactics/tools/smbclient)
- [`Rpcclient — Hackviser`](https://hackviser.com/tactics/tools/rpcclient)
- [`rpclient man page`](https://www.samba.org/samba/docs/current/man-html/rpcclient.1.html)
- [`SMB Access from Linux Cheat Sheet`](https://www.willhackforsushi.com/sec504/SMB-Access-from-Linux.pdf)



## Appendix A: Tools


| Command         | Description                               | Usage                                     |
| --------------- | ----------------------------------------- | ----------------------------------------- |
| `smbclient`     | Connect to an SMB/CIFS server             | `smbclient //server/share`                |
| `smbget`        | Download files from an SMB/CIFS server    | `smbget smb://server/share/file`          |
| `smbpasswd`     | Change a user's SMB password              | `smbpasswd -r server -U username`         |
| `smbstatus`     | Display information about SMB connections | `smbstatus`                               |
| `smbtree`       | List SMB/CIFS shares on a network         | `smbtree`                                 |
| `mount -t cifs` | Mount an SMB/CIFS share                   | `mount -t cifs //server/share /mnt/point` |
| `umount`        | Unmount an SMB/CIFS share                 | `umount /mnt/point`                       |
