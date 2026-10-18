---
created: 2026-09-22
updated: 2026-09-27
tags:
  - services_n_protocols
---
## IMAP

>**[IMAP (Internet Message Access Protocol)](https://en.wikipedia.org/wiki/Internet_Message_Access_Protocol)** is an application-layer protocol for accessing and managing email stored on a remote mail server.

- IMAP is defined in [`RFC 3501`](https://datatracker.ietf.org/doc/html/rfc3501); the current standard in use is **IMAP4rev1**, also referred to as IMAP4, IMAPv4rev1, or simply IMAP.
- IMAP is designed for **real-time, multi-device synchronization** and **server-side management** of mailboxes, folders, and message states — messages stay on the server and are manipulated in place rather than downloaded and removed.

>[!important] IMAP retrieves and manages email on the server; it is **not** used to send email. Sending is handled by [[SMTP]] (Simple Mail Transfer Protocol).

>[!note] IMAP is the richer, stateful counterpart to [[POP3]], which only downloads messages for offline use.

### IMAP ports

| Port  | Protocol | Description                                            |
| ----- | -------- | ------------------------------------------------------ |
| `143` | IMAP     | Default, unencrypted IMAP (optionally upgraded via `STARTTLS`). |
| `993` | IMAPS    | IMAP over implicit SSL/TLS.                            |

>[!important] IMAP servers listen on **TCP port `143`** for unencrypted connections and on **TCP port `993`** for encrypted connections (**IMAPS** — IMAP over SSL/TLS).

### Core features

>[!note]+ Core IMAP features
> - **Server-side mailboxes:** supports hierarchical folders (e.g., Inbox, Sent, Drafts, Trash, and custom folders).
> - **Message flags and states:** tracks message state with system flags: `\Seen`, `\Answered`, `\Flagged`, `\Deleted`, `\Draft`, `\Recent`.
> - **Multi-device synchronization:** changes (e.g., marking as read or moving to a folder) are reflected across all connected clients.
> - **Partial message retrieval:** can fetch only specific parts of messages, such as headers, individual MIME parts, or metadata (useful in bandwidth-constrained environments).
> - **Concurrent session support:** multiple clients can access the same mailbox simultaneously.
> - **Persistent UIDs:** each message has a **Unique Identifier (UID)** that remains stable across sessions.

>[!note]+ Message flags supported by IMAP
> - `\Seen` (read).
> - `\Answered`.
> - `\Flagged` (important).
> - `\Deleted`.
> - `\Draft`.
> - `\Recent`.

### IMAP commands

>IMAP commands are case-sensitive ASCII keywords, each prefixed by a client-generated tag and terminated by a CRLF.

- Each IMAP command is preceded by a unique **command tag** (can be anything from a simple `A` to a more complex `A000912.1`). The server echoes this tag in its response to make it clear which command it is answering.
	- This allows commands to be sent asynchronously — the client doesn't have to wait for a response before sending the next command, and responses are tagged accordingly.

>[!important] Command tags are a mandatory part of the protocol.

- **Untagged responses**: `*`
	- Server responses preceded by an asterisk `*` are **untagged**. They provide data independent of any single command, such as mailbox status or a message update.
- **Continuation**: `+`
	- Server responses preceded by a plus sign `+` request more data from the client, such as during authentication.

>[!example]-
> ```bash
> nc mail.example.com 143
> C: A001 LOGIN alice secret
> S: A001 OK LOGIN completed
> C: A002 SELECT INBOX
> S: * 3 EXISTS
> S: * 1 RECENT
> S: * FLAGS (\Seen \Answered \Flagged \Deleted \Draft \Recent)
> S: A002 OK [READ-WRITE] SELECT completed
> C: A003 FETCH 1 BODY[HEADER]
> S: * 1 FETCH (BODY[HEADER] {342}
> <message headers>
> )
> S: A003 OK FETCH completed
> C: A004 STORE 1 +FLAGS (\Seen)
> S: * 1 FETCH (FLAGS (\Seen))
> S: A004 OK STORE completed
> C: A005 LOGOUT
> S: * BYE IMAP4rev1 Server logging out
> S: A005 OK LOGOUT completed
> ```

- Authentication and session control:

| Command        | Syntax                    | Description                                                    |
| -------------- | ------------------------- | ------------------------------------------------------------- |
| `CAPABILITY`   | `tag CAPABILITY`          | List server capabilities (e.g., `STARTTLS`, `AUTH=PLAIN`).    |
| `STARTTLS`     | `tag STARTTLS`            | Upgrade the connection to TLS (if supported).                 |
| `LOGIN`        | `tag LOGIN "user" "pass"` | Authenticate in plaintext (avoid without TLS).                |
| `AUTHENTICATE` | `tag AUTHENTICATE <mech>` | Authenticate using a SASL mechanism (e.g., `PLAIN`, `LOGIN`, `CRAM-MD5`). |
| `LOGOUT`       | `tag LOGOUT`              | Terminate the session.                                        |

- Mailbox management:

| Command                     | Syntax                     | Description                             |
| --------------------------- | -------------------------- | --------------------------------------- |
| `LIST`                      | `tag LIST <ref> <pattern>` | List mailboxes (e.g., `LIST "" "*"`).   |
| `LSUB`                      | `tag LSUB <ref> <pattern>` | List **subscribed** mailboxes.          |
| `CREATE`                    | `tag CREATE <name>`        | Create a new mailbox.                   |
| `DELETE`                    | `tag DELETE <name>`        | Delete a mailbox (must be empty).       |
| `RENAME`                    | `tag RENAME <old> <new>`   | Rename a mailbox.                       |
| `SUBSCRIBE` / `UNSUBSCRIBE` | `tag SUBSCRIBE <name>`     | Manage mailbox subscriptions.           |

- Message access and manipulation:

| Command   | Syntax                                   | Description                                          |
| --------- | ---------------------------------------- | ---------------------------------------------------- |
| `SELECT`  | `tag SELECT <mailbox>`                   | Open a mailbox for **read-write** access.            |
| `EXAMINE` | `tag EXAMINE <mailbox>`                  | Open a mailbox **read-only**.                        |
| `STATUS`  | `tag STATUS <mailbox> (<attrs>)`         | Retrieve mailbox metadata without opening it.        |
| `SEARCH`  | `tag [UID] SEARCH <criteria>`            | Find messages matching the given criteria.           |
| `FETCH`   | `tag [UID] FETCH <set> <data>`           | Retrieve message data.                               |
| `STORE`   | `tag [UID] STORE <set> <action> <flags>` | Modify message flags.                                |
| `COPY`    | `tag [UID] COPY <set> <dest>`            | Copy messages to another mailbox.                    |
| `EXPUNGE` | `tag EXPUNGE`                            | Permanently delete messages marked with `\Deleted`.  |

>[!important] IMAP message identifiers
>Each message in IMAP has two identifiers:
>- **Sequence number:** a temporary, session-specific index (e.g., `1`, `2`, `3`); it changes if messages are added or deleted.
>- **UID (Unique Identifier):** a persistent, server-assigned ID. Used with the `UID` command prefix (e.g., `UID FETCH 12345 ...`).

### Authentication

IMAP supports several authentication methods a client can use to prove its identity to the server:

- The `LOGIN` command (plaintext authentication).
- [SASL](https://doc.dovecot.org/2.3/configuration_manual/authentication/authentication_mechanisms/) (Simple Authentication and Security Layer) mechanisms, exposed through the `AUTHENTICATE` command:
	- `AUTHENTICATE LOGIN`.
	- `AUTHENTICATE PLAIN`.
	- `CRAM-MD5`.
	- `DIGEST-MD5`.
	- `NTLM`.
	- `GSSAPI` (Kerberos support).

| Method               | Security                   | Notes                                  |
| -------------------- | -------------------------- | -------------------------------------- |
| `LOGIN`              | ❌ Plaintext                | Avoid without TLS.                     |
| `AUTHENTICATE PLAIN` | ❌ Base64-encoded plaintext | Same exposure as `LOGIN`.              |
| `AUTHENTICATE LOGIN` | ❌ Base64-encoded plaintext | Step-wise username and password.       |
| `CRAM-MD5`           | ⚠️ Weak                    | Challenge-response, but MD5 is broken. |
| `DIGEST-MD5`         | ⚠️ Deprecated              | Removed from modern standards.         |
| `GSSAPI`             | ✅ Strong                   | Kerberos SSO (enterprise).             |
| `OAUTHBEARER`        | ✅ Strong                   | OAuth 2.0 tokens (modern cloud).       |

>[!important] Authentication mechanisms and other features supported by the server are advertised in response to the `CAPABILITY` command.

The three most commonly encountered methods are `LOGIN`, SASL `AUTHENTICATE LOGIN`, and SASL `AUTHENTICATE PLAIN`:

- **`LOGIN`**
	- The client sends the username and password in plaintext using the `LOGIN` command. Rarely used on unencrypted connections.

```toml
A1 LOGIN alice@example.com password
A1 OK [CAPABILITY IMAP4rev1 LITERAL+ SASL-IR LOGIN-REFERRALS ID ENABLE IDLE SORT SORT=DISPLAY THREAD=REFERENCES THREAD=REFS THREAD=ORDEREDSUBJECT MULTIAPPEND URL-PARTIAL CATENATE UNSELECT CHILDREN NAMESPACE UIDPLUS LIST-EXTENDED I18NLEVEL=1 CONDSTORE QRESYNC ESEARCH ESORT SEARCHRES WITHIN CONTEXT=SEARCH LIST-STATUS BINARY MOVE NOTIFY SPECIAL-USE QUOTA] Logged in
```

- **`AUTHENTICATE LOGIN`**
	- The username and password are sent as separate Base64-encoded strings (encoded, not encrypted).

```toml
A1 AUTHENTICATE LOGIN
+ VXNlcm5hbWU6 # Username: | base64
YWxpY2VAZXhhbXBsZS5jb20K # alice@example.com | base64
+ UGFzc3dvcmQ6 # Password: | base64
cGFzc3dvcmQK # password
A1 OK [CAPABILITY IMAP4rev1 LITERAL+ SASL-IR LOGIN-REFERRALS ID ENABLE IDLE SORT SORT=DISPLAY THREAD=REFERENCES THREAD=REFS THREAD=ORDEREDSUBJECT MULTIAPPEND URL-PARTIAL CATENATE UNSELECT CHILDREN NAMESPACE UIDPLUS LIST-EXTENDED I18NLEVEL=1 CONDSTORE QRESYNC ESEARCH ESORT SEARCHRES WITHIN CONTEXT=SEARCH LIST-STATUS BINARY MOVE NOTIFY SPECIAL-USE QUOTA] Logged in
```

- **`AUTHENTICATE PLAIN`**
	- The username and password are sent together as a single Base64-encoded string, separated by `NUL` characters (encoded, not encrypted).

```toml
A1 AUTHENTICATE PLAIN
+
YWxpY2VAZXhhbXBsZS5jb21cMHBhc3N3b3JkCg== # alice@example.com\0password | base64
A1 OK [CAPABILITY IMAP4rev1 LITERAL+ SASL-IR LOGIN-REFERRALS ID ENABLE IDLE SORT SORT=DISPLAY THREAD=REFERENCES THREAD=REFS THREAD=ORDEREDSUBJECT MULTIAPPEND URL-PARTIAL CATENATE UNSELECT CHILDREN NAMESPACE UIDPLUS LIST-EXTENDED I18NLEVEL=1 CONDSTORE QRESYNC ESEARCH ESORT SEARCHRES WITHIN CONTEXT=SEARCH LIST-STATUS BINARY MOVE NOTIFY SPECIAL-USE QUOTA] Logged in
```

- Other authentication methods:
	- **`CRAM-MD5` / `DIGEST-MD5`** — challenge-response mechanisms that avoid sending the password in plaintext by using HMAC-MD5 hashes. While better than plaintext, MD5 is cryptographically weak and vulnerable to offline cracking.
	- **`GSSAPI` (Kerberos)** — used in enterprise environments for single sign-on (SSO) via Kerberos; misconfigurations can be a target for attackers. See [[Kerberos]].
	- **`NTLM`** — used in Windows environments; susceptible to NTLM relay attacks.

## Enumerating IMAP

### Port scanning and version detection

- Scan the default IMAP ports (`143`, `993`) with service version detection:

```bash
sudo nmap -p 143,993 -sV 10.10.11.5
```

- Run the default NSE scripts against the mail-service ports:

```bash
sudo nmap -p 143,993 -sC 10.10.11.5
```

>[!example]-
> 
> ```bash
> sudo nmap -p 110,995,143,993 -sC 10.129.244.182
> ```
> 
> ```bash
> Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-09-27 08:37 CDT
> Nmap scan report for 10.129.244.182
> Host is up (0.075s latency).
> 
> PORT    STATE SERVICE
> 110/tcp open  pop3
> |_ssl-date: TLS randomness does not represent time
> |_pop3-capabilities: AUTH-RESP-CODE TOP CAPA SASL UIDL STLS PIPELINING RESP-CODES
> | ssl-cert: Subject: commonName=dev.inlanefreight.htb/organizationName=InlaneFreight Ltd/stateOrProvinceName=London/countryName=UK
> | Not valid before: 2021-11-08T23:10:05
> |_Not valid after:  2295-08-23T23:10:05
> 143/tcp open  imap
> | ssl-cert: Subject: commonName=dev.inlanefreight.htb/organizationName=InlaneFreight Ltd/stateOrProvinceName=London/countryName=UK
> | Not valid before: 2021-11-08T23:10:05
> |_Not valid after:  2295-08-23T23:10:05
> |_imap-capabilities: IMAP4rev1 ID STARTTLS IDLE LOGINDISABLEDA0001 SASL-IR more have post-login listed LITERAL+ Pre-login capabilities OK ENABLE LOGIN-REFERRALS
> |_ssl-date: TLS randomness does not represent time
> 993/tcp open  imaps
> |_imap-capabilities: IMAP4rev1 ID listed IDLE OK SASL-IR more have post-login LITERAL+ Pre-login capabilities LOGIN-REFERRALS AUTH=PLAINA0001 ENABLE
> |_ssl-date: TLS randomness does not represent time
> | ssl-cert: Subject: commonName=dev.inlanefreight.htb/organizationName=InlaneFreight Ltd/stateOrProvinceName=London/countryName=UK
> | Not valid before: 2021-11-08T23:10:05
> |_Not valid after:  2295-08-23T23:10:05
> 995/tcp open  pop3s
> |_ssl-date: TLS randomness does not represent time
> | ssl-cert: Subject: commonName=dev.inlanefreight.htb/organizationName=InlaneFreight Ltd/stateOrProvinceName=London/countryName=UK
> | Not valid before: 2021-11-08T23:10:05
> |_Not valid after:  2295-08-23T23:10:05
> |_pop3-capabilities: AUTH-RESP-CODE TOP CAPA USER UIDL SASL(PLAIN) PIPELINING RESP-CODES
> ```

- Run all available IMAP NSE scripts:

```bash
sudo nmap -p 143,993 --script "imap-*" 10.10.11.5
```

- Analyze the TLS certificate and cipher suites on the encrypted port:

```bash
sudo nmap -p 993 --script ssl-cert,ssl-enum-ciphers 10.10.11.5
```

| Option        | Description                                                              |
| ------------- | ------------------------------------------------------------------------ |
| `-sV`         | Enable service version detection.                                        |
| `-p`          | Specify destination port(s) to scan (`143,993`).                         |
| `-sC`         | Run the default set of NSE scripts.                                      |
| `--script`    | Execute a specific NSE script or glob expression.                        |

- Key Nmap IMAP scripts:

| Script                                                                        | Categories                     | Description                                                                                                                    |
| ----------------------------------------------------------------------------- | ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| [`imap-capabilities`](https://nmap.org/nsedoc/scripts/imap-capabilities.html) | `default`, `safe`              | Retrieve the IMAP server's advertised capabilities.                                                                           |
| [`imap-ntlm-info`](https://nmap.org/nsedoc/scripts/imap-ntlm-info.html)       | `default`, `discovery`, `safe` | Disclose NetBIOS, DNS, and OS build details from a server with NTLM authentication enabled.                                   |
| [`imap-brute`](https://nmap.org/nsedoc/scripts/imap-brute.html)               | `brute`, `intrusive`           | Perform a password brute-force attack using `LOGIN`, `PLAIN`, `CRAM-MD5`, `DIGEST-MD5`, or `NTLM` authentication.             |

>[!tip]+
> - List local Nmap scripts for IMAP:
> 
> ```bash
> ls -l /usr/share/nmap/scripts/*imap*
> ```

>[!example]-
> 
> ```bash
> sudo nmap -p 143,993 --script imap-capabilities 10.129.244.182
> ```
> 
> ```bash
> Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-09-27 08:28 CDT
> Nmap scan report for 10.129.244.182
> Host is up (0.075s latency).
> 
> PORT    STATE SERVICE
> 143/tcp open  imap
> |_imap-capabilities: ID ENABLE IMAP4rev1 IDLE STARTTLS more LOGINDISABLEDA0001 Pre-login SASL-IR OK have post-login listed capabilities LOGIN-REFERRALS LITERAL+
> 993/tcp open  imaps
> |_imap-capabilities: ID ENABLE IMAP4rev1 IDLE more AUTH=PLAINA0001 Pre-login SASL-IR OK have post-login listed capabilities LOGIN-REFERRALS LITERAL+
> 
> Nmap done: 1 IP address (1 host up) scanned in 0.50 seconds
> ```

### Banner grabbing

- Connect to the plaintext port with Netcat or Telnet:

```bash
nc -nv 10.10.11.5 143
```

```bash
telnet 10.10.11.5 143
```

- Connect to the encrypted port (`993`) over TLS:

```bash
openssl s_client -connect 10.10.11.5:993 -quiet -crlf
```

```bash
openssl s_client -connect 10.10.11.5:imaps
```

| Option     | Description                                             |
| ---------- | ------------------------------------------------------- |
| `-connect` | Connect to the specified `host:port`.                   |
| `-quiet`   | Suppress session and certificate output.                |
| `-crlf`    | Translate line feeds into CRLF as required by the protocol. |
| `-nv`      | (Netcat) Disable DNS resolution and print connection details. |

>[!example]-
>
> ```bash
> openssl s_client -connect 10.129.244.182:imaps
> ```
> 
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
>     Session-ID: BB0CB09AAE4D0129189DB0FA230B84A80350BE1401E6FC214AE0B382ED791B87
>     Session-ID-ctx: 
>     Resumption PSK: 733C1B74579A2119B1C80CA8BE50A08BEF0B5BFD3BD116C60A969A628DE0F3D8533E3281AFE4CD9AF99D189DD52051FA
>     PSK identity: None
>     PSK identity hint: None
>     SRP username: None
>     TLS session ticket lifetime hint: 7200 (seconds)
>     TLS session ticket:
>     0000 - 94 c7 b1 e1 6c 49 57 23-49 b2 11 b5 1a fe 39 c7   ....lIW#I.....9.
>     0010 - bb f0 a7 ea b9 7c bc 83-9d fc 0a f0 8f 21 b2 17   .....|.......!..
>     0020 - 10 e0 09 ae 19 9e 80 fb-dc 79 d3 ef a9 08 87 84   .........y......
>     0030 - e3 15 f0 5f fc 05 78 fd-1f 6f 56 54 02 a9 e4 05   ..._..x..oVT....
>     0040 - b1 08 62 9e 23 de 6d ba-14 d5 c8 3b 04 bc a1 99   ..b.#.m....;....
>     0050 - d4 51 8c a1 29 99 5f 1a-d7 28 df e8 98 35 41 a7   .Q..)._..(...5A.
>     0060 - 5c 6b 46 be 54 c0 6e 83-84 35 7b 21 a8 b4 56 53   \kF.T.n..5{!..VS
>     0070 - b0 5b 86 da c0 d1 e5 f6-1a 21 4d 31 06 32 5b b0   .[.......!M1.2[.
>     0080 - 2f 30 59 a1 4f 84 f5 ce-a6 8f 51 6e e5 62 c1 fa   /0Y.O.....Qn.b..
>     0090 - 14 d0 6d 3c 3b 91 8c 05-7e a6 05 69 16 a8 16 2d   ..m<;...~..i...-
>     00a0 - 1b 33 cd 3e 4d f1 da c5-0a f0 5d 77 33 9c 5d 28   .3.>M.....]w3.](
>     00b0 - 58 b1 d7 55 11 6c 14 fd-6a 37 b4 b3 e9 0e ab 7e   X..U.l..j7.....~
> 
>     Start Time: 1758980691
>     Timeout   : 7200 (sec)
>     Verify return code: 18 (self-signed certificate)
>     Extended master secret: no
>     Max Early Data: 0
> ---
> read R BLOCK
> * OK [CAPABILITY IMAP4rev1 SASL-IR LOGIN-REFERRALS ID ENABLE IDLE LITERAL+ AUTH=PLAIN]
> ```

### Discovering server capabilities

- Connect and issue the `CAPABILITY` command to list supported extensions and authentication mechanisms:

```bash
openssl s_client -connect 10.10.11.5:993 -quiet
A1 CAPABILITY
```

>[!example]-
> 
> ```bash
> A3 CAPABILITY
> * CAPABILITY IMAP4rev1 SASL-IR LOGIN-REFERRALS ID ENABLE IDLE SORT SORT=DISPLAY THREAD=REFERENCES THREAD=REFS THREAD=ORDEREDSUBJECT MULTIAPPEND URL-PARTIAL CATENATE UNSELECT CHILDREN NAMESPACE UIDPLUS LIST-EXTENDED I18NLEVEL=1 CONDSTORE QRESYNC ESEARCH ESORT SEARCHRES WITHIN CONTEXT=SEARCH LIST-STATUS BINARY MOVE SNIPPET=FUZZY PREVIEW=FUZZY LITERAL+ NOTIFY SPECIAL-USE
> A3 OK Capability completed (0.001 + 0.000 secs).
> ```

## Brute-forcing credentials

Once a valid username list is available, IMAP passwords can be brute-forced:

- Brute-force credentials using Hydra:

```bash
hydra -L usernames.txt -P /usr/share/wordlists/rockyou.txt imap://10.10.11.5
```

- Brute-force credentials using Medusa:

```bash
medusa -U usernames.txt -P /usr/share/wordlists/rockyou.txt -h 10.10.11.5 -M imap
```

| Option | Description                              |
| ------ | ---------------------------------------- |
| `-l`   | (Hydra) Set a single username to test.   |
| `-L`   | (Hydra) Read usernames from a file.      |
| `-u`   | (Medusa) Set a single username to test.  |
| `-U`   | Read usernames from a file.              |
| `-P`   | Read passwords from a wordlist file.     |
| `-h`   | (Medusa) Set the target host.            |
| `-M`   | (Medusa) Select the service module (`imap`). |

- Brute-force credentials using the Nmap [`imap-brute`](https://nmap.org/nsedoc/scripts/imap-brute.html) script:

```bash
nmap -p 143 --script imap-brute 10.10.11.5
```

- Supply custom wordlists to the script:

```bash
nmap -p 143 --script imap-brute --script-args userdb=usernames.txt,passdb=/usr/share/wordlists/rockyou.txt 10.10.11.5
```

- Brute-force the encrypted port (`993`):

```bash
nmap -p 993 --script imap-brute 10.10.11.5
```

>[!note] IMAP servers commonly rate-limit or temporarily block IP addresses after repeated failed authentication attempts. Start with a low thread count and adjust.
## Interacting with IMAP

### Authenticating to the server

- Connect over TLS and log in with the `LOGIN` command:

```bash
openssl s_client -connect 10.10.11.5:993 -quiet -crlf
A1 LOGIN jdoe@example.com 'passwd123'
```

- Authenticate and access a mailbox with cURL:

```bash
curl -k 'imaps://10.10.11.5' --user jdoe@example.com:'passwd123'
```

| Option   | Description                                              |
| -------- | -------------------------------------------------------- |
| `-k`     | Skip TLS certificate validation (self-signed certs).     |
| `--user` | Supply the `username:password` for authentication.       |

- List the mailboxes available to the account:

```bash
A2 LIST "" "*"
```

- Retrieve the status of a mailbox without opening it:

```bash
A3 STATUS INBOX (MESSAGES UNSEEN)
```

- Open a mailbox for access (`SELECT` for read-write, `EXAMINE` for read-only):

```bash
A4 SELECT INBOX
```

>[!example]-
> 
> ```bash
> A4 LIST "" "*"
> * LIST (\Noselect \HasChildren) "." DEV
> * LIST (\Noselect \HasChildren) "." DEV.DEPARTMENT
> * LIST (\HasNoChildren) "." DEV.DEPARTMENT.INT
> * LIST (\HasNoChildren) "." INBOX
> A4 OK List completed (0.006 + 0.000 + 0.005 secs).
> ```

>[!note] The `STATUS` command takes an argument specifying which mailbox attributes to return: `MESSAGES` (message count), `RECENT` (messages with the `\Recent` flag), `UIDNEXT` (next UID), `UIDVALIDITY` (UID validity), and `UNSEEN` (messages without the `\Seen` flag).

### Searching mailboxes

- **`SEARCH`**
	- Searches for messages in the selected mailbox matching the given criteria.
	- Returns a space-separated list of matching sequence numbers (or UIDs if the `UID` prefix is used).
	- By default, multiple terms are combined with `AND`, not `OR`.

- Syntax:

```bash
tag [UID] SEARCH [CHARSET <charset>] <criterion1> [<criterion2> ...]
```

- Search for sensitive content, administrative communications, and confidential documents:

```bash
SEARCH BODY "password"
SEARCH BODY "credential"
SEARCH BODY "confidential"
SEARCH FROM "admin"
SEARCH SUBJECT "urgent"
```

- Scope searches by time:

```bash
SEARCH SINCE 01-Jan-2024
SEARCH NEW
SEARCH BEFORE 01-Jan-2023
SEARCH SENTBEFORE 01-Jan-2023
```

- Combine criteria with boolean logic:

```bash
SEARCH OR FROM "ceo" FROM "admin"
SEARCH NOT DELETED
```

- Common `SEARCH` criteria:

| Search criterion          | Description                                                   | Example                                       |
| ------------------------- | ------------------------------------------------------------- | --------------------------------------------- |
| `ALL`                     | All messages.                                                 | `A1 SEARCH ALL`                               |
| `UNSEEN`                  | Messages without the `\Seen` flag.                            | `A2 SEARCH UNSEEN`                            |
| `FROM <string>`           | Messages with `<string>` in the `From` header.                | `A3 SEARCH FROM "admin"`                      |
| `SUBJECT <string>`        | Messages with `<string>` in the `Subject`.                    | `A4 SEARCH SUBJECT "password reset"`          |
| `BODY <string>`           | Messages with `<string>` in the message body.                 | `A5 SEARCH BODY "confidential"`               |
| `TEXT <string>`           | Messages with `<string>` in headers or body.                  | `A6 SEARCH TEXT "invoice"`                    |
| `SINCE <date>`            | Messages received on or after a date (format: `DD-Mon-YYYY`). | `A7 SEARCH SINCE 01-Jan-2023`                 |
| `LARGER <n>`              | Messages larger than `n` bytes.                               | `A8 SEARCH LARGER 1000000`                    |
| `HEADER <field> <string>` | Messages with `<string>` in a specific header field.          | `A9 SEARCH HEADER "X-Priority" "1"`           |
| `OR <crit1> <crit2>`      | Logical OR of two criteria.                                   | `A10 SEARCH OR BODY "password" BODY "secret"` |
| `NOT <criterion>`         | Logical NOT.                                                  | `A11 SEARCH NOT DELETED`                      |

>[!note] Dates must be in the format `DD-Mon-YYYY` (e.g., `29-Sep-2025`).

>[!note]- Full list of `SEARCH` criteria
> 
> | Search term               | Description                                       | Example usage                            |
> | ------------------------- | ------------------------------------------------- | ---------------------------------------- |
> | `ALL`                     | All messages in the mailbox.                      | `A1 SEARCH ALL`                          |
> | `ANSWERED`                | Messages with the `\Answered` flag set.           | `A2 SEARCH ANSWERED`                     |
> | `BCC <string>`            | Messages with `<string>` in the `BCC` field.      | `A3 SEARCH BCC "admin@example.com"`      |
> | `BEFORE <date>`           | Messages before date (format: `DD-MM-YYYY`).     | `A4 SEARCH BEFORE 28-Sep-2025`           |
> | `BODY <string>`           | Messages with `<string>` in body.                 | `A5 SEARCH BODY "confidential"`          |
> | `CC <string>`             | Messages with `<string>` in the CC field.         | `A6 SEARCH CC "team"`                    |
> | `DELETED`                 | Messages with the `\Deleted` flag set.            | `A7 SEARCH DELETED`                      |
> | `DRAFT`                   | Messages with the `\Draft` flag set.              | `A8 SEARCH DRAFT`                        |
> | `FLAGGED`                 | Messages with the `\Flagged` flag set.            | `A9 SEARCH FLAGGED`                      |
> | `FROM <string>`           | Messages with `<string>` in the `FROM` field.     | `A10 SEARCH FROM "alice@example.com"`    |
> | `HEADER <field> <string>` | Messages with `<string>` in the specified header. | `A11 SEARCH HEADER "X-Mailer" "Outlook"` |
> | `KEYWORD <flag>`          | Messages with the specified keyword flag set.     | `A12 SEARCH KEYWORD "$Important"`        |
> | `LARGER <n>`              | Messages larger than `n` octets.                  | `A13 SEARCH LARGER 1000000`              |
> | `NEW`                     | Messages with `\Recent` but not `\Seen` flag.     | `A14 SEARCH NEW`                         |
> | `NOT <search-key>`        | Messages not matching search-key.                 | `A15 SEARCH NOT DELETED`                 |
> | `OLD`                     | Messages that are not `\Recent`.                  | `A16 SEARCH OLD`                         |
> | `ON <date>`               | Messages on specified date.                       | `A17 SEARCH ON 28-Sep-2025`              |
> | `OR <key1> <key2>`        | Messages matching `key1` or `key2`.               | `A18 SEARCH OR FROM "bob" TO "carol"`    |
> | `RECENT`                  | Messages with `\Recent` flag set.                 | `A19 SEARCH RECENT`                      |
> | `SEEN`                    | Messages with `\Seen` flag set.                   | `A20 SEARCH SEEN`                        |
> | `SENTBEFORE <date>`       | Messages sent before date (Date: header).         | `A21 SEARCH SENTBEFORE 01-Sep-2025`      |
> | `SENTON <date>`           | Messages sent on date (Date: header).             | `A22 SEARCH SENTON 28-Sep-2025`          |
> | `SENTSINCE <date>`        | Messages sent since date (Date: header).          | `A23 SEARCH SENTSINCE 01-Sep-2025`       |
> | `SINCE <date>`            | Messages since date (internal date).              | `A24 SEARCH SINCE 01-Sep-2025`           |
> | `SMALLER <n>`             | Messages smaller than `n` octets.                 | `A25 SEARCH SMALLER 5000`                |
> | `SUBJECT <string>`        | Messages with `<string>` in the subject field.    | `A26 SEARCH SUBJECT "urgent"`            |
> | `TEXT <string>`           | Messages with `<string>` in a header or body.     | `A27 SEARCH TEXT "project"`              |
> | `TO <string>`             | Messages with `<string>` in the `TO` field.       | `A28 SEARCH TO "dave@example.com"`       |
> | `UID <set>`               | Messages with specified UIDs.                     | `A29 UID SEARCH 100:200`                 |
> | `UNANSWERED`              | Messages without `\Answered` flag.                | `A30 SEARCH UNANSWERED`                  |
> | `UNDELETED`               | Messages without `\Deleted` flag.                 | `A31 SEARCH UNDELETED`                   |
> | `UNDRAFT`                 | Messages without `\Draft` flag.                   | `A32 SEARCH UNDRAFT`                     |
> | `UNFLAGGED`               | Messages without `\Flagged` flag.                 | `A33 SEARCH UNFLAGGED`                   |
> | `UNKEYWORD <flag>`        | Messages without the specified keyword flag.      | `A34 SEARCH UNKEYWORD "$Junk"`           |
> | `UNSEEN`                  | Messages without `\Seen` flag.                    | `A35 SEARCH UNSEEN`                      |

### Retrieving messages

- **`FETCH`**
	- Retrieves data associated with a message (reading emails).
	- The client specifies which messages or message parts to fetch, and the server returns the matching data.

- Syntax:

```bash
tag [UID] FETCH <message_set> <data_item or macro>
```

- Retrieve a message body without marking it as read (`BODY.PEEK` does not set the `\Seen` flag):

```bash
A1 FETCH 1 BODY.PEEK[1]
```

>[!example]-
> ```bash
> A1 FETCH 1 BODY.PEEK[1]
> * 1 FETCH (BODY[1] {102}
> Hi admin,
> 
> How can I change my password to something more secure? 
> 
> flag: HTB{w34k_p4$$w0rd}
> 
> 
> )
> A1 OK FETCH completed
> ```

- Inspect the MIME structure to locate attachments:

```bash
A1 FETCH 1 BODYSTRUCTURE
```


- Common message data items:

| Data item / macro | Description                                                                                               |
| ----------------- | --------------------------------------------------------------------------------------------------------- |
| `FULL`            | Macro for `(FLAGS INTERNALDATE RFC822.SIZE ENVELOPE BODY)`.                                               |
| `ALL`             | Macro for `(FLAGS INTERNALDATE RFC822.SIZE ENVELOPE)`.                                                    |
| `FAST`            | Macro for `(FLAGS INTERNALDATE RFC822.SIZE)`.                                                             |
| `ENVELOPE`        | Parsed header information (From, To, Subject, Date, etc.).                                                |
| `BODYSTRUCTURE`   | The MIME structure of the message. Useful for finding attachments.                                        |
| `FLAGS`           | The flags set for the message (`\Seen`, `\Deleted`, etc.).                                                |
| `RFC822`          | The entire raw message content (equivalent to `BODY[]`).                                                  |
| `RFC822.HEADER`   | The full, raw headers of the message.                                                                     |
| `RFC822.TEXT`     | The body of the message.                                                                                  |
| `BODY[<part>]`    | A specific part of a multipart message (e.g., `BODY[1]` for the first part, `BODY[2]` for an attachment). |
| `BODY.PEEK[...]`  | Same as `BODY[...]` but does not set the `\Seen` flag. **Very useful for recon.**                         |
| `UID`             | The unique identifier of the message.                                                                     |

>[!note] Messages remain on the server unless explicitly deleted or moved.

## References and further reading

- [`Internet Message Access Protocol — Wikipedia`](https://en.wikipedia.org/wiki/Internet_Message_Access_Protocol)
- [`Internet Message Access Protocol - Version 4rev1 — RFC 3501`](https://datatracker.ietf.org/doc/html/rfc3501)
- [`IMAP 101: Manual IMAP Sessions — atmail`](https://www.atmail.com/blog/imap-101-manual-imap-sessions/)
- [`IMAP Commands — atmail`](https://www.atmail.com/blog/imap-commands/)
- [`IMAP Cheat Sheet for Penetration Testers — Route Zero`](https://routezero.security/2025/04/20/imap-cheat-sheet-for-penetration-testers/)
- [`Internet Message Access Protocol (IMAP) Capabilities registry — IANA`](https://www.iana.org/assignments/imap-capabilities/imap-capabilities.xhtml)
- [`Introduction to IMAP — nickb.dev`](https://nickb.dev/blog/introduction-to-imap/)
- [`143,993 - Pentesting IMAP — HackTricks`](https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-imap.html)
