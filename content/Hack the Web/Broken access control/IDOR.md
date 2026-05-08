---
created: 2026-05-03
tags:
  - web_hacking
---
## IDOR

> **Insecure Direct Object Reference (IDOR)** is a class of broken access control vulnerability that arises when an application uses attacker-controllable input to construct a reference to an internal object — such as a database record, file, or resource — and grants access to that object without performing adequate per-object, per-user authorization verification.
 
- IDOR vulnerabilities occur when a web application exposes a **direct reference** to an internal object in a user-controlled parameter, such as a user ID, object ID, file name, or session identifier, and grants access to that resource **without actually verifying if the given user is authorized to access it**.

- This means that an attacker can manipulate the exposed reference to **access, modify, or delete resources** they weren't supposed to interact with. 

>[!note] IDOR is one of the most widespread vulnerabilities found in the wild. See [`A01:2025 — Broken Access Control — OWASP Top 10 2025`](https://owasp.org/Top10/2025/A01_2025-Broken_Access_Control/).

>[!example]+
> Suppose a user accesses their profile a URL like this:
> 
> ```
> https://example.com/users/1209
> ```
> 
> An attacker simply changes the numeric identifier to see if they can access other user accounts:
> 
> ```
> https://target.com/account/1211
> ```
> **If the application returns the profile for user `1211`, this is an IDOR.**
> 
>-  Here, `1211` is a **direct reference** to the database record where user information is stored; this might often be a database primary key.
>- The application doesn't really check if the **current authenticated user** (based on their session ID or authentication token) is authorized to access that user `1211`. 
>- It's a matter of simply changing the identifier in the URL to gain unauthorized access to other accounts. 
> 
> In Python, vulnerable code might look like this:
> 
> ```python
> @app.get("/account/{user_id}")
> async def get_user_by_id(user_id: int):
> 	user = db.query(User).filter(User.id == user_id).first()
> 	if user is None:
> 		raise HTTPException(status_code=404, detail="User does not exist")
> 	return user
> ```
> 
> - The application retrieves the user object from the database without any validation of who is trying to access the account — only whether this account exists.
>
>
>Here is a better version, with an authorization check added:
> 
> ```Python
> @app.get("/account/{user_id}")
> async def get_user_by_id(user_id: int, current_user: User = Depends(get_current_user)):
>     user = db.query(User).filter(User.id == user_id).first()
>     if user is None:
>         raise HTTPException(status_code=404, detail="User does not exist")
>     if user.id != current_user.id:  # authorization check
>         raise HTTPException(status_code=403, detail="Access denied")
>     return user
> 
> ```

>[!note]+ IDOR is fundamentally a **missing authorization check**, not a missing authentication check. Authentication confirms who you are; authorization confirms what you're allowed to do.
> See [[🛠️ Authentication on the web]].
## Root cause analysis

IDOR vulnerabilities result from the combination of **four key factors**:

- **Direct object references** in user-controlled parameters
	- The application directly exposes references to backend objects without any intermediate abstraction layer. 
	- Instead of using indirect references or access tokens, objects are referenced by internal identifiers, such as raw database IDs or file names.

- **Insufficient input validation**
	- The application fails to validate or sanitize user-supplied input before using it to reference objects. Any value the user provides is **trusted implicitly**.

- **Missing per-object authorization**
	- The server performs authentication (validates the session or token), then fetches the object identified by the user-supplied reference **without performing per-object authorization checks**.
	- This primarily stems from the assumption that users won't ever discover references to other objects.

>[!note] Developers often rely solely on session states, such as "this user is logged in", rather than actually checking resource ownership for every action.

- **Predictable object references**
	- The referenced object identifiers are either sequential, algorithmically predictable, or can be leaked from another part of the application.

>[!note] Developers frequently believe that unpredictable IDs (UUIDs, hashes) prevent IDOR. This is a misconception. Unpredictable IDs reduce _discoverability_, but they don't eliminate the vulnerability — if the authorization check is absent, a UUID is just as exploitable as an integer, provided the attacker can obtain it through any other means (API leakage, enumeration of a secondary endpoint, referrer headers, etc.).

>[!example]- Example: Missing per-object authorization — Python, Flask
> 
> - Vulnerable code:
> 
> ```Python
> @app.get('/api/users/{user_id}')
> def get_user_data(user_id: int, request: Request):
> 
> 	# only checks if the current user is logged in, not if they're authorized to access the resource
> 	if not request.user.is_authenticated:
> 		return jsonify({'error': 'Unauthorized'}), 401
> 		
> 	user = db.query(User).filter(User.id == user_id).first()
> 	if user: # checks if the user with the given ID exists
> 		return {
> 			"id": user.id,
> 			"name": user.name,
> 			"email": user.email,
> 			"api_token": user.api_token # sensitive API key
> 		}
> 
> 	return jsonify({'error': 'User not found'}), 404
> ```
> 
> 
> - A more secure version:
> 
> ```Python
> @app.get('/api/users/{user_id}')
> def get_user_data(user_id: int, request: Request):
> 
> 	# checks if the current user is logged in
> 	if not request.user.is_authenticated:
> 		return jsonify({'error': 'Unauthorized'}), 401
> 		
> 	user = db.query(User).filter(User.id == user_id).first()
> 	# checks if the current user has the same ID as the user who's account their're trying to access OR if the user has admin privileges:
> 	if request.user.id != user_id or requeset.user.role != 'admin':
> 		return jsonify({'error': 'Forbidden'}), 403
> 	
> 	if user: # checks if the user with the given ID exists
> 		return {
> 			"id": user.id,
> 			"name": user.name,
> 			"email": user.email,
> 			"api_token": user.api_token # sensitive API key
> 		}
> 
> 	return jsonify({'error': 'User not found'}), 404
> ```
> - The second example has a per-object authorization check added — not just authentication check as in the first example. 

## Attack surface

- IDORs can be present anywhere user-controlled input is used to reference a backend object.

### Commonly vulnerable parameters

| Location                    | Example                                              |
| --------------------------- | ---------------------------------------------------- |
| URL path segment            | `GET /users/1209/profile`                            |
| URL query string            | `GET /messages?inbox_id=5571`                        |
| POST body (JSON)            | `{"user_id": 1209, "action": "delete"}`              |
| POST body (XML)             | `<userId>1209</userId>`                              |
| POST body (form)            | `user_id=1209&submit=1`                              |
| Hidden HTML form field      | `<input type="hidden" name="order_id" value="8821">` |
| Cookie                      | `user_id=1209` stored in cookie                      |
| Custom HTTP header          | `X-User-ID: 1209`                                    |
| Authorization token payload | JWT `sub` claim, API key embedded with user ID       |
| File path/name              | `GET /files/invoice_user1209.pdf`                    |
| AJAX request body           | `$.ajax({ data: { uid: user.uid } })`                |
>[!example]+ Example: Ajax call with exposed ID
> 
> ```JavaScript
> function changeUserPassword() {
>     $.ajax({
>         url:"change_password.php",
>         type: "post",
>         dataType: "json",
>         data: {
> 	        uid: user.uid, 
> 	        password: user.password, 
> 	        is_admin: is_admin
> 	    },
>         success:function(result){
>             // handle result
>         }
>     });
> }
> ```
> 
> The `uid` parameter is directly exposed in the client-side JavaScript and sent to the server.

>[!tip]+ Carefully inspect HTML, JavaScript, and API calls vulnerable parameters.

>[!tip]+ Single-page applications (SPAs) may store IDs in JavaScript or expose them in API calls, which only makes discovery and exploitation easier.


### Object types

- The referenced object doesn't have to be a user account. Any application-managed resource can be an IDOR target:
	- User accounts and profiles
	- Private messages and chat threads
	- Documents, reports, invoices, contracts
	- Orders, transactions, payment records
	- API keys and access tokens
	- Admin configuration objects
	- File uploads and attachments
	- Notification and subscription objects
	- Session and audit log records

> [!tip] IDORs are especially common in APIs 
> - REST API endpoints directly map HTTP verbs and URL paths to CRUD operations on backend objects.
> - Developers frequently skip authorization logic under the false assumption that API traffic is hidden from end users.
> - A proxy like Burp Suite makes all API traffic visible and modifiable.
### Identifier types and encoding 

Exposed references take many forms, such as:

- **Numeric IDs** (simplest and most common)
	- Decimal: `1209`, `1210`, `1211`, etc.
	- Hexadecimal: `4b9`, `4ba`, `4bb`, etc.
	- Unix epoch timestamps (such as resource creation timestamps): `1695574808`, `1695575098`, etc.
- **String and semantic identifiers**
	- Usernames: `john`, `sherlock`, etc.
	- Email addresses: `john@email.com`, etc.
	- Human-readable slugs: `quarterly-report-q3-2026`, etc.
- **Encoded values**
	- Base64: `c2hlcmxvY2s=`
- **Boolean values**
	- `0` or `1`
	- `True`/`true`/`TRUE` or `False`/`false`/`FALSE`
	- `yes`/`no`
- **Weak hashes**
	- MD5: `88b95871316b2b8797f61d87182be195`
	- SHA1: `04fb5abd938165a8febcfb98cc641303ff25a8b0`
- **File names**
	- `report_001.pdf`
	- `invoice_11222025.pdf`
- **Session identifiers**
	- Custom session tokens
- **UUIDs/GUIDs**
	- `550e8400-e29b-41d4-a716-446655440000`

#### Numeric IDs

The simplest and most common form. Usually auto-incremented database primary keys.

- Decimal: `1209`, `1210`, `1211`
- Hexadecimal: `0x4b9`, `0x4ba`
- Unix timestamps (used as creation-time IDs): `1695574808`

Sequential integers make enumeration trivial — one request per ID. Even with gaps from deleted records, a linear scan will hit live records consistently.
#### Encoded identifiers

- Identifiers are commonly encoded or serialized for transfer purposes or sometimes obfuscation.

- Base64 is the most frequently encountered encoding:

```
c2hlcmxvY2s=  →  sherlock
```

General approach to encoded IDs:

1. Intercept a request containing an encoded parameter.
2. Identify the encoding (e.g., Base64 has padding `=` padding and alphanumeric + `/+` charset).
3. Decode using [CyberChef](https://gchq.github.io/CyberChef/), [Burp Decoder](https://portswigger.net/burp/documentation/desktop/tools/decoder), or other tools (e.g., the `base64 -d` command).
4. Modify the underlying value (e.g., change user ID from `1209` to `1211`).
5. Re-encode.
6. Re-submit the modified request.

>[!example]+
> - Decode: 
> 
> ```bash
> echo "c2hlcmxvY2s=" | base64 -d
> ```
> ```bash
> sherlock
> ```
> 
> - Encode:
> 
> ```bash
> echo -n "watson" | base64
> ```
> ```bash
> d2F0c29u
> ```

#### Hashed identifiers

- Hashing algorithms, including MD5 and SHA1, are commonly used to "protect" identifiers. D
- Despite the widespread understanding that [MD5](https://en.wikipedia.org/wiki/MD5) has been cryptographically [broken since 2004](https://en.wikipedia.org/wiki/MD5#History_and_cryptanalysis), it still appears in production code.
- Use [CrackStation](https://crackstation.net/) or [`hashes.com`](https://hashes.com/en/decrypt/hash) to attempt to recover the original plaintext for common hashes. 

>[!example]+
> - You discover a hash in a parameter value:
>```
>?id=7e7e69ea3384874304911625ac34321c
>```
>- A string of 32 seemingly random hex characters — this resembles MD5. Crack it using [CrackStation](https://crackstation.net/) and retrieve the original value: `1209`.
>
>![[IDOR_crackstation.png]]
>- Then increment the ID and compute its hash:
> ```bash
> echo -n "1211" | md5sum
> # output: 285ab9448d2751ee57ece7f762c39095
> ```
> 
> - Submit `?id=285ab9448d2751ee57ece7f762c39095` and observe the response.

>[!tip]+
> - To identify an unknown hash type offline:
> 
> ```bash
> hashid '7e7e69ea3384874304911625ac34321c'
> ```

#### UUIDs and GUIDs

`550e8400-e29b-41d4-a716-446655440000` — these are 128-bit pseudo-random identifiers. Version 4 UUIDs are cryptographically unpredictable, but:

- Earlier UUID versions (v1, v2) are partially time-based and predictable.
- Even random UUIDs can be _leaked_ from other parts of the application — API responses that list resource IDs, referrer headers, error messages, JavaScript source.
- The IDOR vulnerability exists regardless of whether the UUID is guessable; if you obtain it through any means, the missing authorization check is still exploitable.

> [!note] A UUID is an _entropy_ countermeasure, not an _authorization_ countermeasure. They solve different problems. A UUID without an authorization check is still a vulnerability.


## Testing Methodology

>[!quote] IDORs can not be detected by tools alone. IDORs require creativity and manual security testing to identify them. While some scanners might detect activity, it takes a human eye to analyze, evaluate, and interpret. In traditional pentests, unless a pentester tests every possible parameter in every request endpoint, these vulnerabilities can go undetected.
>- [`The Rise of IDOR — HackerOne, 2021`](https://www.hackerone.com/company-news/rise-idor)

>[!important]+ Multiple accounts
> Before any testing begins:
> - **Create at least two test accounts** at the same privilege level (`User A`, `User B`). This lets you generate real object IDs without touching other users' data, observe application behavior from both sides, and confirm exploitation without impacting live user data.
> - If the application has distinct roles, create accounts for each role tier (regular user, moderator, admin if possible).
### 1. Identify vulnerable parameters

- The goal is to identify every place in the application where a resource reference appears in user-controllable input.

- **Passive enumeration — browse the application normally**:
	- Log in as `User A` and interact with every feature: view profile, send a message, create a document, place an order, upload a file, modify settings.
	- Do the same with `User B`.
	- In Burp's HTTP history, filter for requests that contain numeric IDs, UUIDs, or any parameter that looks like an object reference.

- **Look for IDs in**:
	- URL path segments (`/documents/4471`)
	- Query parameters (`?order=8821`)
	- JSON request/response bodies
	- Hidden form fields (inspect the DOM)
	- Cookies (check for `user_id`, `session_id`, `account_id` cookies)
	- Custom headers (`X-Account-Id`, `X-User-Token`)
	- JavaScript files — SPAs often store or transmit object IDs in JS state and API calls

>[!note] See [[#Attack surface]].

>[!tip]+
>Right-click → `Search` in Burp, search for `User A`'s known ID across all captured requests and responses. Any response that includes another user's ID in its body is potentially a reference you can exploit or pivot from.

### 2. Cross-account verification

Take a resource reference created by `User A` and submit it in a request authenticated as `User B` (or unauthenticated):

1. Log in as `User A`. Create a resource (message, document, order) — capture the request.
2. Note the object reference (e.g., `document_id=4471`).
3. Log out, or switch to User B's session in Burp.
4. Replay the request with the captured object reference.
5. Analyze the response:
    - **`200 OK`** with data → confirmed read IDOR.
    - **`200 OK`** with state change → confirmed write IDO
    - **`403 Forbidden`** → authorization check present, but keep testing other endpoints and method
    - **`404 Not Found`** → might still be an IDOR; the application could be hiding objects from unauthorized users to obscure the vulnerability (test another ID you know exists).

> [!note] A `403 Forbidden` on a `GET` endpoint does not mean `POST`, `PUT`, or `DELETE` on the same resource path is protected. Test every HTTP method independently.

### 3. Testing different CRUD operations

- IDOR isn't limited to reading. Test every CRUD operation for every object reference you discover:

|Operation|Example Endpoint|
|---|---|
|Read|`GET /notes/397`|
|Create|`POST /notes` with `{"owner_id": 398}`|
|Update|`PUT /notes/397` or `POST /notes/update/397`|
|Delete|`DELETE /notes/397` or `GET /notes/delete/397`|

- A view endpoint being properly protected doesn't imply modify and delete endpoints are equally protected. These are separate code paths, often written at different times by different developers.

## Exploitation techniques

### Direct ID manipulation

- Substitute the object reference in the request for one belonging to another user.

```
Original (User A's document):  GET /api/documents/4471
Modified (User B's document):  GET /api/documents/4472
```

If it's an API call:

```HTTP
POST /api/update-profile HTTP/1.1
Host: example.com
...
```
```JSON
{
	"user_id": 1209,
	"email": "email@example.com"
}
```

Try these:

- **Change the exposed reference:**

```JSON
{
	"user_id": 1211,
	"email": "attacker@example.com"
}
```

- **Use an array:**

```JSON
{
	"user_id": [1211],
	"email": "attacker@example.com"
}
```

- **Submit multiple IDs in an array** (batch operations):

```JSON
{
	"user_id": [1211, 1212, 1214],
	"email": "attacker@example.com"
}
```

- **Using wildcards or special patterns to test server-side parsing:**

```
/users?id=[0-9]+
/users?id=*
/users?id=%
/users?id=_
/users?id=1-100

```
### HTTP verb tampering

- Access controls are often applied inconsistently across HTTP methods.
- If IDOR isn't possible with `GET` or `POST`, it doesn't mean it's impossible with others.

```
GET /account/1209/settings
→ 403 Forbidden

POST /account/1209/settings
→ 200 OK (allows modification!)

PUT /account/1209/settings
→ 200 OK

DELETE /account/1209/settings
→ 200 OK (deletes account!)

PATCH /account/1209/settings     
→ 200 OK
```

### State-changing actions

- Other than changing HTTP method, you can also change action specified in the API query.

>[!example]+
>Suppose private notes in an application are accessed through the URL:
> 
> ```
> https://example.com/notes/view/397
> ```
> Even if you **can't view** other users' notes by changing the identifier, it doesn't necessarily imply that mean that the notes are protected from **unauthorized modification or deletion**:
> 
> ```
> https://example.com/notes/delete/398
> https://example.com/notes/edit/398
> https://example.com/notes/update/398
> . . . 
> ```
> 

- Use the [`parameters_actions.txt`](https://github.com/xajkep/wordlists/blob/master/discovery/parameters_actions.txt) wordlist to fuzz parameter actions/

### Different file extensions

- Modern frameworks often support **multiple formats** for the same resource. If you can't access the resource in one format, try others:

```
GET /account/1209
→ 403 Forbidden (HTML format denied)

GET /account/1209.json
→ 200 OK (JSON format allowed!)

GET /account/1209.xml
→ 200 OK (XML format allowed!)

GET /account/1209.csv 
→ 200 OK (CSV format allowed!)
```

This is particularly relevant in full-stack frameworks where `.json` routes are handled by API controllers while HTML routes go through a separate middleware stack.


>[!tip]+ Fuzz extensions using SecLists
>- [`Discovery/Web-Content/web-extensions.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/web-extensions.txt)
>- [`Fuzzing/extensions-most-common.fuzz.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/extensions-most-common.fuzz.txt)
>```bash
ffuf -u 'https://target.com/account/1209FUZZ' \
  -w /usr/share/seclists/Discovery/Web-Content/web-extensions.txt \
  -mc 200 -fc 403,404
>  ```
  
### HTTP parameter pollution

- When a server receives duplicate parameter names in a single request, different frameworks resolve the ambiguity differently — some take the first value, some the last, some combine them. 
- If the authorization check evaluates one copy of the parameter while the application logic processes another, you can bypass the check.

- In `GET` requests:

```JSON
Blocked: GET /api/messages?user_id=1211

Attack: GET /api/messages?user_id=1209&user_id=1211
# framework takes first → auth checks 1209 (passes)
# logic uses last       → returns messages for 1211

Attack: GET /api/messages?user_id=1211&user_id=1209
# framework takes last → auth checks 1209 (passes)
# logic uses first     → returns messages for 1211
```

- In `POST` JSON bodies:

```JSON
{"user_id": 1210, "email": "attacker@email.com"}
→
{"user_id": 1210, "user_id": 1209, "email": "attacker@email.com"}
```

- Array notation:

```HTTP
GET /api/messages?user_ids[]=1209&user_ids[]=1211
```

### Injecting IDs on endpoints that don't expose them

- **Offer the application an ID, even if it doesn't ask for it.**
- If no IDs are used in the application-generated requests, try adding them yourself. Append `id`, `user_id`, `message_id`, `uid`, `user`, or other object reference parameters (especially those you already encountered in other endpoints) and watch if the application behaves differently. 

```JSON
# normal request (returns your messages, user derived from session)
GET /api/v1/messages

# test: does appending user_id change the scope?
GET /api/v1/messages?user_id=1211
GET /api/v1/messages?uid=1211
GET /api/v1/messages?account_id=1211
```

## Fuzzing and automation

- Bash loop + `curl`:

```bash
# enumerate user profiles in a range; filter HTTP 200 responses
for id in $(seq 1200 1300); do
  response=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Cookie: session=YOUR_SESSION_COOKIE" \
    "https://example.com/api/users/$id")
  echo "$id: $response"
done | grep ":200"
```

>[!note]+ Options breakdown
> - `-s`: Suppress progress output.
> - `-o /dev/null`: Discard  response body (we only want status codes for enumeration).
> - `-w "%{http_code}"`L Prints only the HTTP status code.

 - To capture full response bodies for further analysis:

```bash
for id in $(seq 1200 1300); do
  curl -s -H "Cookie: session=YOUR_SESSION_COOKIE" \
    "https://target.com/api/invoices/$id" \
    -o "output_${id}.json"
done
```

---

- Basic numeric IDOR fuzz using `ffuf`:

```bash
ffuf -u 'https://example.com/api/documents/FUZZ' \
  -w /usr/share/seclists/Fuzzing/4-digits-0000-9999.txt \
  -H "Cookie: session=YOUR_SESSION_COOKIE" \
  -H "Content-Type: application/json" \
  -mc 200 \
  -fs 1234         # filter responses with size 1234 (the "not found" response size)
```

- Fuzzing `POST` body parameters:

```bash
ffuf -u 'https://example.com/api/transfer' \
  -X POST \
  -H "Content-Type: application/json" \
  -H "Cookie: session=YOUR_SESSION_COOKIE" \
  -d '{"recipient_id": FUZZ, "amount": 1}' \
  -w /usr/share/seclists/Fuzzing/6-digits-000000-999999.txt \
  -mc 200
```

- Fuzzing parameter names (when you don't know what the parameter is called):

```bash
ffuf -u 'https://example.com/api/messages?FUZZ=1211' \
  -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt \
  -H "Cookie: session=YOUR_SESSION_COOKIE" \
  -mc 200 -fw 5    # filter by word count to suppress identical "not found" responses
```

| Option           | Description                                                     |
| ---------------- | --------------------------------------------------------------- |
| `-mc 200`        | Match only HTTP `200` responses.                                |
| `-fc 403,404`    | Filter out `403`/`404` responses.                               |
| `-fs N`          | Filter responses of exactly `N` bytes.                          |
| `-fw N`          | Filter responses with exactly `N` words.                        |
| `-rate N`        | Limit requests per second (avoid triggering rate limiting/WAF). |
| `-t N`           | Thread count (default: `40`).                                   |
| `-o output.json` | Save results to file.                                           |

>[!note] See [[🛠️ ffuf]].

- You can also try fuzzing parameter names with wordlists like:
	- [`burp-parameter-names.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/burp-parameter-names.txt)
	- [`url-params_from-top-55-most-popular-apps.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/url-params_from-top-55-most-popular-apps.txt)

- Wordlists for fuzzing numeric parameters:
	- [`0-999999-hashgen.py`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/0-999999-hashgen.py)
	- [`1-4_all_letters_a-z.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/1-4_all_letters_a-z.txt)
	- [`3-digits-000-999.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/3-digits-000-999.txt)
	- [`4-digits-0000-9999.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/4-digits-0000-9999.txt)
	- [`5-digits-00000-99999.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/5-digits-00000-99999.txt)
	- [`6-digits-000000-999999.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/6-digits-000000-999999.txt)

## Discovering parameters with OSINT

- Use **search engine dorks** to surface indexed endpoints and parameters:


```
site:example.com inurl:id=
site:example.com inurl:user_id=
site:example.com inurl:account?id=
site:example.com "/api/users/"
site:example.com filetype:json
```

- Search **internet archives** for URLs with potentially vulnerable parameters that might have been removed from the current UI but are still processed by the backend server:
	
	- [`gau`](https://github.com/lc/gau) (Get All URLs)
		- Fetches known URLs from AlienVault's [Open Threat Exchange](https://otx.alienvault.com), the Wayback Machine, Common Crawl, and URLScan for the target given domain:
	
	```bash
	gau --threads 5 --subs --o gau_output.txt example.com
	```
	
	- [`waybackurls`](https://github.com/tomnomnom/waybackurls)
		- Fetches all known URLs from the Wayback Machine archive for the target domain(s):
	
	```bash
	waybackurls target.com > wayback_output.txt
	```
	
	- Filter URLs to only include endpoints with query parameters:
	
	```bash
	cat gau_output.txt | grep "?" | sort -u
	```
	
	- Extract all unique parameter names: 
	
	```bash
	cat gau_output.txt | grep "?" | sed 's/.*?\(.*\)/\1/' | tr '&' '\n' | cut -d'=' -f1 | sort -u
	```

- [`waymore`](https://github.com/xnl-h4ck3r/waymore)
	- The idea behind `waymore` is to find even more links from the Wayback Machine than other existing tools. It fetches URL not only from Wayback Machine, but also from Common Crawl, Alien Vault OTX, URLScan and Virus Total.

- [`paramspider`](https://github.com/devanshbatham/ParamSpider)
	- Fetches URLs related to any domain or a list of domains from Wayback archives.

>[!example]+
>```bash
>gau --threads 5 --subs --o output.txt example.com
>```

- Look for **Swagger / OpenAPI documentation** that often reveals API endpoints used by the application:

```
/swagger
/swagger-ui.html
/api/docs
/api/v1/docs
/openapi.json
/openapi.yaml
/v2/api-docs
/v3/api-docs
/.well-known/openapi.json
```



## Real-world case studies


- **[`Delete messages via IDOR (HackerOne #697412`)](https://hackerone.com/reports/697412)**
	- A `DELETE` endpoint accepted a numeric message ID with no ownership check. Any authenticated user could delete any message by iterating IDs.

- **[`IDOR to view User Order Information (HackerOne #287789`)](https://hackerone.com/reports/287789)**
	- Simple decimal integer in URL path. no session-to-resource ownership verification. Allowed to access full order history of any user.

- **[`Delete Campaigns via IDOR (HackerOne #1969141`)](https://hackerone.com/reports/1969141)** 
	- `POST` endpoint with a Base64-encoded campaign ID in the request body. Decoding, substituting a different campaign ID, and re-encoding granted deletion access to other users' campaigns.

- **[`IDOR through MongoDB Object IDs Prediction`](https://techkranti.com/idor-through-mongodb-object-ids-prediction/)**
	- MongoDB `ObjectID`s are 12-byte values with a time-based component, a machine identifier, and a counter. When the generation pattern was understood, the attacker predicted valid `ObjectID`s and accessed documents that didn't belong to them, demonstrating that non-integer IDs can still be vulnerable.

## References and further reading

- [`Insecure Idrect Object Reference (IDOR) — hackviser`](https://hackviser.com/tactics/pentesting/web/idor)

- [`A01:2021 — Broken Access Contro — OWASP Top 10 2021`](https://owasp.org/Top10/A01_2021-Broken_Access_Control/)
- [`How to find more IDORs — Medium`](https://vickieli.medium.com/how-to-find-more-idors-ae2db67c9489)
- [`Insecure direct object references (IDOR) — Portswigger`](https://portswigger.net/web-security/access-control/idor)
- [`The Rise of IDOR — HackerOne`](https://www.hackerone.com/company-news/rise-idor) 
- [`IDOR — HackTricks`](https://book.hacktricks.wiki/en/pentesting-web/idor.html)
- [`Insecure Direct Object Reference Prevention Cheat Sheet — OWASP Cheat Sheet`](https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html)
- [`Insecure Direct Object Reference (IDOR) — BugBountyHunter`](https://www.bugbountyhunter.com/vulnerability/?type=idor)
- [`Finding more IDORs – Tips and Tricks — AON`](https://www.aon.com/cyber-solutions/aon_cyber_labs/finding-more-idors-tips-and-tricks/)

- [`All About IDORs - Understand, Exploit, Prevent — BugBase`](https://bugbase.ai/blog/casting-light-on-idor)

- [`Automated IDOR Discovery through Stateful Swagger Fuzzing`](https://engineeringblog.yelp.com/2020/01/automated-idor-discovery-through-stateful-swagger-fuzzing.html)
- [`Finding and fixing insecure direct object references in Python`](https://snyk.io/blog/insecure-direct-object-references-python/)

- [`IDOR Checklist — Ahsan Khan, X (Twitter)`](https://x.com/hunter0x7/status/1580211248037126145)


