---
created: 2025-04-13
---
## Never commit `.tfstate` files


As Terraform cannot function without an up-to-date state file, many engineers consider submitting it to version control. However, this procedure comes with several risks:

- The state file contains sensitive information, such as passwords and API keys used to authenticate to cloud providers. Committing the state file may lead to exposure of those.

- Terraform may be executed against the stale or old state that you didn't pull down from version control.

### Run Terraform commands with `.var` files

- Example of a `.tfvars` file:

```Python
$ cat dev.tfvars
name=" dev-environment"
s3_terraform_bucket="dev-environment-terraform"
tag_team_name="hello-world"
```

An example of using arguments to pass variables via the command line:

```bash
terraform plan -var-file=dev.tfvars
```

With a .var file, you can easily manage environment variables and avoid running Terraform with a long list of key-value pairs `(-var foo=bar)`.


### One state file per environment


### Avoid hard-coding variables
### Validate and format Terraform code

```bash
terraform fmt
```


```bash
terraform validate
```


### Generate a `README.md` file for each module with input and output variables

### Run Terraform in a Docker container