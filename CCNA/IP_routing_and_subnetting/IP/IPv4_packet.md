---
created: 2025-09-26 05:55:25
tags:
  - IP
  - routing
---
## IPv4 packet

>[!note]
> PDU (Protocol Data Units) names:
> - Layer 4 PDU — **segment**
> - Layer 3 PDU — **packet** (encapsulates segment)
> - Layer 3 PDU — **frame** (encapsulates packet)

The IPv4 packet header consists of **14 fields**, of which 13 are required.

>[!important] 
>- The **minimum** length of an IPv4 **header**: **20 bytes** (IHL 5)
>- The **maximum** length of an IPv4 **header**: **60 bytes** (IHL 15)
>
>The **maximum** length of an IPv4 **packet** is **1500 bytes** (maximum size of Ethernet frame payload).

| Field                                    | Description                                                                                                                                                                                                                                                                                                                                                       |
| ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Version                                  | The version of IP used.<br>⬡ IPv4: `4` — `0100`<br>⬡ IPv6: `6` — `0110`                                                                                                                                                                                                                                                                                           |
| Internet Header Length (IHL)             | The total length of the header (in increments of 4 bytes).                                                                                                                                                                                                                                                                                                        |
| Differentiated Service Code Point (DSCP) | Used for QoS (Quality of Service).                                                                                                                                                                                                                                                                                                                                |
| Explicit Congestion Notification (ECN)   | Used for QoS (Quality of Service).                                                                                                                                                                                                                                                                                                                                |
| Total Length                             | The total length of the packet.                                                                                                                                                                                                                                                                                                                                   |
| Identification                           | Used with fragmented packets to indicate to which packet this fragment belongs to.                                                                                                                                                                                                                                                                                |
| Flags                                    | Flags, used to control and identify fragments.<br>⬡ Bit `0`: reserved, always set to 0.<br>⬡ Bit `1`: Don't Fragment (DF bit), used to indicate a packet that should not be fragmented.<br>⬡ Bit `2`: More Fragments (MF bit). It is set to `1` if there are more fragments in the packet, and is set to `0` for the last fragment. `0` for unfragmented packets. |
| Fragment offset                          | Used to indicate the position of the fragment within the original, unfragmented IP packet.                                                                                                                                                                                                                                                                        |
| Time to live (TTL)                       | Maximum hop count before the packet is dropped.                                                                                                                                                                                                                                                                                                                   |
| Protocol                                 | Indicates the protocol of the encapsulated Layer 4 PDU.<br>⬡ `6`: TCP<br>⬡ `17`: UDP<br>⬡ `1`: ICMP<br>⬡ `89`: OSPF                                                                                                                                                                                                                                               |
| Header checksum                          | A checksum to check for errors in the IPv4 header.                                                                                                                                                                                                                                                                                                                |
| Source IP address                        | The IPv4 address of the intended sender of the packet. May be changes in transit by NAT.                                                                                                                                                                                                                                                                          |
| Destination IP address                   | The IPv4 address of the intended receiver of the packet. May be affected by NAT.                                                                                                                                                                                                                                                                                  |
| Options                                  | An optional field that can be `0` bits in length if not used, or up to `320` bits, `40` bytes, in length. Rarely used.<br>If the IHL field is greater than `5`, it means that Options are present.                                                                                                                                                                |

>[!note] No need to memorize, but know what each field does.

>[!important]+ **Version**
> - `4` bits
> - ⬡ Identifies the version of IP used. There are two versions of IP in use:
> - ⬡ IPv4: 4 `0100`
> - ⬡ IPv6: 6 `0110`

>[!important]+ **Internet Header Length (IHL)**
> - ⬡ `4` bits
> - ⬡ The final field of the IPv4 header (Options) is variable in length, so this field is necessary to indicate the total length of the header. 
> - ⬡ The IHL field specifies the size of the IPv4 header in 4-byte increments, i.e., in words. 
> - ⬡ The **minimum value** is 5 (= 20 bytes). 
> - ⬡ The **maximum value** is 15 (= 60 bytes).

> [!important]+ **Differentiated Service Code Point (DSCP)**
> - ⬡ `6` bits
> - ⬡ Used for QoS (Quality of Service). 
> - ⬡ Essentially, it is used to prioritize delay-sensitive data, such as streaming voice and video.
> - ⬡ This field is used to identify which traffic should receive priority treatment.

> [!important]+ **Explicit Congestion Notification (ECN)**
> - ⬡ `2` bits
> - ⬡ Provides end-to-end (network two endpoints) notification of network congestion **without dropping packets**.
> - ⬡ Normally in a network, if the network is super busy, if there is congestion, this is signaled by dropping packets.  
> - ⬡ Thus, the ECN field provides a way to signal a congested network without dropping packets.
> - ⬡ However, this is an **optional** field that requires both endpoints, as well as the underlying network infrastructure, to support it.

> [!important]+ **Total Length**
> - ⬡ `16` bits
> - ⬡ Indicates the total length of the packet, including the IPv4 header and the encapsulated Layer 4 segment. 
> - This is different than the IHL field, which indicates only the length of the IPv4 header itself. This field indicates the length in **bytes**, **not in 4-bit increments like the IHL header**. 
> - ⬡ The **minimum** value is 20 bytes (header without data), the **maximum** is 65,535 bytes.

>[!important]+ **Identification**
> - `16` bits
> - ⬡ If a packet is fragmented due to being too large, this field is used to identify which packet the fragment belongs to. All fragments of the same packet will have their own IPv4 header with the **same value** in this field, for them to be reassembled later. 
> - ⬡ Packets are fragmented if larger than the **MTU (Maximum Transmission Unit)**. The MTU is usually `1500` bytes. This is the same as the maximum payload size of an Ethernet frame. 
> - ⬡ Fragments are reassembled by the receiving host.

> [!important]+ **Flags**
> - `3` bits
> - ⬡ Flags are used to control and identify fragments. 
> - ⬡ There are 3 flags, and they function like this:
> 	- ⬡ Bit `0`: reserved, always set to 0.
> 	- ⬡ Bit `1`: Don't Fragment (DF bit), used to indicate a packet that should not be fragmented. 
> 	- ⬡ Bit `2`: More Fragments (MF bit). It is set to `1` if there are more fragments in the packet, and is set to `0` for the last fragment. Unfragmented packets will always have their MF bit set to `0`, since there are no fragments. 
 
>[!important]+ **Fragment offset**
> - `13` bits
> - ⬡ Used to indicate the position of the fragment within the original, unfragmented IP packet. This allows fragmented packets to be reassembled even if the fragments arrive out of order. 

>[!important]+ **Time to live (TTL)**
> - `8` bits
> - ⬡ Used to prevent infinite loops.
> - ⬡ Originally designed to indicate the packet's maximum lifetime in second. However, in practice, this indicates a hop count.
> - ⬡ Each time the packet arrives to a router on the way to its destination, the router decreases the TTL value by `1`, then forwards the packet to the next hop. If the TTL reaches `0`, the packet is dropped.
> - ⬡ A router will drop a packet with a TTL of `0`.
> - ⬡ The current recommended default TTL is `64`.

>[!important]+ **Protocol**
> - `8` bits
> - ⬡ Indicates the protocol of the encapsulated Layer 4 PDU.
> - ⬡ Typically, this will be one of the following:
> 	- ⬡ Value of `6`: TCP
> 	- ⬡ Value of `17`: UDP
> 	- ⬡ Value of `1`: ICMP
> 	- ⬡ Value of `89`: OSPF
 
> [!important]+ **Header checksum**
> - `16` bits
> - ⬡ A calculated checksum used to check for errors in the IPv4 header. 
> - ⬡ When a router receives a packet, it calculates the checksum of the header and compares it to the one in this field of the header. 
> - ⬡ It the newly calculates checksum in the IPv4 header do not match, it means that an error has occurred in transmission, therefore the router drops the packet.
> - ⬡ This is used to check for errors only in the IPv4 header, not in this encapsulated data. 
> - ⬡ IP relies on the encapsulated protocol to detect errors in the encapsulated data. Both TCP and UDP have their own checksum fields to detect errors. 
 
>[!important]+ **Source IP address**
> - `32` bits
> - ⬡ The IPv4 address of the intended sender of the packet. It may be changes in transit by NAT.

> [!important]+ **Destination IP address**
> - `32` bits
> - ⬡ The IPv4 address of the intended receiver of the packet. It may be affected by NAT.

> [!important]+ **Options**
> - `0`-`320` bits
> - ⬡ An optional field that can be `0` bits in length if not used, or up to `320` bits, `40` bytes, in length.
> - ⬡ This field is rarely used. 
> - ⬡ If the IHL field is greater than `5`, it means that Options are present. 

## Quiz

1. What is the fixed binary value of the first field of an IPv4 header?
	- a. `0010`
	- b. `0110`
	- c. `0001`
	- d. `0100`
	
2. Which field will cause the packet to be dropped if it has a value of `0`?
	- a. TTL
	- b. DSCP
	- c. IHL
	- d. ECN

3. How are errors in an IPv4 packet's encapsulated data detected?
	- a. The IPv4 Header Checksum field checks for errors. 
	- b. The encapsulated protocol (TCP, UDP) checks for errors.
	- c. Errors in the encapsulated data cannot be detected.

4. Which field of an IPv4 header is variable in length?
	- a. Options
	- b. Header Checksum
	- c. Total Length
	- d. IHL

5. Which field will be set to `1` on all IPv4 packet fragments except the last fragment?
	- a. Fragment Offset bit
	- b. More Fragments bit
	- c. Don't Fragment bit
	- d. Packet Fragment bit

6. Boson ExSim. Which of the following subnet address is the most appropriate for the point-to-point link between Router A and Router B, if the Router B connects to the `192.168.0.0/25` network?
	- a. `192.168.0.0/25`
	- b. `192.168.0.130/30`
	- c. `192.168.0.192/26`
	- d. `192.168.0.0/30`
	- e. `192.168.0.128/25`
	- f. `192.168.0.128/30`

7. Boson ExSim. You issue the `show running-config` command on Router A and receive the following partial output. Host A is on the same physical network as the `FastEthernet0/0` interface of Router A. Which IP address should you configure on Host A to ensure that the host can communicate with the rest of the network? (Select the best answer.)
	- a. `192.168.18.16/28`
	- b. `192.168.18.32/28`
	- c. `192.168.18.48/28`
	- d. `192.168.18.46/28`

| Question | Answer |
| -------- | ------ |
| `1.`     | `d.`   |
| `2.`     | `a.`   |
| `3.`     | `b.`   |
| `4.`     | `a.`   |
| `5.`     | `b.`   |
| `6.`     | `f.`   |
| `7.`     | `d`    |
|          |        |

Explanations:

1. The Options field can vary in length from `0` bits to `320` bits. The other fields are fixed-length. Although the Total Length and IHL fields are used to represent the variable length of the IPv4 header and packet, the fields themselves are fixed in length.

2. The More Fragments (MF) bit, part of the Flags field of the IPv4 header, is used to indicate that the current fragment is not the last fragment of a fragmented packet. It is set to `1` on all fragments except the last, which will set it to `0`. A, fragment offset, is a 13-bit field in the header, not a single bit. C, Don’t fragment bit, is used to prevent a packet from being fragmented. And D, packet fragment bit, is not a real bit in the IPv4 header.

3. The answer is `d.`, `192.168.18.46/28`. 
	- `a.`, `192.168.18.16/28` is incorrect because it doesn't fall within the `192.168.18.32/28` address range. The first usable address in the subnet is `192.168.18.33/28`, and it is assigned to the router.
	- `b.`, `192.168.18.32/28` is incorrect because this is a network ID, and it can't be used as a host address. 
	- `c.`, `192.168.18.48/28` is incorrect because it doesn't fall within the `192.168.18.32/28` address range, and moreover it is a subnet identifier of another `/28` network: `192.168.18.48/28`. The last usable address in the subnet is `192.168.18.46/28`, and `192.168.18.47/28` is the broadcast address. 


4. Boson ExSim. Which of the following networks is not defined in RFC 1918? (Select the best answer.)
	- a. `192.168.1.0`
	- b. `172.20.1.0`
	- c. `172.172.1.0`
	- d. `192.168.111.0`
	- e. `10.1.1.0
	- f. `10.16.1.0`