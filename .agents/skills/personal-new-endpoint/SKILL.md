---
name: personal-new-endpoint
description: Add a new API endpoint to an existing app using the project's APIView, ViewSet action, serializer, and service-layer patterns.
---

# New Endpoint

Add a new API endpoint to an existing app. Description: $ARGUMENTS

## Patterns to follow

### Simple APIView endpoint (non-resource, custom logic)

```python
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from rest_framework import status
from rest_framework.response import Response

from apps.api.views import BaseAPIView
from apps.<app_name> import services
from apps.<app_name>.serializers import <Request>SerializerRequest

if TYPE_CHECKING:
    from rest_framework.request import Request

logger = logging.getLogger(__name__)


class <Name>APIView(BaseAPIView):
    def post(self, request: Request) -> Response:
        serializer = <Request>SerializerRequest(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = services.<do_something>(**serializer.validated_data)

        return Response({"message": "..."}, status=status.HTTP_200_OK)
```

### ViewSet custom action

```python
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status


@action(
    detail=False,        # True if /resource/{pk}/action/
    methods=["post"],
    serializer_class=<ActionSerializer>,
    url_path="<action-path>",
)
def <action_name>(self, request: Request) -> Response:
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    result = services.<do_something>(**serializer.validated_data)

    return Response(result, status=status.HTTP_200_OK)
```

### Request serializer (no model binding)

```python
class <Name>SerializerRequest(serializers.Serializer):
    field = serializers.CharField(required=True)

    def validate_field(self, value: str) -> str:
        # per-field validation
        return value

    def validate(self, attrs: dict) -> dict:
        # cross-field validation
        return attrs
```

### Response serializer (model-bound, read-only)

```python
class <Name>SerializerResponse(serializers.ModelSerializer):
    class Meta:
        model = <Model>
        fields = [
            "id",
            "field_a",
            "field_b",
            "created_at",
            "updated_at",
        ]
```

## Rules

- Views are thin: validate input → call service → return response
- Never put business logic in views or serializers
- Use `raise_exception=True` on `is_valid()` — never check manually
- `@transaction.atomic` on views/services that write multiple models
- Public endpoints: set `permission_classes = []` and `authentication_classes = []`
- Use `reverse("api:<namespace>:<route>")` in tests, never hardcode URLs
- Always return explicit `status=` in `Response(...)`
