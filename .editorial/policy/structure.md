# Document structure and completeness policy

This policy defines the structural architecture, lifecycle sections, completeness requirements, and preservation constraints for vault notes.

## Frontmatter policy

### Existing notes
- **NEVER** modify, update, remove, reorder, normalize, or touch any line of existing YAML frontmatter.
- Existing note status values (`status: draft`, `status: incomplete`, `status: substantial`, `status: complete`) belong exclusively to the human author for manual verification.

### New notes
- Every newly created note must begin with this YAML frontmatter:

```yaml
---
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags:
  - AD
  - AD_attacks
status: incomplete
---
```
*(Use tags appropriate to the domain: `Windows`, `Windows_PrivEsc`, `AD`, `AD_attacks`)*

## Gold Standard note architecture

Standard notes should follow this logical structure:

```text
[YAML Frontmatter]  <-- NEW notes only; never edit in EXISTING notes
  │
  ├── Document title (H2 sentence case)
  ├── Actionable checklist (- [ ] task boxes, only for sequential procedures)
  ├── Scope / High-level summary (> [!abstract]+ Scope)
  ├── How [Concept] works (Brief factual explanation, no "Mechanics" fluff)
  ├── Methodological breakdown
  │    ├── ## Enumerating [Vector]
  │    ├── ## Exploiting [Vector]
  │    ├── Windows command blocks (```powershell / ```cmd)
  │    ├── Linux command blocks (```bash)
  │    ├── Parameter & flag tables
  │    └── Raw tool outputs (>[!example]-)
  ├── Elevated access verification (> [!tip]+ Verify elevated access:)
  ├── Cleanup instructions (> [!tip]+ Cleanup:)
  └── References and further reading (## References and further reading)
```

## Section requirements & completeness criteria

Every comprehensive topic note must fulfill the attack lifecycle:

1. **Scope callout**:
   - Must use `>[!abstract]+ Scope`.
   - Succinctly states affected components, prerequisites, and relevant privilege boundaries.
2. **Actionable checklist**:
   - Add a checklist (`- [ ]`) only when the note describes an actionable, multi-step sequential workflow.
   - Place after the first heading, separated with horizontal delimiters (`---`), not headings.
3. **Conceptual grounding**:
   - Explains the underlying OS or protocol mechanism before commands are run.
   - Heading must be `## How [Concept] works` or `## [Concept] overview` (never `## Mechanics of...`).
4. **Methodological breakdown**:
   - Procedural steps use action-oriented gerunds (`## Enumerating...`, `## Exploiting...`).
   - Every non-trivial command includes an explanation table of flags.
   - Native Windows and Linux commands are provided when applicable.
5. **Verification & cleanup callouts**:
   - Verification steps belong inside `>[!tip]+` callouts.
   - Cleanup steps belong inside `>[!tip]+` callouts (never use `### Cleanup` headings).
6. **References and further reading**:
   - Note ends with `## References and further reading` and hyperlinked external references.

## Preservation of technical material

- **Never reduce already covered material**: Preserve all valid and relevant technical facts, commands, mechanics, payload details, paths, registry keys, permissions, flags, concrete examples, and tool names.
- Reorganization, deduplication, and clarity improvements are encouraged, provided no technical facts are removed.
- Never fabricate example tool outputs inside callouts.

