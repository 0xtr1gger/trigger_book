---
created: 2026-08-22
updated: 2026-09-20
tags:
  - Meta
status: complete
---

# Core execution guide: Windows & Active Directory attacks 

## Authority, purpose, and relationship to the style guide

- This file is the authoritative execution plan and state-management contract for the AI assistant referred to as **Implementer** (such as Claude Sonnet, Claude Opus, Gemini, or GPT-4o). It governs what the Implementer may touch, what work it performs in each run, preservation requirements, scope boundaries, and the ordered implementation roadmap for:
	1. `content/Windows/`
	2. `content/Active Directory/Attacking AD and Windows environments/`

- The target audience is cybersecurity professionals, penetration testers, and CPTS / OSCP / OSCP+ certification candidates. The completed vault must function as a cohesive, high-density, practitioner-grade professional reference manual.
- Use `content/Uncategorized/AI style & formatting guide.md` as the authoritative source for writing, terminology, Markdown, Obsidian, code-block, and presentation rules.

### Precedence contract

- This **core execution guide** controls scope, file operations, preservation, run boundaries, checklist state, and the roadmap.
- The **AI style & formatting guide** controls language, terminology, headings, bullets, callouts, tables, code presentation, references, and cross-reference presentation.
- A roadmap step may impose a step-specific requirement that is more specific than a general style rule; that step-specific requirement wins for that step.
- Do not silently resolve any `[[DECISION ...]]` placeholder. If a placeholder affects the current step and no option has been selected by the human author, stop before making the affected edit and report the unresolved decision.


## System directives and hard constraints

### 1. Frontmatter policy 

#### EXISTING notes

- NEVER modify, update, remove, reorder, normalize, or otherwise touch any line of existing YAML frontmatter.
- Existing note status values (such as `status: draft`, `status: incomplete`, `status: substantial`, and `status: complete`) belong EXCLUSIVELY to the human author for manual verification.
- Touch **ZERO lines** of frontmatter in existing notes.

#### NEW notes

- Every NEWLY created note MUST begin with this YAML frontmatter structure:

```yaml
---
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags:
  - AD
  - AD_attacks
status: incomplete
---
```

- Preserve fixed tags `AD` and `AD_attacks` for new AD notes, and `Windows` and `Windows_PrivEsc` for new Windows notes.

### 2. Preservation of technical material

- NEVER reduce already covered material.
- Preserve all VALID and RELEVANT technical facts, commands, mechanics, payload details, paths, registry keys, permissions, flags, concrete examples, and tool names already present in existing notes. 
- You may reorganize, rewrite, deduplicate redundant wording, and improve presentation without changing technical meaning.
- You may remove material only when it is technically invalid or irrelevant to the note topic; DO NOT remove valid material merely for concision or stylistic smoothness.
- Do not add unsupported technical claims.

### 3. Path accuracy and link verification

- All target file paths in this guide match exact relative paths on disk. Always verify file paths before editing.
- Create Obsidian wikilinks when relevant, for example `[[🛠️ Pass-the-Hash]]`, `[[◯ RBCD attacks]]`, and `[[Kerberos]]`.
- Never enclose wikilinks in backticks.
- Do not verify wikilinks, search for broken wikilinks, check whether target files exist, or run post-edit link-validation searches. The human author handles link validation manually.
- Follow the style guide for the exact presentation of internal versus external references.

### 4. Scope

- All work must focus on practical, actionable, exam-relevant enumeration, exploitation, privilege escalation, post-exploitation, and closely necessary mechanics for CPTS and OSCP / OSCP+.
- Minor theory and protocol mechanics belong directly inside attack or enumeration notes, normally as concise callouts.
- `content/Active Directory/How AD works/` is OUT OF SCOPE. Do not create, edit, rename, or modify files in that directory.
- DO NOT create new standalone theory notes in `How AD works/`.
- Preserve existing theory already present in in-scope notes when it is technically valid and relevant.

### 5. English and style standardization

- Eliminate conversational fluff and intro/outro filler such as “In this guide we will...” and “Hope this helps!”.
- Use practitioner-grade, technically precise English.
- Fix grammatical inconsistencies, unnatural phrasing, fragments, spelling errors, inconsistent terminology, and inconsistent section naming.
- Apply every applicable rule in `content/Uncategorized/AI style & formatting guide.md`.

### 6. Command dual-coverage and parameter explanation rules

- Provide **BOTH** Windows natively executed commands (CMD / PowerShell / Sysinternals) **AND** Linux remote attacker commands (Impacket / NetExec / Rubeus / Certipy / Hashcat) whenever a vector can be executed from either platform.
- For every non-trivial command snippet or tool invocation, include an explicit breakdown of key flags and parameters (in parameter tables or structured callout lists).
- Code blocks must use explicit language identifiers (`powershell`, `cmd`, `bash`, `c`, `python`, `yaml`, `json`).


## Gold Standard note architecture

- Modified and newly created notes SHOULD use this architecture:

```
[YAML Frontmatter]  <-- only for NEW notes; never edit frontmatter in EXISTING notes
  │
  ├── Document title (H2)
  ├── Actionable Checklist section (- [ ] task boxes)
  ├── Conceptual grounding & mechanics (> quote or >[!note])
  ├── Methodological breakdown (## Enumeration / ## Exploitation)
  │    ├── Windows command blocks (```powershell / ```cmd)
  │    ├── Linux command blocks (```bash)
  │    ├── Parameter & flag tables / breakdown lists
  │    └── Raw tool outputs (>[!example]-)
  └── References and further reading (## References and further reading)
```

- The Gold Standard Architecture is a preferred template; omit top-level components when genuinely inapplicable.
- Add a checklist only when the note describes an actionable sequential workflow. If added, the checklist must be placed at the beginning of the note, after the first heading, separated with delimiters (`---`) and not headers.
- YOU DO NOT GENERATE FABRICATED/RAW EXAMPLE COMMAND OUTPUT. YOU DO NOT CREATE EXAMPLES, AND DO NOT MODIFY EXISTING EXAMPLES. Command examples and procedural examples are allowed. Existing examples remain untouched.
- The style guide defines exact sentence case, code fences, bullets, callout syntax, tables, terminology, and references.


## Implementer execution engine (1 step = 1 AI run)

- ONE roadmap **STEP** equals ONE Implementer AI execution RUN.
- On each run, the Implementer MUST check the execution checklist and find the **FIRST unchecked step** (`- [ ]`).
- Execute only the instructions belonging to that step while following all general directives.
- Do not continue into later unchecked steps in the same run.
- After completing the step, change only that roadmap step marker from `- [ ]` to `- [x]`, then stop.
- This checklist is the persistent state manager and supports incremental human review between runs.
- When marking progress in this guide, do not make unrelated edits to the roadmap or this file.

>[!note] You may consult previously finished notes to gain more contextual understanding of the expected style (up to 2 notes per run).


---

## Roadmap & Execution Checklist

### Phase 1: `content/Windows/` Implementation Roadmap

#### Module 1: System Enumeration & Patch Analysis

- [x] **Step 1: Refactor Windows System Enumeration**
  - **Target File**: `content/Windows/Windows PrivEsc/Enumeration & Discovery/Automated & manual Windows enumeration.md`
  - **Operation**: `[POLISH & REFACTOR]`
  - **Instructions**: Preserve all existing content. Restructure into clean H2/H3 headings. Include an instant 5-minute triage cheat-sheet (`netstat -ano`, `tasklist /svc`, `sc.exe query`, `Get-MpComputerStatus`, `wmic qfe`). Ensure comprehensive coverage of automated tools (`PrivescCheck`, `winPEAS`, `Seatbelt`, `PowerUp`).

- [x] **Step 2: Finish Kernel Exploits & Patch Analysis**
  - **Target File**: `content/Windows/Windows PrivEsc/Enumeration & Discovery/🛠️ Windows kernel exploits.md`
  - **Operation**: `[POLISH & FINISH]`
  - **Instructions**: Reformat to fit style guide. Ensure comprehensive coverage of Watson, WES-NG workflow, UBR (Update Build Revision) patch analysis, CVE-2021-36934 (SeriousSAM / HiveNightmare), CVE-2021-34527 (PrintNightmare local EOP), CVE-2023-21768 (AFD.sys), and CVE-2023-28252 (CLFS.sys). Include exact compilation, delivery, and execution commands for classic exam CVEs (MS16-032, MS17-010). Cover kernel security mitigations (KASLR, SMEP, SMAP, HVCI/VBS, kCFG) and BYOVD (Bring Your Own Vulnerable Driver) concepts.

#### Module 2: Service Misconfigurations & DLL Hijacking

- [x] **Step 3: Refactor Weak Service Permissions**
  - **Target File**: `content/Windows/Windows PrivEsc/Service Misconfigurations/🛠️ Weak service permissions.md`
  - **Operation**: `[POLISH & REFACTOR]`
  - **Instructions**: Reorganize into modular sections: 1) Service DACLs (`sc.exe config binPath`), 2) Weak Executable File Permissions (`icacls`), 3) Unquoted Service Paths cross-reference. Add `cmd.exe /c` payload wrappers to prevent service start timeouts. Add verification callouts (`>[!tip]+`). Use `sc.exe` rather than `sc` to avoid confusion with PowerShell alias.

- [x] **Step 4: Unquoted Service Paths & DLL Hijacking**
  - **Target Files**:
    1. `content/Windows/Windows PrivEsc/Service Misconfigurations/Unquoted service paths.md`
    2. `content/Windows/Windows PrivEsc/Service Misconfigurations/DLL hijacking.md`
  - **Operation**: `[FINISH & EXPAND]`
  - **Instructions**: Complete `Unquoted service paths.md` with full detection (`wmic service get name,displayname,pathname,startmode`, PowerShell CIM queries) and step-by-step exploitation methodology. Expand `DLL hijacking.md` detailing KnownDLLs registry key, standard Windows DLL search order (`AppDir` -> `System32` -> `System` -> `CurrentDir` -> `PATH`), phantom DLL identification via Process Monitor, CrowdStrike DLL hijacking taxonomy (Search order, Phantom DLL, Relative path, DLL Redirection), DLL proxying via `SharpDllProxy`, and C/C++ payload code snippets spawning `cmd.exe` or reverse shells.

#### Module 3: Registry Misconfigurations

- [x] **Step 5: Registry Privilege Escalation Vectors**
  - **Target Files**:
    1. `content/Windows/Windows PrivEsc/Registry Misconfigurations/AlwaysInstallElevated.md`
    2. `content/Windows/Windows PrivEsc/🛠️ Auto-start extensibility points.md`
    3. `content/Windows/Windows PrivEsc/Registry Misconfigurations/🛠️ Modifying service registry keys.md`
  - **Operation**: `[POLISH & REFACTOR]`
  - **Instructions**: Standardize dedicated registry attack notes:
    - `AlwaysInstallElevated`: Reg query checks (`HKCU` & `HKLM`), `msfvenom` MSI payload creation, silent installation (`msiexec /quiet /qn /i`).
    - `🛠️ Auto-start extensibility points.md`: Autorun key enumeration, binary swapping, Image File Execution Options (`Debugger` value abuse for `sethc.exe`/`utilman.exe`), scheduled tasks, and startup directory persistence/privesc.
    - `Modifying service registry keys`: Abusing write access to `HKLM\SYSTEM\CurrentControlSet\Services\<ServiceName>` (`ImagePath` modification via `reg add` / PowerShell).

#### Module 4: Token Impersonation, Privileges & Potato Attacks

- [x] **Step 6: Access Token Mechanics & Privileges**
  - **Target Files**:
    1. `content/Windows/Windows PrivEsc/Token Impersonation & Privileges/Access tokens and impersonation.md`
    2. `content/Windows/Windows PrivEsc/Token Impersonation & Privileges/SeDebugPrivilege.md`
    3. `content/Windows/Windows PrivEsc/Token Impersonation & Privileges/SeTakeOwnerShipPrivilege.md`
  - **Operation**: `[POLISH & REFACTOR]`
  - **Instructions**: Refactor `Access tokens and impersonation.md` covering Primary vs Delegation tokens, Impersonation levels, and token privileges. Refactor `SeDebugPrivilege.md` covering Incognito (`incognito.exe`), Mimikatz `token::elevate`, LSASS dump privileges, and shellcode injection. Refactor `SeTakeOwnerShipPrivilege.md` covering step-by-step `takeown` / `icacls` hijacking of protected service binaries.

- [x] **Step 7: Potato Attacks Evolution & LocalPotato / EfxPotato**
  - **Target Files**:
    1. `content/Windows/Windows PrivEsc/Token Impersonation & Privileges/Potato Attacks/🛠️ Potato Attacks Overview & OS Matrix.md` `[NEW]`
    2. `content/Windows/Windows PrivEsc/Token Impersonation & Privileges/Potato Attacks/GodPotato.md`
    3. `content/Windows/Windows PrivEsc/Token Impersonation & Privileges/Potato Attacks/JuicyPotato.md`
    4. `content/Windows/Windows PrivEsc/Token Impersonation & Privileges/Potato Attacks/PrintSpoofer.md`
    5. `content/Windows/Windows PrivEsc/Token Impersonation & Privileges/Potato Attacks/RoguePotato.md`
    6. `content/Windows/Windows PrivEsc/Token Impersonation & Privileges/Potato Attacks/SweetPotato.md`
    7. `content/Windows/Windows PrivEsc/Token Impersonation & Privileges/Potato Attacks/LocalPotato & EfxPotato.md` `[NEW]`
  - **Operation**: `[NEW & POLISH]`
  - **Instructions**: Create `Potato Attacks Overview & OS Matrix.md` comparing OS support (Win 7 to Win 11 / Server 2022), Port 135 requirements, DCOM object dependence, RPC requirements, and target privilege requirements (`SeImpersonatePrivilege` / `SeAssignPrimaryTokenPrivilege`). Polish existing potato notes to match formatting standards. Create `LocalPotato & EfxPotato.md` documenting local SMB-to-HTTP/RPC relay mechanics bypassing modern Windows 11 / Server 2022 patches.

- [x] **Step 8: Specialized Privileges Exploitation (SeBackup, SeRestore, SeLoadDriver, SeManageVolume)**
  - **Target Files**:
	  1. `content/Windows/Windows Internals/Windows Privileges.md` — (for this specific step, it is IN SCOPE) describes Windows privileges and has dedicated sections to explain in detail privileges mentioned in the notes below. It does not cover privilege escalation, but only talks about legitimate priivlege functionaality. 
	  2. `content/Windows/Windows PrivEsc/Token Impersonation & Privileges/SeDebugPrivilege.md`
	  3. `content/Windows/Windows PrivEsc/Token Impersonation & Privileges/SeTakeOwnerShipPrivilege.md`
	  4. `content/Windows/Windows PrivEsc/Token Impersonation & Privileges/SeBackupPrivilege & SeRestorePrivilege.md`
	  5. `content/Windows/Windows PrivEsc/Token Impersonation & Privileges/SeLoadDriverPrivilege & SeManageVolumePrivilege.md` `
  - **Operation**: `[POLISH]`
  - **Instructions**: Consistency and polishing of specialized techniques using Windows privileges:
	  - Extend and complete `content/Windows/Windows Internals/Windows Privileges.md` to make it a comprehensive reference to Windows privileges. Each section specifically dedicated to a privilege (e.g., `## SeDebugPrivilege`) should cover the privilege completely, including what is currently the respected privesc note (e.g., `Windows PrivEsc/Token Impersonation & Privileges/SeDebugPrivilege.md`) but not covering exploitation. If there is no such section, create it. 
	  - Each of the notes mentioned below should 1. give a definition to a privilege; 2. refer to the respective section in `Windows Priivleges.md` with explanations of that specific privielege; 3. explain why it is a privilege escalation vector; 4. polish sections with escalation techniques. Explanations about the privilege itself should be moved to the central `Windows Privileges.md`.
		  1. `content/Windows/Windows PrivEsc/Token Impersonation & Privileges/SeDebugPrivilege.md`
		  2. `content/Windows/Windows PrivEsc/Token Impersonation & Privileges/SeTakeOwnerShipPrivilege.md`
		  3. `content/Windows/Windows PrivEsc/Token Impersonation & Privileges/SeBackupPrivilege & SeRestorePrivilege.md`
		  4. `content/Windows/Windows PrivEsc/Token Impersonation & Privileges/SeLoadDriverPrivilege & SeManageVolumePrivilege.md` `
#### Module 5: Abusing Privileged Groups

- [x] **Step 9: Group Hijacking (Backup Operators, DnsAdmins, Event Log Readers)**
  - **Target Files**:
    1. `content/Windows/Windows PrivEsc/Privileged Groups/Backup Operators.md`
    2. `content/Windows/Windows PrivEsc/Privileged Groups/DnsAdmins.md`
    3. `content/Windows/Windows PrivEsc/Privileged Groups/Event Log Readers.md`
  - **Operation**: `[POLISH & REFACTOR]`
  - **Instructions**: Reformat to fit style guide. Ensure `Backup Operators.md` covers `diskshadow`, `reg save`, `robocopy /b`, and `SeRestorePrivilege`. Ensure `DnsAdmins.md` covers `ServerLevelPluginDll` payload execution via `dnscmd.exe` and service restart cleanup. Ensure `Event Log Readers.md` covers `wevtutil` Event ID 4688 process creation log hunting and Security log credential mining.
  - As for the techniques that rely on a specific privilege (such as `SeBackupPrivilege`) granted to a group rather than specific group capabilities, instead of repeating the information, refer to the appropriate technique from `content/Windows/Windows PrivEsc/Token Impersonation & Privileges/Privileges` (e.g., `SeBackupPrivilege.md`). The content must be consistent.

- [x] **Step 10: Group Hijacking (Print Operators, Server Operators, Hyper-V, Remote Users, Account Operators)**
  - **Target Files**:
    1. `content/Windows/Windows PrivEsc/Privileged Groups/Print Operators.md`
    2. `content/Windows/Windows PrivEsc/Privileged Groups/Server Operators.md`
    3. `content/Windows/Windows PrivEsc/Privileged Groups/🛠️ Hyper-V Administrators.md`
    4. `content/Windows/Windows PrivEsc/Privileged Groups/WinRM-RDP Operators.md` `[NEW]`
    5. `content/Windows/Windows PrivEsc/Privileged Groups/Account Operators.md` `[NEW]`
  - **Operation**: `[POLISH, FINISH STUB, & NEW]`
  - **Instructions**: Reformat `Print Operators.md` (add `EopLoadDriver` for driver loading) and `Server Operators.md` (abusing weak service modification). Fill stub `🛠️ Hyper-V Administrators.md` (VHD/VHDX mounting, shadow copies, VM privilege escalation). Create `WinRM-RDP Operators.md` covering `Remote Management Users` (Evil-WinRM access), `Remote Desktop Users` (`xfreerdp`), and `Distributed COM Users`. Create `Account Operators.md` detailing non-protected user/group creation and privilege modification.
  - As for the techniques that rely on a specific privilege (such as `SeBackupPrivilege`) granted to a group rather than specific group capabilities, instead of repeating the information, refer to the appropriate technique from `content/Windows/Windows PrivEsc/Token Impersonation & Privileges/Privileges` (e.g., `SeBackupPrivilege.md`). The content must be consistent.

#### Module 6: Advanced Escalation & Specialized Environments

- [x] **Step 11: UAC Bypass Techniques & Auto-Elevate**
  - **Target Files**:
    1. `content/Windows/Windows PrivEsc/🛠️ UAC bypasses.md`
  - **Operation**: `[POLISH & FINISH]`
  - **Instructions**: Complete `🛠️ UAC bypasses.md` covering UAC integrity levels (Medium vs High), consent prompt behavior, auto-elevate binaries (`fodhelper.exe`, `sdclt.exe`, `computerdefaults.exe`), registry hijacking (`ms-settings` and `shell\open\command`), `silentcleanup` scheduled task environment variable expansion, and COM object abuse (`ICMLuaUtil` / `CMLuaUtil`). Include both PowerShell manual commands and `Akagi` / `UACME` references.
  
- [x] **Step 12: WSL PrivEsc & Host Escalation**
  - **Target Files**:
    1. `content/Windows/Windows PrivEsc/WSL & Special Environments/🛠️ WSL PrivEsc & Host Escalation.md` `[NEW]`
  - **Operation**: `[NEW]`
  - **Instructions**: Create WSL escalation note covering WSL detection (`wsl -l -v`, checking `/proc/version`), root escalation inside WSL container (`sudo -l`, suid binaries), extracting Linux credentials (`/etc/shadow`, bash history), and writing host Windows startup binaries / scheduled tasks via `/mnt/c/`.

#### Module 7: Windows Saved Credentials & Secret Mining

- [x] **Step 13: DPAPI Credentials & GPP Decryption**
  - **Target Files**:
    1. `content/Windows/Windows Credential Hunting & Post-Exploitation/Windows credential hunting.md`
    2. `content/Windows/Windows Credential Hunting & Post-Exploitation/🛠️ DPAPI credentials.md`
    3. `content/Windows/Windows Credential Hunting & Post-Exploitation/Credential Mining/🛠️ Group Policy Preferences (GPP) & Registry.md` `[NEW]`
  - **Operation**: `[POLISH, REFACTOR, & NEW]`
  - **Instructions**: Refactor `Windows credential hunting.md` adding an executive summary table with top 10 credential search commands (`findstr`, `Get-ChildItem`). Polish `🛠️ DPAPI credentials.md` detailing master keys, preferred files, domain backup keys (`DPAPI-dump`), and Chrome/Vault decryption. Create `🛠️ Group Policy Preferences (GPP) & Registry.md` covering `SYSVOL` `cpassword` XML search, `gpp-decrypt`, `Get-GPPPassword`, and AutoLogon registry credentials (`DefaultUserName`, `DefaultPassword`).

#### Module 8: LSASS Dumping, Hive Extraction & Post-Exploitation

- [x] **Step 14: Hive Extraction & Local Persistence**
  - **Target Files**:
    1. `content/Windows/Windows Credential Hunting & Post-Exploitation/🛠️ Dumping SAM, SYSTEM & SECURITY hives.md` `[NEW]`
  - **Operation**: `[NEW]`
  - **Instructions**: Create `Extracting SAM, SYSTEM & SECURITY Hives`: saving hives (`reg save`), `vssadmin` shadow copy, `impacket-secretsdump -sam LOCAL`, LSA secrets dumping (`lsadump::secrets`).


- [x] **Step 15: LSASS Dumping & PPL Bypass**
  - **Target Files**:
    1. `content/Windows/Windows Credential Hunting & Post-Exploitation/🛠️ Dumping LSASS memory.md`
  - **Operation**: `[POLISH & FINISH]`
  - **Instructions**: Polish `🛠️ Dumping LSASS memory.md` ensuring full coverage of `comsvcs.dll` `MiniDump`, `Procdump`, Task Manager, PowerShell `Out-Minidump`, `SQLDumper`, offline parsing with Mimikatz `sekurlsa::minidump` & Pypykatz, LSA protection (PPL) bypass via BYOVD driver (`RTCore64.sys` / `mimidrv.sys`), and Credential Guard context; must also explain PPL.

- [ ] **Step 16: Local Persistence**
	- **Target Files**:
		1. `content/Windows/Windows Credential Hunting & Post-Exploitation/Local Persistence/🛠️ Windows local persistence techniques.md` `[NEW]`
	  - **Operation**: `[NEW]`
	  - **Instruction**: Create `Windows local persistence techniques`: Registry Run keys, service creation (`sc.exe create`), scheduled tasks, sticky keys/utilman hijacking, WMI event subscriptions, DLL proxying, Netsh helper DLLs, and other techniques for Windows persistence. Make sure you explain each carefully.

- [ ] **Step 17: Pivoting**
  - **Target Files**:
    1. `content/Windows/Windows Commands & Scripts/🛠️ Connecting to a Windows system.md`
    2. `content/Windows/Windows Commands & Scripts/🛠️ Windows file transfers.md`
    3. `content/Windows/Windows Credential Hunting & Post-Exploitation/🛠️ Privileged remote access.md`
  - **Operation**: `[POLISH, FINISH STUB]`
  - **Instructions**: Reformat `Connecting to a Windows system.md` (WinRM, RDP, SMB/psexec/wmiexec/smbexec). Polish `🛠️ Windows file transfers.md` (`certutil`, PowerShell `Invoke-WebRequest`, SMB, HTTP, Base64 encoding). Finish stub `🛠️ Privileged remote access.md`.

### Phase 2: `content/Active Directory/Attacking AD and Windows environments/` Implementation Roadmap

#### Module 9: AD Enumeration & Discovery

- [ ] **Step 18: External Recon & Domain User Enumeration**
  - **Target Files**:
    1. `content/Active Directory/Attacking AD and Windows environments/AD Enumeration & Discovery/External AD & Windows enumeration.md`
    2. `content/Active Directory/Attacking AD and Windows environments/AD Enumeration & Discovery/Username enumeration and password spraying in AD.md`
    3. `content/Active Directory/Attacking AD and Windows environments/AD Enumeration & Discovery/Querying LDAP.md`
  - **Operation**: `[POLISH & REFACTOR]`
  - **Instructions**: Reformat to fit style guide. Ensure `External AD & Windows enumeration.md` covers unauthenticated SMB/LDAP interrogation, NTLM info disclosure, Kerberos user enumeration (`kerbrute`). Ensure `Username enumeration and password spraying in AD.md` covers `kerbrute`, `NetExec`, smart lockout rules, and password policy inspection. Ensure `Querying LDAP.md` covers `ldapsearch`, `windapsearch`, `ldeep`, custom LDAP filters, and RootDSE interrogation.

- [ ] **Step 19: Authenticated AD Enumeration & BloodHound Integration**
  - **Target Files**:
    1. `content/Active Directory/Attacking AD and Windows environments/AD Enumeration & Discovery/🛠️ AD enumeration.md`
    2. `content/Active Directory/Attacking AD and Windows environments/AD Enumeration & Discovery/🛠️ Authenticated AD & Windows enumeration.md`
    3. `content/Active Directory/Attacking AD and Windows environments/AD Enumeration & Discovery/🛠️ BloodHound.md`
    4. `content/Active Directory/Attacking AD and Windows environments/AD Enumeration & Discovery/🛠️ draft AD enumeration.md`
  - **Operation**: `[POLISH & MERGE DRAFT]`
  - **Instructions**: Review the 1950-line `🛠️ draft AD enumeration.md`. Extract all valuable unique command examples (PowerView, ActiveDirectory module, `NetExec`, `bloodyAD`) and merge them into `🛠️ Authenticated AD & Windows enumeration.md` and `🛠️ BloodHound.md`. Replace `🛠️ draft AD enumeration.md` with a clean note or redirect. Ensure `🛠️ BloodHound.md` covers `SharpHound.exe`, `bloodhound-python`, custom Cypher queries, and edge analysis.

#### Module 10: Kerberos Attacks

- [ ] **Step 20: Kerberoasting, AS-REP Roasting & Ticket attacks**
  - **Target Files**:
    1. `content/Active Directory/Attacking AD and Windows environments/Kerberos attacks/Kerberoasting.md`
    2. `content/Active Directory/Attacking AD and Windows environments/Kerberos attacks/AS-REP roasting.md`
    3. `content/Active Directory/Attacking AD and Windows environments/Kerberos attacks/Overpass-the-Hash.md`
    4. `content/Active Directory/Attacking AD and Windows environments/Kerberos attacks/Pass-the-Ticket.md`
  - **Operation**: `[POLISH & REFACTOR]`
  - **Instructions**: Reformat to fit style guide. Ensure clear distinction between Windows tools (Rubeus, Mimikatz) and Linux tools (Impacket `GetUserSPNs.py`, `GetNPUsers.py`, `getTGT.py`, `getST.py`). Add hash cracking syntax for Hashcat (`-m 13100` for Kerberoast, `-m 18200` for AS-REP) and John the Ripper (`--format=krb5tgs`, `--format=krb5asrep`). Include ticket handling (`KRB5CCNAME`, `.kirbi` to `.ccache` conversion via `ticketConverter.py`).

- [ ] **Step 21: Pass-The-Certificate**
	- **Target Files**:
		1. `content/Active Directory/Attacking AD and Windows environments/AD CS/🛠️ Pass-the-Certificate`
	- **Operation**: `[EXTEND, POLISH & REFACTOR]`
	- **Instructions**: Extend the technical material to comprehensive explain all terms and how all techniques work. Reformat to fit style guide.

- [ ] **Step 22: Golden, Silver, Diamond & Sapphire Tickets**
  - **Target Files**:
    1. `content/Active Directory/Attacking AD and Windows environments/Kerberos attacks/◯ Golden Ticket.md`
    2. `content/Active Directory/Attacking AD and Windows environments/Kerberos attacks/◯ Silver Ticket.md`
    3. `content/Active Directory/Attacking AD and Windows environments/Kerberos attacks/Diamond & Sapphire Tickets.md` `[NEW]`
  - **Operation**: `[FINISH STUBS & NEW]`
  - **Instructions**: Complete the stubs:
    - `◯ Golden Ticket.md`: Ticket forgery mechanics, `krbtgt` NTLM/AES hash requirement, domain SID, ticket lifespan, Mimikatz (`kerberos::golden`), Rubeus (`golden`), Impacket (`ticketer.py`), PtT execution, detection indicators.
    - `◯ Silver Ticket.md`: Target service account hash requirement, targeted SPN service ticket forgery (CIFS, HOST, HTTP, WMI, MSSQL), bypassing KDC validation, command syntax for Mimikatz, Rubeus, Impacket.
    - `Diamond & Sapphire Tickets.md`: Requesting legitimate TGT and modifying encrypted ticket contents (Diamond ticket via Rubeus `diamond`) vs requesting ticket via S4U2self (Sapphire ticket via Rubeus `sapphire`).

#### Module 11: ACL Attacks, Delegation & Domain Escalation

- [ ] **Step 22: AD ACL Abuse, DCSync & AdminSDHolder**
  - **Target Files**:
    1. `content/Active Directory/Attacking AD and Windows environments/ACL attacks/AD ACL abuse.md`
    2. `content/Active Directory/Attacking AD and Windows environments/ACL attacks/🛠️ DCSync.md`
  - **Operation**: `[POLISH & REFACTOR]`
  - **Instructions**: Reformat `AD ACL abuse.md` and `🛠️ DCSync.md`. Ensure complete coverage of ACL control rights: `GenericAll`, `GenericWrite`, `WriteDacl`, `WriteOwner`, `WriteProperty`, `Self` (`AddMember`), `ForceChangePassword` across users, groups, computers, OUs, and GPOs using PowerView, `bloodyAD`, `dacledit.py`, and `TargetedKerberoast`. Ensure `DCSync.md` covers `DS-Replication-Get-Changes` and `DS-Replication-Get-Changes-All` rights via Mimikatz (`lsadump::dcsync`) and Impacket `secretsdump.py`.

- [ ] **Step 23: Kerberos Delegation (Unconstrained, Constrained, RBCD)**
  - **Target Files**:
    1. `content/Active Directory/Attacking AD and Windows environments/ACL attacks/◯ RBCD attacks.md`
    2. `content/Active Directory/Attacking AD and Windows environments/Kerberos attacks/Kerberos Delegation Attacks.md` `[NEW]`
  - **Operation**: `[FINISH STUB & NEW]`
  - **Instructions**: Complete stub `◯ RBCD attacks.md` (`msDS-AllowedToActOnBehalfOfOtherIdentity` attribute modification, fake computer account creation via `powermad` / `pywhisker` / `bloodyAD`, S4U2self / S4U2proxy exchange with Rubeus / `getST.py`). Create `Kerberos Delegation Attacks.md` covering Unconstrained Delegation (spoolss PrinterBug coercion -> extract TGT from memory via Mimikatz/Rubeus) and Constrained Delegation with Protocol Transition (`TRUSTED_TO_AUTH_FOR_DELEGATION` + `sddl` / `getST.py -spn`).

- [ ] **Step 24: Shadow Credentials & LAPS Abuse**
  - **Target Files**:
    1. `content/Active Directory/Attacking AD and Windows environments/ACL attacks/◯ Shadow credentials.md`
    2. `content/Active Directory/Attacking AD and Windows environments/Credential Mining/LAPS & LAPS v2 Exploitation.md` `[NEW]`
  - **Operation**: `[FINISH STUB & NEW]`
  - **Instructions**: Complete stub `◯ Shadow credentials.md` (`msDS-KeyCredentialLink` attribute abuse, certificate generation via `pywhisker` / `Whisker`, `PKINIT` authentication via `pyPKINIT` / Rubeus `asktgt` to obtain TGT and NT hash). Create `LAPS & LAPS v2 Exploitation.md` covering Legacy LAPS (`ms-Mcs-AdmPwd` attribute reading via `NetExec`, LDAP, PowerView) and Windows LAPS / LAPS v2 (`msLAPS-Password` encrypted attribute reading & decryption).

#### Module 12: Poisoning, Relay & NTLM Attacks

- [ ] **Step 25: LLMNR/NBT-NS/mDNS Poisoning & mitm6**
  - **Target Files**:
    1. `content/Active Directory/Attacking AD and Windows environments/Poison and Relay/🛠️ LLMNR & NBT-NS poisoning.md`
  - **Operation**: `[POLISH & EXPAND]`
  - **Instructions**: Polish `🛠️ LLMNR & NBT-NS poisoning.md` covering Responder configuration (`Responder.conf`), hash harvesting, Hashcat cracking (`-m 5600`), and mitm6 IPv6 DNS takeover with WPAD proxying (`mitm6 -d domain.local`).

- [ ] **Step 26: NTLM & SMB Relaying with Coercion Primitives**
  - **Target Files**:
    1. `content/Active Directory/Attacking AD and Windows environments/Poison and Relay/◯ NTLM relay.md`
    2. `content/Active Directory/Attacking AD and Windows environments/Poison and Relay/◯ SMB relay.md`
    3. `content/Active Directory/Attacking AD and Windows environments/NTLM Attacks/🛠️ Pass-the-Hash.md`
  - **Operation**: `[FINISH STUBS & POLISH]`
  - **Instructions**: Polish `🛠️ Pass-the-Hash.md` (Impacket `psexec`/`wmiexec`/`smbexec`, `NetExec`, Mimikatz `sekurlsa::pth`, Evil-WinRM). Complete stubs `◯ NTLM relay.md` and `◯ SMB relay.md`: Responder + `ntlmrelayx.py`, coercion primitives (PetitPotam, PrinterBug, ShadowCoerce, DFSCoerce), SMB signing requirements check (`NetExec smb --gen-relay`), relaying to LDAP/LDAPS (`--escalate-user` / RBCD injection), HTTP, and SMB.

#### Module 13: Domain Trusts, AD CS & Specialized Tools

- [ ] **Step 27: Domain Trusts Abuse (Child 🡺 Parent, Parent 🡺 Child, Cross-Forest)**
  - **Target Files**:
    1. `content/Active Directory/Attacking AD and Windows environments/Trust Attacks/🛠️ Child 🡺 Parent trusts.md`
    2. `content/Active Directory/Attacking AD and Windows environments/Trust Attacks/🛠️ Parent 🡺 Child trusts.md`
    3. `content/Active Directory/Attacking AD and Windows environments/Trust Attacks/🛠️ Cross-forest trust abuse.md`
  - **Operation**: `[FINISH STUBS & POLISH]`
  - **Instructions**: Complete trust stubs (`Child 🡺 Parent`, `Parent 🡺 Child`, `Cross-forest`): SID filtering mechanics, ExtraSids injection in Golden Tickets (`-519` Enterprise Admins SID), trust key extraction (`lsadump::trust`), cross-forest authentication, and Foreign Security Principals (FSP).

- [ ] **Step 28: AD CS Attacks & Certipy (ESC1-ESC13, ESC8 Relay)**
  - **Target Files**:
    1. `content/Active Directory/Attacking AD and Windows environments/AD CS/🛠️ AD CS Attacks & Certipy.md` `[NEW]`
  - **Operation**: `[NEW]`
  - **Instructions**: Create comprehensive AD CS note: Certificate Authority enumeration via `certipy find` / `Certify.exe`, ESC1 (misconfigured template with `ENROLLEE_SUPPLIES_SUBJECT`), ESC2, ESC3, ESC4 (vulnerable ACLs), ESC6, ESC7, ESC8 (NTLM relay to HTTP web enrollment), authentication via `certipy req` & `certipy auth`, and PKINIT NT hash extraction.

- [ ] **Step 29: Malicious GPO Abuse, Remote Access & Kerberos Double Hop**
  - **Target Files**:
    1. `content/Active Directory/Attacking AD and Windows environments/GPO Abuse/Malicious GPO Abuse & Persistence.md` `[NEW]`
    2. 
    3. `content/Active Directory/Attacking AD and Windows environments/🛠️ Kerberos double hop problem.md`
    4. `content/Active Directory/Attacking AD and Windows environments/🛠️ Tools.md`
  - **Operation**: `[NEW & POLISH]`
  - **Instructions**: Create `Malicious GPO Abuse & Persistence.md` covering GPO edit permissions, `SharpGPOAbuse`, `StandIn`, immediate scheduled tasks via GPO, and local admin password push. Polish `🛠️ Privileged remote access.md`, `🛠️ Kerberos double hop problem.md` (PSRemoting creds passing, CredSSP, Kerberos delegation), and `🛠️ Tools.md`.

#### Module 14: Verification & Consistency Audit

- [ ] **Step 30: Global Checklist & Consistency Audit**
  - **Operation**: `[VERIFY]`
  - **Instructions**: Audit all generated and refactored notes across `content/Windows/` and `content/Active Directory/Attacking AD and Windows environments/`. Verify that all note architecture components match the Gold Standard, all command blocks are double-covered (Windows native + Linux remote), all parameter tables are filled, and no raw fabricated output exists.
- [ ] **Step 31: Global References and Further Reading Audit**


---

## Verification & progress tracking for human & Implementer

- When the Implementer completes a step, it **MUST ONLY** change `- [ ] Step X` to `- [x] Step X` inside section **Road map & Execution Checklist** of this file.
- **DO NOT** edit frontmatter in modified content notes.
- The human author will periodically review completed notes, verify technical accuracy against CPTS/OSCP standards, and update YAML frontmatter `status` fields manually.
