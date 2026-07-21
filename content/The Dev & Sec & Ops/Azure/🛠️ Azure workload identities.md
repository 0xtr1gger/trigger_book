---
created: 2026-07-27
updated: 2026-07-28
tags:
  - Azure
  - DevSecOps
status: draft
---
## Azure workload identities 

- Historically, applications authenticated using usernames and passwords, connection strings, API keys, or long-lived certificates. These approaches create a fundamental problem: **credentials must exist somewhere**. Once a credential exists, it must be stored, rotated, protected, audited, and eventually revoked; as well as it can also be *leaked*, *stolen*, or otherwise *compromised*.
- Azure replaces this model with **workload identities**. Applications and services can now authenticate to Azure resources **without managing long-lived credentials**. 

- Understanding Azure workload identities requires understanding three core Microsoft Entra ID (formerly Azure Active Directory) concepts:
	- **Application Objects** (App Registrations)
	- **Service Principals**
	- **Managed Identities**

>[!note]+ An **identity** is something Microsoft Entra ID can authenticate. 
>- Every authenticated request originates from some identity.

>[!note] See [[🛠️ Identities and Security Principals in Entra ID]].

## Application Objects and App Registrations

>An **Application Object** is the global, unique definition (or blueprint) of an application within Microsoft Entra ID. It describes what the application is, how it authenticates, and what permissions it requests.

>[!important] The application object itself **is not the running application**.

- An application object serves as a *template* or *blueprint* to create one or more *service principal objects*.
- The application object describes three aspects of an application — inherited by local instances:
	- How the service can issue tokens to access the application.
	- The resources the application might need to access.
	- The actions the application can take. 

>[!important] An application object **resides only in the Microsoft Entra tenant where the application was registered** (known as the application's service *home tenant*). 

- Application objects are created and managed by *app registrations*.

>[!note] An **App Registration** is the user interface entry point in the Azure portal where developers define and configure an application's identity, while the **Application Object** is the underlying technical entity (stored in the home tenant) that represents the global blueprint of that application.

>[!note] An Application Object and an App Registration usually refer to the same thing; the distinction is subtle and usually doesn't matter (depends on the context).

>[!important] An App Registration can't authentication, log in, or receive RBAC. It is merely the definition. 
>- Authentication is performed by a different object: **the Service Principal**.
## Service principals

>A **Service Principal** is the local, tenant-specific security identity created from an Application Object within a Microsoft Entra tenant, serving as the runtime instance of an application that authenticates, receives tokens, is assigned roles, and is granted permissions.

>[!important] Application = blueprint; Service Principal = actual identity.
>Analogy: Application = blueprint of a building; Service Principal = the building itself (one concrete instance).

- A service principal can authenticate using a **client secret** (username + password), **certificate**, or **federated credential**.
 
>[!note] See [`Application and service principal objects in Microsoft Entra ID — Microsoft Learn`](https://learn.microsoft.com/en-us/entra/identity-platform/app-objects-and-service-principals?tabs=browser)

## Managed identities

- Managed Identity is Microsoft's solution to eliminate credential management for Azure-hosted workloads.

>A **Managed Identity** is a special type of service principal that is automatically created, managed, rotated, and secured by Azure for an Azure resource. It enables the resource to authenticate to Microsoft Entra ID without requiring developers or administrators to manage credentials.

- A managed identity **is still a service principal**. The difference is **who manages it**.

>[!note] A Managed Identity **is** a Service Principal — managed automatically, by Azure.

- **Without** managed identities, secreted are stored somewhere, so risks exist. **With** managed identities, no credentials exist. 

### Types of managed identities

Azure provides two kinds of managed identities:
- **System-Assigned Managed Identities**
	- A system-assigned managed identity is automatically created for exactly one Azure resource and shares the same lifecycle as that resource.
	- Advantages: automatic lifecycle (created and deleted automatically with the resource); minimal administration, ideal least privilege (permissions for exactly one resource).
	- Disadvantages: can't share, can't migrate, can't survive deletion.
- **User-Assigned Managed Identities**
	- A user-assigned managed identity is an independent Azure resource that can be attached to one or more Azure resources.
	- Independent lifecycle; reusable; persistent.
	- Advantages: reusable, centralized RBAC, survives workload replacement, excellent for blue-green deployments. 
	- Disadvantages: larger blast radius if compromised; requires lifecycle management; requires cleanup.

## Federation
## Azure Instance Metadata Service (IMDS)

>The **Azure Instance Metadata Service (IMDS)** is a local, non-routable HTTP endpoint available to Azure compute resources that provides metadata and issues OAuth access tokens for managed identities.

>[!important] IMDS is **only accessible locally** at **`http://169.254.169.254/`**; it is never exposed externally.

## Practical scenarios

- Prefer **managed identities** for Azure-hosted workloads whenever supported, because they eliminate secret management and reduce credential exposure.
- Use **system-assigned managed identities** for resource-specific identities with independent permissions.
- Use **user-assigned managed identities** when identity reuse, stable permissions, or independent lifecycle management is required.
- Use **service principals** for external workloads or scenarios where managed identities are unavailable, favoring **workload identity federation** over client secrets or certificates whenever feasible.

### Case study: GitHub Actions -> Azure (Terraform, Azure CLI)


- Developer -> `git push` -> GitHub Actions workflow -> `terraform plan` -> `terraform apply` -> Azure Resource Manager -> Azure Resources. 
- The GitHub runner must authenticate to Azure. How does GitHub prove its identity to Microsoft Entra ID?
---

- Historically, **client secret** (username + password) was used, but today, the answer is **Workload Identity Federation (OIDC)**.

>[!bug]+ Historical approach: Service Principal + Client Secret
> 
> - GitHub Repository secrets:
> 	- `AZURE_CLIENT_ID`
> 	- `AZURE_CLIENT_SECRET`
> 	- `AZURE_TENANT_ID`
> 	- `AZURE_SUBSCRIPTION_ID`
> 
> - GitHub Actions executes:
> 
> ```bash
> az login \
>   --service-principal \
>   -u CLIENT_ID \
>   -p CLIENT_SECRET \
>   --tenant TENANT_ID
> ```
> - Azure validates the credentials. Entra ID issues an access token. Terraform or Azure CLI uses the token.
> - The problem: the client secret must exist somewhere. It must be generated, stored, encrypted, rotated, replaced before expiration.

### OIDC and workload identity federation

>**Workload Identity Federation** is a trust relationship between an external identity provider and Microsoft Entra ID that allows workloads to exchange externally issued identity tokens for Azure access tokens without using stored credentials.

- GitHub, in this case, becomes the identity provider.
- Microsoft Entra ID trusts GitHub.
- The authentication flow:
	- GitHub Runner -> requests OIDC token -> GitHub identity provider -> OIDC token -> Microsoft Entra ID -> access token -> Terraform -> Azure Resource Manager.
- GitHub never receives an Azure secret. Instead, GitHub provides that this runner is the intended workflow you configured. 
- The trust relationship is configured once. 
- You create a Service Principal, federated credential -> trust GitHub Repository -> trust branch -> trust environment. 
- The federated credential defines:
	- repository: `company/infrastructure`
	- branch: `main`
	- audience (optional): `api://AzureADTokenExchange`
	- Only matching workflows can authenticate.
- Step-by-step implementation:
	1. Create an App Registration -> creates the Application Objects.
	2. Create the Service Principal -> becomes the Azure identity.
	3. Assign Azure RBAC permissions (minimum permissions required).
	4. Configure federated credential (add GitHub, repository, branch, environment, audience). Now Azure trusts GitHub.
	5. The workflow calls `azure/login` using `client-id`, `tenant-id`, `subscription-id` — **no client secret**.
	6. Microsoft Entra validates these, and if the data match, it issues an access token.
	7. Terraform executes and uses the access token.



Let's talk about several very important practical use cases.

- GitHub Actions CI/CD + Azure (suppose we need to make changes to the infrastructure - the most classic example is Terraform, or sometimes we need to pull data from Azure with azure-cli)

- On-prem Jenkins (vs. Jenkins running in an Azure VM) + Azure

- What other use cases can you think of?

Please describe in the greatest detail possible how this would work. What would we use? How to implement step-by-step?

Style: academic, textbook, detailed.


## Common interview questions

- **Why are managed identities considered more secure?**
	- Because they eliminate long-lived credentials. 
	- Authentication relies on short-lived OAuth access tokens obtained from Microsoft Entra ID through the Azure Instance Metadata Service. 
	- There are no secrets to store, distribute, rotate, or accidentally expose.

- **Is a managed identity a service principal?**
	- Yes.
	- A managed identity is a **specialized service principal** whose credentials and lifecycle are managed by Azure. Internally, Microsoft Entra ID still represents it as a service principal object.

- **Can a managed identity authenticate outside Azure?**
	- No.
	- Managed identities depend on Azure infrastructure (specifically the Instance Metadata Service) to obtain tokens. Workloads running outside Azure can't use them directly.

- **Can multiple resources share a system-assigned managed identity?**
	- No.
	- A system-assigned managed identity has a strict one-to-one relationship with its Azure resource.

- **Can a user-assigned managed identity be attached to multiple resources?**
	- Yes.
	- This is its primary purpose, but it increases the potential blast radius if the identity is compromised.

- **Does assigning a managed identity automatically grant access to Azure resources?**
	- No.
	- Authentication and authorization are separate concerns. Enabling a managed identity creates an identity capable of requesting tokens, but it has **no permissions** until Azure RBAC (or another authorization mechanism such as Key Vault access policies, where applicable) grants access.




## References and further reading

- An **application registration** defines an application's identity configuration.
- A **service principal** is the tenant-specific security principal that authenticates and receives permissions.
- A **managed identity** is a service principal whose credentials and lifecycle are managed automatically by Azure.
- A **system-assigned managed identity** is permanently associated with one Azure resource and shares its lifecycle.
- A **user-assigned managed identity** is an independent Azure resource that can be attached to multiple supported Azure resources and reused across deployments.

- [`Application and service principal objects in Microsoft Entra ID — Microsoft Learn`](https://learn.microsoft.com/en-us/entra/identity-platform/app-objects-and-service-principals?tabs=browser)
- [`Securing service principals in Microsoft Entra ID — Microsoft Learn`](https://learn.microsoft.com/en-us/entra/architecture/service-accounts-principal)
