---
name: save-finish
description: Finalize local git work safely after implementation. Use when Codex needs to inspect changed files, stage only the intended changes, create a clear commit message, merge the feature branch into the default base branch, push the base branch, and remove the linked worktree after the push succeeds.
---

# Save Finish

## Overview

Finish a coding task without leaving git cleanup half-done. Review the diff, stage intentionally, commit with a high-signal message, merge the feature branch into the repository's default base branch, push that base branch, and remove the linked worktree only after the remote update is confirmed.

## Workflow

1. Inspect the repo state before changing anything:
   - Run `git status --short --branch`.
   - Review the diff for the files that are about to be saved.
   - Notice unrelated changes and avoid staging them unless the user explicitly asks.
   - Determine the current branch with `git branch --show-current`.
   - Determine the default base branch by checking `origin/HEAD` first and falling back to local `main` or `master`.
2. Stage only the intended files:
   - Prefer explicit paths over blind `git add .` when unrelated files may exist.
   - Include new files that are part of the task.
   - Re-check with `git status --short`.
3. Create the commit:
   - Use a concise imperative subject.
   - Prefer a scoped conventional-style message when the change supports it, such as `feat: add save-finish skill` or `chore: update save-finish workflow`.
   - Keep the subject focused on the user-visible or repository-relevant outcome.
4. Merge the feature branch into the base branch:
   - Refuse to proceed if the current branch is already the base branch.
   - Capture the feature branch name before switching branches.
   - Switch to the main worktree or repository root so the target linked worktree can be removed later.
   - Check out the detected base branch and update it from the remote when appropriate.
   - Merge the feature branch into the base branch locally.
5. Push the base branch:
   - Push the updated base branch to `origin`.
   - Stop immediately if the merge or push fails.
6. Clean up the linked worktree only after a successful push:
   - Confirm the target path is a linked worktree rather than the main worktree.
   - Run the removal from the repository root or another safe directory outside the target worktree.
   - Remove it with `git worktree remove <path>`.
   - Keep the branch unless the user explicitly asks to delete it.

## Commit Rules

- Prefer one clear subject line over a vague message like `updates` or `fix stuff`.
- Describe what changed, not the mechanics of editing files.
- Mention the primary outcome first.
- Add a commit body only when it materially helps, such as documenting a safety constraint or follow-up note.

## Safety Rules

- Do not commit unrelated changes just to make the worktree clean.
- Do not merge if the current branch cannot be cleanly merged into the base branch.
- Do not treat `main` as universal; detect the repository's default base branch and support either `main` or `master`.
- Do not remove a dirty worktree.
- Do not remove the main worktree.
- Do not delete local or remote branches unless the user explicitly asks.
- If commit, merge, or push fails, stop at the failure, report it, and leave the worktree intact.

## Handy Commands

Review:

```bash
git status --short --branch
git diff --stat
git diff
git branch --show-current
git symbolic-ref refs/remotes/origin/HEAD
git worktree list
```

Finish:

```bash
git add <paths>
git commit -m "feat: add save-finish skill"
feature_branch="$(git branch --show-current)"
base_branch="$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')"
[ -n "$base_branch" ] || base_branch="$(git branch --list main master --format='%(refname:short)' | head -n 1)"
git checkout "$base_branch"
git merge --no-ff "$feature_branch"
git push origin "$base_branch"
```

Clean up the linked worktree from outside it:

```bash
git worktree remove /absolute/path/to/worktree
```

## Example Requests

- "Use `$save-finish` to commit the skill changes, merge them into `master`, push, and remove this worktree."
- "Use `$save-finish` to stage only the docs I changed and create a clean commit."
- "Use `$save-finish` to wrap up this feature branch by merging it into the default base branch without deleting the branch itself."
