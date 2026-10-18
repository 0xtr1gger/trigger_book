---
title: 0xtr1gger book
created: 2026-09-06
updated: 2026-10-18
---

## Start here

- [[🛠️ Penetration testing methodology]] — the root of the methodology tree. Follow its links from information gathering down to individual techniques.

## Sections

- [[Intelligence/|Intelligence]] — all about recon, OSINT, enumeration. Start with [[🛠️ Information gathering methodology]].
	- [[Intelligence/OSINT/|OSINT]] — searching public sources ([[🛠️ OSINT methodology]]).
	- [[Intelligence/Asset Discovery/|Asset Discovery]] — all about initial reconnaissance stages where you need to get basic information about the target and a list of IP addresses or subdomains to test.
	- [[Intelligence/Web discovery/|Web discovery]] — web recon which doesn't exploit vulnerabilities ([[Web discovery and enumeration methodology]]).
	- [[Intelligence/Nmap/|Nmap]] — all about Nmap.
- [[Hack the Web/|Hack the Web]] — main place for notes on web application security. Start with [[Web application security testing methodology]].
	- [[Hack the Web/Authentication & Authorization/|Authentication & Authorization]] — vulnerabilities related to authentication, authorization, or session handling, including issues in login flows, JWT attacks, OAuth vulnerabilities, and the like.
	- [[Hack the Web/Injection/|Injection]] — server-side injection vulnerabilities such as SQL injection, OS command injection, and so on.
	- [[Hack the Web/Client-Side/|Client-Side]] — client-side vulnerabilities such as XSS, CSRF, WebSockets, and others.
	- [[Hack the Web/Server-Side/|Server-Side]] — server-side vulnerabilities beyond injection.
	- [[Hack the Web/Intermediaries/|Intermediaries]] — vulnerabilities that mostly occur due to discrepancies between how the front-end and back-end servers handle user requests, such as `Host` header attacks and HTTP request smuggling.
	- [[Hack the Web/API/|API]] — everything API-specific (REST API, GraphQL).
	- [[Hack the Web/Applications & Friends/|Applications & Friends]] — attacking specific applications or frameworks or anything of a kind like CMSs, say, WordPress.
		- CMS — well, attacking CMSs: [[WordPress]], [[Drupal]].
		- [[GitLab]]
	- [[Hack the Web/Essential skills/|Essential skills]] — general techniques that come in useful during most attacks, such as encoding obfuscation and quick scanning with Burp Suite.
	- [[Hack the Web/Cheat Sheets/|Cheat Sheets]] — a common place for web cheat sheets I made.
- [[Attacking Enterprise Networks/|Attacking Enterprise Networks]] — attacking network services and protocols (FTP, SMB, RDP, SSH, databases, mail, and more) and searching for known vulnerabilities. Start with [[Attacking network services methodology]].
- [[Active Directory/|Active Directory]] — attacking Active Directory: enumeration, Kerberos, NTLM, ACL, and password attacks, poisoning and relaying, domain trusts. Start with [[🛠️ AD testing methodology]].
- [[Windows/|Windows]]
	- [[Windows/Windows Commands & Scripts/|Windows Commands & Scripts]] — file transfers, persistence, privileged remote access.
	- [[Windows/Windows PrivEsc/|Windows PrivEsc]] — local privilege escalation: privileges, privileged groups, potato attacks, credential harvesting, service and registry misconfigurations, and more.
- [[Linux/|Linux]]
	- [[Linux/Linux Commands & Scripts/|Linux Commands & Scripts]] — file transfers, persistence, domain-joined Linux machines.
	- [[Linux/Linux PrivEsc/|Linux PrivEsc]] — local privilege escalation on Linux.
- [[Shells & Payloads/|Shells & Payloads]]
	- [[Shells & Payloads/Shells/|Shells]] — bind, reverse, and web shells, upgrading shells, Metasploit and MSFvenom.
	- [[Shells & Payloads/Pivoting, Tunneling & Port Forwarding/|Pivoting, Tunneling & Port Forwarding]] — moving deeper into a network through compromised hosts ([[🛠️ Network pivoting primer]]).
	- [[Shells & Payloads/Remote Password Attacks/|Remote Password Attacks]] — attacking credentials of network services.
	- [[Shells & Payloads/Cracking Hashes/|Cracking Hashes]] — cracking password hashes and protected files.
- [[Commands & Cheat Sheets/|Commands & Cheat Sheets]] — general command references.
- [[Tools/|Tools]] — notes on individual tools such as ffuf, NetExec, and Responder.
- [[Walkthrough/|Walkthrough]] — machine write-ups and PortSwigger Web Security Academy labs.
- [[The Dev & Sec & Ops/|The Dev & Sec & Ops]] — security concepts, GCP, Git, Python, Terraform.
- [[Uncategorized/|Uncategorized]] — some useful topics that I don't yet know where to stuff in the current blog structure. As this place expands, I might find it a place.

## About note statuses

- There are no "finished" notes on this website. Learning continuously, I know how much I don't know and what my notes might miss. I can't add everything at ones, so I continue developing and gradually bettering this blog. And if I ever happen to thing I wrote everything I needed, I won't make the note "finished" either — it just means I don't yet know what I don't know. 
- But it doesn't mean that all unfinished notes are complete drafts — no. Most of my notes actually look complete and will stay like this for some time for sure. I call those "substantial".
