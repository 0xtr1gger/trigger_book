---
created: 2026-07-15
tags:
  - recon
  - enumeration
  - asset_discovery
status: substantial
---
>[!important] This blog is not affiliated with, endorsed by, or sponsored by any of the services mentioned. 
## WHOIS

>**[WHOIS](https://en.wikipedia.org/wiki/WHOIS)** is a **query and response protocol** used to retrieve public registration data for **domain names**, **IP addresses**, and **autonomous systems**.

- WHOIS lookup can reveal:
	- Domain registration and expiration dates
	- Domain registrar
	- Registrant organization (when public)
	- Administrative and technical contacts
	- Authoritative name servers 
	- Domain status (locked, expired, etc.)
	- DNSSEC status
	- Regional Internet Registry (RIR) information for IP addresses

- Although modern privacy regulations have significantly reduced the amount of publicly available contact information, WHOIS remains an important reconnaissance resource for mapping infrastructure and identifying potential relationships between organizations.

>[!note] WHOIS data may be hidden if the registrant uses WHOIS Privacy Protection.
### Domain registration hierarchy: registry vs. registrar vs. registrant

>[ICANN (Internet Corporation for Assigned Names and Numbers)](https://www.icann.org/resources/pages/about-icann) is a non-profit organization responsible for coordinating the DNS and IP address allocation to ensure the stable and secure operation of the global Internet. 

>A **registry** manages every domain registered under a particular TLD (Top-Level Domain). 

- A registry is responsible for:
	- Maintaining the authoritative database of registered domains.
	- Publishing TLD zone files.
	- Operating the registry WHOIS/RDAP service
	- Delegating registrations to accredited registrars.
- For example, the [Verisign](https://www.verisign.com/) registry manages `.com` and `.net` domains, [Public Interest Registry](https://pir.org/) manages `.org`, and [Nominet](https://nominet.uk/) manages `.uk` domains.

>[!note] Neither ICANN nor registries sell domains directly to customers.

>A **registrar** is a company accredited by ICANN (or the appropriate registry) to sell and manage domain registrations.

- The registrar acts as the intermediary between the registrant and the registry. It's typically responsible for registering domains, renewing registrations, maintaining registrant information, and so on.
- Examples include Namecheap, GoDaddy, MarkMonitor, and Cloudflare Registrar.  

>[!note] Most WHOIS records identify the registrar responsible for a domain.

>A **registrant** is an individual or organization that owns the registration rights for a domain.

- For example:

```
Registrant Organization: GitHub, Inc.
Registrant Country: US
```

>[!info]+ Domain contacts
>- A **registrant contact** is the legal owner of the domain registration.
>- An **administrative contact** is responsible for administrative decisions, such as transferring ownership or renewing the registration.
>- A **technical contact** is responsible for technical issues related to the domain, including DNS configuration.
>
>>[!note] Modern WHOIS records often omit these contacts due to privacy regulations, but historical WHOIS databases may still contain them.
## The WHOIS protocol

>WHOIS is a simple **query/response protocol** defined in [`RFC 3912`](https://www.rfc-editor.org/rfc/rfc3912).

- By default, WHOIS servers listen on TCP port `43`. 
- The protocol operates in plain text.
- A client connects to a WHOIS server, sends a domain name as a text string, receives a text response and the server closes the connection.
- Traditional WHOIS has no authentication, no encryption, no standardized output format (returns free-form text). Different registrars therefore produce slightly different WHOIS records.
## Querying WHOIS

- The standard Linux client is simply called [`whois`](https://man.archlinux.org/man/whois.1).

```bash
whois [options] <domain>
```

- Query a domain:

```bash
whois example.com
```

- Suppress lengthy legal notices:

```bash
whois -H example.com
```

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

- Some useful options:

| Option      | Description                                        |
| ----------- | -------------------------------------------------- |
| `-h <host>` | Query a specific WHOIS server.                     |
| `-p <port>` | Specify a custom TCP port (default: 43).           |
| `-I`        | Query `whois.iana.org` first and follow referrals. |
| `-H`        | Suppress legal disclaimers.                        |
| `--verbose` | Display additional debugging information.          |

> [!note]- WHOIS referrals
> A common source of confusion is that a WHOIS lookup may appear to return **two different records**. This happens because WHOIS often follows a **referral chain**. 
> 
> - The registry knows **which registrar manages the domain**, but the registrar usually stores the detailed registration information.
> - For this reason, an initial lookup may contain a field like:
> 
> ```
> Registrar WHOIS Server:
> whois.markmonitor.com
> ```
> 
> - Many WHOIS clients (including the `whois` binary for Linux) automatically follow these referrals and display both responses.
> 
> - If necessary, you can query a registrar directly:
> 
> ```bash
> whois -h whois.markmonitor.com github.com
> ```

- Online resources for querying WHOIS databases:
	- [`whoismind`](https://whoismind.com/)
	- [`who.is`](https://who.is/)
	- [`WhoISrequest`](https://whoisrequest.com/)
	- [`Whois Lookup DomainTools`](https://whois.domaintools.com/)

>[!tip]+
> Whenever you obtain a WHOIS record, ask yourself:
> 
> - Who owns the domain?
> - Is an organization name disclosed?
> - Are employee names visible?
> - Are email addresses exposed?
> - What registrar manages the domain?
> - Which authoritative name servers are used?
> - Can the DNS provider be identified?
> - Is DNSSEC enabled?
> - How old is the domain?
> - Has the domain changed ownership?
> - Are there historical WHOIS records available?
> - Can reverse WHOIS identify additional domains?
> - What should be enumerated next based on this information?

>[!important] The amount of information about the target domain available in the WHOIS database can vary depending on the privacy settings chosen by the registrant. 
>- Some individuals or organizations may opt for privacy protection services offered by domain registrars, which can mask contact information and other details. 
>- Though, under some jurisdictions, certain information is required to be publicly available and it can't be masked.

### Historical data

- Current WHOIS records might be privacy-protected. But this doesn't mean they have never been exposed in the past.
- Services for querying historical WHOIS records:
	- [`WhoisXMLAPI`](https://whois-history.whoisxmlapi.com/lookup)
	- [`WhoisFreaks`](https://whoisfreaks.com/)
	- [`SecurityTrails`](https://securitytrails.com/)
	- [`osint.sh`](https://osint.sh/whoishistory/)
	- [`DomainTools`](https://research.domaintools.com/research/whois-history/)
	- [`WhoISrequest`](https://whoisrequest.com/history/)
	- [`WHOXY`](https://www.whoxy.com/whois-history/)

### Reverse WHOIS

- Multiple domain names registered by the same individual or organization usually have correlations in registrant contact information. You may find other domains registered with the same piece of information (such as an email address, organization, physical address, name, etc.) by performing a **reverse WHOIS lookup**.

- You can use the [`revwhoix`](https://github.com/Sybil-Scan/revwhoix) tool to perform reverse WHOIS lookup from the command line. Under the hood, it queries [`WhoisXMLAPI`](https://main.whoisxmlapi.com/signup) (1,000 API queries for free):

```bash
revwhoix -k "Apple Inc."
```

- Services for reverse WHOIS lookup:
	- [`BigDomainData`](https://www.bigdomaindata.com/reverse-whois/)
	- [`reversewhois.io`](https://www.reversewhois.io/)
	- [`Viewdns.info`](https://viewdns.info/reversewhois/)
	- [`osint.sh`](https://osint.sh/reversewhois/?__cf_chl_f_tk=SdZ4wNfJiVLHWUv56QZ2BmhxGn9BM95BOxmeYtCdNNA-1714630838-0.0.1.1-1493)
	- [`domainq`](https://www.domainiq.com/reverse_whois)
	- [`WhoisFreaks`](https://whoisfreaks.com/tools/whois/reverse/search)
	- [`WHOXY`](https://www.whoxy.com/reverse-whois/)

>[!tip] WHOIS lookup for IP addresses: [`DNSChecker`](https://dnschecker.org/ip-whois-lookup.php?query=1.1.1.1).
