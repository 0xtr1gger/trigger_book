---
created: 2024-10-27 03:51:22
tags:
  - terraform
---
The full process of creating an application setup can be divided in to two stages:
1. Infrastructure provisioning
2. Application deployment

Terraform automates the first step — infrastructure provisioning. It aids in automation of creating, managing, and changing infrastructure components.


![[terraform_mindmap.svg]]

## Terraform

>[Terraform](https://www.terraform.io/) is an IaC (Infrastructure as Code) tool for configuration, management, and provisioning automation of cloud and on-premises infrastructures using a declarative configuration language called HashiCorp Configuration Language (HCL) or JSON.

- Terraform is written in Go and created by [HashiCorp](https://www.hashicorp.com/).

Terraform has a vast array of advantages and capabilities that make it stand out from its competitors, such as Ansible and AWS CloudFormation. To name a few,

- IaC (Infrastructure as Code)
	- Terraform codifies infrastructure into human-readable configuration files (HCL) that can be version-controlled and reused.

- Open-source
	- Terraform is open-source software, which allows for community contributions, transparency, and peer review.

- Declarative
	- Terraform uses a declarative approach, meaning that users declare the desired state of the infrastructure in Terraform configuration, rather than the exact steps to achieve that state. It's the responsibility of Terraform to create a plan of actions to bring the infrastructure from the current state to the desired state.

- Infrastructure as Code
	- Terraform allows infrastructure definitions to be written and stored in version control systems, which facilitates collaboration, sharing, and rollback capabilities, as well as ensures consistent and reproducible environments. 
	
- Immutable infrastructure
	- Terraform promotes a model of immutable infrastructure, whereby existing resources are replaced instead of modified in place. This helps to minimize configuration drift and enhance system stability and reliability, as no untracked changes are introduced into infrastructure configuration. 

- Multi-cloud support
	- Terraform is vendor-agnostic and supports a wide cloud providers, such as AWS, Azure, GCP, as well as on-premises solutions. This multi-cloud capability not only provides flexibility but also enables organizations to avoid vendor lock-in and manage infrastructure across different platforms using a unified approach.

- Resource Graphs
	- Terraform automatically builds a dependency graph that visualizes the relationships and dependencies between infrastructure resources, which helps to ensure the correct order of operations during provisioning.

- State Management
	- Terraform maintains a state file that serves as a snapshot of the infrastructure, allowing it to track changes and avoid unnecessary updates. The state file is critical for Terraform to minimize resource duplication or conflicts.  

- Execution Plans
	- Before applying changes, Terraform generates an execution plan that shows what actions it will take to reach the desired state. This feature helps prevent unintended changes, fostering a clear understanding of upcoming modifications.
	
Use cases:

- Infrastructure creation
	- Automatically creating and configuring infrastructure components according to the declared configuration.
- Infrastructure management and modification 
	- Introducing changed to an existing infrastructure my modifying configuration.
- Infrastructure replication 
	- Terraform allows to version-control infrastructure definitions; it can be used to create exactly the identical infrastructure setups, i.e., replicating the setups. This is useful, for example, to reproduce production environment for testing purposes, or for scalability.


Example of infrastructure provisioning with AWS:
1. Allocating a private network space
2. Creating EC2 server instances
3. Installing Docker and other necessary tools on the server instances
4. Setting up security configuration
5. Deploying applications


## How Terraform works

- Terraform creates and manages resources on cloud platforms and other services using their APIs (Application Programming Interfaces). This allows Terraform to be able to work with virtually any cloud or on-premises solution with an accessible API.

Terraform architecture consists of two primary components:
- Terraform Core
- Providers

The Core is responsible for managing the infrastructure state, while Providers interact with external infrastructure services, such as AWS, Azure, or Google Cloud.

![[terraform_architecture.svg]]

#### Terraform Core

>Terraform Core is the central component of Terraform. It is a statically-compiled binary written in Go, responsible for managing the lifecycle of infrastructure resources. 

The Terraform Core works with two information sources:

1. User-defined configuration files written in HCL (HashiCorp Configuration Language) (`.tf`) - source input
	- define the desired state of the infrastructure
2. The state files (`.tfstate`) - state input
	- describe the current state of the infrastructure

The primary function of Terraform Core is to:

1. Compare the desired state of the infrastructure (source input - `.tf`), defined by a user in a HCL (or JSON) configuration file, with its current state (state input - `.tfstate).
2. Generate an execution plan, which details the necessary actions Terraform will to perform to bring the infrastructure to the desired state. This execution plan can be verified manually before applying the changes.
3. Execute the plan by creating, updating, or deleting the infrastructure resources as needed.

![[terraform_core.svg]]

>The Terraform Core provides a CLI (Command-Line Interface) for interacting with Terraform and the infrastructure. 
>Terraform CLI can be downloaded from the official [HashiCorp website](https://developer.hashicorp.com/terraform/install) as a zip archive. For installation, follow the [documentation](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli).

To interact with external components, such as cloud provides like AWS, GCP, Azure, or orchestration solutions like Kubernetes, the Terraform Core connects to Terraform Providers. 

#### Terraform Providers

>Terraform Providers are plugins that allow Terraform to interact with external infrastructure or services, including cloud providers, SaaS platforms, and other APIs.

Therefore, Providers handle the communication between Terraform Core and the services that provide infrastructure resources it manages.

- Each such provider is responsible for managing a specific set of resources. It translates requests from Terraform Core into API calls of the service it manages. 

- Providers are written in Go and communicate with the Terraform Core over a RPC (Remote Procedure Call) interface.

Terraform has over a 100 of providers for over 1000 resources. One of the most popular ones include:

- AWS (Amazon Web Services)
- Azure
- GCP (Google Cloud Platform)
- Kubernetes
- Datadog 
- Fastly
- etc.

Providers often require configuring authentication credentials to interact with the external system. 

![[terraform_providers.svg]]
#### The Workflow

The Terraform workflow consists of three primary steps:

1. Write 
	- Create a definition of the desired state of the infrastructure
2. Plan
	- Preview changes in the execution plan before applying
3. Apply
	- Provision reproducible infrastructure

---

Here is the full description of how a Terraform operates:

1. Configuration files
	- Users configure the desired state of the infrastructure, including infrastructure resources and configuration, in a HCL (or JSON) configuration file.
	- Terraform configuration files have the `.tf` extension. 

2. Directory initialization
	- In response to the `terraform init` command, Terraform initializes a working directory containing configuration files and sets up necessary backend for storing state files.
	- During this step, Terraform downloads necessary provider plugins.

```bash
terraform init
```

3. Generation of an Execution Plan
	- The `terraform plan` command tells Terraform to create an execution plan that details the actions the Core will take to reach the desired state defined in the configuration. To do that, Terraform compares the `.tfstate` state file that it is responsible of maintaining with the `.tf` configuration file describing the desired state of the infrastructure.
	- The plan can be manually reviewed and verified before any changes are introduced.

```bash
terraform plan
```

4. Applying the changes
	- The `terraform apply` command instructs Terraform to finally apply the changes. Terraform prompts the user configuration once more before the execution leaving an opportunity for a review and last-minute adjustments. 
	- To perform the proposed actions, Terraform makes API calls to the specified cloud providers to create, update, or delete resources as necessary. 
	- The state file is updated along the way of execution to reflect the changes made. 

```bash
terraform apply
```

---

5. Managing state
	- Terraform maintains a state file during the whole infrastructure lifecycle. The file holds the metadata about the infrastructure and used to track resources and their configuration. 
	- The state file can be stored either locally, or remotely on the cloud, such as in a S3 bucket. 

6. Modifying configuration
	- Any changes that need to be introduced into an existing configuration are first reflected in the `.tf` file. After declaring modifications, the same sequence of commands and actions is repeated in order to apply the changes: `terraform plan` => `terraform apply`.

---

7. Destroying resources
	- The `terraform destroy` command tears down all the resources defined in the configuraiton file when they are no longer needed.

```bash
terraform destroy
```


## Data sources

>A Terraform data source is a type of resource that enables Terraform to dynamically retrieve data from external sources, such as a cloud provider, a database, or another Terraform configuration. 

Data sources are commonly used to reference existing infrastructure, i.e., access resources that were not created by Terraform, such as AWS AMI or an existing AWS S3 bucket. This prevents Terraform from creating what already exists, but rather tells it to query the information elsewhere.

Data sources are defined using the `data` block and are queried at runtime when executing `terraform plan` and `terraform apply`. Here’s an example:

```JS
data "aws_instance" "example-data-source" {
  instance_id = "i-abc123"
}
```

It is important to know that Terraform does not modify any existing resources referenced with data sources, and neither it stores them in a state file, but only retrieves available data during the `plan` and `apply` phases. 

## Provisioners

>Provisioners in Terraform are used to execute scripts or other types of commands on a local or remote system after a resource is created or modified. Provisioners is the means of automation in Terraform that allows users to further setup or configure resources, such as installing software or running scripts.


## Terraform resources

In Terraform, a resource is a component that represents an infrastructure element, such as a virtual machine, database, network security group, or storage bucket. Resources are defined using a declarative syntax, specifying the desired state of the infrastructure.

A resource block describes one or more infrastructure objects, such as virtual machines, storage accounts, databases, networking components, etc.

A resource block is defined with the following syntax:

```JS
resource "<TYPE>" "<NAME>" {
  # Configuration arguments
}
```

- **Type**: The kind of resource you want to manage (e.g., `azurerm_virtual_machine`, `azurerm_resource_group`, etc.).
- **Name**: A unique name for the resource block within your configuration.

## Variables

>Terraform variables are used to parameterize infrastructure configuration making it more flexible and reusable.

Terraform variables can be broadly divided into three groups:
- Input variables
- Output variables
- Local variables

| Type   | Purpose                                           | Definition                      |
| ------ | ------------------------------------------------- | ------------------------------- |
| Input  | Parameterize configurations, making them reusable | Defined using `variable` blocks |
| Output | Return values from resources or configurations    | Defined using `output` blocks   |
| Local  | Create reusable expressions within a module       | Defined using `locals` blocks   |

#### Output variables

Output variables are used to extract and expose information about the resources created by Terraform configuration. They are especially useful for providing information to users after an apply operation or for chaining modules.

Output variables are defined using the `output` block in Terraform configuration (`.tf`), and typically defined in a separate `outputs.tf` file:

```JS
output "output_name" {
  value = expression // required
  description = "Description of the output" // optional
}
```

For example:

```JS
output "instance_ip" {
  value       = aws_instance.example.public_ip
  description = "The public IP address of the EC2 instance"
}
```

- After applying your Terraform configuration, outputs can be viewed in the command line output with the `terraform output` command:

```bash
terraform output instance_ip
```
  
  
  
- Outputs can be accessed by other configurations or modules that might need that information.

## Workspaces


- Workspaces are a way to create and manage multiple states within a single Terraform configuration directory. 

- Each workspace has a separate state file. For example, if using a local backend, `terraform.tfstate` might correspond to the `default` workspace, and `terraform.tfstate.d` might contain directories for other workspaces. 

- If not specified otherwise, all Terraform operations are performed within the `default` workspace, which is created automatically.

- Changes made in one workspace do not affect resources in another workspace.

- Environment variables can be managed separately across different namespaces. 

Workspaces come particularly useful in the situations where multiple versions of infrastructure need to be managed with the same configuration, such as development, testing, and production environments. Instead of duplicating the configuration, users can just reuse it, but track the states of different sets of resources. 

Terraform workspaces are managed with the `terraform workspace` command. It has several subcommands:

| Command  | Description                                                                                                                                                                                  |
| -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `delete` | Delete a workspace  (if and only if no resources are associated with that workspace; `-force` is used to enforce the deletion of the workspace along will all resources specified within it) |
| `list`   | List workspaces                                                                                                                                                                              |
| `new`    | Create a new workspace                                                                                                                                                                       |
| `select` | Select a workspace                                                                                                                                                                           |
| `show`   | Show the name of the current workspace                                                                                                                                                       |

- References to resources within a Terraform configuration file are implicitly associated with the current workspace. This means that Terraform will automatically manage any resources according to the workspace selected; if Terraform believes that `api_vm` resource exists in the `dev` workspace, it will forget about it in the `prod` workspace and create the VM anew when `terraform apply` is used.

>However, for complex environments with significantly different configurations or resource requirements, it might be more effective to manage Terraform configuration in entirely separate directories.


## Ansible vs. Terraform

#### Terraform Core

Terraform Core is the foundation of Terraform. It is responsible for the core functionalities that enable infrastructure definition, management, and lifecycle handling. Including:

- Configuration management
	- Terraform Core reads the configuration files, written in HashiCorp Configuration Language (HCL), that define the desired state of the infrastructure resources and configuration. 

- Execution plans 
	- The Core generates an execution plan that outlines what changes will be made to reach the desired state of the infrastructure from its current state. The plan provides a detailed overview of the actions Terraform is about to take, including creating, updating, or deleting resources.

- State Management
	- Terraform Core manages the state file. This file represents the current state of the infrastructure, which Terraform compares to the desired state to generate a plan based on the differences. 

- Graph Building
	- Terraform constructs a dependency graph of the resources defined in the configuration to visualize the desired state of the infrastructure and dependencies. This helps to figure out the correct order of operations from the current state to desired during infrastructure provisioning.

- Resource Lifecycle Management
	- The Core controls the lifecycle of resources, orchestrating the creation, updating, and deletion process as defined in the execution plan.

#### Providers

Terraform Providers are plugins that enable Terraform to interact with various third-party APIs and services.


- Providers defined the specific resource types that Terraform can manage, along with the necessary attributes and configurations.

- Providers often require specific configuration, such as access credentials or endpoints, for Providers to authenticate and interact with the respective services. 

- Each provider implements the lifecycle of the resources it manages, handling the specifics of how to create, read, update, and delete those resources according to the provider's API.



## configuration files

- Terraform configurations files are written in the HashiCorp Configuration Language (HCL) and used to describe the desired state of the infrastructure to the Terraform Core. 
- Terraform configuration files have the `.tf` extension.

The configuration file consists of blocks. The basic structure commonly includes:
- Terraform block
	- specifies the required providers
The basic structure of a Terraform configuration consists of several blocks


## Terraform configuration files


A Terraform configuration file, `.tf`, consists of code written in HashiCorp Configuration Language (HCL), which describes the desired state of the infrastructure. This includes defining providers, resources, variables, outputs, and possibly modules. 
Official documentation on the Terraform Language is available [here](https://developer.hashicorp.com/terraform/language).

- Each configuration file starts with a provider block, which specifies which cloud provider's resources are to be managed.

