---
name: personal-agent-test
description: Manually test a local implementation from a linked git worktree by starting the app through portless and verifying behavior with agent-browser. Use when the user wants the agent to test the current worktree implementation, not guess localhost ports, and stop if the current directory is not a linked worktree.
---

# Personal Agent Test

Manually test the current implementation from this linked worktree: $ARGUMENTS

## When to Use

Use this skill when:

- the user wants the agent to test a local implementation manually
- the implementation lives in the current linked git worktree
- the app should be started through `portless`
- the UI or browser flow should be verified with `agent-browser`

Do not use this skill for remote staging or production testing.

## Preconditions

Before doing anything else:

1. Run `git rev-parse --git-dir`.
2. Confirm the result contains `/worktrees/`.
3. If it returns plain `.git` or anything that is not a linked worktree path, stop and tell the user:

```text
This skill only runs from a linked git worktree. Create one with $start-work or $prepare-worktree, then rerun $personal-agent-test.
```

Also verify the required CLIs exist:

- `portless`
- `agent-browser`

If either is missing, stop and report the missing tool instead of improvising a different workflow.

## Required Inputs

The request should provide:

- what behavior or flow to test
- the dev command to start the app

Optional:

- an explicit portless app name if the default inferred name is not desired
- credentials or setup details needed for the test flow

If the dev command is missing, inspect the repo for an obvious `dev` script. Use it only when the choice is unambiguous. Otherwise stop and ask the user for the startup command.

## Workflow

1. Confirm the current directory is a linked worktree.
2. Inspect the repo for the startup command only if the user did not provide one.
3. Inspect local env and config for values that may need to change when the app runs through `portless`.
   - check `.env`, `.env.local`, `.env.development`, and similar local config files when they exist
   - look for URL-sensitive settings such as CORS origins, frontend URLs, backend API URLs, callback URLs, redirect URLs, allowed hosts, and base URLs
   - if the current settings still point at stale localhost ports or non-portless origins, update them before testing
4. Start the app through `portless` from the current worktree:
   - prefer `portless run <dev-command>`
   - if the user provided an explicit app name, use `portless <name> -- <dev-command>`
5. Discover the routed URL from `portless`:
   - use `portless get <name>` when the name is explicit
   - otherwise use `portless list` and select the route created for the current worktree
6. Never guess `localhost` ports. Always use the routed `.localhost` URL returned by `portless`.
7. Re-check any URL-sensitive env values against the actual routed portless URL if the app or related services depend on explicit origins.
8. Open the routed URL with `agent-browser`.
9. Wait for the app to settle with `agent-browser wait --load networkidle` or a more specific wait when needed.
10. Take a baseline `agent-browser snapshot -i`.
11. Execute the requested scenario using the normal loop:
   - snapshot
   - interact
   - wait
   - re-snapshot
   - verify
12. Verify outcomes with explicit checks:
    - URL changed as expected
    - expected text or controls appear
    - unexpected errors or blockers do not appear
    - use `agent-browser diff snapshot` when it helps confirm the UI changed after an action
13. Stop on the first real blocker. Do not keep clicking blindly after a failure.
14. If this run started the dev server, stop it before finishing unless the user asked to keep it running.

## Reporting Rules

Return a concise written summary that includes:

- linked worktree branch
- routed portless URL used for the test
- scenario that was tested
- pass or fail
- the first concrete blocker when it fails

Default to summary only. Screenshots, traces, or extra artifacts are optional and should be produced only when they materially help explain a failure.

## Failure Rules

Stop and tell the user when:

- the current directory is not a linked worktree
- no startup command is available
- local env or config still points at incompatible non-portless URLs and the test cannot run correctly
- `portless` fails to produce a routed URL
- the page never reaches a usable state
- the requested scenario cannot be completed with the available credentials or inputs

When stopping, report the exact failed step and the next action the user should take.

## Example Requests

- `Use $personal-agent-test to run pnpm dev in this worktree and verify the login flow works.`
- `Use $personal-agent-test to start the app through portless and test that the settings form saves successfully.`
- `Use $personal-agent-test to verify this worktree implementation manually with agent-browser and report pass/fail.`
