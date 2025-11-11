---
created: 2025-11-05 11:20:22
---

## Creating resources conditionally

In Terraform, you can create resources conditionally, based on variables values. For this, you can use ternary operators, conditions, and the [`count`](https://developer.hashicorp.com/terraform/language/meta-arguments/count) meta-argument.

>[!note] The `count` meta-argument can be used with `resource` blocks, `ephemeral` blocks, and `module` blocks.

- To create a resource only if a variable is set to `true`:

```Python
resource "<resource_type>" "<resource_name>" {
	count = var.variable_to_check ? 1 : 0
	# ...
}
```

This creates a resource when `variable_to_check` is `true` (`count = 1`), and creates nothing when `false` (`count = 0`).

- You can create resources only if a variable is set to a specific value:

```Python
variable "environment_name" {
  type = string
}

resource "<resource_type>" "<resource_name>" {
	count = (var.environment_name == "dev") ? 1 : 0
  # ...
}
```

This creates a resource only when `environment_name` is set to `dev`.

- Conditions can be combined using logical operators:

```Python
variable "environment_name" {
  type = string
}

resource "<resource_type>" "<resource_name>" {
	count = (var.environment_name == "dev" || var.environment_name == "perf") ? 1 : 0
  # ...
}
```

This creates a resource when `envronment_name` is set to `dev` or `perf`.

- In cases when the resource should be created only if a variable is set to one of the specified values, the cleaner approach is to use a list:

```Python
variable "environment_name" {
  type = string
}

locals {
  non_production_envs = ["dev", "test", "perf"]
  is_non_prod        = contains(local.non_production_envs, var.environment_name)
}

resource "azurerm_application_insights" "monitoring" {
  count               = local.is_non_prod ? 1 : 0
  name                = "appinsights-${var.environment_name}"
  resource_group_name = "my-rg"
  location            = "eastus"
  application_type    = "web"
}

```


Or, with negation:


```Python
locals {
  production_envs = ["prod", "production"]
  is_production  = contains(local.production_envs, var.environment_name)
}

resource "azurerm_storage_account" "test_data" {
  count               = !local.is_production ? 1 : 0
  name                = "teststorage"
  resource_group_name = "my-rg"
  # ... configuration
}
```

