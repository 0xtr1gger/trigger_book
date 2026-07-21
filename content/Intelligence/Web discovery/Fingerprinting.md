---
created: 2026-07-18
tags:
  - recon
  - web_hacking
status: substantial
---
## Fingerprinting

>**Fingerprinting** refers to the process of identifying technologies used by the target web application, including programming languages, frameworks, and infrastructure components.

>[!note]- Why fingerprinting is important
> 
> - **Attack surface prioritization**
> 	- Knowing the technology stack allows you to focus on vulnerabilities relevant to the target.
> - **Known CVEs**
> 	- Once you have the name of a technology in use and a version number, you can search for known vulnerabilities. 
> - **Search for common misconfigurations**
> 	- Identify and test for insecure defaults specific to the technologies you've found.
> - **Reporting**
> 	- Accurately point to the root source of vulnerabilities in reports. 
### Fingerprinting objectives 

- **Web server software and version** (Apache, Nginx, IIS).
- **Backend programming language** (PHP, Python, Java, Ruby, Node.js, .NET, Go).
- **Web framework and libraries** (Django, Laravel, Spring, Express, Rails, Struts).
- **Content Management System (CMS)** (WordPress, Joomla, Drupal, Magento).
- **APIs** (REST, GraphQL, SOAP, gRPC).
- **Database Management System (DBMS)** (MySQL, PostgreSQL, MSSQL, Oracle, MongoDB).
- **Caching layer** (Varnish, Redis, Memcached).
- **Reverse proxies and load-balancers** (HAProxy, Nginx, F5 BIG-IP, Envoy).
- **CDNs** (Cloudflare, Akamai, AWS CloudFront, Fastly).
- **WAFs** (Cloudflare WAF, AWS WAF, Imperva, ModSecurity).
- **TLS/SSL configuration**: protocol versions, cipher suites, and certificate metadata.
- **Third-party integrations**: **OAuth and SSO providers** (Google, Okta, Auth0), **Payment services** (Stripe, PayPal, Square), **Analytics** (Google Analytics, Segment).
- **Operating System** (Windows, Linux + kernel version, FreeBSD).
## Automated tools

- Automated tools are the fastest way to get a baseline understanding of the target's stack.
- Common ones include:
	- [`Wappalyzer`](https://www.wappalyzer.com/)
		- A browser extension and online service for website technology profiling; can identify a wide range of web technologies, including CMSs, frameworks, analytics tools, and more.
	- [`BuiltWith`](http://builtwith.com/) 
		- An online service that profiles websites and identifies technologies including hosting providers, CMS, analytics, JavaScript libraries, and advertising networks.
	- [`WhatWeb`](https://github.com/urbanadventurer/WhatWeb)
		- Uses a vast database of signatures to identify various web technologies such as CMS, frameworks, server software, JavaScript libraries, and more; excels at both passive reconnaissance (stealthy, single-request scanning) and aggressive active testing.
### `WhatWeb`

#### Basic commands

>[!note] For more, see [`urbanadventurer/WhatWeb — GitHub`](https://github.com/urbanadventurer/WhatWeb).

- Scan a single website:

```bash
whatweb https://example.com
```

- Scan multiple websites:

```bash
whatweb example.com example.org
```

- Scan targets from a file:

```bash
whatweb -i targets.txt
```

```bash
cat targets.txt | whatweb -i /dev/stdin
```

- Scan an IP address range:

```bash
whatweb 192.168.1.1-192.168.1.254
```

```bash
whatweb 10.0.0.0/24
```

- Force HTTPS:

```bash
whatweb --url-prefix https:// 10.10.10.0/24
```

- Aggression levels — control how many HTTP requests `WhatWeb` sends:

```bash
whatweb -a 1 example.com
```

| Level | Description                                   |
| ----- | --------------------------------------------- |
| `1`   | Stealthy (default) — one request.             |
| `3`   | Aggressive — additional requests when needed. |
| `4`   | Heavy — aggressive tests on all targets.      |

- Specify a proxy (e.g., Burp Suite):

```bash
whatweb --proxy 127.0.0.1:8080 example.com
```

```bash
whatweb --proxy 127.0.0.1:8080 --proxy-user user:pass example.com
```
#### Customizing HTTP requests

- Custom `User-Agent`:

```bash
whatweb -U "Mozilla/5.0" example.com
```

- Add HTTP headers:

```bash
whatweb -H "Authorization: Bearer TOKEN" example.com
```

```bash
whatweb -H "X-Forwarded-For: 127.0.0.1" example.com
```

- Handling redirects:

```bash
--follow-redirect=never
--follow-redirect=http-only
--follow-redirect=meta-only
--follow-redirect=same-site
--follow-redirect=always
```

- HTTP Basic Authentication:

```bash
whatweb -u admin:password example.com
```

- Cookies:

```bash
whatweb -c "session=abc123" example.com
```

- Load cookies from a file:

```bash
whatweb --cookiejar cookies.txt example.com
```
#### Plugins

- `WhatWeb` has over 1800 plugins, each used to detect something different.
- List all plugins:

```bash
whatweb -l 
```

- Search for a specific plugin:

```bash
whatweb --search-plugins wordpress
```

- Get detailed plugin information:

```bash
whatweb -I wordpress
```

- Only run selected plugins:

```bash
whatweb -p wordpress,apache
```

- Exclude specific plugins:

```bash
whatweb -p -md5,-title
```

- Load a custom plugin (written in Ruby):

```bash
whatweb -p +/custom-plugins/plugin.rb
```

- Add custom plugin directory:

```bash
whatweb -p +./custom-plugins/
```

#### Searching page content

- Search for a string/regex:

```bash
whatweb --grep "Powered by"
```

```bash
whatweb --grep "/wp-content/"
```

#### Options cheat sheet

| Option               | Description                                         |
| -------------------- | --------------------------------------------------- |
| `-a`, `--aggression` | Set aggression level (`1`, `3`, `4`).               |
| `-i`, `--input-file` | Read targets from a file or stdin.                  |
| `--proxy`            | Route requests through an HTTP proxy.               |
| `-g`, `--grep`       | Display only matching results.                      |
| `--dorks`            | Show Google dorks for a plugin.                     |
| `-v`, `--verbose`    | Verbose output with plugin descriptions.            |
| `-q`, `--quiet`      | Suppress progress messages.                         |
| `--no-errors`        | Hide error messages.                                |
| `--color`            | Control colored output (`auto`, `always`, `never`). |
| `--short-help`       | Display condensed help.                             |
| `-h`, `--help`       | Display full help.                                  |
| `--debug`            | Raise plugin exceptions for debugging.              |
| `--version`          | Show WhatWeb version information.                   |

- Customizing HTTP requests:

| Option                       | Description                                                                 |
| ---------------------------- | --------------------------------------------------------------------------- |
| `-U`, `--user-agent`         | Specify a custom User-Agent.                                                |
| `-H`, `--header`             | Add, replace, or remove an HTTP header.                                     |
| `--url-prefix`               | Prepend a string (e.g. `https://`) to every target.                         |
| `--url-suffix`               | Append a path to every target.                                              |
| `--url-pattern`              | Insert targets into a URL using `%insert%`.                                 |
| `-u`, `--user=user:password` | HTTP Basic Authentication credentials.                                      |
| `-c`, `--cookie`             | Supply initial cookies.                                                     |
| `--cookiejar`                | Load cookies from a file.                                                   |
| `--no-cookies`               | Disable automatic cookie handling.                                          |
| `--follow-redirect`          | Redirect policy (`never`, `http-only`, `meta-only`, `same-site`, `always`). |
| `--max-redirects`            | Maximum redirect chain length.                                              |

- Plugins:

| Option                          | Description                                     |
| ------------------------------- | ----------------------------------------------- |
| `--proxy-user=user:password`    | Authenticate to the proxy.                      |
| `-l`, `--list-plugins`          | List all available plugins.                     |
| `-I`, `--info-plugins[=search]` | Show detailed plugin information.               |
| `--search-plugins`              | Search plugins by keyword.                      |
| `-p`, `--plugins`               | Enable or disable selected plugins/directories. |
| `--custom-plugin`               | Define an ad hoc detection plugin.              |

- Threads, delay, and timeout:

| Option                | Description                                        |
| --------------------- | -------------------------------------------------- |
| `-t`, `--max-threads` | Maximum concurrent threads.                        |
| `--open-timeout`      | Connection timeout.                                |
| `--read-timeout`      | Read timeout.                                      |
| `--wait`              | Delay between connections (single-threaded scans). |

- Logs:

| Option                   | Description                     |
| ------------------------ | ------------------------------- |
| `--log-brief`            | Save one-line output.           |
| `--log-verbose`          | Save verbose output.            |
| `--log-errors`           | Save errors to a log file.      |
| `--log-json`             | Export results as JSON.         |
| `--log-json-verbose`     | Export verbose JSON.            |
| `--log-xml`              | Export XML.                     |
| `--log-magictree`        | Export MagicTree XML.           |
| `--log-object`           | Export Ruby object format.      |
| `--log-sql`              | Export SQL INSERT statements.   |
| `--log-sql-create`       | Generate SQL table definitions. |
| `--log-mongo-database`   | MongoDB database name.          |
| `--log-mongo-collection` | MongoDB collection name.        |
| `--log-mongo-host`       | MongoDB server.                 |
| `--log-mongo-username`   | MongoDB username.               |
| `--log-mongo-password`   | MongoDB password.               |
| `--log-elastic-index`    | Elasticsearch index name.       |
| `--log-elastic-host`     | Elasticsearch HTTP endpoint.    |

### HTTPX for fingerprinting at scale

- Live check + technology detection, server info, CDN detection:

```bash
cat subdomains.txt | httpx -silent -sc -title -td -web-server -cdn -o enriched.txt
```

- Group similar applications across the attack surface using JARM and favicon hashes:

```bash
httpx -l hosts.txt -jarm -favicon -json | jq -r '.[] | "\(.jarm) \(.favicon) \(.url)"' | sort -u
```

- Use custom Wappalyzer-style fingerprints:

```bash
httpx -l live.txt -td -cff custom_fingerprints.yaml -title -server -json -o tech.json
```

>[!note] For more about HTTPX, see [[Mapping the attack surface#HTTPX]].

## Detecting WAFs

> [`wafw00f`](https://github.com/EnableSecurity/wafw00f) is a command-line tool specifically designed for identifying WAFs protecting target applications.

>[!note]+ Installation
>```bash
>pip3 install git+https://github.com/EnableSecurity/wafw00f
>```

- `wafw00f` can identify over 200 firewalls. List all of them:

```bash
wafw00f -l
```

>[!tip] Run `wafw00f` early in reconnaissance before attempting any vulnerability testing to avoid triggering blocks or IP bans.

>[!interesting]+ How `wafw00f` works
> - `wafw00f` uses a progressively aggressive methodology:
> 	1. Sends a normal HTTP `GET` request and analysis response headers, cookies, and behavioral patterns that can reveal WAF signatures.
> 	2. If unsuccessful, sends a series of potentially malicious or malformed HTTP requests designed to trigger WAF-specific error messages, blocking behavior, or any distinctive response patterns.
> 	3. If this fails, it uses heuristic algorithms to analyze response timing and any anomalous behavior that indicates the presence of a WAF.

- Basic scan:

```bash
wafw00f https://example.com
```

- Verbose output:

```bash
wafw00f -v https://example.com
```

- Test all possible WAFs even after finding one:

```bash
wafw00f -a https://example.com
```

- Test specific URL path:

```bash
wafw00f https://example.com/admin/login.php
```

>[!tip] Different URL paths may be protected differently; test multiple endpoints (login pages, API endpoints, admin panels). The same goes for different HTTP methods.

>[!tip]
>There is an amazing GitHub repository, [`Awesome-WAF`](https://github.com/0xInfection/Awesome-WAF) that contains a wealth of useful information about web application firewalls. Once a firewall is identified, it is a good place to start searching for known bypasses. 

>[!note] To read more about WAFs, see [`WAF through the eyes of hackers — barracud4, Habr`](https://habr.com/en/companies/dsec/articles/454592/).

## Infrastructure and OS fingerprinting

### Nmap service & version detection

- Nmap maintains a library of probes in the `nmap-service-probes` file. It sends protocol-specific messages (HTTP `GET`, SSL/TLS handshake, etc.) designed to elicit a unique response, then matches it against a vast set of regular expressions to identify the service, application name, and version number.
- Enable service/version detection:

```bash
nmap -sV <target>
```

- Ensure every single probe is attempted (Intensive, slower):

```bash
nmap -sV --version-all <target>
```

- Don't exclude any ports from version detection:

```bash
nmap -sV --allports <target>
```

>[!note] See [[Nmap version detection]].
### Nmap OS Detection

- Nmap uses **TCP/IP stack fingerprinting** for remote OS detection. It sends a series of specific TCP and UDP packets (e.g., TCP ISN sampling, initial window size checks) and compares the responses against its internal `nmap-os-db`.
- Enable OS detection:

```bash
nmap -O <target>
```

- Aggressive scan (OS, version detection, scripts, traceroute):

```bash
nmap -A <target>
```

> [!important] For reliable OS detection, Nmap needs to find at least **one open** and **one closed** port on the target. Take OS versions with a grain of salt if virtualization or load balancers are in place.

## Manual fingerprinting techniques

- When automated tools fail (often due to obfuscation, WAFs, or custom applications), manual techniques become necessary.

### Banner grabbing

>**Banner grabbing** is a technique used to collect information about network services running on the target by capturing **software banners** — usually textual information sent by services upon connection.

- Fetch headers only:

```bash
curl -I https://example.com 
```

```bash
curl --head https://example.com
```

```bash
curl -X HEAD https://example.com
```

| Option         | Description                 |
| -------------- | --------------------------- |
| `-I`, `--head` | Show only HTTP headers.     |
| `-X`           | Specify HTTP method to use. |
| `-v`           | Verbose mode.               |
- Use Netcat for raw interaction:

```bash
nc -nv example.com 80
```
```http
GET / HTTP/1.1
Host: example.com
```

- Nmap:

```bash
nmap -sV --script=banner -p 80,443 example.com
```

Pay special attention to:

- **Server Headers**: Directly reveal web server name and/or version (`Server: Apache/2.4.41`).
- **Non-Standard/Custom Headers**: Often disclose backend frameworks or languages.
	- `X-Powered-By: Express`
	- `X-Powered-By: PHP/7.4.3`
	- `X-AspNet-Version: 4.0.30319`
- **Vendor-Specific Headers**: Reveal CDNs, Proxies, or WAFs.
	- [`Cf-Ray`](https://developers.cloudflare.com/fundamentals/reference/http-headers/#cf-ray), [`Cf-Worker`](https://developers.cloudflare.com/fundamentals/reference/http-headers/#cf-worker) (Cloudflare)
	- `X-Amz-Cf-Id` (AWS CloudFront)
- **Header Order**: While less common today, the specific ordering of HTTP headers can sometimes distinguish between Apache, Nginx, or Lighttpd.

>[!note]- Even the order of HTTP headers may be revealing
> 
> Sometimes you can make an educated guess on what web server or proxy is in use based on the order of HTTP headers in responses. But it becomes less and less common, since responses are slowly becoming pretty standardized. 
> 
> | Apache                                                                                                                   | Nginx                                                                                                                    | lighttpd                                                                                                                 |
| ------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| `Date`<br>`Server`<br>`Last-Modified`<br>`ETag`<br>`Accept-Ranges`<br>`Content-Length`<br>`Connection`<br>`Content-Type` | `Server`<br>`Date`<br>`Content-Type`<br>`Content-Length`<br>`Last-Modified`<br>`Connection`<br>`ETag`<br>`Accept-Ranges` | `Content-Type`<br>`Accept-Ranges`<br>`ETag`<br>`Last-Modified`<br>`Content-Length`<br>`Connection`<br>`Date`<br>`Server` |
### Cookies and session tokens

- Cookie names often indicate the underlying technology:
	- `PHPSESSID` -> PHP
	- `JSESSIONID` -> Java
	- `ASP.NET_SessionId` -> .NET
	- `wordpress_logged_in_*` -> WordPress
	- `rack.session` -> Ruby on Rails

### Source Code Analysis (HTML, JS, CSS)

Analyzing static content often reveals what the application is built on.

- **HTML meta tags & comments**:

```html
<meta name="generator" content="WordPress 5.8.1">
<!-- Built with React 18.2.0 -->
<!-- Powered by Laravel Framework -->
```

- **JavaScript Analysis**:
    - Look for framework-specific variables: `ng-app` (Angular), JSX syntax (React), `v-` directives (Vue).
    - API endpoints: AJAX calls can reveal backend structure (`/api/users/?format=json` indicates Django REST framework).
    - Use tools like [`LinkFinder`](https://github.com/GerbenJavado/LinkFinder) or [`SecretFinder`](https://github.com/m4ll0k/SecretFinder) to parse JS files for hidden endpoints.
- **CSS Files**: Comments or specific class naming conventions (e.g., `tailwind`, `bootstrap`).

### File and directory naming conventions

- Directory and file naming conventions often reveal the technology that powers the application.

- Common file extensions:
	- **PHP**: `.php`, `.php3`, `.php4`, `.php5`, `.phtml`
	- **ASP/ASP.NET**: `.asp`, `.aspx`, `.ashx`, `.asmx`, `.axd`
	- **Java**: `.jsp`, `.jsf`, `.jspx`, `.do`, `.action`
	- **Python**: `.py`, `.pyc`, `.pyo`
	- **Ruby**: `.rb`, `.rhtml`, `.erb`
	- **ColdFusion**: `.cfm`, `.cfc`, `.cfml`
	- **Perl**: `.pl`, `.cgi`

>[!note] See [`Web Files — FileInfo.com`](https://fileinfo.com/filetypes/web).

- CMSs:

```PowerShell
# WordPress
/wp-content/
/wp-admin/
/wp-includes/
/wp-config.php
/xmlrpc.php

# Joomla
/templates/
/configuration.php
/index.php?option=com_
/administrator/
/components/
/modules/

# Drupal
/sites/default/
/sites/all/themes/
/modules/
/core/
/update.php

# Magento
/app/
/skin/
/var/
/media/
```

- Frameworks:

```PowerShell
# Java (Servlet/JSP)
/WEB-INF/
/META-INF/
*.jsp
*.do

# Django (Python)
/static/
/media/
/admin/
*.py

# Laravel (PHP)
/vendor/
/storage/
/public/
/resources/
artisan

# Ruby on Rails
/app/
/config/
/public/
/vendor/
Gemfile

# ASP.NET
/bin/
/App_Data/
/App_Code/
web.config
*.aspx
*.ashx

# Node.js/Express
/node_modules/
/public/
/views/
package.json
```

### Provoking errors for verbose responses

- Intentionally causing application errors can force the server to leak stack traces and reveal additional technical details.

- Methods for invoking errors:
	- Request non-existent resources (will likely result in `4xx` errors).
	- Alter request parameters (`GET` parameters in query strings, `POST` parameters in request body, etc.).
	- Manipulate HTTP headers.
	- Add unexpected characters, such as `[`, `[[`, `]]`, etc. in headers, cookie names, and parameters to disrupt the code that handles these values:

```bash
# array notation in unexpected places
curl "https://example.com/page?param[]=value"
curl "https://example.com/page?param[test][nested]=value"

# brackets in cookies
curl -H "Cookie: session=abc123[[]]xyz" https://example.com
```

- Use arbitrary HTTP verbs

```bash
# standard bur often restricted methods
curl -X PUT https://example.com 
curl -X DELETE https://example.com/resource 
curl -X PATCH https://example.com/resource 
curl -X OPTIONS https://example.com

# WebDAV methods
curl -X COPY https://example.com
curl -X MOVE https://example.com
curl -X MKCOL https://example.com
curl -X PROPFIND https://example.com

# arbitrary/malformed methods
curl -X NIGHT https://example.com
curl -X RAIN https://example.com
curl -X "" https://example.com
curl -X " " https://example.com
```

- Exceed server limits
	- Send requests that exceed server limits, such as payload size.

```bash
# large payload
curl -X POST -d "data=$(python3 -c 'print("A"*10000000)')" https://example.com

# many requests rapidly
for i in {1..1000}; do curl https://example.com & done

# long URL
curl "https://example.com/?param=$(python3 -c 'print("A"*10000)')"
```

What to look for in error messages:

- Stack traces

```bash
Traceback (most recent call last):
  File "/app/views.py", line 42, in index
    user = User.objects.get(id=request.GET['id'])
django.core.exceptions.ObjectDoesNotExist: User matching query does not exist.
```

- Framework-specific errors

```bash
# Laravel (PHP)
Whoops, looks like something went wrong.
1/1 ErrorException in Filesystem.php line 81:

# Django (Python)  
OperationalError at /admin/
no such table: auth_user

# ASP.NET
Server Error in '/' Application.
Description: An unhandled exception occurred during the execution of the current web request.
```

- Database errors:

```bash
# MySQL
You have an error in your SQL syntax near '' at line 1

# PostgreSQL
ERROR:  relation "users" does not exist
LINE 1: SELECT * FROM users WHERE id = 

# MSSQL
Unclosed quotation mark after the character string
```

## References and further reading

- [`Recon Series #3: HTTP fingerprinting — sleuthing for a web application's hidden vulnerabilities — YesWeHack`](https://www.yeswehack.com/learn-bug-bounty/recon-series-http-fingerprinting)
- [`0xInfection/Awesome-WAF — GitHub`](https://github.com/0xInfection/Awesome-WAF)
- [`Service and Version Detection — Nmap`](https://nmap.org/book/man-version-detection.html)
- [`Netcraft Site Reports`](https://sitereport.netcraft.com/)