---
created: 05-01-2026
---

## Linux privilege escalation 


1. Enumeration — [[Inside the System/Linux/Linux_PrivEsc/enumeration]] 
2. Sudo privilege escalation — [[sudo_privilege_escalation]] ✔️
3. SUID & SGID privilege escalation — [[SUID_&_SGID_privilege_escalation]] ✔️
4. Sensitive information & credential abuse — [[credentials_hunting_and_sensitive_information]] ✔️
5. Weak file permissions — [[insecure_file_permissions]] ✔️
6. `PATH` hijacking — [[PATH_hijacking]] ✔️
7. Cron — [[Cron_jobs_privilege_escalation]] ✔️
8. Systemd timers — [[systemd_timers_and_services]] ✔️
9. Capabilities [[capabilities]] ✔️
10. Environment variable abuse [[environment_variables]] ✔️
11. Shared library hijacking [[shared_library_hijacking]] ✔️
12. Privileged groups — [[privileged_groups]] ✔️
---
1. Mounts, filesystems, NFS ([[_mounts_filesystems_NFS]])
	- Mounted filesystems
	- `no_root_squash`
	- Writable mounts
	- Bind mounts
	- NFS misconfigurations
	- CIFS/SMB mounts
	- Device mounts abuse
2. Kernel exploits
	- Kernel version identification    
	- Exploit matching
	- Compile vs precompiled exploits
	- File transfer methods
	- Kernel exploit safety checks
	- Dirty Pipe / Dirty COW class bugs
	- CPTS emphasis: reasoning before exploiting
3. `logrotate` — [[Inside the System/Linux/Linux_PrivEsc/_logrotate_privilege_escalation]]
4. `doas` — [[_doas]] (just stuff to Claude to proofread this)
5. File transfers [[Linux_file_transfers]] ✔️

---

Other attacks and techniques:
- Log file abuse
	- Writable log files
	- Log poisoning
	- Logs parsed by root scripts
	- Cron + logs
	- Monitoring services  
	- Web logs → code execution
- Misconfigured local services 
	- Services running as root
	- Listening on localhost only
	- Writable config files
	- Debug modes
	- Command execution via config
	- Service reload abuse
	- IPC / sockets abuse


| Registry hive               | Supporting files                                                       |
| --------------------------- | ---------------------------------------------------------------------- |
| HKEY_LOCAL_MACHINE\SAM      | Sam, Sam.log, Sam.sav                                                  |
| HKEY_LOCAL_MACHINE\Security | Security, Security.log, Security.sav                                   |
| HKEY_LOCAL_MACHINE\Software | Software, Software.log, Software.sav                                   |
| HKEY_LOCAL_MACHINE\System   | System, System.alt, System.log, System.sav                             |
| HKEY_CURRENT_CONFIG         | System, System.alt, System.log, System.sav, Ntuser.dat, Ntuser.dat.log |
| HKEY_USERS\DEFAULT          | Default, Default.log, Default.sav                                      |
### Topic to ChatGPT

```
Hello, act as a Cybersecurity expert, Windows researcher and instructor, with expertise, years of experience, and many advanced certificates, including OSCP and CPTS. You are aware of these exams' expectations and real exam patterns. I'm trying to prepare to OSCP and CPTS myself, and now focusing on how Windows work (before actual exploitation).

Give me please a comprehensive list of topics I need to know about the Windows registry for my goal of Windows security for OSCP/CPTS
```
### Restructure with more paraphrasing

```
Hello, act as a Cybersecurity expert, researcher and instructor, with expertise, years of experience, and many advanced certificates, including OSCP and CPTS. You are aware of these exams' expectations and real exam patterns. I'm trying to prepare to OSCP and CPTS myself.

I'm asking you to completely restructure, rewrite, improve my notes on 
how Kerberos works

My draft is just an outline of possible structure, and it's almost empty. you should write it from scratch.

- The more sentences you paraphrase the better. I fill that this doesn't sound right, and I ask you to fix it. Natural, human, technical, fluent.
    
- Add explanations.
    
- Add commands if needed.
    
- Structure sections and paragraphs logically.
    
- Style:
    
    - Not overly academic
        
    - Very technical and explanatory
        
    - Written by a practitioner for other hackers
        
    - Write like a skilled offensive security practitioner explaining things to other hackers
        
    - Technical but readable
        
    - Confident, clear, and precise
        
    - Commands should be realistic and OSCP-relevant
        
- Do NOT summarize or “clean up” by removing depth — expand instead.
    
    - If you can add more, aside from what is in the list, add it.
        

The final guide must:

- Be approximately 2,000–4,000 words - Include both detection and exploitation logic

- Explain not only “how” but also “why” techniques work

- Include realistic OSCP-style exploitation examples

- Include common pitfalls, false positives, and time-wasting traps - Emphasize enumeration-to-exploitation decision-making

- Avoid pure copy-paste GTFOBins/command usage; explain reasoning behind each technique

Produce a single, fully rewritten, polished, comprehensive guide that merges my content and the required topic list into one cohesive document, suitable for publishing as a standalone Linux privilege escalation reference.

This is Obsidian Markdown, and you should output in this format, too. 

```

### Reworked by GPT


### Standard restructure

```bash
You are acting as an expert Linux privilege escalation researcher and instructor, with deep familiarity with OSCP and CPTS expectations, real exam patterns, and common candidate failure points.

I will provide you with:
1) My current version of the note on Linux privilege escalation via miunts/filesystems/NFS (may be incomplete, messy, or uneven)
2) A reference list of required topics and sub-topics that this note MUST cover

Your task is to produce a single, complete, refined, and publish-ready guide that:
- Preserves my original writing style and tone:
  - Not overly academic
  - Very technical and explanatory
  - Written by a practitioner for other hackers
- Prioritizes completeness and correctness over brevity
- Is suitable for OSCP and CPTS preparation
- Is suitable for public publication (clear structure, good flow, readable but dense)

CRITICAL RULES (DO NOT VIOLATE):
- If my original note contains content NOT present in the reference topic list, you MUST keep it and integrate it naturally.
- If the reference topic list contains content NOT present in my note, you MUST generate that content from scratch.
- Preference is ALWAYS given to completeness and comprehensiveness.
- If something is ambiguous or underspecified in my note, clarify and expand it.
- Never omit a technique, edge case, or exploitation path that could realistically matter in OSCP or CPTS.
- Do NOT summarize or “clean up” by removing depth — expand instead.
  - If you can add more, aside from what is in the list or my note, add it.

CONTENT REQUIREMENTS:
The final guide must:
- Be approximately 2,000–4,000 words
- Include both detection and exploitation logic
- Explain not only “how” but also “why” techniques work
- Include realistic OSCP-style exploitation examples
- Include common pitfalls, false positives, and time-wasting traps
- Emphasize enumeration-to-exploitation decision-making
- Avoid pure copy-paste GTFOBins usage; explain reasoning behind each abuse

STRUCTURE REQUIREMENTS:
Organize the guide using a clear, consistent structure such as:
- High-level overview of the technique
- Why it matters in OSCP/CPTS
- How to detect it (commands, files, indicators)
- Exploitation techniques (multiple where applicable)
- Chaining with other privesc vectors
- Common mistakes and false positives
- Practical OSCP mindset notes

STYLE REQUIREMENTS:
- Write like a skilled offensive security practitioner explaining things to other hackers
- Technical but readable
- Confident, clear, and precise
- No fluff, no motivational talk, no beginner hand-holding
- Use bullet points, code blocks, and sections where appropriate
- Commands should be realistic and OSCP-relevant

ASSUMPTIONS:
- The reader already knows basic Linux and shell usage
- The reader is preparing for OSCP or CPTS
- The guide should help the reader succeed under time pressure

OUTPUT:
Produce a single, fully rewritten, polished, comprehensive guide that merges my content and the required topic list into one cohesive document, suitable for publishing as a standalone Linux privilege escalation reference.

Wait for me to provide:
1) The reference topic list
2) My current note

Then proceed.
---

1) The reference topic list on mounts/filesystems/NFS:
	- Mounted filesystems
	- `no_root_squash`
	- Writable mounts
	- Bind mounts
	- NFS misconfigurations
	- CIFS/SMB mounts
	- Device mounts abuse
	  
2) My current note
   

```




## Windows
### How Windows works


- [[Windows_services]]
- Windows registry
- LSASS

So, SCM is a remote procedure call server. Could you please tell me more about RPC?
### Windows privilege escalation

The general goal of Windows privilege escalation is to further out access to a given system by gaining access to an account with higher privileges. The most common targets are the `NT AUTHORITY\SYSTEM` (`LocalSystem`) user, `administrator` user, or membership in the `Administrators` group.

>[!tip]+ Windows privilege escalation targets
>- `NT AUTHORITY\SYSTEM` (`LocalSystem`)
>- `adminstrator` user
>- `Administrators` group

Common ways to escalate privileges on a Windows machine include:

- Abusing group privileges
- Abusing user privileges
- Bypassing UAC (User Account Control)
- Abusing weak service/file permissions
- Exploiting unpatched kernel vulnerabilities
- Credential theft
- Traffic sniffing
- etc.


>[!bug] Sometimes code execution can be achieved with **file association hijacking** attacks (e.g., `.exe`, `.msi`, `.lnk`).

>[!bug] **[UAC (User Account Control)](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/user-account-control/)** can often be bypassed with COM object hijacking (via `CLSID` keys).

>[!bug] Service configurations under `HKLM\SYSTEM\CurrentControlSet\Services` are the prime targets for privilege escalation via **service hijacking**.
### Roadmap

- CPTS
	- https://www.brunorochamoura.com/posts/cpts-tips/

- [[Inside the System/Windows/enumeration|enumeration]]


- Potato attacks:
	- https://hideandsec.sh/books/windows-sNL/page/in-the-potato-family-i-want-them-all
	- https://jlajara.gitlab.io/Potatoes_Windows_Privesc
	- https://www.plesk.com/kb/support/microsoft-windows-seimpersonateprivilege-local-privilege-escalation/
	- https://www.drakeaxelrod.com/notes/windows/seimpersonate-privilege
---

-  [`Splunk Universal Forwarder Hijacking`](https://airman604.medium.com/splunk-universal-forwarder-hijacking-5899c3e0e6b2) and [SplunkWhisperer2](https://clement.notin.org/blog/2019/02/25/Splunk-Universal-Forwarder-Hijacking-2-SplunkWhisperer2/).
- [`Erlang-arce blogpost from Mubix`](https://malicious.link/post/2018/erlang-arce/)
### Useful tools

| Tool                                                                                                | Description                                                                                                                                                                                                                                                                                                                                                                     |
| --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`Seatbelt`](https://github.com/GhostPack/Seatbelt)                                                 | Performs a number of safety checks on local Windows privilege escalation.                                                                                                                                                                                                                                                                                                       |
| [`winPEAS`](https://github.com/peass-ng/PEASS-ng/tree/master/winPEAS)                               | Searches possible privilege escalation vectors on a Windows system.<br>All techniques are explained in [`book.hacktricks.wiki`](https://book.hacktricks.wiki/en/windows-hardening/checklist-windows-privilege-escalation.html).                                                                                                                                                 |
| [`PowerUp.ps1`](https://github.com/PowerShellMafia/PowerSploit/blob/master/Privesc/PowerUp.ps1)     | A PowerShell script for finding common Windows privilege escalation vectors; focuses on misconfiguration vulnerabilities.<br>A part of [`PowerSploit`](https://github.com/PowerShellMafia/PowerSploit/tree/master), a public archive of PowerShell scripts that can be used to aid penetration testers during all phases of security assessments.                               |
| [`SharpUp`](https://github.com/GhostPack/SharpUp)                                                   | A C# version of `PowerUp.ps1`.                                                                                                                                                                                                                                                                                                                                                  |
| [`JAWS`](https://github.com/411Hall/JAWS)                                                           | Just Another Windows (Enum) Script (JAWS), written in PowerShell 2.0 (should work on all Windows versions since Windows 7) and designed to quickly identify potential privilege escalation vectors on Windows systems.                                                                                                                                                          |
| [`SessionGopher`](https://github.com/Arvanaghi/SessionGopher)                                       | A PowerShell script designed to find and save session information for PuTTY, WinSCP, FileZilla, SuperPuTTY, and RDP.                                                                                                                                                                                                                                                            |
| [`Watson`](https://github.com/rasta-mouse/Watson)                                                   | Watson is a .NET tool designed to enumerate missing KBs and suggest exploits for privilege escalation vulnerabilities.                                                                                                                                                                                                                                                          |
| [`LaZagne`](https://github.com/AlessandroZ/LaZagne)                                                 | A Python tools designed to automatically retrieve passwords stored on a local Windows system. Supported software includes a variety of web browsers (Firefox, Chrome, Brave, etc.), chats (Skype), databases (PostgreSQL, DBVisualizer), Git, KeePass, VNC, WSL, wireless networks, and other.<br>Also works on Linux and Mac (though the supported software set is different). |
| [`wesng`](https://github.com/bitsadmin/wesng)                                                       | Windows Exploit Suggester - Next Generation (WES-NG). <br>Based on the output of the `systeminfo` command, provides a list of vulnerabilities the OS is likely to be vulnerable to, as well as exploits.                                                                                                                                                                        |
| [`Sysinternals Suite`](https://learn.microsoft.com/en-us/sysinternals/downloads/sysinternals-suite) | Sysinternals Troubleshooting Utilities; a set of troubleshooting tools and help flies for Windows. May be useful during penetration tests.                                                                                                                                                                                                                                      |

### Prompts 

```
Hello, act as a Cybersecurity expert, Windows researcher and instructor, with expertise, years of experience, and many advanced certificates, including OSCP and CPTS. You are aware of these exams' expectations and real exam patterns. I'm trying to prepare to OSCP and CPTS myself, and now focusing on how Windows work (before actual exploitation). 

I'm asking you to generate a huge and comprehensive guide to Windows sessions. Create a publish-ready professional-grade comprehensive guide/article; you should write it from scratch.

- Natural, human, technical, fluent.
    
- Add explanations.
    
- Add commands if needed.
    
- Structure sections and paragraphs logically.
    
- Style:
    
    - Not overly academic
        
    - Very technical and explanatory
        
    - Written by a practitioner for other hackers
        
    - Write like a skilled offensive security practitioner explaining things to other cybersecurity professionals
        
    - Technical but readable
        
    - Confident, clear, and precise
        
    - Commands should be realistic and OSCP-relevant
        
- Do NOT summarize or “clean up” by removing depth — expand instead.
    
    - If you can add more, aside from what is in the list, add it.

The final guide must:

- Be approximately 2,000–4,000 words - Include both detection and exploitation logic
- Explain not only “how” but also “why” techniques work
- Include realistic OSCP-style exploitation examples
- Include common pitfalls, false positives, and time-wasting traps - Emphasize enumeration-to-exploitation decision-making
- Avoid pure copy-paste GTFOBins/command usage; explain reasoning behind each technique Produce a single, polished, comprehensive guide that merges my content and the required topic list into one cohesive document, suitable for publishing as a standalone Linux privilege escalation reference. This is Obsidian Markdown, and you should output in this format, too.
```

#### Topic

```
Hello, act as a Windows and Cybersecurity expert, researcher and instructor, with expertise and years of experience, as well as many advanced certificates, including OSCP and CPTS. You are aware of these exams' expectations and real exam patterns. I'm trying to prepare to OSCP and CPTS myself, and currently introducing myself to core Windows theory (not exploitation, just learning how Windows works what will be necessary for the exam).

Give me please a huge and comprehensive guide to Windows services — everything I need to know about it, including but not limited to:
- what are windows services
- windows service accounts
- SCM
- `services.msc` MMC
- critical system services (https://learn.microsoft.com/en-us/windows/win32/rstmgr/critical-system-services)
- how it all works!!!

Use complete sentences, technical narrative style (do not just give a pile of bullet points); paragraphs, please, not lists.
Be as detailed as possible, covering from beginner to advanced.

Include descriptions of different parts of the system responsible for user authentication. Different authentication methods. How exactly it all works. Mention access tokens, when they are issued, permissions, etc.

No length restrictions on your responses. Let it be as long as it needs to, to cover the topic properly.

Do not over-simplify complex topics.

Remember the advanced nature or OSCP and mention everything for a person to pass successfully - never omit something what may be necessary. The success of the person depends on your guide (assuming they follow it strictly and practice), so don't let them fail.

(But now we're working on necessary knowledge, not exploitation)

Make this guide as detailed as possible, aiming for at least 2,000–3,000 words, and include examples, step-by-step guides, and scenarios for each subtopic.
```

#### PrivEsc

```
Hello, act as a Cybersecurity expert. Windws and Linux privilege escalation researcher and instructor, with expertise, years of experience, and many advanced certificates, including OSCP and CPTS. You are aware of these exams' expectations and real exam patterns. I'm trying to prepare to OSCP and CPTS myself.

Please, create a huge, detailed, and comprehensive guide to 

Windows named pipe attacks

Not cheatsheet-style, with explanations and exploitation examples for OSCP/CPTS, commands, and resources. Remember the advanced nature of OSCP and CPTS and mention everything for a person to pass successfully - never omit something what may be necessary. The success of the person depends on your guide (assuming they follow it strictly and practice), so don't let them fail. 

Output in MD format (not PDF, not DOCS, etc.).

I have some start with my drafts that explain what Windows named pipes are and mention attacks I'd like to learn. Please take a look at it:


```



```
Hello, act as a Cybersecurity and Windows expert. 
I'm trying to prepare to OSCP and CPTS.
Please, write a huge, very detailed, explanatory guide to Windows enumeration for privilege escalatoin.
Not cheatsheet-style, with explanations and exploitation examples for OSCP/CPTS, commands, and resources. Remember the advanced nature of OSCP and CPTS and mention everything for a person to pass successfully - never omit something what may be necessary. The success of the person depends on your guide (assuming they follow it strictly and practice), so don't let them fail. 
```
## Windows drafts


- Create a new local user:

```PowerShell
New-LocalUser -Name "username" -PasswordNeverExpires -Description "New user account"
```

```CMS
net user username passwd123 /add
```

- Set or change a user password:

```PowerShell
Set-LocalUser -Name "username" -Password (Read-Host -AsSecureString "new_password")
```

```bash
net user username new_password
```

- Enable/disable user account:

```PowerShell
Enable-LocalUser -Name "username"
Disable-LocalUser -Name "username"
```




### How Windows works

Core concepts:
- Windows editions

- User vs. kernel mode [[user_mode_vs._kernel_mode]]
- Users and groups [[Windows_users_and_groups]]

- Authentication and authorization
	- NTLM authentication 
	- Kerberos
	- UAC 
	- Token-based security
	- Access Tokens
	- Password hashes:
		- NTML
		- LM (legacy)
	- Credential storage locations

- Windows architecture:
	- `ntoskrnl.exe`
	- `winlogon.exe`
	- `lsass.exe`
	- `services.exe`
- Windows file system
	- NTFS
	- Special directories: 
		- `C:\Windows`
		- `C:\Windows\System32`
		- `C:\Windows\SysWOW64`
		- `C:\Program Files`
		- `C:\Program Files (x86)`
		- `C:\Users\<user>` 
		- `AppData\Local`, `Roaming`, `Temp`
	- ADS (Alternate Data Streams)
	- File permissions and ownership
	- Inheritance rules

- Permissions and security model
	- Access control
		- ACLs, ACEs, DACLs, SACLs
		- Allow vs. Deny precendence
		- Inheritance and explicit permissions
		- Difference between:
			- NTFS permissions 
			- Share permissions
			- Registry permissions
			- Service permissions
- Tokens and integrity levels
	- Access tokens
	- Primary vs. impersonation tokens
	- Integrity levels
		- Low
		- Medium
		- High
		- System
	- UAC split tokens; UAC

- Windows services and processes
	- Windows services
		- Service states
		- Service accounts 
		- Startup types
		- Service control permissions
	- Processes and DLLs
		- How processes load DLLs
		- Search order for DLL loading
		- Parent/child processes
		- `svchost.exe`
		- `WOW64` (32-bit vs. 64-bit)

- Windows networking basics
	- SMB basics
	- Named pipes
	- Windows firewall basics
	- RDP
	- WinRM
	- Scheduled tasks over network
	- RPC

- Registry
	- Registry structure
		- HKLM
		- HKCU
		- HKCR
		- HKU
		- HKCC
	- Keys vs. values
	- Registry permissions
	- Auto-run locations
	- Service configurations in registry


Native Tools
- `whoami`
- `net user`
- `net localgroup`
- `sc`
- `tasklist`
- `icacls`
- `reg query`
- `wmic`
- `schtasks`
- `powershell`

PowerShell Fundamentals
- Cmdlets
- Pipelines
- Objects vs strings
- Execution policies
- Downloading files
- Script execution bypass basics
- `Get-Process`
- `Get-Service`
- `Get-LocalUser`
- `Get-LocalGroup`
- `Get-Acl`
- `Get-ChildItem`
- `Invoke-WebRequest`
- `Invoke-Command

- Session (session 0 isolation)

- Token-based security model
	- Access tokens
	- Primary vs. impersonation tokens
	- Token privileges (`SeImpersonatePrivilege`, `SeAssignPrimaryTokenPrivilege`)
- Integrity levels:
	- Low
	- Medium
	- High 
	- System
- SIDs
- Object manager (everything is an object)
- Handles and permissions
- Boot process

File system and permissions:
- NTFS
	- Read / Write / Modify / Full Control
	- Explicit vs inherited permissions
	- Effective permissions
	- Ownership
	- Alternate Data Streams (ADS)



Understand:
- Registry keys vs values
- Common auto-run locations
- Service configuration storage
- Stored credentials
- Security descriptors on registry keys

Windows services:
- What they are
- How they start:
	- Automatic
	- Manual
	- Disabled
- Service accounts
- Binary path
- Service permissions


Scheduled tasks:
- Task triggers
- Task actions
- Who owns the task
- Where tasks are stored
- Task execution context

Logs and even system:
- Even Viewer
- Log types:
	- Security 
	- System 
	- Application
- What attackers look for
- What defenders monitor

High-level understanding:
- Defender
- AMSI
- UAC
    
- AppLocker
    
- Windows Firewall


### Windows privilege escalation

- Misconfigured services
- Weak service file permissions
- Weak service registry permissions
- Weak service configuration permissions
- Services running as `SYSTEM` with weak ACLs



