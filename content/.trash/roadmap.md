---
created: 2026-08-16
updated: 2026-10-04
---

- `comm`


To do:


- Finish [[🛠️ Authenticated AD & Windows enumeration]]
- [[🛠️ BloodHound]]
- [x] ACL attacks in AD
- [[Privileged remote access]]
- AD CS and `certipy`
- [[◯ Shadow credentials]]


 - Linux tools
	- **LDAP:** `ldapsearch`, `windapsearch`, `bloodyAD`, `ldeep`
	- **Multi-protocol AD enumeration:** `NetExec`
	- **SMB:** `smbclient`, `smbmap`, `NetExec`
	- **RPC:** `rpcclient`, `enum4linux-ng`
	- **Kerberos:** Impacket `GetUserSPNs.py`, `GetNPUsers.py`, `getTGT.py`, `getST.py`
	- **AD ACLs:** `bloodyAD`, Impacket `dacledit.py`, `owneredit.py`
	- **BloodHound:** `bloodhound-python`
	- **AD CS:** `certipy`
	- **DNS:** `dig`, `dnsrecon`, `adidnsdump`
	- **WinRM:** `evil-winrm`, `NetExec`
	- **MSSQL:** `mssqlclient.py`, `NetExec`
	- **General network discovery:** `nmap`


- Protocols
	- WinRM
		- Enumeration: [[🛠️ Authenticated AD & Windows enumeration#5985/5986 — WinRM]]
		- Password cracking: [[🛠️ Network protocols#WinRM]]
		- Remote access: 