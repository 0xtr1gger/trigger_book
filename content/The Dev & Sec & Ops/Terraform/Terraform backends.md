---
created: 2026-10-05
updated: 2026-10-05
---
> A **backend** defines where Terraform stores its state and, for most backend types, how the state is locked during operations. The backend is configured in the root module and applies to every workspace of that configuration.

- The default backend is `local`, which keeps state in a file on disk. Remote backends store state in an object store, a database, or a service, so that several people and pipelines can work with the same state.
- What state contains and how it is used is described in [[Terraform state]].

## Local and remote backends

| Aspect | Local backend | Remote backend |
| ------ | ------------- | -------------- |
| Location | `terraform.tfstate` in the working directory | Object storage, database, or HCP Terraform |
| Collaboration | Only the machine that holds the file | Anyone with access to the backend |
| Locking | OS file lock on the local machine only | Backend-specific distributed lock, if supported |
| Encryption at rest | Depends on the local disk | Provided by the storage service |
| Versioning and recovery | `terraform.tfstate.backup` only | Storage versioning, state history |
| Suitable for | Experiments, single-user projects | Teams, CI/CD, any shared or production infrastructure |

- Local state cannot be used reliably by CI/CD: each pipeline run starts on a fresh runner and would see no state at all, so Terraform would try to create everything again.
- Committing `terraform.tfstate` to a repository is not a substitute for a remote backend. It exposes every secret in state to everyone with repository access, provides no locking, and lets runs operate on stale copies (see [[Terraform project structure#Version control hygiene]]).

The local backend accepts two optional settings:

```hcl
terraform {
  backend "local" {
    path          = "state/terraform.tfstate"
    workspace_dir = "state/workspaces"
  }
}
```

## Configuring a backend

```hcl
terraform {
  backend "s3" {
    bucket       = "acme-tfstate-prod"
    key          = "network/terraform.tfstate"
    region       = "eu-central-1"
    encrypt      = true
    use_lockfile = true
  }
}
```

- The backend is declared with a `backend "<TYPE>"` block inside the `terraform` block, conventionally in `backend.tf`. Only one backend may be configured per root module.
- Child modules cannot declare backends; their resources are stored in the root module's state.
- Backend blocks cannot use variables, locals, or references. They are evaluated before the rest of the configuration, so every value must be a literal. An attempt produces "Variables may not be used here". (OpenTofu allows variables and locals that can be evaluated early.)
- Changing the backend configuration requires re-running `terraform init` (see [[#Migrating state between backends]]).
- Credentials are deliberately omitted from all backend examples in this note.

### Partial configuration

Because backend blocks cannot be parameterised, values that differ per environment are supplied at initialisation time instead. The block in code is left empty or partially filled:

```hcl
terraform {
  backend "s3" {}
}
```

The remaining settings come from a file or from command-line options:

```hcl
# backends/prod.s3.tfbackend
bucket       = "acme-tfstate-prod"
key          = "network/terraform.tfstate"
region       = "eu-central-1"
encrypt      = true
use_lockfile = true
```

- Initialise with a backend configuration file:

```bash
terraform init -backend-config=backends/prod.s3.tfbackend
```

- Initialise with individual key-value pairs:

```bash
terraform init \
  -backend-config="bucket=acme-tfstate-prod" \
  -backend-config="key=network/terraform.tfstate" \
  -backend-config="region=eu-central-1"
```

- The `.tfbackend` extension is the recommended convention for backend configuration files.
- The effective backend configuration, including every value passed with `-backend-config`, is cached in plaintext in `.terraform/terraform.tfstate` and embedded in saved plan files. Only non-secret values belong there.

## Backend types

### S3

Stores state as an object in an Amazon S3 bucket (or an S3-compatible store).

```hcl
terraform {
  backend "s3" {
    bucket       = "acme-tfstate-prod"
    key          = "network/terraform.tfstate"
    region       = "eu-central-1"
    encrypt      = true
    kms_key_id   = "arn:aws:kms:eu-central-1:111111111111:key/0f1e2d3c-4b5a-6978-8091-a2b3c4d5e6f7"
    use_lockfile = true
  }
}
```

| Setting | Purpose |
| ------- | ------- |
| `bucket`, `key`, `region` | Identify the bucket and the object key of the state. |
| `encrypt` | Enable server-side encryption of the state object. |
| `kms_key_id` | Encrypt with a specific customer-managed KMS key instead of the default S3 key. |
| `use_lockfile` | Lock using a `<KEY>.tflock` object created with S3 conditional writes (Terraform 1.10 and later; generally available in 1.11). |
| `dynamodb_table` | Lock using a DynamoDB table (deprecated since Terraform 1.11). |
| `workspace_key_prefix` | Specify the prefix for non-default workspace state (default `env:`). |

- Native S3 locking with `use_lockfile` removes the need for a DynamoDB table. During migration, `use_lockfile` and `dynamodb_table` can be enabled together; Terraform then acquires both locks.
- Legacy DynamoDB locking uses a table whose partition key is the string attribute `LockID`. Terraform writes an item for the lock and a second item holding an MD5 digest of the state, which it uses to detect stale reads.

### AzureRM

Stores state as a blob in an Azure Storage container.

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "rg-tfstate"
    storage_account_name = "acmetfstateprod"
    container_name       = "tfstate"
    key                  = "network.terraform.tfstate"
    use_azuread_auth     = true
  }
}
```

- `use_azuread_auth = true` makes the backend use Microsoft Entra ID authorisation with Azure RBAC data-plane roles on the container, instead of storage account access keys. This allows shared key access to be disabled on the storage account entirely.
- Locking uses **blob leases**: before an operation, Terraform acquires a lease on the state blob; other processes cannot modify the blob while the lease is held.

### GCS

Stores state as objects in a Google Cloud Storage bucket.

```hcl
terraform {
  backend "gcs" {
    bucket             = "acme-tfstate-prod"
    prefix             = "network"
    kms_encryption_key = "projects/acme-prod/locations/europe-west3/keyRings/terraform/cryptoKeys/state"
  }
}
```

- Each workspace is stored as `<PREFIX>/<WORKSPACE>.tfstate`, and locked with a companion `<PREFIX>/<WORKSPACE>.tflock` object.
- `kms_encryption_key` encrypts the state with a customer-managed Cloud KMS key.

### HTTP

Stores state through a REST endpoint that supports `GET`, `POST`, and optionally `LOCK`/`UNLOCK` (or configurable methods). GitLab's managed Terraform state is the most common implementation.

```hcl
terraform {
  backend "http" {}
}
```

- All settings (`address`, `lock_address`, `unlock_address`, `lock_method`, `unlock_method`) are normally supplied as partial configuration or through `TF_HTTP_*` environment variables. The GitLab setup is shown in [[Terraform automation#GitLab CI]].

### Kubernetes

Stores state in a Kubernetes Secret and locks with a Lease object.

```hcl
terraform {
  backend "kubernetes" {
    secret_suffix = "network"
    namespace     = "terraform-state"
  }
}
```

- The Secret is named `tfstate-<WORKSPACE>-<SECRET_SUFFIX>`. Kubernetes limits Secrets to 1 MiB, which caps the size of the state.
- Kubernetes Secrets are only base64-encoded unless encryption at rest is configured for the cluster.

### PostgreSQL

Stores state in a PostgreSQL table and locks with advisory locks.

```hcl
terraform {
  backend "pg" {
    conn_str    = "postgres://terraform@db.internal.example.com/terraform_backend?sslmode=verify-full"
    schema_name = "network"
  }
}
```

### Consul

Stores state in the Consul key-value store, with Consul sessions for locking.

```hcl
terraform {
  backend "consul" {
    address = "consul.internal.example.com:8501"
    scheme  = "https"
    path    = "terraform/network"
    lock    = true
  }
}
```

### HCP Terraform

Configurations connected to HCP Terraform or Terraform Enterprise use the `cloud` block instead of a backend:

```hcl
terraform {
  cloud {
    organization = "acme"

    workspaces {
      name    = "network-prod"
      project = "networking"
    }
  }
}
```

- State is stored, versioned, and locked by the platform, and runs can execute remotely. The platform is described in [[Terraform automation#HCP Terraform and Terraform Enterprise]].
- `workspaces` selects either a single workspace by `name`, or a set of workspaces by `tags`, which CLI workspace commands then switch between.
- The older `backend "remote"` serves the same purpose and is superseded by the `cloud` block.

>[!note]
>Terraform 1.3 removed the `artifactory`, `etcd`, `etcdv3`, `manta`, and `swift` backends. Configurations that still use them must migrate before upgrading.

## State locking

> **State locking** prevents two operations from writing the same state at the same time. Terraform acquires the lock before any operation that may write state and releases it afterwards.

- Without locking, two concurrent applies — for example, two pipeline runs triggered by near-simultaneous merges — both read the same state, both change infrastructure, and the second write silently discards the record of the first run's changes. The result is orphaned resources, duplicates, and a state that no longer matches reality.
- Locking is automatic for commands that write state (`apply`, `destroy`, `import`, state-modifying `state` subcommands) and for `plan`, which holds the lock so that state cannot change while the plan is computed. Purely read-only commands such as `state list` do not lock.
- If the lock is held, the operation fails with "Error acquiring the state lock" and prints the lock's metadata: ID, path, operation, the user and host who hold it, the Terraform version, and the time it was created.

| Backend | Locking mechanism |
| ------- | ----------------- |
| `local` | OS-level file lock and a `.terraform.tfstate.lock.info` file. |
| `s3` | `<KEY>.tflock` object with conditional writes, or a DynamoDB item (legacy). |
| `azurerm` | Blob lease on the state blob. |
| `gcs` | `.tflock` object created with a generation precondition. |
| `kubernetes` | Lease object. |
| `pg` | PostgreSQL advisory locks. |
| `consul` | Consul session. |
| `http` | Optional `LOCK`/`UNLOCK` requests to the configured addresses. |
| HCP Terraform | Workspace lock managed by the platform. |

Lock-related options:

- Wait for a held lock instead of failing immediately — useful in pipelines where runs may briefly overlap:

```bash
terraform apply -lock-timeout=10m
```

- Disable locking for one command. This is unsafe in any shared environment and should be limited to backends that do not support locking:

```bash
terraform plan -lock=false
```

### Force unlock

A lock can remain held after the process that acquired it died — a cancelled pipeline, a killed laptop session, a network failure during apply.

- Release a stale lock using the ID printed in the error message:

```bash
terraform force-unlock 9db590f1-b6fe-c5f2-2678-8804f089deba
```

- `force-unlock` only removes the lock for the current configuration's state. It asks for confirmation unless `-force` is given.
- Before unlocking, verify that the holder is really gone (check the CI system for running jobs, ask the user named in the lock info). Unlocking a lock that is legitimately held leads exactly to the concurrent-write corruption locking exists to prevent.
- After a crashed apply, run `terraform plan` immediately after unlocking to see what the interrupted run left behind.

## Migrating state between backends

`terraform init` detects when the backend configuration differs from the one cached in `.terraform/` and asks what to do.

- Migrate from local state to a newly configured remote backend (or between remote backends), copying existing state:

```bash
terraform init -migrate-state
```

- Answer the copy prompt automatically, for scripted migrations:

```bash
terraform init -migrate-state -force-copy
```

- Use the new backend configuration without copying anything — for example, when switching between environments with partial configuration:

```bash
terraform init -reconfigure -backend-config=backends/staging.s3.tfbackend
```

- Move back to local state: remove the `backend` block and run `terraform init -migrate-state`.

Migration procedure:

1. Make sure no one else is running Terraform against the current state.
2. Take a copy of the current state (`terraform state pull > pre-migration.tfstate`).
3. Change the backend block and run `terraform init -migrate-state`.
4. Run `terraform plan` and confirm it shows no changes. A migration that changes nothing but the storage location must produce an empty plan.
5. Delete the old local `terraform.tfstate` and its backup, which still contain every secret.

## Sharing state between configurations

When infrastructure is split into several root modules (see [[Terraform project structure#State decomposition]]), downstream configurations need values from upstream ones — a VPC ID, subnet IDs, a cluster endpoint.

### terraform_remote_state

```hcl
data "terraform_remote_state" "network" {
  backend = "s3"

  config = {
    bucket = "acme-tfstate-prod"
    key    = "network/terraform.tfstate"
    region = "eu-central-1"
  }
}

resource "aws_instance" "app" {
  ami           = data.aws_ami.app.id
  instance_type = "t3.small"
  subnet_id     = data.terraform_remote_state.network.outputs.private_subnet_ids["eu-central-1a"]
}
```

- Only the **root module outputs** of the other configuration are exposed, through `.outputs`.
- To read them, Terraform downloads the entire state snapshot. The consuming configuration therefore needs read access to the whole state, including every secret the upstream configuration holds, even though it uses only a few outputs.
- It also couples the consumer to the producer's backend type, location, and output names.

### Alternatives

| Approach | Description |
| -------- | ----------- |
| Provider data sources | Look up the objects directly by name or tag (`data "aws_vpc"`, `data "aws_subnets"`); no access to the other state is required. |
| Published parameters | Have the producer write the values to a parameter store (AWS SSM Parameter Store, Azure App Configuration, Consul KV) that consumers read. |
| `tfe_outputs` data source | Read only the outputs of an HCP Terraform workspace, without access to its full state. |
| Terragrunt dependencies | Pass outputs between stacks through the wrapper (see [[Terraform automation#Terragrunt]]). |

- Provider data sources and published parameters keep each state readable only by the configuration that owns it, which is the preferred design where state access is tightly controlled.

## Bootstrapping the backend

A remote backend must exist before any configuration can use it, which creates a chicken-and-egg problem: the bucket that holds state cannot easily be managed by a configuration whose state lives in that bucket.

Common approaches:

1. **Bootstrap configuration with migrated state**
	1. Write a small configuration that creates the state bucket (or storage account), its encryption key, and its access policy, using local state.
	2. Apply it.
	3. Add a backend block pointing at the new bucket, with a dedicated key such as `bootstrap/terraform.tfstate`, and run `terraform init -migrate-state`.
2. **Out-of-band creation** — create the state storage with a cloud-native template (CloudFormation, Bicep), a script, or an organisation-level landing zone, and treat it as a prerequisite.
3. **Managed platform** — use HCP Terraform or GitLab-managed state, which provide storage, locking, and versioning without bootstrapping.

The state storage should always carry `prevent_destroy` or an equivalent deletion lock.

## Securing state storage

State contains secrets in plaintext (see [[Terraform state#Sensitive data in state]]). The storage that holds it is one of the most sensitive assets of the whole infrastructure.

Requirements, independent of the backend type:

- **Encryption at rest**, preferably with a customer-managed key whose usage can be audited and whose access policy is separate from the storage access policy.
- **Encryption in transit** — deny any request not made over TLS.
- **No public access**, enforced at the account or organisation level where possible.
- **Versioning and soft delete**, so that corrupted or deleted state can be restored.
- **Restricted access** — only the identities that run Terraform for a given configuration should be able to read or write its state. Separate state objects or prefixes per configuration and per environment allow access to be scoped narrowly.
- **Access logging** — record every read and write of state objects (S3 data events, Azure Storage diagnostic logs, GCS data access audit logs).
- **Deletion protection** — `prevent_destroy` in the configuration that manages the storage, plus provider-side locks (Azure resource locks, S3 Object Lock if required by policy).

### S3 state bucket

```hcl
resource "aws_kms_key" "tfstate" {
  description         = "Encryption of Terraform state"
  enable_key_rotation = true
}

resource "aws_s3_bucket" "tfstate" {
  bucket = "acme-tfstate-prod"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_ownership_controls" "tfstate" {
  bucket = aws_s3_bucket.tfstate.id
  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_public_access_block" "tfstate" {
  bucket                  = aws_s3_bucket.tfstate.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "tfstate" {
  bucket = aws_s3_bucket.tfstate.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "tfstate" {
  bucket = aws_s3_bucket.tfstate.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.tfstate.arn
    }
    bucket_key_enabled = true
  }
}

data "aws_iam_policy_document" "tfstate_tls_only" {
  statement {
    sid     = "DenyInsecureTransport"
    effect  = "Deny"
    actions = ["s3:*"]
    resources = [
      aws_s3_bucket.tfstate.arn,
      "${aws_s3_bucket.tfstate.arn}/*",
    ]

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }
}

resource "aws_s3_bucket_policy" "tfstate" {
  bucket = aws_s3_bucket.tfstate.id
  policy = data.aws_iam_policy_document.tfstate_tls_only.json
}
```

### Azure Storage

- Enable blob versioning and soft delete for blobs and containers.
- Disable shared key access (`shared_access_key_enabled = false`) and use Entra ID authorisation (`use_azuread_auth = true` in the backend).
- Disable public network access or restrict it to private endpoints and trusted networks.
- Apply a `CanNotDelete` resource lock to the storage account.
- Optionally use customer-managed keys and infrastructure encryption.

### Google Cloud Storage

- Enable uniform bucket-level access and enforce public access prevention.
- Enable object versioning.
- Set a default Cloud KMS key on the bucket or use `kms_encryption_key` in the backend.

### Client-side state encryption

- Terraform relies entirely on the storage service for encryption at rest; anyone with read access to the object sees plaintext.
- OpenTofu (1.7 and later) can encrypt state and plan files on the client before they are written, so that storage access alone does not reveal their contents:

```hcl
terraform {
  encryption {
    key_provider "aws_kms" "state" {
      kms_key_id = "alias/tofu-state"
      region     = "eu-central-1"
      key_spec   = "AES_256"
    }

    method "aes_gcm" "state" {
      keys = key_provider.aws_kms.state
    }

    state {
      method = method.aes_gcm.state
    }

    plan {
      method = method.aes_gcm.state
    }
  }
}
```

## References

- [Backend configuration](https://developer.hashicorp.com/terraform/language/backend)
- [S3 backend](https://developer.hashicorp.com/terraform/language/backend/s3)
- [AzureRM backend](https://developer.hashicorp.com/terraform/language/backend/azurerm)
- [GCS backend](https://developer.hashicorp.com/terraform/language/backend/gcs)
- [State locking](https://developer.hashicorp.com/terraform/language/state/locking)
- [The terraform_remote_state data source](https://developer.hashicorp.com/terraform/language/state/remote-state-data)
- [OpenTofu state encryption](https://opentofu.org/docs/language/state/encryption/)
