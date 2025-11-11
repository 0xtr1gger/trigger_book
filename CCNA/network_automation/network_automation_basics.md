---
created: 2025-10-16 03:54:40
tags:
  - network_automation
---
## Network automation

- In the traditional model, engineers manage devices **one at a** time by connecting to their CLI via SSH. 

>[!note]+ Downsides of configuring devices one-by-one:
> - **Typos** and other small mistakes are common.
> - It is **time-consuming** and **very inefficient** in large-scale networks.
> - It is difficult to ensure that all devices adhere to the **organization's standard configurations**.
 
>[!note]+ Network automation provides many benefits:
> - **Human error**, such as typos, is **reduced**.
> - Networks become much more **scalable**: new deployments, network-wide changes, and troubleshooting can be implemented in a fraction of the time. 
> - **Network-wide policy compliance** can be assured (standard configuration, software versions, etc.).
> - The improved efficiency of network operations **reduces OpEx** (operational expenditures) of the network. Each task requires **fewer man-hours**.

There are various tools and methods that can be used to **automate** tasks in the network:
- SDN (Software-Defined Networking)
- Ansible
- Puppet
- Python scripts
- Etc.

## Network logical planes

>[!note]+ What does a router do?
> 
> - **Forwards messages between networks** by examining information in the Layer 3 header.
> - Uses a **routing protocols** like OSPF to share route information with other routers and builds a routing table.
> - Uses **ARP** to build an ARP table and map IP address to MAC addresses. 
> - Uses **Syslog** to keep logs of events that occur.
> - Allows a user to connect to the router CLI via SSH to manage it.

>[!note]+ What does a switch do?
> 
> - **Forwards messages within a LAN** by examining information in the Layer 2 header. 
> - Uses **STP** to ensure there are no Layer 2 loops in the network.
> - Builds a **MAC address table** by examining the source MAC address of frames.
> - Uses **Syslog** to keep logs of events that occur.
> - Allows a user to connect to the switch CLI via SSH to manage it.

>[!important]+ The various functions of network devices can be logically divided up into **planes**:
> - **Data plane**
> 	- Physical devices that forward data packets.
> - **Control plane**
> 	- The SDN controller software that makes decisions about how packets should be handled.
> - **Management plane**
> 	- Network applications and services that communicate their requirements to the controller.

>A **plane** is an abstract representation of where certain operations take place in networking.
### Data plane

>[!important]+ The Data plane
>- All tasks involved in **forwarding user data from one interface to another** are part of the **Data plane**.


>[!example]+ Data plane example: router
> - A **router** receives a packet, looks for the most specific match route in its routing table, and **forwards the packet out of the appropriate interface** to the next hop. 
> 	- A router also **de-encapsulates** the original Layer 2 header, and **re-encapsulates** it with a new header destined to the next hop's MAC address. 

>[!example]+ Data plane example: switch
> - A **switch** receives a frame, looks at the destination MAC address, and **forwards the frame out of the appropriate interface** (or floods it).
> 	- This includes functions like adding or removing 802.1Q VLAN tags.

>[!example]+ Data plane example: NAT
> - **NAT** is part of the Data plane: it's responsible for **changing the source/destination addresses** before forwarding packets. In other words, it is a part of the process of **forwarding packets.** 

>[!example]+ Data plane example: ACL, port security, and other security features
>- Deciding whether to **forward or discard** messages according to **ACL rules**, **port security**, etc. is a part of the **Data plane**.

>[!important]+ **Data plane** is also called the **forwarding plane**.

- The Data plane is typically implemented in **hardware**, such as network interface cards (NICs) or routers.

### Control plane

>[!important]+ The Control plane
> - How does a device's Data plane make its forwarding decisions?
> 	- Routing tables, MAC address tables, ARP tables, STP, etc.
> - Functions that build these tables (and other functions that *influence the Data plane*) are part of the **Control plane**. 

- The Control plane *controls* what the Data plane does, for example by building the router's routing table.

>[!note] The functions of the Control plane are considered **overhead work**.

>[!example]+ Control plane example: OSPF
> - The OSPF protocol itself doesn't forward user data packets, but it **informs the Data plane about how packets should be forwarded**.

>[!example]+ Control plane example: STP
> - STP itself isn't directly involved in the process of forwarding packets, but it **informs the Data plane about which interfaces should and shouldn't be used to forward frames**.

>[!example]+ Control plane example: ARP
> - ARP messages are not user data, but they are used to **build an ARP table which is used in the process of forwarding data**. 

>[!note]+ Distributed data and Control planes
>In traditional networking, the Data plane and Control plane are both distributed. **Each device has its own Data plane and its own Control plane.** The planes are **'distributed'** throughout the network.
### Management plane

>[!important]+ The Management plane
>- The **Management plane** is responsible for **managing, configuring, and monitoring the network infrastructure**. 

>[!note] Like the Control plane, the Management plane performs **overhead work**.
>- However, the Management plane doesn't directly affect the forwarding of messages in the Data plane. 

 >[!important] The **Management plane** consists of protocols that are used to **manage devices**. 
 
>[!example]+ Management plane examples: SSH
>- SSH is used to connect to the CLI of a device to configure and manage it.

>[!example]+ Management plane example: Syslog
>- Syslog is used to keep logs of events that occur on the device.

>[!example]+ Management plane example: SNMP
>- SNMP is used to monitor the operations of the device. 

>[!example]+ Management plane example: NTP
>- NTP is used to maintain accurate time on the device.

>[!note] Each vendor has its proprietary way to configure its devices.

>[!note]+ 
> The Data plane is the reason we buy routers and switches (and network infrastructure in general), to forward messages. However, the Control plane and Management plane are both necessary to enable the Data plane to do its job.
### A few words about the Data plane

- The operations of the Management plane and Control plane are usually managed by the CPU of the device. 
- However, this is not desirable for Data plane operations, as CPU processing is relatively slow. 
- Instead, a specialized hardware, **ASIC (Application-Specific Integrated Circuit)**, is used. **ASICs** are chips built for specific purposes.

>[!example]+ Example: ASICs in switches
> - When a frame is received, the **ASIC** is what's responsible for the **switching logic** (not the CPU).
> - The MAC address table is stored in special-purpose kind of memory called **TCAM (Ternary Content-Addressable Memory)** or just **CAM (Content-Addressable Memory)**, which allows for very fast MAC address lookups.
> - The **ASIC** feeds the destination MAC address of the frame into the TCAM, which returns the matching MAC address table entry. 
> - The frame is forwarded into the appropriate interface. 

>[!example]+ Example: ASICs in routers
>Modern routers also use a similar hardware Data plane: an ASIC designed for forwarding logic, and tables stored in TCAM.

>[!note]+ To summarize :
> - When a device receives control or management traffic (destined for the device itself), it will be processed in the CPU.
> - When a device receives data traffic which should pass through the device, it is processed by the ASIC for better performance. 
## SDN

>**Software-Defined Networking (SDN)**, also called **Software-Defined Architecture (SDA)**, or **Controller-Based Networking**, is an approach to network management that centralizes the control plane into an application called a **controller**.

- In other words, SDN is a way to control and manage computer networks using **software** instead of specialized hardware.

- Traditional Control planes use a distributed architecture. 
	- For example, each router in the network runs OSPF and the routers share routing information and then independently calculate their preferred routes to each destination. 

- An SDN controller centralizes Control plane functions, e.g., calculating routes. 
	- How much of the Control plane is centralized varies greatly. 

>[!important] The controller can interact programmatically with the network devices using **APIs (Application Programming Interface)**.

>[!note] To learn more about SDN, see [[SDN]].
## SBI and NBI

### Southbound interface

>**SBI (Southbound Interface)** connects the **SDN controller** to the **network devices in the Data plane**. 
- It allows the controller to **send configuration and commands** to devices such as switches or routers and receive status information back. 
- Examples: OpenFlow, SNMP, NETCONF.

>[!note]+ Software interfaces
> The terms SBI and NBI don't refer to any physical interfaces on devices, but rather **software interfaces**.

- The controller communicates with the managed devices via SBI and gathers information about them, such as:
	- Devices in the network
	- Network topology
	- Available interfaces on each device
	- Device configurations
	- etc.

> [!example]+ Examples of SBIs:
> - **OpenFlow**
> - **Cisco OpFlex**
> - **Cisco oneOK** (Open Network Environment Platform Kit)
> - **NETCONF**

### Northbound interface

>**NBI (Northbound Interface)** connects the **SDN controller** to the **application and network administrators**.

- It allows apps to **communicate their network needs and policies to the controller** via APIs (typically REST APIs).
- Data is sent in a structured (serialized) format such as JSON or XML.

> [!example]+ Examples of SBI
> - **OpenFlow**
> - **Cisco OpFlex**
> - **Cisco oneOK** (Open Network Environment Platform Kit)
> - **NETCONF

## Automation in traditional networks vs. SDN

Network tasks can be automated in traditional network architectures too:
- **Scripts** (i.e., Python) can be written to push commands to many devices at once.
- Python with good use of Regular Expressions can parse through `show` commands to gather information about the network devices. 

However, the robust and centralized data collected by SDN controllers greatly facilitates these functions.
- The controller collects information about all devices in the network. 
- **Northbound APIs** allow to access information in a format easily read by programs (e.g., **JSON**, **XML**, etc.).
- The centralized data facilitates network-wide analytics. 

SDN tools can provide the benefits of automation without the requirement of third-party scripts and applications:
- You don't need expertise in automation to make use of SDN tools.
- However, APIs allow third-party applications to interact with the controller, which can be very powerful. 

>[!note]+ To summarize
> Although SDN and automation aren't the same thing, the SDN architecture greatly facilitates the automation of various tasks in the network via the SDN controller and APIs. 