---
created: 2026-03-31
tags:
  - network_services
  - net_hack
---

## NFS

>**[NFS](https://en.wikipedia.org/wiki/Network_File_System) (Network File System)** is a distributed file system protocol that allows users to access files over a network as if they were stored locally.

- NFS is mostly used in Unix/Linux systems for file sharing. 
- The remote client mounts a shared file system exposed by the server.

>[!important] NFS uses several ports, depending on its version and configuration:
> - **NFS** primarily operates on **TCP and UDP port `2049`**. It's used by all NFS versions (NFSv2, NFSv3, NFSv4).
> - NFSv2 and NFSv3 also use **TCP or UDP port `111`**. 
### NFS architecture and components 

NFS operates on a client-server architecture:

- **NFS Servers**
	- Exports directories configured in the **`/etc/exports` file** or files in the **`/etc/exports.d` directory**, in the **[NFS server export table](https://man.archlinux.org/man/exports.5)**.
	- Runs daemons like `rpcbind` (portmapper), `nfsd` (NFS service), `mountd` (mount daemon), and `lockd` (file locking).
	- Relies on UID/GID mappings to manage access permissions.

- **NFS client**
	- Uses `mound.nfs` or `automount` to to mount and access shares exported by the server.
	- Integrates into [VFS](https://en.wikipedia.org/wiki/Virtual_file_system) (Virtual File System)

>[!interesting]+ NFS daemons
>- `rpcbind` (portmapper)
>	- Listens on TCP/UDP port `111`.
>	- Maps **RPC program numbers** to network ports.
>	- Allows clients to discovery which ports NFS services are running on.
>	- **A central point of failure  for RPC-based services.**
>	- `/sbin/rpcbind`
>- `nfsd` (NFS daemon)
>	- Listens on TCP/UDP port `2049` (primary NFS port).
>	- Handles filesystem requests from NFS client; processes the actual file operations like reading, writing, creating, and deleting files over the network.
>	- `/usr/sbin/rpc.nfsd`
>- `rpc.mountd` (mound daemon)
>	- Handles mount/unmount requests from NFS clients; verifies client permissions before allowing filesystem mounts.
>	- Listens on a dynamic port (assigned by portmapper).
>	- `/usr/sbin/spc.mountd`
>- `rpc.lockd` (NLM, Network Lock Manager)
>	- Manages file locking (for concurrent access); implements the NLM (Network Lock Manager) protocol to coordinate file access and prevent data corruption from concurrent modifications. Runs on both clients and servers.
>	- Listens on a dynamic port (assigned by portmapper).
>	- `/usr/sbin/rpc.lockd`

>[!interesting]+ Mount process flow
>1. Client contacts portmapper to find the port `mountd` is listening on.
>2. Client sends a mount request to `mountd`.
>3. `mountd` verifies the requested export exists and the client has necessary permissions to mount it.
>4. `mountd` returns success status and root file handle.
>5. Client uses the file handle for subsequent NFS operations.

>[!interesting]+ File handles
>A **file handle** is a fixed-length, opaque identifier created by the NFS server that uniquely represents a file or directory within its exported filesystem. Clients receive file handles during operations such as `LOOKUP` or `MOUNT` and then use them in subsequent RPC calls (e.g., `READ`, `WRITE`, `GETATTR`, `SETATTR`).
>- Servers reject invalid or tampered handles; and since they're opaque, clients can't just forge them.

>[!note] NFSv4 integrates both mount functionality and locking into the main NFS protocol, eliminating the need for separate `mountd` and `lockd` daemons.

### NFS versions

Currently, there're three versions of NFS:

- **NFSv2** (1984)
	- Stateless protocol, uses UDP only.
	- Supports files up to 2 GB in size (32-bit offsets).
	- Each request is independent, the server keeps no client state.
	- No encryption, relies on host-based access control and client-supplied UID/GID.

- **NFSv3** (1995)
	- Stateless, uses UDP or TCP.
	- Supports files more than 2 GB in size (64-offsets).
	- Supports Secure RPC, but still mostly relies on client-supplied credentials. No built-in encryption.

- **NFSv4** (2000)
	- Stateful, uses TCP only.
	- Operates only over TCP port `2049` (no portmapper).
	- The server keeps track of the client state (e.g., open files, locks).
	- Built-in support for strong authentication (Kerberos, LIPKEY), integrity, and encryption.

| Feature               | NFSv2          | NFSv3                    | NFSv4                      |
| --------------------- | -------------- | ------------------------ | -------------------------- |
| **Year**              | 1984           | 1995                     | 2000                       |
| **Transport**         | UDP only       | UDP or TCP               | TCP only                   |
| **Stateful?**         | Stateless      | Stateless                | **Stateful**               |
| **Port**              | `2049` + `111` | `2049` + `111` + dynamic | **`2049` only**            |
| **Authentication**    | Client UID/GID | Client UID/GID           | **Kerberos, LIPKEY, SPKM** |
| **Security**          | None           | None                     | **Integrity, Encryption**  |
| **ACL Support**       | No             | Yes (via NFSACL)         | Yes (POSIX ACLs)           |
| **Firewall Friendly** | ❌ (many ports) | ❌ (many ports)           | ✅ (single port)            |
### RPC

NFS is not a standalone protocol. It runs on top of the **[RPC](https://en.wikipedia.org/wiki/Remote_procedure_call) (Remote Procedure Call)** protocol — specifically, **Sun RPC/[ONC-RPC]((https://en.wikipedia.org/wiki/Sun_RPC)) (Open Network Computing Remote Procedure Call)** implementation.

>**[RPC](https://en.wikipedia.org/wiki/Remote_procedure_call) (Remote Procedure Call)** is a stateless, connectionless communication protocol that allows one process (the **client**) to direct another process (the **server**) to execute procedure calls (subroutines) as if the client process had run the calls in its own address space, despite being on a separate physical system.

- Sun RPC uses **TCP or UDP port `111`**.

Common NFS PRC programs:

|Program ID|Name|Description|
|---|---|---|
|`100000`|`rpcbind`|Portmapper — maps services to ports|
|`100003`|`nfs`|Core NFS service (read/write)|
|`100005`|`mountd`|Handles mount requests|
|`100021`|`nlockmgr`|Network Lock Manager (file locking)|
|`100227`|`nfs_acl`|NFSv3 ACL extension|

>[!tip]+
>To see all registered programs, use `rpcinto -p TARGET`:
>```bash
>rpcbind -p 192.168.1.11
>```

- RPC messages use **[XDR](https://en.wikipedia.org/wiki/External_Data_Representation) (External Data Representation)** for cross-platform interoperability.

>[!note] XDR addresses fundamental compatibility issues, such as byte order (big-endian), alignment (32-bit), inconsistent data type representations across different architectures, and so on.

## NFS exports

>The act of making file systems accessible over the network is called **exporting**.

- To access files stored in the filesystem the NFS server exports, the client needs to **mount** that filesystem.

>[!important] Filesystems exported by the NFS server are configured in the **`/etc/exports` file** or files in the **`/etc/exports.d` directory**, in the **[NFS server export table](https://man.archlinux.org/man/exports.5)**.


>[!example]+ Example: `/nfs/exports`
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

In NFS, you can specify different **mount options** to control security, performance, and behavior of each export. Here are some common mount options:

| **Option**          | **Description**                                                                                                                                                                                                                                  |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `rw`                | Mount read-writes; allows clients to create, modify, and delete files.                                                                                                                                                                           |
| `ro`                | Mount read-only; prevents client writes.                                                                                                                                                                                                         |
| `sync`/`async`      | `sync`: synchronous data transfer (a bit slower).<br>`async`: asynchronous data transfer (a bit faster).                                                                                                                                         |
| `secure`/`insecure` | `secure`: do not accept requests from client ports above `1024`.<br>`insecure`: accept requests from client ports above `1024`.                                                                                                                  |
| `root_squash`       | Maps remote root user (UID `0`) to the anonymous user (`nobody`, typically UID/GID `65534`); this prevents the client's root user from having full root access on the exported filesystem.                                                       |
| `no_root_squash`    | **Dangerous.** Retains remote root's UID/GID `0` on the server; this allows the client's root user to **have root access to the exported filesystem**, including creating files as root, modifying system binaries, or installing SUID binaries. |
| `all_squash`        | Maps all client users (regardless of UID/GID) to the anonymous user.                                                                                                                                                                             |
| `no_subtree_check`  | Disables subtree checking when exporting subdirectories of a filesystem. Without this, the server verifies that a file resides within the exported subtree on every request. This improves performance.                                          |
| `subtree_check`     | Opposite of `no_subtree_check`; the server verifies each request’s path. Safer but slower.                                                                                                                                                       |
| `nohide`            |  If a filesystem is mounted below an exported directory, `nohide` causes the nested filesystem to be visible under the same export. This can unintentionally expose underlying filesystems that were meant to be separate exports.               |
| `vers=N`            | NFS protocol version to use (`2`, `3`, `4`, `4.1`, or `4,2`).                                                                                                                                                                                    |
| `rsize=N`           | Read/write buffer size.                                                                                                                                                                                                                          |
| `soft`/`hard`       | `hard` (default): retries operations indefinitely on server unresponsiveness; can hang processes.<br>`soft`: returns an error after retry count; might lead to data corruption if writes are incomplete.                                         |
| `noexec`/`exec`     | `noexec`: prevents binary execution on the mounted filesystem.<br>`exec`: allows execution.                                                                                                                                                      |
| `nodev`/`dev`       | `nodev`: disallows creation or use of special device files.<br>`dev`: allows device files.                                                                                                                                                       |
| `nosuid`/`suid`     | `nosuid`: ignores SUID/SGID bits.<br>`suid`: honor SUID/SGID bits.                                                                                                                                                                               |
| `nolock`/`lock`     | `nolock`: disable NLM locking.<br>`lock`: enable NLM locking.                                                                                                                                                                                    |

Export options are defined in `/etc/exports` (or `/etc/exports.d/`) on the NFS server. Each export line follows the format:

```
/export/path  client1(option1,option2,…)  client2(option1,option2,…)
```

## Identities and users in NFS

By default, in NFSv2/NFSv3, NFS **does not authenticate users by username or password**. Instead, it maps the UID/GID of your user on the client to a user on the server.

>[!important] NFS uses the UID and GID of **your current user on the client machine**.
>Your local UID/GID is sent with each NFS request, and the server accepts this data **at face value**. 
>**Anyone can claim to be any UID/GID.**

>[!example]+
>Say, you have UID `1001` on your local system:
>```bash
>id
># uid=1001(alice) gid=1001(alice)
>```
>You mount a share:
>```bash
>sudo mount -t nfs 192.168.1.11:/export /mnt/nfs
>```
>Inside that share, you will appear as **UID `1001`**. Files owned by UID `1001` will appear as owned by you.
>```bash
>ls -la /mnt/nfs/
>```


>[!important] NFSv4 supports Kerberos authentication.

But it's not always the same with the root user.
### Root squashing

By default, exports have the **`root_squash` mount option** enabled. This means that if your UID on your client is `0` (root), your user will be mapped to the **anonymous user inside the share** (usually `nobody`, UID `65534`). Other UIDs are preserved as-is.

>[!note]+ The `all_squash` export mount option can force **all UIDs to be mapped to `nobody`**, not just root. But it's not enabled  by default.

>[!bug] If the server exports have the `no_root_squash` mount option enabled, the UID `0` on the NFS client is preserved as UID `0` in the NFS share. In this case, direct privilege escalation is possible.


## Enumeration

### Nmap

- NFS enumeration with version detection and default scripts:

```bash
sudo nmap -p111,2049 -sV -sC 192.168.1.11
```

- NFS enumeration with NFS Nmap scripts:

```bash
sudo nmap p111,2049 -sV --script nfs* 192.168.1.11
```

>[!interesting]+ `rpcinfo` 
>The [`rcpinfo`](https://nmap.org/nsedoc/scripts/rpcinfo.html) NSE script connects to portmapper and retrieves a list of all registered programs, including the PRC program number, support versions, port number and protocol, and program name, similar to the [`rpcinfo`](https://man.archlinux.org/man/rpcinfo.8.en) command.

- Run the `rcpinfo` NSE script to enumerate RPC programs on the target:

```bash
sudo nmap p111,2049 -sV --script rpcinfo 192.168.1.11
```

>[!example]+ Example: `rpcinfo`
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

Common NFS-related NSE scripts:

| Script                                                                | Categoroes                                | Description                                                              |
| --------------------------------------------------------------------- | ----------------------------------------- | ------------------------------------------------------------------------ |
| [`nfs-ls`](https://nmap.org/nsedoc/scripts/nfs-ls.html)               | `discovery`, `safe`                       | Attempts to get useful information about files from NFS exports.         |
| [`nfs-showmount`](https://nmap.org/nsedoc/scripts/nfs-showmount.html) | `discovery`, `safe`                       | Shows NFS exports, like `showmount -e`.                                  |
| [`nfs-statfs`](https://nmap.org/nsedoc/scripts/nfs-statfs.html)       | `discovery`, `safe`                       | Retrieves disk space statistics and information from a remote NFS share. |
| [`rpcinfo`](https://nmap.org/nsedoc/scripts/rpcinfo.html)             | `discovery`, `safe`, `default`, `version` | Connects to portmapper and fetches a list of all registered programs.    |
### `showmount`

The [`showmount`](https://man.archlinux.org/man/showmount.8.en) command is used to display mount information for an NFS server. 

- Show exports on an NFS server:

```bash
showmount -e 192.168.1.11
```

- If the above command fails, try TCP mode (useful if UDP is blocked):

```bash
showmount -e 192.168.1.11 --no-udp
```

| Option                | Description                                                                   |
| --------------------- | ----------------------------------------------------------------------------- |
| `-a`,` --all`         | List client hostname or IP address and mounted directory (`host:dir` format). |
| `-d`, `--directories` | List only directories mounted by some client.                                 |
| `-e`, `--exports`     | Show the list of exports on an NFS server.                                    |
| `-v`, `--version`     | Display version and exit.                                                     |
| `--no-headers`        | Suppress descriptive headings from the output.                                |

>[!example]+ Example: `showmount -e`
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

### `rpcinfo`

The [`rpcinfo`](https://man.archlinux.org/man/rpcinfo.8.en) command makes an RPC call to an RPC server and reports what it finds. For example, it cal list all RPC services registered with `rpcbind`. 

- Enumerate RPC-based services:

```bash
rpcinfo -p 192.168.1.11
```

- Query specific programs:

```bash
rpcinfo -T tcp 192.168.1.11 100003
```

- List exports on a server:

```bash
sudo rpcinfo -s 192.168.1.11 
```
## Mounting NFS shares

- To mount an NFS share, you can use a standard `mount` command:

```bash
# sudo mmount -t nfs TARGET:/export/path /local/path -o OPTIONS
sudo mount -t nfs 192.162.1.11:/ ./nfs -o nolock

```


>[!example]+ Example: mounting NFS shares
> ```bash
> sudo mount -f nfs 192.162.1.11:/ ./nfs -o nolock
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

Once the share is mounted, you can browse it just like your local files and directories.

## Privilege escalation through NFS



## References and further reading


- [`NFS — Arch Wiki`](https://wiki.archlinux.org/title/NFS)

- [`Network File System — Wikipedia`](https://en.wikipedia.org/wiki/Network_File_System)
- [`Remote procedure call — Wikipedia`](https://en.wikipedia.org/wiki/Remote_procedure_call)
- [`Sun RPC — Wikipedia`](https://en.wikipedia.org/wiki/Sun_RPC)

- [`Network File System (NFS): Overview & Setup — ninjaOne`](https://www.ninjaone.com/blog/network-file-system-nfs/)

---

- [`2049 - Pentesting NFS Service`](https://book.hacktricks.wiki/en/network-services-pentesting/nfs-service-pentesting.html)

- [`Linux Hacking Case Studies Part 2: NFS — NetSPI`](https://www.netspi.com/blog/technical-blog/network-pentesting/linux-hacking-case-studies-part-2-nfs/)
- [`NFS Pentesting Best Practices — secybr`](https://secybr.com/posts/nfs-pentesting-best-practicies/)

- [`NFS Share no_root_squash - Linux Privilege Escalation — Juggernaut Pentesting Academy`](https://juggernaut-sec.com/nfs-no_root_squash/)


To be done:
- `nfs4-acl-tools`
- VFS
- NFS vulnerabilities and attacks