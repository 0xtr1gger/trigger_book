---
created: 2025-10-27 03:47:41
tags:
  - protocols
---
## Internal clock

 All computers have an internal clock, including network devices. It's important that these devices have an accurate clock that is synchronized with other devices. That's the purpose of NTP.
 
>[!note] In operation since before 1985, NTP is one of the oldest Internet protocols in current use. NTP was designed by David L. Mills of the University of Delaware. 

- To show the time on Cisco devices, use the `show clock` command:

```toml
R1# show clock
```

```toml
*00:16:00.857 UTC Mon Sep 1 2025
```

- To also show the time source, use the `show clock detail` command:

```toml
R1# show clock detail
```

```toml
*00:16:00.857 UTC Mon Sep 1 2025
Time source is hardware calendar
```

>[!note] 
>- Asterisk `*` means the time is not considered authoritative.
>- The hardware calendar is the default time source.

>[!important] The default time zone is UTC (Coordinated Universal Time).

>[!important] One of the main reasons to have accurate time on a device is to have accurate logs for troubleshooting.
>- View device's logs:
>```toml
>R1# show logging
>```

### Hardware calendar and software clock

- To manually configure **software clock**, use the `clock set` command:

```toml
R1# clock set <hh:mm:s>s <1-31> <month> <year>
```

```toml
R1# clock set 14:30:00 1 Sep 2025
```

- Show current clocks:

```toml
R1# show clock detail
```

```toml
14:30:05.887 UTC Mon Sep 1 2025
Time source is user configuration
```

>[!note]+ The hardware clock
>- The **hardware clock** tracks the date and time on the device even if it restarts, power is lost, etc. 
>- When the system is restarted, the hardware clock is used to initialize the **software clock**. 

- To manually configure the **hardware calendar**, use the `calendar set` command:

```toml
R1# calendar set 14:30:00 1 Sep 2025
```

>[!note] Although the hardware calendar (built-in clock) is the default time source, the hardware clock and software clock are separate and can be configured separately.

>[!note] Typically you will want to synchronize the software clock and hardware calendar.

- To **sync the calendar to the clock** (hardware calendar is changed): 

```toml
R1# clock update-calendar
```

- To **sync the clock to the calendar** (software clock is changed):

```toml
R1# clock read-calendar
```

### Timezone

- To configure the timezone, use the `clock timezone` command:

```toml
R1(config)# clock timezone <name> <hours_offset> [minutes_offset]
```

```toml
R1(config)# clock timezone JST 9
```

### Summertime daylight saving time

- To configure Daylight Saving Time (DST), also called summer time, use the `clock summer-time` command:

```toml
R1(config)# clock summer-time recurring NAME START-DST END-DST [offset]
```

---

```toml
R1(config)# clock summer-time ?
  WORD       name of time zone in summer
  date       Configure absolute summer time
  recurring  Configure recutting summer time
```

```toml
R1(config)# clock summer-time recurring ?
  <1-4>   Week number to start
  first   First week of the month
  last    Last week of the month
  
R1(config)# clock summer-time recurring 2 Sunday March 2:00 1 Sunday November 02:00
```
---

>[!warning] Manually configuring the time on devices is not scalable.

>[!warning] Manually configured clocks will drift over time.
## NTP

>**The Network Time Protocol (NTP)** is a protocol for clock synchronization between computer systems over packet-switched, variable-latency data networks.

- NTP is intended to synchronize all participating computers to within a few milliseconds of Coordinated Universal Time (UTC).
- The current protocol is **version 4 (NTPv4)**.
- NTP uses only the UTC time zone.

>[!note] NTP can provide accuracy of time within ~1 millisecond if the NTP server is the same LAN, or within ~50 milliseconds if connecting to the NTP server over a WAN/the Internet.

>**NTP uses UDP port `123` to communicate.**

>[!important]+ NTP peer-to-peer
>- The protocol is usually described in terms of a **client-server model**, where NTP clients request the time from NTP servers. 
>- However, NTP can as easily be used in **peer-to-peer** relationships where both peers consider the other to be a potential time source. 
>
>In other words, **a device can be an NTP server and an NTP client at the same time**.

> **NTP peering** is a method for synchronizing the clocks of multiple devices with each other. Unlike NTP servers, which are authoritative time sources, NTP peers are devices that can both act as clients and servers, exchanging time information with each other.


>[!interesting]+ NTP is slow
>NTP is very slow compared to other network protocols. Its default poll interval is typically between 1 and 15 **minutes**.

>[!interesting] NTP works best when a device's clock is already close to the accurate time. 
>The protocol is designed to adjust the time gradually in tiny steps, minimizing abrupt changes that could disrupt processes dependent on precise timing.


>[!important] As a general rule of thumb, before configuring a network device to sync with NTP, **manually set the device's internal clock to a time relatively close to the accurate time**. 

## Clock strata

NTP uses a hierarchical, semi-layered system of time sources. Each level of this hierarchy is referenced to as a **stratum**.

>**Stratum** essentially indicates the **distance from the reference clock**.

- The farther away from the reference clock the higher the stratum.
- The higher the stratum the less accurate the clock considered to be.

Each stratum is assigned a number, starting from `0` for the **reference clock** at the top.
- A server synchronized to a stratum `n` server runs at stratum `n + 1`.


>[!important] **The upper limit for stratum is `15`**.

>[!important] Stratum `16` is used to indicate that a device is **unsynchronized** or **unreachable**.

>[!important] The stratum field set to `0` in an NTP packet indicates an **unspecified stratum**.

>[!important] Reference clocks
>A **reference clock** is an NTP server that serves as a highly accurate time source, such as atomic clock or a GPS satellite. Reference clocks are **stratum `0`**.

>[!interesting]+ Atomic clocks
>- GPS satellites rely on **[atomic clocks](https://en.wikipedia.org/wiki/Atomic_clock)** to provide accurate time to clients on Earth. They're extremely precise, with the accuracy **in the nanosecond range**. 
>- Atomic clocks used in GPS are usually based on rubidium or cesium.


>[!note] Stratum is not always an indication of quality or reliability; it is common to find stratum `3` time sources that are higher quality than other stratum `2` time sources.

- **Stratum `1`** servers are referred to as **primary servers**. They synchronize **within a few milliseconds** to their attached stratum `0` device.
- Servers with **strata `2` and higher** are called **secondary servers**. 

| **Stratum** | **Description**                                                                                     |
| ----------- | --------------------------------------------------------------------------------------------------- |
| `0`         | Primary reference clock; the most precise clock, with accuracy within nanoseconds  to microseconds. |
| `1`         | Directly synchronized to stratum `0`;<br>provide 1-10 microseconds accuracy.                        |
| `2`         | Synchronized to stratum `1`;<br>provide 1-10 milliseconds accuracy.                                 |
| `3`         | Synchronized to stratum `2`;<br>provide 10-100 milliseconds accuracy.                               |
| `4`         | Synchronized to stratum `3`;<br>provide 100 milliseconds to 1 second accuracy.                      |
| `5`-`15`    | Synchronized to a higher stratum;<br>provide 1 to several seconds accuracy.                         |
| `16`        | Unsynchronized or unreachable; not synchronized.                                                    |
## NTP modes

Cisco devices can operate in several NTP modes:

- **NTP client mode**
	- The most common configuration where a device synchronizes its clock with one or more NTP servers.
	- The client sends periodic time requests to configured servers and adjusts its clock based on the responses.
	- Typically used for end devices and network devices that need accurate time but don't provide time services to others.

Configuration:

```toml
# configure an NTP server for a device
R1(config)# ntp server <ip_address_or_hostname>
```

```toml
# configure preferred NTP server
R1(config)# ntp server <ip_address_or_hostname> prefer
```

>[!tip] You can configure multiple NTP servers for redundancy. The `prefer` keyword designates a preferred time source.

>[!note] In the case, the basic NTP client configuration is complete; nothing else needs to be done for NTP to be fully operating. 
>- By default, NTP is enabled on all interfaces on a Cisco switch. 
>
>The following conditions apply to a default NTP configuration:
>- NTP associations, such as peer or server, are not yet configured.
>- NTP authentication is disabled.
>- NTP access restrictions are not configured.
>- NTP broadcast service is disabled.
>- NTP packet source IP address is configured by the outgoing interface.
>
>>[!note] You do not need to configure the NTP packet source IP address (with `ntp source`) as long as the address of the outgoing interface can be used as a destination address for NTP replies.
>

- **NTP server mode**
	- Allows a device to provide time information to NTP clients. 
	- The device synchronizes with upstream NTP servers and then provides time services to downstream clients. 
	- Typically configured on network infrastructure devices like core switches and routers.

Configuration:

```toml
# configure an upstream NTP server for a device
R1(config)# ntp server <upsteram_server_ip_address_or_hostname>
```

```toml
# configure the source IP address or interface for outgoing NTP packets to send to downstream NTP clients
R1(config)# ntp server <ip_address_or_interface>
```

>[!important] The default stratum is `8`.

- **NTP master mode**
	- Configures a Cisco device to act as an authoritative NTP server with a specified stratum level, even without synchronizing to an external source.
	- Useful for isolated networks or as a backup time source.

```toml
R1(config)# ntp master <stratum_level>
```

- **NTP symmetric active mode**
	- Used between NTP devices to synchronize with each other as peers (**peer-to-peer**).
	- This mode is intended for configurations where a group of low-stratum peers operate as mutual backups for each other. 
	- Each peer can both provide and receive time synchronization.

```toml
# configure NTP symmetric active mode by setting an NTP peer
R1(config)# ntp peer <ip_address>
```

- **NTP symmetric passive mode**
	- **NTP symmetric passive mode** is automatically created when a device receives a message from a peer operating in symmetric active mode.
	- The symmetric passive end doesn't require explicit configuration — it activates upon receiving a symmetric active message.
	- The passive association persists only as long as the active peer is reachable.

- **Broadcast/multicast mode**
	- **Broadcast and multicast modes** allow NTP servers to send time information to multiple clients simultaneously without requiring individual client requests.
	- These modes are configured on a per-interface basis.

```toml
# for a broadcast server
R1(config)# interface <interface_id>
R1(config-if)# ntp broadcast
```

```toml
# for a broadcast client
R1(config)# interface <interface_id>
R1(config-if)# ntp broadcast client
```

>[!note] NTP broadcast messages enable an NTP client to configure its time based on NTP broadcast messages from any NTP server on the local area network (LAN).

>[!warning] You can configure an interface to either send NTP broadcast messages or receive NTP broadcast messages, but not both.

```toml
# for a multicast server
R1(config)# interface <interface_id>
R1(config-if)# ntp multicast <multicast_ip_address>
```

```toml
# for a multicast client
R1(config)# interface <interface_id>
R1(config-if)# ntp broadcast client <multicast_ip_address>
```

>[!note] Broadcast and multicast modes consume less bandwidth than client/server polling but may be less accurate (they don't account for network delay).
## NTP authentication

- NTP authentication can be configured to make sure NTP clients only sync to the intended servers.

>[!important] Make sure the server and client are configured in the same way.

- Enable NTP authentication: 

```toml
R1(config)# ntp authenticate
```

- Create the NTP authentication key(s):

```toml
R1(config)# ntp authentication-key <key_number> md5 <key>
```

>[!note] The `<key>` is just a password.

- Specify the trusted key(s):

```toml
R1(config)# ntp trusted-key <key_number>
```

>[!note] Creating the key uses one command, `ntp authentication-key`, and specifying that it's trysted uses another command, `ntp trusted-key`.

- Specify which key to use for the device (not needed for the NTP server itself, only for clients):

```toml
R1(config)# ntp server <ip_address> key <key_number>
```

---

For example, on the server, you run:

```toml
R1(config)# ntp authenticate
R1(config)# ntp authentication-key 1 md5 password123
R1(config)# ntp trusted-key 1
```

Then, on the clients:

```toml
R2(config)# ntp authenticate
R2(config)# ntp authentication-key 1 md5 password123
R2(config)# ntp trusted-key 1
R2(config)# ntp server <ntp_server_ip_address> key 1
```
## Show commands

- To show **NTP configuration and statistics**:

```toml
R1# show ntp
```

- To **check NTP synchronization status**:

```toml
R1# show ntp status
```

- To display **NTP associations** (servers/peers and their status):

```toml
R1# show ntp associations
```

Symbols to note:

- `*` = current synchronization source
- `+` = candidate servers
- `~` = configured servers
- `-` = outlier (ignored)
- `x` = falseticker (discarded due to incorrect time)

## Why clocks drift

Manual clock configurations or internal hardware clocks can drift over time. This happens due to various reasons:

- Crystal oscillator variations
    - Quartz crystals used in internal clocks have natural frequency drifts due to temperature changes, aging, or manufacturing variations. This can result in a gradual deviation from the accurate time.

- Power supply fluctuations
    - Power supply voltage or frequency variations can cause the clock circuitry to drift, leading to inaccuracies.

- Noise and interference
    - Electromagnetic interference (EMI) or radio-frequency interference (RFI) can cause clock circuits to oscillate at incorrect frequencies, leading to drift.

- Software errors
    - In the case of software-based clocks, errors in the clock’s algorithm or incorrect system settings can cause drift.

- Vibrations and mechanical stress
    - Mechanical stress and vibrations can cause the clock’s mechanical components to shift, leading to drift.
## Why time is important

- Synchronization of timestamps
    - Accurate timestamps are crucial for logging, auditing, and trouble shooting purposes. A synchronized clock ensures that all devices on the network have a common reference point for timestamping events, making it easier to correlate logs, monitor performance, and identify issues.
    - From the perspective of CCNA and network engineers, this is the most important reason to have accurate time on a device: to have accurate logs for troubleshooting.

- Time-dependent protocols and security
    - An accurate clock is essential for security protocols like Kerberos, SSL/TLS, and others.
    - These protocols rely on the correct date and time to ensure the security and validity of the encryption. If the computer's date and time are incorrect, it can cause SSL/TLS connections to fail.

- Certificate validation
    - Public Key Infrastructure (PKI) relies on accurate time stamps to validate digital certificates. If the device’s internal clock is off, certificate validation may fail, leading to issues with secure connections.

- Authentication
    - Accurate timekeeping is essential for authentication protocols, such as Kerberos and NTLM. Inaccurate clocks can cause authentication failures, preventing users from accessing online resources.
    - Additionally, some websites and online services use time-based authentication mechanisms, such as tokens that expire after a certain period. If the computer's date and time are incorrect, it can cause authentication failures, preventing access to those services.
## Flashcards

- What is the primary purpose of Network Time Protocol (NTP)?
    
    - To synchronize clocks of computer systems over packet-switched, variable-latency data networks within a few milliseconds of Coordinated Universal Time (UTC).
        
- Which UDP port does NTP use for communication?
    
    - UDP port 123.
        
- What is the current version of the NTP protocol commonly used?
    
    - Version 4 (NTPv4).
        
- Does NTP use local time zones or UTC?
    
    - NTP uses only the UTC time zone.
        
- Can a device act as both an NTP client and an NTP server simultaneously?
    
    - Yes, a device can be both an NTP client and server at the same time.
        
- What is NTP peering?
    
    - A method where devices synchronize clocks mutually, acting as both clients and servers, exchanging time information with each other.
        
- What is a stratum in NTP?
    
    - A hierarchical level that defines the distance from a reference clock to a network device.
        
- What stratum level is assigned to a reference clock?
    
    - Stratum 0.
        
- What types of devices are considered stratum 0?
    
    - High-precision timekeeping devices like atomic clocks, GPS clocks, or PTP-synchronized clocks.
        
- What stratum level do primary time servers have?
    
    - Stratum 1.
        
- What stratum level do secondary servers have?
    
    - Stratum 2 and above.
        
- What does a stratum level of 16 indicate?
    
    - The device is unsynchronized.
        
- How is the stratum level of a server determined relative to its upstream source?
    
    - A server synchronized to a stratum n server runs at stratum n + 1.
        
- What are the three main NTP modes supported by Cisco devices?
    
    - NTP client mode, NTP server mode, and NTP broadcast/multicast mode.
        
- What is the function of an NTP client?
    
    - Synchronizes its clock by querying an NTP server or peer.
        
- What is the function of an NTP server?
    
    - Responds to client requests and provides time synchronization services.
        
- How does NTP broadcast/multicast mode operate?
    
    - The server broadcasts or multicasts time updates without client requests; clients listen for these broadcasts.
        
- What is NTP master mode?
    
    - The device acts as an authoritative time source (stratum 1 to 15) distributing time without external synchronization.
        
- What is symmetric active mode in NTP peering?
    
    - Two devices act as peers and synchronize time mutually, each can serve as client and server dynamically.
        
- What is symmetric passive mode?
    
    - The device listens for NTP packets from a peer and synchronizes time but does not initiate requests.
        
- What is the difference between a broadcast client and a static client in NTP?
    
    - A broadcast client can receive time from any NTP server broadcasting on the network; a static client receives time only from the server specified in the `ntp server` command.
        
- Can an NTP client synchronize to multiple servers?
    
    - Yes, an NTP client can sync to multiple servers for redundancy and accuracy.
        
- What Cisco IOS command shows NTP configuration and statistics?
    
    - `show ntp`
        
- How do you check NTP synchronization status on a Cisco device?
    
    - `show ntp status`
        
- Which command displays NTP associations and their status?
    
    - `show ntp associations`
        
- What symbol in `show ntp associations` output indicates the current synchronization source?
    
    - `*` (asterisk)
        
- What does the `+` symbol indicate in `show ntp associations`?
    
    - Candidate servers.
        
- What does the `~` symbol indicate in `show ntp associations`?
    
    - Configured servers.
        
- What does the `-` symbol indicate in `show ntp associations`?
    
    - Outlier (ignored server).
        
- What does the `x` symbol indicate in `show ntp associations`?
    
    - Falseticker (discarded due to incorrect time).
        
- How do you configure an NTP client to use a specific NTP server?
    
    - `ntp server <NTP_SERVER_IP_OR_HOSTNAME>`
        
- How do you specify a preferred NTP server?
    
    - Append the keyword `prefer` after the server IP or hostname, e.g., `ntp server 192.168.1.1 prefer`
        
- How do you enable NTP broadcast client mode on Cisco IOS?
    
    - `ntp broadcast client`
        
- How do you configure a Cisco device as an authoritative NTP master with stratum 3?
    
    - `ntp master 3`
        
- How do you configure symmetric active NTP peering between two devices?
    
    - `ntp peer <PEER_IP_OR_HOSTNAME>`
        
- How do you enable NTP authentication on a Cisco device?
    
    - `ntp authenticate`
        
- How do you configure an NTP authentication key with MD5?
    
    - `ntp authentication-key <key-number> md5 <secret-key>`
        
- How do you specify trusted keys for NTP authentication?
    
    - `ntp trusted-key <key-number>`
        
- How do you associate an NTP server with an authentication key?
    
    - `ntp server <IP_ADDRESS> key <key-number>`
        
- What command shows the current time on a Cisco device?
    
    - `show clock`
        
- How do you view detailed clock information including time source?
    
    - `show clock detail`
        
- What is the difference between hardware clock and software clock on Cisco devices?
    
    - Hardware clock (calendar) keeps time even when the device is powered off; software clock is the running system time used by the OS.
        
- How do you manually set the software clock time?
    
    - `clock set [time]`
        
- How do you manually set the hardware clock (calendar)?
    
    - `calendar set`
        
- How do you synchronize the hardware clock to the software clock?
    
    - `clock update-calendar`
        
- How do you synchronize the software clock to the hardware clock?
    
    - `clock read-calendar`
        
- How do you configure the timezone on a Cisco device?
    
    - `clock timezone <name> <hours-offset> [minutes-offset]`
        
- How do you configure recurring daylight saving time on Cisco IOS?
    
    - `clock summer-time recurring <name> <start> <end> [offset]`
        
- What is the default timezone on Cisco devices?
    
    - UTC (Coordinated Universal Time).
        
- What stratum level is assigned to a device that is unsynchronized?
    
    - Stratum 16.
        
- Why is stratum not always an indication of time source quality?
    
    - Because some stratum 3 servers may have better quality and reliability than some stratum 2 servers.
        
- What is the purpose of the `prefer` keyword in NTP server configuration?
    
    - To designate a preferred NTP server among multiple configured servers.
        
- What is the main benefit of NTP symmetric active mode?
    
    - Provides redundancy and mutual synchronization between peers.
        
- What is the significance of the stratum number in NTP?
    
    - It prevents cyclical dependencies and indicates the distance from the reference clock.
        
- What is the maximum stratum level allowed in NTP?
    
    - 15.
        
- What does a stratum field set to 0 in an NTP packet indicate?
    
    - An unspecified stratum.
        
- What is the relationship between stratum 1 servers?
    
    - They may peer with each other for sanity checks and backup.
        
- Can NTP clients operate without specifying a server?
    
    - No, clients must be configured with at least one server or peer to synchronize time.
        
- What is the purpose of the `ntp broadcast client` command?
    
    - To enable a device to listen for NTP broadcast messages from servers without sending requests.
        
- What is the default stratum level when configuring `ntp master` without specifying a number?
    
    - Stratum 8.
        
- What type of key does NTP authentication support?
    
    - MD5 keys only.
        
- How do you verify the NTP synchronization source on a Cisco device?
    
    - Using `show ntp associations` and looking for the `*` symbol.
        
- What is the function of the `show ntp` command?
    
    - Displays the NTP configuration and statistics summary.
        
- How do you configure multiple NTP servers on a Cisco router?
    
    - Use multiple `ntp server` commands, one per server.
        
- What happens if an NTP server is unreachable?
    
    - The client will try other configured servers or peers to maintain synchronization.
        
- What is the role of the reference clock in NTP?
    
    - It is the most accurate time source (stratum 0) that primary servers synchronize to.
        
- How does NTP prevent cyclical dependencies in the hierarchy?
    
    - By incrementing the stratum level for each hop away from the reference clock.
        
- What is the significance of the `ntp trusted-key` command?
    
    - It designates which authentication keys are trusted for NTP synchronization.
        
- How do you manually synchronize the software clock to the hardware clock after a reboot?
    
    - Use `clock read-calendar`.
        
- What is the effect of configuring `ntp peer` on a Cisco device?
    
    - Enables symmetric active mode peering for mutual time synchronization.
        
- What is the difference between symmetric active and symmetric passive modes?
    
    - Symmetric active mode initiates synchronization messages; symmetric passive mode only listens and responds.
        
- Why is accurate time synchronization important in networks?
    
    - For correct logging, security protocols, troubleshooting, and time-sensitive applications.
        
- What command would you use to configure an NTP server with authentication key number 1 and key "My_Secret"?
    

```toml
ntp authentication-key 1 md5 MySecret
ntp authenticate
ntp trusted-key 1
ntp server <IP_ADDRESS> key 1

```

- How do you configure a Cisco device to act as an NTP master with stratum 3?
    
    - `ntp master 3`
        
- What is the purpose of the `show clock detail` command?
    
    - To display the current time along with the time source and other detailed clock information.
        
- How can you check if a Cisco device is synchronized to an NTP server?
    
    - Use `show ntp status` and check for the "synchronized" status.
        
- What is the default behavior of NTP when multiple servers are configured?
    
    - It selects the best server based on reachability, stratum, and delay.
        
- How does NTP handle time synchronization in large networks efficiently?
    
    - Using broadcast or multicast modes to reduce client requests.
        
- What is the role of the `ntp master` command in the absence of external time sources?
    
    - It makes the device an authoritative time source (stratum 1-15) for other devices.
        
- How do you disable NTP authentication on a Cisco device?
    
    - Use `no ntp authenticate` in global configuration mode.
        
- What is the command to view NTP associations with detailed statistics?
    
    - `show ntp associations detail`
        
- How do you manually set the time on a Cisco device if no NTP is available?
    
    - Use the `clock set` command.
        
- How do you configure daylight saving time recurring on Cisco IOS?
    
```toml
clock summer-time recurring <name> <start> <end> [offset]
```

- What is the difference between hardware clock and calendar on Cisco devices?
    
    - They refer to the same built-in internal clock, but the terms are used interchangeably; the hardware clock keeps time when powered off.
        
- How do you synchronize the hardware clock to the software clock on Cisco IOS?
    
    - `clock update-calendar`
        
- How do you synchronize the software clock to the hardware clock on Cisco IOS?
    
    - `clock read-calendar`