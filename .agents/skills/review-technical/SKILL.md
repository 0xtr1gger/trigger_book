---
name: review-technical
description: >-
  Audit technical correctness, command syntax, dual Windows/Linux coverage, and security mechanics.
  Use when the user invokes /review-technical or asks to verify cybersecurity claims, command parameters,
  or Windows/Active Directory accuracy.
---

# Technical Accuracy Review (`/review-technical`)

This skill rigorously audits notes for technical accuracy, valid command parameters, security context fidelity, and dual platform coverage.

## Governing policies

Before reviewing, read:
1. `.editorial/policy/technical-verification.md`
2. `.editorial/policy/precedence.md`

## Review protocol

When given one or more target notes:

### Step 1: Audit technical claims & mechanics
Inspect the note content against these core criteria:
- **Object vs. state distinctions**: Are privileges accurately described as "present in token" vs "enabled in token"? Are group SIDs distinguished as enabled vs deny-only?
- **Security context & handles**: Ensure process handle access rights are not conflated with token impersonation, and token impersonation is not conflated with new process creation.
- **Unjustified absolute claims**: Replace bare "always", "full access", "bypasses all" with accurate conditional qualifications ("by default", "when enabled", "subject to...").
- **Command dual-coverage**: Does the note provide **BOTH** Windows native commands (`cmd.exe`, `powershell.exe`, Sysinternals) **AND** Linux remote commands (`impacket`, `netexec`, etc.) for attack vectors executable from both?
- **Parameter & flag validity**: Check that tool flags, options, and arguments are correct for the modern version of the tool.
- **Handling uncertainty**: Never silently replace an uncertain statement with another unverified statement. Flag uncertain claims with `<!-- needs verification -->` or request human verification.

### Step 2: Classify proposals with stable IDs
Tag every proposed change as `TECHNICAL` with a stable identifier: `[TECH-001]`, `[TECH-002]`, etc.

### Step 3: Present unified diff
Present proposed modifications as a **Unified Git Diff**:
- State the exact technical inaccuracy being corrected.
- Cite the authoritative source (Microsoft documentation, protocol RFC, or security research).
- **DO NOT commit, overwrite, or finalize the file until the user reviews and explicitly approves the diff.**

### Step 4: Process user decision
- If approved: apply the changes.
- If rejected: revert rejected items and confirm final state.

