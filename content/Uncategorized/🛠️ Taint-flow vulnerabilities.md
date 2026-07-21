---
created: 2026-07-15
tags:
  - web_hacking
status: stub
---
## Taint-flow model

Many client-side and server-side injection vulnerabilities can be described using a **taint-flow model**.

>A **taint-flow vulnerability** occurs when untrusted data originating from a attacker-controlled **source** reaches a security-sensitive **sink** without being transformed or constrained in a manner that makes it safe for the destination context.

- Not every source-to-sink flow is inherently vulnerable. The vulnerability arises only when the sink interprets or executes the data in a security-sensitive manner and the required validation or sanitization is absent.

>A **source** is any program location, API, or object through which data enters an application and may be influenced, directly or indirectly, by an attacker.

>A **sink** is a program location or API that performs a security sensitive operation whose behavior depends on the data supplied to it.

 - The term ***taint*** is used to indicate that data originates from an untrusted source (that it's *tainted*). This is just a "tag" used for reasoning about data flow.
 - During security analysis, data remains *tainted* until it's either transformed for the the intended sink or proven to be safe.

>**Taint transfer**, also called **taint flow** or **taint propagation**, is the process by which the taint associated with one value is propagated to another value as the program executes.

- Examples of taint transfers:
	- Assigning one variable to another.
	- Concatenating strings.
	- Passing values as function arguments.
	- Returning values from functions.
	- Reading or writing object properties.

>[!example]+ Example: DOM-based taint transfer
> ```js
> const input = location.search;    // source (tainted)
> const value = input;              // taint transfer
> const html = "<p>" + value;       // taint transfer
> element.innerHTML = html;         // sink
> ```

- Although several intermediate variables may be introduced, the attacker-controlled data continues to propagate through the program until it reaches the sink. Security analysis therefore focuses on the **entire data-flow path**, rather than on isolated statements.

## Static and dynamic taint flow analysis


There are two primary approaches to taint analysis.
- **Static taint analysis** — examines JavaScript source code without executing it; typically involves code review and automated static analysis tools.
- **Dynamic taint analysis** — observes tainted data during actual execution in the browser.

For modern JavaScript-heavy applications, combining static and dynamic analysis is usually the most effective approach.