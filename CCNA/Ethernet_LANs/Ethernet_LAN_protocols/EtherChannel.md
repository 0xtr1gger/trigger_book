---
created: 2025-10-11 04:32:00
tags:
  - ethernet
---
## The problem of oversubscription and multiple Ethernet links

>**Oversubscription** refers to the situation when the bandwidth of the interfaces connected to end hosts is greater than the bandwidth of the connection to the distribution switch(es).
 
>[!important] In other words, oversubscription is a situation when the **potential for bandwidth of a network exceeds the available bandwidth**.

![[oversubscription.svg]]

- Some oversubscription is acceptable, but too much will cause congestion.

To mitigate this problem and increase the amount of traffic that can pass between the switches, we can add more Layer 2 links between them. However, there is a problem: STP.

![[STP_blocks_ports_oversubscription.svg]]

- If you connect two switches together with multiple links, all except one will be disabled by spanning tree.

>[!important] No matter how many links connect two switches together, all except one will be disabled by STP to avoid Layer 2 loops. 

>[!note] See [[STP]].

**EtherChannel** can solve this problem by grouping multiple physical interfaces into one logical interface. As a result, STP will treat a group such interface as a **single interface**.
## EtherChannel

>**EtherChannel** is a technology used to bundle multiple physical Ethernet links into a single logical link, called a **port channel** or **channel group**.

>[!important] EtherChannel is also called **Port Channel** or **LAG (Link Aggregation Group)**.

- EtherChannel groups multiple interfaces together to act as a single interface.
- STP will treat this group as a single interface.

- On network diagrams, it's represented with a circle drown around EtherChannel member links:
![[EtherChannel.svg]]


>[!important]+ Traffic will be **load-balanced** among the physical interfaces in the EtherChannel group. 

- To show **port-channel statistics**:

```toml
SW1# show etherchannel port-channel
```

- To show the **status and configuration** of EtherChannel:

```toml
SW1# show etherchannel summary
```
### EtherChannel load-balancing 

Load-balancing in EtherChannel is based on **flows**.

>A **flow** is a communication between two nodes in the network. 

- Frames in the same flow will be forwarded over the same physical link in the EtherChannel group.

>[!note]+
>If frames in the same flow were forwarded over different physical links, some frames may arrive at the destination out of order, which can cause problems with certain protocols. This is why EtherChannel load-balancing is based on flows.

- The calculation used to determine which physical interface to use can take into account the following (and you can configure this):
	- **Source MAC address** (all frames with the same source MAC address will use the same physical interface)
	- **Destination MAC address**
	- **Source and destination MAC address**
	- **Destination IP address**
	- **Source and destination IP address**
	- **Source TCP/UDP port**
	- **Destination TCP/UDP port**
	- **Source and destination TCP/UDP port**

- To see the current load-balancing method:

```toml
SW1# show etherchannel load-balance
```

- To configure load-balancing method:

```toml
SW1(config)# port-channel load-balance ?
	dst-ip        Dst IP Addr
	dst-mac       Dst Mac Addr
	src-dst-ip    Src XOR Dst IP Addr
	src-dst-mac   Src XOR Dst Mac Addr
	src-ip        Src IP Addr
	src-man       Src Mac Addr
```

```toml
SW1(config)# port-channel load-balance src-dst-mac
```
## Configuration protocols

There are three main ways to configure EtherChannel on Cisco switches:

- **LACP (Link Aggregation Control Protocol)**
	- Industry standard protocol (IEEE 802.3ad).
	- LACP dynamically negotiates the creation/maintenance of the EtherChannel (like DTP does for trunks).

- **PAgP (Port Aggregation Protocol)**
	- Cisco-proprietary protocol.
	- PAgP dynamically negotiates the creation/maintenance of the EtherChannel (like DTP does for trunks).

- **Static EtherChannel**
	- Interfaces are statically configured to form an EtherChannel.
	- This is usually avoided.

>[!important] **LACP is the preferred method for configuring LACP.** 

- To configure EtherChannel:

```toml
SW1(config-if-range)# channel-group NUMBER mode MODE
```

```toml
SW1(config-if-range)# channel-group 1 mode ?
	active    Enable LACP unconditionally
	auto      Enable PAgP only if a PAgP device is detected
	desirable Enable PAgP unconditionally
	on        Enable Etherchannel only
	pasive    Enable LACP only if a LACP device is detected
```

>[!example]+ Configuring PAgP
> 
> ```toml
> SW1(config)# interface range g0/0 - 3
> SW1(config-if-range)# channel-group 1 mode desirable
> Creating a port-channel interface Port-channel 1
> ```
>>[!important]+ PAgP EtherChannel mode compatibility
>>- `auto` + `auto` = **no EtherChannel**
>>- `desirable` + `auto` = **EtherChannel**
>>- `desirable` + `desirable` = **EtherChannel** 

>[!important] The `on` mode only works with `on` mode.

>[!important]+ Channel group number
>- The channel-group number has to match for all member interfaces **on the same switch**.
>- However, it **doesn't have to match the channel-gorup number on the other switch**.

| Switch A/Switch B |              `off`               |              `auto`              |           `desirable`            |            `passive`             |             `active`             |               `on`               |
| :---------------: | :------------------------------: | :------------------------------: | :------------------------------: | :------------------------------: | :------------------------------: | :------------------------------: |
|     **`off`**     | <span style="color:red">✘</span> | <span style="color:red">✘</span> | <span style="color:red">✘</span> | <span style="color:red">✘</span> | <span style="color:red">✘</span> | <span style="color:red">✘</span> |
|    **`auto`**     | <span style="color:red">✘</span> | <span style="color:red">✘</span> |               PAgP               | <span style="color:red">✘</span> | <span style="color:red">✘</span> | <span style="color:red">✘</span> |
|  **`desirable`**  | <span style="color:red">✘</span> |               PAgP               |               PAgP               | <span style="color:red">✘</span> | <span style="color:red">✘</span> | <span style="color:red">✘</span> |
|   **`passive`**   | <span style="color:red">✘</span> | <span style="color:red">✘</span> | <span style="color:red">✘</span> | <span style="color:red">✘</span> |               LACP               | <span style="color:red">✘</span> |
|   **`active`**    | <span style="color:red">✘</span> | <span style="color:red">✘</span> | <span style="color:red">✘</span> |               LACP               |               LACP               | <span style="color:red">✘</span> |
|     **`on`**      | <span style="color:red">✘</span> | <span style="color:red">✘</span> | <span style="color:red">✘</span> | <span style="color:red">✘</span> | <span style="color:red">✘</span> |                On                |

- To manually configure EtherChannel negotiation protocol:

```toml
SW1(config-if-range)# channel-protocol ? 
	lacp    Prepare interface for LACP protocol
	pagp    Prepare interface for PAgP protocol
```

## LACP

>**LACP (Link Aggregation Control Protocol)** is the industry-standard protocol for dynamic link aggregation, defined in **IEEE 802.3ad** (later incorporated into **IEEE 802.3-2008**). It provides vendor-neutral interoperability and is supported by virtually all enterprise networking equipment manufacturers.

>[!important]+ **LACP supports up to 16 interfaces per channel group** (8 active, 8 standby).
> - LACP can group up to **16 interfaces** into a single EtherChanne.
> - Up to **8 interfaces** can be **active**; other interfaces (up to 8) will be **standby**, ready to take over in case an active interface fails.

>**Active links** are physical interfaces that are currently used to forward traffic in the EtherChannel.

>**Standby links** are interfaces configured as part of the Ethernet group but are not currently forwarding traffic. Standby links act as backups and become active only if an active link fails or is removed.

>[!note] The protocol selects which links are **active** members of the EtherChannel based on system and interface priorities.

>[!example]+ Configuring LACP
> 
> ```toml
> SW1(config)# interface range g0/0 - 3
> SW1(config-if-range)# channel-group 1 mode active
> Creating a port-channel interface Port-channel 1
> ```

>[!important]+ LACP EtherChannel mode compatibility
>- `passive` + `passive` = **no EtherChannel**
>- `active` + `passive` = **EtherChannel**
>- `active` + `passive` = **EtherChannel**

## EtherChannel interface configuration requirements

>[!important]+ EtherChannel interface configuration requirements
> 
> Member interfaces must have matching configuration:
> 
> - Same duplex
> 
> ```toml
> R1(config-if-range)# duplex full
> ```
> 
> - Same speed
> 
> ```toml
> R1(config-if-range)# speed 1000
> ```
> 
> - Same switchport mode (active/trunk) 
> - Same allowed VLANs and same native VLAN (for trunk interfaces)
> - Same port mode (access or trunk)

>[!warning] If an interface's configuration doesn't match the others, it will be excluded from the EtherChannel.

## Layer 3 EtherChannel

```toml
SW1(config)# int range g0/0 - 3
SW1(config-if-range)# no switchport
SW1(config-if-range)# channel-group 1 mode active
Creating a port-channel interface Port-channel 1
```

## EtherChannel lab: example configuration

`ASW1`:

- Show spanning tree:

```toml
ASW1# show spanning-tree
VLAN0001
  Spanning tree enabled protocol ieee
  Root ID    Priority    20481
             Address     0007.EC07.1D30
             Cost        8
             Port        25(GigabitEthernet0/1)
             Hello Time  2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    32769  (priority 32768 sys-id-ext 1)
             Address     0005.5E1E.5B9D
             Hello Time  2 sec  Max Age 20 sec  Forward Delay 15 sec
             Aging Time  20

Interface        Role Sts Cost      Prio.Nbr Type
---------------- ---- --- --------- -------- --------------------------------
Fa0/2            Desg FWD 19        128.2    P2p
Fa0/1            Desg FWD 19        128.1    P2p
Gi0/1            Root FWD 4         128.25   P2p
Gi0/2            Altn BLK 4         128.26   P2p  
```

- Configure both `G0/1` and `G0/2` together:

```toml
ASW1(config)# int range g0/1-2
ASW1(config-if-range)#
```

- Configure EtherChannel with the `channel-group` command:

```toml
ASW1(config-if-range)# channel-group 1 mode active
Creating a port-channel interface Port-channel 1
```

- This creates a new interface, `Po1` (`Port-channel1`):

```toml
ASW1(config-if-range)# do show int Po1

Port-channel1 is down, line protocol is down (disabled)
  Hardware is EtherChannel, address is 0090.0ce2.144c (bia 0090.0ce2.144c)
  MTU 1500 bytes, BW 2000000 Kbit, DLY 1000 usec,
     reliability 255/255, txload 1/255, rxload 1/255
  Encapsulation ARPA, loopback not set
  Keepalive set (10 sec)
  Half-duplex, 2000Mb/s
  input flow-control is off, output flow-control is off
  Members in this channel: 
  ARP type: ARPA, ARP Timeout 04:00:00
  Last input 00:00:08, output 00:00:05, output hang never
  Last clearing of "show interface" counters never
  Input queue: 0/75/0/0 (size/max/drops/flushes); Total output drops: 0
  Queueing strategy: fifo
  Output queue :0/40 (size/max)
  5 minute input rate 0 bits/sec, 0 packets/sec
  5 minute output rate 0 bits/sec, 0 packets/sec
     956 packets input, 193351 bytes, 0 no buffer
     Received 956 broadcasts, 0 runts, 0 giants, 0 throttles
     0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored, 0 abort
     0 watchdog, 0 multicast, 0 pause input
     0 input packets with dribble condition detected
     2357 packets output, 263570 bytes, 0 underruns
     0 output errors, 0 collisions, 10 interface resets
     0 babbles, 0 late collision, 0 deferred
     0 lost carrier, 0 no carrier
     0 output buffer failures, 0 output buffers swapped out
```

- To configure the port as a trunk, first enter its configuration mode:

```toml
ASW1(config-if-range)# int po1
ASW1(config-if)#
```

- Configure the port as a trunk:

```toml
ASW1(config-if)# switchport mode trunk
```

>[!note]+
>If you then issue the `show interfaces status` command, you will see that both `G0/1` and `G0/2` are configured as `trunk` interfaces:
>```toml
>ASW1(config-if)# do show int status
>```
>![[etherchannel_trunk.png]]

- Display EtherChannel summary:

```toml
ASW1(config-if)# do show etherchannel summary
Flags:  D - down        P - in port-channel
        I - stand-alone s - suspended
        H - Hot-standby (LACP only)
        R - Layer3      S - Layer2
        U - in use      f - failed to allocate aggregator
        u - unsuitable for bundling
        w - waiting to be aggregated
        d - default port


Number of channel-groups in use: 1
Number of aggregators:           1

Group  Port-channel  Protocol    Ports
------+-------------+-----------+----------------------------------------------

1      Po1(SD)           LACP   Gig0/1(D) Gig0/2(D) 
```

Then you basically do the same on the switch `DSW1`, but on interfaces `g1/0/3` and `g1/0/4`.

The full configuration looks like this:

```toml
DSW1(config)# do show spanning-tree

VLAN0001
  Spanning tree enabled protocol ieee
  Root ID    Priority    20481
             Address     0007.EC07.1D30
             Cost        4
             Port        1(GigabitEthernet1/0/1)
             Hello Time  2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    24577  (priority 24576 sys-id-ext 1)
             Address     0002.161B.EBBC
             Hello Time  2 sec  Max Age 20 sec  Forward Delay 15 sec
             Aging Time  20

Interface        Role Sts Cost      Prio.Nbr Type
---------------- ---- --- --------- -------- --------------------------------
Gi1/0/1          Root FWD 4         128.1    P2p
Gi1/0/2          Altn BLK 4         128.2    P2p
```

```toml
DSW1(config)# int range g1/0/1-2

DSW1(config-if-range)# channel-group 1 mode active
Creating a port-channel interface Port-channel 1
```

```toml
DSW1(config-if-range)# int po1
DSW1(config-if)# switchport mode trunk
DSW1(config-if)# do show etherchannel summary

Flags:  D - down        P - in port-channel
        I - stand-alone s - suspended
        H - Hot-standby (LACP only)
        R - Layer3      S - Layer2
        U - in use      f - failed to allocate aggregator
        u - unsuitable for bundling
        w - waiting to be aggregated
        d - default port

Number of channel-groups in use: 1
Number of aggregators:           1

Group  Port-channel  Protocol    Ports
------+-------------+-----------+----------------------------------------------

1      Po1(SD)           LACP   Gig1/0/1(I) Gig1/0/2(I) 
```
## Flashcards

- What is oversubscription?
	- A situation when the **potential for bandwidth of a network exceeds the available bandwidth**.

- What is another name for an EtherChannel logical link?  
	- Port channel or channel group.

- Name the three main methods to configure EtherChannel on Cisco switches.
	- LACP (Link Aggregation Control Protocol)
	- PAgP (Port Aggregation Protocol)
	- Static EtherChannel

- Which EtherChannel configuration protocol is preferred?  
	- LACP (Link Aggregation Control Protocol).

- How many interfaces can LACP group into a single EtherChannel?  
	- Up to 16 interfaces (8 active and 8 standby).

- What is the function of active and standby links in LACP?  
	- Active links forward traffic; standby links are backups that become active if an active link fails.

- Name at least four inputs used for EtherChannel load-balancing calculations.  
	- **Source MAC address** (all frames with the same source MAC address will use the same physical interface)
	- **Destination MAC address**
	- **Source and destination MAC address**
	- **Destination IP address**
	- **Source and destination IP address**
	- **TCP/UDP port numbers** (some switches)

- What physical interface attributes must match for interfaces to be in the same EtherChannel?  
	- Speed, duplex, port type (cannot mix `FastEthernet` and `GigabitEthernet` or copper and fiber).

- What VLAN-related settings must match for trunk interfaces in EtherChannel?  
	- Native VLAN, allowed VLANs, trunk encapsulation (all must match exactly).

- Can you mix access ports and trunk ports in the same EtherChannel group?  
	- No, mixing access and trunk ports is not allowed.

- What are some of the STP settings that must match on EtherChannel member interfaces?  
	- Port priority, path cost, and PortFast settings.

- What command shows the EtherChannel summary and status on a switch?  
	- `show etherchannel summary`

- What command displays EtherChannel port-channel statistics?  
	- `show etherchannel port-channel`

- How can you display the current EtherChannel load-balancing method?  
	- `show etherchannel load-balance`

- What command lists available EtherChannel load balancing methods on a device?  
	- `port-channel load-balance ?`

- Which protocol is incompatible with PAgP when configuring EtherChannel?  
	- LACP (they cannot interoperate).

- **Quiz** - Which of these channel-group mode combinations will form an EtherChannel?
	- a. on - on
	- b. passive - passive
	- c. desirable - auto
	- d. auto - auto
	- e. active - desirable
	- f. on - desirable    
	- g. active - active
- **Answer:** a, c, g

- What does the 'P' flag represent in `show etherchannel summary` output?  
	- The interfaces are bundled in the port-channel.

- **Quiz** - Which member parameters must match to form an EtherChannel? (Choose two)
	- Interface ID
	- IP address
	- Interface speed
	- Switchport mode (access/trunk)
- **Answer:** Interface speed, Switchport mode

- Given mismatched LACP and PAgP protocols on each side with static `mode on` command, what happens?  
	- No EtherChannel link is formed.

## Quiz

1. Which of the following `channel-group mode` combinations will result in an operational EtherChannel? (choose three)
	- a. `on` - `on`
	- b. `passive` - `passive`
	- c. `desirable` - `auto`
	- d. `auto` - `auto`
	- e. `active` - `desirable`
	- f. `on` - `desirable`
	- g. `active` - `active`

2. In the output of the `show etherchannel summary` command, you notice that the physical interfaces in the EtherChannel you configured have the flag (`P`) next to them. What does this mean?
	- a. The interfaces are in LACP passive mode.
	- b. The interfaces are bundled in the port-channel.
	- c. The interfaces are paused until the other switch’s EtherChannel is configured.
	- d. The EtherChannel is a Layer 2 EtherChannel.

3. Which of the following member interface parameters need to match to form an EtherChannel? (choose two)
	- a. Interface ID
	- b. IP address
	- c. Interface speed
	- d. Switchport mode (active/trunk)

4. Boson ExSim. You issue the following commands on Switch A and then on Switch B. Which of the following statements is true about the resulting EtherChannel link between Switch A and Switch B?
	- a. A link is formed using LACP because it was configured first and has priority.
	- b. No link is formed.
	- c. A link is formed using PAgP because it was configured last and has priority.
	- d. A link is formed without an aggregation protocol.

```toml
SwitchA(config)# interface port-channel 1
SwitchA(config-if)# interface range fastethernet 0/5 - 6
SwitchA(config-if-range)# channel-protocol lacp
SwitchA(config-if-range)# channel-group 1 mode on
```

```toml
SwitchB(config)# interface port-channel 1
SwitchB(config-if)# interface range fastethernet 0/5 - 6
SwitchB(config-if-range)# channel-protocol pagp
SwitchB(config-if-range)# channel-group 1 mode on
```

| Question | Answer           |
| -------- | ---------------- |
| `1.`     | `a.`, `c.`, `g.` |
| `2.`     | `b.`             |
| `3.`     | `c.`, `d.`       |
| `4.`     | `b.`             |
4. No link is formed. The last command, `channel-group 1 mode on`, will be rejected, as `lacp`/`pagp` have been manually configured on the interfaces. And since there are two different aggregation protocols on two sides of the EtherChannel, no link will be formed, since protocols must match. 


