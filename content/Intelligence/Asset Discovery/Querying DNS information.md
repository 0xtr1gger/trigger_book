---
created: 2026-07-15
tags:
  - recon
  - asset_discovery
status: substantial
---
## DNS reconnaissance

>[!info] [**DNS (Domain Name System)**](https://en.wikipedia.org/wiki/Domain_Name_System) is a distributed, hierarchical naming system that translates human-readable domain names (such as `example.com`) into IP addresses and stores other information about Internet services.

>[!note] Most DNS queries use **UDP port `53`**; **TCP port `53`** is typically used for larger responses (such as DNSSEC records) and zone transfers.

>[!note] Querying public DNS records is generally considered **passive reconnaissance** — because the information is intended to be publicly accessible.

- DNS is a critical component of a target infrastructure. It can be used for:
	- Mapping the target network infrastructure: target IP ranges (`A`, `AAAA` records), mail servers (`MX` records), name servers (`NS` records), and so on.
	- Discovering forgotten, outdated, or less secure applications (e.g., `dev.example.com`, `test.example.com`). 
	- Monitoring for changes in the target's infrastructure over time (creation of new subdomains or records).
	- Gaining insights into the target's security posture.
	- Finding sensitive information (`TXT` records).

>[!tip] DNS reconnaissance is not only about finding IP addresses. It's about *mapping the attack surface*. 

## Querying DNS records

### Understanding important record types

| Record  | Record             | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| ------- | ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `A`     | IPv4 address       | Returns a 32-bit IPv4 address of the requested domain.                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `AAAA`  | IPv6 address       | Returns a 128-bit IPv6 address of the requested domain.                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `MX`    | Mail exchange      | Returns a list of mail servers responsible for the requested domain.                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `NS`    | Name server        | Returns a list of authoritative name servers responsible for the zone to which the requested domain belongs.                                                                                                                                                                                                                                                                                                                                                                                            |
| `TXT`   | Text               | Returns text information associated with the requested domain. <br>Can contain arbitrary human-readable text data or machine-readable data related to [OE](https://en.wikipedia.org/wiki/Opportunistic_encryption), [SPF](https://en.wikipedia.org/wiki/Sender_Policy_Framework), [DKIM](https://en.wikipedia.org/wiki/DKIM), [DMARC](https://en.wikipedia.org/wiki/DMARC), [DNS-SD](https://en.wikipedia.org/wiki/DNS-SD), and other. <br>A domain may have multiple `TXT` records associated with it. |
| `CNAME` | Canonical name     | Serves as an alias of one domain name to another; always points to another domain and never to an IP address directly.<br>The DNS lookup will continue querying the domain stored in the `CNAME` record.<br>For example, if you want `www.example.com` to point to the same IP address as `example.com`, you would create an `A`/`AAAA` record for `example.com` and a `CNAME` record for `www.example.com` that points to `example.com`.                                                               |
| `PTR`   | Pointer            | Pointer to a canonical name (`CNAME`). <br>Used in reverse DNS lookup to determine the domain name associated with a given IP address.                                                                                                                                                                                                                                                                                                                                                                  |
| `SOA`   | Start Of Authority | Provides information about the corresponding DNS zone and email address of the administrative contact.                                                                                                                                                                                                                                                                                                                                                                                                  |
| `SRV`   | Service locator    | Generalized service location record, used for newer protocols instead of creating protocol-specific records like `MX`.                                                                                                                                                                                                                                                                                                                                                                                  |

- **`A` and `AAAA` records** — Identifying the IP addresses associated with a domain name.

```bash
dig example.com A
```

```bash
dig example.com AAAA
```

- **`MX` records** — Identifying email servers for the domain; also often reveals third-party email providers the organization uses (if any).

```bash
dig example.com MX
```

> [!example]+
> ```bash
> dig gmail.com MX
> ```
> 
> ```bash
> # ...
> gmail.com.		1376	IN	MX	30 alt3.gmail-smtp-in.l.google.com.
> gmail.com.		1376	IN	MX	40 alt4.gmail-smtp-in.l.google.com.
> gmail.com.		1376	IN	MX	10 alt1.gmail-smtp-in.l.google.com.
> gmail.com.		1376	IN	MX	5 gmail-smtp-in.l.google.com.
> gmail.com.		1376	IN	MX	20 alt2.gmail-smtp-in.l.google.com.
> # ... 
> ```
> 
>>[!note] The lower the preference number the more preferred the server is (the 5th column in the above output). 

- **`NS` records** — Identifying the authoritative DNS servers for a domain; can reveal DNS hosting providers, cloud providers (if any), and geographic distribution.

```bash
dig example.com NS
```

>[!tip]+ Once the authoritative name servers are known, they become useful targets for additional DNS enumeration, including zone transfer testing.

- **`TXT` records** — Can contain arbitrary data, including sensitive information. Common examples:
	- **[SPF (Sender Policy Framework)](https://en.wikipedia.org/wiki/Sender_Policy_Framework)**: Specifies which systems are authorized to send email (e.g., `v=spf1 include:_spf.google.com ~all` reveals use of Google Workspace).
	- **[DKIM (DomainKeys Identified Mail)](https://en.wikipedia.org/wiki/DomainKeys_Identified_Mail)**: Contains public keys used to verify digitally signed email.
	- **[DMARC (Domain-based Message Authentication, Reporting and Conformance)](https://en.wikipedia.org/wiki/DMARC)**: Defines how email authentication failures should be handled (authentication policies, reporting email addresses; e.g., `v=DMARC1; p=reject; rua=mailto:dmarc@example.com`).
	- **Domain verification**: Organizations frequently publish verification tokens for cloud services (e.g., Google Search Console, Microsoft 365, Atlassian, GitHub, etc.); reveals which third-party services are integrated with the organization.
	- **Information disclosure**: Occasionally, TXT records may accidentally expose internal hostnames, API endpoints, legacy verification tokens, employee email addresses, environment identifiers.

```bash
dig example.com TXT
```

- **`CNAME` records** — Revealing dependencies on third-party services (like CDNs, cloud hosting, SaaS applications, load balancers, reverse proxies, etc.).

```bash
dig example.com CNAME
```

- **`SOA` records** — Obtaining administrative information about a DNS zone; reveals the primary authoritative name server, administrative contact, zone serial number, etc.

```bash
dig example.com SOA
```

### Tools and services

- Command-line tools:
	- [`dig`](https://man.archlinux.org/man/dig.1) (Domain Information Groper) 
		- One of the most popular tools for interrogating DNS name servers; versatile, useful for manual DNS queries, zone transfers, and in-depth analysis of DNS records.
	- [`nslookup`](https://man.archlinux.org/man/nslookup.1)
		- Simpler DNS lookup tool, primarily for `A`, `AAAA`, and `MX` records; perfect for basic queries, quick checks of domain resolution and mail server records.
	- [`host`](https://man.archlinux.org/man/host.1)
		- Simple DNS lookup tool, useful for quick checks of `A`, `AAAA`, and `MX` records.

- Online services:

	- [`DNSDumpster.com`](https://dnsdumpster.com/)
		- Shows statistics of IP block owners, lists DNS servers, `MX`, `TXT`, and `A` records (up to 100 with the free plan) for the domain and related subdomains, generates visual network maps, etc.
	
	- [`Pentest Tools Subdomain Finder`](https://pentest-tools.com/information-gathering/find-subdomains-of-domain)
		- Subdomain enumeration, forgotten, hidden subdomains, etc.
	
	- [`DNS SPY`](https://dnsspy.io/)
		- Monitors domains for DNS record changes, tests for zone transfers, etc.
	
	- [`ViewDNS.info`](https://viewdns.info/)
		- WHOIS lookup, `traceroute`, reverse IP address lookup, port scanning, etc.
	
	- [`DNSlytics`](https://dnslytics.com/)
		- Reverse IP lookup, historical information, WHOIS lookup, etc.
	
	- [`urlscan.io`](https://urlscan.io)
		- Lists domain registrant information, DNS records, WHOIS for a given domain, and even provides a set of screenshots of the main page of a website over time.
	
	- [`subdomainfinder`](https://subdomainfinder.c99.nl/scans/2020-07-20/github.com)
		- A subdomain finder that also provides access to historical scans of websites, even a couple of years ago. 

## `dig` — Domain Information Groper

>[`dig`](https://man.archlinux.org/man/dig.1) (Domain Information Groper) is one of the most popular tools for interrogating DNS name servers; versatile, useful for manual DNS queries, zone transfers, and in-depth analysis of DNS records.

- The power of `dig` lies in the level of details it can provide and the ability to query specific name servers.

>[!note] Syntax
> 
> ```bash
> dig [@NAME_SERVER] DOMAIN [TYPE] [OPTIONS]
> ```

>[!example]+
> - Query information about the 13 root name servers:
> 
> ```bash
> dig
> ```

### Querying DNS records

| Domain                  | Description                                                          |
| ----------------------- | -------------------------------------------------------------------- |
| `dig example.com`       | Query `A` records; IPv4 addresses associated with the domain.        |
| `dig example.com AAAA`  | Query `AAAA` records; IPv6 addresses associated with the domain.     |
| `dig example.com NS`    | Query `NS` records; the authoritative name servers for the domain.   |
| `dig example.com MX`    | Query `MX` records; mail servers responsible for the domain.         |
| `dig example.com TXT`   | Query `TXT` records; textual information associated with the domain. |
| `dig example.com CNAME` | Query `CNAME` records; canonical names, or aliases of the domain.    |
| `dig example.com SOA`   | Query `SOA` records; information about the DNS zone.                 |

- Query multiple records at once:

```bash
dig example.com A AAAA MX NS
```

- Query all available records for a domain:

```bash
dig example.com any 
```

```bash
dig example.com ANY
```

>[!warning] Many DNS servers ignore `ANY` queries to reduce load and prevent abuse, as per [`RFC 8482`](https://datatracker.ietf.org/doc/html/rfc8482).

- Specify a DNS server to query:

```bash
dig @1.1.1.1 example.com
```

- Perform a reverse DNS lookup (query a `PTR` record for an IP address):

```bash
dig -x 192.168.1.11
```

- Make a batch query to all of the domains specified in a file:

```bash
dig -f queries.txt
```

- Use TCP instead of UDP:

```bash
dig example.com +tcp
```
### BIND version

Berkeley Internet Name Domain ([BIND](https://en.wikipedia.org/wiki/BIND)) is the most commonly used DNS server in today's Internet. And `dig` can be used to query its version:

```bash
dig -c chaos -t txt @"z.example.com" version.bind
```

>[!example]+ Example: BIND version 
> ```bash
> dig CH TXT version.bind @10.129.134.21
> ```
> 
> ```bash
> ; <<>> DiG 9.18.33-1~deb12u2-Debian <<>> CH TXT version.bind @10.129.134.21
> ;; global options: +cmd
> ;; Got answer:
> ;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 46317
> ;; flags: qr aa rd; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1
> ;; WARNING: recursion requested but not available
> 
> ;; OPT PSEUDOSECTION:
> ; EDNS: version: 0, flags:; udp: 4096
> ; COOKIE: ad8abe1a43ec6e4c0100000068ce990feb9a74054d7f932f (good)
> ;; QUESTION SECTION:
> ;version.bind.			CH	TXT
> 
> ;; ANSWER SECTION:
> version.bind.		0	CH	TXT	"9.16.1-Ubuntu"
> 
> ;; Query time: 69 msec
> ;; SERVER: 10.129.134.21#53(10.129.134.21) (UDP)
> ;; WHEN: Sat Sep 20 07:07:43 CDT 2025
> ;; MSG SIZE  rcvd: 95
> ```

### Output breakdown

>[!example]+
> ```bash
> dig github.com
> ```
> 
> ```
> ; <<>> DiG 9.18.33-1~deb12u2-Debian <<>> github.com
> ;; global options: +cmd
> ;; Got answer:
> ;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 35372
> ;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1
> 
> ;; OPT PSEUDOSECTION:
> ; EDNS: version: 0, flags:; udp: 1232
> ;; QUESTION SECTION:
> ;github.com.			IN	A
> 
> ;; ANSWER SECTION:
> github.com.		39	IN	A	20.26.156.215
> 
> ;; Query time: 3 msec
> ;; SERVER: 1.1.1.1#53(1.1.1.1) (UDP)
> ;; WHEN: Thu Oct 02 14:11:48 CDT 2025
> ;; MSG SIZE  rcvd: 55
> ```

- **Command and version:**
	- The version of the `dig` tool you're using.
	- The domain queried (`github.com`).

```
; <<>> DiG 9.18.33-1~deb12u2-Debian <<>> github.com
```

- **Global options:**
	- Lists any global options used (here, just the default `+cmd`.

```
;; global options: +cmd
```

- **Query response:**
	- Indicates that a response was received from the DNS server.

```
;; Got answer:
```

- **Header section:**
	- The type of the query (`QUERY`).
	- Success status (`NOERROR`).
	- A unique identifier of the query (`35372`).
	- Flags in the DNS header (`qr rd ra`).
	- `QUERY`: Number of questions asked (`1`).
	- `ANSWER`: Number of answers received (`1`).
	- `AUTHORITY`: Number of authority records returned (`0`).
	- `ADDITIONAL`: Number of additional records returned (`1`).

```
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 35372
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1
```

| Flag | Name                 | Description                                                                                                     |
| ---- | -------------------- | --------------------------------------------------------------------------------------------------------------- |
| `qr` | Query Response       | Indicates  that this message is a response (not a query itself).                                                |
| `aa` | Authoritative Answer | The responding nameserver is authoritative for the domain (it holds the original data, not just a cached copy). |
| `rd` | Recursion Desired    | Recursion was requested (i.e., follow referrals to get a complete answer).                                      |
| `ra` | Recursion Available  | Recursion is supported by the server and it was performed for the query.                                        |
| `ad` | Authenticated Data   | The data was authenticated using DNSSEC.                                                                        |
| `cd` | Checking Disabled    | DNSSEC validation was disabled for this query.                                                                  |

>[!note]+ `OPT PSEUDOSECTION`
>The `;; OPT PSEUDOSECTION:` shows [EDNS](https://en.wikipedia.org/wiki/Extension_Mechanisms_for_DNS) (Extension Mechanism for DNS) options, such as UDP packet size or DNSSEC flags.
>```bash
>; EDNS: version: 0, flags:; udp: 1232
>```
>- `udp: 1232` indicates the maximum UDP packet size supported.

 - **Question section: `;; QUESTION SECTION:`**
	- The domain name queried (`github.com`).
	- Class of the record; almost always `IN` for Internet. Classes [Chaos](https://en.wikipedia.org/wiki/Chaosnet "Chaosnet") (CH) and [Hesiod](https://en.wikipedia.org/wiki/Hesiod_\(name_service\) "Hesiod (name service)") (HS) also exist.
	- Record type requested (`A`).

```
;; QUESTION SECTION:
;github.com.			IN	A
```

- **Answer section: `;; ANSWER SECTION:`**
	- The domain name (`github.com`).
	- TTL (Time-To-Live), in seconds (`39`); indicates how long this record is valid for caching.
	- Class of the record (`IN` for Internet).
	- Record type (`A`).
	- The answer, e.g., IP address for `A` record (`20.26.156.215`).

```
;; ANSWER SECTION:
github.com.     39  IN  A  20.26.156.215
```

- **Query statistics**
	- `Query time`: how long the query took.
	- `SERVER: 1.1.1.1#53(1.1.1.1) (UDP)`: the DNS server used (in this case, Cloudflare, port `53`, UDP).
	- `WHEN`: date and time of the query.
	- `MSG SIZE  rcvd: 55`: the size of the DNS response in bytes.

```
;; Query time: 3 msec
;; SERVER: 1.1.1.1#53(1.1.1.1) (UDP)
;; WHEN: Thu Oct 02 14:11:48 CDT 2025
;; MSG SIZE  rcvd: 55
```
### Output options

- Short, concise output:

```bash
dig +short example.com
```

>[!example]+ Example: `dig +short`
>```bash
>dig github.com +short
>```
>```bash
>20.26.156.215
>```

- Display only the answer section of the query output:

```bash
dig +noall +answer example.com
```

>[!example]+ Example: `dig +noall +answer`
> ```bash
> dig github.com +noall +answer
> ```
> 
> ```bash
> github.com.		45	IN	A	20.26.156.215
> ```

- Show query details with comments (default):

```bash
dig example.com +cmd
```

- Show query time and statistics:

```bash
dig example.com +stats
```

- Show additional section:

```bash
dig example.com +additional
```

- Show authority section:

```bash
dig example.com +authority
```

- Show the full path of DNS resolution:

```bash
dig +trace example.com
```

>[!example]- Example: `dig +trace`
> 
> ```bash
> dig github.com +trace
> ```
> 
> ```
> ; <<>> DiG 9.18.33-1~deb12u2-Debian <<>> github.com +trace
> ;; global options: +cmd
> .			516542	IN	NS	a.root-servers.net.
> .			516542	IN	NS	b.root-servers.net.
> .			516542	IN	NS	c.root-servers.net.
> .			516542	IN	NS	d.root-servers.net.
> .			516542	IN	NS	e.root-servers.net.
> .			516542	IN	NS	f.root-servers.net.
> .			516542	IN	NS	g.root-servers.net.
> .			516542	IN	NS	h.root-servers.net.
> .			516542	IN	NS	i.root-servers.net.
> .			516542	IN	NS	j.root-servers.net.
> .			516542	IN	NS	k.root-servers.net.
> .			516542	IN	NS	l.root-servers.net.
> .			516542	IN	NS	m.root-servers.net.
> .			516542	IN	RRSIG	NS 8 0 518400 20251016050000 20251003040000 61809 . Zhr4uI7yeMlur7Nrv6yRVnXrNKrl0OiobNX31G54pL0ViTd9ZpSxalFl rGQeA5LOnxV7TBhZW35lSI9G1m4XYaD6q1whxokFSWgVsKUVl1ZFciW7 47wVEVqoS7iTsEjvbSwpihacfftUt+XdlIDS8Tm8l+VYeZkLT4hHCxnF ImfwQ08rHfy8JWT/gvpsrjoBepfxHFZSduapYimf6OtY6hPRldpCdViz XYx5BARanfHZSCPdNlfVvyylISeh6QowlIt5Hdig4l1hNpElQJOEAOQJ hDcbLmt9ZQAxryfojEgMOOpbMwl0J9P8WjRMEykXfq/SolumcMINkkda kM9rIQ==
> ;; Received 525 bytes from 1.1.1.1#53(1.1.1.1) in 3 ms
> 
> ;; UDP setup with 2001:500:12::d0d#53(2001:500:12::d0d) for github.com failed: network unreachable.
> ;; no servers could be reached
> ;; UDP setup with 2001:500:12::d0d#53(2001:500:12::d0d) for github.com failed: network unreachable.
> ;; no servers could be reached
> ;; UDP setup with 2001:500:12::d0d#53(2001:500:12::d0d) for github.com failed: network unreachable.
> com.			172800	IN	NS	l.gtld-servers.net.
> com.			172800	IN	NS	j.gtld-servers.net.
> com.			172800	IN	NS	h.gtld-servers.net.
> com.			172800	IN	NS	d.gtld-servers.net.
> com.			172800	IN	NS	b.gtld-servers.net.
> com.			172800	IN	NS	f.gtld-servers.net.
> com.			172800	IN	NS	k.gtld-servers.net.
> com.			172800	IN	NS	m.gtld-servers.net.
> com.			172800	IN	NS	i.gtld-servers.net.
> com.			172800	IN	NS	g.gtld-servers.net.
> com.			172800	IN	NS	a.gtld-servers.net.
> com.			172800	IN	NS	c.gtld-servers.net.
> com.			172800	IN	NS	e.gtld-servers.net.
> com.			86400	IN	DS	19718 13 2 8ACBB0CD28F41250A80A491389424D341522D946B0DA0C0291F2D3D7 71D7805A
> com.			86400	IN	RRSIG	DS 8 1 86400 20251016050000 20251003040000 61809 . ksJg/RtyI8bqnt94WFjQc/ov8TelGO8L/YalzxgZGuD3BGr+lOngHJ4W pnMuIVzMAJpRADWFtZTbDTK8wyN1Hnr547yB1E1I6bw4oVww10dxY9sC 6a9hU5aTwi/VLhlyJL0vbBnj87io8LfoEwbAyFmTVGDrbF0Q+HwGL680 RLa+4uSzozIY0nMwwDcvv8VLSzJKLUuCLI4KAEyH9EEup9Fkw3IS0VJG wSMYDYZndFosdBo4yQ6MlxeL4jPs2rZ478gHBoqrVfW06+sojimyeV5x PSDms5L8e5XdxyVOh/fXRGZQ2G/3Rk+u/3HHOBpCkPMoGdP69mFvfRDG aNziFw==
> ;; Received 1170 bytes from 198.41.0.4#53(a.root-servers.net) in 0 ms
> 
> ;; UDP setup with 2001:503:a83e::2:30#53(2001:503:a83e::2:30) for github.com failed: network unreachable.
> github.com.		172800	IN	NS	ns-520.awsdns-01.net.
> github.com.		172800	IN	NS	ns-421.awsdns-52.com.
> github.com.		172800	IN	NS	ns-1707.awsdns-21.co.uk.
> github.com.		172800	IN	NS	ns-1283.awsdns-32.org.
> github.com.		172800	IN	NS	dns1.p08.nsone.net.
> github.com.		172800	IN	NS	dns2.p08.nsone.net.
> github.com.		172800	IN	NS	dns3.p08.nsone.net.
> github.com.		172800	IN	NS	dns4.p08.nsone.net.
> CK0POJMG874LJREF7EFN8430QVIT8BSM.com. 900 IN NSEC3 1 1 0 - CK0Q3UDG8CEKKAE7RUKPGCT1DVSSH8LL NS SOA RRSIG DNSKEY NSEC3PARAM
> CK0POJMG874LJREF7EFN8430QVIT8BSM.com. 900 IN RRSIG NSEC3 13 2 900 20251010002619 20251002231619 20545 com. 18d/nW+EnVZVeNivBco0qqV+ntynlb3MPf1E8txfLgPDnDRcIEvmCGgm nYv9EoD8xhgpS7Of3Y6kzytP9OkMTg==
> 4KB4M5P0V10KIBJ8HQ2VH9EMME8NV6MR.com. 900 IN NSEC3 1 1 0 - 4KB4V9IAMJL29MC1VBJ8NDO7E6SI2B8O NS DS RRSIG
> 4KB4M5P0V10KIBJ8HQ2VH9EMME8NV6MR.com. 900 IN RRSIG NSEC3 13 2 900 20251010020632 20251003005632 20545 com. AYD7URPaELExaxqTMvm6nO7B2hDZbGUB/XIHaCWmxdE+L8x21Mr0duwQ /oc0vT1NGC6PtLiUuGviYQpsVyfUJA==
> ;; Received 635 bytes from 192.41.162.30#53(l.gtld-servers.net) in 0 ms
> 
> github.com.		60	IN	A	20.26.156.215
> github.com.		900	IN	NS	dns1.p08.nsone.net.
> github.com.		900	IN	NS	dns2.p08.nsone.net.
> github.com.		900	IN	NS	dns3.p08.nsone.net.
> github.com.		900	IN	NS	dns4.p08.nsone.net.
> github.com.		900	IN	NS	ns-1283.awsdns-32.org.
> github.com.		900	IN	NS	ns-1707.awsdns-21.co.uk.
> github.com.		900	IN	NS	ns-421.awsdns-52.com.
> github.com.		900	IN	NS	ns-520.awsdns-01.net.
> ;; Received 278 bytes from 205.251.193.165#53(ns-421.awsdns-52.com) in 39 ms
> ```

### Timeout and retries

- Set custom timeout (in seconds):

```bash
dig example.com +time=5
```

- Set the maximum number of retry attempts:

```bash
dig example.com +tries=5
```

## DNS reconnaissance using Nmap NSE scripts

Among other features, Nmap can also be helpful for DNS discovery, all thanks to a wide variety of NSE scripts freely available for use.

```bash
nmap -p <port> -sV --script <script> <target>
```

- [`dns-blacklist`](https://nmap.org/nsedoc/scripts/dns-blacklist.html)
	- Checks target IP addresses against multiple DNS anti-spam and open proxy blacklists and returns a list of services for which an IP has been flagged.

```bash
nmap -sn <ip> --script dns-blacklist
# or
nmap --script dns-blacklist --script-args='dns-blacklist.ip=[ip]'
```

- [`dns-brute`](https://nmap.org/nsedoc/scripts/dns-brute.html)
	- Attempts to enumerate DNS hostnames by brute force guessing of common subdomains.

```bash
nmap --script dns-brute target.com
```

- [`dns-service-discovery`](https://nmap.org/nsedoc/scripts/dns-service-discovery.html)
	- Attempts to discover target hosts' services using the DNS Service Discovery protocol.

```bash
nmap --script=dns-service-discovery <target>
```

- [`dns-nsec-enum`](https://nmap.org/nsedoc/scripts/dns-nsec-enum.html)
	- Enumerates DNS names using the DNSSEC NSEC-walking technique.

```bash
nmap -sSU -p 53 --script dns-nsec-enum --script-args dns-nsec-enum.domains=target.com <target>
# dns-nsec-enum.domains - the domain or list of domains to enumerate. If not provided, the script will make a guess based on the name of the target.
```

- [`dns-srv-enum`](https://nmap.org/nsedoc/scripts/dns-srv-enum.html)
	- Enumerates various common service (`SRV`) records for a given domain name.

```bash
nmap --script dns-srv-enum --script-args dns-srv-enum.domain='target.com' <target>
# dns-srv-enum.domain - string containing the domain to queiry
```

- [`dns-zone-transfer`](https://nmap.org/nsedoc/scripts/dns-zone-transfer.html)
	- Requests a zone transfer (`AXFR`) from a DNS server.

```bash
nmap --script dns-zone-transfer --script-args dns-zone-transfer.domain=target.com <target>
```

- [`dns-nsid`](https://nmap.org/nsedoc/scripts/dns-nsid.html)
	- Retrieves information from a DNS name server by requesting its name server ID (`nsid`) and asking for its `id.server` and `version.bind` values.
	- Equivalent to `dig CH TXT bind.version @target; dig +nsid CH TXT id.server @target`.

```bash
nmap -sSu -p 53 --script dns-nsid <target>
```

- [`dns-fuzz`](https://nmap.org/nsedoc/scripts/dns-fuzz.html)
	- Launches a DNS fuzzing attack against DNS servers. The script induces errors into randomly generated but valid DNS packets.

- [`dns-check-zone`](https://nmap.org/nsedoc/scripts/dns-check-zone.html)
	- Checks DNS zone configuration against best practices, including RFC 1912.

## References and further reading

- [`53 - Pentesting DNS — HackTricks`](https://hacktricks.wiki/en/network-services-pentesting/pentesting-dns.html)
- [`Passive information gathering — Hacker's Grimoire`](https://vulp3cula.gitbook.io/hackers-grimoire/recon/passive-information-gathering)
- [`Reconnaissance and Scanning — s0cm0nkey's Security Reference Guide`](https://s0cm0nkey.gitbook.io/s0cm0nkeys-security-reference-guide/red-offensive/scanning-active-recon)