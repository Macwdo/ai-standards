---
name: start-work
description: Safely start implementation from the repository default branch by syncing the primary worktree, then creating or reusing a linked feature worktree so no code changes are made in the main worktree.
---

# Start Work

## Workflow

Before implementation:

1. Identify the repository root with `git rev-parse --show-toplevel`.
2. Identify the repository default branch from `origin/HEAD`. If that is unavailable, use the branch currently checked out in the primary worktree.
3. Ensure you are operating from the primary worktree on that default branch before syncing.
4. Sync the default branch with the remote using `git fetch` and a fast-forward `git pull`.
5. Derive a short kebab-case slug from the task.
6. Look for an existing linked worktree for `feat/<slug>`.
7. If a matching worktree exists and is clean, reuse it. Otherwise create a new branch and worktree:

```bash
git worktree add -b feat/<slug> ./<slug>-worktree
```

8. Switch into the linked worktree before editing.

## Safety Rules

- Never implement changes in the primary worktree.
- Use the primary worktree only to inspect the default branch, sync it, and create or reuse linked worktrees.
- If the current directory is already a linked worktree, move back to the repository root before syncing the default branch.
- If a matching worktree exists but has uncommitted changes, do not reuse it blindly. Create a new specific slug instead.

## Naming Rules

- Keep the slug short and descriptive.
- Use lowercase letters, digits, and hyphens only.
- Keep branch names in the form `feat/<slug>`.
- Keep worktree directories in the form `./<slug>-worktree`.

## Practical Checks

Use these commands as needed:

```bash
git worktree list
git branch --show-current
git symbolic-ref --short refs/remotes/origin/HEAD
git fetch origin
git pull --ff-only origin <default-branch>
git status --short --branch
```
