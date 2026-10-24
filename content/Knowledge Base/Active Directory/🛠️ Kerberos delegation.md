---
created: 2026-10-21
updated: 2026-10-24
tags:
  - AD
  - Kerberos
---





## Kerberos delegation

>[!note]+ The double-hop problem
> - In Kerberos, to authenticate to a service, a user presents an ST (Service Ticket), but not the user's credentials or their TGT (Ticket-Granting Ticket). This means the service itself can't obtain additional tickets on the user's behalf. This is called the **Kerberos double hop problem**.
> - Delegation is the mechanism designed to solve it: it lets a service obtain Kerberos tickets on behalf of a user to access downstream services.
> 
>>[!note] See [[◯ Kerberos double hop problem]].

>**Kerberos delegation** is a mechanism in Active Directory that lets a service authenticate to another service *on behalf of* a user, using the user's identity rather than its own.

- Delegation lets a front-end service reuse the identity of the user who connected to it, so a back-end service applies that user's permissions — not the service account's — without the service ever learning the user's password.
- It exists to solve the **double-hop problem**.
- Delegation builds directly on [[Kerberos]]: it depends on `forwardable` tickets and, for the constrained variants, on the **Service for User (S4U)** protocol extensions.

- There are three types of Kerberos delegation in AD:
	- **Unconstrained delegation (KUD)** — the service can impersonate the user to *any* service in the domain.
	- **Constrained delegation (KCD)** — the service can impersonate the user only to an explicit allowlist of services.
	- **Resource-based constrained delegation (RBCD)** — the list of accounts allowed to delegate is defined on the *target resource*, not on the delegating service. // paraphrase this to explain better

>[!important] Delegation is controlled by `userAccountControl` flags and by two directory attributes:
>- **`msDS-AllowedToDelegateTo`** — on the delegating account; the list of target SPNs it may delegate to (constrained delegation).
>- **`msDS-AllowedToActOnBehalfOfOtherIdentity`** — on the target account; a security descriptor naming the accounts allowed to delegate *to it* (RBCD).





 - If you compromise a host configured for unconstrained delegation, you can dump the cached TGTs from `LSASS` and impersonate any user whose TGT it has cached, potentially up to `Domain Admins`. Connections can be forced using coercion techniques (e.g., the printer bug / `MS-RPRN`). See [[Pass-the-Ticket]].

### Constrained delegation (KCD)

> **Constrained delegation** limits a service to impersonating users only toward an explicit allowlist of target SPNs.

- Introduced in Windows Server 2003.
- The allowlist is stored in the **`msDS-AllowedToDelegateTo`** attribute on the delegating account; the KDC rejects any `S4U2Proxy` target SPN outside it.
- KCD operates in one of two modes, set on the delegating account:

| Mode | Directory configuration | How the user's ticket is obtained |
| ---- | ----------------------- | --------------------------------- |
| **Kerberos only** (no protocol transition) | `msDS-AllowedToDelegateTo` set; `TRUSTED_TO_AUTHENTICATE_FOR_DELEGATION` **not** set | The user must authenticate to the service with Kerberos and present a `forwardable` ST, which the service uses as `S4U2Proxy` evidence. No `S4U2Self`. |
| **Any authentication protocol** (protocol transition) | `msDS-AllowedToDelegateTo` set; **`TRUSTED_TO_AUTHENTICATE_FOR_DELEGATION`** (`0x1000000`, decimal `16777216`) set | The service uses `S4U2Self` to obtain a `forwardable` ST to itself for the user, then `S4U2Proxy`. Works even if the user authenticated by a non-Kerberos protocol. |

- The delegating service can impersonate *any* user — but only toward the allow-listed services.
---
- If an attacker controls an account configured for constrained delegation with protocol transition, they can use `S4U2Self` + `S4U2Proxy` to impersonate arbitrary users (including privileged ones) to the allow-listed services — subject to the "sensitive" and `Protected Users` protections below.

### Resource-based constrained delegation (RBCD)

> **Resource-based constrained delegation (RBCD)** inverts constrained delegation: the *target resource*, not the delegating front-end service, decides which accounts may act on its behalf.

- Introduced in Windows Server 2012.
- Instead of `msDS-AllowedToDelegateTo` on the front-end account, the **target** account carries the **`msDS-AllowedToActOnBehalfOfOtherIdentity`** attribute — a security descriptor listing the accounts allowed to delegate to it.
- The flow uses the same **`S4U2Self` / `S4U2Proxy`** extensions, with the RBCD exception that the evidence ticket need not be `forwardable` (see [[#S4U2Proxy (Service for User to Proxy)]]).
- Configuration requires only **write access over the target resource account** (e.g., `GenericWrite`/`GenericAll` or `WriteProperty` on that attribute), not Domain Admin rights.

---
- Anyone holding write access over a computer object can populate `msDS-AllowedToActOnBehalfOfOtherIdentity` with the SID of an account they control (often a machine account they created), then use S4U to obtain a ticket as any user to that host. 

>[!note] See [[Unconstrained delegation]] and [[AD ACL attacks]].

# drafts


## Forwardable tickets

- Delegation relies on the **`forwardable`** ticket flag (see [[Kerberos#Ticket flags]]).

>[!important] A ticket without the `forwardable` flag can't be used as the basis for a ticket to another service — it can't be delegated.

- Related flags participate in the mechanism:
	- **`forwardable`** — the ticket (typically a TGT) may be used to issue a further ticket with different network addresses, i.e., forwarded to another host.
	- **`forwarded`** — set on a ticket that has already been forwarded.
	- **`ok-as-delegate`** — set by the KDC in a Service Ticket when the target service account is trusted for delegation; it signals to the client that forwarding its TGT to that service is permitted.

- In **unconstrained delegation**, the client forwards its actual TGT to the service.
- In **constrained delegation** and **RBCD**, no TGT is forwarded; the service instead uses the S4U extensions to obtain tickets in the user's name.

## S4U extensions: `S4U2Self` and `S4U2Proxy`

- The **Service for User (S4U)** extensions — defined in [`[MS-SFU]`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-sfu/1fb9caca-4490-4dd3-8f0b-5a75a0e66e43) — let a service request Service Tickets on behalf of a user *without* possessing the user's password or TGT. Both constrained delegation and RBCD are built on them.

### `S4U2Self` (Service for User to Self)

> **`S4U2Self`** lets a service request a Service Ticket to *itself* on behalf of an arbitrary user, obtaining that user's authorization data without the user's involvement.

- The service presents its own TGT to the KDC and names the user it wants to impersonate; the KDC returns an ST whose target is the service itself, carrying the user's PAC (SIDs, group memberships). // paraphrase, this is not understandable at all
- This enables **protocol transition**: because the user never has to present a Kerberos credential, the service can impersonate users who authenticated to it by non-Kerberos means (NTLM, certificates, forms-based auth) and then act for them over Kerberos.
- Whether the resulting ticket is **`forwardable`** depends on how the account is configured:
	- If the service account has the **`TRUSTED_TO_AUTHENTICATE_FOR_DELEGATION`** flag, the S4U2Self ticket is issued **`forwardable`**, so it can be used for the next step.
	- Without that flag, the ticket is returned **non-forwardable**.

>[!note] `S4U2Self` by itself only produces a ticket *to the service's own SPN*. It grants no access to other services; it's the first half of the constrained-delegation flow and a common building block for impersonation.

### `S4U2Proxy` (Service for User to Proxy)

> **`S4U2Proxy`** lets a service present an evidence ticket for a user and request a Service Ticket to a *different, target* service on that user's behalf.

- The service submits the user's ticket (the `forwardable` S4U2Self ticket, or a `forwardable` ST the user presented) as **additional-tickets** evidence, together with the target SPN.
- The KDC issues the delegated ST only if the delegation configuration permits that target — the `msDS-AllowedToDelegateTo` allowlist (KCD) or the `msDS-AllowedToActOnBehalfOfOtherIdentity` descriptor (RBCD).
- The delegated ST is issued in the *user's* name, so the target service applies the user's authorization, not the service account's.

>[!note]+ Forwardable evidence and the RBCD difference
> - Classic constrained delegation (KCD) requires the evidence ticket passed to `S4U2Proxy` to be **`forwardable`**.
> - **RBCD** is the exception: the KDC will honor an `S4U2Proxy` request for an RBCD target even when the evidence ticket is **not** forwardable. This is why RBCD abuse works without the front-end account holding `TRUSTED_TO_AUTHENTICATE_FOR_DELEGATION` (see [`Wagging the Dog — Elad Shamir`](https://eladshamir.com/2019/01/28/Wagging-the-Dog.html)).


## Comparing the delegation models

| Model | Impersonation scope | Configured on | Key configuration |
| ----- | ------------------- | ------------- | ----------------- |
| **Unconstrained (KUD)** | Any service in the domain | Delegating account | `TRUSTED_FOR_DELEGATION` (`0x80000`); user's TGT forwarded and cached |
| **Constrained (KCD)** | Allow-listed target SPNs | Delegating account | `msDS-AllowedToDelegateTo` (+ `TRUSTED_TO_AUTHENTICATE_FOR_DELEGATION` for protocol transition) |
| **Resource-based (RBCD)** | Any account allow-listed by the target | Target resource | `msDS-AllowedToActOnBehalfOfOtherIdentity` |

## Security considerations

- Delegation is a frequent privilege-escalation and lateral-movement vector; the following protections limit who can be impersonated and how.

| Protection | Effect |
| ---------- | ------ |
| **`NOT_DELEGATED` flag** (`0x100000`, "Account is sensitive and cannot be delegated") | Marks an account so its tickets are never `forwardable`; such a user can't be delegated through any model. |
| **`Protected Users` group** | Membership blocks delegation of the user's credentials (and disables NTLM, RC4, and unconstrained-delegation TGT forwarding for the account). |
| **Avoid unconstrained delegation** | Prefer constrained delegation or RBCD with explicit allowlists; audit accounts carrying `TRUSTED_FOR_DELEGATION`. |
| **Restrict write access to delegation attributes** | Control over `msDS-AllowedToDelegateTo` or `msDS-AllowedToActOnBehalfOfOtherIdentity` is equivalent to the ability to impersonate users; treat it as a sensitive right. |

>[!note] Related attacks covered elsewhere in the vault: [[Pass-the-Ticket]] (dumping forwarded TGTs under unconstrained delegation), [[Unconstrained delegation]], and [[AD ACL attacks]] (object control that enables writing delegation attributes).

## References and further reading

- [`[MS-SFU]: Kerberos Protocol Extensions: Service for User and Constrained Delegation Protocol — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-sfu/1fb9caca-4490-4dd3-8f0b-5a75a0e66e43)
- [`S4U2self — [MS-SFU]`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-sfu/02636893-7a1f-4357-af9a-b672e3e3de13)
- [`S4U2proxy — [MS-SFU]`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-sfu/bde93b0e-f3c9-4ddf-9f44-e1453be7af5a)
- [`Kerberos Constrained Delegation Overview — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-constrained-delegation-overview)
- [`How Windows Server 2012 Eases the Pain of Kerberos Constrained Delegation (RBCD) — Microsoft Learn`](https://learn.microsoft.com/en-us/archive/blogs/taylorb/kerberos-constrained-delegation-with-protocol-transition-ad-fs-and-more)
- [`RFC 4120: The Kerberos Network Authentication Service (V5)`](https://www.rfc-editor.org/info/rfc4120)

---

- [`Kerberos Delegation — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/kerberos/delegations)
- [`Wagging the Dog: Abusing Resource-Based Constrained Delegation to Attack Active Directory — Elad Shamir`](https://eladshamir.com/2019/01/28/Wagging-the-Dog.html)
- [`S4U2Pwnage — harmj0y`](https://harmj0y.medium.com/s4u2pwnage-36efe1a2777c)
- [`A Case Study in Wagging the Dog: Computer Takeover — harmj0y`](https://posts.specterops.io/a-case-study-in-wagging-the-dog-computer-takeover-2bcb7f94c783)



- Suppose an internal domain web application runs on `http://web01.example.com`, and is used to upload/download files. The application stores files locally on the same server at `C:\Web\ShareSupport`. 
- To interact with the application, you need to log in first. The application supports Kerberos authentication.
- Services that support Windows authentication can act on behalf of clients. 
- For example, this application lists files of a folder (read permissions) and allows upploading/downloading/deleting  files (write permissions)
