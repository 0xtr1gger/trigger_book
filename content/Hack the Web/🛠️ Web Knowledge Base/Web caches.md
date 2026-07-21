---
created: 2026-05-19
tags:
  - intermediaries
  - web_knowledge_base
status: substantial
---

## Web cache

Before reaching the target server, most commonly, a request goes through a set of intermediary servers, including web caches.

>A web cache, or HTTP cache, is an intermediary system that temporarily stores copies of previously accessed HTTP responses so that subsequent requests for the same resource can be served from the stored copy rather than the origin server, reducing latency and origin server load. 

- The stored copy of a resource is referred to as a **representation** — it represents the state of the resource *at a specific point in time*.
- Cached representations eventually expire and must be either *revalidated* with the origin server or discarded. 

>[!bug] The [[Web Cache Deception|Web Cache Deception]] and [[🛠️ Web Cache Poisoning]] vulnerabilities are direct consequences of mismatches between how caches construct **cache keys**. 
## The HTTP request-response chain


1. **User request**
	- The browser constructs an HTTP request for a resource (e.g., a URL entered directly, a link clicked, or fetched by a script).

2. **Browser cache check** (private cache)
	- The browser first checks its **local cache** (on-disk and in-memory) for a *fresh* copy of the requested resource.
	- If a fresh copy exists locally, it is served immediately without sending any requests over the network. This is called a **cache hit**.

3. **CDN or shared intermediary cache**
	- If the browser cache misses (**cache miss**), the request is sent over the network to the nearest CDN edge node or shared proxy. 
	- The CDN checks whether it has a cached response for this request.
	- If yes, it responds from cache — the origin server never sees the request.

>[!note] CDN stands for Content Delivery Network. 

4. **Origin web server**
	- The origin may itself have an in-process or sidecar cache (e.g., Redis, Memcached, or a full-page cache plugin) to serve frequently accessed dynamic content without hitting the database.
	- If every upstream cache misses, the request reaches the origin. 
	- The application executes business logic, queries a data store, and generates a response. 

5. **Caching and response**
	- The response is sent back through the chain and gets cached at each eligible layer along the way before it finally reaches the user's browser.

## Cache classification

### By access scope

#### Private caches

>A **private cache** is a cache dedicated to a single client. 

- A private cache stores responses intended for a single user and **must not be shared** with other users or stored in shared caches like proxy servers or CDNs.
- The responses it stores may contain sensitive or user-specific data, such as credentials or user preferences.
- The most common example of a private cache is the **browser cache**. 

>[!important]+ The **`Cache-Control: private` directive** instructs intermediate proxy servers and CDNs that a response **must not be stored in a shared cache** (but still can be stored in a private cache).

#### Shared caches

>A **shared cache** is a cache that stores HTTP responses for multiple distinct clients. 

- A shared cache is deployed as an intermediary between a client and server. Examples include CDN edge notes (Cloudflare, Akamai, Fastly), corporate proxy severs, and reverse proxies. 
- Shared caches must not store personalized or sensitive data, because the response may be returned to any client whose request generates the same cache key.
- By default, shared caches will not store responses to requests with the `Authorization` heder, assuming that such responses are user-specific. 

>[!important] The `Cache-Control: public` directives explicitly instructs caches that this response can be stored publicly (even if it would otherwise be non-cacheable, *including* requests with the `Authorization` header).

### By operational location
### Forward caches

>A **forward cache** is deployed on the **client side** of the network, outside the origin server's infrastructure. 

- Browser caches are the primary example. Corporate HTTP proxies that cache content for an entire organization also function as forward caches. 
- These caches serve the interests of **clients** — reducing bandwidth consumption and improving response times.
### Reverse caches

>A **reverse cache** is deployed on the server side of the network, in front of the origin server, and appears to clients as though it were the origin.

- CDNs are the most common example — a global network of edge servers that cache origin responses and serve them to geographically proximate clients.
- Reverse proxies such as **Varnish**, **Nginx**, **Squid**, and **AWS CloudFront** sit between the internet and the origin. Their caching logic is configured *independently* of the origin server's `Cache-Control` headers (which is a common source of configuration mismatches).
## Cache decision matrix

When a cache receives a request, it analyzes it to decide whether and how to store the response. 

A typical cache processes an incoming request as follows:

1. **Check request method**
	- Is the request method **[cacheable](https://developer.mozilla.org/en-US/docs/Glossary/Cacheable)** — `GET` or `HEAD`?
	- Methods like `PUT` or `DELETE` are **not cacheable**, i.e., their result must not be cached.
	- A response to a `POST` or `PATCH` request can be cached if freshness is indicated and the `Content-Location` header is set (but this is rarely implemented).

>[!important] To be cached, a response must have a **cacheable status code**. The following status codes are cacheable: `200`, `203`, `204`, `206`, `300`, `301`, `404`, `405`, `410`, `414`, and `501`.

>[!note] See [`Cacheable — mdn web docs`](https://developer.mozilla.org/en-US/docs/Glossary/Cacheable).

2. **Apply cache rules**
	- Some cache servers are configured to automatically store specific types of responses, such as those requested with a static file extension in the URL (`.css`, `.js`, `.png`, `.jpg`, etc.).

3. **Evaluate cache headers**
	- Does the request contain headers that prevent serving a cached response?
	- For example, `Cache-Control: no-cache` instructs the server to revalidate before serving; `Pragma: no-cache` is an older equivalent. 
	- A request with `Authorization` will typically bypass shared caches unless the response carries `Cache-Control: public`.

4. **Generate a cache key**
	- The cache computes a key from the eligible components of the request. The key is used to look up stored entries.
	- See [[#Cache keys]].

5. **Cache lookup**
	- The cache checks its store for a response that matches the generated key.
		- **Cache hit** — a stored response exists. Proceed to evaluate its *freshness*.
		- **Cache miss** — no stored response. Forward the request to the origin. Store the response if cacheable.

6. **Evaluate freshness** (on hit)
	- Is the cached response still fresh?
	- The cache compares the response's age against its freshness lifetime. If fresh, serve it immediately. If stale, proceed to revalidation.

7. **Revalidation** (on stale hit)
	- The cache server sends a *conditional request* to the origin using a `If-Nonce-Match` (ETag-based) or `If-Modified-Since` (timestamp-based) header. 
	- If the origin responds `304 Not Modified`, refresh the stored entry's TTL and serve it. If the origin responds `200 OK`, replace the stored entry with the new response.

8. **Decide whether to store the response** (on miss)
	- Evaluate the response headers to determine whether the response is cacheable, such as the presence of `Cache-Control` directives (`no-store`, `private`), response status code, content type, and CDN-specific configuration rules.

>[!note] CDNs frequently override this standard logic with configuration rules that prioritize file extensions, URL patterns, or custom headers over the origin's `Cache-Control` headers. For example, a CDN may cache any URL ending in `.css` or `.js` regardless of the origin's directive — a behavior that becomes exploitable if an attacker can make the origin serve a sensitive response on a URL that matches a static file pattern.
>


## Cache key and cache storage

### Cache keys

> A **cache key** is a deterministic identifier generated from a subset of an HTTP request's components, used by a cache to index stored responses and to decide whether an incoming request can be satisfied from cache without contacting the origin server.

- The cache doesn't store the raw HTTP request itself; instead, it computes a cache key from selected fields of the request.
- Two requests that produce identical cache keys are treated as equivalent; the cache returns the same stored response for both, regardless of any differences in the fields not included in the key.
---
- Cached responses are stored as key-value pairs:

```
cache_key → { response_headers, response_body, metadata }
```

- When a new request arrives, the cache computes its cache key and checks if it has a stored response for **the same key**:
	- If yes (there's a cached response corresponding to the same key), returns the cached response immediately — **cache hit**.
	- If no, it forwards the request to the origin server, caches the response if cacheable, and returns it to the client — **cache miss**.

### Cache key construction

- By default, most caches include the following in the cache key:
	- **URL scheme** (e.g., `http://`, `https://`)
	- **`Host` header**
	- **URL path** (normalized)
	- **Query string** (parameters are often included selectively)
	- **Specific headers** (specified in the `Vary` header)
	- **TCP port** (if non-standard)

>[!important] Headers specified in the origin's `Vary` response header are also included in the cache key.

- Everything else — request headers not listed in `Vary`, request body, cookies (unless specified in `Vary`), and most metadata — is **unkeyed**.

>[!example]+
> - Consider two requests:
> 
> ```http
> GET /profile?id=123 HTTP/1.1
> Host: example.com
> ```
> 
> ```http
> GET /profile?id=456 HTTP/1.1
> Host: example.com
> ```
> 
> These produce **different** cache keys because the query string differs. 
> 
> - Consider another two requests:
> 
> ```http
> GET /profile?id=123 HTTP/1.1
> Host: example.com
> User-Agent: Mozilla/5.0 (Windows NT 10.0)
> ```
> 
> ```http
> GET /profile?id=123 HTTP/1.1
> Host: example.com
> User-Agent: curl/7.88.1
> ```
> 
> These produce **identical** cache keys if `User-Agent` is not listed in `Vary`. The cache treats them as the same request and returns the same response to both — regardless of any backend logic that differs based on `User-Agent`.
### Keyed vs. unkeyed inputs

> A **keyed input** is any component of an HTTP request that is included in the cache key and therefore influences which cached response is returned.

> An **unkeyed input** is any component of an HTTP request that is excluded from the cache key but that may nevertheless influence the response generated by the origin server.

>[!bug] If a user-controlled input (e.g., a query parameter or HTTP header) influences the server response but is not included in the cache key, this leads to [[Web Cache Deception|Web Cache Deception]] and [[🛠️ Web Cache Poisoning]] vulnerabilities.

### The `Vary` header

>The **`Vary` response header** specifies a set of request headers whose values the cache server should include in the cache key.  

>[!example]+
> ```http
> Vary: Accept-Encoding, Cookie
> ```
> 
> This directive instructs every downstream cache to include the values of the `Accept-Encoding` and `Cookie` request headers in their cache keys.
> - The same URL with different `Accept-Encoding` values (`gzip` vs. `br`) will result in two separate cache entries — the compressed response is not returned to a client that cannot decompress it.
> - The same URL with different `Cookie` values — including session cookies — will be cached separately, too.

>[!important] **`Vary: *`**  indicates the response is **uncacheable by any shared cache**, regardless of other headers — the response varies in ways the cache cannot predict or key on.

- Headers commonly included in `Vary`:
	- `Accept-Encoding` — Different clients support different compression algorithms.
	- `Accept-Language` — Localized responses differ per language preference.
	- `Cookie` — Session-specific responses differ per user.
	- `Authorization` — Authenticated responses are user-specific.
	- `User-Agent` — Device-specific responses (mobile vs. desktop).

>[!note] See [`Vary — mdn web docs`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Vary).

>[!warning] If the origin generates different responses based on session cookies (e.g., logged-in vs. anonymous views) but does not include `Cookie` in `Vary`, a shared cache may serve one user's session-specific response to a completely different user who hits the same cache key. See [[Web Cache Deception|Web Cache Deception]].
## Cache hit ratio

The **cache hit ratio** is the proportion of requests satisfied from cache without contacting the origin:


$$
\text{Cache hit ratio} = \frac{\text{Cache hits}}{\text{Cache hits + Cache misses}}
$$


The hit ratio serves as primary indicator of cache effectiveness.

- **Overly strict keys** (too many components included in the key) -> low hit ratio, because minor variations in requests produce different keys. This reduces the risk of serving one user's response to another, but reduces caching effectiveness.

- **Overly broad keys** (too few components included in the key) -> high hit ratio, because many different requests map to the same key. This is more efficient but more dangerous — it increases the risk of serving one user's response to another, or of a poisoned response being served widely.
## Cache normalization rules

- Caches frequently normalize request components before computing the cache key.
- Normalization is intended to increase cache hit ratio by treating slightly different but semantically equivalent requests as identical. 
- However, normalization discrepancies between the cache and the origin server can create paths to exploitation.


| Operation                         | Before                     | After                 |
| --------------------------------- | -------------------------- | --------------------- |
| URL decode percent-encoding       | `/path%2fto/file`          | `/path/to/file`       |
| Resolve dot-segments              | `/app/../admin`            | `/admin`              |
| Case normalization of scheme/host | `HTTPS://Example.COM`      | `https://example.com` |
| Strip default ports               | `example.com:443`          | `example.com`         |
| Remove duplicate slashes          | `//api//v1`                | `/api/v1`             |
| Sort query parameters             | `?b=2&a=1`                 | `?a=1&b=2`            |
| Strip tracking parameters         | `?utm_source=chatgpt&id=5` | `?id=5`               |

>[!bug] If the cache normalizes `/path%2fto/resource` to `/path/to/resource` but the origin server processes `%2f` literally (treating it as a path separator only after decoding), the cache key may map to a different origin-side resource than the cache expects. This is the foundation of some path-based [[Web Cache Deception]] attacks.
## Cache control

- Cache control mechanisms define:
	- **Where** a response can be stored (private vs. shared).
	- **How long** a response remains valid without revalidation (*freshness*).
	- **When** a cached response must be validated before serving.
	- **When** a cached entry must be discarded.

- These properties are communicated through HTTP headers, primarily `Cache-Control`.
### Freshness 

>**Freshness** is the property of a cached response that indicates whether the response is still valid and can be served to clients without contacting the origin server. 

- A ***fresh*** response is one that has an age less than its freshness lifetime.
- A ***stale*** response is one that has an age equal to or greater than its freshness lifetime; it requires either revalidation or discarding before it can be served (unless overridden by directives such as `stale-while-revalidate`).

- To determine whether a cached resource is fresh, the cache compares the **age** of the response and its **freshness lifetime**.
	- **Response age** is the time elapsed since the response was *generated* by the origin server (not since the cache received it). The generation time is indicated by the the `Date` response header.
	- **Freshness lifetime** is the maximum age before the response is considered stale.
- The **freshness lifetime** of a resource can be specified in HTTP headers with either:
	- `Cache-Control: max-age` or `s-maxage`
		- Indicates the maximum number of seconds the response is still considered fresh.
	- `Expires`
		- Specifies an exact date and time where the resource expires. After that time, the resource is considered stale. 
- The `Age` response header is typically added by the cache server, and indicates the number of seconds that have elapsed since the origin server generated the response.
#### The `Cache-Control` header: `max-age` and `s-maxage`

> The **`Cache-Control`** response header carries directives that define caching policy for both private and shared caches. It overrides the `Expires` header when both are present.

- `max-age=N`
	- The maximum number of seconds after the response's generation time during which the response is considered fresh. It applies to all caches — private and shared.
	- For example, `max-age=3600` means the response is fresh for one hour from the moment the origin generates it (counts from the timestamp in the `Date` header).
	- If set to `-1` or a non-integer value, this means `max-age` is not defined.

```HTTP
Cache-Control: max-age=3600, public
```

- `s-maxage=N`
	- Same as `max-age` but applies **only to shared caches**. 
	- Private caches (browsers) ignore the `s-maxage` directive entirely. 
	- When both are present, `s-maxage` takes precedence over `max-age` for shared caches.

```http
Cache-Control: max-age=600, s-maxage=3600
```

>[!note] See [`Cache-Control — mdn web docs`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cache-Control).

- Both `max-age` and `s-maxage` can be combined with other `Cach-Control` directives, such as `immutable`:

```http
Cache-Control: public, max-age=86400, s-maxage=604800, immutable
```

- Important `Cache-Control` (response) directives:

| Directive          | Indicates that... / Description                                                                                                                |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `max-age=N`        | The response remains fresh until `N` seconds after the response is generated; applies to both private and public caches.                       |
| `s-maxage`         | Same as `max-age`, but applies **only to public caches**, overrides `max-age` for public caches if both are present.                           |
| `public`           | The response can be stored in a shared cache.<br>                                                                                              |
| `private`          | The response can be stored **only in a private cache** (e.g., local caches in browsers).                                                       |
| `no-store`         | Any caches of any kind (private or shared) should not store this response.                                                                     |
| `no-cache`         | Thee response can be stored in caches, but it must be validated with the origin server before each reuse.                                      |
| `must-revalidate`  | The response can be stored in caches and be reused while fresh; if it becomes stale, it must be validated with the origin server before reuse. |
| `proxy-revalidate` | Same as `must-revalidate`, but applies to shared caches only.                                                                                  |
| `immutable`        | The response will not be updated while it's fresh.                                                                                             |
| `no-transform`     | Any intermediary shouldn't transform the response content (by default, they may).                                                              |

>[!note] `public` overrides the default cache behavior so that responses to requests with the `Authorization` header will be stored in a shared cache.
#### The `Expires` header

>The **`Expires`** response header indicates the absolute date and time at which the stored response transitions from fresh to stale.

```http
Expires: Fri, 13 Jun 2025 11:02:00 GMT
```

- `0` represents a date in the past, e.g., that the resource has already expired; the cache must revalidate it before serving.

```http
Expires: 0
```

>[!note] See [`Expires — mdn web docs`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Expires).

>[!note] If neither `max-age` nor `Expires` is present, caches may estimate freshness based on other headers like `Last-Modified`. For example, a cache may consider a response fresh for 10% of the time since the response was last modified.
#### The `Age` header

> The **`Age`** response header, typically set by an intermediate cache, indicates the number of seconds that have elapsed since the origin server generated the response.


```HTTP
Age: 0
```

- An `Age` of `0` indicates the cache just fetched the response form the origin; you are the first client to receive it from the cache.
- In practice, this means that either you triggered a cache miss or the cache is freshly populated.

```http
Age: 3247
```

- An `Age` value greater than zero confirms you are receiving a cached response. 
- The value `3247` means the cache has held this response for approximately 54 minutes.


>[!tip]+  To determine whether a cached response is still fresh given `Age`, compute:
> 
> ```
> Remaining freshness = max-age - Age
> ```
> - If this value is positive, the response is fresh. If zero or negative, the response is stale and requires revalidation.

>[!note] See [`Age — mdn web docs`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Age).

#### Heuristic freshness

- When a response carries no explicit freshness directives — no `Cache-Control: max-age`, no `s-maxage`, no `Expires` — a cache may still decide to store and serve it based on **heuristic freshness** estimation.

- The most common heuristic uses the `Last-Modified` header: 

```
Freshness lifetime = (Date − Last-Modified) × 0.1
```

- For example, if a resource was last modified 10 days ago, the heuristic assigns a freshness lifetime of 1 day. The logic is that a resource unchanged for a long period is unlikely to change soon.
- This behavior is specified in [`RFC 9111`](https://www.rfc-editor.org/rfc/rfc9111.html) and is implemented by most HTTP/1.1-compliant caches. It means that even resources without explicit `Cache-Control` headers can end up cached — a fact with security implications when you assume a response is never cached simply because it lacks `Cache-Control`.

### Cache validation

- Once a cached response becomes stale, the cache does not immediately discard it. Instead, it sends a **conditional request** to the origin server to determine whether the resource has changed.
- If the resource is unchanged, the origin sends a `304 Not Modified` response with no body — the cache refreshes its entry's TTL without re-downloading the content.
- If the resource has changed, the origin sends a `200 OK` with the new content.

- There are two independent validation mechanisms, each uses a different type of resource identifier:
	- `Last-Modified` + `If-(Un)Modified-Since`
	- `ETag` + `If-None-Match`

>[!note] But `ETags` provide a more precise validation than `Last-Modified` and support strong and weak validation.
#### `Last-Modified` + `If-(Un)Modified-Since`

>The **`Last-Modified`** response header contains the date and time at which the origin server last modified the resource.

>The `If-Modified-Since` and `If-Unmodified-Since` request headers are used in conditional requests to determine whether the requested resource has been (`If-Modified-Since`) or hasn't been (`If-Unmodified-Since`) modified after the date specified in the header.

**Validation flow using `Last-Modified`:**

1. **Initial response from origin:**

	```http
	HTTP/1.1 200 OK
	Last-Modified: Thu, 12 Jun 2025 10:00:00 GMT
	Cache-Control: max-age=3600
	```
	
	- The cache stores the response along with the `Last-Modified` timestamp.

2. After the response becomes stale, the cache sends a **conditional request**:

	```http
	GET /resource HTTP/1.1
	Host: example.com
	If-Modified-Since: Thu, 12 Jun 2025 10:00:00 GMT
	```

	- **Origin — resource unchanged**:

	```http
	HTTP/1.1 200 OK
	Last-Modified: Fri, 13 Jun 2025 08:30:00 GMT
	Cache-Control: max-age=3600
	[new response body]
	```

	- **Origin — resource changed:**

	```http
	HTTP/1.1 304 Not Modified
	Cache-Control: max-age=3600
	```

- `If-Unmodified-Since` is the inverse conditional — the server processes the request only if the resource has **not** been modified since the given date. 
- `Last-Modified` is a coarse validator. Its precision is limited to one-second granularity, and it is an estimate — origin servers often report the filesystem modification time of the backing file, which may not accurately reflect meaningful content changes (e.g., a file touched by a deployment script may have an updated `Last-Modified` without any content change).

>[!note]+ See:
> - [`Last-Modified — mdn web docs`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Last-Modified)
> - [`If-Modfied-Since — mdn web docs`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/If-Modified-Since)
> - [`If-Unmodified-Since — mdn web docs`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/If-Unmodified-Since)
> 
#### `ETag` + `If-None-Match`

> An **`ETag`** (entity tag) is an opaque string assigned by the origin server to a specific version of a resource. It serves as a precise, content-based cache validator. 

- An `Etag` can be **strong** or **weak**:
	- A **strong `ETag`** (e.g., `"v2-a8f3c9b1"`) guarantees byte-for-byte identity.
	- A **weak `ETag`** (prefixed `W/`, e.g., `W/"v2-a8f3c9b1"`) indicates semantically equivalent but not byte-identical content.

> The **`If-None-Match`** request header, included in a conditional request, carries one or more `ETag`s and instructs the server to return the full resource only if its current ETag does not match any of the provided values.

- ETags solve the precision problems of `Last-Modified`. The server generates an ETag from the resource's actual content (typically a hash or a version identifier), so two versions of a resource with different content will always have different `ETag`s, even if the timestamp is the same.

**Validation flow using `ETag`s:**

1. **Initial response from origin:**

```http
HTTP/1.1 200 OK
ETag: "v2-a8f3c9b1"
Cache-Control: max-age=3600
```

2. After the response becomes stale, the cache sends a **conditional request**:

	```http
	GET /resource HTTP/1.1
	Host: example.com
	If-None-Match: "v2-a8f3c9b1"
	```
	
	- **Origin — resource unchanged:**
	
	```http
	HTTP/1.1 304 Not Modified
	ETag: "v2-a8f3c9b1"
	Cache-Control: max-age=3600
	```
	
	- **Origin — resource changed:**
	
	```http
	HTTP/1.1 200 OK
	ETag: "v3-c7d2e4f6"
	Cache-Control: max-age=3600
	[new response body]
	```

>[!note] The `If-None-Match` header uses a **weak comparison** algorithm by default, meaning `W/"v2-a8f3c9b1"` and `"v2-a8f3c9b1"` are considered a match. Strong comparison (requiring byte-identical content) is used by `If-Match`.

- A client or cache can supply **multiple `ETag`s** in the `If-None-Match` header separated by commas, representing multiple versions it has stored. The server matches against all of them:

```http
If-None-Match: "v2-a8f3c9b1", "v1-003f21bc", W/"v0-da9fb2"
```

- If any `ETag` matches the current resource version, the server responds with `304` and the `Etag` of the valid resource.  

>[!note]+ See:
> - [`ETag — mdn web docs`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/ETag)
> - [`If-None-Match — mdn docs`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/If-None-Match)

### Cache invalidation

> **Cache invalidation** is the process by which stored cache entries are marked stale and are either removed from the cache store or revalidated before serving.

- Invalidation may occur **automatically** or **manually**.

- **Automatic invalidation triggers:**
	- **Freshness expiry** — when `max-age` or `s-maxage` is exceeded, the entry is considered stale and subject to revalidation or discarding, depending on the cache's configuration and presence of `must-revalidate`.
	- **Unsafe HTTP methods** — `POST`, `PUT`, `DELETE`, and `PATCH` requests to a given URL cause most caches to invalidate any stored response for that URL. The assumption is that a write operation changed the resource, making the cached version stale.
	- **`no-store` directive** — responses carrying this directive are never stored. If previously cached entries exist, some cache implementations will remove them when they encounter this directive.
	- **`no-cache` directive** — does not remove stored entries but requires revalidation before every serve. Effectively makes every serve a conditional request.

- **Manual invalidation — cache purging:**

	- CDN operators and reverse proxy administrators can issue purge commands to explicitly remove cache entries. Cloudflare, Fastly, Akamai, and similar platforms expose APIs and dashboard controls for purging by URL, tag, or cache key prefix.
## References and further reading

- [`Cacheable — mdn web docs`](https://developer.mozilla.org/en-US/docs/Glossary/Cacheable)

- [`HTTP caching — mdn web docs`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching)
- [`What is caching? — Cloudflare`](https://www.cloudflare.com/learning/cdn/what-is-caching/)
- [`Cache Keys — Cloudflare Docs`](https://developers.cloudflare.com/cache/how-to/cache-keys/)

Headers:
- [`Cache-Control — mdn web docs`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cache-Control)
- [`Expires — mdn web docs`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Expires)
- [`Age — mdn web docs`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Age)
