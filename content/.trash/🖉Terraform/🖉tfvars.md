---
created: 2025-01-19
---
Terraform uses variable files (commonly with a `.tfvars` extension) to manage variable values outside of the main configuration files (like `.tf` files). This allows you to separate configuration logic from variable data, making your Terraform configurations more organized and easier to manage. Below, we'll explore `.tfvars` files, their purpose, and how they compare with module variables such as local, input, and output variables.