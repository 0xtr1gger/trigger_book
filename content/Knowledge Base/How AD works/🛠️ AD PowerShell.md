---
created: 2026-07-28
updated: 2026-09-20
tags:
  - AD
status: draft
---
>[!tip] See [`ActiveDirectory Module — Microsoft Learn`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/?view=windowsserver2022-ps).

```powershell
Import-Module ActiveDirectory
```

## AD users

| Cmdlet             | Purpose                                              |
| ------------------ | ---------------------------------------------------- |
| `New-ADUser`       | Create a new AD user.                                |
| `Get-ADUser`       | Retrieve user objects.                               |
| `Set-ADUser`       | Modify an existing user.                             |
| `Remove-ADUser`    | Delete a user account.                               |
| `Search-ADAccount` | Search for accounts meeting specific criteria.       |
| `Remove-ADObject`  | Delete any AD object (less commonly used for users). |

### `New-ADUser`

- [`New-ADUser`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/new-aduser?view=windowsserver2022-ps) creates Active Directory users.

```powershell
New-ADUser
    [-Name] <String>
    [-SamAccountName <String>]
    [-UserPrincipalName <String>]
    [-GivenName <String>]
    [-Surname <String>]
    [-DisplayName <String>]
    [-Path <String>]
    [-AccountPassword <SecureString>]
    [-Enabled <Boolean>]
    [<CommonParameters>]
```

- Create `Jane Doe` in `OU=Users,DC=example,DC=com`:

```powershell
New-ADUser `
    -Name "Jane Doe" `
    -GivenName "Jane" `
    -Surname "Doe" `
    -DisplayName "Jane Doe" `
    -SamAccountName "jdoe" `
    -UserPrincipalName "j.doe@example.com" `
    -EmailAddress "j.doe@example.com" `
    -Path "OU=Users,DC=example,DC=com" `
    -AccountPassword (Read-Host -AsSecureString 'AccountPassword') `
    -Enabled $true `
    -ChangePasswordAtLogon $true
```

| Parameter            | Description                          | Example                                         |
| -------------------- | ------------------------------------ | ----------------------------------------------- |
| `-Name`              | Full object name (Common Name)       | `"Jane Doe"`                                    |
| `-SamAccountName`    | Legacy (pre-Windows 2000) logon name | `jdoe`                                          |
| `-UserPrincipalName` | Modern logon name (user@domain)      | `jdoe@example.com`                              |
| `-GivenName`         | First name                           | `Jane`                                          |
| `-Surname`           | Last name                            | `Doe`                                           |
| `-DisplayName`       | Display name                         | `"Jane Doe"`                                    |
| `-Path`              | Distinguished Name of the target OU  | `"OU=Users,DC=example,DC=com"`                  |
| `-AccountPassword`   | Initial password (`SecureString`)    | `(Read-Host -AsSecureString 'Password')`        |
| `-Enabled`           | Enables or disables the account      | `$true`                                         |
| `-Description`       | User description                     | `"Cybersecurity Department"`                    |
| `-EmailAddress`      | Email address                        | `"jane.doe@example.com"`                        |
| `-OfficePhone`       | Telephone number                     | `"111-2222"`                                    |
| `-Department`        | Department                           | `"Cybersecurity"`                               |
| `-Title`             | Job title                            | `"Security Engineer"`                           |
| `-Company`           | Company name                         | `"Example"`                                     |
| `-Manager`           | Distinguished Name of manager        | `"CN=John Doe,OU=Users,DC=example,DC=com"`      |
| `-ChangePasswordAtLogon` | Force password change at next logon | `$true`                                     |
| `-AccountNotDelegated`   | Account cannot be delegated        | `$true`                                     |
| `-PasswordNeverExpires`  | Password never expires             | `$true` (avoid in production)               |

### `Get-ADUser`

- [`Get-ADUser`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-aduser?view=windowsserver2022-ps) retrieves one or more user objects.

```powershell
Get-ADUser
    [-Identity] <ADUser>
    [-Properties <String[]>]
    [-Server <String>]
    [<CommonParameters>]
```

```powershell
Get-ADUser
    -Filter <String>
    [-SearchBase <String>]
    [-SearchScope <Base | OneLevel | Subtree>]
```

- Get a specific user:

```powershell
Get-ADUser jdoe
```

- Get specific properties:

```powershell
Get-ADUser jdoe -Properties Department,Title,EmailAddress
```

- Get all properties:

```powershell
Get-ADUser jdoe -Properties *
```

- Display selected attributes:

```powershell
Get-ADUser jdoe -Properties * |
Select-Object Name, SamAccountName, Enabled, Department, Title, LastLogonDate
```

#### Filtering 


```powershell
# All users
Get-ADUser -Filter *
```

```powershell
# Enabled users only
Get-ADUser -Filter 'Enabled -eq $true'
```

```powershell
# Users in a specific OU
Get-ADUser -Filter * -SearchBase "OU=Sales,DC=example,DC=com"
```

```powershell
# Users with a title
Get-ADUser -Filter 'Title -like "*Engineer*"'
```

```powershell
# Users created after a date
Get-ADUser -Filter 'Created -ge "2026-01-01"' -Properties Created
```

```powershell
# Users with expired passwords
Get-ADUser -Filter 'PasswordExpired -eq $true'
```

```powershell
# Users whose password never expires
Get-ADUser -Filter 'PasswordNeverExpires -eq $true'
```

```powershell
# Disabled users
Get-ADUser -Filter 'Enabled -eq $false'
```

```powershell
# Users last logged in before a date
$date = [DateTime]::UtcNow.AddDays(-90)
Get-ADUser -Filter 'LastLogonDate -lt $date' -Properties LastLogonDate
```

| Parameter      | Description                                      | Example                                |
| -------------- | ------------------------------------------------ | -------------------------------------- |
| `-Identity`    | SAM account name, DN, GUID, or SID               | `jdoe`, `CN=Jane Doe,...`, `S-1-5-21-...` |
| `-Filter`      | PowerShell Expression Language query              | `'Name -like "*admin*"'`               |
| `-LDAPFilter`  | Raw LDAP filter                                   | `"(objectCategory=person)"`            |
| `-SearchBase`  | DN to start the search from                       | `"OU=Users,DC=example,DC=com"`        |
| `-SearchScope` | Depth: `Base`, `OneLevel`, `Subtree`              | `Subtree`                              |
| `-Properties`  | Properties to return (default set is limited)     | `Department,Title`, `*` for all        |
| `-Server`      | Target DC (useful in multi-domain environments)   | `dc01.example.com`                     |

### Set-ADUser

[`Set-ADUser`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/set-aduser?view=windowsserver2022-ps) modifies an existing user object.

```powershell
Set-ADUser
    [-Identity] <ADUser>
    [-Description <String>]
    [-Department <String>]
    [-Title <String>]
    [-Manager <ADUser>]
    [-Office <String>]
    [-MobilePhone <String>]
    [-EmailAddress <String>]
    [-Enabled <Boolean>]
    [-PasswordNeverExpires <Boolean>]
    [-Add <Hashtable>]
    [-Remove <Hashtable>]
    [-Replace <Hashtable>]
    [-Clear <String[]>]
```

```powershell
# Update basic attributes
Set-ADUser jdoe -Title "Senior Security Engineer" -Department "Cybersecurity"

# Disable a user
Set-ADUser jdoe -Enabled $false

# Enable a user
Set-ADUser jdoe -Enabled $true

# Set manager by DN
Set-ADUser jdoe -Manager "CN=John Smith,OU=Managers,DC=example,DC=com"

# Replace arbitrary attributes
Set-ADUser jdoe -Replace @{extensionAttribute1="HR Transfer"; customAttribute="value"}

# Add a value to a multi-valued attribute
Set-ADUser jdoe -Add @{otherTelephone="555-1234"}

# Remove a value from a multi-valued attribute
Set-ADUser jdoe -Remove @{otherTelephone="555-1234"}

# Clear a single attribute
Set-ADUser jdoe -Clear "Description"
```

### Set-ADAccountPassword

[`Set-ADAccountPassword`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/set-adaccountpassword?view=windowsserver2022-ps) resets or changes an account password.

```powershell
Set-ADAccountPassword
    [-Identity] <ADAccount>
    [-Reset]
    [-NewPassword <SecureString>]
    [-OldPassword <SecureString>]
```

```powershell
# Reset password (admin does not need old password)
Set-ADAccountPassword -Identity jdoe -Reset `
    -NewPassword (ConvertTo-SecureString -AsPlainText "NewStr0ng!Pass" -Force)

# Interactive reset (prompts for new password)
Set-ADAccountPassword -Identity jdoe -Reset

# Change password (user must supply old password)
Set-ADAccountPassword -Identity jdoe `
    -OldPassword (ConvertTo-SecureString -AsPlainText "OldPass1!" -Force) `
    -NewPassword (ConvertTo-SecureString -AsPlainText "NewPass2@" -Force)
```

### Search-ADAccount

[`Search-ADAccount`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/search-adaccount?view=windowsserver2022-ps) finds accounts matching specific states.

```powershell
# All disabled users
Search-ADAccount -AccountDisabled -UsersOnly

# All locked-out users
Search-ADAccount -LockedOut

# All expired accounts
Search-ADAccount -AccountExpired

# Accounts with passwords expiring in the next 7 days
Search-ADAccount -PasswordExpiring -TimeSpan 7.00:00:00

# Inactive accounts (not logged in for 90+ days)
Search-ADAccount -AccountInactive -UsersOnly -TimeSpan 90.00:00:00
```

| Parameter           | Description                           |
| ------------------- | ------------------------------------- |
| `-AccountDisabled`  | Find disabled accounts                |
| `-AccountExpired`   | Find expired accounts                |
| `-AccountInactive`  | Find inactive accounts (use with `-TimeSpan`)  |
| `-LockedOut`        | Find locked-out accounts              |
| `-PasswordExpiring` | Find accounts with expiring passwords |
| `-PasswordNeverExpires` | Find accounts with non-expiring passwords |
| `-UsersOnly`        | Restrict to user objects               |
| `-ComputersOnly`    | Restrict to computer objects           |
| `-TimeSpan`         | Time window for inactivity/expiry      |
| `-ResultPageSize`   | Control page size for large results    |

### Remove-ADUser

```powershell
# Delete a single user
Remove-ADUser jdoe -Confirm:$false

# Delete all users in a disabled OU (with safety check)
Get-ADUser -Filter * -SearchBase "OU=Terminated,DC=example,DC=com" |
Remove-ADUser -Confirm:$false
```

---

## AD groups

| Cmdlet                        | Purpose                                              |
| ----------------------------- | ---------------------------------------------------- |
| `New-ADGroup`                 | Create a new AD group.                               |
| `Get-ADGroup`                 | Retrieve group objects.                              |
| `Get-ADGroupMember`           | List members of a group.                             |
| `Add-ADGroupMember`           | Add members to a group.                              |
| `Remove-ADGroupMember`        | Remove members from a group.                         |
| `Add-ADPrincipalGroupMembership` | Add a principal to one or more groups.            |
| `Remove-ADPrincipalGroupMembership` | Remove a principal from one or more groups.    |
| `Set-ADGroup`                 | Modify an existing group.                            |
| `Remove-ADGroup`              | Delete an AD group.                                  |

### New-ADGroup

[`New-ADGroup`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/new-adgroup?view=windowsserver2022-ps) creates a new group.

```powershell
New-ADGroup
    [-Name] <String>
    [-GroupScope] <DomainLocal | Global | Universal>
    [-GroupCategory] <Security | Distribution>
    [-SamAccountName <String>]
    [-Path <String>]
    [-Description <String>]
    [-DisplayName <String>]
```

```powershell
# Create a global security group
New-ADGroup -Name "Security Engineers" `
    -SamAccountName "SecEng" `
    -GroupScope Global `
    -GroupCategory Security `
    -Path "OU=Groups,DC=example,DC=com" `
    -Description "Security engineering team"

# Create a domain local distribution group
New-ADGroup -Name "All Staff" `
    -SamAccountName "AllStaff" `
    -GroupScope DomainLocal `
    -GroupCategory Distribution `
    -Path "OU=Distribution,DC=example,DC=com"
```

| Parameter        | Description                                    | Example                                     |
| ---------------- | ---------------------------------------------- | ------------------------------------------- |
| `-Name`          | Full object name (Common Name)                  | `"Security Engineers"`                      |
| `-SamAccountName`| Legacy logon name                               | `SecEng`                                    |
| `-GroupScope`    | `DomainLocal`, `Global`, or `Universal`         | `Global`                                    |
| `-GroupCategory` | `Security` (has SID) or `Distribution` (no SID) | `Security`                                  |
| `-Path`          | Target OU                                       | `"OU=Groups,DC=example,DC=com"`             |
| `-Description`   | Purpose of the group                            | `"Security engineering team"`               |
| `-ManagedBy`     | DN of the managing user/group                   | `"CN=John Doe,OU=Users,DC=example,DC=com"`  |

### Get-ADGroup

[`Get-ADGroup`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-adgroup?view=windowsserver2022-ps) retrieves group objects.

```powershell
# Get a specific group
Get-ADGroup "Domain Admins"

# Get group with all properties
Get-ADGroup "Domain Admins" -Properties *

# Get all groups
Get-ADGroup -Filter *

# Get groups by scope
Get-ADGroup -Filter 'GroupScope -eq "Universal"'

# Get groups by category
Get-ADGroup -Filter 'GroupCategory -eq "Security"'

# Search in a specific OU
Get-ADGroup -Filter * -SearchBase "OU=Groups,DC=example,DC=com"
```

### Add-ADGroupMember

[`Add-ADGroupMember`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/add-adgroupmember?view=windowsserver2022-ps) adds members to a group.

```powershell
# Add a user to a group
Add-ADGroupMember -Identity "Security Engineers" -Members jdoe

# Add multiple users
Add-ADGroupMember -Identity "Security Engineers" -Members jdoe, jsmith, ataylor

# Add a computer to a group
Add-ADGroupMember -Identity "Pre-Windows 2000 Compatible Access" -Members "WORKSTATION01$"

# Add a group to another group (nesting)
Add-ADGroupMember -Identity "Domain Admins" -Members "Security Engineers"

# Add all users from one group to another
Get-ADGroupMember -Identity "SourceGroup" |
ForEach-Object { Add-ADGroupMember -Identity "TargetGroup" -Members $_ }
```

### Remove-ADGroupMember

[`Remove-ADGroupMember`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/remove-adgroupmember?view=windowsserver2022-ps) removes members.

```powershell
Remove-ADGroupMember -Identity "Security Engineers" -Members ataylor -Confirm:$false

# Remove all members from a group
Get-ADGroupMember -Identity "Security Engineers" |
ForEach-Object { Remove-ADGroupMember -Identity "Security Engineers" -Members $_ -Confirm:$false }
```

### Get-ADGroupMember

[`Get-ADGroupMember`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-adgroupmember?view=windowsserver2022-ps) enumerates members of a group.

```powershell
# List members of a group
Get-ADGroupMember -Identity "Domain Admins"

# List members with detailed properties
Get-ADGroupMember -Identity "Domain Admins" |
Select-Object Name, SamAccountName, ObjectClass, DistinguishedName

# Recursively get all members (including nested groups)
Get-ADGroupMember -Identity "Domain Admins" -Recursive

# Count members
(Get-ADGroupMember -Identity "Domain Admins").Count
```

### Add-ADPrincipalGroupMembership

[`Add-ADPrincipalGroupMembership`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/add-adprincipalgroupmembership?view=windowsserver2022-ps) adds a user/computer/group to multiple groups at once.

```powershell
# Add user to multiple groups
Add-ADPrincipalGroupMembership -Identity jdoe `
    -MemberOf "Security Engineers", "VPN Access", "Remote Desktop Users"
```

### Get-ADPrincipalGroupMembership

[`Get-ADPrincipalGroupMembership`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-adprincipalgroupmembership?view=windowsserver2022-ps) lists all groups a principal belongs to.

```powershell
# All groups for a user
Get-ADPrincipalGroupMembership -Identity jdoe

# Check nested group membership (transitive)
Get-ADPrincipalGroupMembership -Identity jdoe | Select-Object Name, GroupScope, GroupCategory
```

### Set-ADGroup

[`Set-ADGroup`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/set-adgroup?view=windowsserver2022-ps) modifies group properties.

```powershell
# Change description
Set-ADGroup "Security Engineers" -Description "Security engineering team (updated)"

# Change group scope (domain local → universal or global → universal)
Set-ADGroup "Security Engineers" -GroupScope Universal

# Change group category (distribution → security)
Set-ADGroup "All Staff" -GroupCategory Security

# Replace arbitrary attributes
Set-ADGroup "Security Engineers" -Replace @{info="Group created for SecEng team"}
```

---

## AD computers

| Cmdlet           | Purpose                                    |
| ---------------- | ------------------------------------------ |
| `New-ADComputer` | Create a new computer object in AD.        |
| `Get-ADComputer` | Retrieve computer objects.                 |
| `Set-ADComputer` | Modify a computer object.                  |
| `Remove-ADComputer` | Delete a computer object.               |

### Get-ADComputer

[`Get-ADComputer`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-adcomputer?view=windowsserver2022-ps) retrieves computer objects.

```powershell
# Get a specific computer
Get-ADComputer WORKSTATION01

# Get computer with all properties
Get-ADComputer WORKSTATION01 -Properties *

# All computers
Get-ADComputer -Filter *

# Computers by name pattern
Get-ADComputer -Filter 'Name -like "SRV-*"'

# Computers with OS information
Get-ADComputer -Filter * -Properties OperatingSystem,OperatingSystemVersion |
Select-Object Name, OperatingSystem, OperatingSystemVersion

# Computers with password last set before a date
$date = [DateTime]::Today.AddDays(-30)
Get-ADComputer -Filter 'PasswordLastSet -lt $date' -Properties PasswordLastSet

# Computers that have not logged in recently
$date = [DateTime]::UtcNow.AddDays(-90)
Get-ADComputer -Filter 'LastLogonDate -lt $date' -Properties LastLogonDate

# Disabled computers
Get-ADComputer -Filter 'Enabled -eq $false'

# Search in specific OU
Get-ADComputer -Filter * -SearchBase "OU=Workstations,DC=example,DC=com"
```

| Parameter      | Description                    | Example                            |
| -------------- | ------------------------------ | ---------------------------------- |
| `-Identity`    | Computer name (with or without `$` suffix) | `WORKSTATION01` or `WORKSTATION01$` |
| `-Properties`  | Extra properties to retrieve   | `OperatingSystem, IPv4Address`     |

### New-ADComputer

[`New-ADComputer`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/new-adcomputer?view=windowsserver2022-ps) creates a computer object.

```powershell
New-ADComputer -Name "WORKSTATION02" `
    -SamAccountName "WORKSTATION02$" `
    -Path "OU=Workstations,DC=example,DC=com" `
    -Description "Sales department workstation"
```

### Set-ADComputer

[`Set-ADComputer`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/set-adcomputer?view=windowsserver2022-ps) modifies computer properties.

```powershell
# Disable a computer account
Set-ADComputer WORKSTATION01 -Enabled $false

# Update description
Set-ADComputer WORKSTATION01 -Description "Reassigned to HR department"

# Set managed by
Set-ADComputer WORKSTATION01 -ManagedBy "CN=John Doe,OU=Users,DC=example,DC=com"
```

---

## AD organizational units

| Cmdlet                    | Purpose                                   |
| ------------------------- | ----------------------------------------- |
| `New-ADOrganizationalUnit`| Create a new OU.                          |
| `Get-ADOrganizationalUnit`| Retrieve OUs.                             |
| `Set-ADOrganizationalUnit`| Modify an OU.                             |
| `Move-ADObject`           | Move objects between OUs.                 |
| `Remove-ADOrganizationalUnit` | Remove an OU.                         |

### New-ADOrganizationalUnit

[`New-ADOrganizationalUnit`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/new-adorganizationalunit?view=windowsserver2022-ps) creates an OU.

```powershell
New-ADOrganizationalUnit -Name "Sales" `
    -Path "DC=example,DC=com" `
    -Description "Sales department" `
    -ProtectedFromAccidentalDeletion $true

# Create nested OU
New-ADOrganizationalUnit -Name "Managers" `
    -Path "OU=Sales,DC=example,DC=com" `
    -ProtectedFromAccidentalDeletion $true
```

### Get-ADOrganizationalUnit

[`Get-ADOrganizationalUnit`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-adorganizationalunit?view=windowsserver2022-ps) retrieves OUs.

```powershell
# All OUs
Get-ADOrganizationalUnit -Filter *

# OU with specific name
Get-ADOrganizationalUnit -Filter 'Name -eq "Sales"'

# OU by identity (DN)
Get-ADOrganizationalUnit -Identity "OU=Sales,DC=example,DC=com" -Properties *

# OUs protected from accidental deletion
Get-ADOrganizationalUnit -Filter 'ProtectedFromAccidentalDeletion -eq $true'
```

### Move-ADObject

[`Move-ADObject`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/move-adobject?view=windowsserver2022-ps) moves objects between OUs or domains.

```powershell
# Move a user to a different OU
Move-ADObject -Identity "CN=Jane Doe,OU=Temp,DC=example,DC=com" `
    -TargetPath "OU=Employees,DC=example,DC=com"

# Move all users from one OU to another
Get-ADUser -Filter * -SearchBase "OU=OldOU,DC=example,DC=com" |
Move-ADObject -TargetPath "OU=NewOU,DC=example,DC=com"
```

---

## Account management and control

| Cmdlet                            | Purpose                                        |
| --------------------------------- | ----------------------------------------------- |
| `Enable-ADAccount`                | Enable a disabled account.                     |
| `Disable-ADAccount`               | Disable an account.                             |
| `Unlock-ADAccount`                | Unlock a locked-out account.                    |
| `Set-ADAccountControl`            | Modify UAC flags (e.g., `PasswordNeverExpires`).|
| `Set-ADAccountExpiration`         | Set account expiration date.                    |
| `Clear-ADAccountExpiration`       | Remove account expiration.                      |

### Enable/Disable/Unlock

```powershell
# Enable a user account
Enable-ADAccount jdoe

# Disable a user account
Disable-ADAccount jdoe

# Disable multiple users
Get-ADUser -Filter 'Enabled -eq $true' -SearchBase "OU=Terminated,DC=example,DC=com" |
Disable-ADAccount

# Unlock a locked-out account
Unlock-ADAccount jdoe

# Unlock all locked-out accounts
Search-ADAccount -LockedOut | Unlock-ADAccount
```

### Set-ADAccountControl

[`Set-ADAccountControl`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/set-adaccountcontrol?view=windowsserver2022-ps) modifies user account control (UAC) flags.

```powershell
# Set password to never expire
Set-ADAccountControl jdoe -PasswordNeverExpires $true

# Require smart card for logon
Set-ADAccountControl jdoe -SmartcardLogonRequired $true

# Prevent user from changing password
Set-ADAccountControl jdoe -CannotChangePassword $true

# Mark account as sensitive and cannot be delegated
Set-ADAccountControl jdoe -AccountNotDelegated $true
```

### Set-ADAccountExpiration

```powershell
# Set expiration date (account will be disabled after this date)
Set-ADAccountExpiration jdoe -DateTime "2026-12-31"

# Clear expiration
Clear-ADAccountExpiration jdoe
```

---

## Object operations (Delete, Rename, Restore)

| Cmdlet              | Purpose                                           |
| ------------------- | ------------------------------------------------- |
| `Remove-ADObject`   | Delete any AD object.                             |
| `Rename-ADObject`   | Rename an AD object.                              |
| `Restore-ADObject`  | Restore a deleted object from the AD Recycle Bin. |
| `Remove-ADUser`     | Remove a user (convenience wrapper).              |
| `Remove-ADGroup`    | Remove a group (convenience wrapper).             |
| `Remove-ADComputer` | Remove a computer (convenience wrapper).          |

### Remove-ADObject

```powershell
# Delete a user
Remove-ADObject -Identity "CN=Jane Doe,OU=Users,DC=example,DC=com" -Confirm:$false

# Delete a GPO by GUID
Remove-ADObject -Identity "CN={GUID},CN=Policies,CN=System,DC=example,DC=com" -Confirm:$false
```

### Rename-ADObject

[`Rename-ADObject`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/rename-adobject?view=windowsserver2022-ps) changes the object name.

```powershell
# Rename a user
Rename-ADObject -Identity "CN=Jane Doe,OU=Users,DC=example,DC=com" -NewName "Jane Smith"
```

### Restore-ADObject

[`Restore-ADObject`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/restore-adobject?view=windowsserver2022-ps) restores deleted objects (requires AD Recycle Bin enabled).

```powershell
# Restore deleted user
Get-ADObject -Filter 'Name -eq "Jane Doe"' -IncludeDeletedObjects |
Restore-ADObject

# Restore with new name and target OU
Get-ADObject -Filter 'Name -eq "Jane Doe"' -IncludeDeletedObjects |
Restore-ADObject -NewName "Jane Smith" -TargetPath "OU=Users,DC=example,DC=com"
```

---

## Domain and forest information

| Cmdlet                          | Purpose                                    |
| ------------------------------- | ------------------------------------------ |
| `Get-ADDomain`                  | Get domain information.                    |
| `Get-ADForest`                  | Get forest information.                    |
| `Get-ADDomainController`        | Find domain controllers.                   |
| `Get-ADTrust`                   | List trust relationships.                  |
| `Get-ADRootDSE`                 | Get root DSE information.                  |

### Get-ADDomain

[`Get-ADDomain`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-addomain?view=windowsserver2022-ps) returns domain properties.

```powershell
Get-ADDomain | Select-Object DNSRoot, NetBIOSName, Forest, DomainMode, PDCEmulator, RIDMaster, InfrastructureMaster
```

| Property              | Description                          |
| --------------------- | ------------------------------------ |
| `DNSRoot`             | DNS name of the domain               |
| `NetBIOSName`         | NetBIOS name (pre-Windows 2000)      |
| `Forest`              | Forest this domain belongs to        |
| `DomainMode`          | Domain functional level              |
| `PDCEmulator`         | DC holding the PDC Emulator role     |
| `RIDMaster`           | DC holding the RID Master role       |
| `InfrastructureMaster`| DC holding the Infrastructure Master |
| `ComputersContainer`  | Default computers container          |
| `UsersContainer`      | Default users container              |
| `LinkedGroupPolicyObjects` | GPOs linked to the domain       |

### Get-ADForest

[`Get-ADForest`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-adforest?view=windowsserver2022-ps) returns forest properties.

```powershell
Get-ADForest | Select-Object Name, RootDomain, Domains, GlobalCatalogs, ForestMode, SchemaMaster, DomainNamingMaster
```

| Property            | Description                          |
| ------------------- | ------------------------------------ |
| `Name`              | Forest DNS name                      |
| `RootDomain`        | Forest root domain                   |
| `Domains`           | All domains in the forest             |
| `GlobalCatalogs`    | Servers hosting the Global Catalog   |
| `ForestMode`        | Forest functional level              |
| `SchemaMaster`      | DC holding the Schema Master role    |
| `DomainNamingMaster`| DC holding the Domain Naming Master  |
| `Sites`             | All sites in the forest              |

### Get-ADDomainController

[`Get-ADDomainController`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-addomaincontroller?view=windowsserver2022-ps) discovers domain controllers.

```powershell
# All DCs in the current domain
Get-ADDomainController -Filter *

# DCs with specific roles
Get-ADDomainController -Filter * |
Select-Object Name, Site, OperationMasterRoles, IPv4Address

# Find a DC with a specific role
Get-ADDomainController -Discover -Service "PrimaryDC"

# DCs in a specific site
Get-ADDomainController -Filter 'Site -eq "Default-First-Site-Name"'

# Current user's DC
Get-ADDomainController -Discover
```

### Get-ADTrust

[`Get-ADTrust`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-adtrust?view=windowsserver2022-ps) lists trust relationships.

```powershell
# All trusts for the current domain
Get-ADTrust -Filter *

# Trusts for a specific domain
Get-ADTrust -Identity example.com

# Cross-forest trusts
Get-ADTrust -Filter 'ForestTransitive -eq $true'

# Trust properties
Get-ADTrust -Filter * |
Select-Object Name, Direction, TrustType, TrustAttributes, Target
```

---

## Replication and site management

| Cmdlet                       | Purpose                                  |
| ---------------------------- | ---------------------------------------- |
| `Get-ADReplication*`         | Various replication status cmdlets.      |
| `Get-ADReplicationSite`      | Get sites.                               |
| `Get-ADReplicationSubnet`    | Get subnets.                             |
| `Get-ADReplicationSiteLink`  | Get site links.                          |
| `Sync-ADObject`              | Force replication of a single object.    |
| `Repadmin`                   | External tool for replication management.|

```powershell
# Get all sites
Get-ADReplicationSite -Filter *

# Get all subnets
Get-ADReplicationSubnet -Filter *

# Get all site links
Get-ADReplicationSiteLink -Filter *

# Get replication partners for a DC
Get-ADReplicationPartnerMetadata -Target "dc01.example.com"

# Force replication of a specific object between two DCs
Sync-ADObject -Object "CN=Jane Doe,OU=Users,DC=example,DC=com" `
    -Source "dc01.example.com" `
    -Destination "dc02.example.com"
```

---

## Fine-grained password policies (FGPP)

| Cmdlet                                  | Purpose                                  |
| --------------------------------------- | ---------------------------------------- |
| `New-ADFineGrainedPasswordPolicy`       | Create a PSO (Password Settings Object). |
| `Get-ADFineGrainedPasswordPolicy`       | Retrieve PSOs.                          |
| `Set-ADFineGrainedPasswordPolicy`       | Modify a PSO.                           |
| `Remove-ADFineGrainedPasswordPolicy`    | Delete a PSO.                           |
| `Add-ADFineGrainedPasswordPolicySubject`| Apply PSO to users/groups.              |

```powershell
# Create a PSO
New-ADFineGrainedPasswordPolicy -Name "StrictPolicy" `
    -Precedence 100 `
    -MinPasswordLength 14 `
    -PasswordHistoryCount 24 `
    -MinPasswordAge "1.00:00:00" `
    -MaxPasswordAge "90.00:00:00" `
    -LockoutThreshold 5 `
    -LockoutDuration "00:30:00" `
    -LockoutObservationWindow "00:30:00" `
    -ComplexityEnabled $true

# Apply PSO to a group
Add-ADFineGrainedPasswordPolicySubject -Identity "StrictPolicy" `
    -Subjects "Security Engineers"

# Get resultant password policy for a user
Get-ADUserResultantPasswordPolicy jdoe
```

---

## Search and filtering patterns

### LDAP filter syntax

> **LDAP filters** use the format `(attribute operator value)` and can be combined with `&` (AND), `|` (OR), and `!` (NOT).

```powershell
# LDAP equivalent of -Filter
Get-ADUser -LDAPFilter '(objectCategory=person)'
Get-ADUser -LDAPFilter '(&(objectCategory=person)(objectClass=user))'

# Find users with specific SPN (service accounts)
Get-ADUser -LDAPFilter '(servicePrincipalName=*)'

# Find enabled users in a specific OU
Get-ADUser -LDAPFilter '(&(objectCategory=person)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))' `
    -SearchBase "OU=Users,DC=example,DC=com"

# Find computers with specific OS
Get-ADComputer -LDAPFilter '(operatingSystem=Windows 10*)'
```

### Common UAC bit checks

The `userAccountControl` attribute is a bitmask. Use these LDAP matching rules:

| UAC Flag                   | Decimal | LDAP Filter                                                     |
| -------------------------- | ------- | --------------------------------------------------------------- |
| Account disabled            | 2       | `(userAccountControl:1.2.840.113556.1.4.803:=2)`               |
| Password never expires      | 65536   | `(userAccountControl:1.2.840.113556.1.4.803:=65536)`           |
| Smartcard required          | 262144  | `(userAccountControl:1.2.840.113556.1.4.803:=262144)`          |
| Account not delegated       | 1048576 | `(userAccountControl:1.2.840.113556.1.4.803:=1048576)`         |
| Trusted for delegation      | 524288  | `(userAccountControl:1.2.840.113556.1.4.803:=524288)`          |
| Password not required       | 32      | `(userAccountControl:1.2.840.113556.1.4.803:=32)`              |

```powershell
# Find users with PasswordNeverExpires
Get-ADUser -LDAPFilter '(userAccountControl:1.2.840.113556.1.4.803:=65536)'

# Find users without Kerberos pre-authentication (AS-REP roastable)
Get-ADUser -LDAPFilter '(userAccountControl:1.2.840.113556.1.4.803:=4194304)'

# Find accounts trusted for delegation
Get-ADUser -LDAPFilter '(userAccountControl:1.2.840.113556.1.4.803:=524288)'
```

---

## Service accounts and SPNs

| Cmdlet                  | Purpose                                     |
| ----------------------- | ------------------------------------------- |
| `Get-ADServiceAccount`  | Retrieve managed service accounts.          |
| `New-ADServiceAccount`  | Create a group Managed Service Account.     |
| `Install-ADServiceAccount` | Install gMSA on a computer.              |

```powershell
# Find accounts with SPNs (potential Kerberoast targets)
Get-ADUser -Filter 'ServicePrincipalNames -like "*"' `
    -Properties ServicePrincipalNames |
Select-Object SamAccountName, ServicePrincipalNames

# Find computers with SPNs
Get-ADComputer -Filter 'ServicePrincipalNames -like "*"' `
    -Properties ServicePrincipalNames |
Select-Object Name, ServicePrincipalNames

# Get all SPN entries (not by account type)
Get-ADObject -Filter 'ServicePrincipalNames -like "*"' -Properties ServicePrincipalNames, SamAccountName

# Create a gMSA
New-ADServiceAccount -Name "SQLSvc" `
    -DNSHostName "sqlsvc.example.com" `
    -ServicePrincipalNames "MSSQLSvc/sqlserver.example.com:1433" `
    -PrincipalsAllowedToRetrieveManagedPassword "SQL Servers"

# List gMSAs
Get-ADServiceAccount -Filter *
```

---

## Delegation and ACL management

| Cmdlet                            | Purpose                                     |
| --------------------------------- | ------------------------------------------- |
| `Set-ADObject`                    | Modify object ACL via `-Replace` (nTSecurityDescriptor). |
| `Get-ADObject`                    | Retrieve ACL information.                   |
| `dsacls`                          | External tool for ACL management.           |

```powershell
# Get ACL for an OU
Get-ADObject -Identity "OU=Sales,DC=example,DC=com" -Properties nTSecurityDescriptor |
Select-Object -ExpandProperty nTSecurityDescriptor |
ForEach-Object { $_.GetAccessRules($true, $true, [System.Security.Principal.NTAccount]) }

# Delegate control with dsacls (external tool)
dsacls "OU=Sales,DC=example,DC=com" /G "EXAMPLE\HelpDesk:CA;Reset Password"
```

---

## Bulk operations and reporting

```powershell
# Export all users to CSV
Get-ADUser -Filter * -Properties Department, Title, Manager, LastLogonDate |
Select-Object Name, SamAccountName, UserPrincipalName, Enabled,
              Department, Title, @{n="Manager";e={$_.Manager -replace '^CN=|,.*$'}},
              LastLogonDate |
Export-Csv -Path "ad_users.csv" -NoTypeInformation

# Export all groups
Get-ADGroup -Filter * -Properties Description, GroupScope, GroupCategory, Members |
Select-Object Name, SamAccountName, GroupScope, GroupCategory,
              @{n="MemberCount";e={($_.Members).Count}}, Description |
Export-Csv -Path "ad_groups.csv" -NoTypeInformation

# Bulk create users from CSV
Import-Csv -Path "new_users.csv" | ForEach-Object {
    New-ADUser -Name "$($_.GivenName) $($_.Surname)" `
        -GivenName $_.GivenName `
        -Surname $_.Surname `
        -SamAccountName $_.SamAccountName `
        -UserPrincipalName "$($_.SamAccountName)@example.com" `
        -Path "OU=Users,DC=example,DC=com" `
        -AccountPassword (ConvertTo-SecureString -AsPlainText $_.InitialPassword -Force) `
        -Enabled $true
}

# Bulk add users to group from CSV
Import-Csv -Path "add_to_group.csv" | ForEach-Object {
    Add-ADGroupMember -Identity $_.GroupName -Members $_.SamAccountName
}

# Create multiple OUs from a list
"Sales", "Marketing", "Engineering", "HR", "Finance" | ForEach-Object {
    New-ADOrganizationalUnit -Name $_ -Path "DC=example,DC=com" `
        -ProtectedFromAccidentalDeletion $true
}
```

---

## Useful one-liners

```powershell
# Count total users
(Get-ADUser -Filter *).Count

# Count enabled vs disabled users
(Get-ADUser -Filter 'Enabled -eq $true').Count
(Get-ADUser -Filter 'Enabled -eq $false').Count

# Find users with the same DisplayName (duplicates)
Get-ADUser -Filter * -Properties DisplayName |
Group-Object DisplayName | Where-Object Count -gt 1

# List domain controllers
Get-ADDomainController -Filter * | Format-Table Name, Site, IPv4Address, OperationMasterRoles -AutoSize

# List all domain functional levels
Get-ADDomain -Filter * | Format-Table DNSRoot, NetBIOSName, DomainMode

# Get last logon across all DCs (most accurate)
Get-ADUser jdoe -Properties LastLogonDate, LastLogonTimestamp, LastBadPasswordAttempt

# Find empty groups
Get-ADGroup -Filter * -Properties Members |
Where-Object { -not $_.Members } |
Select-Object Name

# Find groups with a specific user
Get-ADPrincipalGroupMembership -Identity jdoe |
Select-Object Name, GroupScope, GroupCategory

# Get all managed service accounts
Get-ADServiceAccount -Filter * | Format-Table Name, DNSHostName, ServicePrincipalNames

# Find all users with adminCount=1 (protected by AdminSDHolder)
Get-ADUser -LDAPFilter '(adminCount=1)' -Properties adminCount |
Select-Object Name, SamAccountName

# Show DC time skew
Get-ADDomainController -Filter * | ForEach-Object {
    $dc = $_.Name; New-Object PSObject -Property @{
        DC = $dc
        Time = (Get-Process -ComputerName $dc -IncludeUserName | Out-Null; (Get-Date))
    }
} | Format-Table DC, Time

# Check if AD Recycle Bin is enabled
Get-ADOptionalFeature -Filter "Name -like '*'"

# Get directory partition information
Get-ADObject -Filter 'objectClass -eq "crossRef"' -SearchBase "CN=Partitions,$((Get-ADRootDSE).ConfigurationNamingContext)"
```

---

## Module information

```powershell
# List all available cmdlets in the module
Get-Command -Module ActiveDirectory

# Get help for a specific cmdlet
Get-Help Get-ADUser -Detailed
Get-Help Get-ADUser -Examples

# Find cmdlets by verb
Get-Command -Module ActiveDirectory -Verb Get
Get-Command -Module ActiveDirectory -Verb Set
Get-Command -Module ActiveDirectory -Verb New
Get-Command -Module ActiveDirectory -Verb Remove
```

>[!note] See [[◯ AD users and groups]] for group types, scopes, and built-in groups reference.
