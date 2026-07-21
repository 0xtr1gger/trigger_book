---
created: 2026-07-27
updated: 2026-07-27
---
## Identities in Entra ID

>An **identity** is something Microsoft Entra ID can authenticate. 

- Broadly speaking, Entra ID manages three categories of identities:
	- **Human identities** — developers, administrators, operators, etc.; they can authenticate using passwords, MFA, Windows Hello, FIDO2 keys, or certificates. 
	- **External identities** — B2B partners, guest users, federated identities, etc.
	- **Workload identities** — these represent software rather than humans.

- An identity can be, for example, a human user, Azure VM, AKS cluster, application, GitHub Actions workflow, Azure Function, Container App, and so on.

 >[!important] Every authenticated request originates from some identity.
 
## Security Principals

>A **Security Principal** is any identity that can be authenticated and authorized to access resources. 

- Everything that can receive Azure RBAC permissions is a security principal.
