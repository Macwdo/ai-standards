# Endpoint Patterns

Use these rules when adding or updating DRF endpoints in this repo.

This file is only for the HTTP adapter layer. Keep serializer-specific rules in `serializers.md`, read-side logic in `selectors.md`, and write-side logic in `services.md`.

## Read First

- Inspect the app's `views.py`, `serializers.py`, `selectors.py`, `services.py`, `urls.py`, and tests.
- Match the app's current style before introducing a new API shape.
- Keep views thin and explicit.

## Core Rules

- Validate request data with a serializer.
- Call a selector for read flows and a service for write flows.
- Return `Response(..., status=...)` explicitly.
- Do not put business logic in endpoints or serializers.
- Use `raise_exception=True` with `is_valid()`.
- Keep transaction boundaries in services whenever possible.
- For public endpoints, set `permission_classes = []` and `authentication_classes = []`.

## Default Decision Matrix

Use these defaults unless the existing app already establishes a stronger pattern.

| Situation | Default shape | Why |
| --- | --- | --- |
| Bespoke workflow, RPC-like action, webhook, or multi-step flow | `APIView` | Best when the endpoint does not map cleanly to standard resource CRUD. |
| Behavior belongs to an existing resource | `@action` on a ViewSet | Keeps resource-adjacent behavior grouped with the resource. |
| Read-only resource | `ReadOnlyModelViewSet` | Good for router-backed list/retrieve behavior. |
| Partial CRUD | `GenericViewSet` plus mixins | Preferred for create-only, list-only, list-create, or other partial CRUD shapes. |
| Straightforward CRUD | `ModelViewSet` | Use only when CRUD is genuinely mechanical or the app already uses it. |

## APIView Pattern

Use an APIView when the endpoint is custom logic rather than standard resource CRUD.

```python
from __future__ import annotations

from typing import TYPE_CHECKING

from rest_framework import status
from rest_framework.response import Response

from apps.api.views import BaseAPIView
from apps.example import services
from apps.example.serializers import (
    ExampleSerializerRequest,
    ExampleSerializerResponse,
)

if TYPE_CHECKING:
    from rest_framework.request import Request


class ExampleAPIView(BaseAPIView):
    def post(self, request: Request) -> Response:
        input_serializer = ExampleSerializerRequest(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        example = services.do_example(**input_serializer.validated_data)
        output_serializer = ExampleSerializerResponse(example)

        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
```

## ViewSet Action Pattern

Use a custom action when the behavior belongs on an existing resource.

```python
from apps.example import services
from apps.example.serializers import (
    ExampleApproveSerializerRequest,
    ExampleSerializerResponse,
)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response


@action(
    detail=True,
    methods=["post"],
    serializer_class=ExampleApproveSerializerRequest,
    url_path="approve",
)
def approve(self, request: Request, pk: str | None = None) -> Response:
    input_serializer = self.get_serializer(data=request.data)
    input_serializer.is_valid(raise_exception=True)

    example = self.get_object()
    updated_example = services.do_example(
        example=example,
        **input_serializer.validated_data,
    )
    output_serializer = ExampleSerializerResponse(updated_example)

    return Response(output_serializer.data, status=status.HTTP_200_OK)
```

## CRUD ViewSets

Use DRF's built-in ViewSets when they match the endpoint, and create shared `GenericViewSet` mixin combinations when partial CRUD repeats across the repo.

```python
from rest_framework import mixins, viewsets


class CreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    pass


class ListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    pass


class RetrieveViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    pass


class UpdateViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    pass


class DestroyViewSet(mixins.DestroyModelMixin, viewsets.GenericViewSet):
    pass


class ListCreateViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    pass


class CreateListRetrieveViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    pass


class RetrieveUpdateDestroyViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    pass
```

The curated ViewSet catalog for this skill is:

- `ModelViewSet`
- `ReadOnlyModelViewSet`
- `CreateViewSet`
- `ListViewSet`
- `RetrieveViewSet`
- `UpdateViewSet`
- `DestroyViewSet`
- `ListCreateViewSet`
- `CreateListRetrieveViewSet`
- `RetrieveUpdateDestroyViewSet`

## Service-First CRUD Pattern

When CRUD logic is not trivial, override the action method or prefer an `APIView` instead of pushing business writes into serializer hooks.

```python
from apps.example import selectors, services
from apps.example.serializers import (
    ExampleSerializerRequest,
    ExampleSerializerResponse,
)
from rest_framework import status
from rest_framework.response import Response


class ExampleViewSet(CreateListRetrieveViewSet):
    serializer_action_classes = {
        "create": ExampleSerializerRequest,
        "list": ExampleSerializerResponse,
        "retrieve": ExampleSerializerResponse,
    }

    def get_queryset(self):
        return selectors.example_list(account=self.request.user.account)

    def get_serializer_class(self):
        return self.serializer_action_classes[self.action]

    def create(self, request, *args, **kwargs):
        input_serializer = ExampleSerializerRequest(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        example = services.example_create(
            account=request.user.account,
            **input_serializer.validated_data,
        )

        output_serializer = ExampleSerializerResponse(example)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
```

Use `ModelViewSet` only when the create, update, and destroy behavior is truly straightforward. When the behavior grows branches, side effects, or cross-model rules, override the action method or drop to a thinner adapter.

## Router Rules

- Register router prefixes without a trailing slash.
- If the ViewSet omits a class-level `queryset`, provide `basename=` when registering it with the router.
- Register ViewSets with a router instead of wiring `@action` methods manually.
- Keep action-specific settings such as `serializer_class`, `permission_classes`, `url_path`, and `detail` on the `@action` itself.

```python
from rest_framework.routers import DefaultRouter

from apps.example.views import ExampleViewSet

router = DefaultRouter()
router.register("examples", ExampleViewSet, basename="example")

urlpatterns = router.urls
```

## Response and Object-Fetching Rules

- Return explicit status codes for both success and failure paths.
- Serialize output explicitly instead of relying on hidden serializer side effects.
- For read-only endpoints, prefer `self.get_object()`, `self.get_queryset()`, or selectors that keep object fetching consistent with the rest of the app.
- Keep pagination, filtering, and queryset optimization aligned with the repo's existing base views or pagination classes instead of recreating DRF internals in each endpoint.
