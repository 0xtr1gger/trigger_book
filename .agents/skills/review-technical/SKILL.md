---
name: review-technical
description: >-
  Audit technical correctness and command accuracy.
  Use when the user invokes /review-technical or asks to verify cybersecurity claims, commands, or accuracy of the facts provided in the specified files.
---

# Technical Accuracy Review (`/review-technical`)

This skill rigorously audits notes for technical accuracy, valid command parameters, security context fidelity, and dual platform coverage.

Main priority: all facts must be technically correct, verifiable, and not contradicted by authoritative sources. All commands must be valid, executable, and correctly formatted. Absolute claims must be qualified to reflect reality

## General accuracy principles

- **Technical correctness takes precedence over stylistic preference**: Never change technical meaning solely to improve prose.
- **Do not invent or fabricate**: Do not invent facts, prerequisites, behaviors, commands, parameters, APIs, registry values, privileges, or exploitation steps.
- **Handling uncertainty**: Never silently replace an uncertain statement with another unverified statement. Flag uncertain claims with `<!-- needs verification -->` or request human verification.
- **Phrasing precision**: Use exact phrasing for technical concepts. Avoid false equivalence or conflation of related but distinct concepts. Do not treat related concepts as identical.

## Command accuracy

- **Preserve working commands**: Do not modify working commands only for stylistic preference. Change commands only when:
  - Syntax or flags are incorrect;
  - Quoting or escaping is broken;
  - A parameter is clearly wrong;
  - Markdown fencing is invalid;
  - The command contradicts the surrounding explanation.
- **Command dual-coverage**: The guides generally cover several variants of a command, such as CMD and PowerShell, using Windows native or external tooling; same applies for Linux. Do not remove valid command variants unless they are incorrect or non-functional. Extend where needed.
- **Standardized command placeholders**: Preserve/use standard placeholders like `<attacker_ip_address>` in command blocks, while referring to it as "listener IP" or "listener address" in prose.

## Source verification hierarchy

When verifying technical claims, use this hierarchy of authority:
1. Official vendor documentation (Microsoft Learn, RFCs, official protocol specifications).
2. Authoritative security research blogs (SpecterOps, Mandiant, Microsoft Security Response Center, Project Zero).
3. Primary tool source code repositories and author documentation (e.g., Mimikatz, Impacket, Certipy, NetExec).
4. Well-known practitioner references (HackTricks, The Hacker Recipes).


## Review protocol

When given one or more target notes:

### Step 1: Audit technical claims & mechanics

Inspect the note content against these core criteria:

- **Accuracy of technical claims**: Are all statements factually correct and supported by authoritative sources (Microsoft documentation, protocol RFCs, or security research)?

Note: not all facts must be explicitly supported by external resources, but each fact must be verifiable and not contradicted by authoritative sources. If a claim is uncertain or unverified, flag it with `<!-- needs verification -->` rather than inventing a correction.

- **Absolute claims**: Are any statements presented as unconditional truths when they are actually conditional on configuration, patch level, or context? Qualify such statements and reduce the degree of certainty to reflect the reality.
- Where needed, replace bare "always", "any process", "full access", "automatically", "bypasses all" with qualified terms:
  - "can"
  - "generally"
  - "by default"
  - "when enabled"
  - "when the required access rights are available"
  - "subject to additional Windows protections"
  - "depending on the token and calling context"


- **Command accuracy**: Are all commands valid, executable, and correctly formatted? Check for correct flags, parameters, quoting, escaping, and placeholders. Ensure that commands are not modified solely for stylistic preference.

### Step 2: Correct technical facts & commands

- For all observed technical inaccuracies, propose corrections that are technically accurate and verifiable. Cite authoritative sources for each correction.
- Modify the note content to correct command syntax, flags, parameters, quoting, escaping, and placeholders. Ensure that commands are valid and executable on both Windows and Linux platforms when applicable. 

### Step 3: Present the changes to the user

- Present proposed modifications and apply the changes after explicit user approval.