---
created: 02-03-2026
---
## Pass-the-Ticket

>With a valid TGT (Ticket-Granting Ticket), you can request a **Service Ticket (ST)** to **any service** from the TGS (Ticket-Granting Service, a part of KDC) without knowing any password. This is called a **[[Pass-the-Ticket]]** attack (though it's rather a Kerberos feature than a bug).

>[!important] This attack requires a valid **TGT (Ticket-Granting Ticket)**.

>[!note] The Pass-the-Ticket attack assumes you already have a valid TGT. To get it in the first place, you may try to extract cached Kerberos tickets from [[SAM & LSA Secrets_|LSA secrets]] or try to forge it with [[Overpass-the-Hash]], [[silver_ticket]], or [[golden_ticket]] attacks.

>[!note] See [[how_Kerberos_works]] to learn more about tickets and authentication flow.
>

The Pass-the-Ticket attack main typically follows these steps:

1. Initial compromise and privilege escalation
	- You first obtain a foothold on a machine in the target domain and escalate privileges to be able to read LSASS (Local Security Authority Subsystem Service) memory (usually `SYSTEM`) where Kerberos tickets reside. 

2. Credential dumping
	- From a compromised host, you use a post-exploitation tool like Mimikatz, `Rubeus`, or `Kekeo` to extract Kerberos ticket from process memory or Kerberos cache. 
	- These tickets may include a valid TGT for a logged-in user, or service tickets for specific service principals.
