---
created: 2026-04-01
---
- Tools:
	- [`nmblookup`](https://www.samba.org/samba/docs/current/man-html/nmblookup.1.html)

## smbclient
## smbmap

| Command         | Description                               | Usage                                     |
| --------------- | ----------------------------------------- | ----------------------------------------- |
| `smbclient`     | Connect to an SMB/CIFS server             | `smbclient //server/share`                |
| `smbget`        | Download files from an SMB/CIFS server    | `smbget smb://server/share/file`          |
| `smbpasswd`     | Change a user's SMB password              | `smbpasswd -r server -U username`         |
| `smbstatus`     | Display information about SMB connections | `smbstatus`                               |
| `smbtree`       | List SMB/CIFS shares on a network         | `smbtree`                                 |
| `mount -t cifs` | Mount an SMB/CIFS share                   | `mount -t cifs //server/share /mnt/point` |
| `umount`        | Unmount an SMB/CIFS share                 | `umount /mnt/point`                       |

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


## CrackMapExec

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

## rpcclient


### enum4linux-ng

> [`enum4linux`](https://www.kali.org/tools/enum4linux/) is a **wrapper** around Samba utilities (`smbclient`, `rpcclient`, `net`, `nmblookup`); designed for comprehensive SMB/RPC enumeration.

>[!note]+ `enum4linux` performs:
>- NetBIOS name lookups (`nmblookup`).
>- Share enumeration (`smbclient -L`).
>- User and group enumeration (`rpcclient enumdomusers`, `enumdomgroups`).
>- RID cycling (via `rpcclient lookupsids`).
>- Password policy enumeration (SAMR/LSARPC).
>- OS and domain info discovery.
>- Workgroup/domain listing.
>- Printer enumeration.
>- Samba version detection.


>[`enum4linux-ng`](https://github.com/cddmp/enum4linux-ng) is a complete rewrite of `enum4linux` in Python, designed to fix all the pain points of the original.




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


## Impacket

- `lookupsid.py`
- `samrdump.py`
- `psexec.py`
- `wmiexec.py`

## NetBIOS tools

- `nbtscan`
- `nmblookup`

### nbtscan


>
### nmblookup

 >The [`nmblookup`](https://www.samba.org/samba/docs/current/man-html/nmblookup.1.html) tool is used to query NetBIOS names and map them to IP addresses on a network.

- Query a NetBIOS name:

```bash
nmblookup <NetBIOS_name>
```

- Query an IP address:

```bash
nmblookup -A <IP_address>
```

| Option                 | Description                                                                     |
| ---------------------- | ------------------------------------------------------------------------------- |
| `-r`, `--root-port`    | Attempt and bind to UDP port `137` to send and receive UDP datagrams.           |
| `-A`, `--lookup-by-ip` | Interpret *`name`* as an IP address and do a node status query on this address. |

```bash
nmblookup -A 10.129.27.56
Looking up status of 10.129.27.56
	DEVSMB          <00> -         H <ACTIVE> 
	DEVSMB          <03> -         H <ACTIVE> 
	DEVSMB          <20> -         H <ACTIVE> 
	..__MSBROWSE__. <01> - <GROUP> H <ACTIVE> 
	DEVOPS          <00> - <GROUP> H <ACTIVE> 
	DEVOPS          <1d> -         H <ACTIVE> 
	DEVOPS          <1e> - <GROUP> H <ACTIVE> 

	MAC Address = 00-00-00-00-00-00
```

## Responder /relay tools
- `responder`
- `ntlmrelayx.py`
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

