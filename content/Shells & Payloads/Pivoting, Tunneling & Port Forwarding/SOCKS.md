---
created: 2026-09-10
updated: 2026-09-12
tags:
  - pivoting
---

>[!abstract]+ **Scope**: the SOCKS proxy protocol; SOCKS4 vs SOCKS5; how SOCKS works and how a connection is established; common ways to obtain a SOCKS proxy through a pivot; routing tools through a proxy with `proxychains`.

## SOCKS

>**[SOCKS](https://en.wikipedia.org/wiki/SOCKS) (Socket Secure)** is a proxy protocol that relays TCP (and, in SOCKS5, UDP) connections between a client and a target through an intermediary proxy server.

- A SOCKS proxy accepts a connection from a client, opens a connection to the destination the client asks for, and relays bytes between the two.
- SOCKS is protocol-agnostic. While an HTTP proxy understands only web traffic, SOCKS carries almost any TCP (and UDP, with SOCKS5) traffic.
- This is possible because SOCKS operates at the **session layer** (Layer `5`), rather than the application layer (Layer `7`).

>[!note] A SOCKS proxy is transparent: it doesn't inspect or modify the packets.

- The client specifies the destination per connection, so one proxy reaches any host and port the proxy itself can reach. This is what makes SOCKS useful for pivoting: the proxy runs on (or is tunneled to) a machine inside the target network, and destinations are resolved and reached from that machine's position.

>[!warning] SOCKS carries stream and datagram connections, not raw packets. It can't transport anything that isn't a normal TCP or UDP connection. This means neither ICMP nor TCP `SYN` scans work through SOCKS.

### SOCKS versions

- The SOCKS protocol comes in two main versions:
	- **SOCKS4** is the original version; simple, limited to TCP connections only, works exclusively with IPv4, and doesn't support authentication. **SOCKS4a** extended SOCKS4 with domain name resolution on the proxy side.
	- **SOCKS5** (defined in [`RFC 1928`](https://datatracker.ietf.org/doc/html/rfc1928)) supports both TCP and UDP traffic, works with both IPv4 and IPv6, and provides multiple authentication mechanisms (no authentication, username/password per [`RFC 1929`](https://datatracker.ietf.org/doc/html/rfc1929), GSS-API).
- In practice, you'll use SOCKS5 almost exclusively.
### Establishing a SOCKS5 connection

- A SOCKS5 exchange (per `RFC 1928`) runs over TCP in three phases:
	1. **Method negotiation** — the client connects to the proxy and sends the authentication methods it supports. The proxy selects one and replies.
	2. **Authentication** — if the selected method requires it (for example username/password), the client and proxy complete that sub-negotiation.
	3. **Connection request** — the client sends a request carrying a command (`CONNECT`, `BIND`, or `UDP ASSOCIATE`), the destination address (IPv4, IPv6, or domain name), and the destination port.
- The proxy opens the requested connection to the target, then returns a reply with a status code and the bound address and port. On success, it relays application data between client and target for the life of the connection.
### Obtaining a SOCKS proxy through a pivot

- Common ways to stand up a SOCKS proxy into a target network:
	- **SSH dynamic forwarding (`ssh -D`)** — the SSH client opens a local SOCKS listener; the SSH server (pivot) makes each requested connection. See [[SSH port forwarding#Dynamic SSH port forwarding]].
	- **Plink (`plink -D`)** — SSH dynamic forwarding from a Windows client. See [[Plink]].
	- **Chisel** — SOCKS5 over a WebSocket/SSH transport, forward, or reverse. See [[Chisel#Forward tunnel]] and [[Chisel#Reverse tunnel]].
	- **`rpivot`** — reverse SOCKS4 proxy, for when the pivot can only connect outbound. See [[rpivot]].
	- **`sshuttle`** — SSH-based tunneling that behaves like a VPN rather than a plain SOCKS proxy. See [[sshuttle]].
	- **Meterpreter** — SOCKS proxy through an existing Meterpreter session. See [[Meterpreter tunneling]].

## `proxychains`

- Not every tool supports SOCKS natively. `proxychains` forces the TCP connections of a given program to pass through a SOCKS (or HTTP) proxy without the program's cooperation.

>[`proxychains`](https://github.com/haad/proxychains) forces any TCP connection made by a given application to route through a specified proxy. It supports TOR, SOCKS4, SOCKS5, and HTTP(S) proxies.

>[!interesting]+ How `proxychains` works
>- `proxychains` hooks network functions in dynamically linked programs using a preloaded shared library.
>- It sets `LD_PRELOAD` to load the custom `libproxychains.so` before the program's C library (`libc`). 
>- The library replaces network functions like `connect()`, `socket()`, `send()`, and `recv()` with versions that redirect connections to the configured proxy.
>
>>[!warning] **`proxychains` only works on dynamically linked programs**, and both `proxychains` and the target program must use the same dynamic linker (the same `libc`).

>[!note]+ Installation
>- Install from the package manager:
>```bash
>sudo apt install proxychains4
>```
>- Or build from source:
>```bash
>git clone https://github.com/haad/proxychains
>```
>```bash
>cd proxychains && \
>./configure && \
>make && \
>sudo make install
>```

### Configuring `proxychains`

- The  `proxychains` configuration file is located at `/etc/proxychains.conf` (or `/etc/proxychains4.conf` for `proxychains-ng`).
- The `[ProxyList]` section defines the proxy in the form `<protocol> <address> <port>`.

---

- To route traffic through a SOCKS5 proxy listening on `127.0.0.1:9050`, add the following line to the `[ProxyList]` section:

```bash
socks5 127.0.0.1 9050
```

- To use SOCKS4 instead of SOCKS5 (e.g., for [[rpivot]]):

```bash
socks4 127.0.0.1 1080
```

>[!note] Enable `proxy_dns` in the configuration file to resolve destination hostnames through the proxy. This keeps DNS queries off your local resolver.

### Routing tools through the proxy

- To route traffic from a program through the configured proxy, prefix the command with `proxychains`.

---

- Run a TCP connect scan of an internal host (`-n` prevents DNS lookup timeouts):

```bash
proxychains nmap -sT -Pn -n 172.16.5.19
```

>[!warning] SOCKS proxies relay TCP (and, for SOCKS5, UDP) connections, but not raw packets. Only a TCP connect scan (`nmap -sT`) works through a proxy; `SYN`, UDP, and other scans that craft raw packets don't.

>[!warning] `nmap` through `proxychains` can be slow and can be unreliable.

---
- Fetch an internal web page:

```bash
proxychains curl http://172.16.5.19
```

>[!tip]+ 
>- `curl` supports SOCKS proxies natively:
>```bash
>curl -x socks5://127.0.0.1:9050 http://172.16.5.19
>```

---

- List SMB shares on an internal file server:

```bash
proxychains smbclient -L //172.16.5.19/ -U jdoe
```

---

- Open an RDP session to an internal host:

```bash
proxychains xfreerdp /v:172.16.5.19 /u:victor /p:pass@123
```

---
- Connect via SSH to an internal host:

```bash
proxychains ssh jdoe@172.16.5.19
```

## References and further reading

- [`SOCKS — Wikipedia`](https://en.wikipedia.org/wiki/SOCKS)
- [`RFC 1928 — SOCKS Protocol Version 5`](https://datatracker.ietf.org/doc/html/rfc1928)
- [`RFC 1929 — Username/Password Authentication for SOCKS V5`](https://datatracker.ietf.org/doc/html/rfc1929)
- [`proxychains-ng — GitHub`](https://github.com/rofl0r/proxychains-ng)
- [`proxychains — GitHub`](https://github.com/haad/proxychains)
