---
created: 09-01-2026
tags:
  - Linux_PrivEsc
  - Linux
---
## Hunting for credentials and sensitive information

In the context of Linux privilege escalation, credential hunting is often the path of least resistance. Administrators and developers routinely leave credentials in plaintext within configuration files, environment variables, and shell histories. If you can find these secrets, you can get access in bypass of any complex exploits. 

You're searching for:
- Plaintext passwords
- Password hashes
- SSH private keys
- API tokens
- Database credentials 
## Initial context

- System information:

```bash
uname -a
```

- Current user:

```bash
id
```

- Current directory:

```bash
pwd
```

## `/etc/passwd` and `/etc/shadow`

>The **`/etc/passwd` file** contains information about every user on the system, along with some additional information about them, such as user IDs, group IDs, home directories, and default shells.

- By default, `/etc/passwd` is readable by all users and services.

```bash
cat /etc/passwd
```

- Each line in the file corresponds to a single user and consists of seven colon-separated (`:`) fields:

```bash
username:password:UID:GID:GECOS:home_directory:login_shell
```

```bash
root:x:0:0:,,,:/root:/bin/bash
 |   | | |  |   |     |  
 |   | | |  |   |   shell
 |   | | |  |  home directory   
 |   | | | GECOS
 |   | | GID (Group ID)
 |   | UID (User ID)
 |  password
 username
```

- Any user with UID `0` is root.
 - If a user's shell is set to `/bin/false` or `/usr/sbin/nologin`, **the user can not log in interactively**. More precisely, a shell can be called, but it exits immediately after the start.
- `!` or `*` in the password field indicates that the user **can not login using a password**. In this case, however, the user may still be able to login via other methods, such as SSH.
- `x` in the password field indicates that the password hash is stored in the `/etc/shadow` file. 
 - Empty password field `::` (no characters between colons) means that **no password is required to login**.

>[!note] If you find a user in `/etc/passwd` with an empty password field, you can authenticate with `su`:
> 
> ```bash
> su username
> ```

>The **`/etc/shadow` file** stores hashes of user passwords and other sensitive information.

- `/etc/shadow` is normally only readable by root, but it's worth checking:

```bash
ls -l /etc/shadow
```

If you can read it, try cracking password hashes.

>[!note] See [[insecure_file_permissions]].

## Home directories

- List user home directories:

```bash
ls -la /home
```

- Find files readable by the current user in home directories:

```bash
find /home -type f -readable 2>/dev/null
```

- Find files writable by the current user in home directories:

```bash
find /home -type f -writable 2>/dev/null
```

- Recursively list content of user home directories (recursion depth 3 for readability): 

```bash
cd /home && find -maxdepth 3 -type d -ls
```

### SSH keys and configuration

- SSH configuration and keys for the current user:

```bash
ls -la ~/.ssh
```

- SSH directories for all users:

```bash
find /home -name ".ssh" -type d 2>/dev/null
```

- Private SSH keys across all user directories:

```bash
find /home -name "id_*" -o name "*.pem" 2>/dev/null
```

```bash
find /home -name "id_rsa*" -o -name "id_dsa*" -o -name "id_ecdsa*" -o -name "id_ed25519*" 2>/dev/null
```

- SSH authorized key files:

```bash
find /home -name "authorized_keys" -ls 2>/dev/null
```

>[!note] If you can write to a user's `~/.ssh/authorized_keys`, you can append your own public key and login as that user.

>[!note] The key might be encrypted (passphrase protected). Use `ssh2john` to convert the key to a hash format for John the Ripper and crack it.

### Shell configuration

- Shell startup files may contain:
	- Exported secrets
	- Aliases with passwords
	- Debug leftovers
	- Hardcoded API keys
	- Installed shells:

Shell startup files (`bashrc`, `profile`, etc.) are often used to set environment variables permanently or add aliases. Developers sometimes export API keys or database passwords here for convenience.

- Check Bash startup files for sensitive information:

```bash
cat ~/.bashrc
cat ~/.bash_profile
cat ~/.profile
cat ~/.bash_login
cat /etc/profile
```

- Zsh startup scripts:

```bash
cat ~/.zshrc
cat ~/.zprofile
```

>[!note] See [[shells]] for more. 

### Shell history

- Current shell command history:

```bash
history
```

- Bash/Zsh history:

```bash
cat ~/.bash_history
```

```bash
cat ~/.zsh_history
```

```bash
cat ~/.history
```

- Where command history is saved by Zsh:

```bash
echo $HISTFILE
```

- Find history files:

```bash
find / -type f -name "*hist*" -ls 2>/dev/null
```

### Dot files and user-specific data

Modern Linux systems adhere to the [`XDG Base Directory Specification`](https://specifications.freedesktop.org/basedir/latest/)  that defines standard locations for storing user-specific data. This includes environment variables and default locations that operating systems and applications may use:

| Variable           | Default path                    | Description                                                                                            |
| ------------------ | ------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `$XDG_DATA_HOME`   | `~/.local/share/`               | User-specific data files.                                                                              |
| `$XDG_CONFIG_HOME` | `~/.config/`                    | User-specific configuration files.                                                                     |
| `$XDG_CACHE_HOME`  | `~/.cache`                      | User-specific non-essential (cached) data.                                                             |
| `$XDG_RUNTIME_DIR` | `/run/user/UID`                 | User-specific runtime files and other file objects.                                                    |
| `$XDG_STATE_HOME`  | `~/.local/state`                | User-specific stat data.                                                                               |
| `$XDG_DATA_DIRS`   | `/usr/local/share/:/usr/share/` | A set of preference ordered base directories relative to which data files should be searched.          |
| `$XDG_CONFIG_DIRS` | `/etc/xdg`                      | A set of preference ordered base directories relative to which configuration files should be searched. |
Check these directories for any sensitive data or configuration.

- View all `XDG*` environment variables:

```bash
env | grep XDG
```

>[!example]-
> ```bash
> env | grep XDG
> ```
> ```
> XDG_CONFIG_DIRS=/etc/xdg
> XDG_SESSION_PATH=/org/freedesktop/DisplayManager/Session1
> XDG_MENU_PREFIX=hyprland-
> XDG_BACKEND=wayland
> XDG_DATA_HOME=/home/trigger/.local/share
> XDG_CONFIG_HOME=/home/trigger/.config
> XDG_SEAT=seat0
> XDG_SESSION_DESKTOP=Hyprland
> XDG_SESSION_TYPE=wayland
> XDG_CURRENT_DESKTOP=Hyprland
> XDG_SEAT_PATH=/org/freedesktop/DisplayManager/Seat0
> XDG_CACHE_HOME=/home/trigger/.cache
> XDG_SESSION_CLASS=user
> XDG_VTNR=1
> XDG_SESSION_ID=2
> XDG_STATE_HOME=/home/trigger/.local/state
> XDG_RUNTIME_DIR=/run/user/1000
> XDG_DATA_DIRS=/usr/local/share:/usr/share
> ```

- `~/.cache/`
	- Programs placing data in the `~/.cache/` directory expect that it might be deleted; this data is considered "non-essential" but remains persistent over time and across login sessions and reboots.
	- Often used by browsers to cache static files, by email clients to store cached email and calendars, and any other cache data stored by programs for performance.
- `~/.config/`
	- The user’s `~/.config/` directory is supposed to contain only configuration data, but many application developers use it for other things, such as history and cached information. 
	- Files in `~/.config/` may end in `*rc` or have extensions of `.conf`, `.ini`, `.xml`, `.yaml`, or other configuration formats; most files found here are regular text files.
	- Often used to store general configuration of different applications, application extensions and plug-ins, cookies for some browsers, or any other arbitrary configuration data stored by programs.
- `~/.local/share/`
	- Intended to store persistent data accumulated or generated by applications. 
	- This includes distribution-specific configuration, graphical login session configuration, desktop-specific configuration, and any other persistent data stored by programs.

>[!note] See [`XDG Base Directory — Arch Wiki`](https://wiki.archlinux.org/title/XDG_Base_Directory) for more information.


```bash
ls -la ~/.config/
```

```bash
ls -la ~/.local/share/
```

| Directory       | Description                                                                                  |
| --------------- | -------------------------------------------------------------------------------------------- |
| `.ssh/`         | SSH configuration, keys, and list of known hosts visisted.                                   |
| `.gnupg/`       | GPG configuration, keys, and other people's added public keys.                               |
| `.thunderbird/` | Email and calendar accounts, and synchronized email and calendar content for offline access. |
| `.mozilla/`     | Firefox configuration, cookies, bookmarks, browsing history, and plug-ins.                   |
| `.zoom/`        | Zoom configuration, logs, call history, and shared data.                                     |
| `.john/`        | John the Ripper password-cracking history with discovered passwords.                         |
| `.ICAClient/`   | Citrix client configuration, cache, logs, and other data.                                    |

Directories in `~/.config`:
- `~/.config/obs-studio/basic/profiles/...`: Might contain stream keys.
- `~/.config/steam/`: Steam session data.
- `~/.config/mc/`: Midnight Commander configuration (sometimes contains FTP credentials).

High-value dot files:
- `~/.lesshst`: History of files viewed with `less`.
- `~/.viminfo`: Search/command history for `vim` and recent files edited.
- `~/.mysql_history`: MySQL query history.
- `~/.pgpass`: PostgreSQL password file.
- `~/.aws/credentials`: **Critical**. AWS Access Keys.
- `~/.wget-hsts`: HTTP Strict Transport Security (HSTS) data for websites accessed via `wget`; (usually not useful, but check history).

## Environment variables and process memory

Developers often store secrets in environment variables to avoid hard-coding them in source code. These variables are visible to the user running the process.

- Print current environment:

```bash
env
```

- Display shell variables and functions:

```bash
set
```

- At runtime, environment variables of a process are stored in `/proc/<PID>/environ`:

```bash
cat /proc/<PID>/cmdline | tr '\0' ' '  
```

- Command-line arguments used to start the process are stored at `/proc/<PID>/cmdline`. Look for passwords in the command options:

```bash
cat /proc/<PID>/cmdline | tr '\0' '\n' 
```

- Check environment variables of running processes:

```bash
ps auxww
```
## Open files

- Check open files:

```bash
lsof -u root
```

```bash
lsof -i :3306  # check if MySQL is running
```

- Look for configuration files, password files, databases, etc.
## Application and service configuration

- Generic config search:

```bash
find / -type f \( -name "*conf" -o -name "*config" -o -name "*cnf" \) -ls 2>/dev/null | grep -v '/proc\|/sys\|/usr'
```

```bash
for l in $(echo ".conf .config .cnf"); do echo -e "\nFile extension: " $l; find / -name *$l 2>/dev/null | grep -v "lib\|fonts\|share\|core" ;done
```

>[!tip] Focus on `/etc/`, `/var/www/`, `/opt/`, and `/srv/` first. Avoid `/proc/`, `/sys/`, and `/usr/share/` unless you've exhausted other options.

- Web root directories ([`seclists/Discovery/Web-Content/default-web-root-directory-linux.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/default-web-root-directory-linux.txt)):

```
var/www/html/
var/www/
var/www/sites/
var/www/public/
var/www/public_html/
var/www/html/default/
srv/www/
srv/www/html/
srv/www/sites/
home/www/
home/httpd/
home/$USER/public_html/
home/$USER/www/
```

- Service file locations:

```
/var/www/
/var/www/html/
/srv/www/
/opt/
/usr/share/nginx/
/etc/apache2/
/etc/nginx/
```

### Database configuration

- Database files:

```bash
for l in $(echo ".sql .db .*db .db*");do echo -e "\nDB File extension: " $l; find / -name *$l 2>/dev/null | grep -v "doc\|lib\|headers\|share\|man"; done
```

- MySQL
	- `/etc/mysql/my.cnf`
	- `/etc/mysql/debian.cnf`
	- `/etc/mysql/mysql.conf.d/mysqld.cnf`

```bash
cat /etc/mysql/my.cnf
cat /etc/mysql/debian.cnf
cat /etc/mysql/mysql.conf.d/mysqld.cnf
```

- Look for `password=` entries:

```bash
grep -i "password" /etc/mysql/* 2>/dev/null
```

- PostgreSQL
	- `/etc/postgresql/*/main/pg_hba.conf`
	- `/var/lib/postgresql/.psql_history` (command history; may contain passwords)

```bash
cat /etc/postgresql/*/main/pg_hba.conf
cat /var/lib/postgresql/.psql_history # command history; may contain passwords
```

- MongoDB
	- `/etc/mongod.conf`

```bash
cat /etc/mongod.conf
```
### Web application configuration

Web apps require database access, and credentials may be hardcoded in configuration files.

- WordPress:

```bash
cat /var/www/html/wp-config.php
```

```bash
cat /var/www/html/wp-config.php | grep "DB_PASSWORD"
```

```bash
find / -name wp-config.php 2>/dev/null
```

- Drupal:

```bash
cat /var/www/html/sites/default/settings.php
```

- Joomla:

```bash
cat /var/www/html/configuration.php
```

- Python applications (Django, Flask):
	- Look for `settings.py`, `config.py`, or `.env` files in the web root or `/opt/`.

```bash
find / -name "settings.py" -o -name "config.py" -o name ".env" 2>/dev/null
```

```bash
cat /opt/app/settings.py  # common for Flask/Django apps
```

### Service configuration files

- Apache:

```bash
/etc/apache2/apache2.conf # main configuration file
/etc/apache2/sites-enabled/* # virtual hosts (may contain credentials for proxied services)
```

- `.htpasswd` files (HTTP Basic Auth):

```bash
find / -name ".htpasswd" 2>/dev/null
```

```bash
cat /var/www/.htpasswd
```

- Nginx:

```bash
/etc/nginx/nginx.conf
/etc/nginx/sites-enabled/*
```

- SSH:

```bash
/etc/ssh/sshd_config
# look for PermitRootLogin, PasswordAuthentication, and other custom configs
```

- FTP:

```bash
cat /etc/vsftpd.conf
cat /etc/proftpd/proftpd.conf
```

- Docker:

```bash
cat /etc/docker/daemon.json
cat ~/.docker/config.json # may contain registry credentials
```

## Backup and temporary files

- Search for backup files:

```bash
find / -type f \( -name "*.bak" -o -name "*.old" -o -name "*.save" \) 2>/dev/null
```

- For archived backups:

```bash
tar -tf backup.tar
tar -xf backup.tar
```

- Vim backup files:

```bash
find / -type f -name "*~" 2>/dev/null
```

- Vim/Editor swap files:

```bash
find / -type f -name "*.swp" -o -name "*.swo" 2>/dev/null
```

When a file is opened in Vim, a swap file is created. If the editor crashed these files, remain and can be recovered to reveal the content of the file being edited.

- Vim swap files are binary. To recover them, use `vim -r`:

```bash
vim -r notes.txt.swp
```

- Locations to prioritize:

```bash
ls -la /tmp
```

```bash
ls -la /var
```

```bash
ls -la /var/backups
```

```bash
ls -la /opt
```

## Scripts and binaries

- Script search:

```bash
for l in $(echo ".py .pyc .pl .go .jar .c .sh");do echo -e "\nFile extension: " $l; find / -name *$l 2>/dev/null | grep -v "doc\|lib\|headers\|share"; done
```
## Log files

Logs can contain interesting info, though they are noisy.

| Log file                                                      | Description                                                                        |
| ------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `/var/log/syslog`                                             | Generic system info, cron job failures.                                            |
| `/var/log/mysql/mysql.log` or `/var/log/mysql/mysql-slow.log` | Sometimes queries are logged here, including `SET PASSWORD` or connection strings. |

- `/var/log/auth.log` (Debian): All authentication-related logs.
- `/var/log/syslog`: Generic system activity logs.
- `/var/log/messages`: Generic system activity logs.
- `/var/log/secure` (RedHat/CentOS): All authentication-related logs.
- `/var/log/boot.log`: Booting information.
- `/var/log/dmesg`: Kernel log (normally only readable by root).
- `/var/log/kern.log`: Kernel related warnings, errors and logs.
- `/var/log/faillog`: Failed login attempts.
- `/var/log/cron`: Information related to cron jobs.
- `/var/log/mail.log`: All mail server related logs.
- `/var/log/httpd`: All Apache related logs.
- `/var/log/mysqld.log`: All MySQL server related logs.
- `/var/log/apache2/access.log`: Apache access log.
- `/var/log/mysql/mysql.log` or `/var/log/mysql/mysql-slow.log`: Sometimes queries are logged here, including `SET PASSWORD` or connection strings.

## Checklist 

- [ ]  **Check `/etc/passwd`** for empty passwords (`::`) or UID 0 accounts.
- [ ]  **Read `/etc/shadow`** (if possible) and `unshadow`/crack.
- [ ]  **Grep `.bash_history`** for passwords and failed commands.
- [ ]  **Scan web roots** (`/var/www`) for `config.php`, `settings.py`, `.env`.
- [ ]  **Find SSH keys** (`id_rsa`) and test them; crack passphrases if needed.
- [ ]  **Check `/proc/<PID>/environ`** of running web services for DB credentials.
- [ ]  **Look in `/opt`** and `/var/backups` for `*.bak`, `*.old`, or `*.swp` files.
- [ ]  **Decode Docker auth tokens** in `~/.docker/config.json`.
- [ ]  **Reuse credentials:** If you find one password, try it for `root`, `su`, `ssh`, and database `root`.
## References and further reading

- [`Credential Hunting in Linux — notes.cavementech.com`](https://notes.cavementech.com/pentesting-quick-reference/brute-forcing-password-cracking/credential-hunting-in-linux)

- [`Command-line shell — Arch Wiki`](https://wiki.archlinux.org/title/Command-line_shell)
- [`Bash Startup Files — Bash Reference Manual`](https://www.gnu.org/software/bash/manual/bash.html#Bash-Startup-Files)
- [`Bash — Arch Wiki`](https://wiki.archlinux.org/title/Bash#Configuration_files)

- [`You Don’t Know Jack About .bash_history - SANS DFIR Summit 2016`](https://www.youtube.com/watch?v=wv1xqOV2RyE)


- [`XDF Base Directory Specification — freedesktop.org`](https://specifications.freedesktop.org/basedir/latest/)
- [`XDG Base Directory — Arch Wiki`](https://wiki.archlinux.org/title/XDG_Base_Directory) 


- [`Linux Privilege Escalation – Credentials Harvesting — Stefano Lanaro, steflan-security.com`](https://steflan-security.com/linux-privilege-escalation-credentials-harvesting/)
- [`Credential Hunting in Linux — notes.cavementech.com`](https://notes.cavementech.com/pentesting-quick-reference/brute-forcing-password-cracking/credential-hunting-in-linux)

