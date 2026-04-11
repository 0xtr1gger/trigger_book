---
created: 2026-04-10
---
## Finger

>**[Finger user information protocol](https://en.wikipedia.org/wiki/Finger_(protocol))** is a simple, text-based network protocol developed in 1970s for retrieving human-oriented user and system information across a network. 

>[!important] The finger protocol operates over TCP port `79`.

- Finger is legacy, almost ancient, so you'll rarely see it in the wild. 
- Typically, the information provided includes the **user’s login name, full name**, and, in some cases, additional details, such as office location and phone number, the time the user logged in, the period of inactivity (idle time), the last instance mail was read by the user, and the contents of the user’s plan and project files.

- A daemon may disclose:
	- **currently logged-in users**
	- **full names / GECOS data**
	- **home directories, shells, last login times, and TTYs**
	- **`.plan` / `.project` contents**
	- **relay behavior** to query a second host through the first one

- The protocol is **ASCII over TCP/79**, normally terminated with **CRLF**, and the **server closes the TCP connection** after the response. In practice a null query (`\r\n`) is often enough to retrieve the current user list, which is also what Nmap’s default `finger` NSE script does.


## Enumeration

### Nmap scanning

- Check default finger ports and run version scan:

```bash
sudo nmap -sV -p 79 <target>
```

> [!tip]+
> - Basic port scanning + version detection — in case you suspect non-standard ports:
> 
> ```bash
> sudo nmap -sV -p- <target>
> ```


- There's only one Nmap script for finger — [`finger`](https://nmap.org/nsedoc/scripts/finger.html) (`default`, `discovery`, `safe`). It attempts to retrieve a list of usernames using the finger service:

```bash
sudo nmap -sV -sC -p 79 <target>
```

```bash
sudo nmap -p 79 --script finger <target>
```

Nmap’s `finger` NSE script is **safe** and simply sends a **null query** to recover the current user list. If you want broader username guessing against permissive daemons, consider extending the approach with custom wordlists or using projects such as `fat-finger.nse`, which send multiple likely account names in one request and look for username/GECOS matches.


- Metasploit uses more tricks than Nmap:

```
use auxiliary/scanner/finger/finger_users
```
### User enumeration

- List users:

```bash
finger @<target>
```

- Get information about a specific user:

```bash
finger admin@<target>
```

- Long format from common UNIX clients:

```bash
finger -l user@<target>
```

- Alternatively you can use **[`finger-user-enum`](https://github.com/pentestmonkey/finger-user-enum)** script from [`pentestmonkey`](https://pentestmonkey.net/tools/user-enumeration/finger-user-enum):

```bash
finger-user-enum.pl -U users.txt -t 10.0.0.1
finger-user-enum.pl -u root -t 10.0.0.1
finger-user-enum.pl -U users.txt -T ip_addresses.txt
finger-user-enum.pl -U users.txt -t 10.0.0.2 -r 10.0.0.1
```

>[!warning] The important nuance with Finger enumeration is that there is **no strict response format** across daemons. Tools such as `finger-user-enum` work well against Solaris-style services because valid and invalid users produce different text layouts, but you may need to manually compare **positive** and **negative** replies and adapt the regexes if the target daemon is unusual.


Useful probes when the daemon is not behaving like stock Solaris/BSD:

```bash
# Null query: enumerate currently logged-in users
printf '\r\n' | nc -vn <IP> 79

# Long format
printf '/W\r\n' | nc -vn <IP> 79
printf '/W root\r\n' | nc -vn <IP> 79

# Spray several likely accounts in one go against permissive daemons
printf 'root admin oracle mysql ftp user test\r\n' | nc -vn <IP> 79
```

## Command execution

```bash
finger "|/bin/id@example.com"
finger "|/bin/ls -a /@example.com"

```


RFC 1288 explicitly allows implementations to execute a **user-controlled program** in response to a Finger query, which is where the classic `|/bin/...` abuse comes from. This is rare today, but if you find a custom or legacy daemon, test carefully for:

- shell metacharacters in username handling
- `|program` execution in plan/project hooks
- backend wrappers that pass the username to a shell script or CGI

Also remember the **client-side** abuse path on Windows: `finger.exe` is a signed LOLBIN that can retrieve arbitrary text from a remote Finger server on **TCP/79**, then pipe that output into another process. That technique is more relevant for post-exploitation than service enumeration, so see [the Linux reverse-shell page](https://hacktricks.wiki/en/generic-hacking/reverse-shells/linux.html) for the shell transport idea and keep it in mind when emulating attacker tradecraft.


## References and further reading

- [`79 - Pentesting Finger — HackTricks`](https://hacktricks.wiki/en/network-services-pentesting/pentesting-finger.html)
- 