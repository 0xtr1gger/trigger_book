---
created: 2026-07-18
tags:
  - recon
  - web_hacking
status: substantial
---
## `robots.txt`

>**[`robots.txt`](https://en.wikipedia.org/wiki/Robots.txt)** is a text file placed in the root directory of a website that contains instructions for web crawlers about which parts of the website should or should not be indexed. 

- `robots.txt` implements the [Robots Exclusion Protocol](https://www.robotstxt.org), which relies entirely on **voluntary compliance** (meaning, some crawlers may ignore it).

>[!important] `robots.txt` is not an access control mechanism. It provides **no security whatsoever**.

- The most dangerous misconception about `robots.txt` is treating it as a security feature. 
- By attempting to hide sensitive areas in that file, administrators inadvertently create a **treasure map for attackers**. Paths listed as `Disallow` become the first targets for manual investigation.
	- Disallowed paths often point to administrative panels, backup files, or legacy APIs that administrators intentionally want to hide from search engine crawlers.
	- Paths listed in `robots.txt`, whether allowed or disallowed, help build a website's map and often reveal sections not linked from the main navigation.
	- Some sites use "honeypot" directories to lure malicious bots. Recognizing these traps helps you avoid IP address bans during automated scanning.
### Structure and syntax

- A `robots.txt` file consists of entries targeting specific user-agents. Each entry provides directives.

>[!example]+ Example: `robots.txt` from [`google.com/robots.txt`](https://www.google.com/robots.txt):
>
> ```
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

- **`User-agent`**: Specifies the bot (such as `Googlebot`) the instructions below apply to; the wildcard `*` applies to all crawlers. 
- **`Disallow`**: Paths or patterns that should not be crawled or indexed.

```PowerShell
Disallow: /admin/
Disallow: /private/
```

- **`Allow`**: Paths or patterns explicitly permitted for crawling and indexing (overrides `Disallow`).

```PowerShell
Allow: /public/
Allow: /private/public-file.html
```

- **`Sitemap`**: Provides the location of an XML sitemap (`sitemap.xml`).

```PowerShell
Sitemap: https://example.com/sitemap.xml
```

- **`Crawl-delay`**: Sets a delay (in seconds) between requests to avoid overloading the server.

```PowerShell
Crawl-delay: 10
```

- Wildcards and pattern matching:

| Pattern | Meaning                             | Example             | Blocks                                          |
| ------- | ----------------------------------- | ------------------- | ----------------------------------------------- |
| `*`     | Matches any sequence of characters. | `Disallow: /*.pdf`  | All PDF files.                                  |
| `$`     | End-of-URL anchor.                  | `Disallow: /*.pdf$` | URLs ending exactly with `.pdf`.                |
| `/`     | Path separator.                     | `Disallow: /admin/` | `/admin/` directory and all its subdirectories. |

## `sitemap.xml`

>**`sitemap.xml`** is an XML file that provides a structured list of URLs on a website along with metadata about each URL. It helps search engines discover, understand, and index content efficiently. 

- A sitemap acts as a table of contents. It's useful for reconnaissance, too, since it lists website endpoints explicitly, saving you the trouble of brute-forcing or spidering the application manually to find them.


>[!example]+ Example: `sitemap.xml` from [`gitlab.com/sitemap.xml`](https://gitlab.com/sitemap.xml)
> 
> ```xml
> <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
> <SCRIPT id="allow-copy_script"/>
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
> ```

| Element        | Required | Description                                                                      |
| -------------- | -------- | -------------------------------------------------------------------------------- |
| `<urlset>`     | Yes      | Root element; defines the sitemap protocol namespace.                            |
| `<url>`        | Yes      | Parent tag for each URL entry.                                                   |
| `<loc>`        | Yes      | The actual URL of the page.                                                      |
| `<lastmod>`    | Optional | Date of the last modification.                                                   |
| `<changefreq>` | Optional | How frequently the page is likely to change.                                     |
| `<priority>`   | Optional | Priority relative to other URLs on the website (`0.0` to `1.0`; default: `0.5`). |
## Well-Known URIs (`/.well-known/`)

> The **`.well-known`** directory is a standardized URL prefix defined in [RFC 8615](https://datatracker.ietf.org/doc/html/rfc8615). It provides a consistent location on web servers to host site-wide metadata, configuration files, and information required by various web protocols.

- The standard makes it easier to discovery critical services and configurations. The directory itself is typically located in the root directory of a website (e.g., `https://example.com/.well-known`).
- The IANA (Internet Assigned Numbers Authority) maintains a [registry of `.well-known` URIs](https://www.iana.org/assignments/well-known-uris/well-known-uris.xhtml).

### Notable `.well-known` locations


| File                         | Description                                                                                                                                   |
| :--------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------- |
| `security.txt`               | Contact information for security researchers to report vulnerabilities. (e.g., `/.well-known/security.txt`).                                  |
| `change-password`            | Standard URL directing users to a password change page.                                                                                       |
| `assetlinks.json`            | Used for verifying ownership of digital assets (e.g., mobile apps) associated with a domain.                                                  |
| `terraform.json`             | Reveals Terraform Cloud/Enterprise endpoints and API versions.                                                                                |
| `mta-sts.txt`                | Mail Transfer Agent (MTA) Strict Transport Security (STS) policy, including `MX` records.                                                     |
| `openid-configuration`       | OpenID Connect provider configuration; exposes authorization endpoints, token endpoints, supported scopes, JWKs URI, issuer information, etc. |
| `oauth-authorization-server` | OAuth 2.0 authorization server metadata; reveals OAuth endpoints, supported grand types, token endpoint authentication methods, etc.          |
| `oauth-protected-resource`   | OAuth 2.0 protected resource metadata; identifies resource server capabilities and requirements.                                              |
### `openid-configuration`

- One of the most valuable well-known URIs during a penetration test is `/.well-known/openid-configuration`. It defines configuration details for OpenID Connect, an identity layer built on top of the OAuth 2.0 protocol.

- This is a JSON document that lists the authentication provider's endpoints, supported methods, and cryptographic keys:

```json
{
  "issuer": "https://example.com",
  "authorization_endpoint": "https://example.com/oauth2/authorize",
  "token_endpoint": "https://example.com/oauth2/token",
  "userinfo_endpoint": "https://example.com/oauth2/userinfo",
  "jwks_uri": "https://example.com/oauth2/jwks",
  "response_types_supported": ["code", "token", "id_token"],
  "scopes_supported": ["openid", "profile", "email"],
  "id_token_signing_alg_values_supported": ["RS256"]
}
```

>[!note] See [[OAuth attacks]].

## References and further reading

- [`Introduction to robots.txt — Google Search Central`](https://developers.google.com/search/docs/crawling-indexing/robots/intro)
- [`Learn about sitemaps — Google Search Central`](https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview)

- [`robots.txt — Wikipedia`](https://en.wikipedia.org/wiki/Robots.txt)
- [`Well-known URI — Wikipedia`](https://en.wikipedia.org/wiki/Well-known_URI)
