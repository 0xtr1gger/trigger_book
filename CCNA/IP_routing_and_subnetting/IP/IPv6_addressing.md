---
created: 2025-09-26 05:56:21
tags:
  - IP
  - routing
---
## IPv6 addresses

>**IPv6 (Internet Protocol version 6)** is the latest version of the Internet Protocol, designed to replace IPv4 and address the issue of address exhaustion.

>[!important] IPv6 addresses are of **`128` bits** long, or `32` hexadecimal digits (one hex number takes up `4` bits).

>[!important] IPv6 addresses consist of 8 colon-separated groups by 4 hexadecimal digits, with each such group known as a **hextet** or **hexadectet**. 
>- Each hextet is `16` in size.
>For example:
> ```
> 2345:1111:2222:3333:4444:5555:6666:AAAA
> ```

The IPv6 address space consists of $$3.40282367\times10^{38}$$ addresses. This is $7.92281625\times10^{28}$ times larger than the address space of IPv4: there are *340 undecilions* IPv6 addresses.  


>[!important] IPv6 does not reserve the last address in a subnet for the broadcast address, since **IPv6 does not use broadcasts**.
### Updates brought by IPv6

In IPv6, the following improvements over IPv4 were made:

- **New header format**
	- Non-essential fields were removed to make routing more efficient.

- **Larger address space**
- **Better security**
	- IPSec is built-in and part of the IPv6 protocol.  IPv6 has header extensions that ease the implementation of encryption and authentication.
- **Extensibility**
- **Stateless and Stateful host addressing (SLAAC)**
	- In the absence of a DHCP server, hosts in a LAN can generate IP addresses themselves and start communication over the local network immediately.
- **Multiple IPv6 addresses per device** 
	- Hosts can have multiple IPv6 addresses on the same subnet. This allows for improved security, greater privacy, and creates the possibility for additional network features.
- **New address types** 
	- New network layer address types were included in the IPv6 suite such as non-routable IPv6 link-local addresses.

Replaced protocols:

- OSPFv2 has been updated to OSPFv3 to support IPv6.
- ICMPv6 instead of ICMP.
- Neighbor Discovery Protocol (NDP) in place of ARP: multicast instead of broadcast.

## IPv6 address abbreviation

There are two main ways to abbreviate IPv6 addresses:
- Omit leading zeroes in each hextet
- Use `::` to denote a series of consecutive zeroes

> [!important]+ Omit leading zeroes in each hextet
> - In any hextet, leading zeroes can be omitted. 
> - The rule applies only to leading zeroes, not trailing.
> 
> ```
> 3300:0001:0002:0003:0004:0005:0006:0007
> =>
> 3300:1:2:3:4:5:6:7
> ```

>[!important]+ Using `::` to denote a series of consecutive zeroes
> - A sequence of consecutive hextets of zeroes can be omitted with `::` notation.
> - **Only one** sequence of zeroes can be denoted with `::` in a single address. 
> - If there are other all-zero quartets in the address except the omitted ones, these can be abbreviated with one `0` per quartet instead of two: `0000` => `0`
> 	
> ```
> 2041:0000:140F:0000:0000:0000:875B:131B
> =>
> 2041:0000:140F::875B:131B
> =>
> 2041:0:140F::875B:131B
> ```  

>[!note]
> [RFC 5952](https://datatracker.ietf.org/doc/html/rfc5952) suggests a standard IPv6 address representation:
> - Leading zeroes must be removed
> - `::` must be used to shorten the longest string of all-0 quartets.
> 	- If there is only one all-0 quartet, don't use `::`.
> 	- If there are two equal-length choices for the `::`, use `::` to shorted the one on the left.
> - Hexadecimal characters `a`, `b`, `c`, `d`, and `f` must be written using lower-case, not upper-case `A`, `B`, `C`, `D`, `F`.

## Types of IPv6 addresses

There are three main types of IPv6 addresses:

- **Unicast**
	- Identifies one network interface; used for one-to-one communication.

- **Multicast**
	- Identifies a set of interfaces that belong to a multicast group; used for one-to-many communication.

- **Anycast**
	- Identifies a set of interfaces; packets destined to an anycast address are delivered to a **single closest interface identified by that anycast address**. 
	- Used for one-to-closest communication.
	- Anycast addresses are allocated from the unicast address space, therefore they are **indistinguishable from global unicast addresses**.

>[!important] IPv6 does not implement broadcast addressing.

Summary of IPv6 address types:

- **Unicast addresses**
    - Global Unicast addresses
    - Unique Local addresses
    - Link Local Addresses
- **Multicast addresses**
    - Solicited-mode multicast addresses
- **Anycast addresses**
- **Loopback addresses**
- **Unspecified**
## Unicast addresses

Unicast addresses can be:
- **Global unicast addresses**
- **Unique local addresses**
- **Link local addresses**

>[!important]+ Not routable address ranges:
>- `FE80::/10` (link-local)
>- `FF02::16` (link-local multicast)

### Global unicast addresses

>IPv6 **global unicast addresses**, aka **aggregatable global unicast addresses**, are public, *globally unique* addresses used to identify network devices in the IPv6 network, such as the Internet.

>[!note] Global unicast IPv6 addresses are analogous to public IPv4 addresses: they are globally unique and must be registered before use.

>[!important]
>The block of IPv6 addresses originally defined for public is `2000::/3` (`2000::` to `3fff:ffff:ffff:ffff:ffff:ffff:ffff:ffff`; the first 3 bits are `001`)
>However, now **all addresses** not otherwise reserved for other purposes are global unicast addresses.

Each global unicast IPv6 address consists of two parts: **network prefix** and **host identifier**. A network prefix is made up of a **global routing prefix** and a **subnet identifier**.

>[!important] A **network prefix**, aka **network identifier**, is part of an IPv6 that uniquely identifies the network.
> - An IPv6 network prefix is typically `/64`.
> - A network prefix consists of two parts:    
> 	- **Global routing prefix** — `48` bits
> 	- **Subnet identifier** — `16` bits

![[global_routing_prefix.svg]]

| Part                              | Size (bits) | Usage                                                                                                                                 |
| --------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| **Global routing prefix**         | `48`        | Assigned by the ISP for organization use.<br>Identifies organizations globally.<br>Typically `/64` bits long.                         |
| **Subnet identifier**             | `16`        | Identifies subnets within a global routing prefix address range (i.e., subnets withing an organization).<br>Typically `16` bits long. |
| **Interface, or host identifier** | `64`        | Identifies individual hosts within the network, can be generated using EUI-64.<br>Typically `64` bits long.                           |

### Unique local addresses

>**Unique Local Addresses (ULA)** are intended for communication *within local networks*. These addresses are not expected to be routed on the global Internet.

> [!note]
> - No need for registration.
> - No need to be globally unique.
> - Not globally routable.
> - Can be routed within an organization.
> 

>[!important] Unique local addresses use the `fd00::/8` IPv6 address range (from `fd00::` to `fdff:ffff:ffff:ffff:ffff:ffff:ffff:ffff`).

>[!important] All unique local addresses start with `fd`.

It's recommended to try to make local addresses globally unique by generating pseudo-random global identifier (see below). 

>[!important]
> Each unique local address consists of:
> - **Unique local address identifier** — `8` bits, `fd`
> - **Pseudo-random global identifier** — `40` bits
> - **Subnet identifier** — `16` bits 
> - **Interface identifier** — `64` bits



![[unique_local_addresses.svg]]

| Part                                | Size (bits) | Description                                                         |
| ----------------------------------- | ----------- | ------------------------------------------------------------------- |
| **Unique local address identifier** | `8`         | - `fd`<br>- Identifies that this address is a unique local address. |
| **Global ID (pseudo-random)**       | `40`        | - Identifies these local addresses globally.                        |
| **Subnet ID**                       | `16`        | - Identifies subnets within a network.                              |
### Link local addresses

>A **Link-Local Address** is a type of IPv6 address used for communications within a local link, i.e. the subnet the host is connected to. 

>[!note]
>The idea behind link-local IPv6 addresses is to enable nodes attached to a common link to communicate without the need for globally unique addresses.
>- Unique only on the local network segment.
>- Only valid within a local link.

>[!important]
>- A link-local address is automatically generated on each IPv6-enabled interface with **EUI-64**. 

IPv6 *requires* a link-local address on **every network interface** on which the IPv6 protocol is enabled, even when routable addresses are also assigned. Therefore, each IPv6-enabled interface usually has more than one IPv6 address assigned to it. 

- Link-local IPv6 addresses are required for NDP (Neighbor Discovery Protocol), DHCPv6, and some other IPv6-based protocols, such as duplicate address detection and router advertisement. 

- IPv6 link-local addresses are used for:
	- Routing protocol peering (OSPFv3 uses link-local addresses for neighbor adjacencies)
	- Next-hop addresses for static routes
	- Neighbor Discovery Protocol (NDP, IPv6 replacement for ARP)
	- DHCPv6

>[!important] Link-local addresses use the `fe80::/10`  IPv6 address range (from `fe80::` to `febf:ffff:ffff:ffff:ffff:ffff:ffff:ffff`).
>However, the standard states that the 54 bits after `fe80/10` should be all `0`. This means that link-local addresses actually use the `FE80::/64` address prefix.
>- `10`  most significant bits of a link-local IPv6 address are `1111 1110 10`.

>[!note]
>The difference between *unique local* and *link-local IPv6 addresses* is that link local addresses can only be used in a single network segment, they can't be routed. Unique local addresses can be routed, but only within a local network. 

Link-local addresses can be assigned to end devices in several ways:

- **Manual assignment** 
	- Every node can be configured with an IPv6 address manually by an administrator. It is not a scalable approach and is prone to human error.

- **DHCPv6 (Dynamic Host Configuration Protocol version 6)** 
	- The most widely adopted protocol for dynamically assigning addresses to hosts. Requires a DHCP server on the network and additional configuration.

- **SLAAC (Stateless Address Autoconfiguration)**
	- A method for deriving `64`-bit IPv6 device identifiers based on MAC addresses. 

>**Stateless Address Autoconfiguration (SLAAC)**, defined in [`RFC 4862`](https://tools.ietf.org/search/rfc4862), is a mechanism that allows each host on an IPv6 network to auto-configure a unique address without DHCP or manual configuration.
## Multicast addresses

IPv6 multicast addresses serve the same purpose as in IPv4 — delivering packets to multiple devices at once.

>[!important] IPv6 multicast addresses use the `ff00::/8` IPv6 address range (from `ff00::` to `ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff`).

| Address       | Description                                                       | IPv4 equivalent  |
| ------------- | ----------------------------------------------------------------- | ---------------- |
| `ff02::1`     | All nodes on the local network segment (functions like broadcast) | `224.0.0.1`      |
| `ff02::2`<br> | All routers no the local network segment.                         | `224.0.0.2`      |
| `ff02::5`<br> | All OSPF routers.                                                 | `224.0.0.5`<br>  |
| `ff02::6`<br> | All DR/BDR routers.                                               | `224.0.0.6`<br>  |
| `ff02::9`<br> | All RIP routers.                                                  | `224.0.0.9`<br>  |
| `ff02::A`<br> | All EIGRP routers.                                                | `224.0.0.10`<br> |
| `ff02::1:2`   | All routers acting as DHCPv6 relay agent                          | None             |

>[!note] IPv6 defines multiple multicast scopes which indicate how far the packet should be forwarded.

| Scope                    | IPv6 addresses | Purpose                                                                                                                                                         |
| ------------------------ | -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Interface-local scope    | `ff01::/16`    | Not intended for communication over any network link, must remain within the local device.<br>Can be used to send traffic to a service within the local device. |
| Link-local scope         | `ff02::/16`    | The packets remain the local subnet. Routers will not route the packet between subnets.                                                                         |
| Site-local scope         | `ff05::/16`    | The packets can be forwarded by routers.<br>Should be limited to a single physical location, i.e., not forwarded over a WAN.                                    |
| Organization-local scope | `ff08::/16`    | Restricted to networks used by the organization administering the local network.<br>Wider in scope than site-local (an entire company/organization)             |
| Global scope             | `ff0E::/16`    | No boundaries. Can be routed over the internet.                                                                                                                 |

## EUI-64

> IPv6 **EUI-64 (Extended Unique Identifier)** is a method of converting a MAC address (`48` bits) into a `64`-bit IPv6 interface identifier.

EUI-64 is used in Stateful Address Autoconfiguration (SLAAC) to automatically generate hosts' interface identifiers locally.

EUI-64 works like this:

0. The **MAC address** is taken as it is.
    
1. The **first `24` bits** (`3` bytes) of the MAC address are copied to the first `24` bits of the EUI-64 interface ID.
    
2. After the first `24`-bit portion of the MAC address, the `fffe` hexadecimal value is inserted.
    
3. The **remaining `24` bits** (`3` bytes) of the MAC address are copied to be the last `24` bits of the EUI-64 interface ID right after the `fffe` value.
    
4. The **7th bit is inverted**.

```
0. 1234 5678 90AB
1. 1234 56
2. 1234 56ff fe
3. 1234 56ff fe78 90ab
4. 1034 56ff fe78 90ab
```

> [!example] Examples:
> | MAC address      | EUI-64                |
> | ---------------- | --------------------- |
> | `782b cbac 0867` | `7a2b cbff feac 0867` |
> | `0200 4c4f 4f50` | `0000 4cff fe4f 4f50` |
> | `0050 56c0 0001` | `0250 56ff fec0 0001` |
> | `00ff 6ba6 f456` | `02ff 6Bff fea6 f456` |
> | `96ab 6d6b 98ae` | `94ab 6dff fe6b 98ae` |
> 
## Hexadecimal

| Decimal | Binary | Hexadecimal |
| ------- | ------ | ----------- |
| `0`     | `0000` | `0`         |
| `1`     | `0001` | `1`         |
| `2`     | `0010` | `2`         |
| `3`     | `0011` | `3`         |
| `4`     | `0100` | `4`         |
| `5`     | `0101` | `5`         |
| `6`     | `0110` | `6`         |
| `7`     | `0111` | `7`         |
| `8`     | `1000` | `8`         |
| `9`     | `1001` | `9`         |
| `10`    | `1010` | `A`         |
| `11`    | `1011` | `B`         |
| `12`    | `1100` | `C`         |
| `13`    | `1101` | `D`         |
| `14`    | `1110` | `E`         |
| `15`    | `1111` | `F`         |
