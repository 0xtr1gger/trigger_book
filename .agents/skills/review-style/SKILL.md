---
name: review-style
description: >-
  Audit writing style, tone, voice, and anti-AI guidelines on one or more vault notes.
  Use when the user invokes /review-style or requests an editorial review of prose, tone,
  banned words, dangling participles, or reader perspective.
---

# Style Review (`/review-style`)

This skill audits technical notes for practitioner-grade writing style, active voice, and anti-AI guidelines.

## Governing policies

Before reviewing, read:
1. `.editorial/policy/style.md`
2. `.editorial/memory/preferences.yaml`
3. `.editorial/examples/style-cases.md`

## Review protocol

When given one or more target notes:

### Step 1: Run automated linter
Run the style linter on the target file(s):
```bash
python3 .editorial/scripts/lint_vault.py --check style "<target_file>"
```

### Step 2: Audit prose against style rules
Inspect the note content for:
- **Reader perspective**: Is the reader addressed directly as "you" for all procedures? Ensure the reader is never called "the attacker".
- **Banned AI vocabulary**: Flag words like `mechanics`, `under the hood`, `in a nutshell`, `at its core`, `crucial`, `essential`, `pivotal`, `vital`, `leverage`, `utilize`, `delve`, `harness`, `seamlessly`, `robust`, `basically`, `simply`.
- **Dangling participle clauses (`-ing` tails)**: Find sentences ending in `", allowing you to..."`, `", resulting in..."`, `", leading to..."`. Rephrase them into direct cause-and-effect statements or crisp bullet points.
- **Conversational fluff**: Strip introductory greetings ("In this guide...", "Welcome to..."), closing remarks, or meta-commentary.
- **Contractions**: Ensure natural shortcuts (`can't`, `don't`, `isn't`) are used instead of robotic formal phrases.
- **Sentence length**: Aim for punchy, factual sentences (15–25 words).

### Step 3: Classify proposals with stable IDs
Tag every proposed change as `STYLE` with a stable identifier: `[STYLE-001]`, `[STYLE-002]`, etc.

### Step 4: Present unified diff
Present your proposed modifications as a **Unified Git Diff**:
- Show the line number context.
- Explain the technical or stylistic justification for each change.
- **DO NOT commit, overwrite, or finalize the file until the user reviews and explicitly approves the diff.**

### Step 5: Process user decision
- If approved: apply the modifications.
- If rejected or adjusted: revert rejected changes, incorporate user-specified replacements exactly, and show the updated diff.

