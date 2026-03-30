# Model Patterns

Use these rules when creating or updating Django models in this repo.

## Read First

- Inspect the app's existing `models.py`, `admin.py`, `apps.py`, and migrations before introducing new patterns.
- Reuse existing field names, related names, and model organization when possible.

## Base Classes

Choose the base class from the repo's existing conventions:

| Scenario | Base classes |
| --- | --- |
| Standalone entity | `AppBaseModel` |
| Account-scoped entity | `AppBaseModel, AccountRelatedModel` |
| Junction or through model | `AppBaseModel` |

```python
from apps.account.models import AccountRelatedModel
from apps.common.models import AppBaseModel


class ExampleModel(AppBaseModel, AccountRelatedModel):
    ...
```

## Field and Relationship Rules

- Use string references for cross-app relations to avoid circular imports.
- Use `blank=True, default=""` for optional text fields when that matches the app's style.
- Use `null=True, blank=True` for optional foreign keys that can be absent.
- Do not redeclare `created_at` or `updated_at`; they come from `AppBaseModel`.

```python
from django.db import models

from apps.account.models import AccountRelatedModel
from apps.common.models import AppBaseModel, fmt_model_str


class ExampleModel(AppBaseModel, AccountRelatedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    related = models.ForeignKey(
        "other_app.OtherModel",
        on_delete=models.CASCADE,
        related_name="examples",
    )
    optional_ref = models.ForeignKey(
        "other_app.OtherModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="optional_examples",
    )

    def __str__(self) -> str:
        return fmt_model_str(self, fields=["id", "name"])

    class Meta:
        ordering = ["-created_at"]
```

## `__str__` Rule

Always use `fmt_model_str`.

```python
from apps.common.models import fmt_model_str


def __str__(self) -> str:
    return fmt_model_str(self, fields=["id", "name"])
```

FK traversal is allowed when it improves readability:

```python
def __str__(self) -> str:
    return fmt_model_str(self, fields=["user__email", "created_at"])
```

## AppConfig Rule

Each app's `apps.py` should declare `default_auto_field`:

```python
from django.apps import AppConfig


class ExampleConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.example"
```

## Admin Rule

Register every model in `admin.py` with the decorator pattern.

```python
from django.contrib import admin

from apps.example.models import ExampleModel


@admin.register(ExampleModel)
class ExampleModelAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ["-created_at"]
```

## Properties and Specialized Fields

- Use `@property` for derived values that do not need storage.
- Use `VectorField` only when the app already uses pgvector or the task explicitly requires embeddings.

## Finish Model Changes

When the model changes, also consider:

- `admin.py`
- `apps.py` if missing repo-standard config
- migrations
- serializers, views, and services that expose the model
- tests covering the user-visible behavior

Run:

```bash
make migrations
make migrate
```
