---
name: personal-python-patterns
description: Apply my default Python implementation patterns across plain modules, services, CLIs, workflow code, helpers, and tests. Use when Codex needs one repo-first umbrella skill for writing or refactoring Python code with explicit typing, function-first design, dependency injection, visible boundaries, and behavior-focused validation before layering on framework-specific skills such as Django or LangGraph.
---

# Personal Python Patterns

Use this skill as the default umbrella for Python work before reaching for framework-specific rules.

Start from the repo's existing Python shape, then apply these defaults only where the repo does not already establish a stronger convention.

## Workflow

### 1. Read the local Python code first

- Inspect the target module, sibling modules, and nearby tests before changing anything.
- Reuse the repo's naming, import style, error model, and file layout when they already exist.
- If the repo conflicts with a generic Python best practice, follow the repo.

### 2. Pick the right layer

- Keep domain logic in plain Python functions or small typed modules.
- Keep framework glue, CLI parsing, HTTP adapters, and graph wiring thin.
- Pass dependencies in from the edge instead of constructing them deep inside core logic.

### 3. Load the relevant reference

- For module shape, typing, and dependency rules, read [references/implementation.md](references/implementation.md).
- For tests, helpers, and validation rules, read [references/testing.md](references/testing.md).
- For Django-specific work, also use `$personal-django-patterns` and `$personal-django-tdd`.
- For LangGraph-specific orchestration, also use `$personal-langgraph-patterns`.

### 4. Finish the change completely

- Add or update tests for the behavior you changed.
- Run the smallest validation that proves the code works.
- Keep the final code easy to extend without forcing framework details into core Python modules.

## Decision Rules

- Prefer typed functions and small modules over large stateful classes.
- Prefer explicit inputs and return values over hidden mutation.
- Prefer dependency injection over globals and inline client construction.
- Prefer visible test setup over magic fixtures or broad monkeypatching.
- Prefer composing with narrower personal skills instead of duplicating their rules here.

## References

- [references/implementation.md](references/implementation.md): module design, typing, dependency, and boundary defaults
- [references/testing.md](references/testing.md): behavior-focused tests, helper reuse, and validation defaults
