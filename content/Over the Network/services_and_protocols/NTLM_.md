---
created: 22-02-2026
tags:
  - Windows
  - network_services
---
## NTLM

>**NTLM (NT LAN Manager)** is a suite of Microsoft security protocols designed to provide authentication, integrity, and confidentiality for users in Windows networks.

>[!note] "NT" refers to Windows NT.

>[!note] NTLM is the successor to the authentication protocol in Microsoft [LAN Manager](https://en.wikipedia.org/wiki/LAN_Manager "LAN Manager") (LANMAN), an older Microsoft product.

- Today, NTLM is considered legacy and mostly replaced by Kerberos. It exists primarily for backward compatibility and in situations where Kerberos can't be used. 
- Despite its known flaws, NTLM is still commonly used to ensure compatibility with legacy clients and servers, even on modern systems.
- While Microsoft continues to support NTLM, Kerberos has taken over as the default authentication mechanism in Windows 2000 and subsequent Active Directory (AD) domains.
## NTLM authentication

>**NTLM** is a **challenge-response protocol** used primarily in Windows environments.

- The purpose of NTLM is to allow a client to prove possession of valid credentials (specifically, the NT password hash) without transmitting the password itself over the network. 
- NTLM is not a standalone protocol, but rather an authentication mechanism embedded into other protocols, like SMB, LDAP, WinRM, HTTP (NTLM over HTTP, IIS), MSSQL, RPC/DCOM, etc.

>[!note] Each NTLM protocol has two variants, connection-oriented (such as for TCP) and connectionless (like for UDP). We will primarily be talking about the former. 

>[!note]+ A note on NTLM implementation
> NTLM is best implemented as a function library that can be called by application protocols rather than as a layer in a network protocol stack.
> We have two important components of such implementations:
> 
> - [SSPI (Security Support Provider Interface)](https://learn.microsoft.com/en-us/windows/win32/rpc/sspi-architectural-overview)
> 	- The standard **Windows API** that applications use to perform authentication and establish secure communication channels without knowing protocol specifics.
> 	- Applications call SSPI functions to authenticate a user, establish a security context, and negotiate message signing or encryption.
> 
> - [SSP (Security Support Provider)](https://learn.microsoft.com/en-us/windows/win32/rpc/security-support-providers-ssps-)
> 	- Modules, DLLs (Dynamic-Link Libraries), that actually implements authentication protocols such as NTLM, Kerberos, etc.
> 	- When SSPI is invoked, it selects an appropriate SSP (e.g., `NTLMSSP`) to perform the actual authentication handshake. 
> 	- This allows any application to use NTLM or Kerberos through SSPI without embedding protocol's complexity in the application itself.
> 	- [NTLM SSP](https://learn.microsoft.com/en-us/windows-server/security/windows-authentication/security-support-provider-interface-architecture#BKMK_NTLMSSP) is located at `%Windir%\System32\msv1_0.dll`.
### NTLM messages

The NTLM authentication protocol uses three message types during authentication and one message type for optional message integrity checks after authentication:
- [`NEGOTIATE_MESSAGE`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/b34032e5-3aae-4bc6-84c3-c6d80eadf7f2) (Type 1)
- [`CHALLENGE_MESSAGE`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/801a4681-8809-4be9-ab0d-61dcfe762786) (Type 2)
- [`AUTHENTICATE_MESSAGE`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/033d32cc-88f9-4483-9bf2-b273055038ce) (Type 3)

For integrity and confidentiality, NTLM uses [`NTLMSSP_MESSAGE_SIGNATURE`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/b192b940-a508-4329-8513-efb3342f2c85).

>[!note] See [`Message Syntax — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/907f519d-6217-45b1-b421-dca10fc8af0d).

- Messages are *variable-lengths*: a fixed-length leader + a variable-length payload. 
- The header always starts with `Signature` and `MessageType` fields.
- Message structure is as follows:

![](https://academy.hackthebox.com/storage/modules/232/NTLM_Message_Fields.png)

- `Signature` (8 bytes)
	- An 8-byte character array; always set to `['N', 'T', 'L', 'M', 'S', 'S', 'P', '\0']`.
- `MessageType` (4 bytes)
	- A 4-byte integer that indicates the NTLM message type:
	- `0x00000001` (`NtLmNegotiate`) — `NEGOTIATE_MESSAGE`
	- `0x00000002` (`NtLmChallenge`) — `CHALLENGE_MESSAGE`
	- `0x00000003` (`NtLmAuthenticate`) — `AUTHENTICATE_MESSAGE`
 - `MessageDependentFieldbs` (variable-length)
	 - The NTLM message content.
- `payload` (variable-length)
	- A variable-length field that contains a message-dependent number of individual payload messages, referenced by byte offsets in `MessageDependentFields`.

### Authentication flow

>[!important] The NTLM version used on hosts, whether NTLMv1 or NTLMv2, is [configured out-of-band](https://learn.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/network-security-lan-manager-authentication-level) before authentication.

NTLM authentication  flows looks like this:

1. **[`NEGOTIATE_MESSAGE`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/b34032e5-3aae-4bc6-84c3-c6d80eadf7f2)** (Type 1 message) Client -> Server
	- The client sends a `NEGOTIAGE_MESSAGE`. 
	- The message indicates the start of NTLM authentication and advertises **capabilities and preferences** using a set of **negotiate flags (`NegotiateFlags`)**. The flags may indicate encryption requirements, encoding, support for session keys, and other security features.
	- The client may also include its domain name and workstation name (optional textual identifiers).

At this point, no credential or challenge has yet been presented.

2. **[`CHALLENGE_MESSAGE`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/801a4681-8809-4be9-ab0d-61dcfe762786)** (Type 2 message) Server -> Client
	- The server responds with a `CHALLENGE_MESSAGE`.
	- The message contains a set of **negotiate flags (`NegotiateFlags`)** that indicate which capabilities the server has elected to use based on the client's advertised capabilities, and a 8-byte **nonce** — a random challenge value generated by the server (**Server Challenge**).
	- The purpose of the server challenge is to ensure that the subsequent response from the client can't be replayed across sessions without recomputation — it is a fresh, unique value per session.
	- This message represents a challenge provided by the server to the client.

>[!note] In the NTLMv2 variant, `TargetInfo` fields include additional server or domain identifiers that bind the authentication to the intended target.

3. **[`AUTHENTICATE_MESSAGE`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/033d32cc-88f9-4483-9bf2-b273055038ce)** (Type 3 message) Client -> Sever
	- After receiving the challenge, the client computes a response and constructs an `AUTHENTICATE_MESSAGE`.
	- The message includes metadata such as the username, domain name, and optionally workstation.
	- It includes on or more cryptographic **challenge responses** — values computed based on the server's challenge (nonce) and the client's credentials.
	- This message serves as the **proof of identity**. The client doesn't send its password; it sends data that only someone who knows the correct password could produce given the server's challenge. 
	- Optional session keys and further negotiated options can also be embedded depending on the negotiated capabilities from earlier stages.

The Server then verifies the Client's challenge response by recomputing the expected response based on the stored NT hash of the account and the original challenge.
No plaintext password is transmitted.

>[!note] For the full list of `NegotiateFlags` and their possible values, see [`NEGOTIATE — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/99d90ff4-957f-4c8a-80e4-5bfe5a9a9832).

### Pass-though vs workgroup authentication

NTLM authentication can be divided into two types based on two verifies the credentials: **pass-through authentication** and **workgroup authentication**.


- **Pass-through NTLM authentication**
	- NTLM authentication in *domain environments* (AD); the server forwards the client’s response to a DC (Domain Controller) for verification.

![](https://academy.hackthebox.com/storage/modules/232/Domain-joined_Computers_NTLM_Authentication.png)

- **Workgroup NTLM authentication**
	- NTLM authentication in a *non-domain (peer-to-peer) environments*; the server validates the authentication locally against its own accounts database (SAM); no domain controller is involved.

![](https://academy.hackthebox.com/storage/modules/232/Workgroup_Computers_NTLM_Authentication.png)

## NT hash

>An **NT hash** is a *static password hash* of a user's password stored on Windows systems.

The NT hash is defined as follows:
1. The user's password is taken as-is.
2. The password string is encoded in **UTF‑16 Little Endian ([UTF‑16LE](https://en.wikipedia.org/wiki/UTF-16#Byte-order_encoding_schemes))**. Unlike ASCII or UTF-8, UTF-16LE represents each character as 2 bytes in _little-endian_ order.
3. The UTF-16LE byte sequence is **hashed using [MD4](https://en.wikipedia.org/wiki/MD4)**. This produces a 128-bit (16-byte) result, typically represented as 32 hex character. This is the **NT hash**.

```
NT hash = MD4( UTF-16LE(password) )
```

NT hashes are stored in the Windows SAM database for local accounts, and `NTDS.dit` for domain accounts; also, in memory of logged-on sessions (LSASS).

>[!bug] NT hashes are not salted.

So, the NT hash is the *secret key material* used by NTLM for authentication. If you know this hash, you can authenticate as the user without knowing the plaintext password — this is the basis of **[[Pass-the-Hash]]**.

>[!note] The NT hash is often incorrectly called "NTLM hash"; it's best to use call it **NT hash** to avoid confusion with network challenge responses.

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
>See [`Password hashing algorithm — LAN Manager, Wikipedia`](https://en.wikipedia.org/wiki/LAN_Manager#Password_hashing_algorithm). 

## NTLMv1 and NTLMv2

The NTLM protocol comes in two versions:
- NTLMv1
- NTLMv2
They operate using the same principle but calculate the challenge from the `AUTHENTICATE_MESSAGE` differently: NTLMv1 uses the DES-based LanMan one-way function (LMOWF), and NTLMv2 uses the NT MD4-based on-way function (NTOWF).

>[!important] The NTLM version used on hosts, whether NTLMv1 or NTLMv2, is [configured out-of-band](https://learn.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/network-security-lan-manager-authentication-level) before authentication.

### NTLMv1

- In NTLMv1, the challenge response (what the Client sends in `AUTHENTICATE_MESSAGE` to the Server to authenticate themselves) is computed purely by encrypting the server's challenge (the one sent by the server in `CHALLENGE_MESSAGE`) with the key derived from the NT hash of the user's password.

Given the 8-byte server challenge (the nonce) sent by the Server in `CHALLENGE_MESSAGE`, the Client computes the challenge response as follows:

1. The Client takes its NT hash (16 bytes long) and **pads it to 21 bytes** (the original 16 bytes + 5 zero bytes).
2. These 21 bytes are then chopped into **three blocks of 7 bytes each**.
3. Each 7-byte block is transformed into a **8-byte DES key** (the 7 bytes are converted into a bit stream, and a [parity bit](https://en.wikipedia.org/wiki/Parity_bit) is inserted each 7 bits).
4. Each of these three DES keys is used to encrypt the 8-byte **server challenge (the nonce)**. This results in three 8-byte ciphertext values.
5. The values are concatenated together: 8 + 8 + 8 = 24 bytes. This 24-byte blob is the **NTLMv1 challenge response**.

The above scheme can be written as follows (taken from [Wikipedia](https://en.wikipedia.org/wiki/NTLM#NTLMv1)):

```
C = 8-byte server challenge, random
K1 | K2 | K3 = LM/NT-hash | 5-bytes-0
response = DES(K1,C) | DES(K2,C) | DES(K3,C)
```

So, the entire NTLMv1 response is literally `DES(server_challenge)` using three different keys derived from the users's NT hash. Because of this:
- Each of the 3 DES keys can be attacked independently.
- There's no client randomness: if the same challenge is used, the response is the same.
This is why NTLMv1 is considered weak — DES keys are short, and every component of the response **can be cracked or rainbow-table'd**.

```shell-session
[SMB] NTLMv1 Client   : 172.19.117.36
[SMB] NTLMv1 Username : Support1
[SMB] NTLMv1 Hash     : Support1::WIN-OLMHXGAP0V2:e2dL3196O8f55fB6:Q49S19A2937J6XC3CKA418EI4958OHB9:xF2K324O5L6Q7V8C
```

### NTLMv2

- NTLMv2 still proves knowledge of the user’s secret, but it does so in a way that incorporates **client entropy and context**, which defends against simple replay and precomputation.
- Instead of relying on DES, NTLMv2 uses **[HMAC](https://en.wikipedia.org/wiki/HMAC)-[MD5](https://en.wikipedia.org/wiki/MD5)** and mixes server-generated and client-generated nonces plus timestamps.


In NTLMv2 `CHALLENGE_MESSAGE`, the Server sends not only the 8-byte nonce, but also authentication domain in `TargetInfo` and username (usually uppercase). Specifically, `TargetInfo` contains AV pairs (Attribute-Value pairs) like:
- NetBIOS name
- DNS name
- Timestamp

The Client computes the challenge response as follows:
 
1. The Client derives the **NTLMv2 hash** (don't confuse with NT hash) that binds the user's secret with their identity (username + domain) so that the challenge response can't be reused out of context. 
	- For this, the Client computes a HMAC-MD5 hash of the concatenated username and domain, using NT hash as the key.  

```
v2hash = HMAC-MD5( NT-hash, UTF16-LE(USERNAME + DOMAIN))
```

>[!note] This NTLMv2 hash is a _derived key_ — it’s still ultimately tied to the password, but also tied to the user identity and domain, so it can’t simply be reused in other contexts.

2. The Client then constructs a **blob** (also called the **`NTLMv2_CLIENT_CHALLENGE`** structure) that contains client-side context information. This is what makes an NTLMv2 response unique even for the same server challenge. A typical blob contains:
	- **`RespType`/`HiRespType`** — version indicators.
	- Reserved fields.
	- Timestamp — current time (usually current time in [NT time format](https://www.utctime.net/utc-to-nt-converter)).
	- An 8-byte random **client challenge** (nonce).
	- Reserved.
	- AV pairs (`TargetInfo`) supplied by the server (domain name, server name, etc.).

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

3. The Client concatenates the **server challenge + blob** and **HMAC-MD5 it using the NTLMv2 hash as key**. This produces a 16-byte digest, which is used as a proof of knowledge of the NTLMv2 hash.

```
NTProofStr = HMAC-MD5( v2hash, ServerChallenge + Blob )
```

4. The final NTLMv2 **challenge response** is 16-byte HMAC-MD5 digest + blob.

```
NTLMv2_RESPONSE = NTProofStr + Blob
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

So, in NTLMv2, both sides add randomness (server challenge, client nonce), and there's a timestamp. A HMAC is computed using a key derived from NT hash + identity context. This means the response *varies even for the same password and server challenge*.
This can still be cracked, but you will need to brute-force the NTLMv2 key. You can't use rainbow tables — since no fixed DES keys are used.

Because of that difference, NTLMv2 is usually enforced in modern environments — **NTLMv1 is cryptographically insecure and easy to attack**.

---

```shell-session
[SMB] NTLMv2-SSP Client   : 172.19.117.55
[SMB] NTLMv2-SSP Username : INLANEFREIGHT\Support2
[SMB] NTLMv2-SSP Hash     : Support2::INLANEFREIGHT:e2d2339638fc5fd6:D4979A923DD76BC3CFA418E94958E2B0:010100000000000000E0550D97CCD901509F9CE743AB58760000000002000800350034005800360001001E00570049004E002D00390038004B005100480054005300390048004200550004003400570049004E002D00390038004B00510048005400530039004800420055002E0035003400580036002E004C004F00430041004C000300140035003400580036002E004C004F00430041004C000500140035003400580036002E004C004F00430041004C000700080000E0550D97CCD901060004000200000008003000300000000000000000000000004000002DB95E9E27F0AD66CAA477372F555B500CFEA9C5A231FC68F0DA4FABFF76607E0A001000000000000000000000000000000000000900240063006900660073002F003100370032002E00310036002E003100310037002E00330030000000000000000000
```

## NTLM Session Security

If the client and server negotiate it, [session security](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/d1c86e81-eb66-47fd-8a6f-970050121347) provides [message integrity](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/131b0062-7958-460e-bca5-c7a9f9086652) (`signing`) and [message confidentiality](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/115f9c7d-bc30-4262-ae96-254555c14ea6) (`sealing`). The `NTLM` protocol itself does not provide session security; instead, [SSPI](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/0776e9c8-1d92-488f-9219-10765d11c6b7) provides it. `NTLMv1`, supplanted by `NTLMv2`, does not support `sealing` but only `signing`; therefore, [Microsoft](https://support.microsoft.com/en-au/topic/security-guidance-for-ntlmv1-and-lm-network-authentication-da2168b6-4a31-0088-fb03-f081acde6e73) strongly recommends against its usage (and the deprecated `LM` authentication protocol also).

## Message signing and sealing

`Message signing` provides message integrity and helps against relay attacks; it is a critical security feature designed to enhance the security of messages sent between the client and server during `NTLM` communications. When `session signing` is negotiated, the client and server negotiate a `session key` to sign all messages exchanged. The `session key` is generated using a combination of the client's and server's challenge messages and the user's password hash. Once the session key is established, all messages between the client and server are signed using a `MAC`. The `MAC` is generated by applying a cryptographic algorithm to the message and the session key. The server can verify the `MAC` by using the same algorithm as the message and the session key and comparing the result to the `MAC` provided by the client. Although an adversary might be eavesdropping, they don't possess the user's password hash since it is never transmitted over the wire, and therefore cannot sign messages. Based on the blog post [The Basics of SMB Signing (covering both SMB1 and SMB2)](https://learn.microsoft.com/en-us/archive/blogs/josebda/the-basics-of-smb-signing-covering-both-smb1-and-smb2), we can know the default `SMB signing` settings for hosts in the network depending on the SMB version they are running. Except for `SMB1`, which has three possible settings, `Required`, `Enabled`, or `Disabled`, `SMB2` and `SMB3` only have `Required` or `Not Required`:

| **Host**              | **Default Signing Setting** |
| --------------------- | --------------------------- |
| `SMB1 Client`         | `Enabled`                   |
| `SMB1 Server`         | `Disabled`                  |
| `SMB2 & SMB3 Clients` | `Not Required`              |
| `SMB2 & SMB3 Servers` | `Not Required`              |
| `Domain Controllers`  | `Required`                  |

Due to the ever-lasting abuse of the default SMB signing settings by adversaries, [Microsoft](https://blogs.windows.com/windows-insider/2023/06/02/announcing-windows-11-insider-preview-build-25381/) released an update to enforce SMB `signing` on Windows 11 Insider editions (and later on for major releases). Microsoft decided, for a better security stature, to finally let go of the legacy behavior where Windows 10 and 11 required SMB `signing` by default only when connecting to shares named `SYSVOL` and `NETLOGON` and where DCs required SMB `signing` when any client connected to them. Ned Pyle, a Principal Program Manager at Microsoft, wrote the following regretful statement in the post [SMB signing required by default in Windows Insider](https://techcommunity.microsoft.com/t5/storage-at-microsoft/smb-signing-required-by-default-in-windows-insider/ba-p/3831704):

"SMB encryption is far more secure than signing, but environments still run legacy systems that don't support SMB 3.0 and later. If I could time travel to the 1990s, SMB signing would've always been on and we'd have introduced SMB encryption much sooner; sadly, I was both in high school and not in charge. We'll continue to push out more secure SMB defaults and many new SMB security options in the coming years; I know they can be painful for application compatibility and Windows has a legacy of ensuring ease of use, but security cannot be left to chance."

`Message sealing` provides message confidentiality by implementing a symmetric-key encryption mechanism; it ensures that the content of the messages exchanged between the client and server remains secure and that adversaries cannot read or tamper with them. In the context of `NTLM`, `sealing` also implies `signing` because every `sealed` message is also `signed`.


## Extended Protection for Authentication (EPA)

`Extended Protection for Authentication` (`EPA`), based on [RFC 5056](https://datatracker.ietf.org/doc/html/rfc5056), is a feature introduced in Windows Server 2008 and later versions that enhance the security of `NTLM` authentication. When `EPA` is enabled, the client and server establish a secure channel using a `channel binding token` (`CBT`). The `CBT` binds the authentication to the specific channel characteristics, such as the IP address and port, preventing the authentication from replaying on a different channel. `EPA` is designed to work with SMB and HTTP protocols, providing additional security for applications and services that rely on `NTLM` authentication; however, it requires the client and server to support it to establish a secure channel.
## References and further reading

- [`LAN Manager — Wikipedia`](https://en.wikipedia.org/wiki/LAN_Manager)
- [`Challenge-response authetnciation — Wikipedia`](https://en.wikipedia.org/wiki/Challenge%E2%80%93response_authentication)
- [`Code page — Wikipedia`](https://en.wikipedia.org/wiki/Code_page)
- [`Bit numbering — Wikipedia`](https://en.wikipedia.org/wiki/Bit_numbering#Most_significant_bit)
- [`Data Encryption Standard — Wikipedia`](https://en.wikipedia.org/wiki/Data_Encryption_Standard)
- [`Parity bit — Wikipedia`](https://en.wikipedia.org/wiki/Parity_bit)

---

- [`HMAC — Wikipedia`](https://en.wikipedia.org/wiki/HMAC)
- [`MD5 — Wikipedia`](https://en.wikipedia.org/wiki/MD5)
- [`MD4 — Wikipedia`](https://en.wikipedia.org/wiki/MD4)

---
- [`SSPI Architectural Overview — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/rpc/sspi-architectural-overview)
- [`Security Support Providers (SSPs) — Microsoft Learn`](https://learn.microsoft.com/en-us/windows/win32/rpc/security-support-providers-ssps-)
- [`Network security: LAN Manager authentication level — Microsoft Learn`](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/network-security-lan-manager-authentication-level)
---
- [`Message Syntax — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/907f519d-6217-45b1-b421-dca10fc8af0d)
- [`NEGOTIATE_MESSAGE — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/b34032e5-3aae-4bc6-84c3-c6d80eadf7f2)
- [`CHALLENGE_MESSAGE — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/801a4681-8809-4be9-ab0d-61dcfe762786)
- [`AUTHENTICATE_MESSAGE — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/033d32cc-88f9-4483-9bf2-b273055038ce)
- [`NEGOTIATE — Microsoft Learn`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/99d90ff4-957f-4c8a-80e4-5bfe5a9a9832)

---
- [`Understanding NTLM Authentication and NTLM Relay Attacks — vaadata`](https://www.vaadata.com/blog/understanding-ntlm-authentication-and-ntlm-relay-attacks/)
- [`NTLM Authentication — Nathaniel Cyber Security`](https://docs.wehost.co.in/cybersecurity/ntlm-authentication)
## drafts


- Before the NTLM authentication starts, the Client and Server establish a connection using a transport protocol such as TCP.

---



4. **Server validation**
	- Once the server receives the `AUTHETNCIATE_MESSAGE`:
		- If authentication is happening locally on a standalone server, the server uses its local account database to compute the expected response based on the stored NT hash of the account and the original challenge, and compares it what the client sent.
		- If the account is a **domain account**, the server forwards the challenge-response pair along with the user's account name to the **domain controller (DC)**. The DC uses the stored NT hash from Active Directory and the same algorithm to validate the client's proof. A success or failure is returned.
	- Only once this validation succeeds is the authentication considered complete and the client granted an authenticated session.

5. **Message integrity** (optional)
	- Although the core handshake is the three messages above, NTLM also supports optional **message integrity (signing)** and **confidentiality (sealing)** after authentication, based on flags negotiated in the Type 1 and Type 2 messages. These features provide ongoing cryptographic protection for subsequent communication but are _not part of the basic authentication handshake_.
