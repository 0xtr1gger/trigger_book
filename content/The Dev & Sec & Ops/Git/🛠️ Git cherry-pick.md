---
created: 2026-09-30
updated: 2026-09-30
tags:
  - Git
---
## `git cherry-pick`


>[`git cherry-pick`](https://git-scm.com/docs/git-cherry-pick) applies the changes introduced by some existing commits.

```bash
git cherry-pick [--edit] [-n] [-m <parent-number>] [-s] [-x] [--ff]
		  [-S[<keyid>]] <commit>…​
git cherry-pick (--continue | --skip | --abort | --quit)
```

- Given one or more existing commits, `cherry-pick` applies the change each one introduces, recording a new commit for each.

| Option | Description |
| ------ | ----------- |
|        |             |

### Examples

- Apply the change introduced by the commit at the tip of the `master` branch and create a new commit with this change:

```bash
git cherry-pick master
```

- Apply the changes introduced by all commits that are ancestors of `master` but not of `HEAD` to produce new commits:

```bash
git cherry-pick ..master
```

```bash
git cherry-pick ^HEAD master
```