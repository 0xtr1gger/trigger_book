---
created: 2025-09-26 05:46:25
tags:
  - ethernet
---
## Ethernet frame structure

The Ethernet standard defines the structure of **Ethernet frames**. 

>An Ethernet frame encapsulates data for transmission over an Ethernet connection.

Each Ethernet frame consists of:
- **Header**
- **Payload** 
- **Trailer**

### Ethernet header

| Field                            | Size (bytes) | Notes                                                                                                                                                                                                                                                                                                                                                                                                       |
| -------------------------------- | ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Preamble**                     | `7`          | ⬦ Used for synchronization and to signal the start of the frame.<br>⬦ Allows devices to synchronize their receiver clocks<br>⬦ Value: `10101010` 7 times                                                                                                                                                                                                                                                    |
| **SFD (Start Frame Delimiter)**  | `1`          | ⬦ Marks the end of the preamble and the beginning of the rest of the frame.<br>⬦ Value: `10101011`                                                                                                                                                                                                                                                                                                          |
| **Destination MAC address**      | `6`          | -                                                                                                                                                                                                                                                                                                                                                                                                           |
| **Source MAC address**           | `6`          | -                                                                                                                                                                                                                                                                                                                                                                                                           |
| **802.1Q (VLAN) tag (optional)** | `(4)`        | ⬦ A 802.1Q VLAN tag which indicates the VLAN the frame is about to be sent over a trunk port.                                                                                                                                                                                                                                                                                                               |
| **Type or Length**               | `2`          | <br>⬦ ≤ `1500`: the **Length** of the encapsulated packet (in bytes).<br>⬦ ≥ `1536`: the **Type** of the encapsulated packet (IPv4 or IPv6); the length is determined via other methods. Can be:<br>⬦ `0x0800` (`2048`) = IPv4<br>⬦ `0x86DD` (`34525`) = IPv6<br>Most commonly, used to specify the type of the encapsulated packet; the end of the frame is indicated by a special signal after the frame. |
| **Payload**                      | `46-1500`    | ⬦ The actual data being transmitted.                                                                                                                                                                                                                                                                                                                                                                        |
| **FCS (Frame Check Sequence)**   | `4`          | ⬦ Redundancy check for ensuring data integrity during transmission.<br>⬦ Detecting corrupted data by running CRC (Cyclic Redundancy Check) algorithm over the received data.                                                                                                                                                                                                                                |
>[!important] 
>- **Preamble** + **SFD** are usually not considered a part of the Ethernet header, but they are included with every Ethernet frame.
>- Therefore, the size of the Ethernet header + trailer is **`18` bytes** (`6` + `6` + `2` + `4`); with Preamble and SFD it would be `28` bytes.

>[!note] See [[MAC_addresses]].
### Payload

The **Payload** carries the actual data being transmitted.

- The minimum size for an **Ethernet frame** (Header + Payload + Trailer) is `64` bytes.
- The minimum size of an **Ethernet Payload** is `46` bytes (`64` bytes of minimum frame size - `18` bytes of Ethernet header)

>[!note] 
>If the payload is less than `46` bytes, padding bytes are added. 

>[!important] The maximum size of an Ethernet payload is `1500` bytes.

>[!note] 
>The maximum size of an Ethernet frame defines the maximum size of a Layer 3 (e.g., IP) packet that can be sent over a network. Because the Layer 3 packet rests inside the Payload of an Ethernet frame, `1500` bytes is the largest IP MTU allowed over an Ethernet.

### Trailer

>The **trailer** of an Ethernet frame consists of one field, called **FCS (Frame Check Sequence)**, `4` bytes long. 

It is mainly used for redundancy checks to ensure data integrity during transmission. Corrupted data is detected with the CRC (Cyclic Redundancy Check) algorithm run on each received frame.

>[!note]
>Ethernet devices must allow a minimum idle period between transmission of Ethernet packets. A brief recovery time between packets allows devices to prepare for reception of the next packet. While some physical layer variants literally transmit nothing during the idle period, most modern ones continue to transmit an idle pattern signal. 
>This is called an **Interpacket Gap (IPG)**; it must be minimum of `96` bits (`12` bytes).

## Non-standard frames

>[!important]
>Default Maximum Transmission Unit (MTU) size for an Ethernet Payload is **`1500` bytes**.
>The maximum size of an Ethernet frame, with the Ethernet header and trailer, is **`1518` bytes** (not including the Preamble and SFD).

Although the Ethernet standard requires frames to have a size **between `64` bytes and `1518` bytes**, there are devices that can support larger frame sizes.
These non-standard frames facilitate the efficient transmission of large data payloads in environments where non-standard frame sizes are supported, such as data center storage network implementations. 

There are several common Ethernet frames that exceed the standard size of `1518` bytes:

>[!important] A **giant** is an Ethernet frame that exceeds **`1518` bytes** and has a **bad FCS value**.

>[!important] A **baby giant** is an Ethernet frame **up to `1600` bytes** in length.
>- Baby giants can occur if you use Q-in-Q encapsulation, MPLS (Multiport Label Switching), or any other feature that adds to the size of an Ethernet frame.

>[!important] A **jumbo** is an Ethernet frame **up to 9,216 bytes** in length, which is much much larger than a standard Ethernet frame.

>[!important] A **runt** is an Ethernet frame **fewer than 64 bytes** in length and has a **bad FCS value**.
>- Frames smaller than 64 bytes are discarded. 
>- Runts can sometimes be caused by excessive collisions or malfunctioning hardware.

## Flashcards

- Three parts of Ethernet frame
	- Header
	- Payload
	- Trailer

- Fields in an Ethernet frame, in order
	- Preamble (7 bytes)
	- SFD (Start Frame Delimiter) (1 byte)
	- Destination MAC address (6 bytes)
	- Source MAC address (6 bytes)
	- 802.1Q (VLAN) tag (optional) (4 bytes)
	- Type/Length (2 bytes)
	- Payload (42-1500 bytes)
	- FCS (Frame Check Sequence) (4 bytes)

- What's the EtherType value for IPv4?
	- `0x0800` = `2048` 

- What's the EtherType value for IPv6?
	- `0x86DD` = `34525`

- An Ethernet frame that exceeds `1518` bytes and has a bad FCS value is called...
	- Giant

- An Ethernet frame up to `1600` bytes in length is called..
	- Baby giant

- An Ethernet frame up to `9216` bytes in length is called...
	- Jumbo

 - An Ethernet frame fewer than `64` bytes in length and has a bad FCS value is called...
	 - Runt

- Which non-standard frame is formed due to collisions of Ethernet frames or malfunctioning hardware and is always discarded by switches?
	- Runt