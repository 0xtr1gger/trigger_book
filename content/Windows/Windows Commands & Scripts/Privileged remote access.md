---
created: 2026-08-15
updated: 2026-10-20
tags:
  - Windows
status: complete
---
>[!abstract]+ **Scope**: Windows remote management protocols, administrative execution mechanisms, and lateral movement tools; establishing remote sessions using WinRM, SMB/RPC, WMI, DCOM, Task Scheduler, RDP, MSSQL, and OpenSSH; credential options, Pass-the-Hash, and Kerberos authentication.

>[!abstract]+ Table of contents
> - [[#Remote access protocols]]
> - [[#WinRM]]
> - [[#SMB]]
> - [[#Executing commands via WMI and DCOM]]
> - [[#Executing commands with atexec.py]]
> - [[#RDP]]
> - [[#MSSQL instances]]
> - [[#SSH]]
## Remote access protocols

- Windows exposes several administrative and management protocols for command command execution and interactive access:

| Protocol           | Default ports                     | Protocol/transport                    | Execution mechanism                         | Required privileges                         | Common tools                                                                 |
| :----------------- | :-------------------------------- | :------------------------------------ | :------------------------------------------ | :------------------------------------------ | :--------------------------------------------------------------------------- |
| **WinRM**          | `5985` (HTTP), <br>`5986` (HTTPS) | HTTP/HTTPS (SOAP/WS-Man)              | PowerShell runspaces (`wsmprovhost.exe`)    | `Remote Management Users`, `Administrators` | `Evil-WinRM`, <br>`Enter-PSSession`, <br>`Invoke-Command`, <br>`netexec`     |
| **SMB/RPC**        | `445` (TCP)                       | SMB named pipes (`\pipe\svcctl`)      | Service Control Manager (service binary)    | `Administrators`                            | `psexec.py`, <br>`smbexec.py`, <br>`PsExec.exe`, <br>`sc.exe`, <br>`netexec` |
| **WMI**            | `135` (RPC), <br>`49152`-`65535`  | RPC/DCOM                              | `Win32_Process.Create`                      | `Administrators`                            | `wmiexec.py`, <br>`wmic`, <br>`Invoke-CimMethod`, <br>`netexec`              |
| **DCOM**           | `135` (RPC), <br>`49152`-`65535`  | RPC/DCOM                              | Object activation (`MMC20`, `ShellWindows`) | `Distributed COM Users`, `Administrators`   | `dcomexec.py`, <br>PowerShell COM objects                                    |
| **Task Scheduler** | `135`, `445` (RPC)                | RPC (`ITaskScheduler`/`ITaskService`) | Scheduled task creation                     | `Administrators`                            | `atexec.py`, <br>`schtasks.exe`                                              |
| **RDP**            | `3389` (TCP/UDP)                  | RDP (TLS/NLA)                         | Interactive graphical session               | `Remote Desktop Users`, `Administrators`    | `xfreerdp`, <br>`mstsc.exe`, <br>`Remmina`                                   |
| **MSSQL**          | `1433` (TCP)                      | TDS (Tabular Data Stream)             | Extended stored procedures (`xp_cmdshell`)  | `sysadmin` role, `CONTROL SERVER`           | `mssqlclient.py`, <br>`sqlcmd`, <br>`netexec`                                |
| **SSH**            | `22` (TCP)                        | SSH                                   | Interactive shell, command execution        | Local/domain user account                   | `ssh`, <br>`sftp`                                                            |

- In most cases, you can authenticate with a plaintext password, an NT hash ([[Pass-the-Hash]]), or a Kerberos ticket ([[Pass-the-Ticket]]).
## WinRM

>**[Windows Remote Management (WinRM)](https://learn.microsoft.com/en-us/windows/win32/winrm/portal)** is the Microsoft implementation of the [WS-Management protocol](https://learn.microsoft.com/en-us/windows/win32/winrm/ws-management-protocol), a SOAP-based standard for remotely exchanging management information between Windows systems.

- WinRM uses HTTP or HTTPS as its transport protocols; it listens on TCP port `5985` for HTTP and TCP port `5986` for HTTPS.

- Over HTTP, WinRM messages can still be encrypted at the application level when an authentication mechanism that provides message encryption, such as Kerberos or NTLM via `Negotiate`, is used. The HTTPS listener additionally protects the connection with TLS.

- WinRM provides the underlying transport for PowerShell Remoting. `Enter-PSSession` and `Invoke-Command` execute PowerShell commands and scripts in a remote session hosted by `wsmprovhost.exe` on the target.

- It supports several authentication schemes, including `Negotiate` (NTLM/Kerberos), Kerberos, Basic, CredSSP, and client certificates.

>[!note] See [`Windows Remote Management — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/winrm/portal) and [`WS-Management Protocol — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/winrm/ws-management-protocol).

>[!important] To establish WinRM sessions, a user must be a member of the **`Remote Management Users`** or **`Administrators`** group.

### `Evil-WinRM`

>**[`Evil-WinRM`](https://github.com/Hackplayers/evil-winrm)** is an open-source WinRM client written in Ruby. It provides an interactive PowerShell session over WinRM.

- Authenticate using a password:

```bash
evil-winrm -i 10.10.11.5 -u jdoe -p 'passwd123'
```

- Authenticate using an NT hash ([[Pass-the-Hash]]):

```bash
evil-winrm -i 10.10.11.5 -u jdoe -H 2b576acfd5e0c865136732c44b49b6b1
```

- Authenticate using a Kerberos ticket from the credential cache (specified by `KRB5CCNAME`):

```bash
evil-winrm -i dc01.example.com -r example.com
```

- Connect through an HTTPS listener on port `5986`:

```bash
evil-winrm -i 10.10.11.5 -u jdoe -p 'passwd123' -S
```

- Authenticate using a client certificate and private key:

```bash
evil-winrm -i 10.10.11.5 -c cert.pem -k key.pem -S
```

- Specify local directories containing PowerShell scripts (`-s`) and binaries (`-e`) to load into memory during the session:

```bash
evil-winrm -i 10.10.11.5 -u jdoe -p 'passwd123' -s /opt/scripts -e /opt/binaries
```

| Option | Description                                                                       |
| :----- | :-------------------------------------------------------------------------------- |
| `-i`   | Target IP address or FQDN.                                                        |
| `-u`   | Username for authentication.                                                      |
| `-p`   | Plaintext password.                                                               |
| `-H`   | NT hash to use for authentication (Pass-the-Hash).                                |
| `-r`   | Kerberos realm or Active Directory domain name (enables Kerberos authentication). |
| `-c`   | Path to the client certificate for certificate-based authentication.              |
| `-k`   | Path to the private key corresponding to the client certificate.                  |
| `-S`   | Enable SSL/TLS transport on TCP port `5986`.                                      |
| `-P`   | Custom WinRM listening port (default `5985` for HTTP, `5986` for HTTPS).          |
| `-s`   | Path to a local directory containing PowerShell scripts to load into memory.      |
| `-e`   | Path to a local directory containing executables for in-memory execution.         |
### Executing commands using NetExec WinRM

- [`NetExec`](https://github.com/Pennyw0rth/NetExec) can be used to execute commands remotely over WinRM.
---
- Authenticate using a password and execute a CMD command remotely (lowercase `-x`):

```bash
netexec winrm 10.10.11.5 -u jdoe -p 'passwd123' -x 'whoami /all'
```

- Execute a PowerShell cmdlet (uppercase `-X`):

```bash
netexec winrm 10.10.11.5 -u jdoe -p 'passwd123' -X 'Get-Process'
```

- Authenticate using an NT hash ([[Pass-the-Hash]]):

```bash
netexec winrm 10.10.11.5 -u jdoe -H 2b576acfd5e0c865136732c44b49b6b1 -x 'whoami /all'
```

- Authenticate using a Kerberos ticket from the credential cache (specified by `KRB5CCNAME`):

```bash
netexec winrm dc01.example.com -k --use-kcache -x 'whoami /all'
```

| Option             | Description                                                                   |
| :----------------- | :---------------------------------------------------------------------------- |
| `-u`, `--username` | Username or file containing usernames for authentication.                     |
| `-p`, `--password` | Password or file containing passwords.                                        |
| `-H`, `--hash`     | NT hash to use for authentication (Pass-the-Hash); format: `LM_hash:NT_hash`. |
| `-d`               | Active Directory domain for authentication.                                   |
| `-x`               | CMD command to execute remotely.                                              |
| `-X`               | PowerShell command to execute remotely.                                       |
| `-k`, `--kerberos` | Enable Kerberos authentication.                                               |
| `--use-kcache`     | Use Kerberos credentials from a credential cache (`KRB5CCNAME`).              |
| `--ssl`            | Connect to the WinRM HTTPS listener on TCP port `5986`.                       |
>[!note] See [[🛠️ NetExec & CrackMapExec]].
### Establishing WinRM sessions from Windows

- PowerShell provides built-in cmdlets for establishing WinRM sessions and executing commands on remote Windows hosts.

---

 1. Convert the plaintext password to a `SecureString`:

```powershell
$password = ConvertTo-SecureString 'passwd123' -AsPlainText -Force
```

2. Create a `PSCredential` object:

```powershell
$cred = New-Object System.Management.Automation.PSCredential ('example\jdoe', $password)
```

3. Establish an interactive PowerShell session:

```powershell
Enter-PSSession -ComputerName 10.10.11.5 -Credential $cred
```

---

- Establish an interactive session over HTTPS on TCP port `5986`:

```powershell
Enter-PSSession -ComputerName dc01.example.com -Credential $cred -UseSSL -Port 5986
```

- Execute a script block on a remote host:

```powershell
Invoke-Command -ComputerName 10.10.11.5 -Credential $cred -ScriptBlock { whoami /priv }
```

- Execute a local script file on a remote host:

```powershell
Invoke-Command -ComputerName 10.10.11.5 -Credential $cred -FilePath .\enum.ps1
```

| Option               | Description                                                                        |
| :------------------- | :--------------------------------------------------------------------------------- |
| `-ComputerName`      | Remote hostname, FQDN, or IP address to connect to.                                |
| `-Credential`        | `PSCredential` object to use for authentication.                                   |
| `-ScriptBlock`       | PowerShell commands (in braces `{ ... }`) to execute remotely.                     |
| `-FilePath`          | Local path to a `.ps1` script file to execute remotely.                            |
| `-UseSSL`            | Use HTTPS for the WinRM connection on TCP port `5986`.                             |
| `-Port`              | Network port to use for the WinRM connection (default: `5985` HTTP, `5986` HTTPS). |
| `-ConfigurationName` | Custom session configuration endpoint on the remote machine.                       |
| `-Session`           | An existing `PSSession` object to enter or run commands against.                   |

>[!tip]+
>- Verify the remote WinRM service responds:
>
> ```powershell
> Test-WSMan -ComputerName 10.10.11.5
> ```

## SMB

>**Server Message Block (SMB)** is a network protocol for sharing files, printers, and serial ports; it also supports inter-process communication through named pipes.

- By default, SMB listens on TCP port `445` (directly over TCP). Legacy deployments rely on NetBIOS as a transport protocol, exposed on TCP port `139`.
- Named pipes exposed over SMB can carry RPC (Remote Procedure Call) interfaces, such as `\pipe\svcctl` (Service Control Manager, SCM), `\pipe\atsvc` (Task Scheduler), and `\pipe\winreg` (remote registry).
- Remote command execution over SMB relies on SMB access to named pipes that transport RPC communication, together with the ability to create services through the Service Control Manager (SCM). Administrative shares such as `ADMIN$` and `C$` provide SMB access to the remote system.

- Tools like [`psexec.py`](https://github.com/fortra/impacket/blob/master/examples/psexec.py) and [`smbexec.py`](https://github.com/fortra/impacket/blob/master/examples/smbexec.py) ([Impacket](https://github.com/fortra/impacket)) communicate with the SCM over `\pipe\svcctl` to create and run temporary Windows services that execute commands. [`services.py`](https://github.com/fortra/impacket/blob/master/examples/services.py) exposes the same SCM interface for creating, starting, and deleting services directly.

>[!note] To create services remotely, you need to be a member of the local **`Administrators`** group.

>[!note] Command execution over WMI/DCOM and the Task Scheduler is covered in [[#Executing commands via WMI and DCOM]] and [[#Scheduling tasks with `atexec`]]; both mechanisms retrieve command output over SMB (`ADMIN$`).
### Executing commands using `psexec.py`

- [`psexec.py`](https://github.com/fortra/impacket/blob/master/examples/psexec.py) uploads a service executable to the `ADMIN$` share, registers it as a service through SCM RPC, redirects the process's standard I/O through named pipes, and deletes the service binary after execution completes.
---
- Authenticate using a password and spawn an interactive shell:

```bash
psexec.py example.com/jdoe:'passwd123'@10.10.11.5
```

- Authenticate using an NT hash ([[Pass-the-Hash]]):

```bash
psexec.py -hashes :2b576acfd5e0c865136732c44b49b6b1 example.com/jdoe@10.10.11.5
```


- Authenticate using a Kerberos ticket from the credential cache (specified by `KRB5CCNAME`):

```bash
psexec.py -k -no-pass example.com/jdoe@dc01.example.com
```

- Execute a remote command non-interactively:

```bash
psexec.py example.com/jdoe:'passwd123'@10.10.11.5 'whoami /all'
```

- Register the service under a custom name and upload the service binary to a specified share:

```bash
psexec.py -service-name RemoteSvc -share C$ example.com/jdoe:'passwd123'@10.10.11.5
```

| Option                | Description                                                                             |
| :-------------------- | :-------------------------------------------------------------------------------------- |
| `-hashes`             | NT hash to use for authentication (Pass-the-Hash); format: `LM_hash:NT_hash`.           |
| `-no-pass`            | Suppress the password prompt (useful for Kerberos authentication).                      |
| `-k`                  | Use Kerberos credentials from a credential cache (`KRB5CCNAME`).                        |
| `-service-name`       | Set a custom service name on the target host.                                           |
| `-remote-binary-name` | Set a custom binary filename uploaded to the remote share.                              |
| `-share`              | Remote writable SMB share used for uploading the service executable (default `ADMIN$`). |
| `-codec`              | Set the encoding used to read output.                                                   |
| `-dc-ip`              | IP address of the Domain Controller to use for Kerberos authentication.                 |

### Executing commands using `smbexec.py`

- [`smbexec.py`](https://github.com/fortra/impacket/blob/master/examples/smbexec.py) creates a service that executes a command with `cmd.exe /c` and redirects its standard output to a file on a writable share (default: `C$`). This avoids uploading a service executable to the target.
---
- Authenticate using a password and spawn an interactive shell:

```bash
smbexec.py example.com/jdoe:'passwd123'@10.10.11.5
```

- Authenticate using an NT hash ([[Pass-the-Hash]]):

```bash
smbexec.py -hashes :2b576acfd5e0c865136732c44b49b6b1 example.com/jdoe@10.10.11.5
```

- Authenticate using a Kerberos ticket from the credential cache (specified by `KRB5CCNAME`):

```bash
smbexec.py -k -no-pass example.com/jdoe@dc01.example.com
```

- Specify a custom share for temporary output files:

```bash
smbexec.py -share ADMIN$ example.com/jdoe:'passwd123'@10.10.11.5
```

| Option     | Description                                                                   |
| :--------- | :---------------------------------------------------------------------------- |
| `-hashes`  | NT hash to use for authentication (Pass-the-Hash); format: `LM_hash:NT_hash`. |
| `-no-pass` | Suppress the password prompt (useful for Kerberos authentication).            |
| `-k`       | Use Kerberos credentials from a credential cache (`KRB5CCNAME`).              |
| `-share`   | Remote writable SMB share used to store command output (default: `C$`).       |
| `-mode`    | Execution mode (`SERVER` or `SHARE`).                                         |
| `-port`    | Destination SMB port (default `445`).                                         |
| `-codec`   | Set the encoding used to read output files.                                   |
| `-dc-ip`   | IP address of the Domain Controller to use for Kerberos authentication.       |

### Executing commands using NetExec SMB

- [`NetExec`](https://github.com/Pennyw0rth/NetExec) can be used to execute commands remotely over SMB.
---

- Authenticate using a password and execute a CMD command remotely:

```bash
netexec smb 10.10.11.5 -u jdoe -p 'passwd123' -x 'whoami /all'
```

- Execute a command using the `smbexec` execution method:

```bash
netexec smb 10.10.11.5 -u jdoe -p 'passwd123' --exec-method smbexec -x 'ipconfig /all'
```

- Execute a command using the `wmiexec` execution method:

```bash
netexec smb 10.10.11.5 -u jdoe -p 'passwd123' --exec-method wmiexec -x 'ipconfig /all'
```

- Execute a PowerShell command remotely:

```bash
netexec smb 10.10.11.5 -u jdoe -p 'passwd123' -X 'Get-Process'
```

- Authenticate using an NT hash ([[Pass-the-Hash]]):

```bash
netexec smb 10.10.11.5 -u jdoe -H 2b576acfd5e0c865136732c44b49b6b1 -x 'whoami /all'
```

- Authenticate using a Kerberos ticket from the credential cache (specified by `KRB5CCNAME`):

```bash
netexec smb dc01.example.com -k --use-kcache -x 'whoami /all'
```

| Option             | Description                                                                          |
| :----------------- | :----------------------------------------------------------------------------------- |
| `-u`, `--username` | Username or file containing usernames for authentication.                            |
| `-p`, `--password` | Plaintext password or file containing passwords.                                     |
| `-H`, `--hash`     | NT hash to use for authentication (Pass-the-Hash); format: `LM_hash:NT_hash`.        |
| `-d`               | Active Directory domain for authentication.                                          |
| `-x`               | CMD command to execute via `cmd.exe /c`.                                             |
| `-X`               | PowerShell command to execute.                                                       |
| `--exec-method`    | Execution method to use (`wmiexec`, `smbexec`, `mmcexec`, `atexec`, `ridexec`).      |
| `--share`          | Share name to use for staging files or retrieving command output (default `ADMIN$`). |
| `-k`, `--kerberos` | Enable Kerberos authentication.                                                      |
| `--use-kcache`     | Use Kerberos credentials from a credential cache (`KRB5CCNAME`).                     |

### Executing commands natively on Windows

- [`PsExec.exe`](https://learn.microsoft.com/en-us/sysinternals/downloads/psexec) (from the Sysinternals suite) runs processes on remote systems by uploading a service binary to `ADMIN$` and registering the service through the SCM.

---
- Connect and spawn an interactive `SYSTEM` shell using `PsExec.exe`:

```powershell
PsExec.exe \\10.10.11.5 -u example\jdoe -p 'passwd123' -s cmd.exe
```

- Run a command in the background:

```powershell
PsExec.exe \\10.10.11.5 -u example\jdoe -p 'passwd123' -d cmd.exe /c "whoami > C:\Temp\out.txt"
```

- Copy a local executable to the remote host before execution:

```powershell
PsExec.exe \\10.10.11.5 -u example\jdoe -p 'passwd123' -c agent.exe
```

| Option        | Description                                                                   |
| :------------ | :---------------------------------------------------------------------------- |
| `-u`          | Username for remote authentication (`domain\user`).                           |
| `-p`          | Plaintext password for the user.                                              |
| `-s`          | Execute the remote process in the `SYSTEM` security context.                  |
| `-i`          | Run the program interactively on the specified desktop session.               |
| `-d`          | Detach the process and return immediately without waiting for termination.    |
| `-c`          | Copy the specified executable to the remote system before execution.          |
| `-h`          | Run the process with the account elevated token if available.                 |
| `-accepteula` | Automatically accept the Sysinternals license agreement.                      |

- Create a service remotely ([`sc.exe`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/sc-create)) and set its `binPath` to your custom executable: 

```powershell
sc.exe \\10.10.11.5 create RemoteSvc binPath= "C:\Windows\Temp\agent.exe" start= demand
```

- Start the newly created service:

```powershell
sc.exe \\10.10.11.5 start RemoteSvc
```

- Stop a running service:

```powershell
sc.exe \\10.10.11.5 stop RemoteSvc
```

- Delete the service after execution:

```powershell
sc.exe \\10.10.11.5 delete RemoteSvc
```

| Option | Description |
| :--- | :--- |
| `create` | Create a new service subkey in the SCM database and registry. |
| `binPath=` | Specify the binary path to the service executable (requires a space after `=`). |
| `start=` | Specify the service start type (`boot`, `system`, `auto`, `demand`, `disabled`). |
| `obj=` | Specify the account name under which the service runs (default `LocalSystem`). |
| `start` | Start a stopped service. |
| `stop` | Send a `STOP` control request to a running service. |
| `delete` | Delete a service subkey from the SCM database and registry. |
| `query` | Query operational status and configuration of services. |

## Executing commands via WMI and DCOM

>**[Windows Management Instrumentation (WMI)](https://learn.microsoft.com/en-us/windows/win32/wmisdk/wmi-start-page)** is Microsoft'a=s implementation of Web-Based Enterprise Management (WBEM), based on the Common Information Model (CIM). It provides a unified interface for querying and managing Windows components.

- WMI can be accessed remotely over [DCOM](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-dcom/4a893f3d-bd29-48cd-9f43-d9777a4415b0) (the RPC endpoint mapper on TCP port `135` -> dynamic RPC port in the `49152`-`65535` range) or over WinRM (through CIM/WS-Man interfaces).
- The `Win32_Process` class exposes a `Create` method that can launch a process on the remote target. This is the mechanism used by [`wmiexec.py`](https://github.com/fortra/impacket/blob/master/examples/wmiexec.py), [`dcomexec.py`](https://github.com/fortra/impacket/blob/master/examples/dcomexec.py) (Impacket) and [`Invoke-CimMethod` ](https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/invoke-cimmethod?view=powershell-7.6).

>[!note] **DCOM (Distributed COM)** extends the Component Object Model such that COM objects can be activated and called remotely over RPC. Some registered objects, such as `MMC20.Application`, `ShellWindows`, and `ShellBrowserWindow`, expose methods that can spawn child processes.

>[!note] To activate DOM objects, you need to be a member of the **`Distributed COM Users`** group.

>[!note] See [`Windows Management Instrumentation — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/wmisdk/wmi-start-page) and [`[MS-DCOM]: Distributed Component Object Model (DCOM) Remote Protocol — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-dcom/4a893f3d-bd29-48cd-9f43-d9777a4415b0).
### Executing commands with `wmiexec.py`

- [`wmiexec.py`](https://github.com/fortra/impacket/blob/master/examples/wmiexec.py) invokes the `Win32_Process.Create` method over WMI and retrieves command output through files written to the `ADMIN$` share over SMB.

---

- Authenticate using a password and spawn an interactive shell:

```bash
wmiexec.py example.com/jdoe:'passwd123'@10.10.11.5
```

- Authenticate using an NT hash ([[Pass-the-Hash]]):

```bash
wmiexec.py -hashes :2b576acfd5e0c865136732c44b49b6b1 example.com/jdoe@10.10.11.5
```

- Authenticate using a Kerberos ticket from the credential cache (specified by `KRB5CCNAME`):

```bash
wmiexec.py -k -no-pass example.com/jdoe@dc01.example.com
```

- Execute a command non-interactively using PowerShell:

```bash
wmiexec.py -shell-type powershell example.com/jdoe:'passwd123'@10.10.11.5 'Get-Process'
```

- Execute a command without creating or retrieving output files over SMB:

```bash
wmiexec.py -nooutput example.com/jdoe:'passwd123'@10.10.11.5 'calc.exe'
```

| Option        | Description                                                                   |
| :------------ | :---------------------------------------------------------------------------- |
| `command`     | Command to execute remotely (if omitted, spawns a semi-interactive shell).    |
| `-hashes`     | NT hash to use for authentication (Pass-the-Hash); format: `LM_hash:NT_hash`. |
| `-no-pass`    | Suppress the password prompt when using Kerberos or blank passwords.          |
| `-k`          | Use Kerberos credentials from a credential cache (`KRB5CCNAME`).              |
| `-share`      | Share used to write and read command output files (default `ADMIN$`).         |
| `-shell-type` | Shell wrapper used to execute commands (`cmd` or `powershell`).               |
| `-nooutput`   | Execute the command without creating or retrieving output files over SMB.     |
| `-codec`      | Set the encoding used to read output files.                                   |
| `-dc-ip`      | IP address of the Domain Controller for Kerberos ticket resolution.           |

### Executing commands with `dcomexec.py`

- [`dcomexec.py`](https://github.com/fortra/impacket/blob/master/examples/dcomexec.py) abuses exposed DCOM objects such as `MMC20.Application`, `ShellWindows`, or `ShellBrowserWindow` to spawn child processes.

---
- Authenticate using a password and spawn a shell via the `MMC20.Application` DCOM object:

```bash
dcomexec.py -object MMC20 example.com/jdoe:'passwd123'@10.10.11.5
```

- Execute commands via the `ShellWindows` DCOM object:

```bash
dcomexec.py -object ShellWindows example.com/jdoe:'passwd123'@10.10.11.5
```

- Execute commands via the `ShellBrowserWindow` DCOM object:

```bash
dcomexec.py -object ShellBrowserWindow example.com/jdoe:'passwd123'@10.10.11.5
```

- Authenticate using an NT hash ([[Pass-the-Hash]]):

```bash
dcomexec.py -hashes :2b576acfd5e0c865136732c44b49b6b1 -object MMC20 example.com/jdoe@10.10.11.5
```

| Option           | Description                                                                   |
| :--------------- | :---------------------------------------------------------------------------- |
| `command`        | Command to execute remotely (if omitted, spawns a semi-interactive shell).    |
| `-object`        | Target DCOM object (`MMC20`, `ShellWindows`, or `ShellBrowserWindow`).        |
| `-hashes`        | NT hash to use for authentication (Pass-the-Hash); format: `LM_hash:NT_hash`. |
| `-no-pass`       | Suppress the password prompt when using Kerberos authentication.              |
| `-k`             | Use Kerberos credentials from a credential cache (`KRB5CCNAME`).              |
| `-silentcommand` | Execute the command without retrieving standard output over SMB.              |
| `-share`         | Remote writable SMB share used for storing command output (default `ADMIN$`). |

### Executing commands natively with WMI and DCOM

- Create a process on a remote host using [`wmic`](https://learn.microsoft.com/en-us/windows/win32/wmisdk/wmic):

```powershell
wmic /node:10.10.11.5 /user:example\jdoe /password:'passwd123' process call create "cmd.exe /c whoami > C:\Windows\Temp\out.txt"
```

| Option | Description |
| :--- | :--- |
| `/node:` | Target IP address or computer name. |
| `/user:` | Username for remote authentication (`domain\user`). |
| `/password:` | Password for authentication. |
| `process call create` | Call the `Create` method on the `Win32_Process` class to launch a process. |

- Configure DCOM session options in PowerShell:

```powershell
$opt = New-CimSessionOption -Protocol DCOM
```

- Create a CIM session to the remote host:

```powershell
$session = New-CimSession -ComputerName 10.10.11.5 -Credential $cred -SessionOption $opt
```

- Create a process on a remote host using `Invoke-CimMethod`:

```powershell
Invoke-CimMethod -CimSession $session -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine = 'cmd.exe /c whoami > C:\Windows\Temp\out.txt'}
```

| Option | Description |
| :--- | :--- |
| `-ComputerName` | Remote computer name or IP address. |
| `-Credential` | `PSCredential` object for remote authentication. |
| `-SessionOption` | Session options object created by `New-CimSessionOption` (e.g., specifying `-Protocol DCOM`). |
| `-CimSession` | Active CIM session object to run the method against. |
| `-ClassName` | CIM class name (`Win32_Process`). |
| `-MethodName` | Method to invoke on the CIM class (`Create`). |
| `-Arguments` | Hashtable containing the named arguments passed to the method (e.g., `@{CommandLine = '...'}`). |

- Instantiate the `MMC20.Application` DCOM object on a remote host via PowerShell:

```powershell
$dcom = [Activator]::CreateInstance([type]::GetTypeFromProgID("MMC20.Application", "10.10.11.5"))
```

- Execute a command using the `MMC20.Application` DCOM object:

```powershell
$dcom.Document.ActiveView.ExecuteShellCommand("cmd.exe", $null, "/c whoami > C:\Windows\Temp\out.txt", "7")
```

- Instantiate the `ShellWindows` DCOM object on a remote host:

```powershell
$dcom = [Activator]::CreateInstance([type]::GetTypeFromProgID("ShellWindows", "10.10.11.5"))
```

- Execute a command using the `ShellWindows` DCOM object:

```powershell
$dcom.Item().Document.Application.ShellExecute("cmd.exe", "/c whoami > C:\Windows\Temp\out.txt", "C:\Windows\System32", "open", 0)
```

## Scheduling tasks with `atexec`

>The **Task Scheduler service** registers and runs programs on a defined schedule or in response to system events, and exposes RPC interfaces that let a remote client create and run those tasks.

- The service is reached over RPC through the `\pipe\atsvc` named pipe (TCP ports `135` and `445`). Older systems use the `ITaskScheduler` interface (Windows Server 2003); Windows Vista and later use `ITaskService`.
- A task runs under the principal configured in its definition, so a task registered to run as `SYSTEM` executes with full local privileges regardless of the invoking user's context.

>[!note] Remote task creation requires administrative access rights on the target host.

### Executing commands with `atexec.py`

- `atexec.py` creates a temporary scheduled task, runs the specified command, retrieves standard output via SMB, and removes the task upon completion.

- Authenticate using a password and execute a command:

```bash
atexec.py example.com/jdoe:'passwd123'@10.10.11.5 'whoami /all'
```

- Authenticate using an NT hash ([[Pass-the-Hash]]):

```bash
atexec.py -hashes :2b576acfd5e0c865136732c44b49b6b1 example.com/jdoe@10.10.11.5 'ipconfig /all'
```

- Authenticate using a Kerberos ticket from the credential cache (specified by `KRB5CCNAME`):

```bash
atexec.py -k -no-pass example.com/jdoe@dc01.example.com 'whoami /priv'
```

| Option | Description |
| :--- | :--- |
| `command` | Command to execute inside the scheduled task. |
| `-hashes` | NT hash to use for authentication (Pass-the-Hash); format: `LM_hash:NT_hash`. |
| `-no-pass` | Suppress the password prompt (useful for Kerberos authentication). |
| `-k` | Use Kerberos credentials from a credential cache (`KRB5CCNAME`). |
| `-dc-ip` | IP address of the Domain Controller for Kerberos ticket resolution. |
| `-port` | Destination SMB port (default `445`). |
| `-codec` | Set the encoding used to read output. |

### Scheduling remote tasks natively on Windows

- Use [`schtasks`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks) to create a remote scheduled task configured to execute as `SYSTEM`:

```powershell
schtasks /create /s 10.10.11.5 /u example\jdoe /p 'passwd123' /ru "SYSTEM" /tn "AuditJob" /tr "cmd.exe /c whoami > C:\Windows\Temp\out.txt" /sc once /st 00:00
```

- Trigger the scheduled task on demand:

```powershell
schtasks /run /s 10.10.11.5 /u example\jdoe /p 'passwd123' /tn "AuditJob"
```

- Query the status and configuration of the scheduled task:

```powershell
schtasks /query /s 10.10.11.5 /u example\jdoe /p 'passwd123' /tn "AuditJob" /fo list /v
```

- Remove the scheduled task:

```powershell
schtasks /delete /s 10.10.11.5 /u example\jdoe /p 'passwd123' /tn "AuditJob" /f
```

| Option | Description |
| :--- | :--- |
| `/s` | Name or IP address of the remote computer. |
| `/u` | User account context for running the command (`domain\user`). |
| `/p` | Password for the given user account. |
| `/create` | Create a new scheduled task. |
| `/run` | Run a scheduled task immediately. |
| `/query` | Display scheduled tasks on the target machine. |
| `/delete` | Delete the specified scheduled task. |
| `/tn` | Unique name of the scheduled task. |
| `/tr` | Program or command line that the task executes. |
| `/ru` | User account under which the task runs (e.g., `"SYSTEM"`). |
| `/rp` | Password for the task run-as user account. |
| `/sc` | Schedule frequency (`MINUTE`, `HOURLY`, `DAILY`, `ONCE`, `ONSTART`, `ONLOGON`). |
| `/st` | Task start time in `HH:mm` format. |
| `/f` | Force task creation or deletion without interactive confirmation prompts. |


## RDP

>[!note] See [[Connecting via RDP]] and [[RDP]].
## MSSQL instances

>**Microsoft SQL Server (MSSQL)** is a relational database management system (RDBMS) developed by Microsoft. Clients communicate with SQL Server using the **Tabular Data Stream (TDS)** application-layer protocol.

- The default instance listens on TCP port `1433`. Named instances are located through the SQL Server Browser service, which listens on UDP port `1434`.

- SQL Server supports two authentication modes: SQL authentication (local SQL logins such as `sa`) and Windows authentication (in domain environments, using Kerberos or NTLM).
- The [`xp_cmdshell`](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/xp-cmdshell-transact-sql?view=sql-server-ver17) extended stored procedure runs OS commands under the security context associated with SQL Server (normally the SQL Server service account, or a configured proxy account for non-sysadmin users). It is disabled by default and must be enabled before use.

>[!note] Members of the **`sysadmin`** fixed server role can execute `xp_cmdshell` instructions once it's enabled. To execute first time after `xp_cmdshell` has been enabled, you need the `CONTORL SERVER` permission.

>[!note] See [`xp_cmdshell (Transact-SQL) — Microsoft Learn`](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/xp-cmdshell-transact-sql?view=sql-server-ver17).
### Interacting with `mssqlclient.py`

- To execute commands remotely using `xp_cmdshell`, you can use Impacket's [`mssqlclient.py`](https://github.com/fortra/impacket/blob/master/examples/mssqlclient.py).

---

- Authenticate using local SQL Server credentials (`sa`):

```bash
mssqlclient.py sa:'passwd123'@10.10.11.5
```

- Authenticate using Windows domain credentials:

```bash
mssqlclient.py -windows-auth example.com/jdoe:'passwd123'@10.10.11.5
```

- Authenticate using an NT hash ([[Pass-the-Hash]]):

```bash
mssqlclient.py -hashes :2b576acfd5e0c865136732c44b49b6b1 -windows-auth example.com/jdoe@10.10.11.5
```

- Authenticate using a Kerberos ticket from the credential cache (specified by `KRB5CCNAME`):

```bash
mssqlclient.py -k -no-pass -windows-auth example.com/jdoe@dc01.example.com
```

| Option | Description                                                                                |
| :-------------- | :----------------------------------------------------------------------------------------- |
| `-windows-auth` | Use Windows/Kerberos domain authentication instead of standard SQL Server authentication.  |
| `-hashes` | NT hash to use for authentication (Pass-the-Hash); format: `LM_hash:NT_hash`.             |
| `-no-pass` | Suppress the password prompt when using Kerberos authentication.                           |
| `-k` | Use Kerberos credentials from a credential cache (`KRB5CCNAME`).                           |
| `-port` | Destination SQL Server listening port (default `1433`).                                    |
| `-db` | Connect directly to the specified database instance.                                       |
| `-file` | Execute SQL queries from a local file.                                                     |
| `-dc-ip` | IP address of the Domain Controller for Kerberos ticket resolution.                        |

- Enable `xp_cmdshell` inside the interactive `mssqlclient.py` shell:

```sql
enable_xp_cmdshell
```

- Execute operating system commands inside the interactive `mssqlclient.py` shell:

```sql
xp_cmdshell whoami /all
```

### Executing commands with NetExec MSSQL

- [`NetExec`](https://github.com/Pennyw0rth/NetExec) can be used to execute commands remotely via `xp_cmdshell`.

---

- Execute operating system commands via the `xp_cmdshell` module:

```bash
netexec mssql 10.10.11.5 -u jdoe -p 'passwd123' -M xp_cmdshell -o CMD='whoami /all'
```

- Query the SQL Server version and configuration directly:

```bash
netexec mssql 10.10.11.5 -u jdoe -p 'passwd123' -q 'SELECT @@VERSION;'
```

- Authenticate using local SQL Server accounts:

```bash
netexec mssql 10.10.11.5 -u sa -p 'passwd123' --local-auth -q 'SELECT SYSTEM_USER;'
```

| Option | Description |
| :--- | :--- |
| `-u`, `--username` | Username or file containing usernames for authentication. |
| `-p`, `--password` | Plaintext password or file containing passwords. |
| `-H`, `--hash` | NT hash to use for authentication (Pass-the-Hash); format: `LM_hash:NT_hash`. |
| `-d` | Domain for Windows authentication. |
| `--local-auth` | Authenticate using local SQL Server accounts instead of domain accounts. |
| `-q` | Execute a custom SQL query and return results. |
| `-M` | NetExec module to load (e.g., `xp_cmdshell`). |
| `-o` | Options to pass to the loaded module (e.g., `CMD='whoami /all'`). |
| `-k`, `--kerberos` | Enable Kerberos authentication. |
| `--use-kcache` | Use Kerberos credentials from a credential cache (`KRB5CCNAME`). |

### Interacting with sqlcmd on Windows

- [`sqlcmd`](https://learn.microsoft.com/en-us/sql/tools/sqlcmd/sqlcmd-utility) is the command-line client for running Transact-SQL statements against SQL Server.

---

- Connect with Windows authentication and run a query:

```powershell
sqlcmd -S 10.10.11.5 -E -Q "SELECT @@SERVERNAME;"
```

- Enable `xp_cmdshell` and execute operating system commands:

```powershell
sqlcmd -S 10.10.11.5 -U sa -P 'passwd123' -Q "EXEC sp_configure 'show advanced options', 1; RECONFIGURE; EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE; EXEC xp_cmdshell 'whoami /all';"
```

| Option | Description |
| :--- | :--- |
| `-S` | Target SQL Server instance (`<server>[\<instance>]` or `<server>,<port>`). |
| `-U` | SQL Server login ID for SQL authentication. |
| `-P` | Password for the login ID. |
| `-E` | Use a trusted Windows connection (Windows Authentication) instead of SQL authentication. |
| `-d` | Initial database to use. |
| `-Q` | Execute a query and immediately exit `sqlcmd`. |
| `-q` | Execute a query and remain in the interactive `sqlcmd` prompt. |
| `-i` | Input file containing SQL batches to execute. |
| `-o` | Output file to capture query output. |

## SSH

>**Secure Shell (SSH)** is a cryptographic network protocol for operating network services securely over an unsecured network, most commonly for remote shell access and command execution.

- SSH listens on TCP port `22`. Windows 10, Windows 11, and Windows Server 2019+ ship a native [OpenSSH](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_overview) server (`sshd`).
- The session runs under the authenticated user's context; the default shell (`cmd.exe` or `powershell.exe`) is set through the `DefaultShell` registry value.
- Beyond interactive shells, SSH can tunnel arbitrary TCP traffic through local, remote, and dynamic (SOCKS) port forwards.

>[!note] See [[SSH port forwarding]] for SSH tunneling and port forwarding; see [[Plink]] for an older Windows SSH client.

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

- Forward a local port through the SSH session:

```bash
ssh -L 8443:127.0.0.1:443 -N -f jdoe@10.10.11.5
```

- Create a dynamic SOCKS proxy through the SSH session:

```bash
ssh -D 1080 -N -f jdoe@10.10.11.5
```

| Option | Description |
| :--- | :--- |
| `-i` | Identity file (private key) for public key authentication. |
| `-p` | Destination port on the remote host (default `22`). |
| `-l` | User to log in as on the remote machine. |
| `-L` | Local port forward (`[bind_address:]port:host:hostport`). |
| `-R` | Remote port forward (`[bind_address:]port:host:hostport`). |
| `-D` | Dynamic SOCKS proxy port on the local host. |
| `-N` | Do not execute a remote command (useful for port forwarding only). |
| `-f` | Request SSH to go to the background just before command execution. |
| `-o` | SSH configuration option in `Key=Value` format (e.g., `-o StrictHostKeyChecking=no`). |

## References and further reading

- [`Windows Remote Management — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/winrm/portal)
- [`WS-Management Protocol — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/winrm/ws-management-protocol)
- [`Windows Management Instrumentation — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/wmisdk/wmi-start-page)
- [`Remote Desktop Protocol — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/remote/remote-desktop-services/welcome-to-rds)
- [`[MS-DCOM]: Distributed Component Object Model (DCOM) Remote Protocol — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-dcom/4a893f3d-bd29-48cd-9f43-d9777a4415b0)
- [`OpenSSH for Windows Overview — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_overview)
- [`Microsoft SQL Server Technical Documentation — Microsoft Learn`](https://learn.microsoft.com/en-us/sql/sql-server/)
- [`xfreerdp — TLDR pages`](https://www.cheat-sheets.org/project/tldr/command/xfreerdp/os/linux/)

- TODO:
	- I need requirements and use cases for tools 
