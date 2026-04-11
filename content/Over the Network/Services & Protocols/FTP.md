---
created: 2026-03-25
tags:
  - network_services
  - over_the_network
color: "linear-gradient(45deg, #23d4fd 0%, #3a98f0 50%, #b721ff 100%)"
---
## FTP

>**FTP (File Transfer Protocol)** is a connection-oriented, application-layer protocol designed for bidirectional file transfers between a client and a server.

>[!note] FTP was originally developed in 1970s, in [`RFC 114`](https://www.rfc-editor.org/rfc/rfc114.html) (1971). The current standard is [`RFC 959`](https://datatracker.ietf.org/doc/html/rfc959).

- FTP supports username-password authentication.
- **No encryption**: all data is sent in **plain text** — including authentication credentials, commands, response codes, and file content.

>[!important] FTP uses **TCP ports `20` and `21`**.

>[!interesting]+ Encrypted FTP alternatives
>FTP has two main encrypted alternatives:
>- **FTPS (FTP Secure)** — an extension of the FTP protocol that wraps the control and data channels in TLS/SSL,either implicitly (dedicated port, usually `990`) or explicitly via the `AUTH TLS` command on port `21`. It is defined in [`RFC 4217`](https://www.rfc-editor.org/rfc/rfc4217).
>- **SFTP (SSH File Transfer Protocol)** — an entirely separate protocol, unrelated to FTP despite the name, built on top of the SSH protocol (TCP port `22`). It provides encrypted file transfer and remote file management using the SSH as a transport.
>
>From a recon standpoint, FTPS still exposes a banner, so you can enumerate it — it just requires `openssl` instead of raw `nc`. SFTP is a different beast and falls under SSH enumeration.
### Control and data connections

FTP splits its communication across **two separate TCP connections**:

- **Control connection** (TCP port `21`)
	- A *persistent* TCP session established on port `21` between client and server.
	- The client sends commands and the server responds with three-digit status codes with an optional text message. 

>[!note] See [`List of FTP commands — Wikipedia`](https://en.wikipedia.org/wiki/List_of_FTP_commands) and [`List of FTP server return codes — Wikipedia`](https://en.wikipedia.org/wiki/List_of_FTP_server_return_codes).

- **Data connection** (usually TCP port `20`)
	- A *transient* TCP session established on-demand for actual file transfer and directory listings. 
	- It's opened when needed and closes immediately after the transfer completes. 
	- The port form used for the data connection depends on the FTP mode; active mode uses port `20`. 

>[!important] The **client listens** for incoming TCP connections from the server on a client-specified port. The server *actively* connects back to the client for data transfers.

### Active and passive modes

FTP also has **two modes of operation**:

- **Active mode** (`PORT`) — the client listens for incoming TCP connections from the server, and the server *actively* connects back to the client for data transfers; default mode.

>[!interesting]- Active connection process
> 
>>[!note] FTP server listens on TCP port `21` (by default) for control connections.
> 
> 1. An **FTP client** opens a **control connection** to the FTP server on **TCP port `21`** to send FTP commands.
> 2. The **FTP client** starts listening on an *arbitrary port* for incoming data connections, and sends the **`PORT` command** with the port number to the server. 
> 3. The **FTP server** initiates a **data connection** from its **TCP port `20`** to the client's specified port.
> 4. Once the data connection is established, data (files, directory listings, etc.) can be transferred from the server to client or vice versa.
> 5. After the transfer is complete, the data connection is closed.
> 

- **Passive mode** (`PASV`) — the server listens for incoming TCP connections on a dynamically allocated port, and the client connects to the server for data transfers.

>[!interesting]- Passive connection process
>>[!note] FTP server listens on TCP port `21` (by default) for control connections.
> 1. An **FTP client** opens a **control connection** to the FTP server on **TCP port `21`** to send FTP commands. 
> 2. The client requests the server to listen for a data connection by sending the `PASV` command.
> 3. The FTP server responds with an IP address and a port number for the client to connect to (dynamic port, usually above `1023`).
> 4. The client then initiates a TCP connection **from its side to the server's specified port**.
> 5. Once the data connection is established, data (files, directory listings, etc.) can be transferred from the server to client or vice versa.
> 6. After the transfer is complete, the data connection is closed.

>[!important] In the passive FTP mode, the TCP port `20` is not used at all.

>[!note]+ FTP mode and firewalls
>- The client not always can accept incoming connections because of firewalls and NAT — in case the FTP server is located in an external network. This is the biggest disadvantage of the active FTP mode.
>- Passive mode was designed to solve this problem: the client doesn't listen for connections, but initiates one instead, which is allowed by firewalls in most cases. This is why today passive mode is used far more often than active.

>[!note] When you connect to an FTP server through a tool like `ftp`, `lftp`, or `ncftp`, passive mode is almost certainly what's being negotiated.

## FTP enumeration

### Nmap scanning
 
- Check default FTP ports and run version scan:

```bash
sudo nmap -sV -p 21 <target>
```

> [!tip]+
> - Basic port scanning + version detection — in case you suspect non-standard ports:
> 
> ```bash
> sudo nmap -sV -p- <target>
> ```

- Run default FTP scripts:

```bash
sudo nmap -sV -sC -p 21 <target>
```

- Run all FTP-related scripts:

```bash
nmap -p 21 --script "ftp-*" <target>
```

>[!tip]+ Nmap FTP scripts
> 
> - List Nmap scripts for FTP:
> 
> ```bash
> ls -l /usr/share/nmap/scripts/*ftp*
> ```
> 

- Nmap FTP scripts:

| Name                                                                                | Categories                                | Description                                                                                              |
| ----------------------------------------------------------------------------------- | ----------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| [`ftp-anon`](https://nmap.org/nsedoc/scripts/ftp-anon.html)                         | `default`, `auth`, `safe`                 | Check if an FTP server allows anonymous logins (attempts to log in with the username `anonymous`).       |
| [`ftp-bounce`](https://nmap.org/nsedoc/scripts/ftp-bounce.html)                     | `default`, `safe`                         | Test if an FTP server is vulnerable to the FTP bounce attack (indirect port scanning through the server) |
| [`ftp-syst`](https://nmap.org/nsedoc/scripts/ftp-syst.html)                         | `default`, `safe`, `discovery`            | Retrieve information about the operating system of the FTP server.                                       |
| [`tftp-enum`](https://nmap.org/nsedoc/scripts/tftp-enum.html)                       | `discovery`, `intrusive`                  | Enumerate TFTP filenames.                                                                                |
| [`ftp-brute`](https://nmap.org/nsedoc/scripts/ftp-brute.html)                       | `intrusive`, `brute`                      | Perform brute force password attack against FTP servers.                                                 |
| [`ftp-libopie`](https://nmap.org/nsedoc/scripts/ftp-libopie.html)                   | `vuln`, `intrusive`                       | Test for the OPIE off-by-one stack overflow attack (`CVE-2010-1938`).                                    |
| [`ftp-proftpd-backdoor`](https://nmap.org/nsedoc/scripts/ftp-proftpd-backdoor.html) | `exploit`, `intrusive`, `malware`, `vuln` | Test for the presence of the ProFTPD 1.3.3c backdoor reported as BID 45150.                              |
| [`ftp-vsftpd-backdoor`](https://nmap.org/nsedoc/scripts/ftp-vsftpd-backdoor.html)   | `exploit`, `intrusive`, `malware`, `vuln` | Test for the presence of the vsFTPd 2.3.4 backdoor reported on 2011-07-04 (`CVE-2011-2523`).             |


- Check for anonymous login and gather information:

```bash
nmap --script ftp-anon,ftp-syst -p 21 <target>
```

- Run all FTP scripts:

```bash
nmap --script ftp* <target>
```

### Banner grabbing

Once an FTP control connection is established, the server returns a banner as a first response. The banner reveals the server software and version — you can use this information to search for known CVEs.

- Connect using Netcat:

```bash
nc -vn <target> 21
```

- Or Telnet:

```bash
telnet <target> 21
```

- If the banner is suppressed or misleading, you can use `SYST` and `STAT` commands to gather information:

```bash
echo "SYST" | nc -w 5 <target> 21
```

```bash
echo "STAT" | nc -w 5 <target> 21
```

- List supported server features, such as FTPS suport, UTF-8, MLSD (Machine Listing Send Directory), EPSV (Extended Passive Mode) / EPRT (Extended Port), etc.:

```bash
echo "FEAT" | nc <target> 21
```

>[!note] See [`FTP Commands and Extensions — IANA`](https://www.iana.org/assignments/ftp-commands-extensions/ftp-commands-extensions.xhtml).

- You can always back to Nmap version scan:

```bash
nmap -sV --version-intensity 9 -p 21 <target>
```

>[!tip]+ FTPS banner
> - Get TLS certificate, if any (for FTPS):
> 
> ```bash
> openssl s_client -connect <target>:21 -starttls ftp
> ```
> 

## Anonymous login

Anonymous FTP login is one of the most common misconfigurations. It was designed as a legitimate feature — for public file distribution, like software mirrors. But in practice it's often left enabled where it shouldn't be.

>Anonymous FTP login allows unauthenticated access to the FTP server, typically using a fixed username such as `anonymous` or `ftp` and an empty password.

- The username is typically `anonymous` or `ftp`.
- Password can be:
	- anything
	- empty
	- email (historical etiquette)

>[!note] During anonymous login, server might ask the client to provide an email address as the password, but it's not actually verified — any string is accepted.

- Attempt anonymous login using `ftp` client:

```bash
ftp <target>
```

```bash
Name: anonymous            # use 'anonymous' as a username
Password: test@example.com # when prompted for password, press Enter or type anything
```

- If anonymous login is enabled, you'll receive `230 Login successful` or similar.

> [!example]+ Example: anonymous login
> 
> ```bash
> ftp> open 10.129.233.210
> Connected to 10.129.233.210.
> 220 ProFTPD Server (Debian) [10.129.233.210]
> Name (10.129.233.210:root): anonymous
> 331 Anonymous login ok, send your complete email address as your password
> Password: 
> 230 Anonymous access granted, restrictions apply
> Remote system type is UNIX.
> Using binary mode to transfer files.
> ```

- Netcat:

```bash
nc <target> 21
# connection established
USER anonymous
PASS # any, leave blank
```

- Nmap [`ftp-anon`](https://nmap.org/nsedoc/scripts/ftp-anon.html) script:

```bash
nmap --script ftp-anon -p 21 <target>
```

>[!note] Depending on the server, anonymous credentials may be different. 
>Here are some common combinations:
>- `anonymous:anonymous`
>- `anonymous:`
>- `_anonymous:`
>- `anonymous:guest`
>- `anonymous:test@test.com`
>- `ftp:ftp`
>- `_ftp:ftp`
>- `guest:guest`
>
>Why so many? FTP servers are inconsistent: some accept literally any password, some expect email-like string, some allow multiple usernames (`anonymous`, `ftp`), and some only accept specific combinations. 

>[!tip]+
>You can find a list of common default FTP credentials in [`SecLists/Passwords/Default-Credentials/ftp-betterdefaultpasslist.txt`](https://github.com/danielmiessler/SecLists/blob/master/Passwords/Default-Credentials/ftp-betterdefaultpasslist.txt).
>```bash
>curl -O -s https://raw.githubusercontent.com/danielmiessler/SecLists/refs/heads/master/Passwords/Default-Credentials/ftp-betterdefaultpasslist.txt
>```

>[!tip]+ FTP clients
>Here are some FTP clients you can use to interact with FTP servers:
> - [`ftp`](https://man.archlinux.org/man/ftp.1.enftp)
> - [`lftp`](https://lftp.yar.ru/)
> - [`filezilla`](https://filezilla-project.org/)
> - [`ncftp`](https://www.ncftp.com/)
## Brute-forcing credentials

- Medusa:

```bash
medusa -M ftp -h <target> -u admin -P /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt -e ns
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
hydra -l admin -P /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt ftp://<target>
```

- Non-standard port:

```bash
hydra -L usernames.txt -P passwords.txt -s 2121 <target> ftp
```

>[!note]+ Option breakdown
>- `-l`: Username to test (`-L` to brute-force usernames, too).
>- `-P`: Password wordlist.
>- `-s`: Specify port the target service is listening on.
>- `ftp` or `ftp://`: Target protocol (FTP).

- Nmap [`ftp-brute`](https://nmap.org/nsedoc/scripts/ftp-brute.html) script:

```bash
nmap -p 21 --script ftp-brute <target>
```

>[!note] See [[Password wordlists and default credentials]].
## References and further reading

- [`List of FTP commands — Wikipedia`](https://en.wikipedia.org/wiki/List_of_FTP_commands)
- [`List of FTP server return codes — Wikipedia`](https://en.wikipedia.org/wiki/List_of_FTP_server_return_codes)

- [`21 - Pentesting FTP — HackTricks`](https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-ftp/index.html)
- [`Active FTP vs. Passive FTP, a Definitive Explanation`](https://slacksite.com/other/ftp.html)
- [`Active vs. passive FTP simplified — jscape`](https://www.jscape.com/blog/active-v-s-passive-ftp-simplified)

- [`FTP Commands for Linux and UNIX`](https://www.solarwinds.com/serv-u/tutorials/ftp-commands-for-linux-unix)
- [`FTP Commands and Extensions — IANA`](https://www.iana.org/assignments/ftp-commands-extensions/ftp-commands-extensions.xhtml)


- [`FTP (File Transfer Protocol) — Hackviser`](https://hackviser.com/tactics/pentesting/services/ftp)
- [`TFTP (Trivial File Transfer Protocol) — Hackviser`](https://hackviser.com/tactics/pentesting/services/tftp)

## Appendix A: FTP commands reference

>[!note] Most commands can be entered only after authentication.

- Standard connection:

```bash
ftp <target>
```

- Specify non-standard port:

```bash
ftp -P 2121 <target>
```

>[!tip]+
>You can interact with FTP using `ftp://` URLs.
>
> For example, here is how to download all available files from an FTP server using such URL:
> 
> ```bash
> wget -m --no-passive ftp://anonymous:anonymous@<target>
> ```


- Inline credentials:

```bash
ftp ftp://username:password@<target>
```

- Interactive mode:

```bash
ftp
ftp> open <target>
```

> [!important] The FTP protocol itself is case-insensitive for command keywords. Commands typed in uppercase or lowercase are interpreted the same by servers.
> 
> - The convention in documentation and usage is that FTP commands are usually shown in uppercase (e.g., `LIST`, `RETR`), but common FTP clients accept both cases.
> - Case sensitivity mainly matters in filenames on servers (especially Linux).

- Status and help commands:

| Command      | Description                                                               |
| ------------ | ------------------------------------------------------------------------- |
| `?` / `help` | Show help for FTP commands.                                               |
| `!help`      | Help for local shell commands.                                            |
| `verbose`    | Toggle verbose mode (shows detailed transfer information).                |
| `status`     | Show current connection status.                                           |
| `hash`       | Toggle printing `#` for each data block transferred (progress indicator). |


- Connection and session commands:

| Command                      | Description               |
| ---------------------------- | ------------------------- |
| `open <target>`              | Connect to an FTP server. |
| `user <username> <password>` | Authenticate.             |
| `close`                      | Close FTP connection.     |
| `bye` / `quit`               | Exit FTP client.          |

- Local command execution:

```bash
!ls
!pwd
!cat file.txt
```

>[!note] FTP supports `!` command which allows users to execute local shell commands not leaving the FTP client. This is useful for quick local checks, but sometimes can be exploited for shell escapes and arbitrary command execution if misconfigured. 

- Information gathering:

| Command | Description                                                     |
| ------- | --------------------------------------------------------------- |
| `syst`  | Get system information.                                         |
| `stat`  | Show server status.                                             |
| `feat`  | List supported server features (e.g., FTPS, UTF-8, MLSD, etc.). |


- Directory navigation:

| Command     | Description                     |
| ----------- | ------------------------------- |
| `pwd`       | Print remote working directory. |
| `cd <dir>`  | Change remote directory.        |
| `cdup`      | Move to parent directory.       |
| `ls`        | List directory (uses `LIST`).   |
| `dir`       | Detailed listing (uses `NLST`). |
| `ls -al`    | Show hidden files.              |
| `ls -R`     | Recursive listing.              |
| `lcd <dir>` | Change local directory.         |
| `lpwd`      | Print local working directory.  |

- Also list hidden files and directories:

```bash
ls -al
```

- To list files and directories recursively:

```bash
ls -R
```

- File transfer commands:

| Command                             | Description                                     |
| ----------------------------------- | ----------------------------------------------- |
| `get <remote_file> <local_file>`    | Download a file (shortcut to `RETR`).           |
| `mget <remote_files>`               | Download multiple files (wildcards allowed).    |
| `put <local_file> <remote_file>`    | Upload file to the server.                      |
| `mput <local_files>`                | Upload multiple files to the server.            |
| `rename <old_name> <new_name>`      | Rename remote file.                             |
| `delete <remote_file>`              | Delete remote file.                             |
| `mkdir <directory>`                 | Create remote directory.                        |
| `rmdir <directory>`                 | Remove remote directory.                        |
| `append <local_file> <remote_file>` | Append data from a local file to a remote file. |

- Download all files in the current directory:

```bash
mget *
```


- Transfer mode and type commands:

| Command       | Description                                          |
| ------------- | ---------------------------------------------------- |
| `ascii`       | ASCII mode (line ending conversions).                |
| `binary`      | Binary mode (raw bytes).                             |
| `type <type>` | File transfer type (`A` for ASCII, `I` for binary).  |
| `mode <mode>` | Set transfer mode (`stream`, `block`, `compressed`). |

>[!tip]+
>Always use:
>```
>binary
>```
>Unless you *want* line ending corruptions.

- Active/passive mode commands:

| Command   | Description                       |
| --------- | --------------------------------- |
| `passive` | Toggle passive mode in client.    |
| `PASV`    | Server enters passive mode.       |
| `PORT`    | Client requests active mode.      |
| `EPSV`    | Extended passive (IPv6‑friendly). |
| `EPRT`    | Extended active mode.             |

- Authentication and security:

| Command    | Description                       |
| ---------- | --------------------------------- |
| `AUTH TLS` | Start TLS negotiation.            |
| `PBSZ 0`   | Protection buffer size.           |
| `PROT P`   | Protect data channel (encrypted). |
| `PROT C`   | Clear data channel.               |

- Raw protocol commands (low-level):

| Command | Purpose                      |
| ------- | ---------------------------- |
| `USER`  | Username.                    |
| `PASS`  | Password.                    |
| `ACCT`  | Account info.                |
| `CWD`   | Change working directory.    |
| `CDUP`  | Change to parent.            |
| `SMNT`  | Mount file structure (rare). |
| `REIN`  | Reinitialize session.        |
| `QUIT`  | End session.                 |
| `PORT`  | Active mode.                 |
| `PASV`  | Passive mode.                |
| `TYPE`  | Transfer type.               |
| `STRU`  | File structure.              |
| `MODE`  | Transfer mode.               |
| `RETR`  | Retrieve file.               |
| `STOR`  | Store file.                  |
| `STOU`  | Store unique file.           |
| `APPE`  | Append.                      |
| `ALLO`  | Allocate storage.            |
| `REST`  | Restart transfer.            |
| `RNFR`  | Rename from.                 |
| `RNTO`  | Rename to.                   |
| `ABOR`  | Abort transfer.              |
| `DELE`  | Delete file.                 |
| `RMD`   | Remove directory.            |
| `MKD`   | Make directory.              |
| `PWD`   | Print working directory.     |
| `LIST`  | Directory listing.           |
| `NLST`  | Name list.                   |
| `SITE`  | Server‑specific commands.    |
| `SYST`  | System type.                 |
| `STAT`  | Status.                      |
| `HELP`  | Help.                        |
| `NOOP`  | Keepalive.                   |

## Appendix B: FTP status codes reference

- **`1xx` — Positive Preliminary Reply**
	- Indicate the status of the server's current action, meaning the server is in the process of completing the command.


| Code  | Message                                           | Description                                               |
| ----- | ------------------------------------------------- | --------------------------------------------------------- |
| `110` | `Restart marker reply`                            | Indicates a restart marker; transfer will continue.       |
| `120` | `Service ready in nnn minutes`                    | Server is temporarily unavailable but will be ready soon. |
| `125` | `Data connection already open; transfer starting` | Data connection is open and transfer is beginning.        |
| `150` | `File status okay; about to open data connection` | Server is preparing to open a data connection.            |

- **`2xx` — Positive Completion Reply**
	- Indicates that the requested action has been successfully completed.

| Code  | Message                                                     | Description                                                       |
| ----- | ----------------------------------------------------------- | ----------------------------------------------------------------- |
| `200` | `Command okay`                                              | The command was successfully processed.                           |
| `202` | `Command not implemented, superfluous at this site`         | The command is not implemented or is unnecessary for this server. |
| `211` | `System status, or system help reply`                       | Provides general system status or a help message.                 |
| `212` | `Directory status`                                          | Provides the status of the requested directory.                   |
| `213` | `File status`                                               | Provides the status of the requested file.                        |
| `214` | `Help message`                                              | Returns help documentation for the given command.                 |
| `215` | `NAME system type`                                          | Identifies the name of the remote operating system.               |
| `220` | `Service ready for new user`                                | The FTP server is ready for a new connection.                     |
| `221` | `Service closing control connection`                        | The server is closing the control connection.                     |
| `226` | `Closing data connection; requested file action successful` | Data transfer was successful, and the connection is closing.      |
| `227` | `Entering Passive Mode (h1,h2,h3,h4,p1,p2)`                 | Server is entering passive mode for data transfer.                |
| `250` | `Requested file action okay, completed`                     | Requested file action completed successfully.                     |
| `257` | `Requested directory created`                               | The requested directory was successfully created.                 |

- **`3xx` — Positive Intermediate Reply**
	- Indicates that the server has received the request, but further action is needed.

| Code  | Message                                             | Description                                                  |
| ----- | --------------------------------------------------- | ------------------------------------------------------------ |
| `331` | `User name okay, need password`                     | The server is waiting for a password for the given username. |
| `332` | `Need account for login`                            | The server requires an account to complete the login.        |
| `350` | `Requested file action pending further information` | Action is pending further information from the client.       |

- **`4xx` — Transient Negative Completion Reply**
	- Indicates a temporary error or a failure, where the client can try the command again.

| Code  | Message                                               | Description                                                        |
| ----- | ----------------------------------------------------- | ------------------------------------------------------------------ |
| `421` | `Service not available, closing control connection`   | The server is closing the connection due to a temporary issue.     |
| `425` | `Can't open data connection`                          | The server was unable to establish a data connection.              |
| `426` | `Connection closed; transfer aborted`                 | Data transfer was aborted due to a connection closure.             |
| `450` | `Requested file action not taken; file unavailable`   | The file is unavailable or locked.                                 |
| `451` | `Requested action aborted: local error in processing` | The server encountered a local error while processing the request. |
| `452` | `Requested action not taken; insufficient storage`    | The server ran out of storage space while processing the command.  |

- **`5xx` — Permanent Negative Completion Reply**
	- Indicates a permanent error, and the requested action cannot be completed.

| Code  | Message                                                      | Description                                                     |
| ----- | ------------------------------------------------------------ | --------------------------------------------------------------- |
| `500` | `Syntax error, command unrecognized`                         | The server could not recognize the command syntax.              |
| `501` | `Syntax error in parameters or arguments`                    | There is an error in the provided command arguments.            |
| `502` | `Command not implemented`                                    | The server does not support the command.                        |
| `503` | `Bad sequence of commands`                                   | The commands were issued in an invalid sequence.                |
| `504` | `Command not implemented for that parameter`                 | The server cannot execute the command with the given parameter. |
| `530` | `Not logged in`                                              | The client is not logged in to the server.                      |
| `532` | `Need account for storing files`                             | The server requires an account to store files.                  |
| `550` | `Requested action not taken; file unavailable`               | The requested file is unavailable or not found.                 |
| `551` | `Requested action aborted: page type unknown`                | The server does not recognize the requested file type.          |
| `552` | `Requested file action aborted: exceeded storage allocation` | The server has exceeded its storage limits for the user.        |
| `553` | `Requested action not taken; file name not allowed`          | The server does not accept the given file name.                 |
