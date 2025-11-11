---
created: 2025-08-31
---
## Nmap

>**Nmap (Network Mapper)** is an open-source network scanning and enumeration tool written in C, C++, Python, and Lua.

>[!note] Core capabilities of Nmap:
> 
> - Host discovery 
> - Port scanning
> - Service and version detection
> - OS detection
> - Script execution
> - Vulnerability assessment
> - Firewall/IDS/IPS evasion
> - etc.


Articles in the series:
- [[྾_Nmap_host_discovery]]
- [[྾_Nmap_port_scanning]]
- [[྾_Nmap_version_detection]]
- [[྾_Nmap_NSE_scripts]]
- [[྾_Nmap_firewall_evasion]]

TBD: 
- Full Nmap options cheatsheet in one place
- General options
- Output options
## General options

| Option     | Description                                                               |
| ---------- | ------------------------------------------------------------------------- |
| `--reason` | Provide more details into Nmap reasoning and conclusions                  |
| `-v`       | Verbose                                                                   |
| `-vv`      | Even more verbose                                                         |
| `-d`       | Display debugging information                                             |
| `-dd`      | Display even more debugging information                                   |
| `-A`       | Enable OS detection, version detection, script scanning, and `traceroute` |

## Saving output

| Option | Description                                      |
| ------ | ------------------------------------------------ |
| `-oN`  | Output scan in the normal format.                |
| `-oX`  | Output scan in the XML format.                   |
| `-oG`  | Output scan in the Grepable (`grep`able) format. |
| `-oS`  | Output scan in the script-kiddie format.         |

There are three main formats to save Nmap output in:

1. Normal
2. Grepable (`grep`able)
3. XML

>The `grep`able format makes filtering scan output for specific keywords or terms more efficient.
>An example use of `grep` is `grep KEYWORD TEXT_FILE`; this command will display all the lines containing the provided keyword.

>The XML format is the most suitable for programs to parse.


| Option                      | Meaning                                         |
| --------------------------- | ----------------------------------------------- |
| `-sV`                       | determine service/version info on open ports    |
| `-sV --version-light`       | try the most likely probes (2)                  |
| `-sV --version-all`         | try all available probes (9)                    |
| `-O`                        | detect OS                                       |
| `--traceroute`              | run traceroute to target                        |
| `--script=SCRIPTS`          | Nmap scripts to run                             |
| `-sC` or `--script=default` | run default scripts                             |
| `-A`                        | equivalent to `-sV -O -sC --traceroute`         |
| `-oN`                       | save output in normal format                    |
| `-oG`                       | save output in grepable format                  |
| `-oX`                       | save output in XML format                       |
| `-oA`                       | save output in normal, XML and Grepable formats |
