---
created: 2026-04-05
tags:
  - remote_access
  - SSH
  - network_services
color: "linear-gradient(45deg, #23d4fd 0%, #3a98f0 50%, #b721ff 100%)"
---
## SSH

>**SSH (Secure Shell)** is a cryptographic network protocol designed for operating network services security over an unsecured network. 

- The most notable application of SSH is **remote login** and **command-line execution**. 
- SSH Operates on a client-server model: SSH clients connect to SSH servers.

>[!important] SSH server listens on TCP port `22` by default.

- SSH operates as a layered protocol suite, and consists of three main components:
	- The **transport layer** — provides server authentication, confidentiality, and integrity.
	- The **user authentication protocol** — validates the user to the server.
	- The **connection protocol** — multiplexes the encrypted tunnel unto multiple logical channels (channels, PTYs, port forwarding, etc.).

>[!note] For more on how SSH works, see [[How SSH works]].
## Connecting over SSH

- Connect to an SSH server:

```bash
ssh username@<target>
```

>[!interesting]+ SSH authentication from the client's perspective
> - After the initial client-server negotiation, the server announces allowed authentication methods.
> - Based on what methods are available, SSH client chooses chooses how to authentication. It follows a priority order defined by:
> 	- Your SSH config (`~/.ssh/config`)
> 	- The system-wide config (`/etc/ssh/ssh_config`)
> 	- Available private keys in your agent (`ssh-agent`)
> 	- Keys in `~/.ssh/`
> 	- Command-line flags (`-i`, `-o`, etc.)
> - By default, OpenSSH:
> 	1. Offers public keys it finds. If not keys found, skip the step.
> 	2. If the server rejects the keys (e.g., wrong keys, or server is configured password-only, then it tries password authentication (if allowed).

- Specify the private key:

```bash
ssh -i ~/.ssh/private_key username@<target>
```
## Enumeration

### Banner grabbing

- Netcat:

```bash
nc -vn <target> 22
```

>[!note]+ Option breakdown
>- `-n`: Prevent DNS or service lookups on hostnames.
>- `-v`: Verbose output.
### Nmap scanning

- Check default SSH ports and run version scan:

```bash
sudo nmap -sV -p 22 <target>
```

> [!tip]+
> - Basic port scanning + version detection — in case you suspect non-standard ports:
> 
> ```bash
> sudo nmap -sV -p- <target>
> ```

- Run default SSH scripts:

```bash
sudo nmap -sV -sC -p 22 <target>
```

- Run all SSH-related scripts:

```bash
nmap -p 22 --script "ssh-*" <target>
```

>[!tip]+ Nmap SSH scripts
> 
> - List Nmap scripts for SSH:
> 
> ```bash
> ls -l /usr/share/nmap/scripts/*ssh*
> ```
> 

- Common Nmap SSH scripts: 

| Script                                                                                      | Categories                     | Description                                                                                                        |
| ------------------------------------------------------------------------------------------- | ------------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| [`ssh-auth-methods`](https://nmap.org/nsedoc/scripts/ssh-auth-methods.html)                 | `auth`, `intrusive`            | Enumerate supported SSH authentication methods (e.g., password, public key) by initiating a partial login attempt. |
| [`ssh-brute`](https://nmap.org/nsedoc/scripts/ssh-brute.html)                               | `auth`, `intrusive`, `brute`   | Perform brute-force password guessing against SSH servers using username/password combinations.                    |
| [`ssh-hostkey`](https://nmap.org/nsedoc/scripts/ssh-hostkey.html)                           | `safe`, `default`, `discovery` | Retrieve SSH host keys and fingerprints; can compare them against `known_hosts` for validation.                    |
| [`ssh-publickey-acceptance`](https://nmap.org/nsedoc/scripts/ssh-publickey-acceptance.html) | `auth`, `intrusive`            | Test whether specific public/private key pairs are accepted for authentication on the SSH server.                  |
| [`ssh-run`](https://nmap.org/nsedoc/scripts/ssh-run.html)                                   | `intrusive`                    | Execute arbitrary commands on the remote SSH server using provided credentials and return output.                  |
| [`ssh2-enum-algos`](https://nmap.org/nsedoc/scripts/ssh2-enum-algos.html)                   | `safe`, `discovery`            | Enumerate supported SSHv2 algorithms (key exchange, encryption, MAC, compression).                                 |
| [`sshv1`](https://nmap.org/nsedoc/scripts/sshv1.html)                                       | `safe`, `discovery`, `vuln`    | Detect whether the server supports the insecure and deprecated SSH protocol version 1.                             |

- Enumerate allowed authentication methods by attempting a login:

```bash
nmap -p 22 --script ssh-auth-methods --script-args="ssh.user=test" <target>
```

- Brute-force SSH credentials:

```bash
nmap -p 22 --script ssh-brute --script-args userdb=users.txt,passdb=/usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt <target>
```

- Retrieve SSH host keys:

```bash
nmap -p 22 --script ssh-hostkey <target>
```

- Test whether given SSH keys are accepted for authentication:

```bash
nmap -p 22 --script ssh-publickey-acceptance --script-args "ssh.usernames={'root'},ssh.privatekeys={'id_rsa'}" <target>
```

- Execute a command on the remote system via SSH (requires valid credentials):

```bash
nmap -p 22 --script ssh-run --script-args "ssh.username=root,ssh.password=toor,ssh-run.cmd='id'" <target>
```

- List supported SSH algorithms:

```bash
nmap -p 22 --script ssh2-enum-algos <target>
```

- Detect if insecure SSH version `1` is supported:

```bash
nmap -p 22 --script sshv1 <target>
```
### ssh-audit

>[`ssh-audit`](https://github.com/jtesta/ssh-audit) is a tool for automated SSH server and client configuration auditing.

- `ssh-audit` works both on Linux and Windows, supports Python `3.9`-`3.13`, and has no dependencies. 

- Key features:
	- Analyze SSH server and client configuration.
	- Banner grabbing, device/software OS detection, compression detection.
	- Gathering key-exchange, host-key, encryption and message authentication code algorithms.
	- Output algorithm security information (available since, removed/disabled, unsafe/weak/legacy, etc).
	- Output algorithm recommendations.
	- Analyze SSH version compatibility based on algorithm information.
	- Historical information from OpenSSH, Dropbear SSH, and `libssh`.
	- Policy scans to ensure adherence to a hardened/standard configuration.

- Basic server auditing:

```bash
ssh-audit <target>
```

- Non-standard port:

```bash
ssh-audit <target>:2222
```

- Multiple targets (one line per target, `HOST:[:PORT]`):

```bash
ssh-audit -T servers.txt
```

>[!tip]+
> - Audit client configuration (listens on port `2222` by default):
> 
> ```bash
> ssh-audit
> ```
> 

#### Option reference

| Option                    | Description                                          |
| ------------------------- | ---------------------------------------------------- |
| `-h`, `--help`            | Show help message and exit.                          |
| `-4`, `--ipv4`            | Force IPv4 usage.                                    |
| `-6`, `--ipv6`            | Force IPv6 usage.                                    |
| `-b`, `--batch`           | Enable batch output (no headers, implies verbose).   |
| `-c`, `--client-audit`    | Start a server to audit SSH client configuration.    |
| `-d`, `--debug`           | Enable debug output.                                 |
| `-g`, `--gex-test`        | Perform Diffie-Hellman group exchange modulus tests. |
| `-j`, `--json`            | Output results in JSON format.                       |
| `-l`, `--level`           | Set minimum output level (`info`, `warn`, `fail`).   |
| `-L`, `--list-policies`   | List built-in audit policies.                        |
| `-M`, `--make-policy`     | Generate a policy file from a target server.         |
| `-m`, `--manual`          | Show manual page.                                    |
| `-n`, `--no-colors`       | Disable colored output.                              |
| `-P`, `--policy`          | Run audit using a specified policy.                  |
| `-p`, `--port`            | Specify target or listening port.                    |
| `-T`, `--targets`         | Load targets from file.                              |
| `-t`, `--timeout`         | Set connection/read timeout (seconds).               |
| `-v`, `--verbose`         | Enable verbose output.                               |
| `--conn-rate-test`        | Test connection rate for DoS susceptibility.         |
| `--dheat`                 | Perform DHEat DoS attack test.                       |
| `--get-hardening-guide`   | Fetch hardening guide for a platform.                |
| `--list-hardening-guides` | List available hardening guides.                     |
| `--lookup`                | Lookup algorithm information without scanning.       |
| `--skip-rate-test`        | Skip connection rate test during audit.              |
| `--threads`               | Number of threads for multi-target scans.            |

## SSH attack surface


- **Information leak**    
    - SSH is surprisingly talkative _before_ authentication. A simple TCP connection and banner exchange can reveal:
        - **Software and version** — OpenSSH, Dropbear, `libssh`, proprietary appliances. Version strings often map directly to known CVEs.
        - **Host key algorithms** — RSA, ECDSA, ED25519; key lengths; SHA‑1 vs SHA‑256 fingerprints.
        - **Supported cryptographic algorithms** — KEX, ciphers, MACs, compression. Legacy algorithms (CBC, SHA‑1, DH‑group1) are a red flag.
        - **Authentication methods** — password, public-key, keyboard‑interactive, GSSAPI, host-based.
        - **Timing behavior** — subtle differences in failure responses can leak whether a username exists or whether a key is “recognized.”
    - All of this happens without logging in. A misconfigured SSH daemon can unintentionally expose the age, configuration quality, and even OS family of the host.
        
- **Weak or legacy cryptography**
    - SSH supports a wide range of cryptographic primitives, and older servers often keep legacy algorithms enabled for compatibility.
    - Weaknesses include:
        - **SHA‑1 host keys** (`ssh-rsa`)
        - **1024‑bit RSA keys**
        - **CBC-mode ciphers**
        - **`diffie-hellman-group1-sha1`** (1024‑bit DH)
        - **`arcfour`** (RC4)
    - This doesn't immediately break SSH, but can be used in downgrade attacks and signal that the system is likely old and may have other unpatched issues.

- **Password authentication**
    - If password authentication is enabled, SSH becomes a target for brute-force attacks.

>[!note] Timing differences or PAM messages can reveal valid usernames.

        
- **SSH key mismanagement**
    - Public key authentication is strong — _if_ keys are handled properly. In practice, many environments suffer from:
        - **Unprotected private keys** — stored without passphrases, world-readable, or left in backups.
        - **Key reuse** — the same key pair used across dozens of servers.
        - **Stale authorized_keys entries** — ex‑employees, old automation keys, forgotten CI/CD keys.
        - **Overly permissive key options** — missing `from=`, `command=`, or `no-agent-forwarding` restrictions.
    - A single leaked private key can silently unlock large parts of an infrastructure.
        
- **Agent forwarding abuse**
    - SSH agent forwarding is convenient but dangerous. When enabled:
        - The remote host can request signatures from your agent.
        - The private key never leaves your machine, but the remote host can _use_ it.
    - If that remote host is compromised, the attacker can pivot into other systems using your forwarded agent. This is a classic lateral movement vector in real intrusions.
        
- **Port forwarding and tunneling**
    - SSH supports:
        - **Local port forwarding** (L → R)
        - **Remote port forwarding** (R → L)
        - **Dynamic forwarding** (SOCKS proxy)
    - Misconfigurations can allow:
        - Bypassing firewalls
        - Exposing internal services externally
        - Creating covert tunnels
        - Pivoting deeper into the network
    - Many organizations underestimate how much network access SSH forwarding implicitly grants.

- **Misconfigured access controls**
    - SSH’s access control model is powerful but easy to misconfigure:
        - `PermitRootLogin yes` — direct root access over SSH.
        - `AllowUsers` / `AllowGroups` not set — all system users can attempt SSH.
        - Missing rate limiting — unlimited authentication attempts.
        - Weak PAM configuration — unexpected fallback authentication paths.
    - These aren’t “exploits,” but they dramatically widen the attack surface.
        
- **Vulnerable SSH implementations**
    - While rare, SSH daemons and libraries do occasionally have real vulnerabilities:
        - Memory corruption bugs in older OpenSSH versions.
        - Authentication bypasses (e.g., the 2018 `libssh` bug).
        - Dropbear issues in embedded devices.
    - These are high‑impact because SSH typically runs as root and is exposed to the internet.
        
- **Post-authentication escalation**
    - Once an attacker gains _any_ SSH access (legitimate or stolen credentials), the attack surface expands:
        - **Sudo misconfigurations** — passwordless sudo, wildcard commands.
        - **Writable** `.ssh` **directory** — persistence via authorized_keys injection.
        - **SSH config injection** — adding `ProxyJump`, `IdentityFile`, or forwarding options.
        - **Subsystem abuse** — SFTP or custom subsystems with excessive privileges.
    - SSH is often the first foothold in a chain of privilege escalation and lateral movement.


## Brute-forcing credentials

- Medusa: 

```bash
medusa -M ssh -h <target> -u user@example.com -P /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt -n 2222 -e ns
```

>[!note]+ Option breakdown
>- `-M`: Medusa mode (protocol).
>- `-h`: Target host.
>- `-n`: Target port.
>- `-u`: Username to test (`-U` to brute-force usernames, too).
>- `-P`: Password wordlist.
>- `-e n`: Check for empty passwords.
>- `-e s`: Check for passwords matching the username. 

- Hydra:

```bash
hydra -l user@example.com -P /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt ssh://<target>
```

- Non-standard port:

```bash
hydra -l user@example.com -P /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt ssh://<target>:2222
```

```bash
hydra -L usernames.txt -P passwords.txt -s 2222 <target> ssh
```

- Nmap [`ssh-brute`](https://nmap.org/nsedoc/scripts/ssh-brute.html):

```bash
nmap -p 22 --script ssh-brute --script-args userdb=users.txt,passdb=/usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt <target>
```

>[!note] See [[Password wordlists and default credentials]].
## Post-exploitation

### File transfers

>[!note] See [[Linux_file_transfers#SCP and SSH-based transfers]].
## References and further reading

- [`SSH (Secure Shell) — Hackviser`](https://hackviser.com/tactics/pentesting/services/ssh)
- [`SSH Pentstig -> Enumeration — cyberhalid`](https://cyberkhalid.github.io/posts/ssh-enum/)

