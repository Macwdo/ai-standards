# Service Patterns

Use these rules when adding or updating write-side business logic in this repo.

These defaults intentionally follow the HackSoft split between services for writes and selectors for reads.

## Read First

- Inspect the app's `services.py`, `selectors.py`, `models.py`, `tasks.py`, and `tests/`.
- Match the app's current naming, import style, transaction boundaries, and file layout before introducing new structure.
- If the repo already uses a `services/` package or class-based flow services, follow that shape.

## Core Rules

- Services own business rules, state changes, and side effects.
- Prefer function-based services by default.
- Use keyword-only arguments unless the service takes zero or one argument.
- Type annotate service inputs and return values.
- Keep service APIs explicit and easy to test.
- Call selectors for read-heavy checks or visibility queries instead of duplicating fetch logic.
- Do not hide write-side business logic in views, serializers, managers, querysets, model `save()`, or signals.

## Function-Based Service Pattern

Use a plain function for most mutations.

```python
from __future__ import annotations

from django.db import transaction

from apps.example.models import ExampleModel
from apps.example.tasks import example_created as example_created_task


@transaction.atomic
def example_create(*, account, name: str) -> ExampleModel:
    example = ExampleModel(account=account, name=name)
    example.full_clean()
    example.save()

    transaction.on_commit(
        lambda: example_created_task.delay(example_id=example.id)
    )

    return example
```

## Validation and Transactions

- Call `full_clean()` before `save()` when the service owns persistence for new or materially changed models.
- Use `@transaction.atomic` when the service writes multiple rows, enforces invariants, or coordinates related mutations.
- Keep transaction boundaries in the service layer instead of the serializer layer.
- Use `transaction.on_commit()` for side effects that should only happen after the database commit succeeds.

## Class-Based Flow Services

Use a class only when the service represents a multi-step flow or needs a small namespace around shared dependencies.

```python
from __future__ import annotations

from django.db import transaction

from apps.example.models import ExampleExport


class ExampleExportService:
    def __init__(self, *, account) -> None:
        self.account = account

    @transaction.atomic
    def start(self, *, name: str) -> ExampleExport:
        export = ExampleExport(account=self.account, name=name, status="pending")
        export.full_clean()
        export.save()
        return export

    @transaction.atomic
    def finish(self, *, export: ExampleExport) -> ExampleExport:
        export.status = "finished"
        export.full_clean()
        export.save()
        return export
```

## Naming and Module Layout

- Prefer `<entity>_<action>` names such as `invoice_create`, `invoice_send`, or `invoice_cancel`.
- Start with `services.py` when the app is small.
- Split into a `services/` package when the app grows multiple service domains.
- Re-export from `services/__init__.py` only when it improves imports and matches the repo's existing style.

## Service Boundaries

- Services may call selectors, model methods, external clients, and async tasks.
- Services may return model instances, query-independent DTO-like dicts, or primitives when that makes the call site simpler.
- If a serializer or endpoint starts carrying branching business rules, move that logic into a service.
- If a service becomes read-heavy and stops mutating state, move the fetch logic into a selector instead.
