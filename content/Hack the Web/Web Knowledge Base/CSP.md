---
created: 2026-05-14
tags:
  - web_knowledge_base
  - web_hacking
  - client-side
---
## CSP

>**Content Security Policy (CSP)** is a browser security mechanism that allows a website to explicitly define the sources from which a web page can load and execute resources (JavaScript, CSS, images, fonts, iframes, etc.).

- CSP is primarily used to mitigate attacks such as [[🛠️ XSS|Cross-Site Scripting (XSS)]]. It instructs the browser which sources are trusted for different resource types.
- The CSP is **defined on the server-side** and **enforced on the client-side**.

>[!tip] You can check if your CSP really mitigates XSS vulnerabilities using the [`CSP Evaluator`](http://csp-evaluator.withgoogle.com/).

>[!note]+ CSP vs. SOP
> CSP operates alongside with [[SOP|Same-Origin Policy (SOP)]].
> 
> - The [[SOP]] isolates origins from each other. 
> - CSP restricts what a page itself is allowed to load or execute.

## `Content-Security-Policy` HTTP header and CSP directives

- CSP is implemented through the [`Content-Security-Policy`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy) HTTP response header. The header is **defined on the back-end** and included in all responses from the server. 
- The header contains one or more **CSP directives**, separated by semicolons. Each directive controls a different resource type or behavior.

>[!example]+
> ```http
> Content-Security-Policy: default-src 'self'; script-src 'self' https://trusted.example.com
> ```
> 
> - `default-src` sets a default policy used by all resources unless specified otherwise. In the above example, by default, resources can be loaded only from the same origin (`'self'`).
> - `script-src` explicitly defines the sources from where scripts can be loaded. In this case, scripts can be loaded from the same origin (`'self'`) or `https://trusted.example.com`. 

>[!important] CSP operates on the **deny by default** principle: resources are blocked unless explicitly allowed.

- The `Content-Security-Policy` header can be set on **any response**, whether it's HTML, CSS, or JS, through it's most meaningful on HTML documents.

>[!note] Multiple `Content-Security-Policy` headers in the same response are **valid**. The browser evaluates the *intersection* of all policies and enforces *the most restrictive combination*.

- When the browser encounters a resource request (triggered by `<script>`, `<img>`, `fetch()`, `<iframe>`, `<style>`, etc.), it processes it as follows:
	1. Identify the resource type (script, image, style, worker, frame, etc.).
	2. Locate the most specific applicable directive (`script-src`, `img-src`, etc.).
	3. If no type-specific directive exists, fall back to `default-src`.
	4. Evaluate each source expression in the directive against the resource URL (scheme, host, port).
	5. For inline scripts and styles, check for a matching nonce or hash.
	6. If no expression matches — **block**.
	7. Log a violation to the browser console and, if configured, send a violation report to the `report-uri` or `report-to` endpoint.
### List of CSP directives

>[!important] If a specific directive (e.g., `script-src`) is absent, the browser falls back to `default-src`. If `default-src` is also absent, the resource type is unrestricted (no CSP is enforced).

>[!note] Not all directives fall back to `default-src`. `form-action`, `frame-ancestors`, `base-uri`, and `navigate-to` do **not** inherit from `default-src`. A policy with `default-src 'self'` does not restrict form submissions unless `form-action` is also set explicitly.

| Directive                   | Controls                                                                                                                                            |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| `default-src`               | Fallback for all resource types not explicitly covered (except `form-action`, `frame-ancestors`, `base-uri`, and `navigate-to`); commonly `'self'`. |
| `script-src`                | JavaScript loading and execution (external, inline, `eval`).                                                                                        |
| `script-src-elem`           | `<script>` elements specifically (not event handlers); can override `script-src`.                                                                   |
| `script-src-attr`           | Inline event handlers (`onclick`, `onerror`, etc.).                                                                                                 |
| `style-src`                 | CSS stylesheets (external and inline).                                                                                                              |
| `style-src-elem`            | `<style>` elements and `<link rel="stylesheet">`.                                                                                                   |
| ``img-src``                 | `<img>`, `background-image`, CSS `url()`.                                                                                                           |
| `connect-src`               | `fetch()`, `XMLHttpRequest`, `WebSocket`, `EventSource`.                                                                                            |
| ``font-src``                | Web fonts (`@font-face`).                                                                                                                           |
| `media-src`                 | `<audio>`, `<video>`.                                                                                                                               |
| `object-src`                | `<object>`, `<embed>`, `<applet>`; should always be `'none'`.                                                                                       |
| `frame-src`                 | `<iframe>` and `<frame>` sources.                                                                                                                   |
| `child-src`                 | Workers and frames (deprecated in favor of `frame-src` + `worker-src`).                                                                             |
| `worker-src`                | `Worker`, `SharedWorker`, `ServiceWorker` scripts.                                                                                                  |
| `frame-ancestors`           | Which origins may embed this page via `<iframe>`, `<object>`, `<embed>`.                                                                            |
| `form-action`               | URLs that can be used as form submission targets (`<form action="">`).                                                                              |
| `base-uri`                  | `<base href="">` element.                                                                                                                           |
| `navigate-to`               | Navigation targets (`window.location`, `<a href>`, redirects).                                                                                      |
| `manifest-src`              | Web App Manifest files.                                                                                                                             |
| `prefetch-src`              | Prefetch and prerender requests.                                                                                                                    |
| `sandbox`                   | Enables sandboxing restrictions on the page (like `<iframe sandbox>`).                                                                              |
| `upgrade-insecure-requests` | Instructs browser to upgrade HTTP to HTTPS (enforces HTTPS without breaking mixed content).                                                         |
| `block-all-mixed-content`   | Blocks HTTP resources on HTTPS pages (breaks mixed content).                                                                                        |
| `report-uri`                | Deprecated in CSP Level 3; URL to `POST` violation reports. `report-to` should be used instead.                                                     |
| `report-to`                 | Reporting group name per Reporting API (CSP Level 3 replacement for `report-uri`).                                                                  |
### Source expressions

- Each directive accepts a space-separated list of **source expressions** that define from where the given type of resource can be loaded.
- CSP sources can be specified in several ways:
	- **Keywords**
	- **Host sources** (domains)
	- **Schemes** (protocols)
	- **Nonces and hashes** (only for scripts and styles)
	- **Special values**

### Keywords

- Keywords are quoted literals that represent special policy values. 
- They must be written with *single quotes*.

| Keyword              | Description                                                                                                                                              |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `'self'`             | Same origin only (identical scheme, host, and port).                                                                                                     |
| `'none'`             | Deny all sources for this directive.                                                                                                                     |
| `'unsafe-inline'`    | Permits inline scripts/styles (in `<script>`, `onclick`, `<style>`, `style=""`); weakens security, discouraged.                                          |
| `'unsafe-eval'`      | Permits `eval()`, `Function()`, `setTimeout(string)`, `setInterval(string)`, and similar methods that can execute code from strings; discouraged.        |
| `'strict-dynamic'`   | Allows scripts loaded by a nonce or hash-signed script to load other scripts dynamically, ignoring the list of allowed host sources (since CSP Level 3). |
| `'unsafe-hashes'`    | Permits inline event handlers (and styles) whose hash appears in the policy.                                                                             |
| `'report-sample'`    | Includes first 40 characters of violating content in violation reports.                                                                                  |
| `'wasm-unsafe-eval'` | Permits WebAssembly execution; needed when blocking `unsafe-eval` but still suing WASM.                                                                  |

>[!example]+
> ```HTTP
> Content-Security-Policy: script-src 'self'
> ```

>[!important]
>`'self'` is safer than wildcards because it restricts to the exact origin. Wildcards (`*` or `*.example.com`) can be abused in case of subdomain takeover.

### Host sources

- Host sources specify the exact domain names and optionally port numbers from where resources can be loaded. 

- Wildcards are supported but should be used carefully:
    - `*` allows any origin (except when used with credentials).
    - `*.example.com` allows any subdomain of example.com.
    - `https://*.example.com` allows any subdomain over HTTPS.


>[!example]+
> - Only scripts from this exact host:
> 
> ```http
> Content-Security-Policy: script-src https://cdn.example.com
> ```
> 
> - Any subdomain over HTTPS:
> 
> ```http
> Content-Security-Policy: script-src https://*.example.com
> ```
> 
> - Matches both `http://` and `https://`:
> 
> ```http
> Content-Security-Policy: script-src example.com
> ```
> 
> - Only resources from this exact path prefix:
> 
> ```http 
> Content-Security-Policy: script-src https://cdn.example.com/scripts/
> ```

### Schemes

- Scheme-based sources permit entire protocol families.

>[!example]+
> - Allow images over **any HTTPS origin**:
> 
> ```http
> Content-Security-Policy: img-src https:
> ```
> 
> - Allow scripts from self or any HTTPS origin:
> 
> ```http
> Content-Security-Policy: script-src 'self' https:
> ```
> 
> - `data:` scheme — allows inline Base64-encoded content:
> 
> ```http
> Content-Security-Policy: img-src data:
> ```

- `data:` in `script-src` → equivalent to `unsafe-inline`; any `<script src="data:...">` executes.
- `blob:` in `script-src` → a script can create a Blob from arbitrary JS text and execute it via `URL.createObjectURL()`.
- `https:` in `script-src` → permits loading scripts from any HTTPS origin — functionally useless as a restriction.
### Nonces

>A **nonce** (number used once) in the context of CSP is a cryptographically random, Base64-encoded string generated server-side per page load.

- In CSP, nonces can be specified as sources.
- The server generates a fresh random nonce for every response. It includes that value in two places:
	1. The `Content-Security-Policy` header: `script-src 'nonce-{value}'`.
	2. The `nonce` attribute of each trusted `<script>` tag: `<script nonce="{value}">`.

>[!example]+
> ```http
> Content-Security-Policy: script-src 'nonce-rAnd0mStr1ng9f3f'
> ```
> - Executes — nonce matches:
> ```html
> <script nonce="rAnd0mStr1ng9f3f">
>     initApp();
> </script>
> ```
> 
> - Blocked — no nonce attribute:
> ```html
> <script>
>     alert(document.cookie);
> </script>
> ```
> 
> - Blocked — wrong nonce value:
> ```html
> <script nonce="attacker-controlled">
>     alert(document.domain);
> </script>
> ```
> 
> - When an attacker injects `<script>alert(1)</script>` into the page, the injected element has no `nonce` attribute. 
> - The browser checks the policy — `'nonce-rAnd0mStr1ng9f3f'` is required — and blocks execution.

>[!important] The attacker cannot guess or reconstruct the nonce if it is generated with sufficient entropy (128+ bits is standard) and regenerated on every request.

## `Content-Security-Policy-Report-Only` HTTP header

- The [`Content-Security-Policy-Report-Only`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy-Report-Only) response header is used to *monitor* CSP violations and their effects, but does not actually enforce the restrictions. 

>[!example]+
> ```http
> Content-Security-Policy-Report-Only: default-src 'self'; report-to /csp-violations
> ```
 
- The header must specify where to send violation reports using the [`report-to`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/report-to) directive. If not specified, the header won't have any effect.

>[!note] The `Content-Security-Policy-Report-Only` header supports all `Content-Security-Policy` directives except `sandbox`, which is ignored.

- The two headers, `Content-Security-Policy` and `Content-Security-Policy-Report-Only`, are often used together. The enforce header holds the production policy; the report-only header tests a candidate policy in parallel:

```http
Content-Security-Policy: default-src 'self'; script-src 'self'
Content-Security-Policy-Report-Only: default-src 'self'; script-src 'self' 'strict-dynamic'; report-uri /csp-test
```

>[!important]+ CSP can also be declared in the HTML `<head>`, using the  `<meta http-equiv="Content-Security-Policy">` tag
> ```html
> <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'">
> ```
> 
> This method has significant limitations:
> - Cannot use `report-uri` or `report-to` directives (no violation reporting).
> - Processed _after_ HTML parsing has already begun — resources referenced before the `<meta>` tag are not covered.
> - Cannot set `frame-ancestors` (framing control is ignored).
> - If both the header and tag are present, the header takes precedence.


## References

- [`Content Security Policy Cheat Sheet — OWASP Cheat Sheets`](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html)
- [`Content Security Policy — PortSwigger`](https://portswigger.net/web-security/cross-site-scripting/content-security-policy)

- [`CSP Evaluator`](http://csp-evaluator.withgoogle.com/)
- [`Content-Security-Policy — mdn web docs`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy)
- [`Content-Security-Policy-Report-Only — mdn web docs`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy-Report-Only)
- [`Content Security Policy — content-security-policy.com`](https://content-security-policy.com/)
## Appendix A: CSP levels

Content Security Policy (CSP) has evolved through several levels — commonly referred to as **CSP Level 1, Level 2, and Level 3** — each adding new features, directives, or improvements to the policy language and enforcement capabilities.

- **CSP Level 1 (CSP 1.0)** — 2012, the original CSP specification
	- Basic support in modern browsers.
	- Features:
		- Fundamental directives like `default-src`, `script-src`, `style-src`, `img-src`, `connect-src`, `font-src`, `object-src`, `media-src`, and `frame-src`.
		- Basic protections against XSS and data injection by restricting resource loading origins.
		- Support for `'self'`, `'none'`, `'unsafe-inline'`, and `'unsafe-eval'` keywords.
		- Reporting via `report-uri` directive to send violation reports.
	- Limitations:
		- Limited granularity in specifying resource types.
		- No support for some finer controls like restricting form actions or framing ancestors.
		- `report-uri` mechanism had some limitations, no support for newer reporting methods.
		- No explicit support for controlling workers or advanced framing controls.

- **CSP Level 2 (CSP 2.0)** — 2014, improvement over Level 1.
	- Widely supported in modern browsers; often considered the _de facto_ standard for CSP.
	- Features:
		- New directives: `child-src`, `frame-ancestors`, `form-action`, `manifest-src`, `sandbox`.
		- Enhanced reporting: ability to separate enforcement and reporting with `Content-Security-Policy-Report-Only` and `Content-Security-Policy` headers.
		- More granular controls: separated `child-src` from `frame-src` (although `frame-src` still supported for compatibility).
		- Support for CSP **nonces** and **hashes**.
	- Limitations:
		- `report-uri` still used, which is now deprecated in favor of `report-to`.

- **CSP Level 3 (CSP 3.0)** — current draft standard
	- Final recommendation published by W3C.
	- Partial to full support in modern browsers like Firefox (from version ~58+), Chrome and Edge (from version ~79+), Safari partial support; some directives or features may have varied support and require fallback considerations.
	- Features:
		- New directives: `worder-src`, `navigate-to`, `prefetch-src`, `report-to` (replaces the deprecated `report-uri`)
		- Undeprecated `frame-src` (was deprecated in Level 2) with modified behavior.
		- Refined URL matching (now `http://example.com:80` matches `https://example.com:443`).
		- Introduction of `'strict-dynamic'` keyword for scripts.
		- Fully aligned with the `FETCH` specification (used in Service Workers); improved resource loading and consistent security policy enforcement.

>[!note] Websites primarily use CSP Level 2 features today, as they are well supported and provide solid security controls.


