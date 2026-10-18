---
created: 2026-08-21
updated: 2026-09-20
tags:
  - Meta
status: complete
---
How to Use
You can invoke any review skill directly:

Single Category Review:
text

/review-style content/Uncategorized/tcpdump.md
text


/review-formatting content/Windows/.../note.md
Compound or Full Review:
text


/review-all content/Uncategorized/tcpdump.md
Batch Processing:
text


/review-formatting content/note1.md content/note2.md
Preference Learning:
text


/editorial-learn "Reject F002: In networking notes, keep 'NIC' capitalized rather than expanding to network interface controller."

# AI style & formatting guide: persona, language, and Obsidian documentation rules

## Authority and scope

- This file is the definitive style and presentation reference for any AI Implementer model (such as Claude Sonnet, Opus, Gemini, GPT-4o) or human author writing documentation inside the vault.
- It governs writing style, technical tone, terminology, document hierarchy, Obsidian Markdown, code formatting, callouts, and internal/external references.
- Scope includes:
	- `content/Windows/`
	- `content/Active Directory/Attacking AD and Windows environments/`

- The **Implementer core execution guide** (`content/Uncategorized/Vault organization & content completion guide.md`) controls execution order, scope boundaries, file operations, and roadmap state. This style guide controls writing style, presentation, and formatting.


## Writing style & anti-AI guidelines

### Plain, factual, and direct prose (Factual & No-Fluff)

- Write in a plain, direct, practitioner-grade style.
- State facts directly without fluff, dramatic narrative, pseudo-academic introductory filler, or artificial hype.
- Keep sentences short, simple, and punchy (aim for 15–25 words per sentence).
- Avoid fluff phrasing such as "In this section...", "It is important to remember...", "Note that...", or "As previously discussed...".
- Focus purely on what the configuration is, how to detect it, how to exploit it, how to verify execution, and how to clean up.
- ❌ No text diagrams (if needed, only valid mermaid is accepted).

### Banned AI vocabulary and fluff terms

- Never use pseudo-academic AI filler words or overused AI buzzwords.
- **Banned word list**:
	- `Mechanics` (e.g., do NOT use "Underlying mechanics", "Mechanics of...", or "Conceptual grounding & mechanics" as headings or introductory fluff). Use `How [Vector] works` or `Security model`.
	- `Under the hood` / `In a nutshell` / `At its core`
	- `Crucial` / `Essential` / `Pivotal` / `Vital`
	- `Leverage` (use *use*, *abuse*, or *exploit*)
	- `Utilize` (use *use*)
	- `Seamlessly` / `Robust` / `Comprehensive` / `Delve` / `Harness`
	- `Basically` / `Simply` / `Obviously` / `Clearly`

### Banned adverbial participle clauses (`-ing` tails)

VERY IMPORTANT
USE DIRECT CAUSE-AND-EFFECT SENTENCES OR CRISP BULLET POINTS

- WHAT YOU MUST NOT DO: append dangling participle phrases (`-ing` clauses) to the end of sentences to explain results. This creates repetitive, robotic, and unnatural text.
- **NEVER** end explanatory sentences with dangling participles such as:
	- ❌ *"...allowing an attacker to escalate privileges."*
	- ❌ *"...leading to arbitrary code execution."*
	- ❌ *"...resulting in a system crash."*
	- ❌ *"...enabling unauthenticated  user access."*
	- ❌ *"...granting SYSTEM privileges."*
- **Rephrase into direct cause-and-effect sentences or crisp bullet points**:
	- ❌ *Bad:* "The service executes binary files with SYSTEM privileges, allowing you to escalate privileges."
	- ✅ *Good:* "The service executes as `SYSTEM`. Replacing the binary gives you `SYSTEM` code execution."
	- ❌ *Bad:* "Run `whoami /all`, displaying the active user SID and privileges."
	- ✅ *Good:* "Run `whoami /all` to display your SID, group memberships, and assigned privileges."

### Mandatory shortcuts

- Use "can't", "don't", and other shortcuts where applicable instead of "cannot", "do not" (except where emphasize is needed), even though the overall style is formal.
### Zero conversational fluff

- Eliminate all meta-commentary, introductory greetings, marketing language, dramatic phrasing, soft conclusions, and generic closing statements.
- Forbidden introductory and closing patterns:
	- ❌ "In this guide, we will explore..."
	- ❌ "Welcome to my notes on..."
	- ❌ "Hope this helps with your exam prep!"
	- ❌ "Summary:" (when used as generic closing filler)
	- ❌ "As you can see..."
- Start immediately with frontmatter for new notes, followed by the main document title and scope callout.


## Capitalization, headings, and section naming

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


## Reader voice and perspective

- Address the reader directly as **"you"** for all procedural instructions, conditions, and checks.
- **Never call the reader "the attacker".**
- Use generic role nouns only when describing a systemic security context on the machine:
	- "a low-privileged user"
	- "a privileged service account"
	- "an administrator session"
- Do not mix "you", "the attacker", and "low-privileged user" interchangeably when referring to the same participant in a single scenario.
- Use explicit targets: "the target system", "the target service", "the target executable" (avoid ambiguous bare "target").


## Document structure and Gold Standard architecture

- Notes should follow this logical structure:

```
[YAML Frontmatter]  <-- NEW notes only; never edit frontmatter in EXISTING notes
  │
  ├── Document title (H2 sentence case)
  ├── Actionable checklist (- [ ] task boxes)
  ├── Scope / High-level summary (> [!abstract]+ Scope)
  ├── How [Concept] works (Brief factual explanation, no "Mechanics" fluff)
  ├── Methodological breakdown
  │    ├── ## Enumerating [Vector]
  │    ├── ## Exploiting [Vector]
  │    ├── Windows command blocks (```powershell / ```cmd)
  │    ├── Linux command blocks (```bash)
  │    ├── Parameter & flag tables
  │    └── Raw tool outputs (>[!example]-)
  └── References and further reading (## References and further reading)
```

- Add a checklist only when the note describes an actionable sequential workflow. If added, place it after the first heading, separated with delimiters (`---`) and not section headers.
- Do not fabricate raw example command output.
- Good scope callout examples:

>[!abstract]+ **Scope**: Local Windows privilege escalation and persistence via misconfigured autorun registry keys, startup directories, scheduled tasks, Winlogon configurations, PowerShell profiles, Command Processor `AutoRun`, WMI event subscriptions, and advanced auto-start locations.

> [!abstract]+ **Scope**: Access tokens; primary, impersonation, and delegation tokens; impersonation levels; token privileges relevant to privilege escalation.

## Bullets, procedures, and terminology

### Bullet formatting

- Use bullets (`-`) for facts, conditions, individual checks, alternative commands, and explanatory observations.
- Use numbered lists (`1.`, `2.`) only when steps form a strict sequential procedure.
- A bullet line that directly introduces a command block should end with a colon.
- Explanatory paragraphs and bullet sentences end with a period.
- Use tabs for nested bullet indentation.

### Precise terminology

- **executable / executable file** — the file on disk.
- **service executable path** — the configured path to the binary.
- `binPath` — Windows SCM service binary path property.
- **payload** — code or file used to demonstrate execution; do not call every binary or script a payload.
- **replacement executable** — file substituted in place of a legitimate binary.
- `SYSTEM` / `NT AUTHORITY\SYSTEM` — operating system security context.
- **permissions on** — preferred over "permissions over".
- **write access to** — preferred over "write access over".
- **listener IP / listener address** — address receiving callbacks (keep placeholder `<attacker_ip_address>` in command blocks, but refer to it as listener IP/address in prose).


## Obsidian wikilinks and cross-references

- Create Obsidian wikilinks for internal vault references, e.g. `[[🛠️ Pass-the-Hash]]`, `[[◯ RBCD attacks]]`, `[[Kerberos]]`.
- **NEVER enclose wikilinks in backticks.** Write `[[Kerberos]]`, NOT `` `[[Kerberos]]` ``.
- All internal vault references MUST use wikilinks (`[[...]]`). Markdown links (`[text](url)`) are reserved strictly for external URLs.
- Do not check or validate whether wikilink target files exist on disk; the human author manages link validation.


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

- Verification steps belong inside `>[!tip]+` callouts.
- Cleanup instructions belong inside `>[!tip]+` callouts (do NOT create `### Cleanup` headings).
- Never fabricate example tool outputs inside callouts.


## Code blocks, syntax highlighting, and parameter tables

- Fenced code blocks must specify an explicit language identifier (`powershell`, `bash`, `cmd`, `python`, `c`, `yaml`).
- Use `powershell` for PowerShell commands and general Windows CLI commands.
- Keep commands clean and copy-pastable. Do not include shell prompts (such as `PS C:\>`) inside general command blocks.
- Do not put inline comment lines (`# comment`) inside code blocks; explain commands in the prose immediately preceding or following the block.
- For every non-tr0ivial tool command, provide an explicit parameter breakdown table or structured list explaining the key flags:

| Flag | Parameter | Description |
| :--- | :--- | :--- |
| `-u` | `jdoe` | Specifies the domain username for authentication. |
| `-p` | `'passwd123'` | Specifies the plain-text password. |
| `-d` | `example.com` | Target Active Directory domain FQDN. |

- Standard lab parameters to use across all notes:
	- Domain / FQDN: `example.com`, `dc01.example.com`
	- Target IP: `10.10.11.5`
	- Listener IP placeholder: `<attacker_ip_address>` (referred to in prose as "listener IP" or "listener address")
	- Users: `jdoe` (first context), `rwade` (second / target context)
	- Passwords: `'passwd123'`, `'new_passwd123'`


## References and further reading

- End every note with the exact heading `## References and further reading`.
- Include hyperlinked titles pointing to official source code or documentation:

```markdown
## References and further reading

- [`Overpass-the-Hash — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/kerberos/opth)
- [`Abusing Active Directory ACLs/ACEs — HackTricks`](https://hacktricks.wiki/en/windows-hardening/active-directory-methodology/acl-persistence-abuse/index.html)
- [`SpecterOps Blog`](https://posts.specterops.io/)
```


## Formatting summary & editing checklist

When writing or polishing notes, enforce this checklist:
- [ ] No conversational fluff, greetings, or meta-commentary.
- [ ] No banned words (`Mechanics`, `under the hood`, `in a nutshell`, `crucial`, `leverage`, `utilize`, `delve`, `robust`).
- [ ] No dangling participle clauses (`-ing` tails like "...allowing an attacker to...").
- [ ] Sentence case for all headings and note titles.
- [ ] Action-oriented gerund headings for procedure sections (`## Enumerating...`, `## Exploiting...`, `## Verifying...`).
- [ ] Reader addressed consistently as "you" (never "the attacker").
- [ ] Obsidian wikilinks `[[...]]` without backticks for internal references.
- [ ] Code blocks with language tags (`powershell`, `bash`, `python`) and parameter breakdown tables.
- [ ] Existing frontmatter untouched on existing files; new frontmatter added to new files.
