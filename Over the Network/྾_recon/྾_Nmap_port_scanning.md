---
created: 2025-08-31
tags:
  - nmap
---
## Port scanning

>**Port scanning** is a technique used to discover open ports on network devices. It reveals which services are accepting connections and helps map the attack surface of a target system.

- Scan ports with Nmap's default settings (TCP `SYN` scan if executed by privileged user, and TCP `Connect` if unprivileged):

```bash
sudo nmap TARGET
```

There are a total of **6 different states** for a scanned port you can get:

| State              | Description                                                                                                                                                                                                                                            |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `open`             | ◌ A service or application is actively listening and accepting connections or packets on this port.                                                                                                                                                    |
| `closed`           | ◌ The port is reachable but no application is listening on it.<br>◌ This indicates that the host is alive and responding, even thorough the port isn't used.<br>For example, a closed TCP port responds with TCP `RST` (reset) to connection attempts. |
| `filtered`         | ◌ Nmap can't determine whether the scanned port is open or closed because the target either doesn't respond (e.g., the probe packets are blocked or dropped by a firewall) or returns an error code.                                                   |
| `unfiltered`       | ◌ This state only occurs during the **TCP `ACK` scan**.<br>◌ The port is accessible (host responds), but Nmap can't determine if the port is open or closed.<br>                                                                                       |
| `open\|filtered`   | ◌ No response is received; Nmap can't distinguish whether the port is open of filtered.<br>This indicates that even if the port is open, a firewall may be blocking the probes.<br>                                                                    |
| `clised\|filtered` | ◌ This state only occurs during the **IP ID Idle scan**.<br>◌ Nmap can't determine whether the port is closed or filtered by a firewall.                                                                                                               |

For more information about TCP flags and TCP in general, see [[how_TCP_works]].

>[!interesting]+ Filtered packets
>There are two primary reasons why a port may be marked `filtered`:
>- **Dropped packets**
>	- A firewall silently discards the probe without sending any response.
>	- Nmap retries several times to find out if the previous packet was accidentally mishandled or not. The default retry limit is `10` ; you can change it with the `--max-retries` option.
>	- The scan typically takes longer if the packet is dropped than if it's filtered.
>- **Filtered packets**
>	- A firewall explicitly sends a response, such as a TCP `RST` (reset) packet or an ICMP unreachable error (type `3`), to indicate the probe is rejected. 
>	- It's a good idea to take a closer look at this port later.

>[!warning] The `PST` paradox
>In many TCP scans, the target responds with an `RST` packet if the port is **closed**.
>However, many firewalls and systems **send `RST` for any unsolicited packet** — even to open ports. Such behavior is especially known to pertain Microsoft Windows and Cisco devices.
>As a result, the port is marked `closed` when it should be `open|filtered`. This violates the specification and puts the scan reliability under questioning. 

>[!tip]+ To reduce the number of false negatives in the scan results, **combine multiple scan types**.
>For example, `-sS` (TCP `SYN`) may say the port is `closed`, but `-sA` (TCP `ACK` scan) marks it `open`. The port is likely open.

Nmap supports several port scan types:
- `-sS` TCP `SYN` scan, or stealth scan
- `-sT` TCP Connect scan
- `-sA` TCP `ACK` scan
- `-sU` UDP scan
- `-sN` TCP `NULL` scan
- `-sF` TCP `FIN` scan
- `-sX` TCP Xmas scan
- `-sY` SCTP `INIT` scan
- `-sA` TCP `ACK` scan
- `-sW` TCP Window scan
- `-sM` TCP Maimon scan
- `--scanflags` Custom TCP scan
- `-sI` TCP Idle scan

| Option        | Description                     |
| ------------- | ------------------------------- |
| `-sT`         | TCP Connect scan                |
| `-sS`         | TCP `SYN` scan, or stealth scan |
| `-sA`         | TCP `ACK` scan                  |
| `-sU`         | UDP scan                        |
| `-sN`         | `NULL` scan                     |
| `-sF`         | `FIN` TCP scan                  |
| `-sX`         | Xmas TCP scan                   |
| `-sY`         | SCTP `INIT` scan                |
| `-sA`         | `ACK` TCP scan                  |
| `-sW`         | TCP Window scan                 |
| `-sM`         | TCP Maimon scan                 |
| `--scanflags` | Custom TCP scan                 |
| `-sI`         | TCP Idle scan                   |

>[!important] Only one method may be used at a time, except that UDP scan (`-sU`) and any one of the SCTP scan types (`-sY`, `-sZ`) may be combined with any one of the TCP scan types.

## `-sS` TCP `SYN` scan, or stealth scan

>The **TCP `SYN` scan (`-sS`)**, aka **stealth scan** or **half-open scan**, sends **TCP `SYN` packets** to the target host, as if trying to establish a TCP connection. 
>If the target response with a TCP `ACK`/`SYN` packet, Nmap sends a TCP `RST` packet back to terminate the TCP handshake immediately.

```bash
sudo nmap 192.168.1.11
```

```bash
sudo nmap -sS 192.168.1.11
```

>[!warning] The TCP `SYN` scan requires root (raw packet) privileges.
>If run by an unprivileged user, Nmap falls back to to the **TCP `connect` scan (`-sT`)**, which is slower and detectable.

>[!interesting]
>More precisely, Nmap needs the `CAP_NET_RAW`, `CAP_NET_ADMIN`, and `CAN_NET_BIND_SERVICE` capabilities to perform a TCP `SYN` scan (on Linux).

During the scan, Nmap sends a **TCP `SYN` packet** to the specified port on the target system. Depending on the response, Nmap marks the port as either `open`, `closed`, or `filtered`:

| Port status | TCP response flags                                  | Description                                                                                                                                                                                            |
| ----------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `closed`    | `RST` (reset)                                       | If any packet is sent to a **closed** port (including TCP `SYN`), the target server will respond with a `RST` TCP packet.                                                                              |
| `open`      | `SYN`/`ACK`                                         | If the port is **open**, the target responds with `SYN`/`ACK`, trying to continue the TCP three-way handshake. <br>Nmap then sends an `RST` packet to terminate the half-open connection immediately.  |
| `filtered`  | No response or<br>ICMP unreachable error (type `3`) | If the packet sent by Nmap is dropped by a firewall, typically no response will be received. <br>Sometimes, however, firewalls may be configured to respond with an ICMP unreachable error (type `3`). |


>[!important] By default, Nmap scans the **top 1000 TCP ports** with the **TCP `SYN` scan (`-sS`)**, but **only if you run Nmap as root**.

- To scan **all ports**, from `0` to `65535`:

```bash
nmap -p- 192.168.1.11
```

- To scan **top 100 ports** from the Nmap database:

```bash 
nmap -F 192.168.1.11
```

- To send probes to the specified number of **top ports**:

```bash
nmap --top-ports=10 192.168.1.11 # to send probes to 10 top ports from the Nmap database
```

- To send probes to several **specific ports**:

```bash
nmap -p 22,80,443,139,445 192.168.1.11 # send probes to ports 22, 80, 443, 139, and 445
```

- To send probes to all **ports in a defined range**:

```bash
nmap -p 22-445 192.168.1.11 # send probes to all ports from 22 to 445
```

>[!note]+ Advantages of the TCP `SYN` scan
> 
> - **Stealth**
> 	- The TCP `SYN` scan is also known as **stealth scan** since it doesn't attract much attention. Since the scan doesn't complete the TCP handshake, and TCP connections are typically logged only once they have been fully established, the TCP `SYN` scan leaves fewer traces in logs and often goes unnoticed.
> 
> - **Fast**
> 	- The TCP `SYN` scan is **fast**: it can prove *thousands* of ports per second on fast networks. This is because Nmap doesn't have to bother about completing the TCP three-way handshake or terminating the connection.
> 
> - **Reliable**
> 	- Works against any TCP-compliant stack, and clearly distinguishes between open, closed, and filtered ports.

>[!tip]+ `-Pn`: Skipping ICMP Echo Requests 
> Normally, Nmap sends ICMP Echo Requests (pings) and other probes to check if a host is alive before scanning ports.
>- But if the target host or a firewall in front of it **blocks ICMP Echo Requests** or other discovery probes, Nmap may treat the host as down and **not attempt port scanning**. 
>- To avoid this, you can **disable host discovery step with the `-Pn` option**. In this case, Nmap considers the host as up without sending ping requests, and proceeds straight to port scanning.
> 
> ```bash
> sudo nmap -Pn 192.168.1.11
> ```
> 
> The scan will be more thorough in this case, but likely slower.

>[!tip]+ `-n`: Disabling DNS Resolution
>By default, Nmap tries to resolve IP addresses to hostnames by performing a reverse DNS lookup before scanning. You can disable this with the `-n` option.
>This is useful to speed up the process when you need to scan a large range of IP addresses or when DNS is slow/unreliable. This also helps evade detection caused by **DNS leaks**.
>```bash
>sudo nmap -Pn -n 192.168.1.11
>```
>In short, faster scans, less network noise.

>[!important]+ `--disable-arp-ping`: Disabling ARP ping on local LAN
>When you scan hosts on a local Ethernet network (with root privileges), Nmap usually sends **ARP requests** (Layer 2) to check if the hosts are live. This happens before the actual port scan and even before ICMP Echo Requests.
>This is because ARP is highly reliable on local networks and works even if ICMP is blocked. 
>You can **disable ARP pings with the `--disable-arb-ping`option**:
>```bash
>sudo nmap -Pn -n --disable-arp-ping 192.168.1.11
>```
## `-sT` TCP Connect scan

>The **TCP Connect scan (`-sT`)** tries to establish a **full TCP connection** to the target port.


```bash
nmap 192.168.1.11
```

```bash
nmap -sT 192.168.1.11
```

>[!interesting]+ How TCP Connect scan works
>Nmap calls the OS's **`connect()` system call** to establish a TCP connection with the target. This initiates a TCP three-way handshake, just like in the TCP `SYN` scan. If the port is open, the target will respond with `SYN`/`ACK`, and Nmap will complete the handshake by sending an `ACK` packet. It then terminates the connection immediately with the `RST` packet.
>In case of closed or filtered ports, the behavior is the same as in the TCP `SYN` scan.

| Port status | TCP response flags                                  | Description                                                                                                                                                                                            |
| ----------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `closed`    | `RST` (reset)                                       | If any packet is sent to a **closed** port (including TCP `SYN`), the target server will respond with a `RST` TCP packet.                                                                              |
| `open`      | `SYN`/`ACK`                                         | If the port is **open**, the target responds with `SYN`/`ACK`; Nmap completes the handshake by sending an `ACK` packet back. It then immediately tears the connection down with an`RST` packet.        |
| `filtered`  | No response or<br>ICMP unreachable error (type `3`) | If the packet sent by Nmap is dropped by a firewall, typically no response will be received. <br>Sometimes, however, firewalls may be configured to respond with an ICMP unreachable error (type `3`). |

>[!warning] The TCP Connect scan is one of the **least stealthy** scan types, since fully established TCP connections are logged on most systems, and therefore can be easily detected.

>[!info] TCP Connect scan (`-sT`) doesn't require root privileges.


>[!tip]
>A full TCP Connect port scan takes quite some time. Press the `[Space Bar]` during process to see the scan status:
>```bash
>sudo nmap -sS 10.129.124.161 -sV 
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-09-01 09:30 CDT
Stats: 0:00:01 elapsed; 0 hosts completed (1 up), 1 undergoing SYN Stealth Scan
SYN Stealth Scan Timing: About 53.50% done; ETC: 09:30 (0:00:01 remaining)
Stats: 0:00:03 elapsed; 0 hosts completed (1 up), 1 undergoing SYN Stealth Scan
SYN Stealth Scan Timing: About 44.27% done; ETC: 09:30 (0:00:04 remaining)
>```

>[!tip]
>You can use the `--stats-every=5s` option to define how often the status of the scan will the shown automatically.
>For example, to output scan status every 1 minute:
>```bash
>sudo nmap -sS 192.168.1.11 -sV --stats-every=1m
># or
>sudo nmap -sS 192.168.1.11 -sV --stats-every=60s 
>```

>[!note]+ The TCP scan is highly accurate, but it's slow and noisy. Each connection takes ~1-3 seconds.
>But since Nmap establishes a full TCP connection, it interacts cleanly with services, making it less likely to cause service errors or instability.

>[!tip]+
>You can use `-T4` or `-T5` to speed `-sT` scans a bit. But it will make the scan even more noisy.
>```bash
>nmap -sT -T5 -p- 192.168.1.11
>```
## `-sA` TCP `ACK` scan

>The **TCP `ACK` scan (`-sA`)** sends a TCP `ACK` packet to the target port. 

```bash
nmap -sA 192.168.1.11
```

>[!warning] The TCP `ACK` scan **can't determine whether the port is open or closed**. It can only say if the port is  `filtered` or `unfiltered`.

>[!warning] The TCP `ACK` scan requires root (raw packet) privileges.

>[!interesting]+ How TCP `ACK` scan works
>TCP `ACK` packets are used in already established TCP connections to confirm a packet has been received.
>During the scan, Nmap sends a TCP `ACK` packet to the port **it has no ongoing connection with**. An open port will respond with a **TCP `RST` packet**, same as a closed one would do. That's why this scan can't tell open and closed ports apart.
>But this `RST` also means **the port is reachable** and not filtered by a firewall (except cases when firewall violates the specs and responds with `RST` itself), so Nmap marks the port `unfiltered`. 
>No response means the probes were blocked, and the port is marked `filtered`.

| Port status  | Response                                         |
| ------------ | ------------------------------------------------ |
| `unfiltered` | TCP `RST` packet                                 |
| `filtered`   | No response or ICMP unreachable error (type `3`) |

>[!tip]+ TCP `ACK` scan is mainly used to determine if the firewall in the target network, if it exists, is stateful or stateless, and **map firewall rules**.
> - **Stateful firewalls** keep connection states, so **any TCP `ACK` packets** not part an existing connection **will be dropped**.
> - **Stateless firewalls** generally won't drop `ACK` packets unless explicitly configured.

```bash
sudo nmap -sS -Pn 192.168.1.11 # find open ports
sudo nmap -sA -Pn 192.168.1.11 # map firewall rules
```

>[!tip]
>If you run `-sA` and get `unfiltered` on port 80 → firewall allows `ACK` → **likely stateless** → you might bypass it with `-sF` or `-sX`.
## `-sU` UDP scan

>The **UDP scan (`-sU`)** sends a UDP packet to the target UDP port.

```bash
nmap -sU 192.168.1.11
```

>[!warning] The UDP scan requires root (raw packet) privileges.

>[!interesting]+ How UDP scans work
>For common UDP services, Nmap sends relevant packets (for example, a valid DNS query to UDP port `53`) to increase detection accuracy. For others, Nmap just sends empty packets.
>- If the port is **open**, the target *may* send a valid UDP response back or no response at all. 
>- If the port is **closed**, the host will likely respond with an ICMP unreachable error (type `3`).
>- If the port is **filtered**, the firewall will likely ignore the packet and return no response. 
>
>This means that if no response is received, Nmap can't tell precisely if the port is open or filtered. So the port is marked `open|filtered`.

| Port Status      | Response                          |
| ---------------- | --------------------------------- |
| `open`           | Valid UDP response                |
| `closed`         | ICMP unreachable error (type `3`) |
| `open\|filtered` | No response                       |

>[!warning] UDP scans are generally **much slower** than any other scans.

>[!interesting]+ Why UDP scans are slow
>**UDP is connectionless**.
>Therefore, to make any conclusion about the port state, Nmap has to **wait until the timeout**: there's no `RST` flag like in TCP that can be used to explicitly reject the connection, nor there're any acknowledgment flags.
>This is also why UDP ports are much harder to scan.

- Because UDP scans are so slow (around 20 minutes for the first 1000 ports), it's a good idea to run it against a small number of top ports:

```bash
nmap -sU --top-ports 20 192.168.1.11
```

Common services running over UDP:

| Port           | Service |
| -------------- | ------- |
| `53`           | DNS     |
| `69`           | TFTP    |
| `123`          | NTP     |
| `137`          | NetBios |
| `161`          | SNMP    |
| `389`          | LDAP    |
| `1812`, `1813` | RADIUS  |
| `1900`         | UPnP    |
## Inverse TCP scans: `-sN`, `-sF`, `-sX`

>**Inverse TCP scans** involve sending packets with **unusual flag combinations or no flags set**, and analyzing responses to infer the state of the ports.

There are three main types of inverse TCP scans:
 - `NULL` scan (`-sN`)
 - `FIN` scan (`-sF`)
 - Xmas scan (`-sX`)

>[!important] The primary goal of inverse scan types is **firewall evasion**.
>`NULL`, `FIN`, and Xmas scans are designed to be even more stealth than TCP `SYN` scans.

>[!warning] All inverse scans, `NULL`, `FIN`, and Xmas, require root (raw packet) privileges.

According to [`RFC 793`](https://www.rfc-editor.org/rfc/rfc793.txt), when a TCP packets with flags that don't fit a normal connection attempt is sent:
- If the port is **open**: the target must **ignore the unexpected packet and send no response**.
- If the port is **closed**: the target **must reply with a `RST` (reset) packet**.

For all three types of scans, `NULL` scan, `FIN` scan, and Xmas scan, Nmap infers the port state in the following way:

| Port status      | Probe response                    | Description                                                                                                                                                                                                                                                                                         |
| ---------------- | --------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `open\|filtered` | No response                       | The specification says an **open port must not respond** to a packet with unusual flag combination or no flags set.<br>Firewalls and packet filters usually ignore a filtered packet as well.<br>Since Nmap can't say for sure whether the port was open or filtered, it marks it `open\|filtered`. |
| `closed`         | TCP `RST` packet                  | A closed port must respond with an TCP `RST` packet.                                                                                                                                                                                                                                                |
| `filtered`       | ICMP unreachable error (type `3`) | Many firewalls might issue ICMP unreachable error (type `3`) messages to inform the sender that the packet has been filtered.                                                                                                                                                                       |

>[!important] `NULL`, `FIN` and Xmas scans will only ever mark ports as `open|filtered`, `closed`, or `filtered`. 
>Since most filters will drop banned packets without sending any ICMP response, inverse scans can't differentiate between open and filtered ports either.

- Many **IDS/IPS and firewalls inspect traffic looking for classic TCP handshake sequences** (`SYN` scans) or known connection attempts. Inverse scans neither initiate nor pretend to complete TCP handshakes, thus they're less likely to be logged. 
- Inverse scans produce unusual packet patterns that typically **fall outside standard IDS signatures**.
- However, **traffic anomalies themselves can trigger security alerts**.

>[!warning] On inverse scan reliability
>The `RST` paradox, discussed earlier, can make inverse scans **unreliable**: a number of systems with response with **`RST` packets** even on open ports or filtered ports; the port will be marked `closed` when it's actually `open|filetered`. This violates the `RFC 793` specification.
>
>|OS|Behavior|Impact|
>|---|---|---|
>|Windows XP–11|Sends `RST` for **any** unsolicited packet|All scans show `closed` → **false negatives**|
>|Cisco IOS|Sends `RST` for `FIN`/`NULL`/Xmas scans|Same issue|
>|Linux, BSD, macOS|Compliant → No response on open ports|Scan works|

### `-sN` TCP `NULL` scan

>The **`NULL` scan (`-sN`)** sends an empty TCP packet with no flags set (all TCP flags are zero) to the target port.

```bash
sudo nmap -sN 192.168.1.11
```
### `-sF` TCP `FIN` scan

>The **TCP `FIN` scan (`-sF`)** sends a TCP `FIN` packet to the target host.

```bash
sudo nmap -sF 192.168.1.11
```

>[!example]+ Real-world use cases: bypassing Cisco ASA
>- ASA drops `SYN` packets from external IPs.
>- But allows `FIN` packets → scan with `-sF`.
>```bash
>sudo nmap -sF -Pn -n 192.168.1.11
>```

>[!interesting]+ The `FIN` flag
>TCP `FIN` packets are normally a part of four-way TCP connection termination handshake. They're used to signal that one side wishes to finish sending data and gracefully close the connection.

### `-sX` TCP Xmas scan

>The **TCP Xmas scan (`-sX`)** sends a malformed TCP packet with the `PSH`, `URG`, and `FIN` flags set.

```bash
sudo nmap -sX 192.168.1.11
```

>[!interesting]+ Christmas tree
>The name comes from the packet resembling a blinking Christmas tree with alternate flags set in a packet capturing tool like Wireshark.

## `-sY` SCTP `INIT` scan

>The **SCTP `INIT` scan (`-sY`)** sends a [SCTP](https://en.wikipedia.org/wiki/Stream_Control_Transmission_Protocol) packet with a minimal `INIT` chunk to the target port

```bash
sudo nmap -sY 192.168.1.11
```

>[!warning] The SCTP `INIT` scan requires root (raw packet) privileges.

The SCTP `INIT` scan is an equivalent of a TCP `SYN` scan but for SCTP.

| Port status      | Probe response                                   |
| ---------------- | ------------------------------------------------ |
| `open\|filtered` | `INIT` + `ACK` chunk                             |
| `closed`         | `ABORT` chunk                                    |
| `filtered`       | No response or ICMP unreachable error (type `3`) |

>[!interesting]+ What is SCTP?
>SCTP is mostly used **mobile networks**, including **3G, 4G, 5G** (MME, SGSN, HSS).
>The **SCTP protocol** is designed for transporting signaling messages in telecom networks over IP, specifically within the [SIGTRAN](https://en.wikipedia.org/wiki/SIGTRAN) (Signaling Transport) framework to emulate the reliability of traditional Signaling System [SS7](https://en.wikipedia.org/wiki/Signalling_System_No._7) (Signaling System No. 7).
>
>But SCTP can be used for other applications as well, such as [DIAMETER](https://en.wikipedia.org/wiki/Diameter_(protocol)), [WebRTC](https://en.wikipedia.org/wiki/WebRTC) and [NetFlow](https://en.wikipedia.org/wiki/NetFlow)

- Scan common SCTP ports:

```bash
sudo nmap -sY -p 2905,2906,3868 192.168.1.11
```


## `-sW` TCP Window scan

>The **TCP window scan (`-sW`)** is almost the same as the TCP `ACK` scan, but it also examines the [Window](https://en.wikipedia.org/wiki/Transmission_Control_Protocol#Window_scaling) field of the TCP `RST` packets returned in response to infer the state of target ports.

```bash
sudo nmap -sW 192.168.1.11
```

>[!warning] The TCP Window scan requires root (raw packet) privileges.

>[!interesting]+ How TCP Window scan works
>Nmap sends a TCP `ACK` packet to the target port (like in `-sA`), but then looks at the **TCP Window size** in the `RST` response:
>- **Non-zero window** → the port is **open**.
>- **Zero window** → the port is **closed**.

>[!important]+ The TCP Window scan only works on **specific systems**:
>- Solaris (pre-10)
>- Some old Linux kernels
>- Cisco routers (rarely)
>
>**95% of modern systems return zero window** → all ports appear `closed`.

| Port status | Probe response                                    |
| ----------- | ------------------------------------------------- |
| `open`      | TCP `RST` response with **non-zero** window field |
| `closed`    | TCP `RST` response with **zero** window field     |
| `filtered`  | No response or ICMP unreachable error (type `3`)  |

## `-sM` TCP Maimon scan

>The **TCP Maimon scan (`-sM`)** sends an TCP packet with `FIN` and `ACK` flags to the target port.

```bash
sudo nmap -sM 192.168.1.11
```

>[!warning] The TCP Maimon scan requires root (raw packet) privileges.

The responses are the same as with `NULL`, `FIN`, and Xmas scans:

| Port status      | Probe response                    |
| ---------------- | --------------------------------- |
| `open\|filtered` | No response                       |
| `closed`         | TCP `RST` packet                  |
| `filtered`       | ICMP unreachable error (type `3`) |

>[!note]
>The Maimon scan is named after its discoverer, Uriel Maimon.

This scan is rarely used today, and mostly for educational purposes. It's often identical to `-sF` or `-sX` in results — use them instead.

## `--scanflags` Custom TCP scan

>**Custom TCP scans (`--scanflags`)** allow you to experiment with various combinations of TCP flags on your own, beyond the built-in TCP scans.

- `SYN` + `URG`:

```bash
sudo nmap --scanflags SYNURG 192.128.1.11
```

- `RST` + `SYN`:

```bash
sudo nmap --scanflags RSTSYN 192.128.1.11
```

- `FIN` + `PSH` + `URG` (same as `-sX` but manually):

```bash
sudo nmap --scanflags FINPSHURG 192.128.1.11
```

>[!warning] Custom TCP scans requires root (raw packet) privileges.

Custom scans may really come useful for advanced [DPI](https://en.wikipedia.org/wiki/Deep_packet_inspection) (Deep Packet Inspection) bypass and detection evasion.
## `-sI` TCP Idle scan

>The **TCP Idle scan (`-sI`)**, or **zombie scan**, is a blind port scanning technique that allows you to infer the status of the target port **without sending any packets directly from your real IP address**.

```bash
nmap -Pn -sI ZOMBIE TARGET
```

```bash
nmap -Pn -sI 192.168.1.10 192.168.1.11
```

Rather than sending probes directly to the target, Nmap proxies them through an intermediary **zombie host**.

>[!important] A **zombie** is host used by the attacker as a proxy to perform scan probes on the target.
>Requirements for an effective zombie:
>- It must respond to ICMP Echo Requests (ping probes).
>- It should have a **predictable, incremental IP ID sequence in its IP headers for outgoing packets**.
>- It doesn't generate its own network traffic, e.g., it's **idle**.
>- It must be accessible by both the attacker and the target.
>
>Ideal zombie hosts are lightly loaded web servers or routers with simple TCP/IP stacks.
>Best zombie candidates:
>
>| System                            | Why                                      |
> | --------------------------------- | ---------------------------------------- |
> | **Old routers** (e.g., Linksys WRT54G)  | Simple TCP/IP stack, low traffic         |
> | **Printers** (e.g., HP LaserJet)        | Idle, predictable                        |
> | **Industrial devices** (e..g, PLC, HMI) | Often run embedded Linux with weak IP ID |
> | **Web servers with low traffic**  | If it’s not under load → good            |

> [!interesting]+ How TCP Idle scan works:
> 
> 1. An attacker sends a packet to the zombie to obtain its current [IP ID value (Identification)](https://en.wikipedia.org/wiki/IPv4#Identification) (usually via a `SYN`/`ACK` or other packet).
> 2. The zombie responds to the unsolicited `SYN`/`ACK` with `RST`; the IPv4 packet contains its IP ID.
> 3. The attacker sends a TCP `SYN` packet to the scanned port on the target system but **spoofs the source IP address as the IP address of the zombie host**. The target thinks it's the zombie who's trying to connect.
>
> If the target port is **open**:
>
> 4. The target host sends a TCP `SYN`/`ACK` packet (TCP three-way handshake) to the zombie.
> 5. For the zombie, this `SYN`/`ACK` is not expected, so it sends an `RST` packet back to the target. The zombie's **IP ID value is incremented by `1`**.
> 6. The attacker sends a `SYN`/`ACK` TCP packet to the zombie again to probe for its IPv4 ID.
> 7. The zombie responds with `RST`; its IP ID is incremented by `1` once again.
>> As a result, the zombie's IP ID value is **incremented by `2`** in total.
>
> If the target port is **closed**:
>
> 4. The target host sends a TCP `RST` packet to the zombie
> 5. The zombie ignores the unsolicited `RST`; it's **IP ID value is left unchanged**.
> 6. The attacker sends a `SYN`/`ACK` TCP packet to the zombie again to probe for its IPv4 ID.
> 7. The zombie responds with `RST`; its IP ID is incremented by `1`.
>> As a result, the zombie's IP ID value is **incremented by `1`** in total.
> 
> No increment (or unexpected behavior) means the zombie is unsuitable or network filtering interferes.
> 
> | Port status                                | Zombie's IP ID     |
> | ------------------------------------------ | ------------------ |
> | `open`                                     | incremented by `2` |
> | `closed`                                   | incremented by `1` |
> | `filtered`<br>or the zombie isn't suitable | not incremented    |

>[!note] The zombie scan is **invisible**, but really **slow**.

>[!interesting] IP ID
>**IP ID (Identification)** 16-bit field in the IPv4 header used for **fragmentation/reassembly** of IP packets.
>- Many systems increment the IP ID sequentially for every **outgoing** packet. 
>- The **idle scan exploits this predictable IP ID increment** to detect if the zombie sent additional packets in response to interactions with the target.

>[!important] TCP Idle scan is perhaps the most stealth scan out of all scan type s Nmap supports.

## References and further reading

- [`A Quick Port Scanning Tutorial — Nmap`](https://nmap.org/book/port-scanning-tutorial.html)
- [`Port Scanning Techniques — Nmap`](https://nmap.org/book/man-port-scanning-techniques.html)

