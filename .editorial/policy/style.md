# Writing style and anti-AI guidelines

This policy governs persona, tone, vocabulary, sentence structure, and reader perspective across all vault documentation.

## Core persona & tone

- Write in a plain, direct, practitioner-grade style.
- State facts directly without fluff, dramatic narrative, pseudo-academic introductory filler, or artificial hype.
- Keep sentences short, simple, and punchy (aim for 15–25 words per sentence).
- Explain concepts in natural, fluent human language, but keep text dense and factual like a technical reference manual.
- Use natural shortcuts and contractions (`can't`, `don't`, `isn't`, `won't`) where applicable instead of `cannot` or `do not`, except where specific emphasis is required.

## Reader voice and perspective

- Address the reader directly as **"you"** for all procedural instructions, conditions, and checks.
- **Never call the reader "the attacker".**
- Use generic role nouns only when describing a systemic security context on the machine:
  - "a low-privileged user"
  - "a privileged service account"
  - "an administrator session"
- Do not mix "you", "the attacker", and "low-privileged user" interchangeably when referring to the same participant in a single scenario.
- Use explicit targets: "the target system", "the target service", "the target executable" (avoid ambiguous bare "target").

## Banned AI vocabulary and fluff terms

Never use pseudo-academic AI filler words or overused AI buzzwords.

| Banned Term | Reason | Preferred Replacement |
| :--- | :--- | :--- |
| `Mechanics` (as heading / intro) | Academic AI trope | `How [Vector] works` or `Security model` |
| `Under the hood` | Conversational cliché | State the direct OS behavior or API |
| `In a nutshell` / `At its core` | Conversational cliché | Direct factual statement |
| `Crucial` / `Essential` / `Pivotal` / `Vital` | Emotional over-emphasis | State direct operational consequence |
| `Leverage` | Corporate buzzword | `use`, `abuse`, `exploit` |
| `Utilize` | Pseudo-formal filler | `use` |
| `Seamlessly` / `Delve` / `Harness` | AI signature words | Remove or state concrete action |
| `Robust` / `Comprehensive` | Generic marketing fluff | Specific capability description |
| `Basically` / `Simply` / `Obviously` / `Clearly` | Patronizing filler | Delete word completely |

## Banned dangling participle clauses (`-ing` tails)

**CRITICAL RULE**: Do not append dangling participle phrases (`-ing` clauses) to the end of sentences to explain outcomes or results. This creates repetitive, robotic, and unnatural text.

### Forbidden patterns
- ❌ *"...allowing an attacker to escalate privileges."*
- ❌ *"...leading to arbitrary code execution."*
- ❌ *"...resulting in a system crash."*
- ❌ *"...enabling unauthenticated user access."*
- ❌ *"...granting SYSTEM privileges."*

### Rephrasing rule: Direct cause-and-effect or crisp bullet points
- ❌ **Bad:** "The service executes binary files with SYSTEM privileges, allowing you to escalate privileges."
- ✅ **Good:** "The service executes as `SYSTEM`. Replacing the binary gives you `SYSTEM` code execution."
- ❌ **Bad:** "Run `whoami /all`, displaying the active user SID and privileges."
- ✅ **Good:** "Run `whoami /all` to display your SID, group memberships, and assigned privileges."

## Zero conversational fluff

Eliminate all meta-commentary, introductory greetings, marketing language, and generic summaries.

Forbidden introductory and closing patterns:
- ❌ "In this guide, we will explore..."
- ❌ "Welcome to my notes on..."
- ❌ "Hope this helps with your exam prep!"
- ❌ "Summary:" (when used as generic closing filler)
- ❌ "As you can see..."
- ❌ "It is important to remember that..."
- ❌ "Note that..." (use a callout or state the fact directly)

