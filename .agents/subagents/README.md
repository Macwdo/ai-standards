# Subagents Naming Convention

Use `.agents/subagents/` for specialist agent personas that should not be modeled as skills.

## Subagent layout

Every subagent must live in its own directory and expose `AGENT.md` as the entrypoint:

- `.agents/subagents/<agent-name>/AGENT.md`

Optional UI metadata may be added under:

- `.agents/subagents/<agent-name>/agents/openai.yaml`

## When to use a subagent

Use a subagent when the capability is primarily a specialist reviewer or executor persona rather than a reusable task workflow.

Use a skill when the capability is primarily procedural guidance, conventions, or a repeatable workflow.
