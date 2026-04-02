---
created: 2026-03-29
tags:
  - network_services
  - net_hack
---
## SMB

>**[SMB (Server Message Block)](https://en.wikipedia.org/wiki/Server_Message_Block)** is a network communication protocol that enables shared access to files, printers, serial ports, and other resources between nodes on a network. 

- SMB operates on a **client-server model**: a client sends requests and the server responds based on session context and access control lists.

> [!note] SMB is predominantly a Windows protocol, but Linux systems can speak it too via [Samba](https://en.wikipedia.org/wiki/Samba_\(software\)) — a free, open-source implementation of the SMB protocol stack.

- SMB can also be used for **inter-process communication (IPC)** over a network — this fact becomes very important during exploitation (see [[#RPC Over SMB]]).

## Protocol internals
### Shares

 > An **SMB share** is a named resource — a filesystem directory, printer, or IPC endpoint — exported by an SMB server and made accessible to authenticated or unauthenticated clients over a network.

- Each share carries its own **ACL (Access Control List)**. This means that two users connecting to the same server may have completely different access profiles.
- This per-share ACL is layered *on top of* the underlying filesystem permissions (e.g., NTFS) — the more restrictive of the two wins.

### Transport: direct SMB vs. SMB over NetBIOS

SMB can run in one of two transport modes:

- **Direct SMB**
	- Modern SMB runs directly over **TCP port `445`**. 
	- SMB messages are placed directly in the TCP payload.
- **SMB over NetBIOS**
	- Older implementations wrap SMB inside a *NetBIOS session* on **TCP port `139`**.
	- A NetBIOS handshake is required before any SMB communication begins.
	- NetBIOS also handles name resolution instead of DNS, using UDP ports `137` (name service) and `138` (datagram service).
	- This is deprecated but still supported for backward compatibility on many targets.

When scanning, always hit both `139` and `445`.
### SMB session lifecycle

1. **Connection establishment**
	- An SMB client initiates a TCP connection to the server on port `445`. 
	- Both sides negotiate the *SMB dialect* (version) to use. The server picks the highest dialect both parties support.

2. **Authentication**
	- The client presents credentials. The server verifies them via Kerberos (Active Directory) or NTLM (workgroups, or fallback in AD). Null sessions skip this step.

3. **Tree connect**
	- The client requests access to a specific share (`\\server\sharename`). The server issues a Tree ID (TID) and applies share-level ACLs.

4. **Resource operations**
	- The client requests standard file I/O: open, read, write, close.
	- Each operation is subject to both NTFS permissions and share permissions (again, the more restrictive of the two wins).

5. **Session termination**
	- Client sends a logoff; server tears down the session context.

### SMB versions

| Version                         | Introduced with             | Description                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ------------------------------- | --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **SMBv1** (`1.0`)               | Windows NT                  | The original SMB protocol.<br>No encryption for data in transit.<br>Vulnerable to [`MS17-010`](https://www.rapid7.com/db/modules/exploit/windows/smb/ms17_010_eternalblue/) ([`EternalBlue`](https://en.wikipedia.org/wiki/EternalBlue); was used in [`WannaCry`](https://en.wikipedia.org/wiki/WannaCry_ransomware_attack) and [`NotPetya`](https://en.wikipedia.org/wiki/2017_Ukraine_ransomware_attacks)).<br>Deprecated by Microsoft. |
| **SMBv2** (`2.0`/`2.1`)         | Windows Vista / Server 2008 | Redesigned protocol architecture; reduced attack surface compared to SMBv1.<br>Better hashing algorithms (HMAC-SHA256 for message signing).                                                                                                                                                                                                                                                                                               |
| SMBv3 (SMB `3.0`/`3.1`/`3.1.1`) | Windows 8 / Server 2012     | **End-to-end encryption** support (AES-CCM; AES-256-GCM in Windows 11/Windows Server 2022).<br>Better hashing algorithms (AES-CMAC for integrity checks).<br>Prevents downgrade attacks via dialect negotiation.                                                                                                                                                                                                                          |

> [!note] Nmap often won't tell you the exact SMB dialect on Windows targets — it returns the OS build number instead. Use `crackmapexec`/`netexec` or `enum4linux-ng` to identify the dialect precisely. On Samba (Linux), version info usually appears directly in Nmap output.

### SMB authentication

SMB supports two access models:

- **User-level authentication**
	- The client authenticates with a username and password. Access is then governed by share and filesystem ACLs. Standard in modern environments.

- **Share-level authentication**
	- Legacy; access is protected by a per-share password, no per-user identity. Rare in practice.

>[!important] Passwords are always sent encrypted under both models.

Under the hood, SMB delegates actual credential verification to one of two protocols:

- [NTLM](https://en.wikipedia.org/wiki/NTLM) (NT LAN Manager)
	- Challenge-response protocol; vulnerable to replay attacks, [[Pass-the-Hash]], and downgrade attacks. Used in workgroups and as AD fallback.
	- See [[NTLM_]].
- [Kerberos](https://en.wikipedia.org/wiki/Kerberos_\(protocol\)) 
	- Ticket-based, cryptographically secure. Preferred in Active Directory environments.
	- See [[how_Kerberos_works]].

> [!important] SMB can be configured to require _no_ authentication at all. This is called a **null session** — SMB's equivalent of FTP anonymous login. More on this [[#SMB Null Sessions|below]].


>[!interesting]+ Workgroup vs. domain 
>- **Workgroup** — a **peer-to-peer network** of nodes.
> 
> 	- No central authentication server; each machine maintains its **own local SAM database**.
> 	- User accounts exist per host, not globally.
> 	- Each machine validates its users locally.
> 	- Machines discover each other via **NetBIOS broadcast**.
> 	- NTLM authentication only; Kerberos is not supported.
> - **Domain** — a centralized, structured environment managed by **Active Directory**.
> 	- **Authentication is centralized**: all login requests are processed by a **Domain Controller (DC)**.
> 	- Uses Kerberos authentication by default, and NTLM as a fallback.
> 	- Users, groups, password policies, and Kerberos tickets are stored and managed by the DC.
> 	- **Hierarchical organization** that supports organizational units (OUs).

### Standard administrative shares

Windows automatically creates a set of **hidden administrative shares** (identified by the `$` suffix). These are built-in, can't normally be removed permanently, and are intended for remote system management. 


>[!note] The `$` suffix hides shares from casual browsing (`net view`), but they're fully accessible if you know the name.

| Share            | Maps To                             | Notes                                                                                  |
| ---------------- | ----------------------------------- | -------------------------------------------------------------------------------------- |
| `C$`, `D$`, etc. | Drive root (`C:\`, `D:\`)           | Full filesystem access. Admin-only by default.                                         |
| `ADMIN$`         | `%SystemRoot%` (`C:\Windows`)       | Used for remote admin; PsExec uploads binaries here.                                   |
| `IPC$`           | Named pipes                         | No filesystem access. Used for RPC, auth, SCM, WMI. Often accessible in null sessions. |
| `PRINT$`         | `C:\Windows\System32\spool\drivers` | Printer drivers.                                                                       |
| `SYSVOL`         | Domain controller share             | Group Policy objects, scripts. Only on DCs.                                            |
| `NETLOGON`       | DC share                            | Logon scripts for domain users. Only on DCs.                                           |


| Share                                   | Description                                                                                                                                                                                                                                                                                                                                                                                        |
| --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Disk shares: `C$`, `D$`, `$E`, etc.** | `●` Automatically created for **every drive letter** on the system.<br>`●` Provide full filesystem access on the corresponding drive (e.g., `C$` -> `C:\`).<br>`●` Used by tools like PsExec, SCCM (Microsoft Configuration Manager), backup agents, and domain admins.<br>`●` Accessible to Local Administrator, Domain Admin, and `SYSTEM`.                                                      |
| **`ADMIN$`**                            | `●` Maps to the **Windows system root directory** (`%SystemRoot%`, usually `C:\Windows`).<br>`●` Primarily used for remote management, service installation, and Windows Update deployment. <br>`●` PsExec uses `ADMIN$` to upload its service binary.<br>`●` By default, only accessible to administrators.                                                                                       |
| **`IPC$`**                              | `●` Special share used for **inter-process communication (IPC)** via **named pipes**.<br>`●` Not a real folder; exposes **named pipes**.<br>`●` Used internally for **RPC over SMB**, authentication/session setup, and remote service control (SCM, WMI, etc.).<br>`●` Often accessible in null sessions (depending on configuration) and low-privileged contexts (historically mode permissive). |
| **`PRINT$` and `FAX&`**                 | `●` `PRINT$` is used to store printer drivers, install drivers remotely, and support legacy print spooler operations. See [`CVE-2021-34527`](https://nvd.nist.gov/vuln/detail/cve-2021-34527) (`PrintNightmare` RCE).<br>`●` `FAX$` is for the fax service (rare today ~~unless you're living in Japan~~).                                                                                         |
| **`SYSVOL`**                            | `●` Exists on every DC (and DC only); stores GPOs (Group Policy Objects) and login scripts.<br>`●` Replicated across all DCs via FRS/DFSR.<br>`●` Its default location is **`C:\Windows\SYSVOL`**.                                                                                                                                                                                                 |
| **`NETLOGON`**                          | `●` Exists on every DC (and DC only); stores logon scripts, Group Policy files, and system policies.<br>`●` Replicated across all DCs via FRS/DFSR.<br>`●` Not a standalone folder, but the `scripts` subfolder in the `SYSVOL` directory.<br>`●` Its default location is `C:\Windows\SYSVOL\sysvol\<domain>\scripts`.                                                                             |

`IPC$` deserves special attention — it's the gateway to all RPC-based enumeration. If you can reach `IPC$` (even unauthenticated), you can enumerate users, groups, and shares via named pipes.

```bash
smbclient //target/IPC$ -N
```


## SMB enumeration

>[!note]+ Tools
>- [`smbclient`](https://www.samba.org/samba/docs/current/man-html/smbclient.1.html)
>- [`smbmap`](https://github.com/ShawnDEvans/smbmap)
>- `rcpclient`

### Nmap port scanning and version detection

- Nmap SMB port scanning and version detection:

```bash
sudo nmap -sV -p 139,445 <target>
```

>[!example]- 
> ```bash
> sudo nmap -sV -p 445,139 10.129.202.5
> ```
> 
> ```bash
> Starting Nmap 7.95 ( https://nmap.org ) at 2026-04-01 10:11 UTC
> Nmap scan report for 10.129.202.5
> Host is up (0.13s latency).
> 
> PORT    STATE SERVICE     VERSION
> 139/tcp open  netbios-ssn Samba smbd 4
> 445/tcp open  netbios-ssn Samba smbd 4
> 
> Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
> Nmap done: 1 IP address (1 host up) scanned in 14.08 seconds
> ```

> [!tip]+
> - Basic port scanning + version detection — in case you suspect non-standard ports:
> 
> ```bash
> sudo nmap -sV -p- <target>
> ```

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
>>[!note]+ "Message signing enabled but not required"
>>SMB signing being enabled but not required means the server _supports_ signing but doesn't _enforce_ it — requests can be sent unsigned; vulnerable to **SMB relay attacks**.

>[!warning] Depending on the SMB implementation and the underlying operating system, Nmap will return different information. 
>- When targeting Windows, SMB version information is usually not included as part of Nmap scan results.

- Run default SMB scripts:

```bash
sudo nmap -sV -sC -p 137-139,445 <target>
```

- Run all SMB scripts:

```bash
nmap --script smb* <target>
```

>[!tip]+ Nmap SMB scripts
> 
> - List available SMB scripts:
> 
> ```bash
> ls -l /usr/share/nmap/scripts/*smb*
> ```
> 

#### Targeted NSE scripts

- OS discovery ([`smb-os-discovery`](https://nmap.org/nsedoc/scripts/smb-os-discovery.html)):

```bash
nmap -Pn -p 139,445 --script smb-os-discovery <target>
```

- NetBIOS information ([`nbstat`](https://nmap.org/nsedoc/scripts/nbstat.html)):

```bash
nmap -Pn -p 139,445 --script nbstat <target>
```

>[!example]- 
> ```bash
> nmap -Pn -p 139,445 --script nbstat 10.129.27.56
> ```
> 
> ```bash
> Starting Nmap 7.95 ( https://nmap.org ) at 2026-04-01 13:07 UTC
> Nmap scan report for 10.129.27.56
> Host is up (0.13s latency).
> 
> PORT    STATE SERVICE
> 139/tcp open  netbios-ssn
> 445/tcp open  microsoft-ds
> 
> Host script results:
> | nbstat: NetBIOS name: DEVSMB, NetBIOS user: <unknown>, NetBIOS MAC: <unknown> (unknown)
> | Names:
> |   DEVSMB<00>           Flags: <unique><active>
> |   DEVSMB<03>           Flags: <unique><active>
> |   DEVSMB<20>           Flags: <unique><active>
> |   \x01\x02__MSBROWSE__\x02<01>  Flags: <group><active>
> |   DEVOPS<00>           Flags: <group><active>
> |   DEVOPS<1d>           Flags: <unique><active>
> |_  DEVOPS<1e>           Flags: <group><active>
> 
> Nmap done: 1 IP address (1 host up) scanned in 0.50 seconds
> ```
> 

- Share enumeration ([`smb-enum-shares`](https://nmap.org/nsedoc/scripts/smb-enum-shares.html), attempts null session by default):

```bash
nmap -Pn -p 139,445 --script=smb-enum-shares <target>
```

- User enumeration ([`smb-enum-users`](https://nmap.org/nsedoc/scripts/smb-enum-users.html))

```bash
nmap -p 445 --script=smb-enum-users <target>
```

- Groups ([`smb-enum-groups`](https://nmap.org/nsedoc/scripts/smb-enum-groups.html)) and domain ([`smb-enum-domains`](https://nmap.org/nsedoc/scripts/smb-enum-domains.html)) enumeration:

```bash
nmap -p 445 --script=smb-enum-groups,smb-enum-domains <target>
```

- Security settings, such as signing and authentication level ([`smb-security-mode`](https://nmap.org/nsedoc/scripts/smb-security-mode.html)):

```bash
nmap -p 445 --script=smb-security-mode <target>
```

- Check for EternalBlue ([`smb-vuln-ms17-010`](https://nmap.org/nsedoc/scripts/smb-vuln-ms17-010.html)):

```bash
nmap -p 445 --script smb-vuln-ms17-010 <target>
```

- Check for common SMB vulnerabilities:

```bash
nmap -p 445 --script smb-vuln* <target>
```
### NetBIOS name resolution
#### nbtscan

>`ntbscan` — used to scan IP networks for NetBIOS name information.

>[!note] See [[SMB tools_#nbtscan]].

- Scan a single host:

```bash
nbtscan <target>
```

- Scan a whole subnet:

```bash
nbtscan <network_address>/<prefix>
```

>[!example]+
> ```bash
> nbtscan 10.129.27.56
> ```
> 
> ```bash
> Doing NBT name scan for addresses from 10.129.27.56
> 
> IP address       NetBIOS Name     Server    User             MAC address      
> ------------------------------------------------------------------------------
> 10.129.27.56     DEVSMB           <server>  DEVSMB           00:00:00:00:00:00
> ```
#### nmblookup

 >[`nmblookup`](https://www.samba.org/samba/docs/current/man-html/nmblookup.1.html) is used to query NetBIOS names and map them to IP addresses.

>[!note] See [[SMB tools_#nmblookup]].

- Query a NetBIOS name:

```bash
nmblookup <NetBIOS_name>
```

- Query an IP address:

```bash
nmblookup -A <IP_address>
```

>[!interesting]+ `nmblookup` status query
>`nmblookup` performs a NetBIOS node status query against UDP port `137`. The target responds with its NetBIOS name table, which lists:
>- Registered NetBIOS names
>- Their type (workstation, server, domain, etc.)
>- Whether they're unique or group names
>- Whether they're active
>- Sometimes the MAC address (not always reliable).

>[!example]+
> ```bash
> nmblookup -A 10.129.27.56
> ```
> 
> ```bash
> Looking up status of 10.129.27.56
> 	DEVSMB          <00> -         H <ACTIVE> 
> 	DEVSMB          <03> -         H <ACTIVE> 
> 	DEVSMB          <20> -         H <ACTIVE> 
> 	..__MSBROWSE__. <01> - <GROUP> H <ACTIVE> 
> 	DEVOPS          <00> - <GROUP> H <ACTIVE> 
> 	DEVOPS          <1d> -         H <ACTIVE> 
> 	DEVOPS          <1e> - <GROUP> H <ACTIVE> 
> 
> 	MAC Address = 00-00-00-00-00-00
> ```
> Columns, in order:
> 1. NetBIOS name itself.
> 2. NetBIOS [suffix](http://ubiqx.org/cifs/Appendix-C.html) (16th byte of the name, in hex; shows the *type* of this name).
> 3. Unique/group indicator (`<GROUP>` -> group name, blank -> unique name).
> 4. NetBIOS node type:
> 	- `B` — Broadcast (uses broadcast only).
> 	- `P` — Peer-to-peer (Uses WINS only).
> 	- `M` — Mixed (Broadcast first, then WINS).
> 	- `H` — Hybrid (WINS first, then broadcast).
> 5. Status: Whether the name is currently registered and active (`<ACTIVE>` for active).

>[!note]- Common NetBIOS suffixes
> 
> For a complete reference, see [`Appendix C: Known NetBIOS Suffix Values — Implementing CIFS, ubiqx.com`](http://ubiqx.org/cifs/index.html#Contents)
> 
> - For unique names:
> 
> | Suffix | Name                        |
> | ------ | --------------------------- |
> | `<00>` | Workstation Service         |
> | `<03>` | Messenger Service           |
> | `<06>` | Remote Access Service (RAS) |
> | `<20>` | File Server                 |
> | `<21>` | RAS client                  |
> | `<1B>` | Domain Master Browser       |
> | `<1D>` | Master Browser              |
> 
> - For group names:
> 
> | Suffix | Name                                         |
> | ------ | -------------------------------------------- |
> | `<00>` | Workstation Service (workgroup/domain name)  |
> | `<1C>` | Domain Controllers for a domain              |
> | `<1E>` | Browser Service Elections                    |
> 

- Broadcast workgroup discovery:

```bash
nmblookup '*'
```
### Shares

#### smbclient

>[`smbclient`](https://www.samba.org/samba/docs/current/man-html/smbclient.1.html) is a tool from the Samba suite, allows Linux/Unix systems to interact with SMB/CIFS servers using an interface similar to FTP.

>[!note] See [[SMB tools_#smbclient]].

- List shares anonymously:

```bash
smbclient -L //<target> -U anonymous
```

- With credentials:

```bash
smbclient -L //<target> -U username%password
```

- Specify a domain:

```bash
smbclient -L //<target> -U domain/username%password
```

>[!example]-
> ```bash
> smbclient -L //10.129.27.56 -U anonymous
> ```
> 
> ```bash
> Password for [WORKGROUP\anonymous]:
> 
> 	Sharename       Type      Comment
> 	---------       ----      -------
> 	print$          Disk      Printer Drivers
> 	sambashare      Disk      InFreight SMB v3.1
> 	IPC$            IPC       IPC Service (InlaneFreight SMB server (Samba, Ubuntu))
> Reconnecting with SMB1 for workgroup listing.
> smbXcli_negprot_smb1_done: No compatible protocol selected by server.
> Protocol negotiation to server 10.129.27.56 (for a protocol between LANMAN1 and NT1) failed: NT_STATUS_INVALID_NETWORK_RESPONSE
> Unable to connect with SMB1 -- no workgroup available
> ```

#### smbmap

>[`SMBMap`](https://github.com/ShawnDEvans/smbmap) — SMB enumeration tool, used to identify accessible shares, permissions, and content across a network domain.

>[!note] See [[SMB tools_#smbmap]].

- List shares anonymously:

```bash
smbmap -H <target>
```

> [!example]-
> ```bash
> smbmap -H 10.129.27.56
> ```
> 
> ```bash
> 
>     ________  ___      ___  _______   ___      ___       __         _______
>    /"       )|"  \    /"  ||   _  "\ |"  \    /"  |     /""\       |   __ "\
>   (:   \___/  \   \  //   |(. |_)  :) \   \  //   |    /    \      (. |__) :)
>    \___  \    /\  \/.    ||:     \/   /\   \/.    |   /' /\  \     |:  ____/
>     __/  \   |: \.        |(|  _  \  |: \.        |  //  __'  \    (|  /
>    /" \   :) |.  \    /:  ||: |_)  :)|.  \    /:  | /   /  \   \  /|__/ \
>   (_______/  |___|\__/|___|(_______/ |___|\__/|___|(___/    \___)(_______)
> -----------------------------------------------------------------------------
> SMBMap - Samba Share Enumerator v1.10.7 | Shawn Evans - ShawnDEvans@gmail.com
>                      https://github.com/ShawnDEvans/smbmap
> 
> [*] Detected 1 hosts serving SMB                                                                                                  
> [*] Established 1 SMB connections(s) and 0 authenticated session(s)                                                          
>                                                                                                                              
> [+] IP: 10.129.27.56:445	Name: 10.129.27.56        	Status: NULL Session
> 	Disk                                                  	Permissions	Comment
> 	----                                                  	-----------	-------
> 	print$                                            	NO ACCESS	Printer Drivers
> 	sambashare                                        	READ ONLY	InFreight SMB v3.1
> 	IPC$                                              	NO ACCESS	IPC Service (InlaneFreight SMB server (Samba, Ubuntu))
> [*] Closed 1 connections
> ```

>[!note] `Permissions` column
> - `READ ONLY`: You can browse the share and download files.
> - `READ, WRITE`: You can browse the share, download and upload files.
> - `NO ACCESS`: Means exactly that.

- With credentials: 

```bash
smbmap -H <target> -u username -p password
```

- Specify a domain:

```bash
smbmap -H <target> -u username -p password -d domain
```


- Use NT has instead of a password ([[Pass-the-Hash]]):

```bash
smbmap -H <target> -u username -p 'LMHASH:NTHASH'
```

- Recursive listing:

```bash
smbmap -H <target> -u username -p password -r
```

>[!example]- 
> ```bash
> mbmap -H 10.129.27.56 -r
> ```
> 
> ```bash
> 
>     ________  ___      ___  _______   ___      ___       __         _______
>    /"       )|"  \    /"  ||   _  "\ |"  \    /"  |     /""\       |   __ "\
>   (:   \___/  \   \  //   |(. |_)  :) \   \  //   |    /    \      (. |__) :)
>    \___  \    /\  \/.    ||:     \/   /\   \/.    |   /' /\  \     |:  ____/
>     __/  \   |: \.        |(|  _  \  |: \.        |  //  __'  \    (|  /
>    /" \   :) |.  \    /:  ||: |_)  :)|.  \    /:  | /   /  \   \  /|__/ \
>   (_______/  |___|\__/|___|(_______/ |___|\__/|___|(___/    \___)(_______)
> -----------------------------------------------------------------------------
> SMBMap - Samba Share Enumerator v1.10.7 | Shawn Evans - ShawnDEvans@gmail.com
>                      https://github.com/ShawnDEvans/smbmap
> 
> [*] Detected 1 hosts serving SMB                                                                                                  
> [*] Established 1 SMB connections(s) and 0 authenticated session(s)                                                          
>                                                                                                                              
> [+] IP: 10.129.27.56:445	Name: 10.129.27.56        	Status: NULL Session
> 	Disk                                                  	Permissions	Comment
> 	----                                                  	-----------	-------
> 	print$                                            	NO ACCESS	Printer Drivers
> 	sambashare                                        	READ ONLY	InFreight SMB v3.1
> 	./sambashare
> 	dr--r--r--                0 Mon Nov  8 13:43:14 2021	.
> 	dr--r--r--                0 Mon Nov  8 15:53:19 2021	..
> 	fr--r--r--              807 Tue Feb 25 12:03:21 2020	.profile
> 	dr--r--r--                0 Mon Nov  8 13:43:45 2021	contents
> 	fr--r--r--              220 Tue Feb 25 12:03:21 2020	.bash_logout
> 	fr--r--r--             3771 Tue Feb 25 12:03:21 2020	.bashrc
> 	IPC$                                              	NO ACCESS	IPC Service (InlaneFreight SMB server (Samba, Ubuntu))
> [*] Closed 1 connections 
> ```

>[!tip]+
> - Download a specific file:
> 
> ```bash
> smbmap -H <target> -u username -p password --download 'sharename\path\to\file'
> ```
> 
> - Upload a file:
> 
> ```bash
> smbmap -H <target> -u username -p password --upload /local/file 'sharename\destination'
> ```
> 
> - Execute a command (requires write access or admin):
> 
> ```bash
> smbmap -H <target> -u username -p password -x 'whoami'
> ```
### enum4linux-ng

> [`enum4linux-ng`](https://github.com/cddmp/enum4linux-ng) is a Python rewrite of the original [`enum4linux`](https://www.kali.org/tools/enum4linux/) (wrapper around Samba utilities like `smbclient`, `rpcclient`, `net`, `nmblookup`), designed for comprehensive SMB/RPC enumeration.

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

>[!note] See [[SMB tools_#enum4linux-ng]]

- Do all basic enumeration including `nmblookup` (`-U -G -S -P -O -N -I -L`):

```bash
enum4linux-ng -A <target>
```

```bash
enum4linux-ng <target>
```

>[!example]-
> ```bash
> enum4linux-ng -A 10.129.202.5  
> ```
> 
> ```bash
> ENUM4LINUX - next generation (v1.3.4)
> 
>  ==========================
> |    Target Information    |
>  ==========================
> [*] Target ........... 10.129.202.5
> [*] Username ......... ''
> [*] Random Username .. 'sddkdmpq'
> [*] Password ......... ''
> [*] Timeout .......... 5 second(s)
> 
>  =====================================
> |    Listener Scan on 10.129.202.5    |
>  =====================================
> [*] Checking LDAP
> [-] Could not connect to LDAP on 389/tcp: connection refused
> [*] Checking LDAPS
> [-] Could not connect to LDAPS on 636/tcp: connection refused
> [*] Checking SMB
> [+] SMB is accessible on 445/tcp
> [*] Checking SMB over NetBIOS
> [+] SMB over NetBIOS is accessible on 139/tcp
> 
>  ===========================================================
> |    NetBIOS Names and Workgroup/Domain for 10.129.202.5    |
>  ===========================================================
> [+] Got domain/workgroup name: DEVOPS
> [+] Full NetBIOS names information:
> - DEVSMB          <00> -         H <ACTIVE>  Workstation Service
> - DEVSMB          <03> -         H <ACTIVE>  Messenger Service
> - DEVSMB          <20> -         H <ACTIVE>  File Server Service
> - ..__MSBROWSE__. <01> - <GROUP> H <ACTIVE>  Master Browser
> - DEVOPS          <00> - <GROUP> H <ACTIVE>  Domain/Workgroup Name
> - DEVOPS          <1d> -         H <ACTIVE>  Master Browser
> - DEVOPS          <1e> - <GROUP> H <ACTIVE>  Browser Service Elections
> - MAC Address = 00-00-00-00-00-00
> 
>  =========================================
> |    SMB Dialect Check on 10.129.202.5    |
>  =========================================
> [*] Trying on 445/tcp
> [+] Supported dialects and settings:
> Supported dialects:
>   SMB 1.0: false
>   SMB 2.02: true
>   SMB 2.1: true
>   SMB 3.0: true
>   SMB 3.1.1: true
> Preferred dialect: SMB 3.0
> SMB1 only: false
> SMB signing required: false
> 
>  ===========================================================
> |    Domain Information via SMB session for 10.129.202.5    |
>  ===========================================================
> [*] Enumerating via unauthenticated SMB session on 445/tcp
> [+] Found domain information via SMB
> NetBIOS computer name: DEVSMB
> NetBIOS domain name: ''
> DNS domain: ''
> FQDN: nix01
> Derived membership: workgroup member
> Derived domain: unknown
> 
>  =========================================
> |    RPC Session Check on 10.129.202.5    |
>  =========================================
> [*] Check for null session
> [+] Server allows session using username '', password ''
> [*] Check for random user
> [+] Server allows session using username 'sddkdmpq', password ''
> [H] Rerunning enumeration with user 'sddkdmpq' might give more results
> 
>  ===================================================
> |    Domain Information via RPC for 10.129.202.5    |
>  ===================================================
> [+] Domain: DEVOPS
> [+] Domain SID: NULL SID
> [+] Membership: workgroup member
> 
>  ===============================================
> |    OS Information via RPC for 10.129.202.5    |
>  ===============================================
> [*] Enumerating via unauthenticated SMB session on 445/tcp
> [+] Found OS information via SMB
> [*] Enumerating via 'srvinfo'
> [+] Found OS information via 'srvinfo'
> [+] After merging OS information we have the following result:
> OS: Linux/Unix
> OS version: '6.1'
> OS release: ''
> OS build: '0'
> Native OS: not supported
> Native LAN manager: not supported
> Platform id: '500'
> Server type: '0x809a03'
> Server type string: Wk Sv PrQ Unx NT SNT InlaneFreight SMB server (Samba, Ubuntu)
> 
>  =====================================
> |    Users via RPC on 10.129.202.5    |
>  =====================================
> [*] Enumerating users via 'querydispinfo'
> [+] Found 0 user(s) via 'querydispinfo'
> [*] Enumerating users via 'enumdomusers'
> [+] Found 0 user(s) via 'enumdomusers'
> 
>  ======================================
> |    Groups via RPC on 10.129.202.5    |
>  ======================================
> [*] Enumerating local groups
> [+] Found 0 group(s) via 'enumalsgroups domain'
> [*] Enumerating builtin groups
> [+] Found 0 group(s) via 'enumalsgroups builtin'
> [*] Enumerating domain groups
> [+] Found 0 group(s) via 'enumdomgroups'
> 
>  ======================================
> |    Shares via RPC on 10.129.202.5    |
>  ======================================
> [*] Enumerating shares
> [+] Found 3 share(s):
> IPC$:
>   comment: IPC Service (InlaneFreight SMB server (Samba, Ubuntu))
>   type: IPC
> print$:
>   comment: Printer Drivers
>   type: Disk
> sambashare:
>   comment: InFreight SMB v3.1
>   type: Disk
> [*] Testing share IPC$
> [-] Could not check share: STATUS_OBJECT_NAME_NOT_FOUND
> [*] Testing share print$
> [+] Mapping: DENIED, Listing: N/A
> [*] Testing share sambashare
> [+] Mapping: OK, Listing: OK
> 
>  =========================================
> |    Policies via RPC for 10.129.202.5    |
>  =========================================
> [*] Trying port 445/tcp
> [+] Found policy:
> Domain password information:
>   Password history length: None
>   Minimum password length: 5
>   Maximum password age: 49710 days 6 hours 21 minutes
>   Password properties:
>   - DOMAIN_PASSWORD_COMPLEX: false
>   - DOMAIN_PASSWORD_NO_ANON_CHANGE: false
>   - DOMAIN_PASSWORD_NO_CLEAR_CHANGE: false
>   - DOMAIN_PASSWORD_LOCKOUT_ADMINS: false
>   - DOMAIN_PASSWORD_PASSWORD_STORE_CLEARTEXT: false
>   - DOMAIN_PASSWORD_REFUSE_PASSWORD_CHANGE: false
> Domain lockout information:
>   Lockout observation window: 30 minutes
>   Lockout duration: 30 minutes
>   Lockout threshold: None
> Domain logoff information:
>   Force logoff time: 49710 days 6 hours 21 minutes
> 
>  =========================================
> |    Printers via RPC for 10.129.202.5    |
>  =========================================
> [+] No printers returned (this is not an error)
> 
> Completed after 43.65 seconds
> ```

- Do all simple short enumeration without NetBIOS names lookup (`-U -G -S -P -O -I -L`)L

```bash
enum4linux-ng -As <target>
```

- Retrieve information via RPC:

```bash
enum4linux-ng -U <target>  # users
enum4linux-ng -G <target>  # groups
enum4linux-ng -Gm <target> # groups + members
enum4linux-ng -S <target>  # shares
enum4linux-ng -C <target>  # services
enum4linux-ng -P <target>  # password policy information
enum4linux-ng -O <target>  # OS information
enum4linux-ng -L <target>  # additional domain info via LDAP(S)
                           # for DCs only
enum4linux-ng -I <target>  # printer information
```

- Enumerate users via RID cycling:

```bash
enum4linux-ng -R  <target>
```

- NetBIOS name lookup (like `nbstat`):

```bash
enum4linux-ng -N <target>
```

> [!note]+ `enum4linux-ng`
> `enum4linux-ng` is the modern rewrite of `enum4linux` with better output formatting (JSON/YAML support) and improved reliability. Use it if the original hangs or fails. 
> - Syntax is similar:
> ```
> enum4linux-ng -A <target>
> ```

### Imoacket
### CrackMapExec

> [CrackMapExec (CME)](https://github.com/byt3bl33d3r/CrackMapExec) — a post-exploitation/network assessment tool; can be used for SMB enumeration.

>[!note] See [[SMB tools_#CrackMapExec]].

- Enumerate shares (null session):

```bash
crackmapexec smb <target> -u '' -p '' --shares
```

- Enumerate shares (authenticated):

```bash
crackmapexec smb <target> -u username -p password --shares
```

>[!example]+ Example: Obtaining information about SMB shares
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

>[!note]+ Null sessions were effectively standard in Windows 2000 environments. Microsoft significantly tightened restrictions starting with Windows XP SP2 and Server 2003. 
> - That said, Samba servers and legacy systems remain misconfigured regularly enough that checking for null sessions is always worth the two seconds it takes.


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

>[!tip]+
>Before brute-force, _always_ pull the password policy. If there's an account lockout threshold, adjust your rate accordingly.

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

>[!tip]
>By default, CME exits as soon as it finds a successful login. To continue brute-force even after that to find additional users and passwords, add the `--continue-on-success` option to the command.

## RPC Over SMB

> **RPC (Remote Procedure Call)** is a communication protocol that enables a process on one host to execute a procedure on a remote host, abstracting the underlying network transport from the calling application.

> **MS-RPCE (Microsoft Remote Procedure Call Protocol Extensions)** is Microsoft's extension of the DCE/RPC standard that supports RPC transport over SMB named pipes and provides remote access to Windows management interfaces via standard SMB sessions.

- RPC over SMB works by encapsulating **Remote Procedure Call (RPC)** data directly within SMB transactions, specifically using **named pipes** over the hidden **`IPC`$ share**:
	- The client connects to the `IPC$` share on the target server (TCP port `445`) and authenticates (NTLM/Kerberos/null session), then opens a **named pipe** (e.g, `\pipe\samr`, `\lsarpc`, `\srcsvc`, `\winreg`, etc.). 
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

- Some pipes allow **anonymous/null session access** (depending on configuration), others require authentication/administrative privileges.

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
- [`A little guide to SMB enumeration — Hacking Articles`](https://www.hackingarticles.in/a-little-guide-to-smb-enumeration/)

To be done:
- Add SMB-relevant Impacket scripts
- SMB attack surface overview section +
- Vulnerability scanning and decision tree section
- What to look for section in enumeration
- RCE section

