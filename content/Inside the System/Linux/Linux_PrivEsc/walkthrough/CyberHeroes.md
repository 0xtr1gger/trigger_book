---
created: 09-02-2026
---
## Recon

- Port scanning:

```bash
sudo nmap 10.66.133.22
```

```bash
Starting Nmap 7.95 ( https://nmap.org ) at 2026-02-09 16:13 UTC
Nmap scan report for 10.66.133.22
Host is up (0.17s latency).
Not shown: 998 closed tcp ports (reset)
PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http

Nmap done: 1 IP address (1 host up) scanned in 2.38 seconds
```

- Accessing the website's login page:

![[images/Linux/Linux_PrivEsc/ctf/CyberHeroes/login.png]]

- If you inspect the source, you'd see this:

```JS
    function authenticate() {
      a = document.getElementById('uname')
      b = document.getElementById('pass')
      const RevereString = str => [...str].reverse().join('');
      if (a.value=="h3ck3rBoi" & b.value==RevereString("54321@terceSrepuS")) { 
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
          if (this.readyState == 4 && this.status == 200) {
            document.getElementById("flag").innerHTML = this.responseText ;
            document.getElementById("todel").innerHTML = "";
            document.getElementById("rm").remove() ;
          }
        };
        xhttp.open("GET", "RandomLo0o0o0o0o0o0o0o0o0o0gpath12345_Flag_"+a.value+"_"+b.value+".txt", true);
        xhttp.send();
      }
      else {
        alert("Incorrect Password, try again.. you got this hacker !")
      }
    }
```

- So, username and password are:

```bash
username = h3ck3rBoi
password = SuperSecret@12345
```

```bash
echo "54321@terceSrepuS" | rev
```

![[images/Linux/Linux_PrivEsc/ctf/CyberHeroes/flag.png]]

```
flag{edb0be532c540b1a150c3a7e85d2466e}
```


Well, m... Why easy challenges are so weird sometimes? May be I should start going through medium ones?