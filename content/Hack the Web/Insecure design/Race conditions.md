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

![[race_coupon_1.svg]]



- But if the user sends two coupon redemption requests almost at the same time (millisecond difference), the following happens:

	1. The application receives two coupon redemption requests and creates **two concurrent threads** to handle them — Thread 1 and Thread 2.
	2. Thread 1 checks if the code has already been used (`coupon_used = false`), then applies the discount. 
	3. Almost at the same time, Thread 2 checks if the code has already been used, too; the database record has not been changed by Thread 1 yet (`coupon_used = false`). **Thread 2 applies the discount**.
	4. Thread 1 changes the database record to mark the coupon as used (`coupon_used = true`). 
	5. Thread 2 changes the database record to mark the coupon as used (`coupon_used = true`). 
- Both threads pass the check independently, and **the discount is applied twice**.
- The race window here is the gap between step 2 and step 4; most commonly, it's in the rage of **1–10 milliseconds**.
- Diagrams show this better:
![[race_coupon_2.svg]]



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

![[jitter.svg|810]]

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

- HTTP/2 replaces HTTP/1.1’s sequential, text-based request/response model with a **binary framing layer**.
- Multiple logical request/response exchanges, called **streams**, can be **multiplexed over a single TCP connection**.
- Each HTTP/2 message is split into frames tagged with a **stream identifier**. This means that client and server can **interleave and reassemble frames from multiple messages concurrently** without ambiguity.
- As a result, **multiple requests can be sent simultaneously over a single TCP connection** — without the need to establish separate connections, each of which would introduce its own latency and jitter.

This property underpins the **single-packet attack**.

>The **single-packet attack**, introduced by James Kettle at Black Hat USA 2023, is a technique that **packs multiple complete HTTP/2 requests into a single TCP packet**, almost entirely eliminating network-induced jitter.

- Because all requests are delivered in a single TCP packet, they **arrive at the server nearly simultaneously**, with millisecond precision. The server begins processing each request from the same point in time.

>[!note]+ **Benchmark results** (Melbourne → Dublin, 17,000km, 17,000 repetitions)
> 
> | Technique            | Median spread | Standard deviation |
> | -------------------- | ------------- | ------------------ |
> | Last-byte sync       | 4ms           | 3ms                |
> | Single-packet attack | 1ms           | 0.3ms              |
>
> The single-packet attack is **4–10× more precise** than last-byte sync. In practical terms, when replicating a real-world vulnerability, the single-packet attack succeeded in ~30 seconds, whereas last-byte sync took over two hours.
### The single-packet attack under the hood

- The attack adapts the **last-byte sync concept** to HTTP/2’s framing model and exploits **Nagle’s algorithm** at the TCP layer to batch final frames into a single packet.


>[!note]+ Nagle's algorithm
> - [Nagle's algorithm](https://en.wikipedia.org/wiki/Nagle's_algorithm) is a TCP optimization that reduces network congestion by **aggregating small outgoing packets into larger segments** before sending them.
> - It buffers small packets until either:
>     1. Enough data accumulates to fill a Maximum Segment Size (MSS), or
>     2. An acknowledgment for previously sent data is received.
> - For example, if you send consecutive 1-byte packets:
>     - `1 byte`
>     - `1 byte`
>     - `1 byte`
>     - `1 byte`  
>     TCP will combine them into one larger packet.

1. **Pre-send the bulk of each request**
	- For requests **with a body**, send all headers and all body data **except the final byte**. 
	- For requests **without a body**, send all headers but **omit the `END_STREAM` flag** on the final frame.
	- The server can't process the frames yet because each request is **technically incomplete**.
    
2. **Prepare for simultaneous release**
	- Wait ~100 ms after pre-sending to ensure initial frames have reached the server.
	- **Disable `TCP_NODELAY`** (`TCP_NODELAY = OFF`) to activate Nagle's algorithm.
	- Optionally, send a **ping frame** to warm the connection This is used to prevent OS-level segmentation from splitting the final frames into separate packets.

>[!note]+ Why `TCP_NODELAY` must be `OFF` for the attack
> - With `TCP_NODELAY = ON` (Nagle's algorithm off) all small packets are sent separately.
> - With `TCP_NODELAY = OFF` (Nagle's algorithm on) the final frames are **temporarily held in a buffer** and then **sent together**. The attack relies on sending **the last byte of multiple requests in a single TCP segment** to ensure they arrive at the server simultaneously.

3. **Release simultaneously**
	- Send all withheld final frames. 
	- Because Nagle’s algorithm is active, the OS batches these frames into a **single TCP segment**, so all requests arrive at the same in the same network event.

>[!note]+ Static files
> - Some servers do not process static files in a way compatible with the single-packet attack.
> - In Turbo Intruder, this may appear as a **negative timestamp** (response recorded before the request “completes”). This is a useful check for distinguishing static vs. dynamic endpoints.

>[!note]+ Connection warming
> - Many production setups include reverse proxies or load balancers. These components may route requests over either **existing keep-alive connections** or **new connections**/ This introduces timing variability that resembles jitter.
> - To mitigate this, use **connection warming**: send a few throwaway requests (e.g., 3–5 `GET /`) over the target HTTP/2 connection before executing the attack. This ensures requests travel along the same pre-established path.

## Exploiting race conditions using Burp Suite
### Sending grouped HTTP requests in Repeater

To send a group of requests together:

1. Create a tab group and add relevant tabs to it:

![[repeater_new_tab_group.png]]

![[repeater_new_tab_group_name.png]]

2. If you need to repeat the same request multiple times, right-click on the request tab *inside the tab group* -> `Duplicate tab`, -> enter how many requests you want to send -> `Duplicate`. 

![[repeater_duplicate_tab.png]]

![[repeater_duplicate_tab_times.png]]

3. Click on the arrow near `Send` -> `Send group in parallel`:

![[repeater_single-packet_attack.png]]

4. Click `Send group (parallel)`:

![[repeater_send_group_parallel.png]]


>[!important]+ Sending request groups
> You have three options to send request groups in `Repeater`:
> 
> - **`Send group in sequence (single connection)`**
> 	- `Repeater` establishes a connection tot the target, sends the requests from all of the tabs in the group, then closes the connection.
> 	- All tabs must have the **same target**, and use the **same HTTP version** (i.e., they must either all use HTTP/1 or all use HTTP/2).
> - **`Send group in sequence (separate connections)`**
> 	- `Repeater` establishes a connection to the target, sends the requests from the first tab, then closes the connection. This process is repeated for all of the other tabs in the order they are arranged in the group.
> 
>>[!warning]+ To send requests in sequence, there must be **no WebSocket message tabs** in the group, and **no empty tabs** in the group.
> 
> - **`Send group in parallel`**
> 	- `Repeater` sends the requests from all of the group's tabs at once.
> 	- When sending over HTTP/1, `Repeater` uses **last-byte synchronization**.
> 	- When sending over HTTP/2, `Repeater` uses the **single-packet attack**.

### Turbo Intruder

>[`Turbo Intruder`](https://portswigger.net/bappstore/9abaa233088242e8be252cd4ff534988) is an open-source Burp Suite extension developed by James Kettle, designed to send large numbers of HTTP requests at extreme speeds and analyze the results.

- Turbo Intruder uses async Python scripts to implement custom attack patterns, including single-packet attacks and gated parallel delivery.
- You can install the extension from [`BApp Store`](https://portswigger.net/bappstore/9abaa233088242e8be252cd4ff534988): `Extensions` -> `BApp Store` -> `Turbo Intruder` -> `Install`.

>[!important] Turbo Intruder does not require Burp Suite Professional, and can be installed in Burp Suite Community.  

![[turbo_intruder.png]]

- To send a request to Turbo Intruder, right-click the request -> `Extensions` -> `Turbo Intruder` -> `Send to turbo intruder`:

![[images/walkthrough/PortSwigger/Race conditions/lab2/2.png]]

- Single-packet attack in Turbo Intruder:

```Python
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                            concurrentConnections=1,
                            engine=Engine.BURP2
                            )
    
    # queue 20 requests in gate '1'
    for i in range(20):
        engine.queue(target.req, gate='1')
    
    # send all requests in gate '1' in parallel
    engine.openGate('1')
        
```

- **`queueRequests(target, wordlists)`**: A **predefined function** that Turbo Intruder expects you to implement. Its job is to define the *attack logic*: how requests are queued and sent to the server.
- **`RequestEngine(endpoint, concurrentConnections, engine)`)**: Manages HTTP connections, concurrency level, HTTP version, and request dispatch.
	- **`endpoint`**: The base URL of the target website.
	- **`concurrentConnections`**: The number of TCP connections used concurrently; `1` forces a single TCP connection (for the single-packet attack).
	- **`engine`**: HTTP engine to use; `Engine.BURP2` selects Burp's HTTP/2 engine (required for the single-packet attack).

```Python
engine = RequestEngine(endpoint=target.endpoint,
                       concurrentConnections=1,
                       engine=Engine.BURP2)
```

- **`engine.queue(request, payload, gate=None)`**: Schedules a request for delivery; optionally assigns it to a named gate.
	- **`request`**: The HTTP request template to use; `target.req` specifies the raw HTTP request template captured in Burp.
	- **`payload`**: The value to insert into the payload placeholder(s) in the request marked with `%s`.
	- **`gate`** (optional): A label to group requests together; requests queued with the same gate are held until the gate is open. `'1'` specifies a gate with the string label `'1'`.

```Python
# schedule 20 identical requests
for i in range(20):
	engine.queue(target.req, gate='1')
	
# schedule requests for each value from a payload list
for password in passwords:
	engine.queue(target.req, password, gate='1')
```

>[!tip]+ You can use multiple gates for staged attacks (e.g., `gate='warmup'` for warm-up requests, `gate='attack'` for the actual burst).

>[!note] Gates allow for *synchronized releases* so that multiple requests are sent *simultaneously*. 

- **`engine.openGate('1')`**: Releases all queued requests in gate `'1'` simultaneously.

>[!example]+
> - A template for bypassing rate-limited login endpoints using the single-packet attack:
> 
> ```python
> def queueRequests(target, wordlists):
> 
>     engine = RequestEngine(
>         endpoint=target.endpoint,
>         concurrentConnections=1,   
>         engine=Engine.BURP2
>     )
>     
> 
>     # candidate password list
>     passwords = [
>         "123456", "password", "12345678", "qwerty", "abc123",
>         "monkey", "letmein", "dragon", "111111", "baseball",
>         "iloveyou", "master", "sunshine", "princess", "welcome",
>         "shadow", "superman", "michael", "football", "login"
>     ]
> 
>     for password in passwords:
>         engine.queue(target.req, password, gate='1')
> 
>     # release all queued requests simultaneously as a single TCP packet
>     engine.openGate('1')
> 
> 
> def handleResponse(req, interesting):
>     # add all responses to the results table for analysis
>     table.add(req)
> ```
> 

## Race conditions in multi-step processes
### States and sub-states

- In modern web applications, a single HTTP request often triggers a **multi-step sequence** on the backend. 
- During this processing, the application transitions through several **hidden sub-states** before committing the final state.

>[!quote] Every pentester knows that multi-step sequences are a hotbed for vulnerabilities, but with race conditions, everything is multi-step.
> — James Kettle, [`Smashing the state machine: the true potential of web race conditions`](https://portswigger.net/research/smashing-the-state-machine) 

>A **state** is a persistent representation of a condition of a system or resource at a particular point in time, typically stored server-side in a **database, cache, or session store**.

- Examples of states include:
	- Whether a user is logged in or not.
	- Whether a user account is privileged.
	- Whether a coupon has been redeemed.
- Applications transition between states as they process requests and reflect state changes in responses (for example, when a coupon is redeemed, the state changes from "unused" to "redeemed.").

>A **sub-state** is a **transient intermediate condition** that exists while a request is being processed, _before the final state is committed_.

- Sub-states are often **invisible to end users**.
- They exist for a very short duration — often milliseconds or less.
- So, even if an action appears single-state from the first glance (like redeeming a coupon), it may actually be **multi-step** internally.
- During this time, security invariants may be weaker. This creates **race windows** attackers can exploit.

>[!quote] Every HTTP request may transition an application through multiple fleeting, hidden states, which I'll refer to as 'sub-states'. If you time it right, you can abuse these sub-states for unintended transitions, break business logic, and achieve high-impact exploits. Let's get started.
> — James Kettle, [`Smashing the state machine: the true potential of web race conditions`](https://portswigger.net/research/smashing-the-state-machine) 

### MFA bypass via sub-states

Multi-factor authentication (MFA) workflows are a classic example of sub-state vulnerabilities.

- Vulnerable Python code:

```Python
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = users_db.get(username)
    
    if not user or not verify_password(user, password):
        return "Invalid credentials", 401

    # Session created immediately after login
    session['userid'] = user['userid']

    # Sub-state: MFA not yet enforced
    if user['mfa_enabled']:
        session['enforce_mfa'] = False  # MFA pending
        send_mfa_code(user)
        return redirect('/mfa')
    else:
        session['enforce_mfa'] = True
        return "Login successful", 200

@app.route('/sensitive')
def access_sensitive_resource():
    if 'userid' not in session:
        return "Not logged in", 401
    if not session.get('enforce_mfa', False):
        # Vulnerable check: MFA not completed
        return "MFA required", 403
    return "Sensitive data", 200
```

What’s happening:
1. The session is created immediately after username and password are verified.
2. MFA isn't enforced yet; this creates a **sub-state** where the user has a valid session but hasn't completed MFA.
3. If an attacker sends a request to sensitive endpoint **simultaneously with login**, they may bypass MFA entirely.

## Detecting and exploiting hidden multi-step race conditions

PortSwigger research outlines a structured approach to uncover these hidden vulnerabilities:

1. **Identify potential collisions**
	- Enumerate the endpoints you need to test. For each one, ask yourself the following questions:
		- **Is this endpoint security-critical?** Endpoints that don't touch critical functionality aren't worth testing; target login, password reset, payment processing, user management functionality, etc.
		- **Is there any collision potential?** For collisions to be possible, you typically need two or more requests that operate **on the same shared resource**, such as a database record, session variable, etc.

>[!tip] Target operations that **modify existing data** rather than append new data.

>[!tip] Target requests within the same user session or token (cross-session collisions rarely happen).


2. **Probe for clues**
	- **Benchmark normal behavior**. Send a group of requests **sequentially** (`Send group in sequence (separate connections)` in `Repeater`) with slight delays between them to understand baseline response time and application behavior.
	- Send the same group of requests at once (`Send group in parallel` in `Repeater`) using the **single-packet attack** (HTTP/2) or **last-byte sync** (HTTP/1.1).
	- **Look for anomalies**, some form of deviation from the observed baseline. This includes **changes in one or more responses**, **side-effects** such as unexpected state changes, or **different response timing**.

3. **Prove the concept**
	- Refine timing and concurrency to maximize the chances of a **state collision**.
	- Use tools like **Turbo Intruder** to have precise control over request timing.
	- Confirm the impact and map out underlying state transitions.

>[!tip] Because these vulnerabilities involve complex **state machines**, multiple tests are often required to uncover them.

## References and further reading


- [`Smashing the state machine: the true potential of web race conditions — James Kettle`](https://portswigger.net/research/smashing-the-state-machine)
- [`Race conditions — PortSwigger Web Security Academy`](https://portswigger.net/web-security/race-conditions)

- [`Sending grouped HTTP requests — Burp Suite documentation, PortSwigger`](https://portswigger.net/burp/documentation/desktop/tools/repeater/send-group#sending-requests-in-parallel)
- [`Turbo Intruder — BApp Store, PortSwigger`](https://portswigger.net/bappstore/9abaa233088242e8be252cd4ff534988)
- [`Nagle's Algorithm — Wikipedia`](https://en.wikipedia.org/wiki/Nagle%27s_algorithm)

- [`The single-packet attack: making remote race conditions 'local' — PortSwigger Research`](https://portswigger.net/research/the-single-packet-attack-making-remote-race-conditions-local)
- [`Timeless Timing Attacks: Exploiting Concurrency to Leak Secrets over Remote Connections — Tom Van Goethem et al., USENIX Security 2020`](https://www.usenix.org/conference/usenixsecurity20/presentation/van-goethem)


