---
created: 2026-10-22
updated: 2026-10-22
---



>[!note] The sections below cover memory layout on a 64-bit Linux system (ELF executables, `glibc`). A similar model, however, broadly applies to other platforms as well; the exact tools and allocator internals differ.

## Memory layout

- When a program starts, regardless of the language it's written in, the OS creates a process and gives it a private **virtual address space**.
- The kernel and the C runtime divide this space into several **segments**, each with a defined purpose and permissions (read, write, execute).
---

- The segments are laid out across the virtual address space as shown below, with low addresses at the bottom and high addresses at the top.

```text
High addresses
  ┌───────────────────────────────┐
  │  Kernel space                 │  not accessible from user mode
  ├───────────────────────────────┤  ← top of user space
  │  Command-line arguments       │  argv[] and environ strings,
  │  and environment variables    │  set up by execve() at startup
  ├───────────────────────────────┤
  │  Stack                        │  grows ↓ toward lower addresses
  │             │                 │  local variables, parameters,
  │             ▼                 │  return addresses (LIFO frames)
  ├───────────────────────────────┤
  │           (gap)               │
  ├───────────────────────────────┤
  │  Memory-mapping region (mmap) │  shared libraries, mmap()ed files,
  │                               │  large malloc() blocks, thread stacks
  ├───────────────────────────────┤
  │           (gap)               │
  ├───────────────────────────────┤
  │             ▲                 │
  │             │                 │
  │  Heap                         │  grows ↑ toward higher addresses
  ├───────────────────────────────┤  ← program break (brk)
  │  .bss   (uninitialized data)  │  zero-initialized globals/statics
  ├───────────────────────────────┤
  │  .data  (initialized data)    │  non-zero globals/statics
  ├───────────────────────────────┤
  │  .rodata (read-only data)     │  string literals, const globals
  ├───────────────────────────────┤
  │  .text  (code)                │  machine instructions (read + exec)
  ├───────────────────────────────┤
  │  reserved / unmapped          │  catches NULL-pointer dereferences
  └───────────────────────────────┘
Low addresses (0x0)
```

| Segment | Permissions | Contents |
| --- | --- | --- |
| `.text` | read, execute | Compiled machine instructions |
| `.rodata` | read | String literals and `const` globals |
| `.data` | read, write | Globals and statics with a non-zero initial value |
| `.bss` | read, write | Globals and statics left uninitialized or set to zero |
| Heap | read, write | Dynamically allocated memory (`malloc` family) |
| mmap region | varies | Shared libraries, memory-mapped files, large allocations, thread stacks |
| Stack | read, write | Function call frames (locals, parameters, return addresses) |
| Args / environment | read | `argv[]` and `environ` strings |

> [!note] Sections vs. segments
> An ELF file is organized into **sections** (`.text`, `.rodata`, `.data`, `.bss`, …) that the linker works with. At load time the loader works with **segments** (program headers) that group sections with the same access rights into loadable units — typically one read-only/executable segment (`.text` + `.rodata`) and one read-write segment (`.data` + `.bss`). `readelf -l` shows the section-to-segment mapping. The terms are often used loosely; this note uses "segment" for a region of the running process's address space.

## Segments in detail

### Text segment

- The text segment (also called the *code segment*) stores the binary instructions of the program.
- It's mapped read-only and executable, which prevents the program from modifying its own code.
- Because it's never written to, the text segment can be shared among multiple processes running the same executable or library: the kernel maps one copy of the physical pages into each process. This is why a shared library's code costs memory only once no matter how many processes link it.

### Read-only data (.rodata)

- `.rodata` holds data that's initialized and never modified: string literals and `const`-qualified globals.
- It's mapped read-only, so writing through a pointer into it faults.
- For `char *s = "abc";`, the characters `"abc"` live in `.rodata` while the pointer `s` (if it's a global) lives in `.data`. By contrast, `char arr[] = "abc";` copies the characters into the array itself, which lives on the stack (local) or in `.data` (global).

### Initialized data segment (.data)

- `.data` stores globals and `static` variables that are given a non-zero initial value, for example `int count = 5;`.
- The initial values are stored in the executable file and copied into the segment at load time, so `.data` occupies space both on disk and in memory.

### Uninitialized data segment (.bss)

- The BSS segment (**B**lock **S**tarted by **S**ymbol, named after an operator in an early IBM 704 assembler) holds globals and statics that are left uninitialized or explicitly set to zero.
- These variables are zero-filled by the kernel when the segment is mapped, so no initial values need to be stored in the executable. `.bss` therefore occupies memory at runtime but takes essentially no space on disk — only a size field.

### Heap

- The heap is used for dynamic memory allocation at runtime through the `malloc` family, which in turn grows the heap with the `brk`/`sbrk` and `mmap` system calls.
- The heap begins just after the end of `.bss` and grows toward higher addresses (upward).
- Memory leaks accumulate on the heap; it's covered in depth under [[#The heap in depth]].

### Stack

- The stack stores the local variables, parameters, and return addresses of functions. It follows a LIFO (last-in, first-out) discipline: each function call pushes a frame and each return pops one.
- On most architectures the stack lives at high addresses and grows toward lower addresses (downward), opposite to the heap.
- The kernel allocates the stack when the process starts and extends it on demand as frames are pushed, up to a fixed limit (see [[#The stack in depth]]).

> [!note] Do the heap and stack collide?
> In the classic textbook model the heap and stack grow toward each other, and memory is "exhausted" when they meet. On Linux with virtual memory this rarely happens literally: the mmap region sits between them, and each has its own limit — `RLIMIT_STACK` for the stack, and `brk` failure (bounded by `RLIMIT_DATA`, available physical memory, and swap) for the heap. Allocation fails when a limit is hit, not when two pointers touch.

### Memory-mapping region

- The mmap region holds everything placed with `mmap(2)`: shared libraries (their `.text`, `.rodata`, and `.data`), memory-mapped files, large `malloc` blocks, and the stacks of additional threads.
- On Linux it sits between the heap and the stack. With address-space layout randomization (ASLR) enabled, its base address is randomized on each run.

### Command-line arguments and environment variables

- At the very top of the user address space, above the initial stack, the kernel places the strings of `argv[]` and the environment (`environ`), along with the argument and environment pointer arrays.
- `execve(2)` sets these up before `main` runs. They are part of the top of the stack region rather than a truly separate segment, though many diagrams draw them as their own band.

## Where C variables live

- A variable's segment is determined by its **storage duration** (how long it lives), which in C is set by where and how the variable is declared.

| Storage duration | Examples | Lives in |
| --- | --- | --- |
| Static | Globals, `static` locals, string literals | `.data` / `.bss` / `.rodata` |
| Automatic | Non-static locals, function parameters | Stack |
| Allocated | `malloc`, `calloc`, `realloc` results | Heap (or mmap region for large blocks) |
| Thread | `_Thread_local` / `__thread` variables | Thread-local storage (TLS) |

- A global or `static` variable with a non-zero initializer goes to `.data`; one left uninitialized or set to zero goes to `.bss`.
- The linker exports three symbols that mark the boundaries: `&etext` (end of text), `&edata` (end of initialized data), and `&end` (end of uninitialized data, i.e. the start of the heap). They're declared via `extern char etext, edata, end;` and documented in `end(3)`.

## Inspecting the layout

### Static inspection (the executable on disk)

| Tool | Purpose |
| --- | --- |
| `size a.out` | Print the byte sizes of the text, data, and bss segments. |
| `nm a.out` | List symbols and the segment each belongs to. |
| `readelf -S a.out` | Show the ELF section headers (`.text`, `.data`, `.bss`, `.rodata`, …). |
| `readelf -l a.out` | Show the program headers and the section-to-segment mapping. |
| `objdump -h a.out` | Dump section headers with sizes and file offsets. |
| `objdump -d a.out` | Disassemble the text segment. |

- `size` reports the three classic segments:

```bash
size a.out
```

> [!example]- Illustrative `size` output
> ```text
>    text    data     bss     dec     hex filename
>    1998     640       8    2646     a56 a.out
> ```
> In the Berkeley format shown here, the `text` column counts read-only loadable sections (`.text` and `.rodata`), `data` counts the writable initialized section (`.data`), and `bss` counts the uninitialized section. Because `.bss` has no stored contents, growing a zero-initialized global increases the `bss` figure without enlarging the file.

- `nm` tags each symbol with a letter identifying its segment:

| Letter | Section |
| --- | --- |
| `T` / `t` | Text (code) |
| `D` / `d` | Initialized data (`.data`) |
| `B` / `b` | BSS (`.bss`) |
| `R` / `r` | Read-only data (`.rodata`) |
| `U` | Undefined (defined in another object) |
| `W` / `w` | Weak symbol |

- Uppercase marks an external (global) symbol, lowercase a local one.

### Runtime inspection (the running process)

| Tool | Purpose |
| --- | --- |
| `cat /proc/<pid>/maps` | List the live virtual-memory regions of a running process. |
| `pmap <pid>` | Report the memory map of a running process with per-region sizes. |

- `/proc/<pid>/maps` is the authoritative view of a process's address space.
- Each line is one mapped region, with columns for the address range, permissions (`r`/`w`/`x`, and `p` private or `s` shared), file offset, device, inode, and pathname.
- Anonymous regions have no pathname; the kernel labels special ones such as `[heap]` and `[stack]`.

> [!example]- Illustrative `/proc/self/maps` excerpt
> ```text
> 563b1e2a1000-563b1e2a2000 r--p 00000000 08:03 1319001  /home/user/a.out
> 563b1e2a2000-563b1e2a3000 r-xp 00001000 08:03 1319001  /home/user/a.out
> 563b1e2a3000-563b1e2a4000 r--p 00002000 08:03 1319001  /home/user/a.out
> 563b1e2a5000-563b1e2a6000 rw-p 00003000 08:03 1319001  /home/user/a.out
> 563b1f8c0000-563b1f8e1000 rw-p 00000000 00:00 0        [heap]
> 7f3c9a000000-7f3c9a028000 r-xp 00000000 08:03  917505  /usr/lib/libc.so.6
> 7ffd3c8d6000-7ffd3c8f7000 rw-p 00000000 00:00 0        [stack]
> ```
> The first four lines are the executable's own segments (read-only, read+execute, read-only relro, read-write). `[heap]` and `[stack]` are the anonymous growth regions; the shared C library sits in the mmap region in between. Exact addresses change on every run when ASLR is enabled.

### A program that prints its own layout

- Taking the address of one variable from each segment and printing it reveals the ordering directly:

```c
#include <stdio.h>
#include <stdlib.h>

int       global_init   = 1;      /* .data   */
int       global_uninit;          /* .bss    */
const int global_const  = 1;      /* .rodata */

int main(void)
{
    int        local = 1;             /* stack */
    static int local_static = 1;      /* .data */
    char      *dynamic = malloc(16);  /* heap  */

    printf("text   (main)         : %p\n", (void *)main);
    printf(".rodata(global_const) : %p\n", (void *)&global_const);
    printf(".data  (global_init)  : %p\n", (void *)&global_init);
    printf(".bss   (global_uninit): %p\n", (void *)&global_uninit);
    printf("heap   (dynamic)      : %p\n", (void *)dynamic);
    printf("stack  (local)        : %p\n", (void *)&local);

    free(dynamic);
    return 0;
}
```

> [!example]- Illustrative output
> ```text
> text   (main)         : 0x5569b4e0a169
> .rodata(global_const) : 0x5569b4e0b008
> .data  (global_init)  : 0x5569b4e0e010
> .bss   (global_uninit): 0x5569b4e0e01c
> heap   (dynamic)      : 0x5569b6a2b2a0
> stack  (local)        : 0x7ffd3c8f5a4c
> ```
> The addresses confirm the ordering: text < rodata < data < bss < heap, with the stack far above. Absolute values vary per run under ASLR, but the relative ordering of the segments is stable.

## The heap in depth

- Dynamic memory is requested at runtime through the standard allocator (`malloc`, `calloc`, `realloc`, `free`). On glibc this is an implementation called **ptmalloc2**, which sits between the program and the kernel and decides how to obtain and recycle pages.
- Distinguishing a real leak from merely-retained memory requires understanding how this allocator obtains and recycles pages.

### How the allocator gets memory from the kernel

- The allocator doesn't call the kernel on every `malloc`; it obtains memory in two ways and then subdivides it:
	- `brk(2)` / `sbrk(2)` move the **program break**, the address that marks the end of the heap. Growing the break extends the heap upward; this feeds the *main arena* for small and medium requests.
	- `mmap(2)` maps fresh pages anywhere in the mmap region. The allocator uses it for large requests and for the arenas of additional threads.
- A request at or above the **mmap threshold** (`M_MMAP_THRESHOLD`, default 128 KiB) is served by a dedicated `mmap` mapping and unmapped on `free`, returning those pages to the kernel immediately. Smaller requests are carved out of an arena.

### Chunks, arenas, and bins

- The allocator hands out **chunks**: a small header (the block's size and status flags) followed by the usable region whose address `malloc` returns.
- An **arena** is a pool of memory the allocator manages. The *main arena* grows with `brk`; multithreaded programs get additional arenas backed by `mmap` so threads can allocate without contending on a single lock.
- When a chunk is freed, it isn't handed back to the kernel. It's placed on a free list — a **bin** — for reuse. glibc keeps several kinds: the per-thread cache (*tcache*, added in glibc 2.26), *fast bins*, the *unsorted bin*, *small bins*, and *large bins*. A later `malloc` of a matching size is satisfied from a bin rather than from the kernel.
- The **top chunk** is the free chunk at the high end of the heap. The allocator extends it with `sbrk` when a request can't be met from the bins, and trims it back to the kernel only when it exceeds the trim threshold (`M_TRIM_THRESHOLD`, default 128 KiB).

> [!note] Freed is not the same as returned to the OS
> `free()` marks a chunk reusable **within the allocator**; it doesn't necessarily return the pages to the kernel. A process's resident memory can therefore stay high after large amounts of memory have been freed. This is the central distinction in leak analysis: *retained* memory is still referenced by the allocator's free lists and will be reused, whereas a *leak* is a block the program has dropped every reference to and will never free, so it stays reserved for the life of the process while being unreachable and unusable.

## The stack in depth

- Each function call pushes a **stack frame** (activation record) containing the return address, the saved frame pointer of the caller, saved registers, any arguments passed on the stack, and the function's automatic (local) variables. On the x86-64 System V ABI the first six integer/pointer arguments are passed in registers, and only the rest spill onto the stack.
- The stack pointer register (`rsp`) marks the current top; the frame pointer (`rbp`), when used, anchors the current frame. A `return` unwinds the frame simply by moving the stack pointer, which is why automatic variables need no explicit free and can't be leaked in the `malloc` sense.
- The main thread's stack is bounded by `RLIMIT_STACK` (typically 8 MiB; check with `ulimit -s`). Each additional thread gets its own stack in the mmap region, sized when the thread is created.
- A **guard page** sits just below the stack. Growing the stack into it — through deep or infinite recursion, or a huge local array — raises `SIGSEGV`. This fixed boundary is the structural limit on stack size.

## References

- [brk(2) — Linux manual page](https://man7.org/linux/man-pages/man2/brk.2.html)
- [mmap(2) — Linux manual page](https://man7.org/linux/man-pages/man2/mmap.2.html)
- [malloc(3) — Linux manual page](https://man7.org/linux/man-pages/man3/malloc.3.html)
- [mallopt(3) — Linux manual page](https://man7.org/linux/man-pages/man3/mallopt.3.html)
- [end(3) — Linux manual page (etext, edata, end)](https://man7.org/linux/man-pages/man3/end.3.html)
- [proc(5) — Linux manual page (/proc/pid/maps)](https://man7.org/linux/man-pages/man5/proc.5.html)
- [elf(5) — Linux manual page](https://man7.org/linux/man-pages/man5/elf.5.html)

---

- [Malloc Internals — glibc wiki](https://sourceware.org/glibc/wiki/MallocInternals)
- [size(1) — Linux manual page](https://man7.org/linux/man-pages/man1/size.1.html)
- [nm(1) — Linux manual page](https://man7.org/linux/man-pages/man1/nm.1.html)

---

- [Anatomy of a Program in Memory — Gustavo Duarte](https://manybutfinite.com/post/anatomy-of-a-program-in-memory/)
- [A Deep Dive into Linux Memory Management — 0xtr1gger](https://medium.com/@0xtr1gger/a-deep-dive-into-linux-memory-management-understanding-virtual-memory-and-beyond-7455955bab78)
- [Memory Layout in C — Scaler Topics](https://www.scaler.com/topics/c/memory-layout-in-c/)
