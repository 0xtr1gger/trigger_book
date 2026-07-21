---
created: 2026-07-16
tags:
  - recon
  - web_hacking
status: incomplete
---
## Virtual hosting

>**Virtual hosting** is a technique used by web servers to host **multiple website with different domain names on a single physical server and under the same IP address**.

>[!important] The **HTTP `Host` header** is used to specify the domain (virtual host) a HTTP request is destined to.

- **Multiple websites (virtual hosts) share the same IP address** (therefore all requests are destined to the same address). The `Host` header is used to inform the server to which **virtual host** the request should be routed.

```HTTP
GET / HTTP/1.1
Host: www.example.com
```

>[!important] This process is **transparent to end users** — visitors see each site as if it were hosted on its own dedicated server.

>[!warning]
>The `Host` header is **mandatory** in HTTP/1.1 precisely to support virtual hosting.
>Without the `Host` header, the server would not know which of the multiple hosted websites to serve.

>[!interesting]+ Virtual hosts vs. subdomains
>The key difference between virtual hosts and subdomains is their relationship with DNS and server configuration. 
>- Each **subdomain** typically has its own **DNS record** (`A`, `AAAA`, or `CNAME`), which can point to the same IP address as the parent domain or a different one. 
>- **Virtual hosts** are configured **on a web server**. Each virtual host has its own separate configuration and may or may not have a corresponding DNS record.
>
> A virtual host without a public DNS record might be used for:
> - Internal testing or staging environments
> - Hidden administrative interfaces
> - Development versions of production sites
> - etc.
### Types of virtual hosting

There are three main types of virtual hosting: 

- **Name-based virtual hosting**
	- Multiple virtual hosts share **a single IP address**.
	- The server uses the HTTP `Host` header to distinguish between different sites.
	- This is the most common and flexible approach, but HTTPS requires additional configuration (SNI support, see [[#Virtual hosting over HTTPS and SNI]] section).

This article primarily talks about **name-based virtual hosting**.

>[!example]+ Example: Name-based virtual hosting in Apache
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
	- Each virtual host is assigned a unique IP address, which is used to differentiate between websites.
	- The server determines which site to serve based on the destination IP address of the request.
	- Requires multiple IP addresses.
	- The `Host` header is not necessary for routing decisions.
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
	- Multiple websites share the same IP address but listen on different TCP ports (e.g., `80` for one site, `8080` for another).
	- This method is not user-friendly as the port number has to be specified in the URL (e.g., `https://example.com:8080`).
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

Here is what happens when you make a request to a virtual host, say, `host.example.com`:

1. **DNS resolution**
	- When you access a website (e.g., `host.example.com`), your browser first performs a DNS query to resolve the domain name to its corresponding IP address.

2. **Sending HTTP request**
	- With the IP address obtained, THE browser establishes a connection to the web server and sends an HTTP request that includes the `Host` header to specify the destination virtual host:
``
```HTTP
GET / HTTP/1.1
Host: host.example.com
```


3. **Server-side routing**
	 - The server receives the request, examines the `Host` header, and consults its virtual host configuration to find a matching entry for the requested domain.

4. **Response**
	- The server retrieves the requested content from the corresponding document root and sends it back to the client as an HTTP response.

>[!important] Even though multiple sites (virtual hosts) share the same IP address, each site is perceived as if it is served independently from its own dedicated server.


## Enumerating virtual hosts

- Virtual host enumeration can reveal:
	- **Hidden subdomains** without public DNS records
	- **Development/staging servers**
	- Administrative panels and internal applications
	- Forgotten or legacy applications

- Virtual host enumeration is performed by brute-forcing the `Host` HTTP header. This method **actively interrogates the target servers**.

- [`gobuster`](https://github.com/OJ/gobuster) has the `vhost` mode designed exactly for virtual host enumeration:

```bash
gobuster vhost -u http://example.com -w wordlist.txt
```


```bash
gobuster vhost -u http://example.com  -w /usr/share/wordlists/Discovery/DNS/subdomains-top1million-5000.txt --append-domain
```

```bash
gobuster vhost -u http://192.168.1.11 -w /usr/share/wordlists/Discovery/DNS/subdomains-top1million-5000.txt --domain example.com --append-domain
```

| Option                      | Description                                                |
| --------------------------- | ---------------------------------------------------------- |
| `-w`, `--wordlist`          | Path to the wordlist.                                      |
| `-u`, `--url`               | The target URL.                                            |
| `--append-domain`           | Append main domain from URL to words from wordlist.        |
| `--domain`                  | Domain to append when using an IP address as URL.          |
| `-r`, `--follow-redirect`   | Follow redirects.                                          |
| `-m`, `--method`            | Specify the HTTP method to use.                            |
| `-H`, `--headers`           | Specify HTTP headers.                                      |
| `-c`, `--cookies`           | Cookies to use for the requests.                           |
| `-k`, `--no-tls-validation` | Skip TLS certificate verification.                         |
| `-a`, `--useragent`         | Set the `User-Agent` string.                               |
| `--random-agent`            | Use a random `User-Agent` string.                          |
| `--retry`                   | Retry on request timeout.                                  |
| `--retry-attempts`          | Times to retry on request timeout.                         |
| `--timeout`                 | HTTP timeout.                                              |
| `--proxy`                   | Proxy to use for requests.                                 |
| `--exclude-length`          | Exclude the following content length (ignores the status). |
| `-U`, `--username`          | Username for HTTP Basic Authentication.                    |
| `-P`, `--password`          | Password for HTTP Basic Authentication.                    |
| `-h`, `--help`              | Help for `vhost`.                                          |

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


- Using [`ffuf`](https://github.com/ffuf/ffuf) (manually substituting `Host` header values):

```bash
ffuf -u http://example.com -w /usr/share/wordlists/Discovery/DNS/subdomains-top1million-5000.txt -H "Host: FUZZ.example.com" -c -ic
```


>[!note] Virtual hosts can also be found via **certificate transparency (CT) logs** — even if the virtual host domain doesn't have a real DNS record. See [[Subdomain enumeration#Certificate Transparency logs]].

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

When it comes to virtual hosting **over HTTPS (TLS)**, using the `Host` header to determine the intended recipient of a request is problematic. Why?

The server needs to select the correct SSL/TLS certificate **before** it can process any encrypted requests (where the `Host` header is specified). 
This is because in HTTPS, the SSL/TLS handshake — including certificate negotiation — happens _before_ the actual HTTP request (which contains the `Host` header) is decrypted and processed by the server. 

This leads to a classic chicken-and-egg problem:
- The **browser** expects the server to present a valid SSL certificate for the domain it is trying to access.
- The **server** needs to know the requested hostname (usually from the Host header) to determine which certificate to present.
- But the `Host` header is inside the encrypted HTTPS request, which is only decrypted _after_ the certificate is selected during the handshake.

This problem meant, historically, that HTTPS servers could only present a **single SSL/TLS certificate** per IP address:port combination. This limited the ability to host multiple secure websites (with distinct domain names) on the same IP and port.

To solve this problem, the **SNI** was invented.

>**[SNI](https://en.wikipedia.org/wiki/Server_Name_Indication) (Server Name Indication)** is a TLS extension ([`RFC 6066`](https://datatracker.ietf.org/doc/html/rfc6066)) that allows allows the client (browser) to indicate the hostname it wants to connect to **at the start of the TLS handshake**, before any encrypted content begins. 

With SNI, **the server receives the intended hostname in plaintext as part of the handshake**, and then presents the corresponding SSL certificate for that hostname.

>[!warning] 
>Yet, SNI introduces some privacy concerns: the domain name you're trying to access can be eavesdropped easily, since it's sent in plaintext. And to solve this, another TLS extension was created,  **[ECH (Encrypted Client-side Hello)](https://en.wikipedia.org/wiki/Server_Name_Indication#Encrypted_Client_Hello)**).
>See  [`SNI: Virtual Hosting for HTTPS`](https://www.ssl.com/article/sni-virtual-hosting-for-https/).