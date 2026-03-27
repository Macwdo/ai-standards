# New Service

Create a new service function or module: $ARGUMENTS

## Service conventions

Services are plain Python functions — never classes. They live in `apps/<app>/services.py`.

### Function signature

Always use keyword-only arguments (`*`):

```python
from apps.<app>.models import <Model>


def create_<resource>(
    *,
    field_a: str,
    field_b: int,
) -> <Model>:
    instance = <Model>.objects.create(
        field_a=field_a,
        field_b=field_b,
    )
    return instance


def update_<resource>(
    *,
    instance: <Model>,
    field_a: str | None = None,
) -> <Model>:
    if field_a is not None:
        instance.field_a = field_a
    instance.full_clean()
    instance.save()
    return instance


def delete_<resource>(*, instance: <Model>) -> None:
    instance.delete()
```

### Service that coordinates multiple apps

```python
from django.db import transaction

from apps.<app_a> import services as <app_a>_services
from apps.<app_b> import services as <app_b>_services
from apps.<app_a>.models import <ModelA>


@transaction.atomic
def create_<resource>_with_<related>(
    *,
    field: str,
    related_field: str,
) -> <ModelA>:
    instance = <app_a>_services.create_<resource>(field=field)
    <app_b>_services.create_<related>(instance=instance, related_field=related_field)
    return instance
```

### Service with external dependency (S3, OpenAI, etc.)

Pass dependencies as arguments — never instantiate them inside the function:

```python
from mypy_boto3_s3 import S3Client


def upload_file(
    *,
    file_path: str,
    s3_client: S3Client,
    bucket_name: str,
) -> dict:
    # ...
    pass
```

Callers obtain the dependency via `apps.common.dependencies`:
```python
from apps.common import dependencies as common_dependencies

bucket_name, s3_client = common_dependencies.get_application_default_s3()
```

### Raising exceptions

Use exceptions from `apps.common.exceptions`:

```python
from apps.common.exceptions import BussinesLogicException


def do_something(*, instance) -> None:
    if not instance.is_valid:
        raise BussinesLogicException("Custom message")
```

Add new exception types to `apps/common/exceptions.py` when needed:
```python
class <Name>Exception(BussinesLogicException):
    status_code = status.HTTP_<CODE>
    default_detail = "<human readable message>"
    default_code = "<snake_case_code>"
```

## Rules

- Services are **pure functions** — no class-based services
- All args are **keyword-only** (`def fn(*, ...)`)
- Services return the created/updated model instance or a typed value
- No request/response objects inside services
- No `logger` unless there's a genuine error scenario to log
- Call `full_clean()` before `save()` on new model instances
- Use `@transaction.atomic` on functions that write to multiple tables
