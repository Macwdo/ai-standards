# Python Implementation Patterns

Use these defaults when writing or refactoring Python code unless the repo already establishes a stronger local convention.

## Read First

- Inspect the target file and nearby modules before introducing a new pattern.
- Reuse the repo's package layout, import grouping, naming, and error handling when they already exist.
- Keep framework code at the edge and plain Python in the middle.

## Function-First Rule

- Prefer plain functions for services, transformations, orchestration helpers, and utilities.
- Introduce a class only when the code truly needs durable state, a protocol boundary, or a cohesive object lifecycle.
- Keep modules small enough that one main responsibility is obvious.

## Signatures and Typing

- Add type hints to public functions, methods, return values, and important local data structures.
- Prefer concrete types such as `list[str]`, `dict[str, Any]`, `Path`, or `TypedDict` over vague placeholders.
- Use keyword-only arguments for service-style functions, helpers, and orchestration entry points when that improves clarity.
- Use `TypedDict`, `dataclass`, or small domain types when a dictionary would otherwise become ambiguous.

```python
from __future__ import annotations

from pathlib import Path
from typing import TypedDict


class ReportSummary(TypedDict):
    path: Path
    line_count: int


def summarize_report(*, path: Path) -> ReportSummary:
    """Return simple metadata for a report file."""
    line_count = len(path.read_text().splitlines())
    return {"path": path, "line_count": line_count}
```

## Boundaries and Dependencies

- Pass external clients, repositories, and configurable collaborators into functions instead of constructing them inside business logic.
- Keep I/O, network calls, framework adapters, and environment access at module boundaries.
- Keep the core logic testable without booting the framework or patching module globals.

```python
from collections.abc import Callable


def build_invoice_message(
    *,
    customer_name: str,
    total_cents: int,
    format_currency: Callable[[int], str],
) -> str:
    """Build a customer-facing invoice summary."""
    return f"{customer_name}: {format_currency(total_cents)}"
```

## State and Mutation

- Prefer returning new values over mutating shared state in place.
- If a function updates state, make the side effect explicit in the name and signature.
- Keep hidden global caches, singletons, and mutable default arguments out of normal application code.

## Errors

- Raise explicit exceptions with human-readable messages.
- Do not swallow exceptions just to keep control flow moving.
- Translate low-level exceptions at boundaries when the caller needs a more useful domain error.

## Module Shape

- Start with the smallest useful module.
- Keep public entry points near the top and helpers below them.
- Extract a new file when a module mixes unrelated responsibilities or becomes hard to scan.
- Add short docstrings where they clarify a public API or a non-obvious rule.

## Framework Composition

- For Django models, endpoints, services, and tests, compose with `$personal-django-patterns`.
- For Django TDD flow, compose with `$personal-django-tdd`.
- For LangGraph workflows, compose with `$personal-langgraph-patterns`.
- Keep this reference focused on shared Python defaults rather than framework details.
