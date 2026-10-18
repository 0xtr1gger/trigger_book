---
created: 2026-09-03
updated: 2026-10-09
tags:
  - password_cracking
status: complete
proofread: yes
---
## Hashcat

>[Hashcat](https://hashcat.net/hashcat/) is an open-source password recovery tool designed for high-speed offline hash cracking on Linux, Windows, and macOS. It supports more than 300 hashing algorithms and uses GPU hardware acceleration through [OpenCL](https://en.wikipedia.org/wiki/OpenCL) and [CUDA](https://en.wikipedia.org/wiki/CUDA) to perform hash comparisons in parallel.

- Password cracking is performed **offline**: candidate passwords are hashed locally and then compared against the target hashes. 
- This eliminates the network latency and account lockout associated with online password brute-force attacks.

### Using `hashcat`

- Command syntax:

```bash
hashcat -a <mode> -m <hash_type> [other_options] <hash_file> [wordlist|mask]
```

| Option                | Description                                                  |
| --------------------- | ------------------------------------------------------------ |
| `-m`, `--hash-type`   | Target hash type numeric ID (e.g., `-m 1000` for NTLM). |
| `-a`, `--attack-mode` | Attack mode (`0`, `1`, `3`, `6`, `7`).            |
>[!note] For a more complete option reference, see [[#Appendix A Hashcat command-line option reference]].

- The hash file should contain **one hash per line**. Salted algorithms accept `hash:salt` pairs.
- The positional arguments following the hash file depend on the attack mode:

| Attack mode                  | Positional arguments                     |
| :--------------------------- | :--------------------------------------- |
| `0` — Straight               | `hash.txt wordlist.txt`                  |
| `1` — Combination            | `hash.txt wordlist_1.txt wordlist_2.txt` |
| `3` — Mask                   | `hash.txt MASK`                          |
| `6` — Hybrid Wordlist + Mask | `hash.txt wordlist.txt MASK`             |
| `7` — Hybrid Mask + Wordlist | `hash.txt MASK wordlist.txt`             |

## Identifying hash types

- The `-m` option specifies the target hash type by its numeric ID.
- If omitted, Hashcat attempts to detect the hash type automatically; if it finds multiple possible matches, it reports them in a table.

>[!example]-
> ```bash
> hashcat -a 0 hash.txt /usr/share/wordlists/rockyou.txt
> ```
> 
> ```bash
> hashcat (v6.2.6) starting in autodetect mode
> 
> OpenCL API (OpenCL 2.1 LINUX) - Platform #1 [Intel(R) Corporation]
> ==================================================================
> * Device #1: AMD EPYC 9575F 64-Core Processor, 3920/7905 MB (988 MB allocatable), 4MCU
> 
> OpenCL API (OpenCL 3.0 PoCL 6.0+debian  Linux, None+Asserts, RELOC, SPIR-V, LLVM 18.1.8, SLEEF, DISTRO, POCL_DEBUG) - Platform #2 [The pocl project]
> ====================================================================================================================================================
> * Device #2: cpu-skylake-avx512-AMD EPYC 9575F 64-Core Processor, skipped
> 
> The following 15 hash-modes match the structure of your input hash:
> 
>       # | Name                                                       | Category
>   ======+============================================================+======================================
>     110 | sha1($pass.$salt)                                          | Raw Hash salted and/or iterated
>     120 | sha1($salt.$pass)                                          | Raw Hash salted and/or iterated
>    4900 | sha1($salt.$pass.$salt)                                    | Raw Hash salted and/or iterated
>    4520 | sha1($salt.sha1($pass))                                    | Raw Hash salted and/or iterated
>   24300 | sha1($salt.sha1($pass.$salt))                              | Raw Hash salted and/or iterated
>     140 | sha1($salt.utf16le($pass))                                 | Raw Hash salted and/or iterated
>    4710 | sha1(md5($pass).$salt)                                     | Raw Hash salted and/or iterated
>   21100 | sha1(md5($pass.$salt))                                     | Raw Hash salted and/or iterated
>    4510 | sha1(sha1($pass).$salt)                                    | Raw Hash salted and/or iterated
>    5000 | sha1(sha1($salt.$pass.$salt))                              | Raw Hash salted and/or iterated
>     130 | sha1(utf16le($pass).$salt)                                 | Raw Hash salted and/or iterated
>     150 | HMAC-SHA1 (key = $pass)                                    | Raw Hash authenticated
>     160 | HMAC-SHA1 (key = $salt)                                    | Raw Hash authenticated
>    5800 | Samsung Android Password/PIN                               | Operating System
>     121 | SMF (Simple Machines Forum) > v1.1                         | Forums, CMS, E-Commerce
> 
> Please specify the hash-mode with -m [hash-mode].
> 
> Started: Thu Oct  8 11:45:24 2026
> Stopped: Thu Oct  8 11:45:24 2026
> ```

- To identify a hash type, you can use [`HashID`](https://github.com/psypanda/hashID):

```bash
hashid <hash>
```

>[!example]-
> ```bash
> hashid '$apr1$71850310$gh9m4xcAn3MGxogwX/ztb.'
> 
> Analyzing '$apr1$71850310$gh9m4xcAn3MGxogwX/ztb.'
> [+] MD5(APR) 
> [+] Apache MD5
> ```

- Alternatively, you can look up the hash format manually in Hashcat's list of [example hashes](https://hashcat.net/wiki/doku.php?id=example_hashes). Each entry includes the hash mode, hash name, and a sample hash.
- Output the list of example hashes to the command line to see all supported algorithms and formats:

```bash
hashcat --example-hashes | less
```

>[!example]-
> ```bash
> hashcat --example-hashes | less
> ```
> 
> ```bash
> hashcat (v6.2.6) starting in autodetect mode
> 
> Hash Info:
> ==========
> 
> Hash mode #0
>   Name................: MD5
>   Category............: Raw Hash
>   Slow.Hash...........: No
>   Password.Len.Min....: 0
>   Password.Len.Max....: 256
>   Kernel.Type(s)......: pure, optimized
>   Example.Hash.Format.: plain
>   Example.Hash........: 8743b52063cd84097a65d1633f5c74f5
>   Example.Pass........: hashcat
>   Benchmark.Mask......: ?b?b?b?b?b?b?b
>   Autodetect.Enabled..: Yes
>   Self.Test.Enabled...: Yes
>   Potfile.Enabled.....: Yes
>   Custom.Plugin.......: No
>   Plaintext.Encoding..: ASCII, HEX
> # ...
> ```

### Common hash types


| Hash mode | Algorithm / Format                  | Sample hash format                                                                                                                                                               |
| :-------- | :---------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `0`       | MD5                                 | `8743b52063cd84097a65d1633f5c74f5`                                                                                                                                               |
| `100`     | SHA1                                | `b89eaac7e61417341b710b727768294d0e6a277b`                                                                                                                                       |
| `1400`    | SHA-256                             | `127e6fbfe24a750e72930c220a8e138275656b8e5d8f48a98c3c92df2caba935`                                                                                                               |
| `1700`    | SHA-512                             | `82a9dda829eb7f8ffe9fbe49e45d47d2dad9664fbb7adf72492e3c81ebd3e29134d9bc12212bf83c6840f10e8246b9db54a4859b7ccd0123d86e5872c1e5082f`                                               |
| `500`     | md5crypt (`$1$`), MD5 (Unix)        | `$1$28772684$iEwNOgGugqO9.bIz5sk8k/`                                                                                                                                             |
| `1600`    | md5crypt (`$apr1$`), Apache         | `$apr1$<salt>$<22-char digest>`                                                                                                                                                  |
| `7400`    | sha256crypt (`$5$`), SHA-256 (Unix) | `$5$<salt>$<digest>`                                                                                                                                                             |
| `1800`    | sha512crypt (`$6$`), SHA-512 (Unix) | `$6$52450745$k5ka2p8bFuSmoVT1tzOyyuaREkkKBcCNqoDKzYiJL9RaE8yMnPgh2XzzF0NDrUhgrcLwg78xs1w5pJiypEdFX/`                                                                             |
| `1000`    | NTLM                                | `b4b9b02e6f09a9bd760f388b67351e2b`                                                                                                                                               |
| `3000`    | LM                                  | Two 16-hex-char halves; empty half is `aad3b435b51404ee`                                                                                                                         |
| `3200`    | bcrypt (`$2*$`), Blowfish (Unix)    | `$2a$05$LhayLxezLhK1LhWvKxCyLOj0j1u.Kj0jZ0pEmm134uzrQlFvQJLF6`                                                                                                                   |
| `400`     | phpass (`$P$`) — WordPress, phpBB   | `$P$<iteration char><8-char salt><22-char digest>`                                                                                                                               |
| `5500`    | NetNTLMv1 / NetNTLMv1+ESS           | `u4-netntlm::kNS:338d08f8e26de93300000000000000000000000000000000:9526fb8c23a90751cdd619b6cea564742e1e4bf33006ba41:cb8086049ec4736c`                                             |
| `5600`    | NetNTLMv2                           | `admin::N46iSNekpT:08ca45b7d7ea58ee:88dcbe4446168966a153a0064958dac6:5c7830315c7830310000000000000b45c67103d07d7b95acd12ffa11230e0000000052920b85f78d013c31cdb3b92f5d765c783030` |
| `13100`   | Kerberos 5 TGS-REP (etype 23)       | `$krb5tgs$23$_user$realm$test/spn_$63386d22d359fe42230300d56852c9eb$...`                                                                                                         |
| `18200`   | Kerberos 5 AS-REP (etype 23)        | `$krb5asrep$23$user@DOMAIN.COM:<checksum><encrypted data>`                                                                                                                       |

## Hashcat attack modes

- Hashcat supports several attack modes specified with the `-a` option:

| Mode code | Attack mode            | Description                                        |
| :-------- | :--------------------- | :------------------------------------------------- |
| `0`       | Straight               | Run a dictionary attack using a precompiled wordlist. |
| `1`       | Combination            | Concatenate words from two wordlists.              |
| `3`       | Brute-force / Mask     | Generate candidate passwords using mask patterns.  |
| `6`       | Hybrid Wordlist + Mask | Append mask patterns to wordlist candidates.       |
| `7`       | Hybrid Mask + Wordlist | Prepend mask patterns to wordlist candidates.      |

### Mode `0` — Straight (dictionary) attack

- A classic dictionary attack, often the first choice for password cracking.
- You start with a precompiled list of candidate passwords. Hashcat takes each candidate from the list and computes its hash using the target algorithm, then compares the result with the target hash. If the hashes match, the password is found.
- You can also apply transformation rules to candidate passwords, such as capitalizing, appending digits, etc. (see [[#Hashcat rules]]).

> [!tip]+ 
> - Useful wordlists:
>   - `/usr/share/wordlists/rockyou.txt` — Default password wordlist on Kali Linux and Parrot OS.
>   - [`SecLists`](https://github.com/danielmiessler/SecLists) — Collection of targeted password dictionaries.
>   - [`CrackStation`](https://crackstation.net/crackstation-wordlist-password-cracking-dictionary.htm) — Public password cracking dictionary.

- Execute a basic dictionary attack:

```bash
hashcat -a 0 -m <hash_type> hash.txt wordlist.txt 
```

```bash
hashcat -a 0 -m 1400 hash.txt ./wordlist.txt 
```

- Apply transformation rules during a dictionary attack:

```bash
hashcat -a 0 -m 1400 -r /usr/share/hashcat/rules/best64.rule hash.txt wordlist.txt
```

| Argument | Description |
| :--- | :--- |
| `-a 0` | Select Straight (dictionary) attack mode. |
| `-m 1400` | Set the target hash type to SHA-256. |
| `hash.txt` | Input file containing the target hashes. |
| `wordlist.txt` | Dictionary file containing candidate passwords. |
| `-r best64.rule` | Apply the rule set to transform wordlist entries. |

>[!example]-
> 
> ```bash
> echo -n 'unbreakable' | sha256sum | cut -f1 -d ' ' > sha256_hash
> ```
> 
> ```bash
> hashcat -a 0 -m 1400 sha256_hash /opt/useful/seclists/Passwords/Leaked-Databases/rockyou.txt
> ```
> ```bash
> hashcat (v6.2.6) starting
> 
> OpenCL API (OpenCL 3.0 PoCL 3.1+debian  Linux, None+Asserts, RELOC, SPIR, LLVM 15.0.6, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
> ==================================================================================================================================================
> * Device #1: pthread-haswell-AMD EPYC 7543 32-Core Processor, skipped
> 
> OpenCL API (OpenCL 2.1 LINUX) - Platform #2 [Intel(R) Corporation]
> ==================================================================
> * Device #2: AMD EPYC 7543 32-Core Processor, 3923/7910 MB (988 MB allocatable), 4MCU
> 
> Minimum password length supported by kernel: 0
> Maximum password length supported by kernel: 256
> 
> Hashes: 1 digests; 1 unique digests, 1 unique salts
> Bitmaps: 16 bits, 65536 entries, 0x0000ffff mask, 262144 bytes, 5/13 rotates
> Rules: 1
> 
> Optimizers applied:
> * Zero-Byte
> * Early-Skip
> * Not-Salted
> * Not-Iterated
> * Single-Hash
> * Single-Salt
> * Raw-Hash
> 
> ATTENTION! Pure (unoptimized) backend kernels selected.
> Pure kernels can crack longer passwords, but drastically reduce performance.
> If you want to switch to optimized kernels, append -O to your commandline.
> See the above message to find out about the exact limits.
> 
> Watchdog: Hardware monitoring interface not found on your system.
> Watchdog: Temperature abort trigger disabled.
> 
> Host memory required for this attack: 1 MB
> 
> Dictionary cache built:
> * Filename..: /opt/useful/seclists/Passwords/Leaked-Databases/rockyou-75.txt
> * Passwords.: 59186
> * Bytes.....: 478936
> * Keyspace..: 59186
> * Runtime...: 0 secs
> 
> 4abb806d8a2496f726198403e6e175ffbfce51054638da442cd2bd45efe0baf9:unbreakable
> 
> Session..........: hashcat
> Status...........: Cracked
> Hash.Mode........: 1400 (SHA2-256)
> Hash.Target......: 4abb806d8a2496f726198403e6e175ffbfce51054638da442cd...e0baf9
> Time.Started.....: Sun Sep  7 09:45:13 2025 (0 secs)
> Time.Estimated...: Sun Sep  7 09:45:13 2025 (0 secs)
> Kernel.Feature...: Pure Kernel
> Guess.Base.......: File (/opt/useful/seclists/Passwords/Leaked-Databases/rockyou-75.txt)
> Guess.Queue......: 1/1 (100.00%)
> Speed.#2.........:  5425.1 kH/s (0.18ms) @ Accel:512 Loops:1 Thr:1 Vec:8
> Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
> Progress.........: 22528/59186 (38.06%)
> ```

> [!tip]+
> - Press `s` anytime during an active cracking session to display current progress, hash rate, temperature, and estimated completion time.
> - Additional runtime keys: `p` — pause the session, `r` — resume a paused session, `c` — stop at the next checkpoint, `q` — quit.

### Mode `1` — Combination attack

- Mode `1` combines words from two wordlists by concatenating each entry from the first wordlist with every entry from the second wordlist.

- Execute a combination attack using two wordlists:

```bash
hashcat -a 1 -m <hash_type> hash.txt wordlist_1.txt wordlist_2.txt
```

| Option / argument | Description |
| :--- | :--- |
| `-a 1` | Select Combination attack mode. |
| `-m 0` | Set the target hash type to MD5. |
| `wordlist_1.txt` | Left-side wordlist. |
| `wordlist_2.txt` | Right-side wordlist. |

>[!example]-
> 
> 
> ```bash
> cat wordlist_1.txt
> 
> sunshine
> happy
> frozen
> golden
> ```
> 
> ```bash
> cat wordlist_2.txt
> 
> hello
> joy
> secret
> apple
> ```
> 
> ```bash
> hashid -m '19672a3f042ae1b592289f8333bf76c5'
> Analyzing '19672a3f042ae1b592289f8333bf76c5'
> [+] MD2 
> [+] MD5 [Hashcat Mode: 0]
> # ...
> ```
> 
> ```bash
> hashcat -a 1 -m 0 '19672a3f042ae1b592289f8333bf76c5' wordlist_1.txt wordlist_2.txt
> ```
> 
> ```bash
> hashcat (v6.2.6) starting
> 
> # ...
> 
> Dictionary cache built:
> * Filename..: wordlist_1.txt
> * Passwords.: 4
> * Bytes.....: 29
> * Keyspace..: 4
> * Runtime...: 0 secs
> 
> Dictionary cache built:
> * Filename..: wordlist_2.txt
> * Passwords.: 4
> * Bytes.....: 23
> * Keyspace..: 4
> * Runtime...: 0 secs
> 
> # ...
> 
> Initializing backend runtime for device #2. Please be patient..Host memory required for this attack: 1 MB
> 
> # ...
> 
> 19672a3f042ae1b592289f8333bf76c5:frozenapple              
> 
> Session..........: hashcat
> Status...........: Cracked
> Hash.Mode........: 0 (MD5)
> Hash.Target......: 19672a3f042ae1b592289f8333bf76c5
> Time.Started.....: Sun Sep  7 09:59:24 2025 (0 secs)
> Time.Estimated...: Sun Sep  7 09:59:24 2025 (0 secs)
> Kernel.Feature...: Pure Kernel
> Guess.Base.......: File (wordlist_1.txt), Left Side
> Guess.Mod........: File (wordlist_2.txt), Right Side
> Speed.#2.........:   220.6 kH/s (0.00ms) @ Accel:512 Loops:4 Thr:1 Vec:8
> Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
> Progress.........: 16/16 (100.00%)
> Rejected.........: 0/16 (0.00%)
> Restore.Point....: 0/4 (0.00%)
> Restore.Sub.#2...: Salt:0 Amplifier:0-4 Iteration:0-4
> Candidate.Engine.: Device Generator
> Candidates.#2....: sunshinehello -> goldenapple
> 
> Started: Sun Sep  7 09:59:21 2025
> Stopped: Sun Sep  7 09:59:25 2025
> ```

### Mode `3` — Brute-force (mask) attack

- Systematically generates all possible character combinations for a given mask pattern.
- A mask is a template that defines character types, such as digits, lowercase letters, uppercase letters, special characters, etc.
- Useful when you have partial knowledge of the password structure (length, character classes, known fixed segments, etc.).
- Resource-heavy, especially for long passwords.

```bash
hashcat -a 3 -m <hash_type> hash.txt MASK
```

- Execute a mask attack with a custom character set:

```bash
hashcat -a 3 -m 0 '50a742905949102c961929823a2e8ca0' -1 01 'HASHCAT?l?l?l?l?l20?1?d'
```

| Argument | Description |
| :--- | :--- |
| `-a 3` | Select Brute-force (mask) attack mode. |
| `-m 0` | Set the target hash type to MD5. |
| `-1 01` | Define custom character set 1, containing the characters `0` and `1`. |
| `HASHCAT?l?l?l?l?l20?1?d` | Mask pattern where `HASHCAT` and `20` are literal text, `?l` is a lowercase letter, `?1` is custom set 1, and `?d` is a digit. |

### Mode `6` — Hybrid wordlist + mask attack

- Combines a wordlist with a mask by appending characters defined by the mask to each word in the list.
- Useful when passwords are dictionary words followed by numbers, symbols, or other patterns (e.g., `password1234`).

```bash
hashcat -a 6 -m <hash_type> hash.txt wordlist.txt MASK
```

- In the following example, Hashcat appends all 3-digit combinations to each word in the wordlist:

```bash
hashcat -a 6 -m <hash_type> hash.txt wordlist.txt ?d?d?d
```

### Mode `7` — Hybrid mask + wordlist attack

- Mode `7` prepends characters defined by a mask to each candidate word from a wordlist.
- Opposite of Mode `6`: the mask is prefixed to each word in the wordlist, not appended.


- Execute a hybrid attack prepending three digits to each wordlist entry:
```bash
hashcat -a 7 -m <hash_type> hash.txt ?d?d?d wordlist.txt
```

| Option \ argument | Description |
| :--- | :--- |
| `-a 7` | Select Hybrid Mask + Wordlist attack mode. |
| `-m 1000` | Set the target hash type to NTLM. |
| `?d?d?d` | Mask that prepends three digits (`000`–`999`) to each base word. |
| `wordlist.txt` | Wordlist containing the base words. |

### Masks

- **Mask attacks** generate candidate passwords matching a specific pattern.
- A mask combines static (literal) characters, built-in charset placeholders, and user-defined custom charsets (defined with `-1` through `-4`).

- Common placeholders for Hashcat masks:

| **Placeholder** | **Meaning**                                                   |
| --------------- | ------------------------------------------------------------- |
| `?l`            | Lower-case ASCII letters (`a-z`).                             |
| `?u`            | Upper-case ASCII letters (`A-Z`).                             |
| `?d`            | Digits (`0-9`).                                               |
| `?h`            | `0123456789abcdef`                                            |
| `?H`            | `0123456789ABCDEF`                                            |
| `?s`            | All ASCII special characters, plus space.                     |
| `?a`            | Any character from `?l ?u ?d ?s`                              |
| `?b`            | Binary `0x00 - 0xff`                                          |

>[!example]+
> ```bash
> hashcat -a 3 -m 0 '50a742905949102c961929823a2e8ca0' -1 01 'HASHCAT?l?l?l?l?l20?1?d'
> ```
> 
> - The above command defines a custom character set, `-1 01`, which consists of characters `0` and `1`. 
> - `?1` refers to this character set in the mask; during the attack, Hashcat replaces `?1` with `0` or `1`.

>[!tip] You can use the `--increment` option to tell Hashcat to try all password lengths up to the mask length:
>```bash
>hashcat -a 3 -m <hash_type> --increment hashes.txt ?l?l?l?l?l?l?l?l
>```
### Hashcat rules

- Rule-based attacks are the most advanced and complex attacks in Hashcat; they take dictionary attacks to another level.

>**Hashcat rules** are predefined or custom scripts that apply transformations to each word in the input wordlist, such as prefixing, suffixing, changing case, duplicating, and reversing.

>[!important] Rules can greatly optimize password cracking: they generate password variants on the fly, saving the disk space and processing time that larger precomputed wordlists would require.

- Rules are composed of functions. A function takes a word as input and outputs its modified version.

| Function | Description                                    | Input           | Output                                 |
| -------- | ---------------------------------------------- | --------------- | -------------------------------------- |
| `:`      | Do nothing (pass the word through unchanged)   | `UnBreakable12` | `UnBreakable12`                        |
| `l`      | Lowercase                                      | `UnBreakable12` | `unbreakable12`                        |
| `u`      | Uppercase                                      | `UnBreakable12` | `UNBREAKABLE12`                        |
| `c`      | Capitalize                                     | `UnBreakable12` | `Unbreakable12`                        |
| `C`      | Lowercase first letter, <br>uppercase the rest | `UnBreakable12` | `uNBREAKABLE12`                        |
| `t`      | Toggle case                                    | `UnBreakable12` | `uNbREAKABLE12`                        |
| `TN`     | Toggle case of character at position `N`       | `UnBreakable12` | `Unbreakable12` (`T2`)                 |
| `r`      | Reverse the entire word                        | `UnBreakable12` | `21elbakaerBnU`                        |
| `d`      | Duplicate word                                 | `UnBreakable12` | `UnBreakable12UnBreakable12`           |
| `q`      | Duplicate all characters                       | `UnBreakable12` | `UUnnBBrreeaakkaabbllee1122`           |
| `pN`     | Append duplicated word `N` times               | `UnBreakable12` | `UnBreakable12UnBreakable12UnBreakable12`<br>(`p2`) |
| `f`      | Duplicate word reversed                        | `UnBreakable12` | `UnBreakable1221elbakaerBnU`           |
| `{`      | Rotate word left                               | `UnBreakable12` | `nBreakable12U`                        |
| `}`      | Rotate word right                              | `UnBreakable12` | `2UnBreakable1`                        |
| `$X`     | Append character `X` to end                    | `UnBreakable12` | `UnBreakable123` (`$3`)                |
| `^X`     | Prepend character `X` to front                 | `UnBreakable12` | `3UnBreakable12` (`^3`)                |
| `[`      | Delete first character                         | `UnBreakable12` | `nBreakable12`                         |
| `]`      | Delete last character                          | `UnBreakable12` | `UnBreakable1`                         |
| `sXY`    | Replace all instances of `X` with `Y`          | `UnBreakable12` | `UnBre4k4ble12` (`sa4`)                |
| `'N`     | Truncate word at position `N`                  | `UnBreakable12` | `UnBre` (`'5`)                         |
| `@X`     | Delete all instances of `X`                    | `UnBreakable12` | `UnBrekble12` (`@a`)                   |
| `DN`     | Delete character at position `N`               | `UnBreakable12` | `Breakable12` (`D0D0`)                 |
| `oNX`    | Overwrite character at position `N` with `X`   | `UnBreakable12` | `UnXreakable12` (`o2X`)                |
| `iNX`    | Insert character `X` at position `N`           | `UnBreakable12` | `!UnBreakable12` (`i0!`)               |
| `yN`     | Duplicate first `N` characters                 | `UnBreakable12` | `UnUnBreakable12` (`y2`)               |
| `YN`     | Duplicate last `N` characters                  | `UnBreakable12` | `UnBreakable1212` (`Y2`)               |
| `*NM`    | Swap characters at positions `N` and `M`       | `UnBreakable12` | `rnBUeakable12` (`*03`)                |

>[!note] See [`Rule-based Attack — hashcat`](https://hashcat.net/wiki/doku.php?id=rule_based_attack).

- For example, the following rule substitutes characters according to [`1337`](https://en.wikipedia.org/wiki/Leet) (leet/leetspeak):

```bash
   c  so0 si1 sl1 sz2 se3 sa4 ss5 st7
#  |   |   |   |   |   |   |   |   |
#  |   |   |   |   |   |   |   | t ⇢ 7
#  |   |   |   |   |   |   | s ⇢ 5
#  |   |   |   |   |   | a ⇢ 4
#  |   |   |   |   | e ⇢ 3
#  |   |   |   | z ⇢ 2
#  |   |   | l ⇢ 1
#  |   | i ⇢ 1
#  | o ⇢ 0
# capitalize
```

```bash
echo 'c so0 si1 sl1 sz2 se3 sa4 ss5 st7' > leet_rule.txt
```

- Apply the rule in a dictionary attack:

```bash
hashcat -a 0 -m 100 hash.txt /usr/share/wordlists/rockyou.txt -r leet_rule.txt
```

- To preview how passwords are transformed without cracking, use the `--stdout` option. With `--stdout`, you don't need to specify the hash file.

```bash
hashcat -a 0 --stdout /usr/share/wordlists/rockyou.txt -r leet_rule.txt
```

- Write the transformed candidates to a new wordlist:
```bash
hashcat -a 0 --stdout /usr/share/wordlists/rockyou.txt -r leet_rule.txt > transformed.txt
```

>[!tip]+
> - Record which rule produced each recovered candidate during a cracking session:
> 
> ```bash
> hashcat -a 0 -m 100 hash.txt rockyou.txt -r leet_rule.txt --debug-mode=4 --debug-file=debug.log
> ```
#### Hashcat built-in rules

>[!tip] 
>- You can find the built-in Hashcat rules in the `/usr/share/hashcat/rules/` directory on Parrot and Kali Linux.  

- List built-in Hashcat rules:

```bash
ls /usr/share/hashcat/rules
```

```bash
best64.rule
combinator.rule
d3ad0ne.rule
dive.rule
generated2.rule
generated.rule
hybrid
Incisive-leetspeak.rule
InsidePro-HashManager.rule
InsidePro-PasswordsPro.rule
leetspeak.rule
oscommerce.rule
rockyou-30000.rule
specific.rule
T0XlC_3_rule.rule
T0XlC-insert_00-99_1950-2050_toprules_0_F.rule
T0XlC_insert_HTML_entities_0_Z.rule
T0XlC-insert_space_and_special_0_F.rule
T0XlC-insert_top_100_passwords_1_G.rule
T0XlC.rule
T0XlCv2.rule
toggles1.rule
toggles2.rule
toggles3.rule
toggles4.rule
toggles5.rule
unix-ninja-leetspeak.rule
```
#### Publicly available rules

- There are a variety of publicly available rules as well, such as the [`nsa-rules`](https://github.com/NSAKEY/nsa-rules), [`Hob0Rules`](https://github.com/praetorian-code/Hob0Rules), and the [`corporate.rule`](https://github.com/sparcflow/HackLikeALegend/blob/master/old/chap3/corporate.rule) which is featured in the book [`How to Hack Like a Legend`](https://www.sparcflow.com/new-release-hack-like-legend/). These are curated rulesets generally targeted at common corporate Windows password policies or based on statistics and probable industry password patterns.
## Performance and optimization

- Run a benchmark test for a specific hash type:

```bash
hashcat -b -m 0
```

- Run a benchmark test for all hash modes:

```bash
hashcat -b
```

- Hashcat offers several ways to tune performance:

- Optimized kernels (`-O`)
	- Limits the **maximum password length** to 15 characters.
	- This allows Hashcat to load specialized, highly optimized GPU kernels to maximize cracking speed.
	- Kernel optimizations include reduced memory access and better use of GPU registers and threads.
	- Using `-O` generally increases speed substantially at the cost of disabling support for passwords longer than 15 characters. 
	- Hashcat prints an `ATTENTION! Pure (unoptimized) backend kernels selected` notice when pure kernels are in use.

- Workload profile (`-w`)
	- Controls the **workload tuning** on GPUs; accepts parameters from `1` to `4`:
		- `-w1`: Low workload, minimal GPU load, better for multitasking or unstable environments.	    
		- `-w2`: Balanced workload, good default for most cracking sessions.
		- `-w3`: High workload, higher GPU utilization, faster cracking.
		- `-w4`: Very high workload, maximum GPU utilization (may cause overheating or instability).

- Device selection
    
    - List detected OpenCL platforms and devices: `hashcat -I`.
    - Restrict the session to specific devices: `hashcat -a 0 -m 1000 hash.txt rockyou.txt -d 2`.
    - Restrict to a device type (e.g., GPUs only): `-D 2`.
- Timed and thermally bounded runs: `--runtime=1200` aborts the session after 1200 seconds; `--hwmon-temp-abort=75` aborts at 75 °C. Both pair well with `--session` and `--restore` for long jobs.

>[!warning] Avoid the `--force` option. It disables safety checks and suppresses warnings, which can lead to false positive and false negative results, program instability, and other issues.

## Output and session management

- Hashcat records every recovered `hash:plaintext` pair in the **potfile** (`~/.hashcat/hashcat.potfile`) by default. On subsequent runs, hashes already present in the potfile are skipped; use `--potfile-disable` to force re-cracking.
    
- Display cracked and uncracked hashes from a hash list:

```bash
hashcat -m 1000 hash.txt --show
```

```bash
hashcat -m 1000 hash.txt --left
```

- Control the output format of the `-o` file with `--outfile-format` (e.g., `2` writes plaintexts only):

```bash
hashcat -a 0 -m 1000 hash.txt rockyou.txt -o cracked.txt --outfile-format=2
```

- Hash files that embed usernames (e.g., NTDS-style `user:rid:LM:NTLM:::` lines) require `--username` so Hashcat parses the hash fields correctly:

```bash
hashcat -a 0 -m 1000 ntds.txt rockyou.txt --username
```

- Long-running attacks should be named with `--session`; the restore file is saved as `~/.hashcat/<name>.restore` and can be resumed after interruption:

```bash
hashcat -a 0 -m 1000 hash.txt rockyou.txt --session=ctf1
```

```bash
hashcat --restore --session=ctf1
```
## References and further reading

- [`Hashcat Official Website`](https://hashcat.net/hashcat/)
- [`Hashcat Mask Attack Documentation`](https://hashcat.net/wiki/doku.php?id=mask_attack)
- [`Hashcat Rule-Based Attack Documentation`](https://hashcat.net/wiki/doku.php?id=rule_based_attack)
- [`Hashcat General Wiki`](https://hashcat.net/wiki/doku.php?id=hashcat)
- [`Hashcat Example Hashes Reference`](https://hashcat.net/wiki/doku.php?id=example_hashes)
- [`LM, NTLM, and NetNTLMv2 Format Analysis`](https://medium.com/@petergombos/lm-ntlm-net-ntlmv2-oh-my-a9b235c58ed4)


## Appendix A: Hashcat command-line option reference

| Option | Description |
| :--- | :--- |
| `-m, --hash-type` | Specify the target hash type by its numeric ID (e.g., `-m 1000` for NTLM). |
| `-a, --attack-mode` | Select the attack mode (`0`, `1`, `3`, `6`, `7`). |
| `-o, --outfile` | Write recovered plaintext passwords to the specified file. |
| `-r, --rules-file` | Apply the transformation rules in the specified rule file. |
| `-j, --rule-left` | Apply a single rule to the left wordlist (combination mode). |
| `-k, --rule-right` | Apply a single rule to the right wordlist (combination mode). |
| `-1` … `-4, --custom-charset1 … 4` | Define custom character sets, referenced in masks as `?1`–`?4`. |
| `-i, --increment` | Enable mask increment mode to test all lengths up to the mask size. |
| `--increment-min` | Start increment mode at this mask length (e.g., `--increment-min=4`). |
| `--increment-max` | Stop increment mode at this mask length (e.g., `--increment-max=10`). |
| `-h, --help` | Display command line options. |
| `-V, --version` | Display version information. |
| `-b, --benchmark` | Run benchmark test for the selected hash type. |
| `--benchmark-all` | Run benchmark tests for all hash types. |
| `--speed-only` | Return the expected attack speed, then quit. |
| `--example-hashes` | Display an example hash for each supported hash mode. |
| `--identify` | Show the hash modes that match the supplied hashes. |
| `-I, --opencl-info` | Display detected OpenCL platforms and devices. |
| `--keyspace` | Display the total keyspace of the planned attack, then quit. |
| `--show` | Compare the hash list with the potfile and display cracked hashes. |
| `--left` | Compare the hash list with the potfile and display uncracked hashes. |
| `--color-cracked` | Highlight cracked hashes in the terminal output. |
| `--username` | Ignore usernames in the hash file (for `user:hash` formats). |
| `--potfile-disable` | Do not read from or write to the potfile. |
| `--outfile-format` | Define the output format (e.g., `--outfile-format=2` for plaintext only). |
| `--session` | Assign a name to the session (enables restore files). |
| `--restore` | Restore a previously interrupted session. |
| `-s, --skip` | Skip `N` words from the start of the attack. |
| `-l, --limit` | Limit the attack to `N` words from the start, plus skipped words. |
| `--runtime` | Abort the session after `N` seconds of runtime. |
| `--status` | Enable automatic updates of the terminal status view. |
| `--status-timer` | Set status screen refresh interval in seconds (`--status-timer=X`). |
| `--quiet` | Suppress standard status output. |
| `-O, --optimized-kernel-enable` | Enable optimized GPU kernels (limits maximum password length; commonly to 15 characters — the exact limit depends on the hash type, see `hashcat -h`). |
| `-w, --workload-profile` | Set workload profile (`1` to `4`). |
| `-d, --opencl-devices` | Use specific devices by ID, comma-separated (e.g., `-d 1,2`). |
| `-D, --opencl-device-types` | Restrict to device types (e.g., `-D 2` for GPUs only). |
| `--hwmon-temp-abort` | Abort if hardware temperature reaches `N` degrees Celsius (e.g., `--hwmon-temp-abort=75`). |
| `--stdout` | Print generated candidates instead of cracking (used to preview masks and rules). |
| `--force` | Bypass hardware and environment safety warnings (avoid; see [[#Performance and optimization]]). |
