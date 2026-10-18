---
created: 2026-09-27
updated: 2026-10-04
status: draft
proofread: no
---
## Reconnaissance & enumeration

>[!note] For OSINT, see [[🛠️ OSINT methodology]].
## Asset discovery

- Asset discovery maps the target's external footprint — the domains, hosts, and live services in scope — before any active testing. 
- Work outside-in: DNS → subdomains and virtual hosts → services.

>[!info] This sub-root shortlists the most essential commands for each area. Follow the linked note for the full methodology, tooling, and options.

### DNS records

>[!note] See [[Querying DNS]].

- Query every available record for a domain:

```bash
dig example.com ANY
```

- Attempt a full zone transfer against an authoritative name server:

```bash
dig axfr @ns1.example.com example.com
```

### Subdomain enumeration

>[!note] See [[Subdomain enumeration]].

#### Active subdomain enumeration

>[!note] See [[Subdomain enumeration#Active subdomain enumeration]].

- Enumerate subdomains passively from Certificate Transparency and third-party datasets:

```bash
subfinder -d example.com -all -silent
```

- Brute-force subdomains actively from a wordlist:

```bash
ffuf -u https://FUZZ.example.com -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt
```

- Add resolved hosts to your `/etc/hosts`:

```bash
sudo tee -a /etc/hosts > /dev/null <<EOT
10.10.11.5 blog.example.com careers.example.com dev.example.com gitlab.example.com vpn.example.com
EOT
```

#### Passive subdomain enumeration

>[!note] See [[Subdomain enumeration#Passive subdomain enumeration]].

- Amass passive mode:

```bash
amass enum -passive -d example1.com -d example2.com -o results.txt
```

>[!note] See [[Subdomain enumeration#Amass passive mode]].

- Subfinder:

```bash
subfinder -d example.com -all -o results.txt
```

>[!note] See [[Subdomain enumeration#Subfinder]].

- Certificate Transparency (CT) logs:

```bash
curl -s "https://crt.sh/?q=%25.example.com&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u
```

>[!warning] [`crt.sh`](https://crt.sh/) has occasional periods of downtime or high latency. [`Merklemap`](https://www.merklemap.com/) and [`SSLMate’s Cert Spotter`](https://sslmate.com/certspotter/) can be used as a fallback.

```bash
subfinder -d example.com -sources crtsh -o subfinder_ct.txt
```

```bash
tlsx -u example.com -ctl -silent
```

>[!note] See [[Subdomain enumeration#Certificate Transparency logs]].

- SAN (Subject Alternate Name) from the TLS certificate:

```bash
openssl s_client -connect example.com:443 2>/dev/null | openssl x509 -noout -ext subjectAltName | grep -oP '(?<=DNS:|IP Address:)[^,]+'|sort -uV
```

>[!note] See [[Subdomain enumeration#SAN (Subject Alternative Name)]].

>[!note] See [[Subdomain enumeration#Passive subdomain enumeration]].

### Virtual host enumeration

>[!note] See [[Virtual host enumeration]].

- Discover name-based virtual hosts served on the same IP by fuzzing the `Host` header:

```bash
ffuf -u https://example.com -H "Host: FUZZ.example.com" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt -fs 0
```

### Host and service discovery

>[!note] See [[🛠️ Host and service discovery]].

- Sweep discovered hosts for open ports, then probe the live ones for HTTP:

```bash
naabu -host example.com -silent | httpx -silent
```

### Web application discovery

- Find web applications exposed across the target's infrastructure, then enumerate each one. 

>[!note] See [[Web discovery and enumeration methodology]].

- Sweep the common web ports across the in-scope hosts:

```bash
sudo nmap -p 80,443,8000,8080,8180,8888,10000 --open -oA web_discovery -iL hosts.txt
```

## Nmap 
	
- Nmap is the primary tool for active host and service discovery. A typical sweep moves from finding live hosts, to mapping open ports, to fingerprinting the services behind them — deepened with NSE scripts and, where needed, tuned to evade filtering.
### Host discovery

>[!note] See [[Nmap host discovery]].

- Find live hosts on a subnet without port scanning:

```bash
sudo nmap -sn 10.10.11.0/24
```

### Port scanning

>[!note] See [[Nmap port scanning]].

- Scan the top 1000 TCP ports across the in-scope hosts:

```bash
sudo nmap --open -oA example_tcp_1k -iL hosts.txt
```

- Scan all TCP ports with a stealth `SYN` scan:

```bash
sudo nmap -sS --open -p- -T4 -oA example_tcp_all -iL hosts.txt
```

- Scan the top UDP ports:

```bash
sudo nmap -sU --open -oA example_udp -iL hosts.txt
```

### Filtering the noise

>[!note] See [`awesome-nmap-grep — leonjza, GitHub`](https://github.com/leonjza/awesome-nmap-grep).

- Count the open ports per host:

```bash
egrep -v "^#|Status: Up" example_tcp_all.gnmap | cut -d' ' -f2,4- | sed -n -e 's/Ignored.*//p' | awk -F, '{split($0,a," "); printf "Host: %-20s Ports Open: %d\n" , a[1], NF}' | sort -k 5 -g
```

- Print each host and its open ports:

```bash
egrep -v "^#|Status: Up" example_tcp_all.gnmap | cut -d' ' -f2,4- | sed 's/Ignored.*//' | awk '{print "Host: " $1 " Ports: " NF-1; $1=""; for(i=2; i<=NF; i++) { a=a" "$i }; split(a,s,","); for(e in s) { split(s[e],v,"/"); printf "%-8s %s/%-7s %s\n", v[2], v[3], v[1], v[5] }; a="" }'
```

- Output the running services and their versions:

```bash
egrep -v "^#|Status: Up" example_tcp_all.gnmap | cut -d ' ' -f4- | tr ',' '\n' | sed -e 's/^[ \t]*//' | awk -F '/' '{print $7}' | grep -v "^$" | sort | uniq -c | sort -k 1 -nr
```

### Version and OS detection

>[!note] See [[Nmap version detection]].

- Fingerprint service versions and the operating system on the open ports:

```bash
sudo nmap -sV -O -p <ports> 10.10.11.5
```

### NSE scripts

>[!note] See [[Nmap NSE scripts]].

- Run the default script set alongside version detection:

```bash
sudo nmap -sC -sV 10.10.11.5
```

### Firewall and IDS evasion

>[!note] See [[Nmap firewall evasion]].

- Skip host discovery and slow the scan down to reduce noise against filtered targets:

```bash
sudo nmap -Pn -T2 -f 10.10.11.5
```

## Web recon

>[!note] See [[Web application security testing methodology]] and [[Web discovery and enumeration methodology]].