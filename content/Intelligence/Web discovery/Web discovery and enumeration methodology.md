---
created: 2026-09-27
updated: 2026-10-02
tags:
  - intel
  - methodology
status: complete
proofread: no
---

## Web discovery and enumeration

- Once you've discovered a web application, gather as much information as you can: identify its technology stack, discover available functionality, enumerate endpoints and parameters, and identify the attack surface — everything the application exposes or accepts, including functionality it doesn't directly advertise.

>[!tip]+ 
>- Enumeration is iterative. Repeat the earlier steps with new findings.

>[!tip]+
>- If possible, enumerate the application with different access levels: anonymous, low-privileged user, administrator. Having authenticated, you may be able to identify routes and parameters that were invisible before login.

>[!note] For discovering *which* web applications exist across the target's infrastructure — hosts, ports, subdomains, and virtual hosts — see [[🛠️ Information gathering methodology]].

## Initial fingerprinting

>[!note] See [[Fingerprinting]].

![[Fingerprinting#Fingerprinting objectives]]

## Interesting files

>[!note] See [[robots.txt and other interesting files]].

- Check known files that may reveal the application's structure and other details useful during testing, such as `robots.txt`, `sitemap.xml`, `security.txt`, and files in `/.well-known/`.

```bash
curl -s https://example.com/robots.txt
```

```bash
curl -s https://example.com/sitemap.xml
```

## Mapping the application

- The first step in approaching a web application is to create its **complete map**: enumerating all accessible directories and files, walking through available functionality, and gathering as much information about the potential attack surface as possible.
- Common techniques for mapping a web application:
	- [[#Walking through the application manually]] with a web proxy, recording all requests and responses.
	- [[#Historical data]]
	- [[#Directory and file enumeration]]
		- Web crawling
		- Fuzzing
		- Scanning JS
- Combining these gives broader coverage than any single method.

### Walking through the application manually

- Before any automation, browse the whole application through an intercepting proxy — **Burp Suite** or **OWASP ZAP** — as a normal user. Click every link, button, and menu item, and go through the entire user journey: registration, login, password reset, profile update, and every other feature. This populates the proxy history and reveals the application's functionality, user roles, and naming conventions.
- This manual mapping step is what further enumeration will be based on.

> [!tip] Many modern web applications, such as SPAs built on React or Angular, render content on the client side. Interact with the JavaScript on the page to trigger API calls and reveal endpoints that tools will miss.

### Historical data

- Web archives and URL datasets keep the URLs that an application exposed in the past. They can reveal endpoints that still respond but are no longer referenced from the main application.
- Collect the archived URLs of the target:

```bash
waymore -i example.com -mode U --stream | sort -u > urls.txt
```

```bash
gau example.com > urls.txt
```

>[!note] See [[🛠️ Searching the web#Searching web archives]] for archive sources, query syntax, and other tools.

- Verify which of the collected URLs are still live:

```bash
httpx -l urls.txt -mc 200,204,301,302,307,401,403 -silent -o live.txt
```

```bash
while read -r url; do curl -s -o /dev/null -w "%{http_code} %{url_effective}\n" "$url"; done < urls.txt
```

### Directory and file enumeration

>[!note] See [[Directory and file enumeration]].

- Brute-force unlinked directories and files from a wordlist:

```bash
ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt -u https://example.com/FUZZ -c -ic
```

- Extract endpoints and secrets from the application's JavaScript. For a single-page application, the JS bundles expose most of the attack surface. See [[Directory and file enumeration#Extracting endpoints from JavaScript]].

## Fuzzing parameters

>[!note] See [[Fuzzing parameters]].

- Discover hidden parameters — URL query parameters, HTTP body parameters, headers, cookies — that the application accepts but does not expose in the UI:

```bash
ffuf -u "https://example.com/page?FUZZ=x" -w /usr/share/wordlists/seclists/Discovery/Web-Content/burp-parameter-names.txt -ac -c
```

```bash
arjun -u https://example.com/api
```
## Where to go next

- If a known off-the-shelf application or CMS is discovered, it likely has a well-documented attack surface -> See [[Web application security testing methodology#Attacking common applications]].
- APIs often expose an additional, separate attack surface -> See [[API testing]] and [[GraphQL attacks]].
- With the attack surface mapped, probe each entry point for vulnerabilities -> See [[Web application security testing methodology#Searching for web vulnerabilities]].