---
created: 2025-10-13 03:49:17
tags:
  - routing
---
## Displaying information about routing protocols

- To show information about routing protocols in use:

```toml
R1# show ip protocols
```

- The `show ip protocols` command is used to display a summary of configured routing protocols. The output includes information about the routing protocols, such as the routing protocol name, the interfaces used, the update interval, and the metrics used.

```toml
Routing Protocol is "eigrp 1"  
Outgoing update filter list for all interfaces is not set  
Incoming update filter list for all interfaces is not set  
Default networks flagged in outgoing updates
Default networks accepted from incoming updates
EIGRP-IPv4 Protocol for AS(1)
	Metric weight K1=1, K2=0, K3=1, K4=0, K5=0
	NSF-aware route hold timer is 240
	Router-ID: 172.16.1.14
	Topology : 0 (base)
		Active Timer: 3 min
		Distance: internal 90 external 170
		Maximum path: 4
		Maximum hopcount: 100
		Maximum metric variance 1

Automatic Summarization: disabled
Maximum path: 4  
Routing for Networks:  
	10.0.0.0
	172.16.1.0/28
Passive Interface(s):
	GigabitEthernet1/0

Routing Information Sources:  
Gateway     Distance     Last Update  
10.0.12.2         90     00:00:23  
10.0.13.2         90     00:00:23   
Distance: (default is 90)
```

- `Routing Protocol is "eigrp 1"`
	- `1` is the AS number 
`
- `Router-ID: 172.16.1.14`
	- In EIGRP and OSPF, the router has a unique router ID which identifies it within the AS. ID is not actually an IP address, but just a number formatted like IP address. It can be changed to any 32-bit number.
	- The router ID order of priority:
		1. Manual configuration
		2. Highest IP address on a loopback interface
		3. Highest IP address on a physical interface

- To configure EIGRP router ID:

```toml
R1(config-router)# eigrp router-id 1.1.1.1
```

- `Maximum path: 4`
	- The maximum number of load-balanced links.

>[!note]+ Downside of EIGRP
>Metrics are harder to understand; the numbers are much larger.
## RIP

>**RIP (Routing Information Protocol)** is one of the oldest distance-vector routing protocols that uses hop count as its primary metric to determine the best path between the source and destination network.

- RIP is **Distance vector IGP** (uses routing-by-rumor logic to learn and share routes).
- RIP uses **hop count** as its metric. One router = one hop. Bandwidth is not considered.
- The maximum hop count is **15**. Anything more that that is considered unreachable.

>[!important] RIP routers send messages to a multicast address `244.0.0.9`. 

>[!note] With a defined maximum metric, a routing protocol can mitigate routing loops caused by invalid routing updates.

RIP has three versions:
- RIPv1 (not used)
- RIPv2 
- RIPng (RIP Next Generation), used for IPv6

RIP uses two message types:
- **Request**: To ask RIP-enabled neighbor routers to send their routing table.
- **Response**: To send the local routing table to neighboring routers.

>[!note] By default, RIP-enabled routers will share their routing table **every 30 seconds**. 

>[!note] RIPv1 vs. RIPv2
> - **RIPv1**:
> 	- Only advertises classful addresses (Class A, Class B, Class C).
> 	- Doesn't support VLSM, CIDR.
> 	- Doesn't include subnet mask information in advertisements (response messages).
> 	- Messages are **broadcasts** to `255.255.255.255`.
> - **RIPv2**:
> 	- Supports VLSM, CIDR.
> 	- Includes subnet mask information in advertisements.
> 	- Messages are **multicast** to `224.0.0.9`.

### Basic configuration

```toml
# enter configuration mode
R1(config)# router rip

# use RIPv2
R1(config-router)# version 2

# do not convert the networks the router advertises to classful networks  
R1(config-router)# no auto-summary # auto-summary is on by default

# tell the router what interfaces to activate RIP on
R1(config-router)# network 10.0.0.0
R1(config-router)# network 172.16.0.0
```

- The `network` command tells the router to:
	1. Look for interfaces with an IP address in the specified range.
	2. Activate RIP on the interfaces that fall in the range.
	3. Form adjacencies with connected RIP neighbors.
	4. Advertise the network prefix of the interface (not the prefix in the `network` command).

>[!important] The `network` command doesn't tell the router which networks to advertise. It tells the router which interfaces to activate RIP on, and then the router will advertise the network prefix of those interfaces.

>[!note] The OSPF and EIGRP `network` commands operate in the same way.

>[!note]+ Passive interfaces
>Even if there are no RIP neighbors connected to an interface, router configured to use RIP will nevertheless continuously send advertisements out of that interface. Since this is unnecessary traffic, the interface should be configured as a **passive interface**.
>- To configure an interface as passive:
> 
> ```toml
> R1(config-router)# passive-interface g1/0
> ```
> The command tells the router to stop sending RIP advertisements out of the specified `g1/0` interface.
> 
>- EIGRP and OSPF both have the same passive interface functionality, enabled with the same command.

- Here is how to configure a default route (see [[static_routes]]):

```toml
R1(config)# ip route 0.0.0.0 0.0.0.0 302.0.113.2
```


- And here is how to tell the router to share this default route into RIP:

```toml
R1(config)# router rip
R1(config-router)# default-information originate
```

- To change the maximum number of paths used in ECMP load-balancing (see [[dynamic_routing]]):

```toml
R1(config-router)# maximum-paths ?
   <1-32>  Number of paths

R1(config-router)# maximum-paths 8
```

- To change the administrative distance of RIP on the router:

```toml
R1(config-router)# distance ?
   <1-255>  Adminsitrative distance
   
R1(config-router)# distance 85
```
## EIGRP

>**EIGRP (Enhanced Interior Gateway Routing Protocol)** is an advanced, dynamic routing protocol developed by Cisco to automate routing decisions and configuration within large and complex networks.

- EIGRP was Cisco-proprietary, but Cisco has **published it openly** so other vendors can implement it on their equipment.
- EIGRP is considered an 'advanced'/'hybrid' distance vector routing protocol.
- It has a **much faster convergence** compared to RIP. 

>[!important] EIGRP routers send messages to a multicast address `244.0.0.10`. 

- EIGRP is the only IGP that can perform **unequal**-cost load-balancing (though ECMP over 4 paths is used by default, just like in RIP).

>[!important] By default, EIGRP uses **bandwidth** and **delay** to calculate the **composite metric**, which is used to determine the best path to a destination network:
>- **Bandwidth** refers to the data throughput of a link. 
>- **Delay** refers to the time required to send a packet to a destination.

- EIGRP can also use **load** and **reliability** as components, but these components are not used by default. 
	- **Load** refers to the amount of data activity over a link. 
	- **Reliability** refers to the bit-error rate of a link.

### Basic configuration

```toml
# enter EIGRP configuration mode
R1(config)# router eigrp 1 # the number is the AS number

# turn off route auto-summarization
R1(config-router)# no auto-summary

# set g1/0 to be a passive interface
R1(config-router)# passive-interface g1/0

# activate EIGRP on the given interfaces
R1(config-router)# network 10.0.0.0
R1(config-router)# network 172.16.1.0. 0.0.0.15
```

>[!warning] The **AS (Autonomous System) number must match between routers**, otherwise they will not form an adjacency and share routing information.

>[!important] EIGRP uses a wildcard mask instead of a regular subnet mask (e.g., `0.0.0.15`).

>[!note]+ Auto-summary
>Auto-summary might be enabled or disabled by default, depending on the router/IOS version. It it's enabled, disable it.

- To configure EIGRP router ID:

```toml
R1(config-router)# eigrp router-id ?
  A.B.C.D  EIGRP Router-ID in IP address format
  
R1(config-router)# eigrp router-id 1.1.1.1 
```

