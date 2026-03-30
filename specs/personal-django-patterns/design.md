## Overview

Create a new repo skill at `.agents/skills/personal-django-patterns` that merges the useful, repo-specific parts of:

- `personal-django-tdd`
- `personal-new-endpoint`
- `personal-new-model`
- `django-patterns`

The new skill should act as the preferred umbrella skill for routine Django work in repos that follow these conventions.

## Architecture

- Keep `SKILL.md` focused on workflow and decision rules.
- Move longer code patterns into `references/` so the skill follows progressive disclosure.
- Generate `agents/openai.yaml` during initialization for UI metadata consistency.

## Components and Interfaces

### Skill metadata

- `name`: `personal-django-patterns`
- `description`: explain that the skill is for repo-specific Django model, endpoint, service, and test work, and mention common triggers clearly enough for auto-selection.

### Main skill body

- Explain when to inspect current app structure.
- Provide a small workflow:
  1. Read the app shape first.
  2. Choose whether the task is model-first, endpoint-first, or test-first.
  3. Apply the relevant reference patterns.
  4. Finish with migrations/tests appropriate to the change.
- Keep rules explicit and imperative.

### Reference files

- `references/models.md`: model conventions distilled from `personal-new-model` plus only repo-relevant model guidance.
- `references/endpoints.md`: endpoint and serializer patterns distilled from `personal-new-endpoint`, with a small amount of supporting architecture guidance.
- `references/testing.md`: helper-first TDD/testing guidance distilled from `personal-django-tdd`.

## Data Models

No runtime code or scripts are needed. This skill is documentation-only plus generated metadata.

## Error Handling

- Avoid generic Django guidance that conflicts with repo conventions.
- Avoid repeating the same rules in both `SKILL.md` and references.
- Do not add placeholder resources from the initializer.

## Testing Strategy

- Run the skill initializer with only the `references` resource.
- Run `quick_validate.py` on the completed skill.
- Review the generated `agents/openai.yaml` and ensure the default prompt explicitly mentions `$personal-django-patterns`.

### Decision: Use references instead of a long SKILL body

Context: the source skills contain overlapping examples and long-form guidance.

Options Considered:
1. Put everything in `SKILL.md` - Pros: one file / Cons: noisy, repetitive, higher context cost.
2. Keep `SKILL.md` short and move detail to references - Pros: better progressive disclosure, easier maintenance / Cons: more files.

Decision: Keep `SKILL.md` short and use references.

Rationale: This fits the skill-creator guidance and produces a cleaner umbrella skill.
