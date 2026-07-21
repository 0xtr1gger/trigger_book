---
created: 2026-07-18
tags:
  - recon
  - web_hacking
status: substantial
---
## Directory and file enumeration

- There are several primary techniques you can use for enumeration, and combining them achieves maximum coverage that no single method can match:
	- Walking through the application manually 
	- Passive reconnaissance & historical data
	- Automated web crawling
	- Active enumeration & fuzzing

- Before enumeration, ask yourself:
	- **What kind of application is this?** SPA, CMS, legacy MVC, or something else?
	- **What is the technology stack behind the application?** Programming language, -framework, web server, OS?
	- **Are there authorization boundaries?** Can you authenticate as a low-privileged user to access more routes?
	- **Is there a WAF?** Will aggressive fuzzing lead to rate-limiting or an IP address ban?

- This determines how exactly you should enumerate, and what wordlists to use.

>[!note] See [[Fingerprinting]].

>[!note]+ Directory and file enumeration can reveal:
> - **Sensitive data**: backup files, configuration, credentials, API keys.
> - **Development resources**: test environments, staging sites, administrative panels, Swagger UI docs.
> - **Outdated content**: still active, older versions of APIs (`/v1/` vs. `/v2/`) or scripts vulnerable to known exploits.
> - **Source code exposure**: `.git/`, `.svn/`, `.DS_Store`.

>[!tip] Inspect files like `robots.txt`, `sitemap.xml`, and files in the `/.well-known` directory. They may provide an initial overview of the application structure to base crawling and fuzzing on. See [[robots.txt and other interesting files]].
## Walking through the application manually

- Before using any automation, walk through the application manually with a web proxy like **Burp Suite** recording all requests and responses. Click every link, button, and menu item. Go through the entire user journey: registration, login, password reset, profile update, etc.

> [!tip] Many modern web applications (like SPAs built on React/Angular) render content on the client-side. Interact with JavaScript on the page to trigger API calls and reveal new endpoints that tools will miss.

 - Never underestimate the power of a human brain behind a browser. Manual navigation sets the baseline, populates your proxy history, and reveals business logic and naming conventions important for later fuzzing.

## Passive reconnaissance & historical data

- Pull historical data from web archives to have an overview of possible endpoints the Internet has already stashed.
- These can reveal live endpoints that were present in the past but are no longer referenced from the main application.
	- [`Internet Archive`](https://archive.org/)
	- [`Wayback Machine`](https://web.archive.org/)
	- [`Archive.today`](https://archive.ph/)
- Querying web archives can be automated using:
	- [`waybackurls`](https://github.com/tomnomnom/waybackurls) — Retrieves URLs from the Wayback Machine for a list of domains.
	- [`waymore`](https://github.com/xnl-h4ck3r/waymore) — Similar to `waybackurls`, but fetches URLs not only from the Wayback Machine, but also from Common Crawl, Alien Vault OTX, URLScan, and Virus Total.
	- [`gau`](https://github.com/lc/gau) — Retrieves URLs from AlienVault's [Open Threat Exchange](https://otx.alienvault.com), the Wayback Machine, Common Crawl, and URLScan.
	- [`paramspider`](https://github.com/devanshbatham/ParamSpider) — Retrieves URLs from the Wayback Machine for a list of domains (originally designed to collect interesting URL parameters for bug hunt).

```bash
waymore -i example.com -mode U | sort -U
```

```bash
cat targets.txt | waybackurls > urls.txt
```

```bash
gau example.com
```

```bash
paramspider -d example.com
```
## Web crawling (spidering)

> **Web crawling** is an automated process of systematically browsing and indexing web pages by following hyperlinks to discover all reachable content.

- Web crawlers mimic a human user’s navigation pattern to build an initial map of the target application. Good crawlers handle session management, handle JavaScript rendering (headless mode), and manage scope.

> [!warning] Web crawlers can only enumerate directories and files that are already referenced somewhere in the application. Hidden, unlinked pages will remain undetected.

- Common web crawlers:
	- **Burp Spider** (Burp Suite Professional)
	- **OWASP ZAP Spider**
	- [`harkawler`](https://github.com/hakluke/hakrawler)
	- [`Photon`](https://github.com/s0md3v/Photon)
	- [`katana`](https://github.com/projectdiscovery/katana)
	- [`crawlergo`](https://github.com/Qianlitp/crawlergo)
	- [`dirhunt`](https://github.com/Nekmo/dirhunt)
	- [`gospider`](https://github.com/jaeles-project/gospider)

>[!example]+ Examples
>>[!example]- `hakrawler` example
>>
>>```bash
>> cat urls.txt | hakrawler
>> ```
>>
>> ![[hakrawler_gin&juice.png]]
>---
>>[!example]- `photon` example
>> ```bash
>> python ./photon.py -u https://ginandjuice.shop --level 2 --verbose
>> ```
>> 
>> ![[Photon_gin&juice.shop.png]]
>---
>>[!example]- `katana` example
>>
>> ```bash
>> katana -u https://ginandjuice.shop
>> ```
>>![[katana_hin&juice.shop.png]]

>[!note] [`Gin&Juice`](https://ginandjuice.shop/) is a website created by PortSwigger for testing automatic web tools like crawlers or fuzzers. 

>[!warning] Dynamic or JavaScript-driven content can hinder automated crawling. These are better handled manually.

>[!warning] If not properly handled, web crawlers may miss content that requires authorization.

## Active enumeration & fuzzing

- Fuzzing is one of the most effective ways to enumerate directories and files that are not directly linked to other pages in a web application.
- It works by systematically probing different directory and file names from a wordlist, and then analyzing responses to identify live pages (see [[#Wordlists]]).

- Common tools:
	- [`ffuf`](https://github.com/ffuf/ffuf) (Fuzz Faster U Fool) — Gold standard written in Go.
	- [`gobuster`](https://github.com/OJ/gobuster) — A versatile brute-force tool for different enumeration tasks. 
	- [`wfuzz`](https://github.com/xmendez/wfuzz) — Similar to `ffuf`, Python-based.
	- [`feroxbuster`](https://github.com/epi052/feroxbuster) — Excellent for aggressive, recursive scanning.
	- [`dirsearch`](https://github.com/maurosoria/dirsearch) — Feature-rich directory and file enumeration tool.

>[!note] Most examples in this guide use `ffuf`.

>[!example]+
>- `fuff` command that combines recursive enumeration, extension fuzzing, threading control, and content matching; it matches responses that  contain the string `You don't have access!` in the body:
> ```bash
> ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/directory-list-2.3-small.txt -u http://example.com/FUZZ -recursion -recursion-depth 3 -t 50 -mr "You don't have access!" -e .hta,.htm,.html,.php,.php7,.phps,.phar
> ```
### Basic enumeration

- Basic directory and file enumeration:

```bash
ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -u https://example.com/FUZZ -c -ic
```

> [!tip] Use the `-ic` flag in `ffuf` to get rid of the copyright and other comments in wordlists.

>[!example]+ Example: `ffuf`
>```bash
>ffuf -w ./directory-list-2.3-small.txt:FUZZ -u https://example.com/FUZZ -c -ic
>```
> ```bash
> 
>         /'___\  /'___\           /'___\       
>         /\ \__/ /\ \__/  __  __  /\ \__/       
>         \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
>         \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
>          \ \_\   \ \_\  \ \____/  \ \_\       
>           \/_/    \/_/   \/___/    \/_/       
> 
>         v2.1.0-dev
> ________________________________________________
> 
>  :: Method           : GET
>  :: URL              : https://example.com/FUZZ
>  :: Wordlist         : FUZZ: /opt/useful/seclists/Discovery/Web-Content/directory-list-2.3-small.txt
>  :: Follow redirects : false
>  :: Calibration      : false
>  :: Timeout          : 10
>  :: Threads          : 40
>  :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
> ________________________________________________
> 
> :: Progress: [6/87664] :: Job [1/1] :: 0 req/sec :: Duration: [0:00:00] :# Copyright 2007 James Fisher [Status: 200, Size: 986, Words: 423, Lines: 56, Duration: 1ms]
> # ...
> blog                    [Status: 301, Size: 324, Words: 20, Lines: 10, Duration: 1ms]
> # ...
> forum                   [Status: 301, Size: 325, Words: 20, Lines: 10, Duration: 0ms]
> # ...
> ```

- Impose a delay between requests:

```bash
ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -u https://example.com/FUZZ -c -ic -p 0.8
```

- Limit requests per second:

```bash
ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -u https://example.com/FUZZ -c -ic -rate 10
```

| Option             | Description                                                                                                                                                              |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `-w`               | Wordlist to use. <br>By default, assigns the wordlist to the `FUZZ` keyword; you can set custom keywords for different wordlists using `-w <wordlist>:<keyword>` syntax. |
| `-u`               | Target URL to fuzz.                                                                                                                                                      |
| `-X`               | HTTP method (`GET`, `POST`, etc.).                                                                                                                                       |
| `-H`               | Custom HTTP headers (`-H "<header>: <value>"`).                                                                                                                          |
| `-d`               | `POST` data (for `POST` requests).                                                                                                                                       |
| `-r`               | Follow redirects (default `false`).                                                                                                                                      |
| `recursion`        | Scan recursively; only one keyword supported, `FUZZ`; the URL has to end with the keyword (e.g., `-recursion -u https://example.com/FUZZ`).                              |
| `-recursion-depth` | Maximum recursion depth (default `6`).                                                                                                                                   |
| `-o`               | Output file path.                                                                                                                                                        |
| `-v`               | Verbose output.                                                                                                                                                          |
| `-s`               | Silent mode (suppresses banner).                                                                                                                                         |
| `-c`               | Colorful mode.                                                                                                                                                           |
| `-ic`              | Ignore comments in wordlists (starting with `#`).                                                                                                                        |
| `-e`               | Comma-separated list of file extensions to try; extends the `FUZZ` keyword.                                                                                              |
| `-ac`              | Automatically calibrate filtering options.                                                                                                                               |
| `-p`               | Specify delay between requests, or a range of random delay (in seconds); e.g., `-p 0.1` or `-p 0.1-2.0`.                                                                 |
| `-rate`            | Rate of requests per second (default `0`).                                                                                                                               |
### Fuzzing file extensions

- Sometimes you can discover new files — or already known ones in different formats — only by explicitly appending a certain extension to the URL. One way to enumerate those is extension fuzzing.

>[!note] To save time and reduce the number of requests sent, try extensions based on the server technology stack you've discovered rather than probing all of them. 

- Use `-e` flag to append extension to the wordlist entries (each extension is added to each entry):

```bash
ffuf -w wordlist.txt -u https://example.com/FUZZ -e .php,.html,.bak -c -ic
```


>[!warning]+ The `-e` option only works with the `FUZZ` keyword.

- Alternatively, fuzz over two different wordlists: one with base file names and another with extensions:

```bash
ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt:FILE -w /usr/share/wordlists/seclists/Fuzzing/extensions-most-common.fuzz.txt:EXT -u https://example.com/FILE.EXT -c -ic
```

- Lists of extensions ([`SecLists`](https://github.com/danielmiessler/SecLists)):
	- [`Discovery/Web-Content/web-extensions.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/web-extensions.txt) (39 entries)
	- [`Fuzzing/extensions-most-common.fuzz.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/extensions-most-common.fuzz.txt) (30 entries, for quick enumeration)

>[!tip]
>If extensions in the wordlist contain a dot at the beginning, you can remove it with `sed`:
>```bash
>cat ./web-extensions.txt | sed 's/^.//' > ./web-extensions-no-dot.txt
>```
## Recursive fuzzing

- To enumerate nested subdirectories, fuzz recursively. When a directory is found, the tool automatically starts a new fuzzing job inside that directory.

```bash
ffuf -w directory-list-2.3-small.txt -u http://example.com/FUZZ -recursion -recursion-depth 3 -e .php,.html,.bak -ic -c
```

| Option                | Description                                                                                                                         |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `-recursion`          | Scan recursively. <br>Only one `FUZZ` keyword is supported, and URL has to end with `FUZZ`, e.g., `-r -u https://example.com/FUZZ`. |
| `-recursion-depth`    | Maximum recursion depth (default `6`).                                                                                              |
| `-recursion-strategy` | Recursion strategy: `default` (directories only) or `greedy` (recurse on all matches, including files).                             |

## Analyzing responses

Typical status code meanings in enumeration contexts:

- **`200 OK`**: Resource exists and is accessible; likely a valid discovery.
- **`301 Moved Permanently`, `302 Found`, `307 Temporary Redirect`**: Resource exists but redirects to another location; analyze redirect targets. Redirects to login or registration pages may indicate the need for authentication or authorization.
- **`401 Unauthorized`**: Resource exists but requires authentication; a potential target for credential attacks.
- **`403 Forbidden`**: Resource exists but access is denied due to authorization rules; may be a subject to bypass techniques.  
- **`404 Not Found`**: Resource likely doesn't exist, though custom error pages may use `404` deceptively.
- **`500 Internal Server Error`**: Server-side error; potentially indicates vulnerable code or misconfigurations; a good target for more thorough investigation. 

>[!warning] Many modern applications implement custom error handling that complicates response analysis. Applications may return `200` status codes for non-existent resources (with generic error pages), redirect all invalid requests to a default page (`302`), or use custom status codes. 

## Wordlists

### Generic wordlists

- Some good generic wordlists to start with ([`SecLists/Discovery/Web-Content`](https://github.com/danielmiessler/SecLists/tree/master/Discovery/Web-Content)):
	- [`Discovery/Web-Content/common.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/common.txt) (~4.7K entries): a good general-purpose wordlist with a broad range of common directory and file names; excellent starting point for fuzzing.
	- [`Discovery/Web-Content/raft-small-directories.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/raft-small-directories.txt) (~20K entries): another good choice for initial enumeration; focuses on directories.
	- [`Discovery/Web-Content/DirBuster-2007_directory-list-2.3-medium.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/DirBuster-2007_directory-list-2.3-medium.txt) (~87K entries): a more extensive wordlist specifically focused on directory names.
	- [`Discovery/Web-Content/big.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/big.txt) (~20K entries): a large collection of common directory and file names.
	- [`Discovery/Web-Content/raft-large-directories.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/raft-large-directories.txt) (~62K entries): a massive collection of directory names compiled from various sources; suitable for more thorough investigation.

>[!tip] On a Kali Linux or Parrot machine, SecLists comes preinstalled. It's usually located in `/usr/share/wordlists/seclists` or `/usr/share/wordlists/SecLists`. 
>- To find the exact location, run:
>```bash
>sudo find / -name "SecLists" -type -d 2>/dev/null
>```

- Beyond `SecLists`, utilize dynamically updated lists like those provided by **Assetnote** (e.g., `httparchive_php_2024.txt`, `swagger-apis.txt`). These are generated from global internet scans and contain paths that are actually in use today.
### Generating custom wordlists

- `common.txt` is needed anyway, but for maximum effectiveness, **generate custom contextual wordlists** and run fuzzing again on top of what you already have.

- [`CeWL`](https://github.com/digininja/CeWL) spiders a target website and creates a custom wordlist based on the text found on the pages:

```bash
cewl -d 2 -m 5 -w custom-words.txt https://example.com
```

>[!tip] Find technology-specific wordlists at [`SecLists/Discovery/Web-Content`](https://github.com/danielmiessler/SecLists/tree/master/Discovery/Web-Content).