---
name: review-all
description: >-
  Run a comprehensive multi-dimensional editorial audit (Style, Formatting, Technical Accuracy, Completeness).
  Use when the user invokes /review-all or combines multiple reviews (e.g. /review-style /review-formatting).
---

# Comprehensive Vault Note Review (`/review-all`)

This skill executes a complete, end-to-end editorial audit across all four dimensions: Style, Formatting, Technical Accuracy, and Completeness.

## Governing policies

1. `.editorial/policy/index.md`
2. `.editorial/policy/precedence.md`
3. `.editorial/policy/style.md`
4. `.editorial/policy/formatting.md`
5. `.editorial/policy/technical-verification.md`
6. `.editorial/policy/structure.md`

## Review protocol

When given one or more target notes:

### Step 1: Run deterministic linter
```bash
python3 .editorial/scripts/lint_vault.py "<target_file>"
```

### Step 2: Perform 4-stage audit
Execute each audit pass in order of precedence:
1. **Technical Accuracy**: Ensure statements are true, commands are accurate, and mechanics are qualified. (Proposals tagged `[TECH-xxx]`).
2. **Completeness**: Ensure Scope, Enumeration, Exploitation, Verification, Cleanup, and References are present. (Proposals tagged `[COMPL-xxx]`).
3. **Style & Anti-AI Tone**: Ensure practitioner tone, "you" perspective, direct cause-and-effect, no dangling participles, and no banned vocabulary. (Proposals tagged `[STYLE-xxx]`).
4. **Formatting**: Ensure sentence case headings, gerund procedural headings, valid callouts, wikilinks without backticks, parameter tables, and clean code blocks. (Proposals tagged `[FORMAT-xxx]`).

### Step 3: Enforce preservation & boundaries
- **NEVER** modify existing YAML frontmatter.
- **NEVER** reduce valid technical material.

### Step 4: Present unified diff
Present the consolidated changes as a single **Unified Git Diff**:
- Group proposed changes by section.
- Clearly annotate each proposed edit with its category and identifier (e.g., `[STYLE-001]`, `[FORMAT-002]`).
- **DO NOT commit, overwrite, or finalize the file until the user reviews and explicitly approves the diff.**

### Step 5: Process user decision
- Apply approved proposals.
- Revert any rejected proposals.
- Re-present final clean diff.

