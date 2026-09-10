---
name: review-formatting
description: >-
  Audit headings, Obsidian callouts, parameter tables, wikilinks, code blocks, and bullet points.
  Use when the user invokes /review-formatting or requests a format, layout, or Markdown audit.
---

# Formatting Review (`/review-formatting`)

This skill audits technical notes for Markdown correctness, Obsidian syntax conventions, and presentation consistency.

## Formatting guidelines

### Headings

- **Sentence case**: Use sentence case for all headings, subheadings, and note titles: only the first word is capitalized unless a proper noun, product name, protocol, or technical acronym requires official capitalization.
- Examples:
  - `## Operational breakdown`
  - `## References and further reading`
  - `## Attacking Active Directory ACLs`
  - `Automated & manual Windows enumeration.md`

- **Heading names**: Use gerund (`-ing`) or (for shorter ones) noun headings 
  - `## Enumerating unquoted service paths` (not `## Enumeration of unquoted service paths`)
  - `## Exploiting weak service DACLs` (not `## Weak service DACL exploitation`)
  - `## Verifying elevated access` (not `## Privilege verification`)
  - `## Cleaning up payload files` (not `## Cleanup`)
  - `## Understanding [Concept]` or `## How [Concept] works` (not `## Mechanics of [Concept]`)
  - `## SOCKS proxies`
  - `## Meterpreter tunneling`

- **Numbering**: Prever describing headings using words and do not make headings numbered unless this is a methodology.

### Bullets and lists

- EVERY plain paragraph MUST be bullet-pointed if possible. If a list follows after a paragraph, use nested.
- Use numbered lists (`1.`, `2.`) only when steps form a strict sequential procedure.
- A bullet line that directly introduces a code block or enumeration of items must end with a colon (`:`).
- Explanatory bullet sentences end with a period (`.`).
- Use tabs for nested bullet indentation (NOT spaces).


### Callouts 

- Use callouts for distinct contextual purposes and preserve fold operators:

| Callout | Fold behavior | Intended usage | Canonical form |
| :--- | :--- | :--- | :--- |
| `[!abstract]` | Expanded | Scope / document objectives | `>[!abstract] **Scope**: ...` |
| `[!important]` | Default or expanded | Critical objectives, security boundaries, prerequisites | `>[!important] Objective: ...` |
| `[!note]` | Default or expanded | Protocol details and cross-references | `>[!note] See [[Kerberos]].` |
| `[!tip]` | Expanded (`+`) | Actionable verification, command tips, cleanup | `>[!tip]+ Verify membership:` |
| `[!warning]` | Default | High-risk or destructive actions | `>[!warning] Resetting the password...` |
| `[!example]` | Collapsed (`-`) | Existing raw logs and captured command output | `>[!example]- Raw output` |
| `[!info]` | Default | Operational prerequisite conditions | `>[!info] Network access required.` |

- **Verification steps** belong inside `>[!tip]+` callouts.
- **Cleanup instructions** belong inside `>[!tip]+` callouts (do NOT create `### Cleanup` headings).
- Never fabricate example tool outputs inside callouts. Preserve existing raw outputs.
---
- `>[!tip]` callouts must have no heading.
- ❌ **Bad:** 

>[!tip]+ Verifying shell access
>```bash
># commands here...
>```

- ✅ **Good:**

>[!tip]+ 
> - Verify shell access:
>```bash
># commands here...
>```

- `>[!abstract] Scope` callouts must be one-line. Scope must be defined one time per article, before any headings. 

- ❌ **Bad:** 

>[!abstract]+ Scope
>This guide covers network tunneling and port forwarding using Chisel. It details the SOCKS5 protocol handshake, WebSocket encapsulation, SSH-over-HTTP transport, static binary compilation, forward and reverse SOCKS5 tunneling, individual port forwards, authentication, parameter tables, verification, and cleanup.

- ✅ **Good:**

>[!abstract]+ **Scope**: Network tunneling and port forwarding using Chisel; SOCKS5 protocol handshake, WebSocket encapsulation, SSH-over-HTTP transport; compiling the static binary; creating forwrad and reverse SOCKS5 tunnels; forwarding individual ports; setting up authentication. 


### Code blocks & parameter breakdown tables

- Fenced code blocks must specify an explicit language identifier (`powershell`, `bash`, `python`, `c`, `yaml`, `json`).
- Use `powershell` for PowerShell commands and general Windows CLI commands.
- Keep commands clean and copy-pastable. Do not include shell prompts (such as `PS C:\>`) inside general command blocks.
- Do not put inline comment lines (`# comment`) inside code blocks; explain commands in the prose immediately preceding or following the block.
- For every non-trivial tool command, provide an explicit parameter breakdown table:

| Flag | Parameter | Description |
| :--- | :--- | :--- |
| `-u` | `jdoe` | Specifies the domain username for authentication. |
| `-p` | `'passwd123'` | Specifies the plain-text password. |
| `-d` | `example.com` | Target Active Directory domain FQDN. |

### Standard lab parameters
- Domain / FQDN: `example.com`, `dc01.example.com`
- Target IP: `10.10.11.5`
- Listener IP placeholder: `<attacker_ip_address>` (referred to in prose as "listener IP" or "listener address")
- Users: `jdoe` (first context), `rwade` (second / target context)
- Passwords: `'passwd123'`, `'new_passwd123'`

### Diagrams

- Never create any ASCII diagrams in code blocks. Either create valid Mermaid diagrams, or omit. 
- If you encounter an ASCII diagram, assess its importance for explanations, and either convert to Mermaid or remove.


### Obsidian wikilinks and cross-references

- All internal vault references MUST use wikilinks (NOT standard markdown URLs): [[🛠️ Pass-the-Hash]], [[◯ RBCD attacks]], [[Kerberos]], etc..
- **NEVER enclose wikilinks in backticks.** Write [[Kerberos]], NOT `[[Kerberos]]`.
- Standard Markdown links (`[text](url)`) are reserved strictly for external URLs.
- Do not check or validate whether wikilink target files exist on disk; the human author manages link validation.

### References and further reading

- End every note with the exact heading `## References and further reading`.
- Include hyperlinked titles pointing to official source code or documentation. Format:

```markdown
## References and further reading

- [`Overpass-the-Hash — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/kerberos/opth)
- [`Abusing Active Directory ACLs/ACEs — HackTricks`](https://hacktricks.wiki/en/windows-hardening/active-directory-methodology/acl-persistence-abuse/index.html)
- [`SpecterOps Blog`](https://posts.specterops.io/)
```

### Misc

- Use backticks for:
  - Inline code: `Get-ADUser -Identity jdoe`.
  - Command names: `chisel`, `ssh`, `curl`.
  - File paths: `C:\Users\jdoe\Documents\file.txt`.
  - IP addresses, hostnames, and FQDNs: `10.10.11.5`, etc.
  - Special keywords/protocol or tool-specific terms: `GET`, `POST`, etc.
  - Numbers, where appropriate.
  - Bullets, parameters, arguments, flags, etc. — everything appropriate for monospace formatting must be enclosed in backticks.
  - Names of external articles + sources in URLs: [`Overpass-the-Hash — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/kerberos/opth).
- If bold text + semicolon is used, the semicolon must be outside the bold text: `**Objective**: ...` (not `**Objective:** ...`).

## Review protocol

When given one or more target notes:

### Step 1: Audit Markdown and Obsidian syntax
Inspect the note content for:

- **Headings sentence case**: Only the first word is capitalized unless a proper noun or technical acronym (e.g. `AD`, `DACL`, `Kerberos`).


- **Procedural gerunds**: Methodological sections must use action-oriented gerunds (`## Enumerating...`, `## Exploiting...`, `## Verifying...`).
- **Obsidian callouts**: Verify valid fold operators (`>[!abstract]+ Scope`, `>[!tip]+`, `>[!important]`, `>[!example]-`). Ensure verification and cleanup instructions use `>[!tip]+` callouts rather than bare H3 headings.
- **Wikilinks syntax**: Ensure internal references use `[[...]]` without backticks. Check that no markdown file links `[text](path.md)` are used for vault files.
- **Code blocks**: Check for explicit language tags (`powershell`, `bash`, `python`). Check that commands are clean without prompt strings (`PS C:\>`, `C:\>`).
- **Parameter breakdown tables**: Ensure non-trivial tool invocations are accompanied by flag explanation tables.
- **Frontmatter preservation**: **NEVER modify or touch YAML frontmatter in existing notes.**

### Step 3: Classify proposals with stable IDs
Tag every proposed change as `FORMAT` with a stable identifier: `[FORMAT-001]`, `[FORMAT-002]`, etc.

### Step 4: Present unified diff
Present your proposed modifications as a **Unified Git Diff**:
- Show the line number context.
- Explain the formatting rationale for each change.
- **DO NOT commit, overwrite, or finalize the file until the user reviews and explicitly approves the diff.**

### Step 5: Process user decision
- If approved: apply the modifications.
- If rejected: revert rejected items and re-present the final diff.

### Step :  automated linter
Run the formatting linter on the target file(s):
```bash
python3 .editorial/scripts/lint_vault.py --check formatting "<target_file>"
```

### Step : Present the changes to the user

- Present proposed modifications and apply the changes.