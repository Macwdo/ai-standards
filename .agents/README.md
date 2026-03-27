# Agents Layout

Project agent assets live under `.agents/`.

## Skills

Reusable task workflows and conventions belong in `.agents/skills/`.

Each skill keeps the standard skill layout:

- `.agents/skills/<skill-name>/SKILL.md`

## Subagents

Dedicated specialist agents belong in `.agents/subagents/`.

Each subagent lives in its own directory and exposes `AGENT.md` as the prompt entrypoint:

- `.agents/subagents/<agent-name>/AGENT.md`

Optional UI or invocation metadata can live beside it, for example:

- `.agents/subagents/<agent-name>/agents/openai.yaml`
