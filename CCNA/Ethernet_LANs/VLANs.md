---
created: 2025-10-04 04:40:01
tags:
  - ethernet
---

## A note on LANs

>A **LAN (Local-Area Network)** is a network that connects devices within a limited geographical area, such as a single building or campus. It allows devices like computers, printers, and servers to communicate and share resources locally.

Another definition, a more specific one, sounds like this:

> A **LAN (Local-Area Network)** is a single **broadcast domain**.

>A **broadcast domain** is the group of devices which will receive a broadcast frame, a frame with destination MAC address `ffff.ffff.ffff`, sent by any of the members of that broadcast domain. 

See [[switching#Collision and broadcast domains]]
## VLANs

>A **VLAN (Virtual Local Area Network)** is a broadcast domain partitioned and isolated in a LAN at the data link layer. 

>[!important] VLANs segment a physical LAN into *multiple logical LANs*. 

- VLANs are configured on **switches** — they act as **Layer 2** isolation mechanism.

>[!important] No inter-VLAN frame forwarding
>A switch **will not forward any traffic between different VLANs**, including broadcast and unknown unicast traffic (since VLANs are separate broadcast domains). If you need to send a frame from one VLAN to another, you need a router.

- VLANs are configured on **per-interface** basis: some interfaces are placed into one VLAN, and some interfaces into another. Therefore, **a VLAN can be considered as a subset of switchports in an Ethernet LAN**.

- VLANs can spread across multiple switches, and each VLAN doesn't need to be contiguous. This means that once part of VLAN can be physically separate from another.

>[!important] VLANs defined on a switch are stored in a **VLAN table**. Each entry associates a VLAN with a list of interfaces that belong to that VLAN.

- To show VLAN table on a switch:

```toml
SW1# show vlan brief
```

```toml
VLAN Name                Status    Ports
---- ------------------  --------  --------------------------
1    default             active    Gi0/0, Gi0/1, Gi0/2, Gi0/3
                                   Gi1/0, Gi1/1, Gi1/2, Gi1/3
                                   Gi2/0, Gi2/1, Gi2/2, Gi2/3
                                   Gi3/0, Gi3/1, Gi3/2, Gi3/3
1002 fddi-default        act/unsup
1003 token-ring-default  act/unsup
1004 fddinet-default     act/unsup
1005 trnet-default       act/unsup
```

- `default` is the VLAN all interfaces are assigned by default. It's created automatically and can't be deleted.

>[!warning] Trunk ports are not displayed in the output of the `show vlan` command.
>- To display trunk ports, use the `show interfaces trunk` command. 

>[!important] Automatically-created VLAN
> Besides the default VLAN, Cisco switches automatically create 4 FDDI/Token Ring VLANs (`1002`-`1005`). They are legacy and unsupported; they can **neither be used nor deleted**:
> - `1002` — `fddi-default`
> - `1003` — `token-ring-default`
> - `1004` — `fddinet-default`
> - `1005` — `trnet-default`
>
>All these four VLANs are put in the `unsp` (unsupported) state; they were used for FDDI and Token ring, old technologies not used anymore.

>[!important] VLANs `1`, `1002`-`1005` exist by default and **can't be deleted**.

>[!note] The VLAN table doesn't contain any Layer 3 information. 


![[VLANs.png]]

>[!note]+ Why using VLANs?
> - **Traffic segmentation**
> 	- VLANs split a large physical network into smaller logical networks. Each VLAN is a **separate broadcast domain**.
> 	- This reduces the amount of broadcast traffic within each VLAN.
> - **Security**
> 	- VLANs isolate network segments. This can significantly reduce security risks: help contain malware propagation through the network, limit traffic sniffing, and reduce exposure to attack. 
> 	- It's possible to apply different security policies to each VLAN, such as ACLs (Access Control Lists), firewall, and intrusion detection. which provides a more granular control over the network.
> - **Logical grouping**
> 	- Devices can be grouped by function, project, or department regardless of physical location.
> - **Troubleshooting**
> 	- A failure domain is often bounded to a broadcast domain, and with isolated broadcast domains, it is easier to identify problems on the network.

## VLAN ports 

>[!important] A **VLAN** can be considered as a subset of switch ports on a network.

In a network with VLANs enabled, there are two types of switch ports:
- **Trunk ports** (= tagged ports)
- **Access ports** (= untagged ports)

**Trunk ports** connect switches, where each switch can be configured with one or more VLANs, while **access ports** connect end devices to switches.
### Access ports

>**Access ports**, also known as **untagged ports**, are switchports that belong to a single VLAN and are used to connect to *end devices* like PCs, printers, or IP phones. 

-  A switchport connected to an end host should enter **access mode** by default.

>[!important] Access ports carry traffic for a *single VLAN*.

To configure an access port manually:

1. Enter interface configuration mode:

```toml
SW1(config)# interface gigabiteternet 0/1
SW1(config-if)#
```

2. Change port mode to `access`:

```toml
SW1(config-if)# switchport mode access
```

3. Assign the port to a VLAN:

```toml
SW1(config-if)# switchport access vlan 10
```

>[!important] If the VLAN you're assigning a switchport to doesn't yet exist on a switch, it will be created automatically.

5. Exit interface configuration:

```toml
SW1(config-if)# exit
```


![[VLAN_access_trunk_ports.svg]]

### Trunk ports

>**Trunk ports**, also known as **tagged ports**, are used to connect switches to each other or to routers. Trunk ports carry traffic for *multiple VLANs* simultaneously.  

>[!important] Trunk ports add VLAN tags to frames (except for the native VLAN) so the receiving device knows which VLAN each frame belongs to.

>**VLAN trunking** allows switches to exchange traffic from multiple VLANs over a single physical link, called a **trunk link**, or just **trunk**.

>[!note]+
>**Trunk ports don't "belong" to a VLAN the way access ports do**. Instead, they're configured to allow specific VLANs to pass through them. You can restrict which VLANs are allowed on a trunk using the allowed VLAN list.

To configure a trunk port:

1. Enter interface configuration mode:

```toml
SW1(config)# interface gigabiteternet 0/1
SW1(config-if)#
```

2. Change port mode to `trunk`:

```toml
SW1(config-if)# switchport mode trunk
```

3. Configure VLANs allowed on the trunk port:

```toml
SW1(config-if)# switchport trunk allowed vlan 10,20,30
```

4. (Optional) Configure a native VLAN for the trunk port:

```toml
# this sets VLAN 99 as the native VLAN instead of the default VLAN 1 
SW1(config-if)# switchport trunk native vlan 99
```

5. Exit interface configuration:

```toml
SW1(config-if)# exit
```

![[VLAN_trunking.svg]]


>[!note] VLANs without trunk ports
> It is possible to implement VLANs in a network without trunk ports and tagging. In this case, we would need to use a separate link and pair of ports for each VLAN the frames from which switches my need to transfer between each other:
> 
> ![[VLAN_no_trunking.svg]]
> 
> It might be a viable option in small networks, but it requires lots of switchports and links, and in larger networks, such implementation would just become impractical. Trunk ports allow us to use only one link between switches, no matter how many VLANs are configured on the network. 
## VLAN tagging

>To differentiate between VLANs on a trunk link, switches use **VLAN tagging**: each frame transmitted over a trunk includes a **VLAN tag** that identifies the VLAN it belongs to.

- The format of a VLAN tag is specified in a **trunking protocol**.

- There are two main trunking protocols:
	- ISL (Inter-Switch Link)
	- IEEE 802.1Q (dot1q or .1Q)

>[!Important] The **IEEE 802.1Q**, also known as **.1Q**, is an industry standard trunking protocol.

 >[!note] 
 >Before IEEE 802.1Q was defined, a Cisco-proprietary trunking protocol, **ISL (Inter-Switch Link)**, had been widely used. You are not likely to work with it today, but it still can sometimes be encountered on Cisco switches. 
### VLAN tag

>[!important] IEEE 802.1Q defines a 4-byte (32 bit) **VLAN tag**, inserted into an Ethernet header (between the Source MAC address and Type/Length field) of each frame sent over a trunk link. 

Below is a format of the .1Q VLAN tag:

![[VLAN_tag.svg]]

The tag consists of two main parts:

- **Tag Protocol Identifier (TPID)**: 16 bits
    - TPID is always set to `0x8100`; it indicates that the frame is 802.1Q-tagged.

- **Tag Control Information (TCI)**: 16 bits
	- **Priority Code Point (PCP)**: 3 bits
	    - PCP is used for **Class of Service (CoS)** to prioritize traffic.
	
	- **Drop Eligible Indicator (DEI)**: 1 bit
	    - DEI is used to indicate frames that can be dropped if the network is congested.
	
	- **VLAN identifier (VID)** 12 bits
		- The VID of the VLAN the frame belongs to.


| Field                          | Length  | Description                                                                                                                                 |
| ------------------------------ | ------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Tag Protocol Identifier (TPID) | 16 bits | Always set to `0x8100`; it indicates that the frame is 802.1Q-tagged.                                                                       |
| Tag Control Information (TCI)  | 16 bits | Consists of three sub-fields: <br>◌ PCP (Priority Code Point); 12 bits<br>◌ DEI (Drop Eligible Indicator); 1 bit<br>◌ VID (VLAN ID); 3 bits |

>[!important] A **VLAN ID (VID)** is a unique identifier assigned to each VLAN on a network.

### VLAN ID ranges

>[!important] Because the VID field is `12` bits, there are total  = `4096` possible VLANs, in range from `0` to `4095`. However, `0` and `4095` VLANs are reserved and can't be used. Therefore, **the actual usable range of VLANs is from `1` to `4094`**.

The range of VLANs (`1`-`4094`) is divided into two sections:

- **Normal range VLANs (`1`-`1005`)**
	- Stored in the `vlan.dat` file.
	- Can be configured in both VTP server and client modes.

- **Extended VLANs (`1006`-`4094`)**
	- Stored in the running configuration, not the file.
	- These VLANs require the switch to be in VTP transparent mode because VTP doesn't propagate extended range VLAN information.

>[!note] Some older devices can't use the extended VLAN range. However, it's safe to expect that modern switches will support the extended VLAN range.

>[!note] VLAN as numbers
>A VLAN, in fact, is simply a number between `1` and `4094`. Each switch port is always assigned to a specific VLAN number. Ports assigned to the same VLAN number are in the same broadcast domain.

>[!important] By default, all switchports on a Cisco switch are assigned to VLAN `1`.
## Configuring VLANs

1. Create a new VLAN and give it a name:

```toml
SW1(config)# vlan 10
SW1(config-vlan)# name ENGINEERING
SW1(config-vlan)# exit 
```


2. Configure access ports:

```toml
SW1(config)# interface gigabiteternet 0/1
SW1(config-if)# switchport mode access
SW1(config-if)# switchport access vlan 10
SW1(config-if)# exit
```

3. Configure trunk ports:

```toml
SW1(config)# interface gigabiteternet 0/1
SW1(config-if)# switchport mode trunk
SW1(config-if)# switchport trunk allowed vlan 10,20,30
SW1(config-if)# switchport trunk native vlan 99
SW1(config-if)# exit
```
 
4. Verity VLAN configuration:

```toml
SW1# show vlan brief
```

```toml
SW1# show interfaces gigabiteternet0/1 switchport
```

### Trunk configuration

- To configure an interface to use the trunk mode:

```toml
SW1(config)# interface g0/0
SW1(config-if)# switchport mode trunk
```

- `switchport mode` command options:

| Option              | Description                                                                                                                          |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `access`            | Always act as an access (non-trunk) port.                                                                                            |
| `trunk`             | Always act as a trunk port.                                                                                                          |
| `dynamic desirable` | Initiates negotiation messages and responds to negotiation messages to dynamically choose whether to start using trunking.           |
| `dynamic auto`      | Passively waits to receive trunk negotiation messages, at which point the switch will respond and negotiate whether to use trunking. |
To configure the VLANs allowed on a trunk:

```toml
# to show help
SW1(config-if)# switchport trunk allowed vlan ?
WORD
add
all
except
none
remove

WORD
# configures the list of allowed VLANs:
SW1(config-if)# switchport trunk allowed vlan 10,30

add 
# adds VLANs to the current list:
SW1(config-if)# switchport trunk allowed vlan add 20

remove
# removes a VLAN from the current list:
SW1(config-if)# switchport trunk allowed vlan remove 20

all 
# allows all VLANs:
SW1(config-if)# switchport trunk allowed vlan all

except 
# allow all VLANs except the specified ones:
SW1(config-if)# switchport trunk allowed vlan exept 1-5,10

none
# allow no VLANs at all; this effectively blocks all traffic from passing over the trunk:
SW1(config-if)# switchport trunk allowed vlan none
```

For actual configuration:

```toml
SW1(config-if)# switchport trunk allowed vlan 10,30
```

>[!note] Why to not just leave all VLANs to be allowed on a trunk, but specify only the few needed?
> - Security:
> 	- to make sure that only traffic in the necessary VLANs can use that connection.
> - Performance:
> 	- to avoid sending unnecessary traffic over the trunk.
### Encapsulation error

Sometimes the  `switchport mode trunk` command may result in the following error message:

```toml
Command rejected: An inteface whose trunk encapsulation is "Auto" can not be configured to "trunk" mode.
```

Most modern switch do not support ISL, but whose that support, have a trunk encapsulation of `Auto` by default. 

- To manually configure the interface as a trunk port, you must first set the encapsulation to 802.1Q:

```toml
SW1(config-if)# switchport trunk encapsulation dot1q
```

Once you set an encapsulation type, you can configure the interface as a trunk.

>[!note] This is not necessary on switches that only support 802.1Q.

## VLAN `show` commands

- To **display VLANs** that exist on a switch:

```toml
SW# show vlan brief
```

- Example output
	```toml
	SW1#show vlan brief  
	VLAN Name                        Status    Ports  
	---- --------------------------- --------- -------------------------------  
	1    default                     active    Gi0/1, Gi0/2  
	11   VLAN0011                    active    Fa0/1, Fa0/2, Fa0/3, Fa0/4  
	                                           Fa0/5, Fa0/6, Fa0/7, Fa0/8  
	                                           Fa0/9, Fa0/10  
	12   VLAN0012                    active    Fa0/11, Fa0/12, Fa0/13, Fa0/14  
	                                           Fa0/15, Fa0/16, Fa0/17, Fa0/18  
	                                           Fa0/19  
	14   VLAN0014                    active    Fa0/20, Fa0/21, Fa0/22, Fa0/23  
	                                           Fa0/24  
	<output omitted>
	```

- To display information about **all trunk port interfaces**:

```toml
SW1# show interfaces trunk
```

- Example output
	```toml
	Port   Mode   Encapsulation  Status    Native vlan
	Gi/0   on     802.1q         trunking  1
	
	Port   Vlans allowed on trunk
	Gi0/0  1-4094
	
	Port   Vlans allowed and active in management domain
	Gi0/0  1,10,30
	
	Port   Vlans in spannign tree forwarding state and not pruned
	Gi0/0  1,10,30
	```

- `Mode: on`
	- The interface has been manually configured for the trunk mode.
- `Vlans allowed on trunk: 1-4094`
	- By default, all VLANs, from `1` to `4094`, are allowed on the trunk.

>[!info] The **`show vlan brief`** command shows the *access ports* assigned to each VLAN, but not the trunk ports that allow each VLAN.
>Use the `show interfaces trunk` command instead to view trunk ports configuration.

The `show running-config` command is used to display the current running configuration of a Cisco device. This command is used to view the configuration information currently running on the terminal:

```toml
SW1# show running-config
```

## Inter-VLAN routing

For devices on different VLANs to communicate, routing is necessary.
There are two common techniques used for inter-VLAN routing:
- ROAS (Router On A Stick)
- Multilayer switch (see [[multilayer_switches]])
### ROAS

>**Router On A Stick (ROAS)**, aka **one-armed router**, is a router that has only one physical or logical connection to a network.

For devices on different VLANs to communicate, routing is necessary. For the purpose of inter-VLAN routing, a ROAS (Router On A Stick) can be configured. Physically, it is only connected to one network, the one where the VLANs are defined.

- A ROAS is only connected to a switch through an interface configured as a **trunk port**.

- The ROAS uses **subinterfaces**, with each subinterface assigned to a different VLAN. Each subinterface is a logical division of a physical interface dedicated for routing traffic for a single VLAN.

>[!note]+
>When a ROAS is used for inter-VLAN routing, traffic being routed between VLANs is first sent from one VLAN, from the switch, to the ROAS through one subinterface, then the ROAS receives and routes the frame back to the switch through another subinterface to the destination VLAN.

>[!note]+
>From the ROAS perspective, the interface connected to the switch is logically divided into several subinterfaces. From the switch's perspective, however, the interface is configured as a regular trunk port.

>[!warning] In a busy network, inter-VLAN traffic going through the ROAS can cause network congestion. For this reason, in large networks, the preferred method of inter-VLAN routing is a multi-layer switch.

Here is an example of how to configure ROAS:

```toml
R1(config)# int g0/0
R1(config-if)# no shutdown

R1(config-if)# int g0/0.10
R1(config-subif)# encapsulation dot1q 10
R1(config-subif)# ip address 192.168.1.62 255.255.255.192

R1(config-subif)# int g0/0.20
R1(config-subif)# encapsulation dot1q 20
R1(config-subif)# ip address 192.168.1.126 255.255.255.192

R1(config-subif)# int g0/0.30
R1(config-subif)# encapsulation dot1q 30
R1(config-subif)# ip address 192.168.1.190 255.255.255.192
```

>[!note]+
>The subinterface number does not have to match the VLAN number. However, it is highly recommended that they do match, to make it easier to understand and manage.

- Set a VLAN as native on a subinterface:

```toml
R1(config-if)# int g0/0.10
R1(config-subif)# encapsulation dot1q 10 native
```

- Delete a subinterface:

```toml
R1(config)# no interface g0/0.10
```
## Types of VLANs

### Data VLANs

>**Data VLANs** are used to carry regular user traffic. 

### Voice VLANs

>**Voice VLANs** are specifically designed to carry **Voice over IP (VoIP)** traffic from IP phones.

- The reason we separate voice traffic is quality of service — voice packets need priority treatment to avoid jitter and delay that would make conversations sound choppy. W
- hen you configure a voice VLAN, you're telling the switch to give special treatment to traffic from IP phones, often using Cisco's CDP or LLDP protocols to automatically detect and configure connected phones.

### Default VLAN

>The **default VLAN** is **always VLAN 1** on Cisco switches. It is the VLAN to which *all switch ports belong by default* when the switch is powered on.

- The default VLAN is often used to carry **management traffic**, such as control plane messages (e.g., CDP, STP, VTP, etc.).
- It is possible to change the default VLAN on a switch.

- It **cannot be renamed or deleted**; it is mandatory and always exists on the switch.
- The default VLAN is relevant primarily to **access ports** (ports connected to end devices).
- Best practice is to avoid using VLAN 1 for user data traffic to improve security.
### Management VLANs

>**Management VLANs** are used for administrative access to network devices. 

- By default, Cisco switches use **VLAN 1** as the management VLAN, but this is a security risk because VLAN `1` carries all untagged traffic. Best practice is to create a separate management VLAN, perhaps VLAN `99`, and use that for SSH or SNMP access to your switches.
### Native VLANs

> A **native VLAN** is a VLAN that is not tagged on a trunk port. 

In other words, frames received on a trunk port without a VLAN tag will be associated with the native VLAN.

- When a frame travels across a trunk link, it normally gets tagged with VLAN information. 
- However, one VLAN — the native VLAN — sends its frames *untagged* across the trunk. 

>By default, the native VLAN is **VLAN 1** on all trunk ports, but can be configured to any VLAN number.

**Key facts:**
- The Native VLAN is configured **per trunk port**.
- There can only be **one native VLAN per trunk port**. 

>In case of *native VLAN tags mismatch*, i.e., when the switch on one end of the trunk is configured with one native VLAN and the switch on the opposite end with another, the *receiving* switch *won't forward* such untagged frames at all. 

- To change the native VLAN *on an interface*:

```toml
SW1(config-if)# switchport trunk native vlan 10
```


## Flashcards

- What is a broadcast domain?
	- The set of devices that will receive a broadcast frame (destination MAC `ffff.ffff.ffff`) sent by any device in that domain.

- What is a VLAN?
	- Virtual Local Area Network — a broadcast domain partitioned and isolated at Layer 2, allowing multiple logical LANs on a single physical switch.

- What is stored in the VLAN table?
	- VLAN ID and associated switch ports. It does not contain Layer 3 info.

- What is an access port?
	- An untagged port assigned to a single VLAN, connecting end devices (computers, printers).

- How do you configure an access port?
	```toml
	SW1(config)# interface gigabiteternet 0/1
	SW1(config-if)# switchport mode access
	# assign the port to a VLAN
	SW1(config-if)# switchport access vlan 10
	SW1(config-if)# exit
	```

- What is a trunk port?
	- A port that carries traffic for multiple VLANs, adding VLAN tags to frames.

- How do you configure a trunk port?
	```toml
	SW1(config)# interface gigabiteternet 0/1
	# configure allowed VLANs
	SW1(config-if)# switchport trunk allowed vlan 10,20,30
	# set native VLAN (optional)
	## this sets VLAN 99 as the native VLAN instead of the default VLAN 1 
	SW1(config-if)# switchport trunk native vlan 99
	SW1(config-if)# exit
	```

- What is the purpose of a native VLAN?
	- It’s the VLAN whose frames are untagged on a trunk link.

- Why restrict allowed VLANs on a trunk?
	- For security and performance, limiting traffic to necessary VLANs.

- What's VLAN tagging?
	- The process of adding VLAN ID information to frames transmitted over a trunk link.

- What protocol is the industry standard for VLAN trunking?
	- IEEE 802.1Q

- What is the VLAN tag format in 802.1Q?
	- A 4-byte header inserted into Ethernet frames, consisting of TPID (`0x8100`) and TCI.

- What does TCI contain?
	- Priority Code Point (PCP), Drop Eligible Indicator (DEI), and VLAN ID (VID).

- What is the range of VLAN IDs?
	- 1-4094 (0 and 4095 are reserved).

- What are voice VLANs?
	- VLANs dedicated to carrying VoIP traffic, often with QoS prioritization.

- What is the default VLAN on Cisco switches?
	- VLAN 1, which carries management and normal data traffic.

- What are management VLANs?
	- VLANs dedicated to switch/router management traffic, ideally separate from VLAN 1 for security.

- What is a native VLAN?
	- The VLAN that sends untagged frames over a trunk link, default is VLAN 1.

- How do you create a VLAN and assign a name?
	```toml
	SW1(config)# vlan 10
	SW1(config-vlan)# name ENGINEERING
	SW1(config-vlan)# exit 
	```

- How to verify VLAN and trunk configurations?
	- `show vlan brief` — shows VLANs and assigned ports.
	- `show interfaces trunk` — shows trunk port status and allowed VLANs.

- What command reconfigures the encapsulation to dot1q if needed?
	- `switchport trunk encapsulation dot1q`

- How do you remove a subinterface on a router?
	- `no interface g0/0.[VLAN_ID]`

- What is ROAS?
	- ROAS (Router On A Stick) is a routing method where a single router interface with multiple subinterfaces handles inter-VLAN routing.

- You want VLAN 10 frames to go untagged over a trunk port. Which command?
	- `switchport trunk native vlan 10`

- Which command resets allowed VLANs to default?
	- `switchport trunk allowed vlan all`

- Trunk encapsulation command fix if rejected?
	- `switchport trunk encapsulation dot1q`

- VID
	- VLAN ID in VLAN tag

- Normal VLAN range
	- `1`-`1005`

- Extended VLAN range
	- `1006`-`4094`
## Quiz

1. You want to configure `SW1` to send VLAN 10 frames untagged over its `GigabitEthernet0/1` interface, a trunk port. Which command to use?  
	- a. `encapsulaton dot1q 10`  
	- b. `switchport trunk allowed vlan 10`
	- c. `switchport trunk allowed vlan add 10`  
	- d. `switchport trunk native vlan 10`  

2. After modifying the VLANs allowed on a trunk interface, you want to return it to the default state.  Which command will do this? 
	- a. `switchport trunk allowed vlan default`
	- b. `switchport trunk allowed vlan all` 
	- c. `switchport trunk allowed vlan none`
	- d. `switchport trunk allowed vlan 1 and 1001 to 1005`
  
3. You try to configure an interface on a Cisco switch as a trunk port with the command `switchport mode trunk`, but the command is rejected. Which command might fix this issue?  
	- a. `switch port mode trunk`
	- b. `switchport trunk encapsulation 802.1q`
	- c. `switchport trunk encapsulation dot1q`
	- d. `switchport trunk encapsulation auto`

4. Which field of the 802.1Q tag identifies the VLAN ID of the frame?  
	- a. TPID
	- b. VID  
	- c. TCI  
	- d. VLN
  
5. You configured switchport trunk allowed `vlan add 10` on an interface, but VLAN 10 doesn’t appear in the VLANs allowed and active in management domain section of the `show interfaces trunk` command output. What might be the reason?  
	- a. VLAN 10 doesn’t exist on the switch.  
	- b. the command is invalid
	- c. the command should be `switchport trunk allowed VLAN 10`
	- d. VLAN 10 is reserved

6. Which two answers are valid options too configure the native VLAN on a router in a ROAS configuration? (select the two best answers, each answer is a complete solution)

	- a.    `R1(config-if)# encapsulation dot1q 112`
		 `R1(config-if)# ip address 192.168.1.1 255.255.255.0`

	- b.    `R1(config-subif)# encapsulation dot1q 112 native`
	     `R1(config-if)# ip address 192.168.1.1 255.255.255.0`

	- c.    `R1(config-if)# ip address 192.168.1.1 255.255.255.0`
	
	- d.   `R1(config-subif)# switchport trunk native vlan 112`
         `R1(config-subif)# ip address 192.168.1.1 255.255.255.0`

| question | answer     |
| -------- | ---------- |
| `1.`     | `d.`       |
| `2.`     | `b.`       |
| `3.`     | `c.`       |
| `4.`     | `b.`       |
| `5.`     | `a.`       |
| `6.`     | `b.`, `c.` |



