---
created: 2026-05-26
---
## OAuth

>**OAuth (Open Authorization)** is an open-standard *authorization* framework ([`RFC 6749`](https://datatracker.ietf.org/doc/html/rfc6749))  for access delegation. It allows a resource owner to grant a third-party client application scoped, delegated access to protected resources hosted on a resource server — without sharing the resource owner's credentials with that client.

- **OAuth is an authorization framework** (*not* an authentication protocol) that enables **secure delegation of access rights**.

>[!important] OAuth grants _permissions_. It does not assert _identity_.

- Its main purpose is to allow a user to grant a third-party application **limited access** to their resources on another server (*resource server*, e.g., Google, GitHub, Facebook) **without sharing their username and password** with that third-party app.

>[!important] OAuth is used for **granting and managing access tokens** for specific scopes and permissions; it focuses on **authorization**, and not authenticatoin.

>[!note] Because OAuth itself is not designed for authentication, OpenID Connect (OIDC) was built as an identity layer on top of OAuth 2.0. OIDC adds authentication capabilities (such as returning an `id_token` with user identity information) while still using OAuth authorization flow.

>[!interesting] The predecessor of OAuth 2.0, OAuth 1.0a, is fundamentally different in design and is not used today. 
## OAuth roles

OAuth defines four key [roles](https://datatracker.ietf.org/doc/html/rfc6749#section-1.1):

>A **Resource Owner** is the entity (typically a human user) who holds ownership of protected resources and has the authority to grant delegated access to those resources.

>A **Resource Server** is the server that hosts protected resources and enforces access control by validating access tokens presented in incoming requests.

>A **Client** is the application that requests access to protected resources on behalf of the resource owner. It receives an access token from the authorization server and presents it to the resource server to obtain the resources.

>An **Authorization Server** is the server responsible for authenticating the resource owner, obtaining their consent for access delegation, and issuing access tokens (and optionally refresh tokens) to the client.

- In many cases, the authorization server and resource server are operated by the same entity (e.g., GitHub both authenticates you and hosts your data).

>[!example]+ Example: "Login via GitHub" on `example.com`
>- Suppose you want to authenticate to `example.com` via GitHub.
>- You are (the end user) is the **Resource Owner**. You hold ownership of protected resources — your profile, email, and username in GitHub.
>- `example.com` acts as **Client** that wants to obtain access to your data hosted on GitHub to authenticate you.
>- GitHub is both the **Authorization Server** (it authenticates you, gets your consent for access delegation, and issues access tokens) and **Resource Server** (it hosts your data and verifies access tokens in requests from `example.com`).
>- The client (`example.com`) never sees your GitHub password. It receives a token with a defined scope, uses that token to call the GitHub API, and uses the returned data (e.g., your email) to identify you within its own system.

## OAuth tokens and codes

- OAuth operates with four main types of tokens/codes:
	- **Authorization code**
	- **Access token**
	- **Refresh token**
	- **ID token** (OpenID Connect)

### Authorization code

>An **authorization code** is a short-lived, single-use opaque credential issued by the authorization server to the client after the resource owner has successfully authenticated and consented to the requested scopes. 

- The authorization code itself grants nothing, but it can be used to request an **access token** in a server-to-server exchange with the authorization server that never touches the user's browser. 
- This mechanism was designed to prevent tokens from being exposed in browser history. 
- The specification recommends a maximum authorization code lifetime of **10 minutes**. In practice, it it typically between **30 and 60 seconds**. This ensures the code is used immediately and reduces the risk of leaks.
- The authorization code is **single-use**. The authorization server must invalidate it immediately upon redemption. If a code is presented twice, the server should revoke any 

>[!note] The short lifespan and single-use constraint mean that intercepting an authorization code is a race condition. You'd need to redeem it before the legitimate client does. This is harder than stealing a long-lived token, which is why PKCE was designed to protect against code interception scenarios, not just code theft.

- Access codes are used in the **Authorization Code Grant flow**, the most commonly used grant type in OAuth. 
### Access token

>An **access token** is a bearer credential issued by the authorization server to the client, representing the authorization granted by the resource owner, and used by the client to access protected resources on the resource server within the bounds of the granted scopes and token lifetime.

- Access tokens are **bearer tokens**: possession is sufficient for access. 
- There is no cryptographic binding between the token and the client that originally received it (in standard OAuth 2.0 without extensions like DPoP or mTLS). 
- If you obtain a valid access token, you can use it directly.

---
- The access token is usually included in the `Authorization` HTTP header in API requests: 

```HTTP
Authorization: Bearer <token>
```

- The resource server then validates the access token and grants access to protected data or APIs.
- Access tokens come in two forms: 
	- **Opaque strings**
		- Random identifiers with no client-readable meaning.
		- The resource server must call the authorization server's introspection endpoint (`/introspect`) to validate them and retrieve the associated claims.
	- **Structured tokens (JWTs)**
		- JSON Web Tokens ([[🛠️ JWT|JWTs]]), self-contained tokens that encode claims directly and are cryptographically signed (typically using `RS256` or `HS256`).

- When access tokens are JWTs, they encode:
	- `iss` — Issuer.
	- `aud`  — Audience or resource server.
	- `exp` — Expiry time.
	- `scope` — Permissions granted.
	- Other custom claims.

>[!example]+
> ```JSON
> {
>   "iss": "https://authentication-server.example.com",
>   "aud": "https://resource-server.example.com",
>   "sub": "user_11"
>   "iat": 1788048000,
>   "exp": 1788049800,
>   "scope": "read:email profile",
>   "client_id": "webapp_client_01"
> }
> ```

- Access tokens are typically short-lived — commonly 5 to 60 minutes. This limits the damage if the token is stolen.
- Once expired, tokens are useless, and have to be renewed. 
- Once expired, access tokens have to be renewed if access to resources is still needed. This can be done either by issuing a fresh new token (the user has to re-authenticate), or a token can be refreshed (with a refresh token) without user re-authentication.
### Refresh token

>A **refresh token** is a long-lived credential issued by the authorization server alongside an access token, used by the client to obtain new access tokens after the current one expires, without requiring the resource owner to re-authenticate.

- Refresh tokens are optional but widely used because they improve user experience significantly — without them, users would need to re-authorize every time the access token expires. 

>[!important] Per [`RFC 6749`](https://datatracker.ietf.org/doc/html/rfc6749), refresh tokens should only be issued to confidential clients that can store them securely (e.g., not SPAs or native apps).

- Refresh tokens are **long-lived** and may be valid for days, weeks, or indefinitely until explicitly revoked.
- A stolen refresh token effectively grants persistent access until discovered and revoked.
- Refresh tokens are exchanged server-to-server and must never appear in the browser URL or client-side JavaScript.

>[!note]+ Refresh token rotation 
>- Refresh token rotation means the authorization server issues a new refresh token each time the old one is used to get a new access token. The old token is simultaneously invalidated. 
>- If you steal a refresh token and use it after the legitimate client already used it (or vice versa), the server can detect the replay: both tokens become invalid, and the user's session is forcibly terminated. 

### ID Token (OpenID Connect specific)

> An **ID token** is a signed JWT issued by an OpenID Connect provider that encodes claims about the authentication event and the authenticated user, and is intended for consumption by the client application to establish user identity (not for presentation to resource servers).

- ID tokens are specific to OpenID Connect, not OAuth 2.0 itself (see the [[#OpenID Connect]] section).
## Client types — confidential vs. public

In OAuth 2.0, clients are divided into two main types based on their ability to securely store credentials (e.g., `client_secret`):

- **Confidential clients**, or **private clients**
	- Applications that are architecturally capable of storing credentials — such as a `client_secret`, private key, or certificate — in a secure, server-side environment inaccessible to resource owners or other external parties, and that can authenticate to the token endpoint using those credentials.
	- These are typically server-side rendered web applications and backend services deployed in controlled environments (cloud VMs, on-premises services). The `client_secret` lives on the server and is never sent to the user's browser.

>[!note] The most commonly used grant type for confidential clients is **Authorization Code Grant**.


- **Public clients**
	- Applications that run in environments where credentials cannot be stored securely — either because the application code runs on end-user devices (mobile applications, desktop applications) or is delivered directly to the browser (SPAs, Single-Page Applications) — and therefore cannot authenticate to the token endpoint with a static secret.
	- For public clients, the `client_secret` used in Authorization Code Grant type would be immediately discoverable: in the APK, in the JavaScript bundle, in the binary.
	- Such clients typically use **Authorization Code Grant with Proof Key for Code Exchange (PKCE)** instead.

## Authorization Grant types

- A **grant type** (also called an **OAuth flow**) defines the mechanism by which a client obtains an access token. 
- Different grant types are suited to different deployment contexts, client types, and security requirements. Choosing the wrong grant type for a context is itself a vulnerability.

| Grant type                | Best for                                    | User interaction  | Security level | Token delivery                         |
| ------------------------- | ------------------------------------------- | ----------------- | -------------- | -------------------------------------- |
| Authorization Code        | Confidential clients (server-side web apps) | Yes               | High           | Code → server-to-server token exchange |
| Authorization Code + PKCE | Public clients (SPA, mobile)                | Yes               | High           | Code → server-to-server token exchange |
| Implicit (Deprecated)     | Public clients                              | Yes               | Low            | Token directly in URL fragment         |
| Client Credentials        | Machine-to-machine / service accounts       | No                | High           | Direct token issuance                  |
| ROPC (Deprecated)         | Highly trusted first-party clients          | Yes               | Low–Moderate   | Direct token issuance                  |
| Device Authorization      | Input-limited devices (TV, printer)         | Yes (out-of-band) | Moderate       | Polling-based                          |

- Modern best practice (and the direction of OAuth 2.1) is to reduce this list to essentially two viable options for new implementations: 
	- **Authorization Code + PKCE** (for all user-facing flows)
	- **Client Credentials** (for machine-to-machine). 
- Everything else carries deprecation warnings or significant security caveats.
## Authorization Code Grant

 - The **Authorization Code Grant** is the most commonly used OAuth flow. It is designed for confidential clients and provides the strongest security guarantees.
- The **access token is never exposed to the user's browser**. The browser only ever sees the authorization code that is later exchanged to an access token, server-to-server between the client and the authorization server.
---
- Authorization Code Grant flow:
	1. **Authorization Request**
	2. **Resource Owner authentication and consent**
	3. **Authorization Response**
	4. **Access Token Request**
	5. **Access Token Response**
	6. **Resource request**
	7. **Resource grant**
### 1. Authorization Request

- The client sends an **Authorization Request** and redirects the user's browser to the authorization server's `/authorize` endpoint (or similar).

```HTTP
GET /authorize?
  response_type=code&
  client_id=CLIENT_ID&
  redirect_uri=https%3A%2F%2Fclient.example.com%2Foauth%2Fcallback&
  scope=read%3Aemail%20profile&
  state=CSRF_TOKEN
HTTP/1.1
Host: authorization-server.com
```

- `response_type=code`
	- Indicates to the authorization server that this is an **Authorization Code Grant**, and that the response should contain an authorization code (not a token directly).
- `client_id`
	- The public identifier for the registered client application; not secret.
- `redirect_uri`
	- The callback URL where the authorization server should redirect the user's browser after authentication and consent.

 >[!note] So, once you have authenticated to the authorization server and have given your consent for the client to access your data, the authorization server redirects you back to the client at the endpoint specified in `redirect_uri`.
 
- `scope`
	- A space-separated list of permissions the client is requesting. The user will see these on the consent screen.
- `state`
	- A CSRF token. 
	- The client generates this value, stores it in the user's session, and expects it back unchanged in the callback. 
	- This binds the callback to the original request and prevents CSRF attacks on the OAuth flow. 

>[!note] See https://datatracker.ietf.org/doc/html/rfc6749#section-4.1.1.

### 2. Resource Owner authentication and consent

- The authorization server receives the request, authenticates the user (via login form if not already authenticated), and presents a consent screen listing the requested scopes. 
- The user explicitly approves or denies access.
---
- This step is entirely within the authorization server's domain. The client application doesn't see what happens here at all.
### 3. Authorization Response

- Upon successful authentication and consent, the authorization server issues a `302` redirect back to the client's `redirect_uri`. 
- The authorization code is sent in the `code` URL parameter, and the original `state` value (CSRF token) is sent in the `state` parameter.

```http
HTTP/1.1 302 Found
Location: https://client.example.com/oauth/callback?code=AUTHORIZATION_CODE&state=CSRF_TOKEN
```

- The user's browser follows the redirect and makes a `GET` request to the client's callback endpoint. 
- The authorization code travels through be browser to the client. 
- However, the authorization code alone is an opaque string that can't be used without the `client_secret`. 

>[!note] See https://datatracker.ietf.org/doc/html/rfc6749#section-4.1.2.
### 4. Access Token Request

- The client extracts the authorization code from the callback request and exchanges it for an access token via a direct `POST` request to the authorization sever's `/token` endpoint. 
- This exchange happens server-to-server — entirely outside the browser. 
- The client authenticates itself to the authorization server in this request using its `client_secret`.

```http
POST /token HTTP/1.1
Host: auth.example.com
Authorization: Basic Q0xJRU5UX0lEOkFVVEhPUklaQVRJT05fQ09ERQ==
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
code=AUTHORIZATION_CODE&
redirect_uri=https%3A%2F%2Fclient.example.com%2Foauth%2Fcallback
```

- The `Authorization: Basic` header contains `Base64(client_id:client_secret)`. 
- The client authenticates itself here, and the authorization server verifies:
	1. The code is valid and has not been used before.
	2. The code has not expired.
	3. The `client_id` matches the one that originally requested the code.
	4. The `redirect_uri` matches the one in the original authorization request.

>[!note]+ Alternatively, the client can send its `client_id` and `client_secret` in the `POST` body (plaintext) rather than Base64-encoded in the `Authorization` header. This method is less preferred but common. 
> ```HTTP
> POST /token HTTP/1.1
> Host: authorization-server.com
> Content-Type: application/x-www-form-urlencoded
> 
> grant_type=authorization_code&
> code=AUTHORIZATION_CODE&
> redirect_uri=https%3A%2F%2Fclient.example.com%2Foauth%2Fcallback&
> client_id=CLIENT_ID&
> client_secret=CLIENT_SECRET
> ```

>[!note] See https://datatracker.ietf.org/doc/html/rfc6749#section-4.1.3.
### 5. Access Token Response

- If all validation passes, the authorization server issues an access token (and optionally a refresh token) to the client in a JSON response.

```HTTP
HTTP/1.1 200 OK
Content-Type: application/json;charset=UTF-8
Cache-Control: no-store
Pragma: no-cache
```

```JSON
{
  "access_token": "ACCESS_TOKEN",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "REFRESH_TOKEN",
  "scope": "read:email profile"
}
```

- `Cache-Control: no-store` and `Pragma: no-cache` are mandatory response headers on the token endpoint to prevent tokens from being cached by intermediary proxies.
- `scope` in the response may be a _subset_ of what was requested.
### 6. Resource request

- With a valid toke, the client calls the resource server's API on the user's behalf to request their data.
- The access token is sent in the `Authorization` header, Base64-encoded. 

```HTTP
GET /resource/user/email
Host: resource-server.com
Authorization: Bearer QUNDRVNTX1RPS0VO
```
### 7. Resource grant

- The resource server validates the access token  — either by introspection (for opaque tokens) or by verifying the JWT signature and claims (for structured tokens). 
- If valid and the required scope is present, it returns the requested resource.


```json
{
  "user_id": "user_abc123",
  "email": "jane@example.com",
  "name": "Jane Doe"
}
```
## Implicit Grant (deprecated)

- The **Implicit Grant** was designed for single-page applications (SPAs) and public (non-confidential) clients that could not initiate server-to-server requests. 
- It eliminates the back-channel token exchange entirely: the authorization server returns the access token directly in the URL fragment of the redirect. 

>[!warning] **Implicit Grant is deprecated in OAuth 2.1 and should not be implemented in new systems.**

- However, it still exists in older applications.
---
- Implicit Grant flow:
	1. **Authorization Request**
	2. **Resource Owner authentication and consent**
	3. **Access Token Response (URL fragment)**
	4. **Resource Request and Grant**

>[!bug]+ Why Implicit Grant is insecure
>The token is directly exposed in the browser environment:
>- **Browser history** — Any other JavaScript running on the page, or anyone with access to the browser, can read it.
>- **`Referer` header leakage** — If the SPA navigates to another page or loads a third-party resource after receiving the token, the full URL (including the fragment, in some implementations) may lead in the `Referer` header. 
>**- Cross-Site Scripting** — Any [[XSS]] vulnerability in the application gives an attacker access to `window.location.hash` and therefore the live access token.
>- **No client authentication** — There is no `client_secret` exchange. The authorization server can't verify that the entity receiving the token is actually the registered client. 
>- **No refresh tokens -> long-lived access tokens** — When the token expires, the user must re-authorize. This pushes some developers toward very long-lived access tokens in implicit grant deployments, which increases the exposure window.

>[!note] The modern replacement for Implicit Grant in public clients is **Authorization Code + PKCE**. 
### 1. Authorization Request

- Similar to Authorization Code Grant, the client sends an **Authorization Request** and redirects the user's browser to the authorization server's `/authorize` endpoint (or similar).

```HTTP
GET /authorize?
  response_type=token&
  client_id=CLIENT_ID&
  redirect_uri=https%3A%2F%2Fclient.example.com%2Foauth%2Fcallback&
  scope=read%3Aemail%20profile&
  state=CSRF_TOKEN
HTTP/1.1
Host: authorization-server.com
```

- `response_type=token` distinguishes this from the Authorization Code Grant. The authorization server knows to return a token, not a code.
### 2. Resource Owner authentication and consent 

- Same as Authorization Code Grant: the user logs in and approves access on the authorization server.
### 3. Access Token Response (URL fragment)

- Upon successful authentication and consent, the authorization server `302`-redirects the user back to the client's `redirect_uri`.
- The access token is delivered in the **URL fragment** (`#access_token=...`).
- URL fragments are never sent to the server in HTTP request — the browser handles them client-side.

```http
HTTP/1.1 302 Found
Location: https://authorization-server.com/callback#access_token=ACCESS_TOKEN&token_type=bearer&expires_in=3600&state=CSRF_TOKEN
```

- The SPA reads the token from `window.location.hash` using JavaScript. 
- No authorization code exchange. No `client_secret`. The token is live in the browser from the moment the redirect fires. 
### 4-5. Resource Request and Grant 

- Identical to the Authorization Code flow from this point — the client presents the bearer token to the resource server.

## PKCE Grant

 - The **Proof Key for Code Exchange (PKCE)** is a security extension for the Authorization Code Grant defined in [`RFC 7636`](https://datatracker.ietf.org/doc/html/rfc7636), specifically designed to protect **public clients** like SPAs and native mobile apps from **code interception attacks**.
---
>[!interesting] **PKCE was originally designed for public clients** that can't securely store client secrets (for example, mobile apps), to prevent authorization code interception attacks.

- Modern best practice and the OAuth 2.1 draft specify PKCE for **all authorization code flows, including those used by confidential clients**. There is no scenario where PKCE makes a flow _less_ secure, and it adds meaningful defense-in-depth.

- PKCE Grant flow:
	1. **Client generates a Code Verifier and Code Challenge**
	2. **Authorization Request**
	3. **Authorization Response**
	4. **Access Token Request**
	5. **Access Token Response**

>[!important]+ PKCE security
> - PKCE defends specifically against **authorization code interception**: scenarios where the code is stolen in transit (malicious redirect URI handler on the same device, network-level interception). The proof key is generated fresh per-request, never transmitted before it needs to be verified, and the challenge can only be validated by someone who knows the original verifier.
> 
> - It does **not** replace `state`-based CSRF protection. Both should be present.

### Why PKCE exists

- The original Authorization Grant Code flow has a weakness: if someone steals the **authorization code**, they can exchange it for an access token. PKCE makes the authorization code useless to an attacker unless they also possess a secret that was generated by the original client.

>[!example]+
> - Imagine a mobile app:
> 	1. The app sends the user to the authorization server (Authorization Request).
> 	2. The user logs in.
> 	3. The authorization server redirects back with an authorization code. 
> 	4. The app exchanges that code for an access token.
> 
>- The vulnerability is in step `3.` On mobile devices (and sometimes browsers) another app or intermediary could intercept the authorization code. Without PKCE, the attacker can immediately redeem the code and get the token.

- Before starting the login flow, the client computes two values:
	- **Code verifier** (a random string).
	- **Code challenge** (a SHA-256 hash of the code verifier).

> A **code verifier** is a high-entropy, cryptographically random string of 43-128 characters from the `[A-Z a-z 0-9 - . _ ~]` character set, generated by the client for a single authorization request. 

> A **code challenge** is a transformed derivative of the code verifier, sent to the authorization server in the authorization request. It can either be a copy of the code verifier (`plain`) or its SHA-256 hash (`S256`).



### 1. Client generates a Code Verifier and Code Challenge

- Before making the authorization request, the client generates a fresh `code_verifier` (stored locally, never transmitted until the token exchange) and derives the corresponding `code_challenge`.
### 2. Authorization Request

- The client sends an **Authorization Request** and redirects the user's browser to the authorization server's `/authorize` endpoint (or similar).

```http
GET /authorize?
  response_type=code&
  client_id=CLIENT_ID&
  redirect_uri=https%3A%2F%2Fclient.example.com%2Foauth%2Fcallback&
  scope=read%3Aemail%20profile&
  state=CSRF_TOKEN&
  code_challenge=CODE_CHALLENGE&
  code_challenge_method=S256
HTTP/1.1
Host: authorization-server.com
```

- `response_type=code`
	- Indicates to the authorization server that this is an **Authorization Code Grant**, and that the response should contain an authorization code (not a token directly).
- `code_challenge`
	- The code challenge derived from the code verifier using the method specified in the `code_challenge_method` parameter.
- `code_challenge_method`
	- Specifies how the code challenge was derived from the code verifier: `plain` or `S256`.
- The presence of `code_challenge` and `code_challenge_method` indicates PKCE.

### 3. Authorization Response

- Once the client authenticates and gives consent, the Authorization Server issues an authorization code. 
- The authorization code is associated with the `code_challenge` and `code_challenge_method` values for later verification (these values are typically stored encrypted on the server).
- The response looks exactly like in the Authorization Code Grant.

```http
HTTP/1.1 302 Found
Location: https://client.example.com/oauth/callback?code=AUTHORIZATION_CODE&state=CSRF_TOKEN
```

- Even if an attacker intercepts the authorization code here, **it is useless without `code_verifier`**, because the code is bound to the `code_challenge` the Authorization Server stores.
### 4. Access Token Request

- The client sends the authorization code and the original `code_verifier` (not the challenge) to the Authorization Server's `/token` endpoint.

```HTTP
POST /token HTTP/1.1
Host: authorization-server.example.com
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
code=AUTHORIZATION_CODE&
redirect_uri=https%3A%2F%2Fclient.example.com%2Foauth%2Fcallback&
client_id=CLIENT_ID&
code_verifier=CODE_VERIFIER
```

- There is no `client_secret` here for a public client. The PKCE verification is the authentication mechanism.
### 5. Access Token Response

- The Authorization Server recomputes the `code_challenge` from the submitted `code_verifier` using the stored `code_challenge_method`, and compares it against the stored `code_challenge`. If they match, the access token is issued.

```HTTP
HTTP/1.1 200 OK
Content-Type: application/json;charset=UTF-8
Cache-Control: no-store
Pragma: no-cache
```
```JSON
{
  "access_token": "ACCESS_TOKEN",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "REFRESH_TOKEN",
  "scope": "read:email profile"
}

```

- If they do not match, the server must return an error and must not issue a token. 
- An attacker who intercepted the authorization code but does not know the `code_verifier` can't pass this verification.

## Client Credentials Grant

- The **Client Credentials Grant** is designed for **machine-to-machine (M2M)** or **server-to-server** scenarios where there is no resource owner to authenticate (no user interaction).
- It allows a **confidential client** application to authenticate itself using its own **client ID** and **client secret** to obtain an access token from the authorization server.

>[!note] There is no user involved. No authorization code. No redirect. The client authenticates directly with its `client_id` and `client_secret` and receives an access token.


1. Token request

2. Token Response



3. **Client authentication**
	- The client authenticates with the authorization server using its Client ID and secret.

4. **Token request**
	- The authorization server issues an access token.

5. **Resource access**
	- The client uses the access token to access resources.

Notice that here, **no user authentication or consent is involved** — the client utilizes user credentials directly. 
This grant type is often used for backend services or APIs.

---

4. The Client uses the Resource Owner's credentials to authenticate with the Authorization Server.
5. The Authorization Server issues an access token.
6. The Client uses the token to request Resources (e.g., email address) from the Resource Server.
7. The Resource Server returns requested resources, and the Resource Owner is authenticated to the Client application.
## OIDC

>**OpenID Connect (OIDC)** is an identity authentication protocol built on top of the **OAuth 2.0** authorization framework, published by the **OpenID Foundation** in **2014**.

- OIDC allows third-party applications (Relying Parties) to verify end-user identities and obtain basic profile information from an OpenID Provider (OP) or Identity Provider (IdP).
- The protocol solves the main OAuth problem: OAuth is not an authentication protocol, and using it without additional structures leads to vulnerabilities. 

>[!note] See [`OpenID Connect Core 1.0 — openid.net`](https://openid.net/specs/openid-connect-core-1_0.html).

### OIDC roles

- OIDC roles are almost the same as OAuth, but the terminology differs:
	- **Relying party** — The application that requesting authentication of a user; synonymous with the OAuth client.
	- **End user** — The user who is being authenticated; synonymous with the OAuth resource owner. 
	- **OpenID provider** — An OAuth service that is configured to support OpenID Connect; synonymous with OAuth authorization and resource servers.

### Scopes

- While each OAuth provider introduces unique scopes, OIDC defines a standard set of scopes providers can include:
	- `openid`
	- `profile`
	- `email`
	- `address`
	- `phone`

>[!important] To use OpenID Connect, the client application must specify the scope `openid` in the authorization request.

- Each of these scopes corresponds to read access for a subset of claims about the user that are defined in the OpenID specification.

### ID token

- OpenID Connect adds the `id_token` response type. This returns a [[🛠️ JWT]] signed with a JWS. 
- The JWT payload contains a list of claims based on the scope that was initially requested. It also contains information about how and when the user was last authenticated by the OAuth service. The client application can use this to decide whether or not the user has been sufficiently authenticated.

```json
{
  "iss": "https://oidc-server.com",
  "sub": "jane_doe",
  "aud": "CLIENT_ID",
  "exp": 1726809100,
  "iat": 1726805500,
  "auth_time": 1726805400,
  "nonce": "NONCE",
  "email": "jane_doe@example.com",
  "name": "Jane Doe"
}
```

- `id_token` is designed in a way that reduces the number of requests that need to be sent between the client application and the OAuth service. The token with all the necessary data is sent to the client immediately after the the user has authenticated themselves.

### OpenID Connect discovery 

- Authorization servers implementing OIDC publish a discovery document at:

```http
/.well-known/openid-configuration
```

- The public keys used to sign the JWTs cat be found at:

```http
/.well-known/jwks.json
```
## References and further reading

- [`OAuth and OIDC Specifications — spring-projects/spring-authorization-server, GitHub`](https://github.com/spring-projects/spring-authorization-server/wiki/OAuth2-and-OIDC-Specifications)

- TODO:
	- Client Credentials Grant
	- Device Authorization Grant
	- ROPC (deprecated)
	- Scopes
	- Full OIDC flow (if needed)
# drafts




## Device Authorization

The Device Authorization is used for devices with limited input capabilities, such as TVs or printers. 
The process looks like this:

1. **Device request**
	- The device requests authorization from the authorization server.

2. **User authorization**
	- The user is given a code to enter on a separate device or web age to grant access.

3. **Token issuance**
	- Once the user approves, the device polls the authorization server for an access token.

## ROPC (Deprecated)

>The **Resource Owner Password Credentials (ROPC) grant flow** in OAuth 2.0 is a deprecated and less commonly used. In ROPC, the application directly collects the user's username and password, and exchanges these credentials for an Access Token from the Authorization Server.

The Resource Owner Password Credentials grant is used when the Client is highly trusted by the Resource Owner, such as with first-party applications (e.g., first-party mobile or desktop applications).

### ROPC flaw

1. **Resource Owner provides their username and password**
2. **Access Token Request**
3. **Access Token Response**
#### 1. Resource Owner provides their username and password

- The Resource Owner, user, provides their username and password _directly_ to the Client application (e.g., a mobile or desktop app).
- Unlike other flows, the user does _not_ authenticate via redirection to the authorization server’s login page.
#### 2. Access Token Request

The Client sends  a `POST` request to the Authorization Server's `/token` endpoint, the **Access Token Request**.

The Access Token Request looks like this:

```HTTP
POST /token HTTP/1.1
Host: authorization-server.example.com
Content-Type: application/x-www-form-urlencoded

grant_type=password&
username=USERNAME&
password=PASSWORD&
client_id=CLIENT_ID&
client_secret=CLIENT_SECRET&
scope=email:read

```

- `grant_type`
	- Always set to `password` to indicate a Resource Owner Password Credentials Grant.

- `username`
	- The user's identifier/username.

- `password`
	- The user's password.

- `client_id`
	- This is the **unique public identifier** assigned to the Client application when it registers with the Authorization Server. It allows the Authorization Server to identify which application is making the authorization request.

- `client_secret` (Required only for confidential clients)
	- The Client’s secret (for confidential clients); public clients may not require this, depending on server policy.

- `scope` (Optional)
	- The scope; a space-delimited list of permissions requested.

#### 3. Access Token Response

If successful, the server responds with a JSON payload:

```JSON
{
  "access_token": "ACCESS_TOKEN",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "REFRESH_TOKEN",
  "scope": "read:emal"
}
```

- `access_token`
	- The Access Token to access APIs/resources.

- `token_type`
	- Usually `Bearer`.
    
- `expires_in`
	- Access Token lifetime in seconds.
    
- `refresh_token`
	- A Refresh Token, used to obtain new access tokens (if provided).
    
- `scope`
	- Confirmed scopes for the token session.

## Scopes

>**OAuth scopes** define what actions a client application is allowed to perform on behalf of the user.

Scopes are strings that represent the specific permissions an application requests to access a user’s resources. For example, a scope like `read:email` allows the app to read the user’s emails, and `write:profile` might allow editing profile information.

- Scopes are included in the OAuth authorization request as a space-separated list, e.g., `scope=read:email write:profile`.
- The user is shown a consent screen listing the scopes requested by the application and can approve or deny each scope.
- The resource server must enforce that the access token only allows actions within the granted scopes.

Each Resource server defines their own scopes. Here are some examples in popular services:

- [Slack](https://api.slack.com/docs/oauth-scopes)
- [GitHub](https://developer.github.com/apps/building-oauth-apps/understanding-scopes-for-oauth-apps/)
- [Google](https://developers.google.com/identity/protocols/googlescopes)
- [FitBit](https://dev.fitbit.com/build/reference/web-api/developer-guide/application-design/#Scopes)


| Role                     | Description                                                                                                            |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| **Resource Owner**       | The entity (usually the end user) who owns the data or resource.                                                       |
| **Resource Server**      | The server hosting the protected resources (APIs, data, files, etc.).                                                  |
| **Client**               | The application that requests access to the protected resources on behalf of the resource owner                        |
| **Authorization Server** | The server that authenticates the resource owner and issues access tokens to the client after after obtaining consent. |


---

- **Authorization Code Grant**
- **Implicit Grant**
- **Resource Owner Password Credentials Grant**
- **Client Credentials Grant**
- **Device Authorization Grant**
- **PKCE Grant
- **OpenID Connect**



>[!definition] The **Authorization Code Grant** is a foundational and secure flow in OAuth 2.0, primarily designed for confidential (private) Clients. The user's credentials and tokens are never exposed directly in the user's browser; instead, a one-time authorization code is issued, which is later exchanged server-to-server for an access token.

- The **Authorization Code Grant** is by far the most commonly used grant type in OAuth. 
- The authorization code is exchanged for an access token server-to-server, meaning the **access tokes are not exposed in the user agent (browser) at all**. This reduces the risk of token leakage. 
 - The Authorization Code Grant type also supports **refresh tokens** to maintain long-term access without repeated user authentication.

