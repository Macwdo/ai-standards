---
name: django-tdd
description: Django testing strategies with pytest-django, TDD methodology, factory_boy, mocking, coverage, and testing Django REST Framework APIs.
origin: ECC
---

# Django Testing with TDD

Test-driven development for Django applications using pytest, factory_boy, and Django REST Framework.

## When to Activate

- Writing new Django applications
- Implementing Django REST Framework APIs
- Testing Django models, views, and serializers
- Setting up testing infrastructure for Django projects

## TDD Workflow for Django

### Red-Green-Refactor Cycle

```python
# Step 1: RED - Write failing test
def test_user_creation():
    user = User.objects.create_user(email="test@example.com", password="testpass123")
    assert user.email == "test@example.com"
    assert user.check_password("testpass123")
    assert not user.is_staff

# Step 2: GREEN - Make test pass
# Create User model or factory

# Step 3: REFACTOR - Improve while keeping tests green
```

## Setup

### pytest Configuration

```ini
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.test
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --reuse-db
    --nomigrations
    --cov=apps
    --cov-report=html
    --cov-report=term-missing
    --strict-markers
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
```

### conftest.py

```python
# tests/conftest.py
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(
        email="test@example.com",
        password="testpass123",
        username="testuser",
    )


@pytest.fixture
def api_client():
    """Return DRF API client."""
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def authenticated_api_client(api_client, user):
    """Return authenticated API client."""
    api_client.force_authenticate(user=user)
    return api_client
```

## Factory Boy

### Factory Setup

```python
# tests/factories.py
import factory
from factory import fuzzy
from django.contrib.auth import get_user_model
from apps.products.models import Product, Category

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for User model."""

    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Sequence(lambda n: f"user{n}")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")
    is_active = True


class CategoryFactory(factory.django.DjangoModelFactory):
    """Factory for Category model."""

    class Meta:
        model = Category

    name = factory.Faker("word")
    slug = factory.LazyAttribute(lambda obj: obj.name.lower())
    description = factory.Faker("text")


class ProductFactory(factory.django.DjangoModelFactory):
    """Factory for Product model."""

    class Meta:
        model = Product

    name = factory.Faker("sentence", nb_words=3)
    slug = factory.LazyAttribute(lambda obj: obj.name.lower().replace(" ", "-"))
    description = factory.Faker("text")
    price = fuzzy.FuzzyDecimal(10.00, 1000.00, 2)
    stock = fuzzy.FuzzyInteger(0, 100)
    is_active = True
    category = factory.SubFactory(CategoryFactory)
    created_by = factory.SubFactory(UserFactory)
```

### Using Factories

```python
# tests/test_models.py
from tests.factories import ProductFactory


def test_product_creation():
    """Test product creation using factory."""
    product = ProductFactory(price=100.00, stock=50)
    assert product.price == 100.00
    assert product.stock == 50
    assert product.is_active is True
```

## API Testing

```python
# tests/test_api.py
import pytest
from django.urls import reverse
from rest_framework import status

from tests.factories import ProductFactory


@pytest.mark.django_db
def test_product_list(authenticated_api_client):
    """Test product list endpoint."""
    ProductFactory.create_batch(3)

    url = reverse("product-list")
    response = authenticated_api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 3
```

## Coverage and Verification

```bash
pytest --cov=apps --cov-report=html --cov-report=term-missing --reuse-db
```

Coverage target:

- 80%+ overall coverage
- 100% on critical business logic

## Notes

- This is a generic imported skill.
- If the local project has stronger testing conventions, prefer the project-specific skill over this one.
