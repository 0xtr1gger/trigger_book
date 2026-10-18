---
created: 2026-08-09
updated: 2026-09-20
---
## AD CS

>**AD CS (Active Directory Certificate Services)** is Microsoft's Windows server implementation for operating a **Public Key Infrastructure (PKI)**.

>**[PKI (Public Key Infrastructure)](https://en.wikipedia.org/wiki/Public_key_infrastructure)** is a set of hardware, software, policies, and procedures used to create, manage, distribute, verify, store, and revoke **digital certificates** ad **cryptographic keys**.

- AD CS provides mechanisms for:
	- issuing, renewing, revoking certificates; publishing certificate revocation information; 
	- distributing trust; 
	- automating certificate enrollment; 
	- authenticating users, computers, devices, services; 
	- encrypting and signing data; and 
	- supporting certificate-based network authentication.

- Microsoft [describes](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/active-directory-certificate-services-overview) AD CS as a Windows Server role for issuing and managing PKI certificates used by secure communication and authentication protocols.

>[!important] In a security-sensitive organization, an Enterprise CA should normally be treated as **Tier 0 / identity infrastructure**.

## AD CS architecture

### CA types

## Certificate anatomy

## References and further reading 

- [`What is Active Directory Certificate Services? — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/active-directory-certificate-services-overview)


- [`Public key infrastructure — Wikipedia`](https://en.wikipedia.org/wiki/Public_key_infrastructure)