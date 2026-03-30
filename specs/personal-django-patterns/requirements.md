## User Story

As a maintainer of this skill repo, I want a `personal-django-patterns` skill that consolidates the repo's Django implementation conventions, so Codex can apply the right patterns for models, endpoints, and tests without loading multiple overlapping skills.

## Acceptance Criteria

1. WHEN Codex needs repo-specific Django implementation guidance THEN the skill SHALL provide a single entry point that covers model, endpoint, and test conventions.
2. WHEN the skill is triggered for new Django work THEN the skill SHALL instruct Codex to inspect the target app's existing structure before introducing new patterns.
3. WHEN Codex creates a model THEN the skill SHALL document the repo's base-class, field, `__str__`, admin, and migration conventions.
4. WHEN Codex creates or updates an API endpoint THEN the skill SHALL document the repo's thin-view, serializer, service-layer, permission, and response conventions.
5. WHEN Codex adds or updates tests for the change THEN the skill SHALL require helper-first, API-driven pytest and DRF patterns, including the ban on factories.
6. IF detailed examples would bloat the main skill THEN the skill SHALL move them into reference files and keep `SKILL.md` concise.
7. WHEN the skill is initialized THEN it SHALL include valid `SKILL.md` frontmatter and generated `agents/openai.yaml`.
8. WHEN validation runs against the skill THEN the skill SHALL pass the repository's quick validation script.
