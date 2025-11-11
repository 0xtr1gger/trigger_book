---
created: 2025-08-31
tags:
  - nmap
---
## Firewalls, IDSs, and IPSs

>**Firewalls and Intrusion Detection/Prevention Systems (IDS/IPS)** are defensive tools to monitor, filter, and block suspicious network activities, including port scans.

>[!note] To learn more about firewalls, see [[firewalls_IDS_&_IPS]].

Nmap's evasion capabilities are built on the principle of **altering the scan's fingerprint** to make it indistinguishable from legitimate traffic or to exploit weaknesses in defensive systems.

Core evasion techniques Nmap supports:
- Stealth scan types (`-sS`, `-sA`, `-sF`, `-sN`, `-sX`, `-sI`)
- Timing manipulation (`-T0` to `-T5` + manual options)
- Packet fragmentation (`-f`, `-ff`, `--mtu`)
- IP address spoofing (`-S`)
- Source port spoofing (`-g`, `--source-port`)
- MAC address spoofing (`--spood-mac`)
- Payload customization (`--data-length`, `--data-string`)
- Proxy servers (`--proxy`)
- DNS proxying

The goal is to **blur the scan’s fingerprint enough to slip past simple defenses**, while still retrieving useful information.

>[!warning] No technique is 100% reliable; success depends on firewall/IDS configuration and security posture.

Nmap determines the port state based on the target response. 
There are two primary reasons why a port may be marked `filtered`:

- **Dropped packets**
	- The firewall **silently discards** the probe packet; no response.
	- Nmap retries several times to find out if the previous packet was accidentally mishandled or not. The default retry limit is `10` ; you can change it with the `--max-retries` option. 
	- Only once the retry limit is reached, Nmap makes a decision about the port state.

- **Filtered packets**
	- A firewall sends a response, such as a TCP `RST` (reset) packet or an ICMP destination unreachable error (type `3`), to explicitly indicate the probe is rejected. 
	- It's a good idea to take a closer look at this port later.

>[!note] It typically takes longer to detect dropped packets than filtered due to retries.

>[!warning] The `PST` packet paradox
>In many TCP scans, the target responds with an `RST` packet if the port is **closed**.
>However, many firewalls and systems **send `RST` for any unsolicited packet** — even to open ports. Such behavior is especially known to pertain Microsoft Windows and Cisco devices.
>As a result, the port is marked `closed` when it should be `open|filtered`. This violates the specification and puts the scan reliability under questioning. 

| Option                | Description                                                  |
| --------------------- | ------------------------------------------------------------ |
| `-sS`                 | TCP `SYN` scan.                                              |
| `-sA`                 | TCP `ACK` scan.                                              |
| `-sF`                 | TCP `FIN` scan.                                              |
| `-sN`                 | TCP `NULL` scan.                                             |
| `-sX`                 | TCP Xmas scan.                                               |
| `-sI`                 | TCP zombie scan.                                             |
| `-T0` to `-T5`        | Timing profiles.                                             |
| `--max-retries`       | Maximum retry limit per port.                                |
| `--host-timeout`      | Maximum scan time per host.                                  |
| `--scan-delay`        | Delay between probes.                                        |
| `--max-rate`          | Maximum number of packets per second.                        |
| `--min-rate`          | Minimum number of packets per second.                        |
| `--max-parallelism`   | Maximum number of probes sent in parallel.                   |
| `--min-parallelism`   | Minimum number of probes sent in parallel.                   |
| `--max-rtt-timeout`   | Maximum round trip timeout.                                  |
| `--min-rtt-timeout`   | Minimum round trip timeout.                                  |
| `-f`                  | Split packets into `8`-byte fragments (after the IP header). |
| `-ff` or `-f -f`      | Split packets into `16`-byte fragments.                      |
| `--mtu`               | Set a custom fragment size; must be a multiple of `8`.       |
| `-S`                  | Spoof source IP address.                                     |
| `-g`, `--source-port` | Set a custom source port number.                             |
| `--spoof-mac`         | Spoof source MAC address.                                    |
| `-D`                  | Decoy scan.                                                  |

### ICMP destination unreachable errors

When a firewall or host blocks a packet, it often sends back an ICMP destination unreachable message (Type `3`). The message code is helpful for interpreting the scan results and identifying firewall rules:

| Code | Message                                     | Description                                                                                                                                                          |
| ---- | ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `0`  | `Destination network unreachable`           | The destination network is unreachable; indicates a network-level block. <br>May suggest a routing or ACL issue.                                                     |
| `1`  | `Destination host unreachable`              | The specific destination host is unreachable. <br>May indicate a host-level block or that the host is down.                                                          |
| `2`  | `Destination protocol unreachable`          | The protocol (e.g., UDP, TCP) specified in the packet is not supported or filtered.                                                                                  |
| `3`  | `Destination port unreachable`              | The specified port on the destination host is closed or filtered.                                                                                                    |
| `4`  | `Fragmentation required, and DF flag set`   | The packet is too large for the next hop and the `DF` (Don't Fragment) flag is set. <br>Suggests a potential MTU issue; can be exploited with fragmentation evasion. |
| `5`  | `Source route failed`                       | A source route specified in the packet can't be completed. <br>Rare; may indicate a misconfigured network or security policy that blocks source routing.             |
| `6`  | `Destination network unknown`               | The destination network is unknown to the router; similar to code `0`.                                                                                               |
| `7`  | `Destination host unknown`                  | The specified destination host is unknown to the router; similar to code `1`.                                                                                        |
| `8`  | `Source host isolated`                      | The source host is administratively isolated from the network. Rare; may indicate a severe network policy.                                                           |
| `9`  | `Network administratively prohibited`       | Access to the specified destination network is administratively prohibited.<br>A strong indicator of a firewall rule.                                                |
| `10` | `Host administratively prohibited`          | Access to the specified destination host is administratively prohibited.<br>A strong indicator of a firewall rule.                                                   |
| `11` | `Network unreachable for ToS`               | The network is unreachable for the specified Type of Service (ToS) value.<br>Rare; may indicate QoS or security policies.                                            |
| `12` | `Host unreachable for ToS`                  | The host is unreachable for the specified Type of Service (ToS) value.<br>Rare; may indicate QoS or security policies.                                               |
| `13` | `Communication administratively prohibited` | Communication with the destination is administratively prohibited.<br>A strong indicator of a firewall rule.                                                         |
| `14` | `Host Precedence Violation`                 | The precedence of the packet violates a security policy.<br>Very rare; legacy.                                                                                       |
| `15` | `Precedence cutoff in effect`               | The precedence of the packet is below the cutoff level for the network.<br>Very rare; legacy.                                                                        |

>[!important] Codes `9`, `10`, and `13` are a definitive sign that a firewall is actively blocking your scan. A scan that generates these codes is likely being detected.

## Stealth scan types

Nmap supports numerous scan techniques, some of which are specifically designed to minimize the scan's visibility to defensive systems. 

Stealth scan types include:

- **TCP `SYN` scan (`-sS`)**
	- The default scan type (for privileged users) and the most popular for a reason. 
	- Nmap sends a TCP packet with the `SYN` flag set and waits for a `SYN-ACK` packet from open ports. An `RST` packet means the port is `closed`. If no response is received, the port is marked `filtered`.
	- It's often called a **half-open scan**, since Nmap never completes the three-way handshake. Many systems don't log such connection attempts, which makes this scan **highly effective for evasion**.
	- See [[྾_Nmap_port_scanning#`-sS` TCP `SYN` scan, or stealth scan]].

```bash
sudo nmap 192.168.1.11
```

```bash
sudo nmap -sS 192.168.1.11
```

- **TCP `FIN`, `NULL`, Xmas scan (`-sF`, `-sN`, `-sX`)**
	- These scans are even more stealth but less reliable; can be detected by modern IDS/IPS.
	- Nmap sends packets with unusual TCP flag combinations:
		- `FIN` scan (`-sF`): Sends a packet with only the `FIN` flag.
		- `NULL` scan (`-sN`): Sends a packet with no flags.
		- `Xmas` scan (`-sX`): Sends a packet with the `FIN`, `PSH`, and `URG` flags set (like a Christmas tree).
	- These scans leverage a subtle loophole in the TCP RFC 793, which dictates that if a closed port receives a TCP packet without the `SYN`, `RST`, or `ACK` bits set, it should respond with an `RST`. Open ports should ignore such packets.
	- These scans work best against non-Windows and non-Cisco devices (see "The `RST` Paradox").
	- See [[྾_Nmap_port_scanning#Inverse TCP scans `-sN`, `-sF`, `-sX`]].

```bash
sudo nmap -sN 192.168.1.11
```

```bash
sudo nmap -sF 192.168.1.11
```

```bash
sudo nmap -sX 192.168.1.11
```

>[!warning] The `RST` paradox
>In many TCP scans, the target responds with an `RST` packet if the port is **closed**.
>However, many firewalls and systems **send `RST` for any unsolicited packet** — even to open ports. Such behavior is especially known to pertain Microsoft Windows and Cisco devices.
>As a result, the port is marked `closed` when it should be `open|filtered`. This violates the specification and puts the scan reliability under questioning. 

- **TCP `ACK` scan (`-sA`)**
	- This scan does not determine if a port is `open` or `closed`, but it can **map out firewall rules** and determine whether the firewall is **stateful** or **stateless**. 
	- Nmap sends `ACK` packets to specified ports. If an `RST` is returned, the port is marked `unfiltered` (reachable by the target host). If no response is received, or an ICMP unreachable error is returned, the port is `filtered`.
	- Results may be inaccurate for Windows and Cisco devices, due to the aforementioned "`RST` paradox". 
	- See [[྾_Nmap_port_scanning#`-sA` TCP `ACK` scan]].

```bash
nmap -sA 192.168.1.11
```

>[!note] For more about different port scanning techniques, read [[྾_Nmap_port_scanning]].

- **TCP idle scan (`-sI`)**
## Reducing scan noise (`-Pn`, `-n`, `--disable-arp-ping`)

To reduce your traces further, use the following options:

- **`-Pn`: No ping scan**
	- **:** By default, Nmap first sends ICMP Echo Requests (pings) and other probes to determine if the host is up before attempting a port scan. 
	- If a firewall blocks these probes, Nmap will incorrectly assume the host is down and not scan it at all.
	- You can disable ICMP Echo Requests with the `-Pn` option: Nmap will skip host discovery, assuming all target hosts are alive, and proceed directly to port scanning.

```bash
sudo nmap -Pn 192.168.1.11
```

- **`-n`: Disable DNS Resolution**
	- By default, Nmap performs reverse DNS resolution for every responsive IP address. These DNS queries can be logged by the target's DNS server, leaving a trace of your activity. 
	- The `-n` option disables all DNS resolution, which also speeds up the scan.

```bash
sudo nmap -Pn -n 192.168.1.11
```

-  **`--disable-arp-ping`: Disable ARP ping on local LAN**
	- When scanning on a local Ethernet network (by a privileged user), Nmap uses ARP requests for host discovery by default. This is very fast and reliable but can easily be detected. 
	- The `--disable-arp-ping` option disables ARP request.

```bash
sudo nmap -Pn -n --disable-arp-ping 192.168.1.11
```

For more, see [[྾_Nmap_port_scanning#`-sS` TCP `SYN` scan, or stealth scan]].
## Timing and performance control (`-T0` to `-T5`)

Scan speed is a critical factor in evasion. A fast, aggressive scan is noisy and easily flagged by an IDS. A slow scan can blend in with normal traffic. Nmap's timing options provide granular control over scan aggression and speed.

>Nmap's timing templates, set with the `-T` flag, control how quickly and aggressively Nmap sends probes during a scan. This affects scan speed, stealth, and the likelihood of triggering security alerts.

Nmap provides six timing templates: from `-T0` (slowest and most stealthy, also called `paranoid`) to `-T5` (fastest and most aggressive, also called `insane`).  These are presets that adjust multiple low-level parameters, such as scan timeout, delay between probes, maximum probe rate, and others.

| Option | Name        | Description                                                                                                                                                                          |
| ------ | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `-T0`  | `paranoid`  | Extremely slow; minimizes detection risk.<br>Spreads probes over long periods.<br>Best for highly sensitive environments, maximum stealth.                                           |
| `-T1`  | `sneaky`    | Very slow and cautious.<br>Good for evading IDS/IPS.                                                                                                                                 |
| `-T2`  | `polite`    | Slower than default; reduces bandwidth usage and target machine load.<br>Used for avoiding disruption, polite scanning.                                                              |
| `-T3`  | `normal`    | Default; balanced performance.<br>Best for general-purpose scanning.                                                                                                                 |
| `-T4`  | `agressive` | Fast; suitable for reasonably fast and stable networks.                                                                                                                              |
| `-T5`  | `insane`    | Maximum speed; likely to trigger alarms.<br>Assumes that you are on an extraordinarily fast network or are willing to sacrifice some accuracy for speed.<br>Best for local networks. |

 >[!note]+
 >- The `paranoid` (`-T0`) and `sneaky` (`-T1`) templates are your primary tools for IDS/IPS evasion; they space out probes and reduce scan rate.
 >- The `aggressive` (`-T4`) and `insane` (`-T5`) templates they increase parallelism and probe rate, making scans much faster but more likely to be detected.

### Adjusting timing parameters manually

For more granular control, you can override the templates and tune individual timing parameters manually.

| Option                    | Purpose                                                                                                                |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `--max-rate`/`--min-rate` | Caps/guarantees the number of packets sent per second. `max-rate` is a powerful tool for staying under IDS thresholds. |
|                           |                                                                                                                        |
| `--min/--max-parallelism` | Min/max probes in parallel                                                                                             |
| `--min/--max-rtt-timeout` | Min/max wait for response                                                                                              |
| `--max-retries`           | Maximum retry limit per port.                                                                                          |
| `--host-timeout`          | Maximum scan time per host.                                                                                            |
| `--scan-delay`            | Delay between probes.                                                                                                  |
| `--max-rate`              | Maximum number of packets per second.                                                                                  |
| `--min-rate`              | Minimum number of packets per second.                                                                                  |
| `--max-parallelism`       | Maximum number of probes sent in parallel.                                                                             |
| `--min-parallelism`       | Minimum number of probes sent in parallel.                                                                             |
| `--max-rtt-timeout`       | Maximum round trip timeout.                                                                                            |
| `--min-rtt-timeout`       | Minimum round trip timeout.                                                                                            |
| `--initial-rtt-timeout`   | Initial probe timeout.                                                                                                 |

- **Maximum retries: `--max-retries`**
	- Sets the maximum number of probe retransmissions to a port. 
	- The value of `0` means no retries  (faster but less reliable; may miss open ports if packets are dropped by accident).

```bash
nmap -p21-25 192.168.1.139 --max-retries 0
```

- **Host timeout: `--host-timeout`**
	- Aborts scanning a host after the specified timeout.
	- Too short timeout can cause incomplete or inaccurate results, especially on slow networks, but this is useful for skipping unresponsive hosts quickly.

```bash
nmap -p21-25 192.168.1.139 --host-timeout 100ms
```

>[!note] The time can be specified in milliseconds (`ms`), seconds (`s`), or minutes (`m`).

- **Scan delay: `--scan-delay`**
	- Nmap will wait at least this long between each probe sent to a given host. 
	- Slows down the scan but can bypass rate-limiting defenses. Excellent for fine-grained rate limiting.

```bash
nmap -p21-25 192.168.1.139 --scan-delay 11s
```

- **Maximum and minimum rate: `--max-rate` and `--min-rate`**
	- `--max-rate`: Caps the number of packets sent per second; a powerful tool for staying under IDP thresholds.
	- `--min-rate`: Guarantees at least a certain number of packets are sent per second.

```bash
nmap -p21-25 192.168.1.139 --max-rate 2
```

>[!tip]+
>You can combine `--max-rate` with `--scan-delay` for precise control over the scan's pacing. For example, `--max-rate 1 --scan-delay 1s` ensures exactly one packet per second.

- **Parallelism: `--min-parallelism` and `--max-parallelism`**
	- Controls the number of probes Nmap can have outstanding (in parallel) for a host group.
	- For example, `--min-parallelism 2 --max-parallelism 2` ensures exactly 2 probes at a time.

```bash
nmap -p21-25 192.168.1.139 --min-parallelism 2 --max-parallelism 2
```

- **Round trip timeouts: `--min-rtt-timeout`, `--max-rtt-timeout`, and `--initial-rtt-timeout`**
	- When Nmap sends a packet, it takes some time to receive a response. This time is called **RTT — Round-Trip Time**. Nmap generally starts with a high RTT timeout of **100 ms** (`--min-RTT-timeout`).
	- `--min-rtt-timeout`: Minimum time to wait for a response.
	- `--max-rtt-timeout`: Maximum time to wait for a response.
	- `--initial-rtt-timeout`: Initial time to wait for a response.

>[!example]+ Example: default RTT and optimized RTT scans
> - Default scan:
> 
> ```bash
> sudo nmap 10.129.2.0/24 -F
> 
> # ...
> Nmap done: 256 IP addresses (10 hosts up) scanned in 39.44 seconds
> ```
> 
> - Optimized RTT:
> 
> ```bash
> sudo nmap 10.129.2.0/24 -F --initial-rtt-timeout 50ms --max-rtt-timeout 100ms
> 
> # ...
> Nmap done: 256 IP addresses (8 hosts up) scanned in 12.29 seconds
> ```
> 
>In the above examples, the scan with shortened timeout found two hosts less, but it tool only a **quarter** of the time the default one took.



- **Initial round trip timeout: `--initial-rtt-timeout`**
	- Sets the initial probe timeout. Nmap uses this as a starting point and adjusts it based on network response times.

- **Host groups: `--max-hostgroup` and `--min-hostgroup`**
	- Nmap can scan hosts in parallel. For this, it divides the target IP address space into groups and then scans one group at a time. Generally, the larger the group the more efficient the scan; however, host results can't be provided until the scan for the whole group is finished.
	- The `--max-hostgroup` sets the maximum group size Nmap will never exceed, and `--min-hostgroup` sets the minimum group size Nmap will try to keep.

>[!note] The `--max-hostgroup` and `--min-hostgroup` options don't affect host discovery scans: host discovery always works in large groups of hosts to improve speed and accuracy.

- **Script timeout: `--script-timeout`**
	- Sets the maximum runtime for individual NSE scripts. 
	- Prevents a single script from stalling the entire scan. 
	- `0` means no timeout (can be used to override the `-T5` template which sets the timeout to 10 minutes).
	- See [[྾_Nmap_NSE_scripts]].
### Template parameter breakdown

The following table details the specific internal parameters set by each timing template. A value of `0` or "Dynamic" means Nmap automatically adjusts the value during the scan.

| Template                |   `T0`   |  `T1`  |  `T2`  |  `T3`   |    `T4`    |  `T5`   |
| ----------------------- | :------: | :----: | :----: | :-----: | :--------: | :-----: |
| **Name**                | Paranoid | Sneaky | Polite | Normal  | Aggressive | Insane  |
| `--min-rtt-timeout`     |  100 ms  | 100 ms | 100 ms | 100 ms  |   100 ms   | 100 ms  |
| `--max-rtt-timeout`     |  5 min   | 15 sec | 10 sec | 10 sec  |  1250 ms   | 300 ms  |
| `--initial-rtt-timeout` |  5 min   | 15 sec | 1 sec  |  1 sec  |   500 ms   | 250 ms  |
| `--max-retries`         |    10    |   10   |   10   |   10    |     6      |    2    |
| `--scan-delay`          |  5 min   | 15 sec | 400 ms |    0    |     0      |    0    |
| `--max-parallelism`     |    1     |   1    |   1    | Dynamic |  Dynamic   | Dynamic |
| `--host-timeout`        |    0     |   0    |   0    |    0    |     0      | 15 min  |
| `--script-timeout`      |    0     |   0    |   0    |    0    |     0      | 10 min  |

>[!note] The `--min-parallelism`, `--min-hostgroup`, `--max-hostgroup`, `--min-rate`, `--max-rate` parameters are not affected by timing templates.

>[!interesting]- Manual equivalents
> 
> - `-T0` (Paranoid):
> 
> ```bash
> nmap \
> 	--scan-delay 5m \
> 	--max-retries 10 \
> 	--min-rtt-timeout 100ms \
> 	--max-rtt-timeout 300000ms \
> 	--initial-rtt-timeout 300000ms \
> 	--max-parallelism 1 \
> TARGET_IP
> ```
> 
> - `T1` (Sneaky):
> 
> ```bash
> nmap \
> 	--scan-delay 15s \
> 	--max-retries 10 \
> 	--min-rtt-timeout 100ms \
> 	--max-rtt-timeout 15000ms \
> 	--initial-rtt-timeout 15000ms \
> 	--max-parallelism 1 \
> TARGET_IP
> ```
> 
> - `-T2` (Polite):
> 
> ```bash
> nmap \
> 	--scan-delay 400ms \
> 	--max-retries 10 \
> 	--min-rtt-timeout 100ms \
> 	--max-rtt-timeout 10000ms \
> 	--initial-rtt-timeout 1000ms \
> 	--max-parallelism 1
> TARGET_IP
> ```
> 
> - `-T3` (Normal):
> 
> ```bash
> nmap \
> 	--scan-delay 0 \
> 	--max-retries 10 \
> 	--min-rtt-timeout 100ms \
> 	--max-rtt-timeout 10000ms \
> 	--initial-rtt-timeout 1000ms
> TARGET_IP
> ```
> 
> 
> - `-T4` (Aggressive):
> 
> ```bash
> nmap \
> 	--scan-delay 0 \
> 	--max-retries 6 \
> 	--min-rtt-timeout 100ms \
> 	--max-rtt-timeout 1250ms \
> 	--initial-rtt-timeout 500ms \
> 	--max-scan-delay 10ms
> TARGET_IP
> ```
> 
> 
> - `-T5` (Insane):
> 
> ```bash
> nmap \
> 	--scan-delay 0 \
> 	--max-retries 2 \
> 	--min-rtt-timeout 50ms \
> 	--max-rtt-timeout 300ms \
> 	--initial-rtt-timeout 250ms \
> 	--max-scan-delay 5ms \
> 	--host-timeout 15m
> TARGET_IP
> ```

## Packet fragmentation (`-f`, `-ff`, `--mtu`)

>**Packet fragmentation (`-f`)** is a technique where Nmap splits probe IP packets into smaller fragments before sending then to the target. 

This can make it harder for firewalls and IDS/IPS to recognize and block the scan, especially if those systems do not properly reassemble fragmented packets or don't bother inspecting beyond the first fragment.

```bash
# pplit packets into 8-byte fragments
sudo nmap -f TARGET_IP

# splits packets into 16-byte fragments
sudo nmap -ff TARGET_IP
```

| Option           | Description                                                  |
| ---------------- | ------------------------------------------------------------ |
| `-f`             | Split packets into `8`-byte fragments (after the IP header). |
| `-ff` or `-f -f` | Split packets into `16`-byte fragments.                      |
| `--mtu SIZE`     | Set a custom fragment size; must be a multiple of `8`.       |

>[!warning] Fragmentation is supported for Nmap raw packet scans, including TCP SYN scans (`-sS`), UDP scans (`-sU`), and OS detection (`-O`).

>[!warning] Fragmentation doesn't work with TCP Connect scans (`-sT`) or FTP bounce scans.  

>[!example]+ Example: Nmap fragmentation
>```bash
>sudo nmap -f 192.168.1.11
>```

>[!example]+ Example: Nmap fragmentation with custom MTU (Maximum Transmission Unit)
>```bash
>sudo nmap --mtu 24 192.168.1.11
>```

>[!interesting]+ Why does fragmentation help evade detection?
>- **Signature evasion:** Many firewalls and IDS/IPS devices look for specific patterns or signatures in network traffic. If a scan packet is split into fragments, these devices **may not see the full signature** in any single fragment, making detection more difficult.
>- **Bypassing simple filters:** Some packet filters only inspect the first fragment of a packet (where the TCP/UDP header usually resides). If the header is split across fragments, the filter may not have enough information to block the scan.
>- **Legacy device weaknesses:** Older or misconfigured security devices may not reassemble fragments at all. Fragmented probes will slip through undetected, and reassembled only at the target host.

>[!warning] Modern, stateful firewalls and most IDS/IPS are capable of reassembling fragmented packets, rendering this technique less effective. 

>[!warning] "Suspicious fragmented traffic" alone can trigger alerts.

## Payload customization (`--data-length`, `--data-string`, `--data`)

By default, Nmap's probe packets are minimal. You can append data to these packets to alter their size and content to evade signature-based detection systems that look for default Nmap probes.

- **`--data-length`**
	- Appends the specified number of random bytes to most packets sent. 
	- This is a simple way to vary packet sizes and avoid size-based signatures.

```bash
# add 25 random bytes to each probe packet 
sudo nmap --data-length 25 192.168.1.11
```

- **`--data-length`**
	- Appends a given ASCII string as a payload. 
	- This can be used to mimic legitimate application traffic.

```bash
# add a string that might look like part of an HTTP request
sudo nmap -p 80 --data-string "GET /index.html HTTP/1.1" 192.168.1.11
```

- **`--data`**
	- Appends a custom binary payload specified as a hexadecimal string.
	- Can be used to test specific IDS rules or even exploit vulnerabilities.

```bash
# add the hex bytes DE AD BE EF to each packet
sudo nmap --data 0xdeadbeef 192.168.1.11
```
## IP address spoofing (`-S`)

>With **source IP address spoofing (`-S`)**, Nmap crafts network packets with the source IP address in the header set to an address of a host other than your own. This makes the scan appear to originate from another machine.

```bash
sudo nmap -S SPOOFED_ADDRESS TARGET_IP
```

>[!example]+ Example: IP address spoofing in Nmap
>```bash
>sudo nmap -S 192.168.1.100 192.168.1.11
>```
>This makes it look like this scan is coming from `192.168.1.100` instead of your actual machine.

>[!warning]+ No replies
>**You will not receive replies.** When you spoof your source IP, the target sends all responses to the spoofed address, not to you. 
>This means Nmap won't be able to complete most scan types or provide useful results (say, it won't receive the `SYN-ACK` or `RST` packets needed to determine port states). 
>This is a **blind scanning** technique, useful for triggering IDS alerts from a fake source or for certain advanced attacks, but not for general port scanning.

>[!warning] Some ISPs may filter spoofed packets, but many do not.

>[!note]+ Controlling network interface
>You can also specify the network interface to send packets from with the `-e` option. This can be useful on multi-homed systems.
> 
> ```bash
> sudo nmap -e INTERFACE TARGET_IP
> ```
> ```bash
> sudo nmap -e eth1 192.168.1.11
> ```
 
>[!note]+ MAC address spoofing
>For local network scans, you can also spoof your MAC address with the `--spoof-mac` option. 
> ```bash
> sudo nmap --spoof-mac MAC_ADDRESS TARGET_IP
> ```
> ```bash
> sudo nmap --spoof-mac 00:11:22:33:44:55 TARGET_IP
> ```
> To use a random MAC address:
> ```
>sudo nmap --spoof-mac 0 TARGET_IP # random MAC address
> ```
## Decoys (`-D`)

>In a **decoy scan (`-D`)**, Nmap sends multiple probe packets, some with your real IP address and others with spoofed decoy IP addresses. 

This floods the target's logs with traffic from multiple sources, making it much harder for an administrator to determine which IP was the real attacker.

>[!note] Probe packets are sent in **batches**: the target sees traffic from all listed addresses nearly simultaneously.

```bash
sudo nmap -D DECOY_1,DECOY_2,ME,RND TARGET_IP
```

| Placeholder                | Description                                                                                           |
| -------------------------- | ----------------------------------------------------------------------------------------------------- |
| `DECOY_1`, `DECOY_2`, etc. | IP addresses of other (ideally live) hosts to use as decoys.                                          |
| `ME`                       | Replaced with your own IP address;<br>indicates where to insert your real IP address in the sequence. |
| `RND` or `RND:num`         | Replaced with one or more random decoy IP addresses.                                                  |

>[!example]+ Example: Nmap decoys
>```bash
>sudo nmap -D 192.168.1.5,192.168.1.12,ME,192.168.1.9 192.168.1.11
>```

>[!warning] If you put `ME` in the 6th position or later, some port scan detectors may not show your IP at all.

>[!example]+ Example: Nmap random decoys
>```bash
>sudo nmap -D RND:5,ME 192.168.1.11
>```
>- Nmap will send 5 packets with random source IP addresses (decoys), and one from you. 

>[!tip] Using hostnames as decoys can leave traces in DNS logs; prefer IP addresses.

>[!tip] Too many decoys can slow down the scan and reduce accuracy.

>[!warning] Some ISPs may filter spoofed packets, but many do not.

 Decoys are used using during both the initial host discovery and port scanning phases, as well as remote OS detection (`-O`). 
 
>[!warning] Decoys are incompatible with scan types that require a full connection, such as version detection (`-sV`) or TCP Connect scan (`-sT`).
>Suppose Nmap sends a `SYN` packet with a spoofed source IP address. If the port is open, the target, trying to complete the TCP three-way handshake, sends a `SYN-ACK` back to the **spoofed IP address**. You will never receive this packet and respond with `ACK` to complete the handshake and confirm the port is open or retrieve the service version. 
>The handshake will only succeed with your real IP address, and this will immediately reveal you as the true origin of the scan. Use decoys only with stateless scans like `-sS`, `-sN`, `-sF`, `-sX`, or `-sU`.
>The same goes for spoofing.

>[!important] The key point is that **decoys only work for stateless or semi-stateless scans**—not for scans that require a full TCP session or application-layer interaction.
## Source port manipulation (`-g`, `--source-port`)

Surprisingly, many firewalls are configured to filter inbound traffic based on source port numbers. For example, a firewall might allow any packet with a source port of `53` (DNS), `80` (HTTP), or `443` (HTTPS). 

Nmap can exploit this by setting a custom source port on its probe packets. You can control the source port with the `-g` or `--source-port` option:

```bash
nmap --source-port 80 192.168.1.11
```

```bash
nmap -g 80 192.168.1.11
```

- `--source-port 0` lets Nmap choose a random source port for each probe:

```bash
nmap --source-port 0 192.168.1.11
```

- Use `--source-port 1000-65535` to specify a range of source ports:

```bash
nmap -p 3306 --source-port 1000-65535 192.168.1.11
```

This is extremely effective against simple firewalls. It can truck the into thinking the probe packets are related to legitimate web traffic.

>[!note]+ Common evasion source port choices
> - TCP port `80` (HTTP)
> - TCP port `443` (HTTPS)
> - UDP port `53` (DNS)
> - TCP port `22` (SSH)
## Defeating `RST` Rate Limiting (`--defeat-rst-ratelimit`)

Many modern operating systems (like Linux) and some firewalls will rate-limit the number of TCP `RST` packets **they** send in response to probes to closed ports. For example, a system might only send one `RST` packet per second.

>[!example]+
>Say, the `RST` limit on the target host is set to 1 `RST` per second.
>If Nmap scans 100 closed ports in one second, it will only receive a single `RST` packet. For the other 99 ports, Nmap receives no response and must wait for a timeout and potentially retransmit probes. This drastically slows down the scan.

The `--defeat-rst-ratelimit` option tells Nmap **not to wait for delayed `RST` packets**. If a timely `RST` is not received, Nmap will classify the port as `filtered`. 

```bash
nmap --defeat-rst-ratelimit 192.168.1.11
```

You can use it with scan types that rely on `RST` packets, such as TCP `SYN` scan (`sS`).


>[!note]+ Use case
>This is extremely useful for large-scale scans where you primarily care about finding `open` ports. The `--open` option (which only shows open ports) implies this behavior in recent Nmap versions (since Nmap 7.40).

>[!note] This is a trade-off: you gain immense speed at the cost of accuracy in distinguishing between `closed` and `filtered` ports.

## References and further reading

- [`Firewall/IDS Evasion and Spoofing — Nmap`](https://nmap.org/book/man-bypass-firewalls-ids.html)
- [`Nmap Scan with Timing Parameters — Hacking Articles`](https://www.hackingarticles.in/nmap-scan-with-timing-parameters/)
- [`Timing Templates (-T) — Nmap`](https://nmap.org/book/performance-timing-templates.html)
- [`Timing and Performance — Nmap`](https://nmap.org/book/man-performance.html)
- [`Bypassing Firewall Rules — Nmap`](https://nmap.org/book/firewall-subversion.html)
- [`Proxying — Nmap`](https://nmap.org/ncat/guide/ncat-proxy.html)


# drafts


>[!note]- The ICMP `Destination Unreachable` (type `3`) codes 
> - `Destination network unreachable` (type `3`, code `0`)
> - `Destination host unreachable` (type `3`, code `1`)
> - `Destination protocol unreachable` (type `3`, code `2`)
> - `Destination port unreachable` (type `3`, code `3`)
> - `Fragmentation required, and DF flag set` (type `3`, code `0`)
> - `Source route failed` (type `3`, code `0`)
> - `Network administratively prohibited` (type `3`, code `0`)
> - `Host administratively prohibited` (type `3`, code `0`)
> - `Network unreachable for ToS` (type `3`, code `0`)
> - `Host unreachable for ToS` (type `3`, code `0`)
> - `Communication administratively prohibited` (type `3`, code `0`)
> - `Host Precedence Violation` (type `3`, code `0`)
> - `Precedence cuoff in effect` (type `3`, code `0`)



These techniques rest on three evasion strategies:
- Timing manipulation
- Packet manipulation
- Identity obfuscation


|Parameter|Purpose|Example|
|---|---|---|
|`--max-retries <num>`|Sets the maximum number of probe retransmissions to a port. A value of `0` means no retries, which is faster but less reliable.|`--max-retries 1`|
|`--host-timeout <time>`|Abandons scanning a host after this amount of time. Useful for skipping slow or unresponsive hosts. `(e.g., 20m, 900s, 30000ms)`|`--host-timeout 10m`|
|`--scan-delay <time>`|Nmap will wait at least this long between each probe sent to a given host. Excellent for fine-grained rate limiting.|`--scan-delay 500ms`|
|`--max-rate <num>` / `--min-rate <num>`|Caps or guarantees the number of packets sent per second. `max-rate` is a powerful tool for staying under IDS thresholds.|`--max-rate 10`|
|`--min-parallelism <num>` / `--max-parallelism <num>`|Controls the number of probes Nmap can have outstanding (in parallel) for a host group.|`--max-parallelism 1`|
|`--min-rtt-timeout <time>` / `--max-rtt-timeout <time>`|Sets the bounds on how long Nmap will wait for a probe response. Tuning these can help on very slow or very fast networks.|`--max-rtt-timeout 200ms`|
|`--initial-rtt-timeout <time>`|Sets the initial probe timeout. Nmap uses this as a starting point and adjusts it based on network response times.|`--initial-rtt-timeout 300ms`|
|`--min-hostgroup <num>` / `--max-hostgroup <num>`|Adjusts the size of host groups scanned in parallel. Larger groups are more efficient but delay result reporting.|`--min-hostgroup 64`|
|`--script-timeout <time>`|Sets the maximum runtime for individual NSE scripts. Prevents a single script from stalling the entire scan.|`--script-timeout 5m`|
