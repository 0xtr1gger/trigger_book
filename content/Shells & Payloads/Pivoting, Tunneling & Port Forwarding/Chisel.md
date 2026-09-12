---
created: 2026-09-05
updated: 2026-09-12
tags:
  - pivoting
---

>[!abstract]+ **Scope**: `Chisel`; SOCKS5 tunneling over a WebSocket/SSH transport; compiling a static binary; forward and reverse SOCKS5 tunnels; forwarding individual ports; authentication.

## `Chisel`

>[`Chisel`](https://github.com/jpillora/chisel) is a client/server tunneling tool that multiplexes TCP or UDP connections through an encrypted SSH session carried over HTTP.

- Chisel operates on a client-server model, where **a single Chisel binary can function as either**.
	- **Chisel server** — listens for incoming HTTP connections on a specified port (default: `8080`), and accepts **WebSocket upgrade** requests from clients; once a WebSocket connection is established, the server creates an SSH session over it.
	- **Chisel client** — initiates an HTTP connection to the server and requests a WebSocket upgrade, then establishes an SSH session over that connection. It listens on a local port and forwards that traffic through the tunnel (forward mode), or connects out to a destination on the server's behalf (reverse mode).

- In a forward tunneling scenario, the server runs on the pivot, and the client runs on your attacking machine.

- Chisel's `socks` remote turns the tunnel into a general-purpose SOCKS5 proxy: the destination is decided per-connection by the SOCKS5 handshake itself, then resolved on the other end of the tunnel. One tunnel then reaches any destination visible from that end, instead of needing a separate remote for every host and port you want to reach.

>[!note] Chisel is written in Go; it distributes as a single lightweight, cross-platform binary.

### How Chisel works

- Chisel uses **WebSockets as a transport**. WebSockets run over HTTP(S), so a Chisel tunnel is unlikely to be blocked by firewalls that allow outbound web traffic.

>[!note]+ Each WebSocket connection starts as an HTTP request carrying an `Upgrade` header. Once upgraded, the connection stays open and carries data **bidirectionally**. To learn more about WebSockets, see [[🛠️ WebSocket vulnerabilities]].

- Once the WebSocket tunnel is up, Chisel doesn't send raw data through it directly — it opens an SSH session **inside the WebSocket stream**, using Go's `crypto/ssh` library rather than an actual SSH server on port `22`. The WebSocket connection is only a transport medium; SSH provides the encryption and authentication.

- The SSH session key is derived as follows:
	1. When the Chisel **server** starts, it generates a ECDSA key pair in-memory (or uses the key pair you specify with `--key` or `--keyfile`).
	2. The public key is hashed using **SHA-256**, and the hash is **Base64-encoded** to form a server fingerprint.
	3. When a Chisel client connects, the server presents its fingerprint.
	4. Both sides then use this key to establish an encrypted SSH session.

>[!tip]+
> - You can use the `--fingerprint` option on the client side to specify the fingerprint of the server to connect to; in this case, the client  refuses to connect to anything else

>[!important] SSH-layer encryption is always on, independent of the outer transport. By default Chisel runs over plain WebSocket (`ws://`) on HTTP, which is encrypted at the SSH layer but not at the transport layer. Enabling TLS (`--tls-key`/`--tls-cert`, or `--tls-domain` on port `443`) wraps that WebSocket in `wss://`, so the traffic on the wire also blends in with ordinary HTTPS.

### Installation

- Grab [the latest release](https://github.com/jpillora/chisel/releases/latest), or install it with the official script:

```bash
curl https://i.jpillora.com/chisel! | bash
```

- Then copy the binary to the pivot; see [[🛠️ Windows file transfers]] and [[🛠️ Linux file transfers]].

>[!note] glibc compatibility on older targets
>Compiling on a modern Linux distribution links the binary against a modern `glibc` by default. Running that binary on a target with an older `glibc` fails with `version GLIBC_X.XX not found`. Building with `CGO_ENABLED=0` produces a static binary with no `glibc` dependency, so it runs on any Linux kernel version.

## Using Chisel

### Forward tunnel

- In forward tunneling, the pivot runs the Chisel **server** and listens for a connection from your attacking machine.
- You connect to it with the Chisel **client** and specify the local port your machine will listen on.
- Once the tunnel is up, the server relays traffic between that local port and the final destination, bidirectionally.

---

1. On the pivot host, start the Chisel server:

```bash
chisel server -p 8080 --socks5
```

| Option     | Description                                                                         |
| ---------- | ----------------------------------------------------------------------------------- |
| `-p`       | Specify the port the server listens on for incoming connections from the client.    |
| `--host`   | Specify a bind address for the server to listen on (default: `0.0.0.0`).            |
| `--socks5` | Expose the server's internal SOCKS5 for connected clients to route traffic through. |
| `-v`       | Enable verbose logging.                                                             |

2. On your attacking machine, connect to the server with the Chisel client:

```bash
chisel client 10.10.11.5:8080 9050:socks
```

- Once the tunnel is established, a SOCKS5 proxy listens on your local port `9050`. 
- Connections to that port are carried through the tunnel to the server. The server decodes the request and opens a corresponding connection to the specified target on its behalf, then carries traffic between your machine and the target.

>[!note] To learn more about SOCKS, see [[SOCKS]].

- To route traffic through the SOCKS listener on your side, you can use `proxychains`.

```bash
proxychains nmap -sV 172.16.5.19
```

![[SOCKS#`proxychains`]]

### Forwarding a single port

- Forward one specific port (instead of creating a SOCKS proxy):

```bash
chisel client 10.10.11.5:8080 3306:172.16.5.19:3306
```

```bash
mysql -h 127.0.0.1 -P 3306 -u root -p
```

- Append `/udp` to forward UDP instead of TCP:

```bash
chisel client 10.10.11.5:8080 53:172.16.5.19:53/udp
```

### Reverse tunnel

- Reverse tunneling inverts the connection direction: instead of your machine reaching out to the pivot, **the compromised host initiates an outbound connection to you**. 
- Reverse tunnels are useful in situations where the pivot can't accept arbitrary inbound connections, but can initiate outbound connections to your attacking machine.
---

1. On your attacker machine, start the Chisel **server** in reverse mode:

```bash
chisel server --reverse --port 8080 -v
```

| Option      | Description                                                                            |
| ----------- | -------------------------------------------------------------------------------------- |
| `--reverse` | Configure the server to accept connections from clients that initiate reverse tunnels. |
| `--host`    | Specify a bind address for the server to listen on (default: `0.0.0.0`).               |
| `-v`        | Enable verbose logging.                                                                |

2. On the pivot host, use Chisel client to connect back to your attacking machine and request a reverse SOCKS5 remote:

```bash
chisel client 10.10.11.11:8080 R:socks
```

>[!note]  `R:socks` establishes a **reverse SOCKS5 proxy**: your Chisel server listens on local port `1080` on your attacking machine.

- To route traffic through the SOCKS listener on your side, you can use `proxychains`.

```bash
proxychains nmap -sV 172.16.5.19
```

>[!note] See [[SOCKS#`proxychains`]].

>[!tip]+
>- You can override the default SOCKS port (`1080`) using `R:<port>:socks`:
>```bash
>chisel client 10.10.11.1:8080 R:9050:socks
>```

### Forwarding a single port in reverse

- Prefix a remote with `R:` to forward a single port instead of a SOCKS5 proxy:

```bash
chisel client <attacker_ip_address>:8080 R:3306:172.16.5.19:3306
```

- This binds port `3306` on your attacking machine and forwards it, through the pivot's outbound connection, to `172.16.5.19:3306` as seen from the pivot's network.

## Authentication

- Chisel supports HTTP basic authentication:

1. Start the server with authentication enabled:

```bash
chisel server -p 8080 --auth username:password
```

2. Include the credentials in the client command:

```bash
chisel client --auth username:password http://10.10.11.5:8080 socks
```

>[!note] With `--authfile` instead of a single `--auth` pair, a user's entry must also match the literal token `socks` (or the wildcard `""`) to use SOCKS5 remotes — otherwise the server denies `socks` connections even for users who authenticate successfully.

## Option reference

- **Server options**, `chisel server [options]`:

| **Option**     | **Description**                                                                                                                                                                                                                                                 |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--host`       | Defines the HTTP listening host (defaults to the environment variable `HOST` and falls back to `0.0.0.0`).                                                                                                                                                      |
| `--port`, `-p` | Defines the HTTP listening port (defaults to the environment variable `PORT` and falls back to `8080`).                                                                                                                                                         |
| `--key`        | **(Deprecated — use `--keygen` and `--keyfile` instead).** <br>Optional string to seed ECDSA key generation for securing communications. Defaults to `CHISEL_KEY`, otherwise a new key is generated each run.                                                   |
| `--keygen`     | Path to a file to write a newly generated PEM-encoded SSH private key. <br>Use `-` to output to `STDOUT`. <br>Can be combined with `--key` to output an existing key.                                                                                           |
| `--keyfile`    | Path to a PEM-encoded SSH private key (or inline Base64 string). <br>Overrides `--key`. <br>Defaults to `CHISEL_KEY_FILE`.                                                                                                                                      |
| `--authfile`   | Path to a `users.json` file that defines user authentication and access rules. File auto-reloads on change.                                                                                                                                                     |
| `--auth`       | A string of the form `<user>:<password>` that represents a single user with full access (equivalent to `{"<user>:<password>": [""]}` in the `--authfile`).<br>Defaults to `AUTH` environment variable.                                                          |
| `--keepalive`  | Keep-alive interval (e.g., `5s`, `2m`). Defaults to `25s`. <br>Set to `0s` to disable. Helps prevent proxy timeouts.                                                                                                                                            |
| `--backend`    | Specifies an HTTP server to proxy normal HTTP requests to (useful for disguising Chisel traffic).                                                                                                                                                               |
| `--socks5`     | Allows clients to use the server's internal SOCKS5 proxy through forward `socks` remotes.                                                                                                                                                                       |
| `--reverse`    | Allows clients to specify reverse port forwarding remotes in addition to normal remotes.                                                                                                                                                                        |
| `--tls-key`    | Enables TLS; provides an optional path to a PEM-encoded TLS private key. <br>Requires `--tls-cert`. <br>Cannot be used with `--tls-domain`.                                                                                                                     |
| `--tls-cert`   | Enables TLS; provides an optional path to a PEM-encoded TLS certificate. <br>Requires `--tls-key`. <br>Cannot be used with `--tls-domain`.                                                                                                                      |
| `--tls-domain` | Enables TLS with automatic Let's Encrypt certificates for one or more domains. <br>Requires port `443`. <br>Caches certificates in `$HOME/.cache/chisel` (modifiable via `CHISEL_LE_CACHE`). <br>Optional notification email can be set with `CHISEL_LE_EMAIL`. |
| `--tls-ca`     | Path or directory containing PEM-encoded CA certificates for validating client connections. Used for mutual TLS. Overrides system roots.                                                                                                                        |
| `--pid`        | Generates a PID file in the current working directory.                                                                                                                                                                                                          |
| `-v`           | Enables verbose logging.                                                                                                                                                                                                                                        |
| `--help`       | Displays help text.                                                                                                                                                                                                                                             |

>[!note]+ `users.json` file format
>The `users.json` file, set with the `--authfile` option, uses the following format:
>```json
>{
>	"<user>:<password>": ["<address_regex>", "<address_regex>"]
>}
>```
> - When `<user>` connects to the Chisel server, its password is verified against `<password>`, then its remote address is compared against the list of address regular expressions for a match. Addresses always come in the form `<remote-host>:<remote-port>` for normal remotes, `R:<local_interface>:<local_port>` for reverse port forwarding remotes, and the literal string `socks` for SOCKS5 remotes (forward or reverse).

- **Client options**, `chisel client [options] <server> <remote> [remote] [remote] ...`:

| **Option**             | **Description**                                                                                                                                                                                                                 |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--fingerprint`        | **Strongly recommended.** Fingerprint string for host-key validation against the server's public key.<br>Must be a 44-character Base64-encoded SHA-256 hash (with `=` at the end). Fingerprint mismatches close the connection. |
| `--auth`               | Username and password for client authentication, in the format `<user>:<password>`. <br>Compared to entries in the server's `--authfile`. <br>Defaults to the `AUTH` environment variable.                                     |
| `--keepalive`          | Keep-alive interval (e.g., `5s`, `2m`). Defaults to `25s`. <br>Set to `0s` to disable. Prevents proxy timeouts.                                                                                                                 |
| `--max-retry-count`    | Maximum number of reconnection attempts before exiting. Defaults to unlimited.                                                                                                                                                  |
| `--max-retry-interval` | Maximum wait time between reconnection attempts. Defaults to 5 minutes.                                                                                                                                                         |
| `--proxy`              | Optional HTTP CONNECT or SOCKS5 proxy used to reach the Chisel server. Authentication can be embedded in the URL (e.g., `http://admin:pass@proxy:8080`, `socks://user:pass@host:9050`).                                         |
| `--header`             | Sets a custom HTTP header in the format `"Header: Value"`. Can be used multiple times (e.g., `--header "Header1: Value1" --header "Header1: Value2"`).                                                                          |
| `--hostname`           | Overrides the `Host` header (defaults to the host found in the server URL).                                                                                                                                                     |
| `--sni`                | Overrides the Server Name (SNI) when using TLS. Defaults to the hostname.                                                                                                                                                       |
| `--tls-ca`             | Optional path to a root CA bundle used to verify the Chisel server when using HTTPS/WSS. Defaults to system CAs.                                                                                                                |
| `--tls-skip-verify`    | Skips verification of the server's TLS certificate chain and hostname. Accepts any TLS certificate. Fingerprint verification still applies after connection.                                                                    |
| `--tls-key`            | Path to a PEM-encoded private key for client authentication (mutual TLS).                                                                                                                                                       |
| `--tls-cert`           | Path to a PEM-encoded certificate matching the private key. Required for client authentication (mutual TLS).                                                                                                                   |
| `--pid`                | Generates a PID file in the current working directory.                                                                                                                                                                          |
| `-v`                   | Enables verbose logging.                                                                                                                                                                                                        |

## References and further reading

- [`Chisel — GitHub`](https://github.com/jpillora/chisel)
- [`SOCKS — Wikipedia`](https://en.wikipedia.org/wiki/SOCKS)
- [`A Detailed Guide on Chisel — Hacking Articles`](https://www.hackingarticles.in/chisel-port-forwarding-a-detailed-guide/)
- [`Chisel - Tunneling Traffic with SSH over HTTP — UncleSp1d3r`](https://unclesp1d3r.github.io/posts/2023/02/chisel-tunneling-traffic-with-ssh-over-http/)
- [`How to Use Chisel for Reverse Tunneling — getcyber.me`](https://getcyber.me/posts/how-to-use-chisel-for-reverse-tunneling/)
- [`Port forwarding with Chisel — 0xBEN`](https://notes.benheater.com/books/network-pivoting/page/port-forwarding-with-chisel)

