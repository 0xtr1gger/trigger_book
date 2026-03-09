---
created: 2026-03-09
tags:
  - Windows
  - Windows_credential_dumping
  - password_attacks
  - AD
---
>**MITRE ATT&CK:** [`T1003.003 —  OS Credential Dumping: NTDS`](https://attack.mitre.org/techniques/T1003/003/).

### Table of contents

- [[#What is NTDS.dit]]
- [[#Extracting secrets from NTDS.dit]]
	- [[#NTDSUtil.exe]]
	- [[#Volume Shadow Copy]]
	- [[#Invoke-NinjaCopy]]
	- [[#Analyzing NTDS.dit copy using secretsdump.py and gosecretsdump]]
- [[#More data to be found ntdsdotsqlite]]
- [[#References and further reading]]
## What is NTDS.dit

>**`NTDS.dit`** is the primary database file for **Active Directory Domain Services (AD DS)** that stores the complete directory for the domain in a structured format known as **Directory Information Tree (DIT)**.

- `NTDS.dit` holds user accounts, computer objects, group memberships, security identifiers (SIDs), Group Policies, trust relationships, and **NT password hashes and Kerberos keys** for every domain account.

>[!note] **NTDS** stands for **NT Directory Services** — a core component of **Active Directory (AD)**.

>[!important] **Every Domain Controller (DC)** maintains its own local copy of the `NTDS.dit` database. 
>- The database is synchronized between domain controllers through a process known as **Active Directory replication**.

- By default, on any DC, `NTDS.dit` is located at:

```powershell
C:\Windows\NTDS\ntds.dit
```

NTDS stores information on **every** account in the domain, including:
- **All user accounts** (regular and privileged), including **Domain Admin accounts**.
- **Service accounts**, including the **`krbtgt` account** (the ticket-granting service account; its hash is used in [[Golden Ticket _]] attacks).
- **Computer accounts**.

Secrets extracted from the `NTDS.dit` can be used for various attacks, including:
- [[Pass-the-Hash]] (PtH)
- [[Overpass-the-Hash]]
- [[Golden Ticket _]]
- [[Silver Ticket]]
- Credential spraying, stuffling, shuffling, cracking

So, dumping NTDS means you fully compromise the domain.
## Extracting secrets from NTDS.dit

>[!important] Access to `NDTS.dit` is usually restricted to Domain Admins, Enterprise Admins, members or the `Backup Operators` group, and `SYSTEM`.

>[!important]+ The `NTDS.dit` file is **encrypted** with a system key derived from data stored in the `SYSTEM` registry hive. 
>- Therefore, to access data in `NTDS.dit`, you need to copy both the `NTDS.dit` database and the `SYSTEM` hive (stored at `C:\Windows\System32\config\SECURITY`).
>
>>[!note] See [[Registry & LSA secrets#SYSTEM Boot configuration and encryption keys]].

Once you have the necessary permissions, you can take either of the following approaches to save a copy of `NTDS.dit`:

- Use [`NTDSUtil.exe`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/cc753343(v=ws.11)) Windows command-line tool to save a snapshot of Active Directory data. 
- Create a Volume Shadow Copy using the `vssadmin` command and read `NTDS.dit` from that shadow copy.
- Use [`PowerSploit`](https://github.com/PowerShellMafia/PowerSploit)'s [`Invoke-NinjaCopy.ps1`](https://github.com/PowerShellMafia/PowerSploit/blob/master/Exfiltration/Invoke-NinjaCopy.ps1) to copy `NTDS.dit`.

You can then transfer the copy to your attacker machine and extract credentials with [`Impacket`](https://github.com/SecureAuthCorp/impacket)'s [`secretsdump.py`](https://github.com/fortra/impacket/blob/master/examples/secretsdump.py) or [`gosecretsdump`](https://github.com/c-sto/gosecretsdump) (written in Go, faster for big files).

>[!note] See [[Linux_file_transfers]] and [[Windows_file_transfers]] for file transfer methods.
### NTDSUtil.exe

>[`NTDSUtil.exe`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/cc753343(v=ws.11)) is a built-in Windows command-line tool used for AD DS maintenance tasks.

- One of its features is the **Install From Media (IFM)** function, which creates a snapshot of the Active Directory database. Normally, this is used to bootstrap new DCs without full replication — but can as well be used to dump AD credentials.

- The following command copies the `NTDS.dit` database along with the `SYSTEM` and `SECURITY` hives to `C:\Windows\Temp`:

```powershell
ntdsutil "activate instance ntds" "ifm" "create full C:\Windows\Temp\NTDS" quit quit
```

You get three files:
- `C:\Windows\Temp\NTDS\Active Directory\ntds.dit`
- `C:\Windows\Temp\NTDS\registry\SYSTEM`
- `C:\Windows\Temp\NTDS\registry\SECURITY`

Grab the files and transfer to your attack machine (see [[Linux_file_transfers]] and [[Windows_file_transfers]]).

>[!warning]+ Performance impact
> - `NTDSUtil`'s IFM creates a defragmented backup, and if the NTDS database is very large (several gigabytes), this operation will consumes a lot of CPU and disk resources. 
> - This will cause noticeable slowdowns on the DC and can appear in performance monitoring dashboards. This is noisy — so you might need to choose a different approach.

### Volume Shadow Copy

You can use [`vssadmin`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/vssadmin) to create a **Volume Shadow Copy (VSS)** — a read-only point-in-time snapshot of the filesystem. This you can read  `NTDS.dit` directly from the copy — even through the live file is locked.


1. Create a shadow copy of the `C:` drive:

```powershell
vssadmin create shadow /for=C:
```

>[!warning] `vssadmin create` only works on **Windows Server** operating systems. It's not available on Windows 10 or Windows 11 client editions. On a DC, it won't be a problem, but keep this in mind if you want to create a shadow copy to extract other data.


2. Copy `NTDS.dit` and the `SYSTEM` hive from the shadow copy:

```powershell
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\NTDS\NTDS.dit C:\Windows\Temp\ntds.dit
```

```powershell
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\Config\SYSTEM C:\Windows\Temp\system.hive
```

3. Once your're done, remove the shadow copy:

```powershell
vssadmin delete shadows /for=c: /all
```

>[!example]+
>![[copying_ntds.png]]

>[!tip]+
>Check if there're any existing copies of the filesystem. If you find any recent one, you can just use it instead of creating a new — this avoids unnecessary noise.
> 
> ```powershell
> vssadmin list shadows
> ```

>[!note] This technique was mentioned in [[Registry & LSA secrets#Saving registry hives locally]].

### Invoke-NinjaCopy

[`Invoke-NinjaCopy`](https://github.com/PowerShellMafia/PowerSploit/blob/master/Exfiltration/Invoke-NinjaCopy.ps1) from the [`PowerSploit`](https://github.com/PowerShellMafia/PowerSploit) framework is a PowerShell script that can extract `NTDS.dit`:

```powershell
Import-Module .\Invoke-NinjaCopy.ps1
```

```powershell
Invoke-NinjaCopy.ps1 -Path "C:\Windows\NTDS\NTDS.dit" -LocalDestination "C:\Windows\Temp\ntds.dit.save"
```

Rather than creating a shadow copy, the script opens a read handle directly to the raw NTFS volume (e.g., `\\.\C:`) and manually parses the NTFS structures to locate and read the target file. 
This technique is stealthier than the others — it doesn't involve VSS APIs or `ntdsutil` (may be that's why it's called *`-Ninja`*).
### Analyzing NTDS.dit copy using secretsdump.py and gosecretsdump

Once the required files are copied to your machine, you can use [`Impacket`](https://github.com/SecureAuthCorp/impacket)'s [`secretsdump.py`](https://github.com/fortra/impacket/blob/master/examples/secretsdump.py) to extract credentials from it:

```bash
secretsdump.py -ntds ntds.dit -system system.hive LOCAL
```

The output format for each account is:

```
username:RID:LM_hash:NT_hash:::
```

>[!example]+
>![[impacket_secretsdump_ntds.png]]

- [`gosecretsdump`](https://github.com/c-sto/gosecretsdump) is a Go re-implementation of `secretsdump.py`. It's significantly faster on large `NTDS.dit` files:

```bash
gosecretsdump -ntds ntds.dit -system system.hive
```

## More data to be found: ntdsdotsqlite

Hashes are the primary target, but `NTDS.dit` contains the full Active Directory directory — a goldmine of intelligence. [`ntdsdotsqlite`](https://github.com/almandin/ntdsdotsqlite) parses the NTDS database and dumps it into an SQLite database you can query:

```bash
ntdsdotsqlite ntds.dit -o ntds.sqlite
```

- To also decrypt the secrets, specify the `SYSTEM` hive file:

```bash
ntdsdotsqlite ntds.dit -o ntds.sqlite --system system.hive
```

Once you have the SQLite file, you can query it with any SQLite client:

```bash
sqlite3 ntds.sqlite
```
## References and further reading

- [`NTDS secrets — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/credentials/dumping/ntds)
- [`OS Credential Dumping: NTDS — MITRE ATT&CK`](https://attack.mitre.org/techniques/T1003/003/)
