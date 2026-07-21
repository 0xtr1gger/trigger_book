---
created: 2026-05-31
---
| `#`  | Solved? | Name                                                 |  Date   |
| ---- | :-----: | ---------------------------------------------------- | :-----: |
| `1.` |   `✓`   | Web cache poisoning with an unkeyed header           | `09.06` |
| `2.` |   `✓`   | Web cache poisoning with an unkeyed cookie           | `09.06` |
| `3.` |   `✓`   | Web cache poisoning with multiple headers            | `09.06` |
| `4.` |   `✓`   | Targeted web cache poisoning using an unknown header | `10.06` |
| `5.` |   `✓`   | Web cache poisoning via an unkeyed query string      | `10.06` |
| `6.` |   `✓`   | Web cache poisoning via an unkeyed query parameter   | `10.06` |
| `7.` |   `✓`   | Parameter cloaking                                   | `11.06` |
| `8.` |   `✓`   | Web cache poisoning via a fat `GET` request          | `11.06` |
| `9.` |   `✓`   | URL normalization                                    | `11.06` |

## 1. Web cache poisoning with an unkeyed header

>[!done]

>[!note]+ Lab description
> - [`Lab: Web cache poisoning with an unkeyed header`](https://portswigger.net/web-security/web-cache-poisoning/exploiting-design-flaws/lab-web-cache-poisoning-with-an-unkeyed-header)
> - Level: #Practitioner 
> 
> This lab is vulnerable to web cache poisoning because it handles input from an unkeyed header in an unsafe way. An unsuspecting user regularly visits the site's home page. To solve this lab, poison the cache with a response that executes `alert(document.cookie)` in the visitor's browser.

### Solution

- Access the lab and find inspect server responses. Send a `GET` request to `/` to `Repeater` and add a cache buster.
- Send a request with the same cache buster twice and see the `X-Cache: hit` header in response:

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab1/1.png]]

- Change the cache buster and see `X-Cache: miss`:

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab1/2.png]]

- In this case, `X-Cache` acts as a caching oracle.

---

- Right-click on the request in HTTP proxy history -> `Extensions` -> `Param Miner` -> `Guess headers` -> `OK`:

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab1/3.png]]

- To see the output, go to `Extensions` -> `Installed` -> `Param Miner` > `Output` tab:

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab1/4.png]]

- Param Miner found an unkeyed header, `X-Forwarded-Host`:

```
Loop 0
Queued 1 attacks from 1 requests in 0 seconds
Initiating header bruteforce on 0a6c009a034c32fe80c8174c004700f4.web-security-academy.net
Identified parameter on 0a6c009a034c32fe80c8174c004700f4.web-security-academy.net: x-forwarded-host~%s.%h
```

- Go back to `Repeater` and add this header set to an arbitrary value. Send the request and search for the value in response to see if and where it's reflected:

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab1/5.png]]

- The application dynamically constructs a link to a tracking JavaScript using the value of the `X-Forwarded-Host` header:

```html
<script type="text/javascript" src="//anything/resources/js/tracking.js"></script>
```

---

- Go to your server and change the request path from `/exploit` to `/resources/js/tracking.js`.

```js
/resources/js/tracking.js
```

- Set `Content-Type` to `text/javascript`. 

```js
Content-Type: text/javascript
```

- Paste the following as a response body:

```js
alert(document.cookie)
```

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab1/6.png]]

- Then click `Store`.
---

- Go back to the `GET` request to `/` in `Repeater`. Remove the cache buster and insert your exploit server hostname as a value of the `X-Forwarded-Host` header.
- Send the request several times until you see `X-Cache: hit`.

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab1/7.png]]

- To verify the exploit is working, navigate to the main page within `30` seconds after you cached the poisoned response (`Ctrl + Shift + R` to refresh the page without hitting a previously cached benign response). You should see an alert:

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab1/8.png]]

- Keep the poisoned response cached until the lab is solved.

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab1/solved.png]]

Solved!
## 2. Web cache poisoning with an unkeyed cookie

>[!done]

>[!note]+ Lab description
> - [`Lab: Web cache poisoning with an unkeyed cookie`](https://portswigger.net/web-security/web-cache-poisoning/exploiting-design-flaws/lab-web-cache-poisoning-with-an-unkeyed-cookie)
> - Level: #Practitioner 
> 
> This lab is vulnerable to web cache poisoning because cookies aren't included in the cache key. An unsuspecting user regularly visits the site's home page. To solve this lab, poison the cache with a response that executes `alert(1)` in the visitor's browser.

### Solution

- Find a cache buster, same as in the previous lab (the `X-Cache` header).
- Then use Param Miner to `Guess cookies`. The extension finds an unkeyed `fehost` cookie:

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab2/1.png]]

- The cookie is assigned when you navigate to `/my-account`:

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab2/2.png]]

- Send a `GET` to `/` with this cookie already assigned to `Repeater`. Modify the value and see if and where it is reflected in application response:

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab2/3.png]]

- The value appears inside a `<script>` tag in response:

```html
<script>
	data = {"host":"0a3200c003bde347816dcb75001e0020.web-security-academy.net","path":"/","frontend":"anything"}
</script>
```

- Experiment with the cookie value to inject arbitrary JavaScript and achieve XSS:

```js
fehost=anything"}-alert(1)//
```

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab2/4.png]]

- Get the response cached and navigate to the page with the same cache buster using your browser. 
- See an alert:

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab2/5.png]]

- Remove the cache buster and get the response cached again. Keep it cached by repeating the same request until the lab is solved.

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab2/solved.png]]

Solved!
## 3. Web cache poisoning with multiple headers

>[!done]

>[!note]+ Lab description
> - [`Lab: Web cache poisoning with multiple headers`](https://portswigger.net/web-security/web-cache-poisoning/exploiting-design-flaws/lab-web-cache-poisoning-with-multiple-headers)
> - Level: #Practitioner 
> 
> This lab contains a web cache poisoning vulnerability that is only exploitable when you use multiple headers to craft a malicious request. A user visits the home page roughly once a minute. To solve this lab, poison the cache with a response that executes `alert(document.cookie)` in the visitor's browser.

### Solution

- Browse the application. 
- The cache oracle is the same (the `X-Cache` header).
- Inspect the HTTP history and find a `GET` request to `/resources/js/tracking.js`:

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab3/1.png]]

- Use Param Miner to find unkeyed inputs (`Guess headers`) for this request.
- The extension finds the `X-Forwarded-Scheme` header is unkeyed:

```
Updating active thread pool size to 8
Loop 0
Queued 1 attacks from 1 requests in 0 seconds
Initiating header bruteforce on 0ac100e103482f15814511cf00fb006d.web-security-academy.net
Identified parameter on 0ac100e103482f15814511cf00fb006d.web-security-academy.net: x-forwarded-scheme
```

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab3/2.png]]

- Send a `GET` to `/resources/js/tracking.js` to `Repeater` and insert the `X-Forwarded-Scheme` header:

```js
X-Forwarded-Scheme: http
```

- Send the request and observe the application response:

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab3/3.png]]

- The application responds with a `302` redirect to a secure version of the website. 
- Use Param Miner against this request (with `X-Forwarded-Scheme` set) again:

```
Updating active thread pool size to 8
Loop 0
Queued 1 attacks from 1 requests in 0 seconds
Initiating header bruteforce on 0ac100e103482f15814511cf00fb006d.web-security-academy.net
Identified parameter on 0ac100e103482f15814511cf00fb006d.web-security-academy.net: x-forwarded-host~%s.%h
```

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab3/4.png]]

- The extension detects `X-Forwarded-Host` is unkeyed, too. Add it to the request in `Repeater` (where `X-Forwarded-Scheme` is already present) and set to an arbitrary value. Send the request and observe the response:

```js
X-Forwarded-Host: anything
```

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab3/5.png]]


- The application uses the value of the `X-Forwaded-Host` header to dynamically construct the `Location` URL. Notice that `X-Forwareded-Host` alone doesn't work — you need both `X-Forwarded-Host` and `X-Forwarded-Scheme: http` headers set.

---

- Go to your server and change the request path from `/exploit` to `/resources/js/tracking.js`.

```js
/resources/js/tracking.js
```

- Set `Content-Type` to `text/javascript`. 

```js
Content-Type: text/javascript
```

- Paste the following as a response body:

```js
alert(document.cookie)
```

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab3/6.png]]

- Click `Store`.

---
- Go back to in `Repeater`. Insert your exploit server hostname as a value of the `X-Forwarded-Host` header.
- Send the request several times until you see `X-Cache: hit`.

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab3/7.png]]

- To verify the exploit is working, navigate to the main page within `30` seconds after you cached the poisoned response (`Ctrl + Shift + R` to refresh the page without hitting a previously cached benign response). You should see an alert:

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab3/8.png]]


- Keep the poisoned response cached until the lab is solved.

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab3/solved.png]]

Solved!

## 4. Targeted web cache poisoning using an unknown header

>[!done]

>[!note]+ Lab description
> - [`Lab: Targeted web cache poisoning using an unknown header`](https://portswigger.net/web-security/web-cache-poisoning/exploiting-design-flaws/lab-web-cache-poisoning-targeted-using-an-unknown-header)
> - Level: #Practitioner 
> 
> This lab is vulnerable to web cache poisoning. A victim user will view any comments that you post. To solve this lab, you need to poison the cache with a response that executes `alert(document.cookie)` in the visitor's browser. However, you also need to make sure that the response is served to the specific subset of users to which the intended victim belongs.

### Solution

- Browse the application. 
- The cache oracle is the same (the `X-Cache` header).
- Inspect HTTP history and notice `User-Agent` is included in the cache key (`Vary: User-Agent`). This means that is you were to poison the cache, you could do that only for users with the `User-Agent` you specified. 

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab4/1.png]]

- Go to `Target` -> `Site map`, right-click on the lab host -> `Extensions` -> `Param Miner` -> `Guess headers`.
- Param Miner finds:

```
Updating active thread pool size to 8
Loop 0
Queued 1 attacks from 1 requests in 0 seconds
Initiating header bruteforce on 0a5c002d04f212a1807adfa700c50074.h1-web-security-academy.net
Identified parameter on 0a5c002d04f212a1807adfa700c50074.h1-web-security-academy.net: origin~https://%s.%h
Identified parameter on 0a5c002d04f212a1807adfa700c50074.h1-web-security-academy.net: x-host~%h:%s
Identified parameter on 0a5c002d04f212a1807adfa700c50074.h1-web-security-academy.net: via
```

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab4/2.png]]

- Send a `GET` to `/` to `Repeater`. Add a cache buster and `X-Host` set to an arbitrary hostname to see how the application response changes:

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab4/3.png]]

- Observe the application dynamically generates a JavaScript import URL to `/resources/js/tracking.js`.

---

- Go to your server and change the request path from `/exploit` to `/resources/js/tracking.js`.

```js
/resources/js/tracking.js
```

- Set `Content-Type` to `text/javascript`. 

```js
Content-Type: text/javascript
```

- Paste the following as a response body:

```js
alert(document.cookie)
```

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab4/4.png]]


- Click `Store`.

---
- Go back to in `Repeater`. Insert your exploit server hostname as a value of the `X-Host` header. Ensure the JS import link was generated correctly:

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab4/5.png]]

- Remove the cache buster and resend the request until you `hit`.

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab4/6.png]]

- Visit the main page again (`Ctrl + Shift + R`). You should get an alert:

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab4/7.png]]

---

- Now you need to know the `User-Agent` of your victim.
- In the comment section under any post, paste an image with `src` that points to your website. The victim will view the comment and you will find their `User-Agent` value in the access logs of your exploit server:

```html
<img src="https://exploit-0a82007e0476127c80abdeb701ce00a9.exploit-server.net/image" />
```

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab4/8.png]]


- Go to `Access log` on your exploit server and see the victim's `User-Agent`:

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab4/9.png]]

- Copy the value and paste it instead of your `User-Agent` in the request to `/resources/js/tracking/js` in `Repeater`.
- You won't get an alert anymore (cache poisoning doesn't affect your `User-Agent`), so just keep the poisoned response cached until the lab is solved.

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab4/solved.png]]

Solved!
## 5. Web cache poisoning via an unkeyed query string

>[!done]

>[!note]+ Lab description
> - [`Lab: Web cache poisoning via an unkeyed query string`](https://portswigger.net/web-security/web-cache-poisoning/exploiting-implementation-flaws/lab-web-cache-poisoning-unkeyed-query)
> - Level: #Practitioner 
> 
> This lab is vulnerable to web cache poisoning because the query string is unkeyed. A user regularly visits this site's home page using Chrome.
> 
> To solve the lab, poison the home page with a response that executes `alert(1)` in the victim's browser.
### Solution

- The cache oracle is the same (the `X-Cache` header).
- Use Param Miner to `Guess query params`. Notice that **no query parameters are included in the cache key**, so Param Miner detects a random URL parameter as unkeyed:

```
Updating active thread pool size to 8
Loop 0
Queued 1 attacks from 1 requests in 0 seconds
Initiating url bruteforce on 0a6800f203bfda9780ff03e4003c00be.web-security-academy.net
Identified parameter on 0a6800f203bfda9780ff03e4003c00be.web-security-academy.net: 45qR
```

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab5/1.png]]

- Paste this URL parameter in `Repeater` set to an arbitrary value. See it is reflected in a canonical URL in the response:

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab5/2.png]]

- Since the whole URL string is excluded from the cache key, use a cookie as a cache buster. 

- Inject a XSS payload and get the response cached:

```
/?45qR=1%20'%20%2f%3e%3cscript%3ealert()%3c%2fscript%3e
```

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab5/3.png]]

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab5/solved.png]]

Solved!
## 6. Web cache poisoning via an unkeyed query parameter

>[!done]

>[!note]+ Lab description
> - [`Lab: Web cache poisoning via an unkeyed query parameter`](https://portswigger.net/web-security/web-cache-poisoning/exploiting-implementation-flaws/lab-web-cache-poisoning-unkeyed-param)
> - Level: #Practitioner 
> 
> This lab is vulnerable to web cache poisoning because it excludes a certain parameter from the cache key. A user regularly visits this site's home page using Chrome.
> 
> To solve the lab, poison the cache with a response that executes `alert(1)` in the victim's browser.
### Solution


- The cache oracle is the same (the `X-Cache` header).
- Use Param Miner to `Guess query params`. 
- Param Miner detects an unkeyed URL query parameter, `utm_content`:

```
Updating active thread pool size to 8
Loop 0
Queued 1 attacks from 1 requests in 0 seconds
Initiating url bruteforce on 0a6300a7036a738280df0d5e002c00b9.web-security-academy.net
Identified parameter on 0a6300a7036a738280df0d5e002c00b9.web-security-academy.net: utm_content
```

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab6/1.png]]

- Send a `GET` request to `/` to `Repeater` and insert the `utm_content` parameter set to an arbitrary value:

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab6/2.png]]

- The value is reflected in two places: in the `utm_content` cookie and a canonical link.
- Inject a XSS payload:

```
/?utm_content=test1%20'%20%2f%3e%3cscript%3ealert()%3c%2fscript%3e
```

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab6/3.png]]

- Get the content cached.
- If you visit the main page from the browser without specifying the `utm_content` parameter in the URL, you should see an alert:

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab6/4.png]]

- Keep the content cached until the lab is solved.
![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab6/solved.png]]

Solved!
## 7. Parameter cloaking

>[!done]

>[!note]+ Lab description
> - [`Lab: Parameter cloaking`](https://portswigger.net/web-security/web-cache-poisoning/exploiting-implementation-flaws/lab-web-cache-poisoning-param-cloaking)
> - Level: #Practitioner 
> 
> This lab is vulnerable to web cache poisoning because it excludes a certain parameter from the cache key. There is also inconsistent parameter parsing between the cache and the back-end. A user regularly visits this site's home page using Chrome.
> 
> To solve the lab, use the parameter cloaking technique to poison the cache with a response that executes `alert(1)` in the victim's browser.
### Solution

- Right-click a `GET` request to `/`  -> `Param Miner` -> `Extensions` -> `Guess query params`.
- Param Miner identifies:

```
Updating active thread pool size to 8
Loop 0
Queued 1 attacks from 1 requests in 0 seconds
Initiating url bruteforce on 0aaf00840398d46280b203fa002a00fc.web-security-academy.net
Identified parameter on 0aaf00840398d46280b203fa002a00fc.web-security-academy.net: utm_content
```

- Also notice a request to `/js/geolocate.js`:

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab7/1.png]]

- It has a `callback` parameter set to the `setCountryCookie`. Send this request to repeater and change it:

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab7/2.png]]

- See you are able to inject an arbitrary function. 
- The `callback` parameter is, however, included in the cache key (`miss` as soon as you change it). But you may be able to smuggle another value using parameter cloaking:

```
/js/geolocate.js?cb=2&callback=setCountryCookie&utm_content=test;callback=alert(1)
```

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab7/3.png]]

- See the backend uses the second `callback` you smuggled and outputs JavaScript with `alert()`. 
- Get this response cached without the cache buster and navigate to the main page. You should see an alert popping up:

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab7/4.png]]

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab7/solved.png]]


Solved!
## 8. Web cache poisoning via a fat `GET` request

>[!done]

>[!note]+ Lab description
> - [`Lab: Web cache poisoning via a fat GET request`](https://portswigger.net/web-security/web-cache-poisoning/exploiting-implementation-flaws/lab-web-cache-poisoning-fat-get)
> - Level: #Practitioner 
> 
> This lab is vulnerable to web cache poisoning. It accepts `GET` requests that have a body, but does not include the body in the cache key. A user regularly visits this site's home page using Chrome.
> 
> To solve the lab, poison the cache with a response that executes `alert(1)` in the victim's browser.

### Solution

- Find a `GET` request to `/js/geolocate` and send it to `Repeater`. Add a request body not changing the request method, and set the `callback` parameter to `alert(1)`:

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab8/1.png]]

- The fat `GET` request body is not included in the cache key, however, used by the backend to generate JavaScript dynamically and is prioritized over the `GET` parameter.
- Remove the cache buster and make the poisoned response get cached.

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab8/2.png]]

- Navigate to the main page (`Ctrl + Shift + R`). You should see an alert popping up:

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab8/3.png]]

- Keep the response cached until the lab is solved.

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab8/solved.png]]

Solved!
## 9. URL normalization

>[!done]

>[!note]+ Lab description
> - [`Lab: URL normalization`](https://portswigger.net/web-security/web-cache-poisoning/exploiting-implementation-flaws/lab-web-cache-poisoning-normalization)
> - Level: #Practitioner 
> 
> This lab contains an XSS vulnerability that is not directly exploitable due to browser URL-encoding.
> 
> To solve the lab, take advantage of the cache's normalization process to exploit this vulnerability. Find the XSS vulnerability and inject a payload that will execute `alert(1)` in the victim's browser. Then, deliver the malicious URL to the victim.
### Solution

- In `Repeater`, go to any non-existent path and see the path is reflected in an error message:

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab9/1.png]]
- Any non-existing endpoint can be used to inject arbitrary JavaScript into the response:

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab9/2.png]]

- If you request this URL in the browser, the payload doesn't execute because it is URL-encoded.
- Get the response cached and immediately visit the same page. You should see an alert firing:

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab9/3.png]]

- Then, still keeping the response cached, deliver the link to victim.

```
https://0a4000b80373b4c881175d5400aa00d7.web-security-academy.net/test<script>alert(1)</script>
```

![[images/walkthrough/PortSwigger/Web Cache Poisoning/lab9/solved.png]]