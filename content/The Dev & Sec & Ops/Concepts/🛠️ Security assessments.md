---
created: 2026-09-21
updated: 2026-09-24
tags:
  - concepts
---

//remove links to sections across the article.

> [!abstract]+ **Scope**: Types of security assessments (vulnerability assessments, penetration tests, security audits, bug bounty programs, red team assessments); risk terminology; asset management; compliance and penetration testing standards; vulnerability scoring with CVSS and DREAD; vulnerability classification with OVAL, CVE, and related databases (NVD, CWE, KEV, EPSS); vulnerability disclosure; vulnerability scanning.

## Security assessment types

- **Vulnerability assessments**: Identifying, classifying, and prioritizing security weaknesses against a security standard, without attempting exploitation.
- **Penetration tests**: Simulating authorized cyberattacks to identify and exploit vulnerabilities within a defined scope to evaluate the security posture of the target infrastructure.
- **Security audits**: Evaluate compliance with specific security regulations, industry standards, or governance policies on behalf of external or regulatory bodies.
- **Bug bounty programs**: Inviting members of the general public to find vulnerabilities in exchange for payment.
- **Red team assessments**: Simulate a real adversary pursuing a specific objective; involves executing multi-phase adversarial simulations to test an organization's detection, containment, and response capabilities.

### Vulnerability assessments

> A **vulnerability assessment** is a systematic process of identifying, classifying, and prioritizing security weaknesses across the target infrastructure without attempting exploitation.

- Vulnerability assessments evaluates the security posture of a target infrastructure against established security standards, such as CIS Benchmarks, NIST SP 800-53 controls, or OWASP standards.
- The assessment doesn't involve simulating/executing exploits or pursuing privilege escalation. The process stops at validating the existence of a vulnerability and confirming it is not a false positive.
- Assessments are categorized by operational domain:
	- **Network-based assessments**: evaluate open ports, service banners, protocol implementations, and perimeter or internal network routing and filtering devices.
	- **Host-based assessments**: examine operating system configurations, file permissions, local account policies, patch levels, and installed packages on servers and endpoints.
	- **Application assessments**: analyze web applications, APIs, mobile applications, and software source code for logic flaws, architectural weaknesses, and implementation errors (such as the OWASP Top 10).
	- **Database assessments**: review database management systems (DBMS) for configuration baselines, patch levels, parameter security, and excessive user privileges.

#### Vulnerability assessment methodology

- The vulnerability assessment methodology follows a structured lifecycle:
	1. **Risk identification and scope definition**: identify critical assets, operational constraints, and assessment boundaries.
	2. **Scanning policy formulation**: define scanning criteria, authentication parameters, and acceptable operational thresholds.
	3. **Scan type selection**: determine whether host, network, credentialed, or uncredentialed scanning is appropriate.
	4. **Scanner configuration**: configure target ranges, scan engines, port definitions, and custom plugins.
	5. **Scan execution**: run automated scans against the target environment.
	6. **Risk evaluation and false-positive verification**: validate reported findings to confirm reproducibility and rule out false positives.
	7. **Result interpretation**: analyze root causes, correlation between assets, and organizational impact.
	8. **Remediation planning and reporting**: generate prioritized remediation recommendations and technical reports.

![](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/108/graphics/VulnerabilityAssessment_Diagram_06b.png)
>
> _Adapted from the original graphic found [here](https://purplesec.us/wp-content/uploads/2019/07/8-steps-to-performing-a-network-vulnerability-assessment-infographic.png)._

### Penetration tests

> A **penetration test** (**pentest**) is an authorized simulated attack against a system, application, or network to identify and safely exploit security weaknesses, aimed at verifying whether vulnerabilities allow unauthorized access or compromise.

- Penetration tests require formal legal authorization. Executing testing activities without contractual consent violates computer crime laws. The engagement is bound by contractual terms defining permissible testing activities.
- Penetration tests provide maximum utility for organizations with mature cybersecurity programs. Applying penetration testing to an immature environment is inefficient; automated vulnerability assessments identify missing patches and basic misconfigurations at lower cost.
- Assessments vary by starting network position:
	- **External**: conducted over the internet without internal network access, evaluating perimeter resilience from the viewpoint of an untrusted remote attacker.
	- **Internal**: conducted from inside the corporate perimeter, evaluating the blast radius of a compromised workstation, rogue physical device, or malicious insider.

> [!important] The primary deliverable of a penetration test is an exhaustive technical **report**. It details executive summaries, prioritized findings, reproducible exploit chains, proof-of-concept evidence, and technical remediation roadmaps.

#### Engagement documents

- Penetration tests require agreed legal and operational documents prior to execution:
	- **Non-disclosure agreement (NDA)**: obligates parties to maintain strict confidentiality regarding discovered vulnerabilities, intellectual property, credentials, and operational findings.
	- **Statement of work (SoW)**: establishes the commercial contract, defining engagement scope, scheduled timelines, staffing, and specific deliverables.
	- **Scope definition**: specifies target assets (IP addresses, CIDR ranges, domain names, APIs, physical locations) and explicitly lists out-of-scope systems.
	- **Rules of engagement (RoE)**: governs operational parameters during testing, including allowed testing windows, prohibited attack techniques (such as denial-of-service or physical intrusion), primary and emergency contacts, sensitive data handling, and criteria for immediately halting tests.

#### Black-box, grey-box, and white-box testing

- Engagements are structured by the level of technical information disclosed to testers beforehand:
	- **Black box (zero-knowledge)**: testers receive minimal target information beyond domain names or IP addresses. This posture simulates an external attacker. A significant portion of the engagement is spent on reconnaissance and discovery, which can reduce testing depth on internal application logic within limited timeframes.
	- **Grey box (partial-knowledge)**: testers receive partial information, such as low-privilege user credentials, network topology diagrams, or basic API specifications. This posture balances realism and efficiency, allowing testers to bypass basic authentication boundaries and evaluate internal logic and privilege escalation.
	- **White box (complete-knowledge)**: testers receive full architectural documentation, source code repositories, network maps, and administrative credentials. This posture enables comprehensive static and dynamic analysis, maximizing vulnerability identification within the allocated timeframe.

#### Pentesting specializations

- Engagements are divided into specific technical specializations:
	- **Application penetration testing**: audits web applications, mobile applications, APIs, and compiled desktop binaries for software vulnerabilities.
	- **Network and infrastructure penetration testing**: targets internal Active Directory environments, cloud infrastructure (AWS, Azure, GCP), network hardware, routers, switches, and remote access perimeters.
	- **Physical penetration testing**: evaluates physical controls protecting IT assets, including badge readers, locks, server rooms, and physical surveillance.
	- **Social engineering penetration testing**: tests employee security awareness and procedural adherence through controlled phishing, vishing, or pretexting exercises.

### Vulnerability assessments vs. penetration tests

- **Operational objective**:
	- Vulnerability assessment: catalogues, quantifies, and ranks known security weaknesses against compliance or baseline standards across the environment.
	- Penetration test: proves exploitability by chaining weaknesses to bypass controls and compromise systems.
- **Exploitation depth**:
	- Vulnerability assessment: stops at verifying that a vulnerability exists; avoids lateral movement, privilege escalation, or persistence.
	- Penetration test: exploits identified weaknesses, establishes footholds, escalates privileges, and moves laterally to evaluate real-world impact.
- **Scope and coverage**:
	- Vulnerability assessment: broad, providing comprehensive coverage of all in-scope assets.
	- Penetration test: deep, focusing on exploitable paths leading to specific high-value objectives.

![](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/108/graphics/VulnerabilityAssessment_Diagram_02.png)

### Security audits

> A **security audit** is an independent, formal assessment of an organization's systems, policies, and operational controls to verify compliance with statutory regulations, industry standards, or contractual security requirements.

- Security audits evaluate adherence to established governance frameworks (such as [[#PCI DSS]], SOC 2, HIPAA, or ISO/IEC 27001). They are typically mandated by external regulatory authorities, customers, or governing bodies.
- Unlike technical testing, security audits inspect both technical implementations and administrative controls, including incident response plans, access control policies, encryption standards, training records, and log retention.
- Organizations perform continuous vulnerability assessments and recurring penetration tests to maintain security baselines and prepare evidence for formal external audits.

### Bug bounty programs

> A **bug bounty program** is an open or invite-only crowd-sourced security initiative that compensates external researchers for identifying and reporting valid security vulnerabilities within a defined scope.

- Bug bounty programs supplement internal testing by exposing systems to diverse external testing methodologies continuously. Payouts scale with vulnerability severity, ranging from low-severity issues to critical remote code execution findings.
- Programs are generally hosted on managed platforms (such as [HackerOne](https://www.hackerone.com/), [Bugcrowd](https://www.bugcrowd.com/), or [Intigriti](https://www.intigriti.com/)), which manage triage, duplicate elimination, researcher validation, and bounty disbursements.
- Core program governance elements:
	- **Program policy**: enumerates in-scope domains and assets, prohibited techniques (such as denial-of-service, automated high-throughput fuzzing, or physical access), and response service level agreements (SLAs).
	- **Safe harbor**: an explicit contractual clause protecting security researchers from legal prosecution under anti-hacking laws, provided they operate in good faith within policy guidelines.
	- **Vulnerability Disclosure Program (VDP)**: a structured communication channel (`security.txt`, [RFC 9116](https://www.rfc-editor.org/rfc/rfc9116)) for reporting security issues without monetary rewards, often implemented prior to launching a paid bug bounty program.

### Red team assessments

> A **red team assessment** is an objective-driven, adversarial simulation designed to test an organization's detection, containment, and response capabilities by covertly emulating real-world threat actors.

- Red teams operate covertly, testing not only technical configurations but also human processes, Security Operations Center (SOC) monitoring, and Incident Response (IR) protocols.
- The objective is not to find every vulnerability, but to achieve a specific operational goal (such as exfiltrating proprietary data, compromising a domain controller, or manipulating transactional databases) while evading defensive controls.
- Engagements frequently employ the **assumed breach** model: the red team starts with internal network access or an unprivileged domain account, simulating a successful initial phishing attack or stolen credential. This focuses testing resources on lateral movement, internal privilege escalation, evasion techniques, and detection efficacy.
- Defending and collaborative roles:
	- **Blue team**: internal security personnel (SOC analysts, threat hunters, detection engineers) responsible for monitoring, analyzing, and mitigating attacks.
	- **Purple teaming**: a collaborative exercise where red and blue operators work together in real time, validating detection rules and telemetry coverage against specific attack techniques (such as those mapped in MITRE ATT&CK).

#### Penetration testing vs. red teaming

- **Objective**:
	- Penetration test: identify, exploit, and document as many vulnerabilities as possible within the scoped assets.
	- Red team: achieve defined strategic objectives while evaluating defensive monitoring, alerting, and response effectiveness.
- **Stealth and evasion**:
	- Penetration test: loud or overt testing; evasion is not a priority, and automated tools generate significant network traffic.
	- Red team: covert operations; uses custom tooling, living-off-the-land techniques, obfuscation, and operational security (OPSEC) to avoid detection.
- **Scope**:
	- Penetration test: restricted to technical infrastructure, designated IP ranges, and defined applications.
	- Red team: comprehensive; encompasses technical controls, social engineering, physical access, and organizational procedures.
- **Duration**:
	- Penetration test: fixed, typically one to four weeks.
	- Red team: extended, spanning several weeks to several months to emulate Advanced Persistent Threats (APTs).
- **Deliverables**:
	- Penetration test: an exhaustive list of identified vulnerabilities ranked by severity, accompanied by remediation recommendations.
	- Red team: a chronological attack narrative detailing the path taken, defensive visibility gaps, detection timeline analysis, and root causes of response failures.

## Risk terminology

> A **vulnerability** is a weakness, flaw, or implementation error in an asset, system, or process that can be exploited to violate an established security policy.

- Vulnerabilities exist in software code, hardware architecture, firmware, system configurations, and human processes. Standardized entries are documented in the [[#CVE]] database.

> A **threat** is any circumstance, event, or entity with the potential to cause harm to an asset by exploiting a vulnerability.

- A **threat actor** (or **threat source**) is the individual, group, or nation-state executing the threat (such as an APT group, cybercriminal syndicate, or insider). The threat represents the combination of intent, capability, and opportunity to exploit a weakness.

> An **exploit** is a specific technical mechanism, software tool, script, or payload that takes advantage of a vulnerability to produce unauthorized or unintended behavior on a target system.

- Public repositories such as [Exploit-DB](https://exploit-db.com/) and [Rapid7 DB](https://www.rapid7.com/db/) index known exploit code and proof-of-concept material.

> **Risk** is the potential for loss, harm, or adverse consequences resulting when a threat successfully exploits a vulnerability against an asset.

- The relationship between core risk elements:
	- A **vulnerability** provides the opportunity.
	- A **threat** provides the intent and capability.
	- An **exploit** provides the technical means.
	- A **risk** represents the expected business loss.

![](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/108/graphics/threat_vulnerability_risk.png)
![](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/108/graphics/whatisrisk.png)

### Measuring risk

- Risk is calculated as a function of **likelihood** (probability of occurrence) and **impact** (magnitude of adverse outcome):
  $$\text{Risk} = \text{Likelihood} \times \text{Impact}$$
- Qualitative risk assessment maps likelihood and impact onto ordinal scales (such as low, medium, high, and critical) to create a risk matrix:
	- **High likelihood**:
		- Low impact: Medium risk.
		- Medium impact: High risk.
		- High impact: Critical risk.
	- **Medium likelihood**:
		- Low impact: Low risk.
		- Medium impact: Medium risk.
		- High impact: High risk.
	- **Low likelihood**:
		- Low impact: Informational/Low risk.
		- Medium impact: Low risk.
		- High impact: Medium risk.
- Quantitative risk assessment expresses risk in monetary terms:
	- **Single Loss Expectancy (SLE)**: the financial loss incurred each time a risk materializes.
	  $$\text{SLE} = \text{Asset Value (AV)} \times \text{Exposure Factor (EF)}$$
	- **Annualized Loss Expectancy (ALE)**: the expected annual financial loss.
	  $$\text{ALE} = \text{SLE} \times \text{Annualized Rate of Occurrence (ARO)}$$

### Risk treatment

- Following risk analysis, an organization selects a risk treatment strategy:
	- **Mitigation (reduction)**: implements technical, administrative, or physical controls to reduce the likelihood or impact of exploitation (e.g., patching software, deploying MFA, network segmentation).
	- **Transference (sharing)**: reallocates financial consequences to an external party (e.g., purchasing cyber liability insurance, outsourcing specialized operations).
	- **Avoidance**: terminates the activity, system, or service that introduces the risk (e.g., decommissioning an obsolete unpatchable application).
	- **Acceptance**: formally documents and retains the residual risk without deploying additional controls, typically when the cost of mitigation exceeds the asset value or the risk falls within defined tolerance levels.

## Asset management

- Effective cybersecurity relies on accurate asset inventory: an organization cannot protect, monitor, or assess assets it does not know exist.
- Asset visibility forms the baseline for attack surface management (ASM), vulnerability management, and regulatory compliance.

### Asset inventory

- A cybersecurity asset inventory maintains a real-time catalog of all operational technology (OT), information technology (IT), software, data, and personnel assets.
- Asset inventories record metadata for each item: owner, network location, operational status, data classification, patch history, and business criticality.
- Inventories must account for dynamic asset lifecycles, such as ephemeral containers, cloud compute instances, and mobile remote endpoints.

### Application and system inventory

- An enterprise asset inventory covers five primary categories:
	- **On-premises endpoints and servers**:
		- Physical and virtual servers running enterprise workloads.
		- Workstations, laptops, and mobile devices connected to corporate networks.
		- Network-attached storage (NAS) and storage area networks (SAN).
		- Removable media (flash drives, external HDDs) and legacy offline media.
	- **Cloud provider infrastructure**:
		- Infrastructure-as-a-Service (IaaS) instances, serverless workloads, virtual private clouds (VPCs), and object storage buckets across public clouds ([AWS](https://aws.amazon.com/), [Azure](https://azure.microsoft.com/), [GCP](https://cloud.google.com/)).
		- Multi-cloud asset inventories require automated querying through provider APIs and Cloud Security Posture Management (CSPM) tools.
	- **SaaS applications and shadow IT**:
		- Cloud-hosted enterprise productivity software (`Microsoft 365`, `Google Workspace`, `Salesforce`, `Slack`).
		- Unauthorized applications and services deployed by internal units without security authorization (shadow IT).
	- **Network and security appliances**:
		- Physical and virtual firewalls, routers, core switches, and wireless access points.
		- Security monitoring infrastructure: Intrusion Detection/Prevention Systems (IDS/IPS), Web Application Firewalls (WAF), and Data Loss Prevention (DLP) engines.
	- **Software and component dependencies**:
		- Installed third-party packages, runtime environments, and open-source libraries.
		- Software Bill of Materials (SBOM) tracking to identify supply-chain vulnerabilities within deployed applications.

## Assessment standards

- Adherence to formal standards ensures technical assessments are repeatable, legally defensible, and aligned with industry benchmarks.

### Compliance standards

- Regulatory frameworks define mandatory testing baselines for organizations operating within specific jurisdictions or industries:
- [[#PCI DSS]]:
	- Governs entities that store, process, or transmit cardholder data.
	- Mandates quarterly internal and external vulnerability scans, annual penetration testing, and segmentation testing.
- [Health Insurance Portability and Accountability Act (HIPAA)](https://www.hhs.gov/programs/hipaa/index.html):
	- Regulates the security and privacy of Protected Health Information (PHI) and electronic PHI (ePHI).
	- Enforces ongoing security management processes, requiring vulnerability identification, threat evaluation, and regular risk assessments (45 CFR § 164.308).
- [Federal Information Security Modernization Act (FISMA)](https://www.cisa.gov/federal-information-security-modernization-act):
	- Requires US federal agencies and contractors to implement information security programs based on NIST Special Publications (NIST SP 800-53, FIPS 199/200).
	- Mandates continuous diagnostic and mitigation (CDM) programs, regular system security plan reviews, and Plan of Action and Milestones (POA&M) remediation tracking.
- [[#ISO 27001]]:
	- International standard for Information Security Management Systems (ISMS).
	- Requires formal processes for identifying technical vulnerabilities and evaluating operational exposure based on risk.

> [!important] Regulatory compliance represents a minimum security baseline, not an optimal security posture. Vulnerability management programs must be tailored to an organization's specific threat model and risk tolerance.

#### PCI DSS

- The [Payment Card Industry Data Security Standard (PCI DSS)](https://www.pcisecuritystandards.org/pci_security/) is administered by the Payment Card Industry Security Standards Council (PCI SSC), formed by payment brands (Visa, MasterCard, American Express, Discover, JCB).
- The standard applies to the **Cardholder Data Environment (CDE)**—the network systems, processes, and people that handle primary account numbers (PAN) or sensitive authentication data.
- Requirement 11 of PCI DSS v4.0 ("Test Security of Systems and Networks Regularly") mandates specific technical testing intervals:
	- **Internal vulnerability scanning**: performed at least once every three months and after any significant infrastructure change. Scans can be conducted by qualified internal personnel.
	- **External vulnerability scanning**: performed at least once every three months and after any significant change by an independent, PCI SSC-certified **Approved Scanning Vendor (ASV)**.
	- **Internal and external penetration testing**: performed at least once every 12 months and following any significant infrastructure or application modification.
	- **Segmentation testing**: annual testing (semi-annual for service providers) to verify that network segmentation controls isolate the CDE from out-of-scope enterprise networks.

- The six core PCI DSS control objectives:
	1. Build and maintain a secure network and systems.
	2. Protect cardholder data.
	3. Maintain a vulnerability management program.
	4. Implement strong access control measures.
	5. Regularly monitor and test networks.
	6. Maintain an information security policy.

![PCI DSS Goals: Build and maintain a secure network, protect cardholder data, maintain a vulnerability management program, implement strong access control measures, regularly monitor and test networks, maintain an information security policy.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/108/graphics/PCI-DSS-Goals.png)

[Source](https://adktechs.com/wp-content/uploads/2019/06/PCI-DSS-Goals.png)

#### ISO 27001

- [ISO/IEC 27001](https://www.iso.org/isoiec-27001-information-security.html) establishes the specification for establishing, implementing, maintaining, and continually improving an Information Security Management System (ISMS).
- In ISO/IEC 27001:2022, Annex A control 8.8 specifically covers "Management of technical vulnerabilities":
	- Requires organizations to obtain timely information about technical vulnerabilities of information systems in use.
	- Requires evaluation of the organization's exposure to those vulnerabilities.
	- Mandates implementation of appropriate mitigating controls based on risk evaluation.
- Testing frequency is not fixed to rigid calendar intervals, but is defined by the organization's internal risk assessment methodology.

### Penetration testing standards

- Professional penetration testing methodologies establish standardized workflows and testing coverage:
- [Penetration Testing Execution Standard (PTES)](http://www.pentest-standard.org/index.php/Main_Page):
	- High-level technical framework defining the core phases of penetration testing:
		1. Pre-engagement interactions.
		2. Intelligence gathering.
		3. Threat modeling.
		4. Vulnerability analysis.
		5. Exploitation.
		6. Post-exploitation.
		7. Reporting.
- [Open Source Security Testing Methodology Manual (OSSTMM)](https://www.isecom.org/OSSTMM.3.pdf):
	- Maintained by ISECOM; provides an empirical, metrics-oriented testing methodology measuring operational security through Risk Assessment Values (RAVs).
	- Covers five security channels: Human (social engineering), Physical, Wireless, Telecommunications, and Data Networks.
- [NIST SP 800-115](https://csrc.nist.gov/pubs/sp/800/115/final) (_Technical Guide to Information Security Testing and Assessment_):
	- Technical methodology for federal security assessments.
	- Defines four primary assessment phases: Planning, Discovery, Attack, and Reporting.
- [Open Worldwide Application Security Project (OWASP)](https://owasp.org/):
	- The standard reference body for application security assessment methodologies:
		- [Web Security Testing Guide (WSTG)](https://owasp.org/www-project-web-security-testing-guide/): comprehensive testing guide covering 12 application security categories (authentication, session management, input validation, authorization, cryptography, business logic).
		- [Mobile Application Security Testing Guide (MASTG)](https://mas.owasp.org/MASTG/): security testing standard for Android and iOS applications.
		- [Firmware Security Testing Methodology](https://github.com/scriptingxss/owasp-fstm): auditing framework for embedded devices and IoT firmware.

## Scoring vulnerabilities

### CVSS

> The **[Common Vulnerability Scoring System (CVSS)](https://www.first.org/cvss/)** is an open industry framework maintained by the Forum of Incident Response and Security Teams (FIRST) for evaluating and communicating the technical severity of software vulnerabilities.

- CVSS provides standardized numeric scores ranging from 0.0 to 10.0, corresponding to qualitative severity ratings:
	- **None**: 0.0
	- **Low**: 0.1–3.9
	- **Medium**: 4.0–6.9
	- **High**: 7.0–8.9
	- **Critical**: 9.0–10.0

![](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/108/graphics/VulnerabilityAssessment_Diagram_08.png)

_Adapted from the original graphic found [here](https://www.first.org/cvss/v3-1/media/MetricGroups.svg)._

#### Base metric group

- The Base Metric Group captures intrinsic qualities of a vulnerability that remain constant over time and across user environments. It contains exploitability metrics, the scope metric, and impact metrics.
- **Exploitability metrics**:
	- **Attack Vector** (`AV`): reflects the context by which vulnerability exploitation is possible: `Network` (`N`), `Adjacent` (`A`), `Local` (`L`), or `Physical` (`P`).
	- **Attack Complexity** (`AC`): reflects the presence of conditions beyond the attacker's control required to execute the exploit: `Low` (`L`) or `High` (`H`).
	- **Privileges Required** (`PR`): measures the level of access an attacker must hold prior to exploitation: `None` (`N`), `Low` (`L`), or `High` (`H`).
	- **User Interaction** (`UI`): determines whether exploitation requires action by a separate user (e.g., clicking a link or opening a file): `None` (`N`) or `Required` (`R`).
- **Scope** (`S`):
	- Captures whether a vulnerability in one software component impacts resources in a separate authorization authority: `Unchanged` (`U`) or `Changed` (`C`). Scope changes occur in vulnerabilities like Cross-Site Scripting (where browser DOM authority is compromised) or virtual machine hypervisor escapes.
- **Impact metrics**:
	- Evaluates direct consequences to the **CIA triad** of the impacted component:
		- **Confidentiality Impact** (`C`): loss of data confidentiality (`None` [`N`], `Low` [`L`], `High` [`H`]).
		- **Integrity Impact** (`I`): unauthorized modification of system state or data (`None` [`N`], `Low` [`L`], `High` [`H`]).
		- **Availability Impact** (`A`): disruption of access to resources or services (`None` [`N`], `Low` [`L`], `High` [`H`]).

![](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/108/graphics/cia_triad.png)

#### Temporal metric group

- The Temporal Metric Group measures attributes of a vulnerability that change over time as exploits and remediations develop:
	- **Exploit Code Maturity** (`E`): measures the availability and reliability of exploit mechanisms: `Not Defined` (`X`), `Unproven` (`U`), `Proof-of-Concept` (`P`), `Functional` (`F`), or `High` (`H`).
	- **Remediation Level** (`RL`): reflects the availability of official workarounds and patches: `Not Defined` (`X`), `Official Fix` (`O`), `Temporary Fix` (`T`), `Workaround` (`W`), or `Unavailable` (`U`).
	- **Report Confidence** (`RC`): measures the degree of confidence in the existence of the vulnerability and the validity of technical details: `Not Defined` (`X`), `Unknown` (`U`), `Reasonable` (`R`), or `Confirmed` (`C`).

#### Environmental metric group

- The Environmental Metric Group allows an organization to customize the score to its internal infrastructure context:
	- **Security Requirements** (`CR`, `IR`, `AR`): adjusts the impact score based on the organizational importance of Confidentiality, Integrity, and Availability for the affected asset (`Not Defined` [`X`], `Low` [`L`], `Medium` [`M`], `High` [`H`]).
	- **Modified Base Metrics** (`MAV`, `MAC`, `MPR`, `MUI`, `MS`, `MC`, `MI`, `MA`): overrides base metric values when compensating controls are deployed in the target environment (such as isolating a vulnerable network service behind an air-gapped network).

#### CVSS vector string

- CVSS calculations produce a standardized **vector string** summarizing all metric values:
	- `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H`
- This vector represents the base score of the Windows Print Spooler remote code execution vulnerability (PrintNightmare, [[#CVE examples]]), yielding a CVSS Base Score of 8.8 (High).
- Vector components:
	- `AV:N`: Network attack vector.
	- `AC:L`: Low attack complexity.
	- `PR:L`: Low privileges required.
	- `UI:N`: No user interaction required.
	- `S:U`: Unchanged scope.
	- `C:H/I:H/A:H`: High confidentiality, integrity, and availability impact.

#### CVSS v4.0

- FIRST published CVSS v4.0 in November 2023, introducing several architectural changes:
	- **Restructured metric groups**: Base, Threat (replaces Temporal, isolating **Exploit Maturity**), Environmental, and Supplemental.
	- **Supplemental metric group**: provides operational context (including `Automatable`, `Recovery`, `Safety`, `Vulnerability Response Effort`, and `Provider Urgency`) without altering the calculated numeric score.
	- **Base metric refinements**: adds **Attack Requirements** (`AT`: `None` [`N`], `Present` [`P`]) and divides User Interaction into `None` (`N`), `Passive` (`P`), and `Active` (`A`).
	- **Deprecation of Scope**: replaces the Scope metric with explicit impact separation:
		- **Vulnerable System Impact**: `VC`, `VI`, `VA` (impact on the target component).
		- **Subsequent System Impact**: `SC`, `SI`, `SA` (impact on external systems or authorization boundaries).
	- **Nomenclature**: designates which metric groups are factored into the score:
		- `CVSS-B`: Base metrics only.
		- `CVSS-BT`: Base and Threat metrics.
		- `CVSS-BE`: Base and Environmental metrics.
		- `CVSS-BTE`: Base, Threat, and Environmental metrics.

### DREAD

> **[DREAD](https://en.wikipedia.org/wiki/DREAD_\(risk_assessment_model\))** is a threat-modeling risk assessment model originally developed by Microsoft to evaluate and prioritize software security vulnerabilities.

- DREAD rates five attributes on a scale from 1 to 10 (or 0 to 10), calculating the risk score as the arithmetic mean:
  $$\text{DREAD Score} = \frac{D + R + E + A + D}{5}$$
- The five evaluation factors:
	- **Damage potential**: the severity of damage resulting from successful exploitation.
	- **Reproducibility**: the ease and consistency with which the attack can be repeated.
	- **Exploitability**: the technical skill, tooling, and resources necessary to execute the attack.
	- **Affected users**: the proportion or quantity of users and systems impacted by compromise.
	- **Discoverability**: the ease with which an attacker can identify the weakness.
- While discoverability ratings encourage security through obscurity and can produce subjective inconsistencies between assessors, DREAD remains a foundational conceptual reference in application threat modeling.

## Classifying and cataloging vulnerabilities

### OVAL

> **[Open Vulnerability and Assessment Language (OVAL)](https://oval.mitre.org/)** is an open XML-based specification maintained by the Center for Internet Security (CIS) for standardizing the evaluation and reporting of machine configuration states and software vulnerabilities.

- OVAL provides a standardized machine-readable schema for querying system state without active exploitation. It is a core component of NIST's **Security Content Automation Protocol (SCAP)**.
- Scanners (including Nessus, OpenVAS, and specialized SCAP interpreters) use OVAL definitions to evaluate target configurations against technical compliance profiles.

#### OVAL assessment process

- The OVAL execution process consists of three steps:
	1. **Data collection**: identify and collect system configuration parameters and state information.
	2. **State evaluation**: evaluate collected items against criteria defined in OVAL definitions.
	3. **Report generation**: output compliance and vulnerability findings (`Vulnerable`, `Not Vulnerable`, `Compliant`, `Non-compliant`, `Error`).

![](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/108/graphics/VulnerabilityAssessment_Diagram_05.png)

_Adapted from the original graphic found [here](https://oval.mitre.org/documents/docs-05/extras/0505Martin_f3.gif)._

#### OVAL definitions

- OVAL definitions use an XML schema containing four core classes:
	- `Vulnerability Definitions`: verify presence of specific software bugs or unpatched states.
	- `Compliance Definitions`: verify whether configurations meet security baseline policies.
	- `Inventory Definitions`: determine the presence of installed software assets or hardware configurations.
	- `Patch Definitions`: evaluate whether specific vendor security patches are installed.
- Core schema constructs:
	- **Objects**: specific system elements to inspect (files, registry keys, packages).
	- **States**: expected attributes or values of objects (file hashes, permissions, registry DWORD values).
	- **Tests**: logical assertions comparing objects to states.
	- **Variables**: dynamic values or external inputs provided to objects or states during evaluation.
- Identifier format: `oval:<organization_domain>:<id_type>:<id_value>`
	- `id_type` values include definition (`def`), object (`obj`), state (`ste`), and variable (`var`).
	- Example: `oval:org.mitre.oval:obj:1116`.

### CVE

> The **[Common Vulnerabilities and Exposures (CVE)](https://www.cve.org/)** program is an international dictionary of publicly known cybersecurity vulnerabilities, sponsored by the US Cybersecurity and Infrastructure Security Agency (CISA) and operated by MITRE.

- CVE assigns unique, standardized identifiers (**CVE IDs**) to confirmed vulnerabilities, ensuring disparate security products, researchers, and tools reference identical issues consistently.
- Format: `CVE-YYYY-NNNN...`
	- `YYYY`: the year the CVE identifier was reserved (not necessarily the year of discovery or public release).
	- `NNNN...`: a sequential identification number of four or more digits.
- To qualify for a CVE ID, a security issue must meet three mandatory criteria:
	- **Independently fixable**: the flaw can be remediated independently of other vulnerabilities.
	- **Single codebase or vendor**: the issue affects a distinct codebase; shared libraries used across multiple vendors are coordinated under separate assignments.
	- **Vendor or community acknowledgment**: the vendor or maintainer confirms that the behavior has negative security impact violating the product's security specification.

![](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/108/cve/VulnerabilityAssessment_Diagram_01.png)

_Adapted from the original graphic [here](https://www.balbix.com/app/uploads/what-is-a-CVE-1024x655.png)._

#### Obtaining a CVE ID

1. **Verify qualification**: confirm the issue meets the CVE definition of a vulnerability and that no duplicate CVE ID exists.
2. **Engage the product vendor**: submit detailed technical vulnerability findings to the vendor under coordinated vulnerability disclosure.
3. **Contact the relevant CNA**: submit an ID request to the appropriate **CVE Numbering Authority (CNA)**. Vendors acting as CNAs (such as Microsoft, Red Hat, Apple) assign IDs directly for their products; otherwise, contact a regional or coordinating CNA (such as CERT/CC) or the Root CNA.
4. **Submit web request**: if no direct CNA covers the product, request an ID through the official [CVE web portal](https://cveform.mitre.org/).
5. **Receive confirmation and reservation**: the CNA or CVE team validates the technical documentation and reserves an unannounced CVE ID.
6. **Coordinate patch availability**: the vendor engineers and validates the remediation patch within the agreed disclosure window.
7. **Public disclosure**: the vendor releases the security advisory and remediation patch concurrently with the CVE publication.
8. **Record enrichment**: MITRE and the [National Vulnerability Database (NVD)](https://nvd.nist.gov/) index the CVE record, associating CVSS scores, CWE mappings, and CPE configuration strings.

> [!quote] According to the CVE Program: "A vulnerability is a weakness in the computational logic (for example, code) found in software and hardware components that, when exploited, results in a negative impact to confidentiality, integrity, or availability."

#### Vulnerability disclosure models

- **Coordinated Vulnerability Disclosure (CVD)**:
	- The researcher privately reports technical details to the vendor, agreeing on a confidential remediation timeline (commonly 60 to 90 days).
	- Details are published concurrently with the vendor's security update, preventing malicious exploitation during development.
- **Full disclosure**:
	- Detailed vulnerability findings and exploit mechanisms are published immediately without prior vendor coordination.
	- Supporters argue this forces rapid vendor remediation; opponents note it introduces zero-day exposure to end users before fixes exist.
- **Zero-day (0-day)**:
	- A vulnerability actively known or exploited in the wild before the vendor is aware or has released an official security fix.
- **RFC 9116 (`security.txt`)**:
	- A standardized text file placed at `/.well-known/security.txt` defining security contact addresses, PGP keys, disclosure policies, and preferred languages for reporting vulnerabilities.

#### CVE examples

- [CVE-2020-5902](https://www.cve.org/CVERecord?id=CVE-2020-5902):
	- Critical unauthenticated remote code execution vulnerability in the BIG-IP Traffic Management User Interface (TMUI).
	- Exploitable via directory traversal within the web administration portal, allowing remote attackers to execute arbitrary system commands, manipulate files, and disable services.
- [CVE-2021-34527](https://www.cve.org/CVERecord?id=CVE-2021-34527) (PrintNightmare):
	- Remote code execution and local privilege escalation vulnerability in the Windows Print Spooler service (`spoolsv.exe`).
	- Improper validation of privileged file operations during printer driver installation allows authenticated users to execute arbitrary code with `SYSTEM` privileges on Windows servers and Domain Controllers.

### Related vulnerability databases

- Public databases and frameworks complement the CVE system:
	- [National Vulnerability Database (NVD)](https://nvd.nist.gov/): NIST's repository that enriches CVE entries with CVSS vectors, [[#CWE]] classifications, and **Common Platform Enumeration (CPE)** asset strings.
	- [Common Weakness Enumeration (CWE)](https://cwe.mitre.org/): MITRE's structural categorization of underlying software and hardware architecture, design, and code weaknesses (e.g., `CWE-89` for [[SQL injection]], `CWE-79` for Cross-Site Scripting, `CWE-787` for Out-of-bounds Write).
	- [CISA Known Exploited Vulnerabilities (KEV) Catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog): authoritative registry of CVEs confirmed to be weaponized and actively exploited in real-world attacks. Under Binding Operational Directive (BOD) 22-01, US federal civilian executive branch agencies must remediate KEV flaws within strict deadlines.
	- [Exploit Prediction Scoring System (EPSS)](https://www.first.org/epss/): FIRST data-driven scoring system predicting the statistical probability (0.0 to 1.0) and percentile that a software vulnerability will be exploited in the wild within 30 days.

## Vulnerability scanning

- Vulnerability scanning is the automated identification of unpatched software, misconfigurations, and architectural vulnerabilities across network systems, servers, endpoints, and applications.
- Scanners maintain extensive vulnerability signature databases (plugins) that query service ports, parse banners, evaluate protocols, and inspect system states.
- Scanning tools identify potential vulnerabilities without executing weaponized payloads, serving as an automated component within broader penetration testing and vulnerability management workflows.

### Credentialed vs. non-credentialed scanning

- **Non-credentialed (unauthenticated) scanning**:
	- Scans targets over the network from an external perspective without system access.
	- Identifies exposed ports, listening service banners, transport layer encryption protocols, and externally accessible endpoints.
	- Limited to surface-level visibility and prone to false positives caused by backported software patches where banners do not reflect applied fixes.
- **Credentialed (authenticated) scanning**:
	- Scanners authenticate to target endpoints using administrative credentials via SSH, SMB, or WMI.
	- Directly inspects local file systems, installed package manifests (`dpkg`, `rpm`), registry configurations, running processes, and patch databases.
	- Provides high-fidelity results, identifies local privilege escalation vectors invisible from the network, and reduces false positives.

### Static and dynamic testing mechanisms

- **Static (version/banner-based) checks**:
	- Compares the reported software version against vulnerability databases.
	- Susceptible to reporting false positives on Linux distributions (such as Debian, Ubuntu, or Red Hat) that backport security patches into older upstream package versions without incrementing the primary version number.
- **Dynamic (active/probing) checks**:
	- Transmits non-destructive, targeted payloads to evaluate application or protocol responses directly (e.g., verifying SQL error messages or path traversal reflections).
	- Provides higher confidence by empirically confirming that the vulnerable code execution path is active.

### Scan results: accuracy and error states

- **False positive**:
	- The scanner reports a vulnerability that does not exist on the target system (e.g., flagging an unpatched version due to banner information despite backported fixes or compensating network controls).
	- Wastes engineering resources during triage; requires verification and scanning policy exclusions.
- **False negative**:
	- The scanner fails to identify a real vulnerability present on the target (e.g., due to firewall filtering, missing authentication credentials, scanner signature gaps, or zero-day flaws).
	- False negatives represent unseen operational risk; a scan report displaying zero findings does not demonstrate that a system is secure.

### Vulnerability scanners

| Scanner | Description |
| :--- | :--- |
| **Tenable Nessus** | Identify vulnerabilities, configuration baselines, and missing patches across enterprise networks and operating systems. |
| **Qualys VMDR** | Provide cloud-based vulnerability management, continuous asset discovery, and endpoint compliance assessment. |
| **Rapid7 InsightVM / Nexpose** | Assess infrastructure risk with live dashboards, vulnerability prioritization, and Metasploit exploit verification integration. |
| **Greenbone OpenVAS** | Perform open-source network and host vulnerability scanning powered by the Greenbone Community Feed. |

![](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/108/Nessus_Essentials___Folders___View_Scan.png)

![](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/108/openvas/dashboard.png)
