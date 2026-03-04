---
created: 11-01-2026
---
## SSH

>**[Secure Shell (SSH)](https://en.wikipedia.org/wiki/Secure_Shell)** is a cryptographic network protocol for operating network services securely over an unsecured network. 

- The most notable applications of SSH include remote login and command execution.

SSH was originally designed for Unix-like operating systems as a replacement for Telnet and other insecure, plain-text Unix shell protocols, such as `rsh` (Berkley Remote Shell), `rlogin`, `rexec`, etc.

SSH provides:
- Confidentiality through encryption
- Integrity through message authentication codes
- Authentication through multiple possible mechanisms

## SSH client-server model

SSH operates on the client-server mode.

- The **SSH server** listens on **TCP port `22`** by default.