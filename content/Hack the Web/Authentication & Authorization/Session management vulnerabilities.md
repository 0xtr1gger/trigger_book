---
created: 2026-10-01
updated: 2026-10-02
status: stub
proofread: no
tags:
  - methodology
---

## Session management vulnerabilities

>[!warning] Stub. Reached from [[Web application security testing methodology]]. WSTG category `WSTG-SESS`. For token-based sessions see [[JWT attacks]]; for request forgery see [[CSRF]].

- Covers how the application creates, transmits, and destroys sessions — distinct from authentication (proving identity) and the JWT/CSRF notes.

## Cookie attributes

- Verify `HttpOnly`, `Secure`, `SameSite`, `Domain`/`Path` scope, and expiry on every session cookie.

## Session identifier strength

- Assess entropy and predictability of session IDs; look for sequential or encoded values.

## Session fixation

- Check whether the session ID is rotated on privilege change (login); if not, a pre-set ID can be fixed onto the victim.

## Session lifecycle

- Test logout invalidation (server-side), idle and absolute timeout, and concurrent-session handling.

## References and further reading

- [`Session Management Testing — OWASP WSTG`](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/06-Session_Management_Testing/)
