---
created: 2025-10-14 05:20:49
tags:
  - LAN_protocols
---
## FHRP

>**FHRP (First Hop Redundancy Protocol)** is a type of network protocols designed to provide **redundancy to the gateway router** within the network.

- FHRP allows two or more routers to provide backup for the default gateway address. 
- In the event of failure of an active router, the backup router will take over the address, usually within a few seconds. 

The primary goal of FHRPs is to eliminate a **single point of failure** at the gateway or first hop.

>[!important] Hosts are configured with only one default gateway IP (virtual IP), which is shared by the FHRP group.

>[!note] FHRP itself is not a protocol, just a type of protocols. Commonly used protocol specifications include HSRP, VRRP, and GLBP.
### Principles of FHRPs

- Routers participating in a FHRP group agree on a **virtual IP address**, which is configured as the default gateway for all hosts on the subnet. 
- One or more or more routers in the group share or are assigned a **virtual MAC address**. The format of this MAC address depends on the protocol.

The default gateway on hosts in the network is configured to the virtual IP address shared by the routers in the FHRP group. 

>[!important]+ Active and Standby routers
> - One router from the FHRP group is elected as the **Active** (or Master) router, responsible for forwarding traffic sent to the virtual IP address. 
> - Other routers act as **Standby** (or **Backup**). 

- When a host needs to send traffic to the default gateway, it first males an ARP request for the MAC address associated with the virtual IP address. 
- Only the active router responds to ARP requests requests using the virtual MAC address.


>[!important] If the active router fails, a Standby router becomes the next active router by taking over the virtual IP and MAC addresses.
> - The new active router will send **gratuitous ARP (gARP)** messages, and switches will update their MAC address tables. 
> - Hosts keep using the same default gateway address — **no changes in hosts' ARP table**. Only switches' MAC address table is updated.

- If the old active router comes back online, by default, it won't take back its role as the active router. It will become a standby router.

>[!note] With GLBP, failover also redistributes MAC assignments among the remaining routers for load balancing.

>[!important]+ Non-preemption 
>- FHRPs are **non-preemptive**: the current router will not automatically give up its role, even if the former active router starts functioning again.
>- But you can configure preemption so that the old active router does take back its old role.

>[!note] To monitor each other's status, routers exchange **hello messages**. 
## FHRP implementations

There are three main First Hop Redundancy Protocols:

- **HSRP (Hot Standby Router Protocol)**
    - A Cisco-proprietary protocol; allows a cluster of routers to cooperate and share a virtual IP and MAC addresses

- **VRRP (Virtual Router Redundancy Protocol)**
    - A vendor-neutral protocol that groups a cluster of physical routers to produce a single virtual router.

- **GLBP (Gateway Load Balancing Protocol)**
    - A Cisco-proprietary protocol that enables load balancing and provides redundancy for the default gateway.

| Criteria/FHRP           | HSRP                                         | VRRP                               | GLBP                                                                |
| ----------------------- | -------------------------------------------- | ---------------------------------- | ------------------------------------------------------------------- |
| Acronym                 | Hot Standby Router Protocol                  | Virtual Router Redundancy Protocol | Gateway Load Balancing Protocol                                     |
| Terminology             | Active/Standby                               | Master/Backup                      | AVG/AVF<br><br>Active Virtual Gateway/<br>Active Virtual Forwarders |
| Multicast IP address    | v1: `224.0.0.2`  <br>v2: `224.0.0.102`       | `224.0.0.18`                       | `224.0.0.102`                                                       |
| Virtual MAC address     | v1: `0000.0c07.acXX`<br>v2: `0000.0c9f.fXXX` | `0000.5e00.01XX`                   | `0007.b400.XXYY`                                                    |
| Cisco-proprietary?      | Yes                                          | No                                 | Yes                                                                 |
| VLAN support?           | Yes                                          | Yes                                | Yes                                                                 |
| Load-balancing support? | No                                           | No                                 | Yes                                                                 |
| Default priority        | 100                                          | 100                                |                                                                     |

## HSRP

>**HSRP (Hot Standby Router Protocol)** is a **Cisco-proprietary** FHRP.

- One **Active**, one **Standby** routers per an HSRP group.
- Other routers in the group are put in the **listen** state (only listen for hello messages).

>[!important]+ Active/Standby router election
>Active and Standby routers are elected based on **router priorities**.
>- The router with the **highest configured priority** becomes the **Active router**, and the router with the second highest priority becomes the Standby router.
>- Priority can range from **`0` to `255`**.
>- **`100` is the default priority**.
>
>Highest configured priority => active router
>Second highest priority => standby router
>-  If priorities of two routers are the same, one with the **highest IP address** is chosen to be active router.

There are two versions of HSRP:

- **Version 1**
	- Defined in [RFC 2281](https://datatracker.ietf.org/doc/html/rfc2281).
- **Version 2** 
	- Not published, Cisco-proprietary.
	- Adds support for IPv6 and increases the number of groups that can be configured.

- Multicast IPv4 addresses for Hello messages:
	- Version 1: `224.0.0.2`
	- Version 2: `224.0.0.102`

- Virtual MAC address format:
	- Version 1: `0000.0c07.acXX` (`XX` = HSRP group number)
	- Version 2: `0000.0c9f.fXXX` (`XXX` = HSRP group number)

In the virtual MAC address, `X` represent an HSRP group ID in hexadecimal.

>[!note]+
> - `0000.0c` = Cisco ID
> - `07.ac` = HSRP ID
> - `XX` = Group number

| HSRP version | IP protocol | Group address             | Virtual MAC address range | UDP port |
| ------------ | ----------- | ------------------------- | ------------------------- | -------- |
| **1**        | IPv4        | `224.0.0.2` (all routers) | `0000.0c07.acXX`          | `1985`   |
| **2**        | IPv4        | `224.0.0.102` (HSRP)      | `0000.0c9f.fXXX`          | `1985`   |
| **2**        | IPv6        | `ff02::66`                | `0005.73a0.0XXX`          | `2029`   |

>[!note]+ VLAN support
>In a situation with multiple subnets/VLANs, a different active router can be configured for each subnet/VLAN for load balancing.
## VRRP

>**VRRP (Virtual Router Redundancy Protocol)** is a standard vendor-neutral FHRP defined in [RFC 5798](https://datatracker.ietf.org/doc/html/rfc5798).

- One **Master**, one **Backup** routers.
- Similar to HSRP, but **preemption is enabled by default**, and failover times are faster.
- Master election is based on priority.
- VRRP compatible across various vendor implementations.

>[!important]+ VRRP multicast addresses
> Routers participating in VRRP communicate with each other using multicast IP addresses:
> - IPv4 multicast address: `224.0.0.18`
> - IPv6 multicast address: `ff02:12`

>[!important]+ VRRP virtual MAC address 
>- Virtual MAC addresses start with `0000.5e00.01XX`.

>[!note]+ VLAN support
>Different Master and Backup routers can be configured for each subnet/VLAN for load-balancing.
## GLBP

> **GLBP (Gateway Load Balancing Protocol)** is a Cisco-proprietary FHRP that attempts to overcome the limitations of existing redundant protocols by adding basic load balancing functionality.

- **Load balances** among multiple routers within a single subnet.
- **All routers on the network** take part in GLBP to form a group.

- GLBP allows to configure **multiple routers** in a GLBP group; all the routers in the group receive traffic sent to a virtual IP address configured for the group.

>[!important]+ AVG/AVF
>Each GLBP group contains an **AVG (Active Virtual Gateway)**.    
> - An AVG is elected based on router priorities: the router with the **highest priority** is elected as an AVG.
>- Priority can range from **`0` to `255`**.
>- **`100` is the default priority**.
> - If multiple routers have the same priority, the router with the **highest IP** address is elected as an AVG.
> 
>The other routers in the GLBP group are configured as **primary** or **secondary Active Virtual Forwarders (AVFs)** to serve as backup for the AVG.

- **Up to 4 primary AVFs** can be configured in a GLBP group; the primary AVFs can participate in forwarding traffic.
- **Up to 4 backup AVFs** routers are elected.

>[!important] Up to four AVFs (Active Virtual Forwarders) are assigned by the AVG (in addition, the AVG itself can be an AVF).

- When a client requests the IP address of its default gateway via ARP, the AVG responds with the virtual MAC address of one of the AVFs. When another client sends an ARP message to resolve the default gateway address, the AVG responds with the virtual MAC address of the next AVF.

- Therefore, each AVF acts as the default gateway for a subset of the hosts in the subnet, i.e., load balancing is achieved within a single subnet.

>[!important]+ GLBP multicast addresses
> Routers participating in GLBP communicate with each other using multicast IP addresses:
> - IPv4 multicast address: `224.0.0.102` (same as HSRP version 2).

>[!important]+ GLBP virtual MAC address 
>- Virtual MAC addresses start with `0007.b400.XXYY`.
>     - `XX` = GLBP group number
>     - `YY` = AVF number

## Flashcards

- What is the purpose of First Hop Redundancy Protocol (FHRP)?
    
    - To provide redundancy for the default gateway router so that if the active gateway fails, a backup router takes over to maintain continuous network connectivity.
        
- How do routers in an FHRP group share the gateway address?
    
    - They share the same Virtual IP (VIP) address and a virtual MAC address generated for the VIP, allowing seamless failover without changing host configurations.
        
- What are the roles of routers in an FHRP group?
    
    - One router is the active router (default gateway), and others are standby routers ready to take over if the active router fails.
        
- How do FHRP routers negotiate roles?
    
    - They send multicast Hello messages to each other to elect active and standby routers.
        
- What happens when the active router in an FHRP group fails?
    
    - A standby router automatically takes over as the active router and sends gratuitous ARP messages to update switches' MAC address tables.
        
- Are FHRPs preemptive by default?
    
    - No, FHRPs are non-preemptive by default; the current active router keeps its role even if the former active router returns, unless preemption is explicitly configured.
        
- In FHRP, who responds to ARP requests for the virtual IP address?
    
    - Only the active router responds with a unicast ARP reply containing the virtual MAC address.
        
- What must switches do when the active router changes in an FHRP group?
    
    - Switches update their MAC address tables based on the gratuitous ARP messages sent by the new active router.
        
- Name the three main FHRP protocols.
    
    - HSRP (Hot Standby Router Protocol), VRRP (Virtual Router Redundancy Protocol), and GLBP (Gateway Load Balancing Protocol).
        
- Is HSRP a Cisco proprietary protocol or an open standard?
    
    - HSRP is Cisco proprietary.
        
- What terminology does HSRP use for router roles?
    
    - Active router and standby router.
        
- What is the default priority value in HSRP?
    
    - 100.
        
- How is the active router elected in HSRP?
    
    - The router with the highest configured priority becomes active; if priorities tie, the router with the highest IP address is active.
        
- What multicast IP address does HSRP version 1 use for Hello messages?
    
    - 224.0.0.2.
        
- What multicast IP address does HSRP version 2 use for Hello messages?
    
    - 224.0.0.102.
        
- What is the virtual MAC address format for HSRP version 1?
    
    - 0000.0c07.acXX, where XX is the HSRP group number in hex.
        
- What additional support does HSRP version 2 provide compared to version 1?
    
    - IPv6 support and increased number of groups.
        
- What is the main difference between VRRP and HSRP regarding preemption?
    
    - VRRP has preemption enabled by default; HSRP requires manual configuration to enable preemption.
        
- Is VRRP vendor-neutral or Cisco proprietary?
    
    - VRRP is a vendor-neutral open standard.
        
- What multicast IP address does VRRP use for IPv4?
    
    - 224.0.0.18.
        
- What terminology does VRRP use for router roles?
    
    - Master and backup routers.
        
- What is the default priority value in VRRP?
    
    - 100.
        
- What is GLBP and how does it differ from HSRP and VRRP?
    
    - GLBP is a Cisco proprietary protocol that provides both redundancy and load balancing by allowing multiple routers to actively forward traffic.
        
- What roles exist in GLBP?
    
    - AVG (Active Virtual Gateway) and AVFs (Active Virtual Forwarders).
        
- How is the AVG elected in GLBP?
    
    - The router with the highest priority; if tied, the router with the highest IP address.
        
- How many AVFs can GLBP support per group?
    
    - Up to four primary AVFs plus backup AVFs.
        
- What multicast IP address does GLBP use?
    
    - 224.0.0.102 (same as HSRP version 2).
        
- How does GLBP achieve load balancing?
    
    - The AVG responds to ARP requests with different virtual MAC addresses assigned to AVFs, distributing traffic among multiple routers.
        
- What is the virtual MAC address format used by GLBP?
    
    - 0007.b400.XXYY, where XX is the GLBP group number and YY is the AVF number.
        
- Can FHRP protocols support VLANs and multiple subnets?
    
    - Yes, each VLAN or subnet can have its own FHRP group and active router for load balancing.
        
- What happens if the original active router in an FHRP group comes back online without preemption enabled?
    
    - It remains a standby router and does not take back the active role automatically.
        
- What is the default hello timer interval for HSRP and GLBP?
    
    - Hello packets are sent every 3 seconds.
        
- What is the default hold time for HSRP and GLBP?
    
    - 10 seconds (or three missed hello packets).
        
- What are the default hello and hold timers for VRRP?
    
    - Hello every 1 second; hold time approximately 3 seconds.
        
- Why is load balancing important in GLBP?
    
    - It optimizes bandwidth usage by distributing traffic across multiple routers instead of relying on a single active router.
        
- In FHRP, why do end hosts not need to update their ARP tables during failover?
    
    - Because the virtual IP and MAC addresses remain the same regardless of which router is active.
        
- What is the significance of gratuitous ARP in FHRP failover?
    
    - It updates switches' MAC address tables to reflect the new active router's virtual MAC address.
        
- How does FHRP improve network availability?
    
    - By eliminating a single point of failure at the default gateway and providing automatic failover to backup routers.
        
- What is the range of priority values used in FHRP protocols?
    
    - 0 to 255.
        
- Which FHRP protocol supports load balancing by default?
    
    - GLBP.
        
- Which FHRP protocols are Cisco proprietary?
    
    - HSRP and GLBP.
        
- Which FHRP protocol is an open standard?
    
    - VRRP.
        
