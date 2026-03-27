# New Model

Create a new Django model: $ARGUMENTS

## Model conventions

### Base class selection

| Scenario | Base classes |
|---|---|
| Standalone entity | `AppBaseModel` |
| Account-scoped entity | `AppBaseModel, AccountRelatedModel` |
| Junction/through table | `AppBaseModel` |

```python
# Standalone
class <Model>(AppBaseModel):
    ...

# Account-scoped (tenant isolation)
class <Model>(AppBaseModel, AccountRelatedModel):
    ...
```

### Standard field patterns

```python
from django.db import models

from apps.account.models import AccountRelatedModel
from apps.common.models import AppBaseModel, fmt_model_str


class <Model>(AppBaseModel, AccountRelatedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)

    # FK to other app — always use string reference to avoid circular imports
    related = models.ForeignKey(
        "other_app.OtherModel",
        on_delete=models.CASCADE,
        related_name="<model_name_plural>",
    )

    # Optional FK
    optional_ref = models.ForeignKey(
        "other_app.OtherModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="optional_<model_name_plural>",
    )

    def __str__(self) -> str:
        return fmt_model_str(self, fields=["id", "name"])

    class Meta:
        ordering = ["-created_at"]
```

### `__str__` — always use `fmt_model_str`

```python
from apps.common.models import fmt_model_str

def __str__(self) -> str:
    return fmt_model_str(self, fields=["id", "name"])

# Supports FK traversal:
def __str__(self) -> str:
    return fmt_model_str(self, fields=["user__email", "created_at"])
```

### Timestamps

`created_at` and `updated_at` are automatically provided by `AppBaseModel`. Never redeclare them.

### `AppConfig`

Each app's `apps.py` must declare `default_auto_field`:

```python
from django.apps import AppConfig


class <AppName>Config(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.<app_name>"
```

### Vector fields (AI embeddings)

```python
from pgvector.django import VectorField

embedding = VectorField(dimensions=1536)
```

### Properties

Use `@property` for derived, computed values that don't need to be stored:

```python
@property
def is_valid(self) -> bool:
    return bool(self.upload_finished_at)
```

### Admin registration

Every model must be registered in `admin.py` using the decorator pattern:

```python
from django.contrib import admin
from apps.<app>.models import <Model>


@admin.register(<Model>)
class <Model>Admin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ["-created_at"]
```

## After creating the model

```bash
make migrations
make migrate
```
