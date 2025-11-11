---
created: 2025-10-26 03:40:17
tags:
  - protocols
---
## SNMP

>**SNMP (Simple Network Management Protocol)** is an industry standard *framework* and protocol 

>[!note] SNMP was originally released in 1988.

- The current version of SNMP is **SNMPv3**.

>[!warning] Don't let the word 'simple' in the name fool you! SNMP is not simple. 

>[!important] SNMP uses UDP.

- SNMP can be used to monitor the status of devices, make configuration changes, etc.

There are two main types of devices in SNMP:

- **Managed devices**
	- Devices managed using SNMP, such as routers and switches.

- **Network Management Station, or System (NMS)**
	- The control plane of SNMP  — devices used to manage the managed devices.

>[!important]
>- SNMP Agents (managed devices) listen on **UDP port `161`**.
>- SNMP Managers (NMS) listen on **UDP port `162`**.

>[!important] Three main operations used in SNMP:
> 
> 1. Managed devices can **notify the NMS of events**
> 	- e.g., notify the NMS an interface went down
> 
> 2. The NMS can **ask the managed devices for information about their current status**
> 	- e.g., the NMS asks a device about its current CPU usage
> 
> 3. The NMS can tell the managed devices to **change aspects of their configuration**
> 	- e.g., the NMS asks a device to change an IP address on one of its interfaces

## SNMP components

>[!important] NMS components:
> 
> - **SNMP Manager**
> 	- Listen on **UDP port `162`**.
> 	- The software that interacts with the managed devices.
> 	- It receives notifications, requests for information, sends configuration changes, etc.
> 
> - **SNMP Application**
> 	- Provides an interface for the network administrator to interact with.
> 	- Displays alerts, statistics, charts, etc.

>[!important] Components of managed devices:
> - **SNMP Agent**
> 	- Listens on **UDP port `161`**.
> 	- SNMP agent software that runs on managed devices.
> 	- Sends notifications to and receives messages from the NMS.
> 
> - **MIB (Management Information Base)**
> 	- The structure that contains variables managed by SNMP.
> 	- Each variable is identified with an **Object ID (OID)**.
> 	- Example variables: interface status, traffic thoughput, CPU usage, temperature, etc.

>[!note]+ 
> - **Agent:** a software process that runs on a managed device and gathers management information.
> - **ASN.1 (Abstract Syntax Notation One):** a set of rules for storing data in a machine-independent format.
> - **MIB (Management Information Base):** a database that contains information about a managed device.
> - **NMS (Network Management System):** a central system that proactively gathers management information from managed devices.
> - **Probe:** a standalone device that can monitor a network segment.
> - **RMON (Remote Network Monitoring):** an extension to the MIB that adds statistical and historical Physical and Data Link layer information.
> - **RMON2:** an extension to the MIB that adds statistical and historical Application layer information.

## SNMP OIDs

- SNMP Object IDs are organized in a hierarchical structure.

```bash
. 1 . 3 . 6 . 1 . 2 . 1 . 1 . 5

  |   |   |   |   |   |   |   |   
 iso  |   |   |  mgmt |   |   |
      |  dod  |       |   | sysName
      |       |     mib-2 |
      |       |           |
      |       |         system
      |    internet
      |
  identified
 organization
```

If you want to explore different OID values, see [`oid-base.com`](https://oid-base.com/#oid).
## SNMP versions

Many versions of SNMP have been proposed/developed, however, only three major versions have achieved widespread use:

- **SNMPv1**
	- Original version of SNMP.
	- No built-in authentication.
	- No support for encryption.

- **SNMPv2c**
	- Allows the NMS to retrieve large amounts of information in a single request; more efficient.
	- `c` refers to the 'community strings' used as passwords in SNMPv1, removed from SNMPv2, and then added back to SNMPv2c.

- **SNMPv3**
	- Much more secure; supports strong encryption (via pre-shared key, PSK) and authentication.
	- Should be used whenever possible.

>[!warning] There is no encryption in SNMPv1 and SNMPv2c.

## SNMP messages

| Message Class | Description                                                 | Messages                        |
| ------------- | ----------------------------------------------------------- | ------------------------------- |
| Read          | Sent by NMS to read information from the managed devices.   | `Get`<br>`GetNext`<br>`GetBulk` |
| Write         | Sent by NMS to change configuration on the managed devices. | `Set`                           |
| Notification  | Sent by managed devices to alert the NMS of an event.       | `Trap`<br>`Inform`              |
| Response      | Sent in response to a previous message/request.             | `Response`                      |

>[!important] SNMP Read messages
>- **`Get`**
>	- A request sent from an SNMP Manager (NMS) to an SNMP Agent (managed device) to **retrieve the value of a variable (identified by OIDs) or multiple variables**.
>	- The SNMP Agent will send a Response message with the current value of each requested variable.
>- **`GetNext`**
>	- A request sent from an SNMP Manager (NMS) to an SNMP Agent (managed device) to **discover available variables in the MIB on a managed device**.
>- `GetBulk`
>	- A more efficient version of the`GetNext` message (introduced in SNMPv2). 

>[!important] SNMP Write messages
>- **`Set`**
>	- A request sent from an SNMP Manager (NMS) to an SNMP Agent (managed device) to change the value of one or more variables.
>	- The SNMP Agent will send a Response message with the new values.

>[!important] SNMP Notification messages
>- **`Trap`**
>	- A notification sent from an SNMP Agent (managed device) to an SNMP Manager (SNMP).
>	- No acknowledgment is sent, thus these messages are 'unreliable'.
>- **`Inform`**
>	- A notification message that is **acknowledged** with a Response message.

>[!important] SNMP Response messages
>- `Response`
>	- Messages sent in response to a previous message or request.
## Configuration

```toml
# managed device

# optional info
R1(config)# snmp-server contact email@example.com
R1(config)# snmp-server location Location House

# two community strings
# no Set messages
R1(config)# snmp-server community Jeremy1 ro 
# can use Set messages
R1(config)# snmp-server community Jeremy2 rw

# specify the address of the NMS, SNMP version, and community
R1(config)# snmp-server host 192.168.1.1 versoin 2c Jeremy1

# ocnfigure the Trap types to send to the NMS
R1(config)# snmp-server enable traps snmp linkdown linkup
R1(config)# snmp-server enable traps config
```

