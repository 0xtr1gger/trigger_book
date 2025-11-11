---
created: 2025-10-06 06:52:50
tags:
  - stp
  - LAN_protocols
---
## Spanning Tree Toolkit

The STP Optional Features, sometimes called the Spanning Tree Toolkit, are features that can be enabled to improve the functionality of a spanning tree protocol in some ways.

Common STP Features:

- **PortFast** 
	- Allows switch ports connect to end host to immediately enter the STP Forwarding state, bypassing Listening and Learning. 

- **BPDU Guard**
	- Automatically disables a port if it receives a BPDU, protecting the STP topology by preventing unauthorized devices from becoming a part of the network.

- **BPDU Filter**
	- Stops a port from sending BPDUs or processing received BPDUs.

- **Root Guard**
	- Prevents a port from becoming a Root Port by disabling it if superior BPDUs are received, thereby enforcing current Root Bridge.

- **Loop Guard**
	- Protects the network from loops by disabling a port if it unexpectedly stops receiving BPDUs, ensuring it doesn't mistakenly enter the Forwarding state.
## PortFast

In STP, all ports must first go through Listening and Learning states before they start forwarding traffic, including the ports connected to end hosts.

- When an end host connects to a switch port, the port becomes `up`/`up`, but can't sent or receive traffic yet.
	- It is a **Designated port**, so it will take **30 seconds** before it enters the **Forwarding** state: **15 seconds** in the **Listening** state + **15 seconds** in the **Learning** state.

There is no risk of forming a loop with an end host. Why wait 30 seconds? PortFast solves this problem.

>**PortFast** allows a port to immediately move to the Forwarding state, bypassing Listening and Learning states. 

>[!warning] PortFast must be enabled only on ports connected to end hosts.
>If PortFast is enabled on a port connected to another switch, it could cause a Layer 2 loop. 

- To enabled PortFast on an access port:

```toml
SW1(config)# interface g0/2
SW1(config-if)# spanning-tree portfast
```

>[!important] PortFast will only take effect on access ports. 

- To enable PortFast on all access ports by default:

```toml
SW1(config)# spanning-tree portfast default
```

>[!note] Trunk ports are not affected by the `spanning-tree portfast default` command.

>[!warning] PortFast can cause loops if a switch is connected to a port previously connected to an end host.

- To disable PortFast on an access port:

```toml
SW1(config)# interface g0/2
SW1(config-if)# spanning-tree portfast disable
```

- To display STP information about a port:

```toml
SW1# show spanning-tree interface g0/2 detail 
```

>[!important] In modern Cisco switches, if you use the commands covered above, the device will automatically add the **`edge`** keyword to the configuration:
>```toml
>SW1(config-if)# spanning-tree portfast
># in the running-config: spanning-tree portfast edge
>``` 

>[!note]+ In some cases, you might want to enable PortFast on a trunk port:
>- A port connected to a virtualization server with VMs in different VLANs.
>- A port connected to a router via ROAS.
>```toml
>SW1(config-if)# spanning-tree portfast trunk
>```
## BPDU Guard

>[!note]+ Why BPDU guard?
> - PortFast makes a port start in the Forwarding state when it's connected, but it doesn't disable STP on the port. The port will continue to send BPDUs every 2 seconds.
> - Because end hosts don't run STP or send BPDUs, a PortFast-enabled port shouldn't receive BPDUs.  
> 
> But what if it doesn?
> 
> - If a PortFast-enabled port receives an STP BPDU, it will revert to acting like a regular STP port (without PortFast).

>**BPDU Guard** protects the network from unauthorized switches being connected to ports intended for end hosts. 

- BPDU guard can be configured separately from PortFast, but these features are usually used together — they both enhance functionality on ports intended for end hosts.

>[!important] A BPDU-enabled port continues to send BPDUs, but if it *receives* a BPDU, it enters the **error-disabled** state. This effectively disables the port.

>It automatically disables a port if it receives a BPDU, protecting the STP topology by preventing unauthorized devices from becoming a part of the network.

- To enable BPDU guard on an access port:

```toml
SW1(config)# interface g0/1
SW1(config-if)# spanning-tree bpduguard enable
```

- To display STP port configuration:

```toml
SW1(config-if)# do show spanning-tree interface g0/1 detail
```

- To enable BPDU Guard on all PortFast ports by default:

```toml
SW1(config)# spanning-tree portfast bpduguard default
```

>[!important] When enabled by default, BPDU Guard is activated on all PortFast-enabled ports (not necessarily all access ports).

- To disable BPDU guard on a specific port:

```toml
SW1(config-if)# spanning-tree bpduguard disable 
```

>[!important] To re-enable an err-disabled port, first solve the underlying issue.
>If you re-enable the port without fixing the issue, it will just be err-disabled again.

- To manually re-enable an err-disabled port, use `shutdown` and `no shutdown`:

```toml
SW1(config-if)# shutdown
SW1(config-if)# no shutdown
```

- To automatically re-enable an err-disabled port, configure err-disable recovery:

```toml
SW1# errdisable recovery cause bpduguard
```

```toml
SW1# show errdisable recovery
```

>[!note] The default recovery timer is 300 seconds (5 minutes).

- To configure err-disable recovery timer:

```toml
SW1(config)# errdisable recovery interval SECONDS
```

## BPDU Filter

>[!note]+ Why BPDU filter?
>- A switch port connected to an end host continues sending BPDUs every 2 seconds **regardless of whether PortFast and/or BPDU Guard are enabled**. 
>- If the port doesn't connect to a switch, sending BPDUs is unnecessary and undesirable for a couple of reasons:
>	1. Sending BPDUs uses some bandwidth and processing power on the switch (although it's minimal).
>	2. BPDUs contain information about the LAN's STP topology: sending this information to users can be a security concern.
>
>**BPDU Filter** solves this by preventing a port from sending BPDUs.

>**BPDU Filter** prevents a port from sending BPDUs.

- To enable BPDU Filter on a specific port:

```toml
SW1(config)# interface g0/1
SW1(config-if)# spanning-tree bpdufilter enable
```


>[!note]+
>- The port will not send BPDUs.
>- The port will ignore any BPDUs it receives.
>
>In effect, this disables STP on the port (use with caution).
>
>>[!note] Unlike BPDU Guard, it doesn't disable the port if it receives a BPDU.

- To globally enable BPDU Filter by default:

```toml
SW1(config)# spanning-tree portfast bpdufilter default
```

>[!important] BPDU Filter will be activated on all PortFast-enabled ports.

- To disable BPDU Filter on a specific port:

```toml
SW1(config-if)# spanning-tree bpdufilter disable
```

>[!note]+ 
>- The port will not send BPDUs.
>- If the port receives a BPDU, PortFast and BPDU Filter are disabled, and the port operates a as a normal STP port.

>[!note] Recommendations:
>- Enable PortFast and BPDU Guard however you prefer (per-port or by default).
>- Only enable BPDU Filter by default (global config mode; unless you have a very good reason to enable it per-port).

>[!note]+ BPDU Guard and BPDU Filter can be enabled on the same port at the same time:
>- If BPDU Filter is enabled in global config mode and the port receives a BPDU:
>	1. BPDU Filter will be disabled.
>	2. BPDU Guard will be triggered (and err-disable the interface).
>- If BPDU Filter is enabled in the interface config mode and the port receives a BPDU:
>	- The BPDU will be ignored.
## Root Guard

>**Root guard** is used to protect STP topology by preventing switches from accepting **superior BPDUs** outside of your control. This prevents newly introduced switches from being elected as the new root switch.

- Root guard allows administrators to maintain control over which switch is the root.

- To enable Root Guard on an interface:

```toml
SW2(config-if)# spanning-tree guard root
```

>[!note] Root Guard can only be configured from an interface configuration mode, but not globally.

- If a Root Guard-enabled port receives a BPDU, it will enter the **Broken** (*Root Inconsistent*) state, effectively disabling it.
- The port will not be able to forward data frames and will discard any frames it receives.

>[!important] To re-enable a port disabled by Root Guard, you must solve the issue that disabled the port.
>- The disabled port must stop receiving superior BPDUs.

>[!important] Once the superior BPDUs received on Root Guard-enabled ports age out (a BPDU's Max Age is 20 seconds by default), the ports will automatically be re-enabled.

>[!warning] If Root Guard is enabled on a loop guard–enabled port, Loop Guard will be automatically disabled.
## Loop Guard

- When a **Loop Guard**-enabled port's MaxAge timer counts down to `0`, it doesn't become a Designated port and start transitioning to Forwarding.
	- Instead, it enters the **Broken** (*Loop Inconsistent*) state, effectively disabling it (just like the **Broken** *Root Inconsistent* state). In both cases, the port remains `up`/`up`.

- To enable Loop Guard on a specific interface:

```toml
SW1(config-if)# spanning-tree guard loop
```

- To globally enable Loop Guard by default:

```toml
SW1(config)# spanning-tree loopguard default
```

- To disable Loop Guard on a specific interface:

```toml
SW1(config-if)# spanning-tree guard none
```

>[!important] Loop Guard should be enabled on Root and Non-Designated ports (ports that are supposed to received BPDUs).

>[!warning] Loop Guard and Root Guard are mutually exclusive.
>- Root Guard is meant to prevent Designated ports from becoming Root ports.
>- Loop Guard is meant to prevent Non-Designated or Root ports from becoming Designated ports.

>[!warning] If Loop Guard is configured on a port (`spanning-tree guard loop`) and you then configure Root Guard (`spanning-tree guard root`), Loop Guard will be disabled on the port (and vice versa).