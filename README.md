# AI Standards

This repository is the working home for my Codex skills and subagents.

I use it to keep reusable workflows, personal coding conventions, and specialist agent setups in one place so I can come back, refine them, and use them in future sessions without rebuilding the same context each time.

## What lives here

- `.agents/skills/` contains reusable skills, including the `personal-agent-tester` testing workflow.
- `.agents/subagents/` contains any remaining specialist agent personas that should not be modeled as skills.
- `skills-lock.json` tracks installed skill sources.

The detailed naming rules already live in:

- `.agents/skills/README.md`
- `.agents/subagents/README.md`

## Bootstrap Codex On A New PC

Run the bootstrap script from the repository root:

```bash
python3 scripts/bootstrap-codex.py
```

By default it:

- installs every directory in `.agents/skills/` that contains `SKILL.md` into `${CODEX_HOME:-~/.codex}/skills`
- removes the old installed `personal-agent-test` skill if it still exists
- derives the global `tester` role instructions from `.agents/skills/personal-agent-tester/SKILL.md`
- installs the global `tester` subagent role into `${CODEX_HOME:-~/.codex}/agents/tester.toml`
- updates `${CODEX_HOME:-~/.codex}/config.toml` to enable multi-agent mode and register the `tester` role

The bootstrap script creates a backup of `config.toml` before rewriting it.

Use `--overwrite` to replace already installed copies:

```bash
python3 scripts/bootstrap-codex.py --overwrite
```

## Install Only Local Skills

If you only want the repo skills without the global tester role, use the narrower installer:

```bash
python3 scripts/install-all-skills.py
```

## How I use this repo

This is a maintenance workspace, not a product app. The normal loop is:

1. Add a new skill or subagent when I notice a workflow I repeat often.
2. Update an existing skill or subagent when my standards, tools, or preferred prompts change.
3. Bootstrap the repo onto a machine so Codex can reuse those workflows and specialist roles across sessions.

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

### Add a subagent

1. Create a new directory under `.agents/subagents/`.
2. Add an `AGENT.md` file with the specialist role instructions.
3. Add optional UI metadata under `agents/openai.yaml`.

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

### Use the tester subagent from Codex

After bootstrapping, ask Codex naturally to spawn or use the global `tester` role. Its instructions are sourced from `.agents/skills/personal-agent-tester/SKILL.md`.

Examples:

```text
Spawn the tester subagent to run pnpm dev in this linked worktree and verify the login flow.
```

```text
Use the tester role to start this worktree through portless and check that the settings form saves.
```

Use `/agent` to inspect or continue work in the spawned tester thread.

## Goal

The point of this repo is consistency. Instead of re-explaining my preferences on every task, I can encode them once as skills and subagents, keep improving them, and let Codex reuse them across projects and sessions.
