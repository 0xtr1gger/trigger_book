---
created: 20-02-2026
---
## Windows registry

>The **[Windows Registry](https://learn.microsoft.com/en-us/windows/win32/sysinfo/structure-of-the-registry)** is a **hierarchical database** used to store critical system data, such as operating system configuration, hardware settings, user preferences, installed application settings, security policies, and system startup configuration.

>[!note] The Registry replaces old `.ini` files used in early Windows versions, such as 3.x and MS-DOS. Simply speaking, it is a centralized configuration store.

- The Registry stores both system-wide and user-specific data.
- You can view and edit the Registry using [`regedit.exe`](https://ss64.com/nt/regedit.html) (Registry Editor) and [`reg`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/reg) CMD commands (though it's not recommended to do that directly).
- Every action that modifies system behavior — installing software, creating user accounts, configuring services, establishing persistence — leaves traces in the Registry.
- It acts as a central nervous system for Windows, and controls almost every aspect of system behavior: from boot configuration to application settings.

>[!note] When the Registry is read
>  Configuration data in the Registry is read four principal times:
> - During the initial boot process, by the bootloader reads configuration data and the list of boot device drivers to load into memory before initializing the kernel.
> - During the kernel boot process, the kernel reads settings that specify which device drivers to load and how various system elements (e.g., the memory manager and process manager) configure themselves and tune system behavior.
> - During logon, Explorer and other Windows components read pre-user preferences from the registry, including network drive-letter mappings, desktop wallpapers, screen saver settings, menu behavior, icon placement, and which startup programs to launch and which files were most recently accessed.
> - During their startup, applications read system-wide settings (e.g., a list of optionally installed components and licensing data, per-user settings, etc.).
> 
> However, the registry can be read at other times as well, such as in response to a modification of a registry value or key. 
> Although the registry provides asynchronous callbacks that are the preferred way to receive change notifications, some applications constantly monitor their configuration settings in the registry through polling and automatically take updated settings into account. In general, however, on an idle system there should be no registry activity and such applications violate best practices.
## Keys, subkeys, and values

The data in the Registry is structured in a **tree format**, where each node in the tree is called a **key**, and each key can contain **subkeys** and data entries called **values**:

- **Keys**
	- **Keys** are container objects, similar to folders in a filesystem. 
	- Each key can contain subkeys (child keys) and values.
	- A key can have any number of values, and the values can be in any form.
	- The name of each subkey is unique with respect to the key that is immediately above it in the hierarchy. Key names are not case-sensitive and can contain any printable characters except the backslash (`\`).
	- The name of each subkey must be unique within its parent key.
	- Keys are identified by their full path, starting from a root key (e.g., `HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows`).
	- A Registry tree can be **512 levels deep**, through creating more than 32 levels at once via API is not supported.

>[!example]+ Example of a key path
>```
>HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Run
>```
>This key control programs that start automatically at boot.


- **Values**
	- **Values** are data entries stored within keys.
	- Each value consists of three components:
		- **Value name:** Identifies the setting (e.g., `ImagePath`, `Start`, `AutoAdminLogon`).
		- **Data type:** Defines the format of the data (e.g., string, integer, binary, etc.).
		- **Data:** The actual configuration information.

### Registry value types

| Type                      | Description                                                                                                                                                                                                                                                                                                                                                                        |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `REG_NONE`                | No defined value type.                                                                                                                                                                                                                                                                                                                                                             |
| `REG_SZ`                  | A null-terminated fixed-length string (Unicode or ANSI).                                                                                                                                                                                                                                                                                                                           |
| `REG_EXPAND_SZ`           | A null-terminated variable-length string that can reference environment variables (e.g., `"%PATH%"`, `"%SystemRoot%\System32"`).<br>Variables are expanded when read.                                                                                                                                                                                                              |
| `REG_BINARY`              | Arbitrary-length binary data.                                                                                                                                                                                                                                                                                                                                                      |
| `REG_DWORD`               | A 32-bit number.                                                                                                                                                                                                                                                                                                                                                                   |
| `REG_DWORD_LITTLE_ENDIAN` | A 32-bit number in [little-endian format](https://learn.microsoft.com/en-us/windows/win32/sysinfo/registry-value-types#byte-formats).                                                                                                                                                                                                                                              |
| `REG_QWORD`               | A 64-bit number.                                                                                                                                                                                                                                                                                                                                                                   |
| `REG_QWORD_LITTLE_ENDIAN` | A 64-bit number in little-endian format.                                                                                                                                                                                                                                                                                                                                           |
| `REG_DWORD_BIG_ENDIAN`    | A 32-bit number in [big-endian format](https://learn.microsoft.com/en-us/windows/win32/sysinfo/registry-value-types#byte-formats). <br>Some UNIX systems support big-endian architectures.                                                                                                                                                                                         |
| `REG_LINK`                | Unicode symbolic link; a reference to another key.<br>Symbolic link to another Registry key (internal use). <br>A null-terminated Unicode string that contains the target path of a symbolic link that was created by calling the [`RegCreateKeyEx`](https://learn.microsoft.com/en-us/windows/win32/api/Winreg/nf-winreg-regcreatekeyexa) function with `REG_OPTION_CREATE_LINK`. |
| `REG_MULTI_SZ`            | A sequence of null-terminated strings, terminated by an empty string `\0` (e.g., `String1\0String2\0String3\0LastString\0\0`, where the first `\0` terminates the first string, the second-from-last `\0` terminates the last string, and the final `\0` terminates the sequence).                                                                                                 |


>[!example]+ `REG_LINK` example
>if `\Root1\Link` has a `REG_LINK` value of `\Root2\RegKey` and `RegKey` contains the value `RegValue`, then there are two paths that identify `RegValue`:
>-  `\Root1\Link\RegValue` 
>- `\Root2\RegKey\RegValue`

>[!note] Windows is designed to run on little-endian computer architectures, so `REG_DWORD_LITTLE_ENDIAN` and `REG_QWORD_LITTLE_ENDIAN` are defined as `REG_DWORD` and `REG_QWORD` in the Windows header files, respectively.

>[!important] `REG_SZ` and `REG_DWORD` are types where credentials or service configurations are most commonly stored.

>[!note] See [`Registry value types — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/sysinfo/registry-value-types).

## Registry Hives

>A **[Registry Hive](https://learn.microsoft.com/en-us/windows/win32/sysinfo/registry-hives)**, also called a **root key**, is a top-level logical container within the Windows registry that organizes configuration data into structure namespaces.

- Each hive is backed by one or more physical files on disk, and is loaded into memory by the Windows kernel at boot or user logon
- Hives are exposed to userland as **handles (`HKEY`)**.

>[!note] The `H` in `HKEY` stands for **handle** — these are predefined handles to registry key objects managed by the Windows Object Manager.

- Most system-wide hive files are stored under:

```powershell
C:\Windows\System32\Config
```

| Root key              | Abbreviation |
| --------------------- | ------------ |
| `HKEY_CLASSES_ROOT`   | HKCR         |
| `HKEY_CURRENT_USER`   | HKCU         |
| `HKEY_USERS`          | HKU          |
| `HKEY_LOCAL_MACHINE`  | HKLM         |
| `HKEY_CURRENT_CONFIG` | HKCC         |

- **`HKEY_LOCAL_MACHINE` (HKLM)**
	- Stores **system-wide configuration** (applies to all users), such as hardware settings, installed software, drivers, system services, and security policies.
	- This is probable the most critical hive for penetration testers.

>[!important] `HKLM\SAM` and `HKLM\SECURITY` store **hashes of user credentials** and **LSA secrets**.

- **`HKEY_CURRENT_USER` (HKCU)**
	- Stores configuration specific to the **currently logged-in user**, including desktop preferences, environment variables, network mappings, and application settings.
	- HKCU is not a standalone hive, but a **symbolic link** (`REG_LINK`) to the active user's subkey in `HKEY_Users\<user_SID>`.
	- It is dynamically loaded from the user's `NTUSER.DAT` file (`%USERPROFILE%\NTUSER.DAT`) at login.
	- Any changes to HKCU are written back to `NTUSER.DAT` during the session or at logout.

- **`HKEY_USERS` (HKU)**
	- Contains subkeys for each loaded user profiles. Each subkey is named after the user's SID (e.g., `HKEY_USERS\S-1-5-21-<domain>-<RID>`).
	- Special SIDs like `S-1-5-18` (`SYSTEM`), `S-1-5-19` (`LOCAL SERVICE`), and `S-1-5-20` (`NETWORK SERVICE`) are also here (see [[Windows_users_and_groups]]).

- **`HKEY_CLASSES_ROOT` (HKCR)**
	- Contains file extension associations (which application opens `.txt`, `.exe`, etc.), registered COM objects, OLE configuration, protocol handles, CLSIDs, etc.
	- This is a merged view of:
		- `HKEY_LOCAL_MACHINE\SOFTWARE\Classes` (system-wide settings)
		- `HKEY_CURRENT_USER\SOFTWARE\Classes` (user-specific overrides)
	- User-specific settings take precedence over system-wide for the current user.

- **`HKEY_CURRENT_CONFIG` (HKCC)**
	- Stores information about the **current hardware profile** (e.g., display settings, device configurations, etc.).
	- HKCC is a **symbolic link** to `HKLM\SYSTEM\CurrentControlSet\Hardware Profiles\Current`.
	- It is dynamically generated at boot and doesn't have a separate backing file.

>[!note]+ Version-specific root keys
> - `HKEY_PERFORMANCE_DATA` is present to Windows NT, but invisible in the Windows Registry Editor.
> - `HKEY_DYN_DATA` is specific to Windows 9x, and visible in the Windows Registry Editor.

## Backing files

### `HKEY_LOCAL_MACHINE` (HKLM)

`HKLM` is backed primarily by hive files stored in:

```powershell
C:\Windows\System32\Config
```

Important files include:

- `SYSTEM` (`HKEY_LOCAL_MACHINE\SYSTEM`)
	- Contains boot configuration, control sets (`ControlSet001`, `ControlSet002`, etc.), services, drivers, kernel configuration, etc.

```powershell
C:\Windows\System32\Config\SYSTEM
```

- `SOFTWARE` (`HKEY_LOCAL_MACHINE\SOFTWARE`)
	- Contains configuration for system-wide installed software (such as PowerShell and Windows Defender), COM registrations, etc.

```powershell
C:\Windows\System32\Config\SOFTWARE
```

- `SAM` (`HKEY_LOCAL_MACHINE\SAM`)
	- **Security Account Manager (SAM)**. Stores local user accounts, group membership, password hashes (NTLM), RID mappings, etc.
	- Loaded by the LSASS (Local Security Authority Subsystem Service) at boot.
	- Protected; not readable by regular administrators while the OS is running. Access is restricted to `SYSTEM`.

```powershell
C:\Windows\System32\Config\SAM
```

- `SECURITY` (`HKEY_LOCAL_MACHINE\SECURITY`)
	- Contains LSA policies and secrets, cached domain credentials, service account credentials, Kerberos secrets, trust relationships (AD), etc.

```powershell
C:\Windows\System32\Config\SECURITY
```

- `HARDWARE` (`HKEY_LOCAL_MACHINE\HARDWARE`)
	- Hardware configuration dynamically generated at boot (e.g., ACPI info, CPU info, device mappings, BIOS data, etc.).
	- **Doesn't have a persistent backing file and exists only in memory.**
### `HKEY_USERS` and `HKEY_CURRENT_USER`

>`HKEY_USERS` contains **all loaded user profile hives**. 

- Each user profile has its own registry hive file(s) stored in the user's profile directory:

```powershell
C:\Users\<username>\
```

Unlike HKLM (machine-wide), these are **per-user hives loaded at logon**.

Important files include:

- `NTUSER.DAT` (`HKEY_USERS\<user_SID>`)
	- The main per-user registry hive; contains user-specific settings, desktop configuration, environment variables, user-level run keys, Explorer settings, per-user COM registrations, PowerShell history configuration, etc.
	- When a user logs in, Windows loads `NTUSER.DAT` into memory and mounts it under `HKEY_USERS\<user_SID>`, and then creates a symbolic link to `HKEY_CURRENT_USER`.
	- When the user logs out, the hive is written back to disk.

```powershell
C:\Users\<username>\NTUSER.DAT
```

```powershell
HKCU

   ↓   (symbolic link)
   
HKU\<current_user_SID>

   ↓   (backed by)
   
NTUSER.DAT
```


- `USRCLASS.DAT` (`HKEY_USERS\<SID>_classes`)
	- Contains per-user COM registrations, file associations, shell extensions, thumbnail handler mappings, etc. This file works together with `NTUSER.DAT`.

```powershell
C:\Users\<username>\AppData\Local\Microsoft\Windows\USRCLASS.DAT
```

- `DEFAULT` (`HKEY_USERS\.DEFAULT`)
	- The `SYSTEM` account's user hive; used before login screen by Winlogon

```powershell
C:\Windows\System32\Config\DEFAULT
```
## Windows Registry Editor

>**Windows Registry Editor (`regedit.exe`)** is a built-in tool that allows users to view, edit, create, or delete entries in the Windows Registry.

![](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/49/regedit.png)

![[registry_hives.png]]


## References and further reading

- [`Windows Registry — Wikipedia`](https://en.wikipedia.org/wiki/Windows_Registry)

- [`Registsry Hives — Microsoft Windows`](https://learn.microsoft.com/en-us/windows/win32/sysinfo/registry-hives)


