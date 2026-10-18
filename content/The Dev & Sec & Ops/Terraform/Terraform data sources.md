> A **data source** lets Terraform read information about an object that exists outside the current configuration — created manually, by another Terraform configuration, or by the platform itself — and use that information in expressions, without managing the object.

- Resources declared with `resource` blocks are **managed resources**: Terraform creates, updates, and destroys them. Objects declared with `data` blocks are **data resources**: Terraform only reads them.
- Each data resource is backed by a data source implemented by a provider, which defines the kind of object it reads and the arguments available for the query.
- A data source can be thought of as a `SELECT` query against the provider's API: it retrieves information and never changes anything.

## Data sources compared with resources and imports

| Aspect | Managed resource | Data source | Imported resource |
| ------ | ---------------- | ----------- | ----------------- |
| Declared with | `resource` | `data` | `resource` plus an `import` block or `terraform import` |
| Terraform creates, updates, destroys the object | Yes | No | Yes, after import |
| Object exists before Terraform runs | No | Yes | Yes |
| Recorded in state | Yes | Yes, refreshed on every run | Yes |
| Removing the block from configuration | Destroys the object | Stops reading it | Destroys the object |

- Use a data source when the object is owned by someone else (another team, another configuration, the cloud provider) and must not be changed.
- Use import when the object should come under Terraform's management (see [[Terraform state#Importing existing infrastructure]]).

## Declaring and referencing data sources

```hcl
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"
}
```

- A `data` block takes two labels: the data source type (`aws_ami`) and a local name (`ubuntu`). The pair must be unique within the module.
- The body contains **query arguments**, defined by the data source, which select the object.
- The result is referenced as `data.<TYPE>.<NAME>.<ATTRIBUTE>` — here `data.aws_ami.ubuntu.id`. The `data.` prefix distinguishes it from a managed resource of the same type and name.
- Data sources support the `count`, `for_each`, `depends_on`, `provider`, and `lifecycle` meta-arguments (the latter only for `precondition` and `postcondition`).

## Query arguments and filters

Each data source defines its own query interface. Common patterns:

- **Lookup by identifier or name** — the simplest form, used by most Azure and Google data sources:

```hcl
data "azurerm_resource_group" "shared" {
  name = "rg-shared-network"
}

data "google_compute_network" "shared" {
  name    = "shared-vpc"
  project = "acme-host-project"
}
```

- **Generic filter blocks** — AWS data sources mirror the `Filter` parameter of the EC2 `Describe*` APIs. Each `filter` block takes a `name` (an API filter name) and a list of `values`; multiple blocks are combined with logical AND, multiple values within one block with logical OR:

```hcl
data "aws_vpc" "main" {
  filter {
    name   = "tag:Name"
    values = ["main"]
  }
}
```

- **Tag and attribute arguments** — some data sources accept dedicated arguments, such as `tags` on `aws_vpc` or `most_recent` and `owners` on `aws_ami`.
- **Singular and plural data sources**
	- A singular data source (`aws_subnet`) must match exactly one object; zero or several matches are errors.
	- A plural data source (`aws_subnets`) returns a list of IDs and is used when the number of matches is not fixed:

```hcl
data "aws_subnets" "private" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.main.id]
  }

  tags = {
    Tier = "private"
  }
}

resource "aws_lb" "internal" {
  name     = "internal"
  internal = true
  subnets  = data.aws_subnets.private.ids
}
```

>[!warning]
>Image lookups by name pattern must always constrain the publisher. An `aws_ami` query with `most_recent = true` and a name filter but without `owners` matches public AMIs from any AWS account, so anyone can publish an image with a matching name and have it selected. This class of attack was published as "whoAMI" in 2025. Specify `owners` (an account ID or an alias such as `amazon`), and consider enabling the account-level Allowed AMIs setting.

## When data sources are read

- In most cases, Terraform reads a data source during the **plan** phase, after refreshing managed resources. Its results are then available to the rest of the plan.
- Terraform defers the read to the **apply** phase when:
	- at least one query argument depends on a value that is unknown until apply, such as an attribute of a resource that has not been created yet;
	- the data source depends directly on a managed resource with changes planned in the current run (through `depends_on`);
	- the data source has custom conditions and depends, directly or indirectly, on a managed resource with planned changes.
- A deferred read appears in the plan with the `<=` symbol, and every value derived from it is `(known after apply)`.
- Data sources are evaluated on every plan and every apply. Running `terraform plan` followed by `terraform apply` without a saved plan reads each data source twice, and the two results can differ if the underlying object changed in between. Applying a saved plan reuses the values from the planning step (see [[Terraform CLI#Saved plans]]).

## Dependencies

- A reference in a query argument creates an implicit dependency. In the following example, the data source cannot be read until the function app exists, and Terraform orders it correctly without `depends_on`:

```hcl
data "azurerm_function_app_host_keys" "app" {
  name                = azurerm_linux_function_app.app.name
  resource_group_name = azurerm_linux_function_app.app.resource_group_name
}
```

- `depends_on` is needed only for dependencies that are not visible in the arguments — for example, a data source that queries objects created as a side effect of another resource:

```hcl
resource "aws_eks_cluster" "main" {
  # ...
}

# The cluster creates its security group as a side effect.
data "aws_security_group" "cluster" {
  filter {
    name   = "tag:aws:eks:cluster-name"
    values = [aws_eks_cluster.main.name]
  }
}
```

  Here the reference to `aws_eks_cluster.main.name` already orders the read. If the query used only a literal tag value, `depends_on = [aws_eks_cluster.main]` would be required.
- `depends_on` on a data source has a cost: whenever the dependency has any planned change, the read is deferred to apply, and every value derived from it becomes unknown during planning. This can cascade into unnecessary in-place updates or replacements of downstream resources. Prefer references.

## Custom conditions on data sources

Postconditions on data sources validate that the object found is the one expected, before anything uses it:

```hcl
data "aws_ami" "app" {
  most_recent = true
  owners      = ["self"]

  filter {
    name   = "name"
    values = ["app-*"]
  }

  lifecycle {
    postcondition {
      condition     = self.architecture == "arm64"
      error_message = "The latest app AMI must be built for arm64."
    }

    postcondition {
      condition     = self.root_device_type == "ebs"
      error_message = "The app AMI must use an EBS root device."
    }
  }
}
```

- Placing the guarantee on the data source means every resource that uses it benefits, and the error points to the actual problem rather than to a failed API call later. Custom conditions are described in [[Terraform resources#Custom conditions]].

## Data sources in state

- Data source results are stored in state with `"mode": "data"`, and `terraform state list` shows them with the `data.` prefix.
- They are re-read on every run, so the stored copy is not authoritative; it exists so that Terraform can evaluate expressions consistently within a run and produce correct outputs.
- Anything a data source returns is persisted. A data source that reads a secret (for example, `aws_secretsmanager_secret_version` or a Vault secret) writes that secret to state in plaintext. Where an ephemeral resource of the same kind exists, it reads the value without persisting it (see [[Terraform resources#Ephemeral resources]]).

## Special-purpose data sources

| Data source | Provider | Purpose |
| ----------- | -------- | ------- |
| `terraform_remote_state` | built-in | Read the root module outputs of another configuration's state. |
| `aws_iam_policy_document` | `hashicorp/aws` | Render an IAM policy JSON document from HCL, with no API call. |
| `aws_caller_identity`, `azurerm_client_config`, `google_client_config` | cloud providers | Return the identity Terraform is running as (account, tenant, project). |
| `archive_file` | `hashicorp/archive` | Package local files into an archive. |
| `http` | `hashicorp/http` | Perform an HTTP GET request. |
| `external` | `hashicorp/external` | Run a local program and read a JSON object from its output. |
| `cloudinit_config` | `hashicorp/cloudinit` | Render a multi-part cloud-init document. |

### terraform_remote_state

- `terraform_remote_state` reads the outputs of another configuration from its backend. It is covered, together with its access-control implications and alternatives, in [[Terraform backends#Sharing state between configurations]].

### aws_iam_policy_document

- Renders policy JSON locally, with validation of the structure and automatic handling of interpolation, which is safer than hand-written JSON strings:

```hcl
data "aws_iam_policy_document" "read_logs" {
  statement {
    sid       = "ReadLogs"
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.logs.arn}/*"]
  }
}

resource "aws_iam_policy" "read_logs" {
  name   = "read-logs"
  policy = data.aws_iam_policy_document.read_logs.json
}
```

### http

- Performs a GET request during planning and exposes `status_code`, `response_headers`, and `response_body`:

```hcl
data "http" "allowed_ranges" {
  url = "https://ip-ranges.example.com/office.json"

  request_headers = {
    Accept = "application/json"
  }

  lifecycle {
    postcondition {
      condition     = self.status_code == 200
      error_message = "Could not retrieve the office IP ranges."
    }
  }
}

locals {
  office_cidrs = jsondecode(data.http.allowed_ranges.response_body).cidrs
}
```

- The configuration then depends on an external endpoint being available and returning trustworthy data at every plan.

### external

- Runs a program on the machine executing Terraform, passes the `query` map to it as a JSON object on standard input, and expects a flat JSON object of strings on standard output:

```hcl
data "external" "git" {
  program = ["bash", "${path.module}/scripts/git-info.sh"]
  query = {
    directory = path.module
  }
}

locals {
  commit = data.external.git.result.commit
}
```

```bash
#!/usr/bin/env bash
# scripts/git-info.sh
set -euo pipefail
dir=$(jq -r '.directory')
commit=$(git -C "$dir" rev-parse --short HEAD)
jq -n --arg commit "$commit" '{commit: $commit}'
```

- The program runs during `terraform plan`, not only during apply. Any configuration that contains an `external` data source executes code as soon as it is planned (see [[Terraform security#Code execution during plan]]).
- `external` is an escape hatch. Logic that can be expressed with functions or a provider should not be implemented as an external program.

### Deprecated: template_file

- The `template_file` data source of the archived `hashicorp/template` provider has been replaced by the built-in `templatefile()` function (see [[Terraform expressions and functions#String templates]]). The `template` provider has no builds for some current platforms, such as `darwin_arm64`.

## References

- [Data sources](https://developer.hashicorp.com/terraform/language/data-sources)
- [The terraform_remote_state data source](https://developer.hashicorp.com/terraform/language/state/remote-state-data)
- [Datadog Security Labs — whoAMI](https://securitylabs.datadoghq.com/articles/whoami-a-cloud-image-name-confusion-attack/)
