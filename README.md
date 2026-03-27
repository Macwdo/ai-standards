# AI Standards

This repository stores agent-facing standards and reusable workflow docs for local coding assistants.

## What lives here

- `.agents/skills/` contains reusable skills with a `SKILL.md` entrypoint.
- `.agents/subagents/` contains specialist agent personas and their docs.
- `.agents/README.md` is reserved for top-level agent guidance for this repository.

## Repository conventions

### Skills

Each skill lives in its own directory:

```text
.agents/skills/<skill-name>/SKILL.md
```

Generic workflows keep a regular name. Personal conventions use the `personal-` prefix.

### Subagents

Use subagents for specialist personas rather than repeatable workflows:

```text
.agents/subagents/<agent-name>/AGENT.md
```

## Current skills

- `cleanup-worktrees`
- `django-patterns`
- `personal-new-endpoint`
- `personal-new-model`
- `personal-new-service`
- `personal-test-writer`
- `prepare-worktree`
- `save-finish`

## Purpose

The goal of this repository is to keep coding workflows explicit, reusable, and easy to audit. Skills define procedures and conventions. Subagents define focused execution or review roles.
