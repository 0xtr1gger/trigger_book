---
created: 2026-10-05
updated: 2026-10-06
---

## Infrastructure as Code 

>**Infrastructure as Code (IaC)** is the practice of managing and provisioning infrastructure through machine-readable definitions rather than manual processes or interactive configuration.

- Infrastructure components such as networks, compute, storage, identity, DNS, databases, users, and security policies are treated as code.
- The definition becomes the authoritative, versioned, reviewable, and reproducible description of the infrastructure.
---
- IaC addresses:
	- **Snowflake servers** — manually configured hosts diverge over time.
	- **ClickOps** — console changes lack a reviewable representation of intent.
	- **Configuration drift** — actual infrastructure diverges from intended state.
	- **Slow/error-prone provisioning** — manual procedures do not scale reliably.
	- **Environment inconsistency** — environments differ in ways that invalidate testing.
	- **Limited auditing** — changes can't reliably be attributed, reviewed, or reverted.
---
- Core properties:
	- **Idempotency** — repeatedly applying the same definition produces the same result; a converged system requires no further changes.
	- **Convergence** — the tool compares current and desired state and performs the operations required to eliminate the difference.
	- **Reproducibility** — the same definition and inputs produce equivalent infrastructure across environments, accounts, or regions.
	- **Version control** — definitions are stored in a version-control system such as Git, which provides an ability to review changes history and roll back. 
	- **Review** — infrastructure changes can follow PR/approval workflows; planning tools such as `terraform plan` expose expected changes before execution.
	- **Testing** — definitions can be linted, statically analysed for security misconfigurations, evaluated against policies, and deployed into disposable environments for integration testing.
	- **Self-documentation** — the definition is the authoritative infrastructure description.
## Declarative vs. imperative

- **Declarative IaC** defines **what** the desired end state is; the tool determines the required operations.
    - Removing a resource from the definition causes it to be removed from the desired state and therefore normally destroyed.
    - Examples: Terraform, OpenTofu, CloudFormation, Bicep, Kubernetes manifests, Crossplane.
- **Imperative IaC** defines **how** to reach the desired state as an ordered sequence of operations.
    - The result depends more directly on the starting state.
    - Idempotency must be implemented explicitly.
    - Removing a previous operation does not undo its effects.
    - Examples: shell/Python scripts, cloud CLI/SDK calls, Ansible.

> [!note]+ The distinction is not absolute:
> 
> - Ansible playbooks are procedural task sequences, but modules commonly declare idempotent target states such as `state: present`.
> - Pulumi and AWS CDK use general-purpose languages to construct a declarative resource graph that an engine reconciles.
> - Terraform is declarative, but provisioners such as `local-exec` and `remote-exec` introduce imperative operations.
## Declarative and imperative

IaC tools differ in whether the author describes the result or the procedure.

- **Declarative** — *what* the end state must be
	- The author specifies the desired end state: which resources exist and with which properties. The tool determines the operations, their order, and whether any are necessary at all.
	- Removing a resource from a declarative definition causes the tool to delete it, because the resource is no longer part of the desired state.
	- Examples: Terraform, OpenTofu, AWS CloudFormation, Azure Bicep, Kubernetes manifests, Crossplane.
- **Imperative** — *how* to reach the end state
	- The author specifies the exact sequence of commands. The result depends on the starting state, and idempotency must be implemented explicitly (for example, "create the bucket only if it does not exist").
	- Removing a step from an imperative script does not undo what that step previously did.
	- Examples: shell scripts, Python scripts calling a cloud SDK, cloud CLI invocations.

The distinction is not strictly binary:

- Ansible playbooks are an ordered list of tasks (procedural), but each module is idempotent and describes a target state (`state: present`), so a playbook behaves declaratively at the task level.
- Pulumi and AWS CDK use general-purpose imperative languages to *construct* a declarative resource graph, which an engine then reconciles.
- Terraform is declarative, but provisioners and the `local-exec`/`remote-exec` mechanisms reintroduce imperative steps (see [[Terraform resources#Provisioners]]).

## Push vs. pull

- **Push** — a central controller/workstation/CI runner connects to targets or provider APIs and applies changes.
    - Examples: Terraform, Ansible, pipeline-triggered CloudFormation.
    - Changes occur when the tool runs; drift is not continuously corrected.
    - The controller requires highly privileged credentials and is therefore a high-value target.
- **Pull** — an agent/controller near the target retrieves desired state and reconciles it.
    - Examples: Puppet/Chef agents, Argo CD, Flux, Crossplane.
    - Enables continuous automatic drift correction.
    - Credentials can be scoped per target, but each agent is an execution point that must be secured.
## Mutable vs. immutable infrastructure

- **Mutable infrastructure** modifies existing instances in place.
    - Typical operations: package upgrades, configuration changes, service restarts.
    - In-place changes can partially fail and accumulate configuration differences.
	- Traditional configuration-management tools include Ansible, Puppet, Chef, and Salt.
- **Immutable infrastructure** replaces rather than modifies deployed components.
    - Build a new versioned artifact, deploy new instances, then remove the old ones.
    - Examples of artifacts: machine images and container images.
    - Simplifies rollback and eliminates host-level drift.
    - Common tooling: Packer, Docker, and provisioning/orchestration systems capable of replacement.

- Terraform supports both models. Provider schemas determine whether an attribute can be updated in place or requires resource replacement. `create_before_destroy` and `replace_triggered_by` can be used to implement deliberate replacement-based rollouts.

## Provisioning vs. configuration management

- A typical infrastructure lifecycle has two distinct stages:
	1. **Infrastructure provisioning** — create the platform: networks, subnets, firewalls, VMs, managed databases, IAM roles, DNS records.
	2. **Configuration/deployment** — configure the OS and services and deploy the application.
- Example:
	1. Create VPC and subnets — provisioning.
	2. Create EC2 instances and security groups — provisioning.
	3. Install Docker/runtime dependencies — configuration management.
	4. Harden OS and service configuration — configuration management.
	5. Deploy the application — deployment.

- Terraform is primarily suited to steps 1–2; steps 3–5 are typically handled by configuration management, image building, or a deployment platform.

## IaC tool categories

- **Provisioning** — manages infrastructure through provider APIs: Terraform, OpenTofu, Pulumi, Crossplane.
- **Cloud-native templates** — provider-specific infrastructure definitions: CloudFormation, AWS CDK, ARM templates/Bicep, Google Cloud Infrastructure Manager.
- **Configuration management** — configures existing hosts: Ansible, Puppet, Chef, Salt.
- **Image building** — creates immutable machine/container images: Packer, Docker, Buildah.
- **Orchestration/reconciliation** — continuously reconciles workloads/resources with declared state: Kubernetes, Argo CD, Flux.
---
- Cloud-native template services generally store deployment state in the provider rather than requiring a user-managed state file, but are provider-specific.

- Google Cloud Deployment Manager is deprecated in favor of Infrastructure Manager, which provides managed Terraform execution.

## Configuration drift

>**Configuration drift** is the divergence between infrastructure defined in code and infrastructure that actually exists.

- Common causes:
	- Manual console/CLI changes.
	- External automation such as autoscaling, provider defaults, or security remediation.
	- Partial or failed IaC runs.
	- Multiple IaC configurations managing overlapping resources.

- Consequences:
	- IaC may overwrite legitimate emergency changes.
	- The definition stops accurately describing reality.
	- Unreviewed changes can introduce security weaknesses.

- Typical controls:
	- Periodically run a plan and alert on unexpected changes.
	- Restrict production write access to the IaC pipeline; use a documented break-glass process.
	- Codify legitimate manual changes immediately.

## GitOps

>**GitOps** is an operating model where Git stores the declarative desired state and automated agents continuously reconcile the running system against it.

- OpenGitOps defines four principles:
	1. **Declarative** — desired state is declaratively defined.
	2. **Versioned and immutable** — desired state has immutable/versioned history.
	3. **Pulled automatically** — agents automatically retrieve desired state.
	4. **Continuously reconciled** — agents continuously observe and reconcile actual state.
---
- Argo CD and Flux managing Kubernetes are canonical GitOps implementations.
- Terraform is primarily push-based. A merge-triggered Terraform pipeline provides declarative, versioned state, but not inherently automatic pull or continuous reconciliation.
- Scheduled Terraform plans/applies, Terraform controllers, or Crossplane can approximate/implement continuous reconciliation.
## Security implications

- IaC moves infrastructure security into the software supply chain:
	- A vulnerable or misconfigured shared module can propagate the issue to every consumer.
	- Secrets can leak through definitions, variable files, state files, and CI/CD logs.
	- IaC pipelines often hold credentials capable of modifying or destroying large portions of the environment.    
	- Third-party modules/providers/plugins execute with the permissions available to them.
	- IaC also makes infrastructure security **reviewable before deployment** through:
		- Static analysis.
		- Policy as code.
		- Plan review.
		- Automated testing.
	
## References

- [OpenGitOps principles](https://opengitops.dev/)
- [HashiCorp — What is Infrastructure as Code](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/infrastructure-as-code)
