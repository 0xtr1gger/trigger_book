---
created: 2026-10-11
updated: 2026-10-12
---
- What are common recommendations, principles, and agreements for writing Git commit messages?
- What are common Git branch naming conventions?
- How to divide changes into individual commits and describe them in commit messages?

>[!note] Teams define their own conventions. When a repository has a `CONTRIBUTING.md`, a commit message linter, or a branch naming rule, follow it over any defaults.

## Setting up Git

- Set your identity. It's recorded in every commit; use the email address registered with your hosting service account:

```bash
git config --global user.name "First Last"
git config --global user.email "name@company.com"
```

- Set the default branch name for new repositories:

```bash
git config --global init.defaultBranch main
```

- Make `git pull` rebase local commits on top of the upstream instead of creating merge commits:

```bash
git config --global pull.rebase true
```

- Make `git push` set the upstream automatically on the first push of a new branch:

```bash
git config --global push.autoSetupRemote true
```

- Delete remote-tracking branches whose remote branches no longer exist on each fetch:

```bash
git config --global fetch.prune true
```

- Set the editor for commit messages:

```bash
git config --global core.editor "vim"
```

- Show the effective configuration and where each value comes from:

```bash
git config --list --show-origin
```

---

- Authenticate to the hosting service with an SSH key or a personal access token. Passwords aren't accepted for Git operations on GitHub, GitLab, or Bitbucket Cloud.
- Generate an SSH key, then add the public key (`~/.ssh/id_ed25519.pub`) to your account:

```bash
ssh-keygen -t ed25519 -C "name@company.com"
```

- Sign commits with the same SSH key (Git 2.34+), if the team requires verified commits:

```bash
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global commit.gpgsign true
```

## Daily workflow

- The common workflow on a team: one short-lived branch per task, merged into `main` through a pull request (PR) or merge request (MR).

- Update `main`:

```bash
git switch main
git pull
```

- Create a branch for the task:

```bash
git switch -c feature/PROJ-123-add-login-form
```

- Make changes, review them, and stage them by hunk:

```bash
git status
git diff
git add -p
```

- Commit:

```bash
git commit
```

- Push the branch:

```bash
git push -u origin HEAD
```

- Open a PR in the hosting service. Address review comments with new commits or by updating existing ones (see [[#Rewriting history]]).
- Keep the branch up to date with `main`:

```bash
git fetch origin
git rebase origin/main
git push --force-with-lease
```

- After the PR is merged, delete the local branch and update `main`:

```bash
git switch main
git pull
git branch -d feature/PROJ-123-add-login-form
```

>[!note] After a squash or rebase merge, `git branch -d` refuses to delete the branch because its original commits aren't in `main`. Use `git branch -D` once you've confirmed the PR is merged.

- Commit and push often. Unpushed work exists only on your machine.
- Run `git status` and `git diff --staged` before each commit to check what you're committing.

## Branch naming

- Common format:

```text
<type>/<ticket-id>-<short-description>
```

- Examples:
	- `feature/PROJ-123-add-login-form`
	- `fix/PROJ-456-null-pointer-on-logout`
	- `hotfix/1.4.1-payment-timeout`
	- `release/1.5.0`
	- `chore/update-dependencies`
	- `docs/api-authentication`

| Prefix       | Use for                                                     |
| ------------ | ----------------------------------------------------------- |
| `feature/`   | New functionality.                                          |
| `fix/`, `bugfix/` | Bug fixes in regular development.                      |
| `hotfix/`    | Urgent fixes to production, branched from a release or `main`. |
| `release/`   | Release preparation (in Git Flow).                          |
| `chore/`     | Maintenance: dependencies, build, tooling.                  |
| `docs/`      | Documentation only.                                         |
| `refactor/`  | Code restructuring without behavior change.                 |
| `test/`      | Tests only.                                                 |

- Rules:
	- Use lowercase letters, digits, and hyphens. macOS and Windows filesystems are case-insensitive by default, so `Feature/x` and `feature/x` can conflict there.
	- Include the ticket ID if the team uses a tracker. Jira, GitHub, and GitLab link branches to tickets by ID.
	- Keep names short and descriptive. Don't use names like `fix`, `test`, `my-branch`, or your name alone.
	- Don't use a name that is also a prefix of other branches: `feature` and `feature/x` can't exist at the same time.
- Git rejects branch names that contain spaces, `..`, `~`, `^`, `:`, `?`, `*`, `[`, `\`, or `@{`, begin with `-`, or end with `/`, `.`, or `.lock`. Check a name:

```bash
git check-ref-format --branch <name>
```

## Branching strategies

| Strategy                    | Model                                                                                                                       | Fits                                              |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| Trunk-based development     | Everyone integrates into `main` at least daily, through very short-lived branches. Unfinished features are hidden behind feature flags. | Continuous delivery, mature CI.                   |
| GitHub flow                 | `main` is always deployable. Each change is a branch and a PR; merged changes are deployed.                                 | Web services with one production version.         |
| Git Flow                    | Long-lived `main` and `develop`; `feature/`, `release/`, and `hotfix/` branches with defined merge paths.                   | Products with scheduled releases and several supported versions. |

- Most teams today use GitHub flow or trunk-based development. Git Flow adds overhead and long-lived branches, which increase merge conflicts.

## Commits

### Dividing changes into commits

- **One commit = one logical change.** A commit should be describable in one sentence without "and".
- Each commit should leave the project in a working state: it builds and passes tests. This makes `git bisect` and `git revert` usable.
- Separate these into different commits:
	- formatting or renaming from behavior changes,
	- refactoring from new features or fixes,
	- dependency updates and generated files from hand-written code,
	- unrelated fixes found while working on a task.
- Commit when one logical step is complete. Don't commit half-finished work to shared branches; don't collect a day of unrelated changes into one commit.
- Stage parts of a file by hunk:

```bash
git add -p
```

- Unstage a file without losing changes:

```bash
git restore --staged <path>
```

- Clean up local history before opening a PR: squash "fix typo" and "WIP" commits into the commits they belong to (see [[#Rewriting history]]).

### Commit message format

- Standard structure:

```text
<subject line: summary of the change>

<body: what changed and why, wrapped at 72 characters>

<trailers: issue references, co-authors>
```

- Subject line:
	- 50 characters or fewer (72 at most).
	- Imperative mood: "Add retry to upload", not "Added retry" or "Adds retry". The subject should complete the sentence "If applied, this commit will …".
	- Capitalized first word (unless the team uses Conventional Commits), no period at the end.
	- Specific: "Fix crash when config file is empty", not "Fix bug" or "Update code".
- Blank line between the subject and the body. Git and hosting services use the first line as the title.
- Body (optional for trivial changes):
	- Explain *what* changed and *why*; the diff already shows *how*.
	- Describe the problem, the reason for the chosen solution, and side effects or limitations.
	- Wrap lines at 72 characters.
- Example:

```text
Fix token refresh race on concurrent requests

When two requests received 401 at the same time, both started a token
refresh, and the second refresh invalidated the first token. Requests
that used the first token then failed.

Serialize refreshes with a mutex and reuse the result of a refresh
that is already in progress.

Fixes #482
```

- Common trailers (last paragraph, `Key: value` format):

| Trailer                                  | Meaning                                                                                       |
| ---------------------------------------- | --------------------------------------------------------------------------------------------- |
| `Fixes #123`, `Closes #123`              | Close the issue when the commit reaches the default branch (GitHub, GitLab).                  |
| `Refs #123`, `PROJ-123`                  | Link the issue without closing it.                                                            |
| `Co-authored-by: Name <email>`           | Credit another author (GitHub, GitLab).                                                       |
| `Signed-off-by: Name <email>`            | Certify the right to submit the change ([DCO](https://developercertificate.org/)); add with `git commit -s`. |

- `git commit -m "..."` is acceptable for one-line messages. For a body, run `git commit` to open the editor.

### Conventional Commits

- [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) is a widely used message format. Tools use it to generate changelogs and determine version numbers.

```text
<type>[(scope)][!]: <description>

[body]

[footer(s)]
```

- Examples:

```text
feat(auth): add password reset via email
fix: handle empty config file
docs(readme): describe local setup
refactor(api)!: rename /users endpoint to /accounts
```

| Type       | Use for                                                       |
| ---------- | ------------------------------------------------------------- |
| `feat`     | New feature (minor version bump).                             |
| `fix`      | Bug fix (patch version bump).                                 |
| `docs`     | Documentation only.                                           |
| `style`    | Formatting with no effect on behavior.                        |
| `refactor` | Code change that neither fixes a bug nor adds a feature.      |
| `perf`     | Performance improvement.                                      |
| `test`     | Tests only.                                                   |
| `build`    | Build system or dependencies.                                 |
| `ci`       | CI configuration.                                             |
| `chore`    | Other maintenance that doesn't change source or tests.        |
| `revert`   | Revert of a previous commit.                                  |

- `!` after the type or scope, or a `BREAKING CHANGE: <description>` footer, marks a breaking change (major version bump).
- The description usually starts with a lowercase letter and has no period.
- Teams enforce the format with tools such as `commitlint` in a hook or CI.

## Pull requests and code review

- Keep PRs small and focused on one task. Small PRs are reviewed faster and more thoroughly. To split a large PR, see [[🛠️ How to... Git#How to split PRs]].
- PR title: same rules as a commit subject. Many teams use the PR title as the squash commit message.
- PR description:
	- what changed and why,
	- link to the ticket,
	- how to test the change,
	- screenshots for UI changes,
	- known limitations or follow-up work.
- Before requesting review:
	- review your own diff in the hosting service,
	- make sure CI passes,
	- rebase on the current `main` if the branch is behind or has conflicts.
- Open a **draft PR** for early feedback on unfinished work.
- As a reviewer, comment on the code, not the author; distinguish required changes from suggestions.
- As an author, reply to each comment or resolve it with a change; don't resolve other people's comments without a reply.

### Merge methods

| Method                  | Result on `main`                                                     | Trade-off                                                           |
| ----------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------- |
| Merge commit            | All branch commits plus a merge commit.                              | Full history; non-linear graph.                                     |
| Squash and merge        | One new commit containing all branch changes.                        | Clean linear history; individual commits of the branch are lost.    |
| Rebase and merge        | Branch commits replayed onto `main`, no merge commit.                | Linear history with individual commits; each commit must be clean.  |

- The repository settings usually define the allowed method. Follow them.

## Rewriting history

- **Never rewrite history that others have based work on**: `main`, `develop`, release branches, or anyone else's branch. Rewriting changes commit hashes; other people's clones still contain the old commits.
- Rewriting your own feature branch (amend, rebase, squash) before or during review is normal.
- After rewriting a pushed branch, push with `--force-with-lease`, not `--force`. It refuses to overwrite the remote branch if it contains commits you haven't fetched:

```bash
git push --force-with-lease
```

- Change the last commit (message or content of staged files):

```bash
git commit --amend
```

- Create a commit that will be squashed into an earlier commit:

```bash
git commit --fixup <commit>
```

- Squash fixup commits into their targets:

```bash
git rebase -i --autosquash origin/main
```

- Edit, reorder, squash, or drop commits on the current branch:

```bash
git rebase -i origin/main
```

## Undoing changes

| Situation                                              | Command                                       |
| ------------------------------------------------------ | --------------------------------------------- |
| Discard unstaged changes to a file                     | `git restore <path>`                          |
| Unstage a file                                         | `git restore --staged <path>`                 |
| Fix the last commit (not pushed)                       | `git commit --amend`                          |
| Undo the last commit, keep changes staged (not pushed) | `git reset --soft HEAD~1`                     |
| Undo the last commit, keep changes unstaged (not pushed) | `git reset HEAD~1`                          |
| Undo the last commit and discard its changes (not pushed) | `git reset --hard HEAD~1`                  |
| Undo a pushed commit                                   | `git revert <commit>`                         |
| Recover a lost commit or branch                        | `git reflog`, then `git switch -c <branch> <hash>` |
| Save unfinished changes temporarily                    | `git stash`, then `git stash pop`             |
| Abort a merge or rebase in progress                    | `git merge --abort`, `git rebase --abort`     |

- `git revert` creates a new commit that applies the inverse of an existing commit. It doesn't rewrite history, so it's safe on shared branches.
- `git reset --hard` and `git restore` discard uncommitted changes permanently. The reflog doesn't contain them.

## What not to commit

- **Secrets**: passwords, API keys, tokens, private keys, `.env` files, cloud credentials, `*.tfstate`. Use a secrets manager or CI variables.
- **Generated files**: build output, compiled binaries, logs, coverage reports.
- **Dependencies**: `node_modules/`, `vendor/`, virtual environments. Commit lock files (`package-lock.json`, `poetry.lock`, `go.sum`) instead.
- **Personal files**: editor and OS files (`.idea/`, `.vscode/`, `.DS_Store`). Add them to your global ignore file (`core.excludesFile`), not to the project's `.gitignore`.
- **Large binary files**: store them with [Git LFS](https://git-lfs.com/). GitHub rejects files larger than 100 MB.
- Add a `.gitignore` when you create a repository. Templates: [github/gitignore](https://github.com/github/gitignore).

>[!warning] If you push a secret, consider it compromised: revoke and rotate it first. Deleting the file in a new commit doesn't remove it from history. Removing it from history (`git filter-repo`) requires a force push and doesn't affect existing clones, forks, or caches.

- Detect secrets before they're committed with a pre-commit hook, for example [`gitleaks`](https://github.com/gitleaks/gitleaks) through the [`pre-commit`](https://pre-commit.com/) framework.

## Line endings

- Windows uses CRLF line endings; Linux and macOS use LF. Mixed line endings produce diffs where every line changed.
- Define line endings per repository in a committed `.gitattributes` file:

```text
* text=auto eol=lf
*.bat text eol=crlf
*.png binary
```

## Tags and releases

- Tag releases with annotated tags and [Semantic Versioning](https://semver.org/): `vMAJOR.MINOR.PATCH`.
	- `MAJOR` — incompatible changes.
	- `MINOR` — new backward-compatible functionality.
	- `PATCH` — backward-compatible bug fixes.
- Don't move or delete a tag that has been pushed; create a new version instead.
- For tag commands, see [[🛠️ Commonplace book for Git commands#Tags]].

## References and further reading

- [Pro Git: Contributing to a project](https://git-scm.com/book/en/v2/Distributed-Git-Contributing-to-a-Project)
- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
- [How to write a Git commit message](https://cbea.ms/git-commit/)
- [Git: SubmittingPatches](https://git-scm.com/docs/SubmittingPatches)
- [Semantic Versioning 2.0.0](https://semver.org/)
- [Trunk-based development](https://trunkbaseddevelopment.com/)
- [GitHub flow](https://docs.github.com/en/get-started/using-github/github-flow)
- [`git check-ref-format`](https://git-scm.com/docs/git-check-ref-format)
