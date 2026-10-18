---
created: 2026-09-27
updated: 2026-09-28
tags:
  - OSINT
  - methodology
  - intel
---
## OSINT

- **OSINT (Open-Source Intelligence)** gathers information about the target from publicly available sources — without directly interacting with the target's infrastructure.

### Searching the web

>[!note] See [[🛠️ Searching the web]].

- Narrow results to a single domain and file type with search operators:

```text
site:example.com filetype:pdf confidential
```

### Registration data

>[!note] See [[WHOIS]].

- Query registration, registrar, and contact data for a domain:

```bash
whois example.com
```

### Secrets in Git repositories

>[!note] See [[🛠️ Finding secrets in Git repositories]].

- Scan a repository's full history for committed secrets:

```bash
trufflehog git https://github.com/org/repo
```

### Username enumeration

>[!note] See [[◯ OSINT username enumeration]].

- Search for a username across many social and web platforms:

```bash
sherlock jdoe
```

### Automation frameworks

>[!note] See [[🛠️ Automation]].

- Automate multi-source collection (subdomains, emails, hosts) with theHarvester:

```bash
theHarvester -d example.com -b all
```
