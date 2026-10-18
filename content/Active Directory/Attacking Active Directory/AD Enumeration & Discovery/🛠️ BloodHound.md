---
created: 2026-08-15
updated: 2026-10-14
tags:
  - AD
  - AD_attacks
  - enumeration
---
## BloodHound

- The amount of data, hence the attack surface, produced in Active Directory environments can be enormous. 
- As a way to automate the analysis and collection of this data, [BloodHound](https://github.com/SpecterOps/BloodHound-Legacy) was created.

>**[BloodHound](https://bloodhound.specterops.io/get-started/introduction)** is an open-source Active Directory and Entra ID (formerly Azure AD) reconnaissance and attack path analysis tool that uses **[graph theory](https://en.wikipedia.org/wiki/Graph_theory)** to visualize AD objects and relationships between them.

>[!info] A **graph** is a mathematical structure used to model pairwise relations between objects. It is formally defined as an *ordered pair* $G=(V,E)$, where $V$ is a set of **nodes** (also called *vertices* or *points*), and $E$ is a set of **edges** (also called *links*, *arcs*, or *lines*).

- Every Active Directory **object**, such as a user, group, or computer, becomes a **node**.
- Every **relationship**, such as permissions or group membership, becomes a **directed edge**.
- To analyze relationships between objects, BloodHound supports the [`Cypher query language`](https://neo4j.com/docs/getting-started/cypher/), a declarative query language used to interact with Neo4j graph databases. 

---

- With BloodHound, privilege escalation becomes a path-finding problem: the shortest path from a node marked *owned* to the `Domain Admins` node is the quickest route to compromising the domain.
- A separate collector (`SharpHound` or `BloodHound.py`) is needed to gather the data; the BloodHound application ingests it, stores it in a graph database, and answers questions with the Cypher query language.

// [screenshot example]

---

- As of version 4.0, BloodHound also supports supports Azure. 

>[!note]- BloodHound editions 
> - **[BloodHound Legacy](https://github.com/SpecterOps/BloodHound-Legacy)**
>     - The original BloodHound, no longer supported.
> - **[BloodHound Community Edition](https://github.com/SpecterOps/BloodHound)**
>     - Released in August 2023, actively supported.
>     - Uses Docker Compose to manage a set of containers; easy to deploy, with a web GUI.
> - **[BloodHound Enterprise](https://specterops.io/bloodhound-enterprise/)**
> 	- An attack surface management solution that continuously maps and quantifies Active Directory attaph paths.
>     - Paid version of BloodHound for attack path management, used for risk management and validation.
> 

## Installation and setup

- BloodHound CE is not a single binary; it runs as a **stack of Docker containers** orchestrated by Docker Compose:

| Container        | Description                                                                                                 |
| ---------------- | ----------------------------------------------------------------------------------------------------------- |
| `bloodhound`     | REST API + Web UI; Go backend, React frontend.                                                              |
| `graph-datapipe` | Ingestion pipeline (parses data gathered by a collector and writes to the graph)l written in Go.            |
| `neo4j`          | Graph database, stores the AD/Entra ID attach graph; written in Java, runs in a JVM (Java Virtual Machine). |
| `postgres`       | Application database (AD objects, metadata, collection state); PostgreSQL.                                  |
| `docker-proxy`   | A small helper container running a socket proxy; Alpine/`socat`.                                            |

- [`bloodhound-cli`](https://github.com/SpecterOps/bloodhound-cli/releases) automates the whole deployment. It generates a `docker-compose.yml` manifest, pulls necessary Docker images, generates secrets, and starts the containers.
- BloodHound can be installed on Windows, Linux, and macOS — anywhere Docker runs.

>[!note]+ Minimum specifications
> |           | Minimum specifications | For large environments (>50K) |
> | --------- | ---------------------- | ----------------------------- |
> | RAM       | `8` GB                 | `96` GB                       |
> | Processor | `4` cores              | `12` cores                    |
> | Disk      | `10` GB                | `50` GB                       |
> - On **Docker Desktop** (Windows/macOS), the RAM must be allocated to the Docker VM (`Settings` → `Resources`), not just present on the host.

- Prerequisites: 
	- Docker Engine 24+ (or Docker Desktop) with Compose v2 plugin (`docker compose version`).
	- Root/Administrator rights, or membership in the `docker` group (Linux).
	- (Windows only) WSL2 enabled.

>[!info]- BloodHound CE vs. BloodHound Legacy
>- **BloodHound Legacy** (pre-2024) is an Electron desktop application; it requires you to *manually install Neo4j*. You interact with Neo4j web console at `http://localhost:7474`, and the application is connected via the Bolt protocol (`localhost:7687`).
>- **BloodHound CE** (current, maintained) runs as a set of Docker containers. The UI and API runs on `http://localhost:8080`, and Neo4j runs as a managed container (`7474`/`7687` for directed graphs). 
### Installing BloodHound on Linux

1. Install Docker.

```bash
curl -fsSL https://get.docker.com | sudo sh
```
```bash
sudo usermod -aG docker "$USER" # log out and back in afterwards
```
```bash
docker --version && docker compose version
```

>[!note] See [`Install Docker Desktop on Linux — dockerdocs`](https://docs.docker.com/desktop/setup/install/linux/) and [`Install Docker Engine on Ubuntu — dockerdocs`](https://docs.docker.com/engine/install/ubuntu/).

2. Create a dedicated directory for BloodHound and download [BloodHound CLI](https://github.com/SpecterOps/bloodhound-cli/releases):

```bash
mkdir -p ~/bloodhound && cd ~/bloodhound
```
```bash
wget https://github.com/SpecterOps/bloodhound-cli/releases/latest/download/bloodhound-cli-linux-amd64.tar.gz
```

>[!tip] On ARM64 hosts (Apple Silicon VMs, Raspberry Pi 5, ARM cloud instances) use `bloodhound-cli-linux-arm64.tar.gz` instead.

3. Unpack the file:

```bash
tar -xvzf bloodhound-cli-linux-amd64.tar.gz
```

4. Run the install command:

```bash
./bloodhound-cli install
```

>[!info] `install` pulls the images from `ghcr.io/specterops`, writes a `docker-compose.yml` in the current directory, generates a random admin password (stored in the CLI's local config) and a random Neo4j password (written to `neo4j-secrets.txt`), and starts all containers.

5. Once the installation is complete, you will see a randomly-generated password; save it for the next steps.

```bash
# ...
[+] BloodHound is ready to go!
[+] You can log in as `admin` with this password: <password>
**
[+] You can get your admin password by running: bloodhound-cli config get default_password
[+] You can access the BloodHound UI at: http://127.0.0.1:8080/ui/login
```

> [!warning] The **first startup can take several minutes**: `graph-datapipe` performs database migrations before the UI becomes responsive. A timeout/blank page right after install is normal.

- Check container state using `docker ps`:

```bash
docker ps
```

> [!example]-
> ```bash
> docker ps
> ```
> 
> ```bash
> Emulate Docker CLI using podman. Create /etc/containers/nodocker to quiet msg.
> CONTAINER ID  IMAGE                                   COMMAND     CREATED        STATUS                  PORTS                                                         NAMES
> 3897f75a7dcc  docker.io/library/neo4j:4.4             neo4j       2 minutes ago  Up 2 minutes (healthy)  127.0.0.1:7474->7474/tcp, 127.0.0.1:7687->7687/tcp, 7473/tcp  bloodhound-graph-db-1
> c93c5f474bee  docker.io/library/postgres:18           postgres    2 minutes ago  Up 2 minutes (healthy)  5432/tcp                                                      bloodhound-app-db-1
> f1166b6c2558  docker.io/specterops/bloodhound:latest              2 minutes ago  Up 2 minutes            127.0.0.1:8080->8080/tcp                                      bloodhound-bloodhound-1
> ```

6.  Log in to BloodHound in `http://localhost:8080/ui/login` as `admin` using the generated password.
7. Reset the password. 

>[!tip]+ 
>- Once BloodHound containers are up, you can browse the raw Neo4j graph at `http://localhost:7474` (user `neo4j`) or connect via `bolt://localhost:7687` with tools like `cypher-shell`.
### Useful BloodHound CLI commands

- See container status:

```bash
docker ps
```

- Start/stop/restart BloodHound:

```bash
./bloodhound-cli containers start
```
```bash
./bloodhound-cli containers stop
```
```bash
./bloodhound-cli containers restart
```

- Follow logs:

```bash
./bloodhound-cli logs -f <service> 
```

- Retrieve default administrator password:

```bash
./bloodhound-cli config get default_password
```

>[!info] `config get default_password` only returns the **initial** admin password, not necessarily the current one.

- Update to latest release:

```bash
./bloodhound-cli update
```

- Remove containers:

```bash
./bloodhound-cli containers destroy
```

>[!warning] The graph and all collected AD objects and relations are stored in **Docker volumes**. Removing the volumes (`docker compose down -v`, `docker volume rm ...`) permanently deletes the entire BloodHound database.  


## Collecting data for BloodHound

- There are three main ways to collect data for BloodHound:

| Collector                                                    | Runs on         | Description                                                                                                    |
| ------------------------------------------------------------ | --------------- | -------------------------------------------------------------------------------------------------------------- |
| [`SharpHound`](https://github.com/SpecterOps/SharpHound)     | Windows only    | Official C#/.NET collector; uses native APIs (LDAP, SAM-R, `NetWkstaUserEnum`, remote registry, DCOM).         |
| [`BloodHound.py`](https://github.com/dirkjanm/BloodHound.py) | Linux / Windows | Python port (partial) of `ShaprHound`; uses LDAP and Impacket (SMB/RPC).                                       |
| [`NetExec`](https://github.com/Pennyw0rth/NetExec)           | Linux / Windows | Successor of CrackMapExec; the `--bloodhound` option on the `ldap` module runs `BloodHound.py` under the hood. |

### `SharpHound.exe`

- `SharpHound.exe` runs natively on Windows, no administrator rights required; requires **.NET Framework 4.7.2+** (default on Win10 1809+/Server 2019+).

>[!note]+ Installation
> - Download `Sharphound.zip` from [`github.com/SpecterOps/SharpHound/releases`](https://github.com/SpecterOps/SharpHound/releases):
> 
> ```bash
> wget https://github.com/SpecterOps/SharpHound/releases/download/v2.17.0/SharpHound_v2.17.0_windows_x86.zip
> ```
> 
> - The archive contains `SharpHound.exe` and `SharpHound.ps1` (PowerShell wrapper, `Invoke-SharpHound`).
>
>>[!note] See [`SharpHound releases`](https://github.com/SpecterOps/SharpHound/releases) and [`SharpHound Community Edition — SpecterOps`](https://bloodhound.specterops.io/collect-data/ce-collection/sharphound).

- Collect data using `SharpHound`:

```bash
.\SharpHound.exe -d example.com
```

- If `-c` (`-collectionmethods`) is not specified, BloodHound uses `Default`. The collection method determines what data is gathered.

> [!note]- Common `SharpHound` collection methods (`-c`/`--collectionmethods`):
> 
> | Default        | Description                                                                                                                                                                                                                                                                                                                                                                    |
> | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
> | `Default`      | **Connect to the DC over LDAP**; collect AD security group memberships, domain trusts, exploitable permissions (ACLs) on AD objects (including AD CS objects), the OU tree structure, Group Policy links, Site objects, and the most relevant AD properties. <br>**Connect to other domain-joined computers over SMB/RPC**; collect local group memberships and user sessions. |
> | `All`          | Perform all collection methods.                                                                                                                                                                                                                                                                                                                                                |
> | `DCOnly`       | Connect to the DC over LDAP, collect same information as `Default` but only from the DC; don't connect to other domain-joined computers.                                                                                                                                                                                                                                       |
> | `ComputerOnly` | Connect to non-DC domain-joined computers over SMB/RPC, collect the same information as `Default` but only from domain-joined computers; don't connect to the DC.                                                                                                                                                                                                              |
> | `Session`      | Collect user sessions; doesn't require administrator privileges on targets.                                                                                                                                                                                                                                                                                                    |
> | `LoggedOn`     | Collect user sessions; requires local administrator on the target computers.                                                                                                                                                                                                                                                                                                   |
>>[!note] See [`SharpHound Community Edition Flags — SpecterOps`](https://bloodhound.specterops.io/collect-data/ce-collection/sharphound-flags).

- Multiple methods can be specified in one run, comma-separated.

 >[!warning] `Default`, `All`, `DCOnly`, and `ComputerOnly` are **presets** and can't be combined with each other; only the atomic methods can be combined (e.g. `-c Session,LocalAdmin`).

- Perform all collection methods:

```powershell
.\SharpHound.exe -c All
```

>[!note]- Common `SharpHound` flags
> 
> - Targets and scope:
> 
> | Option | Description |
> | --- | --- |
> | `-c`, `--collectionmethods` | Collection methods (default: `Default`); comma-separated, see table above. |
> | `-d`, `--domain` | Target domain (FQDN); also used to auto-locate a DC. |
> | `-s`, `--searchforest` | Extend collection to every reachable domain in the forest. |
> | `--stealth` | Low-noise mode: collects sessions only against hosts most likely to hold them — no local-group data. |
> | `--computerfile` | Text file with one computer per line; enumerate exactly those machines. |
> | `--excludecomputers` | Comma-separated computers to skip during computer enumeration. |
> | `--excludedomaincontrollers` | Skip DCs during computer enumeration (LDAP collection still uses them). |
> 
> - LDAP connection & authentication:
> 
> | Option                              | Description                                                                                   |
> | ----------------------------------- | --------------------------------------------------------------------------------------------- |
> | `--domaincontroller`                | DC (hostname or IP address); if IP address is specified, NTLM is used as a fallback.          |
> | `--ldapport`                        | Override the LDAP port (default `389`; `636` with `--secureldap`).                            |
> | `--secureldap`                      | Connect over LDAPS.                                                                           |
> | `--disablecertvalidation`           | Skip TLS cert validation for LDAPS (self-signed/internal CA).                                 |
> | `--ldapusername` / `--ldappassword` | Alternate LDAP credentials (non-domain-joined hosts, run-as).                                 |
> | `--searchbase`                      | LDAP base `DistinguishedName`.                                                                |
> | `--ldapfilter`                      | Custom LDAP filter (e.g. `"(admincount=1)"`); collects only matching objects (partial graph). |
> 
> - Output:
> 
> | Option | Description |
> | --- | --- |
> | `--outputdirectory` | Directory for output (default: current directory). |
> | `--outputprefix` | Prefix for generated file names. |
> | `--zipfilename` | Name of the output ZIP (default: `<timestamp>_BloodHound.zip`). |
> | `--zippassword` | ZIP password (default: **`infected`** — change it; the file is a full domain map). |
> | `--randomfilenames` | Randomize output file names (opsec). |
> | `--nozip` | Skip ZIP packaging; write raw JSON files (unencrypted — clean up promptly). |
> | `--collectallproperties` | Collect all string-valued LDAP properties instead of the curated default set. |
> | `--skippassword` | Skip password metadata collection (e.g. `pwdLastSet`). |
> 
> - Looping:
> 
> | Option | Description |
> | --- | --- |
> | `--loop` | Re-run **computer-based** methods on a schedule; upload every iteration to accumulate sessions. |
> | `--loopduration` | Total loop time, `HH:MM:SS` (default `02:00:00`). |
> | `--loopinterval` | Pause between iterations, `HH:MM:SS` (default `00:05:00`). |
> 
> 
> - Performance and timing
> 
> | Option             | Description                                                            |
> | ------------------ | ---------------------------------------------------------------------- |
> | `--threads`        | Number of concurrent threads (default ≈ `50`).                         |
> | `--throttle`       | Fixed delay in **milliseconds** between computer requests.             |
> | `--jitter`         | Random percentage variation (`0`-`100`) applied to the throttle delay. |
> | `--statusinterval` | Seconds between status updates (default `30`).                         |
> 
> - Cache:
> 
> | Option | Description |
> | --- | --- |
> | `--memcache` | Keep the SID/GUID cache in memory instead of a `.cache` file on disk. |
> | `--cachefilename` | Custom cache file path (speeds up subsequent runs). |
> 
>>[!note] See [`SharpHound Community Edition Flags — SpecterOps`](https://bloodhound.specterops.io/collect-data/ce-collection/sharphound-flags).

>[!tip]+
> 
> - You can use a [PowerShell wrapper](https://github.com/SpecterOps/BloodHound-Legacy/blob/master/Collectors/SharpHound.ps1):
> 
> ```powershell
> Import-Module .\SharpHound.ps1
> ```
> 
> ```bash
> Invoke-SharpHound -CollectionMethod All -OutputDirectory C:\Temp
> ```
### `BloodHound.py`

- `BloodHound.py` is a Python port of `SharpHound`, runs on Linux. It doesn't, however, collect AD CS/certificates, has no loop mode or cache file. 

>[!warning] `SharpHound` collects richer data than `BloodHound.py`.
>- `SharpHound` uses native APIs to collect data about the domain; the Python collector reproduces them only partially.

>[!note]+ Installation: `BloodHound.py`
>```bash
>pip install bloodhound
>```

- Collect data using `BloodHound.py`

```bash
bloodhound-python -u 'jdoe' -p 'passwd123' -d example.com -dc dc01.example.com
```

```bash
./bloodhound.py -u 'Olivia' -p 'ichliebedich' -d administrator.htb -ns 10.129.75.222 -c All
```

- Specify collection methods:

```bash
bloodhound-python -u 'jdoe' -p 'passwd123' -d example.com -dc dc01.example.com -c ACL,Group,Trusts,ObjectProps
```

- Authenticate using [[Pass-the-Hash]]:

```bash
bloodhound-python -u 'jdoe' --hashes ':<NT_hash>' -d example.com -dc-ip 10.10.11.5
```

- Authenticate using Kerberos from the cache:

```bash
export KRB5CCNAME=/tmp/jdoe.ccache
bloodhound-python -k -u 'jdoe' -d example.com -dc-ip 10.10.11.5
```

> [!note]- `BloodHound.py` options
> 
> | Option | Description |
> | --- | --- |
> | `-u`, `--username` | Username for authentication. |
> | `-p`, `--password` | Password for authentication. |
> | `--hashes` | Authenticate using [[Pass-the-Hash]]; format: `LM_hash:NT_hash`. |
> | `--no-pass` | Don't prompt for a password (useful with `-k`). |
> | `-k`, `--kerberos` | Authenticate with a Kerberos ticket from `KRB5CCNAME`. |
> | `--aes-key` | Authenticate with an AES key instead of a password (Kerberos). |
> | `-d`, `--domain` | Target domain (FQDN). |
> | `-dc`, `--domain-controller` | IP address or FQDN of the DC. ⚠ The upstream long option is misspelled `--domaincontroler` — use `-dc`. With Kerberos, supply the **FQDN** (SPN construction). |
> | `-ns`, `--nameserver` | DNS server for lookups (usually the DC). |
> | `--dns-tcp` | Resolve DNS over TCP. |
> | `-c`, `--collectionmethod` | Which information to collect: `Group`, `LocalAdmin`, `Session`, `Trusts`, `Default` (all previous), `DCOnly` (no computer collection), `DCOM`, `RDP`, `PSRemote`, `LoggedOn`, `ObjectProps`, `ACL`, `All` (all except `LoggedOn`). Default: `Default`. |
> | `-w`, `--workers` | Parallel workers (default `10`). |
> | `--zip` | Compress the JSON output files into a ZIP archive. |
> | `-op`, `--outputprefix` | Prefix for output file names. |
>
> - For Kerberos authentication to work, the DC must resolve by FQDN (add it to `/etc/hosts`), and clocks must be in sync with the DC.


### `NetExec`

- Collect data using `NetExec` (`nxc`):

```bash
netexec ldap -u 'jdoe' -p 'passwd123' --bloodhound --collection All
```

>[!note] See [`Bloodhound Ingestor — NetExec Wiki`](https://www.netexec.wiki/ldap-protocol/bloodhound-ingestor).

> [!note] See [[🛠️ Authenticated AD & Windows enumeration]] and [[Querying LDAP]] for how this data is queried directly.

## Uploading and ingesting data

1. Log in to the BloodHound CE UI.
2. In the left menu, click `Quick Upload`.
3. Click `Upload Files` and choose JSON or ZIP-ed JSON files to upload. 
4. Click `Upload`.
5. To 

## Navigating BloodHound GUI

- In the `Explore` tab, you have three options to search and analyze data:
	- **`Search`**:
	- **`Pathfinding`**:
	- **`Cypher`**:

- BloodHound comes with a set of ready-to-use Cypher queries. Go to `Cypher` tab -> click `Saved Queries`. 
- For example, to find all domain admins, execute `All Domain Admins`:


- The area where the graph is displayed is called the `Graph Drawing Area`. Here, BloodHound displays nodes and their relationship as edges.
- You can interact with the graph, move objects, zoom in/out, click on nodes to see more information, or right-click to perform different actions.


- Right-click actions:
	- `Set as starting node`: Set this node as the starting point in the pathfinding tool. 
	- `Set as ending node`: Set this node as the target node in the pathfinding tool.
	- `Add to Tier Zero`:
	- `Add to Owned`

- You can add a node to `Owned` and then execute the saved query `Shortest paths from Owned objects` to find out what you can do from the current point.


- You can also interact with edges. These represent links (relationships) between nodes. 
- Click on a link to find more information about it. 


### The Search bar

- You can use the `Search` bar to search for specific objects by their name or type, e.g., `user:olivia` or `group:domain`.
- Types you can search:
	- **Active Directory**:
		- `Group`
		- `Domain`
		- `Computer`
		- `User`
		- `OU`
		- `GPO`
		- `Container`
	- **Azure**:
		- `AZApp`
		- `AZRole`
		- `AZDevice`
		- `AZGroup`
		- `AZKeyVault`
		- `AZManagementGroup`
		- `AZResourceGroup`
		- `AZServicePrincipal`
		- `AZSubscription`
		- `AZTenant`
		- `AZUser`
		- `AZVM`

### Pathfinding

- The `Pathfinding` tool can be used to find an attack path between two given nodes. 
- 
### Cypher


# drafts



## The BloodHound data model

- Every piece of collected data is either a **node** (an object) or an **edge** (a relationship between two objects).
- Nodes carry **properties** — `pwdlastset`, `hasspn`, `unconstraineddelegation`, and so on — queried in Cypher with lowercase names.
- Edges carry the control relationships that make paths traversable.

### Node kinds

- The Active Directory schema defines these node kinds:

| Kind | Represents |
| --- | --- |
| `Base` | Any object; the common label every node also carries. |
| `User` | A user account. |
| `Computer` | A computer account. |
| `Group` | A security group. |
| `Domain` | A domain, with its policy and trust configuration. |
| `OU` | An organizational unit. |
| `GPO` | A Group Policy Object. |
| `Container` | A container object (for example `CN=Users`). |
| `LocalGroup` | A local group on a computer (for example local Administrators). |
| `LocalUser` | A local user account on a computer. |
| `AIACA` | An Authority Information Access CA certificate. |
| `RootCA` | A root CA certificate. |
| `EnterpriseCA` | An enterprise CA (issues certificates). |
| `NTAuthStore` | The NTAuth store listing CAs trusted for domain authentication. |
| `CertTemplate` | A certificate template. |
| `IssuancePolicy` | A certificate issuance policy (OID). |

> [!note] The AD CS kinds (`CertTemplate`, `EnterpriseCA`, `RootCA`, `AIACA`, `NTAuthStore`, `IssuancePolicy`) appear only when SharpHound runs with `CertServices`/`CARegistry` collection. Newer builds also add `Site`, `SiteServer`, and `SiteSubnet`. Entra ID data adds a parallel set of `AZ*` kinds.

### Edge directionality

- Edges are **directed**: `(source)-[:EDGE]->(target)` reads "source has this relationship over target".
- A **traversable** edge is one the attacker can abuse to take control of the target; pathfinding uses only traversable edges.
- A **non-traversable** edge records information (for example `GetChanges`) that becomes an attack only in combination — post-processing collapses `GetChanges` + `GetChangesAll` into a single traversable `DCSync` edge.

---

## Nodes and attributes cheat sheet

- Property names below are the lowercase **Cypher** names stored in the database — the form used in queries (`MATCH (u:User {hasspn:true})`).
- Every node also carries the common properties in the first table.

### Common properties (all nodes)

| Property | Meaning |
| --- | --- |
| `name` | Display name, usually `SAMACCOUNTNAME@DOMAIN.FQDN`. |
| `objectid` | The object SID (or GUID for AD CS objects). |
| `distinguishedname` | Full LDAP distinguished name. |
| `domain` | FQDN of the owning domain. |
| `domainsid` | SID of the owning domain. |
| `description` | The object's `description` attribute. |
| `whencreated` | Creation timestamp. |
| `enabled` | Whether the account is enabled. |
| `isaclprotected` | DACL inheritance is blocked (AdminSDHolder or explicit). |
| `system_tags` | Analysis tags, including `admin_tier_0` for Tier Zero / high-value objects. |
| `lastseen` / `lastcollected` | When the object was last observed/collected. |
| `collected` | Whether the object's data was actually gathered. |

### User

| Property                                               | Meaning                                                                  |
| ------------------------------------------------------ | ------------------------------------------------------------------------ |
| `samaccountname`                                       | Pre-Windows 2000 logon name.                                             |
| `admincount`                                           | AdminSDHolder flag — the account is (or was) in a protected group.       |
| `hasspn`                                               | Has a Service Principal Name — **Kerberoastable**.                       |
| `serviceprincipalnames`                                | The account's SPN list.                                                  |
| `dontreqpreauth`                                       | Kerberos pre-authentication disabled — **AS-REP roastable**.             |
| `unconstraineddelegation`                              | Trusted for unconstrained delegation.                                    |
| `trustedtoauth`                                        | Trusted to authenticate for delegation (constrained delegation / T2A4D). |
| `sensitive`                                            | Account is sensitive and cannot be delegated.                            |
| `pwdneverexpires`                                      | Password never expires.                                                  |
| `passwordnotreqd`                                      | Password is not required.                                                |
| `pwdlastset`                                           | Password last-set timestamp.                                             |
| `lastlogon` / `lastlogontimestamp`                     | Last (DC-local / replicated) logon timestamp.                            |
| `sidhistory`                                           | SID history values.                                                      |
| `encryptedtextpwdallowed`                              | Password stored with reversible encryption.                              |
| `smartcardrequired`                                    | Smart card required for interactive logon.                               |
| `usedeskeyonly`                                        | Only DES keys used for Kerberos.                                         |
| `supportedencryptiontypes`                             | Supported Kerberos encryption types.                                     |
| `useraccountcontrol`                                   | Raw `userAccountControl` bitmask.                                        |
| `lockedout` / `passwordexpired` / `passwordcantchange` | Lockout / password-state flags.                                          |
| `logonscriptenabled`                                   | A logon script is configured.                                            |
| `hasura`                                               | User-rights assignments were collected for the account.                  |
| `homedirectory` / `title` / `email` / `displayname`    | Standard directory attributes.                                           |
| `owned`                                                | Marked as owned by the operator.                                         |

### Computer

| Property | Meaning |
| --- | --- |
| `samaccountname` | Machine account name (`HOST$`). |
| `operatingsystem` | OS string. |
| `dnshostname` | FQDN hostname. |
| `isdc` | The computer is a Domain Controller. |
| `isreadonlydc` | The computer is a Read-Only DC. |
| `unconstraineddelegation` | Trusted for unconstrained delegation. |
| `trustedtoauth` | Configured for constrained delegation (T2A4D). |
| `haslaps` | LAPS manages the local administrator password. |
| `serviceprincipalnames` | The computer's SPNs. |
| `webclientrunning` | The WebClient (WebDAV) service is running — NTLM relay / coercion target. |
| `smbsigning` | SMB signing is required. |
| `restrictoutboundntlm` | Outbound NTLM is restricted. |
| `gmsa` / `msa` | Group-managed / managed service account. |
| `ldapsigning` / `ldapavailable` / `ldapsavailable` / `ldapsepa` | LDAP(S) signing/channel-binding posture (relay relevance). |
| `lastlogon` / `lastlogontimestamp` / `pwdlastset` | Logon and password timestamps. |
| `sidhistory` | SID history values. |
| `supportedencryptiontypes` | Supported Kerberos encryption types. |
| `owned` | Marked as owned. |

### Group

| Property | Meaning |
| --- | --- |
| `samaccountname` | Group name. |
| `admincount` | Protected by AdminSDHolder. |
| `groupscope` | Scope — Global, Domain Local, or Universal. |
| `system_tags` | Carries `admin_tier_0` for privileged groups (Domain/Enterprise Admins, etc.). |

### Domain

| Property | Meaning |
| --- | --- |
| `functionallevel` | Domain functional level. |
| `netbios` | NetBIOS domain name. |
| `machineaccountquota` | Number of machine accounts a user may create (`ms-DS-MachineAccountQuota`). |
| `minpwdlength` / `maxpwdage` / `minpwdage` / `pwdhistorylength` / `pwdproperties` | Password policy. |
| `lockoutthreshold` / `lockoutduration` / `lockoutobservationwindow` | Lockout policy. |
| `expirepasswordsonsmartcardonlyaccounts` | Smart-card-only accounts honor password expiry. |
| `dsheuristics` | `dSHeuristics` string (affects AD CS and other behavior). |
| `spoofsidhistoryblocked` | SID filtering blocks SID-history injection over trusts. |
| `certificatemappingmethods` / `strongcertificatebindingenforcement` | Certificate-to-account binding mode (AD CS ESC relevance). |
| `vulnerablenetlogonsecuritydescriptor` | Netlogon security descriptor is permissive. |

### OU and Container

| Property | Meaning |
| --- | --- |
| `blocksinheritance` | The OU blocks inherited GPOs. |
| `name` / `objectid` / `distinguishedname` | Identity and placement in the tree. |

### GPO

| Property | Meaning |
| --- | --- |
| `gpostatus` | Enabled/disabled state of the GPO's user and computer settings. |
| `name` / `objectid` / `distinguishedname` | Identity of the policy object. |

### LocalGroup and LocalUser

| Property | Meaning |
| --- | --- |
| `name` | `GROUP@COMPUTER.FQDN` (or user), identifying the on-host principal. |
| `objectid` | SID of the local group/user. |

### CertTemplate (AD CS)

| Property | Meaning |
| --- | --- |
| `oid` | Template OID. |
| `schemaversion` | Template schema version (1 vs 2+). |
| `enrolleesuppliessubject` | Enrollee supplies the subject — the core ESC1 condition. |
| `authenticationenabled` | Issued certificates permit client authentication. |
| `requiresmanagerapproval` | CA manager must approve each request. |
| `authorizedsignatures` | Number of authorized signatures required to enroll. |
| `nosecurityextension` | Certificate omits the `szOID_NTDS_CA_SECURITY_EXT` SID extension (ESC9). |
| `ekus` / `effectiveekus` | Extended Key Usages on the template. |
| `subjectaltrequireupn` / `subjectaltrequiredns` / `subjectaltrequiredomaindns` / `subjectaltrequireemail` / `subjectaltrequirespn` | Which SAN components the template forces. |
| `subjectrequireemail` | The subject must include an email. |
| `certificatenameflag` / `enrollmentflag` | Raw name/enrollment flag bitmasks. |
| `renewalperiod` / `validityperiod` | Renewal and validity windows. |
| `applicationpolicies` / `issuancepolicies` / `certificatepolicy` / `certificateapplicationpolicy` | Policy OIDs bound to the template. |
| `schannelauthenticationenabled` | The template allows Schannel (TLS) authentication. |

### EnterpriseCA (AD CS)

| Property | Meaning |
| --- | --- |
| `caname` | The CA's common name. |
| `dnshostname` | Host serving the CA. |
| `isuserspecifiessanenabled` | `EDITF_ATTRIBUTESUBJECTALTNAME2` is set — any requester can specify a SAN (ESC6). |
| `roleseparationenabled` | CA role separation is enforced. |
| `hasenrollmentagentrestrictions` | Enrollment-agent restrictions are configured. |
| `adcswebenrollmenthttp` / `adcswebenrollmenthttps` / `adcswebenrollmenthttpsepa` | Web-enrollment endpoints and whether EPA protects HTTPS (ESC8 relay surface). |
| `httpenrollmentendpoints` / `httpsenrollmentendpoints` | Discovered enrollment URLs. |
| `hasvulnerableendpoint` | A relay-vulnerable enrollment endpoint exists. |
| `certthumbprint` / `certchain` | CA certificate thumbprint and chain. |
| `hasbasicconstraints` / `basicconstraintpathlength` | Basic-constraints presence and path length. |

### RootCA, AIACA, NTAuthStore, IssuancePolicy (AD CS)

| Property | Meaning |
| --- | --- |
| `certthumbprint` / `certthumbprints` | Certificate thumbprint(s); `NTAuthStore` holds the set trusted for domain auth. |
| `certname` / `certchain` | Certificate common name and chain. |
| `hascrosscertificatepair` / `crosscertificatepair` | Cross-certification data. |
| `oid` *(IssuancePolicy)* | Issuance-policy OID. |
| `certtemplateoid` *(IssuancePolicy)* | OID of the template the policy applies to. |
| `grouplinkid` *(IssuancePolicy)* | Linked group via OID group link (ESC13). |

---

## Edges and relationships cheat sheet

- Edges read `(source)-[:EDGE]->(target)`. Traversable edges feed pathfinding; the rest are recorded for context or combined during post-processing.

### Membership and structure

| Edge | Relationship |
| --- | --- |
| `MemberOf` | Principal belongs to a group. |
| `Contains` | OU/container/domain contains a child object. |
| `GPLink` | A GPO is linked to an OU or domain. |
| `Owns` / `OwnsLimitedRights` | Principal owns the target object. |
| `DCFor` | Computer is a DC for the domain. |

### Remote access and execution

| Edge | Relationship |
| --- | --- |
| `AdminTo` | Principal is a local admin on the computer. |
| `CanRDP` | Principal may log on via RDP. |
| `CanPSRemote` | Principal may use PowerShell Remoting. |
| `ExecuteDCOM` | Principal may execute via DCOM. |
| `SQLAdmin` | Principal is a SQL sysadmin on the host. |
| `HasSession` | A user has (had) a session on the computer — credential-theft target. |
| `RemoteInteractiveLogonRight` | Principal holds the remote interactive logon right. |

### Object-control ACLs

| Edge | Relationship / abuse |
| --- | --- |
| `GenericAll` | Full control of the target. |
| `GenericWrite` | Write any non-protected attribute (for example to set an SPN or add a key credential). |
| `WriteDacl` | Rewrite the object's DACL to grant yourself control. |
| `WriteOwner` / `WriteOwnerLimitedRights` | Take ownership of the object. |
| `AllExtendedRights` | Hold all extended rights (includes force-password-reset and DCSync components). |
| `ForceChangePassword` | Reset the target user's password without the old one. |
| `AddMember` / `AddSelf` | Add a principal (or yourself) to the group. |
| `AddKeyCredentialLink` | Add a key credential (Shadow Credentials) for PKINIT. |
| `AddAllowedToAct` | Configure resource-based constrained delegation on the target. |
| `WriteSPN` | Write an SPN to enable targeted Kerberoasting. |
| `WriteAccountRestrictions` | Edit account restriction attributes (for example delegation settings). |
| `WriteGPLink` | Link a GPO to an OU/domain. |
| `WriteAltSecurityIdentities` | Map an alternate certificate identity (ESC14). |
| `WritePublicInformation` | Write public-information attributes. |
| `ReadLAPSPassword` | Read the LAPS local-admin password. |
| `ReadGMSAPassword` / `DumpSMSAPassword` | Recover a gMSA/sMSA managed password. |

### Delegation and Kerberos

| Edge | Relationship |
| --- | --- |
| `AllowedToDelegate` | Constrained delegation to the target service. |
| `AllowedToAct` | Resource-based constrained delegation (RBCD) over the target. |
| `CoerceToTGT` | Coerce authentication to obtain a TGT (unconstrained-delegation abuse). |
| `AbuseTGTDelegation` | Abuse TGT delegation across an unconstrained-delegation host. |

### Replication and SID history

| Edge | Relationship |
| --- | --- |
| `DCSync` | Post-processed edge: the principal can replicate secrets from the domain (**DCSync**). |
| `GetChanges` / `GetChangesAll` / `GetChangesInFilteredSet` | Replication rights that combine into `DCSync`. |
| `SyncLAPSPassword` | Replicate LAPS passwords. |
| `HasSIDHistory` | The principal carries another principal's SID in SID history. |
| `SpoofSIDHistory` | SID history can be spoofed across the trust. |

### Trusts

| Edge | Relationship |
| --- | --- |
| `SameForestTrust` | Intra-forest trust (child ⇄ parent). |
| `CrossForestTrust` | Inter-forest trust. |
| `HasTrustKeys` | The trust account keys are recoverable. |

### NTLM coercion and relay

| Edge | Relationship |
| --- | --- |
| `CoerceAndRelayNTLMToSMB` | Coerce a victim and relay NTLM to SMB. |
| `CoerceAndRelayNTLMToLDAP` / `CoerceAndRelayNTLMToLDAPS` | Relay coerced NTLM to LDAP / LDAPS. |
| `CoerceAndRelayNTLMToADCS` | Relay coerced NTLM to AD CS web enrollment (ESC8). |

### AD CS

| Edge | Relationship |
| --- | --- |
| `Enroll` / `EnrollOnBehalfOf` | Right to enroll (or enroll on behalf of another) against a template. |
| `DelegatedEnrollmentAgent` | Designated enrollment agent for a template. |
| `ManageCA` / `ManageCertificates` | CA administrator / certificate-manager rights. |
| `HostsCAService` | Computer hosts the enterprise CA service. |
| `WritePKIEnrollmentFlag` / `WritePKINameFlag` | Write the template's enrollment/name flags. |
| `RootCAFor` / `EnterpriseCAFor` / `NTAuthStoreFor` | Links a CA / NTAuth store to the domain it serves. |
| `TrustedForNTAuth` | The CA is trusted for NT (domain) authentication. |
| `IssuedSignedBy` / `PublishedTo` | Certificate issuance chain and template publication to a CA. |
| `GoldenCert` | Possession of the CA key enables forging arbitrary certificates. |
| `OIDGroupLink` / `ExtendedByPolicy` | Issuance policy links a group (ESC13) / extends a template. |
| `ADCSESC1`, `ADCSESC3`, `ADCSESC4`, `ADCSESC6a`, `ADCSESC6b`, `ADCSESC9a`, `ADCSESC9b`, `ADCSESC10a`, `ADCSESC10b`, `ADCSESC13` | Post-processed composite edges, each marking a complete ESC attack path. |

> [!note] The ACL, delegation, AD CS, and relay edges are the *finding*; see [[🛠️ AD testing methodology]].

## Using the BloodHound CE GUI

### Uploading data

- Open **Administration → File Ingest** (or the upload control) and submit the ZIP or JSON produced by the collector; wait for ingestion to finish.

> [!important] A graph reflects only the **last collection**. Sessions expire and memberships change — re-collect periodically during long engagements.

### Marking owned and high value

- Right-click a node → **Mark as Owned** to flag compromised principals, and **Mark as High Value** / **Tier Zero** to flag targets.
- Owned markings drive the "from owned principals" pathfinding and the owned-node Cypher queries below.

### Pathfinding, search, and Cypher

- **Search** the graph for a node, then open its **Entity panel** to read properties, memberships, sessions, local-admin rights, and inbound/outbound object control.
- **Pathfinding** takes a start and end node and draws the shortest traversable path between them.
- **Cypher** runs arbitrary queries; the built-in queries cover the common questions (shortest paths to Domain Admins, Kerberoastable users, DCSync principals, and so on).

---

## Cypher query cheat sheet

- [Cypher](https://bloodhound.specterops.io/analyze-data/cypher-search) describes graph patterns with ASCII art: `(u:User)-[:MemberOf]->(g:Group)` matches any user in any group. Run these in the **Cypher** tab.

### Shortest paths to Domain Admins

- From every owned principal:

```cypher
MATCH p=shortestPath((n {owned:true})-[*1..]->(g:Group))
WHERE g.objectid ENDS WITH "-512"
RETURN p
```

- From a specific user:

```cypher
MATCH p=shortestPath((u:User {name:"JSMITH@DOMAIN.LOCAL"})-[*1..]->(g:Group))
WHERE g.objectid ENDS WITH "-512"
RETURN p
```

### Kerberoastable and AS-REP roastable accounts

- All Kerberoastable users (excluding `krbtgt`):

```cypher
MATCH (u:User {hasspn:true})
WHERE NOT u.name STARTS WITH "KRBTGT@"
RETURN u.name, u.serviceprincipalnames, u.admincount
ORDER BY u.name
```

- Kerberoastable users that reach Domain Admins:

```cypher
MATCH p=shortestPath((u:User {hasspn:true})-[*1..]->(g:Group))
WHERE g.objectid ENDS WITH "-512" AND NOT u.name STARTS WITH "KRBTGT@"
RETURN p
```

- All AS-REP roastable users:

```cypher
MATCH (u:User {dontreqpreauth:true})
RETURN u.name, u.admincount
ORDER BY u.name
```

### DCSync rights

```cypher
MATCH p=(n)-[:DCSync]->(:Domain)
RETURN p
```

- Via the underlying replication rights:

```cypher
MATCH p=(n)-[:GetChanges|GetChangesAll]->(:Domain)
RETURN p
```

### ACL-based escalation

- All object control an owned principal holds:

```cypher
MATCH p=(n {owned:true})-[:GenericAll|GenericWrite|WriteDacl|WriteOwner|ForceChangePassword|AddMember|AddKeyCredentialLink|AddAllowedToAct]->(t)
RETURN p
```

- Control over Tier Zero groups:

```cypher
MATCH p=(n)-[:GenericAll|GenericWrite|WriteDacl|WriteOwner|AddMember]->(g:Group)
WHERE "admin_tier_0" IN g.system_tags
RETURN p
```

### Delegation abuse

- Unconstrained delegation (excluding DCs):

```cypher
MATCH (c:Computer {unconstraineddelegation:true})
WHERE c.isdc = false
RETURN c.name
```

- Constrained delegation targets:

```cypher
MATCH p=(s)-[:AllowedToDelegate]->(t:Computer)
RETURN p
```

- RBCD relationships:

```cypher
MATCH p=(s)-[:AllowedToAct]->(t:Computer)
RETURN p
```

### AD CS attack paths

- Templates meeting the ESC1 conditions:

```cypher
MATCH (t:CertTemplate)
WHERE t.enrolleesuppliessubject = true
  AND t.authenticationenabled = true
  AND t.requiresmanagerapproval = false
RETURN t.name
```

- Any computed AD CS escalation edge from an owned principal:

```cypher
MATCH p=(n {owned:true})-[:ADCSESC1|ADCSESC3|ADCSESC4|ADCSESC6a|ADCSESC6b|ADCSESC9a|ADCSESC9b|ADCSESC10a|ADCSESC10b|ADCSESC13]->(:Domain)
RETURN p
```

- CAs exposing HTTP web enrollment (ESC8 relay surface):

```cypher
MATCH (ca:EnterpriseCA)
WHERE ca.adcswebenrollmenthttp = true
RETURN ca.name
```

### Sessions and local admin

- Domain Admins with active sessions:

```cypher
MATCH (u:User)-[:HasSession]->(c:Computer)
WHERE (u)-[:MemberOf*1..]->(:Group {objectid:"...-512"})
RETURN u.name, c.name
```

- Computers where a user is local admin:

```cypher
MATCH p=(u:User {name:"JSMITH@DOMAIN.LOCAL"})-[:AdminTo]->(:Computer)
RETURN p
```

### Trusts, LAPS, and hygiene

- Domain trusts:

```cypher
MATCH p=(:Domain)-[:SameForestTrust|CrossForestTrust]->(:Domain)
RETURN p
```

- Computers without LAPS:

```cypher
MATCH (c:Computer {haslaps:false})
RETURN c.name
```

- Accounts storing passwords with reversible encryption:

```cypher
MATCH (u:User {encryptedtextpwdallowed:true})
RETURN u.name
```

- Count nodes by type:

```cypher
MATCH (n) RETURN labels(n), count(n)
```

---

## Attack path analysis

### Prioritizing paths

1. **Path length** — shorter paths to Tier Zero are the quickest wins.
2. **Starting privilege** — paths beginning at low-privileged or already-owned nodes are the most realistic.
3. **Reliability** — ACLs, group memberships, and delegation are persistent; session data is point-in-time and decays.
4. **Exploitability** — `GenericAll` on a group is trivially abusable; a GPO or certificate path takes more steps.

### Common patterns

| Pattern | Edges involved |
| --- | --- |
| User → nested group → Domain Admins | `MemberOf` |
| User → object control → privileged group | `GenericAll`, `WriteDacl`, `AddMember` |
| User → session on shared host ← Domain Admin | `HasSession`, `AdminTo` |
| Kerberoastable service account in a privileged group | `hasspn`, `MemberOf` |
| User → writable GPO → OU of targets | `WriteGPLink`, `GPLink`, `Contains` |
| User → RBCD / delegation → computer | `AddAllowedToAct`, `AllowedToAct`, `AllowedToDelegate` |
| User → enroll in vulnerable template → domain auth | `Enroll`, `ADCSESC1` |
| User → add key credential → PKINIT | `AddKeyCredentialLink` |

---

## Operational security and detection

### What collection looks like to defenders

- Anomalous **LDAP query volume** from a single host, and LDAP signing events (for example Event ID `2889`) on DCs.
- **SAM-R / remote-registry** access across many computers.
- Spikes in Kerberos `4768`/`4769` events from an unusual host.
- Known collector signatures flagged by EDR, and detections from identity products such as [Microsoft Defender for Identity](https://www.microsoft.com/en-us/security/business/siem-and-xdr/microsoft-defender-for-identity).

### Reducing noise (authorized engagements)

- Start with `-c DCOnly`, then add methods selectively rather than running `All` at once.
- Slow collection with `--throttle` and `--jitter`; use `--stealth` and `--excludedcs` for session work.
- Spread session collection with `--loop` over hours.
- Where policy allows, execute the collector in memory rather than dropping a known binary to disk:

```powershell
$bytes = [System.IO.File]::ReadAllBytes("C:\Temp\SharpHound.exe")
[System.Reflection.Assembly]::Load($bytes) | Out-Null
[Sharphound.Program]::Main(@("-c","DCOnly"))
```

> [!caution] Evasion techniques (in-memory loading, AMSI handling, binary renaming) belong only in engagements that explicitly authorize them. Record what was run so the blue team can reconcile the activity.

---

## Troubleshooting

| Issue | Cause | Fix |
| --- | --- | --- |
| No session/logged-on data | Running without local admin / high integrity | Run elevated (for example `psexec -s`) against hosts where the account is admin. |
| `LDAP operations error` | Permissions or paging limits | Narrow scope with `--ldapfilter` / `--distinguishedname`. |
| BloodHound.py `Kerberos SessionError` | Clock skew or DNS | Sync time to the DC and point `-ns` at a working DNS/DC. |
| `No data collected` | Wrong domain or unreachable DC | Verify `-d` matches the FQDN and `-ns`/`--domaincontroller` is reachable. |
| CE import fails or hangs | Schema mismatch or corrupt ZIP | Confirm a **CE** collector produced the data; re-collect `DCOnly` and re-upload. |
| CE won't start | Insufficient Docker resources | Allocate at least `4 GB` RAM to Docker. |
| Lost the initial password | Printed once on first startup | Reset it via the API, or redeploy with a fresh volume. |

---

## References and further reading

- [`What is Cypher? — neo4j`](https://neo4j.com/docs/getting-started/cypher/)

---
- [`BloodHound documentation — SpecterOps`](https://bloodhound.specterops.io/)
- [`Node reference — SpecterOps`](https://bloodhound.specterops.io/resources/nodes/overview)
- [`Edge reference — SpecterOps`](https://bloodhound.specterops.io/resources/edges/traversable-edges)
- [`Search with Cypher — SpecterOps`](https://bloodhound.specterops.io/analyze-data/cypher-search)
- [`SharpHound collection and permissions — SpecterOps`](https://bloodhound.specterops.io/collect-data/sharphound-data-permissions)
- [`BloodHound CE — GitHub`](https://github.com/SpecterOps/BloodHound)
- [`SharpHound — GitHub`](https://github.com/SpecterOps/SharpHound)
- [`BloodHound.py — GitHub`](https://github.com/dirkjanm/BloodHound.py)
- [`SharpCollection — GitHub`](https://github.com/Flangvik/SharpCollection)
- [`Active Directory BloodHound — Hack The Box Academy`](https://academy.hackthebox.com/course/preview/active-directory-bloodhound)
---

- [`BloodHound Community Edition Quickstart — SpecterOps`](https://bloodhound.specterops.io/get-started/quickstart/community-edition-quickstart)
---
- [`Install Docker Desktop on Linux — dockerdocs`](https://docs.docker.com/desktop/setup/install/linux/)
- [`Install Docker Engine on Ubuntu — dockerdocs`](https://docs.docker.com/engine/install/ubuntu/)

---
- [`SharpHound Community Edition — SpecterOps`](https://bloodhound.specterops.io/collect-data/ce-collection/sharphound)
- [`SharoHound Community Edition Flags — SpecterOps`](https://bloodhound.specterops.io/collect-data/ce-collection/sharphound-flags)
- [`Bloodhound Ingestor — NetExec Wiki`](https://www.netexec.wiki/ldap-protocol/bloodhound-ingestor)
---



> [!warning] Legacy and CE use **incompatible JSON schemas**. Collect with the SharpHound/BloodHound.py build that matches the edition being used — a CE collector feeds CE, a Legacy collector feeds Legacy.