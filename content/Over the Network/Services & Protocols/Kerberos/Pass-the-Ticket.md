---
created: 02-03-2026
---
## Pass-the-Ticket

>With a valid TGT (Ticket-Granting Ticket), you can request a **Service Ticket (ST)** to **any service** from the TGS (Ticket-Granting Service, a part of KDC) without knowing any password. This is called a **[[Pass-the-Ticket]]** attack (though it's rather a Kerberos feature than a bug).

>[!important] This attack requires a valid **TGT (Ticket-Granting Ticket)**.



>[!note] See [[how_Kerberos_works]] to learn more about tickets and authentication flow — the attack will become clear to you.

## Extracting Kerberos tickets from Windows


On Windows, tickets — including Ticket Granting Tickets and Service Tickets — are processed and stored by the **LSASS (Local Security Authority Subsystem Service)** process. 

- To extract Kerberos tickets from LSASS memory, you can use the [Mimikatz](https://github.com/gentilkiwi/mimikatz)'s `sekurlsa::tickets` module. This requires `SYSTEM` or local administrator with 

>[!note] [[LSASS memory]].

- Each ticket is tied to a **Logon Session Identifier (LUID)**.

- When a user authenticates in an Active Directory domain, Kerberos tickets — are cached locally in **LSASS (Local Security Authority Subsystem Service)**.


- Without administrative access, you can only get tickets for your current user.
- As an administrator user, you can get any tickets.
## drafts


The Pass-the-Ticket attack main typically follows these steps:

1. Initial compromise and privilege escalation
	- You first obtain a foothold on a machine in the target domain and escalate privileges to be able to read LSASS (Local Security Authority Subsystem Service) memory (usually `SYSTEM`) where Kerberos tickets reside. 

2. Credential dumping
	- From a compromised host, you use a post-exploitation tool like Mimikatz, `Rubeus`, or `Kekeo` to extract Kerberos ticket from process memory or Kerberos cache. 
	- These tickets may include a valid TGT for a logged-in user, or service tickets for specific service principals.


>[!note] The Pass-the-Ticket attack assumes you already have a valid TGT. To get it in the first place, you may try to extract cached Kerberos tickets from [[Registry & LSA secrets|LSA secrets]] or try to forge it with [[Overpass-the-Hash]], [[Silver Ticket]], or [[Golden Ticket _]] attacks.