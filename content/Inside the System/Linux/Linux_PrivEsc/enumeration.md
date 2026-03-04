---
created: 10-01-2026
tags:
  - in_progress
---
## Who are you?

- Current security context (your username and UID, groups you are a member of and their GIDs):

```bash
id
```

>[!example]+ Example: `id`
>```bash
>id
>```
>```bash
>uid=1000(trigger) gid=1000(trigger) groups=1000(trigger),998(wheel)
>```

- Username of the current user:

```bash
whoami
```

- Groups the current user is a member of (same as `id`, but only group names):

```bash
groups
```

>[!tip]+
>Look for privileged groups relevant for privilege escalation:
>- `sudo`/`wheel` → can run commands as root using `sudo`.
>- `docker` → can spawn privileged containers and escape to root.
>- `lxd`/`lxc` → can create Linux containers and escape to root.
>- `disk` -> direct read/write access to raw disk devices (e.g., `/dev/sda`).
>- `adm`/`systemd-journal` -> can read protected log files.
>- `shadow` -> can read `/etc/shadow` (password hashes).
>
>See [[privileged_groups]].
### Other users and groups

- Local users configured on the system:

```bash
cat /etc/passwd
```

```bash
getent /etc/passwd
```

>[!tip]
>
> - Are there any accounts with a shell?
> - Can you `su` to any of these accounts?
> - Try to find accounts with weak passwords.

- Information about a specific user:

```bash
getent passwd <username>
```

- Local groups and user members:

```bash
cat /etc/group
```

```bash
getent group
```

>[!note] `/etc/passwd` or `/etc/group` doesn't include users or groups managed by external sources, such as LDAP, NIS, or other directory services. 

>[!important]+ `getent` vs. files in `/etc`
>- The `/etc/passwd` and `/etc/group` files only contain information about **local users and groups** configured on the system explicitly. They **don't include users or groups managed by external sources**.
>- The `getent` command queries the system's **[Name Service Switch (NSS)](https://en.wikipedia.org/wiki/Name_Service_Switch) configuration** to retrieve entries for the specified database (in this case, `passwd` and `group`). It **aggregates data from multiple sources** (configured in `/etc/nsswitch.conf`), including:
>	- Local files (`/etc/passwd` and `/etc/group`)
>	- If configured, network services like [LDAP](https://en.wikipedia.org/wiki/Lightweight_Directory_Access_Protocol), [NIS](https://en.wikipedia.org/wiki/Network_Information_Service), etc.
>
>So, `getent` might return more complete information on system users. 

- Users without disabled login shells:

```bash
getent passwd | grep -v "nologin\|false"
```

### Currently logged-in users and login history

- Currently logged-in users and what they're doing:

```bash
w
```

```bash
who
```

- Last login history:

```bash
last
```

>[!note]+ `last` vs. `lastlog`
>- [`last`](https://man.archlinux.org/man/last.1) searches through the [`/var/log/wtmp`](https://man.archlinux.org/man/wtmp.5) file by default and displays a list of all users logged in and out since that file was created. `/va/log/wtmp` deals not only with user logins alone, but with virtually any change to the system-wide state recorded there.
>- [`lastlog`](https://man.archlinux.org/man/lastlog.8) pulls data from `/var/log/lastlog`, which is only concerned with previous logins. But this file is not really used anymore, so it's rare to find any data there.
>
>See [`Difference between last and lastlog? — Unix & Linux StackExchange`](https://unix.stackexchange.com/questions/192078/difference-between-last-and-lastlog) and  [`Why does lastlog show every user as never having logged in? — Unix & Linux StackExchange`](https://unix.stackexchange.com/questions/789526/why-does-lastlog-show-every-user-as-never-having-logged-in).

## Credential hunting

- SSH keys:

```bash
find / -name "id_rsa" -o -name "id_ecdsa" -o -name "id_ed25519" -ls 2>/dev/null
```

### PGP keys

- Current user's PGP keys:

```bash
gpg --list-keys 2>/dev/null
```

- Private keys:

```bash
gpg --list-secret-keys 2>/dev/null
```

- PGP keyrings:

```bash
find /home -name "*.gpg" -o -name "pubring.*" -o -name "secring.*" 2>/dev/null
```

```bash
find /home -type d -name ".gnupg" 2>/dev/null
```

### Passwords

- Files with `password` word in the `/etc` directory:

```bash
grep -ri "password" /etc 2>/dev/null
```

- Files with `pass` word in their names:

```bash
find / -name "*pass*" -type f 2>/dev/null
```

- API keys:

```bash
grep -r "api\|api.key\|apikey\|api_key" / 2>/dev/null | grep -v "proc"
```

## Environment variables and shell configuration

- Environment variables:

```bash
env
```

```bash
cat /etc/environment
```

- Current shell:

```bash
echo $SHELL
```

```bash
echo $0
```

### Shell configuration files

- Installed shells:

```bash
chsh -l
```

```bash
cat /etc/shells
```

- Check Bash startup files for sensitive information:

```bash
cat /etc/profile
```

```bash
cat ~/.bash_profile
```

```bash
cat ~/.bash_login
```

```bash
cat ~/.profile
```

```bash
cat ~/.bashrc
```

- Bash logout script:

```bash
cat /etc/bash.bash_logout
```

```bash
cat ~/.bash_logout
```

- Zsh startup scripts:

```bash
cat /etc/zsh/zshenv
```

```bash
cat $ZDORDIR/.zshenv
```

```bash
cat /etc/zsh/zprofile
```

```bash
cat $ZDOTDIR/.zprofile
```

```bash
cat /etc/zsh/zshrc
```

```bash
cat $ZDOTDIR/.zshrc
```

```bash
cat /etc/zsh/zlogin
```

```bash
cat $ZDOTDIR/.zlogin
```

```bash
cat ~/.zshrc
```

- Zsh logout scripts:

```bash
/etc/zsh/zlogout
```

```bash
cat $ZDOTDIR/.zlogout
```

>[!note] See [[shells]] for more. 

Look for:
- Hardcoded credentials (such as aliases like `alias prod='mysql -u root -p<password>'`)
- Scripts or commands executed on login (potential backdoors or monitoring)
### Shell history

- Current shell command history:

```bash
history
```

- History file location:

```bash
echo $HISTFILE
```

- Bash/Zsh history files:

```bash
cat ~/.bash_history
```

```bash
cat ~/.zsh_history
```

>[!note] History files may be symlinked to `/dev/null`. This disables command history.

- Find history files:

```bash
find / -type f -name "*hist*" -ls 2>/dev/null
```


>[!note] Check for `HISTFILESIZE` and `HISTSIZE` in shell configs. It they're set to `0`, history is disabled. 

## Privilege boundaries

### Sudo

- Commands the current user can execute with `sudo` (usually requires the current user's password):

```bash
sudo -l
```

- Same as above but more verbose:

```bash
sudo -ll
```

Look for:
- Commands with shell escape capabilities
- `NOPASSWD` entries
- `SETENV`, `env_keep`, or absence of `env_reset`
- Wildcards

>[!note] See [[sudo_privilege_escalation|sudo_PrivEsc]].
### SUID/SGID binaries

The goal is to find binaries that execute with **more privileges than the current user**.

- Find all **SUID** binaries:

```bash
find / -perm -4000 -type f 2>/dev/null
```

```bash
find / -perm u+s -type f 2>/dev/null 
```

- Find all **SGID** binaries:

```bash
find / -perm -2000 -type f 2>/dev/null
```

```bash
find / -perm g+s -type f 2>/dev/null
```

- Find binaries with **SUID or SGID** bits set:

```bash
find / -type f -a \( -perm u+s -o -perm -g+s \) -ls 2>/dev/null
```

```bash
find / -type f -a \( -perm -2000 -o -perm -4000 \) -ls 2>/dev/null
```

- Find binaries with both **SUID and SGID** set:

```bash
find / -type f -a \( -perm u+s -a -perm -g+s \) -ls 2>/dev/null
```

```bash
find / -perm /6000 -type f 2>/dev/null
```

>[!note] See [[SUID_&_SGID_privilege_escalation]].

### Vulnerable binaries


For any custom binary you can execute with elevated permissions or which is executed automatically (such as via a Cron job):

- Get file type and other relevant information (e.g., statically/dynamically linked, architecture, interpreter, etc.):

```bash
file /path/to/suid_binary
```

- Readable strings:

```bash
strings /path/to/suid_binary
```

- Trace library calls:

```bash
ltrace /path/to/suid_binary
```

- Trace system calls:

```bash
strace /path/to/suid_binary
```

Look for:
- Hardcoded passwords or keys
- Commands called without absolute paths (e.g., `system("ls")` instead of `system("/bin/ls")` — possible `PATH` hijacking)


### Cron jobs

>[!note] See [[Cron_jobs_privilege_escalation]].


- View the main system crontab:

```bash
cat /etc/crontab
```

- List additional system crontabs:

```bash
ls -l*
a /etc/cron.d
```

- List Cron directories:

```bash
ls -la /etc/cron.*
```

- List periodic Cron directories explicitly:

```bash
ls -la /etc/cron.{hourly,daily,weekly,monthly}/
```

- Show of all system crontab files:

```bash
cat /etc/cron.d/*
```

```bash
cat /etc/cron.hourly/*
```

```bash
cat /etc/cron.daily/*
```

```bash
cat /etc/cron.weekly/*
```

```bash
cat /etc/cron.monthly/*
```

### Systemd timers

- List all systemd timers:

```bash
systemctl list-timers --all
```

- Find timer unit files:

```bash
find /etc/systemd/system -name "*.timer" -ls 2>/dev/null
```

Look for service files you can write to, or that execute scripts you can modify.
### Capabilities

- Search for files with capabilities:

```bash
getcap -r / 2>/dev/null
```

Common dangerous capabilities:
- `cap_setuid+ep` — can set UID.
- `cap_dac_override+ep` — bypass file permissions.
- `cap_dac_read_search+ep` — read any file.

>[!note] [[capabilities_privilege_escalation]].

### `doas`

- Check `doas.conf`, `doas` configuration:

```bash
cat /etc/doas.conf
```

>[!note] `doas` is an alternative to `sudo`, common on OpenBSD and some Linux systems. See [[_doas]]. 

## File system enumeration

- The root directory:

```bash
ls -la /
```

Look for non-standard files or directories. Standard root directories include: `/bin`, `/boot`, `/dev`, `/etc`, `/home`, `/lib`, `/media`, `/mnt`, `/opt`, `/proc`, `/root`, `/run`, `/sbin`, `/srv`, `/sys`, `/tmp`, `/usr`, `/var`

- Application directories:

```bash
ls -la /opt
```

```bash
ls -la /srv
```

```bash
ls -la /var/www
```

```bash
ls -la /var/www/html
```

Web server directories often contain configuration files with database credentials.
### World-writable files and directories

- World-writable files:

```bash
find / -perm -0002 -type f -ls 2>/dev/null | grep -v '/proc/*\|/sys/*\|/usr/*'
```

- World-writable directories:

```bash
find / -perm -0002 -type d -ls 2>/dev/null | grep -v '/proc/*\|/sys/*\|/usr/*'
```

- Files writable by the current user:

```bash
find / -writable -type f 2>/dev/null | grep -v '/proc/*\|/sys/*\|/usr/*'
```

- Directories writable by the current user:

```bash
find / -writable -type d 2>/dev/null | grep -v '/proc/*\|/sys/*\|/usr/*'
```

### Binaries and scripts

- System binaries:

```bash
ls -la /bin \
	   /sbin \
	   /usr/bin \
	   /usr/sbin \
	   /usr/local/bin \
	   /usr/local/sbin
```

- Scripts:

```bash
find / -type f -name "*.sh" -ls 2>/dev/null | grep -v "src\|snap\|share"
```

### Configuration files

- Configuration files:

```bash
find / -type f -name "*.conf" 2>/dev/null
```

```bash
find / -type f \( -name "*.conf" -o -name "*.config" \) -ls 2>/dev/null
```

- Files that contain `config` in their names:

```bash
find / -type f -name "*config*" 2>/dev/null | grep -v proc
```

- Readable files in the `/etc` directory:

```bash
find /etc -type f -readable 2>/dev/null
```

- Backup files:

```bash
find / -name "*.bak" -o -name "*.backup" -o -name "*~" 2>/dev/null
```

- Database files:

```bash
find / -name "*.db" -o -name "*.sqlite" -o -name "*.sqlite3" 2>/dev/null
```


- Login policy configuration (including password aging, UID ranges, etc.):

```bash
cat /etc/login.defs
```

- [PAM (Pluggable Authentication Modules)](https://wiki.archlinux.org/title/PAM) configuration:

```bash
ls -ls /etc/pam.d
```

### Temporary and cache directories

- Temporary files:

```bash
ls -la /tmp
```

```bash
ls -la /var/tmp
```

```bash
ls -la /dev/shm
```

```bash
ls -la /tmp /var/tmp /dev/shm
```


> [!important]+ `/tmp` vs. `/var/tmp` vs. `/dev/shm`
> - `/tmp`: Cleared on reboot, typically 10-day retention for files.
> - `/var/tmp`: Persists across reboots, 30-day retention.
> - `/dev/shm`: RAM-based tmpfs, cleared on reboot, often overlooked.

- Cache and log directories:

```bash
ls -la /var/cache /var/log
```

- Readable log files:

```bash
find /var/log -type f -readable 2>/dev/null
```

### Hidden files and directories

- Hidden files:

```bash
find / -name ".*" -type f -ls 2>/dev/null
```

- Hidden directories:

```bash
find / -name ".*" -type d -ls 2>/dev/null
```

### Recent filesystem activity

- Files modified in the last 24 hours:

```bash
find / -mtime -1 -type f 2>/dev/null | grep -v proc | head -20
```

- Files accessed in the last 24 hours:

```bash
find / -atime -1 -type f 2>/dev/null | grep -v proc | head -20
```

- Files created in the last 24 hours:

```bash
find / -ctime -1 -type f 2>/dev/null | grep -v proc | head -20
```

### Other interesting files and directories

- Current directory content:

```bash
ls -la .
```

- Root directory:

```bash
ls -la /
```

>[!tip]
>Check **the root of the filesystem `/`** for any non-standard files or directories, or any non-standard permissions.

- Other interesting directories:

```bash
ls -la /opt
```

```bash
ls -la /var/www
```

```bash
ls -ls /var/www/html
```
## Kernel and architecture

### Kernel

- System information, including kernel name, release, and version, hostname hardware platform, and processor architecture:

```bash
uname -a
```

>[!example]+
> ```bash
> uname -a
> ```
> ```
> Linux hostname 6.16.5-arch1-1 #1 SMP PREEMPT_DYNAMIC Thu, 04 Sep 2025 23:18:13 +0000 x86_64 GNU/Linux
> ```

| **Option** | **Displays**                             | Example                                                                                                 |
| ---------- | ---------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `uname`    | Kernel name                              | `Linux`                                                                                                 |
| `uname -a` | All available system information         | `Linux hostname 6.16.5-arch1-1 #1 SMP PREEMPT_DYNAMIC Thu, 04 Sep 2025 23:18:13 +0000 x86_64 GNU/Linux` |
| `uname -s` | Kernel name                              | `Linux`                                                                                                 |
| `uname -n` | Hostname                                 | `hostname`                                                                                              |
| `uname -r` | Kernel release version                   | `6.16.5-arch1-1`                                                                                        |
| `uname -v` | Type of the kernel and date of the build | `#1 SMP PREEMPT_DYNAMIC Thu, 04 Sep 2025 23:18:13 +0000`                                                |
| `uname -m` | Machine hardware name                    | `x86_64`                                                                                                |
| `uname -p` | Processor type (if known)                | `unknown`                                                                                               |
| `uname -i` | Hardware platform (if known)             | `unknown`                                                                                               |
| `uname -o` | Operating system name                    | ********`GNU/Linux`********                                                                                             |

- Kernel version and build information (e.g., version of the GCC compiler used to build the kernel):

```bash
cat /proc/version
```

>[!example]+ Example: `/proc/version`
>```bash
>cat /proc/version
>```
> ```bash
> Linux version 6.12.21-4-MANJARO (linux612@manjaro) (gcc (GCC) 14.2.1 20250207, GNU ld (GNU Binutils) 2.  
> 44) #1 SMP PREEMPT_DYNAMIC Tue, 01 Apr 2025 18:45:30 +0000
> ```
> 
> - The exact version of the kernel in use: `Linux version 6.12.21-4-MANJARO`.
> - The name of the user who have compiled the kernel: `linux612@manjaro`.
> - The version of the GCC compiler used to build the kernel: `gcc (GCC) 14.2.1 20250207, GNU ld (GNU Binutils) 2.44)`.
> - The type of the kernel: `#1 SMP PREEMPT_DYNAMIC`; SMP means Symmetric Multi-Processing Kernel.
> - The data and time when the kernel was built: `Tue, 01 Apr 2025 18:45:30 +0000`.

- Hostname, OS version, kernel version, hardware:

```bash
hostnamectl
```


>[!example]+ Example: `hostnamectl`
> ```bash
> hostnamectl
> ```
> 
> ```bash
>  Static hostname: hostname
>        Icon name: computer-vm
>          Chassis: vm 🖴
>       Machine ID: a9f960b588e04143aa8340912e0cbc4e
>          Boot ID: bc7eeb71de5b485c9fa860cef2a8f2de
>   Virtualization: kvm
> Operating System: Parrot Security 6.3 (lorikeet)  
>           Kernel: Linux 6.11+parrot-amd64
>     Architecture: x86-64
>  Hardware Vendor: UpCloud
>   Hardware Model: Cloud Server
> Firmware Version: 1.16.2-debian-1.16.2-1 
>    Firmware Date: Mon 2025-07-21
>     Firmware Age: 5month 3w 1d
> ```

>[!important] `Chassic` set to `vm` or `container` indicates a virtualized system. This may be a cloud instance (Azure, AWS, GCP, etc.). Try to query metadata endpoints (`curl http://169.254.169.245/latest/meta-data`).

- Installed kernels:

```bash
ls /boot/vmlinuz-*
```

>[!important] **Older kernels may contain known security vulnerabilities** that have been fixed in newer releases.
>The presence of multiple kernels itself doesn't necessarily imply the system is vulnerable. But if the administrator or automated process accidentally boots an older kernel, this makes the system vulnerable.

### OS release

- Distribution and version:

```bash
cat /etc/issue
```

- Detailed information about the Linux distribution and its version:

```bash
cat /etc/os-release
```

>[!interesting] The [`os-release`](https://www.freedesktop.org/software/systemd/man/latest/os-release.html) file contains detailed information about the operating system, including the name of the distribution, its version, links to documentation and support. 

>[!example]+
>```bash
>cat /etc/os-release
>```
> ```bash
> NAME="Arch Linux"  
> PRETTY_NAME="Arch Linux"  
> ID=arch  
> BUILD_ID=rolling  
> ANSI_COLOR="38;2;23;147;209"  
> HOME_URL="https://archlinux.org/"  
> DOCUMENTATION_URL="https://wiki.archlinux.org/"  
> SUPPORT_URL="https://bbs.archlinux.org/"  
> BUG_REPORT_URL="https://gitlab.archlinux.org/groups/archlinux/-/issues"  
> PRIVACY_POLICY_URL="https://terms.archlinux.org/docs/privacy-policy/"  
> LOGO=archlinux-logo
> ```

```bash
cat /etc/*-release
```

>[!note]+ `/etc/*-release`
>The wildcard here is critical. Different distributions use different files: 
>
> - `/etc/redhat-release` → RHEL, CentOS
> - `/etc/centos-release` → CentOS
> - `/etc/fedora-release` → Fedora
> - `/etc/debian_version` → Debian (old)
> - `/etc/arch-release` → Arch Linux
> - `/etc/SuSE-release` → SUSE (old)
> - `/etc/issue` → often contains login banner + distribution information (can be manually edited — **trust but verify**).

```bash
cat /etc/lsb-release
```

- LSB (Linux Standard Base) and distribution information on older systems:

```bash
lsb_release -a
```

>[!note] `lsb_release` is deprecated on newer systems but still present on Ubuntu 18.04 and older. 

### Kernel modules

- Information about currently loaded kernel modules:

```bash
lsmod
```

- Detailed information about specific kernel modules (version, dependencies, parameters, etc.):

```bash
modinfo MODULE_NAME
```

- Raw information about kernel modules from the `/proc` file system:

```bash
cat /proc/modules
```

### System architecture

- System architecture (32-bit vs 64-bit matters for exploits):

```bash
uname -m
```

```bash
arch
```

```bash
lscpu
```

```bash
getconf LONG_BIT
```


## Running processes and services

- All running processes:

```bash
ps aux
```

```bash
ps -ef
```

- Processes running as root:

```bash
ps -u root # effective UID
```

```bash
ps -U  # real UID
```

- Process tree:

```bash
pstree -p
```

```bash
pstree -a # with arguments
```

- Monitor processes in real-time (watch for Cron jobs): 

```bash
watch -n 1 "ps aux | grep root"
```

- [`pspy`](https://github.com/DominicBreuker/pspy):

```bash
./pspy64 -pf -i 1000
```

>[!note]+ Installation
>```bash
>wget https://github.com/DominicBreuker/pspy/releases/download/v1.2.1/pspy64 && chmod +x pspy64
>```

### Services & daemons

- Systemd services:

```bash
systemctl list-units --type=service
```

```bash
systemctl list-unit-files --type=service
```

- Service status:

```bash
systemctl status <service_name>
```

- Service logs:

```bash
journalctl -u <service_name>
```

- Service configuration files:

```bash
find /etc/systemd/system -type f 2>/dev/null
```

```bash
cat /etc/systemd/system/*.service
```

## Installed software

- Debian/Ubuntu:

```bash
dpkg -l
```

```bash
apt list --installed
```

- RedHat/CentOS:

```bash
rpm -qa
```

## Network enumeration

- Network interfaces:

```bash
ifconfig
```

```bash
ip addr
```

- Routing table:

```bash
route
```

```bash
ip route
```

- ARP cache (might show hosts on the local network):

```bash
arp -a
```

```bash
ip neigh
```

- Listening sockets:

```bash
ss -tulpn
```

```bash
netstat -tulpn
```


- Network connections:

```bash
ss -antp
```

```bash
netstat -antp
```

```bash
lsof -i # list of open files, including network sockets
```

- Specific port checks:

```bash
lsof -i :80
```

```bash
lsof -i :22
```

```bash
lsof -i 3306
```

>[!example]+
>If you find MySQL running:
>```bash
>mysql -h localhost -u root -p
>```

- Firewall rules:

```bash
iptables -L -n -v 2>/dev/null
```

```bash
cat /etc/iptables/* 2>/dev/null
```

- DNS information:

```bash
cat /etc/resolv.conf
```

```bash
cat /etc/hosts
```

- Network file shares:

```bash
showmount -e localhost
```

```bash
cat /etc/exports 2>/dev/null
```

>[!note] See [[NFS_privilege_escalation]].

## Mounted file systems

- Mounted file systems:

```bash
mount
```

```bash
cat /etc/fstab
```

```bash
df -h
```

- Block devices:

```bash
lsblk
```

## Automated tools

### LinPEAS

>[!note]+ Installation
>```bash
>wget 
>```


## References and further reading

- [`Difference between last and lastlog? — Unix & Linux StackExchange`](https://unix.stackexchange.com/questions/192078/difference-between-last-and-lastlog)
- [`Why does lastlog show every user as never having logged in? — Unix & Linux StackExchange`](https://unix.stackexchange.com/questions/789526/why-does-lastlog-show-every-user-as-never-having-logged-in)

Man pages:
- [`id`](https://man.archlinux.org/man/id.1.en)
- [`last`](https://man.archlinux.org/man/last.1)
- [`utmp`](https://man.archlinux.org/man/wtmp.5)


- [`uname`](https://man.archlinux.org/man/uname.1)
- [`hostnamectl`](https://man.archlinux.org/man/hostnamectl.1.en)
- [`lsb_release`](https://man.archlinux.org/man/lsb_release.1.en) 

### GTFOBins

- Retrieve a list of GTFOBins binaries:

```bash
export gtfobins=$(curl -s https://gtfobins.github.io/ | grep -oP '(?<=/gtfobins/)[^/"]+' | sort -u)
```

- Retrieve a list of all binaries with SUID or SGID bit set:

```bash
export set_id=$(find / -type f -a \( -perm -2000 -o -perm -4000 \) 2>/dev/null | awk -F'/' '{print $4}')
```

- Find vulnerable binaries on the system:

```bash
comm -12 \
  <(printf "%s\n" "$gtfobins" | sort -u) \
  <(printf "%s\n" "$set_id" | sort -u)
```

- One command (it's better to avoid `export` in this case):

```bash
comm -12 \
  <(curl -s https://gtfobins.github.io/ | grep -oP '(?<=/gtfobins/)[^/"]+' | sort -u) \
  <(find / -type f -a \( -perm -2000 -o -perm -4000 \) 2>/dev/null | awk -F'/' '{print $4}' | sort -u)
```

- Retrieve a list of GTFOBins binaries:

```bash
export gtfobins=$(curl -s https://gtfobins.github.io/ | grep -oP '(?<=/gtfobins/)[^/"]+' | sort -u)
```

- Retrieve a list of all binaries with SUID or SGID bit set:

```bash
export set_id=$(find / -type f -a \( -perm -2000 -o -perm -4000 \) 2>/dev/null | awk -F'/' '{print $4}')
```

- Find vulnerable binaries on the system:

```bash
comm -12 \
  <(printf "%s\n" "$gtfobins" | sort -u) \
  <(printf "%s\n" "$set_id" | sort -u)
```