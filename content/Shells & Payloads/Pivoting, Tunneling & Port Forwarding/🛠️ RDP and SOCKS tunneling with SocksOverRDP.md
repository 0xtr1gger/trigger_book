---
created: 2026-09-05
updated: 2026-09-20
tags:
  - pivoting
---

# RDP and SOCKS Tunneling with SocksOverRDP
## RDP and SOCKS tunneling with SocksOverRDP

>[!abstract]+ Scope
>This guide details network pivoting and arbitrary TCP socket tunneling over Microsoft Remote Desktop Protocol (RDP) using SocksOverRDP. It explains the mechanics of RDP Dynamic Virtual Channels (DVC), step-by-step setup using the client-side DLL (`SocksOverRDP-Plugin.dll`) and remote server executable (`SocksOverRDP-Server.exe`), proxying Windows tooling with Proxifier, performance optimization, verification, and cleanup.

During internal penetration tests and Active Directory assessments, you frequently encounter heavily segregated Windows subnets. In these environments, perimeter firewalls and host-based Windows Defender Firewalls often block SSH (TCP/22), PowerShell Remoting / WinRM (TCP/5985/5986), and unapproved high-order ports. However, Remote Desktop (TCP/3389) is almost universally permitted between administrative jumpboxes, tier-1 management hosts, and servers.

When native transport protocols or third-party reverse proxies cannot establish outbound connections, you can tunnel arbitrary TCP and SOCKS proxy traffic directly inside an existing RDP session using [SocksOverRDP](https://github.com/nccgroup/SocksOverRDP).

---

There are often times during an assessment when we may be limited to a Windows network and may not be able to use SSH for pivoting. We would have to use tools available for Windows operating systems in these cases. [SocksOverRDP](https://github.com/nccgroup/SocksOverRDP) is an example of a tool that uses `Dynamic Virtual Channels` (`DVC`) from the Remote Desktop Service feature of Windows. DVC is responsible for tunneling packets over the RDP connection. Some examples of usage of this feature would be clipboard data transfer and audio sharing. However, this feature can also be used to tunnel arbitrary packets over the network. We can use `SocksOverRDP` to tunnel our custom packets and then proxy through it. We will use the tool [Proxifier](https://www.proxifier.com/) as our proxy server.
## How RDP virtual channels work

We can start by downloading the appropriate binaries to our attack host to perform this attack. Having the binaries on our attack host will allow us to transfer them to each target where needed. We will need:
Understanding the underlying transport mechanism clarifies why SocksOverRDP can bypass traditional network firewall restrictions:

1. [SocksOverRDP x64 Binaries](https://github.com/nccgroup/SocksOverRDP/releases)
2. [Proxifier Portable Binary](https://www.proxifier.com/download/#win-tab)
### 1. Static vs. Dynamic Virtual Channels
The Remote Desktop Protocol provides virtual channel extensions defined by Microsoft specifications:
- **Static Virtual Channels (SVC)** ([MS-RDPBCGR](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-rdpbcgr/)): A fixed pool of up to 31 virtual channels negotiated during the initial RDP connection sequence. SVCs are permanent throughout the session and share data over the single negotiated TCP/3389 stream.
- **Dynamic Virtual Channels (DVC)** ([MS-RDPEDYC](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-rdpedyc/)): Multiplexed over a single static virtual channel named `drdynvc`. DVC supports an arbitrary number of dynamically created channels without renegotiating the RDP connection. Operating system features such as audio redirection, clipboard synchronization, smart card forwarding, and PnP device redirection run as DVC plugins.

- We can look for `ProxifierPE.zip`
```text
[Attacker / Jumpbox]                                            [Compromised Target]
┌────────────────────────┐                                     ┌────────────────────────┐
│  mstsc.exe             │                                     │  TermService (svchost) │
│   └─ SocksOverRDP-     │ <═════ TCP Port 3389 (RDP) ═══════> │   └─ DVC Virtual Port  │
│      Plugin.dll        │        Multiplexed DVC Channel      │   └─ SocksOverRDP-     │
│  (Binds 127.0.0.1:1080)│                                     │      Server.exe        │
└───────────┬────────────┘                                     └───────────┬────────────┘
            │                                                              │
   Proxifier / SOCKS Client                                      TCP Forwarding Relay
            │                                                              │
            v                                                              v
   [Local Attack Tools]                                         [Internal Network / DC]
```

We can then connect to the target using xfreerdp and copy the `SocksOverRDPx64.zip` file to the target. From the Windows target, we will then need to load the SocksOverRDP.dll using regsvr32.exe.
### 2. The SocksOverRDP architecture
SocksOverRDP splits its workload into two separate components:
1. **Client plugin (`SocksOverRDP-Plugin.dll`)**:
   - Registered on the connecting Windows host (attacker machine or Windows jumpbox) via `regsvr32.exe`.
   - When the native Remote Desktop Client (`mstsc.exe`) initializes, it queries the Windows Registry (`HKCU\Software\Microsoft\Terminal Server Client\Default\AddIns` or `HKLM`) and loads the registered dynamic channel plugin.
   - The plugin opens a local TCP listening socket on `127.0.0.1:1080` (a local SOCKS proxy listener) and ties incoming SOCKS requests into the RDP DVC stream.
2. **Server service (`SocksOverRDP-Server.exe`)**:
   - Executed with administrative privileges on the remote Windows target.
   - Uses the Windows Terminal Services API (`WTSVirtualChannelOpenEx`) to bind to the custom virtual channel created by the client plugin.
   - Decapsulates SOCKS requests coming from the virtual channel, creates real outbound TCP sockets toward internal hosts on the remote subnet, and feeds response data back through the virtual channel.

#### Loading SocksOverRDP.dll using regsvr32.exe
Because all traffic travels encapsulated inside the existing RDP session packets on TCP/3389, **no additional firewall rules or listening ports are required on intermediate network firewalls**.

        cmd
`C:\Users\htb-student\Desktop\SocksOverRDP-x64> regsvr32.exe SocksOverRDP-Plugin.dll`
---

![Command Prompt showing directory listing of SocksOverRDP files. A RegSvr32 dialog confirms successful registration of SocksOverRDP-Plugin.dll.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/158/socksoverrdpdll.png)
## Required binaries and preparation

Now we can connect to 172.16.5.19 over RDP using `mstsc.exe`, and we should receive a prompt that the SocksOverRDP plugin is enabled, and it will listen on 127.0.0.1:1080. We can use the credentials `victor:pass@123` to connect to 172.16.5.19.
Obtain the compiled binaries prior to beginning the deployment:
1. [SocksOverRDP x64 Release Packages](https://github.com/nccgroup/SocksOverRDP/releases) (includes `SocksOverRDP-Plugin.dll` and `SocksOverRDP-Server.exe`).
2. [Proxifier Portable Binary](https://www.proxifier.com/download/#win-tab) (`ProxifierPE.zip` allows running a SOCKS client without requiring administrative installation).

![Command Prompt with Remote Desktop Connection to 172.16.5.19 as user 'victor'. SocksOverRDP plugin enabled, listening on 127.0.0.1:1080.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/158/pivotingtoDC.png)
---

We will need to transfer SocksOverRDPx64.zip or just the SocksOverRDP-Server.exe to 172.16.5.19. We can then start SocksOverRDP-Server.exe with Admin privileges.
## Step-by-step deployment guide

![Terminal showing Socks Over RDP by Balazs Bucsay with a channel opened over RDP.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/158/executingsocksoverrdpserver.png)
### Step 1: Register the client plugin on the jumpbox

When we go back to our foothold target and check with Netstat, we should see our SOCKS listener started on 127.0.0.1:1080.
On the machine initiating the RDP connection (your Windows attack VM or an initial Windows foothold jumpbox):

#### Confirming the SOCKS Listener is Started
Open an elevated or standard Command Prompt in the directory containing `SocksOverRDP-Plugin.dll` and register the COM DLL using `regsvr32.exe`:

        cmd
`C:\Users\htb-student\Desktop\SocksOverRDP-x64> netstat -antb | findstr 1080    TCP    127.0.0.1:1080         0.0.0.0:0              LISTENING`
```cmd
regsvr32.exe SocksOverRDP-Plugin.dll
```

After starting our listener, we can transfer Proxifier portable to the Windows 10 target (on the 10.129.x.x network), and configure it to forward all our packets to 127.0.0.1:1080. Proxifier will route traffic through the given host and port. See the clip below for a quick walkthrough of configuring Proxifier.
A Windows pop-up dialog confirms successful registration (`DllRegisterServer in SocksOverRDP-Plugin.dll succeeded`).

#### Configuring Proxifier
![Registration of SocksOverRDP-Plugin.dll via regsvr32](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/158/socksoverrdpdll.png)

![GIF showcasing the addition of a SOCKS5 server in Proxifier.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/158/configuringproxifier.gif)
---

With Proxifier configured and running, we can start mstsc.exe, and it will use Proxifier to pivot all our traffic via 127.0.0.1:1080, which will tunnel it over RDP to 172.16.5.19, which will then route it to 172.16.6.155 using SocksOverRDP-server.exe.
### Step 2: Establish the initial RDP connection

![Desktop with Socks Over RDP terminal, Proxifier showing connection to 172.16.6.155:3389, and Remote Desktop session to 172.16.6.155](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/158/rdpsockspivot.png)
Launch the native Windows Remote Desktop client (`mstsc.exe`) and connect to the target Windows host (for example, `172.16.5.19`):

#### RDP Performance Considerations
```cmd
mstsc.exe /v:172.16.5.19
```

When interacting with our RDP sessions on an engagement, we may find ourselves contending with slow performance in a given session, especially if we are managing multiple RDP sessions simultaneously. If this is the case, we can access the `Experience` tab in mstsc.exe and set `Performance` to `Modem`.
Upon connection, `mstsc.exe` loads the registered plugin DLL and displays a notification banner indicating that the SocksOverRDP plugin is active and listening on `127.0.0.1:1080`:

![Remote Desktop Connection settings window showing performance options for a 56 kbps modem. Proxifier Portable lists connections to 172.16.6.155:3389. Command Prompt displays netstat command with port 1080 listening.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/158/rdpexpen.png)
![SocksOverRDP plugin enabled notification banner](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/158/pivotingtoDC.png)

---

Note: When spawning your target, we ask you to wait for 3 - 5 minutes until the whole lab with all the configurations is set up so that the connection to your target works flawlessly.
### Step 3: Run the server executable on the target host

Transfer `SocksOverRDP-Server.exe` to the remote target host (e.g., via RDP clipboard copy-paste, drive redirection, SMB transfer, or web download).

Open an elevated Command Prompt (**Run as Administrator**) on the target host and run the server binary:

```cmd
C:\Tools\SocksOverRDP-x64> SocksOverRDP-Server.exe
```

>[!important] Administrative privileges required on target
>`SocksOverRDP-Server.exe` requires administrative privileges to open the Terminal Services virtual channel endpoint (`WTSVirtualChannelOpenEx`). If run under an unprivileged user context, the virtual channel connection will fail.

The server console confirms the channel is successfully opened over RDP:

![SocksOverRDP server executing on target host](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/158/executingsocksoverrdpserver.png)

---

### Step 4: Verify the local SOCKS listener

Return to the jumpbox/connecting host and verify that the local SOCKS listener is listening on TCP/1080:

```cmd
netstat -ano | findstr 1080
```

Expected output:
```cmd
TCP    127.0.0.1:1080         0.0.0.0:0              LISTENING       4820
```

---

### Step 5: Route tools through the tunnel using Proxifier

Because Windows command-line tools (such as MMC consoles, BloodHound / SharpHound, Mimikatz, or secondary RDP instances) lack native SOCKS proxy support, configure **Proxifier** on the jumpbox to force selected traffic through `127.0.0.1:1080`.

1. Launch `Proxifier.exe`.
2. Navigate to **Profile** > **Proxy Servers** > **Add**.
3. Configure the proxy settings:
   - **Address**: `127.0.0.1`
   - **Port**: `1080`
   - **Protocol**: `SOCKS Version 5`
4. Click **Check** to verify connectivity with the SocksOverRDP listener.

![Configuring SOCKS5 server in Proxifier](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/158/configuringproxifier.gif)

5. Configure **Proxification Rules**:
   - Create a rule directing target subnet traffic (e.g., `172.16.6.0/24` or specific remote ports like `3389, 445, 88, 389`) through the `SOCKS5 127.0.0.1:1080` proxy.
   - Leave `mstsc.exe` for the *primary* connection directed to `Direct` (to prevent an infinite loop where the initial RDP stream attempts to route through itself).

With this rule enabled, you can now launch a secondary `mstsc.exe` session or any Windows penetration testing tool directly toward deeper internal targets (e.g., `172.16.6.155`):

![Pivoting through RDP tunnel into secondary target](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/158/rdpsockspivot.png)

---

## RDP performance optimization

Because RDP sends graphical screen updates, keyboard/mouse events, and virtual channel data over the same underlying connection, running data-heavy SOCKS operations can degrade interactive responsiveness.

To minimize latency and maximize available bandwidth for tunneling:

1. In `mstsc.exe`, navigate to the **Experience** tab prior to connecting.
2. Under **Performance**, choose **Modem (56 kbps)** from the dropdown list.
3. Verify that the following features are disabled:
   - Desktop background
   - Font smoothing
   - Desktop composition
   - Show window contents while dragging
   - Menu and window animation
   - Themes

![Configuring RDP performance settings to 56 kbps modem](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/158/rdpexpen.png)

---

## Component and parameter reference

| Component | Location | Role / Syntax | Privileges Required |
| :--- | :--- | :--- | :--- |
| `SocksOverRDP-Plugin.dll` | Client / Jumpbox | Dynamic Virtual Channel client plugin. Registered via `regsvr32.exe`. Binds `127.0.0.1:1080`. | Standard User |
| `SocksOverRDP-Server.exe` | Target Server | Server-side relay daemon. Connects to the DVC and proxies TCP connections to internal subnets. | Local Administrator |
| `regsvr32.exe <path>` | Client / Jumpbox | Registers the client plugin into the Windows Registry. | Standard User |
| `regsvr32.exe /u <path>` | Client / Jumpbox | Unregisters the client plugin. | Standard User |
| `mstsc.exe /v:<host>` | Client / Jumpbox | Windows Remote Desktop client that loads registered plugins during startup. | Standard User |

---

>[!tip]+ Verification:
>1. Verify plugin registration in the Windows Registry:
>   ```cmd
>   reg query "HKCU\Software\Microsoft\Terminal Server Client\Default\AddIns\SocksOverRDP-Plugin"
>   ```
>2. Verify active SOCKS listener on the client:
>   ```cmd
>   netstat -ano | findstr 1080
>   ```
>3. Verify end-to-end proxy connectivity with PowerShell through Proxifier:
>   ```powershell
>   Test-NetConnection -ComputerName 172.16.6.155 -Port 3389
>   ```

---

>[!tip]+ Cleanup:
>To cleanly remove all components and restore the system to its baseline state:
>
>1. Terminate the server process on the remote host:
>   ```cmd
>   taskkill /F /IM SocksOverRDP-Server.exe
>   ```
>2. Delete the remote executable:
>   ```cmd
>   del C:\Tools\SocksOverRDP-Server.exe
>   ```
>3. Unregister the client plugin on the jumpbox:
>   ```cmd
>   regsvr32.exe /u SocksOverRDP-Plugin.dll
>   ```
>4. Close the RDP session and terminate Proxifier.

---

## References and further reading
- [`SocksOverRDP GitHub Repository — NCC Group`](https://github.com/nccgroup/SocksOverRDP)
- [`[MS-RDPEDYC]: Remote Desktop Protocol: Dynamic Virtual Channel Extension — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-rdpedyc/)
- [`[MS-RDPBCGR]: Remote Desktop Protocol: Basic Connectivity and Graphics Remoting — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-rdpbcgr/)
- [`Proxifier Documentation & Portable Edition`](https://www.proxifier.com/)