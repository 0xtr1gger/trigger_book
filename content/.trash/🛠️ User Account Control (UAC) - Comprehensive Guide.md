---
created: 2026-07-23
---

# 🛠️ User Account Control (UAC) - Comprehensive Guide

## 📌 Overview

**User Account Control (UAC)** is a core Windows security component designed to mitigate the impact of malicious software. It achieves this by restricting applications to standard user privileges until an administrator explicitly authorizes an elevation of privilege. 



By default, even when a user with administrative rights is logged in, their applications execute in the security context of a standard user. When an application or task requires administrative rights, UAC intercepts the request and triggers a prompt, asking for explicit consent or credentials based on the user's role and system configuration.

## ⚙️ Core Mechanics: How UAC Works

### The Sign-in Process and Access Tokens

When a user authenticates to a Windows system, the Local Security Authority Subsystem Service (`LSASS`) generates an **access token** for that session. This token contains the user's Security Identifiers (SIDs) and their associated Windows privileges.

For a standard user, only a single standard token is created. However, when a member of the local **Administrators** group logs in, UAC ensures two distinct tokens are generated:
1. **Filtered (Standard User) Token:** This token contains the same user-specific information as the full token, but administrative Windows privileges and powerful SIDs (like the local Administrators group SID) are removed or designated for "deny-only" use. It is used to start the `explorer.exe` process (the Windows shell). Because child processes inherit the token of their parent, all user-initiated applications inherently run under this filtered context.
2. **Full Administrator Token:** This token retains all administrative privileges. It remains dormant until an application explicitly requests elevation and the user successfully passes the UAC prompt.

### Integrity Levels (ILs)

Windows protects processes from one another using **Integrity Levels**, which act as a measurement of trust. Applications with lower integrity levels are strictly prevented from modifying the memory, data, or processes of applications with higher integrity levels.

- **Low Integrity:** Sandboxed applications that interact with untrusted content (e.g., web browsers) operate here to prevent them from compromising the broader system if exploited.
- **Medium Integrity:** The default execution context for most standard user applications (e.g., standard applications spawned by `explorer.exe`).
- **High Integrity:** Applications performing tasks that modify system data, which require a full administrator token (e.g., Disk Management, Registry Editor, elevated command prompts).
- **System Integrity:** Reserved for core OS services and components (`SYSTEM` account).

For a parent process to successfully spawn a child process without triggering a UAC elevation prompt, both processes must operate at the **same integrity level**.

## 🛡️ The UAC User Experience

UAC behaves differently depending on the user's group membership. When an application requests to run with elevated privileges (requiring the full administrator token), Windows analyzes the executable and triggers one of two types of prompts:

### 1. The Consent Prompt
Presented when an administrator (operating in **Admin Approval Mode**) attempts an action requiring elevation. 
- The user is simply asked to confirm (click "Yes" or "No") if they want to allow the application to make changes to the device.
- By default, it does not require a password. However, in high-security environments, administrators can configure the Local Security Policy (`User Account Control: Behavior of the elevation prompt for administrators in Admin Approval Mode`) to require explicit credentials (**Prompt for credentials**).

### 2. The Credential Prompt
Presented when a standard user attempts an action requiring administrative rights.
- A standard user cannot authorize the change themselves.
- The prompt explicitly requires the input of valid credentials for an account that belongs to the local Administrators group.

### Elevation Prompt Visual Cues
To help users identify potential security risks, UAC prompts are color-coded based on the publisher of the executable:
- **Gray Background:** The application is a built-in Windows administrative tool (like a Control Panel applet) or is signed by a verified, trusted publisher.
- **Yellow Background:** The application is unsigned, or signed but not inherently trusted by the system.

Additionally, standard Windows UI elements (like buttons in the Control Panel) display a small **Shield Icon** if interacting with them requires an elevation of privilege (e.g., changing the system time requires elevation, while viewing the clock does not).

## 🔒 The Secure Desktop

To protect against automated UI manipulation, UAC elevation prompts (both consent and credential) are directed to the **Secure Desktop** by default.

When an executable requests elevation, Windows suspends the interactive user desktop and switches to the Secure Desktop. This environment dims the background and exclusively displays the UAC prompt. 
- **Security Benefit:** Only `SYSTEM` processes can access the Secure Desktop. This prevents malware running on the user's interactive desktop from programmatically clicking "Yes" on the consent prompt (shatter attacks) or spoofing the UI to harvest credentials.
- The desktop switches back to the user's interactive session only after the prompt is explicitly answered or dismissed.
- *Note:* While malware could theoretically present a fake secure desktop on the interactive desktop, this requires the malware to already be running on the system. Furthermore, because it cannot programmatically interact with the *real* secure desktop, the actual elevation cannot be forced without user interaction.

## 🔗 References & Further Reading

- [`User Account Control overview — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/user-account-control/)
- [`How User Account Control works — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/user-account-control/how-it-works)
- [`User Account Control settings and configuration — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/user-account-control/settings-and-configuration)
