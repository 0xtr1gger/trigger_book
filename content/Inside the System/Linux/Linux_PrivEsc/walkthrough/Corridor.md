---
created: 23-01-2026
---

- Challenge: [Corridor](https://tryhackme.com/room/corridor)
- Target IP address: `10.67.181.120`

```
10.67.181.120
```
## Recon

- Basic port scan:

```bash
sudo nmap 10.67.181.120
```

```bash
Starting Nmap 7.95 ( https://nmap.org ) at 2026-01-23 15:18 UTC
Nmap scan report for 10.67.181.120
Host is up (0.16s latency).
Not shown: 999 closed tcp ports (reset)
PORT   STATE SERVICE
80/tcp open  http

Nmap done: 1 IP address (1 host up) scanned in 2.89 seconds
```


- Accessing the website:

![[2026-01-23-162005_hyprshot.png]]

- Page source looks like this:


```HTML
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css"
        integrity="sha384-9aIt2nRpC12Uk9gS9baDl411NQApFmC26EwAOH8WgZl5MYYxFfc+NcPb1dKGj7Sk" crossorigin="anonymous">
    <title>Corridor</title>

    <link rel="stylesheet" href="/static/css/main.css">
</head>

<body>
    

<img src="/static/img/corridor.png" usemap="#image-map">

    <map name="image-map">
        <area target="" alt="c4ca4238a0b923820dcc509a6f75849b" title="c4ca4238a0b923820dcc509a6f75849b" href="c4ca4238a0b923820dcc509a6f75849b" coords="257,893,258,332,325,351,325,860" shape="poly">
        <area target="" alt="c81e728d9d4c2f636f067f89cc14862c" title="c81e728d9d4c2f636f067f89cc14862c" href="c81e728d9d4c2f636f067f89cc14862c" coords="469,766,503,747,501,405,474,394" shape="poly">
        <area target="" alt="eccbc87e4b5ce2fe28308fd9f2a7baf3" title="eccbc87e4b5ce2fe28308fd9f2a7baf3" href="eccbc87e4b5ce2fe28308fd9f2a7baf3" coords="585,698,598,691,593,429,584,421" shape="poly">
        <area target="" alt="a87ff679a2f3e71d9181a67b7542122c" title="a87ff679a2f3e71d9181a67b7542122c" href="a87ff679a2f3e71d9181a67b7542122c" coords="650,658,644,437,658,652,655,437" shape="poly">
        <area target="" alt="e4da3b7fbbce2345d7772b0674a318d5" title="e4da3b7fbbce2345d7772b0674a318d5" href="e4da3b7fbbce2345d7772b0674a318d5" coords="692,637,690,455,695,628,695,467" shape="poly">
        <area target="" alt="1679091c5a880faf6fb5e6087eb1b2dc" title="1679091c5a880faf6fb5e6087eb1b2dc" href="1679091c5a880faf6fb5e6087eb1b2dc" coords="719,620,719,458,728,471,728,609" shape="poly">
        <area target="" alt="8f14e45fceea167a5a36dedd4bea2543" title="8f14e45fceea167a5a36dedd4bea2543" href="8f14e45fceea167a5a36dedd4bea2543" coords="857,612,933,610,936,456,852,455" shape="poly">
        <area target="" alt="c9f0f895fb98ab9159f51fd0297e236d" title="c9f0f895fb98ab9159f51fd0297e236d" href="c9f0f895fb98ab9159f51fd0297e236d" coords="1475,857,1473,354,1537,335,1541,901" shape="poly">
        <area target="" alt="45c48cce2e2d7fbdea1afc51c7c6ad26" title="45c48cce2e2d7fbdea1afc51c7c6ad26" href="45c48cce2e2d7fbdea1afc51c7c6ad26" coords="1324,766,1300,752,1303,401,1325,397" shape="poly">
        <area target="" alt="d3d9446802a44259755d38e6d163e820" title="d3d9446802a44259755d38e6d163e820" href="d3d9446802a44259755d38e6d163e820" coords="1202,695,1217,704,1222,423,1203,423" shape="poly">
        <area target="" alt="6512bd43d9caa6e02c990b0a82652dca" title="6512bd43d9caa6e02c990b0a82652dca" href="6512bd43d9caa6e02c990b0a82652dca" coords="1154,668,1146,661,1144,442,1157,442" shape="poly">
        <area target="" alt="c20ad4d76fe97759aa27a0c99bff6710" title="c20ad4d76fe97759aa27a0c99bff6710" href="c20ad4d76fe97759aa27a0c99bff6710" coords="1105,628,1116,633,1113,447,1102,447" shape="poly">
        <area target="" alt="c51ce410c124a10e0db5e4b97fc2af39" title="c51ce410c124a10e0db5e4b97fc2af39" href="c51ce410c124a10e0db5e4b97fc2af39" coords="1073,609,1081,620,1082,459,1073,463" shape="poly">
    </map>


</body>
</html>
```

So, image regions where the doors are depicted are clickable, and each door leads to a page with a picture of an empty room. Kinda really a corridor. Though "rooms" seem absolutely identical and there's nothing interesting there:

```HTML
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css"
        integrity="sha384-9aIt2nRpC12Uk9gS9baDl411NQApFmC26EwAOH8WgZl5MYYxFfc+NcPb1dKGj7Sk" crossorigin="anonymous">
    <title>Corridor</title>

    <link rel="stylesheet" href="/static/css/main.css">
</head>

<body>
    

<style>
    body{
        background-image: url("/static/img/empty_room.jpg");
        background-size:  cover;
    }
</style>

</body>
</html>
```

- But the link to each room has a name that resembles an MD5 hash (32 characters in length). 
- Retrieve the hashes:

```bash
curl -s http://10.67.181.120/ | grep area | awk '{print $3}' | awk -F'=' '{print $2}' | tr -d '"' > hashes.txt
```

```bash
c4ca4238a0b923820dcc509a6f75849b 1
c81e728d9d4c2f636f067f89cc14862c 2
eccbc87e4b5ce2fe28308fd9f2a7baf3 3
a87ff679a2f3e71d9181a67b7542122c 4
e4da3b7fbbce2345d7772b0674a318d5 5
1679091c5a880faf6fb5e6087eb1b2dc 6
8f14e45fceea167a5a36dedd4bea2543 7
c9f0f895fb98ab9159f51fd0297e236d 8
45c48cce2e2d7fbdea1afc51c7c6ad26 9
d3d9446802a44259755d38e6d163e820 10
6512bd43d9caa6e02c990b0a82652dca 11
c20ad4d76fe97759aa27a0c99bff6710 12
c51ce410c124a10e0db5e4b97fc2af39 13
```

So these are just MD5-hashed numbers.

- There're no numbers after `13`. 
- Here is what you find if you try accessing a page with the name of a hashed `0`:

```bash
curl http://10.67.181.120/cfcd208495d565ef66e7dff9f98764da
```

```bash
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css"
        integrity="sha384-9aIt2nRpC12Uk9gS9baDl411NQApFmC26EwAOH8WgZl5MYYxFfc+NcPb1dKGj7Sk" crossorigin="anonymous">
    <title>Corridor</title>

    <link rel="stylesheet" href="/static/css/main.css">
</head>

<body>
    

<style>
    body{
        background-image: url("/static/img/empty_room.png");
        background-size:  cover;
    }

    h1 {
        width: 100%;
        position: absolute;
        top: 40%;
        text-align: center;
    }
</style>
<h1>
    flag{2477ef02448ad9156661ac40a6b8862e}
</h1>

</body>
</html>
```

Got the flag!