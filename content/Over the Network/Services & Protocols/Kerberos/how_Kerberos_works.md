---
created: 27-02-2026
tags:
  - network_services
---
## Kerberos

>**[Kerberos](https://en.wikipedia.org/wiki/Kerberos_%28protocol%29)** is a network authentication protocol designed to security authenticate users and services over an untrusted network.

- Kerberos operates at a client-server model and provides **mutual authentication** — both the user and the server verify each other's identities. 
- The protocol build on **symmetric-key cryptography** and works on the basis of **tickets** so that passwords are never sent over in clear text over the network. 

>[!important] Kerberos is a standard protocol defined in [`RFC 4120`](https://www.rfc-editor.org/info/rfc4120) and [`RFC 4121`](https://www.rfc-editor.org/info/rfc4121). 

>[!important]+ Kerberos is the default authentication protocol in Active Directory environments. The version used in modern Windows domains is **Kerberos V5**.
## Architecture and components

Key components involved in Kerberos authentication process include:

- **Principals**
	- A **principal** is a unique identity in a Kerberos realm that participates in authentication — a user, machine, or service account.
	- Each principal has a **long-term secret key** known only to the principal and the KDC.
		- For **user principals**, the key is derived from the password.
		- For **service principals**, the secret key is stored in a *keytab file*.
	- Each principal has a unique name in the format: `<primary>/<instance>@<realm>`.

>[!info] In Windows AD terms you’ll see this as **[User Principal Name (UPN)]([https://learn.microsoft.com/en-us/windows/win32/adschema/a-userprincipalname](https://learn.microsoft.com/en-us/windows/win32/ad/naming-properties#userprincipalname))** for user accounts (e.g., `someone@example.com`) and **[Service Principal Name (SPN)](https://learn.microsoft.com/en-us/windows/win32/ad/name-formats-for-unique-spns)** for services (e.g., `HTTP/webserver01.corp.local@example.com`).

- **Clients**
	- A **client** is a principal that initiates the authentication process — usually a user account or machine account acting on behalf of a user.
	- A client requests authentication from the *Key Distribution Center (KDC)* and receives a *Ticket-Granting Ticket (TGT)*, then uses that TGT to request *service tickets* to access applications.

>[!info] In AD contexts, Kerberos client is typically a **domain user or computer account** running a client process.

- **Services**
	- **Services** provide the resources the client wants to access, such as a file server, database, web server, etc.
	- Each service has a corresponding **service principal** registered in the KDC database.

- **Key Distribution Center (KDC)**
	- A **Key Distribution Center (KDC)** is a trusted third party that maintains a database of all principals and their secret keys.
	- KDC is a trusted third party responsible for all ticketing decisions.
	- The KDC consists of two logical components:
		- **Authentication Server (AS)**
			- Responsible for verifying the client's identity during initial login and issuing **Ticket Granting Tickets (TGTs)** after the client proves it knows its secret.
		- **Ticket-Granting Server (TGS)**
			- Responsible for issuing **service tickets** that the client presents to the target services (HTTP, SQL, file services, etc).

>[!note] In an AD environment, every DC (Domain Controller) runs a KDC.

### Kerberos realm

>A **Kerberos realm** is the *administrative boundary* within which a specific Kerberos authority — the Key Distribution Center (KDC) — issues and validates authentication credentials.

>[!info] In AD, the Kerberos realm maps directly to the domain (e.g., `EXAMPLE.COM`).

- Kerberos reams defines the *administrative boundary* where a KDC has responsibility for authenticating users, hosts, and services. 
- The realm name appears as part of every Kerberos principal and is used by clients and servers to determine which KDC to contact for authentication.
- Realms are usually named in uppercase and often correspond to an organization's DNS name (e.g., `EXMAPLE.COM`).
- When a principal is authenticated, the realm indicates the authority that vouched for that identity.

### Client secret keys

>A **client's secret key** (also called **long-term key**) is a symmetric cryptographic key that the client and the Key Distribution Center (KDC) both know and use as a shared secret for authentication.

- The secret key is derived from the client's password by applying a *string-to-key function* to the password + a salt (usually the principal name and realm). That function produces a fixed-length encryption key.
- The key is called *long term* because it doesn't change frequently and is used across multiple authentication sessions until the password changes.

>[!note] The secret key is **not the password itself**; it's a result of transformation of the password that both sides can calculate independently.

The KDC maintains a database of principals, and for each principal, the corresponding secret key.
- When an account is created, the password (or other secret) is stored in the directory (e.g., Active Directory).
- The KDC **applies the same string-to-key conversion** to that stored secret to generate the secret key and stores or uses it internally.

So, the KDC can compute the same symmetric key for that principal as the client does locally. Both sides independently know the same key without ever transmitting the password itself over the network.

### Session keys

>A **session key** is a random, ephemeral symmetric key generated by the KDC (AS) when it issues a ticket, and shared securely between two principals (e.g., client & TGS, or client & service).

- A session key is used to encrypt and authenticate protocol messages between those principals for the duration of the session.

Unlike long-term keys (derived from passwords or stored in keytabs), session keys are not fixed and are valid only for a limited time.

## Tickets

>A **Kerberos ticket** is a time-limited **cryptographically sealed data structure** issued by the KDC to authenticate a client to a specific network service.

- A ticket is something a client presents to a server to demonstrate the authenticity of its identity. 
- Tickets are *encrypted with the **secret key** of the service they are intended for*.
- Since this key is known only to the AS and the service, not even the client which requested the ticket can know it or change its contents.
- Each ticket carries a **session key** that will be used to the client and the server to establish a secure communication channel.
- Tickets are **time-bound**: each one has start and end times. 

- Key pieces of information a ticket carries include:
	- The requesting user's principal (generally the username).
	- The principal of the service it's intended for.
	- The IP address of the client machine from which the ticket can be used (optional in Kerberos 5; multiple addresses can be specified to handle NAT and multi-homed systems).
	- The data and time when the ticket starts to be valid.
	- The ticket's maximum lifetime.
	- The session key.

- Tickets usually have expiration time of **10 hours**. 

>[!note] Even though the realm administrator can prevent the issuing of new tickets for a certain user at any time, it cannot prevent users from using the tickets they already possess. That's why it's important to limit ticket validity time.

There are two main types of tickets Kerberos uses:

- **Ticket-Granting Tickets (TGTs)**
- **Service Tickets (STs)**

### Ticket-Granting Tickets

>A **Ticket-Granting Ticket (TGT)** is a type of ticket that can be used to obtain other tickets.

- The TGT is obtained after the initial client authentication in the Authentication Server (AS) exchange.
- It allows the client to authenticate to the **Ticket-Granting Service (TGS)** without supplying credentials again.
- TGTs are used to enable **SSO (Single-Sign On)** — the client can request tickets for many services using the same TGT.
- TGTs have a validity period (often hours) and may be renewable without reauthentication.

### Service Tickets

>A **Service Ticket (ST)** is a type of ticket for any service other than the TGS (Ticket-Granting Service).

- A service ticket is presented to the target service (e.g., SMB server, HTTP server) to authenticate the client.

### Ticket flags

Kerberos tickets include a **bitfield of flags** that describe _how the ticket may be used_, _how it was obtained_, and _additional properties_. These flags are part of the **encrypted portion of the ticket** and therefore cannot be modified by the client or service.

Each bit in the ticket’s `flags` field corresponds to a specific attribute. The main flags in Kerberos V5 include the following:

- **`forwardable`**
	- Indicates that the ticket may be used as the basis for issuing another ticket (or TGT) that is valid for different network addresses. 
	- Primarily used with TGTs.
    
- **`forwarded`**
	- Set when a ticket has _already been forwarded_ from one host to another. This indicates forwarding has occurred.
    
- **`proxiable`**
	- Indicates that the ticket may be used to obtain a _proxy ticket_ for another address. 
	- This flag tells the ticket-granting service that it is allowed to issue tickets valid for other addresses based on this ticket.
    
- **`proxy`**
	- Set on _proxy tickets_ that were issued based on a proxiable ticket.
    
- **`may-postdate`** 
	- Indicates that a _postdated ticket_ may be issued based on this ticket. 
	- A postdated ticket is not valid until a later time.
    
- **`postdated`**
	- Indicates that the ticket _itself_ has been postdated, meaning its start time is in the future relative to the authentication time.
    
- **`invalid`**  
	- Marks the ticket as invalid (sometimes used for postdated tickets before their valid start time). 
	- Such tickets must be validated by the KDC before use.
    
- **`renewable`**  
    - Indicates that the ticket may be _renewed_ beyond its current end time, up to a specified `renew-till` timestamp. This allows long-running sessions without repeated logins.
    
- **`initial`**  
    - Indicates that the ticket was issued by the **Authentication Server (AS)** as part of the client’s initial authentication rather than being issued based on another TGT.
    
- **`pre-authent`**  
	- indicates that the client performed _pre-authentication_ to obtain this ticket; i.e., the KDC verified client identity (e.g., via encrypted timestamp) before issuing it.
    
- **`hw-authent`**  
	- Originally intended to indicate that _hardware-based authentication_ (e.g., smart card) was used. 
	- Modern Kerberos implementations typically do not set this flag.
    
- **`transited-policy-checked`** (optional)  
	- Indicates that a transited realms policy check has been performed. Used in cross-realm authentication scenarios.
    
- **`ok-as-delegate`**
	- Indicates that the service principal is _trusted for delegation_ (in Active Directory, this supports constrained delegation).
## Kerberos operation

![](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/74/Kerb_auth.png)



### Authentication flow

In Kerberos V5, the authentication process consists of a sequence of exchanges between the client, KDC, and the target service (the actual service the client wants to access).

The flow can be broken into four main exchange:
- **Authentication Service (AS) exchange**: `KRB_AS_REQ`/`KRB_AS_REP`
	- The client authenticates to the Authentication Service (AS) in KDC and receives a Ticket-Granting Ticket (TGT).

- **Ticket-Generation Server (TGS) exchange**: `KRB_TGS_REQ`/`KRB_TGS_REP`
	- The client presents the TGT to Ticket-Granting Service (TGS) in KDC and receives a Service Ticket (ST) for a specific service.

- **Client/Server exchange**: `KRB_AP_REQ`/`KRB_AP_REP`
	- Client presents ST to the target service to authenticate.

>[!note] Messages are encoded in ASN.1/DER on the wire, but different parts of messages are encrypted differently or may be not encrypted at all. 

![[kerberos_process.svg]]

>[!important] Request structure
>The _**requests**_ have two main parts:
>- `padata` (**pre-authentication data**)
>	- May contain information needed for processing or decryption.
>- `KDC-REQ-BODY`
>	- Contains the actual request data.

### `KRB_AS_REQ`/`KRB_AS_REP`

The **Authentication Service (AS) exchange** occurs between the client and the Kerberos Authentication Server, and is initiated by a client when it wants to obtain authentication credentials for a given server (but currently holds no credentials). 

- The exchange consists of two messages: `KRB_AS_REQ` from the client to AS, and `KRB_AS_REP` or `KRB_ERROR` (on error) in reply.

>[!note] The AS exchange is used to initiate a client's **login session** to obtain **credentials for a Ticket-Granting Server (TGS)** (which will subsequently used to obtain credentials for other servers).

1. **`KRB_AS_REQ` — initial authentication request** (client -> KDC/AS)
	- The client asks the AS for a **Ticket-Granting Ticket (TGT)**.
	- The request is sent in clear and **is not encrypted**.
	- The message includes:
		- Pre-authentication data (`padata`).
		- Client principal name and realm.
		- Server principal (typically the TGS principal).
		- Requested ticket options.
		- A random nonce (to bind reply to request).
		- Supported encryption types.

![](https://www.samuraj-cz.com/gallery2/001695.gif)

>[!important] Pre-authentication data
>- Pre-authentication data (`padata`) proves the client knows its secret key (derived from the user password). 
>- It's usually the timestamp encrypted with the client's key. 
>- The KDC attempts to decrypt it using the secret it stores for the principal indicated in the message. 
>- If it succeeds and the timestamp makes sense, the client has proven the possession of its key and therefore its identity.

2. **`KRB_AS_REP` — Authentication Service reply** (KDC/AS -> client)
	- Once the KDC verifies the client, it issues a **Ticket-Granting Ticket (TGT)**. The ticket is encrypted with the **TGS long-term secret key**, so that only the TGS can read it. The TGT contains the client's identity, realm, and a **session key for the exchange between the client and TGS**. 
	- The message also includes a part encrypted with the client's long term key (so that the client can read it). It contains the **session key** (`K_C,TGS`), client principal name, real, some other information about the ticket, and the **nonce from the client's request**. This ensures only the client can learn the session key.
	- So, the client obtains a TGT it can't read, and a session key (`K_C,TGS`) protected with its own key.

![](https://www.samuraj-cz.com/gallery2/001696.gif)
### `KRB_TGS_REQ`/`KRB_TGS_REP`

The **Ticket-Granting Service (TGS) exchange** occurs between a client and the Kerberos TGS and is initiated by a client when it want to obtain authentication credentials (Service Ticket, ST) for a given server, renew/validate an existing ticket, or obtain a proxy ticket.

- The exchange consists of two messages: `KRB_TGS_REQ` from the client to the TGS, and `KRB_TGS_REP` or `KRB_ERROR` (on error) from the TGS in reply.

1. **`KRB_TGS_REQ` — Ticket-Granting Service request**
	- The client requests a **Service Ticket (ST)** for a specific service.
	- The message includes:
		- The **TGT** obtained from the AS exchange.
		- An **Authenticator**, encrypted with the TGT's session key (`K_C,TGS`).
		- The **Service Principal Name (SPN)** for desired service (e.g., `HTTP/web01@REALM`)
		- Ticket options (e.g., renewable/forwardable flags)
	- The **authenticator** proves the client possesses the session key from the AS exchange and prevents replay attacks.

>[!important]+ The Authenticator
>The Authenticator contains the client principal, a timestamp, and optionally a sub-session key. It's encrypted with the **session key from the TGT (`K_C,TGS`)**. This proves the client knows `K_C,TGS`, and binds the timestamp to the request (used to prevent replay attacks).

![](https://www.samuraj-cz.com/gallery2/001699.gif)

2. **`KRB_TGS_REP` — Ticket-Granting Service reply**
	- The TGS replies with a **Service Ticket (ST)** encrypted with the target's service's long-term secret key (`K_S`). It contains the client's identity, realm, and a new **session key for client-service exchange** (`K_C`,`S`). Only the service itself (when presented later) can decrypt this.
	- The reply also includes the **service session key** (`K_C,S`) and other metadata such as ticket lifetime, encrypted with the session key from the TGT, so the client can decrypt it.

![](https://www.samuraj-cz.com/gallery2/001700.gif)

### `KRB_AP_REQ`/`KRB_AP_REP`

The **client/server authentication (CS) exchange** is used by network applications to authenticate the client to the server and vice versa. 

- The exchange is initiated by the client and consists of two messages: `KRB_AP_REQ` from the client to the target service, and `KRB_AP_REP` or `KRB_ERROR` (on error) in response.

1. **`KRB_AP_REQ` ― application request to service**
	- The client presents the **Service Ticket** obtained from the TGS to the target service to authenticate; the ticket is still encrypted with the service's secret key (`K_S`), so the client just copied it from the TGS reply.
	- The message also includes an **Authenticator** encrypted with the **service session key** (`K_C,S`). This one contains the client's principal name, realm, timestamp, and optional sub-session key. It proves the client knows `K_C,S` and prevents replay attacks.

2. **`KRB_AP_REP` — application request to service**
	- If mutual authentication was requested, the service sends back a timestamp from the client's authenticator encrypted with the **session key** (`K_C,S`). This proves the service also has the proper session key and is legitimate.

>[!important]+ Keys and encryption
> - **Client long-term keys** are never sent over the network — only used for encryption of pre-auth and AS-REP parts.
>     
> - **Session keys** are ephemeral and derived by the KDC to protect future messages between client and TGS or service.
>     
> - **Service tickets** are protected with the service’s secret so attackers can’t forge or read them.
>     
> - **Authenticators** encrypted with session keys ensure freshness and prevent replay attacks.

## References and further reading 

- [`Kerberos (protocol) — Wikipedia`](https://en.wikipedia.org/wiki/Kerberos_%28protocol%29)
- [`The Kerberos Network Authentication Service (V5) — RFC 4120`](https://www.rfc-editor.org/info/rfc4120)
- [`The Kerberos Version 5 Generic Security Service Application Program Interface (GSS-API) Mechanism: Version 2 — RFC 4121`](https://www.rfc-editor.org/info/rfc4121)

- [`Kerberos Protocol Tutorial — Kerberos Consortium`](https://kerberos.org/software/tutorial.html)

- [`Kerberos — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/kerberos/)
- [`What is Kerberos? Kerberos Authentication Explained — vaadata.com`](https://www.vaadata.com/blog/what-is-kerberos-kerberos-authentication-explained/)
- [`Kerberos Overview — An Authentication Service for Open Network Systems — Cisco`](https://www.cisco.com/c/en/us/support/docs/security-vpn/kerberos/16087-1.html)

- [`Kerberos Authentication: A Wrap Up — 0xscandker`](https://csandker.io/2017/09/12/KerberosAuthenticationAWrapUp.html)
- [`Kerberos part 4 - key terms of the Kerberos protocol — www.samuraj-cz.com`](https://www.samuraj-cz.com/en/article/kerberos-part-4-key-terms-of-the-kerberos-protocol/)
