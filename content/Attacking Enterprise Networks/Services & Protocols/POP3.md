---
created: 2026-09-22
updated: 2026-09-27
tags:
  - services_n_protocols
---
## POP3

>**[POP3 (Post Office Protocol version 3)](https://en.wikipedia.org/wiki/Post_Office_Protocol)** is an application-layer protocol for retrieving email messages from a remote mail server to a local client over TCP.

- POP3 is defined in [`RFC 1939`](https://datatracker.ietf.org/doc/html/rfc1939), with extensions in later RFCs.
- The protocol is designed for simple, one-way retrieval of messages from a server to a local client. It suits users with intermittent connectivity (e.g., dial-up), who download mail and then read and manage it offline.

>[!important] POP3 retrieves email from the server; it is **not** used to send email. Sending is handled by [[SMTP]] (Simple Mail Transfer Protocol).

>[!note] POP3 is the simpler counterpart to [[IMAP]]; where IMAP synchronizes and manages mail on the server, POP3 typically downloads messages and removes them.

>[!note]+ POP3 limitations
>- No support for folders or labels.
>- No support for read/unread or other message flags.
>- No synchronization: changes made on one client are not reflected elsewhere.

### POP3 ports

| Port  | Protocol | Description                                                    |
| ----- | -------- | ------------------------------------------------------------- |
| `110` | POP3     | Default, unencrypted POP3 (optionally upgraded via `STLS`).   |
| `995` | POP3S    | POP3 over implicit SSL/TLS.                                   |

>[!important] POP3 servers listen on **TCP port `110`** for unencrypted connections and on **TCP port `995`** for encrypted connections (TLS).

### POP3 session states

A POP3 session is divided into three main states:

- **`AUTHORIZATION`**
	- The client establishes a TCP connection to the server on port `110` or `995`; the server responds with a `+OK` greeting.
	- The client then authenticates using the `USER`/`PASS` commands or an authentication extension (e.g., SASL, NTLM).
- **`TRANSACTION`**
	- After successful authentication, the client can list, retrieve, and mark messages for deletion.
- **`UPDATE`**
	- The session ends with the `QUIT` command; the server then applies all changes made during the transaction state.

>[!warning] `USER`/`PASS` are **sent in cleartext** unless the connection is protected by TLS.

>[!note] Once messages are downloaded, they are typically deleted from the server (unless configured otherwise).

>[!example]-
> ```bash
> C: USER alice
> S: +OK
> C: PASS secret
> S: +OK
> C: STAT
> S: +OK 2 320
> C: LIST
> S: +OK 2 messages (320 octets)
> S: 1 120
> S: 2 200
> S: .
> C: RETR 1
> S: +OK 120 octets
> S: <message data>
> S: .
> C: DELE 1
> S: +OK message 1 deleted
> C: QUIT
> S: +OK POP3 server signing off
> ```

### POP3 commands

>POP3 commands are case-sensitive ASCII keywords, each terminated by a CRLF.

- Each response from the server begins with a status indicator: `+OK` for success and `-ERR` for an error.

| Command | State | Syntax                                | Description                                                                                                                           |
| ------- | ----- | ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `USER`  | Auth  | `USER <name>`                         | Specify the username. First step in authentication.                                                                                   |
| `PASS`  | Auth  | `PASS <password>`                     | Specify the password. Sent in cleartext if not over TLS.                                                                              |
| `AUTH`  | Auth  | `AUTH [mechanism] [initial-response]` | Authenticate using a SASL mechanism (e.g., `PLAIN`, `CRAM-MD5`).                                                                       |
| `APOP`  | Auth  | `APOP <name> <digest>`                | Older challenge-response mechanism using MD5 (`digest = MD5(<timestamp> + <secret>)`). Insecure.                                       |
| `QUIT`  | Any   | `QUIT`                                | In the Auth state, close the connection. In the Transaction state, enter the Update state (delete messages) and close the connection. |
| `STAT`  | Trans | `STAT`                                | Return `+OK <message_count> <total_size>`.                                                                                            |
| `LIST`  | Trans | `LIST [msg_number]`                   | With no argument, list all messages with their size; with an argument, list only that message.                                        |
| `RETR`  | Trans | `RETR <msg_number>`                   | Retrieve the full content of the specified message.                                                                                   |
| `DELE`  | Trans | `DELE <msg_number>`                   | Mark a message for deletion; deletion occurs during the Update state (`QUIT`).                                                         |
| `NOOP`  | Trans | `NOOP`                                | No operation; keep the connection alive. Always returns `+OK`.                                                                        |
| `RSET`  | Trans | `RSET`                                | Reset the session; unmark any messages marked for deletion.                                                                           |
| `TOP`   | Trans | `TOP <msg_number> <n>`                | Retrieve the headers and the first `n` lines of a message's body (`TOP 1 0` grabs just the headers).                                  |
| `UIDL`  | Trans | `UIDL [msg_number]`                   | Return a persistent unique ID for messages, letting a client track which messages it has already downloaded.                          |

### Authentication

POP3 supports several ways for a client to prove its identity:

- **`USER`/`PASS`** — the classic two-step login; credentials are sent in cleartext unless the session is protected by TLS.
- **`APOP`** — an older challenge-response mechanism that hashes a server timestamp with a shared secret using MD5; insecure by modern standards.
- **`AUTH <mechanism>`** — SASL-based authentication (e.g., `PLAIN`, `LOGIN`, `CRAM-MD5`), and `NTLM` in Windows environments.

>[!important] The authentication mechanisms and other features supported by the server are advertised in response to the `CAPA` command.


## Enumerating POP3

### Port scanning and version detection

- Scan the default POP3 ports (`110`, `995`) with service version detection:

```bash
sudo nmap -p 110,995 -sV 10.10.11.5
```

- Run the default NSE scripts against the mail-service ports:

```bash
sudo nmap -p 110,995 -sC 10.10.11.5
```

- Run all available POP3 NSE scripts:

```bash
sudo nmap -p 110,995 --script "pop3-*" 10.10.11.5
```

- Analyze the TLS certificate and cipher suites on the encrypted port:

```bash
sudo nmap -p 995 --script ssl-cert,ssl-enum-ciphers 10.10.11.5
```

| Option     | Description                                       |
| ---------- | ------------------------------------------------- |
| `-sV`      | Enable service version detection.                 |
| `-p`       | Specify destination port(s) to scan (`110,995`).  |
| `-sC`      | Run the default set of NSE scripts.               |
| `--script` | Execute a specific NSE script or glob expression. |

- Key Nmap POP3 scripts:

| Script                                                                        | Categories                     | Description                                                                                                                     |
| ----------------------------------------------------------------------------- | ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| [`pop3-capabilities`](https://nmap.org/nsedoc/scripts/pop3-capabilities.html) | `default`, `discovery`, `safe` | Retrieve the POP3 server's advertised capabilities.                                                                           |
| [`pop3-ntlm-info`](https://nmap.org/nsedoc/scripts/pop3-ntlm-info.html)       | `default`, `discovery`, `safe` | Disclose NetBIOS, DNS, and OS build details from a server with NTLM authentication enabled.                                   |
| [`pop3-brute`](https://nmap.org/nsedoc/scripts/pop3-brute.html)               | `brute`, `intrusive`           | Perform a password brute-force attack, defaulting to the `USER` method and also supporting `PLAIN`, `LOGIN`, `CRAM-MD5`, and `APOP`. |

>[!tip]+
> - List local Nmap scripts for POP3:
> 
> ```bash
> ls -l /usr/share/nmap/scripts/*pop3*
> ```

>[!example]-
> 
> ```bash
> sudo nmap -p 110,995 --script pop3-capabilities 10.129.244.182
> ```
> ```bash
> Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-09-27 08:35 CDT
> Nmap scan report for 10.129.244.182
> Host is up (0.075s latency).
> 
> PORT    STATE SERVICE
> 110/tcp open  pop3
> |_pop3-capabilities: CAPA PIPELINING RESP-CODES SASL AUTH-RESP-CODE UIDL STLS TOP
> 995/tcp open  pop3s
> |_pop3-capabilities: CAPA PIPELINING RESP-CODES SASL(PLAIN) USER UIDL AUTH-RESP-CODE TOP
> 
> Nmap done: 1 IP address (1 host up) scanned in 0.65 seconds
> ```

### Banner grabbing

- Connect to the plaintext port with Netcat or Telnet:

```bash
nc -nv 10.10.11.5 110
```

```bash
telnet 10.10.11.5 110
```

- Connect to the encrypted port (`995`) over TLS:

```bash
openssl s_client -connect 10.10.11.5:995 -quiet -crlf
```

```bash
openssl s_client -connect 10.10.11.5:pop3s
```

| Option     | Description                                                    |
| ---------- | ------------------------------------------------------------- |
| `-connect` | Connect to the specified `host:port`.                         |
| `-quiet`   | Suppress session and certificate output.                      |
| `-crlf`    | Translate line feeds into CRLF as required by the protocol.   |
| `-nv`      | (Netcat) Disable DNS resolution and print connection details. |

>[!example]-
> ```bash
> openssl s_client -connect 10.129.244.182:pop3s
> ```
> ```bash
> CONNECTED(00000003)
> Can't use SSL_get_servername
> depth=0 C = UK, ST = London, L = London, O = InlaneFreight Ltd, OU = DevOps Dep\C3\83artment, CN = dev.inlanefreight.htb, emailAddress = cto.dev@dev.inlanefreight.htb
> verify error:num=18:self-signed certificate
> verify return:1
> depth=0 C = UK, ST = London, L = London, O = InlaneFreight Ltd, OU = DevOps Dep\C3\83artment, CN = dev.inlanefreight.htb, emailAddress = cto.dev@dev.inlanefreight.htb
> verify return:1
> ---
> Certificate chain
>  0 s:C = UK, ST = London, L = London, O = InlaneFreight Ltd, OU = DevOps Dep\C3\83artment, CN = dev.inlanefreight.htb, emailAddress = cto.dev@dev.inlanefreight.htb
>    i:C = UK, ST = London, L = London, O = InlaneFreight Ltd, OU = DevOps Dep\C3\83artment, CN = dev.inlanefreight.htb, emailAddress = cto.dev@dev.inlanefreight.htb
>    a:PKEY: rsaEncryption, 2048 (bit); sigalg: RSA-SHA256
>    v:NotBefore: Nov  8 23:10:05 2021 GMT; NotAfter: Aug 23 23:10:05 2295 GMT
> ---
> Server certificate
> -----BEGIN CERTIFICATE-----
> MIIEUzCCAzugAwIBAgIUDf35PqFuv6Uv0EECM8dFmNSZoY8wDQYJKoZIhvcNAQEL
> BQAwgbcxCzAJBgNVBAYTAlVLMQ8wDQYDVQQIDAZMb25kb24xDzANBgNVBAcMBkxv
> bmRvbjEaMBgGA1UECgwRSW5sYW5lRnJlaWdodCBMdGQxHDAaBgNVBAsME0Rldk9w
> cyBEZXDDg2FydG1lbnQxHjAcBgNVBAMMFWRldi5pbmxhbmVmcmVpZ2h0Lmh0YjEs
> MCoGCSqGSIb3DQEJARYdY3RvLmRldkBkZXYuaW5sYW5lZnJlaWdodC5odGIwIBcN
> MjExMTA4MjMxMDA1WhgPMjI5NTA4MjMyMzEwMDVaMIG3MQswCQYDVQQGEwJVSzEP
> MA0GA1UECAwGTG9uZG9uMQ8wDQYDVQQHDAZMb25kb24xGjAYBgNVBAoMEUlubGFu
> ZUZyZWlnaHQgTHRkMRwwGgYDVQQLDBNEZXZPcHMgRGVww4NhcnRtZW50MR4wHAYD
> VQQDDBVkZXYuaW5sYW5lZnJlaWdodC5odGIxLDAqBgkqhkiG9w0BCQEWHWN0by5k
> ZXZAZGV2LmlubGFuZWZyZWlnaHQuaHRiMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A
> MIIBCgKCAQEAxvMwFE6m+iBUSujb5d6DUy1xDYR5awzQRwddyvq6iBrMxbnptSrn
> +j0UOKWHCOpD5LREwP26ghUg0lVJzfo+v5pQJGnxEXKg0OFlzWEd8xgx/JWW/z1/
> rDsWlNa2yYZkCy68YWJlC7UZxvcDFrI0V0pDJIkrjForw26laoYDkrh1A5F8uUXD
> 1TwRLLYo+NGmtNHT3BADJpv6aFUZ4CGrqBQNi7XpsTZ948WLhUwQvWmebiK06Dai
> TvMNKBctjWAiNI4xvq34W9hIUaPxT1JJzuujRslep6nHGHW00QEWTWgyOMYThc3b
> HtKIHMfDLTUMz7s8RhVVwlWE6+ly1DMRgQIDAQABo1MwUTAdBgNVHQ4EFgQUGDTC
> 9B5KCKPWT7vXbnMunL/mEE4wHwYDVR0jBBgwFoAUGDTC9B5KCKPWT7vXbnMunL/m
> EE4wDwYDVR0TAQH/BAUwAwEB/zANBgkqhkiG9w0BAQsFAAOCAQEADh0v5XWCf3KO
> atrWcoiIOC67Z0ZIO7yEF+fQo8z+Wx1dWzmCFVu7u4+l7slcdJICCGBbOX8eItWS
> chwzgnWJToyX8PWY8lSaB8ifMDQcr457Y7O6NmvgU35sRcLnYYqXzu2oh0lxsFLR
> vL1wpyDLPhhoI++j1fELhiJ3GWiUQrb0vfJPcbSkHTgzf0hm7mLJTaqt3WfS/Gr2
> 8Oh7vSfzvqvHLE7HHAO0G5Q81zo+wWsrQF0s40HEF/raEMfOy2Htm79YjyjAlLWf
> ueS+u8rX2smOYdRIpL3UPx7+yZPGu47vYoetde1Z5cfTCgmeS05BQ2qMOp6Tw6+G
> xUuqg8nK1Q==
> -----END CERTIFICATE-----
> subject=C = UK, ST = London, L = London, O = InlaneFreight Ltd, OU = DevOps Dep\C3\83artment, CN = dev.inlanefreight.htb, emailAddress = cto.dev@dev.inlanefreight.htb
> issuer=C = UK, ST = London, L = London, O = InlaneFreight Ltd, OU = DevOps Dep\C3\83artment, CN = dev.inlanefreight.htb, emailAddress = cto.dev@dev.inlanefreight.htb
> ---
> No client certificate CA names sent
> Peer signing digest: SHA256
> Peer signature type: RSA-PSS
> Server Temp Key: X25519, 253 bits
> ---
> SSL handshake has read 1667 bytes and written 377 bytes
> Verification error: self-signed certificate
> ---
> New, TLSv1.3, Cipher is TLS_AES_256_GCM_SHA384
> Server public key is 2048 bit
> Secure Renegotiation IS NOT supported
> Compression: NONE
> Expansion: NONE
> No ALPN negotiated
> Early data was not sent
> Verify return code: 18 (self-signed certificate)
> ---
> ---
> Post-Handshake New Session Ticket arrived:
> SSL-Session:
>     Protocol  : TLSv1.3
>     Cipher    : TLS_AES_256_GCM_SHA384
>     Session-ID: 241B0EC2248C2882D98B385E8CF5A0B0BEE8A224F4AA3066999779102CDBC68B
>     Session-ID-ctx: 
>     Resumption PSK: B130EEFDE6779C09B5D02ADD74312FBB014CF7D2F897F8518EA723FB851AE7BD87B2DB5E7372B02ADE7A7F1A8E374710
>     PSK identity: None
>     PSK identity hint: None
>     SRP username: None
>     TLS session ticket lifetime hint: 7200 (seconds)
>     TLS session ticket:
>     0000 - cc c0 c2 2f 30 05 1b e3-ca 0b a7 7f 44 b7 5d 8a   .../0.......D.].
>     0010 - e4 cb bf 6d b0 09 20 20-23 91 df ea 71 8e 80 a3   ...m..  #...q...
>     0020 - 9c d9 78 79 a9 8e 74 ef-76 a4 96 45 d2 0e 71 82   ..xy..t.v..E..q.
>     0030 - 9d d3 8c 80 fb d0 d5 0e-fa d3 01 3f 29 7f 99 78   ...........?)..x
>     0040 - 9e 84 65 4a c3 98 09 a2-24 c1 15 7a 2b 7c 6d 8e   ..eJ....$..z+|m.
>     0050 - 32 71 90 a5 91 04 54 0e-b9 65 4b 29 46 dd 41 17   2q....T..eK)F.A.
>     0060 - 00 7f 95 26 ac 9f 0f c1-33 c3 2d 83 68 6d e6 31   ...&....3.-.hm.1
>     0070 - 20 01 79 3c c5 bb a9 9f-96 dc fa 31 43 45 53 76    .y<.......1CESv
>     0080 - 33 46 ed 46 9d 2e ec cf-63 59 4d 05 0f 46 2a 91   3F.F....cYM..F*.
>     0090 - 7e ca ac 35 0d 22 fa ca-81 03 f0 13 81 a2 24 fa   ~..5."........$.
>     00a0 - aa dc fe 9d 5e 37 c7 f0-25 44 6f ea fb 5c df 3d   ....^7..%Do..\.=
>     00b0 - ec 62 57 14 76 73 6e 4a-a5 0a 82 b1 16 05 76 96   .bW.vsnJ......v.
> 
>     Start Time: 1758980763
>     Timeout   : 7200 (sec)
>     Verify return code: 18 (self-signed certificate)
>     Extended master secret: no
>     Max Early Data: 0
> ---
> read R BLOCK
> ---
> Post-Handshake New Session Ticket arrived:
> SSL-Session:
>     Protocol  : TLSv1.3
>     Cipher    : TLS_AES_256_GCM_SHA384
>     Session-ID: 50B3D96BDBA5BA70E39035616FE7904A3754C5D1623F0B6B04E9E4C188FB87D0
>     Session-ID-ctx: 
>     Resumption PSK: C56536B8BB5D6E550E540C5A6F984CF011AE580A99878094590697B906B036917F09A38C9EFE023FE2CFBAFE9C5F2D69
>     PSK identity: None
>     PSK identity hint: None
>     SRP username: None
>     TLS session ticket lifetime hint: 7200 (seconds)
>     TLS session ticket:
>     0000 - cc c0 c2 2f 30 05 1b e3-ca 0b a7 7f 44 b7 5d 8a   .../0.......D.].
>     0010 - b4 df f3 ea fa 4b 9f 3e-8f 4c bc 1d b1 a7 36 3c   .....K.>.L....6<
>     0020 - 68 89 d1 3b c5 18 43 9d-46 6b ce 9a 5a 9e 5e ca   h..;..C.Fk..Z.^.
>     0030 - f2 60 8a 34 9e 0d c4 24-e2 99 a3 37 23 6b b2 38   .`.4...$...7#k.8
>     0040 - 2f d2 af 3b af d2 41 db-74 4b e5 cd a4 31 4b ef   /..;..A.tK...1K.
>     0050 - 02 c5 06 cc 98 7e d0 12-b9 08 d1 d2 2e 76 93 74   .....~.......v.t
>     0060 - 40 63 86 62 7a 3d 88 ca-e3 1c bc b8 fa 5a c3 30   @c.bz=.......Z.0
>     0070 - d3 99 49 5c 84 bf 04 17-23 d5 95 a2 32 82 06 c7   ..I\....#...2...
>     0080 - c2 34 3f 7c f5 c8 5a f5-0e a4 06 4a 29 2f 58 2b   .4?|..Z....J)/X+
>     0090 - c0 61 43 93 d2 3d 84 47-26 38 ab c7 01 33 2b 1d   .aC..=.G&8...3+.
>     00a0 - f4 af 7d a8 b9 c4 8d 3e-56 2d c9 9d df 22 75 a1   ..}....>V-..."u.
>     00b0 - 6f b0 d4 cb 91 6b 25 c2-5a 39 6d e9 a0 e8 9f 73   o....k%.Z9m....s
> 
>     Start Time: 1758980763
>     Timeout   : 7200 (sec)
>     Verify return code: 18 (self-signed certificate)
>     Extended master secret: no
>     Max Early Data: 0
> ---
> read R BLOCK
> +OK InFreight POP3 v9.188
> ```

### Discovering server capabilities

- Connect and issue the `CAPA` command to list supported extensions and authentication mechanisms:

```bash
nc -nv 10.10.11.5 110
CAPA
```

## Brute-forcing credentials

Once a valid username list is available, POP3 passwords can be brute-forced:

- Brute-force credentials using Hydra:

```bash
hydra -L usernames.txt -P /usr/share/wordlists/rockyou.txt pop3://10.10.11.5
```

- Brute-force credentials using Medusa:

```bash
medusa -U usernames.txt -P /usr/share/wordlists/rockyou.txt -h 10.10.11.5 -M pop3
```

| Option | Description                                  |
| ------ | -------------------------------------------- |
| `-l`   | (Hydra) Set a single username to test.       |
| `-L`   | (Hydra) Read usernames from a file.          |
| `-u`   | (Medusa) Set a single username to test.      |
| `-U`   | Read usernames from a file.                  |
| `-P`   | Read passwords from a wordlist file.         |
| `-h`   | (Medusa) Set the target host.                |
| `-M`   | (Medusa) Select the service module (`pop3`). |

- Brute-force credentials using the Nmap [`pop3-brute`](https://nmap.org/nsedoc/scripts/pop3-brute.html) script:

```bash
nmap -p 110 --script pop3-brute 10.10.11.5
```

- Select a specific authentication method for the script:

```bash
nmap -p 110 --script pop3-brute --script-args pop3loginmethod=SASL-LOGIN 10.10.11.5
```

```bash
nmap -p 110 --script pop3-brute --script-args pop3loginmethod=APOP 10.10.11.5
```

>[!note] POP3 servers commonly rate-limit or temporarily block IP addresses after repeated failed authentication attempts. Start with a low thread count and adjust.

## Interacting with POP3

### Authenticating to the server

- Connect over TLS and log in with the `USER`/`PASS` commands:

```bash
openssl s_client -connect 10.10.11.5:995 -quiet -crlf
USER jdoe
PASS passwd123
```

- Authenticate and download mail with cURL:

```bash
curl -k 'pop3s://10.10.11.5' --user jdoe:'passwd123'
```

| Option   | Description                                          |
| -------- | ---------------------------------------------------- |
| `-k`     | Skip TLS certificate validation (self-signed certs). |
| `--user` | Supply the `username:password` for authentication.   |

### Retrieving messages

- Report the message count and total mailbox size:

```bash
STAT
```

- List all messages with their sizes:

```bash
LIST
```

- Retrieve the full content of a message:

```bash
RETR 1
```

- Retrieve only the headers and the first `n` body lines (`TOP 1 0` grabs just the headers):

```bash
TOP 1 0
```

- Return persistent unique IDs to track already-downloaded messages:

```bash
UIDL
```

>[!tip]+
> - `RETR` and `LIST` leave messages on the server; `DELE` only marks them for deletion, which is applied during the Update state on `QUIT`.
> - To read mail without altering server state, avoid `DELE` and end the session with `RSET` followed by `QUIT`.

## References and further reading

- [`Post Office Protocol — Wikipedia`](https://en.wikipedia.org/wiki/Post_Office_Protocol)
- [`Post Office Protocol - Version 3 — RFC 1939`](https://datatracker.ietf.org/doc/html/rfc1939)
- [`110,995 - Pentesting POP — HackTricks`](https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-pop.html)
