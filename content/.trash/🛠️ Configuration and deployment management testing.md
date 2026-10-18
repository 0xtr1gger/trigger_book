---
created: 2026-10-01
updated: 2026-10-02
status: stub
proofread: no
tags:
  - methodology
---

## Configuration and deployment management testing

>[!warning] Stub. Reached from [[Web application security testing methodology]]. WSTG category `WSTG-CONF`.

- Tests the server and platform configuration surrounding the application, not its code.

## HTTP methods

- Enumerate allowed verbs (`OPTIONS`); test `PUT`/`DELETE` for arbitrary file write and `TRACE` for Cross-Site Tracing.

## Admin and management interfaces

- Locate and reach administrative consoles, management ports, and default/known credentials.

## Old, backup, and unreferenced files

- Request source, backup, and config artifacts (`.bak`, `.old`, `~`, `.inc`, `.swp`) and alternate extensions that bypass handlers.

## Security headers and TLS

- Review `Strict-Transport-Security`, `Content-Security-Policy` ([[CSP]]), cookie flags, and transport configuration.

## References and further reading

- [`Configuration and Deployment Management Testing — OWASP WSTG`](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/02-Configuration_and_Deployment_Management_Testing/)
