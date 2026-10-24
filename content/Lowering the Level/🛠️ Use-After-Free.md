---
created: 2026-10-22
updated: 2026-10-22
---
>[!note] [`CWE-416: Use After Free`](https://cwe.mitre.org/data/definitions/416.html).

## Use-After-Free

>**Use-After-Free (UAF)** is a critical memory corruption vulnerability, classified as CWE-416, where a program continues to access or reference a memory block after it has been deallocated (freed).

- In languages with manual memory management, such as C and C++, the developer is responsible for deallocating dynamically allocated memory when it's no longer needed. 

- The stack stores local variables; their memory is managed automatically. In heap, memory is allocated dynamically, using `mallow()` in C or `new` in C++; you must release it using `free()` or `delete`, respectively. 

>[!example] For example, `malloc(100)` reserves a block of 100 bytes on the heap. Calling `free(ptr)` releases that block, but it doesn't automatically clear or invalidate every pointer that refers to it.

- **Use-After-Free** occurs when a program accesses memory after it has been freed. 
- The pointer may still contain the old address, but the program no longer owns a valid allocation there.

>[!example]+ 
> ```c
> int *p = malloc(sizeof(int));
> *p = 42;
> 
> free(p);
> printf("%d", *p);  // use-after-free
> ```
> - The final line dereferences a dangling pointer. The result is undefined behavior: the program might print `42`, print something unexpected, or crash.

- A UAF is therefore a heap bug: it arises from a mismatch between when memory is freed and when the program stops using it.
---

- A UAF occurs when a program keeps a pointer to a heap block, frees the block, and then reads or writes through that pointer afterwards.
- Because the allocator recycles freed memory, the pointer no longer refers to the original object — it refers to whatever the allocator later places at the same address.
- UAF bugs are hard to detect because they usually don't produce immediate, visible errors. The program can keep working in ordinary runs, so the bug looks absent while the application is already exploitable.

---

- UAF is a **lifecycle violation**. Given an object on the heap and a pointer `p` to it:
	- `free(p)` returns the block to the allocator but doesn't change `p`. The pointer still holds the same address.
	- From that moment, `p` is a **dangling pointer**.
	- Any later dereference of `p` is undefined behavior: it touches memory the program no longer owns.

>A **dangling pointer** is a pointer that still holds the address of a memory block that has already been freed. It's syntactically valid and non-`NULL`, but the memory it points to has been reclaimed by the allocator and may be handed out to a different object.

## UAF under the hood

### Dangling read and write

```c
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *p = malloc(sizeof(int));   /* allocate 4 bytes on the heap */
    *p = 42;                        /* store an integer in the allocated chunk */
    printf("before free: *p = %d\n", *p);

    free(p);                        /* the chunk returns to the allocator;                                           p keeps the old address */

    /* p is now a dangling pointer; 
    both lines below result in undefined behavior. */

    printf("after free:  *p = %d\n", *p);   /* use-after-free read  */
    *p = 1337;                              /* use-after-free write */
    printf("overwritten: *p = %d\n", *p);
    return 0;
}
```

- Step by step:
	1. `malloc` returns a chunk; `p` points at its usable region, and `*p` is set to `42`.
	2. `free(p)` places the chunk on a free list ([[🛠️ Memory layout of a C program#Chunks, arenas, and bins|bin]]) for reuse. It does **not** return the page to the kernel and does **not** clear `p`.
	3. `*p` after the `free` still reads and writes the same address. The program keeps running.

>[!example]- Illustrative output
> ```text
> before free: *p = 42
> after free:  *p = 1681399308
> overwritten: *p = 1337
> ```
> The read after `free` returns stale bytes (here, allocator bookkeeping left in the freed chunk), and the write still succeeds. The exact stale value varies per run and per build — this nondeterminism is why UAF bugs are unreliable to observe and easy to miss.

>[!note] Why no crash. `free()` marks a chunk reusable **within the allocator**; it usually doesn't unmap the underlying page (see [[🛠️ Memory layout of a C program#The heap in depth]]). The address stays valid to the CPU, so the dereference reads or writes memory instead of faulting. A large, `mmap`-backed allocation is the exception: `free` may unmap it, and a later access then raises `SIGSEGV`.

### Reclaiming the freed chunk

- The read above returned leftover bytes. The security problem appears when a **new allocation reuses the freed chunk** while the dangling pointer is still live. Both pointers then alias the same memory, and a write through one corrupts the object seen through the other.
- The example below stores a function pointer inside a heap object. After the object is freed, an attacker-controlled allocation of the same size lands in the recycled chunk and overwrites that function pointer:

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct session {
    void (*on_close)(void); /* function pointer invoked when the session ends */
    char user[8];
};

void logout(void)      { puts("[*] logout(): closing session normally"); }
void spawn_shell(void) { puts("[!] spawn_shell(): attacker-controlled code ran"); }

int main(void) {
    struct session *s = malloc(sizeof(struct session));
    s->on_close = logout;
    strcpy(s->user, "alice");

    free(s);        /* s is now a dangling pointer */

    /* A later allocation of the same size reuses the just-freed chunk.
       The attacker controls its contents (modelled here as raw words). */
    void **reclaim = malloc(sizeof(struct session));
    reclaim[0] = (void *)spawn_shell;   /* overwrites the bytes of s->on_close */

    s->on_close();  /* use-after-free: dispatches through the overwritten pointer */
    return 0;
}
```

- Step by step:
	1. `s` points at a `session` whose `on_close` field holds the address of `logout`.
	2. `free(s)` returns the 16-byte chunk to the allocator. `s` is now dangling.
	3. `malloc(sizeof(struct session))` requests the same size. glibc's per-thread cache (*tcache*) is last-in-first-out, so it returns **the chunk just freed** — `reclaim` and `s` now point at the same memory. See [[🛠️ Memory layout of a C program#Chunks, arenas, and bins]].
	4. `reclaim[0] = (void *)spawn_shell` writes over the first 8 bytes of that chunk, which are exactly the bytes of `s->on_close`.
	5. `s->on_close()` reads the (now overwritten) pointer and calls `spawn_shell` instead of `logout` — the program's control flow has been redirected.

>[!example]- Illustrative output
> ```text
> [!] spawn_shell(): attacker-controlled code ran
> ```

>[!important] The decisive step is 3: the allocator handing the freed chunk back to a new allocation. This is what turns a stale read into a controllable aliasing primitive. The size class and allocation order are what an attacker manipulates to make the reclaiming object land on top of the freed one.

## Impact

- **Denial of service (crash).** Dereferencing a dangling pointer into an unmapped region (for example, a freed `mmap`-backed block) raises `SIGSEGV`. UAF corruption of allocator metadata can also abort the process.
- **Information disclosure.** Reading through a dangling pointer returns whatever now occupies the chunk. If a newer object with sensitive contents (keys, session tokens, heap pointers) was placed there, the program can leak it — including pointers that defeat [ASLR](https://en.wikipedia.org/wiki/Address_space_layout_randomization).
- **Memory corruption and RCE.** Writing through a dangling pointer corrupts the object that now owns the chunk. When the freed object contains a function pointer (C) or a vtable pointer (C++), reclaiming the chunk with controlled data turns the next method or callback dispatch into attacker-controlled execution — **remote code execution**, as shown above.

>[!note] Use-after-free is one of the most common sources of exploitable bugs in large C/C++ codebases such as browsers and OS kernels, precisely because object lifetimes there are complex and a single missed reference count or early `free` creates a dangling pointer.

## Exploiting a UAF

- Practical exploitation follows a three-step primitive:
	1. **Free** a heap object while a reference to it survives (the dangling pointer).
	2. **Reclaim** the freed chunk by triggering an allocation of a matching size so that attacker-controlled data lands in it. Spraying many allocations to groom the heap raises the odds the chunk is reused as intended.
	3. **Use** the dangling pointer. The program now operates on attacker-controlled bytes through the old object's type — a **type confusion** over the shared chunk.
- The highest-value targets inside the reclaimed object are function pointers and C++ vtable pointers, because using them transfers control flow. Overwritable length fields and data pointers are used to build read/write primitives.

> [!note] A closely related bug is the **double free** ([`CWE-415`](https://cwe.mitre.org/data/definitions/415.html)): calling `free()` twice on the same pointer. It corrupts the allocator's free-list bookkeeping and, on glibc, can be escalated into *tcache poisoning* — tricking `malloc` into returning an attacker-chosen address. See [[🛠️ Memory layout of a C program#Chunks, arenas, and bins]].

## Detection

- A UAF rarely shows up in a normal run, so detection relies on instrumentation.
- **AddressSanitizer (ASan)** is a compile-time instrumentation in GCC and Clang. It surrounds allocations with redzones and holds freed chunks in quarantine, so a use-after-free is caught at the moment of access. Recompile with `-fsanitize=address` and run the binary:

```bash
gcc -fsanitize=address -g uaf.c -o uaf && ./uaf
```

- The same flag works with Clang:

```bash
clang -fsanitize=address -g uaf.c -o uaf && ./uaf
```

>[!example]- Illustrative ASan report (trimmed) for the minimal example
> ```text
> ==1628457==ERROR: AddressSanitizer: heap-use-after-free on address 0x7ba609fe0010 ...
> READ of size 4 at 0x7ba609fe0010 thread T0
>     #0 ... in main uaf.c:12
>
> 0x7ba609fe0010 is located 0 bytes inside of 4-byte region ...
> freed by thread T0 here:
>     #1 ... in main uaf.c:9
>
> previously allocated by thread T0 here:
>     #1 ... in main uaf.c:5
> ```
> The report names the access (`heap-use-after-free`, a `READ of size 4`), the line that freed the block, and the line that allocated it — the three points needed to fix the bug.

- **Valgrind (Memcheck)** detects the same bugs on an unmodified binary, with no recompilation, at the cost of much slower execution. It reports an `Invalid read`/`Invalid write` of a freed block and keeps freed blocks on a quarantine list (`--freelist-vol`) so reuse doesn't hide the error:

```bash
valgrind --leak-check=full ./uaf
```

>[!tip] Use ASan during development and in CI because it's fast enough to run the whole test suite; reach for Valgrind when you can't rebuild the target or need to inspect a release binary.

## Mitigations

- **Null the pointer after freeing it.** Setting `p = NULL` immediately after `free(p)` turns a later dereference into a deterministic `NULL` crash instead of a silent use of freed memory:

```c
free(p);
p = NULL;   /* a later *p now faults predictably instead of reading freed memory */
```

>[!warning] This only protects the one pointer you nulled. If other copies or aliases of the address exist, they remain dangling. It's a hardening habit, not a complete fix.

- **Use RAII and smart pointers in C++.** `std::unique_ptr` and `std::shared_ptr` tie an object's lifetime to ownership, and `std::weak_ptr` expresses a non-owning reference that can be checked before use — removing most manual `delete` calls where UAF originates.
- **Use memory-safe languages.** Rust's ownership and borrow checker reject use-after-free at compile time; garbage-collected languages (Java, Go, Python) free memory only once it's unreachable, so a live reference can't dangle.
- **Enable allocator and hardware defenses.** Run sanitizers in CI (see [[#Detection]]); in production, sampling detectors such as GWP-ASan and hardware tagging such as ARM **MTE** (Memory Tagging Extension) catch a fraction of UAF accesses with low overhead.

## References and further reading

- [`CWE-416: Use After Free`](https://cwe.mitre.org/data/definitions/416.html)
- [`CWE-415: Double Free`](https://cwe.mitre.org/data/definitions/415.html)
- [`Using freed memory — OWASP`](https://community.owasp.org/vulnerabilities/Using_freed_memory)

---

- [`malloc(3) — Linux manual page`](https://man7.org/linux/man-pages/man3/malloc.3.html)
- [`Malloc Internals — glibc wiki`](https://sourceware.org/glibc/wiki/MallocInternals)
- [[🛠️ Memory layout of a C program]]

---

- [`AddressSanitizer — google/sanitizers wiki`](https://github.com/google/sanitizers/wiki/AddressSanitizer)
- [`Memcheck: a memory error detector — Valgrind manual`](https://valgrind.org/docs/manual/mc-manual.html)

---

- [`Use after free — Snyk Learn`](https://learn.snyk.io/lesson/use-after-free/?ecosystem=cpp)
- [`Heap Exploitation — Dhaval Kapil`](https://heap-exploitation.dhavalkapil.com/)
- [`how2heap — shellphish`](https://github.com/shellphish/how2heap)
