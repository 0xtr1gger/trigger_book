---
created: 2025-10-18 05:34:04
tags:
  - routing
---
## OSPF 

>**OSPF (Open Shortest Path First)** is a **Link State IGP (Interior Gateway Routing)** designed to find the best path within an IP network using the **SPF** algorithm.

- OSPF uses the **Shortest Path First (SPF) algorithm**, aka **Dijkstra's algorithm**, created by a Dutch computer scientist **Edsger Dijkstra**, to calculate shortest paths to destination networks.

>[!note]+ Versions of OSPF
> There are three versions of OSPF:
> - OSPFv1 (1989): outdated, not used anymore
> - **OSPFv2 (1998): used for IPv4 — most commonly used**
> - OSPFv3 (2008): used for IPv6 — a newer version that supports both IPv4 and IPv6, but for IPv4-only networks, OSPFv2 is used more often.
> 	
> We will only discuss **OSPF version 2**.

>[!important]+ Link State protocols
> In **Link State protocols**, each router learns the **entire topology of the network**, forms its 'connectivity map'. 
> 
> 
> - Each router advertises information about its interfaces (connected networks) to its neighbors.
> - These advertisements are passed along to other routers, until all routers in the network develop the same connectivity map. 
> - Each router **independently uses this map** to calculate the best routes to each destination.
>>[!note] See [[dynamic_routing]].

- Information between routers is shared in **Link State Advertisements (LSAs)**. Packets that carry LSAs are called a **Link State Updates (LSUs)**.
- Each router maintains a **Link State Database (LSDB)** to store their current view on the network topology.
- Routers exchange LSAs until all routers in the **same OSPF area** come to the same LSDB — a topology map of the network.
- Once all routers have the same LSDB, each router separately calculates best routes to the destination networks using the Dijkstra's algorithm.

>[!important] OSPF process consists of three main steps:
>
> 1. **Becoming neighbors**
> 	- Routers connected to the same segment become neighbors to each other.
> 
> 2. **Exchanging LSAs**
> 	- Neighbor routers exchange LSAs between each other to learn the topology of the entire network.
> 
> 3. **Calculating the best routes**
> 	- Each router independently runs the SPF algorithm on their local copy of the LSDB to calculate the best routes to destination networks. These routes are then added to the routing table.

## OSPF areas

>OSPF divides the network into routing **areas** to simplify administration and optimize resource utilization.

>[!note]+ Single-area design
> - Small networks can be *single-area* without any negative effects on performance.
> - In larger networks, however, a single-area design can have negative effects:
> 	- The SPF algorithm takes more time to calculate routes
> 	- The SPF algorithm requires exponentially more processing power on the routers
> 	- A larger LSDB takes up more memory on the routers
> 	- Any small change in the network causes every router to flood LSAs and run the SPF algorithm again
> - Dividing a large OSPF network into several smaller areas helps avoiding these negative effects.

>[!important]+ OSPF area
>An **OSPF area** is a set of routers and links that share the same LSDB.

>[!important]+ Backbone area
> The **backbone area**, identified with `0` or `0.0.0.0`, is an area that all other areas must connect to.

- OSPF areas should be **contiguous**: each individual area should be connected, not divided up.
- All OSPF areas must have **at least one ABR connected to the backbone area** (area `0`).
- OSPF **interfaces in the same subnet must be in the same area**.

![[OSPF_areas.svg]]

>[!important]+ Area identifiers
>Each area is identified by a **`32`-bit number**, commonly expressed in DDN (Dotted-Decimal Notation), similar to IPv4 addresses. For example, `1.1.1.1`.
### Router types

OSPF routers are divided into three types based on the areas they have interfaces in:

- **Internal routers**
	- Routers with all interfaces in the same area.

- **Area Border Routers (ABRs)**
	- Routers with interfaces in multiple areas.

- **Backbone routers**
	- Routers connected to the backbone area (including ABRs).

- **Autonomous System Boundary Routers (ASBRs)**
	- Routers that connect an OSPF AS to other ASs.


>[!important]+ Area Border Routers (ABRs)
>- ABRs maintain a **separate LSDB for each area** they are connected to.
>- It is recommended to connect an ABR to a **maximum of 2 areas**. Connecting an ABR to 3+ areas can overburden the router.

![[OSPF_area_routers.svg]]

>[!note]+ Intra-area and inter-area routes
>An **intra-area** route is a route to a destination inside the same OSPF area.  
>An **inter-area** route is a route to a destination in a different OSPF area.
## Basic OSPF configuration

1. **Enter OSPF configuration mode:** 

```toml
R1(config)# router ospf ?
	<1-65535>  Process ID

R1(config)# router ospf 1
```

>[!note]+ OSPF process ID
>A router can run multiple OSPF processes at once, and **process ID** is used to identify each of them on the router.
>- The OSPF process ID is **locally significant**: routers with different process IDs **can become** OSPF neighbors. 
>- However, in **EIGRP**, process IDs must match. 

2. **Activate OSPF on all interfaces that are supposed to use it with the `network` command:**

```toml
R1(config-router)# network 10.0.12.0 0.0.0.3 area 0
R1(config-router)# network 10.0.13.0 0.0.0.3 area 0
R1(config-router)# network 172.16.1.0 0.0.0.15 area 0
```

>[!important]+ The `network` command
>The `network` command tells OSPF to...
>1. Look for any **interfaces** with an **IP address within the address range** specified in the `network` command.
>2. **Activate OSPF** on the matching interfaces and assign them to the specified OSPF `area`.
>3. The router will then try to **become OSPF neighbors** with other OSPF routers connected to the matching interfaces.

>[!tip]+
> - To get an overview of each OSPF-enabled interfaces:
> 
> ```toml
> R1# ip ospf interface brief
> ```

- To activate OSPF on **all interfaces**, use:

```toml
R1(config-router)# network 0.0.0.0 255.255.255.255 area 0
```

- Alternatively, you can activate OSPF on an interface directly with the `ip ospf` command in the interface configuration mode:

```toml
R1(config)# int g0/0
R1(config-if)# ip ospf 1 area 0 
             # ip ospf <process_id> area <area>
```

3. **Put interfaces that don't need to use OSPF into the passive mode:**

```toml
R1(config-router)# passive-interface g2/0
```

>[!note] See [[#The `passive-interface` command]].

4. **Configure a default route:**

```toml
R1(config)# ip route 0.0.0.0 0.0.0.0 203.0.113.2
```

5. **Configure the router to advertise its default route:**

```toml
R1(config-router)# default-information originate
```

>[!note] See [[#The `default-information originate` command]].


### The `passive-interface` command

The **`passive-interface` command** tells the router to **stop sending OSPF Hello messages** out of the specified interface. 

```toml
R1(cconfig-router)# passive-interface g2/0
```

- However, the router will **continue sending LSAs** to inform its neighbors about the subnet configured on the interface.

>[!important] You should always use the `passive-interface` command on interfaces which don't have any OSPF neighbors.

### The `default-information originate` command

The **`default-information originate` command** tells the router to **advertise its default route** to other OSPF routers in the same area:

1. Configure a default route:

```toml
R1(config)# ip route 0.0.0.0 0.0.0.0 g0/1
```

2. Advertise the default route into OSPF:

```toml
R1(config)# router ospf 1
R1(config-router)# default-information originate
```


>[!tip]+ `show ip route`
>- To display the default route:
>```toml
>R1# show ip route
>```
### The `show ip protocols` from OSPF perspective 

The `show ip protocols` command displays information about the dynamic routing protocols configured on the router. 

```toml
R1# show ip protocols 
```

On an OSPF router, the output looks like this:

```toml
*** IP Routing is NSF aware ***

Routing Protocol is "ospf 1"
  Outgoing update filter list for all interfaces is not set
  Incoming update filter list for all interfaces is not set
  Router ID 172.16.1.14
  It is an autonomous system boundary router
 Redistributing External Routes from,
  Number of areas in this router is 1. 1 normal 0 stub 0 nssa
  Maximum path: 4
  Routing for Networks:
    10.0.12.0 0.0.0.3 area 0
    10.0.13.0 0.0.0.3 area 0
    172.16.1.0 0.0.0.15 area 0
  Passive Interface(s):
    GigabitEthernet2/0
  Routing Information Sources:
    Gateway       Distance  Last Update
    4.4.4.4            110  00:00:08
    2.2.2.2            110  00:01:07
    3.3.3.3            110  00:01:07
    192.168.4.254      110  00:02:29
  Distance: (default is 110)
```

- `Router ID 172.16.1.14` 
	- Indicates **OSPF Router ID**.

- `It is an autonomous system boundary router`
	- An **autonomous system boundary router (ASBR)** is an OSPF router that connects the OSPF network to an external network.
	- `R1` is connected to the Internet. By using the `default-information originate` command, `R1` becomes an ASBR.

- `Number of areas in this router is 1. 1 normal 0 stub 0 nssa`
	- Indicates the number of OSPF areas on the router; `normal`, `stub`, and `nssa` are three different types of OSPF areas (no need to know for the CCNA). 

- `Maximum paths: 4`
	- The maximum number of paths for [[#ECMP]].

- `Routing for Networks:`
	- Shows the `network` commands used.

- `Passive Interface(s):`
	- Passive interfaces configured.

- `Distance:`
	- The AD of OSPF configured on the router (`110` is the default).

>[!note]
>`IP Routing is NSF aware` means that a router or switch supports **[NSF (Nonstop Forwarding)](https://www.cisco.com/en/US/docs/ios/12_2t/12_2t15/feature/guide/ftosnsfa.html)** awareness, a feature designed to maintain packet forwarding during control plane restart or switchover operation.
### The `router-id` command


>[!important] OSPF Router ID order or priority:
> 1. Manual configuration
> 2. **Highest IP address** on a **loopback interface**
> 3. **Highest IP address** on a **physical interface**

>[!warning] Router IDs must be unique.
>A router will ignore Hello packets marked with its own router ID. 

- The`router-id` command is used to manually configure the OSPF router ID:

```toml
R1(config)# router ospf 1
R1(config-router)# router-id 1.1.1.1
```

- For the change to take effect, either reload the router or use `clear ip ospf process` command.

```toml
R1# clear ip ospf process
Reset ALL OSPF processes? [no]: yes
```

>[!note] Here, `no` is the default choice.

>[!warning] Running `clear ip ospf process` in a real network is a **bad idea**: the router will **lose all of its OSPF routes**. 
>- This basically resets OSPF on a router.

### ECMP

>[!important]+ ECMP
>- If a router learns two or more routers via the **same routing protocols** to the **same destination** (= same network address, same subnet mask) with the **same metric**, **both routes will be added to the routing table**. 
>- **Traffic will be load-balanced over both routes**. 
>>This is called **ECMP (Equal-Cost Multi-Path)** load-balancing.

- To change the maximum number of equal-cost routes that can be used for ECMP:

```toml
# 1. enter routing protocol configuration mode
R1(config)# router ospf

# 2. configure the maximum number of routes for ECMP
R1(config-router)# maximum-paths ? 
	<1-32> Number of paths

R1(config-router)# maximum-paths 8
```

### The `distance` command: changing the default OSPF AD

- To change the default AD (Administrative Distance) of OSPF on a router:

```toml
R1(config)# router ospf
R1(coonfig-router)# distance ?
  <1-255>  Administrative distance

R1(coonfig-router)# distance 85
```
### `show` commands

```toml
R1# show ip protocols
```

```toml
R1# show ip ospf 1
```

```toml
R1# show ip ospf database
```

```toml
R1# show ip ospf neighbor
```

- Display detailed information about OSPF interface configuration and status:

```toml
R1# show ip ospf interface <interface_id>
```

>[!example]
>```toml
>R1# show ip ospf interface fastethernet 0/0
>```
> ```toml
> FastEthernet 0/0 is up, line protocol is up  
>   Internet Address 10.1.1.13/30, Area 0  
>   Process ID 101, Router ID 192.168.15.237, Network Type BROADCAST, Cost: 1  
>   Transmit Delay is 1 sec, State DR, Priority 1  
>   Designated Router (ID) 192.168.15.237, Interface address 10.1.1.13  
>   No Backup Designated router on this network  
>   Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5  
>     Hello due in 00:00:07  
>   Index 1/1, flood queue length 0  
>   Next 0x0(0)/0x0(0)  
>   Last flood scan length is 2, maximum is 2  
>   Last flood scan time is 0 msec, maximum is 4 msec  
>   Neighbor Count is 0, Adjacent neighbor count is 0  
>   Suppress hello for 0 neighbor(s)
> ```



## OSPF cost

>The **OSPF metric** is called **cost**; it's **automatically calculated based on interface bandwidth**.

>[!important]+ OSPF cost
> **Cost** is calculated by dividing a *reference bandwidth* value by the interface's bandwidth. 
>>The **default reference bandwidth is 100 Mbps**.
> 
> $$
> M = \frac{R}{I} = \frac{100 Mb/s}{I}
> $$
>- $M$ - Metric
>-  $R$ - Reference bandwidth
>-  $I$ - Interface bandwidth
>> **OSPF cost** is inversely proportional to the bandwidth of the link: **the higher the bandwidth** of a lint **the lower the cost** and the more preferred the link is.

>[!important] Loopback interfaces have a cost of 1.

>[!example]+ OSPF cost with the default reference bandwidth
>- **Reference:** 100 mbps / **Interface:** 10 mbps = cost of **10**.
>- **Reference:** 100 mbps / **Interface:** 100 mbps = cost of **1**.
>- **Reference:** 100 mbps / **Interface:** 1000 mbps = cost of **1**.
>- **Reference:** 100 mbps / **Interface:** 1000 mbps = cost of **1**.

| Name                | Interface Speed | Metric |
| ------------------- | --------------- | ------ |
| Ethernet            | 10 Mbps         | `10`   |
| Fast Ethernet       | 100 Mbps        | `1`    |
| Gigabit Ethernet    | 1 Gbps          | `1`    |
| 10 Gigabit Ethernet | 10 Gbps         | `1`    |

>[!important] All values less that 1 will be converted to 1.

>[!important] The **total OSPF cost** to a destination is **the sum of the costs of all outgoing/ (exit) interfaces**.

For this reason, **the default OSPF reference bandwidth should be changed**.

There are three ways to change OSPF cost:

- Change the **reference bandwidth**:

```toml
R1(config-router)# auto-cost reference-bandwidth [Mbps]
```

 - Manual configuration:

```toml
R1(config-if)# ip ospf cost [cost]
```

- Change the **interface bandwidth** (not recommended):

```toml
R1(config-if)# bandwidth [Kbps]
```

### Changing reference bandwidth on a router

- To change reference bandwidth on a router, use the `auto-cost reference-bandwidth` command:

```toml
R1(config-router)# auto-cost reference-bandwidth ?
  <1-4294967>  The reference bandwidth in termps of Mbps per second
```

```toml
R1(config-router)# auto-cost reference-bandwidth 100000
% OSPF: Reference bandwidth is changed.
        Please ensure reference bandwidth is consistent across all routers.
```

>[!tip]+
>The reference bandwidth should be configured to be **greater than the fastest links in your network** (to allow for future upgrades).

>[!important] The reference bandwidth **must be the same on all routers**. 

### Manually configuring interface cost

- To manually configure OSPF cost on an interface, use the `ip ospf cost` command:

```toml
R1(config-if)# ip ospf cost [cost]
```

```toml
R1(config-if)# ip ospf cost 10
```

### Changing interface bandwidth (not recommended)

- One more option to change the OSPF cost of an interface is to change the bandwidth of that interface with the `bandwidth` command:

```toml
R1(config)# bandwidth ?
 <1-10000000>   Bandwidth in kilobits
 inherit        Specify how bandwidth is inherited
 qos-reference  Reference bandwidth for QOS test
 receive        Speficy receive-side bandwidth
```

- Although the bandwidth matches the interface speed by default, changing the interface bandwidth **doesn't actually change the speed at which the interface operates**.
- Bandwidth is just a value used to calculate OSPF cost, EIGRP metric, etc.

>[!warning] Because the bandwidth value is used in other calculations, it's not recommended to change this value to alter the interface's OSPF cost.
>- Rather than that, it's recommended to manually configure OSPF cost on an interface.

## OSPF neighbors and adjacencies 

### OSPF neighbors

- Making sure that routers successfully become OSPF neighbors is the main task in configuring and troubleshooting OSPF.
- Once routers become neighbors, they automatically do the work of sharing network information, calculating routes, etc.

>[!important] OSPF neighbors
>**OSPF neighbors** are routers that have discovered each other by exchanging OSPF Hello packets. They are aware of each other's presence and agree on basic parameters. 
>> Neighbors **do not exchange routing information** with each other.

- To become neighbors, routers running OSPF must be in the **same OSPF area**. 

- When OSPF is activated on an interface, the router starts sending **OSPF Hello** messages out of the interface at regular intervals (determined by the **hello timer**). These are used to introduce the router to potential OSPF neighbors.

>[!important]+ Hello messages
>- The **default hello timer is 10 seconds** on an Ethernet connection.
>- Hello messages are **multicast to `224.0.0.5`** (multicast address for all OSPF routers).
>- OSPF messages are encapsulated in an IP header, with a value of `89` in the Protocol field. 

- To show OSPF neighbors:

```toml
R1# show ip ospf neighbor
```

- To activate OSPF directly on an interface:

```toml
R1(config-if)# ip ospf <process-id> area <area>
```
### OSPF adjacencies

>[!important]+ OSPF adjacencies
>**Adjacencies** are a subset of neighbor relationships where routers synchronize their LSDBs (Link State Databases) by exchanging LSAs (Link State Advertisements), i.e., **share routing information**. 

- All adjacencies are neighbors.
- Not all neighbors become adjacencies (especially on multi-access networks).

>[!important] Routers exchange topology information if and only if they have formed an **adjacency**.

### Becoming neighbors and forming adjacencies

>[!important] In OSPF, routers that have detected each other and for whose all required parameters have matched, form an **adjacency**. 

- The adjacency is attained through **seven** steps: 
	1. **Down state**
	2. **Init state**
	3. **2-way state** <- neighborship is formed at this stage
	4. **Exstart state**
	5. **Exchange state**
	6. **Loading state**
	7. **Full state** <- adjacency is formed at this stage

>[!important] It's enough for routers to enter the **two-way state** to start exchanging Hello messages. Routers in the 2-way state are called **OSPF neighbors**.


![[OSPF_becoming_neighbors.png]]

#### 1. The Down state

- The initial state for a router interface running OSPF.
- No OSPF Hello packets have been received from any neighbor on the interface. The router doesn't know of any neighbors yet.

At this stage:
1. The router selects its **router ID (RID)**.
2. The router starts sending OSPF **Hello packets** (multicast to `224.0.0.5`) to discover neighbors.

![[down_state.png]]
#### 2. The Init state

- Router has received Hello packets from a neighbor but hasn't yet seen its own Router ID listed in those packets.

> When a Hello packet is received from the neighbor router but the Hello packet does not contain the receiving router's ID, the neighbor router is the **Init state**.

>[!note]+
>The Hello packet includes a list of known neighbors. If a router finds its RID in the Hello packet received from another router, this means that the sender router "knows" the receiver; otherwise means the sender hasn't acknowledged the receiver router, and this is the **Init state**.

- The router replies with a new Hello packet that contains the RID of the router from which the original Hello packet was received. The router that receives that Hello with its own RID will enter the **2-way state**.

>[!important] Init state = Hello packet is received, but the receiver router ID is not in the Hello packet.

![[init_state.png]]
#### 3. The 2-way state

>[!important] Bidirectional communication established; the router sees its Router ID in the neighbor’s Hello packet.

- The neighbor router replies with a Hello packet that contains the sender's RID; once that Hello is received, both routers enter the **2-way state**.

>[!important] 2-way state = the router has received a Hello message with its own RID in it.

>[!note]+
> If both routers reach the 2-way state, it means that all of the conditions have been met for then to become OSPF neighbors. 
        
>[!note]+ DRs and BDRs election
>At the end of the 2-way state, the DR and BDR are elected for broadcast and non-broadcast multi-access (NBMA) networks.
>- On broadcast and NBMA networks, neighbor routers will proceed to the Full state only with the DR and BDR; other neighbor adjacencies will remain in the 2-way state.
>
>See [[#DRs and BDRs]] 

- Neighbor routers one of which is a DR or BDR, remain in the 2-way state.

>[!note] Troubleshooting  
> If all routers on a segment remain in the 2-way state, you should verify whether all routers on the segment are set to a priority `0`, which prevents any of them from becoming the DR or BDR.

![[2-way_state.png]]
#### 4. The Exstart state

>The two routers will now prepare to exchange information about their LSDB.
>Before that, they have to choose which one will start the exchange. This happens in the **Exstart** state.

>[!important]+ Master-Slave relationships in the Exstart state
>- The router with the higher RID (Router ID) will become the **Master** and initiate the exchange.
>- The router with the lower RID will become the **Slave**.
>
>>This Master/Slave relationship is only needed for the initial exchange of LSDB information.

- To decide the Master and Slave, routers exchange **DBD (Database Description)** packets.

>[!example]+
>- `R1` sends a DBD packet claiming to be the master.
>- However, since `R2` has a greater RID, it corrects `R1` and says it will be the Master.

>[!note] Troubleshooting 
> If a router is stuck in the Exstart state, you should verify whether there is a problem with mismatched Maximum Transmission Unit (MTU) settings or duplicate router IDs.


![[exstart_state.png]]
#### 5. The Exchange state

>In the **Exchange** state, the routers exchange DBDs which contain a list of the LSAs (Link State Advertisements) in their LSDB.

-  The DBD packets contain a list of the LSAs currently contained in the routers' LSDBs. These DBDs don't include any detailed information about the LSAs, only LSAs' headers.

- The routers compare the information in the DBDs they receive to the information in their own LSDB to determine which LSAs they must receive from neighbor.

>[!note] Troubleshooting  
> If a router is stuck in the Exchange state, you should verify whether there is a problem with mismatched MTU settings or duplicate router IDs.


![[exchange_state.png]]
#### 6. The Loading state

>In the **Loading** state, routers send **LSR (Link State Request)** messages to request their neighbors yo send them any LSAs they don't have.

- LSAs are sent in **LSU (Link State Update)** messages.
- The router send **LSAck (LSA Acknowledgment)** messages to acknowledge that they received the LSAs.

>[!note] Troubleshooting  
> If a router is stuck in the Loading state, you should verify whether there is a problem with mismatched MTU settings or corrupted LSR packets.


![[loading_state.png]]
#### 7. The Full state

>In the **Full** state, the routers have a full OSPF adjacency and identical LSDBs.

- They continue to send and listen for Hello packets (every 10 seconds by default) to maintain the neighbor adjacency.

---

- Every time a Hello packet is received, the **Dead timer** (40 seconds by default) is reset.
- If the Dead timer counts down to 0 and no Hello message is received, the neighbor is removed.
-  The routers will continue to share LSAs as the network changes to make sure each router has a complete and accurate map of the network (LSDB).

 >[!note] If a router does not receive a Hello packet from a neighbor within the Dead timer interval, the neighbor router will transition back to the Down state.

![[full_state.png]]


### OSPF neighbor requirements

To become neighbors, two conditions much be fulfilled:
- The OSPF **process must not be `shutdown`**.
- The OSPF **Router's IDs must be unique**.

The following must match on OSPF routers to become neighbors:
- The **area number**
- **Subnet** (interfaces must be in the same subnet)
- **Hello** and **Dead timers**
- **Authentication** settings (OSPF passwords)
- **OSPF network type**

IP MTU settings on the routers must also match.
- The routers do can become OSPF neighbors even if their MTU settings don't match, but OSPF won't function properly (the routers will stuck at the Exstart state).



## OSPF message types

| Type | Name                                  | Purpose                                                                                     |
| ---- | ------------------------------------- | ------------------------------------------------------------------------------------------- |
| 1    | **Hello**                             | Neighbor discovery and maintenance.<br>Sent to `224.0.0.5`.                                 |
| 2    | **Database Description (DBD)**        | Summary of the LSDB of the router.<br>Used to check if the LSDB of each router is the same. |
| 3    | **Link-State Request (LSR)**          | Requests specific LSAs from the neighbor.                                                   |
| 4    | **Link-State Update (LSU)**           | Sends specific LSAs to the neighbor.                                                        |
| 5    | **Link-State Acknowledgment (LSAck)** | Used to acknowledge that the router received a message.                                     |

## OSPF network types

| Network type                          | Link types                                                      | DR/BDR? | Hello | Dead  | Notes                                                                                                         |
| ------------------------------------- | --------------------------------------------------------------- | ------- | ----- | ----- | ------------------------------------------------------------------------------------------------------------- |
| **Broadcast**                         | Ethernet, FDDI (Fiber Distributed Data Interface)               | Yes     | 10 s  | 40 s  | The DR generates a Type 2 Network LSA to represent the multi-access segment.                                  |
| **Non-broadcast multi-access (NBMA)** | Frame relay                                                     | Yes     | 30 s  | 120 s | Multicast is unavailable; neighbors are defined statically; Hello are unicast.                                |
| **Point-to-point**                    | HDLC, PPP;<br>Serial, E1/T1 leased lines, GRE and IPsec tunnels | No      | 10 s  | 40 s  | This is the most efficient network type for links with only two routers.                                      |
| **Point-to-multipoint**               | Frame relay, DMVPN<br>(not configured by default)               | No      | 30 s  | 120 s | Neighbors are discovered automatically; each router forms a direct adjacency with its neighbors without a DR. |
| **Point-to-multipoint non-broadcast** | Non-broadcast hub-and-spoke WAN; DMVPN                          | No      | 30 s  | 120 s | Multicast is unavailable; neighbors are defined statically; Hello are unicast.                                |

>[!important] Network type is configured per-interface.

```toml
R1(config-if)# ip ospf network ?
  broadcast            Specify OSPF broadcast multi-access network
  non-broadcast        Specify OSPF NBMA network
  point-to-multipoint  Specify OSPF point-to-multipoint network
  point-to-point       Specify OSPF point-to-point network
```

| Network Type                                    | Description                                                                               | DR/BDR Election | Hello/Dead Timers (default) | Typical Use Case                |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------- | --------------- | --------------------------- | ------------------------------- |
| **Broadcast**                                   | Multi-access network supporting broadcast/multicast (e.g., Ethernet LAN).                 | Yes             | Hello: 10s, Dead: 40s       | Ethernet LANs                   |
| **Non-Broadcast Multi-Access (NBMA)**           | Multi-access network without broadcast capability; neighbors must be manually configured. | Yes             | Hello: 30s, Dead: 120s      | Frame Relay, ATM networks       |
| **Point-to-Point (P2P)**                        | Link between exactly two routers; no DR/BDR election needed.                              | No              | Hello: 10s, Dead: 40s       | Serial links, PPP, HDLC         |
| **Point-to-Multipoint (P2MP)**                  | Single interface connecting to multiple routers; treats each neighbor as point-to-point.  | No              | Hello: 30s, Dead: 120s      | Hub-and-spoke WAN topologies    |
| **Point-to-Multipoint Non-Broadcast (P2MP-NB)** | Like P2MP but without broadcast/multicast support; neighbors manually configured.         | No              | Hello: 30s, Dead: 120s      | Non-broadcast hub-and-spoke WAN |

## DRs and BDRs

>[!important] When multiple routers sit on the same VLAN, they automatically elect one router to act as the **Designated Router (DR)**, and one more router to act as a **Backup Designated Router (BDR)**.

The DR/BDR election order of priority:

1. **Highest OSPF priority**
2. **Highest OSPF router ID** — if the priorities are the same

The first place in the election becomes the DR for the subnet, the second becomes the BDR.

>[!important]+ OSPF interface priority
>- Each OSPF-enabled router is assigned a **priority**, advertised in each Hello packet.
>- The **default OSPF priority is `1`**.
>- A router with the priority set to `0` can't become a DR or BDR for the subnet.
> To change the OSPF interface priority on a router:
> 
> ```toml
> R2(config)# int g0/0
> R2(config-if): ip ospf priority <0-255>
> ```

- When the DR goes down, the BDR becomes the new DR. Then an election is help for the next BDR.

>[!important] The DR/BDR election is **non-preemptive**: once the DR/BDR are selected, they will keep their role until OSPF reset, or the interface fails, or is shut down, etc.

>[!important] When a Designated Router is elected for the segment, **routers only exchange database information with the DR**.

Without a DR, OSPF routers in a segment would have to form a full mesh of adjacencies so that each router exchanges LSAs with each other router. However, this is inefficient and consumes much more traffic compared to exchanging LSAs only with the DR.

>[!important] DROthers are OSPF routers which are not DR or BDR on the network segment.
> - Routers only exchange LSAs with the DR and BDR. DROthers will not exchange LSAs with each other.

>DROthers will move to the full state only with the DR and BDR; a DROther doesn't form an adjacency with another DROther, only 2-way.
  
>[!important] Messages to the DR and BDR are **multicast to the `224.0.0.6` address**.

>[!example]+
> Consider an example:
> 
> ```toml
> Router1# show ip ospf interface fastethernet 0/1
> ```
> 
> ```toml
> FastEthernet0/1 is up, line protocol is up  
>   Internet Address 10.2.16.43/24, Area 0  
>   Process ID 1, Router ID 10.0.0.4, Network Type BROADCAST, Cost: 1  
>   Transmit Delay is 1 sec, State DROTHER, Priority 50  
>   Designated Router (ID) 10.0.0.7, Interface Address 10.2.16.1  
>   Backup Designated router (ID) 10.0.0.11, Interface Address 10.2.16.17  
>   Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5  
>     Hello due in 00:00:04  
>   Neighbor Count is 5, Adjacent neighbor count is 2  
>     Adjacent with neighbor 10.0.0.7  (Designated Router)  
>     Adjacent with neighbor 10.0.0.11  (Backup Designated Router)  
> Suppress hello for 0 neighbor(s)
> ```
> 
> The output shows that:
> - `Router1` is in the `DROTHER` state. 
> - A router in the `DROTHER` state can only establish adjacencies with the DR and the BDR. Therefore, `Router1` is neither the DR nor the BDR.
> - The DR has a router ID of `10.0.0.7` and an IP address of `10.20.16.1`, and the BDR has a router ID of `10.0.0.11` and an IP address of `10.2.16.17`.
>>`Router1` is not connected to a point-to-multipoint network, because the network segment contains a DR and a BDR. A DR and a BDR are not elected on point-to-multipoint or point-to-point networks; they are elected only on multi-access networks.

## LSA types

- The OSPF LSDB is made up of LSAs.

There are 11 types of LSA, but there're only 3 you should be aware of for the CCNA:

- **Type 1 (Router LSA)**
	- Every OSPF router generates this type of LSA.
	- It identifies the router using the router's ID.
	- It also lists networks attached to the router's OSPF-activated interfaces.

- **Type 3 (Network LSA)**
	- Generated by the DR of each multi=access network (e.g., the **broadcast** network type).
	- Lists the routers attached to the multi-access network.

- **Type 5 (AS-External LSA)**
	- Generated by ASBRs to describe routes to destinations outside of the AS (OSPF domain).
## Labs

### OSPF Lab 1

![[OSPF_lab_1.png]]

#### Step 1: hostnames and IP addresses

- `ISPR1`:

```toml
ISPR1(config)# int g0/0/0
ISPR1(config-if)# ip address 203.0.113.2 255.255.255.252
ISPR1(config-if)# no shutdown
```

- `R1`:

```toml
Router(config)# hostname R1

R1(config)# int g3/0
R1(config-if)# ip address 203.0.113.1 255.255.255.252
R1(config-if)# no shutdown

R1(config-if)# int f1/0
R1(config-if)# ip address 10.0.13.1 255.255.255.252
R1(config-if)# no shutdown

R1(config-if)# int g0/0
R1(config-if)# ip address 10.0.12.1 255.255.255.252
R1(config-if)# no shutdown

R1(config-if)# do sh ip int br
Interface          IP-Address  OK? Method Status    Protocol 
GigabitEthernet0/0 10.0.12.1   YES manual up        down 
FastEthernet1/0    10.0.13.1   YES manual up        down 
FastEthernet2/0    unassigned  YES unset  administratively down down 
GigabitEthernet3/0 203.0.113.1 YES manual up        up
```

- `R2`:

```toml
Router(config)# hostname R2

R2(config)# int g0/0 
R2(config-if)# ip address 10.0.12.2 255.255.255.252
R2(config-if)# no shutdown

R2(config-if)# int f1/0 
R2(config-if)# ip address 10.0.24.1 255.255.255.252
R2(config-if)# no shutdown

R2(config-if)# do sh ip int br
Interface          IP-Address  OK? Method Status  Protocol 
GigabitEthernet0/0 10.0.12.2   YES manual up      up 
FastEthernet1/0    10.0.24.1   YES manual up      down 
FastEthernet2/0    unassigned YES unset  administratively down down
```

- `R3`:

```toml
Router(config)# hostname R3

R3(config)# int f1/0
R3(config-if)# ip address 10.0.13.2 255.255.255.252
R3(config-if)# no shutdown

R3(config-if)# int f2/0 
R3(config-if)# ip address 10.0.34.1 255.255.255.252
R3(config-if)# no shutdown

R3(config-if)# do sh ip int br
Interface          IP-Address  OK? Method Status  Protocol 
GigabitEthernet0/0 unassigned  YES unset  administratively down down 
FastEthernet1/0    10.0.13.2   YES manual up      up 
FastEthernet2/0    10.0.34.1   YES manual up      down
```

- `R4`:

```toml
Router(config)# hostname R4

R4(config)# int f2/0
R4(config-if)# ip address 10.0.34.2 255.255.255.252 
R4(config-if)# no shutdown

R4(config-if)# int f1/0
R4(config-if)# ip address 10.0.24.2 255.255.255.252
R4(config-if)# no shutdown

R4(config-if)# int g0/0
R4(config-if)# ip address 192.168.4.2 255.255.255.252
R4(config-if)# no shutdown
```

#### Step 2: loopback interfaces

- `R1`:

```toml
R1(config)# int l0

R1(config-if)# ip address 1.1.1.1 255.255.255.255

R1(config-if)# do sh ip int br
Interface           IP-Address OK? Method Status Protocol 
GigabitEthernet0/0  10.0.12.1   YES manual up    up 
FastEthernet1/0     10.0.13.1   YES manual up    up 
FastEthernet2/0     unassigned  YES unset  administratively down down 
GigabitEthernet3/0  203.0.113.1 YES manual up    up 
Loopback0           1.1.1.1     YES manual up    up
```

- `R2`:

```toml
R2(config)# int l0

R2(config-if)# ip address 2.2.2.2 255.255.255.255
R2(config-if)# do sh ip int br
Interface              IP-Address      OK? Method Status                Protocol 
GigabitEthernet0/0     10.0.12.2       YES manual up                    up 
FastEthernet1/0        10.0.24.1       YES manual up                    up 
FastEthernet2/0        unassigned      YES unset  administratively down down 
Loopback0              2.2.2.2         YES manual up                    up
```

- `R3`:

```toml
R3(config-if)# int l0

R3(config-if)# ip address 3.3.3.3 255.255.255.255
R3(config-if)# do sh ip int br
Interface              IP-Address      OK? Method Status                Protocol 
GigabitEthernet0/0     unassigned      YES unset  administratively down down 
FastEthernet1/0        10.0.13.2       YES manual up                    up 
FastEthernet2/0        10.0.34.1       YES manual up                    up 
Loopback0              3.3.3.3         YES manual up                    up
```

- `R4`:

```toml
R4(config-if)# int l0
R4(config-if)# ip address 4.4.4.4 255.255.255.255
R4(config-if)# do sh ip int br
Interface              IP-Address      OK? Method Status                Protocol 
GigabitEthernet0/0     192.168.4.2     YES manual up                    up 
FastEthernet1/0        10.0.24.2       YES manual up                    up 
FastEthernet2/0        10.0.34.2       YES manual up                    up 
Loopback0              4.4.4.4         YES manual up                    up
```

#### Step 3: configuring OSPF

- `ISPR1`:

```toml
ISPR1(config)# router ospf 1
ISPR1(config-router)# network 0.0.0.0 255.255.255.255 area 0
```

- `R1`:

```toml
R1(config)# router ospf 1
R1(config-router)# network 0.0.0.0 255.255.255.255 area 0
R1(config-router)# passive-interface l0
R1(config-router)# passive-interface g3/0
```

- `R2`:

```toml
R2(config)# router ospf 2
R2(config-router)# network 0.0.0.0 255.255.255.255 area 0
R2(config-router)# passive-interface l0
```

- `R3`:

```toml
R3(config)# router ospf 3
R3(config-router)# network 0.0.0.0 255.255.255.255 area 0
R3(config-router)# passive-interface l0
```

- `R4`:

```toml
R4(config)#
R4(config)# router ospf 4
R4(config-router)# network 0.0.0.0 255.255.255.255 area 0
R4(config-router)# passive-interface g0/0
R4(config-router)# passive-interface l0
```

#### Step 4: configuring R1 as ASBR

```toml
R1(config)# ip route 0.0.0.0 0.0.0.0 203.0.112.2
R1(config)# router ospf 1
R1(config-router)# default-information originate
```


#### Step 5: show commands


- `R1`:

```toml
R1# show ip protocols
```

```toml
Routing Protocol is "ospf 1"
  Outgoing update filter list for all interfaces is not set 
  Incoming update filter list for all interfaces is not set 
  Router ID 1.1.1.1
  It is an autonomous system boundary router
  Redistributing External Routes from,
  Number of areas in this router is 1. 1 normal 0 stub 0 nssa
  Maximum path: 4
  Routing for Networks:
    0.0.0.0 255.255.255.255 area 0
  Passive Interface(s): 
    GigabitEthernet3/0
    Loopback0
  Routing Information Sources:  
    Gateway         Distance      Last Update 
    1.1.1.1              110      00:02:37
    4.4.4.4              110      00:07:06
    10.0.24.1            110      00:08:24
    10.0.34.1            110      00:07:06
    203.0.113.2          110      00:09:13
  Distance: (default is 110)
```

```toml
R1# show ip ospf 1
```

```toml
 Routing Process "ospf 1" with ID 1.1.1.1
 Supports only single TOS(TOS0) routes
 Supports opaque LSA
 SPF schedule delay 5 secs, Hold time between two SPFs 10 secs
 Minimum LSA interval 5 secs. Minimum LSA arrival 1 secs
 Number of external LSA 1. Checksum Sum 0x00fecf
 Number of opaque AS LSA 0. Checksum Sum 0x000000
 Number of DCbitless external and opaque AS LSA 0
 Number of DoNotAge external and opaque AS LSA 0
 Number of areas in this router is 1. 1 normal 0 stub 0 nssa
 External flood list length 0
    Area BACKBONE(0)
        Number of interfaces in this area is 4
        Area has no authentication
        SPF algorithm executed 8 times
        Area ranges are
        Number of LSA 9. Checksum Sum 0x03bd3d
        Number of opaque link LSA 0. Checksum Sum 0x000000
        Number of DCbitless LSA 0
        Number of indication LSA 0
        Number of DoNotAge LSA 0
        Flood list length 0
```

```toml
R1# show ip ospf database
```

```toml
            OSPF Router with ID (1.1.1.1) (Process ID 1)

                Router Link States (Area 0)

Link ID         ADV Router      Age         Seq#       Checksum Link count
203.0.113.2     203.0.113.2     768         0x80000002 0x0086d1 1
10.0.24.1       10.0.24.1       87          0x80000009 0x008adc 3
1.1.1.1         1.1.1.1         82          0x8000000f 0x005913 4
10.0.34.1       10.0.34.1       87          0x80000009 0x003cfc 3
4.4.4.4         4.4.4.4         82          0x8000000c 0x005c7e 4

                Net Link States (Area 0)
Link ID         ADV Router      Age         Seq#       Checksum
10.0.12.2       10.0.24.1       87          0x80000001 0x007a6e
10.0.24.1       10.0.24.1       87          0x80000002 0x00349c
10.0.13.2       10.0.34.1       86          0x80000001 0x00267d
10.0.34.1       10.0.34.1       86          0x80000002 0x00f5ba

                Type-5 AS External Link States
Link ID         ADV Router      Age         Seq#       Checksum Tag
0.0.0.0         1.1.1.1         372         0x80000001
```

```toml
R1# show ip ospf neighbor
```

```toml
Neighbor ID     Pri   State           Dead Time   Address         Interface
10.0.34.1         1   FULL/DR         00:00:35    10.0.13.2       FastEthernet1/0
10.0.24.1         1   FULL/DR         00:00:35    10.0.12.2       GigabitEthernet0/0
```

```toml
R1# show ip ospf interface
```

```toml
GigabitEthernet0/0 is up, line protocol is up
  Internet address is 10.0.12.1/30, Area 0
  Process ID 1, Router ID 1.1.1.1, Network Type BROADCAST, Cost: 1
  Transmit Delay is 1 sec, State BDR, Priority 1
  Designated Router (ID) 10.0.24.1, Interface address 10.0.12.2
  Backup Designated Router (ID) 1.1.1.1, Interface address 10.0.12.1
  Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5
    Hello due in 00:00:06
  Index 1/1, flood queue length 0
  Next 0x0(0)/0x0(0)
  Last flood scan length is 1, maximum is 1
  Last flood scan time is 0 msec, maximum is 0 msec
  Neighbor Count is 1, Adjacent neighbor count is 1
    Adjacent with neighbor 10.0.24.1  (Designated Router)
  Suppress hello for 0 neighbor(s)
FastEthernet1/0 is up, line protocol is up
  Internet address is 10.0.13.1/30, Area 0
  Process ID 1, Router ID 1.1.1.1, Network Type BROADCAST, Cost: 1
  Transmit Delay is 1 sec, State BDR, Priority 1
  Designated Router (ID) 10.0.34.1, Interface address 10.0.13.2
  Backup Designated Router (ID) 1.1.1.1, Interface address 10.0.13.1
  Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5
    Hello due in 00:00:06
  Index 2/2, flood queue length 0
  Next 0x0(0)/0x0(0)
  Last flood scan length is 1, maximum is 1
  Last flood scan time is 0 msec, maximum is 0 msec
  Neighbor Count is 1, Adjacent neighbor count is 1
    Adjacent with neighbor 10.0.34.1  (Designated Router)
  Suppress hello for 0 neighbor(s)
GigabitEthernet3/0 is up, line protocol is up
  Internet address is 203.0.113.1/30, Area 0
  Process ID 1, Router ID 1.1.1.1, Network Type BROADCAST, Cost: 1
  Transmit Delay is 1 sec, State WAITING, Priority 1
  No designated router on this network
  No backup designated router on this network
  Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5
    No Hellos (Passive interface)
  Index 3/3, flood queue length 0
  Next 0x0(0)/0x0(0)
  Last flood scan length is 1, maximum is 1
  Last flood scan time is 0 msec, maximum is 0 msec
  Neighbor Count is 0, Adjacent neighbor count is 0
  Suppress hello for 0 neighbor(s)
Loopback0 is up, line protocol is up
  Internet address is 1.1.1.1/32, Area 0
  Process ID 1, Router ID 1.1.1.1, Network Type LOOPBACK, Cost: 1
  Loopback interface is treated as a stub Host
```
### Loopback interfaces


>[!important]+ Loopback interfaces
>A **loopback interface** on a Cisco router is a logical, virtual interface that emulates a physical interface and remains in an `up/up` state as long as the router is functioning, regardless of the status of physical interfaces.

- To configure a loopback interface:

```toml
R1(config)# int l0
R1(config-if)# ip address 4.4.4.4 255.255.255.255
```


Here is an example:

```toml
Router(config)# int l0

Router(config-if)#
%LINK-5-CHANGED: Interface Loopback0, changed state to up

%LINEPROTO-5-UPDOWN: Line protocol on Interface Loopback0, changed state to up
 
Router(config-if)# ip address 4.4.4.4 255.255.255.255
Router(config-if)# do sh ip int br
Interface              IP-Address      OK? Method Status                Protocol 
GigabitEthernet0/0     unassigned      YES unset  administratively down down 
FastEthernet1/0        unassigned      YES unset  administratively down down 
FastEthernet2/0        unassigned      YES unset  administratively down down 
Loopback0              4.4.4.4         YES manual up                    up
```

## Quiz

1. Which of the following statements about OSPF are not true? (select two)
	- a. In multi-area OSPF networks, all non-backbone areas must have an ABR connected to area 0.
	- b. Single-area OSPF must use area 0.
	- c. Two OSPF routers with different process IDs can become OSPF neighbors.
	- d. The OSPF area must be specified in the network command.
	- e. An ASBR connects the internal OSPF network to networks outside of the OSPF domain.
	- f. The OSPF process ID must match the area number.
 

2. You want to activate OSPF on R1's `g0/1` and `g0/2` interfaces with a single command.  `g0/1`'s IP address is `10.0.12.1/28`, and `g0/2`'s IP address is `10.0.13.1/26`.
	- a. `R1(config-router)# network 10.0.12.0 0.0.0.255 area 0`
	- b. `R1(config-router)# network 10.0.12.0 0.0.0.254 area 0`
	- c. `R1(config-router)# network 10.0.12.0 0.0.1.255 area 0`
	- d. `R1(config-router)# network 10.0.8.0 0.0.3.255 area 0`

3. Which of the following commands will make R1 an OSPF ASBR?
	- a.    `R1(config-router)# network 10.0.0.0 0.0.0.255 area 0`
		 `R1(config-router)# network 10.0.0.0 0.0.0.255 area 0`
	- b.    `R1(config)# ip route 0.0.0.0 0.0.0.0 203.0.113.2`
	     `R1(config)# router ospf 1`
	     `R1(config-router)# default-information originate`
	- c.    `R1(config-router)# network 0.0.0.0 255.255.255.255 area 0`
	- d.   `R1(config-router)# default-route originate`


4. Which command can be used to manually configure the OSPF router ID?
	- a.    `R1(config-router)# router-id 1.1.1.1`
	- b.    `R1(config-router)# ospf router-id 1.1.1.1`
	- c.    `R1(config)# interace loopback0`
	     `R1(config-if)# ip address 1.1.1.1 255.255.255.255`
	- d.    `R1(config-router)# ospf router id 1.1.1.1`

5. Which option states a characteristic of the OSPF point-to-point network type that is different that the OSPF broadcast network type?
	- a. DR/BDR elections are held.
	- b. DR/BDR elections are not held.
	- c. Neighbors are dynamically discovered.
	- d. Neighbors are not dynamically discovered.

6. There is an OSPF broadcast network with 5 connected routers. R1 is the DR on its `g0/0` interface. How many full OSPF adjacencies does R1 have on the interface?
	- a. 1, with the BDR
	- b. 2, with the DR and BDR
	- c. 4, with all neighbors
	- d. 5, with all routers connected to the segment

7. Which of the following are requirements for routers to become OSPF neighbors? (select two)
	- a. Hello and Dead timers must match
	- b. OSPF Process IDs must match
	- c. OSPF Router IDs must match
	- d. Interfaces must be in the same area
	- e. Interfaces must be in different areas
	- f. Interfaces must be in different subnets

8. Which of the following OSPF LSA types is generated only by the DR of a multi-access network, such as the broadcast network type?
	- a. Type 1
	- b. Type 2
	- c. Type 3
	- d. Type 5

9. R1 is connected to an OSPF network on its `g0/0` interface. R4 is the DR of the segment, and R3 is the BDR. All routers on the segment have the default OSPF priority. You issue the `ip ospf priority 100` command on the R1's `g0/0` to make it DR. Which of the following statements are true about the network after you issue the command? (select two)
	- a. R1 is the DR
	- b. R1 is the BDR
	- c. R1 is still a DROther because its priority isn't high enough
	- d. If you issue the `clear ip ospf process` command on R4, R1 will become the BDR.
	- e. If you issue the `clear ip ospf process` command on R4, R1 will become the BDR.
	- f. The DR and BDR of the network are unchanged.

10. Boson ExSim. You issue the `show ip ospf neighbor` command on Router 1 and see that Router 2 is the `2WAY/DROTHER` state. Which of the following statements is true regarding Router 2? (Select the best answer.)
	- a. Router 2 is the DR for the segment. 
	- b. The MTU are mismatched between Router 1 and Router 2. 
	- c. Router 1 is the DR for the segment. 
	- d. Router 1 and Router 2 are normal neighbor routers that are operating correctly.

11. Boson ExSim. You are trying to configure OSPF to perform equal-cost load balancing. Router 1 should have 8 equal-cost OSPF routers to the `192.168.102.0/24` network. However, only 4 OSPF routes exist. Which of the following should you do to perform equal-cost load-balancing over all 8 routes? (Select the best answer.)
	- a. Configure the variable to a value of 8.
	- b. Issue the `ip ospf cost 1` command on all interfaces.
	- c. Configure EIGRP throughout the network.
	- d. Issue the `maximum-paths 8` command.

| Question | Answer     |
| -------- | ---------- |
| `1.`     | `b.`, `f.` |
| `2.`     | `c.`       |
| `3.`     | `b.`       |
| `4.`     | `a.`       |
| `5.`     | `b.`       |
| `6.`     | `c.`       |
| `7.`     | `a.`, `d.` |
| `8.`     | `b.`       |
| `9.`     | `d.`, `f.` |
| `10.`    | `d.`       |
| `11.`    |            |


1. *After you issue the `clear ip ospf process`, R3 automatically becomes the DR, not R1. Therefore R1 will only become the BDR.*