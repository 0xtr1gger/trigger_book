---
created: 2026-07-25
updated: 2026-09-20
tags:
  - AD
status: slop
---
## Authenticated and unauthenticated users

- **Unauthenticated users** have **very limited** access on modern Windows domains.
- **Any authenticated domain user** (even the least privileged one) can read **a surprisingly large amount** of information.
- **Administrative actions** require elevated privileges, but **reading** is intentionally permissive because AD is a directory service.

>[!important] Active Directory is readable by design.

- An authenticated user can typically read **almost every object in the directory**. They can usually enumerate every user and their attributes, groups, computers, OUs, GPOs, etc.
- However, without administrative privileges, an ordinary authenticated user can't *modify* objects, replicate the directory (DCSync), and read *confidential attributes* (e.g., LAPS passwords, BitLocker recovery keys, certain PKI secrets, etc.).
---
- As for anonymous users, they are usually only allowed to query DNS; SMB or LDAP `null` sessions are another option, if permitted. Additionally, some Kerberos operations are possible without credentials (for example, under certain conditions, Kerberos can reveal whether a username exists).
---
- During a penetration test, you'd want **any domain user**, because **one set of valid credentials dramatically expands visibility**. 


| Identity                  | Typical read access                                                              | Typical write access                                                                                          |
| ------------------------- | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| Anonymous                 | Very limited (DNS, some Kerberos interactions, rarely LDAP/SMB if misconfigured) | None                                                                                                          |
| Authenticated domain user | Most directory objects and many attributes                                       | Almost none beyond their own account (e.g., changing their own password or updating permitted profile fields) |
| Domain admin              | Full directory access                                                            | Full control                                                                                                  |

## drafts

The [Microsoft Local Administrator Password Solution (LAPS)](https://www.microsoft.com/en-us/download/details.aspx?id=46899) is used to randomize and rotate local administrator passwords on Windows hosts and prevent lateral movement.

#### LAPS

Accounts can be set up to have their password rotated on a fixed interval (i.e., 12 hours, 24 hours, etc.). This free tool can be beneficial in reducing the impact of an individual compromised host in an AD environment. Organizations should not rely on tools like this alone. Still, when combined with other hardening measures and security best practices, it can be a very effective tool for local administrator account password management.

#### Audit Policy Settings (Logging and Monitoring)

Every organization needs to have logging and monitoring setup to detect and react to unexpected changes or activities that may indicate an attack. Effective logging and monitoring can be used to detect an attacker or unauthorized employee adding a user or computer, modifying an object in AD, changing an account password, accessing a system in an unauthorized or non-standard manner, performing an attack such as password spraying, or more advanced attacks such as modern Kerberos attacks.

#### Group Policy Security Settings

As mentioned earlier in the module, Group Policy Objects (GPOs) are virtual collections of policy settings that can be applied to specific users, groups, and computers at the OU level. These can be used to apply a wide variety of [security policies](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/security-policy-settings) to help harden Active Directory. The following is a non-exhaustive list of the types of security policies that can be applied:

- [Account Policies](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/account-policies) - Manage how user accounts interact with the domain. These include the password policy, account lockout policy, and Kerberos-related settings such as the lifetime of Kerberos tickets
- [Local Policies](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/security-options) - These apply to a specific computer and include the security event audit policy, user rights assignments (user privileges on a host), and specific security settings such as the ability to install drivers, whether the administrator and guest accounts are enabled, renaming the guest and administrator accounts, preventing users from installing printers or using removable media, and a variety of network access and network security controls.
- [Software Restriction Policies](https://docs.microsoft.com/en-us/windows-server/identity/software-restriction-policies/software-restriction-policies) - Settings to control what software can be run on a host.
- [Application Control Policies](https://docs.microsoft.com/en-us/windows/security/threat-protection/windows-defender-application-control/windows-defender-application-control) - Settings to control which applications can be run by certain users/groups. This may include blocking certain users from running all executables, Windows Installer files, scripts, etc. Administrators use [AppLocker](https://docs.microsoft.com/en-us/windows/security/threat-protection/windows-defender-application-control/applocker/applocker-overview) to restrict access to certain types of applications and files. It is not uncommon to see organizations block access to CMD and PowerShell (among other executables) for users that do not require them for their day-to-day job. These policies are imperfect and can often be bypassed but necessary for a defense-in-depth strategy.
- [Advanced Audit Policy Configuration](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/secpol-advanced-security-audit-policy-settings) - A variety of settings that can be adjusted to audit activities such as file access or modification, account logon/logoff, policy changes, privilege usage, and more.

#### Advanced Audit Policy

![Group Policy Management Editor showing Default Domain Policy under Computer Configuration. Advanced Audit Policy Configuration settings are not configured.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/74/adv-audit-pol.png)

#### Update Management (SCCM/WSUS)

Proper patch management is critical for any organization, especially those running Windows/Active Directory systems. The [Windows Server Update Service (WSUS)](https://docs.microsoft.com/en-us/windows-server/administration/windows-server-update-services/get-started/windows-server-update-services-wsus) can be installed as a role on a Windows Server and can be used to minimize the manual task of patching Windows systems. `System Center Configuration Manager` (SCCM) is a paid solution that relies on the WSUS Windows Server role being installed and offers more features than WSUS on its own. A patch management solution can help ensure timely deployment of patches and maximize coverage, making sure that no hosts miss critical security patches. If an organization relies on a manual method for applying patches, it could take a very long time depending on the size of the environment and also could result in systems being missed and left vulnerable.

#### Group Managed Service Accounts (gMSA)

A gMSA is an account managed by the domain that offers a higher level of security than other types of service accounts for use with non-interactive applications, services, processes, and tasks that are run automatically but require credentials to run. They provide automatic password management with a 120 character password generated by the domain controller. The password is changed at a regular interval and does not need to be known by any user. It allows for credentials to be used across multiple hosts.

#### Security Groups

Security groups offer an easy way to assign access to network resources. They can be used to assign specific rights to the group (instead of directly to the user) to determine what members of the group can do within the AD environment. Active Directory automatically creates some [default security groups](https://docs.microsoft.com/en-us/windows/security/identity-protection/access-control/active-directory-security-groups#active-directory-default-security-groups-by-operating-system-version) during installation. Some examples are Account Operators, Administrators, Backup Operators, Domain Admins, and Domain Users. These groups can also be used to assign permission to access resources (i.e., a file share, folder, printer, or a document). Security groups help ensure you can assign granular permissions to users en masse instead of individually managing each user.

#### Built-in AD Security Groups

![Active Directory Users and Computers interface showing security groups under INLANEFREIGHT.LOCAL. Groups include Access Control Assistance Operators, Account Operators, Administrators, and Backup Operators, with descriptions of their permissions.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/74/def-sec-groups.png)

#### Account Separation

Administrators must have two separate accounts. One for their day-to-day work and a second for any administrative tasks they must perform. For example, a user could log into their machine using their `sjones` account to send/receive an email, create documents, etc. They should have a separate account, such as `sjones_adm`, to access a [secure administrative host](https://docs.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/implementing-secure-administrative-hosts) used to perform administrative tasks. This can help ensure that if a user's host is compromised (through a phishing attack, for example), the attacker would be limited to that host and would not obtain credentials for a highly privileged user with considerable access within the domain. It is also essential for the individual to use different passwords for each account to mitigate the risk of password reuse attacks if their non-admin account is compromised.

#### Password Complexity Policies + Passphrases + 2FA

Ideally, an organization should be using passphrases or large randomly generated passwords using an enterprise password manager. The standard 7-8 character passwords can be cracked offline using a tool such as Hashcat very quickly with a GPU password cracking rig. Shorter, less complex passwords may also be guessed through a password spraying attack, giving an attacker a foothold in the domain. Password complexity rules alone in AD are not enough to ensure strong passwords. For example, the password `Welcome1` would meet the standard complexity rules (3 out of 4 of uppercase, lowercase, number, and special character) but would be one of the first passwords I would try in a password spraying attack. An organization should also consider implementing a password filter to disallow passwords containing the months or seasons of the year, the company name, and common words such as `password` and `welcome`. The minimum password length for standard users should be at least 12 characters and ideally longer for administrators/service accounts. Another important security measure is the implementation of multi-factor authentication (MFA) for Remote Desktop Access to any host. This can help to limit lateral movement attempts that may rely on GUI access to a host.

#### Limiting Domain Admin Account Usage

All-powerful Domain Admin accounts should only be used to log in to Domain Controllers, not personal workstations, jump hosts, web servers, etc. This can significantly reduce the impact of an attack and cut down potential attack paths should a host be compromised. This would ensure that Domain Admin account passwords are not left in memory on hosts throughout the environment.

#### Periodically Auditing and Removing Stale Users and Objects

It is important for an organization to periodically audit Active Directory and remove or disable any unused accounts. For example, there may be a privileged service account that was created eight years ago with a very weak password that was never changed, and the account is no longer in use. Even if the password policy had since been changed to be more resistant to attacks such as password spraying, an account such as this may be a quick and easy foothold or method for lateral movement or privilege escalation within the domain.

#### Auditing Permissions and Access

Organizations should also periodically perform access control audits to ensure that users only have the level of access required for their day-to-day work. It is important to audit local admin rights, the number of Domain Admins (do we really need 30 of them?), and Enterprise Admins to limit the attack surface, file share access, user rights (i.e., membership in certain privileged security groups), and more.

#### Audit Policies & Logging

Visibility into the domain is a must. An organization can achieve this through robust logging and then using rules to detect anomalous activity (such as many failed login attempts that could be indicative of a password spraying attack) or indicators that a Kerberoasting attack is being attempted. These can also be used to detect Active Directory enumeration. It is worth familiarizing ourselves with Microsoft's [Audit Policy Recommendations](https://docs.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/audit-policy-recommendations) to help detect compromise.

#### Using Restricted Groups

[Restricted Groups](https://social.technet.microsoft.com/wiki/contents/articles/20402.active-directory-group-policy-restricted-groups.aspx) allow for administrators to configure group membership via Group Policy. They can be used for a number of reasons, such as controlling membership in the local administrator's group on all hosts in the domain by restricting it to just the local Administrator account and Domain Admins and controlling membership in the highly privileged Enterprise Admins and Schema Admins groups and other key administrative groups.

#### Limiting Server Roles

It is important not to install additional roles on sensitive hosts, such as installing the `Internet Information Server` (IIS) role on a Domain Controller. This would increase the attack surface of the Domain Controller, and this type of role should be installed on a separate standalone web server. Some other examples would be not hosting web applications on an Exchange mail server and separating web servers and database servers out to different hosts. This type of role separation can help to reduce the impact of a successful attack.

#### Limiting Local Admin and RDP Rights

Organizations should tightly control which users have local admin rights on which computers. As stated above, this can be achieved using Restricted Groups. I have seen too many organizations with the entire Domain Users group with local admin rights on one or more hosts. This would allow an attacker that compromises `ANY` account (even a very low privileged one) to access that host as a local admin and potentially obtain sensitive data or steal high privileged domain account credentials from memory if another user is logged in. The same goes for Remote Desktop (RDP) rights. If many users can RDP to one or many machines, this increases the risk of sensitive data exposure or potential privilege escalation attacks, leading to further compromise.

This [link](https://docs.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/best-practices-for-securing-active-directory) provides further reading on Microsoft's Best Practices for Securing Active Directory.


## `Bloodhound.py`

Once we have domain credentials, we can run the [BloodHound.py](https://github.com/fox-it/BloodHound.py) BloodHound ingestor from our Linux attack host. BloodHound is one of, if not the most impactful tools ever released for auditing Active Directory security, and it is hugely beneficial for us as penetration testers. We can take large amounts of data that would be time-consuming to sift through and create graphical representations or "attack paths" of where access with a particular user may lead. We will often find nuanced flaws in an AD environment that would have been missed without the ability to run queries with the BloodHound GUI tool and visualize issues. The tool uses [graph theory](https://en.wikipedia.org/wiki/Graph_theory) to visually represent relationships and uncover attack paths that would have been difficult, or even impossible to detect with other tools. The tool consists of two parts: the [SharpHound collector](https://github.com/BloodHoundAD/BloodHound/tree/master/Collectors) written in C# for use on Windows systems, or for this section, the BloodHound.py collector (also referred to as an `ingestor`) and the [BloodHound](https://github.com/BloodHoundAD/BloodHound/releases) GUI tool which allows us to upload collected data in the form of JSON files. Once uploaded, we can run various pre-built queries or write custom queries using [Cypher language](https://specterops.io/blog/2017/09/18/bloodhound-intro-to-cypher/). The tool collects data from AD such as users, groups, computers, group membership, GPOs, ACLs, domain trusts, local admin access, user sessions, computer and user properties, RDP access, WinRM access, etc.

It was initially only released with a PowerShell collector, so it had to be run from a Windows host. Eventually, a Python port (which requires Impacket, `ldap3`, and `dnspython`) was released by a community member. This helped immensely during penetration tests when we have valid domain credentials, but do not have rights to access a domain-joined Windows host or do not have a Windows attack host to run the SharpHound collector from. This also helps us not have to run the collector from a domain host, which could potentially be blocked or set off alerts (though even running it from our attack host will most likely set off alarms in well-protected environments).

Running `bloodhound-python -h` from our Linux attack host will show us the options available.

#### BloodHound.py Options

        shellsession
`0xtr1gger@htb[/htb]$ bloodhound-python -h usage: bloodhound-python [-h] [-c COLLECTIONMETHOD] [-u USERNAME]                          [-p PASSWORD] [-k] [--hashes HASHES] [-ns NAMESERVER]                         [--dns-tcp] [--dns-timeout DNS_TIMEOUT] [-d DOMAIN]                         [-dc HOST] [-gc HOST] [-w WORKERS] [-v]                         [--disable-pooling] [--disable-autogc] [--zip] Python based ingestor for BloodHound For help or reporting issues, visit https://github.com/Fox-IT/BloodHound.py optional arguments:   -h, --help            show this help message and exit  -c COLLECTIONMETHOD, --collectionmethod COLLECTIONMETHOD                        Which information to collect. Supported: Group,                        LocalAdmin, Session, Trusts, Default (all previous),                        DCOnly (no computer connections), DCOM, RDP,PSRemote,                        LoggedOn, ObjectProps, ACL, All (all except LoggedOn).                        You can specify more than one by separating them with                        a comma. (default: Default)  -u USERNAME, --username USERNAME                        Username. Format: username[@domain]; If the domain is                        unspecified, the current domain is used.  -p PASSWORD, --password PASSWORD                        Password   <SNIP>`

As we can see the tool accepts various collection methods with the `-c` or `--collectionmethod` flag. We can retrieve specific data such as user sessions, users and groups, object properties, ACLS, or select `all` to gather as much data as possible. Let's run it this way.

#### Executing BloodHound.py

        shellsession
`0xtr1gger@htb[/htb]$ sudo bloodhound-python -u 'forend' -p 'Klmcargo2' -ns 172.16.5.5 -d inlanefreight.local -c all  INFO: Found AD domain: inlanefreight.local INFO: Connecting to LDAP server: ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL INFO: Found 1 domains INFO: Found 2 domains in the forest INFO: Found 564 computers INFO: Connecting to LDAP server: ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL INFO: Found 2951 users INFO: Connecting to GC LDAP server: ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL INFO: Found 183 groups INFO: Found 2 trusts INFO: Starting computer enumeration with 10 workers <SNIP>`

The command above executed Bloodhound.py with the user `forend`. We specified our nameserver as the Domain Controller with the `-ns` flag and the domain, INLANEFREIGHt.LOCAL with the `-d` flag. The `-c all` flag told the tool to run all checks. Once the script finishes, we will see the output files in the current working directory in the format of <date_object.json>.

#### Viewing the Results

        shellsession
`0xtr1gger@htb[/htb]$ ls 20220307163102_computers.json  20220307163102_domains.json  20220307163102_groups.json  20220307163102_users.json`

#### Upload the Zip File into the BloodHound GUI

We could then type `sudo neo4j start` to start the [neo4j](https://neo4j.com/) service, firing up the database we'll load the data into and also run Cypher queries against.

Next, we can type `bloodhound` from our Linux attack host when logged in using `freerdp` to start the BloodHound GUI application and upload the data. The credentials are pre-populated on the Linux attack host, but if for some reason a credential prompt is shown, use:

- `user == neo4j` / `pass == HTB_@cademy_stdnt!`.

Once all of the above is done, we should have the BloodHound GUI tool loaded with a blank slate. Now we need to upload the data. We can either upload each JSON file one by one or zip them first with a command such as `zip -r ilfreight_bh.zip *.json` and upload the Zip file. We do this by clicking the `Upload Data` button on the right side of the window (green arrow). When the file browser window pops up to select a file, choose the zip file (or each JSON file) (red arrow) and hit `Open`.

#### Uploading the Zip File

![BloodHound interface showing database info and file selection for 'BloodHound.zip' in Downloads folder.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/bh-injest.png)

Now that the data is loaded, we can use the Analysis tab to run queries against the database. These queries can be custom and specific to what you decide using [custom Cypher queries](https://hausec.com/2019/09/09/bloodhound-cypher-cheatsheet/). There are many great cheat sheets to help us here. We will discuss custom Cypher queries more in a later section. As seen below, we can use the built-in `Path Finding` queries on the `Analysis tab` on the `Left` side of the window.

#### Searching for Relationships

![BloodHound interface displaying pre-built analytics queries and a graph of Active Directory relationships.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/bh-analysis.png)

The query chosen to produce the map above was `Find Shortest Paths To Domain Admins`. It will give us any logical paths it finds through users/groups/hosts/ACLs/GPOs, etc., relationships that will likely allow us to escalate to Domain Administrator privileges or equivalent. This will be extremely helpful when planning our next steps for lateral movement through the network. Take some time to experiment with the various features: look at the `Database Info` tab after uploading data, search for a node such as `Domain Users` and, scroll through all of the options under the `Node Info` tab, check out the pre-built queries under the `Analysis` tab, many which are powerful and can quickly find various ways to domain takeover. Finally, experiment with some custom Cypher queries by selecting some interesting ones from the Cypher cheatsheet linked above, pasting them into the `Raw Query` box at the bottom, and hitting enter. You can also play with the `Settings` menu by clicking the gear icon on the right side of the screen and adjusting how nodes and edges are displayed, enable query debug mode, and enable dark mode. Throughout the remainder of this module, we will use BloodHound in various ways, but for a dedicated study on the BloodHound tool, check out the [Active Directory BloodHound](https://academy.hackthebox.com/course/preview/active-directory-bloodhound) module.

In the next section, we will cover running the SharpHound collector from a domain-joined Windows host and work through some examples of working with the data in the BloodHound GUI.

---

We experimented with several new tools for domain enumeration from a Linux host. The following section will cover several more tools we can use from a domain-joined Windows host. As a quick note, if you haven't checked out the [WADComs project](https://wadcoms.github.io/) yet, you definitely should. It is an interactive cheat sheet for many of the tools we will cover (and more) in this module. It's hugely helpful when you can't remember exact command syntax or are trying out a tool for the first time. Worth bookmarking and even [contributing](https://wadcoms.github.io/contribute/) to!

Now, let's switch gears and start digging into the INLANEFREIGHT.LOCAL domain from our Windows attack host.