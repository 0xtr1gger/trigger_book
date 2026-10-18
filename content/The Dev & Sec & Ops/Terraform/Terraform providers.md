> A **Terraform provider** is a plugin that implements the resource types, data sources, ephemeral resources, and functions of a particular API, and translates Terraform Core's requests into calls to that API.

- Terraform Core contains no platform-specific logic. Without providers, a configuration can declare only variables, locals, outputs, and the built-in `terraform_data` resource.
- Providers are distributed separately from Terraform, versioned independently, and installed per working directory by `terraform init`.
- How Core and providers communicate is described in [[Terraform#Plugin protocol]].

## Provider requirements

Every provider a module uses should be declared in the `required_providers` block inside the `terraform` block.

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 5.0"
    }
  }
}
```

- The key (`aws`, `azurerm`, `cloudflare`) is the provider's **local name**, used to refer to it within the module. It should match the provider's preferred name, which is also the prefix of its resource types (`aws_instance`, `azurerm_storage_account`).
- `source` is the provider's **source address**: `[<HOSTNAME>/]<NAMESPACE>/<TYPE>`.
	- The hostname defaults to `registry.terraform.io`, so `hashicorp/aws` is shorthand for `registry.terraform.io/hashicorp/aws`.
	- Providers from a private registry include the hostname: `app.terraform.io/acme/internal`.
- `version` is a version constraint (see [[Terraform configuration language#Version constraints]]). The exact version selected is recorded in the [[#Dependency lock file]].

### Provider tiers

The Terraform Registry labels providers by who maintains them:

| Tier | Maintainer | Example namespaces |
| ---- | ---------- | ------------------ |
| Official | HashiCorp. | `hashicorp/aws`, `hashicorp/azurerm`, `hashicorp/google`, `hashicorp/kubernetes` |
| Partner | A technology company that has passed HashiCorp's partner verification. | `cloudflare/cloudflare`, `datadog/datadog`, `mongodb/mongodbatlas` |
| Community | Any individual or organisation publishing to the registry. | `kreuzwerker/docker`, `bpg/proxmox` |

- The tier describes provenance, not code quality. Partner and community providers are signed by their publisher's key, which the registry stores but HashiCorp does not audit (see [[Terraform security#Supply chain security]]).

### Implicit provider resolution

- If a resource type is used without a matching `required_providers` entry, Terraform infers the provider from the resource type prefix and assumes the `hashicorp` namespace. A `docker_container` resource with no declaration makes Terraform look for `registry.terraform.io/hashicorp/docker`, which is not the maintained Docker provider (`kreuzwerker/docker`).
- Implicit resolution exists for backward compatibility. Declaring every provider explicitly makes the source unambiguous and allows version constraints.

## Provider configuration

A `provider` block configures an instance of a provider: endpoint, region, and provider-wide defaults. Provider blocks belong in the root module; reusable modules receive provider configurations from their caller (see [[Terraform modules#Providers in modules]]).

```hcl
provider "aws" {
  region              = "eu-central-1"
  allowed_account_ids = ["111111111111"]

  default_tags {
    tags = {
      ManagedBy   = "terraform"
      Repository  = "acme/infrastructure"
      Environment = var.environment
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}
```

- Unlike the `terraform` block, provider arguments can reference variables and locals. They can also reference resource attributes, but a provider configured from values that are unknown until apply cannot plan the resources that depend on it. This is a common failure when a Kubernetes provider is configured from a cluster created in the same configuration (see [[Terraform automation#Integrating with Kubernetes and Helm]]).
- Configuration requirements are specific to each provider:
	- the `azurerm` provider requires a `features {}` block (possibly empty) and, since version 4.0, an explicit subscription ID;
	- the `aws` provider's `allowed_account_ids` and `forbidden_account_ids` arguments make the provider fail before any API call when it is pointed at an unexpected account, which guards against applying a configuration to the wrong environment.
- `default_tags` (AWS) and equivalent features in other providers label every taggable resource, which is the simplest way to mark resources as Terraform-managed and attributable to a repository.
- If a provider is required but has no `provider` block, Terraform uses an empty configuration and the provider falls back to its own defaults and environment variables.

## Multiple provider configurations

A provider can be configured more than once with the `alias` argument, for example to manage several regions from one configuration.

```hcl
provider "aws" {
  region = "eu-central-1"
}

provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}
```

- The configuration without `alias` is the **default** configuration for that provider. Resources use it unless they specify otherwise.
- A resource or data source selects an aliased configuration with the `provider` meta-argument, using the unquoted reference `<LOCAL NAME>.<ALIAS>`:

```hcl
# ACM certificates used by CloudFront must be created in us-east-1.
resource "aws_acm_certificate" "cdn" {
  provider          = aws.us_east_1
  domain_name       = "www.example.com"
  validation_method = "DNS"
}
```

- Modules receive aliased configurations through the `providers` argument of the `module` block (see [[Terraform modules#Providers in modules]]).
- Terraform cannot create provider configurations dynamically with `count` or `for_each`; each must be written out. OpenTofu supports `for_each` on provider blocks.

## Dependency lock file

`terraform init` records the exact provider versions it selected, and their checksums, in `.terraform.lock.hcl` in the root module directory.

```hcl
# This file is maintained automatically by "terraform init".
# Manual edits may be lost in future updates.

provider "registry.terraform.io/hashicorp/aws" {
  version     = "6.0.0"
  constraints = "~> 6.0"
  hashes = [
    "h1:<base64-encoded hash>",
    "zh:<hex-encoded hash>",
    "zh:<hex-encoded hash>",
  ]
}
```

- `version` is the selected version. Later runs of `terraform init` reuse it even if newer versions satisfy the constraint, which makes runs reproducible across machines and over time.
- `hashes` lists the checksums Terraform accepts for that version:
	- `zh:` hashes are SHA-256 checksums of the release archives for each platform, as published in the provider's signed `SHA256SUMS` file;
	- `h1:` hashes are checksums of the unpacked package contents, which also allow verification of providers installed from a mirror or cache.
- The lock file covers providers only. Module versions are not locked; they must be pinned in the `module` block (see [[Terraform modules#Module versioning]]).
- The lock file must be committed to version control. Without it, each environment may select a different provider version, and the integrity check against previously trusted checksums is lost.

Managing the lock file:

- Upgrade providers to the newest versions allowed by the constraints and rewrite the lock file:

```bash
terraform init -upgrade
```

- Record hashes for every platform that runs the configuration (for example, Linux CI runners and macOS workstations). By default, `terraform init` records the full set of `zh:` hashes from the registry but only the `h1:` hash for the current platform:

```bash
terraform providers lock \
  -platform=linux_amd64 \
  -platform=linux_arm64 \
  -platform=darwin_arm64 \
  -platform=windows_amd64
```

- Refuse to modify the lock file, so that a run fails instead of silently selecting a provider that was never reviewed. This is the appropriate mode for CI:

```bash
terraform init -lockfile=readonly
```

- Show the providers required by the configuration and by the state, grouped by module:

```bash
terraform providers
```

## Provider installation

By default, `terraform init` downloads providers from their origin registry into `.terraform/providers/` in the working directory. Installation behaviour is controlled by the CLI configuration file.

### CLI configuration file

- The CLI configuration file is `~/.terraformrc` on Unix-like systems and `%APPDATA%\terraform.rc` on Windows. The `TF_CLI_CONFIG_FILE` environment variable points Terraform at a different file.
- It is configuration of the Terraform binary for a user or machine, not of any particular project, and must not be committed to a project repository.

```hcl
# ~/.terraformrc
plugin_cache_dir   = "$HOME/.terraform.d/plugin-cache"
disable_checkpoint = true

provider_installation {
  network_mirror {
    url     = "https://terraform-mirror.internal.example.com/providers/"
    include = ["registry.terraform.io/hashicorp/*"]
  }
  direct {
    exclude = ["registry.terraform.io/hashicorp/*"]
  }
}
```

| Setting | Purpose |
| ------- | ------- |
| `plugin_cache_dir` | Share downloaded providers between working directories instead of downloading them for each one. |
| `disable_checkpoint` | Disable the background call to HashiCorp's Checkpoint service, which checks for new versions and security bulletins. |
| `provider_installation` | Define the installation methods Terraform may use and which providers each method serves. |

### Plugin cache

- With a plugin cache, `terraform init` places each provider in the cache once and links it into each working directory, which saves bandwidth and time in CI and on workstations with many configurations.
- The cache directory must exist before Terraform uses it. It can also be set with the `TF_PLUGIN_CACHE_DIR` environment variable.
- The cache is not safe for concurrent writes by multiple Terraform processes. Parallel CI jobs should use separate caches or a pre-populated read-only mirror.

### Mirrors

The `provider_installation` block accepts the following methods:

| Method | Purpose |
| ------ | ------- |
| `direct` | Download from the provider's origin registry. |
| `filesystem_mirror` | Install from a local directory with the registry's directory layout. |
| `network_mirror` | Install from an HTTPS server that implements the provider network mirror protocol. |
| `dev_overrides` | Use a locally built provider binary, bypassing version selection and checksums (development only). |

- `include` and `exclude` patterns route each provider to exactly one method. Combining a mirror for approved providers with a `direct` method that excludes everything else allows an organisation to control which providers can be installed at all.
- Populate a mirror directory for air-gapped environments:

```bash
terraform providers mirror -platform=linux_amd64 /srv/terraform-mirror
```

- Then reference it in the CLI configuration:

```hcl
provider_installation {
  filesystem_mirror {
    path    = "/srv/terraform-mirror"
    include = ["registry.terraform.io/*/*"]
  }
}
```

- Without an explicit `provider_installation` block, Terraform also searches implicit local mirror directories such as `~/.terraform.d/plugins` and, on Linux, `/usr/share/terraform/plugins` and `/usr/local/share/terraform/plugins`.
- Whatever the source, Terraform verifies every installed package against the hashes in the dependency lock file.

## Utility providers

Several providers manage local or synthetic resources rather than a remote platform. They are often needed as glue in otherwise cloud-focused configurations.

| Provider | Main objects | Purpose |
| -------- | ------------ | ------- |
| `hashicorp/random` | `random_id`, `random_string`, `random_password`, `random_pet`, `random_shuffle` | Generate values that stay stable across runs until explicitly replaced. |
| `hashicorp/local` | `local_file`, `local_sensitive_file` | Create and manage files on the machine running Terraform. |
| `hashicorp/null` | `null_resource` | Attach provisioners and triggers to a resource with no remote object (superseded by `terraform_data`). |
| `hashicorp/tls` | `tls_private_key`, `tls_self_signed_cert`, `tls_cert_request` | Generate keys and certificates. |
| `hashicorp/time` | `time_sleep`, `time_rotating`, `time_static` | Introduce delays and time-based rotation triggers. |
| `hashicorp/archive` | `archive_file` (data source) | Package files into ZIP archives, for example for serverless functions. |
| `hashicorp/http` | `http` (data source) | Perform an HTTP GET request and expose the response. |
| `hashicorp/external` | `external` (data source) | Run an external program and use its JSON output. |
| `hashicorp/cloudinit` | `cloudinit_config` (data source) | Render multi-part cloud-init documents. |
| `kreuzwerker/docker` | `docker_image`, `docker_container`, `docker_network`, `docker_volume` | Manage Docker objects on a local or remote Docker host. |

- Values generated by `random`, `tls`, and similar providers are stored in state, including private keys and passwords. For secrets, the ephemeral variants of these resources avoid persistence (see [[Terraform resources#Ephemeral resources]]).
- `http` and `external` are covered in [[Terraform data sources#Special-purpose data sources]].

### Example: local provider

A minimal configuration that requires no cloud account, useful for exploring the workflow:

```hcl
terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }
  }
}

resource "local_file" "greeting" {
  filename        = "${path.module}/out/greeting.txt"
  content         = "The wind is getting stronger.\n"
  file_permission = "0644"
}
```

- Initialise the directory, save a plan, apply exactly that plan, and inspect the result:

```bash
terraform init
terraform plan -out=tfplan
terraform apply tfplan
cat out/greeting.txt
```

- Deleting `out/greeting.txt` by hand and running `terraform plan` again shows Terraform detecting the drift and planning to recreate the file.

### Example: Docker provider

```hcl
terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {
  host = "unix:///var/run/docker.sock"
}

resource "docker_image" "nginx" {
  name         = "nginx:1.27-alpine"
  keep_locally = true
}

resource "docker_container" "web" {
  name  = "web"
  image = docker_image.nginx.image_id

  ports {
    internal = 80
    external = 8080
  }
}
```

- `docker_image.nginx.image_id` creates an implicit dependency, so the image is pulled before the container is created.
- Pinning the image tag (or digest) instead of `latest` keeps plans stable.

### Community virtualisation providers

- Community providers exist for local hypervisors and on-premises platforms, for example `bpg/proxmox` for Proxmox VE, `dmacvicar/libvirt` for libvirt/KVM, and `terra-farm/virtualbox` for VirtualBox.
- Their maintenance status varies considerably. Before adopting one, check release activity, open issues, and the publisher's identity in the registry.

## Provider development

- Providers are written in Go. HashiCorp recommends the **Terraform Plugin Framework** for new providers; the older **SDKv2** remains supported for existing ones, and both can be combined in one provider through muxing.
- A provider implements a schema and CRUD functions for each resource type, read functions for data sources, and optionally ephemeral resources and functions.
- During development, the `dev_overrides` block in the CLI configuration points Terraform at a locally built binary:

```hcl
provider_installation {
  dev_overrides {
    "registry.terraform.io/acme/internal" = "/home/dev/go/bin"
  }
  direct {}
}
```

- Providers are published to the public registry from a GitHub repository named `terraform-provider-<TYPE>`, with releases signed by a GPG key registered with the namespace.

## References

- [Provider requirements](https://developer.hashicorp.com/terraform/language/providers/requirements)
- [Provider configuration](https://developer.hashicorp.com/terraform/language/providers/configuration)
- [Dependency lock file](https://developer.hashicorp.com/terraform/language/files/dependency-lock)
- [CLI configuration file](https://developer.hashicorp.com/terraform/cli/config/config-file)
- [Terraform Plugin Framework](https://developer.hashicorp.com/terraform/plugin/framework)
