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

## playbooks

The core of the Ansible automation framework is playbooks. 

>An Ansible <span style="color:#668cff">Playbook</span> is a YAML file that defines a series of tasks to be executed on managed nodes.
>Playbooks consist of a series of instructions known as <span style="color:#668cff">plays</span>, the basic units of Ansible execution.
>Each play contains a set of <span style="color:#668cff">tasks</span>, which are executed in order. 

Below is an example of an Ansible playbook that consists of two plays: the first play updates web servers, while the second play updates database servers. Each play consist of two tasks. 

```YAML
---
# the first play
- name: Update web servers
  hosts: webservers
  remote_user: root

  tasks:

  # the first task in the play
  - name: Ensure apache is at the latest version
    ansible.builtin.yum:
      name: httpd
      state: latest

  # the secoond task in the play
  - name: Write the apache config file
    ansible.builtin.template:
      src: /srv/httpd.j2
      dest: /etc/httpd.conf

# The second play
- name: Update db servers
  hosts: databases
  remote_user: root

  tasks:

  # the first task in the play
  - name: Ensure postgresql is at the latest version
    ansible.builtin.yum:
      name: postgresql
      state: latest

  # the secoond task in the play
  - name: Ensure that postgresql is started
    ansible.builtin.service:
      name: postgresql
      state: started
```

Each task invokes a module to be executed on the target nodes. In the above playbook, three built-in Ansible modules are used: `ansible.builtin.yum` for the Yum package manager, `ansible.builtin.template` to specify configuration template for Apache server, and `ansible.builtin.service` used for managing system services on the database nodes.
## modules

To automate management of Linux and Windows systems, an Ansible Controller connects to managed nodes and transfers small units of code called modules. 

><span style="color:#668cff">Modules</span> are standalone, reusable units of code that perform specific actions on the controlled devices. Modules can manage system services, install packages, execute system commands, manipulate files and directories, interact with APIs and web services, run scripts and programs, and much more.   

- Ansible modules can be written in various programming languages, including Python, Ruby, Bash, Go, and others. Among these, Python is most commonly used.

Here is how a module is invoked and executed on managed devices when an Ansible command or playbook is run:

1. Module identification
	-  The Controller Node identifies the module required for the task defined in the playbook.

2. Module transfer
	 - The Controller transfers the code of the necessary module as a temporary file to the managed node over SSH or WinRM.

3. Execution and result retrieval
	- The managed node interprets and executes the module. After all the tasks are complete, the node sends results and diagnostics back to the Controller.

4. Cleanup
	- Ansible automatically deletes the temporary module files after execution, ensuring that nothing remains on the managed nodes.

Below are several examples of how modules can be used in Playbooks to perform different tasks.

---

- Managing services with `service`

```
- name: Restart docker service
  ansible.builtin.service:
    name: docker
    state: restarted
```

---

- Cloning a Git repository

```YAML
- name: Clone a Git repository
  git: 
    repo: https://github.com/user/repository.git
    dest: /path/to/repository
```

---

- Working with directories and files

```YAML
- name: Create the directory /etc/test if it does not exist and set permissions
  ansible.builtin.file:
    path: /etc/test
    state: directory
    mode: '0750'
```

---

- Copying files

```bash
- name: Copy a file to another directory, set an owner user, group, and permissions
  ansible.builtin.copy:
    src: /source/directory/file.txt
    dest: /destination/directory/file.txt
    owner: joe
    group: joegroup
    mode: '0755'
```

---

- Installing packages with `apt`

```YAML
- name: 'Install Nginx to version {{ nginx_version }} with apt module'
    ansible.builtin.apt:
      name: 'nginx={{ nginx_version }}'
      state: present
```

As seen in the above examples, modules can use Jinja2 syntax to reference variables. Values that incorporate variables need to be quoted for accurate interpretation.

---

- Using templates

```YAML
- name: Create Nginx configuration file based on the Jinja2 template
    ansible.builtin.template:
      src: templates/nginx.conf.j2
      dest: /etc/nginx/nginx.conf
```

The above task uses a Jinja2-formatted template file to configure an Nginx web server.

## templates, variables, and facts

Ansible utilizes two essential components for managing configurations: variables and templates.

In Ansible, configuration files can be generated dynamically during playbook execution using the standard Ansible module `ansible.builtin.template`. This module takes a Jinja2 template and processes it to create the appropriate configuration file based on the provided data.

><span style="color:#668cff">Templates</span> are files that define the structure and contents of configuration files or scripts. These files are written in Jinja2 format and have a `.j2` extension. They can contain placeholders for variables, which are replaced with actual values when the template is processed.

- Jinja2 employs the following syntax:

	- `{% %}` for control flow statements, such as loops and conditionals
	
	- `{{ }}` for expressions to output the values of variables
	
	- Filters can be used to modify the values of the variables; for example, `{{ variable | upper }}` converts a string to uppercase.

Templates are a key element of the automation of Ansible configuration management.
Multiple systems can be configured with one command: all the necessary configuration files can be generated from a single template, then each populated with its own data based on the supplied variables.

><span style="color:#668cff">Variables</span> are used to store configuration data that can be reused in playbooks and templates. They are typically defined in YAML format and consist of key-value pairs. Variables can be defined in various ways — at the playbook level, in the inventory, or through variable files.

In addition to user-defined variables, Ansible can automatically gather information about managed nodes, such as their OS version, hostname, IP address, and more. Such data is called facts.

>Facts are data collected from the managed nodes and returned to the Ansible Controller.

Below is an example of a simple Nginx web server configuration template. The template dynamically substitutes two variables with respective values from a dedicated file: `http_port` and `server_name`.

Template file: `templates/nginx.conf.j2`

```JS
server {
	listen {{ http_port }};
	server_name {{ server_name }};

	location / {
		proxy_pass http://localhost:5000;
	}
}
```

Variables: `group_vars/webservers.yaml`

```YAML
http_port: 80
server_name: "web.example.com"
```

Playbook: `deploy_nginx.yaml`

```YAML
- name: Nginx Configuration
  hosts: webservers
  tasks:
    - name: Install Nginx
      apt:
        name: nginx
        state: present
      become: yes
      
    - name: Generate Nginx configuration file
      template:
        src: templates/nginx.conf.j2
        dest: /etc/nginx/nginx.conf
      notify: Restart Nginx

  handlers:
    - name: Restart Nginx
      service:
        name: nginx
        state: restarted
```

- The `nginx.conf.j2` file is a template used to generate the Nginx configuration file. It uses Jinja2 syntax to include variables named `http_port` and `server_name`. These variables are defined in the variable file `group_vars/webservers.yaml`.

- The playbook, `deplpy_nginx.yaml`, runs on all servers in the `webservers` group within a configured inventory. The playbook ensures that Nginx is installed on each server and then generates the Nginx configuration file using the template. The notify directive triggers the defined `Restart Nginx` handler to restart Nginx, applying the new configuration.

>Ansible handlers are special tasks triggered by other tasks within a playbook. They are used to perform specific actions, such as restarting services, updating configurations, or executing custom scripts, in response to changes made by other tasks.
