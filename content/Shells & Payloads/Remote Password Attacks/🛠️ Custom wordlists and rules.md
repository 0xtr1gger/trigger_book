---
created: 2026-09-04
updated: 2026-10-09
tags:
  - password_cracking
status: slop
---

>[!abstract]+ **Scope**: Building and mutating password wordlists for brute-force and credential attacks; username wordlists and permutation tools; custom wordlist generators (CUPP, CeWL, Crunch); keyboard walk and PRINCE-based generation; Hashcat and John the Ripper rule-based mutations; filtering wordlists to match password policies.

## Username wordlists

| Wordlist | Default path | Entries |
|---|---|---|
| `top-usernames-shortlist.txt` | `/usr/share/seclists/Usernames/top-usernames-shortlist.txt` | `17` |
| `xato-net-10-million-usernames.txt` | `/usr/share/seclists/Usernames/xato-net-10-million-usernames.txt` | `8.3M` |
| `Names/names.txt` | `/usr/share/seclists/Usernames/Names/names.txt` | `10K` |
| `cirt-default-usernames.txt` | `/usr/share/seclists/Usernames/cirt-default-usernames.txt` | `827` |

### username-anarchy

[username-anarchy](https://github.com/urbanadventurer/username-anarchy) generates username permutations from first and last names. Common formats include `jsmith`, `jane.smith`, `j.smith`, `smithj`, and `jane_smith`.

- Generate permutations for a single name:

```bash
username-anarchy Jane Smith
```

- Generate with a specific format:

```bash
username-anarchy -f first.last Jane Smith
```

- Generate in bulk from a CSV file:

```bash
username-anarchy --input-file names.csv --select-format first.last
```

## Password wordlists

| Wordlist | Default path | Entries |
|---|---|---|
| `rockyou.txt` | `/usr/share/wordlists/rockyou.txt` | `14M` |
| `xato-net-10-million-passwords.txt` | `/usr/share/seclists/Passwords/xato-net-10-million-passwords.txt` | `10M` |
| `10-million-password-list-top-100000.txt` | `/usr/share/seclists/Passwords/Common-Credentials/10-million-password-list-top-100000.txt` | `100K` |
| `darkweb2017-top10000.txt` | `/usr/share/seclists/Passwords/darkweb2017-top10000.txt` | `10K` |
| `probable-v2-top1575.txt` | `/usr/share/seclists/Passwords/probable-v2-top1575.txt` | `1.5K` |
| `default-passwords.txt` | `/usr/share/seclists/Passwords/Default-Credentials/default-passwords.txt` | `~1K` |
| `500-worst-passwords.txt` | `/usr/share/seclists/Passwords/Common-Credentials/500-worst-passwords.txt` | `500` |
| `Keyboard-Combinations.txt` | `/usr/share/seclists/Passwords/Keyboard-Combinations.txt` | `~500` |

Guidance on choosing wordlists:
- Target specific audiences. Personal information creates strong custom wordlists. Categories include names, birthdates, phone numbers, addresses, and pet names.
- Combine lists.

>[!tip]+
> You'll often get better results by combining a small high-quality list with mutations (e.g., `Summer2024!`, `CompanyName123`).

## Default credentials

- [CIRT.net](https://cirt.net/passwords)
- [default-password.info](https://default-password.info/)
- [Datarecovery.com](https://datarecovery.com/rd/default-passwords/)
- [SecLists Default-Credentials](https://github.com/danielmiessler/SecLists/tree/master/Passwords/Default-Credentials)
- [ihebski/DefaultCreds-cheat-sheet](https://github.com/ihebski/DefaultCreds-cheat-sheet)
- [defaulty.io](https://defaulty.io/search)

Service-specific default credential lists in SecLists:
- `avaya_defaultpasslist.txt`
- `db2-betterdefaultpasslist.txt`
- `ftp-betterdefaultpasslist.txt`
- `mssql-betterdefaultpasslist.txt`
- `mysql-betterdefaultpasslist.txt`
- `oracle-betterdefaultpasslist.txt`
- `postgres-betterdefaultpasslist.txt`
- `ssh-betterdefaultpasslist.txt`
- `telnet-betterdefaultpasslist.txt`
- `tomcat-betterdefaultpasslist.txt`
- `vnc-betterdefaultpasslist.txt`
- `windows-betterdefaultpasslist.txt`

## Generating custom wordlists

### CUPP

[CUPP](https://github.com/Mebus/cupp) (Common User Password Profiler) generates tailored password wordlists based on target information.

- Information useful for targeted wordlist generation:
	- Name, nickname, initials of the target, their family members, loved ones, pets.
	- Birthdays of the target, their family members (most commonly children), loved ones.
	- Anniversaries, wedding dates, or other memorable dates.
	- Phone numbers, addresses.
	- Company or organization names.
	- Common words: God, love, money, password.
	- Favorite food, hobby, sports team.
	- Memorable places or events.

- Start CUPP in interactive mode:

```bash
python3 cupp.py -i
```

| Option | Description |
|---|---|
| `-h`, `--help` | Display help |
| `-i`, `--interactive` | Interactive mode |
| `-w` | Use this option to profile a custom wordlist |
| `-l` | Choose a wordlist to base the generation on |
| `-a` | Parse default usernames and passwords from the Alecto DB |

>[!example]-
> ```bash
> cupp -i
> ```
> ```
>     cupp.py!                 # Common
>       \                     # User
>        \   ,__,             # Passwords
>         \  (oo)____         # Profiler
>            (__)    )\   
>               ||--|| *      [ Muris Kurgas | j0rgan@remote-exploit.org ]
>                             [ Mebus | https://github.com/Mebus/]
> 
> [+] Insert the information about the victim to make a dictionary
> [+] If you don't know all the info, just hit enter when asked! ;)
> 
> First Name: Jane
> Surname: Smith
> Nickname: Janey
> Birthdate (DDMMYYYY): 11121990
> 
> Partners) name: Jim
> Partners) nickname: Jimbo
> Partners) birthdate (DDMMYYYY): 12121990
> 
> Child's name: 
> Child's nickname: 
> Child's birthdate (DDMMYYYY): 
> 
> Pet's name: Spot
> Company name: AHI
> 
> Do you want to add some key words about the victim? Y/[N]: Y
> Please enter the words, separated by comma. [i.e. hacker,juice,black], spaces will be removed: hackers, pizza, golf, horses, blue
> Do you want to add special chars at the end of words? Y/[N]: Y
> Do you want to add some random numbers at the end of words? Y/[N]:Y
> Leet mode? (i.e. leet = 1337) Y/[N]: Y
> 
> [+] Now making a dictionary...
> [+] Sorting list and removing duplicates...
> [+] Saving dictionary to jane.txt, counting 54478 words.
> [+] Now load your pistolero with jane.txt and shoot! Good luck!
> ```

- Once you've generated a wordlist, match it to the target platform's password policy. For example, if the policy requires 6+ characters, uppercase, lowercase, a number, and two special characters, filter with `grep`:

```bash
grep -E '^.{6,}$' jane.txt | grep -E '[A-Z]' | grep -E '[a-z]' | grep -E '[0-9]' | grep -E '([!@#$%^&*].*){2,}' > jane_filtered.txt
```

>[!example]-
> ```bash
> grep -E '^.{6,}$' jane.txt | grep -E '[A-Z]' | grep -E '[a-z]' | grep -E '[0-9]' | grep -E '([!@#$%^&*].*){2,}' > jane_filtered.txt
> ```
> ```bash
> wc -l jane_filtered.txt
> 8604 jane_filtered.txt
> ```
> ```bash
> hydra -L usernames.txt -P jane_filtered.txt 94.237.122.241 -s 53543 -f http-post-form "/:username=^USER^&password=^PASS^:Invalid credentials"
> ...
> Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2025-09-04 03:50:56
> [DATA] max 16 tasks per 1 server, overall 16 tasks, 120456 login tries (l:14/p:8604), ~7529 tries per task
> [DATA] attacking http-post-form://94.237.122.241:53543/:username=^USER^&password=^PASS^:Invalid credentials
> [53543][http-post-form] host: 94.237.122.241   login: jane   password: 3n4J!!
> [STATUS] attack finished for 94.237.122.241 (valid pair found)
> 1 of 1 target successfully completed, 1 valid password found
> Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2025-09-04 03:50:57
> ```

### CeWL

[CeWL](https://github.com/digininja/CeWL) spiders a target URL and extracts words to create a custom wordlist.

- Spider a website to depth `2` and minimum word length `5`:

```bash
cewl -d 2 -m 5 -w wordlist.txt https://example.com
```

- Include email addresses:

```bash
cewl -e -w emails.txt https://example.com
```

| Option | Description |
|---|---|
| `-d`, `--depth` | Depth to spider to (default `2`). |
| `-m`, `--min_word_length` | Minimum word length (default `3`). |
| `-o`, `--offsite` | Visit other websites. |
| `--exclude` | A file with a list of paths to exclude from crawling. |
| `--allowed` | A regex pattern that a path must match to be followed. |
| `-w`, `--write` | Specify the file to write the output to. |
| `-u`, `--ua` | User agent to send in requests. |
| `-n`, `--no-words` | Don't output the wordlist. |
| `--lowercase` | Lowercase all parsed words. |
| `--with-numbers` | Accept words with numbers and just letters. |
| `--convert-umlauts` | Convert common ISO-8859-1 (Latin 1) umlauts. |
| `-e`, `--email` | Include email addresses. |
| `--email_file` | Specify output file for email addresses. |
| `-c`, `--count` | Show the count for each word found. |
| `-v`, `--verbose` | Be verbose. |
| `--debug` | Display extra debug information. |
| `--auth_type` | Digest or basic. |
| `--auth_user` | Authentication username. |
| `--auth_pass` | Authentication password. |
| `-H`, `--header` | HTTP headers to use (format: `-H header1:value -H header2:value`). |

>[!example]-
> - Spider a website to depth `4` and save words with minimum word length `6` in lowercase:
> ```bash
> cewl https://www.example.com -d 4 -m 6 --lowercase -w example.wordlist
> ```
> 
> ```bash
> cat example.wordlist | wc -l
> ```
> 
> ```
> 326
> ```
> 
> ```bash
> head example.wordlist
> ```
> 
> ```
> example
> contact
> navigation
> services
> offices
> career
> toggle
> navbar
> protected
> wordfence
> ```

### Crunch

[Crunch](https://sourceforge.net/projects/crunch-wordlist/) creates wordlists by generating all permutations of specified character sets.

```bash
crunch <minimum_length> <maximum_length> <charset> -t <pattern> -o <output_file>
```

- Generate words of 4 to 8 characters:

```bash
crunch 4 8 -o wordlist.txt
```

- Generate numeric codes of 4 characters:

```bash
crunch 4 4 0123456789 -o wordlist.txt
```

- Generate words of 6 to 8 characters using letters, numbers, and symbols:

```bash
crunch 6 8 abcdefghijklmnopqrstuvwxyz1234567890!@ -o wordlist.txt
```

- Generate words of 19 characters that match a specific pattern:

```bash
crunch 19 19 -t SECUREPASSWORD!20%% -o wordlist.txt
```

- Specify repetition count using `-d`:

```bash
crunch 12 12 -t 11120905@@@@ -d 1 -w wordlist.txt
```

- Pipe output directly to Aircrack-ng:

```bash
crunch 8 8 abcdefghijklmnopqrstuvwxyz | aircrack-ng -w - -b 00:11:22:33:44:55 handshake.cap
```

>[!note]
> `@` denotes lowercase letters, `,` denotes uppercase letters, `%` denotes digits, and `^` denotes special characters.

## Generating keyboard walk wordlists

[kwprocessor](https://github.com/hashcat/kwprocessor) generates wordlists based on keyboard walk patterns like `qwerty` or `asdfghjkl`.

- Build basic keyboard walks:

```bash
kwp basechars/full.base keymaps/en-us.keymap routes/2-to-16-max-3-direction-changes.route
```

- Export walks to a file:

```bash
kwp basechars/full.base keymaps/en-us.keymap routes/2-to-10-max-3-direction-changes.route -o keywalks.txt
```

## Generating PRINCE-based wordlists

[princeprocessor](https://github.com/hashcat/princeprocessor) generates chains of combined words using the PRobability INfinite Chained Elements algorithm.

- Create chains of combined words:

```bash
pp64 < wordlist.txt
```

- Limit output string length:

```bash
pp64 --pw-min=8 --pw-max=16 < wordlist.txt
```

- Limit element count (words per chain):

```bash
pp64 --elem-cnt-min=2 --elem-cnt-max=3 < wordlist.txt > prince_output.txt
```

- Pipe output directly to Hashcat:

```bash
pp64 < wordlist.txt | hashcat -m 0 hashes.txt
```

## Mutating wordlists with rules

### Hashcat rule-based attacks

- Apply rules to a wordlist using the `--stdout` flag:

```bash
hashcat --force <wordlist> -r /usr/share/hashcat/rules/best64.rule --stdout | sort -u > hashcat_words.txt
```

#### Hashcat rule functions

| Function | Description | Example input | Example output |
|---|---|---|---|
| `:` | Do nothing (passthrough) | `password` | `password` |
| `l` | Lowercase all | `PassWord` | `password` |
| `u` | Uppercase all | `password` | `PASSWORD` |
| `c` | Capitalize first, lower rest | `password` | `Password` |
| `C` | Lowercase first, upper rest | `Password` | `pASSWORD` |
| `t` | Toggle case of all chars | `PassWord` | `pASSwORD` |
| `$X` | Append character X | `password` (`$!`) | `password!` |
| `^X` | Prepend character X | `password` (`^@`) | `@password` |
| `r` | Reverse | `password` | `drowssap` |
| `d` | Duplicate word | `password` | `passwordpassword` |
| `sXY` | Replace X with Y | `password` (`so0`) | `passw0rd` |
| `@X` | Remove all X | `password` (`@s`) | `paword` |
| `[` | Remove first char | `password` | `assword` |
| `]` | Remove last char | `password` | `passwor` |

#### Built-in Hashcat rule files

Path: `/usr/share/hashcat/rules/`

| Rule file | Description |
|---|---|
| `best64.rule` | Most effective 64 rules — best starting point |
| `rockyou-30000.rule` | 30K rules derived from RockYou analysis |
| `d3ad0ne.rule` | Large aggressive ruleset |
| `dive.rule` | Very large ruleset (deep mutations) |
| `toggles1-5.rule` | Case toggling rules |
| `leetspeak.rule` | Leet substitutions |
| `InsidePro-PasswordsPro.rule` | Rules from InsidePro |
| `OneRuleToRuleThemAll.rule` | Community meta-ruleset |

### John the Ripper rules

- Apply rules to a wordlist:

```bash
john --wordlist=wordlist.txt --rules=best64 --stdout > mutated.txt
```

- Generate mutations and save them:

```bash
john --wordlist=wordlist.txt --rules --stdout | sort -u > mutated.txt
```

- Custom rule syntax basics:
  - `l`: Lowercase.
  - `u`: Uppercase.
  - `c`: Capitalize.
  - `$X`: Append character X.
  - `^X`: Prepend character X.
  - `Az"STRING"`: Append string.
  - `A0"STRING"`: Prepend string.
  - `sXY`: Replace X with Y.
  - `[0-9]`: Reference positions.

Common rule sections in `john.conf` include `[List.Rules:Wordlist]`, `[List.Rules:best64]`, and `[List.Rules:KoreLogic]`.

## Filtering wordlists to match password policies

Filter custom wordlists to match a target application's password policy.

- Match a policy requiring 6 characters, uppercase, lowercase, numbers, and two special characters:

```bash
grep -E '^.{6,}$' initial_wordlist.txt | grep -E '[A-Z]' | grep -E '[a-z]' | grep -E '[0-9]' | grep -E '([!@#$%^&*].*){2,}' > filtered_wordlist.txt
```

- Use Perl-compatible regular expressions:

```bash
grep -P '^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*]).{8,}$' wordlist.txt > filtered_wordlist.txt
```

- Use sed for quick substitutions:

```bash
sed -i 's/a/@/g' wordlist.txt
```

>[!note]
> Related topics: [[Hashcat]], [[🛠️ Network protocols]], [[🛠️ Password cracking]]

## References and further reading

- [CUPP GitHub](https://github.com/Mebus/cupp)
- [CeWL GitHub](https://github.com/digininja/CeWL)
- [Crunch](https://sourceforge.net/projects/crunch-wordlist/)
- [username-anarchy](https://github.com/urbanadventurer/username-anarchy)
- [kwprocessor](https://github.com/hashcat/kwprocessor)
- [princeprocessor](https://github.com/hashcat/princeprocessor)
- [hashcat-utils](https://github.com/hashcat/hashcat-utils)
- [Hashcat rule-based attack](https://hashcat.net/wiki/doku.php?id=rule_based_attack)
- [SecLists](https://github.com/danielmiessler/SecLists)
- [OWASP Testing for Default Credentials](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/04-Authentication_Testing/02-Testing_for_Default_Credentials)
- [The Hacker Recipes default credentials](https://www.thehacker.recipes/web/config/default-credentials)
- [Hacking Articles CUPP guide](https://www.hackingarticles.in/comprehensive-guide-on-cupp-a-wordlist-generating-tool/)
