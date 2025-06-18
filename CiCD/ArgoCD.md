

- [x] What is this
- [x] How it works (briefly)
- [x] Workflow example 
- [x] How it's set up
- [x] Benefits
- [ ] Verify everything

TBD:
- Lifecycle hooks such as PreSync, Sync, and PostSync
- Sync policies


## Argo CD

>[Argo CD](https://argo-cd.readthedocs.io/en/stable/) is CD tool designed specifically for Kubernetes environments. It acts as a Kubernetes-native controller that continuously monitors the live stat of applications running in Kubernetes clusters and compares it against the desired target state defined declaratively in Git repositories.
>Written in Go, Argo CD was officially released in 2019 and now part of the Cloud Native Computing Foundation (CNCF) ecosystem.

- Argo CD helps you manage application using Kubernetes deployment YAML file stored in a Git repository.

**Features:**

- Argo CD can automatically/manually synchronize the live state of Kubernetes applications with the declared state stored in Git. 
- When discrepancies between the states arise (a change is detected), it's is called **OutOfSync**. 
- If the application hasn't been changed, it's said that this application is **Synced**. 
- Argo CD supports a wide range of Kubernetes manifest formats and configuration management tools, including:
	- Plain YAML/JSON declarations
	- Helm charts
	- [Kustomize](https://kustomize.io/) overlays
	- [Jsonnet](https://jsonnet.org/)
	- Custom plugins

## Argo CD architecture

The architecture of Argo CD consists of:

- **API server**
	- Exposes **REST and gRPC APIs** for application management, status reporting, sync operations (e.g., sync, rollback), and user-defined actions.
	- Exposes the **Web UI**.
	- Manages **authentication and authorization** by integrating with external identity providers (OIDC, LDAP, SAML, GitHub, GitLab, etc.) and enforcing RBAC.
	- Handles repository and Kubernetes **cluster credential management**, stored securely as Kubernetes secrets (securely, only if you configure encryption...).
	- Listens for Git webhook events to trigger sync events.

- **Repository server** (repo server)
	- Caches Git repositories locally.
	- Generates Kubernetes manifests from the cached Git data (e.g., plain YAML, Helm charts, Kustomize, Jsonnet, and custom plugins).
	- Takes inputs like repository URL, revision (branch, tag, commit), application path, and templating parameters to produce the desired Kubernetes manifests.

- **Application controller**
	- A **Kubernetes controller** that continuously monitors the live state of applications deployed in the cluster.
	- This is namely the component that **compares the live state against the desired state** of the cluster.
	- Detects whether the app is **OutOfSync** or **Synced**.
	- Executes synchronization operations to reconcile differences (triggered automatically or manually).
	- Manages lifecycle hooks such as PreSync, Sync, and PostSync to support complex deployment strategies like blue/green or canary releases.

Under the hood, Argo CD (to be precise, the Argo CD API server) interacts with the underlying Kubernetes cluster API to read and modify cluster state.

Optional components:
- **Redis cache**
	- Caches Kubernetes API and Git repo data to improve performance.
- **Dex** or other AuthN provider
	- Provides authentication and SSO integration

## How Argo CD works: example workflow

Suppose you have a project where a development team manages a Kubernetes application using Argo CD with GitOps principles. 

Example applications:
- https://github.com/argoproj/Argo CD-example-apps
- https://github.com/bukurt/Argo CD


>Your Kubernetes manifests (YAML files, Helm charts, Kustomize overlays, etc.) live in Git, and Argo CD ensures your cluster reflects exactly what’s in Git.
- Argo CD implements GitOps by continuously monitoring Git repositories and synchronizing Kubernetes clusters to match the desired state defined in Git.

### Initial setup
#### 1. Project setup

Your project repository will have:
- **Kubernetes manifests/Helm charts/Kustomize overlays** — the desired state of the cluster.
- **Application definition for Argo CD** — a YAML file describing an Argo CD application resource. This tells Argo CD where to find your manifests in Git and which cluster/namespace to deploy to.

```PowerShell
my-app-repo/
├── base/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── kustomization.yaml
├── overlays/
│   ├── dev/
│   │   └── kustomization.yaml
│   ├── staging/
│   │   └── kustomization.yaml
│   └── prod/
│       └── kustomization.yaml
└── Argo CD-app.yaml   # Argo CD Application resource definition
```

#### 2. Argo CD installation and access

Before using Argo CD, your install it into your Kubernetes cluster:

```bash
kubectl create namespace Argo CD

kubectl apply -n Argo CD -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

This deploys all Argo CD components:
- API sever
- Repository server
- Application controller
- UI

You then can forward the Argo CD API server port to your local machine or use an Ingress:

```bash
kubectl port-forward svc/Argo CD-server -n Argo CD 8080:443
```

Now, the Web UI can be accessed at `https://localhost:8080`. Alternatively, you can use a CLI tool `Argo CD`.

Why separate namespace?
- Argo CD runs as a set of Kubernetes components (API server, repository server, application controller, etc.) inside your cluster.
- Argo CD installs its own CRDs (e.g., `Application`, `AppProject`) and controllers that operate within the cluster.
- Security.

#### 3. Create an Argo CD application

The Argo CD Application resource is the bridge between your Git repository and your Kubernetes cluster. It tells Argo CD:
- Which Git repo to monitor
- Which path inside the repo contains manifests
- Which branch/tag/commit to track
- Which Kubernetes cluster and namespace to deploy to
- Sync policy (manual or automated)

Example:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: example-app
  namespace: Argo CD
spec:
  project: default
  source:
    repoURL: 'https://github.com/username/repo.git'
    targetRevision: HEAD
    path: overlays/dev
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: example-namespace
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

- This defines an application named `example-app` that deploys manifests from the `overlays/dev` directory of the Git repo to the `example-namespace` namespace in the current cluster.
- `automated` sync means Argo CD will automatically apply changes detected in Git and prune deleted resources.
- `selfHeal` means Argo CD will correct any manual drift from the desired state.

Then you apply this application manifest to the cluster:

```bash
kubectl apply -f Argo CD-app.yaml -n Argo CD
```

#### 4. Repository server clones the Git repository and generates manifests

- Argo CD’s repository server clones the Git repo and caches it locally.
- It generates Kubernetes manifests from the specified path (`overlays/dev`) using Kustomize or Helm as needed.

Your Git repository contains declarative Kubernetes manifests, Helm charts, Kustomize overlays, or other supported formats. These define the _desired state_ of your application resources.
- Argo CD’s **Repository Server** clones the Git repo and locally caches it inside the cluster. It then _processes_ these source manifests using the appropriate toolchain:
    - If plain YAML, it reads them as-is.
    - If Helm charts, it runs `helm template` with your specified values to generate raw Kubernetes manifests.        
    - If Kustomize overlays, it runs `kustomize build` to produce the final manifests.
- The output of this generation step is a set of fully rendered Kubernetes manifests representing the _actual_ desired state that can be applied to the cluster. These are the manifests Argo CD uses to compare against the live cluster state and to apply changes during sync.
- These newly generated manifests are cached in-memory or in Argo CD server's internal cache (and possibly Redis for performance), rather than stored on the disk. They exist transiently to be compared and applied.

Argo CD needs the _fully rendered_ Kubernetes manifests to:

1. Compare the desired state (from Git) with the live state in the Kubernetes cluster.
2. Apply changes directly via the Kubernetes API server during sync operations.
#### 5. Application controller compares desired vs. live states

- The Application Controller queries the Kubernetes API to get the current live state of the resources in `example-namespace`.
- It compares this live state with the desired manifests generated from Git.
	- If the live state matches the desired state, the application status is `Synced` and `Healthy`. 
	- If differences exist (e.g., new image tag in Git, missing resource in cluster), the status is `OutOfSync` => since `syncPolicy.automated` is enabled, Argo CD automatically applies the changes to the cluster, creating/updating/deleting resources as needed (if sync is manual, this can be triggered via the UI or CLI).
- Argo CD supports lifecycle hooks (PreSync, Sync, PostSync) to run custom jobs during sync.
- If a deployment fails or you want to revert, you can rollback to any previous Git commit, and Argo CD will restore the cluster state accordingly.

#### 6. Monitoring

- Argo CD continuously monitors both the Git repo and the cluster state, ensuring any drift is detected and corrected if configured.
- Users can view application status, diffs, and history via the Web UI or CLI.

### A change has occurred. What's then?

- **1. Detect the change in the repository**  
	- Argo CD continuously monitors the configured Git repositories either by polling or via webhook notifications triggered by Git hosting services (GitHub, GitLab, Bitbucket). 
	- When you push changes (e.g., update manifests, Helm values, or source code that affects manifests), Argo CD notices the new commit.
    
- **2. Repository server updates cache and generates new manifests**
	- The repository server:
		1. Pulls the latest commit
		2. Updates its cache
		3. Regenerates the Kubernetes manifests from the updated source (Helm templates, Kustomize overlays, or plain YAML).
    
- **3. Application controller compares desired vs live state**
	- The Application controller compares the newly generated desired state with the current live state in the Kubernetes cluster. It determines whether the application is `Synced` or `OutOfSync`.
    
- **4. Sync Operation (automatic or manual)**
    - If Argo CD is configured with **automated sync**, it will immediately apply the changes to the cluster by creating, updating, or deleting Kubernetes resources to match the new desired state.
    - If sync is manual, Argo CD will notify you (via UI or CLI) that the application is OutOfSync and await your command to sync.

- **5. Monitor Sync Progress and Health**
	- Argo CD monitors the deployment progress and resource health, reporting status back to the UI and CLI. If lifecycle hooks are defined (PreSync, Sync, PostSync), they are executed accordingly.
    
- **6. Drift Detection and Self-Healing**
	- If manual changes are made directly to the cluster that diverge from Git, Argo CD detects this drift on its next reconciliation cycle and can automatically revert the changes if `selfHeal` is enabled, ensuring the cluster always matches Git.
## Defining the desired state of the cluster with Argo CD

- The desired state is defined **declaratively** in Git repositories as Kubernetes manifests or Helm/Kustomize configurations. This includes all resources such as Deployments, Services, ConfigMaps, etc
- Argo CD uses its own **Application Custom Resource Definition (CRD)** to define an application. This CRD specifies:
- - The Git repository URL
    - The path within the repo where manifests are located
    - The target Kubernetes cluster and namespace
    - The revision (branch, tag, or commit) to deploy
    - Parameters for Helm or Kustomize, if applicable

- This Application CRD is either created via the CLI, Web UI, or declaratively as YAML applied to the Argo CD namespace. Argo CD then continuously monitors this Application resource and reconciles the cluster state accordingly
## Benefits

**Declarative. You cluster always matches Git.**

- **Argo CD automates synchronization between Git repositories and Kubernetes clusters.** You push a change, and Argo CD propagates — deploys — this change to the Kubernetes cluster. This **reduces manual errors**.
	- Why? **No manual `kubectl` commands — Argo CD deploys everything from Git for you.**
	- Less time, less errors — less engineers to deal with Kubernetes deployments.

- Discrepancies between the cluster and Git? Argo CD will handle them. Actually, it can be configured what to do on OutOfSync events, such as alerting admins or making changes. 
	- **Less configuration drift and consistency.**
	- So, if an engineer decides to make a quick change manually with a `kubectl` command, but not through the Git repository, this will result in differences between the repository state and actual cluster state. Argo CD will tell you about this and, if you want, automatically revert any changes not declared in Git. 
	- This way, there won't be any unexpected issues with subsequent deployments. Everything is version-controlled and transparent.

- Integrations with **CI (GitHub Actions)**:
	1. **GitHub Actions**: automatically builds, tests, **pushes** container images or updates manifests in Git.
	2. **Argo CD**: detects these changes and deploys them to the cluster (say, in Azure).

- Web UI and CLI.

>You make a change to the code, then change Kubernetes manifests somehow (either manually or with CI), and then Argo CD deploys what you've done.

- Centralized deployment management
	- Argo CD provides a **single dashboard** and CLI to manage deployments across multiple Azure clusters, namespaces, and teams.

- Security
	- Argo CD can integrate with **Microsoft Authenticator** or any other OIDC (OpenID connection) authentication. +RBAC.
	- You want to change something? Please, first authenticate, then Argo CD will check whether you're authorized to do what you want to do.

- **Automates deployments and rollbacks.**
- Enforces **Git as a single source of trust** — version-control and transparency.
- Can manage multiple clusters from a centralized control plane (can also group applications via Projects).

- Provides real-time status of application health, sync state, and drift detection. **Troubleshooting is easier.**
- **Very scalable.**

---
**Not a strict comparison! Just thoughts!**
To my mind, in some sense, Argo CD is similar to Terraform configured to run automatically on repository changes, except Terraform doesn't continuously monitors anything (only writes changes to a state file).
- The main difference is that Terraform manages cloud resources and brings the cloud infrastructure to the desired state declared in HCL configuration, but Argo CD is specifically designed to work with Kubernetes. 
- With Terraform, you don't need to run Azure CLI commands manually or touch Azure Portal web GUI — Terraform uses Azure API directly and does everything to bring the infrastructure to whatever you specified.
- Argo CD is the same in this sense. No `kubectl` commands, no manual interventions to the Kubernetes cluster — just you and your Kubernetes manifests.


## ArgoCD vs. Crossplane

| Tool           | Purpose                                                                    | Core Functionality                                                                                                                                          |
| -------------- | -------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Argo CD**    | A Kubernetes-native CD tool implementing GitOps principles.                | Automates deployment and lifecycle management of Kubernetes applications by continuously syncing cluster state with Git repositories.                       |
| **Crossplane** | A Kubernetes-native infrastructure provisioning and management tool (IaC). | Extends Kubernetes to provision and manage cloud infrastructure resources (databases, cloud services, clusters) declaratively via Kubernetes APIs and CRDs. |


- **Argo CD** focuses on **application delivery**:
	- Manages Kubernetes workloads (Deployments, Services, ConfigMaps, etc.) by monitoring Git repos with manifests, Helm charts, or Kustomize overlays.
    - Ensures that Kubernetes clusters' application state matches the desired state declared in Git, enabling continuous deployment with automated or manual sync.
    - A GitOps operator for application lifecycle management.

- **Crossplane** focuses on **infrastructure provisioning and management**:
    - Transforms Kubernetes into a **universal control plane** for infrastructure across multiple cloud providers (AWS, Azure, GCP) and on-premises environments.
    - Uses Kubernetes CRDs to declaratively define infrastructure components like databases, caches, buckets, and even entire Kubernetes clusters.    
    - Allows teams to manage IaC using Kubernetes-native tooling and GitOps principles.
    - Supports composing infrastructure resources into reusable abstractions (Compositions) for platform engineering.

Example:

- **Argo CD:** You store your Kubernetes application manifests (or Helm charts) in Git. Argo CD continuously monitors this repo and deploys your app to Kubernetes clusters, ensuring the live state matches the Git state. If you update your app’s image tag in Git, Argo CD detects it and updates the cluster automatically.
- **Crossplane:** You want to provision an AWS RDS database instance declaratively. You write a Kubernetes CRD manifest describing the RDS instance (region, size, credentials). Crossplane reconciles this manifest and provisions the actual RDS instance on AWS. If you update the manifest, Crossplane updates the infrastructure accordingly.

## How Crossplane, Argo CD, and Terraform can be used together

- **Terraform** is often used for provisioning foundational infrastructure components (networks, clusters, core cloud resources) especially **outside Kubernetes**.

- **Crossplane** manages infrastructure resources **from inside Kubernetes**, i.e., resources that are *tightly coupled with Kubernetes applications*. It is ideal when you want your infrastructure to be managed declaratively alongside Kubernetes workloads.

- **Argo CD** handles CD of Kubernetes applications and can also deploy Crossplane manifests.

- **GitHub Actions** or any CI/CD system orchestrates the pipeline, running Terraform or pushing manifests to Git repos watched by Argo CD.
### Example workflow

- **Goal**: Deploy a Kubernetes application AKS, provision Azure infrastructure (database, storage) declaratively, and automate the entire workflow with CI/CD.
- **Tools**:
	- Terraform 
	- Crossplane
	- ArgoCD
	- Azure


1. Terraform provisioning
	- Use Terraform to provision foundational Azure resources (e.g., Azure RGs, VNets, AKS cluster itself, etc.).

2. Install Crossplane into AKS
	- Can be installed with Helm or `kubectl`.

3. Define Azure infrastructure resources as Crossplane manifests
	- Write Crossplane manifests to provision Azure resources tightly coupled with the K8s app (e.g., Azure SQL database instance, Blob storage container, Redis cache, etc.). These manifests live in a Git repo watched by Argo CD (could be the same repo as app manifests or separate).

4. Define Kubernetes manifests
	- Define Kubernetes manifests or Helm charts for the application, configured to use the Azure infrastructure provisioned by Crossplane.

5. Configure Argo CD
	- Create Argo CD Application resources pointing to the Git repo paths containing:
		- Crossplane infrastructure manifests
		- Kubernetes application manifests

6. Create a GitHub Actions workflow
	1. On PR merge to `main`, run Terraform to provision/update core Azure infrastructure (resource group, AKS cluster).	    
	2. Push Crossplane and app manifests to Git repos watched by Argo CD.
	3. Argo CD detects changes and reconciles cluster state (provisions Azure resources via Crossplane and deploys app).
	4. Run integration tests, notify teams on success/failure.
## References

- https://devopscube.com/argo-cd-ultimate-guide/
- https://argoproj.github.io/cd/
