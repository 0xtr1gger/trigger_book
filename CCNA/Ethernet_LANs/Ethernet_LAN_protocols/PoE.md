---
created: 2025-10-31 05:33:30
tags:
  - ethernet
---
## Power over Ethernet

>**Power over Ethernet (PoE)** allows **PSE (Power Sourcing Equipment)** to provide power to **PD (Powered Devices** over an **Ethernet cable**.

- The device of power source is called **PSE (Power Sourcing Equipment)**
	- The PSE is typically a **switch**.
- The receiver device is called **PD (Power Device)** 
	- Examples of PDs include:
		- IP phones
		- IP cameras
		- WAPs (Wireless Access Points)
		- card readers
		- etc.
- A **midspan/injector PSE** is an external device added between a non-PoE switch and a PD to inject power into the Ethernet cable.

>[!note] With PoE, network switches can simultaneously transmit both power and data through a single Ethernet cable.

- The PSE receives AC power from the outlet, converts it to DC power, and supplies that DC power to the PDs.
- PDs receive less power than the PSE supplies due to power loss over the cable.

>[!important] In Cisco switches, **PoE is typically enabled by default**.

- Manage PoE on an interface:

```toml
SW1(config)# power inline auto
						  never
						  static
```


## PoE standards

| Standard                     | IEEE Name         | Max Power (PSE) | Max Power (PD) | Pairs Used | Typical Devices          |
| ---------------------------- | ----------------- | --------------- | -------------- | ---------- | ------------------------ |
| **Cisco Inline Power (ILP)** | Cisco proprietary | 7W              | 2W             | 2          | Legacy                   |
| **PoE (Type 1)**             | 802.3af           | 15.4W           | 12.95W         | 2          | IP phones, small WAPs    |
| **PoE+ (Type 2)**            | 802.3at           | 30W             | 25.5W          | 2          | WAPs, PTZ cameras        |
| **PoE++ (Type 3)**           | 802.3bt           | 60W             | 51W            | 4          | Video phones, LED lights |
| **PoE++ (Type 4)**           | 802.3bt           | 100W            | 71.3W          | 4          | Laptops, displays        |
| **Cisco UPoE**               | Proprietary       | 60W             | 51W            | 4          | High-power devices       |
| **Cisco UPoE+**              | Proprietary       | 90W             | 71.3W          | 4          | Even higher power needs  |
## Device detection and negotiation

Device detection and negotiation:

- **Detection Process**
	- When a device is connected to a PoE-enabled port, the PSE (switch) sends low-voltage detection signals to the PD and monitors the response to check for a valid PoE signature of the PD and determine how much power the PD needs.
	
	- If the the device needs power, the PSE supplies the power to allow the PD to boot. 
	- The PSE continues to monitor the PD and supply the required amount of power.	

>The PD may indicate its **power class** (`0`-`4` for 802.3af/at) to allow the PSE to allocate the correct power budget.


>This process is called a **hardware handshake** or **PoE handshake**; it is integrated in the switch's hardware.

>[!important] The handshake must occur **before the PD powers up**, so the PSE knows how much power to provide.

| Power class | Power Range (PD) |
| ----------- | ---------------- |
| `0`         | 0.44-12.95W      |
| `1`         | 0.44-3.84W       |
| `2`         | 3.84-6.49W       |
| `3`         | 6.49-12.95W      |
| `4`         | 12.95-25.5W      |

>[!important] Devices may change their class dynamically as their power consumption requirements change (e.g., a phone with a screen that turns on/off).

>[!note] Another way to negotiate the power is through [[CDP_LLDP|LLDP]].
## Power policing

>**Power policing** is a feature on Cisco devices that monitors and controls real-time power consumption of PDs.

>The allocated maximum power draw is called the **cutoff power value**.

- Check power-policing configuration on an interface:

```toml
SW1# show power inline police g0/0
```

Configure power-policing on an interface:

- **`power inline police`: default, error-disabled mode**
	- In case of power violations, the interface enters the **error-disabled state**, which effectively shuts down the port.
	- A **Syslog message** is issued.
	- Equivalent to `power inline police action errdisable`.

```toml
SW1(config-if)# power inline police
```

```toml
SW1(config-if)# power inline police action errdisable
```

>[!note]+ Recovering from the error-disabled state
> - An interface in an error-disabled state will remain shut down until either:
> 	- It is manually re-enabled by an administrator (`shutdown`, then `no shutdown`).
> 	- It is automatically re-enabled with auto error-recovery mechanism.

- Enable error-disable auto recovery for inline power:

```toml
SW1(config)# errdisable recovery cause inline-power
```

>[!note]+ On Cisco PoE-capable switches, 
> - **Error-disable detection** for inline power is **enabled by default**.
> - **Error-disable auto recovery** for inline power is **not enabled by default**.

- **`power inline police action log`: log message + restart**
	- If the PD attempts to draw more power than the cutoff, the interface **restarts**, and a **Syslog message** is issued.
	- Interface restart will typically cause an interface to re-negotiate its power requirements.

```toml
SW1(config-if)# power inline police action log
```


## Flashcards

- How the device that serves as a source of DC power is called?
	- PSE (Power Sourcing Equipment)

- PSE
	- Power Souring Equipment — the source of DC power

- How the power receiver device is called? 
	- PD (Power Device)

- PD
	- Power Device — the receiver of DC power

- Midspan/injector PSE
	- An external device added between a non-PoE switch and a PD to inject power into the Ethernet cable.

- PoE (Type 1) standard
	- 802.3af

- PoE (Type 1) maximum power
	- 15.4W

- PoE+ (Type 2) standard
	- 802.3at

- PoE+ (Type 2) maximum power
	- 30W

- PoE++ (Type 3) standard
	- 802.3bt

- PoE++ (Type 3) maximum power
	- 60W

- PoE++ (Type 4) standard
	- 802.3bt

- PoE++ (Type 4) maximum power
	- 100W

- Cisco UPoE maximum power
	- 60W

- Cisco UPoE+ maximum power
	- 90W

- Minimum required cable standard for PoE
	- Cat5, Cat6a for UPoE

- Command to enable power policing with the default settings on an interface
	- `SW(config-if)# power inline police` or `SW(config-if)# power inline police action errdisable`