# /review-completeness command for Claude Code

Audit the specified file(s) for structural completeness and full attack lifecycle coverage.

## Instructions
1. Load `.agents/skills/review-completeness/SKILL.md` and read `.editorial/policy/structure.md`.
2. Check for Scope callout (`>[!abstract]+ Scope`), prerequisites, conceptual grounding, enumeration, exploitation, verification (`>[!tip]+`), cleanup (`>[!tip]+`), and references.
3. Propose only necessary practical additions; do not bloat the note into an academic textbook.
4. Classify each proposal as `[COMPL-xxx]`.
5. Present proposed modifications strictly as a **Unified Git Diff**.
6. Wait for explicit user approval before applying changes or committing.

