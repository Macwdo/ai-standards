---
name: cleanup-worktrees
description: Audit and clean up git worktrees from any linked worktree or repository root. Use when Codex needs to inspect stale worktrees, remove linked worktree directories, clean up unmerged feature worktrees while preserving branches, prune broken worktree metadata, or safely decide which worktrees are merged, dirty, or detached before deletion.
---

# Cleanup Worktrees

Audit first, then remove. Default to preserving branches and skipping dirty worktrees unless the user explicitly asks for a more aggressive cleanup.

## Workflow

1. Resolve the repository root from the current directory.
2. Run `scripts/audit_worktrees.py` to identify:
   - the default base branch
   - every linked worktree path and branch
   - whether each branch is merged into the base branch
   - whether the worktree has local modifications
   - the recommended action
3. Summarize the findings before any destructive step.
4. Run `scripts/cleanup_worktrees.py` only after the audit confirms the intended targets.
5. Report what was removed, what was skipped, and whether any branches were preserved.

## Commands

Preview the current repository:

```bash
python3 /home/macwdo/Codes/ai-standards/.agents/skills/cleanup-worktrees/scripts/audit_worktrees.py
```

Preview unmerged linked worktrees that could be removed while keeping their branches:

```bash
python3 /home/macwdo/Codes/ai-standards/.agents/skills/cleanup-worktrees/scripts/cleanup_worktrees.py --mode unmerged
```

Execute that cleanup:

```bash
python3 /home/macwdo/Codes/ai-standards/.agents/skills/cleanup-worktrees/scripts/cleanup_worktrees.py --mode unmerged --execute
```

Clean only selected branches:

```bash
python3 /home/macwdo/Codes/ai-standards/.agents/skills/cleanup-worktrees/scripts/cleanup_worktrees.py --mode all-non-main --only feat/example --only feat/other --execute
```

Remove merged worktrees and delete their branches too:

```bash
python3 /home/macwdo/Codes/ai-standards/.agents/skills/cleanup-worktrees/scripts/cleanup_worktrees.py --mode merged --delete-branch --execute
```

## Safety Rules

- Keep the main worktree.
- Skip detached worktrees unless the user explicitly asks for manual cleanup.
- Skip dirty worktrees unless the user explicitly asks to force-remove them with `--include-dirty`.
- Preserve branches by default. This is the right mode for "clean up unmerged worktrees".
- Delete branches only when the user explicitly asks for `--delete-branch`.
- Refuse to delete unmerged branches unless the user explicitly asks for both `--delete-branch` and `--allow-delete-unmerged-branch`.
- Run the audit again after a destructive cleanup only if the user needs confirmation that the repo is clean.

## Interpreting Results

- `remove-worktree-keep-branch`: safe candidate for cleaning an unmerged linked worktree without losing the branch.
- `remove-worktree-and-branch`: merged branch; the linked worktree can be removed and the branch can optionally be deleted.
- `skip-dirty-*`: do not remove unless the user wants to force cleanup.
- `manual-review-detached`: inspect manually before removing.

## Example Requests

- "Use `$cleanup-worktrees` to clean up every unmerged worktree but keep the branches."
- "Audit this repo's worktrees and tell me which ones are already merged."
- "Remove merged worktrees and delete the local branches too."
