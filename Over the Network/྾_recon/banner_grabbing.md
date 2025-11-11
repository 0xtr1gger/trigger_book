---
created: 2025-09-01
---


## Banner grabbing

>**Banner grabbing** is a technique used to collect information network services running on open ports on a target host. This involves capturing *software banners* — usually textual information sent by services upon connection.

- Banner grabbing helps identify the **software** and **versions** of running services, which is useful to find weaknesses or audit security posture of the system.

Banner grabbing can be **active** — when you connect to open ports to solicit banners directly — or **passive**, which involves capturing banners indirectly by sniffing network traffic.
## Active banner grabbing

>**Active banner grabbing** involves directly connecting to the open ports on the target system to solicit banner information.

It's typically more accurate that passive banner grabbing but can be quite noisy.

>[!warning] Active banner grabbing is considered intrusive and can easily be detected by most IDS/IPS.

Common tools used for active banner grabbing include:
- **Nmap**
- **Netcat** (`nc`)
- **Telnet**
- **cURL**

### Nmap 

Nmap supports service and version detection probes with the `-sV` flag, as well as numerous NSE scripts for advanced banner grabbing and vulnerability discovery.

```bash
sudo nmap -sV 192.168.1.11
```

For more information, see [[྾_Nmap_service_and_OS_enumeration_and_detection]] and [[྾_Nmap_NSE_scripts]].

>[!interesting] Why can't we rely solely on Nmap for banner grabbing?
> 
> Nmap has several limitations in terms of banner grabbing and service detection:
> 
> - Once the TCP three-way handshake completes, many services send an identification banner *automatically*. The banner is sent with the **`PSH` (push) flag** in the TCP header. However, not all services send banners **immediately upon connection**: some wait for client activity or require specific protocol commands before replying.
> - Nmap may simply **not wait long enough** or **not send the right commands** to elicit banners. Nmap's version detection tries to be fast and broad, so the results are often incomplete. Additionally, Nmap truncates banners to fit into a single line by default, which can hide multi-line or detailed banners.
> - One more point: administrators can **remove, alter, or obscure banners** on services to hinder automated banner grabbing and fingerprinting. So, without customized probes, investigations may be less effective.
> 
> Manually opening TCP connections and interacting with the services with tools like `nc` (Netcat) **can reveal much more**.

>[!important] **Nmap provides a good quick overview** of service banners but can miss detailed information, especially if the banner is delayed, conditional, or session-dependent.

## Netcat

```bash
nc -nv 10.129.2.28 25

Connection to 10.129.2.28 port 25 [tcp/*] succeeded!
220 inlane ESMTP Postfix (Ubuntu)
```
## Passive banner grabbing

>**Passive banner grabbing** involves capturing banner information indirectly by sniffing network traffic. 

Since passive banner grabbing doesn't imply directly establishing connections with the target system, it reduces detection risks. However, it requires access to the network to capture traffic (e.g., via port mirroring or compromised hosts).

The traffic from existing connections is gathered by a tool called **network sniffer**. Examples include `tcpdump`, Wireshark.

See [[network_sniffing]]

### `tcpdump`

```bash
sudo tcpdump -i eth0 host 10.10.14.2 and 10.129.2.28

tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on eth0, link-type EN10MB (Ethernet), capture size 262144 bytes
```

- `nc`
- `tcpdump`

## TCP Header, Three-Way handshake, and connection termination reminder

TCP three-way handshake:

1. SYN: the client sends a packet with SYN (Synchronize Sequence Number) flag, which informs the server that the client wants to establish a connection.
2. SYN + ACK: the server responds to the client with the packet with SYN and ACK flags set.
3. ACK: the client acknowledges the server with an ACK packet. 

TCP connection termination or four-way handshake:

1. FIN: the clients sends a packet with FIN (final data) flag, which is called the termination request and indicates that the client wants to terminate the connection with the server. 
2. ACK: the server sends the ACK segment when it receives the FIN termination request. this means that the server is ready to close and terminate the connection.
3. FIN: the server sends the FIN segment that depicts the successful approval for the termination.
4. ACK: the client sends an ACK packet to the server which informs the server to terminate the connection. as soon as the server receives the ACK segment, it terminates the connection. 


5. FIN + ACK:  the client waits for the ACK of the FIN termination request form the server. it is a waiting state for the client. 
