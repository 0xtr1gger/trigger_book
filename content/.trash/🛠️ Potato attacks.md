---
created: 2026-09-01
updated: 2026-09-01
tags:
  - Windows
  - Windows_PrivEsc
status: incomplete
---

## Potato attacks overview & OS matrix

> [!abstract]+ Scope
> Selection framework, operating system compatibility matrix, structural requirements, and privilege prerequisites for Windows local privilege escalation potato attacks including [[JuicyPotato]], [[PrintSpoofer]], [[RoguePotato]], [[SweetPotato]], [[GodPotato]], and [[LocalPotato & EfxPotato]].

- [ ] Verify `SeImpersonatePrivilege` or `SeAssignPrimaryTokenPrivilege` via `whoami /priv`.
- [ ] Query operating system caption and build number via `wmic os get Caption,Version,BuildNumber`.
- [ ] Check if the Print Spooler service (`spoolsv.exe`) is running via `sc.exe query spooler`.
- [ ] Audit local listening ports and remote network accessibility on TCP port 135 and port 5985.
- [ ] Select and execute the compatible potato binary based on OS build constraints.

---

## How potato attacks work

Potato attacks elevate access from a low-privileged service account (such as `NT AUTHORITY\LOCAL SERVICE`, `NT AUTHORITY\NETWORK SERVICE`, or IIS AppPool accounts) to `NT AUTHORITY\SYSTEM`. 

The attack sequence follows a consistent multi-step workflow:

1. **Triggering privileged authentication**: The exploit forces a `SYSTEM` process or service (such as `RPCSS`, `spoolsv.exe`, or `BITS`) to initiate an authenticated connection to an endpoint managed by the exploit.
2. **Intercepting authentication tokens**: The exploit captures the NTLM challenge-response traffic or named pipe authentication from the privileged service.
3. **Impersonating client security context**: The exploit calls `ImpersonateNamedPipeClient()` or RPC impersonation APIs to acquire a `SYSTEM` impersonation token.
4. **Duplicating access tokens**: The exploit calls `DuplicateTokenEx()` to convert the impersonation token into a primary access token.
5. **Spawning elevated processes**: The exploit calls `CreateProcessWithTokenW()` or `CreateProcessAsUserW()` to launch a shell or binary running as `NT AUTHORITY\SYSTEM`.

> [!note] See [[Access tokens and impersonation]] for details on primary vs impersonation access tokens and token duplication processes.

## Comparing potato attack vectors

Selection of a potato exploit depends on the operating system build, active system services, network connectivity, and RPCSS security restrictions.

### Operating system and requirement matrix

| Exploit | Supported OS builds | Port 135 required | DCOM / RPCSS dependency | Print Spooler required | External listener required | Required privileges | Key bypass / mechanism |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [[JuicyPotato]] | Windows 7 – Windows 10 `1803` / Server 2016 | No | Yes | No | No | `SeImpersonatePrivilege` / `SeAssignPrimaryTokenPrivilege` | Custom `OBJREF` marshaling to local TCP listener. |
| [[PrintSpoofer]] | Windows 8.1 – Windows 11 / Server 2022 | No | No | Yes | No | `SeImpersonatePrivilege` / `SeAssignPrimaryTokenPrivilege` | Path validation bypass (`/` in pipe hostname) via MS-RPRN RPC interface. |
| [[RoguePotato]] | Windows 10 `1809`+ / Server 2019 – 2022 | Yes (Remote) | Yes | No | Yes | `SeImpersonatePrivilege` | Remote OXID resolver redirection returning poisoned `ncacn_np` binding strings. |
| [[SweetPotato]] | Windows 7 – Server 2019+ | Conditional | Yes | Conditional | No | `SeImpersonatePrivilege` | Multi-vector wrapper abusing BITS WinRM listener (port 5985), DCOM, or Print Spooler. |
| [[GodPotato]] | Windows 8.1 – Windows 11 / Server 2012 – 2022 | No | Yes | No | No | `SeImpersonatePrivilege` | DCOM activation via local RPCSS path bypassing `1809` OXID resolution checks. |
| [[LocalPotato & EfxPotato\|LocalPotato / EfxPotato]] | Windows 10 / 11 / Server 2019 – 2022 | No | No | No | No | `SeImpersonatePrivilege` | Local SMB-to-HTTP/RPC NTLM reflection and authentication context swapping. |

## Selecting the optimal attack vector

Evaluate system conditions in the following priority order to select an exploit binary:

- **Primary choice for modern systems with Print Spooler enabled**: Use [[PrintSpoofer]]. It requires no DCOM interaction, no port 135 access, and executes reliably across Windows 10 `1809`+ and Server 2019/2022.
- **Universal choice for modern standalone systems without Print Spooler**: Use [[GodPotato]]. It operates locally across all modern builds without external network dependencies.
- **Choice for legacy systems**: Use [[JuicyPotato]] on Windows Server 2016, Windows 7, or Windows 10 builds prior to `1809`.
- **Choice when remote attacker infrastructure is available**: Use [[RoguePotato]] if JuicyPotato is blocked, Print Spooler is stopped, and the target system can reach your remote listener on TCP port 135.
- **Choice for C2 in-memory execution**: Use [[SweetPotato]] when operating through C2 agents supporting `execute-assembly` to automatically select available local vectors.
- **Choice for bypassing NTLM reflection mitigations on modern patched builds**: Use [[LocalPotato & EfxPotato|LocalPotato / EfxPotato]] when traditional DCOM NTLM reflection fails due to local port binding restrictions.

## Enumerating potato attack prerequisites

Execute these commands to gather required system metrics before selecting an exploit.

- Query assigned user privileges to confirm impersonation rights:

```powershell
whoami /priv
```

- Inspect operating system caption, version, and build number:

```powershell
wmic os get Caption,Version,BuildNumber,OSArchitecture
```

- Check the execution state of the Print Spooler service:

```powershell
sc.exe query spooler
```

- Audit local listening TCP ports to verify port availability:

```powershell
netstat -ano
```

### Command parameter reference

| Tool / Command | Parameter | Function |
| --- | --- | --- |
| `whoami` | `/priv` | Displays current security token privileges and assigned rights. |
| `wmic` | `os get ...` | Queries WMI for OS caption, build number, and architecture. |
| `sc.exe` | `query spooler` | Interrogates the Service Control Manager for spooler service status. |
| `netstat` | `-ano` | Displays active TCP/UDP connections, listening ports, and owning PIDs. |

> [!tip]+ Verification of elevated access
> After running any potato binary, execute `whoami` to verify that the returned security context is `NT AUTHORITY\SYSTEM`. If process creation fails, check `whoami /priv` to confirm that `SeImpersonatePrivilege` or `SeAssignPrimaryTokenPrivilege` is listed in the token.

## References and further reading

- [`Windows Privilege Escalation — Potatoes — Jorge Lajara`](https://jlajara.gitlab.io/Potatoes_Windows_Privesc)
- [`Juicy Potato — GitHub`](https://github.com/ohpe/juicy-potato)
- [`PrintSpoofer — GitHub`](https://github.com/itm4n/PrintSpoofer)
- [`RoguePotato — GitHub`](https://github.com/antonioCoco/RoguePotato)
- [`GodPotato — GitHub`](https://github.com/BeichenDream/GodPotato)
- [`LocalPotato — GitHub`](https://github.com/localpotato/LocalPotato)
