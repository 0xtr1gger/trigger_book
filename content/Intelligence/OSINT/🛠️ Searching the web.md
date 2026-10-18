---
created: 2026-09-26
updated: 2026-09-30
tags:
  - OSINT
  - web_hacking
status: complete
---
## Using search engines to find sensitive information

- **Search engine discovery** involves gathering publicly indexed information about a target using search engines and web archives. Because search engines query pre-indexed data, this is a passive reconnaissance technique, and therefore no traffic is sent to the target's infrastructure.
- Search engine discovery can be direct or indirect:
	- **Direct** methods search indexed content hosted directly on the target's domain.
	- **Indirect** methods search third-party websites — such as code hosting platforms, pastebins, technical forums, publicly available cloud storage like S3 buckets — for leaked credentials and other useful details associated with the target.
- Sensitive information you may find using search engines includes:
	- Network architecture diagrams and infrastructure documentation.
	- Archived posts and emails by administrators or other employees.
	- Password policies, login procedures, and username formats.
	- User credentials, API keys, and private cryptographic keys.
	- Configuration files for third-party software and cloud services.
	- Error messages and stack traces.
	- Applications not intended to be public, such as development, test, and staging versions.

>[!note] See [[How search engines work]].

### Search engines

- Each search engine maintains its own index, ranking algorithms, and operator syntax, so the same query returns different results on different engines. Don't limit yourself to a single engine.

>[!note] Only a few engines crawl the web and maintain an **independent index** (e.g., Google, Bing, Yandex, Baidu, Brave Search, Mojeek). Many others, including DuckDuckGo and Startpage, largely serve results from another engine's index, so querying them in addition to the underlying engine adds little coverage.

| Search engine                               | Description                                                                                                                                                                                                                                                                                                      |
| :------------------------------------------ | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`Google`](https://www.google.com/)         | The world's [most popular](https://en.wikipedia.org/wiki/Web_search_engine#Market_share) search engine. Ranks results by relevance to the individual user; results may be subject to censorship and personalization.                                                                                             |
| [`Bing`](https://www.bing.com/)             | Microsoft's search engine and the second [most popular](https://en.wikipedia.org/wiki/Web_search_engine#Market_share) worldwide. Supports [advanced search keywords](https://support.microsoft.com/en-us/topic/advanced-search-keywords-ea595928-5d63-4a0b-9c6b-0b769865e78a) absent from Google, such as `ip:`. |
| [`Yandex`](https://yandex.com/)             | The most popular search engine in Russia; maintains an independent index with strong coverage of Russian-language and Eastern European content.                                                                                                                                                                  |
| [`Baidu`](https://www.baidu.com/)           | China's [most popular](https://en.wikipedia.org/wiki/Web_search_engine#Market_share) search engine; strongest coverage of Chinese-language content.                                                                                                                                                              |
| [`Brave Search`](https://search.brave.com/) | A privacy-focused search engine with its own independent index.                                                                                                                                                                                                                                                  |
| [`Mojeek`](https://www.mojeek.com/)         | A privacy-focused search engine with its own independent index.                                                                                                                                                                                                                                                  |
| [`DuckDuckGo`](https://duckduckgo.com/)     | A privacy-focused search engine that compiles results from many different [sources](https://help.duckduckgo.com/results/sources/); supports its own [search syntax](https://help.duckduckgo.com/duckduckgo-help-pages/results/syntax/).                                                                          |
| [`Startpage`](https://www.startpage.com/)   | A privacy-focused front end that returns mainly Google results without tracking or personalization.                                                                                                                                                                                                              |
| [`binsearch.info`](https://binsearch.info/) | A search engine for binary Usenet newsgroups.                                                                                                                                                                                                                                                                    |

>[!note] Google may [censor](https://en.wikipedia.org/wiki/Censorship_by_Google) certain search results and personalize results based on user activity, which can hinder investigations. Privacy-respecting alternatives return more or less consistent results for all users.

>[!tip] You can also self-host a metasearch engine such as [`SearXNG`](https://github.com/searxng/searxng) that aggregates results from many engines at once.

- Internet-wide scan search engines, such as Shodan and Censys, index hosts and services rather than web pages; see [[#Searching internet-connected infrastructure]].
- Web archives and crawl datasets, such as the Wayback Machine and Common Crawl, keep historical copies of pages; see [[#Searching web archives]].

## Search operators

>A **search operator** is a special keyword or syntax that narrows or modifies a search query to return more specific results.

- Documentation on search operators for different search engines:
	- [`Refine Google searches — Google Search Help`](https://support.google.com/websearch/answer/2466433)
	- [`Google Search Operators (community reference)`](https://docs.google.com/document/d/1ydVaJJeL1EYbWtlfj9TPfBTE5IBADkQfZrQaBZxqXGs/edit?tab=t.0)
	- [`Advanced search keywords — Bing`](https://support.microsoft.com/en-us/topic/advanced-search-keywords-ea595928-5d63-4a0b-9c6b-0b769865e78a)
	- [`Search Operators — Brave Search`](https://search.brave.com/help/operators)
	- [`Search Syntax — DuckDuckGo`](https://help.duckduckgo.com/duckduckgo-help-pages/results/syntax/)

>[!important] Don't put a space between an operator and its value: `site:example.com`, not `site: example.com`.

>[!note] Search engines display estimated result counts. A `site:` query doesn't guarantee an exhaustive list of all indexed URLs under a domain.

### General operators

- The following operators work in most major search engines (Google, Bing, Brave Search, and DuckDuckGo):

| Operator                | Description                                                                              | Example                                                                                                   |
| :---------------------- | :--------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------- |
| `" "` (quotation marks) | Search for an exact phrase match.                                                        | `"powered by WordPress"`<br>The exact phrase must appear.                                                 |
| `-` (minus sign)        | Exclude a term or operator from the results. Don't put a space after the minus sign.     | `security -firewall`<br>`site:example.com -site:www.example.com`                                          |
| `site:`                 | Limit results to a domain, subdomain, or URL prefix.                                     | `site:example.com`<br>Search for pages only on `example.com` (and its subdomains, depending on the engine). |
| `filetype:`             | Limit results to files of a specific type.                                               | `filetype:pdf`<br>Search for PDF files.                                                                   |
| `intitle:`              | Search for pages with a specific term in the title.                                      | `intitle:"report"`<br>Find pages with `report` in the title.                                              |
| `OR`                    | Require either term to be present. Must be uppercase.                                    | `site:example.com admin OR login`<br>Find pages that mention either `admin` or `login`.                    |
| `AND`                   | Require both terms to be present. This is the default behavior, so `AND` can be omitted. | `security AND vulnerability`<br>Both terms must appear.                                                   |

>[!note] DuckDuckGo doesn't document `OR` and `AND`.

### Engine-specific operators

- The following operators work only in some search engines. Google officially documents only a few operators (`" "`, `-`, `site:`, `filetype:`, `before:`, and `after:`); the other Google operators below are undocumented but long established.

| Operator                              | Description                                                                                                   | Example                                                          | Supported by                                                                   |
| :------------------------------------ | :------------------------------------------------------------------------------------------------------------ | :--------------------------------------------------------------- | :----------------------------------------------------------------------------- |
| `ext:`                                | Limit results to files with a specific extension. Synonym for `filetype:` in practice.                        | `ext:sql`                                                        | Google, Bing, Brave Search                                                     |
| `inurl:`                              | Search for pages with a specific term in the URL.                                                             | `inurl:login`                                                    | Google, DuckDuckGo                                                             |
| `\|` (pipe)                           | Synonym for `OR`.                                                                                             | `inurl:admin \| inurl:login`                                     | Google, Bing                                                                   |
| `()` (parentheses)                    | Group terms and operators.                                                                                    | `(site:example.org \| site:example.com) filetype:pdf`            | Google, Bing                                                                   |
| `NOT`                                 | Exclude a term from the results. Synonym for `-`.                                                             | `security NOT firewall`                                          | Bing, Brave Search                                                             |
| `+` (plus sign)                       | Require a term to be present.                                                                                 | `+login`                                                         | Bing, Brave Search<br>DuckDuckGo gives the term more weight instead.           |
| `inbody:`                             | Search for pages with a specific term in the page body.                                                       | `inbody:"internal use only"`                                     | Bing, Brave Search                                                             |
| `loc:`, `location:`                   | Limit results to a country or region.                                                                         | `loc:DE`                                                         | Bing, Brave Search                                                             |
| `language:`                           | Limit results to a language. Brave Search also accepts `lang:`.                                               | `language:de`                                                    | Bing, Brave Search                                                             |
| `intext:`                             | Search for pages with a specific term in the page body.                                                       | `intext:"password reset"`                                        | Google                                                                         |
| `allintitle:`, `allinurl:`, `allintext:` | Require **all** the following terms to appear in the title, URL, or page body, respectively.               | `allintitle:private documents confidential`                      | Google                                                                         |
| `before:`, `after:`                   | Limit results to pages dated before or after a date. Format: `YYYY-MM-DD` or `YYYY/MM/DD`.                    | `after:2024-01-01`                                               | Google                                                                         |
| `*` (wildcard)                        | Match any word or words inside a phrase.                                                                      | `"admin * panel"`                                                | Google                                                                         |
| `..` (range search)                   | Search for numbers within a range. Unreliable.                                                                | `site:example.com 100..200`                                      | Google                                                                         |
| `AROUND(n)`                           | Find pages where two terms appear within `n` words of each other. Unreliable.                                 | `"password" AROUND(3) "default"`                                 | Google                                                                         |
| `ip:`                                 | Find sites hosted on a specific IPv4 address, such as virtual hosts that share it.                            | `ip:203.0.113.10`                                                | Bing                                                                           |
| `contains:`                           | Find pages that contain links to files of a specific type.                                                    | `site:example.com contains:pdf`                                  | Bing                                                                           |
| `url:`                                | Check whether a URL is in the index.                                                                          | `url:example.com/admin/`                                         | Bing                                                                           |
| `inanchor:`                           | Search for terms in the anchor text of links pointing to a page.                                              | `inanchor:"admin panel"`                                         | Bing                                                                           |
| `inpage:`                             | Search for pages with a specific term in either the title or the body.                                        | `inpage:confidential`                                            | Brave Search                                                                   |

>[!note] The `all*` operators apply to every term that follows them, so combining them with other operators in the same query gives unpredictable results. Prefer repeating the single-term operator: `inurl:admin inurl:login`.

### Deprecated Google operators

- The following operators no longer work in Google Search or return incomplete results. Older dork collections still use them:

| Operator                    | Former purpose                                                                     | Status                                                                                                  |
| :-------------------------- | :--------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------ |
| `cache:`                    | Show Google's cached copy of a page.                                               | Removed in 2024 together with cached page links. Use [[#Searching web archives\|web archives]] instead. |
| `link:`                     | Find pages that link to a URL.                                                     | Deprecated; returns incomplete results.                                                                 |
| `related:`                  | Find sites similar to a URL.                                                       | Deprecated.                                                                                             |
| `info:`                     | Show the information Google has about a URL.                                       | Deprecated.                                                                                             |
| `inanchor:`, `allinanchor:` | Search for terms in the anchor text of links pointing to a page.                   | Deprecated; `inanchor:` still works in Bing.                                                            |
| `numrange:`                 | Search for numbers within a range.                                                 | Deprecated; `..` is the remaining (unreliable) syntax.                                                  |
| `+` (plus sign)             | Force inclusion of a term Google would otherwise ignore or replace with a synonym. | Removed in 2011; use quotation marks instead: `"login"`. Bing and Brave Search still support `+`.       |

## Google dorks

- Operators can be chained to find specific kinds of exposed files and information. This technique is called [Google hacking](https://en.wikipedia.org/wiki/Google_hacking), or **dorking**, and each such query is a **dork**. It works on any search engine that supports the operators used.
- A typical dork scopes the search to the target with `site:` and combines it with conditions that match a specific kind of content.

>[!note] Enumerating subdomains through search engines is covered in [[Subdomain enumeration#Search engines]].

### Common dorks

- Replace `example.com` with the target domain:

| Dork                                                                                              | Description                                                                                                |
| :------------------------------------------------------------------------------------------------ | :--------------------------------------------------------------------------------------------------------- |
| `site:example.com intitle:"index of"`                                                             | Find exposed directory listings.                                                                           |
| `site:example.com ext:env \| ext:ini \| ext:conf \| ext:cnf \| ext:yml \| ext:xml`                | Find exposed configuration files.                                                                          |
| `site:example.com ext:sql \| ext:bak \| ext:old \| ext:backup \| ext:zip`                         | Find database dumps, backups, and archives.                                                                |
| `site:example.com ext:log`                                                                        | Find log files.                                                                                            |
| `site:example.com ext:pdf \| ext:docx \| ext:xlsx \| ext:pptx`                                    | Find public documents (metadata often reveals usernames, internal paths, and software versions).           |
| `site:example.com inurl:login \| inurl:signin \| intitle:admin`                                   | Find login pages and administrative panels.                                                                |
| `site:example.com inurl:swagger \| inurl:api-docs \| inurl:openapi`                               | Find exposed API documentation.                                                                            |
| `site:example.com ("PHP Fatal error" \| "Warning: mysql_" \| "Traceback (most recent call last)")` | Find exposed error messages and stack traces.                                                              |
| `site:*.example.com inurl:dev \| inurl:staging \| inurl:test`                                     | Find development, staging, and test environments.                                                          |
| `"@example.com" -site:example.com`                                                                | Find email addresses of target personnel published on third-party sites.                                  |
| `site:pastebin.com "example.com"`                                                                 | Find public pastes mentioning the target.                                                                  |
| `site:trello.com \| site:atlassian.net "example.com"`                                             | Find public boards and wiki pages on project management platforms.                                         |
| `site:s3.amazonaws.com \| site:blob.core.windows.net \| site:storage.googleapis.com "example"`     | Find publicly indexed files in cloud storage buckets.                                                      |

>[!important] Google limits a query to 32 words; terms past the limit are ignored. Split long `OR` chains into several queries.

>[!note] Google indexes little of the code on platforms such as GitHub; use the platform's own code search instead. See [[🛠️ Finding secrets in Git repositories]]. For employee names and username formats, see [[◯ OSINT username enumeration]].

### Dork databases

- Dork databases collect ready-made queries for specific kinds of information. The [Google Hacking Database (GHDB)](https://www.exploit-db.com/google-hacking-database) groups its dorks into categories such as:
	- Footholds
	- Files containing usernames
	- Sensitive directories
	- Web server detection
	- Vulnerable files
	- Vulnerable servers
	- Error messages
	- Files containing juicy info
	- Files containing passwords
	- Sensitive online shopping info
- Dork collections for different purposes:
	- [`Google Hacking Database (GHDB) — Exploit-DB`](https://www.exploit-db.com/google-hacking-database)
	- [`Bug Bounty Helper`](https://dorks.faisalahmed.me/)
	- [`google-dorks-bug-bounty`](https://github.com/TakSec/google-dorks-bug-bounty)
	- [`google-dorks`](https://github.com/Proviesec/google-dorks)
	- [`TUXCMD/Google-Dorks`](https://github.com/TUXCMD/Google-Dorks-Full_list/blob/master/googledorks_full.md)
	- [`Pentest Tools — Google Hacking`](https://pentest-tools.com/information-gathering/google-hacking)
	- [`DorkSearch.com`](https://dorksearch.com/)
	- [`7000_google_dork_list.txt`](https://github.com/aleedhillon/7000-Google-Dork-List/blob/master/7000_google_dork_list.txt)
	- [`1000 Google Dorks List`](https://gbhackers.com/latest-google-dorks-list/)
- AI-assisted query generators such as [`DorkGPT`](https://www.dorkgpt.com/) translate natural-language prompts into dork syntax, so you don't need to construct complex operator combinations manually.

>[!warning] Search engines rate-limit automated queries and respond with CAPTCHAs or temporary blocks. Tools that run dork lists automatically, such as [`pagodo`](https://github.com/opsdisk/pagodo), need long delays between queries.

## Searching internet-connected infrastructure

- Search engines such as [`Shodan`](https://www.shodan.io/) and [`Censys`](https://censys.com/) don't index web pages. They continuously scan the Internet and index exposed service data: open ports, service banners, TLS certificates, and HTTP responses.
- Querying them shows the target's exposed services without sending any traffic to the target. The data may be days or weeks old, so validate the results before relying on them.
- Other engines of this kind: [`FOFA`](https://en.fofa.info/), [`ZoomEye`](https://www.zoomeye.ai/), [`Netlas`](https://netlas.io/), and [`Criminal IP`](https://www.criminalip.io/).

>[!note] These services also serve as passive subdomain sources; see [[Subdomain enumeration#Third-party datasets]].

### Shodan filters

- Shodan offers a limited free plan and paid subscriptions. Most filters require a (free) account, and some, such as `vuln:`, require a paid plan.

| Filter                 | Description                                                                 | Example                                  |
| :--------------------- | :-------------------------------------------------------------------------- | :--------------------------------------- |
| `hostname:`            | Match hosts whose hostname contains the value.                              | `hostname:example.com`                   |
| `org:`                 | Match hosts by the organization that owns the IP address range.             | `org:"Example Inc"`                      |
| `net:`                 | Limit results to an IP address range in CIDR notation.                      | `net:203.0.113.0/24`                     |
| `asn:`                 | Limit results to an autonomous system.                                      | `asn:AS64500`                            |
| `port:`                | Match hosts with a specific open port.                                      | `port:3389`                              |
| `product:`             | Match the software product identified in the banner.                        | `product:"Apache httpd"`                 |
| `ssl:`                 | Search the TLS certificate and handshake data for a string.                 | `ssl:"Example Inc"`                      |
| `ssl.cert.subject.cn:` | Match the Common Name in the TLS certificate subject.                       | `ssl.cert.subject.cn:example.com`        |
| `http.title:`          | Match the title of the HTTP response.                                       | `http.title:"Dashboard"`                 |
| `http.favicon.hash:`   | Match the MurmurHash3 hash of the site's favicon.                           | `http.favicon.hash:<mmh3_hash>`          |
| `country:`             | Limit results to a country (two-letter code).                               | `country:DE`                             |

- Searching by TLS certificate finds hosts that serve the target's certificate even when no DNS record points to them, such as origin servers behind a CDN:

```text
ssl.cert.subject.cn:example.com -hostname:example.com
```

- A favicon hash identifies all hosts serving the same web application, such as a specific login portal. `httpx -favicon` computes the hash in the format Shodan expects; see [[🛠️ Host and service discovery]].

- The [`shodan`](https://cli.shodan.io/) CLI queries the same data from the terminal. Initialize it with your API key:

```bash
shodan init <api_key>
```

- Search for hosts and print selected fields:

```bash
shodan search --fields ip_str,port,hostnames 'ssl.cert.subject.cn:example.com'
```

- Show everything Shodan knows about a host:

```bash
shodan host 203.0.113.10
```

>[!note] Censys uses its own query language; see the [`Censys documentation`](https://docs.censys.com/).

## Searching web archives

- Web archives store historical snapshots of pages. They can reveal endpoints, files, parameters, and subdomains that the target once exposed but no longer links to, and many of these still respond:
	- [`Internet Archive`](https://archive.org/)
	- [`Wayback Machine`](https://web.archive.org/)
	- [`Archive.today`](https://archive.ph/)
	- [`Common Crawl`](https://commoncrawl.org/) — an open repository of web crawl data with a queryable URL index.
- [`CachedView`](https://cachedview.com/) aggregates archived copies of a page from several sources, including the Wayback Machine.

### Querying the Wayback Machine

- To view the archived versions of a site, visit `https://web.archive.org/web/*/` followed by the target URL. This displays a calendar view of all available snapshots:

```text
https://web.archive.org/web/*/example.com
```

- Append `/*` to list every archived URL under that prefix instead:

```text
https://web.archive.org/web/*/example.com/*
```

- Add `id_` after the timestamp to retrieve the original archived response without the Wayback Machine toolbar and rewritten links. A partial timestamp redirects to the closest snapshot:

```text
https://web.archive.org/web/2020id_/https://example.com/robots.txt
```

- The [CDX API](https://github.com/internetarchive/wayback/tree/master/wayback-cdx-server) returns the archive index as plain text, which is easier to process than the web interface. Retrieve all archived URLs under a domain, one entry per unique URL:

```bash
curl -s "https://web.archive.org/cdx/search/cdx?url=example.com/*&fl=original&collapse=urlkey"
```

- Include all subdomains with `matchType=domain`, and filter by HTTP status code or MIME type with `filter`:

```bash
curl -s "https://web.archive.org/cdx/search/cdx?url=example.com&matchType=domain&fl=original&collapse=urlkey&filter=statuscode:200"
```

```bash
curl -s "https://web.archive.org/cdx/search/cdx?url=example.com/*&fl=original&collapse=urlkey&filter=mimetype:application/pdf"
```

### Querying Common Crawl

- Common Crawl publishes a separate index for each crawl. List the available crawls:

```bash
curl -s "https://index.commoncrawl.org/collinfo.json"
```

- Query a crawl's index for URLs under the target domain and its subdomains:

```bash
curl -s "https://index.commoncrawl.org/<crawl_id>-index?url=*.example.com&output=json"
```

### Automating archive queries

- Querying web archives can be automated with:
	- [`waybackurls`](https://github.com/tomnomnom/waybackurls) — Retrieve URLs from the Wayback Machine for a list of domains.
	- [`waymore`](https://github.com/xnl-h4ck3r/waymore) — Retrieve URLs from the Wayback Machine, Common Crawl, AlienVault OTX, URLScan, VirusTotal, and other sources.
	- [`gau`](https://github.com/lc/gau) — Retrieve URLs from AlienVault's [Open Threat Exchange](https://otx.alienvault.com/), the Wayback Machine, Common Crawl, and URLScan.
	- [`paramspider`](https://github.com/devanshbatham/ParamSpider) — Extract URLs with parameters from the Wayback Machine (see [[Fuzzing parameters#ParamSpider]]).

```bash
waymore -i example.com -mode U --stream | sort -u
```

```bash
cat targets.txt | waybackurls > urls.txt
```

```bash
gau example.com
```

```bash
paramspider -d example.com
```

>[!note] `waybackurls` includes subdomains of the target by default (disable with `-no-subs`), while `gau` needs the `--subs` flag to include them.

- Other tools for working with web archives:
	- [`waybackrobots.py`](https://gist.github.com/mhmdiaa/2742c5e147d49a804b408bfed3d32d07) — Retrieve archived versions of a site's `robots.txt` files.
	- [`waybackpack`](https://github.com/jsvine/waybackpack) — Download every archived snapshot of a given URL from the Wayback Machine.

- Filter the collected URLs for file types that are worth reviewing, such as JavaScript files that may reference API endpoints and secrets:

```bash
grep -E '\.js(\?|$)' urls.txt | sort -u
```

>[!note] For how archived URLs are used in endpoint and subdomain discovery, see [[Directory and file enumeration#Passive reconnaissance & historical data]] and [[Subdomain enumeration#Web archives]].


## OSINT correlation tools

- Beyond individual search engines, dedicated OSINT frameworks correlate and visualize relationships between discovered entities.
- [`Maltego`](https://maltego.com/) is a link analysis platform that maps relationships between domains, IP addresses, email addresses, and organizations through automated data queries called transforms.
	- It visualizes an organization's attack surface by pivoting from a single entity to related infrastructure and associated data points.
	- A free Community Edition is available for non-commercial use.
- Other OSINT tools commonly used alongside search engine reconnaissance:
	- [`theHarvester`](https://github.com/laramies/theHarvester) — Harvest emails, subdomains, and names from public sources (see [[🛠️ Automation]]).
	- [`Amass`](https://github.com/owasp-amass/amass) and [`subfinder`](https://github.com/projectdiscovery/subfinder) — Enumerate subdomains passively (see [[Subdomain enumeration]]).

## References and further reading

- [`Conduct Search Engine Reconnaissance for Information Leakage — OWASP WSTG`](https://wstg.owasp.org/latest/4-Web_Application_Security_Testing/01-Information_Gathering/01-Conduct_Search_Engine_Reconnaissance_for_Information_Leakage/)
- [`Refine Google searches — Google Search Help`](https://support.google.com/websearch/answer/2466433)
- [`Advanced search keywords — Bing`](https://support.microsoft.com/en-us/topic/advanced-search-keywords-ea595928-5d63-4a0b-9c6b-0b769865e78a)
- [`Search Filters — Shodan`](https://www.shodan.io/search/filters)
- [`Wayback CDX Server API — Internet Archive`](https://github.com/internetarchive/wayback/tree/master/wayback-cdx-server)
