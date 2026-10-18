---
created: 2024-11-01 05:45:36
---
```
kd218H01010
```

## `backend.tf`: configuring the backend

After the existing Storage Account has been imported to the Terraform state file, it's time to configure a remote backend for the resources declared in the static website configuration. Return to the `terraform` directory in the project repository. 

It's a good practice to organize Terraform configuration into separate files based on their purpose. Thus, we create a file called `backend.tf`. 

Here, we will declare a remote backend in the `terraform-state` container created in the previous section to be used for the Terraform state:

```Python
# backend.tf
terraform {
  backend "azurerm" {
    resource_group_name  = "rg-cloud-resume-example"
    storage_account_name  = "<here-is-your-storage-account-name>"
    container_name        = "terraform-state"
    key                   = "terraform.tfstate"
  }
}
```


- Add explanations

- It is important to note that all the values of backend attributes are defined with hardcoded string values. The reason behind this is that backend definitions just does not support dynamic or interpolated values, including outputs from other resources. This is because the backed must be specified with static values that do not change during deployment. 
#### applying configuration

If we run the `terraform plan` command, Terraform will tell that it has no changes to be applied. This is because it moves the state file to the cloud during the `terraform init` command, and then, on each `terraform plan` or `apply` command, connects to it to retrieve the state. We changes nothing except moved the backend, thus the state in the blob storage remains unchanged. 

```
I have a question. 

As you see, I try to comlpete a Cloud Resume Challenge in DevOps mode in Azure. I coped with the first step, deploying a static website in the frist place, and used Terraform for this. It works as expected. 

The next thing I want to do is to load my website and terraform configuraiton to GitHub and use GitHub actions to automate CI/CD.

I will need the following:

- Create a remote backend for terraform state file, tfstate, and upload it to another container in by storage account in Azure. 
- load my code to a GitHub repo
- configure Access Keys in GitHub secrets
- create a GitHub Actions workflow to update the contents of the Blob, index.html, when the source code of the index.html changes

however, my resume contains some sensitive information that i do not want to share publicly. this includes my phone number, email address, etc. so, I do not want to expose my HTML or link to the blob by any means, but still hold my configuration in GitHub as a portfolio project. I plan to only give the link to my CV to my potential employers or specify it in LinkedIn or JustJoinIT.
But my GitHub Actions workflow should nevertheless me able to update the contents of the blob when the index.html in my repo changes. 

is there a way to hide this information from the public, but keeping the project source code open and GitHub Actions working properly?
```

# drafts

## GitHub Actions

## Backend configuration


In the backend, you should specify all necessary authentication credentials for Terraform to be able to query Azure API automatically, independently of your terminal. `<storage_account_name>` is your Azure storage account name created with `state/main.ft`. 

>you can not use traditional Terraform variables in `backend` configuration blocks. 

However, fortunately, it is possible to use environment variables, which Terraform documentation [recommends](https://developer.hashicorp.com/terraform/language/backend#credentials-and-sensitive-data), instead of hard-coding credentials to the backend.

using environment variables instead of hard-coding credentials to the backend - and that's for good. 

Here is how the `backend` block looks like with environment variables:


## Imports

The `terraform import` command is used to import existing infrastructure resources into the Terraform state. 

It takes two arguments:

1. Terraform resource address
	- Terraform addresses have the following format: `resource_type.resource_name`
	- For example, `azurerm_storage_account.blob_storage`

2. The corresponding identifier from the provider's API

	- The format of an identifier varies across different providers, and can be obtained using a CLI or web interface of that provider. 

	- In Azure, for example, a Storage Account identifier looks like this: `/subscriptions/{subscription-id}/resourceGroups/{resource-group-name}/providers/Microsoft.Storage/storageAccounts/{storage-account-name}`. It is displayed, along with other attributes of the Account, in an output of the `az storage account show --name {storage-account-name}` command.
⤬ ⤬ ⤬ ⤬ ⤬ ⤬ ⤬ ⤬ ⤬ ⤬ ⤬ ⤬ ⤬ ⤬ ⤬ ⤬ ⤬ ⤬ ⤬ ⤬ ⤬ ⤬ ⤬ ⤬ ⤬ ⤬ ⤬ ⤬ ⤬ ⤬ ⤬ ⤬ ⤬ ⤬ ⤬ ⤬ ⤬

- The type of replication used for this storage account. 
- Later on, we will define the `var.storage_account_replication_type` and assign `LRS` as the default. LRS (Locally Redundant Storage) is a replication strategy with which Azure keeps multiple copies of data within a single data center. There are other replication strategies as well. 
- Azure defines several Tiers for storage accounts, with the Standard General Purpose v2 (GPv2) Storage Account being the most popular, as it supports all storage services and suitable for most applications. 
## Azure provider

3. The Azure provider

We initiate our configuration with the following blocks:

```Python
terraform {
  required_version = ">=1.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}
```

- The `terraform` block is used to define provider-specific configuration. 
	- `required_version` 
		- The minimum Terraform version required for the project. 
	- `required_providers` 
		- The providers that this Terraform module makes use of.

- `azurerm` block configures the Azure Terraform provider
	- `source`
		- The source from which Terraform can download the provider plugin.
	- `version` 
		- The version of the provider the project requires.  

- The `provider` block can be used to further configure `azurerm`.

>The `required_providers` and `provider` blocks are typically defined on the root module level. 

## Azure CLI installation

>Azure offers its own proprietary service called [ARM (Azure Resource Manager)](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/overview "null") for implementing IaC. However, it is primary designed to be used with Azure, and to manage other cloud resources with it, say, AWS, additional setup is required. Conversely, Terraform is open-source and has robust community support, making it the preferred IaC tool across many industries.
#### Debian/Ubuntu

On Debian-based distributions, including Ubuntu and Debian, Terraform can be installed from the official HashiCorp package repository (which first needs to be added).

4. Ensure necessary packages are installed

```bash
sudo apt-get update && sudo apt-get install -y gnupg software-properties-common
```

5. Install the HashiCorp [GPG key](https://apt.releases.hashicorp.com/gpg "HashiCorp GPG key"):

```bash
wget -O- https://apt.releases.hashicorp.com/gpg | \
gpg --dearmor | \
sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg > /dev/null
```

6. Verify the key's fingerprint:

```bash
gpg --no-default-keyring \
--keyring /usr/share/keyrings/hashicorp-archive-keyring.gpg \
--fingerprint
```

7. Add the HashiCorp repository:

```bash
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] \
https://apt.releases.hashicorp.com $(lsb_release -cs) main" | \
sudo tee /etc/apt/sources.list.d/hashicorp.list
```

8. Install Terraform:

```bash
sudo apt update && sudo apt-get install terraform
```

9. Verify the installation

```bash
terraform --version
```
#### Arch-based distributions



Finally, the module seems to be finished. It is stand-alone and reusable, therefore in order to verify and make use of it, we need to create a separate project that will call the newly created module as a child module.

---

- For example, the following module specifies the `region` input variable, overwriting its default value, if it was defined in the child:

```Python
module "servers" {
	source = "./azure-vm-module"
	region = "us-east-1"
	# other input variables
	# ...
}
```

# docs


List any prerequisites or dependencies needed to use the module, such as required providers, Terraform version, or any other external tools or configurations:

```Markdown
## Requirements

- Terraform version 1.0 or higher
- AzureRM Provider version 3.0 or higher
- An Azure account and subscription with permissions sufficient to create the necessare resources  
- Azure CLI used to authenticate to Azure
```

Then document all input variables, including their names, types, descriptions, and default values (if given). This section should serve as an explanation of how users can customize the behavior of this module.

Here is the inputs part for my module:

```markdown
## Inputs 

| Variable                           | Type   | Default             | Description                                            |
| ---------------------------------- | ------ | ------------------- | ------------------------------------------------------ |
| `storage_account_name`             | string |                     | The unique name for the Azure Storage Account.         |
| `resource_group_name`              | string | `rg-static-website` | The name of the Azure resource group to create.        |
| `rg_location`                      | string | `East US`           | The Azure region to deploy the resources.              |
| `storage_account_tier`             | string | `Standard`          | The tier for the Azure storage account.                |
| `storage_account_replication_type` | string | `LRS`               | The replication type for the storage account.          |
| `index_document`                   | string | `index.html`        | The name of the index document for the static website. |
| `error_document`                   | string | `404.html`          | The name of the error document for the static website. |
| `styles`                           | string | `styles.css`        | The name of the CSS file for the website.              |
| `storage_container_name`           | string | `web`               | The name of the Azure Blob storage container.          |

Required input variables:
- `storage_account_name`
```

## Inputs 


Required input variables:
- `storage_account_name`

After that, add usage examples that include complete configuration to demonstrate how to properly call and use the module. 

```
## Example

\```hcl
module "static_website" {
  source               = "./modules/static-website"
  storage_account_name = "unique_storage_account_name"
  resource_group_name  = "custom-resource-group"
  rg_location          = "West US"
}
\```

```

# variables

Terraform variables allow users to parameterize Terraform configurations, making the infrastructure code more flexible and reusable. 

>Variables in Terraform are named values that can be referenced and utilized in infrastructure configuration files. Depending on the type, variables allow users to define dynamic inputs to Terraform modules and resources or display infrastructure configuration details in the output of Terraform `apply` operations.  

There are three main types of variables in Terraform:

- Input variables
- Output variables
- Local variables

| Type   | Purpose                                           | Definition                      |
| ------ | ------------------------------------------------- | ------------------------------- |
| Input  | Parameterize configurations, making them reusable | Defined using `variable` blocks |
| Output | Return values from resources or configurations    | Defined using `output` blocks   |
| Local  | Create reusable expressions within a module       | Defined using `locals` blocks   |


## Input variables


Each variable declaration consists of:

- Name (required)
	- A unique name for the variable.

- Type (optional) 
	- The data type of the variable.

- Description (optional)
	- Description of the variable. 
	- Also used to generate documentation for the module.

- Default value (optional)
	- An optional default value that will be used if no value is provided.

Supported data types are as follows:

- `string`
	- A sequence of characters, can be defined with double quotes. 
	- Single quotes can be used as well, but interpolation won't work with them. 

```Python
# variable
variable "instance_name" {
	type        = string
	description = "The name for the Azure VM instance"
	default     = "API-VM-instance"
}

# usage
resource "azurerm_resource_group" "example" {
  name     = var.resource_group_name
  # ...
}
```

- `number`

```Python
# variable
variable "vm_count" {
  description = "Number of virtual machines to create"
  type        = number
  default     = 1
}

# usage
resource "azurerm_linux_virtual_machine" "example" {
  count               = var.vm_count
  # ...
}
```

- `bool` (`true`/`false`)

```Python
# varuable
variable "enable_diagnostics" {
  description = "Enable or disable diagnostics for the VM"
  type        = bool
  default     = true
}

# usage
resource "azurerm_linux_virtual_machine" "example" {
  # ...
  provision_vm_agent = var.enable_diagnostics
  # ...
}
```

- `list`
	- A list can hold multiple other variables, but only of the *same* type.

```Python
# variable
variable "vm_tags" {
  description = "A list of tags to assign to the VM"
  type        = list(string)
  default     = ["environment=dev", "team=devops"]
}

# usage
resource "azurerm_linux_virtual_machine" "example" {
  # ...
  tags = toset(var.vm_tags)
  # ..
}
```

- `map`
	- A collection of key-value pairs.

```Python
# variable
variable "vm_labels" {
  description = "Map of labels for the VM"
  type        = map(string)
  default     = {
    environment = "development"
    owner       = "devops-team"
  }
}

# usage 
resource "azurerm_linux_virtual_machine" "example" {
  # ...
  tags = var.vm_labels
  # ...
}
```


- `object`
	- An object allows users to define complex data structures with specific attributes. This is useful for configurations with multiple properties.

```Python
# variable
variable "vm_configuration" {
  description = "Configuration settings for the virtual machine"
  type = object({
    admin_username = string
    admin_password = string
    size           = string
  })
  default = {
    admin_username = "adminuser"
    admin_password = "P@ssword123!"
    size           = "Standard_DS2_v2"
  }
}

# usage
resource "azurerm_linux_virtual_machine" "example" {
  # ...
  admin_username = var.vm_configuration.admin_username
  admin_password = var.vm_configuration.admin_password
  size           = var.vm_configuration.size
}
```

- `any`
	- The `any` type allows a variable to accept any type of value but should be used sparingly. Its purpose is to provide flexibility at the risk of losing type-checking.

```Python
# variable
variable "unknown_type" {
  description = "This variable can be of any type"
  type        = any
}

# usage
resource "azurerm_resource_group" "example" {
  name     = var.unknown_type
  location = "eastus"
}
```

Input variables also support validation rules and can be sensitive. 




# configuration components

- Providers
	- define the cloud provider or service (e.g., AWS, Azure, Google Cloud) that Terraform will interact with

```JS
terraform {
	required_providers {
		aws = {
			source = "hashicorp/aws"
			version = "~> 3.0"
		}
	}
}

provider "aws" {
	region = "us-west-2"
}

```


- Resources
	- specify the infrastructure resources to be created (e.g., EC2 instances, S3 buckets)

```JS
resource "aws_instance" "example" {
	ami = "ami-12345678"
	instance_type = "t2.micro"
}
```

- Data sources
	- Retrieve information from existing resources outside of Terraform management, which can be useful for creating dependencies.

```bash
data "aws_ami" "latest" {
	most_recent = trye
	owners = ["123456789012"]
}
```


- Variables
	- Allow parameterization of configurations, making them more flexible and reusable.

```JS
variable "instance_type" {
  description = "Type of EC2 instance to create"
  type        = string
  default     = "t2.micro"
}
```


- Outputs
	- Extract information from resources created by Terraform, making it accessible after the apply phase.

```JS
output "instance_ip" {
  value = aws_instance.example.public_ip
}
```

- Locals
	- Define reusable values within a configuration, serving as intermediate calculations or constants.

```JS
locals {
  region         = "us-west-2"
  instance_count = 3
}
```

- Modules
	- Organize and encapsulate reusable configurations into self-contained packages.

```JS
module "network" {
  source = "./modules/network"
  vpc_id = aws_vpc.main.id
}
```


# lab local

## Installing Terraform

Terraform is available as a package in many distributions, including Debian, Arch, and RPM-based distributions.

- [Documentation: Install Terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)

---

For Debian-based distributions, including Ubuntu and Debian:

10. Ensure necessary packages are installed

```bash
sudo apt-get update && sudo apt-get install -y gnupg software-properties-common
```

11. Install the HashiCorp [GPG key](https://apt.releases.hashicorp.com/gpg "HashiCorp GPG key"):

```bash
wget -O- https://apt.releases.hashicorp.com/gpg | \
gpg --dearmor | \
sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg > /dev/null
```

12. Verify the key's fingerprint

```bash
gpg --no-default-keyring \
--keyring /usr/share/keyrings/hashicorp-archive-keyring.gpg \
--fingerprint
```

13. Add the official HashiCorp repository to the system:

```bash
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] \
https://apt.releases.hashicorp.com $(lsb_release -cs) main" | \
sudo tee /etc/apt/sources.list.d/hashicorp.list
```

14. Install Terraform from the new repository

```bash
sudo apt update && \
sudo apt-get install terraform
```

15. Verify the installation

```bash
terraform --version
```

---

For Arch-based distributions, including Manjaro and Arch Linux:

16. Install Terraform as a Pacman package

```bash
sudo pacman -S terraform
```

17. Verify the installation

```bash
terraform --version
```
## Local providers

The Local provider is used to manage local resources, such as files.

>Local providers are used to interact with local utilities, such as generating random numbers for unique resource names. There are no specific “types” of local providers, as they are simply plugins that provide resources.

A local provider is a plugin for Terraform that facilitates the interaction with local resources, which could include:

- Local file systems
- Local execution of commands
- Docker containers
- Virtual machines
- Any specific resource or tool that you wish to manage on your local machine

Some common use cases for local providers include:

- Testing Terraform configurations without impacting production systems
- Managing development environments
- Running or orchestrating local applications
- Creating local development setups that mimic production environments

- [`hashicorp/local`](https://registry.terraform.io/providers/hashicorp/local/latest)
	- [docs](https://github.com/hashicorp/terraform-provider-local/tree/main/docs)
	- The `local` provider allows for managing local resources, including

		- Local files: creating, managing, and deleting files on the local system.
		- Local exec and null resources: executing local scripts or commands

`
```JS
resource "local_file" "example" {
  content  = "Hello, Terraform!"
  filename = "${path.private}/hello.txt"
}
```

```JS
resource "null_resource" "example" {
  provisioner "local-exec" {
    command = "echo 'Provisioning finish'"
  }
}
```

- `hashicorp/docker`

	- The `docker` provider allows for managing Docker containers, volumes, images, and networks, on a local machine or a remote Docker host.
		- `docker_container`: create and manage Docker containers
		- `docker_image`: manage Docker containers
		- `docker_volume`: manage Docker volumes for persistent data

```JS
resource "docker_image" "nginx" {
  name = "nginx:latest"
}

resource "docker_container" "nginx" {
  image = docker_image.nginx.latest
  name  = "my_nginx"
  ports {
    internal = 80
    external = 8080
  }
}
```


- `terra-farm/virtualbox`
	- The VirtualBox provider for managing VirtualBox virtual machines using Terraform.
		- `virtualbox_vm`: create and manage VirtualBox VMs

```JS
resource "virtualbox_vm" "my_vm" {
  name      = "test-vm"
  image     = "ubuntu"
  cpus      = 2
  memory    = 1024
  network_interface {
    adapter = "hostonly"
  }
}
```


It is also possible to create a custom Terraform provider using a [Terraform Plugin SDK](https://github.com/hashicorp/terraform-plugin-sdk "null"). Terraform providers are written in Go.
#### Working with `local` provider

18. Create a directory `project_run`
19. Create a file named `main.tf`

```JS
resource "local_file" "first_local_file" {
    content  = "The wind is getting stronger."
    filename = "/tmp/the_wind.txt"
}
```

20. Initialize resources

```bash
terraform init
```

![[terraform_init.png]]

21. Create an execution plan

```bash
terraform plan -out=terraform_plan
```

![[terraform_plan.png]]

- The `-out` option tells Terraform to save the plan to a file.

22. Apply the configuration

```bash
terraform apply terraform_plan
```

![[terraform_apply.png]]

23. Verify the file has been created

```bash
ls /tmp | grep wind
```

```bash
cat /tmp/the_wind.txt
```

![[verify.png]]


```
│──────────────────────────────────────────────────│
│ Here is where the title goes         ✏ [edit]   │
│ Status: PROGRESS                     ⤫ [delete] │  
│ Deadline: xx-xx-xxxx xx:xx x.m.                  │ 
│──────────────────────────────────────────────────│
```


# IaC

Any application environment requires many infrastructure components, including operating systems, database systems, application servers, etc. At scale, manual infrastructure management is a time-consuming and error-prone. Infrastructure as Code is an approach that aims to automate and simplify this process.  

>IaC (Infrastructure as Code) is a practice that allows development teams to manage and provision infrastructure automatically, through code, rather than manually.

IaC automates the deployment and management of infrastructure. It Ensures consistent development, testing, and production environment, and minimizes configuration drift. IaC also facilitates scalability, and helps to optimize resource utilization. 


- IaC is used for infrastructure automation to ensure consistency across development, testing, and production environments. 


Key characteristics:


- Automation
	- IaC automates the deployment and management of infrastructure. This reduces manual efforts, speeding up the process of getting applications into production.

- Configuration management automation
	- IaC minimizes configuration drift by automating infrastructure configuration process and eliminating human errors. It allows to roll back the changes any time thanks for the use of version control systems. 
	- Tools like Ansible, Chef, and Puppet are used to define infrastructure components, such as servers and application, and automate their configuraiton based of the defined state.

- Provisioning automation
	- Provisioning tools automate managing the creation aand management of infrastructure components such as servers, network, and storage. Examples include Terraform and AWS CloudFormation. 

- Consistency
	- Configuration management automation helps to ensure consistent environment across development, testing, and production.

- Version control
	- In IaC, infrastructure definitions and configuration are treated as code and stored in a version control system, such as Git. This allows teams to track changes, collaborate, and roll back to previous configurations if needed.


Key benefits that IaC brings to the DevOps culture include:

- Minimizing automation drift
	- IaC minimizes configuration drift by automating infrastructure configuration process and eliminating human errors. It allows to roll back the changes any time thanks for the use of version control systems, 


''
- IaC is an important part of implementing [Continuous Integration/Continuous Delivery (CI/CD)].  CI/CD relies on ongoing automation and continuous monitoring throughout the application life cycle, from integration and testing to delivery and deployment. In order for an environment to be automated, it needs to be consistent; and this is exactly what IaC approach strives to achieve.

## Declarative vs. Imperative

There are two approach to infrastructure as code: declarative and imperative.

- Declarative approach: *what* to achieve
	- A declarative approach defines the end state of the system, including all the required resources and properties. This approach focuses on the definition of the desired configuration, rather than the exact steps and operations on how to achieve it.
	- Declarative IaC tools, such as Terraform, process the defined configuration and automatically bring the system to the specified state. 

- Imperative approach: *how* to achieve
	- An Imperative approach defines the exact steps, specific commands that the system should go through in order, to achieve the desired configuration. 
	- Imperative approach is used in scripting languages like Bash, Ruby, and Python, and can also be used in such tools like Ansible, Puppet, Chef, and Terraform.
## Push vs. Pull