---
created: 2026-07-22
updated: 2026-09-20
tags:
  - Windows
  - Windows_PrivEsc
status: complete
---

> [!abstract]+ **Scope**: Privilege escalation through membership in the `Print Operators` group.

- [ ] Confirm membership in the `Print Operators` group (`whoami /groups` or `net user %USERNAME% /domain`).
- [ ] Check active token status for `SeLoadDriverPrivilege` (`whoami /priv`).
- [ ] If `SeLoadDriverPrivilege` is stripped by UAC filtering, obtain an elevated process via UAC bypass or administrative prompt.
- [ ] Register and load a vulnerable kernel driver (`Capcom.sys` or `RTCore64.sys`) using `EopLoadDriver.exe`.
- [ ] Exploit the vulnerable driver to achieve `NT AUTHORITY\SYSTEM` code execution.
---
## `Print Operators`

>The **`Print Operators`** group is a built-in Windows security group that allows members to **manage printers, driver installations, and printer shares** on domain controllers and workstations.

- This capability is granted through **`SeLoadDriverPrivilege`**, which allows a process to dynamically load and unload kernel-mode device drivers (`.sys`) into kernel memory.
- Kernel drivers execute in kernel mode (Ring `0`) with unrestricted access to virtual memory and kernel structures.
- To take advantage of `SeLoadDriverPrivilege`, you can load a signed vulnerable kernel driver (such as `Capcom.sys` or `RTCore64.sys`) using `EopLoadDriver.exe` and exploit it to steal `SYSTEM` tokens or disable LSASS process protection.

> [!note] See [[SeLoadDriverPrivilege]] for privilege escalation.

## Checking group membership

- Check whether your current user is a member of `Print Operators`:

```powershell
whoami /groups
```

```cmd
net user %USERNAME% /domain
```

```powershell
Get-LocalGroupMember -Group "Print Operators"
```

- Verify assigned privileges:

```powershell
whoami /priv
```

>[!note] Even if the privilege is present in the output but marked `Disabled`, Windows won't consider it during access checks. You need to enable the privilege first before using it. See [[SeLoadDriverPrivilege#Enumerating and enabling privileges]].

## References and further reading

- [`Print Operators — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/appendix-security-groups-in-active-directory#print-operators)
- [`Load and unload device drivers - security policy setting — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/load-and-unload-device-drivers)
- [`EopLoadDriver — GitHub`](https://github.com/TarlogicSecurity/EoPLoadDriver)
- [`Abusing SeLoadDriverPrivilege for privilege escalation — TarlogicSecurity`](https://www.tarlogic.com/blog/abusing-seloaddriverprivilege-for-privilege-escalation/)
- [`Living off the Land Drivers (LOLDrivers)`](https://www.loldrivers.io/)
