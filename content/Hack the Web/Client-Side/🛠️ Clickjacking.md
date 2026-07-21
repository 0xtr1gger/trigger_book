---
created: 2026-06-08
---
## Clickjacking

>**Clickjacking**, also known as **UI redressing**, is a client-side attack in which a victim user is induced to interact with an actionable element on a hidden, authentic web page by clicking on a visually distinct element in a decoy page. The authentic page is rendered within a transparent, overlaid `<iframe>`, such that the victim's click is captured by the concealed layer rather than the visible one. 

- The attack exploits the fact that `<iframe>` elements can load **any cross-origin page by default**, and CSS can make the frame invisible while still capturing pointer events. 
- You don't need to forge the victim's request. The victim user interacts with real UI elements on the real site, through a transparent frame hosted on a page you control.

>[!note]- Why SOP doesn't help
>Yes, browsers enforce the [[SOP]] for JavaScript. A page at `attacker.com` can't read the DOM of an `<iframe>` loaded from `example.com`. However, the SOP says nothing bout visual rendering or click delivery. 
>- The browser will happily render `example.com` inside an `<iframe>` on `attacker.com` and relay pointer events (mouse clicks) to whichever element sits at the top of the z-index stack at the click coordinates.
>- The `example.com` iframe receives that click event as if the user were on the site directly. There is no cross-origin communication involved; the click simply lands inside the frame.

>[!note]- Why CSRF tokens don't help
> 
> Clickjacking is often confused with [[CSRF]], but they operate through entirely different mechanisms. 
> - CSRF requires you to forge HTTP requests so that the victim's browser sends them without the victim knowing. 
> - CSRF tokens defeat this by including a secret, session-bound value in the request that you can't predict or obtain (because of the [[SOP]]).
> - In clickjacking, however, you don't forge anything. The target page loads normally inside an `<iframe>`, the victim is already authenticated, and the browser sends the victim's real session cookies with every action. 
> - The **CSRF token is present in the page's form** and travels to the server as part of a completely legitimate browser session. 
> - The fact that this session is running inside a hidden `<iframe>` is entirely invisible to the server — from the server's perspective, the request is indistinguishable from any real user action.

- The impact of a clickjacking attack is bounded by what the target page's UI allows an authenticated user to do with a single click (or a small number of clicks). It can be, for example, one-click account deletion or even fund transfers.


## The CSS layering mechanism

>[!note] Clickjacking exploits are pure HTML/CSS — no JavaScript required in most cases.
### The layer stack

- The browser renders page elements in layers. 
- The CSS property `z-index` controls stacking order: elements with a higher `z-index` are rendered "on top" visually. Most importantly, **they receive pointer events first**.
- When the user clicks at a pixel coordinate, the browser walks down the `z-index` stack from highest to lowest and delivers the event to the topmost element at that position (that is not `pointer-events: none`).
- Clickjacking attacks exploit this by:
	1. Placing the target `<iframe>` at a high `z-index` so it receives clicks. 
	2. Making the `<iframe>` transparent via opacity — the victim seems only the decoy beneath it. 
	3. Aligning the decoy's visible element with the `<iframe>`'s actionable element — the victim clicks where they can see, landing where they can't.

### CSS properties

| Property           | Role in the attack                                                           | Typical value               |
| ------------------ | ---------------------------------------------------------------------------- | --------------------------- |
| `opacity`          | Makes iframe invisible while keeping it click-interactive                    | `0.00001`                   |
| `position`         | Enables pixel-precise placement outside normal document flow                 | `absolute`                  |
| `z-index`          | Places iframe on top of decoy in event-capture stack                         | `2` (iframe) vs `1` (decoy) |
| `width` / `height` | Controls iframe viewport — must be large enough to expose the target element | Varies by target            |
| `top` / `left`     | Pixel-accurate offset from the containing block                              | Calibrated per target       |
>[!interesting]+ Why `opacity: 0.00001` instead of `opacity: 0`
>- Setting `opacity: 0` makes an element fully transparent (but still part of the DOM). 
>- However, some browsers implement **clickjacking protection** by applying a threshold-based `<iframe>` transparency detection (for example, Chrome version 76 includes this behavior but Firefox does not).
>- Small non-zero `opacity` value, such as `0.00001`, doesn't get detected yet still remains unnoticeable to human eye.

>[!note] Setting `pointer-events: none` on an element disables click reception entirely, regardless of `z-index` or `opacity`.


- The `<iframe>` and decoy elements should use `position: absolute` to position them relative to the containing block (usually the `<body>` or a positioned parent). 
- This removes them from the normal document flow and allows setting `x`/`y` freely using `top`, `left`, `right`, and `bottom` properties.
---
- Using `position: relative` on a containing div and `position: absolute` on child elements gives you a local coordinate system within that `<div>`, which can simplify alignment when the decoy and `<iframe>` share a common parent. The exact approach depends on how you structure the attack page.

## Constructing clickjacking attacks

- The attack page is a single HTML file you host. It embeds the target site in a transparent `<iframe>` and overlays a decoy UI.

- Basic template:


```html
<head>
	<style>
		#target_website {
			position: relative;
			width: 100px;
			height: 100px;
			opacity: 0.00001;
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
	...decoy web content here...
	</div>
	<iframe id="target_website" src="https://example.com">
	</iframe>
</body>
```

>[!note] To generate Clickjacking exploits automatically, without burdening yourself with manual element adjustment, you can use the Burp's [`Clickbandit`](https://portswigger.net/burp/documentation/desktop/tools/clickbandit) tool.

## Clickjacking with form pre-populated via `GET` parameters

- Many applications allows

## Frame busting scripts and the sandbox bypass

### Frame busting


>**Frame busting** is a technique used to prevent a website from being loaded inside an HTML `<frame>` or `<iframe>`, primarily to mitigate clickjacking attacks.

- Frame busting is usually implemented via JavaScript that detects if the current window is the topmost. If no, then redirect or hide the content. 
 
- Common implementations:

	- Navigate top window to self:
	
	```js
	if (top !== self) {
	    top.location = self.location;
	}
	```
	
	- Conditional content rendering:
	
	```javascript
	if (window.self !== window.top) {
	    document.body.style.display = 'none';
	}
	```
	
	- Replace top-level navigation:
	
	```js
	if (top.location !== location) {
	    top.location.replace(document.location);
	}
	```

- All such techniques rely on JavaScript being able to access `window.top` and navigate the top-level frame. But this can be bypassed easily using `sandbox` frames.

### The sandbox bypass

- The HTML `sandbox` attribute on `<iframe>` creates a permission-restricted execution context for the embedded page.
- By default, a sandboxed iframe has no permissions at all. 
- You selectively re-enable only those capabilities you need for the attack to work and omitting the one that enables frame busting.

```html
<iframe src="https://example.com/my-account"
        sandbox="allow-forms">
</iframe>
```

- `allow-forms` — re-enables form submission. Without this, submitting any form inside the `<iframe>` would be silently blocked. This is required for the attack to function.
- `allow-scripts` — (not included above) re-enables JavaScript execution. If the frame buster is the only script on the page, omitting this kills the frame buster outright. If the page needs JavaScript to render correctly, add `allow-scripts`.


>[!important] `allow-top-navigation` — **deliberately omitted**.
>- Restricting top navigation is what we use the sandbox for.
>- Without `allow-top-navigation`, JavaScript simply can't check `top.location = self.location` — this code silently fails with a `SecurityError` exception. 
>- The frame buster runs, reaches the navigation line, throws a silenced exception, and accomplishes nothing.

- Basic clickjacking exploit with frame busting bypass:

```html
<head>
	<style>
		#target_website {
			position: relative;
			width: 100px;
			height: 100px;
			opacity: 0.00001;
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
	...decoy web content here...
	</div>
	<iframe sandbox="allow-forms" id="target_website" src="https://example.com">
	</iframe>
</body>
```

