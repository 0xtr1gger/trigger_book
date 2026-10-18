---
created: 2026-09-03
updated: 2026-09-20
tags:
  - password_cracking
---
> [!abstract]+ Scope: Offline password hash cracking, single crack mode, dictionary wordlist attacks, incremental Markov chain brute-force, hash format identification, and 2john file extraction tools using John the Ripper (JtR).
## John the Ripper

>**[JohnTheRipper](https://github.com/openwall/john)**, also known as **JtR** or simply **john**, is one of the most widely-used password cracking tools that supports a vast array of password hash types and advanced cracking modes.

>[!note]+ JohnTheRipper is an open-source password cracker initially developed for Unix-based systems and first released in 1996.

>[!note] The "jumbo" variant extends core functionality with additional hash format algorithms, performance optimizations, multilingual wordlist processing, and auxiliary conversion utilities (`2john`).

> [!important] Password cracking operations run **offline**. You compute hash candidates **locally** and compare them against target hashes. Local computation avoids network latency and account lockout controls.

| Option | Long option | Description |
| :--- | :--- | :--- |
| `--single` | `--single` | Enables rule-based single crack mode using account metadata. |
| `--wordlist` | `--wordlist=FILE` | Specifies plain-text wordlist file path. |
| `--rules` | `--rules[=SECTION]` | Applies transformation rules to candidate wordlists. |
| `--incremental` | `--incremental[=MODE]` | Enables Markov chain statistical brute-force mode. |
| `--format` | `--format=NAME` | Forces target hash format identifier. |
| `--show` | `--show` | Displays cracked passwords for loaded hashes from the pot file. |
| `--list` | `--list=WHAT` | Lists internal configuration parameters or supported algorithms. |

## Cracking modes

- John supports a wide range of cracking modes, each designed for different scenarios. Common modes include:
	
	- **Single crack mode**
	- **Wordlist mode**
	- **Incremental mode**
	- **Mask mode**
	- **Loopback mode**

### Single crack mode

- The **single crack mode** generates candidate passwords based on user account metadata (usernames, home directory names, and [GECOS](https://en.wikipedia.org/wiki/Gecos_field) information such as full names or phone numbers) extracted from target authentication files. 
- It then applies an extensive set of **mangling rules** against the obtained metadata strings (case changes, character substitution, appending/prepending numbers, reversing, duplicating, etc.) to generate password candidates.

>[!note] The **single crack mode** is John's fastest and most intelligent mode, designed to crack passwords based on information available about the target user account.

- Execute single crack mode against the target hash file:

```bash
john --single passwd
```

| Flag       | Description                                                       |
| :--------- | :---------------------------------------------------------------- |
| `--single` | Enables single crack metadata transformation mode.                |
| `passwd`   | Target hash file containing account metadata and password hashes. |

- Display cracked passwords stored in the pot file (`john.pot`):

```bash
john --show passwd
```

>[!example]-
> 
> ```bash
> john --single hash.txt
> ```
> 
> ```bash
> Using default input encoding: UTF-8
> Loaded 1 password hash (sha512crypt, crypt(3) $6$ [SHA512 256/256 AVX2 4x])
> Cost 1 (iteration count) is 5000 for all loaded hashes
> Will run 4 OpenMP threads
> Press 'q' or Ctrl-C to abort, almost any other key for status
> NAITSABES        (r0lf)     
> 1g 0:00:00:00 DONE (2025-10-10 02:06) 10.00g/s 4320p/s 4320c/s 4320C/s NAITSABESFL0R..rSebastiannaitsabeSr
> Use the "--show" option to display all of the cracked passwords reliably
> Session completed. 
> ```
> ```bash
> john --show hash.txt
> ```
> 
> ```bash
> r0lf:NAITSABES:0:0:Rolf Sebastian:/home/r0lf:/bin/bash
> 
> 1 password hash cracked, 0 left
> ```

>[!note] Candidate passwords are only tested against the password hash of the user they were derived for.

- The single mode can work with password files like:
	- **`/etc/passwd` and `/etc/shadow`** (and the `unshadow` combined format) on Unix systems
	- **SAM database** for local Windows accounts
	- **`NTDS.DIT`** for Active Directory
	- Memory dumps with credentials
- The file should follow this general structure:

```bash
username:hash:additional_fields
```

- Successful passwords are tried against **all loaded hashes** to test if multiple users have the same password.

>[!tip]+
>- The single mode should usually be your default first try.

#### Unshadow

- John comes with the [`unshadow`](https://manpages.debian.org/unstable/john/unshadow.8.en.html) utility that can be used to combine the `/etc/passwd` and `/etc/shadow` files on Unix system and convert them to the format John can word with. This preserves GECOS fields and information, which is useful for the single crack mode.  

```bash
unshadow /etc/passwd /etc/shadow > combined.txt
```

- Example of a user entry after `unshadow`:

```bash
# ...
r0lf:.GI6ng/qA4oaMrgElZ1Cb9OeXO4Fvy3/:0:0:Rolf Sebastian:/home/r0lf:/bin/bash
```

- Execute a single mode attack against the combined hash entry:

```bash
john --single combined.txt
```

#### Mangling rules

- List all available rules:

```bash
john --list=rules
```

```bash
all
korelogic
replaceletters
replacespecial2special
l33t
appendyears_addspecialeverywhere
appendnumnumnum_addspecialeverywhere
appendnumnum_addspecialeverywhere
# ...
```


- You can customize the mangling rules John uses to generate password candidates in the JtR configuration file, `/etc/john/john.conf`. 
- Modify the `[List.Rules:Single]` section:

```bash
[List.Rules:Single]
# Simple rules come first...
:
-s x**
-c (?a c Q
-c l Q
-s-c x** /?u l
# These were not included in crackers I've seen, but are pretty efficient,
# so I include them near the beginning
-<6 >6 '6
-<7 >7 '7 l
-<6 -c >6 '6 /?u l
-<5 >5 '5

# ...
```

>[!tip] Rules are defined in `john.conf` under `[List.Rules:RULE_NAME]`, e.g., `[List.Rules.Jumbo]`.
### Wordlist mode

>The **wordlist mode** systematically tries every entry in a dictionary as a password candidate. It can optionally apply **mangling rules** to transform each word in the list. 

- Execute a dictionary attack using a wordlist:

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
```

- Apply mutations to wordlist candidates:

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt --rules hash.txt
```

- Apply a specific rule set:

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt --rules=Jumbo hash.txt
```

>[!example]+
> ```bash
> john --wordlist=/usr/share/wordlists/rockyou.txt --format=RIPEMD-128 hash.txt
> ```
> 
> ```bash
> Using default input encoding: UTF-8
> Loaded 1 password hash (ripemd-128, RIPEMD 128 [32/64])
> Warning: no OpenMP support for this hash type, consider --fork=4
> Press 'q' or Ctrl-C to abort, almost any other key for status
> 50cent           (?)     
> 1g 0:00:00:00 DONE (2025-10-10 02:45) 100.0g/s 32000p/s 32000c/s 32000C/s angelo..101010
> Use the "--show" option to display all of the cracked passwords reliably
> Session completed. 
> ```
> 
> ```bash
> john --show --format=RIPEMD-128 hash.txt
> ```
> 
> ```bash
> ?:50cent
> 
> 1 password hash cracked, 0 left
> ```
### Incremental mode

>The **incremental mode** generates candidate password dynamically using statistical Markov chain models — without relying on a pre-existing dictionary file. It systematically tests character combinations ordered by statistical likelihood.

- Incremental mode is the most exhaustive, but also the slowest. 
- It doesn't rely on a predefined wordlist and generates password candidates dynamically. 

>[!important] John generates candidates in order of statistical likelihood rather than lexicographic order.

>[!interesting]- John's statistical optimization
> - The incremental mode uses **statistical optimization** ([Markov chains](https://en.wikipedia.org/wiki/Markov_chain)). Rather than blindly trying every combination sequentially (`aaaa`, `aaab`, `aaac`, etc.), John uses **character frequency tables** (`.chr` files). 
> - Those contain statistical data about which characters appear most frequently at each position for each password length. 
> - This dramatically increases the probability of cracking common passwords early in the attack.
> 
>>[!example]+
>>For example, for 8-character passwords, John knows that:
>> - Position `0` often contains uppercase letters or lowercase `a`, `p`, `s`. 
>> - Position `7` often contains digits (especially `1`, `3`) or `!`.
>> - Middle positions favor common letters

- Execute incremental mode using default configuration settings:

```bash
john --incremental hash.txt
```

>[!tip]+
>- By default, JtR uses predefined incremental modes specified in its configuration file (`john.conf`). 
>- You can customize character sets and password lengths to use for the brute-force or even define your own modes that use specific characters or follow specific patterns.

| Mode         | Charset                            | Count | Use Case                |
| ------------ | ---------------------------------- | ----- | ----------------------- |
| `ASCII`      | All 95 printable ASCII characters. | 95    | Maximum coverage        |
| `Alnum`      | Letters + digits `[a-zA-Z0-9]`.    | 62    | Alphanumeric passwords  |
| `Alpha`      | Letters only `[a-zA-Z]`.           | 52    | Letters-only passwords  |
| `LowerNum`   | Lowercase + digits `[a-z0-9]`.     | 36    | Common pattern          |
| `UpperNum`   | Uppercase + digits `[A-Z0-9]`.     | 36    | License keys, codes     |
| `Lower`      | Lowercase letters `[a-z]`.         | 26    | Simple lowercase        |
| `Upper`      | Uppercase letters `[A-Z]`.         | 26    | Simple uppercase        |
| `Digits`     | Digits only `[0-9]`.               | 10    | PINs, numeric passwords |
| `LowerSpace` | Lowercase + space.                 | 27    | Passphrases             |
| `LM_ASCII`   | For LM hashes.                     | 95    | Windows LM hashes       |
>[!note] The default incremental mode is `ASCII`.

- Specify a custom incremental mode:

```bash
john --incremental=Alnum hashfile.txt 
```

```bash
john --incremental=Lower hashfile.txt 
```

```bash
john --incremental=Digits hashfile.txt
```

### Mask mode

>The **mask mode**, also called **mask attack** or **hybrid mask**, systematically tries all character combinations according to the specified pattern, or **mask**.

A **mask** is a string where special characters represent character classes. Built-in character classes include: 

| Placeholder | Character Class                                               |
| ----------- | ------------------------------------------------------------- |
| `?l`        | Lower-case ASCII letters (`a-z`).                             |
| `?u`        | Upper-case ASCII letters (`A-Z`).                             |
| `?d`        | Digits (`0-9`).                                               |
| `?s`        | Special characters ``!"#$%&'()*+,-./:;<=>?@[]^_`{ `` + space. |
| `?a`        | Any character from `?l ?u ?d ?s`.                             |
| `?h`        | Lowercase hex (`0123456789abcdef`).                           |
| `?H`        | Uppercase hex (`0123456789ABCDEF`).                           |
| `?v`        | Vowels (`aeiouAEIOU`).                                        |
| `?c`        | Consonants (`bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ`).    |
| `?w`        | Whitespace.                                                   |
| `?p`        | Punctuation.                                                  |
| `?b`        | Binary `0x00`-`0xff`.                                         |

You can also define your own placeholders with custom character sets, from `-1` to `-4`:

| Option                    | Description               |
| ------------------------- | ------------------------- |
| `-1`, `--custom-charset1` | User-defined charset `?1` |
| `-2`, `--custom-charset2` | User-defined charset `?2` |
| `-3`, `--custom-charset3` | User-defined charset `?3` |
| `-4`, `--custom-charset4` | User-defined charset `?4` |

Examples:

- Mask mode, an uppercase letter followed by 4 digits:

```bash
john --mask=?u?d?d?d?d hash.txt
```

- Mask mode, 8 lowercase digits:

```bash
john --mask=?l?l?l?l?l?l?l?l hash.txt
```

Or, with length specification:

```bash
john --mask=?l --min-len=8 --max-len=8 hash.txt
```

- `Password` followed by 2 digits and a special character:

```bash
john --mask=Password?d?d?s hash.txt
```


- Incremental length with mask pattern:

```bash
# try ?d?d?d, then ?d?d?d?d, then ?d?d?d?d?d
john --mask=?d --min-len=3 --max-len=5 hash.txt
```

- Multiple custom character sets:

```bash
john --mask=?1?d?d?d?2 -1=[A-Z] -2=[!@#$] hashfile.txt
```

### Loopback mode

>The **loopback mode** uses **already-cracked passwords** from `john.pot` as a wordlist. It can optionally apply mangling rules.


```bash
john --loopback --rules hash.txt
```
## Common JtR hash formats

| Format string | Target hash description | Example invocation |
| :--- | :--- | :--- |
| `raw-md5` | Raw MD5 hashes | `john --format=raw-md5 hashes.txt` |
| `raw-sha256` | Raw SHA-256 hashes | `john --format=raw-sha256 hashes.txt` |
| `raw-sha512` | Raw SHA-512 hashes | `john --format=raw-sha512 hashes.txt` |
| `nt` | Windows NTLM hashes | `john --format=nt hashes.txt` |
| `lm` | Windows LAN Manager (LM) hashes | `john --format=lm hashes.txt` |
| `netntlmv2` | NetNTLMv2 / NTLMv2 challenge-response | `john --format=netntlmv2 hashes.txt` |
| `krb5tgs` | Kerberos 5 TGS-REP ticket hashes | `john --format=krb5tgs hashes.txt` |
| `sha512crypt` | Unix `$6$` SHA-512 crypt hashes | `john --format=sha512crypt hashes.txt` |
| `phpass-md5` | WordPress / PHPass MD5 hashes | `john --format=phpass-md5 hashes.txt` |
| `zip` | Encrypted ZIP archive hashes | `john --format=zip hashes.txt` |
| `rar` | Encrypted RAR archive hashes | `john --format=rar hashes.txt` |
| `pdf` | Encrypted PDF document hashes | `john --format=pdf hashes.txt` |
| `ssh` | Encrypted SSH private key passphrase hashes | `john --format=ssh hashes.txt` |

## Extracting hashes with 2john utilities

- JtR provides helper utilities (prefixed or suffixed with `2john`) that parse encrypted containers, key files, databases, and network captures into JtR-compatible hash formats.

- Extract a hash from a target encrypted file or container:

```bash
<2john_utility> target_file > file.hash
```

- Execute JtR against the extracted hash:

```bash
john file.hash
```

| **Tool**                | **Description**                               |
| ----------------------- | --------------------------------------------- |
| `pdf2john`              | Converts PDF documents for John               |
| `ssh2john`              | Converts SSH private keys for John            |
| `mscash2john`           | Converts MS Cash hashes for John              |
| `keychain2john`         | Converts OS X keychain files for John         |
| `rar2john`              | Converts RAR archives for John                |
| `pfx2john`              | Converts PKCS#12 files for John               |
| `truecrypt_volume2john` | Converts TrueCrypt volumes for John           |
| `keepass2john`          | Converts KeePass databases for John           |
| `vncpcap2john`          | Converts VNC PCAP files for John              |
| `putty2john`            | Converts PuTTY private keys for John          |
| `zip2john`              | Converts ZIP archives for John                |
| `hccap2john`            | Converts WPA/WPA2 handshake captures for John |
| `office2john`           | Converts MS Office documents for John         |
| `wpa2john`              | Converts WPA/WPA2 handshakes for John         |


- Locate available `2john` converter tools installed on the system:

```bash
locate *2john*
```

> [!example]- Raw locate output for 2john utilities
> ```text
> /usr/bin/bitlocker2john
> /usr/bin/dmg2john
> /usr/bin/gpg2john
> /usr/bin/hccap2john
> /usr/bin/keepass2john
> /usr/bin/putty2john
> /usr/bin/rar2john
> /usr/bin/zip2john
> /usr/share/john/1password2john.py
> /usr/share/john/7z2john.pl
> /usr/share/john/DPAPImk2john.py
> /usr/share/john/androidbackup2john.py
> ```

## References and further reading

- [`John the Ripper's cracking modes. — Openwall`](https://www.openwall.com/john/doc/MODES.shtml)
- [`Markov chain — Wikipedia`](https://en.wikipedia.org/wiki/Markov_chain)
- [`John the Ripper Official Website`](https://www.openwall.com/john/)
- [`Openwall John the Ripper Documentation Wiki`](https://www.openwall.com/w/John_the_Ripper)
- [`John the Ripper Jumbo GitHub Repository`](https://github.com/openwall/john)
- [`PentestMonkey Hash Examples Reference`](https://pentestmonkey.net/cheat-sheet/john-the-ripper/john-the-ripper-hash-formats)

## Appendix A: John hash formats

| **Hash format**      | **Example command**                               | **Description**                                                      |
| -------------------- | ------------------------------------------------- | -------------------------------------------------------------------- |
| afs                  | `john --format=afs [...] <hash_file>`             | AFS (Andrew File System) password hashes                             |
| bfegg                | `john --format=bfegg [...] <hash_file>`           | bfegg hashes used in Eggdrop IRC bots                                |
| bf                   | `john --format=bf [...] <hash_file>`              | Blowfish-based crypt(3) hashes                                       |
| bsdi                 | `john --format=bsdi [...] <hash_file>`            | BSDi crypt(3) hashes                                                 |
| crypt(3)             | `john --format=crypt [...] <hash_file>`           | Traditional Unix crypt(3) hashes                                     |
| des                  | `john --format=des [...] <hash_file>`             | Traditional DES-based crypt(3) hashes                                |
| dmd5                 | `john --format=dmd5 [...] <hash_file>`            | DMD5 (Dragonfly BSD MD5) password hashes                             |
| dominosec            | `john --format=dominosec [...] <hash_file>`       | IBM Lotus Domino 6/7 password hashes                                 |
| EPiServer SID hashes | `john --format=episerver [...] <hash_file>`       | EPiServer SID (Security Identifier) password hashes                  |
| hdaa                 | `john --format=hdaa [...] <hash_file>`            | hdaa password hashes used in Openwall GNU/Linux                      |
| hmac-md5             | `john --format=hmac-md5 [...] <hash_file>`        | hmac-md5 password hashes                                             |
| hmailserver          | `john --format=hmailserver [...] <hash_file>`     | hmailserver password hashes                                          |
| ipb2                 | `john --format=ipb2 [...] <hash_file>`            | Invision Power Board 2 password hashes                               |
| krb4                 | `john --format=krb4 [...] <hash_file>`            | Kerberos 4 password hashes                                           |
| krb5                 | `john --format=krb5 [...] <hash_file>`            | Kerberos 5 password hashes                                           |
| LM                   | `john --format=LM [...] <hash_file>`              | LM (Lan Manager) password hashes                                     |
| lotus5               | `john --format=lotus5 [...] <hash_file>`          | Lotus Notes/Domino 5 password hashes                                 |
| mscash               | `john --format=mscash [...] <hash_file>`          | MS Cache password hashes                                             |
| mscash2              | `john --format=mscash2 [...] <hash_file>`         | MS Cache v2 password hashes                                          |
| mschapv2             | `john --format=mschapv2 [...] <hash_file>`        | MS CHAP v2 password hashes                                           |
| mskrb5               | `john --format=mskrb5 [...] <hash_file>`          | MS Kerberos 5 password hashes                                        |
| mssql05              | `john --format=mssql05 [...] <hash_file>`         | MS SQL 2005 password hashes                                          |
| mssql                | `john --format=mssql [...] <hash_file>`           | MS SQL password hashes                                               |
| mysql-fast           | `john --format=mysql-fast [...] <hash_file>`      | MySQL fast password hashes                                           |
| mysql                | `john --format=mysql [...] <hash_file>`           | MySQL password hashes                                                |
| mysql-sha1           | `john --format=mysql-sha1 [...] <hash_file>`      | MySQL SHA1 password hashes                                           |
| NETLM                | `john --format=netlm [...] <hash_file>`           | NETLM (NT LAN Manager) password hashes                               |
| NETLMv2              | `john --format=netlmv2 [...] <hash_file>`         | NETLMv2 (NT LAN Manager version 2) password hashes                   |
| NETNTLM              | `john --format=netntlm [...] <hash_file>`         | NETNTLM (NT LAN Manager) password hashes                             |
| NETNTLMv2            | `john --format=netntlmv2 [...] <hash_file>`       | NETNTLMv2 (NT LAN Manager version 2) password hashes                 |
| NEThalfLM            | `john --format=nethalflm [...] <hash_file>`       | NEThalfLM (NT LAN Manager) password hashes                           |
| md5ns                | `john --format=md5ns [...] <hash_file>`           | md5ns (MD5 namespace) password hashes                                |
| nsldap               | `john --format=nsldap [...] <hash_file>`          | nsldap (OpenLDAP SHA) password hashes                                |
| ssha                 | `john --format=ssha [...] <hash_file>`            | ssha (Salted SHA) password hashes                                    |
| NT                   | `john --format=nt [...] <hash_file>`              | NT (Windows NT) password hashes                                      |
| openssha             | `john --format=openssha [...] <hash_file>`        | OPENSSH private key password hashes                                  |
| oracle11             | `john --format=oracle11 [...] <hash_file>`        | Oracle 11 password hashes                                            |
| oracle               | `john --format=oracle [...] <hash_file>`          | Oracle password hashes                                               |
| pdf                  | `john --format=pdf [...] <hash_file>`             | PDF (Portable Document Format) password hashes                       |
| phpass-md5           | `john --format=phpass-md5 [...] <hash_file>`      | PHPass-MD5 (Portable PHP password hashing framework) password hashes |
| phps                 | `john --format=phps [...] <hash_file>`            | PHPS password hashes                                                 |
| pix-md5              | `john --format=pix-md5 [...] <hash_file>`         | Cisco PIX MD5 password hashes                                        |
| po                   | `john --format=po [...] <hash_file>`              | Po (Sybase SQL Anywhere) password hashes                             |
| rar                  | `john --format=rar [...] <hash_file>`             | RAR (WinRAR) password hashes                                         |
| raw-md4              | `john --format=raw-md4 [...] <hash_file>`         | Raw MD4 password hashes                                              |
| raw-md5              | `john --format=raw-md5 [...] <hash_file>`         | Raw MD5 password hashes                                              |
| raw-md5-unicode      | `john --format=raw-md5-unicode [...] <hash_file>` | Raw MD5 Unicode password hashes                                      |
| raw-sha1             | `john --format=raw-sha1 [...] <hash_file>`        | Raw SHA1 password hashes                                             |
| raw-sha224           | `john --format=raw-sha224 [...] <hash_file>`      | Raw SHA224 password hashes                                           |
| raw-sha256           | `john --format=raw-sha256 [...] <hash_file>`      | Raw SHA256 password hashes                                           |
| raw-sha384           | `john --format=raw-sha384 [...] <hash_file>`      | Raw SHA384 password hashes                                           |
| raw-sha512           | `john --format=raw-sha512 [...] <hash_file>`      | Raw SHA512 password hashes                                           |
| salted-sha           | `john --format=salted-sha [...] <hash_file>`      | Salted SHA password hashes                                           |
| sapb                 | `john --format=sapb [...] <hash_file>`            | SAP CODVN B (BCODE) password hashes                                  |
| sapg                 | `john --format=sapg [...] <hash_file>`            | SAP CODVN G (PASSCODE) password hashes                               |
| sha1-gen             | `john --format=sha1-gen [...] <hash_file>`        | Generic SHA1 password hashes                                         |
| skey                 | `john --format=skey [...] <hash_file>`            | S/Key (One-time password) hashes                                     |
| ssh                  | `john --format=ssh [...] <hash_file>`             | SSH (Secure Shell) password hashes                                   |
| sybasease            | `john --format=sybasease [...] <hash_file>`       | Sybase ASE password hashes                                           |
| xsha                 | `john --format=xsha [...] <hash_file>`            | xsha (Extended SHA) password hashes                                  |
| zip                  | `john --format=zip [...] <hash_file>`             | ZIP (WinZip) password hashes                                         |
