---
created: 2026-07-22
tags:
  - Windows
  - Windows_PrivEsc
status: draft
---

## Hyper-V Administrators

![[🛠️ Windows groups#`Hyper-V Administrators`]]

## Abusing Hyper-V Administrators for privilege escalation

It is also well documented on this [blog](https://decoder.cloud/2020/01/20/from-hyper-v-admin-to-system/), that upon deleting a virtual machine, `vmms.exe` attempts to restore the original file permissions on the corresponding `.vhdx` file and does so as `NT AUTHORITY\SYSTEM`, without impersonating the user. We can delete the `.vhdx` file and create a native hard link to point this file to a protected SYSTEM file, which we will have full permissions to.

If the operating system is vulnerable to [CVE-2018-0952](https://www.tenable.com/cve/CVE-2018-0952) or [CVE-2019-0841](https://www.tenable.com/cve/CVE-2019-0841), we can leverage this to gain SYSTEM privileges. Otherwise, we can try to take advantage of an application on the server that has installed a service running in the context of SYSTEM, which is startable by unprivileged users.

>[!note] See [`From Hyper-V Admin to SYSTEM — Decoder's Blog`](https://decoder.cloud/2020/01/20/from-hyper-v-admin-to-system/).


#### Target File

An example of this is Firefox, which installs the `Mozilla Maintenance Service`. We can update [this exploit](https://raw.githubusercontent.com/decoder-it/Hyper-V-admin-EOP/master/hyperv-eop.ps1) (a proof-of-concept for NT hard link) to grant our current user full permissions on the file below:

        shellsession
`C:\Program Files (x86)\Mozilla Maintenance Service\maintenanceservice.exe`

#### Taking Ownership of the File

After running the PowerShell script, we should have full control of this file and can take ownership of it.

        cmd
`C:\htb> takeown /F C:\Program Files (x86)\Mozilla Maintenance Service\maintenanceservice.exe`

#### Starting the Mozilla Maintenance Service

Next, we can replace this file with a malicious `maintenanceservice.exe`, start the maintenance service, and get command execution as SYSTEM.

        cmd
`C:\htb> sc.exe start MozillaMaintenance`

Note: This vector has been mitigated by the March 2020 Windows security updates, which changed behavior relating to hard links.
## References and further reading

- [`From Hyper-V Admin to SYSTEM — Decoder's Blog`](https://decoder.cloud/2020/01/20/from-hyper-v-admin-to-system/).