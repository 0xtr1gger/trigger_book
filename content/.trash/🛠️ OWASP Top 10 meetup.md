---
created: 2026-08-16
updated: 2026-08-18
---
## Meta

- Goals:
	- Explain what OWASP Top 10 is
	- Explain each category briefly


|Time|Section|Format|
|---|---|---|
|00:00–00:05|What OWASP and the Top 10 are; 2025 changes|Slides|
|00:05–00:10|A01 Broken Access Control, including SSRF|Explanation + short lab|
|00:10–00:13|A02 Security Misconfiguration|Flask example|
|00:13–00:16|A03 Software Supply Chain Failures|Dependency/build example|
|00:16–00:19|A04 Cryptographic Failures|Flask code/data example|
|00:19–00:31|A05 Injection: SQL injection and XSS|Main live demos|
|00:31–00:40|A06 Insecure Design: smuggling, cache poisoning, business logic|Diagrams + walkthrough|
|00:40–00:42|A07 Authentication Failures|Flask example|
|00:42–00:44|A08 Software or Data Integrity Failures|Flask example|
|00:44–00:46|A09 Security Logging and Alerting Failures|Log comparison|
|00:46–00:49|A10 Mishandling of Exceptional Conditions|Flask example|
|00:49–00:50|Summary and further learning|One closing slide|
|00:50–01:00|Q&A|Discussion|

This is deliberately time-boxed. Do not allow audience questions during the first 50 minutes to consume the Q&A reserve; park longer questions for the end.

## OWASP Top 10

### OWASP

- OWASP stands for the Open Worldwide Application Security Project. This is a nonprofit foundation, international open community focused on improving software security. 

{screenshot of their website}

- OWASP develops freely available security projects, including testing guides, secure-development standards, cheat sheets, training applications, tools, and research.

### OWASP Top 10

- OWASP is probably best known for the OWASP Top 10.

- The OWASP Top 10 is a security-awareness document describing ten of the most significant risk categories affecting web applications. It is intended to give developers, testers, architects, security teams, and organizations a common vocabulary for discussing application-security risks.

- What's important to note: these are not individual vulnerabilities (no "SQL injection" thing) — but categories. 
- One category such as Injection can include SQL Injection, Cross-Site scripting, OS command injection LDAP injection, and several others. 
- The 2025 edition groups 248 different Common Weakness Enumerations — or CWEs — into ten broader risk categories.


>[!note] CVE vs CWE
>- **CWE (Common Weakness Enumeration)** describes the **type** of software weakness or design flaw (e.g., SQL injection) that _could_ lead to a vulnerability, serving as a preventive taxonomy for developers.
>	- For example - [CWE-89 Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection')](https://cwe.mitre.org/data/definitions/89.html)
>- **CVE (Common Vulnerabilities and Exposures)** identifies a **specific**, publicly disclosed security flaw in a particular product or system (e.g., a specific buffer overflow in WordPress), serving as an identifier for incident response and patching.
>	- **Log4Shell** (**[CVE-2021-44228](https://nvd.nist.gov/vuln/detail/cve-2021-44228)**)

{live browsing of OWASP Top 10 website}

- The list is created using several sources of information. These include vulnerability data contributed by organizations, relationships between publicly disclosed vulnerabilities and CWEs, information about exploitability and technical impact, and input from the application-security community.

- The ranking is based on:
	- How frequently a vulnerability appears
	- How exploitable and damaging the associated weaknesses can be

- The Top 10 should therefore be treated as a starting point for application security—not as a complete security checklist.

>[!warning] Finding no OWASP Top 10 vulnerabilities does not prove that an application is secure. There are many important weaknesses outside the list, and some Top 10 categories, such as insecure design or ineffective alerting, cannot be tested properly by simply running a vulnerability scanner.

- For more comprehensive and testable requirements, OWASP provides other projects such as the Application Security Verification Standard, or ASVS, and the Web Security Testing Guide. The Top 10 is primarily for awareness and prioritization; ASVS is better suited to defining detailed, verifiable security requirements.

---

- You will also see years attached to the OWASP Top 10, such as 2017, 2021, and 2025. These are editions, and they are created each 4 years, not annually.


The first OWASP Top 10 was published in 2003. Subsequent editions were released in 2004, 2007, 2010, 2013, 2017, 2021, and now 2025. The 2025 release is the eighth edition.


- A new edition does not mean that the older vulnerabilities disappeared or that ten completely new vulnerabilities were discovered. Instead, categories can move in the ranking, change names, expand, merge, or be reorganized as application architectures, development practices, available data, and the threat landscape change.

- For example, injection is ranked lower in 2025 than it was in some previous editions, but that does not make SQL injection or cross-site scripting unimportant. It means the relative categorization and prioritization of risks has changed. The ranking also does not replace an organization’s own threat model: a lower-ranked category may still be the most serious risk for a particular application.

### Other tops

OWASP also maintains—or hosts community projects that maintain—other specialized Top 10 lists. Examples include the API Security Top 10, Mobile Top 10, Kubernetes Top 10, CI/CD Security Risks, and the Top 10 for LLM and generative-AI applications.

These are separate projects created for different technologies and threat models.


### Changes in 2025


Very briefly, the 2025 edition introduces two major category changes and one consolidation.

Software Supply Chain Failures expands the previous focus on vulnerable and outdated components to cover the broader ecosystem of dependencies, package sources, build systems, CI/CD infrastructure, and software distribution.

Mishandling of Exceptional Conditions is a new category focusing on problems such as unsafe error handling, inconsistent state, resource exhaustion, and systems that fail open instead of failing securely.

Server-Side Request Forgery, or SSRF, is no longer a standalone Top 10 category. It has been incorporated into Broken Access Control.

There are also movements and smaller naming changes across the list. Security Misconfiguration moved higher, while the authentication, software and data integrity, and logging categories were renamed slightly to clarify their focus.

We will address those changes in context as we examine each category.

---

The main point to remember is that the OWASP Top 10 is a map of major application-security risk areas. It helps us understand where important classes of failure occur, but we still need threat modeling, secure design, code review, testing, monitoring, and application-specific judgment to determine whether a real system is secure.


**Slide 1 — What is OWASP?**

- Open Worldwide Application Security Project
- Nonprofit foundation and open security community
- Free standards, guidance, tools, training and research
- Common language for software security

**Slide 2 — What is the Top 10?**

- Ten web-application risk categories
- Awareness and prioritization document
- Broad industry and community consensus
- Current edition: 2025
- Starting point—not complete security coverage

**Slide 3 — Editions**

2003 → 2004 → 2007 → 2010 → 2013 → 2017 → 2021 → 2025

Add:

- Categories evolve, merge, expand and move.
- Lower ranking does not mean unimportant.
- Use the edition year when mapping findings.

**Slide 4 — Other OWASP Top 10 projects**

- API Security Top 10
- Mobile Top 10
- Kubernetes Top 10
- CI/CD Security Risks
- LLM and GenAI Top 10

Add a footer:

> Separate projects, scopes, teams and release cycles.

**Slide 5 — 2025 at a glance**

- Broader Software Supply Chain Failures category
- New Mishandling of Exceptional Conditions category
- SSRF consolidated into Broken Access Control
- Security Misconfiguration moved to A02
- Several category names clarified

### Presenter accuracy notes

Avoid saying:

- “These are the ten most common vulnerabilities.”
- “If we test all ten, the application is secure.”
- “A lower position means the vulnerability is less severe.”
- “OWASP is a security company.”
- “OWASP publishes a new edition every four years.”
- “Every Top 10 category can be detected with a scanner.”

Better wording is:

> The Top 10 represents ten broadly significant risk categories selected using data and community judgment.

The specialized projects currently include the [API Security Top 10:2023](https://owasp.org/www-project-api-security/?utm_source=chatgpt.com), [Mobile Top 10:2024](https://owasp.org/www-project-mobile-top-10/2023-risks/?utm_source=chatgpt.com), [Kubernetes Top 10:2025](https://owasp.org/www-project-kubernetes-top-ten/?utm_source=chatgpt.com), [CI/CD Top 10 Security Risks](https://owasp.org/www-project-top-10-ci-cd-security-risks/?utm_source=chatgpt.com), and the current GenAI/LLM project. Their differing edition years help reinforce that they are independently maintained projects.

The definitive sources for this introduction are the [OWASP Top 10 project](https://owasp.org/www-project-top-ten/?utm_source=chatgpt.com), [2025 introduction and change summary](https://owasp.org/Top10/2025/0x00_2025-Introduction/?utm_source=chatgpt.com), and [OWASP guidance on using the Top 10](https://owasp.org/Top10/2025/0x03_2025-Establishing_a_Modern_Application_Security_Program/?utm_source=chatgpt.com).


Before we look at individual vulnerabilities, we need to clarify what the OWASP Top 10 actually is.

OWASP stands for the Open Worldwide Application Security Project. It is a nonprofit foundation and an international open community focused on improving software security. OWASP produces freely available security projects, including testing guides, secure-development standards, cheat sheets, training applications, tools, and research.

OWASP is probably best known for the OWASP Top 10.

The OWASP Top 10 is a security-awareness document describing ten of the most significant risk categories affecting web applications. It is intended to give developers, testers, architects, security teams, and organizations a common vocabulary for discussing application-security risks.

An important word here is “categories.”

These are not simply the ten most common individual vulnerabilities. A category such as Injection can include SQL injection, cross-site scripting, operating-system command injection, LDAP injection, and several other weaknesses. The 2025 edition groups 248 different Common Weakness Enumerations—or CWEs—into ten broader risk categories.

The list is created using several sources of information. These include vulnerability data contributed by organizations, relationships between publicly disclosed vulnerabilities and CWEs, information about exploitability and technical impact, and input from the application-security community.

This means that the ranking is not based only on how frequently a vulnerability appears. It also considers factors such as how exploitable and damaging the associated weaknesses can be. Some risks are also difficult to detect using automated tools, so raw scanner results cannot provide the entire picture.

The Top 10 should therefore be treated as a starting point for application security—not as a complete security checklist.

Finding no OWASP Top 10 vulnerabilities does not prove that an application is secure. There are many important weaknesses outside the list, and some Top 10 categories, such as insecure design or ineffective alerting, cannot be tested properly by simply running a vulnerability scanner.

For more comprehensive and testable requirements, OWASP provides other projects such as the Application Security Verification Standard, or ASVS, and the Web Security Testing Guide. The Top 10 is primarily for awareness and prioritization; ASVS is better suited to defining detailed, verifiable security requirements.

You will also see years attached to the OWASP Top 10, such as 2017, 2021, and 2025. These are editions, not annual vulnerability reports.

The first OWASP Top 10 was published in 2003. Subsequent editions were released in 2004, 2007, 2010, 2013, 2017, 2021, and now 2025. The 2025 release is the eighth edition.

A new edition does not mean that the older vulnerabilities disappeared or that ten completely new vulnerabilities were discovered. Instead, categories can move in the ranking, change names, expand, merge, or be reorganized as application architectures, development practices, available data, and the threat landscape change.

For example, injection is ranked lower in 2025 than it was in some previous editions, but that does not make SQL injection or cross-site scripting unimportant. It means the relative categorization and prioritization of risks has changed. The ranking also does not replace an organization’s own threat model: a lower-ranked category may still be the most serious risk for a particular application.

OWASP also maintains—or hosts community projects that maintain—other specialized Top 10 lists. Examples include the API Security Top 10, Mobile Top 10, Kubernetes Top 10, CI/CD Security Risks, and the Top 10 for LLM and generative-AI applications.

These are separate projects created for different technologies and threat models. They are not additional categories of the Web Application Top 10, and their editions do not necessarily follow the same publication schedule.

In this session, when I say “the OWASP Top 10,” I mean the main Web Application Security Top 10, specifically the 2025 edition.

Very briefly, the 2025 edition introduces two major category changes and one consolidation.

Software Supply Chain Failures expands the previous focus on vulnerable and outdated components to cover the broader ecosystem of dependencies, package sources, build systems, CI/CD infrastructure, and software distribution.

Mishandling of Exceptional Conditions is a new category focusing on problems such as unsafe error handling, inconsistent state, resource exhaustion, and systems that fail open instead of failing securely.

Server-Side Request Forgery, or SSRF, is no longer a standalone Top 10 category. It has been incorporated into Broken Access Control.

There are also movements and smaller naming changes across the list. Security Misconfiguration moved higher, while the authentication, software and data integrity, and logging categories were renamed slightly to clarify their focus.

We will address those changes in context as we examine each category.

The main point to remember is that the OWASP Top 10 is a map of major application-security risk areas. It helps us understand where important classes of failure occur, but we still need threat modeling, secure design, code review, testing, monitoring, and application-specific judgment to determine whether a real system is secure.




----

- One of the best places to learn these vulnerabilities in-depth is PortSwigger Web Security Academy. I dived all down to taking their certification. 
## Explaining SSRF

- CWE-98

- SSRF in one sentence:

>SSRF is a vulnerability where an attacker causes the server-side application to send a request to a location the application was not intended to access.


- In simple terms, SSRF allows an attacker to make the application server send a request somewhere it was not intended to send one.
---

- Suppose an application has a functionality that checks a product's stock:

```http
POST /check-stock HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

stockApi=https://stock.example.com/products/42
```

- The server receives the URL and makes another request to the specified location:

```http
GET /products/42 HTTP/1.1
Host: stock.example.com
```

- Returns the response:

```JSON
{
	"stock": 3268
}
```

- The application displays the results on the page.

---

- But what if an attacker intercepts the request (such as using a web proxy like Burp Suite or OWASP ZAP) and modifies the `stockApi` parameter to point to an internal service?

```http
POST /check-stock HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

stockApi=http://192.168.11.5:8080/admin
```

- If the application doesn't really check the `stockApi` parameter, it just blindly fetches the URI and returns it back with the application response. This way, an attacker may be able to access internal services. 

---

- Or, a more practical example: changing the URL to a cloud's IMDS. AWS's IMDSv1 is susceptible to this:

```http
POST /check-stock HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

stockApi=http://169.254.169.254/latest/meta-data/iam/security-credentials/
```



## A01:2025 Broken access control


- **Access control determines whether an authenticated or unauthenticated actor is permitted to perform a specific action on a specific resource under the current conditions.** 
- Broken Access Control occurs when these authorization rules are missing, inconsistent, enforced only on the client, or based on attacker-controlled data.

## SSRF

**SSRF occurs when an attacker can influence a request made by the application server.** Instead of requesting the protected resource directly, the attacker makes the vulnerable server request it on their behalf.

**CWE-918: Server-Side Request Forgery**

- Fetch image or document from URL.
- Check product stock through another service.
- Import data from a remote location.
- Webhook testing and URL previews.
- PDF generation and link unfurling.
- Server-side proxy, callback or integration endpoints.

Mitigations

- Avoid accepting arbitrary URLs when a resource identifier is sufficient.
- Allowlist required schemes, destinations and ports.
- Resolve the hostname and validate every resulting IPv4 and IPv6 address.
- Reject loopback, link-local, private and reserved ranges unless explicitly required.
- Revalidate every redirect target.
- Account for DNS rebinding and alternative IP representations.
- Apply outbound network restrictions and workload-level egress controls.
- Isolate URL-fetching functionality in a restricted service.
- Protect cloud metadata using platform controls.
- Do not rely solely on substring checks or destination blacklists.


Below is slide-ready text following the same structure and approximate density as your A01 slide.

---

## **A02:2025 – [Security Misconfiguration](https://owasp.org/Top10/2025/A02_2025-Security_Misconfiguration/)**

### **Vulnerability Mechanisms**

**Security configuration** determines how securely an application, framework, server, cloud service and supporting infrastructure operate.

**Security Misconfiguration** occurs when security-relevant settings are absent, insecure, inconsistent between environments, or left at unsafe defaults. Secure code can remain vulnerable when deployed on an insecurely configured platform.

### **Examples**

**Exposed debug functionality** — production mode exposes an interactive debugger, stack traces, internal paths, environment variables or detailed framework errors.  
**CWE-11, CWE-489, CWE-526**

**XML External Entity processing** — an XML parser permits external entities, allowing local file disclosure, internal network requests or resource exhaustion.  
**CWE-611, CWE-776**

**Insecure cookie configuration** — session cookies lack `Secure` or `HttpOnly`, or contain sensitive information in cleartext.  
**CWE-315, CWE-614, CWE-1004**

### **Key Mitigations**

- Establish repeatable, version-controlled hardening baselines for applications, frameworks, servers, containers and cloud services.
    
- Remove unnecessary services, sample applications, default accounts, documentation, debug functionality and unused features.
    
- Automate configuration validation across development, testing and production; use different credentials but equivalent security controls.
    
- Return generic external errors while retaining diagnostic details in protected server-side logs.
    

_**Security Misconfiguration moved from A05:2021 to A02:2025, reflecting the increasing amount of application behavior controlled through configuration.**_

---

## **A03:2025 – [Software Supply Chain Failures](https://owasp.org/Top10/2025/A03_2025-Software_Supply_Chain_Failures/)**

### **Vulnerability Mechanisms**

The **software supply chain** includes dependencies, build tools, package registries, source repositories, CI/CD systems, developer tooling, artifact stores, deployment mechanisms and update channels.

**Software Supply Chain Failures** occur when an organization cannot inventory, control or establish trust in the components and processes used to build, distribute and update its software.

### **Examples**

**Vulnerable dependency** — the application deploys a third-party component with a known exploitable vulnerability, including a vulnerable transitive dependency.  
**CWE-1395, CWE-1035**

**Unmaintained or obsolete component** — production depends on an abandoned library, obsolete function or unsupported platform that no longer receives security updates.  
**CWE-447, CWE-1104**

**Untrustworthy component source** — a build consumes a typosquatted, dependency-confused or malicious package from an insufficiently trusted registry.  
**CWE-1357**

### **Key Mitigations**

- Generate and maintain an SBOM containing direct and transitive dependencies, versions and deployment locations.
    
- Continuously perform software-composition analysis and monitor CVE, OSV and vendor advisories.
    
- Pin and lock dependency versions; obtain components only from controlled, trusted sources and verify signatures or provenance where available.
    
- Harden source control, build systems and artifact repositories using least privilege, protected branches, review and separation of duties.
    
- Remove unused dependencies and define a risk-based update and patching process.
    

_**This category expands A06:2021 “Vulnerable and Outdated Components” from dependency vulnerabilities into the complete software build, distribution and update lifecycle.**_

---

## **A04:2025 – [Cryptographic Failures](https://owasp.org/Top10/2025/A04_2025-Cryptographic_Failures/)**

### **Vulnerability Mechanisms**

**Cryptographic controls** protect the confidentiality, integrity and authenticity of sensitive data and communications.

**Cryptographic Failures** occur when cryptography is absent, weak, incorrectly implemented, used in an unsafe mode, or undermined by poor randomness, certificate validation or key management.

### **Examples**

**Cleartext transmission** — credentials, session identifiers or sensitive data are transmitted without properly enforced TLS.  
**CWE-319, CWE-523**

**Weak password storage** — passwords are stored using unsalted or computationally inexpensive hashes, allowing efficient offline cracking.  
**CWE-759, CWE-760, CWE-916**

**Weak cryptography or key management** — the application uses deprecated algorithms, hard-coded keys, repeated nonces or keys beyond their intended lifetime.  
**CWE-321, CWE-323, CWE-324, CWE-327**

**Predictable security tokens** — password-reset tokens or session identifiers are generated using a non-cryptographic PRNG or insufficient entropy.  
**CWE-330, CWE-331, CWE-338, CWE-340**

### **Key Mitigations**

- Classify sensitive data and define explicit requirements for protection in transit and at rest.
    
- Use current, reviewed cryptographic libraries and authenticated encryption; do not design custom cryptographic protocols.
    
- Store passwords using Argon2id, scrypt, bcrypt or PBKDF2 with appropriate parameters and unique salts.
    
- Generate, store, rotate and revoke keys through a dedicated secrets-management or key-management system.
    
- Enforce certificate and hostname validation; prohibit insecure algorithms, modes and protocol downgrades.
    

_**Encoding is not encryption, encryption does not automatically provide integrity, and hashing is not a substitute for password-specific key derivation.**_

---

## **A05:2025 – [Injection](https://owasp.org/Top10/2025/A05_2025-Injection/)**

### **Vulnerability Mechanisms**

An **interpreter** processes structured instructions, such as SQL, shell commands, HTML, JavaScript, LDAP, XPath or expression language.

**Injection** occurs when attacker-controlled data is combined with instructions and the receiving interpreter treats part of that data as executable syntax rather than as a value.

### **Examples**

**SQL injection** — user input is concatenated into a database query, allowing the attacker to change its structure or meaning.  
**CWE-89, CWE-564**

**Cross-Site Scripting** — attacker-controlled data is inserted into an HTML, attribute or JavaScript context without appropriate output encoding and executes in another user’s browser.  
**CWE-79, CWE-80, CWE-83**

**OS command injection** — input such as a hostname or filename is concatenated into a shell command and interpreted as additional command syntax.  
**CWE-77, CWE-78, CWE-88**

### **Key Mitigations**

- Keep instructions and data separate using parameterized queries, prepared statements and safe framework APIs.
    
- Apply context-aware output encoding for HTML, attributes, JavaScript, CSS and URL contexts.
    
- Avoid invoking command shells; call safe operating-system APIs with separated arguments.
    
- Use allowlists for dynamic identifiers or structural elements that cannot be parameterized, such as column names or sort direction.
    
- Treat input validation as defense in depth—not as a replacement for parameterization or output encoding.
    

_**Injection includes SQL injection and XSS. Prompt injection is addressed separately by the OWASP GenAI/LLM security project because its mechanism and trust model differ from conventional interpreter injection.**_

---

## **A06:2025 – [Insecure Design](https://owasp.org/Top10/2025/A06_2025-Insecure_Design/)**

### **Vulnerability Mechanisms**

**Secure design** defines the trust boundaries, security invariants, abuse controls and valid state transitions that an application must enforce.

**Insecure Design** occurs when a required security control was never designed, the design relies on an invalid assumption, or the application has no safe response to a foreseeable abuse case.

A design flaw is different from an implementation defect: a perfect implementation cannot compensate for a security control that does not exist.

### **Examples**

**Business logic flaw** — the client submits the authoritative product price, or a workflow allows steps to be skipped, repeated or performed in an invalid order.  
**CWE-807, CWE-841, CWE-642**

**HTTP request smuggling** — a front-end and back-end server interpret HTTP message boundaries differently, allowing attacker-controlled bytes to become part of another request.  
**CWE-436, CWE-444**

**Unrestricted file upload** — the system permits dangerous file types or relies only on a client-provided filename or extension to determine safety.  
**CWE-434, CWE-646**

**Race condition** — concurrent requests operate on shared state without sufficient synchronization, allowing a limit or transaction to be executed multiple times.  
**CWE-362**

### **Key Mitigations**

- Perform threat modeling for trust boundaries, authentication, access control, business logic and high-value workflows.
    
- Define security invariants, misuse cases, invalid state transitions and explicit failure behavior before implementation.
    
- Enforce business rules and plausibility checks on trusted server-side state at every relevant tier.
    
- Use reviewed secure-design patterns, reference architectures and reusable “paved road” components.
    
- Test concurrency, workflow order, transaction limits and negative scenarios—not only expected functional behavior.
    

_**HTTP request smuggling and business logic vulnerabilities are explicitly represented in this category. Web cache poisoning may involve A02, A05 or A06 depending on whether its root cause is configuration, unsafe input handling or cache design.**_

---

## **A07:2025 – [Authentication Failures](https://owasp.org/Top10/2025/A07_2025-Authentication_Failures/)**

### **Vulnerability Mechanisms**

**Authentication** establishes and maintains confidence in the identity of a user, service or system.

**Authentication Failures** occur when an attacker can impersonate another identity, bypass authentication, compromise credentials, or reuse an authentication session beyond its intended validity.

### **Examples**

**Credential attacks** — the login endpoint permits unlimited brute force, password spraying or credential stuffing without effective throttling or detection.  
**CWE-307, CWE-521, CWE-1390**

**Session fixation or insufficient expiration** — the application retains a known session identifier after login or does not invalidate sessions after logout, inactivity or account recovery.  
**CWE-384, CWE-613**

**Weak credential recovery** — password reset relies on predictable tokens, knowledge-based questions or an unverified password-change workflow.  
**CWE-620, CWE-640**

**Missing authentication** — a critical function or alternate endpoint can be reached without completing the expected authentication process.  
**CWE-288, CWE-306**

### **Key Mitigations**

- Use a mature identity provider or well-reviewed framework instead of implementing authentication and session management from scratch.
    
- Require phishing-resistant MFA for high-risk users and operations where practical.
    
- Rate-limit and detect automated authentication attacks without creating a trivial account-lockout denial of service.
    
- Rotate the session identifier after authentication and privilege changes; enforce idle and absolute expiration and server-side revocation.
    
- Validate token signature, issuer, audience, expiration, nonce and authorized authentication flow.
    
- Use generic external authentication errors to reduce account enumeration.
    

_**The category was renamed from “Identification and Authentication Failures” to “Authentication Failures”; it remains A07.**_

---

## **A08:2025 – [Software or Data Integrity Failures](https://owasp.org/Top10/2025/A08_2025-Software_or_Data_Integrity_Failures/)**

### **Vulnerability Mechanisms**

**Integrity verification** establishes that software or data originated from the expected source and was not modified without authorization.

**Software or Data Integrity Failures** occur when untrusted code, updates, serialized objects, cookies or other critical data are accepted as authentic without sufficient verification.

### **Examples**

**Insecure deserialization** — attacker-controlled serialized data is reconstructed into application objects, potentially modifying state or invoking dangerous gadget chains.  
**CWE-502**

**Unsigned software update** — an application downloads and executes an update without verifying its signature, provenance or cryptographic integrity.  
**CWE-353, CWE-494**

**Untrusted external code** — scripts, plugins or modules are loaded from an external repository or CDN without establishing trust or verifying integrity.  
**CWE-829, CWE-830**

**Mass assignment** — request properties are automatically copied into internal objects, allowing modification of fields such as `role`, `approved` or `accountBalance`.  
**CWE-915**

### **Key Mitigations**

- Verify signatures, MACs or equivalent authenticity controls before trusting critical software or data.
    
- Accept software only from trusted repositories and use integrity metadata or signed artifacts.
    
- Avoid native object deserialization for untrusted data; use constrained data formats and explicit schemas.
    
- Allowlist accepted object types and properties; never automatically bind every request property to privileged internal state.
    
- Protect CI/CD pipelines with review, access control, separation of duties and artifact-integrity verification.
    

_**A03 concerns governance and compromise of the wider supply-chain lifecycle. A08 concerns the specific trust decision: accepting software or data without proving its authenticity and integrity.**_

---

## **A09:2025 – [Security Logging and Alerting Failures](https://owasp.org/Top10/2025/A09_2025-Security_Logging_and_Alerting_Failures/)**

### **Vulnerability Mechanisms**

**Security logging** records events necessary to reconstruct and investigate security-relevant activity. **Alerting** transforms selected events and patterns into timely action.

**Security Logging and Alerting Failures** occur when important events are missing, incomplete, untrusted, exposed, unmonitored, or do not generate an effective response.

### **Examples**

**Insufficient security logging** — failed authentication, authorization failures, privilege changes or high-value transactions are not recorded.  
**CWE-221, CWE-223, CWE-778**

**Log injection** — attacker-controlled input containing delimiters or line breaks creates forged or misleading log entries.  
**CWE-117**

**Sensitive information in logs** — passwords, access tokens, session identifiers, personal data or cryptographic material are written to log files.  
**CWE-532**

### **Key Mitigations**

- Record structured security events with timestamp, event type, actor, target, result, source and correlation identifier.
    
- Encode or structure untrusted fields so they cannot alter log syntax or forge additional events.
    
- Centralize logs and protect their confidentiality, integrity, retention and availability.
    
- Do not log passwords, complete tokens, sensitive keys or unnecessary personal information.
    
- Define detection logic, thresholds, escalation paths and accountable responders.
    
- Test that penetration tests, simulated attacks and known abuse patterns actually generate alerts.
    

_**The 2021 term “Monitoring” was changed to “Alerting” to emphasize that collecting telemetry is insufficient unless important events cause timely action.**_

---

## **A10:2025 – [Mishandling of Exceptional Conditions](https://owasp.org/Top10/2025/A10_2025-Mishandling_of_Exceptional_Conditions/)**

### **Vulnerability Mechanisms**

An **exceptional condition** is an unusual input, error, resource state or environmental failure that prevents normal processing.

**Mishandling of Exceptional Conditions** occurs when the application fails to prevent, detect or safely respond to that condition, producing information disclosure, inconsistent state, security-control bypass or resource exhaustion.

### **Examples**

**Sensitive error disclosure** — malformed input produces a detailed error containing stack traces, database queries, internal paths, secrets or component information.  
**CWE-209, CWE-550**

**Fail-open authorization** — when an authorization service times out or raises an exception, the application permits the operation instead of rejecting it safely.  
**CWE-274, CWE-636**

**Unchecked error or return value** — a failed security operation is ignored and processing continues as if it succeeded.  
**CWE-252, CWE-390, CWE-391**

**Incomplete cleanup or rollback** — an exception interrupts a transaction but leaves resources locked, money partially transferred or application state inconsistent.  
**CWE-460, CWE-703, CWE-755**

### **Key Mitigations**

- Define secure failure behavior and fail closed when an authorization, validation or integrity decision cannot be completed.
    
- Handle expected errors close to their source and retain a centralized global handler for unexpected exceptions.
    
- Return generic external errors while logging sufficient diagnostic context internally.
    
- Make multi-step state changes atomic and roll back the complete transaction after failure.
    
- Validate missing, extra, malformed and boundary-value inputs explicitly.
    
- Apply timeouts, quotas, rate limits and resource cleanup; test dependency failures, interruption and partial completion.
    

_**This is a new category for 2025. It focuses on fail-open behavior, unsafe error handling and invalid application state—not merely information leakage through verbose errors.**_

---


| Category                                       | What to say                                                                                                                                                                                                                      | Vulnerabilities to mention                                                                                                        | What to show                                                                                                                                                                                                                                                                                                                                                                                                                              |
| ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **A01 Broken Access Control**                  | “Authentication establishes identity; authorization decides whether that identity may perform this action on this resource. The vulnerability is trusting possession of a URL, identifier or session as proof of authorization.” | IDOR/BOLA, horizontal and vertical privilege escalation, forced browsing, CSRF, path traversal, SSRF                              | Open the [OWASP A01 page](https://owasp.org/Top10/2025/A01_2025-Broken_Access_Control/). Show an ID change such as `/orders/812 → /orders/813`. For SSRF, use [Basic SSRF against localhost](https://portswigger.net/web-security/ssrf/lab-basic-ssrf-against-localhost) in Burp Repeater.                                                                                                                                                |
| **A02 Security Misconfiguration**              | “Secure code can still be exposed by insecure runtime, framework, cloud or proxy configuration. Configuration is part of the application attack surface.”                                                                        | Flask debug mode, default accounts, verbose errors, missing cookie/security headers, XXE, permissive CORS                         | Show `app.run(debug=True)` and a stack trace, or inspect headers/cookies in Burp. Briefly show the [OWASP A02 page](https://owasp.org/Top10/2025/A02_2025-Security_Misconfiguration/).                                                                                                                                                                                                                                                    |
| **A03 Software Supply Chain Failures**         | “The application inherits the risk of every dependency, build tool, registry and CI/CD identity involved in producing it. The problem is wider than outdated libraries.”                                                         | Vulnerable dependencies, transitive dependencies, dependency confusion, typosquatting, malicious packages, compromised CI/CD      | Show your `requirements.txt` or lockfile, highlight direct versus transitive dependencies, and optionally show an SBOM or dependency-scanner result. Use the [OWASP A03 page](https://owasp.org/Top10/2025/A03_2025-Software_Supply_Chain_Failures/) for the expanded 2025 scope.                                                                                                                                                         |
| **A04 Cryptographic Failures**                 | “Cryptographic failures include missing protection, weak algorithms, predictable randomness and broken key management—not only ‘bad encryption.’”                                                                                | Cleartext transport, weak password hashing, hard-coded keys, nonce reuse, weak PRNG, invalid certificate handling                 | Show a password stored with plain SHA-256 versus Argon2id/bcrypt/scrypt. Alternatively, show a hard-coded key or an HTTP response without TLS. Open the [OWASP A04 page](https://owasp.org/Top10/2025/A04_2025-Cryptographic_Failures/).                                                                                                                                                                                                  |
| **A05 Injection**                              | “Injection happens when untrusted data crosses into an interpreter and becomes instructions instead of remaining data. The correct defense depends on the interpreter and context.”                                              | SQL injection, XSS, OS command injection, LDAP/XPath injection, server-side template injection                                    | Use your Flask app and Burp. Show the constructed SQL statement before and after an SQLi payload. Then show unescaped input becoming executable HTML/JavaScript. Academy alternatives: [basic SQLi](https://portswigger.net/web-security/sql-injection/lab-retrieve-hidden-data) and [basic reflected XSS](https://portswigger.net/web-security/cross-site-scripting/reflected/lab-html-context-nothing-encoded).                         |
| **A06 Insecure Design**                        | “This is a missing or invalid security design, not simply incorrectly written code. If a required control was never designed, perfect implementation cannot supply it.”                                                          | Business-logic flaws, request smuggling, race conditions, unrestricted upload, client-controlled price/workflow state             | Use a simple front-end/back-end diagram for request smuggling, then Burp Repeater with the [CL.TE access-control bypass lab](https://portswigger.net/web-security/request-smuggling/exploiting/lab-bypass-front-end-controls-cl-te). If time remains, show client-side price manipulation in the [business-logic lab](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-excessive-trust-in-client-side-controls). |
| **A07 Authentication Failures**                | “Authentication fails when the system accepts an invalid identity or does not securely maintain a valid identity and session.”                                                                                                   | Credential stuffing, password spraying, weak reset flows, MFA bypass, session fixation, missing expiration, JWT validation errors | In Burp, compare username-enumeration responses or show the session cookie before and after login. Point out rotation, expiration and cookie attributes. Show the [OWASP A07 page](https://owasp.org/Top10/2025/A07_2025-Authentication_Failures/).                                                                                                                                                                                       |
| **A08 Software or Data Integrity Failures**    | “The application accepts code or security-critical data as trusted without proving its origin and integrity.”                                                                                                                    | Insecure deserialization, unsigned updates, untrusted CDN scripts, cookie tampering, mass assignment                              | Show a serialized or signed value and explain that Base64 is encoding, not integrity protection. Alternatively, show a request containing `role=admin` being automatically bound to an object. Use the [OWASP A08 page](https://owasp.org/Top10/2025/A08_2025-Software_or_Data_Integrity_Failures/).                                                                                                                                      |
| **A09 Security Logging and Alerting Failures** | “Logging creates evidence; monitoring analyzes it; alerting causes action. A log that nobody reviews is not an effective detection control.”                                                                                     | Missing authentication/authorization events, log injection, secrets in logs, no alerting, modifiable local logs                   | Show a poor log such as `POST /login 401`, then a structured event with actor, source, target, result and correlation ID. Mention that a Burp/ZAP scan should produce detectable activity. Open the [OWASP A09 page](https://owasp.org/Top10/2025/A09_2025-Security_Logging_and_Alerting_Failures/).                                                                                                                                      |
| **A10 Mishandling of Exceptional Conditions**  | “Security must remain correct when input is malformed, dependencies fail or transactions stop halfway. The important question is whether the application fails closed and returns to a consistent state.”                        | Fail-open authorization, verbose errors, unchecked return values, missing parameters, partial transactions, resource leaks        | Show a short code comparison: `except: allowed = True` versus deny, log and alert. Alternatively, trigger a Flask error and contrast the external generic response with protected internal diagnostics. Use the [OWASP A10 page](https://owasp.org/Top10/2025/A10_2025-Mishandling_of_Exceptional_Conditions/).                                                                                                                           |