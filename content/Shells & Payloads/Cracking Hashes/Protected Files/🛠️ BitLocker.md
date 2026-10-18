---
created: 2026-09-04
updated: 2026-10-09
---
## BitLocker

>[BitLocker](https://learn.microsoft.com/en-us/windows/security/operating-system-security/data-protection/bitlocker/#device-encryption) is a full disk encryption feature integrated into Microsoft Windows.

- BitLocker can be used for **full-disk encryption** to protect data at rest.

## How BitLocker works

- BitLocker uses the [AES](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard) encryption algorithm with either 128-bit or 256-bit keys. 
- It can also operate in **[CBC](https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#CBC)** mode or more secure **[XTS](https://en.wikipedia.org/wiki/Disk_encryption_theory#XTS)** mode, depending on Windows version and configuration.
- Access to the encrypted disk can be protected by various mechanisms like [TPM](https://en.wikipedia.org/wiki/Trusted_Platform_Module) (Trusted Platform Module), PIN, password, or a USB security token. If the correct credentials are provided, the full volume decrypts automatically at boot.
- If the password or PIN used for BitLocker is forgotten, decryption can still be performed using a recovery key— a 48-digit string generated during the setup process.

BitLocker can encrypt:
- Entire physical disks (HDD, SSD)
- Partitions on physical media
- Removable drives
- Virtual disks such as [VHD and VHDX](https://en.wikipedia.org/wiki/VHD_(file_format)).

 >[!note]+ BitLocker supports NTFS, FAT16, FAT32, and exFAT filesystems.
> - The **operating system drive must be formatted with the NTFS filesystem**.
> - Depending on the firmware, the system drive must be formatted with either FAT32 or NTFS:
> 	- For **UEFI**, the system drive should be formatted with **FAT32**.
> 	- For **BIOS**, the system drive should be formatted with **NTFS**.

BitLocker supports several protection combinations:

- TPM-only
- TPM + PIN
- TPM + PIN + USB key
- TPM + USB key
- USB Key (only with changes to GPOs)  
- Password (only with changes to GPOs)  
### File formats

BitLocker works mainly with physical drives and partitions formatted with supported filesystems

## Cracking BitLocker-encrypted drives

>**[`bitlocker2john`](https://github.com/openwall/john/blob/bleeding-jumbo/run/bitlocker2john.py)** is a script designed to extract password hashes from BitLocker-encrypted volumes or VHD files into a format compatible with [[🛠️ JohnTheRipper]].

>[!interesting]+ How `bitlocker2john` works
>- `bitlocker2john` first parses the BitLocker metadata from the image file or volume and extracts four different hashes:
>	- The first two correspond to the BitLocker password protector.
>	- The last two correspond to the recovery key protector.
>- The tool they filters out the hash related to password protection. This is usually the `$bitlocker$0$...` hash. 
>- Then it converts these to a text format John understands.

>[!note]+ On the recovery key
>Regardless of the authentication method chosen, during encryption, BitLocker asks the user where to store a Recovery Password that can be used to restore the access to the encrypted unit in case they can't unlock it normally. 
>The Recovery Password is a randomly-generated 48-digit key:
>```
>236808-089419-192665-495704-618299-073414-538373-542366
>```
>However, since this password is so long and random, it's impractical to guess it.


1. Extract hashes from a BitLocker volume or VHD image:

```bash
bitlocker2john -i backup.vhd > backup.hashes
```

2. Filter the password-protector hashes:

```bash
grep "bitlocker\$0" backup.hashes > password.hash
```

3. Crack the hash with JohnTheRipper or Hashcat (mode `22100`):

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt password.hash
```

```bash
hashcat -a 0 -m 22100 <hash-file> <wordlist>
```

- The script primarily targets BitLocker password or PIN-protected hashes rather 



## Mounting BitLocker-encrypted drives in Linux

It is possible to mount BitLocker-encrypted drives in Linux or macOS with the tool called [`dislocker`](https://github.com/Aorimn/dislocker).

>[!note]+ Installation
>```bash
>sudo apt-get install dislocker
>```

1. Create two folders:

```bash
sudo mkdir -p /media/bitlocker && sudo mkdir -p /media/bitlockermount
```

2. Use `losetup` to configure the VHD as [loop device](https://en.wikipedia.org/wiki/Loop_device):

```bash
sudo losetup -f -P Backup.vhd
```

3. Decrypt the drive using `dislocker`:

```bash
sudo dislocker /dev/loop0p2 -u<user_password> -- /media/bitlocker
```

4. Mount the decrypted volume:

```bash
sudo mount -o loop /media/bitlocker/dislocker-file /media/bitlockermount
```
## Example

Suppose we have a BitLocker-encrypted VHD file: 

```bash
Private.vhd
```

To extract the hash, use the `bitlocker2john` tool:


```bash
bitlocker2john -i Private.vhd > Private.hashes
```

```bash
Signature found at 0x10003
Version: 8 
Invalid version, looking for a signature with valid version...

Signature found at 0x2200000
Version: 2 (Windows 7 or later)

VMK entry found at 0x22000bb

VMK encrypted with User Password found at 22000dc
VMK encrypted with AES-CCM

VMK entry found at 0x220019b

VMK encrypted with Recovery Password found at 0x22001bc
Searching AES-CCM from 0x22001d8
Trying offset 0x220026b....
VMK encrypted with AES-CCM!!

Signature found at 0x2956000
Version: 2 (Windows 7 or later)

VMK entry found at 0x29560bb

VMK entry found at 0x295619b

Signature found at 0x30ab000
Version: 2 (Windows 7 or later)

VMK entry found at 0x30ab0bb

VMK entry found at 0x30ab19b
```

- The tool searches for BitLocker **signatures** that mark the start of BitLocker metadata blocks.
- For example, `Signature found at 0x10003` indicates the tool found a BitLocker header at offset `0x10003` bytes.
- VMK stands for Volume Master Key. The scripts finds several VMK entries in the metadata, each representing a key protector.
- The VMK entries show encryption with AES in CCM mode, the specific block cipher mode BitLocker uses.
- Finding VMK encrypted with user password means password-based authentication data is available.

The `Private.hashes` file contains the following:

```bash
cat Private.hashes
```

```bash
Encrypted device Private.vhd opened, size 64MB
UP Nonce: b020fe18bbb1db0103000000
UP MAC: e9c6b548788aeff190e517b0d85ada5d
UP VMK: aad7a0a3f40c4467307011ac17f79f8c99768419903025fd7072ee78b15a729afcf54b8c2e3af05bb18d4ba0

Salt: 1d06e8b3aa5f14ddcb5ad7415c1d24f5
RP Nonce: b020fe18bbb1db0106000000
RP MAC: 8ff2e9cdd6ec25df9060e95e3c490a9a
RP VMK: efd5601f4cefa47da810339f809a90187cbbd907bd1077565293727114f3c218c078e03f2f8baa214f1de800


User Password hash:
$bitlocker$0$16$b3c105c7ab7faaf544e84d712810da65$1048576$12$b020fe18bbb1db0103000000$60$e9c6b548788aeff190e517b0d85ada5daad7a0a3f40c4467307011ac17f79f8c99768419903025fd7072ee78b15a729afcf54b8c2e3af05bb18d4ba0
Hash type: User Password with MAC verification (slower solution, no false positives)
$bitlocker$1$16$b3c105c7ab7faaf544e84d712810da65$1048576$12$b020fe18bbb1db0103000000$60$e9c6b548788aeff190e517b0d85ada5daad7a0a3f40c4467307011ac17f79f8c99768419903025fd7072ee78b15a729afcf54b8c2e3af05bb18d4ba0
Hash type: Recovery Password fast attack
$bitlocker$2$16$1d06e8b3aa5f14ddcb5ad7415c1d24f5$1048576$12$b020fe18bbb1db0106000000$60$8ff2e9cdd6ec25df9060e95e3c490a9aefd5601f4cefa47da810339f809a90187cbbd907bd1077565293727114f3c218c078e03f2f8baa214f1de800
Hash type: Recovery Password with MAC verification (slower solution, no false positives)
$bitlocker$3$16$1d06e8b3aa5f14ddcb5ad7415c1d24f5$1048576$12$b020fe18bbb1db0106000000$60$8ff2e9cdd6ec25df9060e95e3c490a9aefd5601f4cefa47da810339f809a90187cbbd907bd1077565293727114f3c218c078e03f2f8baa214f1de800
```

The hash we search for starts with `$bitlocker$0$...`:

```bash
grep "bitlocker\$0" Private.hashes > Private.hash
```

```bash
cat Private.hash
```

```bash
$bitlocker$0$16$b3c105c7ab7faaf544e84d712810da65$1048576$12$b020fe18bbb1db0103000000$60$e9c6b548788aeff190e517b0d85ada5daad7a0a3f40c4467307011ac17f79f8c99768419903025fd7072ee78b15a729afcf54b8c2e3af05bb18d4ba0
```

You can crack this cash with [[Hashcat]] mode `22100`:

```bash
hashcat -a 0 -m 22100 Private.hash /usr/share/wordlists/rockyou.txt
```

```bash
hashcat (v6.2.6) starting

OpenCL API (OpenCL 3.0 PoCL 3.1+debian  Linux, None+Asserts, RELOC, SPIR, LLVM 15.0.6, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
==================================================================================================================================================
* Device #1: pthread-haswell-AMD EPYC 7543 32-Core Processor, skipped

OpenCL API (OpenCL 2.1 LINUX) - Platform #2 [Intel(R) Corporation]
==================================================================
* Device #2: AMD EPYC 7543 32-Core Processor, 3923/7910 MB (988 MB allocatable), 4MCU

Minimum password length supported by kernel: 4
Maximum password length supported by kernel: 256

Hashes: 1 digests; 1 unique digests, 1 unique salts
Bitmaps: 16 bits, 65536 entries, 0x0000ffff mask, 262144 bytes, 5/13 rotates
Rules: 1

Optimizers applied:
* Single-Hash
* Single-Salt
* Slow-Hash-SIMD-LOOP

Watchdog: Hardware monitoring interface not found on your system.
Watchdog: Temperature abort trigger disabled.

Host memory required for this attack: 0 MB

Dictionary cache building /usr/share/wordlists/rockyou.txt: 33553434 bytesDictionary cache built:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344392
* Bytes.....: 139921507
* Keyspace..: 14344385
* Runtime...: 1 sec

$bitlocker$0$16$b3c105c7ab7faaf544e84d712810da65$1048576$12$b020fe18bbb1db0103000000$60$e9c6b548788aeff190e517b0d85ada5daad7a0a3f40c4467307011ac17f79f8c99768419903025fd7072ee78b15a729afcf54b8c2e3af05bb18d4ba0:francisco
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 22100 (BitLocker)
Hash.Target......: $bitlocker$0$16$b3c105c7ab7faaf544e84d712810da65$10...8d4ba0
Time.Started.....: Sat Oct 18 09:26:55 2025 (12 secs)
Time.Estimated...: Sat Oct 18 09:27:07 2025 (0 secs)
Kernel.Feature...: Pure Kernel
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#2.........:       44 H/s (5.55ms) @ Accel:64 Loops:4096 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 512/14344385 (0.00%)
Rejected.........: 0/512 (0.00%)
Restore.Point....: 448/14344385 (0.00%)
Restore.Sub.#2...: Salt:0 Amplifier:0-1 Iteration:1044480-1048576
Candidate.Engine.: Device Generator
Candidates.#2....: lover -> letmein

Started: Sat Oct 18 09:26:40 2025
Stopped: Sat Oct 18 09:27:08 2025hashcat -a 0 -m 22100 Private.hash /usr/share/wordlists/rockyou.txt
hashcat (v6.2.6) starting

OpenCL API (OpenCL 3.0 PoCL 3.1+debian  Linux, None+Asserts, RELOC, SPIR, LLVM 15.0.6, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
==================================================================================================================================================
* Device #1: pthread-haswell-AMD EPYC 7543 32-Core Processor, skipped

OpenCL API (OpenCL 2.1 LINUX) - Platform #2 [Intel(R) Corporation]
==================================================================
* Device #2: AMD EPYC 7543 32-Core Processor, 3923/7910 MB (988 MB allocatable), 4MCU

Minimum password length supported by kernel: 4
Maximum password length supported by kernel: 256

Hashes: 1 digests; 1 unique digests, 1 unique salts
Bitmaps: 16 bits, 65536 entries, 0x0000ffff mask, 262144 bytes, 5/13 rotates
Rules: 1

Optimizers applied:
* Single-Hash
* Single-Salt
* Slow-Hash-SIMD-LOOP

Watchdog: Hardware monitoring interface not found on your system.
Watchdog: Temperature abort trigger disabled.

Host memory required for this attack: 0 MB

Dictionary cache building /usr/share/wordlists/rockyou.txt: 33553434 bytesDictionary cache built:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344392
* Bytes.....: 139921507
* Keyspace..: 14344385
* Runtime...: 1 sec

$bitlocker$0$16$b3c105c7ab7faaf544e84d712810da65$1048576$12$b020fe18bbb1db0103000000$60$e9c6b548788aeff190e517b0d85ada5daad7a0a3f40c4467307011ac17f79f8c99768419903025fd7072ee78b15a729afcf54b8c2e3af05bb18d4ba0:francisco
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 22100 (BitLocker)
Hash.Target......: $bitlocker$0$16$b3c105c7ab7faaf544e84d712810da65$10...8d4ba0
Time.Started.....: Sat Oct 18 09:26:55 2025 (12 secs)
Time.Estimated...: Sat Oct 18 09:27:07 2025 (0 secs)
Kernel.Feature...: Pure Kernel
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#2.........:       44 H/s (5.55ms) @ Accel:64 Loops:4096 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 512/14344385 (0.00%)
Rejected.........: 0/512 (0.00%)
Restore.Point....: 448/14344385 (0.00%)
Restore.Sub.#2...: Salt:0 Amplifier:0-1 Iteration:1044480-1048576
Candidate.Engine.: Device Generator
Candidates.#2....: lover -> letmein

Started: Sat Oct 18 09:26:40 2025
Stopped: Sat Oct 18 09:27:08 2025
```

Or John:

```bash
Created directory: /home/htb-ac-1908986/.john
Note: This format may emit false positives, so it will keep trying even after finding a possible candidate.
Using default input encoding: UTF-8
Loaded 1 password hash (BitLocker, BitLocker [SHA-256 AES 32/64])
Cost 1 (iteration count) is 1048576 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
francisco        (?) 
```



1. Create two folders:

```bash
sudo mkdir -p /media/bitlocker && sudo mkdir -p /media/bitlockermount
```

2. Use `losetup` to configure the VHD as [loop device](https://en.wikipedia.org/wiki/Loop_device):

```bash
sudo losetup -f -P Private.vhd
```

3. Decrypt the drive using `dislocker`:

```bash
sudo dislocker /dev/loop0p1 -ufrancisco -- /media/bitlocker
```

4. Mount the decrypted volume:

```bash
sudo mount -o loop /media/bitlocker/dislocker-file /media/bitlockermount
```

After that, the volume will be accessible as a block device:

```bash
lsblk
```

```bash
NAME      MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
loop0       7:0    0   64M  0 loop 
└─loop0p1 259:0    0   61M  0 part 
loop1       7:1    0   61M  0 loop /media/bitlockermount
vda       254:0    0   40G  0 disk 
├─vda1    254:1    0   39G  0 part /
├─vda2    254:2    0    1K  0 part 
└─vda5    254:5    0  975M  0 part [SWAP]
```

```bash
cd /media/bitlockermount/
```

```bash
ls -la
```

```bash
total 17
drwxrwxrwx 1 root root 4096 Apr 20 01:10  .
drwxr-xr-x 5 root root 4096 Oct 19 03:29  ..
-rwxrwxrwx 1 root root   32 Apr 20 01:11  flag.txt
drwxrwxrwx 1 root root 8192 Apr 20 01:12 'System Volume Information'
```
## My questions

- Why does `dislocker` need two folders?
- What exactly are we cracking in the above example? 
- Why `$bitlocker$0$...` hash and not other?
- How to deal with different types of BitLocker protection?
- How BitLocker works?
## References and further reading

- [`BitLocker — Wikipedia`](https://en.wikipedia.org/wiki/BitLocker)
- [`VHD (file format) — Wikipedia`](https://en.wikipedia.org/wiki/VHD_(file_format))

- [`Loop device — Wikipedia`](https://en.wikipedia.org/wiki/Loop_device)


- [`BitLocker overview — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/security/operating-system-security/data-protection/bitlocker/#device-encryption)

- [`Manage Virtual Hard Disks (VHDs) — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/storage/disk-management/manage-virtual-hard-disks)


- [`A Deep Dive into TPM-based BitLocker Drive Encryption — itm4n`](https://itm4n.github.io/tpm-based-bitlocker/)
- [`Go away BitLocker, you're drunk — LuemmelSec`](https://luemmelsec.github.io/Go-away-BitLocker-you-are-drunk/)

- [`OpenCL BitLocker — openwall.info`](https://openwall.info/wiki/john/OpenCL-BitLocker)
