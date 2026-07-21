---
created: 2026-07-18
tags:
  - recon
  - web_hacking
---
## HTTP parameter fuzzing

>**HTTP parameter fuzzing** is the process of **automatically injecting large sets of data into HTTP parameters** (`GET`, `POST`, headers, cookies, etc.) to observe how the server processes inputs and potentially discover unexpected or vulnerable behavior.

Parameter fuzzing is helpful in finding vulnerabilities like SQL injection, XSS, command injection, parameter pollution, logic flaws, and more.

Types of HTTP parameters you can test include:

- **URL query parameters** (`GET` parameters, e.g., `?id=FUZZ`)
- **HTTP body parameters** (`POST`, `PUT`, `PATCH`, e.g., `username=FUZZ&password=pass`)
- **HTTP headers** (`X-Forwarded-For: FUZZ`)
- **Cookies**
- **URL path parameters** (RESTful APIs)

Parameter fuzzing follows a logical two-phase approach:
1. Fuzz parameter names
2. Fuzz parameter values

>[!note] This article uses `ffuf` as fuzzing tool; see [[྾_ffuf]].
## Fuzzing HTTP `GET` parameters

The general strategy is to first fuzz parameter names with an arbitrary value (such as `x` or `1`, e.g., `example.com/?FUZZ=x`), and then values of discovered parameters. 

Most likely, you will use response size to differentiate between valid parameter names and values. The majority of the responses will have the same size, but responses to requests with valid parameters will likely stand out. To filter out responses of specific size, you can use the `-fs` option in `ffuf`.

- Fuzz `GET` parameter names:

```bash
ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/burp-parameter-names.txt:FUZZ \
     -u http://example/admin?FUZZ=x \
     -fs xxx \
     -c -ic
```

- You can use the `-ac` flag to automatically calibrate filters:

```bash
ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/burp-parameter-names.txt:FUZZ \
     -u http://example/admin?FUZZ=x \
     -c -ic -ac
```

>[!note] See [[྾_ffuf]].

Wordlists for fuzzing common parameter names from [`SecLists`](https://github.com/danielmiessler/SecLists):
- [`Discovery/Web-Content/burp-parameter-names.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/burp-parameter-names.txt)
- [`Discovery/Web-Content/common.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/common.txt)
- [`Discovery/Web-Content/url-params_from-top-55-most-popular-apps.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/url-params_from-top-55-most-popular-apps.txt)
- [`Discovery/Web-Content/uri-from-top-55-most-popular-apps.txt`](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/uri-from-top-55-most-popular-apps.txt)

- To fuzz parameter values:

```bash
ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt:FUZZ \
	 -u http://example/admin?parameter=FUZZ \
	 -fs xxx \
	 -c -ic
```

Parameter values can be anything:
- Numbers
- Strings
- Encoded values
- etc.

For parameter value wordlists, refer to:
- [`SecLists/Fuzzing`](https://github.com/danielmiessler/SecLists/tree/master/Fuzzing) 
- [`fuzzdb`](https://github.com/fuzzdb-project/fuzzdb)

>[!example]+ Example: Generating fuzzing wordlists
>You can generate custom wordlists, such as numeric sequences with Python or Bash one-liners. For example, the following code generates a newline-separated list of numbers from `1` to `1000` and saves it to the `ids.txt` file:
>```bash
>for i in $(seq 1 1000); do echo $i >> ids.txt; done
>```
>This generates a newline-separated list of  numbers from `1` to `1000`.

- It's likely to be less effective, but you can also fuzz both parameter names and values in a single `ffuf` run:

```bash
ffuf -w param_wordlist.txt:PARAM -w value_wordlist.txt:VALUE -u http://example/admin/admin.php?PARAM=VALUE -fs xxx -c
```

This will help you deal with situations when the application only reacts to a parameter when it's set to a correct value. However, such enumeration will take much longer (the number of entries `ffuf` needs to try is a multiplication of entries in both wordlists).

>[!tip] Use `curl` and `curl -I` to validate your findings.
## Fuzzing HTTP `POST` parameters

- Fuzz `POST` parameter names:

```bash
ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/burp-parameter-names.txt:FUZZ \
     -u http://example/admin \
     -X POST \
     -d 'FUZZ=x' \
     -H 'Content-Type: application/x-www-form-urlencoded' \
     -fs xxx \
     -c -ic
```

- Fuzz `POST` parameter values:

```bash
ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt:FUZZ \
     -u http://example/admin \
     -X POST \
     -d 'parameter=FUZZ' \
     -H 'Content-Type: application/x-www-form-urlencoded' \
     -fs xxx \
     -c -ic
```

>[!tip] Use `curl` and `curl -I` to validate your findings.

>[!tip] Inspect application responses for:
> - Error messages
> - Stack traces
> - Redirects
> - Unexpected behavior
> - Reflected values
## Automated tools
### ParamSpider  

>[`ParamSpider`](https://github.com/devanshbatham/ParamSpider) is a command-line tool that can fetch HTTP `GET` parameter names from URLs found in Wayback archives. It can also filter out parameters not likely to be useful in security tests.

```bash
paramspider -d example.com
```

>[!important] ParamSpider does not send requests to the target server or set values; it only extracts parameter names from existing URLs. It can be considered passive reconnaissance.

### Arjun

>[`Arjun`](https://github.com/s0md3v/Arjun) is a command-line tool specifically designed to discover `GET` and `POST` HTTP parameters in a web application. 

Arjun uses a large, curated wordlist to enumerate parameters and detect valid ones based on response differences. 

>[!note] Arjun uses a random string as a value for each parameter.

```bash
arjun -u http://example.com/api
```

## Fuzzing HTTP headers

- To fuzz HTTP headers:

```bash
ffuf -w wordlist.txt -H "X-FUZZ: test" -u "https://example.com/api"
```

- To fuzz HTTP header values:

```bash
ffuf -w wordlist.txt -H "Header: FUZZ" -u "http://example.com/api"
```

- To fuzz cookie values:

```bash
ffuf -w wordlist.txt -b "PHPSESSID=FUZZ" -u "https://example.com/api"
```
