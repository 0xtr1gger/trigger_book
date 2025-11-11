---
created: 2025-09-24 08:55:06
tags:
  - IOS
---
## Configuring Cisco devices

>[!important] When you first configure a device, you have to connect to it via the Console Port. You can use a **[rollover cable](https://en.wikipedia.org/wiki/Rollover_cable)** for this purpose (DB9 serial connector to RJ-45 or DB9 to USB).

>[!important]+ Default console port settings on a switch:
>-  **Speed (baud): `9600` bits/second**
>	- The rate at which data is sent.
>- **Data bits: `8`**
>	- The number of bits of information used for each character of text sent to the device.
>- **Stop bits: `1`**
>	- Sent after every character to allow the receiving device to detect the end of the character.
>- **Parity: `None`** 
>	- An extra bit sent with each character for error detection.
>- **Flow control: `None`**
>	- Provides support for circumstances where a device sends data faster than the receiver can handle.
## Configuration modes


| Prompt                   | Letter | Description                                                                                                                                                         | Access                                                                                                        |
| ------------------------ | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `Router>`                | `U`    | ⬡ User EXEC mode, aka user mode.<br>⬡ Limited to basic commands, such as showing system status.                                                                     | ⬡ Accessible after logging into the router.                                                                   |
| `Router#`                | `P`    | ⬡ Privileged EXEC mode.<br>⬡ Allows viewing and changing router's configuration, and restarting the system.                                                         | ⬡ `enable` command in user mode.                                                                              |
| `Router(config)#`        | `G`    | ⬡ Global configuration mode. <br>⬡ Allows modifying the running system configuration.                                                                               | ⬡ `configure terminal` or `config t` commands in privileged mode.                                             |
| `Router(config-if)#`     | `I`    | ⬡ Interface configuration mode.<br>⬡ Allows configuring individual interfaces.                                                                                      | ⬡ `interface` followed by the interface name, e.g., `interface Ethernet0` in global configuration mode.       |
| `Router(config-subif)#`  | `S`    | ⬡ Subinterface configuration mode.<br>⬡ Allows configuring subinterfaces.                                                                                           | ⬡ `subinterface` followed by the subinterface number, e.g., `subinterface 1` in interface configuration mode. |
| `Router(config-line)#`   | `L`    | ⬡ Line configuration mode.<br>⬡ Allows configuring lines, e.g., console, VTY, AUX, etc.                                                                             | ⬡ `line` followed by the line number, e.g., `line 1` in global configuration mode.                            |
| `Router(config-banner)#` | `B`    | ⬡ Banner configuration mode.<br>⬡ Allows configuring banners, e.g., `login`, `motd`, etc.                                                                           | ⬡ `banner` followed by the banner type, e.g., `banner login` in global configuration mode.                    |
| `Router(config-router)#` | `R`    | ⬡ Routing mode. <br>⬡ A submode of Global configuration mode that allows configuring settings specific to the router, such as routing protocols and routing tables. | ⬡ `router` command in Global configuration mode.                                                              |

---

| Prompt            | Configuration mode        | Enter (from the previous) | Exit (to the previous) | Notes                                                                                                                                                    |
| ----------------- | ------------------------- | ------------------------- | ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Router>`         | User EXEC mode            | N/A                       | N/A                    | Very limited; users can't make any changes to the configuration.                                                                                         |
| `Router#`         | Privileged EXEC mode      | `enable`                  | `exit`                 | Provides complete access to view the device's configuration, restart the device, etc.<br>Can't change the configuration (except the time on the device). |
| `Router(config)#` | Global congiguration mode | `configure terminal`      | `end`                  | Provides complete access to device configuration.                                                                                                        |
## Running and startup configuration

There are two configuration files kept on each IOS device:

- **Running-config**
	- The current, active configuration file on the device. As you enter commands in the CLI, you edit the active configuration.
- **Startup-config**
	- The configuration file that will be loaded upon the restart of the device.

- To show running configuration:

```toml
R1# show running-config
```

- To save configuration:

```toml
R1# write
R1# write memory
R1# copy runnning-config startup-config
```

- To configure hostname:

```toml
R1# hostname HOSTNAME
```



| Filtering parameters             | Effect                                                                                            |
| -------------------------------- | ------------------------------------------------------------------------------------------------- |
| `section [filtering-expression]` | shows the section of the _filtering expression_                                                   |
| `include [filtering-expression]` | includes all lines of output that match the _filtering expression_ **ONLY**                       |
| `exclude [filtering-expression]` | excludes all lines of output that match the _filtering expression_                                |
| `begin [filtering-expression]`   | shows all the lines of output **beginning from** the line that matches the _filtering expression_ |

Here's an example of the usage of filtering with a `show` command:  

```toml
R1#show running-config | include line con
```

