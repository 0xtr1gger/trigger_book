---
created: 2026-05-23
tags:
  - web_knowledge_base
status: draft
---

> [!note] This guide covers JWT internals — structure, signing, verification, and the JOSE ecosystem — as foundational knowledge required before approaching JWT-based attacks. See [[JWT attacks]].

## The JOSE framework

- The standards that governs JWT behavior are part of the **JOSE (JavaScript Object Signing and Encryption)** framework.


>**[JOSE (JavaScript Object Signing and Encryption)](https://jose.readthedocs.io/en/latest/)** is a set of IETF standards that provide a standardized framework for securely transmitting claims, including authorization information, between parties using JSON data structures. 

- The JOSE framework is made up of five core specifications:

| Spec    | RFC                                                         | Full name           | Defines                                                                                                                                     |
| ------- | ----------------------------------------------------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **JWT** | [`RFC 7519`](https://datatracker.ietf.org/doc/html/rfc7519) | JSON Web Token      | The token format; a container for claims as a JSON objec                                                                                    |
| **JWS** | [`RFC 7515`](https://datatracker.ietf.org/doc/html/rfc7515) | JSON Web Signature  | How to cryptographically sign a payload; integrity protection mechanisms for arbitrary payloads using digital signatures or MA              |
| **JWE** | [`RFC 7516`](https://datatracker.ietf.org/doc/html/rfc7516) | JSON Web Encryption | How to encrypt a payload for confidentiality; authenticated encryption mechanisms for arbitrary paylo                                       |
| **JWK** | [`RFC 7517`](https://datatracker.ietf.org/doc/html/rfc7517) | JSON Web Key        | A JSON format for representing cryptographic keys, including symmetric keys, RSA keys, EC keys, and key sets (J                             |
| **JWA** | [`RFC 7518`](https://datatracker.ietf.org/doc/html/rfc7518) | JSON Web Algori The algorithms valid for use by JWS, JWE, and JWK, as well as their identifiers (`HS256`, `RS256`, `ES256`, `A256GCM`, `RSA-OAEP`, etc.).  etc.)  |
- The JWT spec ([`RFC 7519`](https://datatracker.ietf.org/doc/html/rfc7519)) defines the container format as a JSON object. It specifies registered claim names (`iss`, `sub`, `aud`, `exp`, etc.) and transport encoding (Base64URL).
- On its own, JWT has **no cryptographic properties**. 
- The JWT payload is either **signed as JWS** or **encrypted as JWE**.

>[!note] Most commonly, a JWT you encounter in a web application is a JWS-signed JWT — a JWS token.


```mermaid
%%{init: {'theme':'dark'}}%%
flowchart TD
    JWT["JWT<br/>Claims container"]

    JWS["signed as JWS"]
    JWE["encrypted as JWE"]

    JWA1["signing algorithms from JWA"]
    JWA2["encryption algorithms from JWA"]

    JWK["JWK key material"]

    JWT --> JWS
    JWT --> JWE

    JWS -->JWA1
    JWE -->JWA2

    JWA1 --> JWK
    JWA2 --> JWK
```


## JWT

>**JWT (JSON Web Token)** is an open standard ([RFC 7519](https://tools.ietf.org/html/rfc7519)) that defines a compact, URL-safe method for representing claims — statements about an entity and additional metadata — as a JSON object that can be digitally signed or encrypted. 

- JWTs are most commonly used in **authentication** and **authorization**.
- A JWT is issued to the client upon successful login. The client subsequently presents the token to the server with each request as proof of identity. 
- The token contains a set of claims — assertions about the subject, issuer, audience, privileges, and token lifetime — encoded as a JSON object.  
- Most commonly, the JWT is cryptographically signed using JWS, so the server can verify the token integrity. 
- JWTs are especially common in **stateless, distributed architectures** — microservices, APIs, SPAs, federated identity protocols such as OAuth .20 and OpenID Connect — because the server **does not need to store session state** on the back-end. 
- Token validation generally requires only the signing key (or public verification key).

> [!note]+ The trade-offs
> 
> 
> - The absence of server-side session state is both a performance advantage and a security implication. 
> - Since tokens are self-contained and typically not tracked by the server, their **revocation is not trivial**.
> - A token generally remains valid until expiration unless additional revocation mechanisms are implemented, such as token blacklists, key rotation, or invalidation or refresh tokens.
> - So, a captured JWT may remain active after logout if the backend relies solely on signature verification and doesn't implement any other ways to invalidate a token. 
> 
> 
> This is unlike session cookies, that are directly stored on the server and can be invalidated anytime. 

## The structure of a JWT

- A JWS-based JWT consists of three Base64URL-encoded parts separated by dots:

```
header.payload.signature
```

 - **Header** — token metadata; typically includes token type (`"typ": "JWT"`) and signing algorithm (`"alg": "HS256"`).
 - **Payload** — claims; the actual data the token carries. 
- **Signature** — cryptographic proof of token integrity and authenticity. 

```JS
JWT = 
	Base64URL(header) + "." + 
	Base64URL(payload) + "." + 
	Base64URL(signature)
```

> [!example]+
> - A complete JWT:
> ```bash
> eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IjB4dHIxZ2dlciIsImlhdCI6MzQ3NTk0Nzg3MjJ9.p_78UqlSg26HS65nwVBXeXFhyIU6Dfxb4nmb8T82Tfo
> ```
> 
>- Decoded:
> 
> ```JSON
> // header
> {
>   "alg": "HS256",
>   "typ": "JWT"
> }
> // payload
> {
>   "sub": "1234567890",
>   "name": "0xtr1gger",
>   "iat": 34759478722
> }
> // signature (binary, Base64URL-encoded)
> p_78UqlSg26HS65nwVBXeXFhyIU6Dfxb4nmb8T82Tfo
> ```
 
>[!note]
>JWT uses **Base64URL encoding** instead of standard Base64. The differences are:
>- No padding characters (`=`) are added.
>- Uses URL-safe characters (`-` and `_` instead of `+` and `/`).
>- Designed to be safely transmitted in URLs or HTTP headers without encoding issues.

>[!note]
>You can experiment with token generation in the [JWT Debugger](https://www.jwt.io/) at [`jwt.io`](https://jwt.io/).

>[!important] Important: security note 
> JWTs are **digitally signed but not encrypted** by default. This means that:
> - Anyone with the JWT token can decode and view the contents of the header and payload.
> - Sensitive information **must never be stored in JWT payloads without encryption** (JWE).
> - The signature guarantees the token's integrity and authenticity but **not confidentiality**.

### Header

>A **JWT header**, also called **JOSE header**, is a JSON object that describes **metadata** needed to process the token. The header typically includes the token type (`"typ": "JWT"`) and signing algorithm (`"alg": "HS256"`); it may also identify the key or certificate used for verification.

```JSON
{
  "alg": "HS256",
  "typ": "JWT"
}
```

- The only mandatory header parameter is `alg`. 
- All others are optional; the most common include `kid`, `jwk`, and `jku`.

| Code  | Name                        | Description                                                                                                                                                                                         |
| ----- | --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `alg` | Algorithm                   | The signing or encryption algorithm; can be `none` or a named algorithm (e.g., `HS256`, `RS256`). Mandatory.                                                                                        |
| `typ` | Type                        | Token type — typically `"JWT"`. Optional but common.                                                                                                                                                |
| `cty` | Content Type                | **Content type**, defined by JWS and JWE and used to convey structural information about the JWT; used when when the payload is itself a JWT.                                                       |
| `kid` | Key ID                      | Identifies which key should be used to verify the signature when the server has multiple keys; case-sensitive, no format constraint in the spec.                                                    |
| `jwk` | JSON Web Key                | Embeds a public key directly in the header; rarely used.                                                                                                                                            |
| `jku` | JSON Web Key Set URL        | A URL pointing to a JWKS (JSON Web Key-Set); the server retches this URL to verify the signature.                                                                                                   |
| `x5c` | x.509 Certificate Chain     | A certificate chain in [RFC 4945](https://datatracker.ietf.org/doc/html/rfc4945) format that corresponds to the private key used to generate the signature; used in certificate-based verification. |
| `x5u` | x.509 Certificate Chain URL | A URL from which the server can retrieve the certificate chain for the signing (private) key.                                                                                                       |
#### Signature algorithms (`alg`)

- The `alg` parameter tells the server which algorithm was used to produce the signature.
- Valid algorithms are defined in [`RFC 7518`](https://datatracker.ietf.org/doc/html/rfc7518) (JWA, JSON Web Algorithms).
- The spec only _requires_ implementations to support `HS256` and `none`, but recommends supporting others.

| `alg` value | Digital Signature or MAC Algorithm             | Implementation Requirements |
| ----------- | ---------------------------------------------- | --------------------------- |
| `HS256`     | HMAC using SHA-256                             | Required                    |
| `HS384`     | HMAC using SHA-384                             | Optional                    |
| `HS512`     | HMAC using SHA-512                             | Optional                    |
| `RS256`     | `RSASSA-PKCS1-v1_5 using SHA-256`              | Recommended                 |
| `RS384`     | RSASSA-PKCS1-v1_5 using SHA-384                | Optional                    |
| `RS512`     | RSASSA-PKCS1-v1_5 using SHA-512                | Optional                    |
| `ES256`     | ECDSA using P-256 and SHA-256                  | Recommended+                |
| `ES384`     | ECDSA using P-384 and SHA-384                  | Optional                    |
| `ES512`     | ECDSA using P-521 and SHA-512                  | Optional                    |
| `PS256`     | RSASSA-PSS using SHA-256 and MGF1 with SHA-256 | Optional                    |
| `PS384`     | RSASSA-PSS using SHA-384 and MGF1 with SHA-384 | Optional                    |
| `PS512`     | RSASSA-PSS using SHA-512 and MGF1 with SHA-512 | Optional                    |
| `none`      | No digital signature or MAC                    | Optional                    |

- Grouping by family:

| Algorithm           | Description                                                |
| ------------------- | ---------------------------------------------------------- |
| `HSxxx`             | Symmetric algorithms; HMAC using a secret key and SHA-xxx. |
| `RSxxx` and `PSxxx` | Asymmetric algorithms; public key signature using RSA.     |
| `ESxxx`             | Asymmetric algorithms; public key signature using ECDSA.   |
>[!note] See [`Testing JSON Web Tokens — OWASP Web Application Security Testing Guide`](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/06-Session_Management_Testing/10-Testing_JSON_Web_Tokens).

>[!bug]  If a server accepts a token with `alg: none` and no signature, any claims in the payload are implicitly trusted without any integrity verification whatsoever. See [[JWT attacks]].
### Payload

>The **JWT payload** is a JSON object containing **claims** — assertions about an entity (typically the authenticated user) and contextual metadata.

```json
{
  "sub": "00000000-0000-0000-0000-000000000001",
  "iss": "example.com",
  "aud": "11111111-1111-1111-1111-111111111111",
  "exp": 1716480400,
  "iat": 1716476800,
  "jti": "22222222-2222-2222-2222-222222222222",
  "email": "user@example.com",
  "role": "user"
}
```

>[!important] Claims in the payload must be unique. 

Claims are classified into three categories:

- **Registered claims**
	- Standardized, predefined claim names from [`RFC 7519`](https://datatracker.ietf.org/doc/html/rfc7519#section-4.1).
	- Recommended but not mandatory.
	- All registered claims are 3 characters long. 
	- For example: `sub` (subject), `exp` (expiration time), `aud` (audience), `jti` (JWT ID), etc.

| Code  | Name            | Description                                                                          |
| ----- | --------------- | ------------------------------------------------------------------------------------ |
| `iss` | Issuer          | The principal (usually an application or service) that issued the JWT.               |
| `sub` | Subject         | The principal that is the subject of the JWT (e.g., the user).                       |
| `aud` | Audience        | Intended recipients of the token; can be a string or array of strings.               |
| `exp` | Expiration Time | The expiration time **after which** the JWT must no longer be accepted.              |
| `nbf` | Not Before      | The time **before which** the JWT must not yet be accepted for processing.           |
| `iat` | Issued At       | The time at which the JWT was issued; can be used to determine the age of the token. |
| `jti` | JWT ID          | A unique identifier of the JWT; can be used to prevent JWT replay attacks.           |

- **Public claims**
	- Publicly defined claims (registered in IANA or agreed conventions).
	- Registered in [IANA JSON Web Token Registry](https://www.iana.org/assignments/jwt/jwt.xhtml).
	- Such claims still should comply with IANA or be publicly defined to avoid collisions (claims must be unique).
	- For example: `name` (full name), `nickname` (casual name), `profile` (profile page URL), `zoneinfo` (time zone), etc.

- **Private claims**
	- Custom claims agreed between parties, with no standard meaning.

>[!important]
>JWT payload data is **not encrypted** by default unless JWE is used. 
>**Sensitive information must not be included in the JWT payloads unless encrypted.**

>[!note]
>**No payload claims are mandatory according to the specification.** 
>Registered claims are **recommended rather than mandatory** for interoperability and common use cases. It's up to the application that implements JWT which fields to consider mandatory.

>[!note] Claims should be  **unique** (no repeated codes).

Below is an extended example of JWT payload that also includes public and private claims:

```JSON
{
  "aud": "85a03867-dccf-4882-adde-1a79aeec50df",
  "exp": 1644884185,
  "iat": 1644880585,
  "iss": "example.com",
  "sub": "00000000-0000-0000-0000-000000000001",
  "jti": "3dd6434d-79a9-4d15-98b5-7b51dbb2cd31",
  "authenticationType": "PASSWORD",
  "email": "email@example.com",
  "email_verified": true,
  "applicationId": "85a03867-dccf-4882-adde-1a79aeec50df",
  "roles": [
    "ceo"
  ]
}
```
### Signature

>The **JWT signature** is used to verify token **integrity**; it serves as a cryptographic proof that the token hasn't been tampered with since it was issued.

```
9jtgxC81-wziY8E8A9TR5hxPF8bkpb6MSJ9mqmhw-bc
```

>[!important] Tokens are signed according to the **JWS (JSON Web Signature)** standard.

> [!important]+ Signature generation
> Signature creation pseudocode for HMAC SHA-256 (`HS256`):
> 
> ```JS
> HMACSHA256(
>       Base64URL(header) + "." +
>       Base64URL(payload),
>       secret)
> ```
> 
> 1. A Base64URL-encoded header is concatenated with a Base64URL-encoded payload by the dot character `.`. 
> 2. The resulting string is passed through a digital signature/MAC algorithm (of the type indicated in the JWT header) and signed with a private key or secret. 
> 3. The output is then again Base64URL-encoded.

>[!important]+ Verification
> When a server receives a JWT, it:
> 4. Separates the token into header, payload, and signature.
> 5. Recomputes the signature from the header and payload using the server's secret key (or public key for asymmetric algorithms).
> 6. Compares the computed signature with the one received.
> 7. If they match, this means the token is intact and authentic; if not, the token is rejected.
> 8. Additionally, claims like `exp`, `nbf`, and `aud` are used to verify token validity.

>[!note] 
>Since the signature is directly derived from the rest of the token, changing a single byte of the header or payload results in an invalid signature.

>[!note] 
>Without knowing the server's secret signing key, it shouldn't be possible to generate the correct signature for a given header or payload.

## How JWTs work in practice

Having discussed the structure of a JWT, let’s now examine how JWTs are used in practice, particularly in web authentication and authorization workflows:

1. The JWT issuer — typically the application’s backend server — creates a new JWT object and sets the payload claims that it wants to include in the token. The claims carry information about the subject (usually a user) and other metadata (e.g., user ID, role, token expiration time).

2. The issuer signs the JWT object using either a **secret key** (for HMAC-based algorithms like `HS256`) or a **private key** (for asymmetric algorithms like `RS256` or `ES256`).

3. The header, payload, and signature are Base64URL-encoded and concatenated together by the dot character `.` to obtain a compact, URL-safe string suitable for transmission over the HTTP - the JWT.

4. The completed JWT is sent to the client (typically within the response body or as a cookie) — usually as the response to a successful authentication request. The client stores the token locally (usually in local/session storage or as a cookie) for later use.

5. For each subsequent request to protected resources, the client includes the JWT in the `Authorization` header, typically using the `Bearer` scheme.

```HTTP
Authorization: Bearer JWT
```

6. The server receives the JWT and verifies its signature using the corresponding secret or public key. If the signature is valid, the server decodes the payload and extracts the claims to identify the user and their permissions. The server then grants or denies access based on these claims. 

7. The server may issue refresh tokens for seamless re-authentication as needed or revoke tokens on logout or other security events.

## Signing JWSs

A JWS can be signed with either:
- A **secret** — a **symmetric key**, commonly HMAC (Hash-based Message Authentication Code);
- A **public/private key pair** — **asymmetric keys**, commonly RSA or ECDSA.
### Symmetric signing — a secret key

>With **symmetric signing** (e.g., HMAC with secret key), the **same secret key** is used to both **sign** (create) and **verify** the JWT.

 Common symmetric signing algorithms include:
 - `HS256`: HMAC with SHA-256
 - `HS384`: HMAC with SHA-384
 - `HS512`: HMAC with SHA-512

>[!note]
>Symmetric signing is generally faster than asymmetric.

Here is how the signature is generated with symmetric cryptography:
1. The JWT header (e.g., `{"alg":"HS256","typ":"JWT"}`) and payload (claims) are Base64URL-encoded.
2. The encoded header and payload are concatenated with a dot (`.`).
3. This string is *hashed* using HMAC with a **secret key**.
4. The resulting signature is Base64URL-encoded and appended to the JWT.

To verify the token, the recipient (server) uses the **same secret key** to recalculate the signature from the received header and payload. If the calculated signature matches the one in the JWT, the token is valid.

```JS
JWS = 
	HMAC_SHA256(Base64UrlEncode(header) + "." + 
	Base64URL(payload), secret_key)

JWT = 
	Base64URL(header) + "." + 
	Base64URL(payload) + "." + 
	Base64URL(JWS)
```

>[!important]
>For symmetric signing to be any useful, the secret key must be exchanged securely and kept confidential by all parties that sign or verify the token. If the key is leaked or cracked, it becomes possible to forge the tokens.
### Asymmetric signing — public/private key pair

>With **asymmetric signing** (e.g., RSA or ECDSA with public/private key pair), a **private key** is used to **sign** the JWT, and a **public key** is used to **verify** the signature. 

Common algorithms include:
- `RS256`: RSA with SHA-256
- `RS384`: RSA with SHA-384
- `RS512`: RSA with SHA-512
- `ES256`: ECDSA with P-256 and SHA-256
- `PS256`: RSA-PSS with SHA-256 (probabilistic signature variant) 

>[!note]
>Asymmetric signing is slower than symmetric algorithms due to the complexity of RSA/ECDSA operations, but generally not a bottleneck for most applications.

With asymmetric signing, the signature is created in a bit different way:
1. The JWT header (e.g., `{"alg":"RS256","typ":"JWT"}`) and payload are Base64URL-encoded.
2. The encoded header and payload are concatenated with a dot (`.`).
3. This resulting string is **hashed** (e.g., SHA-256 for `RS256`).
4. The **hash is encrypted** with the **private key** to create the signature.
5. The signature is Base64URL-encoded and appended to the JWT.

To verify the token, the recipient (server or any party) uses the **public key** to decrypt the signature and obtain the hash value, then recalculate the hash from the received header and payload, and compares the values. If the decrypted hash matches the recalculated hash, the token is valid, otherwise not.

```JS
hash = 
	SHA256(Base64URL(header) + "." + Base64URL(payload))

JWS = 
	RSA(hash, private_key)

JWT = 
	Base64URL(header) + "." + 
	Base64URL(payload) + "." + 
	Base64URL(JWS)
```

>[!important] The public key must be kept in secret by the issuer, but the private one can be shared freely for verification. 

>[!note]
>Asymmetric signing is suitable for distributed systems, microservices, or any scenario where the verifier can't be trusted with the signing key. It's is commonly used by identity providers (e.g., Auth0, Okta) for issuing tokens to third parties.


# drafts
## JWE

>**JWE (JSON Web Encryption)**, defined in [`RFC 7516`](https://datatracker.ietf.org/doc/html/rfc7516), is a IETF standard that provides a standardized syntax for representing encrypted content using JSON. 

Unlike JWS (signed JWT), which only offers integrity, JWE encrypts the payload so only authorized recipients can decrypt it — this adds confidentiality.

JWE is designed for secure transmission of confidential data in JWT — even if intercepted, data can't be read without decryption keys.

### JWE Compact Serialization format

JWE standard defines a **JWE Compact Serialization** format. It consists of **five Base64URL-encoded parts**, separated by dots (`.`):

- **Protected header**
	- A Base64URL-encoded JSON object that specifies metadata about the JWE, including the cryptographic algorithms used for encryption and key management.
	- Common fields include:
		- `alg`: The key management algorithm used to encrypt the Content Encryption Key (CEK), e.g., `RSA-OAEP`, `A256KW`, `ECDH-ES`, `dir` (direct).
		- `enc`: The algorithm used to encrypt the payload, e.g., `A256GCM` (AES Galois Counter Mode) or `A128CBC-HS256` (AES CBC with HMAC-SHA256).
		- `kid` (key identifier)

```JS
JWE = 
	Base64URL(UTF_8(protected_header)) + "." + 
	Base64URL(encrypted_key) + "." +
	Base64URL(initialization_vector) + "." +
	Base64URL(ciphertext) + "." +
	Base64URL(authentication_tag)
```

#### JWT extensions: JWS and JWE

The JWT specification is actually very limited. It only defines a format for representing information, i.e., claims in the JWT payload, as an encoded JSON object to be transferred between the client and server. thus in practice, JWTs are not really used stand-alone. 

JWT claims are encoded as a JSON object that is subsequently wrapped in a JSON Web Signature (JWS) or JSON Web Encryption (JWE) object, or a combination of the two. JWS and JWE are two of the JavaScript Object Signing and Encryption (JOSE) standards. These define a variety of cryptographic objects with syntax based on familiar encoding mechanisms like JSON or Base64.

The JWT spec is extended by both the JSON Web Signature (JWS) and JSON Web Encryption (JWE) specifications.

>JWS (JSON Web Signature), a defined in [`RFC 7515`](https://datatracker.ietf.org/doc/html/rfc7515), represents content secured with digital signatures or Message Authentication Codes (MACs) using JSON-based data structures. The JWS cryptographic mechanisms provide integrity protection for an arbitrary sequence of bytes.

JWS, similar to JWT, consists of tree Base64-encoded and concatenated with dots JWS header, payload, and signature, but in contrast to JWT, JWSs header and payload are cryptographically secured with a JWS signature.  

Some of the commonly used algorithms to sign the JWS Header and Payload are:

- HMAC using SHA-256 or SHA-512 hash algorithms (`HS256`, `HS512`)
- RSA using SHA-256 or SHA-512 hash algorithms (`RS256`, `RS512`)

>JWE (JSON Web Encryption) is a standard defined in [`RFC 7516`](https://datatracker.ietf.org/doc/html/rfc7516) for encrypting data using JSON-based data structures. It uses cryptographic algorithms and identifiers described in the JSON Web Algorithms (JWA) specification and IANA registries defined by that specification.

JSON Web Encryption enables encrypting a token so that only the intended recipient can read it. It standardizes the way to represent the encoded data in a JSON data structure. Representation of the encrypted payload may be by JWE compact serialization or JWE JSON serialization.

The JWE compact serialization form has five main components:

1. JOSE header
2. JWE Encrypted Key
3. JWE initialization vector
4. JWE Ciphertext
5. JWE Authentication Tag

All these components are Base64-encoded and are concatenated using dots (`.`), similar to JWT and JWS.

In other words, a JWT is usually either a JWS or JWE token. When people use the term "JWT", they almost always mean a JWS token. JWEs are very similar, except that the actual contents of the token are encrypted rather than just encoded.




## References

- [`JSON Web Signature (JWS) — RFC 7515`](https://datatracker.ietf.org/doc/html/rfc7515)
- [`JSON Web Encryption (JWE) — RFC 7516`](https://datatracker.ietf.org/doc/html/rfc7516)
- [`JSON Web Key (JWK) — RFC 7517`](https://datatracker.ietf.org/doc/html/rfc7517)
- [`JSON Web Algorithms (JWA) — RFC 7518`](https://datatracker.ietf.org/doc/html/rfc7518)
- [`JSON Web Token (JWT) — RFC 7519`](https://datatracker.ietf.org/doc/html/rfc7519)
- [`JSON Web Token (JWT) — IANA`](https://www.iana.org/assignments/jwt/jwt.xhtml)
- [`JSON Web Key Sets — auth0 Docs`](https://auth0.com/docs/secure/tokens/json-web-tokens/json-web-key-sets)
- [`JSON Web Token — Wikipedia`](https://en.wikipedia.org/wiki/JSON_Web_Token)

- [`Testing JSON Web Tokens — OWASP Web Application Security Testing Guide`](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/06-Session_Management_Testing/10-Testing_JSON_Web_Tokens)

https://www.loginradius.com/blog/engineering/guest-post/what-are-jwt-jws-jwe-jwk-jwa


- https://jwt.io/introduction


https://auth0.com/docs/secure/tokens/json-web-tokens/json-web-token-structure


## drafts



 - Claims can be **registered** (standardized claims like `iss`, `sub`, `aud`, `exp`, etc.), **public** (defined in namespaces or IANA registry), and **private** (custom claims agreed between parties).
 
 - **Signature**
	 - A cryptographic signature; created by signing the encoded header and payload with a secret or private key.
	 - The signature is used to verify token integrity (i.e., that neither the header nor payload was changed along the way).
