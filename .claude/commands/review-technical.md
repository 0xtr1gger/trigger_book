# /review-technical command for Claude Code

Audit the specified file(s) for technical correctness, command accuracy, security mechanics, and dual platform coverage.

## Instructions
1. Load `.agents/skills/review-technical/SKILL.md` and read `.editorial/policy/technical-verification.md`.
2. Verify object vs. state distinctions, token mechanics, handle access rights, and privilege enablement.
3. Check for dual-coverage (Windows native commands vs. Linux remote tooling).
4. Verify command flags, parameters, and placeholders (`<attacker_ip_address>`).
5. Classify each proposal as `[TECH-xxx]`.
6. Present proposed modifications strictly as a **Unified Git Diff**.
7. Wait for explicit user approval before applying changes or committing.

