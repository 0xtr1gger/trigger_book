---
created: 25-02-2026
---

## Impacket

>[!note]+ Installation
>- Python `pip`:
>```bash
>pip install impacket
>```
>- `apt` on Kali Linux:
>```bash
>sudo apt update
>sudo apt install -y python3-impacket
>```
>- From GitHub:
>```bash
>git clone https://github.com/fortra/impacket.git && \
>cd impacket && \
>pip install -r requirements.txt && \
>python setup.py install
>```
## Windows remoting

### `psexec.py`


- [`PsExec`](https://learn.microsoft.com/en-us/sysinternals/downloads/psexec) is a command-line utility from the Sysinternals suite, designed to execute processes on remote systems. You can run commands, scripts, or applications interactively.
- `Impacket`'s [`psexec.py`](https://github.com/fortra/impacket/blob/master/examples/psexec.py) implements PsExec-like remote execution over SMB. 


1. `psexec.py` uploads a randomly-named executable to the target's `ADMIN$` share.
2. The executable registers itself as a Windows service via the SCM (Service Control Manager). 
3. Windows launches the service, which opens a named pipe back to you.
4. You get an interactive command line (`cmd.exe`) running remotely (`svcctl & srvsvc` RPC over SMB).

You can imagine the binary executing the following command:

```powershell
sc create <service_name> binPath= "C:\Windows\<uploaded-binary>.exe"
```

This means that to connect, the SMB port on the target system (TCP port `445`) must be open.

>[!warning] The uploaded binary is not automatically deleted. This means `psexec.py` leaves artifacts behind that you need to remove manually. Other than that, these events will also be recorded in event logs and EDR.

Conditions:
- SMP port (TCP port `445`) must be open
- Write access to the `ADMIN$` share
- The user has remote execution privileges (local admin or domain admin or equivalent)
- The remote service controller (SCM) accepts service creation

>[!warning] If any of those aren’t true (e.g., no write access to `ADMIN$`), this will fail.

## References and further reading

- [`Windows Remoting: Difference between psexec, wmiexec, atexec, *exec — ally-petitt.com`](https://ally-petitt.com/en/posts/2022-12-09_windows-remoting--difference-between-psexec--wmiexec--atexec---exec-bf7d1edb5986/)