# Testing Patterns

Use these rules when adding or updating Django tests in this repo.

## Read First

- Inspect the app's `tests/`, `helpers.py`, and `conftest.py` before adding setup code.
- Reuse existing helper names, auth fixtures, route naming, and assertion style.
- If setup is missing, add or extend a helper instead of building one-off setup inline.

## Core Workflow

### 1. RED

- Start from the user-visible behavior or API contract.
- Use `reverse()` with the real route name.
- Give every test a one-line docstring.

### 2. GREEN

- Make the smallest production change that satisfies the behavior.
- Assert status code, response body, and persisted database state.
- For list endpoints, assert the paginated response shape.

### 3. REFACTOR

- Move repeated setup into `tests/helpers.py`.
- Wrap helpers in fixtures only when it improves readability.
- Keep setup visible; do not hide important ORM state inside opaque fixtures.

## Naming Rule

Always follow:

```text
test_<resource>_<action>_<condition>_<expected_result>
```

## Default Authenticated Pattern

```python
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.authentication.models import AppUser
from apps.example.models import ExampleModel
from apps.example.tests import helpers


@pytest.mark.django_db
def test_example_create_returns_201_when_valid_data(
    api_client_with_common_user: tuple[APIClient, AppUser],
) -> None:
    """POST /example creates a record for valid input."""
    api_client, user = api_client_with_common_user

    url = reverse("api:example:example-list")
    response = api_client.post(url, {"field": "value"})

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "id": response.json()["id"],
        "field": "value",
        "created_at": response.json()["created_at"],
        "updated_at": response.json()["updated_at"],
    }

    ExampleModel.objects.get(id=response.json()["id"], field="value")
```

## Helper-First Rule

- Build state through helpers or the public API whenever practical.
- Helpers should use keyword-only arguments and sensible defaults.
- Expose reusable setup through helpers first and fixtures second.

```python
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.example.models import ExampleModel

COMMON_FIELD = "default-value"


def create_example(
    *,
    api_client: APIClient,
    field: str = COMMON_FIELD,
) -> ExampleModel:
    """Create an example through the API and return the stored model."""
    url = reverse("api:example:example-list")
    response = api_client.post(url, {"field": field})

    assert response.status_code == status.HTTP_201_CREATED
    return ExampleModel.objects.get(id=response.json()["id"])
```

## DRF Test Rules

- Use `@pytest.mark.django_db` on tests that touch the database.
- Use `reverse()`, never hardcoded URLs.
- Assert both HTTP status and response body.
- For mutations, assert the resulting database state.
- Mock external services at the module where they are used.

For list endpoints, assert:

```python
assert response.json() == {
    "next": None,
    "previous": None,
    "results": [...],
}
```

## Forbidden Patterns

- Do not use `factory_boy`.
- Do not use model factories of any kind.
- Do not use Django fixture files.
- Do not hardcode URLs.
- Do not skip response-body assertions on API tests.
- Do not hide important setup in opaque fixtures when a helper would be clearer.

Expected shared fixtures usually include:

- `api_client`
- `common_user`
- `api_client_with_common_user`
