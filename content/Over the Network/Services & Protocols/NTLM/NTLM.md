---
created: 22-02-2026
tags:
  - Windows
  - network_services
---
## NTLM


> **[NTLM (NT LAN Manager)](https://learn.microsoft.com/en-us/windows-server/security/kerberos/ntlm-overview)** is a suite of Microsoft challenge-response authentication protocols that provides authentication, message integrity, and confidentiality in Windows networks.

>[!note] "NT" refers to Windows NT.

> [!note] NTLM evolved from the older **[LAN Manager (LANMAN)](https://en.wikipedia.org/wiki/LAN_Manager)** authentication protocol.

- Today, NTLM is considered a legacy protocol and has largely been replaced by Kerberos, which became the default authentication mechanism with Windows 2000 and Active Directory. However, NTLM is still widely supported for backward compatibility, particularly in scenarios where Kerberos can't be used (e.g., workgroup environments, legacy systems, or misconfigured services).

- Despite its known flaws (you will see plenty of them yourself), NTLM remains common — even in modern enterprise networks.

---

- NTLM is not tied to a specific transport protocol. Instead, it acts as a *negotiated authentication mechanism* embedded within various application protocols, including:
	- **[[SMB]]** — file shares, named pipes, and common lateral movement paths.
	- **HTTP/HTTPS** — IIS applications, Outlook Web Access (OWA), ADCS web enrollment.
	- **LDAP/LDAPS** — directory queries, domain enumeration.
	- **[[WinRM]]** — remote PowerShell access (e.g., `Evil-WinRM`).
	- **[[🛠️ MSSQL]]** — database authentication over named pipes/TCP.
	- **RPC/DCOM** — remote procedure calls and distributed component communication.

- Each of these protocols encapsulates the same underlying NTLM challenge-response exchange (Negotiate → Challenge → Authenticate). The transport changes, but the authentication flow remains the same.
- That's why tools like `Responder` can capture NTLMv2 challenge-response data across multiple protocols simultaneously, like SMB, HTTP, LDAP — only the wrapper changes. 

## NT hash

> **NT hash** is a fixed-length, unsalted cryptographic digest of a user's plaintext password, computed by encoding the password as UTF-16 Little Endian and hashing the resulting byte sequence with MD4, producing a 128-bit (16-byte) value.

The NT hash is derived as follows:

```
NT hash = MD4( UTF-16LE(password) )
```

1. The user's password is taken as-is.
2. Encode every character as 2 bytes in little-endian order ([UTF‑16LE](https://en.wikipedia.org/wiki/UTF-16#Byte-order_encoding_schemes)).
3. Hash the byte sequence [MD4](https://en.wikipedia.org/wiki/MD4).

The result is a 128-bit (16-byte) strings (32 hex characters) — this is the NT hash.

>[!bug] NT hashes are not salted.

The NT hash is stored in:
- **SAM database** (`C:\Windows\System32\config\SAM`) — local accounts.
- **`NTDS.dit`** (`C:\Windows\NTDS\NTDS.dit`) — domain accounts on the DC.
- **LSASS process memory** — cached in-memory for active sessions.

>[!important]+ **NTLM never transmits the password, or the NT hash, over the wire.**
> - The NT hash is used as key material to produce a _response_ to a _challenge_.
> - If you know the hash, you can authenticate as the user without knowing the plaintext password — this is the basis of **[[🛠️ Pass-the-Hash]]**.

>[!note] The NT hash is often incorrectly called "NTLM hash"; it's best to use call it **NT hash** to avoid confusion with network challenge responses.

>[!note] See [[cracking Windows hashes_#NT hashes]].

>[!note]- LM hash 
>An **LM hash** (LM stands for [LAN Manager](https://en.wikipedia.org/wiki/LAN_Manager#Password_hashing_algorithm)) is an ancient legacy format now mostly disabled by default. 
>It is generated as follows:
> 
> 1. The password is converted to uppercase and encoded in the System OEM [code page](https://en.wikipedia.org/wiki/Code_page).
> 2. It's **`NULL`-padded or truncated to 14 bytes** (characters beyond 14 are ignored).
> 3. This 14-byte character sequence is split into two **7-byte halves**.
> 4. These values are used to create two 8-byte [DES](https://en.wikipedia.org/wiki/Data_Encryption_Standard "Data Encryption Standard") keys. The seven bytes are converted into a bit stream ([MSb](https://en.wikipedia.org/wiki/Bit_numbering#Most_significant_bit) first), and a [parity bit](https://en.wikipedia.org/wiki/Parity_bit) is inserted each 7 bits.
> 5. Each of the two keys is used to DES-encrypt the **constant ASCII string** — `KGS!@#$%`. This results in two 8-byte ciphertext values. 
> 6. These two ciphertext values are concatenated to form a 16-byte value, which is the LM hash.
> 
> This is fundamentally weak because DES itself is weak and not salted, and to add to this, uppercasing and truncation reduce password entropy. 
> 
> For modern Windows **LM hashes are usually disabled by default** (Vista/Server 2008 onward), and if a password is **≥15 characters**, no LM hash is generated at all.
>
>See [[cracking Windows hashes_#LM hashes]].

## SSPI and the SSP model

- In Windows, authentication protocols such as NTLM and Kerberos are **not implemented directly by applications**. Instead, they are abstracted behind a common API layer:

>**[SSPI (Security Support Provider Interface)](https://learn.microsoft.com/en-us/windows/win32/rpc/sspi-architectural-overview)** is a Windows API that provides a **uniform interface for authentication and secure communication**, allowing applications to perform authentication, integrity, and confidentiality operations without implementing protocol-specific logic.

>**[SSP (Security Support Provider)](https://learn.microsoft.com/en-us/windows/win32/rpc/security-support-providers-ssps-)** is a DLL-based module that implements a specific authentication protocol. SSPs are loaded by SSPI at runtime and perform the actual authentication operations (e.g., NTLM or Kerberos exchanges) on behalf of the application.

>[!tip]+
> - **SSPI = abstraction layer (API).**
> - **SSP = protocol implementation (plugin).**

- Windows ships with multiple SSPs, including:
    - **NTLM SSP** — implemented in `msv1_0.dll`
    - **Kerberos SSP** — implemented in `kerberos.dll`
    - **Negotiate SSP** — selects Kerberos or NTLM automatically
- The NTLM SSP (`%Windir%\System32\msv1_0.dll`) implements the NTLM and NTLMv2 protocols and is used whenever NTLM authentication is negotiated through SSPI.

> [!example]+ SMB authentication flow via SSPI  
> When an SMB client authenticates to a remote server:
> 
> 1. The SMB client invokes SSPI functions such as `AcquireCredentialsHandle` and `InitializeSecurityContext`.
> 2. SSPI selects an appropriate SSP:
> 	- If Kerberos is available → `kerberos.dll`.
> 	- Otherwise → `msv1_0.dll` (NTLM SSP).
> 3. The selected SSP generates and processes authentication tokens (e.g., NTLM Negotiate/Challenge/Authenticate messages).
> 4. These tokens are passed back to the application and transmitted over the network within the SMB protocol.

>[!tip]+
>Applications call SSPI → SSPI routes the request to an SSP.

This design means that applications do not need to implement NTLM/Kerberos logic themselves — new authentication mechanisms can be added as SSPs without modifying the code much. Additionally, mechanisms like _Negotiate SSP_ can transparently select the strongest available protocol.

>[!note] Many different services (SMB, HTTP, WinRM, etc.) ultimately invoke the **same SSPI → SSP pipeline**, which explains why NTLM authentication can be triggered and captured across multiple protocols using the same techniques.
## NTLM message structure

The NTLM authentication protocol uses three message types during authentication and one message type for optional message integrity checks after authentication:

| Message                                                                                                                                   | `MessageType` | Direction       | Purpose                              |
| ----------------------------------------------------------------------------------------------------------------------------------------- | ------------- | --------------- | ------------------------------------ |
| [`NEGOTIATE_MESSAGE`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/b34032e5-3aae-4bc6-84c3-c6d80eadf7f2)         | `0x00000001`  | Client → Server | Advertise capabilities.              |
| [`CHALLENGE_MESSAGE`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/801a4681-8809-4be9-ab0d-61dcfe762786)         | `0x00000002`  | Server → Client | Issue nonce.                         |
| [`AUTHENTICATE_MESSAGE`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/033d32cc-88f9-4483-9bf2-b273055038ce)      | `0x00000003`  | Client → Server | Prove identity.                      |
| [`NTLMSSP_MESSAGE_SIGNATURE`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/b192b940-a508-4329-8513-efb3342f2c85) | —             | Both            | Message integrity (signing/sealing). |

>[!note] See [`Message Syntax — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/907f519d-6217-45b1-b421-dca10fc8af0d).

- Messages are *variable-lengths*: a fixed-length leader + a variable-length payload. 
- The header always starts with `Signature` and `MessageType` fields.
- Message structure is as follows:



![Source: `academy.hackthebox.com`](https://academy.hackthebox.com/storage/modules/232/NTLM_Message_Fields.png)

- `Signature` (8 bytes)
	- Always set to the ASCII string `NTLMSSP\0`.
- `MessageType` (4 bytes)
	- An integer that indicates the NTLM message type; one of the three values above:
		- `0x00000001` — `NEGOTIATE_MESSAGE`
		- `0x00000002` — `CHALLENGE_MESSAGE`
		- `0x00000003` — `AUTHENTICATE_MESSAGE`
 - `MessageDependentFieldbs` (variable-length)
	 - The actual NTLM message content, specific to each message type.
- `payload` (variable-length)
	- Additional data referenced by byte offset from the header fields (`MessageDependentFields`).

>[!note] When you see a Base64-encoded blob in an HTTP `Authorization: NTLM <blob>` header, that blob decodes to one of these message structures. The first 8 bytes will always be `4E544C4D53535000` — `NTLMSSP\0` in hex.

## Authentication flow — the three-way handshake

>[!important] NTLM version to use (NTLMv1 or NTLMv2) [configured out-of-band](https://learn.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/network-security-lan-manager-authentication-level) before authentication, not during the handshake.

NTLM authentication flows looks like this:

1. **[`NEGOTIATE_MESSAGE`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/b34032e5-3aae-4bc6-84c3-c6d80eadf7f2)** (Type 1 message) Client -> Server
	- The client sends a `NEGOTIAGE_MESSAGE` to start NTLM authentication and advertise its capabilities. 
	- Negotiate flags (`NegotiateFlags` bitmask) indicate what the client supports (e.g., extended session security, NTLMv2, request for target name, Unicode support, message signing, sealing, etc.).
	- `DomainNameFields` / `WorkstationFields` fields are optional; the client may include its domain and workstation name.

At this point, no credential or challenge has yet been presented.

2. **[`CHALLENGE_MESSAGE`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/801a4681-8809-4be9-ab0d-61dcfe762786)** (Type 2 message) Server -> Client
	- The server responds with a `CHALLENGE_MESSAGE`.
	- Negotiate flags (`NegotiateFlags` bitmask) indicate the server-supported capabilities intersected with what the client advertised. 
	- `ServerChallenge` is an 8-byte cryptographically random **nonce** generated fresh for this session (**Server Challenge**). Its purpose is to ensure that the subsequent response from the client **can't be replayed across sessions without recomputation**.
	- `TargetName` is the server's domain or machine name. 
	- `TargetInfo` (NTLMv2 only) is a structured list of attribute-value pairs (`MsvAvNbDomainName`, `MsvAvDnsDomainName`, `MsvAvTimestamp`, etc.) that bind the authentication to the server's identity.

> [!note] The `TargetInfo` block in NTLMv2 is security-relevant beyond just identification. It's incorporated into the response computation, cryptographically binding the response to the server's advertised identity. This is what Extended Protection for Authentication (EPA) leverages to prevent relay across different servers.

3. **[`AUTHENTICATE_MESSAGE`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/033d32cc-88f9-4483-9bf2-b273055038ce)** (Type 3 message) Client -> Sever
	- After receiving the challenge, the client computes a challenge response and constructs an `AUTHENTICATE_MESSAGE`.
	- `NtChallengeResponse` is the computed challenge response (the core proof of identity). Its exact structure depends on whether NTLMv1 or NTLMv2 is in use.
	- `LmChallengeResponse` is legacy LM response (usually present for backward compatibility, often a null or weaker response in modern configs).
	- `DomainName` / `UserName` / `Workstation` are cleartext identity metadata sent alongside the response.
	- `EncryptedRandomSessionKey` is optional; it's used to establish session keys for signing/sealing.

The password is never transmitted. The NT hash is never transmitted. Only a _value derived from them_, in combination with the server's challenge, is sent. The server (or domain controller) verifies by recomputing the expected response from its stored copy of the NT hash.

>[!note] For the full list of `NegotiateFlags` and their possible values, see [`NEGOTIATE — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/99d90ff4-957f-4c8a-80e4-5bfe5a9a9832).

## NTLMv1 and NTLMv2

The NTLM protocol exists in two primary variants:
- **NTLMv1**
- **NTLMv2**
Both follow the same **challenge–response authentication model**, but differ significantly in how the response is computed and what inputs are included.

- **NTLMv1** → DES-based construction over the NT hash.
- **NTLMv2** → HMAC-MD5-based construction with additional context (identity, nonce, timestamp).

>[!important] The NTLM version used is **not negotiated during the handshake**, but [configured out-of-band](https://learn.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/network-security-lan-manager-authentication-level) before authentication. Both parties must run compatible versions. 
### NTLMv1

>**NTLMv1** is the original NTLM challenge-response variant. It computes the authentication response by DES-encrypting the server's 8-byte challenge using three keys derived from the NT hash, and concatenating the results into a 24-byte response.

Given the 8-byte `ServerChallenge` from `CHALLENGE_MESSAGE`:

1. Take the 16-byte NT hash and **pad it to 21 bytes** (append 5 null bytes).
2. Split the 21 bytes into **three 7-byte blocks**.
3. Expand each 7-byte block into an 8-byte DES key (insert [parity bits](https://en.wikipedia.org/wiki/Parity_bit) every 7 bits).
4. Encrypt the server challenge with each DES key independently to produce three 8-byte ciphertext values.
5. Concatenate the values into a **24-byte `NTLMv1Response`**.

The above scheme can be written as follows (taken from [Wikipedia](https://en.wikipedia.org/wiki/NTLM#NTLMv1)):

```
C = 8-byte server challenge, random
K1 | K2 | K3 = LM/NT-hash | 5-bytes-0
response = DES(K1,C) | DES(K2,C) | DES(K3,C)
```

This design is fundamentally flawed:

- **DES is weak** — NTLMv1 hashes can be cracked to NT hashes in under 30 seconds using rainbow attacks. 
- **No client randomness** — The same password + same challenge = same response, every time. 
	- If an attacker can reuse or control the server challenge (which in some attack scenarios they can), responses become predictable.
	- Other than that, rainbow tables work directly.
- **Each DES key is independent** — The three keys can be attacked separately.
	- The third key is derived from only 2 bytes of the NT hash (the 5-byte padding means only 2 actual bytes end up in the third block) — meaning the third DES key space is only 65,536 possibilities.

>[!example]+ 
> A captured NTLMv1 hash looks like this in `Responder` output:
> ```shell-session
> [SMB] NTLMv1 Client   : 172.19.117.36
> [SMB] NTLMv1 Username : Support1
> [SMB] NTLMv1 Hash     : Support1::WIN-OLMHXGAP0V2:e2dL3196O8f55fB6:Q49S19A2937J6XC3CKA418EI4958OHB9:xF2K324O5L6Q7V8C
> ```
> The format is `username::domain:LMResponse:NTResponse:ServerChallenge`. You can feed NTLMv1 hashes directly to Hashcat (`-m 5500`).

>[!note] [[cracking Windows hashes_]].

### NTLMv2

> **NTLMv2** is the improved NTLM variant that computes authentication using [HMAC](https://en.wikipedia.org/wiki/HMAC)-[MD5](https://en.wikipedia.org/wiki/MD5) over a structured, per-session message. It binds the response to the user’s identity and includes both server and client nonces + a timestamp.

NTLMv2 fixes NTLMv1's core weaknesses by introducing client entropy and cryptographic binding to identity context. Here's the full computation:

1. **Derive the NTLMv2 hash (v2 key)**
	- The NT hash is used as the HMAC key, and the username (uppercase) + domain is the message. 
	
```
NTLMv2_hash = HMAC-MD5(NT_hash, UTF-16LE(uppercase(username) + domain))
```

2. **Construct the blob (`NTLMv2_CLIENT_CHALLENGE`)**
	- The client build a structured blob:
		- Version fields (`RespType` / `HiRespType`).
		- `Timestamp` (NT time format).
		- `ClientChallenge` (8 random bytes generated by the client).
		- `TargetInfo` (AV pairs) from the `CHALLENGE_MESSAGE` (copied verbatim).
		- Terminator.

```
Blob = [ 
	Version Info |
    Timestamp    |
    ClientNonce  |
    AV_PAIRS     |
    Terminator
]
```

>[!note] This blob is what differentiates NTLMv2 responses from each other — it ensures every authentication attempt is unique.

3. **Compute the proof (`NTProofStr`)**
	- The NTLMv2 hash is again used as the HMAC key. The data is the server's 8-byte challenge concatenated with the full blob. This produces a 16-byte digest — the core proof.

```
NTProofStr = HMAC-MD5(NTLMv2_hash, ServerChallenge + Blob)
```

4. **Final Response**

```
NTLMv2_Response = NTProofStr + Blob
```

The above scheme can be written as follows (taken from [Wikipedia](https://en.wikipedia.org/wiki/NTLM#NTLMv2)):

```
SC = 8-byte server challenge, random
CC = 8-byte client challenge, random
CC* = (X, time, CC2, domain name)
v2-Hash = HMAC-MD5(NT-Hash, user name, domain name)
LMv2 = HMAC-MD5(v2-Hash, SC, CC)
NTv2 = HMAC-MD5(v2-Hash, SC, CC*)
response = LMv2 | CC | NTv2 | CC*
```

Verification (server-side):
1. Retrieve the user’s NT hash.
2. Recompute `NTLMv2_hash` using the same identity context.
3. Recompute `NTProofStr` using its own challenge and the received blob.
4. Compare the recomputed `NTProofStr` to the received one.

>[!example]+
> A captured NTLMv2 hash looks like this:
> 
> ```
> [SMB] NTLMv2-SSP Client   : 172.19.117.55
> [SMB] NTLMv2-SSP Username : INLANEFREIGHT\Support2
> [SMB] NTLMv2-SSP Hash     : Support2::INLANEFREIGHT:e2d2339638fc5fd6:D4979A923DD76BC3CFA418E94958E2B0:010100000000000000E0550D97CCD901509F9CE743AB58760000000002000800...
> ```
> 
Format: `username::domain:ServerChallenge:NTProofStr:Blob`.

>[!note] NTLMv2 hashes can be cracked offline using tools like Hashcat (`-m 5600`). However, rainbow tables won't work since each response is unique.

## Pass-though vs. Workgroup authentication

How the server actually _verifies_ the response depends on the environment. NTLM authentication can be **pass-through** or **local**:

- **Pass-through authentication — Domain environments**
	- In an AD environment, the server forwards the client's challenge response (`NtChallengeResponse` from `AUTHENTICATE_MESSAGE`) along with `ServerChallenge` to a DC for verification (usually via `Netlogon`).
	- The DC retrieves the NT hash from `NTDS.dit`, recomputes the expected response, and returns success or failure.
	- The server then grants or denies access based on the DC's verdict.


>[!important] In pass-through authentication, the intermediate server never sees the NT hash; it acts as a relay between the client and the DC.

>[!note] See [[🛠️ NTLM relay]].

![Source: `academy.hackthebox.com`](https://academy.hackthebox.com/storage/modules/232/Domain-joined_Computers_NTLM_Authentication.png)

- **Local authentication — Workgroup / standalone environments**
	- In a *non-domain (peer-to-peer)* environment, the server validates the response itself using its local **SAM database**. The SAM stores NT hashes for local accounts, so the server can perform the verification independently; no DC involved.

![Source: `academy.hackthebox.com`](https://academy.hackthebox.com/storage/modules/232/Workgroup_Computers_NTLM_Authentication.png)
## NTLM session security

Once NTLM authentication completes, `NegotiateFlags` from `NEGOTIATE_MESSAGE` (Type 1) and `CHALLENGE_MESSAGE` (Type 2) determine whether the session uses **signing** and/or **sealing** for ongoing communication.
### Message signing

>**[Message signing](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/131b0062-7958-460e-bca5-c7a9f9086652)**, or **session signing**, applies a digital signature to each transmitted message, computed from the message content and a **session key** derived from the authentication exchange. It provides integrity verification, protecting against tampering and [[🛠️ NTLM relay|relay]].

- Messages are signed with a **session key**:
	- In NTLMv1, the session key is calculated as MD4 of the NT hash.
	- In NTLMv2, the session key is calculated as a HMAC-MD5 of the NT hash + Server Challenge + Client Challenge.

>[!important] A session key is never transmitted on the wire, but computed independently by client and server independently.

- Once the session key is established, a **[MAC (Message Authentication Code)](https://en.wikipedia.org/wiki/Message_authentication_code)** is added to each message message exchanged between the client and the server.
- A MAC is computed by applying a cryptographic algorithm to the message and session key. The receiver can verify message integrity by applying the same MAC algorithm to the message and the session key and comparing the result with the MAC sent in the message. If they're the same — message wasn't tampered with, otherwise it was modified or corrupted during transmission.
- Even if someone is eavesdropping, they can't simply capture and modify NTLM messages without knowing the session key. 
### Message sealing

>**[Message sealing](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/115f9c7d-bc30-4262-ae96-254555c14ea6)**, or **session sealing**, encrypts content of messages exchanged between a client and a server using **symmetric-key encryption**. It provides message confidentiality. 

>[!important] Sealing always implies signing — every sealed message is also signed (but not vice versa).

- [RC4](https://en.wikipedia.org/wiki/RC4) is used as an encryption algorithm (considered insecure today).


>[!warning] NTLMv1 doesn't support message sealing. Only NTLMv2 does.

## References and further reading

- NTLM:
	- [`NTLM overview — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/security/kerberos/ntlm-overview)
	- [`NTLM user authentication — Microsoft Learn`](https://learn.microsoft.com/en-us/windows-server/security/kerberos/ntlm-overview)
	- [`NTLM — Wikipedia`](https://en.wikipedia.org/wiki/NTLM)
	- [`The NTLM Authentication Protocol and Security Support Provider — davenport.sourceforge.net`](https://davenport.sourceforge.net/ntlm.html)
- NTLM negotiation process and messages:
	- [`Message Syntax — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/907f519d-6217-45b1-b421-dca10fc8af0d)
	- [`NEGOTIATE_MESSAGE — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/b34032e5-3aae-4bc6-84c3-c6d80eadf7f2)
	- [`CHALLENGE_MESSAGE — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/801a4681-8809-4be9-ab0d-61dcfe762786)
	- [`AUTHENTICATE_MESSAGE — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/033d32cc-88f9-4483-9bf2-b273055038ce)
	- [`NEGOTIATE — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/99d90ff4-957f-4c8a-80e4-5bfe5a9a9832)
- Session security:
	- [`Session Security Details — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/d1c86e81-eb66-47fd-8a6f-970050121347)
	- [`Message Integrity — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/131b0062-7958-460e-bca5-c7a9f9086652)
	- [`Message Confidentiality — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/115f9c7d-bc30-4262-ae96-254555c14ea6)

- Cryptography and related:
	- [`Challenge-response authentication — Wikipedia`](https://en.wikipedia.org/wiki/Challenge%E2%80%93response_authentication)
	- [`Code page — Wikipedia`](https://en.wikipedia.org/wiki/Code_page)
	- [`Bit numbering — Wikipedia`](https://en.wikipedia.org/wiki/Bit_numbering#Most_significant_bit)
	- [`Parity bit — Wikipedia`](https://en.wikipedia.org/wiki/Parity_bit)
	- [`Data Encryption Standard — Wikipedia`](https://en.wikipedia.org/wiki/Data_Encryption_Standard)
	- [`HMAC — Wikipedia`](https://en.wikipedia.org/wiki/HMAC)
	- [`MD5 — Wikipedia`](https://en.wikipedia.org/wiki/MD5)
	- [`MD4 — Wikipedia`](https://en.wikipedia.org/wiki/MD4)
	- [`Message authentication code — Wikipedia`](https://en.wikipedia.org/wiki/Message_authentication_code)
	- [`The Basics of SMB Signing (covering both SMB1 and SMB2) — Microsoft Learn`](https://learn.microsoft.com/en-us/archive/blogs/josebda/the-basics-of-smb-signing-covering-both-smb1-and-smb2)
	- [`RC4 — Wikipedia`](https://en.wikipedia.org/wiki/RC4)
- Other:
	- [`LAN Manager — Wikipedia`](https://en.wikipedia.org/wiki/LAN_Manager)
	- [`SSPI Architectural Overview — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/rpc/sspi-architectural-overview)
	- [`Security Support Providers (SSPs) — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/rpc/security-support-providers-ssps-)
	- [`Understanding NTLM Authentication and NTLM Relay Attacks — vaadata`](https://www.vaadata.com/blog/understanding-ntlm-authentication-and-ntlm-relay-attacks/)
	- [`NTLM Authentication — Nathaniel Cyber Security`](https://docs.wehost.co.in/cybersecurity/ntlm-authentication)
	- [`Network security: LAN Manager authentication level — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/network-security-lan-manager-authentication-level)
	- [`NTLM Challenge/Response — smallsec`](https://blog.smallsec.ca/ntlm-challenge-response/)
	- [`NTLM Challenge Response is 100% Broken (Yes, this is still relevant) — Mark R. Gamache's Random Blog`](https://markgamache.blogspot.com/2013/01/ntlm-challenge-response-is-100-broken.html)


- To be done:
	- A note on connection-oriented and connectionless modes (the latter is what's discussed above)
	- EPA

