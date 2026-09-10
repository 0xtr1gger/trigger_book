# Style cases: Bad vs Good examples

This file provides curated few-shot transformation examples. Models reviewing documentation should reference these pairs to understand the author's preferred style.

---

### Case 001: Dangling `-ing` participle tails
- ❌ **Bad:** "The service executes binary files with SYSTEM privileges, allowing an attacker to escalate privileges."
- ✅ **Good:** "The service executes as `SYSTEM`; if you replace its binary, your code will run as `SYSTEM` on next service start."
- **Rationale:** Eliminate dangling participle result clause; replace passive attacker reference with direct cause-and-effect addressing the reader as "you".

---

### Case 002: AI buzzwords and academic fluff
- ❌ **Bad:** "In this section, we delve into the crucial mechanics of utilizing BloodHound to seamlessly map Active Directory relationships."
- ✅ **Good:** "- BloodHound maps Active Directory domain relationships and attack paths by querying LDAP, SAMR, and session endpoints."
- **Rationale:** Eliminated "delve", "crucial mechanics", "utilizing", "seamlessly", and meta-commentary "In this section, we...".

---

### Case 003: Heading capitalization and procedural gerunds
- ❌ **Bad:**
  ```markdown
  ## Exploitation Of Weak Service DACLs
  ### Binary Path Modification
  ```
- ✅ **Good:**
  ```markdown
  ## Exploiting weak service DACLs
  ### Modifying the service binary path
  ```
- **Rationale:** Enforce strict sentence case and active gerund (`-ing`) forms for procedural sections.

---

### Case 004: Windows object vs state conflation
- ❌ **Bad:** "Because the user has `SeDebugPrivilege`, they can elevate to SYSTEM."
- ✅ **Good:** "`SeDebugPrivilege` allows a process to open handles to other processes regardless of security descriptors. When enabled in the token, you can open a handle to `lsass.exe` with `PROCESS_VM_READ` access."
- **Rationale:** Explicit technical accuracy; possession vs enablement distinction; exact handle access rights.

---

### Case 005: Wikilink syntax formatting
- ❌ **Bad:** "Refer to `[[🛠️ Pass-the-Hash]]` or [Kerberos](content/Active%20Directory/How%20AD%20works/Kerberos.md)."
- ✅ **Good:** ">[!note] See [[🛠️ Pass-the-Hash]] and [[Kerberos]]."
- **Rationale:** Wikilinks must never be enclosed in backticks, and internal vault references must use `[[...]]` wikilinks, not Markdown file paths.

---

### Case 006: Conversational introductions & fluff
- ❌ **Bad:**
  ```markdown
  ## Introduction
  Welcome to this guide on Windows Access Tokens! Understanding tokens is essential for any penetration tester hoping to pass the OSCP. In the following paragraphs, we will explore the core concepts.
  ```
- ✅ **Good:**
  ```markdown
  >[!abstract]+ **Scope**: Windows access tokens: primary vs. impersonation tokens, impersonation levels, token privileges, and privilege escalation techniques.

  ## How access tokens work
  - An access token is an internal kernel object (`_TOKEN`) that describes the security context of a process or thread.
  ```
- **Rationale:** Eliminate greetings, exam prep commentary, and meta-introductions; replace with crisp Scope callout followed immediately by the technical model.

