---
created: 2026-10-01
updated: 2026-10-01
---
## What it is

- Atlantis runs `terraform plan` and `apply` directly from PRs that affect Terraform code. 
- It doesn't replace Terraform, just orchestrates it.
- Basic flow:
	1. A change to Terraform code is submitted in a pull request. 
	2. Atlantis detects the change and automatically runs `terraform plan`. 
	3. Atlantis posts the plan result to the pull request as a comment.
	4. Once the required conditions are satisfied, you can request `atlantis apply`.
	5. Atlantis runs `terraform apply` using the previously generated plan.
	6. Atlantis reports the result back to the pull request.
	7. The PR can then be merged. 

## PR flow

1. Make changes to Terraform 
2. Push branch
3. Open PR
4. Automatic `atlantis plan` is run
5. Review the plan
6. Send the PR for approval
7. `Update branch` 
8. Check the plan again
9. Send `atlantis apply`
10. If successful -> merge

## Quick command reference

- Useful commands:

| Command         | Description |
| --------------- | ----------- |
| `atlantis plan` |             |


- `atlantis plan` syntax:

```bash
atlantis plan [options] -- [terraform plan flags]
```

- Important `atlantis plan`/`apply` options:

| Option           | Description                                                                                       |
| ---------------- | ------------------------------------------------------------------------------------------------- |
| `-p <project>`   | The project to run plan for (defined in the repo-level `atlantis.yaml`). Can't be used with `-d`. |
| `-d <directory>` | Which directory to run plan in relative to root of the repo. Can't be used with `-p`.             |


## `atlantis`
## Links

- [`Using Atlantis — Atlantis documentation`](https://www.runatlantis.io/docs/using-atlantis.html)
- [`Repo Level atlantis.yaml Config — Atlantis documentation`](https://www.runatlantis.io/docs/repo-level-atlantis-yaml.html)
- 