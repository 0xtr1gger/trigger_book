> **Terraform project structure** is the organisation of Terraform code into files, modules, root configurations, states, and repositories. It determines how environments are separated, how large the blast radius of a mistake is, how fast plans run, and who can change what.

- Terraform imposes almost no structure of its own: it loads all `.tf` files of one directory (see [[Terraform configuration language#Configuration files]]). Everything else is convention.
- This note covers conventions within a module, across a repository, and across environments and states.

## File layout

Within one module, files are split by purpose. The HashiCorp style guide and common practice converge on the following names:

| File | Contents |
| ---- | -------- |
| `terraform.tf` or `versions.tf` | The `terraform` block with `required_version` and `required_providers`. |
| `backend.tf` | The `backend` or `cloud` block (root modules only). |
| `providers.tf` | `provider` blocks (root modules only). |
| `main.tf` | Resources and data sources; split into topic files (`network.tf`, `iam.tf`, `storage.tf`) as the module grows. |
| `variables.tf` | Input variable declarations, in alphabetical order or grouped by topic. |
| `outputs.tf` | Output declarations. |
| `locals.tf` | Local values used across several files. |
| `data.tf` | Data sources, if numerous enough to warrant a separate file. |
| `moved.tf`, `imports.tf` | `moved`, `removed`, and `import` blocks during refactorings and migrations. |
| `README.md` | Module documentation (see [[Terraform modules#Documenting modules]]). |
| `.terraform.lock.hcl` | Dependency lock file (root modules; generated). |

- Files are named by what they contain, not by resource type alone. A reader should find any object by guessing the file name.
- Very large files are a sign that the module does too much and should be split into child modules or separate root modules.

## Naming conventions

- Use lowercase `snake_case` for all Terraform identifiers: resource names, variables, outputs, locals, module calls.
- Do not repeat the resource type in the resource name: `aws_instance.web`, not `aws_instance.web_instance` or `aws_instance.web_ec2`.
- When a module contains a single resource of a type, name it `this` or `main`: `aws_s3_bucket.this`.
- Use nouns, singular for single resources and for `count`/`for_each` resources alike: `aws_subnet.private` with `for_each` yields `aws_subnet.private["eu-central-1a"]`.
- Name variables after the attribute they set, with units where ambiguous: `retention_days`, `disk_size_gb`, `enable_flow_logs` (booleans as `enable_*` or `is_*`).
- Name outputs after what they return, prefixed by the object: `vpc_id`, `private_subnet_ids`, `db_endpoint`.
- Names of real infrastructure objects (the `name` arguments) follow the organisation's cloud naming standard and are usually built in a local value from project, environment, region, and component.
- TFLint's `terraform_naming_convention` rule enforces identifier conventions automatically (see [[Terraform testing#Static checks]]).

## Code style

- Run `terraform fmt` on every change; enforce it in CI.
- Within a block, order content as:
	1. meta-arguments `count` or `for_each`;
	2. arguments;
	3. nested blocks;
	4. `lifecycle`;
	5. `depends_on`.
- Separate groups with a blank line. Align `=` within groups (`fmt` does this).
- Reference other objects instead of repeating literal values, so that dependencies are explicit and values cannot diverge.
- Avoid hardcoded environment-specific values (account IDs, regions, CIDR blocks, names); take them from variables, locals, or data sources.
- Use `#` for comments and explain *why*, not *what* (see [[Terraform configuration language#Syntax]]).
- Prefer `for_each` over `count` for anything with identity (see [[Terraform resources#Meta-arguments]]).
- Keep expressions readable: extract complex `for` expressions and conditionals into named locals.

## Repository layout

A common layout separates reusable modules from the root configurations that use them:

```text
infrastructure/
├── modules/                  # reusable modules, no providers or backends
│   ├── network/
│   ├── database/
│   └── service/
├── live/                     # root modules, one directory per state
│   ├── global/
│   │   ├── iam/
│   │   └── dns/
│   ├── dev/
│   │   ├── network/
│   │   └── app/
│   ├── staging/
│   │   ├── network/
│   │   └── app/
│   └── prod/
│       ├── network/
│       │   ├── backend.tf
│       │   ├── main.tf
│       │   ├── providers.tf
│       │   ├── variables.tf
│       │   ├── outputs.tf
│       │   ├── versions.tf
│       │   ├── terraform.tfvars
│       │   └── .terraform.lock.hcl
│       └── app/
├── policy/                   # Rego or Sentinel policies
├── .tflint.hcl
├── .pre-commit-config.yaml
└── .gitignore
```

- Each directory under `live/` is a root module with its own backend key, its own lock file, and its own pipeline target.
- Root modules are thin: they configure providers and the backend, set environment-specific values, and call modules. Logic lives in `modules/`.

### Monorepo and polyrepo

| Aspect | Monorepo (modules and live configurations together) | Polyrepo (modules in separate repositories) |
| ------ | ---------------------------------------------------- | ------------------------------------------- |
| Module changes | Visible immediately to all configurations; atomic changes across modules and callers. | Released with version tags; callers upgrade deliberately. |
| Versioning | Local paths, no versions; every change affects every caller on the next plan. | Semantic versions, independent upgrade per environment. |
| Access control | One set of repository permissions. | Separate permissions per module and per environment repository. |
| Tooling | Requires change detection to plan only affected roots. | Simple pipelines per repository; more repositories to maintain. |

- A frequent compromise keeps live configurations in one repository and shared modules in a separate repository (or registry), referenced by version, so that a module change reaches production only when production's pin is updated.
- Repository boundaries are also security boundaries: if production configurations live in a separate repository, write access to development code does not imply the ability to change production.

## Environment separation

Several strategies exist for running the same infrastructure in several environments (development, staging, production):

| Strategy | Description | Strengths | Weaknesses |
| -------- | ----------- | --------- | ---------- |
| CLI workspaces | One configuration, one backend, a separate state per workspace (see [[Terraform state#Workspaces]]). | No code duplication; quick to create copies. | Shared backend access; environment invisible in code; structural differences require conditionals. |
| Directory per environment | Separate root modules (`live/dev`, `live/prod`) calling the same modules with different values. | Explicit; separate backends and access control; environments can differ structurally. | Some repetition of root module boilerplate. |
| Directory per environment with Terragrunt | As above, with backend and provider configuration generated (see [[Terraform automation#Terragrunt]]). | Minimal repetition; dependency management between stacks. | Additional tool and conventions to learn. |
| Separate repositories or accounts | Each environment's configuration in its own repository, deploying into its own cloud account or subscription. | Strongest isolation of code, permissions, and blast radius. | Most overhead; changes must be promoted across repositories. |
| HCP Terraform workspaces | One workspace per environment, each with its own variables, state, and permissions. | Platform-enforced separation and approval workflows. | Dependency on the platform. |

Recommendations:

- Use separate cloud accounts, subscriptions, or projects for production and non-production. The cloud account boundary is the strongest isolation available, and Terraform configurations should mirror it.
- Use separate root modules and separate backends (or at least separate state storage with separate access controls) per environment. CLI workspaces are appropriate for disposable copies, not for separating production from development.
- Keep environments as similar as possible: the same modules at the same versions, differing only in input values. Promote module upgrades from development to production.
- Pass environment-specific values through one `.tfvars` file per environment rather than through conditionals on the environment name.

## State decomposition

Splitting infrastructure into several root modules, each with its own state, is the main lever for safety and performance.

Why to split:

- **Blast radius** — a mistake, a bad provider upgrade, or a corrupted state affects only one part of the infrastructure.
- **Performance** — plan time is proportional to the number of resources refreshed (see [[Terraform CLI#Performance]]).
- **Access control** — different states can be planned and applied by different teams and identities.
- **Rate of change** — the network changes rarely, applications daily; separating them keeps routine changes away from foundational resources.
- **Provider configuration** — resources whose providers depend on other resources (Kubernetes objects inside a cluster) must live in a separate state from those resources (see [[Terraform automation#Integrating with Kubernetes and Helm]]).

A typical layering:

| Layer | Contents | Rate of change |
| ----- | -------- | -------------- |
| Organisation / global | Accounts, organisation policies, identity providers, DNS zones | Very low |
| Network | VPCs or VNets, subnets, routing, peering, VPN, firewalls | Low |
| Shared services | Clusters, registries, monitoring, key management | Medium |
| Data | Databases, storage, caches | Low to medium; highest risk |
| Applications | Per-service resources: compute, queues, load balancer rules | High |

- Lower layers expose values to higher layers through outputs read by data sources, published parameters, or `terraform_remote_state` (see [[Terraform backends#Sharing state between configurations]]).
- Dependencies should point in one direction only: applications depend on the network, never the reverse.
- Too fine a split creates its own problems — many pipelines, cross-state dependency management, and changes that require coordinated applies. A state should correspond to a component that is owned, changed, and reasoned about as a unit.

## Version pinning

| Item | Root modules | Reusable modules |
| ---- | ------------ | ---------------- |
| Terraform CLI | `required_version` with an upper bound (`">= 1.11, < 2.0.0"`) and an exact version in pipelines | Minimum version required by the features used (`">= 1.5"`) |
| Providers | `~>` on the major version; exact versions recorded in the committed lock file | Minimum version only (`">= 5.0"`) |
| Registry modules | Exact version in production; `~>` acceptable in development | Exact or `~>` for nested modules |
| Git modules | Full commit SHA in production; tag elsewhere | Tag or SHA |

- Upgrades are performed deliberately: `terraform init -upgrade` in a branch, review of the lock file diff and the plan, promotion from development to production.
- Provider major upgrades follow the provider's upgrade guide; they often rename arguments or change defaults.
- Dependency update bots (Renovate, Dependabot) automate the creation of upgrade pull requests.

## Version control hygiene

### .gitignore

```text
# Local working directories
**/.terraform/*

# State files and backups
*.tfstate
*.tfstate.*
errored.tfstate

# Saved plans
*.tfplan
tfplan
tfplan.json

# Crash logs
crash.log
crash.*.log

# Override files
override.tf
override.tf.json
*_override.tf
*_override.tf.json

# CLI configuration
.terraformrc
terraform.rc

# Variable files that are local-only
*.local.tfvars
```

- `.terraform.lock.hcl` must **not** be ignored; it belongs in version control (see [[Terraform providers#Dependency lock file]]).
- Whether to ignore `*.tfvars` depends on their content. Environment files containing only non-secret values (`prod.tfvars`) should be committed; local developer overrides should follow a naming convention that is ignored, such as `*.local.tfvars`.

### Pre-commit hooks

Pre-commit hooks run formatting, validation, linting, documentation, and secret scanning before a commit is created.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/antonbabenko/pre-commit-terraform
    rev: v1.96.1
    hooks:
      - id: terraform_fmt
      - id: terraform_validate
      - id: terraform_tflint
      - id: terraform_docs
      - id: terraform_trivy
      - id: terraform_checkov

  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.21.2
    hooks:
      - id: gitleaks
```

- Install the hooks once per clone, then run them against all files:

```bash
pre-commit install
pre-commit run --all-files
```

- The same checks must also run in CI, because hooks can be skipped locally.

### Commits and reviews

- Keep infrastructure changes small and focused; a pull request that changes one component produces a plan that reviewers can actually read.
- Include the plan output (or a link to it) in every pull request, and review the plan, not only the code diff.
- Record the reason for non-obvious changes in the commit message, especially for `ignore_changes`, scanner suppressions, and `moved` or `removed` blocks.

## Scaling large codebases

- **Monitor plan duration and resource counts** per state. States with thousands of resources take minutes to plan and are candidates for splitting.
- **Split monolithic states incrementally** — move resources from one root module to another by removing them from the source state with `removed` blocks (`destroy = false`) and importing them into the destination with `import` blocks, one component at a time (see [[Terraform state#Refactoring with moved and removed blocks]]).
- **Standardise through modules and policies**, not through copy-paste: a central module catalogue (private registry) and policy sets keep many teams consistent.
- **Watch provider API limits** — large applies can hit rate limits; tune `-parallelism` and provider retry settings.
- **Automate repetitive structure** with Terragrunt, Terramate, or generated root modules when the number of root modules reaches dozens or hundreds.
- **Assign ownership** — every root module has an owning team, recorded in a `CODEOWNERS` file, which also routes reviews of changes to it.

## References

- [Terraform style guide](https://developer.hashicorp.com/terraform/language/style)
- [Standard module structure](https://developer.hashicorp.com/terraform/language/modules/develop/structure)
- [pre-commit-terraform](https://github.com/antonbabenko/pre-commit-terraform)
- [GitHub Terraform .gitignore template](https://github.com/github/gitignore/blob/main/Terraform.gitignore)
