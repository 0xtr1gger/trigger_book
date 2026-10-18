---
created: 2026-09-22
updated: 2026-10-01
tags:
  - services_n_protocols
---
## NFS

> **[NFS (Network File System)](https://en.wikipedia.org/wiki/Network_File_System)** is a distributed file system protocol that allows clients to access files over a network as if they were stored locally, using a client-server architecture built on top of ONC RPC.

>[!note] NFS was designed for Unix and Linux environments; the equivalent protocol on Windows is [[SMB]].

- NFS is built on the [Open Network Computing Remote Procedure Call](https://en.wikipedia.org/wiki/Sun_RPC) (`ONC-RPC` / `SUN-RPC`) protocol, which uses [External Data Representation](https://en.wikipedia.org/wiki/External_Data_Representation) (`XDR`) for the system-independent exchange of data.
- The NFS protocol itself has **no mechanism for authentication or authorization**:
	- Authentication is delegated entirely to the RPC layer's options.
	- Authorization is derived from the underlying file system permissions.
	- The server translates the client's user information into the file system's format and maps the corresponding authorization details into the required UNIX syntax as accurately as possible.
- NFS is **not encrypted by default** in NFSv2 and NFSv3: file contents, credentials embedded in metadata, and directory listings are all sent in cleartext.
- NFSv4 supports Kerberos authentication and encryption (`krb5p`).

| Version | Description |
| :--- | :--- |
| `NFSv2` | Older but supported by many systems; initially operated entirely over UDP. |
| `NFSv3` | Adds features including variable file size and better error reporting; not fully compatible with NFSv2 clients. |
| `NFSv4` | Includes Kerberos, works through firewalls and over the Internet, no longer requires portmappers, supports ACLs, applies state-based operations, and provides performance and security improvements. First version to implement a stateful protocol. |

### Exports

> **Exporting** is the act of making a server-side filesystem or directory available to network clients via NFS, governed by entries in the NFS server export table.

- NFS operates on a classic client-server model: the server *exports* directories, and clients *mount* those exports.
- From the client's perspective, once an export is mounted it is indistinguishable from a local disk — its contents become part of the local filesystem through the VFS (Virtual File System) layer.
- **NFS server**:
	- Exports are configured in the **`/etc/exports` file** or in files within the **`/etc/exports.d` directory**, forming the **[NFS server export table](https://man.archlinux.org/man/exports.5)**. The table defines which paths are shared, which clients may access them, and under what conditions.
	- NFS runs over RPC; the RPC services an NFS server exposes include `rpcbind` (portmapper), `nfsd` (NFS service), `mountd` (mount daemon), and `lockd` (file locking).
- **NFS client**:
	- Uses `mount.nfs` or `automount` to mount and access shares exported by the server.
	- Integrates exported shares into the [VFS](https://en.wikipedia.org/wiki/Virtual_file_system) (Virtual File System) layer.

>[!example]- Example: `/etc/exports`
>```bash
>cat /etc/exports
>```
> 
> ```bash
> /srv/nfs        192.168.1.0/24(rw,fsid=root)
> /srv/nfs/music  192.168.1.0/24(rw,sync)
> /srv/nfs/home   192.168.1.0/24(rw,sync)
> /srv/nfs/public 192.168.1.0/24(ro,all_squash,insecure) desktop(rw,sync,all_squash,anonuid=99,anongid=99)
> ```
> Source: [`NFS — Arch Wiki`](https://wiki.archlinux.org/title/NFS)
>- To apply changes to `/etc/exports`:
> ```bash
> sudo exportfs -ra # re-export all
> ```
>- To list active exports:
>```bash
>sudo exportfs -v
>```

>[!important] NFS uses several ports, depending on its version and configuration:
> - **NFS** primarily operates on **TCP and UDP port `2049`**, used by all NFS versions (NFSv2, NFSv3, NFSv4).
> - NFSv2 and NFSv3 also use **TCP or UDP port `111`**.

### NFS and RPC

- NFS is built on top of **[ONC RPC (Open Network Computing Remote Procedure Call)](https://en.wikipedia.org/wiki/Sun_RPC)**, Sun's implementation of **[RPC (Remote Procedure Call)](https://en.wikipedia.org/wiki/Remote_procedure_call)**.
- Every NFS operation — `READ`, `WRITE`, `LOOKUP`, `GETATTR`, `SETATTR` — is an RPC call.

>[!note]- RPC: "call a function that runs on another computer as if it were local"
>- **[RPC (Remote Procedure Call)](https://en.wikipedia.org/wiki/Remote_procedure_call)** is a stateless, connectionless communication protocol that allows one process (the **client**) to direct another process (the **server**) to execute procedure calls (subroutines) as if the client process had run the calls in its own address space, despite being on a separate physical system.

- Each RPC call specifies three identifiers:
	- **Program number** (service identifier) — a 32-bit integer that identifies the RPC service (e.g., `100003` = NFS); unique for each service on the server.
	- **Version number** (protocol version) — identifies the interface version; a single service can expose multiple versions simultaneously.
	- **Protocol number** — identifies the specific function within the service (e.g., `READ`, `WRITE`).

>[!note] An *RPC service* is an RPC program that exports a set of remote procedures (calls) on an RPC server.

- Because RPC services bind to dynamic ports, a helper daemon called **`rpcbind`** (formerly `portmapper`) maintains a registry — the *portmap* — that maps `(program, version, protocol)` tuples to actual network ports.
- `rpcbind` itself listens on a **well-known port `111` (TCP/UDP)**.
- Before making an RPC call, a client connects to `rpcbind` at `<target>:111` and asks where the program it needs is listening; `rpcbind` replies with the port number, and the client connects directly to that port.

>[!note] The `rpcbind` (`111`) and `nfs` (`2049`) services run on fixed ports and usually do not require a `rpcbind` lookup.

>[!note] NFSv4 eliminates this dance entirely: it runs exclusively on port `2049` with no `rpcbind` dependency.

>[!note]+ Mount process flow
>1. The client contacts `rpcbind` to find the port `mountd` is listening on.
>2. The client sends a mount request to `mountd`.
>3. `mountd` verifies that the requested export exists and that the client has the necessary permissions to mount it.
>4. `mountd` returns a success status and the root file handle.
>5. The client uses the file handle for subsequent NFS operations.

- Well-known RPC program numbers:

| Program  | Name       | Description                         |
| :------- | :--------- | :---------------------------------- |
| `100000` | `rpcbind`  | Portmapper itself.                  |
| `100003` | `nfs`      | NFS service.                        |
| `100005` | `mountd`   | Handle mount and unmount requests.  |
| `100021` | `nlockmgr` | Network Lock Manager (NLM).         |
| `100024` | `status`   | Status monitoring daemon (`statd`). |
| `100227` | `nfs_acl`  | NFS ACL protocol extension.         |

>[!note] For the full list, see [`Remote Procedure Call (RPC) Program Numbers`](https://www.iana.org/assignments/rpc-program-numbers/rpc-program-numbers.xhtml).

>[!note]- On Linux, RPC port mappings come from `/etc/rpc`.
> ```bash
> cat /etc/rpc
> ```
> 
> ```bash
> #ident	"@(#)rpc	1.11	95/07/14 SMI"	/* SVr4.0 1.2	*/
> #
> #	rpc
> #
> portmapper	100000	portmap sunrpc rpcbind
> rstatd		100001	rstat rup perfmeter rstat_svc
> rusersd		100002	rusers
> nfs		    100003	nfsprog
> ypserv		100004	ypprog
> mountd		100005	mount showmount
> ypbind		100007
> walld		100008	rwall shutdown
> yppasswdd	100009	yppasswd
> etherstatd	100010	etherstat
> rquotad		100011	rquotaprog quota rquota
> sprayd		100012	spray
> 3270_mapper	100013
> rje_mapper	100014
> selection_svc	100015	selnsvc
> database_svc	100016
> rexd		100017	rex
> alis		100018
> sched		100019
> llockmgr	100020
> nlockmgr	100021
> x25.inr		100022
> statmon		100023
> status		100024
> bootparam	100026
> ypupdated	100028	ypupdate
> keyserv		100029	keyserver
> sunlink_mapper	100033
> tfsd		100037
> nsed		100038
> nsemntd		100039
> showfhd		100043	showfh
> ioadmd		100055	rpc.ioadmd
> NETlicense	100062
> sunisamd	100065
> debug_svc 	100066  dbsrv
> ypxfrd		100069  rpc.ypxfrd
> bugtraqd	100071
> kerbd		100078
> event		100101	na.event	# SunNet Manager
> logger		100102	na.logger	# SunNet Manager
> sync		100104	na.sync
> hostperf	100107	na.hostperf
> activity	100109	na.activity	# SunNet Manager
> hostmem		100112	na.hostmem
> sample		100113	na.sample
> x25		    100114	na.x25
> ping		100115	na.ping
> rpcnfs		100116	na.rpcnfs
> hostif		100117	na.hostif
> etherif		100118	na.etherif
> iproutes	100120	na.iproutes
> layers		100121	na.layers
> snmp		100122	na.snmp snmp-cmc snmp-synoptics snmp-unisys snmp-utk
> traffic		100123	na.traffic
> nfs_acl		100227
> sadmind		100232
> nisd		100300	rpc.nisd
> nispasswd	100303	rpc.nispasswdd
> ufsd		100233	ufsd
> fedfs_admin	100418
> pcnfsd		150001	pcnfs
> amd		    300019  amq
> sgi_fam		391002	fam
> bwnfsd		545580417
> fypxfrd		600100069 freebsd-ypxfrd
> ```

### NFS daemons

- A typical NFSv3 server runs several daemons simultaneously:
	- **`rpcbind` (`portmapper`)**:
		- Listens on `111/tcp` and `111/udp`.
		- Acts as the service registry for all RPC programs; maps **RPC program numbers** to network ports.
		- Allows clients to discover which ports NFS services are running on.
		- Represents **a central point of failure for RPC-based services**.
		- Binary: `/sbin/rpcbind`.
	- **`nfsd` (NFS daemon)**:
		- Primary NFS service.
		- Listens on `2049/tcp` and `2049/udp`.
		- Handles all filesystem operations: reads, writes, attribute queries, and directory lookups. Runs as a kernel thread (not userspace) for performance.
		- Binary: `/usr/sbin/rpc.nfsd`.
	- **`rpc.mountd` (mount daemon)**:
		- Handles initial mount and unmount requests.
		- Verifies that the client is authorized to mount the requested export, then returns a root file handle.
		- Binds to a dynamic port registered with `rpcbind`.
		- Binary: `/usr/sbin/rpc.mountd`.
	- **`rpc.lockd` (NLM, Network Lock Manager)**:
		- Manages advisory file locks across the network.
		- Runs on both clients and servers; prevents data corruption from concurrent access.
		- Also binds to a dynamic port.
		- Binary: `/usr/sbin/rpc.lockd`.

>[!info]- File handles 
>- A **file handle** is a fixed-length, opaque binary token generated by the NFS server. It uniquely identifies a file or directory within an exported filesystem. 
>- Clients receive file handles during operations such as `LOOKUP` or `MOUNT` and then use them in subsequent RPC calls to reference that filesystem object (e.g., `READ`, `WRITE`, `GETATTR`, `SETATTR`).

- Servers **reject** invalid or tampered handles; because they are opaque, clients cannot forge them.

### NFS versions

- **NFSv2** (1984):
	- The original. Stateless protocol, uses UDP only.
	- Supports files up to 2 GB in size (32-bit offsets).
	- Each request is independent; the server keeps no client state.
	- No encryption; relies on host-based access control and client-supplied UID/GID.
	- Effectively obsolete, but still encountered on embedded systems, old appliances, and legacy infrastructure.
- **NFSv3** (1995):
	- Stateless, uses UDP or TCP.
	- Supports files larger than 2 GB in size (64-bit offsets).
	- Supports Secure RPC in theory, but in practice almost always runs with `AUTH_SYS` (meaning UID/GID spoofing is still possible).
	- No built-in encryption.
- **NFSv4** (2000):
	- Stateful, uses TCP only.
	- Operates only over TCP port `2049` (no `rpcbind`).
	- The server tracks client state (e.g., open files, locks).
	- Built-in support for strong authentication (Kerberos, LIPKEY), integrity, and encryption.

>[!note]- What NFSv4 brings
> - **Single-port design**: NFSv4 runs exclusively on TCP port `2049` (no `rpcbind`, `mountd`, or `lockd`).
> - **Integrated protocols**: The mount protocol and file locking are built directly into NFSv4, which is why no separate `mountd` or `lockd` is needed.
> - **Stateful protocol**: NFSv4 tracks client state on the server: which files are open, which clients hold locks, and what delegations have been granted.
> 	- **Open/close semantics** — the server is explicitly notified when a client opens or closes a file.
> 	- **Delegations** — the server can *delegate* responsibility for a file to a client, so the client can cache the file locally and serve requests without contacting the server until another client needs access.
> 	- **Sessions** (NFSv4.1) — **exactly-once semantics**; the protocol maintains a **session ID** tied to a **client ID**, so the server can track state relative to specific connections and recover from network interrupts.
> - **Pseudo-filesystem namespace**: NFSv4 servers present a unified namespace rooted at `/`. Clients navigate a virtual filesystem tree rather than mounting individual exports by path. Individual exports are presented as sub-trees of this pseudo-root.
> - **Stronger security**:
> 	- Full **Kerberos support via GSS-API** (`krb5`, `krb5i`, `krb5p`).
> 	- With Kerberos, UID spoofing is impossible — users are authenticated cryptographically.
> 	- `krb5i` adds per-operation integrity checking (data cannot be tampered with in transit).
> 	- `krb5p` adds full encryption — safe to use over untrusted networks, WAN links, and cloud environments.
> 	- `AUTH_SYS` (the old UID/GID model) is still supported for backwards compatibility, but it is explicitly a downgrade.
> - **Rich ACLs**: NFSv4 ACLs are modeled on Windows NTFS ACLs rather than POSIX ACLs. They support fine-grained per-user, per-group permissions with explicit allow/deny entries, inheritance, and auditing flags.
> - **Compound operations**: NFSv4 allows multiple operations to be bundled into a single RPC call. What NFSv3 did in three round trips, NFSv4 can do in one. This matters for performance over high-latency links.
> - **UTF-8 filenames**: internationalization is built into the protocol spec; filename encoding is no longer implementation-defined.
> - **Migration and replication**: NFSv4 includes native support for transparent server migration and replica selection (useful in highly-available environments).

>[!note] NFSv1 was never publicly released; NFSv2 was the first public version of the protocol.

| Feature | NFSv2 | NFSv3 | NFSv4 |
| :--- | :--- | :--- | :--- |
| Year | 1984 | 1995 | 2000 |
| Transport | UDP only | UDP or TCP | TCP only |
| Stateful | No | No | Yes |
| Ports used | `2049` + `111` | `2049` + `111` + dynamic | `2049` only |
| Authentication | `AUTH_SYS` only | `AUTH_SYS` only | `AUTH_SYS`, Kerberos (GSS-API) |
| Encryption | None | None | `krb5p` (optional) |
| File locking | External (`lockd`) | External (`lockd`) | Built-in |
| Mount protocol | External (`mountd`) | External (`mountd`) | Built-in |
| ACLs | No | Via NFSACL extension | Rich NFSv4 ACLs |
| Firewall-friendly | No | No | Yes (single port) |
| Max file size | 2 GB | Unlimited | Unlimited |

### Identity and trust model

#### `AUTH_SYS`

>**`AUTH_SYS`** (or `AUTH_UNIX`, set with `sec=sys`) is the default and oldest authentication mechanism for NFS. The client provides its local UID and GID with each RPC call, and the server grants or denies access based solely on these values, without any cryptographic verification.

- In NFSv2 and NFSv3, the default (and usually only) authentication mechanism is **`AUTH_SYS`** (also called `AUTH_UNIX`).
- Under `AUTH_SYS`:
	- The client includes its local UID, GID, and supplementary groups in every RPC call.
	- The server accepts these values **at face value**.
	- There is no cryptographic verification; the server **trusts** that the client is who it claims to be.

>[!warning] **Anyone who can connect to the NFS server can claim to be any UID.**

>[!example]-
>- Say you have UID `1001` on your local system:
>```bash
>id
># uid=1001(alice) gid=1001(alice)
>```
>- You mount a share:
>```bash
>sudo mount -t nfs 192.168.1.11:/export /mnt/nfs
>```
>- Inside that share you appear as **UID `1001` as well**. Files owned by UID `1001` *inside the share* appear as owned by you.
>```bash
>ls -la /mnt/nfs/
>```

>[!note] NFSv4 supports Kerberos authentication, which removes this trust assumption.

#### Root squashing

> **Root squashing** is an NFS export option (`root_squash`) that maps incoming requests from UID `0` (root) on the client to the anonymous user (`nobody`, typically UID/GID `65534`).

- Root squashing is the one protection NFS applies by default.
- It prevents remote root from gaining privileged access to the exported filesystem.
- **`root_squash` is enabled by default unless `no_root_squash` is configured explicitly.**
- All other UIDs are passed through without modification.

>[!note] `all_squash` goes further: it maps *every* client UID/GID to the anonymous user, regardless of who they claim to be. Useful for public exports; not enabled by default.

>[!warning] When `no_root_squash` is configured, UID `0` from the client is honored as UID `0` on the server's export. A root user on the attacker's machine has full root access to everything in the export, and direct privilege escalation is possible (e.g., creating SUID binaries, modifying config files, or writing SSH keys).

>[!warning] `no_root_squash` + writable share = privilege escalation.

### Export configuration

- Exports are defined in `/etc/exports` on the server. Each line follows this format:

```
/export/path  client_spec(option1,option2,...)  another_client(options,...)
```

- Client specs can be:
	- A single IP address (`192.168.1.11`).
	- A subnet (`192.168.1.0/24`).
	- A hostname (`trustedhost.example.com`).
	- A wildcard (`*.example.com`).
- Common export options:

| Option | Description |
| :--- | :--- |
| `rw` | **Read-write**. Clients can create, modify, and delete files. |
| `ro` | **Read-only**. Client writes are rejected. |
| `sync` | **Synchronous writes** — data is committed to stable storage before the server acknowledges the write. Slower, but safer. |
| `async` | **Asynchronous writes** — server acknowledges before data is committed. Faster, but risks data loss on crash. |
| `root_squash` (default) | Map client UID `0` to `nobody` (the anonymous user; usually UID/GID `65534`). |
| `no_root_squash` | **Dangerous.** Remote root is honored as root on the export. Direct privilege escalation path. |
| `all_squash` | Map all client UIDs/GIDs to the anonymous user. |
| `anonuid=<n>` | Set the UID of the anonymous user for squashed requests (default: `65534`). Used with `all_squash` or `root_squash`. |
| `anongid=<n>` | Set the GID of the anonymous user for squashed requests. |
| `secure` (default) | Reject requests from client ports above `1024` (intended to ensure only root processes can mount, since binding to ports below `1024` requires root). |
| `insecure` | Accept requests from any client port (required by many NFS clients on macOS and some other systems). |
| `no_subtree_check` (default) | Disable per-request subtree verification (the server verifying that a file resides within the exported subtree on every request); improves performance. |
| `subtree_check` | Verify each request falls within the exported subtree; slightly safer and slower, but can cause issues with renamed files. |
| `nohide` | Make nested mounts visible through the export. Can unintentionally expose filesystems that were supposed to be separate. |
| `noexec` | Prevent binary execution on the mounted filesystem. Should be standard on data-only exports. |
| `nosuid` | Ignore SUID/SGID bits on the exported filesystem (e.g., prevents creating SUID/SGID binaries). |
| `nodev` | Disallow creation or use of special device files; prevents device file-based privilege escalation. |

>[!note] See [`exports — man pages`](https://man.archlinux.org/man/exports.5) for the complete list.

>[!example]+
> - Restricted home directories (good):
> 
> ```bash
> /home        192.168.1.0/24(rw,sync,root_squash,no_subtree_check)
> ```
> 
> - Public read-only share:
> 
> ```bash 
> /srv/public  *(ro,all_squash,no_subtree_check)
> ```
> 
> - World-writable with `no_root_squash` (vulnerable):
> 
> ```bash
> /srv/data    *(rw,no_root_squash,sync)
> ```
> 
> - Wildcard `rw` with insecure squash config (vulnerable):
> 
> ```bash
> /backups     *.corp.local(rw,all_squash,anonuid=1000,anongid=1000)
> ```

>[!tip]+
> - To apply changes after editing `/etc/exports`, re-export all shares:
> 
> ```bash
> sudo exportfs -ra
> ```
> 
> - List currently active exports with their options:
> 
> ```bash
> sudo exportfs -v
> ```

## Enumerating NFS

### Port scanning and version detection

- Perform service version detection on the default NFS ports:

```bash
sudo nmap -sV -p 111,2049 10.10.11.5
```

>[!tip]+
> - Scan the full port range with version detection and default scripts to locate NFS instances bound to non-standard ports:
> 
> ```bash
> sudo nmap -sV -sC -p- 10.10.11.5
> ```

- Run all available NFS NSE scripts:

```bash
sudo nmap -sV --script "nfs-*" 10.10.11.5
```

- Query the portmapper for all registered RPC programs:

```bash
sudo nmap -sV -p 111,2049 --script rpcinfo 10.10.11.5
```

| Option | Description |
| :--- | :--- |
| `-sV` | Enable service version detection. |
| `-p` | Specify destination port(s) to scan (`111,2049` or `-p-` for all ports). |
| `-sC` | Execute default category NSE scripts. |
| `--script` | Execute a specific NSE script or glob expression. |
| `-Pn` | Treat the host as online; skip ICMP ping discovery. |

- Key Nmap NFS scripts:

| Script | Categories | Description |
| :--- | :--- | :--- |
| [`rpcinfo`](https://nmap.org/nsedoc/scripts/rpcinfo.html) | `default`, `discovery`, `safe`, `version` | Connect to the portmapper and fetch a list of all registered programs, versions, ports, and protocols. |
| [`nfs-showmount`](https://nmap.org/nsedoc/scripts/nfs-showmount.html) | `discovery`, `safe` | Show NFS exports, like `showmount -e`. |
| [`nfs-ls`](https://nmap.org/nsedoc/scripts/nfs-ls.html) | `discovery`, `safe` | List files and retrieve useful attributes from accessible NFS exports. |
| [`nfs-statfs`](https://nmap.org/nsedoc/scripts/nfs-statfs.html) | `discovery`, `safe` | Retrieve disk space statistics and information from a remote NFS share. |

>[!note] The [`rpcinfo`](https://nmap.org/nsedoc/scripts/rpcinfo.html) NSE script connects to the portmapper and retrieves a list of all registered programs, including the RPC program number, supported versions, port number and protocol, and program name — similar to the [`rpcinfo`](https://man.archlinux.org/man/rpcinfo.8.en) command.

>[!tip]+
> - List local Nmap scripts for NFS:
> 
> ```bash
> ls -l /usr/share/nmap/scripts/*nfs*
> ```

>[!example]- 
> 
> ```bash
> sudo nmap 192.168.1.11 -p111,2049 -sV --script rpcinfo
> ```
> 
> ```bash
> Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-09-20 09:25 CDT
> Nmap scan report for 192.168.1.11
> Host is up (0.083s latency).
> 
> PORT     STATE SERVICE VERSION
> 111/tcp  open  rpcbind 2-4 (RPC #100000)
> | rpcinfo: 
> |   program version    port/proto  service
> |   100003  3           2049/udp   nfs
> |   100003  3           2049/udp6  nfs
> |   100003  3,4         2049/tcp6  nfs
> |   100021  1,3,4      37483/udp6  nlockmgr
> |   100021  1,3,4      37575/tcp   nlockmgr
> |   100021  1,3,4      42955/tcp6  nlockmgr
> |   100021  1,3,4      44033/udp   nlockmgr
> |   100227  3           2049/tcp6  nfs_acl
> |   100227  3           2049/udp   nfs_acl
> |_  100227  3           2049/udp6  nfs_acl
> 2049/tcp open  nfs     3-4 (RPC #100003)
> 
> Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
> Nmap done: 1 IP address (1 host up) scanned in 7.04 seconds
> ```

### Enumerating exports with showmount

- List all exports and their access restrictions:

```bash
showmount -e 10.10.11.5
```

- Force TCP (useful if UDP is blocked):

```bash
showmount -e 10.10.11.5 --no-udp
```

| Option | Description |
| :--- | :--- |
| `-a`, `--all` | List the client hostname or IP address and the mounted directory (`host:dir` format). |
| `-d`, `--directories` | List only directories mounted by some client. |
| `-e`, `--exports` | Show the list of exports on an NFS server. |
| `-v`, `--version` | Display version and exit. |
| `--no-headers` | Suppress descriptive headings from the output. |

>[!example]-
>```bash
>showmount -e 192.168.1.11
> ```
> ```bash
> Export list for 192.168.1.11:
> /var/nfs      192.168.0.0/24
> /mnt/nfsshare 192.168.0.0/24
> /tmp          *
> ```
> The above output means:
> - Only clients in this subnet (`192.168.0.0/24`) can mount shares `/var/nfs` and `/mnt/nfsshare`.
> - Anyone on the network can mount the `/tmp` share.

### Enumerating RPC services with `rpcinfo`

- `rpcinfo` queries `rpcbind` directly and reports which RPC services are running.
- List all registered RPC programs:

```bash
rpcinfo -p 10.10.11.5
```

- Query a specific program by number (`100003` = NFS):

```bash
rpcinfo -T tcp 10.10.11.5 100003
```

- Display a summary of all registered services:

```bash
sudo rpcinfo -s 10.10.11.5
```

| Option | Description |
| :--- | :--- |
| `-p` | Probe the portmapper and list all registered RPC programs. |
| `-T <transport>` | Specify the transport on which to contact the service (`tcp`, `udp`). |
| `-s` | Display a concise summary of all registered RPC services. |

### Enumerating with NetExec

- [NetExec (`nxc`)](https://www.netexec.wiki/) sweeps subnets for NFS services and enumerates shares and their contents.
- Probe for the NFS service and basic information:

```bash
nxc nfs 10.10.11.5
```

- List available shares:

```bash
nxc nfs 10.10.11.5 --shares
```

- List the contents of a specific share:

```bash
nxc nfs 10.10.11.5 --share '/path/to/share' --ls '/'
```

| Option | Description |
| :--- | :--- |
| `nfs` | Select the NFS protocol module. |
| `--shares` | Enumerate exported shares and access permissions. |
| `--share <path>` | Target a specific exported share path. |
| `--ls <path>` | List the contents of a directory within the targeted share. |

>[!tip]+
> - NetExec is best suited to wide subnet sweeps for quickly identifying all hosts running NFS. For deep enumeration of a specific host, use `showmount` and `rpcinfo`.

## Interacting with NFS

> The `mount` command connects to NFS shares and makes remote file systems accessible as if they were local directories.

>[!warning] To work with NFS, ensure the `nfs-common` (Debian/Ubuntu) or `nfs-utils` (RHEL, CentOS, AlmaLinux, Arch Linux) package is installed.
>```bash
>sudo apt install nfs-common # Debian/Ubuntu
>```

- List exported shares:

```bash
showmount -e 10.10.11.5
```

- Create a local mount point before mounting a share:

```bash
sudo mkdir -p /mnt/nfs
```

- Mount a share:

```bash
sudo mount -t nfs 10.10.11.5:/path/from/showmount /mnt/nfs
```

- Force a specific protocol version:

```bash
sudo mount -t nfs -o vers=3 10.10.11.5:/share /mnt/nfs
```

- Read-only mount:

```bash
sudo mount -t nfs -o ro 10.10.11.5:/share /mnt/nfs
```

- Mount without file locking (useful when `lockd` is unreachable, or against `no_root_squash` exports):

```bash
sudo mount -t nfs -o nolock 10.10.11.5:/share /mnt/nfs
```

>[!example]+ Example: mounting NFS shares
> ```bash
> sudo mount -t nfs 192.162.1.11:/ ./nfs -o nolock
> ```
> 
> ```bash
> cd nfs && tree
> ```
> 
> ```bash
> ├── nfs
>     ├── mnt
>     │   └── nfsshare
>     │       └── flag.txt
>     └── var
>         └── nfs
>             └── flag.txt
> ```

| Option | Description |
| :--- | :--- |
| `-t`, `--types` | Indicate the filesystem type to mount, such as `ext4`, `sysfs`, `proc`, `nfs`, `cifs`, etc. Supported types depend on the kernel (see `/proc/filesystems` and `/lib/modules/$(uname -r)/kernel/fs` for a complete list). |
| `-o`, `--options` | Specify mount options as a comma-separated list, such as `noatime`, `nodev`, `nosuid`. Order matters — the last option wins if two conflict. |

- Mount `-o` options:

| Option | Description |
| :--- | :--- |
| `nfsvers`, `vers=<n>` | Specify the NFS protocol version used to contact the server's NFS service. If the server does not support the requested version, the mount request fails. If not specified, the server chooses the highest version both parties support. |
| `lock` / `nolock` | Select whether to use file locking. `lock` (default): applications can lock files, and the locks provide exclusion against other applications. `nolock`: applications can lock files, but locks provide exclusion only against other applications running on the same client. |
| `sec=<mode>` | Set the security mode used to authenticate connections. `sys` (default): use local UNIX UIDs/GIDs. `krb5`: use Kerberos V5 to authenticate users, with no data integrity or encryption. `krb5i`: add integrity checks to prevent data tampering, with no encryption. `krb5p`: the most secure option — authenticate, verify integrity, and encrypt traffic. |
| `ro` | Mount read-only. |
| `rw` | Mount read-write. |
| `ac` / `noac` | Choose whether the client may cache file attributes (default: `ac`, do cache). |
| `mountvers=<n>` | Specify the RPC version used to contact the server's `mountd`. |
| `actimeo=<n>` | Set `acregmin`, `acregmax`, `acdirmin`, and `acdirmax` to the same value. `actimeo=0` disables all caching. |
| `udp` | Same as `proto=udp`; enforce UDP. |
| `tcp` | Same as `proto=tcp`; enforce TCP. |
| `port=<n>` | Specify the NFS server port to connect to. If the server's NFS service is not available on that port, the mount request fails. |

>[!tip]+
> - Unmount the share once triage is complete:
> 
> ```bash
> sudo umount /mnt/nfs
> ```

## References and further reading

- [`Sun RPC — Wikipedia`](https://en.wikipedia.org/wiki/Sun_RPC)
- [`Remote procedure call — Wikipedia`](https://en.wikipedia.org/wiki/Remote_procedure_call)
- [`Network File System — Wikipedia`](https://en.wikipedia.org/wiki/Network_File_System)
- [`External Data Representation — Wikipedia`](https://en.wikipedia.org/wiki/External_Data_Representation)
- [`exports(5) — Arch manual pages`](https://man.archlinux.org/man/exports.5)
- [`Remote Procedure Call (RPC) Program Numbers — IANA`](https://www.iana.org/assignments/rpc-program-numbers/rpc-program-numbers.xhtml)
- [`NFS — Arch Wiki`](https://wiki.archlinux.org/title/NFS)
- [`NetExec (nxc) Official Documentation`](https://www.netexec.wiki/)
- [`NFS (Network File System) — Hackviser`](https://hackviser.com/tactics/pentesting/services/nfs)
- [`Network File System (NFS): Overview & Setup — NinjaOne`](https://www.ninjaone.com/blog/network-file-system-nfs/)
- [`2049 - Pentesting NFS Service — HackTricks`](https://book.hacktricks.wiki/en/network-services-pentesting/nfs-service-pentesting.html)
- [`Linux Hacking Case Studies Part 2: NFS — NetSPI`](https://www.netspi.com/blog/technical-blog/network-pentesting/linux-hacking-case-studies-part-2-nfs/)
- [`NFS Pentesting Best Practices — secybr`](https://secybr.com/posts/nfs-pentesting-best-practicies/)
- [`NFS Share no_root_squash - Linux Privilege Escalation — Juggernaut Pentesting Academy`](https://juggernaut-sec.com/nfs-no_root_squash/)

## Appendix A: Default configuration

- NFS is not difficult to configure, as it has fewer options than FTP or SMB.
- The `/etc/exports` file contains a table of physical filesystems on an NFS server accessible to clients. The [NFS Exports Table](http://manpages.ubuntu.com/manpages/trusty/man5/exports.5.html) shows which options it accepts and, therefore, which options are available.

```bash
cat /etc/exports
```

| Option | Description |
| :--- | :--- |
| `rw` | Read and write permissions. |
| `ro` | Read-only permissions. |
| `sync` | Synchronous data transfer (a bit slower). |
| `async` | Asynchronous data transfer (a bit faster). |
| `secure` | Ports above `1024` will not be used. |
| `insecure` | Ports above `1024` will be used. |
| `no_subtree_check` | Disable the checking of subdirectory trees. |
| `root_squash` | Map files owned by root (UID/GID `0`) to the UID/GID of the anonymous user, which prevents `root` from accessing files on an NFS mount. |

- Dangerous settings:

| Option | Description |
| :--- | :--- |
| `rw` | Read and write permissions. |
| `insecure` | Ports above `1024` will be used. |
| `nohide` | If another filesystem was mounted below an exported directory, this directory is exported by its own exports entry. |
| `no_root_squash` | All files created by root are kept with UID/GID `0`. |
