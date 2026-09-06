# Editorial policy index

This directory contains the authoritative editorial guidelines, writing standards, formatting rules, and technical verification criteria for the documentation vault.

## Policy map

| Policy Document | Scope & Purpose | Governs Skills / Operations |
| :--- | :--- | :--- |
| [`precedence.md`](./precedence.md) | Conflict resolution order between rules, preferences, and technical accuracy. | All operations |
| [`style.md`](./style.md) | Persona, practitioner tone, banned vocabulary, banned dangling participles, reader perspective ("you"). | `/review-style`, `/review-all` |
| [`formatting.md`](./formatting.md) | Sentence-case headings, procedural gerunds, callouts with fold operators, wikilinks, parameter tables, code blocks. | `/review-formatting`, `/review-all` |
| [`technical-verification.md`](./technical-verification.md) | Technical accuracy, dual Windows/Linux coverage, object vs. state distinctions, handling uncertainty. | `/review-technical`, `/review-all` |
| [`structure.md`](./structure.md) | Gold Standard note architecture, checklist criteria, scope definitions, raw output preservation. | `/review-completeness`, `/review-all` |

## Memory & Learning

- [`../memory/preferences.yaml`](../memory/preferences.yaml) — Dynamic repository of approved terms, banned phrases, and user preferences.
- [`../examples/style-cases.md`](../examples/style-cases.md) — Curated before/after diff cases showing bad AI text transformed into good practitioner prose.
- [`../examples/gold-notes.yaml`](../examples/gold-notes.yaml) — Registry of gold-standard notes in the vault that exemplify desired quality.

## Automated validation

- [`../scripts/lint_vault.py`](../scripts/lint_vault.py) — Standalone deterministic validator script enforcing style and formatting invariants.

