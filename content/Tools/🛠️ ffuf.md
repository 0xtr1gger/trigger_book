---
created: 2026-09-28
updated: 2026-09-29
---
## `ffuf`

>[!note]+ Installation
>- Kali Linux or Parrot:
>```bash
>apt install ffuf -y
>```
>- From the [GitHub repository](https://github.com/ffuf/ffuf):
>```bash
> git clone https://github.com/ffuf/ffuf && \
> cd ffuf && \
> go get && \
> go build
>```

| Option             | Description                                                                                                                                                              |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `-w`               | Wordlist to use. <br>By default, assigns the wordlist to the `FUZZ` keyword; you can set custom keywords for different wordlists using `-w <wordlist>:<keyword>` syntax. |
| `-u`               | Target URL to fuzz.                                                                                                                                                      |
| `-X`               | HTTP method (`GET`, `POST`, etc.).                                                                                                                                       |
| `-H`               | Custom HTTP headers (`-H "<header>: <value>"`).                                                                                                                          |
| `-d`               | `POST` data (for `POST` requests).                                                                                                                                       |
| `-r`               | Follow redirects (default: false).                                                                                                                                       |
| `recursion`        | Scan recursively; only one keyword supported, `FUZZ`; the URL has to end with the keyword (e.g., `-recursion -u https://example.com/FUZZ`).                              |
| `-recursion-depth` | Maximum recursion depth (default `6`).                                                                                                                                   |
| `-o`               | Output file path.                                                                                                                                                        |
| `-v`               | Verbose output.                                                                                                                                                          |
| `-s`               | Silent mode (suppresses banner).                                                                                                                                         |

| Option             | Description                                                                                                                                 |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `-H`               | HTTP headers to add to the requests `ffuf` makes.<br>E.g., `-H "X-Host: example.com" -H "X-Forwarded-For: 127.0.0.1"`.                      |
| `-X`               | HTTP method to use (default `GET`).                                                                                                         |
| `-b`               | Cookies to use.<br>E.g., `-b "sessionid=123; stay-logged-in=yes"`.                                                                          |
| `-d`               | `POST` data (for `POST` requests).<br>E.g., `-X POST -d "username=admin&password=FUZZ"`.                                                    |
| `-u`               | Target URL.                                                                                                                                 |
| `-r`               | Follow redirects (default false).                                                                                                           |
| `-recursion`       | Scan recursively. <br>Only one `FUZZ` keyword is supported, and URL has to end with `FUZZ`, e.g., `-recursion -u https://example.com/FUZZ`. |
| `-recursion-depth` | Maximum recursion depth (default `6`).                                                                                                      |
| `-timeout`         | HTTP request timeout, in seconds (default `10`).                                                                                            |
| `-x`               | HTTP proxy URL.                                                                                                                             |
| `-c`               | Colorize output (default false).                                                                                                            |
| `-maxtime`         | Maximum running time, in seconds.                                                                                                           |
| `-p`               | Delay between requests, in seconds.                                                                                                         |
| `-w`               | Wordlist to use.                                                                                                                            |

# drafts

## Ffuf



- To enumerate directories and files:

```bash
ffuf -c -w wordlist.txt -u https://example.com/FUZZ
```

- To enumerate directories recursively:

```bash
ffuf -c -w wordlist.txt -u https://example.com/FUZZ -recursion -recursion-depth 2
```
## Customizing requests


- To add custom HTTP headers:

```bash
ffuf -c -w wordlist.txt -u https://example.com/FUZZ -H "X-Forwarded-For: 127.0.0.1"
```

- To change HTTP method:

```bash
ffuf -c -w wordlist.txt -u https://example.com/FUZZ -X POST
```

- To add `POST` data:

```bash
ffuf -c -w wordlist.txt -u https://example.com/login -X POST -d "username=example&password=FUZZ"
```

- To fuzz multiple parameters:

```bash
ffuf -c -u https://example.com/login -X POST -w usernames.txt:USR -w passwords.txt:PASSWD -d "username=USR&password=PASSWD" 
```

## Matching and filtering

`ffuf` offers a number of flags you can use to filter and match enumeration results:

| Option | Description                                                                    | Option | Description                                                                     |
| ------ | ------------------------------------------------------------------------------ | ------ | ------------------------------------------------------------------------------- |
| `-mc`  | Match HTTP status codes                                                        | `-fc`  | Filter out HTTP responses with this status codes                                |
| `-ms`  | Match HTTP response size                                                       | `-fs`  | Filter out HTTP responses with this size                                        |
| `-ml`  | Match lines in HTTP responses                                                  | `-fl`  | Filter out HTTP responses with this number of lines                             |
| `-mw`  | Match words in HTTP responses                                                  | `-fw`  | Filter out HTTP responses with this number of words                             |
| `-mr`  | Match HTTP responses with regex                                                | `-fr`  | Filter out HTTP responses matching this regex                                   |
| `-mt`  | Match number of milliseconds to the first response byte (e.g., `>100`, `<100`) | `-ft`  | Filter number of milliseconds to the first response byte (e.g., `>100`, `<100`) |

- To filter out responses with status code `404`:

```bash
ffuf -w wordlist.txt:FUZZ -u https://example.com/FUZZ -fc 404
```

- To match only responses with status codes `200` or `301`:

```bash
ffuf -w wordlist.txt:FUZZ -u https://example.com/FUZZ -mc 200,301
```

---

- To filter out responses with the size between `0` and `100` bytes:

```bash
ffuf -w wordlist.txt:FUZZ -u https://example.com/FUZZ -fs 0,100
```

- To match only responses with the size between `100` and `1000` bytes:

```bash
ffuf -w wordlist.txt:FUZZ -u https://example.com/FUZZ -ms 100,1000
```

---

- To match responses that contain the phrase `You don't have access!`.

```

```
## Cheatsheet

| Option             | Description                                                                                                                                 |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `-H`               | HTTP headers to add to the requests `ffuf` makes.<br>E.g., `-H "X-Host: example.com" -H "X-Forwarded-For: 127.0.0.1"`.                      |
| `-X`               | HTTP method to use (default `GET`).                                                                                                         |
| `-b`               | Cookies to use.<br>E.g., `-b "sessionid=123; stay-logged-in=yes"`.                                                                          |
| `-d`               | `POST` data (for `POST` requests).<br>E.g., `-X POST -d "username=admin&password=FUZZ"`.                                                    |
| `-u`               | Target URL.                                                                                                                                 |
| `-r`               | Follow redirects (default false).                                                                                                           |
| `-recursion`       | Scan recursively. <br>Only one `FUZZ` keyword is supported, and URL has to end with `FUZZ`, e.g., `-recursion -u https://example.com/FUZZ`. |
| `-recursion-depth` | Maximum recursion depth (default `6`).                                                                                                      |
| `-timeout`         | HTTP request timeout, in seconds (default `10`).                                                                                            |
| `-x`               | HTTP proxy URL.                                                                                                                             |
| `-c`               | Colorize output (default false).                                                                                                            |
| `-maxtime`         | Maximum running time, in seconds.                                                                                                           |
| `-p`               | Delay between requests, in seconds.                                                                                                         |
| `-w`               | Wordlist to use.                                                                                                                            |
|                    |                                                                                                                                             |
|                    |                                                                                                                                             |

| Command                                                                                                                                                         | Description              |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------ |
| `ffuf -h`                                                                                                                                                       | ffuf help                |
| `ffuf -w wordlist.txt:FUZZ -u http://SERVER_IP:PORT/FUZZ`                                                                                                       | Directory Fuzzing        |
| `ffuf -w wordlist.txt:FUZZ -u http://SERVER_IP:PORT/indexFUZZ`                                                                                                  | Extension Fuzzing        |
| `ffuf -w wordlist.txt:FUZZ -u http://SERVER_IP:PORT/blog/FUZZ.php`                                                                                              | Page Fuzzing             |
| `ffuf -w wordlist.txt:FUZZ -u http://SERVER_IP:PORT/FUZZ -recursion -recursion-depth 1 -e .php -v`                                                              | Recursive Fuzzing        |
| `ffuf -w wordlist.txt:FUZZ -u https://FUZZ.hackthebox.eu/`                                                                                                      | Sub-domain Fuzzing       |
| `ffuf -w wordlist.txt:FUZZ -u http://academy.htb:PORT/ -H 'Host: FUZZ.academy.htb' -fs xxx`                                                                     | VHost Fuzzing            |
| `ffuf -w wordlist.txt:FUZZ -u http://admin.academy.htb:PORT/admin/admin.php?FUZZ=key -fs xxx`                                                                   | Parameter Fuzzing - GET  |
| `ffuf -w wordlist.txt:FUZZ -u http://admin.academy.htb:PORT/admin/admin.php -X POST -d 'FUZZ=key' -H 'Content-Type: application/x-www-form-urlencoded' -fs xxx` | Parameter Fuzzing - POST |
| `ffuf -w ids.txt:FUZZ -u http://admin.academy.htb:PORT/admin/admin.php -X POST -d 'id=FUZZ' -H 'Content-Type: application/x-www-form-urlencoded' -fs xxx`       | Value Fuzzing            |


# drafts

| Option             | Description                                                                                                                                                               |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `-w`               | Wordlist to use.  <br>By default, assigns the wordlist to the `FUZZ` keyword; you can set custom keywords for different wordlists using `-w <wordlist>:<keyword>` syntax. |
| `-u`               | Target URL to fuzz.                                                                                                                                                       |
| `-X`               | HTTP method (`GET`, `POST`, etc.).                                                                                                                                        |
| `-H`               | Custom HTTP headers (`-H "<header>: <value>"`).                                                                                                                           |
| `-d`               | `POST` data (for `POST` requests).                                                                                                                                        |
| `-r`               | Follow redirects (default `false`).                                                                                                                                       |
| `recursion`        | Scan recursively; only one keyword supported, `FUZZ`; the URL has to end with the keyword (e.g., `-recursion -u https://example.com/FUZZ`).                               |
| `-recursion-depth` | Maximum recursion depth (default `6`).                                                                                                                                    |
| `-o`               | Output file path.                                                                                                                                                         |
| `-v`               | Verbose output.                                                                                                                                                           |
| `-s`               | Silent mode (suppresses banner).                                                                                                                                          |
| `-c`               | Colorful mode.                                                                                                                                                            |
| `-ic`              | Ignore comments in wordlists (starting with `#`).                                                                                                                         |
| `-e`               | Comma-separated list of file extensions to try; extends the `FUZZ` keyword.                                                                                               |
| `-ac`              | Automatically calibrate filtering options.                                                                                                                                |
| `-p`               | Specify delay between requests, or a range of random delay (in seconds); e.g., `-p 0.1` or `-p 0.1-2.0`.                                                                  |
| `-rate`            | Rate of requests per second (default `0`).                                                                                                                                |
| `-mc`              | Match HTTP status codes, or `all` (default `200`-`299`, `301`, `302`, `307`, `401`, `403`, `405`,`500`).                                                                  |
| `-fc`              | Filter out responses by HTTP status code.                                                                                                                                 |
| `-fs`              | Filter out responses by size in bytes (single value or range).                                                                                                            |
| `-fw`              | Filter out responses by number of words.                                                                                                                                  |
| `-fl`              | Filter out responses by number of lines.                                                                                                                                  |
| `-mr`              | Match a regular expression in the response.                                                                                                                               |