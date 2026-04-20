# Selector Patterns

Use these rules when adding or updating read-side query logic in this repo.

These defaults intentionally follow the HackSoft split between selectors for reads and services for writes.

## Read First

- Inspect the app's `selectors.py`, `services.py`, `models.py`, `views.py`, and `tests/`.
- Reuse the repo's existing query helpers, visibility rules, and queryset optimizations when they already exist.
- Keep selectors consistent with the app's current return shapes and error-handling style.

## Core Rules

- Selectors own read paths, filtering, query composition, and queryset optimization.
- Use keyword-only arguments unless the selector takes zero or one argument.
- Type annotate selector inputs and return values.
- Return the shape that best fits the caller: queryset, model instance, list, dict, or computed collection.
- Selectors may compose other selectors.
- Selectors do not mutate database state or trigger business side effects.
- Selectors may populate a cache on a read miss when that cache write is only a read optimization.

## Detail Selector Pattern

Use a selector for reusable read access to a single object or a scoped queryset.

```python
from __future__ import annotations

from apps.example.models import ExampleModel


def example_get(*, example_id, account) -> ExampleModel | None:
    return (
        ExampleModel.objects.select_related("account")
        .prefetch_related("tags")
        .filter(id=example_id, account=account)
        .first()
    )
```

## Cached Selector Pattern

Use a read-through cache in the selector when the same read path is hot and the repo already uses caching for similar lookups.

Prefer caching a read model or serialized payload instead of a live ORM instance unless the repo already caches model instances on purpose.

```python
from __future__ import annotations

from typing import TypedDict

from django.core.cache import cache

from apps.authentication.models import AppUser

USER_CACHE_TIMEOUT = 60 * 15


class CachedUser(TypedDict):
    id: str
    email: str
    full_name: str


def user_get_cached(*, user_id: str) -> CachedUser | None:
    cache_key = f"user:{user_id}"
    cached_user = cache.get(cache_key)
    if cached_user is not None:
        return cached_user

    user = (
        AppUser.objects.only("id", "email", "full_name")
        .filter(id=user_id)
        .first()
    )
    if user is None:
        return None

    cached_user = {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
    }
    cache.set(cache_key, cached_user, timeout=USER_CACHE_TIMEOUT)

    return cached_user
```

This keeps the selector responsible for:

- Checking the cache first
- Falling back to the database on a cache miss
- Writing the read result back into cache
- Returning the cached shape consistently to the caller

## List Selector Pattern

Keep filtering and optimization in the selector instead of scattering it across views.

```python
from __future__ import annotations

import django_filters

from apps.example.models import ExampleModel


class ExampleFilter(django_filters.FilterSet):
    class Meta:
        model = ExampleModel
        fields = ("status", "is_active")


def example_list(*, account, filters: dict | None = None):
    filters = filters or {}

    queryset = (
        ExampleModel.objects.filter(account=account)
        .select_related("owner")
        .prefetch_related("tags")
        .order_by("-created_at")
    )

    return ExampleFilter(filters, queryset).qs
```

## Query Optimization Rules

- Use `select_related()` for foreign keys and one-to-one relationships that would otherwise cause N+1 queries.
- Use `prefetch_related()` for many-to-many and reverse relationships.
- Keep heavy read-path annotations, filtering, and ordering logic in selectors.
- If a computed model property spans multiple relations or would cause N+1 queries during serialization, prefer a selector instead.

## Naming and Module Layout

- Prefer `<entity>_<action>` names such as `invoice_get`, `invoice_list`, or `invoice_get_visible_for`.
- Start with `selectors.py` when the app is small.
- Split into a `selectors/` package when the query surface grows by domain.
- Keep selector names easy to grep and map back to the resource they fetch.

## Selector Boundaries

- Services may call selectors to enforce read-side rules before mutating data.
- Endpoints may use selectors directly for read-only flows.
- Be consistent about missing-object behavior: return `None`, return a queryset for endpoint-level `get_object_or_404`, or raise a repo-standard exception.
- Do not hide writes, background tasks, emails, or other side effects in selectors.
