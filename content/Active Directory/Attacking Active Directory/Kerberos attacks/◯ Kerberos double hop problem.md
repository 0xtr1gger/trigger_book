---
created: 2026-08-22
updated: 2026-10-24
tags:
  - AD
  - Kerberos
---

- The **Kerberos double-hop** problem occurs when a user authenticates to a first server, but that server can't forward the user's credentials to access the second server. This happens because Kerberos doesn't automatically cache or forward TGTs (Ticket-Granting Tickets) for security reasons. 
## Kerberos double hop problem

- In Kerberos, when a user authenticates to one host (the **first hop**), and then a process on that host tries to reach another nost (**second hop**) as the same user, the authentication fails — because the first host holds no credentials it can present on the user's behalf.
- This is called the **Kerberos double hop problem**.

- A typical scenario: an operator connects to a host over **WinRM / PowerShell Remoting** (first hop), then runs a tool that queries a domain controller or file server (second hop). Commands that touch only the first host succeed; anything that reaches a second host fails.

```text
AttackBox ──(WinRM)──▶ HostA ──(LDAP/SMB, as the user)──▶ HostB / DC
                       first hop              second hop (fails)
```

- The problem isn't specific to attack tooling. It affects any integrated Windows authentication that crosses two network hops. It's most visible over [[WinRM]], because WinRM is a common entry point for remote administration and post-exploitation.

>[!note] See [[Kerberos]] for how the protocol, the TGT (Ticket-Granting Ticket), and service tickets work.

## Why the second hop fails

- **Kerberos tickets are scoped to a single service.** When the user authenticates to `HostA`, `HostA` receives only a service ticket for its own service (for WinRM, the `HTTP` SPN). That ticket proves the user's identity to `HostA`; it can't be used to obtain tickets for any other service (see [[Kerberos#Service Tickets (STs)]]).
- **`HostA` never receives the user's password or TGT.** Without the user's long-term key or a TGT, `HostA` has no material to request a fresh service ticket for `HostB` as the user.
- **WinRM authenticates with a *network logon* (logon type 3).** A network logon doesn't cache reusable credentials on the target. So even though commands run as the user locally on `HostA`, the session can't authenticate *outbound* as that user.
- The onward request to `HostB` therefore leaves `HostA` with no valid credentials. `HostB` rejects it, and the tool reports an error.

>[!important] In short, Kerberos proves the user's identity for a single hop. By default, a host reached over the network can act as the user locally but can't pass that identity on to a third system.

>[!note]+ Why an interactive logon doesn't have this problem
> - With an **interactive logon** (local console or RDP), the user supplies their password to the host, so the host holds the user's long-term key and a TGT in `LSASS`. It can request service tickets for a second hop on the user's behalf.
> - A **network logon** (WinRM, SMB, and similar) never gives the host that material, which is exactly what creates the double hop problem.

## Symptoms and diagnosis

- A tool such as PowerView works from a local shell on the first host but fails inside a WinRM session the moment it queries another host.
- Common errors:
	- `An operations error occurred.` — a failed LDAP bind against a DC (`Get-DomainUser`, `Get-ADUser`, and similar).
	- `Access is denied.` — SMB or other access to a second host.
- List the Kerberos tickets inside the remote session to confirm the cause:

```powershell
klist
```

- The cache shows a service ticket for the first host but no TGT usable to reach the second host. The missing TGT confirms the session can't authenticate a second hop.

## Workarounds

### Pass explicit credentials to the second-hop tool

- Supply credentials directly to the tool so it authenticates to the second host itself, instead of relying on the session's identity.

```powershell
$pw   = ConvertTo-SecureString '<password>' -AsPlainText -Force
$cred = New-Object PSCredential('<DOMAIN>\<user>',$pw)

Get-DomainUser -Credential $cred
Get-DomainObjectAcl -ResolveGUIDs -Credential $cred
```

- `-Credential` makes each command authenticate the second hop on its own. This is the simplest fix when the tool accepts a credential object and you hold (or can build) the credentials.

### Use an interactive logon

- Connect with RDP instead of WinRM where possible. An interactive session holds the user's TGT, so a second hop works without further steps.

### Inject a TGT into the session

- If you hold the user's TGT, inject it into the session's ticket cache; the second hop can then request service tickets for the target host (see [[Pass-the-Ticket]]).

### Enable CredSSP

- `CredSSP` forwards the user's actual credentials to the first host so it can reuse them for the second hop.
- It's convenient but leaves reusable credentials on the first host, which is a security risk. Enable it only where authorized.

### Register a RunAs session configuration

- Register a PowerShell `PSSessionConfiguration` (a session endpoint) that runs under a fixed account. Connections to that endpoint act with the configured account's credentials, so the second hop is authenticated.

## Kerberos delegation: the designed solution

- **Kerberos delegation** exists specifically to solve the double hop problem: it lets the first host obtain a ticket for the second host *on the user's behalf* (see [[Kerberos#Kerberos delegation]]).
- A host configured for [[Kerberos#Unconstrained delegation|unconstrained delegation]] receives the user's forwardable TGT, so the second hop succeeds with no workaround — which is also why unconstrained delegation is a serious security risk.
- **Constrained delegation** and **RBCD** permit the same forwarding, but only toward an explicit set of services.

## References and further reading

- [`Making the second hop in PowerShell Remoting — Microsoft Learn`](https://learn.microsoft.com/en-us/powershell/scripting/learn/remoting/ps-remoting-second-hop)
- [`about_Remote_Troubleshooting — Microsoft Learn`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_remote_troubleshooting)
- [`Kerberos Constrained Delegation Overview — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-constrained-delegation-overview)
