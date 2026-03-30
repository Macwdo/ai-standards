# Endpoint Patterns

Use these rules when adding or updating DRF endpoints in this repo.

## Read First

- Inspect the app's `views.py`, `serializers.py`, `services.py`, and `urls.py`.
- Match the app's current style before introducing a new API shape.
- Keep views thin and explicit.

## View Rules

- Validate request data with a serializer.
- Call a service for business logic.
- Return `Response(..., status=...)` explicitly.
- Do not put business logic in views or serializers.
- Use `raise_exception=True` with `is_valid()`.
- Use `@transaction.atomic` when the flow writes multiple rows or models.
- For public endpoints, set `permission_classes = []` and `authentication_classes = []`.

## APIView Pattern

Use an APIView when the endpoint is custom logic rather than standard resource CRUD.

```python
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from rest_framework import status
from rest_framework.response import Response

from apps.api.views import BaseAPIView
from apps.example import services
from apps.example.serializers import ExampleSerializerRequest

if TYPE_CHECKING:
    from rest_framework.request import Request

logger = logging.getLogger(__name__)


class ExampleAPIView(BaseAPIView):
    def post(self, request: Request) -> Response:
        serializer = ExampleSerializerRequest(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = services.do_example(**serializer.validated_data)

        return Response(result, status=status.HTTP_200_OK)
```

## ViewSet Action Pattern

Use a custom action when the behavior belongs on an existing resource.

```python
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response


@action(
    detail=False,
    methods=["post"],
    serializer_class=ExampleActionSerializer,
    url_path="example-action",
)
def example_action(self, request: Request) -> Response:
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    result = services.do_example(**serializer.validated_data)

    return Response(result, status=status.HTTP_200_OK)
```

## Serializer Rules

- Use plain `serializers.Serializer` classes for request payloads that are not simple model CRUD.
- Keep validation in serializers and business logic in services.
- Use model serializers for read responses or straightforward model binding.

```python
from rest_framework import serializers


class ExampleSerializerRequest(serializers.Serializer):
    field = serializers.CharField(required=True)

    def validate_field(self, value: str) -> str:
        return value

    def validate(self, attrs: dict) -> dict:
        return attrs
```

## Service Layer Rules

- Put multi-step writes and business rules in services.
- Keep service APIs explicit and easy to test.
- Prefer transaction boundaries around service flows that persist related changes.

## Supporting Django Guidance

Use the generic Django pattern only when it matches the repo:

- `select_related()` for foreign key access that would otherwise cause N+1 queries
- `prefetch_related()` for many-to-many and reverse relations
- custom QuerySets or managers for reusable query behavior

Do not import generic project-layout or settings boilerplate unless the task explicitly asks for it.
