# AI Standards

This repository is the working home for my Codex skills.

I use it to keep reusable workflows, personal coding conventions, and specialist agent setups in one place so I can come back, refine them, and use them in future sessions without rebuilding the same context each time.

## What lives here

- `.agents/skills/` contains reusable skills.
- `.agents/subagents/` contains specialist agent personas that should not be modeled as skills.
- `skills-lock.json` tracks installed skill sources.

The detailed naming rules already live in:

- `.agents/skills/README.md`
- `.agents/subagents/README.md`

## Install all local skills

Run the installer from the repository root:

```bash
python3 scripts/install-all-skills.py
```

By default it installs every directory in `.agents/skills/` that contains `SKILL.md` into `${CODEX_HOME:-~/.codex}/skills`.

Use `--overwrite` to replace already installed copies:

```bash
python3 scripts/install-all-skills.py --overwrite
```

## How I use this repo

This is a maintenance workspace, not a product app. The normal loop is:

1. Add a new skill when I notice a workflow I repeat often.
2. Update an existing skill when my standards, tools, or preferred prompts change.
3. Use those skills from Codex so the agent can follow the same repeatable process every time.

## Skill conventions

Every skill should live in its own directory and expose `SKILL.md` as its entrypoint:

```text
.agents/skills/<skill-name>/SKILL.md
```

Generic or imported skills keep a regular name:

```text
.agents/skills/<skill-name>/SKILL.md
```

Personal conventions use the `personal-` prefix:

```text
.agents/skills/personal-<skill-name>/SKILL.md
```

Use a subagent instead of a skill when the capability is mainly a specialist persona rather than a reusable workflow:

```text
.agents/subagents/<agent-name>/AGENT.md
```

## Typical workflow

### Add a skill

1. Create a new directory under `.agents/skills/`.
2. Add a `SKILL.md` file with the workflow, rules, and examples.
3. Keep the name short, descriptive, and aligned with the existing naming conventions.

### Update a skill

1. Open the existing `SKILL.md`.
2. Tighten the instructions based on real usage.
3. Keep the skill focused on one repeatable job.

### Use a skill from Codex

Mention the skill in the request so Codex loads and follows it.

Examples:

```text
$start-work Add a new Django endpoint for invoice exports.
```

```text
$personal-test-writer Add tests for the new serializer behavior.
```

```text
$personal-django-tdd Add DRF endpoint tests using helper-backed fixtures and no factories.
```

```text
$save-finish Commit the docs changes, merge into the default branch, push, and remove the worktree.
```

## Goal

The point of this repo is consistency. Instead of re-explaining my preferences on every task, I can encode them once as skills, keep improving them, and let Codex reuse them across projects and sessions.
