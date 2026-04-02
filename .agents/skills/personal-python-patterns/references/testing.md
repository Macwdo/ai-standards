# Python Testing And Validation Patterns

Use these rules for Python tests and lightweight validation unless the repo already uses a stronger local testing style.

## Read First

- Inspect the current test suite before adding new tests.
- Reuse existing helpers, fixtures, markers, factories, or naming patterns when they already exist.
- If the repo has no strong convention, default to `pytest`.

## Core Workflow

### 1. Start from behavior

- Write tests around the user-visible or caller-visible contract first.
- Assert return values, raised exceptions, and observable side effects.
- Name tests so the condition and outcome are obvious.

### 2. Keep setup visible

- Prefer small helpers and explicit fixtures over hidden setup chains.
- Keep data construction close to the test unless it is repeated.
- Mock only the true external boundary, not the logic under test.

### 3. Run the narrowest proof

- Run the smallest command that proves the change works.
- Prefer a focused `pytest` target, a single module test run, or the narrowest lint/type check that covers the edit.
- Expand validation only when the change affects shared infrastructure or broad behavior.

## Default Test Rules

- Give each test one clear responsibility.
- Prefer plain assertions over clever loops or generated cases unless parametrization materially helps.
- Use fixtures to share setup, not to hide critical behavior.
- Prefer helper functions with keyword-only arguments when test setup needs reuse.
- Keep monkeypatching and patching near the test that needs it.

```python
import pytest


def format_status(*, is_active: bool) -> str:
    """Return a human-readable status label."""
    return "active" if is_active else "inactive"


def test_format_status_returns_active_when_flag_is_true() -> None:
    """format_status returns active for enabled records."""
    assert format_status(is_active=True) == "active"


def test_format_status_returns_inactive_when_flag_is_false() -> None:
    """format_status returns inactive for disabled records."""
    assert format_status(is_active=False) == "inactive"
```

## Validation Defaults

- If the repo uses Ruff, MyPy, Pyright, pytest, or project-specific make targets, reuse them.
- If typing matters for the change, run the relevant type checker on the touched scope.
- If formatting matters, run the repo's formatter instead of hand-formatting around it.
- Do not claim confidence without running at least one relevant check when a check is available.

## Framework Composition

- For Django endpoint and model tests, compose with `$personal-django-patterns` or `$personal-django-tdd`.
- Keep this reference focused on Python-wide testing defaults that work in plain modules, services, CLIs, and workflow code.
