# AI Standards

This repository is the working home for my reusable skills and subagents for both Codex and OpenCode.

I use it to keep workflows, personal coding conventions, and specialist agent setups in one place so I can install them globally on a machine and reuse them across sessions.

## What lives here

- `.agents/skills/` contains reusable skills.
- `.agents/subagents/` contains installable specialist agents.
- `skills-lock.json` tracks imported skill sources.

The detailed naming rules live in:

- `.agents/skills/README.md`
- `.agents/subagents/README.md`

## Install Everything

Run the unified installer from the repository root:

```bash
python3 scripts/install-assets.py
```

It will ask:

- which CLI you are using: `Codex` or `OpenCode`
- whether to install `skills`, `agents`, or `both`
- whether to overwrite existing installed copies

You can also run it non-interactively:

```bash
python3 scripts/install-assets.py --cli codex --assets both --overwrite
```

```bash
python3 scripts/install-assets.py --cli opencode --assets both --overwrite
```

## Global Install Locations

Codex installs into:

- `${CODEX_HOME:-~/.codex}/skills`
- `${CODEX_HOME:-~/.codex}/agents`
- `${CODEX_HOME:-~/.codex}/config.toml`

OpenCode installs into:

- `${OPENCODE_CONFIG_DIR:-~/.config/opencode}/skills`
- `${OPENCODE_CONFIG_DIR:-~/.config/opencode}/agents`
- `${OPENCODE_CONFIG_DIR:-~/.config/opencode}/opencode.json`

The installers back up the global config file before rewriting it.

## Targeted Installers

Install only skills:

```bash
python3 scripts/install-all-skills.py --cli codex --overwrite
```

```bash
python3 scripts/install-all-skills.py --cli opencode --overwrite
```

Bootstrap Codex with both skills and agents:

```bash
python3 scripts/bootstrap-codex.py --overwrite
```

## Repo Layout

Every skill should live in its own directory and expose `SKILL.md`:

```text
.agents/skills/<skill-name>/SKILL.md
```

Every subagent should live in its own directory and expose:

```text
.agents/subagents/<agent-name>/AGENT.md
.agents/subagents/<agent-name>/config.toml
```

`AGENT.md` is the shared instruction source.

`config.toml` holds the install metadata used to render Codex TOML agents and OpenCode markdown agents.

Optional UI metadata may be added under:

```text
.agents/subagents/<agent-name>/agents/openai.yaml
```

## How I use this repo

This is a maintenance workspace, not a product app. The normal loop is:

1. Add a new skill or subagent when I notice a workflow I repeat often.
2. Update an existing skill or subagent when my standards, tools, or preferred prompts change.
3. Install the repo globally on a machine so Codex or OpenCode can reuse those workflows and specialist roles.

## Typical workflow

### Add a skill

1. Create a new directory under `.agents/skills/`.
2. Add a `SKILL.md` file with the workflow, rules, and examples.
3. Keep the name short, descriptive, and aligned with the existing naming conventions.

### Add a subagent

1. Create a new directory under `.agents/subagents/`.
2. Add an `AGENT.md` file with the shared specialist instructions.
3. Add a `config.toml` file with install metadata.
4. Add optional UI metadata under `agents/openai.yaml` when needed.

### Use a skill

Mention the skill naturally so the active CLI can load and use it.

Examples:

```text
Use the start-work skill to create a fresh worktree for this bug fix.
```

```text
Use personal-django-tdd to add DRF endpoint tests with helper-backed fixtures.
```

### Use a subagent

After installing the repo globally, ask Codex or OpenCode to use one of the installed agents.

Examples:

```text
Use the code-reviewer subagent to review these changes and return findings first.
```

```text
Use the agent-tester subagent to start this linked worktree through portless and verify the login flow.
```

## Goal

The point of this repo is consistency. Instead of re-explaining my preferences on every task, I can encode them once as skills and subagents, keep improving them, and install them globally for Codex or OpenCode reuse.
