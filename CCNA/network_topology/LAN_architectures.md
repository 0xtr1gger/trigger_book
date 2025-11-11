---
created: 2025-10-27 03:47:01
tags:
  - network_topology
---

## 2-tier campus LAN design

The **two-tier LAN design** consists of two hierarchical layers: **Access Layer** and **Distribution Layer**.

>[!note] Also called a **Collapsed Core** design because it omits a layer found in the Three Layer design: the **Core Layer**.

- **Access Layer**
	- The layer that **end hosts** connect to (PCs, printers, cameras, etc.).
	- **Access Layer Switches** typically have lots of ports for end hosts to connect to.
	- QoS marking is typically done here.
	- Security services like port security, DAI, etc., are typically performed here.
	- Switchports may be PoE-enabled for wireless APs, IP phones, etc.

- **Distribution Layer**
	- Aggregates connections from the Access Layer Switches.
	- This is the border between Layer 2 and Layer 3, so **Distribution Layer Switches** run both Layer 3 protocols (e.g., OSPF) and Layer 2 protocols (e.g., RSTP).
	- Connects to services such as Internet, WAN, etc.

>[!note]+
>- In a collapsed core design, the Distribution Layer is sometimes called the **Core-Distribution layer**.
> - Usually, the connections from the Access Layer Switches to Distribution Layer Switches are **Layer-2 connections**.
> - End hosts usually use **SVIs on the Distribution Layer Switches** as their **default gateways**.

![[2_tier.svg]]

>[!important] Each Distribution Layer Switch is connected to each other Distribution Layer Switch (full mesh). 
>- These connections are **Layer 3**.
>- Routing information can be shared via OSPF, for example.

>[!important] Each Access Layer Switches connects to at least one Distribution Layer Switch (typically two for redundancy; partial mesh).

![[2_tier.png]]

In large LAN networks with many Distribution Layer switches (for example, in separate buildings), the number of connections required between Distribution Layer switches grows rapidly.

To help scale large LAN networks, you can add a Core Layer.

>[!note] Cisco recommends adding a Core Layer if there are more than three Distribution Layers in a single location.
## 3-tier campus LAN design

The **three-tier LAN design** consists of two hierarchical layers: **Access Layer**, **Distribution Layer**, and **Core Layer**.

- **Core Layer**
	- Connects Distribution Layers together in large LANs.
	- The focus is speed (fast transport). Just fast packet forwarding, nothing extra.
	- CPU-intensive operations, such as security, QoS marking/classification, etc. should be avoided at this Layer.
	- Connections are all Layer 3. No spanning-three.
	- Connectivity should be maintained throughout the LAN even if devices fail.
	- Redundant connections between switches are important (EtherChannel).


![[3-tier_architecture.png]]
## Spine-Leaf Architecture

### North-South and East-West traffic

- The **Spine-Leaf Architecture** was designed for **data centers**.

>**Data centers** are dedicated spaces or buildings used to store computer systems such as servers and network devices.

>[!interesting] Evolution of network architectures in data centers
>- Traditional data center designs used a 3-tier architecture. This worked well when most traffic in the data center was North-South.
>- With the precedence of **virtual servers**, applications are often deployed in a distributed manner (across multiple physical servers), which increases the amount of East-West traffic in the data center. 
>- The traditional 3-tier architecture is inefficient in this case: it leads to bottlenecks in bandwidth as well as variability in server-to-server latency, depending on the path the traffic takes.
>
> The **Spine-Leaf architecture** was created to solve this.

>**North-south traffic** flows *into and out of a data center* (*inbound or outbound*), and typically involves communication with **external systems** outside the perimeter.

>**East-West traffic** refers to the traffic flow that originates and terminates **within a single data center** or network scope. It involves *communication between devices within the same network*.

### Spine and Leaf

>Data centers commonly use the **Spine-Leaf architecture**, also called **Clos architecture** after the name of one of its designers.

There are two types of switches in the Spine-Leaf architecture:

- **Leaf switches**, or **Leafs**
	- Connect to Spine switches and to end hosts, but not to other leaf switches.
	- Provide connectivity between end hosts and Spine switches.

- **Spine switches**, or **Spines**
	- Connect to Leaf switches.
	- Provide connectivity of the LAN to the Internet.

>[!important]+ In Spine-Leaf architecture:
> - Every **Leaf** switch is connected to every **Spine** switch. 
> - Every **Spine** switch is connected to every **Leaf** switch.
> 
> - **Leaf** switches do not connect to other **Leaf** switches directly. 
> - **Spine** switches do not connect to other **Spine** switches directly. 
> - End hosts, e.g., servers, only connect to **Leaf** switches. 

- The path taken by traffic is randomly chosen to load-balance the traffic among the Spine switches. 
- Each server is separated from another by **the same number of hops** (except those connected to the same Leaf), providing **consistent latency** for East-West traffic.

![[spine-leaf_architecture.png]]


>[!note] Spine-Leaf architecture is simple to scale.

>[!warning]+ Scalability limitations
>Because a spine node has a connection to every leaf node, the **scalability** of the fabric is limited by **the number of ports on Spine nodes**, not by the number of ports on the Leaf nodes.

>[!note]+ On redundant connections
>Redundant connections between Spine and Leaf switches are **unnecessary** because the nature of the topology  that ensures that each Leaf has multiple connections to the network fabric. Therefore, **each Spine node requires only one connection to each Leaf node.**

## SOHO networks

>**Small Office/Home Office (SOHO)** refers to the office of a small company, or a small home office with just a few devices. SOHO also refer to home networks.

- SOHO networks don't have complex needs, so all networking functions are typically provided by a single devices, often called a **home router** or a **wireless router**.

- This one device can serve as:
	- Router
	- Switch
	- Firewall
	- Wireless Access Point
	- Modem
## Quiz

1. Which Layer typically serves as the boundary between Layer 2 and Layer 3 in a traditional 2-tier or 3-tier network?
	- a. Core
	- b. Distribution
	- c. Access
	- d. Leaf

2. Which of the following would you not expect to find in the Core Layer of a traditional 3-tier LAN?
	- a. Layer 3 connections
	- b. STP
	- c. A full mesh of connections to all Distribution Layer switches
	- d. Powerful switches focused on speed

3. At which layer would you expect to find PoE-enabled switchports in a traditional 3-tier LAN?
	- a. Access
	- b. Core
	- c. Distribution
	- d. Leaf

4. In a Spine-Leaf architecture, which of the following should not be connected to a Leaf switch?
	- a. A Spine switch
	- b. A Leaf switch
	- c. A server

5. Which of the following functions might be included in the device known as a wireless router?
	- a. Routing
	- b. Switching
	- c. Wireless Access
	- d. Security
	- e. `a.` and `c.`
	- `a.`, `b.`, `c.`, and `d.`

6. Boson ExSim. Which of the following statements are true regarding physical connections in the Cisco ACI architecture? (Select 2 choices.)
	- a. Each leaf node must connect to every spine node.
	- b. An APIC must connect to at least one spine node.
	- c. Leaf nodes must be fully meshed. 
	- d. Spine nodes must be fully meshed. 
	- e. Each spine node must connect to every leaf node.

7. In a two-tier network design, which layers are combined together? (Select the best answer.)
	- a. Aggregation and access
	- b. Core, aggregation, and access
	- c. Core and distribution
	- d. Core and access
	- e. Core, distribution, and access
	- f. Distribution and access

| Question | Answer     |
| -------- | ---------- |
| `1.`     | `b.`       |
| `2.`     | `b.`       |
| `3.`     | `a.`       |
| `4.`     | `b.`       |
| `5.`     | `f.`       |
| `6.`     | `a.`, `e.` |
| `7.`     | `c.`       |

- VPN security architectures and access points
- East-West traffic security
- North-West traffic security
- secure network architecture: where IDSs, IPSs, firewalls, sensors, etc. should be placed