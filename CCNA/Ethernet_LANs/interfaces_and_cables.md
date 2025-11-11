---
created: 2025-09-24 05:26:59
tags:
  - ethernet
---

>[!important] Ethernet standards are defined in the IEEE 802.3 standard in 1983.

>[!important] IEEE = Institute of Electrical and Electronics Engineers

## Copper cables

Copper cable standards:

| Speed    | Common name         | IEEE standard | Informal name | Maximum length |
| -------- | ------------------- | ------------- | ------------- | -------------- |
| 10 Mbps  | Ethernet            | 802.3i        | 10BASE-T      | 100 m          |
| 100 Mbps | Fast Ethernet       | 802.3u        | 100BASE-T     | 100 m          |
| 1 Gbps   | Gigabit Ethernet    | 803.3ab       | 1000BASE-T    | 100 m          |
| 10 Gbps  | 10 Gigabit Ethernet | 802.3an       | 10GBASE-T     | 100 m          |

>[!note] BASE = baseband signaling

>[!note] T = twisted pair

Copper cables used in Ethernet standards are **UTP cables**.

>**UTP (Unshielded Twisted Pair)**


>[!important] UTP categories
>- **Category 3** - Supports 10 Mbps Ethernet and 16 Mbps Token Ring with voice applications
>     
> - **Category 5** - Handles 10/100 Mbps Ethernet and voice communications
>     
> - **Category 5e** - Enhanced version supporting 100 Mbps and 1000 Mbps Gigabit Ethernet with improved EMI protection
>     
> - **Category 6** - Supports 10 Gbps Ethernet with larger gauge wires and superior performance for Gigabit applications
>     
> - **Category 6a/6e** - Advanced versions providing enhanced EMI protection for high-bandwidth broadband communications

- Wires are twisted to protect against EMI (Electromagnetic Interference).


>[!important] UTP cables
>- 10BASE-T = 2 pairs (4 wires)
>- 100BASE-T
>---
>- 1000BASE-T = 4 pairs (8 wires)
>- 10GBASE-T

>**Shielded Twisted Pair (STP)** includes grounded copper shielding around wire pairs or the entire bundle. This provides enhanced EMI protection, but it's more expensive and difficult to install than UTP.

### Fiber-optic cables

>[!important] Fiber-optic connections are defined in the IEEE 802.3ae standard.

>[!important] **STP Transceiver (Small Form-Factor Pluggable)** allows fiber-optic cables to connect to switches and routers.

Fiber-optic cable structure:

1. **Fiberglass core**
2. **Cladding** that reflects light down the cable
3. **Protective buffer**
4. **Outer jacket**

![[fiber_optic_cable_structure.svg]]
Source: https://commons.wikimedia.org/wiki/File:Singlemode_fibre_structure.svg

There are two main types of fiber-optic cables: 

- **Single-mode fiber (SMF)**
	- The core diameter is **narrower than MMF**.
	- Single-mode fiber cables can be **longer than** both UTP and **MMF** cables.
	- These cables are **more expensive than MMF** (due to more expensive laser-based SFP transmitters).
	- SMF typically uses a 9-micron core, and can support a wavelength of 1,550 nm and distances of 80 km.
	- The light transmitted into the core of an SMF cable is typically in the 1,310-nm or 1,550-nm frequency range.
	- Because SMF has a relatively small core that permits very few angles of light, the signal does not become very dispersed over great distances.

>[!note] SMF is typically used in campus designs that require at least 10 Gbps of bandwidth and network runs greater than 2 km.

![[single-mode_fiber_optic.svg]]

- **Multi-mode fiber (MMF)**
	- The core diameter is wider than single-mode fiber.
	- The **wider diameter** allows multiple angles (modes) of light waves to enter the core. 
	- Multimode fiber cables can be longer than UTP, but **shorter than SMF** cables.
	- Multimode fiber cables are **cheaper than SMF** (due to cheaper LED-based SFP transceivers).
	- The light transmitted into the core of an MMF cable is typically in the 850-nm or 1,300-nm frequency range.
	- Because MMF has a relatively large core, 50 or 62.5 micron, and the large core permits many different angles of light, so the signal becomes dispersed over great distances. This dispersion effectively limits the usable distance of MMF to 2 km.

>[!note] MMF is typically used in campus designs that require at least 1 gigabit per second (Gbps) of bandwidth and network runs less than 2 km.

![[multimode_fiber_optic.svg]]

>[!note]+ The center represents the fiberglass core, and the blue represents the reflective cladding that reflects light down the cable.

Fiber-optic standards:

| Informal name | IEEE standard | Speed   | Cable type                | Maximum length                          |
| ------------- | ------------- | ------- | ------------------------- | --------------------------------------- |
| 1000BASE-LX   | 802.3z        | 1 Gbps  | Multimode/<br>single-mode | 550 m (multimode)<br>5 km (single-mode) |
| 10GBASE-SR    | 802.3ae       | 10 Gbps | Multimode                 | 400 m                                   |
| 10GBASE-LR    | 802.3ae       | 10 Gbps | Single-mode               | 10 km                                   |
| 10GBASE-ER    | 802.3ae       | 10 Gbps | Single-mode               | 30 km                                   |

## UTP vs. fiber-optic

| UTP                                                                                   | Fiber-optic                                                                                                 |
| ------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Cheaper than fiber-optic.                                                             | More expensive than UTP.                                                                                    |
| Shorter maximum distance than fiber-optic (~100 m).                                   | Longer maximum distance than UTP.                                                                           |
| Can be vulnerable to EMI.                                                             | Not vulnerable to EMI.                                                                                      |
| RJ-45 ports used with UTP are cheaper than SFP ports.                                 | SFP ports used in fiber-optic are more expensive than RJ-45 (single-mode is more expensive than multimode). |
| Emit (leak) a faint signal outside of the cable, which cab be copied (security risk). | Doesn't emit any signal outside of the cable (no security risks).                                           |
## Straight-through cables vs. cross-over cables

- Straight-through cable:

![[straight_through_cable.png]]


- Crossover cable:

![[crossover_cable.png]]


>[!important] If two devices transmit and receive on the **same** pins, they must be connected with a crossover cable.

| Device type | Transmit (Tx) pins | Receive (Rx) pins |
| ----------- | ------------------ | ----------------- |
| Router      | `1` and `2`        | `3` and `6`       |
| Firewall    | `1` and `2`        | `3` and `6`       |
| PC          | 1 and 2`1` and `2` | `3` and `6`       |
| Switch      | `3` and `6`        | `1` and `2`       |

>[!important] Auto MDI-X allows devices to automatically detect which pins their neighbor is transmitting data on, and then adjust which pins they use to transmit and receive data.


## Quiz

1. You connect two old routers together with a UTP cable, but data is not successfully sent and received between them. What could be the problem?
	- a. They're connected with a straight-through cable.
	- b. They're connected with a crossover table.
	- c. They're operating in Auto MDI-X mode.


|  Q  |  A  |
| :-: | :-: |
| 1.  | a.  |
