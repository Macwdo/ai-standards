---
name: save-finish
description: Finalize local git work safely after implementation. Use when Codex needs to inspect changed files, stage only the intended changes, create a clear commit message, merge the feature branch into the default base branch, and push the base branch while leaving worktree cleanup to the dedicated cleanup workflow.
---

# Save Finish

## Overview

Finish a coding task without leaving the repository in an ambiguous state. Review the diff, check whether `README.md` should be updated, stage intentionally, commit with a high-signal message, merge the feature branch into the repository's default base branch, and push that base branch. Leave linked worktree cleanup to the dedicated `$cleanup-worktrees` workflow after the push succeeds.

## Workflow

1. Inspect the repo state before changing anything:
   - Run `git status --short --branch`.
   - Review the diff for the files that are about to be saved.
   - Notice unrelated changes and avoid staging them unless the user explicitly asks.
   - Determine the current branch with `git branch --show-current`.
   - Determine the default base branch by checking `origin/HEAD` first and falling back to local `main` or `master`.
2. Check whether `README.md` should be updated before saving:
   - Consider whether the task changes setup, usage, workflow, commands, behavior, or documented project structure.
   - If the change affects what a user or contributor needs to know, update `README.md` in the same task.
   - If no README change is needed, make that a conscious decision before continuing.
3. Stage only the intended files:
   - Prefer explicit paths over blind `git add .` when unrelated files may exist.
   - Include new files that are part of the task.
   - Re-check with `git status --short`.
4. Create the commit:
   - Use a concise imperative subject.
   - Prefer a scoped conventional-style message when the change supports it, such as `feat: add save-finish skill` or `chore: update save-finish workflow`.
   - Keep the subject focused on the user-visible or repository-relevant outcome.
5. Merge the feature branch into the base branch:
   - Refuse to proceed if the current branch is already the base branch.
   - Capture the feature branch name before switching branches.
   - Switch to the main worktree or repository root before checking out the base branch.
   - Check out the detected base branch and update it from the remote when appropriate.
   - Merge the feature branch into the base branch locally.
6. Push the base branch:
   - Push the updated base branch to `origin`.
   - Stop immediately if the merge or push fails.
7. Hand off any worktree cleanup to `$cleanup-worktrees` after a successful push:
   - Do not remove the linked worktree as part of `$save-finish`.
   - Treat cleanup as a separate step so audit and removal decisions stay centralized in the cleanup workflow.
   - If the user wants the worktree removed, direct that request to `$cleanup-worktrees`.

## Commit Rules

- Prefer one clear subject line over a vague message like `updates` or `fix stuff`.
- Describe what changed, not the mechanics of editing files.
- Mention the primary outcome first.
- Add a commit body only when it materially helps, such as documenting a safety constraint or follow-up note.

## Safety Rules

- Do not commit unrelated changes just to make the worktree clean.
- Do not merge if the current branch cannot be cleanly merged into the base branch.
- Do not treat `main` as universal; detect the repository's default base branch and support either `main` or `master`.
- Do not delete local or remote branches unless the user explicitly asks.
- Do not remove any worktree from `$save-finish`; delegate that task to `$cleanup-worktrees`.
- If commit, merge, or push fails, stop at the failure, report it, and leave the worktree intact.

## Handy Commands

Review:

```bash
git status --short --branch
git diff --stat
git diff
git diff -- README.md
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

Then, if cleanup is requested, hand off to `$cleanup-worktrees`:

```bash
python3 /home/macwdo/Codes/ai-standards/.agents/skills/cleanup-worktrees/scripts/audit_worktrees.py
```

## Example Requests

- "Use `$save-finish` to commit the skill changes, merge them into `master`, and push. Leave the worktree for `$cleanup-worktrees`."
- "Use `$save-finish` to stage only the docs I changed and create a clean commit."
- "Use `$save-finish` to wrap up this feature branch by merging it into the default base branch without deleting the branch itself."
