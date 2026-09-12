---
created: 2026-09-05
updated: 2026-09-12
tags:
  - pivoting
  - ssh
---
>[!abstract]+ **Scope**: SSH port forwarding and tunneling (OpenSSH); local port forwarding (`-L`), remote port forwarding (`-R`), dynamic SOCKS proxying (`-D`), reverse dynamic SOCKS forwarding, multi-hop jump hosts (`-J`); background execution and tunnel verification.
## SSH port forwarding

>**SSH port forwarding**, or **SSH tunneling**, allows you to create **encrypted connections** between your local system and the target host using SSH, and access services that are otherwise restricted by firewalls or network policies.

### SSH channels

- When an SSH client connects to an SSH server, they first establish a TCP connection (by default, to TCP port `22` on the SSH server). SSH then performs key exchange, creates an encrypted SSH transport, and authenticates the client.

- After authentication, SSH can create **multiple independent logical channels** inside that same encrypted connection; this is called **multiplexing**. A channel behaves like a separate data stream, even though all channels share the same underlying TCP connection.

- Common SSH channel types include:

	- `session` — used for interactive shells, command execution, and subsystems such as SFTP (Secure File Transfer Protocol).

	- `direct-tcpip` — opened by the SSH client when it wants the SSH server to establish a TCP connection to another destination. This is used for **local port forwarding (`-L`)** and **dynamic SOCKS forwarding (`-D`)**. Each forwarded TCP connection normally receives its own channel.

	- `forwarded-tcpip` — opened by the **SSH server** when a TCP connection arrives at a *remotely forwarded listener* previously created with **remote port forwarding (`-R`)**.

>[!important] The channels are **logical streams inside a single SSH connection**, not separate TCP connections.

### SSH port forwarding types

- OpenSSH provides three primary port forwarding mechanisms:

	- **Local port forwarding (`-L`)**
		- The **SSH client opens a listening TCP socket on the client side**; connections to that socket are forwarded through the SSH tunnel to the SSH server. 
		- The **SSH server then opens a TCP connection to the configured destination host and port**.
		- Use local port forwarding when you want to access a service reachable only from the SSH server through a local port on your machine.

	- **Remote port forwarding (`-R`)**
		- The **SSH server opens a listening TCP socket on the server side**. 
		- When a connection is received on that remote port, the SSH server sends the connection back through the SSH tunnel to the SSH client.
		- The **SSH client then opens a TCP connection to the configured destination host and port**.
		- Use remote forwarding when you want a service reachable **from the SSH client side** to become accessible through a port on the SSH server.

	- **Dynamic port forwarding (`-D`)**
		- The **SSH client opens a local SOCKS proxy listener**.
		- Applications connect to this SOCKS proxy and specify the destination host and port for each connection.
		- The SSH client forwards each requested connection through the SSH tunnel, and the **SSH server opens the corresponding TCP connection to the requested destination**.
		- Unlike `-L`, the destination is **not fixed when the SSH command is started**; it is selected dynamically by the SOCKS client for each connection.

> [!important] In local (`-L`) and dynamic (`-D`) port forwarding, your machine acts as the SSH client and *pulls* traffic through the tunnel. In remote (`-R`) port forwarding, the remote pivot listens and *pushes* traffic back into your client tunnel.

> [!important] Target addresses are always resolved and accessed from the **perspective of the remote SSH server**, not your local system. 
>- For example, `localhost:3306` inside a tunnel reaches MySQL *on the remote pivot host itself*; `172.16.5.19:3389` reaches an internal host *on the pivot's local subnet*.

### On bind addresses

- The bind address defines which network interface accepts incoming connections on a forwarded socket:
	- **`127.0.0.1`/`localhost`** (default) — Localhost; listens only on the loopback interface; accessible only to local processes on that machine.
	- **`0.0.0.0`** (`*`/`INADDR_ANY`) — Listens on all IPv4 interfaces; accessible to hosts on any connected networks.
	- **Specific IP address** (e.g., `192.168.1.11`) — Binds the socket only to the specified physical or virtual network adapter.  
	- **`::1`/`::`** — IPv6 equivalent for loopback (`::1`) and all-interfaces (`::`).

> [!warning] Binding a forwarded port to `0.0.0.0` exposes the tunneled service to every host on connected network segments. Keep sensitive pivots bound to `127.0.0.1` unless external network access is required.
## Local SSH port forwarding

>**Local port forwarding (`-L`)** creates a TCP listener on the SSH client and forwards connections accepted by that listener through the encrypted SSH tunnel to the SSH server. The SSH server then establishes a separate TCP connection to the configured target host and port.

>[!important] In local port forwarding, **your attacker machine is the SSH client**, and the **pivot is the SSH server**.

![[local_SSH_port_forwarding.svg]]

- **Connection flow**:
	1. Your SSH client establishes an encrypted SSH tunnel to the pivot and authenticates to the SSH server. 
	2. The client creates a local listening socket on the configured bind address and port.
	3. When a local application connects to the listener, the SSH client intercepts the connection and forwards it through the encrypted tunnel to the SSH server, via a `direct-tcpip` channel.
	4. The SSH server receives a port forwarding request, and establishes a separate TCP connection to the target host and port. All traffic carried through the `direct-tcpip` channel is decrypted and forwarded to the target.
	5. Response traffic follows the same path in reverse, through the existing SSH channel and back to the local application.

- **Primary use cases**:
	- Accessing services bound to the loopback interface on the pivot.
	- Accessing services on the internal network that is reachable from the pivot (but not directly reachable from your attacker machine), such as web applications, databases, SMB shares, WinRM, LDAP, etc.
### Command syntax

```bash
ssh -N -L [bind_address:]local_port:target_host:target_port user@ssh_server
```

- **`bind_address` (optional)**: Address on the SSH client on which the local listener is created; if omitted, defaults to `localhost`.
- **`local_port`**: TCP port on which the SSH client listens for incoming connections.
- **`target_host`**: Destination host to which the SSH server connects (as seen from the SSH server's perspective).
- **`target_port`**: TCP port of the destination service.
- **`ssh_server`**: SSH server through which the connection is forwarded (the pivot).
- **`user`**: Account used to authenticate to the SSH server.

| Option | Description                                                                       |
| ------ | --------------------------------------------------------------------------------- |
| `-L`   | Configure local TCP port forwarding.                                              |
| `-N`   | Do not execute a remote command; maintain the SSH connection for forwarding only. |
| `-f`   | Place the SSH client in the background after authentication.                      |

>[!example]+
>- Expose an administrative panel bound to the loopback interface on the pivot (`localhost:8080`) to local port `8080`:
>```bash
>ssh -N -f -L 8080:localhost:8080 user@10.10.11.5
>```
>- Connect to the forwarded service through the local listener:
>```bash
>curl http://localhost:8080
>```

>[!example]+
> - Expose RDP service on an internal domain controller (`172.16.5.19:3389`) locally on port `3300`:
> 
> ```bash
> ssh -N -f -L 3300:172.16.5.19:3389 user@10.10.11.5
> ```
> - Connect to the forwarded RDP service through the local listener:
>```bash
>xfreerdp /v:localhost:3300 /u:jdoe /p:'passwd123'
>```

>[!example]+
> - Forward multiple ports over a single SSH connection (each forwarded connection receives a separate `direct-tcpip` channel):
> 
> ```bash
> ssh -N -f \
>     -L 8080:172.16.5.10:80 \
>     -L 3306:172.16.5.11:3306 \
>     -L 3389:172.16.5.19:3389 \
>     user@10.10.11.5
> ```

## Remote SSH port forwarding

- Local port forwarding requires the pivot to accept inbound connections from your machine. If inbound connections to the pivot are blocked by a firewall or NAT, but outbound connections from the pivot are allowed, use **remote port forwarding** instead.

>**Remote port forwarding (`-R`)** creates a TCP listener on the SSH server and forwards connections accepted by that listener through the encrypted SSH connection to the SSH client. The SSH client then establishes a separate TCP connection to the configured target host and port.

>[!important] In remote port forwarding, **your attacker machine is the SSH server**, and the **pivot is the SSH client**.

![[remote_SSH_port_forwarding.svg]]

- **Connection flow**:
	1. The pivot initiates an outbound SSH connection to the SSH server running on your attacker machine and authenticates to it.
	2. The SSH client (the pivot) requests remote port forwarding, and the server (on your machine) creates a listening socket on the specified bind address and port.
	3. When a connection reaches the listener on your attacker machine, the SSH server intercepts the connection and forwards it through the encrypted tunnel to the SSH client, via a `forwarded-tcpip` channel.
	4. The SSH client on the pivot receives a port forwarding request and establishes a separate connection to the specified target.
	5. Traffic flows between the connection accepted by the SSH server and the destination connection established by the client. 

- **Primary use cases**:
	- Accessing a service bound only to a loopback interface on the pivot — when the pivot can initiate outbound connections but can't accept inbound traffic from your attacker machine.  
	- Accessing services on the internal network that is reachable from the pivot but not directly reachable from your attacker machine — when the pivot can initiate outbound connections but can't accept inbound traffic from your machine.

### Command syntax

```bash
ssh -N -R [bind_address:]remote_port:target_host:target_port user@ssh_server
```

>[!important] The `ssh -R` command is executed on the **pivot**, because the pivot is the SSH client.

- **`bind_address` (optional)**: Address on the SSH server on which the remote listener is created; if omitted, defaults to `localhost`.
- **`remote_port`**: TCP port on which the SSH server (your attacker machine) listens for incoming connections.
- **`target_host`**: Destination host to which the SSH client connects (as seen from the SSH client's perspective, i.e., the pivot).
- **`target_port`**: TCP port of the destination service.
- **`ssh_server`**: SSH server on which the remote listener is created (your attacker machine).
- **`user`**: Account used by the pivot to authenticate to the SSH server on your machine.

| Option | Description                                                                       |
| ------ | --------------------------------------------------------------------------------- |
| `-R`   | Configure remote TCP port forwarding.                                             |
| `-N`   | Do not execute a remote command; maintain the SSH connection for forwarding only. |
| `-f`   | Place the SSH client in the background after authentication.                      |

>[!warning] OpenSSH remote forwards are restricted to the server's loopback interface by default. Binding a remote forward to a non-loopback address requires you to allow that explicitly via SSH server configuration (`GatewayPorts`).

>[!note] Remote forwarding mirrors local forwarding in reverse: your machine acts as the SSH server and listens for connections initiated by the pivot (the SSH client). Use this technique when inbound traffic to the pivot is filtered or heavily monitored.

>[!example]+
> - Make an administrative panel bound to `localhost:8080` on the pivot accessible through port `8080` on the attacker machine:
> 
> ```bash
> ssh -N -f -R 8080:localhost:8080 attacker@10.10.11.11
> ```
> 
> - This command is executed **on the pivot**.
> - From your attacker machine, connect to the remote-forward listener:
> 
> ```bash
> curl http://localhost:8080
> ```
> 
> - The `localhost` used by `curl` refers to **your attacker machine**, where the SSH server created the remote-forward listener.
> - The `localhost` in `-R 8080:localhost:8080` refers to the **pivot**, because the SSH client on the pivot establishes the TCP connection to the destination listening on `localhost`.

>[!example]+
> - Make RDP on an internal domain controller (`172.16.5.19:3389`) reachable through port `3300` on your attacker machine:
> 
> ```bash
> ssh -N -f -R 3300:172.16.5.19:3389 attacker@10.10.11.11
> ```
> 
> - From your attacker machine, connect to the remote-forward listener:
> 
> ```bash
> xfreerdp /v:localhost:3300 /u:jdoe /p:'passwd123'
> ```

>[!example]+
> - Configure multiple remote forwards over a single SSH connection (each forwarded connection receives a separate `forwarded-tcpip` channel):
> 
> ```bash
> ssh -N -f \
>     -R 8080:172.16.5.10:80 \
>     -R 3306:172.16.5.11:3306 \
>     -R 3389:172.16.5.19:3389 \
>     attacker@10.10.11.11
> ```

### Allowing remote listeners to bind to non-loopback addresses

- By default, remote forwarded ports bind only to loopback (`127.0.0.1` / `localhost`) on the SSH server. Only processes running locally on the server can connect to the forwarded port.
- If you want to bind the listener to `0.0.0.0` or external network interfaces, configure `GatewayPorts` in `/etc/ssh/sshd_config`:

```bash
# /etc/ssh/sshd_config
GatewayPorts yes
```

- Restart the SSH server to apply the changes:

```bash
sudo systemctl restart sshd
```
## Dynamic SSH port forwarding

- Local and remote port forwarding map a listening port to a **predefined target host and port**. This works well when the destination service is known in advance, but becomes inconvenient when you need to access many different hosts and ports on an internal network.
- Instead of defining the destination in the SSH command, you can create a **SOCKS proxy**. Each application specifies its own destination through the SOCKS protocol.

>**Dynamic port forwarding (`-D`)** creates a SOCKS proxy listener on the SSH client. Applications use this listener to connect to arbitrary destination hosts and ports through the proxy. 

>[!important] In dynamic port forwarding, **your attacker machine is the SSH client**, and the **pivot is the SSH server**.

>[!note] The SOCKS listener is created on your attacker machine; the requested destinations are interpreted from the pivot's perspective. 

- OpenSSH supports both **SOCKS4 and SOCKS5** for dynamic forwarding.

>[!note] To learn more about SOCKS, see [[SOCKS]].

- **Connection flow**:
	1. Your SSH client establishes an encrypted SSH tunnel to the pivot and authenticates to the SSH server. 
	2. The client creates a local SOCKS proxy listening socket on the configured bind address and port.
	3. A local application connects to the listener and specifies the destination host and port. The client intercepts the connection and forwards it through the encrypted tunnel to the SSH server, via a `direct-tcpip` channel.
	4. The SSH server receives a port forwarding request, and establishes a separate TCP connection to the target host and port. All traffic carried through the `direct-tcpip` channel is decrypted and forwarded to the target.
	5. Response traffic follows the same path in reverse, through the existing SSH channel and back to the local application.
	6. Additional SOCKS connections can request different destination hosts and ports. Each TCP connection is carried through its own `direct-tcpip` channel (all channels are multiplexed over the same underlying SSH connection).

- **Primary use cases**:
	- Accessing multiple hosts and TCP services on an internal network using local port forwarding but without configuring a separate `-L` forward for every destination.
	- Performing TCP-based enumeration and interacting with internal services through a pivot when the attacker machine has no direct route to the internal network.

### Command syntax

```bash
ssh -N -D [bind_address:]local_port user@ssh_server
```

- **`bind_address` (optional)**: Address on the SSH client on which the local listener is created; if omitted, defaults to `localhost`.
- **`local_port`**: TCP port on which the SSH client runs the SOCKS proxy.
- **`ssh_server`**: SSH server through which the connection is forwarded (the pivot).
- **`user`**: Account used to authenticate to the SSH server.

| Option | Description                                                                       |
| ------ | --------------------------------------------------------------------------------- |
| `-D`   | Configure local dynamic port forwarding using a SOCKS proxy.                      |
| `-N`   | Do not execute a remote command; maintain the SSH connection for forwarding only. |
| `-f`   | Place the SSH client in the background after authentication.                      |

>[!note] Unlike `-L` and `-R`, the `-D` command doesn't contain `target_host:target_port`. The destination is specified individually by each application connecting through the proxy.

>[!example]+
> - Create a SOCKS proxy on local port `9050` and forward connections through the pivot at `10.10.11.5`:
> 
> ```bash
> ssh -N -f -D 9050 user@10.10.11.5
> ```
> 
> - The SSH client now listens locally on port `9050`. Unlike a local forward, this listener is not associated with a single predefined destination. For example, one application can request a connection to `172.16.5.10:80`, while another can simultaneously request `172.16.5.19:3389`.
> - Both connections traverse the same SSH connection, but each is carried over a separate `direct-tcpip` channel and results in a separate outbound TCP connection from the pivot.
> ---
> - Access an internal web application using `curl` through the SOCKS5 proxy:
> 
> ```bash
> curl --socks5-hostname localhost:9050 http://172.16.5.10
> ```
> 
> - `curl` connects to the SOCKS listener at `localhost:9050` and requests a connection to `172.16.5.10:80`. The SSH client carries this request through SSH, and the pivot establishes the final TCP connection to the internal web server.
> 
> - When you use a hostname rather than an IP address, `--socks5-hostname` instructs `curl` to pass the hostname to the SOCKS proxy instead of resolving it locally:
> 
> ```bash
> curl --socks5-hostname localhost:1080 http://internal.example.com
> ```

- Primary ways to connect via SOCKS proxy:
	- `curl --socks5-hostname localhost:9050 http://internal.example.com`
	- Browser SOCKS configuration
	- `proxychains`

>[!warning] OpenSSH dynamic port forwarding (`-D`) supports only TCP streams. It doesn't support UDP or raw IP packets (such as ICMP or SYN packets).

### Reverse dynamic port forwarding

- In OpenSSH 7.6+, `-R` supports dynamic SOCKS forwarding without specifying a static target host. The remote SSH server creates a SOCKS proxy that routes connections back through your SSH client.
- Use reverse dynamic forwarding when the pivot needs to route traffic through your machine, or when internal hosts need outbound access through your network:

```bash
ssh -N -R 9050 user@10.10.11.5
```

- In this setup, the SSH server on the pivot listens on port `9050` as a SOCKS4/SOCKS5 proxy. Tools running on the pivot (or internal hosts, if `GatewayPorts` is enabled) point to `127.0.0.1:9050` to route their TCP connections out through your machine.

### `proxychains`

- Not every tool supports SOCKS natively. `proxychains` forces a program's TCP connections through a SOCKS proxy — for example the `-D` listener created above.
- Configure it with the SSH SOCKS listener (e.g., `socks5 127.0.0.1 9050`), then prefix commands with `proxychains`. See [[SOCKS#proxychains]]

## Jump hosts and multi-hop forwarding (`-J`)

- When the target host is reachable only through one or more intermediate bastion hosts, use `-J` (`ProxyJump`) to route your SSH session across the chain automatically.

- Connect to a target through a single jump host:

```bash
ssh -J user1@10.10.11.5 user2@172.16.5.19
```

- Chain through multiple jump hosts (comma-separated):

```bash
ssh -J user1@10.10.11.5,user2@172.16.5.19 user3@192.168.1.50
```

- Forward a local port through a jump host chain:

```bash
ssh -J user1@10.10.11.5 -N -f -L 8443:192.168.1.50:443 user2@172.16.5.19
```

## Managing and verifying SSH tunnels

- Verify that the local forwarded port is listening:

```bash
ss -tulpn | grep 9050
```

- Alternatively, inspect listening sockets with `lsof`:

```bash
lsof -i :9050
```

- Identify running background SSH forwarding processes:

```bash
pgrep -af "ssh.*-N"
```

- Terminate a background SSH tunnel:

```bash
pkill -f "ssh.*9050"
```

## Appendix: SSH server configuration options relevant to port forwarding

>[!important] By default, the SSH server configuration file is located at `/etc/ssh/sshd_config`.

- Check port forwarding configuration on an SSH server:

```bash
grep -E "AllowTcpForwarding|GatewayPorts|PermitTunnel|AllowAgentForwarding|AllowStreamLocalForwarding" /etc/ssh/sshd_config
```

- **[`AllowTcpForwarding`](https://man.archlinux.org/man/sshd_config.5.en#AllowTcpForwarding)** — controls whether TCP port forwarding is allowed on the server:
	- `no`: Disables both local (`-L`) and remote (`-R`) port forwarding.
	- `yes` (or `all`): Allows both local and remote port forwarding.
	- `local`: Permits only local port forwarding (`-L`); disables remote port forwarding (`-R`).
	- `remote`: Permits only remote port forwarding (`-R`); disables local port forwarding (`-L`).

>[!warning] If `AllowTcpForwarding` is set to `no`, no port forwarding is possible regardless of other settings.

- **[`GatewayPorts`](https://man.archlinux.org/man/sshd_config.5.en#GatewayPorts)**: Controls whether remote forwarded ports can bind to non-loopback addresses.
	- **`no`** (default): Remote forwarded ports can bind only to `localhost` (`127.0.0.1`). Only services running on the SSH server itself can connect to the forwarded port.
	- **`yes`**: Allows remote forwarded ports to bind to any address (`0.0.0.0`), making them accessible from any machine on the network.
	- **`clientspecified`**: Allows the SSH client to specify the listening address for remote forwarded ports manually.

- **[`AllowAgentForwarding`](https://man.archlinux.org/man/sshd_config.5.en#AllowAgentForwarding)**: Controls whether SSH agent forwarding is permitted (allows the remote host to see your SSH keys for further connections).
	- **`yes`** (default): Allows agent forwarding.
	- **`no`**: Disables agent forwarding. 

- **[`AllowStreamLocalForwarding`](https://man.archlinux.org/man/sshd_config.5.en#AllowStreamLocalForwarding)**: Specifies whether `StreamLocal` (Unix-domain socket) port forwarding is permitted.
	- **`yes` or `all`** (default): Allows `StreamLocal` forwarding.
	- **`no`**: Prevents all `StreamLocal` forwarding.
	- **`local`**: Allows local forwarding only.
	- **`remote`**: Allow remote forwarding only.

- **[`PermitTunnel`](https://man.archlinux.org/man/sshd_config.5.en#PermitTunnel)**: Controls Forwarding of TUN/TAP devices for Layer 2 or Layer 3 tunneling over SSH.
	- **`yes`**: Enables both point-to-point (Layer 3) and Ethernet (Layer 2) tunneling. 
	- **`point-to-point`**: Enables only Layer 3 tunneling.
	- **`ethernet`**: Enables only Layer 2 tunneling.
	- **`no`** (default): Disables TUN/TAP device forwarding.

>[!note] See [`sshd_config — man pages`](https://man.archlinux.org/man/sshd_config.5.en).

## References and further reading

- [`A Practical Guide to SSH Tunnels: Local and Remote Port Forwarding — Ivan Valichko, iximiuz Labs`](https://labs.iximiuz.com/tutorials/ssh-tunnels)
- [`SSH Port Forwarding: Local, Remote, and Dynamic Explained — Vinayak Baranwal, DigitalOcean`](https://www.digitalocean.com/community/tutorials/ssh-port-forwarding)
- [`SSH Tunneling: Examples, Command, Server Config — SSH Academy`](https://www.ssh.com/academy/ssh/tunneling-example)
- [`ssh — man pages`](https://man.archlinux.org/man/ssh.1.en)
- [`ssh_config — man pages`](https://man.archlinux.org/man/ssh_config.5.en)

