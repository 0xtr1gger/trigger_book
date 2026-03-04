---
created: 10-01-2026
---

A shell can be:
- Login + interactive
- Non-login + interactive
- Non-login + non-interactive
- Login + non-interactive (rare but possible)

## Interactive vs. non-interactive shells

>An **interactive shell** is a shell attached to a terminal (`STDIN` and `STDOUT` are attached to a `tty`) **or** stared with the `-i` option.

- A shell is interactive if it's started without non-option arguments (unless `-s` is specified) and without the `-c` option.
- An interactive shell, among other, displays a prompt (`PS1`), expands aliases, supports job control, command history, tab completion, and signal handling (see [`interactive shell behavior`](https://www.gnu.org/software/bash/manual/bash.html#Interactive-Shell-Behavior-1) for the full list of features).
- Examples of interactive shells include `bash`, `bash -i`, `ssh user@host`, `su -`, etc.

>A **non-interactive shell** is designed to execute scripts without human intervention. 

- A shell is non-interactive if it's invoked to execute a script, has no terminal attached, and is not started with `-i`. 
- Non-interactive scripts can run in the background, but interactive ones hang, waiting for input that never comes.
- In contrast to interactive shells, non-interactive shells **do not execute startup scripts and configuration files** (e.g., `~/.bashrc`, `~/.profile`, etc.).
- Limitation of non-interactive shells include:
	- No prompts.
	- No tab completion.
	- No command history (you can't use the up arrow to recall previous commands).
	- No job control (you can't background jobs with `Ctrl+Z` or use `fg`/`bg`).
	- No interactive applications. Commands like `su`, `sudo`, `top`, `htop`, `vim`, `nano`, `ftp`, `ssh` will fail or behave erratically because they require a true TTY to manage screen rendering and user input.
	- Awkward signal handling (e.g., `Ctrl+C` won't work as expected to terminate a process).

To see if the current shell is interactive:

```bash
[[ $- == *i* ]] && echo "interactive"
```

```bash
case "$-" in
*i*)	echo This shell is interactive ;;
*)	    echo This shell is not interactive ;;
esac
```

```bash
if [ -z "$PS1" ]; then
        echo This shell is not interactive
else
        echo This shell is interactive
fi
```

>[!note]+ `BASH_ENV` 
>When invoked non-interactively (e.g., to run a shell script), Bash looks for the `BASH_ENV` environment variable and executes the file it specifies (if the variable is non-empty). In this case, **the `PATH` variable is not used to search for the filename**. 


## Login vs. non-login shells

### Login shells

>A **login shell** is a an invocation mode in which the shell reads files intended for one-time initialization, such as system-wide `/etc/profile`, user's `~/.profile`, or other user-specific files. These files are used to set up the initial environment, which is then inherited by all other processes started from the shell (including non-login shells and graphical programs). 

- A shell is login if it's the first process executed under your UID after you log in for an interactive session, if it's started with the `--login`/`-l` option.
- Examples of login shells include `login`, `ssh user@host`, `su - user`, `bash --login`, etc.

When a login shell is invoked, Bash attempts to execute a set of startup files:
1. `/etc/profile`
	- Sources application settings in `/etc/profile.d/*.sh` and `/etc/bash.bashrc`.
2. `~/.bash_profile`
	- Per-user application settings; often sources `~/.bashrc`.
3. `~/.bash_login`
	- If exists, executes startup scripts. 
4. `~/.profile`
	- One-time shell initialization scripts.

>[!note]+ The `--noprofile` option in Bash inhibits Bash from executing startup profile files.


On exit, a Bash login shell executes:
1. `/etc/bash.bash_logout` (depends on the `-DSYS_BASH_LOGOUT="/etc/bash.bash_logout"` compilation flag).
2. `~/.bash_logout` (per-user).

>A **non-login shell** is any shell that is **not** the first shell of a session and not started with `--login`.

- Examples of non-login shells include `bash`, `bash -i`, etc.

On startup, an interactive non-login shell attempts to execute: 
1. `/etc/bash.bashrc` (depends on the `-DSYS_BASHRC="/etc/bash.bashrc"` compilation flag; sources `/usr/share/bash-completion/bash_completion`).
2. `~/.bashrc` (per-user).

>[!note] The `--norc` option inhibits this behavior; `--rcfile` can be used to specify a custom file instead of `~/.bashrc`.

- Check if the current shell is login:

```bash
shopt -q login_shell && echo "login shell"
```

```bash
echo $0   # starts with "-" in some shells
```


## Shell history
## Options

Options are settings that change shell and/or script behavior.

- The `set` command enables/disables options within a script.
- Options can also be enabled/disabled from a command line.
- The `$-` variable contains a set of shell options/flags enabled in the current shell session.

| Option        | Name            | Description                                                                                                                                 |
| ------------- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `+/-B`        | brace expansion | Enables/disables brace expansion.                                                                                                           |
| `+/-C`        | noclobber       | Prevents files to be overwritten by redirection (may be overriden by `>\|`).                                                                |
| `-a`          | allexport       | Export all defined variables.                                                                                                               |
| `-b`          | notify          | Notify when jobs running in background terminate.                                                                                           |
| `-c`          |                 | Read commands from...                                                                                                                       |
| `-e`          | errexit         | Abort a script at first error (when a command exits with a non-zero status; expect `until`/`while` loops, `if` tests, and list constructs). |
| `-f`          | noglob          | Disable filename expansion (globbing).                                                                                                      |
| `-i`          | interactive     | Run in interactive mode.                                                                                                                    |
| `-n`          | noexec          | Read commands in script, but don't execute them (syntax check).                                                                             |
| `-o <option>` |                 | Invoke the `<option>` option.                                                                                                               |
| `-o posix`    | POSIX           | Change behavior of Bash or invoked script to conform to POSIX standard.                                                                     |
| `-o pipefail` | pipe failure    | Causes a pipeline to return the exit status of the last command in the pipe that returned a non-zero return value.                          |
| `-p`          | privileged      | Script runs as SUID (disabled by default).                                                                                                  |
| `-r`          | restricted      | Script runs in resticted mode.                                                                                                              |
| `-s`          | stdin           | Reads commands from `STDIN`.                                                                                                                |
| `-t`          |                 | Exit after the first command.                                                                                                               |
| `-u`          | nounset         | Attempt to use undefined variable outputs an error message and forces an exit.                                                              |
| `-v`          | verbose         | Print each command to `STDOUT` before executing it.                                                                                         |
| `-x`          | xtrace          | Similar to `-v`, but expands commands.                                                                                                      |
| `-`           |                 | End of options flag; all other argumnets are positional parameters.                                                                         |
| `--`          |                 | Unset positional parameters (positional parameters are set to argumnets).                                                                   |
## References and further reading


- [`Difference between Login Shell and Non-Login Shell? — Unix & Linux ShackExchange`](https://unix.stackexchange.com/questions/38175/difference-between-login-shell-and-non-login-shell)
- [`Options — Advanced Bash-Scripting Guide`](https://tldp.org/LDP/abs/html/options.html)
- [`Restricted shells — Advanced Bash-Scripting Guide`](https://tldp.org/LDP/abs/html/restricted-sh.html)