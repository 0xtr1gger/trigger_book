---
created: 2026-05-02
---
could you please generate useful notes for my article based on my PortSwigger lab solution walkthrough?

| `#`  | Solved? | Name                                                                          | Date    |
| ---- | ------- | ----------------------------------------------------------------------------- | ------- |
| `1.` | `✓`     | File path traversal, simple case                                              | `02.05` |
| `2.` | `✓`     | File path traversal, traversal sequences blocked with absolute path bypass    | `02.05` |
| `3.` | `✓`     | File path traversal, traversal sequences stripped non-recursively             | `02.05` |
| `4.` | `✓`     | File path traversal, traversal sequences stripped with superfluous URL-decode | `02.05` |
| `5.` | `✓`     | File path traversal, validation of start of path                              | `10.05` |
| `6.` | `✓`     | File path traversal, validation of file extension with null byte bypass<br>   | `10.05` |

## 1. File path traversal, simple case

>[!done]

>[!note]+ Lab description
> - [`Lab: File path traversal, simple case`](https://portswigger.net/web-security/file-path-traversal/lab-simple)
> - Level: #Apprentice 
> 
> This lab contains a path traversal vulnerability in the display of product images.
> 
> To solve the lab, retrieve the contents of the `/etc/passwd` file.

### Solution

- The target application is an online shop. Each product has an image. If you inspected the source code, you see:

![[images/walkthrough/PortSwigger/Path Traversal/lab1/1.png]]

- In repeater, request this image separately:

![[images/walkthrough/PortSwigger/Path Traversal/lab1/2.png]]


- Then try to alter the path by adding path traversal sequences:

```powershell
/image?filename=../../../etc/passwd 
```

![[images/walkthrough/PortSwigger/Path Traversal/lab1/3.png]]

![[images/walkthrough/PortSwigger/Path Traversal/lab1/solved.png]]

Solved!

## 2. File path traversal, traversal sequences blocked with absolute path bypass

>[!done]

>[!note]+ Lab description
> - [`Lab: File path traversal, traversal sequences blocked with absolute path bypass`](https://portswigger.net/web-security/file-path-traversal/lab-absolute-path-bypass)
> - Level: #Practitioner 
> 
> This lab contains a path traversal vulnerability in the display of product images.
> 
> The application blocks traversal sequences but treats the supplied filename as being relative to a default working directory.
> 
> To solve the lab, retrieve the contents of the `/etc/passwd`

### Solution

- The vulnerability is in the same `/image?filename=` parameter. However, if you inject path traversal sequences like `../../../etc/passwd`, the application responds with `No such file`:

![[images/walkthrough/PortSwigger/Path Traversal/lab2/1.png]]


- In this case, you can try **absolute path traversal**, requesting `/etc/passwd` directly:

![[images/walkthrough/PortSwigger/Path Traversal/lab2/2.png]]

![[images/walkthrough/PortSwigger/Path Traversal/lab2/solved.png]]

Solved!

## 3. File path traversal, traversal sequences stripped non-recursively

>[!done] 

>[!note]+ Lab description
> 
> - [`Lab: File path traversal, traversal sequences stripped non-recursively`](https://portswigger.net/web-security/file-path-traversal/lab-sequences-stripped-non-recursively)
> - Level: #Practitioner 
> 
> 
> This lab contains a path traversal vulnerability in the display of product images.
> 
> The application strips path traversal sequences from the user-supplied filename before using it.
> 
> To solve the lab, retrieve the contents of the `/etc/passwd` file.

### Solution

- Strat with the same `../../../etc/passwd` payload:

![[images/walkthrough/PortSwigger/Path Traversal/lab3/1.png]]

- The application says `No such file`. Try absolute path traversal:

![[images/walkthrough/PortSwigger/Path Traversal/lab3/2.png]]

- Same result. 
- Then try common bypasses, such as nested path traversal sequences:

```powershell
....//....//....//etc/passwd
```

![[nested_path_traversal_sequences.svg|600]]


![[images/walkthrough/PortSwigger/Path Traversal/lab3/3.png]]

![[images/walkthrough/PortSwigger/Path Traversal/lab3/solved.png]]

Solved!

## 4. File path traversal, traversal sequences stripped with superfluous URL-decode

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: File path traversal, traversal sequences stripped with superfluous URL-decode`](https://portswigger.net/web-security/file-path-traversal/lab-superfluous-url-decode)
> - Level: #Practitioner 
> 
> 
> This lab contains a path traversal vulnerability in the display of product images.
> 
> The application blocks input containing path traversal sequences. It then performs a URL-decode of the input before using it.
> 
> To solve the lab, retrieve the contents of the `/etc/passwd` file.

### Solution

- This time, to bypass sanitization, you need to use encoding. 
- First, try normal URL encoding: `%2e%2e%2f%2e%2e%2f%2e%2e%2f`:

![[images/walkthrough/PortSwigger/Path Traversal/lab4/1.png]]

- No use. Try double URL encoding: `%252e%252e%252f%252e%252e%252f%252e%252e%252f`:


![[images/walkthrough/PortSwigger/Path Traversal/lab4/2.png]]


![[images/walkthrough/PortSwigger/Path Traversal/lab4/solved.png]]


Solved!
## 5. File path traversal, validation of start of path

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: File path traversal, validation of start of path`](https://portswigger.net/web-security/file-path-traversal/lab-validate-start-of-path)
> - Level: #Practitioner 
> 
> This lab contains a path traversal vulnerability in the display of product images.
> 
> The application transmits the full file path via a request parameter, and validates that the supplied path starts with the expected folder.
> 
> To solve the lab, retrieve the contents of the `/etc/passwd` file.

### Solution

- This time, the image loading function uses absolute path to images, such as `/var/www/images/61.jpg`.

![[images/walkthrough/PortSwigger/Path Traversal/lab5/1.png]]

- If you try any path starting with anything other than `/var/www/images`, such as `/image?filename=../../../../etc/passwd`, the application responds with `"Missing parameter 'filename'"`:

![[images/walkthrough/PortSwigger/Path Traversal/lab5/2.png]]

- So, you can use `/var/www/images`, but then traverse to `/etc/passwd` using `/var/www/images/../../../etc/passwd`:


![[images/walkthrough/PortSwigger/Path Traversal/lab5/3.png]]

![[images/walkthrough/PortSwigger/Path Traversal/lab5/solved.png]]

Solved!
## 6. File path traversal, validation of file extension with null byte bypass

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: File path traversal, validation of file extension with null byte bypass`](https://portswigger.net/web-security/file-path-traversal/lab-validate-file-extension-null-byte-bypass)
> - Level: #Practitioner 
> 
> This lab contains a path traversal vulnerability in the display of product images.
> 
> The application validates that the supplied filename ends with the expected file extension.
> 
> To solve the lab, retrieve the contents of the `/etc/passwd` file.
### Solution

- If you try `../../../../etc/passwd`, the application responds with `"No such file"`:

![[images/walkthrough/PortSwigger/Path Traversal/lab6/1.png]]

- The same happens with any input that ends with anything other than `png`. To bypass the limit, append a URL-encoded null byte to the filename, and then `.png`:

```
/image?filename=../../../etc/passwd%00.png
```

![[images/walkthrough/PortSwigger/Path Traversal/lab6/2.png]]

![[images/walkthrough/PortSwigger/Path Traversal/lab6/solved.png]]

Solved!