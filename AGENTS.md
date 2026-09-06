# Cybersecurity knowledge base agent instructions

This repository contains a Quartz website. 

## Repository boundaries

The documentation corpus is stored under `content/`.

Unless the user explicitly requests a Quartz website or infrastructure change:
- Only modify files under `content/` and `.editorial/`.
- Do not modify `quartz/`.
- Do not modify `quartz.config.ts`.
- Do not modify `quartz.layout.ts`.
- Do not modify package manifests, workflows, build configuration, or deployment configuration.
- Do not rename, move, or delete content notes unless explicitly requested.

## Editorial system

`.editorial/` is the authoritative editorial control system.

Before reviewing or modifying documentation, read:
1. `.editorial/policy/index.md`
2. `.editorial/policy/precedence.md`
3. The policy files relevant to the requested operation.
4. `.editorial/memory/preferences.yaml`

Do not infer the author's preferred style from arbitrary files under `content/`.

Only these sources constitute style evidence:

1. Explicit current user instructions.
2. Approved policy under `.editorial/policy/`.
3. Approved preferences under `.editorial/memory/preferences.yaml`.
4. Notes explicitly listed in `.editorial/examples/gold-notes.yaml`.
5. Approved examples in `.editorial/examples/style-cases.md`.
6. Explicit approval/rejection history when preference-learning is requested.

## Review workflow

Documentation review is diff-first.

When reviewing an existing note:

1. Audit the existing note before editing it.
2. Classify proposed changes as:
   - STYLE
   - FORMAT
   - TECHNICAL
   - COMPLETENESS
3. Give each proposal a stable identifier such as `H001`.
4. Make proposed changes only in the current review branch/worktree.
5. Show a unified Git diff before considering the changes accepted.
6. Do not commit, merge, or otherwise promote the changes until the user approves them.
7. Revert rejected changes.
8. Incorporate explicit user replacements exactly unless they introduce a technical error.
9. Show the resulting final diff again after decisions are processed.

No-change is a valid review result. Never rewrite text merely to demonstrate activity.

## Learning

Explicit acceptance, rejection, corrections, and user-written replacements are preference evidence.


Do not silently modify:

- `.editorial/policy/`
- `.agents/skills/`
- `.editorial/memory/preferences.yaml`

The preference-learning workflow may propose changes to these files as diffs.

Such changes become authoritative only after explicit user approval.

## Technical correctness

Do not change technical meaning solely to improve prose.

Technical claims must follow `.editorial/policy/technical-verification.md`.

When evidence is insufficient or conflicting, report the uncertainty rather than inventing a correction.

Technical correctness takes precedence over stylistic preference.

## Validation

After approved documentation changes:

1. Run `.editorial/scripts/lint_vault.py` against affected files.
2. Run the appropriate Quartz build validation when practical.
3. Report failures rather than hiding or bypassing them.