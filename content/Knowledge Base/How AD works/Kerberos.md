---
created: 2026-07-25
updated: 2026-10-18
tags:
  - AD
status: substantial
---
## Kerberos 

>**[Kerberos](https://en.wikipedia.org/wiki/Kerberos_%28protocol%29)** is a network authentication protocol that securely verifies the identities of clients and services communicating over an insecure network.

- The protocol operates on a client-server model and provides **mutual authentication** — both the user and the service can verify each other's identities.
- Kerberos uses a trusted **Key Distribution Center (KDC)** that issues **tickets** (time-limited cryptographically sealed tokens) to securely authenticate both clients and servers. Passwords are never sent over the network in cleartext.
- Kerberos is the **default authentication protocol** in Active Directory environments.


---

-  Kerberos is fundamentally a symmetric-key protocol, with optional asymmetric features (such as [PKINIT](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-pkca/d0cf1763-3541-4008-a75f-a577fa5e8c5b))

---

- Kerberos is used to **centralize authentication**. 
- Kerberos also allows users to authenticate against services without sending a password over the network. 


>[!important] Kerberos version used in modern Windows domains is **Kerberos V5**, defined in [`RFC 4120`](https://www.rfc-editor.org/info/rfc4120) and [`RFC 4121`](https://www.rfc-editor.org/info/rfc4121).

>[!important]+ Network ports
> - **TCP/UDP port `88`** — Kerberos authentication traffic (`AS-REQ`/`AS-REP`, `TGS-REQ`/`TGS-REP`).
> - **TCP/UDP port `464`** — Kerberos password change (`kpasswd`).
## Architecture and components

### Principals

> A **principal** is a unique identity in a Kerberos realm that participates in authentication — typically a user, computer, or service account.

- Every principal has a **long-term secret key** known only to the principal and the KDC:
	- For **user principals**, the key is derived from the account password (using a key derivation function).
	- For **service principals**, the key is stored in the AD database, `NTDS.dit` (the `krbtgt` account for the KDC itself) or in a **`keytab` file** for non-Windows services.
- Each principal is identified by a unique name in the format `<primary>/<instance>@<REALM>`.

>[!important] In AD, **user accounts** are identified by **[User Principal Name (UPN)](https://learn.microsoft.com/en-us/windows/win32/ad/naming-properties#userprincipalname)** (e.g., `someone@example.com`), and service accounts are identified by **[Service Principal Name (SPN)](https://learn.microsoft.com/en-us/windows/win32/ad/name-formats-for-unique-spns)**  (e.g., `HTTP/webserver01.corp.local@example.com`).
### Clients

> A **client** is a principal that initiates the authentication process — typically a user or machine account acting on behalf of a user or system process.

- A client requests authentication from the **Key Distribution Center (KDC)** and receives a **Ticket-Granting Ticket (TGT)**, then uses that TGT to request **service tickets** to access specific applications.
- In AD, the Kerberos client is the **[Kerberos SSP](https://learn.microsoft.com/en-us/windows/win32/secauthn/kerberos-ssp-ap) (Security Support Provider)** (`kerberos.dll`) running in the Windows security subsystem (`LSASS`) on the client machine.
### Services

> A **service** is any resource the client may need to access — such as a file server, database, web server, printer, or any network-accessible application.

- Every service that participates in Kerberos authentication must have a corresponding **service principal** registered in the KDC database (i.e., an SPN in AD).
- When the service receives a Kerberos ticket, it decrypts it using its own long-term secret key to authenticate the client.

### Key Distribution Center (KDC)

> The **Key Distribution Center (KDC)** is the trusted third party responsible for issuing and managing all Kerberos tickets within a realm and maintaining a database of all principals and their secret keys.

- The KDC is a logical component that consists of two distinct services:
	- **Authentication Server (AS)**
		- Responsible for verifying the client's identity during initial authentication; if the authentication is successful, the AS issues a **TGT (Ticket-Granting Ticket)**.
	- **Ticket-Granting Server (TGS)**
		- Responsible for issuing **Service Tickets (STs)** after the client presents a valid TGT; STs are used to access specific services.
		- A TGT proves the client is already authenticated, so there's no need to enter their password again.

> In an AD environment, every Domain Controller runs a KDC instance. The KDC service is a core part of `LSASS` on Windows Server.
### Kerberos realm

> A **Kerberos realm** is the administrative boundary within which a specific KDC has authority to issue and validate authentication credentials.

>[!info] In AD, a Kerberos realm maps directly to a domain (e.g., `EXAMPLE.COM`).

- The realm name appears as part of every Kerberos principal name and tells clients and servers which KDC to contact for authentication.
- Realm names are usually uppercase (e.g., `EXAMPLE.COM`).
- When a principal is authenticated, the realm indicates the authority that vouched for that identity (useful in cross-realm trust relationships).
### Encryption types

- Kerberos **encryption types (`etypes`)** define the cryptographic algorithms used for ticket and key encryption. Some of the most important ones:


| Name                         |                Code | Key size | Security / support notes                                                                                                                                             |
| ---------------------------- | ------------------: | -------: | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `aes128-cts-hmac-sha1-96`    | `0x11` (`etype 17`) |  128-bit | **Modern / secure.** <br>AES-128-CTS with HMAC-SHA1-96. <br>Common, widely supported.                                                                                |
| `aes256-cts-hmac-sha1-96`    | `0x12` (`etype 18`) |  256-bit | **Modern / secure.** <br>AES-256-CTS with HMAC-SHA1-96.<br>Common, widely supported.<br>The preferred `etype` when AES-256 support is available.                     |
| `aes128-cts-hmac-sha256-128` | `0x13` (`etype 19`) |  128-bit | **Modern.** <br>AES-128-CTS with HMAC-SHA-256-128, defined by [`RFC 8009`](https://www.rfc-editor.org/info/rfc8009/). <br>Newer than the SHA-1 AES, but less common. |
| `aes256-cts-hmac-sha384-192` | `0x14` (`etype 20`) |  256-bit | **Modern.** <br>AES-256-CTS with HMAC-SHA-384-192, defined by [`RFC 8009`](https://www.rfc-editor.org/info/rfc8009/).                                                |
| `rc4-hmac`                   | `0x17` (`etype 23`) |  128-bit | **Legacy / deprecated.** <br>RC4 with HMAC-MD5; in Microsoft Kerberos, the key is derived from the NT password hash.                                                 |

- The KDC and client negotiate the strongest mutually supported encryption type during the AS and TGS exchanges.
- When multiple encryption types are available, Windows prefers **AES-256**, then AES-128, then RC4.
- The encryption type used for a ticket determines the key the KDC derives from the principal's secret.

### Client secret keys

> A **client's secret key** (also called **long-term key**) is a symmetric key derived from the principal's password — known only to the principal and the KDC.

- The key is computed by applying a **string-to-key function** to the password combined with a salt (typically the principal name and realm). The result is a fixed-length *encryption key* (appropriate for the chosen encryption type).
- The key is called _long-term_ because it persists across authentication sessions and only changes when the password changes.

>[!note] The secret key is a deterministic transformation of the password that both the client and KDC can compute independently; it's not the password itself.

- Neither the cleartext password nor the derived key is ever transmitted over the network during Kerberos authentication.

### Session keys

> A **session key** is a random, ephemeral symmetric key generated by the KDC and securely delivered to both parties that need to communicate.

- Unlike long-term keys, session keys are **randomly generated** by the KDC when a ticket is issued; they are **time-limited** — valid only for the duration of the authentication session. A separate session key is created for each client-to-service communication.
- Session keys are delivered to the client encrypted with the client's long-term key, and embedded inside the ticket — encrypted with the target's long-term key. This ensures only the intended parties can learn the session key.

### `krbtgt` account

> The **`krbtgt`** account is a special user account, present in every AD domain, whose password hash is used by the KDC to encrypt and sign all TGTs.

- The `krbtgt` account is created automatically. It is **disabled by default** and can't be used for interactive logon.
- The KDC derives its long-term key from the `krbtgt` account's password. This key is used to **encrypt** every TGT issued and **sign** the PAC embedded inside tickets.

>[!note] See the [[#Privilege Attribute Certificate (PAC)]] section.

- Because the `krbtgt` hash is the key that protects all TGTs, it is the single most valuable credential in an AD domain.

>[!bug] If an attacker obtains the `krbtgt` hash, they can perform [[Golden Ticket]] attacks — forging arbitrary TGTs to grant any identity any group membership, with no expiration (unless the `krbtgt` password is reset **twice**). In other words, compromising `krbtgt` leads to a full domain compromise.

### SPNs


> A **Service Principal Name (SPN)** is a unique identifier assigned to a service instance. An SPN binds the service instance on a network host to a specific Active Directory sign-in account.

>[!note] SPNs allow client applications to request service authentication for an account even if the client doesn't have an account name.

- SPN format:

```powershell
<service_class>/<host>:<port>
```

- Examples:
	- `MSSQLSvc/sql01.corp.local:1433`
	- `HTTP/webserver.corp.local`
	- `HOST/dc01.corp.local`

- SPNs must be registered in Active Directory so the KDC can locate the correct account key to encrypt service tickets; this is often done automatically for local system accounts but manually via `setspn.exe` for dedicated service accounts.

>[!note] See [`Service principal names — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/ad/service-principal-names) and [`Name Formats for Unique SPNs`](https://learn.microsoft.com/en-us/windows/win32/ad/name-formats-for-unique-spns).
## Tickets

> A **Kerberos ticket** is a time-limited, cryptographically sealed data structure issued by the KDC that authenticates a client to a specific service.

- A ticket is what a client presents to a server to prove its identity. 
- Tickets are encrypted with the **secret key of the service they are intended for**, so only the destination service (and the KDC) can decrypt and inspect the ticket's content. Even the client for which the ticket is issued can't read or modify it.
- Each ticket contains a **session key** that the client and the target service can subsequently use to establish a secure communication channel.

>[!important] Tickets are **time-bound** — each has a start and end time. Expired tickets are rejected.

- Key pieces of information a ticket carries include:
	- Requesting client principal (name and realm).
	- Service principal name the ticket is intended for.
	- Client IP address, from which the ticket can later be used (optional in Kerberos V5; multiple addresses can be specified to handle NAT and multi-homed systems).
	- Ticket start and end times. 
	- Session key.
	- Authorization data (the PAC in AD).
	- Ticket flags.

>[!important] Tickets in AD have a default maximum lifetime of **10 hours** (configurable via domain policy).
>- Even if an administrator revokes a user's access, the user can continue using already-issued tickets until they expire.
>- This is why ticket lifetime limits and Kerberos armoring (Flexible Authentication Secure Tunneling, or FAST) are important security controls.

- There are two types of tickets in Kerberos:
	- **Ticket-Granting Tickets (TGTs)** — obtained at initial logon and used to request service tickets without re-authenticating.
	- **Service Tickets (STs)** — issued by the TGS and presented to the target service to authenticate the client.

### Ticket-Granting Tickets (TGTs)

> A **Ticket-Granting Ticket (TGT)** is a special Kerberos ticket that authorizes the client to request Service Tickets (STs) from the TGS.

- TGTs are issued by **AS (Authentication Server)** during the AS exchange (`KRB_AS_REQ` / `KRB_AS_REP`), after the client successfully authenticates by proving knowledge of its long-term secret key (see [[#1. AS exchange (KRBASREQ / KRBASREP)]]).
- They are **encrypted and signed using the `krbtgt` account's long-term key**, meaning only the KDC can decrypt (and validate) them.
- TGTs are what enables **Single Sign-On (SSO)**. Once a user has obtained a TGT, they can request Service Tickets for Kerberos-enabled services without re-entering their password. 
- To support SSO, TGTs are **cached**. Once the user logs on, LSASS obtains a TGT from the KDC and stores it in the Kerberos ticket cache. Whenever an application needs to authenticate to a Kerberos service, LSASS transparently reuses the cached TGT to request the appropriate ST.

>[!note] If TGTs weren't cached (discarded after each use), the client would have to re-enter credentials (re-authenticate) — or at least repeat the AS exchange to get a new TGT — every time it needed to access a new Kerberos service.

- On Windows, the TGT is stored in the Kerberos ticket cache (managed by `LSASS`) together with the associated TGT session key (`K_C,TGS`).
### Service Tickets (STs)

> A **Service Ticket (ST)** is a Kerberos ticket issued for a specific network service. Unlike a TGT, it authenticates the client to the target service rather than to the TGS.

- STs are issued by **TGS (Ticket-Granting Server)** during the TGS exchange (`KRB_TGS_REQ` / `KRB_TGS_REP`). To obtain an ST, a client must present a valid TGT together with an authenticator (see [[#2. TGS exchange (KRBTGSREQ / KRBTGSREP)]]).
- They are **encrypted using the target service's long-term secret key**, meaning only that service can decrypt them.
- **An ST grants access only to the service it was issued for** and can't be used to request tickets for other services.
- The client presents the ST to the target service in the **AP exchange** to authenticate to that service (see [[#3. AP exchange (KRBAPREQ / KRBAPREP)]]).
### Privilege Attribute Certificate (PAC)

> The **Privilege Attribute Certificate (PAC)** is a data structure embedded inside Kerberos tickets that carries the client's authorization information — group memberships, security identifiers (SIDs), and user rights.

- The PAC is what makes Kerberos useful in AD: without it, the ticket only proves *who* the user is, but not *what* they are authorized to do.
- The PAC is signed by both the **KDC's signature key** (derived from the `krbtgt` account's password) and optionally by the **target service's key**, which makes tampering detectable (protects the ticket's integrity).
- The PAC includes:
	- The user's **Security Identifier (SID)** and primary group SID.
	- The SIDs of all **security groups** the user belongs to (nested memberships included).
	- **Extra SIDs** (e.g., from SID history during domain migrations).
	- **User account control flags** (e.g., whether the account is disabled, locked out, or requires a smart card).
	- **Logon time, logoff time, and password last set** timestamps.

> [!bug] If an attacker compromises the `krbtgt` account hash, they can forge the PAC to include arbitrary group memberships (e.g., Domain Admins). This is the [[Golden Ticket]] attack.

### Ticket flags

- Kerberos tickets carry a **bitfield of flags** that control how the ticket may be used, how it was obtained, and what properties it has. 
- These flags are embedded in the encrypted portion of the ticket and **can't be modified by the client or service**.

| Flag                       | Description                                                                                                                                                                      |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `forwardable`              | Indicates that the ticket may be used as the basis for issuing another ticket (or TGT) with different network addresses. Primarily used with TGTs for **delegation** scenarios. |
| `forwarded`                | Set when a ticket **has already been forwarded** from one host to another.                                                                                                       |
| `proxiable`                | Indicates that the ticket may be used to obtain a **proxy ticket** for a different IP address.                                                                                  |
| `proxy`                    | Set on **proxy tickets** that were issued based on a `proxiable` ticket.                                                                                                         |
| `may-postdate`             | Indicates that a postdated ticket may be issued based on this ticket (postdated means the ticket becomes valid at a time after its issuance).                             |
| `postdated`                | The ticket's start time is in the future.                                                                                                                                        |
| `invalid`                  | The ticket is not yet valid (used with postdated tickets). Must be validated by the KDC before use.                                                                              |
| `renewable`                | The ticket may be **renewed** beyond its current end time, up to a `renew-till` timestamp.                                                                                       |
| `initial`                  | The ticket was issued by the **Authentication Server (AS)** (initial authentication) rather than derived from a TGT.                                                             |
| `pre-authent`              | Indicates that the client performed **pre-authentication** (e.g., encrypted timestamp) to obtain this ticket.                                                                    |
| `hw-authent`               | Originally intended to indicate that _hardware-based authentication_ (e.g., smart card) was used. <br>Rarely used in modern implementations.                                     |
| `transited-policy-checked` | Indicates that a transited realms policy check was performed. Used in cross-realm authentication.                                                                                |
| `ok-as-delegate`           | Indicates that the service principal is **trusted for delegation** (relevant for Kerberos constrained delegation in AD).                                                         |
| `enc-pa-rep`               | Indicates that the client supports **claims and compound authentication** (introduced in Windows Server 2012).                                                                   |

>[!note]+ The **`enc-pa-rep`** flag is newer and indicates that the ticket was issued with support for **Kerberos armoring (FAST)** and claim-based authentication, introduced in Windows Server 2012 domain functional level.
## Kerberos operation

- The Kerberos V5 authentication process consists of **three exchanges** between the client, the KDC, and the target service:
	1. **AS exchange** (`KRB_AS_REQ` / `KRB_AS_REP`) — a client obtains a TGT (Ticket-Granting Ticket) from the AS (Authentication Server, part of KDC).
	2. **TGS exchange** (`KRB_TGS_REQ` / `KRB_TGS_REP`) — the client presents the TGT to the TGS (Ticket-Granting Service) to obtain an ST (Service Ticket) to access the target server.
	3. **AP exchange** (`KRB_AP_REQ` / `KRB_AP_REP`) — the client presents the ST to the target service to authenticate.

>[!important]+ Kerberos messages are encoded in **[ASN.1](https://en.wikipedia.org/wiki/ASN.1) [DER](https://en.wikipedia.org/wiki/X.690#DER_encoding)** (Kerberos V5) on the wire. 
>- Different parts of each message are encrypted with different keys; some portions may be cleartext while others are encrypted or signed.
>-  Every Kerberos request (`KRB_AS_REQ`, `KRB_TGS_REQ`) has two main parts:
> 	- **`padata`** — pre-authentication data (may contain encrypted timestamps, tickets, or other metadata required for processing).
> 	- **`KDC-REQ-BODY`** — the actual request payload (client name, service name, options, nonce, supported `enctype` values).

### `1.` AS exchange (`KRB_AS_REQ` / `KRB_AS_REP`)

- The **Authentication Service (AS) exchange** is the first step in Kerberos authentication. 
- It occurs when the client has no existing credentials and needs to establish a login session.

>[!note]+ The AS exchange is the equivalent of a user typing their password at the Windows logon screen. After this exchange, the client has a TGT and a session key and can authenticate to any domain service without re-entering the password.

1. **`KRB_AS_REQ` — initial authentication request** (client -> AS/KDC)
	- The client sends an authentication request to the AS asking for a TGT; the request is mostly in cleartext (not encrypted).
	- The message includes:
		- **Pre-authentication data** (`padata`) — proves the client knows its secret key; typically a timestamp encrypted with the client's long-term key.
		- Client principal name and realm (e.g., `user@EXAMPLE.COM`).
		- Server principal name — typically `krbtgt/REALM@REALM` (the TGS service).
		- Requested ticket options (e.g., `forwardable`, `renewable`).
		- A random **nonce** to bind the reply to this specific request.
		- List of supported encryption types.

>[!note] **Pre-authentication** is the mechanism that prevents an attacker from requesting a TGT for a user whose password they don't know. 
>- The KDC decrypts the timestamp with the user's stored key and checks that the time is recent. 

>[!bug] Without pre-authentication, anyone could request a TGT for any user and attempt to crack the encrypted portion offline — this is the **`AS-REP` roasting** attack.

2. **`KRB_AS_REP` — Authentication Service reply** (AS/KDC -> client)
	- If the KDC successfully verifies the pre-authentication data, it responds with a TGT and associated session key.
	- The AS reply contains two encrypted parts:
		- **Ticket (TGT)** — encrypted with the **`krbtgt` account's long-term secret key**; contains the client's identity, realm, the **TGT session key** (`K_C,TGS`), ticket flags, and the PAC. Only the TGS can decrypt this.
		- **Encrypted portion** (for the client) — encrypted with the **client's long-term key**; contains the **session key** (`K_C,TGS`), the client principal, realm, ticket lifetime, and the **nonce** from the request. Only the legitimate client can decrypt this.
	- After this exchange, the client has:
		- A **TGT** (which it can't read — it's encrypted for the TGS).
		- The **TGT session key** (`K_C,TGS`) — known to the client and the TGS, used for the TGS exchange.
### `2.` TGS exchange (`KRB_TGS_REQ` / `KRB_TGS_REP`)

- The **Ticket-Granting Service (TGS) exchange** occurs when the client needs a Service Ticket for a specific target service. The client presents its TGT to prove it has already authenticated.

1. **`KRB_TGS_REQ` — Ticket-Granting Service request**
	- The client sends a request to the TGS asking for a Service Ticket for a specific SPN.
	- The message includes:
		- The **TGT** obtained from the AS exchange (still encrypted with the `krbtgt` key).
		- An **Authenticator** — encrypted with the **TGT session key** (`K_C,TGS`). Contains the client principal name and a timestamp.
		- The **SPN** of the target service (e.g., `HTTP/web01.example.com@EXAMPLE.COM`).
	- Requested ticket options (e.g., `forwardable`, `renewable`).

>[!note]+ The **Authenticator** proves the client knows `K_C,TGS` (the session key from the AS exchange). 
>- Because it includes a timestamp, it also prevents **replay attacks** — even if an attacker captures a valid request, they can't replay it later because the KDC will detect the stale timestamp.

2. **`KRB_TGS_REP` — Ticket-Granting Service reply**
	- If the TGS validates the TGT (decrypts it with the `krbtgt` key) and the authenticator (decrypts it with `K_C,TGS`), it issues a Service Ticket (ST).
	- The TGS reply contains two encrypted parts:
		- **Service Ticket (ST)** — encrypted with the **target service's long-term secret key** (`K_S`). Contains the client's identity, realm, the **service session key** (`K_C,S`), ticket flags, and the client's PAC. Only the target service can decrypt this.
		- **Encrypted portion** (for the client) — encrypted with the **TGT session key** (`K_C,TGS`). Contains the **service session key** (`K_C,S`), the client principal, and ticket metadata. The client can decrypt this because it knows `K_C,TGS`.
	- After this exchange, the client has:
		- A **Service Ticket** (which it can't read — it's encrypted for the target service).
		- The **service session key** (`K_C,S`) — known to the client and the target service, used for the AP exchange.

> [!bug]+ Kerberoasting
> - When a client requests a TGS ticket, the returned ticket is encrypted with the target service's key. 
> - If RC4 encryption is used, an attacker who captures this TGS ticket can attempt to crack the service account password offline — the RC4 key is derived from the NT hash, which can be brute-forced. 
> - Any domain user can request TGS tickets for any SPN, which makes this a common privilege escalation vector.
> - See [[Kerberoasting]].

### `3.` AP exchange (`KRB_AP_REQ` / `KRB_AP_REP`)

- The **client/server authentication (AP) exchange** is the final step. The client authenticates to the target service by presenting the Service Ticket.

1. **`KRB_AP_REQ` — application request from the client to the target service**
	- The client sends the Service Ticket and an authenticator to the target service:
		- **Service Ticket** — copied verbatim from the TGS reply (still encrypted with the service's key `K_S`).
		- **Authenticator** — encrypted with the **service session key** (`K_C,S`). Contains the client principal name, realm, and a timestamp.
	- The target service:
		1. Decrypts the Service Ticket using its own long-term secret key.
		2. Extracts the **service session key** (`K_C,S`) and the **PAC** from the decrypted ticket.
		3. Uses `K_C,S` to decrypt the authenticator and verify the timestamp.

2. **`KRB_AP_REP` — application reply from the service to the client (mutual authentication)**
	- If mutual authentication was requested, the service replies by encrypting the timestamp from the client's authenticator with `K_C,S`. 
	- The client decrypts this and verifies the timestamp, proving the service also knows `K_C,S` and is therefore the legitimate service (and not an impostor).

> [!tip] Mutual authentication is particularly important when connecting to high-value services such as Domain Controllers, file servers, or database servers. Without it, a rogue service could impersonate a legitimate server.

## Kerberos delegation

> **Kerberos delegation** is a mechanism that allows a service to access resources on other services using the identity of the user who connected to it. 

- Delegation allows a service to act *on behalf of* a user without ever learning the user's credentials.

>[!note]+ The double-hop problem 
> - Delegation exists to solve the **double-hop problem**: a user authenticates to service `A` (first hop), and service `A` must in turn authenticate to service `B` (second hop) *as that user* to complete the request.
> - Kerberos tickets are scoped to a single target service, so the ticket the user presents to `A` is useless for accessing `B` — and the user's password must never be shared with `A`.
> - Delegation is what lets `A` obtain a ticket "on behalf of" the user for `B`.

- Delegation relies on **forwardable tickets** (tickets with the `forwardable` flag set).

>[!important] A ticket without the `forwardable` flag can't be used to obtain tickets for other services, i.e., can't be delegated (see [[#Ticket flags]]).

- There are three delegation models in AD, depending on how much power the delegated service gets:
	- **Unconstrained delegation** — the service can **impersonate the user to *any* service**.
	- **Constrained delegation** — the service can **impersonate the user only to an explicit allowlist of services**.
	- **Resource-based constrained delegation (RBCD)** — the allowlist is defined by the *target resource*, not by the delegating service.

### `S4U2Self` and `S4U2Proxy`

- The **Service for User (S4U)** extensions — defined in [`MS-SFU`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-sfu/1fb9caca-4490-4dd3-8f0b-5a75a0e66e43) — let a service request tickets on behalf of a user *without* the user's password or TGT. Both constrained delegation and RBCD are built on these extensions.
- **`S4U2Self` (Service for User to Self)** — the service requests a Service Ticket to *itself* on behalf of a specified user:
	- The KDC returns the ticket together with the user's authorization data (SIDs, group memberships) — the user is never involved in the exchange.
	- This enables **protocol transition**: the service can impersonate users who authenticated via non-Kerberos methods (e.g., NTLM, certificates, or forms-based authentication), because the user never needs to present a forwardable TGT.
- **`S4U2Proxy` (Service for User to Proxy)** — the service presents the S4U2Self ticket (or the user's forwardable TGT) to the KDC and requests a Service Ticket for a *target* service on behalf of the user:
	- The KDC only honors the request if the target SPN is explicitly allowed for delegation.
	- The ticket used for `S4U2Proxy` must be **forwardable** — the KDC marks the S4U2Self ticket as forwardable when the service is trusted to authenticate for delegation.

### Unconstrained delegation

> **Unconstrained delegation** is the legacy delegation mode in which a service is trusted to act on behalf of any user to *any* service in the domain.

- The account is marked with the **`TRUSTED_FOR_DELEGATION`** `userAccountControl` flag (`0x80000`).
- When a user authenticates to the service, the client passes its **forwardable TGT** to the service, which caches it in `LSASS` and can subsequently use it to request tickets for *any* service as that user.
- Because the user's actual TGT is cached, the service also collects the TGTs of every privileged account that connects to it — and of the machines that contact it.

> [!bug] Unconstrained delegation 
> - An attacker who compromises a delegated server can dump the cached TGTs from `LSASS` (a [[Pass-the-Ticket]]-style attack) and impersonate any user who ever connected to it — including `Domain Admins`. 

### Constrained delegation

> **Constrained delegation** limits a service to impersonating users only to an explicit allowlist of target SPNs.

- Introduced in Windows Server 2003, constrained delegation limits impersonation to an explicitly defined list of allowed SPNs.
- Two things are configured on the delegating account:
	- The **`msDS-AllowedToDelegateTo`** attribute — the list of SPNs the account is allowed to delegate to.
	- The **`TRUSTED_TO_AUTHENTICATE_FOR_DELEGATION`** `userAccountControl` flag (`0x1000000`) — marks the account as trusted to authenticate for delegation, which enables **protocol transition** (`S4U2Self`). Without it, the user must present a forwardable TGT for the proxy request to work.
- The service uses **`S4U2Proxy`** to request tickets for the allow-listed targets (see [[#S4U2Self and S4U2Proxy]]); the KDC rejects any target SPN outside the allowlist.
- The service can impersonate *any* user — but only to the allow-listed services.

### Resource-based constrained delegation (RBCD)

> **Resource-based constrained delegation (RBCD)** inverts constrained delegation: the *target resource* — not the delegating front-end service — decides which accounts are allowed to act on its behalf.

- Introduced in **Windows Server 2012**.
- Instead of `msDS-AllowedToDelegateTo` on the front-end account, the target account carries the **`msDS-AllowedToActOnBehalfOfOtherIdentity`** attribute — a security descriptor listing the accounts allowed to delegate to it.
- Configuration requires only **write access over the resource account**, not Domain Admin rights — and conversely, anyone holding such write access (e.g., over a computer object) can change the configuration.
- The flow uses the same **`S4U2Self` / `S4U2Proxy`** extensions.

### Comparing the delegation models

| Model | Impersonation scope | Configured on | Config required |
| ----- | ------------------- | ------------- | --------------- |
| **Unconstrained** | Any service | Delegating account | `TRUSTED_FOR_DELEGATION` |
| **Constrained** | Allowlisted SPNs | Delegating account | `msDS-AllowedToDelegateTo` (+ `TRUSTED_TO_AUTHENTICATE_FOR_DELEGATION` for protocol transition) |
| **Resource-based constrained** | Allowlisted accounts | Target resource | `msDS-AllowedToActOnBehalfOfOtherIdentity` |

## Security considerations

- Kerberos is a robust protocol, but specific attacks target weaknesses in its implementation and configuration:

| Attack                        | Description                                                                                                                                                                                                                                                 | Mitigation                                                                                                                                           |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| [[Kerberoasting]]             | A domain user requests TGS tickets for any SPN and cracks the service account password offline. The ticket is encrypted with the service's key; if RC4 is used, the NT hash can be brute-forced.                                                          | Use **AES-only** encryption for service accounts (disable RC4). Use **group Managed Service Accounts (gMSAs)** with complex auto-rotated passwords.        |
| [[AS-REP roasting]]       | If pre-authentication is disabled for a user account, an attacker can request a TGT for that user and receive data encrypted with the user's key, which can be cracked offline.                                                                             | Enable **pre-authentication** for all user accounts (default in modern AD unless deliberately disabled).                                             |
| [[Golden Ticket]]           | An attacker who obtains the `krbtgt` hash (via DCSync or other means) can forge arbitrary TGTs with any identity and group memberships.                                                                                                                     | Protect the `krbtgt` account like the Crown Jewels. Reset `krbtgt` password twice in succession after a compromise (standard recovery procedure).    |
| [[Silver Ticket]]           | An attacker who obtains a service account's hash can forge Service Tickets for that service, gaining access without involving the KDC.                                                                                                                      | Use **gMSAs** with frequent password rotation. Monitor for anomalous TGS requests.                                                                   |
| [[DCSync]]                | An attacker with replication rights (e.g., Domain Admin, Enterprise Admin, or specially delegated accounts) can replicate account password hashes from a DC, including the `krbtgt` hash.                                                                   | Monitor for **DS-Replication-Get-Changes** and **DS-Replication-Get-Changes-All** access events (4662, 5136). Restrict who has replication rights.   |
| [[Pass-the-Ticket]]         | An attacker extracts a Kerberos ticket (TGT or ST) from `LSASS` on a compromised machine and uses it on another machine to authenticate as that user without knowing the password.                                                                          | Enable **Credential Guard** (virtualization-based security) to protect tickets in `LSASS`. Use **Protected Users** group to restrict ticket caching. |
| [[Overpass-the-Hash]]       | An attacker uses an NT hash to request Kerberos tickets (instead of using the password), effectively converting NTLM credentials into Kerberos tickets.                                                                                                   | Same mitigations as PtT: Credential Guard, Protected Users group, monitoring for anomalous Kerberos ticket requests.                                 |
| **Skeleton Key**              | A malicious rootkit injected into `LSASS` on a DC that allows any user to authenticate with a static "skeleton key" password in addition to their real password.                                                                                            | Monitor for `LSASS` process anomalies, enable **Code Integrity** / **Credential Guard**, use **LSASS auditing**.                                     |
| [[#Kerberos delegation\|Kerberos delegation abuse]] | Misconfigured unconstrained delegation allows a service to impersonate any user to any service. An attacker who compromises a server with unconstrained delegation can capture TGTs from any user connecting to it (e.g., via printer bug or RPC coercion). | Avoid unconstrained delegation. Use **constrained delegation** or **resource-based constrained delegation** with explicit service allowlists.        |


## References and further reading

- [`Kerberos (protocol) — Wikipedia`](https://en.wikipedia.org/wiki/Kerberos_%28protocol%29)
- [`The Kerberos Network Authentication Service (V5) — RFC 4120`](https://www.rfc-editor.org/info/rfc4120)
- [`The Kerberos Version 5 Generic Security Service Application Program Interface (GSS-API) Mechanism: Version 2 — RFC 4121`](https://www.rfc-editor.org/info/rfc4121)
- [`Kerberos Protocol Tutorial — Kerberos Consortium`](https://kerberos.org/software/tutorial.html)
- [`Kerberos Authentication Overview — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview)
- [`What's new in Kerberos authentication for Windows Server 2012 — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/security/kerberos/whats-new-in-kerberos-authentication)
- [`Kerberos — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/kerberos/)
- [`What is Kerberos? Kerberos Authentication Explained — vaadata.com`](https://www.vaadata.com/blog/what-is-kerberos-kerberos-authentication-explained/)
- [`Kerberos Authentication: A Wrap Up — 0xscandker`](https://csandker.io/2017/09/12/KerberosAuthenticationAWrapUp.html)
- [`Kerberos part 4 — key terms of the Kerberos protocol — www.samuraj-cz.com`](https://www.samuraj-cz.com/en/article/kerberos-part-4-key-terms-of-the-kerberos-protocol/)
- [`Kerberos Overview — An Authentication Service for Open Network Systems — Cisco`](https://www.cisco.com/c/en/us/support/docs/security-vpn/kerberos/16087-1.html)
- [`Service principal names — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/ad/service-principal-names)
- [`Name Formats for Unique SPNs`](https://learn.microsoft.com/en-us/windows/win32/ad/name-formats-for-unique-spns)


- [`Kerberos delegation — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-delegation)
- [`Constrained delegation in Active Directory`](https://learn.microsoft.com/en-us/windows-server/security/kerberos/constrained-delegation)
- [`Resource-based constrained delegation`](https://learn.microsoft.com/en-us/windows-server/security/kerberos/resource-based-constrained-delegation)
- [`Encryption types — MIT Kerberos Documentation`](https://web.mit.edu/KERBEROS/krb5-1.22/doc/admin/enctypes.html)
- [`RFC 6649: Deprecate DES, RC4-HMAC-EXP, and Other Weak Cryptographic Algorithms in Kerberos — RFC Editor`](https://www.rfc-editor.org/info/rfc6649/)
- [`RFC 8429: Deprecate Triple-DES (3DES) and RC4 in Kebreros — RFC Editor`](https://www.rfc-editor.org/info/rfc8429/)

## Appendix A: Kerberos encryption types

| Name                         |                Code | Key          | Notes                                                                                                                                                                                                                                                                                |
| ---------------------------- | ------------------: | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `des-cbc-crc`                |  `0x01` (`etype 1`) | DES-56       | **Legacy/deprecated.** <br>DES-CBC with CRC-32 integrity. <br>Original Kerberos encryption type. <br>DES has only a 56-bit effective key and is cryptographically obsolete; implementations/deployments **should no longer** use it.                                                       |
| `des-cbc-md4`                |  `0x02` (`etype 2`) | DES-56       | **Legacy/deprecated.** <br>DES-CBC with MD4-based integrity. <br>Obsolete and explicitly deprecated by `RFC 6649`.                                                                                                                                                                   |
| `des-cbc-md5`                |  `0x03` (`etype 3`) | DES-56       | **Legacy/deprecated.** <br>DES-CBC with MD5. <br>Was historically the commonly recommended DES `etype`, but is now explicitly deprecated.                                                                                                                                            |
| `des3-cbc-md5`               |  `0x05` (`etype 5`) | 3DES-168*    | **Legacy/deprecated.** <br>3DES-CBC with MD5. <br>`RFC 8429` says implementations/deployments **should not** implement or deploy it.                                                                                                                                                 |
| `des3-cbc-sha1`              |  `0x07` (`etype 7`) | 3DES-168*    | **Legacy/deprecated.** <br>3DES-CBC with SHA-1. <br>Explicitly deprecated by `RFC 8429`.                                                                                                                                                                                             |
| `des3-cbc-sha1-kd`           | `0x10` (`etype 16`) | 3DES-168*    | **Legacy/deprecated.** <br>3DES-CBC with SHA-1 and Kerberos key derivation. <br>Explicitly deprecated by `RFC 8429`.                                                                                                                                                                 |
| `aes128-cts-hmac-sha1-96`    | `0x11` (`etype 17`) | AES-128      | **Modern/common.** AES-128 in CBC ciphertext-stealing mode (CTS), with HMAC-SHA1-96. <br>Defined by `RFC 3962`. 128-bit protocol key.                                                                                                                                                |
| `aes256-cts-hmac-sha1-96`    | `0x12` (`etype 18`) | AES-256      | **Modern/common.** <br>AES-256-CTS with HMAC-SHA1-96. <br>Defined by RFC 3962. 256-bit protocol key.                                                                                                                                                                                 |
| `aes128-cts-hmac-sha256-128` | `0x13` (`etype 19`) | AES-128      | **Modern.** <br>AES-128-CTS with HMAC-SHA-256-128. <br>Uses the `RFC 8009` SHA-2/KDF construction rather than the older SHA-1 AES profile.                                                                                                                                           |
| `aes256-cts-hmac-sha384-192` | `0x14` (`etype 20`) | AES-256      | **Modern.** <br>AES-256-CTS with HMAC-SHA-384-192.<br>`RFC 8009`; uses the SHA-2/KDF construction.                                                                                                                                                                                   |
| `rc4-hmac`                   | `0x17` (`etype 23`) | RC4-128      | **Legacy/deprecated.** <br>Microsoft Windows Kerberos `etype`, using RC4 with HMAC-MD5; the long-term key is derived from the NT password hash (MD4). <br>Widely encountered in older Active Directory environments, but `RFC 8429` says it **should not** be implemented or deployed. |
| `rc4-hmac-exp`               | `0x18` (`etype 24`) | RC4-40/56*   | **Legacy/deprecated.** Export-strength variant of Microsoft's RC4-HMAC.<br>Explicitly deprecated by `RFC 6649`. <br>The historical `"fortybits"` terminology should not be interpreted too literally as a 40-bit protocol key; it is an export-strength construction.                |
| `camellia128-cts-cmac`       | `0x19` (`etype 25`) | Camellia-128 | **Standardized, uncommon.**<br>Camellia-128 in CBC-CTS mode with CMAC. <br>Defined by `RFC 6803`. <br>Not deprecated, but substantially less commonly deployed than AES.                                                                                                             |
| `camellia256-cts-cmac`       | `0x1a` (`etype 26`) | Camellia-256 | **Standardized, uncommon.** <br>Camellia-256 in CBC-CTS mode with CMAC. <br>Defined by `RFC 6803`. <br>Not deprecated, but rarely encountered compared with AES.                                                                                                                     |
| `subkey-keymaterial`         | `0x41` (`etype 65`) | Opaque       | **Special/non-general enctype.** Registered as `subkey-keymaterial`, described by IANA as opaque `PacketCable` key material. It is not a normal Kerberos cryptographic `etype` like AES, RC4, or DES.                                                                                |

>[!note] See [`RFC 6649: Deprecate DES, RC4-HMAC-EXP, and Other Weak Cryptographic Algorithms in Kerberos`](https://www.rfc-editor.org/info/rfc6649/) and [`RFC 8429: Deprecate Triple-DES (3DES) and RC4 in Kebreros`](https://www.rfc-editor.org/info/rfc8429/).

- TODO:
	- Extend [[#Kerberos armoring (FAST)]]
	- Extend [[#Kerberos hardening — best practices overview]], but it shouldn't be a comprehensive guide; just an overview and a reference to a dedicated article.
	- Add diagram for Kerberos authentication.


> [!bug] RC4-HMAC is weak against offline brute force. Because the RC4 key is derived directly from the NT hash, an attacker who captures a TGS ticket encrypted with RC4 can attempt to crack the service account's password offline. This is the basis of **[[Kerberoasting]]**.


## Kerberos double-hop problem

- Kerberos doesn't cache credentials in memory, unlike [[🛠️ NTLM]] (this is why Mimikatz won't give you anything).
