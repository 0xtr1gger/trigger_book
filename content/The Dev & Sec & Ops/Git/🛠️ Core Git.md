---
created: 2026-09-20
updated: 2026-10-12
tags:
  - Git
---

- Main principles of Git, the distributed version-control system.
- How does Git manage and store file versions and change history?
- Internal structure of a Git repository (in detail), including the object model (which object types exist?), the index, and the commit history.
- GitHub vs. GitLab vs. Bitbucket for Git repository hosting.
	- Which additional features and tools do they provide?
- How to choose the most appropriate Git hosting service for a specific project or team?

## Git

>**Git** is a [distributed version-control system (DVCS)](https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control) developed by Linus Torvalds in 2005. It records the state of a file tree over time, supports parallel development, and lets you recover any recorded state.

- Every clone contains the complete repository: all objects, history, and branches.
- Most operations (`commit`, `log`, `diff`, `branch`, `merge`) run against the local object database. No network access is required.
- Git doesn't require a central server. In practice, teams designate one remote (GitHub, GitLab, a self-hosted server) as a synchronization point. That server is a peer that developers push to and fetch from.
---

- Key concepts:
	- **Snapshots** — each commit records the full state of the project tree, not a list of changes.
	- **Content addressing** — every object is stored under the SHA-1 hash of its content. Identical content is stored once.
	- **Integrity** — each commit hash depends on its content, its tree, and its parents. Any change to history changes all following hashes, so corruption or tampering is detectable.
	- **Append-only data** — normal operations add objects; they don't modify existing ones. Committed data is hard to lose.
	- **Branches** — a branch is a pointer to one commit. Creating, switching, and deleting branches is instant.
	- **Local operations** — only `clone`, `fetch`, `pull`, and `push` use network access.

---

- A repository is the [`.git`](https://git-scm.com/book/en/v2/Git-Internals-Plumbing-and-Porcelain) directory at the root of the project. It stores the object database, references, configuration, and the index.
- [`git init`](https://git-scm.com/docs/git-init) creates a new repository in the current directory. [`git clone`](https://git-scm.com/docs/git-clone) copies an existing repository, including its full history.

### Git records snapshots, not diffs

- Many VCSs (CVS, Subversion) store each file as a base version plus a sequence of per-file deltas. Git works differently.

---

- **Each Git commit records a snapshot of the entire project tree.**
- Unchanged files aren't stored again; the new snapshot references the existing stored content.
- [`git diff`](https://git-scm.com/docs/git-diff), [`git log -p`](https://git-scm.com/docs/git-log), and [`git show`](https://git-scm.com/docs/git-show) compute differences on demand by comparing two snapshots. Diffs aren't stored.
- Git doesn't record renames. A rename produces a snapshot where the old path is gone and the new path references the same blob. Diff commands reconstruct renames afterward by matching identical or similar blob content (`git diff -M`, `git log --follow`).
- To save disk space, Git later compresses objects into **packfiles**, where similar objects are stored as deltas against each other (see [[#Loose objects and packfiles]]). This is a storage optimization only: it doesn't change the data model, and every commit still resolves to a full snapshot.

## The three states and the index

- Files in a Git repository move between three areas:
	- Working tree
	- Staging area (index)
	- Repository
- Each file in the working tree is either **tracked** (present in the index or the last commit) or **untracked**. A tracked file is *unmodified*, *modified*, or *staged*.

### Working directory

>A **working directory** (or **working tree**) is the directory tree on the filesystem (excluding `.git/`) that contains the files of one commit extracted into normal, editable form, plus any changes the user hasn't recorded yet.

- The working tree is the only place where you edit files directly.
- Normally, the working tree reflects the commit that `HEAD` points to.
- The differences between `HEAD`, the index, and the working tree are what [`git status`](https://git-scm.com/docs/git-status) reports as *staged*, *modified*, and *untracked* files.

>[!note] A repository can have several working directories attached at once ([`git worktree`](https://git-scm.com/docs/git-worktree) `add`); each has its own index and its own `HEAD`.

### Staging area (index)

>A **staging area** (or **index**) is a single binary file, `.git/index`, that stores the list of file paths, file modes, and blob hashes that the next commit will record as the tree of the new commit.

- There is one index per working directory.
- The index is a full proposed snapshot, not a list of changes. After a commit, the index matches the new commit's tree.
- [`git add`](https://git-scm.com/docs/git-add) hashes the file content, writes it as a blob to the object database, and records the blob hash in the index. The content is in the repository from that moment, before any commit.
- For each entry, the index also caches file metadata (size, modification time, inode). Git compares this metadata to detect changed files without rehashing every file.
- During a merge conflict, the index holds up to three versions of a conflicted path: stage 1 (common ancestor), stage 2 (ours), stage 3 (theirs).
- The index makes partial commits possible: you can stage selected files or hunks (`git add -p`) and leave other changes uncommitted.
- [`git ls-files --stage`](https://git-scm.com/docs/git-ls-files) lists the index content.

### Repository

> A **repository** is the complete data store of a project's history: the `.git/` directory, containing (1) the object database — all blobs, trees, commits, and tag objects — and (2) all refs, plus `HEAD`, the index, and configuration.

- A Git repository is self-contained. All objects and all history are present; no network access is needed for local operations. A clone is a full repository, not a partial copy.
- A **bare repository** (`git init --bare`, `git clone --bare`) has the same object database and refs, but no working directory and no index. Servers use bare repositories because no one edits files on them directly.
- All clones are equal peers in the data model. Calling one remote "central" is a team convention, not a property of the data.

>[!note] A **shallow clone** (`git clone --depth <n>`) copies only the most recent commits; a **partial clone** (`git clone --filter=blob:none`) omits blob content until it's needed. Both reduce transfer size and relax the "every clone is complete" rule on purpose. CI jobs use them.

| Path                       | Content                                                                                         |
| -------------------------- | ----------------------------------------------------------------------------------------------- |
| `HEAD`                     | Current branch (`ref: refs/heads/main`) or a commit hash (detached `HEAD`).                     |
| `config`                   | Repository-level configuration: remotes, branch upstreams, local settings.                      |
| `objects/`                 | Object database: loose objects in `objects/<2 chars>/<38 chars>`, packfiles in `objects/pack/`. |
| `refs/heads/`              | Local branches.                                                                                 |
| `refs/tags/`               | Tags.                                                                                           |
| `refs/remotes/`            | Remote-tracking branches.                                                                       |
| `packed-refs`              | Refs packed into one file for performance.                                                      |
| `index`                    | Staging area.                                                                                   |
| `logs/`                    | Reflogs: history of each ref's values.                                                          |
| `hooks/`                   | Client-side hook scripts (samples by default).                                                  |
| `info/exclude`             | Local ignore patterns that aren't committed.                                                    |
| `ORIG_HEAD`                | Previous `HEAD` value, saved before `reset`, `merge`, and `rebase`.                             |
| `FETCH_HEAD`, `MERGE_HEAD` | Last fetched branch tips; commit being merged during a merge.                                   |

### Configuration

- Git reads configuration from several scopes. A narrower scope overrides a wider one:

| Scope    | File                   | Applies to                                           |
| -------- | ---------------------- | ---------------------------------------------------- |
| System   | `/etc/gitconfig`       | Every user on the machine.                           |
| Global   | `~/.gitconfig`         | The current user, all repositories.                  |
| Local    | `.git/config`          | One repository (the default write target).           |
| Worktree | `.git/config.worktree` | One working tree (needs `extensions.worktreeConfig`). |

- A single command can override all files with `-c <key>=<value>`.
- [`git config`](https://git-scm.com/docs/git-config) reads and writes these files. For identity, signing, and workflow defaults, see [[🛠️ Git conventions#Setting up Git]].

### Moving between the three areas

- The three areas form a pipeline. You edit files in the working tree; staging copies a snapshot of selected content into the index; committing ([`git commit`](https://git-scm.com/docs/git-commit)) records the index as a new commit and advances the current branch.
- Three comparisons describe the current state:
	- working tree vs. index — unstaged changes,
	- index vs. `HEAD` — staged changes,
	- working tree vs. `HEAD` — all uncommitted changes.
- `git status` summarizes all three; `git diff` shows them line by line.
- For the commands that move content between the areas, see [[🛠️ Commonplace book for Git commands#Moving changes between areas]].

### Ignoring files

- Git ignores untracked files that match patterns in:
	- `.gitignore` files in the working tree (committed and shared with the team; apply to their directory and subdirectories).
	- `.git/info/exclude` (local to the repository, not committed).
	- the file set in `core.excludesFile` (global, per user; for editor and OS files).
- Ignore patterns affect untracked files only. To ignore a file that is already tracked, untrack it first with [`git rm`](https://git-scm.com/docs/git-rm) `--cached <path>`.
- [`git check-ignore -v <path>`](https://git-scm.com/docs/git-check-ignore) shows which rule ignores a file.

## Commits, branches, and references

### Reference

>A **reference** (or **ref**) is a human-readable name that points to an object ID, usually a commit. Refs are stored under `.git/refs/` (or in `.git/packed-refs`) and named by their path, for example `refs/heads/main`.

| Ref namespace              | Meaning                                    |
| -------------------------- | ------------------------------------------ |
| `refs/heads/<name>`        | Local branch.                              |
| `refs/tags/<name>`         | Tag.                                       |
| `refs/remotes/<remote>/<name>` | Remote-tracking branch.                |
| `HEAD`                     | Symbolic ref to the current branch.        |

- A **symbolic ref** points to another ref instead of an object. `HEAD` is the main example.
- Refs make commits reachable. A commit that no ref (directly or through ancestry) and no reflog entry reaches is eventually deleted by garbage collection.
- [`git show-ref`](https://git-scm.com/docs/git-show-ref) lists all refs and the hashes they point to. [`git rev-parse <name>`](https://git-scm.com/docs/git-rev-parse) resolves any name to its object ID.
- [`git update-ref`](https://git-scm.com/docs/git-update-ref) creates, updates, or deletes a ref directly. Porcelain commands update refs through it.

### Commits

> A **commit** is a Git object that records a snapshot of the repository at a specific point in time. A commit stores a pointer to a tree (the snapshot), pointers to its parent commits, the author, the committer, timestamps, and a commit message.

- Each commit is identified by the hash of its content (SHA-1 by default, 40 hexadecimal characters). Because the content includes the tree hash and the parent hashes, the commit hash identifies the entire history leading to it.
- Most commands accept a unique prefix of a hash (for example, the first 7 characters).
- Commits are immutable. "Changing" a commit (`git commit --amend`, [`git rebase`](https://git-scm.com/docs/git-rebase)) creates a new commit with a new hash; the original stays in the object database until garbage collection.
- Commits form a **[directed acyclic graph (DAG)](https://en.wikipedia.org/wiki/Directed_acyclic_graph)**. Each commit references:
	- no parents — the root (initial) commit,
	- one parent — a normal commit,
	- two or more parents — a merge commit.
- **Author** is who wrote the change; **committer** is who last applied it (they differ after [`git cherry-pick`](https://git-scm.com/docs/git-cherry-pick), `git rebase`, or applying a patch).
- See [[#Commit]] for the object format.

### Branches

>A **branch** is a reference, `refs/heads/<name>`, to a single commit, which Git automatically advances to each new commit made while that branch is checked out. The branch's history is the set of commits reachable from that commit through parent links.

- With the default `files` ref storage, a branch is one small file containing one hash and nothing else. Creating a branch writes this file; no data is copied.
- A branch doesn't contain commits. It points to exactly one commit, the **tip**; the chain of parents produces the line of history.
- On every commit, Git rewrites the branch named by `HEAD` to the new commit's hash. Merging, rebasing, and resetting all reduce to writing different hashes into ref files.
- A branch is a mutable ref by design; a tag is an effectively immutable ref. In the data model, this is the only difference between them.
- Git doesn't allow a branch `a` and a branch `a/b` at the same time, because `a` would have to be both a file and a directory under `refs/heads/`.
- For branch commands, see [[🛠️ Git branches]].

### Remotes and remote-tracking branches

>A **remote** is a named URL of another repository, stored in `.git/config`. `git clone` creates a remote named `origin` that points to the cloned repository.

>A **remote-tracking branch** (`refs/remotes/<remote>/<branch>`, shown as `origin/main`) is a local, read-only copy of a branch's position on a remote at the time of the last fetch.

- Remote-tracking branches change only on [`git fetch`](https://git-scm.com/docs/git-fetch), [`git pull`](https://git-scm.com/docs/git-pull), or [`git push`](https://git-scm.com/docs/git-push). They aren't live views of the remote.
- A local branch may have an **upstream** (a remote-tracking branch it's linked to). The upstream is the default target of `git pull` and `git push`, and the reference for "ahead/behind" counts in `git status`.
- `git push` updates a remote branch only if the change is a **fast-forward** (the remote tip is an ancestor of the pushed commit). Otherwise the push is rejected and you must integrate the remote changes first, or force-push.
- A **refspec** maps refs between two repositories, in the form `<src>:<dst>`; a leading `+` allows a non-fast-forward update. The default fetch refspec of `origin`, `+refs/heads/*:refs/remotes/origin/*`, copies every remote branch to a remote-tracking branch under `refs/remotes/origin/`.
- For remote commands, see [[🛠️ Commonplace book for Git commands#Remotes and remote-tracking branches]].

### Tags

>A **tag** is a reference, `refs/tags/<name>`, that marks a specific object (usually a commit) and isn't moved by normal operations.

- Tags mark significant points in history, such as releases.
- Unlike branches, tags don't advance with new commits.
- There are two types of tags:
	- **Lightweight tag** — a ref that points directly to a commit. No additional metadata. Use it for private or temporary labels.
	- **Annotated tag** — a ref that points to a *tag object*, which stores the tagger, date, message, and optionally a GPG/SSH signature. Use it for releases.
- Tags commonly mark [semantic versions](https://semver.org/) (for example, `v1.0.0`, `v2.1.5`).
- [`git push`](https://git-scm.com/docs/git-push) doesn't push tags by default.
- [`git tag`](https://git-scm.com/docs/git-tag) creates lightweight and annotated tags. See [[🛠️ Commonplace book for Git commands#Tags]] for commands.

### `HEAD`

>**`HEAD`** is a symbolic reference, stored in `.git/HEAD`, that names the current branch (for example, `ref: refs/heads/main`) or, in a detached state, the current commit.

- `HEAD` determines:
	1) which commit the working directory and index are based on,
	2) the parent of the next commit,
	3) which branch is updated when the next commit is made.
- On `git commit`, Git creates the new commit with the commit that `HEAD` resolves to as its parent, then rewrites the branch named by `HEAD` to the new commit's hash.
- [`git switch`](https://git-scm.com/docs/git-switch) and [`git checkout`](https://git-scm.com/docs/git-checkout) change which branch `HEAD` names. [`git reset`](https://git-scm.com/docs/git-reset) moves the branch that `HEAD` names (and optionally updates the index and working tree); `HEAD` keeps naming the same branch.

---

- If you check out a commit, a tag, or a remote-tracking branch instead of a local branch, `HEAD` enters a **detached state** and contains a commit hash directly.
- New commits in a detached state belong to no branch. When `HEAD` moves elsewhere, they become unreachable and are recoverable only through the reflog until it expires. Create a branch to keep them (`git switch -c <new-branch>`).

### Reflog

>A **reflog** is a local log of every value a ref (including `HEAD`) has had, stored in `.git/logs/`.

- Each commit, checkout, reset, merge, rebase, and amend adds an entry.
- The reflog is local. It isn't pushed, fetched, or cloned.
- Use the reflog to recover commits lost after `git reset --hard`, a failed rebase, or work in a detached `HEAD`. [`git reflog`](https://git-scm.com/docs/git-reflog) shows the history of `HEAD`; the revision `HEAD@{<n>}` names its value `n` moves ago.

### Stash

>A **stash** is a set of uncommitted changes saved outside any branch. Git records it as commit objects (the working-tree state and the index state) referenced by `refs/stash`, which has its own reflog.

- Use a stash to switch context with a dirty working tree without committing half-finished work.
- Stash entries are local and aren't pushed. The stack is addressed as `stash@{0}`, `stash@{1}`, and so on.
- [`git stash`](https://git-scm.com/docs/git-stash) saves and restores stashes. See [[🛠️ Git conventions#Undoing changes]] for usage.

### Revision syntax

- Most commands that take a commit accept [revision expressions](https://git-scm.com/docs/gitrevisions):

| Expression          | Meaning                                                                    |
| ------------------- | -------------------------------------------------------------------------- |
| `<hash>`            | Commit with this hash or unique hash prefix.                               |
| `HEAD~<n>`          | `n`-th ancestor, following first parents (`HEAD~1` is the parent).         |
| `HEAD^<n>`          | `n`-th parent of a merge commit (`HEAD^2` is the merged branch's tip).     |
| `@{u}`              | Upstream of the current branch.                                            |
| `@{-1}`             | Previously checked-out branch.                                             |
| `HEAD@{<n>}`        | Value of `HEAD` `n` moves ago (from the reflog).                           |
| `<rev>:<path>`      | File at `<path>` in commit `<rev>`.                                        |
| `A..B`              | Commits reachable from `B` but not from `A` (for example, `main..feature`). |
| `A...B`             | Commits reachable from either `A` or `B`, but not both.                    |

## The Git object model

- Git is a **content-addressable filesystem**: a key-value store where values are *objects* and keys are hashes of the object content.

>A **Git object** is the fundamental unit of storage in a repository. Each object consists of a **type**, a **size**, and **content**, and is stored in the `.git/objects/` directory.

- To compute an object ID, Git hashes the string `<type> <size>\0<content>`. The result is the object's name.
- SHA-1 is the default hash. A SHA-1 collision was demonstrated in 2017, so repositories can use SHA-256 instead (`git init --object-format=sha256`). The two formats don't interoperate.
- A loose object is stored zlib-compressed at `.git/objects/<first 2 hex chars>/<remaining 38 chars>`.
- There are four object types:
	- **Blob** — stores the raw *content* of a file; doesn't include the filename or permissions.
	- **Tree** — represents a *directory*; lists blobs (files) and other trees (subdirectories) with their names and modes.
	- **Commit** — points to one tree (the *snapshot*) and stores metadata: parents, author, committer, timestamps, and message.
	- **Tag** — an annotated tag; points to an object (usually a commit) and stores the tag name, tagger, and message.

### Blob

- A blob contains file content only. Two files with identical content, in any path or commit, are stored as one blob.
- [`git hash-object`](https://git-scm.com/docs/git-hash-object) computes the blob ID of content without storing it. For example, the content `test content` hashes to `d670460b4b4aece5915caf5c68d12f560a9fe3e4`.

### Tree

- A tree entry has a mode, a type, a hash, and a name:

| Mode     | Entry type                           |
| -------- | ------------------------------------ |
| `100644` | Regular file.                        |
| `100755` | Executable file.                     |
| `120000` | Symbolic link.                       |
| `040000` | Subdirectory (tree).                 |
| `160000` | Submodule (commit in another repository). |

- Git tracks only the executable bit, not other file permissions or ownership.
- Git doesn't track empty directories: a tree without entries isn't recorded. To keep an empty directory, add a placeholder file (commonly `.gitkeep`).

### Commit

- A commit object has the following format:

```text
tree <tree-hash>
parent <parent-hash>
author <name> <<email>> <unix-timestamp> <timezone>
committer <name> <<email>> <unix-timestamp> <timezone>

<commit message>
```

- A root commit has no `parent` line; a merge commit has one `parent` line per parent. A signed commit has an additional `gpgsig` header.

### Tag

- A tag object has the following format:

```text
object <object-hash>
type commit
tag <tag-name>
tagger <name> <<email>> <unix-timestamp> <timezone>

<tag message>
```

### How a commit is stored

- Consider a project with two files, `README.md` and `src/main.c`. The first commit creates:
	- one blob per file,
	- one tree for `src/`,
	- one root tree containing `README.md` and `src/`,
	- one commit pointing to the root tree.
- After you change `src/main.c` and commit again, Git creates:
	- a new blob for `src/main.c`,
	- a new `src/` tree,
	- a new root tree,
	- a new commit with the previous commit as its parent.
- The `README.md` blob is unchanged, so the new root tree references the existing blob.

### Porcelain and plumbing commands

- Git commands are divided into **porcelain** (user-facing: `git add`, `git commit`, `git log`) and **plumbing** (low-level: `git cat-file`, `git hash-object`, `git update-ref`). Porcelain commands are built on plumbing commands; porcelain output targets humans, plumbing output is stable for scripts.
- Inspect objects directly with plumbing commands: [`git cat-file -t`](https://git-scm.com/docs/git-cat-file) shows an object's type, `git cat-file -p` prints its content, and [`git ls-tree -r HEAD`](https://git-scm.com/docs/git-ls-tree) lists a tree recursively.
- For these commands, see [[🛠️ Commonplace book for Git commands#Inspecting objects]].

### Loose objects and packfiles

- New objects are written as separate compressed files (**loose objects**).
- [`git gc`](https://git-scm.com/docs/git-gc) (also run automatically when many loose objects accumulate) and network transfers combine objects into a **packfile** (`.git/objects/pack/pack-<hash>.pack`) with an index file (`.idx`) for lookup.
- Inside a packfile, Git stores similar objects (for example, two versions of one file) as one full object plus deltas. The most recent version is usually stored in full, because it's accessed most often.
- Delta compression in packfiles is independent of commits. It isn't the same as storing history as diffs.
- [`git verify-pack -v`](https://git-scm.com/docs/git-verify-pack) lists a packfile's content; [`git count-objects -vH`](https://git-scm.com/docs/git-count-objects) reports object counts and repository size.

### Garbage collection

- `git gc` packs objects, packs refs, and deletes unreachable objects.
- An object is deleted only if it's unreachable from every ref and every reflog entry, and older than `gc.pruneExpire` (default: 2 weeks).
- Reflog entries expire after 90 days (`gc.reflogExpire`), or after 30 days for entries no longer reachable from the ref (`gc.reflogExpireUnreachable`). Until then, commits removed from branches are recoverable.
- An **unreachable** object is one that no ref or reflog entry reaches. A **dangling** object is unreachable and referenced by no other object. [`git fsck --lost-found`](https://git-scm.com/docs/git-fsck) lists dangling objects; use it to recover commits lost after a hard reset or a deleted branch.

## Merging and rebasing

- The **merge base** of two branches is their best common ancestor. [`git merge-base`](https://git-scm.com/docs/git-merge-base) prints it.

### Merge

- [`git merge <branch>`](https://git-scm.com/docs/git-merge) integrates the history of `<branch>` into the current branch.
- **Fast-forward merge** — if the current branch tip is an ancestor of `<branch>`, Git moves the current branch to the tip of `<branch>`. No new commit is created.
- **Three-way merge** — if the branches have diverged, Git compares both tips with their merge base and creates a **merge commit** with two parents. The default strategy is `ort`.
- `git merge --no-ff` creates a merge commit even when a fast-forward is possible; `git merge --ff-only` refuses to merge unless a fast-forward is possible.

### Conflicts

- A conflict occurs when both branches changed the same lines of a file (or one changed and the other deleted it) since the merge base.
- Git stops, writes conflict markers into the file, and stores the three versions in the index:

```text
<<<<<<< HEAD
current branch version
=======
merged branch version
>>>>>>> feature
```

- To resolve a conflict, edit the file to remove the markers, stage the result with `git add`, and complete the operation with `git merge --continue` (or `git rebase --continue`, `git cherry-pick --continue`). `git merge --abort` (or `git rebase --abort`) cancels the operation and returns to the previous state.
- Git can record a resolution and replay it on the same conflict later with the `rerere` feature (`rerere.enabled`).

### Rebase

- `git rebase <base>` takes the commits of the current branch that aren't in `<base>` and replays them one by one on top of `<base>`.
- Each replayed commit is a new commit with a new hash. The original commits stay reachable through the reflog and `ORIG_HEAD`.
- Rebase produces a linear history without merge commits.
- Rebasing a branch that others have already fetched rewrites shared history: their copies still contain the old commits. See [[🛠️ Git conventions]] for rules.
- Interactive rebase (`git rebase -i`) reorders, squashes, rewords, drops, or splits commits. To copy individual commits to another branch, see [[🛠️ Git cherry-pick]].

## Git hosting services

- Git defines repositories, commits, and the transfer protocols (SSH, HTTPS). Pull requests, reviews, issues, CI/CD, and access control aren't part of Git; hosting services add them.
- Common functions of hosting services:
	- **Pull requests / merge requests** — proposing, reviewing, and merging a branch.
	- **Code review** — inline comments, required approvals, code owners.
	- **Branch protection** — blocking direct pushes, force pushes, and merges without approvals or passing checks.
	- **CI/CD** — running pipelines on push and on pull requests.
	- **Issue tracking and planning** — issues, boards, milestones.
	- **Registries** — container images and packages.
	- **Security scanning** — secrets, dependencies, static analysis.
	- **Access control** — organizations, teams, roles, SSO, audit logs.
	- **Documentation** — wikis, static site hosting.

| Aspect                  | GitHub                                                  | GitLab                                                                | Bitbucket                                          |
| ----------------------- | ------------------------------------------------------- | --------------------------------------------------------------------- | -------------------------------------------------- |
| Owner                   | Microsoft                                               | GitLab Inc.                                                           | Atlassian                                          |
| Change proposal         | Pull request                                            | Merge request                                                         | Pull request                                       |
| CI/CD                   | GitHub Actions                                          | GitLab CI/CD (`.gitlab-ci.yml`), built in                             | Bitbucket Pipelines                                |
| Self-hosting            | GitHub Enterprise Server (paid)                         | Self-managed; Community Edition is open source                        | Bitbucket Data Center (paid)                       |
| Registries              | GitHub Packages, Container registry (`ghcr.io`)         | Container, package, and Terraform module registries                   | Mostly through integrations (for example, JFrog Artifactory) |
| Security features       | Dependabot, secret scanning, code scanning (CodeQL)     | SAST, DAST, dependency and container scanning (mostly paid tiers)      | Mostly through integrations (for example, Snyk)    |
| Planning                | Issues, Projects, Discussions                           | Issues, boards, epics, milestones                                     | Jira integration                                   |
| Main strength           | Largest open-source community and integration marketplace | All DevOps stages in one application; full self-hosting              | Integration with Jira and Confluence               |

- Other options: Azure DevOps Repos (Microsoft, for teams on Azure), Gitea and Forgejo (lightweight, open-source, self-hosted).

### Choosing a hosting service

- **Hosting model** — SaaS or self-hosted. Regulatory, data residency, or air-gap requirements usually require self-hosting (GitLab self-managed, GitHub Enterprise Server, Bitbucket Data Center, Gitea).
- **Existing toolchain** — Jira and Confluence favor Bitbucket; Azure favors Azure DevOps; a team with existing CI/CD may need only repository hosting.
- **CI/CD requirements** — built-in pipeline features, runner options (hosted or self-hosted), and included build minutes.
- **Security and compliance** — SSO/SAML, audit logs, branch protection, required reviews, signed commits, scanning features, and the tier each one requires.
- **Cost** — price per user per tier. Many features (advanced security, compliance, some approval rules) are available only in higher tiers.
- **Visibility** — public open-source projects benefit from GitHub's community.
- **Migration** — all three import repositories from the others. Git history moves without loss; issues, pull requests, and pipelines need conversion.

## References and further reading

- [[🛠️ Commonplace book for Git commands]]
- [Pro Git book](https://git-scm.com/book/en/v2)
- https://git-scm.com/book/en/v2/Git-Internals-Git-Objects
- https://git-scm.com/book/en/v2/Git-Internals-Git-References
- https://git-scm.com/book/en/v2/Git-Internals-Packfiles
- https://git-scm.com/book/en/v2/Git-Basics-Tagging
- https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell
- https://git-scm.com/book/en/v2/Git-Branching-Rebasing
- https://git-scm.com/docs/gitrevisions
- https://git-scm.com/docs/gitignore
