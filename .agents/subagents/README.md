# Subagents Naming Convention

Use `.agents/subagents/` for specialist agent personas that should not be modeled as skills.

## Subagent layout

Every subagent must live in its own directory and expose `AGENT.md` as the shared instruction source:

- `.agents/subagents/<agent-name>/AGENT.md`

Every installable subagent should also define target-neutral install metadata in `config.toml`:

- `.agents/subagents/<agent-name>/config.toml`

Optional UI metadata may be added under:

- `.agents/subagents/<agent-name>/agents/openai.yaml`

`AGENT.md` should contain the reusable prompt body.

`config.toml` should contain the install metadata used to render Codex and OpenCode global agents.

## When to use a subagent

Use a subagent when the capability is primarily a specialist reviewer or executor persona rather than a reusable task workflow.

Use a skill when the capability is primarily procedural guidance, conventions, or a repeatable workflow.
