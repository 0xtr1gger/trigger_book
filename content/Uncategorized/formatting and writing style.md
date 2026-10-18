---
created: 2026-08-07
updated: 2026-09-20
---
## Formatting


- Prefer bullet points and nested bullet points instead of paragraphs whenever possible. 

- Syntax for writing commands (separators are delimiters for your parsing, not for use in real notes):
---
- Do some action:

```bash
command --options
```
---

- Headings you can use:
	- `##` — For major sections/topics in the article.
	- `###` — Subsections/subtopics.
	- `####` — Going further in detail.
	- `#####` and `######` — Rare, as necessary, and only if styling will go weird otherwise.
- Heading format: only the first word starting from a capital letter (others must be all-lowercase except for acronyms or where a capital is necessary).

- Commands, values, etc., certain numbers — Must be put into `backtics`.


- Table format for command options (or other similar tables):

| Option                   | Description            |
| ------------------------ | ---------------------- |
| `-o`, `--option`         | Do this and that.      |
| `-a`, `--another-option` | Display this and that. |
- Definition format:

---
>**Term** is something...

---

- Link and reference format:
	- Section name (at the end, before appendices if any and after all other sections): `## References and further reading`
	- Link format: [`Resource name — Source name`](https://example.com) (specify multiple as a list of bullet-points)

>[!warning] A very important warning, something that may lead to harm and to which to pay attention.

>[!bug] You can use !bugs to describe a core of a vulnerability or misconfiguration in a few sentences.

>[!important] Something important, but not potentially-dangerous like !warning.

>[!note] Side-note.

>[!interesting] A fact, description how something works, or even a bit of relevant history; usually something that is not directly fitting the guide primary purpose, but really interesting to mention.

>[!info] Context information. Use sparingly, when doubting prefer !note.

- Never, no text diagrams. 
## Writing style

- Technically dense.
- Like a textbook, very dry (rather, a mix of technical guide and a textbook). People come for facts, not blabbering.
- At the same time, explain things in a human language.
- Very fluent, natural. 

