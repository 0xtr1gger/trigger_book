---
created: 2026-05-29
---


| `#`  | Solved? | Name                                               | Date    | Notes         |
| ---- | ------- | -------------------------------------------------- | ------- | ------------- |
| `1.` | `✓`     | Basic password reset poisoning                     | `29.05` |               |
| `2.` | `✓`     | Host header authentication bypass<br>              | `29.05` |               |
| `3.` | `✓`     | Web cache poisoning via ambiguous requests         | `24.06` |               |
| `4.` | `✓`     | Routing-based SSRF                                 | `29.05` | #Collaborator |
| `5.` | `✓`     | SSRF via flawed request parsing                    | `29.05` | #Collaborator |
| `6.` | `✓`     | Host validation bypass via connection state attack | `29.05` | #Collaborator |

## 1. Basic password reset poisoning

>[!done]

>[!note]+ Lab description
> - [`Lab: Basic password reset poisoning`](https://portswigger.net/web-security/host-header/exploiting/password-reset-poisoning/lab-host-header-basic-password-reset-poisoning)
> - Level: #Apprentice 
> 
> This lab is vulnerable to password reset poisoning. The user `carlos` will carelessly click on any links in emails that he receives. To solve the lab, log in to Carlos's account.
> 
> You can log in to your own account using the following credentials: `wiener:peter`. Any emails sent to this account can be read via the email client on the exploit server.
### Solution

- Go to `My account` and click `Forgot password?`:

![[images/walkthrough/PortSwigger/Host header injection/lab1/1.png]]

- Enter your username (`wiener`):

![[images/walkthrough/PortSwigger/Host header injection/lab1/2.png]]

- The application says: `Please check your email for a reset password link.`.

- Go to your exploit server -> `Email client`.

![[images/walkthrough/PortSwigger/Host header injection/lab1/3.png]]

- The link looks like this:

```
https://0aa400ce04a7756f8113985700f600ab.web-security-academy.net/forgot-password?temp-forgot-password-token=eeap5auobuz02ghbsk41sbnm8o89w53g
```

- Follow it and see a form to set a new password. Set any password.

![[images/walkthrough/PortSwigger/Host header injection/lab1/4.png]]

- See the token is carried in a query parameter:

![[images/walkthrough/PortSwigger/Host header injection/lab1/5.png]]

- If the password reset link is constructed using the value of the `Host` header, can intercept other user's password reset tokens. 
- Send the password reset request to `Repeater`.
- Change the username from `wiener` to `carlos`. 
- Set the `Host` header value to your exploit's domain (e.g., `exploit-0a1000ab0482756981419744016d00f4.exploit-server.net`):

![[images/walkthrough/PortSwigger/Host header injection/lab1/6.png]]

- The application responds with `OK`. 
- Check the logs of your exploit server:

![[images/walkthrough/PortSwigger/Host header injection/lab1/7.png]]

- Construct a password reset link from your previous link using the `carlos`'s token:

```
https://0aa400ce04a7756f8113985700f600ab.web-security-academy.net/forgot-password?temp-forgot-password-token=illswzibvenuwxfset9etzg4f3b7q00m
```

- Paste the link into the browser's search bar and set a new password:

![[images/walkthrough/PortSwigger/Host header injection/lab1/8.png]]

- Log in as `carlos` using the password you set.

![[images/walkthrough/PortSwigger/Host header injection/lab1/solved.png]]

Solved!
## 2. Host header authentication bypass

>[!done]

>[!note]+ Lab description
> - [`Lab: Host header authentication bypass`](https://portswigger.net/web-security/host-header/exploiting/lab-host-header-authentication-bypass)
> - Level: #Apprentice 
> 
> This lab makes an assumption about the privilege level of the user based on the HTTP Host header.
> 
> To solve the lab, access the admin panel and delete the user `carlos`.
### Solution

- Launch the lab and attempt to access `/admin`:

![[images/walkthrough/PortSwigger/Host header injection/lab2/1.png]]

- The application says `Admin interface only available to local users`.
- Send the request to `Repeater` and change the `Host` header to `localhost`:

![[images/walkthrough/PortSwigger/Host header injection/lab2/2.png]]

- The application lets you in.
- Delete the `carlos` user by changing the URL path to `/admin/delete?username=carlos`:

![[images/walkthrough/PortSwigger/Host header injection/lab2/3.png]]

![[images/walkthrough/PortSwigger/Host header injection/lab2/solved.png]]

Solved!
## 3. Web cache poisoning via ambiguous requests

>[!note]+ Lab description
> - [`Lab: Web cache poisoning via ambiguous requests`](https://portswigger.net/web-security/host-header/exploiting/lab-host-header-web-cache-poisoning-via-ambiguous-requests)
> - Level: #Practitioner 
> 
> This lab is vulnerable to web cache poisoning due to discrepancies in how the cache and the back-end application handle ambiguous requests. An unsuspecting user regularly visits the site's home page.
> 
> To solve the lab, poison the cache so the home page executes `alert(document.cookie)` in the victim's browser.

### Solution

- Navigate to the lab's main page and record requests using Burp. 
- Send a `GET` request to `/` to `Repeater` and study application behavior. 

- If you change the `Host` header, you can no longer access the application; it validates `Host` and responds with `Gateway Timeout`:

![[images/walkthrough/PortSwigger/Host header injection/lab3/1.png]]

- But if you duplicate the `Host` header and insert an arbitrary value into the second header, the application no longer throws an error and appears to ignore it. 
- But the value of the second header is reflected in application response: it is used to generate a link to `/resources/js/tracking.js`:

![[images/walkthrough/PortSwigger/Host header injection/lab3/2.png]]


- Also notice this second header is not included in the cache key, since after adding it, you still get `X-Cache: hit`. This is web cache poisoning.

---

- Go to your exploit server and host the following code:

```js
alert(document.cookie)
```

- Then change the exploit path from `/exploit` to `/resources/js/tracking.js`. 

![[images/walkthrough/PortSwigger/Host header injection/lab3/3.png]]

- `Store` the exploit.

- Not go back to repeater and insert your exploit server domain instead of `example.com` and get the response cached. 
- Then visit the main page again and see an alert firing:


![[images/walkthrough/PortSwigger/Host header injection/lab3/4.png]]

- Keep the response cached until the lab is solved.

![[images/walkthrough/PortSwigger/Host header injection/lab3/solved.png]]


Solved!

## 4. Routing-based SSRF

>[!warning] #Collaborator  Burp Collaborator (Professional Edition) is required to solve this lab.

>[!done]

>[!note]+ Lab description
> - [`Lab: Routing-based SSRF`](https://portswigger.net/web-security/host-header/exploiting/lab-host-header-routing-based-ssrf)
> - Level: #Practitioner 
> 
> This lab is vulnerable to routing-based SSRF via the `Host` header. You can exploit this to access an insecure intranet admin panel located on an internal IP address.
> 
> To solve the lab, access the internal admin panel located in the `192.168.0.0/24` range, then delete the user `carlos`.
### Solution

- Access the lab home. Send the `GET /` request that received a `200` response to `Repeater`.
- Right-click the request -> `Insert Collaborator payload`, then replace it with a Collaborator domain name. Send the request.

![[images/walkthrough/PortSwigger/Host header injection/lab4/1.png]]

- To to `Collaborator` and click `Poll now`. See some requests:

![[images/walkthrough/PortSwigger/Host header injection/lab4/2.png]]

- This confirms you can make middleware issue requests to an arbitrary server.
- Send the request to `Intruder` and deselect `Update Host header to match target`.
- Delete the value of the Host header and replace it with:

```http
Host: 192.168.0.§0§
```

- In the `Payloads` side panel, select the payload type `Numbers`; under `Payload configuration`, enter:

```
From: 0
To: 255
Step: 1
```

![[images/walkthrough/PortSwigger/Host header injection/lab4/3.png]]

- Start the attack. Sort the results by status code:

![[images/walkthrough/PortSwigger/Host header injection/lab4/4.png]]

- Find a `302 Found` request; it redirects you do `/admin`. 
- Send this request to `Repeater` and change the path to `/admin`:

![[images/walkthrough/PortSwigger/Host header injection/lab4/5.png]]

- See a delete user form. 
- Change request method to `POST` and insert the CSRF token and username parameters:

```bash
csrf=PCE0Bdkrmqq0RVQSonDAa97f44zHCh28&username=carlos
```

- Change URL path to `/admin/delete`.

- Send the request. The application responds with `302 Found`.

![[images/walkthrough/PortSwigger/Host header injection/lab4/6.png]]

![[images/walkthrough/PortSwigger/Host header injection/lab4/solved.png]]

Solved!
## 5. SSRF via flawed request parsing

>[!warning] #Collaborator  Burp Collaborator (Professional Edition) is required to solve this lab.

>[!done]

>[!note]+ Lab description
> - [`Lab: SSRF via flawed request parsing`](https://portswigger.net/web-security/host-header/exploiting/lab-host-header-ssrf-via-flawed-request-parsing)
> - Level: #Practitioner 
> 
> This lab is vulnerable to routing-based SSRF due to its flawed parsing of the request's intended host. You can exploit this to access an insecure intranet admin panel located at an internal IP address.
> 
> To solve the lab, access the internal admin panel located in the `192.168.0.0/24` range, then delete the user `carlos`.
### Solution

- Send a request to `/` to `Repeater` and change the `Host` header to Collaborator's domain.

![[images/walkthrough/PortSwigger/Host header injection/lab5/1.png]]

- The application responds with `403 Forbidden`.
- Instead of `/`, supply your lab URL as a URL path. The application responds with `200 OK`:

![[images/walkthrough/PortSwigger/Host header injection/lab5/2.png]]

- Go to Collaborator -> `Poll now` to verify outbound connections:

![[images/walkthrough/PortSwigger/Host header injection/lab5/3.png]]

- Send the request to Intruder and enumerate `192.168.0.0/24` address range:

![[images/walkthrough/PortSwigger/Host header injection/lab5/4.png]]

- Start the attack. Sort the results by response code:

![[images/walkthrough/PortSwigger/Host header injection/lab5/5.png]]

- Send a request that caused `302 Found` redirect to `/admin` to `Repeater` and change the URL path to `/admin`:

![[images/walkthrough/PortSwigger/Host header injection/lab5/6.png]]

- Delete the `carlos` user using a `POST` request to `/admin/delete`:

![[images/walkthrough/PortSwigger/Host header injection/lab5/7.png]]

![[images/walkthrough/PortSwigger/Host header injection/lab5/solved.png]]

Solved!
## 6. Host validation bypass via connection state attack

>[!warning] #Collaborator  Burp Collaborator (Professional Edition) is required to solve this lab.

>[!done]

>[!note]+ Lab description
> - [`Lab: Host validation bypass via connection state attack`](https://portswigger.net/web-security/host-header/exploiting/lab-host-header-host-validation-bypass-via-connection-state-attack)
> - Level: #Practitioner 
> 
> This lab is vulnerable to routing-based SSRF via the Host header. Although the front-end server may initially appear to perform robust validation of the Host header, it makes assumptions about all requests on a connection based on the first request it receives.
> 
> To solve the lab, exploit this behavior to access an internal admin panel located at `192.168.0.1/admin`, then delete the user `carlos`.
### Solution

- Send a request to `/` to `Repeater` and change the `Host` header to Collaborator's domain.

![[images/walkthrough/PortSwigger/Host header injection/lab6/1.png]]

- Detect interactions in `Collaborator`:

![[images/walkthrough/PortSwigger/Host header injection/lab6/2.png]]

- Then change the `Host` header in `Repeater` to `192.168.0.1`:

![[images/walkthrough/PortSwigger/Host header injection/lab6/3.png]]

- See a redirect.


- In Burp Repeater, click the settings icon `Enable HTTP/1 connection reuse`.
![[images/walkthrough/PortSwigger/Host header injection/lab6/4.png]]

- Notice that you are able to access an administrator panel by first sending a request with a legitimate `Host` header of your lab (e.g., `0a10008103bf721080de99b2002b004d.h1-web-security-academy.net`) and then immediately sending the same request with `Host` set to `192.168.0.1`:

![[images/walkthrough/PortSwigger/Host header injection/lab6/5.png]]

- This way, obtain the CSRF token needed for the user delete request. Change request method to `POST`, change URL path to `/admin/delete`, and set `csrf` and `username` parameters.

```
csrf=NEFBbRIjxNDoVZ8Oyt6OlPOyeq0TP6lV&username=carlos
```

- First send that request to the legitimate lab host, then immediately switch to `192.168.0.1`:

![[images/walkthrough/PortSwigger/Host header injection/lab6/6.png]]

- You may need several attempts before the `carlos` user is actually deleted.

![[images/walkthrough/PortSwigger/Host header injection/lab6/solved.png]]

Solved!