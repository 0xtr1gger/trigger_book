---
created: 2026-09-22
updated: 2026-09-27
tags:
  - services_n_protocols
---
## SNMP

>**[SNMP (Simple Network Management Protocol)](https://en.wikipedia.org/wiki/Simple_Network_Management_Protocol)** is an application-layer framework and protocol used to monitor, manage, and configure network-attached devices — such as routers, switches, servers, printers, and firewalls — from a central management station.

- SNMP was originally released in 1988 and has since evolved through three major versions; the current version is **SNMPv3**.
- SNMP follows a **manager–agent model**: a central station queries and configures agents running on managed devices, and agents report events back to the station.
- SNMP can read a device's status (interface state, CPU usage, temperature), change its configuration, and receive asynchronous event notifications.

>[!important] SNMP runs over **UDP**, not TCP. Agents listen on **UDP port `161`** and managers receive notifications on **UDP port `162`**.

>[!note] Don't let the word 'simple' in the name fool you — SNMP is a large, extensible framework defined across a series of RFCs ([`RFC 1157`](https://www.rfc-editor.org/rfc/rfc1157) for SNMPv1, [`RFC 1901`](https://www.rfc-editor.org/rfc/rfc1901)/[`RFC 3416`](https://www.rfc-editor.org/rfc/rfc3416) for SNMPv2c, and [`RFC 3411`](https://www.rfc-editor.org/rfc/rfc3411)–[`RFC 3418`](https://www.rfc-editor.org/rfc/rfc3418) for SNMPv3).

- There are two main roles in an SNMP deployment:

	- **Managed devices**
		- Network devices managed via SNMP, such as routers, switches, servers, and printers.
		- Each runs an **SNMP agent** and exposes a **MIB** (see [[#SNMP components]]).
	- **Network Management Station (NMS)**
		- The control plane of SNMP — the system used to manage the managed devices.
		- Also referred to as the SNMP manager.

- Three main operations used in SNMP:
	1. Managed devices **notify the NMS of events** (e.g., an interface went down).
	2. The NMS **asks a managed device for information about its current status** (e.g., current CPU usage).
	3. The NMS **tells a managed device to change its configuration** (e.g., change an IP address on one of its interfaces).

### SNMP ports

| Port           | Role       | Description                                                                                         |
| -------------- | ---------- | --------------------------------------------------------------------------------------------------- |
| UDP port `161` | SNMP agent | Managed devices (agents) listen here for queries (`Get`, `GetNext`, `GetBulk`, `Set`) from the NMS. |
| UDP port `162` | SNMP trap  | The NMS listens here to receive `Trap` and `Inform` notifications sent by agents.                   |

- SNMP agents (managed devices) listen on **UDP port `161`**.
- SNMP managers (NMS) listen on **UDP port `162`**.

### SNMP components

>[!note]+ NMS (manager) components
> - **SNMP Manager**
> 	- Listens on **UDP port `162`**.
> 	- The software that interacts with managed devices — it sends requests, pushes configuration changes, and receives notifications.
> - **SNMP Application**
> 	- Provides the interface the network administrator interacts with.
> 	- Displays alerts, statistics, charts, etc.

>[!note]+ Managed-device components
> - **SNMP Agent**
> 	- Listens on **UDP port `161`**.
> 	- The agent software that runs on a managed device; it sends notifications to and receives messages from the NMS.
> - **MIB (Management Information Base)**
> 	- The hierarchical database of variables managed via SNMP.
> 	- Each variable is identified by an **Object ID (OID)**.
> 	- Example variables: interface status, traffic throughput, CPU usage, temperature, etc.

>[!note]+ Terminology
> - **Agent:** a software process that runs on a managed device and gathers management information.
> - **ASN.1 (Abstract Syntax Notation One):** a set of rules for storing data in a machine-independent format.
> - **MIB (Management Information Base):** a database that describes the objects a managed device exposes.
> - **NMS (Network Management System):** a central system that proactively gathers management information from managed devices.
> - **OID (Object Identifier):** a unique, dotted address that identifies a single variable within the MIB.
> - **Probe:** a standalone device that can monitor a network segment.
> - **RMON (Remote Network Monitoring):** an extension to the MIB that adds statistical and historical Physical and Data Link layer information.
> - **RMON2:** an extension to the MIB that adds statistical and historical Application layer information.

### SNMP OIDs and the MIB

- The MIB organizes managed objects into a hierarchical tree, and each object is addressed by an **Object Identifier (OID)** — a sequence of integers separated by dots that describes the path from the root of the tree to the object.

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

>[!note] To explore different OID values and their meanings, see [`oid-base.com`](https://oid-base.com/#oid).

### SNMP versions

Many versions of SNMP have been proposed, but only three major versions have achieved widespread use:

- **SNMPv1**
	- The original version of SNMP.
	- No built-in authentication and no support for encryption.
- **SNMPv2c**
	- Allows the NMS to retrieve large amounts of information in a single request (`GetBulk`); more efficient than SNMPv1.
	- The `c` refers to the **community strings** used as passwords — present in SNMPv1, removed from SNMPv2, and then reintroduced in SNMPv2c.
- **SNMPv3**
	- Much more secure; supports strong authentication and encryption (via a pre-shared key).
	- Should be used whenever possible.

>[!warning] There is **no encryption** in SNMPv1 and SNMPv2c. Community strings and all queried data traverse the network in cleartext.

### SNMP messages

| Message class | Description                                                 | Messages                        |
| ------------- | ----------------------------------------------------------- | ------------------------------- |
| Read          | Sent by the NMS to read information from managed devices.   | `Get`<br>`GetNext`<br>`GetBulk` |
| Write         | Sent by the NMS to change configuration on managed devices. | `Set`                           |
| Notification  | Sent by managed devices to alert the NMS of an event.       | `Trap`<br>`Inform`              |
| Response      | Sent in response to a previous message or request.          | `Response`                      |

>[!important] SNMP Read messages
>- **`Get`** — a request from the NMS to an agent to **retrieve the value of one or more variables** (identified by OIDs). The agent replies with a `Response` carrying the current value of each requested variable.
>- **`GetNext`** — a request from the NMS to an agent to **discover the available variables in a device's MIB**, one after another.
>- **`GetBulk`** — a more efficient version of `GetNext` (introduced in SNMPv2) that retrieves many variables in a single request.

>[!important] SNMP Write messages
>- **`Set`** — a request from the NMS to an agent to **change the value of one or more variables**. The agent replies with a `Response` carrying the new values.

>[!important] SNMP Notification messages
>- **`Trap`** — an unsolicited notification sent from an agent to the NMS. No acknowledgment is returned, so these messages are considered 'unreliable'.
>- **`Inform`** — a notification that **is acknowledged** by the NMS with a `Response` message.

>[!important] SNMP Response messages
>- **`Response`** — a message sent in reply to a previous request (`Get`, `Set`, etc.).


## Enumerating SNMP

### Port scanning and version detection

- Scan the default SNMP port over **UDP** with service version detection:

```bash
sudo nmap -sU -p 161 -sV 10.10.11.5
```

- Scan both the agent and trap ports and run all available SNMP NSE scripts:

```bash
sudo nmap -sU -p 161,162 --script "snmp-*" 10.10.11.5
```

| Option     | Description                                                       |
| ---------- | ----------------------------------------------------------------- |
| `-sU`      | Scan UDP ports (SNMP runs over UDP).                              |
| `-sV`      | Enable service version detection.                                 |
| `-p`       | Specify destination port(s) to scan (`161,162`).                  |
| `--script` | Execute a specific NSE script or glob expression.                 |

>[!important] SNMP runs over UDP, so a standard TCP scan will miss it entirely. UDP scans are slow and prone to false positives (`open|filtered`); combine `-sU` with `-sV` or an NSE script to confirm the service.

- Key Nmap SNMP scripts:

| Script                                                                          | Categories                     | Description                                                                                     |
| ------------------------------------------------------------------------------- | ------------------------------ | ----------------------------------------------------------------------------------------------- |
| [`snmp-info`](https://nmap.org/nsedoc/scripts/snmp-info.html)                   | `default`, `discovery`, `safe` | Extract basic information (engine ID, vendor) from an SNMPv3 GET request.                        |
| [`snmp-sysdescr`](https://nmap.org/nsedoc/scripts/snmp-sysdescr.html)           | `default`, `discovery`, `safe` | Retrieve the system description and uptime from the `sysDescr` OID.                             |
| [`snmp-brute`](https://nmap.org/nsedoc/scripts/snmp-brute.html)                 | `intrusive`, `brute`           | Brute-force the community string against the target.                                            |
| [`snmp-interfaces`](https://nmap.org/nsedoc/scripts/snmp-interfaces.html)       | `default`, `discovery`, `safe` | Enumerate the network interfaces of the device.                                                 |
| [`snmp-netstat`](https://nmap.org/nsedoc/scripts/snmp-netstat.html)             | `default`, `discovery`, `safe` | Retrieve a `netstat`-like list of active connections.                                           |
| [`snmp-processes`](https://nmap.org/nsedoc/scripts/snmp-processes.html)         | `default`, `discovery`, `safe` | Enumerate running processes, including their paths and arguments.                               |
| [`snmp-win32-users`](https://nmap.org/nsedoc/scripts/snmp-win32-users.html)     | `default`, `discovery`, `safe` | Enumerate Windows user accounts via the LanManager MIB.                                          |
| [`snmp-win32-services`](https://nmap.org/nsedoc/scripts/snmp-win32-services.html) | `default`, `discovery`, `safe` | Enumerate Windows services.                                                                     |
| [`snmp-win32-software`](https://nmap.org/nsedoc/scripts/snmp-win32-software.html) | `default`, `discovery`, `safe` | Enumerate installed software from the Windows host MIB.                                          |
| [`snmp-win32-shares`](https://nmap.org/nsedoc/scripts/snmp-win32-shares.html)   | `default`, `discovery`, `safe` | Enumerate Windows shares.                                                                       |

>[!tip]+
> - List local Nmap scripts for SNMP:
> 
> ```bash
> ls -l /usr/share/nmap/scripts/*snmp*
> ```

### Grabbing the system description

- Confirm access with a default community string by reading the system branch (`1.3.6.1.2.1.1`), which returns the description, uptime, contact, and location:

```bash
snmpwalk -v2c -c public 10.10.11.5 1.3.6.1.2.1.1
```

- Retrieve just the system description (`sysDescr`) with the Nmap script:

```bash
sudo nmap -sU -p 161 --script snmp-sysdescr 10.10.11.5
```

>[!tip]+
> - The `sysDescr` string usually reveals the OS, hardware model, and firmware/software version — a good starting point for looking up CVEs.

## Brute-forcing community strings

Because SNMPv1/v2c authentication reduces to a single community string, guessing it is fast and often the first step:

- Brute-force community strings using `onesixtyone`:

```bash
onesixtyone -c /usr/share/seclists/Discovery/SNMP/snmp.txt 10.10.11.5
```

| Option | Description                                            |
| ------ | ------------------------------------------------------ |
| `-c`   | Read community strings from the given wordlist file.   |
| `-i`   | Read target hosts from a file.                         |
| `-o`   | Write results to an output file.                       |

- Brute-force community strings using Hydra:

```bash
hydra -P /usr/share/wordlists/rockyou.txt -s 161 snmp://10.10.11.5
```

| Option | Description                              |
| ------ | ---------------------------------------- |
| `-P`   | Read community strings from a wordlist.  |
| `-s`   | Set the target port (`161`).             |

- Brute-force community strings using the Nmap [`snmp-brute`](https://nmap.org/nsedoc/scripts/snmp-brute.html) script:

```bash
sudo nmap -sU -p 161 --script snmp-brute 10.10.11.5 --script-args snmp-brute.communitiesdb=/usr/share/seclists/Discovery/SNMP/snmp.txt
```

>[!note] Common default community strings to try first are `public` (read-only) and `private` (read-write); vendor-specific defaults such as `cisco`, `manager`, or `admin` are also worth testing.

## Interacting with SNMP

Once a valid community string is known, the MIB can be queried to extract host and network information.

### Walking the MIB tree

- **`snmpwalk`**
	- Issues a sequence of `GetNext` requests to traverse and dump the MIB subtree beneath a given OID (or the entire tree when no OID is supplied).

- Dump the entire MIB with a known community string:

```bash
snmpwalk -v2c -c public 10.10.11.5
```

- Walk a specific subtree by supplying its OID:

```bash
snmpwalk -v2c -c public 10.10.11.5 1.3.6.1.2.1.25.4.2.1.2
```

| Option  | Description                                                        |
| ------- | ------------------------------------------------------------------ |
| `-v`    | Set the SNMP version (`1`, `2c`, or `3`).                          |
| `-c`    | Set the community string.                                          |
| `-On`   | Print OIDs numerically instead of resolving them to names.         |
| `-Oa`   | Print string values as ASCII text.                                 |

>[!note] Without MIB definitions installed, `snmpwalk` prints numeric OIDs. Install the `snmp-mibs-downloader` package (and enable MIB loading) to resolve them to human-readable names.

### Automated enumeration

- **`snmp-check`**
	- Queries an SNMP host and formats the results into readable sections (system info, network interfaces, routing, running processes, installed software, users, and more).

```bash
snmp-check -v 2c -c public 10.10.11.5
```

| Option | Description                                            |
| ------ | ------------------------------------------------------ |
| `-c`   | Set the community string (default: `public`).          |
| `-v`   | Set the SNMP version (`1` or `2c`).                    |
| `-p`   | Set the destination port (default: `161`).             |
| `-w`   | Detect whether the community string grants write access. |

- **`braa`**
	- A mass SNMP scanner that queries many OIDs across many hosts quickly, useful for large ranges once a community string is known.

```bash
braa public@10.10.11.5:.1.3.6.*
```

### Querying specific OIDs

- Target high-value OIDs directly with `snmpwalk` to extract specific categories of information:

| OID                      | Description                                                            |
| ------------------------ | ---------------------------------------------------------------------- |
| `1.3.6.1.2.1.1`          | System branch — description, uptime, contact, name, and location.      |
| `1.3.6.1.2.1.25.1.6.0`   | Number of running system processes.                                    |
| `1.3.6.1.2.1.25.4.2.1.2` | Names of running programs.                                             |
| `1.3.6.1.2.1.25.4.2.1.4` | Paths of running programs.                                             |
| `1.3.6.1.2.1.25.4.2.1.5` | Command-line arguments of running programs (may leak credentials).     |
| `1.3.6.1.2.1.25.6.3.1.2` | Installed software.                                                    |
| `1.3.6.1.2.1.25.2.3.1.4` | Storage units.                                                         |
| `1.3.6.1.2.1.2.2.1`      | Network interfaces.                                                    |
| `1.3.6.1.2.1.6.13.1.3`   | Local TCP ports.                                                       |
| `1.3.6.1.4.1.77.1.2.25`  | Windows user accounts.                                                 |
| `1.3.6.1.4.1.8072.1.3.2` | `NET-SNMP-EXTEND-MIB` extended objects (custom scripts and commands).  |

- Enumerate Windows user accounts:

```bash
snmpwalk -v2c -c public 10.10.11.5 1.3.6.1.4.1.77.1.2.25
```

- Enumerate the arguments passed to running processes (a common source of leaked credentials):

```bash
snmpwalk -v2c -c public 10.10.11.5 1.3.6.1.2.1.25.4.2.1.5
```

- Inspect Net-SNMP extended objects, which can expose the output of custom scripts configured on the host:

```bash
snmpwalk -v1 -c public 10.10.11.5 NET-SNMP-EXTEND-MIB::nsExtendObjects
```

>[!tip]+
> - When a **read-write** community string is available, confirm write access with `snmp-check -w` before attempting any `Set` operation, and avoid changing device configuration on production systems unless the engagement explicitly authorizes it.

## References and further reading

- [`Simple Network Management Protocol — Wikipedia`](https://en.wikipedia.org/wiki/Simple_Network_Management_Protocol)
- [`A Simple Network Management Protocol (SNMP) — RFC 1157`](https://www.rfc-editor.org/rfc/rfc1157)
- [`Introduction and Applicability Statements for Internet Standard Management Framework — RFC 3410`](https://www.rfc-editor.org/rfc/rfc3410)
- [`An Architecture for Describing SNMP Management Frameworks — RFC 3411`](https://www.rfc-editor.org/rfc/rfc3411)
- [`Management Information Base — Wikipedia`](https://en.wikipedia.org/wiki/Management_information_base)
- [`OID Repository — oid-base.com`](https://oid-base.com/#oid)
- [`Net-SNMP documentation`](https://www.net-snmp.org/docs/man/)
- [`161,162,10161,10162 UDP - Pentesting SNMP — HackTricks`](https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-snmp/index.html)

