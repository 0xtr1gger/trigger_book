---
created: 14-01-2026
---
## Systemd 

>[systemd](https://systemd.io/) is a system and service manager for Linux operating systems that runs as PID `1`.

systemd was created to address limitations in traditional init systems:

- **Parallel service startup**: Unlike SysV init's sequential startup scripts, systemd can start services in parallel based on dependency resolution, significantly reducing boot time.
- **Dependency-based activation**: Services declare explicit dependencies, allowing systemd to manage complex relationships between units.
- **Socket-based activation**: Services can be started on-demand when a client connects to their socket, similar to inetd but more integrated.
- **Unified management interface**: The `systemctl` command provides a consistent interface for managing all types of system units.
- **Process supervision**: systemd tracks services using kernel control groups (cgroups), making it harder for processes to escape supervision.

systemd works as a **unified userspace control plane** responsible for:
- Process supervision
- Service management and dependency resolution
- Resource control (via cgroups)
- Logging (`journald`)
- Device management hooks
- Session and login management (`logind`)
- Timers (Cron replacement)
- Mount and automount management
- Network configuration
- Time synchronization (`timesyncd`)
## systemd units and unit files

>A **systemd unit** refers to any resource systemd manages. 
	
>A **systemd unit file** is a configuration file that defines how a specific unit should be managed by systemd.

- Unit files are written in an INI-like format and contain directives organized into sections.
- Units files have the following naming format:

```python
name.type
```

- Names are **globally unique** per unit type.
- Examples:
	- `ssh.service`
	- `multi-user.target`
	- `home.mount`
	- `systemd-journald.socket`

>[!important] systemd is managed by the [`systemctl`](https://man.archlinux.org/man/systemctl.1) command.
### systemd unit types

- Systemd defies **11 different types of units**:

| Unit file    | Description                                                                                                                         | Man page                                                                                 |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `.service`   | Manages system services (daemons).                                                                                                  | [`systemd.service(5)`](https://man7.org/linux/man-pages/man5/systemd.service.5.html)     |
| `.socket`    | Represents network (TCP/UDP) and Unix domain sockets.                                                                               | [`systemd.socket(5)`](https://man7.org/linux/man-pages/man5/systemd.socket.5.html)       |
| `.target`    | A group of other units.                                                                                                             | [`systemd.target(5)`](https://www.man7.org/linux/man-pages/man5/systemd.target.5.html)   |
| `.device`    | Manages units for kernel devices (`/sys` or `/dev`).                                                                                | [`systemd.device(5)`](https://www.man7.org/linux/man-pages/man5/systemd.device.5.html)   |
| `.mount`     | Manages filesystem mounts.                                                                                                          | [`systemd.mount(5)`](https://www.man7.org/linux/man-pages/man5/systemd.mount.5.html)     |
| `.automount` | Manages on-demand filesystem mounts (typically used for remote or removable media).                                                 | [`systemd.automount(5)`](https://man7.org/linux/man-pages/man5/systemd.automount.5.html) |
| `.timer`     | Responsible for time-based unit activation and scheduling (Cron replacement).                                                       | [`systemd.timer(5)`](https://man7.org/linux/man-pages/man5/systemd.timer.5.html)         |
| `.path`      | Used to monitor files and directories for specific events; can trigger actions when certain conditions are met (e.g., file change). | [`systemd.path(5)`](https://man7.org/linux/man-pages/man5/systemd.path.5.html)           |
| `.swap`      | Used to manage swap devices or files for memory paging.                                                                             | [`systemd.swap(5)`](https://man7.org/linux/man-pages/man5/systemd.swap.5.html)           |
| `.slice`     | Manages resources of a group of processes (with cgroups).                                                                           | [`systemd.slice(5)`](https://man7.org/linux/man-pages/man5/systemd.slice.5.html)         |
| `.scope`     | Manages a set of externally created system processes.                                                                               | [`systemd.scope(5)`](https://man7.org/linux/man-pages/man5/systemd.scope.5.html)         |
>[!note] See [`systemd(1)`](https://man7.org/linux/man-pages/man1/systemd.1.html) and [`bootup(7)`](https://man7.org/linux/man-pages/man7/bootup.7.html) man pages for more.

### Unit file locations

Unit files can be found in different placed in filesystem, depending on their purpose. Here is a list of systemd unit file directories, from the highest priority to the lowest:

- `/etc/systemd/system`
	- The primary directory for system-wide unit files that are created, modified, or installed by system administrators.
	- Unit files placed here will take precedence over identical unit files in other directories. 

- `/run/systemd/systemd`
	- Dynamic configuration for transient units; volatile, cleared at reboot.

- `/lib/systemd/system` or `/usr/lib/systemd/systemd`
		- The default directory that contains unit files provided by the distribution package manager.
		- Files here are generally overridden during operating system updates, therefore it is not advisable to modify files here directly (for these purposes, use `/etc/systemd/system` instead). 

-  `~/.config/systemd/user/` directories
	- For services that should be run in the context of a user session, user-specific unit files can be placed here. This is what allows regular users to manage their background services without the need to elevate privileges.

- To print the full list of directories there systemd looks for unit files, use this command:

```bash
systemctl show --property=UnitPath | tr ' ','=' '\n' | sed '1d' | awk -F'.' '{print $1}'
```

```
/etc/systemd/system
/run/systemd/system
/run/systemd/transient
/run/systemd/generator
/etc/systemd/system
/etc/systemd/system
/run/systemd/system
/run/systemd/system
/run/systemd/generator
/usr/local/lib/systemd/system
/usr/lib/systemd/system
/run/systemd/generator
```

- systemd supports **drop-in configuration files** which extend or override unit definitions. These are stored in:

- `/etc/systemd/system/<unit-name>.service.d/*.conf`
- `/run/systemd/system/<unit-name>.service.d/*.conf`
- `/usr/lib/systemd/system/<unit-name>.service.d/*.conf`

- Command to check unit file locations:

```bash
systemctl show --property=FragmentPath <unit_name>.service
```

```bash
systemctl show -p FragmentPath <unit_name>.service
```

>[!example]
> ```bash
> systemctl show -p FragmentPath bluetooth.service
> ```
> 
> ```bash
> FragmentPath=/usr/lib/systemd/system/bluetooth.service
> ```


## `systemctl`

- List all currently loaded units:

```bash
systemctl
```

You can filter units by type and status:

```bash
systemctl list-units --type=service --state=running
```

- `--type`: Filters units by type (e.g., `service`, `socket`).
- `--state`: Filters units by state (e.g., `active`). 

### Unit states

Each unit can be in one of the following states:

- `active` (`runnning`)
	- The unit is currently loaded into memory and actively running. 
	- For service units this means the service is up and doing its job.
- `active` (`exited`)
	- The unit has successfully executed a one-time configuration and is neither running an active process nor waiting for an event.
- `active` (`waiting`)
	- The unit has successfully executed a one-time configuration and is currently waiting for an event to happen.
- `inactive` (`dead`)
	- The unit is neither loaded nor running.
- `activating`
	- The using is in the process of being started, a halfway from `inactive` to `active`. 
- `deactivating`
	- The opposite of `activating` — a halfway from `active` to `inactive`.
- `loaded`
	- The configuration of this unit file has been successfully read and processed, but the unit is not currently active.

Unit file states:

- `enabled`
	- Systemd starts this unit at boot time.
- `disabled`
	- The unit is not started at boot.
- `static`
	- The unit can not be enabled or disabled, but it is required by other units and can be started on demand. 
	- It is either meant to be run once or is a dependency of another unit and should not be run alone.

- Display systemd unit status and last logs:

```bash
systemctl status polkit.service
```

## Unit file structure

Each unit file is organized into several sections, with names enclosed into square brackets `[]`. Each section contains variables that define the unit behavior and other information. 

Each unit file typically includes at least these three sections:

- `[Unit]`
	- Generic information about the unit.
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


- `Description`: Human-readable description of the unit.
- `Documentation`: Points to a manual page with detailed information about the service.
- `DefaultDependencies` controls whether the unit is treated as dependency even if it's not explicitly required by another unit. `false` means that this service won't be treated as a dependency.

Dependencies:

- `After`: This unit starts after the listed units.
- `Before`: This unit starts before the listed units.
- `Requires`: **Strong dependency**; if the required unit fails, this unit fails as well.
- `Wants`: **Weak dependency**; if the wanted unit fails, this unit continues anyway. In most cases, preferred over `Requires`.
- `Requisite`: Similar to `Requires`, but checks if required units are already active. If not, this unit fails immediately.
- `BindsTo`: Like `Requires`, but also stops this unit if the bound unit stops.
- `PartOf`: If the listed unit stops/restarts, this unit also stops/restarts (one-way relationship).
- `Conflicts`: Negative dependency; the unit can't run simultaneously with the listed units. If this unit starts, the conflicting units stop.

Conditions:
- `Condition...` (e.g., `ConditionPathExists`) and `Assert...` (e.g., `AssertPathIsDirectory`): Test conditions before starting the unit. `Condition...` failures are logged but don't cause failures, and `Assert...` failures cause the unit to fail.

### `[Service]` section

- `Type` sets the type of the service. `notify` means that the service will issue a notification upon start.
- `Sockets` specifies the socket on which the service listens, in this case, `dbus.socket`.
- `OOMScoreAdjust` adjusts the OOM (Out-Of-Memory) score of this service. A negative score means that the process will be killed before other processes if memory is low.
- `LimitNOFILE` sets a limit on the number of open file descriptors for the service. 
- `ProtectSystem` controls whether or not processes started by this unit can modify files in the system root directory `/`. `full` means that the `/usr`, `/boot`, and `/etc` directories are mounted read-only for these processes. `strict`, for example, sets the entire root filesystem to be mounted read-only, except `/dev`, `/proc`, and `/sys` for API.
- `PriateTmp=true` will create a private `/tmp` directory for each instance of the server (its content won't be visible to other processes). 
- `PrivateDevices` controls whether devices are accessible to unprivileged processes or not. 
- `ExecStart` specifies the command to start the service.
- `ExecReload` specifies a command to reload the service configuration. In this case, it's `busctl`, which is used to interact with D-Bus services.

`[Install]` section:
- `Alias` creates an alias for the service unit file. 

Many other unit configuration files are similarly straightforward. For example, the service unit file `sshd.service` enables remote secure shell logins by starting `sshd`.

>If a unit file is empty (zero bytes) or symlinked to `/dev/null`, it is considered to be **masked**. Masked units can not be started or enabled. 

We talked a lot about dependencies between systemd units in this section. Here is how you can list dependencies of a particular unit:

```bash
systemctl list-dependencies unit_name.unit
```

For example:

```bash
systemctl list-dependencies dbus.service
```

```
dbus.service
● ├─-.mount
● ├─dbus.socket
● ├─system.slice
● └─tmp.mount
```
## Targets

>A **systemd target** is unit that represents a specific system state or goal, used to group related units and set synchronization points for ordering dependencies with other unit files.

- Target function similarly to [runlevels](https://en.wikipedia.org/wiki/Runlevel) in [init](https://en.wikipedia.org/wiki/Init). Each target represents a common *operating mode* of a system.

Common targets:

- `default.target`
	- The default target used by systemd to start a system, typically aliased to `multi-user.target` or `graphical.target`.
	
>[!warning] `default.target` should never be aliased to `shutdown.target`, `reboot.target`, or similar.

- `multi-user.target`
	- Used for multi-user system without a GUI (Graphical User Interface). 

- `graphical.target`
	- Used for multi-user system with a graphical interface. 

- `emergency.target`
	- Provides a minimal bootable environment for system repair. 
	- Mounts only the root filesystem read-only; doesn't activate any network interfaces; runs a minimal set of services and provides some tools for troubleshooting. 

- `rescue.target`
	- Similar to `emergency.target`, but mounts all filesystems and provides more services and functions. 

- `poweroff.target` or `systemd-poweroff.target`
	- Initiates a safe shut down; used for powering the system off.

- `reboot.target`
	- Reboots the system.

Runlevel vs. target comparison:

| run level          | target                  | description                                |
| ------------------ | ----------------------- | ------------------------------------------ |
| `0`                | `poweroff.target`       | System halt.                               |
| `emergency`        | `emergency.target`      | Bare-bones shell for system recovery.      |
| `1`, `s`, `single` | `rescue.target`         | Single-user mode.                          |
| `2`                | `multi-user.target`     | Multi-user mode (command line).            |
| `3`                | `multi-user.target`<br> | Multi-user mode with networking (default). |
| `4`                | `multi-user.target`<br> | Not normally used by `init`.               |
| `5`                | `graphical.target`      | Multi-user mode with networking and GUI.   |
| `6`                | `reboot.target`         | System reboot.                             |

- View current target:

```bash
systemctl get-default
```

```bash
graphical.target
```

- Change default target:

```bash
systemctl set-default multi-user.target
```

- List all dependencies of the current target:

```bash
systemctl list-dependencies
```


## References and further reading

- https://www.digitalocean.com/community/tutorials/understanding-systemd-units-and-unit-files
- https://wiki.archlinux.org/title/Systemd

- https://gist.github.com/ageis/f5595e59b1cddb1513d1b425a323db04

- https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/using_systemd_unit_files_to_customize_and_optimize_your_system/assembly_working-with-systemd-unit-files_working-with-systemd#proc_creating-custom-unit-files_assembly_working-with-systemd-unit-files

Further reading:

https://systemd.io/

- A unit can have the following states:

| status     | description                                                     |
| ---------- | --------------------------------------------------------------- |
| `bad`      | some kind of problem within `systemd`; usually a bad unit file. |
| `disabled` | present, but not configured to start autonomously.              |
| `enabled`  | installed and runnable, will start autonomously.                |
| `indirect` | disabled, but has peers in `Also` clauses that may be enabled.  |
| `linked`   | unit file available through a symlink.                          |
| `masked`   | banished from the `systemd` from a logical perspective.         |
| `static`   | depended upon by another unit; has no install requirements.     |


Service states:

| state              | description                                                                                                                     |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------- |
| `active (running)` | Unit is running in the background.                                                                                              |
| `active (exited)`  | Service successfully started from the config file.<br>Typically one time services configuration read before Service was exited. |
| `active (waiting)` | Our service is running but waiting for an event such  <br>as CPUS/printing event.                                               |
| `inactive`         | Service is not running.                                                                                                         |
| `enabled`          | Service is enabled to activate on boot.                                                                                         |
| `disabled`         | Service is disabled from activating on boot.                                                                                    |
| `static`           | Service can not be enabled, but only started by another unit.                                                                   |
| `masked`           | Service is disabled and can not be started.                                                                                     |
| `alias`            | Service name is an alias, e.g., symlink to another unit file.                                                                   |
| `linked`           | Service is made available through one or more symlinks to the unit file.                                                        |
| status             | description                                                                                                                     |
| `bad`              | some kind of problem within `systemd`; usually a bad unit file.                                                                 |
| `disabled`         | present, but not configured to start autonomously.                                                                              |
| `enabled`          | installed and runnable, will start autonomously.                                                                                |
| `indirect`         | disabled, but has peers in `Also` clauses that may be enabled.                                                                  |
| `linked`           | unit file available through a symlink.                                                                                          |
| `masked`           | banished from the `systemd` from a logical perspective.                                                                         |
| `static`           | depended upon by another unit; has no install requirements.                                                                     ||
Unit subcommands:

| subcommand         | description                                                                                                                 |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| `enable`           | Enable a unit to activate on boot                                                                                           |
| `disable`          | Prevent a unit from activating on boot                                                                                      |
| `isolate <target>` | Changes operating mode to `target`, e.g., activates the stated target and its dependencies but deactivates all other units. |
| `start`            | Activate a unit immediately                                                                                                 |
| `stop`             | Deactivate a unit immediately                                                                                               |
| `restart`          | Restart (or start, of not running) a unit immediately                                                                       |
| `status`           | Show a unit's status and recent log entries                                                                                 |
| `kill <pattern>`   | Send a signal to units matching a pattern                                                                                   |
| `mask`             | Mask a unit                                                                                                                 |
| `unmask`           | Unmask a unit                                                                                                               |
>In systemd, a masked unit is a unit file that has been administratively disabled and cannot be started until it is unmasked. Masking a unit is a stronger form of disabling than simply disabling it, as it prevents the unit from being started even if another service requires it.

- When unit is masked, a symbolic link is created form the unit file's location, e.g., `/etc/systemd/system`, to `/dev/null`. This effectively disables the unit.
- A masked unit cannot be started manually or automatically, even if another enabled service requires it. Masking a unit prevents it from being loaded during system boot.
- To enable and activate a unit again, it first needs to be unmasked with `systemctl unmask <unit>`


Other subcommands:

| subcommand        | description                                 |
| ----------------- | ------------------------------------------- |
| `reboot`          | Reboot the system<br>                       |
| `list-units`      | List units                                  |
| `list-unit-files` | List unit files                             |
| `deamon-reload`   | Reload unit files and systemd configuration |

