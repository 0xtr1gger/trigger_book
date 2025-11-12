---
created: 2025-09-25 10:47:53
tags:
  - IOS
  - security
---


```
            256 _
225.255.255.224
            ---
             32
             
10.10.2.0-31
        32-63
        64-95
        96-127
```

## Console port security

>The **console port** provides local, physical access to a Cisco device for initial configuration or troubleshooting.

- In IOS, the console port is referenced as **`line console 0`**.
- There;s only one console line per device.

>[!Important]+ By default, **no password is required for console access** on a Cisco IOS device. 
>Anyone with physical access can connect and control and device.

- To enter console port configuration mode:

```toml
R1(config)# line console 0
```

>[!warning] Securing the console port is critical to prevent unauthorized local access.
### Console port password

- To **configure a console port password**:

```toml
R1(config)# line console 0 # enter console configuration mode
R1(config-line)# password PASSWORD # set a password
R1(config-line)# login # require password to access the CLI
```

>[!important]+ The `password` and `login` commands
> - The `password` command sets the password for the console line.
> - The `login` command tells the device to prompt for the password on the line.
> - Without `login`, the password is ignored.

- To **verify** the console port **password** is set:

```toml
R1# show running-config | section line con 0
```
### Console port authentication via local database (username + password)

To require a **username and password** (not just a line password):

1. Create **local user account** (**Type `5`** password encryption):

```toml
R1(config)# username USERNAME secret SECRET
```

2. Configure the console to use the **local database** for authentication:

```toml
R1(config)# line console 0
R1(config-line)# login local
```

>[!note] The `login local` command tells the console to require a user to login using one of the configured usernames on the device.

>[!important] If `login local` is set, the user can no longer login with just a password set with `password`(see [[#Console port password]]). They must use both username and password.
## Privileged EXEC mode

>[!important] **Privileged EXEC mode** (`enable` mode) gives full access to device configuration.

>[!important] By default, no password is required to enter the privileged EXEC mode.
### Privileged EXEC mode password

- To configure **password for the privileged EXEC mode (plain-text, Type `0`)**:

```toml
R1(config)# enable password PASSWORD # stored in plain text (weak)
```

>[!important] A password set with the `enable password` command is stored **in plaintext** (**Type `0` encryption**). Not recommended.
### Privileged EXEC mode secret

- To configure **password for the privileged EXEC mode** but store it **encrypted (MD5 hash, Type `5`)**:

```toml
R1(config)# enable secret SECRET # stored encrypted (strong)
```

>[!important] If both `enable password` and `enable secret` are set, **`enable secret` takes precedence**.

>[!note] `enable secret` is the recommended command for securing privileged mode access because it stores the password in an encrypted form, unlike `enable password` which stores it in plain text by default.

>[!example]+ Example: `enable password` vs. `enable secret`
> ```toml
> SW1(config)# enable password CCNA
> SW1(config)# do show running-config | section enable
> enable password CCNA
> SW1(config)#
> SW1(config)# enable secret Cisco
> SW1(config)# do show running-config | section enable
> enable secret 5 $1$mERr$YlCkLMcTYWwkF1Ccndtll.
> enable password CCNA
> ```
> ![[enable_password_vs_enable_secret.png]]
### Privileged EXEC mode authentication against local database

- To configure **username and password for the privileged EXEC mode** (store the password **encrypted**, i.e., its **MD5 hash**), use the `enable secret` command:

```toml
R1(config)# username USERNAME secret SECRET # stored encrypted (strong)
```

- To configure **username and password** but store the password in **plain-text**:

```toml
R1(config)# username USERNAME password PASSWORD
```

- If you know the hash value of the password, you can **use the MD5 hash value of a password manually**:

```toml
R1(config)# username USERNAME secret 5 HASH_VALUE
```

>[!note] The `5` indicates that the password was hashed with MD5.

- To display the **hash value** of the password rather than the actual password:

```toml
R1(config)# show running-config
```
### Password encryption

Cisco IOS can store passwords in different formats:
- **Type `0`**: Plain text (default for `password` and `enable password` commands).
- **Type `5`**: MD5 hash (used by `enable secret` and `username ... secret`).
- **Type `7`**: Cisco-proprietary reversible encryption (used when `service password-encryption` is enabled).

---

- To encrypt all plaintext passwords in the configuration (**Type `7` encryption**):

```toml
R1(config)# service password-encryption
```

- All passwords previously configured with the `password` command will be encrypted.
- This command **does not affect `enable secret` or `username ... secret` passwords**, which are always encrypted with MD5 (Type `5`).

>[!note] This prevents casual observers from reading passwords in the running config but is not very secure against determined attackers.

## VTY lines

>**VTY (Virtual Teletype) Lines** are logical interfaces used to remotely access and manage network devices via SSH or Telnet.

>[!note] VTY lines do not correspond to physical ports; they only exist in the device's software.

- The number of VTY lines varies by device and IOS version. Commonly, Cisco devices have **5 VTY lines (`0` to `4`)** or **16 VTY lines (`0` to `15`)**.
- Some devices support up to `21` or more VTY lines, but `5` or `16` are typical.

>[!important] VTY lines support remote CLI access over **Telnet (unencrypted)** or **SSH (encrypted)**.
>- When a user connects to a device using a remote protocol, the device allocates a VTY line to that session.
>- Each **remote session uses its own VTY line**, so multiple administrators can work concurrently without interfering with each other.
>- If all VTY lines are in use, any additional connection attempts will be **denied** until a line frees up.

VTY lines can be configured with different security settings such as passwords, login methods, session timeouts, and ACLs (see [[ACLs]]).

### Configuration mode

- To configure VTY lines, enter **line configuration mode** with:

```toml
R1(config)# line vty 0 15
R1(config-line)# 
```

>[!note] `line vty 0 15` means that you are configuring **all lines at once**, from `0` to `15`. It's recommended for all of the VTY lines to have the same configuration.

- In the line configuration mode, you can set passwords, authentication methods, transport protocols, and access restrictions.
- Type `end` to exit configuration.


>[!tip] How VTY line configuration is displayed in `show running-config`
> 
> ```toml
> line vty 0 4
>   access-class 1 in
>   exec-timout 5 0
>   login-local
>   transport input telnet
> line vty 5 15
>   access-class 1 in
>   exec-timeout 5 0
>   login local
>   transport input telnet
> ```
### VTY line passwords

- To configure **password for a VTY line**:

```toml
R1(config)# line vty 0 4
R1(config-line)# password PASSWORD
R1(config-line)# login
```


>[!important]+ The `password` and `login` commands
> - The `password` command sets the password for the line (console, VTY, aux).
> - The `login` command tells the device to prompt for the password on that line.
> - Without `login`, the password is ignored.
### VTY line authentication against local database

To require a **username and password** (not just a line password):

1. Create **local user account** (**Type `5`** password encryption):

```toml
R1(config)# username USERNAME secret SECRET
```

2. Configure the VTY line to use the **local database** for authentication:

```toml
R1(config)# line vty 0 4
R1(config-line)# login local
```

>[!note] The `login local` command tells the VTY line to require a user to login using one of the configured usernames on the device.

>[!important] If `login local` is set, the user can no longer login with just a password set with `password`(see [[#Console port password]]). They must use both username and password.

>[!note]+ Additional commands
> 
> - **`login block-for`**: Delays login attempts after multiple failed tries to mitigate brute force attacks.
> - **`login delay`**: Adds delay between login attempts.
> - **`login quiet-mode`**: Restricts login attempts and limits access to console only during attack mitigation.
### Console session timeout

- To automatically log out idle console sessions after the specified period of inactivity:

```toml
R1(config-line)# exec-timeout MINTUES SECONDS 
```


- For example, to set idle timeout to 3 minutes and 30 seconds:

```toml
R1(config-line)# exec-timeout 3 30 # 3 minutes, 30 seconds
```

- To **disable the timeout**:

```toml
R1(config-line)# exec-timeout 0 0
```

>[!important] `exec-timeout` can also be set for the console line.

## Layer 2 switch management IP address

>[!important] By default, Layer 2 switches don't perform packet routing and don't build a routing table. They are not routing-aware.

>[!important] **You can assign an IP address to an SVI (Switch Virtual Interface)** to allow remote connections to the CLI of the switch using (Telnet or SSH).

>An **SVI (Switched Virtual Interface)** is a logical, Layer 3 interface configured on a mutlilayer (Layer 3) switch that *connects a VLAN to the routing engine of the switch*. In other prods, it provides IP routing capabilities for a specific VLAN. It allows traffic to be *routed between VLANs* by providing a default gateway for each VLAN.

To configure a management IP address on a switch:

1. Assign an **IP address** to an **SVI** (in the same way as you would do on a multilayer switch):

```toml
SW1(config)# interface vlan1
SW1(config-if)# ip address 192.168.1.253 255.255.255.0
SW1(config-if)# no shutdown # enable the interface (if necessary)
SW1(config-if)# exit 
```

2. Configure the **default gateway**:

```toml
SW1(config)# ip default-gateway 192.168.1.254
```

## SSH

>**SSH (Secure Shell)** is a cryptographic network protocol that allows to securely access remote devices over an insecure network, such as the Internet.

- **SSH (Secure Shell)**, was developed in 1995 to replace less secure protocols like Telnet.    
- SSH version 1 (SSHv1) was developed in 1995 to replace insecure protocols like Telnet.
- SSHv2, a major revision on SSHv1, was released in 2006.
- If the device supports both SSHv1 and SSHv2, it is said to run 'version 1.99'
    - This version number does not reflect a historical software revision, but a method to identify backward compatibility.
- SSH provides security features such as data encryption and authentication.
- SSH server listens on the **TCP port `22`**.

>[!important] In order for SSH to be enabled on a Cisco device, the device must be running a **K9 IOS image**, which provides cryptographic functionality.
>Use the `show version` command to display the version of the IOS running.
### Prerequisites

- Device must have a **hostname** configured (other than the default `Router`).
- Device must have a **domain name** configured.
- **RSA keys** must be generated for encryption.
- **Local user accounts** must be created for SSH authentication.
- **VTY lines** must be configured to accept **SSH only**.

- (Optional) SSH version 2 is recommended for better security.

>[!note] No hostname error
>If you try issuing the `crypto key generate rsa` command without having configured a hostname of the router to something other than the default `Router`, you're most likely to receive the `Please define a hostname other than Router` message.

>[!note] No domain name error
>If you try issuing the `crypto key generate rsa` command without having configured a domain name first, you're most likely to receive the `Please define a domain-name first` message.
### Configuring SSH on VTY lines

To configure SSH for VTY lines on a Cisco router:

1. Configure a **hostname** for a router (other than the default `Router`):

```toml
Router(config)# hostname HOSTNAME # hostname R1
```

2. Configure a **domain name** for the router:

```toml
R1(config)# ip domain-name DOMAIN_NAME
```

3. **Generate an RSA key pair** for the router:

```toml
R1(config)# crypto key generate rsa
```

>[!note]
>The **`crypto key generate rsa`** command will **automatically enable SSH on a router**.

>[!note]
>You can set RSA key size with the `crypto key generate rsa modulus 2048` command (`2048` bits in this case).

4. **Configure local user accounts** for SSH authentication:

```toml
R1(config)# username admin privilege 15 secret SECRET
```

5. **Configure VTY lines to use SSH**:

```toml
R1(config)# line vty 0 15
R1(config-line)# login local # forces use of local database
R1(config-line)# transport input ssh # disables Telnet, allows only SSH
R1(config-line)# exit
```

6. **Configure SSH control parameters**:

```toml
R1(config)# ip ssh timeout 60 # SSH negotiation timeout (seconds)
R1(config)# ip ssh authentication-retries 3 # max password attempts
```

7. Save the configuration:

```toml
R1(config)# write memory
```


>[!important] Summary: SSH configuration
>1. Configure **hostname**: `SW1(config)# hostname HOSTNAME`
> 2. Configure **DNS name**: `SW1(config)# ip domain name DOMAIN_NAME`
> 3. Generate **RSA key pair**: `SW1(config)# crypto key generate rsa`
> 4. Configure and enable **password**: `SW(config)# enable secret SECRET`
> 5. Enable only **SSHv2**: `SW1(config)# ip ssh version 2`
> 6. Configure **VTY lines**: `SW(config)# line vty 0 15`
> 7. **Enable SSH connections**: `SW(config-line)# transport input ssh`

```toml
Router> enable
Router# configure terminal
Router(config)# hostname Router1
Router1(config)# ip domain-name example.com
Router1(config)# crypto key generate rsa modulus 2048
Router1(config)# ip ssh version 2
Router1(config)# username admin privilege 15 secret AdminPass123
Router1(config)# line vty 0 4
Router1(config-line)# login local
Router1(config-line)# transport input ssh
Router1(config-line)# exit
Router1(config)# write memory
```
#### `show` commands

- To **show SSH configuration**:

```toml
SW1# show ip ssh
```

- To **show Cisco IOS version**:

```toml
SW# show version
```

>[!note] IOS images that support SSH will have `K9` in their name

>[!note] Cisco exports *NPE (No Payload Encryption)* IOS images to countries that have restrictions on encryption technologies. Those images do not support cryptographic features such as SSH.
## Telnet

- **Telnet** (Teletype Network) was developed in 1969.    
- Telnet has been largely, almost entirely, replaced by SSH due to security.
- However SSH was developed in 1995, and Telnet had many years of use.
- Telnet sends data in plain text, **no encryption**.
- The Telnet server (the device being connected to) listens on **TCP port `23`**.

To configure Telnet:

1. Enable password:

```toml
SW(config)# enable secret ccna
```

>[!important]
>If a password isn't configured, you **won't be able to access privileged exec mode** when connecting via Telnet.

2. Configure username and password:

```toml
SW(config)# username USERNAME secret SECRET
```

3. (Optional) Configure an ACL to limit which devices can connect to the VTY lines:

```toml
SW(config)# access-list 1 permit host 192.168.2.1
```

4. Enter VTY line configuration mode:

```toml
SW(config)# line vty 0 15
```

5. Configure login and set an `exec-timeout`:

```toml
SW(config)# login local
SW(config-line)# exec-timeout MINUTES SECONDS # e.g., exec-timeout 5 0
```

6. Allow telnet connections to the device:

```toml
SW(config-line)# transport input telnet
```

7. Apply the ACL on the VTY lines:

```toml
SW(config-line)# access-class 1 in
```

>[!note]
>This means that, from now on, only the previously configured `192.168.2.1` host will be able to connect to the switch using Telnet.


| Allow connection command<br>(`SW(config-line)#`) | Description                           |
| ------------------------------------------------ | ------------------------------------- |
| `transport input telnet`                         | Only allow Telnet connection          |
| `transport input ssh`                            | Only allow SSH connections            |
| `transport input telnet ssh`                     | Allow both Telnet and SSH connections |
| `transport input all`                            | Allow all connections                 |
| `transport input none`                           | Allow no connetions                   |

## Types of lines on Cisco devices

Cisco devices provide several types of **lines** that represent different interfaces for user access and management. Each line type serves a specific purpose and supports different connection methods:

- **Console lines** (`console`, `con`)
- **Auxiliary lines** (`aux`)
- **Virtual Terminal Lines — VTY** (`vty`)
- **TTY lines** (`tty`)

| Feature                | **VTY (Virtual Teletype) lines**                                                                                                                                                             | **Console lines**                                                                                                                     |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| **Physical interface** | Logical lines, no physical interface                                                                                                                                                         | Physical serial port on the device                                                                                                    |
| **Access type**        | Remote, network-based                                                                                                                                                                        | Local, direct, OOB management                                                                                                         |
| **Line identifier**    | `line vty 0 4` (default 5 lines) <br>or `line vty 0 15` (up to 16 lines)                                                                                                                     | `line console 0`<br>(only one console line per device)                                                                                |
| **Purpose**            | Provide remote access via Telnet or SSH; allow multiple simultaneous remote sessions                                                                                                         | Direct access to the device CLI via a console cable                                                                                   |
| **Usage**              | Remote device management                                                                                                                                                                     | Initial device setup/recovery; doesn't require network connectivity                                                                   |
| **Characteristics**    | - ACLs can be applied to restrict access<br>- Multiple users can connect simultaneously<br>- Supports encrypted (SSH) and unencrypted (Telnet) connections<br>- Require network connectivity | - Always available regardless of device network state<br>- Typically slower speed<br>- Only one user can access the console at a time |

---

| Feature                | **TTY lines**                                                                                             | **Auxiliary lines**                                                                         |
| ---------------------- | --------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| **Physical interface** | Standard asynchronous serial lines                                                                        | Auxiliary port, usually an EIA/TIA-232 serial port                                          |
| **Access type**        |                                                                                                           | Local or remote via modem                                                                   |
| **Line identifier**    | `line tty <number>`                                                                                       | `line aux 0` (usually only one auxiliary line)                                              |
| **Purpose**            | Used for asynchronous terminal ports; less common on modern routers but still supported.                  | Supports modem connections for remote OOB management; can be used as a backup console port. |
| **Usage**              | May be used for dial-in access or legacy terminal connections                                             | Connect modems for dial-in access; supports asynchronous connections and modem control      |
| **Characteristics**    | - Often used in older or specialized hardware<br>- Can support modem control and asynchronous connections | - Can be used for remote access without network<br>- Supports dial-in access via modem      |

