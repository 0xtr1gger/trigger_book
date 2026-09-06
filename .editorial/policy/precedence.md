# Rule precedence and conflict resolution

When editing or reviewing notes, conflicts between rules or instructions must be resolved using this exact precedence hierarchy:

```
Level 1: Explicit current user instruction
   │
   ▼
Level 2: Technical correctness (technical-verification.md)
   │
   ▼
Level 3: Preservation of valid technical material (no content loss)
   │
   ▼
Level 4: Approved policy documents (.editorial/policy/*.md)
   │
   ▼
Level 5: Approved preferences (.editorial/memory/preferences.yaml)
   │
   ▼
Level 6: Gold notes and curated style cases (.editorial/examples/*)
   │
   ▼
Level 7: Default model priors (lowest priority)
```

## Key conflict resolution rules

1. **Technical accuracy over prose smoothness**:
   Never rewrite a sentence in a way that makes it technically less precise or inaccurate, even if the new sentence sounds more concise or elegant.

2. **Preservation over concision**:
   Never delete valid technical flags, commands, mechanics, payload details, paths, registry keys, permissions, or tool names merely to make an article shorter.

3. **Explicit user instructions over policy**:
   If the user specifies an explicit phrasing or structural choice in the current prompt (e.g., "keep this heading in Title Case for this specific vendor product"), that instruction supersedes general policy for that operation.

4. **Frontmatter immutability on existing notes**:
   Existing YAML frontmatter is never edited, removed, or normalized. Frontmatter status values belong strictly to the human author.

5. **Uncertainty protocol**:
   When technical facts are uncertain or unverified, report the uncertainty rather than inventing a plausible-sounding correction.

