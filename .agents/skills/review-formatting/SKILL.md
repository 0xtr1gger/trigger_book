---
name: review-formatting
description: >-
  Audit headings, Obsidian callouts, parameter tables, wikilinks, code blocks, and bullet points.
  Use when the user invokes /review-formatting or requests a format, layout, or Markdown audit.
---

# Formatting Review (`/review-formatting`)

This skill audits technical notes for Markdown correctness, Obsidian syntax conventions, and presentation consistency.

## Governing policies

Before reviewing, read:
1. `.editorial/policy/formatting.md`
2. `.editorial/policy/precedence.md`
3. `.editorial/memory/preferences.yaml`

## Review protocol

When given one or more target notes:

### Step 1: Run automated linter
Run the formatting linter on the target file(s):
```bash
python3 .editorial/scripts/lint_vault.py --check formatting "<target_file>"
```

### Step 2: Audit Markdown and Obsidian syntax
Inspect the note content for:
- **Headings sentence case**: Only the first word is capitalized unless a proper noun or technical acronym (e.g. `AD`, `DACL`, `Kerberos`).
- **Procedural gerunds**: Methodological sections must use action-oriented gerunds (`## Enumerating...`, `## Exploiting...`, `## Verifying...`).
- **Obsidian callouts**: Verify valid fold operators (`>[!abstract]+ Scope`, `>[!tip]+`, `>[!important]`, `>[!example]-`). Ensure verification and cleanup instructions use `>[!tip]+` callouts rather than bare H3 headings.
- **Wikilinks syntax**: Ensure internal references use `[[...]]` without backticks. Check that no markdown file links `[text](path.md)` are used for vault files.
- **Code blocks**: Check for explicit language tags (`powershell`, `bash`, `cmd`, `python`). Check that commands are clean without prompt strings (`PS C:\>`, `C:\>`).
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

