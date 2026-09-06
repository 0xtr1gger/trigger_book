# /editorial-learn command for Claude Code

Capture review decisions, corrections, and author preferences, proposing updates to editorial memory.

## Instructions
1. Load `.agents/skills/editorial-learn/SKILL.md`.
2. Analyze the user's feedback, rejections, or stated preferences.
3. Formulate the generalized rule, terminology update, or Bad-vs-Good example pair.
4. Generate a **Unified Git Diff** proposing additions to:
   - `.editorial/memory/preferences.yaml`
   - `.editorial/examples/style-cases.md`
5. Prompt the user for approval.
6. Commit changes only after explicit confirmation.

