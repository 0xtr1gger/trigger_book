---
created: 2026-09-24
updated: 2026-09-24
---

## Visual recon and why it is important

**Visual reconnaissance** involves automatically capturing screenshots of rendered web applications or services across hundreds or thousands of hosts.

Screenshots can be really helpful to build a targeted list of valuable applications. Unlike classic port scanning (e.g., with Nmap) or basic HTTP probing (e.g., `curl`, `httpx`, `ffuf`), visual recon goes a step further:

- Rapid triage and prioritization
	- Instead of manually checking each URL or sifting through raw HTML, you quickly scan a report of screenshots to identify interesting targets: login panels, admin interfaces, forgotten development servers, custom web applications, etc.
	- This approach is far faster and more intuitive than dealing with piles of textual data.

- Filter out error or empty pages
	- Even if an endpoint appears to be alive, and the response is `200`, you can't now for sure what's there until you inspect the HTML or render the page. Web applications may implement custom error pages.

- Recognize technology stacks
	- It might be much more easy to fingerprint the technology stack of a target application using visual cues. You just know how WordPress, Tomcat, Jenkins, Grafana *look like*. It's more convenient for a human brain to work with pictures and colors rather than tags and attributes.

Two most commonly used tools for automated visual reconnaissance include:

- [EyeWitness](https://github.com/RedSiege/EyeWitness)
- [Aquatone](https://github.com/michenriksen/aquatone)

>[!interesting]+ Headless browsers
> These tools use a **headless browser** to simulate a user opening a URL.
> 
>>A **[headless browser](https://en.wikipedia.org/wiki/Headless_browser)** is a web browser without a GUI (Graphical User Interface).
> 
> A headless browser can execute JavaScript, parse CSS, render DOM, handle client-side redirects, just like a regular browser. The tool then captures a screenshot of the rendered page and saves it along with metadata like page title, HTTP response headers, cookies, etc.

>[!note] See also: [`gowitness`](https://github.com/sensepost/gowitness).
## EyeWitness

>[EyeWitness](https://github.com/RedSiege/EyeWitness), written in Python, uses the Selenium WebDriver API to control a headless browser, Chrome or Chromium. It takes a list of URLs or hosts, navigates to each, and captures screenshots and metadata.

Key features:
- Works on Windows, Linux, and macOS.
- Automatically adjusts resource consumption based to system capabilities.
- Support for configuration files.
- Pre-flight URL validation checks.
- Progress tracking with ETA (Estimated Time of Arrival).
- Support for multiple input formats (text files, Nmap XML, Nessus XML).
- Isolated virtual environments.

>[!note]+ Installation
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

>[!note]+ Virtual environments
> - To use, first activate a virtual environment:
> 
> ```bash
> source eyewitness-venv/bin/activate
> ```
> 
> - When finished, deactivate it:
> 
> ```bash
> deactivate
> ```

- Scan a list of URLs and save results into the `example.com` directory:

```bash
eyewitness --web -f urls.txt -d example.com
```

- Scan a list of hosts and save results into the `example.com` directory:

```bash
eyewitness --web -f hosts.txt --prepend-https -d example.com
```

Once finished, EyeWitness will generate an HTML report and save it into a directory you specified. By default, it will prompt you to open the page.


| Option                                    | Description                                                                   |
| ----------------------------------------- | ----------------------------------------------------------------------------- |
| `--web`                                   | HTTP screenshot using Selenium.                                               |
| `-f <file>`                               | Newline-separated URLs to capture.                                            |
| `-x <file>.xml`                           | Nmap XML or `.Nessus` file.                                                   |
| `--single <url>`                          | Single host/URL to capture.                                                   |
| `--no-dns`                                | Skip DNS resolution.                                                          |
| `--timeout <seconds>`                     | Maximum number of seconds to wait while requesting a web page (default: `7`). |
| `--jitter <seconds>`                      | Add random delay between requests and query URLs in a random order.           |
| `--delay <seconds>`                       | Delay between opening a navigator and taking a screenshot.                    |
| `--threads <threads>`                     | Number of threads to use (file-based input).                                  |
| `--max-retries <retries>`                 | Maximum retries on timeouts.                                                  |
| `-d <directory>`                          | Directory for report input.                                                   |
| `--result <hosts>`                        | Number of hosts per page or report.                                           |
| `--no-prompt`                             | Don't prompt to open the report.                                              |
| `--user-agent`                            | User agent to use for all requests.                                           |
| `--proxy-ip <ip_address>`                 | IP address of the web proxy to send requests through.                         |
| `--proxy-type <socks5/http>`              | Proxy type (SOCKS5 or HTTP).                                                  |
| `--show-selenium`                         | Show display for selenium.                                                    |
| `--resolve`                               | Resolve IP addresses/hostnames for targets.                                   |
| `--add-http-ports`<br>`--add-https-ports` | Comma-separated additional HTTP/HTTPS port(s) to scan.                        |
| `--prepend-https`                         | Prepend `http://` and `https://` to URLs without either.                      |
| `--cookies key1=value1,key2=value2`       | Cookies to add to the request.                                                |

## Aquatone

>**[Aquatone](https://github.com/michenriksen/aquatone)** is written in Go and uses Google Chrome or Chromium headless browser to capture screenshots and metadata from the target URLs.


>[!note]+ Installation
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




