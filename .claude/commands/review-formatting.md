# /review-formatting command for Claude Code

Audit the specified file(s) for Markdown formatting, headings, Obsidian callouts, parameter tables, and wikilinks.

## Instructions
1. Load `.agents/skills/review-formatting/SKILL.md` and read `.editorial/policy/formatting.md`.
2. Run `.editorial/scripts/lint_vault.py --check formatting "$@"` on the target file(s).
3. Audit heading sentence-casing, procedural gerunds, callout fold operators, and code blocks.
4. Enforce frontmatter preservation: **DO NOT touch YAML frontmatter in existing notes**.
5. Classify each proposal as `[FORMAT-xxx]`.
6. Present proposed modifications strictly as a **Unified Git Diff**.
7. Wait for explicit user approval before applying changes or committing.

