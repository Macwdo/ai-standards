---
name: prepare-worktree
description: Create a fresh git worktree and feature branch before implementation tasks. Use when starting coding work, bug fixes, refactors, tests, or any prompt that will modify files so the task begins in an isolated worktree.
---

# Prepare Worktree

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
