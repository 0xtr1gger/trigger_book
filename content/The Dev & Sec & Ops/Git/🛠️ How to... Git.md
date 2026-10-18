---
created: 2026-09-30
updated: 2026-10-06
tags:
  - Git
---

## How to update branches

```bash
git pull
```
## How to split PRs 

- Split PRs into several branches.

---

- Start from the target branch:

```bash
git fetch origin
git switch main
git pull
```

2. Create the first PR branch and switch to it:

```bash
git switch -c pr-1 main
```

3. Apply commits from the previous branch to this branch:

```bash
git cherry-pick A B
```

4. Push:

```bash
git push origin pr-1
```

5. Create PR `2`, based on RP `1`:

```bash
git switch -c pr-2 pr-1
```

6. Apply next commits:

```bash
git cherry-pick C
```

7. Push:

```bash
git push origin pr-2
```

- ...

8. Create PR `n`, based on PR `n-1`:

```bash
git switch -c pr-n pr-n-1
```

9. Apply commits that go after those applied in PR `n`:

```bash
git cherry-pick X Z
```

10. Push:

```bash
git push -u origin pr-n
```