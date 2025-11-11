---
created: 2025-09-30 11:32:55
tags:
  - LAN_protocols
---
## ARP

>The **Address Resolution Protocol (ARP)** is a network protocol used to discover what MAC addresses (Layer 2) are associated with given IP addresses (Layer 3).

- The goal of ARP is to provide network devices with all information necessary to send packets.
- ARP is used to map IP addresses to MAC addresses (i.e., to learn the MAC address of the next hop); it works as a **bridge from L2 to L3**.

>[!important] ARP works only within the **same subnet**; for communication outside the local subnet, the sender sends packets to the **default gateway (router)** MAC address.

>[!important] The **EtherType** field (Ethernet header) of an ARP packet is **`0x0806`**.

>[!important] An IPv4/Ethernet ARP message is `28` bytes in length.

>[!note] The problem ARP solves
>When one device sends an ICMP ping message to another:
> - **Layer 4**
> 	- The sending device works with ICMP. All necessary information at this layer is available.
> - **Layer 3**
> 	- The sending device knows the destination IP address, since it is explicitly set by a user (or discovered with DNS). All necessary information at this layer is available.
> - **Layer 2**
> 	- The sending device doesn't know the MAC address of the destination device, which is necessary to transfer a packet over the destination LAN. This is what **ARP** solves. 

## How ARP works

There are two main types of messages used in ARP:

- **ARP Request** = **broadcast**, sent by the device that needs to discover a MAC address of another device (the MAC address of the destination host is unknown).

- **ARP Reply** = **unicast**, sent only to one host (the host that sent the Request).

>[!note] ARP messages are encapsulated directly within an Ethernet header and trailer.

>[!important] ARP flow
> 1. **ARP Request** 
> 	- The device that wants to learn a MAC address sends a **broadcast ARP request** (destination MAC address `FF:FF:FF:FF:FF:FF`). This frame includes the IP address of the target device.
> 2. **ARP Reply** 
> 	- All devices on the LAN receive the request, but only the device with the matching IP address sends a **unicast ARP reply** with its MAC address back to the requester.
> 3. **ARP cache** 
> 	- The requester caches this IP-to-MAC mapping in its ARP table for future use.

>[!example]+
> Suppose the **Host A** (IP address `10.0.0.10`, MAC address `AA:AA:AA:AA:AA:AA`) wants to send a packet to the **Host B** (IP address `10.0.0.11`, MAC address `BB:BB:BB:BB:BB:BB`) in the same subnet. 
>>[!important] The **Host A** doesn't now the destination MAC address of the **Host B**, only its IP address.
>
> | Host | IP address  | MAC address         |
> | ---- | ----------- | ------------------- |
> | A    | `10.0.0.10` | `AA:AA:AA:AA:AA:AA` |
> | B    | `10.0.0.11` | `BB:BB:BB:BB:BB:BB` |
> 
> Here is how the **Host A** uses ARP to discover the MAC address of the **Host B**:
> 
> 5. The **Host A** (the sender) sends a **broadcast** Ethernet frame with an **ARP Request**; 
> 	- **In Ethernet frame: the destination MAC address is set to `FF:FF:FF:FF:FF:FF`.**
> 	- **In ARP Request header: the target MAC address is set to `00:00:00:00:00:00`.**
>
> | **Ethernet header**       | **Value**             |
> | ------------------------- | --------------------- |
> | Source MAC address        | `AA:AA:AA:AA:AA:AA`   |
> | *Destination MAC address* | *`FF:FF:FF:FF:FF:FF`* |
> | **ARP Request**           | **Value**             |
> | Sender hardware address   | `AA:AA:AA:AA:AA:AA`   |
> | Sender protocol address   | `10.0.0.10`           |
> | *Target hardware address* | *`00:00:00:00:00:00`* |
> | Target protocol address   | `10.0.0.11`           |
> 6. The switch receives the frame from the **Host A**, and then **broadcasts** that message to all hosts in the network.
> 
> 7. *Every host in the network receives the message* and compares the destination IP address in the frame with its own IP address. *Only the host with the matched address will send an **ARP Reply** (**Host B**)*; all other hosts ignore the frame.
> 
> 8. The **Host B** (the target) sends an **ARP Reply** to the **Host A**:
> 
> | **Ethernet header**       | **Value**           |
> | ------------------------- | ------------------- |
> | Source MAC address        | `BB:BB:BB:BB:BB:BB` |
> | Destination MAC address   | `AA:AA:AA:AA:AA:AA` |
> | **ARP Request**           | **Value**           |
> | Sender hardware address   | `BB:BB:BB:BB:BB:BB` |
> | Sender protocol address   | `10.0.0.11`         |
> | *Target hardware address* | `AA:AA:AA:AA:AA:AA` |
> | Target protocol address   | `10.0.0.10`         |


Here is the structure of an **ARP Request**:

| **Ethernet header**     | **Value**                 |
| ----------------------- | ------------------------- |
| Source MAC address      | MAC address of the sender |
| Destination MAC address | `FF:FF:FF:FF:FF:FF`       |
| **ARP Request**         | **Value**                 |
| Sender hardware address | MAC address of the sender |
| Sender protocol address | IP address of the sender  |
| Target hardware address | MAC address of the target |
| Target protocol address | `00:00:00:00:00:00`       |

### ARP table and timers

>Each device maintains an **ARP table**, or **ARP cache**, to store recent IP-to-MAC mappings, reducing broadcast traffic.

- To view ARP table on Windows or macOS:

```bash
arp -a
```

- To view ARP table on Linux:

```bash
ip neighbor
```

>[!note] The type `Static` means a default entry (the address wasn't actually learned with ARP), and `Dynamic` means the entry was learned by sending an ARP Request and receiving an ARP Reply.

>[!important] The default ARP cache timeout on Cisco devices is **240 minutes (4 hours)**.

- The ARP table is stored locally on each device.
- Subsequent communication use this cached binding instead of sending ARP request out again.

- To show **ARP table** on a Cisco router: 

```toml
R1# show arp
```

- To show **ARP timeout**:

```toml
R1# show int g0/1
```

- To **clear APR cache**:

```toml
R1(config)# clear arp-cache
```
### Static ARP entries

>MAC addresses learn with ARP Requests are called **dynamic addresses**;
>Manually configured MAC addresses are called **static addresses**. 

- **Static ARP entries** are permanent. They can not be overridden by dynamic entries. 

- To **add a static ARP entry** on a Cisco device:

```toml
R1(config)# arp IP_ADDRESS MAC_ADDRESS arpa
```

```toml
R1(config)# arp 192.168.1.5 20fc.1480.aff2 arpa
```

- To **remove a static APR entry**:

```toml
R1(config)# no arp IP_ADDRESS
```

```toml
R1(config)# no arp 192.168.1.5
```

### Gratuitous ARP

ARP may also be used as a simple announcement protocol. This is useful for updating other hosts' mappings of a hardware address when the sender's IP address or MAC address changes. Such announcements are called **gratuitous APR (GARP)**.

>**Gratuitous ARP (GARP**) is a type of ARP messages that doesn't respond to a specific APR request, but instead announces the sender's own ARP mapping to the entire network. GARP messages are broadcast (`FF:FF:FF:FF:FF:FF`).

- GARPs allow other devices to learn the MAC address of the sending device without having to send ARP requests.
- Some devices automatically send GARP messages when an interface is enabled, IP address is changed, MAC address is changed, etc.
## Proxy ARP 

>**Transparent Subnet Gatewaying**, also known as **Proxy ARP**, is a technique used to allow hosts on a subnet to communicate with hosts on another subnet without the need to configure routing or a default gateway.

In a typical network, devices communicate with each other within the same subnet, and ARP is used to resolve IP addresses to MAC addresses. But when devices are in *different subnets*, they can't communicate directly due to the boundary imposed by the subnetting, which requires the packet to go through a router.

- *Transparent subnet gatewaying* allows a router, often referred to as a **gateway** or **transparent bridging device**, to *intercept* ARP requests from hosts in one subnet and respond on behalf of a device located in another subnet.

Here is how it works:

1. **ARP Request**: When Host A in one subnet wants to communicate with Host B in another subnet, it sends an ARP request (broadcast) to find the MAC address of Host B.
2. **Proxy ARP Response**: The router, acting as a proxy, responds to the ARP request with **its own MAC address**, even though the IP address belongs to Host B. 
3. **Packet forwarding**: When Host A wants to send a network packet to Host B, the packet actually goes to the gateway router, which then uses the destination IP address to determine where the packet is supposed to go (Host B).

This technique is useful in scenarios where hosts are not aware of the subnetting and need to communicate as if they are on the same subnet. It simplifies network configuration and can be used to connect different physical segments with the same IP address range (e.g., when both Host A and Host B on different subnets both have address `10.0.0.11`; the ARP proxy prevents conflicts in this case).

>Here is a simple example of configuring proxy ARP on a Cisco router:

- To **check whether proxy ARP is enabled on an interface** (search for line `Proxy ARP`):

```toml
R1# show ip interface gi0/0
```

- To **enable proxy ARP** on an interface:

```toml
R1(config)# interface gi0/0
R1(config-if)# ip proxy-arp
```

- To **disable proxy ARP** on an interface:

```toml
R1(config-if)# no ip proxy-arp
```

Example of full proxy ARP configuration:

```toml
interface FastEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 ip proxy-arp
!
interface FastEthernet0/1
 ip address 192.168.2.1 255.255.255.0
 ip proxy-arp
!
ip route 192.168.2.0 255.255.255.0 FastEthernet0/1
```

>[!note] 
>**A misconfigured Proxy ARP can pose security risks**.

## Flashcards

- ARP
    - Address Resolution Protocol

- What is the main purpose of ARP?
    - To map IPv4 addresses (Layer 3) to MAC addresses (Layer 2) within the same subnet.

- Does ARP work across different subnets?
    - No, ARP works only within the same subnet; if proxy ARP is not in use.

- What MAC address is used in the Ethernet frame when sending an ARP request?
    - Broadcast address `FF:FF:FF:FF:FF:FF`

- What MAC address is used in the ARP request's target hardware address field?
    - `00:00:00:00:00:00` (unknown)
        
- What EtherType value indicates an ARP frame in Ethernet?
    - `0x0806`

- What are the two main types of ARP messages?
    - ARP Request and ARP Reply

- What happens when a host receives an ARP request for its own IP address?
    - It sends an ARP reply with its MAC address to the requester.

- What is stored in the ARP cache/table?
    - Recent IP-to-MAC address mappings.
        
- Purpose of ARP cache
    - It reduces broadcast traffic by caching resolved addresses.

- What is the default ARP timeout on Cisco devices?
    - 240 minutes (4 hours)
        
- How do you display the ARP table on a Cisco router?
    - `show arp`

- How do you add a static ARP entry on a Cisco device? What is it?
    - `arp IP_ADDRESS MAC_ADDRESS arpa`
    - A static ARP cache entry is a manually configured permanent IP-to-MAC mapping that cannot be overwritten by dynamic ARP.

- How do you remove a static ARP entry on Cisco?
    - `no arp IP_ADDRESS`

- How do you clear the ARP cache on Cisco?
    - `clear arp-cache`
        
- What is GARP? Why is it used?
    - GARP (Gratuitous ARP) is an ARP broadcast message where a device announces its own IP-to-MAC mapping without being requested.
    - GARP is used to detect IP conflicts or update other devices’ ARP caches after IP or MAC changes.

- What is proxy ARP?
    - A proxy ARP, or gateway, is a router that answers ARP requests on behalf of a device in another subnet, which allows ARP devices in two different subnets to exchange ARP messages without explicit routing.
    - The gateway router replies with its own MAC address for IP addresses outside the local subnet and then forwards packets appropriately.

- How do you enable Proxy ARP on a Cisco interface?
    - `ip proxy-arp` in interface configuration mode.

- How do you disable Proxy ARP on Cisco?
    - `no ip proxy-arp` in interface configuration mode.

- What security risks are associated with ARP?
    - ARP spoofing/poisoning attacks where false ARP replies redirect traffic.

- What happens if a device does not find an IP-to-MAC mapping in its ARP cache?
    - It sends an ARP request broadcast to resolve the MAC address.

- What command shows if Proxy ARP is enabled on an interface?
    - `show ip interface <interface>` (look for "Proxy ARP" line)

- Can ARP requests be unicast?
    - No, ARP requests are always broadcast.

- Can ARP replies be broadcast?
    - No, ARP replies are unicast to the requester.

- What happens if two devices send Gratuitous ARP with the same IP address?
    - An IP conflict is detected.

- What field in the Ethernet frame indicates that the payload is an ARP message?
    - EtherType field with value `0x0806`

- How does a switch handle ARP requests?
    - It floods the ARP request out all ports except the one it was received on.

- Can ARP be used with IPv6?
    - No, IPv6 uses Neighbor Discovery Protocol (NDP) instead.

- What is the command to view ARP cache timeout on Cisco devices?
    - `show interface <interface>`

- What happens when a device changes its IP or MAC address?
    - It may send a Gratuitous ARP to update other devices’ ARP caches.
        
