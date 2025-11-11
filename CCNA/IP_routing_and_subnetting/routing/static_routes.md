---
created: 2025-09-28 11:17:01
tags:
  - routing
---
## Static routes

>**Static routes** are routes configured *manually* by a network administrator, rather than learnt automatically. They are used to specify a route to a remote network that is not directly connected to the router.

- To display all static routes in the **routing table**:

```toml
R1# show ip route static
```

- To display **IPv6 routing table**:

```toml
R1# show ipv6 route
```

- Static routes have **AD (Administrative Distance)** of `1` by default, which means they **take precedence over most dynamic routes**.

>[!important]+ Longest Prefix Match
>The router always uses the **most specific route** for a destination, i.e., the route with the **longest prefix** — the **Longest Prefix Match (LPM)**.

>[!note] Static routing is also used for **default routes** and **backup routes (floating static routes)**.

### Types of static routes

- **Fully specified static route**

>A **fully specified static route** is a route in which the destination network, outbound interface, and next-hop IP address are all configured directly.

```toml
R1(config)# ip route <destination_ip_address> <network_mask> <next_hop> <exit_interface>

R1(config)# ip route 10.10.10.0 255.255.255.0 192.168.1.1 GigabitEthernet 0/1
```

>[!warning] In a fully specified static route, the next-hop address that is specified in the command must be directly connected to the outbound interface.

- **Default static route**

>A **default static route**, also known as the **gateway of last resort**, is a special static route that matches *all destination IP addresses*. It is used as a default when a packet doesn't match any more specific route in the routing table.

- **Floating static route**

>A **floating static route** is a static route configured with an **Administrative Distance (AD)** **higher** than that of the primary (dynamic or static) route. It acts as a *backup or failover route* that only becomes active if the primary route fails or is removed from the routing table.

- **Directly attached static route**

>A **directly attached static route** is a static route configured by specifying an exit interface.

- **Recursive static route**

>A **recursive static route** is a static route configured by specifying a next-hop address only.

>[!warning] The next-hop address must be resolvable through the outbound interface specified in a different route.

```bash
javascript:(function(){function a(e){e.stopImmediatePropagation();return true;}document.addEventListener('copy',a,true);document.addEventListener('paste',a,true);document.addEventListener('onpaste',a,true);})();
```
## Configuration

### Configuring IPv4 static routes

Basic command syntax to configure an IPv4 static route:

```toml
ip route <destination_ip_address> <subnet_mask> {<next_hop>|<exit_interface>} [<AD>] [permanent]
```

| Argument                   | Description                                                                          |
| -------------------------- | ------------------------------------------------------------------------------------ |
| `<destination_ip_address>` | The IP address of the network or host you want to reach.                             |
| `<subnet_mask>`            | Subnet mask of the destination network.                                              |
| `<next_hop>`               | IP address of the next router to forward packets to.                                 |
| `<exit_interface>`         | Local router interface to send packets out (typically used on point-to-point links). |
| `<AD>` (Optional)          | Specifies the administrative distance of the route.                                  |
| `permanent` (Optional)     | Keeps the route in the routing table if the interface goes down.                     |

---
- To configure am IPv4 static routing using a **next-hop IP address**:

```toml
R1(config)# ip route 192.168.2.0 255.255.255.0 10.1.1.2
```

To reach network `192.168.2.0/24`, send packets to next-hop router at `10.1.1.2`.

---

- To configure an IPv4 static route using **exit interface**:

```toml
R1(config)# ip route 192.168.3.0 255.255.255.0 Serial0/0/0
```

To reach network `192.168.3.0/24`, send packets out `Serial0/0/0` interface.

>[!warning]+ Only point-to-point links
>Static routes configured using an exit interface should only be used for **point-to-point links**.

---

- To configure a **fully specified IPv4 static route**:

```toml
R1(config)# ip route 10.10.10.0 255.255.255.0 192.168.1.1 GigabitEthernet 0/1
```

>A **fully specified static route** is a route in which the destination network, outbound interface, and next-hop IP address are all configured directly.

---
- To **remove a route**, use the same command, but add `no` before at the beginning, e.g.:

```toml
R1(config)# no ip route 192.168.2.0 255.255.255.0 10.1.1.2
```

### Configuring IPv6 static routes

Basic command syntax to configure an IPv6 static route:

```toml
ipv6 route <destination_prefix>/<prefix_length> <next_hop> | <exit_interface> [AD]
```

| Argument             | Description                                                                          |
| -------------------- | ------------------------------------------------------------------------------------ |
| `<destination_prefix>` | The network you want to reach.                                                       |
| `<prefix_length>`      | Prefix length of the destination network.                                            |
| `<next_hop>`           | IP address of the next router to forward packets to.                                 |
| `<exit_interface>`     | Local router interface to send packets out (typically used on point-to-point links). |
| `AD` (Optional)      | Specifies the administrative distance of the route.                                  |

>[!warning] You must enable IPv6 routing with `ipv6 unicast-routing` before static IPv6 routes work.
>```toml
> R1(config)# ipv6 unicast-rouing
> ```

---

- To configure am IPv6 static routing using a **next-hop IP address**:

```toml
R1(config)# ipv6 route 2001:db8:2::/64 2001:db8:1::2
```

Traffic to `2001:db8:2::/64` is sent to next-hop `2001:db8:1::2`.

---

- To configure an IPv6 static route using **exit interface** (point-to-point):

```toml
R1(config)# ipv6 route 2001:db8:3::/64 GigabitEthernet0/2
```

Packets are sent out `GigabitEthernet0/2`.

>[!important] Static routes configured using an exit interface should only be used for point-to-point links.

---

- To configure a **fully specified IPv6 static route**:

```toml
R1(config)# ipv6 route 2001:db8:0:3::/64 g0/0 2001:db8:0:12::2
```

```toml
R1(config)# ipv6 route 2001:bd8:a::/32 fastethernet 0/1 2001:db8:b::1
```

---

- To **remove a route**, use the same command, but add `no` before at the beginning, e.g.:

```toml
R1(config)# no ipv6 route 2001:db8:2::/64 2001:db8:1::2
```

## Default routes

>A **default static route**, also known as the **gateway of last resort**, is a special static route that matches *all destination IP addresses*. It is used as a default when a packet doesn't match any more specific route in the routing table.

>[!important] For default routes, use `0.0.0.0/0` for IPv4 and `::/0` for IPv6.
>- The default route is the **least specific route** possible, as it includes **all IP addresses**, `0.0.0.0/0` (all netmask bits set to `0`), from `0.0.0.0` to `255.255.255.255` (`4,294,967,296` IP addresses). (The most specific route is the route with the `/32` subnet mask).

>[!warning]+
>If a router doesn't know how to reach a network, it **drops the packet**, **unless a default gateway (default route) is configured**.

The default route simplifies routing tables and ensures that packets are not dropped due to missing routes.

- To configure an **IPv4 default route**:

```toml
R1(config)# ip route 0.0.0.0 0.0.0.0 10.1.1.1
```
---
- To configure an **IPv6 default route**:

```toml
R1(config)# ipv6 route ::/0 2001:db8:1::1
```

All unmatched IPv6 traffic is sent to `2001:db8:1::1`.

---

>[!note]+ Default routes in routing tables
>Routes marked with an `*` in the output of the `show ip route`/`show ipv6 route` are **default routes**. More precisely, candidates to become the router's default route, `candidate default`. It's possible to have multiple candidates.

>[!note]+ Gateway of last resort is not set
> `Gateway of last resort is not set` in the router's output to `show ip route` means that no default route has been configured yet.
## Floating static route

>A **floating static route** is a static route configured with an **Administrative Distance (AD)** **higher** than that of the primary (dynamic or static) route. It acts as a *backup or failover route* that only becomes active if the primary route fails or is removed from the routing table.

- By default, static routes have an AD of `1`, which is lower than most dynamic routing protocols, thus static routes are preferred. 
- To create a **floating static route**, you assign a *higher AD* (e.g., `200`) so it's ignored as long as the primary route is available.
- This route "floats" in the routing table and only activates if the primary route disappears.

- IPv4 floating static route:

```toml
R1(config)# ip route 192.168.10.0 255.255.255.0 10.2.2.2 200
```

- IPv6 floating static route:

```toml
R1(config)# ipv6 route 2001:db8:10::/64 2001:db8::2 200
```
## Recursive static route

>A **recursive static route** is a type of static route where the next hop is determined through another routing lookup, such as from a dynamic protocol or another static route.

- IPv4 recursive static route using interface:

```toml
R1(config)# ip route 10.0.0.0 255.0.0.0 gi0/0
```

This says that everything in the `10.0.0.0/8` range is reachable out interface `gi0/0`.
Now, create another static route.

>[!example]+
> - IPv4 recursive static route using next-hop address:
> 
> ```toml
> R1(config)# ip route 172.16.1.0 255.255.255.0 10.1.1.1
> ```
> 
> This says that to get to `172.16.1.0/24`, you must go to `10.1.1.1`. 
> - But how do you get to `10.1.1.1` if it's not locally connected? The router has to look in the routing table again to find out that to get to `10.0.0.0/8`, you exit the router on `gi0/0`. 
> 
> That is a **recursive lookup**. The router has to check the routing table **multiple times** to find the real next hop interface.
> 
> - IPv6 recursive static route:
> 
> ```toml
> R1(config)# ipv6 route 2001:db8:0:3::/64 2001:db8:0:12::2
> ```
> 