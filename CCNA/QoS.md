---
created: 2025-10-31 05:33:22
tags:
---
## IP phones and voice VLANs

- Traditional phones operate over **PSTN (Public Switched Telephone Network)**, sometimes called POTS (Plain Old Telephone Service).

>**IP phones** use **VoIP (Voice over IP)** technologies to enable phone calls over an IP network, such as the Internet.

>[!note] In VoIP, audio data is encapsulated in IP packets and sent over the network.

- IP phones are connected to a switch just like any other end host.
- IP phones have an internal 3-port switch: 
	- 1 port is **uplink**, which connects to an external switch.
	- 1 port is **downlink**, which connects to a PC.
	- 1 port connects internally to the **phone itself**.

- This allows the PC and the IP phone to connect to a single switch port. Traffic from the PC passes through the IP phone to the switch.

![[VoIP.svg]]

>[!note] It's recommended to separate voice traffic (from the IP phone) and data traffic (from the PC) by placing them in a separate VLAN — **voice VLAN**.
>- Traffic from the PC will be **untagged**, but traffic from the phone will be **tagged**.


Configuration:

1. Enter interface configuration mode:

```toml
SW1(config)# interface g0/0
```

2. Configure the port as access port:

```toml
SW1(config-if)# switchport mode access
```

3. Assign the port to a VLAN:

```toml
SW1(config-if)# switchport access vlan 10
```

4. Configure a voice VLAN:

```toml
SW1(config-if)# switchport voice vlan 11
```

>[!note] `PC1` will send its traffic untagged, as normal. `SW1` will use CDP to tell `PH1` to tag `PH1`'s traffic in VLAN `11`.

>[!important] The port on the switch is configured as **access port**.
>Although the interface sends and receives traffic from two VLANs (normal VLAN and voice VLAN), it's **not considered a trunk port**. It's considered an **access port**.

- The `switchport voice vlan` command has four options:
	- `vlan-id`: sends voice traffic over the specified VLAN; a unique voice VLAN is created to carry voice traffic, whereas data traffic is carried over the native VLAN.
	- `dot1p`: sends voice traffic with a default 802.1p priority of `5` and uses VLAN `0`.
	- `untagged`: configures the IP phone to send both untagged voice traffic and untagged data traffic over the native VLAN.
	- `none`: default configuration on a switch; enables IP phone to send untagged voice traffic; no 802.1p or CoS.
- Each of the four options determines how the voice traffic will be encapsulated and whether the voice traffic will be carried over a unique voice VLAN or over the native VLAN.

>[!note] The `vlan-id`, **`dot1p`**, and **`untagged`** modes all use the special-case 802.1Q trunk that is automatically negotiated by DTP and CDP if a trunk is needed.

- To configure the switch so that voice traffic and data traffic are separated but **do not require a unique voice VLAN** to be created:

```toml
SW1(config-if)# switchport voice vlan qot1p
```
## QoS

>[!interesting]+ A bit a history and the reasons behind QoS
>- In the past, voice and data traffic used to use entirely **separate networks**:
>	- Voice traffic used the PSTN.
>	- Data traffic used the IP network (enterprise WAN, Internet, etc.).
>
>QoS wasn't necessary as the different kinds of traffic wouldn't compete for bandwidth.
>- In modern networks, IP phones, video traffic, regular data traffic, etc., typically all share the **same IP network**.
>- This saves costs and enables more advanced features for voice and video traffic, such as integration with collaboration software (e.g., Cisco WebEx, Microsoft Teams, etc.).
>- However, different kinds of traffic now have to **compete for bandwidth**.

>**QoS (Quality of Service)** is a set of technologies used to prioritize to certain types of network traffic in a network.

QoS is used to manage the following characteristics of network traffic:

- **Bandwidth**
    - The overall capacity of the link; measured in bits per second (Kbps, Mbps, Gbps, etc.).
    - With QoS, you can reserve a certain amount of link's bandwidth for specific kinds of traffic. 
    - For example, 20% for voice traffic, 30% for specific kinds of data traffic, and 50% for all other traffic. 

- **Delay**
	- **One-way delay** = the amount of time it takes traffic to go from source to destination.
    - **Two-way delay** = the amount of time it takes traffic to go from source to destination and return.

- **Jitter**
    - The variation in one-way delay between packets sent by the same application.
    - IP phones have a **jitter buffer** to provide a **fixed delay** to audio packets. However, if the jitter is too high, it will overrun the jitter buffer, and the audio quality will suffer.

- **Loss**
    - The percentage of packets that don't reach their destination.
    - This can be caused , for example, by faulty cables, or when a device's packet **queues** get full and the device starts discarding packets that can't fit into the queue..

>[!important]+ Standards recommended for acceptable interactive audio quality (e.g., phone call):
>- **One-way delay:** < 150 ms
>- **Jitter:** < 30 ms
>- **Loss:** < 1%
>
>If these standards aren't met, there could be a noticeable reduction in the quality of the phone call.

## Queues

>In a network device receives messages faster than it can forward them out of the appropriate interfaces, the messages are placed in a **queue**.

- By default, queued messages will be forwarded in a **FIFO (First In First Out)** manner.
- Messages will be sent in the order they're received.

### Tail drop and TCP global synchronization

>If the queue becomes **full**, new packets will be **dropped**. This is called **tail drop**.

- **Tail drop** is harmful because is leads to **TCP global synchronization**:

>[!note]+ A review of the TCP sliding window
> TCP hosts use the **sliding window** to increase and decrease the rate at which they send traffic as needed:
> - When a packet is dropped, it will be re-transmitted.
> - When a drop occurs, the sender will **reduce the rate at which it sends traffic**. 
> - It will then gradually increase the rate again.

- When the queue fills up and tail drops occur, all TCP hosts sending traffic will **slow down the rate at which they send traffic at the same time**. 
- They will all then increase the rate again, which rapidly leads to more congestion, dropped packets, and the process repeats again
- This will create **waves** of the network being **underutilized** when devices slow down the rate, and then **congested** when devices all increase the rate of transmission.

A solution to prevent tail drop and TCP global synchronization is **Random Early Detection (RED)**.
### RED and WRED

>**Random Early Detection (RED)** is a congestion avoidance mechanism monitors the average queue length and **randomly drops** or marks incoming packets before the the queue becomes full.

- When the amount of traffic in the queue reaches a certain threshold, the device will start randomly dropping packets from selected TCP flows.
- These TCP flows will reduce the rate at which traffic is sent, but global TCP synchronization won't happen, since all other TCP flows will send traffic at their normal rate.

In standard RED, all kinds of traffic are treated the same. But there's also WRED. 

>**Weighted Random Early Detection (WRED)** is an improved version of RED that allows you to control which packets are dropped depending on the traffic class.

## Classification

- The purpose of QoS is to give certain kinds of network traffic priority over others during congestion.
- **Classification** organizes network traffic (packets) into traffic classes (categories).
- Classification is fundamental in QoS. To give priority to certain types of traffic, you have to identify which types of traffic to give priority to. 

>**QoS traffic classification** refers to the process of grouping network traffic into categories or classes based on specific criteria.

- There are many ways to classify traffic. For example:
	- **[[ACLs]]**. Traffic permitted by the ACL will be given certain treatment, other traffic will not. Like in [[NAT]].
	- **NBAR** (Network Based Application Recognition) performs **peed packet inspection (DPI)**, looking beyond the Layer 3 and Layer 4 information up to Layer 7 to identify the specific kind of traffic. 

Layer 2 and Layer 3 headers have specific fields used for the purpose of traffic classification:

- **802.1Q PCP** (Layer 2)
	- The **PCP (Priority Code Point)** field of the 802.1Q tag (in the Ethernet header) can be used to identify high/low-priority traffic. 
	- See [[VLANs]] 

- **IPv4 DSCP** (Layer 3)
	- The **DSCP (Differentiated Services Code Point)** field of the IPv4 header can also be used to identify high/low-priority traffic.
	- See [[IPv4_packet]]

### PCP/CoS

>**Priority Code Point (PCP)**, aka **Class of Service (CoS)**, is a 3-bit field within an 802.1Q tag, defined in IEEE 802.1p, that specifies traffic priority.

>[!warning] PCP can only be used when the VLAN tag is present.
>

The PCP traffic priority value ranges between `0` and `7`, inclusively:
- `0` — the lowest priority.
- `7` — the highest priority.

|PCP value|Traffic types|
|---|---|
|`0`|Best effort (default)|
|`1`|Background|
|`2`|Excellent effort|
|`3`|Critical applications|
|`4`|Video|
|`5`|Voice|
|`6`|Internetwork control|
|`7`|Network control|

>[!important]+ IP phones marking
>- IP phones **mark** signaling traffic (used to establish calls) as **PHP `3` (Critical applications)**.
>- The actual voice traffic is marked as **PCP `5` (Voice)**.

>[!note]+ Best effort delivery
>**Best effort** delivery means there is **no guarantee that data is delivered** or that it meets any QoS standard. This is **regular traffic**, not high-priority. 
>This is the default value.

>[!important] To **mark** the traffic means to set the value of the PCP or DSCP fields.

- The PCP value is typically set by the sender or originator of the traffic. 
- When a device sends a packet, it can assign a PCP value to indicate the desired priority level. 
- This PCP value is then used by intermediate network devices to determine the appropriate treatment for the packet.

>[!important] PCP can only be used over the following connections:
> - Trunk links
> - Access links with a voice VLAN

>[!note]+ Traffic types that **can't be marked with CoS**
> 
> - **Layer 3 headers**
>     - The **CoS marking is lost** when a frame travels over a non-802.1Q link or a Layer 3 network layer header.
> 
> - **Uncontrolled Ethernet frames**
>     - Frames that do not have an Ethernet header (e.g., some types of broadcast or multicast traffic) can't be marked with CoS.
> 
> - **LLDP and CDP traffic**
>     - LLDP and CDP packets can't be marked with CoS, as these are separate Layer 2 protocols that don't use Ethernet and, in turn, VLAN tags.
> 
> - **Trunking protocols other than 802.1Q**
>     - Traffic sent over trunking protocols other than 802.1Q, like **ISL**, can't be marked with CoS.
### IP ToS byte

In IPv4 header, there's a byte referred to as the **ToS** byte, **Type of Service**.

ToS consists of two fields:
- **DSCP (Differentiated Services Code Point)** — 6 bits
- **ECN (Explicit Congestion Notification)** — 2 bits

>[!note] IPv6 also has a byte called the **traffic class byte** used for QoS.

>[!interesting]+ Previously, ToS was organized differently
>- **IPP (IP Precedence)** — 3 bits = 8 values (`0`-`7`)
>- Defined by various sources, mostly unused ― 5 bits
>
>The standard IPP markings are similar to PCP:
>- `6` and `7` are reserved for *network control traffic* (e.g., OSPF messages).
>- `5` = voice
>- `4` = video
>- `3` = voice signaling
>- `0` = best effort
>
>With `6` and `7` reserved, 6 possible values remain.
>Although 6 values is sufficient for many networks, the QoS requirements of some networks demand more flexibility. 
### DSCP

>**DSCP (Differentiated Services Code Point)** is a 6-bit field within the IP header used by QoS to prioritize traffic on the Network Layer.

- [`RFC 2474`](https://datatracker.ietf.org/doc/html/rfc2474) defines the DSCP field, and other DiffServ RFCs elaborate on its use. 
- You should be aware of the following standard markings:

	- **Default Forwarding (DF)** — best-effort traffic.
	- **Expedited Forwarding (EF)** — low-loss/latency/jitter traffic (usually voice).
	- **Assured Forwarding (AF)** — a set of 12 standard values that gives assurance of delivery under prescribed conditions.
	- **Class Selector (CS)** — a set of 8 standard values to provide compatibility with the IPP field, previously used in ToS.

| DSCP field                | Value                |
| ------------------------- | -------------------- |
| DF (Default Forwarding)   | `0 0 0 0 0 0 ┊ x x`  |
| EF (Expedited Forwarding) | `1 0 1 1 1 0 ┊ x x`  |
| AF (Assured Forwarding)   | `c c c  d d 0 ┊ x x` |
| CS (Class Selector)       | `x x x 0 0 0 ┊ x x`  |

- [`RFC 4954`](https://datatracker.ietf.org/doc/html/rfc4954) was developed with the help of Cisco to bring all of the DSCP values together and standardize their use.

RFC offers many specific recommendations, but there are a few key ones:

- Voice traffic: **EF**
- Interactive video: **`AF4x`**
- Streaming video: **`AF3x`**
- High priority data: **`AF2x`**
- Best effort: **`DF`**

There are many more recommendations given within the RFC. However, in the end it’s up to the engineer designing the QoS policy of the network which traffic will get which markings. These are just standard recommendations.
#### DF (Default Forwarding)

- **DF (Default Forwarding)** is used for best-effort traffic.
- The DSCP marking for DF is `0`.

```
DF
0 0 0 0 0 0
```

#### EF (Expedited Forwarding)

- **EF (Expedited Forwarding)** is used for traffic that requires low-loss/latency/jitter, such as voice traffic.
- The DSCP marking for EF is `46`.

```
EF
1 0 1 1 1 0
```

#### AF (Assured Forwarding)
    
- **AF (Assured Forwarding)** defines 4 traffic classes. All packets in a class have the same priority.
- A higher class number means higher priority; these packets will be forwarded with better service than lower-priority packets.
- Within each class, there are 3 levels of drop precedence (high, medium or low).
    - Higher drop precedence = a packet is more likely to drop during congestion due WRED.

```
AF
| c c c ┊ d d 0 | x x
```

- The first three bits of the AF field represent the **class** of the traffic.
- The 4th and 5th bits of the AF field represent the **drop precedence**.
- The 6th bit of the AF field is always set to `0`.
- An AF value is written as `AFXY`, where `X` being the decimal number of the class, and `Y` being the decimal number of the drop precedence.

- Formula to convert from AF value to decimal DSCP value:
$$
\text{DSCP value} = 8X + 2Y 
$$

| AF     | DSCP    | Binary   |
| ------ | ------- | -------- |
| `AF11` | DSCP 10 | `001010` |
| `AF12` | DSCP 12 | `001100` |
| `AF13` | DSCP 14 | `001110` |
| `AF21` | DSCP 18 | `010010` |
| `AF22` | DSCP 20 | `010100` |
| `AF23` | DSCP 22 | `010110` |
| `AF31` | DSCP 26 | `011010` |
| `AF32` | DSCP 28 | `011100` |
| `AF33` | DSCP 30 | `011110` |
| `AF41` | DSCP 34 | `100010` |
| `AF42` | DSCP 36 | `100100` |
| `AF43` | DSCP 38 | `100110` |


| Drop  <br>precedence | Class 1                           | Class 2                           | Class 3                           | Class 4<br>(highest priority)     |
| :------------------- | :-------------------------------- | :-------------------------------- | :-------------------------------- | :-------------------------------- |
| Low                  | `AF11`  <br>DSCP 10  <br>`001010` | `AF21`  <br>DSCP 18  <br>`010010` | `AF31`  <br>DSCP 26  <br>`011010` | `AF41`  <br>DSCP 34  <br>`100010` |
| Medium               | `AF12`  <br>DSCP 12  <br>`001100` | `AF22`  <br>DSCP 20  <br>`010100` | `AF32`  <br>DSCP 28  <br>`011100` | `AF42`  <br>DSCP 36  <br>`100100` |
| High                 | `AF13`  <br>DSCP 14  <br>`001110` | `AF23`  <br>DSCP 22  <br>`010110` | `AF33`  <br>DSCP 30  <br>`011110` | `AF43`  <br>DSCP 38  <br>`100110` |

#### CS (Class Selector)

- **CS (Class Selector)** defines 8 DSCP values for backward compatibility with IPP.
- The 3 bits that were added for DSCP are set to `0`, and the original IPP bits are used to make 8 values.

```
CS
| x x x ┊ 0 0 0 |
```

## QoS trust boundaries

>A **QoS trust boundary** refers to the point in the network where the markings on packets is trusted.

- In other words, it is the interface or device where the network administrator decides to trust the QoS markings applied to traffic.
- The trust boundary defines where devices trust and don't trust the QoS markings of received messages.

>[!important]+ Trusted vs. not trusted
>- If the markings are **trusted**, the device will forward the message without changing the markings.
>- If the markings are **not trusted**, the device will change the markings according to the configured policy.

- If an IP phone is connected to the switchport, it is recommended to move the trust boundary to the IP phone, not directly on the phone itself.
- This is done via configuration on the switch port connected to the IP phone itself.
## Queuing and congestion management

- An essential part of QoS is the use of **multiple queues**.
- This is where classification plays a role. The device can match traffic based on various factors (such as DSCP marking) and then **place it in the appropriate queue**.

However, the device is only able to forward **one frame out of an interface at once**, so a **scheduler** is used to decide from which queue traffic is forwarded next.
- **Prioritization** allows the scheduler to give certain queues more priority than others.

>[!important]+ Weighted round-robin (WRR)
>
>A common scheduling method is **weighted round-robin (WRR)**.
> - **round-robin** = packets are taken from each queue in order, cyclically.
> - **weighted** = more data is taken from high priority queues each time the scheduler reaches that queue.
>
> In WRR, each queue or flow is assigned a **weight** that represents its allocated bandwidth.
>The scheduler serves the queues in a round-robin manner, and the number of packets that can be taken from a queue during each round-robin cycle is based on the weight of that queue.

>[!important]+ CBWFQ (Class-Based Weighted Fair Queuing)
>**CBWFQ (Class-Based Weighted Fair Queuing)** is a popular method of scheduling, using  WRR scheduler while while **guaranteeing each queue a certain percentage of the interface's bandwidth during congestion**.

> [!note]+ Let’s put these together. Here’s the process again:
> 1. Classify the traffic
> 2. Place it in queues
> 3. Schedule it
> 4. Transmit it
>
> The device is using a weighted round robin scheduler, sending a certain amount of traffic from each queue in cycles. On top of that, each queue gets a guaranteed minimum amount of bandwidth, even when the queues are congested.

>[!warning] Round-robin is not ideal for voice/video traffic.
>Even if the voice/video traffic receives a guaranteed minimum amount of bandwidth, round-robin can add **delay and jitter** because even high-priority queues have to wait their turn in the scheduler.  

To solve this, one can configure LLQ.
### LLQ

>**LLQ (Low-Latency Queuing)** designates one or more queues as *strict priority queues*.
    
- This means that if there is traffic in the queue, the scheduler will ***always* take the next packet from that queue until it is empty**.
    - As soon as traffic enters the priority queue, the scheduler will forward that traffic.
    - This is very effective for reducing the delay and jitter of voice and video traffic.

>[!warning] However, LLQ has the downside of potentially starving other queues if there is always traffic in the designated strict priority queue: the other queues might never get a turn to send traffic.

**Policing** can control the amount of traffic allowed in the strict priority queue so that it can't take all of the link's bandwidth.
### Shaping and policing

- Traffic shaping and policing are both used to control the rate of traffic.

>[!note] Previously, we assumed that the interfaces are operating **at their full capacity**, or beyond full capacity, which is why packets need to be queued. However, there are situations in which it is desirable to **limit the rate of traffic** to below the actual maximum capacity of the link.

>**Shaping** buffers traffic in a queue if the traffic rate goes over the configured rate.

>**Policing** drops traffic if the traffic rate goes over the configured rate. 

>[!note] Policing also has the option of re-marking the traffic instead of dropping it.

- *Burst* traffic over the configured rate is allowed for a short period of time.
- This accommodates data applications which are typically *bursty* in nature: instead of a constant steam of data, they send data in bursts.
- The amount of burst traffic allowed is configurable.

>[!note] In both cases, **classification** can be used to allow for different rates for different kinds of traffic.

>[!example]+
>- A customer router is connected to an ISP router.
>- The customer configures **shaping outbound traffic** on the customer router.
>- The ISP configures **policing inbound traffic** on the ISP router.