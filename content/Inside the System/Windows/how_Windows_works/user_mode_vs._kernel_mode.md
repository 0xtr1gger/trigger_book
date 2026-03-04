---
created: 05-01-2026
tags:
  - how_Windows_works
  - Windows
---
## Kernel mode and user mode

### CPU rings

Privilege separation in Windows starts **below the OS**, at the **CPU architecture level**. It's implemented through **CPU privilege rings**.

>**Privilege rings** are a *hardware-enforced* security mechanism built into the CPU architecture. They were originally defined in the Intel IA-32 architecture (x86), but similar concepts exist in ARM (which uses Exception Levels, `EL0`-`EL3`).

Modern x86 CPUs define **4 privilege rings (`0`-`3`)**, but Windows uses only **Ring `0` (kernel mode)** and **Ring `3` (user mode)**:

- **Ring `0` → User mode**
	- No direct hardware access.
	- No access to kernel memory.
	- Restricted instruction set.
	- Memory is virtualized and isolated.
	- Uses **system calls** to request OS services.

>[!important]+ Privileged instructions and `#GP`  
>Certain CPU instructions can only be executed in **kernel mode (Ring `0`)**. Attempting them in user mode (Ring `3`) triggers a **General Protection Fault (`#GP`)**. Examples:
> 
> - `in` / `out`: Direct hardware I/O.
> - `cli` / `sti`: Disable/enable interrupts.
> - `lgdt` / `lidt`: Load Global/Interrupt Descriptor Table.
> - `hlt`: Halt the CPU.

- **Ring `3` → Kernel mode**
	- Full access to CPU instructions.
	- Full access to memory.
	- Direct access to hardware.
	- Ability to modify any process and bypass security boundaries.

**Why this separation matters**:
- **Isolation**: A crash in user mode (e.g., an app fault) **does not crash the entire system**. The OS can terminate the faulty process without affecting others.
- **Security**: A user-mode processes can't access other processes’ memory or kernel resources. Damage from bugs or malware is contained.

>[!important] Key idea: if user-mode code crashes, the OS should survive.

>[!note] A bug in a kernel-mode process can cause a **Blue Screen of Death (BSOD)**.

```Bash
+---------------------------+
| User Mode                 |
|---------------------------|
| Applications              |
| Win32 Subsystem           |
| .NET Runtime              |
| Services                  |
+---------------------------+
| Kernel Mode               |
|---------------------------|
| ntoskrnl.exe              |
| HAL                       |
| Device Drivers            |
| Kernel Subsystems         |
+---------------------------+
| Hardware                  |
+---------------------------+
```

## User mode

User mode hosts all **untrusted** code, including:

- **User applications**
	- Web browsers (Chrome, Firefox), text editors (Notepad, VSCode), games, scripting languages (PowerShell, Python), command-line tools (cmd.exe, Bash), etc.

- **Win32 subsystem**
	- Exposes the **Windows API** (e.g., `CreateProcess`, `ReadFile`, etc.).
	- Translates API calls into **system calls** (e.g., `NtReadFile`).
	- Key DLLs:
		- `kernel32.dll`: Core API functions.
		- `user32.dll`: GUI/window management.
		- `gdi32.dll`: Graphics.
		- `ntdll.dll`: System call stubs (bridges user/kernel mode).

>[!important] To perform privileged operations (e.g., file I/O, process creation), a user mode process must request kernel services via **system calls**.

- **.NET runtime**
	- Managed code (C#, VB.NET) executes in the **Common Language Runtime (CLR)**, which runs in user mode.

- **User-mode services**
	- Services like **Windows Update**, **Print Spooler**, or third-party services. These run as processes (e.g., `svchost.exe`) but often under the `SYSTEM` account.

>[!important] Even highly privileged accounts, such as `Administrator` and `SYSTEM`, run in **user mode**. Privileges are enforced by the kernel.
## Kernel mode

Kernel mode hosts the **trusted computing base (TCB)** of Windows:

- **`ntoskrnl.exe`** (Windows NT Kernel — the heart of Windows)
	- **Windows NT Operating System kernel** — the heart of Windows.
	- Core responsibilities:
	    - Process and thread scheduling.
	    - Memory management (paging, virtual memory).
	    - Interrupt and exception handling.
	    - System call dispatching.
	    - Security enforcement (access tokens, privileges).
	    - Object management (files, processes, threads, etc.).

- **HAL (Hardware Abstraction Layer)**
	- Abstracts hardware differences from the kernel (e.g., interrupt controllers, timers, DMA, etc.).
	- Kernel code calls HAL → HAL talks to hardware.

>[!important]+ HAL and ACPI 
>Modern Windows (10/11) has largely deprecated HAL in favor of **ACPI** and direct hardware access via drivers. HAL remains for legacy compatibility but is minimal in newer systems.

- **Device drivers**
	- Kernel-mode drivers (`.sys` files) interact directly with hardware. 
	- Examples include:
		- `ntfs.sys`: NTFS file system driver.
		- `tcpip.sys`: Networking stack.
		- `nvlddmkm.sys`: NVIDIA GPU driver.

>[!important]+ Vulnerable drivers
> Drivers is one of the **most common attack vectors for kernel privilege escalation**. Examples:
> 
> - **CVE-2021-1732**: Win32k elevation of privilege vulnerability.
> - **CVE-2020-0796**: SMBv3 "SMBGhost" vulnerability.
	
- **Kernel subsystems**
	- **Executive**: Higher-level services (e.g., I/O manager, memory manager).
    - **Microkernel**: Low-level core (e.g., context switching, interrupt handling).

## Transition from user mode to kernel mode

A user-mode process can't just "jump" into kernel code when it needs to perform a privileged operation. The transition is hardware-enforced:

1. **High-Level API Call**
    - App calls a Win32 function (e.g., `ReadFile`).

>[!example]+
> ```c
> ReadFile(hFile, buffer, bytesToRead, &bytesRead, NULL);
> ```
        
2. **Win32 Subsystem Translation**
    - The Win32 subsystem (implemented in `kernel32.dll`) translates the high-level API call into a lower-level Native API call (e.g., `NtReadFile` for `ReadFile`).

>[!example]+         
> ```c
> NTSTATUS NtReadFile(HANDLE FileHandle, ...);
> ```


3. **System call stub in `ntdll.dll`**
	- `ntdll.dll` contains the system call stubs — small functions that prepare arguments and invoke the system call.

>[!example]+
> ```Assembly
> mov eax, 0x3F       ; System call number for NtReadFile
> mov rcx, hFile      ; File handle
> mov rdx, buffer     ; Output buffer
> mov r8, bytesToRead ; Bytes to read
> mov r9, &bytesRead  ; Bytes read (output)
> syscall             ; Transition to kernel mode
> ```

>[!note]+ System call subs
>A **system call stub** is a sequence of assembly instructions that facilitates the transition from user mode to kernel mode.

4. **CPU transition**
	- The `syscall` (x86-64) or `sysenter` (x86) instruction switches the CPU from Ring `3` to Ring `0`.
	- The CPU saves its current state (registers, stack, etc.) and jumps to the kernel’s system call handler, whose address is stored in the **Model-Specific Register (MSR)** `IA32_LSTAR`.

5. **Kernel validation and execution**
	- Once in kernel mode, the OS performs several important checks before executing the requested operation: 
		- Whether the system call number is valid.
		- Whether arguments passed from the user mode are valid (that pointers are withing the user-mode address space, and that the process has enough permissions to perform the operation).
	- Once checks are passed, the kernel executes the requested operation (e.g., reading from a file, creating a process, etc.).
	
6. **Returning to the user mode**
	- The kernel sets return values (e.g., `STATUS_SUCCESS` or an error code) and updates output parameters (e.g., `bytesRead`). 
	- Then the `sysret` instruction (x86-64) or `sysexit` (x86) restores the CPU state and returns to `ntdll.dll`. The control flows back to `kernel32.dll`, and then the original application.

>[!note] Privilege escalation aims to **cross the boundary between user mode and kernel mode**.
## References and further reading

- [`(In)direct Syscalls: A journey from high to low`](https://github.com/VirtualAlllocEx/DEFCON-31-Syscalls-Workshop/wiki)