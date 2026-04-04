---
created: 2026-03-31
tags:
  - network_services
  - net_hack
---
## NFS

>**[NFS](https://en.wikipedia.org/wiki/Network_File_System) (Network File System)** is a distributed file system protocol that allows clients to access files over a network as if they were stored locally, using a client-server architecture built on top of ONC RPC.

>[!note] NFS was designed for Unix/Linux environments; Windows does the same thing differently — that's [[SMB]].

- NFS is **not encrypted by default** in NFSv2/NFSv3. Everything — file contents, credentials embedded in metadata, directory listings — is sent in cleartext.
- NFSv4 supports Kerberos authentication and encryption (`krb5p`).

### Exports

- NFS operates on a classic client-server model: the server *exports* directories, and clients *mount* those exports. 
- From the client perspective, once an export is mounted, it looks no different from a local disk — its content becomes a part of local filesystem through VFS (Virtual File System) layer.

>**Exporting** is the act of making a server-side filesystem or directory available to network clients via NFS, governed by entries in the NFS server export table.

- **NFS server**
	- NFS exports are configured in the **`/etc/exports` file** or files in the **`/etc/exports.d` directory**, in the **[NFS server export table](https://man.archlinux.org/man/exports.5)**. The table defines which paths are shared, which clients may access them, and under what conditions.
	- NFS runs over RPC; RPC services the NFS server exposes include `rpcbind` (portmapper), `nfsd` (NFS service), `mountd` (mount daemon), and `lockd` (file locking).

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

- **NFS client**
	- Uses `mound.nfs` or `automount` to to mount and access shares exported by the server.
	- Integrates into [VFS](https://en.wikipedia.org/wiki/Virtual_file_system) (Virtual File System).

>[!important] NFS uses several ports, depending on its version and configuration:
> - **NFS** primarily operates on **TCP and UDP port `2049`**. It's used by all NFS versions (NFSv2, NFSv3, NFSv4).
> - NFSv2 and NFSv3 also use **TCP or UDP port `111`**. 
### NFS and RPC

- NFS is build on top of **[ONC RPC (Open Network Computing Remote Procedure Call)](https://en.wikipedia.org/wiki/Sun_RPC)** — Sun's implementation of **[RPC (Remote Procedure Call)](https://en.wikipedia.org/wiki/Remote_procedure_call)**.
- **Every NFS operation** — `read`, `write`, `getattr`, `lookup` — is an **RPC call**.

>[!interesting]- RPC: "Call a function that runs on another computer as if it were local"
>**[RPC (Remote Procedure Call)](https://en.wikipedia.org/wiki/Remote_procedure_call)** is a stateless, connectionless communication protocol that allows one process (the **client**) to direct another process (the **server**) to execute procedure calls (subroutines) as if the client process had run the calls in its own address space, despite being on a separate physical system.


- Every NFS operation — `READ`, `WRITE`, `LOOKUP`, `GETATTR`, `SETATTR` — is an RPC call. 
- Each RPC call specifies three identifiers:
	- **Program number** (service identifier) — a 32-bit integer that identifies the RPC service (e.g., `100003` = NFS). It's unique for each service on the server.
	- **Version number** (protocol version) — identifies the interface version; a single service can expose multiple versions simultaneously.
	- **Protocol number** — identifies the specific function within the service (e.g., `READ`, `WRITE`).

>[!note] An *RPC service* is an RPC program that exports a set of remote procedures (calls) on an RPC server.

- Because RPC services bind to dynamic ports, a helper daemon called **`rpcbind`** (formerly `portmapper`) maintains a registry — the _portmap_ — that maps `(program, version, protocol)` tuples to actual network ports.
- `rpcbind` itself listens on a **well-known port `111` (TCP/UDP)**.
- So, before making an RPC call, a client connects to `rpcbind` at `<target>:111` and asks where the program it needs is listening. `rpcbind` replies with the port number, and the client connects directly to that port.

>[!note] `rpcbind` (`111`) and `nfs` (`2049`) usually don't require `rpcbind` as they run on fixed ports.

>[!note] NFSv4 eliminates this dance entirely. It runs exclusively on port `2049` with no `rpcbind` dependency.

>[!interesting]+ Mount process flow
>1. The client contacts `rpcbind` to find the port `mountd` is listening on.
>2. The client sends a mount request to `mountd`.
>3. `mountd` verifies the requested export exists and the client has necessary permissions to mount it.
>4. `mountd` returns success status and root file handle.
>5. The client uses the file handle for subsequent NFS operations.

- Well-known RPC  program numbers:

| Program  | Name       | Description                         |
| -------- | ---------- | ----------------------------------- |
| `100000` | `rpcbind`  | Portmapper itself.                  |
| `100003` | `nfs`      | NFS service.                        |
| `100005` | `mountd`   | Handles mount/unmount requests.     |
| `100021` | `nlockmgr` | Network Lock Manager (NLM).         |
| `100024` | `status`   | Status monitoring daemon (`statd`). |
| `100227` | `nfs_acl`  | NFS ACL protocol extension.         |
>[!note] For the full list, see [`Remote Procedure Call (RPC) Program Numbers`](https://www.iana.org/assignments/rpc-program-numbers/rpc-program-numbers.xhtml).

>[!interesting]- On Linux, RPC port mappings come from `/etc/rpc`.
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

A typical NFSv3 server runs several daemons simultaneously:

- **`rpcbind` (`portmapper`)**
	-  Listens on `111/tcp` and `111/udp`.
	- Acts as the service registry for all RPC programs; maps **RPC program numbers** to network ports.
	- Allows clients to discovery which ports NFS services are running on.
	- **A central point of failure for RPC-based services.**
	- `/sbin/rpcbind`
- **`nfsd` (NFS daemon)**
	- Primary NFS service.
	- Listens on `2049/tcp` and `2049/udp`.
	- Handles all filesystem operations: reads, writes, attribute queries, directory lookups. Runs as a kernel thread (not userspace) for performance.
	- `/usr/sbin/rpc.nfsd`
- **`rpc.mountd` (mound daemon)**
	- Handles initial mount/unmount requests. 
	- Verifies that the client is authorized to mount the requested export, then returns a root file handle. 
	- Binds to a dynamic port registered with `rpcbind`.
	- `/usr/sbin/spc.mountd`
- **`rpc.lockd` (NLM, Network Lock Manager)**
	- Manages advisory file locks across the network. 
	- Runs on both clients and servers. Prevents data corruption from concurrent access. 
	- Also binds to a dynamic port.
	- `/usr/sbin/rpc.lockd`

>**A file handle** is a fixed-length, opaque binary token generated by the NFS server that uniquely identifies a file or directory within an exported filesystem.  Clients receive file handles during operations such as `LOOKUP` or `MOUNT` and then use them in subsequent RPC calls to reference that filesystem object (e.g., `READ`, `WRITE`, `GETATTR`, `SETATTR`).

- Servers **reject** invalid or tampered handles; and since they're opaque, clients can't just forge them.

### NFS versions

- **NFSv2** (1984)
	- The original. Stateless protocol, uses UDP only.
	- Supports files up to 2 GB in size (32-bit offsets).
	- Each request is independent, the server keeps no client state.
	- No encryption, relies on host-based access control and client-supplied UID/GID.
	- Effectively obsolete, but you'll encounter it on embedded systems, old appliances, and ancient infrastructure that nobody has touched in fifteen years.

- **NFSv3** (1995)
	- Stateless, uses UDP or TCP.
	- Supports files more than 2 GB in size (64-offsets).
	- Supports Secure RPC in theory, but in practice almost everyone runs it with `AUTH_SYS` (meaning UID/GID spoofing is still possible).
	- No built-in encryption.

- **NFSv4** (2000)
	- Stateful, uses TCP only.
	- Operates only over TCP port `2049` (no `rpcbind`).
	- The server keeps track of the client state (e.g., open files, locks).
	- Built-in support for strong authentication (Kerberos, LIPKEY), integrity, and encryption.

>[!interesting]+ What NFSv4 brings
> NFSv4 is worth a closer look:
> 
> - **Single-port design**: NFSv4 runs exclusively on TCP port `2049` (no `rpcbin`, `mountd`, or `lockd`).
> - **Integrated protocols:** The mount protocol and file locking are built directly into NFSv4, that why no separate `mountd` or `lockd` is needed.
> - **Stateful protocol**: NFSv4 tracks client state on the server: which files are open, which clients hold locks, and what delegations have been granted.
> 	- **Open/close semantics** — The server is explicitly notified when a client opens or closes a file.
> 	- **Delegations** — The server can *delegate* responsibility for a file to a client, so the the client can cache the file locally and serve requests without contacting the server until another client needs access. 
> 	- **Sessions** (NFSv4.1) —  **exactly-once semantics**; the protocol maintains a **session ID** tied to a **client ID**, so the server can track state relative to specific connections and recovery from network interrupts.
> - **Pseudo-filesystem namespace**: NFSv4 servers present a unified namespace rooted at `/`. Clients navigate a virtual filesystem tree rather than mounting individual exports by path. Individual exports are presented as sub-trees of this pseudo-root.
> - **Stronger security**:
> 	- Full **Kerberos support via GSS-API** (`krb5`, `krb5i`, `krb5p`).
> 	- With Kerberos, UID spoofing is impossible — users are authenticated cryptographically.
> 	- `krb5i` adds per-operation integrity checking (data can't be tampered in transit).
> 	- `krb5p` adds full encryption — safe to use over untrusted networks, WAN links, cloud environments.
> 	- `AUTH_SYS` (the old UID/GID model) is still supported for backwards compatibility, but it's explicitly a downgrade.
> - **Rich ACLs**: NFSv4 ACLs are modeled on Windows NTFS ACLs rather than POSIX ACLs. They support fine-grained per-user, per-group permissions with explicit allow/deny entries, inheritance, and auditing flags.
> - **Compound operations**: NFSv4 allows multiple operations to be bundled into a single RPC call. What NFSv3 did in three round trips, NFSv4 can do in one. This matters for performance over high-latency links.
> - **UTF-8 filenames**: Internationalization is built into the protocol spec; filename encoding is no longer implementation-defined.
> - **Migration and replication**: NFSv4 includes native support for transparent server migration and replica selection (useful in highly-available environments).

>[!interesting] Yes, NFSv1 doesn't exist. 

| Feature           | NFSv2               | NFSv3                    | NFSv4                          |
| ----------------- | ------------------- | ------------------------ | ------------------------------ |
| Year              | 1984                | 1995                     | 2000                           |
| Transport         | UDP only            | UDP or TCP               | TCP only                       |
| Stateful          | No                  | No                       | Yes                            |
| Ports used        | `2049` + `111`      | `2049` + `111` + dynamic | `2049` only                    |
| Authentication    | `AUTH_SYS` only     | `AUTH_SYS` only          | `AUTH_SYS`, Kerberos (GSS-API) |
| Encryption        | None                | None                     | `krb5p` (optional)             |
| File locking      | External (`lockd`)  | External (`lockd`)       | Built-in                       |
| Mount protocol    | External (`mountd`) | External (`mountd`)      | Built-in                       |
| ACLs              | No                  | Via NFSACL extension     | Rich NFSv4 ACLs                |
| Firewall-friendly | No                  | No                       | Yes (single port)              |
| Max file size     | 2 GB                | Unlimited                | Unlimited                      |

### Identity and trust model

#### AUTH_SYS: The Honor System

- In NFSv2 and NFSv3, the default (and usually only) authentication mechanism is **`AUTH_SYS`** (also called `AUTH_UNIX`). 
- Under `AUTH_SYS`:
	- The client includes its local UID, GID, and supplementary groups in every RPC call.
	- The server accepts these values **at face value**.
	- There's no cryptographic verification. The server **trusts** that the client is who it says it is.

>**`AUTH_SYS`** (also known as `AUTH_UNIX`, set with `sec=sys`) is the default and oldest authentication for NFS, where the client supplies its local UID and GID with each PRC call, and the server grants or denies access based solely on these values, without any cryptographic verification.

Therefore,
>[!warning] **Anyone who can connect to the NFS server can claim to be any UID**.

>[!example]-
>Say, you have UID `1001` on your local system:
>```bash
>id
># uid=1001(alice) gid=1001(alice)
>```
>You mount a share:
>```bash
>sudo mount -t nfs 192.168.1.11:/export /mnt/nfs
>```
>Inside that share, you appear as **UID `1001` as well**. Files owned by UID `1001` *inside the share* appear as owned by you.
>```bash
>ls -la /mnt/nfs/
>```

>[!note] NFSv4 supports Kerberos authentication.

But it's not always the same with the root user.
#### Root squashing

The one protection NFS applies by default is **root squashing**.

>**Root squashing** is an NFS export option (`root_squash`) that maps incoming requests from UID `0` (root) on the client to the anonymous user (`nobody`, typically UID/GID `65534`). 

- Root squashing prevents remote root from gaining privileged access to the exported filesystem. 
- **`root_squash` is enabled by default unless `no_root_squash` is configured explicitly.**
- All other UIDs are passed through without modification.

 >[!note] `all_squash` goes further: it maps *every* client UID/GID to the anonymous user, regardless who they claim to be. Useful for public exports; not enabled by default. 

>[!bug] When `no_root_squash` is configured, UID `0` from the client is honored as UID `0` on the server's export. A root user on the attacker's machine has full root access to everything in the export, and direct privilege escalation is possible (e.g., creating SUID binaries, modifying config files, or writing SSH keys).

>[!bug] `no_root_squash` + writable share = privilege escalation.


>[!note] See [[NFS_privilege_escalation]].

### Export configuration

- Exports are defined in `/etc/exports` on the server. Each line follows this format:

```
/export/path  client_spec(option1,option2,...)  another_client(options,...)
```

- Client specs can be:
	- A single IP address (`192.168.1.11`).
	- A subnet (`196.168.1.0/24`).
	- A hostname (`trustedhost.example.com`).
	- A wildcard (`*.example.com`).

- Below are some common export options:

| Option                       | Description                                                                                                                                                 |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `rw`                         | **Read-write**. Clients can create, modify, and delete files.                                                                                               |
| `ro`                         | **Read-only**. Client writes are rejected.                                                                                                                  |
| `sync`                       | **Synchronous writes** — data is committed to stable storage before the server acknowledges the write. Slower, but safer.                                   |
| `async`                      | **Asynchronous writes** — server acknowledges before data is committed. Faster, but risks data loss on crash.                                               |
| `root_squash` (default)      | Map client UID `0` to `nobody` (the anonymous user; usually UID/GID `65534`).                                                                               |
| `no_root_squash`             | **Dangerous.** Remote root is honored as root on the export. Direct privilege escalation path.                                                              |
| `all_squash`                 | Map all client UIDs/GIDs to the anonymous user.                                                                                                             |
| `anonuid=<n>`                | Set the UID of the anonymous user for squashed requests (default: `65534`). Used with `all_squash` or `root_squash`.                                        |
| `anongid=<n>`                | Set the GID of the anonymous user for squashed requests.                                                                                                    |
| `secure` (default)           | Reject requests from client ports above `1024` (Intended to ensure only root processes can mount, since binding to ports below `1024` requires root).       |
| `insecure`                   | Accept requests from any client port (Required by many NFS clients on macOS and some other systems).                                                        |
| `no_subtree_check` (default) | Disable per-request subtree verification (when the server verifies that a file resides within the exported subtree on every request); improves performance. |
| `subtree_check`              | Verify each request falls within the exported subtree; Slightly safer, slower, but can cause issues with renamed files.                                     |
| `nohide`                     | Makes nested mounts visible through the export. Can unintentionally expose filesystems that were supposed to be separate.                                   |
| `noexec`                     | Prevents binary execution on the mounted filesystem. Should be standard on data-only exports.                                                               |
| `nosuid`                     | Ignores SUID/SGID bits on the exported filesystem (e.g., prevents creating SUID/SGID binaries).                                                             |
| `nodev`                      | Disallow creation or use of special device files; prevents device file-based privilege escalation.                                                          |
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
> 

- To apply changes after editing `/etc/exports`, re-export all shares:

```bash
sudo exportfs -ra
```

- List currently active exports with options:

```bash
sudo exportfs -v
```

## Connecting to NFS

>You can use the `mount` command to connect to NFS shares and access remote file systems as if they were local directories.

- List exported shares:

```bash
showmount -e <target>
```

>[!warning] To work with NFS, ensure you have `nfs-common` (Debian/Ubuntu) or `nfs-utlis` (RHEL, CentOS, AlmaLinux, ArchLinux) packages installed.
>```bash
>sudo apt install nfs-common # Debian/Ubuntu
>```

- Before mounting a share, create a mount point:

```bash
sudo mkdir -p /mnt/nfs
```

- Mount a share:

```bash
mount -t nfs <target>:/path/from/showmount /mnt/nfs
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
>     ├── mnt
>     │   └── nfsshare
>     │       └── flag.txt
>     └── var
>         └── nfs
>             └── flag.txt
> ```

>[!note]+ Option breakdown
> 
> | Option            | Description                                                                                                                                                                                                                   |
> | ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
> | `-t`, `--types`   | Indicates the filesystem type to mount, such as `ext4`, `sysfs`, `proc`, `nfs`, `cifs`, etc. The supported types depend on the kernel (see `/proc/filesystems` and `/lib/modules/$(uname -r)/kernel/fs` for a complete list). |
> | `-o`, `--options` | Specify mount options to use (comma-separated list), such as `noatime`, `nodev`, `nosuid`.<br>The order matters, the last option wins if there are conflicting ones.                                                          |

- Force a specific version:

```bash
mount -t nfs -o vers=3 <target>:/share /mnt/nfs
```

- Read-only mount:

```bash
mount -t nfs -o ro target.com:/share /mnt/nfs
```

- Mount without root squashing (if `no_root_squash` is enabled on the server):

```bash
mount -t nfs -o nolock target.com:/share /mnt/nfs
```

- Unmount:

```bash
umount /mnt/nfs
```

- `-o` options:

| Option                | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `nfsvers`, `vers=<n>` | The NFS protocol version number used to contact the server's NFS service. <br>If the server does not support the requested version, the mount request fails.<br>If not specified, the server chooses the highest version both parties support.                                                                                                                                                                                                                                                       |
| `lock`/`nolock`       | Select whether to use file locking.<br>`●` `lock` (default): Applications can lock files, and the locks provide exclusion to other applications.<br>`●` `nolock`: Applications can lock files, but locks provide exclusion only against other applications running on the same server.                                                                                                                                                                                                               |
| `sec=<mode>`          | The security mode used to authenticate connections.<br>`●` `sys` (default): Use local UNIX UIDs/GIDs for authentication.<br>`●` `krb5`: Use Kerberos V5 to authenticate users; no data integrity or encryption.<br>`●` `krb5i`: Use Kerberos V5 to authenticate users and perform integrity checks to prevent data tampering; no encryption.<br>`●` `krb5p`: The most secure option; use Kerberos V5 to authenticate users, perform integrity checks to prevent data tampering, and encrypt traffic. |
| `ro`                  | Read-only.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| `rw`                  | Read-write.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `ac`/`noac`           | Choose whether the client may cache file attributes (default: `ac`, do cache).                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `mountvers=<n>`       | The RPC version number used to contact the server's `mountd`.                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `actimeo=<n>`         | Sets `acregmin`, `acregmax`, `acdirmin`, and `acdirmax` to the same value. If not specified, the client uses the default value for each option.<br>`actimeo=0` disables all caching.                                                                                                                                                                                                                                                                                                                 |
| `udp`                 | Same as `proto=udp`; enforces UDP.                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `tcp`                 | Same as `proto=tcp`; enforces TCP.                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `port=<n>`            | The NFS server port to connect to.<br>If the server's NFS service is not available on the specified port, the mount request fails.                                                                                                                                                                                                                                                                                                                                                                   |

## NFS attack surface

- **UID/GID impersonation (`AUTH_SYS`)**
	- The most straightforward NFS attack. 
	- NFSv2/NFSv3 use `AUTH_SYS` authentication method by default (`sec=sys`), i.e., map client's UID/GID to the same UID/GID on the export. This means you can impersonate any user whose UID you know — unless it's root (`no_root_squash` is the default).

- **`no_root_squah` privilege escalation**
	- If `no_root_squash` is set on a writable share, you have a direct path to privilege escalation — your client's UID/GID `0` is mapped to UID/GID `0` on the share, which gives you full control over any exposed files.

>[!note]+ Export misconfiguration patterns
> - **`* (rw,...)`** — Any host can mount and write to the share.
> - **`no_root_squash`** — Remote root is real root. Instant escalation.
> - **`no_subtree_check` + `nohide`** — May expose nested filesystems.
> - **`all_squash,anonuid=1000`** — All users map to UID `1000`. If that UID owns sensitive files, you have access without authentication.
> - **Sensitive paths exported** — `/home`, `/etc`, `/root`, `/var/www`, `/backup`, `/opt/app`.
> - **`insecure`** — Required by some clients but widens the attack surface.

- **Data exposure**
	- NFS shares may expose sensitive data, such as:
		- **SSH private keys** (`~/.ssh/id_rsa`, `~/.ssh/id_ed25519`).
		- **Shell history** (`.bash_history`, `.zsh_history`) — may expose credentials typed on the command line.
		- **Application configs** — database connection strings, API keys, secrets.
		- **`.env` files** — environment variables; often contain access tokens, API keys, passwords, etc.
		- **Kerberos keytabs** (`/etc/krb5.keytab`, `~/user.keytab`).
		- **Web server directories** — if the share is writable and served by a web server, you can plant webshells.
		- **Cron jobs** — modify scripts run by root if they're writable.
		- **Backup archives** — often contain copies of everything listed above.
		- **CI/CD artifacts** — deployment keys, access tokens.

- **No encryption/no integrity (NFSv2/NFSv3)**
	- Without `krb5i` or `krb5p`, NFSv2/NFSv3 traffic is unprotected on the wire:
		- **MitM/passive sniffing** — file contents, metadata, and UID/GID claims are all visible in cleartext.
		- **RPC injection** — an attacker with network access can forge or replay RPC calls.
		- **Replay attacks** — captured NFS operations can be replayed against the server.

- **Export misconfigurations**
	- NFS exports are defined in `/etc/exports`, and misonfigurations are common.
	- `/share *(rw,sync)` — any host can mount the share.
	- `no_root_squash` — root user spoofing; remote root (claimed UID `0`) is treated as real root.
	- Writable sensitive exports: webshells, cron/script poisoning, tampering with the data, malware, etc.
	- `all_squash,anonuid=1000,anongid=1000`, though map all users to `1000`, may unintentionally give attacker the permissions of a real user.
## Enumeration

### Nmap port scanning and version detection

- Nmap NFS port scanning and version detection:

```bash
sudo nmap -sV -p 111,2049 <target>
```

> [!tip]+
> - Basic port scanning + version detection + default scripts — in case you suspect non-standard ports:
> 
> ```bash
> sudo nmap -sV -sC -p- <target>
> ```

- Run all scripts relevant to NFS:

```bash
sudo nmap -sV --script nfs* <target>
```

- RPC enumeration via `rcpbind`:

```bash
sudo nmap -p111,2049 -sV --script rpcinfo 192.168.1.11
```

>[!interesting]+ `rpcinfo` 
>The [`rcpinfo`](https://nmap.org/nsedoc/scripts/rpcinfo.html) NSE script connects to portmapper and retrieves a list of all registered programs, including the PRC program number, support versions, port number and protocol, and program name, similar to the [`rpcinfo`](https://man.archlinux.org/man/rpcinfo.8.en) command.

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

- Common NFS-related NSE scripts:

| Script                                                                | Categoroes                                | Description                                                              |
| --------------------------------------------------------------------- | ----------------------------------------- | ------------------------------------------------------------------------ |
| [`nfs-ls`](https://nmap.org/nsedoc/scripts/nfs-ls.html)               | `discovery`, `safe`                       | Attempts to get useful information about files from NFS exports.         |
| [`nfs-showmount`](https://nmap.org/nsedoc/scripts/nfs-showmount.html) | `discovery`, `safe`                       | Shows NFS exports, like `showmount -e`.                                  |
| [`nfs-statfs`](https://nmap.org/nsedoc/scripts/nfs-statfs.html)       | `discovery`, `safe`                       | Retrieves disk space statistics and information from a remote NFS share. |
| [`rpcinfo`](https://nmap.org/nsedoc/scripts/rpcinfo.html)             | `discovery`, `safe`, `default`, `version` | Connects to portmapper and fetches a list of all registered programs.    |

### Shares

- List all exports and their access restrictions:

```bash
showmount -e <target>
```

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

- Force TCP (useful if UDP is blocked):

```bash
showmount -e <target> --no-udp
```

| Option                | Description                                                                   |
| --------------------- | ----------------------------------------------------------------------------- |
| `-a`,` --all`         | List client hostname or IP address and mounted directory (`host:dir` format). |
| `-d`, `--directories` | List only directories mounted by some client.                                 |
| `-e`, `--exports`     | Show the list of exports on an NFS server.                                    |
| `-v`, `--version`     | Display version and exit.                                                     |
| `--no-headers`        | Suppress descriptive headings from the output.                                |

## NetExec

- Prove for NFS service and basic info:

```bash
nxc nfs <target>
```

- List available shares:

```bash
nxc nfs <target> --shares
```

- List contents of a specific share:

```bash
nxc nfs <target> --share '/path/to/share' --ls '/'
```

- Recursive listing:

```bash
nxc nfs <target> --share '/home' --ls '/path'
```

>[!tip]+
>NetExec is useful in wide subnet sweeps where you want to identify all hosts running NFS quickly. For deep dive enumeration on a specific host, use `showmount` and `rpcinfo`.
### rcpinfo

`rpcinfo` queries `rpcbind` directly and gives you the full picture of what RPC services are running:

- List all registered RPC programs:

```bash
rpcinfo -p <target>
```

- Query a specific program by number (`100003` = NFS):

```bash
rpcinfo -T tcp <target> 100003
```

- Display a summary of all registered services:

```bash
sudo rpcinfo -s <target> 
```

## References and further reading


 - [`Sun RPC — Wikipedia`](https://en.wikipedia.org/wiki/Sun_RPC)
 - [`Remote procedure call — Wikipedia`](https://en.wikipedia.org/wiki/Remote_procedure_call)
- [`Network File System — Wikipedia`](https://en.wikipedia.org/wiki/Network_File_System)
 - [`NFS — Arch Wiki`](https://wiki.archlinux.org/title/NFS)
 - [`NFS (Network File System) — Hackviser`](https://hackviser.com/tactics/pentesting/services/nfs)

- [`Network File System (NFS): Overview & Setup — ninjaOne`](https://www.ninjaone.com/blog/network-file-system-nfs/)

- [`2049 - Pentesting NFS Service — HackTricks`](https://book.hacktricks.wiki/en/network-services-pentesting/nfs-service-pentesting.html)
- [`Linux Hacking Case Studies Part 2: NFS — NetSPI`](https://www.netspi.com/blog/technical-blog/network-pentesting/linux-hacking-case-studies-part-2-nfs/)
- [`NFS Pentesting Best Practices — secybr`](https://secybr.com/posts/nfs-pentesting-best-practicies/)

- [`NFS Share no_root_squash - Linux Privilege Escalation — Juggernaut Pentesting Academy`](https://juggernaut-sec.com/nfs-no_root_squash/)
