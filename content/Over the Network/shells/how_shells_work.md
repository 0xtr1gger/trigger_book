---
created: 22-01-2026
---
## What shells really are

A shell is fundamentally a process that implements a command interpreter. It reads input, parses commands, and orchestrates their execution.

But if you look deeper, shells and terminals use several layers of abstraction, and at each layer, different software and kernel components work together to create the interactive command-line experience you're familiar with.

The complete system consists of several distinct components that communicate with each other:

- **Terminal emulator** — The graphical application you see, such as `xterm` or `GNOME Terminal`.
- **Pseudoterminal (PTY)** — The virtual communication channel with the shell.
- **Line discipline** — The kernel layer that processes user input.
- **TTY driver** — Manages sessions and terminal settings.
- **Shell** — The command interpreter, such as `/bin/bash`.

Let's take a closer look at each component.
## Terminal emulator

>A **terminal emulator** is a software application that replicates the functionality of traditional [hardware terminals](https://en.wikipedia.org/wiki/Computer_terminal#Dumb_terminals).

- A terminal emulator is a *graphical application*, a user interface, which role is to interpret data coming from the *shell* and display it on the screen, as well as to capture keyboard input and pass it to the shell (via the PTY). It operates *entirely in userspace*.
- It also handles fonts, colors, formatting, window resizing, scrolling, text selection, and other visual elements. 

>[!important] Terminal emulator itself does not interpret commands — that's the shell's job.
>It's just another application on your system, an interface. Purely the display and input layer.

Here are some examples of popular terminal emulators for different operating systems:

| **Terminal Emulator**                                          | **Operating System**     |
| :------------------------------------------------------------- | :----------------------- |
| [Windows Terminal](https://github.com/microsoft/terminal)      | Windows                  |
| [cmder](https://cmder.app/)                                    | Windows                  |
| [PuTTY](https://www.putty.org/)                                | Windows                  |
| [kitty](https://sw.kovidgoyal.net/kitty/)                      | Windows, Linux and MacOS |
| [Alacritty](https://github.com/alacritty/alacritty)            | Windows, Linux and MacOS |
| [xterm](https://invisible-island.net/xterm/)                   | Linux                    |
| [GNOME Terminal](https://en.wikipedia.org/wiki/GNOME_Terminal) | Linux                    |
| [Konsole](https://konsole.kde.org/)                            | Linux                    |
| [MATE Terminal](https://github.com/mate-desktop/mate-terminal) | Linux                    |
| [Terminal](https://en.wikipedia.org/wiki/Terminal_\(macOS\))   | MacOS                    |
| [iTerm2](https://iterm2.com/)                                  | MacOS                    |

Capabilities of a terminal are described in a database called **`terminfo`**. It it often used by terminal-based applications to adapt to different terminal types. 

- To query these terminal capabilities, you can you use the [`tput`](https://man.archlinux.org/man/tput.1.en) command:

```bash
# the full name of the current terminal
tput longname

# supported colors
tput colors

# the number of columns in the current terminal (width)
tput cols

# the number of lines in the current terminal (height)
tput lines
```

- To view the `terminfo` database entries for your current terminal, you can use the [`infocmp`](https://man.archlinux.org/man/infocmp.1m) command:

```bash
infocmp
```

A terminal emulator is connected to a shell via a *pseudoterminal*, or *PTY*, which provides a bi-directional asynchronous communication channel between the two.
## Pseudoterminals

>A **pseudoterminal**, or **PTY**, is a pair of virtual character devices that establish an *asynchronous*, *bidirectional* communication channel between two or more processes (IPC, Inter-Process Communication), such as between the terminal emulator and the shell.

- So, when you type text into the terminal, it's sent to the shell through the PTY's standard input (`stdin`). When the shell returns some output or error, it's sent back to the terminal emulator through the PTY's standard output (`stdout`) and standard error (`stderr`).

A pseudoterminal consists of two components, to which official documentation refers by **master** and **slave**:

- **Master end**
	- Connected to a terminal emulator (e.g., `xterm`, `GNOME Terminal`) or remote login server (e.g., Telnet, SSH server) process, controls the slave side.
	- *Anything written on the master end is passed to the process on the slave end.*
	- The master is typically represented by `/dev/ptmx` (pseudo-tty multiplexer). When you open `/dev/ptmx`, the kernel allocates a new PTY pair and assigns a corresponding slave device.

- **Slave end**
	- Connected to a shell process, such as `/bin/bash` or `/bin/zsh`.
	- Emulates a hardware serial port device; used by the shell to read input from the terminal and write output back.
	- *Anything written to the slave end can be read by the process connected to the master end.*
	- Data flow between the master and slave is handled asynchronously. 
	- The slave is represented by `/dev/pts/x` device files, like `/dev/pts/0`, `/dev/pts/1`, and so on. These are virtual devices created and managed by the kernel's PTY subsystem on demand.

>[!interesting]+ How it all works together
> Here is what happens when you start a terminal emulator:
> 
> 1. The terminal emulator initializes and opens `/dev/ptmx`, which causes the kernel to create a new PTY pair.
> 2. The terminal emulator then initializes a shell on the slave end.
> 3. The master end of the PTY is kept open; this is what the terminal emulator reads from to display output. At the same time, the shell uses the slave end for its standard input, output, and error streams.  
> 4. When you type a command, the terminal emulator writes it to the PTY master, where it's processed and eventually reaches the shell's `stdin`.
> 5. To run a command, the shell forks itself and creates a new process.
> 6. The new process runs the program corresponding to the command and returns output to the shell.
> 7. The shell then sends the data to the terminal emulator via the PTY.
> 8. The terminal emulator parses the data ad displays it on the screen.

Remote access protocols like SSH and Telnet work quite similarly. 

You can discover which pseudoterminal you're currently using with the `tty` command:

```bash
tty
```
```bash
/dev/pts/1
```

The `ps` command also shows the associated PTY for each process:

```bash
ps
```
```bash
   PID TTY          TIME CMD  
 11486 pts/1    00:00:00 zsh  
 11730 pts/1    00:00:00 ps
```
## Line discipline

Between the PTY master and slave, there sits a kernel layer called the **line discipline**. 
The line discipline is why you can backspace and edit your commands before pressing `Enter` — it implements much of the interactive editing behavior you're used to. 
Simply put, it's a set of rules and processing logic that intelligently processes your input before passing it to the shell. 

>The **[line discipline](https://docs.kernel.org/driver-api/tty/tty_ldisc.htmlhttps://docs.kernel.org/driver-api/tty/tty_ldisc.html)** (LDISC) is a **kernel layer** that sits between the PTY's master and slave, processing all incoming and outgoing characters.

Primary responsibilities of a line discipline include:

- **Line buffering**
	- The line discipline accumulates characters you type into a *kernel buffer* and holds them until you press `Enter`. This is why you can edit commands before sending them to the shell.

- **Canonical mode editing**
	- The line discipline also interprets special characters you use to edit commands, such as backspace and delete, `Ctrl + U` to clear the line, `Ctrl + W` to delete a word, and others. All these operate on the line discipline's internal buffer.

- **Echo** 
	- When you type a character, the line discipline automatically sends it back to `stdout` so you can see what you're typing. If echo were disabled, you'd be typing into a black hole.
	- By the way, this is what happens when you enter a password — the terminal disabled echo so the characters you type don't appear on the screen, but the line discipline still captures them.

- **Signal generation**
	- Special key combinations are intercepted and converted into signals sent to the foreground process group. 
	- For example, `Ctrl + C` generates `SIGINT` (signal interrupt), `Ctrl + Z` generates `SIGTSTP` (signal stop), `Ctrl + \` generates `SIGQUIT` (signal quit), and `Ctrl + D` generates an `EOF` (end of file) signal.
	- Without line discipline, these characters would be treated literally.

- **Flow control** 
	- `Ctrl + S` (`XOFF`, transmit off) and `Crtl + Q` (`XON`, transmit on) allows you to pause and resume terminal output. This is rarely used in modern systems but was essential when dealing with slow serial connections.

>[!warning] The line discipline operates in kernel space with elevated privileges.

>[!note] The line discipline itself is a part of a *TTY driver*. But it's a whole different story, probably a topic for a separate article.
### Cooked vs. raw mode

A line discipline can operate in two different modes:

- **Canonical mode** (*cooked*)
	- The default mode for interactive shells.
	- Input is not passed to the reading application immediately. Instead, characters are accumulated in an internal kernel buffer. 
	- The complete line is only sent to the shell when the user presses `Enter`.
	- From the shell's perspective, this means a `read()` system call on `stdin` will block (wait) until an entire line is available. The `read()` call then returns the complete line, minus the newline character itself.

- **Non-canonical** (*raw* or *cbreak* mode)
	- In this mode, line discipline is mostly disabled.
	- Characters are passed directly to the application as soon as they are typed. There's no buffering, no line editing, and very minimal special character interpretation.
	- A `read()` call will return as soon as any character is available — it might return just one character at a time.
	- In this mode, a program's `read()` call will return as soon as _any_ character is available. It might return just one character at a time.
	- This mode is used by text editors like `vim` and `emacs`. When you press the `j` key in `vim`, you want the cursor to move down immediately, not wait for you to press `Enter`. To achieve this, `vim` puts the terminal into non-canonical mode at startup and restores canonical mode when it exits.

>[!note] This is why in a non-interactive terminal, backspaces look as a weird sequence of characters. 

>[!example]+ Example: typing `grep` in canonical mode
> 1. You type `grpe`. The line discipline buffer now contains `g`, `r`, `p`, `e`. Nothing is sent to the shell yet.
> 2. You realize you made a typo, so you press Backspace twice. The line discipline removes the `pe` from its buffer, which now contains `gr`. The characters don't get sent to the shell.
> 3. You type `ep`, and the buffer is now `grep`. Still in the buffer.
> 4. You type a space and `file.txt`. The buffer is now `grep file.txt`.
> 5. You press Enter. The line discipline sees the newline character and passes the string `grep file.txt` to the shell's `read()` call, then clears its buffer for the next line.
> 6. The shell parses the command and executes `grep file.txt`.
### The `ssty` command

You can control line discipline settings using the `stty` command. To see your current terminal settings:

```bash
ssty -a
```

- Settings are shown as flags (prefixed with `-` to disable them) and values. 
- You can enable canonical mode with `stty icanon` and disable it with `stty -icanon`. 
- You can enable echo with `stty echo` and disable it with `stty -echo`. 
- To see which special characters are configured for various functions, use `stty -a` and look for lines like `intr = ^C`, `susp = ^Z`, etc.

To restore terminal settings, use `stty sane`:

```bash
stty sane
```

## Shells

>A **shell** is a command interpreter that reads commands, parses them, finds the executable programs they refer to, and orchestrates their execution.

Below are some popular shells:

- [`/bin/sh`](https://en.wikipedia.org/wiki/Bourne_shell) (Bourne Shell)
	- The original Unix shell, created by Stephen Bourne at Bell Labs. It's a simple shell with basic scripting capabilities.

- [`/bin/bash`](https://en.wikipedia.org/wiki/Bash_(Unix_shell)) Bash (Bourne-Again Shell)
	- The default shell on most Linux distributions, it extends `sh` with many features, like command-line completion (`Tab` completion), command history, job control, arrays, etc.

- [`/bin/zsh`](https://en.wikipedia.org/wiki/Z_shell) Z shell
	- An extended Bourne Shell with some features of `bash`, `sh`, and `tcsh`, it supports features like powerful command completion system, advanced globbing (pathname expansion), and loadable modules.

- [`/bin/ksh`](https://en.wikipedia.org/wiki/KornShell) Korn shell
	- Created by David Korn at Bell Labs, Korn shell combines features from both `sh` and `csh` (C shell), adding associative arrays, floating-point arithmetic, built-in regex, and some advanced scripting features.

- [`/bin/fish`](https://en.wikipedia.org/wiki/Fish_(Unix_shell)) Fish (Friendly Interactive Shell)
	- A user-friendly shell with with syntax highlighting, auto-suggestions, and web-based configuration.  

- [`/bin/csh`](https://en.wikipedia.org/wiki/C_shell) C shell
	- Created by Bill Joy at UC Berkeley. Its syntax resembles the C programming language.

- [`/bin/tcsh`](https://en.wikipedia.org/wiki/Tcsh) tee-shell
	- An enhanced version of `csh` with features line command-line completion, editing, and spelling correction.

- To see your current shell:

```bash
echo $SHELL
```

- Or, to see the exact shell process running:

```bash
ps -p $$
```

>[!note] The `$$` is a special variable containing the PID of the current shell. 

- For more details about the current shell process:

```bash
ps auz | grep $$
```

### REPL: the core operational loop

At its heart, an interactive shell operates on the principle similar to [REPL (Read-Eval-Print Loop)](https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop):

1. **Read**
	- The shell waits a line of input from its `stdin` (e.g., attached to the slave end of a PTY).

2. **Parse and expand**
	- The raw string of text is not executed directly, but undergoes a multi-stage parsing and expansion process, which may include:
		- The input line is broken down into a series of works (tokens) and operators (e.g., `|`, `>`, `&&`). This process is known as **tokenization**. For example, `ls -l /home > files.txt` is tokenized into `ls`, `-l`, `/home`, `>`, `files.txt`.
		- `~` is expanded to the current user's home directory (e.g., `/home/user`).
		- Variables like `$PATH` or `$USER` are replaced with their corresponding values.
		- Anything within `$(...)` or backticks `` `...` `` is executed as a separate command, and its output is substituted back into the original command line (**command substitution**).
		- Arithmetic expressions within `$((...))` are evaluated.
		- Wildcards like `*` and `?` are expanded into a list of matching file and directory names.

3. **Execute**
	- The parsed and expanded command is executed.

4. **Print**
	- The shell waits for the command to complete and then prints the prompt again, ready for the next command.

### Execution model: `fork()` and `execve()`

When you type a command like `ls -l`, the shell does not execute `ls` itself. Instead, it creates a new process to run it.

This is achieved with two fundamental system calls:

- **`fork()`**
	- The shell makes a `fork()` system call that creates a **new child process** that is almost exact duplicate of the parent (the shell itself).
	- Both processes continue running from the point of the `fork()` call.
		- The **parent process (the shell)** gets the child's Process ID (PID).
	    - The **child process** gets a PID of `0`.
- **`execve()`**
	- The **child process** immediately makes an `execve()` system call. This call **replaces the current process's memory image with a new one** loaded from an executable file on disk (in this case, `/bin/ls`). The child process ceases to be a copy of the shell and becomes the `ls` process.

Meanwhile, the **parent shell process** does one of two things:
- If the command is **foreground**, the shell calls `wait()` or `waitpid()` to *suspend its own execution* until the child process terminates.
- If the command is **background** (e.g., `ls -l &`), it does **not** wait. It prints the child's PID and immediately returns to the Read step of its REPL loop, printing a new prompt.

What's described above can be applied to **external commands**, i.e., programs that exist as separated flies on the filesystem, such as `/bin/ls`, `/usr/bin/grep`, etc. 

There are also **built-in commands** — commands whose functionality is implemented directly within the shell executable itself. Examples include `cd`, `pwd`, `export`, `alias`, `exit`, and `echo`. Such commands **must** be built-ins because they need to **modify the state of the shell process itself**.

>[!example]+
> - If `cd` were an external command, the child process would change its own directory and then immediately exit. The parent shell's working directory would remain unchanged. By being a built-in, the `cd` command can directly execute the `chdir()` system call within the shell's own process, changing its current working directory.
> - The `export` command needs to modify the shell's own environment variable list, which is then passed to all future child processes.


> [!note]+ The `PATH` variable
> If you don't specify the full path to the program you want to execute, but just its name (such as `ls` instead of `/binls`) the shell uses the `PATH` variable to find that executable itself.
> 
>>The **[`PATH`](https://www.linfo.org/path_env_var.html) environment variable** specifies a colon-separated list of directories the shell searches sequentially to find executable files when you run a command by name without specifying its absolute or relative path.
> 
> ```bash
> echo $PATH
> ```
> ```shell-session
> /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games
> ```
> 
> 
## References and further reading

- [`Terminal emulator — Wikipedia`](https://en.wikipedia.org/wiki/Terminal_emulator)
- [`pty(7) — man pages`](https://man.archlinux.org/man/pty.7.en)


- [`Anatomy of a Terminal Emulator — poor.dev`](https://poor.dev/blog/terminal-anatomy/)
- [`The TTY demystified — linusakkesson.net`](https://www.linusakesson.net/programming/tty/) 
- [`Bash Shortcuts — tuxfigh3r`](https://gist.github.com/tuxfight3r/60051ac67c5f0445efee)

- [`Understanding The Linux TTY Subsystem — ishuah`](https://ishuah.com/2021/02/04/understanding-the-linux-tty-subsystem/)
- [`Build your own Command Line with ANSI escape codes`](https://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html)
