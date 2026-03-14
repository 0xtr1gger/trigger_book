---
created: 2026-03-11
tags:
  - tools
  - nta
---

### Table of contents

- [[#tcpdump]]
- [[#Interface discovery and basic capture]]
- [[#Interface discovery and basic capture]]
- [[#Output formatting]]
	- [[#Timestamps]]
- [[#Writing and reading PCAP files]]
- [[#Understanding tcpdump output]]
- [[#Packet filtering — BPF expressions]]
	- [[#Host filtering]]
	- [[#Port filtering]]
	- [[#Protocol filtering]]
	- [[#Packet length filtering]]
	- [[#Logical operators]]
	- [[#VLAN filtering]]
	- [[#IP protocol number filtering]]
	- [[#Byte-level filtering]]
		- [[#TCP flag filtering]]
		- [[#ICMP type filtering]]
		- [[#IP header filtering]]
- [[#Option quick reference]]
- [[#References and further reading]]
## tcpdump

>**[`tcpdump`]([https://en.wikipedia.org/wiki/Tcpdump](https://www.tcpdump.org/))** is a **command-line packet analyzer** that captures and decodes network packets directly from a network interface or from a previously saved packet capture file (`.pcap`).

- `tcpdump` runs on Linux, macOS, and BSD. Windows equivalent is `WinDump`.
- Internally, `tcpdump` relies on the `libpcap` library, which provides a portable interface for raw packet capture.
- Filtering is handled by **BPF (Berkeley Packet Filter)** — a kernel-level bytecode VM that evaluates filter expressions before packets are passed to userspace. This means that kernel discards unmatched packets before `tcpdump` ever seems them, and this is why this method is so efficient.
- To capture all traffic that reaches the host (not just traffic addresses to the host), `tcpdump` the interface into the **promiscuous mode**. 

>[!interesting]+ Promiscuous mode
>**Promiscuous mode** is an operating mode of a network interface controller (NIC) that causes the controller to pass **all traffic it receives** to the CPU for processing, rather than filtering and only passing frames addressed to its specific MAC address.
> 
> - In this mode, the NIC no longer drops packets not intended for it, but captures everything it receives — regardless of the destination address.
> - On most operating systems, including Linux and Windows, you need **elevated privileges** to enable promiscuous mode on an interface. 


>[!note]+ Installation
>```bash
>sudo apt install tcpdump
>```

>[!note]+ Verify version
>```bash
>sudo tcpdump --version
>```

>[!note] See [`tcpdump(1) man pages — tcpdump.org`](https://www.tcpdump.org/manpages/tcpdump.1.html).

## Interface discovery and basic capture

- List available interfaces:

```bash 
sudo tcdump -D
```

> [!example]+ 
> ```bash 
> sudo tcpdump -D
> ```
> 
> ```bash
> 1.ens3 [Up, Running, Connected]
> 2.tun0 [Up, Running, Connected]
> 3.any (Pseudo-device that captures on all interfaces) [Up, Running]
> 4.lo [Up, Running, Loopback]
> 5.lxcbr0 [Up, Disconnected]
> 6.bluetooth-monitor (Bluetooth Linux Monitor) [Wireless]
> 7.nflog (Linux netfilter log (NFLOG) interface) [none]
> 8.nfqueue (Linux netfilter queue (NFQUEUE) interface) [none]
> 9.dbus-system (D-Bus system bus) [none]
> 10.dbus-session (D-Bus session bus) [none]
> ```

- Start a capture on a specific interface (`ens3` in this example):

```bash
sudo tcpdump -i ens3
```

- Capture on **all interfaces at once** using `any` pseudo-device:

```bash
sudo tpcdump -i any
```

>[!important] The `any` pseudo-device aggregates traffic from all available capture devices, as printed by the `-D` flag.
>- The capture devices may include not only network interfaces like `ens3` or `wlan0`, but also capture devices that `libpcap` implements by means other than the OS network stack, such as **Bluetooth**, **DAG**, **D-Bus**, **SNF**, and **USB**.

>[!note] All regular network interfaces are a subset of all available capture devices.

- Capture on the loopback interface (useful for debugging local services):

```bash
sudo tcpdump -i lo
```

| Option              | Description                                                             |
| ------------------- | ----------------------------------------------------------------------- |
| `-i <interface>`    | Capture packets from the specified network interface.                   |
| `-D`                | List available network interfaces for packet capture.                   |
| `-I`                | Enable monitor mode on supported wireless interfaces.                   |
| `-y <datalinktype>` | Set the data link type for packet capture.                              |
| `-p`                | Disable promiscuous mode (only capture traffic addressed to this host). |
| `-Q in\|out\|inout` | Filter by capture direction at the interface level                      |

## Output formatting

- Disable hostname resolution (show raw IP addresses):

```bash
sudo tcpdump -i ens3 -n
```

- Disable both hostname **and** port name resolution (show numeric ports instead of `http`, `ssh`, etc.):

```bash
sudo tcpdump -i ens3 -nn
```

> [!example]-
> 
> ```bash
> sudo tcpdump -i ens3 -c 3 -nn
> ```
> 
> ```bash
> tcpdump: verbose output suppressed, use -v[v]... for full protocol decode
> listening on ens3, link-type EN10MB (Ethernet), snapshot length 262144 bytes
> 06:04:52.376428 IP 94.237.122.195.80 > 94.237.50.147.38372: Flags [P.], seq 141890140:141890930, ack 1143028512, win 424, options [nop,nop,TS val 2165660361 ecr 2037630551], length 790: HTTP
> 06:04:52.376564 IP 94.237.122.195.80 > 94.237.50.147.38504: Flags [P.], seq 298784202:298784988, ack 403484873, win 371, options [nop,nop,TS val 2165660361 ecr 2037630556], length 786: HTTP
> 06:04:52.376700 IP 94.237.50.147.38504 > 94.237.122.195.80: Flags [.], ack 786, win 9400, options [nop,nop,TS val 2037630584 ecr 2165660333], length 0
> 3 packets captured
> 30 packets received by filter
> 0 packets dropped by kernel
> ```

>[!tip] `-nn` should be your default.

By default, `tcpdump` prints one-line summary per packet. It's often enough, but for deeper analysis you'll need more.

- Print payload in ASCII:

```bash
sudo tcpdump -i ens3 -A
```

- Print payload in hex:

```bash
sudo tcpdump -i ens3 -x
```

- Print payload in both hex and ASCII:

```bash
sudo tcpdump -i ens3 -X
```

> [!example]-
> 
> ```bash
> sudo tcpdump -i ens3 -c 1 -nn -X 
> ```
> 
> ```bash
> tcpdump: verbose output suppressed, use -v[v]... for full protocol decode
> listening on ens3, link-type EN10MB (Ethernet), snapshot length 262144 bytes
> 06:06:28.275176 IP 94.237.122.195.80 > 94.237.50.147.38372: Flags [P.], seq 148907007:148907649, ack 1143079980, win 424, options [nop,nop,TS val 2165756259 ecr 2037726468], length 642: HTTP
> 	0x0000:  4500 02b6 0ad9 4000 4006 c238 5eed 7ac3  E.....@.@..8^.z.
> 	0x0010:  5eed 3293 0050 95e4 08e0 23ff 4422 042c  ^.2..P....#.D".,
> 	0x0020:  8018 01a8 6dd9 0000 0101 080a 8116 d163  ....m..........c
> 	0x0030:  7975 3d04 827e 027e f800 0000 8000 0001  yu=..~.~........
> 	0x0040:  0101 0000 ffff 0000 0068 0020 0001 0000  .........h......
> 	0x0050:  0007 6001 0614 1d2b 9fef 005b cb01 98a8  ..`....+...[....
> 	0x0060:  1c20 2a28 1d29 2917 1e2b 1282 d40b 981b  ..*(.))..+......
> 	0x0070:  d9c0 4b35 80cd 4f00 0000 00ff ff00 0000  ..K5..O.........
> 	0x0080:  6900 2000 0100 0000 0760 0104 141d 2b9f  i........`....+.
> 	0x0090:  ef00 5bcb 019f e90c 482c 2b0e c22d 0fec  ..[.....H,+..-..
> 	0x00a0:  4701 472e 0000 0000 ffff 0098 0069 0008  G.G..........i..
> 	0x00b0:  0001 0000 0007 6001 0514 1d2b 41a7 029e  ......`....+A...
> 	0x00c0:  ef00 9fef 009f ec05 6350 2a00 0102 0304  ........cP*.....
> 	0x00d0:  0500 0001 1800 6900 0800 0100 0000 0760  ......i........`
> 	0x00e0:  0105 141d 2b41 a702 9eef 009f ef00 9fec  ....+A..........
> 	0x00f0:  0563 502a 0000 0001 0203 0405 0258 0069  .cP*.........X.i
> 	0x0100:  0008 0001 0000 0007 6001 0514 1d2b 41a7  ........`....+A.
> 	0x0110:  029e ef00 9fef 009f ec05 6350 2a00 0000  ..........cP*...
> 	0x0120:  0102 0304 0502 8000 6900 0800 0100 0000  ........i.......
> 	0x0130:  0760 0105 141d 2b41 a702 9eef 009f ef00  .`....+A........
> 	0x0140:  9fec 0563 502a 0000 0001 0203 0405 0000  ...cP*..........
> 	0x0150:  006a 0020 0003 0000 0007 6001 0514 1d2b  .j........`....+
> 	0x0160:  9fef 0037 5220 2548 2037 5023 2121 2b14  ...7R.%H.7P#!!+.
> 	0x0170:  c229 0f5c ed06 5f6b 41e8 0210 3cf2 0000  .).\.._kA...<...
> 	0x0180:  0000 ffff 0000 006d 0020 0019 0000 0007  .......m........
> 	0x0190:  5001 0114 1d2b 9fef 0014 2276 8e1b a40e  P....+...."v....
> 	0x01a0:  14bd 208c 1c13 c4b0 0100 0000 ffff 0158  ...............X
> 	0x01b0:  006d 0018 0019 0000 0007 6001 2214 1d2b  .m........`."..+
> 	0x01c0:  786f 2715 1d2b 9fef 0015 3519 7cea 0127  xo'..+....5.|..'
> 	0x01d0:  3b25 405f 1e1a 3e1e 57a8 0796 ec01 91ea  ;%@_..>.W.......
> 	0x01e0:  009b dc04 95ed 016d 7e1f 2736 1a77 e901  .......m~.'6.w..
> 	0x01f0:  1531 197a e901 1534 197b ea01 1628 2721  .1.z...4.{...('!
> 	0x0200:  720b 9cef 0017 3721 3f5f 1e2e 4523 2f58  r.....7!?_..E#/X
> 	0x0210:  1483 eb01 7f86 202f 4523 2e43 261c 1e2b  ......./E#.C&..+
> 	0x0220:  9fe9 0e41 232b 571a 6c00 3814 87b5 1103  ...A#+W.l.8.....
> 	0x0230:  9cb1 c32a 0e1c a2c3 dee8 1114 c22e 2e2c  ...*...........,
> 	0x0240:  825d 1c78 b412 d696 3ca6 b828 68b1 0ee8  .].x....<..(h...
> 	0x0250:  d07a 34f5 c0a3 b881 636e 98e2 c0bb 8e80  .z4.....cn......
> 	0x0260:  1b3f 8937 1f1c 25d0 ab16 31a2 07bc 9102  .?.7..%...1.....
> 	0x0270:  7e59 c960 8b3d 847b 0000 0000 ffff 0000  ~Y.`.=.{........
> 	0x0280:  0086 0020 0019 0000 0007 5001 0114 1d2b  ..........P....+
> 	0x0290:  cccc cc0c a2f5 9216 90f9 0000 0000 ffff  ................
> 	0x02a0:  0000 0000 0000 0000 ffff ff20 f800 0000  ................
> 	0x02b0:  8000 0001 0101                           ......
> 1 packet captured
> 30 packets received by filter
> 0 packets dropped by kernel
> ```

- Display link-layer headers in the summary line (shows MAC addresses):

```bash
sudo tcpdump -i ens3 -e
```


- Print payload and link-layer headers in hex and ASCII:

```bash
sudo tcpdump -i ens3 -XX
```

>[!tip]+
> - To pipe `tcpdump` output to another program, such as `tee`, use the `-l` option:
> 
> ```bash
> tcpdump -l | tee dat
> ```

| Option                | Description                                                              |
| --------------------- | ------------------------------------------------------------------------ |
| `-n`                  | Disable hostname resolution.                                             |
| `-nn`                 | Disable hostname and port name resolution.                               |
| `-N`                  | Strip domain from hostnames (show `host` instead of `host.example.com`). |
| `-A`                  | Print payload in ASCII.                                                  |
| `-x`                  | Print payload in hex.                                                    |
| `-X`                  | Print payload in both hex and ASCII.                                     |
| `-e`                  | Display link-layer headers in the summary line (shows MAC addresses).    |
| `-XX`                 | Print payload and link-layer headers in hex and ASCII.                   |
| `-q`                  | Quiet — print less protocol details.                                     |
| `-v` / `-vv` / `-vvv` | Increasing verbosity.                                                    |
| `-s <snaplen>`        | Snapshot length (bytes per packet); use `0` for unlimited.               |
| `-l`                  | Line-buffer `stdout` (needed for piping to `grep`, `tee`, etc.).         |

> [!note] `-s 0` sets the snapshot length to the **full packet**. Without it, `tcpdump` only captures the first `262144` bytes of each packet on modern versions. This is usually fine, but some legacy setups default to `68` bytes — cutting off most of your payload.

#### Timestamps 

- For incident response where you need absolute timestamps with dates:

```bash
sudo tcpdump -i ens3 -tttt -nn
```

| Option             | Description                                                                                               |
| ------------------ | --------------------------------------------------------------------------------------------------------- |
| `-t`               | No timestamps.                                                                                            |
| `-tt`              | Seconds since Unix epoch (useful for scripting).                                                          |
| `-ttt`             | Delta time between packets (useful for latency analysis)                                                  |
| `-tttt`            | Full date and time (`YYYY-MM-DD HH:MM:SS.microseconds`).                                                  |
| `-ttttt`           | Time since first packet in capture.                                                                       |
| `--micro`          | Microsecond precision.                                                                                    |
| `--nano`           | Nanosecond precision.                                                                                     |
| `-j <tstamp_type>` | Select packet timestamp type (from [`pcap-tstamp`](https://www.tcpdump.org/manpages/pcap-tstamp.7.html)). |

>[!example]-
> - No timestamps:
> 
> ```bash
> sudo tcpdump -i enp0s3 -nn -c 1 -t tcp
> ```
> 
> ```bash
> # ...
>  IP 10.0.2.15.41726 > 38.46.226.33.443: Flags [P.], seq 3901180345:3901180479, ack 525579, win 65535, length 134
> # ...
> ```
> 
> - Seconds since Unix epoch:
> 
> ```bash
> sudo tcpdump -i enp0s3 -nn -c 1 -tt tcp
> ```
> 
> ```bash
> # ...
>  1773522779.817470 IP 10.0.2.15.41726 > 38.46.226.33.443: Flags [P.], seq 3901180479:3901180613, ack 526029, win 65535, length 134
> # ...
> ```
> 
> - Delta time between packets:
> 
> ```bash
> sudo tcpdump -i enp0s3 -nn -c 3 -ttt tcp
> ```
> 
> ```bash
> # ...
>  00:00:00.000000 IP 38.46.226.33.443 > 10.0.2.15.41726: Flags [P.], seq 544029:544179, ack 3901196559, win 65535, length 150
>  00:00:00.000035 IP 10.0.2.15.41726 > 38.46.226.33.443: Flags [.], ack 150, win 65535, length 0
>  00:00:00.067964 IP 10.0.2.15.41726 > 38.46.226.33.443: Flags [P.], seq 1:135, ack 150, win 65535, length 134
> # ...
> ```
> 
> 
> - Full date and time (`YYYY-MM-DD HH:MM:SS.microseconds`):
> 
> ```bash
> sudo tcpdump -i enp0s3 -nn -c 1 -tttt tcp
> ```
> 
> ```bash
> # ...
>  2026-03-14 21:13:12.537590 IP 38.46.226.33.443 > 10.0.2.15.41726: Flags [P.], seq 527229:527379, ack 3901181551, win 65535, length 150
> # ...
> ```
> 
> - Time since first packet in capture:
> 
> ```bash
> sudo tcpdump -i enp0s3 -nn -c 3 -ttttt tcp
> ```
> 
> ```bash
> # ...
>  00:00:00.000000 IP 10.0.2.15.41726 > 38.46.226.33.443: Flags [P.], seq 3901205537:3901205671, ack 554079, win 65535, length 134
>  00:00:00.000209 IP 38.46.226.33.443 > 10.0.2.15.41726: Flags [.], ack 134, win 65535, length 0
>  00:00:00.018707 IP 38.46.226.33.443 > 10.0.2.15.41726: Flags [P.], seq 1:151, ack 134, win 65535, length 150
> # ...
> ```

## Writing and reading PCAP files

- Write captured packets to a file (raw bytes):

```bash
sudo tcpdump -i ens3 -w /tmp/capture.pcap
```

- Capture with no name resolution to a timestamped file:

```bash
sudo tcpdump -i ens3 -nn -s 0 -w /tmp/capture_$(date +%Y%m%d_%H%M%S).pcap
```

- Read a capture file and display its contents:

```bash
sudo tcpdump -r /tmp/capture.pcap
```

- Read with filters applied:

```bash
sudo tcpdump -r /tmp/capture.pcap -nn host 10.10.14.1
```

>[!note] You can filter output from `.pcap` files using standard BPF expressions, just like during live capture. 

For long-running captures, you can rotate files by size or time to avoid single massive files:

- Rotate every 100MB:

```bash
sudo tcpdump -i ens3 -w /tmp/capture_%Y%m%d_%H%M%S.pcap -C 100
```

- Rotate every 60 seconds, keeping a maximum of 10 files (oldest overwritten):

```bash
sudo tcpdump -i ens3 -w /tmp/capture_%Y%m%d_%H%M%S.pcap -G 60 -W 10
```

- Read from a list of `.pcap` files:

```bash
sudo tcpdump -V /tmp/file_list.txt
```

| Option         | Description                                                 |
| -------------- | ----------------------------------------------------------- |
| `-w <file>`    | Write raw packets to file.                                  |
| `-r <file>`    | Read from a `.pcap` file.                                   |
| `-V <file>`    | Read a list of `.pcap` filenames.                           |
| `-C <size_MB>` | Rotate output file at `N` megabytes.                        |
| `-G <seconds>` | Rotate output file every `N` seconds.                       |
| `-W <count>`   | Maximum number of rotation files.                           |
| `-z <command>` | Run a command after each file rotation (e.g., compress it). |

## Understanding tcpdump output

- Consider the following TCP packet capture output:

```bash
sudo tcpdump -i ens3 -c 1 -nn -X
```

```bash
# ...
06:08:50.884590 IP 94.237.122.195.80 > 94.237.50.147.38372: Flags [P.], seq 156420061:156420270, ack 1143135829, win 380, options [nop,nop,TS val 2165898869 ecr 2037869077], length 209: HTTP
	0x0000:  4500 0105 26d8 4000 4006 a7ea 5eed 7ac3  E...&.@.@...^.z.
	0x0010:  5eed 3293 0050 95e4 0952 c7dd 4422 de55  ^.2..P...R..D".U
	0x0020:  8018 017c 6c28 0000 0101 080a 8118 fe75  ...|l(.........u
	0x0030:  7977 6a15 827e 00cd f800 0000 8000 0001  ywj..~..........
	0x0040:  0101 0000 ffff 01a0 006d 0010 0019 0000  .........m......
	0x0050:  0007 6001 2ccc cccc 141d 2b15 1d2b 2571  ..`.,.....+..+%q
	0x0060:  0c97 eb06 6350 2914 281f 67d6 0193 a71d  ....cP).(.g.....
	0x0070:  201e 2b14 1d2a 2c80 099a e40b 503b 2a16  ..+..*,.....P;*.
	0x0080:  301c 72de 0187 8c22 181d 2b5c 9d06 9bd7  0.r...."..+\....
	0x0090:  103d 2b2b 9fed 0377 7026 9ee9 0a50 382b  .=++...wp&...P8+
	0x00a0:  94de 018f 9f1e 1e1e 2b2e 5e10 90e9 075d  ........+.^....]
	0x00b0:  4b2a 141f 254e b702 99bc 1829 202b 184b  K*..%N.....).+.K
	0x00c0:  1487 ea04 7266 2714 1e28 41a4 049c d312  ....rf'..(A.....
	0x00d0:  3928 2b16 3c18 7de5 0183 8523 12a2 7e99  9(+.<.}....#..~.
	0x00e0:  859e c747 cb30 52ea 0400 0000 00ff ff00  ...G.0R.........
	0x00f0:  0000 0000 0000 00ff ffff 20f8 0000 0080  ................
	0x0100:  0000 0101 01                             .....
1 packet captured
20 packets received by filter
0 packets dropped by kernel
```


- At the beginning of each packet, there is a **summary line**:

| Field                     | Description                                                                                                                                                       | Example                                                                                 |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Timestamp                 | Timestamp (local system clock) when the packet was captured.<br>Format: `HH:MM:SS.microseconds`.                                                                  | `06:08:50.884590`                                                                       |
| Network protocol          | Network-layer protocol of the received packet (e.g., `IP` indicates IPv4, `IPv6` indicates IPv6).                                                                 | `IP`                                                                                    |
| Source address            | Source address and port number.<br>Format: `source_IP.source_port`.                                                                                               | `94.237.122.195.80`                                                                     |
| Destination address       | Destination address and port number.<br>Format: `destination_IP.destination_port`.                                                                                | `94.237.50.147.38372`<br>`38372` is an **ephemeral client port**.                       |
| TCP flags                 | TCP control bits (inside brackets).                                                                                                                               | `Flags [P.]`<br>`P`  = `PSH` (Push)<br>`.`  = `ACK`                                     |
| Sequence numbers          | TCP sequence numbers (represent positions in the TCP byte stream).<br>Format: `seq start_byte:end_byte`.<br>`end_byte` - `start_byte` = packet length (in bytes). | `seq 156420061:156420270`                                                               |
| Acknowledgment numbers    | TCP acknowledgement numbers; indicate the next expected byte from the client.                                                                                     | `ack 1143135829`                                                                        |
| Windows size              | TCP receive window; how many more bytes the receiver can currently accept.                                                                                        | `win 380`                                                                               |
| TCP options               | TCP header options.                                                                                                                                               | `options [nop,nop,TS val 2165898869 ecr 2037869077]`                                    |
| Payload length            | The size of TCP payload, in bytes (application data; without Ethernet, IP, and TCP headers).                                                                      | `length 209`                                                                            |
| Protocol identification   | How `tcpdump` recognizes the payload (e.g., `HTTP` because of TCP poty `80`).                                                                                     | `: HTTP`                                                                                |
| Hex dump                  | Raw packet bytes in hex and ASCII (`-X` option).                                                                                                                  | `0x0000:  4500 0105 26d8 4000 4006 a7ea ...`                                            |
| Kernel capture statistics | `captured` = Packets printed by `tcpdump`.<br>`received by filter` = Packets matched BPF filter.<br>`dropped` = Packets dropped due to buffer overflow.           | `1 packet captured`<br>`20 packets received by filter`<br>`0 packets dropped by kernel` |

>[!note]+ 
>In the hex dump, `4500` means **IP header**: `45` = IPv4 + header length `5` (`20` bytes); `00` = DSCP/ECN; `0105` is the total IP packet length (261 bytes).


>[!interesting]+ TCP sequence numbers: relative and absolute
> 
> - **Absolute Sequence Numbers** are the actual 32-bit values used in the TCP header to represent the byte offset in the data stream. 
> 	- Each side of a TCP connection initializes a random **Initial Sequence Number (ISN)** during the 3-way handshake for security and uniqueness.
> 	- These ISNs are **large, random** numbers (e.g., `1,234,567,000`). Because how bulky they are, they make raw packet analysis more difficult for humans.
> 
> - **Relative Sequence Numbers** are a user-friendly display feature used by tools like Wireshark and `tcpdump`.
> 	- Wireshark/`tcpdump` subtracts the ISN from every packet's absolute sequence number in a conversation, so the sequence starts at **`0` or `1`** for readability. 
> 	- This normalization makes it easier to follow the flow of data, track byte counts, and compare packets across directions (e.g., client to server and server to client).

## Packet filtering — BPF expressions

**BPF filters** are Boolean expressions evaluated in the kernel. Packets that don't match are dropped before reaching `tcpdump`'s userspace process — this is why filtering at capture time is far more efficient than capturing everything and grepping the output.

- General structure:

```
tcpdump [options] [filter expression]
```

- Where `[filter expression]` is composed of:

```
[protocol] [direction] [type] value
```

>[!example]+
> ```bash
> tcp src port 443
> ```
> - `protocol` = TCP
> - `direction` = source
> - `type` = port
> - `value` = `80`

- If qualifiers are omitted:
	- Type defaults to `host`.`
	- Direction defaults to `src or dst`.
	- Protocol defaults to all protocols.

>[!example]+
> ```bash
> tcpdump -i eth0 host 192.168.1.10 and port 443
> ```

### Host filtering 

- Match all traffic to or from a specific IP address (bidirectional):

```bash
sudo tcpdump -i ens3 host 192.168.1.11
```

- Match only traffic **originating from** an IP address:

```bash
sudo tcpdump -i ens3 src host 192.168.1.11
```

- Match only traffic **destined for** an IP address:

```bash
sudo tcpdump -i ens3 dst host 192.168.1.11
```

- Filter by MAC address (useful when IP addresses are behind NAT or spoofed):

```bash
sudo tcpdump -i ens3 ether host aa:bb:cc:dd:ee:ff
```

- Filter by source MAC address:

```bash
sudo tcpdump -i ens3 ether src aa:bb:cc:dd:ee:ff
```

| Expression                 | Description                                                                             |
| -------------------------- | --------------------------------------------------------------------------------------- |
| `host <ip_address>`        | Match packets where the **source or destination IP address** equals the specified host. |
| `src host <ip_address>`    | Match packets with the specified **source IP address**.                                 |
| `dst host <ip_address>`    | Match packets with the specified **destination IP address**.                            |
| `ip host <ip_address>`     | Match **IPv4 packets** with the specified source or destination IP address.             |
| `ether host <mac_address>` | Match packets with the specified **Ethernet source or destination MAC address**.        |
| `ether src <mac_address>`  | Match packets with the specified **source MAC address** (Ethernet).                     |
| `ether dst <mac_address>`  | Match packets with the specified **destination MAC address** (Ethernet).                |

You can also filter by subnets, using network prefixes:

- Capture all traffic to or from a subnet:

```bash
sudo tcpdump -i ens3 net 10.10.10.0/24
```

- Capture traffic **sourced from** a subnet (e.g., internal hosts reaching out):

```bash
sudo tcpdump -i ens3 src net 192.168.0.0/16
```

- Capture traffic between two specific networks:

```bash
sudo tcpdump -i ens3 src net 10.0.0.0/8 and dst net 172.16.0.0/12
```
### Port filtering

- Match traffic on a specific port (bidirectional):

```bash
sudo tcpdump -i ens3 port 443
```

- Match traffic **to** a port (e.g., inbound web requests):

```bash
sudo tcpdump -i ens3 dst port 80
```

- Match traffic **from** a port (e.g., server responses):

```bash
sudo tcpdump -i ens3 src port 22
```

- Capture a range of ports — useful for catching services on non-standard high ports:

```bash
sudo tcpdump -i ens3 portrange 8000-9000
```

- Source port range only:

```bash
sudo tcpdump -i ens3 src portrange 1024-65535
```

| Expression                    | Description                                                                                  |
| ----------------------------- | -------------------------------------------------------------------------------------------- |
| `port <port>`                 | Match packets where the **source or destination port** equals the specified port.            |
| `src port <port>`             | Match packets where the **source port** equials the specified port.                          |
| `dst port <port>`             | Match packets where the **destination port** equals the specified port.                      |
| `portrange <start>-<end>`     | Match packets where the **source or destination port** falls within the specified **range**. |
| `src portrange <start>-<end>` | Match packets where the **source port** falls within the specified **range**.                |
| `dst portrange <start>-<end>` | Match packets where the **destination port** falls within the specified **range**.           |

### Protocol filtering

You can filter protocols using keywords:

- Capture only TCP traffic:

```bash
sudo tcpdump -i ens3 tcp
```

- Capture only UDP traffic: 

```bash
sudo tcpdump -i ens3 udp
```

- Capture ICMP traffic:

```bash
sudo tcpdump -i ens3 icmp
```

- Capture ARP traffic:

```bash
sudo tcpdump -i ens3 arp
```

- Capture IPv6 traffic:

```bash
sudo tcpdump -i ens3 ip6
```

| Expression | Description            |
| ---------- | ---------------------- |
| `tcp`      | Match TCP packets.     |
| `udp`      | Match UDP packets.     |
| `icmp`     | Match ICMP packets.    |
| `arp`      | Match ARP packets.     |
| `ip`       | Match IPv4 packets.    |
| `ip6`      | Match IPv6 packets.    |
| `ether`    | Match Ethernet frames. |

### Packet length filtering

Sometimes you want to filter by size, such as to see only actual data transfers and remove tiny keep-alive and `ACK` packets, or only match scanning probes.

- Only capture packets smaller than 64 bytes (likely scanning or keep-alive packets):

```bash
sudo tcpdump -i ens3 less 64
```

- Only capture packets larger than 1000 bytes (likely data transfer):

```bash
sudo tcpdump -i ens3 greater 1000
```

- You can also use C-style operators:

```bash
sudo tcpdump -i ens3 'len > 1000'
```

| Expression                       | Description                                               |
| -------------------------------- | --------------------------------------------------------- |
| `less <size>` /<br>`< <size>`    | Match packets smaller than the specified number of bytes. |
| `greater <size>` /<br>`> <size>` | Match packets larger than the specified number of bytes.  |
### Logical operators 

Filters can be combined with `and`, `or`, and `not` (or their C-style equivalents `&&`, `||`, `!`).

- HTTP or HTTPS traffic:

```bash
sudo tcpdump -i ens3 port 80 or port 443
```

- HTTP traffic to or from a specific host:

```bash
sudo tcpdump -i ens3 tcp port 80 and host 10.10.14.5
```

- Match all traffic **except** SSH (reduce noise when you're connected over SSH):

```bash
sudo tcpdump -i ens3 not port 22
```

- Match all traffic **except** DNS and ARP:

```bash
sudo tcpdump -i ens3 not port 53 and not arp
```

- Match traffic between two specific hosts:

```bash
sudo tcpdump -i ens3 host 10.10.10.5 and host 10.10.10.10
```

>[!tip] `and` takes precedence over `or`, and `not` takes precedence over `or`.
>- So `tcp and port 80 or port 443` is parsed as `(tcp and port 80) or (port 443)` — which is probably not what you want. Use parentheses to group expressions: `tcp and (port 80 or port 443)`.

- Logical operators and grouping with parentheses:

```bash
sudo tcpdump -i ens3 'tcp and (port 80 or port 443)'
```

| Expression         | Description                                 |
| ------------------ | ------------------------------------------- |
| `and` /<br>`&&`    | Require both filter conditions to be true.  |
| `or` /<br>`\|\|`   | Require either filter condition to be true. |
| `not` /<br>`!`<br> | Exclude packets matching the expression.    |
| `()`               | Group expressions to chance precedence.     |

### VLAN filtering

802.1Q VLAN tags add 4 bytes to the Ethernet header. `tcpdump` can filter on them, too:

- Capture traffic that belongs to the VLAN `20`:

```bash
tcpdump vlan 20
```

| Expression  | Description                                                           |
| ----------- | --------------------------------------------------------------------- |
| `vlan`      | Match packets that contain a VLAN tag (that one in Ethernet headers). |
| `vlan <id>` | Match packets belonging to the specified VLAN.                        |

### IP protocol number filtering


The `Protocol` field in the IPv4 header and the `Next Header` field in the IPv6 header identify the encapsulated transport protocol using am **IP protocol number**.

- Capture IPsec ESP traffic (protocol number `50`):

```bash
sudo tcpdump -i ens3 ip proto 50
```


- Capture GRE tunnels (protocol `47`):

```bash
sudo tcpdump -i ens3 ip proto 47
```

- Most common IP protocol numbers:

| Protocol    | Number |
| ----------- | ------ |
| ICMP        | `1`    |
| TCP         | `6`    |
| UDP         | `17`   |
| GRE         | `47`   |
| ESP (IPsec) | `50`   |
| AH (IPsec)  | `51`   |
| EIGRP       | `88`   |
| OSPF        | `89`   |
| SCTP        | `132`  |
>[!note] See [`List of IP protocol numbers — Wikipedia`](https://en.wikipedia.org/wiki/List_of_IP_protocol_numbers) for the full list.

### Byte-level filtering

This is what comes especially useful for security work. BPF allows you to inspect arbitrary bytes within protocol headers using the syntax `proto[offset:size]`, where:

- `proto` is the protocol layer (`tcp`, `udp`, `ip`, `icmp`, `ether`)
- `offset` is the byte offset from the start of that header
- `size` is the number of bytes to read (`1`, `2`, or `4`)

You then compare the result against a value, often using bitwise `AND` (`&`) to test individual bits.

#### TCP flag filtering

- Capture all packets with `SYN` set (e.g., `SYN` and `SYN`-`ACK` used in three-way handshake):

```bash
sudo tcpdump -i ens3 'tcp[tcpflags] & tcp-syn != 0'
```

- Capture packets with **`SYN` flag only** packets (e.g., `SYN` is set, `ACK` is not — only connection initiations):

```bash
sudo tcpdump -i ens3 'tcp[tcpflags] == tcp-syn'
```

- Capture `RST` packets:

```bash
sudo tcpdump -i ens3 'tcp[tcpflags] & tcp-rst != 0'
```

- Capture the Xmas scan pattern (`FIN` + `PSH` + `URG` flags all set):

```bash
sudo tcpdump -i ens3 'tcp[13] == 0x29'
```

> [!note] `0x29 = 0x01 (FIN) | 0x08 (PSH) | 0x20 (URG)` — a Xmas scan fingerprint from `nmap -sX`.

- Capture `NULL` scan packets (no flags set at all):

```bash
sudo tcpdump -i ens3 'tcp[13] == 0'
```

>[!note] TCP flags are at byte offset `13` in the TCP header. This is where this `tcp[13]` comes from.

- Here are TCP flags, for a reference:

| Flag  | Bit position | Mask   |
| ----- | ------------ | ------ |
| `FIN` | `0`          | `0x01` |
| `SYN` | `1`          | `0x02` |
| `RST` | `2`          | `0x04` |
| `PSH` | `3`          | `0x08` |
| `ACK` | `4`          | `0x10` |
| `URG` | `5`          | `0x20` |

>[!tip]+
> To locate a **TCP three-way handshake**, look for the sequence:
> 
> 1. `SYN`         -> `Flags [S]`  
> 2. `SYN`-`ACK`  -> `Flags [S.]`
> 3. `ACK`         -> `Flags [.]
#### ICMP type filtering

>[!note] ICMP type is stored at byte offset `0` of the ICMP header.

- Capture only ICMP `Echo Requests` (ping):

```bash
sudo tcpdump -i ens3 'icmp[0] == 8'
```

- Capture only ICMP `Echo Replies`:

```bash
sudo tcpdump -i ens3 'icmp[0] == 0'
```

- Capture `ICMP Destination Unreachable` (type `3`) — helpful for mapping filtered ports:

```bash
sudo tcpdump -i ens3 'icmp[0] == 3'
```

| ICMP Type                 | Value | Meaning                    |
| ------------------------- | ----- | -------------------------- |
| `Echo Reply`              | `0`   | Ping reply.                |
| `Destination Unreachable` | `3`   | Host/port/net unreachable. |
| `Echo Request`            | `8`   | Ping request.              |
| `Time Exceeded`           | `11`  | TTL expired (traceroute).  |
#### IP header filtering

- Capture only traffic with TTL less than 5 (could indicate a `traceroute` in progress, or a routing loop):

```bash
sudo tcpdump -i ens3 'ip[8] < 5'
```

> [!note] TTL (Time-to-Live) is at byte offset `8` in the IPv4 header. 
> - Each router hop decrements TTL by `1`. 
> - Packets with very low TTL near your host are likely near the end of their path — or from a tool that sets low TTL values intentionally, like `tracerouting`.

- Capture fragmented IP packets (often used in evasion):

```bash
sudo tcpdump -i ens3 '(ip[6:2] & 0x1fff) != 0'
```

> [!note] The IP fragment offset field occupies the lower 13 bits of the byte-6/7 word in the IP header. A non-zero fragment offset means this is not the first fragment. Fragmented traffic can be used to bypass some IDS/IPS systems that don't reassemble fragments.


## Option quick reference

- Interfaces:

| Option              | Description                                           |
| ------------------- | ----------------------------------------------------- |
| `-i <interface>`    | Capture packets from the specified network interface. |
| `-D`                | List available network interfaces for packet capture. |
| `-I`                | Enable monitor mode on supported wireless interfaces. |
| `-y <datalinktype>` | Set the data link type for packet capture.            |


- Capture control:

| Option              | Description                                                     |
| ------------------- | --------------------------------------------------------------- |
| `-c <count>`        | Stop capturing after receiving the specified number of packets. |
| `--count`           | Print the packet number for each packet captured.               |
| `--skip <count>`    | Skip the specified number of packets before processing.         |
| `--immediate-mode`  | Capture packets immediately instead of buffering them.          |
| `-s <snaplen>`      | Capture only the specified number of bytes from each packet.    |
| `-B <buffer_size>`  | Set the operating system capture buffer size.                   |
| `-p`                | Disable promiscuous mode on the interface.                      |
| `-Q in\|out\|inout` | Select packets based on capture direction.                      |
| `-U`                | Flush packet output buffer after each packet.                   |
| `--lengths`         | Print packet lengths for captured packets.                      |

- Working with PCAP files:

| Option                    | Description                                                       |
| ------------------------- | ----------------------------------------------------------------- |
| `-r <file>`               | Read packets from the specified capture file.                     |
| `-V <file>`               | Read a list of capture file names from the specified file.        |
| `-w <file>`               | Write raw packets to the specified file instead of printing them. |
| `-C <file_size>`          | Rotate the output file when it reaches the specified size.        |
| `-G <rotate_seconds>`     | Rotate the output file after the specified number of seconds.     |
| `-W <filecount>`          | Limit the number of rotated output files.                         |
| `-z <postrotate-command>` | Execute a command after rotating capture files.                   |

- Packet output formatting:

| Option | Description                                                         |
| ------ | ------------------------------------------------------------------- |
| `-A`   | Print packet contents in ASCII format.                              |
| `-x`   | Print packet contents in hexadecimal format.                        |
| `-X`   | Print packet contents in both hexadecimal and ASCII formats.        |
| `-XX`  | Print packet contents including link-layer header in hex and ASCII. |
| `-e`   | Print the link-layer header for each packet.                        |
| `-q`   | Print less protocol information for each packet.                    |
| `-v`   | Increase verbosity of packet output.                                |
| `-vv`  | Increase verbosity further.                                         |
| `-vvv` | Print maximum verbosity information.                                |

- Name resolution control:

| Option | Description                                   |
| ------ | --------------------------------------------- |
| `-n`   | Disable hostname resolution.                  |
| `-nn`  | Disable hostname and port name resolution.    |
| `-N`   | Remove domain qualification from host names.  |
| `-f`   | Print foreign internet addresses numerically. |


- Timestamp control:

|Option|Description|
|---|---|
|`-t`|Disable timestamp printing.|
|`-tt`|Print timestamps as seconds since epoch.|
|`-ttt`|Print time difference between packets.|
|`-tttt`|Print timestamps with full date and time.|
|`-ttttt`|Print time difference from the first packet.|
|`--time-stamp-precision=<precision>`|Set timestamp precision.|
|`--micro`|Use microsecond timestamp precision.|
|`--nano`|Use nanosecond timestamp precision.|
|`-j <tstamp_type>`|Select packet timestamp type.|

- Filter and expression input:

|Option|Description|
|---|---|
|`-F <file>`|Read filter expression from the specified file.|
- Protocol decoding control:

|Option|Description|
|---|---|
|`-T <type>`|Force packet decoding as the specified protocol type.|
|`-m <module>`|Load an additional protocol decoding module.|


## References and further reading

-  [`tcpdump(1) man pages — tcpdump.org`](https://www.tcpdump.org/manpages/tcpdump.1.html)
- [`List of IP protocol numbers — Wikipedia`](https://en.wikipedia.org/wiki/List_of_IP_protocol_numbers)