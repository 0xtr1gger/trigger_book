---
created: 04-02-2026
---
## CMD

>**Windows CMD**, officially known as the **Windows Command Processor** or **cmd.exe**, is the command-line interpreter for Windows operating systems. It is the modern incarnation of `COMMAND.COM`, the shell from MS-DOS.

- CMD is implemented as a single executable, `C:\Windows\System32\cmd.exe`. It serves as both an **interactive shell** and a **batch file interpreter**.

```powershell
C:\Windows\System32\cmd.exe
```

- CMD runs as a **user-mode process** that reads text input (from console or a file), parses it, and executes commands.

>[!note] When you double-click a `.bat` or `.cmd` file, Windows launches CMD to interpret it.

### How commands are processed

Here's what happens when you type a command in CMD and press `Enter`:

1. CMD reads the entire line as raw text and expands variables (`%VAR%` syntax).
2. CMD interprets special characters that control command flow and redirection (`&`, `|`, `>`, `<`, `^`, `(`, `)`).
3. CMD determines whether the command is internal or external. Internal commands are executed directly.
4. If the command is not internal, CMD searches for an external executable.
5. When CMD finds the executable, it calls the Windows API function `CreateProcess` to launch it as a new process. CMD then waits for the process to complete (unless you append `&` to run it in the background) and captures its return code in the `%ERRORLEVEL%` variable.

>[!important] Environment variables in CMD are substituted before execution. This is called **early expansion**.

>[!note]+ On variable expansion in CMD
>- Variable expansion happens textually — CMD literally replaces `%VAR%` with the value of that variable in the string before parsing continues.
>- This early expansion is a common source of bugs in batch strings (and it can be exploited in injection attacks).

>[!note]+ External executable search order
> - CMD searches for external executables in:
> 	1. The current working directory
> 	2. Each directory listed in the `PATH` environment variable in order
> - The system determines what counts as an executable by checking file extensions listed in the `PATHEXT` environment variable (typically `.COM`, `.EXE`, `.BAT`, `.CMD`, `.VBS`, `.JS`, `.WS`, `.MSC`).

>[!note] **Internal commands** are those implemented directly inside `cmd.exe`. They exist because they modify CMD's own process state. Examples include `cd`, `dir`, `set`, `echo`, and `exit`.

### Accessing CMD 

A Windows Command Prompt can be accessed **locally** and **remotely**:

- **Local Access** (requires direct physical access to the Windows machine)
	- Windows key + `r` to bring up the run prompt, then `cmd`.
	- Accessing the executable from the drive path `C:\Windows\System32\cmd.exe`.

- **Remote Access**
	- CMD can be accessed through Telnet, SSH, PsExec, WinRM, RDP, or other protocols.

## Basic commands

### Navigating directories

There are two main ways to change the current drive:
- Specify the drive letter and a colon `<drive_letter>:`:

```powershell
C:
```

- Use `cd \<drive_letter>`:

```powershell
cd \D
```

>[!important] Linux CMD and PowerShell commands are **case-insensitive**.

- To change the current drive, specify its letter and a colon, e.g., `c:`, `d:`, etc.

| Command                      | Description                                                                                                                                                                                                                                                                                                | Example                 |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- |
| `cd`                         | Display the current working directory.                                                                                                                                                                                                                                                                     | `cd`                    |
| `cd <path>`                  | Change the current working directory to the specified directory.                                                                                                                                                                                                                                           | `cd c:\Users\trigger`   |
| `cd /<drive_letter>`         | Change the current drive to the specified one.                                                                                                                                                                                                                                                             | `cd /C`                 |
| `dir <folder>`               | List files in the specified folder.                                                                                                                                                                                                                                                                        | `dir C:\Users`          |
| `dir /A:<attributes> <path>` | List files with given attributes in the specified folder (`-` to exclude):<br>- `D` — directories<br>- `H` — hidden files<br>- `S` — system files<br>- `L` — reparse points<br>- `R` — read-only files<br>- `A` — files ready for archiving <br>- `I` — not content indexed files<br>- `O` — offline files | `dir /A:D`              |
| `dir /O:<sortorder> <path>`  | List files in the specified folder and display sort order:<br>- `N` — by name (alphabetic)<br>- `E` — by extension (alphabetic)<br>- `G` — group directories first<br>- `S` — by size (smallest first)<br>- `D` — by date/time (oldest first)<br>- `-` — prefix to reverse order                           | `dir /O:N`              |
| `tree <path>`                | Show the directory structure of the specified folder.                                                                                                                                                                                                                                                      | `tree C:\Users\trigger` |
| `tree /f <path>`             |                                                                                                                                                                                                                                                                                                            |                         |
| `attrib`                     | Display/set attributes of the files in the current directory.                                                                                                                                                                                                                                              | `attrib`                |

### Getting help

>The [`help`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/help) command displays a list of the available commands or detailed help information on a specified command.

```powershell
help
```

- The `help` utility serves as an **offline** manual for CMD- and DOS-compatible Windows operating system commands.

| Command          | Description                                     | Example   |
| ---------------- | ----------------------------------------------- | --------- |
| `help <command>` | Provide help information for a Windows command. | `help cd` |
| `help`           | Lists system commands.                          | `help`    |

>[!example]-
> ```powershell
> C:\Users\htb-student> help
> ```
> 
> ```powershell
> For more information on a specific command, type HELP command-name
> ASSOC          Displays or modifies file extension associations.
> ATTRIB         Displays or changes file attributes.
> BREAK          Sets or clears extended CTRL+C checking.
> BCDEDIT        Sets properties in boot database to control boot loading.
> CACLS          Displays or modifies access control lists (ACLs) of files.
> CALL           Calls one batch program from another.
> CD             Displays the name of or changes the current directory.
> CHCP           Displays or sets the active code page number.
> CHDIR          Displays the name of or changes the current directory.
> CHKDSK         Checks a disk and displays a status report.
> CHKNTFS        Displays or modifies the checking of disk at boot time.
> CLS            Clears the screen.
> CMD            Starts a new instance of the Windows command interpreter.
> COLOR          Sets the default console foreground and background colors.
> COMP           Compares the contents of two files or sets of files.
> COMPACT        Displays or alters the compression of files on NTFS partitions.
> # ...
> ```

- Some commands are not supported by `help`. In such cases, you may try to append the `/?` modifier to the command.

>[!example]+
> ```powershell
> help ipconfig                                                                         This command is not supported by the help utility.  Try "ipconfig /?".
> ```

- Additional resources:
	- [Microsoft Documentation](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/windows-commands)
	- [`ss64`](https://ss64.com/nt/)


>[!tip]+
>To clear your screen, use the `clear` or `cls` command:
>```powershell
>clear
>```
>```powershell
>cls
>```

### History

- View command history:

```powershell
diskey /history
```

|  **Key/Command**  | **Description**                                                                                                             |
| :---------------: | --------------------------------------------------------------------------------------------------------------------------- |
| `doskey /history` | Prints the session's command history.                                                                                       |
|    `<Page Up>`    | Place the first command in the session history to the prompt.                                                               |
|   `<Page Down>`   | Place the last command in the session history to the prompt.                                                                |
|    `Arrow Up`     | Scroll up through the command history.                                                                                      |
|   `Arrow Down`    | Scroll down through the command history.                                                                                    |
|   `Arrow Right`   | Type the previous command to prompt one character at a time.                                                                |
|   `Arrow Left`    | N/A                                                                                                                         |
|       `F3`        | Retype the previous entry to the prompt.                                                                                    |
|       `F5`        | Cycle through previous commands.                                                                                            |
|       `F7`        | Open an interactive list of previous commands.                                                                              |
|       `F9`        | Enters a command to the prompt based on the number specified. The number corresponds to the command's place in the history. |


### File and directory management


- Displaying files:

| Command       | Description                                                           | Example            |
| ------------- | --------------------------------------------------------------------- | ------------------ |
| `more <file>` | Display contents of one or more files.                                | `more file.txt`    |
| `more /S`     | Display contents or one or more files removing excessive blank lines. | `more /S file.txt` |
| `type <file>` | Display contents of one or more files.                                | `type <file>`      |

>[!tip]+
>- To print a line of text:
>```powershell
>echo Some text
>```
>- To erase contents of a file (or create a new blank file) and paste a new line of text to it:
>```powershell
>echo Some text > file.txt
>```
>- To append a line of text to a file:
>```powershell
>echo Some text >> file.txt
>```



- Creating, deleting, copying, moving, and renaming files:

| Command                           | Description                                                                                                                                  | Example                                                                         |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| `fsutil file createNew <file>`    | Create a new file.                                                                                                                           | `fsutil file createNew file.txt`                                                |
| `del <file>`                      | Delete the specified file.                                                                                                                   | `del file.txt`                                                                  |
| `copy <source> <destination>`     | Copy a file from one folder to another.                                                                                                      | `copy file.txt C:\Users\trigger\Documents`                                      |
| `xcopy <file> <destination>`      | Copy files and directory trees to another folder.<br>Similar to `copy` but with additional switches.                                         | `xcopy /S folder1 folder2`                                                      |
| `robocopy <source> <destination>` | Robust copying of files and directories; only works if the source and destination differ in timestamps or file sizes.<br>Useful for backups. | `robocopy /E /B /L C:\Users\htb\Desktop\example C:\Users\htb\Documents\Backup\` |
| `move <file> <destination>`       | Move one or more files to another folder.                                                                                                    | `move c:\f1\text.txt c:\f2`                                                     |
| `ren <old_name>` `<new_name>`     | Rename a file.                                                                                                                               | `ren file.txt important.txt`                                                    |

- Directory management:

| Command                       | Description                      | Example            |
| ----------------------------- | -------------------------------- | ------------------ |
| `md <path>`<br>`mkdir <path>` | Create a new folder.             | `md new_folder`    |
| `rd <path>`<br>`rmdir <path>` | Remove a folder.                 | `rd new_folder`    |
| `rd /S <path>`                | Remove a folder and its content. | `rd /S new_folder` |
### Other 


| Command                  | Description                                                                                                                                                                                                                                                                                                                                                                         | Example                       |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------- |
| `where <file>`           | Locate files that match the specified search pattern.                                                                                                                                                                                                                                                                                                                               | `where *.txt`                 |
| `where /R <path> <file>` | Search files that match the specified search pattern recursively.                                                                                                                                                                                                                                                                                                                   | `where /R C:\ program.exe`    |
| `find "<string>" <path>` | Search for a specific text string within files and display lines containing that string (like `grep`).  <br>`/V` — inverse search.  <br>`/C` — count and display the number of lines containing the string.  <br>`/N` — show line numbers alongside matching lines.  <br>`/I` — case-insensitive search.                                                                            | `find /C /I "password" C:\`   |
| `comp <file1> <file2>`   | Compare the contents of two files or sets of files byte-to-byte.  <br>`/A` — display differences as ASCII characters.  <br>`/D` — display differences in decimal format (default is hexadecimal).  <br>`/L` — show line numbers where differences occur.  <br>`/N=number` — compare only the first `number` of lines of each file.  <br>`/C` — perform case-insensitive comparison. | `comp /C file1.txt file2.txt` |
| `findstr`                | Search for strings or regular expression patterns in files (more powerful than `find`).  <br>`/S` — search recursively.  <br>`/I` — case-insensitive search.  <br>`/R` — use regular expressions.  <br>`/N` — display line numbers.  <br>`/V` — display lines that do NOT match the search string.                                                                                  | `findstr /S /I "error" *.log` |
| `fc`                     | Compare two files or sets of files and display differences line by line (text) or byte by byte (binary).  <br>`/B` — binary comparison.  <br>`/C` — case-insensitive comparison.  <br>`/L` — display line numbers.  <br>`/N` — display line numbers for differences.  <br>`/T` — do not expand tabs to spaces.                                                                      | `fc /C file1.txt file2.txt`   |
| `type`                   | Display the contents of a text file to standard output (similar to `cat`). Can also be used to concatenate multiple files.                                                                                                                                                                                                                                                          | `type file.txt`               |
| `sort`                   | Take input from a source file or pipeline, sort its content alphabetically, and display the output.  <br>`/R` — reverse sort order.  <br>`/UNIQUE` — remove duplicate lines.                                                                                                                                                                                                        | `sort file.txt`               |