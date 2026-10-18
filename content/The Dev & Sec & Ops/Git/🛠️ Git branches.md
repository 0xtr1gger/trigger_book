---
created: 2026-09-30
updated: 2026-10-16
---

## Git branches

- Every time you work with Git, you work on a branch. 

>[!note] Except detached `HEAD` (see [[#Detached HEAD]]).

- [`git init`](https://git-scm.com/docs/git-init) creates a repository with one initial branch. Git's built-in default name for it is `master`; the `init.defaultBranch` setting changes it (see [[🛠️ Git conventions#Setting up Git]]).
- The initial branch is **unborn** until the first commit: `HEAD` names `refs/heads/master`, but the ref doesn't exist yet, so [`git branch`](https://git-scm.com/docs/git-branch) lists nothing.
- GitHub, GitLab, and Bitbucket name the default branch of new repositories `main`. The **default branch** of a remote is the branch that `git clone` checks out and the default target of pull requests.

---

- Branches allow for **parallel development**: several lines of work progress at the same time from a common starting point without affecting each other.
	- Commits on one branch don't change any other branch. `main` stays unchanged while `feature` accumulates commits.
	- Each task (a feature, a bug fix, an experiment, release preparation) gets its own branch. Unfinished or failed work stays out of `main`. To discard an experiment, delete its branch.
	- Switching branches replaces the working tree with another line of work. For example, pause a feature, fix a production bug on a `hotfix` branch, and return to the feature.
	- Developers work on separate branches in their own clones and exchange them through a remote.
- The isolation ends at **integration**: a merge or a rebase combines two lines of development (see [[#Merging branches]], [[#Rebasing branches]]). Git detects conflicts only at integration, not while the branches diverge.
- The longer two branches diverge, the more their changes overlap and the harder integration becomes. Teams keep branches short-lived and integrate often (see [[🛠️ Git conventions#Branching strategies]]).
- Branches are cheap. Creating a branch writes one ref; no files or commits are copied. One branch per task is the normal workflow.

---

>Formally, a **branch** is a movable pointer (a ref, `refs/heads/<name>`) to one commit, the branch's **tip**. Git advances the pointer to each new commit made on the branch.

>Functionally, a **branch** is a separate line of development: the tip and every commit reachable from it through parent links.

- A branch doesn't contain commits. The chain of parents starting at the tip produces the line of history.
- A commit can belong to several branches. Commits made before a branch was created are reachable from both the new branch and the original one.
- A commit doesn't record the branch it was made on. After the branch is deleted, its commits stay in the graph; they're only harder to find.
- For the data model of branches and refs, see [[🛠️ Core Git#Branches]].

>[!note]+ Graph notation in this note
>- Commits are shown left to right, from older to newer: `A---B---C`. Each commit's parent is to its left.
>- Branch names are shown in parentheses after the commit they point to, as [`git log --oneline --graph --decorate`](https://git-scm.com/docs/git-log) prints them.
>- `HEAD -> main` means `HEAD` names `main`. `HEAD` alone means a detached `HEAD`.
>- `D'` is a copy of commit `D` with a new parent and a new hash (created by a rebase).

## `HEAD`

>**`HEAD`** is a symbolic reference, stored in `.git/HEAD`, that names the current branch (for example, `ref: refs/heads/main`) or, in a detached state, the current commit.

- For the role of `HEAD` in commits and resets, see [[🛠️ Core Git#HEAD]].
- There is one `HEAD` per working tree. Git never copies or duplicates it.

### `HEAD` when you create and switch branches

- The repository has three commits on `main`. `HEAD` names `main`:

```text
A---B---C  (HEAD -> main)
```

- `git branch feature` writes a new ref, `refs/heads/feature`, that contains the hash of `C`. `HEAD` doesn't change; it still names `main`. Two refs point to the same commit:

```text
A---B---C  (HEAD -> main, feature)
```

- `git switch feature` rewrites `.git/HEAD` from `ref: refs/heads/main` to `ref: refs/heads/feature`, then updates the index and the working tree to the commit `feature` points to. Both branches point to `C`, so no files change:

```text
A---B---C  (main, HEAD -> feature)
```

- A commit on `feature` creates `D` with parent `C`, and Git moves `feature` (the branch that `HEAD` names) to `D`. `main` doesn't move. `.git/HEAD` doesn't change either: it still contains `ref: refs/heads/feature` and now resolves to `D`:

```text
A---B---C  (main)
         \
          D  (HEAD -> feature)
```

- After `git switch main` and a commit on `main`, the new commit `E` also has parent `C`. The branches have **diverged**; `C` is their merge base:

```text
          D  (feature)
         /
A---B---C---E  (HEAD -> main)
```

---

- `HEAD` changes only when you switch: it starts naming another branch.
- The branch that `HEAD` names moves when you commit, merge, rebase, or reset.
- Other branches move only when you update them explicitly or fetch (remote-tracking branches).

---

- Show the content of `HEAD`:

```bash
cat .git/HEAD
```

>[!example]-
>```text
>ref: refs/heads/feature
>```

- Show the name of the current branch:

```bash
git branch --show-current
```

- Show the commit that `HEAD` resolves to:

```bash
git rev-parse HEAD
```

### Detached `HEAD`

>A **detached `HEAD`** is the state in which `.git/HEAD` contains a commit hash instead of a branch name.

- Git detaches `HEAD` when you check out something other than a local branch: a commit, a tag, or a remote-tracking branch. Rebases, [`git bisect`](https://git-scm.com/docs/git-bisect), and submodules also run in a detached state.
- Switch to a commit in a detached state (for example, to inspect or build an old version):

```bash
git switch --detach <commit>
```

```bash
git checkout <commit>
```

- `git switch` refuses to switch to a tag or a remote-tracking branch without `--detach`. `git checkout` detaches without asking and prints a warning.

```text
A---B---C  (main)
    ^
    HEAD
```

- New commits in a detached state move only `HEAD`; no branch points to them:

```text
A---B---C  (main)
     \
      X---Y  (HEAD)
```

- After you switch away, `X` and `Y` are unreachable from any branch. Git prints their hash when you leave, and they stay in the reflog until it expires.
- Keep the commits by creating a branch while `HEAD` still points to them:

```bash
git switch -c <new_branch_name>
```

- If you already switched away, find the hash in the reflog and create a branch at it:

```bash
git reflog
git branch <new_branch_name> <hash>
```

- Leave the detached state by switching to a branch:

```bash
git switch main
```

## Working with branches

### Creating branches 

- To create a new branch, use [`git branch`](https://git-scm.com/docs/git-branch), [`git switch -c`](https://git-scm.com/docs/git-switch) (recommended), or [`git checkout -b`](https://git-scm.com/docs/git-checkout):

```bash
git branch <new_branch_name>
```

```bash
git switch -c <new_branch_name>
```

```bash
git checkout -b <new_branch_name>
```

>[!note]+ `git branch` vs. `git switch -c` and `git checkout -b`
> - `git branch` creates a new branch pointer but **doesn't switch to it**. 
> - `git switch -c` and `git checkout -b` create a new branch and switch to it.

- A new branch starts at `HEAD` by default. To start it at another commit, pass a **start point**: a branch, a remote-tracking branch, a tag, or a commit hash:

```bash
git switch -c <new_branch_name> <start_point>
```

```bash
git branch <new_branch_name> <start_point>
```

- For example, branch a hotfix from the current state of the remote `main`, without switching to the local `main` first:

```bash
git fetch origin
git switch -c hotfix/payment-timeout origin/main
```

- If the start point is a remote-tracking branch, Git sets it as the upstream of the new branch (`branch.autoSetupMerge`). Use `--track` or `--no-track` to override this.
- `git switch -c` and `git branch` refuse to overwrite an existing branch. `git switch -C` and `git branch -f` reset the existing branch to the start point.
- For naming rules and the characters Git rejects, see [[🛠️ Git conventions#Branch naming]].
- A new branch exists only in your repository. To publish it on the remote and set its upstream, use [`git push -u`](https://git-scm.com/docs/git-push) (see [[#Pushing branches]]):

```bash
git push -u origin <local_branch_name>
```

### Switching branches

- To switch to an existing branch, use `git switch` or `git checkout`:

```bash
git switch <branch_name>
```

```bash
git checkout <branch_name>
```

- Switch to the previously checked-out branch (`@{-1}`):

```bash
git switch -
```

- Switching updates `HEAD`, the index, and the working tree to the target branch's tip. Files that are the same in both commits aren't touched.

>[!note]+ `git switch` vs. `git checkout`
>- `git checkout` has two jobs: it switches branches and it restores files in the working tree (`git checkout -- <path>`). `git checkout <name>` is ambiguous when `<name>` is both a branch and a path.
>- Git 2.23 split these jobs into [`git switch`](https://git-scm.com/docs/git-switch) (branches) and [`git restore`](https://git-scm.com/docs/git-restore) (files). Use `git switch` and `git restore`; `git checkout` still works and appears in older documentation and scripts.
>- For the equivalent commands, see [[#git checkout]].

#### Switching with uncommitted changes

- Uncommitted changes don't belong to any branch. They stay in the working tree and the index, and Git carries them to the target branch.
- Git switches only if the carried changes don't conflict with the target branch. If a file you've modified is different between the current branch and the target branch, Git refuses to switch:

```text
error: Your local changes to the following files would be overwritten by checkout:
	src/app.py
Please commit your changes or stash them before you switch branches.
```

- Git also refuses if an untracked file would be overwritten by a tracked file of the target branch.
- To switch anyway, commit the changes first, or stash them, switch, and restore them later (see [[🛠️ Core Git#Stash]]):

```bash
git stash
git switch <branch_name>
git stash pop
```

- Carry the changes over with a three-way merge. Conflicts are left in the working tree for you to resolve:

```bash
git switch -m <branch_name>
```

- Discard the changes and switch:

```bash
git switch --discard-changes <branch_name>
```

### Listing branches

- List local branches:

```bash
git branch
```

>[!example]+ Output
> ```text
>   feature
> * main
> + hotfix
> ```
> 
>- The asterisk character, `*`, marks the *current branch*.
>- The plus character, `+`, marks a branch checked out in another worktree (see [[#Working on several branches at once]]).

- List local and remote-tracking branches:

```bash
git branch -a
```

>[!example]-
>```text
>* main
>  feature
>  remotes/origin/HEAD -> origin/main
>  remotes/origin/feature
>  remotes/origin/main
>```

- List only remote-tracking branches:

```bash
git branch -r
```

- List local branches with their tip commit, upstream, and ahead/behind counts:

```bash
git branch -vv
```

>[!example]-
>```text
>* feature 3f2c1ab [origin/feature: ahead 2] Add login form
>  main    9e8d7c6 [origin/main] Merge pull request #42
>  old-fix 1a2b3c4 [origin/old-fix: gone] Fix typo in footer
>```
>- `ahead 2` — two local commits aren't on the upstream yet.
>- `gone` — the upstream branch was deleted on the remote and pruned locally.

- List branches already merged into the current branch (safe to delete), or into another branch:

```bash
git branch --merged
git branch --merged main
```

- List branches not merged into the current branch yet:

```bash
git branch --no-merged
```

- List branches that contain a commit (for example, to check which branches include a fix):

```bash
git branch --contains <commit>
```

- List branches matching a pattern:

```bash
git branch --list 'feature/*'
```

- List branches by the date of the last commit, newest first:

```bash
git branch --sort=-committerdate
```

- `git branch` output is meant for humans and can change between Git versions. In scripts, use [`git for-each-ref`](https://git-scm.com/docs/git-for-each-ref):

```bash
git for-each-ref --format='%(refname:short) %(upstream:short)' refs/heads/
```

### Comparing branches

- These commands use the `A..B` and `A...B` revision syntax (see [[🛠️ Core Git#Revision syntax]]).
- Show commits on `feature` that aren't on `main` (the commits that merging `feature` would add):

```bash
git log --oneline main..feature
```

- Show the changes made on `feature` since it diverged from `main` (what a pull request shows):

```bash
git diff main...feature
```

- Show the difference between the two branch tips (includes changes made on `main` after the divergence):

```bash
git diff main feature
```

- Count commits only on `main` (left) and only on `feature` (right):

```bash
git rev-list --left-right --count main...feature
```

- Show the graph of all branches:

```bash
git log --oneline --graph --decorate --all
```

- Show the merge base (the commit where the branches diverged):

```bash
git merge-base main feature
```

- Check whether a commit is in a branch (exit status `0` if it is; for scripts):

```bash
git merge-base --is-ancestor <commit> <branch>
```

### Renaming branches

- Rename the current branch with the `-m`, `--move` option:

```bash
git branch -m <new_name>
```

- Rename any branch:

```bash
git branch -m <old_name> <new_name>
```

- `-m` refuses if `<new_name>` exists; `-M` overwrites it. Git also renames the branch's reflog and moves its configuration (including the upstream).
- A remote has no rename operation. Push the branch under the new name, then delete the old name:

```bash
git push -u origin <new_name>
git push origin --delete <old_name>
```

- To rename the default branch (for example, `master` to `main`), rename it in the hosting service first. GitHub and GitLab then update pull request targets and branch protection rules. Then update each clone:

```bash
git branch -m master main
git fetch origin
git branch -u origin/main main
git remote set-head origin --auto
```

### Moving branches

- Point an existing branch (not the current one) to another commit:

```bash
git branch -f <branch_name> <commit>
```

- Reset an existing branch to a commit and switch to it:

```bash
git switch -C <branch_name> <commit>
```

- To move the current branch, use [`git reset`](https://git-scm.com/docs/git-reset) (see [[🛠️ Git conventions#Undoing changes]]).
- Commits that the branch no longer reaches stay recoverable through its reflog (`<branch_name>@{1}`).

### Deleting branches

- To delete a branch, use the `-d`, `--delete` option:

```bash
git branch -d feature
```

- `-d` deletes the branch only if it's fully merged into its upstream, or into `HEAD` if it has no upstream. This prevents losing unmerged commits.
- To force-remove a branch, regardless of whether it has been merged:

```bash
git branch -D feature
```

- `-D` is short for `--delete --force`.
- You can't delete the current branch or a branch checked out in another worktree. Switch to another branch first.
- After a squash or rebase merge, `-d` refuses to delete the branch because its original commits aren't in `main` (see [[🛠️ Git conventions#Daily workflow]]).
- `git branch -d` and `-D` delete only the local branch, not the branch on the remote. To delete a remote branch:

```bash
git push origin --delete feature
```

```bash
git push origin :feature
```

>[!note]+ Why `:feature` deletes a branch
>- The colon isn't a delete flag. It's part of the [refspec](https://git-scm.com/book/en/v2/Git-Internals-The-Refspec) format, `<src>:<dst>`: `git push origin <src>:<dst>` sets `<dst>` on `origin` to `<src>`.
>- With an empty `<src>`, the command pushes nothing to `feature` on `origin`, which makes `feature` on `origin` not exist.
>- `--delete` is the explicit form of the same operation.

- Deleting a branch on the remote doesn't delete the remote-tracking branches in other clones. Each clone removes them on fetch with pruning:

```bash
git fetch --prune
```

```bash
git remote prune origin
```

- To prune on every fetch, set `fetch.prune` (see [[🛠️ Git conventions#Setting up Git]]).
- Delete all local branches whose upstream is gone (review the list before running it, because `-D` deletes unmerged work):

```bash
git for-each-ref --format='%(refname:short) %(upstream:track)' refs/heads/ | awk '$2 == "[gone]" {print $1}' | xargs -r git branch -D
```

---

- Deleting a branch deletes only the ref and its reflog. The commits stay in the object database until garbage collection.
- `git branch -d` prints the tip hash of the deleted branch:

```text
Deleted branch feature (was 3f2c1ab).
```

- Restore the branch from that hash:

```bash
git branch feature 3f2c1ab
```

- If the hash is lost, find it in the `HEAD` reflog (`git reflog`) or with [`git fsck --lost-found`](https://git-scm.com/docs/git-fsck).

### Orphan branches

>An **orphan branch** is a branch whose first commit has no parent. It shares no history with the other branches.

- Create an orphan branch. `git switch --orphan` also removes all tracked files from the index and the working tree:

```bash
git switch --orphan <new_branch_name>
```

- Use orphan branches for content unrelated to the main code: for example, a `gh-pages` branch with a built website.
- Merging an orphan branch into a branch with other history requires `git merge --allow-unrelated-histories`.

### Working on several branches at once

- A working tree has one checked-out branch. To work on another branch without stashing or committing, check it out in a separate directory with [`git worktree`](https://git-scm.com/docs/git-worktree):

```bash
git worktree add ../project-hotfix hotfix/payment-timeout
```

- Create a new branch in a new worktree:

```bash
git worktree add -b <new_branch_name> ../project-hotfix origin/main
```

- List and remove worktrees:

```bash
git worktree list
git worktree remove ../project-hotfix
```

- All worktrees share one object database and one set of refs; each has its own `HEAD` and index (see [[🛠️ Core Git#Working directory]]).
- A branch can be checked out in only one worktree at a time.

## Remote branches

- One branch name can refer to three different refs:

| Name                  | Ref                                    | Location              | Updated by                               |
| --------------------- | -------------------------------------- | --------------------- | ---------------------------------------- |
| `feature`             | `refs/heads/feature`                   | Your repository       | Your commits, merges, rebases, resets.   |
| `origin/feature`      | `refs/remotes/origin/feature`          | Your repository       | `git fetch`, `git pull`, `git push`.     |
| `feature` on `origin` | `refs/heads/feature` in the remote     | Remote repository     | `git push` from any clone.               |

- `origin/feature` is a **remote-tracking branch**: a read-only copy of the remote branch's position at the last fetch. It isn't a live view of the remote. See [[🛠️ Core Git#Remotes and remote-tracking branches]].

### Fetching and listing remote branches

- Update the remote-tracking branches of `origin`:

```bash
git fetch
```

- Update the remote-tracking branches of all remotes:

```bash
git fetch --all
```

- List remote-tracking branches (as of the last fetch):

```bash
git branch -r
```

- List the branches currently on the remote, without fetching:

```bash
git ls-remote --heads origin
```

- `origin/HEAD` is a symbolic ref to the remote's default branch. Update it after the default branch changes on the remote:

```bash
git remote set-head origin --auto
```

### Checking out a remote branch

- You can't commit to a remote-tracking branch. To work on a remote branch, create a local branch from it.
- If no local branch named `feature` exists and exactly one remote has a branch `feature`, `git switch feature` creates a local `feature` from `origin/feature` and sets it as the upstream:

```bash
git switch feature
```

>[!example]-
>```text
>branch 'feature' set up to track 'origin/feature'.
>Switched to a new branch 'feature'
>```

- Create the local branch explicitly (required when several remotes have the same branch name):

```bash
git switch -c feature --track origin/feature
```

```bash
git checkout --track origin/feature
```

- To inspect a remote branch without creating a local branch, switch to it in a detached state:

```bash
git switch --detach origin/feature
```

### Upstream branches

>The **upstream** of a local branch is the remote-tracking branch it's linked to.

- The upstream is the default source for `git pull`, the default target for `git push`, the reference for the ahead/behind counts in `git status`, and the meaning of `@{u}` in revision syntax.
- Git stores the upstream in `.git/config`:

```ini
[branch "feature"]
	remote = origin
	merge = refs/heads/feature
```

- Set the upstream of the current branch:

```bash
git branch -u origin/feature
```

- Push and set the upstream in one command:

```bash
git push -u origin feature
```

- Show the upstream of the current branch:

```bash
git rev-parse --abbrev-ref @{u}
```

- Show the current branch, its upstream, and the ahead/behind counts:

```bash
git status -sb
```

>[!example]-
>```text
>## feature...origin/feature [ahead 2, behind 1]
>```

- Remove the upstream:

```bash
git branch --unset-upstream
```

- To set the upstream automatically on the first push of a new branch, set `push.autoSetupRemote` (see [[🛠️ Git conventions#Setting up Git]]).

### Pushing branches

- Push a local branch to the branch of the same name on `origin`:

```bash
git push origin feature
```

- Push the current branch under the same name and set the upstream:

```bash
git push -u origin HEAD
```

- Push a local branch to a remote branch with a different name:

```bash
git push origin <local_branch_name>:<remote_branch_name>
```

- Push the current branch to its upstream (after the upstream is set):

```bash
git push
```

- The remote accepts a push only if it's a fast-forward of the remote branch. If someone else pushed first, Git rejects the push: fetch, integrate the remote changes (merge or rebase), and push again.
- After you rewrite a pushed branch (rebase, amend), push with `--force-with-lease` (see [[🛠️ Git conventions#Rewriting history]]).

### Updating a branch from its upstream

- [`git pull`](https://git-scm.com/docs/git-pull) runs `git fetch`, then integrates the upstream into the current branch:

```bash
git pull
```

- Rebase local commits on top of the upstream instead of merging:

```bash
git pull --rebase
```

- Update only if no merge is needed (fails if the branches have diverged):

```bash
git pull --ff-only
```

- If the local branch and its upstream have diverged and neither `pull.rebase` nor `pull.ff` is set, recent Git versions refuse to pull and ask you to choose. To set the default, see [[🛠️ Git conventions#Setting up Git]].
- Fast-forward a local branch that isn't checked out, without switching to it:

```bash
git fetch origin main:main
```

- This fails if `main` has local commits that aren't on `origin/main`, and it refuses to update the current branch.

### Cloning branches

- [`git clone`](https://git-scm.com/docs/git-clone) checks out the remote's default branch. To check out another branch, use the `--branch` (`-b`) option:

```bash
git clone --branch <branch_name> <link_to_repository>
```

- `--branch` changes only the checked-out branch; Git still fetches all branches. To fetch only that branch, add `--single-branch`:

```bash
git clone --branch <branch_name> --single-branch <link_to_repository>
```

- `--single-branch` also limits later fetches to that branch. `--depth` implies `--single-branch`.
- Add another branch to a single-branch clone:

```bash
git remote set-branches --add origin <branch_name>
git fetch origin
```

- `--branch` also accepts a tag; the clone then starts in a detached `HEAD` state.

## Merging branches

- Git integrates the changes of two branches in one of two ways:
	- **Merging** — join the histories with a merge commit (or a fast-forward).
	- **Rebasing** — re-create the commits of one branch on top of the other (see [[#Rebasing branches]]).
- To copy individual commits between branches, see [[🛠️ Git cherry-pick]].

---

- The work on `feature` is finished, and it's time to integrate it into `main`. Switch to the branch that receives the changes, then run [`git merge`](https://git-scm.com/docs/git-merge) with the branch to integrate:

```bash
git switch main
git merge feature
```

- `git merge` changes only the current branch. `feature` stays where it is.
- Git first finds the merge base of the two branches, then performs a fast-forward or a three-way merge. For the algorithm, see [[🛠️ Core Git#Merge]].

### Fast-forward merges

>A **fast-forward merge** happens when the current branch tip is an ancestor of the branch being merged: the current branch has no commits that the other branch doesn't have.

- Before the merge, `main` has no new commits since `feature` was created:

```text
A---B---C  (HEAD -> main)
         \
          D---E  (feature)
```

- Git moves `main` forward to `E`. No new commit is created and no diffs are combined:

```text
A---B---C---D---E  (HEAD -> main, feature)
```

- Create a merge commit even when a fast-forward is possible (keeps a record that a branch was integrated, and keeps the branch's commits grouped):

```bash
git merge --no-ff feature
```

- Merge only if a fast-forward is possible; otherwise fail and change nothing:

```bash
git merge --ff-only feature
```

### Three-way merges

- If both branches have new commits since the merge base, a fast-forward is impossible:

```text
          D---E  (feature)
         /
A---B---C---F---G  (HEAD -> main)
```

- Git compares three snapshots: the merge base (`C`) and the two tips (`G`, `E`):
	- A change made on one side only is taken into the result.
	- The same change made on both sides is taken once.
	- Different changes to the same lines on both sides are a **conflict** (see [[#Merge conflicts]]).
- Git records the result as a **merge commit** `M` with two parents: the previous tip of the current branch (`G`, first parent) and the tip of the merged branch (`E`, second parent):

```text
          D---E  (feature)
         /     \
A---B---C---F---G---M  (HEAD -> main)
```

- `git log --first-parent main` follows only first parents: it shows the history of `main` with each merged branch as one merge commit.
- To keep a long-running branch up to date, merge `main` into it regularly, or rebase it on `main` (see [[#Rebasing branches]]). Frequent integration keeps conflicts small.

### Squash merges

- Combine all changes of a branch into one new commit on the current branch:

```bash
git merge --squash feature
git commit
```

- `--squash` stages the combined changes but doesn't commit and doesn't record a merge: the new commit has one parent. Git doesn't consider `feature` merged, so `git branch -d feature` refuses to delete it.
- Hosting services use the same approach for the "Squash and merge" method (see [[🛠️ Git conventions#Merge methods]]).

### Merge conflicts

- Sometimes, code in one branch conflicts with code in another branch, and a **merge conflict** occurs. Git stops the merge and leaves the conflicting files for you to resolve.

>A **merge conflict** occurs when both branches changed the same lines of a file differently since the merge base, or when one branch changed a file that the other branch deleted.

- Example:
	1. In the common ancestor of `main` and `feature`, a file contains the line `Hello world`.
	2. `feature` changes the line to `Hello feature`.
	3. `main` changes the same line to `Hello main`.
	4. Merging `feature` into `main` produces a conflict: Git can't choose between `Hello main` and `Hello feature`.
- Changes that don't conflict are merged and staged. Git writes conflict markers into the conflicting files (see [[🛠️ Core Git#Conflicts]]) and stores the base, ours, and theirs versions in the index.

---

- To resolve a conflict, list the conflicting (unmerged) files:

```bash
git status
```

- Edit each file: keep the correct content and remove the conflict markers.
- Stage each resolved file, then complete the merge:

```bash
git add <path>
git merge --continue
```

- Cancel the merge and return to the state before it:

```bash
git merge --abort
```

- Resolve conflicts in a visual merge tool, which walks you through the conflicting lines:

```bash
git mergetool
```

- Take one side's version of a whole file:

```bash
git restore --ours <path>
git restore --theirs <path>
```

- `ours` is the current branch (the one you're merging into); `theirs` is the branch being merged.
- Show the merge base version in the conflict markers in addition to the two sides (easier to see what each side changed):

```bash
git config --global merge.conflictStyle zdiff3
```

---

- Resolve all conflicting hunks in favor of one side automatically, with the `-X` (strategy option) flag:

```bash
git merge -X ours feature
```

```bash
git merge -X theirs feature
```

- With `-X ours`, Git keeps the current branch's version of each conflicting hunk, and still takes all non-conflicting changes from `feature`.

>[!warning]+ `-X ours` vs. `-s ours`
>`git merge -s ours feature` uses the `ours` *strategy*: it records a merge commit but discards **all** changes from `feature`, not only the conflicting ones.

- To record conflict resolutions and replay them automatically when the same conflict appears again, enable `rerere` (see [[🛠️ Core Git#Conflicts]]).

### Undoing a merge

- Undo a merge that you haven't pushed (`ORIG_HEAD` is the tip before the merge; uncommitted changes are discarded):

```bash
git reset --hard ORIG_HEAD
```

- Undo a pushed merge with a new commit that reverts it. `-m 1` keeps the first parent's side (the branch you merged into):

```bash
git revert -m 1 <merge_commit>
```

- After a reverted merge, the branch's commits are still in the history of `main`. Merging the branch again doesn't bring back their changes. To re-merge the branch, revert the revert commit first.

## Rebasing branches

>**Rebasing** is the process of moving a sequence of commits from one base commit to another by re-creating each commit on top of the new base.

- Rebasing also integrates changes from two branches, but without a merge commit. Instead, it changes the branch's base commit (the commit the branch was created from).
- Before the rebase:

```text
          D---E  (HEAD -> feature)
         /
A---B---C---F---G  (main)
```

- After `git rebase main` on `feature`:

```text
                  D'---E'  (HEAD -> feature)
                 /
A---B---C---F---G  (main)
```

- [`git rebase main`](https://git-scm.com/docs/git-rebase) on `feature`:
	1. Finds the merge base of `feature` and `main` (`C`).
	2. Collects the commits of `feature` since the merge base (`D`, `E`).
	3. Moves `HEAD` to the tip of `main` (`G`) in a detached state.
	4. Re-applies each collected commit in order. Each result is a new commit (`D'`, `E'`) with the same author, message, and changes, but a new parent and a new hash.
	5. Points `feature` to the last new commit (`E'`) and switches back to `feature`.
- `main` doesn't change. Only the rebased branch moves.
- The original commits `D` and `E` aren't deleted. They stay reachable through the reflog and `ORIG_HEAD` until garbage collection.
- Commits whose changes are already in `main` (for example, cherry-picked earlier) are skipped.

---

- Rebase `feature` on `main`:

```bash
git switch feature
git rebase main
```

- Or, in one command (switches to `feature` first):

```bash
git rebase main feature
```

- `git rebase` without arguments rebases the current branch on its upstream.
- After the rebase, `feature` is a descendant of `main`, so merging it is a fast-forward. Rebasing then fast-forwarding produces a linear history:

```bash
git switch main
git merge --ff-only feature
```

- Rebasing rewrites history: the rebased branch contains new commits that replace the old ones. If others have based work on the old commits, their copies still contain them. **Rebase only branches that no one else works on**, and push a rebased branch with `--force-with-lease` (see [[🛠️ Git conventions#Rewriting history]]).
- To edit, reorder, squash, or drop commits during a rebase, use interactive rebase (`git rebase -i`, see [[🛠️ Git conventions#Rewriting history]]).

### Rebase conflicts

- Git replays commits one at a time, so a conflict stops the rebase at a specific commit. The same conflict can appear for several commits.
- To resolve a conflict, edit the files, stage them, and continue with the next commit:

```bash
git add <path>
git rebase --continue
```

- Skip the current commit (drop its changes):

```bash
git rebase --skip
```

- Cancel the rebase and return the branch to its original state:

```bash
git rebase --abort
```

>[!warning]+ `ours` and `theirs` are swapped during a rebase
>A rebase replays your commits on top of the other branch. During a rebase, `ours` (`--ours`, `-X ours`) is the branch you're rebasing onto, and `theirs` is your commit being replayed.

### Rebasing onto another base

- `git rebase --onto <new_base> <upstream> <branch>` takes the commits of `<branch>` that aren't in `<upstream>` and replays them on `<new_base>`.
- Example: `client` was branched from `server`, but `client` doesn't depend on `server` and should go into `main` alone:

```text
A---B---C  (main)
     \
      D---E  (server)
           \
            F---G  (client)
```

```bash
git rebase --onto main server client
```

```text
          F'---G'  (client)
         /
A---B---C  (main)
     \
      D---E  (server)
```

- The same command moves a branch after its base branch was squash-merged: `git rebase --onto main <old_base_commit> <branch>` replays only the branch's own commits.
- Rebase a chain of dependent branches (stacked branches) in one operation; Git also moves every branch that points to a rebased commit:

```bash
git rebase --update-refs main
```

### Undoing a rebase

- `ORIG_HEAD` points to the branch tip before the rebase:

```bash
git reset --hard ORIG_HEAD
```

- `ORIG_HEAD` is overwritten by the next reset, merge, or rebase. The branch reflog keeps the older state: `<branch>@{1}` is the value before the last change. Use `git reflog <branch>` to find the right entry:

```bash
git reflog feature
git reset --hard feature@{1}
```

### Merge vs. rebase

| Aspect              | Merge                                                                 | Rebase                                                                       |
| ------------------- | --------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| History             | Records the actual history: parallel lines joined by merge commits.   | Produces a linear history, as if the work were done after the latest `main`. |
| Existing commits    | Unchanged.                                                            | Replaced by new commits with new hashes.                                     |
| Conflicts           | Resolved once, in the merge commit.                                   | Resolved per replayed commit; the same conflict can repeat.                  |
| Shared branches     | Safe.                                                                 | Unsafe for commits that others have; requires a force push.                  |
| Integration record  | The merge commit shows when and what was integrated.                  | Not recorded.                                                                |
| Typical use         | Integrating a finished branch into `main`; public branches.           | Updating a private branch on `main`; cleaning up history before review.      |

- A common combination: rebase your feature branch on `main` while you work on it, then integrate it into `main` with a merge, squash, or fast-forward, according to the repository's merge method (see [[🛠️ Git conventions#Merge methods]]).

## Branching conventions

- One branch per task. Keep branches small, short-lived, and specific, and integrate `main` into them often.
- Team rules for branches are in [[🛠️ Git conventions]]:
	- Naming: [[🛠️ Git conventions#Branch naming]].
	- Branching models (trunk-based development, GitHub flow, Git Flow): [[🛠️ Git conventions#Branching strategies]].
	- Workflow for one task: [[🛠️ Git conventions#Daily workflow]].
	- Merge methods for pull requests: [[🛠️ Git conventions#Merge methods]].
	- Rules for rewriting pushed branches: [[🛠️ Git conventions#Rewriting history]].
- Hosting services enforce rules on important branches with branch protection: blocking direct pushes, force pushes, and merges without approvals or passing checks (see [[🛠️ Core Git#Git hosting services]]).

## Command reference

### `git branch`

>[`git branch`](https://git-scm.com/docs/git-branch) lists, creates, or deletes branches.

```bash
git branch [--list] [-a | -r] [-v | -vv] [--merged | --no-merged | --contains <commit>] [<pattern>...]
git branch [--track | --no-track] [-f] <branch_name> [<start_point>]
git branch (--set-upstream-to=<upstream> | -u <upstream>) [<branch_name>]
git branch --unset-upstream [<branch_name>]
git branch (-m | -M) [<old_branch>] <new_branch>
git branch (-c | -C) [<old_branch>] <new_branch>
git branch (-d | -D) [-r] <branch_name>...
```

| Option                              | Description                                                                                         |
| ----------------------------------- | --------------------------------------------------------------------------------------------------- |
| `-l`, `--list [<pattern>]`          | List branches; with a pattern, list only matching branches.                                         |
| `-a`, `--all`                       | List local and remote-tracking branches.                                                            |
| `-r`, `--remotes`                   | List remote-tracking branches; with `-d`, delete a remote-tracking branch.                          |
| `-v`, `-vv`, `--verbose`            | Show the tip hash and subject of each branch; with `-vv`, also show the upstream and ahead/behind counts. |
| `--show-current`                    | Print the name of the current branch; print nothing in a detached `HEAD` state.                     |
| `--merged [<commit>]`               | List branches whose tips are reachable from `<commit>` (default: `HEAD`).                           |
| `--no-merged [<commit>]`            | List branches whose tips aren't reachable from `<commit>` (default: `HEAD`).                        |
| `--contains <commit>`               | List branches that contain `<commit>`.                                                              |
| `--sort=<key>`                      | Sort the list by a key, for example `-committerdate` (newest first).                                |
| `-d`, `--delete`                    | Delete a branch that is fully merged into its upstream or `HEAD`.                                   |
| `-D`                                | Delete a branch regardless of its merge status (`--delete --force`).                                |
| `-m`, `--move`                      | Rename a branch, its reflog, and its configuration.                                                 |
| `-M`                                | Rename a branch even if the new name exists (`--move --force`).                                     |
| `-c`, `--copy`                      | Copy a branch with its reflog and configuration.                                                    |
| `-f`, `--force`                     | Reset an existing branch to the start point; with `-d`, `-m`, or `-c`, force the operation.         |
| `-t`, `--track`                     | Set the start point as the upstream of the new branch.                                              |
| `--no-track`                        | Don't set an upstream, even if `branch.autoSetupMerge` would.                                       |
| `-u`, `--set-upstream-to=<upstream>` | Set the upstream of a branch (default: the current branch).                                        |
| `--unset-upstream`                  | Remove the upstream of a branch.                                                                    |
| `--edit-description`                | Edit the branch description (used by `git format-patch` and `git request-pull`).                    |

### `git switch`

>[`git switch`](https://git-scm.com/docs/git-switch) switches branches.

```bash
git switch [<options>] [--no-guess] <branch>
git switch [<options>] --detach [<start-point>]
git switch [<options>] (-c|-C) <new-branch> [<start-point>]
git switch [<options>] --orphan <new-branch>
```

| Option                               | Description                                                                                                 |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| `-c`, `--create`                     | Create a new branch named `<new-branch>` at `<start-point>` and switch to it.                               |
| `-C`, `--force-create`               | Similar to `--create`, but if `<new-branch>` already exists, reset it to `<start-point>`.                    |
| `-d`, `--detach`                     | Switch to a commit in a detached `HEAD` state.                                                              |
| `--orphan`                           | Create a new branch with no history and remove all tracked files.                                          |
| `--guess`, `--no-guess`              | Create a local branch from a matching remote-tracking branch if `<branch>` doesn't exist (on by default).   |
| `-t`, `--track`                      | Set the start point as the upstream of the new branch.                                                      |
| `--no-track`                         | Don't set an upstream for the new branch.                                                                   |
| `-m`, `--merge`                      | Carry local changes to the target branch with a three-way merge instead of refusing to switch.              |
| `--discard-changes`, `-f`, `--force` | Discard local changes and switch.                                                                           |
| `--recurse-submodules`               | Update the working trees of submodules to the commits recorded in the target branch.                        |
| `-`                                  | Switch to the previously checked-out branch (`@{-1}`).                                                      |

### `git checkout`

>[`git checkout`](https://git-scm.com/docs/git-checkout) switches branches or restores working tree files.

- `git checkout` is the older command that `git switch` and `git restore` replace. Equivalent commands:

| `git checkout`                        | `git switch` / `git restore`                                    |
| ------------------------------------- | --------------------------------------------------------------- |
| `git checkout <branch>`               | `git switch <branch>`                                           |
| `git checkout -b <new> [<start>]`     | `git switch -c <new> [<start>]`                                 |
| `git checkout -B <new> [<start>]`     | `git switch -C <new> [<start>]`                                 |
| `git checkout --track origin/<branch>` | `git switch <branch>` or `git switch -c <branch> --track origin/<branch>` |
| `git checkout <commit>`               | `git switch --detach <commit>`                                  |
| `git checkout --orphan <new>`         | `git switch --orphan <new>` (also removes tracked files)        |
| `git checkout -- <path>`              | `git restore <path>`                                            |
| `git checkout <commit> -- <path>`     | `git restore --source=<commit> --staged --worktree <path>`      |

### `git merge`

>[`git merge`](https://git-scm.com/docs/git-merge) joins two or more development histories together.

```bash
git merge [--ff | --no-ff | --ff-only] [--squash] [--no-commit] [-m <msg>] [-s <strategy>] [-X <strategy-option>] [<commit>...]
git merge (--continue | --abort | --quit)
```

| Option                          | Description                                                                                          |
| ------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `--ff`                          | Fast-forward when possible; otherwise create a merge commit (default).                               |
| `--no-ff`                       | Create a merge commit even when a fast-forward is possible.                                          |
| `--ff-only`                     | Merge only if a fast-forward is possible; otherwise fail.                                            |
| `--squash`                      | Stage the combined changes of the merged branch without committing or recording a merge.             |
| `--no-commit`                   | Perform the merge, but stop before creating the merge commit.                                        |
| `-m <msg>`                      | Set the message of the merge commit.                                                                 |
| `-s <strategy>`                 | Use a merge strategy: `ort` (default for two heads), `octopus` (default for more), `ours`, `subtree`. |
| `-X <option>`                   | Pass an option to the merge strategy, for example `ours`, `theirs`, or `ignore-space-change`.        |
| `--allow-unrelated-histories`   | Merge two histories that have no common ancestor.                                                    |
| `--autostash`                   | Stash local changes before the merge and reapply them after it.                                      |
| `-S`, `--gpg-sign`              | Sign the merge commit.                                                                               |
| `--continue`                    | Complete the merge after resolving conflicts.                                                        |
| `--abort`                       | Cancel the merge and restore the state before it.                                                    |
| `--quit`                        | Forget the merge in progress; leave the index and the working tree as they are.                      |

### `git rebase`

>[`git rebase`](https://git-scm.com/docs/git-rebase) reapplies commits on top of another base tip.

```bash
git rebase [-i | --interactive] [<options>] [--exec <cmd>] [--onto <newbase> | --keep-base] [<upstream> [<branch>]]
git rebase [-i | --interactive] [<options>] [--exec <cmd>] [--onto <newbase>] --root [<branch>]
git rebase (--continue | --skip | --abort | --quit | --edit-todo | --show-current-patch)
```

| Option                       | Description                                                                                              |
| ---------------------------- | -------------------------------------------------------------------------------------------------------- |
| `-i`, `--interactive`        | Edit the list of commits before replaying them: reorder, reword, squash, edit, or drop commits.          |
| `--onto <newbase>`           | Replay the commits on `<newbase>` instead of `<upstream>`.                                               |
| `--keep-base`                | Keep the current merge base as the base: rewrite the branch's commits without moving them.               |
| `--root`                     | Rebase all commits reachable from the branch, including the root commit.                                 |
| `--autosquash`               | Move `fixup!` and `squash!` commits next to their targets in an interactive rebase.                      |
| `--autostash`                | Stash local changes before the rebase and reapply them after it.                                         |
| `--update-refs`              | Also move branches that point to rebased commits.                                                        |
| `-r`, `--rebase-merges`      | Re-create merge commits instead of flattening the history.                                               |
| `-x`, `--exec <cmd>`         | Run a command after each replayed commit; stop if it fails.                                              |
| `-X <option>`                | Pass an option to the merge strategy, for example `ours` or `theirs`.                                    |
| `--continue`                 | Continue the rebase after resolving a conflict.                                                          |
| `--skip`                     | Skip the current commit and continue.                                                                    |
| `--abort`                    | Cancel the rebase and restore the original branch.                                                       |
| `--edit-todo`                | Edit the remaining list of commits during an interactive rebase.                                         |

## References 

- https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell
- https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging
- https://git-scm.com/book/en/v2/Git-Branching-Branch-Management
- https://git-scm.com/book/en/v2/Git-Branching-Remote-Branches
- https://git-scm.com/book/en/v2/Git-Branching-Rebasing
- https://www.atlassian.com/git/tutorials/using-branches
- https://stackoverflow.com/questions/7303687/why-does-git-use-a-colon-branch-to-delete-remote-branches
