---
created: 2026-05-16
tags:
  - web_knowledge_base
  - reference
status: draft
---
## Server identification

| Header Name           | Description                                                                                       | Examples                                                                                       |
| --------------------- | ------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `Server`              | May reveal the web server software and version running on the target system.                      | `Server: Apache/2.4.41 (Ubuntu)`  <br>`Server: nginx/1.18.0`  <br>`Server: Microsoft-IIS/10.0` |
| `X-Powered-By`        | May disclose backend technologies, programming languages, or frameworks powering the application. | `X-Powered-By: PHP/7.4.3`  <br>`X-Powered-By: Express`  <br>`X-Powered-By: ASP.NET`            |
| `X-AspNet-Version`    | Reveals specific version of ASP.NET framework in use.                                             | `X-AspNet-Version: 4.0.30319`                                                                  |
| `X-AspNetMvc-Version` | Discloses ASP.NET MVC framework version, useful for identifying MVC-specific vulnerabilities.     | `X-AspNetMvc-Version: 5.2`                                                                     |
| `X-Runtime`           | Shows execution time and sometimes runtime environment details (Ruby, Node.js).                   | `X-Runtime: 0.234567`  <br>`X-Runtime: Ruby`                                                   |
| `X-Version`           | Generic header used by some applications; may expose software versions.                           | `X-Version: 1.2.3`                                                                             |
| `X-Generator`         | Identifies the CMS or framework that generated the page, commonly seen in CMS platforms.          | `X-Generator: Drupal 8`  <br>`X-Generator: WordPress 5.8`                                      |
## Frameworks and CMSs

| Header Name              | Description                                                                              | Examples                                                  |
| ------------------------ | ---------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| `X-Drupal-Cache`         | Drupal CMS; indicates cache status.                                                      | `X-Drupal-Cache: HIT`  <br>`X-Drupal-Cache: MISS`         |
| `X-Drupal-Dynamic-Cache` | Drupal CMS; shows dynamic cache status.                                                  | `X-Drupal-Dynamic-Cache: UNCACHEABLE`                     |
| `X-Mod-Pagespeed`        | Reveals Google PageSpeed module usage and version.                                       | `X-Mod-Pagespeed: 1.13.35.2-0`                            |
| `X-Pingback`             | WordPress; points to XML-RPC pingback endpoint.                                          | `X-Pingback: https://example.com/xmlrpc.php`              |
| `X-Joomla-Cache`         | Joomla CMS; indicates cache status.                                                      | `X-Joomla-Cache: Miss`<br>`X-Joomla-Cache: Hit`           |
| `X-Redirect-By`          | Identifies the component responsible for redirects (WordPress plugins, etc.).            | `X-Redirect-By: WordPress`  <br>`X-Redirect-By: Polylang` |
| `X-Generator`            | Identifies the CMS or framework that generated the page, commonly seen in CMS platforms. | `X-Generator: Drupal 8`  <br>`X-Generator: WordPress 5.8` |

## Intermediaries
### Caching and CDNs

| Header                | Description                                                                              | Examples                                                             |
| --------------------- | ---------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `Cache-Control`       | Defines caching directives.                                                              | `Cache-Control: no-cache`  <br>`Cache-Control: max-age=3600, public` |
| `Expires`             | Cache expiration time.                                                                   | `Expires: Thu, 01 Dec 2025 16:00:00 GMT`                             |
| `Age`                 | Time in seconds the object has been in proxy cache.                                      | `Age: 12345`                                                         |
| `ETag`                | Entity tag for cache validation and version tracking.                                    | `ETag: "737060cd8c284d8af7ad3082f209582d"`                           |
| `Last-Modified`       | Last modification timestamp, used for cache validation.                                  | `Last-Modified: Tue, 15 Nov 2024 12:45:26 GMT`                       |
| `Vary`                | Indicates which request headers affect cache key; reveals possible cache key components. | `Vary: Accept-Encoding, User-Agent`                                  |
| `X-Cache`             | Shows whether the response was served from cache.                                        | `X-Cache: HIT from cloudfront`  <br>`X-Cache: MISS`                  |
| `X-Cache-Hits`        | Number of cache hits.                                                                    | `X-Cache-Hits: 142`                                                  |
| `X-Served-By`         | Identifies which server or CDN node served the content.                                  | `X-Served-By: cache-lax-kwhp1940032-LAX`                             |
| `X-Backend-Server`    | Reveals internal backend server information behind load balancers.                       | `X-Backend-Server: web-server-01`                                    |
| `Pragma`              | Legacy cache control (HTTP/1.0), still used by some systems.                             | `Pragma: no-cache`                                                   |
| `X-Varnish`           | Varnish-specific cache server identifier.                                                | `X-Varnish: 123456 789012`                                           |
| `X-Fastly-Request-ID` | Fastly CDN request identifier.                                                           | `X-Fastly-Request-ID: abc123def456`                                  |
| `CF-Cache-Status`     | Cloudflare cache status (Cloudflare CDN).                                                | `CF-Cache-Status: HIT`  <br>`CF-Cache-Status: MISS`                  |
| `CF-Ray`              | Cloudflare request identifier and datacenter location.                                   | `CF-Ray: 6a1b2c3d4e5f6g-LAX`                                         |
| `True-Client-IP`      | Akamai CDN; indicates original client IP address.                                        | `True-Client-IP: 203.0.113.195`                                      |
### Proxies

| Header Name           | Description                                                                      | Examples                                                                           |
| --------------------- | -------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `X-Forwarded-For`     | Original client IP address.                                                      | `X-Forwarded-For: 203.0.113.195`  <br>`X-Forwarded-For: 203.0.113.195, 70.41.3.18` |
| `X-Forwarded-Host`    | Original `Host` header value before proxy modification.                          | `X-Forwarded-Host: example.com`  <br>`X-Forwarded-Host: example.com:8080`          |
| `X-Forwarded-Proto`   | Original protocol (HTTP/HTTPS) used by the client.                               | `X-Forwarded-Proto: https`  <br>`X-Forwarded-Proto: http`                          |
| `X-Forwarded-Port`    | Original port number used in the request.                                        | `X-Forwarded-Port: 443`  <br>`X-Forwarded-Port: 8080`                              |
| `X-Real-IP`           | Real IP address of the client (Nginx-specific alternative to `X-Forwarded-For`). | `X-Real-IP: 203.0.113.195`                                                         |
| `Forwarded`           | A standardized header that replaces `X-Forwarded-*` headers.                     | `Forwarded: for=192.0.2.60;proto=http;by=203.0.113.43`                             |
| `Via`                 | Proxies through which the request/response passed.                               | `Via: 1.1 vegur`  <br>`Via: 1.0 fred, 1.1 example.com (Apache/1.1)`                |
| `X-ProxyUser-Ip`      | Google-specific header for real client IP address                                | .`X-ProxyUser-Ip: 203.0.113.195`                                                   |
| `Front-End-Https`     | Microsoft load balancer header; indicates HTTPS frontend.                        | `Front-End-Https: on`                                                              |
| `X-Cluster-Client-IP` | Client IP in clustered environments.                                             | `X-Cluster-Client-IP: 203.0.113.195`                                               |

### Load balancers

| Header Name                | Description                                    | Examples                                             |
| -------------------------- | ---------------------------------------------- | ---------------------------------------------------- |
| `X-Load-Balancer`          | Identifies load balancer handling the request. | `X-Load-Balancer: haproxy-01`                        |
| `X-Upstream-Status`        | Status code from upstream server behind proxy. | `X-Upstream-Status: 200`                             |
| `X-Upstream-Response-Time` | Response time from upstream server.            | `X-Upstream-Response-Time: 0.034`                    |
| `X-Application-Context`    | Spring Boot application context information.   | `X-Application-Context: application:production:8080` |
| `X-Backend`                | Backend server that processed the request.     | `X-Backend: web-01.internal`                         |
| `Server-Timing`            | Performance timing metrics from server.        | `Server-Timing: db;dur=53, app;dur=47.2`             |

### WAFs (Web Application Firewall) 

| Header Name        | Description                                | Examples                                 |
| ------------------ | ------------------------------------------ | ---------------------------------------- |
| `X-WAF-Event-Info` | WAF event information.                     | `X-WAF-Event-Info: blocked`              |
| `X-CDN`            | Identifies CDN provider in use.            | `X-CDN: Cloudflare`  <br>`X-CDN: Akamai` |
| `X-Sucuri-ID`      | Sucuri WAF identifier.                     | `X-Sucuri-ID: 12345`                     |
| `X-Sucuri-Cache`   | Sucuri caching status.                     | `X-Sucuri-Cache: HIT`                    |
| `X-Edge-Location`  | Edge server location handling the request. | `X-Edge-Location: us-east-1`             |

## Security headers

| Header Name                 | Description                                                                                   | Examples                                                                                                        |
| --------------------------- | --------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `Content-Security-Policy`   | Defines allowed content sources; prevents XSS and other injection attacks.                    | `Content-Security-Policy: default-src 'self'`  <br>`Content-Security-Policy: script-src 'self' 'unsafe-inline'` |
| `X-Content-Security-Policy` | Legacy CSP header for older browsers.                                                         | `X-Content-Security-Policy: default-src 'self'`                                                                 |
| `X-WebKit-CSP`              | WebKit-specific legacy CSP header.                                                            | `X-WebKit-CSP: default-src 'self'`                                                                              |
| `Strict-Transport-Security` | Enforces HTTPS.                                                                               | `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`                                       |
| `X-Frame-Options`           | Prevents clickjacking by controlling iframe embedding.                                        | `X-Frame-Options: DENY`  <br>`X-Frame-Options: SAMEORIGIN`                                                      |
| `X-XSS-Protection`          | Browser XSS filter control (deprecated).                                                      | `X-XSS-Protection: 1; mode=block`  <br>`X-XSS-Protection: 0`                                                    |
| `X-Content-Type-Options`    | Prevents MIME-sniffing attacks.                                                               | `X-Content-Type-Options: nosniff`                                                                               |
| `Referrer-Policy`           | Controls information exposed by the `Referer` header.                                         | `Referrer-Policy: strict-origin-when-cross-origin`  <br>`Referrer-Policy: no-referrer`                          |
| `Permissions-Policy`        | Controls browser feature access (camera, microphone, geolocation), formerly `Feature-Policy`. | `Permissions-Policy: geolocation=(), camera=(), microphone=()`                                                  |
| `Feature-Policy`            | Deprecated predecessor to `Permissions-Policy`.                                               | `Feature-Policy: geolocation 'none'; camera 'none'`                                                             |
| `Expect-CT`                 | Certificate Transparency enforcement and reporting (deprecated).                              | `Expect-CT: max-age=86400, enforce, report-uri="https://example.com/report"`                                    |
| `Public-Key-Pins`           | HTTP Public Key Pinning for certificate pinning (deprecated).                                 | `Public-Key-Pins: max-age=2592000; pin-sha256="base64=="`                                                       |

### CORS

| Header Name                        | Description                                              | Examples                                                                                    |
| ---------------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `Access-Control-Allow-Origin`      | Allowed origins for CORS.                                | `Access-Control-Allow-Origin: *`  <br>`Access-Control-Allow-Origin: https://example.com`    |
| `Access-Control-Allow-Methods`     | Allowed HTTP methods for CORS requests.                  | `Access-Control-Allow-Methods: GET, POST, PUT, DELETE`                                      |
| `Access-Control-Allow-Headers`     | Allowed headers for CORS requests.                       | `Access-Control-Allow-Headers: Content-Type, Authorization`                                 |
| `Access-Control-Allow-Credentials` | Whether credentials can be sent in CORS requests.        | `Access-Control-Allow-Credentials: true`                                                    |
| `Access-Control-Expose-Headers`    | Response headers exposed to frontend JavaScript.         | `Access-Control-Expose-Headers: X-Custom-Header`                                            |
| `Access-Control-Max-Age`           | Preflight request cache duration.                        | `Access-Control-Max-Age: 86400`                                                             |
| `Cross-Origin-Opener-Policy`       | Controls document's browsing context group isolation.    | `Cross-Origin-Opener-Policy: same-origin`                                                   |
| `Cross-Origin-Embedder-Policy`     | Prevents loading unapproved cross-origin resources.      | `Cross-Origin-Embedder-Policy: require-corp`                                                |
| `Cross-Origin-Resource-Policy`     | Controls which origins can load the resource.            | `Cross-Origin-Resource-Policy: same-site`  <br>`Cross-Origin-Resource-Policy: cross-origin` |
| `Origin`                           | Request origin for CORS, shows where request originated. | `Origin: https://example.com`                                                               |
| `Timing-Allow-Origin`              | Origins allowed to access Resource Timing API data.      | `Timing-Allow-Origin: *`  <br>`Timing-Allow-Origin: https://example.com`                    |




## Session and authentication

| Header Name           | Description                                                    | Examples                                                                                      |
| --------------------- | -------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| `Set-Cookie`          | Sets cookies.                                                  | `Set-Cookie: PHPSESSID=abc123; HttpOnly; Secure`  <br>`Set-Cookie: JSESSIONID=xyz789; Path=/` |
| `Cookie`              | Request header; shows cookies sent by the client.              | `Cookie: sessionid=abc123; csrftoken=xyz789`                                                  |
| `WWW-Authenticate`    | Indicates authentication scheme (`Basic`, `Digest`, `Bearer`). | `WWW-Authenticate: Basic realm="Access required"`  <br>`WWW-Authenticate: Bearer realm="API"` |
| `Authorization`       | Contains authentication credentials.                           | `Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==`  <br>`Authorization: Bearer token123`     |
| `Proxy-Authenticate`  | Proxy authentication requirements.                             | `Proxy-Authenticate: Basic realm="Proxy"`                                                     |
| `Proxy-Authorization` | Credentials for proxy authentication.                          | `Proxy-Authorization: Basic encodedcredentials`                                               |
| `X-Csrf-Token`        | CSRF protection token.                                         | `X-Csrf-Token: i8XNjC4b8KVok4uw5RftR38Wgp2BFwql`                                              |
| `X-XSRF-TOKEN`        | Alternative CSRF token header.                                 | `X-XSRF-TOKEN: abc123def456`                                                                  |
| `X-CSRFToken`         | Another CSRF token header variant.                             | `X-CSRFToken: token123`                                                                       |

## Custom application headers

| Header Name                         | Description                                                   | Examples                                                 |
| ----------------------------------- | ------------------------------------------------------------- | -------------------------------------------------------- |
| `X-Api-Version`                     | API version information.                                      | `X-Api-Version: v2.3.1`  <br>`X-Api-Version: 2024-10-01` |
| `X-Rate-Limit-Limit`                | Rate limiting maximum requests allowed.                       | `X-Rate-Limit-Limit: 1000`                               |
| `X-Rate-Limit-Remaining`            | Remaining requests in current rate limit window.              | `X-Rate-Limit-Remaining: 742`                            |
| `X-Rate-Limit-Reset`                | Timestamp when rate limit resets.                             | `X-Rate-Limit-Reset: 1633024800`                         |
| `X-Response-Time`                   | Server processing time for the request.                       | `X-Response-Time: 123ms`                                 |
| `X-Robots-Tag`                      | Robot indexing directives (alternative to `robots` meta tag). | `X-Robots-Tag: noindex, nofollow`                        |
| `X-Download-Options`                | IE-specific header controlling download behavior.             | `X-Download-Options: noopen`                             |
| `X-Permitted-Cross-Domain-Policies` | Controls cross-domain policy file usage (Flash, PDF).         | `X-Permitted-Cross-Domain-Policies: none`                |

## User agents and information about the client

| Header Name          | Description                                                                        | Examples                                                            |
| -------------------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `User-Agent`         | Client browser and OS information (request header analyzed during fingerprinting). | `User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/95.0` |
| `Accept-CH`          | Requests specific Client Hints from browser.                                       | `Accept-CH: Viewport-Width, DPR, Device-Memory`                     |
| `Sec-CH-UA`          | User agent client hint with browser branding.                                      | `Sec-CH-UA: "Chromium";v="95", "Chrome";v="95"`                     |
| `Sec-CH-UA-Platform` | Client platform hint.                                                              | `Sec-CH-UA-Platform: "Windows"`                                     |
| `Sec-CH-UA-Mobile`   | Indicates mobile device.                                                           | `Sec-CH-UA-Mobile: ?0`                                              |
| `X-UA-Compatible`    | IE rendering mode recommendation.                                                  | `X-UA-Compatible: IE=edge`                                          |

## Request tracking and debugging headers

| Header               | Description                                           | Examples                                                |
| -------------------- | ----------------------------------------------------- | ------------------------------------------------------- |
| `X-Request-ID`       | Unique request identifier for tracing and debugging.  | `X-Request-ID: f058ebd6-02f7-4d3f-942e-904344e8cde5`    |
| `X-Correlation-ID`   | Request correlation identifier across microservices.  | `X-Correlation-ID: abc-123-def-456`                     |
| `X-Transaction-ID`   | Transaction identifier in distributed systems.        | `X-Transaction-ID: txn_123456789`                       |
| `X-Trace-Id`         | Distributed tracing identifier (OpenTracing, Zipkin). | `X-Trace-Id: 463ac35c9f6413ad48485a3953bb6124`          |
| `X-Span-Id`          | Span identifier within distributed trace.             | `X-Span-Id: a2fb4a1d1a96d312`                           |
| `X-Debug-Token`      | Symfony; profiler debug token.                        | `X-Debug-Token: abc123`                                 |
| `X-Debug-Token-Link` | Symfony; link to web profiler for debugging.          | `X-Debug-Token-Link: http://localhost/_profiler/abc123` |
| `X-B3-TraceId`       | Zipkin B3 propagation trace ID.                       | `X-B3-TraceId: 80f198ee56343ba864fe8b2a57d3eff7`        |
| `X-B3-SpanId`        | Zipkin B3 span ID.                                    | `X-B3-SpanId: e457b5a2e4d86bd1`                         |

## Tracking

| Header Name      | Description                                                | Examples                                       |
| ---------------- | ---------------------------------------------------------- | ---------------------------------------------- |
| `DNT`            | Do Not Track preference (request header).                  | `DNT: 1`                                       |
| `Tk`             | Tracking status response.                                  | `Tk: N` (not tracking)  <br>`Tk: T` (tracking) |
| `Sec-GPC`        | Global Privacy Control indicating consent preferences.     | `Sec-GPC: 1`                                   |
| `X-Do-Not-Track` | Legacy DNT header variant.                                 | `X-Do-Not-Track: 1`                            |
| `X-UIDH`         | Verizon "supercookie" unique identifier (privacy concern). | `X-UIDH: encoded-string`                       |

## Content and media

| Header Name           | Description                                                           | Examples                                                                       |
| --------------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| `Content-Type`        | MIME type of response content, crucial for understanding data format. | `Content-Type: text/html; charset=UTF-8`  <br>`Content-Type: application/json` |
| `Content-Length`      | Size of response body in bytes.                                       | `Content-Length: 348`                                                          |
| `Content-Encoding`    | Encoding applied to response (gzip, deflate).                         | `Content-Encoding: gzip`                                                       |
| `Content-Language`    | Natural language of content.                                          | `Content-Language: en-US`                                                      |
| `Content-Disposition` | Suggests filename for downloads.                                      | `Content-Disposition: attachment; filename="data.pdf"`                         |
| `Content-Location`    | Alternate location for the content.                                   | `Content-Location: /documents/report.pdf`                                      |
| `X-Content-Duration`  | Duration of audio/video content (deprecated).                         | `X-Content-Duration: 42.666`                                                   |

## HTTP method override

| Header Name              | Description                                                               | Examples                                                            |
| ------------------------ | ------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `X-HTTP-Method-Override` | Overrides HTTP method (used when `PUT`/`DELETE` are blocked by firewall). | `X-HTTP-Method-Override: PUT`  <br>`X-HTTP-Method-Override: DELETE` |
| `X-Method-Override`      | Alternative method override header.                                       | `X-Method-Override: PATCH`                                          |

## Other headers

| Header Name     | Description                                          | Examples                                    |
| --------------- | ---------------------------------------------------- | ------------------------------------------- |
| `Location`      | Redirect target URL.                                 | `Location: https://example.com/new-page`    |
| `Refresh`       | Auto-refresh or redirect after delay.                | `Refresh: 5; url=https://example.com`       |
| `Link`          | Relationship links to other resources.               | `Link: </style.css>; rel=preload; as=style` |
| `Allow`         | Allowed HTTP methods for endpoint (`405` responses). | `Allow: GET, POST, HEAD`                    |
| `Accept-Ranges` | Indicates byte-range request support.                | `Accept-Ranges: bytes`                      |
| `Alt-Svc`       | Alternative service locations and protocols.         | `Alt-Svc: h3=":443"; ma=2592000`            |
| `Status`        | CGI status line (non-standard).                      | `Status: 200 OK`                            |
| `P3P`           | P3P privacy policy (largely obsolete).               | `P3P: CP="CAO PSA OUR"`                     |

## Cookies names

| Cookie Name / Pattern        | Likely Technology / Framework / Server                    | Notes / Details                                                                           |
| ---------------------------- | --------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `PHPSESSID`                  | PHP (native session management)                           | Default PHP session cookie name. Common in WordPress, Drupal, Joomla, and other PHP apps. |
| `wordpress_logged_in_*`      | WordPress                                                 | WordPress login session cookie.                                                           |
| `wp-settings-*`              | WordPress                                                 | WordPress user settings cookie.                                                           |
| `JSESSIONID`                 | Java Servlet containers (Tomcat, Jetty, JBoss, WebSphere) | Default Java session cookie.                                                              |
| `jsessionid` (lowercase)     | Java-based web apps                                       | Same as above; case may vary.                                                             |
| `ASP.NET_SessionId`          | ASP.NET / IIS                                             | Default ASP.NET session cookie.                                                           |
| `.ASPXAUTH`                  | ASP.NET Forms Authentication                              | Auth cookie for ASP.NET.                                                                  |
| `CFID` / `CFTOKEN`           | Adobe ColdFusion                                          | ColdFusion session cookies.                                                               |
| `connect.sid`                | Express.js (Node.js)                                      | Default session cookie for Express.js using `express-session`.                            |
| `laravel_session`            | Laravel (PHP framework)                                   | Laravel default session cookie.                                                           |
| `XSRF-TOKEN`                 | Laravel, Angular                                          | CSRF protection token cookie; common in Laravel apps.                                     |
| `SID` / `HSID` / `SSID`      | Google services                                           | Google session cookies; may appear on sites using Google services.                        |
| `S`                          | Google services                                           | Another Google cookie.                                                                    |
| `CAKEPHP`                    | CakePHP (PHP framework)                                   | CakePHP session cookie.                                                                   |
| `symfony`                    | Symfony (PHP framework)                                   | Symfony session cookie.                                                                   |
| `ci_session`                 | CodeIgniter (PHP framework)                               | CodeIgniter session cookie.                                                               |
| `sessionid`                  | Django (Python framework)                                 | Default Django session cookie.                                                            |
| `csrftoken`                  | Django (Python framework)                                 | Default Django CSRF token cookie.                                                         |
| `laravel_token`              | Laravel                                                   | CSRF token cookie.                                                                        |
| `PLAY_SESSION`               | Play Framework (Scala/Java)                               | Play Framework session cookie.                                                            |
| `PHP_AUTH_USER`              | Basic HTTP Authentication (PHP)                           | May appear when HTTP Basic Auth is used.                                                  |
| `ZSESSIONID`                 | Zope / Plone (Python web apps)                            | Session cookie for Zope/Plone applications.                                               |
| `SIDCC`                      | Cloudflare WAF                                            | Cloudflare's bot management cookie.                                                       |
| `__cfduid`                   | Cloudflare                                                | Cloudflare cookie for identifying clients behind shared IPs.                              |
| `BIGipServer*`               | F5 BIG-IP Load Balancer                                   | Load balancer cookie indicating F5 BIG-IP presence.                                       |
| `TS*`                        | F5 TrafficShield WAF                                      | Cookies starting with TS often indicate F5 WAF.                                           |
| `visid_incap_`               | Imperva Incapsula WAF                                     | Incapsula session cookie.                                                                 |
| `incap_ses_`                 | Imperva Incapsula WAF                                     | Incapsula session cookie.                                                                 |
| `akamai_*`                   | Akamai CDN / WAF                                          | Akamai cookies for CDN or WAF functionality.                                              |
| `s_fid` / `s_vi`             | Adobe Analytics / Omniture                                | Analytics cookies, sometimes seen on Adobe Experience Manager sites.                      |
| `ASPSESSIONID*`              | Classic ASP                                               | Classic ASP session cookie.                                                               |
| `SID`                        | Google services                                           | Google session cookie, also used in other Google products.                                |
| `WZRK_*`                     | WebEngage                                                 | WebEngage marketing automation cookies.                                                   |
| `NID`                        | Google services                                           | Google cookie used for preferences.                                                       |
| `SID` / `SAPISID` / `APISID` | Google services                                           | Google authentication cookies.                                                            |

### Programming languages

| Cookie              | Description                                                                                                              | Examples                                       |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------- |
| `PHPSESSID`         | Default PHP session identifier, reveals PHP backend implementation and indicates potential PHP-specific vulnerabilities. | `PHPSESSID=abc123def456789`                    |
| `JSESSIONID`        | Java/J2EE session identifier used by Tomcat, JBoss, WebLogic, and other Java application servers.                        | `JSESSIONID=F1234567890ABCDEF1234567890ABCDEF` |
| `ASP.NET_SessionId` | ASP.NET framework session cookie indicating Microsoft .NET technology stack.                                             | `ASP.NET_SessionId=xyz789abc123`               |
| `ASPSESSIONID`      | Classic ASP session identifier (followed by random characters), revealing older ASP technology.                          | `ASPSESSIONIDQQABCDEF=GHIJKLMNOPQRSTUVWXYZ`    |
| `CFID`              | Adobe ColdFusion session identifier component, part of ColdFusion's session management.                                  | `CFID=123456`                                  |
| `CFTOKEN`           | Adobe ColdFusion authentication token paired with CFID for session tracking.                                             | `CFTOKEN=abcdef123456789`                      |
| `cfglobals`         | ColdFusion global variables cookie.                                                                                      | `cfglobals=...`                                |


### Frameworks

| Cookie            | Description                                                                         | Examples                             |
| ----------------- | ----------------------------------------------------------------------------------- | ------------------------------------ |
| `phpbb3_`         | phpBB forum software session/authentication cookie (followed by unique identifier). | `phpbb3_abc123_sid=session_id_value` |
| `phpbb3_u`        | phpBB user identification cookie.                                                   | `phpbb3_u=2`                         |
| `phpbb3_k`        | phpBB auto-login key cookie.                                                        | `phpbb3_k=autologin_key`             |
| `cakephp`         | CakePHP framework session cookie (default name, often customized).                  | `cakephp=session_identifier`         |
| `CAKEPHP`         | Alternative CakePHP session cookie naming convention.                               | `CAKEPHP=abc123`                     |
| `kohanasession`   | Kohana PHP framework session identifier.                                            | `kohanasession=xyz789`               |
| `laravel_session` | Laravel PHP framework session cookie.                                               | `laravel_session=eyJpdiI6...`        |
| `XSRF-TOKEN`      | Laravel CSRF protection token (also used by other frameworks).                      | `XSRF-TOKEN=abc123def456`            |
| `django`          | Django Python framework session cookie (customizable).                              | `django=sessionid_value`             |
| `sessionid`       | Common Django session cookie name.                                                  | `sessionid=abc123def456`             |
| `csrftoken`       | Django CSRF protection token.                                                       | `csrftoken=token_value`              |
### CMSs


| Cookie                       | Description                                                                         | Examples                                    |
| ---------------------------- | ----------------------------------------------------------------------------------- | ------------------------------------------- |
| `wp-settings-{user_id}`      | WordPress user-specific settings cookie; contains UI preferences and customization. | `wp-settings-1=editor%3Dtinymce`            |
| `wp-settings-time-{user_id}` | WordPress timestamp cookie tracking when settings were last updated.                | `wp-settings-time-1=1633024800`             |
| `wordpress_logged_in_`       | WordPress authentication cookie indicating logged-in user (followed by hash).       | `wordpress_logged_in_abc123=username%7C...` |
| `wordpress_test_cookie`      | WordPress test cookie to verify browser cookie support.                             | `wordpress_test_cookie=WP+Cookie+check`     |
| `BITRIX_`                    | 1C-Bitrix CMS session identifier prefix.                                            | `BITRIX_SM_GUEST_ID=123456`                 |
| `AMP`                        | AMPcms session/identification cookie.                                               | `AMP=value`                                 |
| `DotNetNukeAnonymous`        | DotNetNuke CMS anonymous user tracking cookie.                                      | `DotNetNukeAnonymous=guid_value`            |
| `authentication`             | DotNetNuke authentication cookie.                                                   | `authentication=...`                        |
| `e107_tz`                    | e107 CMS timezone cookie.                                                           | `e107_tz=-5`                                |
| `EPiTrace`                   | EPiServer CMS tracing cookie.                                                       | `EPiTrace=value`                            |
| `EPiServer`                  | EPiServer session/authentication cookie.                                            | `EPiServer=session_value`                   |
| `graffitibot`                | Graffiti CMS bot detection cookie.                                                  | `graffitibot=1`                             |
| `hotaru_mobile`              | Hotaru CMS mobile detection cookie.                                                 | `hotaru_mobile=0`                           |
| `ICMSession`                 | ImpressCMS session identifier.                                                      | `ICMSession=abc123`                         |
| `MAKACSESSION`               | Indico conference management system session cookie.                                 | `MAKACSESSION=value`                        |
| `InstantCMS[logdate]`        | InstantCMS login date tracking cookie.                                              | `InstantCMS[logdate]=timestamp`             |
| `CMSPreferredCulture`        | Kentico CMS language/culture preference cookie.                                     | `CMSPreferredCulture=en-US`                 |
| `MODx`                       | MODx CMS session identifier pattern.                                                | `SN4abc123sessionid=value`                  |
| `fe_typo_user`               | TYPO3 CMS frontend user session cookie.                                             | `fe_typo_user=session_id`                   |
| `be_typo_user`               | TYPO3 backend user authentication cookie.                                           | `be_typo_user=admin_session`                |
| `Dynamicweb`                 | Dynamicweb CMS session cookie.                                                      | `Dynamicweb=value`                          |
| `lep[numeric]+sessionid`     | LEPTON CMS session identifier with numeric component.                               | `lep123456sessionid=abc`                    |
| `VivvoSessionId`             | VIVVO CMS session identifier.                                                       | `VivvoSessionId=xyz789`                     |

## References and further reading

- [`List of HTTP header fields — Wikipedia`](https://en.wikipedia.org/wiki/List_of_HTTP_header_fields)
- [`Cloudflare HTTP headers — Cloudflare Docs`](https://developers.cloudflare.com/fundamentals/reference/http-headers/)
- [`HTTP headers — mdn docs`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers)
- [`HTTP Security Response Headers Cheat Sheet — OWASP Cheat Sheet Series`](https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html)