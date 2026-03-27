---
name: personal-django-tdd
description: Django TDD workflow for this repo using pytest, DRF, helpers, and helper-backed fixtures. Ban factories and prefer API-driven setup.
---

# Personal Django TDD

Use this skill for Django test work in projects that follow this repo's helper-first testing conventions.

It combines a standard red-green-refactor workflow with the rules from `personal-test-writer`, then tightens them for Django and DRF projects.

## When to Use

- Adding tests for Django models, serializers, views, services, or DRF endpoints
- Extending an existing Django test suite with repo-style helpers
- Refactoring flaky or repetitive Django test setup into helpers
- Reviewing a Django test plan before implementation

## Core Workflow

### 1. Read the existing test shape first

- Inspect the app's `tests/`, `helpers.py`, and `conftest.py` before adding new setup code.
- Reuse existing helper names, auth fixtures, route naming, and response assertion style.
- If setup is missing, add or extend a helper instead of inventing one-off inline setup in the test body.

### 2. RED: write the failing test first

- Start from the user-visible behavior or API contract.
- Use `reverse()` and the real route name.
- Import the local `helpers` module when setup or seed data is needed.
- Give every test a one-line docstring.

### 3. GREEN: implement the smallest code change

- Make the test pass with the smallest production change possible.
- Keep assertions explicit for status code, response body, and DB state.
- For list endpoints, assert the paginated response shape.

### 4. REFACTOR: improve the setup, not just production code

- Move repeated setup into `tests/helpers.py`.
- Wrap helpers in fixtures only when it improves readability or reuse.
- Prefer one obvious helper path over many small fixtures with hidden side effects.

## Test Conventions

### File structure

```text
src/apps/<app>/tests/
├── __init__.py
├── helpers.py
└── test_<feature>.py
```

### Test function naming

Always follow:

```text
test_<resource>_<action>_<condition>_<expected_result>
```

Examples:

- `test_register_returns_201_when_valid_data`
- `test_register_returns_400_when_email_already_exists`
- `test_me_returns_401_when_not_authenticated`

### Default authenticated test pattern

```python
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.authentication.models import AppUser
from apps.<app>.models import <Model>
from apps.<app>.tests import helpers


@pytest.mark.django_db
def test_<resource>_<action>_<condition>_<expected_result>(
    api_client_with_common_user: tuple[APIClient, AppUser],
) -> None:
    """One-line docstring describing the behavior under test."""
    api_client, user = api_client_with_common_user

    url = reverse("api:<namespace>:<route-name>")
    response = api_client.post(url, {"field": "value"})

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "id": response.json()["id"],
        "field": "value",
        "created_at": response.json()["created_at"],
        "updated_at": response.json()["updated_at"],
    }

    <Model>.objects.get(id=response.json()["id"], field="value")
```

### Unauthenticated test pattern

```python
@pytest.mark.django_db
def test_<resource>_returns_401_when_not_authenticated(api_client: APIClient) -> None:
    """GET /resource returns 401 when no auth token is provided."""
    url = reverse("api:<namespace>:<route-name>")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

## Helpers and Fixtures

### Helper-first rule

- Build state through helpers or the public API whenever practical.
- Helpers should use keyword-only arguments and sensible defaults.
- If a test needs special setup, extend `helpers.py` instead of creating ad hoc ORM setup inline.

### Fixture rule

- Pytest fixtures are allowed and encouraged for shared setup.
- Fixtures should wrap helpers, authenticated clients, or other common setup utilities.
- Fixtures should not replace helpers with hidden ORM-heavy setup.

Example:

```python
import pytest

from apps.customers.tests import helpers


@pytest.fixture
def created_customer(api_client_with_common_user):
    """Create a customer through the shared helper."""
    api_client, _ = api_client_with_common_user
    return helpers.create_customer(api_client=api_client)
```

### Helpers pattern

```python
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.<app>.models import <Model>

COMMON_<RESOURCE>_FIELD = "default_value"


def create_<resource>(
    *,
    api_client: APIClient,
    field: str = COMMON_<RESOURCE>_FIELD,
) -> <Model>:
    """Create a resource through the API and return the stored model."""
    url = reverse("api:<namespace>:<route>-list")
    response = api_client.post(url, {"field": field})

    assert response.status_code == status.HTTP_201_CREATED
    return <Model>.objects.get(id=response.json()["id"])
```

## Django and DRF Rules

- Use `@pytest.mark.django_db` on every test that touches the database.
- Use `reverse()` and route names, never hardcoded URLs.
- Assert both HTTP status and response body.
- For mutations, assert the DB state after the call.
- For list endpoints, assert:

```python
assert response.json() == {
    "next": None,
    "previous": None,
    "results": [...],
}
```

- Mock external services at the module where they are used.

Example:

```python
from unittest.mock import MagicMock, patch
import pytest

from apps.<app>.services import <external_module>


@pytest.mark.django_db
@patch.object(<external_module>, "<method_name>")
def test_<action>_<condition>(
    mock_method: MagicMock,
    api_client_with_common_user,
):
    """One-line docstring."""
    mock_method.return_value = {"key": "value"}
```

## Forbidden Patterns

- Do not use `factory_boy`.
- Do not use model factories of any kind.
- Do not use Django fixture files (`.json`, `.yaml`, `.xml`).
- Do not hardcode URLs.
- Do not skip response-body assertions on API tests.
- Do not hide important setup inside opaque fixtures when a helper would make the flow clearer.

If helper-backed setup is missing, add the helper first, then write the test against that helper-backed flow.

## Available Fixtures

Global fixtures live in `src/apps/conftest.py`. App-level fixtures live in `src/apps/<app>/conftest.py`.

Expected shared fixtures:

- `api_client`
- `common_user`
- `api_client_with_common_user`

## Decision Rules

- If helpers exist, use them.
- If helpers do not exist, add them.
- If setup is reusable, expose it through helpers first and fixtures second.
- If a factory seems convenient, stop and create a helper instead.
