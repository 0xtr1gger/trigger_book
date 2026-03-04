---
created: 31-01-2026
---
- Challenge: [`VulnNet_Internal`](https://tryhackme.com/room/vulnnetinternal)

```bash
echo "10.65.134.198 vuln.net" >> /etc/hosts
```
## Recon

- Port scanning:

```bash
sudo nmap 10.65.134.198
```

```bash
Starting Nmap 7.95 ( https://nmap.org ) at 2026-01-31 16:12 UTC
Nmap scan report for 10.65.134.198
Host is up (0.16s latency).
Not shown: 993 closed tcp ports (reset)
PORT     STATE    SERVICE
22/tcp   open     ssh
111/tcp  open     rpcbind
139/tcp  open     netbios-ssn
445/tcp  open     microsoft-ds
873/tcp  open     rsync
2049/tcp open     nfs
9090/tcp filtered zeus-admin

Nmap done: 1 IP address (1 host up) scanned in 26.65 seconds
```

- More thorough scanning:

```bash
sudo nmap 10.65.134.198 -sV -sC -p22,111,139,445,873,2049,9090
```

```bash
Starting Nmap 7.95 ( https://nmap.org ) at 2026-01-31 17:10 UTC
Nmap scan report for 10.65.134.198
Host is up (0.39s latency).

PORT     STATE    SERVICE     VERSION
22/tcp   open     ssh         OpenSSH 8.2p1 Ubuntu 4ubuntu0.13 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 35:17:11:91:33:54:c1:bd:05:ab:c4:cc:f7:2a:2c:2f (RSA)
|   256 48:78:21:f2:6a:8a:2b:12:51:67:81:8e:f9:12:68:e6 (ECDSA)
|_  256 c0:a3:aa:7b:06:58:32:94:26:a1:98:bc:84:60:e5:f6 (ED25519)
111/tcp  open     rpcbind     2-4 (RPC #100000)
|_rpcinfo: ERROR: Script execution failed (use -d to debug)
139/tcp  open     netbios-ssn Samba smbd 4
445/tcp  open     netbios-ssn Samba smbd 4
873/tcp  open     rsync       (protocol version 31)
2049/tcp open     nfs         3-4 (RPC #100003)
9090/tcp filtered zeus-admin
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Host script results:
|_nbstat: NetBIOS name: , NetBIOS user: <unknown>, NetBIOS MAC: <unknown> (unknown)
| smb2-time: 
|   date: 2026-01-31T17:10:51
|_  start_date: N/A
| smb2-security-mode: 
|   3:1:1: 
|_    Message signing enabled but not required

Service detection performed. Please report any incorrect result
```