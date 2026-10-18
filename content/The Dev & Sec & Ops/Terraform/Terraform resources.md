> A **resource** is the declaration of an infrastructure object that Terraform manages — a virtual machine, a network, a DNS record, a role assignment, a file. Terraform creates the object, records it in state, keeps it in line with the configuration, and destroys it when the declaration is removed.

- Resources are the most important element of the Terraform language. Every other construct — variables, data sources, modules, expressions — exists to configure resources.
- Each resource type is implemented by a provider (see [[Terraform providers]]). The provider documentation in the Terraform Registry lists every argument and attribute of each type.
- Objects that Terraform only reads, without managing them, are declared as data sources (see [[Terraform data sources]]).

## Resource blocks

```hcl
resource "aws_instance" "web" {
  ami           = data.aws_ami.app.id
  instance_type = "t3.small"
  subnet_id     = aws_subnet.private.id

  root_block_device {
    encrypted   = true
    volume_size = 20
  }

  tags = {
    Name = "web"
  }
}
```

- The first label is the **resource type** (`aws_instance`). Its prefix identifies the provider.
- The second label is the **local name** (`web`). It identifies the resource within the module and has no meaning outside Terraform.
- The body contains:
	- **arguments** defined by the provider schema (`ami`, `instance_type`), some required, some optional;
	- **nested blocks** defined by the schema (`root_block_device`);
	- **meta-arguments** defined by Terraform itself and available for every resource type (see [[#Meta-arguments]]).
- After creation, the resource exposes **attributes**: all arguments plus values computed by the platform, such as `id`, `arn`, or `private_ip`. Other expressions reference them as `<TYPE>.<NAME>.<ATTRIBUTE>`, for example `aws_instance.web.private_ip`.

## Resource addresses

Every resource instance has a unique address, used in plans, state commands, `-target`, `-replace`, `moved` blocks, and `import` blocks.

| Address | Refers to |
| ------- | --------- |
| `aws_instance.web` | A single resource in the root module. |
| `aws_instance.web[0]` | An instance of a resource that uses `count`. |
| `aws_instance.web["blue"]` | An instance of a resource that uses `for_each`. |
| `data.aws_ami.app` | A data source. |
| `module.network` | All resources in a module call. |
| `module.network.aws_subnet.private` | A resource inside a child module. |
| `module.app["eu"].aws_instance.web[1]` | A resource instance inside a module instance. |

- On the command line, addresses that contain quotes or brackets must be quoted for the shell:

```bash
terraform state show 'aws_instance.web["blue"]'
```

## Resource lifecycle

For each resource instance, a plan contains one of the following actions:

| Action | When it is planned |
| ------ | ------------------ |
| Create | The resource is in configuration but not in state. |
| Update in place | An argument changed and the provider can apply the change through the API. |
| Replace | An argument changed that the provider marks as requiring replacement (for example, the AMI of an instance or the name of many resources), or replacement was requested explicitly. |
| Destroy | The resource is in state but no longer in configuration. |
| Read | A data source is read during apply rather than during plan. |
| No-op | Configuration, state, and the remote object agree. |

- Replacement destroys the existing object and creates a new one. By default the old object is destroyed first; `create_before_destroy` reverses the order.
- The plan marks the attributes that cause a replacement with `# forces replacement`. How to read plan output is covered in [[Terraform CLI#Reading a plan]].
- When an attribute is computed by the platform and not yet known (for example, the ID of an object not yet created), the plan shows it as `(known after apply)`. Values that depend on it are also unknown during planning.
- If the creation of a resource fails partway (for example, a creation-time provisioner fails), Terraform marks the object as **tainted** in state and plans to replace it on the next run.

## Meta-arguments

Meta-arguments are arguments that Terraform interprets itself. They are available in every `resource` block, and most of them also in `data` and `module` blocks.

| Meta-argument | Purpose |
| ------------- | ------- |
| `depends_on` | Declare a dependency that Terraform cannot infer from references. |
| `count` | Create a number of instances from one block, addressed by index. |
| `for_each` | Create one instance per element of a map or set, addressed by key. |
| `provider` | Select a non-default provider configuration. |
| `lifecycle` | Customise create, update, replace, and destroy behaviour. |

### `depends_on`

- Terraform infers dependencies from references. A resource that uses `aws_subnet.private.id` already depends on `aws_subnet.private`.
- `depends_on` declares a dependency that exists only outside the configuration — for example, an application that requires an IAM policy to be attached before it starts, although nothing in its configuration refers to the attachment:

```hcl
resource "aws_iam_role_policy_attachment" "app_s3" {
  role       = aws_iam_role.app.name
  policy_arn = aws_iam_policy.app_s3.arn
}

resource "aws_instance" "app" {
  ami                  = data.aws_ami.app.id
  instance_type        = "t3.small"
  iam_instance_profile = aws_iam_instance_profile.app.name

  # The application reads from S3 at boot; the policy must be attached first.
  depends_on = [aws_iam_role_policy_attachment.app_s3]
}
```

- `depends_on` takes a list of references to whole resources or modules, not attributes, and only static references (no expressions).
- It should be used sparingly. It makes the dependency coarser than necessary, and on data sources and modules it causes reads to be deferred to the apply phase whenever the dependency has pending changes (see [[Terraform data sources#Dependencies]]).

### `count`

```hcl
resource "aws_instance" "worker" {
  count = var.worker_count

  ami           = data.aws_ami.app.id
  instance_type = "t3.small"

  tags = {
    Name = "worker-${count.index}"
  }
}
```

- `count` accepts a non-negative whole number. Within the block, `count.index` is the zero-based index of the current instance.
- Instances are addressed as `aws_instance.worker[0]`, `aws_instance.worker[1]`, and so on. The resource as a whole is a list: `aws_instance.worker[*].id`.
- `count = 0` creates no instances, which makes `count` the conventional way to make a resource conditional:

```hcl
resource "aws_cloudwatch_log_group" "flow_logs" {
  count = var.enable_flow_logs ? 1 : 0
  name  = "/vpc/flow-logs"
}
```

- Instances are identified by position. Removing an element from the middle of a list that drives `count` shifts the index of every following element, so Terraform plans to update or replace all of them. Use `for_each` whenever instances correspond to distinct named things.

### `for_each`

```hcl
variable "buckets" {
  type = map(object({
    versioning = bool
  }))
}

resource "aws_s3_bucket" "this" {
  for_each = var.buckets
  bucket   = "acme-${each.key}"
}

resource "aws_s3_bucket_versioning" "this" {
  for_each = { for name, cfg in var.buckets : name => cfg if cfg.versioning }

  bucket = aws_s3_bucket.this[each.key].id
  versioning_configuration {
    status = "Enabled"
  }
}
```

- `for_each` accepts a map or a set of strings. A list must be converted with `toset()`.
- Within the block, `each.key` is the map key (or the set element) and `each.value` is the map value (or, for a set, the element again).
- Instances are addressed by key, for example `aws_s3_bucket.this["logs"]`. Adding or removing a key affects only that instance.
- The resource as a whole is a map of objects. Splat expressions do not apply directly to maps; use `values(aws_s3_bucket.this)[*].arn` or a `for` expression.
- The keys must be known at plan time. Using an attribute that is computed during apply as a key causes the error "Invalid for_each argument". Keys should come from input variables or literals; computed values belong in `each.value`.
- `count` and `for_each` cannot be used in the same block.

### `provider`

- Selects an aliased provider configuration, as described in [[Terraform providers#Multiple provider configurations]]:

```hcl
resource "aws_s3_bucket" "replica" {
  provider = aws.us_east_1
  bucket   = "acme-replica"
}
```

### `lifecycle`

The `lifecycle` nested block changes how Terraform handles changes to the resource.

```hcl
resource "aws_launch_template" "app" {
  name_prefix   = "app-"
  image_id      = data.aws_ami.app.id
  instance_type = var.instance_type

  lifecycle {
    create_before_destroy = true
    ignore_changes        = [tags["LastScannedAt"]]
    replace_triggered_by  = [terraform_data.release]
  }
}
```

| Argument | Effect |
| -------- | ------ |
| `create_before_destroy` | Create the replacement before destroying the old object. |
| `prevent_destroy` | Fail any plan that would destroy the object. |
| `ignore_changes` | Ignore differences in the listed attributes (or `all`) when planning updates. |
| `replace_triggered_by` | Replace the resource when any of the referenced resources or attributes change. |
| `precondition`, `postcondition` | Validate assumptions before and guarantees after the change (see [[#Custom conditions]]). |

- **`create_before_destroy`**
	- Reduces downtime during replacement, but requires that two copies of the object can exist at once. Resources with unique names (security groups, launch templates) should use `name_prefix` or generated names to avoid collisions.
	- The setting propagates to the resource's dependencies: they also adopt create-before-destroy ordering.
- **`prevent_destroy`**
	- Protects stateful resources (databases, state buckets, KMS keys) from accidental replacement or destruction.
	- It protects only while the block is present. If the resource block is deleted from configuration, the protection disappears with it and the resource is destroyed on the next apply. To stop managing such a resource safely, use a `removed` block (see [[Terraform state#Refactoring with moved and removed blocks]]).
- **`ignore_changes`**
	- Appropriate for attributes intentionally changed outside Terraform — tags written by other tools, an auto-scaling group's `desired_capacity` changed by scaling policies.
	- `ignore_changes = all` turns Terraform into a create-only tool for that resource. It hides drift entirely and should be justified in a comment.
- **`replace_triggered_by`**
	- References managed resources or their attributes. Variables and locals cannot be referenced directly; wrap them in `terraform_data` (see [[#terraform_data]]).

## Custom conditions

Preconditions and postconditions turn assumptions into checks that fail the run with a clear message, instead of letting an invalid configuration reach the API.

```hcl
resource "aws_instance" "app" {
  ami           = data.aws_ami.app.id
  instance_type = var.instance_type
  subnet_id     = var.subnet_id

  lifecycle {
    precondition {
      condition     = data.aws_ami.app.architecture == "arm64"
      error_message = "The selected AMI must be built for arm64 to match Graviton instance types."
    }

    postcondition {
      condition     = self.public_ip == ""
      error_message = "Application instances must not receive a public IP address."
    }
  }
}
```

- A **precondition** is evaluated before the resource is planned. It typically checks inputs or data sources.
- A **postcondition** is evaluated after the resource is planned and again after it is applied. It can refer to the resource's own attributes through `self`.
- A failed condition stops the run with the `error_message`. Conditions with unknown values are deferred until the values are known.
- Custom conditions are available in `resource`, `data`, and `output` blocks. Input variables use `validation` blocks instead (see [[Terraform variables and outputs#Input variables]]), and non-blocking checks use `check` blocks (see [[Terraform testing#Check blocks]]).

## Dependencies and the resource graph

- **Implicit dependencies** are created by references. Terraform parses every expression, and each reference to another resource, data source, or module output becomes an edge in the dependency graph.
- **Explicit dependencies** are created by `depends_on`.
- Terraform creates resources in dependency order, updates them in dependency order, and destroys them in reverse order. Independent resources are processed concurrently.
- How Terraform builds and walks the graph is described in [[Terraform#Resource graph]].

Inspecting the graph:

- Render the dependency graph as an image (requires Graphviz):

```bash
terraform graph | dot -Tsvg > graph.svg
```

- Render the graph of a specific operation:

```bash
terraform graph -type=plan-destroy | dot -Tsvg > destroy-graph.svg
```

Cycles:

- A cycle (A depends on B, B depends on A) is an error. Terraform reports it as `Error: Cycle: ...` with the participating nodes.
- Cycles usually come from bidirectional references, such as two security groups that each reference the other in inline rules. They are broken by splitting the mutual part into separate resources — for example, standalone `aws_vpc_security_group_ingress_rule` resources that reference both groups.

## Timeouts

Some resource types accept a `timeouts` block that overrides how long the provider waits for long-running operations.

```hcl
resource "aws_db_instance" "main" {
  # ...

  timeouts {
    create = "60m"
    update = "80m"
    delete = "40m"
  }
}
```

- The available operations and defaults are defined per resource type in the provider documentation. A timeout does not cancel the operation on the platform side; it only stops Terraform from waiting.

## Provisioners

> **Provisioners** run scripts on the local machine or on a remote host as part of a resource's creation or destruction.

- Provisioners model actions that cannot be represented declaratively. Terraform cannot plan their effects, cannot detect drift in what they did, and does not rerun them when the script changes.
- HashiCorp describes provisioners as a last resort. Preferred alternatives are:
	- passing configuration at boot through `user_data` and cloud-init;
	- building images with the software pre-installed (Packer);
	- configuring hosts with a configuration management tool after provisioning (see [[Terraform automation#Integrating with Ansible]]);
	- using a provider resource for the action, if one exists.

### Provisioner types

| Provisioner | Purpose |
| ----------- | ------- |
| `local-exec` | Run a command on the machine running Terraform. |
| `remote-exec` | Run commands on the remote resource over SSH or WinRM. |
| `file` | Copy a file or directory to the remote resource over SSH or WinRM. |

```hcl
resource "aws_instance" "bastion" {
  ami           = data.aws_ami.app.id
  instance_type = "t3.micro"

  provisioner "file" {
    source      = "${path.module}/files/motd"
    destination = "/tmp/motd"
  }

  provisioner "remote-exec" {
    inline = [
      "sudo install -m 0644 /tmp/motd /etc/motd",
    ]
  }

  provisioner "local-exec" {
    command = "./scripts/register-host.sh"
    environment = {
      HOST_ID = self.id
      HOST_IP = self.private_ip
    }
  }
}
```

- Inside a provisioner, the parent resource is available as `self`. Referencing the resource by its own address would create a cycle.
- `remote-exec` accepts `inline` (a list of commands), `script` (a local script to upload and run), or `scripts` (several scripts in order).
- `local-exec` accepts `command`, `working_dir`, `interpreter` (for example `["/bin/bash", "-c"]`), and `environment`.
- Passing values through `environment` instead of interpolating them into `command` keeps them out of the shell's parser, which prevents values containing quotes, semicolons, or `$()` from being executed as shell syntax.

### The connection block

`remote-exec` and `file` need a `connection` block, placed in the resource (shared by all provisioners) or in an individual provisioner.

| Argument | Purpose |
| -------- | ------- |
| `type` | Select the protocol: `ssh` (default) or `winrm`. |
| `host` | Specify the address to connect to, usually `self.public_ip` or `self.private_ip`. |
| `user` | Specify the login user. |
| `host_key` | Pin the expected SSH host key of the remote host. |
| `bastion_host` | Connect through an SSH jump host. |
| `timeout` | Specify how long to wait for the connection to become available. |

- If `host_key` is not set, the SSH communicator does not verify the identity of the remote host.

### Creation-time and destroy-time provisioners

- By default, a provisioner runs once, when the resource is created. It does not run on updates.
- `when = destroy` runs the provisioner before the resource is destroyed. Destroy-time provisioners may reference only `self`, `count.index`, and `each.key`, because other objects may already be gone.
- Destroy-time provisioners do not run if the resource block has been removed from configuration together with the resource; the provisioner is removed with it.

### Failure behaviour

- `on_failure = fail` (default) aborts the apply. For a creation-time provisioner, the resource is marked as tainted and will be replaced on the next apply.
- `on_failure = continue` ignores the failure and continues.

## terraform_data

`terraform_data` is a built-in resource (Terraform 1.4 and later) that holds a value in state and participates in the resource lifecycle without managing any remote object. It requires no provider.

```hcl
# Replace the instances whenever the release version changes.
resource "terraform_data" "release" {
  input = var.release_version
}

resource "aws_instance" "app" {
  # ...
  lifecycle {
    replace_triggered_by = [terraform_data.release]
  }
}

# Run a provisioner whenever the cluster endpoint changes.
resource "terraform_data" "bootstrap" {
  triggers_replace = [aws_eks_cluster.main.endpoint]

  provisioner "local-exec" {
    command = "./scripts/bootstrap-cluster.sh"
    environment = {
      CLUSTER_NAME = aws_eks_cluster.main.name
    }
  }
}
```

- `input` stores an arbitrary value; `output` exposes the same value after apply. Changing `input` updates the resource in place.
- `triggers_replace` forces replacement (and therefore reruns creation-time provisioners) when its value changes.
- `terraform_data` supersedes `null_resource` from the `hashicorp/null` provider, which offered the same pattern through a `triggers` map. Existing `null_resource` blocks can be migrated with a `moved` block from `null_resource.<NAME>` to `terraform_data.<NAME>` (Terraform 1.9 and later).

## Ephemeral resources

> An **ephemeral resource** (Terraform 1.10 and later) is a temporary object that Terraform opens during a run, uses, and closes, without ever writing its values to the plan or the state.

```hcl
ephemeral "random_password" "db" {
  length  = 32
  special = true
}
```

- Ephemeral resources are declared with the `ephemeral` block and referenced as `ephemeral.<TYPE>.<NAME>.<ATTRIBUTE>`.
- Their lifecycle differs from managed resources: Terraform opens them when their values are needed, can renew them during long runs (for example, leases), and closes them at the end of the run. They are opened again on every plan and apply.
- Typical use cases are values that must never be persisted: generated passwords, secrets read from a secrets manager, short-lived tokens.
- Ephemeral values can be referenced only in contexts that are themselves not persisted:
	- write-only arguments of managed resources (see [[#Write-only arguments]]);
	- provider configuration blocks;
	- ephemeral variables and ephemeral outputs (see [[Terraform variables and outputs]]);
	- locals, provisioner blocks, and connection blocks.
- Assigning an ephemeral value to a normal resource argument is an error, which makes accidental persistence detectable at plan time.

## Write-only arguments

> A **write-only argument** (Terraform 1.11 and later) is a resource argument whose value is sent to the provider during apply but is never stored in the plan or the state.

```hcl
resource "aws_db_instance" "main" {
  identifier          = "orders"
  engine              = "postgres"
  instance_class      = "db.t4g.medium"
  allocated_storage   = 50
  username            = "app_admin"
  password_wo         = ephemeral.random_password.db.result
  password_wo_version = 1
}
```

- Providers expose write-only arguments by convention with a `_wo` suffix, paired with a `_wo_version` argument.
- Because Terraform never stores the value, it cannot detect when the value changes. Incrementing the `_wo_version` argument signals that the value must be sent again.
- Write-only arguments accept ephemeral values, which is their main purpose. Together with ephemeral resources they make it possible to manage a secret-bearing resource without the secret reaching state. The broader secrets strategy is covered in [[Terraform security#Secrets management]].
- Support is provider- and resource-specific; check the provider documentation for `_wo` arguments.

## References

- [Resource blocks](https://developer.hashicorp.com/terraform/language/resources/syntax)
- [Meta-arguments](https://developer.hashicorp.com/terraform/language/meta-arguments)
- [Custom conditions](https://developer.hashicorp.com/terraform/language/expressions/custom-conditions)
- [Provisioners](https://developer.hashicorp.com/terraform/language/resources/provisioners/syntax)
- [The terraform_data resource](https://developer.hashicorp.com/terraform/language/resources/terraform-data)
- [Ephemeral resources](https://developer.hashicorp.com/terraform/language/resources/ephemeral)
- [Write-only arguments](https://developer.hashicorp.com/terraform/language/resources/ephemeral/write-only)
