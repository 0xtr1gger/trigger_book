---
created: 2025-10-27 03:48:20
tags:
  - protocols
---

## Syslog

>**Syslog** is an industry standard protocol for message logging. 

>[!important] The purpose of Syslog is to collect, store, and forward these log messages to a centralized location for monitoring, analysis, and auditing.

- Syslog can be used to log events such as changes in interface status (`up` ⟺ `down`), system restarts, etc.
- Messages can be displayed in the CLI, saved in the device's RAM, or sent to an external Syslog server for analysis.

>[!note]
> There are several ways to view Syslog messages:
> 
> - **CLI**
> 	- Syslog messages are displayed in the CLI when connected to the device via the console port. By default, all messages (severity level 0 to 7) are displayed.
> 
> - **VTY lines**
> 	- Syslog messages are displayed in the CLI when connected to the device via SSH (or Telnet). Disabled by default.
> 
> - **External Syslog server**
> 	- An external Syslog server can be configured to collect logs from devices in the network. Syslog servers listen on UDP port 514.
> 
> - **Buffer** (the device's RAM)
> 	- Syslog messages are saved to the device's RAM.
> 	- Messages can be viewed with the `show logging` command. 
## Syslog message format

Here's how a standard Syslog message looks like:

```toml
seq: timestamp: %facility-severity-MNEMONIC: description
```

For example:

```toml
*Feb 11 03:02:55.304: %LINK-3-UPDOWN: Interface GigabitEthernet0/0, changed state to up
```

| Field         | Description                                                               | Example                                             |
| ------------- | ------------------------------------------------------------------------- | --------------------------------------------------- |
| `seq`         | A sequence number indicating the order/sequence of the message.           | N/A                                                 |
| `timestamp`   | A timestamp indicating the time the message was generated.<br>            | `*Feb 11 03:02:55.304`                              |
| `facility`    | A value that indicates which process on the device generated the message. | `LINK`                                              |
| `severity`    | A number that indicates the severity of the logged event.                 | `3`                                                 |
| `MNEMONIC`    | A short code for the message that indicates what happened.                | `UPDOWN`                                            |
| `description` | Detailed information about the event being reported.                      | `Interface GigabitEthernet0/0, changed state to up` |

>[!note] Depending on the device's configuration, `seq` and `timestamp` fields may or may not be displayed. 

### Syslog severity levels

| Value | Severity          | Keyword   | Description                                      |
| ----- | ----------------- | --------- | ------------------------------------------------ |
| `0`   | **Emergency**     | `emerg`   | System is unusable                               |
| `1`   | **Alent**         | `alert`   | Action must be taken immediately                 |
| `2`   | **Critical**      | `crit`    | Critical conditions                              |
| `3`   | **Error**         | `err`     | Error conditions                                 |
| `4`   | **Warning**       | `warning` | Warning conditions                               |
| `5`   | **Notice**        | `notice`  | Normal but significant conditions (Notification) |
| `6`   | **Informational** | `info`    | Informational messages                           |
| `7`   | **Debug**         | `debug`   | Debug-level messages                             |

How to memorize? Choose a mnemonic you like the most:

- **Every Awesome Cisco Engineer Will Need Ice-cream Daily**
- Everyone Always Complains Even When Nothing Is Difficult
- Emergencies Are Critical Even When Nobody Is Dead

>[!quote]
>Because severities are very subjective, a relay or collector should not assume that all originators have the same definition of severity.
>- [`RFC 5424`](https://datatracker.ietf.org/doc/html/rfc5424)

## Configuration

#### Logging in the CLI

- To configure **logging to the console line** (enabled by default) for messages with `6` severity level and higher:

```toml
R1(config)# logging console 6
```


By default, log messages displayed are in the CLI asynchronously. In this case, a log message may appear when you're right in the middle of typing a command, so the message breaks it.

- To prevent this, use the `logging synchronous` command in the VTY line configuration mode:

```toml
R1(config)# line console 0
R1(config-line)# logging synchronous
```

#### Logging to the VTY lines: SSH

To configure logging to the VTY lines for messages with `informational` severity level and higher:

```toml
R1(config)# logging monitor informational 
```

>[!warning] By default, even if `logging monitor [level]` is enables, Syslog messages will not be displayed when connected via SSH (or Telnet).

- For the messages to be displayed in the terminal when connected via SSH or Telnet, type: 

```toml
R1# terminal monitor
```

>[!important] This command must be used every time when connected to the device via SSH (or Telnet).
#### Logging to the device's RAM

To configure logging to the buffer in the device's RAM for messages with severity level `6` (`info`) and higher:

```toml
R1(config)# logging buffered 8192 6
```

>[!note]
>- `8192` specifies the size of the buffer in bytes. It is optional; when not specified, the device will use its default buffer size.

>[!warning] If the size of the buffer set is too large, it can take the system memory away from other essential operations.
#### Logging to an external server

- To configure logging to an external server:

```toml
R1(config)# logging 192.168.1.100
# or
R1(config)# logging host 192.168.1.100
```

- To configure the levels of messages sent to the external server:

```toml
R1(config)# loggin trap debugging
```

#### Logging timestamps

- To enable timestamps for Syslog messages:

```toml
R1(config)# service timestamps log ?
	datetime  Timestamp with date and time
	uptime    Timestamp with system uptime	
```

- `datetime`
	- the date/time when the event occurred
 - `uptime`
	 - timestamps relative to the time system had been running when the event occurred. 

| Command                                                 | Description                                                                       |
| ------------------------------------------------------- | --------------------------------------------------------------------------------- |
| `R1(config)# logging console [severity]`                | Configure logging to the console line (enabled by default)                        |
| `R1(config)# logging monitor [severity]`                | Configure logging to the VTY lines                                                |
| `R1# terminal monitor`                                  | Display messages to the VTY lines. Must be used every time when connected via SSH |
| `R1(config)# logging buffered [buffer-size] [severity]` | Configure logging to the buffer (the device's RAM)                                |
| `R1(config)# logging [IP adddress]`                     | Configure logging to an external server                                           |
| `R1(config)# logging host [IP address]`                 | Configure logging to an external server                                           |
| `R1(config)# logging trap [severity]`                   | Configure the severity levels of messages sent to the external server             |
| `R1(config)# service timestamps log [datetime\|uptime]` | Enable timestamps for Syslog messages                                             |
| `R1(config-line)# logging synchronous`                  | To prevent command break by Syslog messages when typing                           |

## Syslog vs SNMP

>[!note] Syslog vs SNMP
>Syslog and SNMP are both used for monitoring and troubleshooting of devices. They are complementary, but their functionalities are different. 

- **Syslog** is used for message logging.
	- Events that occur within the system are categorized based on facility/severity and logged.
	- Used for system management, analysis, and troubleshooting.
	- Messages are sent from the devices to the server. The server **can't actively pull information from the devices or modify variables**.

- **SNMP** is used to retrieve and organize information about the SNMP managed devices.
	- IP addresses, current interface status, temperature, CPU usage, etc.
	- SNMP servers an use **`Get`** to query (pull) information from clients and **`Set`** to modify variables on the clients.

## Quiz

1. Which of the following locations are Syslog messages sent to by default, without any specific Syslog configuration? (select two)
	- a. External Syslog server
	- b. Console line
	- c. Buffer
	- d. VTY lines

2. You issue the `logging buffered 6` command on R1. Syslog messages of which severity levels will be saved to the logging buffer?
	- a. All Syslog messages.
	- b. Severity `6` and `7`
	- c. Severity `0` to `6`
	- d. Severity `6` only


3. Which of the following Syslog message fields might not be displayed, depending on the device's configuration? (select two)
	- a. `seq`
	- b. `facility`
	- c. `severity`
	- d. `timestamp`

```
seq: timestamp: %facility-severity-MNEMONIC: description
```

| Question | Answer     |
| -------- | ---------- |
| `1.`     | `b.`, `c.` |
| `2.`     | `c.`       |
| `3.`     | `a.`, `d.` |
|          |            |
