---
created: 2026-10-05
---

>[!abstract]+ **Scope**: What Terraform is, how its components fit together, its licensing and distribution model, and how to install it. This note orients you in the Terraform notes and links each topic to the note that owns it.

## Terraform

>[**Terraform**](https://developer.hashicorp.com/terraform) is an [[🛠️ Infrastructure as Code|Infrastructure as Code (IaC)]] tool by HashiCorp that provisions and manages infrastructure through the APIs of cloud platforms and other services, using a declarative configuration language.

- You describe the **desired state** of infrastructure in configuration files written in the HashiCorp Configuration Language (HCL). Terraform computes the actions required to move the real infrastructure from its current state to the desired state, shows them to you as a **plan**, and executes them on approval.
- Terraform automates **infrastructure provisioning**: creating, changing, and destroying networks, virtual machines, storage, DNS records, IAM objects, Kubernetes objects, SaaS settings, and anything else exposed through an API. Configuring software inside machines is the job of configuration management tools; see [[🛠️ Infrastructure as Code#Provisioning vs. configuration management]].
- Terraform is written in Go and distributed as a single statically linked executable, `terraform`.

### Properties that define Terraform

- **Declarative.** Configuration states *what* must exist, not the sequence of API calls that creates it. See [[🛠️ Infrastructure as Code#Declarative vs. imperative]].
- **Provider-agnostic.** Terraform Core knows nothing about any specific platform. All platform knowledge lives in [[🛠️ Terraform providers|providers]], so one workflow and one language manage AWS, Azure, Google Cloud, Kubernetes, GitHub, Cloudflare, Vault, and thousands of other targets, including several in the same configuration.
- **Plan before apply.** Every change is computed as an execution plan that you can review, save, and apply exactly as reviewed. See [[🛠️ Terraform CLI and workflow#Planning changes]].
- **Stateful.** Terraform records the mapping between configuration objects and real infrastructure objects in a **state** file. State is what makes Terraform idempotent: re-applying unchanged configuration produces no changes. See [[🛠️ Terraform state]].
- **Graph-based.** Terraform builds a dependency graph from references between objects, then creates, updates, and destroys objects in dependency order and in parallel where the graph allows. See [[🛠️ Terraform resources and data sources#Dependencies and the resource graph]].
- **Modular.** Configuration is packaged into reusable [[🛠️ Terraform modules|modules]] that can be versioned and shared through registries.

### Typical use cases

- **Provisioning** new environments from code: networks, compute, storage, identity, and the dependencies between them.
- **Changing** existing infrastructure through reviewed code changes instead of console clicks, with a full history in version control (see [[🛠️ Core Git]]).
- **Replicating** environments: the same configuration, parameterized with different [[🛠️ Terraform variables and outputs|variables]], produces identical development, staging, and production environments.
- **Bringing existing infrastructure under management** by importing it into state. See [[🛠️ Terraform state#Importing existing infrastructure]].
- **Enforcing security baselines** by codifying guardrails (encryption, logging, network isolation, IAM boundaries) and checking every change against policy before it reaches the cloud. See [[🛠️ Terraform security]].

## How Terraform works

- Terraform consists of two kinds of components: **Terraform Core** and **plugins**. Providers are the most important plugins.

```text
                 +-------------------------+
 .tf files ----> |                         |  gRPC   +-----------+  HTTPS  +-------------+
                 |     Terraform Core      | <-----> | Provider  | <-----> | Platform API|
 state  <------> |  (graph, plan, apply)   |         |  plugin   |         | (AWS, GCP…) |
                 +-------------------------+         +-----------+         +-------------+
```

### Terraform Core

>**Terraform Core** is the `terraform` executable. It reads configuration and state, builds the dependency graph, computes plans, and drives providers to execute them.

- Core works with two inputs:
	- **Configuration** (`.tf` and `.tf.json` files): the desired state.
	- **State** (`terraform.tfstate` or a remote equivalent): Terraform's record of what it manages and the last known attributes of each object.
- From these inputs, Core:
	1. Parses and evaluates the configuration, including variables, expressions, and module calls.
	2. Refreshes state by asking providers to read the current attributes of every managed object, so the plan accounts for changes made outside Terraform (**drift**).
	3. Builds a dependency graph of all resources, data sources, providers, variables, and outputs.
	4. Diffs the desired state against the refreshed state and produces a plan of create, update, replace, and delete actions.
	5. On apply, walks the graph and calls providers to perform each action, writing the results back to state.
- Core also provides the CLI, the backend system that stores state (see [[🛠️ Terraform state#Backends]]), the module installer, and the [[🛠️ Terraform configuration language#Functions|built-in functions]].

### Providers

>A **provider** is a plugin that implements resource types and data sources for one platform by translating Terraform's create, read, update, and delete operations into that platform's API calls.

- Providers are separate executables that Terraform downloads during `terraform init` and runs as child processes. Core and providers communicate over gRPC on a local socket using the Terraform plugin protocol.
- Because each provider is a native executable that runs with your credentials, the choice and integrity of providers is a supply chain concern. See [[🛠️ Terraform providers]] and [[🛠️ Terraform security#Provider and module supply chain]].

>[!note] Terraform also supports **provisioners**, which run commands on the local machine or on a created resource. They're built into Core, are a last resort, and are covered in [[🛠️ Terraform resources and data sources#Provisioners]].

### The core workflow

- Terraform's workflow has three steps: **write** configuration, **plan** the changes, and **apply** them. In practice:

```bash
terraform init      # Install providers and modules, configure the backend
terraform plan      # Compute and display the execution plan
terraform apply     # Execute the plan and update state
terraform destroy   # Destroy everything this configuration manages
```

- Every command, option, and environment variable of this workflow is covered in [[🛠️ Terraform CLI and workflow]].

## Editions, licensing, and OpenTofu

- Terraform was released under the Mozilla Public License 2.0 (MPL 2.0) until version 1.5.x. In August 2023, HashiCorp relicensed Terraform (from 1.6) under the **Business Source License 1.1 (BSL)**. The BSL permits internal use, including commercial use, but forbids offering Terraform as part of a product that competes with HashiCorp.
- In response, the last MPL-licensed codebase was forked as [**OpenTofu**](https://opentofu.org/), a Linux Foundation project. OpenTofu's CLI is `tofu`, it reads the same configuration language, and it's largely compatible with Terraform's state format and provider ecosystem. Since the fork, the two projects have diverged: for example, OpenTofu offers client-side state encryption, while Terraform has its own features such as `terraform query` and `actions`.
- IBM acquired HashiCorp in February 2025. Terraform remains BSL-licensed.
- Terraform is available in several editions:

| Edition | Description |
| :--- | :--- |
| Terraform CLI (Community Edition) | Run the open-source-available `terraform` executable on your own machines and pipelines. |
| [HCP Terraform](https://developer.hashicorp.com/terraform/cloud-docs) | Use HashiCorp's SaaS for remote runs, remote state, a private registry, policy enforcement, and team access control. Formerly named Terraform Cloud. |
| [Terraform Enterprise](https://developer.hashicorp.com/terraform/enterprise) | Run a self-hosted distribution of HCP Terraform inside your own environment. |

- HCP Terraform and Terraform Enterprise are covered in [[🛠️ Terraform automation and collaboration#HCP Terraform and Terraform Enterprise]].

## Installing Terraform

- Official installation instructions: [Install Terraform](https://developer.hashicorp.com/terraform/install).

### Debian and Ubuntu

- Install the prerequisites:

```bash
sudo apt-get update && sudo apt-get install -y gnupg software-properties-common wget
```

- Download the HashiCorp GPG key and store it as a dedicated keyring:

```bash
wget -O- https://apt.releases.hashicorp.com/gpg | \
gpg --dearmor | \
sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg > /dev/null
```

- Verify the key's fingerprint against the one published on the [HashiCorp security page](https://www.hashicorp.com/en/trust/security):

```bash
gpg --no-default-keyring \
--keyring /usr/share/keyrings/hashicorp-archive-keyring.gpg \
--fingerprint
```

- Add the HashiCorp repository, pinned to that keyring:

```bash
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] \
https://apt.releases.hashicorp.com $(lsb_release -cs) main" | \
sudo tee /etc/apt/sources.list.d/hashicorp.list
```

- Install Terraform:

```bash
sudo apt-get update && sudo apt-get install terraform
```

### RHEL, Fedora, and Amazon Linux

- Add the HashiCorp repository and install Terraform on RHEL-compatible distributions:

```bash
sudo dnf install -y dnf-plugins-core
sudo dnf config-manager --add-repo https://rpm.releases.hashicorp.com/RHEL/hashicorp.repo
sudo dnf install terraform
```

- On Fedora, replace `RHEL` with `fedora` in the repository URL. On Amazon Linux, use `AmazonLinux`.

### Arch Linux

- Install the distribution package:

```bash
sudo pacman -S terraform
```

>[!note] Distribution packages are built by the distribution, not by HashiCorp. If you need a specific version or HashiCorp-signed builds, install the official binary instead.

### macOS

```bash
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
```

### Installing the official binary manually

- Download the archive, the checksum file, and its signature for the version you need:

```bash
VERSION=1.14.0
wget https://releases.hashicorp.com/terraform/${VERSION}/terraform_${VERSION}_linux_amd64.zip
wget https://releases.hashicorp.com/terraform/${VERSION}/terraform_${VERSION}_SHA256SUMS
wget https://releases.hashicorp.com/terraform/${VERSION}/terraform_${VERSION}_SHA256SUMS.sig
```

- Verify the signature of the checksum file with the imported HashiCorp key, then verify the archive against the checksum file:

```bash
gpg --verify terraform_${VERSION}_SHA256SUMS.sig terraform_${VERSION}_SHA256SUMS
sha256sum --ignore-missing -c terraform_${VERSION}_SHA256SUMS
```

- Extract the executable into a directory on your `PATH`:

```bash
unzip terraform_${VERSION}_linux_amd64.zip terraform
sudo install -m 0755 terraform /usr/local/bin/terraform
```

>[!important] Verifying both the signature and the checksum matters on build agents: the `terraform` executable runs with whatever cloud credentials your pipeline holds.

### Managing multiple versions

- Projects pin the Terraform version they require with `required_version` (see [[🛠️ Terraform configuration language#The terraform block]]). When you work across projects that require different versions, use a version manager such as [`tfenv`](https://github.com/tfutils/tfenv) or [`tenv`](https://github.com/tofuutils/tenv) (which also manages OpenTofu):

```bash
tenv tf install 1.14.0
tenv tf use 1.14.0
```

### Verifying the installation

```bash
terraform version
```

- Enable shell tab completion for `bash` or `zsh`:

```bash
terraform -install-autocomplete
```

## Terraform notes

- [[🛠️ Infrastructure as Code]]: IaC principles, declarative vs. imperative, mutable vs. immutable infrastructure, IaC tool landscape, and Terraform with Ansible.
- [[🛠️ Terraform CLI and workflow]]: `init`, `plan`, `apply`, `destroy`, plan files, targeting and replacement, inspection commands, environment variables, CLI configuration, and debugging.
- [[🛠️ Terraform configuration language]]: HCL syntax, files and blocks, the `terraform` block and version constraints, types, expressions, `for` expressions, dynamic blocks, and functions.
- [[🛠️ Terraform providers]]: provider requirements and configuration, aliases, authentication, the dependency lock file, mirrors, and notable providers.
- [[🛠️ Terraform resources and data sources]]: resources, addresses, the dependency graph, meta-arguments, `lifecycle`, custom conditions, `check` blocks, provisioners, data sources, ephemeral resources, and actions.
- [[🛠️ Terraform variables and outputs]]: input variables, types, validation, sensitivity, `.tfvars` files and precedence, local values, and outputs.
- [[🛠️ Terraform state]]: the state file, backends, locking, workspaces, state commands, importing, refactoring with `moved` and `removed`, drift, and recovery.
- [[🛠️ Terraform modules]]: module structure, sources, versioning, meta-arguments, composition, providers in modules, documentation, and design rules.
- [[🛠️ Terraform testing]]: `fmt`, `validate`, TFLint, `terraform test`, mocking, and Terratest.
- [[🛠️ Terraform automation and collaboration]]: repository layouts, environment isolation, CI/CD pipelines, HCP Terraform, Atlantis, Terragrunt, and drift detection.
- [[🛠️ Terraform security]]: threat model, secrets in state and plans, ephemeral values, supply chain, pipeline security, least privilege, policy as code, static analysis, and Terraform artifacts as targets during assessments.
