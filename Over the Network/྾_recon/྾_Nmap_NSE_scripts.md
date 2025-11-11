---
created: 2025-08-31
tags:
  - nmap
---

## NSE

>The **Nmap Scripting Engine (NSE)** is an incredibly powerful addition to Nmap that allows you to extend functionality of the tool with scripts written in the Lua programming language.

Nmap scripts can automate reconnaissance, vulnerability detection, and even exploitation; perform brute-force attacks, gather service banners, enumerate users in network services, etc.

>[!important] Nmap scripts are stored in the `/usr/share/nmap/scripts` directory on Linux.
>- A default Nmap installation can contain almost **600 scripts**. 

NSE is one of the main reasons Nmap is so widely used by penetration testers, red teamers, and network defenders.

To search for relevant scripts:

- Grep the `/usr/share/nmap/scripts/scripts.db` file to search for relevant scripts:

```bash
grep "ftp" /usr/share/nmap/scripts/script.db
```

- `ls` relevant files:

```bash
ls -l /usr/share/nmap/scripts/*ftp*
```

## Script categories

NSE scripts are divided into 14 categories reflecting their purpose:

| **Category** | **Description**                                                                                         |
| ------------ | ------------------------------------------------------------------------------------------------------- |
| `auth`       | Authentication checks, credential testing.                                                              |
| `broadcast`  | Network-wide discovery (broadcast); discovered hosts can be automatically added to the remaining scans. |
| `brute`      | Brute-force attacks (e.g., for credentials, enumeration).                                               |
| `default`    | Safe, useful scripts run with the `-sC` option.                                                         |
| `discovery`  | Information gathering, enumeration.                                                                     |
| `dos`        | DoS (Denial of Service) attacks.                                                                        |
| `exploit`    | Exploitation of known vulnerabilities.                                                                  |
| `external`   | Scripts that interact with external resources.                                                          |
| `fuzzer`     | Fuzzing services for bugs.                                                                              |
| `intrusive`  | Potentially disruptive scripts.                                                                         |
| `malware`    | Malware detection.                                                                                      |
| `safe`       | Non-intrusive, safe scripts.                                                                            |
| `version`    | Service version detection.                                                                              |
| `vuln`       | Vulnerability detection.                                                                                |

- You can run all scripts in a category by specifying it as an argument to the `--script`:

```bash
nmap --script vuln 192.168.1.11
```

- Automatically execute scripts in the `version` category:

```bash
nmap -sC -sV 192.168.1.11
```
## Running scripts

- Show help for a script:

```bash
nmap --script-help http-title
```

- Run a single script:

```bash
nmap --script http-title 192.168.1.11
```

- Run all scripts in one or more categories:

```bash
nmap --script vuln 192.168.1.11
```

```bash
nmap --script vuln,malware 192.168.1.11
```

- Run all `default` scripts:

```bash
nmap -sC 192.168.1.11.
```

```bash
nmap --script default 192.168.1.11
```

- Also execute scripts in the `version` category:

```bash
nmap -sC -sV 192.168.1.11
```

- Run all scripts with names that match a wildcard:

```bash
nmap --script http* 192.168.1.11 # run all scripts starting with 'http'
```

- Run multiple scripts:

```bash
nmap --script "http-title,ssl-cert" 192.168.1.11
```

- Run script by specifying a custom path:

```bash
nmap --script /path/to/custom-script.nse 192.168.1.11
```

- Display all incoming and outgoing communication performed by scripts (similar to `--packet-trace` but works at the application level rather than network):

```bash
nmap --script http-title --script-trace 192.168.1.11
```

### Script arguments

Many scripts accept arguments to customize behavior:

```bash
nmap --script http-enum --script-args http.useragent="Mozilla/5.0" 192.168.1.11
```

### Updating script database

If you add or modify scripts, update the database:

```bash
sudo nmap --script-updatedb
```

### Execution and performance


- Limit execution time of each script run:

```bash
sudo nmap -sC --script-timeout 10m
```

- Debug mode for troubleshooting script execution:

```bash
nmap --script http-title -d 192.168.1.11
```


## Script types and phases

NSE scripts can be divided into 4 types based on the kind of targets they take and the scanning phase when they run:

- **Prerule scripts**
	- Run before any Nmap scan phases; when Nmap hasn't yet collected any information about its targets.
	- Useful for tasks which don't depend on specific scan targets, e.g., sending broadcast requests to query DHCP and DNS servers. 
	- Examples: [`dns-zone-transfer`](https://nmap.org/nsedoc/scripts/dns-zone-transfer.html) (obtains a list of IP addresses in a domain using a zone transfer; automatically adds these IP addresses to the Nmap's scan target list). 
	- Prerule scripts can be identified by containing a `prerule` function.

- **Host scripts**
	- Run during Nmap's normal scanning process, after Nmap has performed host discovery, port scanning, version detection, and OS detection against the targets. 
	- Invoked once against each target host that matches the `hostrule` function.
	- Examples: [`whois-ip`](https://nmap.org/nsedoc/scripts/whois-ip.html) (looks up WHOIS information for a target IP address), [`path-mtu`](https://nmap.org/nsedoc/scripts/path-mtu.html) (tries to determine the maximum IP packet size which can reach the target without fragmentation),

- **Service scripts**
	- Run against specific services listening on a target host; the most common Nmap script type.
	- These scripts are distinguished by containing a `portrule` function that decides which detected services a script should run against.

- **Postrule scripts**
	- Run after Nmap has scanned all its targets; useful for formatting and representing Nmap output.
	- Examples: [`ssh-hostkey`](https://nmap.org/nsedoc/scripts/ssh-hostkey.html) (shows the target SSH server's key fingerprint and the public key itself).
	- Postrule scripts are identified by containing a `postrule` function.

## Writing your own scripts (in progress)
### Script structure

Each NSE script is a Lua file (with the `.nse` extension) that contains:
- **Header/metadata section:** name, description, author, license, and categories of the script.
- **Rule section:** defines when the script should run (e.g., on a specific port or service).
- **Action section:** the main logic of the script (what it does).

>[!example]+ Example skeleton
> ```Lua
> -- Head Section
> local shortport = require "shortport"
> description = [[Checks for open HTTP port (80).]]
> author = "Your Name"
> categories = {"discovery"}
> 
> -- Rule Section
> portrule = shortport.port_or_service(80, "http")
> 
> -- Action Section
> function action(host, port)
>   return "Port 80 is open on " .. host.ip
> end
> ```

## References and further reading

- [`Usage and Examples, Nmap Scripting Engine — Nmap`](https://nmap.org/book/nse-usage.html)
- [`Script Writing Tutorial — Nmap`](https://nmap.org/book/nse-tutorial.html)