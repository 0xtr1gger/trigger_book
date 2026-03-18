---
created: 2026-03-16
tags:
  - defensive
  - monitoring
  - SIEM
---

## Elastic Stack: Architectural overview


>**Elastic Stack** (formerly **ELK Stack**, **Elasticsearch, Logstash, Kibana, Beats)** is a distributed, document-oriented search and analytics platform commonly used for **log management, SIEM, observability, and threat hunting**.

Elastic Stack consists of several primary components:

- **Elasticsearch**
	- Distributed, RESTful **document store and search & analytics engine**.
- **Logstash**
	- Data processing pipeline (ETL) that collects, parses, enriches, transforms logs, and then sends them to Elasticsearch.
- **Beats**
	- Lightweight data shippers (agents), installed on endpoints to **collect and forward data** to Logstash or Elasticsearch.
- **Kibana**
	- Visualization & UI layer; provides dashboards, charts, and search interface or Elasticsearch data. 

> [!important]+ Important default ports
> | Service                         | Default Port   | Protocol        |
> | ------------------------------- | -------------- | --------------- |
> | **Kibana**                      | `5601`         | HTTP            |
> | **Elasticsearch**               | `9200`         | HTTP (REST API) |
> | **Elasticsearch cluster comms** | `9300`         | TCP             |
> | **Logstash Beats input**        | `5044`         | TCP             |
> | **Logstash Syslog input**       | `5514` / `514` | TCP/UDP         |
> 


### Elasticsearch 

>**Elasticsearch** is an open-source, JSON-based distributed search and analytics engine based on [`Apache Lucene`](https://en.wikipedia.org/wiki/Apache_Lucene).

>[!important] By default, Elasticsearch listens on port `9001`.

Core Elasticsearch architecture consists of the following components:

> A **Cluster** is a collection of one or more nodes that work together to provide **distributed search, analytics, and data storage capabilities**.

>A **Node** is an individual server instance running Elasticsearch.

Each node can be assigned one or more roles:
- **Master-eligible node**: A node eligible to be elected as a master, which controls the cluster (e.g., creating or deleting an index, tracking which nodes are part of the cluster, and deciding which shards to allocate to which node).
- **Data node**: A node that hold data and perform data-related operations, such as CRUD, search, and aggregations. 
- **Ingest node**: A node able to apply an ingest pipeline (transformation pipeline) to a document to transform and enrich the data before indexing.
- **Remote-eligible node**: A node that is eligible to act as a remote client.
- **Machine learning node**: A node that can run machine learning features.
- **Transform node**: A node that can perform transforms.

>An **Index** is a collection of (JSON) documents uniquely identified by a name or an alias.

- An index is akin to a database table. 
- Indices are typically named by **source**: `winlogbeat-*`, `filebeat-*`, `packetbeat-*`, etc.

>A **shard** refers to a fundamental unit of data distribution and storage.

- Elastic distributes data across nodes by subdividing an index into **shards**. 
- Each index in Elasticsearch is a grouping of one or more physical shards, where each shard is a self-contained Lucene index containing a subset of the documents in the index.
- There are two types of shards in Elastic:
	- **Primary shards**
		- Each index is divided into one or more primary shards.
		- These shards hold the original data and are responsible for indexing and searching. 
		- The number of primary shards is set when the index is created and **cannot be changed afterward**.
	- **Secondary shards**
		- These are copies of primary shards, created for redundancy and improved query performance. 
		- They ensure data availability in case of node failure and can handle read requests (searches, retrievals), reducing the load on primary shards.
- Primaries accept writes, replicas provide read throughput and redundancy.

```
Cluster
 ├── Node
 │    ├── Shard (primary)
 │    └── Shard (replica)
```

- Each stored document is a **JSON object**. 


>[!example]+
> Here is an example of what a failed SSH login might look like after ingestion:
> 
> ```json
> {
>   "@timestamp": "2026-03-16T12:22:41Z",
>   "source.ip": "10.10.14.8",
>   "destination.port": 22,
>   "event.category": "authentication",
>   "event.outcome": "failure",
>   "event.type": "start",
>   "user.name": "root",
>   "host.name": "web01",
>   "message": "Failed password for root from 10.10.14.8 port 43210 ssh2"
> }
> ```


### Logstash

>**Logstash** is an open-source, server-side data processing pipeline that ingests data from a wide variety of sources, transforms it in real time, and then sends it to a desired destination — commonly Elasticsearch, but also databases, files, or message queues.

A pipeline processor — it collects data from sources, transforms it (parsing, enriching, filtering), and forwards it to Elasticsearch or other destinations. Logstash uses a three-stage model:

- **Input plugins**
	- An input plugin enables a specific source of events to be read by Logstash.
	- Input plugins define where data comes from: files, TCP sockets, Syslog, Kafka, HTTP, etc.
	- See [`Input plugins — Elastic Docs`](https://www.elastic.co/docs/reference/logstash/plugins/input-plugins).
- **Filter plugins**
	- A filter plugin performs intermediary processing on an event. Filters are often applied conditionally depending on the characteristics of the event.
	- So, filter plugins transform and enrich events, e.g., `grok` for pattern matching, `mutate` for field manipulation, `geoip` for IP enrichment, `translate` for lookups.
	- See [`Filter plugins — Elsatic Docs`](https://www.elastic.co/docs/reference/logstash/plugins/filter-plugins).
- **Output plugins**
	- An **output plugin** sends event data to a particular destination. Outputs are the final stage in the event pipeline.
	- For example, output plugins can forward parsed events to Elasticsearch, S3, Kafka, or flat files.
	- See [`Output plugins — Elastic Docs`](https://www.elastic.co/guide/en/logstash/current/output-plugins.html).

Logstash is where normalization happens. Raw Syslog, Windows Event Log XML, Zeek logs, and Suricata alerts all look wildly different — Logstash is what makes them query-able in a consistent format.

### Beats

>**Elastic Beats** are a family of lightweight, open-source data *shippers* designed to collect and send operational data — such as logs, metrics, network packets, and audit data — from servers, containers, and cloud environments to **Elasticsearch** or **Logstash** for further processing and visualization in **Kibana**.


Key Beats:

| Beat                                                                   | Data Collected                                                                                                                                                                                                                                                                |
| ---------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`Filebeat`](https://www.elastic.co/docs/reference/beats/filebeat)     | Forwards log data; monitors log files or locations you specify, collects log events, and forwards to Elasticsearch or Logstash.                                                                                                                                               |
| [`Packetbeat`](https://www.elastic.co/docs/reference/beats/packetbeat) | A real-time network packet analyzer; captures network traffic and records data.                                                                                                                                                                                               |
| [`Winlogbeat`](https://www.elastic.co/docs/reference/beats/winlogbeat) | Collects Windows Event Logs (Security, System, Application, Sysmon).                                                                                                                                                                                                          |
| [`Auditbeat`](https://www.elastic.co/docs/reference/beats/auditbeat)   | Collects audit events about users and processes running on systems, such as audit events from Linux Audit Framework.                                                                                                                                                          |
| [`Metricbeat`](https://www.elastic.co/docs/reference/beats/metricbeat) | Collects metrics from the OS and services running on the server; can monitor services like Apache, HAProxy, MongoDB, MySQL, Nginx, etc. See [Modules](https://www.elastic.co/docs/reference/beats/metricbeat/metricbeat-modules) for the complete list of supported services. |
| [`Heartbeat`](https://www.elastic.co/docs/reference/beats/heartbeat)   | Checks the services status and availability.                                                                                                                                                                                                                                  |

>[!note] For SIEM purposes, the most relevant are `Winlogbeat`, `Filebeat`, and `Auditbeat`. `Packetbeat` adds significant value for network-level detection.

>[!note] See [[Practical guide to Windows Event Logs]].

### Kibana

>**Kibana** is an open-source data visualization and exploration tool designed to work seamlessly with **Elasticsearch**.

The visualization and analysis front-end. Kibana talks to Elasticsearch directly and provides the UI for creating dashboards, running queries, and doing exploratory analysis. For incident response and threat hunting, you'll spend most of your time in **Discover** and **Dashboard** views.

>[!important] By default, Kibana runs on `http://localhost:5601`.
>![[elastic_home.png]]

## Helicopter view

- **What this architecture achieves?**
	- The goal is to collect high-volume telemetry, normalize it, store it as **searchable JSON documents**, and enable fast queries/aggregation for detection and investigation.
	- **Elastic handles ingestion, transformation, distributed storage, and visualization.**

>Documents are **JSON**; **mappings** define types and analyzers — mapping mistakes break queries.

- By default, data from Beats goes directly to Elasticsearch for processing. 
- Logstash is needed if you have logs of sources (like, hundreds or thousands) and want to transform or enrich that data before throwing it to Elasticsearch. 

**Full pipeline (Logstash for normalization):**
`Beats` -> `Logstash` -> `Elasticsearch` -> `Kibana`

![](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/211/beats1.png)

**Lightweight pipeline (direct ingestion):**
`Beats` -> `Elasticsearch` -> `Kibana`

![](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/211/beats2.png)

## Navigating Kibana and creating dashboards

>[!important] By default, Kibana runs on `http://localhost:5601`.

- Before you can search data in Kibana, an **index pattern** must be configured. An index pattern tells Kibana which Elasticsearch indices to query and which field to use as the time field (almost always `@timestamp`).

Common patterns for SIEM systems:

| Index          | Description                        |
| -------------- | ---------------------------------- |
| `winlogbeat-*` | Windows Event Logs.                |
| `filebeat-*`   | File-based logs.                   |
| `auditbeat-*`  | Linux audit events.                |
| `packetbeat-*` | Network data.                      |
| `logs-*`       | Elastic Agent unified data stream. |

### Building dashboards

~~Instead of flooding you with screenshots or cursed GIFs of me clicking around Kibana, I'll just drop a few videos that actually show what to do. Whoops.~~

- How to create dashboards and visualizations:

![](https://www.youtube.com/watch?v=DzGwmr8nKPg&t=14s)

- Exploring and querying data:

![](https://www.youtube.com/watch?v=t3cebUxRliA&list=PLhLSfisesZItoCPKxNHhttGkCTgCrAW2I&index=10)

- Interactive dashboards:

![](https://www.youtube.com/watch?v=SrdespambMg&list=PLhLSfisesZItoCPKxNHhttGkCTgCrAW2I&index=11)
## KQL

>**KQL (Kibana Query Language)** is a simple text-based query language used for filtering data in Kibana.

- KQL **only filters data**; it can't aggregate, transform, or sort data. 
- You can use KQL to filter documents where a value for a field exist, matches a given value, or is within a given range. KQL can match **numeric**, **text**, **date**, and **boolean values**.

>[!example]+
> Identify failed login attempts against disabled accounts that took place between March 3rd 2026 and March 6th 2026:
> 
> ```ruby
> event.code:4625 AND winlog.event_data.SubStatus:0xC0000072 AND @timestamp >= "2023-03-03T00:00:00.000Z" AND @timestamp <= "2023-03-06T23:59:59.999Z"
> ```
> 
> ![[query_1.png]]
> 
> 

### Matching fields

- Basic syntax:

```python
field:value
```

>[!important] When querying keyword, numeric, date, or boolean fields, the value **must be an exact match**, **including punctuation and case**. Text values are tokenized. 

>[!note] For aggregations and precise filtering on string fields, always use the `.keyword` sub-field — e.g., `user.name.keyword` rather than `user.name`. The base `text` field is tokenized and will match partial values, which produces false positives in exact-match contexts.

| Query                      | Description                                                                                |
| -------------------------- | ------------------------------------------------------------------------------------------ |
| `http.request.method: *`   | Match documents where the `http.request.method` field exists (any value).                  |
| `http.request.method: GET` | Match documents where `http.request.method` field is `GET` (exact match on keyword field). |
| `event.code: 4625`         | Match specific Windows event code (exact match on numeric value).                          |
| `user.name: *`             | Match all documents where the `user.name` field has a value.                               |

- The field parameter is optional. If not provided, all fields are searched for the given value.

| Query                            | Description                                                             |
| -------------------------------- | ----------------------------------------------------------------------- |
| `error`                          | Search all fields for `error`.                                          |
| `login failed`                   | Search fields that contains both words anywhere (e.g., `failed login`). |
| `"invalid password"`             | Exact phrase search.                                                    |
| `message: "invalid credentials"` | Exact phrase inside a specific field.                                   |

- Wildcards and patterns:

| Operator              | Description     | Example                                                                                  |
| --------------------- | --------------- | ---------------------------------------------------------------------------------------- |
| `field: "value*"`     | Wildcard match. | `field: admin*` — Matches `admin`, `administrator`, `admin2`, etc.                       |
| `field: /regex/`      | Regex match.    | `process.name: /.*\.exe$/` — Matches all `.exe` processes.                               |
| `field: [min TO max]` | Range query.    | `destination.port: [1024 TO 65535]` — Match any destination port from `1024` to `65535`. |
>[!tip] `*` can be used as an open-ended bound on either side of a range query, e.g., `bytes: [10000 TO *]`.

> [!warning] Wildcards at the beginning of a value (`*malware`) are very resource-intensive — they trigger a full index scan. Use them sparingly on large datasets.

### Date and time filtering

| Query                                                       | Meaning                                             |
| ----------------------------------------------------------- | --------------------------------------------------- |
| `@timestamp >= now-15m`                                     | Last 15 minutes.                                    |
| `@timestamp >= now-1h`                                      | Last hour.                                          |
| `@timestamp >= now-24h`                                     | Last 24 hours.                                      |
| `@timestamp >= now-7d`                                      | Last 7 days.                                        |
| `@timestamp >= now-1M`                                      | Last calendar month.                                |
| `@timestamp >= now/d`                                       | Since the start of today.                           |
| `@timestamp >= "2026-03-01T00:00:00Z"`                      | After specific date/time.                           |
| `@timestamp >= "2026-03-01" AND @timestamp <= "2026-03-07"` | Date range.                                         |
| `event.created >= now-5m`                                   | Recent events by creation time.                     |
| `@timestamp > now-7d/d`                                     | Events within last 7 days, rounded to day boundary. |
> [!tip]+
>The Kibana time picker (top-right) already applies a time filter globally. Explicit `@timestamp` filters in KQL are useful when you need a range _different_ from the global picker — e.g., correlating events from a specific incident window within a broader search context.

### Logical operators

| Operator | Description                                                  |
| -------- | ------------------------------------------------------------ |
| `AND`    | Logical `AND` — both conditions must match.                  |
| `OR`     | Logical `OR` — either condition must match.                  |
| `NOT`    | Logical `NOT` — exclude documents with matching expressions. |
| `()`     | Groups conditions to control precedence.                     |
>[!important] `AND` takes precedence over `OR`.

| Query                                    | Description                                                                                                     |
| ---------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `event.code: 4625 AND user.name: admin*` | Filter for failed logon attempts by users whose username starts with `admin` (e.g., `admin`, `administrator`.). |
| `NOT user.name: *$`                      | Exclude computer accounts (those ending with `$`).                                                              |
|                                          |                                                                                                                 |


>[!example]+
>- Display successful and failed logons:
> 
> ```ruby
> event.code: 4624 OR 4634
> ```
> 

> [!example]+
> - Find connections to non-standard ports:
> 
> ```ruby
> NOT destination.port: (80 or 443 or 53 or 3389)
> ```

>[!example]+
> ```ruby
> event.code: 4625 AND user.name: admin*
> ```
> 
> ![[query_2.png]]

```ruby
process.name:cmd.exe OR process.name:powershell.exe
```

```ruby
NOT source.ip:10.0.0.1
```

```ruby
NOT process.name: "svchost.exe"
```


| Query                     | Description           | Example                                   |
| ------------------------- | --------------------- | ----------------------------------------- |
| `tolower(field)`          | Convert to lowercase. | `tolower(user):"admin"`                   |
| `todate(field)`           | Convert to date.      | `todate(log_time):"2023-10-01T12:00:00Z"` |
| `match(field, "pattern")` | Regex match.          | `match(process.name, "\.exe$")`           |

>[!tip] You should use the `.keyword` field when it comes to aggregations.

### Functions

| Function                  | Usage                           | Example                                    |
| ------------------------- | ------------------------------- | ------------------------------------------ |
| `tolower(field)`          | Case-insensitive match.         | `tolower(user.name): "administrator"`      |
| `todate(field)`           | Convert field to date.          | `todate(log_time): "2026-03-01T12:00:00Z"` |
| `match(field, "pattern")` | Regex match (alternate syntax). | `match(process.name, "\.exe$")`            |

## The Elastic Common Schema (ECS)

>**Elastic Common Schema (ECS)** is an open-source specification developed by Elastic with community support to define a consistent and standardized set of fields for storing event data in Elasticsearch.

- ECS specifies field names and Elasticsearch datatypes for each field, provides descriptions and usage examples. 
- ECS also groups fields into ECS levels, which are used to signal how much a field is expected to be present.


### Key fields

- The most commonly used fields:

|Field Set|Key Fields|Notes|
|---|---|---|
|**Event**|`event.code`, `event.category`, `event.action`, `event.outcome`, `event.type`|Core classification fields. Always start here.|
|**User**|`user.name`, `user.id`, `user.domain`|The subject of the action|
|**Process**|`process.name`, `process.pid`, `process.parent.name`, `process.args`, `process.executable`|Critical for EDR-style detection|
|**Host**|`host.name`, `host.ip`, `host.os.type`, `host.os.name`|Source machine context|
|**Source / Destination**|`source.ip`, `source.port`, `destination.ip`, `destination.port`|Network connections|
|**Network**|`network.protocol`, `network.direction`, `network.bytes`|Higher-level network context|
|**File**|`file.name`, `file.path`, `file.hash.md5`, `file.hash.sha256`|File operations, malware detection|
|**Registry**|`registry.path`, `registry.value`, `registry.data.strings`|Windows registry persistence|
|**DNS**|`dns.question.name`, `dns.question.type`, `dns.resolved_ip`|DNS-based C2 detection|
|**HTTP**|`http.request.method`, `http.request.referrer`, `url.full`, `user_agent.original`|Web traffic analysis|
|**TLS**|`tls.server.subject`, `tls.version`, `tls.cipher`|Encrypted traffic analysis|
|**Threat**|`threat.tactic.name`, `threat.technique.id`|MITRE ATT&CK mapping|
|**Winlog**|`winlog.event_data.*`, `winlog.channel`|Windows-specific fields not in base ECS|

### ECS field reference

- [`ECS field reference`](https://www.elastic.co/docs/reference/ecs/ecs-field-reference):

| Field Set                                                                      | Description                                                                              |
| ------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------- |
| [Base](https://www.elastic.co/docs/reference/ecs/ecs-base)                     | All fields defined directly at the root of the events.                                   |
| [Agent](https://www.elastic.co/docs/reference/ecs/ecs-agent)                   | Fields about the monitoring agent.                                                       |
| [Autonomous System](https://www.elastic.co/docs/reference/ecs/ecs-as)          | Fields describing an Autonomous System (Internet routing prefix).                        |
| [Client](https://www.elastic.co/docs/reference/ecs/ecs-client)                 | Fields about the client side of a network connection, used with server.                  |
| [Cloud](https://www.elastic.co/docs/reference/ecs/ecs-cloud)                   | Fields about the cloud resource.                                                         |
| [Code Signature](https://www.elastic.co/docs/reference/ecs/ecs-code_signature) | These fields contain information about binary code signatures.                           |
| [Container](https://www.elastic.co/docs/reference/ecs/ecs-container)           | Fields describing the container that generated this event.                               |
| [Data Stream](https://www.elastic.co/docs/reference/ecs/ecs-data_stream)       | The data_stream fields take part in defining the new data stream naming scheme.          |
| [Destination](https://www.elastic.co/docs/reference/ecs/ecs-destination)       | Fields about the destination side of a network connection, used with source.             |
| [Device](https://www.elastic.co/docs/reference/ecs/ecs-device)                 | Fields characterizing a (mobile) device a process or application is running on.          |
| [DLL](https://www.elastic.co/docs/reference/ecs/ecs-dll)                       | These fields contain information about code libraries dynamically loaded into processes. |
| [DNS](https://www.elastic.co/docs/reference/ecs/ecs-dns)                       | Fields describing DNS queries and answers.                                               |
| [ECS](https://www.elastic.co/docs/reference/ecs/ecs-ecs)                       | Meta-information specific to ECS.                                                        |
| [ELF Header](https://www.elastic.co/docs/reference/ecs/ecs-elf)                | These fields contain Linux Executable Linkable Format (ELF) metadata.                    |
| [Email](https://www.elastic.co/docs/reference/ecs/ecs-email)                   | Describes an email transaction.                                                          |
| [Entity](https://www.elastic.co/docs/reference/ecs/ecs-entity)                 | Fields to describe various types of entities across IT environments.                     |
| [Error](https://www.elastic.co/docs/reference/ecs/ecs-error)                   | Fields about errors of any kind.                                                         |
| [Event](https://www.elastic.co/docs/reference/ecs/ecs-event)                   | Fields breaking down the event details.                                                  |
| [FaaS](https://www.elastic.co/docs/reference/ecs/ecs-faas)                     | Fields describing functions as a service.                                                |
| [File](https://www.elastic.co/docs/reference/ecs/ecs-file)                     | Fields describing files.                                                                 |
| [Gen AI](https://www.elastic.co/docs/reference/ecs/ecs-gen_ai)                 | Fields on Generative Artificial Intelligence (GenAI) Models requests and responses       |
| [Geo](https://www.elastic.co/docs/reference/ecs/ecs-geo)                       | Fields describing a location.                                                            |
| [Group](https://www.elastic.co/docs/reference/ecs/ecs-group)                   | User's group relevant to the event.                                                      |
| [Hash](https://www.elastic.co/docs/reference/ecs/ecs-hash)                     | Hashes, usually file hashes.                                                             |
| [Host](https://www.elastic.co/docs/reference/ecs/ecs-host)                     | Fields describing the relevant computing instance.                                       |
| [HTTP](https://www.elastic.co/docs/reference/ecs/ecs-http)                     | Fields describing an HTTP request.                                                       |
| [Interface](https://www.elastic.co/docs/reference/ecs/ecs-interface)           | Fields to describe observer interface information.                                       |
| [Log](https://www.elastic.co/docs/reference/ecs/ecs-log)                       | Details about the event's logging mechanism.                                             |
| [Mach-O Header](https://www.elastic.co/docs/reference/ecs/ecs-macho)           | These fields contain Mac OS Mach Object file format (Mach-O) metadata.                   |
| [Network](https://www.elastic.co/docs/reference/ecs/ecs-network)               | Fields describing the communication path over which the event happened.                  |
| [Observer](https://www.elastic.co/docs/reference/ecs/ecs-observer)             | Fields describing an entity observing the event from outside the host.                   |
| [Orchestrator](https://www.elastic.co/docs/reference/ecs/ecs-orchestrator)     | Fields relevant to container orchestrators.                                              |
| [Organization](https://www.elastic.co/docs/reference/ecs/ecs-organization)     | Fields describing the organization or company the event is associated with.              |
| [Operating System](https://www.elastic.co/docs/reference/ecs/ecs-os)           | OS fields contain information about the operating system.                                |
| [Package](https://www.elastic.co/docs/reference/ecs/ecs-package)               | These fields contain information about an installed software package.                    |
| [PE Header](https://www.elastic.co/docs/reference/ecs/ecs-pe)                  | These fields contain Windows Portable Executable (PE) metadata.                          |
| [Process](https://www.elastic.co/docs/reference/ecs/ecs-process)               | These fields contain information about a process.                                        |
| [Registry](https://www.elastic.co/docs/reference/ecs/ecs-registry)             | Fields related to Windows Registry operations.                                           |
| [Related](https://www.elastic.co/docs/reference/ecs/ecs-related)               | Fields meant to facilitate pivoting around a piece of data.                              |
| [Risk information](https://www.elastic.co/docs/reference/ecs/ecs-risk)         | Fields for describing risk score and level.                                              |
| [Rule](https://www.elastic.co/docs/reference/ecs/ecs-rule)                     | Fields to capture details about rules used to generate alerts or other notable events.   |
| [Server](https://www.elastic.co/docs/reference/ecs/ecs-server)                 | Fields about the server side of a network connection, used with client.                  |
| [Service](https://www.elastic.co/docs/reference/ecs/ecs-service)               | Fields describing the service for or from which the data was collected.                  |
| [Source](https://www.elastic.co/docs/reference/ecs/ecs-source)                 | Fields about the source side of a network connection, used with destination.             |
| [Threat](https://www.elastic.co/docs/reference/ecs/ecs-threat)                 | Fields to classify events and alerts according to a threat taxonomy.                     |
| [TLS](https://www.elastic.co/docs/reference/ecs/ecs-tls)                       | Fields describing a TLS connection.                                                      |
| [Tracing](https://www.elastic.co/docs/reference/ecs/ecs-tracing)               | Fields related to distributed tracing.                                                   |
| [URL](https://www.elastic.co/docs/reference/ecs/ecs-url)                       | Fields that let you store URLs in various forms.                                         |
| [User](https://www.elastic.co/docs/reference/ecs/ecs-user)                     | Fields to describe the user relevant to the event.                                       |
| [User agent](https://www.elastic.co/docs/reference/ecs/ecs-user_agent)         | Fields to describe a browser user_agent string.                                          |
| [VLAN](https://www.elastic.co/docs/reference/ecs/ecs-vlan)                     | Fields to describe observed VLAN information.                                            |
| [Volume](https://www.elastic.co/docs/reference/ecs/ecs-volume)                 | Fields related to storage volume details.                                                |
| [Vulnerability](https://www.elastic.co/docs/reference/ecs/ecs-vulnerability)   | Fields to describe the vulnerability relevant to an event.                               |
| [x509 Certificate](https://www.elastic.co/docs/reference/ecs/ecs-x509)         | These fields contain x509 certificate metadata.                                          |


## Resources and further reading


- [`KQL — Elasic Docs`](https://www.elastic.co/docs/explore-analyze/query-filter/languages/kql)
- [`Elastic Common Schema (ECS) reference — Elastic Docs`](https://www.elastic.co/docs/reference/ecs)


- [`Clusters, nodes, and shards — Elastic Docs`](https://www.elastic.co/docs/deploy-manage/distributed-architecture/clusters-nodes-shards)

- [`Node roles — Elastic Docs`](https://www.elastic.co/docs/deploy-manage/distributed-architecture/clusters-nodes-shards/node-roles#node-roles-list)
- [`Index basics — Elastic Docs`](https://www.elastic.co/docs/manage-data/data-store/index-basics)




- [`Input plugins — Elastic Docs`](https://www.elastic.co/docs/reference/logstash/plugins/input-plugins)
- [`Filter plugins — Elsatic Docs`](https://www.elastic.co/docs/reference/logstash/plugins/filter-plugins)
- [`Output plugins — Elastic Docs`](https://www.elastic.co/guide/en/logstash/current/output-plugins.html)

- [`Beats — Elastic Docs`](https://www.elastic.co/docs/reference/beats)
