---
created: 2026-09-16
updated: 2026-10-04
tags:
  - Windows
  - Windows_PrivEsc
  - methodology
status: substantial
---
>[!abstract]+ **Scope**: decision tree and methodology for local Windows privilege escalation.


>- Start with [[Manual & automated Windows enumeration]] before you test any exploit.
>- Use the decision tree below to match your `whoami /priv`, group membership, service, task, registry, credential, or patch findings to the correct exploit note.
>- Treat [[🛠️ Windows kernel exploits]] as a last resort after misconfigurations and credentials are exhausted.

## Start here

- [ ] Break out of a restricted desktop first if you have no shell, then enumerate.
- [ ] Run the initial triage from [[Manual & automated Windows enumeration]] (`whoami /all`, OS build, Defender, network, services).
- [ ] Hunt passively for credentials before you run noisy exploits.
- [ ] Check token privileges, group memberships, services, scheduled tasks, autoruns, registry flags, UAC context, and patch level in that order.
- [ ] Pick one decision-tree branch, confirm the misconfiguration, exploit it, then re-enumerate as the new user.

>[!tip]+ Minimum first commands when you land on a host.
>- Identity, privileges, OS build, Defender status, and listening ports shape every later branch.
>- Full command reference lives in [[Manual & automated Windows enumeration]].

```powershell
whoami /all
```

```powershell
systeminfo
```

```powershell
Get-MpComputerStatus
```

```powershell
Get-Service | Where-Object Status -eq 'Running'
```

## Decision tree

- [ ] Match one row at a time and follow only the linked note for that condition.
- [ ] Re-run `whoami /all` after each escalation step since group SIDs and privileges change with the new token.

| Signal you observe                                                                                                                                                       | Confirmation step                                                                                                                           | Go to                                      |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| No Explorer, no `cmd.exe`, single published app, kiosk, or Citrix/RDS desktop                                                                                            | Try file dialog, Help link, print dialog, or accessibility binary to reach a shell                                                          | Citrix breakout                            |
| `whoami /priv` shows `SeImpersonatePrivilege` or `SeAssignPrimaryTokenPrivilege`                                                                                         | Confirm service account context and OS build with [[Manual & automated Windows enumeration]], then check spooler, RPC, and port `135` state | [[Potato attacks]]                         |
| `whoami /priv` shows other powerful privileges                                                                                                                           | Confirm privilege state (present versus enabled) with `whoami /priv`                                                                        | See privilege rows below                   |
| `SeBackupPrivilege` or `SeRestorePrivilege` is present                                                                                                                   | Confirm with [[Manual & automated Windows enumeration]] user and group checks                                                               | [[SeBackupPrivilege & SeRestorePrivilege]] |
| `SeDebugPrivilege` is present                                                                                                                                            | Confirm a `SYSTEM` process is reachable for token duplication or injection                                                                  | [[SeDebugPrivilege]]                       |
| `SeTakeOwnershipPrivilege` is present                                                                                                                                    | Confirm you can reach a protected credential store or `SYSTEM` binary path                                                                  | [[SeTakeOwnershipPrivilege]]               |
| `SeLoadDriverPrivilege` is present                                                                                                                                       | Confirm driver load path and signing policy before BYOVD work                                                                               | [[SeLoadDriverPrivilege]]                  |
| `whoami /group` shows `Backup Operators`, `Server Operators`, `DnsAdmins`, `Print Operators`, `Account Operators`, `Hyper-V Administrators`, or remote management groups | Confirm exact membership with `net localgroup` per [[Manual & automated Windows enumeration]]                                               | See privileged group rows below            |
| Service runs as `SYSTEM` with a weak DACL, writable binary, writable folder, or writable registry key                                                                    | Audit service account, `PathName`, binary ACLs, and registry ACLs per [[Manual & automated Windows enumeration]]                            | [[Weak service DACLs]]                     |
| Service `PathName` has spaces and no quotes                                                                                                                              | Enumerate unquoted paths and test candidate directories for write access                                                                    | [[Unquoted service paths]]                 |
| Service registry key under `HKLM\SYSTEM\CurrentControlSet\Services` is writable                                                                                          | Check key ACLs with `Get-Acl` and `accesschk.exe`                                                                                           | [[Service registry key misconfigurations]] |
| Privileged process loads a DLL from a writable directory or a missing path exists                                                                                        | Filter ProcMon `NAME NOT FOUND` DLL loads and check search order                                                                            | [[DLL hijacking]]                          |
| Scheduled task, `Run` key, `Startup` folder, Winlogon value, PowerShell profile, or WMI subscription runs as a privileged account                                        | Audit task principal, autorun value, binary ACLs, and trigger conditions                                                                    | [[🛠️ Auto-start extensibility points]]    |
| `HKLM` and `HKCU` `AlwaysInstallElevated` values are both `1`                                                                                                            | Query both hives per the registry section of [[Manual & automated Windows enumeration]]                                                     | [[AlwaysInstallElevated]]                  |
| Plaintext password, hash, ticket, key, token, or database credential appears in files, history, registry, shares, or memory                                              | Start passive, then move to hive, LSASS, vault, DPAPI, and GPP notes as findings dictate                                                    | [[🛠️ Windows credential hunting]]         |
| You are a local administrator with a filtered medium-integrity token                                                                                                     | Confirm integrity level, UAC policy, and auto-elevating binary availability                                                                 | UAC bypasses                               |
| No misconfiguration or credential path works and the build is missing patches                                                                                            | Audit build, UBR, hotfixes, mitigations, and drivers before you run any exploit                                                             | [[🛠️ Windows kernel exploits]]            |
| You need token theory before you pick impersonation, Potato, or debug paths                                                                                              | Read token types, impersonation levels, and privilege semantics                                                                             | [[Access tokens and impersonation]]        |

## Privilege fast lane

- [ ] Run `whoami /priv` first since one enabled privilege often beats long service audits.
- [ ] Read [[Access tokens and impersonation]] if impersonation, delegation, or primary token behavior is unclear.
- [ ] Match the privilege to one exploit note and avoid mixing unrelated privilege techniques in one attempt.

- **Impersonation privileges:** `SeImpersonatePrivilege` or `SeAssignPrimaryTokenPrivilege` point to [[Potato attacks]] and its children [[🛠️ JuicyPotato]], [[PrintSpoofer]], [[RoguePotato]], [[🛠️ SweetPotato]], [[GodPotato]], and [[LocalPotato & EfxPotato]].
- **Backup and restore:** `SeBackupPrivilege` and `SeRestorePrivilege` point to [[SeBackupPrivilege & SeRestorePrivilege]] and to [[Backup Operators]] when group membership grants them.
- **Debug:** `SeDebugPrivilege` points to [[SeDebugPrivilege]] for token duplication, injection, PPID spoofing, and LSASS access.
- **Ownership:** `SeTakeOwnershipPrivilege` points to [[SeTakeOwnershipPrivilege]] for ownership seizure plus ACL rewrite on protected files and binaries.
- **Driver load:** `SeLoadDriverPrivilege` points to [[SeLoadDriverPrivilege]] for signed-driver load and BYOVD paths.

## Privileged group fast lane

- [ ] Run `whoami /group` and `net localgroup` checks from [[Manual & automated Windows enumeration]] before you trust a group-based path.
- [ ] Treat group membership as a pointer to privileges, file access, service control, or credential access rather than as instant administrator access.

- **Backup path:** membership in `Backup Operators` points to [[Backup Operators]] and to [[SeBackupPrivilege & SeRestorePrivilege]].
- **Service and server control:** membership in `Server Operators` points to [[Server Operators]].
- **DNS control:** membership in `DnsAdmins` points to [[DnsAdmins]].
- **Print path:** membership in `Print Operators` points to [[Print Operators]].
- **Account control:** membership in `Account Operators` points to [[Account Operators]].
- **Virtualization path:** membership in `Hyper-V Administrators` points to [[Hyper-V Administrators]].
- **Remote management:** WinRM or RDP operator rights point to [[WinRM-RDP Operators]].
- **Log access:** log reader rights point to [[Event Log Readers]] for credential and operational data in event logs.

## Service, autorun and registry fast lane

- [ ] Enumerate services, tasks, autoruns, and registry values with [[Manual & automated Windows enumeration]] before you change any binary, path, or key.
- [ ] Confirm the service account, trigger, and writable path since a writable file under a user-level service is not privilege escalation.

- **Service DACL and binary ACL:** weak service permissions point to [[Weak service DACLs]].
- **Service registry key:** writable `ImagePath` or key ACL points to [[Service registry key misconfigurations]].
- **Path parsing:** spaces without quotes point to [[Unquoted service paths]].
- **Library load:** missing or hijackable DLL in a privileged process points to [[DLL hijacking]].
- **Scheduled and automatic execution:** privileged tasks, `Run` keys, `Startup` folders, Winlogon, profiles, and WMI subscriptions point to [[🛠️ Auto-start extensibility points]].
- **Installer policy:** dual-hive `AlwaysInstallElevated` flag points to [[AlwaysInstallElevated]].

## Credential fast lane

- [ ] Start with [[🛠️ Windows credential hunting]] since it orders passive file, history, registry, share, and vault checks before noisy memory and hive dumps.
- [ ] Move to a focused note only after you find the credential store type.

- **General hunting order:** configuration files, shell history, registry values, vaults, databases, shares, and memory per [[🛠️ Windows credential hunting]].
- **Local hashes:** `SAM`, `SYSTEM`, and `SECURITY` access points to [[Dumping Windows registry hives]].
- **Memory:** logged-on user secrets point to [[Dumping LSASS memory]].
- **Policy secrets:** domain-pushed secrets point to 
- **Stored vaults:** saved Windows credentials point to [[🛠️ Credential Manager]].
- **Protected blobs:** DPAPI-protected secrets point to [[🛠️ DPAPI credentials]].
- **Registry and LSA:** AutoLogon, LSA secrets, and stored registry passwords point to [[🛠️ Dumping LSA secrets]].

## UAC, restricted and kernel fast lane

- [ ] Confirm you actually need the heavy path since UAC, breakout, and kernel exploits have stricter preconditions than service or credential paths.
- [ ] Record OS build, UBR, hotfixes, mitigations, and EDR state with [[Manual & automated Windows enumeration]] before kernel work.

- **Filtered administrator:** medium integrity plus local administrator membership points to [[🛠️ UAC bypasses]].
- **No shell:** published app, kiosk, RDS, or Citrix session points to [[🛠️  Citrix breakout]] first, then back to enumeration.
- **Missing patch:** old build, absent KB, weak third-party driver, or disabled mitigation points to [[🛠️ Windows kernel exploits]] as a last resort.

## Exploitation order

- [ ] Work from quiet and deterministic checks toward noisy and unstable exploits.
- [ ] Stop and re-enumerate after each new credential or higher-integrity shell.

- **Step 1 — Escape and enumerate:** break out with [[🛠️  Citrix breakout]] if needed, then run full [[Manual & automated Windows enumeration]] triage.
- **Step 2 — Hunt credentials passively:** run [[🛠️ Windows credential hunting]] checks for files, history, registry, shares, vaults, and policy secrets.
- **Step 3 — Use tokens and groups:** test [[Access tokens and impersonation]], [[Potato attacks]], privilege notes, and privileged group notes against `whoami /priv` and `whoami /group` output.
- **Step 4 — Abuse execution paths:** test [[Weak service DACLs]], [[Unquoted service paths]], [[Service registry key misconfigurations]], [[DLL hijacking]], [[🛠️ Auto-start extensibility points]], and [[AlwaysInstallElevated]].
- **Step 5 — Bypass UAC if administration is filtered:** use [[🛠️ UAC bypasses]] only after you confirm medium integrity and local administrator context.
- **Step 6 — Test kernel exploits last:** use [[🛠️ Windows kernel exploits]] after misconfigurations, credentials, and UAC paths are exhausted.

## Folder map

- [ ] Use this map when you know the folder but not the exact note title.

| Area | Notes |
|---|---|
| Enumeration and discovery | [[Manual & automated Windows enumeration]], [[🛠️ Windows kernel exploits]] patch-audit sections |
| Tokens and Potato attacks | [[Access tokens and impersonation]], [[Potato attacks]], [[🛠️ JuicyPotato]], [[PrintSpoofer]], [[RoguePotato]], [[🛠️ SweetPotato]], [[GodPotato]], [[LocalPotato & EfxPotato]] |
| Token privileges | [[SeBackupPrivilege & SeRestorePrivilege]], [[SeDebugPrivilege]], [[SeTakeOwnershipPrivilege]], [[SeLoadDriverPrivilege]] |
| Privileged groups | [[Backup Operators]], [[Server Operators]], [[DnsAdmins]], [[Print Operators]], [[Account Operators]], [[Hyper-V Administrators]], [[WinRM-RDP Operators]], [[Event Log Readers]] |
| Services | [[Weak service DACLs]], [[Unquoted service paths]], [[DLL hijacking]], [[Service registry key misconfigurations]] |
| Autoruns and registry policy | [[🛠️ Auto-start extensibility points]], [[AlwaysInstallElevated]] |
| Credentials | [[🛠️ Windows credential hunting]], [[Dumping Windows registry hives]], [[Dumping LSASS memory]], [[🛠️ Group Policy Preferences (GPP) & Registry]], [[🛠️ Credential Manager]], [[🛠️ DPAPI credentials]], [[🛠️ Dumping LSA secrets]] |
| UAC and restricted environments | [[🛠️ UAC bypasses]], [[🛠️  Citrix breakout]] |

>[!warning]+ Kernel and LSASS handling.
>- Kernel exploits can crash the host and burn access, so snapshot or weigh stability before execution.
>- LSASS access can trigger EDR alerts, so exhaust passive credential paths first.
