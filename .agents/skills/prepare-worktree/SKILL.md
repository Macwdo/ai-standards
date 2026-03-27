---
name: prepare-worktree
description: Create a fresh git worktree and feature branch without performing base-branch sync or pull steps. Use only when the user explicitly asks for `$prepare-worktree` or specifically requests direct worktree creation as a standalone action.
---

# Prepare Worktree

Use this skill only for explicit `$prepare-worktree` requests. For normal start-of-task setup that should return to the base branch and pull first, use `start-work` instead.

## Workflow

Before starting implementation:

1. Derive a short kebab-case slug from the task, using the implementation goal as the basis.
2. Create a branch named `feat/<slug>`.
3. Create a worktree directory named `./<slug>-worktree`.
4. Run:

```bash
git worktree add -b feat/<slug> ./<slug>-worktree
```

## Naming Rules

- Keep the slug short and descriptive.
- Use lowercase letters, digits, and hyphens only.
- Prefer task words that match the requested implementation.
- If the directory or branch already exists, pick a new slug that stays specific to the task.

## After Setup

- Switch into the new worktree before editing.
- Keep all implementation changes inside that worktree.
