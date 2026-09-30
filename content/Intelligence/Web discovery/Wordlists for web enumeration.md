---
created: 2026-09-28
updated: 2026-09-30
tags:
  - web_hacking
  - intel
proofread: no
---
## Wordlists

>[!tip] Layer wordlists instead of relying on one. A quick pass with `common.txt` finds the obvious paths fast; a large list or a custom, context-derived list finds the rest.

## SecLists

> **[SecLists](https://github.com/danielmiessler/SecLists)** is the standard collection of security wordlists, bundling names for content discovery, subdomains, parameters, usernames, passwords, and fuzzing payloads in one repository.

- On Kali and Parrot, SecLists comes preinstalled, usually under `/usr/share/seclists` (also symlinked as `/usr/share/wordlists/seclists`). The paths in the tables below are relative to that directory.
- Find the exact location:

```bash
sudo find / -name "SecLists" -type d 2>/dev/null
```

- Install it manually if it is missing:

```bash
sudo apt install seclists
```

```bash
git clone https://github.com/danielmiessler/SecLists.git /usr/share/seclists
```

- Categories most relevant to discovery:
	- `Discovery/Web-Content/` — directories, files, parameters, and extensions.
	- `Discovery/DNS/` — subdomains and hostnames.
	- `Fuzzing/` — extensions and payload primitives.
	- `Usernames/`, `Passwords/` — credentials for login attacks (see [[🛠️ Custom wordlists and rules]]).

## Directory and file wordlists

| Wordlist                                              | Entries | Use                                                                 |
| :---------------------------------------------------- | :------ | :------------------------------------------------------------------ |
| `Discovery/Web-Content/common.txt`                    | ~4.7K   | Broad general-purpose list; the best first pass.                    |
| `Discovery/Web-Content/directory-list-2.3-medium.txt` | ~220K   | Large, directory-focused list for deeper sweeps.                    |
| `Discovery/Web-Content/raft-small-directories.txt`    | ~20K    | Directory-focused list for early enumeration.                       |
| `Discovery/Web-Content/raft-small-files.txt`          | ~11K    | File-focused counterpart to the directory list.                     |
| `Discovery/Web-Content/raft-large-directories.txt`    | ~62K    | Massive directory list compiled from many sources; thorough sweeps. |
| `Discovery/Web-Content/big.txt`                       | ~20K    | Common directory and file names.                                    |

>[!note] See [[Directory and file enumeration]] for how to drive these lists with `ffuf`, `feroxbuster`, and similar tools.

## Subdomain wordlists

| Wordlist                                          | Entries | Use                                                  |
| :------------------------------------------------ | :------ | :--------------------------------------------------- |
| `Discovery/DNS/subdomains-top1million-5000.txt`   | ~5K     | Fast first pass for common subdomains.               |
| `Discovery/DNS/subdomains-top1million-20000.txt`  | ~20K    | Balanced list for routine enumeration.               |
| `Discovery/DNS/subdomains-top1million-110000.txt` | ~110K   | Broader coverage when the small lists come up short. |
| `Discovery/DNS/bitquark-subdomains-top100000.txt` | ~100K   | Alternative list built from a different dataset.     |
| `Discovery/DNS/dns-Jhaddix.txt`                   | ~2M     | Very large list for exhaustive brute-forcing.        |

>[!note] See [[Subdomain enumeration]] for DNS brute-forcing and permutation workflows.

## Parameter and virtual host wordlists

- Parameter names for fuzzing hidden GET/POST parameters:

| Wordlist                                       | Entries | Use                                        |
| :--------------------------------------------- | :------ | :----------------------------------------- |
| `Discovery/Web-Content/burp-parameter-names.txt` | ~2.5K | Common parameter names, ranked by frequency. |

>[!note] See [[Fuzzing parameters]] for parameter discovery techniques.

- Virtual host enumeration reuses the subdomain wordlists above against the `Host` header rather than DNS. See [[Virtual host enumeration]].

## File extension wordlists

| Wordlist                                          | Entries | Use                                          |
| :------------------------------------------------ | :------ | :------------------------------------------- |
| `Discovery/Web-Content/web-extensions.txt`        | ~39     | Common web file extensions.                  |
| `Fuzzing/extensions-most-common.fuzz.txt`         | ~30     | Compact extension list for quick passes.     |

>[!tip] Try extensions that match the detected stack (e.g., `.php`, `.aspx`, `.jsp`) rather than every extension, to cut requests and noise.

## API endpoint wordlists

| Wordlist                                       | Use                                                     |
| :--------------------------------------------- | :------------------------------------------------------ |
| `Discovery/Web-Content/api/api-endpoints.txt`  | Common REST API paths.                                  |
| `Discovery/Web-Content/api/objects.txt`        | Common API object and resource names.                   |
| `Discovery/Web-Content/swagger.txt`            | Paths that expose Swagger/OpenAPI definitions.          |

## Dynamically updated wordlists

- Beyond `SecLists`, **[Assetnote wordlists](https://wordlists.assetnote.io/)** are regenerated from internet-wide scans, so they reflect paths that are actually in use today (e.g., `httparchive_php_2024.txt`, `swagger-apis.txt`).
- **[commonspeak2](https://github.com/assetnote/commonspeak2)** generates wordlists from publicly available datasets such as Common Crawl and GitHub archives.

## Generating custom wordlists

- The most effective lists are built from the target itself. After a broad pass with a generic list, generate a context-specific wordlist and fuzz again on top of the initial results.
- **[CeWL](https://github.com/digininja/CeWL)** spiders a site and extracts words from its content to seed a custom list:

```bash
cewl -d 2 -m 5 -w custom-words.txt https://example.com
```

>[!note] See [[🛠️ Custom wordlists and rules]] for the full custom-generation and rule-based mutation workflow (CeWL, Crunch, Hashcat and John rules), and for username, password, and default-credential wordlists.

## References and further reading

- [`SecLists`](https://github.com/danielmiessler/SecLists)
- [`Assetnote wordlists`](https://wordlists.assetnote.io/)
- [`commonspeak2`](https://github.com/assetnote/commonspeak2)
- [`CeWL`](https://github.com/digininja/CeWL)
