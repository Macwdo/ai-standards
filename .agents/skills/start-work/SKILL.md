---
name: start-work
description: Sync the repository to the latest remote base branch and start implementation in a fresh git worktree. Use when beginning coding work, bug fixes, refactors, or tests and Codex should first return to the repo base branch, pull from origin, then create and switch into a new feature worktree.
---

# Start Work

Prepare the repository for implementation by syncing the base branch first, then creating an isolated worktree for the task.

## Workflow

Before editing files:

1. Check `git status --short`.
2. Stop if tracked changes would make branch switching or pulling unsafe. Do not stash, reset, or clean up automatically.
3. Resolve the base branch:
   - Prefer `origin/HEAD`.
   - Use the branch it points to.
   - Fall back to `master`, then `main`, only when `origin/HEAD` is unavailable.
4. Switch to the base branch if needed.
5. Pull the latest changes from `origin` for that base branch.
6. Derive a short kebab-case slug from the task.
7. Create a branch named `feat/<slug>`.
8. Create a worktree directory named `./<slug>-worktree`.
9. Run:

```bash
git worktree add -b feat/<slug> ./<slug>-worktree
```

10. Switch into the new worktree before implementation.

## Naming Rules

- Keep the slug short and descriptive.
- Use lowercase letters, digits, and hyphens only.
- Prefer task words that match the requested implementation.
- If the directory or branch already exists, pick a new slug that stays specific to the task.

## Guardrails

- Keep the sync step on the base branch, not on an existing feature branch.
- Do not create the worktree until the pull succeeds.
- If the repository is dirty or branch detection is ambiguous, stop and report the blocker.
- Keep all implementation changes inside the new worktree.
