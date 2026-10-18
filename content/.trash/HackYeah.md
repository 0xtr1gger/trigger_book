---
created: 2026-10-03
updated: 2026-10-03
---
## Office Terminal

```bash
sudo nmap -sT reentry-a856ddcdd44c-office-terminal-0-0.chals.io  
Starting Nmap 7.95 ( https://nmap.org ) at 2026-10-03 09:49 UTC
Nmap scan report for reentry-a856ddcdd44c-office-terminal-0-0.chals.io (143.244.222.115)
Host is up (0.020s latency).
Other addresses for reentry-a856ddcdd44c-office-terminal-0-0.chals.io (not scanned): 143.244.222.116
Not shown: 997 filtered tcp ports (no-response)
PORT     STATE SERVICE
80/tcp   open  http
443/tcp  open  https
8080/tcp open  http-proxy

Nmap done: 1 IP address (1 host up) scanned in 17.14 seconds
```

```bash
ffuf -w /usr/share/seclists/Discovery/Web-Content/DirBuster-2007_directory-list-2.3-medium.txt -u 'https://reentry-a856ddcdd44c-office-terminal-0-0.chals.io/FUZZ' -c -ic

login                   [Status: 405, Size: 153, Words: 16, Lines: 6, Duration: 177ms]
                        [Status: 200, Size: 3994, Words: 1117, Lines: 150, Duration: 175ms]
report                  [Status: 302, Size: 189, Words: 18, Lines: 6, Duration: 165ms]
mirror                  [Status: 302, Size: 189, Words: 18, Lines: 6, Duration: 167ms]
logout                  [Status: 302, Size: 189, Words: 18, Lines: 6, Duration: 148ms]
lookup                  [Status: 200, Size: 2886, Words: 901, Lines: 116, Duration: 156ms]
```


```
reel-A orbit telemetry, 1977 — nominal
reel-B orbit telemetry, 1977 — nominal
reel-C signal capture, 1977 — PURGED (see antenna archive)
```