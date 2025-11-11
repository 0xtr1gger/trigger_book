---
created: 2025-10-30 03:36:35
tags:
  - wireless
---
## Wireless LANs

>A **wireless LAN (WLAN)** is a local area network that uses wireless data connections between network nodes. 

>[!important] Wireless LAN standards are defined in **IEEE 802.11**.

>[!note]+ Wi-Fi
>The term **Wi-Fi** is a trademark of the **Wi-Fi Alliance**, not directly connected to the IEEE. 
>- The Wi-Fi Alliance tests and certifies equipment for 802.11 standard compliance and interoperability with other devices.
>
>![[wi-fi_certified.jpg]]
>- But Wi-Fi has become a common term that people use to refer to 802.11 wireless LANs. 

## Challenges of wireless networks

Unlike wired connections, wireless signals propagate freely in open space; they're not confined in to the cables. Indeed, it allows for greater mobility, but comes with various challenges:

- **Security and privacy concerns:** All devices withing the range of a wireless device receive that device's signals.
- **Collisions:** wireless devices must contend for airtime.
- **Regulation:** wireless communications are regulated by various international and national authorities.
- **Wireless signal coverage area** must be considered:
	- Signal range;
	- Signal **absorption**, **reflection**, **refraction**, **diffraction**, and **scattering**.
- Other devices using the same RF channels can cause **interference**.

>[!note] See [[RF]] for more about radio frequency.

>[!important]+ **CSMA/CA (Carrier Sense Multiple Access with Collision Avoidance)** is used to facilitate half-duplex communications.
>In short, when using CSMA/CA, a device will wait for other devices to stop transmitting before it transmits data itself.
>- **CSMA/CD** is used in wired networks to detect and recover from collisions.
>- **CSMA/CA** is used in wireless networks to avoid collisions.
## Wireless standards

| Standard | Frequencies           | Max Theoretical Data Rate | Wi-Fi Alliance name |
| -------- | --------------------- | ------------------------- | ------------------- |
| 802.11   | 2.4 GHz               | 2 Mbps                    |                     |
| 802.11b  | 2.4 GHz               | 11 Mbps                   |                     |
| 802.11a  | 5 GHz                 | 54 Mbps                   |                     |
| 802.11g  | 2.4 GHz               | 54 Mbps                   |                     |
| 802.11n  | 2.4 GHz, 5 GHz        | 600 Mbps                  | Wi-Fi 4             |
| 802.11ac | 5 GHz                 | 6.93 Gbps                 | Wi-Fi 5             |
| 802.11ax | 2.4 GHz, 5 GHz, 6 GHz | 4 * 802.11ac              | Wi-Fi 6, Wi-Fi 6E   |

## Service sets

>A **Service Set (SS)** is a group of wireless network devices that share a common **Service Set Identifier (SSID)** and operate within a specific **frequency range**.

>[!important] All devices in a service set share the same **SSID (Service Set Identifier)**.

>A **Service Set Identifier (SSID)** is a **non-unique** human-readable name that identifies a service set.

>[!important]+ SSIDs do **not** have to be unique.
>But it's recommended that they are.

There are three main types of **service sets**:
- **Independent** Basic Service Sets (IBSS)
- **Infrastructure** Basic Service Sets (BSS)
- **Mesh** service sets
### Independent service sets

> An **IBSS (Independent Basic Service Set)**, also known as an **ad hoc network**, is a wireless network created by two or more peer devices directly interconnected together *without using an Access Point (AP)*.

- IBSSs can be used for file transfer (e.g., AirDrop, KDE Connect, SnapDrop, etc.).
- To form an IBSS, one of the devices must take the lead and begin advertising the network name and necessary radio parameters, much like an AP would do. Other devices can join as needed.

>[!note] IBSSs are meant to be organized in an impromptu, distributed fashion; therefore, they **do not scale well beyond eight to ten devices**.

>[!important] IBSS are not scalable beyond a few devices.

### Basic service sets

>A **Basic Service Set (BSS)**, or **Infrastructure BSS**, is to a group of wireless network devices, known as **stations (STAs)**, that connect to a wireless network through an **AP (Access Point)**.

>[!important] BSSID
>Each BSS is uniquely identified with a **Basic Service Set Identifier (BSSID)**.
>A BSSID is the MAC address of the AP's radio (48-bits).

| BSSID                               | SSID                                                            |
| :---------------------------------- | :-------------------------------------------------------------- |
| MAC address of the AP               | A non-unique human-readable name                                |
| Unique 48-bit identifier of the BSS | An alphanumeric string of characters; limited to 32 characters. |

>A **Wireless Access Point (WAP)**, or **Access Point (AP)**, is a network hardware device that allows other wireless devices to connect to a wired network.

>[!note] A BSSID is used by an AP to advertise the BSS.

The AP serves as a single point of contact for every device that uses the BSS. It advertises the existence of the BSS so that devices can find it and try to join.
- Wireless devices request to **associate** with the BSS.
- Wireless devices that have associated with the BSS are called **clients** or **stations (STA)**.

>[!important] Membership in a BSS is called an **association**.


As long as a wireless client remains associated with a BSS, **all communications to and from the client pass through the AP**.

>[!important] Clients must communicate via AP, not directly with each other.

> A **Basic Service Area (BSA)**, aka **cell**, is the coverage area of an AP. 

### Extended service sets

To create larger wireless LANs beyond the range of a single AP, you can use an **ESS (Extended Service Set)**.

>An **ESS (Extended Service Set)** is a collection of multiple BSSs interconnected together to create a single wireless network.

>[!important] Each BSS in an ESS uses **the same SSID** but **different BSSIDs**: each BSS has its own **unique BSSID**.

- Each BSS uses a **different RF channel** to avoid interference.
- APs with their own BSSs are connected by a **wired network**.

>[!important]+ BSSs in an ESS
>- Each BSS uses the same SSID.
>- Each BSS has a unique BSSID.
>- Each BSS uses a different channel to avoid interference.

>[!note] The BSAs is BSSs in an ESS should overlap about 10-15%.

>[!important]+ Roaming
> In an ESS, a wireless client can associate with one nearby AP. Wireless clients can *pass between APs without having to reconnect*, which provides a seamless Wi-Fi experience. 
> Passing from one AP to another is called **roaming**.

### Mesh service sets

>A **MBSS (Mesh Basic Service Set)** is a type of wireless network in which **APs are interconnected wirelessly** with each other.

- MBSSs can be used in situations where it's difficult to run an Ethernet connection to every AP.
- Mesh APs use two radios:
    - One to provide a BSS to wireless clients
    - One to form a **backhaul network**, used to bridge traffic from AP to AP.

- At least one AP is connected to the wired network, and it is called the **RAP (Root Access Point)**. The other APs are called **MAPs (Mesh Access Points)**.
    
- A protocol is used to determine the best path through the mesh, similar to routing protocols.

## Distribution system

- Most wireless networks aren't standalone networks.
	- Rather, they are a way for wireless clients to connect to the wired network infrastructure.    

>[!important] In 802.11, the upstream wired network is called the **DS (Distribution System)**.

>[!important] Each wireless BSS or ESS is mapped to a VLAN in the wired network.
    
- It's possible for an AP to provide **multiple wireless LANs**, each with a unique SSID.
- Each WLAN is mapped to a separate VLAN and connected to the wired network via a **trunk**.
- Each WLAN uses a unique BSSID, usually by incrementing the last digit of the BSSID by one.
## AP operational modes

- **Local** (default)
	- Offers a BSS to clients.
	- When the AP doesn't transmit, it measures noise, interference, discovers rogue devices, and checks for matches against IDS events over the network.

- **Repeater**
	- Used to extend the range of a BSS.
	- Simply retranmits any signal it receives from the AP.
		- A repeater with a single radio must operate on the same channel as its AP, but this can drastically reduce the overall throughput on the channel (by 50%).
        - A repeater with two radios can receive on one channel, and then retransmit on another channel.

- **Workgroup Bridge (WGB)**
    - Operates as a wireless client of another AP, and can be used to connect wired devices to the wireless network.
    - It can be used, for example, if a device without wireless capabilities, such as a laptop, wants to connect to the wireless network.

    - There are two kinds of WGBs:
        - **Universal WGB (uWGB)**
            - A 802.11 standard that allows one device to be bridged to the wireless network
        - **WGB**
            - a Cisco-proprietary version of the 802.11 standard that allows multiple wired clients to be bridged to the wireless network.

- **Outdoor bridge**
    - Can be used to connect networks over long distances wirelessly.
    - The APs will use specialized antennas that focus most of the signal power in one direction, which allows the wireless connection to be made over longer distances that normally possible.
    - The connection can be point-to-point, or point-to-multipoint (multiple sites connect to one central site, forming a hub-and-spoke topology).

---

- **Scanner**    
    - The AP will use its radio to scan channels and collect data.

- **Root Bridge**
    - The access point uses its Ethernet port to connect a wired network to a remote wireless bridge over a point-to-point or point-to-multipoint channel.
    - No wireless clients will be allowed to associate.

- **Non-Root Bridge**
    - The AP will act as a remote wireless bridge and will connect to a root bridge AP over a wireless link.

