---
created: 25-02-2026
---
## Mimikatz

>[Mimikatz](https://github.com/gentilkiwi/mimikatz) is a post-exploitation tool that interacts with Windows authentication internals — especially the **Local Security Authority Subsystem Service (LSASS)** — to extract and manipulate credential material.

- Mimikatz runs on Windows. It's specifically designed for Windows authentication architecture and interacts with Windows processes like **LSASS (Local Security Authority Subsystem Service)** to extract credential material.
- During a penetration test, you would install Mimikatz on a compromised Windows host, typically after you already have code execution and elevated privileges on that system. More precisely, you download a Mimikatz official release and extract the ZIP archive where you plan to run it.

## `sekurlsa::pth`

Mimikatz has a module named **`sekurlsa::pth`** that can be used to perform [[Pass-the-Hash]], [[Pass-the-Key]], and [[Overpass-the-Hash]] attacks. 

```powershell
mimikatz.exe privilege::debug "sekurlsa::pth /user:<username> /rc4:<hash> /domain:<domain> /run:cmd.exe" exit
```


Options relevant to PtH attacks:
- `/user`: the username to impersonate.
- `/domain`: the FQDN (Fully-Qualified Domain Name) of the Active Directory domain. 
- `/rc4` or `/ntlm`: the RC4 key/NT hash (derived from the user's password).
- `/aes128` : the AES-128 key derived from the user's password and the realm of the domain.
- `/aes256` : the AES-256 key derived from the user's password and the realm of the domain.
- `/run` : the command line to run (defaulted to `cmd.exe`).
- `/luid` : [locally unique identifier (LUID)](https://devblogs.microsoft.com/oldnewthing/20240830-00/?p=110198).
- `/impersonate`: performs user token impersonation (no new process is spawned, the token is injected into the process running Mimikatz).


## References and further reading

- [`Mimikatz — Internal All the Things`](https://swisskyrepo.github.io/InternalAllTheThings/cheatsheets/mimikatz-cheatsheet/)

- [`pth — The Hacker Tools`](https://tools.thehacker.recipes/mimikatz/modules/sekurlsa/pth)
