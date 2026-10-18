---
created: 2026-08-02
updated: 2026-08-03
tags:
  - DevSecOps
  - Azure
status: draft
---
## 1. Explain Azure RBAC

>**Azure role-based access control (Azure RBAC)** is Microsoft Azure’s primary **authorization system** built on Azure Resource Manager that provides **fine-grained access management** for cloud resources.

- Authentication is typically performed by Microsoft Entra ID.
- Once authenticated, Azure Resource Manager evaluates whether a given authenticated security principal has permissions to perform the requested actions (authorization).

### 2. Key Vault vs Blob Storage access policies vs Entra ID app registrations

>**Question:** Explain the differences between Azure Key Vault, Azure Blob Storage access policies, and Entra ID (Azure AD) app registrations for secrets management in a pipeline or workload. How do you enforce least privilege?

These three serve different layers:

- **Azure Key Vault** — preferred for secrets store.
	- Access is controlled via Azure RBAC (or the older access policies); RBAC is superior because it is consistent with the rest of Azure and supports ABAC conditions.
	- I grant the calling identity (managed identity or service principal) only `Key Vault Secrets User` or `Key Vault Crypto User` on the specific vault or even on individual secrets via data-plane roles where possible. 
- **Blob Storage access policies / SAS** — for data, not secrets. 
	- I avoid storing secrets in Blob Storage. 
	- When I must give a workload access to blobs I prefer Azure AD-based authentication (Storage Blob Data Contributor/Reader) over account keys or SAS tokens. SAS tokens are time-bound and scoped but still represent a shared secret that can leak.
- **Entra ID app registrations / service principals** — the identity.
	- The app registration itself should have the absolute minimum API permissions and should be paired with a federated credential (OIDC) rather than a client secret whenever the caller is GitHub Actions, Azure DevOps, or another workload identity federation-capable platform.

Least privilege is enforced by:

1. Preferring system-assigned or user-assigned managed identities over service principals with secrets.
2. Using RBAC with narrow scopes (resource group or individual resource).
3. Applying Azure Policy to deny the creation of secrets in storage accounts and to require Key Vault soft-delete + purge protection.
4. Regular access reviews and Privileged Identity Management (PIM) for any human standing access.
5. Short-lived tokens only – never long-lived client secrets in pipelines.

### 3. Azure Monitor + Log Analytics for investigating anomalies

>**Question:** Describe the end-to-end process of using Azure Monitor + Log Analytics to investigate a deployment anomaly or failed security configuration change on a VM or container workload.

- I begin by confirming diagnostic settings are enabled on the resource (VM, AKS, Key Vault, NSG, etc.) and that logs are flowing into a central Log Analytics workspace with appropriate retention and access controls.

Investigation flow:

1. Reproduce or identify the time window of the anomaly.
2. Query the relevant tables: `AzureActivity` for control-plane changes, `AzureDiagnostics` or resource-specific tables (e.g., `KubePodInventory`, `VMConnection`, `SecurityEvent`), and `Heartbeat` / `Perf` for agent health.
3. Correlate with Azure Resource Graph or Activity Log for the exact Terraform / portal / CLI change that occurred.
4. Look for configuration drift signals (desired state vs actual) and for security-relevant events (failed managed identity token requests, NSG denies, unexpected process creations if using AMA + Change Tracking).
5. If the workload is containerized I also query Container Insights tables.
6. I build a temporary workbook or use KQL with join and summarize to produce a timeline.
7. Once root cause is identified I remediate (usually via the same IaC that should have enforced the desired state) and add an Azure Monitor alert rule or Azure Policy remediation task so the same class of issue is caught earlier next time.

I always verify that the Log Analytics workspace itself is locked down (private link, RBAC, no public ingestion where possible).


### Azure Firewall s. NSG

>**Question:** How do you configure and troubleshoot Azure Firewall rules versus NSG rules when securing administrative access points for cloud-native control planes?

- NSGs are stateful, Layer-4, and operate at subnet or NIC level. They are excellent for micro-segmentation inside a VNet. 
- Azure Firewall is a managed L3-L7 firewall that sits at the hub and can do FQDN filtering, threat intelligence, TLS inspection (with limitations), and centralized logging.

---

For administrative access to control planes I typically:
- Place Azure Firewall (or Firewall Premium) in the hub.
- Force all management traffic through it via UDRs.
- Use Firewall Policy with DNAT or application rules only for Bastion / Just-in-Time / privileged access workstations.
- Keep NSGs on the spoke subnets as a second layer (deny-all inbound except from the Firewall subnet or Bastion subnet).

Troubleshooting:

- NSG flow logs + Traffic Analytics tell me what was allowed/denied at the subnet.
- Azure Firewall logs (Application, Network, DNS proxy) go to Log Analytics; I query for the specific source IP address, destination FQDN/port, and action.
- I check effective security rules on the NIC and the Firewall policy hit counters.
- Common issues are asymmetric routing, missing route tables, or Firewall policy rule collection group priority mistakes.

I prefer Azure Firewall + Bastion + PIM over public RDP/SSH or broad NSG allows
## Provisioning infrastructure 

### 1. Provisioning a secure Azure VM with Terraform (isolated VNet, NSGs, managed identity)

>**Question:** Walk through how you would provision an Azure Virtual Machine with Terraform that is isolated in a dedicated VNet, has Network Security Groups applied, and uses a managed identity instead of stored credentials.

- I start with a modular Terraform structure:
	- A network module creates a dedicated VNet + at least two subnets: one for the VM, one for private endpoints if needed. 
	- NSGs attacked at the subnet level rather than the NIC where possible for broader protection.
	- The VM uses managed identities instead of stored credentials.
- Restrictive NSG:
	- Deny all inbound (by default).
	- Allow only the specific management source ranges (or Azure Bastion / JIT) on the required ports. 
	- Explicit deny rules higher in priority for common attack ports.
	- Outbound is also constrained where the workload permits (e.g., only to Azure services via service tags or private endpoints).
- VM:
	- Created with a system-assigned (or user-assigned) managed identity.
	- No public IP address.
	- Boot diagnostics and Azure Monitor agent enabled. 
	- Disk encryption with customer-managed keys from Key Vault when the compliance bar requires it.
	- Least-privilege RBAC: the managed identity is granted only the exact RBAC roles needed (e.g., Key Vault Secrets User on a specific vault, Storage Blob Data Reader on a specific container). I never give Contributor or Owner.
- I use `azurerm` provider with explicit depends_on only where necessary and prefer data sources + references. 
- The state file is stored in a remote backend with state locking and encryption (in Azure Blob storage or AWS S3, this is done automatically).
- After apply I verify with `az network nsg rule list`, `az vm identity show`, and a test login that confirms the identity can obtain a token for the allowed resources and nothing else. 
- I also enable Azure Policy to deny public IP addresses and enforce the presence of a managed identity on VMs in that subscription.


##  Troubleshooting scenarios
### 1. A VM can't read a Key Vault secret although it has a Managed Identity. How would you troubleshoot?

1. Verify the Managed Identity exists (in the Entra ID portal or `az vm identity show`) and confirm whether it is a System Assigned or User Assigned,