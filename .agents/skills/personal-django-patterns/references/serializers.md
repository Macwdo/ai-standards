# Serializer Patterns

Use these rules when adding or updating DRF serializers in this repo.

Serializer code should validate input and shape output. It should not become the home of business writes.

## Read First

- Inspect the app's `serializers.py`, `views.py`, `services.py`, `selectors.py`, and tests before introducing new serializer classes.
- Reuse the app's current serializer naming, field style, and nested representation patterns when they already exist.
- Keep serializer responsibilities aligned with the endpoint and service boundaries in this skill.

## Core Rules

- Use a dedicated input serializer and a dedicated output serializer when the endpoint both accepts and returns structured data.
- Keep validation in serializers and business rules in services.
- Follow the repo's local naming style. Common patterns are request/response suffixes such as `ExampleSerializerRequest` and `ExampleSerializerResponse`.
- Pass `context` only when the serializer genuinely needs request-aware behavior for representation or validation.

## Input Serializer Pattern

Use `serializers.Serializer` for request bodies, query params, custom action payloads, and non-trivial validation flows.

```python
from rest_framework import serializers


class ExampleSerializerRequest(serializers.Serializer):
    name = serializers.CharField(required=True)
    is_active = serializers.BooleanField(required=False, default=True)

    def validate_name(self, value: str) -> str:
        return value.strip()

    def validate(self, attrs: dict) -> dict:
        return attrs
```

## Output Serializer Pattern

Use `ModelSerializer` for straightforward read representations or when the app already exposes the model directly.

```python
from rest_framework import serializers

from apps.example.models import ExampleModel


class ExampleSerializerResponse(serializers.ModelSerializer):
    class Meta:
        model = ExampleModel
        fields = [
            "id",
            "name",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
```

## `Serializer` vs `ModelSerializer`

- Use `Serializer` for request payloads, query-parameter validation, action inputs, computed outputs, and responses that do not map cleanly to a single model.
- Use `ModelSerializer` for straightforward read responses and simple model-bound output that the repo already treats as mechanical CRUD.
- Prefer plain `Serializer` over `ModelSerializer` when the service layer owns create or update behavior.

## Action-Aware ViewSet Serializers

When a ViewSet needs different serializers per action, implement `get_serializer_class()` explicitly.

```python
from rest_framework import mixins, viewsets


class ExampleViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_action_classes = {
        "create": ExampleSerializerRequest,
        "list": ExampleSerializerResponse,
        "retrieve": ExampleSerializerResponse,
        "approve": ExampleApproveSerializerRequest,
    }

    def get_serializer_class(self):
        return self.serializer_action_classes.get(
            self.action,
            ExampleSerializerResponse,
        )
```

If the input and output serializer for one action differ, validate with the input serializer and instantiate the output serializer explicitly for the response.

```python
from rest_framework import status
from rest_framework.response import Response


def create(self, request, *args, **kwargs):
    input_serializer = ExampleSerializerRequest(data=request.data)
    input_serializer.is_valid(raise_exception=True)

    example = services.example_create(**input_serializer.validated_data)

    output_serializer = ExampleSerializerResponse(example)
    return Response(output_serializer.data, status=status.HTTP_201_CREATED)
```

## Advanced Serializer Functions

When response shaping gets complex, move the output assembly into a serializer function instead of overloading the selector.

```python
from apps.example.models import ExampleModel


def example_feed_serialize(feed):
    feed_ids = [item.id for item in feed]

    objects = (
        ExampleModel.objects.select_related("owner")
        .prefetch_related("tags")
        .filter(id__in=feed_ids)
        .order_by("-created_at")
    )

    return [ExampleSerializerResponse(obj).data for obj in objects]
```

This keeps the selector responsible for deciding what data to fetch, while the serializer function takes responsibility for shaping the final API-ready payload.

## Serializer Boundaries

- Do not move business writes into `create()` or `update()` unless the repo already treats that serializer as a thin adapter over a service.
- Do not hide orchestration, task dispatch, or side effects in `validate()`.
- Keep nested serializers and computed fields readable; if output optimization grows complex, refetch and serialize deliberately.
