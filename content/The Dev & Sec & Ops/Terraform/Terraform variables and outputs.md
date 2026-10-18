---
created: 2026-10-05
updated: 2026-10-05
---
> **Input variables**, **local values**, and **output values** are the named values of a Terraform module. Input variables are the module's parameters, local values are its internal named expressions, and output values are its return values.

| Kind | Declared with | Referenced as | Analogy |
| ---- | ------------- | ------------- | ------- |
| Input variable | `variable` block | `var.<NAME>` | Function argument |
| Local value | `locals` block | `local.<NAME>` | Local variable inside a function |
| Output value | `output` block | `module.<MODULE>.<NAME>` (from the caller) | Function return value |

- Parameterisation makes one configuration usable for several environments, regions, or tenants, and makes modules reusable.
- Values flow into a module only through input variables and out of it only through outputs (see [[#Values across module boundaries]]).

## Input variables

### Declaring a variable

```hcl
variable "instance_type" {
  type        = string
  description = "EC2 instance type for the application servers."
  default     = "t3.small"
}
```

| Argument | Purpose |
| -------- | ------- |
| `type` | Constrain the accepted type of value. |
| `description` | Document the variable for users and for generated documentation. |
| `default` | Provide a value used when none is assigned; a variable without `default` is required. |
| `validation` | Define rules the value must satisfy. |
| `sensitive` | Redact the value in CLI output. |
| `ephemeral` | Prevent the value from being stored in plan or state files. |
| `nullable` | Specify whether `null` is an acceptable value (default `true`). |

- The variable name is the block label. Names `source`, `version`, `providers`, `count`, `for_each`, `lifecycle`, `depends_on`, and `locals` are reserved because they conflict with `module` block meta-arguments.
- Within the module, the value is referenced as `var.instance_type`.
- `default` must be a literal value; it cannot reference other variables, locals, or resources.
- Every variable should have a `type` and a `description`. Both are used by `terraform-docs` and by readers of the module (see [[Terraform modules#Documenting modules]]).

### Type constraints

**Primitive types**

| Type | Values | Example |
| ---- | ------ | ------- |
| `string` | A sequence of Unicode characters, always written in double quotes. | `"eu-central-1"` |
| `number` | Whole and fractional numbers. | `3`, `0.5` |
| `bool` | `true` or `false`. | `true` |

**Collection types** — all elements have the same type:

| Type | Values | Example |
| ---- | ------ | ------- |
| `list(T)` | An ordered sequence, indexed from zero. | `["a", "b"]` |
| `set(T)` | An unordered collection of unique values. | `toset(["a", "b"])` |
| `map(T)` | A collection of values identified by string keys. | `{ env = "prod", team = "core" }` |

**Structural types** — elements may have different types:

| Type | Values | Example |
| ---- | ------ | ------- |
| `object({...})` | A fixed set of named attributes, each with its own type. | `{ name = "web", port = 443 }` |
| `tuple([...])` | A fixed-length sequence where each position has its own type. | `["web", 443, true]` |

**The `any` placeholder**

- `any` accepts a value of any type, which Terraform infers from the value assigned. `list(any)` still requires all elements to share one type.
- `any` disables type checking at the module boundary and should be avoided in reusable modules except for genuinely free-form data.

Examples:

```hcl
variable "vm_count" {
  type        = number
  description = "Number of application VMs."
  default     = 2
}

variable "enable_diagnostics" {
  type        = bool
  description = "Whether to enable boot diagnostics on the VMs."
  default     = true
}

variable "availability_zones" {
  type        = list(string)
  description = "Availability zones to distribute instances across."
  default     = ["eu-central-1a", "eu-central-1b"]
}

variable "tags" {
  type        = map(string)
  description = "Tags applied to every resource."
  default = {
    Environment = "dev"
    Owner       = "platform-team"
  }
}

variable "vm" {
  type = object({
    size           = string
    admin_username = string
    os_disk_gb     = number
  })
  description = "Virtual machine sizing and login settings."
}
```

### Optional object attributes

- Attributes of an object type can be marked optional with `optional(<TYPE>, <DEFAULT>)` (Terraform 1.3 and later). If the caller omits the attribute, the default applies; without a default, the attribute is `null`.

```hcl
variable "buckets" {
  type = map(object({
    versioning     = optional(bool, true)
    force_destroy  = optional(bool, false)
    lifecycle_days = optional(number)
    tags           = optional(map(string), {})
  }))
  description = "Buckets to create, keyed by bucket suffix."
}
```

```hcl
buckets = {
  logs   = { lifecycle_days = 90 }
  assets = { versioning = false }
}
```

- Optional attributes allow rich configuration objects without forcing callers to specify every field.

### Type conversion

- Terraform converts values automatically where the conversion is unambiguous: the string `"5"` to the number `5`, a tuple to a list, an object to a map. Conversions that would lose information, such as an object with mixed attribute types to `map(string)`, fail.
- Values assigned on the command line or in environment variables are strings, and are converted to the declared type. Complex types must then be written in HCL syntax: `-var='zones=["a","b"]'`.

### Validation

`validation` blocks reject invalid values with a clear message before planning.

```hcl
variable "environment" {
  type        = string
  description = "Deployment environment."

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be one of: dev, staging, prod."
  }
}

variable "vpc_cidr" {
  type        = string
  description = "IPv4 CIDR block of the VPC."

  validation {
    condition     = can(cidrnetmask(var.vpc_cidr))
    error_message = "vpc_cidr must be a valid IPv4 CIDR block."
  }

  validation {
    condition     = tonumber(split("/", var.vpc_cidr)[1]) <= 20
    error_message = "vpc_cidr must be /20 or larger to fit all subnets."
  }
}
```

- `condition` must evaluate to `true` for a valid value. `can()` converts an error into `false`, which makes it the standard tool for format checks.
- A variable can have several `validation` blocks; all are evaluated.
- Since Terraform 1.9, conditions may reference other variables, data sources, and locals, not only the variable being validated.
- Validation runs on every plan, so it also protects against invalid values in `.tfvars` files and pipeline inputs.

### Sensitive variables

```hcl
variable "db_password" {
  type        = string
  description = "Master password of the database."
  sensitive   = true
}
```

- A sensitive value is shown as `(sensitive value)` in plan and apply output, and the sensitivity propagates to every expression and resource attribute derived from it.
- `sensitive` affects display only. The value is still written in plaintext to state, and to saved plan files, wherever it is used. Preventing persistence requires ephemeral values (see below and [[Terraform security#Secrets management]]).
- A sensitive value used in a resource argument that the provider does not mark sensitive still appears redacted, because Terraform tracks sensitivity through expressions.
- `nonsensitive()` removes the marking. It should be used only for values that are provably not secret (for example, a hash of a secret).

### Ephemeral variables

```hcl
variable "bootstrap_token" {
  type      = string
  sensitive = true
  ephemeral = true
}
```

- An ephemeral variable (Terraform 1.10 and later) is never written to the plan or the state.
- It can be referenced only in ephemeral contexts: write-only arguments, provider configuration, ephemeral resources, other ephemeral variables and outputs, locals, provisioners, and connection blocks (see [[Terraform resources#Ephemeral resources]]).
- Because a saved plan does not contain ephemeral values, they must be supplied again when the plan is applied.

### Nullable

- By default, a caller can pass `null` explicitly, and the variable then has the value `null` even if a `default` exists.
- `nullable = false` makes Terraform substitute the default when `null` is passed and reject `null` for required variables. This is useful in modules whose callers forward optional values conditionally:

```hcl
variable "retention_days" {
  type     = number
  default  = 30
  nullable = false
}
```

## Assigning values to root module variables

Variables of child modules are set in the `module` block (see [[Terraform modules#Calling a module]]). Variables of the root module can be set in several ways:

- Pass individual values on the command line:

```bash
terraform plan -var="environment=prod" -var='availability_zones=["eu-central-1a","eu-central-1b"]'
```

- Pass a variable definitions file:

```bash
terraform plan -var-file="environments/prod.tfvars"
```

- Set environment variables named `TF_VAR_<variable name>`:

```bash
export TF_VAR_environment=prod
terraform plan
```

- Let Terraform load `terraform.tfvars`, `terraform.tfvars.json`, `*.auto.tfvars`, and `*.auto.tfvars.json` files from the root module directory automatically.
- Enter values interactively: Terraform prompts for required variables that have no value, unless input is disabled with `-input=false` or `TF_INPUT=0` (as it should be in automation, where a prompt would hang the job).
- In HCP Terraform, set workspace variables or variable sets (see [[Terraform automation#HCP Terraform and Terraform Enterprise]]).

### Variable definitions files

A `.tfvars` file contains only assignments, in HCL syntax:

```hcl
# environments/prod.tfvars
environment        = "prod"
instance_type      = "m7g.large"
availability_zones = ["eu-central-1a", "eu-central-1b", "eu-central-1c"]

tags = {
  Environment = "prod"
  CostCenter  = "1042"
}
```

The JSON form, `.tfvars.json`, holds a single object:

```json
{
  "environment": "prod",
  "availability_zones": ["eu-central-1a", "eu-central-1b", "eu-central-1c"]
}
```

- Variable files separate configuration logic from per-environment data and avoid long lists of `-var` options.
- A common layout keeps one file per environment and passes it explicitly with `-var-file`, rather than relying on auto-loaded files whose presence is easy to overlook.
- Variable files are committed to version control when they contain only non-secret data. Files that would contain secrets should not exist; secrets belong in a secrets manager or in ephemeral inputs (see [[Terraform security#Secrets management]]).
- Assigning a value to a variable that is not declared produces a warning for files and an error for `-var`.

## Variable definition precedence

When the same variable is assigned in several places, Terraform applies them in the following order, from lowest to highest priority. Later sources override earlier ones.

1. Environment variables `TF_VAR_<NAME>`.
2. `terraform.tfvars`.
3. `terraform.tfvars.json`.
4. `*.auto.tfvars` and `*.auto.tfvars.json`, processed in lexical order of their file names.
5. `-var` and `-var-file` options, processed in the order they appear on the command line (in HCP Terraform, workspace variables take this position).

- The variable's `default` applies only if none of these sources assigns a value.
- Because `-var` and `-var-file` share one level, `-var-file=prod.tfvars -var="instance_type=t3.large"` uses `t3.large`, while the reverse order uses the value from the file.

## Local values

Local values assign a name to an expression, to avoid repetition and to give intermediate results a meaningful name.

```hcl
locals {
  name_prefix = "${var.project}-${var.environment}"

  common_tags = merge(var.tags, {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
  })

  private_subnets = {
    for index, zone in var.availability_zones :
    zone => cidrsubnet(var.vpc_cidr, 4, index)
  }
}

resource "aws_subnet" "private" {
  for_each          = local.private_subnets
  vpc_id            = aws_vpc.main.id
  availability_zone = each.key
  cidr_block        = each.value
  tags              = merge(local.common_tags, { Name = "${local.name_prefix}-${each.key}" })
}
```

- Locals are declared in one or more `locals` blocks (plural) and referenced as `local.<NAME>` (singular).
- Unlike variable defaults, locals can reference variables, resource attributes, data sources, other locals, and function calls.
- Locals are visible only within the module that declares them; they cannot be set from outside.
- Locals are evaluated lazily as part of the graph. A local that references a resource attribute is unknown until that attribute is known.
- Overuse hides where values come from. A local is justified when an expression is used more than once or when naming it clarifies intent.

## Output values

```hcl
output "vpc_id" {
  description = "ID of the VPC."
  value       = aws_vpc.main.id
}

output "private_subnet_ids" {
  description = "IDs of the private subnets, keyed by availability zone."
  value       = { for zone, subnet in aws_subnet.private : zone => subnet.id }
}
```

| Argument | Purpose |
| -------- | ------- |
| `value` | Specify the expression whose result is exported (required). |
| `description` | Document the output. |
| `sensitive` | Redact the value in CLI output. |
| `ephemeral` | Export an ephemeral value from a child module without persisting it. |
| `depends_on` | Declare dependencies that the value expression does not express. |
| `precondition` | Validate a guarantee before the output is recorded. |

- In a child module, outputs are the only values its caller can access, as `module.<NAME>.<OUTPUT>`.
- In the root module, outputs are printed after `terraform apply`, saved in state, available through `terraform output`, and readable by other configurations through `terraform_remote_state` (see [[Terraform backends#Sharing state between configurations]]).
- `terraform plan` shows planned changes to root outputs under "Changes to Outputs".

### Sensitive outputs

```hcl
output "db_connection_string" {
  value     = "postgresql://${aws_db_instance.main.username}@${aws_db_instance.main.endpoint}/orders"
  sensitive = true
}
```

- An output whose value contains a sensitive value must itself be marked `sensitive`, or Terraform reports an error. This prevents accidental disclosure through output.
- Sensitive outputs are hidden in the summary printed after apply, but `terraform output -json` and `terraform output -raw <NAME>` print them in plaintext, and they are stored in plaintext in state.
- Ephemeral outputs (`ephemeral = true`) are permitted only in child modules. They pass ephemeral values to the caller without storing them; root modules cannot have ephemeral outputs because root outputs are persisted.

### Preconditions on outputs

```hcl
output "api_url" {
  value = "https://${aws_lb.api.dns_name}"

  precondition {
    condition     = !aws_lb.api.internal
    error_message = "The API load balancer must be internet-facing."
  }
}
```

### Reading outputs

- Print all root module outputs:

```bash
terraform output
```

- Print one output as raw text, without quotes, for use in scripts:

```bash
terraform output -raw vpc_id
```

- Print all outputs as JSON, including sensitive values:

```bash
terraform output -json | jq -r '.private_subnet_ids.value | to_entries[] | "\(.key) \(.value)"'
```

## Values across module boundaries

| Aspect | Root module variables | Child module variables |
| ------ | --------------------- | ---------------------- |
| Declared in | `variables.tf` of the root module | `variables.tf` of the child module |
| Values supplied by | CLI options, `.tfvars` files, environment variables, HCP Terraform | Arguments of the calling `module` block |
| Visibility | The root module only | The child module only |
| Passing to other modules | Must be passed explicitly as module arguments | Must be passed explicitly, or exposed as outputs |

- Variables are never inherited. A child module sees only the values its caller passes as arguments, and a caller sees only the child's outputs.
- This strict interface makes modules self-contained and makes data flow explicit in the graph: an argument that references `module.network.vpc_id` creates a dependency on the network module's resources.

## References

- [Input variables](https://developer.hashicorp.com/terraform/language/values/variables)
- [Local values](https://developer.hashicorp.com/terraform/language/values/locals)
- [Output values](https://developer.hashicorp.com/terraform/language/values/outputs)
- [Type constraints](https://developer.hashicorp.com/terraform/language/expressions/type-constraints)
