---
created: 2026-09-02
updated: 2026-10-08
tags:
  - password_cracking
---
## Hashes 

- Passwords are commonly stored as **hashes**, produced by a _hash function_.

>A **hash function** is a one-way mathematical function that transforms input data of arbitrary length into a fixed-length **hash value**, or **digest** (often simply called a **hash**).

- Key properties of cryptographic hash functions:
	- **One-way operation**
		- It is **computationally infeasible** to recover an input from its hash.
		- Formally, given a hash digest $h$, finding a message $m$ such that $h = H(m)$ should be computationally infeasible.
	- **Deterministic output**
		- The same input always produces the same hash value.
	- **Fixed output length**
		- Regardless of input length, the same hashing algorithm always returns output of the same length (e.g., MD5 always produces 128 bits / 32 hex characters).

- The only reliable way to find a plaintext value of a given hash is to compute a hash using the same hashing algorithm against each candidate password and compare the results with the target hash. There's no reverse operation in this process: you only compute values one-way and compare them.

>[!example]+
>- Convert a string to an MD5 hash:
> ```bash
> echo -n "passwd123" | md5sum
> ```
> ```bash
> 1164f9e5b8cef768396dcd5374e4b6eb
> ```

### Common hashing algorithms

- Modern systems employ different hash algorithms depending on their security needs and performance considerations. Below are some of the most commonly used ones:

- [Argon2](https://en.wikipedia.org/wiki/Argon2)
	- A modern and secure hashing algorithm specifically designed to hash passwords. 
	- Winner of the 2015 Password Hashing Competition, Argon2 is considered one of the strongest hashing algorithms.
	- It is intentionally **slow** and **memory-intensive** to deter brute-force attacks.

- [bcrypt](https://en.wikipedia.org/wiki/Bcrypt)
	- Based on the [Blowfish](https://en.wikipedia.org/wiki/Blowfish_\(cipher\) "Blowfish (cipher)") cipher, bcrypt incorporates an adjustable cost parameter: you can increase hashing complexity as hardware capabilities evolve, so the hashes stay resistant to brute-force.
	- Includes salting to prevent rainbow table attacks.
	- Usually faster than Argon2.

- [PBKDF2](https://en.wikipedia.org/wiki/PBKDF2) (Password-Based Key Derivation Function)
	- Applies a pseudorandom function (like [HMAC](https://en.wikipedia.org/wiki/HMAC)) to the input password or passphrase along with a salt value; this process is repeated multiple times to produce a derived key.
	- Recommended by [`RFC 8018`](https://datatracker.ietf.org/doc/html/rfc8018) for password hashing.

- [SHA (Secure Hash Algorithms) family](https://en.wikipedia.org/wiki/Secure_Hash_Algorithms) (e.g., SHA-128, SHA-256, SHA-384, SHA-512, etc.)
	-  Very fast, widely supported; yet too fast to be secure for password hashing unless techniques like salting or [key stretching](https://en.wikipedia.org/wiki/Key_stretching) are applied.
	- Widely used for integrity checks and digital signatures. SHA-2 and SHA-3 algorithms are used in [HMAC](https://en.wikipedia.org/wiki/HMAC), which acts as a [checksum](https://en.wikipedia.org/wiki/Checksum) to verify whether a message has been tampered, for example, during transmission.
	- Vulnerable to brute-force attacks when used alone for passwords.

- [MD5](https://en.wikipedia.org/wiki/MD5)
	- A widely used fast hashing algorithm; produces 128-bit hashes but **considered broken** due to vulnerabilities to collision and brute-force.
	- Can not be used for password hashing in any modern secure system.
	- Still suitable for noncritical applications such as file integrity verification.
### Salting

- One of the ways to protect hashes rainbow table attacks is **salting**.

>A **salt** is a unique random string added to the plaintext before hashing.

>[!interesting] How salting works
> 1. When a user creates or updates a password, the system generates a unique random string of data, called **salt** (e.g., 16 random bytes).
> 2. The system concatenates the salt string with the plaintext password.
> 3. The cryptographic algorithm hashes the combined string (`Hash(Salt + Password)`).
> 4. The resulting digest and the plaintext salf are stored together in a database.
>
>- At login, the system retrieves the salt from the database, combines it with the entered password, hashes it, and compares the result with the hash stored in the database. If there's a match, the entered password is correct.

- With salting, precalculated rainbow tables become ineffective because every password uses a unique salt.
- As a result, identical passwords generate different hash strings.

>[!warning] Without salting, identical passwords produce identical hashes. This makes hashes susceptible to precomputed rainbow table attacks.

- For comparison, here is a Python code that hashes passwords without salting:

>[!example] Example Python code: Hashing without salting
> 
> ```Python
> import hashlib
> 
> def hash_password_without_salt(password):
> 	return hashlib.sha256(password.encode()).hexdigest()
> ```

>[!example] Example Python code: Hashing with salting
> 
> ```Python
> import hashlib
> import os
> 
> def hash_password_with_salt(password):
>     salt = os.urandom(16)  # generates a random salt (16 bytes)
> 
>     salted_password = salt + password.encode() # concatenates the salt and password
> 
>     hash_digest = hashlib.sha256(salted_password).hexdigest() # hashes the combination
> 
>     return salt.hex(), hash_digest # returns the salf andhash
> ```
### Password cracking

>**Password cracking** is the process of recovering a plaintext password from its encrypted or hashed form.

- Techniques commonly used in password cracking include:
	
	- **Brute-force attacks**
		- Systematically trying all possible password combinations withing a defined character set and length, hashing each candidate, and comparing the result with the target hash. 
		- Time- and resource-consuming process.
	
	- **Dictionary attacks**
		- Iterating through a dictionary of possible passwords (e.g., common words, leaked passwords), hashing each candidate, and comparing the result with the target hash. 
		- This technique exploits users' tendency to use weak passwords or reuse them across multiple platforms.
	
	- **Rainbow table attacks**
		- Using a precomputed table of hashes for common passwords to find a match. 
		- Avoids computing hashes, though tables may take up a lot of disk space.
		- Ineffective against hashes that use **salting**.
	
	- **Cryptanalysis**
		- Exploiting weaknesses in the hashing algorithm or its implementation directly. 
		- Less common against modern strong hashes.

>[!note] Brute-forcing is the only password cracking technique that is **100% effective** - in that, given enough time, any password will be cracked with this technique. That said, it is hardly ever used because of how much time it takes for stronger passwords, and is typically replaced by much more efficient **mask attacks**.

>A **[rainbow table](https://en.wikipedia.org/wiki/Rainbow_table)** is a precomputed table that maps input and output values for a given hash function.

- Rainbow tables are used to quickly identify password and its corresponding hash without calculating the hash itself. 

 >[!example]+
> - Example of a rainbow table:
> 
> | Password    | MD5 hash                           |
> | ----------- | ---------------------------------- |
> | `123456`    | `e10adc3949ba59abbe56e057f20f883e` |
> | `12345`     | `827ccb0eea8a706c4c34a16891f84e7b` |
> | `123456789` | `25f9e794323b453885f5181f1b624d0b` |
> | `password`  | `5f4dcc3b5aa765d61d8327deb882cf99` |
> | `iloveyou`  | `f25a2fc72690b780b2a14e140ef6a9e0` |
> | `princess`  | `8afa847f50a716e64932d995c8e7435a` |
> | `1234567`   | `fcea920f7412b5da7be0cf42b8c93759` |
> | `rockyou`   | `f806fc5a2a0d5ba2471600758452799c` |
> | `12345678`  | `25d55ad283aa400af464c76d713c07ad` |
> | `abc123`    | `e99a18c428cb38d5f260853678922e03` |
> | `...`       | `...`                              |

## Identifying hashing algorithms

- Before attempting cracking a hash, you need to determine the exact hashing algorithm used to compute it.
- It's often possible to identify the hashing algorithm by analyzing the size, format, and character set of the target hash.


- Analyse digest length and character set:

| Bit length | Hex characters | Hashing algorithms |
| ---------- | -------------- | ------------------ |
| `128`      | `32`           | MD5, NTLM, MD4     |
| `160`      | `40`           | SHA-1              |
| `256`      | `64`           | SHA-256            |
| `512`      | `128`          | SHA-512            |

- Unix and Linux systems store hashes using a structured **Modular Crypt Format (MCF)**: `$id$salt$hash`.

| Prefix                                        | Algorithm     |
| :-------------------------------------------- | :------------ |
| `$1$`                                         | MD5 crypt     |
| `$2$`<br>`$2a$`<br>`$2b$`<br>`$2x$`<br>`$2y$` | bcrypt        |
| `$3$`                                         | NT hash       |
| `$5$`                                         | SHA-256 crypt |
| `$6$`                                         | SHA-512 crypt |
| `$7$`                                         | Scrypt        |
| `$y$`                                         | yescrypt      |
| `$argon2i$`, `$argon2id$`                     | Argon2        |


```Python
$1$  : MD5
$2$  : Bcrypt
$2a$ : Bcrypt
$2x$ : Bcrypt
$2y$ : Bcrypt
$2b$ : Bcrypt
$3$  : NTHASH
$5$  : SHA-256
$6$  : SHA-512
$7$  : Scrypt
$y$  : yescrypt
$argon2i$  : Argon2
```

>[!note] See [Modular Crypt Format](https://passlib.readthedocs.io/en/stable/modular_crypt_format.html).

- Windows credential formats:
	- LM hashes consist of 32 uppercase hexadecimal characters split into two 16-character halves (`B4B9B02E6F09A9BD760F388B67351E2B`).
	- NTLM hashes consist of 32 uppercase or lowercase hexadecimal characters (`31d6cfe0d16ae931b73c59d7e0c089c0`).

- Some systems may store salt as `hash:salt` or similar.
### HashID 

- You can use [`HashID`](https://github.com/psypanda/hashID) to identify hash formats automatically. It can identify **over 200 unique hash types**, and for others, it will make a best-effort guess (see the [full list of supported hashes](https://github.com/psypanda/hashID/blob/master/doc/HASHINFO.xlsx)).

>[!note]+ Installation
> ```bash
> pip install hashid
> ```


- Analyze a single target hash string:

```bash
hashid '$apr1$71850310$gh9m4xcAn3MGxogwX/ztb.'
```

>[!example]-
> ```bash
> hashid '$apr1$71850310$gh9m4xcAn3MGxogwX/ztb.'
> 
> Analyzing '$apr1$71850310$gh9m4xcAn3MGxogwX/ztb.'
> [+] MD5(APR) 
> [+] Apache MD5
> ```

- Include Hashcat mode numbers in the output:

```bash
hashid -m '$apr1$71850310$gh9m4xcAn3MGxogwX/ztb.'  
```

>[!example]-
> ```bash
> hashid -m '$apr1$71850310$gh9m4xcAn3MGxogwX/ztb.'  
> 
> Analyzing '$apr1$71850310$gh9m4xcAn3MGxogwX/ztb.'  
> [+] MD5(APR) [Hashcat Mode: 1600]  
> [+] Apache MD5 [Hashcat Mode: 1600]
> ```

- Specify a file with a list of hashes to analyze:

```bash
hashid hashes.txt
```

| Option | Description                                                                             |
| :----- | :-------------------------------------------------------------------------------------- |
| `-m`   | Display the corresponding Hashcat mode numbers (`-m <mode>`) for identified algorithms. |
| `-j`   | Displays the corresponding John the Ripper format identifiers.                          |
| `-o`   | Write output results to a file.                                                         |

> [!warning]+ Limitations 
> - `HashID` relies on regex patterns and length checks to identify the algorithm.
> - Multiple algorithms share identical signatures (e.g., MD5 and NTLM both present as 32 hex characters). In this case, `HashID` will provide multiple options of what the hash might be.
> - You still need evaluate the target system context (Active Directory DB, `/etc/shadow`, database dump) to select the correct hash mode.

>[!warning] It's not always possible to identify the algorithm based on the hash. Depending on the software, the plaintext might undergo multiple encryption and salting transformations, which makes it much harder to recover.

>[!tip]+
>- Always consider **context** for more accurate identification. How was the hash obtained? Was it a password database (such as through SQL injection), Linux host (e.g., `/etc/passwd` or `/etc/shadow`), Windows host, Active Directory?

>[!tip]+
>- Hashcat maintains a list of [example hashes](https://hashcat.net/wiki/doku.php?id=example_hashes), which may come very useful when you need to identify the exact type of the hash you're facing. This table maps Hashcat modes to the corresponding hashing algorithms, and gives examples of each hash type. 
>- You can compare your target hash with examples in the table, based on the list of possibilities HashID gave you, to identify what you're working with.

## References and further reading

- [`Hash function — Wikipedia`](https://en.wikipedia.org/wiki/Hash_function)
- [`Rainbow table — Wikipedia`](https://en.wikipedia.org/wiki/Rainbow_table)

