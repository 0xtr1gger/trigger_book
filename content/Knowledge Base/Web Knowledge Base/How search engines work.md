---
created: 2026-09-26
updated: 2026-09-27
tags:
  - web_knowledge_base
---
## How search engines work

- Search engines generally work in three stages, and not every page makes it through all of them:
	1. **Crawling** — Discovering which pages exist on the web and downloading their text, images, and videos with automated programs called crawlers.
	2. **Indexing** — Analyzing the content of each downloaded page and storing the results in the **index**, a large database.
	3. **Serving search results** — Querying the index and returning the most relevant pages when a user submits a query.

>[!note] See [[🛠️ Searching the web]] for how to use search engines, archives, and similar indexes for reconnaissance.

### Crawling

- There's no central registry of all web pages, so a search engine must constantly look for new and updated pages and add them to its list of known URLs. This process is called **URL discovery**.
- A search engine learns about URLs in several ways:
	- Visiting a previously indexed page to check for updates.
	- Extracting links found on known pages (for example, a category page linking to a new blog post).
	- Parsing XML sitemaps submitted by site owners, typically at `/sitemap.xml` (see [[#sitemap.xml]]).
- A page that is neither linked from other pages nor listed in a sitemap typically remains undiscovered, unless its URL appears on another crawled page.

---
- Once the engine has a list of URLs, it visits each page and processes its content. A program called a **crawler** (also **robot**, **bot**, or **spider**) does the fetching; for example, Google's crawler is **Googlebot**, and Bing's is **Bingbot**.
- The crawler uses an algorithmic process to decide which sites to crawl, how often, and how many pages to fetch from each site.
- Before fetching a page, the crawler checks the site's **`/robots.txt`** file, which specifies which paths crawlers are permitted or forbidden to access (see [[#robots.txt]]).

>[!note] Crawlers limit their request rate to avoid overloading websites. Google, for example, adjusts the rate based on the site's responses: it slows down when the server returns HTTP `500` errors.

- A crawler only reaches pages it can request anonymously. Content behind authentication, pages reachable only by submitting a form, and URLs that return errors don't get crawled.

---
- During the crawl, the engine renders the page and runs any JavaScript it finds in a **headless browser**; Google uses a recent version of Chrome.
- Rendering is necessary because modern websites often rely on JavaScript to load content dynamically; without execution, the search engine cannot parse client-rendered text or links.
- Rendering is resource-intensive, so it may occur in a separate queue after the initial HTML fetch.

### Indexing

- After a page is crawled, the search engine tries to understand what the page is about. This stage is called **indexing**. It includes processing textual content, metadata and attributes (such as `<title>` elements and `alt` attributes), and embedded media.
- Search engines typically store this data in an **inverted index**: a structure that maps each term to the documents containing it, rather than each document to its terms. This lets the engine find every page containing the query terms without scanning the pages themselves.
- Terms are indexed together with the part of the page where they appear, such as the title, URL, or body. This structure enables field-specific search operators such as `intitle:` and `inurl:`.

---
- During indexing, the search engine also determines whether a page is a duplicate of another page on the internet or the **canonical** one, which is the page that may be shown in search results.
- To select the canonical page, the engine groups (*clusters*) pages with similar content and then selects the one that's most representative of the group. The other pages in the group are alternate versions that may be served in different contexts, such as when the user searches from a mobile device or looks for a very specific page from that cluster.
- Site owners can suggest the canonical URL with a `<link rel="canonical" href="...">` element, but the engine treats it as a hint rather than a directive.
- The engine also collects **signals** about the canonical page and its content, such as language, target geographic region, and mobile usability. These signals are used in the next stage to serve the page in search results.

---
- The collected information about the canonical page and its cluster is stored in the index, which is distributed across large-scale storage systems.
- Indexing isn't guaranteed; not every page the engine processes will be indexed. Common reasons include:
	- The content of the page is low quality.
	- A robots `<meta>` tag or the `X-Robots-Tag` HTTP header disallows indexing (see below).
	- The design of the website makes indexing difficult.
- A page stays in the index until the engine recrawls it and finds that it was removed or changed. Content that the site has already deleted may therefore remain searchable for some time.

#### Indexing directives

- Site owners control indexing per page with the robots `<meta>` tag:

```html
<meta name="robots" content="noindex, nofollow">
```

- The same directives can be sent in the `X-Robots-Tag` response header, which also works for non-HTML files such as PDFs (see [[🛠️ HTTP header reference]]):

```http
X-Robots-Tag: noindex
```

| Directive   | Description |
| :---------- | :---------- |
| `noindex`   | Don't index the page (prevents the page from being displayed in search results). |
| `nofollow`  | Don't follow the links on the page. |
| `none`      | Apply both `noindex` and `nofollow`. |
| `noarchive` | Don't show a cached copy of the page in search results. Google ignores this because it stopped showing cached pages. |
| `nosnippet` | Don't show a text snippet or video preview in search results. |

>[!important] Crawling and indexing are controlled separately. `robots.txt` controls crawling, while `noindex` controls indexing:
> - A crawler must fetch a page to see its `noindex` directive, so a `noindex` page must **not** be disallowed in `robots.txt`.
> - A URL disallowed in `robots.txt` can still be indexed if other pages link to it. The engine then shows the bare URL without a description, because it never fetched the content.

### Serving search results

- When a user enters a query, the search engine queries the index for matching documents and returns the highest-quality, most relevant results.
- Relevance is determined by hundreds of factors which, depending on the engine, may include the user's location, language, and device (desktop or phone). For example, a search for "bicycle repair shops" shows different results to a user in Paris than to a user in Hong Kong.
- Results also depend on the engine's own index: each engine crawls and ranks the web independently, so the same query returns different results on different engines.

## `robots.txt`

>**[`robots.txt`](https://en.wikipedia.org/wiki/Robots.txt)** is a text file in the root directory of a website that tells web crawlers which parts of the website they may or may not crawl.

- `robots.txt` implements the [Robots Exclusion Protocol](https://www.robotstxt.org), standardized in [RFC 9309](https://www.rfc-editor.org/rfc/rfc9309.html). The protocol relies entirely on **voluntary compliance**, so some crawlers ignore it.

>[!important] `robots.txt` is not an access control mechanism. It provides **no security whatsoever**.

- The most dangerous misconception about `robots.txt` is treating it as a security feature.
- Administrators who try to hide sensitive areas in `robots.txt` inadvertently create a **treasure map for attackers**. Paths listed as `Disallow` become the first targets for manual investigation:
	- Disallowed paths often point to administrative panels, backup files, or legacy APIs that administrators want to hide from search engine crawlers.
	- Paths listed in `robots.txt`, whether allowed or disallowed, help build a map of the website and often reveal sections not linked from the main navigation.
	- Some sites use "honeypot" directories to lure malicious bots. Recognizing these traps helps avoid IP bans and defensive triggers during automated scanning.

### Location and scope

- A crawler requests `robots.txt` from the top-level path of the site: `https://example.com/robots.txt`.
- The rules apply only to the host, protocol, and port that serve the file. `https://example.com/robots.txt` does not apply to `https://dev.example.com/`, `http://example.com/`, or `https://example.com:8443/`; inspect `robots.txt` separately across all discovered endpoints.
- How crawlers handle the response:
	- **`4xx`** — The file is treated as nonexistent, and everything may be crawled. Google makes an exception for `429`.
	- **`5xx`** — The whole site is treated as disallowed. If the error persists for 30 days, crawlers may treat the file as unavailable (Google then falls back to the last cached copy or crawls without restrictions).
	- **Redirects** — Followed up to five times.
- Crawlers must parse at least the first 500 KiB of the file and should not cache it for more than 24 hours.

### Structure and syntax

- A `robots.txt` file consists of **groups**. Each group starts with one or more `User-agent` lines followed by the rules that apply to those crawlers. Lines starting with `#` are comments.

>[!example]+ Example: `robots.txt` from [`google.com/robots.txt`](https://www.google.com/robots.txt):
>
> ```text
> User-agent: *
> Disallow: /search
> Allow: /search/about
> Allow: /search/static
> Allow: /search/howsearchworks
> Disallow: /sdch
> Disallow: /groups
> Disallow: /index.html?
> ...
> ```

- **`User-agent`**: Specifies the crawler (such as `Googlebot`) that the following rules apply to. Matching is case-insensitive. A crawler obeys only the most specific group that matches it and falls back to the `*` group, which applies to all crawlers.
- **`Disallow`**: Paths or patterns that must not be crawled. An empty value allows everything, while `/` disallows the whole site.

```text
Disallow: /admin/
Disallow: /private/
```

- **`Allow`**: Paths or patterns explicitly permitted for crawling.

```text
Allow: /public/
Allow: /private/public-file.html
```

- When an `Allow` and a `Disallow` rule both match a URL, the rule with the longest (most specific) path wins. If both are equally long, `Allow` wins.
- Paths are case-sensitive and must start with `/`.

---
- The following directives aren't part of RFC 9309, but many crawlers support them.
- **`Sitemap`**: Provides the absolute URL of an XML sitemap (see [[#sitemap.xml]]). A file can list several sitemaps.

```text
Sitemap: https://example.com/sitemap.xml
```

- **`Crawl-delay`**: Sets a delay (in seconds) between requests to avoid overloading the server. Bing honors it; Google ignores it.

```text
Crawl-delay: 10
```

- Wildcards and pattern matching:

| Pattern        | Description                                         | Example             | Target paths                                                   |
| :------------- | :-------------------------------------------------- | :------------------ | :------------------------------------------------------------- |
| (none)         | Match path prefixes by default.                     | `Disallow: /admin`  | `/admin`, `/admin/`, `/admin.php`, `/administrator/`, etc.     |
| `/` (trailing) | Restrict the prefix match to a specific directory.  | `Disallow: /admin/` | The `/admin/` directory and everything under it.               |
| `*`            | Match any sequence of characters (including none).  | `Disallow: /*.pdf`  | Every URL containing `.pdf`, including `/file.pdf?download=1`. |
| `$`            | Anchor the pattern match to the end of the URL.     | `Disallow: /*.pdf$` | Only URLs ending with `.pdf`.                                  |

## `sitemap.xml`

>**`sitemap.xml`** is an XML file that provides a structured list of URLs on a website along with metadata about each URL. It helps search engines discover and index content efficiently.

- The format is defined by the [Sitemaps protocol](https://www.sitemaps.org/protocol.html).
- A sitemap acts as a table of contents for the website. This makes it valuable for reconnaissance, as it enumerates endpoints directly without requiring brute-force discovery or application spidering.

>[!example]+ Example: `sitemap.xml` from [`gitlab.com/sitemap.xml`](https://gitlab.com/sitemap.xml)
>
> ```xml
> <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
> <url>
> <loc>https://gitlab.com/explore/projects</loc>
> <lastmod>2025-10-05</lastmod>
> </url>
> <url>
> <loc>https://gitlab.com/explore/snippets</loc>
> <lastmod>2025-10-05</lastmod>
> </url>
> <url>
> <loc>https://gitlab.com/explore/groups</loc>
> <lastmod>2025-10-05</lastmod>
> </url>
> <url>
> <loc>https://gitlab.com/gitlab-org</loc>
> <lastmod>2025-10-05</lastmod>
> </url>
> <url>
> <loc>https://gitlab.com/groups/gitlab-org/-/issues</loc>
> <lastmod>2025-10-05</lastmod>
> </url>
> <url>
> <loc>https://gitlab.com/groups/gitlab-org/-/merge_requests</loc>
> <lastmod>2025-10-05</lastmod>
> </url>
> <url>
> <loc>https://gitlab.com/groups/gitlab-org/-/packages</loc>
> <lastmod>2025-10-05</lastmod>
> </url>
> ...
> </urlset>
> ```

| Element        | Required | Description                                                                      |
| :------------- | :------- | :------------------------------------------------------------------------------- |
| `<urlset>`     | Yes      | Encapsulate the file and define the XML sitemap namespace standard.              |
| `<url>`        | Yes      | Contain XML entries for an individual URL.                                       |
| `<loc>`        | Yes      | Specify the absolute URL of the page.                                            |
| `<lastmod>`    | Optional | Specify the date of last modification (in ISO 8601 format).                      |
| `<changefreq>` | Optional | Indicate how frequently the page is likely to change.                            |
| `<priority>`   | Optional | Set the priority of the URL relative to other pages on the site (`0.0` to `1.0`). |

>[!note] Google ignores `<changefreq>` and `<priority>`. It uses `<lastmod>` only when the value is consistently accurate.

### Sitemap limits and sitemap indexes

- A single sitemap may contain at most 50,000 URLs and be at most 50 MB uncompressed. Sitemaps can be gzip-compressed (`sitemap.xml.gz`).
- Larger sites split their URLs across several sitemaps and list them in a **sitemap index** file. When you find an index, fetch every sitemap it references:

```xml
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://example.com/sitemap-posts.xml</loc>
  </sitemap>
  <sitemap>
    <loc>https://example.com/sitemap-pages.xml</loc>
  </sitemap>
</sitemapindex>
```

- Besides XML, search engines also accept RSS/Atom feeds and plain-text files with one URL per line as sitemaps.
- A sitemap can only list URLs under the directory where it's hosted, unless it's submitted through the search engine's webmaster tools. A sitemap at `https://example.com/blog/sitemap.xml` covers only `/blog/`.

### Finding sitemaps

- Sitemaps don't have to be located at `/sitemap.xml`. Common places to look:
	- `Sitemap` lines in `robots.txt`.
	- `/sitemap.xml`, `/sitemap_index.xml`, and `/sitemap.xml.gz`.
	- `/wp-sitemap.xml`, the built-in sitemap of WordPress 5.5 and later.

## References and further reading

- [`In-depth guide to how Google Search works — Google Search Central`](https://developers.google.com/search/docs/fundamentals/how-search-works)
- [`RFC 9309: Robots Exclusion Protocol`](https://www.rfc-editor.org/rfc/rfc9309.html)
- [`How Google interprets the robots.txt specification — Google Search Central`](https://developers.google.com/search/docs/crawling-indexing/robots/robots_txt)
- [`Robots meta tag, data-nosnippet, and X-Robots-Tag specifications — Google Search Central`](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag)
- [`Build and submit a sitemap — Google Search Central`](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
- [`Sitemaps XML format — sitemaps.org`](https://www.sitemaps.org/protocol.html)
