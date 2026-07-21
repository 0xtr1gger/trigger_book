---
created: 2026-06-24
---
| `#`  | Solved? | Name                                                         | Date    | Notes |
| ---- | ------- | ------------------------------------------------------------ | ------- | ----- |
| `1.` | `✓`     | Exploiting an API endpoint using documentation               | `24.06` |       |
| `2.` |         | Exploiting server-side parameter pollution in a query string |         |       |
| `3.` | `✓`     | Finding and exploiting an unused API endpoint                | `24.06` |       |
| `4.` | `✓`     | Exploiting a mass assignment vulnerability                   | `24.06` |       |

## 1. Exploiting an API endpoint using documentation

>[!done]

>[!note]+ Lab description
> - [`Lab: Exploiting an API endpoint using documentation`](https://portswigger.net/web-security/api-testing/lab-exploiting-api-endpoint-using-documentation)
> - Level: #Apprentice 
> 
> To solve the lab, find the exposed API documentation and delete `carlos`. You can log in to your own account using the following credentials: `wiener:peter`.


### Solution

- Log in as `wiener` and browse the application; test the email change functionality. 
- In HTTP history, notice a `PATCH` request to `/api/user/wiener`. 

![[images/walkthrough/PortSwigger/API testing/lab1/1.png]]

- Go to `/api` and see REST API documentation:

![[images/walkthrough/PortSwigger/API testing/lab1/2.png]]

- To delete the user `carlos`, send a `DELETE` request to `/api/user/carlos`:

![[images/walkthrough/PortSwigger/API testing/lab1/3.png]]

![[images/walkthrough/PortSwigger/API testing/lab1/solved.png]]

Solved!
## 2. Exploiting server-side parameter pollution in a query string

>[!note]+ Lab description
> - [`Lab: Exploiting server-side parameter pollution in a query string`](https://portswigger.net/web-security/api-testing/server-side-parameter-pollution/lab-exploiting-server-side-parameter-pollution-in-query-string)
> - Level: #Practitioner 
> 
> To solve the lab, log in as the `administrator` and delete `carlos`.
### Solution

- Go to `My account` and click `Forgot password`. In HTTP history, notice a `GET` request to `/static/js/forgotPassword.js`:

![[images/walkthrough/PortSwigger/API testing/lab2/1.png]]

```js
let forgotPwdReady = (callback) => {
    if (document.readyState !== "loading") callback();
    else document.addEventListener("DOMContentLoaded", callback);
}

function urlencodeFormData(fd){
    let s = '';
    function encode(s){ return encodeURIComponent(s).replace(/%20/g,'+'); }
    for(let pair of fd.entries()){
        if(typeof pair[1]=='string'){
            s += (s?'&':'') + encode(pair[0])+'='+encode(pair[1]);
        }
    }
    return s;
}

const validateInputsAndCreateMsg = () => {
    try {
        const forgotPasswordError = document.getElementById("forgot-password-error");
        forgotPasswordError.textContent = "";
        const forgotPasswordForm = document.getElementById("forgot-password-form");
        const usernameInput = document.getElementsByName("username").item(0);
        if (usernameInput && !usernameInput.checkValidity()) {
            usernameInput.reportValidity();
            return;
        }
        const formData = new FormData(forgotPasswordForm);
        const config = {
            method: "POST",
            headers: {
                "Content-Type": "x-www-form-urlencoded",
            },
            body: urlencodeFormData(formData)
        };
        fetch(window.location.pathname, config)
            .then(response => response.json())
            .then(jsonResponse => {
                if (!jsonResponse.hasOwnProperty("result"))
                {
                    forgotPasswordError.textContent = "Invalid username";
                }
                else
                {
                    forgotPasswordError.textContent = `Please check your email: "${jsonResponse.result}"`;
                    forgotPasswordForm.className = "";
                    forgotPasswordForm.style.display = "none";
                }
            })
            .catch(err => {
                forgotPasswordError.textContent = "Invalid username";
            });
    } catch (error) {
        console.error("Unexpected Error:", error);
    }
}

const displayMsg = (e) => {
    e.preventDefault();
    validateInputsAndCreateMsg(e);
};

forgotPwdReady(() => {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const resetToken = urlParams.get('reset-token');
    if (resetToken)
    {
        window.location.href = `/forgot-password?reset_token=${resetToken}`;
    }
    else
    {
        const forgotPasswordBtn = document.getElementById("forgot-password-btn");
        forgotPasswordBtn.addEventListener("click", displayMsg);
    }
});
```


- The code, among other things, looks for a query parameter named `reset-token`. If found, it immediately redirects the browser to a URL that uses `reset_token` instead.
- If no reset token is present, it attaches a click handler to the forgot-password button.
---

- Go to `/forgot-password` and add a `reset-token=test` parameter. The application redirects you to a page that displays `"Invalid token"`:

![[images/walkthrough/PortSwigger/API testing/lab2/2.png]]

- Inspect HTTP history and see that it caused two requests:
	- One you made manually, `GET /forgot-password?reset-token=test` (hyphen).
	- And another, made by the client-side JavaScript, `/forgot-password?reset_token=test` (underscore).

![[images/walkthrough/PortSwigger/API testing/lab2/3.png]]

- Note these parameters.
---
- Enter `administrator` in the username field. This causes a `POST` request to `/forgot-password`:

![[images/walkthrough/PortSwigger/API testing/lab2/4.png]]

- Send this request to `Repeater`.
- Change username from `administrator` to an invalid one, such as `administratorx`. See an `"Invalid username"` error. 

![[images/walkthrough/PortSwigger/API testing/lab2/5.png]]

- Append a non-existing parameter using a URL-encoded ampersand `&`, `%26`, such as `%26x=y`. See a `"Parameter is not supported"` error:

![[images/walkthrough/PortSwigger/API testing/lab2/6.png]]

- This suggests that the internal API may have interpreted `&x=y` as a separate parameter, instead of part of the username.
- Attempt to truncate the server-side query string using a URL-encoded `#` character: `username=administrator%23`. Send the request and see an error `"Field not specified"`:

![[images/walkthrough/PortSwigger/API testing/lab2/7.png]]

- This suggests that the server-side query may include an additional parameter called `field`, which has been removed by the `#` character.
- Add a `field` parameter with an invalid value to the request. Truncate the query string after the added parameter-value pair. For example, add URL-encoded `&field=x#`: `username=administrator%26field=x%23`. See an `"Invalid field"` error message.

![[images/walkthrough/PortSwigger/API testing/lab2/8.png]]

- This suggests that the server-side application may recognize the injected `field` parameter.
- Brute-force `field` using `Intruder` using the `Server-side variable names` payload list:

![[images/walkthrough/PortSwigger/API testing/lab2/9.png]]

- Review the results. Notice that the requests with the username and email payloads both return a `200` response.
- Change the value of the `field` parameter from `x#` to `email`: `username=administrator%26field=email%23`. Send the request.


## 3. Finding and exploiting an unused API endpoint

>[!note]+ Lab description
> - [`Lab: Finding and exploiting an unused API endpoint`](https://portswigger.net/web-security/api-testing/lab-exploiting-unused-api-endpoint)
> - Level: #Practitioner 
> 
> To solve the lab, exploit a hidden API endpoint to buy a **Lightweight l33t Leather Jacket**. You can log in to your own account using the following credentials: `wiener:peter`.

### Solution

- Log in as `wiener`. You have `$0.00` credits at the start.
- Navigate to the first product (leather jacket). In HTTP history, see a request to `/api/products/1/price`. Send this request to `Repeater`. 
- Change request method from `GET` to `PATCH` (`POST` would result in `"Method Not Allowed"`) and set a JSON body with a new price.

```http
PATCH /api/products/1/price HTTP/2
Host: 0a9b00b503c589ed8056c2ec00f80041.web-security-academy.net
Cookie: session=z0MkoyDpjOPZvQh7PrLqkw8F1y9jVesJ
Content-Length: 11
Content-Type: application/json;charset=UTF-8

{"price":0}
```

- Send the request. See the application accepts it and returns the new price:

![[images/walkthrough/PortSwigger/API testing/lab3/2.png]]

- Go to the jacket product page again and add it to cart. Go to `/cart` and see the jacket is there, but the cart's price is `$0.00`:

![[images/walkthrough/PortSwigger/API testing/lab3/3.png]]

- `Place order`.

![[images/walkthrough/PortSwigger/API testing/lab3/solved.png]]

Solved!
## 4. Exploiting a mass assignment vulnerability

>[!done]

>[!note]+ Lab description
> - [`Lab: Exploiting a mass assignment vulnerability`](https://portswigger.net/web-security/api-testing/lab-exploiting-mass-assignment-vulnerability)
> - Level: #Practitioner 
> 
> To solve the lab, find and exploit a mass assignment vulnerability to buy a **Lightweight l33t Leather Jacket**. You can log in to your own account using the following credentials: `wiener:peter`.


### Solution

- Log in as `wiener`. Notice you have `$0.00` credits.
- Add the leather jacket to the cart. Attempt to checkout and see an error: `Not enough store credits for this purchase`.

![[images/walkthrough/PortSwigger/API testing/lab4/1.png]]

- In HTTP history, see a `GET` to `/api/checkout`:

![[images/walkthrough/PortSwigger/API testing/lab4/2.png]]

- Right after that, see `POST` to `/api/checkout`:

![[images/walkthrough/PortSwigger/API testing/lab4/3.png]]

- Send this `POST` request to `Repeater`. In the JSON structure, add the `chosen_discount` parameter with `percentage` set to `100`:

```json
{
"chosen_discount":{"percentage":100},"chosen_products":[{"product_id":"1","quantity":1}]}
```

- Send the request:

![[images/walkthrough/PortSwigger/API testing/lab4/4.png]]

- The application accepts it. 

![[images/walkthrough/PortSwigger/API testing/lab4/solved.png]]

Solved!