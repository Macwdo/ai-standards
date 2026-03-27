---
name: save-finish
description: Finalize local git work safely after implementation. Use when Codex needs to inspect changed files, stage only the intended changes, create a clear commit message, push the current branch to the remote, and optionally remove the linked worktree after the push succeeds.
---

# Save Finish

## Overview

Finish a coding task without leaving git cleanup half-done. Review the diff, stage intentionally, commit with a high-signal message, push the branch, and remove the linked worktree only after the remote branch is confirmed.

## Workflow

1. Inspect the repo state before changing anything:
   - Run `git status --short --branch`.
   - Review the diff for the files that are about to be saved.
   - Notice unrelated changes and avoid staging them unless the user explicitly asks.
2. Stage only the intended files:
   - Prefer explicit paths over blind `git add .` when unrelated files may exist.
   - Include new files that are part of the task.
   - Re-check with `git status --short`.
3. Create the commit:
   - Use a concise imperative subject.
   - Prefer a scoped conventional-style message when the change supports it, such as `feat: add save-finish skill` or `chore: update save-finish workflow`.
   - Keep the subject focused on the user-visible or repository-relevant outcome.
4. Push the branch:
   - Determine the current branch with `git branch --show-current`.
   - Push with upstream when needed: `git push -u origin <branch>`.
   - If the branch already tracks a remote, a regular `git push` is enough.
5. Clean up the linked worktree only after a successful push:
   - Confirm the current directory is a linked worktree rather than the main worktree.
   - Move to the repository root or another safe directory outside the target worktree.
   - Remove it with `git worktree remove <path>`.
   - Keep the branch unless the user explicitly asks to delete it.

## Commit Rules

- Prefer one clear subject line over a vague message like `updates` or `fix stuff`.
- Describe what changed, not the mechanics of editing files.
- Mention the primary outcome first.
- Add a commit body only when it materially helps, such as documenting a safety constraint or follow-up note.

## Safety Rules

- Do not commit unrelated changes just to make the worktree clean.
- Do not remove a dirty worktree.
- Do not remove the main worktree.
- Do not delete local or remote branches unless the user explicitly asks.
- If push fails, stop at the failure, report it, and leave the worktree intact.

## Handy Commands

Review:

```bash
git status --short --branch
git diff --stat
git diff
git branch --show-current
git worktree list
```

Finish:

```bash
git add <paths>
git commit -m "feat: add save-finish skill"
git push -u origin "$(git branch --show-current)"
```

Clean up the linked worktree from outside it:

```bash
git worktree remove /absolute/path/to/worktree
```

## Example Requests

- "Use `$save-finish` to commit the skill changes, push the branch, and remove this worktree."
- "Use `$save-finish` to stage only the docs I changed and create a clean commit."
- "Use `$save-finish` to wrap up this feature branch without deleting the branch itself."
