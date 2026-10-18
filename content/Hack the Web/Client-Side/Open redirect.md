---
created: 2026-10-01
updated: 2026-10-02
status: stub
proofread: no
tags:
  - methodology
---

## Open redirect

>[!warning] Stub. Reached from [[Web application security testing methodology]]. For the DOM-sink variant (`window.location` from a source) see [[🛠️ DOM-based vulnerabilities#DOM-based open redirection]].

- The application redirects to a user-controlled target without validating it, sending victims to an attacker-controlled site.

## Injection points

- Redirect parameters: `?url=`, `?next=`, `?returnTo=`, `?redirect=`, `?dest=`, and `Location`-driven flows after login/logout.

## Detection and filter bypass

- Confirm the parameter controls the `Location` header or a client-side redirect; bypass naive allow-lists with `//evil.com`, `https:evil.com`, `@` tricks, and path confusion.

## Impact and chaining

- Phishing on a trusted domain; stealing OAuth `code`/tokens via a poisoned `redirect_uri` ([[OAuth attacks]]); SSRF when the redirect is followed server-side ([[SSRF]]).

## References and further reading

- [`Testing for Client-side URL Redirect — OWASP WSTG`](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/11-Client-side_Testing/04-Testing_for_Client-side_URL_Redirect)
