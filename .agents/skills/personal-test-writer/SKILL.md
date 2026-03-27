# Test Writer

Write tests for the described feature or endpoint: $ARGUMENTS

## Test conventions

### File structure

```
src/apps/<app>/tests/
├── __init__.py
├── helpers.py       ← setup utilities (create_*, get_*_token, etc.)
└── test_<feature>.py
```

### Test function naming

Always follow: `test_<resource>_<action>_<condition>_<expected_result>`

Examples:
- `test_register_returns_201_when_valid_data`
- `test_register_returns_400_when_email_already_exists`
- `test_customer_create_returns_201_with_nested_data`
- `test_me_returns_401_when_not_authenticated`

### Test structure

```python
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.authentication.models import AppUser
from apps.<app>.models import <Model>
from apps.<app>.tests import helpers


@pytest.mark.django_db
def test_<resource>_<action>_<condition>(
    api_client_with_common_user: tuple[APIClient, AppUser],
) -> None:
    """One-line docstring: what this test validates."""
    api_client, user = api_client_with_common_user

    url = reverse("api:<namespace>:<route-name>")
    data = {...}
    response = api_client.post(url, data)

    # Assert HTTP response
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "id": response.json()["id"],
        "field": "value",
        "created_at": response.json()["created_at"],
        "updated_at": response.json()["updated_at"],
    }

    # Assert DB state
    <Model>.objects.get(id=response.json()["id"], field="value")
```

### Unauthenticated test

```python
@pytest.mark.django_db
def test_<resource>_returns_401_when_not_authenticated(api_client: APIClient) -> None:
    """GET /resource returns 401 when no auth token is provided."""
    url = reverse("api:<namespace>:<route>")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

### Mocking external services

```python
from unittest.mock import MagicMock, patch
from apps.<app>.services import <external_module>


@pytest.mark.django_db
@patch.object(<external_module>, "<method_name>")
def test_<action>_when_<condition>(
    mock_method: MagicMock,
    api_client_with_common_user: tuple[APIClient, AppUser],
):
    """Description."""
    mock_method.return_value = {"key": "value"}

    api_client, _ = api_client_with_common_user
    # ...
```

### Helpers pattern

```python
# tests/helpers.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.<app>.models import <Model>

COMMON_<RESOURCE>_FIELD = "default_value"


def create_<resource>(
    *,
    api_client: APIClient,
    field: str = COMMON_<RESOURCE>_FIELD,
    # other fields with defaults...
) -> <Model>:
    """Creates a <resource> via the API and returns the instance."""
    data = {"field": field}
    url = reverse("api:<namespace>:<route>-list")
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED
    return <Model>.objects.get(id=response.json()["id"])
```

### Fixtures (conftest.py)

Global fixtures live in `src/apps/conftest.py`. App-level fixtures in `src/apps/<app>/conftest.py`.

Available fixtures:
- `api_client: APIClient` — unauthenticated client
- `common_user: AppUser` — registered user
- `api_client_with_common_user: tuple[APIClient, AppUser]` — authenticated client + user

### Pagination response shape

When testing list endpoints:
```python
assert response.json() == {
    "next": None,
    "previous": None,
    "results": [...],
}
```

## Rules

- Every test must have a one-line docstring
- Always assert both HTTP status AND response body
- For mutations, always assert DB state after the call
- Use `reverse()` — never hardcode URLs
- Use `@pytest.mark.django_db` on every test that touches the DB
- Use keyword-only args (`*`) in helper functions
- Helper defaults should cover the most common case
- Never use Django ORM fixtures (`.json`/`.yaml`) — build state via helpers or API
- Mock at the module level where the function is *used*, not where it's *defined*
