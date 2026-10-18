---
created: 2026-07-16
tags:
  - web_hacking
  - intel
status: substantial
updated: 2026-09-28
---

>[!note] See also [[Subdomain enumeration|Subdomain enumeration]].

## Virtual hosting

>**Virtual hosting** is a technique that lets a web server host **multiple websites with different domain names on a single physical server, typically sharing one IP address**.

- Multiple virtual hosts share the same IP address, so requests to different virtual hosts reach the same physical server. 
- The **`Host` HTTP request header** specifies the domain (virtual host) a request is destined for:

```HTTP
GET / HTTP/1.1
Host: www.example.com
```

>[!warning] The `Host` header is **mandatory** in HTTP/1.1 precisely to support virtual hosting. Without it, the server wouldn't know which of the hosted websites to serve.

>[!interesting]+ Virtual hosts vs. subdomains
>- The key difference is their relationship with DNS and server configuration.
>	- Each **subdomain** typically has its own **DNS record** (`A`, `AAAA`, or `CNAME`), which may point to the same IP address as the parent domain or a different one.
>	- **Virtual hosts** are configured **on the web server**. Each has its own configuration and may or may not have a corresponding DNS record.
>- A virtual host without a public DNS record might be used for:
> 	- internal testing or staging environments,
> 	- hidden administrative interfaces,
> 	- development versions of production sites,
> 	- etc.

>[!note] Virtual hosting is **transparent to end users** — each site appears as if it were hosted on its own dedicated server.
### Types of virtual hosting

- There are three main types of virtual hosting. This note primarily covers **name-based virtual hosting**.
- **Name-based virtual hosting**
	- Multiple virtual hosts share **a single IP address**.
	- The server uses the HTTP `Host` header to distinguish between sites.
	- The most common and flexible approach, but HTTPS requires additional configuration (SNI; see [[#Appendix A Virtual hosting over HTTPS and SNI]]).

>[!example]+ Example: name-based virtual hosting in Apache
> ```XML
> Listen 80
> <VirtualHost *:80>
>     ServerName www.example.com
>     ServerAlias example.com
>     DocumentRoot /var/www/example
>     ErrorLog ${APACHE_LOG_DIR}/example-error.log
>     CustomLog ${APACHE_LOG_DIR}/example-access.log combined
> </VirtualHost>
>
> <VirtualHost *:80>
>     ServerName www.example2.com
>     DocumentRoot /var/www/example2
>     ErrorLog ${APACHE_LOG_DIR}/example2-error.log
>     CustomLog ${APACHE_LOG_DIR}/example2-access.log combined
> </VirtualHost>
> ```

- **IP-based virtual hosting**
	- Each virtual host is assigned a unique IP address, which is used to distinguish between sites.
	- The server decides which site to serve based on the destination IP address of the request.
	- Requires multiple IP addresses.
	- The `Host` header is not needed for routing decisions.
	- Rarely used.

>[!example]+ Example: IP-based virtual hosting in Apache
>
> ```XML
> Listen 80
> <VirtualHost 192.0.2.1:80>
>     ServerName www.example.com
>     DocumentRoot /var/www/example
> </VirtualHost>
>
> <VirtualHost 192.0.2.2:80>
>     ServerName www.example2.com
>     DocumentRoot /var/www/example2
> </VirtualHost>
> ```

- **Port-based virtual hosting**
	- Multiple sites share the same IP address but listen on different TCP ports (e.g., `80` for one site, `8080` for another).
	- Not user-friendly, since the port number has to appear in the URL (e.g., `https://example.com:8080`).
	- Commonly used ports: `80`, `443`, `8080`, `8443`, `3000`, etc. (see [top HTTP ports on `shodan.io`](https://www.shodan.io/search/facet?query=HTTP&facet=port)).
	- Rarely used.

>[!example]+ Example: port-based virtual hosting in Apache
> ```XML
> Listen 80
> Listen 8080
>
> <VirtualHost *:80>
>     ServerName www.example.com
>     DocumentRoot /var/www/example
> </VirtualHost>
>
> <VirtualHost *:8080>
>     ServerName www.example.com
>     DocumentRoot /var/www/example-admin
> </VirtualHost>
> ```

### How name-based virtual hosting works

- When you request a virtual host such as `host.example.com`:

1. **DNS resolution** — The browser performs a DNS query to resolve `host.example.com` to its IP address.
2. **HTTP request** — The browser connects to the server and sends an HTTP request with the `Host` header set to the target virtual host:
```HTTP
GET / HTTP/1.1
Host: host.example.com
```
3. **Server-side routing** — The server examines the `Host` header and consults its virtual host configuration to find a matching entry.
4. **Response** — The server retrieves the content from the corresponding document root and returns it to the client.

## Enumerating virtual hosts

- Virtual host enumeration can reveal:
	- **Hidden subdomains** without public DNS records
	- **Development/staging servers**
	- **Administrative panels** and **internal applications**
	- Forgotten or legacy applications
- It works by brute-forcing the `Host` header, which **actively interrogates the target server**.
---
- [`gobuster`](https://github.com/OJ/gobuster) has a `vhost` mode designed exactly for this:

```bash
gobuster vhost -u http://example.com -w wordlist.txt
```

>[!note] Without `--append-domain`, the wordlist must contain fully qualified hostnames (e.g. `admin.example.com`). With `--append-domain`, `gobuster` appends the URL's domain to each word, so the wordlist holds bare labels (e.g. `admin`).

- Append the main domain from the URL to each word in the wordlist:

```bash
gobuster vhost -u http://example.com -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt --append-domain
```

- Target an IP address and specify the domain to append:

```bash
gobuster vhost -u http://192.168.1.11 -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt --domain example.com --append-domain
```

| Option                      | Description                                                 |
| --------------------------- | ---------------------------------------------------------- |
| `-w`, `--wordlist`          | Path to the wordlist.                                      |
| `-u`, `--url`               | The target URL.                                            |
| `--append-domain`           | Append the main domain from the URL to words in the wordlist. |
| `--domain`                  | Domain to append when using an IP address as the URL.      |
| `-r`, `--follow-redirect`   | Follow redirects.                                          |
| `-m`, `--method`            | HTTP method to use.                                        |
| `-H`, `--headers`           | Specify HTTP headers.                                      |
| `-c`, `--cookies`           | Cookies to use for the requests.                           |
| `-k`, `--no-tls-validation` | Skip TLS certificate verification.                         |
| `-a`, `--useragent`         | Set the `User-Agent` string.                               |
| `--random-agent`            | Use a random `User-Agent` string.                          |
| `--retry`                   | Retry on request timeout.                                  |
| `--retry-attempts`          | Number of times to retry on request timeout.               |
| `--timeout`                 | HTTP timeout.                                              |
| `--proxy`                   | Proxy to use for requests.                                 |
| `--exclude-length`          | Exclude responses of the given content length (ignores the status). |
| `-U`, `--username`          | Username for HTTP Basic Authentication.                    |
| `-P`, `--password`          | Password for HTTP Basic Authentication.                    |
| `-h`, `--help`              | Show help for `vhost`.                                     |

>[!example]+
> ```bash
> gobuster vhost -u http://94.237.57.211:48978 -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt --domain inlanefreight.htb --append-domain
> ```
>
> ```bash
> ===============================================================
> Gobuster v3.6
> by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
> ===============================================================
> [+] Url:             http://94.237.57.211:48978
> [+] Method:          GET
> [+] Threads:         10
> [+] Wordlist:        /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt
> [+] User Agent:      gobuster/3.6
> [+] Timeout:         10s
> [+] Append Domain:   true
> ===============================================================
> Starting gobuster in VHOST enumeration mode
> ===============================================================
> Found: blog.inlanefreight.htb Status: 200 [Size: 98]
> Found: admin.inlanefreight.htb Status: 200 [Size: 100]
> Found: forum.inlanefreight.htb Status: 200 [Size: 100]
> Found: support.inlanefreight.htb Status: 200 [Size: 104]
> Found: vm5.inlanefreight.htb Status: 200 [Size: 96]
> Found: browse.inlanefreight.htb Status: 200 [Size: 102]
> Found: web17611.inlanefreight.htb Status: 200 [Size: 106]
> Progress: 114441 / 114442 (100.00%)
> ===============================================================
> Finished
> ===============================================================
> ```

- Using [`ffuf`](https://github.com/ffuf/ffuf), fuzzing the `Host` header directly:

```bash
ffuf -u http://example.com -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt -H "Host: FUZZ.example.com" -c -ic
```

>[!important] A non-existent virtual host still returns the server's default response (usually `200` with the default site), so brute-forcing produces many false positives. Filter out that baseline by response size — `-fs <length>` in `ffuf`, `--exclude-length <length>` in `gobuster`.

>[!note] Virtual hosts can also be found via **Certificate Transparency (CT) logs** — even when the virtual host has no real DNS record. See [[Subdomain enumeration#Certificate Transparency logs]].

- Wordlists:
	- [`Discovery/DNS/subdomains-top1million-5000.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/DNS/subdomains-top1million-5000.txt)
	- [`Discovery/DNS/subdomains-top1million-20000.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/DNS/subdomains-top1million-20000.txt)
	- [`Discovery/DNS/subdomains-top1million-110000.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/DNS/subdomains-top1million-110000.txt)
	- [`Discovery/DNS/n0kovo_subdomains.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/DNS/n0kovo_subdomains.txt)
	- [`Discovery/Web-Content/common.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/common.txt)

>[!note] See [[Subdomain enumeration#Wordlists]] for more.

## References and further reading

- [`Virtual hosting — Wikipedia`](https://en.wikipedia.org/wiki/Virtual_hosting)

## Appendix A: Virtual hosting over HTTPS and SNI

- With virtual hosting **over HTTPS (TLS)**, using the `Host` header to determine a request's intended recipient is problematic: the server must select the correct TLS certificate **before** it can decrypt any request (and thus before it can read the `Host` header). This is because the TLS handshake — including certificate negotiation — happens *before* the HTTP request is decrypted.
- This creates a chicken-and-egg problem:
	- The **browser** expects the server to present a valid certificate for the domain it wants to reach.
	- The **server** needs the requested hostname (usually from the `Host` header) to decide which certificate to present.
	- But the `Host` header is inside the encrypted request, which is only decrypted *after* the certificate is selected during the handshake.
- Historically, this meant an HTTPS server could present only a **single TLS certificate** per each IP-address:port combination, which limits the ability to host multiple secure sites (with distinct domain names) on the same IP and port. **SNI** was invented to solve this.

>**[SNI](https://en.wikipedia.org/wiki/Server_Name_Indication) (Server Name Indication)** is a TLS extension ([`RFC 6066`](https://datatracker.ietf.org/doc/html/rfc6066)) that lets the client indicate the hostname it wants to connect to **at the start of the TLS handshake**, before any encrypted content begins.

- With SNI, **the server receives the intended hostname in plaintext during the handshake** and then presents the corresponding certificate for that hostname.

>[!warning] SNI introduces a privacy concern: the domain you're connecting to is sent in plaintext and can be eavesdropped. To address this, another TLS extension was created — **[ECH (Encrypted Client Hello)](https://en.wikipedia.org/wiki/Server_Name_Indication#Encrypted_Client_Hello)**.
>>[!note] See [`SNI: Virtual Hosting for HTTPS`](https://www.ssl.com/article/sni-virtual-hosting-for-https/).
