---
created: 12-01-2026
tags:
  - in_progress
---
## WHOIS

>**[WHOIS](https://en.wikipedia.org/wiki/WHOIS)** is a public database and protocol that provides information about registered domains.

WHOIS lookup typically provides:
- Domain registration and expiration dates
- Registrant name and organization
- Registrant contact information (phone, email address, etc.)
- Registrar information
- Name servers and DNS configuration
- RIR (Regional Internet Registry) information
- Domain status (active, expired, locked, etc.)
- etc.

>[!note] WHOIS records have proven to be extremely useful for maintaining the integrity of the domain name registration and proof website ownership.

## The hierarchy 

To understand the information WHOIS provides, we need to walk through a few important temps first: 

- **Registry**
	- A **domain registry** is an organization responsible for managing and maintaining the database of all domain names registered under a specific TLD (e.g., `.com`, `.org`, etc.).
	- Examples include Verisign (`.com` and `.net`), Afilias (`.info`), and Nominet (`.uk`).
	- Registries are managed by the [ICANN](https://en.wikipedia.org/wiki/ICANN), which oversees the global coordination of domain names and IP addresses.
	- They don't sell domains directly to the public but instead delegate the commercial sales of domain name registrations to accredited *registrars*.
	- If you need to query a niche TLD (e.g., `.io`, `.xyz`), you must identify the specific registry's WHOIS server, as they often differ from the standard `whois.verisign-grs.com`.

- **Registrar**
	- A **domain registrar** is an accredited organization that sells and manages domain name registrations. It's the reseller; it acts as an intermediary between domain registrars and registrants.
	- Registrars are accredited by ICANN (for gTLDs) or the local registry to sell domains.
	- When you run `whois example.com`, you are usually querying the Registrar's database, not the Registry's.

- **Registrant**
	- A **domain registrant** is an individual or organization that registers a domain name (e.g., `example.com`). It's the customer that holds the lease on the domain name.

>A **registrant contact** is a person or organization that registered the domain.

>An **administrative contact** is a person responsible for managing the domain.

>A **technical contact** is a person responsible for handling technical issues related to the domain.

## The WHOIS protocol

>The WHOIS protocol is a query/response protocol used for querying databases that store an Internet resource's registered users or assignees (the WHOIS database).

- The current protocol specification is defined in [`RFC 3912`](https://www.rfc-editor.org/rfc/rfc3912).
- WHOIS servers listen on TCP port `43` by default.
- When you make a query, your WHOIS client connects to a WHOIS server (usually determined by the TLD), and sends the domain name. THe server returns a text block of data and closes the connection.

>[!note] The "Referral" chain
>A common point of confusion is that `whois` often returns a "Referral URL" or a different `Whois Server` line at the bottom of the output. This indicates that the server you just queried (e.g., the Registry) does not hold the detailed contact info, but knows which Registrar does. 
>Tools like `whois` (the Linux binary) often follow these referrals automatically, but manual investigation sometimes requires you to take the `Registrar WHOIS Server` value and query it explicitly with `whois -h <server> <domain>`.

## The WHOIS record

A WHOIS record is a free-form text block. There is no strict XML or JSON standard; it is a legacy format that varies wildly between registrars.

It usually contains:

- Domain name (the FQDN).
- Registry Domain ID (unique identifier of the Registry).
- Registrar IANA ID (unique identifier for the registrar).
- Temporal data:
	- Creation date (when the domain was firest registered).
## Querying the WHOIS: the `whois` tool

The most commonly used way to quiery the WHOIS database is using the [`whois`](https://man.archlinux.org/man/whois.1) tool.

Syntax:

```bash
whois [options] <domain_name>
```


```bash
whois -H example.com
```

| Option                | Description                                                                                      |
| --------------------- | ------------------------------------------------------------------------------------------------ |
| `-h`, `--host <host>` | Specify a custom WHOIS server.                                                                   |
| `-p`, `--port <port>` | Specify a port on the WHOIS server to connect to (default: `43`).                                |
| `-I`                  | Query `whois.iana.org` first and follow its referral.                                            |
| `-H`                  | Hide legal disclaimers.                                                                          |
| `--verbose`           | Verbose mode.                                                                                    |


During a penetration test, ask yourself:

- When was the domain registered? When does it expire? Old domains domains might have some legacy applications running.
- Who is the registrant, administrator, what other contacts can you find? This is a *goldmine* for social engineering. You can then try searching for those people on LinkedIn or other platforms.
- What are the DNS servers responsible for the domain? Note them, may be you can try enumerating them later.

>[!example]- Example: `whois -H github.com` 
> 
> ```bash
> whois github.com -H
> ```
> 
> ```bash
>    Domain Name: GITHUB.COM
>    Registry Domain ID: 1264983250_DOMAIN_COM-VRSN
>    Registrar WHOIS Server: whois.markmonitor.com
>    Registrar URL: http://www.markmonitor.com
>    Updated Date: 2024-09-07T09:16:32Z
>    Creation Date: 2007-10-09T18:20:50Z
>    Registry Expiry Date: 2026-10-09T18:20:50Z
>    Registrar: MarkMonitor Inc.
>    Registrar IANA ID: 292
>    Registrar Abuse Contact Email: abusecomplaints@markmonitor.com
>    Registrar Abuse Contact Phone: +1.2086851750
>    Domain Status: clientDeleteProhibited https://icann.org/epp#clientDeleteProhibited
>    Domain Status: clientTransferProhibited https://icann.org/epp#clientTransferProhibited
>    Domain Status: clientUpdateProhibited https://icann.org/epp#clientUpdateProhibited
>    Name Server: DNS1.P08.NSONE.NET
>    Name Server: DNS2.P08.NSONE.NET
>    Name Server: DNS3.P08.NSONE.NET
>    Name Server: DNS4.P08.NSONE.NET
>    Name Server: NS-1283.AWSDNS-32.ORG
>    Name Server: NS-1707.AWSDNS-21.CO.UK
>    Name Server: NS-421.AWSDNS-52.COM
>    Name Server: NS-520.AWSDNS-01.NET
>    DNSSEC: unsigned
>    URL of the ICANN Whois Inaccuracy Complaint Form: https://www.icann.org/wicf/
>>> Last update of whois database: 2025-10-02T13:59:08Z <<<
> 
> For more information on Whois status codes, please visit https://icann.org/epp
> 
> # ...
> 
> Domain Name: github.com
> Registry Domain ID: 1264983250_DOMAIN_COM-VRSN
> Registrar WHOIS Server: whois.markmonitor.com
> Registrar URL: http://www.markmonitor.com
> Updated Date: 2024-09-07T09:16:33+0000
> Creation Date: 2007-10-09T18:20:50+0000
> Registrar Registration Expiration Date: 2026-10-09T00:00:00+0000
> Registrar: MarkMonitor, Inc.
> Registrar IANA ID: 292
> Registrar Abuse Contact Email: abusecomplaints@markmonitor.com
> Registrar Abuse Contact Phone: +1.2086851750
> Domain Status: clientUpdateProhibited (https://www.icann.org/epp#clientUpdateProhibited)
> Domain Status: clientTransferProhibited (https://www.icann.org/epp#clientTransferProhibited)
> Domain Status: clientDeleteProhibited (https://www.icann.org/epp#clientDeleteProhibited)
> Registrant Organization: GitHub, Inc.
> Registrant Country: US
> Registrant Email: Select Request Email Form at https://domains.markmonitor.com/whois/github.com
> Tech Email: Select Request Email Form at https://domains.markmonitor.com/whois/github.com
> Name Server: ns-421.awsdns-52.com
> Name Server: ns-1283.awsdns-32.org
> Name Server: dns2.p08.nsone.net
> Name Server: dns1.p08.nsone.net
> Name Server: dns3.p08.nsone.net
> Name Server: ns-520.awsdns-01.net
> Name Server: ns-1707.awsdns-21.co.uk
> Name Server: dns4.p08.nsone.net
> DNSSEC: unsigned
> URL of the ICANN WHOIS Data Problem Reporting System: http://wdprs.internic.net/
>>> Last update of WHOIS database: 2025-10-02T13:58:31+0000 <<<
> 
> # ...
> ```

## Privacy, redaction, and RDAP

Most commercial registrars now offer (or enforce) **Privacy Protection** (e.g., "Domains by Proxy", "PrivacyGuardian").

What it does is that instead of showing:

```
Registrant Name: John Doe
Registrant Email: john.doe@company.com
```

The record shows:

```bash
Registrant Name: Registration Private
Registrant Email: domains@privacyguardian.org
```

ICANN is transitioning from the old WHOIS protocol to the **[RDAP (Registration Data Access Protocol)](https://www.icann.org/rdap/)**. RDAP provides JSON responses and allows for tiered access.
But the information is not accessible to the public. Only law enforcement or accredited parties can see full data via an API.
## Online resources

Here are some online resources you can use to query WHOIS information:
 
- [`whoismind`](https://whoismind.com/)
- [`who.is`](https://who.is/)
- [`WhoISrequest`](https://whoisrequest.com/)
- [`Whois Lookup DomainTools`](https://whois.domaintools.com/)
- etc.


>[!warning] The amount of information about the target domain available in the WHOIS database can vary depending on the privacy settings chosen by the registrant. 
>- Some individuals or organizations may opt for privacy protection services offered by domain registrars, which can mask contact information and other details. 
>- However, under some jurisdictions, certain information is required to be publicly available and it can't be masked.
## Historical WHOIS

Current WHOIS data is often useless due to privacy. But **historical WHOIS** records is a goldmine. It allows you to see the data _before_ the owner enabled privacy protection.

Many services gather such information:
- [`WhoisXMLAPI`](https://whois-history.whoisxmlapi.com/lookup)
- [`WhoisFreaks`](https://whoisfreaks.com/)
- [`SecurityTrails`](https://securitytrails.com/)
- [`osint.sh`](https://osint.sh/whoishistory/)
- [`DomainTools`](https://research.domaintools.com/research/whois-history/)
- [`WhoISrequest`](https://whoisrequest.com/history/)
- [`WHOXY`](https://www.whoxy.com/whois-history/)


## IP WHOIS

While domain WHOIS deals with names, **IP WHOIS** deals with numbers. You can use it to trace the ownership of IP addresses.

Resources: 
- [`DNSChecker`](https://dnschecker.org/ip-whois-lookup.php?query=1.1.1.1)