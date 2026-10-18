> The **Terraform language** is the declarative configuration language in which Terraform configurations are written. It is built on the **HashiCorp Configuration Language (HCL)**, a structured syntax shared by several HashiCorp tools, extended with Terraform-specific block types, expressions, and functions.

- A Terraform configuration describes infrastructure objects and the relationships between them. It does not describe the steps to create them; ordering is derived from dependencies (see [[Terraform resources#Dependencies and the resource graph]]).
- This note covers files, syntax, block types, and the `terraform` block. Expressions, operators, and functions are covered in [[Terraform expressions and functions]].

## Configuration files

- Terraform code is stored in plain-text files with the `.tf` extension. An equivalent JSON form uses the `.tf.json` extension (see [[#JSON syntax]]).
- Files must be encoded in UTF-8. Unix (LF) and Windows (CRLF) line endings are both accepted; `terraform fmt` normalises them to LF.
- Terraform evaluates configuration one directory at a time. A directory of `.tf` files is a **module**; the directory where Terraform is run is the **root module** (see [[Terraform modules]]).
- All `.tf` and `.tf.json` files in a directory are loaded and merged into a single configuration. The division into files is purely for human organisation: there is no import mechanism and file order has no meaning.
- Each object must be defined exactly once per module. Declaring two `resource "aws_instance" "web"` blocks in different files is an error.
- Subdirectories are not loaded automatically. They are separate modules and must be called explicitly with a `module` block.
- Files with other extensions are ignored by configuration loading, with three exceptions that Terraform treats specially:
	- `*.tfvars` and `*.tfvars.json` — variable definition files (see [[Terraform variables and outputs#Assigning values to root module variables]]);
	- `*.tftest.hcl` — test files (see [[Terraform testing#The terraform test framework]]);
	- `.terraform.lock.hcl` — the dependency lock file (see [[Terraform providers#Dependency lock file]]).

The conventional file layout of a module is described in [[Terraform project structure#File layout]].

### Override files

- Files named `override.tf`, `override.tf.json`, or ending in `_override.tf` / `_override.tf.json` are **override files**. Terraform loads them after all other files and merges their contents into existing blocks instead of treating them as duplicates.
- For each block in an override file, Terraform finds the block with the same type and labels in the normal files and replaces the arguments set in the override.

```hcl
# main.tf
resource "aws_instance" "web" {
  instance_type = "t3.micro"
  ami           = "ami-0abcdef1234567890"
}

# override.tf
resource "aws_instance" "web" {
  instance_type = "t3.large"
}
```

- Override files are intended for generated or machine-local adjustments. They make the effective configuration hard to read, so most `.gitignore` templates exclude them (see [[Terraform project structure#Version control hygiene]]).

## Syntax

### Blocks and arguments

The language has two basic constructs: **arguments** and **blocks**.

```hcl
resource "aws_vpc" "main" {     # block type "resource", two labels
  cidr_block = "10.0.0.0/16"    # argument: name = expression

  tags = {                      # argument whose value is a map
    Name = "main"
  }
}
```

- An **argument** assigns the value of an expression to a name: `<IDENTIFIER> = <EXPRESSION>`. Within one block, each argument can be set only once.
- A **block** is a container with a type, zero or more labels, and a body enclosed in braces: `<TYPE> "<LABEL>" "<LABEL>" { <BODY> }`. The number of labels is fixed for each block type: `resource` takes two, `variable` takes one, `locals` takes none.
- Blocks can contain arguments and nested blocks. Nested blocks may repeat (for example, several `ingress` blocks in a security group), whereas arguments may not.
- The distinction between a map argument (`tags = { ... }`) and a nested block (`ingress { ... }`) is defined by the provider schema. A nested block cannot be assigned with `=`, and a map argument cannot be written as a block.

### Identifiers

- Argument names, block type names, and the names of resources, variables, and outputs are identifiers.
- Identifiers can contain letters, digits, underscores, and hyphens, and must not begin with a digit. By convention, Terraform code uses lowercase `snake_case` (see [[Terraform project structure#Naming conventions]]).

### Comments

Three comment syntaxes are supported:

```hcl
# Single-line comment (the idiomatic form)
// Single-line comment, C++ style
/*
   Multi-line comment
*/
```

- `terraform fmt` does not convert between styles, but the HashiCorp style guide recommends `#` for all single-line comments.
- Comments should explain intent and non-obvious constraints (why a value was chosen, which ticket introduced an exception), not restate what the code declares.
- Comments are also where static analysis suppressions are written (see [[Terraform security#Static analysis]]).

### Formatting

- Indentation is two spaces per nesting level.
- Consecutive single-line arguments at the same level align their equals signs.
- `terraform fmt` rewrites files to the canonical style (see [[Terraform CLI#Validating and formatting]]).

## Top-level blocks

| Block | Labels | Purpose |
| ----- | ------ | ------- |
| `terraform` | none | Configure Terraform itself: version requirements, providers, backend, experiments. |
| `provider` | provider local name | Configure a provider instance (region, credentials, defaults). |
| `resource` | type, name | Declare an infrastructure object that Terraform manages. |
| `data` | type, name | Read information about an object that Terraform does not manage. |
| `ephemeral` | type, name | Open a temporary object (for example, a secret or a token) whose values are never persisted. |
| `variable` | name | Declare an input variable of the module. |
| `output` | name | Declare a value that the module exports. |
| `locals` | none | Define named local values. |
| `module` | name | Call a child module. |
| `moved` | none | Record that a resource or module address has changed. |
| `removed` | none | Remove a resource from management, optionally without destroying it. |
| `import` | none | Bring an existing object under management. |
| `check` | name | Define a continuous validation assertion that reports warnings. |

Each block type is covered in the note that owns its concept:

- `provider` in [[Terraform providers]];
- `resource` and `ephemeral` in [[Terraform resources]];
- `data` in [[Terraform data sources]];
- `variable`, `output`, and `locals` in [[Terraform variables and outputs]];
- `module` in [[Terraform modules]];
- `moved`, `removed`, and `import` in [[Terraform state]];
- `check` in [[Terraform testing#Check blocks]].

## The terraform block

The `terraform` block configures the behaviour of Terraform for the module. Only constant values are allowed inside it: it cannot reference variables, locals, or resource attributes, because it is evaluated before any of those exist.

```hcl
terraform {
  required_version = ">= 1.11, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.7"
    }
  }

  backend "s3" {
    bucket       = "acme-tfstate-prod"
    key          = "network/terraform.tfstate"
    region       = "eu-central-1"
    use_lockfile = true
  }
}
```

| Setting | Purpose |
| ------- | ------- |
| `required_version` | Constrain the Terraform CLI versions allowed to run the configuration. |
| `required_providers` | Declare each provider's source address and version constraint (see [[Terraform providers#Provider requirements]]). |
| `backend` | Configure where state is stored (see [[Terraform backends]]). |
| `cloud` | Connect the configuration to HCP Terraform or Terraform Enterprise instead of a backend (see [[Terraform backends#HCP Terraform]]). |
| `experiments` | Opt in to experimental language features in alpha builds. |
| `provider_meta` | Pass module-specific metadata to a provider, used by some providers for usage attribution. |

- `required_version` is checked before anything else. If the running CLI does not satisfy it, every command fails immediately, which prevents an older or newer binary from upgrading the state format unexpectedly.
- Every module, including child modules, may declare its own `required_version` and `required_providers`. Terraform combines the constraints of all modules and selects versions that satisfy all of them.
- A configuration can contain several `terraform` blocks in different files (for example, `versions.tf` and `backend.tf`). Only one `backend` or `cloud` block may exist in the root module.

## Version constraints

Version constraints are strings used in `required_version`, provider `version`, and registry module `version` arguments.

| Operator | Meaning | Example |
| -------- | ------- | ------- |
| `=` or no operator | Allow exactly this version. | `= 1.11.4`, `1.11.4` |
| `!=` | Exclude this version. | `!= 6.2.0` |
| `>`, `>=`, `<`, `<=` | Allow versions in the given direction. | `>= 1.10` |
| `~>` | Allow only the rightmost specified component to increase (pessimistic constraint). | `~> 6.0` |

- Multiple constraints are combined with commas, and all must be satisfied: `">= 1.11, < 2.0.0"`.
- The pessimistic operator depends on how many components are written:
	- `~> 6.0` allows `6.0` and later `6.x` releases, but not `7.0`;
	- `~> 6.0.1` allows `6.0.1` and later `6.0.x` patch releases, but not `6.1.0`.
- Pre-release versions (for example, `1.12.0-beta1`) match only an exact `=` constraint.
- Recommended practice:
	- **root modules** — use `~>` on the major version for providers and rely on the dependency lock file for exact pinning;
	- **reusable modules** — declare only minimum versions (`>= 5.0`) so that callers are not prevented from upgrading.

The pinning policy across a codebase is covered in [[Terraform project structure#Version pinning]].

## JSON syntax

Every construct of the native syntax has a JSON equivalent, intended for configuration generated by other programs.

```json
{
  "resource": {
    "aws_s3_bucket": {
      "logs": {
        "bucket": "acme-logs-${var.environment}",
        "tags": { "ManagedBy": "terraform" }
      }
    }
  },
  "variable": {
    "environment": { "type": "string" }
  }
}
```

- Block labels become nested object keys.
- String values are still parsed as templates, so `${...}` interpolation works.
- A property named `"//"` is treated as a comment and ignored.
- JSON and native files can coexist in the same module.

## References

- [Terraform language documentation](https://developer.hashicorp.com/terraform/language)
- [Terraform block reference](https://developer.hashicorp.com/terraform/language/terraform)
- [Version constraints](https://developer.hashicorp.com/terraform/language/expressions/version-constraints)
- [HCL native syntax specification](https://github.com/hashicorp/hcl/blob/main/hclsyntax/spec.md)
