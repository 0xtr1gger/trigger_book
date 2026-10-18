---
created: 2025-04-12
---


## How Terraform works

- Terraform creates and manages resources on cloud platforms and other services using their APIs (Application Programming Interfaces). This allows Terraform to be able to work with virtually any cloud or on-premises solution with an accessible API.

Terraform architecture consists of two primary components:
- Terraform Core
- Providers

The Core is responsible for managing the infrastructure state, while Providers interact with external infrastructure services, such as AWS, Azure, or Google Cloud.


### Terraform Code

>**Terraform Core** is the central component of Terraform, a statically-compiled binary written in Go, responsible for generating execution plans based on user-defined configuration and the current state of the infrastructure.

The Terraform Core works with two input sources:

1. User-defined configuration files written in HCL (HashiCorp Configuration Language)
	- Defines the desired state of the infrastructure.

2. Terraform state file (`terraform.tfstate`)
	- Describe the current state of the infrastructure.

Terraform core workflow consists of several main steps:
1. Compare the desired state of the infrastructure, defined in HCL configuration files, with the current state (`terraform.tfstate`).
2. Generate an execution plan, which details the necessary actions Terraform will to perform to bring the infrastructure to the desired state.
3. Execute the plan by creating, updating, or deleting the infrastructure resources as needed.

![[terraform_core.svg]]

>The Terraform Core provides a CLI (Command-Line Interface) for interacting with Terraform and the infrastructure. 
>Terraform CLI can be downloaded from the official [HashiCorp website](https://developer.hashicorp.com/terraform/install) as a zip archive. For installation, follow the [documentation](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli).

To manage cloud resources, Terraform Core relies on Terraform Providers.
### Terraform Providers

>Terraform Providers are plugins that allow Terraform to interact with cloud platforms to create, update, or delete infrastructure resources using their APIs (Application Programming Interfaces).

Simply put, Terraform Providers handle the communication between Terraform Core and the services that provide infrastructure resources it manages.

With over a hundred providers, each designed for a specific platform or technology, Terraform enables users to orchestrate infrastructure across multiple cloud providers and technologies seamlessly.


The extensive library of providers grants access to a wide array of resources and functionality, such as provisioning AWS EC2 instances or managing Kubernetes resources, like services, deployments, and namespaces.

Here are some popular cloud providers:

- [`azurerm`](https://registry.terraform.io/providers/hashicorp/azurerm/latest)
	- Manages Microsoft Azure cloud resources, such as Azure VMs, Blob storage, and Kubernetes clusters, using the Azure Resource Manager (ARM) APIs.
- [`aws`](https://registry.terraform.io/providers/hashicorp/aws/latest)
	- Manages AWS cloud resources, such as EC2 instances, Lambda, EKS, ECS, S3 buckets, and other.
- [`google`](https://registry.terraform.io/providers/hashicorp/google/latest)
	- Manages GCP cloud resources, like Compute Engine, Cloud Storage, Cloud Functions, etc.
- [`kubernetes`](https://registry.terraform.io/providers/hashicorp/kubernetes/latest)
	- Manages Kubernetes resources, including Deployments, Services, Custom Resources (CRs and CRDs), Policies, Quotas and more.
- etc.

>Each Provider is responsible for managing a specific set of resources. It translates requests from Terraform Core into respective API calls to cloud services.

## Terraform concepts

### Resources

>**Resources** represent infrastructure objects. They define the desired state and parameters of infrastructure components for Terraform to provision. 

```Python
resource "aws_route53_record" "dev" {
  zone_id  = data.aws_route53_zone.this[0].zone_id
  name     = "www-dev-concept-example"
  type     = "CNAME"
  ttl      = "300"
  records  = [data.aws_cloudfront_distribution.dev.domain_name]
}
```
### Data sources

>**Data sources** act as read-only representations of already existing cloud resources; they are designed to retrieve necessary information about those resources required for creating other resources.

- Terraform never creates, deletes, or otherwise modifies resources represented by data sources.   
- Data sources are often used to provide parameters for other resources Terraform provisions. 

```Python
data "aws_cloudfront_distribution" "dev" {
  id       = var.cloudfront_id
}

resource "aws_route53_record" "dev" {
  zone_id  = data.aws_route53_zone.this[0].zone_id
  name     = "www-dev-concept-example"
  type     = "CNAME"
  ttl      = "300"
  records  = [data.aws_cloudfront_distribution.dev.domain_name]
}
```

### Backends

>A **state file** contains information about the resources created within a specific project. Its main purpose is to offer existing information for communication with Terraform when modifications are made.

State files are stored in JSON format and contain sensitive information, including cloud authentication credentials, necessary to provision resources.

>Terraform manages the location of its state file with **backends**.

```Python
backend "s3" {
  region         = "INPUT-REGION"
  acl            = "private"
  profile        = "INPUT-PROFILE-NAME"
  bucket         = "INPUT-BUCKET-NAME"
}
```

### Modules

>A **module** is a collection of Terraform configuration files in a folder. At least one module, referred to as the root module, is present in every Terraform configuration.


## Terraform workflow![[DevOps_S7_L1_Scheme_2.svg]]

A typical Terraform workflow consists of several steps:

- Create configuration files
	- Start by crafting configuration files using the HashiCorp Configuration Language (HCL). These files describe the desired infrastructure, resources, configurations, and dependencies.

- Initialize configuration
	- Before using Terraform, initialize the working directory, were root module files are located. During initialization, Terraform downloads the necessary provider plugins and sets up the working environment. To start initialization, run the `terraform init` command:

```bash
terraform init
```

- Generate Terraform plan
	- Before making any changes to your infrastructure, you can preview the execution plan using the `terraform plan` command. Terraform analyzes your configuration and the current state to generate a plan that outlines the actions it will take to achieve the desired state.

```bash
terraform plan
```

- Apply changes
	- When you're satisfied with the plan, you can apply it using the `terraform apply` command. Terraform compares the plan to the current state and takes action accordingly. It may create, update, or delete resources as needed.

```bash
terraform apply
```

After the `terraform apply` command, Terraform updates its state file to reflect the changes it made during the apply process. This state file is used as the basis for future operations.

- Destroy resources
	- Once the infrastructure is no longer needed, use the `terraform destroy` command to delete all the resources that were created by a Terraform configuration. Resources are destroyed in reverse order of their creation, ensuring that dependencies are handled correctly.

```bash
terraform destroy
```

Terraform updates its state file to reflect the removal of resources.
### Terraform initialization

The `terraform init` command is used to:
- Install necessary providers
- Install child modules
- Initialize backend

## Terraform modules

Every Terraform project manages the following:

- Defining configurations for the chosen cloud platform to enable interaction with it.
- Specifying cloud components or resources to be managed.
- Maintaining the state of the infrastructure.
- Managing input and output variables for flexibility and customization.
- Creating and utilizing modules for efficient code organization and reuse.
- Implementing infrastructure security standards and best practices.
- Integrating Terraform into CI/CD workflows for automated deployments.

Terraform code is stored in plain text files with the `.tf` file extension. Configuration files are commonly used to refer to files containing Terraform code.

- Configuration files must use UTF-8 encoding.
- Terraform typically loads all `.tf` files in a directory and expects each to define a unique set of configuration objects. Terraform throws an error if two files try to define the same object.


Terraform offers multiple methods for providing values to variables, including using `.tfvars` files, supplying them as CLI arguments, or setting them as environment variables. By default, Terraform loads values from a file named `terraform.tfvars`.


```bash
terraform apply -var-file="myvariables.tfvars"
```

The order of precedence between variable files is as follows:

1. `terraform.tfvars`
2. `*.auto.tfvars`
3. A custom file specified using the `-var-file` argument

```bash
mytf-project
├── main.tf
├── output.tf
├── provider.tf
├── terraform.tfvars
└── variables.tf
```

Modules solve the following problems:
- Organize configuration
	- Modules help you structure and navigate your configuration by grouping related components. Even with moderately complex infrastructure, organizing your configuration into logical components makes management more straightforward.

- Encapsulate configuration
	- Modules encapsulate configuration into distinct logical units, reducing the chances of unintended consequences or naming conflicts between resources.

- Reuse configuration
	- Modules allow you to reuse configuration, saving time and reducing errors by leveraging configurations created by your team or the Terraform community.

- Consistency and best practices 
	- Modules promote consistency in configurations, making complex setups more understandable. They also ensure that best practices are consistently applied, preventing accidental misconfigurations.

![[S7_L3-10_hot_spot_standart_module_structure.svg]]

When to write a module:
- Raising the level of abstraction
- Wrapping several resource types

>It's not advisable to create modules that merely wrap single resource types. If you find it challenging to name your module differently from the main resource type it contains, it's a signal that the module doesn't introduce new abstraction and may add unwarranted complexity. In such cases, it's better to use the resource type directly within the calling module.


## Functions

```Python
<FUNCTION NAME>(<ARGUMENT 1>, <ARGUMENT N>)
```

Types of built-in functions:

- Numeric functions
	- Perform mathematical operations.

```Python
> max(10, 9, 8)
10
> min(10, 9, 8)
8
> log(8, 2)
3
```

- String functions
	- Manipulate strings and retrieve information about them.

```Python
> lower("HELLO WORLD")
hello world
> upper("hello world")
HELLO WORLD
> title("hello world")
Hello world
```

- Collection functions
	- Facilitate the creation of new collections by applying transformation rules to existing ones.

```Python
> distinct(["a", "b", "c", "d", "a", "b"])
[
  "a", 
  "b", 
  "c", 
  "d"
]
> contains([1, 2, 3, 4, 5], 2)
true
```

- Encoding functions
	- Used for encoding and compression encryption.

```Python
> base64encode("string")
c3RyaW5n
```

- Filesystem functions
	- Manipulate and interact with the filesystem.

```Python
> dirname("foo/bar/baz.txt")
foo/bar
```

- Data and time functions
	- Operate on date and time inputs.

```Python
> timestamp()
2021-10-05T21:20:34
> formatdata("DD MMM YYYY hh:mm ZZZ", timestamp())
05 Oct 2021 21:20 UTC
```


- Hash and cryptography functions
	- Used for hashing and encryption.

```Python
> md5("hello world")
5eb63bbbe01eeed093cb22bb8f5acdc3
```

- IP network functions
	- Assist in manipulating IP addresses and network-related data.

```Python
> cidrnetmask("10.0.0.0/24")
255.255.255.0
```

- Type conversion functions
	- Allow you to convert data types.

```Python
> tostring(123)
123
```


You can find the complete list of built-in functions here:
- [Built-in Functions - Terraform documentation](https://developer.hashicorp.com/terraform/language/functions)


- Terraform also supports interpolation. The `${ ... }` markers are used to evaluate expressions and insert the result into strings. For example:

```
"Hello, ${var.name}!"
```


- Based on a resource type's name, Terraform knows which provider to use automatically. As an example, "`aws_instance`" is a resource type name that begins with the preferred local name of the provider.
