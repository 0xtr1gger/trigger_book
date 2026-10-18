> **Terraform state** is the record that maps each resource instance in the configuration to the real object it represents, together with the object's last known attributes and the metadata Terraform needs to plan future changes. It is stored as a JSON document, by default in `terraform.tfstate` in the working directory.

- Terraform cannot function without state. Every plan is computed from three inputs: the configuration, the state, and the current attributes of the real objects.
- Where state is stored, and how it is locked and shared, is determined by the backend (see [[Terraform backends]]).

## Purpose of state

- **Mapping configuration to real objects**
	- The configuration says that `aws_instance.web` should exist; only the state records that it corresponds to instance `i-0a1b2c3d4e5f67890`. Without that mapping, Terraform could not tell whether an object already exists and would create duplicates.
	- The mapping must be one-to-one. Two configurations (or two addresses) managing the same real object make each overwrite the other's changes.
- **Idempotency**
	- Because Terraform knows what it already created, applying the same configuration repeatedly produces no further changes once the infrastructure converges. Only resources whose recorded or refreshed attributes differ from the configuration are changed.
- **Metadata**
	- State records dependencies between resources. When a resource is removed from configuration, the configuration no longer says what depended on it; the dependencies recorded in state let Terraform destroy objects in the correct order.
	- State records the provider configuration that manages each resource and the resource schema version, which allows providers to migrate stored attributes after upgrades.
- **Performance**
	- State caches attribute values. By default Terraform refreshes every resource on each plan, but for very large configurations refreshing can be skipped (`-refresh=false`) and the cached values used instead (see [[Terraform CLI#Performance]]).
- **Outputs**
	- Root module outputs are stored in state, where `terraform output` and other configurations (`terraform_remote_state`) read them.

## State file structure

State is a versioned JSON format. Its structure is documented for reading by tools, but it must not be edited by hand except as a last resort.

```json
{
  "version": 4,
  "terraform_version": "1.11.4",
  "serial": 42,
  "lineage": "3f1c2b9e-6a8d-4c1e-9b2f-7d5e0a4c8b11",
  "outputs": {
    "bucket_arn": {
      "value": "arn:aws:s3:::acme-logs",
      "type": "string"
    }
  },
  "resources": [
    {
      "mode": "managed",
      "type": "aws_s3_bucket",
      "name": "logs",
      "provider": "provider[\"registry.terraform.io/hashicorp/aws\"]",
      "instances": [
        {
          "schema_version": 0,
          "attributes": {
            "id": "acme-logs",
            "arn": "arn:aws:s3:::acme-logs",
            "bucket": "acme-logs",
            "tags": { "Environment": "prod" }
          },
          "sensitive_attributes": [],
          "private": "eyJzY2hlbWFfdmVyc2lvbiI6IjAifQ==",
          "dependencies": ["aws_kms_key.logs"]
        }
      ]
    }
  ],
  "check_results": null
}
```

| Field | Meaning |
| ----- | ------- |
| `version` | Format version of the state file itself (currently 4). |
| `terraform_version` | Version of Terraform that last wrote the state. |
| `serial` | Counter incremented on every write; used to detect stale snapshots. |
| `lineage` | UUID assigned when the state was first created; identifies the "same" state across writes. |
| `outputs` | Root module output values and types. |
| `resources[].mode` | `managed` for resources, `data` for data sources. |
| `resources[].module` | Module path of the resource, such as `module.network` (absent for the root module). |
| `resources[].provider` | Fully qualified provider configuration that manages the resource. |
| `instances[].index_key` | Index (`count`) or key (`for_each`) of the instance, if any. |
| `instances[].attributes` | All attribute values of the object, as last read or written. |
| `instances[].sensitive_attributes` | Paths of attributes marked sensitive. |
| `instances[].private` | Opaque provider metadata, base64-encoded (for example, timeouts and schema details). |
| `instances[].dependencies` | Addresses of resources this instance depended on when it was last applied. |
| `instances[].status` | `tainted` if the object must be replaced. |

- Terraform refuses to write a snapshot whose `serial` is not greater than the stored one, or whose `lineage` differs, which protects against overwriting newer state with an older copy.
- A newer Terraform version may upgrade the state format or provider schemas when it writes state. Older versions then refuse to read it ("state snapshot was created by Terraform vX, which is newer than current vY"). This is the main reason to pin `required_version` (see [[Terraform configuration language#The terraform block]]).

## Sensitive data in state

- State contains every attribute of every managed resource and data source, in plaintext. This includes database passwords, generated private keys (`tls_private_key`), access keys, connection strings, and anything read by data sources.
- `sensitive = true` hides values in CLI output only; it has no effect on state contents.
- Anyone who can read state can read every secret the configuration handles. State must be treated as a secret in its own right: stored encrypted, access-controlled, never committed to version control. Controls are covered in [[Terraform security#Protecting state and plan files]] and [[Terraform backends#Securing state storage]].

## Refresh and drift

- During every plan and apply, Terraform **refreshes** state: it asks each provider to read the current attributes of each managed resource and updates the in-memory state with the result.
- Differences between the refreshed attributes and the previously stored ones are reported under "Objects have changed outside of Terraform". This is **drift** (see [[Infrastructure as Code#Configuration drift]]).
- The subsequent plan then proposes changes to bring the objects back to the configuration, unless the attribute is covered by `ignore_changes`.

Working with drift:

- Show only what changed outside Terraform, without proposing configuration changes:

```bash
terraform plan -refresh-only
```

- Accept the drift into state without changing any infrastructure — for example, after a legitimate manual change that will then be codified:

```bash
terraform apply -refresh-only
```

- Plan without refreshing, using stored attributes only (faster, but blind to drift):

```bash
terraform plan -refresh=false
```

- `terraform refresh` is a deprecated alias for `terraform apply -refresh-only -auto-approve`. It updates state without showing what will change and should not be used.
- If a refreshed object no longer exists (deleted outside Terraform), Terraform removes it from state and plans to create it again.

## Inspecting state

| Command | Purpose |
| ------- | ------- |
| `terraform show` | Print the current state, or a saved plan, in human-readable form. |
| `terraform show -json` | Print the current state, or a saved plan, as machine-readable JSON. |
| `terraform state list` | List the addresses of all resources in state. |
| `terraform state show <ADDRESS>` | Print the attributes of one resource instance. |
| `terraform state pull` | Print the raw state document from the backend. |

- List all resources, or only those matching an address prefix:

```bash
terraform state list
terraform state list module.network
```

- Find the address of the resource that tracks a known remote ID:

```bash
terraform state list -id=i-0a1b2c3d4e5f67890
```

- Show the attributes of one instance:

```bash
terraform state show 'aws_instance.web["blue"]'
```

- Extract information from the raw state with `jq`, for example the IDs of all resources of a type:

```bash
terraform state pull | jq -r '.resources[] | select(.type == "aws_instance") | .instances[].attributes.id'
```

## Modifying state

Commands that change state without changing infrastructure:

| Command | Purpose |
| ------- | ------- |
| `terraform state mv <SOURCE> <DESTINATION>` | Change the address of a resource or module in state. |
| `terraform state rm <ADDRESS>` | Stop tracking a resource without destroying it. |
| `terraform state replace-provider <FROM> <TO>` | Change the provider that manages resources in state. |
| `terraform state push <FILE>` | Overwrite the backend's state with a local file. |
| `terraform untaint <ADDRESS>` | Clear the tainted status of a resource. |

- Rename a resource, or move it into a module, without recreating it:

```bash
terraform state mv aws_instance.web aws_instance.app
terraform state mv aws_instance.app module.app.aws_instance.this
```

- Convert a `count` instance to a `for_each` instance:

```bash
terraform state mv 'aws_instance.web[0]' 'aws_instance.web["primary"]'
```

- Stop managing a resource while leaving the real object in place. The resource block must also be removed from configuration, or the next plan will create a new object:

```bash
terraform state rm aws_s3_bucket.legacy
```

- Preview the effect of `mv` and `rm` without writing state:

```bash
terraform state rm -dry-run aws_s3_bucket.legacy
```

- Switch resources to a fork or a renamed provider source:

```bash
terraform state replace-provider registry.terraform.io/acme/legacy registry.terraform.io/acme/platform
```

Guidelines:

- Every state-modifying command writes a backup. With the local backend it is `terraform.tfstate.backup`; remote backends rely on their own versioning.
- Run state commands only while no other operation is in progress; they acquire the state lock like any other write.
- Prefer the declarative `moved`, `removed`, and `import` blocks described below. They are reviewed in pull requests, shown in plans, and applied by the normal pipeline, whereas CLI state commands are applied immediately by whoever runs them.
- `terraform state push` overwrites remote state and bypasses most safety checks when used with `-force`. It is intended only for recovery.

## Refactoring with moved and removed blocks

### moved

A `moved` block (Terraform 1.1 and later) tells Terraform that an object previously tracked at one address is now at another. The plan shows the move instead of a destroy and create.

```hcl
# Renamed resource
moved {
  from = aws_instance.web
  to   = aws_instance.app
}

# Resource moved into a module
moved {
  from = aws_security_group.app
  to   = module.app.aws_security_group.this
}

# count instance converted to a for_each key
moved {
  from = aws_instance.worker[0]
  to   = aws_instance.worker["primary"]
}

# Whole module renamed
moved {
  from = module.web_server
  to   = module.app
}
```

- Moves are recorded in code, so every working copy and every environment applies them consistently, which is not true of `terraform state mv`.
- Module authors should keep `moved` blocks in the module after a refactoring, so that callers upgrading from an older version keep their resources. Old `moved` blocks can be removed once all callers have upgraded.
- Moves between resource types are supported only if the destination provider implements state migration for them (Terraform 1.8 and later), for example `null_resource` to `terraform_data`.
- `moved` cannot move resources between different states (different root modules). That requires removing the resource from one configuration and importing it into the other.

### removed

A `removed` block (Terraform 1.7 and later) removes a resource or module from configuration without destroying the real object.

```hcl
removed {
  from = aws_s3_bucket.legacy_logs

  lifecycle {
    destroy = false
  }
}
```

- With `destroy = false`, the plan shows that the object will be forgotten; after apply, it is no longer in state but continues to exist.
- With `destroy = true` (the default), the block documents an intentional destruction.
- `removed` is the safe way to stop managing a resource protected by `prevent_destroy`, and the declarative replacement for `terraform state rm`.

## Importing existing infrastructure

Import brings an object created outside Terraform under Terraform's management, by writing it into state at a given address.

### Import blocks

Since Terraform 1.5, imports are declared in configuration and executed as part of a normal plan and apply.

```hcl
import {
  to = aws_s3_bucket.logs
  id = "acme-logs"
}

resource "aws_s3_bucket" "logs" {
  bucket = "acme-logs"
}
```

- `to` is the destination address; `id` is the provider-specific import identifier, documented in the "Import" section of each resource type's page in the registry.
- The plan shows the resource as "will be imported", together with any changes needed to reconcile it with the configuration. Nothing is imported until apply.
- Import blocks can be removed after the import has been applied, or kept as documentation.
- `for_each` in import blocks (Terraform 1.7 and later) imports several objects at once:

```hcl
locals {
  existing_buckets = {
    logs   = "acme-logs"
    assets = "acme-assets"
  }
}

import {
  for_each = local.existing_buckets
  to       = aws_s3_bucket.this[each.key]
  id       = each.value
}

resource "aws_s3_bucket" "this" {
  for_each = local.existing_buckets
  bucket   = each.value
}
```

- Providers that implement resource identity (Terraform 1.12 and later) also accept an `identity` object instead of the string `id`.

### Generating configuration

Writing the resource block for an imported object by hand is error-prone. Terraform can generate it:

- Declare only the `import` block, then let the plan write matching resource blocks into a new file:

```bash
terraform plan -generate-config-out=generated.tf
```

- The generated code contains every argument the provider reports, including defaults and computed values. It should be reviewed, cleaned up (references instead of literal IDs, variables instead of hardcoded values), and moved into the appropriate files before apply.

### The import command

The older CLI command imports one object immediately, outside the plan workflow. The resource block must already exist.

- Import an object:

```bash
terraform import aws_s3_bucket.logs acme-logs
```

- Import into a module or a `for_each` instance (quote the address for the shell):

```bash
terraform import 'module.storage.aws_s3_bucket.this["logs"]' acme-logs
```

- Import an Azure resource, whose identifier is its full Azure Resource Manager ID:

```bash
STORAGE_ID=$(az storage account show --name acmelogs --resource-group rg-logs --query id -o tsv)
terraform import azurerm_storage_account.logs "$STORAGE_ID"
```

Azure IDs have the form `/subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RESOURCE_GROUP>/providers/Microsoft.Storage/storageAccounts/<NAME>`.

- After importing, run `terraform plan` and adjust the configuration until the plan shows no changes; only then is the import complete.

### Migrating existing estates to Terraform

- Import one bounded area at a time (a VPC, an application stack), each into its own configuration, rather than the entire account at once.
- Bulk-export tools generate configuration and import blocks for existing resources as a starting point: `aztfexport` for Azure, Terraformer for several clouds, and the configuration generation built into Terraform. Their output always needs refactoring into idiomatic modules.
- Until the import is complete and the plan is empty, prevent manual changes to the area being migrated, or the code will chase a moving target.
- Imported resources become destroyable by Terraform. Add `prevent_destroy` to critical ones during migration.

## Replacing resources

- Force the replacement of a specific instance in the next plan, for example a VM whose disk is corrupted:

```bash
terraform plan -replace='aws_instance.web["blue"]'
terraform apply -replace='aws_instance.web["blue"]'
```

- `-replace` is shown in the plan and applies only to that run. It supersedes `terraform taint`, which marked the resource as tainted in state immediately, without review. `terraform untaint` remains available to clear a taint set by a failed provisioner.

## Workspaces

> A **CLI workspace** is a named instance of state associated with the same configuration and backend. Each workspace has its own state file, so one configuration can manage several independent copies of its infrastructure.

- Every working directory starts with the `default` workspace, which cannot be deleted.
- Changes in one workspace do not affect resources tracked by another. If Terraform believes `aws_instance.api` exists in `dev`, it has no knowledge of it in `prod`; selecting `prod` and applying creates a separate instance there.
- The current workspace name is available as `terraform.workspace` and is commonly used to vary names and sizes:

```hcl
locals {
  environment   = terraform.workspace
  instance_type = terraform.workspace == "prod" ? "m7g.large" : "t4g.small"
}

resource "aws_s3_bucket" "logs" {
  bucket = "acme-logs-${terraform.workspace}"
}
```

| Command | Purpose |
| ------- | ------- |
| `terraform workspace list` | List workspaces, marking the current one with `*`. |
| `terraform workspace show` | Print the name of the current workspace. |
| `terraform workspace new <NAME>` | Create a workspace and switch to it. |
| `terraform workspace select <NAME>` | Switch to an existing workspace. |
| `terraform workspace select -or-create <NAME>` | Switch to a workspace, creating it if needed (Terraform 1.4 and later). |
| `terraform workspace delete <NAME>` | Delete an empty workspace. |

- `terraform workspace delete` refuses to delete a workspace whose state still tracks resources. `-force` deletes the workspace anyway; the resources are **not** destroyed but become orphaned — they keep running and are no longer tracked by any state. Run `terraform destroy` in the workspace before deleting it.
- The `TF_WORKSPACE` environment variable selects a workspace without running `select`, which is convenient in pipelines.

### Workspace storage

| Backend | Location of a non-default workspace's state |
| ------- | ------------------------------------------- |
| `local` | `terraform.tfstate.d/<WORKSPACE>/terraform.tfstate` |
| `s3` | `env:/<WORKSPACE>/<KEY>` (prefix configurable with `workspace_key_prefix`) |
| `azurerm` | Blob `<KEY>env:<WORKSPACE>` in the configured container |
| `gcs` | Object `<PREFIX>/<WORKSPACE>.tfstate` |
| `kubernetes` | Secret `tfstate-<WORKSPACE>-<SECRET_SUFFIX>` |

### Limitations

- All workspaces of a configuration share the same backend, and therefore the same access controls. Anyone who can work in `dev` can read and write `prod` state. Workspaces do not provide isolation between environments with different trust levels.
- All workspaces share the same code. Differences between environments must be expressed through `terraform.workspace` conditionals, which grow unwieldy when environments differ structurally.
- The current workspace is invisible in the code and easy to forget on the command line, which makes applying to the wrong environment a realistic mistake.
- For these reasons, workspaces suit short-lived copies of the same infrastructure (feature branches, test environments), while long-lived environments are usually separated by directory and backend (see [[Terraform project structure#Environment separation]]).
- HCP Terraform also uses the word "workspace", for a different concept: a fully separate unit with its own state, variables, permissions, and runs (see [[Terraform automation#HCP Terraform and Terraform Enterprise]]).

## State backup and recovery

- **Local backups** — the local backend writes the previous state to `terraform.tfstate.backup` before every write. The `-backup` option of state commands controls the path.
- **Backend versioning** — for remote state, object versioning in the storage service (S3 versioning, Azure blob versioning, GCS object versioning) is the primary recovery mechanism and should always be enabled (see [[Terraform backends#Securing state storage]]).
- **HCP Terraform** keeps every state version and allows rolling back to any of them.

Restoring a previous version from S3:

- List the stored versions of the state object:

```bash
aws s3api list-object-versions \
  --bucket acme-tfstate-prod \
  --prefix network/terraform.tfstate \
  --query 'Versions[].[VersionId,LastModified,Size]' --output table
```

- Download a specific version and inspect it:

```bash
aws s3api get-object \
  --bucket acme-tfstate-prod \
  --key network/terraform.tfstate \
  --version-id <VERSION_ID> restored.tfstate
jq '{serial, lineage, terraform_version, resources: (.resources | length)}' restored.tfstate
```

- Push it back. Because its `serial` is lower than the current one, Terraform refuses the push unless the serial is raised above the current value or `-force` is used:

```bash
terraform state push restored.tfstate
```

Recovery scenarios:

| Situation | Approach |
| --------- | -------- |
| A state write was interrupted or the file is corrupted | Restore the latest valid version from backend versioning or the local backup. |
| State was overwritten by a stale copy | Restore the newest version; compare `serial` values to identify it. |
| State is lost entirely and no version survives | Recreate the resource blocks and import every object again. |
| Resources were deleted manually | Run `terraform plan -refresh-only` to remove them from state, or `apply` to recreate them. |
| A run crashed during apply | Terraform writes `errored.tfstate` locally when it cannot persist state to the backend; push it once the backend is reachable. |

## References

- [State](https://developer.hashicorp.com/terraform/language/state)
- [Refactoring with moved blocks](https://developer.hashicorp.com/terraform/language/modules/develop/refactoring)
- [Import](https://developer.hashicorp.com/terraform/language/import)
- [Generating configuration](https://developer.hashicorp.com/terraform/language/import/generating-configuration)
- [Workspaces](https://developer.hashicorp.com/terraform/language/state/workspaces)
- [terraform state commands](https://developer.hashicorp.com/terraform/cli/commands/state)
