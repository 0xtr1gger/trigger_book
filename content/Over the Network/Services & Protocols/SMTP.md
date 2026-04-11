---
created: 2026-04-03
color: "linear-gradient(45deg, #23d4fd 0%, #3a98f0 50%, #b721ff 100%)"
---
## SMTP

>**[SMTP (Simple Mail Transfer Protocol)](https://en.wikipedia.org/wiki/Simple_Mail_Transfer_Protocol)** is an application-layer, text-based communication protocol defined in [`RFC 5321`](https://www.rfc-editor.org/rfc/rfc5321), used to transmit and relay electronic mail between Mail Transfer Agents (MTAs) across TCP/IP networks.

- SMTP operates on a client-server model — SMTP clients (Mail Transfer Agents, MTAs) speak to SMTP servers to hand off messages hop-by-hop until they reach their destination mail server. 
- It's a **store-and-forward** protocol: SMTP doesn't guarantee delivery end-to-end; it just ensures the message gets handed off to the next relay in line.

> [!note] SMTP is defined in [`RFC 5321`](https://www.rfc-editor.org/rfc/rfc5321). The format of email messages themselves (headers, body) is defined separately in [`RFC 5322`](https://www.rfc-editor.org/rfc/rfc5322).

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
- **`STARTTLS`**  — **Opportunistic TLS**, or Explicit TLS upgrade
	- The client upgrades an existing plaintext connection (usually port `25` or `587`) using the `STARTTLS` command.
	- This is done _after_ the initial `EHLO` (see [[#Connection establishment and authentication]]).
	- **Encryption is optional unless enforced.**

> [!note] `STARTTLS` is _opportunistic_ — it upgrades to TLS if the server supports it, but it does not enforce it. 

- **Implicit TLS (SMTPS, port `465`)**
	- TLS is established *immediately* upon connection (usually using a dedicated port, `465`); no plaintext phase at all.
	- Defined in [`RFC 8314`](https://datatracker.ietf.org/doc/html/rfc8314); was originally deprecated in favor of `STARTTLS`, though it remains supported by many providers for compatibility.
### Connection establishment and authentication


1. **Connection establishment**
	- The client opens a TCP connection to the server (on port `587`, `25`, or `465`).
	- The server responds with a `220` greeting.

```bash
220 smtp.example.com ESMTP Service Ready
```

2. **`EHLO`/`HELO`**
	- The client sends `EHLO` (or `HELO` for legacy servers) to identify itself and request server capabilities. 
	- The server responds with `250` and lists supported extensions (e.g., `AUTH`, `STARTTLS`).

```bash
EHLO client.example.com
250-smtp.example.com greets client.example.com
250-STARTTLS
250-AUTH LOGIN PLAIN CRAM-MD5
250 SIZE 10485760
```

3. **`STARTTLS`** (if supported)
	- If `STARTTLS` is listed, the client sends the `STARTTLS` command to establish a TLS connection.
	- The server responds with `220`, and both sides perform a TLS handshake.
	- Once encrypted, the client sends another `EHLO` to re-negotiate the session capabilities over the secure channel —  the extension list may differ (some extensions are only advertised post-TLS).

```bash
STARTTLS
220 Ready to start TLS
```

>[!tip]+
> - Interact with SMTP over TLS manually:
> 
> ```bash
> openssl s_client -connect example.com:587 -starttls smtp
> ```
> 
> - Or for implicit TLS (port `465`):
> 
> ```bash
> openssl s_client -connect example.com:465 -crlf -quiet
> ```

4. **`AUTH`**
	- After establishing a connection and optionally upgrading to TLS, the client can authenticate using the `AUTH` command followed by a authentication exchange for the selected mechanism. These mechanisms are defined by **SASL**.
	- The server responds with `235` if the authentication was successful, or an error code if failed.

>**SMTP SASL (Simple Authentication and Security Layer)** is a framework defined in [`RFC 4954`](https://www.rfc-editor.org/rfc/rfc4954) that enables SMTP clients to authenticate with a server using  various mechanisms such as `PLAIN`, `LOGIN`, `CRAM-MD5`, or `GSSAPI`.

>[!note] See [`Simple AUthentication and Security Layer (SASL) Mechanisms — IANA`](https://www.iana.org/assignments/sasl-mechanisms/sasl-mechanisms.xhtml).

- Common `AUTH` mechanisms:

| Mechanism                                            | Description                                                                                                                                                                                                   |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`PLAIN`](https://www.rfc-editor.org/rfc/rfc4616)    | Username and password; <br>The client encodes  `username\0username\0password` as a single Base64 string.<br>Plaintext; dangerous without TLS.                                                                 |
| `LOGIN`                                              | Username and password;<br>The client sends username and password as in two steps, as separate Base64-encoded strings.<br>Plaintext; dangerous without TLS (same as `PLAIN`).<br>Obsolete in favor of `PLAIN`. |
| [`CRAM-MD5`](https://en.wikipedia.org/wiki/CRAM-MD5) | Challenge-response authentication: server sends a nonce, client hashes it with the password using [HMAC-MD5](https://en.wikipedia.org/wiki/HMAC).<br>Obsolete.                                                |
| `OAUTH2`                                             | Token-based authentication; used by major providers like Gmail, Outlook, etc.<br>Strong.                                                                                                                      |
| `GSSAPI`                                             | Uses the [Generic Security Service API (GSSAPI)](https://en.wikipedia.org/wiki/Generic_Security_Services_Application_Programming_Interface) API to enable **Kerberos-based login**.<br>Secure.                |

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

After the negotiation and authentication phase is completed, the client can proceed to submitting the email message or sending other commands, and then terminate the session.

### SMTP commands

>SMTP operates as a line-oriented, request-response protocol. The client sends **text commands** and the server replies with numeric status codes. 

| **Command** | When sent                       | **Description**                                                                                                                                        |
| ----------- | ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `EHLO`      | After connection establishment. | Extended hello — identifies the client and requests the server's supported extensions.                                                                 |
| `HELO`      | After connection establishment. | Legacy hello — identifies the client for basic SMTP (no extensions).                                                                                   |
| `STARTTLS`  | After `EHLO`.                   | Upgrades the connection to TLS (Opportunistic TLS).                                                                                                    |
| `AUTH`      | After `EHLO`/`STARTTLS`.        | Initiates authentication using a specified [SASL](https://datatracker.ietf.org/doc/html/rfc4422) mechanism (e.g., `PLAIN`, `LOGIN`, `CRAM-MD5`, etc.). |
| `VRFY`      | After `EHLO`.                   | Verifies  if a mailbox exists on the server; used for user enumeration.                                                                                |
| `EXPN`      | After `EHLO`.                   | Expands a mailing list alias to reveal individual addresses; used for enumeration.                                                                     |
| `HELP`      | Anytime.                        | Requests list of supported commands from the server.                                                                                                   |
| `NOOP`      | Anytime.                        | No operation. Keeps the connection alive and checks server responsiveness; prevents disconnection due to timeout.                                      |
| `QUIT`      | End of session.                 | Gracefully terminates session; server closes the connection.                                                                                           |

- Mail transaction:

| **Command** | When sent                   | **Description**                                                                                                          |
| ----------- | --------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `MAIL FROM` | After `AUTH`/`EHLO`.        | Begins mail transaction, sets envelope sender.                                                                           |
| `RCPT TO`   | After `MAIL FROM`.          | Sets one recipient per command; repeated for multiple recipients.                                                        |
| `DATA`      | After `RCPT TO`.            | Signals start of message content. Body ends with a single `.` on its own line.                                           |
| `RSET`      | Anytime during transaction. | Resets current mail transaction (clears sender/recipient state). Keeps connection alive.<br>The connection is kept open. |

### SMTP response codes

| Code  | Description                                                                                      |
| ----- | ------------------------------------------------------------------------------------------------ |
| `220` | Service ready;<br>Server is up and accepting connections.                                        |
| `235` | Authentication successful — valid credentials accepted.                                          |
| `250` | Command `OK` — generic success.                                                                  |
| `251` | User not local; forwarding — valid user, but relayed elsewhere.                                  |
| `252` | Cannot verify, but will attempt delivery. This means the user _may_ exist; server won't confirm. |
| `334` | Auth challenge — waiting for client's Base64-encoded credential.                                 |
| `354` | Start input — server ready to receive message body.                                              |
| `421` | Service unavailable — server is closing; try again later.                                        |
| `450` | Mailbox unavailable (temporary) — temporary failure; retry is appropriate.                       |
| `550` | Mailbox unavailable (permanent) — user doesn't exist, or relay denied.                           |
| `551` | User not local; relay rejected.                                                                  |
| `552` | Exceeded storage (quota exceeded).                                                               |
| `553` | Mailbox name invalid (malformed address).                                                        |

> [!note] During user enumeration, `250`, `251`, and `252` all indicate the user _may_ exist. `550` and `553` are the clearest "nope." Pay attention to how the server responds — different servers handle this differently.
## SMTP attack surface

- **Information leak**
	- SMTP servers are chatty by default. Even before authentication, a single `EHLO` exchange can reveal:
		- **Hostnames** — internal FQDNs from banners or `Received:` headers
		- **Software and version** — Postfix, Exim, Sendmail, Exchange (worth looking up for CVEs).
		- Supported `AUTH` mechanisms.
		- **Valid usernames** — via `VRFY`/`EXPN` if not disabled.
		- **Relay permissions** — whether the server acts as an open relay.
		- **Internal routing** — visible in mail headers (`Received:` chain).

- **Open relay attacks**
	- An open SMTP relay is an SMTP server configured to accept and forward email from any sender to any recipient without authentication.
	- This is a critical misconfiguration. It means anyone can use the server to send mail as *anyone* (you name it: spam, spoofing, phishing, etc.). IP addresses of such servers are often blacklisted.

- **SNMP injection**
	- SMTP injection is a vulnerability that unintentionally allows user-supplied data to break out of the intended email fields and inject raw SMTP commands into the conversation between the application and the mail server.
	- The vulnerability is usually caused by insufficient user input validation (`\r\n`), and often allows an attacker to manipulate the envelope sender or recipients (spoofing), add arbitrary headers, modify headers, etc. 

- **SNMP spoofing**
	- Without email authentication records (`SPF`, `DKIM`, `DMARC`), the `MAIL FROM` and `From:` headers are completely arbitrary. An attacker can send mail claiming to be anyone.

> [!note] **`SPF`**, **`DKIM`**, and **`DMARC`** are the three DNS-based mechanisms designed to prevent email spoofing. 
> - `SPF` validates the sending IP address against a list of authorized IP addresses for the domain. 
> - `DKIM` validates a cryptographic signature in the email headers. 
> - `DMARC` ties both together and tells receivers what to do on failure (reject, quarantine, report).

- **SMTP smuggling**
	- SMTP smuggling exploits discrepancies in how different SMTP implementations parse the end-of-data sequence (`<CR><LF>.<CR><LF>`), allowing an attacker to "smuggle" a second, hidden image message within the body of a single legitimate message (somewhat similar to HTTP request smuggling).
	- This is a newer and particularly nasty class of vulnerability. It was publicized in late 2023 and affects multiple major SMTP implementations.

- **Brute-force attacks**
	- Once you've enumerated valid usernames, SMTP authentication is a viable brute-force target. Modern Postfix configurations will rate-limit or block repeated failures, but many misconfigured or legacy servers won't.

- **Downgrade attacks (`STARTTLS` stripping)**
	- If `STARTTLS` is advertised but not enforced, a MitM can remove the `STARTTLS` extension from the `250` response before it reaches the client. The client, not seeing `STARTTLS` in the list, proceeds in plaintext — and the attacker captures credentials or message content.
## Enumeration

### DNS recon (MX records)

- To find which servers handle mail for a domain, retrieve `MX` records for that domain:

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
>- `MX` records have a priority value — lower numbers = higher priority.

- Short output (just the servers):

```bash
dig +short MX example.com
```

>[!note] See [[DNS recon]].


### Banner grabbing

- Telnet:

```bash
telnet <target> 25
```

- Netcat:

```bash
nc <target> 25
```

- One-liner `EHLO`: 

```bash
echo "EHLO test" | nc <target> 25
```

- Implicit TLS on `465` (if supported):

```bash
openssl s_client -connect <target> 465 -crlf -quiet
```

- `STARTTLS` on `587`:

```bash
openssl s_client -connect example.com:587 -starttls smtp
```
### Nmap scanning

- Check default SMTP ports and run version scan:

```bash
sudo nmap -sV -p 25,465,587 <target>
```

> [!tip]+
> - Basic port scanning + version detection — in case you suspect non-standard ports (e.g., `2525`):
> 
> ```bash
> sudo nmap -sV -p- <target>
> ```

- Run all SMTP scripts:

```bash
sudo nmap <target> -p 25,465,587 --script smtp*
```

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

- Key SMTP scripts:

| Script                                                                                  | Categories                           | Description                                                                                                                                                                                                                                                                      |
| --------------------------------------------------------------------------------------- | ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`smtp-commands`](https://nmap.org/nsedoc/scripts/smtp-commands.html)                   | `default`, `discovery`, `safe`       | Attempts to use `EHLO` and `HELP` to gather the Extended commands supported by an SMTP server.                                                                                                                                                                                   |
| [`smtp-enum-users`](https://nmap.org/nsedoc/scripts/smtp-enum-users.html)               | `auth`, `external`, `intrusive`      | Attempts to enumerate users on an SMTP server by issuing the `VRFY`, `EXPN`, or `RCPT TO` commands.                                                                                                                                                                              |
| [`smtp-brute`](https://nmap.org/nsedoc/scripts/smtp-brute.html)                         | `brute`, `intrusive`                 | Performs password brute-force attack against SMTP servers using either `LOGIN`, `PLAIN`, `CRAM-MD5`, `DIGEST-MD5`, or `NTLM` authentication.                                                                                                                                     |
| [`smtp-ntlm-info`](https://nmap.org/nsedoc/scripts/smtp-ntlm-info.html)                 | `default`, `discovery`, `safe`       | Retrieves information from remote SMTP services with NTLM authentication enabled.<br>Works by sending a SMTP NTLM authentication request with null credentials, which causes the remote service to respond with a NTLMSSP message disclosing NetBIOS, DNS, and OS build version. |
| [`smtp-open-relay`](https://nmap.org/nsedoc/scripts/smtp-open-relay.html)               | `discovery`, `intrusive`, `external` | Tests for SMTP open relay vulnerability by issuing a predefined combination of SMTP commands.                                                                                                                                                                                    |
| [`smtp-strangeport`](https://nmap.org/nsedoc/scripts/smtp-strangeport.html)             | `malware`, `safe`                    | Checks if SMTP is running on a non-standard port.                                                                                                                                                                                                                                |
| [`smtp-vuln-cve2010-4344`](https://nmap.org/nsedoc/scripts/smtp-vuln-cve2010-4344.html) | `exploit`, `intrusive`, `vuln`       | Tests for the [`CVE-2010-4344`](https://nvd.nist.gov/vuln/detail/cve-2010-4344) vulnerability.                                                                                                                                                                                   |
| [`smtp-vuln-cve2011-1720`](https://nmap.org/nsedoc/scripts/smtp-vuln-cve2011-1720.html) | `intrusive`, `vuln`                  | Tests for the [`CVE-2011-1720`](https://www.postfix.org/CVE-2011-1720.html) vulnerability.                                                                                                                                                                                       |
| [`smtp-vuln-cve2011-1764`](https://nmap.org/nsedoc/scripts/smtp-vuln-cve2011-1764.html) | `intrusive`, `vuln`                  | Tests for the [`CVE-2011-1764`](https://www.cve.org/CVERecord?id=CVE-2011-1764) vulnerability.                                                                                                                                                                                   |

### User enumeration

There are three commands you can use to enumerate valid usernames and email addresses on an SMTP server:

- **`VRFY` (verify) command**
	- Used to verify whether a given mailbox exists on the server.
	- `250`, `251`, `252` response codes -> the request has been accepted, the username likely exists.
	- `550`, `553` response codes -> error; the username is invalid.

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
	- Used expand a mailing list or alias to reveal individual addresses.
	- `250` response code -> the username is successfully expanded (and is valid).
	- `550` response code -> error; the username is invalid.
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

>[!warning] To prevent user enumeration, `VRFY` and `EXPN` commands are often disabled on mail servers.

- **`RCPT TO` (receipt to) command**
	- The `RCPT TO` command is used to start sending an email to the server by specifying its recipient. It can't be disabled — it's fundamental to how email works.
	- `250` response code -> the username exists.
	- `550` response code -> error; the username is invalid.
	- If the server identifies the recipient (`250` response code), this means the user exists; otherwise (`550` response code), the user is invalid.

>[!important] Unlike `VRFY` and `EXPN`, **`RCTP TO` can't be disabled**. It's required for normal email operation.

- You can automate user enumeration using the [`smtp-user-enum`](https://pentestmonkey.net/tools/user-enumeration/smtp-user-enum) script ([`GitHub`](https://github.com/pentestmonkey/smtp-user-enum)):

```bash
smtp-user-enum -M RCPT -U userlist.txt -D example.com -t <target>
```

| Option | Description                                                                          |
| ------ | ------------------------------------------------------------------------------------ |
| `-M`   | Method to use for username enumeration: `EXPN`, `VRFY`, or `RCPT` (default: `VRFY`). |
| `-u`   | User to check on the target server.                                                  |
| `-D`   | Domain to append to the username checked (default: none).                            |
| `-U`   | File with a list of usernames to check.                                              |
| `-t`   | Target SMTP server.                                                                  |
| `-T`   | File with a list of target SMTP servers.                                             |
| `-p`   | TCP port number on which the SMTP service runs (default: `25`).                      |
| `-m`   | Maximum number of processes (default: `5`).                                          |

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
<target>
```

## Brute-forcing credentials

Once you have a valid username list, you can brute-force SMTP passwords:

- Medusa: 

```bash
medusa -M smtp -h <target> -u user@example.com -P /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt -n 587 -e ns
```

>[!note]+ Option breakdown
>- `-M`: Medusa mode (protocol).
>- `-h`: Target host.
>- `-n`: Target port.
>- `-u`: Username to test (`-U` to brute-force usernames, too).
>- `-P`: Password wordlist.
>- `-e n`: Check for empty passwords.
>- `-e s`: Check for passwords matching the username. 

- Hydra:

```bash
hydra -l user@example.com -P /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt smtp://<target>
```


- Non-standard port:

```bash
hydra -l user@example.com -P /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt smtp://<target>:2525
```

```bash
hydra -L usernames.txt -P passwords.txt -s 2525 <target> smtp
```

- Nmap [`smtp-brute`](https://nmap.org/nsedoc/scripts/smtp-brute.html):

```bash
nmap -p 25 --script smtp-brute \
  --script-args userdb=users.txt,passdb=passwords.txt \
  example.com
```

>[!note] SMTP servers commonly rate-limit or temporarily block IP addresses after repeated failed authentication attempts. Start with `-t 3` or `-t 5` in Hydra and adjust. Watch for `421 Too many connections` or `535 Authentication failed` becoming increasingly delayed — these indicate rate-limiting.

>[!note] See [[Password wordlists and default credentials]].
## Sending emails from the command-line

### swaks 

>[`swaks`](https://github.com/jetmore/swaks) (Swiss Army Knife for SMTP) is purpose-built for SMTP testing. It supports TLS, different authentication methods, attachments, and custom headers.

- Send a test email:

```bash
swaks --to victim@example.com --from sender@attacker.com --server example.com
```

- With authentication:

```bash
swaks --to victim@example.comm \
      --from user@example.com \
      --auth-user user@example.com \
      --auth-password 'passwd' \
      --server example.com --port 587
```

- With TLS:

```bash
swaks --to victim@example.com \
      --from sender@example.com \
      --server example.com --port 587 \
      --tls \
      --auth-user user@example.com \
      --auth-password 'passwd'
```

- Spoofed phishing email with custom headers:

```bash
swaks --to victim@example.com \
      --from ceo@example.com \
      --header "Subject: Urgent: Action Required" \
      --header "Reply-To: attacker@evil.com" \
      --body "Please review the attached document and respond by EOD." \
      --server mail.example.com
```

- With an attachment:

```bash
swaks --to victim@example.com \
      --from sender@attacker.com \
      --attach /path/to/payload.pdf \
      --server example.com
```

- Testing for open relay:

```bash
swaks --to external@gmail.com \
      --from external@yahoo.com \
      --server example.com --port 25
```

### sendemail

- Basic send:

```bash
sendemail -f sender@attacker.com \
          -t victim@target.com \
          -u "Subject Here" \
          -m "Message body" \
          -s target.com:25
```


- With authentication:

```bash
sendemail -f user@target.com \
          -t victim@target.com \
          -u "Quarterly Report" \
          -m "Please find the report attached." \
          -s target.com:587 \
          -xu user@target.com \
          -xp 'passwd'
```
## References and further reading

- [`Simple Mail Transfer Protocol — Wikipedia`](https://en.wikipedia.org/wiki/Simple_Mail_Transfer_Protocol)
- [`Simple Mail Transfer Protocol — RFC 5321`]([`RFC 5321`](https://www.rfc-editor.org/rfc/rfc5321))
- [`Internet Message Format — RFC 5322`](https://datatracker.ietf.org/doc/html/rfc5322)
- [`SMTP Service Extension for Authentication — RFC 4954`](https://datatracker.ietf.org/doc/html/rfc4954)
- [`Simple Authentication and Security Layer (SASL) — RFC 4422`](https://datatracker.ietf.org/doc/html/rfc4422)

- [`Opportunistic TLS — Wikipedia`](https://en.wikipedia.org/wiki/Opportunistic_TLS)
- [`Internet Message Access Protocol — Wikipedia`](https://en.wikipedia.org/wiki/Internet_Message_Access_Protocol)
- [`Post Office Protocol — Wikipedia`](https://en.wikipedia.org/wiki/Post_Office_Protocol)
- [`Introduction to IMAP — nickb.dev`](https://nickb.dev/blog/introduction-to-imap/)
- [`SMTP Authentication — Wikipedia`](https://en.wikipedia.org/wiki/SMTP_Authentication)
- [`Simple AUthentication and Security Layer (SASL) Mechanisms — IANA`](https://www.iana.org/assignments/sasl-mechanisms/sasl-mechanisms.xhtml)

- [`4 ways to SMTP Enumeration — Hacking Articles`](https://www.hackingarticles.in/4-ways-smtp-enumeration/)
- [`smtp-user-enum — pentestmonkey`](https://pentestmonkey.net/tools/user-enumeration/smtp-user-enum)


- [`SMTP (Simple Message Transfer Protocol — Hackviser`](https://hackviser.com/tactics/pentesting/services/smtp)


To be done: 
- Information gathering on a compromised email server