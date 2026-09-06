---
name: review-completeness
description: >-
  Audit structural completeness and lifecycle coverage on vault notes.
  Use when the user invokes /review-completeness or asks whether a note is missing
  prerequisites, detection, exploitation, verification, cleanup, or references.
---

# Completeness Review (`/review-completeness`)

This skill audits technical notes for end-to-end lifecycle completeness, Gold Standard architecture, and missing prerequisites or procedures.

## Governing policies

Before reviewing, read:
1. `.editorial/policy/structure.md`
2. `.editorial/policy/technical-verification.md`

## Review protocol

When given one or more target notes:

### Step 1: Audit lifecycle stages
Verify whether the note includes all required stages of the practitioner attack/defense lifecycle:
1. **Scope Callout**: `>[!abstract]+ Scope` defining the boundaries and technologies covered.
2. **Actionable Checklist**: `- [ ]` checklist present if the note describes an actionable, multi-step sequential workflow.
3. **Conceptual Grounding**: Factual explanation of how the mechanism works before launching into commands (H2: `## How [Concept] works`).
4. **Methodological Breakdown**:
   - Enumeration & detection steps (`## Enumerating [Vector]`).
   - Exploitation steps (`## Exploiting [Vector]`).
   - Parameter breakdown tables for all non-trivial tool commands.
5. **Verification Callout**: An actionable verification procedure inside a `>[!tip]+` callout.
6. **Cleanup Callout**: Instructions for cleaning up payloads, modified services, or artifacts inside a `>[!tip]+` callout.
7. **References & Further Reading**: Ending section with hyperlinked sources.

### Step 2: Identify missing elements without bloating
- Only propose adding missing sections or prerequisites when their absence creates a gap in practical execution or makes an existing statement misleading.
- Do not expand notes into general textbook chapters; keep additions concise and practical.
- Never fabricate example tool outputs.

### Step 3: Classify proposals with stable IDs
Tag every proposed addition as `COMPLETENESS` with a stable identifier: `[COMPL-001]`, `[COMPL-002]`, etc.

### Step 4: Present unified diff
Present proposed additions as a **Unified Git Diff**:
- Explain why the added section or detail is necessary for topic completeness.
- **DO NOT commit, overwrite, or finalize the file until the user reviews and explicitly approves the diff.**

### Step 5: Process user decision
- If approved: apply changes.
- If rejected: revert rejected additions and confirm final state.

