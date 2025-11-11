---
created: 2025-10-29 03:53:31
tags:
  - network_topology
---
## WAN

>**WAN (Wide Area Network)** is a network that extends over a large geographic area. 

- WANs are used to connect geographically separate LANs.

>[!note] Although the Internet itself can be considered a WAN, the term WAN is typically used to refer to an enterprise's private connections that connect their offices, data centers, and other sites together.

- Over public/shared networks like the Internet, VPNs (Virtual Private Networks) can be used to create private WAN connections.

## Leased lines

>A **leased line**, aka **private circuit**, is a private telecommunications circuit between two or more locations provided according to a commercial contract.

- A **leased line** is a dedicated physical link, typically connecting two sites.
- Leased lines use **serial connections** (PPP or HDLC encapsulation).

Due to the higher cost, higher installation lead time, and slower speeds of leased lines, Ethernet WAN technologies are becoming more popular.
## MPLS

>**Multi Protocol Label Switching (MPLS)** is a networking technology that directs traffic from one node to the next based on **short path labels** rather than long network addresses.

- Similar to the Internet, service providers' MPLS networks are **shared infrastructure**, because many customer enterprises connect to and share the same infrastructure to make WAN connections. 
- However, the *label switching* in the name of MPLS allows VPNs to be created over the MPLS infrastructure through the use of **labels**. 


>[!note]+
>- Labels are used to separate the traffic of different customers as it travels over the shared infrastructure.
>- These labels are used to make forwarding decisions within the service provider network, not the destination network.

>[!important]+ Important terms
> 
> - **CE** router = **Customer Edge** router
> 	- Customer's router.
> 
> - **PE** router = **Provider Edge** router
> 	- Connect to customer routers.
> 
> - **P** router = **Provider core** router
> 	- Don't connect to customer routers; form the internal network infrastructure of the service provider's network.
> ![[MPLS_routers.png]]

- When the PE routers receive frames from the CE routers, they add a **label** to the frame. 
- MPLS is only used by the PE/P routers.
- The CE routers don't use MPLS. 

>[!note] Labels are placed between the Layer 2 Ethernet header and Layer 3 IP header, therefore sometimes MPLS is called a **Layer 2.5 protocol**.   

There are a few kinds of VPNs that can be provided by MPLS:

- **Layer 3 MPLS VPNs**
	- When using a Layer 3 MPLS VPN, the CE and PE routers **peer using OSPF**, or any other routing protocol/static routes, to share routing information. 

- **Layer 2 MPLS VPNs**
	- When using a Layer 2 MPLS VPN, the CE and PE routers do not form peerings.
	- The service provider network is **entirely transparent to the CE routers**. 
	- It works as if two CE routers are directly connected: **their WAN interfaces will be in the same subnet**. 
	- If a routing protocol is used, the two CE routers will peer directly with each other. 
	- In this case, **the entire service provider network is acting as a big switch** connecting the CE routers together.

Many different technologies can be used to connect to the service provider's MPLS network for WAN service: wireless 4G/5G, CATV (Cable TV), Serial, Ethernet (Fiber optic), etc.

## Internet connections

There are countless ways for an enterprise to connect to the Internet, e.g., 
- MPLS VPN
- CATV
- DSL
- Fiber optic Ethernet
## DSL

>Digital Subscriber Line (DSL) is a technology used to transmit data over telephone lines. 

- DSL uses the copper wire infrastructure of the PSTN, the phone lines, to provide internet connectivity to customers; it share the same phone line that is already installed in most homes.

- A **DSL modem (modulator-demodulator)** is required to convert data into a format suitable to be sent over the phone lines.
	- A modem might be a separate device, or it might be incorporated into the home router.

>A **modem (modulator-demodulator)** is a device used to convert data from **digital format** into a format suitable for **analog transmission**, such as telephone or radio. 

![[DSL.png]]
## Cable Internet

>**Cable Internet access**, or **cable Internet**, is a form of broadband internet access which uses the same infrastructure as cable television.

- Cable Internet provides Internet access via the same **CATV (Cable Television)** lines that are used for TV service. 

- Like DSL, a **cable modem** is required to convert data into a format suitable to be sent over the CATV cables.
	- Like a DSL model, this can be a separate device or built into the home router.

>[!note] Cable models provide speeds of up to 27 Mbps, making cable one of the fastest options for home Internet service. 

![[CATV.png]]
## Redundant Internet connections

| Connection          | Description                               | Diagram                      |
| ------------------- | ----------------------------------------- | ---------------------------- |
| **Single Homed**    | 1 connection to 1 ISP<br>No redundancy    | ![[single_homed.drawio.svg]] |
| **Dual Homed**      | 2 connections to 1 ISP                    | ![[dual_homed.svg]]          |
| **Multihomed**      | 2 connections to each of 2 different ISPs | ![[multihomed.svg]]          |
| **Dual Multihomed** | 2 connections to each of 2 different ISPs | ![[dual_multihomed.svg]]     |

## Internet VPNs

- Private WAN services such as leased lines and MPLS provide security because each customer's traffic is separated by using dedicated physical connections (leased lines) or by MPLS labels. 
- However, when using the public Internet as a WAN to connect sites together, there is no built-in security by default. 
- To provide secure communications over a shared network like the Internet, VPNs (Virtual Private Networks) are used. 

>**A Virtual Private Network (VPN)** is a mechanism for creating a secure connection between sites over a shared network such as the public Internet.

We will discuss two kinds of Internet VPNs:
- Site-to-Site VPNs using IPsec
- Remote-access VPNs using TLS

### Site-to-Site VPNs using IPsec

#### Site-to-Site VPNs

>A **Site-to-Site VPN** is a type of VPN that establishes connections between sites (networks) over an untrusted network, such as the Internet. 

- Site-to-Site VPNs connect **entire networks** together. 
- Remote access servers or firewalls on the network’s border act as the start points for VPNs.
- Therefore, **traffic is not protected within the source LAN**, protected between the LANs over a public network, and then **not protected again once it reaches the destination LAN**.

![[site-to-site_VPN.svg]]

1. The sending device combines the original packet and session key (encryption key) and encrypts the packet.
2. The sending device the encapsulates the encrypted packet with a VPN header and a new IP header.
3. The sending device sends the new packet to the device on the other side of the tunnel.
4. The receiving device decrypts the data to get the original packet, and then forwards the original packet to its destination.

>[!important] The tunnel is formed only between the tunnel endpoints (e.g., routers).
>- All other devices in each site don't need to create a VPN for themselves. They can send unencrypted data to their site's router, which will encrypt it and forward it in the tunnel.

>[!important] Limitations of standard IPsec
>- **IPsec doesn't support broadcast and multicast traffic**, only unicast. This means that routing protocols such as OSPF can't be used over the tunnels, because they rely on multicast traffic.
>	- This can be solved with **GRE over IPsec**.
>- Configuring a full mesh of tunnels between many sites is a labor-intensive task.
>	- This can be solved with Cisco's DMVPN.

#### GRE over IPsec

>**GRE (Generic Routing Encapsulation)** is a tunneling protocol that encapsulates data packets of one network protocol within another network protocol, allowing them to be transmitted over a network that may not support the original protocol.

- The advantage of GRE comes with its ability to encapsulate a wide variety of **Layer 3 protocols**, as well as **broadcast and multicast** messages.
- However, GRE doesn't encrypt the traffic. 
	- GRE doesn't encrypt, authenticate, or provide integrity checks for network packets. GRE is insecure.

- To get the flexibility of GRE and security of IPsec, **GRE over IPsec** can be used.

- The original packet will be encapsulated by a GRE header and a new IP header, and then the GRE packet will be encrypted and encapsulated within an IPsec VPN header and new IP header.

![[GRE_encapsulation.svg]]


![[ipsec_modes.png]]

Meanwhile, IPsec can operate in two primary modes: **transport mode** and **tunnel mode**.


- **Transport mode**
	- Does not encrypt the IP or IPsec header.
	- Only the data payload of the packet is encrypted.
	- Commonly used for host-to-host VPNs. 
	- Best used only within a trusted network between individual systems (since it doesn't encrypt the header).
	- Less compatible with [[NAT]] than tunnel mode.

![[transport_mode_VPN.png]]

- **Tunnel mode**
	- Encrypts the entire packet, both the IP header and data payload.
	- Requires additional headers.
	- Encapsulates the original IP packet within a new IPsec packet.
	- Commonly used for site-to-site VPNs.
	- Mode is suitable to be used across untrusted networks (since both IP header and payload are encrypted).
	

![[tunneling_mode_VPN.png]]
#### Cisco DMPVN

>**DMVPN (Dynamic Multiport VPN)** is a Cisco-developed solution that allows routers to dynamically create a full mesh of IPsec tunnels without having to manually configure every single tunnel.

![[DMVPN.png]]

>[!important] DMVPN provides the configuration simplicity for hub-and-spoke (each spoke router only needs one tunnel configured) and the efficiency of direct spoke-to-spoke communication (spoke routers can communicate directly without traffic passing through the hub).
### Remote-access VPNs using TLS

>Whereas site-to-site VPNs are used to make a point-to-point connection between two sites over the Internet, remote-access VPNs are used to allow end devices (PCs, mobile phones) to access the company's internal resources security over the Internet.

- Remote-access VPNs typically use TLS (Transport Layer Security).
- VPN client software (e.g., Cisco AnyConnect) is installed on end devices (e.g., company-provided laptops that employees use to work from home).
- These end devices then form secure tunnels to one of the company's routers/firewalls acting as a TLS server.
- This allows the end users to security access resources on the company's internal network without being directly connected to the company network.