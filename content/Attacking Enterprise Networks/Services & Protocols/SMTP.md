---
created: 2026-09-22
updated: 2026-09-27
tags:
  - services_n_protocols
---
## SMTP

>**[SMTP (Simple Mail Transfer Protocol)](https://en.wikipedia.org/wiki/Simple_Mail_Transfer_Protocol)** is an application-layer, text-based communication protocol defined in [`RFC 5321`](https://www.rfc-editor.org/rfc/rfc5321), used to transmit and relay electronic mail between Mail Transfer Agents (MTAs) across TCP/IP networks.

- SMTP operates on a client-server model — SMTP clients (Mail Transfer Agents, MTAs) speak to SMTP servers to hand off messages hop-by-hop until they reach their destination mail server.
- It is a **store-and-forward** protocol: SMTP does not guarantee end-to-end delivery; it only ensures that the message is handed off to the next relay in line.

> [!note] SMTP is defined in [`RFC 5321`](https://www.rfc-editor.org/rfc/rfc5321). The format of email messages themselves (headers, body) is defined separately in [`RFC 5322`](https://www.rfc-editor.org/rfc/rfc5322).

### SMTP ports

| Port   | Protocol             | Description                                                                                                                                                                                                                                                  |
| ------ | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `25`   | SMTP                 | **Legacy MTA-to-MTA relay port ([`RFC 5321`](https://www.rfc-editor.org/rfc/rfc5321))**. Typically unauthenticated and historically plaintext (though `STARTTLS` may be supported but not enforced). <br>Often **blocked outbound by ISPs/cloud providers**. |
| `587`  | SMTP (Submission)    | **Modern message submission port ([`RFC 6409`](https://www.rfc-editor.org/rfc/rfc6409))** used by clients (MUA → MSA). <br>Requires authentication (`AUTH`); typically supports `STARTTLS` (explicit TLS upgrade).                                           |
| `465`  | SMTPS (implicit TLS) | **SMTP over implicit TLS**. <br>Previously deprecated but reintroduced ([`RFC 8314`](https://datatracker.ietf.org/doc/html/rfc8314)) for secure submission.<br>Often seen in legacy or tightly controlled environments.                                      |
| `2525` | SMTP (alternate)     | **Non-standard fallback submission port**, commonly used when `25`/`587` are blocked by network policies. <br>Behavior usually mirrors port `587` (`AUTH` + `STARTTLS`), but implementations vary.                                                           |

### Encryption

>[!important] By default, SMTP traffic is not encrypted.

Two mechanisms exist to add TLS:

- **`STARTTLS`** — **opportunistic TLS**, or explicit TLS upgrade:
	- The client upgrades an existing plaintext connection (usually port `25` or `587`) using the `STARTTLS` command.
	- This is done _after_ the initial `EHLO` (see [[#Connection establishment and authentication]]).
	- **Encryption is optional unless enforced.**

> [!note] `STARTTLS` is _opportunistic_ — it upgrades to TLS if the server supports it, but it does not enforce it.

- **Implicit TLS (SMTPS, port `465`)**:
	- TLS is established *immediately* upon connection (usually using a dedicated port, `465`); no plaintext phase at all.
	- Defined in [`RFC 8314`](https://datatracker.ietf.org/doc/html/rfc8314); was originally deprecated in favor of `STARTTLS`, though it remains supported by many providers for compatibility.

### Connection establishment and authentication

1. **Connection establishment**:
	- The client opens a TCP connection to the server (on port `587`, `25`, or `465`).
	- The server responds with a `220` greeting.

```bash
220 smtp.example.com ESMTP Service Ready
```

2. **`EHLO`/`HELO`**:
	- The client sends `EHLO` (or `HELO` for legacy servers) to identify itself and request the server's capabilities.
	- The server responds with `250` and lists supported extensions (e.g., `AUTH`, `STARTTLS`).

```bash
EHLO client.example.com
250-smtp.example.com greets client.example.com
250-STARTTLS
250-AUTH LOGIN PLAIN CRAM-MD5
250 SIZE 10485760
```

3. **`STARTTLS`** (if supported):
	- If `STARTTLS` is listed, the client sends the `STARTTLS` command to establish a TLS connection.
	- The server responds with `220`, and both sides perform a TLS handshake.
	- Once encrypted, the client sends another `EHLO` to re-negotiate the session capabilities over the secure channel — the extension list may differ (some extensions are only advertised post-TLS).

```bash
STARTTLS
220 Ready to start TLS
```

>[!tip]+
> - Interact with SMTP over TLS manually:
> 
> ```bash
> openssl s_client -connect 10.10.11.5:587 -starttls smtp
> ```
> 
> - Or for implicit TLS (port `465`):
> 
> ```bash
> openssl s_client -connect 10.10.11.5:465 -crlf -quiet
> ```

4. **`AUTH`**:
	- After establishing a connection and optionally upgrading to TLS, the client can authenticate using the `AUTH` command followed by an authentication exchange for the selected mechanism. These mechanisms are defined by **SASL**.
	- The server responds with `235` if authentication was successful, or an error code if it failed.

>**SMTP SASL (Simple Authentication and Security Layer)** is a framework defined in [`RFC 4954`](https://www.rfc-editor.org/rfc/rfc4954) that enables SMTP clients to authenticate with a server using various mechanisms such as `PLAIN`, `LOGIN`, `CRAM-MD5`, or `GSSAPI`.

>[!note] See [`Simple Authentication and Security Layer (SASL) Mechanisms — IANA`](https://www.iana.org/assignments/sasl-mechanisms/sasl-mechanisms.xhtml).

- Common `AUTH` mechanisms:

| Mechanism                                            | Description                                                                                                                                                                                                   |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`PLAIN`](https://www.rfc-editor.org/rfc/rfc4616)    | Username and password; <br>The client encodes `username\0username\0password` as a single Base64 string.<br>Plaintext; dangerous without TLS.                                                                 |
| `LOGIN`                                              | Username and password;<br>The client sends username and password in two steps, as separate Base64-encoded strings.<br>Plaintext; dangerous without TLS (same as `PLAIN`).<br>Obsolete in favor of `PLAIN`. |
| [`CRAM-MD5`](https://en.wikipedia.org/wiki/CRAM-MD5) | Challenge-response authentication: server sends a nonce, client hashes it with the password using [HMAC-MD5](https://en.wikipedia.org/wiki/HMAC).<br>Obsolete.                                                |
| `OAUTH2`                                             | Token-based authentication; used by major providers such as Gmail and Outlook.<br>Strong.                                                                                                                      |
| `GSSAPI`                                             | Uses the [Generic Security Service API (GSSAPI)](https://en.wikipedia.org/wiki/Generic_Security_Services_Application_Programming_Interface) to enable **Kerberos-based login**.<br>Secure.                |

>[!example]+
>
> 
> ```bash
> 220 smtp.example.com ESMTP Service Ready
> EHLO client.example.com
> 250-smtp.example.com greets client.example.com
> 250-STARTTLS
> 250-AUTH LOGIN PLAIN CRAM-MD5
> STARTTLS
> 220 Ready to start TLS
> EHLO client.example.com
> 250-smtp.example.com greets client.example.com
> 250-AUTH LOGIN PLAIN CRAM-MD5
> AUTH LOGIN
> 334 VXNlcm5hbWU6
> <base64-encoded username>
> 334 UGFzc3dvcmQ6
> <base64-encoded password>
> 235 Authentication successful
> ```

- After the negotiation and authentication phase completes, the client submits the email message or issues other commands, and then terminates the session.

### SMTP commands

>SMTP operates as a line-oriented, request-response protocol. The client sends **text commands** and the server replies with numeric status codes.

| **Command** | When sent                       | **Description**                                                                                                     |
| ----------- | ------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `EHLO`      | After connection establishment. | Identify the client and request the server's supported extensions (extended hello).                                 |
| `HELO`      | After connection establishment. | Identify the client for basic SMTP without extensions (legacy hello).                                               |
| `STARTTLS`  | After `EHLO`.                   | Upgrade the connection to TLS (opportunistic TLS).                                                                  |
| `AUTH`      | After `EHLO`/`STARTTLS`.        | Initiate authentication using a specified [SASL](https://datatracker.ietf.org/doc/html/rfc4422) mechanism (e.g., `PLAIN`, `LOGIN`, `CRAM-MD5`). |
| `VRFY`      | After `EHLO`.                   | Verify whether a mailbox exists on the server (used for user enumeration).                                          |
| `EXPN`      | After `EHLO`.                   | Expand a mailing list alias to reveal individual addresses (used for enumeration).                                  |
| `HELP`      | Anytime.                        | Request the list of commands supported by the server.                                                               |
| `NOOP`      | Anytime.                        | Keep the connection alive and check server responsiveness (no operation); prevents timeout disconnection.           |
| `QUIT`      | End of session.                 | Terminate the session gracefully; the server closes the connection.                                                 |

- Mail transaction:

| **Command** | When sent                   | **Description**                                                                                     |
| ----------- | --------------------------- | --------------------------------------------------------------------------------------------------- |
| `MAIL FROM` | After `AUTH`/`EHLO`.        | Begin a mail transaction and set the envelope sender.                                               |
| `RCPT TO`   | After `MAIL FROM`.          | Set one recipient per command; repeat for multiple recipients.                                      |
| `DATA`      | After `RCPT TO`.            | Signal the start of message content; the body ends with a single `.` on its own line.               |
| `RSET`      | Anytime during transaction. | Reset the current mail transaction and clear sender/recipient state while keeping the connection open. |

### SMTP response codes

| Code  | Description                                                                                      |
| ----- | ------------------------------------------------------------------------------------------------ |
| `220` | Service ready;<br>Server is up and accepting connections.                                        |
| `235` | Authentication successful — valid credentials accepted.                                          |
| `250` | Command `OK` — generic success.                                                                  |
| `251` | User not local; forwarding — valid user, but relayed elsewhere.                                  |
| `252` | Cannot verify, but will attempt delivery. This means the user _may_ exist; server won't confirm. |
| `334` | Auth challenge — waiting for client's Base64-encoded credential.                                 |
| `354` | Start input — server ready to receive message body.                                              |
| `421` | Service unavailable — server is closing; try again later.                                        |
| `450` | Mailbox unavailable (temporary) — temporary failure; retry is appropriate.                       |
| `550` | Mailbox unavailable (permanent) — user doesn't exist, or relay denied.                           |
| `551` | User not local; relay rejected.                                                                  |
| `552` | Exceeded storage (quota exceeded).                                                               |
| `553` | Mailbox name invalid (malformed address).                                                        |

> [!note] During user enumeration, `250`, `251`, and `252` all indicate the user _may_ exist. `550` and `553` are the clearest "nope." Pay attention to how the server responds — different servers handle this differently.


## Enumerating SMTP

### Port scanning and version detection

- Scan the default SMTP ports (`25`, `465`, `587`) with service version detection:

```bash
sudo nmap -sV -p 25,465,587 10.10.11.5
```

> [!tip]+
> - Scan the full TCP range with version detection in case SMTP is bound to a non-standard port (e.g., `2525`):
> 
> ```bash
> sudo nmap -sV -p- 10.10.11.5
> ```

- Run all available SMTP NSE scripts:

```bash
sudo nmap -p 25,465,587 --script "smtp-*" 10.10.11.5
```

| Option | Description |
| :--- | :--- |
| `-sV` | Enable service version detection. |
| `-p` | Specify destination port(s) to scan (`25,465,587` or `-p-` for all ports). |
| `--script` | Execute a specific NSE script or glob expression. |

>[!example]-
> 
> ```bash
> sudo nmap 10.129.31.148 -p 25 --script smtp*
> ```
> 
> ```bash
> Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-09-24 09:48 CDT
> Nmap scan report for 10.129.31.148
> Host is up (0.075s latency).
> 
> PORT   STATE SERVICE
> 25/tcp open  smtp
> |_smtp-commands: mail1, PIPELINING, SIZE 10240000, VRFY, ETRN, STARTTLS, ENHANCEDSTATUSCODES, 8BITMIME, DSN, SMTPUTF8, CHUNKING
> |_smtp-open-relay: Server is an open relay (16/16 tests)
> | smtp-vuln-cve2010-4344: 
> |_  The SMTP server is not Exim: NOT VULNERABLE
> | smtp-enum-users: 
> |   root
> |   admin
> |   administrator
> |   webadmin
> |   sysadmin
> |   netadmin
> |   guest
> |   user
> |   web
> |_  test
> 
> Nmap done: 1 IP address (1 host up) scanned in 13.60 seconds
> ```

- Key Nmap SMTP scripts:

| Script                                                                                  | Categories                           | Description                                                                                                                                        |
| --------------------------------------------------------------------------------------- | ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`smtp-commands`](https://nmap.org/nsedoc/scripts/smtp-commands.html)                   | `default`, `discovery`, `safe`       | Issue `EHLO` and `HELP` to gather the extended commands supported by the SMTP server.                                                              |
| [`smtp-enum-users`](https://nmap.org/nsedoc/scripts/smtp-enum-users.html)               | `auth`, `external`, `intrusive`      | Enumerate users on the server by issuing the `VRFY`, `EXPN`, or `RCPT TO` commands.                                                                |
| [`smtp-brute`](https://nmap.org/nsedoc/scripts/smtp-brute.html)                         | `brute`, `intrusive`                 | Perform a password brute-force attack using `LOGIN`, `PLAIN`, `CRAM-MD5`, `DIGEST-MD5`, or `NTLM` authentication.                                  |
| [`smtp-ntlm-info`](https://nmap.org/nsedoc/scripts/smtp-ntlm-info.html)                 | `default`, `discovery`, `safe`       | Retrieve NetBIOS, DNS, and OS build information by sending a null-credential SMTP NTLM authentication request that triggers an NTLMSSP response.   |
| [`smtp-open-relay`](https://nmap.org/nsedoc/scripts/smtp-open-relay.html)               | `discovery`, `intrusive`, `external` | Test for an open relay by issuing a predefined combination of SMTP commands.                                                                       |
| [`smtp-strangeport`](https://nmap.org/nsedoc/scripts/smtp-strangeport.html)             | `malware`, `safe`                    | Check whether SMTP is running on a non-standard port.                                                                                              |
| [`smtp-vuln-cve2010-4344`](https://nmap.org/nsedoc/scripts/smtp-vuln-cve2010-4344.html) | `exploit`, `intrusive`, `vuln`       | Test for the [`CVE-2010-4344`](https://nvd.nist.gov/vuln/detail/cve-2010-4344) Exim vulnerability.                                                 |
| [`smtp-vuln-cve2011-1720`](https://nmap.org/nsedoc/scripts/smtp-vuln-cve2011-1720.html) | `intrusive`, `vuln`                  | Test for the [`CVE-2011-1720`](https://www.postfix.org/CVE-2011-1720.html) Postfix vulnerability.                                                  |
| [`smtp-vuln-cve2011-1764`](https://nmap.org/nsedoc/scripts/smtp-vuln-cve2011-1764.html) | `intrusive`, `vuln`                  | Test for the [`CVE-2011-1764`](https://www.cve.org/CVERecord?id=CVE-2011-1764) Exim vulnerability.                                                 |

>[!tip]+
> - List local Nmap scripts for SMTP:
> 
> ```bash
> ls -l /usr/share/nmap/scripts/*smtp*
> ```

### Banner grabbing

- Grab the banner using Telnet:

```bash
telnet 10.10.11.5 25
```

- Grab the banner using Netcat:

```bash
nc 10.10.11.5 25
```

- Send a one-liner `EHLO` and read the response:

```bash
echo "EHLO test" | nc 10.10.11.5 25
```

- Grab the banner over implicit TLS on port `465`:

```bash
openssl s_client -connect 10.10.11.5:465 -crlf -quiet
```

- Grab the banner over `STARTTLS` on port `587`:

```bash
openssl s_client -connect 10.10.11.5:587 -starttls smtp
```

| Option | Description |
| :--- | :--- |
| `-connect` | Connect to the specified `host:port`. |
| `-starttls smtp` | Perform the SMTP `STARTTLS` upgrade before the TLS handshake. |
| `-crlf` | Translate line feeds into CRLF as required by SMTP. |
| `-quiet` | Suppress session and certificate output. |

### Discovering mail servers via DNS

- Retrieve the `MX` records for a domain to identify which servers handle its mail:

```bash
dig MX example.com
```

```bash
nslookup -type=MX example.com
```

```bash
host -t MX example.com
```

>[!tip]+
> - `MX` records carry a priority value — lower numbers indicate higher priority.

- Print only the mail server names:

```bash
dig +short MX example.com
```

>[!note] See [[Querying DNS]].

### Enumerating users

There are three commands that enumerate valid usernames and email addresses on an SMTP server:

- **`VRFY` (verify) command**
	- Verifies whether a given mailbox exists on the server.
	- `250`, `251`, `252` response codes → the request was accepted; the username likely exists.
	- `550`, `553` response codes → error; the username is invalid.

> [!example]+
> ```bash
> VRFY root
> 252 2.0.0 root
> ```
> 
> ```bash
> VRFY fakeuser99
> 550 5.1.1 <fakeuser99>: Recipient address rejected: User unknown
> ```

- **`EXPN` (expand) command**
	- Expands a mailing list or alias to reveal individual addresses.
	- `250` response code → the alias was successfully expanded (and is valid).
	- `550` response code → error; the username is invalid.
	- On a poorly configured server, `EXPN all` might dump the entire organization's email list.

>[!example]+ 
> ```bash
> EXPN admin
> 250 2.0.0 root <root@example.com>
> ```
> 
> ```bash
> EXPN nobody
> 550 5.1.1 <nobody>: Recipient address rejected
> ```

>[!warning] To prevent user enumeration, `VRFY` and `EXPN` are often disabled on mail servers.

- **`RCPT TO` (recipient to) command**
	- Starts sending an email by specifying its recipient. It cannot be disabled — it is fundamental to how email works.
	- `250` response code → the username exists.
	- `550` response code → error; the username is invalid.

>[!important] Unlike `VRFY` and `EXPN`, **`RCPT TO` cannot be disabled**. It is required for normal email operation.

- Automate user enumeration using the [`smtp-user-enum`](https://pentestmonkey.net/tools/user-enumeration/smtp-user-enum) script ([`GitHub`](https://github.com/pentestmonkey/smtp-user-enum)):

```bash
smtp-user-enum -M RCPT -U usernames.txt -D example.com -t 10.10.11.5
```

| Option | Description                                                                          |
| ------ | ------------------------------------------------------------------------------------ |
| `-M`   | Select the enumeration method: `EXPN`, `VRFY`, or `RCPT` (default: `VRFY`).          |
| `-u`   | Check a single username on the target server.                                        |
| `-D`   | Append this domain to each username checked (default: none).                         |
| `-U`   | Read the list of usernames to check from a file.                                     |
| `-t`   | Set the target SMTP server.                                                          |
| `-T`   | Read the list of target SMTP servers from a file.                                    |
| `-p`   | Set the TCP port on which the SMTP service runs (default: `25`).                     |
| `-m`   | Set the maximum number of processes (default: `5`).                                  |

>[!example]-
> ```bash
> perl smtp-user-enum.pl -M RCPT -U users.list -D inlanefreight.htb -t 10.129.203.12
> ```
> 
> ```bash
> Starting smtp-user-enum v1.2 ( http://pentestmonkey.net/tools/smtp-user-enum )
> 
>  ----------------------------------------------------------
> |                   Scan Information                       |
>  ----------------------------------------------------------
> 
> Mode ..................... RCPT
> Worker Processes ......... 5
> Usernames file ........... users.list
> Target count ............. 1
> Username count ........... 79
> Target TCP port .......... 25
> Query timeout ............ 5 secs
> Target domain ............ inlanefreight.htb
> 
> ######## Scan started at Thu Oct 16 07:14:41 2025 #########
> 10.129.203.12: marlin@inlanefreight.htb exists
> ######## Scan completed at Thu Oct 16 07:14:47 2025 #########
> 1 results.
> 
> 79 queries in 6 seconds (13.2 queries / sec)
> ```

- Or use the [`smtp-enum-users`](https://nmap.org/nsedoc/scripts/smtp-enum-users.html) Nmap script:

```bash
nmap --script smtp-enum-users \
	--script-args smtp-enum-users.methods={VRFY,EXPN,RCPT} \
	--script-args smtp-enum-users.domain=example.com \
	-p 25,465,587 \
10.10.11.5
```

## Brute-forcing credentials

Once a valid username list is available, SMTP passwords can be brute-forced:

- Brute-force credentials using Medusa:

```bash
medusa -M smtp -h 10.10.11.5 -u jdoe@example.com -P /usr/share/wordlists/rockyou.txt -n 587 -e ns
```

| Option  | Description                                                                              |
| :------ | :--------------------------------------------------------------------------------------- |
| `-M`    | Specify the service module name (`smtp`).                                                |
| `-h`    | Set the target IP address or hostname.                                                   |
| `-n`    | Set the destination port.                                                                |
| `-u`    | Set a single username to test.                                                           |
| `-U`    | Read usernames from a file.                                                              |
| `-P`    | Read passwords from a wordlist file.                                                     |
| `-e ns` | Test additional passwords (`n` for empty password, `s` for password equal to username). |

- Brute-force credentials using Hydra:

```bash
hydra -l jdoe@example.com -P /usr/share/wordlists/rockyou.txt smtp://10.10.11.5
```

- Brute-force credentials on a non-standard port:

```bash
hydra -l jdoe@example.com -P /usr/share/wordlists/rockyou.txt smtp://10.10.11.5:2525
```

```bash
hydra -L usernames.txt -P /usr/share/wordlists/rockyou.txt -s 2525 10.10.11.5 smtp
```

| Option    | Description                              |
| :-------- | :--------------------------------------- |
| `-l`      | Set a single username to test.           |
| `-L`      | Read usernames from a wordlist file.     |
| `-P`      | Read passwords from a wordlist file.     |


- Brute-force credentials using the Nmap [`smtp-brute`](https://nmap.org/nsedoc/scripts/smtp-brute.html) script:

```bash
nmap -p 25 --script smtp-brute \
  --script-args userdb=usernames.txt,passdb=/usr/share/wordlists/rockyou.txt \
  10.10.11.5
```

>[!note] SMTP servers commonly rate-limit or temporarily block IP addresses after repeated failed authentication attempts. Start with `-t 3` or `-t 5` in Hydra and adjust. Watch for `421 Too many connections` or increasingly delayed `535 Authentication failed` responses — these indicate rate-limiting.

## Sending emails from the command line

### `swaks`

>[`swaks`](https://github.com/jetmore/swaks) (Swiss Army Knife for SMTP) is a command-line tool designed for testing and debugging SMTP servers.


- Send a test email:

```bash
swaks --to victim@example.com --from sender@attacker.com --server 10.10.11.5
```

- Send an authenticated email:

```bash
swaks --to victim@example.com \
      --from jdoe@example.com \
      --auth-user jdoe@example.com \
      --auth-password 'passwd123' \
      --server 10.10.11.5 --port 587
```

- Send over TLS:

```bash
swaks --to victim@example.com \
      --from jdoe@example.com \
      --server 10.10.11.5 --port 587 \
      --tls \
      --auth-user jdoe@example.com \
      --auth-password 'passwd123'
```

- Send a spoofed phishing email with custom headers:

```bash
swaks --to victim@example.com \
      --from ceo@example.com \
      --header "Subject: Urgent: Action Required" \
      --header "Reply-To: attacker@evil.com" \
      --body "Please review the attached document and respond by EOD." \
      --server 10.10.11.5
```

- Send an email with an attachment:

```bash
swaks --to victim@example.com \
      --from sender@attacker.com \
      --attach /path/to/payload.pdf \
      --server 10.10.11.5
```

- Test for an open relay:

```bash
swaks --to external@gmail.com \
      --from external@yahoo.com \
      --server 10.10.11.5 --port 25
```

| Option | Description |
| :--- | :--- |
| `--to` | Set the envelope and header recipient address. |
| `--from` | Set the envelope and header sender address. |
| `--server` | Specify the target SMTP server. |
| `--port` | Specify the destination port. |
| `--auth-user` | Set the username for SMTP authentication. |
| `--auth-password` | Set the password for SMTP authentication. |
| `--tls` | Force a `STARTTLS` upgrade before the mail transaction. |
| `--header` | Add a custom message header. |
| `--body` | Set the message body content. |
| `--attach` | Attach a local file to the message. |

### `sendemail`

- Send an email:

```bash
sendemail -f sender@attacker.com \
          -t victim@example.com \
          -u "Subject Here" \
          -m "Message body" \
          -s 10.10.11.5:25
```

- Send an authenticated email:

```bash
sendemail -f jdoe@example.com \
          -t victim@example.com \
          -u "Quarterly Report" \
          -m "Please find the report attached." \
          -s 10.10.11.5:587 \
          -xu jdoe@example.com \
          -xp 'passwd123'
```

| Option | Description |
| :--- | :--- |
| `-f` | Set the sender (`FROM`) address. |
| `-t` | Set the recipient (`TO`) address. |
| `-u` | Set the message subject line. |
| `-m` | Set the message body. |
| `-s` | Specify the target SMTP server and port. |
| `-xu` | Set the username for SMTP authentication. |
| `-xp` | Set the password for SMTP authentication. |
## References and further reading

- [`Simple Mail Transfer Protocol — Wikipedia`](https://en.wikipedia.org/wiki/Simple_Mail_Transfer_Protocol)
- [`Simple Mail Transfer Protocol — RFC 5321`](https://www.rfc-editor.org/rfc/rfc5321)
- [`Internet Message Format — RFC 5322`](https://datatracker.ietf.org/doc/html/rfc5322)
- [`SMTP Service Extension for Authentication — RFC 4954`](https://datatracker.ietf.org/doc/html/rfc4954)
- [`Simple Authentication and Security Layer (SASL) — RFC 4422`](https://datatracker.ietf.org/doc/html/rfc4422)

- [`Opportunistic TLS — Wikipedia`](https://en.wikipedia.org/wiki/Opportunistic_TLS)
- [`Internet Message Access Protocol — Wikipedia`](https://en.wikipedia.org/wiki/Internet_Message_Access_Protocol)
- [`Post Office Protocol — Wikipedia`](https://en.wikipedia.org/wiki/Post_Office_Protocol)
- [`Introduction to IMAP — nickb.dev`](https://nickb.dev/blog/introduction-to-imap/)
- [`SMTP Authentication — Wikipedia`](https://en.wikipedia.org/wiki/SMTP_Authentication)
- [`Simple Authentication and Security Layer (SASL) Mechanisms — IANA`](https://www.iana.org/assignments/sasl-mechanisms/sasl-mechanisms.xhtml)

- [`4 ways to SMTP Enumeration — Hacking Articles`](https://www.hackingarticles.in/4-ways-smtp-enumeration/)
- [`smtp-user-enum — pentestmonkey`](https://pentestmonkey.net/tools/user-enumeration/smtp-user-enum)

- [`SMTP (Simple Mail Transfer Protocol) — Hackviser`](https://hackviser.com/tactics/pentesting/services/smtp)

- TODO: 
	- information gathering on a compromised email server.