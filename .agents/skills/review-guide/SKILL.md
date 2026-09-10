---
name: review-guide
description: >-
  Audit writing style, tone, voice, and anti-AI guidelines on one or more vault notes.
  Use when the user invokes /review-guide or requests an editorial review of prose, tone,
  banned words, dangling participles, or reader perspective.
---

# Style Review (`/review-guide`)

This skill audits technical notes for practitioner-grade writing style, active voice, and anti-AI guidelines.

General rule: paraphrasal for more natual and fluent variants with the preferrence to technicality and consiceness is welcomed and encouraged. Avoid fluff, filler, and pseudo-academic AI tropes. 
Use natural contractions (`can't`, `don't`, `isn't`) and avoid robotic formal phrases.

## Rules and structure

- Frontmantter must not be modified in any way. It is a metadata block and not part of the note content. Do not add, remove, or change any frontmatter fields or values.
- Each note must have a clear, logical structure that follows the attack lifecycle. The note must be complete and cover all necessary aspects of the topic.
- Every note must have "References and further reading" section at the end, with links to relevant external resources.


## Preservation of technical material

- **Never reduce already covered material**: Preserve all valid and relevant technical facts, commands, mechanics, payload details, paths, registry keys, permissions, flags, concrete examples, and tool names.
- Reorganization, deduplication, and clarity improvements are encouraged, provided no technical facts are removed.
- Never fabricate example tool outputs inside callouts.

## On drafts

- If you encounter a draft section, take the important information and incorporate into the main article. If no new details are listed, remove the section.
- The final guide must never contain `## drafts` sections.

## Review protocol

When given one or more target notes:

## Step 1: Fix structure and completeness

- Read the given note(s) and assess whether the order in which sections, bullet points, facts, or commands are presented is logical, clear, and efficient for the human reader who learns the outlined concepts and procedures.
- If the order is illogical, reorder sections, bullet points, or commands to improve clarity and efficiency.
- The reading experience should be smooth, with essential information presented in the appropriate order for the human reader to understand the concepts and procedures. If any important information is missing, add it, however do not go too far out of scope or bloat the note into an academic textbook. Add only those facts essential to understand the main purpose of the note.
- If the completeness of the given topic requires additional sections, add them in the appropriate order. Ensure that the note is complete and covers all necessary aspects of the topic. Any added prose must already conform the style rules outlined in this skill.
- Avoid unnecessary repetition, fluff, or filler.
- Sections with similar structure in the same article should use uniform phrasing and formatting.

### Step 2: Fix prose against style rules

Inspect the note content for:

- **Style**: Explain concepts in natural, fluent human language, but keep text dense and factual like a technical reference manual. State facts directly without fluff, dramatic narrative, pseudo-academic introductory filler, or artificial hype.

- **Reader perspective**: The reader must beaddressed directly as "you" for all procedures. Ensure the reader is never called "the attacker".

- **Banned AI vocabulary**: Flag banned words and phrases that are pseudo-academic, overused AI buzzwords, or conversational clichés. Avoid (if encountered, remove or replace) the following terms:
  - `mechanics`
  - `under the hood`
  - `in a nutshell`
  - `at its core`
  - `crucial`
  - `essential`
  - `pivotal`
  - `vital`
  - `leverage`
  - `utilize`
  - `delve`
  - `harness`
  - `seamlessly`
  - `robust`
  - `basically`
  - `simply`
  - `matrix`

- **Dangling participle clauses (`-ing` tails)**: Sentences ending in `", allowing you to..."`, `", resulting in..."`, `", leading to..."` must be rephrased into direct cause-and-effect statements or crisp bullet points.

- **Conversational fluff**: Strip introductory greetings ("In this guide...", "Welcome to..."), closing remarks, or meta-commentary, or any filler that does not directly contribute to the technical content. Avoid generic summaries or marketing language.

- **Emphasis**: Evaluate the emphasize and phrasing so that the text delivers the information in the most efficient way for a human reader. 

Note: Reader's attention span is limited. Make sure the information is clear, put essential things first in text and paragraphs.

- **Contractions**: Ensure natural shortcuts (`can't`, `don't`, `isn't`) are used instead of robotic formal phrases.

- **Sentence length**: Aim for punchy, factual sentences (15–25 words).

- **Typos and grammar**: Fix any spelling, grammar, or punctuation errors. The text must be correct. 

- For style correction examples, see `content/.editorial/examples/style-cases.md`.
- For examples of good notes (choose based on your current task), see `content/.editorial/examples/gold-notes.yaml`.

### Step 3: Run automated linter

- Run the style linter on the target file(s):
```bash
python3 .editorial/scripts/lint_vault.py --check style "<target_file>"
```

- Fix any flagged issues, except for those that are false positives for the given note(s).

### Step 4: Present the changes to the user

- Present proposed modifications and apply the changes after explicit user approval.