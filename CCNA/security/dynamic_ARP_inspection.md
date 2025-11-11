---
created: 2025-10-26 03:53:03
tags:
  - security
---
## DAI

>**Dynamic ARP Inspection (DAI)** is a security feature on switches used to validate ARP messages on untrusted ports. 

>[!important] DAI validates only [[ARP]] messages; non-ARP messages are not affected.

>[!important] In DAI, all ports are **untrusted** by default.

- Typically, all ports connected to other network devices (switches, routers) — uplink ports — should be configured as **trusted**, while interfaces connected to end hosts — downlink ports — should remain **untrusted** (default). 

![[trusted_and_untrusted_ports.svg]]

>[!note] See [[DHCP_snooping#DHCP snooping]].


- Dynamic ARP inspection prevents attacks such as **ARP poisoning**.

>[!warning] Configuring interfaces as untrusted when they should be trusted can result in **loss of connectivity**.

>[!bug]+ ARP poisoning (MitM)
>- Similar to DHCP poisoning, ARP poisoning involves an attacker manipulating targets' ARP tables so that is sent to the attacker.
>- To do that, the attacker can send GARP messages using another device's IP address.
>- Alternatively, the attacker can send ARP reply messages to the targets' legitimate ARP request messages.
>- Other devices in the network will receive the GARP and update their ARP tables, causing them to send traffic to the attacker instead of the legitimate destination.

>[!note] See [[ARP#Gratuitous ARP#]].
## How DAI works

When DAI is enabled, the switch performs the following three activities:

- DAI inspects the **source MAC address** and **source IP address** of ARP messages received on **untrusted ports** and checks that there's a matching entry in the **DHCP Snooping Binding Table**.
	- If there's a matching entry, the ARP message is forwarded normally.
	- If there isn't a matching entry, the ARP message is discarded.

![[DHCP_binding_table.png]]

>[!important] DAI doesn't inspect messages received on **trusted** ports. They are forwarded as normal.

So, DAI operations are usually reliant on DHCP snooping, but actually there's another option:

- **ARP ACLs** can be manually configured to map IP addresses/MAC address for DAI to check.
	- This is useful for hosts that don't use DHCP (if they don't use DHCP, they won't have an entry in the DHCP snooping table, so DAI will just drop all ARP messages they try to send).
	- ARP ACLs have precedence over entries in the DHCP snooping database.

- DAI can be configured to perform more in-depth checks, but these are optional.

- Like DHCP snooping, DAI supports rate-limiting to prevent attackers from overwhelming the switch with ARP messages.
## DAI configuration

Configure DAI:

1. Enable DAI on a VLAN:

```toml
SW1(config)# ip arp inspection vlan 1
```

>[!tip]+ You can specify multiple VLANs at once:
>- Enable DAI on VLANs `11`, `15`, and `19`:
>```toml
>SW1(config)# ip arp inspection vlan 11,15,19
>```
>- Enable DAI on VLANs from `11` to `15`:
>```toml
>SW1(config)# ip arp inspection vlan 11-15
>```


>[!note] DAI needs to be enabled on each VLAN separately.

2. Configure trusted ports:

```toml
SW1(config)# int range g0/0 - 1
SW1(config-if-range)# ip arp inspection trust
```

---

- Show DAI interfaces:

```toml
SW1# show ip arp inspection interfaces
```

### DAI rate limiting

>[!important] DAI rate-limiting is enabled on untrusted ports by default with rate of **15 packets per second.** It is disabled on trusted ports by default.
>- In contrast, DHCP snooping rate limiting is disabled on all interfaces by default.

- **DHCP snooping rate-limiting:** `x` packets per second:

```toml
SW1(config-if-range)# ip dhcp snooping limit rate [packets-per-second]
```

- **DAI rate-limiting:** `x` packets per `y` seconds (burst interval):

```toml
SW1(config-if-range)# ip arp inspection limit rate 25 burst interval 2
```

>[!note] `burst interval` is optional. if not specified, the default value is 1 second.

>[!important] If the rate of incoming ARP packets exceeds the configured limit, the interface is **err-disabled state**.
>- The interface can be manually re-enabled with `shutdown`/`no shutdown`, or automatically re-enabled with **errdisable recovery**.

### DAI err-disable recovery

- Enable **err-disable recovery** for **DAI rate-limiting**:

```toml
SW1(config)# errdisable recovery cause arp-inspection
```

- Show **err-disable recovery table**:

```toml
SW1# show errdisable recovery
```

### DAI optional checks

By default, DAI checks the source MAC and IP addresses, to see if there's a matching entry in the DHCP Snooping Binding Table or not.

However, additional checks can be performed based on:
 - Destination MAC address
 - IP address
 - Source MAC address

- Configure optional DAI checks:

```toml
SW1(config)# ip arp inspection validate ?
	dst-mac  Validate detination MAC address
	ip       Validate IP addresses
	src-mac  Validate source MAC address
```

 - `dst-mac`: Destination MAC address
	 - Enables validation of the destination MAC address in the Ethernet header against the target MAC address in the ARP messages. 
	 - If there is a mismatch, DAI classifies packets as invalid and drops them.
 
 - `ip`: IP address
	 - Enables validation of the ARP messages for invalid and unexpected IP addresses. These addresses include `0.0.0.0`, `255.255.255.255`, and all IP multicast addresses. 
	 - DAI checks the sender IP address in both ARP requests and responses, and the target IP address only in ARP responses.

 - `src-mac`: Source MAC address
	 - Enables validation of the source MAC address in the Ethernet header against the sender MAC address in the ARP message for both ARP requests and responses. 
	 - If there is a mismatch, DAI classifies packets as invalid and drops them.

>[!note] These checks are performed in addition to the standard DAI checks, which looks at the sender MAC and IP addresses and compares them to the DHCP snooping binding table. 
>- If the optional checks are configured, an ARP message must pass all of the checks to be considered valid.

- Enable an optional DAI validation check:

```toml
SW1(config)# ip arp inspection validate dst-mac
```

- Enable several DAI validation checks:

```toml
SW1(config)# ip arp inspection validate dst-mac ip scr-mac
```

>[!note] You need to specify all of the validation checks you want to configure **in a single** command. The order doesn't matter.

- Check DAI validation:

```toml
SW1(config)# do show running-config | include validate
```
### DAI `show` commands

- Display DAI status, statistics, and number of dropped ARP packets:

```toml
SW1# show ip arp inspection
```

- Show detailed DAI statistics for a specific VLAN:

```toml
SW1# show ip arp inspection vlan VLAN_ID
```

- Display trust state and rate limits per interface:

```toml
SW#1 show ip arp inspection interfaces
```

- Show DHCP snooping bindings used by DAI:

```toml
SW1# show ip dhcp snoopping binding
```

- Check DAI validation:

```toml
SW1(config)# do show running-config | include validate
```


## Quiz

1. You issue the **`show vlan brief`** command on `Switch1` and receive the following partial output:

```toml
Switch1#show vlan brief  
  
VLAN Name                        Status    Ports  
---- --------------------------- --------- -------------------------------  
1    default                     active    Gi0/1, Gi0/2  
11   VLAN0011                    active    Fa0/1, Fa0/2, Fa0/3, Fa0/4  
                                           Fa0/5, Fa0/6, Fa0/7, Fa0/8  
                                           Fa0/9, Fa0/10  
12   VLAN0012                    active    Fa0/11, Fa0/12, Fa0/13, Fa0/14  
                                           Fa0/15, Fa0/16, Fa0/17, Fa0/18  
                                           Fa0/19  
14   VLAN0014                    active    Fa0/20, Fa0/21, Fa0/22, Fa0/23  
                                           Fa0/24  
<output omitted>
```

- You issue the following commands on `Switch1`:

```toml
Switch1#configure terminal  
Switch1(config)#ip arp inspection vlan 11-12,14  
Switch1(config)#interface range gigabitethernet 0/1 – 2  
Switch1(config-if-range)#switchport access vlan 11  
Switch1(config-if-range)#switchport mode access  
Switch1(config-if-range)#ip arp inspection
```

- Which of the following statements is true?  (Select the best answer.)
	- A. Only `GigabitEthernet 0/1` and `GigabitEthernet 0/2` ports are untrusted ports.
	- B. Only `GigabitEthernet 0/1` and `GigabitEthernet 0/2` are trusted ports.
	- C. All ports on the switch are untrusted ports.
	- D. All ports on the switch are trusted ports.
	- E. Only VLAN `11` ports are trusted ports.

| Question | Answer     |
| -------- | ---------- |
| `1.`     | `C.`       |
| `2.`     | `c.`       |
| `3.`     | `b.`, `d.` |
| `4.`     | `b.`, `d.` |
| `5.`     | `a.`, `c.` |

---

1. You issue the `ip arp inspection vlan 1` command on `SW1`. Which of the following statements is true about `SW1` after issuing the command?
	- a. All interfaces in VLAN 2 are untrusted.
	- b. DAI isn't fully enabled until globally with `ip arp inspection`
	- c. Only ARP messages from hosts with a static IP will be permitted.
	- d. DHCP snooping is enabled. 

2. The following commands are configured on SW1. Which of the following statements is true after the commands have been issued?
	- a. DAI validation is only enabled for IP addresses
	- b. DAI validation is only enabled for source MAC addresses 
	- c. DAI validation is only enabled for destination MAC addresses
	- d. DAI validation is enabled for all three causes

```toml
SW1(config)# ip arp inspection validate 
SW1(config)# ip arp inspection validate src-mac
SW1(config)# ip arp inspection validate dst-mac
```

3. Which of the following are true about DAI rate limiting? (select two)
	- a. It is enabled on trusted and untrusted ports by default. 
	- b. It is enabled on untrusted ports by default.
	- c. It is enabled at a rate of 10 packets per second by default.
	- d. It is enabled at a rate of 15 packets per second by default.

4. DAI inspects the sender IP and MAC addresses to determine whether an ARP packet should be forwarded or dropped. Which of the following does it check the sender IP and MAC against? (select two). 
	- a. MAC address table
	- b. DHCP snooping table
	- c. ARP table
	- d. ARP ACLs

5. Which of the following commands limit ARP messages to a maximum average of 15 per second? (select two)
	- a. `ip arp inspection limit rate 15`
	- b. `ip arp inspection limit rate 30 burst interval 3`
	- c. `ip arp inspection limit rate 45 burst interval 3`
	- d. `ip arp inspection limit rate 30 burst interval 1`

---



| Question | Answer     |
| -------- | ---------- |
| `1.`     | `a.`       |
| `2.`     | `c.`       |
| `3.`     | `b.`, `d.` |
| `4.`     | `b.`, `d.` |
| `5.`     | `a.`, `c.` |

