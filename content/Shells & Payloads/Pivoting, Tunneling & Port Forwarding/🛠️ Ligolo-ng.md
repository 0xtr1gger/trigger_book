---
created: 2026-09-09
updated: 2026-09-20
tags:
  - pivoting
---
## Ligolo-ng

>**[Ligolo-ng](https://github.com/nicocha30/ligolo-ng)** is a lightweight and fast tool for establishing Lauer-3 tunnels using a TUN interface, without relying on SOCKS proxies).

- Instead of using a SOCKS proxy or TCP/UDP forwarders, **Logolo-ng** creates a userland network stack using [`gVisor`](https://gvisor.dev/).
- When running the _relay/proxy_ server, a **tun** interface is used, packets sent to this interface are translated, and then transmitted to the _agent_ remote network.
- This allows you to use `nmap` without the use of `proxychains`.
- On the agent side, ligolo-ng does not require administrative access.

>[!warning] Because the _agent_ is running without privileges, it's not possible to forward raw packets. When you perform a `SYN`-scan, a TCP `connect()` is performed on the agent.