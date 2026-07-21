---
created: 2026-07-17
tags:
  - recon
  - web_hacking
status: incomplete
---
## Visual recon

>**Visual reconnaissance** involves automatically capturing screenshots of rendered web applications or services across hundreds or thousands of hosts.

- Screenshots are helpful in building a list of primary targets for the security assessment.
- Unlike classic port scanning (e.g., with Nmap) or basic HTTP probing (e.g., `curl`, `httpx`, `ffuf`), visual recon goes a step further:
	
	- Rapid triage and prioritization
		- Instead of manually checking each URL or sifting through raw HTML, you quickly scan a report of screenshots to identify interesting targets: login panels, admin interfaces, forgotten development servers, custom web applications, etc.
		- This approach is far faster and more intuitive than dealing with piles of textual data.
	
	- Filter out error or empty pages
		- Even if an endpoint appears to be alive, and the response is `200`, you can't now for sure what's there until you inspect the HTML or render the page. Web applications may implement custom error pages.
	
	- Recognize technology stacks
		- It might be much more easy to fingerprint the technology stack of a target application using visual cues. You just know how WordPress, Tomcat, Jenkins, Grafana *look like*. It's more convenient for a human brain to work with pictures and colors rather than tags and attributes.

- Most commonly used tools for automated visual recon:
	- [`EyeWitness`](https://github.com/RedSiege/EyeWitness) — Uses Selenium WebDriver to control a headless browser. Generates categorized HTML reports.

	```bash
	eyewitness --web -f urls.txt -d example.com
	```

	- [`Aquatone`](https://github.com/michenriksen/aquatone) — Written in Go, uses headless Chrome/Chromium.

	
	```bash
	cat subdomains.txt | aquatone -out ./aquatone_report
	```


	- [`httpx`](https://github.com/projectdiscovery/httpx) — Among another things, can take screenshots using a local headless browser.

	```bash
	httpx -l interesting.txt -ss -system-chrome -o screenshots/
	```

	- [`gowitness`](https://github.com/sensepost/gowitness) —


>[!interesting]+ Headless browsers
> These tools use a **headless browser** to simulate a user opening a URL.
> 
>>A **[headless browser](https://en.wikipedia.org/wiki/Headless_browser)** is a web browser without a GUI (Graphical User Interface).
> 
> A headless browser can execute JavaScript, parse CSS, render DOM, handle client-side redirects, just like a regular browser. The tool then captures a screenshot of the rendered page and saves it along with metadata like page title, HTTP response headers, cookies, etc.
## EyeWitness

>[EyeWitness](https://github.com/RedSiege/EyeWitness), written in Python, uses the Selenium WebDriver API to control a headless browser, Chrome or Chromium. It takes a list of URLs or hosts, navigates to each, and captures screenshots and metadata.

- Key features:
	- Works on Windows, Linux, and macOS.
	- Automatically adjusts resource consumption based to system capabilities.
	- Support for configuration files.
	- Pre-flight URL validation checks.
	- Progress tracking with ETA (Estimated Time of Arrival).
	- Support for multiple input formats (text files, Nmap XML, Nessus XML).
	- Isolated virtual environments.

>[!note]- Installation
>- Debian-based:
>```bash
>sudo apt install eyewitness
>```
>- From source:
>```bash
>git clone https://github.com/RedSiege/EyeWitness && \
>cd EyeWitness/setup && \
>sudo ./setup.sh && \
>cd ..
>```
>

- Scan a list of URLs and save results into the `example.com_eyewitness` directory:

```bash
eyewitness --web -f urls.txt -d example.com_eyewitness
```

- Take screenshots of targets specified in an Nmap XML file:

```bash
eyewitness --web -x web_discovery.xml -d example.com_eyewitness
```

| Option            | Description                                              |
| ----------------- | -------------------------------------------------------- |
| `--web`           | Take screenshots using Selenium.                         |
| `-f`              | File with a list of URLs to capture (newline-separated). |
| `-x`              | Nmap XML or `.Nessus` file.                              |
| `-d`              | Output directory for screenshots.                        |
| `--prepend-https` | Prepend `http://` and `https://` to URLs without either. |

- Once finished, EyeWitness generates an HTML report, saves it into the directory with screenshots, and prompts if you want to open it right away.
### Options cheat sheet

| Option            | Description                                 |
| ----------------- | ------------------------------------------- |
| `--web`           | Take screenshots using Selenium.            |
| `-d`              | Output directory for screenshots.           |
| `--result`        | Number of hosts per page or report.         |
| `--no-prompt`     | Don't prompt to open the report.            |
| `--show-selenium` | Show display for selenium.                  |
| `--no-dns`        | Skip DNS resolution.                        |
| `--resolve`       | Resolve IP addresses/hostnames for targets. |
| `--proxy-ip`      | Proxy IP address.                           |
| `--proxy-type`    | Proxy type (SOCKS5 or HTTP).                |

- Targets:

| Option                                    | Description                                                                  |
| ----------------------------------------- | ---------------------------------------------------------------------------- |
| `-f`                                      | File with a list of URLs to capture (newline-separated).                     |
| `-x`                                      | Nmap XML or `.Nessus` file.                                                  |
| `--single`                                | Single host/URL to capture.                                                  |
| `--add-http-ports`<br>`--add-https-ports` | Comma-separated list of non-standard ports to scan (each must serve HTTP/S). |

- Customizing requests:

| Option            | Description                                                      |
| ----------------- | ---------------------------------------------------------------- |
| `--user-agent`    | User agent to use for all requests.                              |
| `--cookies`       | Cookies to add to the request (e.g., `key1=value1,key2=value2`). |
| `--prepend-https` | Prepend `http://` and `https://` to URLs without either.         |

- Timeout, delay, and retries:

| Option          | Description                                                                      |
| --------------- | -------------------------------------------------------------------------------- |
| `--timeout`     | Request timeout (default: `7`).                                                  |
| `--jitter`      | Add random delay (in seconds) between requests and query URLs in a random order. |
| `--delay`       | Delay (in seconds) between opening a navigator and taking a screenshot.          |
| `--threads`     | Number of threads to use (file-based input).                                     |
| `--max-retries` | Maximum retries on timeouts.                                                     |
## Aquatone

>**[Aquatone](https://github.com/michenriksen/aquatone)** is written in Go and uses Google Chrome or Chromium headless browser to capture screenshots and metadata from the target URLs.

>[!note]- Installation
> ```bash
> wget https://github.com/michenriksen/aquatone/releases/download/v1.7.0/aquatone_linux_amd64_1.7.0.zip && \
> unzip aquatone_linux_amd64_1.7.0.zip
> ```

- Scan a list of URLs and save results into the `example.com` directory:

```bash
cat subs.txt | aquatone
```


| Option                | Description                                                                                                  | Default                         |
| --------------------- | ------------------------------------------------------------------------------------------------------------ | ------------------------------- |
| `-chrome-path`        | Full path to the Chrome/Chromium executable to use. By default, aquatone will search for Chrome or Chromium. | N/A                             |
| `-debug`              | Print debugging information.                                                                                 | `false`                         |
| `-http-timeout`       | Timeout in miliseconds for HTTP requests.                                                                    | `3000`                          |
| `-nmap`               | Parse input as Nmap/Masscan XML.                                                                             | `false`                         |
| `-out`                | Directory to write files to.                                                                                 | `.`                             |
| `-ports`              | Ports to scan on hosts. Supported list aliases: small, medium, large, xlarge.                                | `80`,`443`,`8000`,`8080`,`8443` |
| `-proxy`              | Proxy to use for HTTP requests.                                                                              | N/A                             |
| `-resolution`         | Screenshot resolution.                                                                                       | `1440`,`900`                    |
| `-save-body`          | Save response bodies to files.                                                                               | `true`                          |
| `-scan-timeout`       | Timeout in miliseconds for port scans.                                                                       | `100`                           |
| `-screenshot-timeout` | Timeout in miliseconds for screenshots.                                                                      | `30000`                         |
| `-session`            | Load Aquatone session file and generate HTML report.                                                         | N/A                             |
| `-silent`             | Suppress all output except for errors.                                                                       | `false`                         |
| `-template-path`      | Path to HTML template to use for report.                                                                     | N/A                             |
| `-threads`            | Number of concurrent threads.                                                                                | Number of logical CPUs.         |
| `-version`            | Print current Aquatone version.                                                                              |                                 |

