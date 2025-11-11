---
created: 2025-10-28 03:46:47
tags:
  - LAN_protocols
---

## Layer 2 discovery protocols

Layer 2 discovery protocols such as CDP and LLDP allow network devices to share information with and discover information about **directly connected neighbors**.

- These protocols operate at Layer 2, and doesn't use IP addresses. However, they can be used to share Layer 3 information. 

Shared information includes:
- Device ID (hostname)
- Local interface
- Neighbor interface
- Platform (model)
- Capabilities (router, switch, etc.)
- IP addresses
- Software version and OS
- VLAN information
- Power over Ethernet (PoE) information for connected devices

The two main protocols are:
- **CDP (Cisco Discovery Protocol)** — Cisco-proprietary
- **LLDP (Link Layer Discovery Protocol)** — industry-standard (IEEE 802.1AB).

>[!warning]
>Because Layer 2 discovery protocols share information about devices in a network, they can be considered a **security risk**, and that's why they are often not used.

Important facts:

| Feature                             | **CDP**            | **LLDP**                   |
| ----------------------------------- | ------------------ | -------------------------- |
| **Vendor**                          | Cisco-proprietary  | IEEE 802.1AB open standard |
| **Default status on Cisco devices** | Enabled by default | Disabled by default        |
| **Update interval**                 | 60 seconds         | 30 seconds                 |
| **Holdtime**                        | 180 seconds        | 120 seconds                |
| **Destination MAC address**         | `0100.0CCC.CCCC`   | `0180.C200.000E`           |
| **Reinitialization delay**          | -                  | 2 seconds                  |
## CDP

>**CDP (Cisco Discovery Protocol)** is a Cisco-proprietary Layer 2 discovery protocol. 

- CDP is **enabled globally** on Cisco devices (routers, switches, firewalls, IP phones, etc.) **by default**.

>[!important] CDP-enabled devices periodically send out unsolicited multicast advertisements, **CDP messages**, to the **multicast MAC address `01:00:0C:CC:CC:CC`**. By default, CDP messages are sent every **60 seconds** out of all interfaces.

- When a device receives a CDP message from a neighboring device, it adds an entry for the device in its **CDP neighbor table**.

- To show **CDP neighbor table**:

```toml
R1# show cdp neighbors
```

- To see more **detailed information on CDP neighbors**:

```toml
R1# show cdp neighbor detail
```

If CDP is not enabled on the device, you will get something line `CDP is not enabled`.


>[!important] CDP holdtime
>By default, the CDP holdtime is **180 seconds**. If a message isn't received from a neighbor for 180 seconds, the neighbor is removed from the CDP neighbor table.

>[!note] When a device receives a CDP message, it **processes and discards** the message. It **doesn't forward the message to other devices**.

- To display global CDP information:

```toml
R1# show cdp
```

```toml
Global CDP information:
      Sending CSP packets every 60 seconds
      Sending a holdtime value of 180 seconds
      Sencing CDPv2 advertisements is  enabled
```

- To show CDP traffic statistics:

```toml
R1# show cdp traffic
```

```toml
CDP counters :
        Total packets output: 105, Input: 112
        Hdr syntax: 0, Chksum error: 0, Encaps failed: 0 
        No memory: 0, Invalid packet: 0,
        CDP version 1 advertisements output: 0, Input: 0
        CDP version 2 advertisements output: 105, Input 112
```

- To display basic information about CDP on each interface:

```toml
R1# show cdp interface
```

- To display information about CDP on a particular interface:

```toml
R1# show cdp interface G0/1
```

>[!warning]
>**The CDP protocol wasn't designed with security in mind.** Cisco recommends **disabling CDP** on any interfaces connected to untrusted devices to reduce security risks associated with information disclosure.
>>CDP can be disabled *globally* or *per interface*.

- To **enable/disable CDP globally**:

```toml
R1(config)# [no] cdp run
```

- To **enable/disable CDP on a specific interface**:

```toml
R1(config-if)# [no] cdp enable
```

- To **enable/disable CDPv2**:

```toml
R1(config)# [no] cdp advertise-v2
```

>[!note] **CDPv2** is used by default.

>[!info]
>- Devices use CDP to discover directly connected Cisco devices, such as switches, routers, and IP phones.
>- CDP is also used for PoE management, duplex mismatch detection, wrong VLAN assignment detection, and so on.

>[!important] CDP timers
> 
>- **Hello interval** — CDP messages are exchanged every **`60` seconds** (by default) — how often CDP messages are sent.
>
>- **Hold time** — **`180` seconds**, x3 the update interval (by default) — if a message isn't received from a neighbor in 180 seconds, the neighbor is removed from the CDP neighbor table.

- To show **CDP timers**:

```toml
R1# show cdp
```

- To configure the **CDP timer**:

```toml
R1(config)# cdp timer SECONDS
```

- To configure the **CDP holdtime**:

```toml
R1(config)# cdp holdtime SECONDS
```


Example configuration:

```toml
R1(config)# no cdp run               # disable CDP globally
R1(config)# cdp run                  # enable CDP globally
R1(config)# interface GigabitEthernet0/1
R1(config-if)# no cdp enable         # disable CDP on this interface
R1(config-if)# cdp enable            # enable CDP on this interface
```
## LLDP

>**LLDP (Link-Layer Discovery Protocol)** is a vendor-neutral industry standard protocol (**IEEE 802.1AB**) used by network devices to advertise their identity, capabilities, and neighbors on a LAN. 

>[!important]
>- LLDP is usually **disabled** on Cisco devices by default, so it must be enabled manually.
>- A device can run both CDP and LLDP at the same time.

- To **enable/disable LLDP globally**:

```toml
R1(config)# [no] lldp run
```

- To **enable/disable sending LLDP messages from an interface** (`tx`):

```toml
R1(config-if)# [no] lldp transmit 
```

- To **enable/disable receiving LLDP messages on an interface** (`rx`):

```toml
R1(config-if)# [no] lldp receive
```

>[!note] 
>Information gathered by LLDP can be stored in the device management information base (MIB) and queried with the Simple Network Management Protocol (SNMP), as specified in [RFC 2922](https://datatracker.ietf.org/doc/html/rfc2922).

>[!important] LLDP-enabled devices periodically send out unsolicited multicast advertisements — **LLDPDUs (LLDP Data Units)** — every **60 seconds** (by default) to the **multicast MAC address `01:80:C2:00:00:00`**.

- Devices listen for these LLDPDUs on their interfaces, storing received information about directly connected neighbors in a local **LLDP neighbor table**.

When a device receives an LLDP message, it processes and discards the message; it does not forward it to other devices.

>[!important] LLDP timers
>- **Hello interval** — **30 seconds** (by default) — how often LLDP messages are sent.
>- **Hold time** — **120 seconds**, x4 the update interval (by default) — if a message isn't received from a neighbor in 120 seconds, the neighbor is removed from the LLDP neighbor table.
>- **Reinitialization delay** — **2 seconds** (by default) — if LLDP is enabled, either globally or on an interface, this timer will delay the actual initialization of LLDP for the time set (**2 seconds** by default).

- To configure **LLDP timer**:

```toml
R1(config)# lldp timer SECONDS
```
The timer can be configured to an integer from **`5` to `65534`** seconds.

- To configure **LLDP holdtime**:

```toml
R1(config)# lldp holdtime SEcONDS
```
The holdtime can be configured to an integer from **`0` to `65535`** seconds. 


Example configuration:

```toml
R1(config)# lldp run                 # enable LLDP globally
R1(config)# interface GigabitEthernet0/1
R1(config-if)# lldp transmit         # enable LLDP transmit on interface
R1(config-if)# lldp receive          # enable LLDP receive on interface
```


- To display **information about LLDP neighbors**:

```toml
R1# show lldp neighbors
```

- To display more **detailed information about LLDP neighbors**:

```toml
R1# show lldp neighbors
```

- To display **global LLDP information**:

```toml
R1# show lldp 
```

- To display **information about a single neighboring device**:

```toml
R1# show lldp entry HOSTNAME
```

## Quiz

1. Which of the following commands show the configured CDP timers? (select two options)
	- a. `R1# show cdp`
	- b. `R1# show cdp traffic`
	- c. `R1# show cdp interface`
	- d. `R1# show cdp neighbors`

2. Which of the following commands represent the default CDP state? (select two options)
	- a. `R1(config)# no cdp run`
	- b. `R1(config)# cdp holdtime 120`
	- c. `R1(config-if)# cdp enable`
	- d. `R1(config)# cdp timer 60`

3. You issue the `show lldp entry SW1` command on R1. R1's neighbor `SW1` is a multilayer switch. What do you expect to see in the `System Capabiltiies` field of the output?
	- a. `System Capabilities: B`
	- b. `System Capabilities: B,R`
	- c.`System Capabilities: S`
	- d. `System Capabilities: S,R`

>[!note] `S` means `Switch` in CDP, but not LLDP; switches are called bridges (`B`) in LLDP.

4. Which of the following statements about LLDP are true? (select two options)
	- a. LLDP only operates on Cisco devices.
	- b. Interfaces Tx and Rx operations are enabled separately.
	- c. LLDP messages are sent every `60` seconds by default.
	- d. LLDP can be used to learn the OSPF settings of a neighboring device.
	- e. LLDP can be used to learn the VTP settings of a neighboring device.
	- f. LLDP can be used to learn the OS version of a neighboring device.


5. Boson ExSim. Which of the following commands should you issue to globally disable LLDP? (Select the best answer.)
	- a. `lldp holdtime 0`
	- b. `no lldp run`
	- c. `no lldp receive`
	- d. `no lldp transmit`

| Question | Answer     |
| -------- | ---------- |
| `1.`     | `a.`, `d.` |
| `2.`     | `c.`, `d.` |
| `3.`     | `b.`       |
| `4.`     | `b.`, `f.` |
| `5.`     | `d.`       |

