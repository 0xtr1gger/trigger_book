---
created: 2026-01-11
tags:
  - recon
  - OSINT
status: incomplete
---
## Search engine operators 

- Operators for different search engines:
	- [`Search Operators | Brave Search`](https://search.brave.com/help/operators)
	- [`Search Operators | DuckDuckGo Search`](https://help.duckduckgo.com/duckduckgo-help-pages/results/syntax/)
	- [`Search Operators | Bing`](https://help.bing.microsoft.com/#apex/bing/en-us/10001/-1)
	- [`Search Opeartors | Google`](https://docs.google.com/document/d/1ydVaJJeL1EYbWtlfj9TPfBTE5IBADkQfZrQaBZxqXGs/edit?tab=t.0)

- Google dorks for different purposes:
	- [`Google Hacking Database (GHDB) - Exploit-DB`](https://www.exploit-db.com/google-hacking-database)
	- [`Bug Bounty Helper`](https://dorks.faisalahmed.me/)
	- [`google-dorks-bug-bounty`](https://github.com/TakSec/google-dorks-bug-bounty)
	- [`google-dorks`](https://github.com/Proviesec/google-dorks)
	- [`TUXCMD/Google-Dorks`](https://github.com/TUXCMD/Google-Dorks-Full_list/blob/master/googledorks_full.md)
	- [`Pentest Tools - Google Hacking`](https://pentest-tools.com/information-gathering/google-hacking)
	- [`DorkSearch.com`](https://dorksearch.com/)

>[!note] Google may [censor](https://en.wikipedia.org/wiki/Censorship_by_Google) certain search results, which may hinder investigations; it's advised to appeal to privacy-respecting alternatives, as they provide more or less generic results for all users (and not based on your previous activity).

## Search operators

| Operator                | Description                                                                                 | Example                                                                                                              |
| :---------------------- | :------------------------------------------------------------------------------------------ | :------------------------------------------------------------------------------------------------------------------- |
| `site:`                 | Limits results to a specific domain.                                                        | `site:example.com`<br>Searches for pages only on `example.com`.                                                      |
| `inurl:`                | Searches for pages with a specific term in the URL.                                         | `inurl:login`<br>Finds pages with `login` in URL.                                                                    |
| `filetype:`             | Limits results to files of a specific type.                                                 | `filetype:pdf`<br>Searches for PDFs.                                                                                 |
| `intitle:`              | Searches for pages with a specific term in the title.                                       | `intitle:"report"`<br>Searches for documents with `report` in the title.                                             |
| `intext:`               | Searches for pages with a specific term within the page body.                               | `intext:"password reset"`<br>Searches for pages containing the term `password reset`.                                |
| `cache:`                | Displays Google's cached version of a webpage. Useful for viewing deleted content.          | `cache:example.com/page.html`  <br>Shows Google's cached version of the page.                                        |
| `link:`                 | Finds pages that link to a specific URL (deprecated/limited functionality).                 | `link:example.com`  <br>Finds pages linking to example.com.  <br>**Google has largely deprecated this.**             |
| `related:`              | Finds websites similar or related to a specified URL.                                       | `related:example.com`  <br>Finds similar websites to example.com.                                                    |
| `define:`               | Provides definitions from various sources.                                                  | `define:phishing`  <br>Shows definitions of phishing.                                                                |
| `numrange:`             | Searches for pages with numbers withing a specific range.<br>Synonym: `..` (range search).  | `site:example.com numrange:1000-2000`<br>Find pages on `example.com` that contain numbers between `1000` and `2000`. |
| `before:`               | Limits results to pages indexed before a specific date. <br>Format: `YYYY-MM-DD`.           | `before:2020-01-01`  <br>Pages indexed before January 1, 2020.                                                       |
| `after:`                | Limits results to pages indexed after a specific date. <br>Format: `YYYY-MM-DD`.            | `after:2024-01-01`  <br>Pages indexed after January 1, 2024.                                                         |
| `allintext:`            | Searches for pages containing **all** specified terms in the body text.                     | `allintext:admin password reset`  <br>All three terms must appear in page body.                                      |
| `allinurl:`             | Searches for pages containing **all** specified terms in the URL.                           | `allinurl:"admin login php"`  <br>All three terms must be in URL.                                                    |
| `allintitle:`           | Searches for pages containing **all** specified terms in the title.                         | `allintitle:"private documents confidential"`  <br>All terms must be in title.                                       |
| `AND`                   | Boolean `AND` operator: both terms must be present (default behavior, can be omitted).      | `security AND vulnerability`  <br>Both terms must appear.                                                            |
| `OR`                    | Boolean `OR` operator: either term must be present. Must be uppercase.                      | `site:example.com (inurl:admin OR inurl:login)`  <br>Finds either admin or login URLs.                               |
| `NOT`                   | Boolean `NOT` operator: excludes term from results; synonym: `-` (minus sign).              | `security NOT firewall`  <br>Same as `security -firewall`                                                            |
| `-` (minus sign)        | Excludes terms from search results. No space between minus and term (alternative to `NOT`). | `security -firewall`  <br>Results about security excluding firewall.  <br>`site:example.com -inurl:blog`             |
| `*` (wildcard)          | Placeholder for any word or phrase. Useful for pattern matching.                            | `"admin * panel"`  <br>Matches `admin control panel`, `admin user panel`, etc.                                       |
| `" "` (quotation marks) | Searches for exact phrase match. Very important for precision.                              | `"powered by WordPress"`  <br>Exact phrase must appear.                                                              |
| `+` (plus sign)         | Forces inclusion of common words Google usually ignores (deprecated).                       | `+login`  <br>Now largely obsolete.                                                                                  |
| `..` (range search)     | Searches for numbers within a range (alternative to `numrange:`).                           | `site:example.com 100..200`<br>Find pages on `example.com` that contain numbers between `100` and `200`.             |
| `define:`               | Provides definitions from various sources.                                                  | `define:phishing`  <br>Shows definitions of phishing.                                                                |
| `info:`                 | Displays information Google has about a URL.                                                | `info:example.com`  <br>Shows cached, similar, and linked pages.                                                     |
| `weather:`              | Shows weather for a location.                                                               | `weather:London`  <br>Displays London weather.                                                                       |
| `in`                    | Converts units.                                                                             | `50 km in miles`  <br>Converts kilometers to miles.                                                                  |
| `source:`               | Searches within Google News sources.                                                        | `election source:reuters`  <br>News about elections from Reuters.                                                    |
| `()` (parentheses)      | combinations of search terms                                                                | `(site:example.org \| site:example.com) & filetype:pdf`                                                              |
