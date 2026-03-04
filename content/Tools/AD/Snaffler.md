---
created: 17-02-2026
tags:
  - tools
  - "#active_directory"
---
## `Snaffler`

>[`Snaffler`](https://github.com/SnaffCon/Snaffler) is a .NET tool that automates the discovery of interesting data on Windows networks, such as passwords and secrets stored in plain text files (e.g., `web.config`, `unattend.xml`, sticky notes, etc.), hard-coded credentials in scripts, keys and certificates (private keys, API keys).

On a high level, `Snaffer` works like this:
1. It queries Active Directory to get a list of all computers in the domain and their associated file shares (SMB shares).
2. It then connects to these shares (using the permissions of the user who runs the tool) and recursively walks through the directory structure.
3. It opens files (up to a certain size limit) and checks their contents against a massive database of "rules", such as:
	- `password=`
	- `sql connection string`
	- `ssh private key`
	- `.kdbx` (KeePass database)
	- `.ovpn` (OpenVPN configs)

## Usage

Since `Snaffler` is a compiled C# binary (`Snaffler.exe`), you typically upload it to your target machine (or a machine inside the network) and run it.

- Basic usage:

```powershell
Snaffler.exe -S
```

`-s` outputs the results to `stdout` (console) as soon as they're found.

- Target a specific machine:

```powershell
Snaffler.exe -s -i 10.129.11.35
```

- Output results to a file:

```powershell
Snaffler.exe -s -o C:\Temp\snaffler.log
```

