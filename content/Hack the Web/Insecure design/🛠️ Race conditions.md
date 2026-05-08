---
created: 2026-05-03
sticker: lucide//fast-forward
---
## Race conditions

>**Race conditions** are concurrency vulnerabilities caused by unsynchronized access to shared state.

- Race conditions occur when **two or more execution contexts** (threads, processes, or network requests) access and modify the **same shared resource** (database record, file, network state) **concurrently** **without proper synchronization.** 
- The final outcome of an operation becomes dependent on *timing* and *execution order* rather than program logic.

- A race condition exists when all of the following conditions hold:
	
	- **Shared mutable state**
		- Multiple execution contexts interact with the **same resource or state**, such as a database record, session or authorization state, file, counter, etc.
	
	- **Concurrent or interleaved execution**
		- Multiple operations *may overlap in time* (either via true parallelism or scheduler interleaving).
		- This includes multithreading, async workers, distributed services, HTTP/2 multiplexing, queue consumers, etc.
	
	- **Non-atomic operations**
		- A logical operation is **decomposed into multiple observable steps**.
			- `read → modify → write`
		- This introduces a **time-of-check to time-of-use (TOCTOU) window**, where state can change between steps.
	
	- **Lack of synchronization or exclusivity guarantees**
		- The system does not enforce exclusivity or atomicity over the critical section.
		- Missing or insufficient controls include:
			- Locks / mutexes
			- Transactions (ACID isolation)
			- Compare-and-swap (CAS)
			- Optimistic locking
			- Idempotency keys
			- Distributed locking mechanisms

## Race windows & TOCTOU

> A **race window** is the finite time interval between the point at which an application reads a value from a shared resource (the check) and the point at which the application commits its state update back to that resource (the use). 

- Any concurrent operation that reads the same resource within this interval will observe stale state and may proceed on incorrect assumptions.
- Race conditions lead to *collisions*.

>A **collision** occurs when multiple concurrent execution contexts access and modify the same shared resource within a race window. 

- The most common type of race conditions is **TOCTOU**.

> **TOCTOU (Time-of-Check to Time-of-Use)** race conditions, also called **limit overrun**, occur when a security check operates on a value read from **shared state**, and a **concurrent operation modifies that state between the check and the subsequent action**. The checking thread acts on data that no longer reflects reality.

> [!note] Non-determinism 
> Race condition bugs are **non-deterministic**. 
>- A **non-deterministic bug** is one that does not always occur when a program is run with the same inputs. 
>- Deterministic bugs occur consistently given the same inputs, but non-deterministic bugs may or may not manifest depending on unpredictable conditions.
> 
> Whether a collision occurs depends on thread scheduling, CPU load, database connection pooling behavior, and precise network timing — none of which an attacker controls directly.

### Canonical example — coupon redemption

- An online store offers a one-use discount coupon worth $20. The coupon redemption process works as follows:
	
	1. Check if the user has already used the coupon. The state is stored as a database record.
		- `coupon_used = false` — The coupon hasn't been used yet.
		- `coupon_used = true` —  The coupon has already been used.
	2. If the coupon is marked as not used (`coupon_used = false`), apply the $20 discount. 
	3. Marks the coupon as used (`coupon_used = true`).


- Under normal sequential execution, this works just fine:

![[race_conditions_1.svg]]


- But if the user sends two coupon redemption requests almost at the same time (millisecond difference), the following happens:

	1. The application receives two coupon redemption requests and creates **two concurrent threads** to handle them — Thread 1 and Thread 2.
	2. Thread 1 checks if the code has already been used (`coupon_used = false`), then applies the discount. 
	3. Almost at the same time, Thread 2 checks if the code has already been used, too; the database record has not been changed by Thread 1 yet (`coupon_used = false`). **Thread 2 applies the discount**.
	4. Thread 1 changes the database record to mark the coupon as used (`coupon_used = true`). 
	5. Thread 2 changes the database record to mark the coupon as used (`coupon_used = true`). 
- Both threads pass the check independently, and **the discount is applied twice**.
- The race window here is the gap between step 2 and step 4; most commonly, it's in the rage of **1–10 milliseconds**.
- Diagrams show this better:
![[race_conditions_2.svg]]


- Example timing:

| Time, ms | Request 1                                                        | Time ms | Request 2                                                        | `discount_already_used` |
| -------- | ---------------------------------------------------------------- | ------- | ---------------------------------------------------------------- | ----------------------- |
| `00:00`  | Submit a discount code                                           |         |                                                                  | `false`                 |
| `00:01`  | Check if the code has already been used (`coupon_used = false`). | `00:01` | Submit a discount code                                           | `false`                 |
| `00:02`  | Apply the discount.                                              | `00:02` | Check if the code has already been used (`coupon_used = false`). | `false`                 |
| `00:03`  | Mark the code as used (`coupon_used = true`).                    | `00:03` | Apply the discount.                                              | `true`                  |
| `00:04`  |                                                                  | `00:04` | Mark the code as used (`coupon_used = true`).                    | `true`                  |

### Other vulnerable patterns

TOCTOU manifests across many common application features:

- **Financial operations** — concurrent withdrawal or transfer requests exceeding an account balance.
- **Vote / rating systems** — submitting multiple votes when a single-vote constraint is enforced.
- **Invite redemption** — claiming a single-use registration token more than once.
- **Anti-brute-force rate limiting** — bypassing failed login attempt counters (covered separately below).
- **Gift card / promo code redemption** — the same mechanics as coupon redemption above.

## The network jitter problem 

>[!important] To trigger a race condition, concurrent requests must arrive at the server **within the same race window**, which is often **just a few milliseconds wide**.

- The primarily obstacle to achieve this timing is **network jitter**.

>**Network jitter** is the *statistical variability in per-packet transmission latency*, or delay, across a network path.

- This means that two packets sent from the same host simultaneously will arrive at the destination host with **unpredictably different delays**.
- Jitter is typically measured in milliseconds, but given tight race windows, this is enough to  make attempts to exploit race conditions unreliable or nearly impossible, especially if the target is far away.

>[!interesting] Causes of network jitter
>- Variable routing paths.
>- Queuing delays at intermediate nodes (occurs under load).
>- Transmission speed differences (different link bandwidths).
>- Packet loss and re-transmission events.

>[!note] The farther the attacker is geographically from the target, the larger the jitter. 

## Overcoming jitter — HTTP/1.1 and last-byte synchronization

- HTTP/1.1 is fundamentally sequential; a single TCP connection carries **one request at a time**. 
- To work around this, browsers open 6-8 parallel TCP connections to the same server.
- However, each connection is independently subject to jitter, so even if several requests are sent at exactly the same time over those parallel connections, they're very unlikely to arrive at the same time.

But there's one technique that can help — **last-byte synchronization**.

>**Last-byte synchronization**, or **last-byte sync**, is a technique used to mitigate network jitter over HTTP/1.1. It works by sending most of the request data (e.g., readers and body) while withholding the **final byte**, and then sending the last byte across all connections at the same time to trigger concurrent server processing.

- Last-byte synchronization exploits two properties of TCP and HTTP:

	1. TCP is a stream protocol. An HTTP request body can be *split across multiple TCP packets*.
	2. An HTTP/1.1 server begins processing a request only when it receives the complete request, including the terminal byte.

- The attack proceeds as follows:
	1. Open multiple parallel TCP connections to the target — one per request.
	2. Send each request across its respective connection, **withholding the final byte** of each request body.
	3. The server receives partial request and buffers them, waiting for each complete. No processing beings yet.
	4. Simultaneously send the withheld final byte across all connections.
	5. All requests become complete at **virtually the same instant**. The server begins processing all of them at *approximately the same time*.

- Because the final frame for each request is a single byte, network jitter has minimal impact on their arrival times relative to one another. The bulk of the data was already buffered; only the 1-byte trigger packet matters for timing.

---
- **Burp Repeater** uses last-byte synchronization automatically when you use `Send group in parallel` over HTTP/1.1 connections. 
- **Turbo Intruder** implements last-byte synchronization via the `gate` mechanism — requests are queued with a gate ID and `envine.openGate()` releases all of them simultaneously. 

> [!warning]+ Limitations
> - Last-byte sync is not perfect. Each request still travels over a separate TCP connection, so inter-connection jitter still contributes. 
> - The technique reduces the spread significantly but cannot eliminate it. Benchmark data from [James Kettle's research](https://portswigger.net/research/smashing-the-state-machine) shows a median spread of **4 ms** with a standard deviation of **3 ms** — workable, but still insufficient for very tight race windows. 

HTTP/2 does better.
## Overcoming jitter — HTTP/2 and the single-packet attack

- HTTP/2 replaces HTTP/1.1's sequential text-based model with a binary framing layer. 
- Multiple logical request/response exchanges — called **streams** — are **multiplexed over a single TCP connection**.
- Each HTTP/2 message is split into frames tagged with a stream identifier, so that the client and server can **interleave and reassemble frames from different messages** without ambiguity. 
- This means that **multiple requests can be sent concurrently over one TCP connection**, without the need to establish separate connections and suffer from jitter.

This fact is used by the **single-packet attack**.

> The **single-packet attack**, developed by James Kettle and introduced at Black Hat USA 2023, is a technique that **packs multiple complete HTTP/2 requests into a single TCP packet** to eliminate network jitter almost entirely.

- Because all requests are contained in a single TCP packet, they **arrive at the server simultaneously** — with a millisecond precision. The server processes all of them starting from the same point in time.

>[!note]+ **Benchmark results** (Melbourne → Dublin, 17,000km, 17,000 repetitions):
> 
> | Technique            | Median spread | Standard deviation |
> | -------------------- | ------------- | ------------------ |
> | Last-byte sync       | 4ms           | 3ms                |
> | Single-packet attack | 1ms           | 0.3ms              |
>
> The single-packet attack is **4–10× more effective** than last-byte sync. In practice: when Kettle replicated one real-world vulnerability, the single-packet attack succeeded in ~30 seconds; last-byte sync took over two hours.
 
## Exploitation

- A few key points to remember:

>[!important] To trigger a race condition, concurrent requests must arrive at the server **within the same race window**, which is often **just a few milliseconds wide**.


### How It Works — Under the Hood

The technique adapts the core idea of last-byte sync to HTTP/2's framing model, and exploits **Nagle's algorithm** at the TCP layer to batch final frames into a single packet without requiring a custom TCP/TLS stack.

The protocol-level steps are:

1. **Pre-send the bulk of each request**: For requests with a body, send all headers and all body data _except the final byte_. For requests with no body, send all headers but withhold the empty `END_STREAM` data frame. Do **not** set the `END_STREAM` flag on any pre-sent frame.
    
2. **Prepare the release**: Wait approximately 100 ms after pre-sending to ensure that initial frames have been flushed over the wire. **Disable `TCP_NODELAY`** — this is critical, because it enables Nagle's algorithm to coalesce the final frames into a single TCP packet. Send a ping packet to warm the local connection (prevents the first final frame from landing in a separate packet due to OS network stack behavior).
    
3. **Release simultaneously**: Send all withheld final frames. Because Nagle's algorithm is active and all frames are queued nearly simultaneously, the OS batches them into a single TCP segment. All requests arrive at the server in the same network event.
    

> [!note] Why `TCP_NODELAY` must be disabled `TCP_NODELAY` disables Nagle's algorithm. Nagle's algorithm deliberately delays transmission of small packets to coalesce them with subsequent data. If `TCP_NODELAY` is enabled, each final byte is flushed immediately as its own packet — defeating the entire approach. With Nagle's algorithm active, all final frames are held briefly and sent together.

> [!note] Static files The single-packet attack doesn't work for static files on certain servers. In Turbo Intruder, this manifests as a negative timestamp (response received before the request "completed"). Use this as a quick check to determine whether an endpoint is static or dynamic.

### Connection Warming

Many production applications sit behind reverse proxies or load balancers. These components may route requests over _existing_ keep-alive connections to the backend, or over _freshly established_ connections — and this decision can introduce per-request timing variability that looks like application-level jitter.

To normalize this, use **connection warming**: send a few throwaway requests down the same HTTP/2 connection before executing the attack. This ensures the front-end-to-back-end connection is already established and cached, so the attack requests all travel the same pre-warmed path.

```
# Conceptual warming sequence (Turbo Intruder)
# Send 3-5 innocuous requests (e.g., GET /) to the target before queueing attack requests
# This can be done by queuing warm-up requests first, then the actual attack gate
```

---

## Attack types

### Limit overrun (classic TOCTOU)

The simplest and most common class. Send multiple parallel requests to an endpoint that enforces a limit using a check-then-act pattern. The goal is for all requests to pass the check before any of them complete the state update.

**Target patterns**:

- Single-use coupon/discount codes
- Gift card redemption
- Vote/rating submission with a per-user limit
- Email confirmation token reuse
- File-per-user creation limits

**Attack**: Send N identical (or near-identical) requests simultaneously using the single-packet attack. One or more should bypass the limit.

### Class 2 — Rate Limit Bypass

Rate limiting is a common defense against brute-force attacks. It typically works by maintaining a server-side counter (per user or per IP) that is incremented on each failed attempt and checked before the next attempt is processed.

This pattern is inherently vulnerable to a TOCTOU race: the counter check and the counter increment are separate operations. If you send a burst of parallel login attempts simultaneously, many of them will pass the check before any increments the counter.

**Scenario**: The application blocks login after 3 failed attempts within a time window. The race window exists between the read of the counter and the write of the incremented value.

**Attack**: Send 20–30 parallel login attempts in a single packet. Many will complete their check before the counter reflects any failed attempt. You effectively get N-1 uncounted attempts per burst.

```
# Turbo Intruder: HTTP/2 single-packet rate-limit bypass
# See Tooling section for full script
```

### Class 3 — Multi-Endpoint Sub-State Exploitation

The most powerful and underexplored class. This does not require a simple limit overrun. Instead, it abuses the fact that every HTTP request internally transitions an application through a series of **sub-states** before reaching a final state — and those sub-states may have weaker security postures than the final state.

This is covered in depth in the [[#Sub-States and Hidden Multi-Step Transitions]] section.

### Class 4 — Single-Endpoint Sub-State (Colliding Requests on One Endpoint)

Two requests to the _same_ endpoint targeting _different_ parameters or data items can collide if the endpoint writes to a shared session or shared data structure. The most illustrative real-world case discovered by Kettle: sending simultaneous password reset requests for _two different email addresses_ from the same session caused the session to contain one user's ID paired with the other user's reset token — a cross-account token oracle.

The key insight: the vulnerability is **keyed on session ID**, not on the specific email address. Both requests modify the same session record concurrently.

---

## Sub-States and Hidden Multi-Step Transitions

> A **state** is a persistent representation of a condition of a system or resource at a given point in time, typically stored server-side in a database, session store, or cache.

> A **sub-state** is a transient intermediate condition that an application occupies during the processing of a single request, prior to the request completing and the final state being committed. Sub-states are invisible to users, typically persist for sub-millisecond to low-millisecond durations, and often carry weaker security invariants than the terminal state.

James Kettle's central insight in _Smashing the State Machine_ is this: **with race conditions, everything is multi-step**. Even an operation that appears atomic from the outside — "apply coupon", "log in", "confirm email" — is internally a sequence of reads, validations, writes, and side-effects. If a second request can interact with the same resource while the first request is mid-sequence, the application may behave in ways its authors never anticipated.

### MFA Bypass via Sub-State Collision

The following pattern is directly testable and BSCP-relevant.

A vulnerable MFA login flow:

```python
@app.route('/login', methods=['POST'])
def login():
    # Step 1: validate credentials
    user = users_db.get(username)
    if not user or not verify_password(user, password):
        return "Invalid credentials", 401

    # Step 2: issue session BEFORE MFA is enforced
    session['userid'] = user['userid']       # <-- logged in at this point

    if user['mfa_enabled']:
        session['mfa_verified'] = False       # <-- sub-state: logged in, MFA pending
        send_mfa_code(user)
        return redirect('/mfa')
    else:
        session['mfa_verified'] = True
        return "Login successful", 200

@app.route('/sensitive')
def sensitive():
    if 'userid' not in session:
        return "Not logged in", 401
    if not session.get('mfa_verified', False):
        return "MFA required", 403            # <-- this check is the target
    return "Sensitive data", 200
```

The race window exists between the moment `session['userid']` is set (step 2) and the moment the redirect to `/mfa` completes — during which `mfa_verified` is `False` but a valid session already exists. If a second request to `/sensitive` arrives and is processed during this sub-state window, the `userid` check passes but the `mfa_verified` check hasn't been enforced yet for the _current_ MFA cycle.

**Attack**:

1. Initiate a login request to `/login` with valid credentials.
2. Simultaneously send a request to `/sensitive` with the same session cookie.
3. The `/sensitive` request may land during the sub-state window — after `session['userid']` is written, before `mfa_verified` is set or the MFA redirect is processed.

> [!note] PHP session locking PHP locks on the session ID by default. Concurrent requests using the _same_ PHP session will be processed sequentially, not in parallel. To attack PHP sub-states, you must use separate sessions, or find another shared resource the two requests operate on. This is not a general protection — other frameworks do not have this behavior.

### Role Privilege Sub-State

A real-world example from Kettle's research: an application initialized every new session with **administrator privileges**, then immediately overwrote them with the user's actual role when the browser followed a redirect to `/role`. The sub-state window between session creation and role assignment would grant admin access to any request that arrived during that window.

```
POST /login → 302 → GET /role (overwrites session role)
                         ^
                         |
              Race window here: session has admin role
              before /role request fires
```

An attacker who initiated a login and immediately (in parallel) sent a request to a privileged endpoint could land that second request during the sub-state — before the role was downgraded.

---

## Three-Phase Exploitation Methodology

PortSwigger's black-box methodology for discovering and exploiting race conditions, as developed by James Kettle. Apply this even when you have source code access — static analysis of concurrent code paths is notoriously unreliable.

### Phase 1 — Predict Potential Collisions

Map the application and identify endpoints that are worth attacking. Not every endpoint is a candidate. Apply three filters:

**Filter 1: Is the state stored server-side and persistently?**

- Candidates: database records, session stores, file system objects, cache entries
- Discard: client-side state (JWT payloads, URL-embedded tokens), purely stateless flows

**Filter 2: Does the endpoint edit existing data, or only append new data?**

- Candidates: update operations — changing an email address, applying a discount, modifying a role, confirming a token
- Low-value: append-only operations — adding an additional email address to a list, inserting a new record with a new key

**Filter 3: What key does the operation use? Do concurrent requests share the same key?**

Two requests must operate on the **same record** to produce a collision. Identify the key that selects the affected row/document:

- User ID / username
- Session ID
- Password reset token
- Email address
- Filename or resource ID

If two concurrent requests use _different_ keys, they modify different records — no collision is possible.

> [!note] Password reset token keying Consider two password reset implementations: one stores the reset token in `users` table, keyed on `userid`; the other stores it in the user's session, keyed on `session_id`. In the first, two simultaneous reset requests for different users modify different rows — no collision. In the second, two simultaneous reset requests for _different email addresses_ from the _same session_ both modify the same session record — collision is possible, and may result in session contamination where one user's ID is associated with another's token.

### Phase 2 — Probe for Clues (Benchmarking)

Once you have candidate endpoints, the goal is not yet to achieve a meaningful exploit — it's to detect evidence that hidden sub-states exist. This is an empirical, chaos-based phase.

**Step 1 — Benchmark baseline behavior**

Send your candidate requests _sequentially_ with deliberate delays (e.g., 1–2 seconds between each). Record:

- Response codes and body content
- Processing time per request
- Side effects: emails sent, state changes visible in the UI, session changes

This is your baseline. Any deviation from this baseline in concurrent execution is a clue.

**Step 2 — Send requests concurrently**

Send the same request group simultaneously using:

- **Single-packet attack** (preferred, HTTP/2)
- **Last-byte sync** (fallback, HTTP/1.1)

Use 20–30 requests per burst. In Turbo Intruder, assign all requests to the same gate and call `openGate()`. In Burp Repeater, group the requests and use **Send group in parallel**.

**Step 3 — Analyze deviations**

Anything that deviates from the baseline is a clue. Pay particular attention to:

|Observation|Possible Interpretation|
|---|---|
|Shorter processing time than baseline|Request handed off to a separate thread — high-value signal|
|Longer processing time than baseline|Locking or resource contention — may indicate protection _or_ a bottleneck you can stress|
|Different response content in some requests|State collision occurred; branching behavior under concurrency|
|Some requests returned unexpected status codes|A check was bypassed or an unexpected code path was hit|
|Second-order effects (duplicate emails, etc.)|Server-side sub-states triggered multiple side-effects|

Do not expect the exploit to succeed cleanly at this stage. A single anomalous response out of 20 is a meaningful signal.

### Phase 3 — Prove the Concept

With a clue in hand, refine the attack into a reliable exploit.

1. **Reduce noise**: Strip out requests that are not contributing to the collision. Send only the minimum set needed to trigger the race.
2. **Adjust timing**: For multi-endpoint attacks, the two requests don't always need to arrive simultaneously — they need to overlap within the race window. Experiment with small delays (1–5ms) between the trigger request and the racing request.
3. **Use connection warming**: Send 3–5 warm-up requests before the attack batch to normalize front-end routing behavior (see [[#Connection Warming]]).
4. **Repeat**: Race conditions are non-deterministic. Run the attack multiple times and look for consistent patterns, not a single success.
5. **Map the state machine**: Draw out what sub-states the trigger request creates, and what the racing request needs to observe. This prevents wasted effort and clarifies what constitutes a successful hit.

---

## Turbo Intruder

**Turbo Intruder** is a Burp Suite extension that provides fine-grained control over concurrent HTTP request delivery. Unlike Burp Intruder (which has deliberate rate limits and no concurrency primitives), Turbo Intruder uses async Python scripts to implement custom attack patterns, including single-packet attacks and gated parallel delivery.

### Installation

Available in the BApp Store from within Burp Suite → Extender → BApp Store → search "Turbo Intruder".

### Core Concepts

|Component|Purpose|
|---|---|
|`RequestEngine`|Manages HTTP connections, concurrency level, HTTP version, and request dispatch|
|`engine.queue()`|Schedules a request for delivery, optionally assigning it to a named gate|
|`engine.openGate()`|Releases all requests assigned to a gate simultaneously|
|`gate`|A named hold group — requests assigned to a gate are withheld until `openGate()` is called|
|`Engine.BURP2`|Selects Burp's HTTP/2 engine, enabling single-packet attack support|
|`concurrentConnections=1`|Forces a single TCP connection — required for HTTP/2 single-packet delivery|

### Template: Single-Packet Rate Limit Bypass

This is the standard template for bypassing rate-limited login endpoints using the single-packet attack over HTTP/2.

```python
def queueRequests(target, wordlists):

    # Engine.BURP2 enables HTTP/2
    # concurrentConnections=1 forces a single TCP connection → single-packet attack
    engine = RequestEngine(
        endpoint=target.endpoint,
        concurrentConnections=1,
        engine=Engine.BURP2
    )

    # Candidate password list — adjust for target context
    passwords = [
        "123456", "password", "12345678", "qwerty", "abc123",
        "monkey", "letmein", "dragon", "111111", "baseball",
        "iloveyou", "master", "sunshine", "princess", "welcome",
        "shadow", "superman", "michael", "football", "login"
    ]

    # Queue all requests under gate '1'
    # The gate withholds final frames until openGate() is called
    # %s is replaced with the payload (password) for each request
    for password in passwords:
        engine.queue(target.req, password, gate='1')

    # Release all queued requests simultaneously as a single TCP packet
    engine.openGate('1')


def handleResponse(req, interesting):
    # Add all responses to the results table for analysis
    table.add(req)
```

**Key parameters explained**:

- `target.req`: The raw HTTP request template captured in Burp. The `%s` placeholder in the request body is substituted with each password at queue time.
- `gate='1'`: All requests are held under this gate name. You can use multiple gates for staged attacks (e.g., `gate='warmup'` for warm-up requests, `gate='attack'` for the actual burst).
- `engine.openGate('1')`: Sends all withheld final frames. This is the moment of attack.

### Template: Multi-Endpoint Sub-State Attack

For sub-state attacks involving two different endpoints (e.g., triggering a login while simultaneously requesting a sensitive resource):

```python
def queueRequests(target, wordlists):

    engine = RequestEngine(
        endpoint=target.endpoint,
        concurrentConnections=1,
        engine=Engine.BURP2
    )

    # Connection warm-up: send a few requests to normalize front-end routing
    # These are sent without a gate, so they execute immediately and sequentially
    for i in range(5):
        engine.queue(target.req)  # innocuous warm-up request (e.g., GET /)

    # Queue the trigger request (e.g., POST /login) under the attack gate
    engine.queue(loginRequest, gate='race')

    # Queue multiple copies of the racing request (e.g., GET /sensitive)
    # Multiple copies compensate for server-side jitter
    for i in range(20):
        engine.queue(sensitiveRequest, gate='race')

    engine.openGate('race')


def handleResponse(req, interesting):
    table.add(req)
```

> [!note] Using multiple copies Sending 20 copies of the racing request serves two purposes. First, it compensates for server-side jitter — even with a single-packet delivery, the server may not schedule all threads at exactly the same time. Second, for sub-state attacks, only a subset of racing requests need to land during the brief sub-state window; more requests means a higher probability that at least one does.

### Template: HTTP/1.1 Last-Byte Sync Fallback

When the target doesn't support HTTP/2:

```python
def queueRequests(target, wordlists):

    # Engine.THREADED uses HTTP/1.1 with last-byte sync
    # concurrentConnections must match the number of requests for parallel delivery
    engine = RequestEngine(
        endpoint=target.endpoint,
        concurrentConnections=30,
        requestsPerConnection=1,      # One request per connection
        pipeline=False,
        engine=Engine.THREADED
    )

    for password in wordlists.clipboard:
        engine.queue(target.req, password, gate='1')

    engine.openGate('1')


def handleResponse(req, interesting):
    table.add(req)
```

### Placeholder Syntax

In the request template captured in Burp, mark payload injection points with `%s`:

```http
POST /login HTTP/2
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded

username=victim&password=%s
```

If you need to inject into multiple positions, you can pass a list as the payload argument or use `%s` multiple times (depending on Turbo Intruder version).

---

## Tooling — Burp Repeater Parallel Groups

For rapid, manual testing without scripting, Burp Repeater's **"Send group in parallel"** feature is sufficient for basic single-packet attack tests.

**Workflow**:

1. Capture the target request in Proxy and send it to Repeater.
2. Duplicate the tab as many times as needed (right-click → Duplicate tab).
3. Modify each tab's request as needed (e.g., different payload values).
4. Right-click any tab → Create tab group.
5. Name the group and add all relevant tabs.
6. From the Send dropdown → **Send group in parallel**.

Burp automatically uses:

- **Single-packet attack** if the target supports HTTP/2
- **Last-byte sync** if falling back to HTTP/1.1

This is fast enough for detection and proof-of-concept, but for large-scale parallel bursts (20+ requests), Turbo Intruder gives more control and visibility.

---

## Identifying Race Conditions in the Wild — Practical Checklist

Before reaching for an exploit, mentally run through this checklist:

```
[ ] Is the targeted state stored server-side? (database, session store, cache)
[ ] Does the operation EDIT an existing record (not just INSERT a new one)?
[ ] Do concurrent requests share the same key (same user, session, token, ID)?
[ ] Is there a visible CHECK before an ACT in the application's behavior?
[ ] Does the endpoint's normal response time suggest it performs multiple DB operations?
[ ] Does the endpoint trigger side-effects (emails, logs, status changes) that could be multiplied?
[ ] Does the application use a framework with known session locking behavior? (PHP: locked; most others: unlocked)
```

High-value targets to always test:

- `POST /apply-coupon` / `POST /redeem-code`
- `POST /login` (rate limit bypass)
- `POST /password-reset` / `POST /confirm-email`
- `POST /checkout` / `POST /transfer`
- Anything that changes a user's role, subscription, or permission level

---

## Defence and Detection

Understanding defences is required for BSCP — you need to recognize when a target is protected and what the protection looks like.

### Atomic Operations

The correct fix for most race conditions is to make the check-then-act sequence **atomic** — either as a single atomic database operation (e.g., a compare-and-swap or an `UPDATE ... WHERE coupon_used = false` that returns the number of affected rows), or within a database transaction with appropriate isolation.

```sql
-- Vulnerable (two separate operations, race window between them):
SELECT coupon_used FROM coupons WHERE id = ?;   -- check
UPDATE coupons SET coupon_used = true WHERE id = ?;  -- act

-- Protected (single atomic conditional update):
UPDATE coupons SET coupon_used = true
WHERE id = ? AND coupon_used = false;
-- Check rows_affected == 1; if 0, the coupon was already used
```

### Mutex / Advisory Locks

Database advisory locks or application-level mutexes can serialize access to critical code sections. If a target's response is _longer_ under concurrent load than under sequential load, this is a signal that locking may be in place.

### Session-Level Serialization

PHP serializes requests sharing the same session ID by default (`session.serialize_handler`). This means that concurrent requests with the same PHP session cookie will be queued and processed sequentially, not in parallel. This prevents session-based sub-state attacks but does not protect against attacks targeting shared database records via different sessions.

> [!note] Detecting session locking Send parallel requests with the same session token. If all responses arrive in sequence with artificially spaced timestamps (rather than all at the same time), session locking is probably active. Switch to different sessions per request when attacking such targets.

### Database Transaction Isolation

Proper use of `SERIALIZABLE` isolation level in database transactions prevents most TOCTOU races at the storage layer, at a performance cost. Most applications use `READ COMMITTED` (the default for PostgreSQL/MySQL), which does not prevent phantom reads within a transaction and leaves TOCTOU windows open.

---

## References and Further Reading

- [Smashing the State Machine: The True Potential of Web Race Conditions — James Kettle, PortSwigger Research (2023)](https://portswigger.net/research/smashing-the-state-machine)
- [Race Conditions — PortSwigger Web Security Academy](https://portswigger.net/web-security/race-conditions)
- [The Single-Packet Attack: Making Remote Race Conditions Local — PortSwigger Research](https://portswigger.net/research/the-single-packet-attack-making-remote-race-conditions-local)
- [Timeless Timing Attacks — Tom Van Goethem et al., USENIX Security 2020](https://www.usenix.org/conference/usenixsecurity20/presentation/van-goethem)
- [Race Conditions on the Web — Josip Franjković (2016)](https://www.josipfranjkovic.com/blog/race-conditions-on-web)
- [Turbo Intruder — GitHub](https://github.com/PortSwigger/turbo-intruder)
- [Nagle's Algorithm — Wikipedia](https://en.wikipedia.org/wiki/Nagle%27s_algorithm)