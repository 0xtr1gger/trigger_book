---
created: 2026-09-22
updated: 2026-09-27
tags:
  - services_n_protocols
---
## FTP

> **FTP (File Transfer Protocol)** is a connection-oriented, application-layer protocol designed for bidirectional file transfers between a client and a server.

>[!note] FTP was originally specified in [`RFC 114`](https://www.rfc-editor.org/rfc/rfc114.html) (1971); the current core protocol standard is defined in [`RFC 959`](https://datatracker.ietf.org/doc/html/rfc959).

- FTP supports username and password authentication.
- No encryption: all data is sent in **cleartext**, including authentication credentials, commands, response status codes, and transferred files.
- By default, the FTP service listens on TCP port `21` (control connections); port `20` is used for data connections in active mode.

>[!note]+ Encrypted FTP alternatives
> - **FTPS (FTP Secure)**: An extension of FTP that encrypts control and data channels using TLS/SSL, either implicitly on dedicated TCP port `990` or explicitly via the `AUTH TLS` command on TCP port `21` ([`RFC 4217`](https://www.rfc-editor.org/rfc/rfc4217)).
> - **SFTP (SSH File Transfer Protocol)**: An independent protocol built as an SSH subsystem over TCP port `22`. It provides encrypted file transfers using SSH transport and is unrelated to FTP despite its name.

### Control and data channel architecture

- FTP splits communication across **two separate TCP connections**:
	- **Control connection** (TCP port `21`): A persistent session established between client and server. The client sends commands and the server replies with three-digit status codes.
	- **Data connection** (TCP port `20` or dynamic high ports): A transient connection opened on demand for directory listings and file transfers. The connection closes automatically after the transfer completes.

>[!note] See [`List of FTP commands — Wikipedia`](https://en.wikipedia.org/wiki/List_of_FTP_commands) and [`List of FTP server return codes — Wikipedia`](https://en.wikipedia.org/wiki/List_of_FTP_server_return_codes).

### Active and passive modes

- FTP supports **two modes of operation**:
	- **Active mode** (`PORT`): The client listens for incoming connections on a dynamic port and sends the `PORT` command to the server. The server initiates an *outbound data connection* from TCP port `20` to the client's listener.
	- **Passive mode** (`PASV`): The client sends the `PASV` command to the server. The server opens a listening port (above `1023`) and sends the port number to the client. The client initiates the data connection to the server.

>[!interesting]- Active connection establishment
> 
> 1. An **FTP client** opens a **control connection** to the FTP server on **TCP port `21`** to send FTP commands.
> 2. The **FTP client** starts listening on an *arbitrary port* for incoming data connections and sends the **`PORT` command** with the port number to the server.
> 3. The **FTP server** initiates a **data connection** from its **TCP port `20`** to the client's specified port.
> 4. Once the data connection is established, data (files, directory listings, etc.) can be transferred from the server to the client or vice versa.
> 5. After the transfer is complete, the data connection is closed.

>[!interesting]- Passive connection establishment
> 1. An **FTP client** opens a **control connection** to the FTP server on **TCP port `21`** to send FTP commands. 
> 2. The client asks the server to listen for a data connection by sending the `PASV` command.
> 3. The FTP server responds with an IP address and a port number for the client to connect to (dynamic port, usually above `1023`).
> 4. The client then initiates a TCP connection **from its side to the server's specified port**.
> 5. Once the data connection is established, data (files, directory listings, etc.) can be transferred from the server to the client or vice versa.
> 6. After the transfer is complete, the data connection is closed.

>[!important] Active mode requires the client to accept inbound connections from the server. When inbound connections are blocked by a firewall or NAT, passive mode is used.

>[!important] TCP port `20` is used only in active mode.

## Enumerating FTP

### Port scanning and version detection

- Check default FTP ports and run a version scan:

```bash
sudo nmap -sV -p 21 10.10.11.5
```
- Scan all ports and perform version detection (identifies FTP on non-standard ports):

```bash
sudo nmap -sV -p- 10.10.11.5
```

- Increase Nmap version detection intensity:

```bash
nmap -sV --version-intensity 9 -p 21 10.10.11.5
```

- Run default FTP scripts:

```bash
sudo nmap -sV -sC -p 21 10.10.11.5
```

- Run all available FTP NSE scripts:

```bash
nmap -p 21 --script "ftp-*" 10.10.11.5
```

| Option | Description |
| :--- | :--- |
| `-sV` | Enable service version detection. |
| `-p` | Specify target port to scan. |
| `-p-` | Scan all TCP ports (`1`-`65535`). |
| `--script` | Specify NSE script to execute. |
| `-sC` | Execute `default` scripts. |
| `--version-intensity` | Specify version detection intensity (`0`-`9`). |


>[!tip]+
> - List available NSE scripts for FTP:
> 
> ```bash
> ls -l /usr/share/nmap/scripts/*ftp*
> ```

- Key Nmap FTP scripts:

| Script                                                                              | Categories                                | Description                                                                  |
| :---------------------------------------------------------------------------------- | :---------------------------------------- | :--------------------------------------------------------------------------- |
| [`ftp-anon`](https://nmap.org/nsedoc/scripts/ftp-anon.html)                         | `default`, `auth`, `safe`                 | Check if an FTP server allows anonymous logins.                              |
| [`ftp-syst`](https://nmap.org/nsedoc/scripts/ftp-syst.html)                         | `default`, `safe`, `discovery`            | Retrieve operating system and software details using the `SYST` command.     |
| [`ftp-bounce`](https://nmap.org/nsedoc/scripts/ftp-bounce.html)                     | `default`, `safe`                         | Test if the server is vulnerable to FTP bounce attacks (`PORT` relaying).    |
| [`ftp-brute`](https://nmap.org/nsedoc/scripts/ftp-brute.html)                       | `intrusive`, `brute`                      | Perform password brute-forcing against user accounts.                        |
| [`ftp-libopie`](https://nmap.org/nsedoc/scripts/ftp-libopie.html)                   | `vuln`, `intrusive`                       | Test for the OPIE off-by-one stack overflow vulnerability (`CVE-2010-1938`). |
| [`ftp-proftpd-backdoor`](https://nmap.org/nsedoc/scripts/ftp-proftpd-backdoor.html) | `exploit`, `intrusive`, `malware`, `vuln` | Test for the `ProFTPD 1.3.3c` backdoor command execution flaw.               |
| [`ftp-vsftpd-backdoor`](https://nmap.org/nsedoc/scripts/ftp-vsftpd-backdoor.html)   | `exploit`, `intrusive`, `malware`, `vuln` | Test for the `vsFTPd 2.3.4` backdoor (`CVE-2011-2523`).                      |
| [`tftp-enum`](https://nmap.org/nsedoc/scripts/tftp-enum.html)                       | `discovery`, `intrusive`                  | Enumerate TFTP filenames.                                                    |

### Banner grabbing

- Once an FTP control connection opens, the server sends an initial banner containing software and version details.
- Grab the FTP banner using Netcat or Telnet:

```bash
nc -vn 10.10.11.5 21
```
```bash
telnet 10.10.11.5 21
```

- If the banner is suppressed or misleading, send raw FTP commands like `SYST` to retrieve system information and `STAT` to query server status:

```bash
echo "SYST" | nc -w 5 10.10.11.5 21
```

```bash
echo "STAT" | nc -w 5 10.10.11.5 21
```

- Enumerate supported protocol extensions and features:

```bash
echo "FEAT" | nc -w 5 10.10.11.5 21
```

>[!note]+ `nc` options
>
> | Option | Description |
> | :--- | :--- |
> | `-v` | Enable verbose output. |
> | `-n` | Suppress DNS name resolution. |
> | `-w` | Set network timeout in seconds before closing the connection. |

>[!note] See [`FTP Commands and Extensions — IANA`](https://www.iana.org/assignments/ftp-commands-extensions/ftp-commands-extensions.xhtml).

>[!tip]+
> - Retrieve TLS certificate details from an FTPS server:
> 
> ```bash
> openssl s_client -connect 10.10.11.5:21 -starttls ftp
> ```

## Anonymous login

- Anonymous FTP login is one of the most common misconfigurations. It was designed as a legitimate feature for public file distribution, such as software mirrors, but in practice, it is often left enabled in situations where it should not be.

>**Anonymous FTP login** allows unauthenticated access to the FTP server, typically using a fixed username such as `anonymous` or `ftp` and an empty password.

- Accepted credentials vary across implementations:
	- Username: `anonymous` (most common), `ftp`, `_ftp`, `guest`, or `_anonymous`
	- Password: Any text, an empty string, or an arbitrary email address (e.g. `test@example.com`)

>[!tip]+
>- You can find a list of common default FTP credentials in [`SecLists/Passwords/Default-Credentials/ftp-betterdefaultpasslist.txt`](https://github.com/danielmiessler/SecLists/blob/master/Passwords/Default-Credentials/ftp-betterdefaultpasslist.txt).

![[Attacking network services methodology#Testing for anonymous login]]

> [!example]- 
> ```bash
> ftp> open 10.129.233.210
> ```
> ```bash
> Connected to 10.129.233.210.
> 220 ProFTPD Server (Debian) [10.129.233.210]
> Name (10.129.233.210:root): anonymous
> 331 Anonymous login ok, send your complete email address as your password
> Password: 
> 230 Anonymous access granted, restrictions apply
> Remote system type is UNIX.
> Using binary mode to transfer files.
> ```
### Brute-forcing credentials

![[Attacking network services methodology#Brute-forcing credentials]]
## Interacting with FTP servers

- Connect to an FTP server interactively:

```bash
ftp 10.10.11.5
```


- Alternatively, open a connection inside an interactive `ftp` client:

```bash
ftp
```
```bash
ftp> open 10.10.11.5
```

- Connect to a non-standard port:

```bash
ftp -P 2121 10.10.11.5
```

>[!tip]+
> - You can interact with FTP using `ftp://` URLs.
>
> For example, to download all available files from an FTP server:
> 
> ```bash
> wget -m --no-passive ftp://anonymous:anonymous@<target>
> ```

- Connect using inline credentials:

```bash
ftp ftp://jdoe:passwd123@10.10.11.5
```

> [!important] The FTP protocol itself is case-insensitive for command keywords. Commands typed in uppercase or lowercase are interpreted the same way by servers.
> 
> - By convention, FTP commands are usually shown in uppercase (e.g., `LIST`, `RETR`), but common FTP clients accept both cases.
> - Case sensitivity mainly matters for filenames on servers (especially Linux).

- To execute a command locally on your system, prepend `!` to the command:

```bash
!ls
!pwd
!cat file.txt
```

>[!note] See [[#Appendix A FTP commands reference]].

## References and further reading

- [`RFC 959 — File Transfer Protocol (FTP)`](https://datatracker.ietf.org/doc/html/rfc959)
- [`RFC 4217 — Securing FTP with TLS`](https://datatracker.ietf.org/doc/html/rfc4217)
- [`IANA FTP Commands and Extensions`](https://www.iana.org/assignments/ftp-commands-extensions/ftp-commands-extensions.xhtml)
- [`21 - Pentesting FTP — HackTricks`](https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-ftp/index.html)
- [`vsftpd.conf Manual Page`](http://vsftpd.beasts.org/vsftpd_conf.html)
- [`SecLists — Default FTP Credentials`](https://github.com/danielmiessler/SecLists/blob/master/Passwords/Default-Credentials/ftp-betterdefaultpasslist.txt)
- [`Active FTP vs. Passive FTP, a Definitive Explanation`](https://slacksite.com/other/ftp.html)
- [`Active vs. passive FTP simplified — jscape`](https://www.jscape.com/blog/active-v-s-passive-ftp-simplified)
- [`FTP Commands for Linux and UNIX`](https://www.solarwinds.com/serv-u/tutorials/ftp-commands-for-linux-unix)
- [`FTP Commands and Extensions — IANA`](https://www.iana.org/assignments/ftp-commands-extensions/ftp-commands-extensions.xhtml)
- [`FTP (File Transfer Protocol) — Hackviser`](https://hackviser.com/tactics/pentesting/services/ftp)
- [`TFTP (Trivial File Transfer Protocol) — Hackviser`](https://hackviser.com/tactics/pentesting/services/tftp)

## Appendix A: FTP commands reference

>[!note] Most commands can be entered only after authentication.

>[!note] See [`List of FTP commands — Wikipedia`](https://en.wikipedia.org/wiki/List_of_FTP_commands) and [`List of FTP server return codes — Wikipedia`](https://en.wikipedia.org/wiki/List_of_FTP_server_return_codes).


- Status and help commands:

| Command      | Description                                                               |
| ------------ | ------------------------------------------------------------------------- |
| `?` / `help` | Show help for FTP commands.                                               |
| `!help`      | Show help for local shell commands.                                            |
| `verbose`    | Toggle verbose mode (shows detailed transfer information).                |
| `status`     | Show current connection status.                                           |
| `hash`       | Toggle printing `#` for each data block transferred (progress indicator). |


- Connection and session commands:

| Command                      | Description               |
| ---------------------------- | ------------------------- |
| `open <target>`              | Connect to an FTP server. |
| `user <username> <password>` | Authenticate.             |
| `close`                      | Close the FTP connection. |
| `bye` / `quit`               | Exit the FTP client.      |

- Local command execution:

```bash
!ls
!pwd
!cat file.txt
```

>[!note] FTP supports the `!` command, which allows users to execute local shell commands without leaving the FTP client. This is useful for quick local checks, but can sometimes be exploited for shell escapes and arbitrary command execution if misconfigured. 

- Information gathering:

| Command | Description                                                     |
| ------- | --------------------------------------------------------------- |
| `syst`  | Get system information.                                         |
| `stat`  | Show server status.                                             |
| `feat`  | List supported server features (e.g., FTPS, UTF-8, MLSD). |


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
| `put <local_file> <remote_file>`    | Upload a file to the server.                    |
| `mput <local_files>`                | Upload multiple files to the server.            |
| `rename <old_name> <new_name>`      | Rename a remote file.                           |
| `delete <remote_file>`              | Delete a remote file.                           |
| `mkdir <directory>`                 | Create a remote directory.                      |
| `rmdir <directory>`                 | Remove a remote directory.                      |
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
>Unless you *want* line-ending corruption.

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
| `PBSZ 0`   | Set protection buffer size.       |
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
	- Indicates the status of the server's current action, meaning the server is in the process of completing the command.

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

## Appendix C: vsFTPd configuration

- [`vsFTPd`](https://security.appspot.com/vsftpd.html) is one of the most widely deployed Linux FTP servers.
- The primary configuration file is located at `/etc/vsftpd.conf`.

---

- Inspect the `vsFTPd` configuration (filters out commands and empty lines):

```bash
grep -v "^#" /etc/vsftpd.conf | grep -v "^$"
```

- Key `vsFTPd` security settings:

| Setting                | Value      | Description                                                              |
| :--------------------- | :--------- | :----------------------------------------------------------------------- |
| `listen`               | `YES`/`NO` | `YES`: Run vsFTPd as a standalone daemon.                                |
| `listen_ipv6`          | `YES`/`NO` | `YES`: Listen on IPv6 sockets.                                           |
| `anonymous_enable`     | `YES`/`NO` | `YES`: Accept anonymous logins.                                          |
| `local_enable`         | `YES`/`NO` | `YES`: Allow local user accounts from `/etc/passwd` to authenticate.     |
| `write_enable`         | `YES`/`NO` | `YES`: Allow filesystem write operations (`STOR`, `DELE`, `MKD`, `RMD`). |
| `chroot_local_user`    | `YES`/`NO` | `YES`: Restrict local users to their home directory upon authentication. |
| `connect_from_port_20` | `YES`/`NO` | `YES`: Force active data connections to originate from TCP port `20`.    |
| `pam_service_name`     | `vsftpd`   | Specify the PAM service configuration file in `/etc/pam.d/`.             |
| `ssl_enable`           | `YES`/`NO` | `YES`: Enable FTPS TLS encryption.                                       |
| `rsa_cert_file`        | `<path>`   | Specify the path to the RSA certificate file for TLS.                    |
| `rsa_private_key_file` | `<path>`   | Specify the path to the RSA private key file for TLS.                    |

- Dangerous anonymous settings:

| Setting                   | Value    | Security impact                                               |
| :------------------------ | :------- | :------------------------------------------------------------ |
| `anonymous_enable`        | `YES`    | Enable unauthenticated access to the FTP directory tree.      |
| `anon_upload_enable`      | `YES`    | Allow anonymous users to upload arbitrary files.              |
| `anon_mkdir_write_enable` | `YES`    | Allow anonymous users to create new directories.              |
| `anon_other_write_enable` | `YES`    | Allow anonymous users to delete or overwrite existing files.  |
| `no_anon_password`        | `YES`    | Suppress password prompt for anonymous logins.                |
| `anon_root`               | `<path>` | Set the root directory for anonymous users (e.g. `/var/ftp`). |

- The `/etc/ftpusers` file lists accounts that are explicitly forbidden from authenticating to the FTP service.

```bash
cat /etc/ftpusers
```