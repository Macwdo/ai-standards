---
name: personal-django-patterns
description: Repo-specific Django implementation patterns for models, selectors, services, serializers, DRF endpoints, and pytest tests in projects that follow this repo's conventions. Use when Codex needs one entry point for adding or updating Django apps, models, selectors, services, serializers, APIViews, ViewSet actions, admin registration, helper-first tests, or adjacent service-layer code.
---

# Personal Django Patterns

Use this skill as the default umbrella skill for Django work in repos that match these conventions.

Keep the implementation aligned with the existing app shape before introducing anything new.

## Workflow

### 1. Read the local app first

- Inspect the target app's `models.py`, `views.py`, `serializers.py`, `selectors.py`, `services.py`, `admin.py`, `urls.py`, and `tests/` before editing.
- Reuse existing naming, route structure, base classes, and helper patterns when they already exist.
- If the repo's current code conflicts with a generic Django best practice, follow the repo.

### 2. Choose the task shape

- For model work, read [references/models.md](references/models.md).
- For write-side business logic, read [references/services.md](references/services.md).
- For read-side query logic, read [references/selectors.md](references/selectors.md).
- For serializer or response-shaping work, read [references/serializers.md](references/serializers.md).
- For APIView, ViewSet, routing, or response-adapter work, read [references/endpoints.md](references/endpoints.md).
- For test work, read [references/testing.md](references/testing.md).
- For most feature work, use these references in order: models, services, selectors, serializers, endpoints, testing.

### 3. Keep boundaries explicit

- Keep endpoints thin: validate input, call a selector or service, return a response.
- Keep serializers focused on validation and representation, not business writes.
- Keep selectors focused on pulling data and query optimization.
- Keep services focused on pushing state changes, business rules, and side effects.
- Keep test setup visible through helpers and public APIs.
- Keep admin registration and migrations in scope when a model changes.

### 4. Finish the change completely

- Add or update migrations when models change.
- Add or update tests for the user-visible behavior.
- Run the smallest validation that proves the change works.

## Decision Rules

- Prefer repo-specific patterns over generic Django examples.
- Prefer extending existing helpers over adding opaque fixtures or inline ORM-heavy setup.
- Prefer service and selector boundaries over business logic in serializers or endpoints.
- Prefer string model references for cross-app foreign keys.
- Prefer progressive disclosure: keep `SKILL.md` short and load references only when needed.

## References

- [references/models.md](references/models.md): model, admin, and migration conventions
- [references/services.md](references/services.md): write-side business logic, transactions, and side effects
- [references/selectors.md](references/selectors.md): read-side query patterns, filtering, and optimization
- [references/serializers.md](references/serializers.md): input/output serializers and response shaping
- [references/endpoints.md](references/endpoints.md): DRF APIViews, ViewSets, routing, and response rules
- [references/testing.md](references/testing.md): pytest, DRF, helpers, and TDD rules
