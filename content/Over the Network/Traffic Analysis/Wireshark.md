---
created: 2026-03-09
tags:
  - tools
  - nta
---
## Wireshark

>**[Wireshark](https://www.wireshark.org/)** is a free and open-source network protocol analyzer used for capturing, inspecting, and troubleshooting network traffic.


>[!note]+ Installation
>```bash
>sudo apt install wireshark
>```
## Wireshark filters

- Comparison operators:

|       **Capture Filters**       | **Result**                                                                |
| :-----------------------------: | ------------------------------------------------------------------------- |
|         `host x.x.x.x`          | Capture traffic to or from the specified host.                            |
|        `net x.x.x.x/24`         | Capture traffic to or from the specified network.                         |
|      `src net x.x.x.x/24`       | Capture traffic originating from the specified network.                   |
|      `dst net x.x.x.x/24`       | Capture traffic destined to the specified network.                        |
|            `port #`             | Capture traffic to or from the specified port.                            |
|         `portrange #-#`         | Capture traffic to or from the specified port range.                      |
|       `ip / ether / tcp`        | Filter                                                                    |
| broadcast / multicast / unicast | Grabs a specific type of traffic. one to one, one to many, or one to all. |

- Filter protocols:

|Option|Description|
|---|---|
|`ip`|Show packets containing IPv4 protocol.|
|`ipv6`|Show packets containing IPv6 protocol.|
|`tcp`|Show all TCP packets.|
|`udp`|Show all UDP packets.|
|`icmp`|Show ICMP traffic.|
|`arp`|Show ARP traffic.|
|`dns`|Show DNS queries and responses.|
|`http`|Show HTTP traffic.|
|`tls`|Show TLS/SSL encrypted traffic.|
|`ssh`|Show SSH traffic.|
|`ftp`|Show FTP traffic.|
|`smtp`|Show SMTP traffic.|
|`ntp`|Show NTP traffic.|

- IP address filtering:

| Option                                  | Description                                                        |
| --------------------------------------- | ------------------------------------------------------------------ |
| `ip.addr == x.x.x.x`                    | Match traffic with the specified source or destination IP address. |
| `ip.src == x.x.x.x`                     | Match traffic with the specified source IP address.                |
| `ip.dst == x.x.x.x`                     | Match traffic with the specified destination IP address.           |
| `ip.addr == x.x.x.x/24`                 | Match traffic to or from the specified network.                    |
| `!(ip.addr == x.x.x.x)`                 | Exclude traffic to or from the specified IP address.               |
| `ip.addr == x.x.x.1 \|\| ip == x.x.x.2` | Match traffic between the specified hosts.                         |

- MAC address filtering:

| Option                          | Description                                                         |
| ------------------------------- | ------------------------------------------------------------------- |
| `eth.addr == xx:xx:xx:xx:xx:xx` | Match traffic with the specified source or destination MAC address. |
| `eth.src == xx:xx:xx:xx:xx:xx`  | Match traffic with the specified source MAC address.                |
| `eth.dst == xx:xx:xx:xx:xx:xx`  | Match traffic with the specified destination MAC address.           |
- Port filtering:


| Option              | Description                                                                                           |
| ------------------- | ----------------------------------------------------------------------------------------------------- |
| `tcp.port == xx`    | Match traffic with the specified source or destination TCP port number.                               |
| `tcp.srcport == xx` | Match traffic with the specified source TCP port number.                                              |
| `tcp.dstport == xx` | Match traffic with the specified destination TCP port number.                                         |
| `udp.port >= xx`    | Match traffic with the source or destination UDP port number greater or equal to the specified value. |
| `tcp.port != 80`    | Exclude traffic to or from the specified port number.                                                 |

- Packet size:

| Option              | Description                     |
| ------------------- | ------------------------------- |
| `frame.len > 1000`  | Packets larger than 1000 bytes. |
| `frame.len < 128`   | Packets smaller than 128 bytes. |
| `frame.len >= 1500` | Large packets near MTU size.    |
| `tcp.len > 0`       | Packets containing TCP payload. |
## Decrypting traffic


>If you have a cryptographic key used to encrypt traffic between two hosts, you can use Wireshark to decrypt it.