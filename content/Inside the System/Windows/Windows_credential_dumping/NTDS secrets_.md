---
created: 2026-03-06
tags:
  - Windows
  - Windows_credential_dumping
  - password_attacks
  - AD
---
>**MITRE ATT&CK:** [`T1003.003 —  OS Credential Dumping: NTDS`](https://attack.mitre.org/techniques/T1003/003/).
>**Required privilege:** Local Administrator or `SYSTEM` (requires `SeDebugPrivilege`). 
>**Goal:** Extract NTLM hashes, Kerberos tickets, and (sometimes) plaintext passwords from LSASS process memory.

### Table of contents
## NTDS

>**`NTDS.dit`** is the primary database file for **Active Directory Domain Services (AD DS)** in Windows Server environments that stores all directory data in a structured format known as the **Directory Information Tree (DIT)**. The information `NTDS.dit` stores includes user accounts, computer objects, groups, security identifiers (SIDs), password hashes (e.g., NT hashes), and configuration data for the domain.

- **NTDS (NT Directory Services)** is a core component of **Active Directory (AD)**.
- **Every Domain Controller (DC)** maintains its own local copy of the `NTDS.dit` database. 
- The contents are synchronized between domain controllers using what's known as **Active Directory replication**.
- By default, `NTDS.dit` is located at:

```powershell
C:\Windows\NTDS\ntds.dit
```

Secrets extracted from the `NTDS.dit` can be used for various attacks, including:
- credential spraying, stuffling, shuffling, cracking
- [[Pass-the-Hash]]
- [[Overpass-the-Hash]]
- [[silver_ticket]]
- [[golden_ticket]]

>[!important] The `NTDS.dit` file is **encrypted** with a system key derived from data stored in the `SYSTEM` registry hive. See [[Registry & LSA secrets#SYSTEM Boot configuration and encryption keys]].

## Extracting secrets from `NTDS.dit`

Since the `NTDS.dit` is constantly used by AD processes such as the Kerberos KDC, it can't be just copied like regular files.

- Accessing `NTDS.dit` usually requires Domain Admin or Enterprise Admin User, or membership in `Backup Operators` group on a domain controller.
- To decrypt `NTDS.dit`, you will need access to the `SYSTEM` registry hive (stored at `C:\Windows\System32\config\SECURITY`). See [Registry & LSA secrets > SYSTEM Boot configuration and encryption keys](app://obsidian.md/Registry%20&%20LSA%20secrets#SYSTEM%20Boot%20configuration%20and%20encryption%20keys).

You can take either of the following approaches to save a copy of `NTDS.dit`:

- Use [`NTDSUtil.exe`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/cc753343(v=ws.11)) Windows command-line tool to save a snapshot of Active Directory data. 
- Create a Volume Shadow Copy using the `vssadmin` command and read `NTDS.dit` from that shadow copy.
- Use [`PowerSploit`](https://github.com/PowerShellMafia/PowerSploit)'s [`Invoke-NinjaCopy.ps1`](https://github.com/PowerShellMafia/PowerSploit/blob/master/Exfiltration/Invoke-NinjaCopy.ps1) to copy `NTDS.dit`.

Once you have the copy, you can transfer it to your attacker machine and analyze it with [`Impacket`](https://github.com/SecureAuthCorp/impacket)'s [`secretsdump.py`](https://github.com/fortra/impacket/blob/master/examples/secretsdump.py) or [`gosecretsdump`](https://github.com/c-sto/gosecretsdump) (written in Go, faster for big files).

>[!note] See [[Linux_file_transfers]] and [[Windows_file_transfers]] for file transfer methods.
### `NTDSUtil.exe`

>[`NTDSUtil.exe`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/cc753343(v=ws.11)) is a Windows command-line tool used to perform database maintenance of AD DS, manage and control single master operations, and other

- The following command copies the `NTDS.dit` database along with the `SYSTEM` and `SECURITY` hives to `C:\Windows\Temp`:

```powershell
ntdsutil "activate instance ntds" "ifm" "create full C:\Windows\Temp\NTDS" quit quit
```

The following files can then be exported

- `C:\Windows\Temp\NTDS\Active Directory\ntds.dit`
- `C:\Windows\Temp\NTDS\registry\SYSTEM`

>[!warning] If the NTDS database is very large (several gigabytes), the generation of a defragmented backup with `ntdsutil` consumes a lot of CPU and disk resources on the server, which can cause slowdowns and other undesirable effects on the domain controller.

### `vssadmin`

You can use  [`vssadmin`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/vssadmin) to create a **Volume Shadow Copy** — a point-in-time snapshot of the filesystem, including `NTDS.dit` — that you can then read safely:

```powershell
vssadmin create shadow /for=C:
```

>[!warning] The `vssadmin create` command is **not available on Windows 10 and Windows 11** (client editions). This command is only present in **Windows Server** operating systems.

- List existing volume shadows:

```powershell
vssadmin list shadows
```

- Then copy `NTDS.dit` and the `SYSTEM` hive from the shadow copy:

```powershell
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\NTDS\NTDS.dit C:\Windows\Temp\ntds.dit
```

```powershell
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\Config\SYSTEM C:\Windows\Temp\system.hive
```


- Once your're done, remove the shadow copy:

```powershell
vssadmin delete shadows /shadow=HarddiskVolumeShadowCopy1
```

>[!note] This technique was mentioned in [[Registry & LSA secrets#Saving registry hives locally]].

### `Invoke-NinjaCopy`

[`PowerSploit`](https://github.com/PowerShellMafia/PowerSploit)'s [`Invoke-NinjaCopy.ps1`](https://github.com/PowerShellMafia/PowerSploit/blob/master/Exfiltration/Invoke-NinjaCopy.ps1) is a PowerShell script that can extract `NTDS.dit`:

```bash
Invoke-NinjaCopy.ps1 -Path "C:\Windows\NTDS\NTDS.dit" -LocalDestination "C:\Windows\Temp\ntds.dit.save"
```

The script copies files off an NTFS volume by opening a read handle to the entire volume (such as `C:`) and parsing the NTFS structures. This technique is stealthier than the others.
### Analyzing `NTDS.dit` copy using `secretsdump.py` and `gosecretsdump`

Once the required files are exfiltrated and copied to your machine, you can use [`Impacket`](https://github.com/SecureAuthCorp/impacket)'s [`secretsdump.py`](https://github.com/fortra/impacket/blob/master/examples/secretsdump.py) to extract credentials from it:

```bash
secretsdump.py -ntds ntds.dit.save -system system.hive LOCAL
```

Alternatively, you can use [`gosecretsdump`](https://github.com/c-sto/gosecretsdump), a Go version of `secretsdump.py`, faster for large files:

```bash
gosecretsdump -ntds ntds.dit.save -system system.hive
```

## More data to be found: `ntdsdotsqlite`

With the required files, it is possible to extract more information than just secrets. The NTDS file is responsible for storing the entire directory, with users, groups, OUs, trusted domains etc... This data can be retrieved by parsing the NTDS with tools like [`ntdsdotsqlite`](https://github.com/almandin/ntdsdotsqlite):

```bash
ntdsdotsqlite ntds.dit -o ntds.sqlite
ntdsdotsqlite ntds.dit -o ntds.sqlite --system system.hive
```

## References and further reading

- [`NTDS secrets — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/credentials/dumping/ntds)
- [`OS Credential Dumping: NTDS — MITRE ATT&CK`](https://attack.mitre.org/techniques/T1003/003/)
## drafts

- The `C:\Windows\NTDS` directory typically contains files like:

```powershell
C:\Windows\NTDS\
   ntds.dit
   edb.log
   edb00001.log
   edb.chk
   edbtmp.log
```

- **`edb.log` and `edbXXXXX.log`** are **transaction logs** that record database modifications before they're written to the database. Each log file is typically **10 MB**.
- **`edb.chk`** is the **checkpoint file** that tracks which transactions have already been written to the database.
- **`edptmp.log`** is a **temporary logs file** used when rotating log files.

>[!note]+ ESE
>- The storage engine NTDS uses is called the **Extensible Storage Engine (ESE)**, also called **Jet Blue**.
>- Data is stored in **fixed-size pages**, and these pages are organized through **B-tree indexes** for efficient searching.

