---
created: 2026-08-28
updated: 2026-08-29
---
## Gaining foothold

### Port scanning

- Scan all TCP ports:

```bash
sudo nmap -sV -sC 10.129.54.192 -p-
```

```bash
Starting Nmap 7.95 ( https://nmap.org ) at 2026-08-28 10:47 EDT
Nmap scan report for 10.129.54.192
Host is up (0.059s latency).
Not shown: 65532 filtered tcp ports (no-response)
PORT   STATE SERVICE VERSION
21/tcp open  ftp     Microsoft ftpd
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_Can't get directory listing: PASV failed: 425 Cannot open data connection.
| ftp-syst: 
|_  SYST: Windows_NT
23/tcp open  telnet  Microsoft Windows XP telnetd
| telnet-ntlm-info: 
|   Target_Name: ACCESS
|   NetBIOS_Domain_Name: ACCESS
|   NetBIOS_Computer_Name: ACCESS
|   DNS_Domain_Name: ACCESS
|   DNS_Computer_Name: ACCESS
|_  Product_Version: 6.1.7600
80/tcp open  http    Microsoft IIS httpd 7.5
|_http-server-header: Microsoft-IIS/7.5
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-title: MegaCorp
Service Info: OSs: Windows, Windows XP; CPE: cpe:/o:microsoft:windows, cpe:/o:microsoft:windows_xp

Host script results:
|_clock-skew: 1s

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 148.34 seconds
```

### Anonymous FTP access

- Access the FTP server via anonymous login:

```bash
ftp 10.129.54.192
```

```bash
Connected to 10.129.54.192.
220 Microsoft FTP Service
Name (10.129.54.192:user): anonymous
331 Anonymous access allowed, send identity (e-mail name) as password.
Password: 
230 User logged in.
Remote system type is Windows_NT.
```

- List remote directories: 

```bash
ftp> ls

200 PORT command successful.
125 Data connection already open; Transfer starting.
08-23-18  09:16PM       <DIR>          Backups
08-24-18  10:00PM       <DIR>          Engineer
226 Transfer complete.
```

- Inspect the directories and download all flies:

```bash
ftp> ls Backups

200 PORT command successful.
125 Data connection already open; Transfer starting.
08-23-18  09:16PM              5652480 backup.mdb
226 Transfer complete.
```

```bash
ftp> cd Backups

250 CWD command successful.
```

```bash
ftp> get backup.mdb
# ...
```

```bash
ftp> cd ..

250 CWD command successful.
```

```bash
ftp> cd Engineer

250 CWD command successful.
```

```bash
ftp> ls

200 PORT command successful.
125 Data connection already open; Transfer starting.
08-24-18  01:16AM                10870 Access Control.zip
226 Transfer complete.
```

```bash
ftp> get "Access Control.zip"
# ...
```

```bash
ftp> exit

221 Goodbye.
```

### `backup.mdb`

- To open a Microsoft Access file (`.mdb`) in Bash, you can use `mdbtools`:

```bash
sudo apt install mdbtools
```

- There, you find credentials:

```bash
admin:admin
engineer:access4u@security
backup_admin:admin
```

- Inside the `zip`, find:

```
security:4Cc3ssC0ntr0ller
```
## Questions

- How many TCP ports are listening on Access?
	- `3`