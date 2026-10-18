---
created: 2026-07-15
updated: 2026-09-26
tags:
  - intel
status: complete
---

>[!note] See also [[Virtual host enumeration|Virtual host enumeration]].

## Passive subdomain enumeration

>**Passive subdomain enumeration** is the process of discovering subdomains from publicly accessible information and third-party services, **without directly interacting with the target servers**.

>[!important] Subdomains discovered passively must be validated — the data may be outdated. See [[#DNS brute-force]].

### Third-party datasets

- Passive enumeration often relies on **third-party datasets** of asset intelligence gathered by external organizations. Rather than interacting with the target, you query these datasets to discover subdomains and other assets.
- Third-party datasets aggregate information from many independent sources:
	- Historical DNS resolution records (passive DNS)
	- Internet-wide scanning
	- WHOIS and registration data
	- Web crawling
	- Malware telemetry
	- Security research
	- Publicly available OSINT
- Because each provider maintains its data independently, coverage, update frequency, and retention differ. Querying multiple providers therefore yields more complete results than relying on a single source.
- Common providers:
	- [`Shodan`](https://www.shodan.io/)
	- [`Censys`](https://censys.com/)
	- [`BinaryEdge`](https://www.binaryedge.io/)
	- [`VirusTotal`](https://www.virustotal.com/gui/home/upload)
	- [`SecurityTrails`](https://securitytrails.com/)
	- [`DNSDumpster`](https://dnsdumpster.com/)
	- [`Netlas`](https://netlas.io/)
	- [`FullHunt`](https://fullhunt.io/)
	- [`Chaos`](https://chaos.projectdiscovery.io/) (`ProjectDiscovery`)
	- [`WhoisXMLAPI`](https://www.whoisxmlapi.com/)
- More than [90](https://gist.github.com/sidxparab/22c54fd0b64492b6ae3224db8c706228) public and commercial providers exist, each exposing different datasets and APIs.
- Rather than querying each service individually, you can use tools like [`Amass`](https://github.com/owasp-amass/amass), [`Subfinder`](https://github.com/projectdiscovery/subfinder), [`Assetfinder`](https://github.com/tomnomnom/assetfinder), and [`Findomain`](https://github.com/Findomain/Findomain) that automate requests to many providers and merge the results into a single output.

>[!note] Some sources are publicly accessible, but many require API keys. Keys are often free (usually with limits); some are paid-only.

- [`Chaos`](https://chaos.projectdiscovery.io/) and its [`chaos-client`](https://github.com/projectdiscovery/chaos-client) provide access to a curated dataset of subdomains that `ProjectDiscovery` has already crawled, primarily sourced from public bug bounty program scopes (shouldn't be treated as a substitute for tools like `subfinder` or `amass`).
#### Amass passive mode

>[`Amass`](https://github.com/owasp-amass/amass) is an attack surface discovery tool that supports both passive and active reconnaissance.

- In passive mode, Amass enumerates subdomains by querying third-party data providers, without interacting directly with the target's infrastructure.

>[!note]+ Installation
>
> - With `go install`:
>
> ```bash
> CGO_ENABLED=0 go install -v github.com/owasp-amass/amass/v5/cmd/amass@main
> ```
>
>See [`Getting Started — Amass Docs`](https://owasp-amass.github.io/docs/#getting-started).

- List all supported data sources:

```bash
amass enum -list
```

##### Configuration

- API keys are configured in `~/.config/amass/config.ini`.

>[!note] See [`Amass Data Sources Configuration — Amass Docs`](https://owasp-amass.github.io/docs/configuration/data_sources/).

##### Usage

>[!note] These commands perform **passive enumeration only** — no active probes or DNS resolution.

- Enumerate subdomains of a single domain:

```bash
amass enum -passive -d example.com
```

- Enumerate multiple domains and save the results to a file:

```bash
amass enum -passive -d example1.com -d example2.com -o results.txt
```

| Option     | Description                                                     |
| ---------- | -------------------------------------------------------------- |
| `-passive` | Passive enumeration only (no active probes or DNS resolution). |
| `-include` | Include specific data sources (comma-separated).               |
| `-exclude` | Exclude specific data sources (comma-separated).               |
| `-o`       | Write output to a file.                                        |
| `-timeout` | Enumeration timeout (minutes).                                 |
| `-v`       | Enable verbose output.                                        |

#### Subfinder

>[`Subfinder`](https://github.com/projectdiscovery/subfinder) is a passive subdomain enumeration tool that discovers subdomains by querying third-party data providers.

>[!note] Subfinder does not interact directly with the target unless active verification is explicitly enabled.

>[!note]+ Installation
> - With `go install`:
>
> ```bash
> go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
> # requires go1.21 or later
> ```
>See [`Installing Subfinder — ProjectDiscovery`](https://docs.projectdiscovery.io/opensource/subfinder/install).

- Without additional configuration, Subfinder uses only publicly available sources.
- List all supported data sources:

```bash
subfinder -ls
```

##### Configuration

- API keys are configured in `~/.config/subfinder/provider-config.yaml`:

```YAML
securitytrails: [] # empty
censys:
  - <censys_API_key>
shodan:
  - <shodan_API_key>
github:
  - <github_API_key_1>
  - <github_API_key_2>
# ...
```

##### Usage

- Use all configured providers:

```bash
subfinder -d example.com -all -o results.txt
```

- Enumerate multiple target domains:

```bash
subfinder -d example1.com,example2.com -all -o results.txt 
```

- Read target domains from a file:

```bash
subfinder -dL target_domains.txt -all -o results.txt 
```

- Use specific sources only:

```bash
subfinder -d target.com -s virustotal,crtsh,github
```

| Option                    | Description                                                                                    |
| ------------------------- | --------------------------------------------------------------------------------------------- |
| `-d`                      | Domains to find subdomains for.                                                               |
| `-dL`                     | File with target domains.                                                                     |
| `-s`, `-sources`          | Use specific providers.                                                                       |
| `-recursive`              | Use only sources that can handle subdomains recursively.                                      |
| `-all`                    | Use all sources for enumeration (slow).                                                       |
| `-es`, `-exclude-sources` | Sources to exclude from enumeration.                                                          |
| `-m`, `-match`            | Subdomain or list of subdomains to match (file or comma-separated list).                     |
| `-f`, `-filter`           | Subdomain or list of subdomains to filter (file or comma-separated list).                    |
| `-rl`, `-rate-limit`      | Maximum number of HTTP requests to send per second.                                           |
| `-t`                      | Number of concurrent goroutines for resolving (only with `-active`); default `10`.            |
| `-up`, `-update`          | Update `subfinder` to the latest version.                                                     |
| `-o`, `-output`           | Output file.                                                                                  |
| `-oJ`, `-json`            | Write output in JSON format.                                                                  |
| `-oD`, `-output-dir`      | Directory to write output to (`-dL` only).                                                    |
| `-cs`, `-collect-sources` | Include all sources in the output.                                                            |
| `-oI`, `-ip`              | Include host IP in output (`-active` only).                                                   |
| `-pc`, `-provider-config` | Provider configuration file, default `~/.config/subfinder/provider-config.yaml`.              |
| `-nW`, `-active`          | Display active subdomains only.                                                               |
| `-proxy`                  | HTTP proxy to use for HTTP requests.                                                          |
| `-ei`, `-exclude-ip`      | Exclude IP addresses from the list of domains.                                                |
| `-v`                      | Produce verbose output.                                                                        |
| `-ls`, `-list-sources`    | List supported providers.                                                                     |
| `-silent`                 | Show only subdomains in output.                                                               |

##### Sources

>[!note]- Sources that don't require API keys
>
> ```bash
> anubis
> commoncrawl
> crtsh
> digitorus
> hackertarget
> rapiddns
> sitedossier
> threatcrowd
> waybackarchive
> hudsonrock
> ```

>[!note]- Sources that require API keys
>
> ```bash
> alienvault
> bevigil
> bufferover
> c99
> censys
> certspotter
> chaos
> chinaz
> dnsdb
> dnsdumpster
> domainsproject
> dnsrepo
> driftnet
> fofa
> fullhunt
> github
> intelx
> netlas
> onyphe
> leakix
> quake
> pugrecon
> redhuntlabs
> robtex
> rsecloud
> securitytrails
> shodan
> threatbook
> virustotal
> whoisxmlapi
> windvane
> zoomeyeapi
> facebook
> builtwith
> digitalyama
> ```

>[!note]- Provider URLs
>
> | Name             | URL                                                   |
> | ---------------- | ----------------------------------------------------- |
> | `BeVigil`        | `https://bevigil.com/osint-api`                       |
> | `BinaryEdge`     | `https://binaryedge.io`                               |
> | `BufferOver`     | `https://tls.bufferover.run`                          |
> | `BuiltWith`      | `https://api.builtwith.com/domain-api`                |
> | `C99`            | `https://api.c99.nl/`                                 |
> | `Censys`         | `https://censys.io`                                   |
> | `CertSpotter`    | `https://sslmate.com/certspotter/api/`                |
> | `Chaos`          | `https://chaos.projectdiscovery.io`                   |
> | `Chinaz`         | `http://my.chinaz.com/ChinazAPI/DataCenter/MyDataApi` |
> | `DNSDB`          | `https://api.dnsdb.info`                              |
> | `dnsrepo`        | `https://dnsrepo.noc.org`                             |
> | `Facebook`       | `https://developers.facebook.com`                     |
> | `Fofa`           | `https://fofa.info/static_pages/api_help`             |
> | `FullHunt`       | `https://fullhunt.io`                                 |
> | `GitHub`         | `https://github.com`                                  |
> | `Hunter`         | `https://hunter.qianxin.com/`                         |
> | `Intelx`         | `https://intelx.io`                                   |
> | `PassiveTotal`   | `http://passivetotal.org`                             |
> | `quake`          | `https://quake.360.cn`                                |
> | `Robtex`         | `https://www.robtex.com/api/`                         |
> | `SecurityTrails` | `http://securitytrails.com`                           |
> | `Shodan`         | `https://shodan.io`                                   |
> | `ThreatBook`     | `https://x.threatbook.cn/en`                          |
> | `VirusTotal`     | `https://www.virustotal.com`                          |
> | `WhoisXML`       | `https://whoisxmlapi.com/`                            |
> | `ZoomEye`        | `https://www.zoomeye.org`                             |

### Certificate Transparency logs

>**[Certificate Transparency (CT)](https://en.wikipedia.org/wiki/Certificate_Transparency)** is an open framework and Internet security standard ([`RFC 6962`](https://datatracker.ietf.org/doc/html/rfc6962)) for monitoring and auditing the issuance of digital certificates.

- CT **requires** publicly trusted Certificate Authorities (CAs) to add issued TLS certificates to **publicly accessible, append-only CT logs**. Each record must include the full domain and **all subdomains** the certificate is issued for.
- This makes CT logs one of the most reliable sources for passive subdomain enumeration. However, they only reveal domains that are (or were) present in public certificates — domains without certificates won't appear.

>[!note] Newly issued certificates may take several minutes to appear in the logs.

- The primary source of CT logs is **[`crt.sh`](https://crt.sh/)**, which provides a web interface and can return JSON. Query it with `curl` and parse with `jq`:

```bash
curl -s "https://crt.sh/?q=%25.example.com&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u
```

>[!warning] [`crt.sh`](https://crt.sh/) has occasional periods of downtime or high latency. [`Merklemap`](https://www.merklemap.com/) and [`SSLMate’s Cert Spotter`](https://sslmate.com/certspotter/) can be used as a fallback.

- Subfinder can also query CT logs:

```bash
subfinder -d example.com -sources crtsh -o subfinder_ct.txt
```

- You can also use [`tlsx`](https://github.com/projectdiscovery/tlsx) to query CT logs.

```bash
tlsx -u example.com -ctl -silent
```

>[!note] [`Censys.io`](https://search.censys.io/) can be more up-to-date than `crt.sh` in some cases, but it doesn't cover all CT logs and requires registration.

>[!note]+ Online CT log checkers
> - [`Qualys`](https://www.ssllabs.com/ssltest)
> - [`SSLmarket`](https://www.sslmarket.com/ssl-verification-tool/?domain=github.com)
> - [`namecheap`](https://decoder.link/sslchecker/)

### SAN (Subject Alternative Name)

>**SAN (Subject Alternative Name)** is an X.509 certificate extension that specifies additional domain names or IP addresses the certificate protects, beyond the Common Name (CN).

>[!note] [`RFC 2818`](https://datatracker.ietf.org/doc/html/rfc2818) specifies SAN as the preferred method of adding DNS names to certificates.

- Because a single certificate can cover multiple domains and subdomains, examining the SAN field can uncover subdomains that are not advertised publicly elsewhere.

>[!example] A certificate for `www.example.com` may include SAN entries for `dev.example.com`, `test.example.com`, and so on.

- Extract the domain names from the SAN field of a TLS certificate with OpenSSL:

```bash
openssl s_client -connect example.com:443 2>/dev/null | openssl x509 -noout -ext subjectAltName | grep -oP '(?<=DNS:|IP Address:)[^,]+'|sort -uV
```

>[!note]- Command breakdown
> - `openssl s_client -connect example.com:443` — Retrieve the certificate of `example.com` by connecting over TLS (port `443`).
> - `2>/dev/null` — Suppress error messages.
> - `openssl x509 -noout -ext subjectAltName` — Print only the SAN field.
> - `grep -oP '(?<=DNS:|IP Address:)[^,]+'|sort -uV` — Arrange the subdomains into a clean column.

>[!example]+
>
> ```bash
> openssl s_client -connect wikimedia.org:443 2>/dev/null | openssl x509 -noout -ext subjectAltName | grep -oP '(?<=DNS:|IP Address:)[^,]+'|sort -uV
> ```
>
>![[san_openssl_wikimedia.png]]

- Alternatively, use [`san_subdomain_enum`](https://github.com/appsecco/the-art-of-subdomain-enumeration/blob/master/san_subdomain_enum.py) (a Python script):

```bash
python ./san_subdomain_enum.py domain.com
```

#### `tlsx`

>[`tlsx`](https://github.com/projectdiscovery/tlsx) is a TLS grabber designed mainly for information gathering.

- `tlsx` can retrieve subdomains from both CT logs and SAN fields.

>[!note]+ Installation
>```bash
>go install github.com/projectdiscovery/tlsx/cmd/tlsx@latest
>```

- Find all subdomains of `example.com` ever recorded in public CT logs:

```bash
tlsx -u example.com -ctl -silent
```

- Extract subdomains from the SAN field of a certificate:

```bash
tlsx -u api.example.com -san -silent
```

- Reverse IP address lookup:

```bash
echo "203.0.113.12" | tlsx -l - -cn -silent
```

| Option    | Description        |
| --------- | ------------------ |
| `-u`      | Target host.       |
| `-san`    | Print SAN entries. |
| `-ctl`    | Stream CT logs.    |
| `-cn`     | Print Common Name. |
| `-silent` | Silent output.     |
| `-json`   | JSON output.       |
| `-o`      | Output file.       |

### Search engines

- Search engines can reveal publicly accessible subdomains indexed by web crawlers. This is particularly useful for finding legacy applications, forgotten virtual hosts, and Internet-exposed development environments.
>[!note] See [[🛠️ Searching the web#Search operators]] for operator syntax across search engines and [[🛠️ Searching the web#Dork databases]] for dork collections.

- The methodology is simple: make a search query, extract URLs from the results, strip unnecessary parts to get the domains, and remove duplicates.
- The `site:` operator filters results to a specific domain and is supported by most engines. Combine it with a wildcard to match subdomains:

```text
site:*.example.com
```

- Exclude results from a specific subdomain:

```text
site:*.example.com -site:www.example.com
```

- Tools like [`GoogleEnum`](https://github.com/psjs97/GoogleEnum) and [`sd-goo`](https://github.com/darklotuskdb/sd-goo) automate the process.

> [!example]+ Example: enumerating subdomains with `GoogleEnum`
>
> ```bash
> python3 google_enum -d example.com -o results.txt
> ```

### Web archives

- Archived pages often reference historical subdomains, legacy applications, retired API endpoints, and deprecated hostnames. Many of these hosts are no longer indexed by search engines but may still resolve.
- To enumerate subdomains, pull all URLs archived under the target domain and its subdomains, extract the domain names, and remove duplicates.
- Retrieve all archived URLs under the domain with `waybackurls` (it includes subdomains by default):

```bash
echo example.com | waybackurls > urls.txt
```

- Extract the unique domain names from the URLs with [`unfurl`](https://github.com/tomnomnom/unfurl):

```bash
cat urls.txt | unfurl --unique domains
```

>[!note] See [[🛠️ Searching the web#Searching web archives]] for archive sources, query syntax, and other tools.

## Active subdomain enumeration

>**Active subdomain enumeration** is the process of discovering subdomains through **direct interaction with the target infrastructure**.

>[!warning] Active techniques generate traffic directed at the target and may therefore be detected, logged, or rate-limited.

### DNS brute-force

- DNS brute-force generates candidate hostnames from a wordlist and queries the target's authoritative DNS servers to determine whether each hostname exists. If a DNS record exists, the hostname is valid; otherwise the query returns a negative response such as `NXDOMAIN`.

>[!note] Brute-force is often the only way to discover subdomains that:
> - have never appeared in Certificate Transparency logs,
> - are absent from historical DNS datasets,
> - are not indexed by search engines,
> - are not referenced anywhere publicly.

- Effectiveness depends primarily on:
	- the quality of the wordlist,
	- wildcard DNS handling,
	- resolver quality,
	- query throughput.
- Several tools implement DNS brute-force with different approaches:
	- [`PureDNS`](https://github.com/d3mondev/puredns) — High-performance brute-force tool; accurately filters wildcards and can validate enumeration results (uses `massdns`).
	- [`massdns`](https://github.com/blechschmidt/massdns) — Extremely fast DNS resolver; used as the backend for many enumeration tools.
	- [`Amass`](https://github.com/owasp-amass/amass) — Attack surface mapping tool; supports recursive DNS brute-force among other techniques.
	- [`gobuster`](https://github.com/OJ/gobuster) — Lightweight brute-force tool; suitable for smaller engagements.

>[!tip] For large engagements, **PureDNS** is generally preferred because it combines high query throughput with automatic wildcard filtering and validation against trusted resolvers.

>[!important] This method is also the standard final step to **validate subdomains obtained with other passive and active techniques**.

>[!note] See [[#Appendix A Wildcard DNS records]].

#### Wordlists

- [`2m-subdomains.txt`](https://wordlists-cdn.assetnote.io/data/manual/2m-subdomains.txt) — 2 million+ subdomains from [Assetnote](https://wordlists.assetnote.io/), generated from the GitHub dataset on BigQuery.
- [`best-dns-wordlist.txt`](https://wordlists-cdn.assetnote.io/data/manual/best-dns-wordlist.txt) — 9 million+ subdomains from Assetnote. Manually generated; one of the most comprehensive.
- [`n0kovo_subdomains`](https://github.com/n0kovo/n0kovo_subdomains/blob/main/n0kovo_subdomains_huge.txt) — 3 million+ subdomains by [N0kovo](https://github.com/n0kovo); see [this blog](https://n0kovo.github.io/posts/subdomain-enumeration-creating-a-highly-efficient-wordlist-by-scanning-the-entire-internet).
- [`six2dez_small_wordlist`](https://gist.githubusercontent.com/six2dez/a307a04a222fab5a57466c51e1569acf/raw) — 102k subdomains by [`six2dez`](https://github.com/six2dez).

- SecLists:
	- [`Discovery/DNS/subdomains-top1million-5000.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/DNS/subdomains-top1million-5000.txt)
	- [`Discovery/DNS/subdomains-top1million-20000.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/DNS/subdomains-top1million-20000.txt)
	- [`Discovery/DNS/subdomains-top1million-110000.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/DNS/subdomains-top1million-110000.txt)
	- [`Discovery/DNS/n0kovo_subdomains.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/DNS/n0kovo_subdomains.txt)
	- [`Discovery/Web-Content/common.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/common.txt)

```bash
curl -o ./subdomains-top1million-110000.txt https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-110000.txt
```

- Wordlist collections:

| Collection                                                                        | Description                                                                                                  |
| --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| [`danielmiessler/SecLists`](https://github.com/danielmiessler/SecLists)           | A collection of multiple types of wordlists for fuzzing, enumeration, and vulnerability testing.            |
| [`Assetnote`](https://wordlists.assetnote.io/)                                    | A collection of wordlists for various purposes.                                                             |
| [`Karanxa/Bug-Bounty-Wordlists`](https://github.com/Karanxa/Bug-Bounty-Wordlists) | A repository with a wide variety of wordlists for testing and enumeration.                                  |
| [`xajkep/wordlists`](https://github.com/xajkep/wordlists?tab=readme-ov-file)      | A collection of wordlists of various kinds plus language dictionaries (English, French, Spanish, Irish, etc.). |

>[!tip] You can also use [`CeWL`](https://github.com/digininja/CeWL) to generate custom wordlists from information scraped off the target website.

##### Permutation-based enumeration

- DNS brute-force relies on predefined wordlists, but many subdomains follow naming conventions unique to an organization. Rather than guessing new names, **permutation-based enumeration** generates additional candidates from hostnames that have already been discovered. This often uncovers subdomains that generic wordlists would miss.

>[!example]+
> Given the hostname `api.example.com`, a permutation generator may produce:
>
> ```
> api-dev.example.com
> api-test.example.com
> api-staging.example.com
> api-v2.example.com
> old-api.example.com
> internal-api.example.com
> ```

>[!note] Permutation tools only create wordlists for enumeration; they don't send any active or passive probes.

- Generate permutation wordlists from already-discovered subdomains with [`alterx`](https://github.com/projectdiscovery/alterx):

```bash
alterx -l subdomains.txt
```

>[!note]- Installation
>```bash
>go install github.com/projectdiscovery/alterx/cmd/alterx@latest
>```
> See [`Installation — alterx`](https://github.com/projectdiscovery/alterx).

- Add custom words:

```bash
alterx -l subdomains.txt -pp words.txt
```

- Write output:

```bash
alterx -l subdomains.txt -p candidates.txt
```

- Pipe into PureDNS for validation:

```bash
alterx -l subdomains.txt | puredns resolve -r resolvers.txt
```
#### PureDNS

>[`PureDNS`](https://github.com/d3mondev/puredns) is designed for large-scale DNS brute-force and can resolve **millions** of queries in minutes.

- `PureDNS` relies on [`massdns`](https://github.com/blechschmidt/massdns), a stub resolver that queries multiple public DNS servers in parallel.

>[!warning] PureDNS can crush your router ☀️.

>[!note]- Installation
>
> - PureDNS requires `massdns`, so install it first:
>
> ```bash
> git clone https://github.com/blechschmidt/massdns.git && \
> cd massdns && \
> make
> ```
>
> ```bash
> sudo make install
> ```
>
>- Then install PureDNS:
>
> ```bash
> go install github.com/d3mondev/puredns/v2@latest
> ```
>See [`Installation — PureDNS`](https://github.com/d3mondev/puredns#installation).

- Basic DNS brute-force resolves each candidate from `wordlist.txt` against the public resolvers in `resolvers.txt` and outputs valid subdomains:

```bash
puredns bruteforce wordlist.txt example.com -r resolvers.txt
```

>[!note] See [[#Obtaining up-to-date resolver lists]].

>[!interesting]+ PureDNS workflow
> 1. Before querying anything, PureDNS removes domains with invalid characters (not in `[a-z0-9.-]`) and duplicates.
> 2. It then uses `massdns` to query the public DNS resolvers from the resolver list.
> 3. Results from `massdns` are validated against trusted resolvers such as Cloudflare (`1.1.1.1`) and Google (`8.8.8.8`, `8.8.4.4`). If a result doesn't match what the trusted resolvers return, it's discarded.

- For more control over performance and accuracy:

```bash
puredns bruteforce wordlist.txt example.com --rate-limit 500 --rate-limit-trusted 500 -r resolvers.txt --wildcard-batch 10000
```

| Option                 | Description                                                                                                                                                                                                                                        |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--rate-limit`         | Queries per second sent to public resolvers through `massdns`.                                                                                                                                                                                     |
| `--rate-limit-trusted` | Query rate against the trusted resolvers (e.g., Cloudflare, Google).                                                                                                                                                                               |
| `--wildcard-batch`     | Batch size for wildcard filtering. <br>Rather than checking each result individually against trusted resolvers (slow), PureDNS groups results into batches. Larger batches are faster but use more memory; smaller batches *may be* more accurate. |
| `--threads`            | Number of concurrent resolver queries. The optimal value depends on your network capacity and the target's DNS infrastructure.                                                                                                                     |
##### Obtaining up-to-date resolver lists

- PureDNS requires two wordlists: one of candidate subdomains and another of **public DNS resolvers**.
---
- Public DNS resolvers change constantly — servers go down, new ones appear, and existing ones become misconfigured. Each query to a dead server has to time out (this is UDP), so a stale resolver list slows enumeration dramatically.
- To check reliability, compare a resolver's responses against trusted resolvers such as Cloudflare (`1.1.1.1`) and Google (`8.8.8.8`). If the results differ or the server doesn't respond, remove it from the list.
- One of the most reliable resolver lists is [`Trickest's list of DNS resolvers`](https://github.com/trickest/resolvers), **updated daily**. It aggregates work from open source contributors like [`proabiral`](https://github.com/proabiral/Fresh-Resolvers) and [`janmasarik`](https://github.com/janmasarik/resolvers) and validates resolvers with [`dnsvalidator`](https://github.com/vortexau/dnsvalidator).

```bash
curl -o resolvers.txt https://raw.githubusercontent.com/trickest/resolvers/main/resolvers.txt
```


#### `gobuster`

>[`gobuster`](https://github.com/OJ/gobuster) is a lightweight, fast brute-force tool written in Go. Its `dns` mode discovers subdomains by resolving each candidate hostname from a wordlist.

- `gobuster` resolves against your system's configured DNS resolver by default, so it doesn't need `resolvers.txt`. This makes it the quickest option for smaller scopes — one command against a wordlist, no resolver list to fetch or validate. For large-scale brute-force with wildcard filtering and validation, prefer [[#PureDNS]].

>[!note]- Installation
> - Pre-installed on Kali and Parrot. Otherwise, with `go install`:
>
> ```bash
> go install github.com/OJ/gobuster/v3@latest
> ```

- Brute-force subdomains using a SecLists wordlist:

```bash
gobuster dns -d example.com -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt
```

- Show the resolved IP addresses and query a specific resolver:

```bash
gobuster dns -d example.com -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt -i -r 1.1.1.1
```

| Option               | Description                                                              |
| -------------------- | ------------------------------------------------------------------------ |
| `-d`, `--domain`     | Target domain.                                                           |
| `-w`, `--wordlist`   | Path to the wordlist.                                                    |
| `-r`, `--resolver`   | Query a custom DNS resolver (`host` or `host:port`); defaults to the system resolver. |
| `-i`, `--show-ips`   | Show the IP addresses of resolved subdomains.                            |
| `-c`, `--show-cname` | Show `CNAME` records (cannot be combined with `-i`).                     |
| `--wildcard`         | Continue even when a wildcard DNS record is detected.                    |
| `-t`, `--threads`    | Number of concurrent threads (default `10`).                             |
| `--timeout`          | DNS resolution timeout (default `1s`).                                   |
| `--delay`            | Delay between requests.                                                  |
| `-o`, `--output`     | Write output to a file.                                                  |
| `-q`, `--quiet`      | Suppress the banner and progress output.                                 |

>[!tip] [`dnsx`](https://github.com/projectdiscovery/dnsx) can also brute-force in a single command using its built-in resolvers: `dnsx -d example.com -w wordlist.txt`.
#### Amass

- Basic DNS brute-force:

```bash
amass enum -active -brute -d example.com -w wordlist.txt
```

- Specify the depth for recursive enumeration:

```bash
amass enum -active -brute -d example.com -w wordlist.txt -max-depth 3
```

- Common `amass enum` options:

| Option         | Description                                                            |
| -------------- | --------------------------------------------------------------------- |
| `-active`      | Attempt zone transfers and certificate name grabs.                    |
| `-addr`        | IP addresses and ranges separated by commas.                          |
| `-alts`        | Enable generation of altered names.                                   |
| `-asn`         | ASNs separated by commas.                                             |
| `-aw`          | Path to a different wordlist file for alterations.                    |
| `-awm`         | Hashcat-style wordlist masks for name alterations.                    |
| `-bl`          | Blacklist of subdomain names that will not be investigated.           |
| `-blf`         | Path to a file with blacklisted subdomains.                           |
| `-brute`       | Execute brute-forcing after searches.                                 |
| `-w`           | Path to a different wordlist file for brute-force.                    |
| `-wm`          | Hashcat-style wordlist masks for brute-force.                         |
| `-cidr`        | CIDRs separated by commas.                                            |
| `-config`      | Path to the YAML configuration file.                                  |
| `-d`           | Domain names separated by commas.                                     |
| `-df`          | Path to a file with root domain names.                                |
| `-dir`         | Path to the directory for output files.                               |
| `-dns-qps`     | Maximum number of DNS queries per second across all resolvers.        |
| `-if`          | Path to a file with data sources to include.                          |
| `-iface`       | Network interface to send traffic through.                            |
| `-log`         | Path to the log file to write errors to.                              |
| `-max-depth`   | Maximum number of subdomain labels to brute-force.                    |
| `-nf`          | Path to a file with already known subdomains.                         |
| `-norecursive` | Turn off recursive brute-forcing.                                     |
| `-o`           | Output file.                                                          |
| `-p`           | Ports separated by commas (default `80`, `443`).                      |
| `-r`           | IP addresses of untrusted DNS resolvers.                              |
| `-rf`          | Path to a file with untrusted DNS resolvers.                          |
| `-rqps`        | Maximum number of DNS queries per second for each untrusted resolver. |
| `-tr`          | IP addresses of trusted DNS resolvers.                                |
| `-trf`         | Path to a file with trusted DNS resolvers.                            |
| `-trqps`       | Maximum number of DNS queries per second for each trusted resolver.   |
| `-timeout`     | Number of minutes to let enumeration run before quitting.             |
| `-v`           | Produce verbose output (status/debug/troubleshooting).                |

>[!note] Amass can be slower at subdomain enumeration than other, more lightweight tools.

### Reverse DNS

- Additional subdomains can often be found by enumerating IP addresses owned by the target and performing reverse DNS lookups.

>[!note] Reverse DNS lookups query **`PTR` (Pointer)** records stored under special **reverse zones** like `in-addr.arpa` (IPv4) and `ip6.arpa` (IPv6).

```bash
dig -x 8.8.8.8
```

>[!example]-
> ```bash
> dig -x 8.8.8.8
> ```
>
> ```bash
> ; <<>> DiG 9.20.24 <<>> -x 8.8.8.8
> ;; global options: +cmd
> ;; Got answer:
> ;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 13830
> ;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1
>
> ;; OPT PSEUDOSECTION:
> ; EDNS: version: 0, flags:; udp: 65494
> ;; QUESTION SECTION:
> ;8.8.8.8.in-addr.arpa.		IN	PTR
>
> ;; ANSWER SECTION:
> 8.8.8.8.in-addr.arpa.	77220	IN	PTR	dns.google.
>
> ;; Query time: 22 msec
> ;; SERVER: 127.0.0.53#53(127.0.0.53) (UDP)
> ;; WHEN: Thu Jul 16 19:43:00 CEST 2026
> ;; MSG SIZE  rcvd: 73
> ```

>[!note] Some online reverse DNS lookup tools
> - [`MxToolBox`](https://mxtoolbox.com/ReverseLookup.aspx)
> - [`DNSChecker`](https://dnschecker.org/reverse-dns.php)
> - [`Hacker Target`](https://hackertarget.com/reverse-dns-lookup/)
> - [`whatsmydns.net`](https://www.whatsmydns.net/reverse-dns-lookup)

>[!note] See [[Querying DNS]].

- For bulk reverse DNS lookups, use [`dnsx`](https://github.com/projectdiscovery/dnsx):

```bash
dnsx -ptr -l ip_addresses.txt
```

- Or analyze the TLS certificate with `tlsx`:

```bash
tlsx -u example.com -so
```

>[!important] `PTR` records are optional and absent from many IP addresses.

>[!info] `PTR` hostnames are not guaranteed to belong to the same organization as the IP address.

### Discovering IP addresses by ASNs

>An **Autonomous System (AS)** is a collection of IP networks operated under a common administrative authority and identified by a unique **Autonomous System Number (ASN)**.

>[!info] ASNs are managed by IANA (Internet Assigned Numbers Authority).

- Large organizations commonly own one or more ASNs that advertise their public IP ranges through the Border Gateway Protocol (BGP). Enumerating these prefixes can reveal Internet-facing infrastructure that isn't directly linked from the organization's primary domain. 
- Once you find the IP block(s) that belong to your target, you can extract subdomains through bulk reverse DNS lookups.

>[!interesting]+ Types of ASNs
>- 16-bit (2-byte) ASNs (`0`–`65,535`)
>- 32-bit (4-byte) ASNs (`0`–`4,294,967,295`)
>---
>- The numbers are written in the form `AS<number>`.

- Information about ASNs can be found on RIR (Regional Internet Registry) websites (ARIN, RIPE NCC, APNIC, LACNIC, AFRINIC), in BGP routing databases, in WHOIS records, and via search engines like Shodan and Censys.

>[!info]- RIRs
> | Acronym  | Name                                                         | Regions                                                           | Website                                    |
> | -------- | ------------------------------------------------------------ | ----------------------------------------------------------------- | ------------------------------------------ |
> | AFRINIC  | The African Network Information Center                       | Africa                                                            | [www.afrinic.net](https://www.afrinic.net) |
> | ARIN     | The American Registry for Internet Numbers                   | Antarctica, Canada, parts of the Caribbean, and the United States | [www.arin.net](https://www.arin.net/)      |
> | APNIC    | The Asia Pacific Network Information Center                  | East Asia, Oceania, South Asia, Southeast Asia                    | [www.apnic.net](https://www.apnic.net)     |
> | LACNIC   | The Latin America and Caribbean Network Information Centre    | Latin America and most of the Caribbean                           | [www.lacnic.net](https://www.lacnic.net/)  |
> | RIPE NCC | Réseaux IP Européens Network Coordination Centre (French)    | Europe, Central Asia, Russia, West Asia                           | [www.ripe.net](https://www.ripe.net/)      |

- To find an ASN associated with a target organization, use `amass intel`:

```bash
amass intel -org "Example Inc."
```

- Or query the hostname directly with `dnsx`:

```bash
echo example.com | dnsx -asn
```

- [`HURRICANE ELECTRIC`](https://bgp.he.net/) provides a specialized (free) search engine for this purpose and often gives more comprehensive, accurate results.

>[!note] For more methods of discovering ASNs, see [`SecurityTrails: ASN Lookup Tools, Strategies and Techniques`](https://securitytrails.com/blog/asn-lookup#autonomous-system-lookup-script).

- Once you have an ASN, retrieve the full IP ranges (`PTR` records) associated with it:

```bash
echo AS<number> | dnsx -silent -resp-only -ptr
```

```bash
amass intel -asn AS<number>
```

```bash
whois AS<number>
```

- Using the [`asn`](https://github.com/nitefood/asn/) tool:

```bash
asn -u 203.0.113.5
```

- Online tools:
	- [`HACKER TARGET`](https://hackertarget.com/as-ip-lookup/) — Search IP ranges by ASN (or vice versa).
	- [`MXTOOLBOX`](https://mxtoolbox.com/SuperTool.aspx?action=asn%3a13335&run=toolpage) — Search CIDR ranges by ASN.
	- [`ASNLOOKUP`](https://asnlookup.com/) — Get information about a specific AS, organization, CIDR range, or IP address.
	- [`DNSCHECKER`](https://dnschecker.org/asn-whois-lookup.php) — `whois` for an ASN and other information about an AS.
	- [`ASRank`](https://asrank.caida.org/asns/6427) — Get information about a specific AS, its rank, and its relationships with other ASes.

>[!note] See also [`HostHunter`](https://github.com/SpiderLabs/HostHunter), which discovers hostnames from IP addresses using OSINT and active reconnaissance.

>[!info]- ASN ranges
> | Range                           | Bits | Description                                       | Reference                                                                                                                                                                                 |
> | ------------------------------- | ---- | ------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
> | `0`                             | 16   | Reserved for RPKI unallocated space invalidation  | [RFC](https://en.wikipedia.org/wiki/RFC_(identifier) "RFC (identifier)") [6483](https://datatracker.ietf.org/doc/html/rfc6483), RFC [7607](https://datatracker.ietf.org/doc/html/rfc7607) |
> | `1`–`23,455`                    | 16   | Public ASNs                                       |                                                                                                                                                                                           |
> | `23,456`                        | 16   | Reserved for AS Pool Transition                   | RFC [6793](https://datatracker.ietf.org/doc/html/rfc6793)                                                                                                                                 |
> | `23,457`–`64,495`               | 16   | Public ASNs                                       |                                                                                                                                                                                           |
> | `64,496`–`64,511`               | 16   | Reserved for use in documentation and sample code | RFC [5398](https://datatracker.ietf.org/doc/html/rfc5398)                                                                                                                                 |
> | `64,512`–`65,534`               | 16   | Reserved for private use                          | RFC [1930](https://datatracker.ietf.org/doc/html/rfc1930), RFC [6996](https://datatracker.ietf.org/doc/html/rfc6996)                                                                      |
> | `65,535`                        | 16   | Reserved                                          | RFC [7300](https://datatracker.ietf.org/doc/html/rfc7300)                                                                                                                                 |
> | `65,536`–`65,551`               | 32   | Reserved for use in documentation and sample code | RFC [5398](https://datatracker.ietf.org/doc/html/rfc5398), RFC [6793](https://datatracker.ietf.org/doc/html/rfc6793)                                                                      |
> | `65,552`–`131,071`              | 32   | Reserved                                          |                                                                                                                                                                                           |
> | `131,072`–`4,199,999,999`       | 32   | Public 32-bit ASNs                                |                                                                                                                                                                                           |
> | `4,200,000,000`–`4,294,967,294` | 32   | Reserved for private use                          | RFC [6996](https://datatracker.ietf.org/doc/html/rfc6996)                                                                                                                                 |
> | `4,294,967,295`                 | 32   | Reserved                                          | RFC [7300](https://datatracker.ietf.org/doc/html/rfc7300)                                                                                                                                 |

### DNSSEC zone walking

>**DNSSEC (Domain Name System Security Extensions)** extends DNS with cryptographic signatures that provide authenticity and integrity for DNS records.

- If the target uses **`NSEC` records** for a DNSSEC-signed zone, negative responses include an `NSEC` record that states the queried hostname doesn't exist and reveals the **next valid hostname in canonical order**. This creates a chain that links every name in the zone.
- By repeatedly querying for non-existent names and following each `NSEC` record to the next hostname, you can **walk the entire zone** and obtain all its hostnames without brute-forcing them individually. This technique is known as **DNSSEC zone walking**.
- It only works when:
	- DNSSEC is enabled, and
	- the zone uses **`NSEC` records** rather than **`NSEC3`**.
- Check whether the target uses DNSSEC by querying `DNSKEY` (or other DNSSEC records: `RRSIG`, `DS`, `NSEC`, `NSEC3`):

```bash
dig example.com DNSKEY +short
```

- Perform DNSSEC zone walking:

```bash
dig example.com NSEC
```

- Because most deployments either disable DNSSEC or use `NSEC3`, successful zone walking is relatively uncommon. Still, it remains valuable where applicable because it can reveal complete zone contents with relatively few queries.

>[!note]+ As of 2026, DNSSEC adoption is still spotty. See [`DNSSEC World Map — APNIC`](https://stats.labs.apnic.net/dnssec) for validation rates by country (with a map).
>![[dnssec_adoption_map.png]]

>[!note] You can also use the [`Verisign DNSSEC Analyzer`](https://dnssec-analyzer.verisignlabs.com/) to check whether a zone uses DNSSEC.

## References and further reading

- [`Wildcard DNS record — Wikipedia`](https://en.wikipedia.org/wiki/Wildcard_DNS_record)
- [`How does DNSSEC work? — Cloudflare`](https://www.cloudflare.com/learning/dns/dnssec/how-dnssec-works/)
- [`Domain Name System Security Extensions — Wikipedia`](https://en.wikipedia.org/wiki/Domain_Name_System_Security_Extensions)
- [`List of DNS record types — Wikipedia`](https://en.wikipedia.org/wiki/List_of_DNS_record_types)
- [`Zone Walking (Zone Enumeration via DNSSEC NSEC Records) — DomainTools`](https://www.domaintools.com/resources/blog/zone-walking-zone-enumeration-via-dnssec-nsec-records/)
- [`Subdomain Enumeration — 0xffsec`](https://0xffsec.com/handbook/information-gathering/subdomain-enumeration/#dns-aggregators)
- [`Subdomain enumeration tools and techniques — Ceeyu`](https://www.ceeyu.io/resources/blog/subdomain-enumeration-tools-and-techniques)
- [`Subdomains Enumeration Cheat Sheet — PentesterLand`](https://pentester.land/blog/subdomains-enumeration-cheatsheet/)

## Appendix A: Wildcard DNS records

>A **wildcard DNS record** matches queries for **non-existent hostnames** within a zone. Instead of returning `NXDOMAIN`, the DNS server returns a valid response for almost any queried name.

- Such records use an asterisk (`*`) as the leftmost label of the domain name:

```bash
*.example.com.   86400 IN NS ns1.example.com.
```

>[!example] If `*.example.com` resolves to `203.0.113.5`, then `random.example.com`, `nothingthere.example.com`, and so on all resolve to that IP — even though none of them actually exist.

- Wildcard records therefore produce **false positives** during brute-force enumeration.
- The first indicator of a wildcard domain is an unusually large number of valid subdomains.
- The simplest way to confirm a wildcard is to query a subdomain you're sure doesn't exist:

```bash
dig fc9518847a.example.com A
```

- Query a random 10-character subdomain:

```bash
dig "$(tr -dc 'a-z0-9' < /dev/urandom | head -c 10).example.com" A
```

- If the query returns a valid record instead of `NXDOMAIN`, the zone is likely using wildcard DNS.

>[!example]+
> ```bash
> dig "$(tr -dc 'a-z0-9' < /dev/urandom | head -c 10).example.com" A
> ```
>
> ```bash
> ; <<>> DiG 9.20.24 <<>> 9rymh2rak0.example.com A
> ;; global options: +cmd
> ;; Got answer:
> ;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 4845
> ;; flags: qr rd ra; QUERY: 1, ANSWER: 0, AUTHORITY: 1, ADDITIONAL: 1
>
> ;; OPT PSEUDOSECTION:
> ; EDNS: version: 0, flags:; udp: 65494
> ;; QUESTION SECTION:
> ;9rymh2rak0.example.com.		IN	A
>
> ;; AUTHORITY SECTION:
> example.com.		1800	IN	SOA	elliott.ns.cloudflare.com. dns.cloudflare.com. 2407636105 10000 2400 604800 1800
>
> ;; Query time: 35 msec
> ;; SERVER: 127.0.0.53#53(127.0.0.53) (UDP)
> ;; WHEN: Thu Jul 16 15:42:34 CEST 2026
> ;; MSG SIZE  rcvd: 113
> ```

> [!important] Some wildcard configurations respond only to specific hostnames and don't answer queries for `*.example.com` directly. Detection should therefore always use randomly generated hostnames.

- Most modern enumeration tools automatically detect and filter wildcard responses.
