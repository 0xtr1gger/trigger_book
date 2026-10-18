> **Testing Terraform code** means verifying, at increasing cost and confidence, that a configuration is well-formed, that it expresses the intended infrastructure, and that the infrastructure it creates actually behaves as required.

Terraform testing is commonly arranged in layers, from cheap and fast to expensive and slow:

| Layer | Question answered | Tools | Infrastructure created |
| ----- | ----------------- | ----- | ---------------------- |
| Formatting and validation | Is the code well-formed and internally consistent? | `terraform fmt`, `terraform validate` | None |
| Linting | Does the code follow conventions and use valid provider values? | TFLint | None |
| Security and policy scanning | Does the code violate security or organisational rules? | Checkov, Trivy, KICS, OPA, Sentinel | None |
| Unit tests | Does the module compute the right values and plan the right resources? | `terraform test` with `command = plan` and mocks | None |
| Contract tests | Does the module reject invalid inputs and uphold its guarantees? | `validation`, preconditions, postconditions | None |
| Integration tests | Does the module deploy successfully and produce working infrastructure? | `terraform test` with `command = apply`, Terratest | Temporary |
| Continuous validation | Does the deployed infrastructure keep working? | `check` blocks, drift detection | Existing |

Security scanning and policy as code are covered in [[Terraform security#Static analysis]] and [[Terraform security#Policy as code]].

## Static checks

### Formatting and validation

- `terraform fmt -check -recursive` fails when any file is not in canonical format.
- `terraform validate` fails on syntax errors, unknown arguments, type mismatches, and invalid references.

Both are described in [[Terraform CLI#Validating and formatting]]. They need no credentials and run in seconds, so they belong in every pre-commit hook and every pipeline.

### TFLint

> **TFLint** is a pluggable linter for Terraform that detects errors `terraform validate` cannot: invalid provider-specific values, deprecated syntax, unused declarations, and violations of naming conventions.

- `terraform validate` checks only that an argument has the right type. TFLint's provider rulesets know, for example, that `t2.superlarge` is not a valid EC2 instance type or that an Azure VM size does not exist, and report it before an API call fails.
- Configure TFLint with `.tflint.hcl` in the repository root:

```hcl
config {
  call_module_type = "local"
}

plugin "terraform" {
  enabled = true
  preset  = "recommended"
}

plugin "aws" {
  enabled = true
  version = "0.38.0"
  source  = "github.com/terraform-linters/tflint-ruleset-aws"
}

rule "terraform_naming_convention" {
  enabled = true
}

rule "terraform_documented_variables" {
  enabled = true
}
```

- Install the plugins declared in the configuration:

```bash
tflint --init
```

- Lint the current module, or every module in the repository:

```bash
tflint
tflint --recursive
```

- Produce output for code-scanning integrations:

```bash
tflint --recursive --format sarif > tflint.sarif
```

- Rulesets exist for AWS, Azure (`tflint-ruleset-azurerm`), and Google Cloud (`tflint-ruleset-google`). The built-in `terraform` ruleset checks language-level issues such as unused variables, missing version constraints, and deprecated interpolation syntax.
- Individual findings can be suppressed with an annotation comment above the offending line:

```hcl
# tflint-ignore: aws_instance_invalid_type
instance_type = var.custom_instance_type
```

## Custom conditions as contract tests

Terraform's own validation features act as tests that run on every plan, in every environment:

- **Variable validation** rejects invalid inputs (see [[Terraform variables and outputs#Input variables]]).
- **Preconditions** verify assumptions about inputs and data sources before a resource is planned.
- **Postconditions** verify guarantees about a resource or data source after it is planned or applied (see [[Terraform resources#Custom conditions]]).

They fail the run, which makes them appropriate for conditions that must never be violated. Conditions that should only warn belong in `check` blocks.

## Check blocks

> A **check block** (Terraform 1.5 and later) defines assertions about infrastructure that are evaluated at the end of every plan and apply, and that produce **warnings** rather than errors when they fail.

```hcl
check "website_health" {
  data "http" "homepage" {
    url = "https://${aws_cloudfront_distribution.site.domain_name}/"
  }

  assert {
    condition     = data.http.homepage.status_code == 200
    error_message = "The website returned HTTP ${data.http.homepage.status_code}."
  }
}

check "certificate_expiry" {
  assert {
    condition     = timecmp(aws_acm_certificate.site.not_after, timeadd(plantimestamp(), "720h")) > 0
    error_message = "The TLS certificate expires within 30 days."
  }
}
```

- A check block contains one or more `assert` blocks and optionally one **scoped data source**. The scoped data source is read as part of the check, and its failure is also reported as a warning instead of stopping the run.
- Checks run after the rest of the plan or apply, so they observe the infrastructure as it is or is about to be.
- Because failures do not block, checks are suited to operational health conditions — endpoint availability, certificate expiry, quota headroom — rather than to correctness requirements.
- HCP Terraform evaluates check blocks during its periodic health assessments, which turns them into continuous monitoring of deployed infrastructure.

## The terraform test framework

> **`terraform test`** (Terraform 1.6 and later) is Terraform's native test framework. Tests are written in HCL in `.tftest.hcl` files and execute plans or applies against the module under test, with assertions on the results.

### Test files

- Test files live in the module's root directory or, by convention, in a `tests/` directory. `terraform test` discovers both.
- Each file contains one or more `run` blocks, executed in order, plus optional `variables`, `provider`, and `mock_provider` blocks.

```hcl
# tests/static_website.tftest.hcl

variables {
  storage_account_name = "tftestwebsite01"
  resource_group_name  = "rg-tftest-website"
  source_dir           = "./tests/fixtures/site"
}

run "rejects_invalid_account_name" {
  command = plan

  variables {
    storage_account_name = "Invalid_Name"
  }

  expect_failures = [var.storage_account_name]
}

run "plans_one_blob_per_file" {
  command = plan

  assert {
    condition     = length(azurerm_storage_blob.site) == length(fileset("./tests/fixtures/site", "**"))
    error_message = "Expected one blob per file in the source directory."
  }

  assert {
    condition     = azurerm_storage_account.this.allow_nested_items_to_be_public == false
    error_message = "Public blob access must be disabled."
  }
}

run "deploys_website" {
  command = apply

  assert {
    condition     = startswith(output.website_url, "https://")
    error_message = "The website URL must use HTTPS."
  }
}
```

### Run blocks

| Element | Purpose |
| ------- | ------- |
| `command` | Execute a `plan` or an `apply` (default `apply`). |
| `variables` | Override variable values for this run. |
| `assert` | Specify a condition and an error message; all assertions in a run are evaluated. |
| `expect_failures` | List checkable objects (variables, resources, outputs, check blocks) whose validation is expected to fail. |
| `module` | Execute a different module (for example, a setup helper) instead of the module under test. |
| `providers` | Map provider configurations for this run. |
| `plan_options` | Set planning options such as `mode = refresh-only`, `refresh`, `replace`, and `target`. |

- Assertions can reference resources, data sources, variables, and outputs of the module, and the outputs of earlier runs through `run.<NAME>.<OUTPUT>`.
- **`command = plan`** runs make no changes and are fast. They test computed values, resource counts, and argument values — unit tests.
- **`command = apply`** runs create real infrastructure. Terraform keeps the state of each test file in memory and destroys all created resources, in reverse order, after the last run of the file. A failed destroy leaves resources behind and is reported, so integration tests should run in a dedicated, regularly cleaned account or subscription.

### Setup modules

A `run` block with a `module` block executes a helper configuration, typically to create prerequisites:

```hcl
run "setup" {
  module {
    source = "./tests/setup"
  }
}

run "uses_setup_outputs" {
  command = plan

  variables {
    vpc_id = run.setup.vpc_id
  }

  assert {
    condition     = aws_security_group.this.vpc_id == run.setup.vpc_id
    error_message = "The security group must be created in the given VPC."
  }
}
```

### Mocking providers

Since Terraform 1.7, providers and individual resources can be mocked, so that `apply` runs execute without contacting any API and without credentials.

```hcl
mock_provider "azurerm" {
  mock_resource "azurerm_storage_account" {
    defaults = {
      id                   = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-test/providers/Microsoft.Storage/storageAccounts/tftestwebsite01"
      primary_web_endpoint = "https://tftestwebsite01.z6.web.core.windows.net/"
    }
  }
}

run "outputs_web_endpoint" {
  command = apply

  assert {
    condition     = output.website_url == "https://tftestwebsite01.z6.web.core.windows.net/"
    error_message = "website_url must expose the storage account's web endpoint."
  }
}
```

- A `mock_provider` replaces the real provider for the whole file. Computed attributes not given in `defaults` receive generated placeholder values.
- `override_resource`, `override_data`, and `override_module` replace specific objects, either at file level or within a single run:

```hcl
run "with_overridden_ami" {
  command = plan

  override_data {
    target = data.aws_ami.app
    values = {
      id           = "ami-0123456789abcdef0"
      architecture = "arm64"
    }
  }
}
```

- Mocked tests verify the module's logic, not the provider's behaviour or the platform's acceptance of the configuration. They complement, but do not replace, a smaller number of real `apply` tests.

### Running tests

- Run every test file of the module:

```bash
terraform init
terraform test
```

- Run one file and print the plan or state of each run:

```bash
terraform test -filter=tests/static_website.tftest.hcl -verbose
```

- Use a different test directory or pass variables:

```bash
terraform test -test-directory=integration -var="location=northeurope"
```

## Terratest

> **Terratest** is a Go library by Gruntwork for writing automated tests that deploy real infrastructure with Terraform, verify it through APIs, HTTP requests, or SSH, and destroy it afterwards.

- Terratest predates `terraform test` and remains useful when tests must interact with the deployed infrastructure in ways HCL cannot express: making HTTP requests with retries, running commands over SSH, querying Kubernetes, or combining Terraform with other tools such as Packer and Docker.

```go
// test/static_website_test.go
package test

import (
	"fmt"
	"strings"
	"testing"
	"time"

	http_helper "github.com/gruntwork-io/terratest/modules/http-helper"
	"github.com/gruntwork-io/terratest/modules/random"
	"github.com/gruntwork-io/terratest/modules/terraform"
)

func TestStaticWebsite(t *testing.T) {
	t.Parallel()

	suffix := strings.ToLower(random.UniqueId())

	opts := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		TerraformDir: "../examples/basic",
		Vars: map[string]interface{}{
			"storage_account_name": fmt.Sprintf("tt%s", suffix),
			"resource_group_name":  fmt.Sprintf("rg-tt-%s", suffix),
		},
	})

	defer terraform.Destroy(t, opts)
	terraform.InitAndApply(t, opts)

	url := terraform.Output(t, opts, "website_url")

	http_helper.HttpGetWithRetryWithCustomValidation(t, url, nil, 30, 10*time.Second,
		func(status int, body string) bool {
			return status == 200 && strings.Contains(body, "<html")
		})
}
```

- Run the tests with a timeout long enough for creation and destruction:

```bash
cd test
go test -v -timeout 45m ./...
```

- `defer terraform.Destroy` guarantees cleanup even when assertions fail. Unique names generated per run allow tests to run in parallel without collisions.
- Terratest tests are Go code, which is a barrier for teams that do not use Go; `terraform test` covers most module-level needs without it.

## Plan-based testing

A saved plan converted to JSON describes every planned change in machine-readable form. Tests and policies can evaluate it without creating infrastructure.

- Produce the JSON plan:

```bash
terraform plan -out=tfplan
terraform show -json tfplan > tfplan.json
```

- Query it directly, for example to list every resource that would be deleted:

```bash
jq -r '.resource_changes[] | select(.change.actions | index("delete")) | .address' tfplan.json
```

- **terraform-compliance** evaluates plans against behaviour-driven scenarios written in Gherkin:

```gherkin
Feature: Storage must be encrypted

  Scenario: S3 buckets have server-side encryption
    Given I have aws_s3_bucket_server_side_encryption_configuration defined
    Then it must contain rule
    And it must contain apply_server_side_encryption_by_default
```

```bash
terraform-compliance -p tfplan.json -f compliance/
```

- **Conftest** with Rego policies and **Sentinel** in HCP Terraform evaluate the same plan JSON; they are described in [[Terraform security#Policy as code]].

## Testing strategy

- **Test reusable modules thoroughly** — they are shared and change rarely, so investment pays off. Root configurations are tested mainly through plan review and policy checks.
- **Prefer plan-level tests with mocks** for logic: they are fast, deterministic, cost nothing, and need no credentials.
- **Keep a small number of real apply tests** per module, run on merge or nightly rather than on every commit.
- **Isolate integration tests** in a dedicated cloud account, subscription, or project, with budgets and alerts, and run a scheduled cleanup of leftover resources (for example, with `cloud-nuke` or `aws-nuke`-style tools scoped strictly to the test account).
- **Generate unique names** for every test run and tag test resources with the run ID, to allow parallel runs and reliable cleanup.
- **Test the examples** — the module's `examples/` directory doubles as documentation and test fixtures, which keeps documentation correct.
- **Verify deployed infrastructure** with post-deployment checks (`check` blocks, Chef InSpec profiles, or smoke tests in the pipeline) in addition to pre-deployment tests.

## References

- [Tests (terraform test)](https://developer.hashicorp.com/terraform/language/tests)
- [Mocks](https://developer.hashicorp.com/terraform/language/tests/mocking)
- [Checks](https://developer.hashicorp.com/terraform/language/checks)
- [TFLint](https://github.com/terraform-linters/tflint)
- [Terratest](https://terratest.gruntwork.io/)
- [terraform-compliance](https://terraform-compliance.com/)
