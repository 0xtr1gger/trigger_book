---
created: 2026-09-22
updated: 2026-10-11
tags:
  - services_n_protocols
---
## SMB

> **[SMB (Server Message Block)](https://en.wikipedia.org/wiki/Server_Message_Block)** is a client-server network communication protocol that enables shared access to files, printers, serial ports, and inter-process communication (IPC) endpoints between nodes across a network.

>[!note] The core SMB protocol and its Windows extensions are documented across Microsoft technical specifications, including [`MS-SMB`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-smb/) (Server Message Block Protocol), [`MS-SMB2`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-smb2/) (Server Message Block Protocol Versions 2 and 3), [`MS-CIFS`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-cifs/) (Common Internet File System), and [`MS-RPCE`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-rpce/) (Remote Procedure Call Protocol Extensions).

- SMB operates on a **client-server architecture**:
	- The client establishes a transport connection, negotiates dialect versions, authenticates security contexts, and requests tree connections to specific exported shares.
	- The server validates client requests against share permissions and underlying filesystem access control lists (ACLs).
- While SMB is mostly associated with Windows operating systems, Unix-like systems implement it via [Samba](https://www.samba.org/) — a free, open-source re-implementation of the SMB/CIFS networking protocol suite.
- SMB provides underlying transport for **inter-process communication (IPC)** over named pipes, exposing remote management interfaces (RPC over SMB).

### Shares and access control

> An **SMB share** is a named resource (filesystem folder, printer queue, or IPC abstraction) exported by an SMB server and made available to network clients.

- Share access is governed by **two independent permission layers**:
	- **Share-level permissions**: Defined in the SMB daemon configuration (or Windows share properties) and evaluated during the initial tree connect phase (`READ`, `CHANGE`, `FULL CONTROL`).
	- **Filesystem-level permissions**: Defined on the underlying storage filesystem (such as NTFS ACLs or POSIX file permissions) and evaluated during file I/O operations.
- The **most restrictive permission** between share-level and filesystem-level ACLs always takes precedence.

### Direct SMB vs. SMB over NetBIOS transport

- SMB operates across two distinct transport configurations:
	- **Direct TCP transport (Modern SMB)**: Operates directly over **TCP port `445`** without an intermediate NetBIOS transport encapsulation. Used by modern Windows and Samba systems.
	- **SMB over NetBIOS (Legacy NetBIOS over TCP/IP — NBT)**: Encapsulates SMB frames inside NetBIOS session service packets over **TCP port `139`**. Relies on NetBIOS Name Service on **UDP port `137`** and NetBIOS Datagram Service on **UDP port `138`**.
- When assessing target networks, both **TCP `139`** and **TCP `445`** should be probed.

### SMB session lifecycle

- The lifecycle of an SMB connection follows five sequential phases:
	1. **Transport connection and dialect negotiation**: The client opens a TCP connection to port `445` (or `139`) and sends an `SMB_COM_NEGOTIATE` or `SMB2 NEGOTIATE` packet. The server selects the highest mutually supported dialect.
	2. **Session setup and authentication**: The client issues an authentication request (`SESSION_SETUP`) carrying NTLM challenge-response tokens or Kerberos tickets. Unauthenticated sessions establish a **null session** or guest context.
	3. **Tree connect**: The client requests connection to a specific share name (e.g. `\\10.10.11.5\share`) via `TREE_CONNECT`. The server allocates a Tree ID (TID) and applies share ACLs.
	4. **File and resource operations**: The client performs read, write, create, delete, or named pipe transaction calls against resources referencing the allocated TID and File ID (FID).
	5. **Tree disconnect and logoff**: The client closes active file handles, terminates share connections with `TREE_DISCONNECT`, and ends the session with `LOGOFF`.

### SMB protocol versions and dialects

| Version | Introduced with | Description |
| :--- | :--- | :--- |
| **CIFS / SMB 1.0** | Windows NT 4.0 / Windows 2000 | Legacy 16-bit protocol; operates over NetBIOS (TCP `139`) or direct TCP (`445`). Lacks transport encryption; vulnerable to [`MS17-010`](https://nvd.nist.gov/vuln/detail/CVE-2017-0144) ([`EternalBlue`](https://en.wikipedia.org/wiki/EternalBlue)). Deprecated and disabled by default on modern OS builds. |
| **SMB 2.0 / 2.1** | Windows Vista / Server 2008 / Windows 7 | Streamlined command set (reduced from over 100 commands to 19); pipelining and compound requests; HMAC-SHA256 message signing; opportunistic locking and client-side caching. |
| **SMB 3.0 / 3.0.2** | Windows 8 / Server 2012 / 2012 R2 | End-to-end transparent AES-CCM data encryption; SMB Multichannel; SMB Direct (RDMA); AES-CMAC message signing; secure dialect negotiation to prevent downgrade attacks. |
| **SMB 3.1.1** | Windows 10 / Server 2016+ | Pre-authentication integrity checks (SHA-512 hashing across negotiate/session setup frames); AES-128-GCM and AES-256-GCM cipher support; cluster client failover. |

>[!note] Standard Nmap version scans against Windows targets frequently report the Windows kernel build number rather than the negotiated SMB dialect. Use tools such as `enum4linux-ng` or `netexec` (`NetExec`) to enumerate exact dialect capabilities.

### SMB authentication models

- SMB implements two distinct authentication architectures:
	- **User-level authentication**: The client supplies distinct identity credentials (username, domain, and password/hash). Permissions are mapped to specific security identifiers (SIDs).
	- **Share-level authentication**: Legacy authentication where a password is assigned directly to an exported share without individual user accounts.
- Under the hood, authentication tokens are validated via one of two underlying mechanisms:
	- **NTLM (NT LAN Manager)**: Challenge-response protocol utilized in standalone workgroups and as a fallback in Active Directory. Vulnerable to NTLM relaying, credential sniffing, and [[Pass-the-Hash]].
	- **Kerberos**: Ticket-based authentication protocol utilizing Kerberos Key Distribution Centers (KDCs) on Domain Controllers. Preferred and enforced across Active Directory domains.

>[!note]+ Workgroup vs. domain environments
> - **Workgroup**: A decentralized peer-to-peer architecture where each host maintains its own local Security Accounts Manager (SAM) database (`C:\Windows\System32\config\SAM`). Accounts exist purely per host, discovery relies on NetBIOS/LLMNR broadcasts, and NTLM is the sole authentication protocol.
> - **Domain**: A centralized enterprise directory managed by **Active Directory Domain Services (AD DS)**. All authentication requests are processed by Domain Controllers (DCs) using Kerberos tickets, accounts and policies are global, and resources are organized into hierarchical Organizational Units (OUs).

### Standard administrative shares

- Windows hosts automatically generate **hidden administrative shares** ending with a `$` character.
- These shares are invisible to standard unauthenticated directory browsing, but accessible when explicitly queried with administrative credentials:

| Share | Scope | Description |
| :--- | :--- | :--- |
| **`C$`, `D$`, `E$`** | All Windows hosts | Administrative drive shares mapping directly to the root of each local filesystem volume (`C:\`, `D:\`). Accessible strictly by Local Administrators, Domain Admins, and `SYSTEM`. |
| **`ADMIN$`** | All Windows hosts | Administrative share mapping to the Windows operating system root (`%SystemRoot%`, typically `C:\Windows`). Used by remote administration utilities (such as PsExec and SCCM) to stage service binaries. |
| **`IPC$`** | All Windows & Samba hosts | Inter-Process Communication share. Does not expose filesystem files; instead exposes **named pipes** for RPC communication (`\pipe\samr`, `\pipe\lsarpc`, `\pipe\srvsvc`). Gateway for RPC enumeration and null sessions. |
| **`PRINT$`** | Print servers / Workstations | Administrative share hosting shared printer drivers (`C:\Windows\System32\spool\drivers`). Abused in spooler vulnerabilities such as [`PrintNightmare (CVE-2021-34527)`](https://nvd.nist.gov/vuln/detail/cve-2021-34527). |
| **`SYSVOL`** | Domain Controllers only | Active Directory share mapping to `C:\Windows\SYSVOL\sysvol`. Replicated across all domain controllers; stores Group Policy Objects (GPOs), logon scripts, and domain policies. Read-accessible to all domain authenticated users. |
| **`NETLOGON`** | Domain Controllers only | Subfolder within `SYSVOL` (`C:\Windows\SYSVOL\sysvol\<domain>\scripts`) storing logon scripts and policy files. Read-accessible to all domain authenticated users. |

### SMB signing and security mode

- **SMB signing** verifies the integrity and authenticity of SMB packets by appending a cryptographic signature (HMAC-SHA256 or AES-CMAC) generated using session keys.
- Signing states:
	- **Disabled**: The server does not support signing.
	- **Enabled (Not Required)**: The server supports signing, but accepts unsigned packets if the client does not negotiate it. Hosts in this state are vulnerable to **SMB relay attacks**.
	- **Required**: The server mandates valid signatures on all packets; unsigned requests are dropped. Completely mitigates SMB relaying.

| Host type | SMBv1 default signing | SMBv2 / SMBv3 default signing |
| :--- | :--- | :--- |
| **Windows Workstation / Member Server** | Enabled (not required) | Enabled (not required) |
| **Domain Controller (DC)** | Required | Required |
| **Samba (Default)** | Disabled | Enabled (not required) |

## Enumerating SMB

### Port scanning and version detection

- Scan standard SMB ports (`139`, `445`) with service version detection:

```bash
sudo nmap -sV -p 139,445 10.10.11.5
```

- Scan full TCP range with version detection to locate SMB instances bound to non-standard ports:

```bash
sudo nmap -sV -p- 10.10.11.5
```

- Execute default SMB NSE enumeration scripts:

```bash
sudo nmap -sV -sC -p 139,445 10.10.11.5
```

- Execute all available SMB NSE scripts against the target host:

```bash
nmap -p 139,445 --script "smb-*" 10.10.11.5
```

| Option | Description |
| :--- | :--- |
| `-sV` | Enable service version detection. |
| `-p` | Specify destination port(s) to scan (`139,445` or `-p-` for all ports). |
| `-sC` | Execute default category NSE scripts. |
| `--script` | Execute specific NSE script or glob expression. |
| `-Pn` | Treat host as online; skip ICMP ping discovery. |

>[!tip]+
> - List local Nmap NSE scripts available for SMB enumeration and vulnerability scanning:
> 
> ```bash
> ls -l /usr/share/nmap/scripts/*smb*
> ```

- Key Nmap SMB scripts:

| Script | Categories | Description |
| :--- | :--- | :--- |
| [`smb-os-discovery`](https://nmap.org/nsedoc/scripts/smb-os-discovery.html) | `default`, `discovery`, `safe` | Extract OS distribution, computer name, NetBIOS domain/workgroup, and system time. |
| [`smb-enum-shares`](https://nmap.org/nsedoc/scripts/smb-enum-shares.html) | `discovery`, `intrusive` | Connect via null session or credentials to list exported shares and check permissions. |
| [`smb-enum-users`](https://nmap.org/nsedoc/scripts/smb-enum-users.html) | `auth`, `intrusive` | Query SAMR and LSA interfaces over named pipes to enumerate local and domain users. |
| [`smb-enum-groups`](https://nmap.org/nsedoc/scripts/smb-enum-groups.html) | `discovery`, `intrusive` | Enumerate local and domain security groups along with group memberships. |
| [`smb-enum-domains`](https://nmap.org/nsedoc/scripts/smb-enum-domains.html) | `discovery`, `intrusive` | Query the domain name, domain SID, and password policies. |
| [`smb-security-mode`](https://nmap.org/nsedoc/scripts/smb-security-mode.html) | `default`, `discovery`, `safe` | Identify whether SMB message signing is enabled or required. |
| [`smb-protocols`](https://nmap.org/nsedoc/scripts/smb-protocols.html) | `default`, `discovery`, `safe` | Enumerate supported SMB protocol versions and dialects. |
| [`smb-vuln-ms17-010`](https://nmap.org/nsedoc/scripts/smb-vuln-ms17-010.html) | `vuln`, `safe` | Check whether the target is unpatched against EternalBlue (`CVE-2017-0143`). |
| [`smb-vuln-cve-2017-7494`](https://nmap.org/nsedoc/scripts/smb-vuln-cve-2017-7494.html) | `vuln`, `safe` | Test Samba servers for the SambaCry remote code execution flaw. |
| [`nbstat`](https://nmap.org/nsedoc/scripts/nbstat.html) | `default`, `discovery`, `safe` | Perform NetBIOS node status queries against UDP port `137`. |

- Execute targeted discovery scripts to extract OS, security modes, and NetBIOS metadata:

```bash
sudo nmap -Pn -p 139,445 --script smb-os-discovery,smb-security-mode,nbstat 10.10.11.5
```

>[!example]-
> ```bash
> sudo nmap -Pn -sV -p 139,445 --script smb-os-discovery,smb-security-mode 10.129.203.6
> ```
> 
> ```bash
> Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-04-01 10:15 UTC
> Nmap scan report for 10.129.203.6
> Host is up (0.076s latency).
> 
> PORT    STATE SERVICE     VERSION
> 139/tcp open  netbios-ssn Samba smbd 4.6.2
> 445/tcp open  netbios-ssn Samba smbd 4.6.2
> 
> Host script results:
> | smb-os-discovery: 
> |   OS: Linux/Unix (Samba 4.6.2)
> |   Computer name: attcsvc-linux
> |   NetBIOS computer name: ATTCSVC-LINUX\x00
> |   Domain name: \x00
> |   FQDN: attcsvc-linux
> |_  System time: 2026-04-01T10:15:22+00:00
> | smb-security-mode: 
> |   account_used: <blank>
> |   authentication_level: user
> |   challenge_response: supported
> |_  message_signing: disabled (dangerous, but default)
> 
> Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
> Nmap done: 1 IP address (1 host up) scanned in 3.42 seconds
> ```

### NetBIOS name resolution and node status queries

- [`nbtscan`](https://github.com/resurrecting-open-source-projects/nbtscan) scans IP networks for NetBIOS name information by sending NetBIOS status queries to UDP port `137`.
- Scan a single target host for NetBIOS names:

```bash
nbtscan -r 10.10.11.5
```

- Scan an entire CIDR subnet for active NetBIOS hosts:

```bash
nbtscan -r 10.10.11.0/24
```

| Option | Description |
| :--- | :--- |
| `-r` | Use local port 137 for scans to satisfy legacy NetBIOS firewalls. |
| `-v` | Verbose mode; display all names in the target's NetBIOS name table. |
| `-h` | Display human-readable help and option definitions. |

- [`nmblookup`](https://www.samba.org/samba/docs/current/man-html/nmblookup.1.html) performs NetBIOS node status queries and maps NetBIOS names to IP addresses.
- Perform a NetBIOS node status query against a target IP address:

```bash
nmblookup -A 10.10.11.5
```

- Query the master browser and workgroup name across the broadcast domain:

```bash
nmblookup -M '*'
```

| Option | Description |
| :--- | :--- |
| `-A` | Query node status for the specified IP address. |
| `-M` | Query master browser on the local broadcast subnet. |
| `-S` | Query node status and display full table information. |
| `-r` | Bind to UDP port 137 to send queries. |

>[!note]- Common NetBIOS name suffixes
> - The 16th byte of a NetBIOS name indicates the registered service role:
> 
> | Suffix | Record type | Service role |
> | :--- | :--- | :--- |
> | `<00>` | Unique | Workstation Service (computer name) |
> | `<00>` | Group | Domain / Workgroup Name |
> | `<03>` | Unique | Windows Messenger Service |
> | `<06>` | Unique | Remote Access Service (RAS) Server |
> | `<1B>` | Unique | Domain Master Browser (PDC) |
> | `<1C>` | Group | Domain Controllers for an Active Directory domain |
> | `<1D>` | Unique | Master Browser for the local subnet |
> | `<1E>` | Group | Browser Service Elections |
> | `<20>` | Unique | File Server Service (SMB Server) |

### Enumerating shares and permissions with SMBMap

- [`SMBMap`](https://github.com/ShawnDEvans/smbmap) is an automated SMB share and permission enumerator.
- Enumerate shares and effective permissions via null session:

```bash
smbmap -H 10.10.11.5
```

- Enumerate shares and effective permissions with user credentials:

```bash
smbmap -H 10.10.11.5 -u jdoe -p 'passwd123'
```

- Enumerate shares against a specific Active Directory domain:

```bash
smbmap -H 10.10.11.5 -u jdoe -p 'passwd123' -d example.com
```

- Authenticate using an NT hash ([[Pass-the-Hash]]):

```bash
smbmap -H 10.10.11.5 -u jdoe -p 'aad3b435b51404eeaad3b435b51404ee:2b576acfd5e0c865136732c44b49b6b1'
```

- List files and directories recursively across all accessible shares:

```bash
smbmap -H 10.10.11.5 -u jdoe -p 'passwd123' -r
```

- List files recursively inside a specific share:

```bash
smbmap -H 10.10.11.5 -u jdoe -p 'passwd123' -s finance -r
```

- Download a remote file from a share:

```bash
smbmap -H 10.10.11.5 -u jdoe -p 'passwd123' -s finance --download 'finance\confidential.docx'
```

- Upload a local file to a writable share:

```bash
smbmap -H 10.10.11.5 -u jdoe -p 'passwd123' -s shared --upload /tmp/payload.exe 'shared\payload.exe'
```

- Execute a remote command via WMI or PsExec (requires administrative privileges):

```bash
smbmap -H 10.10.11.5 -u jdoe -p 'passwd123' -x 'whoami /priv'
```

- `smbmap` option reference:

| Option | Description |
| :--- | :--- |
| `-H <host>` | Target IP address or hostname. |
| `--host-file <file>` | File containing list of target IP addresses/hostnames. |
| `-u <username>` | Username for authentication (omitted for null session). |
| `-p <password>` | Plaintext password or NT hash for Pass-the-Hash; format: `LM_hash:NT_hash`. |
| `-d <domain>` | Domain or workgroup name. |
| `-P <port>` | Destination SMB port (default: `445`). |
| `-s <share>` | Target specific share name. |
| `-r` | Recursively list directories and files. |
| `--depth <depth>` | Maximum directory recursion depth (default: `1`). |
| `--download <path>` | Download specified remote file path. |
| `--upload <src> <dst>` | Upload local file to remote destination path. |
| `--delete <path>` | Delete specified remote file from share. |
| `-x <command>` | Execute operating system command on target host. |
| `-L` | List all local drives on the host (requires administrative privileges). |
| `-A <pattern>` | Regex search pattern to auto-download matching files during recursive scans. |
| `-q` | Quiet mode; display only shares with `READ` or `WRITE` access. |
| `--signing` | Check whether SMB signing is disabled, enabled, or required. |

### Enumerating with NetExec

- [NetExec (`netexec`)](https://www.netexec.wiki/) (active fork of CrackMapExec) automates SMB enumeration, credential validation, and share discovery across enterprise networks.
- Enumerate SMB version, domain details, signing configuration, and accessible shares via null session:

```bash
netexec smb 10.10.11.5 --shares
```

- Enumerate shares and permissions with valid credentials:

```bash
netexec smb 10.10.11.5 -u jdoe -p 'passwd123' --shares
```

- Enumerate active logged-on user sessions:

```bash
netexec smb 10.10.11.5 -u jdoe -p 'passwd123' --loggedon-users
```

- Enumerate local user accounts via SAM:

```bash
netexec smb 10.10.11.5 -u jdoe -p 'passwd123' --users
```

- Enumerate domain groups:

```bash
netexec smb 10.10.11.5 -u jdoe -p 'passwd123' --groups
```

- Retrieve domain password policy (lockout thresholds, history, complexity):

```bash
netexec smb 10.10.11.5 -u jdoe -p 'passwd123' --pass-pol
```

- Authenticate against local accounts (`--local-auth` bypasses domain authentication):

```bash
netexec smb 10.10.11.5 -u Administrator -p 'passwd123' --local-auth --shares
```

- Execute a remote command via CMD (requires local administrative privileges):

```bash
netexec smb 10.10.11.5 -u Administrator -p 'passwd123' --local-auth -x 'whoami'
```

- Execute a remote PowerShell command:

```bash
netexec smb 10.10.11.5 -u Administrator -p 'passwd123' --local-auth -X 'Get-Process'
```

- `netexec smb` option reference:

| Option | Description |
| :--- | :--- |
| `smb` | Select SMB protocol module. |
| `-u <user>` | Single username or path to user wordlist file. |
| `-p <pass>` | Single password, NT hash, or path to password wordlist file. |
| `-d <domain>` | Domain name (defaults to local hostname/workgroup). |
| `--local-auth` | Authenticate against the target's local SAM database instead of Active Directory. |
| `--shares` | Enumerate SMB shares and test read/write permissions. |
| `--users` | Enumerate users via RPC SAMR. |
| `--groups` | Enumerate domain security groups. |
| `--loggedon-users` | Enumerate currently logged on user accounts. |
| `--pass-pol` | Query domain password and lockout policy settings. |
| `--rid-brute [<max>]` | Enumerate accounts by brute-forcing Relative Identifiers (RIDs). |
| `-x <command>` | Execute operating system command via standard Windows methods. |
| `-X <ps_command>` | Execute PowerShell command string. |
| `--continue-on-success` | Continue testing subsequent credentials after finding a valid login. |

### Automated enumeration with enum4linux-ng

- [`enum4linux-ng`](https://github.com/cddmp/enum4linux-ng) is a Python-based utility that extracts system information, user accounts, groups, password policies, and share ACLs over SMB and RPC.
- Execute full automated enumeration against target host:

```bash
enum4linux-ng -A 10.10.11.5
```

- Execute short enumeration (skips slow NetBIOS name lookups and RPC bruteforcing):

```bash
enum4linux-ng -As 10.10.11.5
```

- Run authenticated full enumeration:

```bash
enum4linux-ng -A -u jdoe -p 'passwd123' 10.10.11.5
```

- Enumerate users via RID cycling (brute-forces RID values from `500` to `1100`):

```bash
enum4linux-ng -R 10.10.11.5
```

- Enumerate specific components via targeted flags:

```bash
enum4linux-ng -U 10.10.11.5   # Enumerate users via RPC
enum4linux-ng -G 10.10.11.5   # Enumerate groups
enum4linux-ng -Gm 10.10.11.5  # Enumerate groups and their members
enum4linux-ng -S 10.10.11.5   # Enumerate shares and check permissions
enum4linux-ng -P 10.10.11.5   # Retrieve password policy
enum4linux-ng -O 10.10.11.5   # Extract OS version and build metadata
enum4linux-ng -L 10.10.11.5   # Query domain metadata via LDAP/LDAPS (Domain Controllers)
enum4linux-ng -I 10.10.11.5   # Enumerate shared printers
```

- Output enumeration findings to JSON format for automated processing:

```bash
enum4linux-ng -A -oJ /tmp/enum_smb_results.json 10.10.11.5
```

- `enum4linux-ng` option reference:

| Option | Description |
| :--- | :--- |
| `-A` | Run all enumeration checks (users, groups, shares, policies, OS, NetBIOS, RID cycle). |
| `-As` | Run short enumeration checks (omits NetBIOS scan and deep RID brute-force). |
| `-U` | Enumerate users via SAMR RPC (`querydispinfo` and `enumdomusers`). |
| `-G` | Enumerate local, builtin, and domain security groups. |
| `-Gm` | Enumerate groups along with their associated member accounts. |
| `-S` | Enumerate shares and test read/write access per share. |
| `-P` | Query password policy (minimum length, complexity, lockout thresholds). |
| `-O` | Retrieve OS information, version, and architecture. |
| `-L` | Query domain information via LDAP/LDAPS (for Active Directory DCs). |
| `-I` | Query printer information. |
| `-N` | Query NetBIOS name table (`nmblookup`). |
| `-R [<ranges>]` | Enumerate users and groups via RID cycling (default range: `500-1100`). |
| `-u <user>` | Username for authenticated RPC sessions. |
| `-p <pass>` | Password for authenticated RPC sessions. |
| `-d <domain>` | Custom domain or workgroup name. |
| `-oJ <file>` | Output results to JSON file. |
| `-oY <file>` | Output results to YAML file. |

## Assessing null sessions and guest access

> A **null session** is an unauthenticated SMB connection established with an empty username (`""`) and an empty password (`""`) against the `IPC$` share (`\\10.10.11.5\IPC$`).

- Null sessions allow unauthenticated clients to bind to named pipes and execute RPC queries against SAMR, LSA, and Netlogon services.
- While restricted by default in Windows Server 2003+ and modern Windows desktop builds, null sessions frequently succeed on Samba configurations, legacy devices, NAS appliances, and unhardened enterprise servers.

### Testing null sessions with smbclient

- List exported shares using a null session (`-N` flag disables password prompt):

```bash
smbclient -L //10.10.11.5 -N
```

- Attempt direct connection to a discovered share via null session:

```bash
smbclient //10.10.11.5/public -N
```

- Attempt connection using anonymous guest credentials:

```bash
smbclient -L //10.10.11.5 -U 'anonymous%'
```

```bash
smbclient //10.10.11.5/public -U 'guest%'
```

>[!example]-
> ```bash
> smbclient -L //10.129.203.6 -N
> ```
> 
> ```bash
> 	Sharename       Type      Comment
> 	---------       ----      -------
> 	print$          Disk      Printer Drivers
> 	public          Disk      Public Department Share
> 	IPC$            IPC       IPC Service (attcsvc-linux Samba)
> SMB1 disabled -- no workgroup available
> ```

### Testing null sessions with SMBMap

- Check share accessibility and permissions via null session:

```bash
smbmap -H 10.10.11.5 -u '' -p ''
```

- Check share accessibility using the `anonymous` account:

```bash
smbmap -H 10.10.11.5 -u 'anonymous' -p ''
```

### Testing null sessions with NetExec

- Validate unauthenticated access across target host:

```bash
netexec smb 10.10.11.5 -u '' -p '' --shares
```

```bash
netexec smb 10.10.11.5 -u 'guest' -p '' --shares
```

### Testing null sessions with Nmap

- Probe share permissions via the `smb-enum-shares` NSE script:

```bash
nmap -p 445 --script smb-enum-shares --script-args smbusername='',smbpassword='' 10.10.11.5
```

## Enumerating via RPC over SMB

### RPC over SMB architecture and named pipes

> **MS-RPCE (Microsoft Remote Procedure Call Protocol Extensions)** enables application components to execute procedures across remote hosts by encapsulating RPC data inside SMB transactions over the `IPC$` share.

- The client connects to `\\10.10.11.5\IPC$` and opens a **named pipe** (`\pipe\<service>`).
- Each named pipe maps to a specific Windows operating system service interface:

| Named pipe | Service interface | Information and capabilities exposed |
| :--- | :--- | :--- |
| `\pipe\samr` | Security Account Manager (SAM) | User enumeration, RID lookup, group memberships, password policy. |
| `\pipe\lsarpc` | Local Security Authority (LSA) | Security identifiers (SIDs), account privileges, domain trusts, audit policies. |
| `\pipe\srvsvc` | Server Service | Share definitions, active sessions, connected client IP addresses. |
| `\pipe\winreg` | Remote Registry Service | Windows Registry querying and key manipulation. |
| `\pipe\netlogon` | Netlogon Service | Domain authentication validation, secure channel management. |
| `\pipe\svcctl` | Service Control Manager (SCM) | Remote Windows service creation, configuration, start/stop (used for PsExec execution). |
| `\pipe\spoolss` | Print Spooler Service | Printer driver management; target of PrintNightmare exploitation. |

### Interactive RPC enumeration with rpcclient

- [`rpcclient`](https://www.samba.org/samba/docs/current/man-html/rpcclient.1.html) provides an interactive shell for executing raw MS-RPC commands over SMB named pipes.
- Connect via null session:

```bash
rpcclient -U '%' 10.10.11.5
```

- Connect with authenticated user credentials:

```bash
rpcclient -U 'jdoe%passwd123' 10.10.11.5
```

- Connect using domain credentials:

```bash
rpcclient -U 'example.com\jdoe%passwd123' 10.10.11.5
```

- Key `rpcclient` command reference:

| Command | Description |
| :--- | :--- |
| `srvinfo` | Query server operating system, platform ID, and server type flags. |
| `querydominfo` | Query domain name, total user count, server role, and sequence number. |
| `getdompwinfo` | Query password policy properties and minimum password length. |
| `enumdomusers` | Enumerate all user accounts returning RID and username pairs. |
| `queryuser <RID>` | Retrieve detailed metadata for a user account (logon time, description, groups). |
| `querydispinfo` | Retrieve list of user accounts with descriptive comments. |
| `enumdomgroups` | Enumerate all domain groups with their corresponding RIDs. |
| `querygroup <RID>` | Retrieve group metadata and attributes for a specified RID. |
| `querygroupmem <RID>` | Retrieve user RIDs belonging to a specified group. |
| `lsaenumsid` | Enumerate LSA security identifiers (SIDs) registered on the host. |
| `lookupsids <SID>` | Resolve an arbitrary SID into its associated username or group name. |
| `lookupnames <username>` | Resolve a username into its corresponding SID. |
| `netshareenumall` | Enumerate all exported network shares including administrative hidden shares. |
| `netsharegetinfo <share>` | Retrieve detailed path, permissions, and comment metadata for a share. |
| `enumalsgroups domain` | Enumerate local alias groups. |
| `samlookupnames <domain> <user>` | Resolve username to RID via SAMR interface. |
| `samlookuprids <domain> <RID>` | Resolve RID to username via SAMR interface. |

>[!tip]+
> - Enumerate users by looping through Relative Identifiers (RIDs) non-interactively using `rpcclient`:
> 
> ```bash
> for i in $(seq 500 1100); do rpcclient -N -U '%' 10.10.11.5 -c "queryuser 0x$(printf '%x' $i)" 2>/dev/null | grep 'User Name' && echo "RID: $i"; done
> ```

### Automated RPC enumeration with Impacket

- [`Impacket`](https://github.com/fortra/impacket) provides dedicated Python utilities for querying MS-RPC endpoints over SMB:
- Enumerate domain and local accounts via RID cycling with `lookupsid.py`:

```bash
lookupsid.py anonymous@10.10.11.5
```

```bash
lookupsid.py example.com/jdoe:passwd123@10.10.11.5
```

- Dump user accounts and password policies via SAMR named pipes with `samrdump.py`:

```bash
samrdump.py anonymous@10.10.11.5
```

```bash
samrdump.py example.com/jdoe:passwd123@10.10.11.5
```

- Enumerate registered RPC endpoints and bound interfaces with `rpcdump.py`:

```bash
rpcdump.py 10.10.11.5
```

| Option | Description |
| :--- | :--- |
| `-target-ip` | Explicit target IP address. |
| `-port` | Destination SMB port (default `445`). |
| `-hashes` | NT hash to use for authentication (Pass-the-Hash); format: `LM_hash:NT_hash`. |
| `-no-pass` | Suppress the password prompt (useful for Kerberos authentication or null sessions). |

## Brute-forcing credentials

>[!important] Always inspect the domain or local password policy (`--pass-pol` via `netexec` or `getdompwinfo` via `rpcclient`) prior to initiating brute-force attacks. If an **account lockout threshold** is active, password spraying should be prioritized over dictionary attacks to avoid locking domain accounts.

### Password spraying and brute-forcing with NetExec

- Password spray a single password against a list of usernames across a subnet:

```bash
netexec smb 10.10.11.0/24 -u usernames.txt -p 'passwd123' --no-bruteforce
```

- Brute-force local user accounts against a single target:

```bash
netexec smb 10.10.11.5 -u usernames.txt -p /usr/share/wordlists/rockyou.txt --local-auth
```

- Brute-force domain credentials against an Active Directory target:

```bash
netexec smb 10.10.11.5 -u usernames.txt -p /usr/share/wordlists/rockyou.txt -d example.com
```

- Test credentials and continue after finding valid accounts:

```bash
netexec smb 10.10.11.5 -u usernames.txt -p /usr/share/wordlists/rockyou.txt --continue-on-success
```

### Brute-forcing with Hydra

- Brute-force a single user against an SMB service:

```bash
hydra -l jdoe -P /usr/share/wordlists/rockyou.txt smb://10.10.11.5
```

- Brute-force a list of usernames and passwords:

```bash
hydra -L usernames.txt -P /usr/share/wordlists/rockyou.txt smb://10.10.11.5
```

- Brute-force SMB credentials on a non-standard port:

```bash
hydra -L usernames.txt -P /usr/share/wordlists/rockyou.txt -s 4455 10.10.11.5 smb
```

| Option | Description                                                                                      |
| :----- | :----------------------------------------------------------------------------------------------- |
| `-l`   | Single username to test.                                                                         |
| `-L`   | Path to wordlist containing target usernames.                                                    |
| `-p`   | Single password to test.                                                                         |
| `-P`   | Path to wordlist containing passwords.                                                           |
| `-s`   | Specify non-standard destination port.                                                           |
| `-t`   | Number of concurrent connection tasks (default: `16`; reduce for SMB to avoid crashing service). |
| `-vV`  | Enable very verbose output showing every attempt.                                                |

### Brute-forcing with Medusa

- Brute-force SMB accounts using Medusa:

```bash
medusa -M smb -h 10.10.11.5 -u jdoe -P /usr/share/wordlists/rockyou.txt -e ns
```

- Brute-force user and password lists across multiple target threads:

```bash
medusa -M smb -h 10.10.11.5 -U usernames.txt -P /usr/share/wordlists/rockyou.txt -t 4 -e ns
```

| Option  | Description                                                                             |
| :------ | :-------------------------------------------------------------------------------------- |
| `-M`    | Specify service module name (`smb`).                                                    |
| `-h`    | Target IP address or hostname.                                                          |
| `-u`    | Single username to test.                                                                |
| `-U`    | File containing list of usernames.                                                      |
| `-p`    | Single password to test.                                                                |
| `-P`    | File containing password dictionary.                                                    |
| `-e ns` | Test additional passwords (`n` for empty password, `s` for password equal to username). |
| `-t`    | Number of concurrent execution threads.                                                 |

### Brute-forcing with Nmap

- Perform dictionary attack using the `smb-brute` NSE script:

```bash
nmap -p 445 --script smb-brute --script-args userdb=usernames.txt,passdb=/usr/share/wordlists/rockyou.txt 10.10.11.5
```

| Option | Description |
| :--- | :--- |
| `-p 445` | Specify SMB port. |
| `--script smb-brute` | Execute Nmap SMB brute-force script. |
| `--script-args` | Pass `userdb` and `passdb` wordlist file paths. |

### Testing credentials with Metasploit

- Validate SMB credentials across multiple targets using Metasploit:

```bash
msfconsole -q -x "use auxiliary/scanner/smb/smb_login; set RHOSTS 10.10.11.5; set USER_FILE usernames.txt; set PASS_FILE /usr/share/wordlists/rockyou.txt; set STOP_ON_SUCCESS true; run; exit"
```

| Option | Description |
| :--- | :--- |
| `RHOSTS` | Target IP address or CIDR network range. |
| `USER_FILE` | Path to username wordlist file. |
| `PASS_FILE` | Path to password wordlist file. |
| `STOP_ON_SUCCESS` | Stop testing once a valid credential pair is discovered. |
| `BLANK_PASSWORDS` | Attempt login with empty passwords (`true`/`false`). |
| `USER_AS_PASS` | Attempt login using the username as the password (`true`/`false`). |

## Interacting with SMB shares

### Interactive and non-interactive sessions with smbclient

- [`smbclient`](https://www.samba.org/samba/docs/current/man-html/smbclient.1.html) is the standard Linux client for connecting to SMB shares.
- Connect to an SMB share interactively with username and password:

```bash
smbclient //10.10.11.5/finance -U jdoe%passwd123
```

- Connect to an SMB share specifying an Active Directory domain:

```bash
smbclient //10.10.11.5/finance -U jdoe -W example.com
```

- Connect to an SMB share on a non-standard port:

```bash
smbclient //10.10.11.5/finance -U jdoe%passwd123 -p 4455
```

- Authenticate using an NT hash string:

```bash
smbclient //10.10.11.5/finance -U jdoe --pw-nt-hash 2b576acfd5e0c865136732c44b49b6b1
```

- Execute non-interactive commands against the share:

```bash
smbclient //10.10.11.5/finance -U jdoe%passwd123 -c 'ls; get budget.xlsx'
```

- Download all files recursively using tar mode:

```bash
smbclient //10.10.11.5/finance -U jdoe%passwd123 -Tc backup_finance.tar
```

- Key interactive `smbclient` session commands:

| Command | Description |
| :--- | :--- |
| `ls` / `dir` | List files and folders in the current remote working directory. |
| `cd <dir>` | Change remote directory on the share. |
| `pwd` | Display current remote working directory path. |
| `lcd <dir>` | Change local working directory on the client machine. |
| `lpwd` | Display current local working directory path. |
| `get <file> [<local>]` | Download remote file to local machine. |
| `mget <mask*>` | Download multiple files matching wildcard pattern. |
| `put <local> [<remote>]` | Upload local file to remote share directory. |
| `mput <mask*>` | Upload multiple local files matching wildcard pattern. |
| `mkdir <dir>` | Create new directory on remote share. |
| `rmdir <dir>` | Remove directory on remote share. |
| `rm <file>` | Delete specified file on remote share. |
| `rename <old> <new>` | Rename remote file on share. |
| `allinfo <file>` | Display full file metadata, timestamps, and attributes. |
| `more <file>` | View contents of remote text file without downloading. |
| `recurse ON` | Toggle recursive mode on for wildcard operations (`mget`/`mput`). |
| `prompt OFF` | Disable interactive confirmation prompts during multi-file transfers. |
| `! <cmd>` | Execute local shell command without exiting `smbclient`. |
| `exit` / `quit` | Close active SMB connection and exit client. |

>[!tip]+
> - Download all files from an SMB directory without prompting for individual confirmations:
> 
> ```text
> smbclient> recurse ON
> smbclient> prompt OFF
> smbclient> mget *
> ```

### Automated file transfers and management with SMBMap

- Recursively download all files that match a specific filename pattern:

```bash
smbmap -H 10.10.11.5 -u jdoe -p 'passwd123' -s finance -r -A '(config|backup|password|secret)'
```

- Delete a remote file from an SMB share:

```bash
smbmap -H 10.10.11.5 -u jdoe -p 'passwd123' -s shared --delete 'shared\payload.exe'
```

## Mounting SMB shares locally

- Mount a remote SMB share directly to a local Linux mount point using CIFS:

```bash
sudo mkdir -p /mnt/smb
sudo mount -t cifs //10.10.11.5/finance /mnt/smb -o username=jdoe,password=passwd123,domain=example.com
```

- Mount using an external credentials file (avoids leaking credentials in command history):

```bash
sudo mount -t cifs //10.10.11.5/finance /mnt/smb -o credentials=/etc/smbcredentials
```

- Format of the credentials file (`/etc/smbcredentials`):

```text
username=jdoe
password=passwd123
domain=example.com
```

- Unmount a mounted SMB share:

```bash
sudo umount /mnt/smb
```

## Remote code execution via SMB

>[!note] See [[Privileged remote access#SMB]].
## References and further reading

- [`MS-SMB: Server Message Block (SMB) Protocol Specification`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-smb/)
- [`MS-SMB2: Server Message Block (SMB) Protocol Versions 2 and 3 Specification`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-smb2/)
- [`MS-CIFS: Common Internet File System (CIFS) Protocol Specification`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-cifs/)
- [`MS-RPCE: Remote Procedure Call Protocol Extensions`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-rpce/)
- [`The Basics of SMB Signing — Microsoft Learn`](https://learn.microsoft.com/en-us/archive/blogs/josebda/the-basics-of-smb-signing-covering-both-smb1-and-smb2)
- [`NetExec (netexec) Official Documentation`](https://www.netexec.wiki/)
- [`Impacket GitHub Repository & Documentation`](https://github.com/fortra/impacket)
- [`SMBMap GitHub Repository`](https://github.com/ShawnDEvans/smbmap)
- [`enum4linux-ng GitHub Repository`](https://github.com/cddmp/enum4linux-ng)
- [`Samba smbclient Manual Page`](https://www.samba.org/samba/docs/current/man-html/smbclient.1.html)
- [`Samba rpcclient Manual Page`](https://www.samba.org/samba/docs/current/man-html/rpcclient.1.html)
- [`Samba smb.conf Manual Page`](https://www.samba.org/samba/docs/current/man-html/smb.conf.5.html)
- [`445 - Pentesting SMB — HackTricks`](https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-smb/index.html)
- [`139,445 - Pentesting SMB — Hackviser`](https://hackviser.com/tactics/pentesting/services/smb)
- [`A Little Guide to SMB Enumeration — Hacking Articles`](https://www.hackingarticles.in/a-little-guide-to-smb-enumeration/)

## Appendix A: Samba server configuration

- The primary configuration file for Samba daemons (`smbd` and `nmbd`) is located at `/etc/samba/smb.conf`.
- Inspect active configuration parameters (stripping comments and blank lines):

```bash
grep -v "^\s*#" /etc/samba/smb.conf | grep -v "^\s*;" | grep -v "^\s*$"
```

- Key global and share configuration settings:

| Directive | Scope | Default | Description |
| :--- | :--- | :--- | :--- |
| `[global]` | Global | N/A | Section header defining global server parameters. |
| `workgroup` | Global | `WORKGROUP` | NetBIOS workgroup or Active Directory domain name announced by the server. |
| `server string` | Global | `Samba Server` | Descriptive banner string returned in NetBIOS and SMB responses. |
| `server min protocol` | Global | `SMB2_02` | Minimum SMB protocol dialect accepted by the server (`NT1`, `SMB2`, `SMB3`). |
| `server max protocol` | Global | `SMB3` | Maximum SMB protocol dialect supported by the server. |
| `server signing` | Global | `auto` | Configure SMB signing requirement (`disabled`, `auto`, `mandatory`). |
| `map to guest` | Global | `Never` | `Bad User` maps failed authentications to guest account; enables null/anonymous access. |
| `interfaces` | Global | All | Restrict listening sockets to specific network interfaces or IP/CIDR ranges. |
| `bind interfaces only` | Global | `no` | Force Samba to bind strictly to interfaces declared in `interfaces`. |
| `[sharename]` | Share | N/A | Share definition header exported to connecting clients. |
| `path` | Share | N/A | Local filesystem path exposed by the share (e.g. `/srv/samba/share`). |
| `browseable` | Share | `yes` | `yes` advertises share in directory listings; `no` hides share (requires exact path). |
| `read only` | Share | `yes` | `yes` prevents write operations; `no` permits file modification if filesystem ACLs allow. |
| `guest ok` / `public` | Share | `no` | `yes` permits unauthenticated connections to the share without password. |
| `valid users` | Share | All | List of specific users or `@groups` permitted to access the share. |
| `write list` | Share | None | List of specific users or `@groups` granted write permissions on a read-only share. |
| `create mask` | Share | `0744` | Octal permission mask applied to newly created files. |
| `directory mask` | Share | `0755` | Octal permission mask applied to newly created directories. |

- Dangerous Samba configuration settings:

| Directive | Dangerous value | Security impact |
| :--- | :--- | :--- |
| `map to guest` | `Bad User` | Automatically degrades invalid credential attempts to guest access, exposing guest shares. |
| `guest ok` | `yes` | Enables unauthenticated access to the share without credential validation. |
| `read only` | `no` | Enables write, modification, and deletion access on the share. |
| `browseable` | `yes` | Exposes share name in unauthenticated share enumeration queries. |
| `ntlm auth` | `yes` / `ntlmv1-permitted` | Allows legacy, insecure NTLMv1 challenge-response authentication. |
| `server signing` | `disabled` | Disables packet signing, leaving SMB connections vulnerable to NTLM relaying. |

## Appendix B: smbclient commands reference

| Command category         | Command         | Syntax                   | Description                                         |
| :----------------------- | :-------------- | :----------------------- | :-------------------------------------------------- |
| **Directory navigation** | `ls` / `dir`    | `ls [mask]`              | List files in current remote directory.             |
|                          | `cd`            | `cd <dir>`               | Change current remote working directory.            |
|                          | `pwd`           | `pwd`                    | Print current remote working directory path.        |
|                          | `lcd`           | `lcd <local_dir>`        | Change local working directory on client.           |
|                          | `lpwd`          | `lpwd`                   | Print local working directory path on client.       |
| **File management**      | `get`           | `get <remote> [<local>]` | Download remote file to local host.                 |
|                          | `mget`          | `mget <mask*>`           | Download multiple files matching pattern.           |
|                          | `put`           | `put <local> [<remote>]` | Upload local file to remote share.                  |
|                          | `mput`          | `mput <mask*>`           | Upload multiple files matching pattern.             |
|                          | `mkdir`         | `mkdir <dir>`            | Create new remote directory on share.               |
|                          | `rmdir`         | `rmdir <dir>`            | Remove existing remote directory.                   |
|                          | `rm`            | `rm <mask*>`             | Delete remote file(s) on share.                     |
|                          | `rename`        | `rename <old> <new>`     | Rename remote file on share.                        |
| **Inspecting files**     | `allinfo`       | `allinfo <file>`         | Display full filesystem metadata and timestamps.    |
|                          | `more`          | `more <file>`            | Display text file contents through pager.           |
|                          | `stat`          | `stat <file>`            | Display POSIX stat information (UNIX extensions).   |
| **Session toggles**      | `recurse`       | `recurse [ON\|OFF]`      | Toggle directory recursion for `mget`/`mput`.       |
|                          | `prompt`        | `prompt [ON\|OFF]`       | Toggle interactive confirmation prompts.            |
|                          | `lowercase`     | `lowercase [ON\|OFF]`    | Toggle automatic lowercase conversion of filenames. |
| **Local execution**      | `!`             | `! <command>`            | Execute local shell command without disconnecting.  |
| **Session exit**         | `exit` / `quit` | `exit`                   | Terminate SMB session and close client.             |

## Appendix C: rpcclient commands reference

| Functional group | Command | Syntax | Description |
| :--- | :--- | :--- | :--- |
| **Server & domain info** | `srvinfo` | `srvinfo` | Query server OS version, build, and platform ID. |
| | `querydominfo` | `querydominfo` | Query domain name, PDC name, and user totals. |
| | `getdompwinfo` | `getdompwinfo` | Query minimum password length and policy flags. |
| | `enumdomains` | `enumdomains` | Enumerate domains known to the endpoint. |
| **User enumeration** | `enumdomusers` | `enumdomusers` | Enumerate all user accounts returning `[username] [RID]`. |
| | `queryuser` | `queryuser <RID>` | Query detailed user profile and attributes by RID. |
| | `querydispinfo` | `querydispinfo` | Query user accounts with descriptions and full names. |
| | `enumalsgroups` | `enumalsgroups domain\|builtin` | Enumerate local or builtin alias groups. |
| **Group enumeration** | `enumdomgroups` | `enumdomgroups` | Enumerate domain security groups and RIDs. |
| | `querygroup` | `querygroup <RID>` | Query group metadata and attributes by RID. |
| | `querygroupmem` | `querygroupmem <RID>` | Query member user RIDs belonging to group. |
| | `queryaliasmem` | `queryaliasmem builtin\|domain <RID>` | Query members of a specific alias group. |
| **SID & name lookup** | `lsaenumsid` | `lsaenumsid` | Enumerate LSA security identifiers (SIDs). |
| | `lookupsids` | `lookupsids <SID>` | Resolve SID to username/group string. |
| | `lookupnames` | `lookupnames <name>` | Resolve username/group string to SID. |
| | `samlookuprids` | `samlookuprids <domain> <RID>` | Resolve domain RID to name via SAMR. |
| | `samlookupnames` | `samlookupnames <domain> <name>` | Resolve name to RID via SAMR. |
| **Share enumeration** | `netshareenumall` | `netshareenumall` | Enumerate all shares (including administrative `$` shares). |
| | `netsharegetinfo` | `netsharegetinfo <share>` | Retrieve path and comment metadata for share. |
| **Session control** | `quit` / `exit` | `quit` | Close RPC session and exit. |