---
created: 2026-06-11
tags:
  - web_hacking
status: draft
---
## JavaScript prototypes and inheritance

### Notes on JavaScript

- JavaScript (JS) is a high-level, interpreted programming language primarily used in web browsers (client-side) and on servers via Node.js (server-side).
- It si **dynamically-typed** (variable types are determined at runtime) and supports both object-oriented and functional programming. 

>**Variables** are contains for storing data. 

- JavaScript variables are declared using `let`, `const`, or `var` (older):

```js
let name = "Jane"; // string
constr age = 20;   // number, can't be reassigned
```

- **Data types** can be:
	- **Primitive**: Simple values like `string`, `number`, `boolean` (`true`/`false`), `null`, `undefined`, `symbol`, `bigint`.
	- **Object**: Complex data structures that can hold multiple values and behaviors. 
- Primitive data types:

| Primitive         | Description                                                                                                                                                               | Examples                                                |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| `number`          | Integer and floating-point numbers.<br>Special numeric values: `NaN` (Not a Number), `Infinity`, `-Infinity`.                                                             | `11`, <br>`3.14`, <br>`-5`, <br>`NaN`                   |
| `string`          | A sequence of UTF-16 characters.<br>Strings are **immutable**: you can't modify characters at specific string indeces.                                                    | `"Hello"`, <br>`'world'`, <br>`` `template literals` `` |
| `boolean`         | A logical entity who two possible values: `true` or `false`                                                                                                               | `true`, <br>`false`                                     |
| `undefined`       | Represents absence of a value or an uninitialized variable. <br>This is the default value when a variable is declared but not assigned.                                   | `let x;`                                                |
| `null`            | Represents intentional absence of any object value.                                                                                                                       | `let obj = null;`                                       |
| `symbol` (ES6)    | Represents a unique and immutable identifier.<br>Used as keys for object properties to avoid property name collisions.<br>Created using the `Symbol()` function.          | `const sym = Symbol('desc');`                           |
| `bigint` (ES2020) | Represents integers with arbitrary precision; used for very large integers beyond `Number.MAX_SAFE_INTEGER`.<br>Created by appending `n` or using `BigInt()` constructor. | `123456789012345678901234567890n`                       |


>**Functions** are reusable blocks of code. 

- In JavaScript, functions themselves are objects that can be assigned to variables, passed as arguments, etc.

```js
function greet() {
  console.log("Hello!");
}
greet(); // calls the function
```

>[!note]+ Assigning a primitive to another variable copies the actual value.
> 
> ```JS
> let a = 10;
> let b = a; 
> b = 20;
> console.log(a); // 10, unchanged
> ```

### Objects

- In JavaScript, **almost everything is an object** (or can behave like one).

>An **object** is a collection of **properties** (key-value pairs).

```js
let person = {
	name: "John",   // property: key "name", value "John"
	age: 23,
	greet: function() { 
		console.log("Hi"); // method (function property)
	}
};
```

- There are two ways to access object properties:
	- **Dot notation**: `person.name`.
	- **Bracket notation**: `person["name"]` (useful when keys have special characters or are dynamic).

>[!important] Objects have properties defined directly on them (*own*) and can access properties from their **prototype** (*inherited*).

- **Objects are mutable**: you can add, modify, or delete properties at runtime.

```js
person.job = "Developer"; // adds a new property
delete person.age;        // removes the property
```

- Two ways to construct an object:
	- **Object literal**: `{}` (as shown above).
	- **Constructor functions** or classes (ES6+):

	```js
	function Person(name) {
	  this.name = name;
	}
	let p1 = new Person("Charlie");
	```

>[!note] `this` inside an object method refers to the object that owns the method; in constructors, this is the object being created.

- **`Object.create(proto)`** creates a new object with a specified prototype.
### Prototypes and the prototype chain

- Every JavaScript object (except some primitives) has an internal link to another object called its **prototype**. This link is used for **inheritance**.

>Every JavaScript object has a hidden internal property, `[[Prototype]]`, that represents the object's prototype. This property is called an **internal prototype** or **internal slot**.

- `__proto__` is a (non-standard but widely supported) way to access an object's prototype. It's a getter/setter for the internal `[[Prototype]]` slot.

- The `prototype` property exists on **functions** (and constructors). When you create an object using `new Constructor()`, the new object's `__proto__` points to `Constructor.prototype`.
---
- Object prototype can either be `null` or another object.

>[!important] The prototype is itself an object that contains properties and methods. This creates a **prototype chain**.
>- If a property or method is not found on the object itself, JavaScript looks up the prototype chain until it either finds the property or reaches `null` (the end of the chain).
>- In other words, a prototype acts as a fallback source of properties and methods of an object.

>[!important] Prototype chain of every object ultimately leads to `null`.

```js
let arr = [1, 2, 3];  // array instance

arr.__proto__              -> Array.prototype
Array.prototype.__proto__  -> Object.prototype
Object.prototype.__proto__ -> null
```

- `arr.push(4)` works because push is on Array.prototype, inherited by all arrays.
- `arr.toString()` comes from Object.prototype.

>[!important] Objects automatically **inherit** all properties and methods from their assigned prototype, *unless they already have their own property with the same name*. This is called **prototype inheritance**. 

>[!important] All plain objects inherit from `Object.prototype` by default (unless created with `Object.create(null))`.


>[!Important] Objects inherit properties not only from their immediate prototype, but from all objects before them in the prototype chain.
>When you access a property or method of an bbject, JavaScript first checks if the property exist on the object itself. If not found, it checks the Object's prototype. 
>This prototype lookup continues up to the chain until:
>- Property is found, or
>- The end of the chain (`null`) is reached; this results in `undefined`.

- If an object has its own property with the same name as one in its prototype, the own property **shadows** (overrides) the inherited one. This is called **shadowing**.

```JS
const grandparent = { val: 1 };
const parent = Object.create(grandparent);
parent.val = 2;
const child = Object.create(parent);
child.val = 3;

console.log(child.val); // 3 (own property)
delete child.val;
console.log(child.val); // 2 (inherited from parent)
delete parent.val;
console.log(child.val); // 1 (inherited from grandparent)
```

### Inheritance

- JS uses **prototype inheritance** (not class inheritance like in Java/C++).
	- Objects inherit properties and methods from their prototype.
	- **Changes to a prototype affect all objects that inherit from it** (unless they have their own overriding property).

```js
// polluting Object.prototype (dangerous!)
Object.prototype.isAdmin = true;

let user1 = {};  // no own 'isAdmin'
let user2 = { isAdmin: false };  // own property overrides

console.log(user1.isAdmin);  // true (inherited)
console.log(user2.isAdmin);  // false (own)
```
## Prototype pollution

>**Prototype pollution** is a JavaScript vulnerability that allows an attacker to inject arbitrary properties into global object prototypes.

- Prototype pollution occurs when attacker-controlled input is recursively merged into an object without sanitizing keys like `__proto__`, `constructor`, or `prototype`.

>[!important] Prototype pollution affects only **JavaScript applications** (Node.js). 

- It is not usually a standalone vulnerability that directly executes code.
- Instead, it gives you control over object properties that developers assume are safe and non-controllable. 
- You then chain it with other weaknesses (gadgets + sinks) to achieve impact like **DOM [[XSS]]** (client-side) or even **Remote Code Execution (RCE)** (server-side).

>[!note]+ Pollution happens when you make the JavaScript engine do something like:
>```
>target.__proto__.someProperty = maliciousValue;
>```
>- This sets `someProperty` directly on `Object.prototype`.

### The root cause

- Prototype pollution typically occurs in recursive merge / extend / deep clone functions that combine objects without sanitizing keys.

- Common in `merge()` or `extend()` functions from libraries like lodash, jQuery, or custom code:

```js
function merge(target, source) {
	for (let key in source) {  // loops over source keys
		if (typeof source[key] === 'object') {
			if (!target[key]) target[key] = {};
				merge(target[key], source[key]); // recursive!
		} else {
			target[key] = source[key]; // assignment
		}
	}
}
```

- If `source = {"__proto__": {"polluted": true}}`, the merge sets a property on `Object.prototype.polluted`.
- During merging:
	1. The parser treats `__proto__` as a normal string key.
	2. The recursive merge eventually does an assignment equivalent to `target.__proto__.polluted = "true"`.
	3. Because `__proto__` is special (it's a getter for the prototype), `polluted` lands on `Object.prototype`.
- Now **every object** in the application has `.polluted === true` (unless it has its own property shadowing it).

>[!note] `JSON.parse()`
> 
> - Object literals like `let obj = {__proto__: {x:1}}` do **not** create a real `__proto__` own property (it sets the prototype instead).
> - But `JSON.parse('{"__proto__": {"x":1}}')` **does** create a real own property named `__proto__`. This is why JSON input is a common vector.

### Three components for exploitation

>[!important]+ Three components for exploitation
> 
> - **Source** — User-controllable input that reaches a merge function.
> - **Gadget** — A property the app reads from an object (via inheritance) and uses unsafely.
> - **Sink** — A dangerous function or API that executes code based on the gadget value.

- Sources:
	- **URL query string or hash/fragment**: `?__proto__[foo]=bar` or `#__proto__[foo]=bar`.
	- **JSON input** (via `JSON.parse()` + merge): Common in `POST` bodies, web messages, `localStorage`, etc.
	- **Web messages** (`postMessage`).
	- Other: Cookies, headers, etc., if parsed into objects.
- Gadgets:
	- A gadget is a property that:
		- The application reads from a config/options object (using `obj.prop || default` style).
		- Is **not** defined as an own property on that object (so inheritance works, otherwise shadowing blocks it).
		- Gets passed to a dangerous sink without sanitization.
	- Gadgets can be in:
		- Application code.
		- Third-party libraries.
		- Browser built-in APIs.

>[!example]+
>```js
> let transport_url = config.transport_url || defaults.transport_url;
> let script = document.createElement('script');
> script.src = `${transport_url}/example.js`;
> document.body.appendChild(script);
> ```
> 
> - If you pollute `Object.prototype.transport_url = "data:,alert(1)//"`, the config object inherits it.
> - Result: Script tag with `src="data:,alert(1)//"` → DOM XSS.

- Sinks:
	- **Client-side**: Anything that leads to DOM XSS (`innerHTML`, `script.src`, `eval()`, `new Function()`, event handlers, etc.).
	- **Server-side** (Node.js): Properties that control `child_process.exec`, file paths (`fs`), module loading, deserialization, etc.


>[!note]+ Client-side vs. server-side
>- **Client-side**: Usually DOM XSS. Easier to trigger via a malicious link. Tools like **DOM Invader** in Burp Suite automate source/gadget discovery.
>- **Server-side**: Can lead to RCE, privilege escalation, etc. Payloads often target things like `json spaces` for detection or deeper config objects.

## Client-side prototype pollution

- **Client-side prototype pollution** is the variant of the vulnerability that occurs entirely in the browser's JavaScript environment. The goal is usually to achieve **DOM-based XSS** (or other client-side impacts like open redirects, script execution, etc.).

- On the client side, your goal is to:

	1. **Pollute** Object.prototype (or another prototype) using a **source** (user-controllable input).
	2. Find a **gadget** — a place in the application's (or library's) code where it reads a property from an object that can now inherit your polluted value.
	3. Pass that value to a **sink** — a dangerous browser API that leads to code execution (typically DOM XSS).

### Finding sources manually

Try different ways of adding an arbitrary property to `Object.prototype` until you find a source that works.

1. **Identify a parameter to target**
	- Common sources on the client:
		- **Query string** (`location.search`): `?__proto__[polluted]=true`.
		- **URL fragment/hash** (`location.hash`): `#__proto__[polluted]=true`.
		- **JSON input** parsed with `JSON.parse()` (from `fetch()`, `postMessage()`, `localStorage`, etc.).
		- Web messages (`window.postMessage`).
		- Other: cookies, headers, or any data that gets merged into an object.
	
>[!example]+ Example: prototype pollution in JSON
> ```json
> {
>   "username": "janedoe",
>   "__proto__": {
>     "polluted": "true"
>   }
> }
> ```

2. **Attempt to inject a property to `Object.prototype`**
	- `?__proto__[polluted]=true` — using `__proto__`, bracket notation.
	- `?__proto__.polluted=true` — using `__proto__`, dot notation.
	- `?constructor[prototype][polluted]` — via `constructor` prototype property. 

>[!note] `myObject.constructor.prototype` is equivalent to `myObject.__proto__`. 

3. **Check the polluted property**
	- Open DevTools Console and type:

	```js
	Object.prototype.polluted // if polluted, should return 'true'
	```
	
	- If worked (returns `true`), prototype pollution is found. Proceed to finding an exploitable gadget.
	- If blocked (`undefined`), try an alternative notation or sanitization bypass techniques.

4. **Attempt to bypass flawed key sanitization**
	- Bypass non-recursive filters by injecting nested `__proto__` or `constructor` keywords, such as `?__pr__proto__oto__[polluted]=true`.

### Finding gadgets manually

>[!important]+ Gadgets
> - A **gadget** is a property read from an object in the code where:
> 	- The property is **not** defined as an own property on that object.
> 	- The value is inherited from the polluted prototype.
> 	- The value is then used in a dangerous way (passed to a sink).
> 	- Gadgets are often found in:
> 		- Application custom code.
> 		- Third-party libraries (very common).
> 		- **Browser built-in APIs** (PortSwigger Research discovered widespread ones).

Once you've found a source that lets you add arbitrary properties to the global `Object.prototype`, find a suitable gadget that you can use for an exploit.

1. Inspect the source code and identify properties that are used by the application or any libraries it imports.

2. Intercept the JavaScript you want to test using Burp. 

3. Add a `debugger;` statement at the start of the script, then forward any remaining requests and responses. Make sure the console is open, or the browser will ignore the expression.

4. In Burp's browser, go to the page on which the target script is loaded. The `debugger;` statement pauses execution of the script.

5. While the script is still paused, switch to the console and enter the command:

	```js
	Object.defineProperty(Object.prototype, 'gadget', {
		get() {
			console.trace();
			return 'polluted';
		}
	})
	```

	- The property is added to the global `Object.prototype`, and the browser will log a stack trace to the console whenever it is accessed.

6. Press the button to continue execution of the script and monitor the console. If a stack trace appears, this confirms that the property was accessed somewhere within the application.

7. Expand the stack trace and use the provided link to jump to the line of code where the property is being read.

8. Using the browser's debugger controls, step through each phase of execution to see if the property is passed to a sink, such as `innerHTML` or `eval()`.
    
9. Repeat this process for any properties that you think are potential gadgets.

> [!example]+
> ```js
> // application code
> const config = getConfig();  // maybe empty or partial object
> const url = config.transportUrl || 'https://default.com';
> 
> // later:
> const script = document.createElement('script');
> script.src = url;
> document.head.appendChild(script);
> ```
> 
> - If you pollute `Object.prototype.transportUrl = "https://evil.com/xss.js"`, the `config` object inherits it → script tag loads your malicious JS.

- Common sinks that turn a gadget into DOM XSS:
	- `innerHTML`, `outerHTML`.
	- `script.src`, `iframe.src`, `object.data`.
	- `eval()`, `new Function()`.
	- Event handlers (`onclick`, etc.).
	- `document.write()`.
	- Various DOM manipulation methods.

### DOM Invader

- Burp Suite's **DOM Invader** automates almost everything:
	- Automatically detects prototype pollution **sources**.
	- Scans for **gadgets**.
	- Generates DOM XSS PoCs.
	- Works great with third-party libraries and browser APIs.

- Enable it in Burp's built-in browser when testing client-side prototype pollution labs.

## Validation bypass

## Server-side prototype pollution

- Testing and exploitation of server-side prototype pollution vulnerabilities adds several difficulties compared to client-side variant:
	- **No access to source code**
	- **Lack of developer tools**
	- **DoS risks**
	- **Pollution persistence**

## References and further reading

- https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Prototype%20Pollution