---
created: 2026-07-17
tags:
  - recon
status: incomplete
---

So, you have a bunch of IP addresses and subdomains. What's next?

>[!note] This stage assumes you've done asset discovery and have a list of target subdomains and/or IP addresses. 

>[!note] See [[Visual recon]].
## Naabu

>**[Naabu](https://github.com/projectdiscovery/naabu)** is a fast, open-source port scanner written in Go by ProjectDiscovery, optimized for initial reconnaissance and mass scanning.

>[!note]+ Naabu vs. Nmap
>- Naabu is significantly faster than Nmap for initial discovery. It doesn't attempt deep service identification, just answers the question: "Is this port open?"
>- It includes **automatic IP address deduplication** when resolving domains. This prevents redundant scans. 
>- Naabu is best for bug bounty recon and scanning large IP ranges quickly. It supports passive scanning via Shodan API and simple TCP/UDP scans.
>- For complex network auditing and more thorough scans, Nmap is, of course, superior. 

>[!note]+ Installation
>- Download a [binary](https://github.com/projectdiscovery/naabu/releases/) or a [Docker image](https://hub.docker.com/r/projectdiscovery/naabu).
>- See [`Installation Instructions — naabu`](https://github.com/projectdiscovery/naabu#installation-instructions).

- Basic port scan:

```bash
naabu -host example.com
```

- Scan multiple hosts at once and save results to a file:

```bash
naabu -list subdomains.txt -p results.txt
```

- Scan specific ports:

```bash
naabu -host example.com -p 80,443,8080
```

```bash
naabu -host example.com -p 1-1000
```

- Scan top `100` ports:

```bash
naabu -host example.com -sa -tp 100 -ec -o results.txt
```

- Scan all ports (`1`-`65535`):

```bash
naabu -host example.com -sa -p - -ec -o results.txt
```

> [!note]+ Options breakdown
> 
> | Option                 | Description                                                             |
> | ---------------------- | ----------------------------------------------------------------------- |
> | `-host`                | Hosts to scan (comma-separated).                                        |
> | `-p`, `-port`          | Ports to scan, e.g. `80`, `443`, `100-200`.                             |
> | `-tp`, `-top-ports`    | Top ports to scan (`full`, `100`, `1000`). Default: `100`.              |
> | `-sa`, `-scan-all-ips` | Scan all IP addresses associated with a DNS record.                     |
> | `-ec`, `-exclude-cdn`  | Skip full port scans for CDN/WAF hosts; only scan ports `80` and `443`. |
> | `-o`, `-output`        | File to write output to.                                                |


### Options cheat sheet

```bash
naabu -h
```

- Input:

| Option                  | Description                                         |
| ----------------------- | --------------------------------------------------- |
| `-host`                 | Hosts to scan (comma-separated).                    |
| `-l`, `-list`           | File with a list of hosts to scan.                  |
| `-eh`, `-exclude-hosts` | Hosts to exclude from the scan (comma-separated).   |
| `-ef`, `-exclude-file`  | File with a list of hosts to exclude from the scan. |

- Ports:

| Option                    | Description                                                             |
| ------------------------- | ----------------------------------------------------------------------- |
| `-p`, `-port`             | Ports to scan, e.g. `80`, `443`, `100-200`.                             |
| `-tp`, `-top-ports`       | Top ports to scan (`full`, `100`, `1000`). Default: `100`.              |
| `-ep`, `-exclude-ports`   | Ports to exclude from the scan (comma-separated).                       |
| `-pf`, `-ports-file`      | File with a list of ports to scan.                                      |
| `-pts`, `-port-threshold` | Skip port scan for hosts above this threshold.                          |
| `-ec`, `-exclude-cdn`     | Skip full port scans for CDN/WAF hosts; only scan ports `80` and `443`. |
| `-cdn`, `-display-cdn`    | Display the CDN in use.                                                 |

- Rate-limit:

| Option  | Description                                      |
| ------- | ------------------------------------------------ |
| `-c`    | General internal worker threads (default: `25`). |
| `-rate` | Packets to send per second (default: `1000`).    |

- Output:

| Option          | Description                        |
| --------------- | ---------------------------------- |
| `-o`, `-output` | File to write output to.           |
| `-j`, `-json`   | Write output in JSON Lines format. |
| `-csv`          | Write output in CSV format.        |

- Service discovery:

| Option                      | Description                                                               |
| --------------------------- | ------------------------------------------------------------------------- |
| `-sD`, `-service-discovery` | Identify services by port number.                                         |
| `-sV`, `-service-version`   | Detect service versions using `nmap-service-probes`.                      |
| `-sV-fast`                  | Only probe port-hinted services; faster, skips fallback.                  |
| `-sV-timeout`               | Timeout for service version probes (default: `5s`).                       |
| `-sV-workers`               | Number of concurrent service version workers. Default: `25`.              |
| `-sV-probes`                | Custom `nmap-service-probes` file path. Auto-detected if empty.           |
| `-uP`, `-udp-probes`        | Send protocol-specific payloads on UDP scans using `nmap-service-probes`. |

- Configuration:

| Option                        | Description                                                                                |
| ----------------------------- | ------------------------------------------------------------------------------------------ |
| `-config`                     | Path to the Naabu configuration file. Default: `$HOME/.config/naabu/config.yaml`.          |
| `-sa`, `-scan-all-ips`        | Scan all IP addresses associated with a DNS record.                                        |
| `-ip-version`, `-iv`          | IP versions to scan for hostname: `4`, `6` (default: `["4","6"]`).                         |
| `-scan-type`, `-s`            | Type of port scan: `SYN` or `CONNECT` (default: `c`).                                      |
| `-source-ip`                  | Source IP and port (`x.x.x.x:yyy`). May not work on macOS.                                 |
| `-cp`, `-connect-payload`     | Payload to send in `CONNECT` scans.                                                        |
| `-interface-list`, `-il`      | List available interfaces and public IP.                                                   |
| `-interface`, `-i`            | Network interface to use for port scan.                                                    |
| `-nmap`                       | Invoke nmap scan on targets. Deprecated.                                                   |
| `-nmap-cli`                   | Nmap command to run on found results.                                                      |
| `-r`                          | Custom resolver DNS list, comma-separated or from file.                                    |
| `-proxy`                      | SOCKS5 proxy (`ip[:port]`/`fqdn[:port]`).                                                  |
| `-proxy-auth`                 | SOCKS5 proxy authentication (`username:password`).                                         |
| `-dns-order`                  | DNS resolution order: `p`,`l`, `lp`, or `pl` (default: `l`).                               |
| `-sr`, `-system-resolver`     | Use system DNS as fallback resolver.                                                       |
| `-resume`                     | Resume scan using `resume.cfg`.                                                            |
| `-stream`                     | Stream mode; disables resume, nmap, verify, retries, shuffling, etc.                       |
| `-passive`                    | Display passive open ports using Shodan InternetDB API; enables stream mode automatically. |
| `-irt`, `-input-read-timeout` | Timeout on input read. Default: `3m0s`.                                                    |
| `-no-stdin`                   | Disable stdin processing.                                                                  |

- Host discovery:

| Option                            | Description                                                                  |
| --------------------------------- | ---------------------------------------------------------------------------- |
| `-sn`, `-host-discovery`          | Perform only host discovery.                                                 |
| `-show-dead`                      | Show hosts that did not respond to host discovery. Requires host discovery.  |
| `-Pn`, `-skip-host-discovery`     | Skip host discovery. Deprecated; use `-wn` / `-with-host-discovery` instead. |
| `-wn`, `-with-host-discovery`     | Enable host discovery.                                                       |
| `-ps`, `-probe-tcp-syn`           | TCP SYN ping. Requires host discovery.                                       |
| `-pa`, `-probe-tcp-ack`           | TCP ACK ping. Requires host discovery.                                       |
| `-pe`, `-probe-icmp-echo`         | ICMP echo request ping. Requires host discovery.                             |
| `-pp`, `-probe-icmp-timestamp`    | ICMP timestamp request ping. Requires host discovery.                        |
| `-pm`, `-probe-icmp-address-mask` | ICMP address mask request ping. Requires host discovery.                     |
| `-arp`, `-arp-ping`               | ARP ping. Requires host discovery.                                           |
| `-nd`, `-nd-ping`                 | IPv6 Neighbor Discovery. Requires host d.                                    |
| `-rev-ptr`                        | Reverse PTR lookup for input IPs.                                            |

- Optimization:

| Option                         | Description                                                                             |
| ------------------------------ | --------------------------------------------------------------------------------------- |
| `-retries`                     | Number of retries for the port scan (default: `3`).                                     |
| `-timeout`                     | Milliseconds to wait before timing out (default: `1000`).                               |
| `-warm-up-time`                | Time in seconds between scan phases (default: `2`).                                     |
| `-ping`                        | Ping probes for verification of host.                                                   |
| `-verify`                      | Validate the ports again with TCP verification.                                         |
| `-ss`, `-smart-scan`           | Predictive port scanning using port correlation model. Not compatible with stream mode. |
| `-pt`, `-prediction-threshold` | Minimum confidence for port predictions, `0-100%` (default: `20`).                      |

- Debug:

| Option                   | Description                                                             |
| ------------------------ | ----------------------------------------------------------------------- |
| `-health-check`, `-hc`   | Run diagnostic checkup.                                                 |
| `-debug`                 | Display debugging information.                                          |
| `-verbose`, `-v`         | Display verbose output.                                                 |
| `-no-color`, `-nc`       | Disable colors in CLI output.                                           |
| `-silent`                | Display only results in output.                                         |
| `-version`               | Display version of Naabu.                                               |
| `-stats`                 | Display stats of the running scan. Deprecated.                          |
| `-si`, `-stats-interval` | Number of seconds between statistics updates. Deprecated. Default: `5`. |
| `-mp`, `-metrics-port`   | Port to expose Naabu metrics on (default: `63636`).                     |

- Cloud:

| Option                      | Description                                                       |
| --------------------------- | ----------------------------------------------------------------- |
| `-auth`                     | Configure Project Cloud (pdcp) API key. Default: `true`.          |
| `-ac`, `-auth-config`       | Configure ProjectDiscovery Cloud (pdcp) API key credential file.  |
| `-pd`, `-dashboard`         | Upload/view output in ProjectDiscovery Cloud dashboard.           |
| `-tid`, `-team-id`          | Upload asset results to a given team ID (optional).               |
| `-aid`, `-asset-id`         | Upload new assets to an existing asset ID (optional).             |
| `-aname`, `-asset-name`     | Set asset group name (optional).                                  |
| `-pdu`, `-dashboard-upload` | Upload Naabu output file (`jsonl`) to ProjectDiscovery dashboard. |
## HTTPX

>[`httpx`](https://github.com/projectdiscovery/httpx) is a fast, multi-purpose HTTP toolkit written in Go by ProjectDiscovery, primarily designed for HTTP probing, enumeration, and fingerprinting.

- HTTPX can handle thousands of hosts efficiently thanks to high concurrency capabilities.
- It accepts domains, URLs, IP addresses, CIDR ranges, raw requests; can output in JSON and CVS.

>[!note]+ Installation
> - `go install` (Go >= 1.25.0):
>```bash
>go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
>```
>- See [`Installation Instructions — httpx`](https://github.com/projectdiscovery/httpx#installation-instructions).

- Single request:

```bash
httpx -u exaple.com
```

- From file or `stdin`:

```bash
cat subdomains.txt | httpx
```

### Subdomain & live host discovery

- Probe live HTTP/HTTPS services, output clean list with status and title:

```bash
cat subdomains.txt | httpx -silent -sc -title -o live_hosts.txt
```

- Live check + technology detection, server info, content length, response time, IP address, and CDN detection:

```bash
cat subdomains.txt | httpx -silent -sc -title -td -web-server -cl -rt -ip -cdn -o enriched.txt
```

- Probe every IP address associated with the host (great for finding hidden services behind CDNs):

```bash
httpx -l hosts.txt -pa -probe -sc -title
```

| Option                   | Description                                |
| ------------------------ | ------------------------------------------ |
| `-silent`                | Silent mode (only URLs).                   |
| `-sc`, `-status-code`    | Display response status code.              |
| `-title`                 | Display page title.                        |
| `-td`, `-tech-detect`    | Display technologies (Wappalyzer dataset). |
| `-server`, `-web-server` | Display server name.                       |
| `-cl`, `-content-length` | Display response content length.           |
| `-rt`, `-response-time`  | Display response time.                     |
| `-pa`, `-probe-all-ips`  | Probe all IPs for the same host.           |
| `-probe`                 | Display probe status.                      |
| `-ip`                    | Display host IP address.                   |
| `-cdn`                   | Display CDN/WAF in use (default: `true`).  |
| `-o`, `-output`          | File to write output results.              |
### Fingerprinting 

- Use custom Wappalyzer-style fingerprints for niche tech (e.g., internal frameworks):

```bash
httpx -l live.txt -td -cff custom_fingerprints.yaml -title -server -json -o tech.json
```

- Groups similar applications/servers across the attack surface using JARM fingerprints and favicon hashes:

```bash
httpx -l hosts.txt -jarm -favicon -json | jq -r '.[] | "\(.jarm) \(.favicon) \(.url)"' | sort -u
```

- Pull additional domains/subdomains mentioned in HTML/headers (expanding scope):

```bash
httpx -l hosts.txt -efqdn -json -o domains.json
```

### Screenshots & visual recon

- Take screenshots with custom timeout/idle time using local Chrome (saves screenshots to the output directory):

```bash
httpx -l interesting.txt -ss -st 15 -sid 2 -system-chrome -o screenshots/
```

### Pipelining with other tools

```bash
subfinder -d target.com -silent | dnsx -silent -a -resp | httpx -silent -sc -title -o live_hosts.txt
```
### Options cheat sheet

- Input:

| Option               | Description                                                        |
| -------------------- | ------------------------------------------------------------------ |
| `-l`, `-list`        | Input file containing list of hosts to process.                    |
| `-rr`, `-request`    | File containing raw HTTP request.                                  |
| `-u`, `-target`      | Input target host(s) to probe (comma-separated or multiple flags). |
| `-im`, `-input-mode` | Mode of input file (e.g. `burp`).                                  |
- Probes:

| Option                             | Description                                                                        |
| ---------------------------------- | ---------------------------------------------------------------------------------- |
| `-sc`, `-status-code`              | Display response status code.                                                      |
| `-cl`, `-content-length`           | Display response content length.                                                   |
| `-ct`, `-content-type`             | Display response content type.                                                     |
| `-location`                        | Display response redirect location.                                                |
| `-title`                           | Display page title.                                                                |
| `-server`, `-web-server`           | Display server name.                                                               |
| `-td`, `-tech-detect`              | Display technologies (Wappalyzer dataset).                                         |
| `-cff`, `-custom-fingerprint-file` | Path to custom fingerprint file for tech detection.                                |
| `-method`                          | Display HTTP request method.                                                       |
| `-ws`, `-websocket`                | Display if server supports WebSocket.                                              |
| `-ip`                              | Display host IP address.                                                           |
| `-cname`                           | Display host `CNAME`.                                                              |
| `-asn`                             | Display host ASN information.                                                      |
| `-cdn`                             | Display CDN/WAF in use (default: `true`).                                          |
| `-favicon`                         | Display mmh3 hash for `/favicon.ico`.                                              |
| `-hash`                            | Display response body hash (`md5`, `mmh3`, `simhash`, `sha1`, `sha256`, `sha512`). |
| `-jarm`                            | Display JARM fingerprint hash.                                                     |
| `-rt`, `-response-time`            | Display response time.                                                             |
| `-lc`, `-line-count`               | Display response body line count.                                                  |
| `-wc`, `-word-count`               | Display response body word count.                                                  |
| `-bp`, `-body-preview`             | Display first N characters of response body (default: `100`).                      |
| `-probe`                           | Display probe status.                                                              |
| `-extract-fqdn`, `-efqdn`          | Extract domains/subdomains from body and headers (JSONL/CSV).                      |

- Headless (screenshots):

| Option                              | Description                                      |
| ----------------------------------- | ------------------------------------------------ |
| `-ss`, `-screenshot`                | Enable saving screenshot using headless browser. |
| `-system-chrome`                    | Use locally installed Chrome for screenshots.    |
| `-ho`, `-headless-options`          | Additional Chrome options (comma-separated).     |
| `-st`, `-screenshot-timeout`        | Screenshot timeout in seconds (default: 10s).    |
| `-sid`, `-screenshot-idle`          | Idle time before screenshot (default: 1s).       |
| `-jsc`, `-javascript-code`          | JavaScript to execute after navigation.          |
| `-esb`, `-exclude-screenshot-bytes` | Exclude screenshot bytes from JSON output.       |
| `-ehb`, `-exclude-headless-body`    | Exclude headless body from JSON output.          |
| `-no-screenshot-full-page`          | Disable full page screenshots.                   |

- Matchers:

| Option                         | Description                                   |
| ------------------------------ | --------------------------------------------- |
| `-mc`, `-match-code`           | Match specific status codes (e.g. `200,302`). |
| `-ml`, `-match-length`         | Match content length (e.g. `100,102`).        |
| `-mlc`, `-match-line-count`    | Match line count.                             |
| `-mwc`, `-match-word-count`    | Match word count.                             |
| `-mfc`, `-match-favicon`       | Match favicon hash.                           |
| `-ms`, `-match-string`         | Match response containing string.             |
| `-mr`, `-match-regex`          | Match response with regex.                    |
| `-mcdn`, `-match-cdn`          | Match specific CDN provider.                  |
| `-mrt`, `-match-response-time` | Match response time (e.g. `'< 1'`).           |
| `-mdc`, `-match-condition`     | Match with DSL expression.                    |


- Extractor:

| Option | Description |
| --- | --- |
| `-er`, `-extract-regex` | Extract content matching regex. |
| `-ep`, `-extract-preset` | Extract using preset (e.g. `url`, `ipv4`, `mail`). |

- Filters:

| Option                          | Description                                             |
| ------------------------------- | ------------------------------------------------------- |
| `-fc`, `-filter-code`           | Filter out specific status codes (e.g. `403,401`).      |
| `-fpt`, `-filter-page-type`     | Filter page types (e.g. `login,captcha,parked`).        |
| `-fep`, `-filter-error-page`    | Filter error pages (ML-based, deprecated — use `-fpt`). |
| `-fd`, `-filter-duplicates`     | Filter near-duplicate responses.                        |
| `-fl`, `-filter-length`         | Filter content length.                                  |
| `-flc`, `-filter-line-count`    | Filter line count.                                      |
| `-fwc`, `-filter-word-count`    | Filter word count.                                      |
| `-ffc`, `-filter-favicon`       | Filter favicon hash.                                    |
| `-fs`, `-filter-string`         | Filter responses containing string.                     |
| `-fe`, `-filter-regex`          | Filter with regex.                                      |
| `-fcdn`, `-filter-cdn`          | Filter specific CDN providers.                          |
| `-frt`, `-filter-response-time` | Filter response time.                                   |
| `-fdc`, `-filter-condition`     | Filter with DSL expression.                             |
| `-strip`                        | Strip tags from response (html/xml).                    |

- Output:

| Option                                 | Description                                        |
| -------------------------------------- | -------------------------------------------------- |
| `-o`, `-output`                        | File to write output results.                      |
| `-oa`, `-output-all`                   | Write output in all formats.                       |
| `-j`, `-json`                          | Output in JSONL format.                            |
| `-csv`                                 | Output in CSV format.                              |
| `-csvo`, `-csv-output-encoding`        | CSV output encoding.                               |
| `-irh`, `-include-response-header`     | Include response headers in JSON.                  |
| `-irr`, `-include-response`            | Include request/response (headers + body) in JSON. |
| `-irrb`, `-include-response-base64`    | Include base64 encoded request/response in JSON.   |
| `-include-chain`                       | Include redirect chain in JSON.                    |
| `-sr`, `-store-response`               | Store HTTP responses to output directory.          |
| `-srd`, `-store-response-dir`          | Custom directory for stored responses.             |
| `-ob`, `-omit-body`                    | Omit response body in output.                      |
| `-svrc`, `-store-vision-recon-cluster` | Store visual recon clusters.                       |

- Rate limit & concurrency:

| Option                       | Description                               |
| ---------------------------- | ----------------------------------------- |
| `-t`, `-threads`             | Number of threads (default: `50`).        |
| `-rl`, `-rate-limit`         | Max requests per second (default: `150`). |
| `-rlm`, `-rate-limit-minute` | Max requests per minute.                  |

- Miscellaneous:

| Option                     | Description                                             |
| -------------------------- | ------------------------------------------------------- |
| `-p`, `-ports`             | Ports to probe (nmap syntax, e.g. `http:80,https:443`). |
| `-path`                    | Paths to probe (comma-separated or file).               |
| `-x`                       | HTTP methods to probe (`all` for all methods).          |
| `-fr`, `-follow-redirects` | Follow HTTP redirects.                                  |
| `-maxr`, `-max-redirects`  | Max redirects (default: `10`).                          |
| `-pa`, `-probe-all-ips`    | Probe all IPs for the same host.                        |
| `-vhost`                   | Probe for VHost support.                                |
| `-tls-probe`               | Probe TLS-extracted domains.                            |
| `-csp-probe`               | Probe CSP-extracted domains.                            |
| `-tls-grab`                | Perform TLS data grabbing.                              |
| `-pipeline`                | Check HTTP/1.1 pipeline support.                        |
| `-http2`                   | Check HTTP/2 support.                                   |
| `-random-agent`            | Enable random User-Agent (default: true).               |
| `-H`, `-header`            | Custom HTTP headers.                                    |
| `-proxy`                   | HTTP/SOCKS proxy.                                       |
| `-r`, `-resolvers`         | Custom resolvers (file or comma-separated).             |
| `-allow` / `-deny`         | Allowed/Denied IP/CIDR lists.                           |

- Optimizations & config:

| Option                | Description                            |
| --------------------- | -------------------------------------- |
| `-nf`, `-no-fallback` | Display both HTTP and HTTPS.           |
| `-retries`            | Number of retries.                     |
| `-timeout`            | Timeout in seconds (default: `10`).    |
| `-delay`              | Delay between requests (e.g. `200ms`). |
| `-resume`             | Resume scan from `resume.cfg`.         |
| `-silent`             | Silent mode (only URLs).               |
| `-v`, `-verbose`      | Verbose mode.                          |
| `-debug`              | Show request/response in CLI.          |
| `-config`             | Path to config file.                   |

- Update & debug:

| Option                 | Description                     |
| ---------------------- | ------------------------------- |
| `-up`, `-update`       | Update httpx to latest version. |
| `-version`             | Show version.                   |
| `-health-check`, `-hc` | Run diagnostic check.           |
| `-stats`               | Display scan statistics.        |