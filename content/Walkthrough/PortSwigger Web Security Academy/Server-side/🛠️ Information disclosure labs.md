---
created: 2026-06-05
---
| `#`  | Solved? | Name                                              | Date    |
| ---- | ------- | ------------------------------------------------- | ------- |
| `1.` | `✓`     | Information disclosure in error messages          | `05.06` |
| `2.` | `✓`     | Information disclosure on debug page              | `05.06` |
| `3.` | `✓`     | Source code disclosure via backup files           | `05.06` |
| `4.` | `✓`     | Authentication bypass via information disclosure  | `05.06` |
| `5.` | `✓`     | Information disclosure in version control history | `05.06` |

## 1. Information disclosure in error messages

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Information disclosure in error messages`](https://portswigger.net/web-security/information-disclosure/exploiting/lab-infoleak-in-error-messages)
> - Level: #Apprentice 
> 
> This lab's verbose error messages reveal that it is using a vulnerable version of a third-party framework. To solve the lab, obtain and submit the version number of this framework.

### Solution

- Navigate to any product. To trigger an error, it's enough to append an unexpected character, just as a single quote, to the `productId` URL parameter:

![[images/walkthrough/PortSwigger/Information Disclosure/lab1/1.png]]

- Vulnerable framework version is revealed at the end of the error message:

![[images/walkthrough/PortSwigger/Information Disclosure/lab1/2.png]]

- Submit the version number as a solution (`2.3.31`).

![[images/walkthrough/PortSwigger/Information Disclosure/lab1/solved.png]]


Solved!

## 2. Information disclosure on debug page

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Information disclosure on debug page`](https://portswigger.net/web-security/information-disclosure/exploiting/lab-infoleak-on-debug-page)
> - Level: #Apprentice 
> 
> This lab contains a debug page that discloses sensitive information about the application. To solve the lab, obtain and submit the `SECRET_KEY` environment variable.

### Solution

- Right-click the lab's home page -> `View page source`. Scroll down to find an HTML comment:

![[images/walkthrough/PortSwigger/Information Disclosure/lab2/1.png]]

- It says:

```html
<!-- <a href=/cgi-bin/phpinfo.php>Debug</a> -->
```

- Go to the specified path:

```
/cgi-bin/phpinfo.php
```

- And search for `SECRET_KEY` in the response:

![[images/walkthrough/PortSwigger/Information Disclosure/lab2/2.png]]

- Submit the value as a solution.

![[images/walkthrough/PortSwigger/Information Disclosure/lab2/solved.png]]


Solved!
## 3. Source code disclosure via backup files

>[!done]


>[!note]+ Lab description
> 
> - [`Lab: Source code disclosure via backup files`](https://portswigger.net/web-security/information-disclosure/exploiting/lab-infoleak-via-backup-files)
> - Level: #Apprentice 
> 
> This lab leaks its source code via backup files in a hidden directory. To solve the lab, identify and submit the database password, which is hard-coded in the leaked source code.

### Solution

- Navigate the lab and go to `/robots.txt`. Find a disallowed path:

```
Disallow: /backup
```

![[images/walkthrough/PortSwigger/Information Disclosure/lab3/1.png]]

- Go to `/backup` and find a directory listing:

![[images/walkthrough/PortSwigger/Information Disclosure/lab3/2.png]]

- Go to `/backup/ProductTemplate.java.bak` and find PostgreSQL password in the connection builder:

```
/backup/ProductTemplate.java.bak
```

```java
ConnectionBuilder connectionBuilder = ConnectionBuilder.from(
                "org.postgresql.Driver",
                "postgresql",
                "localhost",
                5432,
                "postgres",
                "postgres",
                "rrg53fgz5n4of4wo6tt6dntkt84z4sh1"
        ).withAutoCommit();
```

![[images/walkthrough/PortSwigger/Information Disclosure/lab3/3.png]]

- Submit the password as a solution.

![[images/walkthrough/PortSwigger/Information Disclosure/lab3/solved.png]]

Solved!
## 4. Authentication bypass via information disclosure

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Authentication bypass via information disclosure`](https://portswigger.net/web-security/information-disclosure/exploiting/lab-infoleak-authentication-bypass)
> - Level: #Practitioner 
> 
> This lab's administration interface has an authentication bypass vulnerability, but it is impractical to exploit without knowledge of a custom HTTP header used by the front-end.
> 
> To solve the lab, obtain the header name then use it to bypass the lab's authentication. Access the admin interface and delete the user `carlos`.
> 
> You can log in to your own account using the following credentials: `wiener:peter`

### Solution

- Log in as `wiener` and navigate to `/admin`. See an error message: `Admin interface only available to local users`.


![[images/walkthrough/PortSwigger/Information Disclosure/lab4/1.png]]

- Send this request to `Repeater` and change request method to `TRACE`:

![[images/walkthrough/PortSwigger/Information Disclosure/lab4/2.png]]

- See a custom HTTP header with your IP address:

```http
X-Custom-IP-Authorization: <ip_address>
```

- Change the request method back to `GET`. Add the `X-Custom-IP-Authorization` header set to the loopback address, `127.0.0.1`:

![[images/walkthrough/PortSwigger/Information Disclosure/lab4/3.png]]

- See that your are given access to the admin panel.
- Repeat the request changing the path to `/admin/delete/Username=carlos` to delete the `carlos` user.

![[images/walkthrough/PortSwigger/Information Disclosure/lab4/4.png]]

![[images/walkthrough/PortSwigger/Information Disclosure/lab4/solved.png]]

Solved!
## 5. Information disclosure in version control history

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Information disclosure in version control history`](https://portswigger.net/web-security/information-disclosure/exploiting/lab-infoleak-in-version-control-history)
> - Level: #Practitioner 
> 
> This lab discloses sensitive information via its version control history. To solve the lab, obtain the password for the `administrator` user then log in and delete the user `carlos`.

### Solution

- Navigate the lab and go to `/.git`. See a directory listing of a typical `.git` directory:

![[images/walkthrough/PortSwigger/Information Disclosure/lab5/1.png]]

- Use [`git-dumper`](https://search.brave.com/search?q=git+dumper) or similar tool to extract the Git repository:

>[!note]+ Installation
> ```bash
> pip install git-dumper
> ```

```bash
git-dumper https://0adf00650460fd89801e627600bd0037.web-security-academy.net/.git lab-git
```
```bash
cd lab-git
```

- Output `admin.conf`:

```bash
cat admin.conf
```

![[images/walkthrough/PortSwigger/Information Disclosure/lab5/2.png]]

- No password here. 

- Output `admin_panel.php`:

```bash
cat admin_panel.php
```
```PHP
<?php echo 'TODO: build an amazing admin panel, but remember to check the password!'; ?>
```

- See `git log`:

```bash
git log
```
```bash
commit 0b42cb4d19d096738d41bdc09954965930e04f2b (HEAD -> master)
Author: Carlos Montoya <carlos@carlos-montoya.net>
Date:   Tue Jun 23 14:05:07 2020 +0000

    Remove admin password from config

commit df014671b4c9c2c4f950421fc5ae4cbd1cdf9559
Author: Carlos Montoya <carlos@carlos-montoya.net>
Date:   Mon Jun 22 16:23:42 2020 +0000

    Add skeleton admin panel
```

![[images/walkthrough/PortSwigger/Information Disclosure/lab5/3.png]]

- Checkout to the commit:

```bash
git checkout df014671b4c9c2c4f950421fc5ae4cbd1cdf9559
```

- Run `cat admin.conf` again:

![[images/walkthrough/PortSwigger/Information Disclosure/lab5/4.png]]

- Log in as `administrator` with the discovered password.

![[images/walkthrough/PortSwigger/Information Disclosure/lab5/5.png]]

- Go to `Admin panel` and delete the `carlos` user.

![[images/walkthrough/PortSwigger/Information Disclosure/lab5/solved.png]]

Solved!
