---
created: 2025-10-30 03:37:15
tags:
  - wireless
---
## AP deployment methods

There are three main wireless AP deployment methods:
- Autonomous
- Lightweight 
- Cloud-based 
## Autonomous APs

>[!important] **Autonomous APs** are self-contained systems that don't rely on a WLC.

- Autonomous APs are configured individually.
	- Can be configured via **console cable (CLI)**, **Telnet/SSH (CLI)**, or **HTTP/HTTPS web connection (GUI)**.
	- For remote management over Telnet/SSH or HTTP/HTTPS, an IP address should be configured.
	- The RF parameters must be configured manually (e.g., transmit power, channel, etc.).
	- Security policies, QoS rules, etc. are **configured individually on each AP**.

- No central monitoring or management of autonomous APs.

>[!important] Autonomous APs connect to the wired network with a **trunk link**. 
>- Even if there is only one SSID advertised by an AP, a trunk connection is needed, since the **management traffic** used to remotely connect to the wireless APs and other devices, such as switches, is placed in a **separate VLAN**.

- Data traffic from wireless clients has a **very direct path to the wired network** or other wireless clients associated with the same AP (i.e., the traffic does not pass through a WLC).

- Each VLAN has to stretch across the **entire network**. This is considered a bad practice:
	- Large broadcast domain
	- Spanning tree will disable links
	- Adding/deleting VLANs is very labor-intensive.

>[!note] Autonomous APs are commonly used in small networks, but they're not viable in medium to large networks.

- Autonomous APs can also functions in repeater, outdoor bridge, and WGB modes.
 
>[!note] A big focus of modern network design is to avoid spanning tree as much as possible.

## Lightweight APs

The functions of a lightweight AP can be split between the AP and a **Wireless LAN Controller (WLC)**.

>A **WLC (Wireless LAN Controller)** is used to centrally configure and manage lightweight APs. 

>[!important] **Lightweight APs** handle **real-time** operations:
> - Transmitting/receiving RF traffic
> - Encrypting/decrypting traffic
> - Sending out beacons and probes
> - etc.

>[!important] **WLC** handles other operations:
> - RF management
> - Security and QoS management
> - Client authentication and association
> - Roaming management
> - etc.

>[!important] This is called a **split-MAC architecture**. 

- The WLC is used to centrally configure the lightweight APs.
- The WLC can be located in the same subnet/VLAN as the lightweight APs it manages, or in a different subnet/VLAN. 
- The WLC and the lightweight APs authenticate each other using digital certificates installed on each device (X.509 standard certificates). 
	- This ensures that only authorized APs can join the network (protects from attacks such as evil twin or rogue AP).

![[lightweight_AP.png]]
### CAPWAP

>[!important] The WLC and lightweight APs communicate using the **CAPWAP (Control And Provisioning of Wireless Access Points)** protocol.

 - CAPWAP is based on an older protocol called LWAPP (Lightweight Access Point Protocol).

Two tunnels are created between each AP and the WLC:
	
- **Control tunnel (UDP port `5246`)**
	- Used to configure the APs, and control/manage the operations. 
	- All traffic in this tunnel is **encrypted by default**. 

- **Data tunnel (UDP port `5247`)**
	- All traffic from wireless clients is sent through this tunnel to the WLC. It doesn't go directly to the wired network.
	- Traffic in this tunnel is **not encrypted by default**, but it can be configured to be encrypted with **DTLS (Datagram Transport Layer Security)**. 
	- DTLS uses UDP, whereas TLS uses TCP.

>[!important] Because all traffic from wireless clients is tunneled to the WLC with CAPWAP, **Lightweight APs connect to switch access ports, not trunk ports**. 


![[split_MAC.svg]]




>[!note] **CAPWAP tunnels are not wireless**; they are depicted on the diagram as direct lines for simplicity, but in reality, traffic between the APs and WLC goes through wired infrastructure, i.e., switches shown above.


### Benefits of a split-MAC architecture

- **Scalability**
	- With a WLC (or multiple WLCs in very large networks), it's much simpler to build and support a network with thousands of APs.

- **Dynamic channel assignment**
	- The WLC can automatically select which channel each AP should use.

- **Transmit power optimization**
	- The WLC can automatically set the appropriate transmit power for each AP.

- **Self-healing wireless coverage**
	- When an AP stops functioning, the WLC can increase the transmit power of nearby APs to avoid coverage holes.

- **Seamless roaming**
	- Clients can roam between APs with no noticeable delay.

- **Client load balancing**
	- If a client is in range of two APs, the WLC can associate the client with the least-used AP, to balance the load among APs. 

- **Security and QoS management**
	- Central management of security and QoS policies ensures consistency across the network. 

![[lightweight_vs_autonomous_AP.png]]
### Lightweight AP operational modes

**AP offers one or more BSSs:**

- **Local** (default)
	- The AP offers one or more BSSs for clients to associate with.

- **FlexConnect**
	- The AP offers one or more BSSs for clients to associate with.
	- Allows the AP to locally switch traffic between wired and wireless networks if the tunnels to the WLC go down.

>[!important] If an LAP operates in FlexConnect mode, it can switch traffic locally instead of tunneling it to the WLC.
>This is useful at remote sites, where sending Internet-bound traffic through the CAPWAP tunnel to the central WLC would be inefficient. With FlexConnect, the AP can forward Internet traffic directly to the wired network at the local site.
>- The lightweight AP can thereby **provide wireless connectivity to clients without sending the data to the WLC**. 
>- Furthermore, lightweight APs operating in FlexConnect mode can **provide client connectivity even if the connection to the remote WLC is lost**.

- **Flex plus Bridge**
	- Adds FlexConnect functionality to the Bridge/Mesh mode. Allows wireless access points to locally forward traffic even if connectivity to the WLC is lost. 


| Mode                                     | BSS? | Notes                                                                                                                                                                                                                                                                                                                  |
| ---------------------------------------- | ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Local** (default)                      | BSS  |                                                                                                                                                                                                                                                                                                                        |
| **FlexConnect**                          | BSS  | Allows the AP to locally switch traffic between wired and wireless networks if the tunnels to the WLC go down.                                                                                                                                                                                                         |
| **Sniffer**                              | No   | The AP captures 802.11 frames and sends them to a device running traffic analysis software, such as Wireshark.                                                                                                                                                                                                         |
| **Monitor**                              | No   | It's dedicated to receiving 802.11 frames to detect rogue devices. <br>If a client is found to be a rogue device, an AP can send de-authentication messages to disassociate the device from the AP.                                                                                                                    |
| **Rogue detector**                       | No   | The AP doesn't even use its radio.<br>The AP listens on the **wired network only**.<br>It receives a list of suspected rogue clients and AP MAC addresses from the WLC. Then, by listening to **ARP messages** on the **wired network** and correlating it with the information from WLC, it can detect rogue devices. |
| **SE-Connect (Spectrum Expert Connect)** | No   | The AP is dedicated to RF spectrum analysis on all channels. <br>It can send information to software such as Cisco Spectrum Expert on a PC to collect and analyze the data. This can help find sources of interference.                                                                                                |
| **Bridge/Mesh**                          | No   | Like the Autonomous AP's outdoor bridge mode, the lightweight AP can be a dedicated bridge between sites, even over long distances. A mesh can be made between the access points.                                                                                                                                      |
| **Flex plus Bridge**                     | BSS  | Adds FlexConnect functionality to the Bridge/Mesh mode. Allows wireless access points to locally forward traffic even if connectivity to the WLC is lost. <br>                                                                                                                                                         |

**AP does not offer any BSSs:**

- **Sniffer**
	- The AP captures 802.11 frames and sends them to a device running traffic analysis software, such as Wireshark.
	- The AP listens on a specific channel to capture the traffic. 
	
- **Monitor**
	- It's dedicated to receiving 802.11 frames to detect rogue devices. 
	- If a client is found to be a rogue device, an AP can send de-authentication messages to disassociate the device from the AP.

- **Rogue detector**
	- The AP doesn't even use its radio.
	- The AP listens on the **wired network only**.
	- It receives a list of suspected rogue clients and AP MAC addresses from the WLC. Then, by listening to **ARP messages** on the **wired network** and correlating it with the information from WLC, it can detect rogue devices.

---

- **SE-Connect (Spectrum Expert Connect)**
	- The AP is dedicated to RF spectrum analysis on all channels. 
	- It can send information to software such as Cisco Spectrum Expert on a PC to collect and analyze the data. This can help find sources of interference.

- **Bridge/Mesh**
	- Like the Autonomous AP's outdoor bridge mode, the lightweight AP can be a dedicated bridge between sites, even over long distances. A mesh can be made between the access points. 

## Cloud-based APs

**Cloud-based AP** architecture is in-between autonomous AP and split-MAC architecture.
- Autonomous APs are centrally managed in the cloud.
- **Cisco Meraki** is a popular cloud-based Wi-Fi solution.
- The Meraki can be used to configure APs, monitor the network, generate performance reports, etc.
	- Meraki also tells each AP which channel to use, what transmit power to use, etc.

>[!important] Regular data traffic is not sent to the cloud. It is sent directly to the wired network, same as when using Autonomous APs.
>Only management/control traffic is sent to the cloud (e.g., RF spectrum information, management information, etc.).

## WLC deployment models

>[!important] **This only applies to split-MAC architecture.**

In a split-MAC architecture, there are **4 main WLC deployment models**:

- **Unified** WLC deployment model
	- The WLC is a hardware appliance in a central location of the network.
	- Can support up to about **6000 APs**.
	- If more than 6000 APs are needed, additional WLCs can be added to the network. 

- **Cloud-based** WLC deployment model
	- The WLC is a VM running on a server, usually in a private cloud in a data center. 
	- This is not the same as the cloud-based AP architecture.
	- In this case, the APs are not cloud-based, they are lightweight APs. Only the WLC is in the cloud.
	- A cloud-based WLCs can typically support up to about **3000 APs**.
	- If more than 3000 APs are needed, more WLC VMs can be added. 

- **Embedded** WLC deployment model
	- The WLC is integrated within a switch.
	- An embedded WLC can support up to about **200 APs**. 
	- If more than 200 APs are needed, more switches with embedded WLCs can be added. 

- **Mobility Express** WLC deployment model
	- The WLC is integrated within an AP.
	- A Mobility Express WLC can support up to about **100 APs**.