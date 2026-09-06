# /review-all command for Claude Code

Perform a comprehensive multi-dimensional editorial audit on the specified file(s).

## Instructions
1. Load `.agents/skills/review-all/SKILL.md` and read all relevant policies in `.editorial/policy/`.
2. Run `.editorial/scripts/lint_vault.py "$@"` on the target file(s).
3. Sequentially audit Technical Accuracy, Completeness, Writing Style, and Formatting.
4. Enforce frontmatter immutability on existing notes.
5. Classify all proposals with stable IDs (`[TECH-xxx]`, `[COMPL-xxx]`, `[STYLE-xxx]`, `[FORMAT-xxx]`).
6. Present the consolidated changes strictly as a **Unified Git Diff**.
7. Wait for explicit user approval before applying changes or committing.

