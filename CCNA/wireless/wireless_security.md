---
created: 2025-10-30 03:36:55
tags:
  - security
  - wireless
---
## Wireless network security

>[!important] Because wireless signals are not contained within a wire, any device within the range of a signal can receive that traffic.
>It's very important that traffic sent between wireless clients and the AP is encrypted. 

>[!note] In wired networks, traffic is often only encrypted when sent over an untrusted network such as the Internet.

Main concepts:
- Authentication
- Encryption 
- Integrity
## Authentication methods

>[!important] All clients must be authentication before they can associate with an AP.

![[association_process.svg]]

There are multiple ways to authenticate to a wireless network:
- Password
- Username + password
- Certificates

Authentication methods used on wireless networks:

- **Open authentication**
- **WEP (Wired Equivalent Privacy)**
- **EAP (Extensible Authentication Protocol)**
	- **LEAP (Lightweight EAP)**
	- **EAP-FAST (EAP Flexible Authentication via Secure Tunneling)**
	- **PEAP (Protected EAP)**
	- **EAP-TLS (EAP Transport Layer Security)**

### Open authentication and WEP

The original 802.11 standard included two options for authentication:

- **Open authentication**
	- The client sends an authentication request, and the AP accepts it. No authentication. 
	- After the client is authenticated and associated with the AP, it's possible to require the user to authenticate via other methods before access to the network is granted.

- **WEP (Wired Equivalent Privacy)**
	- **WEP encryption is not secure and can easily be cracked.**
	- WEP is used to provide both authentication and encryption of wireless traffic.
	- For encryption, WEP uses RC4 (cracked).
	- WEP is a shared-key protocol: it requires the sender and receiver to have the same key.
	- WEP keys can be 40 bits or 104 bits in length.
	- These keys are combined with a 24-bit **IV (Initialization Vector)** to bring the total length to 64 bits or 128 bits. 

### EAP

>**EAP (Extensible Authentication Protocol)** is an authentication framework that defines a set of standards for authentication functions used by various **EAP methods**.

>[!note] EAP is integrated with 802.1X, which provides **port-based network access control**.

>[!note]+ 802.1X
>**802.1x** is used to limit network access for clients connected to LAN or WLAN until they authenticate.
>There are three main entries in 802.1X:
> There are three main entities in 802.1X:
> - **Supplicant:** The device that wants to connect to the network.
> - **Authenticator:** The device that provides access to the network (e.g., the AP or WLC).
> - **Authentication Server (AS):** The device that receives client credentials and permits or denies access (e.g., a RADIUS server).

For commonly used EAP methods are:

- **LEAP (Lightweight EAP)** — **considered vulnerable**, should not be used
	- Developed by Cisco as an improvement over WEP.
	- Clients must provide a username and password to authenticate.
	- In addition, **mutual authentication** is provided by both the client and serve sending a challenge phrase to each other.
	- **Dynamic WEP keys are used** (i.e., WEP keys are changed frequently).

- **EAP-FAST (EAP Flexible Authentication via Secure Tunneling)**
	- Developed by Cisco.
	- Consists of three phases:
		1. A PAC  (Protected Access Credential) is generated and passed from the server to the client.
		2. A secure TLS tunnel is established between the client and authentication server.
		3. Inside the secure (encrypted) TLS tunnel, the client and server communicate further to authenticate/authorize the client.

- **PEAP (Protected EAP)**
	- Like EAP-FAST, PEAP involves establishing a secure TLS tunnel between the client and server.
	- Instead of a PAC, the server has a digital certificate.
	- The certificate is also used to establish a TLS tunnel.
	- Because only the server provides a certificate for authentication, the client must still be authenticated within the secure tunnel, for example, with MS-CHAT (Microsoft Challenge-Handshake Authentication Protocol).

- **EAP-TLS (EAP Transport Layer Security)**
	-  Whereas PEAP only requires the AS to have a certificate, EAP-TLS requires a certificate on the AS and on every single client.
	- EAP-TLS is the most secure wireless authentication method, but it's more difficult to implement than PEAP because every client device needs a certificate. 
	- Because the client and server authenticate each other with digital certificates, there's no need to authenticate the client within the TLS tunnel.
	- The TLS tunnel is still used to exchange encrypted key information.
## Encryption

>[!important] Traffic sent between clients and APs should be encrypted to prevent eavesdropping.

- All devices on the WLAN use the same protocol, but the encryption keys are unique for each user.

>[!note] An AP uses a **group key** to encrypt traffic meant to be sent to all of its clients.
>All clients associated with the AP keep that key to decrypt the traffic. 

Encryption methods used commonly used in wireless networks include:
- **TKIP (Temporal Key Integrity Protocol)**
	- A temporary solution after WEP was found vulnerable (wireless hardware at that time was built to use WEP).
	- TKIP is based on WEP; it's a more secure version of WEP.
	- TKIP is used in WPA (WPA1).

- **CCMP (Counter/CBC-MAC Protocol)**
	- CCMP was developed after TKIP and is more secure.
	- It's used in WPA2.
	- To use CCMP, it must be supported by the device's hardware. Old hardware built only to use WEP/TKIP can't use CCMP.
	- **AES counter mode** is used for encryption.
	- **CBC-MAC (Cipher Block Chaining Message Authentication Code)** for integrity (MIC).

- **GCMP (Galois/Counter Mode Protocol)**
	- GCMP is more secure and efficient than CCMP (higher data throughput).
	- It's used in WPA3.
	- **AES counter mode** is used for encryption.
	- **GMAC (Galois Message Authentication Code** for integrity (MIC).

## Wi-Fi protected access

- The Wi-Fi alliance developed three WPA certifications for wireless devices:
	- WPA
	- WPA2
	- WPA3
- To be WPA-certified, equipment must be tested in authorized testing labs.
- All of the above support two authentication modes:
	- **Personal mode**
		- A PSK (Pre-Shared Key) is used for authentication. You enter a password and get authenticated. This is common in small networks.
		- The PSK itself is not sent over the air. A 4-way handshake is used for authentication, and the PSK is used to generate encryption keys.
	- **Enterprise mode**
		- 802.1X is used with an authentication server (RADIUS server).

- **WPA** certification was developed after WEP was proven to be vulnerable.
	- **TKIP** provides encryption/MIC.
	- **802.1X** authentication (Enterprise mode) or PSK (Personal mode).

- **WPA2** was released in 2004 and includes the following protocols:
	- CCMP provides encryption/MIC.
	- **802.1X** authentication (Enterprise mode) or PSK (Personal mode).

- **WPA3** was released in 2018 and includes the following protocols:
	- GCMP provides encryption/MIC.
	- **802.1X** authentication (Enterprise mode) or PSK (Personal mode).
	- WPA3 also provides several additional security features, for example:
		- **PMF (Protected Management Frames):** protects 802.11 management frames from eavesdropping and forging.
		- **SAE (Simultaneous Authentication of Equals):** protects the 4-way handshake when using Personal mode for authentication (802.1X).
		- **Forward secrecy:** prevents data from being decrypted after transmission over the air (the attacker can't capture frames and then try decrypt them later).


| Certification | Encryption/MIC                             | Authentication                                                      |
| ------------- | ------------------------------------------ | ------------------------------------------------------------------- |
| WPA           | **TKIP (Temporal Key Integrity Protocol)** | **802.1X** authentication (Enterprise mode) or PSK (Personal mode). |
| WPA2          | **CCMP (Counter/CBC-MAC Protocol)**        | **802.1X** authentication (Enterprise mode) or PSK (Personal mode). |
| WPA3          | **GCMP (Galois/Counter Mode Protocol)**    | **802.1X** authentication (Enterprise mode) or PSK (Personal mode). |

>[!important] PSK
>- The **PSK** method configures WPA or WPA2 to use the **Pre-Shared Key (PSK)** key management method. 
>	- This method requires that an administrator configure each wireless client that will connect to the network with the key that is configured on the Cisco WLC. 
>	- The **PSK** option supports key entry as either an ASCII passphrase from 8 through 63 characters in length or a key of 64 hexadecimal values. 
>
> Combining WPA or WPA2 with a PSK key management method is often known as WPA-PSK, or WPA Personal.

## Integrity

>[!important] A MIC (Message Integrity Check) is added to each message to protect integrity.

## AAA override 

>The **AAA Override** feature on a Cisco WLC can be used to configure VLAN tagging, [[QoS]], and [[ACLs]] to **individual clients** based on **RADIUS (Remote Authentication Dial-In User Service)** attributes.

- When using the AAA Override feature, the access control server, such as Cisco Identity Services Engine (ISE), should be configured with the appropriate override properties. 
- For example, you should configure the appropriate QoS-Level and VLAN-Tag attribute for each user.

>[!note] The RADIUS Change of Authorization (CoA) feature can be used to modify or terminate an already authenticated session.