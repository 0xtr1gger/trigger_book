---
created: 2026-07-18
status: substantial
updated: 2026-09-30
tags:
  - web_hacking
  - intel
proofread: yes
---
## `robots.txt`

![[How search engines work#robots.txt]]

## `sitemap.xml`

![[How search engines work#sitemap.xml]]

## Well-known URIs (`/.well-known/`)

> **`/.well-known/`** is a standardized URL path prefix defined in [RFC 8615](https://datatracker.ietf.org/doc/html/rfc8615). It provides a consistent location on web servers to host site-wide metadata, configuration files, and information required by various web protocols.

- The standard makes it easier to discover services and configurations. The `.well-known` directory is usually located at the web root (e.g., `https://example.com/.well-known/`).
- The Internet Assigned Numbers Authority (IANA) maintains a [registry of `.well-known` URIs](https://www.iana.org/assignments/well-known-uris/well-known-uris.xhtml).

### Notable `.well-known` locations

| URI suffix | Description |
| :--- | :--- |
| `security.txt` | Contact information for security researchers to report vulnerabilities. |
| `change-password` | URL that redirects users to the site's password change page. |
| `assetlinks.json` | Digital Asset Links file used to verify ownership of digital assets (e.g., mobile apps) associated with a domain. |
| `terraform.json` | Terraform remote service discovery document listing Terraform Cloud/Enterprise endpoints and API versions. |
| `mta-sts.txt` | Mail Transfer Agent (MTA) Strict Transport Security (STS) policy, including the permitted MX hosts. |
| `openid-configuration` | OpenID Connect provider configuration that exposes the authorization and token endpoints, supported scopes, the JWKS URI, the issuer identifier, etc. |
| `oauth-authorization-server` | OAuth 2.0 authorization server metadata that reveals the OAuth endpoints, supported grant types, token endpoint authentication methods, etc. |
| `oauth-protected-resource` | OAuth 2.0 protected resource metadata that describes the resource server's capabilities and requirements. |

### `openid-configuration`

- One of the most valuable (from the security perspective) well-known URIs is `/.well-known/openid-configuration`. It exposes the configuration of an OpenID Connect provider. 
- It is a JSON document that lists information about the identity provider, such as supported signing algorithms and scopes:

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
>[!note] OpenID Connect is an identity layer built on top of the OAuth 2.0 authorization framework.

- The document is useful during reconnaissance because it discloses:
	- **Endpoints** (`authorization_endpoint`, `token_endpoint`, `userinfo_endpoint`): lists the URLs used in authentication.
	- **`jwks_uri`**: the location of the provider's public signing keys, which matters when analyzing how ID tokens and access tokens are signed and validated.
	- **`response_types_supported`**: OAuth flows the identity provider supports, such as the implicit flow (`token`, `id_token`).
	- **`scopes_supported`**: supported scopes, i.e., the user data the provider can release and the access levels it can grant.
- The related `/.well-known/oauth-authorization-server` URI ([RFC 8414](https://datatracker.ietf.org/doc/html/rfc8414)) exposes equivalent metadata for OAuth 2.0 authorization servers that do not implement OpenID Connect.

>[!note] These endpoints are a starting point for reconnaissance only. For ways to abuse the disclosed configuration, see [[OAuth attacks]].

## Other interesting files

>[!note] See [[Directory and file enumeration]].

- **Version control and source code**
	- `.git/` — an exposed Git repository. Its object store can be reconstructed into the complete source tree and commit history, which makes it one of the highest-impact findings.
	- `.svn/`, `.hg/`, `.bzr/` — Subversion, Mercurial, and Bazaar metadata directories (can be reconstructed in the same way as `.git/`).
	- `.DS_Store` — macOS Finder metadata that records the file names of the containing directory, which may expose locations not linked anywhere.
- **Configuration and secrets**
	- `.env` — an environment file read by many frameworks at startup; it commonly stores database credentials, API keys, and application secrets.
	- `.htaccess`, `.htpasswd` — Apache files: `.htaccess` list per-directory configuration, and `.htpasswd` stores the usernames and password hashes for HTTP Basic Authentication (both are `403 Forbidden` by default).
	- `web.config` — the IIS and ASP.NET configuration file; it can expose connection strings, framework settings, and internal file paths.
	- `wp-config.php`, `config.php` — application configuration files that hold database credentials and secret keys.
	- `phpinfo.php` — a page that calls PHP's `phpinfo()` and dumps the PHP version, loaded modules, and server environment variables.
- **Dependency manifests**
	- `package.json`, `composer.json`, `Gemfile`, `requirements.txt`, `pom.xml` — manifests that declare the project's libraries and their versions (lock-files); this information can be useful to identify knwon vulnerabilities.
- **Backup, temporary, and archive files**
	- `.bak`, `.old`, `.orig`, `.save`, `~`, `.swp` — backup copies and editor swap files. The server often returns them as plain text instead of executing them, which can sometimes expose the application source code.
	- `.zip`, `.tar.gz`, `backup.sql`, `db.sql` — archives and database dumps left in the web root; they may contain the entire application or its data.
- **Cross-domain policies**
	- `crossdomain.xml` — an Adobe Flash cross-domain policy file. Permissive rules such as `allow-access-from domain="*"` let Flash content hosted on other domains read the site's responses.
	- `clientaccesspolicy.xml` — the Microsoft Silverlight equivalent, prone to the same class of misconfiguration.
- **CI/CD and container files**
	- `Dockerfile`, `docker-compose.yml` — container build and orchestration files that reveal base images, service layout, and sometimes hardcoded secrets.
	- `.gitlab-ci.yml`, `.github/workflows/`, `Jenkinsfile` — CI/CD pipeline definitions that expose build steps, internal hostnames, and occasionally credentials.
- **Documentation and metadata**
	- `README`, `CHANGELOG`, `LICENSE`, `INSTALL` — documentation files that identify the software and its version, and often describe the default configuration or setup steps.
	- `humans.txt` — an optional credits file that lists the staff and tools behind the site.

## References and further reading

- [`Introduction to robots.txt — Google Search Central`](https://developers.google.com/search/docs/crawling-indexing/robots/intro)
- [`Learn about sitemaps — Google Search Central`](https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview)

- [`robots.txt — Wikipedia`](https://en.wikipedia.org/wiki/Robots.txt)
- [`Well-known URI — Wikipedia`](https://en.wikipedia.org/wiki/Well-known_URI)
