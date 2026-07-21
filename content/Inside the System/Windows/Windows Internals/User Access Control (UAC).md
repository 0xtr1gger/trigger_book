---
created: 2026-07-23
tags:
  - Windows
status: substantial
---
## UAC

>**[UAC (User Access Control)](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/user-account-control/how-it-works)** is a security feature designed to **limit application software to standard user privileges** until an administrator explicitly authorizes an elevation.

- UAC was introduced to limit the ability of malicious code to execute with administrator privileges and mitigate the potential impact. 

- By default, even when a user with administrative rights is logged in, their applications execute in the context of a standard user. 
- When an application requires administrative rights, UAC intercepts the request and triggers a prompt, asking for explicit consent or credentials (based on the user's role and system configuration).

>[!important] Microsoft officially defines UAC as an **integrity boundary**, not a strict security boundary; UAC does it restrict unauthorized changes, but it's not designed to be an impenetrable defense mechanism against local attackers who have already gained code execution.

>[!bug] See [[🛠️ UAC bypasses]].

## The sign-in process and access token

- When a user authenticates to a Windows system, the LSASS (Local Security Authority Subsystem Service) generates an access token for that session. This token contains the user's SID and their associated privileges.  

>[!note] See [[🛠️ Access tokens and impersonation]].

- For a regular user, only a single standard token is created. 
- However, when an administrator logs in (or a member of the `Administrators` group), two distinct tokens are created:
	1. **Standard user access token** — contains the same user-specific information as the administrator token, but with administrative privileges and SIDs removed.
	2. **Administrator access token** — retains all administrative privileges; remains dormant until an application explicitly requests elevation and the user passes the UAC prompt.

- The standard user access token is used to start the `explorer.exe` process (the Windows shell). Because child processes inherit the token of their parent, all user-initiated applications run under this filtered context by default.

>[!important] This split-token configuration is called the Admin Approval Mode (AAM).
>The ***default*** configuration is as follows: 
> - For the built-in `Administrator` user (RID `500`), the Admin Approval Mode is **disabled**, meaning all applications this user starts run with full administrative privileges.
> - For the members of the `Adminsitrators` group, the elevation prompt **appears only when a non-Microsoft application requires elevation**. 
>
>This behavior varies across systems depending on the configuration. See [`User Account Control settings and configuration — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/user-account-control/settings-and-configuration?tabs=intune).

## Integrity levels

- Windows protects processes from one another using **Integrity Levels** — they act as a measurement of tryst.
- Applications with lower integrity levels are strictly prevented fro modifying the memory, data, or processes of applications with higher integrity levels:
	- **Low Integrity** — sandboxed applications that interact with untrusted content (e.g., web browsers); prevents a compromise from spreading to the broader system if exploited.
	- **Medium Integrity** — the default execution context for most standard user applications (e.g., standard applications spawned by `explorer.exe`).
	- **High Integrity** — applications performing tasks that modify system data; requires a full administrator token (e.g., Disk Management, Registry Editor, elevated command prompts).
	- **System Integrity** — reserved for core OS services and components (`SYSTEM` account).
- For a parent process to successfully spawn a child process *without* triggering a UAC elevation prompt, both processes must operate at the **same integrity level**.
## The UAC user experience

- UAC behaves differently depending on the user's group membership. 
- When an application requests to run with elevated privileges (requiring the full administrator token), Windows analyzes the executable and triggers one of two types of prompts:
	- **Consent prompt** — presented when an administrator (operating in Admin Approval Mode) attempts an action that requires elevation.
		- The user is asked to confirm (`Yes` or `No`) if they want to allow the application to make changes to the device. 
		- By default, it does not require a password (`Prompt for credentials` can be configured to require explicit credentials).
	- **Credential prompt** — presented when a standard user attempts an action that requires administrative rights.
		- A standard user can't authorize the change themselves.
		- The prompt explicitly requires to input valid credentials for an account that belongs to the local `Administrators` group.


- To help users identify potential security risks, UAC prompts are color-coded based on the publisher of the executable:
	- **Gray Background**: The application is a built-in Windows administrative tool (like a Control Panel applet) or is signed by a verified, trusted publisher.
	- **Yellow Background**: The application is unsigned, or signed but not inherently trusted by the system.

- Additionally, standard Windows UI elements (like buttons in the Control Panel) display a small **shield icon** if interacting with them requires an elevation of privilege (e.g., changing the system time requires elevation, while viewing the clock does not).

## The Secure Desktop

- To protect against automated UI manipulation, UAC elevation prompts (both consent and credential) are directed to the **Secure Desktop** by default.

>**Windows Secure Desktop** is a protected, isolated desktop environment used by the operating system to display sensitive prompts, such as the UAC elevation requests and the `Ctrl+Alt+Del` sign-in screen.

- When an executable requests elevation, Windows suspends the interactive user desktop and switches to the Secure Desktop. This environment dims the background and exclusively displays the UAC prompt.
- Only `SYSTEM` processes can access the Secure Desktop. This prevents malware running on the user's interactive desktop from programmatically clicking `Yes` on the consent prompt (shatter attacks) or spoofing the UI to harvest credentials.
- The desktop switches back to the user's interactive session only after the prompt is explicitly answered or dismissed.

>[!note] While malware could theoretically present a fake secure desktop on the interactive desktop, this requires the malware to already be running on the system. Additionally/ because it can't programmatically interact with the _real_ secure desktop, the actual elevation can't be forced without user interaction.

## UAC Group Policy settings

There are 10 Group Policy settings that can be set for UAC:

| Group Policy Setting                                                                                                                                                                                                                                                                                                                                                           | Registry key                  | Default setting                                              |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------- | ------------------------------------------------------------ |
| [User Account Control: Admin Approval Mode for the built-in Administrator account](https://docs.microsoft.com/en-us/windows/security/identity-protection/user-account-control/user-account-control-group-policy-and-registry-key-settings#user-account-control-admin-approval-mode-for-the-built-in-administrator-account)                                                     | `FilterAdministratorToken`    | Disabled                                                     |
| [User Account Control: Allow UIAccess applications to prompt for elevation without using the secure desktop](https://docs.microsoft.com/en-us/windows/security/identity-protection/user-account-control/user-account-control-group-policy-and-registry-key-settings#user-account-control-allow-uiaccess-applications-to-prompt-for-elevation-without-using-the-secure-desktop) | `EnableUIADesktopToggle`      | Disabled                                                     |
| [User Account Control: Behavior of the elevation prompt for administrators in Admin Approval Mode](https://docs.microsoft.com/en-us/windows/security/identity-protection/user-account-control/user-account-control-group-policy-and-registry-key-settings#user-account-control-behavior-of-the-elevation-prompt-for-administrators-in-admin-approval-mode)                     | `ConsentPromptBehaviorAdmin`  | Prompt for consent for non-Windows binaries                  |
| [User Account Control: Behavior of the elevation prompt for standard users](https://docs.microsoft.com/en-us/windows/security/identity-protection/user-account-control/user-account-control-group-policy-and-registry-key-settings#user-account-control-behavior-of-the-elevation-prompt-for-standard-users)                                                                   | `ConsentPromptBehaviorUser`   | Prompt for credentials on the secure desktop                 |
| [User Account Control: Detect application installations and prompt for elevation](https://docs.microsoft.com/en-us/windows/security/identity-protection/user-account-control/user-account-control-group-policy-and-registry-key-settings#user-account-control-detect-application-installations-and-prompt-for-elevation)                                                       | `EnableInstallerDetection`    | Enabled (default for home) Disabled (default for enterprise) |
| [User Account Control: Only elevate executables that are signed and validated](https://docs.microsoft.com/en-us/windows/security/identity-protection/user-account-control/user-account-control-group-policy-and-registry-key-settings#user-account-control-only-elevate-executables-that-are-signed-and-validated)                                                             | `ValidateAdminCodeSignatures` | Disabled                                                     |
| [User Account Control: Only elevate UIAccess applications that are installed in secure locations](https://docs.microsoft.com/en-us/windows/security/identity-protection/user-account-control/user-account-control-group-policy-and-registry-key-settings#user-account-control-only-elevate-uiaccess-applications-that-are-installed-in-secure-locations)                       | `EnableSecureUIAPaths`        | Enabled                                                      |
| [User Account Control: Run all administrators in Admin Approval Mode](https://docs.microsoft.com/en-us/windows/security/identity-protection/user-account-control/user-account-control-group-policy-and-registry-key-settings#user-account-control-run-all-administrators-in-admin-approval-mode)                                                                               | `EnableLUA`                   | Enabled                                                      |
| [User Account Control: Switch to the secure desktop when prompting for elevation](https://docs.microsoft.com/en-us/windows/security/identity-protection/user-account-control/user-account-control-group-policy-and-registry-key-settings#user-account-control-switch-to-the-secure-desktop-when-prompting-for-elevation)                                                       | `PromptOnSecureDesktop`       | Enabled                                                      |
| [User Account Control: Virtualize file and registry write failures to per-user locations](https://docs.microsoft.com/en-us/windows/security/identity-protection/user-account-control/user-account-control-group-policy-and-registry-key-settings#user-account-control-virtualize-file-and-registry-write-failures-to-per-user-locations)                                       | `EnableVirtualization`        | Enabled                                                      |

>[!note] See [`User Account Control settings and configuration — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/user-account-control/settings-and-configuration?tabs=intune).

## References and further reading

- [`User Account Control overview — Microsfot Learn`](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/user-account-control/)
- [`How User Account Control works — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/user-account-control/how-it-works)
- [`User Account Control settings and configuration — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/user-account-control/settings-and-configuration?tabs=intune)
- [`User Account Control: Behavior of the elevation prompt for administrators in Admin Approval Mode`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/user-account-control-behavior-of-the-elevation-prompt-for-administrators-in-admin-approval-mode)

>[!important] Microsoft officially states that UAC is an integrity boundary —  not a security boundary.