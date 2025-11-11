---
created: 2025-10-15 09:34:10
tags:
  - security
---
## ACLs

>An **Access Control List (ACL)** is a set of rules used to control inbound and outbound traffic at the subnet level within a network.

- ACLs operate at Layer 3 and Layer 4, and can filter traffic based on:
	- Source/destination **IP addresses**
	- Source/destination **TCP/UDP port numbers**
	- **Layer 4 protocol** (TCP, UDP, ICMP, etc.)
	- **Packet length**
	- **Fragmented traffic**
	- DSCP (DiffServ Code Point, see [[QoS]])

>[!important]+ ACL configuration
> - ACLs are **configured globally on the router**, and applied **per interface per direction**: 
> 	- **Inbound** 
> 	- **Outbound**
> -  **Only one ACL** can be applied **per interface per direction**.
 
>[!important] ACEs (Access Control Entries)
>An ACL consists of an ordered sequence of **ACEs (Access Control Entries)**.
> - ACEs are processes in order, **from top to bottom**. 
> - The router checks the packet against the ACLs **starting from the ACE with the lowest sequence number to the highest**.
> - If a packet matches one of ACEs in an ACL, the router takes the action and stops processing the ACL. All entries below the matching ACE will be ignored.
> - If no ACE matches, the router automatically denies the packet. 

>[!critical] By default, ACLs follow **implicit deny** rules.
## Types of ACLs

There are two main types of ACLs:

>[!important]+ **Standard ACLs**
> - Match based on **source IP address only**.
> - Standard ACLs can be:
> 	- **Standard numbered ACLs**
> 	- **Standard named ACLs**

>[!important]+ **Extended ACLs**    
> - Match based on **source/destination IP**, **source/destination port**, etc.
> - Extended ACLs can be:
> 	- **Extended numbered ACLs**
> 	- **Extended named ACLs**
## Standard ACLs

>[!important] **Standard ACLs** can filter packets **based on the source IP address only**.

There are two types of standard ACLs:

- **Standard Numbered** ACLs
- **Standard Named** ACLs
### Standard numbered ACLs

- Numbered ACLs are **identified with a number** (`1`, `2`, etc.)
- **Standard numbered ACLs can be identified with numbers `1`-`99` and `1300`-`1999`**.

>[!important]+ Numbered ACL ranges
>Different types of ACLs have a different range of numbers that can be used:
> - Standard numbered ACLs: `1`-`99` and `1300`-`1999`
> - Extended numbered ACLs: `100`-`199` and `2000`-`2699`

- Configure a **standard numbered ACL**:

```toml
R1(config)# access-list <number> {deny|permit} <source_ip_address> <wildcard_mask>
```

- Permit or deny a single host:

```toml
# with a wildcard mask:
R1(config)# access-list 1 {deny|permit} <host_ip_address> 0.0.0.0
```

```toml
# no wildcard mask implies 0.0.0.0:
R1(config)# access-list 1 {deny|permit} <host_ip_address>
```

```toml
# host keyword:
R1(config)# access-list 1 deny host <host_ip_address>
```

>[!note] The `0.0.0.0` wildcard mask denotes a single address.

 - **Permit by default** (override the deny-by-default rule), i.e., **allow any traffic**:

```toml
# with any keyword:
R1(config)# access-list 1 permit any
```

```toml
# with a wildcard mask:
R1(config)# access-list 1 permit 0.0.0.0 255.255.255.255
```

- Here're some examples with wildcard masks:

```toml
# ignore the last octet, match anything starting with 172.16.1.*
R1(config)# access-list 50 permit 172.16.1.0 0.0.0.255

# ignore the last two octets, match anything starting with 172.16.*.*
R1(config)# access-list 50 permit 172.16.0.0 0.0.255.255

# ignore the last three octets, match anything starting with 172.*.*.*
R1(config)# access-list 50 permit 172.0.0.0 0.255.255.255

```

>[!interesting]- Table of ACL number ranges
> | Protocol                              | Range                      |
> | ------------------------------------- | -------------------------- |
> | Standard IP                           | `1`-`99`, `1300`-`1999`    |
> | Extended IP                           | `100`-`199`, `2000`-`2699` |
> | Ethernet type code                    | `200`-`299`                |
> | Ethernet address                      | `700`-`799`                |
> | Transparent bridging (protocol type)  | `200`-`299`                |
> | Transparent bridging (vendor code)    | `700`-`799`                |
> | Ethernet transparent bridging         | `1100`-`1199`              |
> | DECnet and extended DECnet            | `300`-`399`                |
> | XNS (Xerox Network Systems)           | `400`-`499`                |
> | Extended XNS                          | `500`-`599`                |
> | AppleTalk                             | `600`-`699`                |
> | Source-route bridging (vendor code)   | `700`-`799`                |
> | IPX (Internetwork Packet Exchange)    | `800`-`899`                |
> | Extended IPX                          | `900`-`999`                |
> | IPX Service Advertzing Protocol (SAP) | `1000`-`1099`              |

>[!warning] When configuring/editing numbered ACLs from global configuration mode, **you can't delete individual entries, <u>you can only delete the entire ACL</u>**.

>[!important]+ Numbered ACLs configuration mode
>In modern IOS, you can also configure **numbered ACLs** in the exact same way as named ACLs:
> ```toml
> R1(config)# ip access-list standard 1
> R1(config-std-nacl)#
> ```
### Standard named ACLs

>**Named ACLs** are **identified with a name**.

Standard named ACLs are configured by entering the **standard named ACL config mode**, and then configured each entry within that config mode.

1. Enter the standard named ACL configuration mode:

```toml
R1(config)# ip access-list standard NAME
R1(config-std-nacl)#
```

- **Add an entry**:

```toml
R1(config-std-nacl)# [<entry_number>] {deny|permit} <source_ip_address> [<wildcard_mask>] 
```

>[!note]+ Entry numbers
> - Entry numbers starts with `10`.
> - By default, each entry number is `10` more than the previous one.

- **Delete an entry**:

```toml
R1(config-std-nacl)# no <entry_number>
```

For example:

```toml
R1(config)# ip access-list standard EXAMPLE_NAME
R1(config-std-nacl)# 5 deny 1.1.1.1
R1(config-std-nacl)# 10 permit any
R1(config-std-nacl)# remark EXAMPLE REMARK
R1(config-std-nacl)# interface g0/0 # enter interface config mode
R1(config-std-nacl)# ip address-group EXAMPLE_NAME in # apply ACL
```

>[!tip] Configure rules from **most specific** to **least specific**.

>[!important] ACEs configured earlier take precedence.

### Applying standard ACLs to interfaces

>[!note]+ **Standard ACLs** should be applied as **close to the destination** as possible.

>[!important] An interface can only have **two ACLs**: one for **inbound** (`in`) traffic, and another for **outbound** (`out`).

- Apply an ACLs on an interface:

```toml
R1(config)# int g0/0
R1(config-if)# ip access-group <acl_number_or_name> {in|out}
```
## Extended ACLs

>**Extended Access Control Lists (ACLs)** are a type of ACL that uses both source and destination IP addresses, as well as port numbers, to filter IP packets.

Extended ACLs are more complex to configure and require more processing power than standard ACLs, but they provide a more granular level of control.

- Extended ACLs are processed from top to bottom, just like standard ACLs.

There are two types of extended ACLs:
- **Extended Numbered ACLs**
- **Extended Named ACLs**
###  Extended numbered ACL 

>[!important]+ Numbered ACL ranges
>Different types of ACLs have a different range of numbers that can be used:
> - Standard numbered ACLs: `1`-`99` and `1300`-`1999`
> - Extended numbered ACLs: `100`-`199` and `2000`-`2699

- To configure an extended numbered ACL:

```toml
R1(config)# access-list <number> {permit|deny} 
	<protocol> 
	<source_ip_address> <wildcard_mask> 
	<destination_ip_address> <wildcard_mask>
	[<options>]
```

- Enter extended numbered/named ACL configuration mode:

```toml
R1(config)# access-list {<name>|<number>}
R1(config-ext-nacl)# [entry_numer] {permit|deny} 
	<protocol> 
	<source_ip_address> <wildcard_mask> 
	<destination_ip_address> <wildcard_mask>
	[<options>]
```

- Filter traffic based on **protocol**:

```toml
R1(config-ext-nacl)# {permit|deny} {<ip_protocol_number>|<protocol_name>}

# to deny all ICMP traffic:
R1(config-ext-nacl)# deny icmp
# or
R1(config-ext-nacl)# deny 1
```

Common IP protocol numbers:

| Number | Protocol |
| ------ | -------- |
| `1`    | ICMP     |
| `6`    | TCP      |
| `17`   | UDP      |
| `88`   | EIGRP    |
| `89`   | OSPF     |

- Filter traffic from specific IP addresses:

```toml
R1(config-ext-nacl)# deny {<ip_protocol_number>|<protocol_name>} <source_ip_address> <wildcard_mask>

# to prevent 172.16.1.1/32 from pinging hosts in 192.168.0.0/24:
R1(config-ext-nacl)# deny icmp host 172.16.1.1 192.168.0.0 0.0.0.255

# to deny all UDP traffic from 10.0.0.0/16 to 192.168.1.1/32:
R1(config-ext-nacl)# deny udp 10.0.0.0 0.0.255.255 host 192.168.1.1
```

- Allow by default:

```toml
R1(config-ext-nacl)# permit ip any any
```

>[!important] When matching TCP/UDP, you can optionally specify the source and/or destination port numbers to match.

- Filter traffic based on TCP/UDP ports:

```toml
R1(config-ext-nacl)# deny tcp SRC_IP eq SRC_PORT DEST_IP eq DEST_PORT
                                     gt                  gt
                                     lt                  lt
                                     neq                 neq
                                     range               range
```

- `eq 80` = equal to port `80`
- `gt 80` = greater than `80` (`81` and greater)
- `lt 80` = less than `80` (`79` and less)
- `neq 80` = NOT `80`
- `range 80 100` = from port `80` to port `100`

- To deny all packets destined to `1.1.1.1/32` TCP port `80`:

```toml
R1(config-ext-nacl)# deny tcp any host 1.1.1.1 eq 80
```

>[!note]+
>After the destination IP address and/or destination port numbers, there are many more options you can use to match (not necessary for the CCNA).
>For example:
>- `ack` = TCP `ACK` flag
>- `fin` = TCP `FIN` flag
>- `syn` = TCP `SYN` flag
>- `ttl` = `TTL` values
>- `dscp` = DSCP values

>[!warning]+ Match all
>If you specify the protocol, source IP address, source port, destination IP address, destination port, etc., a packet must match ALL of those values to match an ACE. Even if it matches all except one of the parameters, the packet won't match that ACE.

- To allow traffic from `10.10.0.0/16` to access the server at `2.2.2.2/32` using HTTP:

```toml
R1(config-ext-nacl)# permit tcp 10.0.0.0 0.0.255.255 2.2.2.2 0.0.0.0 eq 443
```

- To prevent all hosts using source UDP port numbers from `20000` to `30000` from accessing the server at `3.3.3.3/32`:

```toml
R1(config-ext-nacl)# deny udp any range 20000 30000 host 3.3.3.3
```

- To allow hosts in `172.16.1.0/24` using a TCP source port greater than `9999` to access all TCP ports on server `4.4.4.4/32` except port `23`:

```toml
R1(config-ext-nacl)# permit tcp 172.16.1.0 0.0.0.255 gt 9999 host 4.4.4.4 neq 23 
```

>[!tip] Place more specific rules before the general ones.
### Applying extended ACLs on an interface

>[!note]+ **Extended ACLs** should be applied as **close to the source** as possible. 

- Apply an ACLs on an interface:

```toml
R1(config)# int g0/0
R1(config-if)# ip access-group <acl_number_or_name> {in | out}
```


## Applying ACLs

- Apply an ACL to an interface:

```toml
R1(config-if)# ip access-group <acl_number_or_name> {in | out}
```

- Apply an ACL to an IPv6 interface:

```toml
R1(config-if)# ipv6 traffic-filter <acl_number_or_name> {in | out}
```

- Apply an IPv4 ACL to a VTY line, AUX line, or the console line:

```toml
R1(config-if)# access-class <acl_number_or_name> {in | out}
```
## The wildcard mask

More often than not, the goal of an ACL is not to match a single IP address but rather a **range of addresses**, e.g., all addresses in a subnet or across several subnets. 

>[!important] ACLs use a **wildcard mask** (WC mask) to match a range of IP address.

Wildcard masks are reverse to regular subnet masks; they tell the router which parts of the IP address to ignore during matching.

>[!example] 
>For example, a wildcard mask of `0.0.0.255` tells the ACL to ignore the last octet of the IP address:
>![[wildcard.svg]]
>- `0.0.255.255` ignores the last two octets.
>- `0.255.255.255` ignores the last three octets.


![[most-common-wildcard-masks.svg]]

>[!important] A wildcard mask does not need to be continuous.
>The bits can be mixed — some 0s, some 1s — anywhere.

## General commands

### Show commands

- Show ACLs on a router:

```toml
R1# show access-lists
```

- To **show ACLs** configured on a router:

```toml
R1(config)# do show ip access-lists

# or 
R1(config)# do show running-config | include access list
```
### Default policy 

- To set a **default policy** of an ACL:

```toml
R1(config)# access-list 1 permit any
# or
R1(config)# access-list 1 permit 0.0.0.0 255.255.255.255
```
### Applying IPv4/IPv6 ACLs

- To **apply an ACL to an IPv4 interface**:

```toml
R1(config-if)# ip access-group number {in | out}
```

>The **`ip access-group`** command can be used to apply an ACL to an IPv4 interface. You can configure each interface on a router with one inbound ACL and one outbound ACL.

- To **apply an ACL to an IPv6 interface**:

```toml
R1(config-if)# ipv6 traffic-filter IPv6_ACL {in | out}
```

>An ACL will only take effect when applied on an interface.

- To **apply an IPv4 ACL to a `vty` line, AUX line, or console line**:

```toml
access-class ACL_NAME_OR_NUMBER {in | out}
```

- To **apply an IPv4 ACL to a `vty` line, AUX line, or console line**:

```toml
ipv6 access-class command is ipv6 access-class IPv6_ACL {in | out}.
```

### Creating remarks

- To **configure a remark** of an ACL:

```toml
R1(config)# access-list 1 remark REMARK TEXT
```

### Deleting ACLs

- Delete a named ACL:

```toml
R1(config)# no ip access-list {extended|standard} <acl>
```

- To delete a numbered ACL:

```toml
R1(config)# no access-list <acl>
```

## Lab: standard ACLs


![[standard_ACL_lab1.png]]

- Only PC 1 and PC 3 can access `192.168.1.0/24`
- Hosts in `172.16.2.0/24` can't access `192.168.2.0/24`
- `172.16.1.0/24` can't access `172.16.2.0/24`
- `172.16.2.0/24` can't access `172.16.1.0/24`

---

- First, allow PC 1 and PC 3 access `192.168.1.0/24`. This should be done on **`R2`**, since **standard ACLs should be configured as close to the destination as possible**.
- On `R2`, we need to configure **standard named ACLs**.
- `PC1` has address `172.16.1.1`, and `PC3` has address `172.16.2.1`. 

```toml
R2(config)# ip access-list standard TO_192.168.1.0/24
R2(config-std-nacl)# permit host 192.16.1.1
R2(config-std-nacl)# permit host 192.16.2.1
R2(config-std-nacl)# exit

R2(config)# do show access-lists
Standard IP access list TO_192.168.1.0/24
	10 permit host 192.16.1.1
	20 permit host 192.16.2.1

R2(config)# int g0/0
R2(config-if)# ip access-group TO_192.168.1.0/24 out
```

---

- Then, deny hosts in `172.16.2.0/24` from accessing `192.168.2.0`:

```toml
R2(config)# ip access-list standard TO_192.168.2.0/24
R2(config-std-nacl)# deny 172.16.2.0 0.0.0.255

R2(config)# do show access-lists
Standard IP access list TO_192.168.1.0/24
	10 permit host 192.16.1.1
	20 permit host 192.16.2.1
Standard IP access list TO_192.168.2.0/24
	10 deny 172.16.2.0 0.0.0.255
	
R2(config)# int g0/1
R2(config-if)# ip access-group TO_192.168.2.0/24 out
```

---

- Then, configure `R1` with these rules:
	- `172.16.1.0/24` can't access `172.16.2.0/24`
	- `172.16.2.0/24` can't access `172.16.1.0/24`

```toml
R1(config)# access-list 1 deny 172.16.1.0 0.0.0.255 
R1(config)# access-list 2 deny 172.16.2.0 0.0.0.255 
R1(config)# int g0/1
R1(config-if)# ip access-group 1 out
R1(config-if)# ing g0/0
R1(config-if)# ip access-group 2 out
R1(config-if)# exit
R1(config)# do show access-lists
Standard IP access list 1
Standard IP access list 2
	10 deny 172.16.2.0 0.0.0.255
```


## Lab: extended ACLs

![[extended_ACL_lab1.png]]

- Hosts in `172.16.2.0/24` can't communicate with `PC1`.
- Hosts in `172.16.1.0/24` can't access the DNS service on `SRV1`
- Hosts in `172.16.2.0/24` can't access the HTTP or HTTPS services on `SRV2`.

- Extended ACLs should be applied as **close to the source** as possible. 

- So, on `R1`, we need to restrict all traffic from `172.16.2.0/24` to `172.16.1.1` (`PC1`) and HTTP/HTTPS on `192.168.2.100` (`SRV2`):

```toml
R1(config)# ip access-list extended FROM_172.16.2.0/24
R1(config-ext-nacl)# deny ip 172.16.2.0 0.0.0.255 host 172.16.1.1
R1(config-ext-nacl)# deny tcp 172.16.2.0 0.0.0.255 host 192.168.2.100 eq 80
R1(config-ext-nacl)# deny tcp 172.16.2.0 0.0.0.255 host 192.168.2.100 eq 443

R1(config)# do show access-list
Extended IP access list FROM_172.16.2.0/24
10 deny ip 172.16.2.0 0.0.0.255 host 172.15.1.1
20 deny tcp 172.16.2.0 0.0.0.255 host 192.168.2.100 eq www
30 deny tcp 172.16.2.0 0.0.0.255 host 192.168.2.100 eq 443

R1(config)# int g0/1
R1(config-if)# ip access-group FROM_172.16.2.0/24 in
```

- To restrict traffic from `172.16.1.0/24` to DNS on `192.168.1.100` (`SRV1`):

```toml
R1(config)# ip access-list extended TO_SRV1
R1(config-ext-nacl)# deny udp 172.16.1.0 0.0.0.255 host 192.168.1.100 eq 53

R1(config)# do show ip access-list
Extended IP access list FROM_172.16.2.0/24
    10 deny ip 172.16.2.0 0.0.0.255 host 172.15.1.1
    20 deny tcp 172.16.2.0 0.0.0.255 host 192.168.2.100 eq www
    30 deny tcp 172.16.2.0 0.0.0.255 host 192.168.2.100 eq 443
Extended IP access list TO_SRV1
    10 deny udp 172.16.1.0 0.0.0.255 host 192.168.1.100 eq domain

R1(config-if)# ip access-group TO_SRV1 in
```