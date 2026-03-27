# Codex notify hook with hookify

This example uses Codex's `notify` command hook and implements the handler with the `hookify` npm package.

## What Codex supports today

Codex currently documents a `notify = [...]` config entry that spawns an external command after an agent turn completes. Codex appends a JSON payload as the last argv item.

Example payload shape used by current Codex builds:

```json
{
  "type": "agent-turn-complete",
  "thread-id": "thread-123",
  "turn-id": "turn-456",
  "cwd": "/tmp/project",
  "client": "codex-tui",
  "input-messages": ["Add a hook example"],
  "last-assistant-message": "Implemented the example hook."
}
```

## Install

```bash
cd examples/codex-notify-hookify
npm install
```

## Configure Codex

Update `~/.codex/config.toml` with the sample in `config.toml.example`.

Important: use an absolute path because Codex stores `notify` as an argv array, not a shell command string.

## Test locally

```bash
cd examples/codex-notify-hookify
npm run test:sample
```

The hook writes:

- `output/notify.log`
- `output/last-summary.txt`

## Why hookify is useful here

`hookify` lets the script define middleware around the Codex event:

- `pre("agent-turn-complete", ...)` validates and enriches the payload
- `handle(...)` performs the main hook action
- `post("agent-turn-complete", ...)` writes a simple summary artifact
