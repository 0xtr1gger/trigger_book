---
created: 15-02-2026
---
## Named pipes

>A **[named pipe](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipes)** is Inter-Process Communication (IPC) mechanism implemented by the Windows I/O subsystem and exposed through the Win32 API. It's a **kernel-managed communication channel** that allows two processes to exchange data using a **file-like interface**.

>[!note] Windows named pipes are conceptually similar to Unix FIFOs, but the Windows implementation is deeply integrated with the Windows object manager and security model.

- Anonymous pipes exist only between related process (such as parent and child) and can't be addressed by name. 
- **Named pipes** can be accessed by any process (subject to security checks), even *across the network*.
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
- Does the service 

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

- You can use `gci` ([`Get-ChildItem`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-childitem?view=powershell-7.5)) to list named pipes:

```powershell
gci \\.\pipe\
```

>[!example]-
>```PowerShell
>gci \\.\pipe\
>```
>![[gci_pipe.png]]

- Or simply `dir`:

```powershell
dir \\.\pipe\
```


- Or, with [`PipeList`](https://learn.microsoft.com/en-us/sysinternals/downloads/pipelist) from the Sysinternals Suite:

```powershell
pipelist.exe /accepteula 
```

>[!example]-
> ```powershell
> .\PipeList\pipelist.exe /accepteula 
> ```
> 
> ![[pipelist.png]]

- To enumerate permissions assigned to a specific named pipe, you can use [`AccessChk`](https://learn.microsoft.com/en-us/sysinternals/downloads/accesschk) from Sysinternals:

```powershell
accesschk.exe /accepteula \\.\pipe\lsass -v
```

>[!example]-
> ```powershell
> .\AccessList\accesschk.exe /accepteula \\.\Pipe\lsass -v
> ```
> 
> ![[accesschk.png]]

>[!example]-
> ```powershell
>  .\AccessChk\accesschk.exe \pipe\SQLLocal\SQLEXPRESS01 -v
> ```
> ![[accesschk_sql.png]]

> [!note]+ Installation
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
> Invoke-WebRequest -Uri "http://10.10.16.71:8080/PipeList.zip" -OutFile "PipeList.zip"
> ```
> ```powershell
> Invoke-WebRequest -Uri "http://10.10.16.71:8080/AccessChk.zip" -OutFile "AccessChk.zip"
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
## References and further reading

- [`Named Pipes — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipes)
- [`Named Pipe Security and Access Rights — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-security-and-access-rights)