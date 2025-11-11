---
created: 2025-10-05 08:01:16
tags:
  - stp
  - LAN_protocols
---
## Switching loops and broadcast storms 

In LANs, redundant links between switches are often added for fault tolerance and high availability. However, redundant connections cause **switching loops**.

>A **switching loop**, or **bridge loop**, occurs in a network when there is more than one Layer 2 path between two devices. 

>Switching loops can lead to a situation when a **BUM (Broadcast, Unknown unicast, and Multicast)** frames are forwarded out every port, and as a result, start endlessly rushing around the network, consuming bandwidth. At some point, the network becomes so congested that legitimate traffic can no longer be sent. This is known as **broadcast storm** or **broadcast radiation**.

- Broadcast storms not only consume network bandwidth, but also significantly impact performance of end-user devices, since they need to process excessive number of broadcast frames.

>[!note]+ On TTL
>In Layer 3 networks, such broadcast storms are prevented by **TTL (Time-To-Live)** field in the IP packet, which is used to indicate hop count: each time the packet arrives to a router on the way to its destination, the router decreases the TTL value by `1`, then forwards the packet to the next hop. If the TTL reaches `0`, the packet is dropped.
>However, the Ethernet header doesn't have such TTL field. This means that broadcast frames can loop around the network indefinitely.
>See [[IPv4_packet]] and [[Ethernet_frames]].

>[!example]-
> Here is a detailed description of how broadcast storms occur:
> 
> 1. A host `A` sends a broadcast frame to the switch `SW1` through the interface `Fa0/11`.
>     
> 2. The switch's logic tells to flood the broadcast frame out of all its interfaces in the same VLAN except the interface to which the frame arrived.
>     
>     - Therefore, `SW1` will forward broadcast frames to the switches `SW2` and `SW3` through the interfaces `Gi0/1` and `Gi0/2`, respectively.
> 3. The switches `SW2` and `SW3` receive the broadcast frame from `SW1`
>     
>     1. `SW2` receives a broadcast frame on the `Gi0/2` interface. In response to a broadcast, `SW2`, following the same logic, sends the broadcast frame out of all its interfaces except `Gi0/2`: through `Gi0/1` to the switch `SW3`, and through `Fa0/12` to the host `B`.
>         
>     2. Similarly, `SW3` receives a broadcast on its `Gi0/1` interface, and floods the frame through the `Gi0/2` interface to `SW2`, and through `Fa0/13` to the host `C`.
>         
> 4. Therefore, the switches `SW2` and `SW3` send the same copy of the broadcast frame to each other simultaneously, in response to the broadcast from `SW1`.
>     
>     1. The switch `SW2` receives the broadcast from `SW3` on its `Gi0/1` interface (from which it sent the same frame just a moment ago). `SW2` then sends out this frame back to the switch `SW1` (`Gi0/2`), and again to the host `B` (`Fa0/12`).
>         
>     2. The switch `SW3` receives the same broadcast it just sent from `SW2` on its port `Gi0/2`. `SW3`, Again, it sends the frame to the switch `SW1` (`Gi0/1`) and ho the host `C` (`Fa0/13`).
>         
> 5. The switch `SW1` now receives two broadcast frames simultaneously. Its logic dictates to flood them again. The process repeats, starting from the step `1`, but the number of broadcast frames _doubles_.
> ![[broadcast_radiation_example.png]]

>[!note]+ MAC table instability (MAC address flapping)
>Broadcast storms can also cause **MAC table instability (MAC address flapping)**:
>- Each time a frame arrives on a switchport, the switch updates its MAC address table to associate the source MAC address of the frame with the interface it has arrived on.
>- During broadcast storms, frames with the same source MAC address repeatedly arrive on different ports.
>- This causes switches to constantly update their MAC address table with contradictory information, leading to **MAC address table instability**. 
>- Eventually, switches will fail to accurately forward any frame. This is called **thrashing** of the MAC address table.

So, switching loops are roots of all the evil. To prevent them, we have **STP**.

## STP

> The **Spanning Tree Protocol (STP)** is a network protocol that builds a loop-free (*tree*) logical topology for Ethernet networks.

- Classic STP is standardized by IEEE in **802.1D**.
- Switches from all vendors run STP **by default**.
- STP prevents Layer 2 loops by placing redundant ports in a blocking state, essentially disabling the interfaces.
- These interfaces act as backups that can enter the forwarding state if an active (currently forwarding) interface fails.
- Interfaces in the forwarding state behave normally. They send and receive all normal traffic.
- Interfaces in a blocking state only send or receive STP messages (called **BPDUs = Bridge Protocol Data Units**).

>[!note]+ Spanning Tree Algorithm (STA)
>The algorithm STP uses to choose which interfaces should be placed into a forwarding state, and which into a blocking state, is called the **Spanning Tree Algorithm (STA)**. 
>Any interface that hasn't been chosen to be placed into a forwarding state is placed into a blocking state.

>[!note]+ Bridges
>STP still uses the term 'bridge'. When we use the term 'bridge', we actually mean 'switch'. Bridges are not used in modern networks.
## Hello BPDUs and Bridge IDs 

>Switches running STP send messages called **BPDUs (Bridge Protocol Data Units)** to exchange information with each other.

- Using BPDUs, switches **advertise themselves** and **learn about other switches** on the network.
- Switches send BPDUs regularly, by default every **2 seconds**, out of all interfaces.

>[!important]+ Destination multicast address of STP BPDUs
>The **destination MAC address** for STP BPDUs is a reserved multicast address: **`01:80:C2:00:00:00`**. 
>These frames are processed by switches participating in STP and are not forwarded outside the local link.

>If a switch receives a BPDU on an interface, this indicates it's connected to another switch on that interface (just because routers, personal computers, etc., don't send BPDUs). 

>[!note]- The structure of a BPDU
> ![[BPDU.png]] 

### Bridge IDs

In STP, each switch is assigned to a unique ID, called Bridge ID (BID), included in every STP BPDU.

>An **STP BID (Bridge ID)** is a unique **8-byte** (64-bit) identifier assigned to each STP-enabled switch on a STP-enabled network. BIDs are advertised in one of the fields of STP BPDUs. 

The bridge ID consists of two fields:

- **Bridge priority** — **2 bytes (16 bits)**, configurable in multiples of `4096`.
- **MAC address** of the switch (aka System ID) — **6 bytes (48 bits)**, unique to the device.

![[BID.svg]]
#### Bridge priority

>**Bridge priority** is used to select a root bridge and non-blocking ports on the network.

The **bridge priority** consists of two parts:

- **Bridge priority** (4 bits)
- **Extended system ID** = VLAN ID (12 bits)

>[!tip] Wait, what VLAN ID does in BID?
> - Cisco switches use a version of STP called **PVST (Per-VLAN Spanning Tree)**. 
> - PVST runs a separate STP "instance" in each VLAN: in each VLAN different interfaces can be forwarding/blocking. 
> - For example, one interface can be forwarding in VLAN `10`, but blocking in VLAN `20`.
> - PVST uses the VLAN ID specified in the BID to distinguish between VLANs.

>[!note] See [[VLANs]].

>[!important] 
>Typically, STP traffic is assigned to the **default VLAN** with the **VID `1`**.

>[!important] 
>In the default VLAN (VLAN `1`), the default bridge priority is `32769` (`32768` + `1`)

Let's look at the figure:

![[bridge_priority.png]]


The **bridge priority + extended system ID** is **a single field** of the bridge ID. 

>[!important]
>The *extended system ID* is set and can not be changed. It's determined by the VLAN ID of the VLAN to which the BPDU frame belongs. 
>Therefore, you can only control the **four most significant bits** of the Bridge Priority field (light purple on the picture). 

>[!important] In STP, the **range** of Bridge Priority is **from `0` to `61440`**, but it can only be changed in units of **`4096`** (the value of the least significant bit of Bridge Priority).

>[!important] To obtain the total Bridge Priority value, add the VLAN ID to the Bridge Priority.

The valid values of **Bridge Priority** are as follows:

| Decimal |        Binary         |
| :-----: | :-------------------: |
|   `0`   | `0000` `000000000000` |
| `4096`  | `0001` `000000000000` |
| `8192`  | `0010` `000000000000` |
| `12288` | `0011` `000000000000` |
| `16384` | `0100` `000000000000` |
| `20480` | `0101` `000000000000` |
| `24576` | `0110` `000000000000` |
| `28672` | `0111` `000000000000` |
| `32768` | `1000` `000000000000` |
| `36864` | `1001` `000000000000` |
| `40960` | `1010` `000000000000` |
| `45056` | `1011` `000000000000` |
| `49152` | `1100` `000000000000` |
| `53248` | `1101` `000000000000` |
| `57344` | `1110` `000000000000` |
| `61440` | `1111` `000000000000` |

>[!note]+ A BID of history
>Initially, the first two bytes of the BID (Bridge Priority) were a single field, a `16`-bit bridge priority. 
>However, since IEEE 802.1D-2004, the System ID extension, the field has been divided, and now the first `4` bits are an actual configurable priority, and the last twelve bits carry the bridge system ID extension. 
>For example, in Cisco's PVST and some other STP variations set the extended bridge system ID to carry a VLAN ID of a packet.

## How STP works

Here's how STP works in a nutshell:

1. STP elects a **root bridge**.
    - All ports on the root bridge are put in a **forwarding state**.
    - All other non-root switches must have a path to reach the root bridge.
    
2. Each non-root switch selects one of its interfaces to be its **root port**.
    - The interface with the lowest **root cost** becomes the **root port**.
    - If the two ports have the same root cost, the port connecting to the switch with the **lowest neighbor bridge ID** becomes the root port.
    - All root ports are put in a **forwarding state**.

3. Each remaining collision domain selects one interface with the lowest root cost to be a **designated port** (forwarding state). The other port in the collision domain will be non-designated (blocking).

Now let's walk through these steps one-by-one.

In order to create a loop-free topology, STP answers the following four questions:
- Who is the **Root Bridge**?
- What are the **Root Ports**?
- What are the **Designated Ports**?
- What are the **Blocking (Non-Designated) Ports**?
### Root Bridge

>The **Root Bridge** is the central point of a spanning tree.
>Each switch on the network must have a path to reach the Root Bridge, and all STP paths are calculated relative to the Root Bridge. 

>[!important] In a network running STP, there can **only be one root switch**.

>[!important] The Root Bridge is elected based on the **BID (Bridge ID)** field in STP BPDUs: the switch with the **lowest BID** becomes the **Root Bridge**.

>[!note] The Bridge ID (BID) consists of two fields: Bridge Priority and System ID (MAC address). See [[#Hello BPDUs and Bridge IDs]] section.

The root bridge is elected based on the following scheme:
1. The switch with the lowest **Bridge Priority field** becomes the Root Bridge.
2. If priorities of the switches are equal (this situation is called a **tie**), the switch with the **lowest MAC address** will become the root bridge (the MAC address in this case is called a **tie-breaker**).

>[!important] By default, the root bridge is elected based on its MAC address (lowest), since the default bridge priority on all switches is the same, `32768`.

STP Root Bridge election process:

1. **All switches claim to be the root bridge** by sending **Hello BPDUs** with the root BID set to their own BID.
2. If a switch receives a Hello BPDU with a **lower root BID** (called **superior Hello BPDU**), the switch stops advertising itself as root and starts sending Hello BPDUs with the that lower BID.
3. Eventually, once the topology has converged all switches agree on the root switch with the lowest BID, i.e., the root bridge, **only the root bridge sends Hello BPDUs**.
4. Other switches in the network will only forward these BPDUs, but not generate their own original BPDUs.

>**Hello BPDUs** are configuration BPDUs used by switches to declare themselves as the root bridge and to share information about their bridge ID, priority, and path cost to the root bridge.

>[!note] After the root bridge has been elected, it becomes the only switch that sends BPDUs. Other switches on the network **only forward these BPDUs to each other**.

>A **superior Hello BPDU** is a Hello BPDU from a switch with a lower BID.

>An **inferior Hello BPDU** is a Hello BPDU that lists the root BID of the switch with the higher BID.

>[!important] All ports on the root bridge become **Designed Ports**. Designated ports are out in the **forwarding** state.

>[!important] The switches will only forward BPDUs on their designated ports.
>- Switches do not forward the BPDUs out of their root ports and non-designated ports, only their **designated** ports. 

### Root Ports 

>Each **non-root** switch seeks one best link to the **Root Bridge**, and selects the **interface** with the lowest **root cost** to be the **root port**.

>[!important]+ Cost
>Each interface has an associated spanning tree **cost**. The cost is based on the interface's bandwidth:
> 
> | Speed    | STP Cost |
> | -------- | -------- |
> | 10 Mbps  | `100`    |
> | 100 Mbps | `19`     |
> | 1 Gbps   | `4`      |
> | 10 Gbps  | `2`      |
> | 100 Gbps | `x`      |
> | 1 Tbps   | `x`      |


>[!important]+ Root cost
>The **root cost** is the **total cost** of the **outgoing** interfaces along the **whole path** to the root bridge.

>[!important] The cost of all interfaces on the Root Bridge are `0`.

- Each non-root switch selects **one** of its interfaces to be its **root port**.
- The interface with the **lowest root cost** becomes the **root port**.
- **Root ports are put into forwarding state**.

>In BPDUs sent by the root bridge, the **root cost** is set to **`0`** (the root's cost to reach itself is `0`).

### Designed and Non-Designated Ports

>[!important]+ Designated ports
>The ports connected to another switch's Root Port must be **Designed**, i.e., put into the **forwarding state**.
>Because the root port is the switch's path to the root bridge, another switch must not block it.

>[!important]+ Interface IDs
>In STP, each interface on each switch is assigned to an **interface ID**, which consists of the **port priority** and **port number** *hexadecimal* values. **Port priority** is **`128`** by default:
>- **STP port ID** = **port priority** (default `128`) + port number = `x80` + port number.

- If two ports have the same Root Cost, the port connected to the switch with the **lowest neighbor bridge ID** becomes the root port.
- If the two ports have the same root cost and neighbor bridge ID (connected to the same switch), the port connected to the interface on the neighbor switch with the **lowest port ID** becomes the root port.

> A tie-breaker for the root cost is the **neighbor bridge ID**.  
> A tie-breaker for the neighbor bridge ID is the **neighbor interface ID**.

To summarize, the selection of **designated ports** on **each switch** is based on:

1. Lowest root cost
2. Lowest neighbor ID
3. Lowest neighbor port ID

>[!note]+ Collision domains and links
>Every collision domain (most often, it is one cable between two switches) has one Designated port.  
>Each link is a separate collision domain.

4. The interface with the **lowest root cost** will be **designated** on a switch.
5. If there's a tie, interface on the switch with the **lowest bridge ID** will be designated.
6. The other switch will make its port **non-designated**.

>**Non-Designated** ports are put in **blocking** state.
## STP port states 

Once we've done with root and root ports election, it's time to take a closer look on how STP operates. 

Previously, we only talked about Blocking and Forwarding states, but there are 2 more port states.  

In STP, each switch ports in the LAN can be in one of the following states:

- **Blocking**
- **Listening**
- **Learning** 
- **Forwarding**


>[!important]+ Blocking
> - **Non-designated** ports are put in the **Blocking** state.
> - Interfaces in the Blocking state are effectively disabled to prevent loops.
> - An interface in the Blocking state:
> 	-  **receives STP BPDUs**;
> 	- **does not send or receive regular network traffic**: any traffic that arrives at the interfaces in the Listening state will be **dropped**;
> 	- **does not forward STP BPDUs**;
> 	- **does not learn MAC addresses**.

After the Blocking state, Designated or Root ports enter the Listening state. 

>[!important]+ Listening
> - Only **Designated** or **Root Ports** enter the Listening state; Non-Designated Ports are always Blocking.
> - The Listening state is **15 seconds** by default. This is determined by the **Forward delay timer**.
> - An interface in the Listening state:
> 	- **only forwards and receives STP BPDUs**;
> 	- **does not send or receive regular network traffic**: any traffic that arrives at the interfaces in the Listening state will be **dropped**;
> 	- **does not learn MAC addresses**.

After the Listening state, a Designated or Root port will enter the Learning state. 

>[!important]+ Learning
> - Only **Designated** or **Root ports** enter the Learning state: Non-Designated ports are always Blocking.
> - The Learning state is **15 seconds** by default. This is determined by the **Forward delay timer** (same as with Listening).
> - An interface in the Learning state:
> 	- **only sends and receives STP BPDUs**;
> 	- **does not send or receive regular network traffic**: any traffic that arrives at the interfaces in the Listening state will be **dropped**;
> 	- **does learn MAC addresses** from regular traffic that arrives on the interface.

Finally, having gone through Disabled, Listening, and Learning states, Designates and Root Ports enter the Forwarding state.

>[!important]+ Forwarding
> - **Root** and **Designated** ports are in a Forwarding state when they are **stable**.
> - A port in the Forwarding state operates as normal:
>     - sends and receives BPDUs
>     - sends and receives normal network traffic
>     - learns MAC addresses

>[!note]+ Disabled state
>There is also a **Disabled** state. This refers to the interface that is administratively disabled, i.e., shutdown. Such interface doesn't play any role in spanning tree.

Each of these states can be either **stable** or **transitional**:

 - **Stable** states: **Blocking** and **Forwarding**
	- Root and designated ports remain stable in a Forwarding state.
	- Non-designated ports remain stable in a Blocking state. 
	- Ports remain **stable** as long as there are **no changes in the network topology**. 

- **Transitional** states: **Listening** and **Learning**
	- **Transitional** states are passed through when an interface is activated, or when a Blocking port must transition to a Forwarding state due to a **change in the network topology**. 

| STP Port state | Forward/Receive BPDUs | Forward regular traffic | MAC address learning | Stable/Transitional |
| :------------: | :-------------------: | :---------------------: | :------------------: | :-----------------: |
|  **Blocking**  |        No/Yes         |           No            |          No          |       Stable        |
| **Listening**  |        Yes/Yes        |           No            |          No          |    Transitional     |
|  **Learning**  |        Yes/Yes        |           No            |         Yes          |    Transitional     |
| **Forwarding** |        Yes/Yes        |           Yes           |         Yes          |       Stable        |
|  **Disabled**  |         No/No         |           No            |          No          |       Stable        |


>[!note]+
>- A Forwarding interface can move directly to the Blocking state (there is no worry about creating a loop by blocking an interface).
>- A Blocking interface can't move directly to Forwarding state. It must go through the Listening and Learning states. 

## STP timers

| Timer             | Description                                                                                        | Default value                        |
| ----------------- | -------------------------------------------------------------------------------------------------- | ------------------------------------ |
| **Hello**         | How often the root bridge sends Hello BPDUs.                                                       | 2 seconds                            |
| **Forward delay** | How long the port will stay in the Listening and Learning states (each state 15 s = 30 s in total) | 15 seconds                           |
| **MaxAge**        | How long an interface will wait after ceasing to receive Hello BPDUs to change the STP topology.   | 10 * **Hello** <br>(e.g, 20 seconds) |

MaxAge:
- If another BPDU is **received before the MaxAge timer expires** (counts down to 0), **the time will reset** to 20 seconds and **no changes will occur**.
- If another BPDU is **not received**, the **MaxAge timer counts down to 0** and the **switch will re-evaluate its STP choices**, including root bridge, local root, designated, and non-designated ports.

>[!note] If a non-designated port is selected to become a designated or root port, it will transition:
>1. From the blocking state 
>2. To the listening state (15 seconds)
>3. To the learning state (15 seconds)
>4. To the forwarding state
>
> In total, it can take **50 seconds** for a blocking interface to transition to forwarding.

>[!note] The timers and transition states are to make sure that loops aren't accidentally created by an interface moving to forwarding state too soon.

>[!important] The STP timers on the root bridge determine the STP timers for the entire network. 

### PortFast
## Quiz

1. You connect a PC to a switch, however for about half a minute you are unable to connect to the network. Which two options could fix this issue and allow you to access the network more quickly? (Choose two. Each answer is a complete solution.)
	- a. Enable PortFast on the switch port you connect the PC to.
	- b. Reduce the STP Hello timer.
	- c. Reduce the STP forward delay timer.
	- d. Reduce the STP Max Age timer.


2. A packet capture indicates that a switch port has an STP port ID of `0x8002`. What is the STP port priority of this port?
	- a. `80`
	- b. `32`
	- c. `128`
	- d. `224`

3. You want to make sure that a Layer 2 loop will not be caused if a user connects a switch to a switch port. Which spanning tree optional features achieves this?
	- a. PortFast
	- b. Loop Guard
	- c. Root Guard
	- d. BPDU Guard

4. Boson ExSim. You want to decrease the amount of time that it takes for switch ports on `SW1` to begin forwarding. PortFast is not configured on any of the switch ports on `SW1`. You issue the `spanning-tree portfast default` command from global configuration mode. Which of the ports on `SW1` will use PortFast?
	- a. No ports, because PortFast cannot be enabled globally.
	- b. All trunk ports
	- c. All ports
	- d. All access ports

| Question | Answer      |
| -------- | ----------- |
| `1.`     | `a.`, `c .` |
| `2.`     | `c.`        |
| `3.`     | `d.`        |
| `4.`     | `d.`        |
