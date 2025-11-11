---
created: 2025-10-28 03:44:47
tags:
  - routing
---
## Private IP address

[`RFC 1918`](https://datatracker.ietf.org/doc/html/rfc1918) defines three private IPv4 address ranges:

| Class | CIDR notation    | Range                           | `#`      | Address         |
| ----- | ---------------- | ------------------------------- | -------- | --------------- |
| A     | `10.0.0.0/8`     | `10.0.0.0`-`10.255.255.255`     | `16.78M` | `10.x.x.x`      |
| B     | `172.16.0.0/12`  | `172.16.0.0`-`172.31.255.255`   | `1.05M`  | `172.16-31.x.x` |
| C     | `192.168.0.0/16` | `192.168.0.0`-`192.168.255.255` | `65.5K`  | `192.168.x.x`   |

>[!important] Private IP addresses can not be used over the Internet. An ISP will simply drop the packets destined to or from private IP addresses.

>[!note] For more information on IPv4 addresses, see [[IPv4_addressing]].

NAT (Network Address Translation) can be used to *translate* private IP addresses into public. Actually, it can translate any one type of addresses into another.

## Inside/outside local/global addresses

>[!important] Inside and outside hosts
>- An **inside host** refers to a host **withing a local network**.
>- An **outside host** refers to a host **outside of a local network**.

>[!important]
>- **Inside Local address** is the IP address of the inside host, from the perspective of the local network.

- An inside local address is the address either configured manually on the OS or received via a dynamic address allocation protocol such as DHCP. 
- Inside local addresses are usually private addresses under IP address ranges specified in RFC 1918, e.g., `192.168.1.9`.

>[!important]
>**Inside Global address** is the IP address of the inside host, from the perspective of outside hosts.

- In other words, an inside global address is an IP address after network address translation (NAT), usually a public IP address.

>[!important]
>**Outside Local address** is the IP address of the outside host, from the perspective of the local network. 

>[!important]
>**Outside Global address** is the IP address of the outside host, from the perspective of the outside network.

>[!note]
>Unless destination NAT is used, *Outside Global* and *Outside Local* addresses are the same (i.e., no translation).

| Address                    | Host    | Perspective          |
| -------------------------- | ------- | -------------------- |
| **Inside Local address**   | Inside  | Local network        |
| **Inside Global address**  | Inside  | Outside networks     |
| **Outside Local address**  | Outside | Local network<br>    |
| **Outside Global address** | Outside | Outside networks<br> |
>**Inside/Outside** = Location of the host.
>**Local/Global** = Perspective


## NAT

>**NAT (Network Address Translation)** is used to modify the source and/or destination IP addresses of packets.

There're various reasons to use NAT, but the most common reason is to allow hosts with private IP addresses to communicate with other hosts over the Internet; that's why we will mostly discuss NAT in this context.

Additionally, NAT allows multiple internal hosts to share a single public IP address, which can decrease the number of public IP addresses needed for a network. 

>[!tip] 
>Addresses don't have to be private or public. NAT can map any address to any other address.

There are three types of NAT:

- **Static NAT**
- **Dynamic NAT**
- **NAT Overload (PAT)**


## Static NAT

>With Static NAT, an inside local IP address is always translated to the  same inside global IP address.
 
>[!note] Static NAT:
> - Creates one-to-one mappings from the same private IP addresses to the same public IP addresses. The mapping is static and configured manually.
> - Doesn't conserve public IP address space.
> - Doesn't scale.
> - Allows hosts on the outside to initiate connections with hosts on the inside.

>[!important]
>Static NAT allows devices with private IP addresses to communicate over the Internet.
>However, because it requires a one-to-one IP address mapping, it doesn't help preserve public IP addresses.

![[static_NAT.svg]]

To configure **Static NAT**:

1. Define the **inside** interface(s) connected to the *internal* network:

```toml
R1(config)# int g0/1
R1(config-if)# ip nat inside
```

2. Define the **outside** interface(s) connected to the *external* network:

```toml
R1(config)# int g0/1
R1(config-if)# ip nat outside
R1(config-if)# exit
```

3. Configure the NAT rules:

```toml
R1(config)# ip nat inside source static 10.0.0.1 1.1.1.1
R1(config)# ip nat inside source static 10.0.0.2 1.1.1.2
R1(config)# exit
```

A command to configure static one-to-one IP address mappings:

```toml
ip nat inside source static INSIDE_LOCAL_IP INSIDE_GLOBAL_IP
```

To show NAT configuration:

```toml
R1# show ip nat translations
```

```toml
Pro Inside global  Inside local    Outside local  Outside global
udp 1.1.1.1:56310  10.0.0.1:56310  8.8.8.8:53     8.8.8.8:53
--- 1.1.1.1        10.0.0.1        ---            ---
udp 1.1.1.2:62321  10.0.0.2:62321  8.8.8.8:53     8.8.8.8:53
--- 1.1.1.2        10.0.0.2        ---            ---
```

>[!note]
>`Pro` means protocol, such as `udp`.

>[!Important] Unless **destination NAT** is used, the Outside local and Outside global addresses will be the same.

- To clear **dynamic NAT** entries (created each time NAT is used, even static):

```toml
R1# clear ip nat translation *
```

After that, the NAT translation table will look somewhat like this:

```toml
Pro Inside global  Inside local    Outside local  Outside global
--- 1.1.1.1        10.0.0.1        ---            ---
--- 1.1.1.2        10.0.0.2        ---            ---
```

- To display detailed NAT statistics:

```toml
R1# show ip nat statistics
```

>[!important]
>This one-to-one mapping of IP address doesn't only allow the internal host to access external resources, it also allows external hosts to access the internal host via the **inside global address**.
>

## Dynamic NAT

>In **dynamic NAT**, the router dynamically maps *inside local* addresses to *inside global* addresses as needed.

>[!important]+ An ACL is used to **identify** which traffic should be translated.
> - If the source IP address is **permitted** by the ACL, the source IP address will be translated by NAT.
> - If the source IP address is **denied** by the ACL, the source IP address **will not be translated**. However, **the traffic will not be dropped**.

>[!important] A **NAT pool** is used to define the available **inside global** addresses.

>[!note]
>ACLs can be used not only to indicate which traffic should be forwarded and which should be blocked, but also just **identify** traffic.

>[!note] Dynamic NAT doesn't conserve public IP address space.
>Although dynamically assigned, the mappings are still one-to-one (one *inside local* IP address per *inside global* IP address).

>[!warning]
>If a packet from another inside host arrives and needs NAT but there are no available addresses, the router will **drop the packet**.
>The host will be **unable** to access outside networks until one of the *inside global* IP addresses becomes available.

>[!important] Dynamic NAT entries will **time out** automatically after some time if not used, or you can clear them manually (`clear ip nat translations *`).


>[!important] Two private IP addresses can not translate to the same public IP address. 
>For this, you will have to use **PAT (Port Address Translation)**.

To configure **Dynamic NAT**:

1. Define the **inside** interface(s) connected to the *internal* network:

```toml
R1(config)# int g0/1
R1(config-if)# ip nat inside
```

2. Define the **outside** interface(s) connected to the *external* network:

```toml
R1(config)# int g0/1
R1(config-if)# ip nat outside
R1(config-if)# exit
```

3. Define the  traffic that should be translated (traffic permitted by the ACL):

```toml
R1(config)# access-list 1 permit 10.1.0.0 0.0.0.255
```

4. Define the pool of inside global IP addresses:

```toml
R1(config)# ip nat pool POOL1 1.1.1.1 1.1.1.255 prefix-length 24
# or, equivalently
R1(config)# ip nat pool POOL1 1.1.1.1 1.1.1.255 255.255.255.0
```

5. Configure dynamic NAT by mapping the ACL to the pool:

```toml
R1(config)# ip nat inside source list 1 pool POOL1
```

>[!important] Dynamic NAT entries expiration time
>- The original dynamic mappings have a default timeout value of **24 hours**. Each time a translation is made, the timer resets.
>- The translations made when the mappings are actually used will be cleared after about a minute after creation. 

## PAT (NAT Overload)

>**PAT (Port Address Translation)**, aka **NAT overload**, translates **multiple inside local IP addresses into a single inside global public IP address**.

>[!important]
>PAT uniquely identifies each communication flow with a port number.
>Each port number is `16` bits, so there're over `65,000` available port numbers.
>This means that PAT can simultaneously map over `65,000` communication to a single public IP address.

>[!important] In PAT, a single public IP address can be used by many different internal hosts.

>[!note] PAT is the most widely used type of NAT.

When there are no more ports available, and there is more than one external IP address configured, PAT moves to the next IP address and tries to allocate the original source port again. This process continues until it runs out of available ports and external IP addresses.

>[!note] How port numbers are assigned
>PAT attempts to preserve the original source port (the ephemeral port on the sender device OS). If this source port is already used, PAT assigns the first available port number starting from the beginning of the corresponding port group (`0`-`511`, `512`-`1,023`, or `1024`-`65,535`).

To configure **PAT**:

1. Define the **inside** interface(s) connected to the *internal* network:

```toml
R1(config)# int g0/1
R1(config-if)# ip nat inside
```

2. Define the **outside** interface(s) connected to the *external* network:

```toml
R1(config)# int g0/1
R1(config-if)# ip nat outside
R1(config-if)# exit
```

3. Define the  traffic that should be translated (traffic permitted by the ACL):

```toml
R1(config)# access-list 1 permit 10.1.0.0 0.0.0.255
```

4. Define the pool of inside global IP addresses:

```toml
R1(config)# ip nat pool POOL1 1.1.1.1 1.1.1.255 prefix-length 24
# or, equivalently
R1(config)# ip nat pool POOL1 1.1.1.1 1.1.1.255 255.255.255.0
```

5. Configure dynamic NAT by mapping the ACL to the pool with **NAT overload**:

```toml
R1(config)# ip nat inside source list 1 pool POOL1 overload
```

## Show commands


To show NAT translation tables:

```toml
R1# show ip nat translations
```

The `show ip nat translations` command displays five fields of information for each NAT translation session:

- Protocol
	- Displays the type of protocol in the translates session, such as Internet Control Message Protocol (ICMP), Transmission Control Protocol (TCP), or User Datagram Protocol (UDP).
- Inside global address
	- Displays an IP address that represents an inside host as seen by hosts on the outside network.
- Inside local address 
	- Displays the IP address configured on a host on the local network. 
- Outside local address
	- Displays the IP address of the host on the outside network as seen from a host on the inside network. 
- Outside global address 
	- Displays the IP address configured on a host on the outside network. 


To show NAT statistics:

```toml
R1# show ip nat statistics
```

To show NAT configuration:

```toml
R1# show run | include nat
```
## Quiz

1. Which of the following commands will configure a static source NAT mapping of `192.168.10.10` to `203.0.113.10`?

	- a. `R1(config)# ip nat inside source static 203.0.113.10 192.168.10.10`

	- b. `R1(config)# ip nat inside static source 192.168.10.10 203.0.113.10`
	
	- c. `R1(config)# ip nat source inside static 203.0.113.10 192.168.10.10`
	
	- d. `R1(config)# ip nat inside source static 192.168.10.10 203.0.113.10`

2. You have configured the following command on R1. What happen if you issue the next command?
	- a. `10.0.0.1` and `10.0.0.2` will both be translated to `20.0.0.1`
	- b. Only `10.0.0.1` will be translated to `20.0.0.1`
	- c. Only `10.0.0.2` will be translated to `20.0.0.1`
	- d. `20.0.0.1` will be translated to `10.0.0.1` or `10.0.0.2`

```
R1(config)# ip nat inside source static 10.0.0.1 20.0.0.1

R1(config)# ip nat inside source static 10.0.0.2 20.0.0.1
```

3. Examine the following partial `show` command output on R1. How many active translations will there be if you issue the `clear ip nat translation *` command on R1?
	- a. `0`
	- b. `3`
	- c. `4`
	- d. `7`

```
R1# show ip nat statistics
Total active translations: 7 (3 static, 4 dynamic; 0 extended)
```

4. Which of the following are private IPv4 addresses? (select all that apply)
	- a. `10.254.255.0`
	- b. `192.169.0.1`
	- c. `172.32.1.22`
	- d. `192.191.20.2`
	- e. `172.20.2.3`
	- f. `10.11.12.13`

5. Which of the following NAT types best fulfills the goal of preserving public IPv4 addresses?
	- a. Static NAT
	- b. Source NAT
	- c. Dynamic NAT
	- d. NAT Overload

6. After specifying the inside and outside NAT interfaces, you issue the following commands on R1. What will happen to hosts from the `192.168.1.0/24` subnet?
	- a. The source IP of their packets will be translated to an address from `203.0.113.0/24`
	- b. The packets they send will be discarded by R1.
	- c. The packets they send will not be translated by R1.
	- d. The packets they send will be discarded until inside global address is available.

```
access-list 1 permit 10.0.1.0 0.0.0.255
access-list 1 deny 192.168.1.0 0.0.0.255
ip nat pool POOL1 203.0.113.0 203.0.113.255 netmask 24
ip nat inside source list 1 pool POOL1
```


| Question | Answer           |
| -------- | ---------------- |
| `1.`     | `d.`             |
| `2.`     | `b.`             |
| `3.`     | `b.`             |
| `4.`     | `a.`, `e.`, `f.` |
| `5.`     | `d.`             |
| `6.`     | `c.`             |
| `7.`     | `d.`             |



3. n
	- a. 
	- b. 
	- c. 
	- d. 