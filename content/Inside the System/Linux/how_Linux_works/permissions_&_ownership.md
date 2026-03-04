---
created: 27-01-2026
---
## File permissions

- Every file in Linux has a set of permissions that determine whether users can read, write, or execute the file.
- Every file on a Linux system is **owned** by a user and a group. Owners have broad control over their objects. 

Display file permissions:

```bash
ls -l
```

>[!example]+
> ```bash
> ls -l
> ```
> 
> 
> ```bash
> drwxr-xr-x 3 trigger trigger 4096 Dec  4 17:39  Bash_scripting  
> -rw-r--r-- 1 trigger trigger 1546 Dec  5 14:36  permissions_&_ownership.md 
> -rw-r--r-- 1 trigger trigger   37 Nov 23 11:20  text_processing.md
> # ...
> ```

- The first column in the output **the permission flag set** for each file:

```bash
drwxr-xr--
 d rwx rwx rwx
 |  |   |   |
 |  |   |   |
 |  |   | others
 |  | group
 | user
 |
file type
```

- The first character indicates the **type of the file** (e.g., `d` for a directory or `-` for a regular file).
- Next, there are three 3-flag sets: the first for **user owner**, the second for **group owner** (pertains to all users who belong to the owner group of the file), and the third is for **others** (pertains to all other users). 
- The permission is set if its corresponding letter is present in the flag set. The dash character `-` in place of a letter means that this permission not set.

File types:
- `-` = regular file
- `d` = directory
- `l` = symlink
- `p` = pipe
- `s` = socket

Meaning of `rwx` on a **regular file**:
- **Read (`r`):** Permission to read the file's contents.
- **Write (`w`):** Permission to modify the file's contents or delete the file.
- **Execute (`x`):** Permission to execute the file as a program or script.

Meaning of `rwx` on a **directory**:
- **Read (`r`):** Permission to list the directory's contents (e.g., `ls`).
- **Write (`w`):** Permission to create, delete, and rename files _within_ the directory.
- **Execute (`x`):** Permission to traverse the directory (e.g., `cd` into it) and access information about the files within it (e.g., `ls -l`). Without `x`, you can't `cd` into the directory, even if you have `r` or `w` permissions.

>[!important] Directory permissions control access to the file's _metadata_ (the inode), not the files within.

Permissions are often represented numerically:
- `r` = 4
- `w` = 2
- `x` = 1

You sum them for each class (octal):
- `7` = `rwx` (4+2+1)
- `6` = `rw-` (4+2)
- `5` = `r-x` (4+1)
- `4` = `r--` (4)
- `0` = `---` (0)

>[!example]+
> This sets permissions of the `script.sh` to `rwxr-xr-x`:
> 
> ```bash
> chmod 755 myscript.sh
> ```
> 
## `rwx` (read-write-execute)

- `rwx` (read-write-execute) is the classic permission set you see with `ls -l`. 
- It's divided into three classes:
	- **User (owner)**
	- **Group**
	- **Others**

```bash
-rwxr-xr-- 1 user group 1024 Jan 1 12:00 script.sh


^^^^^^^^^^
| |  |  |
| |  |  +--- Others (everyone else)
| |  +------ Group (members of file's group)
| +--------- User (owner of the file)
+----------- File Type (- for file, d for directory, l for link, etc.)
```

## SUID, SGID, and sticky bit permissions 

Beyond standard permissions, Linux implements three special permission bits:

- **SUID (Set User ID)**: the `4000` bit
	- When set on an executable, the process runs with the privileges of the **user owner** of the file.
	- More specifically, when a file with the SUID bit is executed, the process runs with the **Effective User ID (EUID)** of the **file's owner**, not the user who executed it.
	- Displayed as `s` in the file owner's execute permission (e.g., `-rwsr-xr-x`).
	- **Octal Value:** `4` (e.g., `4755`)

>[!example]+ SUID and `passwd`
>The `passwd` (`/usr/bin/passwd`) executable is a SUID binary owned by root. This means that when a regular user invokes the `passwd` command, **the `passwd` process runs with the root privileges** (not with the privileges of the caller user).
> 
> ```bash
> ls -l /usr/bin/passwd
> ```
> 
> ```bash
> -rwsr-xr-x 1 root root 80856 Jun 27  2025 /usr/bin/passwd
> ```
>This is because to change a user's password `passwd` needs to modify the `/etc/shadow`, which is only writable by root.

Find all SUID files:

```bash
find / -perm -4000 -type f 2>/dev/null
```

- **SGID (Set Group ID)**: the `2000` bit
	- When a file with the SGID bit is executed, the process runs with the **Effective Group ID (EGID)** of the **file's group**.
	- This is more commonly used on directories. Any file or directory created within a directory with the SGID bit will automatically inherit the _group ownership_ of the parent directory, not the primary group of the user who created it.
	- Displayed as `s` in the group owner's execute permission (e.g., `-rwxr-sr-x`).
	- **Octal Value:** `2` (e.g., `2755`).

Find all SGID directories:

```bash
find / -perm -2000 -type d 2>/dev/null
```

>[!note] To learn more about the difference between real, effective, and set-user IDs of a process, see [[processes#Process IDs]].

- **Sticky bit**: the `1000` bit
	- When set on a directory, all files within that directory can be deleted **only by the file owners**.
	- A user can only delete or rename files within that directory if they are the owner of the file, or the owner of the directory, regardless of the write permissions on the directory itself.
	- The sticky bit **doesn't affect individual files**.
	- Displayed as `t` in the others' execute permission (e.g., `drwxrwxrwt`).
	- **Octal Value:** `1` (e.g., `1777`)

>[!example]+
> The sticky bit is set on the `/tmp` directory. It's world-writable, but you don't want users deleting each other's temporary files.

>[!tip]+ SGID on a directory
>If SGID is set on a directory, new files created within that directory inherit the group of the directory rather than the group of the user who created the file.

Find all directories with the sticky bit set:

```bash
find / -perm -1000 -type d 2>/dev/null
```

In octal representation, SUID, SGID, and sticky bit permissions occupy a digit before traditional `rwx` permissions. To represent a file with multiple permissions, the respective octal values are summed:

```bash
chmod 4755 program   # SUID
chmod 2755 program   # SGID
chmod 1755 directory # SGID + sticky bit
```

| Permission    | Octal value | Permission       | Octal value |
| ------------- | ----------- | ---------------- | ----------- |
| `r` (read)    | `4`         | `s` (SUID)       | `4`         |
| `w` (write)   | `2`         | `s` (SGID)       | `2`         |
| `x` (execute) | `1`         | `t` (sticky bit) | `1`         |

>[!example]+ Example: SUID, SGID, and sticky bits
> - SUID:
> ```bash
> find / -type f -perm -4000 -ls 2>/dev/null
> ```
> ```bash
> # ...
>   281940     20 -rwsr-xr-x   1 root     root        18528 Jun 24 12:45 /usr/bin/newgrp  
>   281431     80 -rwsr-xr-x   1 root     root        80856 Jun 27 09:35 /usr/bin/passwd  
> # ...
> ```
> - SGID:
> ```bash
> find / -type f -perm -2000 -ls 2>/dev/null
> ```
> ```bash
> # ...
>   281989     24 -rwxr-sr-x   1 root     tty         22616 Jun 24 12:45 /usr/bin/write  
>   281985     24 -rwxr-sr-x   1 root     tty         22616 Jun 24 12:45 /usr/bin/wall
> # ...
> ```
> - Sticky bit:
> ```bash
> find / -type d -perm /1000 -ls 2>/dev/null
> ```
> 
> ```bash
>  2621800      4 drwxrwxrwt   6 root     root         4096 Sep 17 08:49 /var/tmp  
>     1143      0 drwxrwxrwt   2 root     root           40 Sep 17 08:49 /dev/mqueue  
>        1      0 drwxrwxrwt   2 root     root           40 Sep 17 10:30 /dev/shm  
>        1      0 drwxrwxrwt  25 root     root          580 Sep 17 10:30 /tmp
> ```

>[!bug]+ Missing sticky bit
>Missing sticky bit on world-writable directories like `/tmp` or `/var/tmp` allows you to delete other uses' file from there.
>If it happens to be an executable, you can override it. The user who launches the program with the same name will execute your commands. 
## Access Control Lists

>Linux **Access Control Lists (ACLs)** provide an additional, more granular permission system that the traditional `ugp`/`rwx`.

- ACLs are a set of rules that are checked in addition to the standard permissions. They can be used to set permissions for specific users or groups.

- ACLs can be:
	- **Access ACLs:** Control access to a specific file or directory.
	- **Default ACLs:** A template ACL that is automatically inherited by new files and directories created within a parent directory. They are **only applicable to directories**.


>[!important] For ACLs to work, the filesystem in question must be mounted with the `acl` mount option (check it in `/etc/fstab`).
>The `acl` option may also be active as a default mount option; this is the case for Btrfs and Ext2/3/4. Check it with:
>```bash
>sudo tune2fs -l /dev/sdXY | grep "Default mount options"
>```
>```bash
>Default mount options:    user_xattr acl
>```

- Get ACLs for a file or directory:

```bash
getfacl <file>
```

>[!example]+
>```bash
>getfacl file_name
>```
> ```bash
> # file: file_name  
> # owner: trigger  
> # group: trigger  
> user::rwx  
> group::r-x  
> other::r-x
> 
> user:alice: rw-
> group:auditors: r--
> group:: r-x
> → mask: rwx (union)
> 
> Effective rights:
> alice: rw-
> auditors: r--
> group:: r-x
> ```

>[!note] Output shows `user`, `group`, `other`, and then specific entries like `user:username:rw-` and `group:auditors:r--`.

To modify the ACLs, use the `setfacl` command:

- Modify (add/set) an ACL for a user `username`:

```bash
setfacl -m u:username:rw file.txt
```

- Modify an ACL for a group `auditors`:

```bash
setfacl -m g:auditors:r /directory
```

- Remove an ACL for user `username`:

```bash
setfacl -x u:username file.txt
```

- Remove all ACLs:

```bash
setfacl -b file.txt
```

- Set a *default* ACL for the `auditors` group on the `/directory` directory:

```bash
setfacl -d -m g:auditors:rwx /directory
```

>[!note] If a file has an ACL, a `+` sign will appear at the end of the permissions string (e.g., `rw-r-----+`).

## Extended attributes (`xattr`)

>**Extended attributes** are `name:value` pairs permanently associated with files and directories.

- In short, extended attributes provide filesystem-level flags that enforce specific behaviors. Even the `root` user must obey these attributes.

- The `getfattr` command can be used to display a list of extended attributes of a particular file:

```bash
getfattr <file>
```

- The `lsattr` command lists files in a directory along with their attributes:

```bash
lsattr
```

> [!example]+
> ```bash
> lsattr
> ```
> 
> ```
> --------------e------- ./09_-_walt.mp3
> --------------e------- ./11_-_Fa.mp3
> --------------e------- ./12_-_nc17.mp3
> ...
> ```

- List attributes of files and directories recursively, use the `-R` option:

```bash
lsattr -R
```

To modify extended attributes, use the `chattr` command.

- Add an extended attribute:

```bash
chattr +i file.txt # makes file.txt immutable
```

- Remove an extended attribute:

```bash
chattr -i file.txt # make file.txt mutable again
```

>[!warning] The `e` extended attribute can't be removed with `chattr`.

| Letter | Name                               | Description                                                                                                                                                                                                                                                                                                                                                                      |
| ------ | ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `a`    | append-only                        | The file can only be opened for appending, i.e., data can only be added at the end of the file.<br>This attribute is often used for log flies.                                                                                                                                                                                                                                   |
| `A`    | no `atime` updates                 | The `atime` record of the file is not modified.<br>Avoids a certain amount of disk I/O.                                                                                                                                                                                                                                                                                          |
| `c`    | compressed                         | The file will be automatically compressed on the disk by kernel. <br>A read from this file returns uncompressed data, and a write to this file compresses data before storing them on the disk.                                                                                                                                                                                  |
| `C`    | no copy on write                   | The file will not be subject to copy-on-write updates.<br>The file system does not create a copy of the file’s blocks in memory when a process opens the file for writing, bur rather directly modifies the original file blocks on disk.<br>This means that any changes made by one process will be immediately visible to other processes that have the file open for reading. |
| `d`    | no dump                            | The file is not a candidate for backup when the [`dump`](https://linux.die.net/man/8/dump) program is run (ext2/3)                                                                                                                                                                                                                                                               |
| `D`    | synchronous directory updates      | The changes to the directory are written synchronously to the disk. <br>Equivalent to the `dirsync` mount option.                                                                                                                                                                                                                                                                |
| `e`    | extent format                      | Indicates that the file is using extents for mapping the blocks on disk. Can not be removed with `chattr`.                                                                                                                                                                                                                                                                       |
| `F`    | case-insensitive directory lookups | The file is encrypted by the filesystem. <br>Can not be set or cleared with `chattr`.                                                                                                                                                                                                                                                                                            |
| `i`    | immutable                          | The file can not be modified, deleted, renamed, or linked to; the file can not be opened in the write mode.<br>The attribute can only be set by root; it is useful for protecting important files or scripts. <br>                                                                                                                                                               |
| `I`    | indexed directory                  | Indicates that the directory is being indexed using hashed trees. Can not be set or cleared with `chattr`.                                                                                                                                                                                                                                                                       |
| `j`    | data journaling                    | Any changes to the file will first be written to a journal, aka a log, before being written to the filesystem.<br>Used to improve filesystem reliability, since journal will allow to recover the latest file data on, say, system crash, avoiding data corruption or loss.                                                                                                      |
| `m`    | don't compress                     | The file will not be compressed on the filesystems that support per-file comression.                                                                                                                                                                                                                                                                                             |
| `N`    | inline data                        | The data of the file are stored inline, withing the inode itself.                                                                                                                                                                                                                                                                                                                |
| `s`    | secure deletion                    | When the file is being deleted, the file blocks are zeroed and written back to the disk.                                                                                                                                                                                                                                                                                         |
| `S`    | synchronous updates                | The changes to the file are written synchronously to the disk. Equivalent to the `sync` mount option.                                                                                                                                                                                                                                                                            |
| `u`    | undeletable                        | When the file with this attribute is deleted, its contents are saved. The file can be undeleted.                                                                                                                                                                                                                                                                                 |

>[!note] See [`chattr`](https://man.archlinux.org/man/chattr.1) for a full list of attributes.

>[!note] Not all filesystems support every attribute.
## References and further reading

- [`Access Control Lists — Arch Wiki`](https://wiki.archlinux.org/title/Access_Control_Lists)
- [`Extended attributes — Arch Wiki`](https://wiki.archlinux.org/title/Extended_attributes)
- [`xattr — man pages`](https://man.archlinux.org/man/xattr.7)
- [`chattr — man pages`](https://man.archlinux.org/man/chattr.1)