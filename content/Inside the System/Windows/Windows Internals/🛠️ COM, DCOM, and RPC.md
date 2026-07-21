---
created: 2026-07-20
tags:
  - Windows
status: draft
---
## COM (Component Object Model)

> **COM (Component Object Model)** is a binary interface standard for inter-process communication (IPC) and object interaction in Windows systems.

- More precisely, COM is a **low-level ABI (Application Binary Interface) standard**. It defines how software components expose functionality to other components — without either side needing to know the other's implementation or internal structure.
- COM enforces **language-agnostic interoperability**; a C++ component, a .NET wrapper, and a scripting client can all interact via COM.

> [!note] COM was introduced in the early 1990s and remains deeply embedded in Windows to this day.

### Key terms

> A **COM object** is a runtime instance of a COM class that exposes one or more COM interfaces.

- Internal implementation is opaque; a COM object is a black box.
- Interaction happens only via interface pointers, never directly.
---
> A **[COM interface](https://learn.microsoft.com/en-us/windows/win32/learnwin32/what-is-a-com-interface-)** is a strongly-typed contract that consists of a set of methods a COM object exposes.

- Each interface is identified by an **IID (Interface Identifier)**.
- All interfaces inherit from [`IUnknown`](https://learn.microsoft.com/en-us/windows/win32/api/unknwn/nn-unknwn-iunknown).
---
> A **[COM class](https://learn.microsoft.com/en-us/windows/win32/com/com-class-objects-and-clsids)** defines how to instantiate a COM object and which interfaces it exposes.

- Each COM class is uniquely identified by a **CLSID (Class Identifier)**, a 128-bit GUID.
- CLSIDs are stored in the Windows Registry under:

```
HKEY_LOCAL_MACHINE\SOFTWARE\Classes\CLSID\{CLSID-GUID}
```
---
> A **COM server** is a binary that implements one or more COM classes.

- A COM server can be:
	- **In-process server (DLL)** — Loaded into the client process; no IPC overhead.
	- **Out-of-process server (EXE)** — Runs in a separate process; communication via RPC.

> [!important] Out-of-process COM servers commonly run as **`SYSTEM`**, which makes them attractive targets for privilege escalation techniques such as [[JuicyPotato]].

### COM activation

When a client requests a COM object, the **Service Control Manager (`SCM`)** component inside **`RPCSS`** handles the activation:

1. The client calls a COM activation API (e.g., `CoCreateInstance()`, `CoGetInstanceFromIStorage()`).
2. `RPCSS` looks up the CLSID in the registry to find the associated server binary.
3. `RPCSS` launches the server process (if out-of-process) and returns an interface pointer to the client.

> **`RPCSS` (Remote Procedure Call Sub-System)** is a `SYSTEM`-level service responsible for handling COM activation requests, managing the RPC Endpoint Mapper, and coordinating communication between COM clients and servers.

> [!note] Because `RPCSS` runs as `SYSTEM` and is responsible for authenticating to COM servers during activation, it becomes the source of the privileged token in potato-style attacks.

### Marshaling and `OBJREF`

When a COM object reference needs to cross a process or machine boundary, it must be **marshaled** — serialized into a transferable format.

> An **OBJREF (Object Reference)** is a marshaled representation of a COM interface pointer. It contains enough information for a remote client to locate and connect to the object's server.

- An `OBJREF` typically includes:
	- The **OXID (Object Exporter ID)** — identifies the specific process (object exporter) hosting the COM object.
	- The **OID (Object ID)** — identifies the specific object within that process.
	- The **IPID (Interface Pointer ID)** — identifies the specific interface on the object.
	- **Binding information** — the network endpoint (host, port, protocol) where the object's RPC server listens.

- COM supports **custom marshaling** via the `IMarshal` interface. If a COM class implements `IMarshal`, it can supply its own `OBJREF` data — including a custom endpoint address.

> [!bug] This is the mechanism [[JuicyPotato]] exploits: by supplying a custom-marshaled `OBJREF` that points to the attacker's own listener (`127.0.0.1:<attacker_port>`), the exploit redirects `RPCSS`'s activation traffic to itself.

### OXID resolution

When a client receives an `OBJREF` containing an **OXID** it hasn't seen before, it needs to resolve that OXID into a set of RPC binding strings (protocol, host, port) that tell it how to connect to the server process.

> The **OXID Resolver** is a service within `RPCSS` that maps OXIDs to their network endpoints. It listens on **port 135** (the RPC Endpoint Mapper port).

The resolution process:

1. The client extracts the OXID from the received `OBJREF`.
2. The client contacts the **OXID Resolver** on the machine specified in the `OBJREF`.
3. The OXID Resolver responds with the **RPC binding strings** for the target process.
4. The client uses these binding strings to establish an RPC connection to the server.

> [!bug] [[RoguePotato]] exploits OXID resolution by redirecting it to a remote machine running a **rogue OXID Resolver**. The rogue resolver responds with poisoned binding strings that point `RPCSS` to the attacker's local named pipe.

> [!note] In Windows 10 `1809`+, Microsoft hardened the local OXID resolution path — `RPCSS` no longer allows arbitrary port specifications in local RPC binding strings. This is what broke [[JuicyPotato]] on newer systems and why [[RoguePotato]] routes the OXID resolution through a remote machine to bypass this restriction.

## DCOM (Distributed COM)

> **DCOM (Distributed Component Object Model)** is an extension to COM that allows software components on **different Windows machines** to communicate and interact **over a network**.

- DCOM preserves the COM programming model — client code does not need to change regardless of whether the target object is local or remote.
- Under the hood, DCOM relies on **RPC** for transport, authentication, and message integrity.
- DCOM activation requests include OXID resolution, which is how the client discovers the remote server's endpoint.

## RPC (Remote Procedure Call)

> [!note]- RPC in one sentence: "Call a function that runs in another process as if it were local."

> **[RPC (Remote Procedure Call)](https://en.wikipedia.org/wiki/Remote_procedure_call)** is a communication protocol that allows one process (the **client**) to invoke subroutines in another process (the **server**) — even across machine boundaries — as if they were local function calls.

- RPC handles:
	- **Transport** — Named pipes (`ncacn_np`), TCP/IP (`ncacn_ip_tcp`).
	- **Serialization** — Marshalling/unmarshalling of parameters (NDR encoding).
	- **Authentication** — NTLM, Kerberos.
	- **Session management** — Connection lifecycle.
- RPC automatically authenticates the connecting client, creates a security context (token), and enables server-side impersonation.

> [!note]+ RPC transport protocols
> - `ncacn_ip_tcp` — RPC over TCP/IP. Used by DCOM for remote and local activation.
> - `ncacn_np` — RPC over named pipes (SMB). Used for local IPC and for services like the Endpoint Mapper.
> - `ncalrpc` — Local RPC (LPC). Fastest, limited to the same machine.
>
> DCOM defaults to TCP for remote calls. Potato attacks exploit the ability to redirect connections between these transports.

### Security context and impersonation

When an RPC client connects to a server, the RPC runtime:
1. Authenticates the client (NTLM or Kerberos exchange).
2. Creates an impersonation token representing the client on the server side.
3. Makes this token available to the server via `RpcImpersonateClient()`.

This is the mechanism exploited by potato-style attacks: by controlling the RPC/COM server endpoint, an attacker can capture the authentication exchange from a `SYSTEM`-level caller and obtain a `SYSTEM` impersonation token.

> [!note] See [[🛠️ Access tokens and impersonation]] for token mechanics and [[JuicyPotato]] for exploitation context.

## References and further reading

- [`Component Object Model (COM) — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/com/component-object-model--com--portal)
- [`What Is a COM Interface? — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/learnwin32/what-is-a-com-interface-)
- [`COM Class Objects and CLSIDs — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/com/com-class-objects-and-clsids)
- [`COM Marshaling Details — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/com/com-marshaling-details)
- [`OBJREF — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-dcom/fe6c5e46-adf8-4e34-a8de-3f756c875f31)
- [`Remote Procedure Call — Wikipedia`](https://en.wikipedia.org/wiki/Remote_procedure_call)
- [`Distributed Component Object Model — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-dcom/ba4c4d80-ef81-49b4-848f-9714d72b5c01)
