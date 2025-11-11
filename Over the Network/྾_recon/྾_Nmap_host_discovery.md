---
created: 2025-08-31
tags:
  - nmap
aliases: []
---
## Host discovery

>**Host discovery** is the process of identifying active devices on a network. 

Host discovery is the first step of an internal penetration test; it gives an overview of the entire network. I

>[!note]+ Ping scan
>Nmap's host discovery is often called **ping scan**, though Nmap capabilities go far beyond simple ICMP Echo. Nmap supports various probe types tailored for different network configuration and security levels.

- Nmap host discovery:

```bash
nmap -sn TARGET 
```

>[!important] The `-sn` option **disables port scanning**.

There are several host discovery scan types Nmap supports:

- **`-sn` Ping scan**
- **`-PS` TCP `SYN` scan**
- **`-PA` TCP `ACK`scan**
- **`-PU` UDP scan**
- **`-PY` SCTP `INIT` scan**
- **`-PR` ARP scan**
- **`-PE`, `-PP`, `-PM` ICMP-only scan**
- **`-PO` IP protocol scan**
- **`-sL` List scan**
- **`-Pn` No ping scan**

| Option              | Description                                     |
| ------------------- | ----------------------------------------------- |
| `-sn`               | Ping scan (default)                             |
| `-PS`               | TCP `SYN` ping scan                             |
| `-PA`               | TCP `ACK` ping scan                             |
| `-PU`               | UDP ping scan                                   |
| `-PY`               | SCTP `INIT` ping scan                           |
| `-PR`               | ARP scan (local LAN)                            |
| `-PE`, `-PP`, `-PM` | ICMP-only scan (Echo, Timestamp, Mask requests) |
| `-PO`               | IP protocol ping scan                           |
| `-sL`               | List scan (no packets)                          |
| `-Pn`               | No ping scan (host discovery disabled)          |

- ARP pings are by far the fastest and most reliable on local Ethernet networks.
- UDP pings are slower and less reliable (no response guarantees).

>[!tip] 
>Store every all scan results. This can later be used for comparison, documentation, and reporting.

>[!tip]
>Combine multiple probe types to maximize host detection in restrictive environments (e.g., `-sn PS80,443 -PU53,123 -PE`).

Once we know a host is alive, we can proceed the investigation to find out:
- Open ports and its services
- Service versions
- Information the services provided
- Operating system
## `-sn` Ping scan

>**Ping scan (`-sn`)**, aka **no port scan** or **ping sweep**, sends ICMP Echo requests to specified hosts, but doesn't perform any port scan.

Ping scans are useful to quickly identify live hosts on a network, especially a large one, without attracting  much attention.

```bash
sudo nmap -sn TARGET
```

Ping scan is the default host discovery scan. Nmap sends a combination of probes to detect whether hosts are alive:

- **ICMP Echo Requests**
	- Classic ping packets (ICMP type `8`); many systems respond with Echo Replies (ICMP type `0`) unless ICMP is filtered or disabled; same as `-PE`.

- **TCP `SYN` Ping to port `443`**
	- TCP packets with `SYN` flag set to port `443` (HTTPS); same as `-PS`.
	- Any response from the server (`SYN`/`ACK` or `RST`) indicates the host is up.

- **TCP `ACK` Ping to port `80`**
	- TCP packets with `ACK` flag set to port `80` (HTTP); same as `-PA`.

- **ARP Requests** (if on a local Ethernet network and run with root privileges)
	- APR requests; same as `-PR`.
	- ARP is extremely fast and reliable for LAN discovery.

>[!tip]+
>The `-sn` option can be combined with any of the discovery probe types (the `-P*` options).

How Nmap treats responses:
- **Any response** from the target to **any probe** (ICMP reply, TCP `SYN`/`ACK` or `RST`, ARP reply) marks the host alive.
- No response or an ICMP unreachable message (type `3`) means the host is down or filtered.

>[!interesting]+ Why multiple probes?
>Firewalls and packet filters may block certain types of probes. Using multiple different probes improves coverage and reduces the number of false negative results.

>[!important] If a host response to one probe, Nmap doesn't send others.

- To scan a network range:

```bash
sudo nmap -sn 192.168.1.0/24
```

- To scan a list of IP addresses:

```bash
sudo nmap -sn -iL hosts.lst
```

>[!note]+
>`-iL` accepts a file with a list of hosts to scan.
> ```bash
> cat hosts.lst
> 
> 192.168.1.4
> 192.168.1.10
> 192.168.1.11
> 192.168.1.18
> 192.168.1.19
> 192.168.1.20
> 192.168.1.28
> ```

- To scan a range of IP addresses:

```bash
sudo nmap -sn 192.168.1.0-20
```

- To scan a single IP address:

```bash
sudo nmap -sn 192.168.1.11
```


>[!important]+ ARP scans
>If run by a **privileged user** and on a **local Ethernet network**, Nmap automatically sends **ARP requests** (ARP pings), *even before any ICMP Echo Requests are sent*. ARP is considered more reliable for local host detection.
> - To ensure Nmap sends **ICMP Echo Requests regardless of ARP ping**, add the `-PE` option:
> 
> ```bash
> sudo nmap -sn -PE 192.168.1.0/24
> ```
> - To disable ARP ping entirely, specify the `--disable-arp-ping` or `--send-id` option:
>```bash
>nmap -sn --disable-arp-ping 192.168.1.0/24
>```
>```bash
>nmap -sn --send-ip 192.168.1.0/24
>```

>[!warning] Nmap doesn't send TCP `ACK` probes or ARP requests when executed by an unprivileged user.

>[!note]+ To understand why Nmap has marked the target alive, use add `--reason` option:
>```bash
>sudo nmap -sn --reason 192.168.1.0/24
>```

>[!note]+ To show all packets Nmap sends and receives, add the `--packet-trace` option:
>```bash
>sudo nmap -sn -PE --packet-trace --disable-arp-ping -oA host 192.168.1.11 
>```
> ```bash
> Starting Nmap 7.80 ( https://nmap.org ) at 2020-06-15 00:12 CEST
> SENT (0.0107s) ICMP [10.10.14.2 > 10.129.2.18 Echo request (type=8/code=0) id=13607 seq=0] IP [ttl=255 id=23541 iplen=28 ]
> RCVD (0.0152s) ICMP [10.129.2.18 > 10.10.14.2 Echo reply (type=0/code=0) id=13607 seq=0] IP [ttl=128 id=40622 iplen=28 ]
> Nmap scan report for 10.129.2.18
> Host is up (0.086s latency).
> MAC Address: DE:AD:00:00:BE:EF
> Nmap done: 1 IP address (1 host up) scanned in 0.11 seconds
> ```
### Determining OS family based on TTL

There's a way to infer the operating system of the target host even without running Nmap OS detection scripts (`-O` option; see [[྾_Nmap_service_and_OS_enumeration_and_detection]]), **just based TTL values in response IP packets**.

>**[TTL](https://en.wikipedia.org/wiki/Time_to_live) (Time-To-Live)**, or **hop limit**, is an 8-bit field in IPv4 header designed to limit a packet's lifetime to prevent infinite routing loops. 

- Each hop the router traverses decrements TTL by `1`. 
- If the TTL reaches zero before the packet arrives at its destination, the packet is discarded, and the router sends an ICMP `Time Exceeded` message (Type `11`, Code `0`) back to the sender.

The initial TTL value is set by the OS and varies across different OS families:

| OS/Device Type                   | Common Initial TTL Value |
| -------------------------------- | ------------------------ |
| Linux and most Unix-like systems | `64`                     |
| Windows                          | `128`                    |
| Cisco routers and some others    | `255`                    |

- The maximum TTL value is `255` (since the field is 8-bit).
- The recommended default initial TTL value is `64`. 

>[!interesting] 
>Without TTL, packets may start traversing the network indefinitely, such as due to routing errors, consuming network bandwidth and power. This could lead to a situation similar to *broadcast storms* on Layer 2 (Ethernet frames don't have a TTL value; STP — Spanning Tree Protocol — is used to deal with it).

By analyzing the TTL value in a received packet and accounting for hop count (estimated or known), you can **infer the likely OS family of the sender host**.

>[!example]+
>Returning to the previous example, let's consider the output of the host discovery scan:
>```bash
>sudo nmap -sn -PE --packet-trace --disable-arp-ping -oA host 192.168.1.11 
>```
> ```bash
> Starting Nmap 7.80 ( https://nmap.org ) at 2020-06-15 00:12 CEST
> SENT (0.0107s) ICMP [192.168.1.2 > 192.168.1.11 Echo request (type=8/code=0) id=13607 seq=0] IP [ttl=255 id=23541 iplen=28 ]
> RCVD (0.0152s) ICMP [192.168.1.11 > 192.168.1.2 Echo reply (type=0/code=0) id=13607 seq=0] IP [ttl=128 id=40622 iplen=28 ]
> ...
> ```
> The TTL of the received packet (`RCVD`) is `128`. The sender is probably Windows (zero hops away; on the same network).

## `-PS` TCP `SYN` scan

>The **TCP `SYN` scan (`-PS`)** sends a TCP `SYN` packet (empty TCP packet with the `SYN` flag set) to the given ports (port `80` by default) on the target host.

This scan is useful for detection evasion: when ICMP Echo Requests are blocked by firewalls, TCP `SYN` packets may go unnoticed.

```bash
sudo nmap -sn -PS TARGET
```

>[!interesting]+
>TCP `SYN` ping host discovery is similar to TCP `SYN` port scanning, except Nmap doesn't care whether the port is open or not. 
> Nmap sends a TCP `SYN` packet to the chosen port (the first step in a TCP handshake) and waits for the response.
> - **Any response** from the target (whether it's `SYM`/`ACK` when the port is open or `RST` when closed) marks the host alive.
> - Only if the target host doesn't response or an ICMP unreachable message (type `3`) received, the host is considered down or filtered.

- Perform a TCP `SYN` scan:

```bash
sudo nmap -sn -PS 192.168.1.11
```

- You can customize which ports to probe by specifying them after the `-PS` flag, e.g.:

```bash
sudo nmap -sn -PS22,80,443 192.168.1.0/24 # probes the ports 22, 80, and 443
```

```bash
sudo nmap -sn -PS20-25,80 192.168.1.0/24 # probes the ports 20, 21, 22, 23, 24, and 80
```

- To scan multiple hosts by sending TCP `SYN` packets to the specified ports on each host:

```bash
sudo nmap -sn -PS80,443,22 192.168.1.0/24
```

>[!warning] The TCP `SYN` scan requires root (raw packet) privileges.
## `-PA` TCP `ACK` scan

>The **TCP `ACK` scan (`-PA`)** sends a TCP `ACK` packet to the given ports (port `80` by default) on the target host.

```bash
sudo nmap -sn -PA TARGET
```

TCP `ACK` packets may get through where TCP `SYN` probes or ICMP pings are blocked by firewalls. It can be useful for firewall evasion.

>[!interesting] 
>During the scan, Nmap sends a TCP `ACK` packet, which are normally used in already existing TCP connections to confirm successful packet delivery. In this case, however, there's no TCP connection.
> - When a host receives an `ACK` packet on a port with **no connection state** (no active connection with the sender), it will usually respond with an **`RST` (reset) packet** if the port is **reachable**, regardless of whether it's open or closed.
> - **The receipt of an `RST` generally means the host is alive.** 
> - No response or ICMP unreachable message (type `3`) typically indicates the host is down or filtered.

- To perform a TCP `ACK` scan:

```bash
sudo nmap -sn -PA 192.168.1.0/24
```

- To specify other ports to send probes to:

```bash
sudo nmap -sn -PA20-25,80 192.168.1.0/24
```

## `-PU` UDP scan

>The **UDP scan (`-PU`)** sends a UDP packet to the given ports (port `40125` by default). For most ports, the packet will be empty, but for some, Nmap will send protocol-specific payload. 

The UDP scan may come useful in cases when ICMP and TCP probes are blocked.

```bash
sudo nmap -sn -PU
```

>[!interesting] UDP port `40125` is the default because it's unlikely to be open or generate noise.

>[!interesting]
>- **Any response** from the target (whether it's a UDP packet or ICMP message) marks the host alive.
>- If no response is received, host is either down or UDP probes are filtered.

- To perform a UDP scan:

```bash
sudo nmap -sn -PU 192.168.1.0/24
```

- Specifying more common UDP ports, such as `53` (DNS), `123` (NTP), or `161` (SNMP) might increases chances the system will respond:

```bash
sudo nmap -sn -PU53,123,161 192.168.1.0/24
```

- You can combine a UDP scan with ICMP and TCP `SYN` pings (`-PE`, `-PS`) to increase changes of a successful scan on protected networks:

```bash
sudo nmap -sn -PU53,123,161 -PS -PI 192.168.1.0/24
```

>[!warning] UDP scans require root (raw packet) privileges.

>[!important] UDP scans are slow and less reliable. Many ports will silently discard UDP packets (sometimes even when the port is open). Nmap then tries multiple times and waits for the timeout.

## `-PY` SCTP `INIT` ping scan

>The **SCTP `INIT` scan (`-PY`)** sends a [SCTP](https://en.wikipedia.org/wiki/Stream_Control_Transmission_Protocol) packet with a minimal `INIT` chunk to the given ports (port `80` by default).

SCTP ping is less common but useful in advanced scans. 

```bash
sudo nmap -PY -sn TARGET
```

>[!interesting]+
>If the host replies with `INIT`-`ACK` or `ABORT`, it's marked alive.

- To perform a SCTP scan:

```bash
sudo nmap -PY -sn 192.168.1.0/24
```

## `-PR` ARP scan

>The **ARP scan (`-PR`)** rends ARP requests to discover live hosts on a **local network**, bypassing ARP cache. Nmap also handles retransmission and timeout periods.

```bash
nmap -sn -PR TARGET  
```

For example:

```bash
nmap -sn -RP 192.168.1.0/24
```

>[!warning] ARP scans require root (raw packet) privileges.
## `-PE`, `-PP`, `-PM` ICMP-only scan

>The **ICMP ping scans (`-PE`, `-PP`, `-PM`)** send ICMP requests.

- `-PE`: ICMP Echo request (type `8`; standard ping).
- `-PP`: ICMP Timestamp request (type `13`).
- `-PM`: ICMP Address mask request (type `17`; deprecated).

These scans are less commonly used because of firewalls, but can serve as fallback.

```bash
nmap -sn -PE TARGET
```

```bash
nmap -sn -PP TARGET
```

```bash
nmap -sn -PM TARGET
```

## `-PO` IP protocol scan

>The **IP protocol scan (`-PO`)** sends raw IP packets with specified protocol numbers in the header (e.g., ICMP, IGMP, TCP, UDP, etc.).


The IP protocol scan is useful for discovering hosts based on the protocols they support. It may come handy in environments where traditional TCP/UDP pings are filtered but other protocols are allowed.


```bash
nmap -PO TARGET
```

 If no protocols are specified, the default is to send multiple IP packets for:
 - ICMP (protocol `1`)
 - IGMP (protocol `2`)
 - IP-in-IP (protocol `4`)

Protocol numbers:

| Protocol number | Protocol                                                                   |
| --------------- | -------------------------------------------------------------------------- |
| `1`             | [ICMP](https://en.wikipedia.org/wiki/Internet_Control_Message_Protocol)    |
| `2`             | [IGMP](https://en.wikipedia.org/wiki/Internet_Group_Management_Protocol)   |
| `4`             | [IP-in-IP](https://en.wikipedia.org/wiki/IP_in_IP)                         |
| `6`             | [TCP](https://en.wikipedia.org/wiki/Transmission_Control_Protocol)         |
| `17`            | [UDP](https://en.wikipedia.org/wiki/User_Datagram_Protocol)                |
| `33`            | [DCCP](https://en.wikipedia.org/wiki/Datagram_Congestion_Control_Protocol) |
| `132`           | [SCTP](https://en.wikipedia.org/wiki/Stream_Control_Transmission_Protocol) |

See [`Protocol Numbers — IANA`](https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml).

>[!note] For the ICMP, IGMP, TCP, UDP, and SCTP, the packets are sent with the proper protocol headers; other protocols are sent with no additional data beyond the IP header (unless `--data`, `--data-string`, or `--data-length` options are specified).

>[!interesting]+
>- Any response from the target using the same protocol as a probe marks the host alive.
>- ICMP unreachable error (type `3`), this means the host is down or filtered.


- To send IP packets with ICMP, IGMP, and IP-in-IP protocols specified:

```bash
nmap -PO1,2,4 192.168.1f.0/24
```

## `-sL` List scan

>**List scan (`-sL`)**  lists IP addresses on a network **without sending any probes** except DNS reverse lookups.

List scans are useful to perform a light, non-intrusive enumeration.

```bash
nmap -sL TARGET
```

- For example:

```bash
nmap -sL 192.168.1.0/24
```

## `-Pn` No ping scan

>The **no ping scan (`-Pn`)** skips the host discovery stage altogether. Nmap treats all specified hosts alive and scans them regardless. 

```bash
nmap -Pn OPTIONS TARGET
```

Normally, Nmap performs host scanning before port scanning or version detection. Then, Nmap continues scanning only those hosts that were found alive. The `-Pn` option disables this initial host detection stage and forces Nmap to complete other scans.

>[!note]+
>No ping scan is often used in conjunction with other scanning techniques, such as port scanning, service detection, and OS detection. This flag forces Nmap to attempt scan every specified host.
>See [[྾_Nmap_port_scanning]] and [[྾_Nmap_service_and_OS_enumeration_and_detection]].


>[!important]+ APR scans are still performed when run by a privileged user against a local Ethernet network. You can disable ARP scans with `--disable-arp-ping` or `--send-ip` option.

- For example, to perform TCP Connect port scan against all specified hosts without verifying whether they're up:

```bash
nmap -Pn -sT 192.168.1.0/24
```

## References and further reading

- [`Host Discovery Techniques — Nmap`](https://nmap.org/book/host-discovery-techniques.html)
- [`Host Discovery — Nmap`](https://nmap.org/book/man-host-discovery.html)
- [`Protocol Numbers — IANA`](https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml)
- [`Internet Control Message Protocol`](https://en.wikipedia.org/wiki/Internet_Control_Message_Protocol)
- [`Time to Live — Wikipedia`](https://en.wikipedia.org/wiki/Time_to_live)