---
created: 2026-09-14
updated: 2026-09-20
tags:
  - Meta
status: incomplete
---

# AD attacks completion plan

## Purpose and authority

This file is the execution plan and state-management contract for the AI assistant ("Implementer") completing `content/Active Directory/Attacking AD and Windows environments/` into a comprehensive CPTS/OSCP-grade reference. It governs scope, ordering, and checklist state for this folder only.

- Style, terminology, Markdown, and presentation rules are governed exclusively by `.agents/skills/fix-styling/SKILL.md`. This plan does not restate them.
- `content/Uncategorized/Vault organization & content completion guide.md` already carries a Phase 2 roadmap (Steps 18–31) covering this same folder. That roadmap's checklist for Phase 2 is still all-unchecked and matches disk state reasonably well (unlike its Phase 1 WSL step, which was checked off but never actually created — verify checkmarks against disk, don't trust them blindly). This plan supersedes that roadmap's Phase 2 for day-to-day execution: it reorders the same work by actual severity found on disk and fixes a few of its inconsistencies (see Audit summary).
- This plan controls only scope, ordering, file operations, and checklist state.

## Hard constraints

- **Frontmatter**: never touch existing frontmatter. New notes get `created`, `updated`, `tags: [AD, AD_attacks]`, `status: incomplete`.
- **Preservation**: never reduce existing valid technical material. Remove content only when it is factually wrong or off-topic for the note.
- **Dual coverage**: every technique needs both Windows-side tooling (Rubeus, Mimikatz, PowerView, native `ActiveDirectory` module) and Linux attacker tooling (Impacket, NetExec, `bloodyAD`, Certipy) where the vector supports both, with flags/parameters explained.
- **No fabricated output**: do not invent command output or examples.
- **Out of scope**: `content/Active Directory/How AD works/` — do not create, edit, rename, or touch anything there. Theory belongs inline in attack notes as concise callouts, not as new standalone theory notes.
- **1 step = 1 run**: each execution finds the first unchecked step below, does only that work, checks it off, and stops. No unrelated edits to this file.
- Do not silently resolve ambiguity — if a step requires a judgment call the human hasn't made, stop and report it.

## Audit summary (2026-09-14)

Findings behind the ordering below:

- **Biggest single item**: `AD Enumeration & Discovery/🛠️ draft AD enumeration.md` is 1,950 lines of unmerged material (status `substantial`, despite the filename). It duplicates and, in places, exceeds what's in `🛠️ Authenticated AD & Windows enumeration.md` and `🛠️ BloodHound.md`. Until this is merged and retired, those two notes are not trustworthy as the canonical enumeration reference and the draft is dead weight.
- **`status: draft`** (worst true status): `NTLM Attacks/🛠️ Pass-the-Hash.md`, `Poison and Relay/🛠️ LLMNR & NBT-NS poisoning.md` — both core, heavily-tested techniques.
- **`status: incomplete`**: `ACL attacks/AD ACL abuse.md`, `ACL attacks/🛠️ DCSync.md`, `Kerberos attacks/AS-REP roasting.md`, `AD Enumeration & Discovery/🛠️ Authenticated AD & Windows enumeration.md`.
- **Genuine stubs (4–9 lines, `status: stub` or no status)** — these are real coverage gaps, not leftover junk, and cover some of the most exam-relevant AD techniques on the syllabus, so they outrank later "substantial" polish work:
  - `Kerberos attacks/◯ Golden Ticket.md`, `Kerberos attacks/◯ Silver Ticket.md`
  - `ACL attacks/◯ RBCD attacks.md`, `ACL attacks/◯ Shadow credentials.md`
  - `Poison and Relay/◯ NTLM relay.md`, `Poison and Relay/◯ SMB relay.md`
  - `Trust Attacks/🛠️ Child → Parent trusts.md`, `Trust Attacks/🛠️ Parent → Child trusts.md`, `Trust Attacks/🛠️ Cross-forest trust abuse.md`
- **Missing notes** that the parent roadmap (Steps 22–29) calls for but that don't exist on disk yet:
  - `Kerberos attacks/Diamond & Sapphire Tickets.md`
  - `Kerberos attacks/Kerberos Delegation Attacks.md`
  - `AD CS/🛠️ AD CS Attacks & Certipy.md`
  - A GPO abuse note — the parent roadmap names `GPO Abuse/Malicious GPO Abuse & Persistence.md`, but no `GPO Abuse/` folder exists; create it.
  - A LAPS note — the parent roadmap names `Credential Mining/LAPS & LAPS v2 Exploitation.md` under this AD path, but no `Credential Mining/` folder exists here (there is one under `content/Windows/`, which is a different location). Confirm placement with the human before creating a new folder; defaulting to a new `Credential Mining/` folder under this AD path if not told otherwise.
  - Note: the parent roadmap has two steps both numbered "Step 22" (Golden/Silver/Diamond Tickets, and AD ACL Abuse/DCSync). This plan does not inherit that numbering — treat it only as a heads-up if you ever cross-reference the parent file.
- **Two notes outside any existing roadmap** — flag to the human for a scope decision rather than guessing:
  - `🛠️ Infiltrating Windows.md` — reads as near-verbatim imported course material (informal prose, a hotlinked external CDN image). Needs a decision: rewrite as a proper overview note, or fold its unique content into the relevant attack notes and retire it.
  - `🛠️ Credential hunting in network shares.md` — a 6-line title-only stub with no defined scope (SYSVOL/Netlogon share hunting? general share credential mining?). Needs a decision on scope before it can be written.
- **`status: substantial`** (real content, needs polish not rescue): `External AD & Windows enumeration.md`, `Querying LDAP.md`, `Username enumeration and password spraying in AD.md`, `Kerberoasting.md`, `Overpass-the-Hash.md`, `Pass-the-Ticket.md`.
- **No `status` field, needs a status decision from the human plus light verification**: `AD Enumeration & Discovery/🛠️ AD enumeration.md`, `AD Enumeration & Discovery/🛠️ BloodHound.md`, `AD CS/🛠️ Pass-the-Certificate.md` (also needs the Step-14 extension below), `🛠️ Kerberos double hop problem.md`, `🛠️ Tools.md`.
- `roadmap.md` in this same folder is the human author's personal scratch to-do list, not an execution contract — do not edit it as part of this plan, and do not treat its checked items as authoritative either way.

## Roadmap & execution checklist

### Phase 1: Retire the enumeration draft (do first — unblocks two other notes)

- [ ] **Step 1: Merge and retire `AD Enumeration & Discovery/🛠️ draft AD enumeration.md`**
  - Extract every unique, valid command example (PowerView, `ActiveDirectory` module, NetExec, `bloodyAD`) not already present in `🛠️ Authenticated AD & Windows enumeration.md` or `🛠️ BloodHound.md`, and merge it into whichever of those two notes it belongs to.
  - Replace the draft file with a short redirect note (or delete it, if the human confirms Quartz/Obsidian backlinks allow it) — report the diff and the list of extracted material before finalizing.

### Phase 2: Decisions needed (do next — do not guess)

- [ ] **Step 2: Report scope decisions for `🛠️ Infiltrating Windows.md`, `🛠️ Credential hunting in network shares.md`, and the LAPS note's target folder**
  - Do not edit these three items yet. Present the options (rewrite vs. fold-and-retire; intended scope; folder placement) and wait for a decision before Steps 8, 11, and 13 below.

### Phase 3: Draft-status notes

- [ ] **Step 3: Finish `NTLM Attacks/🛠️ Pass-the-Hash.md`**
  - Impacket (`psexec`/`wmiexec`/`smbexec`), NetExec, Mimikatz `sekurlsa::pth`, Evil-WinRM — full dual coverage.

- [ ] **Step 4: Finish `Poison and Relay/🛠️ LLMNR & NBT-NS poisoning.md`**
  - Responder configuration (`Responder.conf`), hash harvesting, Hashcat cracking (`-m 5600`), mitm6 IPv6/WPAD takeover (`mitm6 -d domain.local`).

### Phase 4: Incomplete notes

- [ ] **Step 5: Finish `ACL attacks/AD ACL abuse.md` and `ACL attacks/🛠️ DCSync.md`**
  - ACL abuse: `GenericAll`, `GenericWrite`, `WriteDacl`, `WriteOwner`, `WriteProperty`, `Self` (`AddMember`), `ForceChangePassword` — across users, groups, computers, OUs, GPOs — via PowerView, `bloodyAD`, `dacledit.py`, `TargetedKerberoast`.
  - DCSync: `DS-Replication-Get-Changes` / `DS-Replication-Get-Changes-All` rights, via Mimikatz `lsadump::dcsync` and Impacket `secretsdump.py`.

- [ ] **Step 6: Finish `Kerberos attacks/AS-REP roasting.md`**
  - Ensure parity with the Kerberoasting note: Rubeus, Impacket `GetNPUsers.py`, Hashcat `-m 18200`, John `--format=krb5asrep`.

- [ ] **Step 7: Finish `AD Enumeration & Discovery/🛠️ Authenticated AD & Windows enumeration.md`**
  - Confirm the Step 1 merge landed cleanly and the note reads as complete on its own.

### Phase 5: Genuine stubs — core attack techniques

- [ ] **Step 8: Write `Kerberos attacks/◯ Golden Ticket.md` and `Kerberos attacks/◯ Silver Ticket.md`**
  - Golden Ticket: forgery mechanics, `krbtgt` NTLM/AES hash requirement, domain SID, ticket lifespan, Mimikatz `kerberos::golden`, Rubeus `golden`, Impacket `ticketer.py`, PtT execution, detection indicators.
  - Silver Ticket: target service account hash requirement, targeted SPN forgery (CIFS, HOST, HTTP, WMI, MSSQL), bypassing KDC validation, Mimikatz/Rubeus/Impacket syntax.

- [ ] **Step 9: Write `ACL attacks/◯ RBCD attacks.md` and `ACL attacks/◯ Shadow credentials.md`**
  - RBCD: `msDS-AllowedToActOnBehalfOfOtherIdentity` modification, fake computer account creation (`powermad`/`pywhisker`/`bloodyAD`), S4U2self/S4U2proxy via Rubeus/`getST.py`.
  - Shadow credentials: `msDS-KeyCredentialLink` abuse, certificate generation (`pywhisker`/`Whisker`), PKINIT auth (`pyPKINIT`/Rubeus `asktgt`) to obtain a TGT and NT hash.

- [ ] **Step 10: Write `Poison and Relay/◯ NTLM relay.md` and `Poison and Relay/◯ SMB relay.md`**
  - Responder + `ntlmrelayx.py`, coercion primitives (PetitPotam, PrinterBug, ShadowCoerce, DFSCoerce), SMB signing checks (`NetExec smb --gen-relay`), relay targets (LDAP/LDAPS with `--escalate-user`/RBCD injection, HTTP, SMB).

- [ ] **Step 11: Write the three Trust Attacks stubs**
  - `🛠️ Child → Parent trusts.md`, `🛠️ Parent → Child trusts.md`, `🛠️ Cross-forest trust abuse.md`: SID filtering mechanics, ExtraSids injection in Golden Tickets (`-519` Enterprise Admins SID), trust key extraction (`lsadump::trust`), cross-forest authentication, Foreign Security Principals.

### Phase 6: Missing notes

- [ ] **Step 12: Write `Kerberos attacks/Diamond & Sapphire Tickets.md`**
  - Diamond: legitimate TGT request + encrypted ticket content modification (Rubeus `diamond`). Sapphire: S4U2self-based ticket request (Rubeus `sapphire`).

- [ ] **Step 13: Write `Kerberos attacks/Kerberos Delegation Attacks.md`**
  - Unconstrained delegation (spoolss PrinterBug coercion → extract TGT from memory via Mimikatz/Rubeus). Constrained delegation with protocol transition (`TRUSTED_TO_AUTH_FOR_DELEGATION` + `getST.py -spn`).

- [ ] **Step 14: Extend `AD CS/🛠️ Pass-the-Certificate.md` and write `AD CS/🛠️ AD CS Attacks & Certipy.md`**
  - Pass-the-Certificate: extend to fully explain every term and mechanic already referenced.
  - New note: CA enumeration (`certipy find`/`Certify.exe`), ESC1–ESC8 (misconfigured templates, vulnerable ACLs, NTLM relay to HTTP web enrollment), `certipy req`/`certipy auth`, PKINIT NT hash extraction.

- [ ] **Step 15: Write the GPO abuse note (per the Step 2 decision on folder placement)**
  - GPO edit permissions, `SharpGPOAbuse`, `StandIn`, immediate scheduled tasks via GPO, local admin password push.

- [ ] **Step 16: Write the LAPS note (per the Step 2 decision on folder placement)**
  - Legacy LAPS (`ms-Mcs-AdmPwd` via NetExec/LDAP/PowerView) and Windows LAPS v2 (`msLAPS-Password` encrypted attribute reading and decryption).

### Phase 7: Substantial-tier polish

- [ ] **Step 17: Polish `External AD & Windows enumeration.md`, `Querying LDAP.md`, `Username enumeration and password spraying in AD.md`**
  - Confirm coverage of `kerbrute`, NetExec, smart-lockout rules, password policy inspection, `ldapsearch`/`windapsearch`/`ldeep`, custom LDAP filters, RootDSE interrogation.

- [ ] **Step 18: Polish `Kerberos attacks/Kerberoasting.md`, `Overpass-the-Hash.md`, `Pass-the-Ticket.md`**
  - Confirm Windows/Linux tool parity, Hashcat/John cracking syntax, `KRB5CCNAME` and `.kirbi`↔`.ccache` conversion via `ticketConverter.py`.

### Phase 8: Verification

- [ ] **Step 19: Consistency and gold-standard audit**
  - Confirm `🛠️ AD enumeration.md`, `🛠️ BloodHound.md`, `🛠️ Pass-the-Certificate.md`, `🛠️ Kerberos double hop problem.md`, `🛠️ Tools.md` each have a `status` field the human can set — flag to the human, don't set it yourself.
  - Confirm every technique that depends on a specific Windows privilege (e.g., `SeBackupPrivilege`) links to the relevant note under `content/Windows/Windows PrivEsc/Privileges/` instead of re-explaining it.
  - Confirm dual OS coverage, correct code-fence languages, and a References section on every note touched above.
  - Re-check that no other stub/duplicate files exist anywhere else under this folder.

## Progress tracking

- On completing a step, change only that step's `- [ ]` to `- [x]` in this file. Do not edit frontmatter or make unrelated changes.
- The human author verifies technical accuracy and updates each note's `status` field manually; the Implementer never sets `status` in existing notes.
