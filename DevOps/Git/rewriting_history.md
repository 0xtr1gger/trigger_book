Often, when working with Git, it can be beneficial to revise the local commit history. The ability to make decisions at the very last minute is one of the greatest advantages of Git.

The staging area is useful to decide what files will be included in the next commit. But in addition, it is possible to rewrite any existing commits to make them appear to have been initially made differently. This may include rearranging the commits in a different order, editing the files or commit messages, squashing or dividing commits, or deleting commits entirely.
## changing the last commit

Changing the most recent commit is probably the most common task when rewriting Git history.

Using `git commit --amend` can be useful for including forgotten files or correcting typos and minor mistakes in previous commits. This command helps to avoid the need to create numerous small, unnecessary commits that can clutter Git's history. 

>`git commit --amend` command does not change the number of commits in the repository, meaning that it does not create any new commits on top of existing ones. Instead, it only replaces the last commit with a new one.

- To modify the last commit, first make the necessary changes, add the updated files to the staging area, and use the `git commit` command with the `--amend` option to save changes.

For example, to alter the `README.md` file and attribute the changes to the last commit:

```bash
git add README.md
git commit --amend
```

- Git amend also allows modifying the commit message of the previous commit. 

- The `git commit --amend` commend opens a text editor where the commit message can be modified. When the message is saved and the editor is closed, Git replaces the old commit message with the new one.

- The new commit message can also be specified with the `-m` option, which is often quicker. 

```bash
git commit --amend -m "new commit message"
```

- To update the content of the last commit while leaving the commit message unchanged, the `--no-edit` option can be specified:

```bash
git commit --amend --no-edit
```

>The `git commit --amend` command does not merely alter the most recent commit but replaces it entirely with a completely new one. This means that the replaced commit vanishes without a trace.
>For this reason, the `git commit --amend` should not be applied to public repositories to which other developers contribute, as this can lead to confusion and troublesome merge conflicts in the future.

>Amending changes the SHA-1 hash of the commit.
## modifying older or multiple commits 

Git does not inherently have a tool designed specifically for changing commit history. However, the same effects can be accomplished with the `git rebase` command in an interactive mode (`-i`/`--interactive`).

git rebase in interactive mode is used to modify one or multiple commits anywhere in the Git history. It can be used to:

- Add or modify files
- Remove files
- Edit commit messages
- Remove commits
- Reset commits
- Squash (combine) multiple commits together
- Insert commits between others

Here is a step-by-step guide on how to modify one or more older commits:

1. Identify the commit range
	- Use the `git log` command to determine the number of the commits to be changed and their commit hashes. The `--oneline` option may be helpful in this case.

```bash
git log --oneline
```

2. Start the interactive rebase

	- Initiate the interactive rebase with the `git rebase -i` command. Specify the number of commits to alter before the starting point. You can either use the last commit (referred to as `HEAD`) or any earlier commit (specified with a commit hash).

```bash
# to modify the last n commits
git rebase -i HEAD~n


# to modify n commits before the specified one
git rebase -i 1234567~n
```

where
- `-i` (`--interactive`) indicates the interactive mode
- `HEAD~n`/`1234567~n` refers to the last `n` commits before the specified one. 

> Every commit in the range `HEAD~n..HEAD` with a changed message and *all of its descendants* will be rewritten. 
>It is important to note that these commits are listed in the opposite order compared to the `git log` command.

This will start a default text editor with a list of the last `n` commits. It will look somewhat like this:

```bash
pick 1234567 Commit message 1
pick 8901234 Commit message 2
pick 5678901 Commit message 3

# Rebase 1234567..5678901 onto 1234567 (3 commands)
# ...

```

Each line represents a commit; in front of each commit, a command is specified:

- `pick`
	- The default command. Apply the commit as-is without any changes.
- `reword`
	- Edit the commit message without changing the commit content.
- `edit`
	- Stop the rebase process and allow to modify the contents of the files of the commit. When editing is finished, the rebase continues.
- `squash`
	- Combine the commit with the previous one. Also promotes editing the resulting commit message.
- `fixup`
	- Combine the commit with the previous one (the same as `squash`), and discard the original commit message in favor of a default one.
- `drop` 
	- Remove a commit from the rebase sequence entirely.
- `reset`
	- Reset the commit to its parent commit, effectively undoing the changes made in that commit.

3. Modify the commit list
	- Choose the necessary action to be done against the commit by modifying the commands in front of the commits. 

```bash
edit 1234567 Commit message 1
pick 8901234 Commit message 2
drop 5678901 Commit message 3
```

4. Save and exit the editor

	- After specifying the necessary commands and making changes, save the file and close the editor. After saving, Git will start processing each command. For example, encountering the first `reword` command, Git will open another editor allowing you to change the commit message. Make the changes, save, and exit. 

	- For `edit` commands, Git will pause the rebase process, allowing you to make changes to the specified commit.

After using the `edit` command:

5. Make necessary changes to the files in the commit

6. Stage the changes with the `git add` command

```bash
git add .
```

7. Amend the commit

```bash
git commit --amend
```


8. Continue the rebase

	- Once changes are made and the commit is amended, continue the rebase with the `git rebase --continue` command

```bash
git rebase --continue
```


9. Resolve conflicts (if necessary)

	- If any conflicts during the rebase process occurred, Git will prompt about them. To resolve a conflict, follow the steps:
		1. Resolve the conflicts in the file shown by Git.
		2. Stage the resolved files using the `git add` command.
		3. Continue the rebase with `git rebase --continue`.

10. Once all the edits and conflicts are resolved, the rebase will complete, and the commit history will reflect all the modifications made. 

11. Push the changes with the `git push` command (if necessary):

```bash
git push origin branch_name --force
```

---

For example, to modify the last 3 commits, enter the `git rebase` command with the `-i` (`--interactive`) option and the number of commits, `3`, after the `HEAD~` specified:

```bash
git rebase -i HEAD~3
```

This will open a default text editor with a list of the last `3` commits. 

---

>Using `git rebase -i` is a powerful way to modify Git commit history interactively. However, it is essential to remember that rewriting history can have implications, especially in shared repositories.
