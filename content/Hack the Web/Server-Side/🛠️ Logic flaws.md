---
created: 2026-06-08
tags:
  - web_hacking
status: draft
---
## Logic flaws

>A **logic flaw**, or **business logic flaw**, is a weakness in the *design*, *implementation*, or *enforcement* of an application's business rules that allows an attacker to cause the application to enter an unintended state or to perform an unintended action while interacting through otherwise legitimate functionality. 

>[!important]+ Classification
> - Logic flaws map to:
> 	- [`CWE-840: Business Logic Errors`](https://cwe.mitre.org/data/definitions/840.html)
> 	- [`CWE-841: Improper Enforcement of Behavioral Workflow`](https://cwe.mitre.org/data/definitions/841.html)
>

- Business logic flaws are a family of vulnerabilities that share one property: the vulnerable code is functioning exactly as its authors intended, but the authors' intentions did not account for the way an attacker — as opposed to a normal user — will actually use the application.

- Logic-based vulnerabilities can be extremely diverse and are often **unique to the application and its specific functionality**.
	- Price manipulation
	- Coupon abuse
	- Workflow bypasses
	- Race conditions
	- State-transition abuse
	- Privilege escalation through process flaws
	- Negative-value attacks
	- Multi-step process manipulation
- Identifying logic flaws often requires human understanding of the underlying functionality, which makes them difficult to detect using automated vulnerability scanners. 
- Additionally, logic flaws are often invisible during normal interaction with the application. 
### How business logic vulnerabilities occur

- Logic flaws occur when the application's security depends on an *assumption* about user behavior, their input, or order of their actions. If that assumption is not enforced, it can be violated by an attacker; as a result, a legitimate functionality can be abused to perform unintended actions.

- In other words, a logic flaw means that when an attacker deviates from the expected user behavior, the application fails to take appropriate actions to prevent this, and, subsequently, fails to handle the situation safely.

>[!note] Logic flaws are particularly common in overly complicated systems that even developers no longer fully understand.

- Once assumption that commonly leads to logic flaws: **client-side validation is mistaken for security checks**. User input is only validated by JavaScript and accepted by the server as-is. 

### Business logic

- One of the main purposes of business logic is to enforce the rules and constraints that were defined when designing the application or functionality.
- Broadly speaking, the business rules dictate how the application should react when a given scenario occurs.
- This includes preventing users from doing things that will have a negative impact on the business or that simply don't make sense. For example, enforcing step order in a multi-step process.

---

- Flaws in the logic can allow attackers to circumvent these rules. For example, they might be able to complete a transaction without going through the intended purchase workflow.
- In other cases, broken or non-existent validation of user-supplied data might allow users to make arbitrary changes to transaction-critical values or submit nonsensical input. By passing unexpected values into server-side logic, an attacker can potentially induce the application to do something that it isn't supposed to.





## Examples of logic flaws



Logic flaws are defects in the application's state-transition model that permit unauthorized, unintended, or inconsistent transitions between states.

### Excessive trust in client-side controls

- A fundamentally flawed assumption is that users will only interact with the application via the provided web interface.
- This leads to an assumption that client-side controls will prevent users from supplying malicious inputs. 
- As a results, an application may rely only on client-side JavaScript to validate user input entry.
- However, these controls may easily be bypassed by supplying request directly using command-line interface or web proxy such as Burp Suite. 

### Failing to handle unconventional input

- The application logic aims to restrict user input to values that adhere to the business rules, such as accepting values of a specific data type. 
- Many applications incorporate numeric limits into their logic. The developer needs to anticipate all edge cases and properly validate this. Otherwise, if there is no explicit logic for handling a given case, this can lead to unexpected and potentially exploitable behavior.

---

- For numeric values, always check:
	- Zero values
	- Negative values


>[!bug]+ Labs
>- [[🛠️ Business logic vulnerabilities labs#2. High-level logic vulnerability]]
>- 


### Making flawed assumptions about user behavior

Applications may appear to be secure because they implement seemingly robust measures to enforce the business rules. Unfortunately, some applications make the mistake of assuming that, having passed these strict controls initially, the user and their data can be trusted indefinitely. This can result in relatively lax enforcement of the same controls from that point on.

If business rules and security measures are not applied consistently throughout the application, this can lead to potentially dangerous loopholes that may be exploited by an attacker.
## Logic flaws checklist

- Multi-step functionality:
	- [ ] Can I skip steps?
	- [ ] Can I repeat steps?
	- [ ] Can I perform actions out of order?
- [ ] Can I tamper with trusted values?
- User-controlled input — integers:
	- [ ] Can I use negative values?
	- [ ] Can I overflow or underflow values?
- State machine:
	- [ ] Can I jump states?
	- [ ] Can I go backwards?
	- [ ] Can I reach impossible states?
- Money:
	- **Coupons** — can they be reused?
	- **Store credit** — can balance go negative?
	- **Refunds** — can you refund after consuming a product?
	- **Discounts** — can discounts stack?


- Content should be based on cases and examples, use lab solutions.