---
created: 2026-05-06
---

| `#`   | Solved? | Name                                                                  | Date    | Notes |
| ----- | ------- | --------------------------------------------------------------------- | ------- | ----- |
| `1.`  | `✓`     | Unprotected admin functionality                                       | `06.05` |       |
| `2.`  | `✓`     | Unprotected admin functionality with unpredictable URL                | `06.05` |       |
| `3.`  | `✓`     | User role controlled by request parameter                             | `06.05` |       |
| `4.`  | `✓`     | User role can be modified in user profile                             | `06.05` |       |
| `5.`  | `✓`     | User ID controlled by request parameter                               | `06.05` |       |
| `6.`  | `✓`     | User ID controlled by request parameter, with unpredictable user IDs  | `06.05` |       |
| `7.`  | `✓`     | User ID controlled by request parameter with data leakage in redirect | `06.05` |       |
| `8.`  | `✓`     | User ID controlled by request parameter with password disclosure      | `06.05` |       |
| `9.`  | `✓`     | Insecure direct object references                                     | `06.05` |       |
| `10.` | `✓`     | URL-based access control can be circumvented                          | `06.05` |       |
| `11.` | `✓`     | Method-based access control can be circumvented                       | `06.05` |       |
| `12.` | `✓`     | Multi-step process with no access control on one step                 | `06.05` |       |
| `13.` | `✓`     | Referer-based access control                                          | `06.05` |       |

## 1. Unprotected admin functionality

>[!done]

>[!note]+ Lab description
> - [`Lab: Unprotected admin functionality`](https://portswigger.net/web-security/access-control/lab-unprotected-admin-functionality)
> - Level: #Apprentice 
> 
> This lab has an unprotected admin panel.
> 
> Solve the lab by deleting the user `carlos`.

### Solution

- Navigate to `/robots.txt` and see:

```
User-agent: *
Disallow: /administrator-panel
```

![[images/walkthrough/PortSwigger/Access Controls/lab1/1.png]]

- Then go to `/administrator-panel` and see it's completely unprotected and you can access it freely even without authentication:

![[images/walkthrough/PortSwigger/Access Controls/lab1/2.png]]


- Delete the `carlos` user:

![[images/walkthrough/PortSwigger/Access Controls/lab1/solved.png]]

Solved!
## 2. Unprotected admin functionality with unpredictable URL

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Unprotected admin functionality with unpredictable URL`](https://portswigger.net/web-security/access-control/lab-unprotected-admin-functionality-with-unpredictable-url)
> - Level: #Apprentice 
> 
> 
> This lab has an unprotected admin panel. It's located at an unpredictable location, but the location is disclosed somewhere in the application.
> 
> Solve the lab by accessing the admin panel, and using it to delete the user `carlos`.

### Solution

- Inspect the source code of the main page and find:

![[images/walkthrough/PortSwigger/Access Controls/lab2/1.png]]


- Navigate to the `/admin-*` (in this case, `/admin-pvihka`) set as `href` attribute:

![[images/walkthrough/PortSwigger/Access Controls/lab2/2.png]]

- This gets you to an unprotected administrator panel. Delete the `carlos` user.

![[images/walkthrough/PortSwigger/Access Controls/lab2/solved.png]]

Solved!
## 3. User role controlled by request parameter

>[!note]+ Lab description
> - [`Lab: User role controlled by request parameter`](https://portswigger.net/web-security/access-control/lab-user-role-controlled-by-request-parameter)
> - Level: #Apprentice 
> 
> This lab has an admin panel at `/admin`, which identifies administrators using a forgeable cookie.
> 
> Solve the lab by accessing the admin panel and using it to delete the user `carlos`.
> 
> You can log in to your own account using the following credentials: `wiener:peter`

### Solution

- Try to navigate to admin panel at `/admin`. The application responds with `401 Unauthorized`:

```
Admin interface only available if logged in as an administrator
```

![[images/walkthrough/PortSwigger/Access Controls/lab3/1.png]]

- Log in as `wiener` and attempt to access `/admin` again:

![[images/walkthrough/PortSwigger/Access Controls/lab3/2.png]]

- The application gives the same response, however this time, in your request there is an `Admin=false` cookie. Send the request to `Repeater` and change it to `Admin=true`:

![[images/walkthrough/PortSwigger/Access Controls/lab3/3.png]]

- For the access check, the application relies solely on that cookie. You get access to the admin panel.
- Change the path to `/admin/delete?username=carlos` and `Send`:


![[images/walkthrough/PortSwigger/Access Controls/lab3/4.png]]

![[images/walkthrough/PortSwigger/Access Controls/lab3/solved.png]]


Solved!


## 4. User role can be modified in user profile

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: User role can be modified in user profile`](https://portswigger.net/web-security/access-control/lab-user-role-can-be-modified-in-user-profile)
> - Level: #Apprentice 
> 
> This lab has an admin panel at `/admin`. It's only accessible to logged-in users with a `roleid` of `2`.
> 
> Solve the lab by accessing the admin panel and using it to delete the user `carlos`.
> 
> You can log in to your own account using the following credentials: `wiener:peter`

### Solution

- Log in as `wiener` and attempt to access `/admin`:

![[images/walkthrough/PortSwigger/Access Controls/lab4/1.png]]

- The application responds with `401 Unauthorized`.

- Then go to your profile and change the email to test this functionality:


![[images/walkthrough/PortSwigger/Access Controls/lab4/2.png]]

- `POST` body:

```JSON
{
	"email":"wiener@normal-user.net"
}
```

- JSON response:

```JSON
{
  "username": "wiener",
  "email": "wiener@normal-user.net",
  "apikey": "eaEdJmNCyl8Y53XU1nK4cTJmXE56GXzQ",
  "roleid": 1
}
```

- Send the request to `Repeater` and change it to:

```JSON
{
	"email":"wiener@normal-user.net",
	"roleid": 2
 }
```

![[images/walkthrough/PortSwigger/Access Controls/lab4/3.png]]

- The application responds with `302 Found`.
- Try accessing `/admin` again:

![[images/walkthrough/PortSwigger/Access Controls/lab4/4.png]]


- Delete the `carlos` user:

![[images/walkthrough/PortSwigger/Access Controls/lab4/solved.png]]


Solved!
## 5. User ID controlled by request parameter

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: User ID controlled by request parameter`](https://portswigger.net/web-security/access-control/lab-user-id-controlled-by-request-parameter)
> - Level: #Apprentice 
> 
> This lab has a horizontal privilege escalation vulnerability on the user account page.
> 
> To solve the lab, obtain the API key for the user `carlos` and submit it as the solution.
> 
> You can log in to your own account using the following credentials: `wiener:peter`


### Solution

- Log is an `wiener` and see your profile with an API key:

![[images/walkthrough/PortSwigger/Access Controls/lab5/1.png]]

- Change the `id` URL parameter from `wiener` to `carlos`:

![[images/walkthrough/PortSwigger/Access Controls/lab5/2.png]]

- No authorization controls — you get access to `carlos`'s account. Kinda [[IDOR]].
- Copy the key and submit it as a solution:

![[images/walkthrough/PortSwigger/Access Controls/lab5/solved.png]]


Solved!

## 6. User ID controlled by request parameter, with unpredictable user IDs

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: User ID controlled by request parameter, with unpredictable user IDs`](https://portswigger.net/web-security/access-control/lab-user-id-controlled-by-request-parameter-with-unpredictable-user-ids)
> - Level: #Apprentice 
> 
> This lab has a horizontal privilege escalation vulnerability on the user account page, but identifies users with GUIDs.
> 
> To solve the lab, find the GUID for `carlos`, then submit his API key as the solution.
> 
> You can log in to your own account using the following credentials: `wiener:peter`
### Solution

- Log in as `wiener` and see your profile:

![[images/walkthrough/PortSwigger/Access Controls/lab6/1.png]]

- Rather than just username, the application uses UUIDs as profile identifiers, so you can't simply guess `carlos`'s ID.
- Browse the application. Find a blog post written by `carlos`:

![[images/walkthrough/PortSwigger/Access Controls/lab6/2.png]]

- Link to the author exposes their identifier. Copy it and insert as an `id` at `/my-account?id=`:

![[images/walkthrough/PortSwigger/Access Controls/lab6/3.png]]

- Access `carlos`'s account, copy their API key, and submit it as a solution:

![[images/walkthrough/PortSwigger/Access Controls/lab6/4.png]]

Solved!

## 7. User ID controlled by request parameter with data leakage in redirect

>[!note]+ Lab description
> 
> - [`Lab: User ID controlled by request parameter with data leakage in redirect`](https://portswigger.net/web-security/access-control/lab-user-id-controlled-by-request-parameter-with-data-leakage-in-redirect)
> - Level: #Apprentice 
> 
> This lab contains an access control vulnerability where sensitive information is leaked in the body of a redirect response.
> 
> To solve the lab, obtain the API key for the user `carlos` and submit it as the solution.
> 
> You can log in to your own account using the following credentials: `wiener:peter`

### Solution

- Log in as `wiener`. Trying to access `carlos`'s account redirects you to `/login`:

![[images/walkthrough/PortSwigger/Access Controls/lab7/1.png]]

- And yet in the body of the redirect response you see `carlos`'s profile data:

![[images/walkthrough/PortSwigger/Access Controls/lab7/2.png]]

- Without a proxy, you wouldn't see it.
- Copy their API key and submit it as a lab solution:

![[images/walkthrough/PortSwigger/Access Controls/lab7/solved.png]]


Solved!


## 8. User ID controlled by request parameter with password disclosure

>[!done]

>[!note]+ Lab description
> - [`Lab: User ID controlled by request parameter with password disclosure`](https://portswigger.net/web-security/access-control/lab-user-id-controlled-by-request-parameter-with-password-disclosure)
> - Level: #Apprentice 
> 
> This lab has user account page that contains the current user's existing password, prefilled in a masked input.
> 
> To solve the lab, retrieve the administrator's password, then use it to delete the user `carlos`.
> 
> You can log in to your own account using the following credentials: `wiener:peter`
> 

### Solution

- Log in as `wiener`:

![[images/walkthrough/PortSwigger/Access Controls/lab8/1.png]]

- Notice that as soon as you navigate to your profile, your see your password pre-filled and masked in the `Update password` form
- Change account ID in the URL to `administrator` and access their account:

![[images/walkthrough/PortSwigger/Access Controls/lab8/2.png]]

- To reveal the password, inspect the element:

![[images/walkthrough/PortSwigger/Access Controls/lab8/3.png]]

- Copy the value. Log out and log in as `administrator`:

![[images/walkthrough/PortSwigger/Access Controls/lab8/4.png]]

- Access `Admin panel`:

![[images/walkthrough/PortSwigger/Access Controls/lab8/5.png]]

- Delete the `carlos` user:

![[images/walkthrough/PortSwigger/Access Controls/lab8/solved.png]]

Solved!
## 9. Insecure direct object references

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Insecure direct object references`](https://portswigger.net/web-security/access-control/lab-insecure-direct-object-references)
> - Level: #Apprentice 
> 
> This lab stores user chat logs directly on the server's file system, and retrieves them using static URLs.
> 
> Solve the lab by finding the password for the user `carlos`, and logging into their account.

### Solution

- Access `Live chat` in the application:

![[images/walkthrough/PortSwigger/Access Controls/lab9/1.png]]

- Click `View transcript`. This downloads a transcript file, `2.txt`, to your local machine. The request looks like this:

![[images/walkthrough/PortSwigger/Access Controls/lab9/2.png]]

- Send the request to `Repeater` and change the file identifier to `1.txt`:

![[images/walkthrough/PortSwigger/Access Controls/lab9/3.png]]

- You can access to the transcript, and in the transcript you find a password. Use it to log in as `carlos`:

![[images/walkthrough/PortSwigger/Access Controls/lab9/4.png]]


Solved!

## 10. URL-based access control can be circumvented

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: URL-based access control can be circumvented`](https://portswigger.net/web-security/access-control/lab-url-based-access-control-can-be-circumvented)
> - Level: #Practitioner 
> 
> This website has an unauthenticated admin panel at `/admin`, but a front-end system has been configured to block external access to that path. However, the back-end application is built on a framework that supports the `X-Original-URL` header.
> 
> To solve the lab, access the admin panel and delete the user `carlos`.

### Solution

- Access the admin panel. The application responds with `403 Forbidden`. Inspect the request:

![[images/walkthrough/PortSwigger/Access Controls/lab10/1.png]]

- Send the request to `Repeater`. Add the `X-Original-URL` HTTP header set to `/admin` and change `GET` path to `/`. This gets you access to the admin panel:

![[images/walkthrough/PortSwigger/Access Controls/lab10/2.png]]


- Delete the `carlos` user by changing `X-Original-URL` to `/admin/delete` and `GET` path to `?username=carlos`:

![[images/walkthrough/PortSwigger/Access Controls/lab10/3.png]]


Solved!

## 11. Method-based access control can be circumvented

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Method-based access control can be circumvented`](https://portswigger.net/web-security/access-control/lab-method-based-access-control-can-be-circumvented)
> - Level: #Practitioner 
> 
> This lab implements access controls based partly on the HTTP method of requests. You can familiarize yourself with the admin panel by logging in using the credentials `administrator:admin`.
> 
> To solve the lab, log in using the credentials `wiener:peter` and exploit the flawed access controls to promote yourself to become an administrator.

### Solution

- Log in as `administrator` and access admin panel: 

![[images/walkthrough/PortSwigger/Access Controls/lab11/1.png]]

- Promote `carlos` to `administrator` and inspect the request:

![[images/walkthrough/PortSwigger/Access Controls/lab11/2.png]]

- Log out and log in as `wiener`. 
- Send the `carlos`'s upgrade request to Repeater and replace the session ID with your own. Then change the username from `carlos` to `wiener`:

![[images/walkthrough/PortSwigger/Access Controls/lab11/3.png]]

- See `401 Unauthorized`.
- Change request method to `PUT` and send the request again:

![[images/walkthrough/PortSwigger/Access Controls/lab11/4.png]]

- Receive `302 Found`.

![[images/walkthrough/PortSwigger/Access Controls/lab11/solved.png]]

Solved!

## 12. Multi-step process with no access control on one step

>[!done]

>[!note]+ Lab description
> - [`Lab: Multi-step process with no access control on one step`](https://portswigger.net/web-security/access-control/lab-multi-step-process-with-no-access-control-on-one-step)
> - Level: #Practitioner 
> 
> This lab has an admin panel with a flawed multi-step process for changing a user's role. You can familiarize yourself with the admin panel by logging in using the credentials `administrator:admin`.
> 
> To solve the lab, log in using the credentials `wiener:peter` and exploit the flawed access controls to promote yourself to become an administrator.


### Solution

- Log in as `administrator`, navigate to the admin panel and promote the `carlos` user to admin. Inspect the requests:

![[images/walkthrough/PortSwigger/Access Controls/lab12/1.png]]


![[images/walkthrough/PortSwigger/Access Controls/lab12/2.png]]

- Notice that you can upgrade and downgrade users by repeating the second request only.
- Send the second request to `Repeater`.
- In an `Incognito` window, log in as `wiener`. Change the username in the `Repeater` request to `wiener` and replace the session ID with your own:

![[images/walkthrough/PortSwigger/Access Controls/lab12/3.png]]

- The request works.

>[!warning] This won't work if you log out of the `administrator` account in the main window.

- The application, apparently, only checks the fact that the `administrator` user is logged-in, but doesn't authorizes the actions based on the session cookie.

![[images/walkthrough/PortSwigger/Access Controls/lab12/solved.png]]

Solved!

## 13. Referer-based access control

>[!done]

>[!note]+ Lab description
> - [`Lab: Referer-based access control`](https://portswigger.net/web-security/access-control/lab-referer-based-access-control)
> - Level: #Practitioner 
> 
> 
> This lab controls access to certain admin functionality based on the Referer header. You can familiarize yourself with the admin panel by logging in using the credentials `administrator:admin`.
> 
> To solve the lab, log in using the credentials `wiener:peter` and exploit the flawed access controls to promote yourself to become an administrator.

### Solution

- Log in as `administrator` and promote `carlos` to admin. Inspect the request:

![[images/walkthrough/PortSwigger/Access Controls/lab13/1.png]]

- Send this request to `Repeater`.

- Log in as `wiener` and attempt to access the administrator panel. Receive `401 Unauthorized` and the message:

```
Admin interface only available if logged in as an administrator
```


![[images/walkthrough/PortSwigger/Access Controls/lab13/2.png]]

- Replace the session ID you `wiener`'s in the request in `Repeater`, and change `username` parameter to `wiener`:

![[images/walkthrough/PortSwigger/Access Controls/lab13/3.png]]

- Apparently, the application bases its access control on the `Referer` header.

![[images/walkthrough/PortSwigger/Access Controls/lab13/solved.png]]

Solved!