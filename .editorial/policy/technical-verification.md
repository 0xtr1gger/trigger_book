# Technical verification policy

This policy governs factual accuracy, technical precision, verification standards, and command integrity for Windows, Active Directory, and cybersecurity content.

## General accuracy principles

- **Technical correctness takes precedence over stylistic preference**: Never change technical meaning solely to improve prose.
- **Do not invent or fabricate**: Do not invent facts, prerequisites, behaviors, commands, parameters, APIs, registry values, privileges, or exploitation steps.
- **Handling uncertainty**: When a technical claim is unverified or conflicting, report the uncertainty or flag it as `needs verification` rather than inventing a correction.

## Command accuracy & dual-coverage requirements

- **Command dual-coverage**: Provide **BOTH** Windows natively executed commands (`CMD` / `PowerShell` / `Sysinternals`) **AND** Linux remote attacker commands (`Impacket` / `NetExec` / `Rubeus` / `Certipy` / `Hashcat`) whenever a vector can be executed from either platform.
- **Preserve working commands**: Do not modify working commands only for stylistic preference. Change commands only when:
  - Syntax or flags are incorrect;
  - Quoting or escaping is broken;
  - A parameter is clearly wrong;
  - Markdown fencing is invalid;
  - The command contradicts the surrounding explanation.
- **Standardized command placeholders**: Use `<attacker_ip_address>` in command blocks, while referring to it as "listener IP" or "listener address" in prose.

## Object vs. state distinctions

Explicitly distinguish between what a Windows object contains versus its current state:
- Privilege **present** in a token vs. privilege **enabled**.
- Group SID **present** vs. **enabled** or **deny-only**.
- Token identity vs. mutable token attributes.
- Process primary token vs. thread impersonation token.
- Access right requested vs. handle actually granted.

Use exact phrasing:
- "present in the token"
- "enabled in the token"
- "assigned to the account"
- "granted on the handle"
- "current thread's impersonation context"

## Avoiding false equivalence and conflation

Do not treat related concepts as identical:
- Possessing a privilege is NOT equivalent to that privilege being enabled.
- Access to a process is NOT equivalent to access to its token.
- Token access is NOT equivalent to token impersonation.
- Token impersonation is NOT equivalent to creating a new process under that token.
- A security context is NOT merely a set of permissions.
- An impersonation level is NOT a separate token type.
- A duplicated token is NOT the same token object.

## Qualified vs. absolute claims

Windows behavior almost always depends on prerequisites, configurations, and patch levels. Flag and qualify unconditional assertions:
- Replace bare "always", "any process", "full access", "automatically", "bypasses all" with qualified terms:
  - "can"
  - "generally"
  - "by default"
  - "when enabled"
  - "when the required access rights are available"
  - "subject to additional Windows protections"
  - "depending on the token and calling context"

## Source verification hierarchy

When verifying technical claims, use this hierarchy of authority:
1. Official vendor documentation (Microsoft Learn, RFCs, official protocol specifications).
2. Authoritative security research blogs (SpecterOps, Mandiant, Microsoft Security Response Center, Project Zero).
3. Primary tool source code repositories and author documentation (e.g., Mimikatz, Impacket, Certipy, NetExec).
4. Well-known practitioner references (HackTricks, The Hacker Recipes).

