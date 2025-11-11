---
created: 2025-10-26 03:13:22
tags:
  - LAN_protocols
---
## DHCP

>The **Dynamic Host Configuration Protocol (DHCP)** is a network management protocol used to automatically assign IP addresses and other parameters to devices on a LAN.

- DHCP is used to allow hosts automatically and dynamically learn various aspects of their network configuration, such as IP address, subnet mask, default gateway, DNS server, etc. without manual configuration.

>[!note]+ DHCP can be used by hosts to learn:
> - Private IP address
> - Subnet mask
> - Default gateway
> - DNS server
> - IP address lease duration
> - NTP server
> - FTP server
> - etc.

>[!note] DHCP eliminates the need for manual configuration of individual devices on a network.

## How DHCP works

DHCP infrastructure usually consists of two components:

- **DHCP server**
	- The server responsible for automatically assigning IP addresses to network devices on a LAN.
	- Uses **UDP port `67`**.

- **DHCP clients**
	- Network devices, such as laptops, smartphones, and other, to which the DHCP server gives IP addresses.
	- Use **UDP port `68`**.

>[!note]+
>- On small networks, functions of the DHCP server are usually performed by a router.
>- On larger networks, the DHCP server is usually a dedicated Linux/Windows server.

### DHCP lease

DHCP uses a lease-based system where IP addresses are assigned to devices **for a specific period of time**.

>A **DHCP lease** is the amount of time for which a DHCP server assigns an IP address to a device.

- When a client disconnects from the network, IP address is released back to a DHCP pool of addresses, and can then be assigned to another device.
- When a lease is about to expire, the client must *renew* the lease. 

>[!important] A common default value for a DHCP lease is **24 hours (86 400 seconds)**.

- Display all DHCP clients that are currently assigned IP addresses:

```toml
R1# show ip dhcp binding
```

```toml
Bindings from all pools not associated with VRF:
IP address    Client-ID/         Lease expiration     Type
              Hardware address/  
              User name
192.168.1.11  0100.0c29.e727.29  Sep 05 2025 3:07 PM  Automatic
```


### DORA

DHCP address assignment works as follows:

- **DHCP Discover**
- **DHCP Offer**
- **DHCP Request**
- **DHCP Acknowledgment**

| Message  | Direction       | Type                 |
| -------- | --------------- | -------------------- |
| Discover | Client ⇒ Server | Broadcast            |
| Offer    | Client ⇐ Server | Broadcast or Unicast |
| Request  | Client ⇒ Server | Broadcast            |
| Ack      | Client ⇐ Server | Broadcast or Unicast |

![[DORA.png]]
#### DHCP Discover

>The client sends a **broadcast DHCP Discover** message to discover DHCP servers on the network.

| Field                   | Value                                                |
| ----------------------- | ---------------------------------------------------- |
| Destination IP address  | `255.255.255.255`                                    |
| Source IP address       | `0.0.0.0`                                            |
| Destination port number | `67` (DHCP server port)                              |
| Source port number      | `68` (DHCP client port)                              |
| Destination MAC address | `FF:FF:FF:FF:FF:FF` (broadcast)<br>(Ethernet header) |
| Source MAC address      | The client's MAC address<br>(Ethernet header)        |
>[!note] 
>If the PC previously had an IP address inside a network, it can mark it as a preferred option. The DHCP server might assign this address to the host again if it's available; if the address is already taken, the server will choose a different one.

#### DHCP Offer

>The server sends a **broadcast or unicast DHCP Offer** message, offering an IP address for the client to use and sharing information about the network (e.g., the default gateway, DNS server, etc.). 

>[!important] The DHCP Offer messages can be either **broadcast** or **unicast**.
>- This depends on the DHCP client: some clients don't accept unicast messages before their IP address is actually configured. 

| Field                   | Value                                                                                                  |
| ----------------------- | ------------------------------------------------------------------------------------------------------ |
| Destination IP address  | **Broadcast**: `255.255.255.255`<br>**Unicast**: IP address offered to the client                      |
| Source IP address       | IP address of the DHCP server                                                                          |
| Destination port number | `68` (DHCP client port)                                                                                |
| Source port number      | `67` (DHCP server port)                                                                                |
| Destination MAC address | **Broadcast**: `FF:FF:FF:FF:FF:FF`<br>**Unicast**: MAC address of the DHCP client<br>(Ethernet header) |
| Source MAC address      | MAC address of the DHCP server<br>(Ethernet header)                                                    |
In the Options section of a DHCP message, the server also lists the following:
- DHCP lease time
- DHCP server IP address
- Subnet mask
- Default gateway IP address
- The DNS server

>[!note] At this point, the client's IP address hasn't yet been actually configured.

#### DHCP Request

>The client sends a **broadcast DHCP Request** to inform the server it wants to use the offered IP address.

>[!important] DHCP Requests are especially important on networks with multiple DHCP servers. 
>- In this case, all those servers would reply to the DHCP Discover message from the client, so the client has to tell which server it is accepting the Offer from and request the IP address to use.

>[!note] Typically, the client will accept the first offer it receives.

| Field                   | Value                                         |
| ----------------------- | --------------------------------------------- |
| Destination IP address  | `255.255.255.255`                             |
| Source IP address       | `0.0.0.0`                                     |
| Destination port number | `67` (DHCP server port)                       |
| Source port number      | `68` (DHCP client port)                       |
| Destination MAC address | `FF:FF:FF:FF:FF:FF`<br>(Ethernet header)      |
| Source MAC address      | The client's MAC address<br>(Ethernet header) |
>[!note] Destination MAC address: `FF:FF:FF:FF:FF:FF`
>If there are multiple DHCP servers on the network, all of them will receive the DHCP Request, so all servers will know what address the client has requested.

>[!note] Source IP address: `0.0.0.0`
>- Since the client IP address hasn't been actually configured yet despite being offered by the server, the source IP address of a DHCP offer is still set to `0.0.0.0`.

>[!note] Destination IP address (DHCP server's address)
>- The client knows the IP address of the DHCP server because it's listed in the Options of the DHCP Offer message the client previously received (e.g., `DHCP Server Identiifer (192.168.1.1)`).

#### DHCP Acknowledgment

>The server sends a **broadcast or unicast DHCP Acknowledgment** to confirm that the client may use the requested IP address.

| Field                   | Value                                                                                                  |
| ----------------------- | ------------------------------------------------------------------------------------------------------ |
| Destination IP address  | **Broadcast**: `255.255.255.255`<br>**Unicast**: IP address offered to the client                      |
| Source IP address       | IP address of the DHCP server                                                                          |
| Destination port number | `68` (DHCP client port)                                                                                |
| Source port number      | `67` (DHCP server port)                                                                                |
| Destination MAC address | **Broadcast**: `FF:FF:FF:FF:FF:FF`<br>**Unicast**: MAC address of the DHCP client<br>(Ethernet header) |
| Source MAC address      | MAC address of the DHCP server<br>(Ethernet header)                                                    |

>[!important] Only after the client receives the DHCP Ack message it can finally configure the IP address on its network interface.

>[!note] Broadcast or unicast 
>Just like the DHCP Offer message, DHCP Ack can be either *broadcast or unicast*, depending on the client.

>[!important]+ DHCP Nak
>The server may decline the DHCP Request from the client by sending a **DHCP Nak (Negative Acknowledgment)** message.
>Nak messages are also sent by the server to indicate the client's lease has expired.

 >[!important]+ DHCP Release
When the client doesn't need an IP address anymore, it can inform the DHCP server about it my sending a **unicast DHCP Release** message.

## Configuring a DHCP server and DHCP pools

To configure a DHCP server on a network:

1. Specify a range of addresses that won't be given to DHCP clients (**addresses excluded from DHCP pools**):

```toml
R1(config)# ip dhcp excluded-address 192.168.1.1 192.168.1.20
```

>[!important]+ DHCP pool
>A **DHCP pool** is a defined range of IP addresses that a DHCP server manages and assigns to network clients dynamically.
>- The DHCP server maintains a database of valid IP addresses within the pool, and these addresses are leased to clients for a specific period, after which they can be returned to the pool for reuse.
>- A pool can also be configured with a default gateway, DNS servers, and a domain to provide to clients.

2. Create a **DHCP pool**:

```toml
R1(config)# ip dhcp pool DHCP_POOL
R1(dhcp-config)#
```

>[!tip]+
>You should create a **separate DHCP pool for each network** the router is acting as DHCP server for. 

3. Configure the **range of IP addresses** to be assigned to clients in the DHCP pool
	- The range of IP address except the ones configured as excluded, will be given to the DHCP IP address pool.

```toml
R1(dhcp-config)# network 192.168.1.0 ?
  /nn or A.B.C.D  Network mask ore prefix length

R1(dhcp-config)# network 192.168.1.0 /24
# or
R1(dhcp-config)# network 192.168.1.0 255.255.255.0
```

4. Configure the **DNS server** to provide to clients:

```toml
R1(dhcp-config)# dns-server 1.1.1.1
```

5. Configure the **domain name** for the network:

```toml
R1(dhcp-config)# domain-name domain.com
```

6. Specify the **default gateway**:

```toml
R1(dhcp-config)# default-router 192.168.1.1
```

7. **Configure the DHCP lease time**

```toml
R1(dhcp-config)# lease 0 5 30

# 0 days
# 5 hours
# 30 minutes
```

>[!note]+ Infinite release time
>To configure **infinite lease time**, enter:
> 
> ```toml
> R1(dhcp-config)# lease infinite
> ```
> Though this is not recommended. 

```toml
R1(dhcp-config)# host 192.168.1.20/26
R1(dhcp-config)# client-identifier 0000.0c12.3456
```

```toml
R1(dhcp-config)# host 192.168.1.20 255.255.255.192
R1(dhcp-config)# client-identifier 0000.0c12.3456
```

>**You can not use the same DHCP pool for manual bindings and for dynamic IP address allocation.** 

## DHCP Relay

Some network engineers might choose to configure each router to act as the DHCP server for its connected LANs. Large enterprises, however, often choose to use a **centralized DHCP server** to assign IP address to clients in all subnets throughout the network.

However, if the server is centralized, it won't receive broadcast DHCP messages from all clients (since broadcast messages don't leave the local subnet).

>To fix this, you can configure a router to act as a **DHCP Relay agent**; it will forward the clients' broadcast DHCP messages to the remote DHCP server as unicast messages.

- A DHCP relay agent and a DHCP server communicate by sending unicast messages to each other. The DHCP relay simply forwards every DHCP message it receives to the DHCP server, only changing the source and destination address to its and DHCP server's own. 


![[DHCP_relay.png]]

Source: [Jeremy's IT Lab: Free CCNA | DHCP](https://www.youtube.com/watch?v=hzkleGAC2_Y&list=PLxbwE86jKRgMpuZuLBivzlM8s2Dk5lXBQ&index=76)

### Configuring a DHCP Relay agent

To configure a DHCP Relay agent:

1. Enter the config mode of the interface connected to the client devices:

```toml
R1(config)# interface g0/1
```

2. **Specify the IP address of the DHCP server as the helper address**:

```toml
R1(config-if)# ip helper-address 203.0.113.1
```

>[!interesting]+ The `helper-address` command
> By default, the **`ip helper-address`** command configures an interface to forward broadcasts to the following UDP ports:
> - UDP port `37` – Time Protocol
> - UDP port `49` – TACACS
> - UDP port `53` – DNS
> - UDP port `67` – Bootstrap Protocol (BOOTP) and DHCP Server
> - UDP port `68` – BOOTP and DHCP Client
> - UDP port `69` – TFTP
> - UDP port `137` – NetBIOS Name Service
> - UDP port `138` – NetBIOS Datagram
> You can issue the **`ip forward-protocol udp <port>`** command to configure the router to forward broadcasts for additional UDP ports.


>[!tip]+ Multiple DHCP servers
> 
> The use of the **`ip helper-address`** command is not limited to a single unicast address. If a network has multiple DHCP servers, an entry for each server could be configured on the router. The same DHCP, DNS, and TFTP on multiple servers with different IP addresses.
> 
>- For example, if DHCP requests were serviced at IP address `10.10.3.5`, DNS at `10.10.3.4`, and TFTP at `10.10.3.3`, you would issue the following commands:  
> 
> ```toml
> RouterA(config-if)#ip helper-address 10.10.3.3  
> RouterA(config-if)#ip helper-address 10.10.3.4  
> RouterA(config-if)#ip helper-address 10.10.3.5
> ```
> - In `show running-config`: 
> ```toml
> RouterA# show runnning-config
> ```
> 
> ```toml
> # ...
> !
> interface FastEthernet0/0  
>  ip address 10.10.2.1 255.255.255.0  
>  ip helper-address 10.10.3.3  
>  ip helper-address 10.10.3.4  
>  ip helper-address 10.10.3.5  
>  no ip directed-broadcast  
>  no shutdown
> !
> # ... 
> ```


## DHCP `show` commands

- To **display information about the currently leased addresses**:

```toml
R1# show ip dhcp binding
```

- To **display information about the configured DHCP pools**:

```toml
R1# show ip dhcp pool
```

- To **display current DHCP configuration**:

```toml
R1# do show run | section dhcp
```

- To **show all DHCP clients that are currently assigned IP addresses**:

```toml
R1# show ip dhcp binding
```
## Configuring DHCP clients

- The `ip address dhcp` mode tells the router to use DHCP to learn its IP address:

```toml
R1(config)# interface g0/1
R1(config-if)# ip address dhcp
```

## Windows and Linux DHCP commands
### Windows: DHCP commands

- Manually release an IP address obtained from a DHCP server:

```PowerShell
C:\Users\user> ipconfig /release
```

- Manually renew the IP address obtained from a DHCP server:

```PowerShell
C:\Users\user> ipconfig /renew
```

- View network configuration:

```PowerShell
C:\Users\user> ipconfig /all
```
### Linux: DHCP commands

To get IP address and interface information:

```bash
ip a
```

Manually renew the current IP address on the `eth0` interface:

```bash
dhclient -v -r eth0
```

To find out the DHCP server's IP address and other DHCP-related information:

```bash
more /var/lib/dhcp/dhclient.leases
```

Sample output:

```bash
lease {
  interface "ra0";
  fixed-address 192.168.1.106;
  option subnet-mask 255.255.255.0;
  option dhcp-lease-time 86400;
  option routers 192.168.1.1;
  option dhcp-message-type 5;
  option dhcp-server-identifier 192.168.1.1;
  option domain-name-servers 208.67.222.222,208.67.220.220;
  option dhcp-renewal-time 43200;
  option dhcp-rebinding-time 75600;
  option host-name "vivek-desktop";
  renew 0 2007/12/9 05:17:36;
  rebind 0 2007/12/9 15:06:37;
  expire 0 2007/12/9 18:06:37;
}
lease {
  interface "ra0";
  fixed-address 192.168.1.106;
  option subnet-mask 255.255.255.0;
  option routers 192.168.1.1;
  option dhcp-lease-time 86400;
  option dhcp-message-type 5;
  option domain-name-servers 208.67.222.222,208.67.220.220;
  option dhcp-server-identifier 192.168.1.1;
  option dhcp-renewal-time 43200;
  option dhcp-rebinding-time 75600;
  option host-name "vivek-desktop";
  renew 0 2007/12/9 06:11:22;
  rebind 0 2007/12/9 16:13:50;
  expire 0 2007/12/9 19:13:50;
}
```

- Look for `dhcp-server-identifier`.

## DHCP lab

![[DHCP_lab.png]]


1. Configure the following DHCP pools on `R2`:

- `POOL1`: `192.168.1.0/24` (reserve `.1` to `.10`)
	- DNS server: `1.1.1.1`
	- Domain: `jeremysitlab.com`
	- Default Gateway: `R1`

```toml
R2(config)# ip dhcp excluded-address 192.168.1.1 192.168.1.10
R2(config)# ip dhcp pool POOL1
R2(dhcp-config)# network 192.168.1.10 255.255.255.0
R2(dhcp-config)# dns-server 1.1.1.1
R2(dhcp-config)# domain-name jeremysitlab.com
R2(dhcp-config)# default-router 192.168.1.1
```

- `POOL2`: `192.168.2.0/24` (reserve `.1` to `.10`)
	- DNS: `8.8.8.8`
	- Domain: `jeremysitlab.com`
	- Default Gateway: `R2`


```toml
R2(config)# ip dhcp excluded-address 192.168.2.1 192.168.2.10
R2(config)# ip dhcp pool POOL2
R2(dhcp-config)# network 192.168.2.0 255.255.255.0
R2(dhcp-config)# dns-server 1.1.1.1
R2(dhcp-config)# domain-name jeremysitlab.com
R2(dhcp-config)# default-router 192.168.2.1
```

- `POOL3`: `203.0.113.0/30` (reserve `.1`)

```toml
R2(config)# ip dhcp excluded-address 203.0.113.1
R2(config)# ip dhcp pool POOL3
R2(dhcp-config)# network 203.0.113.0 255.255.255.252
```

```toml
R2(config)# do show ip dhcp pool
```

```toml
R2(dhcp-config)# do show ip dhcp pool

Pool POOL1 :
 Utilization mark (high/low)    : 100 / 0
 Subnet size (first/next)       : 0 / 0 
 Total addresses                : 254
 Leased addresses               : 0
 Excluded addresses             : 3
 Pending event                  : none

 1 subnet is currently in the pool
 Current index        IP address range                    Leased/Excluded/Total
 192.168.1.1          192.168.1.1      - 192.168.1.254     0    / 3     / 254

Pool POOL2 :
 Utilization mark (high/low)    : 100 / 0
 Subnet size (first/next)       : 0 / 0 
 Total addresses                : 254
 Leased addresses               : 0
 Excluded addresses             : 3
 Pending event                  : none

 1 subnet is currently in the pool
 Current index        IP address range                    Leased/Excluded/Total
 192.168.2.1          192.168.2.1      - 192.168.2.254     0    / 3     / 254

Pool POOL3 :
 Utilization mark (high/low)    : 100 / 0
 Subnet size (first/next)       : 0 / 0 
 Total addresses                : 2
 Leased addresses               : 0
 Excluded addresses             : 3
 Pending event                  : none

 1 subnet is currently in the pool
 Current index        IP address range                    Leased/Excluded/Total
 203.0.113.1          203.0.113.1      - 203.0.113.2       0    / 3     / 2
```

2. Configure `R1`'s `G0/0` interface as a DHCP client.
	- What IP address did it configure?

```toml
R1(config-if)# ip address dhcp
R1(config-if)# do show ip int br
Interface              IP-Address      OK? Method Status                Protocol 
GigabitEthernet0/0     unassigned      YES DHCP   administratively down down 
GigabitEthernet0/1     192.168.1.1     YES manual up                    up 
GigabitEthernet0/2     unassigned      YES unset  administratively down down 
Vlan1                  unassigned      YES unset  administratively down down
```

3. Configure `R1` as a DHCP relay agent for the `192.168.1.0/24` subnet.

```toml
R1(config-if)# int g0/1
R1(config-if)# ip helper-address 203.0.113.1
```

4. Use the CLI of `PC1` and `PC2` to make them request an IP address from their DHCP server.

## Flashcards

- What is DHCP?
    
    - DHCP (Dynamic Host Configuration Protocol) is a network management protocol used to automatically assign IP addresses and other network parameters to devices on a LAN.
        
- What network configurations does DHCP automate for individual hosts?
    
    - Private IP address, subnet mask, default gateway, DNS server, IP address lease duration, and other servers' IP addresses like FTP and NTP servers.
        
- What are the two main components of DHCP infrastructure?
    
    - DHCP server (assigns IP addresses) and DHCP clients (devices receiving IP addresses).
        
- On small networks, which device usually performs DHCP server functions?
    
    - The router.
        
- What is a DHCP lease?
    
    - The amount of time for which a DHCP server assigns an IP address to a device.
        
- What happens when a DHCP lease expires?
    
    - The client must renew the lease to continue using the IP address.
        
- What is the default DHCP lease time?
    
    - Commonly 24 hours (86,400 seconds).
        
- What are the four phases of DHCP address assignment?
    
    - DHCP Discover, DHCP Offer, DHCP Request, DHCP Acknowledgment (DORA).
        
- What type of message is DHCP Discover and who sends it?
    
    - Broadcast message sent from client to discover DHCP servers.
        
- What is the destination IP address in a DHCP Discover message?
    
    - 255.255.255.255 (broadcast).
        
- What does a DHCP Offer message contain?
    
    - An offered IP address and other network info like default gateway and DNS server.
        
- Can DHCP Offer messages be sent as unicast?
    
    - Yes, depending on the client’s capability; otherwise broadcast.
        
- What is the purpose of the DHCP Request message?
    
    - Client broadcasts to request the offered IP address from a specific DHCP server.
        
- Why is DHCP Request broadcast even when the client requests a specific server?
    
    - To inform all DHCP servers which offer the client accepted.
        
- What does DHCP Acknowledgment (Ack) signify?
    
    - Server confirms the client can use the requested IP address.
        
- What is the DHCP Release message used for?
    
    - Client informs the server it no longer needs the assigned IP address.
        
- What is a DHCP Nak message?
    
    - Negative Acknowledgment sent by server indicating the client’s IP address is invalid or lease expired.
        
- What is a DHCP Decline message?
    
    - Message from client to server indicating the offered IP address is already in use.
        
- Why is DHCP relay used in large networks?
    
    - To forward DHCP broadcast messages from clients in different subnets to a centralized DHCP server.
        
- How does a DHCP relay agent forward messages?
    
    - Converts client broadcasts to unicasts directed to the DHCP server.
        
- What Cisco IOS command shows current DHCP bindings?
    
    - `show ip dhcp binding`
        
- What command displays configured DHCP pools on a Cisco device?
    
    - `show ip dhcp pool`
        
- How do you exclude addresses from being assigned by DHCP?
    
    - `ip dhcp excluded-address <start-ip> <end-ip>`
        
- How do you create a DHCP pool on a Cisco router?
    
    - `ip dhcp pool <pool-name>`
        
- How do you specify the network and subnet mask for a DHCP pool?
    
    - `network <network-address> <subnet-mask>`
        
- How do you configure the DNS server for DHCP clients?
    
    - `dns-server <dns-ip-address>`
        
- How do you set the default gateway for DHCP clients?
    
    - `default-router <gateway-ip-address>`
        
- How do you configure the DHCP lease time?
    
    - `lease <days> <hours> <minutes>`
        
- How do you configure a DHCP relay agent on a router interface?
    
    - Enter interface config mode and use `ip helper-address <dhcp-server-ip>`
        
- Can you assign a fixed IP address to a specific client in DHCP?
    
    - Yes, by configuring a manual binding with `host <ip> <mask>` and `client-identifier <mac-address>` in the DHCP pool.
        
- Can the same DHCP pool be used for both manual bindings and dynamic IP allocation?
    
    - No, manual bindings and dynamic allocations require separate DHCP pools.
## Quiz

1. What is the correct order of messages when a  DHCP client gets an IP address from a server?

	- a. Request - Discover - Offer - Ack
	- b. Discover - Offer - Request - Ack
	- c. Discover - Ack - Request - Offer
	- d. Offer - Request - Discover - Ack

2. Which of the following Windows command prompt commands will cause a PC to broadcast a DHCP Discover message?
	- a. `ipconfig /dhcp`
	- b. `ipconfig /dhcpdiscover`
	- c. `ipconfig /release`
	- d. `ipconfig /renew`

3. Examine the following DHCP Offer message that Server 1 sent to R2. What destination IP address did Server 1 send it to?
	- a. `0.0.0.0`
	- b. `192.168.10.1`
	- c. `192.168.10.10`
	- d. `255.255.255.255`

![[DHCP_message.png]]

4. Which of the following DHCP messages can be sent using unicast? (select all that apply)
	- a. DHCP Ack
	- b. DHCP Discover
	- c. DHCP Release
	- d. DHCP Request
	- e. DHCP Offer

5. In which of the following situations would you configure a router as a DHCP relay agent?
	- a. When the router is not a DHCP server, there are DHCP clients in the router's connected LAN, and there are no other DHCP server in the connected LAN.
	- b. When the router is a DHCP server, there are DHCP clients in the router's connected LAN, and there is no other DHCP server in the connected LAN.
	- c. When the router is not a DHCP server, there are no DHCP clients in the router's connected LAN, and there are no other DHCP server in the connected LAN.
	- d. When the router is a DHCP server, there are DHCP clients in the router's connected LAN, and there is another DHCP server in the connected LAN.

6. Boson ExSim. You want to configure your Cisco router to provide IP addresses to the computers on your network. The IP addresses should be assigned from the `192.168.1.0/26` address range. Which of the following commands should you issue? (Select 2 choices.)
	- a. `network 192.168.1.0 255.255.255.192`
	- b. `dhcp pool 1`
	- c. `ip address dhcp`
	- d. `ip dhcp pool 1`
	- e. `host 192.168.1.0 255.255.255.192`
	- f. `network 192.168.1.0 0.0.0.63`

| Question | Answer           |
| -------- | ---------------- |
| `1.`     | `b.`             |
| `2.`     | `d.`             |
| `3.`     | `d.`             |
| `4.`     | `a.`, `c.`, `e.` |
| `5.`     | `a.`             |
| `6.`     | `d.`, `a.`       |
