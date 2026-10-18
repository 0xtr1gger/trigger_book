---
created: 2026-10-01
updated: 2026-10-02
proofread: no
status: stub
tags:
  - methodology
---

## Access control and privilege escalation


- Covers function-level and vertical access control — reaching actions or data the current role should not have. Test with at least two accounts plus an anonymous session.

## Vertical privilege escalation

- Access admin-only functions as a low-privileged or anonymous user by calling the endpoint directly rather than through the UI.

## Forced browsing

- Request privileged routes, API endpoints, and hidden pages that the UI does not link for the current role.

## Access-control bypass techniques

- Method swap (`GET`↔`POST`), header overrides (`X-Original-URL`, `X-Rewrite-URL`, `X-Forwarded-For`), and path/case/encoding tricks to defeat `401`/`403` checks.

## Horizontal escalation

- Reach a peer user's functionality; where the reference is an object ID, see [[IDOR]].

## References and further reading

- [`Authorization Testing — OWASP WSTG`](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/05-Authorization_Testing/)
