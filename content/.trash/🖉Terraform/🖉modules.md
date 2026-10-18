---
created: 2025-01-17
sticker: lucide//cog
color: "#7E00FF"
tags:
  - terraform
  - lab
---
# Terraform Modules Demystified: Deploying a Static Website on Azure Blob Storage

Learn how to create reusable Terraform modules and create a fully functional static website hosted on Azure (for $0) 
## Introduction

Terraform modules are a powerful way to break down complex infrastructure configurations into smaller, reusable components, making it easier to manage and maintain your Infrastructure as Code (IaC). Modules are the primary means of packaging and distributing Terraform code. 

In this article, we will explore this topic in great details, both from a theoretical and practical perspectives, by achieving two goals:

1. Understanding what Terraform modules are, their structure, and the how to write them. The discussion will also include module variables and their usage (input, output, and local variables), and how to call reusable modules in other configurations.

2. Creating and using a Terraform module that deploys a static website on Azure Blob storage. A classic project, perfect to illustrate main Terraform concepts.

So, let's jump right in!
## Terraform modules

>A Terraform module is a set of Terraform configuration files that define a group of related infrastructure resources. Modules help to organize IaC into logical units, each typically accomplishing a single goal, such as provisioning a network, database, or a virtual machine. 

>A module represents a structured set of Terraform configuration files (`.tf` or `.tf.json`) in a dedicated folder. 

- Any set of Terraform configuration files in a folder is considered a module. 

- Every Terraform configuration has at least one module, known as the **root module**. The root module is the top-level module of any Terraform configuration.

- Any Terraform module (usually the root) can invoke, or reuse, other modules, known as **child modules**, to include their resources into the configuration. 

- Child modules can be called multiple times within the same configuration, and multiple configurations can use the same child module.

 - Terraform modules can be loaded to/from a public or private registry. The official [Terraform Registry](https://registry.terraform.io/browse/modules) is a host for numerous publicly available Terraform modules for configuring many types of infrastructure.
 - These modules are free to use, and Terraform can download them automatically if they are called somewhere in the project, given the appropriate module source and version.

>For those who are familiar with Ansible: Terraform modules can be compared to Ansible roles, also being the way to share and reuse configuration components in structured directories. However, not every Ansible configuration can be considered a role, whereas any Terraform configuration is a module, just not necessarily reusable.
### Structure of a Module

- Each module must have its own directory. Conventionally, modules are stored in the `modules` folder inside a project directory.

A well-structured Terraform module typically includes the following files:

- `main.tf` 
	- The main configuration file that defines primary infrastructure resources.

- `variables.tf`
	- The file that defines input variables passed into the module and used to customize module behavior.

- `outputs.tf`
	- The file that defines the output variables produced by the module.

- `README.md`
	- An optional, yet highly recommended, Markdown file that documents how to use the module, including variable descriptions, example usage, and output values. 

Other optional files might be:
w
- `providers.tf`
	- Only configured in the root modules.
	- The file where Terraform providers are configured.


Here is the structure of a Terraform module, depicted schematically:

```bash
modules
├── module-name/
│   ├── main.tf 
│   ├── variables.tf
│   ├── outputs.tf
│   └── README.md
└── another-module/
    ├── # ...
    # ...
```

## Module variables

>Variables in Terraform are named values that can be referenced and utilized in infrastructure configuration files. 

There are three main types of variables in Terraform:

- Input variables
- Output variables
- Local variables




### Input variables

Input variables are used to customize the behavior of a module by allowing users to pass input values in module invocation blocks (`module`), or through command-line arguments (`-var`).

Definitions of input variables consists of:

- Name (required)
	- A unique name for the variable.

- Type (optional) 
	- The data type of the variable.

- Description (optional)
	- Description of the variable. 
	- Also used to generate documentation for the module.

- Default value (optional)
	- An optional default value that will be used if no value is provided.

In modules themselves, input variables are defined using the `variable` blocks in a separate file named`variables.tf`:

```Python
# variables.tf
variable "variable_name" {
  type        = variable_type                 
  description = "Description of the variable" 
  default     = default_value                 
}
```

For example: 

```Python
# variables.tf
variable "region" {
  type        = string
  description = "The Azure region to deploy resources"
  default     = "East US"
}
```

In resource definitions, input variables are referenced by their name with the `var.` prefix: `var.variable_name`. For instance:

```Python
# main.tf
resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name  # "rg-cloud-resume-challenge"
  location = var.region               # "East US"
}
```


### Output variables

Output variables serve as a means of returning data about infrastructure resources from a module. They make it easier to understand the results of module execution and *to pass values as inputs to a parent module.* 

- A root module can print values of output variables in the CLI after running `terraform apply` (not `terraform plan`).

Each output variable is declared with:

- Name (required)
	- A unique name for the output variable.

- Value (required)
	- An expression whose result is to be returned by this variable.

- Description (optional)
	- Description of the variable. 

Output variables are typically defined with `output` blocks, typically in a separate, `outputs.tf` file inside a module:

```Python
output "output_name" {
  value       = <expression> # the data you want to output
  description = "Description of the variable"
}
```

For example:

```Python
output "resource_group_name" {
  value       = azurerm_resource_group.rg.name
  description = "The name of the resource group containing the storage account."
}
```

Here, `value` takes the `name` attribute of the `rg` object of the type `azurerm_resource_group` as the value for the output variable. 

### Variable data types

For more information, refer to the [official documentation](https://developer.hashicorp.com/terraform/language/values/variables).

## Reusing modules: calling child modules

One of the key reasons for creating Terraform modules is their reusability. You only need to call a Terraform module that describes resources that you need to provision and customize the behavior of that module using variables.  

To invoke an existing module within a Terraform configuration, use the `module` block. Here is how it looks like:

```Python
module "<module_name>" {
  source = "<source>"
  # input variables... 
}
```

You assign the module a name local to your current configuration, specify source and other metadata, and then input variables you want to use.

Here is an example of how to call the module we will create in the next section:

```Python
module "azure_static_website" {
	source = "./modules/static-website"
	storage_account_name = "unique_storage_account_name" # required
	resource_group_name  = "custom-resource-group-name"
    rg_location          = "West US"
    # other input variables ...
}
```
### Module sources

The `source` parameter specifies where Terraform can find the module. 
There are several module sources supported, notably:

- Local paths 
	- Relative filesystem paths that point to modules stored locally. 

```Python
module "module_name" {
	source = "./modules/module_name"
	# input variables...
}
```

- Terraform Registry
	- Public modules loaded from the [Terraform Registry](https://registry.terraform.io/), referred to by a registry source address in the form `<namespace>/<name>/<provider>`.

```Python
module "consul" {
  source = "hashicorp/consul/aws"
  version = "0.1.0"
  # input variables...
}
```

- GitHub
	- URLs to modules stored in GitHub repositories. 

```Python
module "module_name" {
	source = "github.com/<username>/<module_repository>"
	# input variables...
}
```

- Git, Mercurial repositories
	- Modules stored in generic Git or Mercurial repositories, specified by Git/Mercurial URLs with the appropriate prefix.

```Python
module "storage" {
  source = "git::username@example.com:storage.git"
  # input variables...
}
```

```Python
module "vpc" {
  source = "hg::http://example.com/vpc.hg"
  # input variables...
}
```

When working with modules written by someone else, you will often need to consult module documentation to understand what input variables are available and what values are expected to be put there.  
This documentation is typically located in the Terraform Registry alongside the module. Search for modules in Terraform Registry [here](https://registry.terraform.io/browse/modules).

### Other module meta-arguments

Apart from `source` and `version`, Terraform defines a few other optional meta-arguments that can be specified in the `module` block:

- [`count`](https://developer.hashicorp.com/terraform/language/meta-arguments/count)
	- Creates multiple instances of a module from a single `module` block.
	- For example, when referring to an `azure-vm-module` module which specifies configuration for an Azure Virtual machine, the `count` argument set to `3` will create three virtual machines. Individual VM instances can then be referred to by `module.<name>[<index>]`, e.g., `module.azurerm_virtual_machine[0]`

- [`for_each`](https://developer.hashicorp.com/terraform/language/modules/syntax#for_each)
	- Similarly to `count`, creates multiple instances of a module from a single `module` block.
	- The `count` and `for_each` arguments can not both be used in the same module.

- [`providers`](https://developer.hashicorp.com/terraform/language/meta-arguments/module-providers)
	- Passes provider configurations to a child module.
	- If not specified, the child module inherits all default (unaliased) provider configurations from the calling module.

- [`depends_on`](https://developer.hashicorp.com/terraform/language/meta-arguments/depends_on)
	- Creates explicit dependencies between the entire module and the listed targets.

Arguments with names apart from the `source` and `version`, as well as names of other module meta-arguments, represent input variables defined by the child module.

### Chaining modules

Another noteworthy fact is that resources attributes from one module can be used as inputs to another module. This creates a configuration somewhat resembling a chain.
For example, 

```Python
module "vpc" {
  source = "./vpc"
}

module "subnet" {
  source    = "./subnet"
  vpc_id    = module.vpc.vpc_id
}
```

For more information, see [official documentation](https://developer.hashicorp.com/terraform/language/modules/sources#local-paths).
## Creating a Terraform module: deploying static website on Azure blob storage

It's time to get our hands dirty. Roll up your sleeves!
We will deploy a simple static website in Azure blob storage — a great project to demonstrate the key concepts behind writing Terraform modules. 

Prerequisites:
- Azure account (don’t worry, all deployments in this lab will incur no costs — $0).
- Azure CLI ([installation documentation](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-linux?pivots=script))
- Terraform ([installation documentation](https://developer.hashicorp.com/terraform/install))

When you're done with this tutorial, our project will look like this:

```bash
tree
```
```bash
.
├── modules/
│   └── static-website/
│       ├── main.tf
│       ├── variables.tf
│       ├── outputs.tf
│       └── README.md
└── example/
    └── main.tf
```


- Modules will go into the `modules` directory inside the project repository, each contained in its own subdirectory.
- The `src/static` will hold files for the website itself. 

Here is what we will do, step-by-step:

1. Create the `main.tf` file to define the primary Azure resources to be provisioned by Terraform (e.g., storage account, blob storage containers, etc.). Configuration will utilize several input variables that we will define subsequently.

2. Create the `variables.tf` file to declare all necessary input variables for the module.

3. Define the output variables of the module in the `outputs.tf` file.

4. Create a `README.md` file for proper module documentation. 

Let's get started!
### Step 1: Provisioning cloud resources: `main.tf`

Each module in Terraform should accomplish a single objective — here, our goal is to create an Azure storage account and deploy a static website. The `main.tf` file will govern all cloud resources that Terraform will create and manage for this specific purpose. If we were deploying, say, an API server, all related Terraform configuration would reside in a separate module.

We won't get into the syntax too much, but pay attention to how we define resources and use variables in the configuration. We use variables whenever we can, to make the module as flexible and reusable as possible.

Here is how `main.tf` looks like:

```Python
provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name # "rg-cloud-resume-challenge"
  location = var.rg_location         # "East US"
}

resource "azurerm_storage_account" "blob_storage" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = var.storage_account_tier             # "Standard"
  account_replication_type = var.storage_account_replication_type # "LRS"
}

resource "azurerm_storage_account_static_website" "static_website" {
  storage_account_id = azurerm_storage_account.blob_storage.id
  index_document     = var.index_document # "index.html"
  error_404_document = var.error_document # "index.html"
}

resource "azurerm_storage_container" "container" {
  name                  = var.storage_container_name # web
  storage_account_name  = azurerm_storage_account.blob_storage.name
  container_access_type = "container"
}

resource "azurerm_storage_blob" "index_blob" {
  name                   = var.index_document # index.html
  storage_account_name   = azurerm_storage_account.blob_storage.name
  storage_container_name = azurerm_storage_container.container.name
  type                   = "Block"
  source                 = local.index_filepath
  content_type           = "text/html" 
  content_md5            = md5(file(local.index_filepath))
  # "${path.module}/../../src/static/index.html"
}

resource "azurerm_storage_blob" "styles_blob" {
  name                   = var.styles # styles.css
  storage_account_name   = azurerm_storage_account.blob_storage.name
  storage_container_name = azurerm_storage_container.container.name
  type                   = "Block"
  source                 = local.styles_filepath
  content_type			 = "text/css"
  content_md5            = md5(file(local.styles_filepath))
  # "${path.module}/../../src/static/styles.css"
}

locals {
	source_path     = "${path.module}/../../src/static/"
	styles_filepath = "${local.source_path}${var.styles}"
	index_filepath  = "${local.source_path}${var.index_document}"
}
```

- Link to this file on GitHub: [`modules/static-website/main.tf`](https://github.com/0xtr1gger/cloud_resume_challenge/blob/main/modules/static-website/main.tf)

>You may have noticed the absence of the `provider` block in the module definition. Providers should only be configured in root modules, rather than within reusable modules.

>In this configuration, we defined only two blobs (`index_blob` and `styles_blob` for `index.html` and `styles.css`, respectively). However, if you plan to upload more files, you may find it cumbersome to define each blob separately. In such situations, use the `for_each` Terraform meta-argument instead ([documentation](https://developer.hashicorp.com/terraform/language/meta-arguments/for_each)).
### Step 2: Defining variables: `variables.tf`

In the `main.tf` file, we referenced the following variables, which we will now define in the `variables.tf` file:

1. `var.storage_account_name`
2. `var.resource_group_name`
3. `var.rg_location`
4. `var.storage_account_tier`
5. `var.storage_account_replication_type`
6. `var.index_document`
7. `var.error_document`
8. `var.styles`
9. `var.storage_container_name`

Thus, the `variables.tf` file will be structured like this:

```Python
variable "storage_account_name" {
  type        = string
  description = "The unique name for the Azure Storage Account."
}

variable "resource_group_name" {
  type        = string
  description = "The name of the Azure resource group to create."
  default     = "rg-cloud-resume-challenge"
}

variable "rg_location" {
  type        = string
  description = "The Azure region to deploy the resources."
  default     = "East US"
}

variable "storage_account_tier" {
  type        = string
  description = "The tier for the Azure storage account."
  default     = "Standard"
}

variable "storage_account_replication_type" {
  type        = string
  description = "The replication type for the storage account."
  default     = "LRS"
}

variable "index_document" {
  type        = string
  description = "The name of the index document for the static website."
  default     = "index.html"
}

variable "error_document" {
  type        = string
  description = "The name of the error document for the static website."
  default     = "index.html"
}

variable "styles" {
  type        = string
  description = "The name of the CSS file for the website."
  default     = "styles.css"
}

variable "storage_container_name" {
  type        = string
  description = "The name of the Azure Blob storage container."
  default     = "web"
}
```

- Link to this file on GitHub: [`modules/static-website/variables.tf`](https://github.com/0xtr1gger/cloud_resume_challenge/blob/main/modules/static-website/variables.tf)

Here, we define only one mandatory variable without the default value: the name for the Azure storage account, `storage_account_name`, since it must be unique.

>**Note**: Both the index page (`var.index_document`) and the error page (`var.error_document`) reference the same variable. This is why we had no need to create a separate blob for the error page file. However, if you define a custom error page, remember to add the corresponding `azurerm_storage_blob` block to load the static file, similar to the `index_blob` and `styles_blob` configurations we defined earlier in the `main.tf` file.

### Step 3: Defining outputs: `outputs.tf`

Next, we will define module outputs in the `outputs.tf` file. Here is what we put there:

```Python
output "resource_group_name" {
  description = "The name of the resource group containing the storage account."
  value       = azurerm_resource_group.rg.name
}

output "storage_account_name" {
  description = "The name of the Azure Storage Account."
  value       = azurerm_storage_account.blob_storage.name
}

output "storage_account_primary_web_endpoint" {
  description = "The primary web endpoint for the static website."
  value       = azurerm_storage_account.blob_storage.primary_web_endpoint
}

output "storage_container_name" {
  description = "The name of the storage container for static files."
  value       = azurerm_storage_container.container.name
}

output "index_blob_url" {
  description = "The URL of the index.html blob."
  value       = "${azurerm_storage_account.blob_storage.primary_web_endpoint}${azurerm_storage_container.container.name}/${var.index_document}"
}
```

- Link to this file on GitHub: [`modules/static-website/outputs.tf`](https://github.com/0xtr1gger/cloud_resume_challenge/blob/main/modules/static-website/outputs.tf)

The last output variable `index_blob_url`, evaluates the URL of the index page of the static website by concatenating the storage account endpoint, took from a resource definition block in `main.tf`, and the name of the index file, defined in a variable.

Notice that we don't need to import anything explicitly. Terraform treats all configuration files in a module as if they were parts of a single file; organizing configuration into separate files is only used to make it easier for humans to understand and deal with.
### Step 4: Creating HTML and CSS

The focus of this article isn’t on HTML and CSS, so we won't go through it here. You can just include a minimal heading with "Hello, world!": it won't affect the Terraform module operation anyway.

For reference, here are links to my example files. They serve as a CV template:

- [`index.html`](https://github.com/0xtr1gger/cloud_resume_challenge/blob/main/src/static/index.html)
- [`styles.css`](https://github.com/0xtr1gger/cloud_resume_challenge/blob/main/src/static/styles.css)

### Step 5: Using the module

With the module complete and functional, we can now create a separate project that invokes it as a child module.

Create a folder called `example` in your project directory, and the `main.tf` file inside — this is where we will call our module. Here is how it looks like:

```Python
# example/main.tf

terraform {
  required_version = ">=1.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

module "website_module" {
	source               = "../modules/static-website"
	storage_account_name = "unique_storage_account_name"
}
```

- Link to this file on GitHub: [`example/main.tf`](https://github.com/0xtr1gger/cloud_resume_challenge/blob/main/example/main.tf)

>Providers are only configured in the root module. So, here they are.

As mentioned, we defined only one required variable (`storage_account_name`), while others will simply be substituted with the defaults. 
However, if you want to customize the behavior of this module, you can override any of the variables we defined. For example: 

```Python
# ...
module "website_module" {
	source               = "../modules/static-website"
	storage_account_name = "unique_storage_account_name"
	resource_group_name  = "custom-resource-group-name"
	rg_location          = "East Asia"
}
```
### Step 6: Validating and formatting Terraform configuration

To verify your Terraform configuration, use the `terraform validate` command. Although it doesn't check if the resources themselves are valid, it verifies the syntax and structure of configuration files, tries to resolve variables, and checks if all the required providers are installed.

```bash
terraform validate
```

After validation, it is best to apply the `terraform fmt` command to format the files according to standards. This won't change anything functionally, but merely adjust indentation.

```bash
terraform fmt
```

### Step 7: Initiating and applying the configuration

Finally, the configuration is finished. It's time to apply it!

1. First, initialize the configuration with `terraform init`:

```bash
terraform init
```


![[images/DevOps/Terraform/cloud_resume_challenge_lab/static_website/terraform_init.png]]


2. Next, run the `terraform plan`. This command outputs all the changes Terraform will make to the infrastructure without applying them. This is a dry run that helps you verify the configuration works as intended.

```bash
terraform plan
```

3. If everything looks good, execute the `terraform apply` command:

```bash
terraform apply
```

Upon running this command, Terraform will report what's going on, and if everything is provisioned successfully, print the output variables to the terminal, like this:

![[images/DevOps/Terraform/cloud_resume_challenge_lab/static_website/terraform_apply.png]]
### Step 8: Writing module documentation: `README.md`

Don't underestimate this part, please. Providing documentation is crucial. 

There are two ways to add documentation to a Terraform module:
- Generate the docs automatically with [`terraform-docs`](https://github.com/terraform-docs/terraform-docs)
- Write them manually

Let's try out the  [`terraform-docs`](https://github.com/terraform-docs/terraform-docs). We can launch this tool directly in a Docker container, mounting the module as a Docker volume and redirecting container output (the documentation itself) to a markdown file:

```bash
docker run --rm --volume "$(pwd):/terraform-docs" -u $(id -u) quay.io/terraform-docs/terraform-docs:0.19.0 markdown /terraform-docs > README.md
```

`terraform-docs` takes the description of the variables we provided in variable definitions to generate tables with essential information about the inputs and outputs. It also detects all requirements and dependencies, puts them into a table, and even adds links to their documentation. 

You can also add a custom short description to your module to outline its purpose:

```Markdown
# Azure Blob Storage Static Website  

This Terraform module provisions a static website hosted on Azure Blob Storage. It creates an Azure resource group, storage account, storage container, then loads blobs for HTML and CSS files and deploys a static website within the container.
```

Giving examples of how to use the module would also be beneficial:

```Python
module "azure_static_website" {
	source               = "./modules/static-website"
	storage_account_name = "unique_storage_account_name" # required
	resource_group_name  = "custom-resource-group-name"
    rg_location          = "West US"
    # other input variables ...
}
```

You can see the resulting `README.md` in the project repository: [`modules/static-website/README.md`](https://github.com/0xtr1gger/cloud_resume_challenge/tree/main/modules/static-website).
## Conclusion

Terraform modules is a backbone of effective Infrastructure as Code (IaC). They simplify the management of complex configurations by breaking them down into smaller, reusable components. This article walked you through understanding the structure of Terraform modules, module variables, and module invocation, illustrating the process of writing modules with a practical example: deploying a static website on Azure Blob Storage.

The module that we used for the demonstration in the practical part is the first component of my [Cloud Resume Challenge](https://cloudresumechallenge.dev/) project, which, apart from the static website, will also include a GitHub Actions pipeline and API server written in Flask, Python (deployed in an Azure VM using Terraform). I will publish the full project walkthrough soon, where we will take a more in-depth look at the complete infrastructure, so stay tuned! 

Happy coding!

## References and further reading

- https://developer.hashicorp.com/terraform/language/values/variables
- https://developer.hashicorp.com/terraform/language/values/locals
- https://developer.hashicorp.com/terraform/language/values/outputs
## Sharing modules

# drafts


## Best practices

- Keep modules focused
- Use descriptive names of modules
- Document everything in `README.md`
- Use consistent variable naming
- Define variable types and provide default values
- Minimize hardcoding
- Tests modules with tools like `terratest`
- Use version control for writing modules
- Regularly run the `terraform fmt` command to maintain consistent formatting of HCL code.  

## Using modules

| Feature                  | Traditional Variables                                                    | Module Variables                                                        |
| ------------------------ | ------------------------------------------------------------------------ | ----------------------------------------------------------------------- |
| **Scope**                | Root module; affects all resources globally                              | Scoped to the specific module                                           |
| **Declaration Location** | Usually in `variables.tf` of the root module                             | In `variables.tf` within the module                                     |
| **Usage**                | Used by resources/action in the root module and can be passed to modules | Used by resources in the module and defined during module instantiation |
| **Accessibility**        | Global to the configuration unless passed                                | Must be passed from the root module to be used                          |

>Terraform modules are self-contained packages of Terraform configuration code that defines  encapsulate a logical unit of infrastructure, such as a network, a database, or an application.


### Conditional logic


## References

Documentation:
- https://developer.hashicorp.com/terraform/language/modules/sources#local-paths