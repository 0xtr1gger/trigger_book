# Markdown & Obsidian formatting policy

This policy governs headings, callouts, lists, code blocks, parameter tables, wikilinks, and cross-references.

## Capitalization and headings

### Sentence case
- Use sentence case for all headings, subheadings, and note titles: only the first word is capitalized unless a proper noun, product name, protocol, or technical acronym requires official capitalization.
- Examples:
  - `## Operational breakdown`
  - `## References and further reading`
  - `## Attacking Active Directory ACLs`
  - `Automated & manual Windows enumeration.md`

### Active gerund headings for procedural sections
- Use action-oriented gerund headings (`-ing` forms) for procedural and methodological sections:
  - `## Enumerating unquoted service paths` (not `## Enumeration of unquoted service paths`)
  - `## Exploiting weak service DACLs` (not `## Weak service DACL exploitation`)
  - `## Verifying elevated access` (not `## Privilege verification`)
  - `## Cleaning up payload files` (not `## Cleanup`)
  - `## Understanding [Concept]` or `## How [Concept] works` (not `## Mechanics of [Concept]`)

## Bullets and lists

- Prefer bullet points (`-`) and nested bullet points over prose blocks whenever possible.
- Use numbered lists (`1.`, `2.`) only when steps form a strict sequential procedure.
- A bullet line that directly introduces a code block must end with a colon (`:`).
- Explanatory bullet sentences end with a period (`.`).
- Use tabs for nested bullet indentation.

## Obsidian callouts

Use callouts for distinct contextual purposes and preserve fold operators:

| Callout | Fold behavior | Intended usage | Canonical form |
| :--- | :--- | :--- | :--- |
| `[!abstract]` | Expanded (`+`) | Scope, document objectives, high-level summaries | `>[!abstract]+ Scope` |
| `[!important]` | Default or expanded | Critical objectives, security boundaries, prerequisites | `>[!important] Objective: ...` |
| `[!note]` | Default or expanded | Protocol details and cross-references | `>[!note] See [[Kerberos]].` |
| `[!tip]` | Expanded (`+`) | Actionable verification, command tips, cleanup | `>[!tip]+ Verify membership:` |
| `[!warning]` | Default | High-risk or destructive actions | `>[!warning] Resetting the password...` |
| `[!example]` | Collapsed (`-`) | Existing raw logs and captured command output | `>[!example]- Raw output` |
| `[!info]` | Default | Operational prerequisite conditions | `>[!info] Network access required.` |

- **Verification steps** belong inside `>[!tip]+` callouts.
- **Cleanup instructions** belong inside `>[!tip]+` callouts (do NOT create `### Cleanup` headings).
- Never fabricate example tool outputs inside callouts. Preserve existing raw outputs.

## Code blocks & parameter breakdown tables

- Fenced code blocks must specify an explicit language identifier (`powershell`, `bash`, `cmd`, `python`, `c`, `yaml`, `json`).
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

## Obsidian wikilinks and cross-references

- All internal vault references MUST use wikilinks: `[[🛠️ Pass-the-Hash]]`, `[[◯ RBCD attacks]]`, `[[Kerberos]]`.
- **NEVER enclose wikilinks in backticks.** Write `[[Kerberos]]`, NOT `` `[[Kerberos]]` ``.
- Standard Markdown links (`[text](url)`) are reserved strictly for external URLs.
- Do not check or validate whether wikilink target files exist on disk; the human author manages link validation.

## References and further reading

- End every note with the exact heading `## References and further reading`.
- Include hyperlinked titles pointing to official source code or documentation:

```markdown
## References and further reading

- [`Overpass-the-Hash — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/kerberos/opth)
- [`Abusing Active Directory ACLs/ACEs — HackTricks`](https://hacktricks.wiki/en/windows-hardening/active-directory-methodology/acl-persistence-abuse/index.html)
- [`SpecterOps Blog`](https://posts.specterops.io/)
```

