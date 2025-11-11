---
created: 2025-09-25 03:54:12
tags:
  - ethernet
---
## Switches

>A **switch** is a network device that primarily operates at **Layer 2 (Data Link layer)** of the OSI model. It forwards Ethernet **frames** based on the **MAC addresses** in the frame headers.

>[!note]+ Layer 3 switches 
>**Layer 3 switches**, also known as **multilayer switches**, combine Layer 2 switching functions with routing capabilities.
## Collision and broadcast domains

>A **collision domain** is a network segment where data packets can collide if two devices attempt to transmit data at the same time.

>[!warning] Network collisions often cause packet loss or corruption.

- Each switch port creates a **separate collision domain**.
- Modern switches use full-duplex communication and buffering, so **collisions are effectively eliminated**.

---

>A **broadcast domain** is a network segment where any broadcast frame sent by one device is received by all other devices in that segment.

>[!important] All devices connected to a switch normally share the same broadcast domain **unless VLANs are configured** (see [[VLANs]] for details).

- Routers separate broadcast domains; switches do not (by default).
## MAC address tables

>A **MAC address table**, aka **CAM table**, is a data structure stored in switch memory that maps MAC (Media Access Control) addresses of the connected devices to the corresponding switch ports.

- Switches use this table to decide which port to forward a frame to (and whether to forward it at all). 

>[!important]+ CAM
>**CAM (Content Addressable Memory)**, also known as **associative memory**, is refers to specialized high-speed memory optimized for fast MAC address lookups. 
>Switches use this type of memory store their MAC address table.

- To display a MAC address table on a Cisco switch:

```toml
SW1# show mac address-table
```

>[!example]+ Example: `show mac address-table`
>![[show_mac_address-table.png]]

>[!note] See [[MAC_addresses]].
## Switching decision logic

Each time a switch receives an Ethernet frame, it makes a **switching decision**: either to forward the frame out of certain ports (and what ports exactly), or ignore (drop) the frame.

- **Filtering**
	- If the destination MAC address maps to the same port the frame was received on, the frame is discarded (filtered).

- **Forwarding**
	- If the destination MAC is known and maps to a different port, forward the frame out that port.

- **Flooding**
	- 1. If the destination MAC address is unknown in the MAC address table, the frame is flooded to all ports except the receiving port (to discover the destination). This process is called **flooding**.

- **Broadcasting**
	- If the destination MAC address is a broadcast address (`ff:ff:ff:ff:ff:ff`), the frame is sent out all ports in the broadcast domain except the source port.

>[!important] When the switch is first plugged in, the MAC address table is empty: no destinations are known.
## MAC address learning

There are two main methods a switch uses to learn MAC addresses of the connected devices and build its MAC address table:

- Learning based on source MAC address of incoming frames
- Flooding unknown unicast frames to handle destination MAC addresses

>[!important] Known and unknown unicast
>- An **unknown unicast** is the frame whose destination MAC address is unknown to the switch.
>- A **known unicast** is the frame whose destination MAC address is already known to the switch, i.e., those destination MAC address is already in the MAC address table of that switch.
### Learning based on source MAC address

- When a switch receives an Ethernet frame on a specific port, it examines the **source MAC address** in the frame header.
- The switch checks if this source MAC address already exists in its **MAC address table**.
- If the source MAC address is **not present**, the switch **creates a new entry** in the MAC address table associating the MAC address with the port on which the frame arrived. 
- If the source MAC is **already in the table**, the switch **updates the entry's aging timer** to keep the record active and current.

>[!important] The switch inspects the **source MAC address** of each incoming frame and records this address along with the port on which the frame was received in its MAC address table.

### Handling destination MAC addresses: flooding unknown unicast frames

- When the switch receives a frame with an **unknown destination MAC address** (i.e., not in the MAC address table), the switch doesn't know where to forward the frame.
- To learn the destination MAC address, it uses **flooding**: sends the frame out of **all interfaces except the one it was received on**.
- All devices on the switched LAN segment receive the frame and check whether the destination MAC matches their own MAC address.
- The device with the matching MAC address responds, sending a frame back to the switch.
- This response allows the switch to **learn the destination MAC address** and update the MAC address table accordingly.
- Subsequent frames destined for that MAC address can be sent directly to the correct port (no flooding is needed anymore, since the address is already known).

>[!important] When a switch receives a frame the destination MAC address of which is not yet in the MAC address table, if uses the **flooding algorithm** to learn this MAC address.

----

>[!important]+ Dynamic MAC addresses
>MAC addresses learned by a switch from incoming frames or with flooding are called **dynamic MAC addresses**.

>[!important] By default, dynamic MAC addresses are removed from the MAC address table after **5 minutes (300 seconds)** of inactivity on Cisco switches. This is known as **Aging**.

### Clearing MAC address table

- To clear a MAC address table:

```toml
SW1# clear mac address-table
```

- To clear dynamic MAC addresses from a MAC address table:

```toml
SW1# clear mac address-table dynamic
```

>[!example] Example: `clear mac address-table dynamic`
>![[clear_mac_address-table_dynamic.png]]

- To clear dynamic MAC addresses for a specific addresses:

```toml
SW1# clear mac address-table dynamic MAC_ADDRESS
```

```toml
SW1# clear mac address-table dynamic 0001.647b.3119
```

- To clear dynamic MAC addresses for a specific interface:

```toml
SW1# clear mac address-table dynamic INTERFACE
```


```toml
SW1# clear mac address-table dynamic g0/0
```



>[!important] Arrival time 
>- To handle dynamic topologies, the arrival time of each frame is recorded and associated with the source MAC address of this frame. 
>- Whenever the switch receives another frame with an already known source MAC address, it **updates the arrival time** of that address in the MAC address table.
>- The expiry timer of that MAC address entry in the table, therefore, resets.
## Configuration

- To show information about switch interfaces:

```toml
SW1# show ip interface brief
```

>[!important]
>**Router** interfaces have the `shutdown` command applied by default.
>This means they will be in the `administratively down/down` state by default.
>---
>**Switch** interfaces do NOT have the `shutdown` command applied by default.
>This means they will be:
>- in the `up/up` state **if connected to another device**
>OR
>- in the `down/down` state **if not connected to another deivce**

- To show interface status:

```toml
SW1# show interface status
```

- To configure multiple interfaces at once:

```toml
SW1(config)# interface range f0/5 - 12
SW1(config-if-range)#

# the interface range may not be contiguous:
SW1(config)# int range f0/5 - 6, f0/9 - 12
```
### Speed

- To manually configure the speed at which the interface operates:

```toml
SW1(config-if)# speed ?
10    Force 10 Mbps operation
100   Force 100 Mbps operation
auto  Enable AUTO speed configuration
```

For example:

```toml
SW1(config-if)# speed 100
```

>[!important] Speed is configured automatically by default (auto-negotiated with the connected interfaces).

For example, in the output of `show interfaces status`, the `Speed` field set to `a-100` means the speed of `100` megabits per second was auto-negotiated.
### Duplex

- To manually set interface duplex:

```toml
SW1(config-if)# duplex ?
auto  Enable AUTO duplex configuration
full  Force full duplex operation
half  Force half-duplex operation
```

For example:

```toml
SW1(config)# duplex full
```

>[!important] Duplex is configured automatically by default (auto-negotiated with the connected interfaces).

For example, in the output of `show interfaces status`, the `Duplex` field set to `a-full` means the `full` duplex was auto-negotiated.

>[!important]
>- **Half-duplex**: the device **can't** send and receive data at the same time. If it is receiving a frame, **it must wait before sending a frame**.
>- **Full-duplex**: the device **can** send and receive data at the same time. It doesn't have to wait.
>
>In modern networks that use switches, all devices can use **full duplex** on their devices.

#### About connection speed

>**Connection speed** is the rate at which data can be transferred over a network or Internet connection.

- It is measured in **bits per second (bps)**, commonly expressed in kilobits (Kbps), megabits (Mbps), or gigabits per second (Gbps).
- Network interfaces, internet connections, and devices support different maximum speeds (e.g., 100 Mbps, 1 Gbps).

>[!important] Speed often refers to **bandwidth**, the maximum capacity of the connection channel.

---

- Most consumer ISPs provide **asymmetric connections**, meaning **download speeds are higher than upload speeds**. This is because a typical user downloads more data (websites, videos) than uploads.
- Upload speed is crucial for applications like:
    - Video conferencing (Zoom, Teams)
    - Online gaming (sending commands)
    - Cloud backups and file sharing
    - Streaming your own video content
- Upload speed tends to be smaller on residential plans but can be symmetric for business or fiber plans.

---

| Use Case                  | Download Speed       | Upload Speed     | Notes                                                                                                                |
| ------------------------- | -------------------- | ---------------- | -------------------------------------------------------------------------------------------------------------------- |
| Basic web browsing, email | 1-5 Mbps             | N/A              | Minimal bandwidth required                                                                                           |
| HD video streaming        | 5-10 Mbps per stream | N/A              | Multiple streams aggregate speed                                                                                     |
| 4K video streaming        | 25+ Mbps per stream  | N/A              | Higher bandwidth needed                                                                                              |
| Online gaming             | 3-6 Mbps             | 1-3 Mbps         | Low latency is often more important than speed                                                                       |
| Video conferencing        | 3-5 Mbps             | 1.5-3 Mbps       | Upload speed is critical                                                                                             |
| Home with multiple users  | 50-100 Mbps total    | 10-20 Mbps       | Total bandwidth should be aggregate of all expected traffic; e.g., family of 4 streaming + gaming may need 50+ Mbps. |
| Business/office           | 100+ Mbps            | Symmetric upload | Fiber and high-speed uplinks                                                                                         |


>Connection speed suitable for offices/businesses
- Shared internet: Bandwidth aggregates for all employees.
- Remote working with many video calls: Symmetric upload/download of 50-100 Mbps or more preferred.
- Cloud service access, backups: Fast upload critical; direct fiber with 100 Mbps+ upload common.
- Enterprise LAN speed (switch ports): Typically 1 Gbps or higher, often multiple aggregated links.

