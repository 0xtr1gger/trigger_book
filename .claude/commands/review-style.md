# /review-style command for Claude Code

Audit the specified file(s) for writing style, anti-AI guidelines, voice, and tone.

## Instructions
1. Load `.agents/skills/review-style/SKILL.md` and read `.editorial/policy/style.md`.
2. Run `.editorial/scripts/lint_vault.py --check style "$@"` on the target file(s).
3. Audit the prose, flag dangling `-ing` participles, banned words, and ensure reader is addressed as "you".
4. Classify each proposal as `[STYLE-xxx]`.
5. Present proposed modifications strictly as a **Unified Git Diff**.
6. Wait for explicit user approval before applying changes or committing.

