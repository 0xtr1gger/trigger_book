---
created: 2026-08-22
updated: 2026-08-22
tags:
  - Meta
  - Audit
  - Vault_Organization
  - CPTS
  - OSCP
  - Style_Guide
status: complete
---

# Master Strategy & Execution Guide: Vault Refactoring, Content Completion & Quartz Site Optimization

This document provides a comprehensive, strategic blueprint for an AI agent (or human editor) to systematically audit, refactor, rewrite, complete, and publish all technical notes under `content/Windows` and `content/Active Directory/Attacking AD and Windows environments`.

The ultimate objective is to transform these directories into a **100% complete, practitioner-grade, exam-ready reference vault for CPTS (HTB Certified Penetration Testing Specialist) and OSCP (OffSec Certified Professional)** while strictly enforcing the author's writing persona and formatting directives set forth in [[AI Style & Formatting Guide]].

> [!important] Public Publishing Directive  
> This vault is published as a public website using **Quartz**. Every modified or newly created note must be visually cohesive, structurally consistent, free of dead links or broken callouts, and formatted to render flawlessly on Quartz.

---

## 1. The 5-Tier Note Refactoring Classification Matrix

Every note in the target directories must be audited and assigned to one of five action tiers depending on its current state and required level of intervention:

```
                  ┌─────────────────────────────────────────┐
                  │ 📝 NOTE REFACTORING ACTION TIERS        │
                  └────────────────────┬────────────────────┘
                                       │
     ┌─────────────────┬───────────────┼───────────────┬────────────────┐
     ▼                 ▼               ▼               ▼                ▼
┌─────────┐       ┌─────────┐     ┌─────────┐     ┌─────────┐      ┌─────────┐
│ TIER 1  │       │ TIER 2  │     │ TIER 3  │     │ TIER 4  │      │ TIER 5  │
│ Polish  │       │Align/Fmt│     │ Complete│     │ Overhaul│      │ Scratch │
└─────────┘       └─────────┘     └─────────┘     └─────────┘      └─────────┘
 (Grammar/        (Frontmatter,   (Fill Stubs/    (Split Mega-     (Create New
 Syntactical      Callouts,       Unfinished      Notes, Re-       Missing CPTS/
 Tweaks)          Wikilinks)      Sections)       Architect)       OSCP Topics)
```

### Tier Definitions & Operating Procedures

#### Tier 1: Language & Wording Polish (Light Edit)
- **Target Notes**: Complete, well-structured notes that already follow the basic layout but contain minor spelling errors, grammatical awkwardness, non-standard phrasing, or inconsistent backticks.
- **AI Operating Procedure**:
  - Fix typos, technical phrasing, and English wording without altering technical commands or structural layout.
  - Ensure all tool names, attributes, flags, and SIDs are enclosed in backticks (`GenericAll`, `sAMAccountName`, `-ResolveGUIDs`).
  - Verify bold-anchored bullet formatting.

#### Tier 2: Structural & Formatting Realignment (Medium Edit)
- **Target Notes**: Technically accurate notes that lack proper Obsidian layout standards (missing YAML frontmatter, scope callouts, checklists, standardized callouts, tables, wikilinks, or reference sections).
- **AI Operating Procedure**:
  - Add standard YAML frontmatter (`created`, `updated`, `tags`, `status`).
  - Insert `>[!abstract]+ Scope` or `>[!important] Objective:` callout at the top.
  - Insert `## Checklist` section with task checkboxes (`- [ ]`) outlining actionable steps.
  - Convert generic text notes/warnings into appropriate fold-state callouts (`>[!note]`, `>[!tip]+`, `>[!warning]`, `>[!example]-`).
  - Convert unlinked technical concepts into Obsidian Wikilinks (`[[Kerberos]]`, `[[🛠️ Pass-the-Hash]]`).
  - Append `## References and further reading` at the bottom.

#### Tier 3: Content Completion / Finishing Drafts (Heavy Edit)
- **Target Notes**: Partial notes, empty stubs (< 20 lines), or drafts marked `status: incomplete` / `status: draft` that contain missing tool sections (e.g. missing Linux alternatives for Windows tools), truncated steps, or placeholder text.
- **AI Operating Procedure**:
  - Perform thorough technical expansion to complete missing sections.
  - Ensure dual-tooling parity: provide both Windows (PowerShell/CMD/Native) and Linux (Impacket/bloodyAD/Samba/NetExec) execution options where applicable.
  - Add parameter tables (`| Command | Description |`) and verification steps (`>[!tip]+`).

#### Tier 4: Full Overhaul & Rewriting (Re-Architecting)
- **Target Notes**: Unstructured "mega-notes" (e.g., single notes spanning 30+ KB combining multiple distinct attack vectors), notes with broken technical flow, or files with incorrect folder placements/naming conventions.
- **AI Operating Procedure**:
  - Split mega-notes into modular, focused notes (e.g., splitting `Weak service permissions.md` into Service DACLs, Weak Binary Permissions, and Unquoted Service Paths).
  - Rewrite contents from scratch using the author's textbook style, adhering strictly to the Gold Standard structure in `[[AI Style & Formatting Guide]]`.

#### Tier 5: Creation from Scratch (Gap Filling)
- **Target Notes**: Critical CPTS/OSCP syllabus topics currently completely absent from the vault.
- **AI Operating Procedure**:
  - Author brand-new, comprehensive reference guides following the exact 7-part note anatomy.
  - Integrate new notes seamlessly into existing roadmaps and cross-link via wikilinks.

---

## 2. Complete Note-by-Note Audit & Action Register

Below is the definitive master inventory of all existing notes in `content/Windows` and `content/Active Directory/Attacking AD and Windows environments`, categorized by action tier with specific refactoring instructions.

### A. Windows Notes Directory (`content/Windows/`)

| File Path / Title | Current State / Lines | Assigned Action Tier | Required Refactoring & CPTS/OSCP Enhancements |
| :--- | :--- | :--- | :--- |
| `Windows PrivEsc/Enumeration & Discovery/Automated & manual Windows enumeration.md` | Present (Substantial) | **Tier 4 (Overhaul)** | Restructure into quick-reference 5-minute triage cheat-sheet at top. Add AV/EDR detection checks (`Get-MpComputerStatus`), AppLocker policy queries, LAPS status, and output parsing guides for WinPEAS / Seatbelt / PrivescCheck. |
| `Windows PrivEsc/Enumeration & Discovery/🛠️ Kernel exploits & patch analysis.md` | Present (Draft) | **Tier 3 (Complete)** | Add exact exploitation workflows for WES-NG and Watson. Include step-by-step guides for staple exam CVEs: SeriousSAM (CVE-2021-36934), PrintNightmare (CVE-2021-34527), MS16-032, MS17-010, and CVE-2023-21768 (AFD.sys). |
| `Windows PrivEsc/Service Misconfigurations/Weak service permissions.md` | Present (30 KB Mega-Note) | **Tier 4 (Overhaul / Split)** | Split into 3 clean, modular sub-notes: (1) Service DACLs (`sc config binPath`), (2) Weak File Permissions on Executables, and (3) Unquoted Service Paths. Add `cmd.exe /c` payload wrappers to prevent service start timeouts. |
| `Windows PrivEsc/Service Misconfigurations/🛠️ Unquoted service paths.md` | Present | **Tier 2 (Align/Fmt)** | Ensure standalone file is properly linked, formatted with YAML frontmatter, scope callout, checklist, callouts, and command tables. |
| `Windows PrivEsc/Token Impersonation & Privileges/SeDebugPrivilege.md` | Present | **Tier 3 (Complete)** | Add token stealing via Incognito (`incognito.exe`), Mimikatz `token::elevate`, and code injection into `winlogon.exe` (PID targeting). |
| `Windows PrivEsc/Token Impersonation & Privileges/SeTakeOwnerShipPrivilege.md` | Present | **Tier 2 (Align/Fmt)** | Add practical exam walkthrough for taking ownership of protected service binaries (`utilman.exe` / custom services) and resetting DACLs via `takeown` and `icacls`. |
| `Windows PrivEsc/Token Impersonation & Privileges/Potato Attacks/JuicyPotato.md` | Present (17 KB) | **Tier 2 (Align/Fmt)** | Add explicit warning callout (`>[!warning]`) regarding Windows OS build boundaries (fails on Win 10 1809+ / Server 2019+). Ensure CLSID selection rules are clear. |
| `Windows PrivEsc/Token Impersonation & Privileges/Potato Attacks/PrintSpoofer.md` | Present (6 KB) | **Tier 1 (Polish)** | Polish language, ensure proper backtick formatting, add pipe creation explanation and syntax for `PrintSpoofer.exe -i -c cmd.exe`. |
| `Windows PrivEsc/Token Impersonation & Privileges/Potato Attacks/RoguePotato.md` | Present (7.8 KB) | **Tier 2 (Align/Fmt)** | Emphasize RPC traffic redirection requirements (requires port 135 listening on attacker IP or `socat` redirector). |
| `Windows PrivEsc/Token Impersonation & Privileges/Potato Attacks/GodPotato.md` | Present (5 KB) | **Tier 2 (Align/Fmt)** | Highlight that GodPotato works on modern Windows (Win 11, Server 2022) without requiring port 135 listening or CLSID brute-forcing. |
| `Windows PrivEsc/Token Impersonation & Privileges/Potato Attacks/SweetPotato.md` | Present (2.8 KB) | **Tier 1 (Polish)** | Polish syntax and maintain as automation wrapper reference. |
| `Windows PrivEsc/Privileged Groups/Backup Operators.md` | Present | **Tier 2 (Align/Fmt)** | Cross-link cleanly with `SeBackupPrivilege` and `SeRestorePrivilege`. Include `robocopy /b` usage and registry hive dumping (`reg save`). |
| `Windows PrivEsc/Privileged Groups/DnsAdmins.md` | Present | **Tier 2 (Align/Fmt)** | Ensure `ServerLevelPluginDll` attack path is complete and include cleanup command (`dnscmd /config /serverlevelplugindll`). |
| `Windows PrivEsc/Privileged Groups/Event Log Readers.md` | Present | **Tier 2 (Align/Fmt)** | Add `wevtutil` command examples for hunting process creation (Event ID 4688) with command-line arguments. |
| `Windows PrivEsc/Privileged Groups/Print Operators.md` | Present | **Tier 3 (Complete)** | Simplify C++ driver code examples by adding modern driver load utility (`EopLoadDriver`) workflow for `SeLoadDriverPrivilege`. |
| `Windows PrivEsc/Privileged Groups/Server Operators.md` | Present | **Tier 2 (Align/Fmt)** | Clean up command syntax for service binary modification and service start/stop controls. |
| `Windows PrivEsc/Privileged Groups/🛠️ Hyper-V Administrators.md` | Stub (4 lines) | **Tier 3 (Complete)** | Fully author guide on mounting VHD/VHDX virtual hard disks, VM management, and host credential extraction. |
| `Windows Commands & Scripts/🛠️ Connecting to a Windows system.md` | Present | **Tier 2 (Align/Fmt)** | Ensure complete coverage of WinRM (`evil-winrm`), RDP (`xfreerdp`), PsExec, SMBExec, WMIExec, and SSH. |
| `Windows Internals/*` (groups, UAC, COM, pipes, users, tokens) | Present | **Tier 2 (Align/Fmt)** | Format with YAML, callouts, wikilinks, and clean conceptual diagrams/tables. |
| `Windows Credential Hunting & Post-Exploitation/Windows credential hunting.md` | Present (33 KB Mega-Note) | **Tier 4 (Overhaul)** | Add top 10 search command box (`findstr`, PowerShell `Get-ChildItem`). Integrate KeePass master key extraction (`keepass2john`). Document automated mining tools (LaZagne, Snaffler, SessionGopher). |
| `Windows Credential Hunting & Post-Exploitation/🛠️ DPAPI credentials.md` | Present (23 KB) | **Tier 1 (Polish)** | Add quick-reference command box at top (`SharpDPAPI.exe`, `mimikatz dpapi::cred`). |
| `Windows Credential Hunting & Post-Exploitation/🛠️ Dumping LSASS memory.md` | Stub (4 lines) | **Tier 3 (Complete)** | Expand into master guide: `comsvcs.dll` MiniDump, ProcDump, Task Manager, PowerShell `Out-Minidump`, `SQLDumper.exe`, offline Mimikatz/Pypykatz parsing, PPL bypass via BYOVD driver (`RTCore64.sys`), and Credential Guard limitations. |

---

### B. Active Directory Notes Directory (`content/Active Directory/Attacking AD and Windows environments/`)

| File Path / Title | Current State / Lines | Assigned Action Tier | Required Refactoring & CPTS/OSCP Enhancements |
| :--- | :--- | :--- | :--- |
| `ACL attacks/AD ACL abuse.md` | Present (Substantial) | **Tier 1 (Polish)** | Current Gold Standard. Maintain structure, polish language, ensure all wikilinks are active. |
| `ACL attacks/🛠️ DCSync.md` | Present | **Tier 2 (Align/Fmt)** | Align with Gold Standard format. Detail `secretsdump.py` and Mimikatz `lsadump::dcsync` flags, plus replication extended rights requirements. |
| `ACL attacks/◯ RBCD attacks.md` | Stub (4 lines) | **Tier 3 (Complete)** | Expand into master guide covering: (1) Machine Account Quota (MAQ), (2) Creating computer account (`addcomputer.py` / PowerMad), (3) Configuring `msDS-AllowedToActOnBehalfOfOtherIdentity` (`bloodyAD` / `Set-DomainObject`), (4) Requesting S4U2self/S4U2proxy tickets (`getST.py` / Rubeus), (5) PtT. |
| `ACL attacks/◯ Shadow credentials.md` | Stub (4 lines) | **Tier 3 (Complete)** | Expand into master guide covering: KeyCredentialLink attribute modification, `pywhisker`, `Whisker`, PKINIT pre-authentication (`PKINITtools` / `Rubeus asktgt /certificate`), and certificate hash extraction. |
| `AD Enumeration & Discovery/External AD & Windows enumeration.md` | Present (Substantial) | **Tier 1 (Polish)** | Excellent content. Ensure callout fold states (`>[!abstract]+`, `>[!example]-`) and wikilinks are consistent. |
| `AD Enumeration & Discovery/Username enumeration and password spraying in AD.md` | Present | **Tier 2 (Align/Fmt)** | Ensure complete coverage of `kerbrute`, `rpcclient`, `NetExec` (SMB/WinRM/LDAP), account lockout policy checks, and smart lockout bypasses. |
| `AD Enumeration & Discovery/Querying LDAP.md` | Present | **Tier 2 (Align/Fmt)** | Detail LDAP filters (`ldapsearch`, `windapsearch`, `ldeep`), RootDSE unauthenticated queries, and custom attribute extraction. |
| `AD Enumeration & Discovery/🛠️ AD enumeration.md` & `🛠️ Authenticated AD & Windows enumeration.md` | Present | **Tier 4 (Overhaul / Merge)** | Consolidate overlapping authenticated enumeration notes into a single cohesive guide. Cover PowerView, `ActiveDirectory` PowerShell module, NetExec, and LDAP. |
| `AD Enumeration & Discovery/🛠️ BloodHound.md` | Present | **Tier 3 (Complete)** | Cover full workflow: collection (`SharpHound.exe`, `bloodhound-python`), ingest into BloodHound GUI / BloodHound CE, running cypher queries, and identifying shortest path to Domain Admin. |
| `Kerberos attacks/Kerberoasting.md` | Present | **Tier 2 (Align/Fmt)** | Cover SPN discovery, requesting TGS tickets (GetUserSPNs.py / Rubeus), offline hash cracking (`hashcat` mode 13100), and targeted Kerberoasting via `GenericWrite` on SPN. |
| `Kerberos attacks/AS-REP roasting.md` | Present | **Tier 2 (Align/Fmt)** | Cover querying accounts with `DONT_REQ_PREAUTH`, requesting AS-REP hashes (`GetNPUsers.py` / Rubeus), cracking (`hashcat` mode 18200), and targeted AS-REP roasting via UAC modification. |
| `Kerberos attacks/Overpass-the-Hash.md` | Present (Substantial) | **Tier 1 (Polish)** | Gold Standard reference. Maintain syntax. |
| `Kerberos attacks/Pass-the-Ticket.md` | Present | **Tier 2 (Align/Fmt)** | Detail `.kirbi` vs `.ccache` conversions (`ticketConverter.py`), importing tickets via Rubeus (`/ptt`) and Linux (`export KRB5CCNAME`), and ticket lifetime considerations. |
| `Kerberos attacks/◯ Golden Ticket.md` | Present | **Tier 3 (Complete)** | Detail KRBTGT hash requirement, domain SID, ticket forgery via Mimikatz (`kerberos::golden`) and Impacket (`ticketer.py`), and persistence applications. |
| `Kerberos attacks/◯ Silver Ticket.md` | Present | **Tier 3 (Complete)** | Detail targeting specific service accounts (HTTP, CIFS, MSSQL, HOST), SPN key derivation, and forging service tickets without contacting KDC. |
| `NTLM Attacks/🛠️ Pass-the-Hash.md` | Present | **Tier 2 (Align/Fmt)** | Detail PtH via SMB (`crackmapexec`/`nxc`, `smbexec.py`, `wmiexec.py`), WinRM (`evil-winrm -H`), and Mimikatz `sekurlsa::pth`. |
| `Poison and Relay/🛠️ LLMNR & NBT-NS poisoning.md` | Present | **Tier 2 (Align/Fmt)** | Cover Responder setup (`Responder -I eth0`), analyzing traffic (`-A`), capturing NTLMv1/v2 hashes, and hash cracking (`hashcat` mode 5600). |
| `Poison and Relay/◯ NTLM relay.md` & `◯ SMB relay.md` | Present | **Tier 3 (Complete)** | Consolidate and detail SMB signing requirements check, `ntlmrelayx.py` execution, relaying to SMB / LDAP / LDAPS / HTTP, and executing commands via SOCKS proxy (`proxychains`). |
| `Trust Attacks/🛠️ Child 🡺 Parent trusts.md` | Stub (4 lines) | **Tier 3 (Complete)** | Expand into master guide: Enterprise Admins privilege escalation, SID Filtering concept, ExtraSIDs forgery via Golden Ticket (`/sids:S-1-5-21-...-519`), and cross-domain DCSync. |
| `Trust Attacks/🛠️ Parent 🡺 Child trusts.md` | Stub (4 lines) | **Tier 3 (Complete)** | Detail parent-to-child trust traversal, trust key extraction, and domain escalation techniques. |
| `Trust Attacks/🛠️ Cross-forest trust abuse.md` | Stub (4 lines) | **Tier 3 (Complete)** | Cover foreign group membership, PAM trusts, Selective Authentication limitations, and mapping trust relationships via PowerView (`Get-DomainTrust`). |
| `🛠️ Privileged remote access.md` | Present | **Tier 2 (Align/Fmt)** | Detail WinRM (`evil-winrm`), PSRemoting, WMI (`wmiexec.py`), RDP (`xfreerdp`), and DCOM remote execution. |
| `🛠️ Kerberos double hop problem.md` | Present | **Tier 2 (Align/Fmt)** | Explain PowerShell remoting credential delegation issue, CredSSP solutions, and PSRemoting workarounds. |
| `🛠️ Tools.md` | Present | **Tier 2 (Align/Fmt)** | Ensure master tool table is updated with links to all tool-specific notes. |

---

## 3. Gap Analysis: Essential Missing CPTS & OSCP Topics (Tier 5 - Creation List)

To achieve 100% syllabus completeness for CPTS and OSCP, the following **10 new master notes** MUST be created from scratch following the exact Gold Standard style:

### Missing Windows PrivEsc Topics
1. **`content/Windows/Windows PrivEsc/Registry Misconfigurations/🛠️ AlwaysInstallElevated.md`**:
   - Querying registry keys (`HKLM` & `HKCU` `AlwaysInstallElevated` set to `0x1`).
   - Generating malicious MSI payloads (`msfvenom -p windows/x64/shell_reverse_tcp -f msi`).
   - Executing via `msiexec /quiet /qn /i c:\temp\payload.msi`.
2. **`content/Windows/Windows PrivEsc/Registry Misconfigurations/🛠️ Autoruns & IFEO Debugger Hijacking.md`**:
   - Enumerating autorun registry keys (`HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run`).
   - Overwriting target executables with weak file permissions.
   - Image File Execution Options (IFEO) debugger hijacking (`sethc.exe` / `utilman.exe` accessibility replace).
3. **`content/Windows/Windows PrivEsc/Service Misconfigurations/🛠️ DLL Hijacking & Search Order Exploitation.md`**:
   - Standard Windows DLL search order (`AppDir` -> `System32` -> `System` -> `CurrentDir` -> `PATH`).
   - Finding missing DLLs via Process Monitor (`ProcMon` filters: `NAME NOT FOUND`).
   - Writing malicious C/C++ DLL skeletons (`DLL_PROCESS_ATTACH` executing payload).
4. **`content/Windows/Windows PrivEsc/UAC Bypass/🛠️ UAC Bypass Techniques & Auto-Elevate.md`**:
   - Understanding UAC Integrity Levels (Medium vs High).
   - Auto-Elevate binaries (`fodhelper.exe`, `computerdefaults.exe`, `sdclt.exe`).
   - Registry hijack paths (`HKCU\Software\Classes\ms-settings\Shell\Open\command`).
   - `silentcleanup` scheduled task environment variable expansion.
5. **`content/Windows/Windows Credential Hunting & Post-Exploitation/Credential Mining/🛠️ Group Policy Preferences (GPP) & Registry.md`**:
   - Searching `SYSVOL` for `Groups.xml`, `Services.xml`, `ScheduledTasks.xml`.
   - Extracting `cpassword` attribute and decrypting with `gpp-decrypt` / `Get-GPPPassword`.
   - MS14-025 patch mitigation context.
6. **`content/Windows/Windows Credential Hunting & Post-Exploitation/LSASS & Hive Extraction/🛠️ Extracting SAM, SYSTEM & SECURITY Hives.md`**:
   - Dumping hives via `reg save HKLM\SAM c:\temp\sam.hiv`.
   - Volume Shadow Copies (`vssadmin` / `diskshadow`).
   - Parsing offline hashes using `impacket-secretsdump -sam sam.hiv -system system.hiv LOCAL`.
   - Extracting LSA Secrets (`lsadump::secrets`).
7. **`content/Windows/Windows Credential Hunting & Post-Exploitation/Pivoting & Network Post-Exploitation/🛠️ Host Recon, Port Forwarding & Pivoting.md`**:
   - Host network discovery (`netstat -ano`, `Get-NetTCPConnection`).
   - Port proxying with `netsh interface portproxy`.
   - SSH dynamic/remote port forwarding (`plink.exe`).
   - Chisel and Ligolo-ng setup on Windows hosts.

### Missing Active Directory Topics
8. **`content/Active Directory/Attacking AD and Windows environments/AD CS Attacks/🛠️ AD CS & Certipy.md`**:
   - Active Directory Certificate Services (AD CS) architecture & PKI basics.
   - Enumeration with `certipy find -vulnerable`.
   - Vulnerability breakdown: ESC1 (Enrolment rights + SAN subjectAltName specification), ESC2, ESC3, ESC4 (Vulnerable template DACL), ESC8 (NTLM relay to HTTP enrollment interface `certsrv`).
   - Requesting certificates (`certipy req`), authentication via PKINIT (`certipy auth`), and extracting NT hash.
9. **`content/Active Directory/Attacking AD and Windows environments/Kerberos Attacks/◯ Kerberos Delegation Attacks.md`**:
   - Protocol Transition & Constrained Delegation mechanics.
   - **Unconstrained Delegation**: Extracting TGTs from memory of compromised server (`sekurlsa::tickets`), forcing auth via SpoolSample / PetitPotam.
   - **Constrained Delegation**: Impersonating users via S4U2self & S4U2proxy using `getST.py` / Rubeus.
   - Cross-referencing Resource-Based Constrained Delegation (`[[◯ RBCD attacks]]`).
10. **`content/Active Directory/Attacking AD and Windows environments/AD Enumeration & Discovery/🛠️ MSSQL Enumeration & Link Abuse.md`**:
    - Enumerating MSSQL instances (`NetExec mssql`, `mssqlclient.py`).
    - Authenticating with domain credentials / hashes.
    - Executing commands via `xp_cmdshell` or `sp_OACreate`.
    - Enumerating and crawling database links (`enum_links`, `EXEC ('sp_configure...') AT [LINKED_SERVER]`).
    - Escalating privileges across nested database links.

---

## 4. Quartz Site Compatibility & Publishing Directives

Because this vault is rendered and published publicly via **Quartz**, every AI modification MUST adhere to static site generator requirements:

1. **Strict Relative Wikilinks**:
   - NEVER insert local filesystem URIs (e.g. `file:///home/...`).
   - Always use standard Obsidian Wikilink syntax: `[[Note Title]]` or `[[Note Title#Section Header|Display Text]]`.
2. **Standardized Header Levels**:
   - Heading 1 (`# Title`) should be used ONCE at the very top (or omit H1 if using filename as title, starting sections with `##`).
   - Subsections must strictly follow hierarchy: `##` -> `###` -> `####` -> `#####`.
3. **Valid Frontmatter YAML**:
   - Ensure frontmatter YAML has no syntax errors, unclosed strings, or broken lists.
   - Use standard Quartz tag formatting (alphanumeric and underscores only, e.g., `AD_attacks`).
4. **Callout Syntax Rendering**:
   - Use official Obsidian callout types supported by Quartz: `[!abstract]`, `[!important]`, `[!note]`, `[!tip]`, `[!warning]`, `[!example]`, `[!info]`.
   - Always include fold operators (`+` or `-`) to maintain clean page layout.
5. **No Orphan Notes**:
   - Every newly created note MUST be linked from at least one existing core note or roadmap (`content/Windows/roadmap.md` or `content/Active Directory/Attacking AD and Windows environments/roadmap.md`).

---

## 5. Step-by-Step AI Execution Protocol

When instructing an AI agent to begin modifying the vault content, execute the work in **5 strict phases**:

```
┌──────────────────────────────────────────────────────────────────────────┐
│ 🚀 PHASE-BY-PHASE EXECUTION PROTOCOL                                     │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │
 ┌───────────────────────────────────┼───────────────────────────────────┐
 ▼                                   ▼                                   ▼
[PHASE 1: High Priority]           [PHASE 2: Structural Align]         [PHASE 3: Split Mega-Notes]
- Fill empty stubs (4-line files)  - Add YAML, scope, checklists       - Split Weak service permissions
- RBCD, Shadow Credentials,        - Format callouts & tables          - Split Windows credential hunting
  LSASS Dumping, AD CS, Trusts     - Insert Wikilinks & References     - Consolidate AD enum notes
                                     │
 ┌───────────────────────────────────┴───────────────────────────────────┐
 ▼                                                                       ▼
[PHASE 4: Create Missing Syllabus]                                      [PHASE 5: Vault Audit & Links]
- Author 10 missing CPTS/OSCP notes                                     - Validate all Wikilinks
- AlwaysInstallElevated, GPP, SAM/SYSTEM,                               - Update master Roadmaps
  UAC Bypass, DLL Hijacking, Delegation                                 - Verify Quartz site render
```

### Phase 1: High-Priority Fixes & Blocker Stubs
1. Complete empty stubs under `ACL attacks/`: `◯ RBCD attacks.md` and `◯ Shadow credentials.md`.
2. Complete empty stub under `Windows Credential Hunting/`: `🛠️ Dumping LSASS memory.md`.
3. Complete empty stubs under `Trust Attacks/`: `🛠️ Child 🡺 Parent trusts.md`, `🛠️ Parent 🡺 Child trusts.md`, and `🛠️ Cross-forest trust abuse.md`.
4. Complete empty stub: `Windows PrivEsc/Privileged Groups/🛠️ Hyper-V Administrators.md`.

### Phase 2: Structural Alignment & Formatting Overhaul of Existing Notes
1. Audit and refactor all Tier 2 notes across `content/Windows/` and `content/Active Directory/`.
2. Apply YAML frontmatter, Scope callout, Checklist, formatted callouts, parameter tables, and References section to each file.

### Phase 3: Splitting and Re-architecting Mega-Notes
1. Re-architect `Weak service permissions.md` into modular notes: Service DACLs, Weak Binary Permissions, and Unquoted Service Paths.
2. Re-architect `Windows credential hunting.md` into quick-reference triage format with tool command boxes.
3. Merge overlapping authenticated AD enumeration notes into a consolidated master guide.

### Phase 4: Authoring Missing CPTS/OSCP Syllabus Notes from Scratch
1. Author the 10 missing Tier 5 master notes detailed in Section 3 (AD CS, Delegation, AlwaysInstallElevated, UAC Bypass, DLL Hijacking, GPP, SAM/SYSTEM hives, Host Pivoting, MSSQL links, Autoruns/IFEO).

### Phase 5: Vault-Wide Integrity, Wikilink Verification & Quartz Site Audit
1. Perform recursive wikilink check across the entire vault to ensure zero broken links.
2. Update `content/Windows/roadmap.md` and `content/Active Directory/Attacking AD and Windows environments/roadmap.md` to index every note.
3. Verify that all notes conform 100% to `[[AI Style & Formatting Guide]]`.
