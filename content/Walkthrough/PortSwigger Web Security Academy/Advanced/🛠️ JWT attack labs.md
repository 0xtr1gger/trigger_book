---
created: 2026-05-23
---
| `#`  | Solved? | Name                                                        | Date    |
| ---- | ------- | ----------------------------------------------------------- | ------- |
| `1.` | `✓`     | JWT authentication bypass via unverified signature          | `23.05` |
| `2.` | `✓`     | JWT authentication bypass via flawed signature verification | `23.05` |
| `3.` | `✓`     | JWT authentication bypass via weak signing key              | `24.05` |
| `4.` | `✓`     | JWT authentication bypass via `jwk` header injection        | `24.05` |
| `5.` | `✓`     | JWT authentication bypass via `jku` header injection        | `26.05` |
| `6.` | `✓`     | JWT authentication bypass via `kid` header path traversal   | `27.05` |

## 1. JWT authentication bypass via unverified signature

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: JWT authentication bypass via unverified signature`](https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-unverified-signature)
> - Level: #Apprentice 
> 
> This lab uses a JWT-based mechanism for handling sessions. Due to implementation flaws, the server doesn't verify the signature of any JWTs that it receives.
> 
> To solve the lab, modify your session token to gain access to the admin panel at `/admin`, then delete the user `carlos`.
> 
> You can log in to your own account using the following credentials: `wiener:peter`
### Solution

- Log in as `wiener`. Observe the session cookie the application issues is a JWT:

![[images/walkthrough/PortSwigger/JWT/lab1/1.png]]

- Inspect the JWT ([`jwt.io`](https://jwt.io)):

![[images/walkthrough/PortSwigger/JWT/lab1/2.png]]

- The signing algorithm is set to `RS256`. 

- Attempt the access the `/admin` endpoint:

![[images/walkthrough/PortSwigger/JWT/lab1/3.png]]

- The application responds with `403` unauthorized; the error message says the user must be `adminitrator`.
- To check if the application actually verifies the JWT, change `sub` in the JWT payload from `wiener` to `administrator` and send the request:

![[images/walkthrough/PortSwigger/JWT/lab1/4.png]]

- The application lets you in. Repeat the request changing the path to `/admin/delete?username=carlos`:

![[images/walkthrough/PortSwigger/JWT/lab1/5.png]]

![[images/walkthrough/PortSwigger/JWT/lab1/solved.png]]

Solved!

## 2. JWT authentication bypass via flawed signature verification

>[!done]

>[!note]+ Lab description
> - [`Lab: JWT authentication bypass via flawed signature verification`](https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-flawed-signature-verification)
> - Level: #Apprentice 
> 
> This lab uses a JWT-based mechanism for handling sessions. The server is insecurely configured to accept unsigned JWTs.
> 
> To solve the lab, modify your session token to gain access to the admin panel at `/admin`, then delete the user `carlos`.
> 
> You can log in to your own account using the following credentials: `wiener:peter`

### Solution

- Log in as `wiener` and inspect the JWT the server issues as a session cookie:

![[images/walkthrough/PortSwigger/JWT/lab2/1.png]]

- Attempt to access `/admin` and see the application responds with `401 Unauthorized`.
- Send this request to repeater. Change the username in the JWT payload from `wiener` to `administrator`:

![[images/walkthrough/PortSwigger/JWT/lab2/2.png]]

- Still `401`. 
- Remove the signature entirely:

![[images/walkthrough/PortSwigger/JWT/lab2/3.png]]

- No use. 
- In the `JSON Web Token` tab, change the algorithm to `none`:

![[images/walkthrough/PortSwigger/JWT/lab2/4.png]]

- The application lets you in. 
- Delete the `carlos` user by sending a `GET` to `/admin/delete?username=carlos`:

![[images/walkthrough/PortSwigger/JWT/lab2/5.png]]

![[images/walkthrough/PortSwigger/JWT/lab2/solved.png]]

Solved!
## 3. JWT authentication bypass via weak signing key

>[!done]

>[!note]+ Lab description
> - [`Lab: JWT authentication bypass via weak signing key`](https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-weak-signing-key)
> - Level: #Practitioner 
> 
> This lab uses a JWT-based mechanism for handling sessions. It uses an extremely weak secret key to both sign and verify tokens. This can be easily brute-forced using a [wordlist of common secrets](https://github.com/wallarm/jwt-secrets/blob/master/jwt.secrets.list).
> 
> To solve the lab, first brute-force the website's secret key. Once you've obtained this, use it to sign a modified session token that gives you access to the admin panel at `/admin`, then delete the user `carlos`.
> 
> You can log in to your own account using the following credentials: `wiener:peter`

### Solution

- Log in as `wiener` and inspect the JWT issued by the server:

![[images/walkthrough/PortSwigger/JWT/lab3/1.png]]

- Attempt to access `/admin` and observe `401` response. 
- Send the request to `Repeater`. Change the payload, then supply arbitrary signature, change the algorithm to `"none"`, leave the signature empty — these methods won't work. 
- Notice the original algorithm is HMAC-based (`HS256`). If the server uses a weak key, you may be able to brute-force it.

----
- Save candidate keys locally ([`jwt-secrets`](https://github.com/wallarm/jwt-secrets/blob/master/jwt.secrets.list)):

```bash
wget https://raw.githubusercontent.com/wallarm/jwt-secrets/refs/heads/master/jwt.secrets.list
```

- Use `hashcat` to crack the secret:

```bash
hashcat -a 0 -m 16500 eyJraWQiOiJmY2IwODE1MC05N2E3LTQzNWUtYjQ3Ny1iYzRiZmEyZTE0Y2IiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJwb3J0c3dpZ2dlciIsImV4cCI6MTc3OTYxODQ2Mywic3ViIjoid2llbmVyIn0.SK7cpxhYb0ioBAu-Vfk3rLm_Q2_IFfaKSPb-FxFHpmM jwt.secrets.list
```

```bash
hashcat (v6.2.6) starting

OpenCL API (OpenCL 3.0 PoCL 3.1+debian  Linux, None+Asserts, RELOC, SPIR, LLVM 15.0.6, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
==================================================================================================================================================
* Device #1: pthread-haswell-AMD EPYC 7543 32-Core Processor, skipped

OpenCL API (OpenCL 2.1 LINUX) - Platform #2 [Intel(R) Corporation]
==================================================================
* Device #2: AMD EPYC 7543 32-Core Processor, 3904/7872 MB (984 MB allocatable), 4MCU

Minimum password length supported by kernel: 0
Maximum password length supported by kernel: 256

Hashes: 1 digests; 1 unique digests, 1 unique salts
Bitmaps: 16 bits, 65536 entries, 0x0000ffff mask, 262144 bytes, 5/13 rotates
Rules: 1

Optimizers applied:
* Zero-Byte
* Not-Iterated
* Single-Hash
* Single-Salt

Watchdog: Hardware monitoring interface not found on your system.
Watchdog: Temperature abort trigger disabled.

Host memory required for this attack: 1 MB

Dictionary cache hit:
* Filename..: jwt.secrets.list
* Passwords.: 103965
* Bytes.....: 1231757
* Keyspace..: 103965

eyJraWQiOiJmY2IwODE1MC05N2E3LTQzNWUtYjQ3Ny1iYzRiZmEyZTE0Y2IiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJwb3J0c3dpZ2dlciIsImV4cCI6MTc3OTYxODQ2Mywic3ViIjoid2llbmVyIn0.SK7cpxhYb0ioBAu-Vfk3rLm_Q2_IFfaKSPb-FxFHpmM:secret1
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 16500 (JWT (JSON Web Token))
Hash.Target......: eyJraWQiOiJmY2IwODE1MC05N2E3LTQzNWUtYjQ3Ny1iYzRiZmE...xFHpmM
Time.Started.....: Sun May 24 04:42:39 2026 (0 secs)
Time.Estimated...: Sun May 24 04:42:39 2026 (0 secs)
Kernel.Feature...: Pure Kernel
Guess.Base.......: File (jwt.secrets.list)
Guess.Queue......: 1/1 (100.00%)
Speed.#2.........:  1477.0 kH/s (1.25ms) @ Accel:512 Loops:1 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 2048/103965 (1.97%)
Rejected.........: 0/2048 (0.00%)
Restore.Point....: 0/103965 (0.00%)
Restore.Sub.#2...: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#2....:  -> everybody knows it

Started: Sun May 24 04:42:38 2026
Stopped: Sun May 24 04:42:40 2026
```

- `hashcat` outputs the secret in the format `JWT:SECRET`:

```bash
eyJraWQiOiJmY2IwODE1MC05N2E3LTQzNWUtYjQ3Ny1iYzRiZmEyZTE0Y2IiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJwb3J0c3dpZ2dlciIsImV4cCI6MTc3OTYxODQ2Mywic3ViIjoid2llbmVyIn0.SK7cpxhYb0ioBAu-Vfk3rLm_Q2_IFfaKSPb-FxFHpmM:secret1
```

- The secret is `secret1`. In Base64URL — `c2VjcmV0MQ`.

- Attack using `JWT Editor` in Burp:
	1. In `JWT Editor` -> `Keys` tab, click `New Symmetric Key`, then paste the cracked secret into the `k` field of the JWK (Base64URL-encoded). Alternatively, use the `Generate` button to create a random key and then overwrite the `k` value.
	![[keys_tab.png]]
	![[secret_generated.png]]

	2. Switch to `Repeater`'s `JSON Web Token` tab and modify the payload. 
	
	![[modify_payload.png]]
	2. Click `Sign`, select the symmetric key you just stored, and confirm the algorithm matches the original token.
	![[sign.png]]
	3. Send the request. 

![[images/walkthrough/PortSwigger/JWT/lab3/2.png]]

- Access to the administrator is granted. Repeat the request to the URL `/admin/delete?username=carlos`.

![[images/walkthrough/PortSwigger/JWT/lab3/solved.png]]

Solved!
## 4. JWT authentication bypass via `jwk` header injection

>[!done]

>[!note]+ Lab description
> - [`Lab: JWT authentication bypass via jwk header injection`](https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-jwk-header-injection)
> - Level: #Practitioner 
> 
> This lab uses a JWT-based mechanism for handling sessions. The server supports the `jwk` parameter in the JWT header. This is sometimes used to embed the correct verification key directly in the token. However, it fails to check whether the provided key came from a trusted source.
> 
> To solve the lab, modify and sign a JWT that gives you access to the admin panel at `/admin`, then delete the user `carlos`.
> 
> You can log in to your own account using the following credentials: `wiener:peter`

### Solution

- Log in as `wiener` and inspect the JWT issued by the server:

![[images/walkthrough/PortSwigger/JWT/lab4/1.png]]


- Send the request to `Repeater` and change the endpoint to `/admin`. Send the request and observe the application responds with `401 Unauthorized`.
- Attempt a `jwk` injection attack:

1. Generate an RSA key in the `JWT Editor` tab: `New RSA Key → Generate → OK`.

![[rsa.png]]

2. In `Repeater`'s `JSON Web Token` tab, modify the token's payload.
3. Click `Attack` -> `Embedded JWK`. 

![[embedded_jwk.png]]

4. Select your newly generated RSA key.

![[embedded_jwk_select_key.png]]

5. Send the request to test how the server responds

![[images/walkthrough/PortSwigger/JWT/lab4/2.png]]

- The application lets you in. Repeat the request with `/admin/delete?username=carlos`.

![[images/walkthrough/PortSwigger/JWT/lab4/solved.png]]
## 5. JWT authentication bypass via `jku` header injection

>[!done]

>[!note]+ Lab description
> - [`Lab: JWT authentication bypass via jku header injection`](https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-jku-header-injection)
> - Level: #Practitioner 
> 
> This lab uses a JWT-based mechanism for handling sessions. The server supports the `jku` parameter in the JWT header. However, it fails to check whether the provided URL belongs to a trusted domain before fetching the key.
> 
> To solve the lab, forge a JWT that gives you access to the admin panel at `/admin`, then delete the user `carlos`.
> 
> You can log in to your own account using the following credentials: `wiener:peter`
### Solution

- Log in as `wiener` and inspect the session cookie the application issues: this is a JWT.

![[images/walkthrough/PortSwigger/JWT/lab5/1.png]]

- Send a request to `/admin` and see `401 Unauthorized`.
- Notice the `alg` parameter is set to `RS256`. This means that application uses a private key to sign the tokens, and a public key to verify them.
- One of the possible attacks you may try is `jwk` injection ([[#4. JWT authentication bypass via jwk header injection]]). Another is `jku` injection.

1. Generate an RSA key pair using Burp's `JWT Editor`.

![[images/walkthrough/PortSwigger/JWT/lab5/2.png]]


- To host the public key, copy the following values:

```JSON
{
	"kty": "RSA",
	"e": "AQAB",
	"kid": "16f7d2d3-079b-4940-8d0f-78b51754c827",
	"n": "n_LKOp1LoUQN7Z8IJnopvw_Ovkf-vaDUMj24EFUPkNSFQWeI2FHJG1ezBmiBclzR8U8gFEfs6CoECVL277d43FxVPfDkDlIKOribrSPo7l-6zdVxETMQBIFEGTIZEXq9-UMAiAYGYTerZHvhPDdP72KZvuXgMgnp-HrlaIfSEqPvYI1tEANsCL0T350cR3KNs7OZQvH92CCJgJ2r8Yd9RgJmv-msooClpPHkWXudTo1WTiMBamZbqrwpqFVmbb5NKVuR-yZnC19yHpsRKhZuI15IX18LgtDXreHVSQIYQwHNHkSM1Nu_P_k-ArsBH5ou5LjH2ImEfqmKvJH-p9j7_Q"
}
```

- Then place it into the `keys` JSON array:

```JSON
{
    "keys": [

    ]
}
```

->

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

- Copy this value and paste it a response body on your exploit server (`/exploit.json`).

![[images/walkthrough/PortSwigger/JWT/lab5/3.png]]

- Then modify the JWT payload: replace `wiener` with `administrator`. Then modify the header:

```JSON
{  
	"alg": "RS256",
	"typ": "JWT",		
    "kid": "16f7d2d3-079b-4940-8d0f-78b51754c827",  
    "jku": "https://exploit-0aff004603e29da0803b89e901120071.exploit-server.net/exploit.json"
      
}
```

and sign with your RSA key.

- Send the request to `/admin` again and see the application lets you in:

![[images/walkthrough/PortSwigger/JWT/lab5/4.png]]

- Delete `carlos` by sending a request to `/admin/delete?username=carlos`.


![[images/walkthrough/PortSwigger/JWT/lab5/solved.png]]

Solved!
## 6. JWT authentication bypass via `kid` header path traversal

>[!done]

>[!note]+ Lab description
> - [`Lab: JWT authentication bypass via kid header path traversal`](https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-kid-header-path-traversal)
> - Level: #Practitioner 
> 
> 
> This lab uses a JWT-based mechanism for handling sessions. In order to verify the signature, the server uses the `kid` parameter in JWT header to fetch the relevant key from its filesystem.
> 
> To solve the lab, forge a JWT that gives you access to the admin panel at `/admin`, then delete the user `carlos`.
> 
> You can log in to your own account using the following credentials: `wiener:peter`

### Solution

- Log in as `wiener` and inspect the session cookie the application issues: this is a JWT.

![[images/walkthrough/PortSwigger/JWT/lab6/1.png]]

- Attempt to access the `/admin` panel and see `401 Unauthorized`.
- Observe the `alg` parameter is set to `HS256`; this means the application signs and verifies the token using the same key (symmetric cryptography).
- To go `JWT Editor` -> `New Symmetric Key`, then create an empty key:

![[images/walkthrough/PortSwigger/JWT/lab6/2.png]]

- Then go to `Repeater` -> `JSON Web Token`. Change `wiener` to `administrator` in the token payload, then replace the `kid` value with `../../../../../dev/null` and `Sign` the token using your empty key.

![[images/walkthrough/PortSwigger/JWT/lab6/3.png]]

- This grants you access to `/admin`. Repeat the request to `/admin/delete?username=carlos`.

![[images/walkthrough/PortSwigger/JWT/lab6/solved.png]]


Solved!