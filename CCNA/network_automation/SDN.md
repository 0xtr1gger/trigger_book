---
created: 2025-10-17 09:53:09
tags:
  - network_automation
---
## SDN architecture

Other than the logical data planes covered in [[network_automation_basics]], SDN can be divided into three layers:

- **Application layer**
	- Scripts and applications that tell the SDN controller what network behavior is desired.

- **Control layer**
	- The SDN controller that receives and processes instructions form the application layer.

- **Infrastructure layer**
	- Network devices responsible for forwarding messages across the network.

## Cisco SD-Access

>**Cisco SD-Access (Software-Defined Access)** is Cisco's SDN solution for automating campus LANs.

- Cisco **DNA (Digital Network Architecture) Center** is the controller at the center of SD-Access.

![[SD-Access_architecture.svg]]

### Fabric

>The **underlay** is the underlying *physical network* of devices and connections (including wired and wireless) which provide IP connectivity (i.e., using IS-IS).
- Multilayer switches and their connections.

![[underlay.svg]]

>The **overlay** is the *virtual network* built on top of the physical underlay network.
- SD-Access uses a protocol called **VXLAN (Virtual Extensible LAN)** to build tunnels. 

![[overlay.svg]]

>The **fabric** is the combination of the overlay and underlay; the physical and virtual network as a whole.

![[fabric.svg]]


>[!note]+ Cisco has other SDN solutions as well:
> - **ACI (Application Centric Infrastructure)**
> 	- SDN solution for automating data center networks.
> - **SD-WAN (Software-Defined WAN)**
> 	- SDN solution for automating WANs.
#### SD-Access underlay

>The purpose of the **underlay** is to support the VXLAN tunnels of the overlay.

There are three different roles for switches in SD-Access:

- **Edge nodes**
    - Connect to end hosts.

- **Border nodes**
    - Connect to devices outside of the SD-Access domain, i.e., WAN routers.

- **Control nodes**
    - Use **LISP (Locator ID Separation Protocol)** to perform various control plane functions.

>[!note]+ **Virtual Extensible LAN (VXLAN)** is an encapsulation protocol that enables VLANs to be stretched across subnets and geographic distances. 
>- VLANs are typically restricted to Layer 2 network areas and are not able to include hosts from other networks
>- VXLAN allows for up to **16 million** virtual networks to be created, whereas traditional VLANs are limited to only 4,096. 
>- VXLAN can be used as a means to implement microsegmentation without limiting segments to local entities only.
>- VXLAN is defined in [RFC 7348](https://datatracker.ietf.org/doc/html/rfc7348).

>[!important]+ Brownfield deployment
>You can add SD-Access on top of an existing network if the network hardware and software supports it. This is called a **brownfield deployment**. 
>- In this case DNS Center won't configure the underlay.

>[!important]+ Greenfield deployment
>A new deployment, called **greenfield deployment**, will be configured by DNA Center to use the optimal SD-Access underlay:
> - All switches are **Layer 3 (multilayer)** and use **IS-IS** as their routing protocol. 
> - All links between switches are **routed ports** (i.e., STP is not needed).
> - Edge nodes (access switches) act as the default gateway of end hosts (routed access layer).
#### SD-Access overlay

- **LISP** provides the control plane of SD-Access.
	- A list of mappings of **EIDs (endpoint identifiers)** to **RLOCs (routing locators)** is kept.
	- EIDs identify end hosts connected to edge switches, and RLOCs identify the edge switch which can be used to reach the end host.
- **Cisco TrustSec (CTS)** provides policy control (QoS, security policy, etc.).
- VXLAN provides the **data plane** of SD-Access.
### Cisco DNA Center

Cisco DNA Center has two main roles:
- The SDN controller in SD-Access.
- A network manager in a traditional network (non-SD-Access).

>DNA Center is an application installed on Cisco UCS server hardware.
- DNA Center has a REST API which can be used to interact with it.

>[!important] The SBI supports protocols such as **NETCONF** and **RESTCONF**, as well as traditional protocols like **Telnet**, **SSH**, and **SNMP**, to control and monitor devices.

>DNA Center enables **Intent-Based Networking (IBN)**.
- The goal is to allow the engineer to communicate their intent for network behavior to DNA Center, and then DNA Center will take care of the details of the actual configurations and policies on devices. 

For example:
- Traditional security policies using ACLs can become very cumbersome.
	- ACLs can have thousands of entries. 
	- The intent of entries is forgotten with time and as engineers leave and new engineers take over. 
	- Configuring and applying the ACLs correctly across a network is cumbersome and leaves room for error.
- DNA Center allows the  engineer to specify the intent of the policy (this group of users can't communicate with this group, this group can access this server but not that server, etc.) and DNA Center will take care of the exact details of implementing the policy.

## DNA Center vs. Traditional Network Management

- **Traditional network management:**
	- Devices are configured one-by-one via SSH or console connection.
	- Devices are manually configured via console connection before being deployed. 
	- Configurations and policies are managed on per-device basis (distributed).
	- New network deployments can take a long time due to the manual labor required. 
	- Errors and failures are more likely due to increased manual effort.

- **DNA Center-based network management:**
	- Devices are centrally managed and monitored from the DNA Center GUI or other applications using its REST API.
	- The administrator communicates their intended network behavior to DNA Center, which changes those intentions into configurations on the managed network devices. 
	- Configurations and policies are centrally managed. 
	- Software versions are also centrally managed. DNA Center can monitor cloud servers for new versions and then update the managed devices. 
	- New network deployments are much quicker. New devices can automatically receive their configurations from DNA Center without manual configuration.

## Objectives

- SDN (Software-Defined Networking)
- SDA (Software-Defined Architecture)
- SDN controller
- API (Application Programming Interface)
- SBI (Southbound Interface)
- NBI (Northbound Interface)
- REST API
- Serialization

- brownfield deployment
- greenfield deployment 
	- IS-IS
	- Multilayer switches
- VXLAN (Virtual Extensible Local Area Network)
- Underlay
- Overlay
- Fabric
- SD-Access
- Edge nodes
- Border nodes
- Control nodes
- SD-Access
- DNA Center
#### Quiz 

1. Which of the following terms describes the  network of devices and physical connections?
	- a. Underlay
	- b. Fabric
	- c. Overlay
	- d. Tunnel

2. In which of the following layers would you expect to find scripts that interact with the controller?
	- a. Infrastructure
	- b. Application
	- c. REST
	- d. Control

3. Which of the following is a characteristic of an optimal SD-Access underlay network as configured by DNA Center? 
	- a. All switch are Layer 3 and use OSPF as their routing protocol.
	- b. All links between switches are Layer 3.
	- c. An FHRP is used to provide a redundant default gateway for end hosts. 
	- d. All links between switches run Cisco proprietary Rapid-PVST+.

4. Which protocol is used to create virtual tunnels in the SD-Access overlay?
	- a. LISP
	- b. IPsec
	- c. GRE
	- d. VXLAN

5. Which of the following are valid switch roles in Cisco SD-Access? (select three)
	- a. Control node
	- b. Management node
	- c. Border node
	- d. Edge node

6. Boson ExSim. To which of the following planes does a centralized controller connect by using a northbound API? (Select the best answer.)
	- a. the control plane
	- b. the data plane
	- c. the management plane
	- d. the application plane

7. Boson ExSim. Which of the following Cisco management solutions supports Cisco SDA?
	- a. Cisco IOS 15
	- b. Cisco Network Assistant
	- c. Cisco PI
	- d. Cisco DNA Center

| Question | Answer           |
| -------- | ---------------- |
| `1.`     | `a.`             |
| `2.`     | `d.`             |
| `3.`     | `b.`             |
| `4.`     | `d.`             |
| `5.`     | `a.`, `c.`, `d.` |
| `6.`     | `d.`             |
