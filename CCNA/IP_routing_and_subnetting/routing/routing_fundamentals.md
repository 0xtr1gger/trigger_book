---
created: 2025-09-28 11:16:09
tags:
  - routing
---

## Routing

>**Routing** is the process that routers use to determine the path that IP packets should take over a network to reach the destination.

- **Routers** operate at Layer 3 (Network layer) of the OSI model.

>[!important] Routers store routes to all of their known destinations in a **routing table**.

### Static vs. dynamic routing

There are two main **routing methods** (methods that routers use to learn routes):

- **Static routing**
	- Routes are **manually configured** by a network administrator on each router.
	- Not scalable for large or frequently changing networks.

- **Dynamic routing**
	- Routers use **dynamic routing protocols**, such as OSPF, to automatically share routing information with each other and build their routing tables. 
	- Routing protocols adapt to network changes automatically.

## Routes and routing tables

>[!note]+ Routes
>A **route** tells the router: to send a packet to destination `X`, you should send the packet to next-hop `Y`.
>- *If the destination is directly connected to the router, send the packet there.*
>- *If the destination is the router's own IP address, receive the packet for yourself (don't forward).*

>[!important] **Next-hop** = the next router in the path to the destination.

- A routing table is typically stored in the **RAM (Random Access Memory)** of forwarding devices (routers and Layer 3 switches). 
- Each routing table is unique and acts as an address map for networks the router can reach.

- To show the routing table:

```toml
R1# show ip route
```


>[!example]+ Example: `show ip route`
>```toml
>R1# show ip route
>```
>
>```toml
> Codes: L - local, C - connected, S - static, R - RIP, M -mobile, B - BGP
> 	D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area
>     N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2
>     E1 - OSPF external type 1, E2 - OSPF external type 2 
>     i - IS-IS, su - IS-IS summary, L1 - IS-IS level-1, L2 - IS-IS level-2
>     ia - IS-IS inter area, * - candidate default, U - per-user static route
>     o - ODR, P - periodic downloaded static route, H - HNRP, l - LIST
>     a - application route
>     + - replicated route, % - next hop override, p - overrides from PfR
> 
> Gateway of last resort is not set
> 
>      192.168.1.0/24 is variably subnetted, 2 subnets, 2 masks
>  C       192.168.1.0/24 is directly connected, GigabitEthernet0/2
>  L       192.168.1.1/32 is directly connected, GigabitEthernet0/2
>     192.168.12.0/24 is variably subnetted, 2 subnets, 2 masks
>  C       192.168.12.0/24 is directly connected, GigabitEthernet0/1
>  L       192.168.12.1/32 is directly connected, GigabitEthernet0/1
>     192.168.13.0/24 is variably subnetted, 2 subnets, 2 masks
>  C       192.168.13.0/24 is directly connected, GigabitEthernet0/1
>  L       192.168.13.1/32 is directly connected, GigabitEthernet0/1
> ```

A routing table typically stores the following:

| Field                       | Notes                                                                                                                                             |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Destination network ID**  | The destination network of the route (network IP address + subnet mask).                                                                          |
| **Next-hop (gateway)**      | IP address of the next router to send the packet to.<br>                                                                                          |
| **Outgoing interface**      | Local interface to use to reach the next hop (e.g., `eth0`, `br0`).                                                                               |
| **Metric**                  | A routing **metric** indicates the cost associated with the route; used to determine route efficiency and compare routes to the same destination. |
| **Route source/code**       | How the route was learned (e.g., `C`=Connected, `L`=Local, `S`=Static, `O`=OSPF, `D`=EIGRP, `R`=RIP)                                              |
| **Flags**                   | Used to describe the destination network.                                                                                                         |
| **Administrative Distance** | **Administrative Distance (AD)** of the route; trustworthiness of the route source.                                                               |

>[!note] To learn more about metrics, administrative distances, and dynamic protocols, see [[dynamic_routing]].

>[!important] Routers never flood packets.

>[!note] **Codes** in the routing table indicate how the route was learned:
> - `C` = Connected
> - `L` = Local
> - `S` = Static
> - `O` = OSPF
> - `D` = EIGRP
> - `R` = RIP
> - `*` = Default route

>[!note] Routes marked with an `*` in the output of the `show ip route`/`show ipv6 route` are **default** routes. 

>[!important] A route **matches** a packet's destination if the packet's destination IP address is part of the network specified in the route. 
## Connected and local routes

There are two types of routes created automatically as soon as an interface is assigned an IP address and turned on; they are considered neither static nor dynamic:
- **Connected routes**
	- "Directly connected network ID"
- **Local routes**
	- "For me route"

>[!important] Connected and local routes are automatically added to the routing table for each active interface with an IP address configured.
### Connected routes

>A **connected route** is a route is the route to the network the interface is connected to.

- A connected route provides a route to **all host in that network**, i.e., it stores the **network ID** (the host portion of the address is set to all `0`).

- The destination address of a connected route is the address of the network the interface is connected to (the network ID, with the host portion set to all `0`).

>[!important] Connected routes are added to the routing table automatically and always take precedence over static or dynamic routes.
>- By default, connected routes have the **lowest administrative distance (AD)** value of `0`.

### Local routes

>A **local route** is a route to the actual IP address configured on the interface.

- Local routes always have the `/32` subnet mask.
- Local routes are used to forward packets sent to the router itself.
- Same as connected routes, local routes are configured automatically.

>**Local route** = keep the packet, don't forward it.

>[!important]
>If the destination address of a packet matches several routes in the routing table, the router will use the **most specific matching route** (with the longest prefix length).

>[!important] The **most specific** matching route is the matching route with the **longest prefix length** (shortest host part of the address).

## Not routes

But what do these `variably connected` lines mean?

```bash
     192.168.1.0/24 is variably subnetted, 2 subnets, 2 masks
 #C       192.168.1.0/24 is directly connected, GigabitEthernet0/2
 #L       192.168.1.1/32 is directly connected, GigabitEthernet0/2
    192.168.12.0/24 is variably subnetted, 2 subnets, 2 masks
 #C       192.168.12.0/24 is directly connected, GigabitEthernet0/1
 #L       192.168.12.1/32 is directly connected, GigabitEthernet0/1
    192.168.13.0/24 is variably subnetted, 2 subnets, 2 masks
 #C       192.168.13.0/24 is directly connected, GigabitEthernet0/1
 #L       192.168.13.1/32 is directly connected, GigabitEthernet0/1
```

- These three lines are **not routes**.

- They mean the following:

- `192.168.1.0/24 is variably subnetted, 2 subnets, 2 masks`
	- In the routing table, there are two routes to subnets that fit within the `192.168.1.0/24` Class C network, with two different netmasks (`/24` and `/32`).

- `192.168.12.0/24 is variably subnetted, 2 subnets, 2 masks`
	- In the routing table, there are two routes to subnets that fit within the `192.168.12.0/24` Class C network, with two different netmasks (`/24` and `/32`).

- `192.168.13.0/24 is variably subnetted, 2 subnets, 2 masks`
	- In the routing table, there are two routes to subnets that fit within the `192.168.13.0/24` Class C network, with two different netmasks (`/24` and `/32`).

Generally, these lines can be ignored in the routing tables, if we focus on the routes themselves.
## Host and network routes

Routes in a routing table can be either **host routes** or **network routes**.

>A **network route** is a route to a network or subnet (mask length < `/32`).

>A **host route** is a route to a specific host (`/32` mask for IPv4 and `/128` for IPv6).

>[!example]+ Example: host route
> 
> ```toml
> R1# show ip route
> ```
> 
> ```toml
> ...
> L 192.168.1.1/32 is directly connected, FastEthernet0/0
> ...
> ```
## Quiz

1. The IP address configured on a router interface will appear in the router table as that kind of route?
	- a. Static
	- b. Connected
	- c. Local
	- d. Dynamic

2. Examine the R1's routing table. What will it do when it receives a packet destined for `192.168.3.25`?
	- a. Drop the packet.
	- b. Receive the packet for itself.
	- c. Forward out of the `G0/0` interface.
	- d. Forward out of the `G0/2` interface.


3. Which of the following statements about the behavior of routers and switches are true (select two)?
	- a. Routers flood packets with an unknown destination.
	- b. Switches flood packets with an unknown destination.
	- c. Routers drop packets with an unknown destination.
	- d. Switches drop packets with an unknown destination.

4. Which two types of routes are automatically added to the routing table when you configure an IP address on an interface and enable it?
	- a. `C`, `L`
	- b. `C`, `S`
	- c. `L`, `S`
	- d. `L`, `D`

5. Examine R1's routing table below. If R1 receives a packet destined for `10.0.1.23`, how many routes match that destination?
	- a. One matching route: `10.0.1.0/24`
	- b. One matching route: `10.0.1.23/32`
	- c. Two matching routes: `10.0.1.0/24`, `10.0.1.23/32`. Most specific: `10.0.1.23/32`.
	- d. Two matching routes: `10.0.1.0/24`, `10.0.1.23/32`. Most specific: `10.0.1.0/24`.

```bash
     10.0.0.0/24 is variably subnetted, 2 subnets, 2 masks
 C       10.0.0.0/24 is directly connected, GigabitEthernet0/0
 L       10.0.0.1/32 is directly connected, GigabitEthernet0/0
    10.0.2.0/24 is variably subnetted, 2 subnets, 2 masks
 C       10.0.2.0/24 is directly connected, GigabitEthernet0/1
 L       10.0.2.0/32 is directly connected, GigabitEthernet0/1
    10.0.1.0/24 is variably subnetted, 2 subnets, 2 masks
 C       10.0.1.0/24 is directly connected, GigabitEthernet0/2
 L       10.0.1.23/32 is directly connected, GigabitEthernet0/2
```

6. Boson ExSim. Which of the following entries in the `show ip route` command indicates a host route? (Select the best answer.)
	- a. `L  192.168.1.1/32 is directly connected, FastEthernet0/0`
	- b. `O  192.168.1.0/24 [110/2] via 10.1.1.13, 00:00:08, FastEthernet0/0`
	- c. `S  192.168.1.0/24 [5/0] via 10.1.2.3`
	- d. `C  192.168.1.o/30 is directly connected, FastEthernet0/0`
	- e. `D  192.168.0.4/3 [90/2195456] via 192.168.0.18, 00:03:31, FastEthernet0/0`
	- f. `S* 0.0.0.0/0 [1/0] via FastEthernet0/0`

7. Boson ExSim. Which of the following codes from the output of the `show ip rotue` command indicates that the route is a default route? (Select the best answer.)
	- a. `*`
	- b. `s`
	- c. `EX`
	- d. `D`

| Question | Answer     |
| -------- | ---------- |
| `1.`     | `c.`       |
| `2.`     | `a.`       |
| `3.`     | `b.`, `c.` |
| `4.`     | `a.`       |
| `5.`     | `c.`       |
| `6.`     | `f.`       |
| `7.`     | `*`        |
| `8.`     |            |
| `9.`     |            |
| `10.`    |            |
