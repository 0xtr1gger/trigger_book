---
created: 2025-10-27 03:48:43
tags:
  - protocols
---
## FTP and TFTP

>**FTP (File Transfer Protocol)** and **TFTP (Trivial File Transfer Protocol)** are industry standard protocols used to transfer files over a network. 

Both FTP and TFTP use a client-server model: clients can use FTP/TFTP to copy files to of from a server.

- These protocols are widely used in networking.
- For example, you can use FTP/TFTP to upgrade the operating system on a network device: download the newer version of IOS from a server, and then reboot the device with the new IOS image.

| FTP                                                                           | TFTP                                               |
| ----------------------------------------------------------------------------- | -------------------------------------------------- |
| Uses TCP                                                                      | Uses UDP                                           |
| TCP port `20` for data connections<br>TCP port `21` for control connections   | UDP port `69` for connectionless communication     |
| Clients can use FTP commands to perform various actions, not just copy files. | Clients can only copy files to or from the server. |
| Username/password authentication                                              | No authentication                                  |
| More complex                                                                  | Simpler                                            |
## TFTP

>**Trivial File Transfer Protocol (TFTP)** is an industry-standard protocol for file transfers, first standardized in 1981. TFTP is simpler than FTP and runs over UDP.

TFTP was first standardized in 1981. It's named *Trivial* because it's simple and has only basic features compared to FTP.

>[!important] TFTP servers listen on **UDP port `69`**.

- **No authentication**: servers will respond to **all TFTP requests**.
- **No encryption**: all data is sent in **plain text**.
- Best used in a controlled environment to transfer small files quickly.
- TFTP uses UDP, which is connectionless and doesn't provide reliability features. However, TFTP has built-in reliability (acknowledgments and retransmissions) within the protocol itself.

>[!note] TFTP reliability
>- Every TFTP data message is **acknowledged**.
>	- If the client is transferring a file to the server, the server will send Ack messages in response.
>	- If the server is transferring a file to the client, the client will send Ack messages.
>- TFTP clients and servers use **timers**: if an expected acknowledgment isn't received in time, the waiting device will re-send its previous message.
>
>TFTP uses **lock-step communication**: the client and server alternately send a message and then wait for a reply; retransmissions are sent as needed.
### TFTP file transfers

TFTP file transfers have three phases:
1. **Connection**
	- TFTP client sends a request to the server, and the server responds back, initializing the connection.

2. **Data Transfer**
	- The client and server exchange TFTP messages. One sends data, and the other sends acknowledgments. 

3. **Connection termination**
	 - After the last data message has been sent, a final acknowledgment is sent to terminate the connection.

### TFTP TID

>When the client sends the first message to the server, the destination port is UDP `69` and the source is a random ephemeral port. In TFTP, this random port is called a **Transfer Identifier (TID)**, and is used to identify the data transfer.

- The server then also selects a random TID to use as the source port when it replies, not `69`.
- When the client sends the next message, the destination port will be the server's TID, not `69`.
## FTP

- FTP was first standardized in 1971.

>[!important] FTP uses **TCP ports `20` and `21`**.

- Usernames and passwords are used for **authentication**.
- **No encryption**: all data is sent in **plain text**.

>[!tip]
>For greater security, you can also use one these two protocols:
>- **FTPS (FTP over SSL/TLS, or FTP Secure)** — upgrade to FTP 
>- **SFTP (SSH File Transfer Protocol)** — new protocol

FTP is more complex that TFTP. Not only it allows for file transfers, but also navigation across file directories and directory management, adding/removing directories, listing files, etc. The client sends **FTP commands** to the server to perform these functions.

>[!note] See [List of FTP commands — Wikipedia](https://en.wikipedia.org/wiki/List_of_FTP_commands).

### FTP connections

FTP uses two types of connections:

- **FTP control connection** (TCP port `21`)
	- Used to send FTP commands and replies.
	- The server responds with three-digit status codes in ASCII with an optional text message. 

>[!note] See [List of FTP server return codes — Wikipedia](https://en.wikipedia.org/wiki/List_of_FTP_server_return_codes).

- **FTP data connection** (TCP port `20`)
	- Established and terminated for **file and data transfer**, as needed.
### FTP modes

FTP can operate in two modes:
- **Active mode**
- **Passive mode**
#### Active mode

1. An **FTP client** opens a **control connection** to the FTP server's **TCP port `21`** to send FTP commands. 
2. The **FTP client** starts listening on an **arbitrary port** for a **data connection**. It then sends the **`PORT` command** to the server to tell the port it's listening on.
3. The **FTP server** initiates a **data connection** from its **TCP port `20`** to the client's specified port.
4. Once the data connection is established, data (files, directory listings, etc.) can be transferred from the server to client or vice versa.
5.  After the transfer is complete, the data connection is closed.


>[!important] The **client listens** for incoming TCP connections from the server on a client-specified port. The server *actively* connects back to the client for data transfers.

>[!warning] One of the biggest disadvantages of the active mode is that the client not always can listen for incoming connections because of firewalls and NAT, which often restrict outside devices to initiate connections.
#### Passive mode

1. An **FTP client** opens a **control connection** to the FTP server's **TCP port `21`** to send FTP commands. 
2. The client requests the server to listen for a data connection by sending the `PASV` command.
3. The FTP server responds with an IP address and a port number for the client to connect to (dynamic port, usually above `1023`).
4. The client then initiates a TCP connection **from its side to the server's specified port**.
5. Once the data connection is established, data (files, directory listings, etc.) can be transferred from the server to client or vice versa.
6. After the transfer is complete, the data connection is closed.

>[!important] The **server listens** on a dynamically allocated port, and the **client connects** to the server for data transfer.

>[!note]+ The problem with firewalls passive mode solves
>Passive mode overcomes the problem with firewalls and NAT: no need for the client to listen for incoming connections at all. Today, the passive mode is used much more often than active, because of the widespread implementation of firewalls.

>[!important] In the passive FTP mode, the TCP port `20` is not used at all.
## IOS file systems

>A file system is a way of controlling how data is stored and retrieved.

- To view file systems on a Cisco IOS device:

```toml
R1# show file systems
```

Types of filesystems:
- `disk`
	- Storage devices such as flash memory.
	- This is usually where the Cisco IOS file itself is stored. 
	- When the device boots up, it copies, the IOS file from flash into RAM.
- `opaque`
	- Used for internal functions.
- `nvram`
	- Internal NVRAM. 
	- The startup-config file is stored here.
- `network`
	- Represents external filesystems, e.g., external FTP/TFTP servers.

## Upgrading Cisco IOS

- To view the current version of IOS:

```toml
R1# show version
```

- To show the contents of flash:

```toml
R1# show flash
```

#### TFTP: copying files

- To copy files using TFTP:

```toml
R1# copy <source> <destination>
```

- For example:

```toml
R1# copy tftp: flash:
Address or name of remote host []? 192.168.1.1
Source filename []? c2900-universalk9-mz.SPA.155-3.M4a.bin
Destination filename [c2900-universalk9-mz.SPA.155-3.M4a.bin]?

Accessing tftp://192.168.1.1/c2900-universalk9-mz.SPA.155-3.M4a.bin....
Loading c2900-universalk9-mz.SPA.155-3.M4a.bin from 
192.168.1.1: ...
...
[OK - 33429835 bytes]

33429835 bytes copied in 4.01 secs (984598 bytes/sec)
```

### FTP: copying files

To copy files using FTP:

- Configure the FTP username/password that the device will use to authenticate to an FTP server.

```toml
R1(config)# ip ftp username cisco
R1(config)# ip ftp password cisco

R1(config)# exit
```

- Copy files from an FTP server:

```toml
R1# copy ftp: flash:
Address or name of remote host []? 192.168.1.1
Source filename []? c2900-universalk9-mz.SPA.155-3.M4a.bin
Destination filename [c2900-universalk9-mz.SPA.155-3.M4a.bin]?

Accessing ftp://192.168.1.1/c2900-universalk9-mz.SPA.155-3.M4a.bin....
Loading c2900-universalk9-mz.SPA.155-3.M4a.bin from 
192.168.1.1: ...
...
```
#### Upgrading Cisco IOS

- To upgrade the Cisco IOS from flash memory:

```toml
R1(config)# boot system flash:c2900-universalk9-mz.SPA.155-3.M4a.bin
R1(config)# exit
R1# write memory
Building configuration...
[OK]
R1# reload
Proceed with reaload? [confirm]
```

>[!warning] If you don't use the `boot system ...` command, the router will boot with the first IOS file it finds in flash.

- To delete the old version of IOS:

```toml
R1# delete flash:c2900-universalk9-mz.SPA.151-4.M4.bin
```

