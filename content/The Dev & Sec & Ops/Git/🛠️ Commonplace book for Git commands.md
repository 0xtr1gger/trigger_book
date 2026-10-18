---
created: 2026-09-20
updated: 2026-10-12
tags:
  - Git
---


## Creating repositories

- Create a new repository in the current directory:

```bash
git init
```

- Create a bare repository (no working directory; for servers):

```bash
git init --bare
```

- Copy an existing repository, including its full history:

```bash
git clone <url> [<directory>]
```

- Clone without a working directory (for a server or mirror):

```bash
git clone --bare <url>
```

- Copy only recent history (a shallow clone), or omit blob content until needed (a partial clone):

```bash
git clone --depth 1 <url>
git clone --filter=blob:none <url>
```

## Inspecting state

- Show the state of the working tree and the index:

```bash
git status
```

- Show differences between the working tree and the index (unstaged changes):

```bash
git diff
```

- Show differences between the index and `HEAD` (staged changes):

```bash
git diff --staged
```

- Show all differences between the working tree and `HEAD`:

```bash
git diff HEAD
```

- List the index content:

```bash
git ls-files --stage
```

## Moving changes between areas

| Command                        | From → to                          | Effect                                                         |
| ------------------------------ | ---------------------------------- | -------------------------------------------------------------- |
| `git add <path>`               | Working tree → index               | Stage the current content of a file.                           |
| `git commit`                   | Index → repository                 | Record the index as a new commit; advance the current branch.  |
| `git restore --staged <path>`  | Repository (`HEAD`) → index        | Unstage a file; keep working tree changes.                     |
| `git restore <path>`           | Index → working tree               | Discard unstaged changes to a file.                            |
| `git switch <branch>`          | Repository → index, working tree   | Check out another branch.                                      |
| `git rm <path>`                | Index, working tree                | Delete a file and stage the deletion.                          |
| `git rm --cached <path>`       | Index                              | Stop tracking a file; keep it on disk.                         |

- Stage parts of a file by hunk:

```bash
git add -p
```

## Ignoring files

- Show which rule ignores a file:

```bash
git check-ignore -v <path>
```

## Inspecting references

- List all refs and the hashes they point to:

```bash
git show-ref
```

- Resolve any name to its object ID:

```bash
git rev-parse <name>
```

## Remotes and remote-tracking branches

| Command                           | Effect                                                                                     |
| --------------------------------- | ------------------------------------------------------------------------------------------ |
| `git remote -v`                   | List remotes and their URLs.                                                               |
| `git fetch [<remote>]`            | Download new objects and update remote-tracking branches; don't touch local branches.      |
| `git pull`                        | Run `git fetch`, then merge (or rebase) the upstream into the current branch.              |
| `git push [<remote> <branch>]`    | Upload objects and update the remote branch.                                               |
| `git push -u <remote> <branch>`   | Push and set the remote branch as the upstream of the current branch.                      |
| `git branch -vv`                  | Show local branches with their upstream and ahead/behind counts.                           |

## Tags

- Create an annotated tag:

```bash
git tag -a v1.0.0 -m "Release 1.0.0"
```

- Create a lightweight tag:

```bash
git tag v1.0.0
```

- Push one tag:

```bash
git push origin v1.0.0
```

- Push annotated tags reachable from the pushed commits:

```bash
git push --follow-tags
```

## Reflog and recovery

- Show the history of `HEAD`:

```bash
git reflog
```

- Restore the current branch to the state before the last operation:

```bash
git reset --hard HEAD@{1}
```

- Keep commits made in a detached `HEAD` by creating a branch:

```bash
git switch -c <new-branch>
```

## Inspecting objects

- These are plumbing commands. Show the type of an object:

```bash
git cat-file -t <object>
```

- Show the content of an object in readable form:

```bash
git cat-file -p <object>
```

- Show the tree of the current commit:

```bash
git cat-file -p 'HEAD^{tree}'
```

- List a tree recursively:

```bash
git ls-tree -r HEAD
```

- Compute the blob hash of content without storing it:

```bash
echo 'test content' | git hash-object --stdin
```

>[!example]-
>```text
>d670460b4b4aece5915caf5c68d12f560a9fe3e4
>```

## Packfiles and maintenance

- Show a packfile's content:

```bash
git verify-pack -v .git/objects/pack/pack-<hash>.idx
```

- Show object counts and repository size:

```bash
git count-objects -vH
```

- Pack objects, pack refs, and delete unreachable objects:

```bash
git gc
```

- List dangling objects (recover lost commits and branches):

```bash
git fsck --lost-found
```

## Merging

- Show the merge base of two branches:

```bash
git merge-base main feature
```

- After editing conflicted files, stage the result and continue:

```bash
git add <path>
git merge --continue
```

- Cancel a merge or rebase in progress:

```bash
git merge --abort
git rebase --abort
```
