---
created: 2024-12-03 05:51:02
color: "#7E00FF"
tags:
  - terraform
---

## Data sources

The primary kind of resource is Terraform, declared in a `resource` block, is known as a **managed resource**, or just **resource**. These resources are defined and managed by Terraform, responsible for creating, updating, and deleted respective infrastructure objects.

However, Terraform also provides functionality to keep track of resources defined and managed externally, and these are called data resources. In contrast to managed resources, Terraform can only *read* objects represented by data resources. 

Each data resource is associated with a single <mark class="hltr-violet">data source</mark>, which determines the kind of object (or objects) it reads and the arguments available for querying.

><mark class="hltr-violet">Data sources</mark> allow Terraform to fetch and use information from existing resources or services defined outside of the current Terraform configuration, without the need to manage them. 

In other words, data sources serve as a bridge between the infrastructure configuration and external resources defined elsewhere.

- Each data source belongs to a Terraform provider. 

- Data sources allow for dynamic configurations; for instance, fetching the IDs of existing resources, retrieving output properties, or querying databases for necessary details, which can then be used in other resource configurations.

>Similar to [importing](https://developer.hashicorp.com/terraform/cli/import), data sources allow Terraform to use externally defined resources in the current configuration. However, importing a resource brings that resources under the Terraform control. In contrast, a data source only allows Terraform to read the data for the current run. Any modifications to the infrastructure will not affect resources defined by data sources. 
## Defining data sources

Data sources are defined using the `data` block:

```Python
data "aws_ami" "latest" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}
```

- A `data` block tells Terraform to read from a given data source, `"aws_ami"`, and export the result under the specified local name, `"latest"`. The name will be used to refer to this resource elsewhere in the module (using the Terraform address, a combination of resource type and name, e.g., `aws_ami.latest`) as if it were a regular locally-defined resource. Therefore, the name specified for the resource should be unique among resources of the same type declared within the module.

A data source can be compared with a `SELECT` SQL query, in some sense; it is used to retrieve existing information, and nothing more. 



- Terraform reads data sources during the planning phase.

- Terraform evaluates data sources everything time `terraform plan` or `terraform apply` is run. Therefore running `terraform plan` and then `terraform apply` will run the data source’s read operation twice.

## Data source dependencies 

- There are, however, situations, when Terraform defers reading data sources (from [documentation](https://developer.hashicorp.com/terraform/language/data-sources#data-resource-behavior)):
	- At least one of the given arguments is a managed resource attribute or other value that Terraform cannot predict until the apply step.
	- The data resource depends directly on a managed resource that itself has planned changes in the current plan.
	- The data resource has custom conditions and it depends directly or indirectly on a managed resource that itself has planned changes in the current plan.

- In other words, Terraform first waits for all the required information to query the data source. In case it has not enough data, it returns an error. 

Here is where data source dependencies come useful. 

- Dependencies between data sources are managed with the `depends_on` meta-argument within `data` blocks. This argument defers Terraform from reading the data source immediately, but wait for the dependencies to finish running. 

For example, 

```Python
data "azurerm_function_app_host_keys" "example" {  
  name                = azurerm_function_app.dependency_app.name  
  resource_group_name = azurerm_function_app.dependency_app.resource_group_name  
    
  depends_on = [  
    azurerm_function_app.dependency_app
  ]
}
```

Here, `azurerm_function_app_host_keys.example` data resource depends on the `azurerm_function_app.dependency_app` resource. Thus, prior to retrieving the function host keys, Terraform wait the dependency application to finish executing. 

Notice that without the `depends_on` meta-argument, Terraform will not have enough information to query the data source. The `name` and the `resouce_group_name` parameters that the data source specifies are taken from the `azurerm_function_app.example` resource specification.

>Terraform dependencies dictate the order of data source evaluation based on the `depends_on` argument.

Thus, dependencies should be managed explicitly. Simply referring to another resource's argument is not enough. 

## Using data sources

Data sources can be queried by referring to them with `data.<data_source_name>`:

```YAML
resource "aws_instance" "my_instance" {
  ami           = data.aws_ami.latest.id
  instance_type = "t2.micro"
}
```

## Data source filters


## How it works internally

