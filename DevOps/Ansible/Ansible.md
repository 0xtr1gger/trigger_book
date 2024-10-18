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

- <span style="color:#668cff">Inventory</span> 
	- A list of managed nodes or hosts that Ansible configures and deploys. It's typically written in INI or YAML format and can include variables related to each host.

- <span style="color:#668cff">Playbooks</span>
	- YAML files that describe the automation process. Playbooks contain a set of instructions (plays) that defined tasks to be executed on managed nodes.

- <span style="color:#668cff">Modules</span>
	- Standalone, reusable units of code that perform specific actions on managed devices (e.g., managing services, installing packages, executing commands).

- <span style="color:#668cff">Templates</span>
	- Files that define the structure and content of configuration files or scripts that need to be generated dynamically. Ansible templates are written using the Jinja2 template language and have a `.j2` extension.

- <span style="color:#668cff">Variables</span>
	- Key-value pairs defined in YAML format used to store reusable configuration data that can be substituted into playbooks and templates.

## Inventory

Inventory files are where the nodes Ansible responsible to configure and automate are defined.

>An Ansible <span style="color:#668cff">Inventory</span> is a file that defines a list of logically grouped hosts that Ansible deploys and configures. 

- Inventory files are configured on the Ansible Controller. 
- An inventory file typically consists of a list of IP addresses or domain names of managed hosts organized into logical groups. The inventory may also include variables that provide further details about the managed devices.
- The default location for an Ansible inventory is `/etc/ansible/hosts`.

```bash
mkdir /etc/ansible && \
touch /etc/ansible/hosts
```

- An alternate location for an inventory can be specified at the command line using the `-i <path>` option, or in the Ansible configuration under the `inventory` directive.

- In order for an Ansible Controller to be able to manage nodes, only two things are required:
	- Network connectivity between the controller and the nodes
	- Proper SSH configuration

- Everything required for an Ansible Controller to manage and configure nodes is ability to connect to these nodes

- An inventory file can be written in either of two formats: INI or YAML. 

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

>YAML is strict about indentation. Even a slight deviation from the requirements makes a YAML file invalid.

- For this reason, the need to check YAML for validity becomes almost inevitable. There are many online tools that can help with this, to name a few:
	- [YAML Checker](https://yamlchecker.com/)
	- [YAML Lint](https://www.yamllint.com/)
	- [Online YAML Tools](https://onlineyamltools.com/validate-yaml)

An inventory can be either static or dynamic. Above are the examples of static inventories defined in text files; in contrast, dynamic inventory files are generated by scripts when a playbook is run.

- A dynamic inventory tracks hosts from one or more sources, such as cloud providers (AWS, Azure, GCP) or Configuration Management Database (CMDB) systems. This allows for real-time updates and management of inventory based on the current state of the infrastructure, rather than pre-defined static configuration.
## Playbooks

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

Playbooks are executed with the `ansible-playbook` command that takes an Ansible Playbook file as an argument:

```bash
ansible-playbook anisble_playbook.yaml
```

A custom inventory can be specified with the `-i` (`--inventory`) option:

```bash
ansible-playbook -i custom_inventory.ini anisble_playbook.yaml
```

To specify specify Ansible to display verbose debug output, the `-v` (`--verbose`) option is used:

```bash
ansible-playbook -v anisble_playbook.yaml
```

Ansible has a built-in way to check the playbook YAML syntax validity without actually running the playbook. This can be done using the `ansible-playbook` command with the `--syntax-check` option specified:

```bash
ansible-playbook --syntax-check ansible_playbook.yaml
```

## Modules

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

>Note: Jinja2 syntax can be used in playbooks in the same way as in templates. However, an important limitation is that loops and conditionals are not permitted in playbooks. It is impossible to create a loop of task. Ansible primarily uses declarative approach.

---

- Using templates

```YAML
- name: Create Nginx configuration file based on the Jinja2 template
    ansible.builtin.template:
      src: templates/nginx.conf.j2
      dest: /etc/nginx/nginx.conf
```

The above task uses a Jinja2-formatted template file to configure an Nginx web server.
## Templates, variables, and facts

Ansible utilizes two essential components for managing configurations: variables and templates.

In Ansible, configuration files can be generated dynamically during playbook execution using the standard Ansible module `ansible.builtin.template`. This module takes a Jinja2 template and processes it to create the appropriate configuration file based on the provided data.

><span style="color:#668cff">Templates</span> are files that define the structure and contents of configuration files or scripts. These files are written in Jinja2 format and have a `.j2` extension. They can contain placeholders for variables, which are replaced with actual values when the template is processed.

- Jinja2 employs the following syntax:

	- `{% %}` for control flow statements, such as loops and conditionals
	
	- `{{ }}` for expressions to output the values of variables
	
	- Filters can be used to modify the values of the variables; for example, `{{ variable | upper }}` converts a string to uppercase.

Templates are a key element of the automation of Ansible configuration management. Multiple systems can be configured with one command: all the necessary configuration files can be generated from a single template, then each populated with its own data based on the supplied variables.

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
      include_vars: group_vars/webservers.yaml
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


- The playbook runs on all servers in the `webservers` group within a configured inventory.  The playbook first ensures that Nginx is installed on each server and then creates the configuration file from the specified template.

- The `nginx.conf.j2` file is a template used to generate the Nginx configuration file and store it as `/etc/nginx/nginx.conf` inside each host from the `webservers` group. The template uses Jinja2 syntax to define placeholders for variables `http_port` and `server_name`, which are dynamically substituted when the playbook runs. These variables are defined in the `group_vars/webservers.yaml` file and specified in the playbook using the `include_vars` directive.

- The `notify` directive is used to trigger the `Restart Nginx` handler to that restarts Nginx, applying the new configuration.

>Ansible handlers are special tasks triggered by other tasks within a playbook. They are used to perform specific actions, such as restarting services, updating configurations, or executing custom scripts, in response to changes made by other tasks.

#### Playbook variables

Similar to templates, variables and facts can also be used inside playbooks. For example, below is a task used to install a package those name is stored in the `package_name` variable with the default value being `zlib`:

```YAML
- name: Install a package
  package:
    name: "{{ package_name|default('zlib') }}"
```
  
## Vault

Ansible Vault is a feature that provides a way to securely store and manage sensitive data, such passwords, API keys, and other confidential information, within Ansible projects. 

Ansible Vault is used for various operations, including:

- Encrypting and decrypting files
- Viewing an encrypted file without breaking the encryption
- Creating or editing an encrypted file
- Generating or resetting an encryption key

To work with Ansible Vault, the `ansible-vault` command can be used. 

- `ansible-vault create` is used to create Ansible Vaults. 	
	- For example, to create an encrypted YAML file `vault.yaml` to store sensitive variables:

```bash
ansible-vault create vault.yaml
```
```
New Vault password: 
Confirm New Vault password:
```

This command prompts for a password which will be used to encrypt the file. After the password is created, Ansible opens an editor that can be used to enter information to be stored in the vault. Once the editor is closed, Ansible encrypts the file. 

```bash
# vault.yaml
Sensitive
```

An attempt to display the file content not providing an encryption key will result in a meaningless string of symbols following header information that Ansible uses to handle the file. From the header it is evident that Ansible uses AES-256 symmetric encryption algorithm.

```bash
cat vault.yaml
```
```
$ANSIBLE_VAULT;1.1;AES256
65663133303830633363356564313234613133636261313761376366393234636361306664313364
3133326565326536663931333931316366353464373535330a623236393366663632313531383766
31653732666531643733346166343532313333373964356664373933326565383762386238363037
3634626437323863640a393861303931383566376139666636656430666339306236383164353634
3238

```

---

- `ansible-vault encrypt` is used to encrypt existing files.
	- For example, to encrypt a text file `sensitive.txt`:

```bash
ansible-vault encrypt sensitive.txt
```

Similarly, Ansible will prompt for a password.

---

- `ansible-vault view` is used to display decrypted file content provided a valid password.

```bash
ansible-vault view vault.yaml
```

The program asks for password and outputs the file in cleartext right after a password prompt and a new line. 

```
Vault password:

Sensitive
```

The `cat` command, however, will still result in meaningless data:

```bash
cat vault.yaml
```
```
$ANSIBLE_VAULT;1.1;AES256
65663133303830633363356564313234613133636261313761376366393234636361306664313364
3133326565326536663931333931316366353464373535330a623236393366663632313531383766
31653732666531643733346166343532313333373964356664373933326565383762386238363037
3634626437323863640a393861303931383566376139666636656430666339306236383164353634
3238
```

Therefore, `ansible-vault view` is the only way to display files encrypted by Ansible Vault - all other commands and utilities will display cyphertext.


---

- `ansible-vault decrypt` is used to permanently decrypt a file

```bash
ansible-vault decrypt sensistive.txt
```

---

To actually use encrypted files with Ansible, the `--ask-vault-pass` option to `ansible` or `ansible-playbook` commands is added.

To example, to copy the contents of a vault-encrypted file to a host,

```bash
ansible --ask-vault-pass -bK -m copy -a 'src=sensitive.txt dest=/tmp/sensistive.txt mode=0600 owner=root group=root' webservers
```

This command copies the encrypted file, to the `/tmp` directory inside all hosts under the `webservers` group, change permissions to `0600` and sets ownership to `root`. 
The command will prompt for the password.

Another way is to use password files. This avoids the need to enter the password manually each time a command or playbook is run:

```bash
echo 'ansible_vault_password' > .vault_pass
```

- Don't forget to add the file to `.gitignore` when using Git. 

Then, the password file can be specified with the `--vault-password-file` option to the `ansible` or `anisble-playbook` command:

```bash
ansible-playbook --vault-password-file .vault_pass playbook.yaml
```

Another way is to add the password file name to the `ANSIBLE_VAUlT_PASSWORD_FILE`. In this case, the file will be set automatically on each `ansible` or `ansible-playbook` command:

```bash
export ANSIBLE_VAULT_PASSWORD_FILE=./.vault_pass
```

Or even specify the file in Ansible configuration, `ansible.cfg`:

```
[defaults]
. . .
vault_password_file = ./.vault_pass
```
## Ansible Galaxy

>[Ansible Galaxy](https://galaxy.ansible.com) is a platform for discovering, installing, and managing Ansible roles and collections. It provides a centralized location for users to find and share reusable Ansible content, making it easier to automate infrastructure and applications.

Ansible roles is how Ansible configuration files, such as playbooks, templates, variables, are grouped and organized. Ansible collections is how roles are packed and distributed.

>An Ansible role is a self-contained, portable unit of Ansible automation that groups related tasks, variables, files, handlers, and other assets in a standardized file structure.

- Ansible roles are portable: they can easily be moved between different systems.
- Roles can be easily reused across multiple playbooks and environments.
- Each role includes all components necessary for Ansible execution (e.g., playbooks, templates, variables) making it easy to manage and maintain.
- Roles follow a consistent directory structure, simplifying and standardizing Ansible configuration.

>An Ansible Collection is a distribution format for Ansible content, including playbooks, roles, modules, and plugins. Collections provide a way to package and distribute Ansible content, making it easier to manage and share complex automation workflows.

- Roles are typically managed locally, while Collections are distributed through Ansible Galaxy.

The `ansible-galaxy` command provides various sub-commands for managing roles and collections:

The `ansible-galaxy` command is used to manage Ansible roles and collections. 

- To manage roles:

```bahs
ansible-galaxy role <subcommand>
```

| sub-command | description                                               |
| ----------- | --------------------------------------------------------- |
| `install`   | Install a role.                                           |
| `remove`    | Remove one or more roles.                                 |
| `list`      | Display the name and the version of installed roles.      |
| `info`      | Display information about a role.                         |
| `init`      | Generate a skeleton of a new role.                        |
| `import`    | Import a role from the galaxy web site. Requires a login. |
- To manage collections:

```bash
ansible-galaxy collection <subcommand>
```

| sub-command | description                                                |
| ----------- | ---------------------------------------------------------- |
| `init`      | Generate a skeleton of a new collection.                   |
| `install`   | Install a collection.                                      |
| `list`      | Display the name and the version of installed collections. |
