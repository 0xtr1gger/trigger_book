---
created: 13-01-2026
n:
---
## Sudo

>The **[`sudo`](https://wiki.archlinux.org/title/Sudo) (Super User DO)** is a command that allows a user to execute a command another user (usually `root`) based on rules defined in `/etc/sudoers` and `/etc/sudoers.d/*`.

- The most common use for `sudo` is executing <command>s as root. This is safer than just logging in as root with `su`.

```bash
sudo <command>
```

- When you run `sudo <command>`, the system checks rules defined in `/etc/sudoers` and `/etc/sudoers.d/*` to see if you have permissions to run the `<command>` with `sudo`.
- If allowed, you're prompted for the **password for your current user** (unless configured otherwise).
- If you don't specify the user, `root` is assumed.

>[!important] `sudo` logs both the command and its output.

`sudo` options:

| Option                     | Description                                                                                                                              |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `-u`, `--user`             | Execute <command> as another user instead of root.                                                                                       |
| `-i`, `--login`            | Launch a login shell (similar to `su`).                                                                                                  |
| `-s`, `--shell`            | Start a shell specified in the `$SHELL` environment variable of the target user.                                                         |
| `-K`, `--remove-timestamp` | Force a password prompt next time you use `sudo`.                                                                                        |
| `-k`, `--reset-timestamp`  | Invalidate the `sudo` session (reset timestamp; password must be entered on next `sudo` run).                                            |
| `-l`, `--list`             | List the <command>s that the current user sis allowed to execute with `sudo`                                                             |
| `-D`, `--chdir`            | Specify the directory where to run the <command>                                                                                         |
| `-R`, `--chroot`           | Specify a new root directory to change to before running the <command>                                                                   |
| `-h`, `--host`             | Run <command> on the specified host                                                                                                      |
| `-e`, `--edit`             | Edit one or more files rather than running a <command> (`sudoedit`).                                                                     |
| `-g`, `--group`            | Specify the primary group to run the <command> with instead of the primary group specified by the target user's password database entry. |
| `-V`, `--version`          | Print the `sudo` version and exit.                                                                                                       |

>[!note] For more information, see [`sudo`](https://man.archlinux.org/man/sudo.8).

## `/etc/sudoers` file structure

>The [`/etc/sudoers`](https://man.archlinux.org/man/sudoers.5) file, as well as files located in `/etc/sudoers.d`, control which users can use `sudo`, what commands they can run, and under what conditions.

>[!note] Files in `/etc/sudoers.d/` are parsed in lexicographical order, and files with a `.` or `~` in the name are ignored.

Each line in `/etc/sudoers` defines a rule in the following format:

```bash
user    host = (runas_user:runas_group)    tags  command
```

- `user`: Specifies who is allowed to run the command. This can be a username, a system group (prefixed with `%`, a network group (prefixed with `+`), or a `User_Alias`). `ALL` means any user.
- `host`: Specifies on which host(s) the rule applies to. `ALL` means any host.
- `(runas_user:runas_group)`: Specifies the user and/or group identity that the command can be run as. If this field is omitted, defaults to `(root)`. `(ALL:ALL)` means the command can be run as any user and any group.
- `tags`: Optional keywords that modify the rule's behavior.
- `command`: The command(s) the user is allowed to run. `ALL` means any command.

| Tag                  | Description                                              |
| -------------------- | -------------------------------------------------------- |
| `NOPASSWD`           | The user is not required to enter their password.        |
| `PASSWD` (default)   | Requires the user to enter their password.               |
| `NOEXEC`             | Prevents the command from executing other programs.      |
| `EXEC` (default)     | Allows the command to execute other programs.            |
| `SETENV`             | Allows the user to preserve their environment variables. |
| `NOSETENV` (default) | Overrides user-defined environment variables.            |
Common examples:

- Allow a user to run all commands as all users and groups on all hosts:

```bash
trigger ALL=(ALL:ALL) ALL
#        |   |    |    |
#        |   |    |  <command>s
#        |   | run as group
#        | run as user
#     hostname 
```

- Full root access for a user:

```bash
trigger ALL=(ALL:ALL) ALL
```

- No password requires:

```bash
trigger ALL=(ALL:ALL) NOPASSWD: ALL
```

- Allow only specific commands:

```bash
trigger ALL=(ALL:ALL) /usr/bin/apt-get, /usr/bin/systemctl
```

- Full root access to all members of a group:

```bash
%wheel ALL=(ALL:ALL) ALL
```

- Forbid specific commands:

```bash
trigger ALL=(ALL:ALL) ALL, !/usr/bin/vim
```

>[!note] Files in `/etc/sudoers.d/` are parsed in lexicographical order, and files with a `.` or `~` in the name are ignored.```

- Allow to run scripts in the specified directory without password:

```bash
trigger ALL=(ALL:ALL) NOPASSWD: /usr/local/scripts/*
```

## Default settings

>`Default` lines set global options for the `sudo` environment.

Common defaults and security settings:

- `secure_path` overrides the user's `PATH` variable (prevents `PATH` hijacking).

```bash
Defaults        secure_path="/usr/local/sbin:/usr/local/bin:/usr/bin"
```

- `env_reset` resets the environment to a known state. This prevents users from passing their own variables (e.g., `LD_PRELOAD`) to the privileged command.

```bash
Defaults        env_reset
```

- `tty_tickets` requires a separate password for each terminal session.

```bash
Defaults        tty_tickets
```

- `lecture` displays a lecture, or disclaimer, the first time (or always) a user runs `sudo`.

```bash
Defaults        lecture=always
```

- `env_keep` specifies what user-defined environment variables to keep, if any:

```bash
Defaults env_keep += "HOME"
```


>[!warning] Never edit the `/etc/sudoers` file or files in the `/etc/sudoers.d` directly with a regular editor — always use `visudo`.
>`visudo` which checks the file for syntax errors before saving. If you edit `/etc/sudoers` directly and make a mistake, there's a good chance you will lose access to the root or any user on the system.
>```bash
>sudo visudo
>```
>```bash
>sudo visudo -f /etc/sudoers.d/trigger
>```

>[!warning]+ Always specify the absolute path to any binaries listed in `/etc/sudoers`.
>Otherwise, an attacker might be able to abuse the `PATH` variable to create a malicious binaries that will be executed when the <command> runs (e.g., if the `sudoers` entry specifies `cat` instead of `/bin/cat` this can be abused). This can lead to privilege escalation.


>[!warning] Follow the principle of the least privilege when granting `sudo` rights.