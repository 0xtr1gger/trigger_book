---
created: 2026-09-19
updated: 2026-09-20
---
## Gaining foothold 

- Port scanning:

```bash
sudo nmap -p- 10.129.234.67
```
```bash
Starting Nmap 7.95 ( https://nmap.org ) at 2026-09-19 13:14 EDT
Nmap scan report for 10.129.234.67
Host is up (0.061s latency).
Not shown: 65532 filtered tcp ports (no-response)
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
3389/tcp open  ms-wbt-server

Nmap done: 1 IP address (1 host up) scanned in 157.64 seconds

```

- Version detection:

```bash
sudo nmap 10.129.234.67 -p 22,80,3389 -sV -sC

```
```bash
Starting Nmap 7.95 ( https://nmap.org ) at 2026-09-19 13:17 EDT
Nmap scan report for 10.129.234.67
Host is up (0.055s latency).

PORT     STATE SERVICE       VERSION
22/tcp   open  ssh           OpenSSH for_Windows_9.5 (protocol 2.0)
80/tcp   open  http          Apache httpd 2.4.56 ((Win64) OpenSSL/1.1.1t PHP/8.1.17)
|_http-server-header: Apache/2.4.56 (Win64) OpenSSL/1.1.1t PHP/8.1.17
|_http-title: ProMotion Studio
3389/tcp open  ms-wbt-server Microsoft Terminal Services
| rdp-ntlm-info: 
|   Target_Name: MEDIA
|   NetBIOS_Domain_Name: MEDIA
|   NetBIOS_Computer_Name: MEDIA
|   DNS_Domain_Name: MEDIA
|   DNS_Computer_Name: MEDIA
|   Product_Version: 10.0.20348
|_  System_Time: 2026-09-19T17:17:27+00:00
|_ssl-date: 2026-09-19T17:17:31+00:00; -1s from scanner time.
| ssl-cert: Subject: commonName=MEDIA
| Not valid before: 2026-09-18T16:56:58
|_Not valid after:  2027-03-20T16:56:58
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 12.89 seconds

```
