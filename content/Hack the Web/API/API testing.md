---
created: 2026-07-14
tags:
  - api_testing
  - web_hacking
status: incomplete
---

>[!info] **API (Application Programming Interface)** is a set of rules, protocols, and definitions that allows different software components to communicate, exchange data, and request services from one another. It acts as a **defined contract** or interface that specifies how requests must be formatted, what information is exchanged, and how responses are returned.

>[!note] See [`OWASP Top 10 API Security Risks — 2023 — OWASP API Security Top 10`](https://owasp.org/API-Security/editions/2023/en/0x11-t10/).
## API reconnaissance

- API reconnaissance objectives:
	- List of **endpoints**
	- List of **parameters** each endpoint accepts
	- Accepted HTTP methods
	- Request formats (headers, query parameters, body structure)
	- Response formats (status codes, data types, error formats)
	- Authentication methods
	- Rate-limiting

### Discovering API documentation

- Documentation is the fastest way to mapping an API's attack surface. 
- Even if you can't find documentation published online, it can often be exposed by the API server itself.
#### Enumerating API documentation endpoints

>[!note]+ API subdomains
Many organizations host separate domains specifically dedicated for API services. They're often overlooked, but may expose sensitive endpoints not found anywhere else. See [[Subdomain enumeration]].

- Fuzzing wordlist: [`Hacking-APIs/api_docs_path`](https://github.com/hAPI-hacker/Hacking-APIs/blob/main/api_docs_path).
- Common paths to check:

```PowerShell
/docs
/api/docs
/apidocs
/api-docs
/api-docs.yaml
/api-docs.json
/api/apidocs/swagger.json

/api/v1
/v1
/api/v1/docs
/v1/docs

/api/v2
/v2
/api/v2/docs
/v2/docs

/docs/swagger
/swagger/index.html
/swagger.json
/swagger.yaml
/swagger.yml
/api/swagger/index.html
/api/swagger.json
/api/swagger.yaml
/api/swagger.yml
/api/swagger/ui/index
/api/swagger/v1/swagger.json
/swagger-ui

/docs/openapi
/openapi
/openapi.json
/openapi.yaml
/openapi.yml

/developer
/static/api-docs
/cdb/api-docs
/schema
/redoc
/graphql
```

>[!tip] If you've already found an API endpoint, walk up the path toward the root (e.g., if you found `/api/swagger/v1/users/11`, check `/api/swagger/v1`, `/api/swagget`, and `/api`). API documentation is often mounted at the API root.

>[!note] For GraphQL testing, see [[GraphQL attacks]].
> 
#### Other sources of API documentation

- **Developer portals** — Dedicated developer portals with API documentation, such as [Swagger UI](https://swagger.io/tools/swagger-ui/) or Redoc.
- **API marketplaces**:
	- [`SwaggerHub`](https://app.swaggerhub.com/search)
	- [`Postman Public API Network`](https://www.postman.com/explore)
	- [`RapidAPI`](https://rapidapi.com/)
- **Source code repositories** — Public GitHub/GitLab repositories with API documentation, Postman collections, API client SDKs, etc.
- **Google dorking**:

```powershell
site:example.com filetype:json openapi
site:example.com inurl:swagger
site:github.com "example.com" postman_collection
```

- **Web archives** — [`WaybackMachine`](https://web.archive.org/).
- **Bug bounty write-ups** — If the target runs a public program, prior disclosed reports may include references to documentation or otherwise undocumented information on discovered API endpoints.

>[!tip]+ Search other subdomains for documentation 
> ```
> https://docs.example.com/
> https://dev.example.com/docs
> https://developer.example.com/docs
> https://api.example.com/docs
> https://api.com/developers/documentation
> ``` 

>[!note] Some Burp Suite extensions can dynamically generate API docs from intercepted traffic, such as [`API Exporter`](https://github.com/portswigger/api-exporter) (available in both Burp Community).




### Interacting with API endpoints

- Interact with identified API endpoints to observe API behavior and discover additional attack surface. 

>[!important] As you interact with the API endpoints, review error messages and other responses closely for any useful information on the intended request format and other details.

#### Identifying supported HTTP methods

- An **HTTP method** (verb) specifies the action requested against a resource.
- An API endpoint may support different HTTP methods. It's advised to test all methods against all target endpoints.

|  Method   | Description                                                                                                                                                                          |             Idempotent?              |                Safe?                 |
| :-------: | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------: | :----------------------------------: |
|   `GET`   | Retrieves a resource representation. <br>Safe, idempotent, and cacheable. <br>No state modification is expected.                                                                     | <span style="color:#44B7B7">✔</span> | <span style="color:#44B7B7">✔</span> |
|  `HEAD`   | Retrieves response headers for the target resource without a message body.<br>Commonly used for metadata validation and cache validation. <br>Safe and idempotent.                   |   <span style="color:red">✘</span>   | <span style="color:#44B7B7">✔</span> |
|  `POST`   | Submits data for resource-specific processing.<br>Commonly used to create subordinate resources or invoke non-idempotent operations (state changes).<br>Not safe and not idempotent. | <span style="color:#44B7B7">✔</span> |   <span style="color:red">✘</span>   |
|   `PUT`   | Creates or completely replaces the representation of the target resource. <br>Idempotent by definition.                                                                              | <span style="color:#44B7B7">✔</span> |   <span style="color:red">✘</span>   |
| `DELETE`  | Removes the target resource. <br>Idempotent (although repeated requests may return different status codes after the resource is deleted).                                            |   <span style="color:red">✘</span>   |   <span style="color:red">✘</span>   |
| `CONNECT` | Establishes a tunnel to the target server; typically used for HTTP(S) proxies.                                                                                                       |   <span style="color:red">✘</span>   |   <span style="color:red">✘</span>   |
| `OPTIONS` | Retrieves the communication options and supported methods for the target resource. <br>Frequently used for CORS preflight requests. <br>Safe and idempotent.                         | <span style="color:#44B7B7">✔</span> | <span style="color:#44B7B7">✔</span> |
|  `TRACE`  | Performs a diagnostic loop-back of the request message. <br>Intended for debugging and commonly disabled for security reasons.<br>Safe and idempotent.                               | <span style="color:#44B7B7">✔</span> | <span style="color:#44B7B7">✔</span> |
|  `PATCH`  | Applies a partial modification to a resource. <br>Typically not idempotent (although idempotent implementations are permitted).                                                      |   <span style="color:red">✘</span>   |   <span style="color:red">✘</span>   |

- A method is **idempotent** if making multiple identical requests produces the same server state as making a single request.
- A method is **safe** if it doesn't alter the state of the server or cause side effects beyond logging and statistics. In other words, a method is safe if it leads to a read-only operation.

>[!burp] To automatically cycle through a list of standard HTTP methods, you can use the built-in **HTTP verbs** list.

>[!info] **Verb tampering** is a technique where an attacker changes the HTTP method of a request in an attempt to bypass access controls or trigger different, less-restricted server-side logic than the one bound to the originally intended verb.

- Access controls are sometimes implemented per-verb rather than per-endpoint. For example, a reverse proxy blocks `POST /admin/users` for non-admins but never checks `PATCH` or `PUT` against the same path, because the developer assumed only `POST` would ever be used to reach that code.

>[!warning] When fuzzing methods, target low-value, disposable objects. `DELETE`, `PUT`, and `PATCH` mutate state and may result in permanent data loss.
#### Identifying supported content types

- API endpoints often expect data in a specific format and may behave differently depending on the content type provided in a request.
- Changing `Content-Type` may trigger errors that disclose useful information bypass flawed defenses, or even cause different processing logic.

```http
POST /api/profile HTTP/1.1
Content-Type: application/json

{"name":"peter"}
```

```http
POST /api/profile HTTP/1.1
Content-Type: application/xml

<name>peter</name>
```

>[!tip] To fuzz through `Content-Type` values, you can use the [`Discovery/Web-Content/web-all-content-types.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/web-all-content-types.txt) wordlist ([`SecLists`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/web-all-content-types.txt)).

>[!tip] You can use the [`Content type converter`](https://portswigger.net/bappstore/db57ecbe2cb7446292a94aa6181c9278) BApp to automatically convert data submitted within requests between XML and JSON.

### Enumerating hidden endpoints

- Once you have discovered a set of initial endpoints, you can fuzz for hidden endpoints using wordlists of common known paths or application-specific keywords you discovered during recon.
- [`actions.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/api/actions.txt) — Starting from an initial endpoint (e.g., `PUT /api/users/update`), enumerate API actions:

```bash
ffuf -u https://api.example.com/api/users/FUZZ -w /usr/share/wordlists/SecLists/Discovery/Web-Content/api/actions.txt -X PUT -ic -c
```

- [`objects.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/api/objects.txt) — Enumerate API objects:

```bash
ffuf -u https://api.example.com/api/FUZZ -w /usr/share/wordlists/SecLists/Discovery/Web-Content/api/objects.txt -X PUT -ic -c
```

-  [`api-endpoints.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/api/api-endpoints.txt) — General API endpoint enumeration (for discovering initial paths):

```bash
ffuf -u https://api.example.com/api/users/FUZZ -w /usr/share/wordlists/SecLists/Discovery/Web-Content/api/actions.txt -X PUT -ic -c
```

>[!note] See [`SecLists/Discovery/Web-Content/api`](https://github.com/danielmiessler/SecLists/tree/master/Discovery/Web-Content/api) for more API-related wordlists.

>[!important] Generic wordlists find generic endpoints. Complement those with keywords found in the application or API paths (or related to them) during reconnaissance.
>>[!example] If the applications works with `orders`, also fuzz `cancel`, `refund`, `ship`, `void`, etc. If it's a CMS, fuzz `publish`, `draft`, `revert`.
### Finding hidden parameters

- Fuzzing — Replace or append parameter names from a curated list (e.g., [`burp-parameter-names.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/burp-parameter-names.txt)) and compare the response to the baseline (length/status/timing).
- The [`Param miner`](https://portswigger.net/bappstore/17d2949a985c4b7ca092728dba871943) Burp extension automatically guesses **up to 65,536 parameter names per request**, and tailors its guesses using terms found in the target application source code (in-scope JS/HTML).
- The [`Content discovery`](https://portswigger.net/burp/documentation/desktop/tools/engagement-tools/content-discovery) tool (Burp Professional only) engine recursively probes for pages not linked from visible content, including query parameters.
- [`s0md3v/Arjun`](https://github.com/s0md3v/Arjun) is a standalone tool for discovering hidden parameters:

```bash
# scan a single endpoint (GET)
arjun -u https://api.example.com/endpoint
```

```bash
# POST request
arjun -u https://api.example.com/endpoint -m JSON
```

```bash
# JSON body
arjun -u https://api.example.com/endpoint -m JSON  
```

```bash
# specify custom headers
arjun -u https://api.example.com/endpoint --headers "Accept-Language: en-US\nCookie: null" 
```

## Mass assignment vulnerabilities 

>**Mass assignment** (also called auto-binding) is a vulnerability in which an application automatically maps incoming request parameters directly onto the fields of an internal data object — without properly validating which fields the user is permitted to set — such that an attacker can influence object fields the developer never intended to expose as user input.

- Many web frameworks (such as Spring, Rails, Django REST Framework, ASP.NET, and Express applications using an ORM) automatically deserialize request bodies into model objects by matching parameter names to object fields.
- Auto-binding is not inherently vulnerable on its own. The vulnerability arises when the application doesn't verify which properties can actually be modified by a user.
- In this case, you may be able to modify sensitive fields (e.g., `isAdmin`, `role`, `verified`, `subscriptionTier`, or `accountBalance`) to bypass access controls or otherwise cause an application to behave in unintended way — once you've discovered valid parameter names.

>[!bug]+ Labs
>- [[🛠️ API testing labs#4. Exploiting a mass assignment vulnerability]]

### Identifying hidden parameters

- Mass assignment requires knowledge of server-side property names. 
- One of the most reliable ways to discover them is to compare the read and write representations of the same resource.

>[!example]+
> - Say, a legitimate update request might look like this:
> 
> ```http
> PATCH /api/users/11
> ...
> 
> {
>     "username": "jane",
>     "email": "jane@example.com"
> }
> ```
> 
> - A `GET` request to the same resource returns:
> 
> ```http
> GET /api/users/11
> ```
> 
> ```http
> HTTP/1.1 200 OK
> ...
> 
> {
>     "id": 11,
>     "username": "jane",
>     "email": "jane@example.com",
>     "isAdmin": false
> }
> ```
> 
> - The `id` and `isAdmin` properties exist on the server-side object but are absent from the legitimate write request. These become candidates for mass-assignment testing.

>[!note] A field appearing in a response only proves that it exists on the server-side object. It does not prove that the field is writable. Each candidate must be tested individually.

- Alternatively, you can try brute-forcing potential properties — this works if the application provides any signals that indicate whether a specific tested property exists. 
- However, this may potentially break functionality and disrupt the application work — if you accidentally alter critical parameters.
### Testing for mass assignment

- Once you've identified a candidate property, test if you can modify it.

1. **Add the property set to its current value**
	- A successful response indicates that the additional property is accepted syntactically, but not necessarily processed.
	
```json
{
	"username": "jane",
	"email": "jane@example.com",
	"isAdmin": false
}
```

2. **Replace the value with an invalid type**
	- If the application returns a validation error, different status code, or otherwise changes its behavior, the property is likely being bound and validated rather than ignored.
	- If both requests produce identical responses, the parameter may simply be discarded.

```json
{
	"username": "jane",
	"email": "jane@example.com",
	"isAdmin": "invalid"
}
```

3. **Attempt exploitation**
	- Submit the desired value and observe application behavior.

```json
{
	"username": "jane",
	"email": "jane@example.com",
	"isAdmin": true
}
```

>[!note] A `200 OK` response does not guarantee that the property was updated, as many APIs silently ignore unauthorized or unknown fields.

- Independently verify whether the state actually changed by retrieving the object again or, for example, attempting a privileged action (depends on which parameters you attempted to modify).

## Server-side parameter pollution

>**Server-side parameter pollution (SSPP)** occurs when a front-end application incorporates user-controlled input into a server-side request to an internal API without proper validation and encoding. An attacker can then inject, modify, truncate, or override parameters in the internal request, potentially altering application behavior or gaining unauthorized access to restricted functionality.

>[!note] SSPP is sometimes referred to as _HTTP parameter pollution_, although that term is also used for a client-side WAF bypass technique involving duplicate parameters. It is also unrelated to **server-side prototype pollution**, despite the similar name.

- To test for SSPP, inject query syntax characters (`#`, `&`, `=`) in the query string and observe how the application responds.

>[!example]+
> - Consider a public endpoint:
> 
> ```bash
> GET /userSearch?name=jane&back=/home
> ```
> 
> - The is internally converted to:
> 
> ```bash
> GET /users/search?name=jane&publicProfile=true
> ```
> 
> The goal is to determine whether the `name` parameter is copied directly into the internal query string.

>[!note] The examples were adapted from [`Server-side parameter pollution — PortSwigger Web Security Academy`](https://portswigger.net/web-security/api-testing/server-side-parameter-pollution).
### Truncating parameters

- **Attempt to truncate the internal query string using a URL-encoded `#` (`%23`)**:

```bash
GET /userSearch?name=jane%23injected&back=/home
```

- If incorporated directly, the internal request becomes:

```bash
GET /users/search?name=peter#injected&publicProfile=true
```

>[!important] The `#` must be URL-encoded (`%23`). Otherwise, the browser interprets it as a fragment and  never sends to the server.

### Injecting invalid parameters

- **Attempt to inject an invalid parameter using a URL-encoded `&` (`%26`)**:

```bash
GET /userSearch?name=jane%26injected=arbitrary&back=/home
```

- Internal request:

```bash
GET /users/search?name=jane&injected=arbitrary&publicProfile=true
```

- An unchanged response often indicates that the injected parameter reached the internal API but was ignored because it is not recognized.
- Although not directly exploitable, this confirms that query-string injection is possible.

### Injecting valid parameters


- If you're able to modify the query string, **attempt to inject a valid parameter to the server-side request**:

```bash
GET /userSearch?name=jane%26email=example&back=/home
```

- Internal request:

```bash
GET /users/search?name=jane&email=example&publicProfile=true
```

- Observe whether the application's behavior changes. A different response indicates that the injected parameter is recognized by the backend API.

### Overriding existing parameters

- Attempt to inject a second instance of an existing parameter:

```bash
GET /userSearch?name=jane%26name=john&back=/home
```

- Internal request:

```bash
GET /users/search?name=jane&name=john&publicProfile=true
```

- The result depends on how duplicate parameters are handled (whether the server respects the first or the second parameter). Typical behavior:

| Platform          | Typical behavior                                                                                                                |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| PHP               | Last value wins.                                                                                                                |
| ASP.NET           | Values are concatenated.                                                                                                        |
| Node.js / Express | First value wins.                                                                                                               |
| Java Servlet APIs | `getParameter()` commonly returns the first value;<br>`getParameterValues()` returns all values; framework behavior may differ. |
- If the backend honors the injected value, it may become possible to override parameters such as usernames, account identifiers, or access-control flags.
## References and further reading

- [`OWASP Top 10 API Security Risks — 2023 — OWASP API Security Top 10`](https://owasp.org/API-Security/editions/2023/en/0x11-t10/)
- [`Web Security Academy alignment with the OWASP Top 10 API vulnerabilities — PortSwigger Web Security Academy`](https://portswigger.net/web-security/api-testing/top-10-api-vulnerabilities)
- [`API Recon with Kiterunner - Hacker Toolbox — InsiderPhd, YouTube`](https://www.youtube.com/watch?v=hNs8fpWfcyU)
- [`How To Do Recon: API Enumeration — InsiderPhD, YouTube`](https://www.youtube.com/watch?v=fvcKwUS4PTE&list=PLbyncTkpno5EHe1jhC-ZuqZwrDoRTx4HV&index=2)


- [`Mass Assignment Cheat Sheet — OWASP Cheat Sheet Series`](https://cheatsheetseries.owasp.org/cheatsheets/Mass_Assignment_Cheat_Sheet.html)
- [`Mass assignment — snyk learn`](https://learn.snyk.io/lesson/mass-assignment/?ecosystem=javascript)

- [`Server-side parameter pollution — PortSwigger Web Security Academy`](https://portswigger.net/web-security/api-testing/server-side-parameter-pollution)