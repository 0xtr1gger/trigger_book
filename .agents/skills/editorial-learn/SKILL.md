---
name: editorial-learn
description: >-
  Extract and record editorial preferences, terminology updates, and style cases from user review decisions.
  Use when the user invokes /editorial-learn, /learn, or provides explicit approval, rejection,
  or correction feedback on an editorial diff.
---

# Editorial Preference Learning (`/editorial-learn`)

This skill captures author preferences, decisions, and corrections from review sessions and codifies them into persistent memory (`.editorial/memory/preferences.yaml` and `.editorial/examples/style-cases.md`).

## Core principle

**Do not silently modify policy or preferences.** Every modification to the agent's memory or skill rules must be presented as a diff to the author for explicit approval.

## Protocol

When the user gives review feedback (e.g., rejecting a proposed change, specifying a preferred term, or asking the system to remember a stylistic pattern):

### Step 1: Analyze the feedback
Distill the feedback into:
1. **Rule category**: Is it a vocabulary term, a sentence structure rule, a formatting convention, or a technical nuance?
2. **Generalized pattern**: Formulate a clear, unambiguous rule that applies beyond just this single file.
3. **Concrete example**: Create a minimal Before/After snippet capturing the difference between the undesirable phrasing and the user's preferred phrasing.

### Step 2: Prepare proposals
Target the appropriate storage layer:
- For concrete term replacements, banned words, or configuration flags: propose edits to `.editorial/memory/preferences.yaml`.
- For prose style and before/after transformation patterns: propose a new case in `.editorial/examples/style-cases.md`.
- For overarching behavioral policies: propose an update to the corresponding file in `.editorial/policy/`.

### Step 3: Present unified diff for approval
Present the proposed additions to `preferences.yaml` or `style-cases.md` as a **Unified Git Diff**.
Ask the user:
> *"Here is the preference rule extracted from your feedback. Would you like me to commit this to your editorial memory?"*

### Step 4: Apply upon approval
Only upon explicit user confirmation:
- Write the changes to `.editorial/memory/preferences.yaml` and/or `.editorial/examples/style-cases.md`.
- The updated rules will automatically take effect on all subsequent review runs.

