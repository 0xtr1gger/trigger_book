---
created: 2026-07-21
tags:
  - Windows
  - Windows_PrivEsc
updated: 2026-09-20
status: complete
---

> [!abstract]+ **Scope**: Privilege escalation through membership in the `Backup Operators` group.

- [ ] Confirm membership in the `Backup Operators` group (`whoami /groups` or `net localgroup "Backup Operators"`).
- [ ] Check active token status for `SeBackupPrivilege` and `SeRestorePrivilege` (`whoami /priv`).
- [ ] Dump sensitive registry hives (`SAM`, `SYSTEM`, `SECURITY`) or domain database (`NTDS.dit`) using `reg save`, `diskshadow`, or `robocopy /b`.
- [ ] Extract credentials offline using `impacket-secretsdump` or Mimikatz.
- [ ] Abuse `SeRestorePrivilege` to overwrite service executables or DLLs running under `SYSTEM`.
---
## `Backup Operators`

>The **`Backup Operators`** group is a built-in Windows security group that allows members to **back up and restore files and directories** regardless of object DACLs and owenership. 

- This capability is granted through **`SeBackupPrivilege`** (bypasses DACLs for read operations during) and **`SeRestorePrivilege`** (bypasses DACLs for write operations). Both privileges take effect only when a process opens files using backup semantics (`FILE_FLAG_BACKUP_SEMANTICS`). 
- Standard commands like `type`, `copy`, and `Get-Content` don't use backup semantics and therefore can't bypass DACLs.
- To take advantage of `SeBackupPrivilege` and `SeRestorePrivilege`, you need to use tools like `reg save`, `diskshadow`, or `robocopy /b` that honor backup semantics.


> [!note] See [[SeBackupPrivilege & SeRestorePrivilege]] for privilege escalation.

## Checking group membership

- Check whether your current user is a member of `Backup Operators`:

```powershell
whoami /groups
```

```cmd
net localgroup "Backup Operators"
```

```powershell
Get-LocalGroupMember -Group "Backup Operators"
```

- Verify assigned privileges:

```powershell
whoami /priv
```

>[!note] Even if the privileges are present in the output but marked `Disabled`, Windows won't consider them during access checks. You need to enable the privileges first before using them. See [[SeBackupPrivilege & SeRestorePrivilege#Enumerating and enabling privileges]].

## References and further reading

- [`Back up files and directories - security policy setting — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/back-up-files-and-directories)
- [`Restore files and directories - security policy setting — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/restore-files-and-directories)
- [`Diskshadow — LOLBAS`](https://lolbas-project.github.io/lolbas/Binaries/Diskshadow/)
- [`robocopy — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/robocopy)
- [`impacket-secretsdump — Impacket`](https://github.com/fortra/impacket/blob/master/impacket/examples/secretsdump.py)
