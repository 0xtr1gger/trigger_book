---
created: 2025-10-09 04:14:14
tags:
  - stp
  - LAN_protocols
---
## Types of STP 

- **STP (Spanning Tree Protocol) — IEEE 802.1D**
	- The original STP.
	- All VLANs share one STP instance.
	- No load-balancing.

- **PVST+ (Per VLAN Spanning Tree Plus) — Cisco Proprietary**
	- Cisco's upgrade to 802.1D.
	- Each VLAN has its own STP instance.
	- Can load-balance by blocking different ports in each VLAN.

- **RSTP (Rapid Spanning Tree Protocol) — IEEE 802.1w**
	- Much faster convergence than 802.1D.
	- All VLANs share one STP instance.
	- No load-balancing.

- **Rapid PVST+ (Rapid Per VLAN Spanning Tree Plus) — Cisco Proprietary**
	- Cisco's upgrade to 802.1w.
	- Each VLAN has its own STP instance.
	- Can load-balance by blocking different ports in each VLAN.

- **MSTP (Multiple Spanning Tree Protocol) — IEEE 802.1s**
	- Uses modified RSTP mechanism. 
	- Can group multiple VLANs into different instances to perform load-balancing.


| Feature                | STP (802.1D)                                        | PVST+ (Cisco)             | RSTP (802.1w)                       | Rapid PVST+ (Cisco)       | MSTP (802.1s)              |
| ---------------------- | --------------------------------------------------- | ------------------------- | ----------------------------------- | ------------------------- | -------------------------- |
| Standard               | IEEE 802.1D                                         | Cisco Proprietary         | IEEE 802.1w                         | Cisco Proprietary         | IEEE 802.1s                |
| Instances              | Single (all VLANs)                                  | Per VLAN                  | Single (all VLANs)                  | Per VLAN                  | Multiple (groups of VLANs) |
| Convergence Speed      | Slow (30-50 sec)                                    | Slow                      | Fast (<10 sec)                      | Fast                      | Fast                       |
| Port Roles             | Root, Designated, Non-Designated                    | Same as STP               | Root, Designated, Alternate, Backup | Same as RSTP              | Same as RSTP               |
| Port States            | Blocking, Listening, Learning, Forwarding, Disabled | Same as STP               | Discarding, Learning, Forwarding    | Same as RSTP              | Same as RSTP               |
| Load Balancing         | No                                                  | Yes (per VLAN)            | No                                  | Yes (per VLAN)            | Yes (per instance)         |
| Backward Compatibility | N/A                                                 | Compatible with STP       | Compatible with STP                 | Compatible with RSTP      | Compatible with RSTP       |
| Resource Usage         | Low                                                 | High (many instances)     | Medium                              | High                      | Medium to High             |
| Default Cisco Mode     | No                                                  | Default on older switches | No                                  | Default on newer switches | Optional                   |
>[!important] MSTP, RPVST+, and RSTP are all backward-compatible with STP.

| Spanning Tree                         | Acronym     | Standard                           | Description                                                                                                                                                                                   |
| ------------------------------------- | ----------- | ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Spanning Tree Protocol                | STP         | 802.1D                             | ⬡ The original STP<br>⬡ All VLANs share one STP instance<br>⬡ Cannot load balance<br>⬡ Up to 50 seconds to respond to changes in the network                                                  |
| Per-VLAN Spanning Tree Plus           | PVST+       | Cisco proprietary                  | ⬡ Cisco's upgrade to 802.1D<br>⬡ Each VLAN has its own STP instance<br>⬡ Can load balance by blocking different ports in each VLAN<br>⬡ Up to 50 seconds to respond to changes in the network |
| Rapid Spanning Tree Protocol          | RSTP        | 802.1w (initially)<br>802.1Q (now) | ⬡ Much faster at converging/adapting to network changes than 802.1D<br>⬡ All VLANs share one STP instance<br>⬡ Cannot load balance                                                            |
| Rapid Per-VLAN Spanning Tree Plus<br> | Rapid RVST+ | Cisco proprietary<br>              | ⬡ Cisco's upgrade to 802.1w<br>⬡ Each VLAN has its own STP instance<br>⬡ Can load balance by blocking different ports in each VLAN<br>                                                        |
| Multiple Spanning Tree Protocol       | MSTP        | 802.1s                             | ⬡ Uses modified RSTP mechanics.<br>⬡ Can group multiple multiple VLAN instances to perform load balancing.                                                                                    |

>[!important]+ PVST vs. PVST+
>- PVST   = only ISL trunk encapsulation
>- PVST+ = supports 802.1Q

>[!important] Regular STP (not Cisco's PVST+) uses a destination MAC address of `0180.c200.0000`.

## RSTP

>[!quote] Cisco's summary:
>RSTP is not a timer-based spanning tree algorithm like 802.1D.
>- RSTP offers an improvement over the 30 seconds or more that 802.1D takes to move a list to forwarding.
>- The heart of the protocol is a new bridge-to-bridge handshake mechanism, which allows ports to move directly to forwarding.

>**RSTP (Rapid Spanning Tree Protocol)** is an evolution of STP. 
- RSTP is defined in **IEEE 802.1Q**.

>[!note] Similarities between RSTP and STP:
> 
> - RSTP serves the **same purpose** as STP, blocking specific ports to prevent Layer 2 loops. 
> - RSTP elects a **root bridge** with the same rules as STP.
> - RSTP elects **root ports** with the **same rules** as STP.
> - RSTP elects **designated ports** with the **same rules** as STP.

>[!important] Differences between RSTP and STP:
> 
> - RSTP has **faster convergence** time than STP (usually withing a few seconds).
> ---
> - New port state: **Discarding** (merges Listening, Blocking, and Disabled states from STP).
> ---
> - RSTP adds two more port types: 
> 	- **Alternate**
> 	- **Backup**
> ---
> - RSTP updates the way interface costs are calculated.
> ---
> - In STP, only the root switch generates and sends Hello BPDUs, and non-root switches replay them. **In RSTP, each switch can generate its own Hello BPDUs.**
> ---
> - Switches 'age' the BPDU information much more quickly. In classic STP, a switch waits 10 Hello intervals (20 seconds), but in Rapid STP, a switch considers a neighbor lost if it misses **3 BPDUs (6 seconds)**. When the neighbor on some interface is dead, a switch will flush all MAC addresses learned on that interface. 
### RSTP Cost

In RSTP, the path cost is calculated by the formula: $$\frac{20\ Tbit/s}{bandwidth}$$

|  Speed   | STP Cost |  RSTP Cost  |
| :------: | :------: | :---------: |
| 10 Mbps  |  `100`   | `2,000,000` |
| 100 Mbps |   `19`   |  `200,000`  |
|  1 Gbps  |   `4`    |  `20,000`   |
| 10 Gbps  |   `2`    |   `2,000`   |
| 100 Gbps |   `x`    |    `200`    |
|  1 Tbps  |   `x`    |    `20`     |

### RSTP port states

**RSTP port states:**

| STP Port state |           Forward/Receive <span style="color:#7BC1DF">BPDUs</span>            | Forward <span style="color:#7BC1DF">regular traffic</span> | <span style="color:#7BC1DF">MAC address</span> learning | Stable/Transitional |
| :------------: | :---------------------------------------------------------------------------: | :--------------------------------------------------------: | :-----------------------------------------------------: | :-----------------: |
|   Discarding   |                   No/<span style="color:#7BC1DF">Yes</span>                   |                             No                             |                           No                            |       Stable        |
|    Learning    | <span style="color:#7BC1DF">Yes</span>/<span style="color:#7BC1DF">Yes</span> |                             No                             |         <span style="color:#7BC1DF">Yes</span>          |    Transitional     |
|   Forwarding   |                    <span style="color:#7BC1DF">Yes</span>                     |           <span style="color:#7BC1DF">Yes</span>           |         <span style="color:#7BC1DF">Yes</span>          |       Stable        |

**STP port states:**

| STP Port state |           Forward/Receive <span style="color:#7BC1DF">BPDUs</span>            | Forward <span style="color:#7BC1DF">regular traffic</span> | <span style="color:#7BC1DF">MAC address</span> learning | Stable/Transitional |
| :------------: | :---------------------------------------------------------------------------: | :--------------------------------------------------------: | :-----------------------------------------------------: | :-----------------: |
|    Blocking    |                   No/<span style="color:#7BC1DF">Yes</span>                   |                             No                             |                           No                            |       Stable        |
|   Listening    | <span style="color:#7BC1DF">Yes</span>/<span style="color:#7BC1DF">Yes</span> |                             No                             |                           No                            |    Transitional     |
|    Learning    | <span style="color:#7BC1DF">Yes</span>/<span style="color:#7BC1DF">Yes</span> |                             No                             |         <span style="color:#7BC1DF">Yes</span>          |    Transitional     |
|   Forwarding   | <span style="color:#7BC1DF">Yes</span>/<span style="color:#7BC1DF">Yes</span> |           <span style="color:#7BC1DF">Yes</span>           |         <span style="color:#7BC1DF">Yes</span>          |       Stable        |
|    Disabled    |                                     No/No                                     |                             No                             |                           No                            |       Stable        |
### RSTP port roles

**RSTP port roles:**

- **Root port**
	- ⬡ Unchanged in RSTP.
	- ⬡ The port closest to the root bridge becomes the root port for the switch.
	- ⬡ The root bridge is the only switch that doesn't have a root port.

- **Designated port**
	- ⬡ Unchanged in RSTP.
	- ⬡ The port on a segment (collision domain) that sends the best BPDU is that segments's designated port (only per segment).

- **Alternate port**
	- ⬡ A **discarding** port that receives a superior BPDU from another switch.
	- ⬡ **Same as for blocking ports** in classic STP.
	- ⬡ Functions as a **backup to the root port**.
	- ⬡ If the root port fails, the switch can immediately move its best alternate port to the forwarding state. 
	- ⬡ This immediate move to forwarding state functions like classic STP optional feature called **UplinkFast**, but it is built into RSTP and there's no need to activate it manually.  

- **Backup port**
	- ⬡ A **discarding** port that receives a superior BPDU from another interface on the same switch. 
	- ⬡ This only happens when two interfaces are connected to the same collision domain (via a **hub**).
	- ⬡ Hubs are not used in modern networks, so **you will probably not encounter an RSTP backup port**. 
	- ⬡ Functions as a backup for designated port.
	- ⬡ The interface with the lowest port ID will be selected as the designated port, and the other will be the backup port.


>[!important] Non-designated port has been divided into two separate roles:
> - **Alternate** port
> - **Backup** port
 
>[!note] One more STP optional feature that was built into RSTP is **BackboneFast**.

RSTP example:

![[RSTP_example.png]]

- [Source](https://www.youtube.com/watch?v=EpazNsLlPps&list=PLxbwE86jKRgMpuZuLBivzlM8s2Dk5lXBQ&index=45).

| RSTP Port Roles | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | STP Port Roles      |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- |
| Root port       | ⬡ Unchanged in RSTP.<br>⬡ The port is the closes to the root bridge becomes the root port for the switch.<br>⬡ The root bridge is the only switch that doesn't have a root port.                                                                                                                                                                                                                                                                                                   | Root port           |
| Designated port | ⬡ Unchanged in RSTP.<br>⬡ The port on a segment (collision domain) that sends the best BPDU is that segments's designated port (only per segment).                                                                                                                                                                                                                                                                                                                                 | Designated port     |
| Alternate port  | ⬡ A discarding port that receives a superior BPDU from another switch.<br>⬡ This is the same as for blocking ports in classic STP.<br>⬡ Functions as a backup to the root port.<br>⬡ If the root port fails, the switch can immediately move its best alternate port to forwarding. <br>⬡ This immediate move to forwarding state functions like classic STP optional feature called UplinkFast, but it is built into RSTP and there's no need to activate it manually.            | Non-designated port |
| Backup port     | ⬡ A discarding port that receives a superior BPDU from another interface on the same switch. <br>⬡ This only happens when two interfaces are connected to the same collision domain (via a hub).<br>⬡ Hubs are not used in modern networks, so you will probably not encounter an RSTP backup port.<br>⬡ Functions as a backup for designated port.<br>⬡ The interface with the lowest port ID will be selected as the designated port, and the other will be the backup port.<br> | Non-designated port |


### RSTP BPDU

- Most of BPDU remains unchanged compared to the STP BPDU, but there are some differences:

1. Protocol versions:
	- **STP:**
		- Protocol Identifier: Spanning Tree Protocol (`0x0000`)
		- Protocol Version Identifier: Spanning Tree (`0`)
		- BPDU Type: Configuration (`0x00`)

	- **RSTP:**
		- Protocol Identifier: Spanning Tree Protocol (`0x0000`)
		- Protocol Version Identifier: Rapid Spanning Tree (`2)
		- BPDU Type: Rapid/Multiple Spanning Tree (`0x02`)

2. Flags
	- The Classic STP BPDU uses only two bits of the BPDU flags, the **1st** and the **8th** bit.
	- The RSTP uses **all 8 bits** of the BPDU flags. 
	- Flags are used in the negotiation process that allows rapid STP to converge much faster than classic STP. 

### RSTP link types

RSTP distinguishes between three different link types:

- Edge 
	- A port connected to an **end host**. 
	- Moves directly to the **forwarding** state, **without negotiation**.
	- Functions like a classic STP port with **PortFast** enabled. 

```toml
SW1(config-if)# spanning-tree portfast
```

>Edge ports connected to end hosts will still be point-to-point links if they are using full duplex.

>Ports connected to hubs that only connect to end host also should be edge ports. The hub basically doesn't exist in terms of spanning tree. 

- Point-to-point
	- A direct connection between two switches. 
	- Functions in full-duplex mode.
	- Detected automatically, without manual configuration

```toml
SW1(config-if)# spanning-tree link-type point-to-point
```

- Shared
	- Connection to a hub. 
	- Must operate in half-duplex.
	- Detected automatically, without manual configuration

```toml
SW1(config-if)# spanning-tree link-type shared
```

## Configuration

- Configure STP mode:

```toml
SW1(config)# spanning-tree mode ?

```

## Lab

Your company's network includes two Cisco switches, `SwitchA` and `SwitchB`.  
  
`SwitchB` has been configured to participate in a VTP domain named **`boson`** with the password **`NetSimX`**. `SwitchB` has also been configured with the correct trunk and EtherChannel settings.  
  
`SwitchA` is being repurposed from a previous installation and must be reconfigured.  
  
Configure `SwitchA` with the following parameters:  
- Configure `SwitchA` to participate in the same VTP domain as `SwitchB`, and ensure that changes can be made to the VLAN configuration of `SwitchA` directly from the command line.

```toml
SwitchA(config)# vtp mode server
SwitchA(config)# vtp domain boson
SwitchA(config)# vtp password NetSimX
```

- Configure switch ports `FastEthernet 0/1` and `FastEthernet 0/2` to use a Cisco-proprietary EtherChannel negotiation protocol.

```toml
SwitchA(config)# int range f0/1 - 2
SwitchA(config-if-range)# channel-protocol pagp
```

- Configure switch ports `FastEthernet 0/1` and `FastEthernet 0/2` as members of EtherChannel port-group `1`, and ensure that they actively negotiate EtherChannel links.

```toml
SwitchA(config-if-range)# channel-group 1 mode desirable
```

- Configure the EtherChannel virtual interface to establish a trunk link with `SwitchB`, and ensure that the link uses a standards-based encapsulation protocol.

```toml
SwitchA(config-if-range)# int po1
SwitchA(config-if)# switchport trunk encapsulation dot1q
SwitchA(config-if)# switchport mode trunk
```

- Ensure that DTP is disabled on the EtherChannel virtual interface.

```toml
SwitchA(config-if)# switchport nonegotiate
```

![[topology_boson.png]]