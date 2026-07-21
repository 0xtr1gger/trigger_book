---
created: 2026-04-29
tags:
  - web_hacking
  - essential_skills
status: draft
---

## Encoding and decoding

- The backend application, intermediaries, and the client apply a variety of encodings to data passed between systems. 
- This means that the receiving end would first need to decode the data before use. 
- The exact sequence of decoding steps that are performed depends on the context in which the data appears.
- When considering an attack, you should think about where exactly your payload is being injected — the context. If you can infer how your input is being decoded based on this context, you can potentially identify alternative ways to represent the same payload.

>[!important] If you find a discrepancy between decoding used by an input filter and decoding the backend applies, you may be able to exploit it to evade defenses.

### URL encoding

- In [[🛠️ URL|URLs]], a series of reserved characters carry special meaning:

| Character | Description                               |
| --------- | ----------------------------------------- |
| `?`       | Indicates the start of the query string.  |
| `=`       | Indicates parameter value assignment.     |
| `&`       | Separates parameters in the query string. |

- If these characters appear in the URL, they must be URL-encoded.

| Character | URL-encoded |
| --------- | ----------- |
| `?`       | `%3F`       |
| `=`       | `%3D`       |
| `&`       | `%26`       |
| `[space]` | `+`, `%20`  |
- Any URL-based input is automatically URL decoded server-side before it is assigned to the relevant variables. 
- This means that (in most servers) sequences like `%22`, `%3C`, and `%3E` in a query parameter are synonymous with `"`, `<`, and `>` characters respectively. In other words, you can inject URL-encoded data via the URL and it will usually still be interpreted correctly by the back-end application.
- Occasionally, you may find that WAFs and suchlike fail to properly URL decode your input when checking it. In this case, you may be able to smuggle payloads to the back-end application simply by encoding any characters or words that are blacklisted. For example, in a SQL injection attack, you might encode the keywords, so `SELECT` becomes `%53%45%4C%45%43%54` and so on.

### Double URL encoding

- For one reason or another, some servers perform two rounds of URL decoding on any URLs they receive. 
- This isn't necessarily an issue in its own right, provided that any security mechanisms also double-decode the input when checking it. 
- Otherwise, this discrepancy allows you to smuggle malicious input to the back-end by simply encoding it twice.

### HTML encoding

- In HTML documents, certain characters need to be escaped or encoded to prevent the browser from incorrectly interpreting them as part of the markup. 
- This is achieved by substituting the offending characters with a reference, prefixed with an ampersand and terminated with a semicolon. 
- In many cases, a name can be used for the reference. For example, the sequence `&colon;` represents a colon character.
- Alternatively, the reference may be provided using the character's decimal or hex code point, in this case, `&#58;` and `&#x3a;` respectively. 
- In specific locations within the HTML, such as the text content of an element or the value of an attribute, browsers will automatically decode these references when they parse the document. When injecting inside such a location, you can occasionally take advantage of this to obfuscate payloads for client-side attacks, hiding them from any server-side defenses that are in place.

#### Leading 

- When using decimal or hex-style HTML encoding, you can optionally include an arbitrary number of leading zeros in the code points. Some WAFs and other input filters fail to adequately account for this.

```html
<a href="javascript&#00000000000058;alert(1)">Click me</a>
```

### Obfuscation via XML encoding

- XML is closely related to HTML and also supports character encoding using the same numeric escape sequences. This enables you to include special characters in the text content of elements without breaking the syntax, which can come in handy when testing for XSS via XML-based input, for example.

- Even if you don't need to encode any special characters to avoid syntax errors, you can potentially take advantage of this behavior to obfuscate payloads in the same way as you do with HTML encoding. The difference is that your payload is decoded by the server itself, rather than client-side by a browser. This is useful for bypassing WAFs and other filters, which may block your requests if they detect certain keywords associated with SQL injection attacks.

```XML
<stockCheck>
    <productId>
        123
    </productId>
    <storeId>
        999 &#x53;ELECT * FROM information_schema.tables
    </storeId>
</stockCheck>
```

## Unicode escaping

- Unicode escape sequences consist of the prefix `\u` followed by the four-digit hex code for the character. 

>[!example] `\u003a` represents a colon. ES6 also supports a new form of Enicode escape using curly braces: `\u{3a}`.

- When parsing strings, most programming languages decode these Unicode escapes. This includes the JavaScript engine used by browsers. When injecting into a string context, you can obfuscate client-side payloads using Unicode, just like we did with HTML escapes in the example above.

>[!example]+
> - Let's say you're trying to exploit DOM XSS where your input is passed to the `eval()` sink as a string. If your initial attempts are blocked, try escaping one of the characters as follows:
> 
> ```js
> eval("\u0061lert(1)")
> ```
> 
> 
> - As this will remain encoded server-side, it may go undetected until the browser decodes it again.
> 

>[!note] Inside a string, you can escape any characters like this. However, outside of a string, escaping some characters will result in a syntax error. This includes opening and closing parentheses, for example.

- The ES6-style Unicode escapes also allow optional leading zeros, so some WAFs may be easily fooled using the same technique we used for HTML encodings. For example:

```html
<a href="javascript:\u{00000000061}alert(1)">Click me</a>
```

## Hex escaping

- Another option when injecting into a string context is to use hex escapes, which represent characters using their hexadecimal code point, prefixed with `\x`. For example, the lowercase letter `a` is represented by `\x61`.

- Just like Unicode escapes, these will be decoded client-side as long as the input is evaluated as a string:

```js
eval("\x61lert")
```

- Note that you can sometimes also obfuscate SQL statements in a similar manner using the prefix `0x`. For example, `0x53454c454354` may be decoded to form the `SELECT` keyword.
## Octal escaping

- Octal escaping works in pretty much the same way as hex escaping, except that the character references use a base-8 numbering system rather than base-16. These are prefixed with a standalone backslash, meaning that the lowercase letter `a` is represented by `\141`.

```js
eval("\141lert(1)")
```

## Multiple encoding 

It is important to note that you can combine encodings to hide your payloads behind multiple layers of obfuscation. Look at the `javascript:` URL in the following example:

`<a href="javascript:&bsol;u0061lert(1)">Click me</a>`

Browsers will first HTML decode `&bsol;,` resulting in a backslash. This has the effect of turning the otherwise arbitrary `u0061` characters into the unicode escape `\u0061`:

`<a href="javascript:\u0061lert(1)">Click me</a>`

This is then decoded further to form a functioning XSS payload:

`<a href="javascript:alert(1)">Click me</a>`

Clearly, to successfully inject a payload in this way, you need a solid understanding of which decoding is performed on your input and in what order.
## Overlong UTF-8 Unicode encoding

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

For example, let's say an application blocks `../`. But the attacker sends `%c0%ae%c0%ae%c0%af`, which filter doesn't detect. The backend, however, decodes the characters just fine and uses `../` -> [[Path traversal]].

>[!warning] Modern filters today usually reject overlong UTF-8.

> **Overlong encoding = same character, wrong (longer) representation → used to trick filters**.


```
/ -> 0x2f -> 00101111
```

### Appendix A: ASCII characters chart

### Lowercase letters (`a`-`z`)

| Char | Dec   | Hex  | URL   | Unicode  | JS hex | Octal  |
| ---- | ----- | ---- | ----- | -------- | ------ | ------ |
| `a`  | `97`  | `61` | `%61` | `\u0061` | `\x61` | `\141` |
| `b`  | `98`  | `62` | `%62` | `\u0062` | `\x62` | `\142` |
| `c`  | `99`  | `63` | `%63` | `\u0063` | `\x63` | `\143` |
| `d`  | `100` | `64` | `%64` | `\u0064` | `\x64` | `\144` |
| `e`  | `101` | `65` | `%65` | `\u0065` | `\x65` | `\145` |
| `f`  | `102` | `66` | `%66` | `\u0066` | `\x66` | `\146` |
| `g`  | `103` | `67` | `%67` | `\u0067` | `\x67` | `\147` |
| `h`  | `104` | `68` | `%68` | `\u0068` | `\x68` | `\150` |
| `i`  | `105` | `69` | `%69` | `\u0069` | `\x69` | `\151` |
| `j`  | `106` | `6A` | `%6A` | `\u006A` | `\x6A` | `\152` |
| `k`  | `107` | `6B` | `%6B` | `\u006B` | `\x6B` | `\153` |
| `l`  | `108` | `6C` | `%6C` | `\u006C` | `\x6C` | `\154` |
| `m`  | `109` | `6D` | `%6D` | `\u006D` | `\x6D` | `\155` |
| `n`  | `110` | `6E` | `%6E` | `\u006E` | `\x6E` | `\156` |
| `o`  | `111` | `6F` | `%6F` | `\u006F` | `\x6F` | `\157` |
| `p`  | `112` | `70` | `%70` | `\u0070` | `\x70` | `\160` |
| `q`  | `113` | `71` | `%71` | `\u0071` | `\x71` | `\161` |
| `r`  | `114` | `72` | `%72` | `\u0072` | `\x72` | `\162` |
| `s`  | `115` | `73` | `%73` | `\u0073` | `\x73` | `\163` |
| `t`  | `116` | `74` | `%74` | `\u0074` | `\x74` | `\164` |
| `u`  | `117` | `75` | `%75` | `\u0075` | `\x75` | `\165` |
| `v`  | `118` | `76` | `%76` | `\u0076` | `\x76` | `\166` |
| `w`  | `119` | `77` | `%77` | `\u0077` | `\x77` | `\167` |
| `x`  | `120` | `78` | `%78` | `\u0078` | `\x78` | `\170` |
| `y`  | `121` | `79` | `%79` | `\u0079` | `\x79` | `\171` |
| `z`  | `122` | `7A` | `%7A` | `\u007A` | `\x7A` | `\172` |

### Uppercase Letters (`A`-`Z`)

| Char | Dec  | Hex  | URL   | Unicode  |
| ---- | ---- | ---- | ----- | -------- |
| `A`  | `65` | `41` | `%41` | `\u0041` |
| `B`  | `66` | `42` | `%42` | `\u0042` |
| `C`  | `67` | `43` | `%43` | `\u0043` |
| `D`  | `68` | `44` | `%44` | `\u0044` |
| `E`  | `69` | `45` | `%45` | `\u0045` |
| `F`  | `70` | `46` | `%46` | `\u0046` |
| `G`  | `71` | `47` | `%47` | `\u0047` |
| `H`  | `72` | `48` | `%48` | `\u0048` |
| `I`  | `73` | `49` | `%49` | `\u0049` |
| `J`  | `74` | `4A` | `%4A` | `\u004A` |
| `K`  | `75` | `4B` | `%4B` | `\u004B` |
| `L`  | `76` | `4C` | `%4C` | `\u004C` |
| `M`  | `77` | `4D` | `%4D` | `\u004D` |
| `N`  | `78` | `4E` | `%4E` | `\u004E` |
| `O`  | `79` | `4F` | `%4F` | `\u004F` |
| `P`  | `80` | `50` | `%50` | `\u0050` |
| `Q`  | `81` | `51` | `%51` | `\u0051` |
| `R`  | `82` | `52` | `%52` | `\u0052` |
| `S`  | `83` | `53` | `%53` | `\u0053` |
| `T`  | `84` | `54` | `%54` | `\u0054` |
| `U`  | `85` | `55` | `%55` | `\u0055` |
| `V`  | `86` | `56` | `%56` | `\u0056` |
| `W`  | `87` | `57` | `%57` | `\u0057` |
| `X`  | `88` | `58` | `%58` | `\u0058` |
| `Y`  | `89` | `59` | `%59` | `\u0059` |
| `Z`  | `90` | `5A` | `%5A` | `\u005A` |

### Special characters

| Char    | Meaning       | Dec   | Hex  | URL   | Unicode  |
| ------- | ------------- | ----- | ---- | ----- | -------- |
| `space` | Space         | `32`  | `20` | `%20` | `\u0020` |
| `!`     | Exclamation   | `33`  | `21` | `%21` | `\u0021` |
| `"`     | Double quote  | `34`  | `22` | `%22` | `\u0022` |
| `#`     | Fragment      | `35`  | `23` | `%23` | `\u0023` |
| `$`     | Dollar        | `36`  | `24` | `%24` | `\u0024` |
| `%`     | Percent       | `37`  | `25` | `%25` | `\u0025` |
| `&`     | Ampersand     | `38`  | `26` | `%26` | `\u0026` |
| `'`     | Single quote  | `39`  | `27` | `%27` | `\u0027` |
| `(`     | Open paren    | `40`  | `28` | `%28` | `\u0028` |
| `)`     | Close paren   | `41`  | `29` | `%29` | `\u0029` |
| `*`     | Asterisk      | `42`  | `2A` | `%2A` | `\u002A` |
| `+`     | Plus          | `43`  | `2B` | `%2B` | `\u002B` |
| `,`     | Comma         | `44`  | `2C` | `%2C` | `\u002C` |
| `-`     | Hyphen        | `45`  | `2D` | `%2D` | `\u002D` |
| `.`     | Dot           | `46`  | `2E` | `%2E` | `\u002E` |
| `/`     | Slash         | `47`  | `2F` | `%2F` | `\u002F` |
| `:`     | Colon         | `58`  | `3A` | `%3A` | `\u003A` |
| `;`     | Semicolon     | `59`  | `3B` | `%3B` | `\u003B` |
| `<`     | Less than     | `60`  | `3C` | `%3C` | `\u003C` |
| `=`     | Equals        | `61`  | `3D` | `%3D` | `\u003D` |
| `>`     | Greater than  | `62`  | `3E` | `%3E` | `\u003E` |
| `?`     | Question      | `63`  | `3F` | `%3F` | `\u003F` |
| `@`     | At            | `64`  | `40` | `%40` | `\u0040` |
| `[`     | Open bracket  | `91`  | `5B` | `%5B` | `\u005B` |
| `\`     | Backslash     | `92`  | `5C` | `%5C` | `\u005C` |
| `]`     | Close bracket | `93`  | `5D` | `%5D` | `\u005D` |
| `^`     | Caret         | `94`  | `5E` | `%5E` | `\u005E` |
| `_`     | Underscore    | `95`  | `5F` | `%5F` | `\u005F` |
| ```     | Backtick      | `96`  | `60` | `%60` | `\u0060` |
| `{`     | Open brace    | `123` | `7B` | `%7B` | `\u007B` |
| `\|`    | Pipe          | `124` | `7C` | `%7C` | `\u007C` |
| `}`     | Close brace   | `125` | `7D` | `%7D` | `\u007D` |
| `~`     | Tilde         | `126` | `7E` | `%7E` | `\u007E` |


| Char | Hex  |
| ---- | ---- |
| `<`  | `3C` |
| `>`  | `3E` |
| `"`  | `22` |
| `'`  | `27` |
| `(`  | `28` |
| `)`  | `29` |
| `:`  | `3A` |
| `;`  | `3B` |
| `/`  | `2F` |
| `\`  | `5C` |
| `=`  | `3D` |
| `%`  | `25` |
| `&`  | `26` |
| `a`  | `61` |
| `A`  | `41` |
| `S`  | `53` |
| `E`  | `45` |
| `L`  | `4C` |
| `T`  | `54` |

TODO:
add payload examples for each encoding