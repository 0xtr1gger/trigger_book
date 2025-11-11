---
created: 2025-10-30 03:37:38
tags:
  - wireless
---
## RF and electromagnetic waves

>Wireless communication takes place over free space through the use of **Radio Frequency (RF)** signals.

>[!interesting]
> To send wireless signals, the sender applies an alternating current to an antenna. This creates electromagnetic fields which propagate out as waves.  

- Electromagnetic waves can be measured in multiple ways, such as **amplitude** and **frequency**.

>**Amplitude** is the maximum strength of an electric and magnetic fields.

>**Frequency** measures the number of up/down cycles per a given unit of time.

Frequency is typically measured in **hertz (Hz)**, where $1 Hz = 1 s^{-1}$.
- 1 kHz = $10^3$ Hz
- 1 MHz = $10^6$ Hz
- 1 GHz = $10^9$ Hz
- 1 THz = $10^{12}$ Hz

>[!interesting]+
>- **[Amplitude](https://en.wikipedia.org/wiki/Amplitude)** of the wave the maximum displacement or distance that a particle in the wave oscillates from its equilibrium position. Measured in units of distance, such as centimeters or meters. 
>- **[Frequency](https://en.wikipedia.org/wiki/Frequency)** $f$ is the number of complete cycles or oscillations of a wave per a unit of time. 

>[!note]+
>- The visible frequency range is about 400 THz to 790 THz.
>- The radio frequency range is from 30 Hz to 300 GHz.
>
>IEEE 802.11 wireless LANs use a few sections of the Ultra High and Super High frequency ranges.
>See [Radio spectrum — Wikipedia](https://en.wikipedia.org/wiki/Radio_spectrum).

### Bands and channels

Wi-Fi uses two main **bands** (frequency ranges):
- **2.4 GHz** band
	- The actual range is **2.400 GHz** to **2.4835 GHz**.
- **5 GHz** band
	- The actual range is **5.150 GHz** to **5.825 GHz**.
	- The 5 GHz band is divided into 4 smaller bands:
		- **5.150 GHz** to **5.250 GHz**
		- **5.250 GHz** to **5.350 GHz**
		- **5.470 GHz** to **5.725 GHz**
		- **5.725 GHz** to **5.825 GHz**


>[!note]
>- The **2.4 GHz** band typically provides further reach in open space and better penetration of obstacles such as walls (lower frequency ⇒ greater wavelength ⇒ waves travel over longer distances).
>- However, more devices tend to use the **2.4 GHz** band, which leads to higher interference compared to the **5 GHz** band. 
>- **Wi-Fi 6 (802.11ax)** has expanded the spectrum range to include a band in the **6 GHz** range.

| Band    | Frequency range        |
| ------- | ---------------------- |
| 2.4 GHz | 2.400 GHz - 2.4835 GHz |
| 5 GHz   | 5.150 GHz - 5.825 GHz  |
| 6 GHz   | 5.925 GHz - 7.125 GHz  |

>Each band is divided up into multiple **channels**. Devices are configured to transmit and receive traffic on one or more of these channels. 

- The 2.4 GHz band is divided into several channels, each with 22 MHz range.
- In a small wireless LAN with only a single AP, you can use any channel.
- However, in larger WLANs with multiple APs, it's important that adjacent APs don's use overlapping channels; this helps avoid interference.

>[!important] In the 2.4 GHz band, it is recommended to use channels **1, 6, and 11**. 

>[!note]+
>Outside of the North America, you could use other combinations, but for CCNA, remember 1, 6, and 11.


>[!important] WLANs with multiple APs, it's important that adjacent APs don't use overlapping channels. This helps avoid interference. 

>[!important] Acceptable wireless coverage overlap: 20-35%.

## Wireless signal coverage

The theoretical maximum throughput of IEEE 802.11g is 54 Mbps (Megabits). But the effective throughput is generally a third of that. This loss is called **wireless signal attenuation**.

Source of GIFs: http://emanim.szlab.org
#### Absorption

>**Absorption** occurs when the signal strength is reduced as it passes through a medium, such as walls, furniture, or human bodies.

- Different materials absorb signals at different rates, with some materials like wood and water being more effective at absorbing signals than others.
- A signal energy, being absorbed by a material, is converted into heat, weakening the original signal.

![[absorption.gif]]
#### Reflection

>**Reflection** occurs when a signal is reflected from, or bounced off of a material back to its source.

- This is why Wi-Fi reception is usually poor in elevators: the signal bounced off the metal and only a small percentage of the signal penetrates into the elevator.

- This can happen when a signal hits a wall, floor, or ceiling.
#### Refraction

>**Refraction** happens when a wave is bent when entering a medium where the signal travels at a different speed. 

- For example, glass and water can refract waves. 

- This happens when a signal passes through a medium with a different density, causing the direction of the wave to change. 

![[refraction.gif]]
#### Diffraction

>**Diffraction** happens when a signal encounters and obstacle and bends around it.

- This can result in blind spots behind the obstacle.
#### Scattering

>**Scattering** happens when a material causes a signal to scatter in all directions.

- Dust, smog, uneven surfaces, etc. can cause scattering.  happens when a wave is bent when entering a medium where the signal travels at a different speed. 
- For example, glass and water can refract waves. 

- Refraction happens when a signal passes through a medium with a different density, causing the direction of the wave to change. 

![[refraction.gif]]

## Half- and full-duplex

>[!important] Wireless communication channels are **half-duplex**: only one device can transmit at a time. 
>The reason for that is interference: RF signals will interfere with one another, and the signal can be corrupted or lost.

- To achieve full-duplex communication, wireless systems require two separate channels for both the transmitter and receiver can transmit and receive simultaneously.

>[!important] IEEE 802.11 WLANs are **always half-duplex** because transmissions between stations use the same frequency or channel. Only one station can transmit at any time; otherwise, collisions occur.

- The 802.11 standard does not permit full-duplex operation.