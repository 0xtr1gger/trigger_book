---
created: 2026-10-04
updated: 2026-10-04
---
## DNS

>**DNS (Domain Name System)** is a hierarchical and distributed naming system that translates human-readable domain names into IP addresses.

>[!interesting]+ DNS: the phonebook of the internet
>DNS is often compared to a phonebook

>[!important] DNS typically uses UDP port `53`. TCP port `53` is used for large queries and zone transfers.


>A **Fully Qualified Domain Name (FQDN)** is a domain name that completely specifies its exact location in the tree hierarchy of DNS. An FQDN specifies all domain levels, including the top-level domain (TLD) and the root zone.
## Domain names and domain name hierarchy

>A **domain name** is a unique string of characters that identifies a realm of administrative autonomy, authority, or control. Domain names are used to identify internet services, such as websites, email services, hosts, and so on.

>[!interesting]+ roadmap
> 1. DNS Fundamentals
> 	- What is DNS? Purpose and role in the internet
> 	
> 	- How DNS maps domain names to IP addresses
> 	
> 	- History and evolution of DNS
> 	
> 	- The domain namespace: structure, hierarchy, and delegation
> 	
> 	- Internationalized Domain Names (IDN)
> 
> 2. DNS Architecture & Components
> 	- DNS client-server model
> 	
> 	- Types of DNS servers:
> 	
> 	- Recursive resolver (recursor)
> 	
> 	- Root nameserver
> 	
> 	- TLD nameserver
> 	
> 	- Authoritative nameserver
> 	
> 	- Caching nameserver
> 	
> 	- Zones and zone files: primary/secondary, delegation
> 	
> 	- Domains, subdomains, and FQDNs
> 
> 3. DNS Resolution Process
> 	- Step-by-step DNS query flow (user to IP)
> 
> 	- Recursive vs iterative queries
> 	
> 	- Caching and TTL (Time-to-Live)
> 	
> 	- DNS propagation: what happens when records change
> 	
> 	- Server selection and retransmission
> 	
> 	- DNS Records: Types & Management
> 	- Resource Records (RR):
> 	
> 	- A, AAAA, PTR, CNAME, MX, SRV, TXT, NS, SOA, SPF, DKIM
> 	
> 	- Infrastructure records, wildcards, RRset order
> 	
> 	- How to read and write zone files
> 	
> 	- Managing records: adding, updating, deleting
> 	
> 	- Reverse DNS (PTR records)
> 
> 4. DNS Software & Platforms
> 	- Popular DNS server software: BIND, Windows DNS, Unbound, PowerDNS
> 	
> 	- Forwarders and forwarding
> 	
> 	- Cloud DNS providers: Cloudflare, AWS Route 53, Google Cloud DNS
> 	
> 	- DNS as a managed service
> 
> 5. Practical DNS Setup & Configuration
> 	- Registering and purchasing a domain
> 	
> 	- Setting up basic DNS records for a website or app
> 	
> 	- Delegating subdomains and configuring NS records
> 	
> 	- Setting up custom domains for services (GitHub Pages, DigitalOcean)
> 	
> 	- Infrastructure: Anycast, redundancy, failover
> 
> 6. DNS Tools & Troubleshooting
> 	- Query tools: nslookup, dig, host, traceroute
> 	
> 	- Debugging DNS issues: cache, propagation, misconfiguration
> 	
> 	- Tracing resolution with dig
> 	
> 	- Monitoring DNS health and performance
> 
> 7. Advanced DNS Topics
> 	- Dynamic DNS updates
> 	
> 	- DNS load balancing and GeoDNS
> 	
> 	- DNS wildcards and advanced record types
> 	
> 	- DNS in containerized/cloud environments (Kubernetes CoreDNS)
> 	
> 	- DNS protocol internals: packet structure, flags, EDNS
> 
> 8. DNS Security Foundations
> 	- DNSSEC: signing, validation, chain of trust
> 	
> 	- DNS over TLS (DoT), DNS over HTTPS (DoH)
> 	
> 	- Zone transfer security (AXFR, IXFR, TSIG)
> 	
> 	- Split-horizon DNS
> 	
> 	- Access controls and best practices
> 
> 9. Real-World Projects & Labs
> 	- Set up a custom domain and configure DNS for a static site
> 	
> 	- Delegate subdomains and set up mail records
> 	
> 	- Practice troubleshooting with dig/nslookup
> 	
> 	- Experiment with DNS propagation and TTL changes
> 	
> 	- Simulate DNS failures and recovery
> 
> 10. Further Reading & Community
> 	- Follow comprehensive guides and courses
> 	
> 	- Join DNS and networking communities (roadmap.sh, Reddit, Discord)
> 	
> 	- Stay updated on DNS RFCs and protocol changes
> 

### Top-level domains 

>A **Top-Level Domain (TLD)**, sometimes also called a domain extension or domain suffix, is the last part of a domain name, appearing after the final dot in a domain name. It represents the highest level in the DNS after the root domain. 

>[!note] Most top-level domains are managed by ICANN. 


There are several types of TLDs:

- gTLD, generic top-level domains
	- Top-level domains with three or more characters.

- grTLD, generic restricted top-level domains
	- managed under official ICANN accredited registrars.

- sTLD, sponsored top-level domains
	- proposed and sponsored by private agencies or organizations that establish and enforce rules restricting the eligibility to use the TLD, managed under official ICANN accredited registrars.
	- `.travel`, `.edu`, `.coop`, `.gov`, etc.

- ccTLD, country-code top-level domains
	- two-letter domains established for countries and territories. 
	- `.us`, `.uk`, `.ua`, `.jp`, etc.
	
- IDN ccTLD, internationalized country code top-level domains
	- encoded ccTLDs in non-Latin character sets (e.g., Arabic, Cyrillic, Greek, Hebrew, or Chinese).
	- `.рф`, پاکستان, etc.

- tTLD, test top-level domain
	- intended for usage in software testing, guaranteed to never be registered into the internet. 

- `.arpa`
	- the TLD `.arpa` is mainly used for management of technical network infrastructure, being acronym which stands for Address and Routing Parameter Area.

| TLD       | eligibility                                              |
| --------- | -------------------------------------------------------- |
| `.aero`   | members of the air-transport industry                    |
| `.asia`   | organizations and individuals in the Asia-Pacific region |
| `.cat`    | Catalan linguistic and cultural community                |
| `.coop`   | cooperative associations                                 |
| `.edu`    | US institutions of higher education                      |
| `.gov`    | US government, states and local governments              |
| `.int`    | international treaty-based organisations                 |
| `.jobs`   | employment-related sites                                 |
| `.mil`    | US military entities                                     |
| `.museum` | museums                                                  |
| `.post`   | postal services                                          |
| `.tel`    | for publishing contact data                              |
| `.travel` | travel agencies, airlines, etc.                          |
| `.xxx`    | pornographic sites                                       |
#### International domain names (IDN)



## DNS architecture

DNS servers form a hierarchical structure:

- DNS root server
- Authoritative name server
- Non-authoritative name server
- Caching DNS server
- Forwarding DNS server
- DNS Resolver

![](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/27/tooldev-dns.png)
### Recursive resolver

The **recursive resolver** is the first DNS server your device contacts when you make a DNS query (e.g., typing `www.example.com` in your browser). Its job is to find the answer on your behalf, even if it has to ask several other servers in the DNS hierarchy.

>A **recursive DNS resolver** acts as an intermediary between a user's device and the hierarchical DNS servers. Its primary function is to resolve a user's domain name query into an IP address by performing the full lookup process, starting from the root servers, moving through Top-Level Domain (TLD) servers, and finally querying the authoritative DNS server for the specific domain.

- A recursive resolver also mains a **DNS cache**. If the resolver has a recent answer in its cache, it returns it immediately; this significantly speeds up the process.
- If not cached, the resolver performs a series of queries, starting with the root server, then the TLD server, and finally the authoritative server, to get the answer.

>[!note] Because recursive resolvers are exposed to the public, they are often targets for attacks like DNS cache poisoning and amplification DDoS.
### DNS root server

>A **root name server** is a DNS server that serves the **root DNS zone**, responsible for **top-level domains (TLD)**.

- Root servers answer queries for the location of TLD (Top-Level Domain) servers (e.g., `.com`, `.net`, `.org`, etc.).
- The work of root name servers is coordinated by **[ICANN](https://www.icann.org/) (Internet Corporation for Assigned Names and Numbers)**.
- There are 13 logical root servers (labeled `A`-`M`), but each is actually a cluster of many physical servers distributed globally. These severs are operated by 12 independent organizations.

>[!interesting]+ DNS root servers mapped
>Here are all root servers mapped, take a look: [`root-servers.org`](https://root-servers.org/). This is a Root Server Technical Operations Associations website; there you can also find information on all 12 organizations that maintain the root servers.

>[!interesting]+ Informational homepage
>Each logical root server has an informational homepage (except for G-root, which is under US DoS NIC control) located at `letter.root-servers.org`, where `letter` ranges from `a` to `m` (except `g`). 

>[!important] Root name servers **do not store DNS records for individual domain names**. They only point to the correct TLD server of each domain.
>In fact, the size of the root zone file is only about 2 MB; this zone file is updated by IANA.

>[!example]+
>For example, if you ask for `www.example.com`, the root server will point you to the `.com` TLD server.

>[!interesting]+ To discover all DNS root servers, you can make a **priming query**:
> 
> ```bash
> dig . NS
> ```
> 
> Or just 
> 
> ```bash
> dig
> ```
> 
> ```bash
> ; <<>> DiG 9.20.13 <<>>  
> ;; global options: +cmd  
> ;; Got answer:  
> ;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 54801  
> ;; flags: qr rd ra; QUERY: 1, ANSWER: 13, AUTHORITY: 0, ADDITIONAL: 27  
>   
> ;; OPT PSEUDOSECTION:  
> ; EDNS: version: 0, flags:; udp: 512  
> ;; QUESTION SECTION:  
> ;.                              IN      NS  
>   
> ;; ANSWER SECTION:  
> .                       495366  IN      NS      m.root-servers.net.  
> .                       495366  IN      NS      e.root-servers.net.  
> .                       495366  IN      NS      b.root-servers.net.  
> .                       495366  IN      NS      j.root-servers.net.  
> .                       495366  IN      NS      i.root-servers.net.  
> .                       495366  IN      NS      h.root-servers.net.  
> .                       495366  IN      NS      d.root-servers.net.  
> .                       495366  IN      NS      g.root-servers.net.  
> .                       495366  IN      NS      a.root-servers.net.  
> .                       495366  IN      NS      c.root-servers.net.  
> .                       495366  IN      NS      k.root-servers.net.  
> .                       495366  IN      NS      l.root-servers.net.  
> .                       495366  IN      NS      f.root-servers.net.  
>   
> ;; ADDITIONAL SECTION:  
> f.root-servers.net.     581921  IN      A       192.5.5.241  
> f.root-servers.net.     598548  IN      AAAA    2001:500:2f::f  
> m.root-servers.net.     581749  IN      A       202.12.27.33  
> m.root-servers.net.     581749  IN      AAAA    2001:dc3::35  
> e.root-servers.net.     581907  IN      A       192.203.230.10  
> e.root-servers.net.     590566  IN      AAAA    2001:500:a8::e  
> b.root-servers.net.     581921  IN      A       170.247.170.2  
> b.root-servers.net.     587672  IN      AAAA    2801:1b8:10::b  
> j.root-servers.net.     581875  IN      A       192.58.128.30  
> j.root-servers.net.     594370  IN      AAAA    2001:503:c27::2:30  
> i.root-servers.net.     581875  IN      A       192.36.148.17  
> i.root-servers.net.     587671  IN      AAAA    2001:7fe::53  
> h.root-servers.net.     581909  IN      A       198.97.190.53  
> h.root-servers.net.     595241  IN      AAAA    2001:500:1::53  
> d.root-servers.net.     581806  IN      A       199.7.91.13  
> d.root-servers.net.     585317  IN      AAAA    2001:500:2d::d  
> g.root-servers.net.     581819  IN      A       192.112.36.4  
> g.root-servers.net.     587672  IN      AAAA    2001:500:12::d0d  
> a.root-servers.net.     581754  IN      A       198.41.0.4  
> a.root-servers.net.     581757  IN      AAAA    2001:503:ba3e::2:30  
> c.root-servers.net.     581914  IN      A       192.33.4.12  
> c.root-servers.net.     599249  IN      AAAA    2001:500:2::c  
> k.root-servers.net.     581840  IN      A       193.0.14.129  
> k.root-servers.net.     584193  IN      AAAA    2001:7fd::1  
> l.root-servers.net.     581908  IN      A       199.7.83.42  
> l.root-servers.net.     581749  IN      AAAA    2001:500:9f::42  
>   
> ;; Query time: 23 msec  
> ;; SERVER: 192.168.1.1#53(192.168.1.1) (UDP)  
> ;; WHEN: Fri Sep 19 16:43:27 CEST 2025  
> ;; MSG SIZE  rcvd: 811
> ```

>[!interesting]+ 13 servers
> In the original DNS specification ([`RFC 1035`](https://www.rfc-editor.org/rfc/rfc1035.txt)), UDP DNS packets are limited to `512` bytes by design. 
> 
> The fundamental reason why there are only 13 root servers in the DNS system originates from the **512-byte limitation of DNS UDP packets**, as defined in the original DNS protocol ([`RFC 1035`](https://www.rfc-editor.org/rfc/rfc1035.txt)). Each root server entry includes its name and IP address record; 13 entries were calculated as the maximum number that could fit inside the 512-byte limit.
> 
> Indeed, modern networks can handle larger packets and support extensions like [EDNS0](https://en.wikipedia.org/wiki/Extension_Mechanisms_for_DNS) to increase UDP packet size, but there're still only 13 logical root name servers.

>[!interesting]+ Anycast routing
Each physical server in the cluster is assigned the **same IP address**. **Anycast routing** is used to distribute requests based on load and proximity: an IP packet destined to an anycast IP address of a root name server hits the nearest and least loaded physical server with this IP address.  
### Top-Level Domain (TLD) servers

>A **TLD (Top-Level Domain)** name server is responsible for storing and managing information about all domain names under a specific TLD (e.g., `.com`, `.net`, `.org`). TLD servers are managed by IANA.

- **TLD servers point to the authoritative name servers of each domain.**

- TLD servers are divided into two main groups:
	- Generic TLD (gTLDs)
		- Store records for domains under generic TLDs, e.g., `.com`, `.org`, `.net`, `.edu`, etc.
	- Country-code TLD (ccTLDs)
		- Store records for domains specific to a country or state, e.g., `.uk`, `.us`, `.ru`, `.jp`, etc.


- **Authoritative name server**
- **Non-authoritative name server**
- **Caching DNS server**
- **Forwarding DNS server**
- **DNS Resolver**

### Authoritative name servers

>An **authoritative name server** holds authority for a particular DNS zone. Authoritative name servers store the actual DNS records for a domain (`A`, `AAAA`, `MX`, `CNAME`, etc.).

- Authoritative name servers are a final stop in the DNS lookup process. 
- Authoritative name servers only respond to queries from their area of responsibility. 

There are two types of authoritative name servers:

- **Primary (master)**
	- Holds the original, writable copy of the zone file. All changes are made here.
- **Secondary (slave)**
	- Holds a read-only copy, updated via zone transfers from the primary server. Used for redundancy and load balancing.

### DNS zone transfers

>A **DNS zone transfer**, also known by its DNS record type **`AXRF`**, is a process used to synchronize DNS records between a primary (master) authoritative DNS server to one or more secondary (slave) DNS servers.

>[!important] **DNS zone transfers** are performed over **TCP port `53`**.

>A **DNS zone** represents an administrative portion of the DNS namespace managed as a single unit. 

>[!example] For example, `example.com` with its subdomains may be a DNS zone.

There are two main types of zone transfers:

- **Full zone transfer (`AXFR`)**
	- Transfers the **entire DNS zone** from the primary to the secondary server.
	- Initiated when a secondary server has no zone data or when incremental transfer is unsupported.
	- Uses **TCP port `53`**.
	- Contains all resource records (RRs), starting and ending with the `SOA` record.
	- Bandwidth- and time-intensive for very large zones.

- **Incremental zone transfer (`IXFR`)**
	- Transfers **only the changes** made since the last transfer.
	- Efficient and bandwidth-saving, especially for large zones with few changes.
	- Secondary server provides the serial number of its current zone copy; primary responds with differences.
	- Supported only if both servers implement `IXFR`.

>[!important] Each zone has a **`SOA` (Start of Authority)** record with a serial number of the zone. 

>[!interesting]+ How zone transfers work
> 
> 1. **`SOA` record check**
> 	- The secondary server queries the primary server’s **`SOA` (Start of Authority)** record, which contains a **serial number** (version) of the zone. It compares this with its own cached serial number.
>     
> 2. **Determining the necessity of the transfer**
>     - If the primary’s serial number is **higher**, the secondary knows updates exist and requests a zone transfer.
>     - If the serial numbers match, no transfer needed.
> 
> 3. **Initiate Transfer**
> 	- The secondary initiates a zone transfer by sending a zone transfer request, an `AXFR` (full) or `IXFR` (incremental), over a **TCP connection** to the primary server (port `53`).
>     
> 4. **Primary Responds**
> 	- The primary sends the entire zone data (`AXFR`) or only changes (`IXFR`). The data transfer starts with the `SOA` record and ends with a repeated `SOA` record to signal completion.
>     
> 5. **Update Cache and Refresh Timers**
> 	- Secondary updates its zone file and sets timers for when to check again (refresh interval).
>     
> 6. **`NOTIFY` Messages (Optional):**  
> 	- The primary server can send **`NOTIFY`** messages to secondaries to inform them of updates, allowing immediate zone transfers without waiting for refresh timers.

>[!note] When a change occurs, the primary server can send a `NOTIFY` message to trigger a transfer sooner than the usual refresh interval.

### Non-authoritative name servers

>**Non-authoritative name servers** are servers not responsible for a particular DNS zone.


>An authoritative name server is a name server that is responsible for giving answers in response to questions asked about names in a zone.

- Responsible for storing and managing DNS records for a specific domain or zone
- Holds the original and definitive answers to DNS queries for a particular domain
- Provides IP addresses and other DNS data for a domain
- Can be a managed DNS provider, a domain registrar, or an organization’s own DNS infrastructure

An authoritative name server can either be a primary server or a secondary server:

- Primary authoritative name servers
	- Primary authoritative DNS servers (aka masters) hold the original, authoritative zone data and are responsible for updating and managing the DNS records.

- Secondary  authoritative name servers
	- Secondary authoritative DNS servers (aka slaves) periodically receive zone transfers from the primary server and maintain a read-only copy of the zone data. They act as backups for authoritative name servers.

Both primary and secondary servers can respond authoritatively to DNS queries, but secondary servers rely on the primary server for updates and validation.

The primary name server for a zone notifies all the known secondaries for that zone about changes in its contents, where the content itself is either configured manually by an administrator, or managed with dynamic DNS. 

Every existing domain name appears in a zone file served by one or more authoritative name servers.

When a domain is registered with a domain name registrar, the zone administrator provides the list of name servers (2 or more) that are authoritative for the zone that contains the domain. The registrar provides the names of these servers to the domain registry for the top-level domain containing the zone. The domain registry, in turn, configures the authoritative name servers for that top-level domain with delegations for each server for the zone.


## DNS Resource Records


Common DNS record types:

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


## Querying DNS records


## DNS message structure

The DNS protocol uses two types of DNS messages: **queries** and **responses**; both have the same format.

Each message is divided into 5 sections:
- **Header**
- **Question:** The question for the name server.
- **Answer:** RRs answering the question.
- **Authority:** RRs pointing toward an authority.
- **Additional:** RRs holding additional information.

Here is an example of a DNS query captured in Wireshark:



The corresponding DNS response looks like this:



- **Header**

The DNS header is present in each message and consists of:

| Field                        | Size    | Description                                                                                                                                                |
| ---------------------------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Transaction ID**           | 16 bits | A 16-bit identifier assigned by the program that generates the query; copied in the corresponding reply and can be used to match up responses to requests. |
| **Flags**                    | 16 bits | Flags, provide information about the message.                                                                                                              |
| **Number of Questions**      | 16 bits | The number of questions in the question section.                                                                                                           |
| **Number of Answers**        | 16 bits | The number of answer records in the response.                                                                                                              |
| **Number of Authority RRs**  | 16 bits | The number of authoritative records in the response.                                                                                                       |
| **Number of Additional RRs** | 16 bits | The number of additional records in the response.                                                                                                          |

The flags are:

| Flag     | Size   | Description                                                                                                                                                                                                                                                                                              |
| -------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `QR`     | 1 bit  | Indicates if the message is a query (`0`) or a reply (`1`).                                                                                                                                                                                                                                              |
| `OPCODE` | 4 bits | Defines the query type:<br>`QUERY` (standard query, `0`)<br>`IQUERY` (inverse query, `1`)<br>`STATUS` (server status request, `2`)                                                                                                                                                                       |
| `AA`     | 1 bit  | Authoritative Answer, indicates if the DNS server is authoritative for the queried hostname; `1` if yes.                                                                                                                                                                                                 |
| `TC`     | 1 bit  | Truncation, indicates if this message was truncated due to excessive length; `1` if yes.                                                                                                                                                                                                                 |
| `RD`     | 1 bit  | Recursion Desired, indicates if the client means a recursive query; `1` if yes.                                                                                                                                                                                                                          |
| `RA`     | 1 bit  | Recursion Available (in response), indicates if the replying DNS server supports recursion; `1` if yes.                                                                                                                                                                                                  |
| `Z`      | 1 bit  | Zero, reserved for future use; must always be set to `0`.                                                                                                                                                                                                                                                |
| `AD`     | 1 bit  | Authentic Data (in response), indicates if the replying DNS server has verified the data; `0` if yes.                                                                                                                                                                                                    |
| `CD`     | 1 bit  | Checking Disabled (in query), indicates if non-verified data is acceptable in a response; `0` if yes.                                                                                                                                                                                                    |
| `RCODE`  | 4 bits | Response code, can be:<br>`NOERROR` (`0`)<br>`FORMERR` (`1`, Format error)<br>`SERVFALI` (`2`, Server failure)<br>`NXDOMAIN` (`3`, Nonexistent domain)<br>etc.; for the complete list, see [`DNS RCODEs — IANA`](https://www.iana.org/assignments/dns-parameters/dns-parameters.xhtml#dns-parameters-6). |
- **Question section**

The question section is only present in DNS queries. It consists of domain names (or IP addresses) and resource types the client is requesting.

Each question record (usually just one in the section) consists of:

| Field   | Size     | Description                                                                             |
| ------- | -------- | --------------------------------------------------------------------------------------- |
| `NAME`  | Variable | The name of the requested resource, such as domain or IP address (e.g., `exmaple.com`). |
| `TYPE`  | 2 bytes  | The type of the RRs requested (e.g., `A`, `AAAA`, `MX`, `TXT`, etc.).                   |
| `CLASS` | 2 bytes  | Class code; usually `IN` for Internet.                                                  |

- **Answer section**
	- Contains zero or more records that answer the query, including the requested IP address or other resource records.

- **Authority section**
	- Contains authoritative records for the queried domain

- **Additional section**
	- Contains additional resource records that provide supplemental information.

## DNS security

>[!important] DNS is mainly unencrypted.

### DNSSEC

### DNS over TLS (DoT)
### DNS over HTTPS (DoH)
### DNS over QUIC (DoQ)

### Split-horizon DNS
### Access controls

## Resources and further reading

- https://en.wikipedia.org/wiki/Domain_Name_System
- https://en.wikipedia.org/wiki/List_of_DNS_record_types#AAAA
- [`Domain name — Wikipedia`](https://en.wikipedia.org/wiki/Domain_name)
- https://en.wikipedia.org/wiki/Extension_Mechanisms_for_DNS

- [`DNS server types — Cloudflare`](https://www.cloudflare.com/learning/dns/dns-server-types/)
- [`List of DNS records — Wikipedia`](https://en.wikipedia.org/wiki/List_of_DNS_record_types#AAAA)
- [`Top-level domain — Wikipedia`](https://en.wikipedia.org/wiki/Top-level_domain)

- [`4. MESSAGES, DOMAIN NAMES - IMPLEMENTSTION AND SPECIFICATION — RFC 1035`](https://www.rfc-editor.org/rfc/rfc1035)
- [`DNS RCODEs — IANA`](https://www.iana.org/assignments/dns-parameters/dns-parameters.xhtml#dns-parameters-6)



https://github.com/BlackWolfed/DNS-Penetration-Testing-Methodology