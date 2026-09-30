---
created: 2026-07-18
updated: 2026-09-30
tags:
  - web_hacking
  - intel
status: complete
proofread: yes
---
## HTTP parameter fuzzing

>**HTTP parameter fuzzing** is the process of **automatically injecting large sets of data into HTTP parameters** (`GET`, `POST`, headers, cookies, etc.) to observe how the server processes inputs and to discover unexpected or vulnerable behavior.

- Applications frequently accept parameters that are never referenced in the UI, like debug switches, feature flags, or legacy parameters. 
- These hidden parameters are often validated less thoroughly or not validated at all, but may still influence application behavior.
- Parameters worth testing:
	- URL query parameters (HTTP `GET` parameters, e.g., `?id=FUZZ`)
	- HTTP body parameters (`POST`, `PUT`, `PATCH`, e.g., `username=FUZZ&password=pass`)
	- **HTTP headers** (e.g., `X-Forwarded-For: FUZZ`)
	- Cookies
     - HTTP path parameters (RESTful APIs, e.g., `/api/user/FUZZ`)

- The general approach is as follows:
     1. Fuzz parameter names with a fixed, arbitrary value (e.g., `x` or `1`) to find parameters the application recognizes.
     2. Fuzz the values of the discovered parameters and observe application behavior.

>[!note] Most examples in this guide use `ffuf`. See [[🛠️ ffuf]].

>[!tip]+
> - To fuzz both parameter names and values in a single `ffuf` run (pitchfork-style attack):
> 
> ```bash
> ffuf -w param_wordlist.txt:PARAM -w value_wordlist.txt:VALUE -u http://example.com/admin/admin.php?PARAM=VALUE -fs xxx -c
> ```
> 
> - This generates many times more requests, but can discover parameters that the application reacts to only when they are set to a valid value. 

>[!tip]+
>- If possible, enumerate parameters under different access levels — anonymous, low-privileged user, administrator.

## Wordlists

>[!note] See [[Wordlists for web enumeration]].

- Parameter *name* wordlists from [`SecLists`](https://github.com/danielmiessler/SecLists):
	- [`Discovery/Web-Content/burp-parameter-names.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/burp-parameter-names.txt) — the standard starting list for parameter names.
	- [`Discovery/Web-Content/url-params_from-top-55-most-popular-apps.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/url-params_from-top-55-most-popular-apps.txt) — parameter names observed across popular applications.

- Parameter *value* wordlists depend on what is being tested (injection payloads, numeric IDs, encoded strings):
	- [`SecLists/Fuzzing`](https://github.com/danielmiessler/SecLists/tree/master/Fuzzing)
     - [`IntruderPayloads (BurpSuite Pro built-in wordlists)`](https://github.com/1N3/IntruderPayloads)
	- [`fuzzdb`](https://github.com/fuzzdb-project/fuzzdb)

- Generate a numeric wordlist:

```bash
for i in $(seq 1 1000); do echo $i >> ids.txt; done
```

>[!info] This command generates a newline-separated list of numbers from `1` to `1000` and writes them into `ids.txt`.

## Identifying valid parameters

- A request with an unknown parameter and one with a known parameter usually return the same `200 OK`, but you can often still distinguish valid parameters by differences in the response content or timing relative to a baseline.

- During fuzzing, most responses will share the same size. To identify interesting parameters, you can either filter out constant size (in `ffuf`, `-fs`), or let `ffuf` calibrate the baseline automatically (`-ac`):

```bash
ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/burp-parameter-names.txt:FUZZ \
     -u http://example.com/admin?FUZZ=x \
     -fs 4242 \
     -c -ic
```

```bash
ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/burp-parameter-names.txt:FUZZ \
     -u http://example.com/admin?FUZZ=x \
     -c -ic -ac
```

- To filter based on timing differences:


>[!note] See [[🛠️ ffuf]].


## Fuzzing `GET` parameters

- Fuzz `GET` parameter names with an arbitrary value (such as `x` or `1`):

```bash
ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/burp-parameter-names.txt:FUZZ \
     -u http://example.com/admin?FUZZ=x \
     -fs 4242 \
     -c -ic
```

- Once a valid parameter is found, fuzz its values:

```bash
ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt:FUZZ \
     -u http://example.com/admin?parameter=FUZZ \
     -fs 4242 \
     -c -ic
```

- Fuzz both names and values in a single run when the application only reacts to a parameter set to a specific value:

```bash
ffuf -w param_wordlist.txt:PARAM \
     -w value_wordlist.txt:VALUE \
     -u http://example.com/admin/admin.php?PARAM=VALUE \
     -fs 4242 \
     -c -ic
```

>[!warning] Fuzzing names and values together multiplies request volume: `ffuf` tries the product of both wordlists. Reserve this for cases where single-phase fuzzing misses a value-gated parameter.

## Fuzzing `POST` parameters

- Fuzz `POST` parameter names:

```bash
ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/burp-parameter-names.txt:FUZZ \
     -u http://example.com/admin \
     -X POST \
     -d 'FUZZ=x' \
     -H 'Content-Type: application/x-www-form-urlencoded' \
     -fs 4242 \
     -c -ic
```

- Fuzz `POST` parameter values:

```bash
ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt:FUZZ \
     -u http://example.com/admin \
     -X POST \
     -d 'parameter=FUZZ' \
     -H 'Content-Type: application/x-www-form-urlencoded' \
     -fs 4242 \
     -c -ic
```

>[!tip] For JSON APIs, set `-H 'Content-Type: application/json'` and place the `FUZZ` keyword inside the JSON body, e.g., `-d '{"FUZZ":"x"}'`.

>[!note] APIs frequently accept parameters absent from the web UI. See [[API testing]] and [[GraphQL attacks]].

## Fuzzing HTTP headers and cookies

- Fuzz HTTP header names:

```bash
ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/burp-parameter-names.txt:FUZZ \
     -H "FUZZ: test" \
     -u https://example.com/
```

- Fuzz HTTP header values:

```bash
ffuf -w wordlist.txt:FUZZ \
     -H "X-Forwarded-For: FUZZ" \
     -u https://example.com/
```

- Fuzz cookie values:

```bash
ffuf -w wordlist.txt:FUZZ \
     -b "PHPSESSID=FUZZ" \
     -u https://example.com/
```

>[!tip] Headers such as `X-Forwarded-For`, `X-Original-URL`, and `X-Forwarded-Host` are common targets for access control bypasses and host-header attacks.

## Automated tools

- Dedicated tools automate parameter discovery with curated wordlists and built-in response analysis:

| Tool | Description |
| :--- | :--- |
| [`Arjun`](https://github.com/s0md3v/Arjun) | Discover `GET`, `POST`, JSON, and XML parameters using a large built-in wordlist. |
| [`ParamSpider`](https://github.com/devanshbatham/ParamSpider) | Mine parameter names from URLs archived in the Wayback Machine. |
| [`x8`](https://github.com/Sh1Yo/x8) | Discover hidden parameters through response-difference analysis, written in Rust. |

### Arjun

>[`Arjun`](https://github.com/s0md3v/Arjun) is a command-line tool designed to discover valid `GET` and `POST` HTTP parameters in a web application.

- Arjun submits parameters from a large, curated wordlist and detects valid ones based on differences in the responses.

```bash
arjun -u http://example.com/api
```

>[!note] Arjun sends a random string as the value for each parameter, so it detects parameters that are recognized regardless of their expected value.

### ParamSpider

>[`ParamSpider`](https://github.com/devanshbatham/ParamSpider) is a command-line tool that extracts `GET` parameter names from URLs found in web archives, and filters out parameters unlikely to be useful for security testing.

```bash
paramspider -d example.com
```

>[!important] ParamSpider does not send requests to the target or set values; it only extracts parameter names from previously archived URLs. It is a passive reconnaissance technique. See [[🛠️ Searching the web#Searching web archives]].

## Analyzing responses

- Inspect application responses for signals that a parameter was recognized:
	- Reflected values
	- Error messages and stack traces
	- Redirects
	- Changes in response size, words, or lines
	- Unexpected behavior or timing differences

- Validate findings manually using `curl` before deeper testing:

```bash
curl -s "http://example.com/admin?parameter=x"
```

```bash
curl -I "http://example.com/admin?parameter=x"
```

- Depending on the findings, test for vulnerabilities. Pay attention to [[🛠️ Injection vulnerabilities|injection vulnerabilities]] like SQL injection, OS command injection, and XSS; [[🛠️ Authentication and authorization vulnerabilities|authorization vulnerabilities]] such as IDOR; caching flaws like [[Web Cache Deception]] and [[🛠️ Web Cache Poisoning]]; information disclosure vulnerabilities, and others.

>[!note] See [[Web discovery and enumeration methodology]].