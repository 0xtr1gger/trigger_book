---
created: 2025-09-22 09:21:12
---
## Encrypted files

During penetration tests, it's common to encounter encrypted, password-protected documents or archives. These may include:

- **Microsoft Office documents** 
	- DOCX (Word), XLSX (Excel), PPTX (PowerPoint), OneNote, etc.
- **Archives**
	- ZIP, RAR, 7z, etc.
- **KeePass databases**
- **Disk images**
	- VeraCrypt, BitLocker, etc.
- **PDF files**
- **Protected SSH Keys**
- **Encrypted SQLite files**
- etc.
## How password protection works

1. **Key derivation**
	- When a user sets a password, a **[KDF](https://en.wikipedia.org/wiki/Key_derivation_function)** (Key Derivation Function), such as [PBKDF2](https://en.wikipedia.org/wiki/PBKDF2), [scrypt](https://en.wikipedia.org/wiki/Scrypt), or [Argon2](https://en.wikipedia.org/wiki/Argon2), is applied to a password to generate a **symmetric encryption key**.
	- The password is often salted to prevent rainbow table attacks.

2. **Symmetric encryption**
	- The file content is encrypted using the derived key and a symmetric encryption algorithm like AES-256, ChaCha20, or Twofish.
	- Different file formats use different encryption algorithms and modes (CBC, GCM, etc.)

3. **Metadata storage**
	- Encryption algorithm, salt, KDF parameters, and verification data is usually stored in file metadata. Some formats may store a hash of the password for verification.

When a user enters the password to access the file, the application uses the same KDF to derive a cryptographic key, and then attempts to decrypt a small verification block. If the output matches a known value, the password is correct, and the file can be fully decrypted.

>[!important] Some file formats store a hash. Cracking this hash will give the correct password.

Password cracking for such files follows this general process:
1. **Extract the hash/encryption metadata** from the protected file. For example, the password cracking tool [JohnTheRipper](https://github.com/openwall/john) comes with many tools that can be used to extract hashes from a variety of password-protected file formats.
2. **Convert the hash** to the format the cracking tool can understand.
3. **Crack the hash** using tools like [[྾_password_cracking_with_Hashcat#Hashcat|Hashcat]].

>[!note] In this guide, we will primarily use JohnTheRipper tools to extract relevant file metadata, and Hashcat for cracking hashes themselves.

>[!note] To read more about hash cracking, see [[྾_password_cracking_with_Hashcat]].

>[!note]+ Installing JohnTheRipper
>Tools that JohnTheRipper provides are available right after installing the tool itself. But you can also compile them from the source found in the [JohnTheRipper GitHub repository](https://github.com/magnumripper/JohnTheRipper/tree/bleeding-jumbo/src): 
>```bash
>git clone https://github.com/magnumripper/JohnTheRipper.git && \
>cd JohnTheRipper/src 
>```
>```bash
>sudo ./configure && \
>sudo make
>```
>
>Most of those tools are also available in Python. You can find them in the John's repository as well, [here](https://github.com/openwall/john/tree/bleeding-jumbo/run).
## Microsoft Office documents

### Microsoft Office encryption

Modern Office formats (2007+), such as DOCS, XLSX, PPTX, are actually **ZIP archives** with XML files and binary data inside. 
- When you set a password, Office uses a [KDF](https://en.wikipedia.org/wiki/Key_derivation_function) like SHA-1 or SHA-2, with a random salt and a large number of hash iterations (e.g., 100,000+ rounds), to produce a 128-bit key symmetric encryption key.
- The file is then encrypted with [AES](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard) (AES-128 or AES-256 in CBC mode) using that derived key.

>[!note]+ File formats
>- Microsoft Office 2007+ file formats: `.docx`, `.xlsx`, `.pptx` (ZIP-based containers with XML metadata and strong AES encryption).
>- Microsoft Office 97-2003: `.doc`, `.xls`, `.ppt` (weaker encryption, often RC4)

>[!note] Data necessary for decryption, such as salt and KDF parameters, are stored in the file's metadata, usually in XML inside the ZIP container (DOCS/XLSX/PPTX), or in binary headers (older formats).

The KDF used depends on the Office version:

| Version     | KDF                                                                                                 | Encryption |
| ----------- | --------------------------------------------------------------------------------------------------- | ---------- |
| Office 2007 | SHA-1, 50,000 rounds                                                                                | AES        |
| Office 2010 | SHA-1, 100,000 rounds                                                                               | AES        |
| Office 2013 | SHA-1, 100,000 rounds                                                                               | AES        |
| Office 2016 | SHA-2, 16 bytes of salt and [CBC](https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#CBC) | AES        |

>[!note] As for older formats,
> - In Excel and Word 95, a password was converted to a 16-bit verified and a 16-byte XOR obfuscation array key.
> - Office 97, 2000, XP, and 2003 used [RC4](https://en.wikipedia.org/wiki/RC4 "RC4") with 40 bits (RC4 is considered insecure; it was [cracked within days back in 1994 right after its code was leaked to public](https://en.wikipedia.org/wiki/RC4#History)).

See [`Microsoft Office password protection, AES since Office 2007 — Wikipedia`](https://en.wikipedia.org/wiki/Microsoft_Office_password_protection#AES_since_Office_2007).
### Cracking Microsoft Office hashes 

Cracking a password of a Microsoft Office file involves the following steps:

1. **Extract the hash and relevant encryption metadata from the file**
	- You can use [`office2john.py`](https://raw.githubusercontent.com/magnumripper/JohnTheRipper/bleeding-jumbo/run/office2john.py) script (part of John the Ripper) for this purpose.
	
	```bash
	python3 office2john.py word_file.docx > hash.txt
	```

2. **Crack the hash**
	
	```bash
	hashcat -m 9600 hash.txt /usr/share/wordlists/rockyou.txt
	```
	
>[!note]+ Download `office2john.py`
>```
>curl -s -O https://raw.githubusercontent.com/magnumripper/JohnTheRipper/bleeding-jumbo/run/office2john.py
>```

Hashcat modes for Microsoft Office documents (2007+):

| Mode   | Descriptoin    |
| ------ | -------------- |
| `9400` | MS Office 2007 |
| `9500` | MS Office 2010 |
| `9600` | MS Office 2013 |

Hashcat modes for older Office documents:

| `9700` | MS Office 2003 (MD5 + RC4, `oldoffice$0`, `oldoffice$1`)   |
| ------ | ---------------------------------------------------------- |
| `9710` | MS Office 2003 `$0/$1` (MD5 + RC4, collider 1)             |
| `9720` | MS Office 2003 `$0/$1` (MD5 + RC4, collider 2)             |
| `9800` | MS Office 2003 (SHA-1 + RC4, `oldoffice$3`, `oldoffice$4`) |
| `9810` | MS Office 2003 (SHA-1 + RC4, collider 1)                   |
| `9820` | MS Office 2003 (SHA-1 + RC4, collider 2)                   |

>[!note]+ *Collider* refers to a mode Hashcat uses to crack the hash by exploiting collision vulnerabilities in hash functions.

## Archive files

### Archive encryption 

Archives can be encrypted in different ways based on the format:
- **ZIP** (ZipCrypto/AES)
	- ZipCrypto is the classic ZIP encryption method that, however, is weak and can be cracked easily. AES is much stronger; it's also used in 7-Zip and WinRAR encryption.
	- See [`ZIP (file format), Encryption — Wikipedia`](https://en.wikipedia.org/wiki/ZIP_(file_format)#Encryption).
- **RAR**
	- RAR3 uses AES-128, RAR5 uses AES-256 and a strong [KDF](https://en.wikipedia.org/wiki/Key_derivation_function).
- **7z**
	- 7z archives use AES-256 and encrypt the **entire archive**, including file names and headers.

>[!interesting]+ How encryption is applied in archives
>- **File-by-file encryption (ZIP, RAR)**
>	- In classic ZIP and RAR formats, **each file inside the archive is encrypted separately**. This means every file has its own encrypted data block, and sometimes its own initialization vector (IV) or salt.
>	- The archive's directory (the list of filenames, sizes, etc.) may or may not be encrypted, depending on the tool and settings.
>	- Cracking tools extract necessary metadata (salt, encrypted verification block, and the hash itself) from one file in the archive, usually the first one. If you crack the password for one file, you can decrypt all files in the archive (the same password is used for all).
>
>
>- **While-archive encryption (7z)**
>	- 7z archives (with AES encryption) can encrypt the entire archive, including file names and metadata. This means everything inside the archive is protected the key derived from the password.
>	- When cracking, the encryption metadata is extracted from the archive itself, and you only need to decrypt one file (the archive itself).
### Cracking archive hashes

Cracking a password of a an archive file involves the following steps:

1. **Extract the hash and relevant encryption metadata from the archive**
	- Depending on the archive format, there're different tools you can use:
	-  [`zip2john`](https://github.com/openwall/john/blob/bleeding-jumbo/src/zip2john.c) for ZIP archives:
	
	```bash
	zip2john archive.zip > hash.txt
	```
	
	- [`rar2john`](https://github.com/openwall/john/blob/bleeding-jumbo/src/rar2john.c) for RAR archives:
	
	```bash
	rar2john archive.rar > hash.txt
	```
	
	-  [`7z2hashcat`](https://github.com/philsmd/7z2hashcat), a Perl script that outputs a hash in the format Hashcat can work with, for 7z archives:
	
	```bash
	perl 7z2hashcat.pl archive.7z
	```

2. **Crack the hash**
	- Use Hashcat or John the Ripper to crack the extracted hash:

	```bash
	hashcat -13600 hash.txt /usr/share/wordlists/rockyou.txt
	```

>[!note]+ Download `7z2hashcat`
>```bash
>curl -s -O https://raw.githubusercontent.com/philsmd/7z2hashcat/refs/heads/master/7z2hashcat.pl
>```

Hashcat modes for ZIP hashes:

| **Mode**  | **Target**                                  |
| --------- | ------------------------------------------- |
| **7-Zip** |                                             |
| `11600`   | 7-Zip                                       |
| **ZIP**   |                                             |
| `13600`   | WinZip                                      |
| `17200`   | PKZIP (Compressed)                          |
| `17210`   | PKZIP (Uncompressed)                        |
| `17220`   | PKZIP (Compressed Multi-File)               |
| `17225`   | PKZIP (Mixed Multi-File)                    |
| `17230`   | PKZIP (Compressed Multi-File Checksum-Only) |
| `20500`   | PKZIP Master Key                            |
| `20510`   | PKZIP Master Key (6-byte optimization)      |
| `23001`   | SecureZIP AES-128                           |
| `23002`   | SecureZIP AES-192                           |
| `23003`   | SecureZIP AES-256                           |
| **RAR**   |                                             |
| `12500`   | RAR3-hp                                     |
| `13000`   | RAR5                                        |
| `23700`   | RAR3-p (Uncompressed)                       |
| `23800`   | RAR3-p (Compressed)                         |

>[!example]+ Example: Cracking a 7z archive
>1. Extract the hash from the target archive file:
>```bash
>perl 7z2hashcat.pl hashcat.7z
>```
>```bash
>ATTENTION: the hashes might contain sensitive encrypted data. Be careful when sharing or posting these hashes
>$7z$0$19$0$$8$9c7684c204c437fa0000000000000000$1098215690$112$106$7395978cad9ad8b18aef51ba2f9dcf909a1bff70d240b1c8e98dffabd352d69a1f37978e5df0179860d0fe4754721ae3cbbee1b558d93cd27e0b2959efe44a00305f982527d19584d62bcf8c23cf89e24fd19db844108e452a26d4a8343d504fc3063744d081db1492ea1cdef7a9b983
>```
>2. Save the hash into a fire:
>```bash
>echo "$7z$0$19$0$$8$9c7684c204c437fa0000000000000000$1098215690$112$106$7395978cad9ad8b18aef51ba2f9dcf909a1bff70d240b1c8e98dffabd352d69a1f37978e5df0179860d0fe4754721ae3cbbee1b558d93cd27e0b2959efe44a00305f982527d19584d62bcf8c23cf89e24fd19db844108e452a26d4a8343d504fc3063744d081db1492ea1cdef7a9b983" > hash.txt
>```
>3. Use Hashcat and a wordlist of possible passwords to crack the hash:
>```bash
>hashcat -m 11600 hash.txt /usr/share/wordlists/rockyou.txt
>```
>```bash
> # result
>$7z$0$19$0$$8$9c7684c204c437fa0000000000000000$1098215690$112$106$7395978cad9ad8b18aef51ba2f9dcf909a1bff70d240b1c8e98dffabd352d69a1f37978e5df0179860d0fe4754721ae3cbbee1b558d93cd27e0b2959efe44a00305f982527d19584d62bcf8c23cf89e24fd19db844108e452a26d4a8343d504fc3063744d081db1492ea1cdef7a9b983:123456789a
>```
>4. Unarchive the file using the obtained password: 
> ```bash
> 7z x hashcat.7z
> ```
> ```bash
> 7-Zip [64] 16.02 : Copyright (c) 1999-2016 Igor Pavlov : 2016-05-21
> p7zip Version 16.02 (locale=en_US.UTF-8,Utf16=on,HugeFiles=on,64 bits,128 CPUs AMD EPYC 7543 32-Core Processor                 (A00F11),ASM,AES-NI)
> 
> Scanning the drive for archives:
> 1 file, 230 bytes (1 KiB)
> 
> Extracting archive: hashcat.7z
> 
> Enter password (will not be echoed):
> --
> Path = hashcat.7z
> Type = 7z
> Physical Size = 230
> Headers Size = 182
> Method = LZMA2:12 7zAES
> Solid = -
> Blocks = 1
> 
> Everything is Ok
> 
> Size:       33
> Compressed: 230
> ```
> After that, you can access files previously stored in the archive.
> ```bash
> cat flag.txt
> ```
## KeePass databases

**[KeePass](https://en.wikipedia.org/wiki/KeePass) databases (`.kdbx`)** store all entries (usernames, passwords, notes, attachments) in a single encrypted file. The entire database is encrypted, not just individual fields.

- Modern KeePass supports **[AES-256](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard)**, **[ChaCha20](https://en.wikipedia.org/wiki/Salsa20#ChaCha_variant)**, and **[Twofish](https://en.wikipedia.org/wiki/Twofish)** encryption algorithms. The default is AES-256.
- The database is protected by a **master key**. It can be a password, key file, and/or some other data (e.g., Windows user account data).

>[!note]+ The KDBX file starts with a header that contains metadata such as:
> - Encryption algorithm
> - Compression flags
> - Master seed (random value for key derivation) 
> - Transform seed (for KDF)
> - Transform rounds (work factor for KDF) 
> - Initialization vector (IV)
> - Stream start bytes (for stream cipher)
> - KDF variant library (for KDBX 4)
> - etc. 
> 

>[!info] The KDBX header includes a SHA-256 hash for integrity checks.

Cracking a password of a KeePass database involves the following steps:

1. **Extract the hash and relevant encryption metadata from the database file**
	- You can use the [`keepass2john.py`](https://gist.github.com/HarmJ0y/116fa1b559372804877e604d7d367bbc#file-keepass2john-py) script for this purpose.
	
	```bash
	python3 keepass2john.py database.kdbx > hash.txt
	```

2. **Crack the hash**
	- Use Hashcat or John the Ripper to crack the extracted hash:
	
	```bash
	hashcat -m 13400 hash.txt /usr/share/wordlists/rockyou.txt
	```

>[!note]+ Download `keepass2john.py`
>```bash
>curl -s -O https://gist.githubusercontent.com/HarmJ0y/116fa1b559372804877e604d7d367bbc/raw/c0c6f45ad89310e61ec0363a69913e966fe17633/keepass2john.py
>```

Hashcat modes for KeePass:

| **Mode** | **Target**                       |
| -------- | -------------------------------- |
| `13400`  | KeePass 1 AES / without keyfile  |
| `13400`  | KeePass 2 AES / without keyfile  |
| `13400`  | KeePass 1 Twofish / with keyfile |
| `13400`  | Keepass 2 AES / with keyfile     |
## Protected PDF files

[PDF](https://en.wikipedia.org/wiki/PDF) (Portable Document Format) files support two types of passwords:

- **User password (open password)**
	- Prevents opening the PDF without the correct password.

- **Owner password (permission password)**
	- Restricts printing, copying, or editing the document; enforcement depends on the viewer software.

PDF encryption metadata resides in the **encryption dictionary** at the **file's trailer**. The dictionary contains:

| Field              | Purpose                                                                                |
| ------------------ | -------------------------------------------------------------------------------------- |
| `Filter`           | Security handler name (e.g., `Standard`).                                              |
| `V`                | Algorithm revision (`1`–`6`); indicates key length and algorithm (RC4 or AES).         |
| `Length`           | Key length in bits (`40`, `128`, `256`).                                               |
| `R`                | Revision number; defines algorithm details (e.g., `R=3` for 128-bit RC4 with SHA-256). |
| `O`                | Owner password hash (encrypted file key with owner key).                               |
| `U`                | User password hash (encrypted file key with user key).                                 |
| `P`                | Permission flags bitmask.                                                              |
| `Encrypt Metadata` | Whether metadata streams are encrypted.                                                |

>[!interesting]+ How PDF encryption works
> 1. **Key Derivation**
>     - PDF versions prior to 2.0 use RC4 or AES-128 with a password padded/truncated to 32 bytes, then hashed (MD5 or SHA-256 depending on R).
>     - Newer versions (PDF 2.0) support AES-256-GCM and Argon2 KDF.
> 2. **Encryption**
>     - The derived key first decrypts the **file key** (from the `/O` or `/U` entry), and then that file key decrypts all encrypted objects (streams and strings).
> 3. **Verification:**
>     - After deriving a candidate file key, the handler decrypts the file’s metadata or a known plaintext (e.g., 32-byte padding string). If it matches the expected pattern, the password is correct.

Cracking a password of a PDF file involves the following steps:

1. **Extract the hash and relevant encryption metadata from the PDF file**
	- You can use [`pdf2john.py`](https://raw.githubusercontent.com/truongkma/ctf-tools/master/John/run/pdf2john.py) script for this:

```bash
python3 pdf2john.py inventory.pdf
```

2. **Crack the hash**
	- Use Hashcat or John the Ripper to crack the extracted hash:

```bash
hashcat -m 10500 hash.txt /usr/share/wordlists/rockyou.txt
```

>[!note]+ Download `pdf2john.py`
>```bash
>curl -s -O https://raw.githubusercontent.com/truongkma/ctf-tools/master/John/run/pdf2john.py
>```

Hashcat modes for PDF:

| **Mode** | **Target**                                 |
| -------- | ------------------------------------------ |
| `10400`  | PDF 1.1 - 1.3 (Acrobat 2 - 4)              |
| `10410`  | PDF 1.1 - 1.3 (Acrobat 2 - 4), collider #1 |
| `10420`  | PDF 1.1 - 1.3 (Acrobat 2 - 4), collider #2 |
| `10500`  | PDF 1.4 - 1.6 (Acrobat 5 - 8)              |
| `10600`  | PDF 1.7 Level 3 (Acrobat 9)                |
| `10700`  | PDF 1.7 Level 8 (Acrobat 10 - 11)          |
## Private SSH keys

Cracking a password of a PDF file involves the following steps:

1. **Extract the hash and relevant encryption metadata from the SSH key file**
	- You can use [`ssh2john.py`](https://github.com/openwall/john/blob/bleeding-jumbo/run/ssh2john.py) script

```bash
python3 ssh2john.py id_rsa > hash.txt
```

2. **Crack the hash**
	- Use Hashcat or John the Ripper to crack the extracted hash:

```bash
hashcat -m 10500 hash.txt /usr/share/wordlists/rockyou.txt
```

>[!note]+ Download `ssh2john.py`
>```bash
>curl -s -O https://raw.githubusercontent.com/openwall/john/refs/heads/bleeding-jumbo/run/ssh2john.py
>```

Hashcat modes for SSH keys:

| Mode    | Target                                        |
| ------- | --------------------------------------------- |
| `22911` | RSA/DSA/EC/OpenSSH Private Keys (`$0$`)       |
| `22921` | RSA/DSA/EC/OpenSSH Private Keys (`$6$`)       |
| `22931` | RSA/DSA/EC/OpenSSH Private Keys (`$1`, `$3$`) |
| `22941` | RSA/DSA/EC/OpenSSH Private Keys (`$4$`)       |
| `22951` | RSA/DSA/EC/OpenSSH Private Keys (`$5$`)       |
## References and further reading

- [`Microsoft Office password protection, AES since Office 2007 — Wikipedia`](https://en.wikipedia.org/wiki/Microsoft_Office_password_protection#AES_since_Office_2007)
- [`RC4, History — Wikipedia`](https://en.wikipedia.org/wiki/RC4#History)
- [`Key Derivation Function — Wikipedia`](https://en.wikipedia.org/wiki/Key_derivation_function)
- [`ZIP (file format), Encryption — Wikipedia`](https://en.wikipedia.org/wiki/ZIP_(file_format)#Encryption)
- [`PDF, Encryption and signatures — Wikipedia`](https://en.wikipedia.org/wiki/PDF#Encryption_and_signatures)
- [`KeePass.info`](https://keepass.info/)
- [`Master Key — KeePass.info`](https://keepass.info/help/base/keys.html)