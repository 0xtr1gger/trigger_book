---
created: 2025-10-30 03:36:12
tags:
  - wireless
---


- Configure DHCP so that the switch tells the AP the IP address of their WLC, configure the `43` option:

```toml
SW1(dhcp-config)# option 43 ip 192.168.1.11
```


>[!note] This is not necessary if the AP and the WLC are in the same subnet.
>The WLC will hear the APs broadcast CAPWAP discovery messages.

## WLC ports and interfaces

- WLC **ports** are physical ports that cables connect to.
- WLC **interfaces** are logical interfaces within the WLC (e.g., SVIs on switch).

### WLC ports 

WLCs have a few different kinds of **ports**:

- **Service port**
	- A dedicated management port.
	- used for OOB management.
	- Must connect to a switch access port (only supports one VLAN).
	- This port can be used to connect to the device while it's booting, performing system recovery, etc.

- **Distribution system port**
	- These are standard network ports that connect to the distribution system (DC) and are used for data traffic. 
	- These ports usually connect to switch trunk ports, and if multiple distribution ports are used, they can form a LAG.

- **Console port**
	- A standard console port, e.g., RJ-45 or USB.

- **Redundancy port**
	- This port is used to connect to another WLC to form a high availability pair.

![[WLC_ports.png]]

### WLC interfaces

WLCs have a few different kinds of **interfaces**:

- **Management interfaces**
	- Used for management traffic, such as Telnet, SSH, HTTP, HTTPS, RADIUS, authentication, NTP, Syslog, etc.
	- CAPWAP tunnels are also formed to/from the WLC's management interface.
	- This interface is used for all Layer 2 LWAPP communications between the controller and the lightweight APs. 
	- The management interface is also used to communicate with other WLCs on the wireless network.

- **Redundancy management interfaces**
	- When two WLCs are connected by their redundancy ports, one WLC is **active** and the other is **standby**. 
	- This interface can be used to connect to and manage the **standby** WLC.

- **Virtual interfaces**
	- This interface is used when communicating with wireless clients to relay DHCP requests, perform client web authentication, etc.

- **Service port interfaces**
	- Used for out-of-band (OOB) maintenance purposes on a WLC.
	- This is a physical interface on the WLC that can be used for recovery purposes in the event of failure.
	- This is the only interface available while the WLC is booting. 
	- It is used as a last-resort measure to access the WLC GUI.

>[!note] Alternatively, you can use the **console port** to access the WLC command-line interface (CLI). The console port is an out-of-band asynchronous interface and is typically accessed with a serial cable or a USB to RJ-45 adapter.

- **Dynamic interfaces**
	- Dynamic interfaces are user-defined and are typically used for client data.
	- These interfaces are used to map a WLAN to VLAN. 
	- For example, traffic from the 'internal' WLAN will be sent to the wired network from the WLC's 'internal' dynamic interface.

>[!note] Management, virtual, redundant management, and service port interfaces are **static** interfaces.

>[!note] A WLC can contain up to 512 dynamic interfaces.