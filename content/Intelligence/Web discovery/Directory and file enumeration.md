---
created: 2026-07-18
updated: 2026-09-30
tags:
  - web_hacking
  - intel
proofread: yes
---
## Directory and file enumeration

- Before beginning enumeration, assess:
	- **What kind of application is this?** SPA, CMS, legacy MVC, or something else?
	- **What is the technology stack behind the application?** Programming language, framework, web server, OS?
	- **Are there authorization boundaries?** Can you authenticate as a low-privileged user to access more routes?
	- **Is there a WAF?** Will aggressive fuzzing lead to rate-limiting or an IP address ban?

>[!tip]+
>- Check for WAFs and identify the application stack before starting automated enumeration. See [[Fingerprinting]].

>[!note]+ Directory and file enumeration can reveal:
> - **Sensitive data**: backup files, configuration files, credentials, and API keys.
> - **Development resources**: test/staging environments, administrative panels, and internal documentation (e.g., Swagger UI docs).
> - **Outdated content**: older, still-active versions of APIs (`/v1/` vs. `/v2/`), and components with known vulnerabilities.
> - **Source code exposure**: `.git/`, `.svn/`, `.DS_Store`.

>[!note] See [[🛠️ Sensitive information disclosure in web content]].

>[!tip] Inspect files such as `robots.txt` and `sitemap.xml`, as well as resources in the `/.well-known/` directory. They may provide an initial overview of the application to guide crawling and fuzzing. See [[robots.txt and other interesting files]].

## Web crawling (spidering)

> **Web crawling** is the automated process of systematically browsing and indexing web pages by following hyperlinks to discover all reachable content.

- Web crawlers mimic human navigation patterns to build an initial map of the target application. Modern crawlers handle session management, render client-side JavaScript using headless browsers, and enforce crawling scope.

> [!warning] Web crawlers can only enumerate directories and files that are already referenced somewhere in the application. Hidden, unlinked pages will remain undetected.

>[!note] See [[🛠️ Searching the web]] and [[How search engines work]].

- Common web crawlers:
	- **Burp Spider** (Burp Suite Professional)
	- **OWASP ZAP Spider**
	- [`hakrawler`](https://github.com/hakluke/hakrawler)
	- [`Photon`](https://github.com/s0md3v/Photon)
	- [`katana`](https://github.com/projectdiscovery/katana)
	- [`crawlergo`](https://github.com/Qianlitp/crawlergo)
	- [`dirhunt`](https://github.com/Nekmo/dirhunt)
	- [`gospider`](https://github.com/jaeles-project/gospider)

```bash
cat urls.txt | hakrawler
```

>[!example]- `hakrawler` example
>
>```bash
> cat urls.txt | hakrawler
> ```
>
> ![[hakrawler_gin&juice.png]]

```bash
python ./photon.py -u https://ginandjuice.shop --level 2 --verbose
```

>[!example]- `photon` example
> ```bash
> python ./photon.py -u https://ginandjuice.shop --level 2 --verbose
> ```
> 
> ![[Photon_gin&juice.shop.png]]

```bash
katana -u https://ginandjuice.shop
```

>[!example]- `katana` example
>
> ```bash
> katana -u https://ginandjuice.shop
> ```
>![[katana_hin&juice.shop.png]]

>[!note] [`Gin&Juice`](https://ginandjuice.shop/) is a website created by PortSwigger for testing automated web tools such as crawlers and fuzzers.

- Dynamic, JavaScript-driven content often defeats automated crawlers; it is better explored manually.

>[!warning] Without a valid authenticated session, a crawler will miss any content behind a login.

## Active enumeration (fuzzing)

- Fuzzing is one of the most effective ways to enumerate directories and files that are not directly linked to other pages in a web application. Fuzzing systematically probes paths and filenames from a wordlist and analyzes server responses to identify accessible resources.
- Start with a small, general-purpose wordlist such as `common.txt`, proceed to a larger list like `directory-list-2.3-medium.txt`, and generate a custom wordlist from target application content (for example, using `CeWL`) for a targeted pass.

>[!note] See [[Wordlists for web enumeration]].

- Common tools:
	- [`ffuf`](https://github.com/ffuf/ffuf) (Fuzz Faster U Fool) — Fast and flexible web fuzzer written in Go.
	- [`gobuster`](https://github.com/OJ/gobuster) — Versatile brute-force tool for various enumeration tasks.
	- [`wfuzz`](https://github.com/xmendez/wfuzz) — Flexible Python-based web application fuzzer.
	- [`feroxbuster`](https://github.com/epi052/feroxbuster) — Fast, recursive content discovery tool written in Rust.
	- [`dirsearch`](https://github.com/maurosoria/dirsearch) — Feature-rich command-line tool for directory and file enumeration.

>[!note] Most examples in this guide use `ffuf`. See [[🛠️ ffuf]] for its full flag reference.

- Basic directory and file enumeration:

```bash
ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -u https://example.com/FUZZ -c -ic
```

> [!tip] The `-ic` flag ignores comments in wordlists.

> [!example]-
> 
> ```bash
> ffuf -w ./directory-list-2.3-small.txt:FUZZ -u https://example.com/FUZZ -c -ic
> ```
> 
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

>[!note] See [[🛠️ ffuf]].

```bash
gobuster dir -u https://example.com -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -x php,html,txt
```

```bash
feroxbuster -u https://example.com -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -x php,html -d 3
```

>[!info] `feroxbuster` recurses by default.
### Analyzing responses

- Typical status code meanings in enumeration contexts:
	- **`200 OK`**: Resource exists and is accessible; likely a valid discovery.
	- **`301 Moved Permanently`, `302 Found`, `307 Temporary Redirect`**: Resource exists but redirects to another location; analyze redirect targets. Redirects to login or registration pages may indicate the need for authentication or authorization.
	- **`401 Unauthorized`**: Resource exists but requires authentication; a potential target for credential attacks.
	- **`403 Forbidden`**: Resource exists but access is denied due to authorization rules. Worth retrying with 403-bypass techniques—path variations (`/admin/`, `/./admin`, `/%2e/admin`, trailing dot or slash), alternative HTTP methods, and headers such as `X-Original-URL` or `X-Forwarded-For`.
	- **`404 Not Found`**: Resource likely doesn't exist, though custom error pages may use `404` deceptively.
	- **`500 Internal Server Error`**: Server-side error; potentially indicates vulnerable code or misconfigurations; a good target for more thorough investigation.

>[!warning] Many modern applications implement custom error handling that complicates response analysis. Applications may return `200` status codes for non-existent resources (with generic error pages), redirect all invalid requests to a default page (`302`), or use custom status codes.

- Custom error pages often return a consistent response size. Once identified, filter out the constant response size (e.g., `4242` bytes):

```bash
ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -u https://example.com/FUZZ -c -ic -fs 4242
```

- Alternatively, automatically calibrate and filter baseline responses using `-ac`:

```bash
ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -u https://example.com/FUZZ -c -ic -ac
```

>[!note] See [[🛠️ ffuf]] for the full set of matchers and filters (`-mc`, `-fc`, `-fs`, `-fw`, `-fl`, `-mr`).

### Rate-limiting

- To avoid triggering rate limits or IP address bans, throttle requests or introduce a delay between them.

>[!note] A series of `429 Too Many Requests` or `403 Forbidden` responses following successful requests usually indicates automated rate limiting or an active IP ban.

- Impose a delay between requests:

```bash
ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -u https://example.com/FUZZ -c -ic -p 0.8
```

- Limit requests per second:

```bash
ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -u https://example.com/FUZZ -c -ic -rate 10
```

| Option | Description |
| :--- | :--- |
| `-p` | Set the delay between requests in seconds. |
| `-rate` | Set the maximum number of requests per second (default `0`). |
### Fuzzing file extensions

- Certain files—or alternate formats of existing resources—are only discoverable by explicitly appending file extensions to requests. Extension fuzzing automates this process.

>[!note] To save time and reduce request volume, test extensions relevant to the identified technology stack rather than fuzzing indiscriminately.

- Use the `-e` flag to specify a comma-separated list of extensions to append to each wordlist entry:

```bash
ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -u https://example.com/FUZZ -e .php,.html,.bak -c -ic
```

>[!warning]+ The `-e` option only works with the `FUZZ` keyword.

- Alternatively, fuzz using two separate wordlists—one for base filenames and another for extensions:

```bash
ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt:FILE -w /usr/share/wordlists/seclists/Fuzzing/extensions-most-common.fuzz.txt:EXT -u https://example.com/FILE.EXT -c -ic
```

- Common extension lists in [`SecLists`](https://github.com/danielmiessler/SecLists):
	- [`Discovery/Web-Content/web-extensions.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/web-extensions.txt) (39 entries)
	- [`Fuzzing/extensions-most-common.fuzz.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/extensions-most-common.fuzz.txt) (30 entries, for quick enumeration)

>[!tip]
>If wordlist entries include leading dots, remove them using `sed`:
>```bash
>cat ./web-extensions.txt | sed 's/^\.//' > ./web-extensions-no-dot.txt
>```

### Recursive fuzzing

- Use recursive fuzzing to discover nested subdirectories. When a valid directory is discovered, the tool automatically spawns a new fuzzing job targeting that path.

```bash
ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/directory-list-2.3-small.txt -u http://example.com/FUZZ -recursion -recursion-depth 3 -e .php,.html,.bak -ic -c
```

>[!warning] Recursion multiplies request volume rapidly: combining a medium wordlist with multiple extensions at a recursion depth of 3 can generate millions of requests. Start with a small wordlist and shallow depth, then recurse selectively into relevant directories. Combine recursion with rate controls to avoid detection and IP bans.

>[!note] See [[🛠️ ffuf]] for recursion options (`-recursion`, `-recursion-depth`, `-recursion-strategy`).

### Authenticated enumeration

- Significant portions of an application's attack surface are accessible only after authentication. When valid credentials are available, repeat enumeration within an authenticated session to discover protected routes.
- Pass session cookies with `-b` or custom authorization headers with `-H`:

```bash
ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -u https://example.com/FUZZ -b "session=<cookie>" -c -ic
```

- When testing applications with role-based access control, enumerate endpoints under each role (e.g., standard user vs. administrator). Discrepancies in accessible routes often indicate broken access control vulnerabilities.

>[!tip] Proxy fuzzing traffic through Burp Suite using `-x http://127.0.0.1:8080` to reuse active sessions and log all requests in the proxy history for subsequent testing.

## Extracting endpoints from JavaScript

- Single-Page Applications (SPAs) define most routes and API endpoints client-side within JavaScript files. Crawlers that do not execute JavaScript miss these endpoints, requiring direct analysis of JavaScript files.
- Crawl the target and extract endpoints from linked JavaScript files:

```bash
katana -u https://example.com -jc -o urls.txt
```

- Analyze JavaScript files and extract relative endpoints:

```bash
python3 linkfinder.py -i https://example.com -d -o cli
```

- Useful tools:
	- [`LinkFinder`](https://github.com/GerbenJavado/LinkFinder) — Extract endpoints from JavaScript files.
	- [`SecretFinder`](https://github.com/m4ll0k/SecretFinder) — Search JavaScript files for API keys, tokens, and credentials.
	- [`getJS`](https://github.com/003random/getJS) — Extract and download JavaScript files referenced by a page.

>[!tip] Check for exposed source maps (`.js.map`). They allow reconstructing original, unminified source code, including developer comments and internal routes.

>[!tip] If enumeration exposes a version control directory (`/.git/`, `/.svn/`) or a `.DS_Store` file, treat it as source code disclosure: reconstruct the repository or directory listing to recover source files, commit history, and internal paths. Tools such as `git-dumper` automate rebuilding `.git/` repositories from exposed directories.

## Next steps

- Content discovery informs subsequent assessment phases. After mapping directories, files, and endpoints:
	- Test discovered parameters and inputs for injection and logic flaws — see [[Fuzzing parameters]].
	- Probe discovered APIs and their definitions (Swagger/OpenAPI) — see [[API testing]].
	- Feed newly found hostnames and virtual hosts back into [[Subdomain enumeration]] and [[Virtual host enumeration]].
	- Prioritize high-value findings—such as administrative interfaces, file upload endpoints, exposed source code, and `500` errors—for in-depth vulnerability testing.
