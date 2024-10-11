## Ansible

Ansible is an open-source automation tool that simplifies configuration management, application deployment, task automation, and orchestration processes. Developed by Red Hat, it uses a declarative language (YAML) to define automation tasks, making it easy to read and write.

><span style="color:#668cff">Ansible</span> is a powerful [open source](https://github.com/ansible/ansible) automation tool written in Python and used for configuration management, application deployment, cloud provisioning, ad-hoc task execution, network automation, and orchestration.

Ansible is particularly useful for automating tasks across multiple servers. Examples of tasks that Ansible can perform include:

- Applying patches and updates via `yum`, `apt`, and other package managers
- Checking resource usage (e.g., disk space, memory, CPU, swap space, network, etc.)
- Monitoring and checking log files
- Managing system users and groups
- Managing DNS settings and host files
- Copying files to and from remote servers
- Deploying and maintaining applications
- Rebooting servers as needed
- Managing scheduled task, such as cron jobs
- And much more

## Architecture

- Ansible follows a <span style="color:#668cff">client-server architecture</span>
	- Managed nodes are configured from a centralized server, called the Control node or the Controller. 
	- The Controller can be either be a local machine, whether physical or virtual, or a dedicated remote server with Ansible installed.
	- Ansible Controller works well with any node to which it can connect — both remote or local.
	
- Ansible is <span style="color:#668cff">agentless</span>
	- Ansible does not require any agent software to be installed on managed nodes. The Ansible Controller communicates with the nodes over SSH (or WinRM), which simplifies configuration and reduces maintenance overhead.
	- Agentless is what makes Ansible lightweight compared to other automation tools such as Chef and Puppet.

>Note: Despite the absence of agent software on managed nodes, they must be able to execute instructions in at least one programming language. It does not necessarily have to be Python, but Python is the primary programming language in which Ansible modules are written.

- Ansible operates in a <span style="color:#668cff">push-based model</span>
	- Changes are initiated and pushed to managed nodes by the Controller via SSH (or WinRM for Windows). This architecture allows for immediate task execution, eliminating the need for nodes to authenticate and pull changes themselves.

- Ansible follows the <span style="color:#668cff">mutable infrastructure paradigm</span>
	- Ansible follows the mutable infrastructure paradigm, where host configuration can be changed dynamically after deployment, rather than adheres the immutable paradigm. However, this is considered disadvantageous in terms of configuration drift. 

>The mutable infrastructure paradigm is one of the key reasons why other tools that follow immutable paradigm, such as Terraform, may be preferred over Ansible in certain situations. Although it is entirely feasible to implement immutable infrastructure with Ansible, Terraform is generally recommended for managing large and complex systems. 

- Ansible is primarily a <span style="color:#668cff">declarative</span> automation tool
	- In Ansible, playbooks define the ultimate desired state of the infrastructures or applications using YAML syntax (which is inherently a declarative language) rather than the specific instructions to be executed. In other words, Ansible allows users to focus on the end state instead of the exact steps to get there (which represents a procedural approach.). 
	- However, Ansible also allows for procedural code, particularly through the use of shell modules (e.g., `shell`, `command`) and Python code in playbooks.

- Ansible execution is <span style="color:#668cff">idempotent</span>
	- Ansible modules are designed to be idempotent, meaning they can be executed multiple times without causing unintended changes to the system. If a module is executed repeatedly with the same parameters, Ansible ensures that no further changes occur beyond what is explicitly defined. This characteristic is critical for maintaining a consistent state across environments.

Key components of Ansible automation include:

- <span style="color:#668cff">Playbooks</span>
	- YAML files that describe the automation process. Playbooks contain a set of instructions (plays) that defined tasks to be executed on managed nodes.

- <span style="color:#668cff">Inventory</span> 
	- A list of managed nodes or hosts that Ansible configures and deploys. It's typically written in INI or YAML format and can include variables related to each host.

- <span style="color:#668cff">Modules</span>
	- Standalone, reusable units of code that perform specific actions on managed devices (e.g., managing services, installing packages, executing commands).

- <span style="color:#668cff">Templates</span>
	- Files that define the structure and content of configuration files or scripts that need to be generated dynamically. Ansible templates are written using the Jinja2 template language and have a `.j2` extension.

- <span style="color:#668cff">Variables</span>
	- Key-value pairs defined in YAML format used to store reusable configuration data that can be substituted into playbooks and templates.


## inventory

Inventory files are where the nodes Ansible responsible to configure and automate are defined.

>An Ansible <span style="color:#668cff">Inventory</span> is a file that defines a list of logically grouped hosts that Ansible deploys and configures. 

- Inventory files are configured on the Ansible Controller. 
- The default location for an Ansible inventory is `/etc/ansible/hosts`.

```bash
mkdir /etc/ansible && \
touch /etc/ansible/hosts
```

- An alternate location for an inventory can be specified at the command line using the `-i <path>` option, or in the Ansible configuration under the `inventory` directive.

- An inventory file can be written in either of two formats: INI or YAML. 
- It typically consists of a list of IP addresses or domain names organized into logical groups. To provide further details about the managed devices, an inventory can specify associated variables in the `key=value` format.

Below is an example of an INI Inventory File:

```ini
[webserers]
web1.example.com http_port=80
web2.example.com http_port=8080

[dbservers]
db1.example.com ansible_user=dbuser ansible_password=dbpass
two.example.com
three.example.com

[webservers:vars]
ansible_user=ansible

[all:vars]
ansible_python_interpreter=/usr/bin/python3
```

-  Here, `www1.example.com`, `www2.example.com`, etc. define host domain names; `http_port=80`, `ansible_user=dbuser`, etc. denote variables and their values.
- Groups of hosts that Ansible controls are defined in square brackets, `[]`, such as `[webservers]` or `[dbservers]`.
- Host-specific variables are specified in the same line with the host IP address or a domain name. Hosts can accept multiple `key=value` parameters per line.
- Variables, global to a particular group of hosts, are defined in `:vars` sections for the respective group, for example, `[webservers:vars]`.
- The `all:vars` section lists variables that apply to all hosts in the inventory.

INI format is concise and easy-to-read; however, it might not be suitable for large and complex inventories, at least due to limitations in variable types:
- When declared inline with the host, INI values are interpreted as Python literal structures (e.g., strings, numbers, tuples, lists, dictionaries, Boolean, None). However, all INI variables declared in a `:vars` sections are treated as strings. For example, `var=FALSE` would create a string equal to `'FALSE'`. In cases where the variable type is critical, YAML format is preferable.

YAML inventories interpret variable values more accurately, preserving their types. Below is an example of the same inventory file, but in YAML format:

```YAML
all:
  hosts:
    webservers:
      hosts:
        web1.example.com:
          http_port: 80
        web2.example.com:
          http_port: 8080
        
    dbservers:
      hosts:
        db1.example.com:
          ansible_user: dbuser
          ansible_password: dbpass
        two.example.com:
        three.example.com:
  
  vars:
    ansible_python_interpreter: /usr/bin/python3
    webservers:
      ansible_user: ansible
```


- YAML inventories use nested structures to denote group definitions under the `all` key.
- In YAML, variables can be defined as part of host or group configurations, or globally with the `all:vars:` directive.

An inventory can be either static or dynamic. Above are the examples of static inventories defined in text files; in contrast, dynamic inventory files are generated by scripts when a playbook is run.

- A dynamic inventory tracks hosts from one or more sources, such as cloud providers (AWS, Azure, GCP) or Configuration Management Database (CMDB) systems. This allows for real-time updates and management of inventory based on the current state of the infrastructure, rather than pre-defined static configuration.
