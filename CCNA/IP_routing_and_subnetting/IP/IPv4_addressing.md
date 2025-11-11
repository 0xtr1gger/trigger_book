---
created: 2025-09-26 05:51:20
tags:
  - IP
  - routing
---
## IPv4 addresses

>IPv4 addresses are **`32` bits long**, divided into four **octets** (`8` bits each). 

>[!important]+ DDN
>Most commonly, IPv4 addresses are represented in **Dotted Decimal Notation (DDN)**, where each octet is a decimal number from `0` to `255` (`00000000` to `11111111` in binary), and octets are separated by dots. For example, `192.168.1.1`.

>[!note]+ 4.3 billion addresses
>The total IPv4 address space is $2^{32}$ or about 4.3 billion unique addresses.

Each IPv4 address consists of two parts:

- **Network address**, **network prefix**, **routing prefix**, or **network ID**
    - Uniquely identifies the network.

- **Host address**, or **host**/**interface identifier**
    - Uniquely identifies the specific host within the network.

## IPv4 address classes

IPv4 addresses are traditionally divided into **5 classes** (A, B, C, D, E) based on the **first octet of the address**:

| Class |             Range             | Subnet mask | First octet |     Purpose      |   Addresses per network   | Networks              | Leading bits |
| :---: | :---------------------------: | :---------: | :---------: | :--------------: | :-----------------------: | --------------------- | ------------ |
|   A   |  `0.0.0.0`-`127.255.255.255`  |    `/8`     |  `0`-`127`  | Host addressing  | `16,777,216` ($2^{24}-2$) | `128` ($2^{7})        | `0`          |
|   B   | `128.0.0.0`-`191.255.255.255` |    `/16`    | `128`-`191` | Host addressing  |   `65,536` ($2^{16}-2$)   | `16,384` ($2^{14}-2$) | `10`         |
|   C   | `192.0.0.0`-`223.255.255.25`  |    `/24`    | `192`-`223` | Host addressing  |     `256` ($2^{8}-2$)     | `2,097,152` ($2^21$)  | `110`        |
|   D   | `224.0.0.0`-`239.255.255.255` |      -      | `224`-`239` |    Multicast     |            N/A            | N/A                   | `1110`       |
|   E   | `240.0.0.0`-`255.255.255.255` |      -      | `240`-`255` | Experimental use |            N/A            | N/A                   | `1111`       |

>[!note]+ Problems of the classful addressing 
> The classful network architecture was introduced in 1981 as a part of the specification of the Internet Protocol (IP), back at the beginnings of the Internet.
> 
> IP addresses from the first three classes (**A**, **B** and **C**) were meant to be used for *host addresses*, while **D** was dedicated for *multicast addresses*, and **E** for *experimental use*.
> 
> This classful division isn't really used in modern networks, but it's crucial to understand them for the exam.

Starting in 1993, classful networking was replaced by **Classless Inter-Domain Routing (CIDR)**.

See [[IPv4_subnetting#CIDR and subnet masks]]

## Private IPv4 address ranges

>**Private IP addresses** are reserved for use within private networks (home, office, enterprise LANs) and **cannot be routed on the public internet**.

>[!note]
>Unlike public IP addresses, private address are **not globally unique**; the same address can be used in different networks at the same time.

Private IP addresses are defined in [`RFC 1918`](https://datatracker.ietf.org/doc/html/rfc1918). These are three private IP address ranges:

| Class | CIDR notation    | Range                           | `#`      | Address         |
| ----- | ---------------- | ------------------------------- | -------- | --------------- |
| A     | `10.0.0.0/8`     | `10.0.0.0`-`10.255.255.255`     | `16.78M` | `10.x.x.x`      |
| B     | `172.16.0.0/12`  | `172.16.0.0`-`172.31.255.255`   | `1.05M`  | `172.16-31.x.x` |
| C     | `192.168.0.0/16` | `192.168.0.0`-`192.168.255.255` | `65.5K`  | `192.168.x.x`   |

>[!important] Loopback addresses
>There are also a range **loopback addresses**, `127.0.0.0/8` (`127.0.0.0`-`127.255.255.255`). Loopback addresses are used to test the network stack on the **local device**.
>If a device sends a packet to an address in this range, the packet is processed back up the TCP/IP stack as if it's a packet received from another device.

## Multicast IPv4 addresses

>**Multicast addresses** allow one-to-many communication where one source sends packets to multiple interested receivers.

>[!note]
> - Unlike broadcast (which targets all devices on a subnet), multicast targets a specific group of devices that have joined a multicast group.
> - Multicast is used in streaming media, conferencing, and routing protocols.

>[!important] The multicast address space is defined as **`224.0.0.0`-`239.255.255.255`** (Class D).

| Address      | Description                                                                     |
| ------------ | ------------------------------------------------------------------------------- |
| `224.0.0.1`  | **All hosts** on the local subnet. <br>All multicast-capable hosts listen here. |
| `224.0.0.2`  | **All routers** on the local subnet. <br>Used by routing protocols.             |
| `224.0.0.5`  | **OSPFv2**: **All SPF routers** multicast address.                              |
| `224.0.0.6`  | **OSPFv2**: **All Designated Routers** multicast address.                       |
| `224.0.0.9`  | **RIPv2**: **All routers** multicast address.                                   |
| `224.0.0.13` | **PIM (Protocol Independent Multicast)** routers multicast address.             |
| `224.0.0.18` | **VRRP** (Virtual Router Redundancy Protocol) routers multicast address.        |
| `224.0.1.1`  | **NTP** multicast address.                                                      |

---

| Address Range                     | Description                                                                                                                                               |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`224.0.0.0`-`224.0.0.255`**     | _Link-Local Multicast_ (Local Network Control Block). Used by network protocols on local subnet only; **not forwarded by routers**. `TTL=1`.              |
| **`224.0.1.0`-`238.255.255.255`** | _Globally Scoped Multicast Addresses_. <br>Used for multicast applications across subnets and the internet. These addresses are **forwarded by routers**. |
| **`232.0.0.0`-`232.255.255.255`** | _Source-Specific Multicast (SSM)_ range. Used for one-to-many multicast with known sources.                                                               |
| **`233.0.0.0`-`233.255.255.255`** | _GLOP addressing_ range. Used for multicast addressing based on autonomous system numbers (ASNs).                                                         |
| **`239.0.0.0`-`239.255.255.255`** | _Administratively Scoped_ (Private) multicast addresses. Used within organizations, not routed on the internet.                                           |

## Configuration
### Show interfaces

- To confirm the status of each interface on a device and display its IP address:

```toml
R1# show ip interface brief
```

![[show_ip_interface_brief.png]]

- To display more detailed information about interfaces:

```toml
R1# show interfaces 

# or, for a specific interface:
R1# show interfaces g0/0
```

![[show_interfaces.png]]

>[!note]+ `administratively down`
>The default `Status` of interfaces on Cisco **routers** is `administratively down`. 
>But **not** on switches.
### Configuring IP addresses

To configure an IP address on a router interface:

1. Enter interface configuration mode:

```toml
R1(config)# interface gigabitethernet 0/0
R1(config-if)#
```

2. Set an IP address:

```toml
R1(config-if)# ip address IP_ADDRESS SUBNET_MASK

# for example:
R1(config-if)# ip address 172.16.255.254 255.255.0.0
```

3. Turn the interface on:

```toml
R1(config-if)# no shutdown
```

>[!example]+ Example: configuring IP address
> ```toml
> R1(config)# interface g0/0   
> R1(config-if)# ip address 15.255.255.254 255.0.0.0
> R1(config-if)# no shutdown
> 
> R1(config-if)# interface g0/1
> R1(config-if)# ip address 182.98.255.254 255.255.0.0
> R1(config-if)# no shutdown
> 
> R1(config-if)# interface g0/2
> R1(config-if)# ip address 201.191.20.254 255.255.255.0
> R1(config-if)# no shutdown
> 
> R1(config-if)# do show ip interface brief
> Interface              IP-Address      OK? Method Status                Protocol 
> GigabitEthernet0/0     15.255.255.254  YES manual up                    up 
> GigabitEthernet0/1     182.98.255.254  YES manual up                    up 
> GigabitEthernet0/2     201.191.20.254  YES manual up                    up 
> Vlan1                  unassigned      YES unset  administratively down down
> ```
>![[configuring_IP_address.png]]

To add an interface description:

1. Enter interface configuration mode:

```toml
R1(config)# interface gigabitethernet 0/0
R1(config-if)#
```

2. Configure the description:

```toml
R1(config-if)# description INTERFACE DESCRIPTION GOES HERE
```

