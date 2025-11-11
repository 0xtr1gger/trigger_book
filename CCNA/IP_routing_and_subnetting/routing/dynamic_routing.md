---
created: 2025-09-28 11:18:57
tags:
  - routing
---
## Dynamic routing

- Routers use **dynamic routing protocols** to advertise information about the routes they know to other routers. 
- They form **adjacencies**, aka **neighbor relationships**, or **neighborships**, with adjacent routers to exchange this information.
- If multiple routes to a destination are learned, the router determines which route is superior and adds it to the routing table. It uses the **metric** of the route to decide which is superior (lower metric = superior).

>**Dynamic routing** uses **routing protocols** to let routers to automatically discover, share, and update routes within a network.

- Unlike static routing, dynamic routing protocols adapt to network changes automatically.

>[!important] To exchange routing information, routers form **adjacencies**, aka **neighbor relationships** or **neighborships**, with adjacent routers.

>[!important] The best route to the destination network is determined based on **metrics**. The **lowest** metric generally means the **superior** route.

IP routing protocols fall into one of two main categories:

>[!example]+
>- For example, a network created and paid for by a single company is probably a separate AS. 
>- The same goes for a large school or university network — each of these is a separate AS, too. 
>- Other examples include large divisions of state or national government. 
>- Each ISP typically has a separate AS as well.

![[ASNs_and_communication.png]]

### Types of algorithms used in routing protocols

Routing protocols can further be divided based on type of the **routing algorithm** in use.

>A **routing algorithm** is a set of processes that a routing protocol uses to share route information between routers and choose the best route to each destination.

Types of dynamic routing algorithms and protocols that use them:

- EGP (External Gateway Protocol):
	- **Path Vector**
		- BGP (Border Gateway Protocol)

- IGP (Internal Gateway Protocol):
	- **Distance Vector**
		- EIGRP (Enhanced Interior Gateway Routing Protocol)
		- RIP (Routing Information Protocol)
	- **Link State**
		- OSPF (Open Shortest Pat First)
		- IS-IS (Intermediate System to Intermediate System)

![[routing_protocols.svg]]

>[!note] To learn more about OSPF, see [[OSPF]].

>An **IGP (Interior Gateway Protocol)** is used to exchange information between routers within a single **Autonomous System (AS)**. 

>An **EGP (Exterior Gateway Protocol)** is used to exchange information between routers in different Autonomous Systems (ASs).

>An **Autonomous System (AS)** is network (a collection of routing prefixes) under the administrative control of a single entity or domain.

>[!important] The only EGP used today is **BGP (Border Gateway Protocol)**.

| IGP                                                 | Type                     | State    | Year |
| --------------------------------------------------- | ------------------------ | -------- | ---- |
| RIP (Routing Information Protocol)                  | Distance Vector          | Obsolete | 1988 |
| RIPv2                                               | Distance Vector          | Obsolete | 1998 |
| IGRP (Interior Gateway Routing Protocol)            | Distance Vector          | Obsolete | 1989 |
| EIGRP (Enhanced Interior Gateway Routing Protocol)) | Advanced Distance Vector | Standard | 2013 |
| OSPF (Open Shortest Path First)                     | Link State               | Standard | 1989 |
| IS-IS (Intermediate System to Intermediate System)  | Link State               | Standard | 1990 |

>[!important]+ Distance vector protocols
> - **Distance Vector protocols** use the **routing by rumor** method for sharing route information. Routers operate by sending the following to their directly connected neighbors:
> 	- Known destination networks
> 	- Metric to reach each destination network
>
> - Routers only learn the **distance** (metric) and the **vector** (direction, the next-hop router) of each route.
> 
>-  Examples:
> 	- **EIGRP (Enhanced Interior Gateway Routing Protocol)**
> 	- **RIP (Routing Information Protocol)**
> 
>>Routers **don't know about the networks beyond their neighbors**. They only receive information from its direct neighbors.
> 


>[!important]+ Link State protocols
> In **Link State protocols**, each router learns the **entire topology of the network**, forms its 'connectivity map'. 
> 
> 
> - Each router advertises information about its interfaces (connected networks) to its neighbors.
> - These advertisements are passed along to other routers, until all routers in the network develop the same connectivity map. 
> - Each router **independently uses this map** to calculate the best routes to each destination.
>---
>- Metric: **cost** (bandwidth-based)
>- Examples:
>	- **OSPF (Open Shortest Pat First)**
>	- **IS-IS (Intermediate System to Intermediate System)**
>
>- Link state protocols use more resources (e.g., CPU and power) on the router than other protocols, since more information is shared. But they tend to **converge faster**, i.e., they're faster in reacting to changes in the network topology than distance vector protocols.
## Metrics

>Routing protocols choose the best route to reach a subnet by choosing the route with the **lowest metric**.

Each routing protocol uses a different metric to determine which route is the best:

| IGP   | Metric                                                   | Description                                                                                                                                                                        |
| ----- | -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| RIPv2 | Hop count                                                | The total metrics is the total number of hops to the destination.<br>**Links of all speed are equal.**                                                                             |
| EIGRP | Calculation is based on bandwidth and delay (by default) | Complex formula that takes into account many values. By default, EIGRP uses the bandwidth of the **slowest link in the route** and the total delay of all links in the route.      |
| OSPF  | Cost                                                     | The cost of each link is calculated based on bandwidth. <br>The total metric is the total cost of each link in the route.                                                          |
| IS-IS | Cost                                                     | The total metric is the total cost to each link in the route.<br>The cost of each link is **not** automatically calculated by default. <br>All links have a cost of 10 by default. |

>[!important] ECMP 
>If a router learns two or more routers via the **same routing protocols** to the **same destination** (= same network address, same subnet mask) with the **same metric**, **both routes will be added to the routing table**. **Traffic will be load-balanced over both routes**. This is called **ECMP (Equal-Cost Multi-Path)** load-balancing.
>- To change the maximum number of equal-cost routes that can be used for ECMP:
>```toml
># 1. enter routing protocol configuration mode
>R1(config)# router ospf
># 2. configure the maximum number of routes for ECMP
>R1(config-router)# maximum-paths 8
>```
>- The command syntax is as follows:
>```toml
>R1(config-router)# maximum-paths ? 
>	<1-32> Number of paths
>```


>[!note] **Cost:** OSPF and IS-IS metrics 
>**Open Shortest Path First (OSPF)** and **Intermediate System-to-Intermediate System (IS-IS)** use **cost** to calculate the best path to a destination network. By default, OSPF and IS-IS calculate the cost based on bandwidth. However, cost can be configured by using any value that an administrator desires, such as the monetary cost of using a link.
## Administrative Distance (AD)

>**Administrative Distance (AD)** is a locally significant value that determines the trustworthiness of routing information sources.

In Cisco IOS software, each source of routing information, be it a dynamic routing protocol or a static route, is assigned a default AD value between `0` and `255`, with `0` being the most reliable and `255` being the least reliable source.

>[!important] When multiple routes to a network exist, a router prefers the route with the **lowest AD**.

| Routing protocol           | AD    |
| -------------------------- | ----- |
| Directly connected routes  | `0`   |
| Static routes              | `1`   |
| External BGP (eBGP)        | `20`  |
| Internal EIGRP             | `90`  |
| OSPF                       | `110` |
| IS-IS                      | `115` |
| RIP                        | `120` |
| External EIGRP             | `170` |
| Internal BGP (iBGP)        | `200` |
| Unknown/unreachable routes | `255` |
>[!warning] If AD of a route is `255`, the router doesn't believe the source of that route and doesn't install the route in the routing table.

- **Metric** is used to compare routes learned from the same routing protocol.
- Before comparing metrics, **AD** is used to select the best route source.


>[!important] You can change AD of a routing protocol or a static route on a router.

- To configure a routing protocol with a different AD on a Cisco router, use the `distance` command in the routing protocol configuration mode:

```toml
R1(config)# router ospf 1
R1(config-router)# distance 80
```

- To change the AD of a static route:

```toml
R1(config)# ip route 10.0.0.0 255.0.0.0 10.0.13.2 ?
  <1-255>  Distance metric for this route
  ...
R1(config)# ip route 10.0.0.0 255.0.0.0 10.0.13.2 100
```

>[!important]+ Floating static routes 
>A static route whose AD has been manually changed for the route to be **less preferred** than routes learned by a dynamic routing protocols to the same destination is called a **floating static route**.

- To show IP routes on a router:

```toml
R1# show ip route
```

```toml
...
Gateway of last resort is 10.19.54.20 to network 10.140.0.0

O E2 172.150.0.0 [110/5] via 10.19.54.6, 0:01:00, Ethernet2
```

- The AD is the first number inside the brackets. In the above example, the router output shows an OSPF route with an AD `110`.
- The second number in the brackets, `5` in this example, indicates the OSPF metric. 

>[!note]+
>OSPF uses **cost** as a metric and calculates it based on the **interface bandwidth**: the higher the bandwidth, the lower the cost. When two OSPF paths exist to the same destination (identical AD), the router will choose the OSPF path with the lowest cost.

