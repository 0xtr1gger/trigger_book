---
created: 2025-09-26 05:47:41
tags:
  - ethernet
---
## MAC addresses and address space

- Devices in a LAN are identified with **MAC (Medium Access Control)** addresses. 

>A **MAC address** is a unique **48-bit (6-byte)** identifier assigned to a **NIC (Network Interface Card)** of a device, used for communication within a LAN. MAC addresses are used in IEEE 802 networking technologies, including Ethernet, Wi-Fi, and Bluetooth. 

>[!important] MAC addresses are **6 bytes (48 bits)** long. They are most commonly represented as **12 hex digits**, usually separated by colons or hyphens.

>[!example]+
>```bash
>00:11:22:33:44:55 # colon-separated
>00-11-22-33-44-55 # hyphen-separated
>```

>[!note] MAC addresses are primarily assigned by device manufacturers, hence called **hardware addresses**, aka **physical** or **burned-in** addresses.

- MAC addresses are **globally unique**: no two devices in the world should have the same MAC address.
- The 48-bit address space contains $2^{48}$ (over 281 trillion) possible MAC addresses.
- MAC addresses are managed by the **IEEE**. They were first called MAC-48 identifiers but are now often referred to as **EUI-48**.

>[!note]+ EUI-64
>For non-Ethernet applications, the IEEE encourages the adoption of the more plentiful **EUI-64**.
>The IEEE has a target lifetime of 100 years (until 2080) for applications using EUI-48 space.
## Unicast, Broadcast and Multicast MAC addresses

There are three types of MAC addresses:
- **Unicast**
- **Broadcast**
- **Multicast**
### Unicast MAC addresses

>A **unicast MAC address** is a unique identifier assigned to a single NIC.

- When a frame is sent to a unicast MAC address, only the device with that specific MAC address processes the frame. **A unicast frame is intended for a single device.**
### Broadcast MAC addresses

>A **broadcast MAC address** is used to send a frame to all devices on a local network segment.

>[!important] The broadcast MAC address is **`FF:FF:FF:FF:FF:FF`**, where all bits are set to `1`.

When a frame is sent to the broadcast MAC address, every device  in the local network segment receives and processes it.

Broadcast MAC addresses are used for various purposes, such as:
- Switching (for discovering MAC addresses of unknown hosts with flooding algorithm)
- ARP requests (Address Resolution Protocol)
- DHCP (Dynamic Host Configuration Protocol)
### Multicast MAC addresses

>A **multicast MAC address** is used to send a frame to a specific group of devices.

>[!important]
>Multicast MAC addresses are *mapped* from multicast IP addresses. **IPv4 and IPv6 multicast MAC address ranges are different.**

>[!important] Multicast MAC addresses start with `01:00:5E` (`25` bits, `00000001.00000000.01011110.0`). The last `23` bits of multicast MAC addresses represent the **multicast group**.

>[!note]+ From IP to MAC multicast addresses
> - **Multicast IP addresses** represent groups of receivers rather than single devices:
> 	- **IPv4 multicast addresses**: `224.0.0.0` to `239.255.255.255`
> 	- **IPv6 multicast addresses**: `FF00::/8`
> 
> Here is how IP multicast addresses are mapped to MAC multicast addresses: 
> - **IPv4**: `MAC address = 01:00:5E:0 + last 23 bits of IPv4 multicast address`
> 	- The **fixed `25`-bit MAC prefix is `01:00:5E`**.
> 	- The **25th bit** of the MAC address is always `0`.
> 	- The upper 9 bits of a IPv4 address are **ignored**/lost — which causes **32 IPv4 multicast IP addresses to map to the same MAC address**.
> 	- Example: IPv4 `239.5.5.5` maps to `01:00:5E:05:05:05`.
> 
> - **IPv6**: `MAC address = 33:33 + last 32 bits of IPv6 multicast address`
> 	- The **fixed `16`-bit MAC prefix is `33:33`**.
> 
> ```
> IPv4:
> MAC multicast address = 01:00:5E + last 23 bits of IPv4 multicast address
> 
> IPv6:
> MAC multicast address = 33:33 + last 32 bits of IPv6 multicast address
> ```
> 
> You can use converters from MAC to IP, such as:
> - [`MAC to IPv6 Converter — NetTools.club`](https://nettools.club/mac2ipv6)
>
>| IP Version | Multicast IP Range              | Ethernet MAC Prefix | Bits Mapped from IP to MAC       | Resulting Mapping   | Notes                                                   |
> | ---------- | ------------------------------- | ------------------- | -------------------------------- | ------------------- | ------------------------------------------------------- |
> | IPv4       | `224.0.0.0` - `239.255.255.255` | `01:00:5E`          | Last `23` bits of IPv4 multicast | `01:00:5E:0X:XX:XX` | 32 IPv4 multicast IP addresses share one multicast MAC. |
> | IPv6       | `FF00::/8`(multicast range)     | `33:33`             | Last `32` bits of IPv6 multicast | `33:33:XX:XX:XX:XX` | Direct `32`-bit mapping                                 |


Multicast MAC addresses are used if various protocols, such as:
- IGMP (Internet Group Management Protocol) to manage group membership on IP multicast networks.
- STP (Spanning Tree Protocol)
- LLDP (Link Layer Discovery Protocol)
- CDP (Cisco Discovery Protocol)
#### Common multicast MAC addresses

| **MAC Address**     | **Type**  | **Notes**                                                                                                                                |
| ------------------- | --------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `01:00:0C:CC:CC:CC` | Multicast | Cisco Discovery Protocol (CDP) multicast address; used by Cisco devices to send unsolicited multicast advertisements ― **CDP messages**. |
| `01:80:C2:00:00:00` | Multicast | Link-Layer Discovery Protocol (LLDP) multicast address; used as a destination MAC address of **LLDPDUs (LLDP Data Units)**.              |
|                     |           |                                                                                                                                          |


| **MAC Address**                                                    | Notes                                                                                                                                       |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `FF:FF:FF:FF:FF:FF`                                                | Broadcast MAC address; reaches all devices within the broadcast domain (all hosts on VLAN).                                                 |
| `01:00:5E:XX:XX:XX`<br>(`25` bits; `00000001.00000000.01011110.0`) | Targets IPv4 multicast (`224.0.0.0` - `239.255.255.255`) addresses.<br>The last `23` bits of the address represent the **multicast group**. |
| `33:33:XX:XX:XX:XX`                                                | Targets IPv6 multicast (`FF00::/8` range) addresses. <br>The last `32` bits of the address represent the **multicast group**.               |
| `01:00:0C:CC:CC:CC`                                                | CDP multicast address.                                                                                                                      |
| `01:00:0C:CC:CC:CD`                                                | VTP (VLAN Trunking Protocol) multicast MAC address.                                                                                         |
| `01:00:0C:CC:CC:CE`                                                | PAgP multicast MAC address.                                                                                                                 |
| `01:00:0C:CC:CC:CF`                                                | HSRP address for active routers.                                                                                                            |
| `01:00:0C:CC:CC:CG`                                                | HSRP address for standby routers (less common).                                                                                             |

##  The structure of a MAC address

Each unicast MAC address consists of two parts:

1. **First 3 bytes — OUI**
	- The **OUI (Organizationally Unique Identifier)** assigned to the manufacturer; uniquely identifies the organization that produced the NIC. 
	- An OUI is assigned to the company that manufactured the device.
2. **Last 3 bytes — device identifier**
	- Unique NIC identifier under the same OUI.

>An **OUI (Organizationally Unique Identifier)** is a unique 3-byte (24-bit) identifier assigned to an organization that manufactures devices and assigns them MAC addresses. All MAC addresses assigned by an organization will have the first 24 bits set to the OUI of that organization.

Use online OUI lookup tools to determine the manufacturer associated with a MAC address:
- [`Wireshark OUI Lookup Tool`](https://www.wireshark.org/tools/oui-lookup.html)
- [`macaddress.io`](https://macaddress.io/mac-address-lookup/E2Ngxb9w56)
- [`MAC Address Lookup`](https://www.macvendorlookup.com/)

![[mac_addresses.svg]]

### `U`/`L` bit: Universal/Local addresses

MAC addresses can be divided two types:
- **Universally Administered Address (UAA)**
- **Locally Administered Address (LAA)**

>[!important]
>- A **UAA** is assigned by the *manufacturer* and is **globally unique**;
>- A **LAA** is assigned by a *network administrator* and is **locally unique within a network segment**.

LAAs are =simply= addresses manually configured by network administrators within a network. These can be used, for example, for network virtualization.

>[!important] Whether an address is a UAA or LAA is determined by the **`U`/`L` bit** (Universal/Local bit), which is the **least-significant bit (LSB)** of the first octet of the address, or the 7th bit of the first byte of the address.

>[!important]
>- **UAA**: `U`/`L` bit is set to **`0`**.
>- **LAA**: `U`/`L` bit is set to **`1`**.

|      UAA      |      LAA      |
| :-----------: | :-----------: |
| `xx:xx:xx:0x` | `xx:xx:xx:1x` |

### `I`/`G` bit: individual and group addresses

Multicast addresses are signified with the `I`/`G` (Individual Group) bit, which is the least-significant bit of the first byte of the address. 

>[!important]
>- **Unicast addresses**: `I`/`G` bit is set to **`0`**.
>- **Multicast addresses**: `I`/`G` bit is set to **`1`**.

|   Multicast   |    Unicast    |
| :-----------: | :-----------: |
| `xx:xx:xx:x0` | `xx:xx:xx:x1` |

>[!note]
>Broadcast addresses are a subset of multicast addresses. 
