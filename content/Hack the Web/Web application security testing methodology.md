---
created: 2026-09-26
updated: 2026-10-04
tags:
  - methodology
  - web_hacking
proofread: no
---

>[!tip]+ If a payload is filtered by a WAF, try obfuscation and encoding. See [[🛠️ Obfuscating attacks using encoding]].

## Web application security testing methodology

>[!note]+ Each entry consists of:
>- **Cue** — an observable signal or behavior that hints at a weakness.
>- **Check** — what to probe once the cue appears, and what a positive result proves.
>- **→ Reference** — the note that covers the technique in depth.

>[!note] Work through the categories as a checklist, not a strict sequence.
## Enumeration

>[!important] Enumeration is iterative. Every endpoint, parameter, header, or credential you discover should be passed back into earlier enumeration stages.

>[!note] See [[Web discovery and enumeration methodology]].

- Fingerprint the technology stack: web server, programming language, frameworks, any third-party components. 
	- → [[Fingerprinting]].
- Walk the application manually recording requests and responses with a web proxy; note parameters, headers, and methods for each endpoint you encounter.
- Run a web crawler to enumerate linked pages in the application, then fuzz possible directories and files with a wordlist.
	- -> [[Directory and file enumeration]].
- Enumerate user-controlled parameters the application accepts and processes.
	- -> [[Fuzzing parameters]].
## Configuration and deployment

>[!note] See [`WSTG-CONF — OWASP WSTG`](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/02-Configuration_and_Deployment_Management_Testing/).

>[!important] A web application's infrastructure is only as secure as its weakest, most poorly configured element.

### Known vulnerabilities in the stack

- **An identified server, framework, language, or library version**
	- Search public advisories and exploit databases for known vulnerabilities affecting the exact versions. 
	- → [[Fingerprinting]], [[🛠️ Searching for known vulnerabilities]].
### Platform and server (mis)configuration

- **`Server`, `X-Powered-By`, `X-AspNet-Version` response headers**
	- Read the headers to identify the web server, framework, and language. 
	- → [[Fingerprinting]].

- **Default framework/sample pages left in production**
	- Default framework pages (welcome pages in Django, Laravel, Rails), unmodified starter `index.html`, sample/test scripts (`phpinfo.php`, `test.php`), CMS installation scripts (`wp-admin/install.php`) often expose the exact framework version and other details, sometimes secrets. 
	- -> [[🛠️ Sensitive information disclosure]].

- **Framework debug consoles**
	- Django `DEBUG=True` error pages, the Werkzeug debugger (`/console`), Rails development-mode errors — may leak fragments of application source code and configuration, and sometimes be abused for code execution.
	- -> [[🛠️ Sensitive information disclosure]].

- **Auto-generated API documentation reachable in production**
	- // rephrase
	- Swagger UI/Open API documentation (`/swagger-ui`, `/swagger.json`, `/v2/api-docs`), GraphQL Playground/GraphiQL, or gRPC reflection expose the full API schema, including admin-only operations; some execute requests directly.
	- -> [[API testing]].

- **Directory listings**
	- Automatically generated directory and file listing pages may expose source code, configuration, and hidden endpoints.
	- → [[🛠️ Sensitive information disclosure]].

- **Verbose errors**
	- Verbose errors and stack traces caused by 

- **Auto-generated API documentation reachable in production**
	- Swagger UI/OpenAPI (`/swagger-ui`, `/swagger.json`, `/v2/api-docs`), GraphQL Playground/GraphiQL, or gRPC reflection often expose the full schema, including undocumented or admin-only operations, and some run requests directly without extra authorization. 
	- → [[API testing]].

- **Directory listing enabled**
	- An auto-index page may expose source, backups, and config you were never meant to browse. 
	- → [[🛠️ Sensitive information disclosure]].
### Admin and management interfaces

- **Reachable admin panels and management consoles**
	- `/admin`, `/manager/html` (Tomcat), `/console`, database admins (`/phpmyadmin`, `/adminer`), CI and monitoring dashboards; try default credentials, test for credential brute-force attacks, attempt to bypass access controls.
	- → [[Directory and file enumeration]].
### Sensitive and backup files

- **Backup, temporary, and unreferenced files**
	- // paraphrase
	- Backup or temporary editor flies (`index.php.bak`, `config.php~`, `.old`, `.zip`, `.tar.gz`), environment and configuration files (`.env`, `application.yml`, `web.config`, `composer.json`, `package.json`) may leak source code, configuration, credentials, and secret keys. 
	- -> [[🛠️ Sensitive information disclosure]].

- **Alternative file extensions**
	- Request a file with a different extensions (e.g., `.xml` -> `.json`, `.php` -> `.phps`) to check if the server returns source code or a different representation potentially containing additional, sensitive data. 
	- -> [[🛠️ Sensitive information disclosure]].
### HTTP methods

- **`OPTIONS` lists verbs beyond `GET`/`POST`; `PUT`, `DELETE`, `TRACE`, or `PATCH` accepted**
	- Send an `OPTIONS` request to check if the server returns accepted methods. `PUT` may write a file into the web root, `DELETE` may remove resources, `TRACE` may enable cross-site tracing.
### Transport security and headers

>[!note] See [`WSTG-CRYP — OWASP WSTG`](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/09-Testing_for_Weak_Cryptography/) for transport and cryptography tests.

- **Missing HSTS (`Strict-Transport-Security`)**
	- [`Strict-Transport-Security`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Strict-Transport-Security) (HSTS) enforces communication exclusively over HTTPS; without it, a connection can be downgraded to HTTP and potentially intercepted (Man-in-the-Middle attacks).
	- -> [[🛠️ Misconfiguration]].

- **Sensitive information sent over HTTP (mixed content)**
	- // paraphrase and extend
	- Check login or other sensitive requests are sent only over HTTPS.

- **Weak TLS configuration**
	- // paraphrase
	- Outdated protocols (SSLv3, TLS 1.0/1.1), weak ciphers, expired or misissued certificates. Scan with an SSL/TLS analyzer; scan with an SSL/TLS analyzer.

- **Permissive or missing `Content-Security-Policy`**
	- // paraphrase
	- A weak CSP means the browser enforces fewer protections, so client-side attacks such as XSS and clickjacking stand a greater chance of success. 
	- → [[CSP]].

- **Other missing security headers**
	- `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`, framing controls (`X-Frame-Options` / `frame-ancestors`). 
	- → [[🛠️ HTTP header reference]].

### Cloud and infrastructure misconfiguration

- **Dangling DNS pointing at a deprovisioned service**
	- A `CNAME` to an unclaimed S3 bucket, GitHub Pages, Azure, or Heroku app lets you register the target and serve content from the victim's subdomain.
	- -> [[🛠️ Subdomain takeover]].

- **Publicly readable cloud storage**
	- // paraphrase and extend
	- Guess/enumerate cloud storage containers (e.g., S3 buckets in AWS, blob containers in Azure, Google storage buckets in GCP) and check for misconfigured access controls
	- -> [[🛠️ Enumerating S3 buckets]].
## Information disclosure

>[!note] See [`WSTG-INFO — OWASP WSTG`](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/) and [`WSTG-ERRH — OWASP WSTG`](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/08-Testing_for_Error_Handling/).
### Search engines and meta-files

- **`robots.txt`, `sitemap.xml`, `security.txt`, `.well-known/`**
	- Check for known files that may contain information useful during security testing, such as hidden or unreferenced endpoints. 
	- → [[robots.txt and other interesting files]].
- **Indexed content and cached pages**
	- // paraphrase
	- Use search-engine operators (`site:`, `inurl:`, `filetype:`) to search for indexed forgotten pages, exposed documents, and leaked credentials. 
	- → [[🛠️ Searching the web]].

### Sensitive information in page content

- **HTML and JavaScript comments, hidden form fields, debug parameters**
	-  // extend and paraphrase
	- Analyze application source HTML and JavaScript; look for leaked credentials and any other valuable information. 
	- → [[🛠️ Sensitive information disclosure]].

- **Secrets in client-side JavaScript**
	- API keys, cloud tokens, internal URLs, and hardcoded credentials in bundled scripts and source maps. Pull every `.js` file and the `.map` files beside it, then grep for secrets. 
	- → [[🛠️ Sensitive information disclosure]].

### Error handling and stack traces

- **Verbose errors or stack traces from malformed input, type juggling, or fuzzing**
	- Send unexpected input (wrong types, oversized values, broken syntax) and watch for errors. 
	- A verbose error message or a stack trace may leak the exact framework, version, and often fragments of code or configuration.
	- → [[🛠️ Sensitive information disclosure]].
### Exposed version-control and editor artifacts

- **`.git/`, `.svn/`, `.hg/`, `.DS_Store`, editor swap files (`.swp`, `~`)**
	- A deployed `.git/` directory or an editor swap file lets you reconstruct the source and recover secrets from history. Request these paths directly, then download and rebuild the source to read credentials and find further vulnerabilities offline. 
	- → [[🛠️ Sensitive information disclosure]].

## Authentication

>[!note] See [`WSTG-ATHN — OWASP WSTG`](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/04-Authentication_Testing/) and [`WSTG-IDNT — OWASP WSTG`](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/03-Identity_Management_Testing/).

- Authentication is the process of verifying the user identity. 
- Test every authentication mechanism the application exposes — password-based login, multi-factor authentication flows, OAuth & OIDC — and related functionality — password reset, `Remember me`, self-registration.
### Identity and roles

- **Roles and privileges**
	- Enumerate the roles and privileges the application defines to understand what to escalate toward.
	- Search documentation, if any, attempt to find any clues from the traffic, probe relevant parameters:
		- Cookie or token values (`role=admin`, `isAdmin=true`).
		- Account fields (`"role": "manager"`).
		- Hidden directories (`/admin`, `/mod`, `/backups`).
		- Well-known account names (`admin`, `backup`, `test`, `service`).

### Registration and account provisioning

- Ask who can get an account and on what terms:
	- Can anyone register, or does a human vet each request?
	- Can one identity register multiple times?
	- Can a registrant choose a role or permission level?
	- What proof of identity is required, and is it verified?
- **Open self-registration**
	- Where anyone can create an account, test which role the new account receives and which extra fields the endpoint honors. Submitting unexpected fields such as `role` or `isAdmin` can grant elevated privileges; this chains into mass assignment. → [[API testing#Mass assignment vulnerabilities]].
- **Username enumeration via registration**
	- A "username already taken" message confirms which accounts exist. Use the confirmed list for brute-force and credential stuffing. → [[🛠️ Vulnerabilities in password-based login#Username enumeration]].
- **Predictable username format (`first.last`, sequential IDs, email local-part)**
	- A guessable scheme hands you half of every credential pair and widens enumeration. 
	- → [[🛠️ Vulnerabilities in password-based login#Username enumeration]].

### Password-based login

- **Login responses that differ by username or response time**
	- Compare responses for valid and invalid usernames. A different message, status code, response length, or timing lets you enumerate accounts, and that list makes brute-force and credential stuffing practical. 
	- → [[🛠️ Vulnerabilities in password-based login]].
- **Default or weak credentials**
	- Test vendor defaults (`admin:admin`, `root:root`) and common passwords against known accounts before brute-forcing. 
	- → [[🛠️ Vulnerabilities in password-based login#Password brute-force]].
- **Weak or missing lockout and rate limiting**
	- Probe how many attempts a form allows and whether lockout can be bypassed. Flawed lockout opens the door to brute-force, security-question guessing, and OTP guessing, and some lockout logic can be turned into a denial of service.
	- Test header-based IP spoofing (`X-Forwarded-For`) to reset per-IP counters.
	- → [[🛠️ Vulnerabilities in password-based login#Flawed brute-force protection]].
- **Weak password policy**
	- Register or change a password to a trivial value to confirm the policy accepts short or common passwords, which widens any brute-force. 
	- → [[🛠️ Vulnerabilities in password-based login#Password brute-force]].

### Bypassing the authentication schema

- **Post-login pages reachable without a valid session**
	- Request authenticated pages directly, replay or tamper with session tokens, and force-browse past the login step. The objective is to reach authenticated functionality without completing login. 
- **Parameters that control authentication state (`authenticated=false`, `step=2`)**
	- Tamper with hidden fields and flow parameters to skip the credential check. → [[🛠️ Logic flaws]].

### Remember-me and alternative flows

- **Persistent-login cookies ("remember me")**
	- Decode the cookie and test whether it carries a predictable or forgeable value (username, static hash) instead of an unguessable token. A weak persistent cookie is a long-lived account takeover. → [`WSTG-ATHN-05 — OWASP WSTG`](https://wstg.owasp.org/latest/4-Web_Application_Security_Testing/04-Authentication/05-Vulnerable_Remember_Password/).
- **Sensitive data cached by the browser**
	- Check `Cache-Control` and `Pragma` on authenticated responses, and whether the back button reveals data after logout.
- **Weaker authentication on a secondary channel**
	- Mobile sites, legacy endpoints, or an API login may enforce fewer controls than the main form. Test each entry point.

### Password reset and change

- **Password reset and change-password flows**
	- These protect the account less carefully than the login form does. Test reset tokens for predictability and brute-forceability, and the reset logic for steps that can be reordered or skipped to take over an account. → [[🛠️ Other authentication vulnerabilities]].
- **The `Host` header reflected into a reset link**
	- If the reset email builds its URL from the `Host` header, poison it to deliver the token to your server. 
	- → [[🛠️ Host header injection]].
- **Weak security questions**
	- Guessable or OSINT-recoverable answers bypass the knowledge check.

### Multi-factor authentication

- **A one-time code or second factor requested after the password**
	- Where a second step follows the password, probe whether it can be skipped, brute-forced, or downgraded. The objective is to reach the authenticated state without completing the second factor — by tampering with the multi-step flow, reusing or guessing codes, or forcing the application back to single-factor login. → [[🛠️ Vulnerabilities in MFA]].
- **Verification logic tied to a user parameter you control**
	- Change the account identifier between the password step and the code step to verify against your own factor. → [[🛠️ Vulnerabilities in MFA#Flawed two-factor verification logic]].

### OAuth 2.0 and OIDC

- **A "Sign in with…" button, `/authorize`, `/oauth`, `redirect_uri`, `state`, or `id_token`**
	- These mark a delegated-authorization flow. Walk the flow, pull the discovery document (`/.well-known/openid-configuration`), and map the attack surface. 
	- → [[OAuth attacks]].
- **A tampered `redirect_uri` is honored**
	- Point it at a domain you control to steal authorization codes or tokens. 
	- → [[OAuth attacks#Account hijacking via redirect URI]].
- **Missing or unvalidated `state`**
	- A flow without a bound `state` is CSRF-able; test for forced profile linking. 
	- → [[OAuth attacks#CSRF in the OAuth flow]].

## Authorization and access control

>[!note] See [`WSTG-ATHZ — OWASP WSTG`](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/05-Authorization_Testing/).

- Authentication proves who you are; authorization decides what you're allowed to do. Test whether the application enforces those limits on every request, not just by hiding links in the UI. Access-control flaws let a low-privileged or unauthenticated user reach another user's data or an administrator's functionality.

### Insecure direct object references

- **Object references you can change (`?id=`, `/orders/1024`, GraphQL node arguments)**
	- Where a request names a specific record, change the identifier to one you shouldn't own. If the application returns or modifies the other record without checking ownership, it has an IDOR. → [[IDOR]].
- **Indirect, encoded, or hashed identifiers**
	- Predictable encodings (Base64, sequential hashes) are still IDOR; decode and iterate them.
	- → [[IDOR#Attack surface]].

### HTTP verb tampering

- **Access control that depends on the HTTP method**
	- Test the same endpoint with different methods to check for inconsistent access controls.
	- -> [[🛠️ HTTP verb tampering]].

### Privilege escalation and forced browsing

- **Privileged routes or functions reachable by lower-privileged roles**
	- Request administrative URLs and actions directly as a low-privileged or anonymous user. Where access is blocked, test bypasses: swap the HTTP method, add headers such as `X-Original-URL` or `X-Rewrite-URL`, or alter the path's case or encoding. The objective is to run privileged functionality without holding the required role. 
- **Horizontal access to peer accounts**
	- Reach another user's records at the same privilege tier by swapping identifiers or reusing their references. 
### Path and file access

- **A parameter names a file or path (`?file=`, `?template=`, `?lang=`, `?download=`)**
	- When input selects a file on the server, test whether `../` sequences escape the intended directory to read (or sometimes write) arbitrary files such as `/etc/passwd` or the application's own source. → [[Path traversal]].
	- Defeat filters with URL encoding, nested sequences (`....//`), absolute paths, and required prefix or extension tricks.

## Session management

>[!note] See [`WSTG-SESS — OWASP WSTG`](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/06-Session_Management_Testing/).

- After login, an application tracks the user with a session token, usually a cookie. Test how that token is generated, transmitted, and retired. A weak session mechanism lets an attacker steal, fixate, or forge a session and act as the victim.

### Session tokens and cookies

- **Session cookie attributes (`HttpOnly`, `Secure`, `SameSite`)**
	- A missing `HttpOnly` lets script read the token; a missing `Secure` exposes it over HTTP; a weak `SameSite` exposes it to cross-site requests. 
	- → [[Session management vulnerabilities#Cookie attributes]].
- **Predictable or short session tokens**
	- Collect many tokens and analyze them for structure, sequence, or weak entropy. A guessable token is a hijacked session. 
	- → [[Session management vulnerabilities#Session identifier strength]].
- **No token rotation on login or privilege change**
	- If the pre-login token stays valid after authentication, the application is open to session fixation. 
	- → [[Session management vulnerabilities#Session fixation]].
- **Session not invalidated on logout or timeout**
	- Confirm that logout and idle timeout kill the session server-side, not just in the browser. 
	- → [[Session management vulnerabilities#Session lifecycle]].
- **Session tokens exposed in URLs, logs, or referers**
	- Tokens in query strings leak through browser history, proxies, and the `Referer` header.

### JWT

- **A JWT (`eyJ…`) in a cookie or `Authorization` header**
	- A value beginning with `eyJ` is a Base64URL-encoded JWT. Decode the header and test whether the signature is actually enforced: `alg:none`, a weak or guessable HMAC secret, or an RS256→HS256 confusion can let you forge claims such as a different user ID or role. 
	- → [[JWT attacks]], [[🛠️ JWT attacks cheat sheet]].

### Cross-site request forgery

- **A state-changing request carries no unpredictable token**
	- If a request that changes state (transfer funds, change email) is accepted without a per-request anti-CSRF token, a malicious page can submit it on behalf of a logged-in victim. Confirm that a forged cross-site request is honored with the victim's session. 
	- → [[CSRF]], [[CSRF cheat sheet]].
- **A CSRF token that isn't bound to the session or isn't validated**
	- Drop the token, submit an empty value, reuse another user's token, or change the request method to test whether validation is real. 
	- → [[CSRF cheat sheet]].

## Injection and input handling

>[!note] See [`WSTG-INPV — OWASP WSTG`](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/).

- Injection happens when user input is interpreted as code or commands by a downstream interpreter — a database, a shell, a template engine, an XML or LDAP parser. The method is the same for each: supply input containing that interpreter's syntax, then watch for a change in behavior, an error, or a timing difference that proves the input crossed from data into code.

### Database injection

- **A quote breaks the page; boolean or time-based payloads change the response; database errors appear**
	- Inject SQL metacharacters into a parameter and observe. A changed result set, a conditional true/false difference, a deliberate time delay, or a database error all indicate the input reaches an SQL query. The objective ranges from extracting data, through bypassing authentication, to reaching the host. 
	- → [[SQL injection]], [[SQL injection cheat sheet]], [[sqlmap]].
- **A JSON or NoSQL back end where operators such as `$ne` or `$gt` change behavior**
	- Against document stores such as MongoDB, submit query operators in place of plain values. If `{"$ne": null}` alters the result, the input is interpreted as query structure, which enables authentication bypass and data extraction. 
	- → [[NoSQL injection]].

### Command and code execution

- **Input passed to a shell (ping, host lookup, file conversion); a delay on `;`, `|`, `&&`, or `` ` ``**
	- Where the application shells out to a system command, inject shell separators and test for command execution. It's often blind, confirmed with a deliberate delay or an out-of-band callback. A finding yields arbitrary OS commands on the server. 
	- → [[OS command injection]].
- **`{{7*7}}` renders as `49` after the server processes it**
	- When input is embedded in a server-side template, template syntax is evaluated. Confirm the engine with an arithmetic probe, identify it from the result, then escalate engine-specific payloads toward remote code execution. 
	- → [[SSTI]].
- **Input reflected into a page with server-side includes enabled (`.shtml`)**
	- Inject SSI directives such as `<!--#exec cmd="id"-->` and check whether the server runs them. A positive result is command execution through the templating layer.

### Directory, XML, and query-language injection

- **A directory-backed login or search where `*` or `)(` changes the results**
	- Applications that query LDAP build filters from input. Injecting filter metacharacters can bypass authentication or enumerate directory entries. 
	- → [[🛠️ LDAP injection]].
- **An XML body or SOAP endpoint, or a `.docx`/`.svg`/`Content-Type` you can switch to XML**
	- Where the server parses XML, test whether it resolves external entities. XXE can read local files, drive server-side requests, and exfiltrate data out-of-band. 
	- → [[XXE injection]], [[XXE injection cheat sheet]].
- **A filter parameter against XML data (XPath), or mail headers you can break (`\r\n` into SMTP/IMAP)**
	- Inject the relevant metacharacters to bypass filters or forge commands.

### Server-side request forgery

- **A parameter holds a URL or host (webhooks, link previews, PDF or image fetchers)**
	- When the server fetches a URL you control, test whether you can point it at internal addresses or cloud metadata endpoints unreachable from outside. This is SSRF. 
	- → [[SSRF]].
	- Probe cloud metadata (`http://169.254.169.254/`), loopback (`http://127.0.0.1/`), and internal ranges.
	- Confirm blind SSRF with an out-of-band callback, then try bypasses: alternate encodings, open redirects, and DNS rebinding.

### Object and parameter manipulation

- **A serialized object in the traffic (`rO0`, `O:`, ViewState, Base64-encoded objects)**
	- Recognizable serialized blobs mean the server deserializes client-supplied data. Tampering with the object, or crafting a gadget chain, can alter application logic or reach remote code execution. 
	- → [[Insecure Deserialization]].
- **User-controlled keys merged into objects (`__proto__`, `constructor`, `prototype`)**
	- Where the application merges user input into objects by key, test whether you can reach the prototype and inject properties that change unrelated behavior, on the client or the server. 
	- → [[🛠️ Prototype pollution]].
- **A duplicated parameter, or one echoed into an internal request**
	- Supplying a parameter twice, or in a different location, can split or pollute how the front end and back end interpret it, steering the application into unintended logic. 
	- → [[API testing#Server-side parameter pollution]].

## Business logic and workflows

>[!note] See [`WSTG-BUSL — OWASP WSTG`](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/10-Business_Logic_Testing/).

- Business-logic flaws are valid-looking requests that break the application's assumptions about how its features are meant to be used. There's no malformed syntax to detect — understand the intended workflow first, then test what happens when you deviate from it.

### Workflow and data-validation abuse

- **Multi-step flows that assume an order, price, or quantity**
	- Map a workflow (checkout, transfer, approval), then violate its assumptions: send a negative quantity, a tampered price, a different currency, or requests out of sequence. The objective is to reach a state the designers assumed was impossible. 
	- → [[🛠️ Logic flaws]].
- **Client-side-only validation of business rules**
	- Replay the request directly, past the UI, to confirm the server re-checks limits, prices, and permissions. 
	- → [[🛠️ Logic flaws#Examples of logic flaws]].
- **Payment and checkout logic**
	- Test negative or zero amounts, currency and rounding handling, coupon stacking, and whether an order is confirmed before payment clears. 
	- → [[🛠️ Logic flaws]].

### Limits and race conditions

- **Single-use or rate-limited actions (coupons, withdrawals, votes, OTP checks)**
	- Where an action is meant to happen once, send many requests at the same instant. If the check and the use aren't atomic, concurrent requests slip through the window — redeeming a coupon twice, overdrawing a balance. 
	- → [[🛠️ Race conditions]].
- **A function usable more times than intended**
	- Test whether per-account or per-session limits reset, or can be reused across sessions. 
	- → [[🛠️ Logic flaws#Logic flaws checklist]].

### File upload

- **Any upload field (avatar, document, import)**
	- Test what the upload accepts and where the file lands. Bypassing validation can store a web shell for code execution, a crafted SVG for stored XSS, or a malicious document for XXE. 
	- → [[File upload]].
- **Upload filtering you can bypass (extension, `Content-Type`, magic bytes)**
	- Fuzz allowed extensions, double extensions, null bytes, and MIME mismatches to slip an executable file past the filter. 
	- → [[File upload#Server-side filtering bypass]].

## Client-side

>[!note] See [`WSTG-CLNT — OWASP WSTG`](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/11-Client-side_Testing/).

- Client-side vulnerabilities run in the victim's browser rather than on the server. Test how the application reflects, stores, and processes input in HTML and JavaScript, and how it handles redirects and cross-origin messages.

### Cross-site scripting

- **Input reflected or stored into HTML or JavaScript**
	- Inject a marker and check whether it appears unescaped in the response or in a later page. Unescaped output runs script in the victim's session: reflected XSS from a crafted link, stored XSS from persisted content. 
	- → [[XSS]], [[🛠️ XSS cheat sheet]].
- **JavaScript that reads a source into a dangerous sink (`location`, `postMessage`, `innerHTML`, `document.cookie`)**
	- Trace client-side data from where it enters (the URL, a message) to where it's used (writing HTML, redirecting). A tainted path to a sink causes DOM-based XSS without the server ever seeing the payload. 
	- → [[🛠️ DOM-based vulnerabilities]].
- **HTML or CSS injected without script**
	- Unescaped markup allows HTML injection and dangling-markup data theft; injected CSS can read attribute values and keystrokes.
- **Client-side code that builds a URL, script `src`, or resource path from input**
	- Test whether you can redirect a resource load to an attacker-controlled host. This is client-side resource manipulation. 
	- → [[🛠️ DOM-based vulnerabilities]].
- **A `<script src>` pointed at a JSON or JSONP data endpoint**
	- Cross-site script inclusion lets a third-party page read the data the endpoint returns.

### Redirects and navigation

- **A redirect target taken from a parameter (`?url=`, `?next=`, `?returnTo=`)**
	- If the application redirects to a URL supplied in a parameter, test whether it sends the user to an external site. This enables convincing phishing and can be chained to steal OAuth codes or tokens. → [[Open redirect]].
- **Links with `target="_blank"` and no `rel="noopener"`**
	- The opened page can rewrite the opener tab toward a phishing site. This is reverse tabnabbing.

### Cross-origin and framing

- **`Access-Control-Allow-Origin` reflects the request `Origin` with credentials**
	- If the application echoes an arbitrary `Origin` back while also allowing credentials, a malicious site can read the victim's authenticated responses cross-origin. → [[🛠️ CORS]].
- **A sensitive action can be framed (no `X-Frame-Options` or `frame-ancestors`)**
	- If the application loads in an iframe, test whether a transparent overlay tricks a victim into clicking a sensitive control they can't see. This is clickjacking. 
	- → [[🛠️ Clickjacking]].
- **WebSocket traffic (`ws://` or `wss://`)**
	- Test the handshake and the messages: inject into messages, tamper with the handshake, and check for cross-site WebSocket hijacking when the connection is authenticated by cookie alone. 
	- → [[🛠️ WebSocket vulnerabilities]].
- **`postMessage` handlers without an origin check, or sinks fed from `localStorage`/`sessionStorage`**
	- A handler that trusts any sender, or a sink fed from browser storage, can be driven cross-origin into script execution or data theft. 
	- → [[🛠️ DOM-based vulnerabilities]].

## Intermediaries and HTTP infrastructure

- Requests rarely reach the application directly — they pass through proxies, load balancers, and caches. These intermediaries make their own parsing and trust decisions, and disagreements between them and the application create a distinct class of attacks.

### Host and header trust

- **The application trusts the `Host` or `X-Forwarded-Host` header (in links, reset URLs, routing)**
	- Change the header and see whether the value is reflected into generated links or used for routing. If it is, you can poison password-reset links to point at your server or reach internal virtual hosts. 
	- → [[🛠️ Host header injection]].

### Caching

- **Caching is in play (`X-Cache`, `Age`, `Vary` headers, a CDN)**
	- Where responses are cached and shared between users, test whether an input the cache ignores (unkeyed) still changes the response. A positive result lets you poison a cached entry so other users receive attacker-controlled content.
	- → [[🛠️ Web Cache Poisoning]].
- **The cache keys on path or extension (`/account/profile.css`)**
	- Test whether appending a static-looking suffix makes the cache store a response that contains another user's private data for you to retrieve. This is web cache deception. 
	- → [[Web Cache Deception]].

### Request smuggling

- **A front end forwards to a back end over HTTP/1.1 with a `Content-Length`/`Transfer-Encoding` disagreement**
	- Where two servers parse request boundaries differently, craft a request each interprets differently to smuggle a second request, poison the next user's response, or bypass front-end controls. 
	- → [[HTTP_1.1 request smuggling]].

## APIs

>[!note] See [`WSTG-APIT — OWASP WSTG`](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/12-API_Testing/).

- APIs expose application functionality directly, often with thinner server-side rendering and their own documentation. Enumerate their endpoints and methods, then test the same vulnerability classes as the web application, plus a few specific to API design.

- **Paths like `/api/`, `/v1/`, JSON responses, or an OpenAPI/Swagger document**
	- These mark a REST-style API. Enumerate its endpoints and methods, read any specification, and test for mass assignment (binding fields the client shouldn't set) and excessive data exposure (an endpoint returning more than the UI shows). 
	- → [[API testing]].
- **A `/graphql` endpoint, or `__typename` in responses**
	- This marks a GraphQL API. Use introspection to map the schema, then test for object-level access flaws (IDOR), alias-based rate-limit bypass, and CSRF against the endpoint. 
	- → [[GraphQL attacks]].

## Attacking common applications

- Off-the-shelf applications and CMS have well-documented attack surfaces once you identify the product and version, so fingerprint first. → [[Fingerprinting]].
- **WordPress (`/wp-login.php`, `/wp-content/`)**
	- Enumerate users, plugins, and themes, then match versions to known plugin and theme vulnerabilities; test XML-RPC for amplified brute-force and SSRF. → [[WordPress]].
- **Drupal (`CHANGELOG.txt`, `/sites/default/`)**
	- Identify the core version and match it to known remote-code-execution issues such as the PHP filter module and Drupalgeddon. → [[Drupal]].
- **GitLab (`/users/sign_in`)**
	- Enumerate projects and users, then match the version to published CVEs. → [[GitLab]].

## Where to go next

- A web vulnerability is usually a foothold, not the goal. Once you have one, move into the wider engagement.
- **Remote code execution reached (via SSTI, file upload, deserialization, command injection, or SSRF→RCE)**
	- You have command execution on the server; continue with post-exploitation, upgrade to a stable shell, and pivot into the internal network. → [[🛠️ Penetration testing methodology]].
- **Credentials or tokens recovered**
	- Reuse them for credential attacks and lateral movement across the application and the network. 
	- → [[🛠️ Penetration testing methodology]].
- **New endpoints, parameters, or roles found**
	- Any new surface loops back into discovery; enumerate it. 
	- → [[Web discovery and enumeration methodology]].

## References and further reading

- [`OWASP Web Security Testing Guide — OWASP`](https://owasp.org/www-project-web-security-testing-guide/)
- [`Attack Surface Identification — OWASP WSTG`](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/04-Attack_Surface_Identification/)



- TODO:
	- Obfuscation/WAF bypass for each vulnerability