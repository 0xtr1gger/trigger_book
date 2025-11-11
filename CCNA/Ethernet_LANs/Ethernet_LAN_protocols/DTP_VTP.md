---
created: 2025-10-28 03:44:12
tags:
  - ethernet
---
## DTP

>**DTP (Dynamic Trunking Protocol)** is a Cisco-proprietary protocol that allows Cisco switches to dynamically determine their interface status (**access** or **trunk**) without manual configuration.

>[!important] Both VTP and DTP are Cisco-proprietary protocols. 

- DTP is enable by default on all Cisco switch interfaces.

>[!warning] 
>For security reasons, **DTP should be disabled on all switchports**:
>```toml
>SW1(config-if)# switchport nonegotiate
>```
>- Configuring an access port with `switchport mode access` also disables DTP negotiation on an interface.

### DTP switchport modes

- To change switchport trunking mode:

```toml
SW1(config-if)# switchport mode ?
  access         Set trunking mode to ACCESS unconditionally
  dot1q-tunnel   Set trunking mode to dynamically negotiate access or trunk mode
  private-vlan   Set private-vlan mode
  trunk          Set trunking mode to TRUNK unconditionally
```

- To configure DTP switchport mode:

```toml
Sw1(config-if)# switchport mode dynamic ?
  auto        Set trunking mode dynamic negotiation parameter to AUTO
  desirable   Set trunking mode dynamic negotiation parameter to DESIRABLE
```


- **Dynamic desirable**
	- A switchport in **`dynamic desitable` mode** will **actively try to form a trunk link** with other Cisco switches.
	- It will form a trunk link if connected to another switchport in the following modes:
		- `switchport mode trunk`
		- `switchport mode dynamic desirable`
		- `switchport mode dynamic auto`

- **Dynamic auto**
	- A switchport in **`dynamic auto` mode** will **not** actively try to form a trunk link with other Cisco switches, but it will form a trunk if the switch connected to it is actively trying to form a trunk.
	- If will form a trunk with a switchport in the following modes:
		- `switchport mode trunk`
		- `switchport mode dynamic desirable`
	- It's as if it were saying "If you want to form a trunk, I'll form a trunk, but I'm not going to actively try too form a trunk with you".


>[!note] Static access vs. dynamic access ports
>```toml
>SW1# show interfaces g0/0 switchport
>```
>```toml
>Name: Gi0/0
>Switchport: Enabled
>Administrative Mode: static access
>```
>- `Operation Mode` set to `static access` denotes an **access port that belongs to a single VLAN** that doesn't change (unless you configure a different VLAN).
>- There're also `dynamic access` ports, in which a server automatically assigns the VLAN depending on the MAC address of the connected device.
>
>**This is out of the scope of the CCNA.**

|  Administrative <br>mode  |                   Trunk                   |           Dynamic <br>Desirable           |                  Access                   |             Dynamic <br>Auto              |
| :-----------------------: | :---------------------------------------: | :---------------------------------------: | :---------------------------------------: | :---------------------------------------: |
|         **Trunk**         | <span style="color:#596BF4">Trunk</span>  | <span style="color:#596BF4">Trunk</span>  | <span style="color:rgb(192,0,0)">✘</span> | <span style="color:#596BF4">Trunk</span>  |
| **Dynamic <br>Desirable** | <span style="color:#596BF4">Trunk</span>  | <span style="color:#596BF4">Trunk</span>  | <span style="color:#7BC1DF">Access</span> | <span style="color:#596BF4">Trunk</span>  |
|        **Access**         | <span style="color:rgb(192,0,0)">✘</span> | <span style="color:#7BC1DF">Access</span> | <span style="color:#7BC1DF">Access</span> | <span style="color:#7BC1DF">Access</span> |
|   **Dynamic <br>Auto**    | <span style="color:#596BF4">Trunk</span>  | <span style="color:#596BF4">Trunk</span>  | <span style="color:#7BC1DF">Access</span> | <span style="color:#7BC1DF">Access</span> |

>[!note] Default administrative mode
>- On older switches, `switchport mode dynamic desirable` is the default administrative mode.
>- On newer switches, `switchport mode dynamic auto` is the default administrative mode.

- To disable DTP negotiation on an interface:

```toml
SW1(config-if)# switchport nonegotiate
```

- Configuring an access port with `switchport mode access` also disables DTP negotiation on an interface.

### Encapsulation

Switches that support both **802.1Q** and **ISL** trunk encapsulations can use DTP to negotiate the encapsulation they will use.

- This negotiation is enabled by default, as the default trunk encapsulation mode is: `switchport trunk encapsulation negotiate`.

**ISL** is favored over **802.1Q**, so if both switches support ISL, it will be used.

- DTP frames are sent in VLAN `1` when using **ISL**, or in the native VLAN when using **802.1Q** (the default native VLAN is VLAN `1`, however).

### DTP configuration example

Basic DTP configuration:

```toml
# view current DTP status
Switch# show dtp interface fastethernet 0/1

# configure dynamic auto (default on most interfaces)
Switch(config)# interface fastethernet 0/1
Switch(config-if)# switchport mode dynamic auto
Switch(config-if)# exit

# configure dynamic desirable
Switch(config)# interface fastethernet 0/1
Switch(config-if)# switchport mode dynamic desirable
Switch(config-if)# exit

# configure trunk with DTP
Switch(config)# interface fastethernet 0/1
Switch(config-if)# switchport mode trunk
Switch(config-if)# exit

# configure access port
Switch(config)# interface fastethernet 0/1
Switch(config-if)# switchport mode access
Switch(config-if)# exit

# disable DTP (security best practice)
Switch(config)# interface fastethernet 0/1
Switch(config-if)# switchport mode trunk
Switch(config-if)# switchport nonegotiate
Switch(config-if)# exit
```

DTP verification commands:

```toml
# show DTP information for specific interface
Switch# show dtp interface fastethernet 0/1

# show DTP information for all interfaces
Switch# show dtp

# show interface switchport status
Switch# show interfaces fastethernet 0/1 switchport

# show trunk interfaces
Switch# show interfaces trunk
```


Sample DTP output analysis:

```toml
SW# show dtp interface fastethernet 0/1
DTP information for FastEthernet0/1:
  TOS/TAS/TNS:                              ACCESS/AUTO/ACCESS
  TOT/TAT/TNT:                              802.1Q/802.1Q/802.1Q
  Neighbor address 1:                       0CD904D23C01
  Neighbor address 2:                       000000000000
  Hello timer expiration (sec/state):       7/RUNNING
  Access timer expiration (sec/state):      never/STOPPED
  Negotiation timer expiration (sec/state): never/STOPPED
  Multidrop timer expiration (sec/state):   never/STOPPED
  FSM state:                                S2:ACCESS
  # times multi & trunk                     0
  Enabled:                                  yes
  In STP:                                   forwarding
```
## VTP

>**VTP (VLAN Trunking Protocol)** is a Cisco-proprietary protocol that allows you to configure VLANs on a central VTP server switch, and other switches (VTP clients) will synchronize their VLAN database to the server.

- VTP is designed for large networks with many VLANs, so that you don't have to configure each VLAN on every switch.
- However, VTP is rarely used, and it's recommended that you don't use it.
- There are three VTP modes: **server**, **client**, and **transparent**.

- To view the current state of VTP on the switch:

```toml
SW1# show vtp status
```

>[!note] VTP versions
>- There are three versions of VTP: 1, 2, and 3. Most modern Cisco switches support all three, but older switches might only support 1 and 2.
>- VTPv2 is not much different from VTPv1. The major difference is that VTPv2 introduces support for Token Ring VLANs. If you don't use Token Ring, there's no point to enable VTPv2.
>- Changing the VTP version increases the revision number.
>
>To change the VTP version:
> 
> ```toml
> SW(config)# vtp version 2
> ```

### VTP modes

There are three VTP modes a switch can operate in:

- **Server mode**
	- Can add/modify/delete VLANs.
	- Store the VLAN database in non-volatile RAM (NVRAM); this means the VLAN database is saved even if the switch is turned off or reloaded.
	- Will increase the **revision number** every time a VLAN is added/modified/deleted.
	- Will advertise the latest version of the VLAN database on trunk interfaces, and the VTP clients will synchronize their VLAN databases to it.
	- **VTP servers also function as VTP clients. This means a VTP server will synchronize to another VTP server with a higher revision number.**

>[!important]+ The **revision number** is what VTP uses to determine the newest version of the VLAN database, the version all switches will synchronize to.

- **Client mode**
	- Can't add/modify/delete VLANs.
	  Don't store the VLAN database in NVRAM (in VTPv3, they do).
	- Will synchronize their VLAN database to the server with the highest revision number in their VTP domain.
	- Will advertise their VLAN database and forward VTP advertisements to other clients over their trunk ports.

- **Transparent mode**
	- Does not participate in the VTP domain (doesn't synchronize its VLAN database).
	- Maintains its own VLAN database in NVRAM. It can add/modify/delete VLANs, but they won't be advertised to other switches.
	- Will forward VTP advertisements in the same domain.

- **Off mode** (VTP version 3)
	- VTP is completely disabled.
	- Does not process or forward VTP advertisements.
	- Functions similar to transparent but doesn't forward VTP messages.

- To change the VTP mode on a switch:

```toml
SW1(config)# vtp mode client
```

| Descriptor                           | Server | Client | Transparent |
| ------------------------------------ | :----: | :----: | :---------: |
| Creates, modifies, and deletes VLANs |   ✔︎   |        |     ✔︎      |
| Synchronizes VTP information         |   ✔︎   |   ✔︎   |             |
| Originates VTP advertisements        |   ✔︎   |   ✔︎   |             |
| Forwards VTP advertisements          |   ✔︎   |   ✔︎   |     ✔︎      |
| Stores VLAN information in NVRAM     |   ✔︎   |        |     ✔︎      |

| VTP Server mode                | VTP Client mode                | VTP Transparent mode             |
| ------------------------------ | ------------------------------ | -------------------------------- |
| Can add/modify/delete VLANs    |                                | Can add/modify/delete VLANs      |
| Stores VLAN database in NVRAM  |                                | Stores VLAN information in NVRAM |
| Synchronizes with VTP servers  | Synchronizes with VTP servers  |                                  |
| Forwards VTP advertisements    | Forwards VTP advertisements    | Forwards VTP advertisements      |
| Advertises local VLAN database | Advertises local VLAN database |                                  |

>[!important] Cisco switches operate in **VTP server mode** by default.

>[!important] VTP servers also function as VTP clients. This means a VTP server will synchronize to another VTP server with a higher revision number.

>[!important] VTPv1 and VTPv3 don't support the extended VLAN range (`1006`-`4096`). Only VTPv3 supports them.

### VTP domain

>A **VTP domain**is a group of switches in a LAN that share the same VTP domain name.

By default, switches don't have a VTP domain name; in this state, VTP is not active.

- To change VTP domain:

```toml
SW1(config)# vtp domain VTP_DOMAIN_NAME
```

>[!important] If you configure a VTP domain name on one switch, it will send VTP messages to other switches, and all switches without a VTP domain name will adopt a new one.

>[!danger]+ One danger of VTP
> If you connect an old switch with a higher revision number to your network (and the VTP domain name matches), all switches in the domain will synchronize their VLAN databases to that switch.

>[!important] Changing the VTP domain to an unused domain will reset the revision number to `0`.

>[!important] Changing the VTP mode to transparent will also reset the revision number to `0`.

