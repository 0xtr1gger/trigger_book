---
created: 2026-08-20
updated: 2026-10-11
tags:
  - AD
status: incomplete
---
## AD security descriptors & ACLs

### Security descriptors

- Every object in Active Directory has a binary attribute named `nTSecurityDescriptor`. 
- This attribute stores the object's **Security Descriptor (SD)**, which defines ownership, access permissions, auditing rules, and permission inheritance settings.

#### Structure of security descriptors

- An Active Directory security descriptor consists of five primary structures:

- **Owner SID**
	- The binary SID (Security Identifier) of the user or group account that owns the object.
	- The owner holds an implicit right (`WRITE_DAC`) to modify the object's permissions (DACL), even if explicit access to the object has been removed or restricted.

- **Group SID**
	- The binary SID of the object's primary group.
	- It is inherited from Windows NT and POSIX subsystem requirements. AD authorization logic completely ignores this field; it remains solely for backward compatibility.

- **DACL (Discretionary Access Control List)**
	- An ordered list of Access Control Entries (ACEs) that enforce authorization rules. 
	- Each ACE defines whether a specific principal (user, group, computer) is **Allowed** or **Denied** specific rights (e.g., `Reset Password`, `Write All Properties`, `Full Control`, `Create Child Objects`).

- **SACL (System Access Control List)**
	- An ordered list of audit ACEs that govern security event logging.
	- It defines which actions (e.g., successful reads or failed attribute updates) performed by a specific principal trigger events in the **Security Event Log** on the Domain Controller. 
	- Reading or modifying an object's SACL requires the `SeSecurityPrivilege` privilege.

- **Control Flags** 
	- A bitmask set of metadata flags that qualify descriptor behavior.
	- Key flags include:
		- `SE_DACL_PROTECTED`: Blocks permission inheritance from parent containers (explicitly breaks inheritance).
		- `SE_DACL_AUTO_INHERITED`: Indicates that the DACL was automatically generated through child object inheritance.
		- `SE_DACL_PRESENT`: Indicates whether a valid DACL is attached to the object.

### Access Control Lists

- In Active Directory, Access Control Lists are *ordered* collections of ACEs (Access Control Entries) stored inside an object's security descriptor.
- While DACLs enforce authorization, SACLs manage security auditing.

### Discretionary Access Control Lists (DACLs)

- **DACL (Discretionary Access Control List)** defines which security principals (users, computers, or groups) are allowed or denied access to that object and what operations they can perform.
	- If a DACL is **null or missing**, access control is disabled and **everyone has full access** to the object.
	- If a DACL is **empty** (contains zero ACEs), **no principal has access** (except for the object owner who retains implicit rights to take control).

##### DACL access mask

- The permissions granted or denied by ACEs in a DACL are stored as a 32-bit integer called **access mask** (`ACCESS_MASK`). 
- The 32 bits are divided into four distinct regions:

| Bits `28`-`31` <br>(4 bits) | Bits `25`-`27` <br>(3 bits) | Bits `16`-`24` <br>(9 bits) | Bits `0`-`15` <br>(16 bits) |
| --- | --- | --- | --- |
| Generic rights<br>(`GA`, `GR`, `GW`, `GX`) | System / special rights | Standard rights<br>(`SD`, `RC`, `WD`, `WO`) | Object-specific rights<br>(`CC`, `DC`, `RP`, `WP`) |

- Object-specific rights (bits `0`-`15`):

| Bit | Flag name | Bitmask value | SDDL | Description |
| --- | --- | --- | --- | --- |
| `0` | `CreateChild` | `0x00000001` | `CC` | Create child objects (e.g., creating a new user under an OU). |
| `1` | `DeleteChild` | `0x00000002` | `DC` | Delete child objects within a container. |
| `2` | `ListChildren` | `0x00000004` | `LC` | List child objects contained within the target object. |
| `3` | `Self` | `0x00000008` | `SW` | Perform validated writes (e.g., self-membership updates via `AddSelf`). |
| `4` | `ReadProperty` | `0x00000010` | `RP` | Read attribute values on the target object. |
| `5` | `WriteProperty` | `0x00000020` | `WP` | Write or update attribute values on the target object. |
| `6` | `DeleteTree` | `0x00000040` | `DT` | Delete an entire object subtree, regardless of child DACLs. |
| `7` | `ListObject` | `0x00000080` | `LO` | List the object itself during enumeration routines. |
| `8` | `ControlAccess` | `0x00000100` | `CR` | Perform extended rights (control access rights, e.g., `Reset Password`, `Replicating Directory Changes`). |
| `9`-`15` | *Reserved* | — | — | Unused bit positions in the DS-specific range. |

- Standard access rights (bits `16`-`23`):

| Bit | Flag name | Bitmask value | SDDL | Description |
| --- | --- | --- | --- | --- |
| `16` | `Delete` | `0x00010000` | `SD` | Delete the object directly. |
| `17` | `ReadControl` | `0x00020000` | `RC` | Read the object's DACL; required to inspect permissions. |
| `18` | `WriteDACL` | `0x00040000` | `WD` | Modify DACL permissions (a principal with this right can elevate privileges). |
| `19` | `WriteOwner` | `0x00080000` | `WO` | Change the owner SID in the object's security descriptor. |
| `20` | `Synchronize` | `0x00100000` | `SY` | Synchronize threads (rarely used in AD authorization logic). |
| `21`-`23` | *Reserved* | — | — | Unused standard rights bits. |

>[!note] `ReadControl` (`RC`) is the minimum right needed to read a DACL; if you don't have it, you cannot inspect object permissions.

- Special and system rights (bits `24`-`27`):

| Bit | Bitmask value | Flag name | SDDL | Description |
| --- | --- | --- | --- | --- |
| `24` | `0x01000000` | `AccessSACL` | `S` | Read or modify the SACL; requires `SeSecurityPrivilege` on the DC. |
| `25` | `0x02000000` | `MaximumAllowed` | `MA` | Evaluates and returns maximum access rights held by requesting token. |
| `26`-`27` | — | *Reserved* | — | System reserved bits. |

- Generic access rights (bits `28`-`31`):

| Bit | Bitmask value | Flag name | SDDL | Description |
| --- | --- | --- | --- | --- |
| `28` | `0x10000000` | `GenericAll` | `GA` | Full control over object; maps to all standard and DS-specific rights. |
| `29` | `0x20000000` | `GenericExecute` | `GX` | Execution rights; in AD, evaluates to `READ_CONTROL` + `DS_LIST`. |
| `30` | `0x40000000` | `GenericWrite` | `GW` | Standard write privileges; maps to writing properties and standard writes. |
| `31` | `0x80000000` | `GenericRead` | `GR` | Standard read privileges; maps to reading properties and security descriptors. |

##### Generic rights mapping

- Generic rights serve as high-level aliases.
- When an ACE with generic bits is processed, Active Directory automatically maps them into corresponding combinations of standard and object-specific rights:
	- **`GenericAll`** -> `DE` | `RC` | `WD` | `WO` | `CC` | `DC` | `DT` | `RP` | `WP` | `LC` | `LO` | `CR` | `SW`
	- **`GenericRead`** -> `RC` | `LC` | `RP` | `LO`
	- **`GenericWrite`** -> `RC` | `WP` | `SW`
	- **`GenericExecute`** -> `RC` | `LC`

>[!important] `GenericWrite` does **not** include `WriteDACL` (`WD`) or `WriteOwner` (`WO`). It allows modifying existing attributes but does not grant direct permission to rewrite security descriptors. `GenericAll` includes `WD` and `WO`, conferring complete administrative control.

#### Extended rights and property sets

- Extended rights (`ControlAccess` / `CR`) are specific rights defined in the AD schema that govern specialized operations or access to sensitive attribute groups:

| Extended right / GUID | Display name | Operational impact |
| --- | --- | --- |
| `00299570-246d-11d0-a768-00aa006e0529` | `User-Force-Change-Password` | Force-reset user password without knowing current credentials. |
| `1131f6aa-9c07-11d1-f79f-00c04fc2dcd2` | `DS-Replication-Get-Changes` | Required right for domain directory replication (DCSync part 1). |
| `1131f6ad-9c07-11d1-f79f-00c04fc2dcd2` | `DS-Replication-Get-Changes-All` | Required right to replicate secret attributes (DCSync part 2). |
| `1131f6ac-9c07-11d1-f79f-00c04fc2dcd2` | `DS-Replication-Manage-Topology` | Manage domain replication topology. |
| `bf9679c0-0de6-11d0-a285-00aa003049e2` | `Self-Membership` (`AddSelf`) | Validated write to add/remove principal's own account to a group. |

#### SACL (System Access Control List)

- **SACL (System Access Control List)** handles auditing and security monitoring. A SACL defines which access attempts generate events in the DC's Security Log.

##### Passive auditing

- SACLs operate passively and do not block or grant access requests. When an access attempt matches a SACL ACE, the Domain Controller generates specific event logs:
	- **Event ID `4662`** (`An operation was performed on an object`)
	- **Event ID `5136`** (`A directory service object was modified`)

- For SACL logging to function, two conditions must be met:
	- A relevant **Audit ACE** must exist in the target object's SACL.
	- The Advanced Audit Policy for **Audit Directory Service Access** or **Audit Directory Service Changes** must be explicitly enabled on the DC.

##### Components of a SACL ACE

- Each SACL ACE includes:
	- **Trustee SID**: The security principal whose actions trigger audit logs.
	- **Audit flags**: Trigger conditions (`Audit Success` or `Audit Failure`).
	- **Access mask / object type**: Defines the exact operation being audited.

