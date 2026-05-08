---
created: 2026-05-01
---

- Bypass of OTP (one-time password).
- Weak implementations of push notifications or hardware tokens.
- Replay attacks on OTP.
- SMS or email interception.
- MFA fatigue attacks (repeated push notifications)
- Weak fallback mechanisms (SMS, email)
- Logic flaws in MFA implementation

## Authentication factors and their weaknesses

The idea behind MFA is to require multiple authentication factors **of different types** for the user to log in. Below are factors commonly used in MFA and their potential weaknesses.

>**Knowledge factors** (e.g., passwords, PINs, security questions)

- Vulnerable to guessing, brute-force, and password reuse attacks.
- Susceptible to phishing and social engineering. 
- Passwords can be compromised through database leaks.

>[!warning] Knowledge factors, such as passwords, PINs, or answers to security questions are often **the weakest link**. 

>**Ownership factors**

- **SMS and voice OTPs**
	- Vulnerable to **SIM swap attacks** (SIM card hijacking), [SS7](https://en.wikipedia.org/wiki/Signalling_System_No._7) attacks, and malware.
	- SMS OTP codes are usually 4-6 digits, which often makes them susceptible to brute-forcing attacks unless rate limiting or locking is implemented properly. 

- **Email-based authentication codes or tokens**
	- Email accounts themselves may be compromised.

- **[TOTP](https://en.wikipedia.org/wiki/Time-based_one-time_password)**
	- Secure against SIM swap but vulnerable to seed secret leakage.

- **Hardware**
	- Very secure, but expensive and can be lost or broken.

- **Certificate/PKI management**
	- Vulnerable to private key leakage; complex to manage and deploy.

- **Push notifications**
	- Susceptible to MFA fatigue attacks (push spam; might cause accidental approval).
	- Relies on device security.
	- Users can be trick into approving with social engineering.

>**Inheritance factors**

- Vulnerable to spoofing with high-quality replicas or 3D models.
- Can be circumvented with attacks against sensor hardware or software (fingerprint readers, cameras, etc.).
- Raise privacy and regulatory concerns around storage and use of biometric data.

>[!warning] Biometric data leaks are permanent; unlike passwords, biometrics cannot be changed.

>[!note] See [[🛠️ Authentication on the web#Authentication factors and common authentication methods]].

Common attacks against MFA include:
- Flawed implementation of multistage processes
- OTP brute-force
- MFA fatigue
- MitM
- SIM swap

>[!tip] **Session hijacking** is one of the ways to bypass authentication completely, no matter how secure it is, since it targets already authenticated users.

## OTP brute-force

Many MFA systems use 4- to 6-digit codes (TOTP, SMS OTP). It's really easy to brute-force those if rate-limiting or lockout policies are absent or weak. 
With no brute-force protection, say, a 4-digit code (10,000 possible values) can be tested withing minutes.

TOTPs are usually sent via:
- SMS
- Email
- Authenticator applications (e.g., Microsoft Authenticator, etc.)

## Flawed implementation of multistage processes

MFA can indeed make authentication process considerably more secure. However, due to the complexity of such mechanisms, they're prone to **implementation flaws**.

>[!warning] MFA is only as secure as its **implementation**.

Many MFA systems use multi-step authentication:
- First step: user submits a username and password (knowledge factors)
- Second step: user submits MFA code or proves their identity with another second factor

Certain implementations of multistage login processes make potentially insecure assumptions about the user's actions in previous steps. For example:

- **Partial session creation before MFA completion**
	- The application sets session cookies immediately after the first step (the second factor is not really enforced) and gives the user *some* level of authentication, often to track user through the MFA process.

- **Unsafe assumptions about user progress through stages**
	- If the application doesn't properly verify the order and the completion of each step during the authentication process, an attacker can skip stages and bypass MFA.
	- This often happens, for example, when the application uses separate endpoints for each authentication step. Without sufficient validation, the attacker can proceed directly to the last stage.
	- In this case, the application assumes that the user accessing later stages has already completed the previous ones. 

- **Lack of integrity checks on authentication data between stages**
	- Applications often carry forward identifiers (e.g., cookies or tokens) or data from one authentication stage to subsequent ones, e.g., whether the user’s account is active, locked, or requires additional verification. 
	- If this data is data is not validated across the steps, an attacker can manipulate it to bypass authentication (e.g., exposing user-controlled `stage2complete=true` parameter to the client and trusting its value).

- **Identity mismatch between stages**
	- If the application doesn't explicitly check that the username or user ID given in each stage matches, the attacker can modify credentials on the way. 
	- For example, the attacker can use their own password to complete the first stage, then change the user identifier and complete the second stage as a victim user (such as entering an OTP). The application accepts this combination and logs the attacker in as the victim.

>[!bug] Step 1: Analyze a complete valid login flow
>- Perform a legitimate login with your own account intercepting all request sand responses.
>- Enumerate endpoints involved in the process.
>- Identify each distinct authentication stage and data submitted at each stage.

>[!bug] Step 2: Try to skip any stage
>- For example, try to access the last stage not going through the previous ones before.

>[!bug]+ Step 3: Try to access protected resources before completing the process
>- Try to access authenticated-only pages after first factor but before second factor.

>[!bug] Step 4: Manipulate data re-submitted across stages
>- If the same data (like username or flags) is submitted multiple times in different stages, try providing inconsistent values for these fields.
>- For example, use one valid username and password at stage 1, and a different username or token at stage 2, then see if authentication succeeds.

>[!bug] Step 5: Modify state flags 
>- If the application exposes any flags like `stage2complete=true` to the client, try changing or replaying them and skip steps.

>[!bug] Step 6: Reuse MFA codes
>- To try submit a previously used MFA token again. 

>[!tip] As with any logic flaws, the goal is to behave in a way developers didn't anticipate.


>[!bug]+ Labs
>- [[🛠️ Authentication labs#2. 2FA simple bypass]]

## Flawed two-factor verification logic

Sometimes flawed logic in two-factor authentication means that after a user has completed the initial login step, the website doesn't adequately verify that the same user is completing the second step.

For example, the user logs in with their normal credentials in the first step as follows:

```HTTP
POST /login-steps/first HTTP/1.1
Host: vulnerable-website.com
...
username=carlos&password=qwerty
```

They are then assigned a cookie that relates to their account, before being taken to the second step of the login process:

```http
HTTP/1.1 200 OK
Set-Cookie: account=carlos

GET /login-steps/second HTTP/1.1
Cookie: account=carlos
```

When submitting the verification code, the request uses this cookie to determine which account the user is trying to access:

```HTTP
POST /login-steps/second HTTP/1.1
Host: vulnerable-website.com
Cookie: account=carlos
...
verification-code=123456
```

In this case, an attacker could log in using their own credentials but then change the value of the `account` cookie to any arbitrary username when submitting the verification code.

```http
POST /login-steps/second HTTP/1.1
Host: vulnerable-website.com
Cookie: account=victim-user
...
verification-code=123456
```

This is extremely dangerous if the attacker is then able to brute-force the verification code as it would allow them to log in to arbitrary users' accounts based entirely on their username. They would never even need to know the user's password.

>[!bug]+ Labs
>- [[🛠️ Authentication labs#8. 2FA broken logic]]

## References

- [`Vulnerabilities in multi-factor authentication — Burp Suite Web Security Academy`](https://portswigger.net/web-security/authentication/multi-factor)