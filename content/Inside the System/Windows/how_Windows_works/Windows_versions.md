---
created: 01-02-2026
---
## What is Windows

>**Windows is a family of proprietary operating systems developed by Microsoft**, primarily designed for personal computers and enterprise environments.
## Windows versions and editions

When talking about different kinds of Windows, it's important to understand the distinction between **Windows version** and **edition**.

>**Windows Version** refers to the specific build or update level of Windows, identified by a numerical label, e.g., `Windows 10 Version 22H2` or `Windows 11 24H2`.

>**Windows Edition** refers to a specific variant of the Windows operating system, tailored for different user needs, markets, or device types. Each edition offers a distinct set of features, licensing terms, and pricing.

### Windows versions

Below are major Windows operating systems and associated version numbers:

| NT version | Client OS names                     | Server OS names                     |
| ---------- | ----------------------------------- | ----------------------------------- |
| `3.1`      | Windows NT 3.1                      | Windows NT 3.1 Server               |
| `3.5`      | Windows NT 3.5                      | Windows NT 3.5 Server               |
| `3.51`     | Windows NT 3.51                     | Windows NT 3.51 Server              |
| `4.0`      | Windows NT 4.0 Workstation          | Windows NT 4.0 Server               |
| `5.0`      | Windows 2000 Professional           | Windows 2000 Server                 |
| `5.1`      | Windows XP (Home, Pro)              | —                                   |
| `5.2`      | Windows XP x64, XP Professional x64 | Windows Server 2003, Server 2003 R2 |
| `6.0`      | Windows Vista                       | Windows Server 2008                 |
| `6.1`      | Windows 7                           | Windows Server 2008 R2              |
| `6.2`      | Windows 8                           | Windows Server 2012                 |
| `6.3`      | Windows 8.1                         | Windows Server 2012 R2              |
| `10.0`     | Windows 10                          | Windows Server 2016                 |
| `10.0`     | Windows 10 (later releases)         | Windows Server 2019                 |
| `10.0`     | Windows 10 (later releases)         | Windows Server 2022                 |
| `10.0`     | **Windows 11**                      | —                                   |
- Yes, Windows 11 is still NT `10.0`.
- Windows jumped from `6.3` straight to `10.0`. There's no NT `7.0`, `8.0`, or `9.0`. 
- Windows 11 is best though as Windows 10 with stricter hardware policy and a new shell. That's it. Is uses **the same NT version (`10.0`), kernel family, driver model, and Win32 ABI**.
### Windows editions

>[!important] All desktop Windows editions of the same version share the same kernel and core OS.

Most prominent editions are:
- Windows Home
- Windows Pro
- Windows Pro for Workstations
- Windows Enterprise
- Windows Education
- Windows IoT
- Windows Server Standard
- Windows Server Datacenter

We will go through Windows 10 editions as an example.

### Windows 10 editions

**Every Windows 10 desktop edition** has:

- NT 10.0 kernel
- Win32 + UWP application support
- NTFS (full feature set)
- Windows Defender (AV + firewall)
- Windows Update (consumer channel)
- DirectX 12
- PowerShell
- WSL / WSL2 (supported technically)
- Same driver model (WDDM)

| Edition                               | Features                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Windows 10 Home<br>(baseline edition) | - Local & Microsoft accounts<br>- Windows Defender (basic security)<br>- Windows Update (automatic)<br>- Windows Hello (biometrics)<br>- Device encryption (limited BitLocker-lite)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Windows 10 Pro                        | - Everything in Home plus:<br>- Group Policy Editor (`gpedit.msc`)<br>- Local Security Policy<br>- Domain Join (Active Directory/Entra ID)<br>- Enterprise State Roaming (basic)<br>- BitLocker (full disk encryption)<br>- BitLocker To Go (removable media)<br>- Windows Information Protection (basic)<br>- Hyper-V (Type-1 hypervisor)<br>- Windows Sandbox<br>- Remote Desktop (host)<br>- Windows Update for Business<br>- Deferred feature updates                                                                                                                                                                                                            |
| Windows 10 Pro for Workstations       | - Everything in Pro **plus**:<br>- ReFS support (non-boot volumes)<br>- Persistent memory (NVDIMM-N)<br>- SMB Direct (RDMA)<br>- Support for up to 4 CPUs and up to 6 TB RAM                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Windows 10 Enterprise                 | - Everything in Pro **plus**:<br>- AppLocker<br>- Windows Defender Application Control (WDAC)<br>- Credential Guard/Remote Credential Guard<br>- Advanced Exploit Guard<br>- Attack Surface Reduction rules<br>- Device Guard<br>- Secure Boot enforcement<br>- Advanced Entra ID integration<br>- Conditional Access<br>- Single sign-on across enterprise apps<br>- Microsoft Endpoint Manager (Intune)<br>- Advanced Group Policy<br>- Enterprise provisioning packages<br>- Enterprise analytics & telemetry control<br>- LTSC (Long-Term Servicing Channel) option<br>- Feature update deferral for years<br>- Reduced consumer features (depending on channel) |
## References and further reading

- [`List of Microsoft Windows versions — Wikipedia`](https://en.wikipedia.org/wiki/List_of_Microsoft_Windows_versions)
- [`Microsoft Windows version history — Wikipedia`](https://en.wikipedia.org/wiki/Microsoft_Windows_version_history)
- [`List of Microsoft Windows versions — Windows Fandom`](https://microsoft.fandom.com/wiki/List_of_Microsoft_Windows_versions)
