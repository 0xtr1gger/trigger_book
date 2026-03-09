---
created: 03-03-2026
---
## Windows hash formats

Windows rarely stores or transmits passwords and other secrets in plain text, but rather in a **hashed format**.

Hash functions Windows uses include:
- LM hashes
- NT hashes
- DCC1 and DCC2 (Domain Cached Credentials) hashes

>[!note] In case you're not familiar with hashing, see [`Hash function — Wikipedia`](https://en.wikipedia.org/wiki/Hash_function).

### Table of contents

## LM hashes

>An **LM hash** (LM stands for [LAN Manager](https://en.wikipedia.org/wiki/LAN_Manager#Password_hashing_algorithm)) is an ancient legacy format now mostly disabled by default. 

It is generated as follows:

1. The password is converted to uppercase and encoded in the System OEM [code page](https://en.wikipedia.org/wiki/Code_page).
2. It's **`NULL`-padded or truncated to 14 bytes** (characters beyond 14 are ignored).
3. This 14-byte character sequence is split into two **7-byte halves**.
4. These values are used to create two 8-byte [DES](https://en.wikipedia.org/wiki/Data_Encryption_Standard "Data Encryption Standard") keys. The seven bytes are converted into a bit stream ([MSb](https://en.wikipedia.org/wiki/Bit_numbering#Most_significant_bit) first), and a [parity bit](https://en.wikipedia.org/wiki/Parity_bit) is inserted each 7 bits.
5. Each of the two keys is used to DES-encrypt the **constant ASCII string** — `KGS!@#$%`. This results in two 8-byte ciphertext values. 
6. These two ciphertext values are concatenated to form a 16-byte value, which is the LM hash.

This is fundamentally weak because DES itself is weak and not salted, and to add to this, uppercasing and truncation reduce password entropy. 

For modern Windows **LM hashes are usually disabled by default** (Vista/Server 2008 onward), and if a password is **≥15 characters**, no LM hash is generated at all.

>[!note] See [`Password hashing algorithm — LAN Manager, Wikipedia`](https://en.wikipedia.org/wiki/LAN_Manager#Password_hashing_algorithm). 


To crack an LM hash, you would use the **`3000` Hashcat mode**:

```bash
hashcat -m 3000 hash.txt /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt 
```

Because LM hashes split the password into halves, brute forcing can be extremely fast.
## NT hashes

>An **NT hash** is a *static password hash* of a user's password stored on Windows systems.

The NT hash is defined as follows:
1. The user's password is taken as-is.
2. The password string is encoded in **UTF‑16 Little Endian ([UTF‑16LE](https://en.wikipedia.org/wiki/UTF-16#Byte-order_encoding_schemes))**. Unlike ASCII or UTF-8, UTF-16LE represents each character as 2 bytes in _little-endian_ order.
3. The UTF-16LE byte sequence is **hashed using [MD4](https://en.wikipedia.org/wiki/MD4)**. This produces a 128-bit (16-byte) result, typically represented as 32 hex character. This is the **NT hash**.

```
NT hash = MD4( UTF-16LE(password) )
```

NT hashes are stored in the Windows SAM database for local accounts, and `NTDS.dit` for domain accounts; also, in memory of logged-on sessions (LSASS).

>[!bug] NT hashes are not salted.

So, the NT hash is the *secret key material* used by NTLM for authentication. If you know this hash, you can authenticate as the user without knowing the plaintext password — this is the basis of **[[Pass-the-Hash]]**.

>[!note] The NT hash is often incorrectly called "NTLM hash"; it's best to use call it **NT hash** to avoid confusion with network challenge responses.

To crack an NT hash, you would use the **`1000` Hashcat mode**:

```bash
hashcat -m 1000 hash.txt /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt 
```

Target hash:

```
31f87811133bc6aaa75a536e77f64314
```

```bash
hashcat -m 1000 hash.txt /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt
```

```bash
hashcat (v6.2.6) starting

OpenCL API (OpenCL 3.0 PoCL 6.0+debian  Linux, None+Asserts, RELOC, SPIR-V, LLVM 18.1.8, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
====================================================================================================================================================
* Device #1: cpu-haswell-AMD Ryzen 7 250 w/ Radeon 780M Graphics, 2184/4432 MB (1024 MB allocatable), 4MCU

Minimum password length supported by kernel: 0
Maximum password length supported by kernel: 256

Hashes: 1 digests; 1 unique digests, 1 unique salts
Bitmaps: 16 bits, 65536 entries, 0x0000ffff mask, 262144 bytes, 5/13 rotates
Rules: 1

Optimizers applied:
* Zero-Byte
* Early-Skip
* Not-Salted
* Not-Iterated
* Single-Hash
* Single-Salt
* Raw-Hash

ATTENTION! Pure (unoptimized) backend kernels selected.
Pure kernels can crack longer passwords, but drastically reduce performance.
If you want to switch to optimized kernels, append -O to your commandline.
See the above message to find out about the exact limits.

Watchdog: Temperature abort trigger set to 90c

Host memory required for this attack: 1 MB

Dictionary cache built:
* Filename..: /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt
* Passwords.: 14344391
* Bytes.....: 139921497
* Keyspace..: 14344384
* Runtime...: 2 secs

31f87811133bc6aaa75a536e77f64314:Mic@123                  
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 1000 (NTLM)
Hash.Target......: 31f87811133bc6aaa75a536e77f64314
Time.Started.....: Sat Mar  7 19:08:27 2026 (0 secs)
Time.Estimated...: Sat Mar  7 19:08:27 2026 (0 secs)
Kernel.Feature...: Pure Kernel
Guess.Base.......: File (/usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#1.........:  5000.6 kH/s (0.08ms) @ Accel:512 Loops:1 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 2111488/14344384 (14.72%)
Rejected.........: 0/2111488 (0.00%)
Restore.Point....: 2109440/14344384 (14.71%)
Restore.Sub.#1...: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#1....: NANONINO -> MeMe159
Hardware.Mon.#1..: Util: 31%

Started: Sat Mar  7 19:08:14 2026
Stopped: Sat Mar  7 19:08:28 2026
```
## DCC1 and DCC2

Windows allows **offline login for domain users**.

If a domain user logs into a workstation and later the Domain Controller becomes unavailable, Windows still allows authentication using cached credentials.

These credentials are stored locally in the registry, at:

```powershell
HKLM\SECURITY\Cache
```

Windows typically stores **the last ~10 domain logins** on the system. 

These cached values are called **Domain Cached Credentials**, or **MS-Cache v2**.

- Credential dumping tools usually output DCC2 hashes in the following format:

```
$DCC2$10240#username#hash
```

>[!important] This hash does not allow pass-the-hash style attacks.
## References and further reading
 
- [`Hash function — Wikipedia`](https://en.wikipedia.org/wiki/Hash_function)
- [`MSCash2 Algorithm — Openwall Community Wiki`](https://openwall.info/wiki/john/MSCash2)
- [`Cached and Stored Credentials Technical Overview — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/hh994565(v%3Dws.11))