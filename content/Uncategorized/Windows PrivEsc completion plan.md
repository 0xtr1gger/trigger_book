---
created: 2026-09-14
updated: 2026-09-20
tags:
  - Meta
status: incomplete
---

# Windows PrivEsc folder completion plan

- **Scope**: `content/Windows/Windows PrivEsc/` (37 notes). Goal: bring the whole folder to a comprehensive, exam-grade Windows local privilege escalation reference for CPTS and OSCP, at the quality bar set by `[[SeDebugPrivilege]]` (checklist, precise mechanics, methodology broken into commands with parameter tables, References section, no fluff).
- Follow `content/Uncategorized/AI style & formatting guide.md` and the vault's non-duplication law (each topic lives in exactly one owning note; every other note links to it and mentions only its own angle).
- Ignore each note's `status` frontmatter field and any naming-convention inconsistencies (emoji prefixes, etc.) — neither is in scope for this plan.
- Do not touch frontmatter of existing notes. New notes get standard `Windows` / `Windows_PrivEsc` tag frontmatter.
- One checklist step below = one execution run. Mark `- [x]` and stop after finishing a step.
- Do not fabricate example command output; do not execute vault commands locally to verify them.

## All notes, prioritized

| Note | Verdict |
|---|---|
| 🛠️ Windows PrivEsc methodology.md | **Empty — write first (Step 1)** |
| Registry Misconfigurations/Modifying service registry keys.md | Duplication (Step 2) |
| Service Misconfigurations/Weak service permissions.md | Duplication, owning side (Step 2) |
| Credential Harvesting/🛠️ Dumping SAM, SYSTEM & SECURITY hives.md | Duplication (Step 3) |
| Credential Harvesting/Registry & LSA secrets.md | Duplication, owning side — gold otherwise (Step 3) |
| Credential Harvesting/Windows credential hunting.md | Duplication (Step 4) |
| Credential Harvesting/🛠️ Group Policy Preferences (GPP) & Registry.md | Duplication (Steps 4–5) |
| Credential Harvesting/🛠️ Credential Manager.md | Duplication, owning side (Step 4) |
| Potato Attacks/LocalPotato & EfxPotato.md | Technical accuracy (Step 6) |
| 🛠️ Auto-start extensibility points.md | Broken wikilink (Step 7) |
| Privileged Groups/Print Operators.md | Paste artifact (Step 8) |
| Privileges/SeTakeOwnershipPrivilege.md | Duplicated steps (Step 8) |
| Enumeration & Discovery/🛠️ Windows kernel exploits.md | Typos (Step 8) |
| Service Misconfigurations/DLL hijacking.md | Typos (Step 8) |
| Credential Harvesting/🛠️ Dumping LSASS memory.md | Broken reference link (Step 8) |
| Access tokens and impersonation.md | Stray bullet (Step 8) |
| 🛠️ UAC bypasses.md | Missing opening checklist (Step 9) |
| Credential Harvesting/🛠️ DPAPI credentials.md | Missing opening checklist (Step 9) |
| Potato Attacks/GodPotato.md | Incomplete privilege coverage (Step 10) |
| Potato Attacks/🛠️ SweetPotato.md | Thin mechanics (Step 11) |
| Privileged Groups/Network Configuration Operators.md | **Missing — new note (Step 12)** |
| WSL & Special Environments/🛠️ WSL PrivEsc & host escalation.md | **Missing — new note (Step 13)** |
| Access tokens and impersonation.md, Enumeration & Discovery/Manual & automated Windows enumeration.md, Potato Attacks/Potato attacks.md, Potato Attacks/JuicyPotato.md, Potato Attacks/PrintSpoofer.md, Potato Attacks/RoguePotato.md, Privileged Groups/Account Operators.md, Privileged Groups/Backup Operators.md, Privileged Groups/DnsAdmins.md, Privileged Groups/Event Log Readers.md, Privileged Groups/Hyper-V Administrators.md, Privileged Groups/Server Operators.md, Privileged Groups/WinRM-RDP Operators.md, Privileges/🛠️ SeBackupPrivilege & SeRestorePrivilege.md, Privileges/SeDebugPrivilege.md, Privileges/🛠️ SeLoadDriverPrivilege.md, Privileges/🛠️ SeManageVolumePrivilege.md, Registry Misconfigurations/AlwaysInstallElevated.md, Service Misconfigurations/Unquoted service paths.md | Already at gold/solid standard — no action needed |

## Execution checklist

### Priority 1 — Entry point

- [ ] **Step 1**: Write `🛠️ Windows PrivEsc methodology.md` (currently only frontmatter, zero content). Build the folder's index/decision-tree note: an enumeration checklist (privileges, group memberships, services, registry, autoruns, kernel/patch level, credentials-at-rest) that routes each finding to the matching dedicated note in this folder — mirror how `Potato Attacks/Potato attacks.md` already does this for the Potato family. This is the entry point to the whole folder; do it before anything else.

### Priority 2 — Non-duplication law violations

- [ ] **Step 2**: Resolve `Registry Misconfigurations/Modifying service registry keys.md` ↔ `Service Misconfigurations/Weak service permissions.md`. Both document the same `ModelManagerService` `ImagePath`-hijack example with near-identical commands; the former even has a self-authored TODO flagging this. `Weak service permissions.md` should own the general "writable service registry key → `ImagePath` hijack" mechanics. `Modifying service registry keys.md` should keep only its distinct angle (direct registry write access without SCM-level rights, if that distinction holds) and link to the other note instead of repeating the walkthrough.
- [ ] **Step 3**: Resolve `Credential Harvesting/🛠️ Dumping SAM, SYSTEM & SECURITY hives.md` ↔ `Credential Harvesting/Registry & LSA secrets.md`. The latter is the deeper canonical note (SYSKEY, DCC1/DCC2, NetExec automation). Trim the hive-dumping note to its own angle (hive extraction procedure: `reg save`, VSS) and link to `Registry & LSA secrets.md` for hash/secret-derivation mechanics instead of re-explaining them.
- [ ] **Step 4**: Resolve `Credential Harvesting/Windows credential hunting.md`'s duplication with `🛠️ Group Policy Preferences (GPP) & Registry.md` and `🛠️ Credential Manager.md`. The survey note fully re-walks GPP `cpassword` decryption and `cmdkey`/`vaultcmd`/`runas /savedcred` rather than linking out. Trim both subsections to a brief mention + link, keeping `Windows credential hunting.md` as the top-level index/survey note.
- [ ] **Step 5**: Trim `🛠️ Group Policy Preferences (GPP) & Registry.md`'s "Mining Windows Registry credentials" and SAM/SYSTEM/SECURITY subsections to brief cross-links — that material belongs to `Windows credential hunting.md`'s registry section and the dedicated hive-dumping note, respectively. Keep this note scoped to GPP `cpassword`.

### Priority 3 — Technical accuracy

- [ ] **Step 6**: Rewrite the mechanics section of `Potato Attacks/LocalPotato & EfxPotato.md`. Current wording is vague ("local SMB-to-RPC/HTTP context swapping", "targeting EFS or scheduled task RPC interfaces"). LocalPotato (CVE-2023-21746) is an SMB-loopback NTLM relay to RPC combined with an NTFS junction for arbitrary file write / token capture — verify the exact chain against public writeups and correct the description to the same precision as the other Potato notes.

### Priority 4 — Broken references and copyedits

- [ ] **Step 7**: `🛠️ Auto-start extensibility points.md`'s IFEO section links to `[[🛠️ IFEO debugger hijacking]]`, which no longer exists (moved to `content/.trash/`). Fold the `sethc.exe` / `utilman.exe` `Debugger`-value abuse walkthrough (the classic logon-screen accessibility-tool backdoor) directly into the IFEO section here instead of linking to a dead note — this is the only place in the vault this mechanism would live.
- [ ] **Step 8**: Fix small artifacts left from editing:
	- `Privileged Groups/Print Operators.md` — remove the trailing paste artifact after the References section (stray "operation completed successfully." plus an orphan code fence).
	- `Privileges/SeTakeOwnershipPrivilege.md` — de-duplicate the repeated steps in "Hijacking service binaries" (items 6–7 appear twice, once numbered and once as near-duplicate unnumbered text).
	- `Enumeration & Discovery/🛠️ Windows kernel exploits.md` — fix typos ("patses"→"parses", "Microsot"→"Microsoft", "WEB-GN"→"WES-NG", "acess"→"access").
	- `Service Misconfigurations/DLL hijacking.md` — fix typos ("i snot resoled", "diabled").
	- `Credential Harvesting/🛠️ Dumping LSASS memory.md` — fix the malformed trailing reference link.
	- `Access tokens and impersonation.md` — remove the stray empty bullet (line 15).

### Priority 5 — Structural polish to the gold-standard bar

- [ ] **Step 9**: Add an opening checklist to `🛠️ UAC bypasses.md` and `Credential Harvesting/🛠️ DPAPI credentials.md` — every other technique note in the folder opens with one; these two don't.
- [ ] **Step 10**: `Potato Attacks/GodPotato.md` — add the `SeAssignPrimaryTokenPrivilege` alternative path (the other Potato notes document both `SeImpersonatePrivilege` and `SeAssignPrimaryTokenPrivilege`; GodPotato covers only the former) and expand its parameter table.
- [ ] **Step 11**: `Potato Attacks/🛠️ SweetPotato.md` — tighten the BITS/WinRM abuse mechanics to the same rigor as `PrintSpoofer.md` / `RoguePotato.md`, expand its parameter table, and replace its scenario-decision content with a link to `Potato attacks.md`'s comparison table instead of repeating it.

### Priority 6 — New notes (confirmed coverage gaps, nothing elsewhere in the vault)

- [ ] **Step 12**: Create `Privileged Groups/Network Configuration Operators.md` — the group's `netsh` privileges (helper-DLL registration, WFP/firewall configuration) as a local privesc / code-execution vector. Confirmed: no dedicated note exists anywhere in the vault; only passing mentions in `Windows Internals/Windows groups.md` and an AD enumeration note.
- [ ] **Step 13**: Create `WSL & Special Environments/🛠️ WSL PrivEsc & host escalation.md` — WSL detection, root escalation inside the WSL container, credential extraction from the Linux filesystem, and writing to host Windows startup locations via `/mnt/c/`. Confirmed: no WSL privesc coverage exists anywhere in the vault.

> [!note] Local persistence techniques (hidden accounts, scheduled-task/service backdoors) are intentionally out of scope here — persistence is a post-exploitation topic, not privilege escalation, and belongs elsewhere in the vault.
