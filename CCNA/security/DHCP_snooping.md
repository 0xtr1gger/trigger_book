---
created: 2025-10-26 10:45:40
tags:
  - security
---
## DHCP snooping

>**DHCP Snooping** is a Layer 2 security feature on switches used to filter DHCP messages received on untrusted ports.

>[!important] DHCP snooping only filters DHCP messages. Non-DHCP messages aren't affected.

DHCP snooping divides ports into two groups:

- **Trusted ports**
	- Ports connected to legitimate DHCP servers or uplinks; receive DHCP server messages (`OFFER`, `ACK`).
- **Untrusted ports**
	- Default state for all ports; reject DHCP server messages.

>[!important]+ All  ports are **untrusted** by default. 

Usually,
- **Uplink** ports are configured as **trusted** ports. 
- **Downlink** ports are configured as **untrusted** ports.

![[trusted_and_untrusted_ports.svg]]

To prevent DHCP attacks, the DHCP Snooping inspects, validates, filters out, and rate-limits DHCP traffic (and DHCP traffic only) coming from **untrusted** ports.

>[!important] DHCP snooping doesn't inspect messages on trusted ports.

>[!note]+ On untrusted ports
>The network administrator doesn't have direct control over the end user devices. A malicious user could initiate a DHCP-based attack from one of their devices: that's why it's best to leave downlink ports in the default untrusted state.

- This prevents attacks such as:
	- **Rogue DHCP server**
	- **MitM (Man-in-the-Middle)** 
	- **IP address spoofing**
	- **DHCP starvation**

>[!bug]+ DHCP poisoning (MitM)
>Similar to ARP poisoning, DHCP poisoning can be used to perform a MitM (Man-in-the-Middle) attack.
>- A **spurious DHCP server** replies to client's DHCP Discover messages and assigns them IP addresses, but makes the clients use the spurious server's IP address as their **default gateway**.

>[!bug]+ DHCP starvation
>In **DHCP starvation** attack, also called **DHCP exhaustion** attack, an attacker uses spoofed MAC addresses to flood DHCP Discover messages. 
>- The target server's DHCP pool becomes full, which results in DoS (Denial of Service) to other devices, i.e., devices can't connect to the network: they won't be able to obtain an IP address from the server (clients usually accept the first DHCP Offer they receive).
>- As a result, any traffic from the clients destined to addresses outside of the local network will be sent to the attacker instead of the legitimate default gateway. 
>- The attacker can then examine/tamper with the traffic before forwarding it to the legitimate default gateway.
>
> Because the traffic reaches its destination, hosts probably won't notice it's intercepted by the attacker.

## DHCP messages

DHCP snooping differentiates between **DHCP server** messages and **DHCP client messages:

- DHCP Server messages:
	- Offer
	- Ack (acknowledgment)
	- Nak = opposite of Ack, used to decline a client's Request.

- DHCP Client messages:
	- Discover
	- Request
	- Request = used to tell the server that the client no longer needs its IP address.
	- Decline = used to decline the IP address  offered by a DHCP server.

>[!important] DHCP server messages received on untrusted ports will always be discarded with no further checks.

## DHCP snooping operation

If a DHCP message is received on a **trusted port**, forward it as normal without inspection.

If a DHCP message is received on an untrusted port, inspect it and act as follows:

- If it's a **DHCP server** message (Offer, Ack, Nak), discard it.

- If it's a **DHCP client** message, check:

	- For **Discover/Request** messages: Check if the frame source MAC address and the DHCP message's `CHADDR` field match: match = forward, mismatch = discard.
	
	- For **Release/Decline** messages: Check if the packet's source IP address and the receiving interface match the entry in the **DHCP Snooping Binding Table**: match = forward, mismatch = discard. 

- When a client successfully leases an IP address from a server, create a new entry in the **DHCP Snooping Binding Table**.

>[!important] The DHCP Snooping Binding Table maps client MAC address to their assigned IP address, lease times, VLAN, and interface.

## DHCP snooping configuration

Configure DHCP snooping:

1. Enable DHCP snooping on a switch:

```toml
SW1(config)# ip dhcp snooping
```

2. Enable DHCP snooping on a VLAN:

```toml
SW1(config)# ip dhcp snooping vlan 1
```

3. Disable information option:

```toml
SW1(config)# no ip dhcp snooping information option
```

4. Configure trusted ports:

```toml
SW1(config)# interface g0/0
SW1(config-if)# ip dhcp snooping trust
```

>[!important]+ DHCP Snooping is enabled on a **per-VLAN basis**.
>- By default, DHCP snooping is inactive on all VLANs.

>[!note]+ To configure an interface as a untrusted port:
> 
> ```toml
> SW1(config-if)# no ip dhcp snooping trust
> ```
> 

- Check the DHCP Snooping Binding table:

```toml
SW1# show ip dhcp snooping binding
```

>[!note] Other security features, such as [[dynamic_ARP_inspection]] also use information stored in the DHCP Snooping binding database.
## DHCP snooping rate-limiting

- DHCP can rate-limit DHCP messages allowed to enter an interface.

>[!important]+ If the rate of the DHCP messages crosses the configured limit, the interface is **err-disabled**.
>- The interface can then be re-enabled manually or automatically with err-disable recovery.

- Configure DHCP rate-limiting:

```toml
SW1(config)# interface range g0/1 - 3
SW1(config)# ip dhcp snooping limit rate 5 # 5 messages per second
```

- Enable err-disable recovery for DHCP rate-limiting:

```toml
SW1(config)# errdisable recovery cause dhcp-rate-limit
```

- Check err-disable recovery settings:

```toml
SW1# show errdisable recovery
```

>[!note] DHCP rate-limiting can be very useful to protect against DHCP exhaustion attacks.
## DHCP Option 82

>**Option 82**, also known as the **DHCP relay agent information option**, is a DHCP option that provides additional information about which DHCP relay agent received the client's message, on which interface, in which VLAN, etc.

- DHCP relay agents can add Option 82 to messages they forward to the remote DHCP server.
- With DHCP snooping enabled, by default Cisco switches will add Option 82 to DHCP messages they receive from clients, **even if the switch isn't acting as a DHCP relay agent**.
    
>[!important] By default, Cisco switches will drop DHCP messages with Option 82 that are received on an untrusted port. 

-  To disable Option 82:

```toml
SW1(config)# no dhcp snooping information option
```
#### DHCP snooping `show` commands

To display all VLANs that have DHCP snooping enabled:

```toml
SW1# show ip dhcp snooping
```

To display a DHCP binding table:

```toml
R1# show ip dhcp snooping binding
```

To display the DHCP snooping database agent statistics:

```toml
R1# show ip dhcp snooping database
```

## Commands that don't work with DHCP snooping

When DHCP snooping is enabled, these Cisco IOS DHCP commands are not available on the switch:

- `ip dhcp relay information check`
    - global configuration command
- `ip dhcp relay information policy`
    - global configuration command
- `ip dhcp relay information trust-all`
    - global configuration command
- `ip dhcp relay information option`
    - global configuration command
- `ip dhcp relay information trusted`
    - interface configuration command

## DHCP snooping lab


![[DHCP_lab.png]]

1. Configure `R1` as a DHCP server.
	- Exclude `192.168.1.1`-`192.168.1.9` from the pool.
	- Default gateway: `R1`.

```toml
R1(config)# ip dhcp excluded-address 192.168.1.1 192.168.1.9
R1(config)# ip dhcp pool POOL1
R1(dhcp-config)# network 192.168.1.0 255.255.255.0
R1(dhcp-config)# default-router 192.168.1.1
```

```toml
R1(config)# do show ip dhcp pool
```

```toml
Pool POOL1 :
 Utilization mark (high/low)    : 100 / 0
 Subnet size (first/next)       : 0 / 0 
 Total addresses                : 254
 Leased addresses               : 0
 Excluded addresses             : 1
 Pending event                  : none

 1 subnet is currently in the pool
 Current index        IP address range                    Leased/Excluded/Total
 192.168.1.1          192.168.1.1      - 192.168.1.254     0    / 1     / 254
```

2. Configure DHCP snooping on `SW1` and `SW2`.
	- Configure the uplink interfaces as trusted ports.

```toml
SW1(config)# ip dhcp snooping
SW1(config)# ip dhcp snooping vlan 1
SW1(config)# no ip dhcp snooping information option
SW1(config)# interface g0/2
SW1(config-if)# ip dhcp snooping trust
```

```toml
SW2(config)# ip dhcp snooping
SW2(config)# ip dhcp snooping vlan 1
SW2(config)# no ip dhcp snooping information option
SW2(config)# interface g0/1
SW2(config-if)# ip dhcp snooping trust
```

3. Use `ipconfig /renew` on `PC1` to get an IP address.
	- Does it work? Why or why not?

4. If it doesn't work, make the necessary configuration change to fix it.
## Quiz

1. Which of the following DHCP message types will always be discarded if received on a DHCP snooping untrusted interface? (select three)
    
    - a. Discover
    - b. Request
    - c. Nak
    - d. Offer
    - e. Decline
    - f. Release
    - g. Ack
2. Which of the following is not stored in the DHCP snooping binding database?
    
    - a. IP address
    - b. Interface
    - c. VLAN
    - d. default gateway
    - e. MAC address
3. Which of the following are functions of DHCP snooping? (select two)
    
    - a. Limiting the rate of DHCP messages
    - b. Filtering DHCP messages on trusted ports
    - c. Filtering DHCP messages on untrusted ports
    - d. Filtering all DHCP messages`
4. When DHCP snooping inspects a DHCP Discover message that arrives on an untrusted interface, what does it check? (select the two best answers)
    
    - a. Source MAC address
    - b. `CHADDR`
    - c. IP address
    - d. Interface
5. DHCP snooping rate-limiting is configured on a switch's `g0/1` interface. What happens if DHCP messages are received on `go/1` at a rate faster than the configured limit?
    
    - a. The messages that cross the limit will be dropped.
    - b. The interface will be disabled.
    - c. All DHCP messages on the interface will be dropped.
    - d. A warning Syslog message will be displayed.
6. Boson ExSim: Which of the following Layer 2 attacks uses the MAC address of another known host on the network in order to bypass port security measures? (Select the best answer)
    
    - a. ARP poisoning
    - b. VLAN hopping
    - c. MAC flooding
    - d. DHCP spoofing
    - e. MAC spoofing

| Question | Answer           |
| -------- | ---------------- |
| `1.`     | `c.`, `d.`, `g.` |
| `2.`     | `d.`             |
| `3.`     | `a.`, `c.`       |
| `4.`     | `a.`, `b.`       |
| `5.`     | `b.`             |
| `6.`     | `e.`             |

