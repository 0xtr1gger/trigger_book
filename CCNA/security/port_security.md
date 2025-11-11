---
created: 2025-10-24 05:39:48
tags:
  - security
---
## Port security

>**Port security** is a security feature on Cisco switches that allows you to control which source MAC addresses are allowed to enter the switchport.

>[!important]+ Unauthorized source MAC addresses and actions
> - If an unauthorized source MAC address enters the port, an **action** will be taken.
> - The **default action** is to place the interface in an **err-disabled state**: traffic will no longer be sent or received by that interface unless reset.

>[!note] Port security rules are **configured on per-interface** basis.

>[!important]+ Allowed MAC addresses 
>When you enable port security on an interface with the default settings, **one MAC address** is allowed.

- You can configure the allowed MAC address manually.
- If you don't configure it manually, the switch will allow the **first source MAC address that enters the interface**.
- You can change the maximum number of MAC addresses allowed.
- A combination of manually configured MAC addresses and dynamically learned addresses is possible.

>[!note] Why port security?
> - Port security allows network administrators to control which devices are allowed to access the network.
> - However, port security isn't a perfect solution against MAC address spoofing.
> - Rather than manually specifying the MAC addresses allowed on each port, port security's ability to limit the number of MAC addresses allows on an interface is more useful. Limiting the number of MAC addresses on an interface can protect against such attacks as DHCP starvation. 

Port security protects against the following attacks:
- MAC address table flooding
- MAC address spoofing
- ARP spoofing
- DHCP spoofing
- DHCP starvation

## Configuration

### Enabling port security

- **Enable port security** on an interface:

```toml
SW1(config)# interface g0/1
SW1(config-if)# switchport port-security
```

>[!warning] By default, switchports have an administrative mode of **`dynamic auto`**. Port security can not be configured on dynamic ports.

>[!warning] Port security can be enabled on access ports or trunk ports, but they must be statically configured as access or trunk.

>[!important] Port security can be enabled on access ports or trunk ports, but they must be **statically configured** as access or trunk.
>- `switchport mode access` = OK
>- `switchport mode trunk` = OK
>- ~~`switchport mode dynamic auto`~~
>- ~~`switchport mode dynamic desirable`~~

- Show port security:

```toml
SW1# do show port-security
```

- For example:

```toml
SW1(config)# int range f0/1 - 3
SW1(config-if-range)# switchport port-security
Command rejected: FastEthernet0/1 is a dynamic port.
Command rejected: FastEthernet0/2 is a dynamic port.
Command rejected: FastEthernet0/3 is a dynamic port.
SW1(config-if-range)# switchport mode access
SW1(config-if-range)# switchport port-security
```

```toml
SW1(config-if-range)# do show port-security
Secure Port MaxSecureAddr CurrentAddr SecurityViolation Security Action
               (Count)       (Count)        (Count)
--------------------------------------------------------------------
        Fa0/1        1          0                 0         Shutdown
        Fa0/2        1          0                 0         Shutdown
        Fa0/3        1          0                 0         Shutdown
----------------------------------------------------------------------
```
### `show` commands

- **Show port security status** of an interface:

```toml
SW1# show port-security interface g0/1
```

```toml
Port Security               : Enabled
Port Status                 : Secure-up # port security is enabled
Violation Mode              : Shutdown
Aging Time                  : 0 mins # addresses will never age out
Aging Type                  : Absolute
SecureStatic Address Aging  : Disabled
Maximum MAC Addresses       : 1
Total MAC Addresses         : 0
Sticky MAC Addresses        : 0 
Last Source Address:Vlan    : 0000.0000.0000:0 # means no MAC addresses
Security Violation Count    : 0 
```

- Show which interfaces have port security enabled and other details:

```toml
SW1# show port-security interface g0/1
```
### Manually configuring MAC addresses

- To manually configure authorized MAC address on an interface:

```toml
SW1(config-if)# switchport port-security mac-address <MAC_address>
```

```toml
SW1(config-if)# switchport port-security mac-address 000a.000a.000a
```
## Violation modes

There are three different violation modes that determine what the switch will do if an unauthorized frame enters an interface configured with port security:

- **Shutdown** (default)
	- Effectively **shuts down the port** by placing it in an **err-disabled state**.
	- Generates a Syslog and/or SNMP message when the interface is disabled.
	- The violation counter is set to `1` when the interface is disabled, although it will be reset to `0` when the interface is re-enabled.

- **Restrict**
	- The switch **discards traffic from unauthorized MAC addresses**.
	- The interface is **not disabled**.
	- Generates a Syslog and/or SNMP message each time an unauthorized MAC is detected.
	- The violation counter is incremented by `1` for each unauthorized frame.

- **Protect**
	- The switch **silently discards traffic from unauthorized MAC addresses**.
	- The interface is **not disabled**.
	- Does **not** generate Syslog/SNMP messages for unauthorized traffic.
	- Does **not** increment the violation counter.

- To change the violation mode on an interface:

```toml
SW1(config-if)# switchport port-security violation restrict
```
### Err-disable recovery

- To **manually re-enable** an interface once it has been err-disabled:
	1. **Disconnect the unauthorized device**
	2. Run `shutdown` and then `no shutdown` on the interface:

```toml
SW1(config)# interface g0/1
SW1(config-if)# shutdown
SW1(config-if)# no shutdown  
```

>[!important] You can configure an err-disabled interface to be automatically re-enabled after a certain period of time. This is called **err-disable recovery**.

There are many reasons why an interface can be put in the err-disabled state. To list these reasons:

```toml
SW1# show errdisable recovery
```

>[!important] By default, err-disable recovery is disabled for all reasons.

- To configure err-disable recovery for port security reason:

```toml
SW1(config)# errdisable recovery cause psecure-violation
```

>[!note] The reason name is displayed in the output of the `show errdisable recovery` command.

>[!important] If err-disable recovery has been enabled for the cause of the interface's disablement, all err-disabled interfaces will be re-enabled every 5 minutes (by default).

- To configure err-disable recovery timer:

```toml
SW1(config)# errdisable recovery interval 180
```

>[!warning] Err-disable recovery is useless if you don't remove the device that caused the interface to enter the err-disabled state.

>[!important] If the authorized MAC addresses are dynamically learned on the interface, re-enabling the interface clears previously learned addresses.

## Aging

By default, security MAC addresses will not 'age out' (`Aging Time: 0 mins`)

- To configure aging time on an interface:

```toml
SW1(config-if)# switchport port-security aging time <minutes>
```

>[!important] The default aging type is **Absolute**.

- **Absolute**
	- After a secure MAC address is learned, the aging timer starts and the MAC address is removed after the timer expires, even if the switch continues receiving frames from that source MAC address.
- **Inactivity**
	- After the security MAC address is learned, the aging timer starts but is reset every time a frame from that source MAC address is received on the interface.

>[!important] Secure **Static MAC aging** (addresses configured with `switchport port-security mac-address x.x.x`) is disabled by default.

Authorized MAC addresses can be assigned in two ways: 

- **Statically configured**
	- Configured manually by a network administrator.
	- `switchport port-security mac-address [MAC_ADDRESS]` 

- **Dynamically learned**
	- Addresses will be learned dynamically based on incoming traffic, up to the maximum number of MAC addresses (`1` by default). 
	- This means that `n` source MAC addresses that first arrived on the interface after configured will become *authorized*, and others - unauthorized.
	- If MAC address are not configured manually, the switch will only allow the first source MAC address that enters the interface (`n = 0`).
	- By default, when more than the maximum number of allowable devices attempt to access the network through the same interface, the switch will shut down the interface, bu no other interfaces will be affected.
## Sticky secure MAC addresses

>[!important] Sticky secure MAC addresses will **never** age out.

- Sticky secure MAC address learning can be enabled with the following command:

```toml
SW1(config-if)# switchport port-security mac-address sticky
```

- When enabled, dynamically-learned secure MAC addresses will be added to the running config like this:

```toml
SW1(config-if)# switchport port-security mac-address sticky MAC_ADDRESS
```

## MAC address table

- Secure MAC addresses will be added to the MAC address table just like any other MAC address.
	- Sticky and Static secure MAC addresses will have the type `STATIC`.
	- Dynamically-learned secure MAC addresses will have the type `DYNAMIC`.

- View all secure MAC addresses:


```toml
SW1# show mac address-table secure
```

```toml
         Mac Address Table
-----------------------------------------
Vlan   Mac Address        Type      Ports
----   -----------        ------    -----
   1   000a.000a.000a     STATIC    Gi0/1
Total Mac Addresses for this criterion: 1
```

## Configuration

### Show commands

- To display unauthorized MAC addresses:

```toml
SW1(config-if)# show mac-address-table
```

- To see that a switch has searched a MAC address on a port with port security enabled:

```toml
SW1# show port-security interface fastEthernet0/1
```

Example output:

```toml
Port Security : Enabled
Port Status : Secure-up
Violation Mode : Shutdown
Aging Time : 0 mins
Aging Type : Absolute
SecureStatic Address Aging : Disabled
Maximum MAC Addresses : 1
Total MAC Addresses : 1
Configured MAC Addresses : 0
Sticky MAC Addresses : 1
Last Source Address:Vlan : 000A.4188.D0C3:1
Security Violation Count : 0
```
### Configuring port security

>**Configure port security on an interface**

1. Define the interface as an **access port**:

```toml
SW1(config-if)# switchport mode access
```

2. Enable port security:

```toml
SW(config-if)# switchport port-security
```

>**Define static allowed MAC addresses**

3. Define allowed MAC addresses:

```toml
SW(config-if)# switchport port-security mac-address MAC_ADDRESS
```

>**Enable dynamic MAC address learning (sticky)**

4. **Enable dynamic MAC address learning:**

```toml
SW(config-if)# switchport port-security mac-adderss sticky
```

5. *(Optional)* **Change the maximum number of authorized MAC addresses** that can be dynamically learned from incoming traffic:

```toml
SW1(config-if)# switchport port-security maximum 2
```

>By default, the maximum number of allowed MAC addresses is *one*.

>**Define action**

6. *(Optional)* **Define what action** the switch will take when receiving a frame from an unauthorized device:

```toml
SW(config-if)# port security violation {protect | restrict | shutdown}
```

- To clear all dynamically learned secure MAC addresses:

```toml
SW1(config-if)# clear port-security dynamic
```

- Te `switchport port-security mac-address sticky` command converts dynamically learned MAC addresses to sticky MAC addresses, which are stored in the running configuration. 
	- To ensure that the sticky MAC addresses are not lost during a reboot, the `write memory` or `copy runnin-config startup-config` commands are used.  

![[command_review_port_security.png]]
## Quiz

1. Boson ExSim. Which of the following commands should you issue on a switch port so that no more than two devices can send traffic into the port? (Select the best answer.)
	- a. `switchport port-security`
	- b. `switchport port-security mac-address 2`
	- c. `switchport port-security mac-address sticky`
	- d. `switchport port-security maximum 2`
	- e. `switchport port-security 2`

| Question | Answer |
| -------- | ------ |
| `1.`     | `d.`   |
| `2.`     |        |
| `3.`     |        |
| `4.`     |        |
| `5.`     |        |
| `6.`     |        |

## Lab

- `SW1`:

```toml
SW1(config)# int range f0/1 - 3
SW1(config-if-range)# switchport port-security
Command rejected: FastEthernet0/1 is a dynamic port.
Command rejected: FastEthernet0/2 is a dynamic port.
Command rejected: FastEthernet0/3 is a dynamic port.
SW1(config-if-range)# switchport mode access
SW1(config-if-range)# switchport port-security
SW1(config-if-range)# switchport port-security violation shutdown
SW1(config-if-range)# switchport port-security maximum 1
SW1(config-if-range)# no switchport port-security mac-address sticky
SW1(config-if-range)# switchport port-security aging time 60
```

```toml
SW1(config-if-range)# do show port-security
Secure Port MaxSecureAddr CurrentAddr SecurityViolation Security Action
               (Count)       (Count)        (Count)
--------------------------------------------------------------------
        Fa0/1        1          0                 0         Shutdown
        Fa0/2        1          0                 0         Shutdown
        Fa0/3        1          0                 0         Shutdown
----------------------------------------------------------------------
```

```toml
SW1(config-if-range)# do show port-security int f0/1
Port Security              : Enabled
Port Status                : Secure-up
Violation Mode             : Shutdown
Aging Time                 : 60 mins
Aging Type                 : Absolute
SecureStatic Address Aging : Disabled
Maximum MAC Addresses      : 1
Total MAC Addresses        : 0
Configured MAC Addresses   : 0
Sticky MAC Addresses       : 0
Last Source Address:Vlan   : 0000.0000.0000:0
Security Violation Count   : 0

SW1(config-if-range)# do show port-security int f0/2
Port Security              : Enabled
Port Status                : Secure-up
Violation Mode             : Shutdown
Aging Time                 : 60 mins
Aging Type                 : Absolute
SecureStatic Address Aging : Disabled
Maximum MAC Addresses      : 1
Total MAC Addresses        : 0
Configured MAC Addresses   : 0
Sticky MAC Addresses       : 0
Last Source Address:Vlan   : 0000.0000.0000:0
Security Violation Count   : 0

SW1(config-if-range)# do show port-security int f0/3
Port Security              : Enabled
Port Status                : Secure-up
Violation Mode             : Shutdown
Aging Time                 : 60 mins
Aging Type                 : Absolute
SecureStatic Address Aging : Disabled
Maximum MAC Addresses      : 1
Total MAC Addresses        : 0
Configured MAC Addresses   : 0
Sticky MAC Addresses       : 0
Last Source Address:Vlan   : 0000.0000.0000:0
Security Violation Count   : 0
```

- `SW2`:

```toml
SW2(config)# int g0/1
SW2(config-if)# switchport port-security
Command rejected: GigabitEthernet0/1 is a dynamic port.
SW2(config-if)# switchport mode access
SW2(config-if)# switchport port-security
SW2(config-if)# switchport port-security violation restrict
SW2(config-if)# switchport port-security maximum 4
SW2(config-if)# switchport port-security mac-address sticky
```

```toml
SW2(config-if)# do show port-security
Secure Port MaxSecureAddr CurrentAddr SecurityViolation Security Action
               (Count)       (Count)        (Count)
--------------------------------------------------------------------
       Gig0/1        4          1                 0         Restrict
----------------------------------------------------------------------
```

```toml
SW2(config-if)# do show port-security int g0/1
Port Security              : Enabled
Port Status                : Secure-up
Violation Mode             : Restrict
Aging Time                 : 0 mins
Aging Type                 : Absolute
SecureStatic Address Aging : Disabled
Maximum MAC Addresses      : 4
Total MAC Addresses        : 1
Configured MAC Addresses   : 0
Sticky MAC Addresses       : 0
Last Source Address:Vlan   : 0060.471C.1D19:1
Security Violation Count   : 0
```