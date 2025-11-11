---
created: 2025-09-26 05:55:51
tags:
  - IP
  - routing
---

>[!tip] For subnetting practice resources, see [`subnettingpractice.com`](https://subnettingpractice.com/).
## Subnetting 

> A **subnetwork**, or **subnet**, is a a logical subdivision of an IP network.

>A **subnet** is a logical subset of a larger network, created by an administrator to improve network performance or to provide security.

- All devices on the same subnet will have the same network identifier.
- The size of a network prefix is determined by the **subnet mask**.

>**Subnet mask** is a 32-bit bitmask that, when applied to any IP address in the network by a bitwise AND operation, yields the network address. In other words, a subnet mask divides an IP address into the network part and the host part.

One of the main purposes of creating subnets is efficient routing of network packets based on IP addresses.

>[!note]
>- Devices within the same subnet are not separated by a router (i.e., communication occurs only at the Layer 2).
>- Devices in different subnets are separated by at least one router.

>[!note]- One subnet per every:
>- **VLAN**
>- **Point-to-point WAN link** (subnets that consist of only 2 addresses)
>- **Ethernet LAN**
>
>![[subnets.png]]
## CIDR and subnet masks

>**CIDR (Classless Inter-Domain Routing)** is a method for allocating IP addresses and routing internet traffic that uses **VLSM (Variable-Length Subnet Masking)**.

>[!note] CIDR was designed to replace the old classful subnetting system.

>[!important] CIDR uses a **prefix length** that specifies how many bits of the `32`-bit IPv4 address represent the network portion.

A subnet mask can be written in three different formats:

- **Binary notation**
	- The subnet mask is a **32-bit** number with a series of 1s followed by 0s.

- **Dotted-Decimal Notation (DDN)**
	- Each byte is converted into a decimal equivalent; the result four numbers are concatenated with dots.

- **Prefix** (aka prefix, prefix mask, CIDR mask)
	- Represents a number that indicates the number of binary `1` in the bitmask, following a slash.
	- For example, `/24`, `/27`, `/20`, etc.

| CIDR Notation | DDN               | Binary Representation                 |
| ------------- | ----------------- | ------------------------------------- |
| `/24`         | `255.255.255.0`   | `11111111.11111111.11111111.00000000` |
| `/26`         | `255.255.255.192` | `11111111.11111111.11111111.11000000` |
| `/28`         | `255.255.255.240` | `11111111.11111111.11111111.11110000` |

>[!important] IPv4 address classes
> 
> | Class | First octet | First octet range | Address ranges                | Prefix length |
> | ----- | ----------- | ----------------- | ----------------------------- | ------------- |
> | `A`   | `0xxxxxxx`  | `0`-`127`         | `0.0.0.0`-`127.255.255.255`   | `/8`          |
> | `B`   | `10xxxxxx`  | `128`-`191`       | `128.0.0.0`0`191.255.255.255` | `/16`         |
> | `C`   | `110xxxxx`  | `192`-`223`       | `192.0.0.0`-`223.255.255.255` | `/24`         |
> | `D`   | `1110xxxx`  | `224`-`239`       | `224.0.0.0`-`239.255.255.255` |               |
> | `E`   | `1111xxxx`  | `240`-`255`       | `240.0.0.0`-`255.255.255.255` |               |
> 

## Key formulas for subnetting

### Number of subnets

- To create subnets, we **borrow bits from the host portion**.
- Each borrowed bit *doubles* the number of subnets.

>[!important]+ Number of subnets
> $$
> \text{Number of subnets} = 2^n
> $$
> - $n$ = network bits.

### Number of hosts per subnet

>[!important] Number of usable host addresses
> 
> $$
> \text{Usable addresses}=2^k - 2
> $$
> - $k$ = number of host bits = $32 - n$
>
>Here, we subtract 2 because of network and broadcast addresses.

>[!example]- Example: usable addresses
>- `203.0.113.0/25` (`255.255.255.128`)
>	- $32 - 25 = 7$; $2^7 - 2 = 128 - 2 = 126$ usable addresses.
>	- `203.0.113.1`- `203.0.113.126`
>---
>- `203.0.113.0/26` (`255.255.255.192`)
>	- $32 - 26 = 6$; $2^6 - 2 = 64 - 2 = 62$ usable addresses.
>	- `203.0.113.1`- `203.0.113.62`
>---
>- `203.0.113.0/27` (`255.255.255.224`)
>	- $32 - 27 = 5$; $2^5 - 2 = 32 - 2 = 30$ usable addresses.
>	- `203.0.113.1`- `203.0.113.30`
>---
>- `203.0.113.0/28` (`255.255.255.240`)
>	- $32 - 28 = 4$; $2^4 - 2 = 16 - 2 = 14$ usable addresses.
>	- `203.0.113.1`- `203.0.113.14`
>---
>- `203.0.113.0/29` (`255.255.255.248`)
>	- $32 - 29 = 3$; $2^3 - 2 = 8 - 2 = 6$ usable addresses.
>	- `203.0.113.1`- `203.0.113.6`
>---
>- `203.0.113.0/30` (`255.255.255.252`)
>	- $32 - 30 = 2$; $2^2 - 2 = 4 - 2 = 2$ usable addresses.
>	- `203.0.113.1`- `203.0.113.3`

### Increment

>[!important] Increment (block size)
>$$
>\text{Increment} = 256 -x
>$$
>- $x$ = the decimal value of the octet in the subnet mask (e.g., `192` for `255.255.255.192`).

### Number of bits required for hsots

>[!important] Number of bits required for hosts
>$$
>2^k - 2 \geq \text{required hosts}
>$$
>Solve for $k$, the smallest number of bits to hold that host count (subtract 2 for network and broadcast addresses): $k \geq log_2(\text{required hosts + 2})$ .

### Network address

>[!important] Subnet ID and broadcast address
>The first (lowest) address: **subnet identifier (subnet ID)** — all host bits are zeroes.
>The last (highest) address: **broadcast address** — all host bits are ones.

>[!important] Point-to-point networks are networks that directly connect two devices. For such networks, the `/31` subnet mask (`255.255.255.254`), is typically used.
>Despite that `/31` subnet mask implies `2` usable addresses, point-to-point networks have no need in broadcast and network addresses. 

### How to determine to which subnet a host belongs to

>[!example]+ Example: to what subnet does a host `192.168.5.57/27` belong?
>1. Find the block size (increment)
>	- `/27` is `255.255.255.224`; "interesting octet" = `224`
>	- block size = $256 - 224 = 32$
>2. List the subnet ranges in the interesting octet
>	- The 4th octet subnets starts at `0` an increment by `32`:
>		- `192.168.5.0`-`31`
>		- `192.168.5.32`-`63`
>		- `192.168.5.64`-`95`
>		- `192.168.5.96`-`127`
>		- `192.168.5.128`-`159`
>		- `192.168.5.160`-`191`
>		- `192.168.5.192`-`223`
>		- `192.168.5.224`-`255
>	- Each subnet covers addresses from its starting value up to one less than the next block.
>3. Find the subnet for the host
>	- `57` is withing `192.168.5.32`-`63` (usable host addresses: `192.168.5.33`-`192.168.5.62`), therefore the subnet is `192.168.5.32/27`.

>[!example]+ Example: to what subnet does a host `192.168.29.219/29` belong?
>1. Find the block size (increment)
>	- `/29` is `255.255.255.248`; "interesting octet" = `248`
>	- block size = $256 - 248 = 8$
>2. List the subnet ranges in the interesting octet
>	- The 4th octet subnets starts at `0` an increment by `8`:
>		- `192.168.29.0`-`7`
>		- `192.168.29.8`-`15`
>		- `192.168.29.16`-`23`
>		- `192.168.29.24`-`31`
>		- ...
>		- `192.168.5.216`-`223`
>3. Find the subnet for the host
>	- `219` is withing `192.168.29.216`-`223` (usable host addresses: `192.168.29.217`-`192.168.29.222`), therefore the subnet is `192.168.29.216/29`.
## Quick subnetting tips

>[!tip]+ Tip: "Interesting octet"
>Find the "interesting octet": look for the octet in the subnet mask that's neither `255` nor `0` (e.g., `192` for `255.255.255.192`).

>[!example]+
>- For `/27`, the mask is `255.255.255.224` → last octet `224` → block size = `256 - 224 = 32`.
>- Subnets increment by 32 in the last octet: `0`, `32`, `64`, `96`, etc.

 
>[!tip]+ Tip: For host requirements, find the smallest subnet that fits
> 
> - Given the number of hosts, find the smallest power of `2` greater than `hosts + 2`.
> - To get the prefix length, subtract that power from `32`.

>[!example]
>Need `50` hosts → `50 + 2 = 52` → next power of `2` is `64` ($2^6$) → host bits = `6` → `prefix = 32 - 6 = /26`.

>[!tip]+ Tip: Memorize common subnet masks and their increments
> 
> 
> | CIDR  | Subnet mask       | Block size<br>(increment) |
> | ----- | ----------------- | -------------------------------- |
> | **A** |                   |                                  |
> | `/32` | `255.255.255.255` | `1`                              |
> | `/31` | `255.255.255.254` | `2`                              |
> | `/30` | `255.255.255.252` | `4`                              |
> | `/29` | `255.255.255.248` | `8`                              |
> | `/28` | `255.255.255.240` | `16`                             |
> | `/27` | `255.255.255.224` | `32`                             |
> | `/26` | `255.255.255.192` | `64`                             |
> | `/25` | `255.255.255.128` | `128`                            |
> | **B** |                   |                                  |
> | `/24` | `255.255.255.0`   | `256`                            |
> | `/23` | `255.255.254.0`   | `512`                            |
> | `/22` | `255.255.252.0`   | `1024`                           |
> | `/21` | `255.255.248.0`   | `2048`                           |
> | `/20` | `255.255.240.0`   | `4096`                           |
> | `/19` | `255.255.224.0`   | `8192`                           |
> | `/18` | `255.255.192.0`   | `16384`                          |
> | `/17` | `255.255.128.0`   | `32768`                          |
> | `/16` | `255.255.0.0`     | `65536`                          |
>>[!note] Note: `/31` is used for point-to-point links (no broadcast).
> 
> ```plaintext
> BINARY REPRESENTATION               |  DECIMAL REPRESENTATION 
> --------------------------------------------------------------------
> 00000000.00000000.00000000.00000000 | 0.0.0.0                
> 10000000.00000000.00000000.00000000 | 128.0.0.0              
> 11000000.00000000.00000000.00000000 | 192.0.0.0              
> 11100000.00000000.00000000.00000000 | 224.0.0.0              
> 11110000.00000000.00000000.00000000 | 240.0.0.0              
> 11111000.00000000.00000000.00000000 | 248.0.0.0              
> 11111100.00000000.00000000.00000000 | 252.0.0.0              
> 11111110.00000000.00000000.00000000 | 254.0.0.0              
> 11111111.00000000.00000000.00000000 | 255.0.0.0 (Class A)    
> 11111111.10000000.00000000.00000000 | 255.128.0.0            
> 11111111.11000000.00000000.00000000 | 255.192.0.0            
> 11111111.11100000.00000000.00000000 | 255.224.0.0            
> 11111111.11110000.00000000.00000000 | 255.240.0.0            
> 11111111.11111000.00000000.00000000 | 255.248.0.0            
> 11111111.11111100.00000000.00000000 | 255.252.0.0            
> 11111111.11111110.00000000.00000000 | 255.254.0.0            
> 11111111.11111111.00000000.00000000 | 255.255.0.0 (Class B)  
> 11111111.11111111.10000000.00000000 | 255.255.128.0          
> 11111111.11111111.11000000.00000000 | 255.255.192.0          
> 11111111.11111111.11100000.00000000 | 255.255.224.0          
> 11111111.11111111.11110000.00000000 | 255.255.240.0          
> 11111111.11111111.11111000.00000000 | 255.255.248.0          
> 11111111.11111111.11111100.00000000 | 255.255.252.0          
> 11111111.11111111.11111110.00000000 | 255.255.254.0          
> 11111111.11111111.11111111.00000000 | 255.255.255.0 (Class C)
> 11111111.11111111.11111111.10000000 | 255.255.255.128        
> 11111111.11111111.11111111.11000000 | 255.255.255.192        
> 11111111.11111111.11111111.11100000 | 255.255.255.224        
> 11111111.11111111.11111111.11110000 | 255.255.255.240        
> 11111111.11111111.11111111.11111000 | 255.255.255.248        
> 11111111.11111111.11111111.11111100 | 255.255.255.252        
> 11111111.11111111.11111111.11111110 | 255.255.255.254        
> 11111111.11111111.11111111.11111111 | 255.255.255.255      
> ```
### Subnetting guide

>**Subnetting process:**

1. Identify the **network address and prefix length (CIDR)**.
2. Determine **how many bits to borrow** from the host portion to create the required number of subnets or hosts.
3. Calculate the **new subnet mask** by adding borrowed bits to the original prefix.
4. Calculate the **number of subnets and hosts per subnet** using the formulas.
5. Calculate the block size — **subnet increment**:

$$
\text{Block size} = 256 - \text{value of the last subnet mast octet}
$$

6. List the **subnet ranges** by incrementing the block size.
7. Identify **network, usable host, and broadcast addresses** for each subnet.


>**Example: subnetting a `/24` network into `/28` subnets**

- Given: Network `192.168.1.0/24`
- Borrow 4 bits (from host bits) → new prefix = $24 + 4 = /28$ 
- Number of **subnets** = $2^4 = 16$
- Number of **hosts per subnet** = $2^{(32−28)} - 2 = 2^4 -2 = 14$
- Subnet mask: `255.255.255.240`
- Block size: $256−240=16$ (increment in the last octet) 
- Subnet ranges:

| Subnet # | Network address | Usable host range               | Broadcast address |
| -------- | --------------- | ------------------------------- | ----------------- |
| `1`      | `192.168.1.0`   | `192.168.1.1`-`192.168.1.14`    | `192.168.1.15`    |
| `2`      | `192.168.1.16`  | `192.168.1.17`-`192.168.1.30`   | `192.168.1.31`    |
| `...`    | `...`           | `...`                           | `...`             |
| `16`     | `192.168.1.240` | `192.168.1.241`-`192.168.1.254` | `192.168.1.255`   |

## Examples

| Target IP address    | Network           | First host        | Last host         | Broadcast         | Next subnet      |
| -------------------- | ----------------- | ----------------- | ----------------- | ----------------- | ---------------- |
| `212.90.93.141/24`   | `212.90.93.0`     | `212.90.93.1`     | `212.90.93.254`   | `212.90.93.255`   | `212.90.94.0`    |
| `197.149.167.35/29`  | `197.149.167.32`  | `197.149.167.33`  | `197.149.167.38`  | `197.149.167.39`  | `197.149.167.40` |
| `215.107.27.66/29`   | `215.107.27.64`   | `215.107.27.65`   | `215.107.27.70`   | `215.107.27.71`   | `215.107.27.72`  |
| `50.138.152.146/14`  | `50.138.0.0`      | `50.138.0.1`      | `50.139.255.254`  | `50.139.255.255`  | `50.140.0.0`     |
| `222.181.236.234/25` | `222.181.236.128` | `222.181.236.129` | `222.181.236.254` | `222.181.236.255` | `222.181.237.0`  |
| `3.227.97.33/18`     | `3.227.64.0`      | `3.227.64.1`      | `3.227.64.254`    | `3.227.64.255`    | `3.227.128.0`    |

Best place to train subnetting: https://subnetipv4.com/
## Subnetting lab

- Link to the lab video: [`Free CCNA | Subnetting (VLSM) | Day 15 Lab | CCNA 200-301 Complete Course — Jeremy's IT Lab`](https://www.youtube.com/watch?v=Rn_E1Qv8--I&list=PLxbwE86jKRgMpuZuLBivzlM8s2Dk5lXBQ&index=28)

![[subnetting_lab.png]]

| LAN   | Hosts | Network address | CIDR  | Mask              | First usable address | Last usable address |
| ----- | ----- | --------------- | ----- | ----------------- | -------------------- | ------------------- |
| LAN 2 | 64    | `192.168.5.0`   | `/25` | `255.255.255.128` | `192.168.5.1`        | `192.168.5.126`     |
| LAN 1 | 45    | `192.168.5.128` | `/26` | `255.255.255.192` | `192.168.5.129`      | `192.168.5.190`     |
| LAN 3 | 14    | `192.168.5.192` | `/28` | `255.255.255.240` | `192.168.5.193`      | `192.168.5.206`     |
| LAN 4 | 9     | `192.168.5.208` | `/28` | `255.255.255.240` | `192.168.5.209`      | `192.168.5.222`     |


| PC   | Address         | Gateway         | Subnet          | Mask              |
| ---- | --------------- | --------------- | --------------- | ----------------- |
| PC 2 | `192.168.5.1`   | `192.168.5.126` | `192.168.5.0`   | `255.255.255.128` |
| PC 1 | `192.168.5.129` | `192.168.5.190` | `192.168.5.128` | `255.255.255.192` |
| PC 3 | `192.168.5.193` | `192.168.5.206` | `192.168.5.192` | `255.255.255.240` |
| PC 4 | `192.168.5.209` | `192.168.5.222` | `192.168.5.208` | `255.255.255.240` |


- **LAN 2:**

```toml
R1(config)# int g0/1
R1(config-if)# ip address 192.168.5.126 255.255.255.128
R1(config-if)# no shutdown
```

- **LAN 1:**

```toml
R1(config-if)# int g0/0
R1(config-if)# ip address 192.168.5.190 255.255.255.192
R1(config-if)# no shutdown
```

- **LAN 3:**

```toml
R2(config)# int g0/0
R2(config-if)# ip address 192.168.5.206 255.255.255.240
R2(config-if)# no shutdown
```

- **LAN 4:**

```toml
R2(config)# int g0/1
R2(config-if)# ip address 192.168.5.222 255.255.255.240
R2(config-if)# no shutdown
```

- **`R1`:**

```toml
R1(config)# int g0/0/0
R1(config-if)# ip address 192.168.5.225 255.255.255.252
R1(config-if)# no shutdown
```

- **`R2`:**

```toml
R2(config-if)# int g0/0/0
R2(config-if)# ip address 192.168.5.226 255.255.255.252
R2(config-if)# no shutdown
```

- **`R2` routes:**

```toml
R2(config)# ip route 192.168.5.0 255.255.255.128 192.168.5.225
R2(config)# ip route 192.168.5.128 255.255.255.192 192.168.5.225
R2(config)# do show ip route
# ...
192.168.5.0/24 is variably subnetted, 6 subnets, 5 masks
S 192.168.5.0/25 [1/0] via 192.168.5.225
S 192.168.5.128/26 [1/0] via 192.168.5.225
C 192.168.5.208/28 is directly connected, GigabitEthernet0/1
L 192.168.5.222/32 is directly connected, GigabitEthernet0/1
C 192.168.5.224/30 is directly connected, GigabitEthernet0/0/0
L 192.168.5.226/32 is directly connected, GigabitEthernet0/0/0
192.169.5.0/24 is variably subnetted, 2 subnets, 2 masks
C 192.169.5.192/28 is directly connected, GigabitEthernet0/0
L 192.169.5.206/32 is directly connected, GigabitEthernet0/0
```

- **`R1` routes:**

```toml
R1(config)# ip route 192.168.5.192 255.255.255.240 192.168.5.226
R1(config)# ip route 192.168.5.208 255.255.255.240 192.168.5.226
R1(config)# do show ip route
# ...
192.168.5.0/24 is variably subnetted, 8 subnets, 5 masks
C 192.168.5.0/25 is directly connected, GigabitEthernet0/1
L 192.168.5.126/32 is directly connected, GigabitEthernet0/1
C 192.168.5.128/26 is directly connected, GigabitEthernet0/0
L 192.168.5.190/32 is directly connected, GigabitEthernet0/0
S 192.168.5.192/28 is directly connected, GigabitEthernet0/0/0
[1/0] via 192.168.5.226
S 192.168.5.208/28 is directly connected, GigabitEthernet0/0/0
[1/0] via 192.168.5.226
C 192.168.5.224/30 is directly connected, GigabitEthernet0/0/0
L 192.168.5.225/32 is directly connected, GigabitEthernet0/0/0
```
## Flashcards

- What is the subnet mask for CIDR `/26`?
    
    - `255.255.255.192`
        
- How many usable hosts are there in a `/28` subnet?
    
    - 14 usable hosts
        
- What is the block size (increment) for a subnet mask of `255.255.255.224`?
    
    - 32
        
- How many subnets can be created by borrowing 3 bits from the host portion?
    
    - 8 subnets
        
- What is the network address of host `192.168.10.130/25`?
    
    - `192.168.10.128`
        
- What is the broadcast address for the subnet `10.0.0.0/30`?
    
    - `10.0.0.3`
        
- How many host bits are left in a `/22` subnet?
    
    - 10 bits
        
- How many usable hosts are in a `/30` subnet?
    
    - 2 usable hosts
        
- What is the subnet mask in dotted decimal for `/29`?
    
    - `255.255.255.248`
        
- Given the network `172.16.0.0/16`, what prefix length is needed to create at least 500 subnets?
    
    - `/25`
        
- What is the first usable IP address in the subnet `192.168.1.64/26`?
    
    - `192.168.1.65`
        
- How many usable hosts are there in a `/24` subnet?
    
    - 254 usable hosts
        
- What is the subnet mask for a network with 62 usable hosts?
    
    - `255.255.255.192` (`/26`)
        
- What subnet does the IP `172.21.111.201/20` belong to?
    
    - `172.21.96.0`
        
- What is the broadcast address of the subnet that contains `192.168.91.78/26`?
    
    - `192.168.91.127`
        
- How many subnets are created if you borrow 5 bits from the host portion?
    
    - 32 subnets
        
- What is the subnet mask for a point-to-point link with 2 usable hosts?
    
    - `255.255.255.252` (`/30`)
        
- What is the block size for subnet mask `255.255.255.240`?
    
    - 16
        
- How many usable hosts does a `/27` subnet provide?
    
    - 30 usable hosts
        
- What is the network address of the second subnet when dividing `172.16.0.0/16` into 4 equal subnets?
    
    - `172.16.64.0`
        
- What is the broadcast address of the second subnet from the previous question?
    
    - `172.16.127.255`
        
- What prefix length will create at least 2000 subnets from `10.0.0.0/8`?
    
    - `/21`
        
- What is the last usable IP address in the subnet `192.168.1.128/25`?
    
    - `192.168.1.254`
        
- How many host bits remain in a `/23` subnet?
    
    - 9 bits
	
- What is the subnet mask for a subnet with 14 usable hosts?
    
    - `255.255.255.240` (`/28`)
        
- What is the network address of the host `10.188.31.45/23`?
    
    - `10.188.30.0`
        
- What is the broadcast address for `10.188.31.0/23`?
    
    - `10.188.31.255`
        
- How many usable hosts are in a `/25` subnet?
    
    - 126 usable hosts
        
- What is the first usable IP address in `172.22.243.160/27`?
    
    - `172.22.243.161`
        
- Which subnet mask is most efficient for a point-to-point serial link?
    
    - `255.255.255.252` (`/30`)
        
- What is the CIDR notation for subnet mask `255.255.254.0`?
    
    - `/23`
        
- How many subnets can be created from `192.168.1.0/24` if you borrow 4 bits?
    
    - 16 subnets
        
- What is the usable host range for subnet `192.168.1.32/27`?
    
    - `192.168.1.33` to `192.168.1.62`
        
- What is the broadcast address for subnet `192.168.1.32/27`?
    
    - `192.168.1.63`
        
- What is the subnet mask in binary for `/26`?
    
    - `11111111.11111111.11111111.11000000`
        
- What is the smallest subnet mask that supports 110 hosts?
    
    - `/25` (`255.255.255.128`)
        
- How many total addresses are in a `/24` subnet?
    
    - 256 addresses
        
- What is the network address for host `192.168.100.130/25`?
    
    - `192.168.100.128`
        
- What is the broadcast address for network `192.168.100.128/25`?
    
    - `192.168.100.255`
        
- How many hosts can a `/21` subnet accommodate?
    
    - 2046 usable hosts
        
- What is the block size for subnet mask `255.255.252.0`?
    
    - 4 (in the third octet)
        
- What is the network address of the third subnet when dividing `10.0.0.0/8` into 8 subnets?
    
    - `10.32.0.0`
        
- How many bits must you borrow to create 80 subnets from `172.16.0.0/16`?
    
    - 7 bits
        
- What is the subnet mask after borrowing 7 bits from `/16`?
    
    - `/23` (`255.255.254.0`)
        
- What is the usable host range for subnet `192.168.1.0/26`?
    
    - `192.168.1.1` to `192.168.1.62`
        
- What is the broadcast address for subnet `192.168.1.0/26`?
    
    - `192.168.1.63`
        
- How many usable hosts are in a `/22` subnet?
    
    - 1022 usable hosts
        
- What is the network address for host `172.18.5.10/24`?
    
    - `172.18.5.0`
        
- What is the broadcast address for network `172.18.5.0/24`?
    
    - `172.18.5.255`
        
- What is the prefix length when subnet mask is `255.255.255.128`?
    
    - `/25`
        
- What is the usable host range for subnet `10.10.10.0/29`?
    
    - `10.10.10.1` to `10.10.10.6`
        
- What is the broadcast address for subnet `10.10.10.0/29`?
    
    - `10.10.10.7`
        
- How many usable hosts are in a `/29` subnet?
    
    - 6 usable hosts
        
- What is the block size for subnet mask `255.255.255.252`?
    
    - 4
        
- What is the network address of the first subnet when dividing `192.168.0.0/24` into 4 subnets?
    
    - `192.168.0.0`
        
- What is the network address of the last subnet when dividing `192.168.0.0/24` into 4 subnets?
    
    - `192.168.0.192`
        
- What is the broadcast address of the last subnet in the previous question?
    
    - `192.168.0.255`
        
- How many usable hosts are in a `/31` subnet?
    
    - 0 usable hosts (used for point-to-point links)
        
- What is the subnet mask for a `/31` prefix?
    
    - `255.255.255.254`
        
- What is the first usable IP address in subnet `172.16.10.0/24`?
    
    - `172.16.10.1`
        
- What is the broadcast address for subnet `172.16.10.0/24`?
    
    - `172.16.10.255`
        
- How many subnets are created by borrowing 4 bits from `/24`?
    
    - 16 subnets
        
- What is the CIDR notation for subnet mask `255.255.255.248`?
    
    - `/29`
        
- What is the usable host range for subnet `192.168.1.128/25`?
    
    - `192.168.1.129` to `192.168.1.254`
        
- What is the broadcast address for subnet `192.168.1.128/25`?
    
    - `192.168.1.255`
        
- How many hosts can a `/20` subnet support?
    
    - 4094 usable hosts
        
- What is the network address of the host `172.21.111.201/20`?
    
    - `172.21.96.0`
        
- What is the broadcast address of the subnet containing `172.21.111.201/20`?
    
    - `172.21.111.255`
        
- What is the subnet mask in dotted decimal for `/20`?
    
    - `255.255.240.0`
        
- What is the block size for subnet mask `255.255.240.0`?
    
    - 16 (third octet)
        
- How many bits are borrowed if the subnet mask is `255.255.255.224`?
    
    - 3 bits
        
- What is the number of usable hosts in a `/21` subnet?
    
    - 2046 usable hosts
        
- What is the first usable IP address in subnet `10.0.0.0/21`?
    
    - `10.0.0.1`

- What is the broadcast address for subnet `10.0.0.0/21`?
    - `10.0.7.255`
        
- What is the network address of the fourth subnet when dividing `172.16.0.0/16` into 8 subnets?
    - `172.16.96.0`
        
- What is the subnet mask for 512 subnets from `172.16.0.0/16`?
    - `/25`
        
- How many usable hosts are in a `/25` subnet?
    
    - 126 usable hosts