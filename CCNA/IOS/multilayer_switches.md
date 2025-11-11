---
created: 2025-10-06 03:48:02
tags:
  - IOS
  - ethernet
---
## Multilayer switches

>**Layer 3 switches**, also known as **multilayer switches**, combine Layer 2 switching functions with routing capabilities.

- A multilayer switch is capable of both switching and routing; it is **Layer 3 aware**.
- You can assign IP address to its interfaces, like a router.
- You can create virtual interfaces for each VLAN, and assign IP address to those interfaces.
- You can configure routes on it, just like a router.
- It can be used for **inter-VLAN routing**.

>**SVIs (Switch Virtual Interfaces)** are the virtual interfaces you can assign IP address to in a multilayer switch.

- The gateway address of PCs on the network should be configured to the SVI (not the router).

- To enter SVI configuration:

```toml
SW1(config)# interface vlan10 # creates an SVI
SW1(config-if)# ip address 192.168.1.62 255.255.255.192
SW1(config-if)# no shutdown
```


>[!important] SVIs are **`shutdown`** by default, so remember to use `no shutdown`.

For inter-VLAN routing to work:

- The VLAN must exist on the switch.
- The switch must have at least one access port in the VLAN in an `up`/`up` state, **and**/**or** one trunk port that allows the VLAN that is in an `up`/`up` state.
- The SVI must not be shutdown.

>[!warning] If you create an SVI for a VLAN that doesn't exist yet, the switch **will not** automatically create the VLAN.