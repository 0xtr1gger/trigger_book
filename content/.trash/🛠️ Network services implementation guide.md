---
created: 2026-09-22
updated: 2026-09-26
tags:
  - services_n_protocols
---

# Network services implementation guide

This document is the standard reference and operational tracking roadmap for standardizing and completing all network services notes in the vault.

---

## Two-tier architecture

The knowledge base organizes network service notes into a **two-tier hierarchy**:

```
                  [[🛠️ Penetration testing methodology]]
                                    │
                                    ▼ (Open ports discovered)
          ┌───────────────────────────────────────────────────┐
          │  Tier 1: [[🛠️ Attacking network services]]         │
          │  - Central rapid triage & initial probing hub     │
          │  - Strictly facts, commands, minimal notes        │
          │  - Direct wikilinks into deep-dive articles       │
          └─────────────────────────┬─────────────────────────┘
                                    │ (Deeper analysis & misconfig checks)
            ┌───────────────────────┼───────────────────────┐
            ▼                       ▼                       ▼
    [[🛠️ FTP]]             [[🛠️ SSH]]             [[🛠️ SMB]] ... (Tier 2 notes)
    - Protocol mechanics    - Protocol mechanics    - Protocol mechanics
    - In-depth enum         - In-depth enum         - In-depth enum
    - Parameter tables      - Parameter tables      - Parameter tables
    - Misconfigurations     - Misconfigurations     - Misconfigurations
    - Credential attacks    - Credential attacks    - Credential attacks
```

### Tier 1: Central hub (`🛠️ Attacking network services.md`)
- **Purpose**: Fast-paced command cheat-sheet for live penetration testing engagements.
- **Content density**: Strictly facts, high-value commands, and wikilinks. No theoretical explanations or conversational filler.
- **Section structure** (`## <Protocol Name>`):
	1. Top callout linking to dedicated note (`>[!note] See [[🛠️ <Protocol>]].`).
	2. Default ports & quick service identification / banner grabbing.
	3. Primary enumeration commands (targeted Nmap scripts, banner probes).
	4. Anonymous / default authentication checks.
	5. Rapid credential brute-forcing / password spraying command.
	6. Basic triage actions (e.g., listing shares, downloading files, testing execution).

SIBLING SECTIONS MUST BE STRUCTURED AND FRAMED IN A VERY SIMILAR WAY (whenever and ONLY IF practical)

### Tier 2: Dedicated protocol notes (`🛠️ <Protocol>.md`)
- **Purpose**: Comprehensive technical deep-dive, theoretical background, protocol mechanics, edge cases, misconfigurations, and post-authentication interaction.
- **Content density**: Detailed procedural explanations, bulleted paragraphs, RFC context, comprehensive parameter breakdown tables, and official references.
- **Section structure**:
	1. Frontmatter (preserved untouched).
	2. Protocol overview & mechanics (`## <Protocol>` or `## How <Protocol> works`).
	3. Enumeration & reconnaissance (`## Enumerating <Protocol>`).
	4. Misconfigurations & unauthorized access (`## Assessing anonymous / default access`, etc.).
	5. Credential testing & brute-forcing (`## Brute-forcing credentials`).
	6. Service interaction & privilege escalation (`## Interacting with <Service>`, `## Abusing <Feature>`).
	7. Verification & cleanup callouts (`>[!tip]+`).
	8. References section (`## References and further reading`).
	9. (Optional) Appendices
- Rather than sticking to the above section structure, attempt to derive it from sibling notes if something is unclear.

SIBLING NOTES MUST BE STRUCTURED AND FRAMED IN A VERY SIMILAR WAY (whenever and ONLY IF practical)


MAIN RULE: DO NOT REMOVE ANY RELEVANT TECHNICAL INFORMATION

---


The main objective is to make all notes nearly identical in terms of style and structure, but for different protocols and with different commands when needed. The context itself should change, each specific note may add its own sections or omit those present in other notes if irrelevant, but the main rule remains: the grammar, phrasing, wording, headings, structure must be standarnized, the same. 
The main problem with prose is its grammar and sentence construction. No fluff, no introductory stuff, and sentences must be constructed in the correct way, grammativelly perfect.

Therefore, it's best to use previous notes to standarize everything.


## Editorial & formatting standards

1. **Headings**:
	- **Sentence case**: Capitalize only the first word and proper nouns / technical acronyms (e.g., `## Enumerating Active Directory shares`, `## Brute-forcing credentials`).
	- **Gerund/noun style**: Action headings must use either `-ing` verbs (e.g., `## Enumerating FTP servers`, not `## FTP Enumeration`) or nouns (prefer the simplest option).
2. **Bullets & paragraphs**:
	- Explanatory prose must be bullet-pointed.
	- Bullet lines introducing code blocks or lists must end with a colon (`:`).
	- Explanatory bullet sentences end with a period (`.`).
	- Tab indentation for nested bullets (no space indentation).
3. **Callouts**:
	- `>[!note]` for cross-references, protocol notes, and RFCs.
	- `>[!tip]+` with no title for actionable tips, verification steps, and cleanup.
	- `>[!important]` for operational constraints and prerequisites.
	- `>[!warning]` for dangerous, locking, or destructive actions.
4. **Code blocks & parameter tables**:
	- Explicit language tags (`bash`, `powershell`, `python`).
	- Clean commands without shell prompt characters (`$`, `#`, `PS C:\>`).
	- Non-trivial commands should include a parameter breakdown table (`| Option | Description |`); if a command used multiple times in a section, put the breakdown after all uses.
5. **Obsidian wikilinks**:
	- Use `[[Note Name]]` or `[[Note Name|Alias]]`.
	- Never enclose wikilinks in backticks.
	- Standard Markdown links `[text](url)` strictly for external URLs.
6. **Standard lab placeholders**:
	- Domain / FQDN: `example.com`, `dc01.example.com`
	- Target IP: `10.10.11.5`
	- Attacker IP / Listener: `<attacker_ip_address>`
	- Accounts: `jdoe`, `rwade`
	- Passwords: `'passwd123'`, `'new_passwd123'`

NEVER modify or make up raw command output in `[!example]`.

Custom: no scope abstract for these notes.
---

## Single-stage AI run protocol

When executing an individual protocol stage, the implementer AI must follow these 5 steps:

1. **Step 1: Inspect files**
	- Read the protocol section in `content/Attacking Enterprise Networks/Services & Protocols/🛠️ Attacking network services.md`.
	- Read the full dedicated note in `content/Attacking Enterprise Networks/Services & Protocols/🛠️ <Protocol>.md`.
2. **Step 2: Rework central hub section**
	- Strip out theoretical text and ensure the section is strictly facts, high-value commands, and wikilinks.
	- Verify uniform structure: header wikilink, quick identification, NSE scripts, anonymous check, brute-force, quick actions.
3. **Step 3: Refactor and extend dedicated note**
	- Standardize sentence-case gerund headings and bulleted prose.
	- Add complete parameter breakdown tables for all non-trivial commands.
	- Wrap verification and cleanup steps inside `>[!tip]+` callouts.
	- Ensure `## References and further reading` heading at the bottom with official references.
4. **Step 4: Harmonize wikilinks**
	- Verify bidirectional cross-references between the hub section and the dedicated note.
5. **Step 5: Update stage checklist**
	- Mark the corresponding stage checkbox as completed (`- [x]`) in this implementation guide note.

---

## Stage tracking checklist

- [x] **Stage 1: FTP**
	- Hub section: `## FTP` in [[🛠️ Attacking network services methodology|🛠️ Attacking network services methodology]]
	- Dedicated note: [[FTP|FTP]]
- [x] **Stage 2: SSH**
	- Hub section: `## SSH` in [[🛠️ Attacking network services methodology|🛠️ Attacking network services methodology]]
	- Dedicated note: [[SSH|SSH]]
- [x] **Stage 3: SMB**
	- Hub section: `## SMB` in [[🛠️ Attacking network services methodology|🛠️ Attacking network services methodology]]
	- Dedicated note: [[SMB|SMB]]
- [x] **Stage 4: NFS**
	- Hub section: `## NFS` in [[🛠️ Attacking network services methodology|🛠️ Attacking network services methodology]]
	- Dedicated note: [[NFS|NFS]]
- [x] **Stage 5: SMTP**
	- Hub section: `## SMTP` in [[🛠️ Attacking network services methodology|🛠️ Attacking network services methodology]]
	- Dedicated note: [[SMTP|SMTP]]
- [x] **Stage 6: IMAP & POP3**
	- Hub sections: `## IMAP` & `## POP3` in [[🛠️ Attacking network services methodology|🛠️ Attacking network services methodology]]
	- Dedicated notes: [[IMAP|IMAP]] & [[POP3|POP3]] (split from the former consolidated `🛠️ IMAP & POP3` note)
- [x] **Stage 7: SNMP**
	- Hub section: `## SNMP` in [[🛠️ Attacking network services methodology|🛠️ Attacking network services methodology]]
	- Dedicated note: [[SNMP|SNMP]]
- [x] **Stage 8: MySQL**
	- Hub section: `## MySQL` in [[🛠️ Attacking network services methodology|🛠️ Attacking network services methodology]]
	- Dedicated note: [[MySQL|MySQL]]
- [x] **Stage 9: MSSQL**
	- Hub section: `## MSSQL` in [[🛠️ Attacking network services methodology|🛠️ Attacking network services methodology]]
	- Dedicated note: [[MSSQL|MSSQL]]
- [x] **Stage 10: RDP**
	- Hub section: `## RDP` in [[🛠️ Attacking network services methodology|🛠️ Attacking network services methodology]]
	- Dedicated note: [[Attacking Enterprise Networks/Services & Protocols/🛠️ RDP|🛠️ RDP]]
- [x] **Stage 11: WinRM**
	- Hub section: `## WinRM` in [[🛠️ Attacking network services methodology|🛠️ Attacking network services methodology]]
	- Dedicated note: [[Attacking Enterprise Networks/Services & Protocols/🛠️ WinRM|🛠️ WinRM]]
- [x] **Stage 12: IPMI**
	- Hub section: `## IPMI` in [[🛠️ Attacking network services methodology|🛠️ Attacking network services methodology]]
	- Dedicated note: [[Attacking Enterprise Networks/Services & Protocols/🛠️  IPMI|🛠️  IPMI]]
- [x] **Stage 13: DNS**
	- Hub section: `## DNS` in [[🛠️ Attacking network services methodology|🛠️ Attacking network services methodology]]
	- Dedicated note: [[Attacking Enterprise Networks/Services & Protocols/Querying DNS|Querying DNS]] (or `🛠️ DNS`)
- [x] **Stage 14: Oracle TNS**
	- Hub section: `## Oracle TNS` in [[🛠️ Attacking network services methodology|🛠️ Attacking network services methodology]]
	- Dedicated note: [[Attacking Enterprise Networks/Services & Protocols/🛠️ Oracle TNS|🛠️ Oracle TNS]]
- [x] **Stage 15: Final synchronization & top triage audit**
	- Central port table & overview alignment in [[🛠️ Attacking network services methodology|🛠️ Attacking network services methodology]]
	- Vault-wide cross-reference audit across all service notes



