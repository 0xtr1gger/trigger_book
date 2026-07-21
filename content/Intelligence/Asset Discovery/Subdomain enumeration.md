---
created: 2026-07-15
tags:
  - recon
  - asset_discovery
status: substantial
---

>[!note] See also [[Virtual host enumeration|Virtual host enumeration]].
## Passive subdomain enumeration

>**Passive subdomain enumeration** is the process of discovering subdomains by using publicly accessible information and third-party services, **without directly interacting with the target servers**. 

>[!important] Subdomains obtained using passive methods must be validated. The results might be outdated. See[[#subdoma]].
### Third-party datasets

- Passive subdomain enumeration often relies on **third-party datasets** of asset intelligence gathered by external organizations.
- Rather than interacting with the target directly, you can query these existing datasets to discover subdomains and other assets.

- Third-party datasets aggregate information from many independent sources, including:
	- Historical DNS resolution records (passive DNS)
	- Internet-wide scanning
	- WHOIS and registration data
	- Web crawling
	- Malware telemetry
	- Security research
	- Publicly available OSINT

- Since these datasets are maintained independently, each provider has different coverage, update frequency, and data retention policies. So querying multiple providers typically yields more complete results than relying on a single source.

- Common providers include:

	- [`Shodan`](https://www.shodan.io/) 
	- [`Censys`](https://censys.com/)
	- [`BinaryEdge`](https://www.binaryedge.io/)
	- [`VirusTotal`](https://www.virustotal.com/gui/home/upload)
	- [`SecurityTails`](https://securitytrails.com/)
	- [`DNSDumpster`](https://dnsdumpster.com/)
	- [`Netlas`](https://netlas.io/)
	- [`FullHunt`](https://fullhunt.io/)
	- [`Chaos`](https://chaos.projectdiscovery.io/) (`ProjectDiscovery`)
	- [`WhoisXMLAPI`](https://www.whoisxmlapi.com/)
- More than [90](https://gist.github.com/sidxparab/22c54fd0b64492b6ae3224db8c706228) public and commercial providers are available, and each exposes different datasets and APIs.

- Rather than querying each service individually, you can use tools like [`Amass`](https://github.com/owasp-amass/amass), [`Subfinder`](https://github.com/projectdiscovery/subfinder), [`Assetfinder`](https://github.com/tomnomnom/assetfinder), and [`Findomain`](https://github.com/Findomain/Findomain) — they automate requests to many providers and merge the results into a single output.

>[!note] Some sources are publicly accessible, but many require API keys. In many cases, you can get keys for free (though often with limits), others are paid-only.

#### Amass passive mode

>[`Amass`](https://github.com/owasp-amass/amass) is an attack surface discovery tool that supports both passive and active reconnaissance. 

- In passive mode, Amass enumerates subdomains by querying third-part data providers — without interacting directly with the target's infrastructure.

>[!note]+ Installation
> 
> - With `go install`:
> 
> ```bash
> CGO_ENABLED=0 go install -v github.com/owasp-amass/amass/v5/cmd/amass@main
> ```
> 
>See [`Getting Started — Amass Docs`](https://owasp-amass.github.io/docs/#getting-started).

```bash
amass enum -h
```

- List all supported data sources:

```bash
amass enum -list
```
##### Configuration

- API keys are configured in:

```bash
~/.config/amass/config.ini
```

>[!note] [`Amass Data Sources Configuration — Amass Docs`](https://owasp-amass.github.io/docs/configuration/data_sources/).

##### Usage 

>[!note] These commands perform **passive enumeration only**. No active probes or DNS resolution.

- Enumerate subdomains of a single domain:

```bash
amass enum -passive -d example.com
```

- Enumerate for multiple domains, then save results into a file:

```bash
amass enum -passive -d example1.com -d example2.com -o results.txt
```

| Option     | Description                                                    |
| ---------- | -------------------------------------------------------------- |
| `-passive` | Passive enumeration only (no active probes or DNS resolution). |
| `-include` | Include specific data sources (comma-separated).               |
| `-exclude` | Exclude specific data sources (comma-separated).               |
| `-o`       | Write output to a file.                                        |
| `-timeout` | Enumeration timeout (minutes).                                 |
| `-v`       | Verbose output.                                                |

#### Subfinder

>[`Subfinder`](https://github.com/projectdiscovery/subfinder) is a passive subdomain enumeration tool that discovers subdomains by querying third-party data providers. 

>[!note] Subfinder does not interact directly with the target unless active verification is explicitly enabled.

>[!note]+ Installation
> - `go install`:
> 
> ```bash
> go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
> # requires go1.21 or later
> ```
>See [`Installing Subfinder — ProjectDiscovery`](https://docs.projectdiscovery.io/opensource/subfinder/install).

```bash
subfinder -h
```

- Without any additional configuration, Subfinder uses only publicly available sources. 

- List all supported data sources:

```bash
subfinder -ls
```

##### Configuration

- API keys are configured in:

```bash
~/.config/subfinder/provider-config.yaml
```

- Format:

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

- Use all configured providers during enumeration:

```bash
subfinder -d example.com -all
```

- Use all available sources for enumeration:

```bash
subfinder -d target.com -v -all
```

- Specify multiple target domains:

```bash
subfinder -d example1.com,example2.com -o results.txt --all
```

- Specify a file with target domains:

```bash
subfinder -dL target_domains.txt --all
```

- Use specific sources for enumeration:

```bash
subfinder -d target.com -s virustotal,crtsh,github
```

| Option                    | Description                                                                                   |
| ------------------------- | --------------------------------------------------------------------------------------------- |
| `-d`                      | Domains to find subdomains for.                                                               |
| `-dL`                     | File with target domains.                                                                     |
| `-s`, `-sources`          | Use specific providers.                                                                       |
| `-recursive`              | Use only sources that can handle subdomains recursively.                                      |
| `-all`                    | Use all sources for enumeration (slow).                                                       |
| `-es`, `-exclude-sources` | Sources to exclude from enumeration.                                                          |
| `-m`, `-match`            | Subdomain or list of subdomain to match (file or a comma-separated separated list).           |
| `-f`, `-filter`           | Subdomain or list of subdomain to filter (file or a comma-separated list).                    |
| `-rl`, `-rate-limit`      | Maximum number of HTTP requests to send per second.                                           |
| `-t`                      | Number of concurrent goroutines for resolving (only with `-active`), default is `10`.         |
| `-up`, `-update`          | Update `subfinder` to latest version.                                                         |
| `-o`, `-output`           | Output file.                                                                                  |
| `-oJ`, `-json`            | Write output in JSON format.                                                                  |
| `-oD`, `-output-dir`      | Directory to write output to (`-dL` only).                                                    |
| `-cs`, `-collect-sources` | Include all sources in the output.                                                            |
| `-oI`, `-ip`              | Include host IP in output (`-active` only).                                                   |
| `-pc`, `-provider-config` | Provider configuration file, default `/home/username/.config/subfinder/provider-config.yaml`. |
| `-nW`, `-active`          | Display active subdomains only.                                                               |
| `-proxy`                  | HTTP proxy to use for HTTP requests.                                                          |
| `-ei`, `-exclude-ip`      | Exclude IP addresses from the list of domains.                                                |
| `-v`                      | Verbose output.                                                                               |
| `-ls`, `-list-sources`    | List supported providers.                                                                     |
| `-silent`                 | Show only subdomains in output.                                                               |
##### Sources

- List all supported services:

```bash
subfinder -ls
```

>[!note]- Sources that don't require API keys to work
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

>[!note]- Sources that do require API keys to work
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

- List of all sources supported by `Subfinder`:

| Name             | URL                                                   |
| ---------------- | ----------------------------------------------------- |
| `BeVigil`        | `https://bevigil.com/osint-api`                       |
| `BinaryEdge`     | `https://binaryedge.io`                               |
| `BufferOver`     | `https://tls.bufferover.run`                          |
| `BuiltWith`      | `https://api.builtwith.com/domain-api`                |
| `C99`            | `https://api.c99.nl/`                                 |
| `Censys`         | `https://censys.io`                                   |
| `CertSpotter`    | `https://sslmate.com/certspotter/api/`                |
| `Chaos`          | `https://chaos.projectdiscovery.io`                   |
| `Chinaz`         | `http://my.chinaz.com/ChinazAPI/DataCenter/MyDataApi` |
| `DNSDB`          | `https://api.dnsdb.info`                              |
| `dnsrepo`        | `https://dnsrepo.noc.org`                             |
| `Facebook`       | `https://developers.facebook.com`                     |
| `Fofa`           | `https://fofa.info/static_pages/api_help`             |
| `FullHunt`       | `https://fullhunt.io`                                 |
| `GitHub`         | `https://github.com`                                  |
| `Hunter`         | `https://hunter.qianxin.com/`                         |
| `Intelx`         | `https://intelx.io`                                   |
| `PassiveTotal`   | `http://passivetotal.org`                             |
| `quake`          | `https://quake.360.cn`                                |
| `Robtex`         | `https://www.robtex.com/api/`                         |
| `SecurityTrails` | `http://securitytrails.com`                           |
| `Shodan`         | `https://shodan.io`                                   |
| `ThreatBook`     | `https://x.threatbook.cn/en`                          |
| `VirusTotal`     | `https://www.virustotal.com`                          |
| `WhoisXML`       | `https://whoisxmlapi.com/`                            |
| `ZoomEye`        | `https://www.zoomeye.org`                             |
| `ZoomEye`        | `https://api.zoomeye.org`                             |

### Certificate Transparency logs

>**[Certificate Transparency (CT)](https://en.wikipedia.org/wiki/Certificate_Transparency)** is an open framework and Internet security standard ([`RFC 6962`](https://datatracker.ietf.org/doc/html/rfc6962)) designed for monitoring and auditing issuance of digital certificates.

- CT **requires** publicly trusted Certificate Authorities (CAs) to add issued TLS certificates to **publicly accessible, append-only CT logs**. 
- Each record must include the full domain and **all subdomains** the certificate is issued for.
- This makes CT logs one of the most reliable sources for passive subdomain enumeration. However, it only reveals domains that are currently present or were present in public certificates (you won't find domains without certificates).

>[!note] Newly issued certificates may take several minutes to appear in the logs. 

- The primary source of CT logs is **[`crt.sh`](https://crt.sh/)**. It provides an easy-to-use web interface and can return results in JSON format.
- To query the logs using `curl` and parse them using `jq`:

```bash
curl -s "https://crt.sh/?q=%25.example.com&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u
```

- Subfinder can also look into CT logs:

```bash
subfinder -d example.com -sources crtsh -o subfinder_ct.txt
```

- Using [`tlsx`](https://github.com/projectdiscovery/tlsx):

```bash
tlsx -u example.com -ctl -silent
```

 >[!note] There's also [`Censys.io`](https://search.censys.io/), which is might be a bit more up-to-date than `crt.sh` in some cases, but it doesn't provide access to all CT logs, and it also requires registration. 

>[!note]+ Online CT logs checkers
> - [`Qualys`](https://www.ssllabs.com/ssltest)
> - [`SSLmarket`](https://www.sslmarket.com/ssl-verification-tool/?domain=github.com)
> - [`namecheap`](https://decoder.link/sslchecker/)
### SAN (Subject Alternate Name)

>**SAN (Subject Alternate Name)** is an extension to X.509 certificates that specifies additional domain names or IP address the certificate protects aside for the Common Name (CN). 

>[!note] [`RFC 2818`](https://datatracker.ietf.org/doc/html/rfc2818) specifies SAN as the preferred method of adding DNS names to certificates.

- Use OpenSSL to extract SAN subdomains from a certificate:

With SAN, a single certificate can cover multiple domains and subdomains of an organization. This means you can examine the SAN field of certificates to discover related subdomains. 
This can uncover subdomains that are not publicly advertised elsewhere. 

>[!example] For example, a certificate for `www.example.com` may include SAN entries for `dev.example.com`, `test.example.com`, etc.

- You can use OpenSSL tool to extract domain names specified in the SAN field of a TLS certificate:

```bash
openssl s_client -connect example.com:443 2>/dev/null | openssl x509 -noout -ext subjectAltName | grep -oP '(?<=DNS:|IP Address:)[^,]+'|sort -uV
```

>[!note]- Command breakdown
> - `openssl s_client -connect example.com:443` — Retrieves the digital certificate of `example.com` by connecting to it over HTTP (port `443`).
> - `2>/dev/null` — Suppresses error messages.
> - `openssl x509 -noout -ext subjectAltName` — Prints only the SAN field.
> - `grep -oP '(?<=DNS:|IP Address:)[^,]+'|sort -uV` — Arranges subdomains into a nice column. 

>[!example]+
> 
> ```bash
> openssl s_client -connect wikimedia.org:443 2>/dev/null | openssl x509 -noout -ext subjectAltName | grep -oP '(?<=DNS:|IP Address:)[^,]+'|sort -uV
> ```
> 
>![[san_openssl_wikimedia.png]]

- Or you can use [`san_subdomain_enum`](https://github.com/appsecco/the-art-of-subdomain-enumeration/blob/master/san_subdomain_enum.py) (a Python script):

```bash
python ./san_subdomain_enum.py domain.com
```
#### `tlsx`

>[`tlsx`](https://github.com/projectdiscovery/tlsx) is a TLS grabber mainly designed for information gathering.

- `tlsx` can retrieve subdomains from both CT logs and SAN fields in TLS certificates.

>[!note]+ Installation 
>```bash
>go install github.com/projectdiscovery/tlsx/cmd/tlsx@latest
>```

```bash
tlsx -h
```

- Find all subdomains of `example.com` ever logged in public CT logs:

```bash
tlsx -u example.com -ctl -silent
```

- Extract subdomains listed in the SAN field of a certificate:

```bash
tlsx -u api.example.com -san -silent
```

- Reverse IP address lookup:

```bash
echo "302.113.0.12" | tlsx -l - -cn -silent
```

| Option    | Description       |
| --------- | ----------------- |
| `-u`      | Target host       |
| `-san`    | Print SAN entries |
| `-ctl`    | Stream CT logs    |
| `-cn`     | Print Common Name |
| `-silent` | Silent output     |
| `-json`   | JSON output       |
| `-o`      | Output file       |
### Search engines

- Search engines can reveal publicly accessible subdomains that have been indexed by web crawlers. 
- This technique is particularly useful for identifying legacy applications, forgotten virtual hosts, and development environments exposed to the Internet.

- Most search engines support advanced search operators that restrict results to specific domains:
	- [`Search Operators | Brave Search`](https://search.brave.com/help/operators)
	- [`Search Operators | DuckDuckGo Search`](https://help.duckduckgo.com/duckduckgo-help-pages/results/syntax/)
	- [`Search Operators | Bing`](https://help.bing.microsoft.com/#apex/bing/en-us/10001/-1)
	- [`Search Opeartors | Google`](https://docs.google.com/document/d/1ydVaJJeL1EYbWtlfj9TPfBTE5IBADkQfZrQaBZxqXGs/edit?tab=t.0)

>[!note] See [[Search engine operators]].
	
- The methodology is simple: you make a search query, extract URLs from the results, strip unnecessary parts to get the domains, and then remove duplicates.
- The `site:` operator filters results to a specific domain, and it's supported by most engines. Use it with a wildcard to match subdomains:

```PowerShell
site:*.example.com 
```

- To exclude the results from a specific subdomain:

```PowerShell
site:*.example.com -site:www.example.com
```

>[!note]+ Google Dorks collections
> 
> - [`7000_google_dork_list.txt`](https://github.com/aleedhillon/7000-Google-Dork-List/blob/master/7000_google_dork_list.txt)
> - [`1000 Google Dorks List`](https://gbhackers.com/latest-google-dorks-list/)

- Tools like [`GoogleEnum`](https://github.com/psjs97/GoogleEnum) and [`sd-goo`](https://github.com/darklotuskdb/sd-goo) can automate the process.

> [!example]+ Example: enumerating subdomains using `GoogleEnum`
> 
> ```bash
> python3 google_enum -d example.com -o results.txt
> ```
### Web archives

- Archived pages often reference historical subdomains, legacy applications, retired API endpoints, deprecated hostnames. Many of these hosts are no longer indexed by search engines but may still resolve.
	- [`Internet Archive`](https://archive.org/)
	- [`Wayback Machine`](https://web.archive.org/)
	- [`Archive.today`](https://archive.ph/)
- To enumerate subdomains, you pull all URLs from the archived copies under the target domain and its subdomains, domain names, and remove duplicates. 
- Querying web archives can be automated using:
	- [`waybackurls`](https://github.com/tomnomnom/waybackurls) — Retrieves URLs from the Wayback Machine for a list of domains.
	- [`waymore`](https://github.com/xnl-h4ck3r/waymore) — Similar to `waybackurls`, but fetches URLs not only from the Wayback Machine, but also from Common Crawl, Alien Vault OTX, URLScan, and Virus Total.
	- [`gau`](https://github.com/lc/gau) — Retrieves URLs from AlienVault's [Open Threat Exchange](https://otx.alienvault.com), the Wayback Machine, Common Crawl, and URLScan.
	- [`paramspider`](https://github.com/devanshbatham/ParamSpider) — Retrieves URLs from the Wayback Machine for a list of domains (originally designed to collect interesting URL parameters for bug hunt).

>[!example]+
>Retrieve all archived pages under a given domain with `waybackurls`:
> 
> ```bash
> echo example.com | waybackurls > output.txt
> ```

- To extract domain names from the URLs, you can use [`unfurl`](https://github.com/tomnomnom/unfurl) (it can also remove duplicates automatically):

```bash
cat urls.txt | unfurl --unique domains
```
## Active subdomain enumeration

>**Active subdomain enumeration** is the process of discovering subdomains through **direct interaction with the target infrastructure**.

>[!warning] Active techniques generate traffic directed at the target and therefore may be detected, logged, or rate-limited.

>[!note] Other notable tools for working with web archives
> 
> - [`waybackrobots.py`](https://gist.github.com/mhmdiaa/2742c5e147d49a804b408bfed3d32d07)
> 	- A script that automates search for archived `robots.txt` files.
> - [`waybackpack`](https://github.com/jsvine/waybackpack)
> 	- A command-line tool that allows to download the entire Wayback Machine archive for a given URL.
### DNS brute-force

- DNS brute-force works by generating candidate hostnames from a wordlist and querying the target's authoritative DNS servers to determine whether each hostname exists.
- If a DNS record exists, the hostname is considered valid; otherwise the query returns a negative response like `NXDOMAIN`.

>[!note] Brute-force is often the only way to discover subdomains that:
> - have never appeared in Certificate Transparency logs,
> - are absent from historical DNS datasets,
> - are not indexed by search engines,
> - are not referenced anywhere publicly.

- The effectiveness of such enumeration depends primarily on:
	- the quality of the wordlist,
	- wildcard DNS handling,
	- resolver quality,
	- query throughput.

- Several tools implement DNS brute-force using different approaches:
	- [`PureDNS`](https://github.com/d3mondev/puredns) — High-performance DNS brute-force tool; accurately filters out wildcards and can be used for validating enumeration results (uses `massdns`).
	- [`massdns`](https://github.com/blechschmidt/massdns) — Extremely fast DNS resolver; used as the backend for many enumeration tools.
	- [`Amass`](https://github.com/owasp-amass/amass) — Attack surface mapping tool; among other techniques, supports (recursive) DNS brute-force.
	- [`gobuster`](https://github.com/OJ/gobuster) — Lightweight brute-force tool, can be used for subdomain enumeration; suitable for smaller engagements.

>[!tip] For large engagements, **PureDNS** is generally the preferred choice because it combines high query throughput with automatic wildcard filtering and validation against trusted resolvers. 

>[!note] See [[#Appendix A Wildcard DNS records]].

>[!important] This method is also used as a final step to **validate subdomains obtained with other passive and active enumeration techniques**.

#### PureDNS

>[`PureDNS`](https://github.com/d3mondev/puredns) is a designed for large-scale DNS brute-force; it can resolve **millions** of queries in minutes.

- Under the hood, `PureDNS` uses [`massdns`](https://github.com/blechschmidt/massdns) — a powerful stub resolver that queries multiple public DNS servers in parallel.

>[!warning] PureDNS can crush your router ☀️.

>[!note]- Installation
>
> 
> - PureDNS requires `massdns` to work, install it first:
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
>- Then install PureDNS itself:
> 
> ```bash
> go install github.com/d3mondev/puredns/v2@latest
> ```
>See  [`Installation — PureDNS`](https://github.com/d3mondev/puredns#installation).

- Basic DNS brute-force:

```bash
puredns bruteforce wordlist.txt example.com -r resolvers.txt
```

- This command resolves each candidate subdomains from `wordlist.txt` against public resolves listed in `resolvers.txt`, and outputs valid subdomains.

>[!note] See [[#Obtaining up-to-date resolver lists]].

>[!interesting]+ PureDNS workflow
> 1. Before querying anything, PureDNS removes domains with invalid characters (not in `[a-z0-9.-]`) and duplicates.
> 2. It then uses `massdns` to query public DNS resolvers from the resolver list.
> 3. Results from `massdns` are then validated against trusted resolvers like Cloudflare (`1.1.1.1`) and Google (`8.8.8.8`, `8.8.4.4`). If a result from `massdns` doesn't match what the trusted resolvers return, it's discarded.

- For more control over performance and accuracy:

```bash
puredns bruteforce wordlist.txt example.com --rate-limit 500 --rate-limit-trusted 500 -r resolvers.txt --wildcard-batch 10000
```

- `--rate-limit` controls how many queries per second are sent to public resolvers through `massdns`.
- `--rate-limit-trusted` controls query rate against your trusted resolvers (e.g., Cloudflare, Google).
- `--wildcard-batch` specifies the size of batches for wildcard filtering. Rather than checking each result individually against trusted resolvers (which would be slow), PureDNS groups results into batches and checks them together. Larger batches are faster but use more memory; smaller batches might yield more accurate results.
- `--threads` controls the number of concurrent resolver queries. The optimal value depends on your network capacity and your target's DNS infrastructure.

##### Obtaining up-to-date resolver lists

PureDNS requires two wordlists: one of candidate subdomains and another of **public DNS resolvers**.

- Public DNS resolvers constantly change — servers go down, new ones appear, and existing ones become misconfigured. Each query to a dead server will need to timeout (this is UDP, after all), so a stale or poorly maintained list of resolvers will slow down enumeration dramatically. 
- To check reliability, you can compare a resolver’s responses to those from trusted resolvers, such as Cloudflare (`1.1.1.1`) and Google (`8.8.8.8`). If the results are different or the server is not responding, it should be removed from the list.

- One of the most reliable resolver lists is [`Trickest list of DNS resolvers`](https://github.com/trickest/resolvers), **updated daily**. It aggregates efforts from open source contributors like [`proabiral`](https://github.com/proabiral/Fresh-Resolvers) and [`janmasarik`](https://github.com/janmasarik/resolvers) and validates resolvers using [`dnsvalidator`](https://github.com/vortexau/dnsvalidator).

```bash
curl -o resolvers.txt https://raw.githubusercontent.com/trickest/resolvers/main/resolvers.txt
```

#### Amass

- Basic DNS brute-force:

```bash
amass enum -active -brute -d example.com -w wordlist.txt
```

- Specify depth level for recursive enumeration:

```bash
amass enum -active -brute -d example.com -w wordlist.txt -max-depth 3
```

Here's a summary of common `enum` options:

| option         | description                                                           |
| -------------- | --------------------------------------------------------------------- |
| `-active`      | Attempt zone transfers and certificate name grabs.                    |
| `-addr`        | IP addresses and ranges separated by commas.                          |
| `-alts`        | Enable generation of altered names.                                   |
| `-asn`         | ASNs separated by commas.                                             |
| `-aw`          | Path to a different wordlist file for alternations.                   |
| `-awm`         | Hashcat-style wordlist masks for name alterations.                    |
| `-bl`          | Blacklist of subdomains names what will not be investigated.          |
| `-blf`         | Path to a file with blacklisted subdomains.                           |
| `-brute`       | Execute brute-forcing after searches.                                 |
| `-w`           | Path to a different wordlist file for brute-force.                    |
| `-wm`          | Hashcat-style wordlist masks for brute-force.                         |
| `-cidr`        | CIDRs separated by commas.                                            |
| `-config`      | Path to the YAML configuration file.                                  |
| `-d`           | Domain names separated by commas.                                     |
| `-df`          | Path to a file with root domain names.                                |
| `-dir`         | Path to the directory with output files.                              |
| `-dns-qps`     | Maximum number of DNS queries per second across all resolvers.        |
| `-if`          | Path to a file with data sources to include.                          |
| `-iface`       | Network interface to send traffic through.                            |
| `-log`         | Path to the log file to write errors to.                              |
| `-max-depth`   | Maximum number of subdomain labels to brute-force.                    |
| `-nf`          | Path to a file with already known subdomains.                         |
| `-norecursive` | Turn off recursive brute-forcing.                                     |
| `-o`           | Output file.                                                          |
| `-p`           | Ports separated by commas (default: `80`, `443`).                     |
| `-r`           | IP addresses of untrusted DNS resolvers.                              |
| `-rf`          | Path to a file with untrusted DNS resolvers.                          |
| `-rqps`        | Maximum number of DNS queries per second for each untrusted resolver. |
| `-tr`          | IP addresses of trusted DNS resolvers.                                |
| `-trf`         | Path to a file with trusted DNS resolvers.                            |
| `-trqps`       | Maximum number of DNS queries per second for each trusted resolver.   |
| `-timeout`     | Number of minutes to let enumeration run before quitting,             |
| `-v`           | Verbose output (status/debug/troubleshooting).                        |

>[!note] Amass can be a bit slower in subdomain enumeration than other, more lightweight tools.


#### Wordlists

- [`2m-subdomains.txt`](https://wordlists-cdn.assetnote.io/data/manual/2m-subdomains.txt) — 2 million+ subdomains from [Assetnote](https://wordlists.assetnote.io/), generated from the GitHub dataset on BigQuery.
- [`best-dns-wordlist.txt`](https://wordlists-cdn.assetnote.io/data/manual/best-dns-wordlist.txt) — 9 million+ subdomains from Assetnote. Manually generated, one of the most comprehensive.
- [`n0kovo_subdomains`](https://github.com/n0kovo/n0kovo_subdomains/blob/main/n0kovo_subdomains_huge.txt) — 3 million+ subdomains created by [N0kovo](https://github.com/n0kovo); see [this blog](https://n0kovo.github.io/posts/subdomain-enumeration-creating-a-highly-efficient-wordlist-by-scanning-the-entire-internet).
- [`six2dez_small_wordlist`](https://gist.githubusercontent.com/six2dez/a307a04a222fab5a57466c51e1569acf/raw) — 102k subdomains created by [`six2dez`](https://github.com/six2dez).

SecLists:
- [`Discovery/DNS/subdomains-top1million-5000.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/DNS/subdomains-top1million-5000.txt)
- [`Discovery/DNS/subdomains-top1million-20000.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/DNS/subdomains-top1million-20000.txt)
- [`Discovery/DNS/subdomains-top1million-110000.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/DNS/subdomains-top1million-110000.txt)
- [`Discovery/DNS/n0kovo_subdomains.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/DNS/n0kovo_subdomains.txt)
- [`Discovery/Web-Content/common.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/common.txt)

```bash
curl -o ./subdomains-20k.txt https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-110000.txt
```

- Wordlist collections:

| Collection                                                                        | Description                                                                                                 |
| --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| [`danielmiessler/SecLists`](https://github.com/danielmiessler/SecLists)           | A collection of multiple types of wordlists for fuzzing, enumeration, and vulnerability testing.            |
| [`Assetnote`](https://wordlists.assetnote.io/)                                    | A collection of wordlists for various purposes.                                                             |
| [`Karanxa/Bug-Bounty-Wordlists`](https://github.com/Karanxa/Bug-Bounty-Wordlists) | A repository with a wide variety of wordlists for testing and enumeration.                                  |
| [`xajkep/wordlists`](https://github.com/xajkep/wordlists?tab=readme-ov-file)      | A collection of wordlists of various kinds + language dictionaries (English, French, Spanish, Irish, etc.). |

>[!tip] You can also use [`CeWL`](https://github.com/digininja/CeWL) to generate custom wordlists based on information scraped from the target website.  
##### Permutation-based enumeration

- DNS brute-force relies on predefined wordlists, but many subdomains follow naming conventions unique to an organization. Rather than guessing completely new names, **permutation-based enumeration** generates additional candidates from hostnames that have already been discovered.
- This often helps discover subdomains domains that would not appear in generic wordlists.

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
> 

>[!note] Permutation generation tools only create wordlists for enumeration, but not actually send any active or passive probes.

- To generate permutation wordlists from already-discovered subdomains, you can use [`alertx`](https://github.com/projectdiscovery/alterx):

```bash
alterx -l subdomains.txt
```

- To add more custom words:

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

>[!note]- Installation
>```bash
>go install github.com/projectdiscovery/alterx/cmd/alterx@latest
>```
> See [`Installation — alterx`](https://github.com/projectdiscovery/alterx).
### Reverse DNS

- Additional subdomains can often be discovered by enumerating IP addresses owned by the target and performing reverse DNS lookups.

>[!note] Reverse DNS lookup is performed by querying **`PTR` (Pointer)** DNS records stored under special **reverse zones** like `in-addr.arpa` for IPv4 and `ip4.arpa` for IPv6.

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

>[!note] Some online tools for reverse DNS lookup
> - [`MxToolBox`](https://mxtoolbox.com/ReverseLookup.aspx)
> - [`DNSChecker`](https://dnschecker.org/reverse-dns.php)
> - [`Hacker Targer`](https://hackertarget.com/reverse-dns-lookup/)
> - [`whatsmydns.net`](https://www.whatsmydns.net/reverse-dns-lookup)

>[!note] See [[Querying DNS information]].

- To perform bulk reverse DNS lookup, you can use, for example, [`dnsx`](https://github.com/projectdiscovery/dnsx):

```bash
dnsx -ptr -l ip_addressees.txt
```

- Or analyze the TLS certificate using `tlsx`:

```bash
tlsx -u example.com -so
```

>[!important] `PTR` records are optional and are absent from many IP addresses. 

>[!info] `PTR` hostnames are not guaranteed to belong to the same organization as the IP address.

### Discovering IP addresses by ASNs

>An **Autonomous System (AS)** is a collection of IP networks operated under a common administrative authority and identified by a unique **Autonomous System Number (ASN)**.

>[!info] ASNs are managed by IANA (Internet Assigned Numbers Authority). 

- Large organizations commonly own one or more ASNs that advertise their public IP address ranges through the Border Gateway Protocol (BGP). Enumerating these prefixes can reveal Internet-facing infrastructure that is not directly linked from the organization's primary domain.

>[!note]+ Types of ASNs
>- 16 bit (2 bytes) ASNs (`0`-`65,535`)
>- 32 bit (4 bytes) ASNs (`0`-`4,294,967,295`) 
>
>The numbers are written in the form `AS<number>`.

- Information about ASNs can be found on RIR (Regional Internet Registries) websites (ARIN, RIPE NCC, APNIC, LACNIC, ARFINIC), BGP routing databases, WHOIS records, and internet search engines like Shodan and Censys.

>[!info]- RIRs
> | Acronym  | Name                                                         | Rgions                                                            | Website                                    |
> | -------- | ------------------------------------------------------------ | ----------------------------------------------------------------- | ------------------------------------------ |
> | AFRINIC  | the African Network Information Center                       | Africa                                                            | [www.afrinic.net](https://www.afrinic.net) |
> | ARIN     | the American Registry for Internet Numbers                   | Antarctica, Canada, parts of the Caribbean, and the United States | [www.arin.net](https://www.arin.net/)      |
> | APNIC    | the Asia Pacific Network Information Center                  | East Asia, Oceania, South Asia, Southeast Asia                    | [www.apnic.net](https://www.apnic.net)     |
> | LACNIC   | the Latin America and Caribbean Network Information          | Latin America and most of the Caribbean                           | [www.lacnic.net](https://www.lacnic.net/)  |
> | RIPE NCC | Le Réseaux IP Européens Network Coordination Centre (French) | Europe, Central Asia, Russia, West Asia                           | [www.ripe.net](https://www.ripe.net/)      |
> 
Every AS controls a specific set of IP addresses, called an IP address block. If you find the block(s) that belongs to your target organization, you can try extracting subdomains by massive reverse DNS lookups.

- To find an ASN associated with a target organization, you can use `amass intel`:

```bash
amass intel -org "Example Inc."
```

- Or query the hostname directly using `dnsx`:

```bash
echo example.com | dnsx -asn
```

- [`HURRICANE ELECTRIC`](https://bgp.he.net/) provides a specialized (and free) search engine for this purpose and often gives more comprehensive and accurate results. 

>[!note] For more methods on how to discover ASNs, see [`SecurityTrails: ASN Lookup Tools, Strategies and Techniques`](https://securitytrails.com/blog/asn-lookup#autonomous-system-lookup-script).

- Once you have the ASNs, full IP ranges (`PTR` records) associated with it:

```bash
echo AS<number> | dnsx -silent -resp-only -ptr
```

```bash
amass intel -asn AS<number>
```

```bash
whois AS<number>
```

- Using [`asn`](https://github.com/nitefood/asn/) tool:

```
asn -u 203.0.113.5
```

- Online tools:
	- [`HACKER TARGET`](https://hackertarget.com/as-ip-lookup/) — Search IP address ranges by an ASN (or vice versa). 
	- [`MXTOOLBOX`](https://mxtoolbox.com/SuperTool.aspx?action=asn%3a13335&run=toolpage) — Search CIDR ranges by an ASN.
	- [`ASNLOOKUP`](https://asnlookup.com/) — Get information about a specific AS, organization, CIDR range, or IP address.
	- [`DNSCHECKER`](https://dnschecker.org/asn-whois-lookup.php) — `whois` for an ASN and other information about an AS.
	- [`ASRank`](https://asrank.caida.org/asns/6427) — Get information about a specific AS, its rank, and relationships with other ASs.

>[!note] Take a look at the [`HostHunter`](https://github.com/SpiderLabs/HostHunter) tool. It can discover hostnames from IP addresses using OSINT and active reconnaissance techniques.

>[!info]- ASN ranges
> | Bits                            | Bits | Description                                       | Reference                                                                                                                                                                                 |
> | ------------------------------- | ---- | ------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
> | `0`                             | 16   | Reserved for RPKI unallocated space invalidation  | [RFC](https://en.wikipedia.org/wiki/RFC_(identifier) "RFC (identifier)") [6483](https://datatracker.ietf.org/doc/html/rfc6483), RFC [7607](https://datatracker.ietf.org/doc/html/rfc7607) |
> | `1`–`23,455`                    | 16   | Public ASNs                                       |                                                                                                                                                                                           |
> | `23,456`                        | 16   | Reserved for AS Pool Transition                   | RFC [6793](https://datatracker.ietf.org/doc/html/rfc6793)                                                                                                                                 |
> | `23,457`–`64,495`               | 16   | Public ASNs                                       |                                                                                                                                                                                           |
> | `64,496`–`64,511`               | 16   | Reserved for use in documentation and sample code | RFC [5398](https://datatracker.ietf.org/doc/html/rfc5398)                                                                                                                                 |
> | `64,512`–`65,534`               | 16   | Reserved for private use                          | RFC [1930](https://datatracker.ietf.org/doc/html/rfc1930), RFC [6996](https://datatracker.ietf.org/doc/html/rfc6996)                                                                      |
> | `65,535`                        | 16   | Reserved                                          | RFC [7300](https://datatracker.ietf.org/doc/html/rfc7300)                                                                                                                                 |
> | `6,5536`–`65,551`               | 32   | Reserved for use in documentation and sample code | RFC [5398](https://datatracker.ietf.org/doc/html/rfc5398), RFC [6793](https://datatracker.ietf.org/doc/html/rfc6793)                                                                      |
> | `65,552`–`131,071`              | 32   | Reserved                                          |                                                                                                                                                                                           |
> | `131,072`–`4,199,999,999`       | 32   | Public 32-bit ASNs                                |                                                                                                                                                                                           |
> | `4,200,000,000`–`4,294,967,294` | 32   | Reserved for private use                          | RFC [6996](https://datatracker.ietf.org/doc/html/rfc6996)                                                                                                                                 |
> | `4,294,967,295`                 | 32   | Reserved                                          | RFC [7300](https://datatracker.ietf.org/doc/html/rfc7300)                                                                                                                                 |
### DNSSEC zone walking

>**DNSSEC (Domain Name System Security Extensions)** extends DNS with cryptographic signatures that provide authenticity and integrity for DNS records.

- If the target uses **`NSEC` records** for a DNSSEC-signed zone, negative responses include an `NSEC` record that explicitly states the hostname doesn't exist. That record also reveals the **next valid hostname in canonical order**. This creates a chain that links every name in the zone.
- To enumerate subdomains, you can repeatedly query for non-existent names and follow each `NSEC` record to the next hostname, **walking through the zone**. You get all hostnames in the zone without having to brute-force them individually. This technique is known as **DNSSEC zone walking**.
- It only works when:
	- DNSSEC is enabled.
	- The zone uses **`NSEC` records** rather than **`NSEC3`**.

- To check if the target uses DNSSEC, query `DNSKEY` or other DNSSEC records (`RRSIG`, `DS`, `NSEC`, `NSEC3`):

```bash
dig example.com DNSKEY +short
```

- Perform DNSSEC zone walking:

```bash
dig example.com NSEC
```

- Because most deployments either disable DNSSEC or use `NSEC3`, successful zone walking is relatively uncommon. However, it remains a valuable technique when applicable because it can reveal complete zone contents with relatively few queries.

>[!note]+ As of 2026, DNSSEC adoption is still spotty. See [`DNSSEC World Map — APNIC`](https://stats.labs.apnic.net/dnssec) for DNSSEC validation rates by country (and a map).
>![[dnssec_adoption_map.png]]

>[!note] You can also use [`Verisign DNSSEC-analyzer`](https://dnssec-analyzer.verisignlabs.com/) to see if a zone to which the target domain belons uses DNSSEC.

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

>A **wildcard DNS record** matches queries for **non-existent hostnames** within a zone domain names. Instead of returning `NXDOMAIN`, the DNS server returns a valid response for almost any queried name.

- Such records have an asterisk (`*`) as the leftmost label of a domain name:

```bash
*.example.com.   86400 IN NS ns1.example.com.
```

>[!example] For example, if `*.example.com` resolves to `203.0.113.5`, then `random.example.com`, `nothingthere.example.com`, etc. all resolve to that IP address — even though none of these actually exist.

- Wildcard records therefore produce **false positives** during brute-force enumeration.
-  The first indicator of a wildcard domain is an unusually large number of valid subdomains. 
- The simplest way to confirm a wildcard is to query a subdomain you're sure doesn't exist:

```bash
dig fc9518847a.example.com A
```

- Query a random 10-character subdomain:

```bash
dig "$(tr -dc 'a-z0-9' < /dev/urandom | head -c 10).example.com" A
```

- If the query returns a valid record instead of `NXDOMAIN`, the zone is likely using wildcard DNS.

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

> [!important] Some wildcard configurations respond only to specific hostnames and do not answer queries for `*.example.com` directly. Detection should therefore always be performed using randomly generated hostnames.

>[!important] Some configurations respond to wildcard entries but don't respond to queries like `*.example.com` directly.

- Most modern enumeration tools automatically detect and filter wildcard responses.


