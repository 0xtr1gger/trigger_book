---
created: 2026-04-29
---
### Overlong UTF-8 Unicode encoding

UTF-8 is a **variable-length encoding**.
- 1 byte -> simple characters (ASCII).
- Up to 4 bytes -> more complex Unicode characters.

Key rule:

>[!important] Every character must be encoded using the **shortest possible representation**.

>**Overlong UTF-8 encoding** is an invalid encoding technique where a character is represented using more bytes than necessary.

>[!important] **Overlong UTF-8 encoding** = encoding a character using **more bytes than necessary**.

| Character | Normal UTF-8    | Overlong UTF-8        |
| --------- | --------------- | --------------------- |
| `A`       | `0x41` (1 byte) | `0xC1 0x81` (2 bytes) |

>[!important] Overlong UTF-8 encoding is considered **invalid UTF-8**.

Why this is possible:

- UTF-8 uses patterns like:

```
1 byte:  0xxxxxxx
2 bytes: 110xxxxx 10xxxxxx
3 bytes: 1110xxxx 10xxxxxx 10xxxxxx
```

- So you can "pad" a small value with extra zeros and still represent the same character.

```
7   = normal
007 = overlong
```

Same value, different representation.


Overlong encodings become dangerous when:

- One component **validates input**
- Another component **decodes it differently**

For example, let's say an application blocks `../`. But the attacker sends `%c0%ae%c0%ae%c0%af`, which filter doesn't detect. The backend, however, decodes the characters just fine and uses `../` -> [[🛠️ Path traversal]].

>[!warning] Modern filters today usually reject overlong UTF-8.

> **Overlong encoding = same character, wrong (longer) representation → used to trick filters**.


```
/ -> 0x2f -> 00101111
```