---
created: 2024-11-22 02:14:07
color: "#7E00FF"
tags:
  - terraform
  - article
sticker: lucide//cog
---

- [[#How State files work|How State files work]]
- [[#Inspecting the contents of Terraform state files|Inspecting the contents of Terraform state files]]
- [[#Terraform backends|Terraform backends]]
- [[#State locking|State locking]]
		- [[#Force Unlock|Force Unlock]]
- [[#Refreshing the state|Refreshing the state]]
- [[#Managing Terraform state|Managing Terraform state]]
- [[#Versioning|Versioning]]
- [[#Best practices|Best practices]]

The state file essentially keeps track of the associations between resource instances in your configuration and the corresponding remote objects they represent.
## How State files work
https://blog.gruntwork.io/how-to-manage-terraform-state-28f5697e68fa

State management in Terraform is a fundamental aspect that allows it to keep track of the resources it manages. 

- Terraform keeps track of all the infrastructure resources it manages, along with their current state, in a State File, `terraform.tfstate`, written in the JSON format. The file is stored in the same directory where the `.tf` configuration is defined. 

- Given user-defined infrastructure configuration, Terraform determines the changes need to be made to the infrastructure during the `terraform apply` stage based on the information stored in the State File.

- Building an execution plan based on the current state of the infrastructure is the essence of the idempotency of Terraform operation. This strategy ensures that re-applying the same configuration multiple times will not result in undesired changes to the resources Terraform tracks - the infrastructure will remain in the configured state, no matter how many times `terraform apply` has been used. Terraform makes changes only to the resources which state in the `terraform.tfstate` file is not the same as in the `*.tf` configuration file. 

- Additionally, State Files eliminate the need to query cloud provider APIs on each `terrafrom apply` command, which improves performance. 

---

## Terraform backends

There are several types of backends, including:

- Local backends
	- The default backend, which stores state data in a local file on disk (`terraform.tfstate`)
- Remote backends
	- A backend that stores state in a remote location, most commonly on a cloud. Common remote backends include:
		- Amazon S3: Store state files in an S3 bucket, often combined with DynamoDB for state locking.
		- Terraform Cloud: A hosted service that provides state management along with advanced features like team collaboration and version control.
		- Azure Block Storage: Store Terraform state in Azure's cloud storage.
		- Google Cloud Storage (GCS): Store Terraform state files in Google’s cloud infrastructure.

When using backends, the state files are often stored encrypted. 

A backend is specified in the `terraform` block of `.tf` configuration files. For example:

```JS
terraform {
  backend "s3" {
    bucket         = "terraform-state-bucket-230598209"
    key            = "terraform.tfstate"
    region         = "us-east-1"
  }
}
```

Many remote backends support state locking, preventing concurrent applies that could corrupt the infrastructure: when running `terraform apply`, Terraform locks the state file to prevent concurrent modifications that could lead to conflicts. Many cloud providers also offer additional automatic mechanisms for state locking.

---

Local state files are not always suitable for team collaboration. For example, when all the project files, including Terraform configuration, are stored inside a remote repository, say, on GitHub or GitLab, and Terraform commands run automatically as part of a CI/CD pipeline (for example, with Jenkins, GitHub Actions, or GitLab CI), it is essential to store the file remotely, for Terraform to be able to access the file regardless on the machine where it runs.  

## State locking

>Terraform state locking is a mechanism that prevents concurrent access to the same Terraform state file from multiple users or processes.

State locking is necessary to protect the Terraform state file when a Terraform is performing modifications to the infrastructure. 

With state locking, only one operation can modify the state at a time. If another operation attempts to access the state while it's locked, it will fail with an error message indicating that the state is currently locked.

---
the world without state locking 

Without locking, multiple users or CI/CD processes could modify the same state simultaneously, which will lead to corruption, inconsistent states, and chaos in infrastructure. 
Say, if two users nearly simultaneously push to a GitHub repository that triggers a GitHub Actions workflow, which in turn, invokes Terraform commands, this means that the state files is supposed to be accessed by two concurrently running workflows at the same time. One issues `terraform apply`, which modifies something in the infrastructure, then another, while the first haven't yet documented the modifications to the state file - and so on: the consequences are unpredictable.

---



State locking must be supported by the remote backend. 

Different backends implement state locking in various ways. For example, 

- S3 with DynamoDB (AWS)
	- For a state file stored in an S3 bucket, state locking can be configured with DynamoDB. 
	- A DynamoDB table is used to store lock information. The table has a single partition key, `LockID` (Lock Identifier, typically derived from the name of the S3 bucket), used to identify the S3 object being locked, that is, the State file.
	- When a Terraform operation is initiated, such as with `terraform apply`, Terraform attempts to create a new entry in the DynamoDB table using that `LockID`. If the lock for the State file already exists, this will mean that the lock is busy, and the operation will fail.  
	- When an operation is finished, Terraform sends a request to DynamoDB to release the lock. The entry with the respective `LockID` is then deleted from the name. 

- Azure Blob Storage (Azure)
	- For Azure Blob Storage, Terraform uses the blob leasing feature to implement state locking. A lease is a temporary lock on a blob that prevents other Terraform processes from modifying or deleting the blob until the lease expires or is explicitly released.
	- When an operation (e.g., `terraform apply`) begins, Terraform will attempt to acquire a lease on the blob storing the state file. This lease prevents other processes from modifying or deleting the blob while the lease is active. If another operation attempts to access the blob while the lease is active, it will fail with an error indicating that the blob is currently leased.

In Terraform Cloud or HashiCorp Consul solutions, the lock is managed automatically through built-in mechanisms, but the principle should be somewhat similar. 

#### Force Unlock

Sometimes the state file may remain locked even when no operation is currently accessing the State file, for example, due to an interrupted operation, error, or bug. For such situations, there is a fallback in the form of the `force-unlock` command.

`force-unlock` is used to manually unlock the state file when it is being locked by another process;

```bash
terraform force-unlock [options] LOCK_ID
```

The location of the Lock ID depends on the backend. It is typically stored alongside with the state file, and has the name `*.tfstate.lock`. 

## Refreshing the state

The `terraform apply` command with the `-refresh-only` option is used to update the state file to match the current state of the infrastructure managed by Terraform. The command does not make any modifications to the underlying infrastructure, but rather updates the state file by querying information about the current state of affairs using the Cloud provider API.

```bash
terraform apply -refresh-only
```


## Defining remote backends

- It's a good practice to store your state files remotely rather than keeping them on your local machine. To achieve this, you can specify the location of the remote state file by using a `backend` block within the `terraform` block. Typically, you'd include this in your `main.tf` file.

>**Azure** blob storage

```Python
terraform {
  backend "azurerm" {
    resource_group_name  = "tfresourcegroup"
    storage_account_name = "tfstorageaccount"
    container_name       = "tfstate"
    key                  = "terraform.tfstate"
  }
}
```

>**AWS** S3

```Python
terraform {
  backend "s3" {
    bucket = "terraform-state-bucket"
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}
```

>**GCP** GCS

```Python
terraform {
  backend "gcs" {
    bucket  = "terraform-state-bucket"
    prefix  = "terraform/state"
  }
}
```

- It's a good practice to isolate your state files to minimize the potential impact of any errors or changes. Typically, projects are organized within a single folder and share a single state file for all their resources. However, this can be risky because any configuration mistakes could alter the state file and lead to unintended consequences across all your resources.

>A more reliable approach is to employ multiple state files for different parts of your infrastructure. By logically separating resources and assigning them their own state file in the backend, you ensure that modifications to one resource won't impact the others. Using distinct state files for various environments is also advisable to maintain a clean separation.


## Managing Terraform state


Terraform provides a command to manage the state file, `terraform state`. It has many subcommands used to perform various operations regarding `terraform.tfstate`, and below is the table summarizing them.

| Command                            | Description                                         |
| ---------------------------------- | --------------------------------------------------- |
| `terraform state list`             | List resources currently tracked in the state file. |
| `terraform state show`             | Show a resource in the state.                       |
| `terraform state rm`               | Remove instances from the state.                    |
| `terraform state mv`               | Move an item in the state.                          |
| `terraform state pull`             | Pull current state and output to stdout.            |
| `terraform state push`             | Update remote state from a local state file.        |
| `terraform state replace-provider` | Replace provider in the state.                      |

- In Terraform, the `terraform state rm` command serves the purpose of removing items from the state file. It's important to note that removing an item from the state file doesn't physically destroy the resource; instead, it signifies that Terraform will no longer manage it.

```bash
terraform state rm aws_instance.my_example
```

Here is an example of usage of the `terraform state list` command, which lists all the resources currently tracked by Terraform:

```bash
terraform state list
```
```bash
azurerm_linux_virtual_machine.api_vm_cloud_resume
azurerm_network_interface.api_vm_nic
azurerm_network_interface_security_group_association.nsg_nic_association
azurerm_network_security_group.cloud_resume_nsg
azurerm_public_ip.api_public_ip
azurerm_resource_group.rg_vm
azurerm_subnet.api_subnet
azurerm_virtual_machine_extension.vm_extension
azurerm_virtual_network.cloud_resume_vnet
```

>These resources are taken from my Cloud Resume Challenge lab. In the lab walk-through, I show practical usage of Terraform and Azure.  

The `terraform state show` command provides a more detailed state information about a particular resource referenced by its Terraform address. For example,

```bash
terraform state show azurerm_linux_virtual_machine.api_vm_cloud_resume
```
```
resource "azurerm_linux_virtual_machine" "api_vm_cloud_resume" {
    admin_username                                         = "azureadmin"
    allow_extension_operations                             = true
    availability_set_id                                    = null
    bypass_platform_safety_checks_on_user_schedule_enabled = false
    capacity_reservation_group_id                          = null
    computer_name                                          = "hostname"
    dedicated_host_group_id                                = null
    dedicated_host_id                                      = null
    disable_password_authentication                        = true
    disk_controller_type                                   = "SCSI"
    ...
```

The `rm` subcommand removes a resource form the state without destroying the actual resource itself:

```bash
terraform state rm <address>
```

The operation may be inverted with the `terraform import` command, which allows Terraform to start tracking existing infrastructure resources.

`terraform state mv` moves a resource from one Terraform address in the state file to another. It can be used both for mere resource renaming, or for more complex operations like moving items between modules, or even moving entire modules.

```bash
terraform state mv <source> <destination>
```

The `terraform state pull` command retrieves the current state of the infrastructure from the remote backend and prints it to standard output.

```bash
terraform state pull
```
```bash
{
  "version": 4,
  "terraform_version": "1.9.5",
  "serial": 12,
	...
```

On the contrary, `terraform state push` updates the remote state file in the configured backend with the state stored locally. This command is not commonly used since remote state is usually managed automatically.

```bash
terrafrom state push <path-to-the-state-file>
```

The `replace-provider` subcommand is used to replace the provider of a resource in the state file with a new one.

```bash
terraform state replace-provider <old> <new>
```

For example, 

```bash
terraform state replace-provider aws aws2
```

## Versioning

TBD
## Best practices

- **Separate State Files**: Understand the benefits of having separate state files for different environments (e.g., dev, staging, production).
- **Avoid Manual Modifications**: Know the risks associated with manually editing state files.
- **Use of Workspaces**: Learn how workspaces manage separate states for different environments in the same configuration.
- **Sensitive Data in State Files**: Awareness of sensitive data exposure in state files and methods to handle sensitive values securely.


