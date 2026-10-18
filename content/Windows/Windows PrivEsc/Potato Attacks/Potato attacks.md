---
created: 2026-09-01
updated: 2026-09-20
tags:
  - Windows
  - Windows_PrivEsc
status: substantial
---

> [!abstract]+ **Scope**: Overview of Windows local privilege escalation using potato attacks, including [[🛠️ JuicyPotato]], [[PrintSpoofer]], [[RoguePotato]], [[🛠️ SweetPotato]], [[GodPotato]], and [[LocalPotato & EfxPotato]]; a strategy for the selecting the appropriate exploit; OS compatibility and requirements of each exploit.

- [ ] Verify `SeImpersonatePrivilege` or `SeAssignPrimaryTokenPrivilege` via `whoami /priv`.
- [ ] Query operating system caption and build number via `wmic os get Caption,Version,BuildNumber`.
- [ ] Check if the Print Spooler service (`spoolsv.exe`) is running via `sc.exe query spooler`.
- [ ] Audit local listening ports and remote network accessibility on TCP port `135` and port `5985`.
- [ ] Select and execute the compatible potato binary based on OS build constraints.
## Potato attacks

- Potato attacks elevate access from a low-privileged service account (such as `NT AUTHORITY\LOCAL SERVICE`, `NT AUTHORITY\NETWORK SERVICE`, or IIS AppPool accounts) to `NT AUTHORITY\SYSTEM`. 

- General attack sequence:

	1. **Triggering privileged authentication**: The exploit forces a `SYSTEM` process or service (such as `RPCSS`, `spoolsv.exe`, or `BITS`) to initiate an authenticated connection to an endpoint managed by the exploit.
	2. **Intercepting authentication tokens**: The exploit captures the NTLM challenge-response traffic or named pipe authentication from the privileged service.
	3. **Impersonating client security context**: The exploit calls `ImpersonateNamedPipeClient()` or RPC impersonation APIs to acquire a `SYSTEM` impersonation token.
	4. **Duplicating access tokens**: The exploit calls `DuplicateTokenEx()` to convert the impersonation token into a primary access token.
	5. **Spawning elevated processes**: The exploit calls `CreateProcessWithTokenW()` or `CreateProcessAsUserW()` to launch a shell or binary running as `NT AUTHORITY\SYSTEM`.

>[!note] See [[Access tokens and impersonation]].

## Potato exploits

- Which potato exploit to use depends on the target OS build, active system services, network connectivity, and RPCSS security restrictions.

| Exploit                                              | Supported buils                               | Port `135` required | DCOM / RPCSS dependency | Print Spooler required | External listener required |
| ---------------------------------------------------- | --------------------------------------------- | ------------------- | ----------------------- | ---------------------- | -------------------------- |
| [[🛠️ JuicyPotato]]                                      | Windows 7 - Windows 10 `1803` / Server 2016   | No                  | Yes                     | No                     | No                         |
| [[PrintSpoofer]]                                     | Windows 8.1 - Windows 11 / Server 2022        | No                  | No                      | Yes                    | No                         |
| [[RoguePotato]]                                      | Windows 10 `1809`+ / Server 2019 - 2022       | Yes (Remote)        | Yes                     | No                     | Yes                        |
| [[GodPotato]]                                        | Windows 8.1 - Windows 11 / Server 2012 – 2022 | No                  | Yes                     | No                     | No                         |
| [[LocalPotato & EfxPotato\|LocalPotato / EfxPotato]] | Windows 10 / 11 / Server 2019 - 2022          | No                  | No                      | No                     | No                         |

>[!important] Each exploit variant requires **`SeImpersonatePrivilege`** ([[🛠️ JuicyPotato]] and [[PrintSpoofer]] can also work with `SeAssignPrimaryTokenPrivilege`).

- Modern systems (Windows 10 `1809`+, Server 2019/2022) with Print Spooler enabled -> [[PrintSpoofer]] (no DCOM interaction required, no port `135` access).
- Modern systems with Print Spooler disabled -> [[GodPotato]] (operates locally).
- Legacy systems (Windows Server 2016, Windows 7, or Windows 10 builds prior to `1809`) with Print Spooler disabled -> [[🛠️ JuicyPotato]].
- Systems where JuicyPotato is blocked, Print Spooler is stopped, and the target system can reach your remote listener on TCP port `135` -> [[RoguePotato]].

## Gathering prerequisite information

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

>[!note] See [[Manual & automated Windows enumeration]].

## References and further reading

- [`Windows Privilege Escalation — Potatoes — Jorge Lajara`](https://jlajara.gitlab.io/Potatoes_Windows_Privesc)
- [`Juicy Potato — GitHub`](https://github.com/ohpe/juicy-potato)
- [`PrintSpoofer — GitHub`](https://github.com/itm4n/PrintSpoofer)
- [`RoguePotato — GitHub`](https://github.com/antonioCoco/RoguePotato)
- [`GodPotato — GitHub`](https://github.com/BeichenDream/GodPotato)
- [`LocalPotato — GitHub`](https://github.com/localpotato/LocalPotato)
