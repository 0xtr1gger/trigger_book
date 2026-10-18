---
created: 2026-10-05
updated: 2026-10-05
---
> A **module** is a set of Terraform configuration files in a single directory. Modules are the unit of composition and reuse in Terraform: a module groups related resources behind an interface of input variables and outputs, and can be called from other configurations.

- Every Terraform configuration is a module. Any directory of `.tf` files qualifies; not every module is designed to be reusable.
- Modules organise configuration into logical components, encapsulate implementation details, enforce consistent conventions (naming, tagging, encryption), and allow tested patterns to be shared across teams.
- Modules are comparable to Ansible roles as a packaging mechanism, with one difference: every Terraform configuration is implicitly a module, whereas only purpose-built Ansible content is a role.

## Root and child modules

- The **root module** is the directory in which Terraform commands are run. It holds the backend configuration, provider configurations, and the values of root input variables.
- A **child module** is a module called by another module through a `module` block. Child modules can call further child modules, forming a **module tree**.
- A child module can be called several times, from one or many configurations, each call creating an independent set of resources.
- Child modules are installed by `terraform init` (or `terraform get`) into `.terraform/modules/`, and indexed in `.terraform/modules/modules.json`. Local-path modules are used in place and not copied.

## Standard module structure

HashiCorp defines a standard structure that tooling (the registry, `terraform-docs`) understands:

```text
terraform-aws-network/
├── main.tf            # resources of the module
├── variables.tf       # input variable declarations
├── outputs.tf         # output declarations
├── versions.tf        # terraform block: required_version, required_providers
├── README.md          # purpose, usage, inputs, outputs
├── LICENSE
├── modules/           # nested modules, callable separately
│   └── subnet-group/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── examples/          # complete, runnable usage examples
│   └── basic/
│       └── main.tf
└── tests/             # *.tftest.hcl test files
    └── basic.tftest.hcl
```

| File or directory | Purpose |
| ----------------- | ------- |
| `main.tf` | Declare the module's resources and data sources; split into more files by concern as it grows. |
| `variables.tf` | Declare the input variables with types, descriptions, defaults, and validation. |
| `outputs.tf` | Declare the values the module exports. |
| `versions.tf` | Declare the minimum Terraform and provider versions the module requires. |
| `README.md` | Document purpose, usage examples, inputs, outputs, and requirements. |
| `modules/` | Hold nested modules that callers may also use directly. |
| `examples/` | Provide runnable configurations that call the module, used as documentation and as test fixtures. |
| `tests/` | Hold tests for the native test framework (see [[Terraform testing#The terraform test framework]]). |

- A reusable module contains no `provider` blocks and no `backend` block. Both are the responsibility of the root module (see [[#Providers in modules]]).
- How root configurations are laid out in a repository is covered in [[Terraform project structure#Repository layout]].

## Calling a module

```hcl
module "network" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 6.0"

  name            = "prod"
  cidr            = "10.10.0.0/16"
  azs             = ["eu-central-1a", "eu-central-1b", "eu-central-1c"]
  private_subnets = ["10.10.1.0/24", "10.10.2.0/24", "10.10.3.0/24"]
  public_subnets  = ["10.10.101.0/24", "10.10.102.0/24", "10.10.103.0/24"]
}

resource "aws_security_group" "app" {
  name   = "app"
  vpc_id = module.network.vpc_id
}
```

- The label (`network`) is the module call's local name, used in addresses (`module.network`) and references (`module.network.vpc_id`).
- `source` is required and tells Terraform where to obtain the module (see [[#Module sources]]). `version` constrains the version for registry modules.
- Every other argument corresponds to an input variable declared by the child module. Required variables must be set; optional ones fall back to their defaults.
- The calling module can access only the child's outputs. Resource attributes inside the child are not accessible unless the child exports them.
- After adding or changing a `module` block, `terraform init` must be run to install the module.

## Module sources

| Source type | Example `source` value |
| ----------- | ---------------------- |
| Local path | `./modules/network`, `../shared/network` |
| Terraform Registry | `terraform-aws-modules/vpc/aws` |
| Private registry | `app.terraform.io/acme/network/aws` |
| GitHub | `github.com/acme/terraform-aws-network` |
| Bitbucket | `bitbucket.org/acme/terraform-aws-network` |
| Generic Git | `git::https://git.example.com/infra/network.git?ref=v1.4.0` |
| Generic Git over SSH | `git::ssh://git@git.example.com/infra/network.git?ref=v1.4.0` |
| Mercurial | `hg::https://hg.example.com/network?ref=v1.4.0` |
| HTTP archive | `https://artifacts.example.com/modules/network-1.4.0.zip` |
| Amazon S3 | `s3::https://s3.eu-central-1.amazonaws.com/acme-modules/network-1.4.0.zip` |
| Google Cloud Storage | `gcs::https://www.googleapis.com/storage/v1/acme-modules/network-1.4.0.zip` |

- **Local paths** must begin with `./` or `../`; otherwise Terraform interprets the string as a registry address. They are not versioned independently — they change together with the calling code.
- **Registry addresses** have the form `[<HOSTNAME>/]<NAMESPACE>/<NAME>/<PROVIDER>`. They are the only source type that supports the `version` argument.
- **Git sources** accept query parameters:
	- `ref` selects a branch, a tag, or a commit SHA;
	- `depth=1` performs a shallow clone.
- **Subdirectories** of a repository or archive are selected with a double slash: `git::https://git.example.com/infra/modules.git//network?ref=v1.4.0`.
- Authentication to private Git, HTTP, S3, and GCS sources uses the credentials of the environment that runs `terraform init` (SSH agent, Git credential helpers, cloud SDK credentials).

## Module versioning

- **Registry modules** are versioned with semantic version tags and selected with the `version` argument and a version constraint:

```hcl
module "network" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "6.0.0"
}
```

- **Git modules** are versioned with `ref`. A tag (`?ref=v1.4.0`) is readable but mutable — it can be moved to another commit by anyone with push access. A full commit SHA (`?ref=5f1e3c9a...`) is immutable and is the strongest pin.
- Module versions are not recorded in the dependency lock file, which covers providers only. The pin in the `module` block is the only protection against an upstream change (see [[Terraform security#Supply chain security]]).
- Upgrade modules to the newest versions allowed by their constraints:

```bash
terraform init -upgrade
```

- Module authors should follow semantic versioning: increment the major version for any change that breaks callers, including renamed variables, removed outputs, and changes that force resource replacement.

## Module meta-arguments

| Meta-argument | Purpose |
| ------------- | ------- |
| `source` | Specify where to obtain the module (required). |
| `version` | Constrain the version of a registry module. |
| `count` | Create several instances of the module, addressed by index. |
| `for_each` | Create one instance of the module per map key or set element. |
| `providers` | Pass provider configurations to the child module explicitly. |
| `depends_on` | Make the entire module depend on other resources or modules. |

- `count` and `for_each` work as on resources (see [[Terraform resources#Meta-arguments]]) and cannot be combined:

```hcl
module "service" {
  source   = "./modules/service"
  for_each = var.services

  name          = each.key
  image         = each.value.image
  desired_count = each.value.replicas
}

output "service_urls" {
  value = { for name, svc in module.service : name => svc.url }
}
```

- Instances are addressed as `module.service["api"]`; resources inside them as `module.service["api"].aws_ecs_service.this`.
- `depends_on` on a module makes every resource and data source in it depend on the targets. All data sources inside the module are then read during apply whenever the target has changes, which can produce large numbers of unknown values. Passing the needed values as inputs creates finer-grained dependencies and should be preferred.

## Providers in modules

- Provider configurations belong in the root module. A child module declares which providers it needs in `required_providers`, and receives configurations from its caller.
- By default, a child module inherits the default (unaliased) configuration of each provider from its caller.
- Aliased configurations must be passed explicitly with the `providers` argument:

```hcl
# Root module
provider "aws" {
  region = "eu-central-1"
}

provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}

module "cdn" {
  source = "./modules/cdn"

  providers = {
    aws           = aws
    aws.us_east_1 = aws.us_east_1
  }
}
```

- A module that needs several configurations of the same provider declares the alias names it expects with `configuration_aliases`:

```hcl
# modules/cdn/versions.tf
terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source                = "hashicorp/aws"
      version               = ">= 5.0"
      configuration_aliases = [aws.us_east_1]
    }
  }
}

# modules/cdn/main.tf
resource "aws_acm_certificate" "this" {
  provider          = aws.us_east_1
  domain_name       = var.domain_name
  validation_method = "DNS"
}
```

- A module that contains its own `provider` blocks (a **legacy module**) cannot be used with `count`, `for_each`, or `depends_on`, and removing the module call from configuration fails, because the provider configuration needed to destroy its resources disappears together with them.

## Module composition

- **Chaining** — outputs of one module become inputs of another, which creates the dependency between them:

```hcl
module "network" {
  source = "./modules/network"
  cidr   = "10.10.0.0/16"
}

module "database" {
  source     = "./modules/database"
  vpc_id     = module.network.vpc_id
  subnet_ids = module.network.private_subnet_ids
}
```

- **Flat composition** — the root module calls each component module directly and wires them together, rather than modules calling each other in deep hierarchies. Shallow trees are easier to understand, refactor, and test.
- **Dependency inversion** — a module accepts the objects it depends on as inputs (`vpc_id`, `subnet_ids`) instead of creating them or looking them up itself. The same module then works with infrastructure created by Terraform, by another configuration, or by hand.
- **Data-only modules** — a module that contains only data sources and outputs encapsulates the lookup of shared infrastructure (for example, the organisation's network by naming convention), so that consumers do not depend on how it is found.

## Designing modules

When a module is justified:

- It raises the level of abstraction: callers think in terms of "a service", "a network", "a static website", not in terms of individual resources.
- It groups several resource types that are always deployed together and must be configured consistently.
- It encodes organisational policy: encryption, logging, tagging, network placement.

When a module is not justified:

- A module that wraps a single resource type adds a layer of indirection without adding abstraction. If the module is hard to name differently from the resource it contains, use the resource directly.

Interface design:

- Keep the interface small and stable. Every input is a commitment; every output is a contract.
- Give every variable a `type` and a `description`, use `optional()` attributes for rich objects, and add `validation` blocks for constraints.
- Default to secure behaviour: encryption enabled, public access disabled, logging on. Make insecure options explicit opt-ins with descriptive names.
- Do not hardcode environment-specific values (account IDs, regions, names); accept them as inputs or derive them from data sources.
- Export the identifiers and attributes callers are likely to need (IDs, ARNs, names, endpoints), including whole objects where convenient.
- In `versions.tf`, declare minimum versions only (`>= 5.0`), leaving exact selection to the root module's lock file.
- Avoid `depends_on` inside modules and avoid calling other modules deeply.

## Documenting modules

A module's `README.md` should cover:

- the purpose of the module and what it creates;
- requirements: Terraform and provider versions, permissions needed, external prerequisites;
- at least one complete usage example;
- inputs (name, type, default, description, whether required);
- outputs (name, description).

The inputs, outputs, and requirements tables are best generated from the code with [terraform-docs](https://terraform-docs.io/), which reads the `description` of each variable and output:

- Generate a Markdown README for a module:

```bash
terraform-docs markdown table ./modules/static-website > ./modules/static-website/README.md
```

- Inject the generated section between `<!-- BEGIN_TF_DOCS -->` and `<!-- END_TF_DOCS -->` markers in an existing README, preserving the hand-written parts:

```bash
terraform-docs markdown table --output-file README.md --output-mode inject ./modules/static-website
```

- Run `terraform-docs` from its container image, without installing it:

```bash
docker run --rm -v "$(pwd):/terraform-docs" -u "$(id -u)" \
  quay.io/terraform-docs/terraform-docs:0.19.0 markdown /terraform-docs > README.md
```

- Generation is usually automated with a pre-commit hook so that documentation cannot drift from the code (see [[Terraform project structure#Version control hygiene]]).

## Publishing modules

- **Public Terraform Registry**
	- The module must be in a public GitHub repository named `terraform-<PROVIDER>-<NAME>` (for example, `terraform-aws-network`), follow the standard module structure, and have semantic version tags such as `v1.0.0`.
	- After the repository is registered, each new tag is published automatically as a module version.
- **Private registries**
	- HCP Terraform and Terraform Enterprise provide a private registry with addresses such as `app.terraform.io/<ORGANIZATION>/<NAME>/<PROVIDER>`.
	- GitLab provides a Terraform module registry per project or group.
	- Other artifact managers (Artifactory, Nexus) implement the registry protocol.
- **Git without a registry** — modules can be consumed directly from Git with `?ref=` pins, at the cost of losing version constraint resolution.

## Worked example

This module deploys a static website to an Azure Storage account using the built-in static website feature. It demonstrates the standard structure, inputs with validation, `for_each` over files, an explicit dependency, and outputs.

```text
.
├── modules/
│   └── static-website/
│       ├── main.tf
│       ├── variables.tf
│       ├── outputs.tf
│       └── versions.tf
├── site/
│   ├── index.html
│   ├── 404.html
│   └── styles.css
└── live/
    └── main.tf
```

### versions.tf

```hcl
terraform {
  required_version = ">= 1.5"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 4.0"
    }
  }
}
```

### variables.tf

```hcl
variable "storage_account_name" {
  type        = string
  description = "Globally unique name of the storage account (3-24 lowercase letters and digits)."

  validation {
    condition     = can(regex("^[a-z0-9]{3,24}$", var.storage_account_name))
    error_message = "storage_account_name must be 3-24 characters of lowercase letters and digits."
  }
}

variable "resource_group_name" {
  type        = string
  description = "Name of the resource group to create."
}

variable "location" {
  type        = string
  description = "Azure region of the resources."
  default     = "westeurope"
}

variable "replication_type" {
  type        = string
  description = "Replication type of the storage account."
  default     = "LRS"

  validation {
    condition     = contains(["LRS", "ZRS", "GRS", "RAGRS", "GZRS", "RAGZRS"], var.replication_type)
    error_message = "replication_type must be a valid Azure Storage replication type."
  }
}

variable "source_dir" {
  type        = string
  description = "Local directory whose contents are uploaded as the website."
}

variable "index_document" {
  type        = string
  description = "Document served for directory requests."
  default     = "index.html"
}

variable "error_document" {
  type        = string
  description = "Document served for missing paths."
  default     = "404.html"
}

variable "tags" {
  type        = map(string)
  description = "Tags applied to all resources."
  default     = {}
}
```

### main.tf

```hcl
locals {
  files = fileset(var.source_dir, "**")

  content_types = {
    ".html" = "text/html"
    ".css"  = "text/css"
    ".js"   = "application/javascript"
    ".svg"  = "image/svg+xml"
    ".png"  = "image/png"
    ".ico"  = "image/x-icon"
  }
}

resource "azurerm_resource_group" "this" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

resource "azurerm_storage_account" "this" {
  name                            = var.storage_account_name
  resource_group_name             = azurerm_resource_group.this.name
  location                        = azurerm_resource_group.this.location
  account_kind                    = "StorageV2"
  account_tier                    = "Standard"
  account_replication_type        = var.replication_type
  min_tls_version                 = "TLS1_2"
  https_traffic_only_enabled      = true
  allow_nested_items_to_be_public = false
  tags                            = var.tags
}

resource "azurerm_storage_account_static_website" "this" {
  storage_account_id = azurerm_storage_account.this.id
  index_document     = var.index_document
  error_404_document = var.error_document
}

resource "azurerm_storage_blob" "site" {
  for_each = local.files

  name                   = each.value
  storage_account_name   = azurerm_storage_account.this.name
  storage_container_name = "$web"
  type                   = "Block"
  source                 = "${var.source_dir}/${each.value}"
  content_md5            = filemd5("${var.source_dir}/${each.value}")
  content_type = lookup(
    local.content_types,
    lower(try(regex("\\.[^./]+$", each.value), "")),
    "application/octet-stream"
  )

  # The $web container is created by enabling the static website feature,
  # which no argument above references.
  depends_on = [azurerm_storage_account_static_website.this]
}
```

- The static website feature serves files from the special `$web` container through a dedicated web endpoint. Public anonymous blob access stays disabled (`allow_nested_items_to_be_public = false`); the web endpoint does not depend on it.
- `for_each` over `fileset()` creates one blob per file, keyed by its relative path. Adding a file adds one blob; editing a file changes its `content_md5` and triggers a re-upload of that blob only.
- The `$web` container is not referenced by any argument, so the dependency on the static website resource must be declared with `depends_on` — a legitimate case of a hidden dependency.

### outputs.tf

```hcl
output "resource_group_name" {
  description = "Name of the resource group containing the website."
  value       = azurerm_resource_group.this.name
}

output "storage_account_id" {
  description = "ID of the storage account."
  value       = azurerm_storage_account.this.id
}

output "website_url" {
  description = "Primary endpoint of the static website."
  value       = azurerm_storage_account.this.primary_web_endpoint
}

output "uploaded_files" {
  description = "Paths of the files uploaded to the website container."
  value       = sort(keys(azurerm_storage_blob.site))
}
```

### Calling the module

```hcl
# live/main.tf
terraform {
  required_version = ">= 1.11"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

variable "subscription_id" {
  type        = string
  description = "Azure subscription to deploy into."
}

module "website" {
  source = "../modules/static-website"

  storage_account_name = "acmewebsiteprod01"
  resource_group_name  = "rg-website-prod"
  source_dir           = "${path.root}/../site"

  tags = {
    Environment = "prod"
    ManagedBy   = "terraform"
  }
}

output "website_url" {
  value = module.website.website_url
}
```

- Format and validate the configuration, then deploy it:

```bash
cd live
terraform fmt -recursive ..
terraform init
terraform validate
terraform plan -out=tfplan
terraform apply tfplan
terraform output -raw website_url
```

## References

- [Modules overview](https://developer.hashicorp.com/terraform/language/modules)
- [Module sources](https://developer.hashicorp.com/terraform/language/modules/sources)
- [Standard module structure](https://developer.hashicorp.com/terraform/language/modules/develop/structure)
- [Module composition](https://developer.hashicorp.com/terraform/language/modules/develop/composition)
- [Providers within modules](https://developer.hashicorp.com/terraform/language/modules/develop/providers)
- [Publishing modules](https://developer.hashicorp.com/terraform/registry/modules/publish)
